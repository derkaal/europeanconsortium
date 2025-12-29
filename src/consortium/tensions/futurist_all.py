"""Futurist vs All Agents tension protocol."""
from typing import Dict, Any, Optional
from .base import TensionProtocol
import logging

logger = logging.getLogger(__name__)


class FuturistAllProtocol(TensionProtocol):
    """
    Handles tension between Futurist and all other agents.
    
    Trigger: Futurist identifies strategy fails in >50% of scenarios.
    Resolution: Scenario matrix evaluation, adaptation mechanisms.
    Max iterations: 3
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        default_config = {
            "protocol_id": "futurist_all",
            "agent_a": "futurist",
            "agent_b": "all",
            "max_iterations": 3,
            "priority": 4,
            "trigger_conditions": {
                "scenario_failure_threshold": 0.50
            }
        }
        super().__init__(config or default_config)
    
    def detect(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect Futurist concern about scenario robustness."""
        
        futurist_response = self._get_agent_response(state, "futurist")
        
        if not futurist_response:
            return None
        
        # Check if Futurist has concerns about future viability
        if futurist_response["rating"] in ["WARN", "BLOCK"]:
            reasoning = futurist_response.get("reasoning", "").lower()
            if any(kw in reasoning for kw in [
                "scenario", "future", "brittle", "fragile", "obsolete"
            ]):
                logger.info(f"Tension detected: {self.protocol_id}")
                return {
                    "protocol_id": self.protocol_id,
                    "agent_a": self.agent_a,
                    "agent_b": self.agent_b,
                    "priority": self.priority,
                    "trigger_reason": (
                        f"Futurist flags scenario concerns: "
                        f"{futurist_response['rating']}"
                    ),
                    "iteration_count": 0,
                    "max_iterations": self.max_iterations,
                    "status": "active"
                }
        
        return None
    
    def resolve(
        self, state: Dict[str, Any], tension: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Attempt resolution via scenario matrix analysis."""
        
        iteration = tension.get("iteration_count", 0) + 1
        
        if iteration >= self.max_iterations:
            tension["status"] = "escalated"
            tension["resolution"] = (
                "Escalated - requires strategic optionality analysis"
            )
            return state
        
        tension["iteration_count"] = iteration
        tension["status"] = "resolving"
        
        logger.info(
            f"{self.protocol_id}: Resolution iteration "
            f"{iteration}/{self.max_iterations}"
        )
        
        return state
