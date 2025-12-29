"""
Utility functions for LangGraph nodes.
"""

import logging
from typing import Dict, List, Any
from ..state import ConsortiumState

logger = logging.getLogger(__name__)


def _load_agents(agent_ids: List[str]) -> List[Any]:
    """
    Load agent instances from configuration.
    
    Args:
        agent_ids: List of agent identifiers to load
        
    Returns:
        List of agent instances
        
    Note:
        This is a placeholder. In a full implementation, this would:
        1. Load agent configurations from config/agents/
        2. Initialize agent instances with their LLM providers
        3. Return ready-to-invoke agent objects
    """
    from ..config import load_agent_config
    
    agents = []
    for agent_id in agent_ids:
        try:
            config = load_agent_config(agent_id)
            # TODO: Initialize actual agent instance
            # For now, return a mock agent structure
            agents.append({
                "agent_id": agent_id,
                "config": config,
                "invoke": lambda state: _mock_agent_response(agent_id, state)
            })
        except Exception as e:
            logger.error(f"Failed to load agent {agent_id}: {e}")
            
    return agents


def _mock_agent_response(
    agent_id: str, state: ConsortiumState
) -> Dict[str, Any]:
    """
    Generate a mock agent response for testing.
    
    In production, this would be replaced by actual LLM invocation.
    """
    return {
        "rating": "ACCEPT",
        "confidence": 85,
        "reasoning": f"Mock response from {agent_id}",
        "concerns": [],
        "recommendations": [f"Recommendation from {agent_id}"]
    }


def _generate_recommendation(state: ConsortiumState) -> str:
    """
    Generate executive recommendation from agent responses.
    
    Args:
        state: Current consortium state
        
    Returns:
        Executive recommendation text (2-3 sentences)
    """
    query = state["query"]
    responses = state["agent_responses"]
    
    # Count ratings
    ratings = [r["rating"] for r in responses.values()]
    endorsements = ratings.count("ENDORSE")
    accepts = ratings.count("ACCEPT")
    warns = ratings.count("WARN")
    blocks = ratings.count("BLOCK")
    
    # Calculate average confidence
    avg_confidence = (
        sum(r["confidence"] for r in responses.values()) / len(responses)
    )
    
    # Generate recommendation based on consensus
    if blocks > 0:
        return (
            f"The consortium recommends AGAINST proceeding with "
            f"'{query}' due to {blocks} blocking concern(s). "
            f"Critical issues must be resolved before implementation "
            f"can be considered."
        )
    elif warns > 2:
        return (
            f"The consortium recommends CONDITIONAL APPROVAL for "
            f"'{query}' with {warns} warning(s) requiring mitigation. "
            f"Proceed with caution and address identified concerns "
            f"before full deployment."
        )
    elif (endorsements + accepts) / len(responses) >= 0.60:
        return (
            f"The consortium recommends PROCEEDING with '{query}'. "
            f"With {endorsements + accepts}/{len(responses)} positive "
            f"ratings and {avg_confidence:.0f}% average confidence, "
            f"the proposal demonstrates strong alignment with European "
            f"strategic objectives."
        )
    else:
        positive_pct = (endorsements + accepts) / len(responses) * 100
        return (
            f"The consortium recommends FURTHER ANALYSIS for '{query}'. "
            f"While no blocking concerns exist, insufficient consensus "
            f"({positive_pct:.0f}% positive) suggests additional "
            f"stakeholder engagement is needed."
        )


def _extract_action_items(state: ConsortiumState) -> List[Dict[str, Any]]:
    """
    Extract action items from agent responses.
    
    Args:
        state: Current consortium state
        
    Returns:
        List of action items with owner, priority, and description
    """
    action_items = []
    
    for agent_id, response in state["agent_responses"].items():
        # Extract recommendations as action items
        for idx, rec in enumerate(response.get("recommendations", [])):
            priority = (
                "high"
                if response["rating"] in ["BLOCK", "WARN"]
                else "medium"
            )
            action_items.append({
                "id": f"{agent_id}_{idx}",
                "owner": agent_id,
                "priority": priority,
                "description": rec,
                "status": "pending"
            })
            
        # Extract concerns as action items
        for idx, concern in enumerate(response.get("concerns", [])):
            priority = (
                "critical" if response["rating"] == "BLOCK" else "high"
            )
            action_items.append({
                "id": f"{agent_id}_concern_{idx}",
                "owner": agent_id,
                "priority": priority,
                "description": f"Address concern: {concern}",
                "status": "pending"
            })
    
    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    action_items.sort(key=lambda x: priority_order.get(x["priority"], 4))
    
    return action_items


def _format_decision_provenance(state: ConsortiumState) -> Dict[str, Any]:
    """
    Format decision provenance for audit trail.
    
    Args:
        state: Current consortium state
        
    Returns:
        Structured provenance information
    """
    return {
        "trace_id": state["trace_id"],
        "query": state["query"],
        "context": state["context"],
        "agents_engaged": state["triggered_agents"],
        "total_iterations": sum(state["iteration_counts"].values()),
        "tensions_detected": (
            len(state.get("resolved_tensions", []))
            + len(state.get("active_tensions", []))
        ),
        "tensions_resolved": [
            {
                "protocol_id": t["protocol_id"],
                "agents": t["agents"],
                "resolution": t.get("resolution", "unknown")
            }
            for t in state.get("resolved_tensions", [])
        ],
        "tensions_escalated": [
            {
                "protocol_id": t["protocol_id"],
                "agents": t["agents"],
                "reason": t.get("escalation_reason", "unresolvable")
            }
            for t in state.get("active_tensions", [])
            if t.get("status") == "escalated"
        ],
        "convergence_metrics": state.get("convergence_status", {}),
        "timestamp": state.get("timestamp"),
    }
