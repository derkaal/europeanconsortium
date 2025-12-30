"""
Tiered LLM Provider - Cost-Optimized Multi-Model Strategy

Strategy:
- Reasoning: EU-first (Mistral Large) for complex agent analysis
- Standard: Cheapest (Gemini Flash) for synthesis and formatting
- Fast: Cheapest (Gemini Flash) for classification and routing
- Embedding: Cheapest (Google Embedding) for memory operations
"""

import os
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model tiers matched to task complexity and cost strategy."""
    REASONING = "reasoning"    # EU-first: Mistral Large → Claude → GPT-4
    STANDARD = "standard"      # Cheapest: Gemini Flash → GPT-4o-mini → Mistral Small
    FAST = "fast"             # Cheapest: Gemini Flash → GPT-4o-mini → Mistral Small
    EMBEDDING = "embedding"    # Cheapest: Google Embedding → OpenAI → Mistral


@dataclass
class CostTracker:
    """Track LLM costs across the system."""

    total_cost_usd: float = 0.0
    costs_by_tier: Dict[str, float] = field(default_factory=lambda: {
        "reasoning": 0.0,
        "standard": 0.0,
        "fast": 0.0,
        "embedding": 0.0
    })
    calls_by_tier: Dict[str, int] = field(default_factory=lambda: {
        "reasoning": 0,
        "standard": 0,
        "fast": 0,
        "embedding": 0
    })
    calls_by_provider: Dict[str, int] = field(default_factory=lambda: {
        "mistral": 0,
        "anthropic": 0,
        "openai": 0,
        "google": 0
    })

    def record(
        self,
        tier: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        costs: Dict[str, float],
        currency: str = "USD"
    ) -> float:
        """Record a call's cost."""
        input_cost = (input_tokens / 1_000_000) * costs.get("input", 0)
        output_cost = (output_tokens / 1_000_000) * costs.get("output", 0)
        total = input_cost + output_cost

        # Convert EUR to USD if needed (approximate)
        if currency == "EUR":
            total_usd = total * 1.10  # Rough conversion
        else:
            total_usd = total

        self.total_cost_usd += total_usd
        self.costs_by_tier[tier] += total_usd
        self.calls_by_tier[tier] += 1
        self.calls_by_provider[provider] += 1

        logger.info(
            f"💰 LLM Cost: ${total_usd:.6f} | tier={tier} | provider={provider} | "
            f"tokens_in={input_tokens} | tokens_out={output_tokens}"
        )

        return total_usd

    def summary(self) -> Dict[str, Any]:
        """Get cost summary."""
        return {
            "total_cost_usd": round(self.total_cost_usd, 6),
            "costs_by_tier": {k: round(v, 6) for k, v in self.costs_by_tier.items()},
            "calls_by_tier": dict(self.calls_by_tier),
            "calls_by_provider": dict(self.calls_by_provider)
        }

    def reset(self):
        """Reset all counters."""
        self.total_cost_usd = 0.0
        for key in self.costs_by_tier:
            self.costs_by_tier[key] = 0.0
            self.calls_by_tier[key] = 0
        for key in self.calls_by_provider:
            self.calls_by_provider[key] = 0


class TieredLLMProvider:
    """
    Multi-tier LLM provider with EU-first reasoning and cheapest-first for other tasks.

    Tier Strategy:
    - REASONING: Mistral Large (EU) → Claude Sonnet → GPT-4o
    - STANDARD: Gemini Flash → GPT-4o-mini → Mistral Small
    - FAST: Gemini Flash → GPT-4o-mini → Mistral Small
    - EMBEDDING: Gemini Embedding → OpenAI Embedding → Mistral Embed
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the tiered LLM provider."""
        self.config = self._load_config(config_path)
        self.cost_tracker = CostTracker()
        self.clients: Dict[str, Any] = {}
        self._init_clients()
        self.task_routing = self.config.get("task_routing", {})

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load tier configuration from YAML file."""
        if config_path:
            path = Path(config_path)
        else:
            path = Path("config/model_tiers.yaml")

        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f)

        logger.warning(f"Config not found at {path}, using defaults")
        return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Default configuration matching our cost optimization strategy."""
        return {
            "model_tiers": {
                "reasoning": {
                    "primary": {"provider": "mistral", "model": "mistral-large-latest", "max_tokens": 4096, "temperature": 0.7},
                    "fallback_1": {"provider": "anthropic", "model": "claude-sonnet-4-20250514", "max_tokens": 4096, "temperature": 0.7},
                    "fallback_2": {"provider": "openai", "model": "gpt-4o", "max_tokens": 4096, "temperature": 0.7},
                    "cost_per_1m_tokens": {"input": 2.0, "output": 6.0},
                    "currency": "EUR"
                },
                "standard": {
                    "primary": {"provider": "google", "model": "gemini-1.5-flash", "max_tokens": 4096, "temperature": 0.3},
                    "fallback_1": {"provider": "openai", "model": "gpt-4o-mini", "max_tokens": 4096, "temperature": 0.3},
                    "fallback_2": {"provider": "mistral", "model": "mistral-small-latest", "max_tokens": 4096, "temperature": 0.3},
                    "cost_per_1m_tokens": {"input": 0.075, "output": 0.30},
                    "currency": "USD"
                },
                "fast": {
                    "primary": {"provider": "google", "model": "gemini-1.5-flash", "max_tokens": 1024, "temperature": 0.1},
                    "fallback_1": {"provider": "openai", "model": "gpt-4o-mini", "max_tokens": 1024, "temperature": 0.1},
                    "fallback_2": {"provider": "mistral", "model": "mistral-small-latest", "max_tokens": 1024, "temperature": 0.1},
                    "cost_per_1m_tokens": {"input": 0.075, "output": 0.30},
                    "currency": "USD"
                },
                "embedding": {
                    "primary": {"provider": "google", "model": "text-embedding-004", "dimensions": 768},
                    "fallback_1": {"provider": "openai", "model": "text-embedding-3-small", "dimensions": 1536},
                    "fallback_2": {"provider": "mistral", "model": "mistral-embed", "dimensions": 1024},
                    "cost_per_1m_tokens": {"input": 0.00625, "output": 0.0},
                    "currency": "USD"
                }
            },
            "task_routing": {
                "agent_sovereign": "reasoning",
                "agent_intelligence_sovereign": "reasoning",
                "agent_economist": "reasoning",
                "agent_jurist": "reasoning",
                "agent_architect": "reasoning",
                "agent_ecosystem": "reasoning",
                "agent_philosopher": "reasoning",
                "agent_ethnographer": "reasoning",
                "agent_technologist": "reasoning",
                "agent_consumer_voice": "reasoning",
                "synthesizer": "standard",
                "cla_gate": "standard",
                "architect_revision": "standard",
                "router": "fast",
                "convergence_test": "fast",
                "memory_store": "embedding",
                "memory_retrieve": "embedding",
            }
        }

    def _init_clients(self):
        """Initialize LLM clients for each provider."""

        # Mistral (EU Sovereign - Primary for Reasoning)
        if os.getenv("MISTRAL_API_KEY"):
            try:
                from langchain_mistralai import ChatMistralAI
                # Create a basic client - we'll configure per-call
                self.clients["mistral"] = ChatMistralAI
                logger.info("✓ Mistral client initialized (EU Sovereign)")
            except ImportError:
                logger.warning("langchain-mistralai not installed: pip install langchain-mistralai")
        else:
            logger.warning("MISTRAL_API_KEY not set - EU sovereign reasoning unavailable")

        # Google Gemini (Primary for Standard/Fast)
        if os.getenv("GOOGLE_API_KEY"):
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.clients["google"] = ChatGoogleGenerativeAI
                logger.info("✓ Google Gemini client initialized (Cheapest)")
            except ImportError:
                logger.warning("langchain-google-genai not installed: pip install langchain-google-genai")
        else:
            logger.warning("GOOGLE_API_KEY not set - cheapest tier unavailable")

        # OpenAI (Fallback)
        if os.getenv("OPENAI_API_KEY"):
            try:
                from langchain_openai import ChatOpenAI
                self.clients["openai"] = ChatOpenAI
                logger.info("✓ OpenAI client initialized (Fallback)")
            except ImportError:
                logger.warning("langchain-openai not installed: pip install langchain-openai")

        # Anthropic (Fallback for Reasoning)
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                from langchain_anthropic import ChatAnthropic
                self.clients["anthropic"] = ChatAnthropic
                logger.info("✓ Anthropic client initialized (Fallback)")
            except ImportError:
                logger.warning("langchain-anthropic not installed: pip install langchain-anthropic")

    def get_tier_for_task(self, task: str) -> ModelTier:
        """Determine appropriate tier for a task."""
        tier_name = self.task_routing.get(task, "reasoning")
        return ModelTier(tier_name)

    def _get_model_config(self, tier: ModelTier) -> tuple:
        """Get model config with fallback chain."""
        tier_config = self.config["model_tiers"][tier.value]

        # Try primary, then fallbacks
        for key in ["primary", "fallback_1", "fallback_2"]:
            if key not in tier_config:
                continue

            model_config = tier_config[key]
            provider = model_config["provider"]

            if provider in self.clients:
                return model_config, tier_config

        raise RuntimeError(f"No available provider for tier {tier.value}")

    def invoke(
        self,
        prompt: str,
        task: str,
        system_prompt: Optional[str] = None,
        tier_override: Optional[ModelTier] = None,
    ) -> str:
        """
        Invoke LLM with appropriate tier for task.

        Args:
            prompt: The user prompt
            task: Task identifier (e.g., "agent_sovereign", "router")
            system_prompt: Optional system prompt
            tier_override: Force a specific tier

        Returns:
            LLM response text
        """
        from langchain_core.messages import SystemMessage, HumanMessage

        tier = tier_override or self.get_tier_for_task(task)
        model_config, tier_config = self._get_model_config(tier)

        provider = model_config["provider"]
        model = model_config["model"]
        max_tokens = model_config.get("max_tokens", 4096)
        temperature = model_config.get("temperature", 0.7)

        logger.info(f"🤖 LLM invoke: task={task}, tier={tier.value}, provider={provider}, model={model}")

        # Build messages
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        # Try providers in fallback order
        last_error = None
        for attempt_key in ["primary", "fallback_1", "fallback_2"]:
            if attempt_key not in tier_config:
                continue

            attempt_config = tier_config[attempt_key]
            attempt_provider = attempt_config["provider"]

            if attempt_provider not in self.clients:
                continue

            try:
                # Create client instance with specific configuration
                client_class = self.clients[attempt_provider]
                
                # Shorter timeout for Mistral to fail fast and fallback
                timeout = 30 if attempt_provider == "mistral" else 60
                
                client = client_class(
                    model=attempt_config["model"],
                    temperature=attempt_config.get("temperature", 0.7),
                    max_tokens=attempt_config.get("max_tokens", 4096),
                    timeout=timeout,
                    max_retries=1 if attempt_provider == "mistral" else 2
                )

                # Invoke
                response = client.invoke(messages)
                content = response.content

                # Estimate tokens (rough approximation)
                input_tokens = len(prompt.split()) * 1.3 + (len(system_prompt.split()) * 1.3 if system_prompt else 0)
                output_tokens = len(content.split()) * 1.3

                # Track costs
                self.cost_tracker.record(
                    tier.value,
                    attempt_provider,
                    int(input_tokens),
                    int(output_tokens),
                    tier_config.get("cost_per_1m_tokens", {}),
                    tier_config.get("currency", "USD")
                )

                logger.info(f"✓ {attempt_provider} succeeded for {task}")
                return content

            except Exception as e:
                logger.warning(f"✗ {attempt_provider} failed for {task}: {e}")
                last_error = e
                continue

        # All providers failed
        raise RuntimeError(f"All providers failed for tier {tier.value}. Last error: {last_error}")

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary."""
        return self.cost_tracker.summary()

    def reset_cost_tracking(self):
        """Reset cost counters (e.g., between queries)."""
        self.cost_tracker.reset()


# Singleton instance
_tiered_provider: Optional[TieredLLMProvider] = None


def get_tiered_provider() -> TieredLLMProvider:
    """Get or create the tiered LLM provider singleton."""
    global _tiered_provider
    if _tiered_provider is None:
        _tiered_provider = TieredLLMProvider()
    return _tiered_provider


def reset_tiered_provider():
    """Reset the singleton (useful for testing)."""
    global _tiered_provider
    _tiered_provider = None
