"""Main consortium graph implementation with CLA gate and Scout.

Contains two graph topologies:
1. Parallel Mode (original): All agents critique user query in parallel
2. Cascade Mode (NEW): Proposal → Critique → Transformation cascade
"""

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
    # Cascade nodes
    founder_provocation_node,
    breaker_critique_node,
    alchemist_transformation_node,
)


def create_consortium_graph(search_tool=None, enable_scout: bool = True, mode: str = "cascade"):
    """Create the main consortium graph with optional Scout and CLA gate.

    Args:
        search_tool: Optional web search tool for Scout (Tavily, Brave, etc.)
        enable_scout: Whether to enable Scout upstream research (default: True)
                     Note: Scout will auto-configure Brave/Tavily from env
        mode: Graph topology mode - "cascade" (default) or "parallel"
              - cascade: Founder → Breakers → Alchemist (strategy engine)
              - parallel: All agents critique user query in parallel (original)

    Returns:
        Compiled LangGraph instance
    """
    if mode == "cascade":
        return create_consortium_graph_cascade(search_tool, enable_scout)
    elif mode == "parallel":
        return create_consortium_graph_parallel(search_tool, enable_scout)
    else:
        raise ValueError(f"Unknown graph mode: {mode}. Use 'cascade' or 'parallel'")


def create_consortium_graph_parallel(search_tool=None, enable_scout: bool = True):
    """Create the PARALLEL consortium graph (original topology).

    All agents critique the user query in parallel.
    This is the original "compliance auditor" mode.

    The Scout runs BEFORE routing to gather current intelligence for agents.
    The CLA (Conditionality & Leverage Agent) gate runs after convergence
    but before final synthesis, ensuring temporal robustness.

    Args:
        search_tool: Optional web search tool for Scout (Tavily, Brave, etc.)
        enable_scout: Whether to enable Scout upstream research (default: True)
                     Note: Scout will auto-configure Brave/Tavily from env

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


def create_consortium_graph_cascade(search_tool=None, enable_scout: bool = True):
    """Create the CASCADE consortium graph (Proposal-Critique-Transformation).

    NEW ARCHITECTURE: Strategy Engine (not compliance auditor)

    Workflow:
    1. Scout (optional): Gather current intelligence
    2. Founder Provocation: Generate aggressive "Max Upside" proposal
    3. Breaker Critique: All constraint agents attack Founder's proposal in parallel
    4. Alchemist Transformation: Convert constraints into competitive advantages
    5. Tension Detection/Resolution: (unchanged)
    6. Convergence Test: (unchanged)
    7. CLA Gate: (unchanged)
    8. Architect Revision: (unchanged)
    9. Advantage Analysis: (unchanged)
    10. Synthesizer with Yes-If Protocol: Force "Yes, If..." resolution (no deadlocks)

    This cascade forces:
    - Ambition (Founder leads, constraints follow)
    - Conflict (Breakers critique the proposal)
    - Alchemy (Alchemist transmutes constraints)
    - Resolution (Synthesizer applies "Yes, If..." protocol)

    Args:
        search_tool: Optional web search tool for Scout (Tavily, Brave, etc.)
        enable_scout: Whether to enable Scout upstream research (default: True)

    Returns:
        Compiled LangGraph instance
    """
    graph = StateGraph(ConsortiumState)

    # === STEP 0: Scout (optional - unchanged) ===
    if enable_scout:
        scout_node = create_scout_node(search_tool)
        graph.add_node("scout", scout_node)
        graph.set_entry_point("scout")
    else:
        graph.set_entry_point("founder_provocation")

    # === STEP 1: Founder Provocation ===
    graph.add_node("founder_provocation", founder_provocation_node)

    if enable_scout:
        graph.add_edge("scout", "founder_provocation")

    # === STEP 2: Breaker Critique ===
    graph.add_node("breaker_critique", breaker_critique_node)
    graph.add_edge("founder_provocation", "breaker_critique")

    # === STEP 3: Alchemist Transformation ===
    graph.add_node("alchemist_transformation", alchemist_transformation_node)
    graph.add_edge("breaker_critique", "alchemist_transformation")

    # === Tension Detection & Resolution (unchanged) ===
    graph.add_node("tension_detector", tension_detector_node)
    graph.add_edge("alchemist_transformation", "tension_detector")

    graph.add_node("tension_resolver", tension_resolver_node)

    # Conditional edges for tension workflow
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
    ) -> Literal["breaker_critique", "convergence_test"]:
        """Route based on whether tensions remain after resolution.

        NOTE: In cascade mode, we route back to breaker_critique (not agent_executor)
        to re-critique the Founder's proposal with resolved tensions.
        """
        return (
            "breaker_critique"
            if state.get("active_tensions")
            else "convergence_test"
        )

    graph.add_conditional_edges(
        "tension_detector",
        route_after_tension_detection
    )

    graph.add_conditional_edges(
        "tension_resolver",
        route_after_tension_resolution
    )

    # === Convergence Test ===
    graph.add_node("convergence_test", convergence_test_node)

    def route_after_convergence_test(
        state: ConsortiumState
    ) -> Literal["cla_gate", "breaker_critique"]:
        """Route to CLA gate if converged, else back to breaker critique."""
        converged = state.get("convergence_status", {}).get("converged")
        return "cla_gate" if converged else "breaker_critique"

    graph.add_conditional_edges(
        "convergence_test",
        route_after_convergence_test
    )

    # === CLA Gate (unchanged) ===
    graph.add_node("cla_gate", cla_gate_node)

    graph.add_conditional_edges(
        "cla_gate",
        route_after_cla_gate
    )

    # === Architect Revision → Advantage Analysis → Synthesizer ===
    graph.add_node("architect_revision", architect_revision_node)
    graph.add_node("advantage_analysis", advantage_analysis_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.add_edge("architect_revision", "advantage_analysis")
    graph.add_edge("advantage_analysis", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()
