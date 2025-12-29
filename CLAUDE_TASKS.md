# Task Queue for Claude Code

Work through these in order. Test after each task.

---

## TASK 1: Implement Operator Agent ⏳

**Create `agents/operator.py`**

Mandate: Ensure strategies are executable given organizational constraints, change management capacity, and timeline realism.

Key concerns:
- Timeline realism (flag if >200% optimistic)
- Resource availability
- Change fatigue and competing initiatives
- Skill gaps and recruitment market
- Procurement cycles

Red lines:
- Timelines assuming instant skill acquisition
- Exceeding organizational change capacity
- Ignoring competing resource demands

**Also create:**
- `config/agents/operator.yaml`
- `tests/test_operator.py`

**Verify:** `pytest tests/test_operator.py -v`

---

## TASK 2: Implement Futurist Agent ⏳

**Create `agents/futurist.py`**

Mandate: Ensure strategies remain viable across multiple future scenarios. Prevent lock-in to current paradigms.

Key concerns:
- Scenario robustness (must work in >50% of plausible futures)
- Technology evolution risks
- Regulatory trend changes
- Strategic optionality

Red lines:
- Irreversible commitments without scenario testing
- Assuming static landscape
- No adaptation mechanisms

**Also create:**
- `config/agents/futurist.yaml`
- `tests/test_futurist.py`

**Verify:** `pytest tests/test_futurist.py -v`

---

## TASK 3: Implement Founder Agent (Accelerator) ⏳

**Create `agents/founder.py`**

Mandate: Maximize UPSIDE. Counter excessive caution. Push for 10x thinking.

Persona: "The Pirate" - aggressive, visionary, impatient

Counters other agents:
- Jurist says "Risk" → Founder says "Moat"
- Economist says "Cost" → Founder says "Investment"
- Operator says "Impossible" → Founder says "Necessary"

Style: Reference Blitzscaling, Network Effects, First-Mover Advantage, Category King

**Also create:**
- `config/agents/founder.yaml`
- `tests/test_founder.py`

**Verify:** `pytest tests/test_founder.py -v`

---

## TASK 4: Implement Alchemist Agent (Accelerator) ⏳

**Create `agents/alchemist.py`**

Mandate: Transform compliance costs into premium revenue. "European regulation is a luxury brand."

Core mechanic - REFRAMING:
- "Data must stay in EU" → "Swiss-Bank-Grade Privacy" (+30% premium)
- "Must use green energy" → "Zero-Carbon Compute" tier
- "AI Act conformity" → "Trustworthy AI" certification badge

Never lowers costs - raises prices to cover them.

**Also create:**
- `config/agents/alchemist.yaml`
- `tests/test_alchemist.py`

**Verify:** `pytest tests/test_alchemist.py -v`

---

## TASK 5: Update Sovereign with Proportionate Risk ⏳

**Modify `agents/sovereign.py`**

Replace blanket anti-US-cloud stance with 4-tier framework:

| Tier | Sensitivity | US Cloud Policy |
|------|-------------|-----------------|
| 1 | Low (public content) | OK with standard terms |
| 2 | Medium (PII) | OK with SCCs + DPA + EU region |
| 3 | High (trade secrets) | Requires customer-managed encryption |
| 4 | Critical (gov/defense) | EU-only infrastructure |

Add reference to EU-US Data Privacy Framework (2023).

**Verify:** `pytest tests/test_sovereign.py -v`

---

## TASK 6: Implement "Yes, If" Protocol ⏳

**Modify `src/consortium/nodes/convergence_test.py`**

Rules:
1. No naked BLOCKs (except Jurist on criminal matters)
2. BLOCKs must include conditions: "YES, IF [condition]"
3. Alchemist reframes count as bonus points
4. Founder ENDORSE boosts confidence

**Verify:** `pytest tests/test_convergence.py -v`

---

## TASK 7: Update Router and Executor ⏳

**Modify `src/consortium/nodes/router.py`**
- Trigger all agents (should be 10+)

**Modify `src/consortium/nodes/agent_executor.py`**
- Add all new agents to registry

**Verify:** 
```bash
python -c "
from src.consortium.nodes.router import router_node
result = router_node({'query': 'test'})
print(f'Agents: {len(result[\"triggered_agents\"])}')
assert len(result['triggered_agents']) >= 10
"
```

---

## TASK 8: Full Integration Test ⏳

Run complete test suite:
```bash
pytest tests/ -v --tb=short
```

Create `test_full_consortium.py` that runs all agents on a sample query.

---

## TASK 9 (Optional): Remaining Original Agents ⏳

If time permits, implement:
- `agents/ethnographer.py` - Cultural fit across EU
- `agents/technologist.py` - Cybersecurity/CISO
- `agents/consumer_voice.py` - User rights

---

## Completion Checklist

- [ ] All agents implemented and tested
- [ ] Router triggers all agents
- [ ] "Yes, If" protocol working
- [ ] Sovereign uses proportionate risk
- [ ] Full test suite passes (>90%)
- [ ] Integration test runs successfully