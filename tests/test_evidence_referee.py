"""Tests for Evidence Referee (Feature 3: Deterministic claim tracking).

Tests:
1. Claim model and fingerprinting
2. Evidence grading by source type
3. Deterministic conflict detection
4. Claim registration from structured fields
5. Claims registry persistence
6. Evidence report generation
7. Integration with search results
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os

from src.consortium.models.evidence import (
    Claim,
    ClaimConflict,
    EvidenceGrade,
    ConflictSeverity,
    grade_evidence_by_source_type,
    detect_conflict_simple
)
from src.consortium.tools.evidence_referee import EvidenceReferee


# ==============================================================================
# Test: Claim Fingerprinting (Deterministic)
# ==============================================================================

def test_claim_fingerprint_deterministic():
    """Test that claim fingerprints are deterministic."""
    content = "The EU AI Act enters into force in 2024"
    source = "https://eur-lex.europa.eu/..."

    fp1 = Claim.compute_fingerprint(content, source)
    fp2 = Claim.compute_fingerprint(content, source)

    assert fp1 == fp2, "Fingerprints should be deterministic"


def test_claim_fingerprint_normalization():
    """Test that fingerprints normalize content properly."""
    source = "https://example.com"

    # Different whitespace, punctuation
    content1 = "The EU AI Act enters into force in 2024."
    content2 = "the eu ai act enters into force in 2024"
    content3 = "The   EU  AI  Act   enters into force in 2024!!!"

    fp1 = Claim.compute_fingerprint(content1, source)
    fp2 = Claim.compute_fingerprint(content2, source)
    fp3 = Claim.compute_fingerprint(content3, source)

    assert fp1 == fp2 == fp3, "Fingerprints should normalize whitespace and punctuation"


def test_claim_fingerprint_different_sources():
    """Test that different sources produce different fingerprints."""
    content = "Same content"

    fp1 = Claim.compute_fingerprint(content, "https://source1.com")
    fp2 = Claim.compute_fingerprint(content, "https://source2.com")

    assert fp1 != fp2, "Different sources should produce different fingerprints"


# ==============================================================================
# Test: Evidence Grading (Deterministic)
# ==============================================================================

def test_grade_primary_sources():
    """Test PRIMARY grade for official/regulatory sources."""
    primary_types = ["regulatory", "official", "filing", "law", "government", "eu_commission"]

    for source_type in primary_types:
        grade = grade_evidence_by_source_type(source_type)
        assert grade == EvidenceGrade.PRIMARY, f"{source_type} should be PRIMARY"


def test_grade_secondary_sources():
    """Test SECONDARY grade for news/analyst sources."""
    secondary_types = ["news", "analyst", "research", "report", "journal"]

    for source_type in secondary_types:
        grade = grade_evidence_by_source_type(source_type)
        assert grade == EvidenceGrade.SECONDARY, f"{source_type} should be SECONDARY"


def test_grade_tertiary_sources():
    """Test TERTIARY grade for blogs/social sources."""
    tertiary_types = ["blog", "social", "forum", "twitter", "reddit"]

    for source_type in tertiary_types:
        grade = grade_evidence_by_source_type(source_type)
        assert grade == EvidenceGrade.TERTIARY, f"{source_type} should be TERTIARY"


def test_grade_unknown_sources():
    """Test UNKNOWN grade for unclassified sources."""
    unknown_types = ["unknown", "something_random", "xyz"]

    for source_type in unknown_types:
        grade = grade_evidence_by_source_type(source_type)
        assert grade == EvidenceGrade.UNKNOWN, f"{source_type} should be UNKNOWN"


# ==============================================================================
# Test: Claim Creation from Structured Fields
# ==============================================================================

def test_claim_from_structured_field():
    """Test creating claim from structured field (deterministic)."""
    claim = Claim.from_structured_field(
        field_name="title",
        field_value="EU AI Act enters into force",
        source="https://eur-lex.europa.eu/...",
        source_type="regulatory",
        agent_id="scout",
        metadata={"result_type": "search"}
    )

    assert claim.content == "EU AI Act enters into force"
    assert claim.source_type == "regulatory"
    assert claim.evidence_grade == EvidenceGrade.PRIMARY
    assert claim.agent_id == "scout"
    assert claim.extracted_from_field == "title"
    assert claim.metadata["result_type"] == "search"
    assert len(claim.id) == 64  # SHA256 hex digest


def test_claim_serialization():
    """Test claim to/from dict serialization."""
    claim = Claim.from_structured_field(
        field_name="snippet",
        field_value="Test content",
        source="https://example.com",
        source_type="news",
        agent_id="scout"
    )

    # Serialize
    claim_dict = claim.to_dict()

    # Deserialize
    claim2 = Claim.from_dict(claim_dict)

    assert claim.id == claim2.id
    assert claim.content == claim2.content
    assert claim.evidence_grade == claim2.evidence_grade


# ==============================================================================
# Test: Conflict Detection (Deterministic)
# ==============================================================================

def test_no_conflict_same_source():
    """Test that claims from same source don't conflict."""
    source = "https://example.com"

    claim1 = Claim.from_structured_field(
        "title", "Content A", source, "news", "scout"
    )
    claim2 = Claim.from_structured_field(
        "snippet", "Content B", source, "news", "scout"
    )

    conflict = detect_conflict_simple(claim1, claim2)
    assert conflict is None, "Same source shouldn't produce conflict"


def test_conflict_negation_pattern():
    """Test conflict detection with negation patterns."""
    claim1 = Claim.from_structured_field(
        "title",
        "Company will launch new product in Q4",
        "https://source1.com",
        "news",
        "scout"
    )
    claim2 = Claim.from_structured_field(
        "title",
        "Company will not launch new product in Q4",
        "https://source2.com",
        "news",
        "scout"
    )

    conflict = detect_conflict_simple(claim1, claim2)

    assert conflict is not None, "Negation pattern should be detected"
    assert conflict.severity == ConflictSeverity.MODERATE
    assert "negation" in conflict.reason.lower()


def test_no_conflict_different_topics():
    """Test that claims on different topics don't conflict."""
    claim1 = Claim.from_structured_field(
        "title",
        "EU AI Act enters into force",
        "https://source1.com",
        "regulatory",
        "scout"
    )
    claim2 = Claim.from_structured_field(
        "title",
        "Mistral releases new model",
        "https://source2.com",
        "news",
        "scout"
    )

    conflict = detect_conflict_simple(claim1, claim2)
    assert conflict is None, "Different topics shouldn't conflict"


# ==============================================================================
# Test: Evidence Referee - Claims Registration
# ==============================================================================

@pytest.fixture
def evidence_referee():
    """Create temporary Evidence Referee for testing."""
    # Use temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name

    referee = EvidenceReferee(persist_path=db_path)

    yield referee

    # Cleanup
    referee.close()
    os.unlink(db_path)


def test_register_claim_from_field(evidence_referee):
    """Test registering a claim from structured field."""
    claim = evidence_referee.register_claim_from_field(
        field_name="title",
        field_value="EU AI Act compliance deadline approaching",
        source="https://europa.eu/...",
        source_type="official",
        agent_id="scout"
    )

    assert claim.evidence_grade == EvidenceGrade.PRIMARY
    assert len(claim.conflicts_with) == 0

    # Verify persistence
    claims = evidence_referee.get_claims_by_agent("scout")
    assert len(claims) == 1
    assert claims[0].id == claim.id


def test_register_conflicting_claims(evidence_referee):
    """Test that conflicting claims are detected and linked."""
    # Register first claim
    claim1 = evidence_referee.register_claim_from_field(
        field_name="title",
        field_value="Company will expand to European market",
        source="https://source1.com",
        source_type="news",
        agent_id="economist"
    )

    # Register conflicting claim
    claim2 = evidence_referee.register_claim_from_field(
        field_name="title",
        field_value="Company will not expand to European market",
        source="https://source2.com",
        source_type="news",
        agent_id="economist"
    )

    # Check conflicts detected
    assert len(claim2.conflicts_with) > 0, "Conflict should be detected"
    assert claim2.conflict_severity in [ConflictSeverity.MODERATE, ConflictSeverity.CRITICAL]

    # Verify conflicts table
    conflicts = evidence_referee.get_conflicts()
    assert len(conflicts) > 0


def test_register_claims_from_search_results(evidence_referee):
    """Test registering claims from search results (structured fields)."""
    search_results = [
        {
            "title": "EU GDPR enforcement increases",
            "snippet": "GDPR fines reach new high in 2024",
            "url": "https://gdpr-info.eu/...",
            "source_type": "regulatory"
        },
        {
            "title": "Mistral AI releases Mixtral 8x7B",
            "snippet": "New open-source LLM from European AI leader",
            "url": "https://mistral.ai/...",
            "source_type": "news"
        }
    ]

    claims = evidence_referee.register_claims_from_search_results(
        search_results, agent_id="scout"
    )

    # Should register claims from title AND snippet for each result
    assert len(claims) == 4  # 2 results × 2 fields (title, snippet)

    # Verify evidence grades
    regulatory_claims = [c for c in claims if c.source_type == "regulatory"]
    assert all(c.evidence_grade == EvidenceGrade.PRIMARY for c in regulatory_claims)

    news_claims = [c for c in claims if c.source_type == "news"]
    assert all(c.evidence_grade == EvidenceGrade.SECONDARY for c in news_claims)


# ==============================================================================
# Test: Evidence Referee - Queries
# ==============================================================================

def test_get_claims_by_agent(evidence_referee):
    """Test retrieving claims by agent."""
    # Register claims from different agents
    evidence_referee.register_claim_from_field(
        "title", "Scout finding 1", "https://s1.com", "news", "scout"
    )
    evidence_referee.register_claim_from_field(
        "title", "Scout finding 2", "https://s2.com", "news", "scout"
    )
    evidence_referee.register_claim_from_field(
        "title", "Economist finding", "https://s3.com", "analyst", "economist"
    )

    scout_claims = evidence_referee.get_claims_by_agent("scout")
    economist_claims = evidence_referee.get_claims_by_agent("economist")

    assert len(scout_claims) == 2
    assert len(economist_claims) == 1


def test_get_claims_by_source(evidence_referee):
    """Test retrieving claims by source."""
    source = "https://example.com"

    evidence_referee.register_claim_from_field(
        "title", "Title claim", source, "news", "scout"
    )
    evidence_referee.register_claim_from_field(
        "snippet", "Snippet claim", source, "news", "scout"
    )

    claims = evidence_referee.get_claims_by_source(source)
    assert len(claims) == 2


def test_get_conflicting_claims(evidence_referee):
    """Test retrieving only claims with conflicts."""
    # Non-conflicting claim
    evidence_referee.register_claim_from_field(
        "title", "Claim A", "https://s1.com", "news", "scout"
    )

    # Conflicting claims
    evidence_referee.register_claim_from_field(
        "title", "Product will launch in Q4", "https://s2.com", "news", "scout"
    )
    evidence_referee.register_claim_from_field(
        "title", "Product will not launch in Q4", "https://s3.com", "news", "scout"
    )

    conflicting = evidence_referee.get_conflicting_claims()

    # At least the conflicting pair should be flagged
    assert len(conflicting) >= 2


# ==============================================================================
# Test: Evidence Report Generation
# ==============================================================================

def test_evidence_report_generation(evidence_referee):
    """Test generating evidence quality and conflict report."""
    # Register variety of claims
    evidence_referee.register_claim_from_field(
        "title", "Regulatory update", "https://eur-lex.europa.eu/...", "regulatory", "jurist"
    )
    evidence_referee.register_claim_from_field(
        "title", "News article", "https://reuters.com/...", "news", "scout"
    )
    evidence_referee.register_claim_from_field(
        "title", "Blog post", "https://blog.example.com/...", "blog", "scout"
    )

    # Register conflicting claims
    evidence_referee.register_claim_from_field(
        "title", "Price will increase", "https://s1.com", "news", "economist"
    )
    evidence_referee.register_claim_from_field(
        "title", "Price will not increase", "https://s2.com", "news", "economist"
    )

    report = evidence_referee.generate_evidence_report()

    # Check report structure
    assert "total_claims" in report
    assert "evidence_quality" in report
    assert "conflicts_detected" in report

    # Check evidence quality breakdown
    assert report["evidence_quality"]["primary"] == 1  # regulatory
    assert report["evidence_quality"]["secondary"] == 3  # 2 news + conflicts
    assert report["evidence_quality"]["tertiary"] == 1  # blog

    # Check conflicts
    assert report["conflicts_detected"]["total"] > 0


def test_empty_evidence_report(evidence_referee):
    """Test evidence report when no claims registered."""
    report = evidence_referee.generate_evidence_report()

    assert report["total_claims"] == 0
    assert report["evidence_quality"]["primary"] == 0
    assert report["conflicts_detected"]["total"] == 0


# ==============================================================================
# Test: Integration Scenarios
# ==============================================================================

def test_full_workflow_scout_integration(evidence_referee):
    """Test full workflow: Scout searches → claims registered → conflicts detected → report."""

    # Simulate Scout search results
    search_results = [
        {
            "title": "EU AI Act officially enters into force",
            "snippet": "The comprehensive AI regulation is now active",
            "url": "https://eur-lex.europa.eu/ai-act",
            "source_type": "regulatory"
        },
        {
            "title": "Industry concerns about AI Act compliance",
            "snippet": "Companies struggle with new requirements",
            "url": "https://reuters.com/ai-act-concerns",
            "source_type": "news"
        },
        {
            "title": "AI Act not yet enforced for small companies",
            "snippet": "Enforcement delayed for SMEs",
            "url": "https://techcrunch.com/ai-act-delay",
            "source_type": "news"
        }
    ]

    # Register claims from search results
    claims = evidence_referee.register_claims_from_search_results(
        search_results, agent_id="scout"
    )

    # Should have title + snippet for each result = 6 claims
    assert len(claims) == 6

    # Generate report
    report = evidence_referee.generate_evidence_report()

    assert report["total_claims"] == 6
    assert report["evidence_quality"]["primary"] >= 2  # Regulatory source
    assert report["evidence_quality"]["secondary"] >= 4  # News sources

    # May have conflicts detected between "enters into force" vs "not yet enforced"
    # (Depends on heuristic sensitivity)
