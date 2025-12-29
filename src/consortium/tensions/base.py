"""Base class for tension protocols."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TensionProtocol(ABC):
    """Abstract base class for tension resolution protocols."""
    
    def __init__(self, config: Dict[str, Any]):
        self.protocol_id = config.get("protocol_id", "unknown")
        self.agent_a = config.get("agent_a")
        self.agent_b = config.get("agent_b")
        self.max_iterations = config.get("max_iterations", 3)
        self.trigger_conditions = config.get("trigger_conditions", {})
        self.priority = config.get("priority", 5)
    
    @abstractmethod
    def detect(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detect if this tension exists in the current state.
        
        Returns tension dict if detected, None otherwise.
        """
        pass
    
    @abstractmethod
    def resolve(
        self, state: Dict[str, Any], tension: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Attempt to resolve the tension.
        
        Returns updated state with resolution attempt.
        """
        pass
    
    def _get_agent_response(
        self, state: Dict[str, Any], agent_id: str
    ) -> Optional[Dict[str, Any]]:
        """Helper to get an agent's response from state."""
        return state.get("agent_responses", {}).get(agent_id)
    
    def _ratings_conflict(self, rating_a: str, rating_b: str) -> bool:
        """Check if two ratings represent a conflict."""
        blocking = {"BLOCK"}
        accepting = {"ACCEPT", "ENDORSE"}
        
        # BLOCK vs ACCEPT/ENDORSE is a conflict
        if rating_a in blocking and rating_b in accepting:
            return True
        if rating_b in blocking and rating_a in accepting:
            return True
        
        return False
