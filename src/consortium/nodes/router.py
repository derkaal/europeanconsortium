"""Router node - determines which agents to trigger."""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route query to appropriate agents.
    
    Now includes Tier 1 agents: Architect, Eco-System, Philosopher
    """
    
    # Core agents for comprehensive analysis
    triggered_agents = [
        "sovereign",    # Data sovereignty
        "economist",    # Financial viability
        "jurist",       # Legal compliance
        "architect",    # Technical feasibility
        "ecosystem",    # Sustainability
        "philosopher",  # Ethics alignment
    ]
    
    query = state.get("query", "")
    
    logger.info(f"Router: Query received - '{query[:50]}...'")
    logger.info(
        f"Router: Triggering {len(triggered_agents)} agents: "
        f"{triggered_agents}"
    )
    
    return {"triggered_agents": triggered_agents}
