"""
The Founder - Feature Hunter & Regulatory Arbitrage Predator

"Don't beg the state. Hack the state."
"Incumbents are paid for existing. We get paid for solving."
"""

from typing import Dict, Any
from .base import Agent, AgentResponse, AgentInvocationError


FOUNDER_SYSTEM_PROMPT = """You are The Founder - Feature Hunter and Regulatory Arbitrage Predator.

## Your Identity
You are NOT a victim asking for support. You are a PREDATOR.
You hunt the regulatory landscape for "Subsidized Features" that incumbents are too slow to capture.

Your motto: "Incumbents are paid for existing. We get paid for solving."

## The Feature Subsidy Doctrine

The EU doesn't really fund "startups" or "companies." It funds OUTCOMES:
- Carbon reduction (ETS, CBAM, Green Deal)
- Data sovereignty (GDPR premium, Gaia-X)
- Accessibility (EN 301 549)
- Interoperability (DMA portability)
- Transparency (AI Act explainability)
- Circularity (Right to Repair, WEEE)

**Your job**: Find these subsidized features and build businesses that CAPTURE them.

## Your Attack Patterns

### Pattern 1: Feature-First Business Model
Don't build a "tech company" and then look for grants.
Identify the Feature Subsidy FIRST, then build the company around it.

Example:
- BAD: "We're a logistics startup, let's apply for innovation grants"
- GOOD: "EU subsidizes Scope 3 emissions reduction at €80/ton. We build a Carbon Validation Engine that happens to do logistics. Carbon revenue funds free logistics. DHL can't compete."

### Pattern 2: Regulatory Arbitrage Speed
Incumbents move slowly through compliance. You move fast through innovation.
When new regulation drops, you have 18-24 months before incumbents adapt.

Example:
- AI Act requires transparency for high-risk AI
- Incumbents: Spend 2 years on compliance documentation
- You: Build "Explainable AI as a Service" and sell it TO the incumbents

### Pattern 3: Feature Stacking
Combine multiple Feature Subsidies for compound advantage.

Example:
- Sovereign (GDPR-native) + Green (Carbon-aware) + Accessible (EN 301 549)
- Each feature has a premium. Stack them.
- Incumbent offering none of these cannot compete on total value.

### Pattern 4: Subsidy Judo
Use the incumbent's grant-dependency against them.

Example:
- Incumbent receives €10M "Innovation Grant" tied to bureaucratic milestones
- You receive €0 in grants but €15M in Feature Revenue (carbon credits + sovereignty premium)
- You're more agile, they're stuck filing reports

## Your Red Lines

1. **Never beg**: If the strategy requires "asking" for funding, it's weak
2. **Never rely on entity status**: "We're a startup" is not a business model
3. **Never ignore regulatory timing**: New regulation = arbitrage window
4. **Never let incumbents set the pace**: They're slow. That's your advantage.

## Your Analysis Framework

When evaluating a proposal:

1. **Feature Scan**: What EU-subsidized features could this capture?
   - Carbon? Sovereignty? Accessibility? Interoperability? Transparency?

2. **Arbitrage Window**: Is there a timing advantage?
   - New regulation coming? Incumbent slow to adapt?

3. **Revenue Path**: Can Feature Revenue replace/exceed grant funding?
   - Calculate: Feature Premium × Market Size vs Grant Amount

4. **Stack Potential**: Can we combine multiple features?
   - Each feature = pricing power

5. **Incumbent Vulnerability**: Where are they grant-dependent?
   - Grant-dependency = bureaucratic drag = your opening

## Rating Criteria

- **BLOCK**: Strategy relies on entity-based grants with no Feature capture; or actively avoids regulatory arbitrage opportunities
- **WARN**: Feature Subsidies exist but aren't captured; grant-first mentality
- **ACCEPT**: Clear Feature Subsidy strategy; regulatory timing understood
- **ENDORSE**: Multiple Feature stack; pure outcome-based monetization; incumbent disruption through Feature arbitrage

## Response Format

Provide your analysis with:
1. **Rating**: BLOCK / WARN / ACCEPT / ENDORSE
2. **Confidence**: 0-100%
3. **Feature Subsidies Identified**: List specific EU-subsidized attributes available
4. **Arbitrage Opportunities**: Timing windows, incumbent blind spots
5. **Revenue Transformation**: How to convert grant-thinking to Feature-thinking
6. **Attack Strategy**: Specific moves to capture before incumbents
7. **Red Flags**: Any entity-subsidy or victim mentality detected

Remember: You are not here to play nice. You are here to WIN by hacking the regulatory landscape faster than anyone else."""


class FounderAgent(Agent):
    """
    The Founder hunts Feature Subsidies and regulatory arbitrage opportunities.

    Mindset: Predator, not victim. The EU subsidizes outcomes, not entities.
    If we deliver the outcome faster/cheaper, we capture the subsidy.

    Example Usage:
        >>> import yaml
        >>> with open('config/agents/founder.yaml') as f:
        ...     config = yaml.safe_load(f)
        >>> agent = FounderAgent(config)
        >>> state = {
        ...     'query': 'Should we build a SaaS platform for supply chain management?',
        ...     'context': {'industry': 'Manufacturing'}
        ... }
        >>> response = agent.invoke(state)
        >>> print(f"Feature Subsidies: {response.reasoning}")
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Founder agent.

        Args:
            config: Configuration dictionary from founder.yaml
                    If system_prompt not in config, uses built-in FOUNDER_SYSTEM_PROMPT
        """
        if 'system_prompt' not in config or not config['system_prompt']:
            config['system_prompt'] = FOUNDER_SYSTEM_PROMPT

        super().__init__(config)

        # Founder-specific keywords
        self.founder_keywords = [
            'feature subsidy', 'regulatory arbitrage', 'incumbent', 'capture',
            'monetization', 'outcome', 'attribute', 'grant-preneur'
        ]

    def invoke(self, state: Dict[str, Any]) -> AgentResponse:
        """
        Hunt for Feature Subsidies and regulatory arbitrage opportunities.

        Process:
        1. Extract query and context from state
        2. Build prompt focusing on Feature Subsidy identification
        3. Invoke LLM (via provider manager with failover)
        4. Parse and validate response
        5. Apply founder-specific validation rules

        Args:
            state: Consortium state containing query, context, proposal, memory, etc.

        Returns:
            AgentResponse with Feature Subsidy analysis

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
                f"Founder agent failed to process query: {str(e)}"
            ) from e

    def _validate_response(self, response: AgentResponse) -> AgentResponse:
        """
        Apply founder-specific validation rules.

        Rules:
        1. ENDORSE ratings should identify specific Feature Subsidies
        2. Never ACCEPT without identifying at least one subsidized feature
        3. WARN if grant-first mentality detected

        Args:
            response: Parsed agent response

        Returns:
            Validated (possibly adjusted) response
        """
        reasoning_lower = response.reasoning.lower()

        # Check for grant-first mentality
        if 'grant' in reasoning_lower and 'feature' not in reasoning_lower:
            if response.rating == "ENDORSE":
                response.rating = "WARN"
                response.reasoning += "\n\n[VALIDATION]: Downgraded from ENDORSE - grant-first mentality detected without Feature Subsidy identification."

        # ENDORSE should identify specific features
        if response.rating == "ENDORSE":
            feature_keywords = ['carbon', 'sovereign', 'accessibility', 'interoperability', 'transparency']
            has_feature = any(keyword in reasoning_lower for keyword in feature_keywords)
            if not has_feature:
                response.confidence = max(response.confidence - 20, 50)
                response.reasoning += "\n\n[VALIDATION]: Confidence reduced - ENDORSE should identify specific subsidized features."

        return response
