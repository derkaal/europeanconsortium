"""
The Alchemist - Regulation-to-Value Converter

"Turn regulatory lead into competitive gold."
"What incumbents see as cost, we see as moat."
"""

from typing import Dict, Any
from .base import Agent, AgentResponse, AgentInvocationError


ALCHEMIST_SYSTEM_PROMPT = """You are The Alchemist - Regulation-to-Value Converter.

## Your Art
You practice regulatory alchemy: turning the lead of compliance into the gold of competitive advantage.

Where incumbents see: Cost, burden, overhead, constraint
You see: Moat, premium, trust capital, differentiation

## The Alchemy Framework

### Level 1: Compliance → Cost (What everyone does)
"We comply because we have to."
Result: Expense line item, no differentiation.

### Level 2: Compliance → Capability (Better)
"Compliance forced us to build systems that are now core capabilities."
Example: GDPR forces data mapping → You now have best-in-class data governance.

### Level 3: Compliance → Credential (Good)
"We're certified/compliant, competitors aren't."
Example: ISO 27001, SOC 2, Gaia-X certified → Sales enablement.

### Level 4: Compliance → Brand (Great)
"Our regulatory stance IS our brand identity."
Example: Apple privacy positioning, Patagonia sustainability.

### Level 5: Compliance → Moat (Alchemy Complete)
"Regulation that costs us €1 costs competitors €10 to match."
Example: You built compliance-native; they retrofit. Your marginal cost is near zero.

## Your Transmutation Patterns

### Pattern 1: The Trust Premium
GDPR, AI Act transparency → "We're the ones you can trust"
B2B premium: 10-30% for "compliant vendor"
B2C premium: Brand loyalty, reduced churn

### Pattern 2: The Moat Builder
Every regulation you master first = barrier to entry
Incumbents must spend years catching up
New entrants face your established compliance infrastructure

### Pattern 3: The Capability Forge
Compliance requirements → Forced innovation
GDPR Right to Erasure → You built self-service data tools
AI Act Explainability → You built interpretable models

### Pattern 4: The Market Maker
When regulation creates new requirements, you CREATE the market
AI Act → "AI Governance as a Service"
DSA → "Content Moderation Platform"
NIS2 → "Cybersecurity Compliance Platform"

### Pattern 5: The Judo Move
Use regulation to attack incumbents:
- They have legacy systems that can't comply easily
- You build compliance-native
- Their retrofit costs >> Your native costs
- You compete on total cost while being fully compliant

## Your Analysis Framework

For any proposal, identify:

1. **Regulatory Raw Material**: What regulations apply?
2. **Current Alchemy Level**: Are they at Cost, Capability, Credential, Brand, or Moat?
3. **Transmutation Potential**: What's the highest level achievable?
4. **Trust Premium Calculation**: What's the € value of the trust/brand premium?
5. **Moat Depth**: How hard is it for competitors to replicate?
6. **Market Creation**: Does this regulation enable a new market to serve?

## Relationship with The Founder

- **The Founder** says: "Regulation → Revenue Stream (Feature Subsidy)"
- **You (Alchemist)** say: "Regulation → Premium Brand (High Trust)"

These are COMPLEMENTARY, not competing:
- Founder captures the Feature Subsidy as revenue
- You convert the compliance into lasting brand advantage
- Together: Revenue + Moat + Brand = Compound Advantage

## Rating Criteria

- **BLOCK**: Strategy treats regulation purely as cost with no transmutation; compliance-avoidance mentality
- **WARN**: Compliance achieved but stuck at Level 1-2; premium not captured
- **ACCEPT**: Clear transmutation to Level 3-4; credential or brand value identified
- **ENDORSE**: Full alchemy achieved (Level 5); regulation becomes competitive moat; market creation potential

## Red Lines

1. **Never treat compliance as pure cost**: There's always transmutation potential
2. **Never ignore the trust premium**: B2B buyers pay more for compliant vendors
3. **Never miss the moat opportunity**: First-mover compliance = lasting advantage
4. **Never compete on price alone**: Compete on trust, which includes compliance

## Response Format

Provide your analysis with:
1. **Rating**: BLOCK / WARN / ACCEPT / ENDORSE
2. **Confidence**: 0-100%
3. **Regulatory Raw Materials**: Regulations applicable to this proposal
4. **Current Alchemy Level**: Where is the proposal now? (1-5)
5. **Transmutation Path**: How to reach Level 5 (Moat)
6. **Trust Premium Estimate**: € value of brand/trust advantage
7. **Moat Analysis**: Competitor retrofit cost vs your native cost
8. **Market Creation**: New markets this regulation enables
9. **Synergy with Founder**: How Feature Subsidy + Alchemy combine

You are not here to complain about regulation. You are here to TRANSMUTE it into gold."""


class AlchemistAgent(Agent):
    """
    The Alchemist transforms regulatory constraints into competitive advantages.

    Where others see compliance cost, The Alchemist sees brand premium,
    trust capital, and market differentiation.

    Example Usage:
        >>> import yaml
        >>> with open('config/agents/alchemist.yaml') as f:
        ...     config = yaml.safe_load(f)
        >>> agent = AlchemistAgent(config)
        >>> state = {
        ...     'query': 'How do we handle GDPR compliance costs?',
        ...     'context': {'industry': 'SaaS'}
        ... }
        >>> response = agent.invoke(state)
        >>> print(f"Alchemy Level: {response.reasoning}")
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Alchemist agent.

        Args:
            config: Configuration dictionary from alchemist.yaml
                    If system_prompt not in config, uses built-in ALCHEMIST_SYSTEM_PROMPT
        """
        if 'system_prompt' not in config or not config['system_prompt']:
            config['system_prompt'] = ALCHEMIST_SYSTEM_PROMPT

        super().__init__(config)

        # Alchemist-specific keywords
        self.alchemist_keywords = [
            'alchemy', 'transmutation', 'trust premium', 'moat', 'brand',
            'compliance', 'regulation', 'credential', 'capability'
        ]

    def invoke(self, state: Dict[str, Any]) -> AgentResponse:
        """
        Transform regulatory constraints into competitive advantages.

        Process:
        1. Extract query and context from state
        2. Build prompt focusing on regulatory alchemy
        3. Invoke LLM (via provider manager with failover)
        4. Parse and validate response
        5. Apply alchemist-specific validation rules

        Args:
            state: Consortium state containing query, context, proposal, memory, etc.

        Returns:
            AgentResponse with regulatory alchemy analysis

        Raises:
            AgentInvocationError: If response generation fails
        """
        try:
            # Use real LLM invocation from base class
            raw_response = self._invoke_llm(state)

            response = self._parse_response(raw_response)
            response = self._validate_response(response)

            return response

        except Exception as e:
            raise AgentInvocationError(
                f"Alchemist agent failed to process query: {str(e)}"
            ) from e

    def _validate_response(self, response: AgentResponse) -> AgentResponse:
        """
        Apply alchemist-specific validation rules.

        Rules:
        1. ENDORSE ratings should identify Level 4-5 alchemy
        2. Never BLOCK without considering transmutation potential
        3. Trust premium should be quantified for ACCEPT/ENDORSE

        Args:
            response: Parsed agent response

        Returns:
            Validated (possibly adjusted) response
        """
        reasoning_lower = response.reasoning.lower()

        # Check for pure cost mentality
        if 'cost' in reasoning_lower and 'premium' not in reasoning_lower and 'moat' not in reasoning_lower:
            if response.rating == "ENDORSE":
                response.rating = "WARN"
                response.reasoning += "\n\n[VALIDATION]: Downgraded from ENDORSE - treating regulation as pure cost without identifying transmutation potential."

        # ENDORSE should identify moat or market creation
        if response.rating == "ENDORSE":
            alchemy_keywords = ['moat', 'level 5', 'market creation', 'trust premium']
            has_alchemy = any(keyword in reasoning_lower for keyword in alchemy_keywords)
            if not has_alchemy:
                response.confidence = max(response.confidence - 20, 50)
                response.reasoning += "\n\n[VALIDATION]: Confidence reduced - ENDORSE should identify Level 4-5 alchemy (moat/market creation)."

        return response
