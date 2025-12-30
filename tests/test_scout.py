"""Tests for The Scout agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.scout import ScoutAgent, ResearchBriefing


class TestScoutAgent:
    """Test suite for Scout agent."""

    def test_initialization(self):
        """Test agent initializes correctly."""
        scout = ScoutAgent()
        assert scout.agent_id == "scout"
        assert scout.name == "The Scout"
        assert scout.max_searches == 15

    def test_initialization_with_config(self):
        """Test agent accepts config overrides."""
        scout = ScoutAgent(config={"max_searches": 10})
        assert scout.max_searches == 10

    def test_system_prompt_contains_key_concepts(self):
        """Test system prompt includes research concepts."""
        scout = ScoutAgent()
        prompt = scout.system_prompt.lower()

        assert "intelligence" in prompt
        assert "research" in prompt
        assert "source" in prompt
        assert "briefing" in prompt

    def test_identify_relevant_agents_ai_query(self):
        """Test agent identification for AI-related query."""
        scout = ScoutAgent()

        query = "Should we use GPT-4 for our analytics platform?"
        context = {"industry": "Technology"}

        agents = scout._identify_relevant_agents(query, context)

        assert "intelligence_sovereign" in agents
        assert "architect" in agents
        assert "economist" in agents

    def test_identify_relevant_agents_sustainability_query(self):
        """Test agent identification for sustainability query."""
        scout = ScoutAgent()

        query = "How can we reduce the carbon footprint of our data centers?"
        context = {"industry": "Technology"}

        agents = scout._identify_relevant_agents(query, context)

        assert "ecosystem" in agents

    def test_identify_relevant_agents_security_query(self):
        """Test agent identification for security query."""
        scout = ScoutAgent()

        query = "What are the security risks of using cloud AI?"
        context = {"industry": "Finance"}

        agents = scout._identify_relevant_agents(query, context)

        assert "technologist" in agents

    def test_plan_searches_limits_results(self):
        """Test search planning respects limits."""
        scout = ScoutAgent(config={"max_searches": 5})

        research_needs = {
            "sovereign": ["topic1", "topic2", "topic3"],
            "economist": ["topic4", "topic5"],
            "jurist": ["topic6", "topic7"]
        }

        plans = scout.plan_searches(research_needs)

        assert len(plans) <= 5

    def test_plan_searches_prioritizes_jurist_sovereign(self):
        """Test high-priority agents come first in search plans."""
        scout = ScoutAgent()

        research_needs = {
            "economist": ["cost analysis"],
            "jurist": ["GDPR update"],
            "sovereign": ["cloud policy"]
        }

        plans = scout.plan_searches(research_needs)

        # First searches should be high priority (jurist, sovereign)
        high_priority_first = [p["agent_id"] for p in plans[:2]]
        assert "jurist" in high_priority_first or "sovereign" in high_priority_first


class TestScoutIntegration:
    """Integration tests for Scout in the consortium."""

    @pytest.mark.asyncio
    async def test_research_without_search_tool(self):
        """Test research degrades gracefully without search tool."""
        scout = ScoutAgent(search_tool=None)

        briefing = await scout.research(
            query="Test query",
            context={"industry": "Test"}
        )

        assert isinstance(briefing, ResearchBriefing)
        assert briefing.searches_executed == 0
        assert briefing.confidence < 0.5  # Low confidence without actual searches

    @pytest.mark.asyncio
    async def test_research_with_mock_search(self):
        """Test research with mocked search tool."""
        mock_search = AsyncMock()
        mock_search.search.return_value = [
            {"title": "Test Result", "snippet": "Important finding", "url": "http://test.com", "source": "Test"}
        ]

        scout = ScoutAgent(search_tool=mock_search)

        briefing = await scout.research(
            query="Should we use AWS for our EU data?",
            context={"industry": "Financial Services", "target_markets": "Germany"}
        )

        assert isinstance(briefing, ResearchBriefing)
        assert briefing.searches_executed > 0
        assert mock_search.search.called


class TestBraveSearch:
    """Test suite for Brave Search integration."""

    def test_brave_initialization_without_key(self):
        """Test Brave initializes but unavailable without key."""
        import os
        # Temporarily remove key if set
        original = os.environ.pop("BRAVE_API_KEY", None)

        try:
            from src.consortium.tools.search import BraveSearchTool
            brave = BraveSearchTool(api_key=None)
            assert not brave.is_available()
        finally:
            if original:
                os.environ["BRAVE_API_KEY"] = original

    def test_brave_initialization_with_key(self):
        """Test Brave initializes correctly with key."""
        from src.consortium.tools.search import BraveSearchTool
        brave = BraveSearchTool(api_key="test_key")
        assert brave.is_available()

    @pytest.mark.asyncio
    async def test_brave_source_extraction(self):
        """Test source extraction from URLs."""
        from src.consortium.tools.search import BraveSearchTool
        brave = BraveSearchTool(api_key="test")

        assert brave._extract_source("https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689") == "EUR-Lex"
        assert brave._extract_source("https://mistral.ai/news/mistral-large-2/") == "Mistral AI"
        assert brave._extract_source("https://www.reuters.com/technology/") == "Reuters"


class TestMultiProviderSearch:
    """Test suite for multi-provider search with failover."""

    def test_factory_creates_tool(self):
        """Test factory creates some tool even without keys."""
        from src.consortium.tools.search import SearchToolFactory
        tool = SearchToolFactory.create()
        assert tool is not None

    @pytest.mark.asyncio
    async def test_failover_tries_next_provider(self):
        """Test failover moves to next provider on failure."""
        from src.consortium.tools.search import MultiProviderSearchTool, BaseSearchTool
        from unittest.mock import AsyncMock

        # Create mock providers
        failing_provider = AsyncMock(spec=BaseSearchTool)
        failing_provider.is_available.return_value = True
        failing_provider.search.side_effect = Exception("API Error")

        working_provider = AsyncMock(spec=BaseSearchTool)
        working_provider.is_available.return_value = True
        working_provider.search.return_value = [{"title": "Success", "url": "http://test.com"}]

        multi = MultiProviderSearchTool(
            providers=[failing_provider, working_provider],
            mode="failover"
        )

        results = await multi.search("test query")

        assert len(results) == 1
        assert results[0]["title"] == "Success"
        assert working_provider.search.called

    @pytest.mark.asyncio
    async def test_aggregate_combines_results(self):
        """Test aggregate mode combines results from multiple providers."""
        from src.consortium.tools.search import MultiProviderSearchTool, BaseSearchTool
        from unittest.mock import AsyncMock

        provider1 = AsyncMock(spec=BaseSearchTool)
        provider1.is_available.return_value = True
        provider1.search.return_value = [
            {"title": "Result 1", "url": "http://a.com", "score": 0.9}
        ]

        provider2 = AsyncMock(spec=BaseSearchTool)
        provider2.is_available.return_value = True
        provider2.search.return_value = [
            {"title": "Result 2", "url": "http://b.com", "score": 0.8}
        ]

        multi = MultiProviderSearchTool(
            providers=[provider1, provider2],
            mode="aggregate"
        )

        results = await multi.search("test query", max_results=5)

        assert len(results) == 2
        # Should be sorted by score
        assert results[0]["title"] == "Result 1"
        assert results[1]["title"] == "Result 2"


class TestBriefingInjection:
    """Test briefing injection into agent contexts."""

    def test_inject_briefing_adds_summary(self):
        """Test executive summary is injected."""
        from src.consortium.nodes.scout_node import inject_briefing_into_agent_context

        briefing = {
            "executive_summary": "Test summary",
            "research_timestamp": "2025-01-15T10:00:00Z",
            "agent_briefings": {}
        }

        enhanced = inject_briefing_into_agent_context(
            "sovereign", {}, briefing
        )

        assert enhanced["research_summary"] == "Test summary"

    def test_inject_briefing_adds_agent_specific(self):
        """Test agent-specific findings are injected."""
        from src.consortium.nodes.scout_node import inject_briefing_into_agent_context

        briefing = {
            "executive_summary": "Summary",
            "research_timestamp": "2025-01-15T10:00:00Z",
            "agent_briefings": {
                "sovereign": {
                    "relevant_findings": ["Finding 1", "Finding 2"],
                    "sources": ["EUR-Lex"],
                    "confidence": 0.9
                }
            }
        }

        enhanced = inject_briefing_into_agent_context(
            "sovereign", {}, briefing
        )

        assert "Finding 1" in enhanced["research_findings"]
        assert enhanced["research_confidence"] == 0.9

    def test_inject_briefing_handles_missing_agent(self):
        """Test graceful handling when agent not in briefing."""
        from src.consortium.nodes.scout_node import inject_briefing_into_agent_context

        briefing = {
            "executive_summary": "Summary",
            "research_timestamp": "2025-01-15T10:00:00Z",
            "agent_briefings": {}
        }

        enhanced = inject_briefing_into_agent_context(
            "sovereign", {"existing": "data"}, briefing
        )

        assert enhanced["existing"] == "data"  # Original preserved
        assert "research_findings" not in enhanced  # Not added if not in briefing


class TestScoutNode:
    """Test suite for Scout node integration."""

    @pytest.mark.asyncio
    async def test_scout_node_with_valid_query(self):
        """Test scout node processes valid query."""
        from src.consortium.nodes.scout_node import create_scout_node

        mock_search = AsyncMock()
        mock_search.search.return_value = []

        scout_node = create_scout_node(search_tool=mock_search)

        state = {
            "query": "Test query",
            "context": {"industry": "Test"}
        }

        result = await scout_node(state)

        assert "research_briefing" in result
        assert result["scout_completed"] is True

    @pytest.mark.asyncio
    async def test_scout_node_with_empty_query(self):
        """Test scout node handles empty query gracefully."""
        from src.consortium.nodes.scout_node import create_scout_node

        scout_node = create_scout_node()

        state = {"query": "", "context": {}}

        result = await scout_node(state)

        assert result["research_briefing"] is None

    @pytest.mark.asyncio
    async def test_scout_node_handles_errors(self):
        """Test scout node handles search errors gracefully."""
        from src.consortium.nodes.scout_node import create_scout_node

        mock_search = AsyncMock()
        mock_search.search.side_effect = Exception("Search failed")

        scout_node = create_scout_node(search_tool=mock_search)

        state = {
            "query": "Test query",
            "context": {"industry": "Test"}
        }

        result = await scout_node(state)

        assert "scout_error" in result or result.get("scout_completed") is False
