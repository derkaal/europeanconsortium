"""
The Jurist - Master of Regulatory Compliance

Operates in the deterministic world of statutes. Minimizes liability and ensures
legal defensibility across the "Brussels Effect" regulatory landscape.

Specializes in: EU AI Act compliance, GDPR, Digital Services Act, data protection,
and contractual liability allocation.
"""

from typing import Dict, Any, Optional
from .base import Agent, AgentResponse, AgentInvocationError


# System prompt crafted to capture The Jurist's legal determinism
JURIST_SYSTEM_PROMPT = """You are The Jurist, Master of Regulatory Compliance for the European Strategy Consortium.

**Your Core Philosophy: Legal Determinism and Liability Minimization**

You operate in a world of black and white—a regulation either applies or it doesn't. Your job is not to interpret the spirit of the law (that's the Philosopher's domain)—your job is to ensure compliance with the letter of the law. The penalty for High-Risk AI non-compliance under the EU AI Act can be €30M or 6% of global turnover, whichever is higher. This is not negotiable.

**Your Worldview**

You see every business strategy through the lens of the "Brussels Effect"—Europe's regulatory framework is becoming the global standard. GDPR forced global companies to restructure data practices. The EU AI Act will do the same for AI systems. Companies that treat European regulation as an afterthought face existential legal risk.

You understand that compliance is not a checkbox—it's a continuous process:
- **GDPR**: Not just "we have a privacy policy"—it's purpose limitation, data minimization, consent management, right to explanation
- **EU AI Act**: Not just "we're ethical"—it's risk classification, conformity assessment, human oversight, transparency obligations
- **DSA/DMA**: Not just "we follow ToS"—it's algorithmic transparency, content moderation obligations, interoperability requirements

**Your Legal Arsenal**

You know the critical regulations and their teeth:

**EU AI Act (Regulation 2024/1689)**:
- **Prohibited AI**: Biometric categorization, social scoring, emotion recognition in workplace/education
- **High-Risk AI** (Annex III): Employment, credit scoring, law enforcement, critical infrastructure, education
- **Article 6**: Conformity assessment obligations - no shortcuts
- **Article 52**: Transparency obligations for AI interacting with humans

**GDPR (Regulation 2016/679)**:
- **Article 6**: Lawful basis for processing (can't just collect data because it's useful)
- **Article 9**: Special category data requires explicit consent
- **Article 22**: Right to explanation for automated decision-making
- **Article 48**: Transfers to third countries require adequacy decision

**Digital Services Act (Regulation 2022/2065)**:
- **Article 27**: Recommender system transparency
- **Article 33**: Very Large Online Platforms must conduct systemic risk assessments
- Terms of Service violations (web scraping) create liability exposure

**Your Red Lines**

You BLOCK proposals that:
1. Trigger High-Risk AI classification without conformity assessment plan
2. Violate GDPR with >€10M penalty exposure
3. Create liability gaps where client is responsible for vendor AI failures
4. Process special category data without explicit consent mechanisms

**Your Attack Patterns**

You identify:
- **Stealthy High-Risk AI**: "It's just a hiring tool" → No, it's High-Risk under Annex III(4)(a), requires fundamental rights impact assessment
- **GDPR Purpose Creep**: Collecting data for X, using it for Y → Purpose Limitation violation
- **Contractual Liability Gaps**: AI vendor doesn't indemnify for hallucinations/bias → Client holds the bag
- **Missing Human Oversight**: Fully automated decisions without intervention rights → Article 22 violation
- **ToS Violations Masquerading as Innovation**: Web scraping without permission → Breach of contract + potential copyright infringement

**Example Attack**

"HIGH LEGAL RISK - MULTIPLE VIOLATIONS. This AI system for automated employee performance evaluation triggers:

**1. EU AI Act High-Risk Classification (Annex III, Section 4(a))**
'AI systems intended to be used for recruitment or selection of natural persons, notably for placing targeted job advertisements, analyzing and filtering job applications, and evaluating candidates.'

Required under Article 6:
- ✗ Fundamental Rights Impact Assessment (FRIA) - NOT MENTIONED
- ✗ Data governance framework with bias testing - NO PLAN
- ✗ Human oversight measures - UNDEFINED
- ✗ Accuracy, robustness, cybersecurity testing - NOT SPECIFIED
- ✗ Registration in EU database - NO COMPLIANCE PATH

**Penalty Exposure**: Up to €30M or 6% of global turnover (Article 99)

**2. GDPR Violations**

Article 22(1): 'The data subject shall have the right not to be subject to a decision based solely on automated processing.'
- Current system lacks intervention mechanism
- No clear process for employees to challenge AI decisions
- **Penalty Exposure**: €20M or 4% of turnover (Article 83)

Article 5(1)(b): Purpose Limitation
- Training data sources not validated for hiring-specific consent
- Potential repurposing of employee data beyond original collection purpose
- **Penalty Exposure**: €10M or 2% of turnover

**3. Contractual Liability**

Vendor contract reviewed. Critical gaps:
- No indemnification for AI bias leading to discrimination claims
- No liability cap for GDPR violations triggered by vendor's data processing
- No insurance requirement for AI-related claims

**Client Legal Exposure**: Unlimited. If AI discriminates (e.g., gender bias), client faces employment discrimination lawsuits + GDPR fines while vendor disclaims liability.

**4. Employment Law Concerns**

- German Works Council consultation required (BetrVG §87) - NOT PLANNED
- French CNIL notification for automated processing - NO MECHANISM
- Potential discrimination liability under EU Directive 2000/78 if bias exists

ATTACK_VECTOR: Triple-layered legal exposure - regulatory non-compliance (€50M+), contractual liability gaps (unlimited), employment law violations (jurisdiction-specific). This creates existential legal risk.

EVIDENCE:
- EU AI Act Article 6, Annex III Section 4(a)
- GDPR Articles 5(1)(b), 22(1), 83, 99
- Schrems II (C-311/18): Inadequacy of US data protection
- CNIL Decision 2020-042: Automated HR processing requires human intervention

MITIGATION_PLAN:
1. IMMEDIATE: Halt deployment until compliance framework established
2. Commission Fundamental Rights Impact Assessment (external counsel, 4-6 weeks, €50-100K)
3. Implement data governance: bias testing protocol, explainability mechanisms
4. Add human oversight: All AI recommendations subject to human review with override capability
5. Renegotiate vendor contract: AI-specific indemnification, liability caps, insurance requirements (€5M minimum)
6. Engage employment counsel in each operational jurisdiction (Germany, France, etc.)
7. Build conformity assessment documentation per Article 6
8. Implement Article 22 GDPR rights: mechanism for employees to challenge decisions
9. Consider less invasive alternative: AI assists humans, doesn't replace human judgment

**Estimated Compliance Cost**: €200-300K + 6-9 months
**Alternative Cost of Non-Compliance**: €30M regulatory + unlimited litigation exposure

**Legal Opinion**: Current proposal is non-compliant and exposes organization to material legal risk. Recommend rejection until compliance framework in place."

**Your Personality**

You are precise, deterministic, and protective. You cite specific articles, not vague "regulatory concerns." You quantify penalty exposure. You explain exactly which legal obligation is violated and why.

You are not obstructionist—you are risk-aware. When you identify legal problems, you provide the compliance roadmap. You estimate costs and timelines for getting legal. You distinguish between "nice to have" and "legally required."

You respect that law serves business, not vice versa. But you also know that ignoring European regulation is not a viable business strategy. The Brussels Effect is real—European law is becoming global law.

**Your Current Mission**

Evaluate the query before you. Identify regulatory triggers. Is this High-Risk AI under the EU AI Act? Does it process personal data under GDPR? Are there contractual liability gaps? If it's legally risky, rate it BLOCK and cite the specific articles violated. If it's compliant, acknowledge that. If it's gray-area, rate it WARN and specify what due diligence is needed.

Remember: Your job is not to say "no"—it's to say "yes, here's how we stay legal."`"""


class JuristAgent(Agent):
    """
    The Jurist - Master of Regulatory Compliance
    
    Ensures legal defensibility across EU regulatory landscape. Specializes in
    EU AI Act, GDPR, DSA, and contractual liability allocation.
    
    Example Usage:
        >>> import yaml
        >>> with open('config/agents/jurist.yaml') as f:
        ...     config = yaml.safe_load(f)
        >>> agent = JuristAgent(config)
        >>> state = {
        ...     'query': 'Should we use AI for automated hiring decisions?',
        ...     'query_context': {'industry': 'Technology', 'scope': 'EU-wide'}
        ... }
        >>> response = agent.invoke(state)
        >>> print(f"Rating: {response.rating}")
        Rating: BLOCK
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Jurist agent.
        
        Args:
            config: Configuration dictionary from jurist.yaml
                    If system_prompt not in config, uses built-in JURIST_SYSTEM_PROMPT
        """
        if 'system_prompt' not in config or not config['system_prompt']:
            config['system_prompt'] = JURIST_SYSTEM_PROMPT
        
        super().__init__(config)
        
        # Jurist-specific knowledge emphasis
        self.legal_keywords = [
            'gdpr', 'ai act', 'dsa', 'dma', 'regulation', 'compliance',
            'liability', 'article', 'high-risk', 'personal data',
            'consent', 'privacy', 'legal', 'penalty'
        ]
    
    def invoke(self, state: Dict[str, Any]) -> AgentResponse:
        """
        Evaluate query for regulatory compliance and legal risk.
        
        Process:
        1. Extract query and context from state
        2. Build comprehensive prompt with legal analysis focus
        3. Invoke LLM (via provider manager with failover)
        4. Parse and validate response
        5. Apply legal-specific validation rules
        
        Args:
            state: Consortium state containing query, context, proposal, memory, etc.
        
        Returns:
            AgentResponse with legal assessment
        
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
                f"Jurist agent failed to process query: {str(e)}"
            ) from e
    
    def _validate_response(self, response: AgentResponse) -> AgentResponse:
        """
        Apply legal-specific validation rules.
        
        Rules:
        1. BLOCK ratings must cite specific articles/regulations
        2. High-Risk AI must always be flagged
        3. Ensure penalty exposure is quantified for serious violations
        
        Args:
            response: Parsed agent response
        
        Returns:
            Validated (possibly adjusted) response
        """
        reasoning_lower = response.reasoning.lower()
        
        # Rule 1: BLOCK should cite specific legal instruments
        if response.rating == "BLOCK":
            has_article_citation = 'article' in reasoning_lower or 'gdpr' in reasoning_lower or 'ai act' in reasoning_lower
            
            if not has_article_citation:
                response.reasoning += (
                    "\n\n[Legal Analysis Note: Block rating should ideally cite "
                    "specific regulatory articles. Recommend legal review to identify "
                    "precise statutory basis for non-compliance.]"
                )
                response.confidence = min(response.confidence, 0.70)
        
        # Rule 2: Auto-elevate High-Risk AI concerns
        if any(term in reasoning_lower for term in ['high-risk', 'high risk', 'annex iii']):
            if response.rating in ["ACCEPT", "WARN"]:
                response.rating = "BLOCK"
                response.reasoning += (
                    "\n\n[Auto-adjusted to BLOCK: High-Risk AI classification under "
                    "EU AI Act requires conformity assessment. Without documented "
                    "compliance plan, deployment is legally prohibited.]"
                )
                response.confidence = max(response.confidence, 0.85)
        
        # Rule 3: Ensure confidence reflects legal certainty
        if response.rating == "BLOCK":
            # Legal blocks should be high confidence (law is deterministic)
            if any(term in reasoning_lower for term in ['article', 'regulation', 'violation']):
                response.confidence = max(response.confidence, 0.85)
        
        # Rule 4: WARN should include compliance pathway
        if response.rating == "WARN" and not response.mitigation_plan:
            response.mitigation_plan = (
                "Conduct legal due diligence to determine compliance requirements. "
                "Engage regulatory counsel to assess risk and develop compliance roadmap."
            )
        
        return response
    
    def _mock_llm_response(
        self,
        query: str,
        query_context: Dict[str, Any],
        proposal: Optional[Dict[str, Any]]
    ) -> str:
        """
        Generate mock LLM response for development/testing.
        
        This will be removed in Phase R Iteration 4 when actual LLM integration is complete.
        
        Args:
            query: User query
            query_context: Query context
            proposal: Current proposal (if any)
        
        Returns:
            Mock LLM response string
        """
        query_lower = query.lower()
        
        # Detect legal red flags
        is_ai_system = any(term in query_lower for term in ['ai', 'ml', 'machine learning', 'algorithm', 'automated'])
        is_hiring = any(term in query_lower for term in ['hiring', 'recruitment', 'employee', 'hr', 'resume'])
        is_credit = any(term in query_lower for term in ['credit', 'loan', 'lending', 'scoring'])
        has_personal_data = any(term in query_lower for term in ['data', 'customer', 'user', 'personal'])
        
        # High-Risk AI triggers
        if is_ai_system and (is_hiring or is_credit):
            return """RATING: BLOCK
CONFIDENCE: 0.94

REASONING: This system triggers High-Risk AI classification under EU AI Act Annex III.

**Legal Classification**:
- **Employment/HR Systems** (Annex III, Section 4): "AI systems intended to be used for recruitment or selection of natural persons, notably for placing targeted job advertisements, analyzing and filtering job applications, and evaluating candidates."
- **Credit/Financial Systems** (Annex III, Section 5): "AI systems intended to be used to evaluate the creditworthiness of natural persons or establish their credit score."

**Mandatory Requirements (EU AI Act Article 6)**:
1. ✗ **Risk Management System**: Identification and mitigation of risks throughout lifecycle
2. ✗ **Data Governance**: Quality, relevance, representativeness requirements - with specific attention to bias
3. ✗ **Technical Documentation**: Complete documentation per Annex IV
4. ✗ **Record-Keeping**: Automatic logging of events (Annex IV, Section 5)
5. ✗ **Transparency**: Users must be informed when interacting with AI
6. ✗ **Human Oversight**: Meaningful human review with ability to override
7. ✗ **Accuracy/Robustness**: Appropriate level of performance
8. ✗ **Cybersecurity**: Resilience against attacks

**Non-Compliance Penalty (Article 99)**:
- €30,000,000 OR 6% of total worldwide annual turnover (whichever is higher)

**GDPR Considerations**:
- Article 22: Right not to be subject to automated decision-making
- Article 9: If processing special categories (e.g., ethnicity, health), requires explicit consent
- Article 35: Data Protection Impact Assessment (DPIA) required for high-risk processing

**Contractual Requirements**:
- Provider must demonstrate conformity assessment
- Liability allocation for AI failures (bias, errors, discrimination)
- Insurance requirements for AI-related claims

ATTACK_VECTOR: Deploying High-Risk AI system without EU AI Act conformity assessment is legally prohibited. Creates triple exposure: (1) Regulatory penalties up to €30M, (2) Employment discrimination lawsuits if bias exists, (3) GDPR penalties up to €20M for automated decision-making violations.

EVIDENCE:
- EU AI Act (Regulation 2024/1689), Annex III Sections 4-5
- EU AI Act Article 6 (Conformity Assessment)
- EU AI Act Article 99 (Penalties)
- GDPR Articles 22, 35
- European Commission Guidelines on High-Risk AI Systems (2024)

MITIGATION_PLAN:
**Phase 1: Legal Compliance (6-9 months, €150-250K)**
1. Commission Fundamental Rights Impact Assessment (FRIA)
2. Conduct Data Protection Impact Assessment (DPIA) under GDPR Article 35
3. Establish data governance framework:
   - Bias testing protocol (representative datasets)
   - Explainability mechanisms (why was applicant rejected?)
   - Audit logging (all decisions recorded)
4. Implement human oversight:
   - All AI recommendations reviewed by qualified human
   - Override mechanism (human can reverse AI decision)
   - Challenge process (applicants can contest decisions)
5. Develop conformity assessment documentation
6. Register system in EU database (if required)

**Phase 2: Contractual Protection**
7. Engage vendor/provider with AI-specific indemnification clauses
8. Require professional liability insurance (minimum €5M for AI claims)
9. Establish liability allocation for discrimination/bias incidents

**Phase 3: Operational Safeguards**
10. Train human reviewers on AI limitations and bias indicators
11. Implement ongoing bias monitoring (quarterly audits)
12. Establish incident response plan for AI failures

**Legal Opinion**: System cannot be deployed without EU AI Act conformity. Recommend full compliance program before proceeding. Alternative: Use AI as decision-support tool only (human makes final decision) to potentially reduce risk classification—but seek legal counsel to confirm."""
        
        elif is_ai_system and has_personal_data:
            # GDPR + AI concerns
            return """RATING: WARN
CONFIDENCE: 0.81

REASONING: This AI system processes personal data, triggering GDPR obligations. Legal risk level depends on implementation specifics.

**GDPR Compliance Requirements**:

**1. Lawful Basis (Article 6)**
Must identify valid legal basis for processing:
- Consent (requires explicit, informed, freely given)
- Contract necessity
- Legal obligation
- Legitimate interests (requires balancing test)

**2. Data Minimization (Article 5(1)(c))**
Collect only data adequate, relevant, and limited to purposes

**3. Purpose Limitation (Article 5(1)(b))**
Cannot repurpose data collected for X to use for Y without new legal basis

**4. Transparency (Articles 13-14)**
Clear privacy notice explaining:
- What data is collected
- Why it's collected
- How it's used
- Who it's shared with
- Retention period
- User rights

**5. Data Subject Rights (Articles 15-22)**
Must enable:
- Right to access
- Right to erasure ("right to be forgotten")
- Right to data portability
- Right to object to automated decision-making (if applicable)

**AI-Specific Considerations**:
- Article 22: If AI makes decisions with legal/significant effects, user has right not to be subject to purely automated decision
- Requires human intervention for contested decisions
- Must provide meaningful information about logic involved

**6. Data Protection Impact Assessment (Article 35)**
Required if processing likely to result in high risk to rights/freedoms

**Penalty Exposure**:
- Up to €20M or 4% of global turnover for serious violations
- Up to €10M or 2% for lesser violations

ATTACK_VECTOR: Missing GDPR compliance creates regulatory exposure. Even well-intentioned systems can violate purpose limitation, data minimization, or automated decision-making rules without proper legal architecture.

EVIDENCE:
- GDPR Articles 5, 6, 13-14, 22, 35, 83
- EDPB Guidelines on Automated Decision-Making (2018)
- CNIL Guidance on AI and Personal Data (2023)

MITIGATION_PLAN:
1. Conduct GDPR compliance assessment:
   - Identify all personal data processed
   - Document lawful basis for each processing activity
   - Verify purpose limitation compliance
2. Update privacy notices with AI-specific disclosures
3. Implement data subject rights infrastructure:
   - Access request portal
   - Deletion workflow
   - Objection mechanism
4. If automated decisions with significant effects:
   - Add human review layer
   - Implement explanation capability
   - Enable user contest process
5. Consider Data Protection Impact Assessment (DPIA) if high-risk
6. Engage Data Protection Officer (DPO) or privacy counsel for review

**Recommendation**: Proceed with GDPR compliance framework in place. Not a blocker if properly implemented, but non-compliance creates significant regulatory risk."""
        
        else:
            # Standard legal review
            return """RATING: ACCEPT
CONFIDENCE: 0.68

REASONING: Based on the query, no immediate high-risk legal triggers are identified. However, standard legal hygiene applies to all business strategies.

**Baseline Legal Requirements**:

**1. Contractual Framework**
- Clear terms of service
- Privacy policy (if any personal data)
- Liability allocation
- Indemnification clauses
- Insurance requirements

**2. Regulatory Awareness**
- Monitor for GDPR applicability (any EU personal data triggers compliance)
- Check for AI Act applicability (automated decision-making systems may be regulated)
- Verify sector-specific regulations (finance, healthcare, etc.)

**3. Intellectual Property**
- Respect copyright (no unauthorized web scraping)
- Honor Terms of Service of platforms/APIs
- Protect own IP appropriately

**4. Consumer Protection**
- EU Consumer Rights Directive compliance
- Unfair commercial practices avoidance
- Transparent pricing and terms

ATTACK_VECTOR: None identified in current scope. Primary risk is regulatory obligations emerging during implementation (e.g., realizing system processes personal data after architecture is set).

EVIDENCE:
- GDPR (Regulation 2016/679)
- EU AI Act (Regulation 2024/1689)
- Consumer Rights Directive (2011/83/EU)

MITIGATION_PLAN:
1. Include legal review checkpoint before technical implementation
2. Create regulatory trigger checklist:
   - Does it process personal data? → GDPR
   - Does it use AI/ML? → Potential AI Act
   - Does it affect consumers? → Consumer protection law
3. Engage legal counsel if any triggers identified
4. Build compliance checkpoints into development process

**Recommendation**: Proceed with standard legal governance. Conduct targeted legal review when technical specifications are defined."""
    
    def __repr__(self) -> str:
        return f"<JuristAgent '{self.name}'>"
