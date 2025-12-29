"""Agent executor node - invokes triggered agents with real LLMs."""
from typing import Dict, Any
import logging
import sys

logger = logging.getLogger(__name__)


def agent_executor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute all triggered agents with real LLM calls."""
    
    if '.' not in sys.path:
        sys.path.insert(0, '.')
    
    try:
        from agents.sovereign import SovereignAgent
        from agents.economist import EconomistAgent
        from agents.jurist import JuristAgent
        from agents.architect import ArchitectAgent
        from agents.ecosystem import EcosystemAgent
        from agents.philosopher import PhilosopherAgent
        from agents.ethnographer import EthnographerAgent
        from agents.technologist import TechnologistAgent
        from agents.consumer_voice import ConsumerVoiceAgent
        from src.consortium.config import ConfigManager
    except ImportError as e:
        logger.error(f"Import failed: {e}")
        return {
            "agent_responses": {
                agent_id: {
                    "rating": "WARN",
                    "confidence": 0,
                    "reasoning": f"Agent import failed: {e}"
                }
                for agent_id in state.get("triggered_agents", [])
            }
        }
    
    config_manager = ConfigManager()

    # Registry of all available agents (9 total across all tiers)
    available_agents = {
        # Big Three
        "sovereign": SovereignAgent,
        "economist": EconomistAgent,
        "jurist": JuristAgent,
        # Tier 1
        "architect": ArchitectAgent,
        "ecosystem": EcosystemAgent,
        "philosopher": PhilosopherAgent,
        # Tier 4
        "ethnographer": EthnographerAgent,
        "technologist": TechnologistAgent,
        "consumer_voice": ConsumerVoiceAgent,
    }
    
    agent_responses = {}
    triggered = state.get("triggered_agents", [])
    
    if not triggered:
        triggered = ["sovereign", "economist", "jurist"]
        logger.warning("No triggered agents, defaulting to Big Three")
    
    logger.info(
        f"Agent Executor: Processing {len(triggered)} agents: {triggered}"
    )
    
    for agent_id in triggered:
        if agent_id not in available_agents:
            logger.warning(f"Agent '{agent_id}' not in registry, skipping")
            continue
        
        try:
            agent_config = config_manager.load_agent_config(agent_id)
            
            if hasattr(agent_config, 'model_dump'):
                agent_config = agent_config.model_dump()
            elif hasattr(agent_config, 'dict'):
                agent_config = agent_config.dict()
            
            agent_class = available_agents[agent_id]
            agent = agent_class(agent_config)
            
            logger.info(f"Invoking {agent_id}...")
            response = agent.invoke(state)
            
            if not isinstance(response, dict):
                response = {
                    "rating": "WARN",
                    "confidence": 50,
                    "reasoning": str(response)
                }
            
            if "rating" not in response:
                response["rating"] = "WARN"
            if "confidence" not in response:
                response["confidence"] = 50
            if "reasoning" not in response:
                response["reasoning"] = "No reasoning provided"
            
            agent_responses[agent_id] = response
            rating = response['rating']
            conf = response['confidence']
            logger.info(f"✓ {agent_id}: {rating} ({conf}%)")
            
        except Exception as e:
            logger.error(f"✗ {agent_id} failed: {e}")
            import traceback
            traceback.print_exc()
            agent_responses[agent_id] = {
                "rating": "WARN",
                "confidence": 0,
                "reasoning": f"Agent execution failed: {str(e)}"
            }
    
    if not agent_responses:
        agent_responses = {
            "fallback": {
                "rating": "WARN",
                "confidence": 0,
                "reasoning": "All agents failed"
            }
        }
    
    logger.info(
        f"Agent Executor: Completed with {len(agent_responses)} responses"
    )
    return {"agent_responses": agent_responses}
