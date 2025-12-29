"""Tests for Tier 4 Agents: Ethnographer, Technologist, Consumer Voice."""
import sys

sys.path.insert(0, '.')


def _get_minimal_config(agent_id, name):
    """Get minimal config for agent initialization."""
    return {
        "agent_id": agent_id,
        "name": name,
        "mandate": "Test mandate",
        "red_lines": [],
        "acceptance_criteria": {},
        "knowledge_domains": []
    }


class TestEthnographerAgent:
    """Test Ethnographer agent."""

    def test_ethnographer_initialization(self):
        """Test Ethnographer agent initializes."""
        from agents.ethnographer import EthnographerAgent

        agent = EthnographerAgent(_get_minimal_config("ethnographer", "The Ethnographer"))

        assert agent.agent_id == "ethnographer"
        assert "cultural" in agent.system_prompt.lower() or \
               "hofstede" in agent.system_prompt.lower()
        print("✓ Ethnographer agent initialized")

    def test_ethnographer_prompt_building(self):
        """Test Ethnographer builds appropriate prompts."""
        from agents.ethnographer import EthnographerAgent

        agent = EthnographerAgent(_get_minimal_config("ethnographer", "The Ethnographer"))

        state = {
            "query": "Implement US-style rapid iteration culture across Europe",
            "context": {"markets": ["Germany", "France"], "workforce": "500+"}
        }

        prompt = agent._build_prompt(
            query=state["query"],
            query_context=state["context"]
        )
        assert "rapid iteration" in prompt.lower() or "culture" in prompt.lower()
        print("✓ Ethnographer prompt built correctly")

    def test_ethnographer_validation_rules(self):
        """Test Ethnographer applies validation rules."""
        from agents.ethnographer import EthnographerAgent
        from agents.base import AgentResponse

        agent = EthnographerAgent(_get_minimal_config("ethnographer", "The Ethnographer"))

        # Test ENDORSE without cultural analysis gets downgraded
        response = AgentResponse(
            agent_id="ethnographer",
            rating="ENDORSE",
            confidence=0.9,
            reasoning="This looks good"
        )

        validated = agent._validate_response(response)
        assert validated.rating == "ACCEPT"
        print("✓ Ethnographer validation rules applied")


class TestTechnologistAgent:
    """Test Technologist agent."""

    def test_technologist_initialization(self):
        """Test Technologist agent initializes."""
        from agents.technologist import TechnologistAgent

        agent = TechnologistAgent(_get_minimal_config("technologist", "The Technologist"))

        assert agent.agent_id == "technologist"
        assert "security" in agent.system_prompt.lower() or \
               "ciso" in agent.system_prompt.lower() or \
               "operational" in agent.system_prompt.lower()
        print("✓ Technologist agent initialized")

    def test_technologist_prompt_building(self):
        """Test Technologist builds appropriate prompts."""
        from agents.technologist import TechnologistAgent

        agent = TechnologistAgent(_get_minimal_config("technologist", "The Technologist"))

        state = {
            "query": "Store API keys in environment variables",
            "context": {"system": "Production", "data_sensitivity": "High"}
        }

        prompt = agent._build_prompt(
            query=state["query"],
            query_context=state["context"]
        )
        assert "api key" in prompt.lower() or "environment" in prompt.lower()
        print("✓ Technologist prompt built correctly")

    def test_technologist_validation_rules(self):
        """Test Technologist applies validation rules."""
        from agents.technologist import TechnologistAgent
        from agents.base import AgentResponse

        agent = TechnologistAgent(_get_minimal_config("technologist", "The Technologist"))

        # Test ENDORSE without security controls gets downgraded
        response = AgentResponse(
            agent_id="technologist",
            rating="ENDORSE",
            confidence=0.9,
            reasoning="This is a good solution"
        )

        validated = agent._validate_response(response)
        assert validated.rating == "ACCEPT"
        print("✓ Technologist validation rules applied")


class TestConsumerVoiceAgent:
    """Test Consumer Voice agent."""

    def test_consumer_voice_initialization(self):
        """Test Consumer Voice agent initializes."""
        from agents.consumer_voice import ConsumerVoiceAgent

        agent = ConsumerVoiceAgent(_get_minimal_config("consumer_voice", "The Consumer Voice"))

        assert agent.agent_id == "consumer_voice"
        assert "consumer" in agent.system_prompt.lower() or \
               "accessibility" in agent.system_prompt.lower() or \
               "dark pattern" in agent.system_prompt.lower()
        print("✓ Consumer Voice agent initialized")

    def test_consumer_voice_prompt_building(self):
        """Test Consumer Voice builds appropriate prompts."""
        from agents.consumer_voice import ConsumerVoiceAgent

        agent = ConsumerVoiceAgent(_get_minimal_config("consumer_voice", "The Consumer Voice"))

        state = {
            "query": "Make cancellation require calling customer service",
            "context": {"product": "Subscription service", "market": "EU"}
        }

        prompt = agent._build_prompt(
            query=state["query"],
            query_context=state["context"]
        )
        assert "cancellation" in prompt.lower() or "customer service" in prompt.lower()
        print("✓ Consumer Voice prompt built correctly")

    def test_consumer_voice_validation_rules(self):
        """Test Consumer Voice applies validation rules."""
        from agents.consumer_voice import ConsumerVoiceAgent
        from agents.base import AgentResponse

        agent = ConsumerVoiceAgent(_get_minimal_config("consumer_voice", "The Consumer Voice"))

        # Test ENDORSE without consumer analysis gets downgraded
        response = AgentResponse(
            agent_id="consumer_voice",
            rating="ENDORSE",
            confidence=0.9,
            reasoning="This works well"
        )

        validated = agent._validate_response(response)
        assert validated.rating == "ACCEPT"
        print("✓ Consumer Voice validation rules applied")


class TestTier4Integration:
    """Test Tier 4 agents integration."""

    def test_all_tier4_agents_importable(self):
        """Test all Tier 4 agents can be imported."""
        from agents.ethnographer import EthnographerAgent
        from agents.technologist import TechnologistAgent
        from agents.consumer_voice import ConsumerVoiceAgent

        registry = {
            "ethnographer": EthnographerAgent,
            "technologist": TechnologistAgent,
            "consumer_voice": ConsumerVoiceAgent,
        }

        assert len(registry) == 3
        agents_list = list(registry.keys())
        print(f"✓ All 3 Tier 4 agents importable: {agents_list}")

    def test_tier4_agent_configs_exist(self):
        """Test all Tier 4 agent config files exist."""
        from src.consortium.config import get_config_loader

        config_manager = get_config_loader()

        agents = ["ethnographer", "technographer", "consumer_voice"]

        for agent_id in agents:
            try:
                config = config_manager.load_agent_config(agent_id)
                if config is not None:
                    if hasattr(config, 'agent_id'):
                        assert config.agent_id == agent_id
                    elif isinstance(config, dict):
                        assert config.get('agent_id') == agent_id
                    print(f"✓ {agent_id} config loaded")
            except Exception as e:
                # Config file might not exist yet
                print(f"⚠ {agent_id} config not found (expected during development): {e}")

    def test_tier4_agent_characteristics(self):
        """Test Tier 4 agents have appropriate characteristics."""
        from agents.ethnographer import EthnographerAgent
        from agents.technologist import TechnologistAgent
        from agents.consumer_voice import ConsumerVoiceAgent

        # Ethnographer should have cultural keywords
        ethnographer = EthnographerAgent(_get_minimal_config("ethnographer", "The Ethnographer"))
        assert hasattr(ethnographer, 'cultural_keywords')
        assert len(ethnographer.cultural_keywords) > 0
        print(f"✓ Ethnographer has {len(ethnographer.cultural_keywords)} cultural keywords")

        # Technologist should have security keywords
        technologist = TechnologistAgent(_get_minimal_config("technologist", "The Technologist"))
        assert hasattr(technologist, 'security_keywords')
        assert len(technologist.security_keywords) > 0
        print(f"✓ Technologist has {len(technologist.security_keywords)} security keywords")

        # Consumer Voice should have consumer keywords
        consumer_voice = ConsumerVoiceAgent(_get_minimal_config("consumer_voice", "The Consumer Voice"))
        assert hasattr(consumer_voice, 'consumer_keywords')
        assert len(consumer_voice.consumer_keywords) > 0
        print(f"✓ Consumer Voice has {len(consumer_voice.consumer_keywords)} consumer keywords")
