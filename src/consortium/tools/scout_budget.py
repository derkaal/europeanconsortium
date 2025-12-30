"""
Scout Budget Manager - Cost control for web search operations.

Manages search quotas with persistence across runs:
- Monthly budget tracking (calendar month reset, Europe/Berlin)
- Per-query limits
- Per-agent limits
- Time budgets
- Diminishing returns detection
- Cache-aware counting (cache hits = no budget consumed)
"""

import sqlite3
import hashlib
import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class BudgetStatus:
    """Current budget status."""
    monthly_limit: int
    monthly_used: int
    monthly_remaining: int
    current_month: str
    last_reset: str
    queries_this_run: int
    searches_this_run: int


@dataclass
class ScoutState:
    """State tracked during a single Scout run."""
    total_searches: int = 0
    searches_by_agent: Dict[str, int] = None
    fact_fingerprints_seen: set = None
    no_new_facts_streak: int = 0
    start_time: Optional[datetime] = None

    def __post_init__(self):
        if self.searches_by_agent is None:
            self.searches_by_agent = {}
        if self.fact_fingerprints_seen is None:
            self.fact_fingerprints_seen = set()


class ScoutBudgetManager:
    """
    Manages Scout search budgets and stop conditions.

    Features:
    - Monthly budget with calendar month reset (Europe/Berlin timezone)
    - Per-query and per-agent limits
    - Time budget enforcement
    - Diminishing returns detection (deterministic fingerprinting)
    - Cache-aware counting (only cache misses consume budget)
    """

    def __init__(
        self,
        persist_path: str = "data/scout_budget.db",
        monthly_limit: int = 900,
        per_query_limit: int = 15,
        per_agent_limit: int = 3,
        time_budget_seconds: int = 30,
        diminishing_returns_threshold: int = 3,
        timezone: str = "Europe/Berlin"
    ):
        """
        Initialize budget manager.

        Args:
            persist_path: Path to SQLite database for persistence
            monthly_limit: Max searches per calendar month
            per_query_limit: Max searches per user query
            per_agent_limit: Max searches per agent domain
            time_budget_seconds: Max wall time for research phase
            diminishing_returns_threshold: Stop after N searches with no new facts
            timezone: Timezone for calendar month reset
        """
        self.persist_path = Path(persist_path)
        self.monthly_limit = monthly_limit
        self.per_query_limit = per_query_limit
        self.per_agent_limit = per_agent_limit
        self.time_budget_seconds = time_budget_seconds
        self.diminishing_returns_threshold = diminishing_returns_threshold
        self.tz = ZoneInfo(timezone)

        # Ensure parent directory exists
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_db()

        # Check for monthly reset
        self._check_and_reset_if_new_month()

    def _init_db(self):
        """Initialize SQLite database with budget tracking table."""
        with sqlite3.connect(self.persist_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS budget_tracking (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    current_month TEXT NOT NULL,
                    monthly_used INTEGER NOT NULL DEFAULT 0,
                    last_reset TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)

            # Initialize with current month if empty
            cursor = conn.execute("SELECT COUNT(*) FROM budget_tracking")
            if cursor.fetchone()[0] == 0:
                now = datetime.now(self.tz)
                month_key = now.strftime("%Y-%m")
                now_iso = now.isoformat()

                conn.execute("""
                    INSERT INTO budget_tracking (id, current_month, monthly_used, last_reset, last_updated)
                    VALUES (1, ?, 0, ?, ?)
                """, (month_key, now_iso, now_iso))
                conn.commit()

    def _get_current_month_key(self) -> str:
        """Get current month key in YYYY-MM format (Europe/Berlin time)."""
        return datetime.now(self.tz).strftime("%Y-%m")

    def _check_and_reset_if_new_month(self):
        """Check if we've entered a new calendar month and reset if so."""
        current_month = self._get_current_month_key()

        with sqlite3.connect(self.persist_path) as conn:
            cursor = conn.execute("SELECT current_month, monthly_used FROM budget_tracking WHERE id = 1")
            row = cursor.fetchone()

            if row:
                db_month, monthly_used = row

                if db_month != current_month:
                    # New month! Reset counter
                    now = datetime.now(self.tz).isoformat()
                    conn.execute("""
                        UPDATE budget_tracking
                        SET current_month = ?, monthly_used = 0, last_reset = ?, last_updated = ?
                        WHERE id = 1
                    """, (current_month, now, now))
                    conn.commit()

                    logger.info(
                        f"📅 Monthly budget reset: {db_month} → {current_month} "
                        f"(was {monthly_used}/{self.monthly_limit} used)"
                    )

    def get_budget_status(self) -> BudgetStatus:
        """Get current budget status."""
        with sqlite3.connect(self.persist_path) as conn:
            cursor = conn.execute("""
                SELECT current_month, monthly_used, last_reset
                FROM budget_tracking WHERE id = 1
            """)
            row = cursor.fetchone()

            if not row:
                # Should not happen after init
                raise RuntimeError("Budget tracking not initialized")

            current_month, monthly_used, last_reset = row

            return BudgetStatus(
                monthly_limit=self.monthly_limit,
                monthly_used=monthly_used,
                monthly_remaining=max(0, self.monthly_limit - monthly_used),
                current_month=current_month,
                last_reset=last_reset,
                queries_this_run=0,  # Set by caller
                searches_this_run=0  # Set by caller
            )

    def consume_budget(self, count: int = 1) -> bool:
        """
        Consume budget (only called on cache miss).

        Returns True if budget consumed successfully, False if limit exceeded.
        """
        with sqlite3.connect(self.persist_path) as conn:
            cursor = conn.execute("SELECT monthly_used FROM budget_tracking WHERE id = 1")
            row = cursor.fetchone()

            if not row:
                return False

            monthly_used = row[0]
            new_used = monthly_used + count

            if new_used > self.monthly_limit:
                logger.warning(
                    f"❌ Monthly budget exceeded: {new_used} > {self.monthly_limit}"
                )
                return False

            # Update counter
            now = datetime.now(self.tz).isoformat()
            conn.execute("""
                UPDATE budget_tracking
                SET monthly_used = ?, last_updated = ?
                WHERE id = 1
            """, (new_used, now))
            conn.commit()

            remaining = self.monthly_limit - new_used
            logger.info(f"💰 Budget consumed: {count} (remaining: {remaining}/{self.monthly_limit})")

            return True

    def should_stop(self, state: ScoutState) -> Tuple[bool, str]:
        """
        Check if Scout should stop searching.

        Stop conditions:
        1. Time budget exceeded
        2. Per-query limit hit
        3. Per-agent limit hit (for any agent)
        4. Diminishing returns (N consecutive searches with no new facts)
        5. Monthly budget exhausted

        Returns (should_stop, reason)
        """
        # 1. Time budget
        if state.start_time:
            elapsed = (datetime.now(timezone.utc) - state.start_time).total_seconds()
            if elapsed > self.time_budget_seconds:
                return True, f"time_budget_exceeded ({elapsed:.1f}s > {self.time_budget_seconds}s)"

        # 2. Per-query limit
        if state.total_searches >= self.per_query_limit:
            return True, f"per_query_limit_reached ({state.total_searches} >= {self.per_query_limit})"

        # 3. Per-agent limit
        for agent_id, count in state.searches_by_agent.items():
            if count >= self.per_agent_limit:
                return True, f"per_agent_limit_reached (agent={agent_id}, {count} >= {self.per_agent_limit})"

        # 4. Diminishing returns
        if state.no_new_facts_streak >= self.diminishing_returns_threshold:
            return True, f"diminishing_returns ({state.no_new_facts_streak} consecutive searches with no new facts)"

        # 5. Monthly budget
        status = self.get_budget_status()
        if status.monthly_remaining <= 0:
            return True, f"monthly_budget_exhausted ({status.monthly_used}/{status.monthly_limit})"

        return False, ""

    def record_search_results(
        self,
        state: ScoutState,
        agent_id: str,
        results: list,
        cache_hit: bool
    ) -> int:
        """
        Record search results and update state.

        Returns number of new facts found (for diminishing returns tracking).
        """
        # Update search counts
        state.total_searches += 1
        state.searches_by_agent[agent_id] = state.searches_by_agent.get(agent_id, 0) + 1

        # Consume budget only on cache miss
        if not cache_hit:
            self.consume_budget(1)

        # Compute fact fingerprints (deterministic)
        new_facts = 0
        for result in results:
            fingerprint = self._compute_fact_fingerprint(result)
            if fingerprint not in state.fact_fingerprints_seen:
                state.fact_fingerprints_seen.add(fingerprint)
                new_facts += 1

        # Update diminishing returns streak
        if new_facts == 0:
            state.no_new_facts_streak += 1
        else:
            state.no_new_facts_streak = 0

        logger.info(
            f"📊 Search recorded: agent={agent_id}, cache_hit={cache_hit}, "
            f"new_facts={new_facts}, streak={state.no_new_facts_streak}"
        )

        return new_facts

    def _compute_fact_fingerprint(self, result: dict) -> str:
        """
        Compute deterministic fingerprint for a fact.

        Uses normalized URL + title + snippet to detect duplicate facts.
        """
        url = self._normalize_url(result.get("url", ""))
        title = self._normalize_text(result.get("title", ""))
        snippet = self._normalize_text(result.get("snippet", ""))

        content = f"{url}|{title}|{snippet}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for fingerprinting (remove query params, anchors, etc.)."""
        if not url:
            return ""

        # Remove trailing slashes, query params, anchors
        url = url.rstrip("/")
        if "?" in url:
            url = url.split("?")[0]
        if "#" in url:
            url = url.split("#")[0]

        return url.lower()

    def _normalize_text(self, text: str) -> str:
        """Normalize text for fingerprinting (lowercase, strip whitespace)."""
        return " ".join(text.lower().split())
