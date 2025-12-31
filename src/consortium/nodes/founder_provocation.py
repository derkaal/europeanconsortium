"""Founder Provocation Node - Step 1 of Proposal-Critique-Transformation Cascade.

The Founder runs ALONE to generate a "Max Upside" aggressive proposal.
This node implements the "Provocation" phase where ambition leads, constraints follow.
"""

import logging
import sys
from typing import Dict, Any

logger = logging.getLogger(__name__)


def founder_provocation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Founder agent ALONE to generate aggressive "Max Upside" proposal.

    This is Step 1 of the cascade: The Provocation.

    The Founder's job is to:
    - Ignore constraints and focus on maximum market opportunity
    - Generate a visionary, ambitious proposal
    - Think "10X" not incremental improvements
    - Identify Feature Subsidies and regulatory arbitrage opportunities

    The output becomes the INPUT for the Breaker agents in Step 2.

    Args:
        state: Current consortium state with query and context

    Returns:
        Partial state update with:
        - draft_strategy: Founder's visionary proposal text
        - agent_responses: {"founder": <founder_response>}
    """

    if '.' not in sys.path:
        sys.path.insert(0, '.')

    try:
        from agents.founder import FounderAgent
        from src.consortium.config import ConfigLoader
    except ImportError as e:
        logger.error(f"Import failed in founder_provocation_node: {e}")
        return {
            "draft_strategy": "ERROR: Founder agent import failed",
            "agent_responses": {
                "founder": {
                    "rating": "WARN",
                    "confidence": 0,
                    "reasoning": f"Founder provocation failed: {e}"
                }
            }
        }

    logger.info("=== STEP 1: THE PROVOCATION ===")
    logger.info("Founder Agent generating 'Max Upside' aggressive proposal...")

    config_manager = ConfigLoader()

    try:
        # Load Founder configuration
        founder_config = config_manager.load_agent_config("founder")

        if hasattr(founder_config, 'model_dump'):
            founder_config = founder_config.model_dump()
        elif hasattr(founder_config, 'dict'):
            founder_config = founder_config.dict()

        # Initialize Founder agent
        founder = FounderAgent(founder_config)

        # Build enhanced state for Founder
        # Include Scout research if available
        enhanced_state = state.copy()

        # Inject research briefing into context if available
        research_briefing = state.get("research_briefing")
        if research_briefing:
            base_context = state.get("context", {})
            enhanced_context = base_context.copy()
            enhanced_context["scout_research"] = research_briefing
            enhanced_state["context"] = enhanced_context
            logger.info("Injected Scout research briefing into Founder context")

        # Add explicit instruction for "Max Upside" thinking
        original_query = state.get("query", "")
        enhanced_state["query"] = f"""
{original_query}

IMPORTANT: Your task is to generate a "Max Upside" proposal that:
1. Focuses on MAXIMUM market opportunity (not safe incremental improvements)
2. Identifies EU Feature Subsidies that can be captured
3. Finds regulatory arbitrage windows before incumbents adapt
4. Proposes aggressive competitive positioning

Ignore constraints for now - other agents will handle risk assessment.
Your job: Maximum ambition. Think 10X.
"""

        # Invoke Founder
        logger.info("Invoking Founder agent...")
        founder_response = founder.invoke(enhanced_state)

        # Handle response format
        if not isinstance(founder_response, dict):
            if hasattr(founder_response, 'to_dict'):
                founder_response_dict = founder_response.to_dict()
            else:
                founder_response_dict = {
                    "rating": "WARN",
                    "confidence": 50,
                    "reasoning": str(founder_response)
                }
        else:
            founder_response_dict = founder_response

        # Extract the draft strategy from Founder's reasoning
        draft_strategy = founder_response_dict.get("reasoning", "No strategy provided")

        rating = founder_response_dict.get("rating", "UNKNOWN")
        confidence = founder_response_dict.get("confidence", 0)

        logger.info(f"✓ Founder Provocation complete: {rating} ({confidence}%)")
        logger.info(f"Draft Strategy (preview): {draft_strategy[:200]}...")

        return {
            "draft_strategy": draft_strategy,
            "agent_responses": {
                "founder": founder_response_dict
            }
        }

    except Exception as e:
        logger.error(f"✗ Founder provocation failed: {e}")
        import traceback
        traceback.print_exc()

        return {
            "draft_strategy": f"ERROR: Founder provocation failed - {str(e)}",
            "agent_responses": {
                "founder": {
                    "rating": "WARN",
                    "confidence": 0,
                    "reasoning": f"Founder execution failed: {str(e)}"
                }
            }
        }
