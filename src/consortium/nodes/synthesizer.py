"""Synthesizer node - creates final recommendation.

Implements Pyramid Principle format:
- Level 1: Executive recommendation
- Level 2: Supporting arguments by agent
- Level 3: Action items
- Level 4: Decision provenance

Also handles post-convergence storage in memory for future retrieval.

COST OPTIMIZATION: Currently uses no LLM (ZERO-LLM = FREE) - rule-based synthesis
If LLM-based synthesis added: Use STANDARD tier (Gemini Flash - cheapest)
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List

from ..state import ConsortiumState

logger = logging.getLogger(__name__)


def synthesizer_node(state: ConsortiumState) -> Dict[str, Any]:
    """Synthesize final recommendation in Pyramid Principle format.
    
    LANGGRAPH PATTERN: Return partial state update with
    final_recommendation.
    
    Args:
        state: Current consortium state
        
    Returns:
        Partial state update with final_recommendation
    """
    logger.info("Synthesizing final recommendation")
    
    # Generate executive recommendation
    recommendation = _generate_recommendation(state)
    
    # Collect supporting arguments
    supporting_arguments = {}
    for agent_id, response in state.get("agent_responses", {}).items():
        supporting_arguments[agent_id] = {
            "rating": response.get("rating"),
            "confidence": response.get("confidence"),
            "reasoning": response.get("reasoning")
        }
    
    # Extract action items
    action_items = _extract_action_items(state)
    
    # Build decision provenance
    provenance = {
        "query": state.get("query"),
        "agents_engaged": state.get("triggered_agents", []),
        "tensions_detected": len(state.get("active_tensions", [])),
        "convergence_status": state.get("convergence_status"),
        "iteration_count": state.get("iteration_count", 0)
    }
    
    # Assemble final report
    report = {
        "recommendation": recommendation,
        "supporting_arguments": supporting_arguments,
        "action_items": action_items,
        "decision_provenance": provenance
    }

    logger.info("✓ Final recommendation synthesized")

    # =========================================================================
    # POST-STORAGE: Store case in memory for future retrieval
    # =========================================================================

    case_id = None

    # Only store if OpenAI API key is available (required for embeddings)
    if os.getenv("OPENAI_API_KEY"):
        try:
            from ..memory import get_memory_manager

            # Generate unique case ID
            case_id = str(uuid.uuid4())

            # Create case dict for storage
            case = {
                "id": case_id,
                "query": state.get("query", ""),
                "context": state.get("context", {}),
                "agents_engaged": state.get("triggered_agents", []),
                "agent_responses": state.get("agent_responses", {}),
                "tensions": state.get("active_tensions", []),
                "convergence_status": state.get("convergence_status", {}),
                "final_recommendation": report,
                "timestamp": datetime.now(),
                # user_feedback and outcome are initially None
                # They will be updated later via update_feedback() and update_outcome()
                "user_feedback": None,
                "outcome": None
            }

            # Store in memory
            memory_manager = get_memory_manager()
            stored_id = memory_manager.store_case(case)

            logger.info(f"✓ Case stored in memory: {stored_id[:12]}... (for future retrieval and feedback)")

        except Exception as e:
            logger.warning(f"Failed to store case in memory (proceeding anyway): {e}")
            # Graceful degradation: case_id remains None if storage fails
            case_id = None
    else:
        logger.info("Case storage skipped (OPENAI_API_KEY not set for embeddings)")

    # Return final recommendation and case_id (for feedback collection)
    return {
        "final_recommendation": report,
        "case_id": case_id
    }


def _generate_recommendation(state: ConsortiumState) -> str:
    """Generate executive-level recommendation."""
    
    responses = state.get("agent_responses", {})
    convergence = state.get("convergence_status", {})
    
    if not responses:
        return "Insufficient agent input to generate recommendation."
    
    # Count ratings
    blocks = sum(
        1 for r in responses.values()
        if r.get("rating") == "BLOCK"
    )
    warns = sum(
        1 for r in responses.values()
        if r.get("rating") == "WARN"
    )
    accepts = sum(
        1 for r in responses.values()
        if r.get("rating") == "ACCEPT"
    )
    endorses = sum(
        1 for r in responses.values()
        if r.get("rating") == "ENDORSE"
    )
    
    # Generate recommendation based on consensus
    if convergence.get("converged"):
        if endorses >= 2:
            strength = "STRONGLY RECOMMENDED"
        elif accepts >= 2:
            strength = "RECOMMENDED WITH CONDITIONS"
        else:
            strength = "PROCEED WITH CAUTION"
    else:
        if blocks > 0:
            strength = "NOT RECOMMENDED"
        else:
            strength = "REQUIRES FURTHER ANALYSIS"
    
    avg_conf = convergence.get("avg_confidence", 0)
    
    recommendation = f"""{strength} (Confidence: {avg_conf:.0f}%)

Based on analysis by {len(responses)} expert agents, the consortium's \
assessment is:
{_summarize_consensus(responses)}

Key considerations from the expert panel are detailed in the supporting \
arguments below."""
    
    return recommendation


def _summarize_consensus(responses: Dict[str, Any]) -> str:
    """Summarize consensus from agent responses."""
    
    ratings = [r.get("rating") for r in responses.values()]
    
    if all(r in ["ACCEPT", "ENDORSE"] for r in ratings):
        return "All agents agree this approach is viable."
    elif any(r == "BLOCK" for r in ratings):
        blockers = [
            aid for aid, r in responses.items()
            if r.get("rating") == "BLOCK"
        ]
        return f"Critical concerns raised by: {', '.join(blockers)}."
    else:
        return "Mixed assessment with conditions noted."


def _extract_action_items(state: ConsortiumState) -> List[Dict[str, Any]]:
    """Extract action items from agent responses."""
    
    items = []
    
    for agent_id, response in state.get("agent_responses", {}).items():
        rating = response.get("rating")
        reasoning = response.get("reasoning", "")
        
        if rating == "WARN":
            mitigation = response.get("mitigation_plan", "")
            items.append({
                "action": f"Address {agent_id} concerns",
                "owner": "Strategy Team",
                "priority": "High",
                "details": (
                    mitigation[:100] + "..."
                    if len(mitigation) > 100
                    else mitigation or reasoning[:100] + "..."
                )
            })
        elif rating == "BLOCK":
            items.append({
                "action": f"CRITICAL: Resolve {agent_id} blocking issue",
                "owner": "Executive Team",
                "priority": "Critical",
                "details": reasoning[:100] + "..."
            })
    
    return items
