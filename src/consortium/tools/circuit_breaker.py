"""Circuit Breaker for LLM Providers (Feature 8 - BONUS).

Implements circuit breaker pattern for LLM API calls to handle provider failures gracefully.

States:
- CLOSED: Normal operation, all requests go through
- OPEN: Provider is failing, reject requests immediately
- HALF_OPEN: Testing if provider has recovered

Features:
- Automatic failover to backup provider
- Configurable failure thresholds
- Exponential backoff for recovery attempts
- Per-provider circuit breakers
- Health tracking and metrics
"""

import time
from enum import Enum
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Provider is failing, reject immediately
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes to close from half-open
    timeout_seconds: int = 60   # How long to wait before half-open
    window_seconds: int = 60    # Rolling window for failure counting
    max_failures_percent: float = 50.0  # Max failure % before opening


@dataclass
class CircuitMetrics:
    """Metrics for circuit breaker."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rejected_requests: int = 0  # Rejected due to open circuit
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_transitions: int = 0
    recent_failures: list = field(default_factory=list)  # Timestamps
    recent_successes: list = field(default_factory=list)  # Timestamps


class CircuitBreaker:
    """Circuit breaker for LLM provider calls.

    Implements the circuit breaker pattern to prevent cascading failures
    when an LLM provider is down or degraded.
    """

    def __init__(
        self,
        provider_name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        """Initialize circuit breaker.

        Args:
            provider_name: Name of LLM provider
            config: Circuit breaker configuration
        """
        self.provider_name = provider_name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.metrics = CircuitMetrics()
        self.opened_at: Optional[datetime] = None

    def call(
        self,
        func: Callable,
        *args,
        fallback_func: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """Execute function with circuit breaker protection.

        Args:
            func: Function to call (LLM API call)
            *args: Positional arguments for func
            fallback_func: Fallback function if circuit is open
            **kwargs: Keyword arguments for func

        Returns:
            Result from func or fallback_func

        Raises:
            Exception: If circuit is open and no fallback provided
        """
        # Check circuit state
        if self.state == CircuitState.OPEN:
            # Check if timeout has elapsed
            if self._should_attempt_recovery():
                self._transition_to_half_open()
            else:
                # Circuit still open, use fallback or reject
                self.metrics.rejected_requests += 1
                if fallback_func:
                    logger.warning(
                        f"Circuit OPEN for {self.provider_name}, using fallback"
                    )
                    return fallback_func(*args, **kwargs)
                else:
                    raise Exception(
                        f"Circuit breaker OPEN for {self.provider_name}. "
                        f"Provider is unavailable."
                    )

        # Attempt the call
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result

        except Exception as e:
            self._record_failure()

            # If circuit is open after failure, use fallback
            if self.state == CircuitState.OPEN and fallback_func:
                logger.warning(
                    f"Circuit opened for {self.provider_name}, using fallback"
                )
                return fallback_func(*args, **kwargs)

            # Re-raise if no fallback
            raise e

    def _record_success(self):
        """Record successful request."""
        now = datetime.now()

        self.metrics.total_requests += 1
        self.metrics.successful_requests += 1
        self.metrics.last_success_time = now
        self.metrics.recent_successes.append(now)

        # Clean old successes outside window
        self._clean_recent_records()

        # State transitions based on success
        if self.state == CircuitState.HALF_OPEN:
            # Count recent successes
            recent_success_count = len(self.metrics.recent_successes)

            if recent_success_count >= self.config.success_threshold:
                self._transition_to_closed()

    def _record_failure(self):
        """Record failed request."""
        now = datetime.now()

        self.metrics.total_requests += 1
        self.metrics.failed_requests += 1
        self.metrics.last_failure_time = now
        self.metrics.recent_failures.append(now)

        # Clean old failures outside window
        self._clean_recent_records()

        # Check if we should open circuit
        if self.state == CircuitState.CLOSED:
            recent_failure_count = len(self.metrics.recent_failures)
            recent_total = len(self.metrics.recent_failures) + len(self.metrics.recent_successes)

            # Open if failures exceed threshold
            if recent_failure_count >= self.config.failure_threshold:
                self._transition_to_open()

            # Or if failure rate exceeds percentage
            elif recent_total > 0:
                failure_rate = (recent_failure_count / recent_total) * 100
                if failure_rate >= self.config.max_failures_percent:
                    self._transition_to_open()

        elif self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open state reopens circuit
            self._transition_to_open()

    def _clean_recent_records(self):
        """Remove records outside rolling window."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.config.window_seconds)

        self.metrics.recent_failures = [
            t for t in self.metrics.recent_failures if t > cutoff
        ]
        self.metrics.recent_successes = [
            t for t in self.metrics.recent_successes if t > cutoff
        ]

    def _should_attempt_recovery(self) -> bool:
        """Check if we should attempt recovery from open state.

        Returns:
            True if timeout has elapsed
        """
        if not self.opened_at:
            return False

        elapsed = (datetime.now() - self.opened_at).total_seconds()
        return elapsed >= self.config.timeout_seconds

    def _transition_to_closed(self):
        """Transition to CLOSED state."""
        logger.info(
            f"Circuit breaker for {self.provider_name}: HALF_OPEN → CLOSED "
            f"(provider recovered)"
        )
        self.state = CircuitState.CLOSED
        self.opened_at = None
        self.metrics.state_transitions += 1

    def _transition_to_open(self):
        """Transition to OPEN state."""
        logger.warning(
            f"Circuit breaker for {self.provider_name}: {self.state.value} → OPEN "
            f"(failures: {len(self.metrics.recent_failures)})"
        )
        self.state = CircuitState.OPEN
        self.opened_at = datetime.now()
        self.metrics.state_transitions += 1

    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state."""
        logger.info(
            f"Circuit breaker for {self.provider_name}: OPEN → HALF_OPEN "
            f"(attempting recovery)"
        )
        self.state = CircuitState.HALF_OPEN
        self.metrics.state_transitions += 1

    def get_state(self) -> CircuitState:
        """Get current circuit state.

        Returns:
            Current state
        """
        return self.state

    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit metrics.

        Returns:
            Metrics dict
        """
        now = datetime.now()
        recent_total = len(self.metrics.recent_failures) + len(self.metrics.recent_successes)

        return {
            "provider": self.provider_name,
            "state": self.state.value,
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "rejected_requests": self.metrics.rejected_requests,
            "recent_failures": len(self.metrics.recent_failures),
            "recent_successes": len(self.metrics.recent_successes),
            "failure_rate_percent": (
                (len(self.metrics.recent_failures) / recent_total * 100)
                if recent_total > 0 else 0.0
            ),
            "last_failure": (
                self.metrics.last_failure_time.isoformat()
                if self.metrics.last_failure_time else None
            ),
            "last_success": (
                self.metrics.last_success_time.isoformat()
                if self.metrics.last_success_time else None
            ),
            "state_transitions": self.metrics.state_transitions,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None
        }

    def reset(self):
        """Reset circuit breaker to initial state."""
        self.state = CircuitState.CLOSED
        self.metrics = CircuitMetrics()
        self.opened_at = None

    def is_available(self) -> bool:
        """Check if provider is available.

        Returns:
            True if circuit is closed or half-open
        """
        return self.state != CircuitState.OPEN


# ==============================================================================
# MULTI-PROVIDER CIRCUIT BREAKER MANAGER
# ==============================================================================

class CircuitBreakerManager:
    """Manages circuit breakers for multiple LLM providers."""

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """Initialize circuit breaker manager.

        Args:
            config: Default config for all circuit breakers
        """
        self.config = config or CircuitBreakerConfig()
        self.breakers: Dict[str, CircuitBreaker] = {}

    def get_breaker(self, provider: str) -> CircuitBreaker:
        """Get or create circuit breaker for provider.

        Args:
            provider: Provider name

        Returns:
            CircuitBreaker instance
        """
        if provider not in self.breakers:
            self.breakers[provider] = CircuitBreaker(
                provider_name=provider,
                config=self.config
            )

        return self.breakers[provider]

    def call_with_fallback(
        self,
        primary_provider: str,
        fallback_provider: str,
        primary_func: Callable,
        fallback_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Call primary provider with automatic fallback.

        Args:
            primary_provider: Primary provider name
            fallback_provider: Fallback provider name
            primary_func: Function to call on primary
            fallback_func: Function to call on fallback
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result from primary or fallback
        """
        primary_breaker = self.get_breaker(primary_provider)

        # If primary circuit is open, go directly to fallback
        if not primary_breaker.is_available():
            logger.info(
                f"Primary provider {primary_provider} unavailable, "
                f"using fallback {fallback_provider}"
            )
            fallback_breaker = self.get_breaker(fallback_provider)
            return fallback_breaker.call(fallback_func, *args, **kwargs)

        # Try primary with fallback
        return primary_breaker.call(
            primary_func,
            *args,
            fallback_func=lambda *a, **kw: self.get_breaker(fallback_provider).call(
                fallback_func, *a, **kw
            ),
            **kwargs
        )

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all circuit breakers.

        Returns:
            Dict mapping provider name to metrics
        """
        return {
            provider: breaker.get_metrics()
            for provider, breaker in self.breakers.items()
        }

    def get_available_providers(self) -> list[str]:
        """Get list of available providers.

        Returns:
            List of provider names with closed circuits
        """
        return [
            provider
            for provider, breaker in self.breakers.items()
            if breaker.is_available()
        ]

    def reset_all(self):
        """Reset all circuit breakers."""
        for breaker in self.breakers.values():
            breaker.reset()


# ==============================================================================
# GLOBAL INSTANCE
# ==============================================================================

_circuit_breaker_manager: Optional[CircuitBreakerManager] = None


def get_circuit_breaker_manager(
    config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreakerManager:
    """Get global CircuitBreakerManager instance (singleton).

    Args:
        config: Optional configuration

    Returns:
        CircuitBreakerManager instance
    """
    global _circuit_breaker_manager

    if _circuit_breaker_manager is None:
        _circuit_breaker_manager = CircuitBreakerManager(config=config)

    return _circuit_breaker_manager
