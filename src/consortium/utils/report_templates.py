"""
Report Templates Utility

Provides template-based generation for report sections.
Enables zero-LLM baseline report generation with professional formatting.
"""

from typing import Dict, List, Any, Optional


def generate_executive_summary(
    query: str,
    final_recommendation: Dict[str, Any],
    convergence_status: Dict[str, Any],
    critical_actions: List[Dict[str, Any]]
) -> str:
    """
    Generate executive summary from final recommendation.

    Args:
        query: Strategic question
        final_recommendation: Synthesized recommendation with action items
        convergence_status: Convergence metrics
        critical_actions: List of critical priority actions

    Returns:
        Executive summary text (board-grade formatting)
    """
    # Extract key data
    recommendation_text = final_recommendation.get('recommendation', '')
    converged = convergence_status.get('converged', False)
    positive_percentage = convergence_status.get('positive_percentage', 0)
    iteration_count = convergence_status.get('iteration_count', 1)

    # Determine recommendation statement
    if converged:
        rec_statement = f"RECOMMENDED WITH CONDITIONS (Consensus: {positive_percentage}%)"
    else:
        rec_statement = "ESCALATED TO HUMAN DECISION (Consortium did not reach consensus)"

    # Build executive summary
    summary = f"""STRATEGIC QUESTION
{query}

RECOMMENDATION
{rec_statement}

The European Consortium has completed {iteration_count} round(s) of deliberation with participation from 12 specialized agents across data sovereignty, financial viability, legal compliance, technical architecture, security, sustainability, ethics, cultural fit, and strategic opportunity analysis.

"""

    # Add key findings section
    summary += "KEY FINDINGS\n\n"

    # Extract findings from recommendation text
    findings = extract_key_findings(recommendation_text, final_recommendation)
    for i, finding in enumerate(findings[:5], 1):
        summary += f"{i}. {finding}\n"

    summary += "\n"

    # Add critical actions section
    if critical_actions:
        summary += "CRITICAL ACTIONS REQUIRED\n\n"
        summary += "The following actions require immediate executive attention and block the decision until addressed:\n\n"

        for i, action in enumerate(critical_actions, 1):
            action_text = action.get('action', '')
            owner = action.get('owner', 'Executive Team')
            details = action.get('details', '')

            summary += f"{i}. {action_text}\n"
            summary += f"   Owner: {owner}\n"
            if details:
                summary += f"   Details: {details}\n"
            summary += "\n"

    # Add risk assessment
    summary += generate_risk_assessment(final_recommendation, convergence_status)

    # Add confidence assessment
    summary += generate_confidence_assessment(convergence_status)

    return summary


def extract_key_findings(recommendation_text: str,
                        final_recommendation: Dict[str, Any]) -> List[str]:
    """
    Extract key findings from recommendation text.

    Args:
        recommendation_text: Full recommendation text
        final_recommendation: Complete recommendation structure

    Returns:
        List of key finding statements
    """
    findings = []

    # Extract from supporting arguments
    supporting_args = final_recommendation.get('supporting_arguments', {})

    # Find BLOCK ratings
    blocks = [(agent, data) for agent, data in supporting_args.items()
             if data.get('rating') == 'BLOCK']
    if blocks:
        findings.append(f"{len(blocks)} blocking concern(s) identified requiring mandatory resolution")

    # Find WARN ratings
    warns = [(agent, data) for agent, data in supporting_args.items()
            if data.get('rating') == 'WARN']
    if warns:
        findings.append(f"{len(warns)} significant warning(s) requiring mitigation strategies")

    # Find ENDORSE ratings
    endorses = [(agent, data) for agent, data in supporting_args.items()
               if data.get('rating') == 'ENDORSE']
    if endorses:
        findings.append(f"{len(endorses)} strong endorsement(s) highlighting strategic advantages")

    # Extract from competitive advantages if present
    comp_advantages = final_recommendation.get('competitive_advantages', {})
    if comp_advantages:
        regulatory_moats = comp_advantages.get('regulatory_moats', [])
        if regulatory_moats:
            findings.append(f"Identified {len(regulatory_moats)} regulatory advantage(s) creating competitive moats")

    # Extract from decision provenance
    provenance = final_recommendation.get('decision_provenance', {})
    tensions_detected = provenance.get('tensions_detected', 0)
    if tensions_detected > 0:
        findings.append(f"{tensions_detected} inter-agent tension(s) detected and resolved through deliberation")

    return findings


def generate_risk_assessment(final_recommendation: Dict[str, Any],
                             convergence_status: Dict[str, Any]) -> str:
    """
    Generate risk assessment section.

    Args:
        final_recommendation: Complete recommendation structure
        convergence_status: Convergence metrics

    Returns:
        Risk assessment text
    """
    assessment = "RISK ASSESSMENT\n\n"

    # Identify major concerns
    supporting_args = final_recommendation.get('supporting_arguments', {})
    blocks = [(agent, data) for agent, data in supporting_args.items()
             if data.get('rating') == 'BLOCK']
    warns = [(agent, data) for agent, data in supporting_args.items()
            if data.get('rating') == 'WARN']

    if blocks:
        assessment += "Major Concerns:\n"
        for agent_id, data in blocks[:3]:  # Top 3 blocks
            concern = data.get('reasoning', '').split('.')[0]
            assessment += f"• {concern}\n"
        assessment += "\n"

    if warns:
        assessment += "Secondary Concerns:\n"
        for agent_id, data in warns[:3]:  # Top 3 warns
            concern = data.get('reasoning', '').split('.')[0]
            assessment += f"• {concern}\n"
        assessment += "\n"

    # Mitigation strategy
    assessment += "Mitigation Strategy:\n"
    if blocks or warns:
        assessment += "Action items have been prioritized by severity (CRITICAL → HIGH → MEDIUM → LOW). "
        assessment += "CRITICAL items must be addressed before proceeding with the decision. "
        assessment += "All mitigation plans are detailed in the Implementation Roadmap section.\n\n"
    else:
        assessment += "No major risks identified. Standard implementation best practices apply.\n\n"

    return assessment


def generate_confidence_assessment(convergence_status: Dict[str, Any]) -> str:
    """
    Generate decision confidence assessment.

    Args:
        convergence_status: Convergence metrics

    Returns:
        Confidence assessment text
    """
    converged = convergence_status.get('converged', False)
    positive_percentage = convergence_status.get('positive_percentage', 0)
    iteration_count = convergence_status.get('iteration_count', 1)
    gate_status = convergence_status.get('gate_status', {})

    assessment = "DECISION CONFIDENCE\n\n"

    if converged:
        assessment += f"Status: CONVERGED after {iteration_count} deliberation round(s)\n"
        assessment += f"Consensus Level: {positive_percentage}% positive ratings (ACCEPT or ENDORSE)\n\n"

        # Gate status details
        block_count = gate_status.get('block_count', 0)
        warn_count = gate_status.get('warn_count', 0)

        assessment += "Convergence Gates Status:\n"
        assessment += f"• Zero blocking concerns: {'✓ PASSED' if block_count == 0 else '✗ FAILED'}\n"
        assessment += f"• Limited warnings (≤2): {'✓ PASSED' if warn_count <= 2 else '✗ FAILED'}\n"
        assessment += f"• Consensus threshold (≥60%): {'✓ PASSED' if positive_percentage >= 60 else '✗ FAILED'}\n\n"

        if block_count == 0 and warn_count <= 2 and positive_percentage >= 60:
            assessment += "The recommendation meets all convergence criteria and has strong consortium support.\n"
        else:
            assessment += "The recommendation converged with some gate waivers. Review mitigation plans carefully.\n"

    else:
        assessment += f"Status: ESCALATED TO HUMAN after {iteration_count} deliberation round(s)\n"
        assessment += f"Consensus Level: {positive_percentage}% positive ratings\n\n"
        assessment += "The consortium could not reach consensus within the configured iteration limit. "
        assessment += "This indicates significant complexity or conflicting requirements that require "
        assessment += "executive judgment to resolve.\n"

    assessment += "\n"
    return assessment


def generate_solution_overview(final_recommendation: Dict[str, Any],
                               agent_responses: Dict[str, Any]) -> str:
    """
    Generate solution overview section.

    Args:
        final_recommendation: Complete recommendation structure
        agent_responses: All agent responses

    Returns:
        Solution overview text
    """
    overview = "RECOMMENDED SOLUTION\n\n"

    # Extract solution description from recommendation
    recommendation_text = final_recommendation.get('recommendation', '')

    # Parse out the main recommendation (first paragraph usually)
    paragraphs = recommendation_text.split('\n\n')
    if paragraphs:
        overview += paragraphs[0] + "\n\n"

    # Add implementation approach
    overview += "IMPLEMENTATION APPROACH\n\n"
    overview += "The recommended solution addresses the following key dimensions:\n\n"

    # Dimension analysis based on agent ratings
    dimensions = analyze_solution_dimensions(agent_responses)
    for dimension, status in dimensions.items():
        overview += f"• {dimension}: {status}\n"

    overview += "\n"

    return overview


def analyze_solution_dimensions(agent_responses: Dict[str, Any]) -> Dict[str, str]:
    """
    Analyze solution across key dimensions.

    Args:
        agent_responses: All agent responses

    Returns:
        Dictionary of dimension → status
    """
    dimensions = {}

    # Data sovereignty dimension
    if 'sovereign' in agent_responses:
        rating = agent_responses['sovereign'].get('rating', 'ACCEPT')
        if rating == 'BLOCK':
            dimensions['Data Sovereignty'] = "CRITICAL CONCERNS - requires mitigation"
        elif rating == 'WARN':
            dimensions['Data Sovereignty'] = "Significant considerations - mitigation planned"
        elif rating == 'ENDORSE':
            dimensions['Data Sovereignty'] = "Strong alignment with EU requirements"
        else:
            dimensions['Data Sovereignty'] = "Acceptable with standard practices"

    # Financial dimension
    if 'economist' in agent_responses:
        rating = agent_responses['economist'].get('rating', 'ACCEPT')
        if rating == 'BLOCK':
            dimensions['Financial Viability'] = "COST PROHIBITIVE - requires restructuring"
        elif rating == 'WARN':
            dimensions['Financial Viability'] = "Cost concerns - optimization needed"
        elif rating == 'ENDORSE':
            dimensions['Financial Viability'] = "Strong ROI with feature subsidies"
        else:
            dimensions['Financial Viability'] = "Acceptable cost-benefit ratio"

    # Technical dimension
    if 'architect' in agent_responses:
        rating = agent_responses['architect'].get('rating', 'ACCEPT')
        if rating == 'BLOCK':
            dimensions['Technical Feasibility'] = "ARCHITECTURAL ISSUES - requires redesign"
        elif rating == 'WARN':
            dimensions['Technical Feasibility'] = "Technical challenges - solution planned"
        elif rating == 'ENDORSE':
            dimensions['Technical Feasibility'] = "Well-architected solution"
        else:
            dimensions['Technical Feasibility'] = "Technically sound"

    # Security dimension
    if 'technologist' in agent_responses:
        rating = agent_responses['technologist'].get('rating', 'ACCEPT')
        if rating == 'BLOCK':
            dimensions['Security & Privacy'] = "CRITICAL VULNERABILITIES - must address"
        elif rating == 'WARN':
            dimensions['Security & Privacy'] = "Security considerations - controls needed"
        elif rating == 'ENDORSE':
            dimensions['Security & Privacy'] = "Excellent security posture"
        else:
            dimensions['Security & Privacy'] = "Adequate security controls"

    # Compliance dimension
    if 'jurist' in agent_responses:
        rating = agent_responses['jurist'].get('rating', 'ACCEPT')
        if rating == 'BLOCK':
            dimensions['Legal Compliance'] = "NON-COMPLIANT - legal issues must resolve"
        elif rating == 'WARN':
            dimensions['Legal Compliance'] = "Compliance considerations - review needed"
        elif rating == 'ENDORSE':
            dimensions['Legal Compliance'] = "Fully compliant with GDPR and EU law"
        else:
            dimensions['Legal Compliance'] = "Generally compliant"

    return dimensions


def generate_implementation_roadmap(action_items: List[Dict[str, Any]]) -> str:
    """
    Generate implementation roadmap from action items.

    Args:
        action_items: List of action items with priorities

    Returns:
        Implementation roadmap text
    """
    roadmap = "IMPLEMENTATION ROADMAP\n\n"

    # Group by priority
    critical = [a for a in action_items if a.get('priority') == 'CRITICAL']
    high = [a for a in action_items if a.get('priority') == 'HIGH']
    medium = [a for a in action_items if a.get('priority') == 'MEDIUM']
    low = [a for a in action_items if a.get('priority') == 'LOW']

    if critical:
        roadmap += "PHASE 1: CRITICAL (Pre-Decision Requirements)\n"
        roadmap += "These items BLOCK the decision and must be resolved before proceeding.\n\n"
        for i, action in enumerate(critical, 1):
            roadmap += format_action_item(i, action)
        roadmap += "\n"

    if high:
        roadmap += "PHASE 2: HIGH PRIORITY (Early Implementation)\n"
        roadmap += "Address these items in the first 30 days of implementation.\n\n"
        for i, action in enumerate(high, 1):
            roadmap += format_action_item(i, action)
        roadmap += "\n"

    if medium:
        roadmap += "PHASE 3: MEDIUM PRIORITY (Ongoing Implementation)\n"
        roadmap += "Address these items within the first 90 days.\n\n"
        for i, action in enumerate(medium, 1):
            roadmap += format_action_item(i, action)
        roadmap += "\n"

    if low:
        roadmap += "PHASE 4: LOW PRIORITY (Optimization)\n"
        roadmap += "These are ongoing improvements and optimizations.\n\n"
        for i, action in enumerate(low, 1):
            roadmap += format_action_item(i, action)
        roadmap += "\n"

    return roadmap


def format_action_item(index: int, action: Dict[str, Any]) -> str:
    """
    Format a single action item for roadmap.

    Args:
        index: Item number
        action: Action item dictionary

    Returns:
        Formatted action item text
    """
    action_text = action.get('action', 'No action specified')
    owner = action.get('owner', 'Not assigned')
    details = action.get('details', '')

    item = f"{index}. {action_text}\n"
    item += f"   Responsible: {owner}\n"
    if details:
        item += f"   Details: {details}\n"
    item += "\n"

    return item


def generate_methodology_appendix(convergence_status: Dict[str, Any],
                                  decision_provenance: Dict[str, Any]) -> str:
    """
    Generate methodology appendix explaining the consortium process.

    Args:
        convergence_status: Convergence metrics
        decision_provenance: Decision provenance data

    Returns:
        Methodology appendix text
    """
    appendix = "APPENDIX: METHODOLOGY\n\n"

    appendix += "THE EUROPEAN CONSORTIUM METHODOLOGY\n\n"

    appendix += """The European Consortium is a multi-agent deliberation system designed for strategic
decision-making in European cloud and AI contexts. The methodology ensures that decisions
account for the unique requirements of European businesses, including data sovereignty,
GDPR compliance, cultural considerations, and sustainable practices.

AGENT STRUCTURE

The consortium comprises 12 specialized agents organized into 4 tiers:

Tier 0 - Foundational (Big Three + AI Sovereignty):
• Data Sovereignty Agent: Vendor lock-in, GDPR, jurisdictional control
• AI Sovereignty Agent: Strategic intelligence protection from foreign AI providers
• Financial Viability Agent: Cost-benefit analysis, ROI, Feature Subsidy Doctrine
• Legal Compliance Agent: Contract review, GDPR, standard contractual clauses

Tier 1 - Technical & Values:
• Systems Architecture Agent: Technical feasibility, disaster recovery planning
• Sustainability Agent: Carbon footprint, renewable energy considerations
• Ethics & Values Agent: Human autonomy, dignity, ethical red lines

Tier 2 - Specialized:
• Cultural Fit Agent: Works councils, regional norms, cultural adaptation
• Security & Technology Agent: Encryption, key management, SIEM integration
• User Protection Agent: Privacy, transparency, consumer rights

Tier 3 - Value Creation (Feature Subsidy Philosophy):
• Regulatory Advantage Agent: Transmuting compliance into competitive moats
• Strategic Opportunities Agent: Feature arbitrage, regulatory subsidy stacks

DELIBERATION PROCESS

"""

    # Add specific metrics for this analysis
    iteration_count = decision_provenance.get('iteration_count', 1)
    agents_engaged = decision_provenance.get('agents_engaged', [])
    tensions_detected = decision_provenance.get('tensions_detected', 0)

    appendix += f"This analysis engaged {len(agents_engaged)} agents over {iteration_count} deliberation round(s).\n"
    if tensions_detected > 0:
        appendix += f"{tensions_detected} inter-agent tension(s) were detected and resolved.\n"

    appendix += "\n"

    appendix += """CONVERGENCE CRITERIA

The consortium uses the following gates to determine convergence:
• Zero BLOCK ratings (no unresolved critical issues)
• Maximum 2 WARN ratings (limited significant concerns)
• Minimum 70% average confidence across agents
• Minimum 60% positive ratings (ACCEPT or ENDORSE)

If convergence is not reached within 3 iterations, the decision is escalated to human judgment.

"""

    return appendix
