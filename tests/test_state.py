"""
Unit tests for state schema implementation
"""

import pytest
from src.consortium.state import (
    ConsortiumState,
    create_initial_state
)


class TestConsortiumState:
    """Test ConsortiumState TypedDict"""
    
    def test_create_initial_state(self):
        """Test initial state creation"""
        query = "Should we migrate to AWS?"
        context = {"industry": "automotive", "company_size": "large"}
        
        state = create_initial_state(query, context)
        
        # Verify core fields
        assert state["query"] == query
        assert state["context"] == context
        
        # Verify initialization
        assert state["triggered_agents"] == []
        assert state["agent_responses"] == {}
        assert state["active_tensions"] == []
        assert state["convergence_status"] == {}
        assert state["final_recommendation"] == {}
        assert state["iteration_count"] == 0
    
    def test_create_initial_state_no_context(self):
        """Test initial state creation without context"""
        query = "Test query"
        
        state = create_initial_state(query)
        
        assert state["query"] == query
        assert state["context"] == {}
        assert state["triggered_agents"] == []
    
    def test_state_has_required_fields(self):
        """Test state has all required fields"""
        state = create_initial_state("Test", {})
        
        required_fields = [
            "query",
            "context",
            "triggered_agents",
            "agent_responses",
            "active_tensions",
            "convergence_status",
            "final_recommendation",
            "iteration_count"
        ]
        
        for field in required_fields:
            assert field in state, f"Missing required field: {field}"
    
    def test_state_agent_responses_structure(self):
        """Test agent responses can be added to state"""
        state = create_initial_state("Test query", {})
        
        # Simulate adding agent responses
        state["agent_responses"] = {
            "sovereign": {
                "rating": "BLOCK",
                "confidence": 90,
                "reasoning": "Sovereignty concerns"
            },
            "economist": {
                "rating": "ACCEPT",
                "confidence": 85,
                "reasoning": "Cost effective"
            }
        }
        
        assert len(state["agent_responses"]) == 2
        assert state["agent_responses"]["sovereign"]["rating"] == "BLOCK"
        assert state["agent_responses"]["economist"]["rating"] == "ACCEPT"
    
    def test_state_active_tensions_structure(self):
        """Test active tensions can be added to state"""
        state = create_initial_state("Test query", {})
        
        # Simulate adding tensions
        state["active_tensions"] = [
            {
                "protocol_id": "sovereign_economist",
                "agents_involved": ["sovereign", "economist"],
                "status": "active",
                "priority": 2
            }
        ]
        
        assert len(state["active_tensions"]) == 1
        assert state["active_tensions"][0]["protocol_id"] == "sovereign_economist"
    
    def test_state_convergence_status_structure(self):
        """Test convergence status can be set"""
        state = create_initial_state("Test query", {})
        
        state["convergence_status"] = {
            "converged": True,
            "criteria_met": {
                "no_blocks": True,
                "max_warns": True,
                "min_confidence": True,
                "min_agreement": True
            }
        }
        
        assert state["convergence_status"]["converged"] is True
        assert len(state["convergence_status"]["criteria_met"]) == 4
    
    def test_state_final_recommendation_structure(self):
        """Test final recommendation can be set"""
        state = create_initial_state("Test query", {})
        
        state["final_recommendation"] = {
            "recommendation": "Use AWS with sovereignty controls",
            "confidence": 85,
            "supporting_arguments": ["Cost effective", "EU regions available"],
            "action_items": ["Deploy in eu-central-1", "Enable encryption"]
        }
        
        assert state["final_recommendation"]["recommendation"]
        assert state["final_recommendation"]["confidence"] == 85
        assert len(state["final_recommendation"]["action_items"]) == 2
    
    def test_state_iteration_count(self):
        """Test iteration count can be incremented"""
        state = create_initial_state("Test query", {})
        
        assert state["iteration_count"] == 0
        
        state["iteration_count"] = 1
        assert state["iteration_count"] == 1
        
        state["iteration_count"] += 1
        assert state["iteration_count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
