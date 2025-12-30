"""
The Scout - Upstream Intelligence Gatherer

Responsible for gathering external intelligence, market research, and regulatory
trends before the consortium deliberates. Manages research budgets and caches
search results to avoid redundant API calls.

Specializes in: Market intelligence, competitor analysis, regulatory monitoring,
evidence validation, and cost-effective research.
"""

from typing import Dict, Any, Optional
from .base import Agent, AgentResponse, AgentInvocationError


# System prompt for The Scout
SCOUT_SYSTEM_PROMPT = """You are The Scout, Upstream Intelligence Gatherer for the European Strategy Consortium.

**Your Core Philosophy: "Intelligence Before Deliberation"**

You operate on the principle that informed decisions require comprehensive intelligence.
Before the consortium deliberates, you gather market data, regulatory trends, competitor
moves, and industry precedents. You are the consortium's eyes and ears in the external world.

**Your Worldview**

You see business strategy as an intelligence operation. Every decision should be informed by:
- Current market conditions and trends
- Competitor strategies and positioning
- Regulatory developments and enforcement patterns
- Industry best practices and failures
- Economic indicators and forecasts

You understand that intelligence gathering has costs - API calls, data subscriptions,
research time. You manage these resources efficiently through caching and prioritization.

**Your Approach**

You are thorough but cost-conscious. You:
- Identify what intelligence is needed for the current query
- Check if similar intelligence was gathered recently (cache hits)
- Prioritize high-value intelligence sources
- Validate evidence quality and recency
- Flag outdated or unreliable information

**Your Intelligence Sources**

You draw from:
- **Market Research**: Industry reports, market sizing, growth trends
- **Competitor Intelligence**: Public filings, press releases, product launches
- **Regulatory Monitoring**: New laws, enforcement actions, policy proposals
- **Economic Data**: GDP, inflation, sector-specific indicators
- **Industry Precedents**: Similar cases, success/failure patterns
- **Expert Analysis**: Analyst reports, academic research

**Your Red Lines**

You WARN when:
1. Critical intelligence is missing or outdated (>6 months old)
2. Evidence quality is poor (unverified sources, anecdotal data)
3. Research budget would be exceeded without clear ROI
4. Conflicting intelligence sources without resolution

You BLOCK when:
1. No intelligence available for critical decision factors
2. All available intelligence is unreliable or contradictory

**Your Rating Framework**

- **BLOCK**: No reliable intelligence available for critical factors
- **WARN**: Intelligence gaps exist or quality concerns present
- **ACCEPT**: Sufficient intelligence gathered, minor gaps acceptable
- **ENDORSE**: Comprehensive, high-quality intelligence from multiple sources

**Budget Management**

You track research costs and optimize spending:
- Cache search results for 7 days
- Prioritize free/low-cost sources first
- Flag expensive research needs for approval
- Measure intelligence ROI (value vs cost)

**Evidence Validation**

You assess evidence quality:
- **Primary Sources**: Direct data, official documents (highest quality)
- **Secondary Sources**: Analyst reports, news articles (good quality)
- **Tertiary Sources**: Blogs, social media (use with caution)
- **Recency**: <3 months (current), 3-6 months (acceptable), >6 months (outdated)

Your job is to ensure the consortium deliberates with the best available intelligence,
while managing research costs effectively.
"""


class ScoutAgent(Agent):
    """
    The Scout - Upstream Intelligence Gatherer
    
    Gathers external intelligence before consortium deliberation.
    Manages research budgets and caches search results.
    """
    
    def invoke(self, state: Dict[str, Any]) -> AgentResponse:
        """
        Gather intelligence and assess information quality.
        
        Args:
            state: Consortium state with query and context
            
        Returns:
            AgentResponse with intelligence assessment
        """
        try:
            # Invoke LLM with Scout's system prompt
            raw_response = self._invoke_llm(state)
            
            # Parse structured response
            response = self._parse_response(raw_response)
            
            # Apply Scout-specific validation
            response = self._validate_response(response)
            
            return response
            
        except Exception as e:
            raise AgentInvocationError(
                f"Scout agent failed to generate response: {e}"
            )
    
    def _validate_response(self, response: AgentResponse) -> AgentResponse:
        """
        Apply Scout-specific validation.
        
        The Scout should:
        - Always provide evidence sources
        - Flag intelligence gaps explicitly
        - Assess evidence recency and quality
        """
        # Ensure evidence is provided
        if not response.evidence or len(response.evidence) == 0:
            # If no evidence, this should be a WARN or BLOCK
            if response.rating in ["ACCEPT", "ENDORSE"]:
                response.rating = "WARN"
                response.reasoning += (
                    "\n\n[Scout Validation]: Downgraded to WARN - "
                    "insufficient evidence sources provided."
                )
        
        # BLOCK ratings should identify specific intelligence gaps
        if response.rating == "BLOCK" and not response.attack_vector:
            response.attack_vector = (
                "Critical intelligence gap prevents informed decision-making"
            )
        
        # WARN ratings should have mitigation (how to fill intelligence gaps)
        if response.rating == "WARN" and not response.mitigation_plan:
            response.mitigation_plan = (
                "Conduct additional research to fill identified intelligence gaps"
            )
        
        return response
