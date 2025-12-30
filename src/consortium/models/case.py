"""Case fingerprinting for deterministic retrieval.

Feature 5: Hybrid Memory Retrieval + Case Fingerprints

Implements deterministic case matching based on context metadata to improve
retrieval accuracy beyond pure vector similarity.
"""

import hashlib
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class CaseFingerprint(BaseModel):
    """Deterministic fingerprint for case matching.

    Fingerprints enable exact context matching before applying vector similarity,
    reducing false positives from semantic drift.
    """

    market_hash: str = Field(..., description="SHA256 hash of sorted markets")
    industry_hash: str = Field(..., description="SHA256 hash of sorted industries")
    company_size: str = Field(..., description="Standardized company size")
    regulatory_context: str = Field(..., description="Regulatory jurisdiction")
    query_category: str = Field(default="Strategy", description="Query category")

    @classmethod
    def from_context(cls, context: Dict[str, Any]) -> "CaseFingerprint":
        """Generate fingerprint from query context.

        Args:
            context: Query context dict with markets, industry, company_size, etc.

        Returns:
            CaseFingerprint instance
        """
        # Extract and normalize markets
        markets_raw = context.get("target_markets", [])
        if isinstance(markets_raw, str):
            markets_raw = [markets_raw]
        markets = sorted([m.lower().strip() for m in markets_raw if m])
        market_hash = hashlib.sha256("|".join(markets).encode()).hexdigest()[:16]

        # Extract and normalize industries
        industries_raw = context.get("industry", "")
        if isinstance(industries_raw, list):
            industries = sorted([i.lower().strip() for i in industries_raw if i])
        else:
            industries = [industries_raw.lower().strip()] if industries_raw else []
        industry_hash = hashlib.sha256("|".join(industries).encode()).hexdigest()[:16]

        # Standardize company size
        size = context.get("company_size", "unknown").lower()
        size_map = {
            "small": "Small",
            "medium": "Medium",
            "large": "Large",
            "enterprise": "Enterprise",
            "startup": "Small",
            "sme": "Medium",
            "corporation": "Large",
            "mid-market": "Medium",
            "smb": "Small"
        }
        company_size = size_map.get(size, "Unknown")

        # Determine regulatory context
        markets_set = set(m.lower() for m in markets)
        eu_markets = {"germany", "france", "spain", "italy", "netherlands", "poland",
                      "belgium", "austria", "sweden", "denmark", "finland", "portugal"}

        if markets_set & eu_markets:
            regulatory_context = "EU"
        elif "united states" in markets_set or "usa" in markets_set or "us" in markets_set:
            regulatory_context = "US"
        elif "united kingdom" in markets_set or "uk" in markets_set:
            regulatory_context = "UK"
        else:
            regulatory_context = "Global"

        # Determine query category (simple keyword-based for now)
        query_text = context.get("query", "").lower()
        if any(word in query_text for word in ["strategy", "approach", "plan"]):
            query_category = "Strategy"
        elif any(word in query_text for word in ["compliance", "regulation", "gdpr", "legal"]):
            query_category = "Compliance"
        elif any(word in query_text for word in ["technical", "architecture", "implementation"]):
            query_category = "Technical"
        elif any(word in query_text for word in ["cost", "pricing", "budget", "roi"]):
            query_category = "Financial"
        else:
            query_category = "Strategy"  # Default

        return cls(
            market_hash=market_hash,
            industry_hash=industry_hash,
            company_size=company_size,
            regulatory_context=regulatory_context,
            query_category=query_category
        )

    def to_metadata(self) -> Dict[str, Any]:
        """Convert to metadata dict for storage.

        Returns:
            Metadata dict compatible with vector DB storage
        """
        return {
            "market_hash": self.market_hash,
            "industry_hash": self.industry_hash,
            "company_size": self.company_size,
            "regulatory_context": self.regulatory_context,
            "query_category": self.query_category
        }

    def similarity_score(self, other: "CaseFingerprint") -> float:
        """Calculate similarity score with another fingerprint.

        Args:
            other: Another CaseFingerprint to compare with

        Returns:
            Similarity score between 0.0 and 1.0
        """
        score = 0.0

        # Market match (40% weight)
        if self.market_hash == other.market_hash:
            score += 0.4

        # Industry match (30% weight)
        if self.industry_hash == other.industry_hash:
            score += 0.3

        # Company size match (20% weight)
        if self.company_size == other.company_size:
            score += 0.2
        elif self._is_adjacent_size(self.company_size, other.company_size):
            score += 0.1  # Partial credit for adjacent sizes

        # Regulatory context match (10% weight)
        if self.regulatory_context == other.regulatory_context:
            score += 0.1

        return score

    @staticmethod
    def _is_adjacent_size(size1: str, size2: str) -> bool:
        """Check if two company sizes are adjacent.

        Args:
            size1: First company size
            size2: Second company size

        Returns:
            True if sizes are adjacent in the ladder
        """
        size_ladder = ["Small", "Medium", "Large", "Enterprise"]

        if size1 not in size_ladder or size2 not in size_ladder:
            return False

        idx1 = size_ladder.index(size1)
        idx2 = size_ladder.index(size2)

        return abs(idx1 - idx2) == 1


def get_adjacent_sizes(size: str) -> List[str]:
    """Get company size and adjacent sizes for filtering.

    Args:
        size: Target company size

    Returns:
        List of target size and adjacent sizes
    """
    size_ladder = ["Small", "Medium", "Large", "Enterprise"]

    if size not in size_ladder:
        return size_ladder  # Return all if unknown

    idx = size_ladder.index(size)

    # Include target size + adjacent
    adjacent = [size]
    if idx > 0:
        adjacent.append(size_ladder[idx - 1])
    if idx < len(size_ladder) - 1:
        adjacent.append(size_ladder[idx + 1])

    return adjacent
