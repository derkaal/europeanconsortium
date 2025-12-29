"""Router node - determines which agents to trigger.

COST OPTIMIZATION: Currently uses no LLM (ZERO-LLM = FREE)
If LLM-based routing is added later, use FAST tier (Gemini Flash - cheapest)
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route query to appropriate agents.

    Now includes all 10 agents across all tiers:
    - Big Three: Sovereign, Intelligence Sovereign, Economist, Jurist
    - Tier 1: Architect, Eco-System, Philosopher
    - Tier 4: Ethnographer, Technologist, Consumer Voice

    COST: $0 (no LLM calls - triggers all agents)
    If LLM routing added: Use tiered_llm_provider.get_tiered_provider() with task="router" (FAST tier)
    """

    # All agents for comprehensive analysis
    triggered_agents = [
        # Big Three (foundational)
        "sovereign",                # Data sovereignty
        "intelligence_sovereign",   # AI sovereignty
        "economist",                # Financial viability
        "jurist",                   # Legal compliance
        # Tier 1 (technical & values)
        "architect",                # Technical feasibility
        "ecosystem",                # Sustainability
        "philosopher",              # Ethics alignment
        # Tier 4 (specialized)
        "ethnographer",             # Cultural ergonomics
        "technologist",             # Operational security (CISO)
        "consumer_voice",           # Consumer protection & accessibility
    ]
    
    query = state.get("query", "")
    
    logger.info(f"Router: Query received - '{query[:50]}...'")
    logger.info(
        f"Router: Triggering {len(triggered_agents)} agents: "
        f"{triggered_agents}"
    )
    
    return {"triggered_agents": triggered_agents}
