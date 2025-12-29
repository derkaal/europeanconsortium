"""Tests for Conditionality & Leverage Agent."""
import pytest
import sys
sys.path.insert(0, '.')


def test_cla_agent_initialization():
    """Test CLA agent can be initialized."""
    from agents.cla import CLAAgent
    
    cla = CLAAgent({
        "agent_id": "cla",
        "name": "CLA",
        "mandate": "Test",
        "red_lines": [],
        "acceptance_criteria": {},
        "knowledge_domains": []
    })
    
    assert cla.agent_id == "cla"
    assert "Constitutional Court" in cla.system_prompt


def test_cla_parse_response():
    """Test CLA response parsing."""
    from agents.cla import CLAAgent
    
    cla = CLAAgent({
        "agent_id": "cla",
        "name": "CLA",
        "mandate": "Test",
        "red_lines": [],
        "acceptance_criteria": {},
        "knowledge_domains": []
    })
    
    # Mock response with failed tests
    response_text = """
VERDICT: ZOMBIE_RISK

FAILED_TESTS: [Commitment, Trigger]

CRITIQUE: Proposal lacks sunset clause and relies on endogenous review.

MECHANISM_PATCH:
TRIGGER: Utilization drops below 60% for 2 consecutive quarters
ACTION: Subsidy automatically converts to voucher system
AUTHORITY: Exogenous/Automatic
"""
    
    result = cla._parse_cla_response(response_text)
    
    assert result["verdict"] == "ZOMBIE_RISK"
    assert "Commitment" in result["failed_tests"]
    assert "Trigger" in result["failed_tests"]
    assert result["rating"] == "BLOCK"
    assert result["mechanism_patch"] is not None
    assert "60%" in result["mechanism_patch"]["trigger"]


def test_cla_gate_node():
    """Test CLA gate node integration."""
    from src.consortium.nodes.cla_gate import cla_gate_node
    
    state = {
        "query": "Test query",
        "context": {},
        "agent_responses": {
            "sovereign": {
                "rating": "ACCEPT",
                "confidence": 80,
                "reasoning": "OK"
            }
        },
        "final_recommendation": {
            "recommendation": "Test recommendation without sunset clause"
        }
    }
    
    result = cla_gate_node(state)
    
    assert "cla_gate_status" in result
    assert "cla_review" in result or result["cla_review"] is None
    assert result["cla_gate_status"] in ["OPEN", "CLOSED"]
    
    print(f"✓ CLA gate status: {result['cla_gate_status']}")


def test_architect_revision_node():
    """Test architect revision node."""
    from src.consortium.nodes.architect_revision import architect_revision_node
    
    state = {
        "cla_review": {
            "verdict": "ZOMBIE_RISK",
            "failed_tests": ["Commitment"],
            "critique": "No sunset clause",
            "mechanism_patch": {
                "trigger": "3 years from implementation",
                "action": "Automatic review and renewal vote required",
                "authority": "Exogenous/Automatic"
            }
        },
        "final_recommendation": {
            "recommendation": "Original recommendation"
        }
    }
    
    result = architect_revision_node(state)
    
    assert result["cla_gate_status"] == "OPEN"
    assert "final_recommendation" in result
    assert "conditionality_mechanisms" in result["final_recommendation"]
    
    mechanisms = result["final_recommendation"]["conditionality_mechanisms"]
    assert "trigger" in mechanisms
    assert "3 years" in mechanisms["trigger"]
    
    print("✓ Architect revision completed successfully")


def test_route_after_cla_gate():
    """Test CLA gate routing logic."""
    from src.consortium.nodes.cla_gate import route_after_cla_gate
    
    # Test OPEN gate
    state_open = {"cla_gate_status": "OPEN"}
    assert route_after_cla_gate(state_open) == "synthesizer"
    
    # Test CLOSED gate
    state_closed = {"cla_gate_status": "CLOSED"}
    assert route_after_cla_gate(state_closed) == "architect_revision"
    
    print("✓ CLA gate routing works correctly")


@pytest.mark.skip(reason="Requires real LLM API calls")
def test_graph_with_cla():
    """Test full graph execution with CLA gate."""
    from src.consortium.graph import create_consortium_graph
    from src.consortium.state import create_initial_state
    
    graph = create_consortium_graph()
    
    state = create_initial_state(
        query="Should we create a permanent AI research fund?",
        context={"governance": "committee", "duration": "permanent"}
    )
    
    result = graph.invoke(state, {"recursion_limit": 25})
    
    # Check CLA was invoked
    assert ("cla" in result.get("agent_responses", {}) or
            result.get("cla_review") is not None)
    
    # Check final recommendation exists
    assert result.get("final_recommendation") is not None
    
    print("✓ Graph with CLA completed successfully")
    if result.get("cla_review"):
        print(f"  CLA verdict: {result['cla_review'].get('verdict')}")
