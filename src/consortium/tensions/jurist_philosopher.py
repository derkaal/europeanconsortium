"""Jurist vs Philosopher tension protocol."""
from typing import Dict, Any, Optional
from .base import TensionProtocol
import logging

logger = logging.getLogger(__name__)


class JuristPhilosopherProtocol(TensionProtocol):
    """
    Handles tension between Jurist and Philosopher.
    
    Trigger: Jurist ACCEPT BUT Philosopher BLOCK (ethical violation).
    Resolution: IMMEDIATE ESCALATION - values conflicts need human.
    Max iterations: 0 (instant escalation)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        default_config = {
            "protocol_id": "jurist_philosopher",
            "agent_a": "jurist",
            "agent_b": "philosopher",
            "max_iterations": 0,  # Instant escalation
            "priority": 0,  # Highest priority
            "trigger_conditions": {
                "legal_vs_ethical_conflict": True
            }
        }
        super().__init__(config or default_config)
    
    def detect(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect Jurist vs Philosopher tension."""
        
        jurist_response = self._get_agent_response(state, "jurist")
        philosopher_response = self._get_agent_response(
            state, "philosopher"
        )
        
        if not jurist_response or not philosopher_response:
            return None
        
        # Specific case: Legal ACCEPT but Ethical BLOCK
        if (jurist_response["rating"] in ["ACCEPT", "ENDORSE"] and
                philosopher_response["rating"] == "BLOCK"):
            logger.warning("CRITICAL: Legal vs Ethical conflict detected")
            return {
                "protocol_id": self.protocol_id,
                "agent_a": self.agent_a,
                "agent_b": self.agent_b,
                "priority": self.priority,
                "trigger_reason": (
                    "Legal compliance conflicts with ethical principles - "
                    "requires human judgment"
                ),
                "iteration_count": 0,
                "max_iterations": self.max_iterations,
                "status": "requires_escalation"
            }
        
        return None
    
    def resolve(
        self, state: Dict[str, Any], tension: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Immediate escalation - no automatic resolution."""
        
        tension["status"] = "escalated"
        tension["resolution"] = (
            "ESCALATED TO HUMAN: Legal vs Ethical conflict requires "
            "human judgment on values hierarchy"
        )
        
        logger.warning(f"{self.protocol_id}: Escalated to human decision")
        
        return state
