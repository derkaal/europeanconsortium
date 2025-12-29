# ARCHITECTURE - Phase A (Part 1 of 3)

**Project**: European Strategy Consortium Multi-Agent System  
**Methodology**: SPARC Phase A (Architecture)  
**Date**: 2024-12-24  
**Status**: DRAFT - Awaiting Approval

---

## TABLE OF CONTENTS

**Part 1 (This Document)**:
1. State Schema Implementation
2. Graph Topology  
3. LangGraph Implementation Pattern
4. Component Interfaces

**Part 2**:
5. Memory Architecture - Chroma Specifics
6. Multi-LLM Provider Strategy
7. Knowledge & Tools Strategy

**Part 3**:
8. Configuration Management
9. Testing Strategy
10. Observability & Debugging
11. Architecture Decision Trade-offs
12. Performance Targets & Implications
13. Technology Stack
14. Implementation Guidance & Risk Assessment

---

## 1. STATE SCHEMA IMPLEMENTATION

### 1.1 Core State Schema

```python
from typing import TypedDict, Optional, Dict, List, Tuple, Literal
from datetime import datetime
from uuid import UUID

class ConsortiumState(TypedDict, total=False):
    """
    Complete state for the European Strategy Consortium system.
    TypedDict chosen over Pydantic for LangGraph native compatibility.
    total=False allows optional fields for progressive state building.
    """
    
    # ==============================================================
    # QUERY AND CONTEXT
    # ==============================================================
    query: str  # Original user query
    query_context: Dict[str, any]  # Industry, company size, sensitivity, etc.
    conversation_history: List['Message']  # Multi-turn conversation support
    session_id: str  # For multi-turn tracking
    
    # ==============================================================
    # OBSERVABILITY (Required for audit trails)
    # ==============================================================
    trace_id: str  # UUID for end-to-end tracing
    timestamp_start: datetime  # Query received timestamp
    timestamp_end: Optional[datetime]  # Query completed timestamp
    timestamps: Dict[str, datetime]  # Granular timestamps per phase
    # Example: {"routing_start": ..., "routing_end": ..., "debate_start": ...}
    
    # ==============================================================
    # AGENT ENGAGEMENT
    # ==============================================================
    triggered_agents: List[str]  # Agent IDs engaged for this query
    agent_confidence_scores: Dict[str, float]  # Initial confidence per agent
    sub_questions: List['SubQuestion']  # MECE decomposition results
    assignments: Dict[str, List['SubQuestion']]  # Agent -> sub-questions mapping
    
    # ==============================================================
    # DEBATE TRACKING
    # ==============================================================
    agent_responses: Dict[str, 'AgentResponse']  # Latest response per agent
    response_history: List['AgentResponse']  # Full chronological history
    current_proposal: Optional['Proposal']  # Active proposal under debate
    proposal_version: int  # Iteration counter for proposal revisions
    
    # ==============================================================
    # TENSION PROTOCOL TRACKING (SUPPORTS MULTIPLE SIMULTANEOUS TENSIONS)
    # ==============================================================
    active_tensions: List['TensionStatus']  # Multiple simultaneous tensions
    tension_priority_queue: List[str]  # Order to resolve tensions (by tension_id)
    tension_dependency_graph: Dict[str, List[str]]  # tension_id -> blocking tension IDs
    tension_iterations: Dict[str, int]  # Tension protocol -> iteration count
    # Example: {"Sovereign_Economist": 2, "EcoSystem_Architect": 1}
    tension_history: List['TensionEvent']  # Full tension resolution history
    
    # ==============================================================
    # ITERATION TRACKING (Critical for loop detection)
    # ==============================================================
    iteration_counts: Dict[Tuple[str, str], int]  # Agent pair -> iteration count
    # Example: {("Sovereign", "Economist"): 3, ("EcoSystem", "Architect"): 1}
    total_debate_rounds: int  # Global iteration counter
    max_debate_rounds: int  # Complexity overload threshold (default: 20)
    
    # ==============================================================
    # MEMORY AND KNOWLEDGE
    # ==============================================================
    memory_retrievals: List['Case']  # Retrieved historical cases
    memory_retrieval_metadata: 'MemoryMetadata'  # Cold-start flags, confidence adjustments
    knowledge_tier_used: Literal["tier_1_static", "hybrid_1_2", "dynamic"]
    knowledge_sources: List['KnowledgeSource']  # All sources consulted
    knowledge_conflicts: List['KnowledgeConflict']  # Detected contradictions
    
    # ==============================================================
    # CONVERGENCE
    # ==============================================================
    convergence_status: Optional['ConvergenceStatus']  # Latest convergence check result
    convergence_history: List['ConvergenceStatus']  # All convergence attempts
    
    # ==============================================================
    # OUTPUT
    # ==============================================================
    final_recommendation: Optional['Report']  # Pyramid Principle structured report
    escalation_required: bool  # True if human decision needed
    escalation_report: Optional['EscalationReport']  # Detailed escalation context
    
    # ==============================================================
    # PROVIDER TRACKING (For multi-LLM failover)
    # ==============================================================
    provider_used: Dict[str, str]  # Agent -> provider mapping
    # Example: {"Sovereign": "anthropic", "Economist": "mistral"}
    provider_failures: List['ProviderFailure']  # Failure events for debugging
    failover_events: List['FailoverEvent']  # Provider switch events
    
    # ==============================================================
    # AUDIT TRAIL (Complete event log)
    # ==============================================================
    audit_trail: List['AuditEvent']  # Append-only event log
    # Every significant action logged: routing decisions, agent invocations,
    # rating submissions, tension detections, convergence checks, escalations
```

### 1.2 Nested Object Schemas

```python
class Message(TypedDict):
    """Single message in conversation history"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime


class SubQuestion(TypedDict):
    """Decomposed sub-question from MECE analysis"""
    question: str
    target_agents: List[str]  # Agents assigned to answer this
    complexity_score: float  # 0-1 complexity estimate
    priority: int  # Execution priority


class AgentResponse(TypedDict):
    """Complete response from a single agent"""
    agent_id: str
    rating: Literal["BLOCK", "WARN", "ACCEPT", "ENDORSE"]
    confidence: float  # 0-1 scale
    reasoning: str  # Detailed explanation
    attack_vector: Optional[str]  # For adversarial critique
    evidence: List[str]  # Citations to knowledge sources
    
    # For WARN ratings
    mitigation_plan: Optional[str]
    mitigation_accepted: Optional[bool]
    rejection_reason: Optional[str]
    
    # Metadata
    timestamp: datetime
    provider_used: str  # Which LLM generated this response
    latency_ms: float  # Response time
    token_count: int  # For cost tracking


class Proposal(TypedDict):
    """A concrete proposal under debate"""
    version: int  # Iteration number
    proposer: str  # Agent who generated this proposal
    content: str  # Full proposal text
    success_metrics: List[str]  # How to measure success
    assumptions: List[str]  # Key assumptions
    timestamp: datetime


class TensionStatus(TypedDict):
    """Status of an active tension protocol (supports multiple simultaneous tensions)"""
    
    # Core identification
    protocol_id: str  # e.g., "Sovereign_Economist"
    tension_id: str  # Unique instance ID (protocol_id + timestamp for multiple instances)
    agents_involved: Tuple[str, str]  # (agent_1, agent_2) - for dependency detection
    
    # Legacy fields (kept for backwards compatibility)
    agent_1: str  # Same as agents_involved[0]
    agent_2: str  # Same as agents_involved[1]
    
    # Iteration tracking
    iteration_count: int  # Current iteration number
    max_iterations: int  # Maximum allowed iterations
    
    # Status tracking
    status: Literal["active", "resolved", "escalated", "blocked"]
    trigger_reason: str
    resolution: Optional[Dict[str, any]]  # Resolution details if resolved
    
    # Priority management (for multi-tension scenarios)
    priority: int  # 1=highest priority (resolve first), higher numbers=lower priority
    # Priority levels: 1=values conflict, 2=BLOCK ratings, 3=ready, 4=blocked
    
    # Dependency tracking (for multi-tension scenarios)
    depends_on_tensions: List[str]  # Tension IDs that must resolve first
    blocking_tensions: List[str]  # Tension IDs that this tension is blocking
    
    # Metadata
    triggered_at: datetime
    resolved_at: Optional[datetime]


class TensionEvent(TypedDict):
    """Single event in tension resolution history"""
    tension_id: str
    event_type: Literal["triggered", "iteration", "resolved", "escalated"]
    details: Dict[str, any]
    timestamp: datetime


class Case(TypedDict):
    """Historical case from memory system (Hybrid B+C structure)"""
    id: str  # UUID
    query: str
    context: Dict[str, any]
    agents_engaged: List[str]
    debate_transcript: List[AgentResponse]
    final_recommendation: 'Report'
    timestamp: datetime
    
    # Immediate feedback (Hybrid B component)
    user_feedback: 'UserFeedback'
    
    # Long-term outcome (Hybrid C component)
    outcome: 'Outcome'
    
    # Retrieval metadata
    similarity_score: float  # Cosine similarity to current query
    enhanced_score: float  # After outcome-based weighting
    boost_reason: str  # Why this case was boosted/penalized


class UserFeedback(TypedDict, total=False):
    """Immediate feedback captured after delivery"""
    quality_score: Optional[float]  # 1-5 scale
    feedback_text: Optional[str]
    submitted_at: Optional[datetime]


class Outcome(TypedDict, total=False):
    """Long-term outcome tracking (optional, async updates)"""
    status: Literal["not_implemented", "in_progress", "implemented", "abandoned"]
    alignment_score: Optional[float]  # 1-5 scale
    actual_results: Optional[str]
    verified_at: Optional[datetime]


class MemoryMetadata(TypedDict):
    """Metadata about memory retrieval"""
    total_matches: int
    quality_filtered: int
    returned: int
    cold_start: bool
    confidence_adjustment: float  # e.g., -0.15 for cold start
    warning: Optional[str]


class KnowledgeSource(TypedDict):
    """Single knowledge source consulted"""
    source_type: Literal["static_db", "eurlex", "ec_website", "web_search"]
    url: Optional[str]
    title: str
    snippet: str
    relevance_score: float
    sovereignty_flagged: bool  # True if non-EU source


class KnowledgeConflict(TypedDict):
    """Detected conflict between knowledge sources"""
    static_claim: str
    static_source: str
    dynamic_claim: str
    dynamic_source: str
    conflict_type: str
    user_flag_message: str


class ConvergenceStatus(TypedDict):
    """Result of convergence testing"""
    converged: bool
    status: str  # Human-readable status message
    details: Dict[str, any]
    failed_criteria: List[str]  # Which criteria failed
    timestamp: datetime


class Report(TypedDict):
    """Final Pyramid Principle structured report"""
    recommendation: str  # Level 1: The recommendation (2-3 sentences)
    confidence_level: float
    key_assumptions: List[str]
    
    domain_analysis: Dict[str, 'DomainSection']  # Level 2: By domain
    # Example: {"financial": {...}, "legal": {...}, "sovereignty": {...}}
    
    evidence_and_reasoning: List[str]  # Level 3: Supporting detail
    action_items: List['ActionItem']  # Level 4: Next steps
    
    # Metadata
    agents_engaged: List[str]
    total_iterations: int
    debate_duration_seconds: float
    timestamp: datetime


class DomainSection(TypedDict):
    """Domain-specific analysis section"""
    domain: str
    agent_id: str
    rating: Literal["BLOCK", "WARN", "ACCEPT", "ENDORSE"]
    confidence: float
    key_reasoning: str
    mitigation_strategies: Optional[List[str]]


class ActionItem(TypedDict):
    """Specific action item from recommendation"""
    task: str
    responsible_party: Optional[str]
    deadline: Optional[str]
    priority: Literal["critical", "high", "medium", "low"]


class EscalationReport(TypedDict):
    """Detailed report for human escalation"""
    escalation_reason: str  # Why human decision needed
    tension_type: str  # e.g., "values_conflict", "infinite_loop"
    summary: str
    positions: Dict[str, any]  # Agent positions
    quantified_tradeoffs: Dict[str, any]  # Numerical trade-offs
    historical_precedents: List[Case]  # Similar cases
    recommendation_to_human: str


class ProviderFailure(TypedDict):
    """Provider failure event"""
    provider: str
    agent_id: str
    failure_type: Literal["timeout", "rate_limit", "api_error"]
    error_message: str
    timestamp: datetime


class FailoverEvent(TypedDict):
    """Provider failover event"""
    from_provider: str
    to_provider: str
    agent_id: str
    reason: str
    state_preserved: bool
    timestamp: datetime


class AuditEvent(TypedDict):
    """Single audit trail event"""
    event_id: str  # UUID
    trace_id: str  # Links to ConsortiumState.trace_id
    event_type: str  # e.g., "query_received", "agent_invoked", "tension_detected"
    agent_id: Optional[str]  # If agent-related event
    details: Dict[str, any]  # Event-specific details
    timestamp: datetime
```

### 1.3 Example: Iteration Count Tracking

```python
# Example state showing iteration count tracking
example_state = {
    "iteration_counts": {
        ("Sovereign", "Economist"): 3,  # 3 rounds of debate
        ("EcoSystem", "Architect"): 1,  # 1 round of debate
    },
    "tension_iterations": {
        "Sovereign_Economist": 3,  # Same as above, but keyed by protocol
        "EcoSystem_Architect": 1,
    },
    "total_debate_rounds": 7,  # Total iterations across all agent pairs
    "max_debate_rounds": 20,  # Complexity overload threshold
}

# How to increment (in node function):
def increment_iteration_count(state: ConsortiumState, agent_1: str, agent_2: str) -> ConsortiumState:
    """Increment iteration count for an agent pair"""
    key = tuple(sorted([agent_1, agent_2]))  # Ensure consistent ordering
    current_count = state["iteration_counts"].get(key, 0)
    state["iteration_counts"][key] = current_count + 1
    state["total_debate_rounds"] += 1
    return state
```

---

## 2. GRAPH TOPOLOGY

### 2.1 ASCII Diagram - Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EUROPEAN STRATEGY CONSORTIUM                              │
│                          Main Execution Graph                                │
└─────────────────────────────────────────────────────────────────────────────┘

[START]
   │
   │ (unconditional)
   ▼
┌──────────────┐
│   Router     │  ◄─── Query analysis, agent selection, MECE decomposition
│              │       Always engages: Economist, Architect
└──────┬───────┘       Output: triggered_agents, sub_questions, assignments
       │
       │ (unconditional)
       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│              Agent Executor Sub-Graph (Parallel Execution)               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐           ┌─────────┐           │
│  │Sovereign│  │Economist│  │ Jurist  │    ...    │Operator │           │
│  └────┬────┘  └────┬────┘  └────┬────┘           └────┬────┘           │
│       │            │            │                     │                 │
│       └────────────┴────────────┴─────────────────────┘                 │
│                            │                                            │
│                   (all agents complete)                                 │
└────────────────────────────┬───────────────────────────────────────────┘
                             │
                             │ (unconditional)
                             ▼
                    ┌────────────────┐
                    │ Tension        │  ◄─── Scans agent_responses for conflicts
                    │ Detector       │       Identifies which protocols to invoke
                    └────────┬───────┘
                             │
                ┌────────────┴────────────┐
                │                         │
         (no tensions)              (tensions detected)
                │                         │
                │                         ▼
                │              ┌──────────────────────┐
                │              │ Tension Prioritizer  │  ◄─── NEW: Prioritizes
                │              │                      │       multiple tensions
                │              │ - Detects dependencies        │
                │              │ - Assigns priorities          │
                │              │ - Creates resolution queue    │
                │              └──────────┬───────────┘
                │                         │
                │                         ▼
                │              ┌──────────────────────────────────────────┐
                │              │   Tension Resolver Sub-Graph             │
                │              │   [Processes tensions from priority queue]│
                │              │                                          │
                │              │   Protocols (each with max iterations):  │
                │              │   - Sovereign ↔ Economist (4)           │
                │              │   - Eco-System ↔ Architect (3)          │
                │              │   - Jurist ↔ Philosopher (0 - instant)  │
                │              │   - Operator ↔ Strategy (2)             │
                │              │   - Futurist ↔ All (3)                  │
                │              │                                          │
                │              │    ┌───────────┬──────────┐             │
                │              │    │           │          │             │
                │              │ (resolved) (not resolved)              │
                │              │    │           │          │             │
                │              │    │    (iter < max)     │             │
                │              │    │           │          │             │
                │              │    │    ┌──────▼───────┐  │             │
                │              │    │    │ Loop back to │◄─┼─────────────┼──┐
                │              │    │    │ Agent Exec   │  │             │  │
                │              │    │    └──────────────┘  │             │  │
                │              │    │                      │             │  │
                │              │    │    (iter >= max)     │             │  │
                │              │    │           │          │             │  │
                │              │    │    ┌──────▼───────┐  │             │  │
                │              │    │    │ Escalate to  │  │             │  │
                │              │    │    │ Human        │  │             │  │
                │              │    │    └──────────────┘  │             │  │
                │              └────┴───────────┬──────────┘             │  │
                │                              │                         │  │
                │                   (all tensions resolved/escalated)    │  │
                └──────────────────┬───────────────────────────────────┘   │
                                   │                                        │
                                   │ (conditional merge)                    │
                                   ▼                                        │
                          ┌────────────────┐                                │
                          │ Convergence    │  ◄─── Tests 5 cumulative      │
                          │ Tester         │       criteria                 │
                          └────────┬───────┘                                │
                                   │                                        │
                      ┌────────────┴────────────┐                           │
                      │                         │                           │
               (converged)              (not converged)                     │
                      │                         │                           │
                      │                 ┌───────▼──────────┐                │
                      │                 │ Failure Mode     │                │
                      │                 │ Detection        │                │
                      │                 └───────┬──────────┘                │
                      │                         │                           │
                      │          ┌──────────────┴──────────────┐            │
                      │          │                             │            │
                      │   (infinite loop)               (complexity         │
                      │          │                       overload)          │
                      │          │                             │            │
                      │  ┌───────▼────────┐          ┌────────▼────────┐   │
                      │  │ Extract        │          │ Suggest         │   │
                      │  │ Quantified     │          │ Decomposition   │   │
                      │  │ Trade-offs     │          │                 │   │
                      │  └───────┬────────┘          └────────┬────────┘   │
                      │          │                            │            │
                      │          └────────────┬───────────────┘            │
                      │                       │                            │
                      │               ┌───────▼────────┐                   │
                      │               │ Escalate to    │                   │
                      │               │ Human          │                   │
                      │               └────────────────┘                   │
                      │                                                    │
                      │         (normal flow - retry needed)               │
                      │                       │                            │
                      │               ┌───────▼────────┐                   │
                      │               │ Proposer       │                   │
                      │               │ Revises        │───────────────────┘
                      │               │ Proposal       │  (loop back to 
                      │               └────────────────┘   Agent Executor)
                      │
                      │ (convergence achieved)
                      ▼
             ┌────────────────┐
             │ Synthesizer    │  ◄─── Generates Pyramid Principle report
             │                │       L1: Recommendation, L2: Domain analysis
             └────────┬───────┘       L3: Evidence, L4: Action items
                      │
                      │ (unconditional)
                      ▼
             ┌────────────────┐
             │ Memory Writer  │  ◄─── Store case in Chroma with embedding
             │                │       Capture structure for user feedback
             └────────┬───────┘
                      │
                      │ (unconditional)
                      ▼
                   [END]


LEGEND:
━━━━  Unconditional edge (always follows this path)
────  Conditional edge (depends on state evaluation)
┌──┐  Node (function that modifies state)
│  │  Sub-graph (contains multiple nodes)
◄───  Loop back edge (creates cycle)

PARALLEL EXECUTION:
- Agent Executor Sub-Graph: All triggered agents run in parallel
- LangGraph handles parallelization automatically

LOOPS (where cycles can occur):
1. Tension Resolution → Agent Executor (proposal revision loop)
2. Convergence Failure → Proposal Revision → Agent Executor
3. Both loops have termination conditions (max iterations, escalation)

FAILURE MODE EXIT PATHS:
- Infinite Loop Detection → Escalate to Human → END
- Complexity Overload → Suggest Decomposition → Escalate → END
- Values Conflict (Jurist↔Philosopher) → Instant Escalate → END
```

### 2.2 Conditional Edge Logic

```python
# Example conditional edge functions

def should_resolve_tensions(state: ConsortiumState) -> str:
    """Determines if tension resolution is needed"""
    if len(state.get("active_tensions", [])) > 0:
        return "resolve_tensions"
    else:
        return "check_convergence"


def check_convergence_result(state: ConsortiumState) -> str:
    """Routes based on convergence test result"""
    convergence = state.get("convergence_status")
    
    if convergence and convergence["converged"]:
        return "synthesize_report"
    
    # Check failure modes
    if state["total_debate_rounds"] > state["max_debate_rounds"]:
        return "complexity_overload"
    
    # Check for infinite loop (same pair >5 iterations without change)
    for (agent_1, agent_2), count in state["iteration_counts"].items():
        if count > 5:
            return "infinite_loop_detected"
    
    # Check for low confidence cascade
    low_confidence_agents = [
        agent for agent, response in state["agent_responses"].items()
        if response["confidence"] < 0.4
    ]
    if len(low_confidence_agents) >= 3:
        return "low_confidence_cascade"
    
    # Normal case: revise proposal and retry
    return "revise_proposal"
```

---

## 3. LANGGRAPH IMPLEMENTATION PATTERN

### 3.1 Graph Structure Decision: Hybrid Approach

**Decision**: Use **Main Graph + Sub-Graphs** pattern.

**Rationale**:
- ✅ Single monolithic graph would be >30 nodes (unwieldy, hard to debug)
- ✅ Sub-graphs provide logical grouping (all agents, all tension protocols)
- ✅ LangGraph supports nested graphs with StateGraph composition
- ✅ Easier to test sub-graphs in isolation
- ✅ Allows parallel execution within sub-graphs

### 3.2 Main Graph Structure

```python
from langgraph.graph import StateGraph, END

# Main orchestration graph
workflow = StateGraph(ConsortiumState)

# ============================================
# MAIN GRAPH NODES
# ============================================

# Entry point
workflow.add_node("router", router_node)

# Agent execution (sub-graph)
workflow.add_node("execute_agents", agent_executor_subgraph)

# Tension handling
workflow.add_node("detect_tensions", tension_detector_node)
workflow.add_node("prioritize_tensions", tension_prioritizer_node)  # NEW: Multi-tension support
workflow.add_node("resolve_tensions", tension_resolver_subgraph)

# Convergence and synthesis
workflow.add_node("check_convergence", convergence_tester_node)
workflow.add_node("revise_proposal", proposal_revision_node)
workflow.add_node("synthesize_report", synthesizer_node)

# Failure mode handlers
workflow.add_node("handle_infinite_loop", infinite_loop_handler)
workflow.add_node("handle_complexity_overload", complexity_overload_handler)
workflow.add_node("handle_low_confidence", low_confidence_handler)

# Memory and output
workflow.add_node("write_to_memory", memory_writer_node)

# ============================================
# MAIN GRAPH EDGES
# ============================================

# Entry
workflow.set_entry_point("router")

# Unconditional edges
workflow.add_edge("router", "execute_agents")
workflow.add_edge("execute_agents", "detect_tensions")
workflow.add_edge("synthesize_report", "write_to_memory")
workflow.add_edge("write_to_memory", END)

# Conditional edges
workflow.add_conditional_edges(
    "detect_tensions",
    should_resolve_tensions,
    {
        "prioritize_tensions": "prioritize_tensions",  # NEW: Route to prioritizer first
        "check_convergence": "check_convergence"
    }
)

# NEW: Unconditional edge from prioritizer to resolver
workflow.add_edge("prioritize_tensions", "resolve_tensions")

workflow.add_conditional_edges(
    "resolve_tensions",
    lambda state: "check_convergence",
    {"check_convergence": "check_convergence"}
)

workflow.add_conditional_edges(
    "check_convergence",
    check_convergence_result,
    {
        "synthesize_report": "synthesize_report",
        "revise_proposal": "revise_proposal",
        "infinite_loop_detected": "handle_infinite_loop",
        "complexity_overload": "handle_complexity_overload",
        "low_confidence_cascade": "handle_low_confidence"
    }
)

# Loop edges (proposal revision)
workflow.add_edge("revise_proposal", "execute_agents")

# Failure mode exits
workflow.add_edge("handle_infinite_loop", END)
workflow.add_edge("handle_complexity_overload", END)
workflow.add_edge("handle_low_confidence", END)

# Compile
app = workflow.compile()
```

### 3.3 Iteration Count Management

**Decision**: Increment iteration counts **in the node** (protocol handler), not in edge functions.

**Rationale**:
- ✅ Nodes have full access to state and can update multiple fields atomically
- ✅ Edge functions should be lightweight routing logic only
- ✅ Easier to test (node logic is self-contained)
- ✅ Clear audit trail (iteration increment logged as part of node execution)

```python
# CORRECT: Increment in node
def protocol_handler_node(state: ConsortiumState) -> ConsortiumState:
    tension_id = "Sovereign_Economist"
    state["tension_iterations"][tension_id] = state["tension_iterations"].get(tension_id, 0) + 1
    state = increment_iteration_count(state, "Sovereign", "Economist")
    # ... rest of logic
    return state

# INCORRECT: Don't increment in edge function
def should_continue_tension(state: ConsortiumState) -> str:
    # Edge functions should only READ state, not MODIFY
    if state["tension_iterations"]["Sovereign_Economist"] < 4:
        return "continue"
    else:
        return "escalate"
```

---

## 4. COMPONENT INTERFACES

### 4.1 Agent Base Class

```python
from abc import ABC, abstractmethod

class Agent(ABC):
    """Abstract base class for all consortium agents"""
    
    def __init__(self, config: Dict[str, Any]):
        self.agent_id = config["agent_id"]
        self.name = config["name"]
        self.mandate = config["mandate"]
        self.system_prompt = config["system_prompt"]
        self.red_lines = config["red_lines"]
        self.acceptance_criteria = config["acceptance_criteria"]
        self.knowledge_domains = config["knowledge_domains"]
        
        # Pre-compute mandate embedding for routing
        self.mandate_embedding = self._compute_mandate_embedding()
    
    def _compute_mandate_embedding(self) -> List[float]:
        """Pre-compute embedding from mandate text for routing"""
        from openai import OpenAI
        client = OpenAI()
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=self.mandate
        )
        
        return response.data[0].embedding  # 1536-dim vector
    
    @abstractmethod
    def invoke(self, state: ConsortiumState) -> AgentResponse:
        """Main agent invocation logic"""
        pass
    
    def build_prompt(self, query: str, proposal: Optional[Proposal], 
                     memory_cases: List[Case], knowledge: Dict[str, Any]) -> str:
        """Builds complete prompt for LLM invocation"""
        
        prompt_parts = [
            f"# Agent Role: {self.name}",
            f"\n{self.system_prompt}",
            f"\n## Your Mandate\n{self.mandate}",
            f"\n## Non-Negotiable Red Lines\n" + "\n".join(f"- {rl}" for rl in self.red_lines),
        ]
        
        # Add historical context if available
        if memory_cases:
            prompt_parts.append("\n## Historical Precedents")
            for i, case in enumerate(memory_cases[:3], 1):
                prompt_parts.append(
                    f"\n### Case {i} (Similarity: {case['similarity_score']:.2f})\n"
                    f"Query: {case['query']}\n"
                )
        
        # Add current query and proposal
        prompt_parts.append(f"\n## Current Query\n{query}")
        
        if proposal:
            prompt_parts.append(
                f"\n## Proposal Under Review (Version {proposal['version']})\n"
                f"{proposal['content']}"
            )
        
        # Add response format instructions
        prompt_parts.append(
            "\n## Your Task\n"
            "Evaluate this query/proposal from your specialized perspective.\n\n"
            "RATING: [BLOCK | WARN | ACCEPT | ENDORSE]\n"
            "CONFIDENCE: [0.0-1.0]\n"
            "REASONING: [Your detailed analysis]\n"
        )
        
        return "\n".join(prompt_parts)
```

### 4.2 LLM Provider Adapter Interface

```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """
    Abstract interface for LLM providers.
    Supports conversation history (messages list) for multi-turn debates.
    """
    
    @abstractmethod
    def invoke(
        self,
        messages: List[Dict[str, str]],  # UPDATED: Now accepts conversation history
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Invoke the LLM with conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
                [
                    {"role": "user", "content": "First question"},
                    {"role": "assistant", "content": "First answer"},
                    {"role": "user", "content": "Follow-up question"}
                ]
            config: Provider-specific configuration
        
        Returns:
            {
                "response": str,
                "latency_ms": float,
                "token_count": int,
                "model_used": str
            }
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if provider is available"""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider with conversation history support"""
    
    def __init__(self, api_key: str):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
    
    def invoke(self, messages: List[Dict[str, str]], config: Dict[str, Any]) -> Dict[str, Any]:
        import time
        start_time = time.time()
        
        try:
            # Anthropic API expects messages list directly
            response = self.client.messages.create(
                model=config.get("model", "claude-sonnet-4-20250514"),
                max_tokens=config.get("max_tokens", 4096),
                temperature=config.get("temperature", 0.7),
                messages=messages  # UPDATED: Pass full conversation history
            )
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "response": response.content[0].text,
                "latency_ms": latency_ms,
                "token_count": response.usage.input_tokens + response.usage.output_tokens,
                "model_used": response.model
            }
        
        except Exception as e:
            if "timeout" in str(e).lower():
                raise ProviderTimeoutError(f"Anthropic timeout: {e}")
            elif "rate" in str(e).lower():
                raise ProviderRateLimitError(f"Anthropic rate limit: {e}")
            else:
                raise ProviderAPIError(f"Anthropic API error: {e}")
    
    def health_check(self) -> bool:
        try:
            self.invoke("ping", {"max_tokens": 10})
            return True
        except:
            return False
```

---

**[END OF PART 1]**

**Continue to Part 2 for**:
- Memory Architecture - Chroma Specifics
- Multi-LLM Provider Strategy
- Knowledge & Tools Strategy

**Continue to Part 3 for**:
- Configuration Management with concrete YAML examples
- Testing Strategy with complete test case
- Observability & Debugging
- Architecture Decision Trade-offs
- Performance Targets & Implications
- Technology Stack
- Implementation Guidance & Risk Assessment
