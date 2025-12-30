"""Evidence Referee - Deterministic claim tracking and conflict detection.

Feature 3: Evidence Referee (deterministic)

Manages:
1. Claims registry (SQLite persistence)
2. Deterministic claim extraction from structured fields
3. Evidence grading based on source type
4. Conflict detection using deterministic heuristics
5. Provenance tracking

NON-NEGOTIABLE: v1 MUST be deterministic (no LLM extraction).
Claims extracted from structured fields only.
"""

import logging
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.evidence import (
    Claim,
    ClaimConflict,
    EvidenceGrade,
    ConflictSeverity,
    detect_conflict_simple
)

logger = logging.getLogger(__name__)


class EvidenceReferee:
    """Manages claim registry and conflict detection (deterministic).

    This is a ZERO-LLM implementation for v1. All extraction and grading
    is rule-based.
    """

    def __init__(self, persist_path: str = ".consortium/evidence_referee.db"):
        """Initialize Evidence Referee.

        Args:
            persist_path: Path to SQLite database for claims persistence
        """
        self.persist_path = Path(persist_path)
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self.conn = sqlite3.connect(str(self.persist_path))
        self.conn.row_factory = sqlite3.Row
        self._init_database()

        logger.info(f"Evidence Referee initialized (database: {persist_path})")

    def _init_database(self):
        """Initialize claims and conflicts tables."""
        cursor = self.conn.cursor()

        # Claims table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                source_type TEXT NOT NULL,
                evidence_grade TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                extracted_at TEXT NOT NULL,
                extracted_from_field TEXT NOT NULL,
                metadata TEXT,
                conflicts_with TEXT,
                conflict_severity TEXT NOT NULL
            )
        """)

        # Conflicts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conflicts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim1_id TEXT NOT NULL,
                claim2_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                reason TEXT NOT NULL,
                detected_at TEXT NOT NULL,
                FOREIGN KEY (claim1_id) REFERENCES claims(id),
                FOREIGN KEY (claim2_id) REFERENCES claims(id)
            )
        """)

        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_claims_agent
            ON claims(agent_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_claims_source
            ON claims(source)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conflicts_claims
            ON conflicts(claim1_id, claim2_id)
        """)

        self.conn.commit()

    def register_claim_from_field(
        self,
        field_name: str,
        field_value: str,
        source: str,
        source_type: str,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Claim:
        """Register a claim extracted from a structured field.

        This is the PRIMARY method for claim registration - deterministic
        extraction from structured fields (no LLM).

        Args:
            field_name: Name of structured field (e.g., "title", "summary")
            field_value: Value extracted from field
            source: Source identifier (URL, document ID, etc.)
            source_type: Type of source for evidence grading
            agent_id: Agent who submitted this claim
            metadata: Optional additional metadata

        Returns:
            Registered Claim with evidence grade and conflict detection
        """
        # Create claim from structured field
        claim = Claim.from_structured_field(
            field_name=field_name,
            field_value=field_value,
            source=source,
            source_type=source_type,
            agent_id=agent_id,
            metadata=metadata
        )

        # Check for conflicts with existing claims
        conflicts = self._detect_conflicts(claim)

        if conflicts:
            # Update claim with conflict information
            claim.conflicts_with = [c.claim2_id for c in conflicts]
            claim.conflict_severity = max(
                (c.severity for c in conflicts),
                default=ConflictSeverity.NONE
            )

            # Store conflicts
            for conflict in conflicts:
                self._store_conflict(conflict)

        # Store claim
        self._store_claim(claim)

        logger.info(
            f"Claim registered: {claim.id[:12]}... "
            f"(grade={claim.evidence_grade.value}, "
            f"conflicts={len(claim.conflicts_with)})"
        )

        return claim

    def register_claims_from_search_results(
        self,
        search_results: List[Dict[str, Any]],
        agent_id: str
    ) -> List[Claim]:
        """Register claims from Scout search results.

        Extracts claims from STRUCTURED FIELDS in search results:
        - title
        - snippet
        - URL (as source)

        Args:
            search_results: List of search result dicts from Scout
            agent_id: Agent who performed the search

        Returns:
            List of registered claims
        """
        claims = []

        for result in search_results:
            # Extract structured fields
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            url = result.get("url", "")
            source_type = result.get("source_type", "unknown")

            # Register claim from title
            if title:
                try:
                    claim_title = self.register_claim_from_field(
                        field_name="title",
                        field_value=title,
                        source=url,
                        source_type=source_type,
                        agent_id=agent_id,
                        metadata={"result_type": "search"}
                    )
                    claims.append(claim_title)
                except Exception as e:
                    logger.warning(f"Failed to register claim from title: {e}")

            # Register claim from snippet
            if snippet:
                try:
                    claim_snippet = self.register_claim_from_field(
                        field_name="snippet",
                        field_value=snippet,
                        source=url,
                        source_type=source_type,
                        agent_id=agent_id,
                        metadata={"result_type": "search"}
                    )
                    claims.append(claim_snippet)
                except Exception as e:
                    logger.warning(f"Failed to register claim from snippet: {e}")

        logger.info(f"Registered {len(claims)} claims from {len(search_results)} search results")

        return claims

    def _detect_conflicts(self, new_claim: Claim) -> List[ClaimConflict]:
        """Detect conflicts between new claim and existing claims.

        Uses deterministic heuristics (no LLM).

        Args:
            new_claim: Newly registered claim

        Returns:
            List of detected conflicts
        """
        conflicts = []

        # Get all existing claims from database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM claims")
        rows = cursor.fetchall()

        for row in rows:
            existing_claim = Claim.from_dict(dict(row))

            # Detect conflict using deterministic heuristics
            conflict = detect_conflict_simple(new_claim, existing_claim)

            if conflict:
                conflicts.append(conflict)

        return conflicts

    def _store_claim(self, claim: Claim):
        """Store claim in database."""
        cursor = self.conn.cursor()

        claim_dict = claim.to_dict()

        cursor.execute("""
            INSERT OR REPLACE INTO claims
            (id, content, source, source_type, evidence_grade, agent_id,
             extracted_at, extracted_from_field, metadata, conflicts_with,
             conflict_severity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            claim_dict["id"],
            claim_dict["content"],
            claim_dict["source"],
            claim_dict["source_type"],
            claim_dict["evidence_grade"],
            claim_dict["agent_id"],
            claim_dict["extracted_at"],
            claim_dict["extracted_from_field"],
            claim_dict["metadata"],
            claim_dict["conflicts_with"],
            claim_dict["conflict_severity"]
        ))

        self.conn.commit()

    def _store_conflict(self, conflict: ClaimConflict):
        """Store conflict in database."""
        cursor = self.conn.cursor()

        conflict_dict = conflict.to_dict()

        cursor.execute("""
            INSERT INTO conflicts
            (claim1_id, claim2_id, severity, reason, detected_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            conflict_dict["claim1_id"],
            conflict_dict["claim2_id"],
            conflict_dict["severity"],
            conflict_dict["reason"],
            conflict_dict["detected_at"]
        ))

        self.conn.commit()

    def get_claims_by_agent(self, agent_id: str) -> List[Claim]:
        """Get all claims submitted by a specific agent.

        Args:
            agent_id: Agent identifier

        Returns:
            List of claims
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM claims WHERE agent_id = ?", (agent_id,))
        rows = cursor.fetchall()

        return [Claim.from_dict(dict(row)) for row in rows]

    def get_claims_by_source(self, source: str) -> List[Claim]:
        """Get all claims from a specific source.

        Args:
            source: Source identifier

        Returns:
            List of claims
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM claims WHERE source = ?", (source,))
        rows = cursor.fetchall()

        return [Claim.from_dict(dict(row)) for row in rows]

    def get_conflicting_claims(self) -> List[Claim]:
        """Get all claims that have conflicts.

        Returns:
            List of claims with conflicts
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM claims
            WHERE conflict_severity != 'NONE'
            ORDER BY conflict_severity DESC
        """)
        rows = cursor.fetchall()

        return [Claim.from_dict(dict(row)) for row in rows]

    def get_conflicts(self) -> List[ClaimConflict]:
        """Get all detected conflicts.

        Returns:
            List of claim conflicts
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM conflicts ORDER BY detected_at DESC")
        rows = cursor.fetchall()

        conflicts = []
        for row in rows:
            row_dict = dict(row)
            conflicts.append(ClaimConflict(
                claim1_id=row_dict["claim1_id"],
                claim2_id=row_dict["claim2_id"],
                severity=ConflictSeverity(row_dict["severity"]),
                reason=row_dict["reason"],
                detected_at=datetime.fromisoformat(row_dict["detected_at"])
            ))

        return conflicts

    def generate_evidence_report(self) -> Dict[str, Any]:
        """Generate evidence quality and conflict report.

        Returns:
            Report dict with evidence statistics and conflicts
        """
        cursor = self.conn.cursor()

        # Count claims by evidence grade
        cursor.execute("""
            SELECT evidence_grade, COUNT(*) as count
            FROM claims
            GROUP BY evidence_grade
        """)
        grade_counts = {row["evidence_grade"]: row["count"] for row in cursor.fetchall()}

        # Count conflicts by severity
        cursor.execute("""
            SELECT severity, COUNT(*) as count
            FROM conflicts
            GROUP BY severity
        """)
        conflict_counts = {row["severity"]: row["count"] for row in cursor.fetchall()}

        # Get conflicting claims
        conflicting_claims = self.get_conflicting_claims()

        # Total claims
        cursor.execute("SELECT COUNT(*) as count FROM claims")
        total_claims = cursor.fetchone()["count"]

        report = {
            "total_claims": total_claims,
            "evidence_quality": {
                "primary": grade_counts.get("PRIMARY", 0),
                "secondary": grade_counts.get("SECONDARY", 0),
                "tertiary": grade_counts.get("TERTIARY", 0),
                "unknown": grade_counts.get("UNKNOWN", 0)
            },
            "conflicts_detected": {
                "critical": conflict_counts.get("CRITICAL", 0),
                "moderate": conflict_counts.get("MODERATE", 0),
                "minor": conflict_counts.get("MINOR", 0),
                "total": sum(conflict_counts.values())
            },
            "conflicting_claims_count": len(conflicting_claims),
            "conflicting_claims": [
                {
                    "id": claim.id[:12] + "...",
                    "content": claim.content[:100] + "..." if len(claim.content) > 100 else claim.content,
                    "source": claim.source,
                    "evidence_grade": claim.evidence_grade.value,
                    "conflict_severity": claim.conflict_severity.value,
                    "conflicts_with_count": len(claim.conflicts_with)
                }
                for claim in conflicting_claims[:10]  # Show top 10
            ]
        }

        return report

    def close(self):
        """Close database connection."""
        self.conn.close()
        logger.info("Evidence Referee database closed")
