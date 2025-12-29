"""Tension detector node - identifies tensions between agent responses."""

import logging
from typing import Dict, Any

from ..state import ConsortiumState
from ..tensions.orchestrator import TensionOrchestrator

logger = logging.getLogger(__name__)


def tension_detector_node(state: ConsortiumState) -> Dict[str, Any]:
    """Detect tensions between agent responses.
    
    LANGGRAPH PATTERN: Return partial state update containing only
    the fields that changed (active_tensions).
    
    Args:
        state: Current consortium state
        
    Returns:
        Partial state update with detected tensions
    """
    agent_responses = state.get("agent_responses", {})
    
    if not agent_responses:
        logger.warning("No agent responses to analyze for tensions")
        return {"active_tensions": []}
    
    logger.info(f"Detecting tensions among {len(agent_responses)} agents")
    
    try:
        # Initialize tension orchestrator
        orchestrator = TensionOrchestrator()
        
        # Detect tensions using orchestrator
        tensions = orchestrator.detect_tensions(state)
        
        logger.info(f"Detected {len(tensions)} active tensions")
        
        # LANGGRAPH PATTERN: Return only the updated fields
        return {"active_tensions": tensions}
        
    except Exception as e:
        logger.error(f"Tension detection failed: {e}", exc_info=True)
        # Return empty tensions on error - don't fail the graph
        return {"active_tensions": []}
