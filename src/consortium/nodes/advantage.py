"""Competitive Advantage Analysis node (Feature 6).

Runs after convergence to identify competitive advantages from constraints.
"""

import yaml
from pathlib import Path
from typing import Dict, Any

from src.consortium.state import ConsortiumState
from src.consortium.agents.advantage import CompetitiveAdvantageAgent


def load_advantage_config() -> Dict[str, Any]:
    """Load advantage agent configuration.

    Returns:
        Config dict
    """
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "agents" / "advantage.yaml"

    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    # Default config if file not found
    return {"enabled": True, "min_keyword_matches": 1}


def advantage_analysis_node(state: ConsortiumState) -> Dict[str, Any]:
    """Analyze competitive advantages from regulatory constraints.

    Runs after convergence to identify how constraints can become advantages.

    Args:
        state: Current consortium state

    Returns:
        State update with advantage analysis
    """
    config = load_advantage_config()

    # Check if enabled
    if not config.get("enabled", True):
        return {
            "advantage_analysis": {
                "enabled": False,
                "advantages": [],
                "opportunities": [],
                "recommendations": []
            }
        }

    # Initialize agent
    agent = CompetitiveAdvantageAgent(config=config)

    # Get proposal and context
    proposal = state.get("query", "")
    context = state.get("context", {})

    # Get agent responses (convert dict to list of response values)
    agent_responses_dict = state.get("agent_responses", {})
    if isinstance(agent_responses_dict, dict):
        agent_responses = list(agent_responses_dict.values())
    else:
        agent_responses = []

    # Analyze advantages
    analysis = agent.analyze(
        proposal=proposal,
        context=context,
        agent_responses=agent_responses
    )

    # Add metadata
    analysis["enabled"] = True
    analysis["agent_name"] = "Competitive Advantage Analyzer"

    return {"advantage_analysis": analysis}
