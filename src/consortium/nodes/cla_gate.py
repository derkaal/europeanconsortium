"""CLA Gate node - enforces temporal robustness check.

The CLA gate runs AFTER convergence but BEFORE final synthesis.
It evaluates whether the proposal has structural credibility over time.
"""

from typing import Dict, Any, Literal
import logging
import sys

logger = logging.getLogger(__name__)


def cla_gate_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute CLA review and set gate status.
    
    Runs AFTER convergence but BEFORE final synthesis.
    
    Args:
        state: Current consortium state
        
    Returns:
        Partial state update with cla_review and cla_gate_status
    """
    if '.' not in sys.path:
        sys.path.insert(0, '.')
    
    try:
        from agents.cla import CLAAgent
    except ImportError as e:
        logger.error(f"Failed to import CLA: {e}")
        return {"cla_gate_status": "OPEN", "cla_review": None}
    
    from src.consortium.config import get_config_loader
    
    config_loader = get_config_loader()
    
    try:
        cla_config_model = config_loader.load_agent_config("cla")
        # Convert Pydantic model to dict
        cla_config = cla_config_model.model_dump()
    except Exception as e:
        logger.warning(f"Could not load CLA config: {e}, using defaults")
        cla_config = {
            "agent_id": "cla",
            "name": "Conditionality & Leverage Agent",
            "mandate": "Evaluate temporal robustness",
            "system_prompt": "You are the Conditionality & Leverage Agent (CLA). Evaluate proposals for temporal robustness.",
            "red_lines": [
                "Proposals without explicit reversibility mechanisms",
                "Endogenous review triggers",
                "Unallocated downside risk",
                "Enforcement relying solely on political will"
            ],
            "acceptance_criteria": {
                "BLOCK": "Proposal fails one or more of the 4 tests",
                "ACCEPT": "Proposal passes all 4 tests with explicit mechanisms"
            },
            "knowledge_domains": [
                "Fritz Scharpf Joint-Decision Trap theory",
                "European governance pathologies"
            ]
        }
    
    cla = CLAAgent(cla_config)
    
    logger.info("CLA: Evaluating proposal for temporal robustness...")
    
    try:
        review = cla.invoke(state)
    except Exception as e:
        logger.error(f"CLA invocation failed: {e}", exc_info=True)
        return {"cla_gate_status": "OPEN", "cla_review": None}
    
    verdict = review.get("verdict", "ZOMBIE_RISK")

    if verdict == "STRUCTURALLY_CREDIBLE":
        gate_status = "OPEN"
        logger.info("✓ CLA: Proposal is structurally credible - GATE OPEN")
    else:
        gate_status = "CLOSED"
        logger.warning(f"✗ CLA: {verdict} - GATE CLOSED")
        failed_tests = review.get('failed_tests', [])
        critique = review.get('critique', 'No specific critique provided.')
        logger.warning(f"  Failed tests: {failed_tests}")
        logger.warning(f"  Critique: {critique}")

        # Log mechanism patch status for debugging
        mechanism_patch = review.get('mechanism_patch')
        if mechanism_patch:
            logger.info(f"  CLA provided mechanism patch:")
            logger.info(f"    - Trigger: {mechanism_patch.get('trigger', 'N/A')}")
            logger.info(f"    - Action: {mechanism_patch.get('action', 'N/A')}")
            logger.info(f"    - Authority: {mechanism_patch.get('authority', 'N/A')}")
        else:
            logger.warning(f"  ⚠ CLA did not provide a mechanism patch")

        # Log raw reasoning for debugging (truncated)
        reasoning = review.get('reasoning', '')
        if reasoning:
            reasoning_preview = reasoning[:300] + "..." if len(reasoning) > 300 else reasoning
            logger.debug(f"  CLA reasoning (preview): {reasoning_preview}")
    
    # Add CLA to agent responses
    agent_responses = {**state.get("agent_responses", {}), "cla": review}
    
    return {
        "cla_review": review,
        "cla_gate_status": gate_status,
        "agent_responses": agent_responses
    }


def route_after_cla_gate(
    state: Dict[str, Any]
) -> Literal["synthesizer", "architect_revision"]:
    """Route based on CLA gate status.
    
    Args:
        state: Current consortium state
        
    Returns:
        Next node to execute
    """
    if state.get("cla_gate_status") == "OPEN":
        return "synthesizer"
    return "architect_revision"
