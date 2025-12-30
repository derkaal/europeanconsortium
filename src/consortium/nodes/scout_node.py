"""
Scout node - upstream research before debate begins.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def create_scout_node(search_tool=None):
    """
    Factory function to create scout node with search tool.

    Args:
        search_tool: Web search tool (Tavily, SerpAPI, etc.)

    Returns:
        Scout node function for LangGraph
    """
    # Import here to avoid circular dependencies
    from agents.scout import ScoutAgent

    scout = ScoutAgent(search_tool=search_tool)

    async def scout_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute scout research and add briefing to state.

        This node should run BEFORE the router node.
        """
        query = state.get("query", "")
        context = state.get("context", {})

        if not query:
            logger.warning("Scout received empty query")
            return {"research_briefing": None}

        logger.info("Scout node executing research...")

        try:
            briefing = await scout.research(query, context)

            logger.info(f"Scout completed: {briefing.searches_executed} searches, "
                       f"{len(briefing.critical_updates)} critical updates")

            return {
                "research_briefing": briefing.model_dump(),
                "scout_completed": True
            }

        except Exception as e:
            logger.error(f"Scout research failed: {e}")
            return {
                "research_briefing": None,
                "scout_completed": False,
                "scout_error": str(e)
            }

    return scout_node


def inject_briefing_into_agent_context(
    agent_id: str,
    base_context: Dict[str, Any],
    briefing: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Inject relevant research findings into an agent's context.

    Args:
        agent_id: The agent receiving the briefing
        base_context: Original context
        briefing: Full research briefing

    Returns:
        Enhanced context with agent-specific research
    """
    if not briefing:
        return base_context

    enhanced = base_context.copy()

    # Add executive summary for all agents
    enhanced["research_summary"] = briefing.get("executive_summary", "")
    enhanced["research_timestamp"] = briefing.get("research_timestamp", "")

    # Add critical updates
    critical = briefing.get("critical_updates", [])
    relevant_critical = [
        u for u in critical
        if agent_id in u.get("affects_agents", [])
    ]
    if relevant_critical:
        enhanced["critical_updates"] = relevant_critical

    # Add agent-specific briefing
    agent_briefings = briefing.get("agent_briefings", {})
    if agent_id in agent_briefings:
        enhanced["research_findings"] = agent_briefings[agent_id].get("relevant_findings", [])
        enhanced["research_sources"] = agent_briefings[agent_id].get("sources", [])
        enhanced["research_confidence"] = agent_briefings[agent_id].get("confidence", 0.5)

    # Add information gaps
    enhanced["information_gaps"] = briefing.get("information_gaps", [])

    return enhanced
