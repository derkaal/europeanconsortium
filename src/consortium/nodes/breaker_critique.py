"""Breaker Critique Node - Step 2 of Proposal-Critique-Transformation Cascade.

All constraint agents ("The Breakers") run in parallel to critique the Founder's proposal.
This node implements the "Attack" phase where constraints surface.
"""

import logging
import sys
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def breaker_critique_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute all constraint agents in parallel to critique Founder's proposal.

    This is Step 2 of the cascade: The Attack.

    The Breaker agents' job is to:
    - Attack the Founder's proposal (NOT the original user query)
    - Surface all constraints: legal, economic, technical, ethical, etc.
    - Provide BLOCK/WARN ratings with specific reasoning
    - Identify risks and blockers

    The Breakers are:
    - Jurist (legal compliance)
    - Sovereign (data sovereignty)
    - Economist (financial viability)
    - Technologist (operational security)
    - Eco-System (sustainability)
    - Philosopher (ethics)
    - Architect (technical feasibility)
    - Intelligence Sovereign (AI sovereignty)
    - Ethnographer (cultural ergonomics)
    - Consumer Voice (consumer protection)

    Args:
        state: Current consortium state with draft_strategy from Step 1

    Returns:
        Partial state update with:
        - agent_responses: Dict of all breaker responses
        - breaker_constraints: List of collected constraints/blockers
    """

    if '.' not in sys.path:
        sys.path.insert(0, '.')

    try:
        from agents.sovereign import SovereignAgent
        from agents.intelligence_sovereign import IntelligenceSovereignAgent
        from agents.economist import EconomistAgent
        from agents.jurist import JuristAgent
        from agents.architect import ArchitectAgent
        from agents.ecosystem import EcosystemAgent
        from agents.philosopher import PhilosopherAgent
        from agents.ethnographer import EthnographerAgent
        from agents.technologist import TechnologistAgent
        from agents.consumer_voice import ConsumerVoiceAgent
        from src.consortium.config import ConfigLoader
        from src.consortium.nodes.scout_node import inject_briefing_into_agent_context
    except ImportError as e:
        logger.error(f"Import failed in breaker_critique_node: {e}")
        return {
            "agent_responses": {},
            "breaker_constraints": [{
                "agent": "system",
                "rating": "BLOCK",
                "constraint": f"Breaker critique failed: {e}"
            }]
        }

    logger.info("=== STEP 2: THE ATTACK ===")
    logger.info("Breaker agents critiquing Founder's proposal...")

    # Get Founder's draft strategy
    draft_strategy = state.get("draft_strategy", "")

    if not draft_strategy or draft_strategy.startswith("ERROR"):
        logger.warning("No valid draft strategy from Founder - skipping breaker critique")
        return {
            "agent_responses": {},
            "breaker_constraints": [{
                "agent": "system",
                "rating": "WARN",
                "constraint": "No Founder proposal available to critique"
            }]
        }

    config_manager = ConfigLoader()
    research_briefing = state.get("research_briefing")

    # Registry of breaker agents (10 constraint agents)
    breaker_agents = {
        "jurist": JuristAgent,
        "sovereign": SovereignAgent,
        "economist": EconomistAgent,
        "technologist": TechnologistAgent,
        "ecosystem": EcosystemAgent,
        "philosopher": PhilosopherAgent,
        "architect": ArchitectAgent,
        "intelligence_sovereign": IntelligenceSovereignAgent,
        "ethnographer": EthnographerAgent,
        "consumer_voice": ConsumerVoiceAgent,
    }

    agent_responses = {}
    breaker_constraints = []

    # Build enhanced state for all breaker agents
    enhanced_state = state.copy()

    # Inject Founder's proposal into context
    base_context = state.get("context", {})
    enhanced_context = base_context.copy()
    enhanced_context["founder_proposal"] = draft_strategy

    # Inject Scout research if available
    if research_briefing:
        enhanced_context["scout_research"] = research_briefing

    enhanced_state["context"] = enhanced_context

    # Modify query to explicitly ask agents to critique the Founder's proposal
    original_query = state.get("query", "")
    enhanced_state["query"] = f"""
FOUNDER'S PROPOSAL:
---
{draft_strategy}
---

ORIGINAL USER QUERY:
{original_query}

YOUR TASK: Critique the Founder's proposal above.
Identify all constraints, risks, and blockers specific to this proposal.
Provide your rating (BLOCK/WARN/ACCEPT/ENDORSE) based on the proposal's viability.
"""

    logger.info(f"Executing {len(breaker_agents)} breaker agents in critique mode...")

    # Execute all breaker agents
    for agent_id, agent_class in breaker_agents.items():
        try:
            # Load agent configuration
            agent_config = config_manager.load_agent_config(agent_id)

            if hasattr(agent_config, 'model_dump'):
                agent_config = agent_config.model_dump()
            elif hasattr(agent_config, 'dict'):
                agent_config = agent_config.dict()

            # Initialize agent
            agent = agent_class(agent_config)

            # Further inject research briefing if available
            agent_state = enhanced_state.copy()
            if research_briefing:
                agent_context = inject_briefing_into_agent_context(
                    agent_id, enhanced_context, research_briefing
                )
                agent_state["context"] = agent_context

            # Invoke agent
            logger.info(f"Invoking breaker: {agent_id}...")
            response = agent.invoke(agent_state)

            # Handle response format
            if not isinstance(response, dict):
                if hasattr(response, 'to_dict'):
                    response = response.to_dict()
                else:
                    response = {
                        "rating": "WARN",
                        "confidence": 50,
                        "reasoning": str(response)
                    }

            # Ensure required fields
            if "rating" not in response:
                response["rating"] = "WARN"
            if "confidence" not in response:
                response["confidence"] = 50
            if "reasoning" not in response:
                response["reasoning"] = "No reasoning provided"

            agent_responses[agent_id] = response

            rating = response["rating"]
            confidence = response["confidence"]
            logger.info(f"✓ {agent_id}: {rating} ({confidence}%)")

            # Collect constraints (BLOCK and WARN ratings)
            if rating in ["BLOCK", "WARN"]:
                breaker_constraints.append({
                    "agent": agent_id,
                    "rating": rating,
                    "confidence": confidence,
                    "constraint": response["reasoning"]
                })

        except Exception as e:
            logger.error(f"✗ {agent_id} failed: {e}")
            import traceback
            traceback.print_exc()

            agent_responses[agent_id] = {
                "rating": "WARN",
                "confidence": 0,
                "reasoning": f"Agent execution failed: {str(e)}"
            }

            breaker_constraints.append({
                "agent": agent_id,
                "rating": "WARN",
                "confidence": 0,
                "constraint": f"Agent execution failed: {str(e)}"
            })

    logger.info(f"✓ Breaker Critique complete: {len(agent_responses)} responses, {len(breaker_constraints)} constraints identified")

    # Merge with existing agent_responses (preserve Founder response)
    existing_responses = state.get("agent_responses", {})
    merged_responses = existing_responses.copy()
    merged_responses.update(agent_responses)

    return {
        "agent_responses": merged_responses,
        "breaker_constraints": breaker_constraints
    }
