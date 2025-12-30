"""Tests for Convergence Gates and Waiver Register."""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import date, datetime, timedelta

from src.consortium.models.waiver import Waiver, WaiverStatus, WaiverScope
from src.consortium.nodes.convergence_gates import ConvergenceGates


class TestWaiverModel:
    """Test waiver data model."""

    def test_waiver_creation(self):
        """Test creating a waiver."""
        waiver = Waiver(
            id="test-waiver-001",
            granted_by="Legal Counsel",
            granted_at=datetime.now(),
            reason="Emergency deployment to comply with regulatory deadline",
            promised_mitigation="Full compliance audit within 30 days",
            review_date=date.today() + timedelta(days=30),
            linked_red_lines=["GDPR_VIOLATION"],
            linked_agent_blocks=["jurist"]
        )

        assert waiver.id == "test-waiver-001"
        assert waiver.status == WaiverStatus.ACTIVE
        assert waiver.is_valid()

    def test_waiver_expiry(self):
        """Test waiver expiry checking."""
        waiver = Waiver(
            id="expired-waiver",
            granted_by="CISO",
            granted_at=datetime.now() - timedelta(days=10),
            reason="Test",
            promised_mitigation="Test",
            review_date=date.today(),
            expiry_date=date.today() - timedelta(days=1),  # Expired yesterday
            linked_red_lines=["DATA_SUBJECT_TO_FOREIGN_LAW"],
            linked_agent_blocks=["sovereign"]
        )

        assert not waiver.is_valid()

    def test_waiver_scope_matching(self):
        """Test waiver scope matching."""
        scope = WaiverScope(
            markets=["DE", "FR"],
            industries=["Financial Services"]
        )

        waiver = Waiver(
            id="scoped-waiver",
            granted_by="Legal",
            granted_at=datetime.now(),
            reason="Test",
            promised_mitigation="Test",
            review_date=date.today() + timedelta(days=30),
            scope=scope,
            linked_red_lines=["GDPR_VIOLATION"],
            linked_agent_blocks=["jurist"]
        )

        # Matching context
        context_match = {
            "target_markets": "DE, FR",
            "industry": "Financial Services"
        }
        assert waiver.applies_to("jurist", "GDPR_VIOLATION", context_match)

        # Non-matching context
        context_no_match = {
            "target_markets": "US",
            "industry": "Healthcare"
        }
        assert not waiver.applies_to("jurist", "GDPR_VIOLATION", context_no_match)

    def test_waiver_serialization(self):
        """Test waiver to/from dict."""
        waiver = Waiver(
            id="serialize-test",
            granted_by="Test",
            granted_at=datetime.now(),
            reason="Test",
            promised_mitigation="Test",
            review_date=date.today(),
            linked_red_lines=["TEST"],
            linked_agent_blocks=["test"]
        )

        # To dict
        data = waiver.to_dict()
        assert data["id"] == "serialize-test"

        # From dict
        waiver2 = Waiver.from_dict(data)
        assert waiver2.id == waiver.id


class TestConvergenceGates:
    """Test convergence gates logic."""

    def test_tier1_block_without_waiver(self):
        """Test Tier-1 BLOCK prevents convergence without waiver."""
        config = {
            "convergence": {
                "agent_tiers": {
                    "tier1": {
                        "agents": ["sovereign"],
                        "block_resolution": "REDESIGN_OR_WAIVER"
                    }
                },
                "waivers": {"persist_path": "data/waivers"}
            }
        }

        gates = ConvergenceGates(config)

        responses = {
            "sovereign": {"rating": "BLOCK", "reasoning": "Data sovereignty violation"},
            "economist": {"rating": "ACCEPT", "confidence": 0.8}
        }

        can_proceed, status = gates.check_convergence_gates(responses, {})

        assert not can_proceed
        assert status["gate_decision"] == "TIER1_BLOCK_NO_WAIVER"
        assert len(status["tier1_blocks"]) == 1
        assert status["tier1_blocks"][0]["agent_id"] == "sovereign"

    def test_tier1_block_with_waiver(self):
        """Test Tier-1 BLOCK can proceed with valid waiver."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create waiver
            waiver = Waiver(
                id="sovereignty-waiver",
                granted_by="CTO",
                granted_at=datetime.now(),
                reason="Migration to EU cloud provider scheduled Q2",
                promised_mitigation="Full migration by June 30",
                review_date=date.today() + timedelta(days=90),
                linked_red_lines=["DATA_SUBJECT_TO_FOREIGN_LAW"],
                linked_agent_blocks=["sovereign"]
            )

            # Save waiver
            waiver_dir = Path(tmpdir) / "waivers"
            waiver_dir.mkdir()
            with open(waiver_dir / "sovereignty-waiver.json", "w") as f:
                json.dump(waiver.to_dict(), f)

            config = {
                "convergence": {
                    "agent_tiers": {
                        "tier1": {
                            "agents": ["sovereign"],
                            "block_resolution": "REDESIGN_OR_WAIVER"
                        }
                    },
                    "waivers": {"persist_path": str(waiver_dir)}
                }
            }

            gates = ConvergenceGates(config)

            responses = {
                "sovereign": {"rating": "BLOCK", "reasoning": "Data sovereignty violation"},
                "economist": {"rating": "ACCEPT", "confidence": 0.8}
            }

            can_proceed, status = gates.check_convergence_gates(responses, {})

            assert can_proceed
            assert status["gate_decision"] == "GATES_PASSED"
            assert len(status["waivers_applied"]) == 1
            assert status["waivers_applied"][0]["agent_id"] == "sovereign"

    def test_philosopher_block_requires_waiver(self):
        """Test Philosopher BLOCK triggers values escalation."""
        config = {
            "convergence": {
                "agent_tiers": {
                    "values_escalation": {
                        "agents": ["philosopher"],
                        "block_resolution": "ESCALATE_VALUES_REPORT"
                    }
                },
                "waivers": {"persist_path": "data/waivers"}
            }
        }

        gates = ConvergenceGates(config)

        responses = {
            "philosopher": {"rating": "BLOCK", "reasoning": "Dark patterns detected"},
            "economist": {"rating": "ACCEPT", "confidence": 0.8}
        }

        can_proceed, status = gates.check_convergence_gates(responses, {})

        assert not can_proceed
        assert status["gate_decision"] == "VALUES_ESCALATION_REQUIRED"
        assert status.get("requires_values_report") is True
        assert len(status["philosopher_blocks"]) == 1

    def test_tier2_block_allows_proceed(self):
        """Test Tier-2 BLOCK allows proceeding with tradeoff docs."""
        config = {
            "convergence": {
                "agent_tiers": {
                    "tier2": {
                        "agents": ["economist"],
                        "block_resolution": "REDESIGN_OR_EXPLICIT_TRADEOFF"
                    }
                },
                "waivers": {"persist_path": "data/waivers"}
            }
        }

        gates = ConvergenceGates(config)

        responses = {
            "economist": {"rating": "BLOCK", "reasoning": "High cost"},
            "architect": {"rating": "ACCEPT", "confidence": 0.8}
        }

        can_proceed, status = gates.check_convergence_gates(responses, {})

        # Tier-2 blocks don't prevent convergence (require tradeoff docs in synthesis)
        assert can_proceed
        assert len(status["tier2_blocks"]) == 1

    def test_tier3_block_is_advisory(self):
        """Test Tier-3 BLOCK is advisory only."""
        config = {
            "convergence": {
                "agent_tiers": {
                    "tier3": {
                        "agents": ["ethnographer"],
                        "block_resolution": "DOCUMENT_AND_PROCEED"
                    }
                },
                "waivers": {"persist_path": "data/waivers"}
            }
        }

        gates = ConvergenceGates(config)

        responses = {
            "ethnographer": {"rating": "BLOCK", "reasoning": "Cultural mismatch"},
            "economist": {"rating": "ACCEPT", "confidence": 0.8}
        }

        can_proceed, status = gates.check_convergence_gates(responses, {})

        assert can_proceed
        assert len(status["tier3_blocks"]) == 1
        assert status["gate_decision"] == "GATES_PASSED"

    def test_multiple_tiers(self):
        """Test handling multiple tier blocks simultaneously."""
        config = {
            "convergence": {
                "agent_tiers": {
                    "tier1": {
                        "agents": ["sovereign", "jurist"],
                        "block_resolution": "REDESIGN_OR_WAIVER"
                    },
                    "tier2": {
                        "agents": ["economist"],
                        "block_resolution": "REDESIGN_OR_EXPLICIT_TRADEOFF"
                    },
                    "tier3": {
                        "agents": ["ethnographer"],
                        "block_resolution": "DOCUMENT_AND_PROCEED"
                    }
                },
                "waivers": {"persist_path": "data/waivers"}
            }
        }

        gates = ConvergenceGates(config)

        responses = {
            "sovereign": {"rating": "BLOCK", "reasoning": "Sovereignty issue"},
            "jurist": {"rating": "BLOCK", "reasoning": "GDPR violation"},
            "economist": {"rating": "BLOCK", "reasoning": "Too expensive"},
            "ethnographer": {"rating": "BLOCK", "reasoning": "Cultural issue"}
        }

        can_proceed, status = gates.check_convergence_gates(responses, {})

        # Should fail due to tier1 blocks
        assert not can_proceed
        assert len(status["tier1_blocks"]) == 2
        assert len(status["tier2_blocks"]) == 1
        assert len(status["tier3_blocks"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
