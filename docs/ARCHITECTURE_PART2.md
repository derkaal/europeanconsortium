# ARCHITECTURE - Phase A (Part 2 of 3)

**Project**: European Strategy Consortium Multi-Agent System  
**Methodology**: SPARC Phase A (Architecture)  
**Date**: 2024-12-24

---

## 5. MEMORY ARCHITECTURE - CHROMA SPECIFICS

### 5.1 Collection Structure

**Decision**: **Single collection** for all cases with rich metadata filtering.

**Rationale**:
- ✅ Simpler architecture (one collection to manage)
- ✅ Cross-domain case retrieval (Sovereign cases can inform Economist decisions)
- ✅ Chroma supports efficient metadata filtering
- ❌ Alternative (separate collections per agent) would fragment knowledge

### 5.2 Chroma Setup and Configuration

```python
import chromadb
from chromadb.config import Settings
import json

class ConsortiumMemorySystem:
    """Memory system using ChromaDB - Hybrid B+C approach"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="consortium_cases",
            metadata={
                "description": "Historical cases for European Strategy Consortium",
                "hnsw:space": "cosine"  # Cosine similarity
            }
        )
        
        # Initialize embedding function
        from chromadb.utils import embedding_functions
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"  # 1536 dimensions
        )
    
    def store_case(self, case: Case) -> str:
        """Store new case in memory system"""
        
        # Generate embedding from query + context + recommendation
        embedding_text = self._create_embedding_text(case)
        embedding = self.embedding_function([embedding_text])[0]
        
        # Prepare metadata for filtering
        # Note: Chroma metadata values must be str, int, float, or bool
        # Complex objects must be JSON-serialized
        metadata = {
            "timestamp": case["timestamp"].isoformat(),
            "agents_engaged": json.dumps(case["agents_engaged"]),
            "quality_score": case["user_feedback"].get("quality_score", 0.0),
            "outcome_status": case["outcome"].get("status", "not_implemented"),
            "alignment_score": case["outcome"].get("alignment_score", 0.0),
            "query_length": len(case["query"]),
            "industry": case["context"].get("industry", "unknown")
        }
        
        # Store in Chroma
        self.collection.add(
            ids=[case["id"]],
            embeddings=[embedding],
            documents=[embedding_text],
            metadatas=[metadata]
        )
        
        return case["id"]
    
    def retrieve_cases(
        self,
        query: str,
        top_k: int = 10,
        quality_threshold: float = 3.5
    ) -> Dict[str, Any]:
        """Retrieve relevant cases with progressive threshold fallback"""
        
        # Generate query embedding
        query_embedding = self.embedding_function([query])[0]
        
        # Initial query with quality filter
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"quality_score": {"$gte": quality_threshold}},
            include=["documents", "metadatas", "distances"]
        )
        
        filtered_cases = []
        confidence_penalty = 0.0
        
        # Progressive threshold fallback (from pseudocode)
        if len(results["ids"][0]) == 0:
            quality_threshold = 3.0
            confidence_penalty = -0.20
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"quality_score": {"$gte": quality_threshold}},
                include=["documents", "metadatas", "distances"]
            )
            
            if len(results["ids"][0]) == 0:
                quality_threshold = 2.5
                confidence_penalty = -0.25
                
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where={"quality_score": {"$gte": quality_threshold}},
                    include=["documents", "metadatas", "distances"]
                )
        
        # Convert results to Case objects with outcome-based weighting
        for i, case_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]
            similarity_score = 1.0 - distance
            
            # Apply outcome-based weighting (Hybrid C component)
            enhanced_score = similarity_score
            boost_reason = "immediate_feedback_only"
            
            if metadata["outcome_status"] == "implemented":
                if metadata["alignment_score"] >= 4.0:
                    enhanced_score *= 1.5  # 50% boost
                    boost_reason = "verified_positive_outcome"
                elif metadata["alignment_score"] < 3.0:
                    enhanced_score *= 0.7  # 30% penalty
                    boost_reason = "verified_negative_outcome"
            
            case = {
                "id": case_id,
                "query": results["documents"][0][i],
                "similarity_score": similarity_score,
                "enhanced_score": enhanced_score,
                "boost_reason": boost_reason,
                "metadata": metadata
            }
            
            filtered_cases.append(case)
        
        # Sort by enhanced score and take top 3
        filtered_cases.sort(key=lambda c: c["enhanced_score"], reverse=True)
        top_cases = filtered_cases[:3]
        
        # Metadata
        retrieval_metadata = MemoryMetadata(
            total_matches=len(results["ids"][0]),
            quality_filtered=len(filtered_cases),
            returned=len(top_cases),
            cold_start=len(top_cases) == 0,
            confidence_adjustment=confidence_penalty if len(top_cases) == 0 else 0.0,
            warning="No historical precedent found" if len(top_cases) == 0 else None
        )
        
        return {
            "cases": top_cases,
            "retrieval_metadata": retrieval_metadata
        }
    
    def update_case_outcome(self, case_id: str, outcome: Outcome) -> bool:
        """
        Update existing case with long-term outcome.
        
        Strategy: Delete and re-insert with updated metadata
        (Chroma doesn't support in-place updates)
        """
        
        try:
            # Get existing case
            existing = self.collection.get(
                ids=[case_id],
                include=["documents", "embeddings", "metadatas"]
            )
            
            if not existing["ids"]:
                return False
            
            # Update metadata
            metadata = existing["metadatas"][0]
            metadata["outcome_status"] = outcome.get("status", "not_implemented")
            metadata["alignment_score"] = outcome.get("alignment_score", 0.0)
            
            # Delete old entry
            self.collection.delete(ids=[case_id])
            
            # Re-insert with updated metadata
            self.collection.add(
                ids=[case_id],
                embeddings=[existing["embeddings"][0]],
                documents=[existing["documents"][0]],
                metadatas=[metadata]
            )
            
            return True
        
        except Exception as e:
            print(f"Error updating case {case_id}: {e}")
            return False
    
    def _create_embedding_text(self, case: Case) -> str:
        """
        Create text for embedding generation.
        Combines query, context, and recommendation.
        """
        
        parts = [
            f"Query: {case['query']}",
            f"Industry: {case['context'].get('industry', 'N/A')}",
            f"Company Size: {case['context'].get('company_size', 'N/A')}",
            f"Recommendation: {case['final_recommendation']['recommendation']}",
            f"Agents: {', '.join(case['agents_engaged'])}"
        ]
        
        return "\n".join(parts)
```

### 5.3 Metadata Schema for Chroma

```python
# Metadata fields stored in Chroma (all must be primitive types)
CHROMA_METADATA_SCHEMA = {
    "timestamp": "str",  # ISO format datetime
    "agents_engaged": "str",  # JSON-serialized list
    "quality_score": "float",  # 1-5 scale (0.0 if not yet rated)
    "outcome_status": "str",  # not_implemented, in_progress, implemented, abandoned
    "alignment_score": "float",  # 1-5 scale (0.0 if not yet verified)
    "query_length": "int",  # For filtering complex vs simple queries
    "industry": "str",  # For domain-specific filtering
    "has_sovereignty_tension": "bool",  # Quick filter
    "has_environmental_tension": "bool",  # Quick filter
}
```

### 5.4 Embedding Strategy

**Decision**: Embed **query + context + recommendation** (not full transcript).

**Rationale**:
- ✅ Captures semantic essence (~500 tokens vs 10K+ for full transcript)
- ✅ Faster embedding generation
- ✅ Detailed transcript still stored in relational DB for audit
- ❌ Alternative (full transcript) would be expensive and slow

---

## 6. MULTI-LLM PROVIDER STRATEGY

### 6.1 Provider Priority Configuration

```yaml
# config/providers.yaml

providers:
  - name: anthropic
    priority: 1  # Primary provider
    api_key_env: ANTHROPIC_API_KEY
    models:
      default: claude-sonnet-4-20250514
    timeout_seconds: 30
    max_retries: 2
    
  - name: mistral
    priority: 2  # Secondary (European sovereignty preference)
    api_key_env: MISTRAL_API_KEY
    models:
      default: mistral-large-latest
    timeout_seconds: 30
    max_retries: 2
    
  - name: openai
    priority: 3  # Tertiary fallback
    api_key_env: OPENAI_API_KEY
    models:
      default: gpt-4-turbo-preview
    timeout_seconds: 30
    max_retries: 2

retry_strategy:
  base_delay_seconds: 1.0  # Initial delay
  exponential_backoff: true  # 1s, 2s, 4s, ...
  max_delay_seconds: 10.0  # Cap backoff at 10s
  jitter: 0.1  # Add ±10% random jitter
```

### 6.2 Retry Logic with Exponential Backoff

```python
import time
import random

def exponential_backoff_with_jitter(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    jitter: float = 0.1
) -> float:
    """
    Calculate delay for exponential backoff with jitter.
    
    Formula: delay = min(base_delay * 2^attempt, max_delay) ± jitter%
    """
    
    # Exponential backoff
    delay = min(base_delay * (2 ** attempt), max_delay)
    
    # Add jitter
    jitter_amount = delay * jitter
    delay += random.uniform(-jitter_amount, jitter_amount)
    
    return max(0.1, delay)  # Minimum 0.1s delay
```

### 6.3 Provider Failover Manager

```python
class LLMProviderManager:
    """Manages multi-provider failover with exponential backoff"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = self._initialize_providers()
        self.retry_attempts = config.get("retry_attempts", 2)
        self.base_delay = config.get("base_delay_seconds", 1.0)
        self.timeout = config.get("timeout_seconds", 30)
    
    def invoke_with_failover(
        self,
        agent_id: str,
        prompt: str,
        state: ConsortiumState
    ) -> str:
        """
        Invoke LLM with automatic failover on failure.
        Preserves conversation state across failovers.
        """
        
        last_exception = None
        
        for provider_info in self.providers:
            provider_name = provider_info["name"]
            provider = provider_info["instance"]
            
            # Attempt with retry and exponential backoff
            for attempt in range(self.retry_attempts):
                try:
                    result = provider.invoke(
                        prompt,
                        {
                            "max_tokens": 4096,
                            "temperature": 0.7,
                            "timeout": self.timeout
                        }
                    )
                    
                    # Success - log and return
                    state["provider_used"][agent_id] = provider_name
                    
                    state["audit_trail"].append({
                        "event_id": generate_uuid(),
                        "trace_id": state["trace_id"],
                        "event_type": "llm_invocation",
                        "agent_id": agent_id,
                        "details": {
                            "provider": provider_name,
                            "attempt": attempt + 1,
                            "latency_ms": result["latency_ms"],
                            "tokens": result["token_count"]
                        },
                        "timestamp": datetime.now()
                    })
                    
                    return result["response"]
                
                except (ProviderTimeoutError, ProviderRateLimitError, ProviderAPIError) as e:
                    last_exception = e
                    
                    # Log failure
                    state["provider_failures"].append({
                        "provider": provider_name,
                        "agent_id": agent_id,
                        "failure_type": type(e).__name__,
                        "error_message": str(e),
                        "timestamp": datetime.now()
                    })
                    
                    # Exponential backoff before retry
                    if attempt < self.retry_attempts - 1:
                        delay = self.base_delay * (2 ** attempt)
                        time.sleep(delay)
            
            # Log failover event
            if provider_info != self.providers[-1]:
                next_provider = self.providers[self.providers.index(provider_info) + 1]
                
                state["failover_events"].append({
                    "from_provider": provider_name,
                    "to_provider": next_provider["name"],
                    "agent_id": agent_id,
                    "reason": f"Provider failed after {self.retry_attempts} attempts",
                    "state_preserved": True,
                    "timestamp": datetime.now()
                })
        
        # All providers failed
        raise AllProvidersFailedError(
            f"All {len(self.providers)} providers failed for agent {agent_id}"
        )
```

### 6.4 Testing Failover

```python
class MockFailingProvider(LLMProvider):
    """Mock provider for testing failover logic"""
    
    def __init__(self, failure_type: str = "timeout", fail_after: int = 0):
        self.failure_type = failure_type
        self.fail_after = fail_after
        self.invocation_count = 0
    
    def invoke(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        self.invocation_count += 1
        
        if self.invocation_count > self.fail_after:
            if self.failure_type == "timeout":
                raise ProviderTimeoutError("Simulated timeout")
            elif self.failure_type == "rate_limit":
                raise ProviderRateLimitError("Simulated rate limit")
        else:
            return {
                "response": "Mock response",
                "latency_ms": 100.0,
                "token_count": 50,
                "model_used": "mock-model"
            }
    
    def health_check(self) -> bool:
        return False


# Test case
def test_provider_failover():
    """Test that failover works correctly"""
    
    config = {
        "providers": [
            {"name": "mock_failing", "priority": 1, 
             "instance": MockFailingProvider("timeout", fail_after=0)},
            {"name": "mock_working", "priority": 2, 
             "instance": MockWorkingProvider()}
        ],
        "retry_attempts": 2,
        "base_delay_seconds": 0.1
    }
    
    manager = LLMProviderManager(config)
    state = create_test_state()
    
    response = manager.invoke_with_failover("TestAgent", "test prompt", state)
    
    assert response == "Mock response"
    assert len(state["failover_events"]) == 1
    assert state["failover_events"][0]["state_preserved"] == True
```

---

## 7. KNOWLEDGE & TOOLS STRATEGY

### 7.1 Three-Tier Knowledge Architecture

```python
class KnowledgeAccessRouter:
    """
    Routes knowledge access across three tiers.
    Tier 1: Static vector DB (fast, stable regulations)
    Tier 2: Dynamic web search (current information)
    Tier 3: Agent system prompts (always active, loaded from YAML)
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize Tier 1: Static knowledge base
        self.static_kb = chromadb.PersistentClient(path="./knowledge_db")
        self.regulations_collection = self.static_kb.get_or_create_collection(
            name="eu_regulations"
        )
        
        # Initialize Tier 2: Dynamic search cache
        self.search_cache = {}
        self.cache_ttl_seconds = config["tier2_dynamic"]["cache_ttl_hours"] * 3600
    
    def route_knowledge_access(
        self,
        query: str,
        static_confidence: float = 0.8
    ) -> Dict[str, Any]:
        """Routes knowledge access based on query characteristics"""
        
        # Check for date/recency keywords
        date_keywords = ["latest", "current", "recent", "new", "today", "2024", "2025"]
        contains_date_keyword = any(kw in query.lower() for kw in date_keywords)
        
        if contains_date_keyword:
            return self.use_hybrid_tier_1_and_2(query)
        elif static_confidence < 0.7:
            return self.use_hybrid_tier_1_and_2(query)
        else:
            return self.use_tier_1_only(query)
    
    def use_tier_1_only(self, query: str) -> Dict[str, Any]:
        """Retrieve from static vector DB only (<500ms target)"""
        
        from openai import OpenAI
        client = OpenAI()
        
        # Generate embedding
        embedding_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = embedding_response.data[0].embedding
        
        # Query static knowledge base
        results = self.regulations_collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        # Compile knowledge
        knowledge = {
            "retrieved_documents": [],
            "combined_confidence": 0.0
        }
        
        for i, doc_id in enumerate(results["ids"][0]):
            knowledge["retrieved_documents"].append({
                "document": results["documents"][0][i],
                "source": results["metadatas"][0][i].get("source", "Static KB"),
                "relevance": 1.0 - results["distances"][0][i],
                "chunk_text": results["documents"][0][i]
            })
        
        if results["distances"][0]:
            knowledge["combined_confidence"] = 1.0 - sum(results["distances"][0]) / len(results["distances"][0])
        
        return {
            "knowledge": knowledge,
            "confidence": knowledge["combined_confidence"],
            "sources": [doc["source"] for doc in knowledge["retrieved_documents"]],
            "tier": "tier_1_static"
        }
    
    def use_hybrid_tier_1_and_2(self, query: str) -> Dict[str, Any]:
        """Combine static DB + dynamic web search"""
        
        # Get static knowledge
        static_knowledge = self.use_tier_1_only(query)
        
        # Get dynamic knowledge
        dynamic_knowledge = self.use_tier_2_dynamic(query)
        
        # Combine with weighting (static 70%, dynamic 30%)
        combined_docs = []
        
        for doc in static_knowledge["knowledge"]["retrieved_documents"]:
            doc["weighted_relevance"] = doc["relevance"] * 0.7
            doc["source_type"] = "static_regulatory_db"
            combined_docs.append(doc)
        
        for doc in dynamic_knowledge["knowledge"]["retrieved_documents"]:
            doc["weighted_relevance"] = doc["relevance"] * 0.3
            doc["source_type"] = "dynamic_web_search"
            combined_docs.append(doc)
        
        # Sort by weighted relevance
        combined_docs.sort(key=lambda d: d["weighted_relevance"], reverse=True)
        
        # Detect conflicts
        conflicts = self.detect_knowledge_conflicts(
            static_knowledge["knowledge"],
            dynamic_knowledge["knowledge"]
        )
        
        # Combined confidence
        combined_confidence = (
            static_knowledge["confidence"] * 0.7 +
            dynamic_knowledge["confidence"] * 0.3
        )
        
        return {
            "knowledge": {"combined_documents": combined_docs},
            "confidence": combined_confidence,
            "sources": static_knowledge["sources"] + dynamic_knowledge["sources"],
            "conflicts": conflicts,
            "tier": "hybrid_static_dynamic"
        }
    
    def use_tier_2_dynamic(self, query: str) -> Dict[str, Any]:
        """Dynamic web search with sovereignty safeguards"""
        
        # Check cache first
        cache_key = f"dynamic_{hash(query)}"
        if cache_key in self.search_cache:
            cached_result, cached_time = self.search_cache[cache_key]
            if time.time() - cached_time < self.cache_ttl_seconds:
                return cached_result
        
        dynamic_results = []
        
        # Priority 1: EUR-Lex (EU official legal database)
        eurlex_results = self.search_eurlex(query)
        for result in eurlex_results:
            result["priority"] = "primary_eu_source"
            result["sovereignty_flagged"] = False
            dynamic_results.append(result)
        
        # Priority 2: European Commission websites
        ec_results = self.search_european_commission(query)
        for result in ec_results:
            result["priority"] = "secondary_eu_source"
            result["sovereignty_flagged"] = False
            dynamic_results.append(result)
        
        # Priority 3: General web search (if needed)
        if len(dynamic_results) < 3:
            web_results = self.search_general_web(query)
            for result in web_results:
                # Flag non-EU sources
                if not self.is_eu_hosted(result.get("domain", "")):
                    result["sovereignty_flagged"] = True
                    self.log_sovereignty_access(result["url"], query)
                else:
                    result["sovereignty_flagged"] = False
                
                result["priority"] = "fallback_external"
                dynamic_results.append(result)
        
        # Compile knowledge
        knowledge = {
            "retrieved_documents": dynamic_results,
            "eu_sources_count": sum(1 for r in dynamic_results if not r["sovereignty_flagged"]),
            "external_sources_count": sum(1 for r in dynamic_results if r["sovereignty_flagged"])
        }
        
        # Calculate confidence
        confidence = self.calculate_dynamic_confidence(dynamic_results)
        
        result = {
            "knowledge": knowledge,
            "confidence": confidence,
            "sources": [r.get("url", "Unknown") for r in dynamic_results],
            "sovereignty_flagged": knowledge["external_sources_count"] > 0,
            "tier": "dynamic_web_search"
        }
        
        # Cache result (24-hour TTL)
        self.search_cache[cache_key] = (result, time.time())
        
        return result
    
    def calculate_dynamic_confidence(self, dynamic_results: List[Dict]) -> float:
        """Calculates confidence score based on source quality"""
        
        confidence = 0.5  # Base confidence
        
        # Boost for EU primary sources
        eu_primary_count = sum(1 for r in dynamic_results if r["priority"] == "primary_eu_source")
        confidence += eu_primary_count * 0.15  # +15% per EUR-Lex source
        
        # Boost for EU secondary sources
        eu_secondary_count = sum(1 for r in dynamic_results if r["priority"] == "secondary_eu_source")
        confidence += eu_secondary_count * 0.10  # +10% per EC source
        
        # Penalty if all sources are external
        external_only = sum(1 for r in dynamic_results if r["sovereignty_flagged"]) == len(dynamic_results)
        if external_only:
            confidence -= 0.2
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def log_sovereignty_access(self, url: str, query: str):
        """Logs access to non-EU sources for audit compliance"""
        
        audit_log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "external_source_access",
            "url": url,
            "query": query,
            "domain": self.extract_domain(url),
            "is_eu_hosted": False,
            "reason": "Insufficient EU sources available"
        }
        
        # Append to audit log file
        with open("./logs/sovereignty_access.jsonl", "a") as f:
            f.write(json.dumps(audit_log_entry) + "\n")
```

### 7.2 Static Knowledge Base Setup

```python
def populate_static_knowledge_base():
    """
    One-time setup to populate Tier 1 static knowledge base.
    
    Sources:
    - EU AI Act (complete text)
    - GDPR (complete text)
    - DSA (complete text)
    - DMA (complete text)
    - Gaia-X specifications
    - Green Software Foundation documentation
    """
    
    knowledge_router = KnowledgeAccessRouter(config)
    
    # Example: Load GDPR
    with open("./knowledge_sources/gdpr.txt", "r") as f:
        gdpr_text = f.read()
    
    # Chunk into 500-1000 token segments with 100-token overlap
    chunks = chunk_text(gdpr_text, chunk_size=800, overlap=100)
    
    # Generate embeddings for each chunk
    from openai import OpenAI
    client = OpenAI()
    
    for i, chunk in enumerate(chunks):
        embedding_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk
        )
        
        embedding = embedding_response.data[0].embedding
        
        knowledge_router.regulations_collection.add(
            ids=[f"gdpr_chunk_{i}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{
                "source": "GDPR",
                "chunk_index": i,
                "regulation_type": "privacy"
            }]
        )
    
    # Repeat for AI Act, DSA, DMA, etc.
```

---

**[END OF PART 2]**

**Continue to Part 3 for**:
- Configuration Management (with concrete YAML examples)
- Testing Strategy (with complete test case)
- Observability & Debugging
- Architecture Decision Trade-offs
- Performance Targets & Implications
- Technology Stack
- Implementation Guidance & Risk Assessment
