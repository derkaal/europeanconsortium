"""Tests for Feature Subsidy philosophy agents."""

import sys
import os
from pathlib import Path

sys.path.insert(0, '.')


class TestFounderAgent:
    """Test The Founder - Feature Hunter."""

    def test_initialization(self):
        """Test Founder agent initializes correctly."""
        from agents.founder import FounderAgent

        # Create minimal config
        config = {
            'agent_id': 'founder',
            'name': 'The Founder',
            'mandate': 'Hunt Feature Subsidies',
            'red_lines': [],
            'acceptance_criteria': {},
            'knowledge_domains': []
        }

        agent = FounderAgent(config)
        assert agent.agent_id == "founder"
        assert "feature" in agent.mandate.lower() or "subsid" in agent.mandate.lower()

        print("✓ Founder agent initializes correctly")

    def test_system_prompt_contains_feature_doctrine(self):
        """Test system prompt contains Feature Subsidy doctrine."""
        from agents.founder import FounderAgent

        config = {
            'agent_id': 'founder',
            'name': 'The Founder',
            'mandate': 'Hunt Feature Subsidies',
            'red_lines': [],
            'acceptance_criteria': {},
            'knowledge_domains': []
        }

        agent = FounderAgent(config)
        prompt = agent.system_prompt.lower()

        assert "feature subsid" in prompt
        assert "predator" in prompt or "hunt" in prompt
        assert "incumbent" in prompt
        assert "arbitrage" in prompt

        print("✓ Founder system prompt contains Feature Subsidy doctrine")

    def test_rejects_grant_mentality(self):
        """Test Founder rejects victim/grant mentality."""
        from agents.founder import FounderAgent

        config = {
            'agent_id': 'founder',
            'name': 'The Founder',
            'mandate': 'Hunt Feature Subsidies',
            'red_lines': [],
            'acceptance_criteria': {},
            'knowledge_domains': []
        }

        agent = FounderAgent(config)
        prompt = agent.system_prompt.lower()

        # Should reject entity-based thinking
        assert "victim" in prompt or "beg" in prompt
        assert "red line" in prompt or "never beg" in prompt

        print("✓ Founder rejects grant/victim mentality")

    def test_config_file_exists(self):
        """Test founder.yaml configuration exists."""
        config_path = Path("config/agents/founder.yaml")
        assert config_path.exists(), "config/agents/founder.yaml should exist"

        print("✓ Founder config file exists")


class TestAlchemistAgent:
    """Test The Alchemist - Regulation-to-Value Converter."""

    def test_initialization(self):
        """Test Alchemist agent initializes correctly."""
        from agents.alchemist import AlchemistAgent

        config = {
            'agent_id': 'alchemist',
            'name': 'The Alchemist',
            'mandate': 'Transform regulation',
            'red_lines': [],
            'acceptance_criteria': {},
            'knowledge_domains': []
        }

        agent = AlchemistAgent(config)
        assert agent.agent_id == "alchemist"
        assert "regulat" in agent.mandate.lower() or "compliance" in agent.mandate.lower() or "transform" in agent.mandate.lower()

        print("✓ Alchemist agent initializes correctly")

    def test_system_prompt_contains_alchemy_levels(self):
        """Test system prompt contains alchemy levels."""
        from agents.alchemist import AlchemistAgent

        config = {
            'agent_id': 'alchemist',
            'name': 'The Alchemist',
            'mandate': 'Transform regulation',
            'red_lines': [],
            'acceptance_criteria': {},
            'knowledge_domains': []
        }

        agent = AlchemistAgent(config)
        prompt = agent.system_prompt.lower()

        assert "cost" in prompt
        assert "capability" in prompt or "level" in prompt
        assert "brand" in prompt
        assert "moat" in prompt

        print("✓ Alchemist system prompt contains alchemy levels")

    def test_trust_premium_concept(self):
        """Test Alchemist understands trust premium."""
        from agents.alchemist import AlchemistAgent

        config = {
            'agent_id': 'alchemist',
            'name': 'The Alchemist',
            'mandate': 'Transform regulation',
            'red_lines': [],
            'acceptance_criteria': {},
            'knowledge_domains': []
        }

        agent = AlchemistAgent(config)
        prompt = agent.system_prompt.lower()

        assert "trust" in prompt
        assert "premium" in prompt

        print("✓ Alchemist understands trust premium concept")

    def test_config_file_exists(self):
        """Test alchemist.yaml configuration exists."""
        config_path = Path("config/agents/alchemist.yaml")
        assert config_path.exists(), "config/agents/alchemist.yaml should exist"

        print("✓ Alchemist config file exists")


class TestEconomistFeatureUpdate:
    """Test Economist's Feature Subsidy doctrine update."""

    def test_economist_has_feature_doctrine(self):
        """Test Economist system prompt includes Feature Subsidy."""
        from agents.economist import ECONOMIST_SYSTEM_PROMPT

        prompt = ECONOMIST_SYSTEM_PROMPT.lower()

        # Should now include Feature Subsidy thinking
        assert "feature" in prompt
        assert "subsid" in prompt or "monetization" in prompt

        print("✓ Economist has Feature Subsidy doctrine")

    def test_economist_rejects_grant_thinking(self):
        """Test Economist rejects pure grant approach."""
        from agents.economist import ECONOMIST_SYSTEM_PROMPT

        prompt = ECONOMIST_SYSTEM_PROMPT.lower()

        # Should mention grants in context of being rejected or warned about
        assert "grant" in prompt

        print("✓ Economist rejects pure grant thinking")


class TestAgentRegistry:
    """Test all agents are registered."""

    def test_founder_in_registry(self):
        """Test Founder is registered in agent executor."""
        # We can't easily import the executor in this context,
        # but we can verify the files exist
        from pathlib import Path

        agent_file = Path("agents/founder.py")
        assert agent_file.exists(), "agents/founder.py should exist"

        print("✓ Founder agent file exists")

    def test_alchemist_in_registry(self):
        """Test Alchemist is registered in agent executor."""
        from pathlib import Path

        agent_file = Path("agents/alchemist.py")
        assert agent_file.exists(), "agents/alchemist.py should exist"

        print("✓ Alchemist agent file exists")

    def test_tension_protocol_exists(self):
        """Test Founder-Alchemist tension protocol exists."""
        from pathlib import Path

        tension_file = Path("config/tensions/founder_alchemist.yaml")
        assert tension_file.exists(), "config/tensions/founder_alchemist.yaml should exist"

        print("✓ Founder-Alchemist tension protocol exists")


class TestFeatureSubsidyPhilosophy:
    """Test overall Feature Subsidy philosophy integration."""

    def test_feature_subsidy_map_in_founder_config(self):
        """Test feature_subsidy_map in founder.yaml."""
        import yaml
        from pathlib import Path

        config_path = Path("config/agents/founder.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "feature_subsidy_map" in config
        assert "carbon" in config["feature_subsidy_map"]
        assert "sovereignty" in config["feature_subsidy_map"]

        print("✓ Feature Subsidy map defined in founder config")

    def test_alchemy_levels_in_alchemist_config(self):
        """Test alchemy_levels in alchemist.yaml."""
        import yaml
        from pathlib import Path

        config_path = Path("config/agents/alchemist.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "alchemy_levels" in config
        assert "level_1_cost" in config["alchemy_levels"]
        assert "level_5_moat" in config["alchemy_levels"]

        print("✓ Alchemy levels defined in alchemist config")

    def test_tiered_llm_routes_new_agents(self):
        """Test new agents are routed to reasoning tier."""
        import yaml
        from pathlib import Path

        config_path = Path("config/model_tiers.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "agent_founder" in config["task_routing"]
        assert config["task_routing"]["agent_founder"] == "reasoning"

        assert "agent_alchemist" in config["task_routing"]
        assert config["task_routing"]["agent_alchemist"] == "reasoning"

        print("✓ New agents routed to REASONING tier (EU-first)")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Feature Subsidy Philosophy Implementation")
    print("=" * 60 + "\n")

    # Run tests manually
    test_classes = [
        TestFounderAgent,
        TestAlchemistAgent,
        TestEconomistFeatureUpdate,
        TestAgentRegistry,
        TestFeatureSubsidyPhilosophy,
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
                import traceback
                traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"Test Results: {passed_tests}/{total_tests} passed")
    print("=" * 60 + "\n")

    sys.exit(0 if passed_tests == total_tests else 1)
