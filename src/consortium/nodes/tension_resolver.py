"""Tension resolver node - resolves detected tensions."""

import logging
from typing import Dict, Any

from ..state import ConsortiumState
from ..tensions.orchestrator import TensionOrchestrator

logger = logging.getLogger(__name__)


def tension_resolver_node(state: ConsortiumState) -> Dict[str, Any]:
    """Resolve the next active tension.
    
    LANGGRAPH PATTERN: Return partial state update containing only
    the fields that changed (active_tensions, current_proposal).
    
    Args:
        state: Current consortium state
        
    Returns:
        Partial state update with resolved tension
    """
    active_tensions = state.get("active_tensions", [])
    
    if not active_tensions:
        logger.info("No active tensions to resolve")
        return {"active_tensions": []}
    
    logger.info(f"Resolving tensions: {len(active_tensions)} active")
    
    try:
        # Initialize tension orchestrator
        orchestrator = TensionOrchestrator()
        
        # Resolve next tension using orchestrator
        result = orchestrator.resolve_next_tension(state)
        
        if result:
            logger.info(
                f"Tension resolved. Remaining: {len(result['tensions'])}"
            )
            # Return updated tensions and potentially updated proposal
            return {
                "active_tensions": result["tensions"],
                "current_proposal": result.get(
                    "proposal", state.get("current_proposal")
                )
            }
        else:
            logger.warning("Tension resolution returned no result")
            return {"active_tensions": []}
        
    except Exception as e:
        logger.error(f"Tension resolution failed: {e}", exc_info=True)
        # Clear tensions on error - don't block the graph
        return {"active_tensions": []}
