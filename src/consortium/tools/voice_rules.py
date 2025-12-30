"""Voice Rules - Board-grade final recommendation formatting.

Feature 4: Final Recommendation Voice (board-grade)

Enforces strict voice rules for final recommendations to ensure
board-ready, professional, action-oriented communication.
"""

import re
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


# ==============================================================================
# Voice Rules Configuration
# ==============================================================================

# Words/phrases to REMOVE (hedging, weak language)
HEDGING_WORDS = [
    "maybe", "perhaps", "possibly", "might", "could be", "seems like",
    "appears to", "sort of", "kind of", "somewhat", "fairly", "relatively",
    "quite", "rather", "probably", "likely", "potentially", "arguably",
    "in my opinion", "i think", "i believe", "it seems", "it appears",
    "to some extent", "to a certain degree", "more or less"
]

# Weak phrases to strengthen
WEAK_TO_STRONG = {
    "we suggest": "We recommend",
    "you might want to": "You must",
    "you could": "You should",
    "you should consider": "You must",
    "it would be good to": "You must",
    "it may be beneficial": "It is essential",
    "this could help": "This will",
    "this might work": "This will work",
    "we think": "We conclude",
    "we feel": "We determine",
    "in our view": "Our analysis shows",
    "our opinion is": "Our recommendation is",
    "we believe": "We determine",
    "seems like a good idea": "is the optimal approach",
    "could be a good choice": "is the recommended choice"
}

# Passive voice patterns to detect (for warning)
PASSIVE_VOICE_PATTERNS = [
    r"\bis\s+\w+ed\b",  # "is completed", "is recommended"
    r"\bare\s+\w+ed\b",  # "are completed"
    r"\bwas\s+\w+ed\b",  # "was completed"
    r"\bwere\s+\w+ed\b",  # "were completed"
    r"\bhas\s+been\s+\w+ed\b",  # "has been completed"
    r"\bhave\s+been\s+\w+ed\b",  # "have been completed"
]

# Action verbs for board-grade recommendations
ACTION_VERBS = [
    "implement", "deploy", "establish", "execute", "launch", "adopt",
    "enforce", "mandate", "require", "ensure", "verify", "validate",
    "eliminate", "terminate", "cease", "discontinue", "prioritize",
    "accelerate", "optimize", "streamline", "consolidate", "standardize"
]


# ==============================================================================
# Voice Rule Application
# ==============================================================================

def apply_voice_rules(text: str) -> Tuple[str, List[str]]:
    """Apply board-grade voice rules to text.

    Transformations:
    1. Remove hedging words
    2. Strengthen weak phrases
    3. Ensure action-oriented language
    4. Detect passive voice (warning only)

    Args:
        text: Original text

    Returns:
        Tuple of (transformed_text, list of warnings)
    """
    warnings = []
    transformed = text

    # 1. Remove hedging words
    for hedge in HEDGING_WORDS:
        pattern = r'\b' + re.escape(hedge) + r'\b'
        if re.search(pattern, transformed, re.IGNORECASE):
            transformed = re.sub(pattern, '', transformed, flags=re.IGNORECASE)
            warnings.append(f"Removed hedging word: '{hedge}'")

    # 2. Strengthen weak phrases
    for weak, strong in WEAK_TO_STRONG.items():
        pattern = re.escape(weak)
        if re.search(pattern, transformed, re.IGNORECASE):
            # Preserve capitalization of first letter
            def replacer(match):
                original = match.group(0)
                if original[0].isupper():
                    return strong[0].upper() + strong[1:]
                return strong

            transformed = re.sub(pattern, replacer, transformed, flags=re.IGNORECASE)
            warnings.append(f"Strengthened: '{weak}' → '{strong}'")

    # 3. Check for passive voice (warning only, don't auto-fix)
    for pattern in PASSIVE_VOICE_PATTERNS:
        matches = re.findall(pattern, transformed, re.IGNORECASE)
        if matches:
            warnings.append(f"Passive voice detected: {matches[:3]}")  # Show first 3

    # 4. Clean up extra whitespace from removals
    transformed = re.sub(r'\s+', ' ', transformed)
    transformed = re.sub(r'\s+([.,;:])', r'\1', transformed)

    return transformed, warnings


def format_executive_recommendation(
    recommendation_data: Dict[str, Any]
) -> str:
    """Format executive recommendation with board-grade voice.

    Args:
        recommendation_data: Dict with strength, confidence, summary, etc.

    Returns:
        Board-grade formatted recommendation
    """
    strength = recommendation_data.get("strength", "REQUIRES FURTHER ANALYSIS")
    confidence = recommendation_data.get("avg_confidence", 0)
    summary = recommendation_data.get("summary", "")

    # Apply voice rules to summary
    summary_clean, warnings = apply_voice_rules(summary)

    if warnings:
        logger.info(f"Applied {len(warnings)} voice transformations")

    # Format with strong, direct language
    if "STRONGLY RECOMMENDED" in strength:
        opening = "**RECOMMENDATION: PROCEED IMMEDIATELY**"
    elif "RECOMMENDED WITH CONDITIONS" in strength:
        opening = "**RECOMMENDATION: PROCEED WITH CONDITIONS**"
    elif "PROCEED WITH CAUTION" in strength:
        opening = "**RECOMMENDATION: PROCEED WITH MITIGATION**"
    elif "NOT RECOMMENDED" in strength:
        opening = "**RECOMMENDATION: DO NOT PROCEED**"
    else:
        opening = "**RECOMMENDATION: ADDITIONAL ANALYSIS REQUIRED**"

    # Build board-grade recommendation
    recommendation = f"""{opening}

**Confidence:** {confidence:.0f}%

**Executive Summary:**
{summary_clean}

**Analysis Basis:**
This recommendation reflects consensus analysis by the European Strategy Consortium's
expert panel, applying European market requirements, regulatory constraints, and
strategic priorities."""

    return recommendation


def format_action_items_board_grade(
    action_items: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Format action items with board-grade language.

    Args:
        action_items: List of action item dicts

    Returns:
        Board-grade formatted action items
    """
    formatted = []

    for item in action_items:
        action = item.get("action", "")
        owner = item.get("owner", "")
        priority = item.get("priority", "")
        details = item.get("details", "")

        # Apply voice rules to action and details
        action_clean, _ = apply_voice_rules(action)
        details_clean, _ = apply_voice_rules(details)

        # Ensure action starts with action verb
        if not any(action_clean.lower().startswith(verb) for verb in ACTION_VERBS):
            # Prepend "Execute: " if no action verb
            action_clean = f"Execute: {action_clean}"

        formatted.append({
            "action": action_clean,
            "owner": owner,
            "priority": priority.upper(),  # All caps for priority
            "details": details_clean
        })

    return formatted


def validate_board_readiness(text: str) -> Dict[str, Any]:
    """Validate text meets board-readiness criteria.

    Checks:
    1. No hedging words
    2. Contains action verbs
    3. Minimal passive voice
    4. Clear structure

    Args:
        text: Text to validate

    Returns:
        Validation result dict with score and issues
    """
    issues = []
    score = 100  # Start at perfect

    # Check for hedging words
    hedge_count = 0
    for hedge in HEDGING_WORDS:
        pattern = r'\b' + re.escape(hedge) + r'\b'
        matches = len(re.findall(pattern, text, re.IGNORECASE))
        hedge_count += matches

    if hedge_count > 0:
        issues.append(f"Contains {hedge_count} hedging words/phrases")
        score -= min(hedge_count * 10, 30)  # Max -30 for hedging

    # Check for action verbs
    action_verb_count = sum(
        len(re.findall(r'\b' + verb + r'\b', text, re.IGNORECASE))
        for verb in ACTION_VERBS
    )

    if action_verb_count == 0:
        issues.append("No action verbs found")
        score -= 20
    elif action_verb_count < 2:
        issues.append("Insufficient action verbs (need more directive language)")
        score -= 10

    # Check for passive voice
    passive_count = 0
    for pattern in PASSIVE_VOICE_PATTERNS:
        matches = len(re.findall(pattern, text, re.IGNORECASE))
        passive_count += matches

    if passive_count > 3:
        issues.append(f"Excessive passive voice ({passive_count} instances)")
        score -= min((passive_count - 3) * 5, 20)  # Max -20

    # Check for weak phrases
    weak_count = sum(
        1 for weak in WEAK_TO_STRONG.keys()
        if re.search(re.escape(weak), text, re.IGNORECASE)
    )

    if weak_count > 0:
        issues.append(f"Contains {weak_count} weak phrases")
        score -= min(weak_count * 5, 15)

    # Determine readiness level
    if score >= 90:
        readiness = "BOARD-READY"
    elif score >= 75:
        readiness = "ACCEPTABLE (minor revisions recommended)"
    elif score >= 60:
        readiness = "NEEDS REVISION"
    else:
        readiness = "NOT BOARD-READY"

    return {
        "score": max(score, 0),
        "readiness": readiness,
        "issues": issues,
        "metrics": {
            "hedging_words": hedge_count,
            "action_verbs": action_verb_count,
            "passive_voice": passive_count,
            "weak_phrases": weak_count
        }
    }
