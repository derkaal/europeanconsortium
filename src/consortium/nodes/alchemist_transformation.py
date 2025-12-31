"""Alchemist Transformation Node - Step 3 of Proposal-Critique-Transformation Cascade.

The Alchemist runs ALONE to convert constraints into competitive advantages.
This node implements the "Alchemy" phase where regulatory lead becomes competitive gold.
"""

import logging
import sys
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def alchemist_transformation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Alchemist agent to convert constraints into opportunities.

    This is Step 3 of the cascade: The Alchemy.

    The Alchemist's job is to:
    - Take the constraints identified by Breaker agents
    - Transmute them into competitive advantages
    - Convert "GDPR blocker" → "Privacy-First Premium Brand"
    - Convert "Carbon regulation" → "Green Market Leadership"
    - Reach Level 5 Alchemy (Regulation → Moat)

    Args:
        state: Current consortium state with breaker_constraints from Step 2

    Returns:
        Partial state update with:
        - agent_responses: Updated with alchemist response
        - reframed_opportunities: List of transmuted constraints
    """

    if '.' not in sys.path:
        sys.path.insert(0, '.')

    try:
        from agents.alchemist import AlchemistAgent
        from src.consortium.config import ConfigLoader
    except ImportError as e:
        logger.error(f"Import failed in alchemist_transformation_node: {e}")
        return {
            "reframed_opportunities": [{
                "constraint": "System Error",
                "opportunity": f"Alchemist import failed: {e}",
                "alchemy_level": 0
            }]
        }

    logger.info("=== STEP 3: THE ALCHEMY ===")
    logger.info("Alchemist Agent converting constraints into competitive advantages...")

    # Get constraints from Step 2
    breaker_constraints = state.get("breaker_constraints", [])

    if not breaker_constraints:
        logger.warning("No constraints to transmute - skipping alchemy")
        return {
            "reframed_opportunities": [{
                "constraint": "None",
                "opportunity": "No constraints detected - proposal is unconstrained",
                "alchemy_level": 5
            }]
        }

    config_manager = ConfigLoader()

    try:
        # Load Alchemist configuration
        alchemist_config = config_manager.load_agent_config("alchemist")

        if hasattr(alchemist_config, 'model_dump'):
            alchemist_config = alchemist_config.model_dump()
        elif hasattr(alchemist_config, 'dict'):
            alchemist_config = alchemist_config.dict()

        # Initialize Alchemist agent
        alchemist = AlchemistAgent(alchemist_config)

        # Build alchemy prompt
        constraint_text = _format_constraints_for_alchemy(breaker_constraints)

        alchemy_query = f"""
The following constraints were raised by the consortium's expert agents:

{constraint_text}

YOUR TASK: Regulatory Alchemy - Turn Lead into Gold

For each constraint above, perform transmutation:
1. Identify the regulatory raw material (what regulation/constraint is this?)
2. Determine current alchemy level (1=Cost, 2=Capability, 3=Credential, 4=Brand, 5=Moat)
3. Design transmutation path to Level 5 (Regulation → Competitive Moat)
4. Calculate Trust Premium (€ value of brand/trust advantage)
5. Estimate Moat Depth (competitor retrofit cost vs your native cost)

Output Format:
For each constraint, provide:
- Original Constraint: [agent name + constraint text]
- Transmutation: [how to convert this into advantage]
- Alchemy Level Achieved: [1-5]
- Trust Premium: [estimated € value or % markup]
- Moat Depth: [HIGH/MEDIUM/LOW based on competitor difficulty]
- Market Creation Potential: [any new markets this enables]

Remember: What incumbents see as cost, you see as moat.
"""

        alchemist_state = state.copy()
        alchemist_state["query"] = alchemy_query

        # Inject constraints into context
        enhanced_context = state.get("context", {}).copy()
        enhanced_context["constraints_to_transmute"] = breaker_constraints
        enhanced_context["constraint_count"] = len(breaker_constraints)
        alchemist_state["context"] = enhanced_context

        # Invoke Alchemist
        logger.info(f"Invoking Alchemist to transmute {len(breaker_constraints)} constraints...")
        alchemist_response = alchemist.invoke(alchemist_state)

        # Handle response format
        if not isinstance(alchemist_response, dict):
            if hasattr(alchemist_response, 'to_dict'):
                alchemist_response_dict = alchemist_response.to_dict()
            else:
                alchemist_response_dict = {
                    "rating": "WARN",
                    "confidence": 50,
                    "reasoning": str(alchemist_response)
                }
        else:
            alchemist_response_dict = alchemist_response

        # Extract reframed opportunities from Alchemist's reasoning
        reasoning = alchemist_response_dict.get("reasoning", "")
        reframed_opportunities = _parse_alchemist_opportunities(reasoning, breaker_constraints)

        rating = alchemist_response_dict.get("rating", "UNKNOWN")
        confidence = alchemist_response_dict.get("confidence", 0)

        logger.info(f"✓ Alchemist Transformation complete: {rating} ({confidence}%)")
        logger.info(f"Transmuted {len(reframed_opportunities)} constraints into opportunities")

        # Update agent responses
        existing_responses = state.get("agent_responses", {})
        updated_responses = existing_responses.copy()
        updated_responses["alchemist"] = alchemist_response_dict

        return {
            "agent_responses": updated_responses,
            "reframed_opportunities": reframed_opportunities
        }

    except Exception as e:
        logger.error(f"✗ Alchemist transformation failed: {e}")
        import traceback
        traceback.print_exc()

        # Graceful degradation: create basic opportunity framing
        fallback_opportunities = [
            {
                "constraint": c["constraint"][:100],
                "opportunity": f"Constraint from {c['agent']} requires strategic mitigation",
                "alchemy_level": 1,
                "agent": c["agent"]
            }
            for c in breaker_constraints[:5]  # Limit to first 5
        ]

        return {
            "reframed_opportunities": fallback_opportunities
        }


def _format_constraints_for_alchemy(constraints: List[Dict[str, Any]]) -> str:
    """Format constraints for Alchemist input.

    Args:
        constraints: List of constraint dicts from breaker agents

    Returns:
        Formatted constraint text
    """
    formatted = []
    for i, c in enumerate(constraints, 1):
        agent = c.get("agent", "unknown")
        rating = c.get("rating", "UNKNOWN")
        constraint = c.get("constraint", "No details")
        confidence = c.get("confidence", 0)

        formatted.append(f"""
Constraint #{i}:
  Agent: {agent}
  Severity: {rating}
  Confidence: {confidence}%
  Details: {constraint[:300]}{'...' if len(constraint) > 300 else ''}
""")

    return "\n".join(formatted)


def _parse_alchemist_opportunities(reasoning: str, original_constraints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse Alchemist's reasoning to extract reframed opportunities.

    Args:
        reasoning: Alchemist's full reasoning text
        original_constraints: Original constraint list for reference

    Returns:
        List of opportunity dicts
    """
    opportunities = []

    # Try to extract structured opportunities from reasoning
    # Look for patterns like "Transmutation:", "Alchemy Level:", etc.

    # Pattern 1: Look for numbered transmutations
    transmutation_pattern = re.compile(
        r'Constraint #(\d+).*?Transmutation:\s*(.+?)(?=\n.*?Alchemy Level:|$)',
        re.DOTALL | re.IGNORECASE
    )

    matches = transmutation_pattern.findall(reasoning)

    if matches:
        for constraint_num, transmutation in matches:
            idx = int(constraint_num) - 1
            if 0 <= idx < len(original_constraints):
                original = original_constraints[idx]

                # Try to extract alchemy level
                alchemy_level = 3  # Default to Level 3 (Credential)
                level_match = re.search(
                    rf'Constraint #{constraint_num}.*?Alchemy Level.*?(\d)',
                    reasoning,
                    re.DOTALL | re.IGNORECASE
                )
                if level_match:
                    alchemy_level = int(level_match.group(1))

                # Try to extract trust premium
                trust_premium = "Not quantified"
                premium_match = re.search(
                    rf'Constraint #{constraint_num}.*?Trust Premium.*?([^\n]+)',
                    reasoning,
                    re.DOTALL | re.IGNORECASE
                )
                if premium_match:
                    trust_premium = premium_match.group(1).strip()

                opportunities.append({
                    "constraint": original["constraint"][:200],
                    "agent": original["agent"],
                    "original_rating": original["rating"],
                    "opportunity": transmutation.strip(),
                    "alchemy_level": alchemy_level,
                    "trust_premium": trust_premium
                })
    else:
        # Fallback: Create generic opportunities from reasoning
        logger.warning("Could not parse structured transmutations - using fallback extraction")

        # Look for key alchemy phrases in reasoning
        alchemy_keywords = [
            ("moat", 5),
            ("market creation", 5),
            ("brand", 4),
            ("credential", 3),
            ("capability", 2),
            ("compliance", 1)
        ]

        for constraint in original_constraints[:10]:  # Limit to first 10
            # Check if this constraint is mentioned in reasoning
            agent = constraint["agent"]
            if agent.lower() in reasoning.lower():
                # Find highest alchemy level mentioned near this agent
                alchemy_level = 3
                for keyword, level in alchemy_keywords:
                    if keyword in reasoning.lower():
                        alchemy_level = max(alchemy_level, level)

                opportunities.append({
                    "constraint": constraint["constraint"][:200],
                    "agent": agent,
                    "original_rating": constraint["rating"],
                    "opportunity": f"Transmute {agent} constraint into competitive advantage (see full analysis)",
                    "alchemy_level": alchemy_level,
                    "trust_premium": "See analysis"
                })

    # If still no opportunities, create minimal fallback
    if not opportunities:
        logger.warning("No opportunities extracted - using minimal fallback")
        opportunities = [
            {
                "constraint": "Multiple constraints identified",
                "opportunity": "Alchemist analysis available in full reasoning",
                "alchemy_level": 3,
                "trust_premium": "See full report"
            }
        ]

    return opportunities
