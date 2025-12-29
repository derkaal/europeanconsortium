"""The Eco-System - Champion of Planetary Boundaries."""
from typing import Dict, Any
from agents.base import Agent
import logging
import re

logger = logging.getLogger(__name__)

ECOSYSTEM_SYSTEM_PROMPT = """
IDENTITY:
You are The Eco-System - Champion of Planetary Boundaries for the
European Strategy Consortium.

CORE MANDATE:
Represent the biosphere in the boardroom. Reject environmental damage as
an "externality." Treat ecological limits as hard constraints, modeled on
Doughnut Economics (Kate Raworth) and Planetary Boundaries (Rockström).

KNOWLEDGE DOMAINS:
- Software Carbon Intensity (SCI) specification: SCI = ((E × I) + M) / R
- Doughnut Economics framework (Kate Raworth)
- Planetary Boundaries theory (Rockström)
- Scope 1, 2, and 3 emissions accounting across value chains
- Embodied carbon in hardware manufacturing
- Green Software Foundation standards
- Carbon-aware computing and scheduling
- Jevons Paradox and rebound effects
- Power Usage Effectiveness (PUE) metrics
- Energy grid carbon intensity by region and time
- Lifecycle assessment methodologies

RED TEAM ATTACK PATTERN:
When evaluating proposals, identify:
- High inference costs for unnecessary generative models
- Content inflation that increases storage and transmission energy
- Efficiency gains that will lead to increased consumption (Jevons Paradox)
- Embodied carbon costs that negate operational efficiency gains
- Lack of carbon-aware scheduling strategies
- Missing SCI scores or degradation projections
- Greenwashing through vague sustainability claims

ACCEPTANCE CRITERIA:
- BLOCK: SCI score degrades >200% from baseline, or violates absolute
  planetary boundary
- WARN: Missing carbon accounting, or efficiency gains without rebound
  effect mitigation
- ACCEPT: Carbon-neutral with credible offsets and monitoring
- ENDORSE: Carbon-negative or regenerative design with continuous SCI
  improvement

NON-NEGOTIABLE RED LINES:
- Solutions that make net-zero targets mathematically impossible
- Lack of Scope 3 accounting for significant value chain impacts
- Efficiency improvements without Jevons Paradox mitigation plan

OUTPUT FORMAT:
RATING: [BLOCK|WARN|ACCEPT|ENDORSE]
CONFIDENCE: [0-100]

REASONING:
[Your detailed environmental analysis covering:
- Carbon footprint assessment (Scope 1, 2, 3)
- SCI score estimation
- Jevons Paradox risk evaluation
- Planetary boundary implications
- Recommended sustainability measures]
"""


class EcosystemAgent(Agent):
    """The Eco-System - evaluates environmental sustainability."""
    
    def __init__(self, config: Dict[str, Any]):
        # Add system_prompt to config before calling super
        config["system_prompt"] = ECOSYSTEM_SYSTEM_PROMPT
        super().__init__(config)
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposal from sustainability perspective."""
        prompt = self._build_prompt(state)
        response_text = self._invoke_llm(prompt)
        return self._parse_response(response_text)
    
    def _build_prompt(self, state: Dict[str, Any]) -> str:
        """Build sustainability-focused prompt."""
        parts = [
            "ENVIRONMENTAL SUSTAINABILITY REVIEW REQUEST:",
            f"\nSTRATEGIC QUERY: {state.get('query', 'No query')}",
            f"\nCONTEXT: {state.get('context', {})}",
        ]
        
        if state.get("agent_responses"):
            parts.append("\nOTHER AGENT ASSESSMENTS:")
            for agent_id, response in state["agent_responses"].items():
                if agent_id != "ecosystem":
                    rating = response.get('rating', 'N/A')
                    reasoning = response.get('reasoning', '')[:200]
                    parts.append(f"\n{agent_id.upper()}: {rating}")
                    parts.append(f"  {reasoning}...")
        
        parts.append("""

INSTRUCTIONS:
Analyze this proposal from an environmental sustainability perspective.
Consider:
1. Carbon footprint across all scopes (1, 2, 3)
2. Software Carbon Intensity (SCI) implications
3. Jevons Paradox and rebound effects
4. Planetary boundary impacts
5. Lifecycle environmental costs

Provide your assessment using the specified format.""")
        
        return "\n".join(parts)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Eco-System response."""
        rating = "WARN"
        for r in ["ENDORSE", "ACCEPT", "WARN", "BLOCK"]:
            if r in response_text.upper():
                rating = r
                break
        
        confidence = 75
        conf_match = re.search(
            r"CONFIDENCE:\s*(\d+)",
            response_text,
            re.IGNORECASE
        )
        if conf_match:
            confidence = min(100, max(0, int(conf_match.group(1))))
        
        return {
            "rating": rating,
            "confidence": confidence,
            "reasoning": response_text
        }
