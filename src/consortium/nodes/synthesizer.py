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
from typing import Dict, Any, List, Optional

from ..state import ConsortiumState

logger = logging.getLogger(__name__)


def synthesizer_node(state: ConsortiumState) -> Dict[str, Any]:
    """Synthesize final recommendation in Pyramid Principle format.

    CASCADE MODE ENHANCEMENT:
    - Applies "Yes, If..." protocol (no deadlocks unless illegal)
    - Pyramid structure starts with Strategic Bet (Founder + Alchemist vision)
    - Constraints become "Governance Shield" not "Blockers"

    LANGGRAPH PATTERN: Return partial state update with
    final_recommendation.

    Args:
        state: Current consortium state

    Returns:
        Partial state update with final_recommendation
    """
    logger.info("Synthesizing final recommendation")

    # Detect if we're in cascade mode (has draft_strategy)
    is_cascade_mode = bool(state.get("draft_strategy"))

    if is_cascade_mode:
        logger.info("CASCADE MODE: Applying Yes-If protocol and Strategic Bet structure")
        report = _synthesize_cascade_mode(state)
    else:
        logger.info("PARALLEL MODE: Using traditional synthesis")
        report = _synthesize_parallel_mode(state)

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


def _synthesize_cascade_mode(state: ConsortiumState) -> Dict[str, Any]:
    """Synthesize final recommendation in CASCADE mode with Yes-If protocol.

    Pyramid Principle Structure (Cascade):
    1. The Strategic Bet (Founder vision + Alchemist opportunities)
    2. The Governance Shield (Constraints as protective moats)
    3. The Execution Path (Roadmap with conditional approvals)
    4. The Kill Switch (CLA exit criteria)

    Args:
        state: Current consortium state

    Returns:
        Final report dict
    """
    # Get cascade-specific data
    draft_strategy = state.get("draft_strategy", "")
    breaker_constraints = state.get("breaker_constraints", [])
    reframed_opportunities = state.get("reframed_opportunities", [])
    agent_responses = state.get("agent_responses", {})

    # Apply YES, IF... protocol
    illegal_blocks = _identify_illegal_blocks(breaker_constraints)

    if illegal_blocks:
        # Only hard stop if proposal is illegal
        recommendation_text = "CANNOT PROCEED - Proposal involves illegal activities"
        conditional_approvals = []
    else:
        # Generate "Yes, If..." conditional approvals
        conditional_approvals = _generate_conditional_approvals(breaker_constraints)

        # Build recommendation with "Yes-If" protocol
        if conditional_approvals:
            recommendation_text = f"PROCEED WITH CONDITIONS - {len(conditional_approvals)} mitigations required"
        else:
            recommendation_text = "PROCEED - No blocking constraints identified"

    # Build Pyramid Principle sections
    sections = {
        "1_strategic_bet": {
            "title": "The Strategic Bet: Why We Should Do This",
            "founder_vision": draft_strategy,
            "reframed_opportunities": reframed_opportunities,
            "content": _format_strategic_bet(draft_strategy, reframed_opportunities)
        },
        "2_governance_shield": {
            "title": "The Governance Shield: How We Protect the Bet",
            "conditional_approvals": conditional_approvals,
            "constraints_count": len(breaker_constraints),
            "content": _format_governance_shield(conditional_approvals, breaker_constraints)
        },
        "3_execution_path": {
            "title": "The Execution Path: How We Execute",
            "roadmap": _extract_roadmap(state),
            "action_items": _extract_action_items(state),
            "content": _format_execution_path(state)
        },
        "4_kill_switch": {
            "title": "The Kill Switch: How We Exit if Needed",
            "cla_criteria": _extract_cla_exit_criteria(state),
            "content": _format_kill_switch(state)
        }
    }

    # Collect supporting arguments
    supporting_arguments = {}
    for agent_id, response in agent_responses.items():
        supporting_arguments[agent_id] = {
            "rating": response.get("rating"),
            "confidence": response.get("confidence"),
            "reasoning": response.get("reasoning")
        }

    # Build decision provenance
    provenance = {
        "query": state.get("query"),
        "mode": "CASCADE",
        "workflow": "Founder → Breakers → Alchemist → Yes-If Resolution",
        "agents_engaged": list(agent_responses.keys()),
        "tensions_detected": len(state.get("active_tensions", [])),
        "convergence_status": state.get("convergence_status"),
        "iteration_count": state.get("iteration_count", 0)
    }

    # Assemble final report
    report = {
        "recommendation": recommendation_text,
        "structure": "Pyramid Principle (Cascade Mode)",
        "sections": sections,
        "supporting_arguments": supporting_arguments,
        "decision_provenance": provenance,
        "yes_if_protocol_applied": True,
        "conditional_approvals_count": len(conditional_approvals)
    }

    # Add standard features
    _add_standard_features(report, state)

    return report


def _synthesize_parallel_mode(state: ConsortiumState) -> Dict[str, Any]:
    """Synthesize final recommendation in PARALLEL mode (original).

    Traditional structure:
    - Recommendation
    - Supporting arguments
    - Action items
    - Decision provenance

    Args:
        state: Current consortium state

    Returns:
        Final report dict
    """
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
        "mode": "PARALLEL",
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

    # Add standard features
    _add_standard_features(report, state)

    return report


def _add_standard_features(report: Dict[str, Any], state: ConsortiumState) -> None:
    """Add standard features to report (both cascade and parallel modes).

    Modifies report dict in place.

    Args:
        report: Report dict to modify
        state: Current consortium state
    """
    # Add Evidence Report if Evidence Referee is active (Feature 3)
    evidence_report = _generate_evidence_report_section(state)
    if evidence_report:
        report["evidence_report"] = evidence_report

    # Add Competitive Advantage Analysis if available (Feature 6)
    advantage_analysis = state.get("advantage_analysis")
    if advantage_analysis and advantage_analysis.get("enabled"):
        report["competitive_advantages"] = {
            "advantages": advantage_analysis.get("advantages", []),
            "opportunities": advantage_analysis.get("opportunities", []),
            "recommendations": advantage_analysis.get("recommendations", []),
            "pattern_matches": advantage_analysis.get("pattern_matches", 0)
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
        reasoning = response.get("reasoning") or ""

        if rating == "WARN":
            mitigation = response.get("mitigation_plan") or ""
            items.append({
                "action": f"Resolve {agent_id} concerns",
                "owner": "Strategy Team",
                "priority": "HIGH",
                "details": mitigation or reasoning
            })
        elif rating == "BLOCK":
            items.append({
                "action": f"CRITICAL: Resolve {agent_id} blocking constraints",
                "owner": "Executive Team",
                "priority": "CRITICAL",
                "details": reasoning
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


# ============================================================================
# CASCADE MODE HELPER FUNCTIONS (Yes-If Protocol & Pyramid Principle)
# ============================================================================

def _identify_illegal_blocks(constraints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify constraints that involve illegal activities.

    Args:
        constraints: List of constraint dicts

    Returns:
        List of illegal constraint dicts
    """
    illegal_keywords = ["illegal", "unlawful", "prohibited", "criminal", "fraud"]

    illegal_blocks = []
    for c in constraints:
        if c.get("rating") == "BLOCK":
            constraint_text = c.get("constraint", "").lower()
            if any(keyword in constraint_text for keyword in illegal_keywords):
                illegal_blocks.append(c)

    return illegal_blocks


def _generate_conditional_approvals(constraints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate "Yes, If..." conditional approvals from constraints.

    This is the core of the Yes-If protocol: convert BLOCKs into mitigations.

    Args:
        constraints: List of constraint dicts

    Returns:
        List of conditional approval dicts
    """
    conditional_approvals = []

    for c in constraints:
        agent = c.get("agent", "unknown")
        rating = c.get("rating")
        constraint = c.get("constraint", "")

        if rating == "BLOCK":
            # Extract mitigation from constraint reasoning
            mitigation = _extract_mitigation_from_constraint(constraint, agent)

            conditional_approvals.append({
                "blocker_agent": agent,
                "original_constraint": constraint[:200],
                "condition": f"YES, IF {mitigation}",
                "mitigation": mitigation,
                "priority": "HIGH"
            })
        elif rating == "WARN":
            # Warnings become lower-priority conditions
            mitigation = _extract_mitigation_from_constraint(constraint, agent)

            conditional_approvals.append({
                "blocker_agent": agent,
                "original_constraint": constraint[:200],
                "condition": f"RECOMMENDED: {mitigation}",
                "mitigation": mitigation,
                "priority": "MEDIUM"
            })

    return conditional_approvals


def _extract_mitigation_from_constraint(constraint: str, agent: str) -> str:
    """Extract mitigation strategy from constraint text.

    Args:
        constraint: Constraint text from agent
        agent: Agent ID

    Returns:
        Mitigation text
    """
    # Look for common mitigation patterns
    patterns = [
        "should", "must", "require", "need to", "recommend",
        "ensure", "implement", "add", "include", "establish"
    ]

    # Try to find sentences with mitigation keywords
    sentences = constraint.split(".")
    for sentence in sentences:
        if any(pattern in sentence.lower() for pattern in patterns):
            return sentence.strip()

    # Fallback: generic mitigation based on agent
    agent_mitigations = {
        "jurist": "legal review and compliance documentation completed",
        "sovereign": "data sovereignty guarantees established",
        "economist": "financial viability validated with risk analysis",
        "technologist": "security assessment and operational readiness confirmed",
        "ecosystem": "sustainability impact assessment completed",
        "philosopher": "ethical review and values alignment confirmed",
        "architect": "technical feasibility study completed",
        "intelligence_sovereign": "AI sovereignty requirements satisfied",
        "ethnographer": "cultural impact assessment conducted",
        "consumer_voice": "consumer protection safeguards implemented"
    }

    return agent_mitigations.get(agent, f"{agent} concerns addressed with appropriate mitigation plan")


def _format_strategic_bet(founder_vision: str, opportunities: List[Dict[str, Any]]) -> str:
    """Format the Strategic Bet section (Pyramid Principle Level 1).

    Args:
        founder_vision: Founder's proposal
        opportunities: Alchemist's reframed opportunities

    Returns:
        Formatted strategic bet text
    """
    content = f"""
## Why We Should Do This

### Founder's Vision: The Market Opportunity

{founder_vision}

### Alchemist's Transformation: Constraints as Competitive Advantages

The consortium has identified {len(opportunities)} ways to convert regulatory constraints into competitive moats:

"""

    for i, opp in enumerate(opportunities[:10], 1):  # Limit to top 10
        alchemy_level = opp.get("alchemy_level", 3)
        opportunity_text = opp.get("opportunity", "")
        trust_premium = opp.get("trust_premium", "Not quantified")

        content += f"""
{i}. **Level {alchemy_level} Alchemy**: {opportunity_text}
   - Trust Premium: {trust_premium}
"""

    content += "\n**Strategic Conclusion**: This proposal combines ambitious market opportunity with regulatory advantage transformation."

    return content


def _format_governance_shield(conditional_approvals: List[Dict[str, Any]], all_constraints: List[Dict[str, Any]]) -> str:
    """Format the Governance Shield section (Pyramid Principle Level 2).

    Args:
        conditional_approvals: List of Yes-If conditions
        all_constraints: All constraints from breakers

    Returns:
        Formatted governance shield text
    """
    if not conditional_approvals:
        return """
## How We Protect the Bet

No blocking constraints identified. The proposal can proceed without additional governance mitigations.

All expert agents have reviewed the Founder's proposal and found it viable within existing compliance frameworks.
"""

    high_priority = [c for c in conditional_approvals if c.get("priority") == "HIGH"]
    medium_priority = [c for c in conditional_approvals if c.get("priority") == "MEDIUM"]

    content = f"""
## How We Protect the Bet

The consortium has applied the **"Yes, If..." Protocol** to convert constraints into governance protections.

**Total Conditional Approvals**: {len(conditional_approvals)} ({len(high_priority)} HIGH priority, {len(medium_priority)} MEDIUM priority)

### High-Priority Mitigations (Required Before Proceeding)

"""

    for i, approval in enumerate(high_priority, 1):
        content += f"""
{i}. **{approval['blocker_agent'].upper()}**: {approval['condition']}
   - Mitigation: {approval['mitigation']}
"""

    if medium_priority:
        content += "\n### Recommended Mitigations (Reduce Risk)\n\n"
        for i, approval in enumerate(medium_priority, 1):
            content += f"{i}. **{approval['blocker_agent'].upper()}**: {approval['condition']}\n"

    content += "\n**Governance Conclusion**: These mitigations convert constraints into competitive advantages (see Strategic Bet)."

    return content


def _format_execution_path(state: ConsortiumState) -> str:
    """Format the Execution Path section (Pyramid Principle Level 3).

    Args:
        state: Current consortium state

    Returns:
        Formatted execution path text
    """
    roadmap = _extract_roadmap(state)
    action_items = _extract_action_items(state)

    content = """
## How We Execute

### Implementation Roadmap

"""

    if roadmap:
        for phase, details in roadmap.items():
            content += f"**{phase}**: {details}\n"
    else:
        content += "Detailed roadmap to be developed based on final approvals.\n"

    content += "\n### Critical Action Items\n\n"

    if action_items:
        for item in action_items[:10]:  # Limit to top 10
            action = item.get("action", "")
            priority = item.get("priority", "MEDIUM")
            owner = item.get("owner", "TBD")
            content += f"- **[{priority}]** {action} (Owner: {owner})\n"
    else:
        content += "No critical action items identified - proceed with standard implementation.\n"

    return content


def _extract_roadmap(state: ConsortiumState) -> Dict[str, str]:
    """Extract roadmap from architect revision if available.

    Args:
        state: Current consortium state

    Returns:
        Roadmap dict
    """
    # Check if architect has provided roadmap info
    agent_responses = state.get("agent_responses", {})
    architect_response = agent_responses.get("architect", {})

    # Look for roadmap-related content in reasoning
    reasoning = architect_response.get("reasoning", "")

    # Simple extraction: return phases if found
    # This is a placeholder - enhance based on actual architect output
    return {
        "Phase 1": "Foundation & Compliance Setup",
        "Phase 2": "Core Implementation",
        "Phase 3": "Market Launch & Scaling"
    }


def _format_kill_switch(state: ConsortiumState) -> str:
    """Format the Kill Switch section (Pyramid Principle Level 4).

    Args:
        state: Current consortium state

    Returns:
        Formatted kill switch text
    """
    cla_criteria = _extract_cla_exit_criteria(state)

    content = """
## How We Exit if Needed

### CLA Gate Exit Criteria

The Conditionality & Leverage Agent (CLA) has established the following exit triggers:

"""

    if cla_criteria:
        for criterion, threshold in cla_criteria.items():
            content += f"- **{criterion}**: {threshold}\n"
    else:
        content += """
- **Commitment Test**: Exit if stakeholder commitment drops below threshold
- **Trigger Test**: Exit if activation conditions fail to materialize
- **Cost Test**: Exit if expenses exceed 120% of projections
- **Leverage Test**: Exit if strategic leverage deteriorates
"""

    content += """

These criteria ensure temporal robustness. Regular CLA reviews will monitor these thresholds.

**Kill Switch Protocol**: If any exit criterion triggers, escalate to board for go/no-go decision.
"""

    return content


def _extract_cla_exit_criteria(state: ConsortiumState) -> Dict[str, str]:
    """Extract CLA exit criteria from CLA review.

    Args:
        state: Current consortium state

    Returns:
        Dict of exit criteria
    """
    cla_review = state.get("cla_review")

    if not cla_review:
        return {}

    # Extract from CLA review if available
    failed_tests = cla_review.get("failed_tests", [])

    criteria = {}
    if "Commitment" in failed_tests:
        criteria["Commitment"] = "Monitor stakeholder commitment quarterly"
    if "Trigger" in failed_tests:
        criteria["Trigger"] = "Re-validate activation conditions at 6-month mark"
    if "Cost" in failed_tests:
        criteria["Cost"] = "Monthly budget review with 20% variance threshold"
    if "Leverage" in failed_tests:
        criteria["Leverage"] = "Quarterly competitive position assessment"

    return criteria
