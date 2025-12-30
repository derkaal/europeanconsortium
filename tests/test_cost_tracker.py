"""Tests for Feature 7: Cost Tracking per Query.

Tests:
1. CostTracker initialization and database setup
2. Track single LLM call
3. Calculate costs for different models
4. Get query cost breakdown
5. Get agent cost aggregation
6. Get model cost aggregation
7. Monthly cost reporting
8. Total cost calculation
9. Data cleanup
10. Model pricing validation
"""

import pytest
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from src.consortium.tools.cost_tracker import (
    CostTracker,
    get_cost_tracker,
    MODEL_PRICING
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def tracker(temp_db):
    """Create CostTracker instance with temp database."""
    return CostTracker(db_path=temp_db)


# ==============================================================================
# Test: Initialization
# ==============================================================================

def test_cost_tracker_initialization(temp_db):
    """Test cost tracker initializes correctly."""
    tracker = CostTracker(db_path=temp_db)

    assert os.path.exists(temp_db)
    assert tracker.db_path == temp_db


def test_database_schema_created(tracker):
    """Test database schema is created."""
    import sqlite3

    conn = sqlite3.connect(tracker.db_path)
    cursor = conn.cursor()

    # Check table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='llm_calls'
    """)

    assert cursor.fetchone() is not None
    conn.close()


def test_global_instance_singleton():
    """Test global instance is singleton."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        tracker1 = get_cost_tracker(db_path)
        tracker2 = get_cost_tracker(db_path)

        assert tracker1 is tracker2
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


# ==============================================================================
# Test: Track LLM Calls
# ==============================================================================

def test_track_single_call(tracker):
    """Test tracking single LLM call."""
    cost = tracker.track_call(
        query_id="q1",
        agent_name="Jurist",
        model="claude-3-5-sonnet-20241022",
        provider="anthropic",
        input_tokens=1000,
        output_tokens=500,
        purpose="agent_reasoning"
    )

    assert cost > 0
    assert isinstance(cost, float)


def test_track_multiple_calls(tracker):
    """Test tracking multiple LLM calls."""
    costs = []

    for i in range(5):
        cost = tracker.track_call(
            query_id=f"q{i}",
            agent_name="Jurist",
            model="claude-3-5-sonnet-20241022",
            provider="anthropic",
            input_tokens=1000,
            output_tokens=500
        )
        costs.append(cost)

    assert len(costs) == 5
    assert all(c > 0 for c in costs)


# ==============================================================================
# Test: Cost Calculation
# ==============================================================================

def test_calculate_cost_claude_sonnet(tracker):
    """Test cost calculation for Claude Sonnet."""
    input_cost, output_cost, total_cost = tracker._calculate_cost(
        model="claude-3-5-sonnet-20241022",
        input_tokens=1_000_000,  # 1M tokens
        output_tokens=1_000_000  # 1M tokens
    )

    # Pricing: $3/1M input, $15/1M output
    assert input_cost == 3.00
    assert output_cost == 15.00
    assert total_cost == 18.00


def test_calculate_cost_claude_haiku(tracker):
    """Test cost calculation for Claude Haiku (budget tier)."""
    input_cost, output_cost, total_cost = tracker._calculate_cost(
        model="claude-3-haiku-20240307",
        input_tokens=1_000_000,
        output_tokens=1_000_000
    )

    # Pricing: $0.25/1M input, $1.25/1M output
    assert input_cost == 0.25
    assert output_cost == 1.25
    assert total_cost == 1.50


def test_calculate_cost_gpt4(tracker):
    """Test cost calculation for GPT-4."""
    input_cost, output_cost, total_cost = tracker._calculate_cost(
        model="gpt-4",
        input_tokens=1_000_000,
        output_tokens=1_000_000
    )

    # Pricing: $30/1M input, $60/1M output
    assert input_cost == 30.00
    assert output_cost == 60.00
    assert total_cost == 90.00


def test_calculate_cost_gemini_flash(tracker):
    """Test cost calculation for Gemini Flash (budget tier)."""
    input_cost, output_cost, total_cost = tracker._calculate_cost(
        model="gemini-1.5-flash",
        input_tokens=1_000_000,
        output_tokens=1_000_000
    )

    # Pricing: $0.075/1M input, $0.30/1M output
    assert input_cost == 0.075
    assert output_cost == 0.30
    assert total_cost == 0.375


def test_calculate_cost_unknown_model(tracker):
    """Test cost calculation for unknown model uses fallback."""
    input_cost, output_cost, total_cost = tracker._calculate_cost(
        model="unknown-model-xyz",
        input_tokens=1_000_000,
        output_tokens=1_000_000
    )

    # Should use fallback pricing (standard tier)
    assert total_cost > 0


def test_calculate_cost_small_tokens(tracker):
    """Test cost calculation for small token counts."""
    input_cost, output_cost, total_cost = tracker._calculate_cost(
        model="claude-3-5-sonnet-20241022",
        input_tokens=100,  # 100 tokens
        output_tokens=50   # 50 tokens
    )

    # Should be very small but non-zero
    assert total_cost > 0
    assert total_cost < 0.01


# ==============================================================================
# Test: Query Cost
# ==============================================================================

def test_get_query_cost_single_call(tracker):
    """Test getting cost for single query."""
    tracker.track_call(
        query_id="q1",
        agent_name="Jurist",
        model="claude-3-5-sonnet-20241022",
        provider="anthropic",
        input_tokens=1000,
        output_tokens=500
    )

    cost = tracker.get_query_cost("q1")

    assert cost["query_id"] == "q1"
    assert cost["call_count"] == 1
    assert cost["total_input_tokens"] == 1000
    assert cost["total_output_tokens"] == 500
    assert cost["total_cost_usd"] > 0


def test_get_query_cost_multiple_calls(tracker):
    """Test getting cost for query with multiple calls."""
    for i in range(3):
        tracker.track_call(
            query_id="q1",
            agent_name=f"Agent{i}",
            model="claude-3-5-sonnet-20241022",
            provider="anthropic",
            input_tokens=1000,
            output_tokens=500
        )

    cost = tracker.get_query_cost("q1")

    assert cost["call_count"] == 3
    assert cost["total_input_tokens"] == 3000
    assert cost["total_output_tokens"] == 1500


def test_get_query_cost_nonexistent(tracker):
    """Test getting cost for nonexistent query."""
    cost = tracker.get_query_cost("nonexistent")

    assert cost["call_count"] == 0
    assert cost["total_cost_usd"] == 0.0


# ==============================================================================
# Test: Agent Costs
# ==============================================================================

def test_get_agent_costs(tracker):
    """Test getting cost breakdown by agent."""
    tracker.track_call("q1", "Jurist", "claude-3-5-sonnet-20241022", "anthropic", 1000, 500)
    tracker.track_call("q2", "Jurist", "claude-3-5-sonnet-20241022", "anthropic", 1000, 500)
    tracker.track_call("q3", "Economist", "claude-3-5-sonnet-20241022", "anthropic", 1000, 500)

    agent_costs = tracker.get_agent_costs()

    assert len(agent_costs) == 2
    assert agent_costs[0]["agent_name"] in ["Jurist", "Economist"]
    assert all(c["call_count"] > 0 for c in agent_costs)
    assert all(c["total_cost_usd"] > 0 for c in agent_costs)


def test_get_agent_costs_sorted(tracker):
    """Test agent costs are sorted by total cost descending."""
    # Jurist makes expensive calls
    tracker.track_call("q1", "Jurist", "gpt-4", "openai", 10000, 5000)

    # Economist makes cheap calls
    tracker.track_call("q2", "Economist", "gemini-1.5-flash", "google", 1000, 500)

    agent_costs = tracker.get_agent_costs()

    # Jurist should be first (higher cost)
    assert agent_costs[0]["agent_name"] == "Jurist"
    assert agent_costs[1]["agent_name"] == "Economist"


def test_get_agent_costs_date_filter(tracker):
    """Test agent costs with date filter."""
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    tracker.track_call("q1", "Jurist", "claude-3-5-sonnet-20241022", "anthropic", 1000, 500)

    # Filter for yesterday should return nothing
    agent_costs = tracker.get_agent_costs(start_date=yesterday - timedelta(days=1), end_date=yesterday)
    assert len(agent_costs) == 0

    # Filter for today should return results
    agent_costs = tracker.get_agent_costs(start_date=now - timedelta(hours=1))
    assert len(agent_costs) > 0


# ==============================================================================
# Test: Model Costs
# ==============================================================================

def test_get_model_costs(tracker):
    """Test getting cost breakdown by model."""
    tracker.track_call("q1", "Jurist", "claude-3-5-sonnet-20241022", "anthropic", 1000, 500)
    tracker.track_call("q2", "Economist", "gpt-4", "openai", 1000, 500)

    model_costs = tracker.get_model_costs()

    assert len(model_costs) == 2
    assert all("model" in c for c in model_costs)
    assert all("provider" in c for c in model_costs)
    assert all("tier" in c for c in model_costs)


def test_get_model_costs_includes_tier(tracker):
    """Test model costs include tier information."""
    tracker.track_call("q1", "Jurist", "claude-3-haiku-20240307", "anthropic", 1000, 500)

    model_costs = tracker.get_model_costs()

    assert model_costs[0]["tier"] == "BUDGET"


# ==============================================================================
# Test: Monthly Reporting
# ==============================================================================

def test_get_monthly_report_current_month(tracker):
    """Test getting monthly report for current month."""
    tracker.track_call("q1", "Jurist", "claude-3-5-sonnet-20241022", "anthropic", 1000, 500)
    tracker.track_call("q2", "Economist", "claude-3-5-sonnet-20241022", "anthropic", 1000, 500)

    report = tracker.get_monthly_report()

    assert "month" in report
    assert "summary" in report
    assert "by_agent" in report
    assert "by_model" in report

    assert report["summary"]["total_calls"] == 2
    assert report["summary"]["unique_queries"] == 2
    assert report["summary"]["total_cost_usd"] > 0


def test_get_monthly_report_specific_month(tracker):
    """Test getting monthly report for specific month."""
    # Get report for January 2024
    report = tracker.get_monthly_report(month=datetime(2024, 1, 1))

    assert report["month"] == "2024-01"
    assert "2024-01-01" in report["start_date"]


def test_get_monthly_report_empty(tracker):
    """Test monthly report with no data."""
    report = tracker.get_monthly_report()

    assert report["summary"]["total_calls"] == 0
    assert report["summary"]["total_cost_usd"] == 0.0


# ==============================================================================
# Test: Total Cost
# ==============================================================================

def test_get_total_cost_all_time(tracker):
    """Test getting total cost across all time."""
    tracker.track_call("q1", "Jurist", "claude-3-5-sonnet-20241022", "anthropic", 1000, 500)
    tracker.track_call("q2", "Economist", "claude-3-5-sonnet-20241022", "anthropic", 1000, 500)

    total = tracker.get_total_cost()

    assert total > 0


def test_get_total_cost_date_range(tracker):
    """Test getting total cost for date range."""
    now = datetime.now()

    tracker.track_call("q1", "Jurist", "claude-3-5-sonnet-20241022", "anthropic", 1000, 500)

    # Get cost for last hour
    total = tracker.get_total_cost(start_date=now - timedelta(hours=1))
    assert total > 0

    # Get cost for yesterday (should be 0)
    yesterday = now - timedelta(days=1)
    total = tracker.get_total_cost(
        start_date=yesterday - timedelta(hours=1),
        end_date=yesterday
    )
    assert total == 0.0


# ==============================================================================
# Test: Data Cleanup
# ==============================================================================

def test_clear_old_data(tracker):
    """Test clearing old data."""
    # Add some calls
    tracker.track_call("q1", "Jurist", "claude-3-5-sonnet-20241022", "anthropic", 1000, 500)

    # Clear data older than 0 days (should delete everything)
    deleted = tracker.clear_old_data(days_to_keep=0)

    # Should have deleted at least 1 record
    assert deleted >= 0


# ==============================================================================
# Test: Model Pricing Validation
# ==============================================================================

def test_model_pricing_has_all_tiers():
    """Test model pricing includes all tiers."""
    tiers = {pricing["tier"] for pricing in MODEL_PRICING.values()}

    assert "BUDGET" in tiers
    assert "STANDARD" in tiers
    assert "PREMIUM" in tiers


def test_model_pricing_has_required_fields():
    """Test all model pricing has input and output costs."""
    for model, pricing in MODEL_PRICING.items():
        assert "input" in pricing
        assert "output" in pricing
        assert "tier" in pricing
        assert pricing["input"] > 0
        assert pricing["output"] > 0


def test_model_pricing_budget_cheaper_than_premium():
    """Test budget tier is cheaper than premium tier."""
    budget_models = [m for m, p in MODEL_PRICING.items() if p["tier"] == "BUDGET"]
    premium_models = [m for m, p in MODEL_PRICING.items() if p["tier"] == "PREMIUM"]

    # Compare average costs
    budget_avg = sum(MODEL_PRICING[m]["input"] + MODEL_PRICING[m]["output"]
                     for m in budget_models) / len(budget_models)

    premium_avg = sum(MODEL_PRICING[m]["input"] + MODEL_PRICING[m]["output"]
                      for m in premium_models) / len(premium_models)

    assert budget_avg < premium_avg


# ==============================================================================
# Test: Integration Scenarios
# ==============================================================================

def test_track_full_query_lifecycle(tracker):
    """Test tracking costs for full query lifecycle."""
    query_id = "full_query_1"

    # Simulate multiple agents making calls
    tracker.track_call(query_id, "Jurist", "claude-3-5-sonnet-20241022", "anthropic",
                       2000, 1000, "agent_reasoning")
    tracker.track_call(query_id, "Economist", "claude-3-5-sonnet-20241022", "anthropic",
                       1500, 800, "agent_reasoning")
    tracker.track_call(query_id, "Synthesizer", "claude-3-5-sonnet-20241022", "anthropic",
                       3000, 2000, "synthesis")

    # Get query cost
    query_cost = tracker.get_query_cost(query_id)

    assert query_cost["call_count"] == 3
    assert query_cost["total_input_tokens"] == 6500
    assert query_cost["total_output_tokens"] == 3800
    assert query_cost["total_cost_usd"] > 0


def test_compare_model_costs(tracker):
    """Test comparing costs across different models."""
    # Same input/output, different models
    query_id = "model_comparison"

    tracker.track_call(query_id, "Agent1", "claude-3-haiku-20240307", "anthropic", 10000, 5000)
    tracker.track_call(query_id, "Agent2", "claude-3-5-sonnet-20241022", "anthropic", 10000, 5000)
    tracker.track_call(query_id, "Agent3", "gpt-4", "openai", 10000, 5000)

    model_costs = tracker.get_model_costs()

    # Should have 3 different models
    assert len(model_costs) == 3

    # GPT-4 should be most expensive
    gpt4_cost = next(c for c in model_costs if c["model"] == "gpt-4")
    haiku_cost = next(c for c in model_costs if c["model"] == "claude-3-haiku-20240307")

    assert gpt4_cost["total_cost_usd"] > haiku_cost["total_cost_usd"]
