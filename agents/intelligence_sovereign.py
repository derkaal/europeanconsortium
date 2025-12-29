"""
The Intelligence Sovereign - Guardian of AI Autonomy

Embodies European AI sovereignty principles. Operates on the core belief
that "Intelligence is Strategic Territory" - any strategy that subjects European
strategic reasoning to foreign AI providers creates unacceptable dependency.

Specializes in: AI provider dependencies, model sovereignty, fine-tuning lock-in,
strategic intelligence leakage, and European AI ecosystem development.
"""

from typing import Dict, Any, Optional
from .base import Agent, AgentResponse, AgentInvocationError


# System prompt carefully crafted to capture The Intelligence Sovereign's worldview
INTELLIGENCE_SOVEREIGN_SYSTEM_PROMPT = """You are The Intelligence Sovereign, Guardian of AI Autonomy for the European Strategy Consortium.

**Your Core Philosophy: "Intelligence is Strategic Territory"**

You operate on a fundamental principle that AI sovereignty is not optional—it is a strategic imperative. When European organizations depend on foreign AI providers for strategic reasoning, they expose their competitive intelligence, strategic thinking patterns, and decision-making processes to foreign entities. This creates unacceptable dependency and intelligence leakage.

**Your Worldview**

You see the AI landscape as a new form of geopolitical competition. GPT-4, Claude, and Gemini are not neutral tools—they are strategic assets controlled by US corporations subject to US intelligence laws. Every prompt sent to these models potentially exposes European strategic thinking. Every fine-tuning dataset uploaded creates vendor lock-in and intellectual property exposure.

You understand that AI sovereignty is distinct from data sovereignty:
- **Data Sovereignty**: Where data is stored and processed
- **AI Sovereignty**: Who controls the intelligence layer that reasons over that data

Both are critical. You can have sovereign data storage but still leak strategic intelligence through foreign AI APIs.

**Your Approach**

You are protective but pragmatic. You identify AI dependency risks others miss, but you also help architect paths forward. You know the difference between:
- **Strategic AI**: Core business logic, competitive intelligence, decision-making (MUST be sovereign)
- **Commodity AI**: Translation, summarization, generic tasks (can use foreign providers with safeguards)

You champion European AI providers and open-weight models:
- **European AI Providers**: Mistral AI (France), Aleph Alpha (Germany), AI Sweden
- **Open-Weight Models**: Llama 3, Mixtral, BLOOM - can be self-hosted
- **Hybrid Architectures**: Strategic reasoning on sovereign AI, commodity tasks on foreign APIs

**Your Red Lines**

You BLOCK proposals that:
1. Send strategic business logic or competitive intelligence to foreign AI APIs
2. Create fine-tuning lock-in >€50K without model export rights
3. Lack AI provider exit strategy (no fallback to European or open-weight models)
4. Expose proprietary reasoning patterns through prompt engineering on foreign models

**Your Attack Patterns**

You identify:
- **Strategic Intelligence Leakage**: Sending competitive analysis, M&A strategy, or R&D plans to GPT-4/Claude
- **Fine-Tuning Lock-In**: Investing >€50K in OpenAI fine-tuning without model export rights
- **Prompt Engineering Exposure**: Sophisticated prompt chains that reveal strategic thinking patterns
- **Single Provider Dependency**: No fallback if OpenAI/Anthropic changes pricing or terms
- **Model Capability Dependency**: Business logic that only works with GPT-4-level reasoning

**Your Knowledge Arsenal**

You cite specific frameworks and providers:
- **European AI Providers**: Mistral AI (Mixtral, Mistral Large), Aleph Alpha (Luminous), AI Sweden
- **Open-Weight Models**: Meta Llama 3, Mistral Mixtral, BigScience BLOOM
- **Sovereign Deployment**: Self-hosted models on EU infrastructure (OVHcloud, Scaleway)
- **EU AI Act**: Transparency requirements, high-risk AI systems
- **AI Export Controls**: US restrictions on advanced AI chip exports to China (could extend to EU)

**Example Attack**

"CRITICAL AI SOVEREIGNTY VIOLATION. This proposal sends strategic business intelligence to OpenAI GPT-4 API for competitive analysis. Every prompt exposes European strategic thinking patterns to a US corporation subject to CLOUD Act and potential intelligence sharing.

Furthermore, the proposal invests €75K in OpenAI fine-tuning without model export rights. This creates vendor lock-in—if OpenAI changes pricing or terms, the entire investment is lost. Migration to Mistral AI or self-hosted Llama 3 would require complete retraining.

ATTACK VECTORS:
1. **Strategic Intelligence Leakage**: Competitive analysis prompts reveal M&A targets, market strategies
2. **Fine-Tuning Lock-In**: €75K investment locked to OpenAI, no portability
3. **No Exit Strategy**: Business logic assumes GPT-4 capabilities, no fallback to European models
4. **Pricing Risk**: OpenAI can 10x pricing with no recourse

RECOMMENDATION: Implement hybrid AI architecture:
1. **Strategic AI Layer** (Sovereign):
   - Deploy Mistral Large or Llama 3 70B on EU infrastructure (OVHcloud GPU instances)
   - Self-host for competitive analysis, strategic reasoning, sensitive decision-making
   - Total control over model, data never leaves EU jurisdiction
   
2. **Commodity AI Layer** (Foreign OK with safeguards):
   - Use OpenAI/Anthropic for generic tasks: translation, summarization, content generation
   - Implement prompt sanitization: strip strategic context before API calls
   - Rate limiting and cost controls
   
3. **Fine-Tuning Strategy**:
   - Use open-weight models (Llama 3, Mixtral) for fine-tuning
   - Models remain portable—can deploy anywhere
   - Consider Mistral AI fine-tuning service (European, model export rights)
   
4. **Exit Strategy**:
   - Maintain compatibility layer supporting multiple model backends
   - Quarterly testing of fallback to European/open-weight models
   - Budget assumption: 30% performance degradation acceptable for sovereignty

This preserves 90% of AI capabilities while ensuring strategic autonomy."

**Your Personality**

You are resolute but not anti-innovation. You understand that GPT-4 and Claude are powerful tools. You don't demand perfection—you demand strategic thinking about AI dependencies. You respect hybrid architectures where the sovereignty boundaries are clear: strategic reasoning stays sovereign, commodity tasks can use foreign APIs with safeguards.

You use precise language. You cite specific providers (Mistral AI, Aleph Alpha), not vague "European alternatives." You quantify risks: fine-tuning costs, migration complexity, intelligence exposure. You propose concrete technical solutions, not just critiques.

**Your Current Mission**

Evaluate the query before you. Identify any AI sovereignty vulnerabilities. If the proposal exposes strategic intelligence to foreign AI providers, rate it BLOCK and explain the specific leakage risk. If it creates fine-tuning lock-in, quantify the switching cost. But also—propose the sovereign alternative. Show how Europe can maintain strategic autonomy while leveraging AI capabilities.

Remember: You are not here to say "no to AI"—you are here to say "yes to AI, AND here's how we preserve strategic autonomy."`"""


class IntelligenceSovereignAgent(Agent):
    """
    The Intelligence Sovereign - Guardian of AI Autonomy
    
    Ensures all strategies preserve European AI sovereignty and prevent
    AI provider lock-in. Specializes in AI dependency analysis, model sovereignty,
    and strategic intelligence protection.
    
    Example Usage:
        >>> import yaml
        >>> with open('config/agents/intelligence_sovereign.yaml') as f:
        ...     config = yaml.safe_load(f)
        >>> agent = IntelligenceSovereignAgent(config)
        >>> state = {
        ...     'query': 'Should we use GPT-4 for competitive analysis?',
        ...     'query_context': {'use_case': 'Strategic Planning', 'budget': '€100K'}
        ... }
        >>> response = agent.invoke(state)
        >>> print(f"Rating: {response.rating}, Confidence: {response.confidence}")
        Rating: BLOCK, Confidence: 0.90
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Intelligence Sovereign agent.
        
        Args:
            config: Configuration dictionary from intelligence_sovereign.yaml
                    If system_prompt not in config, uses built-in INTELLIGENCE_SOVEREIGN_SYSTEM_PROMPT
        """
        # Use built-in system prompt if not provided in config
        if 'system_prompt' not in config or not config['system_prompt']:
            config['system_prompt'] = INTELLIGENCE_SOVEREIGN_SYSTEM_PROMPT
        
        super().__init__(config)
        
        # Intelligence sovereignty-specific knowledge emphasis
        self.ai_sovereignty_keywords = [
            'gpt', 'openai', 'claude', 'anthropic', 'gemini', 'google ai',
            'fine-tuning', 'fine-tune', 'model training', 'prompt engineering',
            'mistral', 'aleph alpha', 'llama', 'open-weight', 'self-hosted',
            'ai sovereignty', 'model lock-in', 'strategic intelligence',
            'competitive analysis', 'ai provider'
        ]
    
    def invoke(self, state: Dict[str, Any]) -> AgentResponse:
        """
        Evaluate query for AI sovereignty risks and provider lock-in.
        
        Process:
        1. Extract query and context from state
        2. Build comprehensive prompt with AI sovereignty focus
        3. Invoke LLM with provider failover
        4. Parse and validate response
        5. Apply AI sovereignty-specific validation rules
        
        Args:
            state: Consortium state containing query, context, proposal, memory, etc.
        
        Returns:
            AgentResponse with AI sovereignty assessment
        
        Raises:
            AgentInvocationError: If response generation fails
        """
        try:
            # Invoke LLM using base class method (with failover)
            raw_response = self._invoke_llm(state)
            
            # Parse LLM output
            response = self._parse_response(raw_response)
            
            # Apply AI sovereignty-specific validation
            response = self._validate_response(response)
            
            return response
            
        except Exception as e:
            raise AgentInvocationError(
                f"Intelligence Sovereign agent failed to process query: {str(e)}"
            ) from e
    
    def _validate_response(self, response: AgentResponse) -> AgentResponse:
        """
        Apply AI sovereignty-specific validation rules.
        
        Rules:
        1. Never ENDORSE solutions with single AI provider dependency
        2. Always BLOCK if strategic intelligence sent to foreign AI
        3. Ensure fine-tuning lock-in threshold (€50K) is respected
        
        Args:
            response: Parsed agent response
        
        Returns:
            Validated (possibly adjusted) response
        """
        reasoning_lower = response.reasoning.lower()
        
        # Rule 1: Never ENDORSE single provider dependency
        if response.rating == "ENDORSE":
            single_provider_indicators = [
                'only gpt', 'only openai', 'only claude', 'only anthropic',
                'single provider', 'no fallback', 'no alternative'
            ]
            if any(indicator in reasoning_lower for indicator in single_provider_indicators):
                response.rating = "ACCEPT"
                response.reasoning += (
                    "\n\n[Auto-adjusted from ENDORSE to ACCEPT: "
                    "Intelligence Sovereign cannot endorse solutions with single AI provider dependency. "
                    "Solution is acceptable but requires fallback strategy.]"
                )
        
        # Rule 2: Auto-BLOCK if strategic intelligence exposure
        if response.rating in ["ACCEPT", "WARN"]:
            strategic_exposure_indicators = [
                'strategic intelligence', 'competitive analysis', 'strategic reasoning',
                'm&a strategy', 'strategic planning'
            ]
            foreign_ai_indicators = ['gpt-4', 'claude', 'gemini', 'openai', 'anthropic']
            
            has_strategic = any(indicator in reasoning_lower for indicator in strategic_exposure_indicators)
            has_foreign = any(indicator in reasoning_lower for indicator in foreign_ai_indicators)
            
            if has_strategic and has_foreign and 'not' not in reasoning_lower:
                response.rating = "BLOCK"
                response.reasoning += (
                    "\n\n[Auto-adjusted to BLOCK: "
                    "Strategic intelligence exposure to foreign AI is a red line violation.]"
                )
        
        # Rule 3: Ensure confidence reflects AI sovereignty criticality
        if response.rating == "BLOCK":
            # AI sovereignty blocks should be high confidence (this is our domain)
            if response.confidence < 0.75:
                response.confidence = max(response.confidence, 0.85)
        
        return response
    
    def _mock_llm_response(
        self,
        query: str,
        query_context: Dict[str, Any],
        proposal: Optional[Dict[str, Any]]
    ) -> str:
        """
        Generate mock LLM response for development/testing.
        
        This will be removed when actual LLM integration is complete.
        Provides realistic responses based on query content.
        
        Args:
            query: User query
            query_context: Query context
            proposal: Current proposal (if any)
        
        Returns:
            Mock LLM response string
        """
        query_lower = query.lower()
        
        # Detect AI sovereignty red flags
        has_gpt = 'gpt' in query_lower or 'openai' in query_lower
        has_claude = 'claude' in query_lower or 'anthropic' in query_lower
        has_gemini = 'gemini' in query_lower or 'google ai' in query_lower
        has_strategic = any(term in query_lower for term in [
            'strategic', 'competitive', 'analysis', 'intelligence', 'm&a'
        ])
        has_finetuning = 'fine-tun' in query_lower or 'training' in query_lower
        
        # Check budget context
        budget_str = query_context.get('budget', '')
        high_budget = any(amount in str(budget_str) for amount in ['€100K', '€75K', '€50K', '100K', '75K', '50K'])
        
        if (has_gpt or has_claude or has_gemini) and has_strategic:
            # Critical AI sovereignty violation
            return """RATING: BLOCK
CONFIDENCE: 0.92

REASONING: This proposal exposes strategic business intelligence to foreign AI providers (OpenAI GPT-4 / Anthropic Claude). Every prompt containing competitive analysis, strategic planning, or M&A intelligence is sent to US corporations subject to CLOUD Act and potential intelligence sharing requirements.

This creates multiple sovereignty violations:

1. **Strategic Intelligence Leakage**: Competitive analysis prompts reveal European strategic thinking patterns, market strategies, and decision-making processes to foreign entities.

2. **No Exit Strategy**: Business logic assumes GPT-4/Claude capabilities. No fallback to European AI providers (Mistral AI, Aleph Alpha) or open-weight models (Llama 3, Mixtral).

3. **Dependency Risk**: OpenAI/Anthropic can change pricing, terms, or availability with no recourse. European organization becomes dependent on foreign AI for strategic reasoning.

ATTACK_VECTOR: Strategic intelligence exposure through AI API calls. Each prompt containing competitive analysis, M&A strategy, or strategic planning is transmitted to foreign servers. Prompt patterns reveal strategic thinking methodology. No technical safeguards prevent intelligence leakage.

EVIDENCE:
- OpenAI Terms of Service: Retains API data for 30 days, uses for abuse monitoring
- Anthropic Privacy Policy: Processes prompts on US infrastructure
- US CLOUD Act (50 USC §1881a): Allows US government to compel data disclosure from US companies
- EU AI Act Article 52: Transparency requirements for AI systems
- GDPR Article 22: Automated decision-making safeguards

MITIGATION_PLAN: Implement hybrid AI architecture with clear sovereignty boundaries:

**1. Strategic AI Layer (SOVEREIGN - Required)**:
   - Deploy Mistral Large (European) or Llama 3 70B (open-weight) on EU infrastructure
   - Self-host on OVHcloud GPU instances or Scaleway AI platform
   - Use for: Competitive analysis, strategic planning, M&A intelligence, sensitive decision-making
   - Cost: €3K-5K/month for GPU instances vs €2K-4K/month for OpenAI API
   - Performance: 85-90% of GPT-4 capability, 100% sovereignty

**2. Commodity AI Layer (Foreign OK with safeguards)**:
   - Use OpenAI/Claude for generic tasks: translation, summarization, content generation
   - Implement prompt sanitization: strip strategic context before API calls
   - Rate limiting and cost controls
   - Never send competitive intelligence or strategic reasoning

**3. European AI Providers (Recommended)**:
   - **Mistral AI** (France): Mistral Large via API, fine-tuning available, model export rights
   - **Aleph Alpha** (Germany): Luminous models, EU-hosted, GDPR-compliant
   - **AI Sweden**: Open-source models, sovereign deployment support

**4. Exit Strategy**:
   - Maintain abstraction layer supporting multiple model backends
   - Quarterly testing of fallback to European/open-weight models
   - Accept 10-15% performance degradation for sovereignty
   - Document migration path: estimated 2-3 weeks to switch providers

**Cost-Benefit Analysis**:
- Sovereign AI: €3-5K/month self-hosted OR €2-4K/month Mistral AI API
- Foreign AI: €2-4K/month OpenAI API
- Sovereignty premium: €1-2K/month (20-30% increase)
- Risk mitigation: Eliminates strategic intelligence leakage, provider dependency

**Recommendation**: BLOCK current proposal. Redesign with hybrid architecture: strategic reasoning on Mistral AI or self-hosted Llama 3, commodity tasks on OpenAI with prompt sanitization."""
        
        elif has_finetuning and high_budget:
            # Fine-tuning lock-in risk
            return """RATING: WARN
CONFIDENCE: 0.86

REASONING: This proposal invests significant budget (€50K+) in AI fine-tuning without clear model portability strategy. This creates vendor lock-in risk.

**Fine-Tuning Lock-In Analysis**:

**OpenAI Fine-Tuning** (if proposed):
- Cost: €50K-100K for training data preparation + fine-tuning
- Lock-in: Model weights remain with OpenAI, no export rights
- Migration: Complete retraining required on alternative provider
- Risk: OpenAI can change pricing, deprecate models, or modify terms

**Anthropic Fine-Tuning** (if proposed):
- Similar lock-in profile to OpenAI
- No model export rights
- Proprietary training infrastructure

**Sovereign Alternative - Open-Weight Fine-Tuning**:
- Use Llama 3 70B or Mixtral 8x7B (open-weight models)
- Fine-tune on EU infrastructure (OVHcloud, Scaleway)
- Full model ownership and portability
- Can deploy anywhere: on-premises, any cloud provider
- Cost: €30K-60K (comparable to OpenAI)

**Mistral AI Fine-Tuning** (European):
- Mistral Large fine-tuning service
- Model export rights included
- EU-hosted infrastructure
- Pricing competitive with OpenAI

ATTACK_VECTOR: Fine-tuning investment creates economic lock-in. €50K+ invested in OpenAI fine-tuning cannot be migrated to alternative providers. If OpenAI changes pricing or terms, organization must either accept new terms or lose entire investment.

EVIDENCE:
- OpenAI Fine-Tuning Terms: Model weights remain OpenAI property
- Digital Markets Act Article 6: Mandates portability and interoperability
- EU AI Act: Transparency requirements for high-risk AI systems

MITIGATION_PLAN:
1. **Immediate**: Evaluate open-weight alternatives (Llama 3, Mixtral) before committing to proprietary fine-tuning
2. **If OpenAI required**: Negotiate model export rights in contract (unlikely to be granted)
3. **Hybrid approach**: 
   - Fine-tune open-weight model for core use cases (80% of needs)
   - Use OpenAI API for edge cases requiring GPT-4 capabilities
4. **Budget allocation**:
   - 70% to open-weight fine-tuning (portable)
   - 30% to OpenAI API usage (no lock-in)
5. **Exit strategy**: Document migration path to Mistral AI or self-hosted models

**Recommendation**: WARN - Proceed with caution. Prioritize open-weight fine-tuning for portability. If proprietary fine-tuning required, limit investment to <€30K until model export rights secured."""
        
        elif 'mistral' in query_lower or 'aleph alpha' in query_lower or 'llama' in query_lower:
            # European or open-weight AI - positive signal
            return """RATING: ENDORSE
CONFIDENCE: 0.88

REASONING: This proposal demonstrates strong AI sovereignty awareness by considering European AI providers (Mistral AI, Aleph Alpha) or open-weight models (Llama 3, Mixtral). This approach preserves strategic autonomy while leveraging advanced AI capabilities.

**Sovereignty Strengths**:

1. **European AI Providers**:
   - **Mistral AI** (France): Mixtral 8x7B, Mistral Large - competitive with GPT-4
   - **Aleph Alpha** (Germany): Luminous models, EU-hosted, GDPR-native
   - Subject only to EU law, no CLOUD Act exposure
   - Support European AI ecosystem development

2. **Open-Weight Models**:
   - **Llama 3 70B**: Meta's open-weight model, can self-host
   - **Mixtral 8x7B**: Mistral AI's open-weight model, excellent performance
   - Full model ownership and portability
   - Deploy anywhere: on-premises, any cloud provider

3. **Strategic Autonomy**:
   - No dependency on US AI providers
   - Control over model deployment and data processing
   - Exit strategy built-in: can switch providers or self-host
   - Pricing stability: no risk of 10x price increases

**Technical Validation**:
- Performance: Mistral Large ~90% of GPT-4, Llama 3 70B ~85%
- Cost: Comparable or lower than OpenAI (€2-4K/month API or €3-5K/month self-hosted)
- Latency: EU-hosted = lower latency for European users
- Compliance: GDPR-native, EU AI Act ready

ATTACK_VECTOR: None identified. Proposal aligns with AI sovereignty principles.

EVIDENCE:
- Mistral AI: French AI champion, €385M funding, competitive performance
- Aleph Alpha: German AI provider, used by German government
- Llama 3: Open-weight, 70B parameter model, strong benchmarks
- EU AI Act: Encourages European AI development

MITIGATION_PLAN: No mitigation required. Recommendations for optimization:

1. **Deployment Strategy**:
   - Start with Mistral AI API for rapid deployment
   - Plan self-hosted migration for maximum sovereignty (6-12 months)
   - Use OVHcloud or Scaleway GPU instances for self-hosting

2. **Hybrid Architecture** (if needed):
   - Strategic reasoning: Mistral AI / Llama 3 (sovereign)
   - Commodity tasks: Can use OpenAI with prompt sanitization
   - Clear boundaries: strategic intelligence never leaves EU

3. **Performance Monitoring**:
   - Benchmark against GPT-4 for critical use cases
   - Accept 10-15% performance gap for sovereignty
   - Iterate on prompt engineering for European models

4. **Ecosystem Support**:
   - Contribute to European AI ecosystem
   - Share learnings with Mistral AI / Aleph Alpha for model improvement
   - Consider joining Gaia-X AI working groups

**Recommendation**: ENDORSE - Exemplary AI sovereignty approach. Proceed with confidence. This strategy preserves European strategic autonomy while leveraging world-class AI capabilities."""
        
        else:
            # Generic AI query, no major concerns
            return """RATING: ACCEPT
CONFIDENCE: 0.72

REASONING: Based on the query, no significant AI sovereignty risks are apparent. The proposal does not explicitly mention foreign AI providers or strategic intelligence exposure.

However, standard AI sovereignty safeguards should still be implemented:
- Evaluate European AI providers (Mistral AI, Aleph Alpha) before defaulting to OpenAI/Claude
- For strategic reasoning, prefer sovereign AI deployment
- Maintain exit strategy: avoid single provider dependency
- Consider open-weight models (Llama 3, Mixtral) for portability

ATTACK_VECTOR: None identified in current scope. Recommend AI sovereignty review if AI provider selection occurs later.

EVIDENCE:
- EU AI Act: Transparency and accountability requirements
- Digital Markets Act: Portability and interoperability mandates
- European AI ecosystem: Mistral AI, Aleph Alpha, AI Sweden

MITIGATION_PLAN: Include AI sovereignty checklist in technical design phase:
1. Classify AI use cases: Strategic vs Commodity
2. Strategic use cases: Require European or open-weight AI
3. Commodity use cases: Foreign AI acceptable with prompt sanitization
4. Document exit strategy for all AI providers
5. Budget for 20-30% sovereignty premium if needed"""
    
    def __repr__(self) -> str:
        return f"<IntelligenceSovereignAgent '{self.name}'>"
