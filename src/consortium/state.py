"""Consortium state management."""

from typing import TypedDict, List, Dict, Any, Optional, Annotated, Literal
import operator


class MechanismPatch(TypedDict, total=False):
    """The specific mechanism to inject into a proposal."""
    trigger: str        # e.g., "Utilization drops below 60% for 2 quarters"
    action: str         # e.g., "Subsidy converts to voucher system automatically"
    authority: str      # e.g., "Exogenous / Automatic"


class CLAReview(TypedDict, total=False):
    """Conditionality & Leverage Agent review output."""
    verdict: Literal["STRUCTURALLY_CREDIBLE", "FRAGILE_CONSENSUS", "ZOMBIE_RISK"]
    failed_tests: List[str]  # ["Commitment", "Trigger", "Cost", "Leverage"]
    critique: str
    mechanism_patch: Optional[MechanismPatch]
    reasoning: str
    rating: str
    confidence: float


class ConsortiumState(TypedDict, total=False):
    """State for the consortium graph.

    Attributes:
        query: The user's query
        context: Additional context for the query
        triggered_agents: List of agent IDs to execute
        agent_responses: Responses from executed agents
        active_tensions: List of detected tensions (append-only with reducer)
        convergence_status: Convergence check results
        final_recommendation: Final synthesized recommendation
        iteration_count: Number of iterations performed
        cla_review: CLA temporal robustness review
        cla_gate_status: Status of CLA gate (OPEN/CLOSED/PENDING)
        memory_retrievals: Similar historical cases retrieved before agent execution
        case_id: ID of stored case (for feedback/outcome updates)
        retrieval_metadata: Metadata about memory retrieval (quality, cold-start status)
    """
    query: str
    context: Dict[str, Any]
    triggered_agents: List[str]
    agent_responses: Dict[str, Dict[str, Any]]
    # Use operator.add reducer for safe concurrent updates
    active_tensions: Annotated[List[Dict[str, Any]], operator.add]
    convergence_status: Dict[str, Any]
    final_recommendation: Dict[str, Any]
    iteration_count: int
    # CLA fields
    cla_review: Optional[CLAReview]
    cla_gate_status: Literal["OPEN", "CLOSED", "PENDING"]
    # Memory fields
    memory_retrievals: List[Dict[str, Any]]  # Similar historical cases
    case_id: Optional[str]  # ID of stored case for feedback
    retrieval_metadata: Optional[Dict[str, Any]]  # Retrieval quality info


def create_initial_state(
    query: str,
    context: Optional[Dict[str, Any]] = None
) -> ConsortiumState:
    """Create initial state for consortium graph.

    Args:
        query: User's query
        context: Optional additional context

    Returns:
        Initial consortium state
    """
    return ConsortiumState(
        query=query,
        context=context or {},
        triggered_agents=[],
        agent_responses={},
        active_tensions=[],
        convergence_status={},
        final_recommendation={},
        iteration_count=0,
        cla_review=None,
        cla_gate_status="PENDING",
        memory_retrievals=[],
        case_id=None,
        retrieval_metadata=None
    )
