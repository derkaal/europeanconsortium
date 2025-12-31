"""
Chapter Organization Utility

Organizes agent responses into thematic chapters for structured PDF reports.
Maps 12 agents into 6 thematic chapters based on domain expertise.
"""

from typing import Dict, List, Any, Tuple

# Rating severity for sorting (BLOCK is most severe)
RATING_SEVERITY = {
    'BLOCK': 4,
    'WARN': 3,
    'ACCEPT': 2,
    'ENDORSE': 1
}

# Chapter structure mapping agents to thematic chapters
CHAPTER_STRUCTURE = {
    "1_sovereignty": {
        "title": "Data & AI Sovereignty",
        "agents": ["sovereign", "intelligence_sovereign"],
        "focus": "Jurisdictional control, vendor lock-in, strategic intelligence protection",
        "key_themes": ["GDPR compliance", "Data residency", "AI sovereignty", "Vendor independence"]
    },
    "2_financial_legal": {
        "title": "Financial & Legal Analysis",
        "agents": ["economist", "jurist"],
        "focus": "Cost-benefit analysis, ROI, Feature Subsidy Doctrine, legal compliance",
        "key_themes": ["Total Cost of Ownership", "Feature subsidies", "Contract terms", "Legal compliance"]
    },
    "3_technical": {
        "title": "Technical Architecture & Security",
        "agents": ["architect", "technologist"],
        "focus": "Systems design, disaster recovery, encryption, security monitoring",
        "key_themes": ["Architecture patterns", "Disaster recovery", "Encryption standards", "Security controls"]
    },
    "4_values": {
        "title": "Sustainability & Ethics",
        "agents": ["ecosystem", "philosopher"],
        "focus": "Environmental impact, carbon footprint, ethical considerations, human dignity",
        "key_themes": ["Carbon emissions", "Renewable energy", "Ethical red lines", "Human autonomy"]
    },
    "5_cultural_user": {
        "title": "Cultural Fit & User Protection",
        "agents": ["ethnographer", "consumer_voice"],
        "focus": "Regional cultural norms, works councils, user privacy, transparency",
        "key_themes": ["Works council engagement", "Cultural adaptation", "User privacy", "Transparency"]
    },
    "6_strategic": {
        "title": "Strategic Opportunities & Value Creation",
        "agents": ["alchemist", "founder"],
        "focus": "Regulation-to-value transmutation, feature arbitrage, competitive advantage",
        "key_themes": ["Regulatory moats", "Feature subsidies", "Competitive advantages", "Market opportunities"]
    }
}

# Agent display names with emojis
AGENT_DISPLAY_NAMES = {
    "sovereign": "🛡️ Data Sovereignty",
    "intelligence_sovereign": "🤖 AI Sovereignty",
    "economist": "💰 Financial Viability",
    "jurist": "⚖️ Legal Compliance",
    "architect": "🏗️ Systems Architecture",
    "technologist": "🔒 Security & Technology",
    "ecosystem": "🌱 Sustainability",
    "philosopher": "🧠 Ethics & Values",
    "ethnographer": "🌍 Cultural Fit",
    "consumer_voice": "👥 User Protection",
    "alchemist": "💎 Regulatory Advantage",
    "founder": "🚀 Strategic Opportunities"
}


def organize_into_chapters(agent_responses: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Organize agent responses into thematic chapters.

    Args:
        agent_responses: Dictionary of agent responses keyed by agent_id

    Returns:
        List of chapter dictionaries with organized content
    """
    chapters = []

    for chapter_id, chapter_config in CHAPTER_STRUCTURE.items():
        # Collect relevant agent responses for this chapter
        chapter_agents = {}
        for agent_id in chapter_config['agents']:
            if agent_id in agent_responses:
                chapter_agents[agent_id] = agent_responses[agent_id]

        # Skip chapter if no agents have responses
        if not chapter_agents:
            continue

        # Sort agents by rating severity (BLOCK first, then WARN, etc.)
        sorted_agents = sorted(
            chapter_agents.items(),
            key=lambda x: RATING_SEVERITY.get(x[1].get('rating', 'ACCEPT'), 0),
            reverse=True
        )

        # Generate chapter introduction
        intro = generate_chapter_intro(
            title=chapter_config['title'],
            focus=chapter_config['focus'],
            agents=sorted_agents
        )

        # Extract key insights from agents in this chapter
        key_insights = extract_chapter_insights(sorted_agents, chapter_config)

        # Build chapter structure
        chapter = {
            'id': chapter_id,
            'number': int(chapter_id.split('_')[0]),
            'title': chapter_config['title'],
            'introduction': intro,
            'focus': chapter_config['focus'],
            'agents': sorted_agents,
            'key_insights': key_insights,
            'key_themes': chapter_config['key_themes']
        }

        chapters.append(chapter)

    return chapters


def generate_chapter_intro(title: str, focus: str, agents: List[Tuple[str, Dict]]) -> str:
    """
    Generate introduction text for a chapter.

    Args:
        title: Chapter title
        focus: Chapter focus area
        agents: List of (agent_id, response) tuples

    Returns:
        Introduction paragraph
    """
    # Count ratings
    rating_counts = {}
    for agent_id, response in agents:
        rating = response.get('rating', 'ACCEPT')
        rating_counts[rating] = rating_counts.get(rating, 0) + 1

    # Build rating summary
    rating_parts = []
    if rating_counts.get('BLOCK', 0) > 0:
        rating_parts.append(f"{rating_counts['BLOCK']} blocking concern(s)")
    if rating_counts.get('WARN', 0) > 0:
        rating_parts.append(f"{rating_counts['WARN']} warning(s)")
    if rating_counts.get('ENDORSE', 0) > 0:
        rating_parts.append(f"{rating_counts['ENDORSE']} endorsement(s)")
    elif rating_counts.get('ACCEPT', 0) > 0:
        rating_parts.append(f"{rating_counts['ACCEPT']} acceptance(s)")

    rating_summary = ", ".join(rating_parts) if rating_parts else "general acceptance"

    # Generate intro
    intro = f"""This chapter examines {focus}.

The consortium's analysis in this domain reveals {rating_summary}. The following agents contributed their specialized perspectives:"""

    for agent_id, response in agents:
        display_name = AGENT_DISPLAY_NAMES.get(agent_id, agent_id)
        intro += f"\n• {display_name}"

    return intro


def extract_chapter_insights(agents: List[Tuple[str, Dict]],
                             chapter_config: Dict[str, Any]) -> List[str]:
    """
    Extract key insights from agents in a chapter.

    Args:
        agents: List of (agent_id, response) tuples
        chapter_config: Chapter configuration

    Returns:
        List of key insight strings
    """
    insights = []

    for agent_id, response in agents:
        rating = response.get('rating', 'ACCEPT')
        reasoning = response.get('reasoning', '')

        # Extract critical concerns from BLOCK/WARN ratings
        if rating == 'BLOCK':
            attack_vector = response.get('attack_vector', '')
            if attack_vector:
                insights.append(f"CRITICAL: {attack_vector}")

        elif rating == 'WARN':
            # Extract first sentence of reasoning as insight
            first_sentence = reasoning.split('.')[0] if reasoning else ''
            if first_sentence:
                insights.append(f"Important consideration: {first_sentence}")

        elif rating == 'ENDORSE':
            # Extract positive insights from endorsements
            if 'advantage' in reasoning.lower() or 'benefit' in reasoning.lower():
                first_sentence = reasoning.split('.')[0] if reasoning else ''
                if first_sentence:
                    insights.append(f"Strategic advantage: {first_sentence}")

    # Limit to top 3 insights per chapter
    return insights[:3]


def get_chapter_summary(chapter: Dict[str, Any]) -> str:
    """
    Generate a summary statement for a chapter.

    Args:
        chapter: Chapter dictionary

    Returns:
        Summary string
    """
    # Count ratings
    ratings = [response.get('rating', 'ACCEPT')
              for _, response in chapter['agents']]

    has_blocks = 'BLOCK' in ratings
    has_warns = 'WARN' in ratings
    has_endorses = 'ENDORSE' in ratings

    if has_blocks:
        return f"This area presents critical concerns that must be addressed before proceeding."
    elif has_warns:
        return f"This area requires careful consideration and mitigation planning."
    elif has_endorses:
        return f"This area presents strategic opportunities and aligns well with European values."
    else:
        return f"This area is generally acceptable with standard implementation practices."


def format_agent_section(agent_id: str, response: Dict[str, Any],
                        compact: bool = False) -> str:
    """
    Format an agent's response for inclusion in a chapter.

    Args:
        agent_id: Agent identifier
        response: Agent response dictionary
        compact: If True, use compact formatting

    Returns:
        Formatted section text
    """
    display_name = AGENT_DISPLAY_NAMES.get(agent_id, agent_id)
    rating = response.get('rating', 'ACCEPT')
    confidence = response.get('confidence', 0.0)
    reasoning = response.get('reasoning', 'No reasoning provided.')
    attack_vector = response.get('attack_vector', '')
    mitigation_plan = response.get('mitigation_plan', '')

    if compact:
        # Compact format for appendix
        section = f"{display_name} - {rating} (Confidence: {confidence:.0%})\n"
        section += f"{reasoning}\n"
    else:
        # Full format for main chapters
        section = f"\n{display_name}\n"
        section += f"Rating: {rating} | Confidence: {confidence:.0%}\n\n"
        section += f"{reasoning}\n"

        if attack_vector:
            section += f"\nKey Concern: {attack_vector}\n"

        if mitigation_plan:
            section += f"\nMitigation Strategy: {mitigation_plan}\n"

    return section


def get_agent_tier(agent_id: str) -> str:
    """
    Get the tier classification for an agent.

    Args:
        agent_id: Agent identifier

    Returns:
        Tier name
    """
    tier_mapping = {
        "sovereign": "Tier 0 - Foundational",
        "intelligence_sovereign": "Tier 0 - Foundational",
        "economist": "Tier 0 - Foundational",
        "jurist": "Tier 0 - Foundational",
        "architect": "Tier 1 - Technical & Values",
        "ecosystem": "Tier 1 - Technical & Values",
        "philosopher": "Tier 1 - Technical & Values",
        "ethnographer": "Tier 2 - Specialized",
        "technologist": "Tier 2 - Specialized",
        "consumer_voice": "Tier 2 - Specialized",
        "alchemist": "Tier 3 - Value Creation",
        "founder": "Tier 3 - Value Creation"
    }
    return tier_mapping.get(agent_id, "Unknown")
