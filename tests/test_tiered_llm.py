"""Tests for Tiered LLM Provider - Cost Optimization System."""

import sys
import os
from pathlib import Path

sys.path.insert(0, '.')


class TestModelTierConfiguration:
    """Test model tier configuration loading."""

    def test_config_file_exists(self):
        """Test that config file exists."""
        config_path = Path("config/model_tiers.yaml")
        assert config_path.exists(), "config/model_tiers.yaml should exist"

    def test_config_has_all_tiers(self):
        """Test that config defines all required tiers."""
        from src.consortium.tiered_llm_provider import TieredLLMProvider

        provider = TieredLLMProvider()
        config = provider.config

        assert "model_tiers" in config
        assert "reasoning" in config["model_tiers"]
        assert "standard" in config["model_tiers"]
        assert "fast" in config["model_tiers"]
        assert "embedding" in config["model_tiers"]

        print("✓ All 4 tiers defined in config")

    def test_reasoning_tier_eu_first(self):
        """Test reasoning tier prioritizes EU (Mistral)."""
        from src.consortium.tiered_llm_provider import TieredLLMProvider

        provider = TieredLLMProvider()
        reasoning_config = provider.config["model_tiers"]["reasoning"]

        # Primary should be Mistral (EU)
        assert reasoning_config["primary"]["provider"] == "mistral"
        assert "mistral-large" in reasoning_config["primary"]["model"]

        print("✓ Reasoning tier uses Mistral (EU) as primary")

    def test_fast_tier_cheapest_first(self):
        """Test fast tier prioritizes cheapest (Gemini Flash)."""
        from src.consortium.tiered_llm_provider import TieredLLMProvider

        provider = TieredLLMProvider()
        fast_config = provider.config["model_tiers"]["fast"]

        # Primary should be Google Gemini
        assert fast_config["primary"]["provider"] == "google"
        assert "gemini" in fast_config["primary"]["model"].lower()

        print("✓ Fast tier uses Gemini Flash (cheapest) as primary")


class TestTierRouting:
    """Test task-to-tier routing logic."""

    def test_agent_tasks_use_reasoning_tier(self):
        """Test all agent tasks route to REASONING tier."""
        from src.consortium.tiered_llm_provider import TieredLLMProvider, ModelTier

        provider = TieredLLMProvider()

        # All agents should use REASONING tier
        agent_tasks = [
            "agent_sovereign",
            "agent_intelligence_sovereign",
            "agent_economist",
            "agent_jurist",
            "agent_architect",
            "agent_ecosystem",
            "agent_philosopher",
            "agent_ethnographer",
            "agent_technologist",
            "agent_consumer_voice",
        ]

        for task in agent_tasks:
            tier = provider.get_tier_for_task(task)
            assert tier == ModelTier.REASONING, f"{task} should use REASONING tier"

        print(f"✓ All {len(agent_tasks)} agent tasks route to REASONING tier")

    def test_synthesis_uses_standard_tier(self):
        """Test synthesis tasks route to STANDARD tier."""
        from src.consortium.tiered_llm_provider import TieredLLMProvider, ModelTier

        provider = TieredLLMProvider()

        synthesis_tasks = ["synthesizer", "cla_gate", "architect_revision"]

        for task in synthesis_tasks:
            tier = provider.get_tier_for_task(task)
            assert tier == ModelTier.STANDARD, f"{task} should use STANDARD tier"

        print(f"✓ All {len(synthesis_tasks)} synthesis tasks route to STANDARD tier")

    def test_router_uses_fast_tier(self):
        """Test router uses FAST tier."""
        from src.consortium.tiered_llm_provider import TieredLLMProvider, ModelTier

        provider = TieredLLMProvider()

        fast_tasks = ["router", "convergence_test"]

        for task in fast_tasks:
            tier = provider.get_tier_for_task(task)
            assert tier == ModelTier.FAST, f"{task} should use FAST tier"

        print(f"✓ All {len(fast_tasks)} fast tasks route to FAST tier")


class TestCostTracking:
    """Test cost tracking functionality."""

    def test_cost_tracker_initializes_correctly(self):
        """Test cost tracker starts at zero."""
        from src.consortium.tiered_llm_provider import CostTracker

        tracker = CostTracker()

        assert tracker.total_cost_usd == 0.0
        assert tracker.costs_by_tier["reasoning"] == 0.0
        assert tracker.costs_by_tier["standard"] == 0.0
        assert tracker.costs_by_tier["fast"] == 0.0
        assert tracker.costs_by_tier["embedding"] == 0.0

        print("✓ Cost tracker initializes to $0")

    def test_cost_tracker_records_calls(self):
        """Test cost tracker accumulates costs."""
        from src.consortium.tiered_llm_provider import CostTracker

        tracker = CostTracker()

        # Simulate reasoning call (expensive - Mistral Large)
        cost1 = tracker.record(
            tier="reasoning",
            provider="mistral",
            input_tokens=1000,
            output_tokens=500,
            costs={"input": 2.0, "output": 6.0},  # EUR per 1M tokens
            currency="EUR"
        )

        # Simulate fast call (cheap - Gemini Flash)
        cost2 = tracker.record(
            tier="fast",
            provider="google",
            input_tokens=500,
            output_tokens=200,
            costs={"input": 0.075, "output": 0.30},  # USD per 1M tokens
            currency="USD"
        )

        assert tracker.total_cost_usd > 0
        assert cost1 > cost2, "Reasoning should cost more than fast"
        assert tracker.calls_by_tier["reasoning"] == 1
        assert tracker.calls_by_tier["fast"] == 1

        print(f"✓ Cost tracking works: ${tracker.total_cost_usd:.6f}")
        print(f"  - Reasoning call: ${cost1:.6f}")
        print(f"  - Fast call: ${cost2:.6f}")

    def test_cost_tracker_can_reset(self):
        """Test cost tracker can be reset."""
        from src.consortium.tiered_llm_provider import CostTracker

        tracker = CostTracker()

        # Record some costs
        tracker.record("reasoning", "mistral", 1000, 500, {"input": 2.0, "output": 6.0}, "EUR")

        assert tracker.total_cost_usd > 0

        # Reset
        tracker.reset()

        assert tracker.total_cost_usd == 0.0
        assert tracker.calls_by_tier["reasoning"] == 0

        print("✓ Cost tracker resets correctly")

    def test_cost_summary_format(self):
        """Test cost summary returns correct format."""
        from src.consortium.tiered_llm_provider import CostTracker

        tracker = CostTracker()
        tracker.record("reasoning", "mistral", 1000, 500, {"input": 2.0, "output": 6.0}, "EUR")

        summary = tracker.summary()

        assert "total_cost_usd" in summary
        assert "costs_by_tier" in summary
        assert "calls_by_tier" in summary
        assert "calls_by_provider" in summary

        print(f"✓ Cost summary format correct: {summary}")


class TestTieredProviderIntegration:
    """Test integration with agent base class."""

    def test_agents_use_tiered_provider(self):
        """Test that agents use the tiered provider."""
        # This will be tested by checking the agent base class imports
        from agents.base import Agent

        # Check that _get_llm_provider imports tiered provider
        import inspect
        source = inspect.getsource(Agent._get_llm_provider)

        assert "tiered_llm_provider" in source, "Agent should import tiered_llm_provider"
        assert "get_tiered_provider" in source, "Agent should call get_tiered_provider"

        print("✓ Agent base class uses tiered provider")

    def test_agents_route_to_reasoning_tier(self):
        """Test that agents route to reasoning tier."""
        from agents.base import Agent
        import inspect

        source = inspect.getsource(Agent._invoke_llm)

        # Should call with task=f"agent_{self.agent_id}"
        assert "task=" in source, "Should specify task parameter"
        assert "agent_" in source, "Task should include agent_ prefix"

        print("✓ Agents route to REASONING tier via task parameter")


class TestCostOptimizationStrategy:
    """Test overall cost optimization strategy."""

    def test_reasoning_more_expensive_than_fast(self):
        """Test reasoning tier costs more than fast tier."""
        from src.consortium.tiered_llm_provider import TieredLLMProvider

        provider = TieredLLMProvider()

        reasoning_cost = provider.config["model_tiers"]["reasoning"]["cost_per_1m_tokens"]
        fast_cost = provider.config["model_tiers"]["fast"]["cost_per_1m_tokens"]

        # Reasoning should cost significantly more
        reasoning_total = reasoning_cost["input"] + reasoning_cost["output"]
        fast_total = fast_cost["input"] + fast_cost["output"]

        assert reasoning_total > fast_total * 5, "Reasoning should be much more expensive"

        print(f"✓ Cost optimization strategy correct:")
        print(f"  - Reasoning: €{reasoning_total}/M tokens")
        print(f"  - Fast: ${fast_total}/M tokens")

    def test_zero_llm_nodes_documented(self):
        """Test that ZERO-LLM nodes are documented."""
        zero_llm_files = [
            "src/consortium/nodes/router.py",
            "src/consortium/nodes/synthesizer.py",
            "src/consortium/nodes/tension_detector.py",
        ]

        for filepath in zero_llm_files:
            with open(filepath, 'r') as f:
                content = f.read()

            assert "ZERO-LLM" in content or "no LLM" in content or "FREE" in content, \
                f"{filepath} should document ZERO-LLM optimization"

        print(f"✓ All {len(zero_llm_files)} ZERO-LLM nodes documented")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Tiered LLM Provider - Cost Optimization")
    print("=" * 60 + "\n")

    # Run tests manually
    test_classes = [
        TestModelTierConfiguration,
        TestTierRouting,
        TestCostTracking,
        TestTieredProviderIntegration,
        TestCostOptimizationStrategy,
    ]

    total_tests = 0
    passed_tests = 0

    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        print("-" * 60)

        test_instance = test_class()
        methods = [m for m in dir(test_instance) if m.startswith('test_')]

        for method_name in methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                passed_tests += 1
            except AssertionError as e:
                print(f"✗ {method_name} FAILED: {e}")
            except Exception as e:
                print(f"✗ {method_name} ERROR: {e}")

    print("\n" + "=" * 60)
    print(f"Test Results: {passed_tests}/{total_tests} passed")
    print("=" * 60 + "\n")

    sys.exit(0 if passed_tests == total_tests else 1)
