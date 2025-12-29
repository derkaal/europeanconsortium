"""The Architect - Master of Systems and Patterns."""
from typing import Dict, Any
from agents.base import Agent
import logging
import re

logger = logging.getLogger(__name__)

ARCHITECT_SYSTEM_PROMPT = """
IDENTITY:
You are The Architect - Master of Systems and Patterns for the European Strategy Consortium.

CORE MANDATE:
Translate strategic intent into executable system design. Build capabilities while respecting 
constraints from all other agents. You evaluate technical feasibility, architectural soundness, 
and implementation complexity.

KNOWLEDGE DOMAINS:
- Multi-Agent System design patterns (Supervisor, Hierarchical, Swarm)
- LangGraph for state-based agent flows
- Infrastructure as Code (Kubernetes, Terraform, Docker)
- Cloud-native architectures and container orchestration
- Microservices decomposition principles
- System reliability and failure mode analysis
- Single points of failure identification
- Parallel execution optimization
- Performance profiling and bottleneck identification
- Context window management and memory systems

RED TEAM ATTACK PATTERN:
When evaluating proposals, identify:
- Monolithic designs that should be decomposed
- Single points of failure in system architecture
- Context drift from handling too many domains
- Impossible integration requirements
- Performance bottlenecks from poor parallelization
- Missing tool access that would enable capabilities
- Overly complex designs that could be simplified
- Lack of deterministic state management

ACCEPTANCE CRITERIA:
- BLOCK: Single point of failure with no fallback, or fundamentally unscalable design
- WARN: Suboptimal architecture patterns, tight coupling, performance concerns
- ACCEPT: Solid architecture following established patterns with clear migration path
- ENDORSE: Innovative architecture that elegantly solves multiple constraints simultaneously

NON-NEGOTIABLE RED LINES:
- Architectures that cannot be tested or debugged
- Designs that create irrecoverable failure modes
- Missing observability and monitoring capabilities

OUTPUT FORMAT:
RATING: [BLOCK|WARN|ACCEPT|ENDORSE]
CONFIDENCE: [0-100]

REASONING:
[Your detailed technical analysis covering:
- Architecture pattern assessment
- Scalability evaluation
- Failure mode analysis
- Integration complexity
- Performance considerations
- Recommended improvements]
"""


class ArchitectAgent(Agent):
    """The Architect - evaluates technical feasibility and system design."""
    
    def __init__(self, config: Dict[str, Any]):
        # Add system_prompt to config before calling super
        config["system_prompt"] = ARCHITECT_SYSTEM_PROMPT
        super().__init__(config)
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposal from architecture perspective."""
        prompt = self._build_prompt(state)
        response_text = self._invoke_llm(prompt)
        return self._parse_response(response_text)
    
    def _build_prompt(self, state: Dict[str, Any]) -> str:
        """Build architecture-focused prompt."""
        parts = [
            "TECHNICAL ARCHITECTURE REVIEW REQUEST:",
            f"\nSTRATEGIC QUERY: {state.get('query', 'No query')}",
            f"\nCONTEXT: {state.get('context', {})}",
        ]
        
        if state.get("agent_responses"):
            parts.append("\nOTHER AGENT ASSESSMENTS:")
            for agent_id, response in state["agent_responses"].items():
                if agent_id != "architect":
                    rating = response.get('rating', 'N/A')
                    reasoning = response.get('reasoning', '')[:200]
                    parts.append(f"\n{agent_id.upper()}: {rating}")
                    parts.append(f"  {reasoning}...")
        
        parts.append("""

INSTRUCTIONS:
Analyze this proposal from a technical architecture perspective. Consider:
1. System design patterns and their appropriateness
2. Scalability and performance implications
3. Single points of failure and resilience
4. Integration complexity and dependencies
5. Observability and debugging capability

Provide your assessment using the specified format.""")
        
        return "\n".join(parts)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Architect response."""
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
