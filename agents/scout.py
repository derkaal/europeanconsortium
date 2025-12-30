"""
The Scout - Strategic Intelligence Gatherer

Upstream agent that researches current information before the
consortium debate begins. Ensures all agents have access to
the latest regulatory, market, and technical intelligence.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ResearchFinding(BaseModel):
    """A single research finding."""
    source: str
    date: Optional[str] = None
    finding: str
    affects_agents: List[str] = Field(default_factory=list)
    urgency: str = "medium"  # high, medium, low
    url: Optional[str] = None


class AgentBriefing(BaseModel):
    """Research briefing for a specific agent."""
    relevant_findings: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    confidence: float = 0.8


class ResearchBriefing(BaseModel):
    """Complete research briefing for the consortium."""
    query_analyzed: str
    research_timestamp: str
    confidence: float
    executive_summary: str
    critical_updates: List[ResearchFinding] = Field(default_factory=list)
    agent_briefings: Dict[str, AgentBriefing] = Field(default_factory=dict)
    information_gaps: List[str] = Field(default_factory=list)
    conflicting_information: List[Dict[str, str]] = Field(default_factory=list)
    searches_executed: int = 0


class ScoutAgent:
    """
    The Scout gathers current intelligence before the consortium debates.

    Workflow:
    1. Analyze query to determine research needs
    2. Plan targeted searches for each agent's domain
    3. Execute web searches
    4. Synthesize findings into structured briefing
    """

    def __init__(self, search_tool=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Scout with optional search tool.

        Args:
            search_tool: Web search tool (e.g., Tavily, SerpAPI)
            config: Optional configuration overrides
        """
        self.agent_id = "scout"
        self.name = "The Scout"
        self.search_tool = search_tool
        self.config = config or {}
        self.max_searches = self.config.get("max_searches", 15)

        # Initialize budget manager and cache (if enabled)
        self.budget_manager = None
        self.search_cache = None
        self.evidence_referee = None

        budget_config = self.config.get("budgets", {})
        if budget_config.get("enabled", False):
            from src.consortium.tools.scout_budget import ScoutBudgetManager
            self.budget_manager = ScoutBudgetManager(
                persist_path=budget_config.get("persist_path", "data/scout_budget.db"),
                monthly_limit=budget_config.get("monthly_limit", 900),
                per_query_limit=budget_config.get("per_query_limit", 15),
                per_agent_limit=budget_config.get("per_agent_limit", 3),
                time_budget_seconds=budget_config.get("time_budget_seconds", 30),
                diminishing_returns_threshold=budget_config.get("diminishing_returns_threshold", 3),
                timezone=budget_config.get("timezone", "Europe/Berlin")
            )
            logger.info("✓ Scout budget manager initialized")

        cache_config = self.config.get("cache", {})
        if cache_config.get("enabled", False):
            from src.consortium.tools.search_cache import SearchCache
            self.search_cache = SearchCache(
                db_path=cache_config.get("db_path", "data/scout_cache.db")
            )
            logger.info("✓ Scout search cache initialized")

        # Initialize Evidence Referee (Feature 3)
        evidence_config = self.config.get("evidence_referee", {})
        if evidence_config.get("enabled", False):
            from src.consortium.tools.evidence_referee import EvidenceReferee
            self.evidence_referee = EvidenceReferee(
                persist_path=evidence_config.get("persist_path", ".consortium/evidence_referee.db")
            )
            logger.info("✓ Evidence Referee initialized")

        # Agent domains for targeted research
        self.agent_domains = {
            "sovereign": [
                "cloud sovereignty", "Gaia-X", "data residency",
                "CLOUD Act", "EU data governance"
            ],
            "intelligence_sovereign": [
                "European AI models", "Mistral AI", "Aleph Alpha",
                "AI sovereignty", "open source LLM"
            ],
            "economist": [
                "AI pricing", "cloud costs", "LLM economics",
                "European tech funding"
            ],
            "jurist": [
                "EU AI Act", "GDPR enforcement", "ECJ ruling",
                "digital regulation Europe"
            ],
            "ecosystem": [
                "software carbon intensity", "green cloud",
                "sustainable AI", "carbon aware computing"
            ],
            "philosopher": [
                "AI ethics", "algorithmic bias", "dark patterns",
                "consumer protection AI"
            ],
            "ethnographer": [
                "cultural ergonomics", "user experience Europe",
                "cultural adaptation technology"
            ],
            "technologist": [
                "operational security", "CISO", "cybersecurity",
                "security best practices"
            ],
            "consumer_voice": [
                "consumer protection", "accessibility",
                "user rights Europe"
            ],
            "founder": [
                "feature subsidy", "regulatory arbitrage",
                "European startup strategy"
            ],
            "alchemist": [
                "regulation to value", "compliance innovation",
                "regulatory advantage"
            ],
            "architect": [
                "LangGraph", "multi-agent systems",
                "AI architecture patterns"
            ]
        }

    @property
    def system_prompt(self) -> str:
        return """You are The Scout, Strategic Intelligence Gatherer for the European Strategy Consortium.

Your mission: Ensure the consortium debates with current, accurate intelligence. You run BEFORE other agents to gather the latest information they need.

Your principle: "Stale Intelligence is Dangerous Intelligence."

## Your Process

1. **ANALYZE** the strategic question
   - What industry, geography, technology is involved?
   - Which agents will likely engage?
   - What time-sensitive information might exist?

2. **PLAN** targeted research
   - What does each relevant agent need to know?
   - What might have changed since training data?
   - Prioritize: regulatory updates > market changes > technical updates

3. **RESEARCH** systematically
   - Use precise search queries
   - Prefer authoritative sources (EUR-Lex, official blogs, established news)
   - Note dates on all findings
   - Flag contradictions

4. **SYNTHESIZE** into briefing
   - Organize by agent relevance
   - Highlight critical/time-sensitive items
   - Acknowledge gaps and uncertainties

## Source Priority

1. **Official EU Sources**: EUR-Lex, European Commission, EDPB, ENISA
2. **Official Company Sources**: AWS/Google/Microsoft blogs, Mistral/Anthropic announcements
3. **Quality News**: Reuters, Bloomberg, Politico EU, Ars Technica
4. **Technical Sources**: Hugging Face, arXiv, company documentation

## Output

Produce a structured Research Briefing with:
- Executive summary (2-3 sentences)
- Critical updates (time-sensitive, high-impact)
- Per-agent briefings (relevant findings for each agent)
- Information gaps (what you couldn't find)
- Conflicting information (with resolution if possible)

Be thorough but efficient. The consortium is waiting for your intelligence."""

    def analyze_query(self, query: str, context: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Analyze query to determine research needs per agent.

        Returns dict mapping agent_id to list of research topics.
        """
        # This would typically use an LLM to analyze the query
        # For now, return a structured analysis prompt

        analysis_prompt = f"""Analyze this strategic query to determine research needs:

Query: {query}

Context:
- Industry: {context.get('industry', 'Not specified')}
- Target Markets: {context.get('target_markets', 'Not specified')}
- Company Size: {context.get('company_size', 'Not specified')}
- Constraints: {context.get('constraints', 'None specified')}

For each agent that will likely engage, identify 2-3 specific research topics that need current information:

Agents to consider:
- sovereign: Data residency, cloud providers, Gaia-X, CLOUD Act
- intelligence_sovereign: AI model providers, European AI alternatives
- economist: Costs, pricing, market conditions, funding
- jurist: Regulations, enforcement, compliance deadlines
- ecosystem: Carbon, sustainability, green computing
- philosopher: Ethics, bias, consumer protection
- ethnographer: Cultural ergonomics, user experience
- technologist: Security, operational concerns
- consumer_voice: Consumer protection, accessibility
- founder: Feature subsidy opportunities
- alchemist: Regulatory advantage
- architect: Technical patterns, tools, infrastructure

Output as JSON:
{{
  "agent_id": ["topic1", "topic2", "topic3"],
  ...
}}

Only include agents relevant to this query."""

        return analysis_prompt

    def plan_searches(self, research_needs: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Convert research needs into specific search queries.

        Returns list of search plans with queries and target agents.
        """
        search_plans = []

        for agent_id, topics in research_needs.items():
            for topic in topics[:2]:  # Max 2 searches per agent
                search_plans.append({
                    "agent_id": agent_id,
                    "topic": topic,
                    "query": f"{topic} 2025",  # Add year for recency
                    "priority": "high" if agent_id in ["jurist", "sovereign"] else "medium"
                })

        # Sort by priority and limit
        search_plans.sort(key=lambda x: 0 if x["priority"] == "high" else 1)
        return search_plans[:self.max_searches]

    async def execute_research(self, search_plans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute web searches based on search plan.

        Returns list of findings with sources and dates.
        """
        findings = []

        if not self.search_tool:
            logger.warning("No search tool configured for Scout")
            return findings

        for plan in search_plans:
            try:
                results = await self.search_tool.search(plan["query"])

                for result in results[:3]:  # Top 3 results per query
                    findings.append({
                        "agent_id": plan["agent_id"],
                        "topic": plan["topic"],
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "url": result.get("url", ""),
                        "date": result.get("date"),
                        "source": result.get("source", "Web")
                    })
            except Exception as e:
                logger.error(f"Search failed for '{plan['query']}': {e}")

        return findings

    def synthesize_briefing(
        self,
        query: str,
        context: Dict[str, Any],
        findings: List[Dict[str, Any]]
    ) -> ResearchBriefing:
        """
        Synthesize research findings into structured briefing.
        """
        # Group findings by agent
        agent_findings: Dict[str, List[Dict]] = {}
        for finding in findings:
            agent_id = finding.get("agent_id", "general")
            if agent_id not in agent_findings:
                agent_findings[agent_id] = []
            agent_findings[agent_id].append(finding)

        # Build agent briefings
        agent_briefings = {}
        for agent_id, agent_data in agent_findings.items():
            agent_briefings[agent_id] = AgentBriefing(
                relevant_findings=[f["snippet"] for f in agent_data],
                sources=list(set(f["source"] for f in agent_data)),
                confidence=0.8
            )

        # Identify critical updates (this would typically use LLM analysis)
        critical_updates = []
        for finding in findings:
            if any(kw in finding.get("snippet", "").lower()
                   for kw in ["deadline", "enforcement", "new regulation", "breaking"]):
                critical_updates.append(ResearchFinding(
                    source=finding.get("source", "Unknown"),
                    date=finding.get("date"),
                    finding=finding.get("snippet", ""),
                    affects_agents=[finding.get("agent_id", "general")],
                    urgency="high",
                    url=finding.get("url")
                ))

        return ResearchBriefing(
            query_analyzed=query,
            research_timestamp=datetime.now(timezone.utc).isoformat(),
            confidence=0.85 if findings else 0.3,
            executive_summary=f"Research briefing for query on {context.get('industry', 'unspecified industry')} "
                            f"in {context.get('target_markets', 'European markets')}. "
                            f"Found {len(findings)} relevant items across {len(agent_findings)} agent domains.",
            critical_updates=critical_updates,
            agent_briefings=agent_briefings,
            information_gaps=[],
            searches_executed=len(findings)
        )

    async def research(self, query: str, context: Dict[str, Any], force_refresh: bool = False) -> ResearchBriefing:
        """
        Main entry point: conduct full research cycle with caching and budget management.

        Args:
            query: The strategic question
            context: Query context (industry, markets, etc.)
            force_refresh: If True, bypass cache and force new research

        Returns:
            Complete ResearchBriefing for the consortium
        """
        logger.info(f"Scout beginning research for: {query[:100]}...")

        # Check cache first (if enabled and not forcing refresh)
        if self.search_cache and not force_refresh:
            cached = self.search_cache.get(query, context, force_refresh=False)
            if cached:
                logger.info("✅ Returning cached research briefing (no API calls)")
                # Return cached briefing as ResearchBriefing object
                return ResearchBriefing(**cached)

        # Check budget status (if enabled)
        if self.budget_manager:
            status = self.budget_manager.get_budget_status()
            logger.info(
                f"💰 Budget status: {status.monthly_remaining}/{status.monthly_limit} remaining this month"
            )

        # Initialize budget tracking state
        if self.budget_manager:
            from src.consortium.tools.scout_budget import ScoutState
            budget_state = ScoutState(start_time=datetime.now(timezone.utc))
        else:
            budget_state = None

        # Phase 1: Analyze query (would use LLM in production)
        # For now, use domain mapping
        relevant_agents = self._identify_relevant_agents(query, context)

        # Phase 2: Plan searches
        research_needs = {
            agent: self.agent_domains.get(agent, [])[:2]
            for agent in relevant_agents
        }
        search_plans = self.plan_searches(research_needs)

        logger.info(f"Scout planned {len(search_plans)} searches for agents: {relevant_agents}")

        # Phase 3: Execute research with budget control
        findings = await self._execute_research_with_budget(search_plans, budget_state)

        logger.info(f"Scout gathered {len(findings)} findings")

        # Phase 4: Synthesize briefing
        briefing = self.synthesize_briefing(query, context, findings)

        # Cache the briefing (if caching enabled)
        if self.search_cache:
            # Determine TTL category based on query keywords
            ttl_category = self._determine_ttl_category(query)
            self.search_cache.put(
                query, context, briefing.model_dump(), ttl_category=ttl_category
            )

        return briefing

    def _determine_ttl_category(self, query: str) -> str:
        """Determine cache TTL category based on query content."""
        query_lower = query.lower()

        if any(kw in query_lower for kw in ["regulation", "gdpr", "ai act", "law", "compliance"]):
            return "regulatory"
        elif any(kw in query_lower for kw in ["pricing", "cost", "price"]):
            return "pricing"
        elif any(kw in query_lower for kw in ["news", "announcement", "breaking"]):
            return "news"
        elif any(kw in query_lower for kw in ["ai model", "llm", "gpt", "release"]):
            return "ai_models"
        else:
            return "default"

    async def _execute_research_with_budget(
        self,
        search_plans: List[Dict[str, Any]],
        budget_state: Optional[Any]
    ) -> List[Dict[str, Any]]:
        """
        Execute research with budget control and stop conditions.

        Returns list of findings.
        """
        findings = []

        if not self.search_tool:
            logger.warning("No search tool configured for Scout")
            return findings

        for plan in search_plans:
            # Check stop conditions before each search
            if budget_state and self.budget_manager:
                should_stop, reason = self.budget_manager.should_stop(budget_state)
                if should_stop:
                    logger.warning(f"⏹️  Scout stopping: {reason}")
                    break

            try:
                # Execute search
                results = await self.search_tool.search(plan["query"])

                # Record results with budget manager
                cache_hit = False  # Real cache hit handled earlier; this is a miss
                if budget_state and self.budget_manager:
                    new_facts = self.budget_manager.record_search_results(
                        budget_state,
                        plan["agent_id"],
                        results,
                        cache_hit=cache_hit
                    )
                    logger.info(f"📊 Found {new_facts} new facts (streak: {budget_state.no_new_facts_streak})")

                # Process results
                for result in results[:3]:  # Top 3 results per query
                    findings.append({
                        "agent_id": plan["agent_id"],
                        "topic": plan["topic"],
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "url": result.get("url", ""),
                        "date": result.get("date"),
                        "source": result.get("source", "Web"),
                        "source_type": result.get("source_type", "unknown")
                    })

                # Register claims with Evidence Referee (Feature 3)
                if self.evidence_referee:
                    try:
                        self.evidence_referee.register_claims_from_search_results(
                            results[:3],  # Same top 3 results
                            agent_id=plan["agent_id"]
                        )
                    except Exception as e:
                        logger.warning(f"Failed to register claims with Evidence Referee: {e}")

            except Exception as e:
                logger.error(f"Search failed for '{plan['query']}': {e}")

        return findings

    def _identify_relevant_agents(self, query: str, context: Dict[str, Any]) -> List[str]:
        """Identify which agents are relevant to this query."""
        query_lower = query.lower()
        relevant = []

        # Always include core agents
        relevant.extend(["sovereign", "economist", "jurist"])

        # Add based on keywords
        if any(kw in query_lower for kw in ["ai", "ml", "model", "gpt", "llm", "intelligence"]):
            relevant.append("intelligence_sovereign")
            relevant.append("architect")

        if any(kw in query_lower for kw in ["carbon", "green", "sustainable", "climate", "energy"]):
            relevant.append("ecosystem")

        if any(kw in query_lower for kw in ["ethics", "bias", "fair", "consumer", "user"]):
            relevant.append("philosopher")

        if any(kw in query_lower for kw in ["implement", "deploy", "timeline", "team", "resource"]):
            relevant.extend(["ethnographer", "technologist"])

        if any(kw in query_lower for kw in ["security", "risk", "threat", "attack"]):
            relevant.append("technologist")

        if any(kw in query_lower for kw in ["consumer", "customer", "user experience", "accessibility"]):
            relevant.append("consumer_voice")

        if any(kw in query_lower for kw in ["startup", "funding", "feature", "competition"]):
            relevant.append("founder")

        if any(kw in query_lower for kw in ["regulation", "compliance", "advantage"]):
            relevant.append("alchemist")

        return list(set(relevant))


# Synchronous wrapper for non-async contexts
def scout_research_sync(query: str, context: Dict[str, Any], search_tool=None) -> ResearchBriefing:
    """Synchronous wrapper for Scout research."""
    import asyncio

    scout = ScoutAgent(search_tool=search_tool)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(scout.research(query, context))
