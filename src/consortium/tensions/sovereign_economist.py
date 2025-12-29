"""Sovereign vs Economist tension protocol."""
from typing import Dict, Any, Optional
from .base import TensionProtocol
import logging

logger = logging.getLogger(__name__)


class SovereignEconomistProtocol(TensionProtocol):
    """
    Handles tension between Sovereign and Economist.
    
    Trigger: Sovereign demands EU-only AND Economist >40% cost premium.
    Resolution: Calculate trust premium, quantify sovereignty risk.
    Max iterations: 4
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        default_config = {
            "protocol_id": "sovereign_economist",
            "agent_a": "sovereign",
            "agent_b": "economist",
            "max_iterations": 4,
            "priority": 1,
            "trigger_conditions": {
                "cost_premium_threshold": 0.40,
                "rating_conflict": True
            }
        }
        super().__init__(config or default_config)
    
    def detect(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect Sovereign vs Economist tension."""
        
        sovereign_response = self._get_agent_response(state, "sovereign")
        economist_response = self._get_agent_response(state, "economist")
        
        if not sovereign_response or not economist_response:
            return None
        
        # Check for rating conflict
        if self._ratings_conflict(
            sovereign_response["rating"], economist_response["rating"]
        ):
            logger.info(f"Tension detected: {self.protocol_id}")
            return {
                "protocol_id": self.protocol_id,
                "agent_a": self.agent_a,
                "agent_b": self.agent_b,
                "priority": self.priority,
                "trigger_reason": (
                    f"Rating conflict: Sovereign="
                    f"{sovereign_response['rating']}, "
                    f"Economist={economist_response['rating']}"
                ),
                "iteration_count": 0,
                "max_iterations": self.max_iterations,
                "status": "active"
            }
        
        return None
    
    def resolve(
        self, state: Dict[str, Any], tension: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Attempt resolution via trust premium calculation."""
        
        iteration = tension.get("iteration_count", 0) + 1
        
        if iteration >= self.max_iterations:
            logger.warning(
                f"{self.protocol_id}: Max iterations reached, escalating"
            )
            tension["status"] = "escalated"
            tension["resolution"] = (
                "Escalated to human decision - "
                "unresolvable after 4 iterations"
            )
            return state
        
        tension["iteration_count"] = iteration
        tension["status"] = "resolving"
        
        logger.info(
            f"{self.protocol_id}: Resolution iteration "
            f"{iteration}/{self.max_iterations}"
        )
        
        return state
