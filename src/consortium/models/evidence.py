"""Evidence models for deterministic claim tracking and grading.

Feature 3: Evidence Referee (deterministic)

Tracks claim provenance, grades evidence quality, and surfaces conflicts
using ONLY deterministic methods (no LLM extraction).
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import hashlib
import json


class EvidenceGrade(str, Enum):
    """Evidence quality grades based on source type."""
    PRIMARY = "PRIMARY"      # Official docs, regulatory filings, direct observation
    SECONDARY = "SECONDARY"  # News from reputable sources, analyst reports
    TERTIARY = "TERTIARY"    # Blogs, social media, unverified sources
    UNKNOWN = "UNKNOWN"      # Source type not classified


class ConflictSeverity(str, Enum):
    """Severity of conflicts between claims."""
    CRITICAL = "CRITICAL"    # Direct contradictions on core facts
    MODERATE = "MODERATE"    # Contradictions on details
    MINOR = "MINOR"          # Slight discrepancies
    NONE = "NONE"            # No conflict detected


class Claim(BaseModel):
    """A single verifiable claim with provenance and evidence grading.

    Claims are extracted from STRUCTURED FIELDS ONLY (deterministic).
    Never extracted from free text using LLMs.
    """
    id: str = Field(..., description="Unique claim ID (SHA256 fingerprint)")
    content: str = Field(..., description="The claim text")
    source: str = Field(..., description="Source identifier (URL, document ID, etc.)")
    source_type: str = Field(..., description="Type of source (regulatory, news, etc.)")
    evidence_grade: EvidenceGrade = Field(..., description="Quality grade of evidence")
    agent_id: str = Field(..., description="Agent who submitted this claim")
    extracted_at: datetime = Field(default_factory=datetime.now)
    extracted_from_field: str = Field(..., description="Structured field name claim came from")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    # Conflict tracking
    conflicts_with: List[str] = Field(
        default_factory=list,
        description="IDs of conflicting claims"
    )
    conflict_severity: ConflictSeverity = Field(
        default=ConflictSeverity.NONE,
        description="Severity of detected conflicts"
    )

    @staticmethod
    def compute_fingerprint(content: str, source: str) -> str:
        """Compute deterministic fingerprint for claim.

        Fingerprint = SHA256(normalized_content + source)

        This enables deterministic duplicate detection.

        Args:
            content: Claim text
            source: Source identifier

        Returns:
            SHA256 hex digest
        """
        # Normalize: lowercase, strip whitespace, remove punctuation
        normalized = content.lower().strip()
        normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
        normalized = ' '.join(normalized.split())  # Collapse whitespace

        # Combine with source
        fingerprint_data = f"{normalized}|{source}"

        return hashlib.sha256(fingerprint_data.encode()).hexdigest()

    @classmethod
    def from_structured_field(
        cls,
        field_name: str,
        field_value: str,
        source: str,
        source_type: str,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "Claim":
        """Create claim from structured field (deterministic extraction).

        Args:
            field_name: Name of structured field (e.g., "title", "summary")
            field_value: Value of the field
            source: Source identifier
            source_type: Type of source for evidence grading
            agent_id: Agent who submitted this claim
            metadata: Optional additional metadata

        Returns:
            Claim instance with evidence grade assigned
        """
        # Compute fingerprint
        claim_id = cls.compute_fingerprint(field_value, source)

        # Grade evidence based on source type
        evidence_grade = grade_evidence_by_source_type(source_type)

        return cls(
            id=claim_id,
            content=field_value,
            source=source,
            source_type=source_type,
            evidence_grade=evidence_grade,
            agent_id=agent_id,
            extracted_from_field=field_name,
            metadata=metadata or {}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "source_type": self.source_type,
            "evidence_grade": self.evidence_grade.value,
            "agent_id": self.agent_id,
            "extracted_at": self.extracted_at.isoformat(),
            "extracted_from_field": self.extracted_from_field,
            "metadata": json.dumps(self.metadata),
            "conflicts_with": json.dumps(self.conflicts_with),
            "conflict_severity": self.conflict_severity.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Claim":
        """Create from dictionary (for loading from storage)."""
        return cls(
            id=data["id"],
            content=data["content"],
            source=data["source"],
            source_type=data["source_type"],
            evidence_grade=EvidenceGrade(data["evidence_grade"]),
            agent_id=data["agent_id"],
            extracted_at=datetime.fromisoformat(data["extracted_at"]),
            extracted_from_field=data["extracted_from_field"],
            metadata=json.loads(data["metadata"]) if isinstance(data["metadata"], str) else data["metadata"],
            conflicts_with=json.loads(data["conflicts_with"]) if isinstance(data["conflicts_with"], str) else data["conflicts_with"],
            conflict_severity=ConflictSeverity(data["conflict_severity"])
        )


class ClaimConflict(BaseModel):
    """Detected conflict between claims."""
    claim1_id: str
    claim2_id: str
    severity: ConflictSeverity
    reason: str
    detected_at: datetime = Field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "claim1_id": self.claim1_id,
            "claim2_id": self.claim2_id,
            "severity": self.severity.value,
            "reason": self.reason,
            "detected_at": self.detected_at.isoformat()
        }


# ============================================================================
# Deterministic Evidence Grading
# ============================================================================

def grade_evidence_by_source_type(source_type: str) -> EvidenceGrade:
    """Grade evidence quality based on source type (deterministic).

    This is RULE-BASED grading - no LLM involved.

    Args:
        source_type: Type of source (from config or agent classification)

    Returns:
        EvidenceGrade enum value
    """
    # Normalize source type
    source_type_lower = source_type.lower()

    # PRIMARY: Official, regulatory, first-hand sources
    if any(keyword in source_type_lower for keyword in [
        "regulatory", "official", "filing", "statute", "law",
        "government", "directive", "eu_commission", "legal_document"
    ]):
        return EvidenceGrade.PRIMARY

    # SECONDARY: Reputable news, analyst reports, research
    if any(keyword in source_type_lower for keyword in [
        "news", "analyst", "research", "report", "journal",
        "publication", "media", "press_release"
    ]):
        return EvidenceGrade.SECONDARY

    # TERTIARY: Blogs, social, unverified
    if any(keyword in source_type_lower for keyword in [
        "blog", "social", "forum", "comment", "opinion",
        "reddit", "twitter", "linkedin_post"
    ]):
        return EvidenceGrade.TERTIARY

    # Default: UNKNOWN
    return EvidenceGrade.UNKNOWN


# ============================================================================
# Conflict Detection (Deterministic)
# ============================================================================

def detect_conflict_simple(claim1: Claim, claim2: Claim) -> Optional[ClaimConflict]:
    """Detect conflicts between claims using deterministic heuristics.

    This is a SIMPLE deterministic approach:
    - Same source, same field → likely duplicate (no conflict)
    - Different sources, similar content → potential conflict
    - Negation words detected → likely conflict

    For v1, we use simple heuristics. For v2, could add LLM-based
    semantic conflict detection as optional enhancement.

    Args:
        claim1: First claim
        claim2: Second claim

    Returns:
        ClaimConflict if conflict detected, None otherwise
    """
    # Skip if same claim
    if claim1.id == claim2.id:
        return None

    # Skip if same source (likely duplicate, not conflict)
    if claim1.source == claim2.source:
        return None

    # Normalize content for comparison
    content1_norm = claim1.content.lower().strip()
    content2_norm = claim2.content.lower().strip()

    # Check for negation patterns
    negation_words = ["not", "no", "never", "cannot", "won't", "doesn't", "isn't"]

    # Simple heuristic: if one claim has negation and the other doesn't,
    # and they share significant word overlap, likely conflict
    has_negation_1 = any(word in content1_norm for word in negation_words)
    has_negation_2 = any(word in content2_norm for word in negation_words)

    if has_negation_1 != has_negation_2:
        # Check word overlap
        words1 = set(content1_norm.split())
        words2 = set(content2_norm.split())
        overlap = words1 & words2

        if len(overlap) >= 3:  # At least 3 common words
            return ClaimConflict(
                claim1_id=claim1.id,
                claim2_id=claim2.id,
                severity=ConflictSeverity.MODERATE,
                reason="Negation pattern detected with significant word overlap"
            )

    # Could add more heuristics here:
    # - Numeric contradictions (different numbers for same metric)
    # - Date contradictions
    # - etc.

    return None
