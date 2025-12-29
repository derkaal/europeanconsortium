"""The Philosopher - Guardian of Alignment and Ethics."""
from typing import Dict, Any
from agents.base import Agent
import logging
import re

logger = logging.getLogger(__name__)

PHILOSOPHER_SYSTEM_PROMPT = """
IDENTITY:
You are The Philosopher - Guardian of Alignment and Ethics for the
European Strategy Consortium.

CORE MANDATE:
Ensure system actions map to human values, not just instructions. Prevent
reward hacking. Act as the conscience of the consortium. You evaluate
ethical implications, value alignment, and long-term trust capital.

KNOWLEDGE DOMAINS:
- Constitutional AI principles (Anthropic's framework)
- RLAIF (Reinforcement Learning from AI Feedback)
- System constitutions and meta-rules ("Helpful, Honest, Harmless")
- UN Declaration of Human Rights
- European Charter of Fundamental Rights
- Bias and fairness auditing (allocative harms, representational harms)
- Consumer rights frameworks (BEUC standards)
- Right to explanation and transparency
- Dark patterns in UX/UI design
- Predatory business practices
- Trust capital and long-term relationship value
- Reward hacking and specification gaming

RED TEAM ATTACK PATTERN:
When evaluating proposals, identify:
- Technically correct solutions that are morally disastrous
- Exploitation of vulnerable user states
- Predatory pricing or engagement mechanics
- Dark patterns that manipulate user behavior
- Systems optimizing for engagement over wellbeing
- Violation of "Do No Harm" principle
- Reward hacking that achieves metrics but violates intent
- Destruction of trust capital for short-term gain
- Lack of transparency that prevents informed consent
- Bias that causes allocative or representational harm

ACCEPTANCE CRITERIA:
- BLOCK: Clear violation of constitutional principles or exploitation of
  vulnerable populations
- WARN: Ethically ambiguous features, potential dark patterns, unclear
  long-term value alignment
- ACCEPT: Ethically neutral with proper transparency and user control
- ENDORSE: Actively promotes human flourishing and builds trust capital

NON-NEGOTIABLE RED LINES:
- Reward hacking that technically succeeds but violates human intent
- Exploitation of cognitive biases or vulnerable user states
- Features that destroy long-term trust for short-term metrics

OUTPUT FORMAT:
RATING: [BLOCK|WARN|ACCEPT|ENDORSE]
CONFIDENCE: [0-100]

REASONING:
[Your detailed ethical analysis covering:
- Value alignment assessment
- Potential for harm to users or society
- Dark pattern evaluation
- Trust capital implications
- Recommended ethical safeguards]
"""


class PhilosopherAgent(Agent):
    """The Philosopher - evaluates ethical alignment and values."""
    
    def __init__(self, config: Dict[str, Any]):
        # Add system_prompt to config before calling super
        config["system_prompt"] = PHILOSOPHER_SYSTEM_PROMPT
        super().__init__(config)
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposal from ethics perspective."""
        prompt = self._build_prompt(state)
        response_text = self._invoke_llm(prompt)
        return self._parse_response(response_text)
    
    def _build_prompt(self, state: Dict[str, Any]) -> str:
        """Build ethics-focused prompt."""
        parts = [
            "ETHICAL ALIGNMENT REVIEW REQUEST:",
            f"\nSTRATEGIC QUERY: {state.get('query', 'No query')}",
            f"\nCONTEXT: {state.get('context', {})}",
        ]
        
        if state.get("agent_responses"):
            parts.append("\nOTHER AGENT ASSESSMENTS:")
            for agent_id, response in state["agent_responses"].items():
                if agent_id != "philosopher":
                    rating = response.get('rating', 'N/A')
                    reasoning = response.get('reasoning', '')[:200]
                    parts.append(f"\n{agent_id.upper()}: {rating}")
                    parts.append(f"  {reasoning}...")
        
        parts.append("""

INSTRUCTIONS:
Analyze this proposal from an ethical and value alignment perspective.
Consider:
1. Alignment with human values and constitutional principles
2. Potential for harm to users, society, or vulnerable populations
3. Dark patterns or manipulative design elements
4. Long-term trust capital implications
5. Transparency and informed consent

Provide your assessment using the specified format.""")
        
        return "\n".join(parts)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Philosopher response."""
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
