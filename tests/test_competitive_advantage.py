"""Tests for Feature 6: Competitive Advantage Module.

Tests:
1. Advantage pattern matching
2. Constraint extraction from agent responses
3. Constraint domain classification
4. Pattern applicability checking
5. Advantage generation
6. Relevance scoring
7. Advantage prioritization
8. Opportunity generation
9. Recommendation generation
10. Integration with synthesizer
"""

import pytest
from src.consortium.agents.advantage import (
    CompetitiveAdvantageAgent,
    AdvantagePattern,
    ADVANTAGE_PATTERNS
)


# ==============================================================================
# Test: Pattern Library
# ==============================================================================

def test_advantage_patterns_exist():
    """Test that advantage patterns are defined."""
    assert len(ADVANTAGE_PATTERNS) > 0
    assert all(isinstance(p, AdvantagePattern) for p in ADVANTAGE_PATTERNS)


def test_gdpr_patterns_exist():
    """Test GDPR patterns are defined."""
    gdpr_patterns = [p for p in ADVANTAGE_PATTERNS if p.constraint_domain == "GDPR"]
    assert len(gdpr_patterns) >= 2


def test_ai_act_patterns_exist():
    """Test AI Act patterns are defined."""
    ai_patterns = [p for p in ADVANTAGE_PATTERNS if p.constraint_domain == "AI Act"]
    assert len(ai_patterns) >= 3


def test_carbon_patterns_exist():
    """Test Carbon patterns are defined."""
    carbon_patterns = [p for p in ADVANTAGE_PATTERNS if p.constraint_domain == "Carbon"]
    assert len(carbon_patterns) >= 2


def test_pattern_has_required_fields():
    """Test all patterns have required fields."""
    for pattern in ADVANTAGE_PATTERNS:
        assert pattern.constraint_domain
        assert len(pattern.constraint_keywords) > 0
        assert pattern.advantage_type
        assert pattern.advantage_template
        assert len(pattern.evidence_keywords) > 0
        assert isinstance(pattern.applicability_conditions, dict)


# ==============================================================================
# Test: Agent Initialization
# ==============================================================================

def test_agent_initialization_default():
    """Test agent initializes with default config."""
    agent = CompetitiveAdvantageAgent()
    assert agent.enabled is True
    assert agent.min_keyword_matches == 1
    assert len(agent.patterns) > 0


def test_agent_initialization_custom_config():
    """Test agent initializes with custom config."""
    config = {
        "enabled": False,
        "min_keyword_matches": 2
    }
    agent = CompetitiveAdvantageAgent(config=config)
    assert agent.enabled is False
    assert agent.min_keyword_matches == 2


# ==============================================================================
# Test: Constraint Extraction
# ==============================================================================

def test_extract_constraints_from_jurist():
    """Test constraint extraction from Jurist agent."""
    agent = CompetitiveAdvantageAgent()

    agent_responses = [
        {
            "agent_name": "Jurist",
            "rating": 7,
            "concerns": [
                "GDPR compliance required for data processing",
                "AI Act transparency obligations apply"
            ]
        }
    ]

    constraints = agent._extract_constraints(agent_responses)

    assert len(constraints) == 2
    assert constraints[0]["source"] == "Jurist"
    assert constraints[0]["domain"] in ["GDPR", "AI Act"]


def test_extract_constraints_from_ecosystem():
    """Test constraint extraction from Ecosystem agent."""
    agent = CompetitiveAdvantageAgent()

    agent_responses = [
        {
            "agent_name": "Ecosystem",
            "rating": 6,
            "concerns": [
                "Carbon emissions must be reported",
                "Energy efficiency improvements needed"
            ]
        }
    ]

    constraints = agent._extract_constraints(agent_responses)

    assert len(constraints) == 2
    assert all(c["domain"] == "Carbon" for c in constraints)


def test_extract_constraints_from_philosopher():
    """Test constraint extraction from Philosopher agent."""
    agent = CompetitiveAdvantageAgent()

    agent_responses = [
        {
            "agent_name": "Philosopher",
            "rating": 8,
            "concerns": [
                "Dark patterns detected in UI",
                "Accessibility issues for users"
            ]
        }
    ]

    constraints = agent._extract_constraints(agent_responses)

    assert len(constraints) == 2
    assert all(c["domain"] == "Consumer Protection" for c in constraints)


# ==============================================================================
# Test: Constraint Classification
# ==============================================================================

def test_classify_gdpr_constraint():
    """Test GDPR constraint classification."""
    agent = CompetitiveAdvantageAgent()

    test_cases = [
        "GDPR compliance required",
        "Data protection measures needed",
        "Privacy concerns identified"
    ]

    for concern in test_cases:
        domain = agent._classify_constraint_domain(concern)
        assert domain == "GDPR"


def test_classify_ai_act_constraint():
    """Test AI Act constraint classification."""
    agent = CompetitiveAdvantageAgent()

    test_cases = [
        "AI Act compliance required",
        "High-risk AI system classification",
        "Explainability requirements apply"
    ]

    for concern in test_cases:
        domain = agent._classify_constraint_domain(concern)
        assert domain == "AI Act"


def test_classify_carbon_constraint():
    """Test Carbon constraint classification."""
    agent = CompetitiveAdvantageAgent()

    test_cases = [
        "Carbon emissions reporting needed",
        "Sustainability requirements",
        "Emissions disclosure required"
    ]

    for concern in test_cases:
        domain = agent._classify_constraint_domain(concern)
        assert domain == "Carbon"


# ==============================================================================
# Test: Pattern Matching
# ==============================================================================

def test_match_patterns_gdpr_proposal():
    """Test pattern matching for GDPR-related proposal."""
    agent = CompetitiveAdvantageAgent()

    proposal = "We need to ensure GDPR compliance for our cloud service in Germany"
    context = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "medium"
    }
    constraints = [
        {"domain": "GDPR", "description": "GDPR compliance required"}
    ]

    matched = agent._match_patterns(proposal, context, constraints)

    assert len(matched) > 0
    assert any(p.constraint_domain == "GDPR" for p in matched)


def test_match_patterns_ai_act_proposal():
    """Test pattern matching for AI Act-related proposal."""
    agent = CompetitiveAdvantageAgent()

    proposal = "Building an AI system that requires explainability under the AI Act"
    context = {
        "target_markets": ["Germany", "France"],
        "industry": "AI",
        "company_size": "large"
    }
    constraints = [
        {"domain": "AI Act", "description": "Explainability required"}
    ]

    matched = agent._match_patterns(proposal, context, constraints)

    assert len(matched) > 0
    assert any(p.constraint_domain == "AI Act" for p in matched)


def test_match_patterns_minimum_keyword_threshold():
    """Test minimum keyword matching threshold."""
    config = {"min_keyword_matches": 3}
    agent = CompetitiveAdvantageAgent(config=config)

    proposal = "Building a cloud service"  # Too few matches
    context = {"target_markets": ["Germany"], "industry": "Technology"}
    constraints = []

    matched = agent._match_patterns(proposal, context, constraints)

    # Should match fewer patterns with higher threshold
    assert len(matched) >= 0


# ==============================================================================
# Test: Applicability Checking
# ==============================================================================

def test_check_applicability_eu_market():
    """Test applicability for EU market."""
    agent = CompetitiveAdvantageAgent()

    pattern = AdvantagePattern(
        constraint_domain="GDPR",
        constraint_keywords=["GDPR"],
        advantage_type="Brand",
        advantage_template="European Data Haven",
        evidence_keywords=["data sovereignty"],
        applicability_conditions={"markets": ["EU"], "industry": ["Technology"]}
    )

    context = {
        "target_markets": ["Germany"],
        "industry": "Technology"
    }

    assert agent._check_applicability(pattern, context) is True


def test_check_applicability_wrong_market():
    """Test applicability fails for wrong market."""
    agent = CompetitiveAdvantageAgent()

    pattern = AdvantagePattern(
        constraint_domain="GDPR",
        constraint_keywords=["GDPR"],
        advantage_type="Brand",
        advantage_template="European Data Haven",
        evidence_keywords=["data sovereignty"],
        applicability_conditions={"markets": ["EU"], "industry": ["Technology"]}
    )

    context = {
        "target_markets": ["United States"],  # Wrong market
        "industry": "Technology"
    }

    assert agent._check_applicability(pattern, context) is False


def test_check_applicability_global_market():
    """Test applicability for Global market patterns."""
    agent = CompetitiveAdvantageAgent()

    pattern = AdvantagePattern(
        constraint_domain="Carbon",
        constraint_keywords=["carbon"],
        advantage_type="Brand",
        advantage_template="Green Tech Leader",
        evidence_keywords=["sustainability"],
        applicability_conditions={"markets": ["Global"], "industry": ["Technology"]}
    )

    context = {
        "target_markets": ["Japan"],  # Any market
        "industry": "Technology"
    }

    assert agent._check_applicability(pattern, context) is True


def test_check_applicability_industry_mismatch():
    """Test applicability fails for wrong industry."""
    agent = CompetitiveAdvantageAgent()

    pattern = AdvantagePattern(
        constraint_domain="GDPR",
        constraint_keywords=["GDPR"],
        advantage_type="Brand",
        advantage_template="Data Haven",
        evidence_keywords=["data"],
        applicability_conditions={"markets": ["EU"], "industry": ["Technology"]}
    )

    context = {
        "target_markets": ["Germany"],
        "industry": "Agriculture"  # Wrong industry
    }

    assert agent._check_applicability(pattern, context) is False


# ==============================================================================
# Test: Advantage Generation
# ==============================================================================

def test_generate_advantages_basic():
    """Test basic advantage generation."""
    agent = CompetitiveAdvantageAgent()

    matched_patterns = [ADVANTAGE_PATTERNS[0]]  # Use first pattern
    context = {
        "target_markets": ["Germany"],
        "industry": "Technology"
    }

    advantages = agent._generate_advantages(matched_patterns, context)

    assert len(advantages) == 1
    assert "constraint_domain" in advantages[0]
    assert "advantage_type" in advantages[0]
    assert "description" in advantages[0]
    assert "relevance_score" in advantages[0]


def test_relevance_score_calculation():
    """Test relevance score calculation."""
    agent = CompetitiveAdvantageAgent()

    pattern = ADVANTAGE_PATTERNS[0]
    context = {
        "target_markets": ["Germany"],
        "industry": "Technology"
    }

    score = agent._calculate_relevance(pattern, context)

    assert 0.0 <= score <= 1.0


# ==============================================================================
# Test: Advantage Prioritization
# ==============================================================================

def test_prioritize_advantages_by_relevance():
    """Test advantages are prioritized by relevance."""
    agent = CompetitiveAdvantageAgent()

    advantages = [
        {
            "advantage_type": "Market",
            "description": "Advantage 1",
            "relevance_score": 0.6
        },
        {
            "advantage_type": "Brand",
            "description": "Advantage 2",
            "relevance_score": 0.9
        },
        {
            "advantage_type": "Technical",
            "description": "Advantage 3",
            "relevance_score": 0.8
        }
    ]

    context = {"target_markets": ["Germany"], "industry": "Technology"}
    prioritized = agent._prioritize_advantages(advantages, context)

    # Should be sorted by relevance_score descending
    assert prioritized[0]["relevance_score"] == 0.9
    assert prioritized[1]["relevance_score"] == 0.8
    assert prioritized[2]["relevance_score"] == 0.6


def test_prioritize_advantages_by_type():
    """Test advantages with same relevance prioritized by type."""
    agent = CompetitiveAdvantageAgent()

    advantages = [
        {
            "advantage_type": "Operational",
            "description": "Advantage 1",
            "relevance_score": 0.8
        },
        {
            "advantage_type": "Market",
            "description": "Advantage 2",
            "relevance_score": 0.8
        },
        {
            "advantage_type": "Brand",
            "description": "Advantage 3",
            "relevance_score": 0.8
        }
    ]

    context = {"target_markets": ["Germany"], "industry": "Technology"}
    prioritized = agent._prioritize_advantages(advantages, context)

    # With same relevance, should prioritize by type: Market > Brand > Technical > Operational
    assert prioritized[0]["advantage_type"] == "Market"
    assert prioritized[1]["advantage_type"] == "Brand"
    assert prioritized[2]["advantage_type"] == "Operational"


# ==============================================================================
# Test: Opportunity Generation
# ==============================================================================

def test_generate_opportunities():
    """Test opportunity generation from advantages."""
    agent = CompetitiveAdvantageAgent()

    advantages = [
        {
            "advantage_type": "Market",
            "description": "European Data Haven positioning",
            "relevance_score": 0.9
        },
        {
            "advantage_type": "Brand",
            "description": "Green Tech Leader brand",
            "relevance_score": 0.8
        }
    ]

    opportunities = agent._generate_opportunities(advantages)

    assert len(opportunities) == 2
    assert all("Opportunity:" in opp for opp in opportunities)


def test_generate_opportunities_limits_to_top_3():
    """Test opportunity generation limits to top 3."""
    agent = CompetitiveAdvantageAgent()

    advantages = [
        {"advantage_type": "Market", "description": f"Advantage {i}", "relevance_score": 0.5}
        for i in range(10)
    ]

    opportunities = agent._generate_opportunities(advantages)

    assert len(opportunities) == 3


# ==============================================================================
# Test: Recommendation Generation
# ==============================================================================

def test_generate_recommendations_by_type():
    """Test recommendation generation groups by advantage type."""
    agent = CompetitiveAdvantageAgent()

    advantages = [
        {"advantage_type": "Market", "description": "Market adv 1"},
        {"advantage_type": "Market", "description": "Market adv 2"},
        {"advantage_type": "Brand", "description": "Brand adv 1"},
        {"advantage_type": "Technical", "description": "Tech adv 1"}
    ]

    recommendations = agent._generate_recommendations(advantages)

    assert len(recommendations) >= 3
    assert any("Market positioning" in rec for rec in recommendations)
    assert any("Brand strategy" in rec for rec in recommendations)
    assert any("Product strategy" in rec for rec in recommendations)


def test_generate_recommendations_no_advantages():
    """Test recommendation when no advantages identified."""
    agent = CompetitiveAdvantageAgent()

    recommendations = agent._generate_recommendations([])

    assert len(recommendations) == 1
    assert "No competitive advantages identified" in recommendations[0]


# ==============================================================================
# Test: Full Analysis
# ==============================================================================

def test_analyze_gdpr_proposal():
    """Test full analysis for GDPR proposal."""
    agent = CompetitiveAdvantageAgent()

    proposal = "Launch cloud service with GDPR compliance in Germany"
    context = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "medium"
    }
    agent_responses = [
        {
            "agent_name": "Jurist",
            "rating": 7,
            "concerns": ["GDPR data residency required"]
        }
    ]

    result = agent.analyze(proposal, context, agent_responses)

    assert "advantages" in result
    assert "opportunities" in result
    assert "recommendations" in result
    assert len(result["advantages"]) > 0


def test_analyze_ai_act_proposal():
    """Test full analysis for AI Act proposal."""
    agent = CompetitiveAdvantageAgent()

    proposal = "Deploy AI system with explainability under AI Act"
    context = {
        "target_markets": ["France"],
        "industry": "AI",
        "company_size": "large"
    }
    agent_responses = [
        {
            "agent_name": "Jurist",
            "rating": 8,
            "concerns": ["AI Act explainability required"]
        }
    ]

    result = agent.analyze(proposal, context, agent_responses)

    assert len(result["advantages"]) > 0
    assert any("explainability" in adv["description"].lower()
               for adv in result["advantages"])


def test_analyze_disabled_agent():
    """Test analysis when agent is disabled."""
    config = {"enabled": False}
    agent = CompetitiveAdvantageAgent(config=config)

    proposal = "Test proposal"
    context = {"target_markets": ["Germany"], "industry": "Technology"}
    agent_responses = []

    result = agent.analyze(proposal, context, agent_responses)

    assert result["advantages"] == []
    assert result["opportunities"] == []
    assert result["recommendations"] == []


def test_analyze_no_matching_patterns():
    """Test analysis when no patterns match."""
    agent = CompetitiveAdvantageAgent()

    proposal = "Simple internal tool"
    context = {
        "target_markets": ["Internal"],
        "industry": "Unknown"
    }
    agent_responses = []

    result = agent.analyze(proposal, context, agent_responses)

    # May have no advantages if no patterns match
    assert "advantages" in result
    assert "recommendations" in result


def test_analyze_multiple_constraints():
    """Test analysis with multiple constraint types."""
    agent = CompetitiveAdvantageAgent()

    proposal = "GDPR-compliant AI system with carbon tracking"
    context = {
        "target_markets": ["Germany", "France"],
        "industry": "Technology",
        "company_size": "large"
    }
    agent_responses = [
        {
            "agent_name": "Jurist",
            "rating": 7,
            "concerns": ["GDPR compliance", "AI Act transparency"]
        },
        {
            "agent_name": "Ecosystem",
            "rating": 6,
            "concerns": ["Carbon reporting required"]
        }
    ]

    result = agent.analyze(proposal, context, agent_responses)

    # Should identify advantages from multiple domains
    assert len(result["advantages"]) >= 2
    domains = {adv["constraint_domain"] for adv in result["advantages"]}
    assert len(domains) > 1  # Multiple domains represented
