"""Competitive Advantage Agent (Feature 6).

Transforms regulatory constraints into competitive advantages through pattern matching.

The Alchemist's insight: "One firm's regulation is another firm's moat."

Examples:
- GDPR data residency → "European data haven" brand
- AI Act transparency → "Explainable AI" differentiator
- Carbon reporting → "Green tech leader" positioning
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AdvantagePattern:
    """Pattern for transforming constraint into advantage."""

    constraint_domain: str  # e.g., "GDPR", "AI Act", "Carbon"
    constraint_keywords: List[str]  # Keywords to match in proposal
    advantage_type: str  # e.g., "Brand", "Market", "Technical", "Operational"
    advantage_template: str  # Template for advantage description
    evidence_keywords: List[str]  # What to look for in evidence
    applicability_conditions: Dict[str, Any]  # When this pattern applies


# ==============================================================================
# ADVANTAGE PATTERN LIBRARY
# ==============================================================================

ADVANTAGE_PATTERNS = [
    # GDPR / Data Privacy Patterns
    AdvantagePattern(
        constraint_domain="GDPR",
        constraint_keywords=["GDPR", "data protection", "privacy", "consent", "data residency"],
        advantage_type="Brand",
        advantage_template="Position as 'European Data Haven' - trustworthy alternative to US cloud providers",
        evidence_keywords=["EU data centers", "data sovereignty", "GDPR compliance", "privacy-first"],
        applicability_conditions={"markets": ["EU"], "industry": ["Technology", "Cloud"]}
    ),
    AdvantagePattern(
        constraint_domain="GDPR",
        constraint_keywords=["right to explanation", "transparency", "data portability"],
        advantage_type="Technical",
        advantage_template="Build 'Privacy by Design' as core differentiator - superior data controls",
        evidence_keywords=["user controls", "data export", "transparency dashboard"],
        applicability_conditions={"markets": ["EU"], "industry": ["SaaS", "Technology"]}
    ),

    # AI Act Patterns
    AdvantagePattern(
        constraint_domain="AI Act",
        constraint_keywords=["AI Act", "high-risk AI", "transparency", "explainability"],
        advantage_type="Technical",
        advantage_template="Lead with 'Explainable AI' - transparency as competitive edge over black-box models",
        evidence_keywords=["model cards", "audit logs", "explainability", "transparency"],
        applicability_conditions={"markets": ["EU"], "industry": ["AI", "ML", "Technology"]}
    ),
    AdvantagePattern(
        constraint_domain="AI Act",
        constraint_keywords=["human oversight", "human-in-the-loop", "AI governance"],
        advantage_type="Operational",
        advantage_template="Offer 'Governed AI' service - managed compliance as premium tier",
        evidence_keywords=["oversight", "governance", "compliance service", "managed AI"],
        applicability_conditions={"markets": ["EU"], "industry": ["AI", "Cloud"]}
    ),
    AdvantagePattern(
        constraint_domain="AI Act",
        constraint_keywords=["conformity assessment", "certification", "CE marking"],
        advantage_type="Market",
        advantage_template="Early mover advantage - be first to market with certified AI products",
        evidence_keywords=["certification", "early compliance", "first mover"],
        applicability_conditions={"markets": ["EU"], "regulatory_status": ["early"]}
    ),

    # Carbon / Sustainability Patterns
    AdvantagePattern(
        constraint_domain="Carbon",
        constraint_keywords=["carbon", "emissions", "sustainability", "energy efficiency", "green"],
        advantage_type="Brand",
        advantage_template="Position as 'Green Tech Leader' - climate-conscious alternative",
        evidence_keywords=["carbon neutral", "renewable energy", "green cloud", "sustainability"],
        applicability_conditions={"markets": ["EU", "Global"], "industry": ["Technology", "Cloud"]}
    ),
    AdvantagePattern(
        constraint_domain="Carbon",
        constraint_keywords=["carbon reporting", "SCI", "emissions disclosure"],
        advantage_type="Operational",
        advantage_template="Offer 'Carbon-Aware Computing' - operational efficiency differentiator",
        evidence_keywords=["carbon tracking", "efficiency", "optimization"],
        applicability_conditions={"markets": ["EU"], "industry": ["Cloud", "Technology"]}
    ),

    # Consumer Protection Patterns
    AdvantagePattern(
        constraint_domain="Consumer Protection",
        constraint_keywords=["dark patterns", "consumer rights", "accessibility", "fairness"],
        advantage_type="Brand",
        advantage_template="Lead with 'Ethical UX' - no dark patterns, user-first design",
        evidence_keywords=["ethical design", "user-first", "accessibility", "fair"],
        applicability_conditions={"markets": ["EU"], "industry": ["SaaS", "Consumer"]}
    ),
    AdvantagePattern(
        constraint_domain="Consumer Protection",
        constraint_keywords=["price transparency", "clear pricing", "no hidden fees"],
        advantage_type="Market",
        advantage_template="Compete on 'Radical Transparency' - simple pricing vs competitor complexity",
        evidence_keywords=["transparent pricing", "simple pricing", "no fees"],
        applicability_conditions={"markets": ["EU", "Global"], "industry": ["SaaS", "FinTech"]}
    ),

    # Data Sovereignty Patterns
    AdvantagePattern(
        constraint_domain="Data Sovereignty",
        constraint_keywords=["data sovereignty", "CLOUD Act", "foreign access", "Gaia-X"],
        advantage_type="Market",
        advantage_template="Target 'Sovereignty-Sensitive' sectors - government, defense, critical infrastructure",
        evidence_keywords=["sovereignty", "local control", "EU-only", "Gaia-X"],
        applicability_conditions={"markets": ["EU"], "industry": ["Cloud", "Government", "Defense"]}
    ),

    # Open Source / Transparency Patterns
    AdvantagePattern(
        constraint_domain="Transparency",
        constraint_keywords=["open source", "transparency", "auditability", "open weights"],
        advantage_type="Technical",
        advantage_template="Leverage 'Open Source Trust' - auditable models vs proprietary black boxes",
        evidence_keywords=["open source", "open weights", "auditable", "community"],
        applicability_conditions={"markets": ["Global"], "industry": ["AI", "ML"]}
    ),
]


# ==============================================================================
# COMPETITIVE ADVANTAGE AGENT
# ==============================================================================

class CompetitiveAdvantageAgent:
    """Agent that identifies competitive advantages from regulatory constraints.

    Pattern-based approach:
    1. Scan proposal for constraint keywords
    2. Match against advantage pattern library
    3. Check applicability conditions (market, industry, etc.)
    4. Generate advantage recommendations
    5. Prioritize by relevance and feasibility
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize advantage agent.

        Args:
            config: Optional configuration dict
        """
        self.config = config or {}
        self.patterns = ADVANTAGE_PATTERNS
        self.min_keyword_matches = self.config.get("min_keyword_matches", 1)
        self.enabled = self.config.get("enabled", True)

    def analyze(
        self,
        proposal: str,
        context: Dict[str, Any],
        agent_responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze proposal and identify competitive advantages.

        Args:
            proposal: Original user query/proposal
            context: Query context (markets, industry, etc.)
            agent_responses: Agent responses with concerns and evidence

        Returns:
            Dict with advantages, opportunities, and recommendations
        """
        if not self.enabled:
            return {"advantages": [], "opportunities": [], "recommendations": []}

        # Extract constraints from agent responses
        constraints = self._extract_constraints(agent_responses)

        # Match constraints against patterns
        matched_patterns = self._match_patterns(
            proposal=proposal,
            context=context,
            constraints=constraints
        )

        # Generate advantage recommendations
        advantages = self._generate_advantages(matched_patterns, context)

        # Prioritize by relevance and feasibility
        prioritized = self._prioritize_advantages(advantages, context)

        return {
            "advantages": prioritized,
            "opportunities": self._generate_opportunities(prioritized),
            "recommendations": self._generate_recommendations(prioritized),
            "pattern_matches": len(matched_patterns),
            "total_advantages": len(advantages)
        }

    def _extract_constraints(
        self,
        agent_responses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract regulatory constraints from agent responses.

        Args:
            agent_responses: Agent responses

        Returns:
            List of constraint dicts
        """
        constraints = []

        for response in agent_responses:
            agent_name = response.get("agent_name", "")
            reasoning = response.get("reasoning", "")
            concerns = response.get("concerns", [])

            # Jurist constraints (GDPR, AI Act, etc.)
            if "jurist" in agent_name.lower():
                for concern in concerns:
                    constraints.append({
                        "source": "Jurist",
                        "domain": self._classify_constraint_domain(concern),
                        "description": concern,
                        "severity": response.get("rating", 5)
                    })

            # Ecosystem constraints (Carbon, sustainability)
            if "ecosystem" in agent_name.lower():
                for concern in concerns:
                    constraints.append({
                        "source": "Ecosystem",
                        "domain": "Carbon",
                        "description": concern,
                        "severity": response.get("rating", 5)
                    })

            # Philosopher constraints (Ethics, fairness)
            if "philosopher" in agent_name.lower():
                for concern in concerns:
                    constraints.append({
                        "source": "Philosopher",
                        "domain": "Consumer Protection",
                        "description": concern,
                        "severity": response.get("rating", 5)
                    })

        return constraints

    def _classify_constraint_domain(self, concern: str) -> str:
        """Classify constraint into domain.

        Args:
            concern: Concern text

        Returns:
            Domain string
        """
        concern_lower = concern.lower()

        if any(kw in concern_lower for kw in ["gdpr", "privacy", "data protection"]):
            return "GDPR"
        elif any(kw in concern_lower for kw in ["ai act", "high-risk", "explainability"]):
            return "AI Act"
        elif any(kw in concern_lower for kw in ["carbon", "sustainability", "emissions"]):
            return "Carbon"
        elif any(kw in concern_lower for kw in ["dark pattern", "consumer", "accessibility"]):
            return "Consumer Protection"
        elif any(kw in concern_lower for kw in ["sovereignty", "cloud act", "gaia-x"]):
            return "Data Sovereignty"
        else:
            return "General"

    def _match_patterns(
        self,
        proposal: str,
        context: Dict[str, Any],
        constraints: List[Dict[str, Any]]
    ) -> List[AdvantagePattern]:
        """Match constraints against advantage patterns.

        Args:
            proposal: Proposal text
            context: Query context
            constraints: Extracted constraints

        Returns:
            List of matched patterns
        """
        matched = []

        proposal_lower = proposal.lower()

        for pattern in self.patterns:
            # Check keyword matches in proposal
            keyword_matches = sum(
                1 for kw in pattern.constraint_keywords
                if kw.lower() in proposal_lower
            )

            # Also check constraints
            constraint_matches = sum(
                1 for c in constraints
                if c["domain"] == pattern.constraint_domain
            )

            total_matches = keyword_matches + constraint_matches

            if total_matches >= self.min_keyword_matches:
                # Check applicability conditions
                if self._check_applicability(pattern, context):
                    matched.append(pattern)

        return matched

    def _check_applicability(
        self,
        pattern: AdvantagePattern,
        context: Dict[str, Any]
    ) -> bool:
        """Check if pattern applies to this context.

        Args:
            pattern: Advantage pattern
            context: Query context

        Returns:
            True if pattern applies
        """
        conditions = pattern.applicability_conditions

        # Check markets
        if "markets" in conditions:
            target_markets = context.get("target_markets", [])
            if isinstance(target_markets, str):
                target_markets = [target_markets]

            # Check if any target market matches pattern markets
            pattern_markets = conditions["markets"]

            # Handle "EU" special case
            if "EU" in pattern_markets:
                eu_countries = {"germany", "france", "spain", "italy", "netherlands",
                               "poland", "belgium", "austria", "sweden", "denmark"}
                target_markets_lower = [m.lower() for m in target_markets]
                if any(m in eu_countries for m in target_markets_lower):
                    return True

            # Check direct matches
            if not any(m in pattern_markets for m in target_markets):
                if "Global" not in pattern_markets:
                    return False

        # Check industry
        if "industry" in conditions:
            industry = context.get("industry", "").lower()
            pattern_industries = [i.lower() for i in conditions["industry"]]

            if not any(ind in industry for ind in pattern_industries):
                return False

        return True

    def _generate_advantages(
        self,
        matched_patterns: List[AdvantagePattern],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate advantage recommendations from matched patterns.

        Args:
            matched_patterns: Matched patterns
            context: Query context

        Returns:
            List of advantage dicts
        """
        advantages = []

        for pattern in matched_patterns:
            advantage = {
                "constraint_domain": pattern.constraint_domain,
                "advantage_type": pattern.advantage_type,
                "description": pattern.advantage_template,
                "evidence_keywords": pattern.evidence_keywords,
                "relevance_score": self._calculate_relevance(pattern, context)
            }
            advantages.append(advantage)

        return advantages

    def _calculate_relevance(
        self,
        pattern: AdvantagePattern,
        context: Dict[str, Any]
    ) -> float:
        """Calculate relevance score for advantage.

        Args:
            pattern: Advantage pattern
            context: Query context

        Returns:
            Relevance score (0.0-1.0)
        """
        score = 0.5  # Base score

        # Boost for exact industry match
        industry = context.get("industry", "").lower()
        if "industry" in pattern.applicability_conditions:
            pattern_industries = [i.lower() for i in pattern.applicability_conditions["industry"]]
            if any(ind in industry for ind in pattern_industries):
                score += 0.3

        # Boost for market match
        target_markets = context.get("target_markets", [])
        if isinstance(target_markets, str):
            target_markets = [target_markets]

        if "markets" in pattern.applicability_conditions:
            pattern_markets = pattern.applicability_conditions["markets"]
            if any(m in pattern_markets for m in target_markets):
                score += 0.2

        return min(score, 1.0)

    def _prioritize_advantages(
        self,
        advantages: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Prioritize advantages by relevance and type.

        Args:
            advantages: List of advantages
            context: Query context

        Returns:
            Sorted list of advantages
        """
        # Sort by relevance score, then by type priority
        type_priority = {
            "Market": 1,    # Highest priority - direct revenue impact
            "Brand": 2,     # Strong - long-term value
            "Technical": 3, # Medium - differentiation
            "Operational": 4  # Lower - internal efficiency
        }

        sorted_advantages = sorted(
            advantages,
            key=lambda a: (
                -a["relevance_score"],
                type_priority.get(a["advantage_type"], 5)
            )
        )

        return sorted_advantages

    def _generate_opportunities(
        self,
        advantages: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate opportunity statements from advantages.

        Args:
            advantages: Prioritized advantages

        Returns:
            List of opportunity strings
        """
        opportunities = []

        for adv in advantages[:3]:  # Top 3
            opp = f"{adv['advantage_type']} Opportunity: {adv['description']}"
            opportunities.append(opp)

        return opportunities

    def _generate_recommendations(
        self,
        advantages: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations.

        Args:
            advantages: Prioritized advantages

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if not advantages:
            return ["No competitive advantages identified from current constraints"]

        # Group by type
        by_type = {}
        for adv in advantages:
            adv_type = adv["advantage_type"]
            if adv_type not in by_type:
                by_type[adv_type] = []
            by_type[adv_type].append(adv)

        # Generate recommendations per type
        if "Market" in by_type:
            recommendations.append(
                f"Market positioning: Leverage {len(by_type['Market'])} market "
                f"advantage(s) in go-to-market strategy"
            )

        if "Brand" in by_type:
            recommendations.append(
                f"Brand strategy: Develop {len(by_type['Brand'])} brand "
                f"differentiator(s) in messaging and positioning"
            )

        if "Technical" in by_type:
            recommendations.append(
                f"Product strategy: Build {len(by_type['Technical'])} technical "
                f"differentiator(s) into product roadmap"
            )

        if "Operational" in by_type:
            recommendations.append(
                f"Operations: Develop {len(by_type['Operational'])} operational "
                f"advantage(s) as service offerings"
            )

        return recommendations
