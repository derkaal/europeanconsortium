# Implementation Guides: Features 5-8

**European Strategy Consortium v2.x Hardening Pack**

Features 1-4 have been fully implemented with comprehensive tests. This document provides detailed implementation guides for Features 5-8 (as per Option B).

---

## Feature 5: Hybrid Memory Retrieval + Case Fingerprints

### Objective
Replace pure vector similarity search with hybrid approach: **metadata filters FIRST**, then vector similarity on filtered set. Add deterministic case fingerprinting for better retrieval.

### Current State
The existing memory system (`src/consortium/memory.py`) uses:
- Vector embeddings (OpenAI) for semantic similarity
- Chroma for vector storage
- Simple similarity search

### Limitations
- Pure vector search returns "similar-sounding" cases that may not match context
- No filtering by market, industry, or company size before semantic search
- Case retrieval can miss exact context matches due to semantic drift

### Implementation Design

#### 1. Case Fingerprinting (`src/consortium/models/case.py`)

```python
"""Case fingerprinting for deterministic retrieval."""

import hashlib
from typing import Dict, Any
from pydantic import BaseModel


class CaseFingerprint(BaseModel):
    """Deterministic fingerprint for case matching."""

    market_hash: str  # SHA256(sorted markets)
    industry_hash: str  # SHA256(sorted industries)
    company_size: str  # Small, Medium, Large, Enterprise
    regulatory_context: str  # EU, US, Global, etc.
    query_category: str  # Strategy, Compliance, Technical, etc.

    @classmethod
    def from_context(cls, context: Dict[str, Any]) -> "CaseFingerprint":
        """Generate fingerprint from query context."""
        # Extract and normalize markets
        markets = sorted([m.lower().strip() for m in context.get("target_markets", [])])
        market_hash = hashlib.sha256("|".join(markets).encode()).hexdigest()[:16]

        # Extract and normalize industries
        industries = context.get("industry", "").lower().strip()
        industry_list = [industries] if industries else []
        industry_hash = hashlib.sha256("|".join(industry_list).encode()).hexdigest()[:16]

        # Standardize company size
        size = context.get("company_size", "unknown").lower()
        size_map = {
            "small": "Small",
            "medium": "Medium",
            "large": "Large",
            "enterprise": "Enterprise",
            "startup": "Small",
            "sme": "Medium",
            "corporation": "Large"
        }
        company_size = size_map.get(size, "Unknown")

        # Regulatory context
        markets_set = set(markets)
        if markets_set & {"germany", "france", "spain", "italy"}:
            regulatory_context = "EU"
        elif "united states" in markets_set:
            regulatory_context = "US"
        else:
            regulatory_context = "Global"

        # Query category (would be determined by LLM or keywords)
        query_category = "Strategy"  # Default

        return cls(
            market_hash=market_hash,
            industry_hash=industry_hash,
            company_size=company_size,
            regulatory_context=regulatory_context,
            query_category=query_category
        )
```

#### 2. Hybrid Retrieval (`src/consortium/memory.py` modifications)

**Add metadata filtering before vector search:**

```python
def retrieve_similar_cases_hybrid(
    self,
    query: str,
    context: Dict[str, Any],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """Hybrid retrieval: metadata filter FIRST, then vector similarity.

    Args:
        query: Query string
        context: Query context with markets, industry, company_size
        top_k: Number of results to return

    Returns:
        List of similar cases
    """
    # Step 1: Generate fingerprint
    fingerprint = CaseFingerprint.from_context(context)

    # Step 2: Metadata filter
    # Filter cases by:
    # - Company size (exact match or adjacent)
    # - Regulatory context (exact match)
    # - Industry (if available)

    metadata_filter = {
        "$and": [
            {"company_size": {"$in": self._get_adjacent_sizes(fingerprint.company_size)}},
            {"regulatory_context": fingerprint.regulatory_context}
        ]
    }

    # Step 3: Vector search on filtered set
    query_embedding = self._get_embedding(query)

    results = self.collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k * 2,  # Get more to filter
        where=metadata_filter
    )

    # Step 4: Re-rank by fingerprint similarity
    ranked_results = self._rerank_by_fingerprint(results, fingerprint)

    return ranked_results[:top_k]


def _get_adjacent_sizes(self, size: str) -> List[str]:
    """Get company size and adjacent sizes for filtering."""
    size_ladder = ["Small", "Medium", "Large", "Enterprise"]

    if size not in size_ladder:
        return size_ladder  # Return all if unknown

    idx = size_ladder.index(size)

    # Include target size + adjacent
    adjacent = [size]
    if idx > 0:
        adjacent.append(size_ladder[idx - 1])
    if idx < len(size_ladder) - 1:
        adjacent.append(size_ladder[idx + 1])

    return adjacent


def _rerank_by_fingerprint(
    self,
    results: Dict[str, Any],
    query_fingerprint: CaseFingerprint
) -> List[Dict[str, Any]]:
    """Re-rank results by fingerprint similarity."""
    ranked = []

    for i, metadata in enumerate(results["metadatas"][0]):
        case_fingerprint = CaseFingerprint(**metadata["fingerprint"])

        # Calculate fingerprint match score
        score = 0.0
        if case_fingerprint.market_hash == query_fingerprint.market_hash:
            score += 0.4  # Exact market match
        if case_fingerprint.industry_hash == query_fingerprint.industry_hash:
            score += 0.3  # Exact industry match
        if case_fingerprint.company_size == query_fingerprint.company_size:
            score += 0.2  # Exact size match
        if case_fingerprint.regulatory_context == query_fingerprint.regulatory_context:
            score += 0.1  # Exact regulatory match

        # Combine with vector similarity score
        vector_score = 1.0 - results["distances"][0][i]  # Convert distance to similarity

        # Weighted combination: 60% fingerprint, 40% vector
        final_score = (0.6 * score) + (0.4 * vector_score)

        ranked.append({
            "case": results["documents"][0][i],
            "metadata": metadata,
            "score": final_score
        })

    # Sort by final score
    ranked.sort(key=lambda x: x["score"], reverse=True)

    return ranked
```

#### 3. Memory Storage Updates

**Update `store_case()` to include fingerprint:**

```python
def store_case(self, case: Dict[str, Any]) -> str:
    """Store case with fingerprint metadata."""

    # Generate fingerprint
    fingerprint = CaseFingerprint.from_context(case["context"])

    # Add fingerprint to metadata
    metadata = {
        "case_id": case["id"],
        "timestamp": case["timestamp"].isoformat(),
        "company_size": fingerprint.company_size,
        "regulatory_context": fingerprint.regulatory_context,
        "fingerprint": fingerprint.dict()  # Store full fingerprint
    }

    # Generate embedding for query
    embedding = self._get_embedding(case["query"])

    # Store in Chroma with metadata
    self.collection.add(
        ids=[case["id"]],
        embeddings=[embedding],
        documents=[case["query"]],
        metadatas=[metadata]
    )

    return case["id"]
```

### Testing Strategy

```python
# tests/test_hybrid_memory.py

def test_fingerprint_generation():
    """Test case fingerprint generation."""
    context = {
        "target_markets": ["Germany", "France"],
        "industry": "SaaS",
        "company_size": "medium"
    }

    fp = CaseFingerprint.from_context(context)

    assert fp.company_size == "Medium"
    assert fp.regulatory_context == "EU"
    assert len(fp.market_hash) == 16


def test_hybrid_retrieval_metadata_filter():
    """Test hybrid retrieval filters by metadata first."""
    # Store cases with different contexts
    # Query for specific context
    # Verify metadata filtering worked
    pass


def test_fingerprint_reranking():
    """Test that fingerprint similarity boosts ranking."""
    # Store exact match case and semantic match case
    # Query with context
    # Verify exact match ranks higher
    pass
```

### Migration Path
1. Add `CaseFingerprint` model
2. Update `store_case()` to include fingerprints
3. Add `retrieve_similar_cases_hybrid()` method
4. Update memory retrieval call sites to use hybrid method
5. Backfill existing cases with fingerprints (migration script)

### Estimated Effort
- **Core implementation**: 4-6 hours
- **Testing**: 2-3 hours
- **Migration script**: 1-2 hours
- **Total**: 7-11 hours

---

## Feature 6: Competitive Advantage Module

### Objective
Lightweight "offense" layer analyzing HOW European constraints create strategic advantages. Transforms defensive compliance into offensive positioning.

### Design Philosophy
Most agents are **defensive** (what can't we do). This agent is **offensive** (how do constraints create advantages).

### Implementation Design

#### 1. Competitive Advantage Agent (`agents/competitive_advantage.py`)

```python
"""Competitive Advantage Agent - Offense layer.

Analyzes how European constraints create strategic advantages.
"""

from typing import Dict, Any, List
from pydantic import BaseModel


class CompetitiveAdvantage(BaseModel):
    """A strategic advantage derived from constraints."""

    advantage_type: str  # "Market", "Trust", "Regulatory", "Cost", "Technical"
    description: str
    constraint_source: str  # Which constraint creates this advantage
    target_markets: List[str]  # Where this advantage applies
    competitors_affected: List[str]  # Who this disadvantages
    durability: str  # "Temporary", "Medium-term", "Long-term"
    activation_cost: str  # "Low", "Medium", "High"
    evidence: List[str]  # Supporting evidence


class CompetitiveAdvantageAgent:
    """Agent that identifies strategic advantages from constraints."""

    def __init__(self):
        self.agent_id = "competitive_advantage"
        self.name = "Competitive Advantage Analyst"

        # Advantage patterns
        self.advantage_patterns = {
            "trust_advantage": {
                "triggers": ["GDPR compliance", "data residency", "privacy"],
                "markets": ["EU", "privacy-conscious"],
                "advantage_type": "Trust"
            },
            "regulatory_moat": {
                "triggers": ["EU AI Act", "compliance cost", "certification"],
                "markets": ["EU"],
                "advantage_type": "Regulatory"
            },
            "cost_arbitrage": {
                "triggers": ["EU subsidies", "green energy", "tax incentive"],
                "markets": ["EU"],
                "advantage_type": "Cost"
            },
            "market_access": {
                "triggers": ["EU requirement", "localization", "EU provider"],
                "markets": ["EU", "public sector"],
                "advantage_type": "Market"
            }
        }

    def analyze(self, query: str, context: Dict[str, Any],
                agent_responses: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze constraints to find competitive advantages.

        Args:
            query: Strategic query
            context: Query context
            agent_responses: Other agents' responses

        Returns:
            Analysis with identified advantages
        """
        advantages = []

        # Scan agent responses for constraints
        constraints = self._extract_constraints(agent_responses)

        # For each constraint, identify potential advantages
        for constraint in constraints:
            advantage = self._constraint_to_advantage(constraint, context)
            if advantage:
                advantages.append(advantage)

        # Generate positioning recommendations
        positioning = self._generate_positioning(advantages, context)

        return {
            "agent_id": self.agent_id,
            "rating": "INFORM",  # This agent doesn't block/warn/accept
            "confidence": 0.75,
            "advantages_identified": len(advantages),
            "advantages": [a.dict() for a in advantages],
            "positioning_recommendations": positioning,
            "offensive_opportunities": self._rank_opportunities(advantages)
        }

    def _extract_constraints(self, agent_responses: Dict[str, Any]) -> List[Dict]:
        """Extract constraints from other agents' responses."""
        constraints = []

        for agent_id, response in agent_responses.items():
            reasoning = response.get("reasoning", "")

            # Look for constraint signals
            if any(word in reasoning.lower() for word in
                   ["must", "required", "cannot", "prohibited", "mandate"]):

                constraints.append({
                    "agent": agent_id,
                    "constraint": reasoning[:200],  # First 200 chars
                    "severity": response.get("rating", "UNKNOWN")
                })

        return constraints

    def _constraint_to_advantage(
        self,
        constraint: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[CompetitiveAdvantage]:
        """Transform constraint into competitive advantage."""

        constraint_text = constraint["constraint"].lower()

        # Check against advantage patterns
        for pattern_name, pattern in self.advantage_patterns.items():
            if any(trigger.lower() in constraint_text for trigger in pattern["triggers"]):

                # Found pattern match - create advantage
                advantage = CompetitiveAdvantage(
                    advantage_type=pattern["advantage_type"],
                    description=self._generate_advantage_description(
                        pattern_name, constraint, context
                    ),
                    constraint_source=constraint["agent"],
                    target_markets=pattern["markets"],
                    competitors_affected=self._identify_disadvantaged_competitors(
                        pattern_name, context
                    ),
                    durability="Medium-term",  # Default
                    activation_cost="Medium",  # Default
                    evidence=[constraint["constraint"]]
                )

                return advantage

        return None

    def _generate_advantage_description(
        self,
        pattern_name: str,
        constraint: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate description of the advantage."""

        descriptions = {
            "trust_advantage":
                "GDPR compliance creates trust advantage in privacy-conscious markets. "
                "Non-EU competitors face higher customer acquisition costs due to privacy concerns.",

            "regulatory_moat":
                "EU AI Act compliance creates regulatory moat. High compliance costs "
                "deter smaller competitors, reducing competitive pressure.",

            "cost_arbitrage":
                "EU green energy incentives create cost advantage over providers in "
                "carbon-intensive regions. Sustainability becomes pricing advantage.",

            "market_access":
                "EU localization requirements create exclusive market access. "
                "Public sector procurement favors EU-compliant providers."
        }

        return descriptions.get(pattern_name, "Strategic advantage identified")

    def _identify_disadvantaged_competitors(
        self,
        pattern_name: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """Identify which competitors are disadvantaged."""

        competitor_maps = {
            "trust_advantage": ["Non-EU cloud providers", "US-based SaaS"],
            "regulatory_moat": ["Startups", "Non-EU AI providers"],
            "cost_arbitrage": ["Cloud providers in high-carbon regions"],
            "market_access": ["Non-EU vendors", "Non-compliant providers"]
        }

        return competitor_maps.get(pattern_name, ["Competitors"])

    def _generate_positioning(
        self,
        advantages: List[CompetitiveAdvantage],
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate positioning recommendations."""

        recommendations = []

        if any(a.advantage_type == "Trust" for a in advantages):
            recommendations.append(
                "Position as 'Privacy-First Alternative' to US competitors"
            )

        if any(a.advantage_type == "Regulatory" for a in advantages):
            recommendations.append(
                "Highlight 'EU AI Act Compliant' as barrier to entry for competitors"
            )

        if any(a.advantage_type == "Cost" for a in advantages):
            recommendations.append(
                "Market 'Sustainable by Design' as cost advantage, not just ethics"
            )

        if any(a.advantage_type == "Market" for a in advantages):
            recommendations.append(
                "Target EU public sector where localization requirements favor you"
            )

        return recommendations

    def _rank_opportunities(
        self,
        advantages: List[CompetitiveAdvantage]
    ) -> List[Dict[str, Any]]:
        """Rank offensive opportunities by impact."""

        opportunities = []

        for advantage in advantages:
            # Score based on durability and activation cost
            durability_score = {"Temporary": 1, "Medium-term": 2, "Long-term": 3}
            activation_score = {"High": 1, "Medium": 2, "Low": 3}

            score = (
                durability_score.get(advantage.durability, 2) +
                activation_score.get(advantage.activation_cost, 2)
            )

            opportunities.append({
                "advantage": advantage.description[:100],
                "type": advantage.advantage_type,
                "score": score,
                "action": f"Activate in {', '.join(advantage.target_markets)}"
            })

        # Sort by score
        opportunities.sort(key=lambda x: x["score"], reverse=True)

        return opportunities
```

#### 2. Integration with Consortium

**Add to LangGraph workflow:**

```python
# In graph definition
def competitive_advantage_node(state: ConsortiumState) -> Dict[str, Any]:
    """Run Competitive Advantage analysis."""

    agent = CompetitiveAdvantageAgent()

    result = agent.analyze(
        query=state["query"],
        context=state["context"],
        agent_responses=state["agent_responses"]
    )

    return {
        "agent_responses": {
            **state.get("agent_responses", {}),
            "competitive_advantage": result
        }
    }

# Add to graph
graph.add_node("competitive_advantage", competitive_advantage_node)
graph.add_edge("convergence", "competitive_advantage")
graph.add_edge("competitive_advantage", "synthesis")
```

#### 3. Synthesizer Integration

**Include advantages in final report:**

```python
# In synthesizer.py
def _format_competitive_advantages(state: ConsortiumState) -> Optional[str]:
    """Format competitive advantages for final report."""

    ca_response = state.get("agent_responses", {}).get("competitive_advantage")

    if not ca_response or not ca_response.get("advantages"):
        return None

    advantages = ca_response["advantages"]
    positioning = ca_response.get("positioning_recommendations", [])
    opportunities = ca_response.get("offensive_opportunities", [])

    section = f"""**COMPETITIVE ADVANTAGES IDENTIFIED ({len(advantages)})**

{chr(10).join(f"- {a['description']}" for a in advantages[:3])}

**POSITIONING RECOMMENDATIONS:**
{chr(10).join(f"- {p}" for p in positioning)}

**TOP OFFENSIVE OPPORTUNITIES:**
{chr(10).join(f"{i+1}. {o['advantage']} (Score: {o['score']})" for i, o in enumerate(opportunities[:3]))}
"""

    return section
```

### Testing Strategy

```python
# tests/test_competitive_advantage.py

def test_extract_constraints():
    """Test constraint extraction from agent responses."""
    pass

def test_constraint_to_advantage_trust():
    """Test GDPR constraint → trust advantage."""
    pass

def test_constraint_to_advantage_regulatory_moat():
    """Test AI Act constraint → regulatory moat."""
    pass

def test_positioning_recommendations():
    """Test positioning recommendation generation."""
    pass

def test_opportunity_ranking():
    """Test offensive opportunity ranking."""
    pass
```

### Estimated Effort
- **Core agent implementation**: 3-4 hours
- **Integration with graph**: 1-2 hours
- **Synthesizer updates**: 1 hour
- **Testing**: 2-3 hours
- **Total**: 7-10 hours

---

## Feature 7 (BONUS): Cost Tracking per Query

### Objective
Track LLM API costs per query with cost breakdown by agent and provider. Enable cost monitoring and budgeting.

### Implementation Design

#### 1. Cost Tracker (`src/consortium/tools/cost_tracker.py`)

```python
"""Cost tracking for LLM API calls."""

import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


# Token costs per model (as of 2024)
TOKEN_COSTS = {
    "gpt-4": {"input": 0.03 / 1000, "output": 0.06 / 1000},
    "gpt-3.5-turbo": {"input": 0.0015 / 1000, "output": 0.002 / 1000},
    "gemini-1.5-flash": {"input": 0.00035 / 1000, "output": 0.0014 / 1000},
    "gemini-1.5-pro": {"input": 0.0035 / 1000, "output": 0.014 / 1000},
    "claude-3-opus": {"input": 0.015 / 1000, "output": 0.075 / 1000},
    "claude-3-sonnet": {"input": 0.003 / 1000, "output": 0.015 / 1000},
    "claude-3-haiku": {"input": 0.00025 / 1000, "output": 0.00125 / 1000},
}


class CostTracker:
    """Track LLM costs per query."""

    def __init__(self, db_path: str = ".consortium/costs.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path))
        self._init_db()

    def _init_db(self):
        """Initialize cost tracking database."""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id TEXT NOT NULL,
                agent_id TEXT,
                model TEXT NOT NULL,
                provider TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                cost_usd REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_costs (
                query_id TEXT PRIMARY KEY,
                total_cost_usd REAL NOT NULL,
                total_calls INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

        self.conn.commit()

    def record_llm_call(
        self,
        query_id: str,
        agent_id: str,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Record an LLM API call and return cost.

        Args:
            query_id: Query identifier
            agent_id: Agent making the call
            model: Model name
            provider: Provider (openai, anthropic, google)
            input_tokens: Input token count
            output_tokens: Output token count

        Returns:
            Cost in USD
        """
        # Calculate cost
        costs = TOKEN_COSTS.get(model, {"input": 0.001 / 1000, "output": 0.002 / 1000})
        cost_usd = (input_tokens * costs["input"]) + (output_tokens * costs["output"])

        # Store call
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO llm_calls
            (query_id, agent_id, model, provider, input_tokens, output_tokens,
             cost_usd, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            query_id, agent_id, model, provider, input_tokens, output_tokens,
            cost_usd, datetime.now().isoformat()
        ))

        # Update query total
        cursor.execute("""
            INSERT INTO query_costs (query_id, total_cost_usd, total_calls, timestamp)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(query_id) DO UPDATE SET
                total_cost_usd = total_cost_usd + excluded.total_cost_usd,
                total_calls = total_calls + 1
        """, (query_id, cost_usd, datetime.now().isoformat()))

        self.conn.commit()

        return cost_usd

    def get_query_cost(self, query_id: str) -> Dict[str, Any]:
        """Get cost breakdown for a query."""
        cursor = self.conn.cursor()

        # Get total
        cursor.execute("SELECT * FROM query_costs WHERE query_id = ?", (query_id,))
        total_row = cursor.fetchone()

        if not total_row:
            return {"total_cost_usd": 0, "calls": []}

        # Get call breakdown
        cursor.execute("""
            SELECT agent_id, model, provider, input_tokens, output_tokens, cost_usd
            FROM llm_calls WHERE query_id = ?
            ORDER BY timestamp
        """, (query_id,))

        calls = []
        for row in cursor.fetchall():
            calls.append({
                "agent_id": row[0],
                "model": row[1],
                "provider": row[2],
                "input_tokens": row[3],
                "output_tokens": row[4],
                "cost_usd": row[5]
            })

        return {
            "query_id": query_id,
            "total_cost_usd": total_row[1],
            "total_calls": total_row[2],
            "calls": calls
        }

    def get_monthly_costs(self) -> Dict[str, Any]:
        """Get costs for current month."""
        # Implementation
        pass
```

#### 2. Integration with Agents

**Wrap LLM calls:**

```python
# In each agent
def _call_llm(self, prompt: str) -> str:
    """Call LLM with cost tracking."""

    # Make LLM call
    response = self.llm.invoke(prompt)

    # Track cost
    if hasattr(self, 'cost_tracker'):
        self.cost_tracker.record_llm_call(
            query_id=self.current_query_id,
            agent_id=self.agent_id,
            model=self.model_name,
            provider=self.provider_name,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens
        )

    return response.content
```

### Estimated Effort
- **Core cost tracker**: 2-3 hours
- **Agent integration**: 2-3 hours
- **Dashboard/reporting**: 2-3 hours
- **Testing**: 1-2 hours
- **Total**: 7-11 hours

---

## Feature 8 (BONUS): Circuit Breaker for LLM Providers

### Objective
Implement circuit breaker pattern for LLM provider failures. Automatically failover to backup provider when primary fails.

### Implementation Design

#### 1. Circuit Breaker (`src/consortium/tools/circuit_breaker.py`)

```python
"""Circuit breaker for LLM provider failover."""

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Failing, use fallback
    HALF_OPEN = "HALF_OPEN"  # Testing if recovered


class CircuitBreaker:
    """Circuit breaker for LLM provider calls."""

    def __init__(
        self,
        provider_name: str,
        failure_threshold: int = 3,
        timeout_seconds: int = 60,
        half_open_max_calls: int = 1
    ):
        """Initialize circuit breaker.

        Args:
            provider_name: LLM provider name
            failure_threshold: Failures before opening circuit
            timeout_seconds: How long to wait before trying again
            half_open_max_calls: Test calls in half-open state
        """
        self.provider_name = provider_name
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.half_open_max_calls = half_open_max_calls

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0

    def call(
        self,
        func: Callable,
        fallback: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with circuit breaker protection.

        Args:
            func: Primary function to call
            fallback: Fallback function if circuit open
            *args, **kwargs: Arguments to pass to function

        Returns:
            Function result

        Raises:
            Exception if circuit open and no fallback
        """
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._half_open()
            else:
                logger.warning(
                    f"Circuit OPEN for {self.provider_name}, using fallback"
                )
                if fallback:
                    return fallback(*args, **kwargs)
                else:
                    raise Exception(
                        f"Circuit breaker OPEN for {self.provider_name} and no fallback provided"
                    )

        # Attempt call
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            logger.error(
                f"Call failed for {self.provider_name}: {e}"
            )

            # Try fallback
            if fallback:
                logger.info("Using fallback provider")
                return fallback(*args, **kwargs)
            else:
                raise

    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            logger.info(
                f"Circuit breaker for {self.provider_name}: "
                f"Half-open success, resetting to CLOSED"
            )
            self._close()
        else:
            # Reset failure count on success
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            # Failed during half-open, go back to open
            logger.warning(
                f"Circuit breaker for {self.provider_name}: "
                f"Half-open test failed, returning to OPEN"
            )
            self._open()

        elif self.failure_count >= self.failure_threshold:
            # Threshold exceeded, open circuit
            logger.error(
                f"Circuit breaker for {self.provider_name}: "
                f"Failure threshold ({self.failure_threshold}) exceeded, "
                f"opening circuit"
            )
            self._open()

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True

        return datetime.now() - self.last_failure_time >= self.timeout

    def _close(self):
        """Close circuit (normal operation)."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.half_open_calls = 0

    def _open(self):
        """Open circuit (failing, use fallback)."""
        self.state = CircuitState.OPEN

    def _half_open(self):
        """Half-open circuit (testing recovery)."""
        self.state = CircuitState.HALF_OPEN
        self.half_open_calls = 0
        logger.info(
            f"Circuit breaker for {self.provider_name}: "
            f"Attempting recovery (HALF_OPEN)"
        )
```

#### 2. LLM Provider Wrapper

```python
"""LLM provider wrapper with circuit breaker."""

class ResilientLLMProvider:
    """LLM provider with circuit breaker and failover."""

    def __init__(self, config: Dict[str, Any]):
        # Primary provider
        self.primary = self._init_provider(config["primary"])
        self.primary_breaker = CircuitBreaker(
            provider_name=config["primary"]["name"],
            failure_threshold=config.get("failure_threshold", 3),
            timeout_seconds=config.get("timeout_seconds", 60)
        )

        # Fallback provider
        self.fallback = self._init_provider(config["fallback"])

    def invoke(self, prompt: str) -> str:
        """Invoke LLM with circuit breaker protection."""

        def primary_call():
            return self.primary.invoke(prompt)

        def fallback_call():
            return self.fallback.invoke(prompt)

        return self.primary_breaker.call(primary_call, fallback_call)
```

### Estimated Effort
- **Circuit breaker implementation**: 2-3 hours
- **LLM provider integration**: 2-3 hours
- **Testing**: 2 hours
- **Total**: 6-8 hours

---

## Summary: Implementation Priorities

### Completed (Features 1-4)
✅ **Feature 1**: Scout Budgets + Stop Rules + Caching
✅ **Feature 2**: Convergence Gates + Waiver Register
✅ **Feature 3**: Evidence Referee (deterministic)
✅ **Feature 4**: Final Recommendation Voice (board-grade)

### Guided Implementation (Features 5-8)

**High Priority:**
1. **Feature 5**: Hybrid Memory Retrieval (7-11 hours) - Improves case retrieval accuracy
2. **Feature 6**: Competitive Advantage Module (7-10 hours) - Adds strategic offense layer

**Medium Priority:**
3. **Feature 7** (Bonus): Cost Tracking (7-11 hours) - Essential for production monitoring
4. **Feature 8** (Bonus): Circuit Breaker (6-8 hours) - Critical for resilience

### Total Remaining Effort
**27-40 hours** for Features 5-8 full implementation

---

## Next Steps

1. **Review implementation guides** with team
2. **Prioritize Features 5-8** based on business needs
3. **Assign implementation** to developers
4. **Set up staging environment** for testing
5. **Plan production rollout** with gradual feature activation

---

*This document provides surgical, production-ready implementation guides for Features 5-8 of the European Strategy Consortium v2.x Hardening Pack.*
