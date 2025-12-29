# European Strategy Consortium - Claude Code Instructions

## Project Status
- **Phase**: SPARC Phase R (Refinement) - Iteration 10
- **Completed**: 6 core agents (Sovereign, Economist, Jurist, Architect, Eco-System, Philosopher)
- **Test Status**: 94% pass rate (76 tests)

## What's Missing (Priority Order)

### Priority 1: Remaining Agents from Original Spec
These agents are in the original specification but NOT yet implemented:

| Agent | File to Create | Role |
|-------|----------------|------|
| **Operator** | `agents/operator.py` | Implementation realism, timeline feasibility |
| **Futurist** | `agents/futurist.py` | Strategic foresight, scenario robustness |
| **Ethnographer** | `agents/ethnographer.py` | Cultural fit across EU member states |
| **Technologist** | `agents/technologist.py` | Cybersecurity, SecOps (CISO perspective) |
| **Consumer Voice** | `agents/consumer_voice.py` | User rights, accessibility, dark patterns |

### Priority 2: Accelerator Agents (NEW - for solution-seeking balance)
These counter excessive caution from "braker" agents:

| Agent | File to Create | Role |
|-------|----------------|------|
| **Founder** | `agents/founder.py` | Ambition accelerator, 10x thinking, "The Pirate" |
| **Alchemist** | `agents/alchemist.py` | Transforms constraints into premium features |

### Priority 3: Governance Updates
1. **Update Sovereign** (`agents/sovereign.py`): Change to proportionate 4-tier risk framework (not blanket anti-US-cloud)
2. **"Yes, If" Protocol** (`src/consortium/nodes/convergence_test.py`): Ban naked BLOCKs, require conditions
3. **Update Router** (`src/consortium/nodes/router.py`): Trigger ALL agents (should be 11-13 total)
4. **Update Agent Executor** (`src/consortium/nodes/agent_executor.py`): Include all new agents

### Priority 4: SPARC Phase C (Completion)
1. Run full integration test with all agents
2. Test historical cases
3. Validate convergence rates
4. Update documentation

## Development Pattern

All agents follow this pattern (see `agents/base.py`):
```python
from agents.base import Agent

class NewAgent(Agent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.system_prompt = NEW_AGENT_SYSTEM_PROMPT
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._build_prompt(state)
        response_text = self._invoke_llm(prompt)
        return self._parse_response(response_text)
```

Each agent also needs:
- Config file: `config/agents/[agent_name].yaml`
- Tests: `tests/test_[agent_name].py`

## Commands
```bash
# Run all tests
pytest tests/ -v

# Quick graph test
python -c "from src.consortium.graph import create_consortium_graph; print('OK')"

# Run 6-agent demo
python test_6_agents.py

# Test specific agent
pytest tests/test_[agent_name].py -v
```

## Key Reference Files
- `docs/SOLUTION_BRIEF.md` - Full system architecture
- `docs/Specification_Gap_Resolutions.md` - Approved design decisions  
- Original spec: See agent definitions for Operator, Futurist, Ethnographer, Technologist, Consumer Voice