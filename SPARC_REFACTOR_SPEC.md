# SPARC REFACTORING SPECIFICATION
## Refactor: Consortium from "Compliance Auditor" to "Strategy Engine"

**Date**: 2025-12-31
**Branch**: `claude/refactor-langgraph-Naqpy`
**Objective**: Transform LangGraph from parallel "Department of No" to sequential "Adversarial Strategy Generation"

---

## S - SPECIFICATION

### Problem Statement
**Current Failure Mode:**
- 0% Consensus, No Inter-Agent Tensions detected
- "Deadlock" escalation with 11 blocking constraints
- Zero strategic upside or competitive vision
- Functions as "Department of No" compliance checker

**Root Cause:**
- Parallel agent execution (all 12 agents triggered simultaneously)
- No strategic "Proposal" phase - agents critique the raw user query
- No "Alchemy" transformation of constraints into opportunities
- Synthesizer allows "Deadlock" without forcing "Yes, If..." resolution

### Target Architecture
**New Workflow: "Proposal-Critique-Transformation Cascade"**

```
User Query
    ↓
[Scout] (unchanged - research gathering)
    ↓
[STEP 1: PROVOCATION]
    ↓
Founder Agent ALONE
    → Generates "Max Upside" aggressive proposal
    → Output: draft_strategy (visionary, ignores constraints)
    ↓
[STEP 2: THE ATTACK]
    ↓
Parallel execution of "The Breakers":
    → Jurist, Sovereign, Economist, Technologist, Eco-System
    → Philosopher, Architect, Intelligence Sovereign, Ethnographer, Consumer Voice
    → Input: Founder's draft_strategy (NOT raw user query)
    → Output: List of blocking constraints + warnings
    ↓
[STEP 3: THE ALCHEMY]
    ↓
Alchemist Agent ALONE
    → Input: Collected constraints from Step 2
    → Transform: "GDPR blocker" → "Privacy-First Premium Brand"
    → Output: reframed_opportunities (constraints as features)
    ↓
[Tension Detector → Tension Resolver] (unchanged)
    ↓
[Convergence Test] (unchanged)
    ↓
[STEP 4: THE GATE]
    ↓
CLA Agent (unchanged - validates commitment/trigger/cost/leverage)
    ↓
[STEP 5: THE RESOLUTION]
    ↓
Architect Revision (unchanged)
    ↓
Advantage Analysis (unchanged)
    ↓
[SYNTHESIZER with "YES, IF..." PROTOCOL]
    → NEVER output "Deadlock" unless strictly illegal
    → Transform blocks into conditional approvals:
      "Proceed with Founder's vision YES, IF [Jurist's mitigation]"
    → Pyramid Principle structure:
        1. The Strategic Bet (Founder + Alchemist vision)
        2. The Governance Shield (Constraints as protective moats)
        3. The Execution Path (Roadmap)
        4. The Kill Switch (CLA exit criteria)
```

### Success Criteria
1. **Consensus > 0%**: Synthesizer produces a path forward (not deadlock)
2. **Strategic Upside**: Founder's vision leads the final report
3. **Alchemy Active**: Constraints reframed as opportunities in final output
4. **Yes, If... Protocol**: Blockers converted to conditional approvals
5. **Pyramid Principle**: Report starts with "Why we should do this" (not risks)

---

## P - PSEUDOCODE

### New Graph Topology (graph.py)

```python
def create_consortium_graph_cascade(search_tool=None, enable_scout=True):
    """Create adversarial strategy cascade graph."""

    graph = StateGraph(ConsortiumState)

    # === STEP 0: Scout (unchanged) ===
    if enable_scout:
        graph.add_node("scout", scout_node)
        graph.set_entry_point("scout")
        graph.add_edge("scout", "founder_provocation")
    else:
        graph.set_entry_point("founder_provocation")

    # === STEP 1: Founder Provocation ===
    graph.add_node("founder_provocation", founder_provocation_node)

    # === STEP 2: The Breakers (parallel critique) ===
    graph.add_node("breaker_critique", breaker_critique_node)
    graph.add_edge("founder_provocation", "breaker_critique")

    # === STEP 3: The Alchemy ===
    graph.add_node("alchemist_transformation", alchemist_transformation_node)
    graph.add_edge("breaker_critique", "alchemist_transformation")

    # === Tension Detection & Resolution (unchanged) ===
    graph.add_node("tension_detector", tension_detector_node)
    graph.add_edge("alchemist_transformation", "tension_detector")

    graph.add_node("tension_resolver", tension_resolver_node)
    graph.add_conditional_edges("tension_detector", route_after_tension)

    # === Convergence Test ===
    graph.add_node("convergence_test", convergence_test_node)
    graph.add_conditional_edges("tension_resolver", route_after_resolution)
    graph.add_conditional_edges("convergence_test", route_after_convergence)

    # === CLA Gate ===
    graph.add_node("cla_gate", cla_gate_node)
    graph.add_conditional_edges("cla_gate", route_after_cla_gate)

    # === Final Synthesis with Yes-If Protocol ===
    graph.add_node("architect_revision", architect_revision_node)
    graph.add_node("advantage_analysis", advantage_analysis_node)
    graph.add_node("synthesizer_yes_if", synthesizer_yes_if_node)

    graph.add_edge("architect_revision", "advantage_analysis")
    graph.add_edge("advantage_analysis", "synthesizer_yes_if")
    graph.add_edge("synthesizer_yes_if", END)

    return graph.compile()
```

### New Nodes Pseudocode

```python
# === Step 1: Founder Provocation Node ===
def founder_provocation_node(state):
    """Execute Founder agent ALONE to generate aggressive proposal."""
    founder = FounderAgent(config)

    # Founder gets: user query + scout research
    founder_response = founder.invoke(state)

    return {
        "draft_strategy": founder_response.reasoning,  # The visionary proposal
        "agent_responses": {"founder": founder_response.to_dict()}
    }

# === Step 2: Breaker Critique Node ===
def breaker_critique_node(state):
    """Execute all constraint agents in parallel against Founder's proposal."""

    draft_strategy = state.get("draft_strategy")

    # Inject draft_strategy into context for all breaker agents
    enhanced_state = state.copy()
    enhanced_state["context"]["founder_proposal"] = draft_strategy
    enhanced_state["query"] = f"Evaluate this proposal: {draft_strategy}"

    # Trigger all breaker agents (10 agents)
    breaker_agents = [
        "jurist", "sovereign", "economist", "technologist", "ecosystem",
        "philosopher", "architect", "intelligence_sovereign",
        "ethnographer", "consumer_voice"
    ]

    agent_responses = {}
    for agent_id in breaker_agents:
        agent = get_agent(agent_id)
        response = agent.invoke(enhanced_state)
        agent_responses[agent_id] = response.to_dict()

    # Collect all constraints/blockers
    constraints = []
    for agent_id, response in agent_responses.items():
        if response["rating"] in ["BLOCK", "WARN"]:
            constraints.append({
                "agent": agent_id,
                "rating": response["rating"],
                "constraint": response["reasoning"]
            })

    return {
        "agent_responses": agent_responses,
        "breaker_constraints": constraints
    }

# === Step 3: Alchemist Transformation Node ===
def alchemist_transformation_node(state):
    """Execute Alchemist to convert constraints into opportunities."""

    constraints = state.get("breaker_constraints", [])

    # Build alchemy prompt
    alchemy_query = f"""
    The following constraints were raised by the consortium:

    {format_constraints(constraints)}

    Your task: Transform each constraint into a competitive advantage or premium feature.
    Output a list of "Reframed Opportunities".
    """

    alchemist_state = state.copy()
    alchemist_state["query"] = alchemy_query
    alchemist_state["context"]["constraints_to_transmute"] = constraints

    alchemist = AlchemistAgent(config)
    alchemist_response = alchemist.invoke(alchemist_state)

    # Extract reframed opportunities from alchemist reasoning
    opportunities = parse_opportunities(alchemist_response.reasoning)

    # Update agent responses
    updated_responses = state.get("agent_responses", {}).copy()
    updated_responses["alchemist"] = alchemist_response.to_dict()

    return {
        "agent_responses": updated_responses,
        "reframed_opportunities": opportunities
    }

# === Step 5: Synthesizer with Yes-If Protocol ===
def synthesizer_yes_if_node(state):
    """Synthesize with MANDATORY Yes-If protocol - no deadlocks allowed."""

    founder_vision = state.get("draft_strategy")
    constraints = state.get("breaker_constraints", [])
    opportunities = state.get("reframed_opportunities", [])

    # Check for hard blocks (illegal)
    illegal_blocks = [
        c for c in constraints
        if c["rating"] == "BLOCK" and "illegal" in c["constraint"].lower()
    ]

    if illegal_blocks:
        recommendation = "CANNOT PROCEED - Illegal proposal"
    else:
        # Apply YES, IF... protocol
        conditional_approvals = []
        for constraint in constraints:
            if constraint["rating"] == "BLOCK":
                mitigation = extract_mitigation(constraint)
                conditional_approvals.append({
                    "blocker": constraint["agent"],
                    "condition": f"YES, IF {mitigation}"
                })

        recommendation = format_yes_if_recommendation(
            founder_vision,
            opportunities,
            conditional_approvals
        )

    # Build Pyramid Principle report
    report = {
        "structure": "Pyramid Principle",
        "sections": {
            "1_strategic_bet": {
                "title": "The Strategic Bet",
                "content": f"{founder_vision}\n\nReframed Opportunities:\n{format_opportunities(opportunities)}"
            },
            "2_governance_shield": {
                "title": "The Governance Shield",
                "content": format_conditional_approvals(conditional_approvals)
            },
            "3_execution_path": {
                "title": "The Execution Path",
                "content": extract_roadmap(state)
            },
            "4_kill_switch": {
                "title": "The Kill Switch",
                "content": extract_cla_exit_criteria(state)
            }
        },
        "recommendation": recommendation,
        "supporting_arguments": state.get("agent_responses", {}),
        "decision_provenance": build_provenance(state)
    }

    return {"final_recommendation": report}
```

---

## A - ARCHITECTURE

### Files to Modify

1. **`src/consortium/graph.py`**
   - Add new cascade graph builder: `create_consortium_graph_cascade()`
   - Keep old graph for backwards compatibility (rename to `create_consortium_graph_parallel()`)

2. **`src/consortium/nodes/__init__.py`**
   - Export new nodes: `founder_provocation_node`, `breaker_critique_node`, `alchemist_transformation_node`

3. **`src/consortium/nodes/founder_provocation.py`** (NEW)
   - Implements Step 1: Founder runs alone

4. **`src/consortium/nodes/breaker_critique.py`** (NEW)
   - Implements Step 2: All constraint agents attack Founder's proposal

5. **`src/consortium/nodes/alchemist_transformation.py`** (NEW)
   - Implements Step 3: Alchemist converts constraints to opportunities

6. **`src/consortium/nodes/synthesizer.py`**
   - Update `synthesizer_node()` to `synthesizer_yes_if_node()`
   - Implement "Yes, If..." protocol
   - Enhance Pyramid Principle with new 4-section structure

7. **`src/consortium/state.py`**
   - Add new state fields:
     - `draft_strategy: str` (Founder's proposal)
     - `breaker_constraints: List[Dict]` (Collected blockers)
     - `reframed_opportunities: List[Dict]` (Alchemist output)

### New State Fields

```python
class ConsortiumState(TypedDict, total=False):
    # ... existing fields ...

    # Cascade workflow fields
    draft_strategy: str  # Founder's aggressive proposal
    breaker_constraints: List[Dict[str, Any]]  # Collected blocks/warns
    reframed_opportunities: List[Dict[str, Any]]  # Alchemy output
```

---

## R - REFINEMENT

### Key Design Decisions

1. **Backwards Compatibility**: Keep old parallel graph as `create_consortium_graph_parallel()` - don't break existing integrations

2. **Founder Enhancement**: Founder agent prompt is already excellent ("Feature Hunter"). No changes needed to agent logic.

3. **Alchemist Enhancement**: Alchemist agent prompt is already excellent ("Regulation-to-Value Converter"). No changes needed to agent logic.

4. **Synthesizer Protocol**:
   - NEVER output "Deadlock" unless `illegal` keyword in blocker reasoning
   - Transform all other blocks into "YES, IF [mitigation]" format
   - Prioritize Founder vision in final report (top of Pyramid)

5. **Pyramid Principle Structure**:
   ```
   1. The Strategic Bet (Why we SHOULD do this)
      - Founder's vision
      - Alchemist's reframed opportunities

   2. The Governance Shield (How we PROTECT the bet)
      - Conditional approvals from constraint agents
      - "YES, IF..." statements

   3. The Execution Path (How we EXECUTE)
      - Roadmap from Architect
      - Action items

   4. The Kill Switch (How we EXIT if needed)
      - CLA exit criteria
      - Commitment/Trigger/Cost/Leverage tests
   ```

6. **Error Handling**: If Founder or Alchemist fail, gracefully degrade to parallel mode

---

## C - COMPLETION

### Testing Checklist

1. **Unit Tests**:
   - [ ] `test_founder_provocation_node()`
   - [ ] `test_breaker_critique_node()`
   - [ ] `test_alchemist_transformation_node()`
   - [ ] `test_synthesizer_yes_if_protocol()`

2. **Integration Tests**:
   - [ ] Full cascade workflow with real query
   - [ ] Verify Consensus > 0% (no deadlock)
   - [ ] Verify Pyramid Principle structure
   - [ ] Verify Founder vision appears first in report

3. **Regression Tests**:
   - [ ] Old parallel graph still works (backwards compatibility)
   - [ ] Scout integration unchanged
   - [ ] CLA gate still functions

### Rollout Plan

1. **Phase 1**: Implement new nodes (founder_provocation, breaker_critique, alchemist_transformation)
2. **Phase 2**: Create new cascade graph topology
3. **Phase 3**: Update synthesizer with Yes-If protocol
4. **Phase 4**: Test end-to-end with sample queries
5. **Phase 5**: Update main entry point to use cascade graph by default

---

## Summary

This refactoring transforms the consortium from a **risk-first compliance checker** to an **ambition-first strategy engine**:

- **Before**: All agents critique user query in parallel → List of blockers → Deadlock
- **After**: Founder proposes vision → Agents critique proposal → Alchemist transmutes → "Yes, If..." resolution

The cascade architecture forces **conflict** (Founder vs Breakers), then **alchemy** (constraints → opportunities), then **resolution** (Yes-If protocol), resulting in strategic recommendations instead of bureaucratic deadlock.
