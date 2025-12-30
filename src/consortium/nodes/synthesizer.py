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
    
    # Extract action items with board-grade voice (Feature 4)
    action_items = _extract_action_items(state)
    
    # Build decision provenance
    provenance = {
        "query": state.get("query"),
        "agents_engaged": state.get("triggered_agents", []),
        "tensions_detected": len(state.get("active_tensions", [])),
        "convergence_status": state.get("convergence_status"),
        "iteration_count": state.get("iteration_count", 0)
    }

    # Extract convergence gate information (Feature 2: Convergence Gates)
    convergence_status = state.get("convergence_status", {})
    gate_status = convergence_status.get("gate_status")

    waivers_applied = []
    values_escalation_report = None

    if gate_status:
        # Extract waivers that were applied
        waivers_applied = gate_status.get("waivers_applied", [])

        # Check if Philosopher BLOCKs require Values Escalation Report
        philosopher_blocks = gate_status.get("philosopher_blocks", [])
        if philosopher_blocks:
            values_escalation_report = _generate_values_escalation_report(
                state, philosopher_blocks
            )

    # Assemble final report
    report = {
        "recommendation": recommendation,
        "supporting_arguments": supporting_arguments,
        "action_items": action_items,
        "decision_provenance": provenance
    }

    # Add waivers section if any were applied (Feature 2)
    if waivers_applied:
        report["waivers_applied"] = waivers_applied

    # Add Values Escalation Report if Philosopher BLOCKs occurred (Feature 2)
    if values_escalation_report:
        report["values_escalation_report"] = values_escalation_report

    # Add Evidence Report if Evidence Referee is active (Feature 3)
    evidence_report = _generate_evidence_report_section(state)
    if evidence_report:
        report["evidence_report"] = evidence_report

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
    """Generate executive-level recommendation with board-grade voice.

    Feature 4: Final Recommendation Voice (board-grade)
    """

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

    # Generate summary with board-grade voice
    summary = _summarize_consensus(responses)

    # Apply voice rules (Feature 4)
    try:
        from ..tools.voice_rules import format_executive_recommendation

        recommendation = format_executive_recommendation({
            "strength": strength,
            "avg_confidence": avg_conf,
            "summary": summary
        })

    except Exception as e:
        logger.warning(f"Failed to apply voice rules (using fallback): {e}")
        # Fallback to basic formatting
        recommendation = f"""{strength} (Confidence: {avg_conf:.0f}%)

Based on analysis by {len(responses)} expert agents, the consortium's assessment is:
{summary}

Key considerations from the expert panel are detailed in the supporting arguments below."""

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
    """Extract action items from agent responses with board-grade voice.

    Feature 4: Final Recommendation Voice (board-grade)
    """

    items = []

    for agent_id, response in state.get("agent_responses", {}).items():
        rating = response.get("rating")
        reasoning = response.get("reasoning", "")

        if rating == "WARN":
            mitigation = response.get("mitigation_plan", "")
            items.append({
                "action": f"Resolve {agent_id} concerns",
                "owner": "Strategy Team",
                "priority": "HIGH",
                "details": (
                    mitigation[:100] + "..."
                    if len(mitigation) > 100
                    else mitigation or reasoning[:100] + "..."
                )
            })
        elif rating == "BLOCK":
            items.append({
                "action": f"CRITICAL: Resolve {agent_id} blocking constraints",
                "owner": "Executive Team",
                "priority": "CRITICAL",
                "details": reasoning[:100] + "..."
            })

    # Apply voice rules to action items (Feature 4)
    try:
        from ..tools.voice_rules import format_action_items_board_grade
        items = format_action_items_board_grade(items)
    except Exception as e:
        logger.warning(f"Failed to apply voice rules to action items: {e}")

    return items


def _generate_values_escalation_report(
    state: ConsortiumState,
    philosopher_blocks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate Values Escalation Report for Philosopher BLOCKs.

    When the Philosopher agent BLOCKs, this generates a board-grade report
    documenting the values violation and requiring explicit waiver to proceed.

    Feature 2: Convergence Gates + Waiver Register

    Args:
        state: Current consortium state
        philosopher_blocks: List of Philosopher BLOCK incidents

    Returns:
        Values Escalation Report dict
    """
    agent_responses = state.get("agent_responses", {})
    philosopher_response = agent_responses.get("philosopher", {})

    # Extract red line violations from Philosopher response
    red_lines_violated = []
    for block in philosopher_blocks:
        red_lines_violated.extend(block.get("red_lines", []))

    report = {
        "escalation_trigger": "Philosopher BLOCK - Values Violation Detected",
        "severity": "CRITICAL - Requires Board-Level Review",
        "values_analysis": philosopher_response.get("reasoning", ""),
        "red_lines_violated": list(set(red_lines_violated)),  # Deduplicate
        "philosopher_confidence": philosopher_response.get("confidence", 0),
        "strategic_implications": _extract_strategic_implications(philosopher_response),
        "recommendation": (
            "This strategy proposal conflicts with fundamental organizational values. "
            "Proceeding requires:\n"
            "1. Explicit waiver granted by authorized decision-maker\n"
            "2. Documented mitigation plan\n"
            "3. Time-bounded review process\n"
            "4. Clear scope restrictions\n\n"
            "Without waiver, this proposal MUST NOT proceed."
        ),
        "next_steps": [
            "Escalate to Board or Ethics Committee",
            "Document business justification for waiver request",
            "Design mitigation plan addressing values concerns",
            "Define waiver scope, time bounds, and review schedule"
        ]
    }

    return report


def _extract_strategic_implications(philosopher_response: Dict[str, Any]) -> str:
    """Extract strategic implications from Philosopher reasoning.

    Args:
        philosopher_response: Philosopher agent's response

    Returns:
        Strategic implications summary
    """
    reasoning = philosopher_response.get("reasoning", "")

    # Simple extraction: look for key phrases
    implications = []

    if "reputation" in reasoning.lower():
        implications.append("Potential reputational risk")
    if "trust" in reasoning.lower():
        implications.append("Erosion of stakeholder trust")
    if "principle" in reasoning.lower() or "value" in reasoning.lower():
        implications.append("Violation of core organizational principles")
    if "precedent" in reasoning.lower():
        implications.append("Sets dangerous precedent for future decisions")

    if implications:
        return "; ".join(implications)
    else:
        return "Fundamental misalignment with organizational values and ethics"


def _generate_evidence_report_section(state: ConsortiumState) -> Optional[Dict[str, Any]]:
    """Generate Evidence Report section for final synthesis.

    Feature 3: Evidence Referee (deterministic)

    Args:
        state: Current consortium state

    Returns:
        Evidence report dict if Evidence Referee is active, None otherwise
    """
    try:
        # Check if Evidence Referee is available in the state
        # The Evidence Referee is typically attached to Scout agent
        # We need to access it through a global instance or config

        # For now, check if we have evidence data in state
        # (Future: could store evidence report in state during Scout phase)

        # Try to get Evidence Referee instance
        from ..tools.evidence_referee import EvidenceReferee

        # Check config for evidence referee path
        import yaml
        from pathlib import Path

        config_path = Path("config/evidence_referee.yaml")
        if not config_path.exists():
            return None

        with open(config_path) as f:
            config = yaml.safe_load(f)

        evidence_config = config.get("evidence_referee", {})
        persist_path = evidence_config.get("persist_path", ".consortium/evidence_referee.db")

        # Check if database exists (if not, Evidence Referee hasn't been used)
        db_path = Path(persist_path)
        if not db_path.exists():
            return None

        # Initialize Evidence Referee to get report
        evidence_referee = EvidenceReferee(persist_path=persist_path)

        # Generate evidence report
        report = evidence_referee.generate_evidence_report()

        # Close connection
        evidence_referee.close()

        # Only include report if there are claims
        if report["total_claims"] == 0:
            return None

        # Format for synthesis
        formatted_report = {
            "summary": (
                f"Evidence analysis of {report['total_claims']} claims from research. "
                f"{report['conflicts_detected']['total']} conflicts detected."
            ),
            "evidence_quality": report["evidence_quality"],
            "conflicts": report["conflicts_detected"],
            "conflicting_claims": report["conflicting_claims"]
        }

        return formatted_report

    except Exception as e:
        logger.warning(f"Failed to generate evidence report: {e}")
        return None
