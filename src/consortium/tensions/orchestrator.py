"""Tension orchestrator - coordinates detection and resolution."""
from typing import Dict, Any, List
import logging

from .sovereign_economist import SovereignEconomistProtocol
from .ecosystem_architect import EcosystemArchitectProtocol
from .jurist_philosopher import JuristPhilosopherProtocol
from .operator_strategy import OperatorStrategyProtocol
from .futurist_all import FuturistAllProtocol

logger = logging.getLogger(__name__)


class TensionOrchestrator:
    """
    Orchestrates tension detection and resolution across all protocols.
    
    Responsibilities:
    - Detect all active tensions
    - Prioritize tensions for resolution
    - Coordinate resolution attempts
    - Track iteration counts
    - Handle escalations
    """
    
    def __init__(self):
        # Initialize all tension protocols
        self.protocols = [
            JuristPhilosopherProtocol(),  # Priority 0 - instant escalation
            SovereignEconomistProtocol(),  # Priority 1
            EcosystemArchitectProtocol(),  # Priority 2
            OperatorStrategyProtocol(),    # Priority 3
            FuturistAllProtocol(),         # Priority 4
        ]
    
    def detect_tensions(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect all active tensions in current state.
        
        Returns list of tension dicts sorted by priority.
        """
        tensions = []
        
        for protocol in self.protocols:
            tension = protocol.detect(state)
            if tension:
                tensions.append(tension)
                logger.info(f"Detected tension: {tension['protocol_id']}")
        
        # Sort by priority (lower = higher priority)
        tensions.sort(key=lambda t: t.get("priority", 99))
        
        return tensions
    
    def resolve_next_tension(
        self, state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve the highest priority active tension.
        
        Returns updated state after resolution attempt.
        """
        active_tensions = state.get("active_tensions", [])
        
        if not active_tensions:
            logger.info("No active tensions to resolve")
            return state
        
        # Get highest priority tension
        tension = active_tensions[0]
        protocol_id = tension.get("protocol_id")
        
        # Find matching protocol
        protocol = self._get_protocol(protocol_id)
        
        if not protocol:
            logger.error(f"Unknown protocol: {protocol_id}")
            return state
        
        # Attempt resolution
        logger.info(f"Resolving tension: {protocol_id}")
        state = protocol.resolve(state, tension)
        
        # Update tension in state
        if tension.get("status") in ["escalated", "resolved"]:
            # Remove from active tensions
            state["active_tensions"] = [
                t for t in active_tensions
                if t["protocol_id"] != protocol_id
            ]
        else:
            # Update the tension in place
            state["active_tensions"][0] = tension
        
        return state
    
    def _get_protocol(self, protocol_id: str):
        """Get protocol by ID."""
        for protocol in self.protocols:
            if protocol.protocol_id == protocol_id:
                return protocol
        return None
    
    def get_escalated_tensions(
        self, state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get all tensions that have been escalated to human decision."""
        return [
            t for t in state.get("active_tensions", [])
            if t.get("status") == "escalated"
        ]
