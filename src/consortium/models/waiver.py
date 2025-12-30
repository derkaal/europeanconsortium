"""
Waiver models for non-compensatory red line exceptions.

Waivers allow proceeding despite Tier-1 BLOCK ratings, but only with:
- Explicit authorization
- Documented justification
- Promised mitigation
- Time-bounded validity
- Scope restrictions
"""

from enum import Enum
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class WaiverStatus(str, Enum):
    """Waiver lifecycle status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"
    REVOKED = "revoked"


class WaiverScope(BaseModel):
    """Scope restrictions for waiver applicability."""
    markets: Optional[List[str]] = Field(default=None, description="Geographic markets (e.g., ['DE', 'FR'])")
    industries: Optional[List[str]] = Field(default=None, description="Industry sectors")
    company_sizes: Optional[List[str]] = Field(default=None, description="Company size categories")

    def matches(self, context: dict) -> bool:
        """Check if context matches waiver scope."""
        # If no scope restrictions, waiver applies everywhere
        if not self.markets and not self.industries and not self.company_sizes:
            return True

        # Check each dimension
        if self.markets:
            context_markets = context.get("target_markets", "")
            if isinstance(context_markets, str):
                context_markets = [m.strip() for m in context_markets.split(",")]
            if not any(m in self.markets for m in context_markets):
                return False

        if self.industries:
            context_industry = context.get("industry", "")
            if context_industry not in self.industries:
                return False

        if self.company_sizes:
            context_size = context.get("company_size", "")
            if context_size not in self.company_sizes:
                return False

        return True


class Waiver(BaseModel):
    """
    A waiver allows proceeding despite non-compensatory red lines.

    Waivers are **high-trust, high-stakes** exceptions and must:
    - Be explicitly granted by authorized party
    - Document clear justification
    - Promise specific mitigation
    - Have bounded validity (time + scope)
    - Link to specific red lines and agent BLOCKs
    """
    id: str = Field(description="Unique waiver ID")
    granted_by: str = Field(description="Who granted this waiver (e.g., 'CISO', 'Legal Counsel')")
    granted_at: datetime = Field(description="When waiver was granted")
    reason: str = Field(description="Why this waiver is necessary")
    promised_mitigation: str = Field(description="What will be done to address the risk")
    review_date: date = Field(description="When waiver must be reviewed")
    expiry_date: Optional[date] = Field(default=None, description="When waiver expires (None = manual review only)")
    scope: Optional[WaiverScope] = Field(default=None, description="Where waiver applies")
    linked_red_lines: List[str] = Field(description="Red line IDs this waiver addresses")
    linked_agent_blocks: List[str] = Field(description="Agent IDs whose BLOCKs are waived")
    status: WaiverStatus = Field(default=WaiverStatus.ACTIVE, description="Current waiver status")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = Field(default=None, description="Additional notes")

    def is_valid(self, check_date: Optional[date] = None) -> bool:
        """Check if waiver is currently valid."""
        if self.status != WaiverStatus.ACTIVE:
            return False

        check_date = check_date or date.today()

        if self.expiry_date and check_date > self.expiry_date:
            return False

        return True

    def applies_to(self, agent_id: str, red_line_id: Optional[str], context: dict) -> bool:
        """Check if waiver applies to this agent/red line/context."""
        if not self.is_valid():
            return False

        if agent_id not in self.linked_agent_blocks:
            return False

        if red_line_id and red_line_id not in self.linked_red_lines:
            return False

        if self.scope and not self.scope.matches(context):
            return False

        return True

    def to_dict(self) -> dict:
        """Convert to dict for serialization."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "Waiver":
        """Create from dict."""
        return cls(**data)
