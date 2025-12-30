"""Conditionality & Leverage Agent - The Constitutional Court of Time.

Based on Fritz Scharpf's Joint-Decision Trap analysis, the CLA prevents
"Zombie Policies" that are politically convenient today but structurally
brittle tomorrow.
"""

from typing import Dict, Any, Optional
from .base import Agent, AgentResponse, AgentInvocationError
import logging
import re

logger = logging.getLogger(__name__)

CLA_SYSTEM_PROMPT = """You are the Conditionality & Leverage Agent (CLA).
You are the "Constitutional Court of Time" for the European Strategy Consortium.

Your mandate is to prevent "Zombie Policies"—strategies that are politically
convenient today but structurally brittle tomorrow.

Your intellectual framework derives from Fritz Scharpf's analysis of the
'Joint-Decision Trap' in European governance—the pathology where unanimous
consent requirements produce suboptimal outcomes that no party can
unilaterally exit.

THE PRIME DIRECTIVE:
You do not evaluate content (is this a good idea?).
You evaluate robustness (what happens when the current consensus breaks?).

Your role protects democratic legitimacy by preventing commitments that will
inevitably be broken through ad-hoc political intervention. Structured
conditionality is not a constraint on democracy—it is the mechanism by which
democracy adapts without losing credibility.

EVALUATION PROTOCOL (The 4 Tests):

1. THE COMMITMENT TEST (Reversibility):
   Question: If this policy becomes obsolete (technology shifts, prices drop),
   can it be reversed without a humiliating political vote?
   Failure Mode: "Locked-in" commitments requiring unanimous consensus to undo.
   Pass Criteria: Explicit sunset clause, automatic review trigger, or
   graduated phase-out.

2. THE TRIGGER TEST (Exogeneity):
   Question: What observable signal forces a change?
   Pass: Exogenous triggers with:
     - Metric (what is measured)
     - Threshold (numeric boundary)
     - Observation window (how long before trigger fires)
     - Automatic consequence (what happens without further decision)
   Fail: Endogenous triggers (e.g., "The Board will review annually").
   Reviews are not constraints; they are theater.

3. THE COST ALLOCATION TEST (Liability):
   Question: When (not if) this fails, who pays?
   Requirement: The proposal must explicitly name the bearer of downside risk.
   Examples: "Vendor pays penalties," "Subsidy budget capped at €10M,"
   "Insurance bond required."

4. THE LEVERAGE TEST (Bradford's Law):
   Question: Does enforcement rely on "Political Will" (fragile) or
   "Market Access" (robust)?
   Requirement: Enforcement must leverage the Single Market (procurement bans,
   certification denial, fines tied to revenue).
   Fail: Enforcement that requires ongoing political consensus or voluntary
   compliance.

OUTPUT FORMAT (You MUST use this exact format):

VERDICT: [STRUCTURALLY_CREDIBLE | FRAGILE_CONSENSUS | ZOMBIE_RISK]

FAILED_TESTS: [Commitment, Trigger, Cost, Leverage] or [None]

CRITIQUE: [One sentence explaining the core fragility]

MECHANISM_PATCH:
TRIGGER: [Specific metric + threshold + window]
ACTION: [Automatic consequence]
AUTHORITY: [Exogenous/Automatic or Conditional/Requires-Approval]

BEHAVIOR:
You are a BLOCKER. If a proposal fails ANY of these tests, you must reject it.
You cannot "warn." You must STOP the process until the mechanism is fixed.

Remember: Your job is to say "yes, AND here's the mechanism that makes it
credible over time."
"""


class CLAAgent(Agent):
    """Conditionality & Leverage Agent.
    
    Evaluates temporal robustness of proposals using the 4 Scharpfian tests.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize CLA agent.
        
        Args:
            config: Configuration dictionary
        """
        if 'system_prompt' not in config or not config['system_prompt']:
            config['system_prompt'] = CLA_SYSTEM_PROMPT
        
        super().__init__(config)
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposal against the 4 Scharpfian tests.
        
        Args:
            state: Current consortium state
            
        Returns:
            CLA review with verdict and mechanism patch
            
        Raises:
            AgentInvocationError: If evaluation fails
        """
        try:
            # Use real LLM invocation from base class
            raw_response = self._invoke_llm(state)
            
            # Parse CLA-specific response format
            review = self._parse_cla_response(raw_response)
            
            return review
            
        except Exception as e:
            raise AgentInvocationError(
                f"CLA agent failed to process query: {str(e)}"
            ) from e
    
    def _parse_cla_response(self, response_text: str) -> Dict[str, Any]:
        """Parse CLA response into structured format.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Structured CLA review
        """
        # Extract verdict
        verdict = "ZOMBIE_RISK"
        if "STRUCTURALLY_CREDIBLE" in response_text.upper():
            verdict = "STRUCTURALLY_CREDIBLE"
        elif "FRAGILE_CONSENSUS" in response_text.upper():
            verdict = "FRAGILE_CONSENSUS"
        
        # Extract failed tests
        failed_tests = []
        for test in ["Commitment", "Trigger", "Cost", "Leverage"]:
            pattern = rf"(?:fail|failed|fails).*{test}"
            if re.search(pattern, response_text, re.IGNORECASE) or \
               re.search(rf"{test}.*(?:fail|failed|fails)",
                         response_text, re.IGNORECASE):
                failed_tests.append(test)
        
        # Also check FAILED_TESTS line
        failed_match = re.search(
            r"FAILED_TESTS:\s*\[([^\]]+)\]",
            response_text,
            re.IGNORECASE
        )
        if failed_match:
            tests_str = failed_match.group(1)
            for test in ["Commitment", "Trigger", "Cost", "Leverage"]:
                if test in tests_str and test not in failed_tests:
                    failed_tests.append(test)
        
        # Extract critique
        critique_match = re.search(
            r"CRITIQUE:\s*(.+?)(?:\n|MECHANISM|$)",
            response_text,
            re.IGNORECASE | re.DOTALL
        )
        critique = (
            critique_match.group(1).strip()
            if critique_match
            else "No specific critique provided."
        )
        
        # Extract mechanism patch
        mechanism_patch = None
        trigger_match = re.search(
            r"TRIGGER:\s*(.+?)(?:\n|ACTION|$)",
            response_text,
            re.IGNORECASE
        )
        action_match = re.search(
            r"ACTION:\s*(.+?)(?:\n|AUTHORITY|$)",
            response_text,
            re.IGNORECASE
        )
        authority_match = re.search(
            r"AUTHORITY:\s*(.+?)(?:\n|$)",
            response_text,
            re.IGNORECASE
        )
        
        if trigger_match or action_match:
            mechanism_patch = {
                "trigger": (
                    trigger_match.group(1).strip()
                    if trigger_match
                    else "Not specified"
                ),
                "action": (
                    action_match.group(1).strip()
                    if action_match
                    else "Not specified"
                ),
                "authority": (
                    authority_match.group(1).strip()
                    if authority_match
                    else "Requires-Approval"
                )
            }
        
        return {
            "verdict": verdict,
            "failed_tests": failed_tests,
            "critique": critique,
            "mechanism_patch": mechanism_patch,
            "reasoning": response_text,
            "rating": "BLOCK" if verdict != "STRUCTURALLY_CREDIBLE" else "ACCEPT",
            "confidence": 0.95 if failed_tests else 0.85  # Fixed: was 95/85, now 0.95/0.85
        }
    
    def __repr__(self) -> str:
        return f"<CLAAgent '{self.name}'>"
