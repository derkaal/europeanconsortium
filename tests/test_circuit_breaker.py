"""Tests for Feature 8: Circuit Breaker for LLM Providers.

Tests:
1. Circuit breaker initialization
2. State transitions (CLOSED → OPEN → HALF_OPEN → CLOSED)
3. Failure threshold triggering
4. Success threshold recovery
5. Automatic fallback on open circuit
6. Timeout and recovery attempts
7. Metrics tracking
8. Multi-provider manager
9. Call with fallback
10. Rolling window behavior
"""

import pytest
import time
from datetime import datetime, timedelta
from src.consortium.tools.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerManager,
    CircuitState,
    CircuitBreakerConfig,
    get_circuit_breaker_manager
)


# ==============================================================================
# Test Helpers
# ==============================================================================

def success_func():
    """Mock successful function."""
    return "success"


def failure_func():
    """Mock failing function."""
    raise Exception("API Error")


def fallback_func():
    """Mock fallback function."""
    return "fallback"


# ==============================================================================
# Test: Initialization
# ==============================================================================

def test_circuit_breaker_initialization():
    """Test circuit breaker initializes correctly."""
    breaker = CircuitBreaker("anthropic")

    assert breaker.provider_name == "anthropic"
    assert breaker.state == CircuitState.CLOSED
    assert breaker.metrics.total_requests == 0


def test_circuit_breaker_custom_config():
    """Test circuit breaker with custom config."""
    config = CircuitBreakerConfig(
        failure_threshold=10,
        timeout_seconds=120
    )

    breaker = CircuitBreaker("openai", config=config)

    assert breaker.config.failure_threshold == 10
    assert breaker.config.timeout_seconds == 120


# ==============================================================================
# Test: Successful Calls
# ==============================================================================

def test_call_success():
    """Test successful call through circuit breaker."""
    breaker = CircuitBreaker("anthropic")

    result = breaker.call(success_func)

    assert result == "success"
    assert breaker.metrics.successful_requests == 1
    assert breaker.metrics.failed_requests == 0
    assert breaker.state == CircuitState.CLOSED


def test_multiple_success_calls():
    """Test multiple successful calls."""
    breaker = CircuitBreaker("anthropic")

    for _ in range(10):
        result = breaker.call(success_func)
        assert result == "success"

    assert breaker.metrics.successful_requests == 10
    assert breaker.state == CircuitState.CLOSED


# ==============================================================================
# Test: Failed Calls
# ==============================================================================

def test_call_failure():
    """Test failed call through circuit breaker."""
    breaker = CircuitBreaker("anthropic")

    with pytest.raises(Exception):
        breaker.call(failure_func)

    assert breaker.metrics.failed_requests == 1
    assert breaker.metrics.successful_requests == 0


def test_failures_below_threshold():
    """Test failures below threshold don't open circuit."""
    config = CircuitBreakerConfig(failure_threshold=5)
    breaker = CircuitBreaker("anthropic", config=config)

    # 4 failures (below threshold of 5)
    for _ in range(4):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    # Circuit should still be closed
    assert breaker.state == CircuitState.CLOSED


def test_failures_exceed_threshold_opens_circuit():
    """Test failures exceeding threshold opens circuit."""
    config = CircuitBreakerConfig(failure_threshold=3)
    breaker = CircuitBreaker("anthropic", config=config)

    # 3 failures (meets threshold)
    for _ in range(3):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    # Circuit should be open
    assert breaker.state == CircuitState.OPEN


# ==============================================================================
# Test: State Transitions
# ==============================================================================

def test_transition_closed_to_open():
    """Test transition from CLOSED to OPEN on failures."""
    config = CircuitBreakerConfig(failure_threshold=3)
    breaker = CircuitBreaker("anthropic", config=config)

    assert breaker.state == CircuitState.CLOSED

    # Trigger failures
    for _ in range(3):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    assert breaker.state == CircuitState.OPEN
    assert breaker.opened_at is not None


def test_transition_open_to_half_open_after_timeout():
    """Test transition from OPEN to HALF_OPEN after timeout."""
    config = CircuitBreakerConfig(
        failure_threshold=2,
        timeout_seconds=1  # Short timeout for testing
    )
    breaker = CircuitBreaker("anthropic", config=config)

    # Open circuit
    for _ in range(2):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    assert breaker.state == CircuitState.OPEN

    # Wait for timeout
    time.sleep(1.1)

    # Next call should transition to half-open
    result = breaker.call(success_func)

    assert breaker.state == CircuitState.HALF_OPEN
    assert result == "success"


def test_transition_half_open_to_closed_on_success():
    """Test transition from HALF_OPEN to CLOSED on successful recovery."""
    config = CircuitBreakerConfig(
        failure_threshold=2,
        success_threshold=2,
        timeout_seconds=1
    )
    breaker = CircuitBreaker("anthropic", config=config)

    # Open circuit
    for _ in range(2):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    # Wait for timeout
    time.sleep(1.1)

    # Transition to half-open
    breaker.call(success_func)
    assert breaker.state == CircuitState.HALF_OPEN

    # Second success should close circuit
    breaker.call(success_func)
    assert breaker.state == CircuitState.CLOSED


def test_transition_half_open_to_open_on_failure():
    """Test transition from HALF_OPEN back to OPEN on failure."""
    config = CircuitBreakerConfig(
        failure_threshold=2,
        timeout_seconds=1
    )
    breaker = CircuitBreaker("anthropic", config=config)

    # Open circuit
    for _ in range(2):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    # Wait for timeout
    time.sleep(1.1)

    # Transition to half-open
    breaker.call(success_func)
    assert breaker.state == CircuitState.HALF_OPEN

    # Failure should reopen circuit
    with pytest.raises(Exception):
        breaker.call(failure_func)

    assert breaker.state == CircuitState.OPEN


# ==============================================================================
# Test: Fallback Functionality
# ==============================================================================

def test_fallback_when_circuit_open():
    """Test fallback function is called when circuit is open."""
    config = CircuitBreakerConfig(failure_threshold=2)
    breaker = CircuitBreaker("anthropic", config=config)

    # Open circuit
    for _ in range(2):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    # Call with fallback should use fallback
    result = breaker.call(failure_func, fallback_func=fallback_func)

    assert result == "fallback"
    assert breaker.metrics.rejected_requests == 1


def test_no_fallback_raises_exception():
    """Test that open circuit without fallback raises exception."""
    config = CircuitBreakerConfig(failure_threshold=2)
    breaker = CircuitBreaker("anthropic", config=config)

    # Open circuit
    for _ in range(2):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    # Call without fallback should raise
    with pytest.raises(Exception) as exc_info:
        breaker.call(failure_func)

    assert "Circuit breaker OPEN" in str(exc_info.value)


def test_fallback_after_failure():
    """Test fallback is called after failure opens circuit."""
    config = CircuitBreakerConfig(failure_threshold=3)
    breaker = CircuitBreaker("anthropic", config=config)

    # First 2 failures don't open circuit
    for _ in range(2):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    # Third failure opens circuit and uses fallback
    result = breaker.call(failure_func, fallback_func=fallback_func)

    assert result == "fallback"
    assert breaker.state == CircuitState.OPEN


# ==============================================================================
# Test: Metrics
# ==============================================================================

def test_metrics_tracking():
    """Test metrics are tracked correctly."""
    breaker = CircuitBreaker("anthropic")

    # Successful calls
    breaker.call(success_func)
    breaker.call(success_func)

    # Failed call
    with pytest.raises(Exception):
        breaker.call(failure_func)

    metrics = breaker.get_metrics()

    assert metrics["total_requests"] == 3
    assert metrics["successful_requests"] == 2
    assert metrics["failed_requests"] == 1
    assert metrics["provider"] == "anthropic"
    assert metrics["state"] == "closed"


def test_metrics_recent_failures():
    """Test recent failures are tracked in window."""
    config = CircuitBreakerConfig(window_seconds=60)
    breaker = CircuitBreaker("anthropic", config=config)

    # Add failures
    for _ in range(3):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    metrics = breaker.get_metrics()

    assert metrics["recent_failures"] == 3


def test_metrics_failure_rate():
    """Test failure rate calculation."""
    breaker = CircuitBreaker("anthropic")

    # 2 successes, 2 failures = 50% failure rate
    breaker.call(success_func)
    breaker.call(success_func)

    with pytest.raises(Exception):
        breaker.call(failure_func)
    with pytest.raises(Exception):
        breaker.call(failure_func)

    metrics = breaker.get_metrics()

    assert metrics["failure_rate_percent"] == 50.0


# ==============================================================================
# Test: Circuit Breaker Manager
# ==============================================================================

def test_circuit_breaker_manager_initialization():
    """Test circuit breaker manager initializes."""
    manager = CircuitBreakerManager()

    assert len(manager.breakers) == 0


def test_manager_get_or_create_breaker():
    """Test manager gets or creates breaker for provider."""
    manager = CircuitBreakerManager()

    breaker1 = manager.get_breaker("anthropic")
    breaker2 = manager.get_breaker("anthropic")

    # Should return same instance
    assert breaker1 is breaker2
    assert len(manager.breakers) == 1


def test_manager_multiple_providers():
    """Test manager handles multiple providers."""
    manager = CircuitBreakerManager()

    anthropic = manager.get_breaker("anthropic")
    openai = manager.get_breaker("openai")

    assert anthropic.provider_name == "anthropic"
    assert openai.provider_name == "openai"
    assert len(manager.breakers) == 2


def test_manager_call_with_fallback():
    """Test manager call with fallback between providers."""
    config = CircuitBreakerConfig(failure_threshold=2)
    manager = CircuitBreakerManager(config=config)

    # Open primary circuit
    primary_breaker = manager.get_breaker("anthropic")
    for _ in range(2):
        with pytest.raises(Exception):
            primary_breaker.call(failure_func)

    # Call with fallback should use fallback provider
    result = manager.call_with_fallback(
        primary_provider="anthropic",
        fallback_provider="openai",
        primary_func=failure_func,
        fallback_func=fallback_func
    )

    assert result == "fallback"


def test_manager_get_available_providers():
    """Test getting available providers."""
    config = CircuitBreakerConfig(failure_threshold=2)
    manager = CircuitBreakerManager(config=config)

    # Create breakers
    manager.get_breaker("anthropic")
    manager.get_breaker("openai")

    # Open anthropic
    anthropic = manager.get_breaker("anthropic")
    for _ in range(2):
        with pytest.raises(Exception):
            anthropic.call(failure_func)

    available = manager.get_available_providers()

    assert "openai" in available
    assert "anthropic" not in available


def test_manager_get_all_metrics():
    """Test getting metrics for all providers."""
    manager = CircuitBreakerManager()

    manager.get_breaker("anthropic").call(success_func)
    manager.get_breaker("openai").call(success_func)

    all_metrics = manager.get_all_metrics()

    assert "anthropic" in all_metrics
    assert "openai" in all_metrics
    assert all_metrics["anthropic"]["successful_requests"] == 1


def test_manager_reset_all():
    """Test resetting all circuit breakers."""
    config = CircuitBreakerConfig(failure_threshold=2)
    manager = CircuitBreakerManager(config=config)

    # Open circuit
    breaker = manager.get_breaker("anthropic")
    for _ in range(2):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    assert breaker.state == CircuitState.OPEN

    # Reset
    manager.reset_all()

    assert breaker.state == CircuitState.CLOSED
    assert breaker.metrics.total_requests == 0


# ==============================================================================
# Test: Rolling Window
# ==============================================================================

def test_rolling_window_cleanup():
    """Test old failures are cleaned from rolling window."""
    config = CircuitBreakerConfig(
        window_seconds=1,  # 1 second window
        failure_threshold=5
    )
    breaker = CircuitBreaker("anthropic", config=config)

    # Add 2 failures
    for _ in range(2):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    assert len(breaker.metrics.recent_failures) == 2

    # Wait for window to expire
    time.sleep(1.1)

    # Clean old records
    breaker._clean_recent_records()

    # Old failures should be removed
    assert len(breaker.metrics.recent_failures) == 0


def test_failure_threshold_with_rolling_window():
    """Test failure threshold respects rolling window."""
    config = CircuitBreakerConfig(
        window_seconds=2,
        failure_threshold=3
    )
    breaker = CircuitBreaker("anthropic", config=config)

    # Add 2 failures
    for _ in range(2):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    # Wait for window to expire
    time.sleep(2.1)

    # Add 1 more failure (old ones should be cleaned)
    with pytest.raises(Exception):
        breaker.call(failure_func)

    # Circuit should still be closed (only 1 recent failure)
    assert breaker.state == CircuitState.CLOSED


# ==============================================================================
# Test: Percentage-Based Triggering
# ==============================================================================

def test_open_on_failure_percentage():
    """Test circuit opens based on failure percentage."""
    config = CircuitBreakerConfig(
        failure_threshold=100,  # High threshold
        max_failures_percent=50.0  # 50% failures
    )
    breaker = CircuitBreaker("anthropic", config=config)

    # 5 successes, 5 failures = 50% failure rate
    for _ in range(5):
        breaker.call(success_func)

    for _ in range(5):
        with pytest.raises(Exception):
            breaker.call(failure_func)

    # Circuit should be open due to 50% failure rate
    assert breaker.state == CircuitState.OPEN


# ==============================================================================
# Test: Global Instance
# ==============================================================================

def test_global_instance_singleton():
    """Test global instance is singleton."""
    manager1 = get_circuit_breaker_manager()
    manager2 = get_circuit_breaker_manager()

    assert manager1 is manager2


# ==============================================================================
# Test: Integration Scenarios
# ==============================================================================

def test_full_lifecycle():
    """Test full circuit breaker lifecycle."""
    config = CircuitBreakerConfig(
        failure_threshold=2,
        success_threshold=2,
        timeout_seconds=1
    )
    breaker = CircuitBreaker("anthropic", config=config)

    # 1. CLOSED: Normal operation
    assert breaker.state == CircuitState.CLOSED
    breaker.call(success_func)

    # 2. CLOSED → OPEN: Failures exceed threshold
    for _ in range(2):
        with pytest.raises(Exception):
            breaker.call(failure_func)
    assert breaker.state == CircuitState.OPEN

    # 3. OPEN: Requests rejected
    result = breaker.call(failure_func, fallback_func=fallback_func)
    assert result == "fallback"

    # 4. OPEN → HALF_OPEN: Timeout elapsed
    time.sleep(1.1)
    breaker.call(success_func)
    assert breaker.state == CircuitState.HALF_OPEN

    # 5. HALF_OPEN → CLOSED: Successful recovery
    breaker.call(success_func)
    assert breaker.state == CircuitState.CLOSED
