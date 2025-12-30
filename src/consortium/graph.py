"""Main consortium graph implementation with CLA gate and Scout."""

from typing import Literal, Optional
from langgraph.graph import StateGraph, END

from .state import ConsortiumState
from .nodes import (
    router_node,
    agent_executor_node,
    tension_detector_node,
    tension_resolver_node,
    convergence_test_node,
    synthesizer_node,
    cla_gate_node,
    route_after_cla_gate,
    architect_revision_node,
    create_scout_node,
    advantage_analysis_node,
)


def create_consortium_graph(search_tool=None, enable_scout: bool = False):
    """Create the main consortium graph with optional Scout and CLA gate.

    The Scout runs BEFORE routing to gather current intelligence for agents.
    The CLA (Conditionality & Leverage Agent) gate runs after convergence
    but before final synthesis, ensuring temporal robustness.

    Args:
        search_tool: Optional web search tool for Scout (Tavily, Brave, etc.)
        enable_scout: Whether to enable Scout upstream research (default: False)
                     Note: Scout requires search_tool parameter to function

    Returns:
        Compiled LangGraph instance
    """
    graph = StateGraph(ConsortiumState)

    # Add all nodes
    if enable_scout:
        scout_node = create_scout_node(search_tool)
        graph.add_node("scout", scout_node)

    graph.add_node("router", router_node)
    graph.add_node("agent_executor", agent_executor_node)
    graph.add_node("tension_detector", tension_detector_node)
    graph.add_node("tension_resolver", tension_resolver_node)
    graph.add_node("convergence_test", convergence_test_node)
    graph.add_node("cla_gate", cla_gate_node)
    graph.add_node("architect_revision", architect_revision_node)
    graph.add_node("advantage_analysis", advantage_analysis_node)
    graph.add_node("synthesizer", synthesizer_node)

    # Entry point - Scout if enabled, otherwise router
    if enable_scout:
        graph.set_entry_point("scout")
        # Scout -> Router (always)
        graph.add_edge("scout", "router")
    else:
        graph.set_entry_point("router")
    
    # Linear edges
    graph.add_edge("router", "agent_executor")
    graph.add_edge("agent_executor", "tension_detector")
    
    # Conditional edges with Literal type hints
    def route_after_tension_detection(
        state: ConsortiumState
    ) -> Literal["tension_resolver", "convergence_test"]:
        """Route based on whether tensions were detected."""
        return (
            "tension_resolver"
            if state.get("active_tensions")
            else "convergence_test"
        )
    
    def route_after_tension_resolution(
        state: ConsortiumState
    ) -> Literal["agent_executor", "convergence_test"]:
        """Route based on whether tensions remain after resolution."""
        return (
            "agent_executor"
            if state.get("active_tensions")
            else "convergence_test"
        )
    
    def route_after_convergence_test(
        state: ConsortiumState
    ) -> Literal["cla_gate", "agent_executor"]:
        """Route to CLA gate if converged, else back to agents."""
        converged = state.get("convergence_status", {}).get("converged")
        return "cla_gate" if converged else "agent_executor"
    
    graph.add_conditional_edges(
        "tension_detector",
        route_after_tension_detection
    )
    
    graph.add_conditional_edges(
        "tension_resolver",
        route_after_tension_resolution
    )
    
    graph.add_conditional_edges(
        "convergence_test",
        route_after_convergence_test
    )
    
    # CLA gate routing (uses imported function)
    graph.add_conditional_edges(
        "cla_gate",
        route_after_cla_gate
    )
    
    # After architect revision, run advantage analysis (Feature 6)
    graph.add_edge("architect_revision", "advantage_analysis")

    # After advantage analysis, go to synthesis
    graph.add_edge("advantage_analysis", "synthesizer")

    graph.add_edge("synthesizer", END)
    
    return graph.compile()
