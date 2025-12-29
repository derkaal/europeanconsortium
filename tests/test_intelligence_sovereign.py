"""Tests for Intelligence Sovereign Agent - AI Sovereignty Guardian."""
import sys
import yaml

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


class TestIntelligenceSovereignAgent:
    """Test Intelligence Sovereign agent."""
    
    def test_intelligence_sovereign_initialization(self):
        """Test Intelligence Sovereign agent initializes correctly."""
        from agents.intelligence_sovereign import IntelligenceSovereignAgent
        
        config = _get_minimal_config(
            "intelligence_sovereign",
            "The Intelligence Sovereign"
        )
        agent = IntelligenceSovereignAgent(config)
        
        assert agent.agent_id == "intelligence_sovereign"
        assert agent.name == "The Intelligence Sovereign"
        assert "Intelligence" in agent.system_prompt or \
               "AI" in agent.system_prompt
        print("✓ Intelligence Sovereign agent initialized")
    
    def test_intelligence_sovereign_with_full_config(self):
        """Test Intelligence Sovereign with full YAML config."""
        from agents.intelligence_sovereign import IntelligenceSovereignAgent
        
        with open('config/agents/intelligence_sovereign.yaml') as f:
            config = yaml.safe_load(f)
        
        agent = IntelligenceSovereignAgent(config)
        
        assert agent.agent_id == "intelligence_sovereign"
        assert len(agent.red_lines) > 0
        assert len(agent.knowledge_domains) > 0
        assert "Mistral" in str(agent.knowledge_domains) or \
               "Aleph Alpha" in str(agent.knowledge_domains)
        print("✓ Intelligence Sovereign loaded full config")
    
    def test_intelligence_sovereign_system_prompt(self):
        """Test Intelligence Sovereign has comprehensive system prompt."""
        from agents.intelligence_sovereign import (
            IntelligenceSovereignAgent,
            INTELLIGENCE_SOVEREIGN_SYSTEM_PROMPT
        )
        
        config = _get_minimal_config(
            "intelligence_sovereign",
            "The Intelligence Sovereign"
        )
        agent = IntelligenceSovereignAgent(config)
        
        # Should use built-in prompt if not in config
        assert agent.system_prompt == INTELLIGENCE_SOVEREIGN_SYSTEM_PROMPT
        
        # Check for key concepts
        prompt_lower = agent.system_prompt.lower()
        assert "intelligence" in prompt_lower
        assert "sovereignty" in prompt_lower
        assert any(term in prompt_lower for term in [
            "mistral", "aleph alpha", "llama", "open-weight"
        ])
        assert any(term in prompt_lower for term in [
            "gpt", "openai", "claude", "anthropic"
        ])
        print("✓ Intelligence Sovereign system prompt comprehensive")
    
    def test_intelligence_sovereign_red_lines(self):
        """Test Intelligence Sovereign red lines are defined."""
        from agents.intelligence_sovereign import IntelligenceSovereignAgent
        
        with open('config/agents/intelligence_sovereign.yaml') as f:
            config = yaml.safe_load(f)
        
        agent = IntelligenceSovereignAgent(config)
        
        # Should have red lines about AI sovereignty
        red_lines_str = " ".join(agent.red_lines).lower()
        assert any(term in red_lines_str for term in [
            "strategic", "intelligence", "foreign", "ai"
        ])
        assert any(term in red_lines_str for term in [
            "fine-tuning", "lock-in", "exit"
        ])
        print("✓ Intelligence Sovereign red lines defined")
    
    def test_intelligence_sovereign_keywords(self):
        """Test Intelligence Sovereign has AI-specific keywords."""
        from agents.intelligence_sovereign import IntelligenceSovereignAgent
        
        config = _get_minimal_config(
            "intelligence_sovereign",
            "The Intelligence Sovereign"
        )
        agent = IntelligenceSovereignAgent(config)
        
        # Should have AI sovereignty keywords
        assert hasattr(agent, 'ai_sovereignty_keywords')
        keywords = agent.ai_sovereignty_keywords
        
        # Check for foreign AI providers
        assert any(term in keywords for term in [
            'gpt', 'openai', 'claude', 'anthropic', 'gemini'
        ])
        
        # Check for European/open alternatives
        assert any(term in keywords for term in [
            'mistral', 'aleph alpha', 'llama', 'open-weight'
        ])
        
        # Check for lock-in indicators
        assert any(term in keywords for term in [
            'fine-tuning', 'lock-in', 'strategic intelligence'
        ])
        print("✓ Intelligence Sovereign keywords defined")
    
    def test_intelligence_sovereign_invoke_gpt4_query(self):
        """Test Intelligence Sovereign response to GPT-4 query."""
        from agents.intelligence_sovereign import IntelligenceSovereignAgent
        
        with open('config/agents/intelligence_sovereign.yaml') as f:
            config = yaml.safe_load(f)
        
        agent = IntelligenceSovereignAgent(config)
        
        state = {
            "query": "Should we use GPT-4 for competitive analysis?",
            "context": {
                "use_case": "Strategic Planning",
                "data_sensitivity": "High"
            }
        }
        
        response = agent.invoke(state)
        
        # Should BLOCK strategic intelligence on foreign AI
        assert response.rating in ["BLOCK", "WARN"]
        assert response.confidence > 0.7
        assert "strategic" in response.reasoning.lower() or \
               "intelligence" in response.reasoning.lower()
        print(f"✓ Intelligence Sovereign GPT-4 query: "
              f"{response.rating} ({response.confidence})")
    
    def test_intelligence_sovereign_invoke_mistral_query(self):
        """Test Intelligence Sovereign response to Mistral AI query."""
        from agents.intelligence_sovereign import IntelligenceSovereignAgent
        
        with open('config/agents/intelligence_sovereign.yaml') as f:
            config = yaml.safe_load(f)
        
        agent = IntelligenceSovereignAgent(config)
        
        state = {
            "query": "Should we use Mistral AI for our AI infrastructure?",
            "context": {
                "use_case": "AI Platform",
                "provider": "European"
            }
        }
        
        response = agent.invoke(state)
        
        # Should ENDORSE or ACCEPT European AI
        assert response.rating in ["ENDORSE", "ACCEPT"]
        assert response.confidence > 0.7
        print(f"✓ Intelligence Sovereign Mistral query: "
              f"{response.rating} ({response.confidence})")
    
    def test_intelligence_sovereign_invoke_finetuning_query(self):
        """Test Intelligence Sovereign response to fine-tuning query."""
        from agents.intelligence_sovereign import IntelligenceSovereignAgent
        
        with open('config/agents/intelligence_sovereign.yaml') as f:
            config = yaml.safe_load(f)
        
        agent = IntelligenceSovereignAgent(config)
        
        state = {
            "query": "Should we invest €75K in OpenAI fine-tuning?",
            "context": {
                "budget": "€75K",
                "use_case": "Custom Model"
            }
        }
        
        response = agent.invoke(state)
        
        # Should WARN or BLOCK about fine-tuning lock-in
        assert response.rating in ["BLOCK", "WARN"]
        assert "fine-tun" in response.reasoning.lower() or \
               "lock-in" in response.reasoning.lower()
        print(f"✓ Intelligence Sovereign fine-tuning query: "
              f"{response.rating} ({response.confidence})")
    
    def test_intelligence_sovereign_validation_rules(self):
        """Test Intelligence Sovereign validation rules."""
        from agents.intelligence_sovereign import IntelligenceSovereignAgent
        from agents.base import AgentResponse
        
        config = _get_minimal_config(
            "intelligence_sovereign",
            "The Intelligence Sovereign"
        )
        agent = IntelligenceSovereignAgent(config)
        
        # Test Rule 1: Never ENDORSE single provider dependency
        response = AgentResponse(
            agent_id="intelligence_sovereign",
            rating="ENDORSE",
            confidence=0.9,
            reasoning="This uses only OpenAI with no fallback"
        )
        validated = agent._validate_response(response)
        assert validated.rating == "ACCEPT"  # Should downgrade
        print("✓ Validation rule 1: Single provider dependency")
        
        # Test Rule 2: BLOCK strategic intelligence exposure
        response = AgentResponse(
            agent_id="intelligence_sovereign",
            rating="ACCEPT",
            confidence=0.8,
            reasoning="Strategic intelligence sent to GPT-4"
        )
        validated = agent._validate_response(response)
        assert validated.rating == "BLOCK"  # Should upgrade to BLOCK
        print("✓ Validation rule 2: Strategic intelligence exposure")
        
        # Test Rule 3: High confidence for BLOCK ratings
        response = AgentResponse(
            agent_id="intelligence_sovereign",
            rating="BLOCK",
            confidence=0.6,
            reasoning="AI sovereignty violation"
        )
        validated = agent._validate_response(response)
        assert validated.confidence >= 0.85  # Should boost confidence
        print("✓ Validation rule 3: High confidence for blocks")
    
    def test_intelligence_sovereign_response_structure(self):
        """Test Intelligence Sovereign returns proper response structure."""
        from agents.intelligence_sovereign import IntelligenceSovereignAgent
        
        with open('config/agents/intelligence_sovereign.yaml') as f:
            config = yaml.safe_load(f)
        
        agent = IntelligenceSovereignAgent(config)
        
        state = {
            "query": "Evaluate AI provider options",
            "context": {}
        }
        
        response = agent.invoke(state)
        
        # Check response structure
        assert hasattr(response, 'agent_id')
        assert hasattr(response, 'rating')
        assert hasattr(response, 'confidence')
        assert hasattr(response, 'reasoning')
        assert response.rating in ["BLOCK", "WARN", "ACCEPT", "ENDORSE"]
        assert 0 <= response.confidence <= 1
        assert len(response.reasoning) > 0
        print("✓ Intelligence Sovereign response structure valid")
    
    def test_intelligence_sovereign_integration_with_executor(self):
        """Test Intelligence Sovereign integrates with agent executor."""
        from src.consortium.nodes.agent_executor import agent_executor_node
        
        state = {
            "query": "Should we use Claude for strategic planning?",
            "context": {"use_case": "Strategy"},
            "triggered_agents": ["intelligence_sovereign"]
        }
        
        result = agent_executor_node(state)
        
        assert "agent_responses" in result
        assert "intelligence_sovereign" in result["agent_responses"]
        
        response = result["agent_responses"]["intelligence_sovereign"]
        assert "rating" in response
        assert "confidence" in response
        assert "reasoning" in response
        print("✓ Intelligence Sovereign integrates with executor")
    
    def test_intelligence_sovereign_integration_with_router(self):
        """Test Intelligence Sovereign is triggered by router."""
        from src.consortium.nodes.router import router_node
        
        state = {
            "query": "AI infrastructure strategy"
        }
        
        result = router_node(state)
        
        assert "triggered_agents" in result
        assert "intelligence_sovereign" in result["triggered_agents"]
        print("✓ Intelligence Sovereign triggered by router")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
