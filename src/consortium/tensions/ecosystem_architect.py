"""Eco-System vs Architect tension protocol."""
from typing import Dict, Any, Optional
from .base import TensionProtocol
import logging

logger = logging.getLogger(__name__)


class EcosystemArchitectProtocol(TensionProtocol):
    """
    Handles tension between Eco-System and Architect.
    
    Trigger: Architect compute-intensive AND Eco-System SCI >100%.
    Max iterations: 3
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        default_config = {
            "protocol_id": "ecosystem_architect",
            "agent_a": "ecosystem",
            "agent_b": "architect",
            "max_iterations": 3,
            "priority": 2,
            "trigger_conditions": {
                "sci_degradation_threshold": 1.0,
                "rating_conflict": True
            }
        }
        super().__init__(config or default_config)
    
    def detect(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect Eco-System vs Architect tension."""
        
        ecosystem_response = self._get_agent_response(state, "ecosystem")
        architect_response = self._get_agent_response(state, "architect")
        
        if not ecosystem_response or not architect_response:
            return None
        
        if self._ratings_conflict(
            ecosystem_response["rating"], architect_response["rating"]
        ):
            logger.info(f"Tension detected: {self.protocol_id}")
            return {
                "protocol_id": self.protocol_id,
                "agent_a": self.agent_a,
                "agent_b": self.agent_b,
                "priority": self.priority,
                "trigger_reason": (
                    f"Rating conflict: Ecosystem="
                    f"{ecosystem_response['rating']}, "
                    f"Architect={architect_response['rating']}"
                ),
                "iteration_count": 0,
                "max_iterations": self.max_iterations,
                "status": "active"
            }
        
        return None
    
    def resolve(
        self, state: Dict[str, Any], tension: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Attempt resolution via carbon mitigation strategies."""
        
        iteration = tension.get("iteration_count", 0) + 1
        
        if iteration >= self.max_iterations:
            tension["status"] = "escalated"
            tension["resolution"] = (
                "Escalated - requires Economist justification"
            )
            return state
        
        tension["iteration_count"] = iteration
        tension["status"] = "resolving"
        
        logger.info(
            f"{self.protocol_id}: Resolution iteration "
            f"{iteration}/{self.max_iterations}"
        )
        
        return state
