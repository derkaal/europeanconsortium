# ARCHITECTURE - Phase A (Part 3 of 3)

**Project**: European Strategy Consortium Multi-Agent System  
**Methodology**: SPARC Phase A (Architecture)  
**Date**: 2024-12-24

---

## 8. CONFIGURATION MANAGEMENT

### 8.1 Directory Structure

```
config/
├── agents/
│   ├── sovereign.yaml
│   ├── economist.yaml
│   ├── jurist.yaml
│   ├── ecosystem.yaml
│   ├── architect.yaml
│   ├── philosopher.yaml
│   ├── ethnographer.yaml
│   ├── technologist.yaml
│   ├── consumer_voice.yaml
│   ├── futurist.yaml
│   └── operator.yaml
├── tensions/
│   ├── sovereign_economist.yaml
│   ├── ecosystem_architect.yaml
│   ├── jurist_philosopher.yaml
│   ├── operator_strategy.yaml
│   └── futurist_all.yaml
├── convergence.yaml
├── providers.yaml
└── system.yaml
```

### 8.2 Agent Configuration Example

```yaml
# config/agents/sovereign.yaml

agent_id: sovereign
name: "The Sovereign"
mandate: "Prevent vendor lock-in and extraterritorial exposure. Data is Territory."

system_prompt: |
  You are The Sovereign, Guardian of Digital Autonomy for the European Strategy Consortium.
  
  Your core mandate is to ensure that all business strategies preserve European digital sovereignty.
  You operate on the principle that "Data is Territory" - any strategy that subjects European
  data or intellectual property to non-EU jurisdiction is a violation of sovereignty.
  
  You are deeply knowledgeable about:
  - Gaia-X Architecture and Trust Framework
  - Confidential Computing (Intel TDX, AMD SEV-SNP)
  - Trusted Execution Environments (TEEs)
  - External Key Management (EKM) standards
  - US CLOUD Act implications
  - Chinese National Intelligence Law
  - EU Data Governance Act
  - Digital Markets Act portability requirements
  
  When evaluating proposals, your primary concern is preventing:
  1. Vendor lock-in through proprietary APIs
  2. Data flows subject to foreign subpoena power
  3. Services claiming compliance without true sovereignty guarantees
  4. Inability to migrate workloads without total refactoring
  
  You are adversarial by design. Your job is to identify sovereignty risks that others miss.
  You must be specific about the attack vectors you identify and provide concrete evidence
  from your knowledge domains.
  
  Rate proposals using this framework:
  - BLOCK: Data residency cannot be guaranteed EU-only OR migration cost >50% of initial implementation
  - WARN: Foreign providers without EKM or TEE guarantees
  - ACCEPT: Hybrid architectures with clear sovereignty boundaries
  - ENDORSE: Fully sovereign stack with open standards and proven portability

red_lines:
  - "Data subject to non-EU intelligence laws"
  - "Proprietary lock-in without escape clauses in contracts"
  - "Missing data sovereignty guarantees in vendor SLAs"

acceptance_criteria:
  block: "Data residency cannot be guaranteed EU-only OR migration cost >50% of initial implementation"
  warn: "Foreign providers without EKM or TEE guarantees"
  accept: "Hybrid architectures with clear sovereignty boundaries"
  endorse: "Fully sovereign stack with open standards and proven portability"

knowledge_domains:
  - "Gaia-X Architecture and Trust Framework"
  - "Distinction between Gaia-X Sovereign vs Gaia-X Compliant"
  - "Confidential Computing (Intel TDX, AMD SEV-SNP)"
  - "Trusted Execution Environments (TEEs)"
  - "Zero Trust architecture"
  - "US CLOUD Act"
  - "Chinese National Intelligence Law"
  - "EU Data Governance Act"
  - "Digital Markets Act portability requirements"
  - "External Key Management (EKM)"

# Example attack patterns (for reference, not in prompt)
example_attack_patterns:
  - "Deep coupling with AWS Lambda creates unacceptable lock-in"
  - "Google BigQuery subjects EU data to US CLOUD Act"
  - "Missing EKM means encryption keys accessible to provider"
  - "Proprietary APIs prevent migration to sovereign cloud"
```

### 8.3 Tension Protocol Configuration Example

```yaml
# config/tensions/sovereign_economist.yaml

protocol_id: sovereign_economist
name: "Sovereign ↔ Economist Tension"
description: "Resolves conflict between sovereignty requirements and economic viability"

agents:
  - sovereign
  - economist

trigger:
  # Trigger when both conditions are met
  conditions:
    - agent: sovereign
      rating: BLOCK
      keywords: ["EU-only", "sovereignty", "vendor lock-in", "data residency"]
    - agent: economist
      rating: BLOCK
      threshold_mentioned: 0.40  # Cost premium >40%

max_iterations: 4

resolution_steps:
  - step: 1
    action: "Economist calculates Trust Premium"
    inputs:
      - "European market preference data"
      - "Sovereignty requirement specifics"
      - "Historical cases with similar positioning"
    outputs:
      - "Projected revenue increase"
      - "Confidence level"
  
  - step: 2
    action: "Sovereign quantifies sovereignty risk"
    inputs:
      - "Sovereignty requirement"
      - "Query context (industry, data sensitivity)"
    outputs:
      - "Breach probability"
      - "Financial impact if breached"
      - "Risk mitigation value"
  
  - step: 3
    action: "Compare combined value vs cost delta"
    logic: |
      IF (trust_premium + risk_mitigation_value) > cost_delta THEN
        Resolution: Accept sovereign approach
      ELSE
        Proceed to Step 4
  
  - step: 4
    action: "Architect proposes hybrid architecture"
    inputs:
      - "Sovereignty requirement"
      - "Acceptable cost delta"
    outputs:
      - "Hybrid proposal"
      - "Cost estimate"
  
  - step: 5
    action: "Evaluate hybrid proposal"
    participants:
      - sovereign
      - economist
    success_criteria:
      - "Both agents rate ACCEPT or ENDORSE"

escalation:
  condition: "Iterations >= max_iterations WITHOUT resolution"
  report_includes:
    - "Sovereignty requirement"
    - "Cost delta (€/year)"
    - "Trust premium potential (€/year)"
    - "Risk mitigation value (€)"
    - "Net cost of sovereignty"
    - "Recommendation to human"
```

### 8.4 Convergence Configuration

```yaml
# config/convergence.yaml

convergence_criteria:
  # ALL criteria must be met simultaneously (cumulative)
  
  criterion_1:
    name: "Zero BLOCK ratings"
    check: "COUNT(ratings WHERE rating == BLOCK) == 0"
    failure_message: "Blocking concerns must be resolved"
  
  criterion_2:
    name: "Maximum 2 WARN ratings"
    check: "COUNT(ratings WHERE rating == WARN) <= 2"
    failure_message: "Too many unresolved warnings"
  
  criterion_3:
    name: "All WARN ratings have accepted mitigation plans"
    check: |
      FOR EACH warn_rating:
        mitigation_plan EXISTS AND mitigation_accepted == True
    failure_message: "WARN without accepted mitigation"
  
  criterion_4:
    name: "Combined confidence >70%"
    check: "AVERAGE(all agent confidence levels) > 0.70"
    failure_message: "Insufficient combined confidence"
  
  criterion_5:
    name: "60% ACCEPT or ENDORSE"
    check: "COUNT(ratings WHERE rating IN [ACCEPT, ENDORSE]) / TOTAL_AGENTS >= 0.60"
    failure_message: "Insufficient agent agreement"

failure_modes:
  infinite_loop:
    detection: "Same agent pair exchanges >5 arguments without position change"
    action: "Extract quantified trade-offs and escalate to human"
  
  complexity_overload:
    detection: "Total debate rounds > 20"
    action: "Suggest query decomposition, escalate to human"
  
  low_confidence_cascade:
    detection: ">=3 agents report confidence <40%"
    action: "Warn user 'Insufficient information', suggest research phase"
```

### 8.5 System Configuration

```yaml
# config/system.yaml

system:
  name: "European Strategy Consortium"
  version: "1.0.0"
  environment: "development"  # development, staging, production

performance_targets:
  simple_query_seconds: 30
  medium_query_seconds: 120
  complex_query_seconds: 300
  memory_retrieval_ms: 500

debug:
  log_level: "INFO"  # DEBUG, INFO, WARN, ERROR
  enable_trace_logging: true
  save_intermediate_states: true

memory:
  persist_directory: "./chroma_db"
  embedding_model: "text-embedding-3-small"
  quality_threshold: 3.5
  progressive_fallback_enabled: true

knowledge:
  static_db_path: "./knowledge_db"
  dynamic_cache_ttl_hours: 24
  confidence_threshold: 0.7

routing:
  max_agents_per_query: 7
  always_engaged_agents:
    - economist
    - architect
  keyword_confidence_threshold: 0.6
  semantic_similarity_threshold: 0.6
```

---

## 9. TESTING STRATEGY

### 9.1 Complete Test Case Example

```yaml
# tests/test_cases/tc_001_german_automotive_cloud.yaml

test_case_001:
  id: "tc_001_german_automotive_cloud"
  name: "German Automotive R&D Cloud Migration"
  category: "sovereignty_economics"
  
  query: "Should we move our German automotive R&D data to AWS for better AI/ML capabilities?"
  
  context:
    industry: "Automotive"
    company_size: "Large (10K+ employees)"
    revenue_annual: "€5B"
    data_sensitivity: "High (trade secrets, GDPR personal data)"
    current_state: "On-premise datacenter in Frankfurt"
    current_cost: "€2M/year infrastructure"
    driver: "Need advanced AI/ML capabilities for autonomous vehicle development"
    timeline: "12 months to migrate"
  
  expected_behavior:
    triggered_agents:
      must_include:
        - Sovereign
        - Jurist
        - Economist
        - Architect
        - Technologist
      may_include:
        - Eco-System
        - Operator
    
    expected_tensions:
      - sovereign_economist
    
    tension_outcomes:
      sovereign_economist:
        trigger: true
        iterations_min: 2
        iterations_max: 4
        resolution_type: "hybrid_architecture"
    
    expected_ratings:
      sovereign:
        initial_rating: "BLOCK"
        final_rating: "ACCEPT"  # After hybrid solution
        confidence_range: [0.7, 0.9]
        must_mention:
          - "Confidential Computing"
          - "External Key Management"
          - "EU regions"
      
      economist:
        initial_rating: "WARN"
        final_rating: "ACCEPT"
        confidence_range: [0.6, 0.8]
        must_mention:
          - "cost premium"
          - "trust premium"
          - "30-40%"
      
      jurist:
        rating: "ACCEPT"
        confidence_range: [0.8, 1.0]
        must_mention:
          - "GDPR"
          - "Model Contractual Clauses"
          - "data processing agreement"
      
      architect:
        rating: "ACCEPT"
        confidence_range: [0.7, 0.9]
        must_mention:
          - "AWS Nitro Enclaves"
          - "architecture diagram"
          - "migration strategy"
    
    recommendation_elements:
      must_include:
        - "AWS EU regions"
        - "Confidential Computing"
        - "External Key Management"
        - "sovereignty safeguards"
      
      must_not_include:
        - "direct AWS services without controls"
        - "US-hosted"
      
      cost_analysis_required: true
      cost_premium_range: [0.30, 0.45]  # 30-45% higher than pure AWS
  
  convergence:
    must_converge: true
    max_iterations: 15
    confidence_threshold: 0.70
  
  known_historical_outcome:
    decision: "Implemented hybrid architecture"
    details: |
      Company implemented AWS EU regions (Frankfurt, Ireland) with:
      - Confidential VMs using Nitro Enclaves
      - External Key Management (Thales CipherTrust)
      - Dedicated tenancy for sensitive workloads
      - Cost premium: 35% over standard AWS
      - Migration took 14 months
    
    alignment_score: 4.5  # 1-5 scale
    
    long_term_results: |
      - No sovereignty incidents in 2 years
      - Successfully passed client audits
      - AI/ML capabilities enabled €50M in new contracts
      - Cost premium justified by revenue growth
  
  validation_criteria:
    - criterion: "Sovereign agent must BLOCK or WARN pure AWS approach"
      type: "mandatory"
    
    - criterion: "Final recommendation includes sovereignty controls"
      type: "mandatory"
    
    - criterion: "Economist addresses cost premium (typically 30-40%)"
      type: "mandatory"
    
    - criterion: "Convergence within 15 iterations"
      type: "mandatory"
    
    - criterion: "Trust premium calculation present"
      type: "recommended"
    
    - criterion: "Architect provides hybrid architecture diagram"
      type: "recommended"
```

### 9.2 Test Implementation

```python
# tests/test_historical_cases.py

import pytest
import yaml
from src.consortium.graph import app as consortium_app

def load_test_case(test_case_id: str):
    """Load test case from YAML"""
    with open(f"./tests/test_cases/{test_case_id}.yaml", "r") as f:
        return yaml.safe_load(f)[test_case_id]

def test_tc_001_german_automotive_cloud():
    """Test Case 001: German Automotive R&D Cloud Migration"""
    
    # Load test case
    test_case = load_test_case("tc_001_german_automotive_cloud")
    
    # Create initial state
    initial_state = {
        "query": test_case["query"],
        "query_context": test_case["context"],
        "trace_id": "test_tc_001",
        "triggered_agents": [],
        "agent_responses": {},
        "iteration_counts": {},
        "tension_iterations": {},
        "total_debate_rounds": 0,
        "max_debate_rounds": 20,
        "audit_trail": []
    }
    
    # Execute consortium
    final_state = consortium_app.invoke(initial_state)
    
    # =========================================
    # VALIDATE: Agent Engagement
    # =========================================
    triggered = final_state["triggered_agents"]
    
    for required_agent in test_case["expected_behavior"]["triggered_agents"]["must_include"]:
        assert required_agent in triggered, f"Required agent {required_agent} not triggered"
    
    # =========================================
    # VALIDATE: Tensions
    # =========================================
    assert "Sovereign_Economist" in [t["tension_id"] for t in final_state["tension_history"]], \
        "Expected Sovereign_Economist tension not detected"
    
    # Check tension iterations
    sovereign_economist_iterations = final_state["tension_iterations"].get("Sovereign_Economist", 0)
    assert 2 <= sovereign_economist_iterations <= 4, \
        f"Sovereign_Economist iterations {sovereign_economist_iterations} outside expected range [2-4]"
    
    # =========================================
    # VALIDATE: Agent Ratings
    # =========================================
    expected_ratings = test_case["expected_behavior"]["expected_ratings"]
    
    # Sovereign
    sovereign_response = final_state["agent_responses"]["Sovereign"]
    assert sovereign_response["rating"] == expected_ratings["sovereign"]["final_rating"], \
        f"Sovereign final rating {sovereign_response['rating']} != expected {expected_ratings['sovereign']['final_rating']}"
    
    assert expected_ratings["sovereign"]["confidence_range"][0] <= sovereign_response["confidence"] <= expected_ratings["sovereign"]["confidence_range"][1], \
        f"Sovereign confidence {sovereign_response['confidence']} outside expected range"
    
    for keyword in expected_ratings["sovereign"]["must_mention"]:
        assert keyword.lower() in sovereign_response["reasoning"].lower(), \
            f"Sovereign reasoning missing keyword: {keyword}"
    
    # Economist
    economist_response = final_state["agent_responses"]["Economist"]
    assert economist_response["rating"] == expected_ratings["economist"]["final_rating"]
    
    for keyword in expected_ratings["economist"]["must_mention"]:
        assert keyword.lower() in economist_response["reasoning"].lower(), \
            f"Economist reasoning missing keyword: {keyword}"
    
    # =========================================
    # VALIDATE: Convergence
    # =========================================
    assert final_state["convergence_status"]["converged"] == True, \
        "Expected convergence but got failure"
    
    assert final_state["total_debate_rounds"] <= test_case["convergence"]["max_iterations"], \
        f"Exceeded max iterations: {final_state['total_debate_rounds']} > {test_case['convergence']['max_iterations']}"
    
    # =========================================
    # VALIDATE: Recommendation Content
    # =========================================
    recommendation = final_state["final_recommendation"]["recommendation"]
    
    for required_element in test_case["expected_behavior"]["recommendation_elements"]["must_include"]:
        assert required_element.lower() in recommendation.lower(), \
            f"Recommendation missing required element: {required_element}"
    
    for forbidden_element in test_case["expected_behavior"]["recommendation_elements"]["must_not_include"]:
        assert forbidden_element.lower() not in recommendation.lower(), \
            f"Recommendation contains forbidden element: {forbidden_element}"
    
    # =========================================
    # VALIDATE: Performance
    # =========================================
    duration = (final_state["timestamp_end"] - final_state["timestamp_start"]).total_seconds()
    assert duration < 300, f"Query took {duration}s, exceeds 300s limit for complex queries"
    
    print(f"✅ Test Case 001 PASSED in {duration:.1f}s with {final_state['total_debate_rounds']} iterations")
```

### 9.3 Test Categories

```python
# tests/test_categories.py

"""
Test categories organized by complexity and focus area:

CATEGORY 1: Unit Tests (Fast, Isolated)
- test_agent_prompt_building.py
- test_convergence_criteria.py
- test_memory_retrieval.py
- test_knowledge_routing.py
- test_provider_failover.py

CATEGORY 2: Integration Tests (Medium, Component Interaction)
- test_tension_protocols.py
- test_supervisor_routing.py
- test_agent_debate_cycles.py
- test_memory_integration.py

CATEGORY 3: System Tests (Slow, End-to-End)
- test_historical_cases.py (5+ historical test cases)
- test_performance_targets.py
- test_failure_modes.py

CATEGORY 4: Regression Tests
- test_no_regression.py (ensure old test cases still pass)
"""
```

---

## 10. OBSERVABILITY & DEBUGGING

### 10.1 Logging Strategy

```python
import logging
import json
from datetime import datetime

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/consortium.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('consortium')

def log_structured_event(event_type: str, details: Dict[str, Any], trace_id: str):
    """Log structured event in JSON format"""
    
    event = {
        "timestamp": datetime.now().isoformat(),
        "trace_id": trace_id,
        "event_type": event_type,
        "details": details
    }
    
    logger.info(json.dumps(event))

# Example usage
log_structured_event(
    "agent_response",
    {
        "agent_id": "Sovereign",
        "rating": "BLOCK",
        "confidence": 0.85,
        "latency_ms": 1234.5
    },
    trace_id="abc-123"
)
```

### 10.2 Trace ID Propagation

```python
import uuid

def generate_trace_id() -> str:
    """Generate unique trace ID for request"""
    return str(uuid.uuid4())

# At entry point
initial_state["trace_id"] = generate_trace_id()

# All audit events include trace_id
audit_event = {
    "event_id": str(uuid.uuid4()),
    "trace_id": state["trace_id"],  # Links to parent request
    "event_type": "agent_invoked",
    ...
}
```

### 10.3 Monitoring Dashboard Requirements

```yaml
# monitoring/dashboard_spec.yaml

dashboards:
  - name: "Consortium Overview"
    metrics:
      - metric: "queries_per_hour"
        type: "counter"
        visualization: "time_series"
      
      - metric: "average_convergence_time"
        type: "histogram"
        visualization: "heatmap"
      
      - metric: "convergence_rate"
        type: "gauge"
        target: 0.70  # >70% queries should converge
        visualization: "gauge"
      
      - metric: "human_escalation_rate"
        type: "gauge"
        target: 0.30  # <30% queries escalated
        visualization: "gauge"
  
  - name: "Agent Performance"
    metrics:
      - metric: "agent_response_latency"
        dimensions: ["agent_id", "provider"]
        type: "histogram"
        visualization: "multi_line"
      
      - metric: "agent_confidence_distribution"
        dimensions: ["agent_id"]
        type: "histogram"
        visualization: "box_plot"
      
      - metric: "rating_distribution"
        dimensions: ["agent_id"]
        type: "counter"
        visualization: "stacked_bar"
  
  - name: "Tension Protocols"
    metrics:
      - metric: "tension_frequency"
        dimensions: ["tension_id"]
        type: "counter"
        visualization: "bar_chart"
      
      - metric: "tension_resolution_rate"
        dimensions: ["tension_id"]
        type: "gauge"
        visualization: "gauge"
      
      - metric: "tension_iterations"
        dimensions: ["tension_id"]
        type: "histogram"
        visualization: "box_plot"
```

---

## 11. ARCHITECTURE DECISION TRADE-OFFS

### 11.1 Vector Database: Chroma vs Pinecone vs Weaviate

| Criterion | Chroma ✅ | Pinecone | Weaviate |
|-----------|----------|----------|----------|
| Deployment | Embedded, local | External service | Self-hosted or cloud |
| Cost | Free (open-source) | $$ (per index) | $ (infrastructure) |
| Sovereignty | EU-compliant (local) | US-based service | Can be EU-hosted |
| Complexity | Simple API | Simple API | Complex setup |
| Scale | Good for prototype | Excellent | Excellent |
| Vendor Lock-in | None | High | Medium |

**Decision**: **Chroma** ✅

**Rationale**:
- ✅ Embeddable - no external dependencies
- ✅ Open-source - aligns with sovereignty principles
- ✅ Simple API - faster Phase R implementation
- ✅ No vendor lock-in - can migrate later if needed
- ❌ May need to migrate to Weaviate for production scale
- Acceptable trade-off for Phase R prototype

---

### 11.2 State Management: TypedDict vs Pydantic

| Criterion | TypedDict ✅ | Pydantic |
|-----------|--------------|----------|
| LangGraph Native | Yes | No (requires conversion) |
| Validation | No | Yes (runtime) |
| Performance | Fast | Slower (validation overhead) |
| Type Hints | Static only | Runtime + static |
| Complexity | Simple | More complex |

**Decision**: **TypedDict** ✅ for Phase R, migrate to Pydantic for production

**Rationale**:
- ✅ LangGraph native support - less friction
- ✅ Lightweight - faster execution
- ✅ Simpler - easier to implement in Phase R
- ❌ No runtime validation - could cause bugs
- Migration path: Add Pydantic validation layer in Phase R Iteration 8 (final refinement)

---

### 11.3 Graph Structure: Monolithic vs Sub-Graphs

| Criterion | Monolithic | Sub-Graphs ✅ |
|-----------|------------|---------------|
| Node Count | 30+ nodes | Main: 10 nodes + 2 sub-graphs |
| Testability | Hard (full system) | Easy (test sub-graphs) |
| Maintainability | Poor (complex) | Good (modular) |
| Debugging | Difficult | Easier |
| Performance | Slightly faster | Negligible overhead |

**Decision**: **Sub-Graphs** ✅ (Hybrid approach)

**Rationale**:
- ✅ Modularity - agent executor and tension resolver isolated
- ✅ Testability - can test sub-graphs independently
- ✅ Maintainability - easier to modify individual sub-graphs
- ✅ Clear separation of concerns
- Negligible performance cost for massive maintainability gain

---

### 11.4 Embedding Model: text-embedding-3-small vs text-embedding-3-large

| Criterion | small ✅ | large |
|-----------|----------|-------|
| Dimensions | 1536 | 3072 |
| Cost per 1M tokens | $0.02 | $0.13 |
| Performance | Good | Excellent |
| Storage | 1x | 2x |
| Latency | Fast | Slower |

**Decision**: **text-embedding-3-small** ✅

**Rationale**:
- ✅ 6.5x cheaper
- ✅ Half the storage requirements
- ✅ Faster retrieval
- ✅ Good enough for semantic similarity in regulatory text
- Can upgrade to large if retrieval quality insufficient in Phase R testing

---

## 12. PERFORMANCE TARGETS & IMPLICATIONS

### 12.1 Approved Success Metrics

From `Specification_Gap_Resolutions.md`:

```yaml
Performance Targets:
  Simple query: <30 seconds
  Medium complexity: <2 minutes
  Complex query: <5 minutes
  Memory retrieval: <500ms
```

### 12.2 Architectural Implications

#### Simple Query (<30s target)

**Implications**:
- Agent timeout: 5 seconds per agent
- Max 3 agents engaged (Economist, Architect + 1 domain specialist)
- No tension protocols triggered
- Static knowledge only (Tier 1)
- No iteration loops

**Example**: "What is the GDPR retention period for customer data?"

---

#### Medium Complexity (<2min target)

**Implications**:
- Agent timeout: 15 seconds per agent
- Max 5 agents engaged
- 1-2 tension protocols, max 2 iterations each
- Hybrid knowledge (Tier 1 + 2)
- Total iterations: <10

**Example**: "Should we implement facial recognition for employee access control?"

**Budget Breakdown**:
- Routing: 5s
- Agent execution (5 agents × 15s): 75s
- Tension resolution (2 protocols × 2 iterations): 20s
- Convergence testing: 5s
- Synthesis: 5s
- Memory write: 2s
- **Total**: ~112s (within 120s target)

---

#### Complex Query (<5min target)

**Implications**:
- Agent timeout: 30 seconds per agent
- Max 7 agents engaged
- 3-4 tension protocols, max 4 iterations each
- Full knowledge access (all 3 tiers)
- Total iterations: 15-20

**Example**: "Design a comprehensive AI governance framework for EU expansion"

**Budget Breakdown**:
- Routing: 10s
- Agent execution (7 agents × 30s): 210s
- Tension resolution (4 protocols × 4 iterations): 180s
- Convergence testing: 10s
- Synthesis: 20s
- Memory write: 5s
- **Total**: ~435s (~7.25 min) ⚠️ **EXCEEDS TARGET**

**Optimization Required**:
- Reduce agent timeout to 20s: Saves 70s
- Parallel tension resolution (if independent): Saves 90s
- **Optimized Total**: ~275s (~4.6 min) ✅

---

### 12.3 Timeout Configuration

```yaml
# config/timeouts.yaml

timeouts:
  simple_query:
    agent_timeout_seconds: 5
    total_timeout_seconds: 30
  
  medium_query:
    agent_timeout_seconds: 15
    total_timeout_seconds: 120
  
  complex_query:
    agent_timeout_seconds: 20
    total_timeout_seconds: 300

# Auto-detect query complexity
complexity_detection:
  simple:
    keywords: ["what is", "define", "explain"]
    max_words: 20
  
  complex:
    keywords: ["design", "framework", "comprehensive", "strategy"]
    multiple_domains: true  # >3 agents triggered
```

---

## 13. TECHNOLOGY STACK

### 13.1 Core Dependencies

```toml
# pyproject.toml

[tool.poetry.dependencies]
python = "^3.11"

# LangGraph and LangChain
langgraph = "^0.2.0"
langchain = "^0.3.0"
langchain-anthropic = "^0.2.0"
langchain-openai = "^0.2.0"

# Vector Database
chromadb = "^0.5.0"

# LLM Providers
anthropic = "^0.40.0"
openai = "^1.50.0"
mistralai = "^1.2.0"

# Data Handling
pydantic = "^2.9.0"
pyyaml = "^6.0"

# Testing
pytest = "^8.3.0"
pytest-asyncio = "^0.24.0"
pytest-cov = "^5.0.0"

# Observability
structlog = "^24.0.0"

# Utilities
python-dotenv = "^1.0.0"
```

### 13.2 Version Justifications

- **Python 3.11**: Latest stable, performance improvements over 3.10
- **LangGraph 0.2.0**: Sub-graph support, StateGraph composition
- **Chroma 0.5.0**: Stable API, persistent client support
- **Anthropic 0.40.0**: Latest Claude Sonnet 4.5 support
- **Pydantic 2.9.0**: Fast validation (if migrating from TypedDict)

---

## 14. IMPLEMENTATION GUIDANCE & RISK ASSESSMENT

### 14.1 Iteration Risk Matrix

| Iteration | Focus | Risk Level | Mitigation |
|-----------|-------|------------|------------|
| 1 | Core Infrastructure | 🟢 Low | Foundational, well-understood patterns |
| 2 | Memory System | 🟡 Medium | Chroma integration complexity; test extensively |
| 3 | Big Three Agents | 🔴 High | Prompt engineering is hard; iterate on prompts |
| 4 | Tension Protocols | 🔴 Very High | Complex state management; build one at a time |
| 5 | Supervisor & Routing | 🟡 Medium | MECE validation tricky; use LLM validation |
| 6 | Remaining Agents | 🟡 Medium | Repetition of Iteration 3; reuse patterns |
| 7 | Complete Graph | 🔴 High | Integration bugs; comprehensive testing |
| 8 | Historical Test Cases | 🟢 Low | Validation phase; tune thresholds |

### 14.2 Implementation Order Rationale

**Why Big Three (Sovereign, Economist, Jurist) First?**
- ✅ Most critical agents - cover 80% of use cases
- ✅ Establishes prompt engineering patterns
- ✅ Validates core debate mechanics before scaling

**Why Tension Protocols in Iteration 4?**
- ❌ Can't test until we have working agents (Iteration 3)
- ✅ Most complex logic - needs dedicated iteration
- ✅ Build one protocol at a time, test thoroughly

**Why Historical Test Cases Last?**
- ✅ Requires complete system
- ✅ Serves as final validation gate
- ✅ Threshold tuning based on real performance

---

### 14.3 Risk Mitigation Strategies

#### Risk: Prompt Engineering Failures

**Symptoms**: Agents produce inconsistent ratings, miss red lines, poor reasoning

**Mitigation**:
1. Start with detailed system prompts (see config examples)
2. Test with synthetic queries covering edge cases
3. Iterate on prompts based on failure patterns
4. Consider few-shot examples in prompts for tricky cases

---

#### Risk: Chroma Integration Issues

**Symptoms**: Slow retrieval, poor relevance, embedding errors

**Mitigation**:
1. Test Chroma separately before integrating
2. Validate embedding model choice with sample queries
3. Monitor retrieval times - optimize if >500ms
4. Consider caching frequently retrieved cases

---

#### Risk: Tension Protocol Infinite Loops

**Symptoms**: Same agent pair iterates 10+ times without resolution

**Mitigation**:
1. Implement strict iteration limits (already in design)
2. Add "no progress" detection (same ratings for 3 iterations → escalate)
3. Logging at every iteration to debug loop causes
4. Human-in-the-loop testing for each protocol

---

#### Risk: Performance Target Violations

**Symptoms**: Queries exceed time budgets (>30s, >2min, >5min)

**Mitigation**:
1. Implement timeouts at every level (agent, protocol, total)
2. Profile execution to find bottlenecks
3. Optimize: parallel agent execution, caching, faster embeddings
4. Complexity detection to route simple queries to fast path

---

### 14.4 Phase R Success Criteria

**Before proceeding to Phase C (Completion), validate**:

1. ✅ All 11 agents operational and producing structured responses
2. ✅ All 5 tension protocols tested and resolving correctly
3. ✅ Multi-LLM failover tested (simulate provider failures)
4. ✅ Memory system integrated and retrieving relevant cases
5. ✅ Historical test case (tc_001) passes validation
6. ✅ Performance targets met for at least one query in each category
7. ✅ Audit trail complete for manual inspection
8. ✅ No critical bugs in issue tracker

---

## PHASE A APPROVAL CHECKLIST

Before proceeding to Phase R (Refinement), confirm:

- [ ] **State Schema** reviewed and approved
- [ ] **Graph Topology** diagram clear and complete
- [ ] **LangGraph Implementation** pattern agreed upon (sub-graphs)
- [ ] **Component Interfaces** (Agent, Provider, Tension) finalized
- [ ] **Chroma Memory Architecture** strategy validated
- [ ] **Multi-LLM Failover** logic acceptable
- [ ] **Knowledge Routing** (3-tier) approach confirmed
- [ ] **Configuration Examples** sufficient for implementation
- [ ] **Test Case tc_001** comprehensive and realistic
- [ ] **Architecture Decisions** (Chroma, TypedDict, etc.) justified
- [ ] **Performance Targets** understood and achievable
- [ ] **Technology Stack** versions approved
- [ ] **Risk Assessment** complete and mitigation strategies clear

---

**[END OF ARCHITECTURE PHASE A]**

**Next Phase**: Phase R (Refinement) - Iterative Implementation

Upon approval, proceed to build the system incrementally following the 8-iteration plan with validation at each step.

**Status**: ⏸️ AWAITING APPROVAL
