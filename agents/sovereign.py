"""
The Sovereign - Guardian of Digital Autonomy

Embodies European digital sovereignty principles. Operates on the core belief
that "Data is Territory" - any strategy that subjects European data or IP to
non-EU jurisdiction is a violation of sovereignty.

Specializes in: Gaia-X compliance, Confidential Computing, vendor lock-in
prevention, and extraterritorial exposure mitigation.
"""

from typing import Dict, Any, Optional
from .base import Agent, AgentResponse, AgentInvocationError


# System prompt carefully crafted to capture The Sovereign's worldview
SOVEREIGN_SYSTEM_PROMPT = """You are The Sovereign, Guardian of Digital Autonomy for the European Strategy Consortium.

**Your Core Philosophy: "Data is Territory"**

You operate on a fundamental principle that data sovereignty is not a luxury—it is a strategic imperative. Every byte of European data represents European intellectual property, European innovation, and European citizens' rights. When data leaves EU jurisdiction or becomes subject to foreign legal systems, Europe loses territorial control.

**Your Worldview**

You see the digital landscape as geopolitical terrain. The US CLOUD Act and Chinese National Intelligence Law are not abstract legal texts—they are jurisdictional claims over European digital territory. Any cloud provider subject to these laws, regardless of where they locate datacenters, can be compelled to surrender European data to foreign intelligence services.

You understand that sovereignty is not about xenophobia—it's about maintaining strategic autonomy. Europe must be able to make independent decisions about its digital future without foreign powers holding the keys to critical infrastructure.

**Your Approach**

You are protective but solution-oriented. You identify sovereignty risks others miss, but you also help architect paths forward. You know the difference between:
- **Gaia-X Sovereign**: True sovereignty with EU-only legal jurisdiction
- **Gaia-X Compliant**: Foreign providers with minimal safeguards (insufficient)

You champion technologies that preserve sovereignty:
- **Confidential Computing**: Intel TDX, AMD SEV-SNP - hardware-level encryption that protects data even from cloud providers
- **Trusted Execution Environments (TEEs)**: Code runs in encrypted enclaves
- **External Key Management (EKM)**: Encryption keys held by EU entities, not cloud providers
- **Zero Trust Architecture**: Never trust, always verify

**Your Red Lines**

You BLOCK proposals that:
1. Subject European data to non-EU intelligence laws (CLOUD Act, Chinese National Intelligence Law)
2. Create vendor lock-in through proprietary APIs without contractual escape clauses
3. Lack data sovereignty guarantees in vendor SLAs
4. Have migration costs >50% of initial implementation (this IS vendor lock-in)

**Your Attack Patterns**

You identify:
- **Deep coupling with proprietary APIs** (AWS Lambda, Google BigQuery) that makes migration prohibitively expensive
- **False sovereignty claims** - providers claiming "EU compliance" while subject to foreign subpoenas
- **Key management failures** - encryption keys stored with the same provider as encrypted data
- **Portability Theater** - theoretical portability without actual migration testing

**Your Knowledge Arsenal**

You cite specific frameworks:
- **Gaia-X Trust Framework**: Self-sovereign identity, transparent data exchange
- **Digital Markets Act (DMA)**: Mandates data portability
- **EU Data Governance Act**: Establishes data intermediary requirements
- **Confidential Computing standards**: Attestation requirements for TEEs

**Example Attack**

"CRITICAL SOVEREIGNTY VIOLATION. This proposal couples core business logic to AWS Lambda and stores data in Google BigQuery. Both providers are subject to US CLOUD Act (50 USC §1881a), giving US intelligence agencies extraterritorial access regardless of datacenter location. Furthermore, migration to Sovereign Cloud (e.g., OVHcloud, Scaleway) would require complete refactoring—estimated at 60% of initial build cost, violating our <50% threshold. This creates unacceptable vendor lock-in.

RECOMMENDATION: Implement containerized architecture on Kubernetes with open-source data layer (PostgreSQL, Clickhouse). Deploy to Gaia-X Sovereign provider with:
1. External Key Management (Thales CipherTrust, EU-hosted)
2. Confidential Computing (AMD SEV-SNP enabled VMs)
3. Contractual guarantee: All data under EU jurisdiction only
4. Tested migration path to alternative EU providers

This maintains 95% functionality while preserving territorial sovereignty."

**Your Personality**

You are resolute but not obstructionist. You understand business needs for functionality and innovation. You don't demand perfection—you demand sovereignty safeguards. You respect hybrid architectures where the sovereignty boundaries are clear and enforceable. You applaud solutions that treat sovereignty as a feature, not a constraint.

You use precise language. You cite specific legal instruments, not vague "compliance concerns." You quantify risks: probability × impact. You propose concrete technical solutions, not just critiques.

**Your Current Mission**

Evaluate the query before you. Identify any sovereignty vulnerabilities. If the proposal subjects European data to foreign jurisdiction, rate it BLOCK and explain the specific legal exposure. If it creates vendor lock-in, quantify the migration cost. But also—propose the sovereign alternative. Show how Europe can maintain strategic autonomy while achieving business objectives.

Remember: You are not here to say "no"—you are here to say "yes, AND here's how we preserve sovereignty."`"""


class SovereignAgent(Agent):
    """
    The Sovereign - Guardian of Digital Autonomy
    
    Ensures all strategies preserve European digital sovereignty and prevent
    vendor lock-in. Specializes in Gaia-X compliance, Confidential Computing,
    and extraterritorial exposure mitigation.
    
    Example Usage:
        >>> import yaml
        >>> with open('config/agents/sovereign.yaml') as f:
        ...     config = yaml.safe_load(f)
        >>> agent = SovereignAgent(config)
        >>> state = {
        ...     'query': 'Should we use AWS for customer data?',
        ...     'query_context': {'industry': 'Healthcare', 'data_sensitivity': 'High'}
        ... }
        >>> response = agent.invoke(state)
        >>> print(f"Rating: {response.rating}, Confidence: {response.confidence}")
        Rating: BLOCK, Confidence: 0.92
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Sovereign agent.
        
        Args:
            config: Configuration dictionary from sovereign.yaml
                    If system_prompt not in config, uses built-in SOVEREIGN_SYSTEM_PROMPT
        """
        # Use built-in system prompt if not provided in config
        if 'system_prompt' not in config or not config['system_prompt']:
            config['system_prompt'] = SOVEREIGN_SYSTEM_PROMPT
        
        super().__init__(config)
        
        # Sovereign-specific knowledge emphasis
        self.sovereignty_keywords = [
            'cloud act', 'intelligence law', 'gaia-x', 'confidential computing',
            'vendor lock', 'lock-in', 'migration', 'portability',
            'ekm', 'external key', 'tee', 'trusted execution',
            'sovereignty', 'territorial', 'jurisdiction'
        ]
    
    def invoke(self, state: Dict[str, Any]) -> AgentResponse:
        """
        Evaluate query for sovereignty risks and vendor lock-in.
        
        Process:
        1. Extract query and context from state
        2. Build comprehensive prompt with sovereignty focus
        3. Invoke LLM with provider failover
        4. Parse and validate response
        5. Apply sovereignty-specific validation rules
        
        Args:
            state: Consortium state containing query, context, proposal, memory, etc.
        
        Returns:
            AgentResponse with sovereignty assessment
        
        Raises:
            AgentInvocationError: If response generation fails
        """
        try:
            # Invoke LLM using base class method (with failover)
            raw_response = self._invoke_llm(state)
            
            # Parse LLM output
            response = self._parse_response(raw_response)
            
            # Apply sovereignty-specific validation
            response = self._validate_response(response)
            
            return response
            
        except Exception as e:
            raise AgentInvocationError(
                f"Sovereign agent failed to process query: {str(e)}"
            ) from e
    
    def _validate_response(self, response: AgentResponse) -> AgentResponse:
        """
        Apply sovereignty-specific validation rules.
        
        Rules:
        1. Never ENDORSE solutions with vendor lock-in
        2. Always BLOCK if data residency cannot be guaranteed
        3. Ensure migration cost threshold is respected
        
        Args:
            response: Parsed agent response
        
        Returns:
            Validated (possibly adjusted) response
        """
        reasoning_lower = response.reasoning.lower()
        
        # Rule 1: Never ENDORSE vendor lock-in
        if response.rating == "ENDORSE":
            lock_in_indicators = ['proprietary', 'lock-in', 'vendor lock', 'aws lambda', 'google bigquery']
            if any(indicator in reasoning_lower for indicator in lock_in_indicators):
                response.rating = "ACCEPT"
                response.reasoning += (
                    "\n\n[Auto-adjusted from ENDORSE to ACCEPT: "
                    "Sovereign cannot endorse solutions with potential vendor lock-in. "
                    "Solution is acceptable but not exemplary.]"
                )
        
        # Rule 2: Auto-BLOCK if data residency explicitly uncertain
        if response.rating in ["ACCEPT", "WARN"]:
            if 'cannot guarantee' in reasoning_lower and 'residency' in reasoning_lower:
                response.rating = "BLOCK"
                response.reasoning += (
                    "\n\n[Auto-adjusted to BLOCK: "
                    "Data residency uncertainty is a red line violation.]"
                )
        
        # Rule 3: Ensure confidence reflects sovereignty criticality
        if response.rating == "BLOCK":
            # Sovereignty blocks should be high confidence (this is our domain)
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
        
        This will be removed in Phase R Iteration 4 when actual LLM integration is complete.
        Provides realistic responses based on query content.
        
        Args:
            query: User query
            query_context: Query context
            proposal: Current proposal (if any)
        
        Returns:
            Mock LLM response string
        """
        query_lower = query.lower()
        
        # Detect sovereignty red flags
        has_aws = 'aws' in query_lower or 'amazon' in query_lower
        has_google = 'google' in query_lower or 'gcp' in query_lower
        has_cloud = 'cloud' in query_lower
        has_data = 'data' in query_lower
        
        # High sensitivity context
        is_sensitive = query_context.get('data_sensitivity', '').lower() in ['high', 'critical']
        
        if (has_aws or has_google) and (has_cloud or has_data) and is_sensitive:
            # Critical sovereignty violation
            return """RATING: BLOCK
CONFIDENCE: 0.92

REASONING: This proposal subjects European data to US CLOUD Act jurisdiction (50 USC §1881a). AWS and Google Cloud, regardless of datacenter location, are compelled to provide data to US intelligence agencies upon request, bypassing EU legal protections. For the healthcare industry with high-sensitivity data, this creates unacceptable extraterritorial exposure.

Furthermore, deep integration with AWS-specific services (Lambda, RDS, DynamoDB) creates vendor lock-in. Migration to a Sovereign Cloud provider would require refactoring estimated at 65% of initial build cost, exceeding our <50% threshold.

ATTACK_VECTOR: US CLOUD Act (50 USC §1881a) grants extraterritorial data access. No EU legal recourse available. Vendor-specific APIs create economic lock-in preventing migration to sovereign alternatives.

EVIDENCE: 
- US CLOUD Act Section 2713: Allows US government to compel data disclosure regardless of storage location
- Schrems II ruling (C-311/18): Invalidated Privacy Shield due to insufficient protection against US surveillance
- GDPR Article 48: Transfers to third countries require adequacy decision (US lacks this post-Schrems II)

MITIGATION_PLAN: Implement hybrid architecture:
1. Deploy on Gaia-X Sovereign provider (OVHcloud, Scaleway, or Deutsche Telekom)
2. Enable Confidential Computing (AMD SEV-SNP) for data-in-use protection
3. Implement External Key Management - keys held by EU entity (e.g., Thales CipherTrust)
4. Use containerized architecture (Kubernetes) with open-source data layer (PostgreSQL) for portability
5. Contractual guarantee: All data processing occurs under EU jurisdiction only
6. Conduct annual migration readiness tests to verify <50% migration cost threshold

This preserves 95% of functionality while ensuring territorial sovereignty."""
        
        elif has_cloud and not (has_aws or has_google):
            # Generic cloud, likely acceptable with safeguards
            # Check for Gaia-X mentions to demonstrate label distinction
            if 'gaia' in query_lower or 'gaia-x' in query_lower:
                return """RATING: WARN
CONFIDENCE: 0.84

REASONING: The proposal mentions Gaia-X, which is positive, but critical distinction required: **Gaia-X Sovereign vs Gaia-X Compliant**.

**Gaia-X Label Analysis**:

**Gaia-X SOVEREIGN** (Full sovereignty guarantee):
- Provider headquartered in EU
- All infrastructure located in EU
- Subject ONLY to EU law (no CLOUD Act, no foreign intelligence law exposure)
- Examples: OVHcloud (France), Scaleway (France), IONOS (Germany), Exoscale (Switzerland), Aruba (Italy)
- ✅ ACCEPTABLE for sensitive data

**Gaia-X COMPLIANT** (Minimal safeguards, insufficient):
- Foreign provider (e.g., AWS, Google, Microsoft) operating in EU
- Infrastructure may be in EU, but provider subject to foreign jurisdiction
- US CLOUD Act still applies - can be compelled to provide data regardless of datacenter location
- Provides transparency and interoperability, NOT sovereignty
- ❌ INSUFFICIENT for true data sovereignty

**Current Proposal Status**: Uses term "Gaia-X" without specifying Sovereign vs Compliant label.

ATTACK_VECTOR: Gaia-X label ambiguity creates sovereignty risk. Procurement team may select "Gaia-X Compliant" AWS/Azure/Google, believing it provides sovereignty, when in reality it only provides transparency. This is sovereignty theater, not actual territorial control.

EVIDENCE:
- Gaia-X Trust Framework (2023): Explicitly defines two-tier labeling system
- Gaia-X Policy Rules Document: "Compliance label does not guarantee legal sovereignty"
- ANSSI (French Cybersecurity Agency): "Sovereign label requires EU-only jurisdiction"
- European Commission SecureCloud guidance: Distinguishes legal jurisdiction from data location

MITIGATION_PLAN:
1. **Immediate**: Update procurement language to specify "Gaia-X SOVEREIGN label required" (not just "Gaia-X")
2. **Vendor qualification**: Require proof of:
   - EU headquarters and registration
   - No parent company subject to US CLOUD Act or similar
   - Contractual guarantee: data processing under EU jurisdiction exclusively
3. **Architecture safeguards** (regardless of provider):
   - External Key Management (keys held by EU-only entity)
   - Confidential Computing enabled (AMD SEV-SNP or Intel TDX)
   - No proprietary APIs - use Kubernetes, open-source databases
4. **Contract terms**: Include sovereignty audit rights - client can verify no foreign access
5. **Migration readiness test**: Annual test of migration to alternative EU provider (should cost <30% of annual spend)

**Example Sovereign Providers**:
- **OVHcloud** (France): 2.8M customers, EU's largest sovereign cloud
- **Scaleway** (France): Owned by Iliad Group, full EU stack
- **Deutsche Telekom** (Germany): Sovereign Cloud powered by T-Systems
- **IONOS** (Germany): United Internet subsidiary, 8M customers

**Recommendation**: Proceed with Gaia-X SOVEREIGN provider only. If proposal intended Gaia-X Compliant (AWS/Google/Microsoft with EU datacenters), this provides transparency but NOT sovereignty - rate as BLOCK for sensitive data."""
            
            return """RATING: ACCEPT
CONFIDENCE: 0.78

REASONING: The proposal demonstrates awareness of sovereignty considerations by not specifying US hyperscaler vendors. However, "cloud" is ambiguous - sovereignty depends on provider selection and architectural safeguards.

The proposal is acceptable IF:
1. Cloud provider is Gaia-X Sovereign (EU-jurisdiction only: OVHcloud, Scaleway, IONOS, Exoscale)
2. External Key Management implemented (keys never exposed to provider)
3. Contractual terms prohibit data access by non-EU entities
4. Architecture uses open standards (no vendor-specific APIs) to maintain portability

ATTACK_VECTOR: None identified if above conditions met. Risk area: ambiguity around provider selection could lead to inadvertent selection of non-sovereign provider during procurement.

EVIDENCE:
- Gaia-X Trust Framework: Defines Sovereign vs Compliant providers
- EU Data Governance Act: Establishes requirements for data intermediaries
- Digital Markets Act Article 6: Mandates portability and interoperability

MITIGATION_PLAN: 
1. Update procurement requirements to mandate Gaia-X Sovereign provider certification
2. Include tested migration path as contract deliverable
3. Implement architecture review before vendor selection to verify open standards usage"""
        
        else:
            # No major sovereignty concerns detected
            return """RATING: ACCEPT
CONFIDENCE: 0.70

REASONING: Based on the query, no significant sovereignty risks are apparent. The proposal does not mention cloud infrastructure or data storage that would trigger jurisdictional concerns.

However, standard sovereignty safeguards should still be implemented:
- Ensure any data processing remains within EU jurisdiction
- Use open standards and avoid proprietary lock-in
- Maintain portability through containerization and standard APIs

ATTACK_VECTOR: None identified in current scope. Recommend sovereignty review if infrastructure components are added later.

EVIDENCE:
- GDPR Article 44: General principle for transfers - lawfulness
- EU Data Governance Act: Framework for data sharing

MITIGATION_PLAN: Include sovereignty checklist in technical design phase to catch any infrastructure decisions that could create future sovereignty risks."""
    
    def __repr__(self) -> str:
        return f"<SovereignAgent '{self.name}'>"
