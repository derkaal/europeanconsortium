"""Tests for Voice Rules (Feature 4: Final Recommendation Voice - board-grade).

Tests:
1. Hedging word removal
2. Weak phrase strengthening
3. Passive voice detection
4. Action verb presence
5. Executive recommendation formatting
6. Action items formatting
7. Board-readiness validation
8. Integration with synthesizer
"""

import pytest
from src.consortium.tools.voice_rules import (
    apply_voice_rules,
    format_executive_recommendation,
    format_action_items_board_grade,
    validate_board_readiness,
    HEDGING_WORDS,
    WEAK_TO_STRONG,
    ACTION_VERBS
)


# ==============================================================================
# Test: Hedging Word Removal
# ==============================================================================

def test_remove_single_hedging_word():
    """Test removal of single hedging word."""
    text = "We might proceed with this approach."
    transformed, warnings = apply_voice_rules(text)

    assert "might" not in transformed.lower()
    assert any("might" in w.lower() for w in warnings)


def test_remove_multiple_hedging_words():
    """Test removal of multiple hedging words."""
    text = "This could possibly work, but it seems like maybe we should reconsider."
    transformed, warnings = apply_voice_rules(text)

    # Check that hedging words are removed
    for hedge in ["could", "possibly", "seems like", "maybe"]:
        assert hedge not in transformed.lower()


def test_hedging_word_case_insensitive():
    """Test hedging word removal is case-insensitive."""
    text = "Perhaps we should proceed. MAYBE this will work."
    transformed, warnings = apply_voice_rules(text)

    assert "perhaps" not in transformed.lower()
    assert "maybe" not in transformed.lower()


def test_no_hedging_words():
    """Test text without hedging words is unchanged."""
    text = "We must implement this immediately."
    transformed, warnings = apply_voice_rules(text)

    assert transformed == text
    assert len([w for w in warnings if "hedging" in w.lower()]) == 0


# ==============================================================================
# Test: Weak Phrase Strengthening
# ==============================================================================

def test_strengthen_single_weak_phrase():
    """Test strengthening a single weak phrase."""
    text = "We suggest you implement this feature."
    transformed, warnings = apply_voice_rules(text)

    assert "We recommend" in transformed
    assert "we suggest" not in transformed.lower()


def test_strengthen_multiple_weak_phrases():
    """Test strengthening multiple weak phrases."""
    text = "We think this could help you. You should consider it."
    transformed, warnings = apply_voice_rules(text)

    assert "We conclude" in transformed or "we conclude" in transformed
    assert "You must" in transformed or "you must" in transformed


def test_preserve_capitalization():
    """Test that capitalization is preserved when strengthening."""
    text = "We suggest implementing this."
    transformed, warnings = apply_voice_rules(text)

    assert transformed.startswith("We recommend")  # Capital W preserved


def test_no_weak_phrases():
    """Test text without weak phrases is unchanged (except spacing)."""
    text = "Implement this feature immediately."
    transformed, warnings = apply_voice_rules(text)

    # Should be mostly unchanged (minor whitespace cleanup possible)
    assert "implement" in transformed.lower()
    assert "immediately" in transformed.lower()


# ==============================================================================
# Test: Passive Voice Detection
# ==============================================================================

def test_detect_passive_voice():
    """Test passive voice detection."""
    text = "The strategy was approved by the board."
    transformed, warnings = apply_voice_rules(text)

    # Passive voice detected but NOT automatically changed
    assert any("passive voice" in w.lower() for w in warnings)
    # Original text preserved (we only warn, don't auto-fix passive)
    assert "was approved" in transformed.lower()


def test_detect_multiple_passive_voice():
    """Test detection of multiple passive voice instances."""
    text = "The proposal is recommended and has been validated by experts."
    transformed, warnings = apply_voice_rules(text)

    passive_warnings = [w for w in warnings if "passive voice" in w.lower()]
    assert len(passive_warnings) > 0


def test_no_passive_voice():
    """Test text without passive voice."""
    text = "The board approves this strategy."
    transformed, warnings = apply_voice_rules(text)

    passive_warnings = [w for w in warnings if "passive voice" in w.lower()]
    assert len(passive_warnings) == 0


# ==============================================================================
# Test: Executive Recommendation Formatting
# ==============================================================================

def test_format_strongly_recommended():
    """Test formatting for STRONGLY RECOMMENDED."""
    data = {
        "strength": "STRONGLY RECOMMENDED",
        "avg_confidence": 95,
        "summary": "All agents agree this is the best approach."
    }

    formatted = format_executive_recommendation(data)

    assert "PROCEED IMMEDIATELY" in formatted
    assert "95%" in formatted
    assert "European Strategy Consortium" in formatted


def test_format_not_recommended():
    """Test formatting for NOT RECOMMENDED."""
    data = {
        "strength": "NOT RECOMMENDED",
        "avg_confidence": 85,
        "summary": "Critical concerns raised by multiple agents."
    }

    formatted = format_executive_recommendation(data)

    assert "DO NOT PROCEED" in formatted
    assert "85%" in formatted


def test_format_with_conditions():
    """Test formatting for RECOMMENDED WITH CONDITIONS."""
    data = {
        "strength": "RECOMMENDED WITH CONDITIONS",
        "avg_confidence": 70,
        "summary": "Acceptable with mitigation."
    }

    formatted = format_executive_recommendation(data)

    assert "PROCEED WITH CONDITIONS" in formatted
    assert "70%" in formatted


def test_voice_rules_applied_to_summary():
    """Test that voice rules are applied to summary text."""
    data = {
        "strength": "STRONGLY RECOMMENDED",
        "avg_confidence": 90,
        "summary": "We think this might work well."  # Weak phrase + hedging
    }

    formatted = format_executive_recommendation(data)

    # Weak phrases should be strengthened
    assert "we think" not in formatted.lower()
    assert "might" not in formatted.lower()


# ==============================================================================
# Test: Action Items Formatting
# ==============================================================================

def test_format_action_items_basic():
    """Test basic action items formatting."""
    items = [
        {
            "action": "Address economist concerns",
            "owner": "Strategy Team",
            "priority": "high",
            "details": "Review pricing model"
        }
    ]

    formatted = format_action_items_board_grade(items)

    assert len(formatted) == 1
    assert formatted[0]["priority"] == "HIGH"  # Capitalized


def test_format_action_items_prepend_verb():
    """Test prepending action verb if missing."""
    items = [
        {
            "action": "Pricing model review",  # No action verb
            "owner": "Team",
            "priority": "high",
            "details": "Details"
        }
    ]

    formatted = format_action_items_board_grade(items)

    # Should prepend "Execute: " if no action verb found
    assert formatted[0]["action"].startswith("Execute:")


def test_format_action_items_with_verb():
    """Test action items that already have action verbs."""
    items = [
        {
            "action": "Implement new security protocol",
            "owner": "Security Team",
            "priority": "critical",
            "details": "Deploy by Q4"
        }
    ]

    formatted = format_action_items_board_grade(items)

    # Should NOT prepend "Execute:" since "Implement" is an action verb
    assert not formatted[0]["action"].startswith("Execute:")
    assert formatted[0]["action"].startswith("Implement")
    assert formatted[0]["priority"] == "CRITICAL"


def test_format_action_items_voice_rules():
    """Test voice rules applied to action items."""
    items = [
        {
            "action": "We suggest reviewing maybe the pricing",
            "owner": "Team",
            "priority": "high",
            "details": "This could possibly help"
        }
    ]

    formatted = format_action_items_board_grade(items)

    # Hedging words and weak phrases should be removed/strengthened
    action_lower = formatted[0]["action"].lower()
    details_lower = formatted[0]["details"].lower()

    assert "maybe" not in action_lower
    assert "suggest" not in action_lower or "recommend" in action_lower


# ==============================================================================
# Test: Board-Readiness Validation
# ==============================================================================

def test_validate_board_ready_text():
    """Test validation of board-ready text."""
    text = """Implement this strategy immediately. Deploy the new system.
    Ensure compliance with all regulations. Validate all assumptions."""

    result = validate_board_readiness(text)

    assert result["score"] >= 90
    assert "BOARD-READY" in result["readiness"]
    assert result["metrics"]["hedging_words"] == 0
    assert result["metrics"]["action_verbs"] >= 4


def test_validate_text_with_hedging():
    """Test validation detects hedging words."""
    text = "We might possibly consider maybe implementing this approach."

    result = validate_board_readiness(text)

    assert result["score"] < 90
    assert result["metrics"]["hedging_words"] > 0
    assert any("hedging" in issue.lower() for issue in result["issues"])


def test_validate_text_without_action_verbs():
    """Test validation detects missing action verbs."""
    text = "The strategy is good and has been reviewed thoroughly."

    result = validate_board_readiness(text)

    assert any("action verb" in issue.lower() for issue in result["issues"])


def test_validate_text_with_weak_phrases():
    """Test validation detects weak phrases."""
    text = "We think you should consider implementing this."

    result = validate_board_readiness(text)

    assert result["metrics"]["weak_phrases"] > 0
    assert any("weak phrase" in issue.lower() for issue in result["issues"])


def test_validate_excessive_passive_voice():
    """Test validation detects excessive passive voice."""
    text = """The plan was approved. The system is being deployed.
    The results have been validated. Recommendations were made."""

    result = validate_board_readiness(text)

    assert result["metrics"]["passive_voice"] > 3
    assert any("passive voice" in issue.lower() for issue in result["issues"])


# ==============================================================================
# Test: Integration Scenarios
# ==============================================================================

def test_full_transformation_pipeline():
    """Test complete transformation from weak to board-grade."""
    weak_text = """We think you might want to consider implementing this feature.
    It could possibly help improve performance. Perhaps we should test it first.
    In our opinion, this seems like a good approach."""

    transformed, warnings = apply_voice_rules(weak_text)

    # Check transformations applied
    assert "might" not in transformed.lower()
    assert "possibly" not in transformed.lower()
    assert "perhaps" not in transformed.lower()
    assert "seems like" not in transformed.lower()

    # Validate final result
    validation = validate_board_readiness(transformed)
    assert validation["score"] > 60  # Should improve significantly


def test_board_grade_recommendation_full_flow():
    """Test full flow: weak data → formatted recommendation → validation."""
    # Start with weak language
    data = {
        "strength": "STRONGLY RECOMMENDED",
        "avg_confidence": 92,
        "summary": "We think this could possibly work well, and maybe should be deployed."
    }

    # Format with voice rules
    formatted = format_executive_recommendation(data)

    # Validate result
    validation = validate_board_readiness(formatted)

    # Should be board-ready after transformation
    assert validation["score"] >= 75
    assert "might" not in formatted.lower()
    assert "could possibly" not in formatted.lower()


def test_action_items_full_flow():
    """Test action items transformation and validation."""
    items = [
        {
            "action": "We suggest you might want to review the pricing",
            "owner": "Economist",
            "priority": "high",
            "details": "This could help with the budget"
        },
        {
            "action": "Perhaps implement security measures",
            "owner": "Technologist",
            "priority": "critical",
            "details": "It seems important"
        }
    ]

    # Format with voice rules
    formatted = format_action_items_board_grade(items)

    # Check transformations
    for item in formatted:
        # Priority capitalized
        assert item["priority"].isupper()

        # Action has verb or Execute prefix
        action_lower = item["action"].lower()
        has_verb = any(verb in action_lower for verb in ACTION_VERBS)
        has_execute = item["action"].startswith("Execute:")
        assert has_verb or has_execute

        # Hedging removed
        assert "perhaps" not in action_lower
        assert "might" not in action_lower
        assert "seems" not in action_lower
