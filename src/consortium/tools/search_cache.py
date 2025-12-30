"""
Scout Search Cache - Reduces API calls through intelligent caching.

Caches search results with configurable TTL by content category:
- Regulatory content: 30 days (changes slowly)
- Pricing: 1 day (changes fast)
- News: 1 day (ephemeral)
- AI models: 3 days (frequent releases)
- Default: 7 days
"""

import sqlite3
import hashlib
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class SearchCache:
    """
    Caches Scout search results to reduce API calls.

    Key = hash(query + context_fingerprint + date_bucket)
    Value = SearchCacheEntry (results + metadata)

    TTL varies by content category for optimal freshness vs. cost balance.
    """

    # TTL by category (in days)
    TTL_DAYS = {
        "regulatory": 30,
        "pricing": 1,
        "news": 1,
        "ai_models": 3,
        "default": 7
    }

    def __init__(self, db_path: str = "data/scout_cache.db"):
        """
        Initialize search cache.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)

        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with cache table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_cache (
                    cache_key TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    context_fingerprint TEXT NOT NULL,
                    results_json TEXT NOT NULL,
                    ttl_category TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    hit_count INTEGER NOT NULL DEFAULT 0,
                    last_hit_at TEXT
                )
            """)

            # Index for expiry cleanup
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at
                ON search_cache(expires_at)
            """)

            conn.commit()

    def get(
        self,
        query: str,
        context: Dict[str, Any],
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached search results if available and fresh.

        Args:
            query: Search query
            context: Query context (industry, markets, etc.)
            force_refresh: If True, bypass cache

        Returns:
            Cached results dict or None if cache miss
        """
        if force_refresh:
            logger.info("🔄 Cache bypassed (force_refresh=True)")
            return None

        cache_key = self._compute_cache_key(query, context)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT results_json, expires_at, hit_count
                FROM search_cache
                WHERE cache_key = ?
            """, (cache_key,))

            row = cursor.fetchone()

            if not row:
                logger.info(f"❌ Cache miss: {cache_key[:16]}...")
                return None

            results_json, expires_at, hit_count = row

            # Check expiry
            expires_dt = datetime.fromisoformat(expires_at)
            now = datetime.now(timezone.utc)

            if now > expires_dt:
                logger.info(f"⏰ Cache expired: {cache_key[:16]}... (expired {expires_at})")
                # Delete expired entry
                conn.execute("DELETE FROM search_cache WHERE cache_key = ?", (cache_key,))
                conn.commit()
                return None

            # Cache hit! Update hit stats
            conn.execute("""
                UPDATE search_cache
                SET hit_count = ?, last_hit_at = ?
                WHERE cache_key = ?
            """, (hit_count + 1, now.isoformat(), cache_key))
            conn.commit()

            logger.info(
                f"✅ Cache HIT: {cache_key[:16]}... (hits: {hit_count + 1}, "
                f"expires: {expires_at})"
            )

            return json.loads(results_json)

    def put(
        self,
        query: str,
        context: Dict[str, Any],
        results: list,
        ttl_category: str = "default"
    ):
        """
        Store search results in cache.

        Args:
            query: Search query
            context: Query context
            results: Search results list
            ttl_category: Category for TTL ("regulatory", "pricing", "news", "ai_models", "default")
        """
        cache_key = self._compute_cache_key(query, context)
        context_fingerprint = self._compute_context_fingerprint(context)

        # Determine TTL
        ttl_days = self.TTL_DAYS.get(ttl_category, self.TTL_DAYS["default"])
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=ttl_days)

        # Serialize results
        results_json = json.dumps(results)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO search_cache
                (cache_key, query, context_fingerprint, results_json, ttl_category,
                 created_at, expires_at, hit_count, last_hit_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, NULL)
            """, (
                cache_key,
                query,
                context_fingerprint,
                results_json,
                ttl_category,
                now.isoformat(),
                expires_at.isoformat()
            ))
            conn.commit()

        logger.info(
            f"💾 Cache stored: {cache_key[:16]}... (category={ttl_category}, "
            f"ttl={ttl_days}d, {len(results)} results)"
        )

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns number of entries deleted.
        """
        now = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM search_cache
                WHERE expires_at < ?
            """, (now,))
            deleted = cursor.rowcount
            conn.commit()

        if deleted > 0:
            logger.info(f"🧹 Cache cleanup: {deleted} expired entries removed")

        return deleted

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as total_entries,
                    SUM(hit_count) as total_hits,
                    AVG(hit_count) as avg_hits_per_entry
                FROM search_cache
            """)
            row = cursor.fetchone()
            total_entries, total_hits, avg_hits = row if row else (0, 0, 0.0)

            # Count by category
            cursor = conn.execute("""
                SELECT ttl_category, COUNT(*) as count
                FROM search_cache
                GROUP BY ttl_category
            """)
            by_category = {row[0]: row[1] for row in cursor.fetchall()}

            return {
                "total_entries": total_entries,
                "total_hits": total_hits or 0,
                "avg_hits_per_entry": avg_hits or 0.0,
                "by_category": by_category
            }

    def _compute_cache_key(self, query: str, context: Dict[str, Any]) -> str:
        """
        Compute deterministic cache key.

        Key = hash(normalized_query + context_fingerprint + date_bucket)
        """
        normalized_query = query.lower().strip()
        context_fp = self._compute_context_fingerprint(context)
        date_bucket = self._get_date_bucket()

        content = f"{normalized_query}|{context_fp}|{date_bucket}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _compute_context_fingerprint(self, context: Dict[str, Any]) -> str:
        """
        Compute deterministic fingerprint for context.

        Uses sorted keys to ensure stability.
        """
        # Extract relevant context fields
        relevant_fields = ["industry", "target_markets", "company_size"]
        context_values = []

        for field in relevant_fields:
            value = context.get(field, "")
            if isinstance(value, list):
                value = ",".join(sorted(str(v) for v in value))
            context_values.append(f"{field}={value}")

        return "|".join(context_values)

    def _get_date_bucket(self) -> str:
        """
        Get date bucket for cache key.

        Uses day granularity (YYYY-MM-DD) for most queries.
        """
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def clear_all(self):
        """Clear entire cache (use sparingly)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM search_cache")
            deleted = cursor.rowcount
            conn.commit()

        logger.warning(f"🗑️  Cache cleared: {deleted} entries deleted")
