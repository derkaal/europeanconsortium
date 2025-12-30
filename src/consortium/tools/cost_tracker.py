"""Cost Tracker (Feature 7 - BONUS).

Tracks LLM API costs across all queries, models, agents, and providers.

Features:
- Per-query cost tracking
- Per-agent cost aggregation
- Per-model cost tracking
- Per-provider aggregation
- Monthly cost reporting
- SQLite persistence
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMCall:
    """Record of a single LLM API call."""

    id: Optional[int] = None
    query_id: str = ""
    timestamp: datetime = None
    agent_name: str = ""
    model: str = ""
    provider: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    input_cost_usd: float = 0.0
    output_cost_usd: float = 0.0
    total_cost_usd: float = 0.0
    purpose: str = ""  # e.g., "agent_reasoning", "synthesis", "tension_resolution"


# ==============================================================================
# MODEL PRICING (per 1M tokens, USD)
# ==============================================================================

MODEL_PRICING = {
    # Anthropic Claude (standard pricing as of 2024)
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00, "tier": "PREMIUM"},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00, "tier": "STANDARD"},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25, "tier": "BUDGET"},

    # OpenAI (standard pricing as of 2024)
    "gpt-4-turbo": {"input": 10.00, "output": 30.00, "tier": "PREMIUM"},
    "gpt-4": {"input": 30.00, "output": 60.00, "tier": "PREMIUM"},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50, "tier": "BUDGET"},

    # Google Gemini (standard pricing as of 2024)
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00, "tier": "STANDARD"},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30, "tier": "BUDGET"},

    # Mistral (standard pricing as of 2024)
    "mistral-large-latest": {"input": 4.00, "output": 12.00, "tier": "STANDARD"},
    "mistral-medium-latest": {"input": 2.70, "output": 8.10, "tier": "STANDARD"},
    "mistral-small-latest": {"input": 1.00, "output": 3.00, "tier": "BUDGET"},
}


# ==============================================================================
# COST TRACKER
# ==============================================================================

class CostTracker:
    """Track LLM API costs across queries and agents.

    Persistent SQLite storage for cost analysis and budgeting.
    """

    def __init__(self, db_path: str = "data/cost_tracker.db"):
        """Initialize cost tracker.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path

        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                model TEXT NOT NULL,
                provider TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                input_cost_usd REAL NOT NULL,
                output_cost_usd REAL NOT NULL,
                total_cost_usd REAL NOT NULL,
                purpose TEXT
            )
        """)

        # Create indices for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_query_id ON llm_calls(query_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON llm_calls(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_name ON llm_calls(agent_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_model ON llm_calls(model)
        """)

        conn.commit()
        conn.close()

    def track_call(
        self,
        query_id: str,
        agent_name: str,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        purpose: str = "agent_reasoning"
    ) -> float:
        """Track a single LLM API call.

        Args:
            query_id: Unique query identifier
            agent_name: Agent making the call
            model: Model name
            provider: Provider (anthropic, openai, google, mistral)
            input_tokens: Input token count
            output_tokens: Output token count
            purpose: Purpose of the call

        Returns:
            Total cost in USD
        """
        # Calculate costs
        input_cost, output_cost, total_cost = self._calculate_cost(
            model, input_tokens, output_tokens
        )

        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO llm_calls (
                query_id, timestamp, agent_name, model, provider,
                input_tokens, output_tokens, input_cost_usd, output_cost_usd,
                total_cost_usd, purpose
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            query_id,
            datetime.now().isoformat(),
            agent_name,
            model,
            provider,
            input_tokens,
            output_tokens,
            input_cost,
            output_cost,
            total_cost,
            purpose
        ))

        conn.commit()
        conn.close()

        return total_cost

    def get_query_cost(self, query_id: str) -> Dict[str, Any]:
        """Get total cost for a specific query.

        Args:
            query_id: Query identifier

        Returns:
            Cost breakdown dict
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as call_count,
                SUM(input_tokens) as total_input_tokens,
                SUM(output_tokens) as total_output_tokens,
                SUM(total_cost_usd) as total_cost_usd
            FROM llm_calls
            WHERE query_id = ?
        """, (query_id,))

        row = cursor.fetchone()
        conn.close()

        if not row or row[0] == 0:
            return {
                "query_id": query_id,
                "call_count": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost_usd": 0.0
            }

        return {
            "query_id": query_id,
            "call_count": row[0],
            "total_input_tokens": row[1],
            "total_output_tokens": row[2],
            "total_cost_usd": round(row[3], 6)
        }

    def get_agent_costs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get cost breakdown by agent.

        Args:
            start_date: Start date filter (optional)
            end_date: End date filter (optional)

        Returns:
            List of agent cost dicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT
                agent_name,
                COUNT(*) as call_count,
                SUM(total_cost_usd) as total_cost_usd,
                AVG(total_cost_usd) as avg_cost_per_call
            FROM llm_calls
        """

        params = []
        if start_date or end_date:
            conditions = []
            if start_date:
                conditions.append("timestamp >= ?")
                params.append(start_date.isoformat())
            if end_date:
                conditions.append("timestamp <= ?")
                params.append(end_date.isoformat())
            query += " WHERE " + " AND ".join(conditions)

        query += " GROUP BY agent_name ORDER BY total_cost_usd DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "agent_name": row[0],
                "call_count": row[1],
                "total_cost_usd": round(row[2], 6),
                "avg_cost_per_call": round(row[3], 6)
            }
            for row in rows
        ]

    def get_model_costs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get cost breakdown by model.

        Args:
            start_date: Start date filter (optional)
            end_date: End date filter (optional)

        Returns:
            List of model cost dicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT
                model,
                provider,
                COUNT(*) as call_count,
                SUM(input_tokens) as total_input_tokens,
                SUM(output_tokens) as total_output_tokens,
                SUM(total_cost_usd) as total_cost_usd
            FROM llm_calls
        """

        params = []
        if start_date or end_date:
            conditions = []
            if start_date:
                conditions.append("timestamp >= ?")
                params.append(start_date.isoformat())
            if end_date:
                conditions.append("timestamp <= ?")
                params.append(end_date.isoformat())
            query += " WHERE " + " AND ".join(conditions)

        query += " GROUP BY model, provider ORDER BY total_cost_usd DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "model": row[0],
                "provider": row[1],
                "call_count": row[2],
                "total_input_tokens": row[3],
                "total_output_tokens": row[4],
                "total_cost_usd": round(row[5], 6),
                "tier": MODEL_PRICING.get(row[0], {}).get("tier", "UNKNOWN")
            }
            for row in rows
        ]

    def get_monthly_report(self, month: Optional[datetime] = None) -> Dict[str, Any]:
        """Get monthly cost report.

        Args:
            month: Month to report (defaults to current month)

        Returns:
            Monthly report dict
        """
        if month is None:
            month = datetime.now()

        # Calculate month start and end
        start_date = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)

        # Get total costs
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as call_count,
                COUNT(DISTINCT query_id) as unique_queries,
                SUM(input_tokens) as total_input_tokens,
                SUM(output_tokens) as total_output_tokens,
                SUM(total_cost_usd) as total_cost_usd
            FROM llm_calls
            WHERE timestamp >= ? AND timestamp < ?
        """, (start_date.isoformat(), end_date.isoformat()))

        row = cursor.fetchone()
        conn.close()

        # Get breakdown by agent and model
        agent_costs = self.get_agent_costs(start_date, end_date)
        model_costs = self.get_model_costs(start_date, end_date)

        return {
            "month": start_date.strftime("%Y-%m"),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "summary": {
                "total_calls": row[0] if row else 0,
                "unique_queries": row[1] if row else 0,
                "total_input_tokens": row[2] if row else 0,
                "total_output_tokens": row[3] if row else 0,
                "total_cost_usd": round(row[4], 2) if row and row[4] else 0.0
            },
            "by_agent": agent_costs,
            "by_model": model_costs
        }

    def get_total_cost(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> float:
        """Get total cost for date range.

        Args:
            start_date: Start date (optional)
            end_date: End date (optional)

        Returns:
            Total cost in USD
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT SUM(total_cost_usd) FROM llm_calls"
        params = []

        if start_date or end_date:
            conditions = []
            if start_date:
                conditions.append("timestamp >= ?")
                params.append(start_date.isoformat())
            if end_date:
                conditions.append("timestamp <= ?")
                params.append(end_date.isoformat())
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()

        return round(row[0], 6) if row and row[0] else 0.0

    def _calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> tuple[float, float, float]:
        """Calculate cost for LLM call.

        Args:
            model: Model name
            input_tokens: Input token count
            output_tokens: Output token count

        Returns:
            (input_cost, output_cost, total_cost) in USD
        """
        pricing = MODEL_PRICING.get(model)

        if not pricing:
            # Unknown model - use fallback pricing (standard tier)
            pricing = {"input": 3.00, "output": 15.00}

        # Calculate costs (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        return (
            round(input_cost, 6),
            round(output_cost, 6),
            round(total_cost, 6)
        )

    def clear_old_data(self, days_to_keep: int = 90):
        """Clear data older than specified days.

        Args:
            days_to_keep: Number of days to keep
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM llm_calls WHERE timestamp < ?
        """, (cutoff_date.isoformat(),))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted_count


# ==============================================================================
# GLOBAL INSTANCE
# ==============================================================================

_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker(db_path: str = "data/cost_tracker.db") -> CostTracker:
    """Get global CostTracker instance (singleton pattern).

    Args:
        db_path: Path to SQLite database

    Returns:
        CostTracker instance
    """
    global _cost_tracker

    if _cost_tracker is None:
        _cost_tracker = CostTracker(db_path=db_path)

    return _cost_tracker
