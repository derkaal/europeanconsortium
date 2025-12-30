"""
Convergence Gates - Tier-based BLOCK resolution.

Implements non-compensatory red lines:
- Tier-1 BLOCKs cannot be averaged away
- Tier-2 BLOCKs require explicit tradeoff documentation
- Tier-3 BLOCKs are advisory
- Philosopher BLOCKs trigger Values Escalation Report
"""

import logging
import json
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ConvergenceGates:
    """
    Implements tier-based convergence gates and waiver checking.

    Prevents "voting out" non-compensatory constraints.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize convergence gates.

        Args:
            config: Convergence configuration (from config/convergence.yaml)
        """
        self.config = config or {}
        self.agent_tiers = self._parse_agent_tiers()
        self.red_lines = self._parse_red_lines()
        self.waivers = self._load_waivers()

    def _parse_agent_tiers(self) -> Dict[str, Dict[str, Any]]:
        """Parse agent tier configuration."""
        tier_config = self.config.get("convergence", {}).get("agent_tiers", {})

        # Flatten into agent_id -> tier mapping
        agent_to_tier = {}

        for tier_name, tier_info in tier_config.items():
            agents = tier_info.get("agents", [])
            for agent_id in agents:
                agent_to_tier[agent_id] = {
                    "tier": tier_name,
                    "resolution": tier_info.get("block_resolution"),
                    "description": tier_info.get("description")
                }

        return agent_to_tier

    def _parse_red_lines(self) -> Dict[str, Dict[str, Any]]:
        """Parse non-compensatory red lines."""
        red_lines = self.config.get("convergence", {}).get("non_compensatory_red_lines", [])
        return {rl["id"]: rl for rl in red_lines}

    def _load_waivers(self) -> List[Any]:
        """Load active waivers from persistence."""
        waivers = []
        waiver_path = Path(self.config.get("convergence", {}).get("waivers", {}).get("persist_path", "data/waivers"))

        if not waiver_path.exists():
            return waivers

        # Load all .json files from waiver directory
        for waiver_file in waiver_path.glob("*.json"):
            try:
                with open(waiver_file) as f:
                    data = json.load(f)
                    from src.consortium.models.waiver import Waiver
                    waiver = Waiver.from_dict(data)
                    if waiver.is_valid():
                        waivers.append(waiver)
                    else:
                        logger.info(f"Skipping invalid waiver: {waiver.id} (status={waiver.status})")
            except Exception as e:
                logger.warning(f"Failed to load waiver {waiver_file}: {e}")

        logger.info(f"Loaded {len(waivers)} active waivers")
        return waivers

    def check_convergence_gates(
        self,
        agent_responses: Dict[str, Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if convergence gates allow proceeding.

        Returns (can_proceed, gate_status)

        gate_status includes:
        - tier1_blocks: List of Tier-1 BLOCKs
        - tier2_blocks: List of Tier-2 BLOCKs
        - tier3_blocks: List of Tier-3 BLOCKs
        - philosopher_blocks: List of Philosopher BLOCKs
        - waivers_applied: List of waivers that allowed proceeding
        - gate_decision: Overall decision
        """
        tier1_blocks = []
        tier2_blocks = []
        tier3_blocks = []
        philosopher_blocks = []
        waivers_applied = []

        # Categorize BLOCKs by tier
        for agent_id, response in agent_responses.items():
            if response.get("rating") != "BLOCK":
                continue

            tier_info = self.agent_tiers.get(agent_id, {})
            tier = tier_info.get("tier", "tier3")  # Default to tier3 if not configured

            block_info = {
                "agent_id": agent_id,
                "reasoning": response.get("reasoning", ""),
                "attack_vector": response.get("attack_vector"),
                "tier": tier,
                "resolution": tier_info.get("resolution")
            }

            if tier == "tier1":
                tier1_blocks.append(block_info)
            elif tier == "tier2":
                tier2_blocks.append(block_info)
            elif tier == "tier3":
                tier3_blocks.append(block_info)
            elif tier == "values_escalation":
                philosopher_blocks.append(block_info)

        # Check Tier-1 blocks (non-compensatory)
        if tier1_blocks:
            # Check for waivers
            unwaived_tier1 = []
            for block in tier1_blocks:
                has_waiver = self._check_waiver(block["agent_id"], None, context)
                if has_waiver:
                    waivers_applied.append({
                        "agent_id": block["agent_id"],
                        "waiver_id": has_waiver.id,
                        "reason": has_waiver.reason
                    })
                else:
                    unwaived_tier1.append(block)

            if unwaived_tier1:
                return False, {
                    "can_proceed": False,
                    "gate_decision": "TIER1_BLOCK_NO_WAIVER",
                    "tier1_blocks": tier1_blocks,
                    "unwaived_tier1_blocks": unwaived_tier1,
                    "tier2_blocks": tier2_blocks,
                    "tier3_blocks": tier3_blocks,
                    "philosopher_blocks": philosopher_blocks,
                    "waivers_applied": waivers_applied,
                    "message": (
                        f"Convergence blocked by {len(unwaived_tier1)} Tier-1 agent(s). "
                        f"These are non-compensatory constraints requiring redesign or waiver: "
                        f"{', '.join(b['agent_id'] for b in unwaived_tier1)}"
                    )
                }

        # Check Philosopher blocks (values escalation required)
        if philosopher_blocks:
            has_waiver = self._check_waiver("philosopher", None, context)
            if not has_waiver:
                return False, {
                    "can_proceed": False,
                    "gate_decision": "VALUES_ESCALATION_REQUIRED",
                    "tier1_blocks": tier1_blocks,
                    "tier2_blocks": tier2_blocks,
                    "tier3_blocks": tier3_blocks,
                    "philosopher_blocks": philosopher_blocks,
                    "waivers_applied": waivers_applied,
                    "requires_values_report": True,
                    "message": (
                        "Convergence blocked by Philosopher (ethical concern). "
                        "Requires Values Escalation Report and explicit waiver to proceed."
                    )
                }
            else:
                waivers_applied.append({
                    "agent_id": "philosopher",
                    "waiver_id": has_waiver.id,
                    "reason": has_waiver.reason
                })

        # Tier-2 blocks require explicit tradeoff documentation
        # (This is handled in synthesis - we note them but don't block)

        # All gates passed (or waived)
        return True, {
            "can_proceed": True,
            "gate_decision": "GATES_PASSED",
            "tier1_blocks": tier1_blocks,
            "tier2_blocks": tier2_blocks,
            "tier3_blocks": tier3_blocks,
            "philosopher_blocks": philosopher_blocks,
            "waivers_applied": waivers_applied,
            "message": (
                "Convergence gates passed. "
                f"Tier-1 blocks: {len(tier1_blocks)} (all waived), "
                f"Tier-2 blocks: {len(tier2_blocks)} (require tradeoff docs), "
                f"Tier-3 blocks: {len(tier3_blocks)} (advisory)."
            ) if (tier1_blocks or tier2_blocks or tier3_blocks) else "No blocking concerns."
        }

    def _check_waiver(
        self,
        agent_id: str,
        red_line_id: Optional[str],
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """Check if a valid waiver exists for this agent/red line/context."""
        for waiver in self.waivers:
            if waiver.applies_to(agent_id, red_line_id, context):
                return waiver
        return None


def load_convergence_config() -> Dict[str, Any]:
    """Load convergence configuration from YAML."""
    import yaml
    from pathlib import Path

    config_path = Path("config/convergence.yaml")
    if not config_path.exists():
        logger.warning("convergence.yaml not found, using defaults")
        return {}

    with open(config_path) as f:
        return yaml.safe_load(f)
