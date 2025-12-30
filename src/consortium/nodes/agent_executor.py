"""Agent executor node - invokes triggered agents with real LLMs."""
from typing import Dict, Any
import logging
import sys
import os

logger = logging.getLogger(__name__)


def agent_executor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute all triggered agents with real LLM calls.

    Process:
    1. Retrieve similar historical cases from memory (if available)
    2. Execute all triggered agents in parallel with historical context
    3. Return agent responses and memory metadata
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
        from agents.founder import FounderAgent
        from agents.alchemist import AlchemistAgent
        from src.consortium.config import ConfigLoader
        from src.consortium.memory import get_memory_manager
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

    config_manager = ConfigLoader()

    # =========================================================================
    # MEMORY RETRIEVAL - Retrieve similar historical cases before agent execution
    # =========================================================================

    query = state.get("query", "")
    context = state.get("context", {})
    memory_retrievals = []
    retrieval_metadata = None

    # Only attempt memory retrieval if OpenAI API key is available
    if os.getenv("OPENAI_API_KEY"):
        try:
            logger.info("Retrieving similar historical cases from memory...")
            memory_manager = get_memory_manager()

            # Retrieve top 3 similar cases with quality threshold >= 3.5
            retrieval_result = memory_manager.retrieve_similar_cases(
                query=query,
                top_k=3,
                min_similarity=0.7,
                min_quality_score=3.5
            )

            memory_retrievals = retrieval_result.get("cases", [])
            retrieval_metadata = retrieval_result.get("retrieval_metadata", {})

            # Log retrieval results
            if retrieval_metadata.get("cold_start", True):
                logger.info("Cold start: No similar historical cases found (system will proceed without memory context)")
            else:
                num_cases = len(memory_retrievals)
                logger.info(f"✓ Retrieved {num_cases} similar historical case(s) for context")
                for i, case in enumerate(memory_retrievals[:3], 1):
                    similarity = case.get("similarity_score", 0.0)
                    case_id = case.get("id", "unknown")[:8]
                    logger.info(f"  Case {i}: {case_id}... (similarity: {similarity:.2f})")

        except Exception as e:
            logger.warning(f"Memory retrieval failed (will proceed without historical context): {e}")
            # Graceful degradation: continue without memory
            memory_retrievals = []
            retrieval_metadata = {
                "cold_start": True,
                "error": str(e),
                "total_matches": 0,
                "quality_filtered": 0,
                "returned": 0
            }
    else:
        logger.info("Memory retrieval skipped (OPENAI_API_KEY not set)")
        retrieval_metadata = {
            "cold_start": True,
            "warning": "Memory retrieval requires OPENAI_API_KEY",
            "total_matches": 0,
            "quality_filtered": 0,
            "returned": 0
        }

    # Update state with memory retrievals
    state["memory_retrievals"] = memory_retrievals
    state["retrieval_metadata"] = retrieval_metadata

    # Registry of all available agents (12 total across all tiers)
    available_agents = {
        # Big Three (Foundational)
        "sovereign": SovereignAgent,
        "intelligence_sovereign": IntelligenceSovereignAgent,
        "economist": EconomistAgent,
        "jurist": JuristAgent,
        # Tier 1 (Technical & Values)
        "architect": ArchitectAgent,
        "ecosystem": EcosystemAgent,
        "philosopher": PhilosopherAgent,
        # Tier 4 (Specialized)
        "ethnographer": EthnographerAgent,
        "technologist": TechnologistAgent,
        "consumer_voice": ConsumerVoiceAgent,
        # Value Creation (NEW)
        "founder": FounderAgent,
        "alchemist": AlchemistAgent,
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
            
            # Handle both AgentResponse objects and dict responses
            if not isinstance(response, dict):
                # Check if it's an AgentResponse object
                if hasattr(response, 'to_dict'):
                    response = response.to_dict()
                else:
                    # Fallback for unknown types
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

    # Return agent responses along with memory retrievals
    return {
        "agent_responses": agent_responses,
        "memory_retrievals": memory_retrievals,
        "retrieval_metadata": retrieval_metadata
    }
