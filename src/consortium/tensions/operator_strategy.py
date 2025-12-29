"""Operator vs Strategy Agents tension protocol."""
from typing import Dict, Any, Optional
from .base import TensionProtocol
import logging

logger = logging.getLogger(__name__)


class OperatorStrategyProtocol(TensionProtocol):
    """
    Handles tension between Operator and strategy agents.
    
    Trigger: Operator identifies timeline >2x longer than proposed.
    Resolution: Revise timeline, reduce scope, or increase resources.
    Max iterations: 2
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        default_config = {
            "protocol_id": "operator_strategy",
            "agent_a": "operator",
            "agent_b": "strategy",
            "max_iterations": 2,
            "priority": 3,
            "trigger_conditions": {
                "timeline_multiplier_threshold": 2.0
            }
        }
        super().__init__(config or default_config)
    
    def detect(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect Operator vs Strategy tension."""
        
        operator_response = self._get_agent_response(state, "operator")
        
        if not operator_response:
            return None
        
        # Check if Operator has WARN or BLOCK due to timeline concerns
        if operator_response["rating"] in ["WARN", "BLOCK"]:
            reasoning = operator_response.get("reasoning", "").lower()
            if any(kw in reasoning for kw in [
                "timeline", "resource", "capacity",
                "impossible", "unrealistic"
            ]):
                logger.info(f"Tension detected: {self.protocol_id}")
                return {
                    "protocol_id": self.protocol_id,
                    "agent_a": self.agent_a,
                    "agent_b": self.agent_b,
                    "priority": self.priority,
                    "trigger_reason": (
                        f"Operator flags implementation concerns: "
                        f"{operator_response['rating']}"
                    ),
                    "iteration_count": 0,
                    "max_iterations": self.max_iterations,
                    "status": "active"
                }
        
        return None
    
    def resolve(
        self, state: Dict[str, Any], tension: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Attempt resolution via timeline/scope revision."""
        
        iteration = tension.get("iteration_count", 0) + 1
        
        if iteration >= self.max_iterations:
            tension["status"] = "escalated"
            tension["resolution"] = (
                "Escalated - requires scope reduction or timeline extension"
            )
            return state
        
        tension["iteration_count"] = iteration
        tension["status"] = "resolving"
        
        logger.info(
            f"{self.protocol_id}: Resolution iteration "
            f"{iteration}/{self.max_iterations}"
        )
        
        return state
