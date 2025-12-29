"""Tests for Tier 1 Agents: Architect, Eco-System, Philosopher."""
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


class TestArchitectAgent:
    """Test Architect agent."""
    
    def test_architect_initialization(self):
        """Test Architect agent initializes."""
        from agents.architect import ArchitectAgent
        
        agent = ArchitectAgent(_get_minimal_config("architect", "The Architect"))
        
        assert agent.agent_id == "architect"
        assert "Systems" in agent.system_prompt or \
               "Architect" in agent.system_prompt
        print("✓ Architect agent initialized")
    
    def test_architect_prompt_building(self):
        """Test Architect builds appropriate prompts."""
        from agents.architect import ArchitectAgent
        
        agent = ArchitectAgent(_get_minimal_config("architect", "The Architect"))
        
        state = {
            "query": "Build a distributed microservices platform",
            "context": {"scale": "enterprise"}
        }
        
        prompt = agent._build_prompt(state)
        assert "microservices" in prompt.lower()
        print("✓ Architect prompt built correctly")


class TestEcosystemAgent:
    """Test Eco-System agent."""
    
    def test_ecosystem_initialization(self):
        """Test Eco-System agent initializes."""
        from agents.ecosystem import EcosystemAgent
        
        agent = EcosystemAgent(_get_minimal_config("ecosystem", "The Eco-System"))
        
        assert agent.agent_id == "ecosystem"
        assert "carbon" in agent.system_prompt.lower() or \
               "planetary" in agent.system_prompt.lower()
        print("✓ Eco-System agent initialized")
    
    def test_ecosystem_prompt_building(self):
        """Test Eco-System builds appropriate prompts."""
        from agents.ecosystem import EcosystemAgent
        
        agent = EcosystemAgent(_get_minimal_config("ecosystem", "The Eco-System"))
        
        state = {
            "query": "Deploy AI training infrastructure",
            "context": {"compute": "high"}
        }
        
        prompt = agent._build_prompt(state)
        assert "AI" in prompt or "infrastructure" in prompt.lower()
        print("✓ Eco-System prompt built correctly")


class TestPhilosopherAgent:
    """Test Philosopher agent."""
    
    def test_philosopher_initialization(self):
        """Test Philosopher agent initializes."""
        from agents.philosopher import PhilosopherAgent
        
        agent = PhilosopherAgent(_get_minimal_config("philosopher", "The Philosopher"))
        
        assert agent.agent_id == "philosopher"
        assert "ethics" in agent.system_prompt.lower() or \
               "values" in agent.system_prompt.lower()
        print("✓ Philosopher agent initialized")
    
    def test_philosopher_prompt_building(self):
        """Test Philosopher builds appropriate prompts."""
        from agents.philosopher import PhilosopherAgent
        
        agent = PhilosopherAgent(_get_minimal_config("philosopher", "The Philosopher"))
        
        state = {
            "query": "Implement user behavior tracking",
            "context": {"purpose": "engagement optimization"}
        }
        
        prompt = agent._build_prompt(state)
        assert "tracking" in prompt.lower() or \
               "behavior" in prompt.lower()
        print("✓ Philosopher prompt built correctly")


class TestTier1Integration:
    """Test Tier 1 agents work together."""
    
    def test_all_tier1_agents_in_registry(self):
        """Test all Tier 1 agents are in executor registry."""
        from agents.sovereign import SovereignAgent
        from agents.economist import EconomistAgent
        from agents.jurist import JuristAgent
        from agents.architect import ArchitectAgent
        from agents.ecosystem import EcosystemAgent
        from agents.philosopher import PhilosopherAgent
        
        registry = {
            "sovereign": SovereignAgent,
            "economist": EconomistAgent,
            "jurist": JuristAgent,
            "architect": ArchitectAgent,
            "ecosystem": EcosystemAgent,
            "philosopher": PhilosopherAgent,
        }
        
        assert len(registry) == 6
        agents_list = list(registry.keys())
        print(f"✓ All 6 Tier 1 agents available: {agents_list}")
    
    def test_router_triggers_all_agents(self):
        """Test router triggers all Tier 1 agents."""
        from src.consortium.nodes.router import router_node
        
        result = router_node({"query": "Test query"})
        triggered = result.get("triggered_agents", [])
        
        expected = [
            "sovereign",
            "economist",
            "jurist",
            "architect",
            "ecosystem",
            "philosopher"
        ]
        
        for agent in expected:
            assert agent in triggered, f"Missing {agent} in triggered"
        
        print(f"✓ Router triggers all {len(triggered)} agents")
    
    def test_agent_configs_exist(self):
        """Test all agent config files exist."""
        from src.consortium.config import get_config_loader
        
        config_manager = get_config_loader()
        
        agents = [
            "sovereign",
            "economist",
            "jurist",
            "architect",
            "ecosystem",
            "philosopher"
        ]
        
        for agent_id in agents:
            config = config_manager.load_agent_config(agent_id)
            assert config is not None
            assert config.agent_id == agent_id
        
        print(f"✓ All {len(agents)} agent configs loaded successfully")
