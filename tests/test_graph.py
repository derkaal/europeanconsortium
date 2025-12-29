"""Tests for consortium graph."""

from src.consortium.graph import create_consortium_graph
from src.consortium.state import create_initial_state


def test_graph_compiles():
    """Test that the graph compiles without errors."""
    graph = create_consortium_graph()
    assert graph is not None


def test_simple_flow():
    """Test that a simple flow through the graph works."""
    graph = create_consortium_graph()
    initial_state = create_initial_state(
        query="Should we invest in renewable energy?",
        context={"budget": 1000000}
    )
    
    result = graph.invoke(initial_state)
    
    # Verify the graph completed
    assert result is not None
    
    # Verify key state fields were populated
    assert "triggered_agents" in result
    assert "agent_responses" in result
    assert "convergence_status" in result
    assert "final_recommendation" in result
    
    # Verify final recommendation exists
    assert result["final_recommendation"] is not None
    assert "recommendation" in result["final_recommendation"]


def test_router_triggers_agents():
    """Test that router node triggers agents."""
    graph = create_consortium_graph()
    initial_state = create_initial_state(query="test query")
    
    result = graph.invoke(initial_state)
    
    # Verify agents were triggered
    assert len(result["triggered_agents"]) > 0
    assert "economist" in result["triggered_agents"]


def test_agent_executor_produces_responses():
    """Test that agent executor produces responses."""
    graph = create_consortium_graph()
    initial_state = create_initial_state(query="test query")
    
    result = graph.invoke(initial_state)
    
    # Verify agent responses were generated
    assert len(result["agent_responses"]) > 0
    
    # Verify response structure
    for agent_id, response in result["agent_responses"].items():
        assert "rating" in response
        assert "confidence" in response
        assert "reasoning" in response


def test_convergence_reached():
    """Test that convergence is reached."""
    graph = create_consortium_graph()
    initial_state = create_initial_state(query="test query")
    
    result = graph.invoke(initial_state)
    
    # Verify convergence status
    assert "convergence_status" in result
    assert result["convergence_status"].get("converged") is True


def test_final_recommendation_generated():
    """Test that final recommendation is generated."""
    graph = create_consortium_graph()
    initial_state = create_initial_state(query="test query")
    
    result = graph.invoke(initial_state)
    
    # Verify final recommendation
    assert "final_recommendation" in result
    assert result["final_recommendation"] is not None
    assert "recommendation" in result["final_recommendation"]
