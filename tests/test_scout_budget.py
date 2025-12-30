"""Tests for Scout Budget Manager and Search Cache."""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, AsyncMock

# Test imports
from src.consortium.tools.scout_budget import ScoutBudgetManager, ScoutState, BudgetStatus
from src.consortium.tools.search_cache import SearchCache


class TestScoutBudgetManager:
    """Test suite for Scout budget management."""

    def test_initialization(self):
        """Test budget manager initializes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_budget.db")
            manager = ScoutBudgetManager(persist_path=db_path, monthly_limit=100)

            status = manager.get_budget_status()
            assert status.monthly_limit == 100
            assert status.monthly_remaining == 100
            assert status.monthly_used == 0

    def test_consume_budget(self):
        """Test budget consumption."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_budget.db")
            manager = ScoutBudgetManager(persist_path=db_path, monthly_limit=100)

            # Consume budget
            assert manager.consume_budget(10) is True

            status = manager.get_budget_status()
            assert status.monthly_used == 10
            assert status.monthly_remaining == 90

    def test_monthly_limit_enforcement(self):
        """Test that monthly limit is enforced."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_budget.db")
            manager = ScoutBudgetManager(persist_path=db_path, monthly_limit=10)

            # Consume up to limit
            assert manager.consume_budget(10) is True

            # Try to exceed limit
            assert manager.consume_budget(1) is False

            status = manager.get_budget_status()
            assert status.monthly_used == 10
            assert status.monthly_remaining == 0

    def test_per_query_limit(self):
        """Test per-query search limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_budget.db")
            manager = ScoutBudgetManager(
                persist_path=db_path,
                per_query_limit=5
            )

            state = ScoutState()
            state.total_searches = 5

            should_stop, reason = manager.should_stop(state)
            assert should_stop is True
            assert "per_query_limit" in reason

    def test_per_agent_limit(self):
        """Test per-agent search limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_budget.db")
            manager = ScoutBudgetManager(
                persist_path=db_path,
                per_agent_limit=3
            )

            state = ScoutState()
            state.searches_by_agent = {"sovereign": 3}

            should_stop, reason = manager.should_stop(state)
            assert should_stop is True
            assert "per_agent_limit" in reason

    def test_time_budget(self):
        """Test time budget enforcement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_budget.db")
            manager = ScoutBudgetManager(
                persist_path=db_path,
                time_budget_seconds=1
            )

            state = ScoutState()
            state.start_time = datetime.now(timezone.utc) - timedelta(seconds=2)

            should_stop, reason = manager.should_stop(state)
            assert should_stop is True
            assert "time_budget" in reason

    def test_diminishing_returns(self):
        """Test diminishing returns stop condition."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_budget.db")
            manager = ScoutBudgetManager(
                persist_path=db_path,
                diminishing_returns_threshold=3
            )

            state = ScoutState()
            state.no_new_facts_streak = 3

            should_stop, reason = manager.should_stop(state)
            assert should_stop is True
            assert "diminishing_returns" in reason

    def test_fact_fingerprinting(self):
        """Test deterministic fact fingerprinting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_budget.db")
            manager = ScoutBudgetManager(persist_path=db_path)

            state = ScoutState()

            # First search - all new facts
            results1 = [
                {"url": "http://example.com/1", "title": "Title 1", "snippet": "Snippet 1"},
                {"url": "http://example.com/2", "title": "Title 2", "snippet": "Snippet 2"}
            ]
            new_facts = manager.record_search_results(state, "sovereign", results1, cache_hit=False)
            assert new_facts == 2
            assert state.no_new_facts_streak == 0

            # Second search - duplicate facts
            results2 = [
                {"url": "http://example.com/1", "title": "Title 1", "snippet": "Snippet 1"}
            ]
            new_facts = manager.record_search_results(state, "sovereign", results2, cache_hit=False)
            assert new_facts == 0
            assert state.no_new_facts_streak == 1

    def test_cache_hit_no_budget_consumed(self):
        """Test that cache hits don't consume budget."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_budget.db")
            manager = ScoutBudgetManager(persist_path=db_path, monthly_limit=100)

            state = ScoutState()
            results = [{"url": "http://example.com", "title": "Test", "snippet": "Test"}]

            # Record cache hit
            manager.record_search_results(state, "sovereign", results, cache_hit=True)

            # Budget should not be consumed
            status = manager.get_budget_status()
            assert status.monthly_used == 0


class TestSearchCache:
    """Test suite for search cache."""

    def test_initialization(self):
        """Test cache initializes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_cache.db")
            cache = SearchCache(db_path=db_path)

            stats = cache.get_stats()
            assert stats["total_entries"] == 0
            assert stats["total_hits"] == 0

    def test_cache_miss(self):
        """Test cache miss returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_cache.db")
            cache = SearchCache(db_path=db_path)

            result = cache.get("test query", {"industry": "Tech"})
            assert result is None

    def test_cache_put_and_get(self):
        """Test caching and retrieval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_cache.db")
            cache = SearchCache(db_path=db_path)

            # Store results
            results = [{"url": "http://test.com", "title": "Test"}]
            cache.put("test query", {"industry": "Tech"}, results)

            # Retrieve results
            cached = cache.get("test query", {"industry": "Tech"})
            assert cached is not None
            assert cached == results

    def test_cache_expiry(self):
        """Test that expired cache entries are not returned."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_cache.db")
            cache = SearchCache(db_path=db_path)

            # Manually insert expired entry
            import sqlite3
            import json
            from datetime import datetime, timezone, timedelta

            expired_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            cache_key = cache._compute_cache_key("test query", {"industry": "Tech"})

            with sqlite3.connect(db_path) as conn:
                conn.execute("""
                    INSERT INTO search_cache
                    (cache_key, query, context_fingerprint, results_json, ttl_category,
                     created_at, expires_at, hit_count, last_hit_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0, NULL)
                """, (
                    cache_key,
                    "test query",
                    "industry=Tech",
                    json.dumps([]),
                    "default",
                    expired_time,
                    expired_time
                ))
                conn.commit()

            # Should return None and delete expired entry
            cached = cache.get("test query", {"industry": "Tech"})
            assert cached is None

    def test_force_refresh(self):
        """Test force_refresh bypasses cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_cache.db")
            cache = SearchCache(db_path=db_path)

            # Store results
            results = [{"url": "http://test.com"}]
            cache.put("test query", {"industry": "Tech"}, results)

            # force_refresh should bypass cache
            cached = cache.get("test query", {"industry": "Tech"}, force_refresh=True)
            assert cached is None

    def test_hit_count_tracking(self):
        """Test that cache hits are tracked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_cache.db")
            cache = SearchCache(db_path=db_path)

            # Store and retrieve multiple times
            results = [{"url": "http://test.com"}]
            cache.put("test query", {"industry": "Tech"}, results)

            cache.get("test query", {"industry": "Tech"})
            cache.get("test query", {"industry": "Tech"})

            stats = cache.get_stats()
            assert stats["total_hits"] == 2

    def test_ttl_categories(self):
        """Test different TTL categories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_cache.db")
            cache = SearchCache(db_path=db_path)

            # Store with different categories
            cache.put("regulatory query", {}, [], ttl_category="regulatory")
            cache.put("pricing query", {}, [], ttl_category="pricing")

            stats = cache.get_stats()
            assert stats["by_category"]["regulatory"] == 1
            assert stats["by_category"]["pricing"] == 1


@pytest.mark.asyncio
async def test_scout_integration():
    """Test Scout integration with budget and cache."""
    from agents.scout import ScoutAgent

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create Scout with budget and cache
        config = {
            "budgets": {
                "enabled": True,
                "persist_path": os.path.join(tmpdir, "budget.db"),
                "monthly_limit": 100,
                "per_query_limit": 5
            },
            "cache": {
                "enabled": True,
                "db_path": os.path.join(tmpdir, "cache.db")
            }
        }

        # Mock search tool
        mock_search = AsyncMock()
        mock_search.search.return_value = [
            {"url": "http://test.com", "title": "Test", "snippet": "Test result", "source": "Test"}
        ]

        scout = ScoutAgent(search_tool=mock_search, config=config)

        # First research (cache miss)
        briefing1 = await scout.research("test query", {"industry": "Tech"})
        assert briefing1 is not None
        assert mock_search.search.called

        # Reset mock
        mock_search.reset_mock()

        # Second research (should be cache hit)
        briefing2 = await scout.research("test query", {"industry": "Tech"})
        assert briefing2 is not None
        assert not mock_search.search.called  # Should not call search tool (cache hit)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
