"""Data models for consortium components."""

from .waiver import Waiver, WaiverStatus, WaiverScope
from .evidence import (
    Claim,
    ClaimConflict,
    EvidenceGrade,
    ConflictSeverity,
    grade_evidence_by_source_type,
    detect_conflict_simple
)

__all__ = [
    "Waiver",
    "WaiverStatus",
    "WaiverScope",
    "Claim",
    "ClaimConflict",
    "EvidenceGrade",
    "ConflictSeverity",
    "grade_evidence_by_source_type",
    "detect_conflict_simple"
]
