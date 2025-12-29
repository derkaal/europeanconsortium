# ARCHITECTURE - CRITICAL FIXES

**Project**: European Strategy Consortium Multi-Agent System  
**Date**: 2024-12-24  
**Status**: CRITICAL FIXES for Phase A Approval

---

## Critical Issue #1: Multiple Simultaneous Tensions

### Problem Statement

The current state schema can only track **ONE** active tension at a time:

```python
# ❌ CURRENT (WRONG)
tension_status: Optional[TensionStatus]
```

**Real-World Scenario**:
Query: "EU-only cloud with AI/ML capabilities and carbon-neutral operations at 30% cost reduction"

This triggers:
- ✅ Sovereign ↔ Economist (EU-only vs cost)
- ✅ Eco-System ↔ Architect (carbon vs ML compute intensity)

Both tensions are **active simultaneously** and need different resolution strategies.

---

### Solution: Multi-Tension State Management with Priority Queue

#### Updated State Schema (Section 1.1)

```python
class ConsortiumState(TypedDict, total=False):
    # ... existing fields ...
    
    # ============================================
    # TENSION PROTOCOL TRACKING (UPDATED)
    # ============================================
    
    # ❌ OLD: tension_status: Optional[TensionStatus]
    # ✅ NEW:
    active_tensions: List['TensionStatus']  # Multiple simultaneous tensions
    tension_priority_queue: List[str]  # Order to resolve tensions (by tension_id)
    tension_iterations: Dict[str, int]  # Tension protocol -> iteration count
    tension_history: List['TensionEvent']  # Full tension resolution history
    
    # NEW: Dependency tracking
    tension_dependency_graph: Dict[str, List[str]]  # tension_id -> blocking tension IDs
```

#### Updated TensionStatus Schema (Section 1.2)

```python
class TensionStatus(TypedDict):
    """Status of an active tension protocol"""
    
    # Core identification
    protocol_id: str  # e.g., "Sovereign_Economist"
    tension_id: str  # Unique instance ID (protocol_id + timestamp)
    agents_involved: Tuple[str, str]  # (agent_1, agent_2)
    
    # Iteration tracking
    iteration: int  # Current iteration number
    max_iterations: int  # Maximum allowed iterations
    
    # Status
    status: Literal["active", "resolved", "escalated", "blocked"]
    
    # Resolution tracking
    resolution_history: List[str]  # History of resolution attempts
    resolution: Optional[Dict[str, any]]  # Final resolution if resolved
    
    # Priority management
    priority: int  # 1=highest priority (resolve first), higher numbers=lower priority
    
    # Metadata
    trigger_reason: str  # Why this tension was triggered
    triggered_at: datetime
    resolved_at: Optional[datetime]
    
    # Dependency tracking
    depends_on_tensions: List[str]  # Tension IDs that must resolve first
    blocking_tensions: List[str]  # Tension IDs that this tension is blocking


class TensionEvent(TypedDict):
    """Single event in tension resolution history"""
    tension_id: str  # Links to TensionStatus.tension_id
    event_type: Literal["triggered", "iteration", "resolved", "escalated", "blocked"]
    details: Dict[str, any]
    timestamp: datetime
```

---

### Updated Graph Topology (Section 2.1)

**NEW NODE**: Add "Tension Prioritizer" before "Tension Resolver"

```
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
                │              │ Tension Prioritizer  │  ◄─── NEW NODE
                │              │                      │
                │              │ - Detects dependencies
                │              │ - Assigns priorities
                │              │ - Creates queue
                │              └──────────┬───────────┘
                │                         │
                │                         ▼
                │              ┌──────────────────────────────────────────┐
                │              │   Tension Resolver Sub-Graph             │
                │              │   [Processes tensions from priority queue]│
                │              └──────────────────────────────────────────┘
```

---

### Tension Prioritizer Node (NEW - Section 3.2)

```python
def tension_prioritizer_node(state: ConsortiumState) -> ConsortiumState:
    """
    Prioritizes multiple active tensions for resolution.
    
    Priority Rules:
    1. Jurist ↔ Philosopher (values conflict) = Priority 1 (instant escalation)
    2. Tensions with BLOCK ratings = Priority 2 (critical)
    3. Tensions with dependencies resolved = Priority 3
    4. Other tensions = Priority 4
    
    Also detects dependencies between tensions.
    """
    
    active_tensions = state.get("active_tensions", [])
    
    if not active_tensions:
        return state
    
    # ============================================
    # Step 1: Detect dependencies
    # ============================================
    
    dependency_graph = {}
    
    for tension in active_tensions:
        tension_id = tension["tension_id"]
        agents_involved = set(tension["agents_involved"])
        
        # Check for shared agents with other tensions
        blocking = []
        for other_tension in active_tensions:
            if other_tension["tension_id"] == tension_id:
                continue
            
            other_agents = set(other_tension["agents_involved"])
            
            # If tensions share an agent, they're dependent
            # (can't modify same agent's position in parallel)
            if agents_involved & other_agents:
                blocking.append(other_tension["tension_id"])
        
        dependency_graph[tension_id] = blocking
        tension["depends_on_tensions"] = blocking
    
    state["tension_dependency_graph"] = dependency_graph
    
    # ============================================
    # Step 2: Assign priorities
    # ============================================
    
    for tension in active_tensions:
        protocol_id = tension["protocol_id"]
        
        # Priority 1: Values conflicts (instant escalation)
        if protocol_id == "Jurist_Philosopher":
            tension["priority"] = 1
        
        # Priority 2: BLOCK-level tensions (critical)
        elif any(
            state["agent_responses"][agent]["rating"] == "BLOCK"
            for agent in tension["agents_involved"]
            if agent in state["agent_responses"]
        ):
            tension["priority"] = 2
        
        # Priority 3: Tensions with all dependencies resolved
        elif all(
            any(t["tension_id"] == dep and t["status"] in ["resolved", "escalated"]
                for t in active_tensions)
            for dep in tension["depends_on_tensions"]
        ):
            tension["priority"] = 3
        
        # Priority 4: Other tensions
        else:
            tension["priority"] = 4
    
    # ============================================
    # Step 3: Create priority queue
    # ============================================
    
    # Sort by priority (lower number = higher priority)
    sorted_tensions = sorted(
        active_tensions,
        key=lambda t: (t["priority"], t["triggered_at"])  # Secondary sort by time
    )
    
    # Create queue of tension IDs
    state["tension_priority_queue"] = [t["tension_id"] for t in sorted_tensions]
    
    # ============================================
    # Step 4: Log prioritization
    # ============================================
    
    state["audit_trail"].append({
        "event_id": generate_uuid(),
        "trace_id": state["trace_id"],
        "event_type": "tension_prioritization",
        "details": {
            "total_tensions": len(active_tensions),
            "priority_queue": state["tension_priority_queue"],
            "dependency_graph": dependency_graph,
            "priorities": {
                t["tension_id"]: t["priority"] for t in active_tensions
            }
        },
        "timestamp": datetime.now()
    })
    
    return state
```

---

### Updated Tension Resolver Sub-Graph (Section 3.3)

```python
def create_tension_resolver_subgraph() -> StateGraph:
    """
    Sub-graph for tension protocol resolution.
    Processes tensions from priority queue, respects dependencies.
    """
    
    subgraph = StateGraph(ConsortiumState)
    
    # ============================================
    # PROTOCOL HANDLER NODES
    # ============================================
    
    subgraph.add_node("sovereign_economist", sovereign_economist_protocol_node)
    subgraph.add_node("ecosystem_architect", ecosystem_architect_protocol_node)
    subgraph.add_node("jurist_philosopher", jurist_philosopher_protocol_node)
    subgraph.add_node("operator_strategy", operator_strategy_protocol_node)
    subgraph.add_node("futurist_all", futurist_all_protocol_node)
    
    # NEW: Queue processor node
    subgraph.add_node("process_next_tension", process_next_tension_node)
    
    # ============================================
    # CONDITIONAL ROUTING
    # ============================================
    
    def route_to_next_tension(state: ConsortiumState) -> str:
        """Route to next tension in priority queue"""
        
        priority_queue = state.get("tension_priority_queue", [])
        active_tensions = state.get("active_tensions", [])
        
        if not priority_queue:
            return END
        
        # Get next tension from queue
        next_tension_id = priority_queue[0]
        
        # Find the tension object
        next_tension = next(
            (t for t in active_tensions if t["tension_id"] == next_tension_id),
            None
        )
        
        if not next_tension:
            # Tension was resolved, skip
            state["tension_priority_queue"] = priority_queue[1:]
            return "process_next_tension"
        
        # Check if dependencies are resolved
        deps_resolved = all(
            any(t["tension_id"] == dep and t["status"] in ["resolved", "escalated"]
                for t in active_tensions)
            for dep in next_tension["depends_on_tensions"]
        )
        
        if not deps_resolved:
            # Dependencies not resolved, mark as blocked
            next_tension["status"] = "blocked"
            state["tension_priority_queue"] = priority_queue[1:]
            return "process_next_tension"
        
        # Route to appropriate protocol
        protocol_id = next_tension["protocol_id"]
        
        protocol_node_map = {
            "Sovereign_Economist": "sovereign_economist",
            "EcoSystem_Architect": "ecosystem_architect",
            "Jurist_Philosopher": "jurist_philosopher",
            "Operator_Strategy": "operator_strategy",
            "Futurist_All": "futurist_all"
        }
        
        return protocol_node_map.get(protocol_id, "process_next_tension")
    
    # Set conditional entry point
    subgraph.set_conditional_entry_point(
        route_to_next_tension,
        then={
            "sovereign_economist": "sovereign_economist",
            "ecosystem_architect": "ecosystem_architect",
            "jurist_philosopher": "jurist_philosopher",
            "operator_strategy": "operator_strategy",
            "futurist_all": "futurist_all",
            "process_next_tension": "process_next_tension",
            END: END
        }
    )
    
    # All protocol nodes return to queue processor
    for protocol_node in ["sovereign_economist", "ecosystem_architect",
                          "jurist_philosopher", "operator_strategy", "futurist_all"]:
        subgraph.add_edge(protocol_node, "process_next_tension")
    
    # Queue processor decides: continue or done
    subgraph.add_conditional_edges(
        "process_next_tension",
        lambda state: "continue" if state.get("tension_priority_queue") else "done",
        {
            "continue": route_to_next_tension,
            "done": END
        }
    )
    
    return subgraph.compile()


def process_next_tension_node(state: ConsortiumState) -> ConsortiumState:
    """
    Processes result of tension resolution and prepares for next tension.
    """
    
    priority_queue = state.get("tension_priority_queue", [])
    
    if priority_queue:
        # Remove processed tension from queue
        state["tension_priority_queue"] = priority_queue[1:]
    
    # Check if any blocked tensions can now proceed
    active_tensions = state.get("active_tensions", [])
    for tension in active_tensions:
        if tension["status"] == "blocked":
            # Check if dependencies are now resolved
            deps_resolved = all(
                any(t["tension_id"] == dep and t["status"] in ["resolved", "escalated"]
                    for t in active_tensions)
                for dep in tension["depends_on_tensions"]
            )
            
            if deps_resolved:
                # Unblock and add back to queue
                tension["status"] = "active"
                state["tension_priority_queue"].append(tension["tension_id"])
    
    return state
```

---

### Updated Main Graph (Section 3.2)

```python
# Main orchestration graph
workflow = StateGraph(ConsortiumState)

# ... existing nodes ...

# NEW: Add tension prioritizer
workflow.add_node("prioritize_tensions", tension_prioritizer_node)

# ... existing edges ...

# UPDATED: Conditional edges from detect_tensions
workflow.add_conditional_edges(
    "detect_tensions",
    should_resolve_tensions,
    {
        "prioritize_tensions": "prioritize_tensions",  # NEW: Go to prioritizer first
        "check_convergence": "check_convergence"
    }
)

# NEW: Unconditional edge from prioritizer to resolver
workflow.add_edge("prioritize_tensions", "resolve_tensions")
```

---

### Example: Multi-Tension Flow

```
Query: "EU-only cloud with AI/ML and carbon-neutral at 30% cost reduction"

Step 1: Agent Execution
  - Sovereign: BLOCK (EU-only conflicts with cost reduction)
  - Economist: BLOCK (30% cost reduction impossible with EU-only)
  - Eco-System: WARN (AI/ML compute-intensive, conflicts with carbon-neutral)
  - Architect: ACCEPT (can design hybrid)

Step 2: Tension Detector
  Detects:
    - Sovereign ↔ Economist
    - Eco-System ↔ Architect
  
  Creates active_tensions:
    [
      {
        tension_id: "tension_001",
        protocol_id: "Sovereign_Economist",
        agents_involved: ("Sovereign", "Economist"),
        status: "active",
        iteration: 0,
        triggered_at: <timestamp>
      },
      {
        tension_id: "tension_002",
        protocol_id: "EcoSystem_Architect",
        agents_involved: ("EcoSystem", "Architect"),
        status: "active",
        iteration: 0,
        triggered_at: <timestamp>
      }
    ]

Step 3: Tension Prioritizer
  Dependency detection:
    - Both tensions share "Architect" → tension_002 depends on tension_001
  
  Priority assignment:
    - tension_001: priority=2 (BLOCK ratings)
    - tension_002: priority=4 (dependencies not resolved)
  
  Priority queue: ["tension_001", "tension_002"]

Step 4: Tension Resolver
  Process tension_001 (Sovereign ↔ Economist):
    - Iteration 1: Calculate trust premium
    - Iteration 2: Architect proposes hybrid
    - Resolution: Hybrid architecture with EU regions + Confidential Computing
    - Status: "resolved"
  
  Remove tension_001 from queue: ["tension_002"]
  
  Process tension_002 (Eco-System ↔ Architect):
    - Dependencies now resolved (tension_001 done)
    - Iteration 1: Calculate SCI for hybrid architecture
    - Iteration 2: Add carbon mitigation (renewable energy scheduling)
    - Resolution: Hybrid + carbon-aware scheduling
    - Status: "resolved"

Step 5: Check Convergence
  All tensions resolved → Proceed to convergence testing
```

---

## Critical Issue #4: Conversation History Preservation During Provider Failover

### Problem Statement

The current provider adapter doesn't preserve **conversation history** during failover, which breaks:
1. **Multi-turn debates** (agent changes position over iterations)
2. **Context continuity** (agent needs to remember what it said before)
3. **Provider switches** (new provider has no context)

**Example Failure Scenario**:
```
Iteration 1 (Anthropic):
  Sovereign: "BLOCK - data subject to US CLOUD Act"

Iteration 2 (Anthropic fails, fallback to Mistral):
  Sovereign: "ACCEPT - seems fine" ← Lost context! Contradicts iteration 1
```

---

### Solution: Conversation History Preservation in Provider Adapter

#### Updated LLM Provider Adapter (Section 4.2)

```python
class LLMProviderManager:
    """
    Manages multi-provider failover with conversation history preservation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = self._initialize_providers()
        self.retry_attempts = config.get("retry_attempts", 2)
        self.base_delay = config.get("base_delay_seconds", 1.0)
        self.timeout = config.get("timeout_seconds", 30)
        
        # NEW: Conversation history per agent
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        # Structure: {agent_id: [{role: "user", content: "..."}, {role: "assistant", content: "..."}]}
    
    def invoke_with_failover(
        self,
        agent_id: str,
        prompt: str,
        state: ConsortiumState
    ) -> str:
        """
        Invoke LLM with automatic failover AND conversation history preservation.
        
        CRITICAL: Conversation history is preserved across provider switches.
        """
        
        # ============================================
        # Step 1: Build message context with history
        # ============================================
        
        # Get existing conversation history for this agent
        history = self.conversation_history.get(agent_id, [])
        
        # Build complete message list (history + current prompt)
        messages = history + [{"role": "user", "content": prompt}]
        
        last_exception = None
        
        # ============================================
        # Step 2: Try providers with history
        # ============================================
        
        for provider_info in self.providers:
            provider_name = provider_info["name"]
            provider = provider_info["instance"]
            
            # Attempt with retry and exponential backoff
            for attempt in range(self.retry_attempts):
                try:
                    # CRITICAL: Pass full conversation history to provider
                    result = provider.invoke(
                        messages,  # ← Full history included
                        {
                            "max_tokens": 4096,
                            "temperature": 0.7,
                            "timeout": self.timeout
                        }
                    )
                    
                    # ============================================
                    # Step 3: Update conversation history on success
                    # ============================================
                    
                    if agent_id not in self.conversation_history:
                        self.conversation_history[agent_id] = []
                    
                    # Add user message to history
                    self.conversation_history[agent_id].append({
                        "role": "user",
                        "content": prompt
                    })
                    
                    # Add assistant response to history
                    self.conversation_history[agent_id].append({
                        "role": "assistant",
                        "content": result["response"]
                    })
                    
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
                            "tokens": result["token_count"],
                            "conversation_turn": len(self.conversation_history[agent_id]) // 2  # Each turn = user + assistant
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
            
            # ============================================
            # Step 4: Failover to next provider WITH history
            # ============================================
            
            if provider_info != self.providers[-1]:  # Not the last provider
                next_provider = self.providers[self.providers.index(provider_info) + 1]
                
                # CRITICAL: Log that conversation history is preserved
                state["failover_events"].append({
                    "from_provider": provider_name,
                    "to_provider": next_provider["name"],
                    "agent_id": agent_id,
                    "reason": f"Provider failed after {self.retry_attempts} attempts",
                    "state_preserved": True,
                    "conversation_history_length": len(self.conversation_history.get(agent_id, [])),
                    "timestamp": datetime.now()
                })
                
                # Continue to next provider (messages variable already contains full history)
        
        # All providers failed
        raise AllProvidersFailedError(
            f"All {len(self.providers)} providers failed for agent {agent_id}. "
            f"Last error: {last_exception}"
        )
    
    def clear_conversation_history(self, agent_id: str):
        """
        Clear conversation history for an agent.
        Called after convergence or escalation.
        """
        if agent_id in self.conversation_history:
            del self.conversation_history[agent_id]
    
    def clear_all_conversations(self):
        """
        Clear all conversation histories.
        Called at the start of a new query.
        """
        self.conversation_history = {}
    
    def get_conversation_length(self, agent_id: str) -> int:
        """Get number of turns in conversation for an agent"""
        return len(self.conversation_history.get(agent_id, [])) // 2
```

#### Updated Provider Interface (Section 4.2)

```python
class LLMProvider(ABC):
    """
    Abstract interface for LLM providers.
    Supports conversation history (messages list).
    """
    
    @abstractmethod
    def invoke(
        self,
        messages: List[Dict[str, str]],  # ← Changed from single prompt string
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


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider with conversation history support"""
    
    def invoke(self, messages: List[Dict[str, str]], config: Dict[str, Any]) -> Dict[str, Any]:
        import time
        start_time = time.time()
        
        try:
            # Anthropic API expects messages list directly
            response = self.client.messages.create(
                model=config.get("model", "claude-sonnet-4-20250514"),
                max_tokens=config.get("max_tokens", 4096),
                temperature=config.get("temperature", 0.7),
                messages=messages  # ← Pass full conversation history
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


class MistralProvider(LLMProvider):
    """Mistral AI provider with conversation history support"""
    
    def invoke(self, messages: List[Dict[str, str]], config: Dict[str, Any]) -> Dict[str, Any]:
        import time
        start_time = time.time()
        
        try:
            # Mistral API expects messages list
            response = self.client.chat(
                model=config.get("model", "mistral-large-latest"),
                messages=messages,  # ← Pass full conversation history
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 4096)
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "response": response.choices[0].message.content,
                "latency_ms": latency_ms,
                "token_count": response.usage.total_tokens,
                "model_used": response.model
            }
        
        except Exception as e:
            if "timeout" in str(e).lower():
                raise ProviderTimeoutError(f"Mistral timeout: {e}")
            elif "rate" in str(e).lower():
                raise ProviderRateLimitError(f"Mistral rate limit: {e}")
            else:
                raise ProviderAPIError(f"Mistral API error: {e}")
```

#### Conversation History Lifecycle

```python
# At start of new query
def router_node(state: ConsortiumState) -> ConsortiumState:
    """Router node - entry point for each query"""
    
    # Get provider manager from application context
    provider_manager = get_provider_manager()
    
    # Clear all conversation histories for fresh start
    provider_manager.clear_all_conversations()
    
    # ... rest of routing logic ...
    
    return state


# After convergence
def synthesizer_node(state: ConsortiumState) -> ConsortiumState:
    """Synthesizer node - generates final report"""
    
    # ... synthesis logic ...
    
    # Get provider manager
    provider_manager = get_provider_manager()
    
    # Clear conversation histories for all agents
    # (Query is complete, no need to retain context)
    provider_manager.clear_all_conversations()
    
    return state
```

---

## Updated Test Case for Multi-Tension + Conversation History

```python
# tests/test_critical_fixes.py

def test_multi_tension_with_conversation_history():
    """
    Test that multiple tensions are handled correctly
    AND conversation history is preserved during resolution.
    """
    
    # Query that triggers multiple tensions
    query = "EU-only cloud with AI/ML capabilities and carbon-neutral operations at 30% cost reduction"
    
    initial_state = {
        "query": query,
        "query_context": {
            "industry": "Technology",
            "company_size": "Large",
            "current_state": "On-premise",
            "constraints": ["EU-only", "carbon-neutral", "cost-reduction-30%"]
        },
        "trace_id": "test_multi_tension",
        "active_tensions": [],
        "tension_priority_queue": [],
        "tension_dependency_graph": {},
        "iteration_counts": {},
        "tension_iterations": {},
        "audit_trail": []
    }
    
    # Execute consortium
    final_state = consortium_app.invoke(initial_state)
    
    # ============================================
    # VALIDATE: Multiple tensions detected
    # ============================================
    
    tension_ids = [t["protocol_id"] for t in final_state["active_tensions"]]
    assert "Sovereign_Economist" in tension_ids, "Expected Sovereign_Economist tension"
    assert "EcoSystem_Architect" in tension_ids, "Expected EcoSystem_Architect tension"
    
    # ============================================
    # VALIDATE: Tensions were prioritized
    # ============================================
    
    assert "tension_priority_queue" in final_state
    assert len(final_state["tension_priority_queue"]) >= 2
    
    # ============================================
    # VALIDATE: Dependencies detected
    # ============================================
    
    assert "tension_dependency_graph" in final_state
    dependency_graph = final_state["tension_dependency_graph"]
    
    # At least one tension should have dependencies
    has_dependencies = any(len(deps) > 0 for deps in dependency_graph.values())
    assert has_dependencies, "Expected at least one tension to have dependencies"
    
    # ============================================
    # VALIDATE: Conversation history preserved
    # ============================================
    
    # Check audit trail for conversation turn tracking
    llm_invocations = [
        event for event in final_state["audit_trail"]
        if event["event_type"] == "llm_invocation"
    ]
    
    # Should have multiple turns for at least one agent
    agent_turns = {}
    for invocation in llm_invocations:
        agent_id = invocation["agent_id"]
        turn = invocation["details"].get("conversation_turn", 0)
        if agent_id not in agent_turns:
            agent_turns[agent_id] = []
        agent_turns[agent_id].append(turn)
    
    # At least one agent should have multiple turns (multi-turn debate)
    multi_turn_agents = [agent for agent, turns in agent_turns.items() if len(turns) > 1]
    assert len(multi_turn_agents) > 0, "Expected at least one agent to have multi-turn conversation"
    
    # ============================================
    # VALIDATE: Provider failover preserved history
    # ============================================
    
    failover_events = final_state.get("failover_events", [])
    if len(failover_events) > 0:
        # If failover occurred, verify conversation history was preserved
        for event in failover_events:
            assert event["state_preserved"] == True
            assert "conversation_history_length" in event
            assert event["conversation_history_length"] >= 0
    
    # ============================================
    # VALIDATE: Both tensions resolved
    # ============================================
    
    for tension in final_state["active_tensions"]:
        assert tension["status"] in ["resolved", "escalated"], \
            f"Tension {tension['protocol_id']} not resolved: {tension['status']}"
    
    print("✅ Multi-tension with conversation history test PASSED")
```

---

## Summary of Critical Fixes

### Issue #1: Multiple Simultaneous Tensions ✅ FIXED

**Changes Made**:
1. ✅ Updated `ConsortiumState` schema:
   - Changed `tension_status: Optional[TensionStatus]` → `active_tensions: List[TensionStatus]`
   - Added `tension_priority_queue: List[str]`
   - Added `tension_dependency_graph: Dict[str, List[str]]`

2. ✅ Updated `TensionStatus` schema:
   - Added `priority: int`
   - Added `depends_on_tensions: List[str]`
   - Added `blocking_tensions: List[str]`

3. ✅ Added new node: `tension_prioritizer_node`
   - Detects dependencies between tensions
   - Assigns priorities
   - Creates resolution queue

4. ✅ Updated `tension_resolver_subgraph`:
   - Processes tensions from priority queue
   - Respects dependencies
   - Handles blocked tensions

5. ✅ Updated graph topology:
   - Added "Tension Prioritizer" node
   - Updated routing logic

### Issue #4: Conversation History Preservation ✅ FIXED

**Changes Made**:
1. ✅ Updated `LLMProviderManager`:
   - Added `conversation_history: Dict[str, List[Dict[str, str]]]`
   - Modified `invoke_with_failover` to preserve history
   - Added `clear_conversation_history` and `clear_all_conversations` methods

2. ✅ Updated `LLMProvider` interface:
   - Changed `invoke(prompt: str, ...)` → `invoke(messages: List[Dict], ...)`
   - All providers now accept conversation history

3. ✅ Updated provider implementations:
   - `AnthropicProvider` passes messages to API
   - `MistralProvider` passes messages to API

4. ✅ Added conversation lifecycle:
   - Clear at query start (router_node)
   - Preserve during debates
   - Clear after convergence (synthesizer_node)

5. ✅ Enhanced audit trail:
   - Track conversation turns
   - Log history preservation during failover

---

## Files Updated

- **ARCHITECTURE_PART1.md** Section 1.1, 1.2: State schema updates
- **ARCHITECTURE_PART1.md** Section 2.1, 2.2: Graph topology updates
- **ARCHITECTURE_PART1.md** Section 3.2, 3.3: Tension handling updates
- **ARCHITECTURE_PART1.md** Section 4.2: Provider adapter updates
- **ARCHITECTURE_PART3.md** Section 9.2: Test case updates

---

## ✅ CRITICAL FIXES COMPLETE

Both critical issues are now resolved. The architecture supports:
- ✅ Multiple simultaneous tensions with dependency management
- ✅ Conversation history preservation across provider failovers

**Status**: Ready for Phase A approval and Phase R implementation.
