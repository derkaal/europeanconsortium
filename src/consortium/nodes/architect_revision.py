"""Architect revision node - integrates CLA mechanism patches.

When the CLA gate closes, this node forces integration of the CLA's
mechanism patch into the proposal. The Architect cannot argue - it must
integrate the patch to ensure temporal robustness.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def architect_revision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Force integration of CLA's mechanism patch into the proposal.
    
    The Architect cannot argue - it must integrate the patch.
    
    Args:
        state: Current consortium state
        
    Returns:
        Partial state update with patched recommendation and open gate
    """
    cla_review = state.get("cla_review", {})
    mechanism_patch = cla_review.get("mechanism_patch", {})

    if not mechanism_patch:
        verdict = cla_review.get("verdict", "UNKNOWN")
        failed_tests = cla_review.get("failed_tests", [])
        critique = cla_review.get("critique", "No specific critique provided.")

        logger.warning("⚠ No mechanism patch from CLA, opening gate anyway")
        logger.warning(f"  CLA Verdict: {verdict}")
        logger.warning(f"  Failed Tests: {failed_tests}")
        logger.warning(f"  Critique: {critique}")
        logger.warning("  → This may indicate the CLA's response was not properly formatted")
        logger.warning("  → Check that the LLM response includes TRIGGER, ACTION, and AUTHORITY fields")

        return {"cla_gate_status": "OPEN"}
    
    logger.info("Architect: Integrating CLA mechanism patch...")
    logger.info(f"  Trigger: {mechanism_patch.get('trigger')}")
    logger.info(f"  Action: {mechanism_patch.get('action')}")
    logger.info(f"  Authority: {mechanism_patch.get('authority')}")
    
    current_rec = state.get("final_recommendation", {})
    
    # Create patched recommendation with conditionality mechanisms
    patched_recommendation = {
        **current_rec,
        "conditionality_mechanisms": {
            "trigger": mechanism_patch.get("trigger", "Not specified"),
            "action": mechanism_patch.get("action", "Not specified"),
            "authority": mechanism_patch.get("authority", "Requires-Approval"),
            "added_by": "CLA Gate Review",
            "reason": cla_review.get("critique", "Structural robustness")
        }
    }
    
    # Update recommendation text to include mechanisms
    rec_text = current_rec.get("recommendation", "")
    patch_text = "\n\nCONDITIONALITY MECHANISMS (Added by CLA):\n"
    patch_text += f"• Trigger: {mechanism_patch.get('trigger')}\n"
    patch_text += f"• Action: {mechanism_patch.get('action')}\n"
    patch_text += f"• Authority: {mechanism_patch.get('authority')}"
    
    patched_recommendation["recommendation"] = rec_text + patch_text
    
    logger.info("✓ Architect: Mechanism patch integrated successfully")
    
    return {
        "final_recommendation": patched_recommendation,
        "cla_gate_status": "OPEN"  # After patch, open the gate
    }
