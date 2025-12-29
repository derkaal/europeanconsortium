# LangGraph Best Practices - Research Findings

## Research Query 1: State Management with TypedDict

### Key Findings:

1. **Nodes return partial state updates** - Don't mutate input state, return dict with updates
2. **Use reducers for list/dict fields** - Prevents concurrent update errors
3. **Annotated type for reducers** - `Annotated[list, operator.add]` for append-only lists
4. **StateGraph auto-merges** - Return values automatically merged with existing state

### Pattern to Apply:
```python
from typing import Annotated
from typing_extensions import TypedDict
import operator

class ConsortiumState(TypedDict):
    # Simple fields - direct replacement
    query: str
    convergence_status: Dict[str, Any]
    
    # List fields with reducer - append-only
    active_tensions: Annotated[list, operator.add]
    
    # Dict fields - direct replacement (no reducer needed)
    agent_responses: Dict[str, Dict[str, Any]]

def node(state: ConsortiumState) -> ConsortiumState:
    # Return partial update - will be merged
    return {
        "agent_responses": {"economist": {...}},
        "active_tensions": [new_tension]  # Reducer will append
    }
```

**Decision**: Use `operator.add` reducer for `active_tensions` list to enable safe concurrent updates.

---

## Research Query 2: Conditional Edges

### Key Findings:

1. **Use Literal type hints** - `-> Literal["node_b", "node_c"]` for routing functions
2. **Return string node names** - Simple string return values
3. **Can return multiple nodes** - `Sequence[str]` for fan-out
4. **Optional path mapping** - Can provide dict mapping return values to nodes

### Pattern to Apply:
```python
from typing import Literal

def route_after_tension_detection(
    state: ConsortiumState
) -> Literal["tension_resolver", "convergence_test"]:
    """Route based on tension detection."""
    if state.get("active_tensions"):
        return "tension_resolver"
    return "convergence_test"

# Add to graph
graph.add_conditional_edges(
    "tension_detector",
    route_after_tension_detection
)
```

**Decision**: Use `Literal` type hints for all routing functions to enable proper graph visualization in LangGraph Studio.

---

## Research Query 3: Node Function Patterns

### Key Findings:

1. **Signature**: `def node(state: StateType) -> StateType` or `-> Dict[str, Any]`
2. **Return partial updates** - Only return fields that changed
3. **Don't mutate input** - Always return new dict
4. **Access state via dict keys** - `state["field_name"]`
5. **Can use Command object** - For combined state update + routing

### Pattern to Apply:
```python
def agent_executor_node(state: ConsortiumState) -> ConsortiumState:
    """Execute agents and return partial state update."""
    
    # Read from state
    triggered_agents = state["triggered_agents"]
    query = state["query"]
    
    # Process
    responses = {}
    for agent_id in triggered_agents:
        response = execute_agent(agent_id, query)
        responses[agent_id] = response
    
    # Return ONLY updated fields
    return {
        "agent_responses": responses
    }
```

**Decision**: All nodes return partial state dicts. No mutation of input state.

---

## Research Query 4: Parallel Execution

### Key Findings:

1. **Send API for dynamic parallelism** - `Send("node", state)` for map-reduce
2. **Multiple edges = parallel execution** - Nodes with multiple incoming edges run in parallel
3. **Reducers required for parallel writes** - Must use reducer for fields updated by parallel nodes
4. **@task decorator** - For parallel I/O operations within a node
5. **defer=True** - Wait for all branches before executing node

### Pattern to Apply:

**Option A: Send API (Dynamic Parallelism)**
```python
from langgraph.types import Send

def router_node(state: ConsortiumState) -> list[Send]:
    """Dynamically create parallel agent tasks."""
    agents = ["economist", "sovereign", "jurist"]
    return [
        Send("agent_executor", {"agent_id": agent, "query": state["query"]})
        for agent in agents
    ]
```

**Option B: Sequential Execution (Simpler)**
```python
def agent_executor_node(state: ConsortiumState) -> ConsortiumState:
    """Execute all agents sequentially."""
    responses = {}
    for agent_id in state["triggered_agents"]:
        responses[agent_id] = execute_agent(agent_id, state)
    return {"agent_responses": responses}
```

**Decision**: Use **Option B (Sequential)** for MVP. Send API adds complexity and our agents need full state context, not isolated tasks. Can optimize with parallel execution later if needed.

---

## Implementation Checklist

Based on research findings:

- [x] Add `operator.add` reducer to `active_tensions` in state
- [x] Use `Literal` type hints for all routing functions
- [x] Nodes return partial state dicts (no mutation)
- [x] Sequential agent execution (no Send API for now)
- [x] Proper error handling in nodes
- [x] Logging for observability

---

## Code Quality Notes

1. **Type Safety**: All routing functions use `Literal` for proper type checking
2. **Immutability**: No state mutation, only return new dicts
3. **Reducers**: Use for any field that might be updated concurrently
4. **Simplicity**: Start sequential, optimize to parallel later if needed
