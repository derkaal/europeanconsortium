"""
Base Agent Class for European Strategy Consortium

Defines the abstract interface that all specialized agents must implement.
Each agent embodies a distinct worldview and provides adversarial critique
from their specialized domain.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
import re


class AgentResponse:
    """Structured response from an agent"""
    
    def __init__(
        self,
        agent_id: str,
        rating: Literal["BLOCK", "WARN", "ACCEPT", "ENDORSE"],
        confidence: float,
        reasoning: str,
        attack_vector: Optional[str] = None,
        evidence: Optional[List[str]] = None,
        mitigation_plan: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self.agent_id = agent_id
        self.rating = rating
        self.confidence = confidence
        self.reasoning = reasoning
        self.attack_vector = attack_vector
        self.evidence = evidence or []
        self.mitigation_plan = mitigation_plan
        self.mitigation_accepted = None
        self.rejection_reason = None
        self.timestamp = timestamp or datetime.now()
        
        # Metadata (filled by provider)
        self.provider_used = ""
        self.latency_ms = 0.0
        self.token_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for state storage"""
        return {
            "agent_id": self.agent_id,
            "rating": self.rating,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "attack_vector": self.attack_vector,
            "evidence": self.evidence,
            "mitigation_plan": self.mitigation_plan,
            "mitigation_accepted": self.mitigation_accepted,
            "rejection_reason": self.rejection_reason,
            "timestamp": self.timestamp.isoformat(),
            "provider_used": self.provider_used,
            "latency_ms": self.latency_ms,
            "token_count": self.token_count
        }


class Agent(ABC):
    """
    Abstract base class for all consortium agents.
    
    Each agent embodies a distinct worldview with specialized knowledge,
    attack patterns, and acceptance criteria. Agents provide adversarial
    critique to ensure comprehensive strategic analysis.
    
    Example Usage:
        >>> from agents.sovereign import SovereignAgent
        >>> config = load_yaml("config/agents/sovereign.yaml")
        >>> agent = SovereignAgent(config)
        >>> response = agent.invoke(state)
        >>> print(f"{agent.name}: {response.rating} (confidence: {response.confidence})")
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize agent with configuration.
        
        Args:
            config: Agent configuration dictionary containing:
                - agent_id: Unique identifier (e.g., "sovereign")
                - name: Display name (e.g., "The Sovereign")
                - mandate: Core mandate statement
                - system_prompt: Full system prompt defining worldview
                - red_lines: List of non-negotiable constraints
                - acceptance_criteria: Dict mapping ratings to criteria
                - knowledge_domains: List of domain expertise areas
        """
        self.agent_id = config["agent_id"]
        self.name = config["name"]
        self.mandate = config["mandate"]
        self.system_prompt = config["system_prompt"]
        self.red_lines = config["red_lines"]
        self.acceptance_criteria = config["acceptance_criteria"]
        self.knowledge_domains = config.get("knowledge_domains", [])
        
        # Initialize LLM provider (lazy loading)
        self._llm_provider = None
    
    def _get_llm_provider(self):
        """Get tiered LLM provider instance (lazy initialization).

        All agents use the REASONING tier which prioritizes:
        1. Mistral Large (EU Sovereign) - Primary
        2. Claude Sonnet - Fallback 1
        3. GPT-4o - Fallback 2
        """
        if self._llm_provider is None:
            from src.consortium.tiered_llm_provider import get_tiered_provider
            self._llm_provider = get_tiered_provider()
        return self._llm_provider
    
    def _invoke_llm(self, state: Dict[str, Any]) -> str:
        """
        Invoke LLM with system prompt and user message.
        
        PATTERN FROM LANGCHAIN RESEARCH:
        - Build user message with full context
        - Use SystemMessage + HumanMessage pattern
        - Provider handles failover automatically
        
        Args:
            state: Consortium state with query and context
            
        Returns:
            Raw LLM response text
            
        Raises:
            AgentInvocationError: If LLM invocation fails
        """
        import logging
        import time
        
        logger = logging.getLogger(__name__)
        
        try:
            # Extract query and context from state
            query = state.get("query", "")
            context = state.get("context", {})
            memory_cases = state.get("memory_retrievals", [])
            
            # Build user message with full context
            user_message = self._build_prompt(
                query=query,
                query_context=context,
                memory_cases=memory_cases
            )
            
            # Get LLM provider
            provider = self._get_llm_provider()
            
            # Invoke with timing using REASONING tier (EU-first: Mistral Large)
            start_time = time.time()

            response = provider.invoke(
                prompt=user_message,
                task=f"agent_{self.agent_id}",  # Maps to REASONING tier
                system_prompt=self.system_prompt
            )

            latency_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"LLM invocation for {self.agent_id} completed "
                f"in {latency_ms:.0f}ms"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LLM invocation failed for {self.agent_id}: {e}")
            raise AgentInvocationError(
                f"Failed to invoke LLM for {self.agent_id}: {e}"
            )
    
    @abstractmethod
    def invoke(self, state: Dict[str, Any]) -> AgentResponse:
        """
        Process query and return structured rating.
        
        This is the main entry point called by the consortium graph.
        Implementations should:
        1. Build context-aware prompt
        2. Invoke LLM (with provider failover)
        3. Parse response into AgentResponse
        4. Apply domain-specific validation
        
        Args:
            state: Complete consortium state containing query, context,
                   memory retrievals, current proposal, etc.
        
        Returns:
            AgentResponse with rating, confidence, reasoning, and evidence
        
        Raises:
            AgentInvocationError: If agent fails to generate valid response
        """
        pass
    
    def _build_prompt(
        self,
        query: str,
        query_context: Dict[str, Any],
        proposal: Optional[Dict[str, Any]] = None,
        memory_cases: Optional[List[Dict[str, Any]]] = None,
        iteration: int = 1,
        compact: bool = True  # NEW: Enable compact mode by default
    ) -> str:
        """
        Construct complete prompt with all relevant context.
        
        This method assembles:
        - Agent role and mandate
        - System prompt defining worldview
        - Non-negotiable red lines
        - Acceptance criteria
        - Historical precedents from memory
        - Current query and context
        - Proposal under review (if in debate phase)
        - Response format instructions
        
        Args:
            query: User's original query
            query_context: Contextual information (industry, company size, etc.)
            proposal: Current proposal under debate (optional)
            memory_cases: Retrieved historical cases (optional)
            iteration: Current iteration number in debate
        
        Returns:
            Complete prompt string ready for LLM invocation
        """
        prompt_parts = []

        if compact:
            # COMPACT MODE: Reduced tokens (~50-60% reduction)
            # Combine header and mandate in one line
            prompt_parts.append(f"# {self.name} - {self.mandate}")
        else:
            # FULL MODE: Original verbose format
            prompt_parts.append(f"# {self.name}")
            prompt_parts.append(f"\n{self.system_prompt}\n")
            prompt_parts.append("## Your Mandate")
            prompt_parts.append(self.mandate)
        
        # Non-negotiable red lines
        if self.red_lines:
            if compact:
                # Compact: Just list red lines
                prompt_parts.append("\n## Red Lines (BLOCK if violated):")
                for red_line in self.red_lines[:3]:  # Limit to top 3 in compact mode
                    prompt_parts.append(f"• {red_line}")
            else:
                # Full: Include explanation
                prompt_parts.append("\n## Non-Negotiable Red Lines")
                prompt_parts.append("You must BLOCK any proposal that violates these constraints:")
                for red_line in self.red_lines:
                    prompt_parts.append(f"- {red_line}")

        # Acceptance criteria
        if compact:
            # Compact: Only show BLOCK and ACCEPT criteria (most critical)
            prompt_parts.append("\n## Rating:")
            block_criteria = self.acceptance_criteria.get('block') or self.acceptance_criteria.get('BLOCK', [])
            accept_criteria = self.acceptance_criteria.get('accept') or self.acceptance_criteria.get('ACCEPT', [])
            if block_criteria:
                first_block = block_criteria[0] if isinstance(block_criteria, list) else block_criteria
                prompt_parts.append(f"BLOCK if: {first_block}")
            if accept_criteria:
                first_accept = accept_criteria[0] if isinstance(accept_criteria, list) else accept_criteria
                prompt_parts.append(f"ACCEPT if: {first_accept}")
        else:
            # Full: Show all rating levels
            prompt_parts.append("\n## Rating Framework")
            prompt_parts.append("Use this framework to rate proposals:")
            for rating, criteria in self.acceptance_criteria.items():
                prompt_parts.append(f"- **{rating.upper()}**: {criteria}")
        
        # Historical precedents (if available)
        if memory_cases and len(memory_cases) > 0:
            if compact:
                # COMPACT: Show only 1-2 most relevant cases with minimal details
                prompt_parts.append("\n## Past Cases:")
                for i, case in enumerate(memory_cases[:2], 1):  # Max 2 cases in compact mode
                    similarity = case.get('similarity_score', 0.0)
                    metadata = case.get('metadata', {})
                    outcome_status = metadata.get('outcome_status', 'not_implemented')

                    # Ultra-compact format: outcome + similarity + query
                    outcome_icon = {"implemented": "✅", "abandoned": "❌", "in_progress": "🔄"}.get(outcome_status, "⏸️")
                    query_short = case.get('query', 'N/A')[:80] + "..." if len(case.get('query', '')) > 80 else case.get('query', 'N/A')
                    prompt_parts.append(f"{i}. {outcome_icon} (sim:{similarity:.0%}) {query_short}")
            else:
                # FULL: Detailed case information
                prompt_parts.append("\n## Historical Precedents")
                prompt_parts.append(
                    "The following similar cases from the consortium's memory may inform your analysis. "
                    "Learn from successful approaches and past failures:"
                )
                for i, case in enumerate(memory_cases[:3], 1):
                    case_id = case.get('id', 'unknown')[:12]
                    similarity = case.get('similarity_score', 0.0)
                    enhanced_score = case.get('enhanced_score', similarity)
                    boost_reason = case.get('boost_reason', 'N/A')
                    metadata = case.get('metadata', {})

                    quality_score = metadata.get('quality_score', 0.0)
                    outcome_status = metadata.get('outcome_status', 'not_implemented')
                    alignment_score = metadata.get('alignment_score', 0.0)
                    agents_engaged = metadata.get('agents_engaged', '[]')

                    outcome_display = {
                        "implemented": "✅ IMPLEMENTED",
                        "in_progress": "🔄 IN PROGRESS",
                        "abandoned": "❌ ABANDONED",
                        "not_implemented": "⏸️ NOT IMPLEMENTED"
                    }.get(outcome_status, outcome_status.upper())

                    prompt_parts.append(f"\n### Case {i}: {case_id}... (Similarity: {similarity:.2f})")
                    prompt_parts.append(f"**Query**: {case.get('query', 'N/A')}")
                    prompt_parts.append(f"**Outcome**: {outcome_display}")

                    if quality_score > 0:
                        prompt_parts.append(f"**User Rating**: {quality_score:.1f}/5.0")

                    if outcome_status == "implemented" and alignment_score > 0:
                        prompt_parts.append(f"**Alignment Score**: {alignment_score:.1f}/5.0 (how well did it work?)")

                    if "verified" in boost_reason:
                        prompt_parts.append(f"**Note**: {boost_reason.replace('_', ' ').title()} (weighted higher in retrieval)")

                    try:
                        import json
                        agents_list = json.loads(agents_engaged) if isinstance(agents_engaged, str) else agents_engaged
                        if self.agent_id in agents_list:
                            prompt_parts.append(f"**Your Previous Engagement**: You ({self.name}) participated in this case.")
                    except:
                        pass
        else:
            # Cold-start message
            if not compact:
                prompt_parts.append("\n## Historical Precedents")
                prompt_parts.append("**No similar historical cases found.** This appears to be a novel query for the consortium.")
        
        # Current query context
        if compact:
            # Compact: Single line query + key context
            context_items = []
            if query_context:
                for key, value in query_context.items():
                    if value and key in ['industry', 'company_size', 'target_markets']:  # Only critical fields
                        context_items.append(f"{key}={value}")
            context_str = f" ({', '.join(context_items)})" if context_items else ""
            prompt_parts.append(f"\n## Query:{context_str}\n{query}")
        else:
            # Full: Separate sections
            prompt_parts.append("\n## Current Query")
            prompt_parts.append(f"**Query**: {query}")

            if query_context:
                prompt_parts.append("\n**Context**:")
                for key, value in query_context.items():
                    if value:
                        prompt_parts.append(f"- {key.replace('_', ' ').title()}: {value}")
        
        # Proposal under review (if in debate/iteration phase)
        if proposal:
            version = proposal.get('version', 1)
            proposer = proposal.get('proposer', 'Unknown')
            content = proposal.get('content', '')
            
            prompt_parts.append(f"\n## Proposal Under Review (Version {version})")
            prompt_parts.append(f"**Proposed by**: {proposer}")
            prompt_parts.append(f"\n{content}")
            
            if iteration > 1:
                prompt_parts.append(
                    f"\n*Note: This is iteration {iteration}. "
                    "Consider your previous position and whether the revised proposal addresses your concerns.*"
                )
        
        # Response format instructions
        if compact:
            # Compact: Clear but concise format instructions
            prompt_parts.append(
                "\n## Your Response (REQUIRED FORMAT):\n"
                "You MUST respond in this exact format:\n\n"
                "RATING: [Choose one: BLOCK | WARN | ACCEPT | ENDORSE]\n"
                "CONFIDENCE: [Number from 0.0 to 1.0]\n"
                "REASONING: [Your detailed analysis citing specific evidence]\n"
                "ATTACK_VECTOR: [Required if BLOCK/WARN - describe the specific risk]\n"
                "MITIGATION_PLAN: [Required if WARN - propose how to fix the issue]\n\n"
                "Example:\n"
                "RATING: WARN\n"
                "CONFIDENCE: 0.8\n"
                "REASONING: The proposal uses AWS which subjects EU data to US CLOUD Act...\n"
                "ATTACK_VECTOR: Non-EU intelligence agencies could subpoena customer data\n"
                "MITIGATION_PLAN: Implement External Key Management (EKM) with EU-only key storage"
            )
        else:
            # Full: Detailed format with examples
            prompt_parts.append("\n## Your Response")
            prompt_parts.append(
                "Provide your assessment in this exact format:\n"
                "\n"
                "RATING: [BLOCK | WARN | ACCEPT | ENDORSE]\n"
                "CONFIDENCE: [0.0-1.0]\n"
                "REASONING: [Your detailed analysis from your specialized perspective]\n"
                "ATTACK_VECTOR: [If BLOCK/WARN, identify the specific vulnerability or risk]\n"
                "EVIDENCE: [Cite specific regulations, data, or domain knowledge that supports your position]\n"
                "MITIGATION_PLAN: [If WARN, propose specific actions to address your concerns]\n"
                "\n"
                "**Critical Instructions**:\n"
                "- Be specific and cite concrete evidence from your knowledge domains\n"
                "- If you identify problems, propose solutions when possible\n"
                "- Your job is to find issues others miss, but also to help solve them\n"
                "- Provide confidence level honestly - uncertainty is valuable information\n"
                "- Reference your non-negotiable red lines when they apply"
            )
        
        return "\n".join(prompt_parts)
    
    def _parse_response(self, raw_response: str) -> AgentResponse:
        """
        Parse LLM output into structured AgentResponse.
        
        Extracts:
        - RATING: BLOCK, WARN, ACCEPT, or ENDORSE
        - CONFIDENCE: Float between 0.0 and 1.0
        - REASONING: Main analysis text
        - ATTACK_VECTOR: Specific vulnerability identified (optional)
        - EVIDENCE: Supporting citations (optional)
        - MITIGATION_PLAN: Proposed solutions for WARN ratings (optional)
        
        Args:
            raw_response: Raw text from LLM
        
        Returns:
            Structured AgentResponse object
        
        Raises:
            ValueError: If response cannot be parsed or is invalid
        """
        # Extract rating
        rating_match = re.search(
            r"RATING:\s*(BLOCK|WARN|ACCEPT|ENDORSE)",
            raw_response,
            re.IGNORECASE
        )
        if not rating_match:
            raise ValueError(
                f"Could not extract RATING from {self.agent_id} response. "
                f"Response must include 'RATING: [BLOCK|WARN|ACCEPT|ENDORSE]'"
            )
        rating = rating_match.group(1).upper()
        
        # Extract confidence
        confidence_match = re.search(
            r"CONFIDENCE:\s*([0-9]*\.?[0-9]+)",
            raw_response,
            re.IGNORECASE
        )
        if confidence_match:
            confidence = float(confidence_match.group(1))
            confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
        else:
            # Default confidence based on rating
            confidence = 0.8 if rating in ["BLOCK", "ENDORSE"] else 0.6
        
        # Extract reasoning (everything after REASONING: until next section or end)
        reasoning_match = re.search(
            r"REASONING:\s*(.+?)(?=\n(?:ATTACK_VECTOR:|EVIDENCE:|MITIGATION_PLAN:|$))",
            raw_response,
            re.IGNORECASE | re.DOTALL
        )
        reasoning = reasoning_match.group(1).strip() if reasoning_match else raw_response
        
        # Extract attack vector (optional, mainly for BLOCK/WARN)
        attack_match = re.search(
            r"ATTACK_VECTOR:\s*(.+?)(?=\n(?:EVIDENCE:|MITIGATION_PLAN:|$))",
            raw_response,
            re.IGNORECASE | re.DOTALL
        )
        attack_vector = attack_match.group(1).strip() if attack_match else None
        
        # Extract evidence (optional)
        evidence_match = re.search(
            r"EVIDENCE:\s*(.+?)(?=\n(?:MITIGATION_PLAN:|$))",
            raw_response,
            re.IGNORECASE | re.DOTALL
        )
        evidence = []
        if evidence_match:
            evidence_text = evidence_match.group(1).strip()
            # Split by newlines or bullet points
            evidence = [
                line.strip().lstrip('-•*').strip()
                for line in evidence_text.split('\n')
                if line.strip() and not line.strip().startswith('MITIGATION')
            ]
        
        # Extract mitigation plan (optional, mainly for WARN)
        mitigation_match = re.search(
            r"MITIGATION_PLAN:\s*(.+?)$",
            raw_response,
            re.IGNORECASE | re.DOTALL
        )
        mitigation_plan = mitigation_match.group(1).strip() if mitigation_match else None
        
        # Validation: WARN should have mitigation plan
        if rating == "WARN" and not mitigation_plan:
            # Extract from reasoning as fallback
            if "recommend" in reasoning.lower() or "suggest" in reasoning.lower():
                mitigation_plan = "See reasoning for mitigation suggestions"
        
        return AgentResponse(
            agent_id=self.agent_id,
            rating=rating,
            confidence=confidence,
            reasoning=reasoning,
            attack_vector=attack_vector,
            evidence=evidence,
            mitigation_plan=mitigation_plan
        )
    
    def _validate_response(self, response: AgentResponse) -> AgentResponse:
        """
        Apply agent-specific validation to response.
        
        Override this method to implement domain-specific validation logic.
        For example, Sovereign might never ENDORSE solutions with vendor lock-in.
        
        Args:
            response: Parsed agent response
        
        Returns:
            Validated (possibly modified) response
        """
        # Base implementation: no additional validation
        return response
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.agent_id} name='{self.name}'>"


class AgentInvocationError(Exception):
    """Raised when agent fails to generate valid response"""
    pass
