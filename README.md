# European Strategy Consortium Multi-Agent System

A sophisticated multi-agent system for strategic decision-making following European values and regulatory frameworks.

## Overview

The European Strategy Consortium is a LangGraph-based multi-agent system designed to provide strategic recommendations for European businesses. It features **9 specialized agents + 1 meta-agent (CLA)** that debate proposals through structured tension protocols, ensuring decisions balance sovereignty, economics, legal compliance, cultural ergonomics, operational security, consumer protection, and other critical factors.

## Project Status

**Phase**: Phase 2 Complete - Production Ready ✅

**Agents**: 9 core agents + CLA (Conservative Legalese Advocate)
- ✅ Big Three: Sovereign, Economist, Jurist
- ✅ Tier 1: Architect, Eco-System, Philosopher
- ✅ Tier 4: Ethnographer, Technologist, Consumer Voice
- ✅ Meta: CLA (zombie detection)

## Architecture

Built following SPARC methodology:
- ✅ **Specification** (Phase S) - Complete
- ✅ **Pseudocode** (Phase P) - Complete  
- ✅ **Architecture** (Phase A) - Complete
- ⏳ **Refinement** (Phase R) - In Progress (Iteration 1 complete)

### Iteration 1: Core Infrastructure (COMPLETE)

This iteration implements the foundational components:

1. **State Schema** ([`src/consortium/state.py`](src/consortium/state.py))
   - Complete TypedDict definitions for LangGraph state management
   - Multi-tension support with priority queue
   - Conversation history tracking
   - Comprehensive audit trail

2. **Configuration Loader** ([`src/consortium/config.py`](src/consortium/config.py))
   - YAML-based configuration with Pydantic validation
   - Hot-reload support for agent configs
   - Tension protocol configuration
   - System and provider configuration

3. **LLM Provider Adapter** ([`src/consortium/providers.py`](src/consortium/providers.py))
   - Multi-provider support (Anthropic, Mistral, OpenAI, Gemini)
   - Automatic failover with exponential backoff
   - **Conversation history preservation during failover** (critical for multi-turn debates)
   - Thread-safe for parallel agent execution

4. **Agent Configurations** (9 agents + 1 meta-agent)
   - **Big Three**:
     - [`sovereign.yaml`](config/agents/sovereign.yaml) - Guardian of Digital Sovereignty
     - [`economist.yaml`](config/agents/economist.yaml) - Pragmatist of Sustainable Value
     - [`jurist.yaml`](config/agents/jurist.yaml) - Master of Regulatory Compliance
   - **Tier 1**:
     - [`architect.yaml`](config/agents/architect.yaml) - Systems Design Specialist
     - [`ecosystem.yaml`](config/agents/ecosystem.yaml) - Environmental Sustainability Guardian
     - [`philosopher.yaml`](config/agents/philosopher.yaml) - Ethics & Values Advocate
   - **Tier 4**:
     - [`ethnographer.yaml`](config/agents/ethnographer.yaml) - Cultural Ergonomics Specialist
     - [`technologist.yaml`](config/agents/technologist.yaml) - Operational Security Expert (CISO)
     - [`consumer_voice.yaml`](config/agents/consumer_voice.yaml) - Consumer Protection & Accessibility Champion
   - **Meta**:
     - [`cla.yaml`](config/agents/cla.yaml) - Conservative Legalese Advocate (zombie detection)

5. **Comprehensive Test Suite**
   - All agent tests passing ✅
   - Convergence validation tests ✅
   - Multi-LLM failover tests ✅
   - Performance benchmarks ✅

## Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd europeanconsortium

# Install dependencies
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Configuration

Required: At least one LLM provider API key
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here  # Recommended (Claude)
# OR
OPENAI_API_KEY=sk-proj-your-key-here    # Alternative
```

See [`.env.example`](.env.example) for full configuration options.

### Running the Streamlit Demo

```bash
streamlit run app/streamlit_app.py
```

Then navigate to http://localhost:8501 to interact with the consortium.

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suite
python -m pytest tests/test_tier4_agents.py -v
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/consortium --cov-report=term-missing

# Run specific test file
pytest tests/test_state.py -v
```

## Project Structure

```
european-strategy-consortium/
├── src/
│   └── consortium/
│       ├── __init__.py
│       ├── state.py           # State schema (202 lines, 99% coverage)
│       ├── config.py          # Configuration loader (198 lines, 91% coverage)
│       ├── providers.py       # LLM provider adapter (198 lines, 42% coverage*)
│       └── agents/
│           ├── __init__.py
│           ├── base.py        # Abstract Agent base class
│           ├── sovereign.py   # Guardian of Digital Autonomy
│           ├── economist.py   # Pragmatist of Sustainable Value
│           └── jurist.py      # Master of Regulatory Compliance
├── config/
│   ├── agents/
│   │   ├── sovereign.yaml
│   │   ├── economist.yaml
│   │   └── jurist.yaml
│   └── providers.yaml
├── tests/
│   ├── __init__.py
│   ├── test_state.py         # 9 tests
│   ├── test_config.py        # 12 tests
│   └── test_providers.py     # 13 tests
├── docs/                     # Architecture documentation
├── pyproject.toml
└── README.md
```

*Note: Provider adapter coverage is 42% because actual LLM provider implementations (Anthropic, Mistral, OpenAI, Gemini) are tested with mocks. Real provider integration will be tested in integration tests.

## Key Features

### Multi-Tension Support
The system can handle multiple simultaneous tensions (e.g., Sovereign ↔ Economist AND Eco-System ↔ Architect) with:
- Priority queue for resolution order
- Dependency tracking between tensions
- Parallel tension detection

### Conversation History Preservation
Critical feature for multi-turn debates:
- Full conversation history maintained per agent
- History preserved during provider failover
- Thread-safe for parallel agent execution

### Provider Failover
Robust multi-provider support:
- Primary: Anthropic (Claude Sonnet 4)
- Secondary: Mistral (European sovereignty preference)
- Tertiary: OpenAI (GPT-4)
- Quaternary: Gemini
- Exponential backoff retry (2 attempts per provider)
- Automatic failover on timeout/rate limit/API errors

## The Agents

### Big Three (Foundational)
1. **Sovereign** - Ensures European digital sovereignty and GDPR compliance
2. **Economist** - Ensures financial viability and sustainable value creation
3. **Jurist** - Ensures legal compliance and manages regulatory risk

### Tier 1 (Technical & Values)
4. **Architect** - Ensures technical feasibility and sound systems design
5. **Eco-System** - Ensures environmental sustainability and planetary boundaries
6. **Philosopher** - Ensures ethical alignment and human dignity

### Tier 4 (Specialized)
7. **Ethnographer** - Ensures cultural ergonomics across Europe's diverse contexts
8. **Technologist** - Ensures operational security (CISO perspective)
9. **Consumer Voice** - Protects end-users, champions accessibility

### Meta-Agent
10. **CLA** (Conservative Legalese Advocate) - Prevents "zombie" programs that persist indefinitely without achieving goals

For detailed agent documentation, see [`docs/AGENTS.md`](docs/AGENTS.md).

## The "Yes, If" Protocol

Agents don't simply approve or reject proposals—they propose **conditional acceptance**:

- **Sovereign**: "Yes, if we use EU cloud providers or encrypt with customer-managed keys"
- **Economist**: "Yes, if we start with fine-tuned model (€2M) instead of custom LLM (€14M)"
- **Ethnographer**: "Yes, if we adapt rollout for German works councils (6-month consultation)"
- **Technologist**: "Yes, if we use HashiCorp Vault for secrets, not environment variables"

The consortium **converges** on a recommendation that satisfies all agents' conditions, or **escalates** to human decision-makers when consensus cannot be reached.

**Target Metrics**:
- Autonomous convergence rate: >70%
- Human escalation rate: <30%
- Average iterations to convergence: <5

## Example Use Cases

- **Cloud Strategy**: "Should we use AWS for our German automotive R&D data?"
  - Tensions: Sovereign (data sovereignty) ↔ Economist (cloud costs)
  - Resolution: AWS EU regions + encryption + customer-managed keys + Trust Premium positioning

- **AI Hiring System**: "Deploy AI for CV screening across EU offices?"
  - Tensions: Jurist (EU AI Act compliance) ↔ Philosopher (bias/fairness) ↔ Ethnographer (cultural hiring norms)
  - Resolution: Human-in-loop design + bias testing + works council approval + candidate right to explanation

- **Innovation Fund**: "Create €50B EU cloud/AI fund?"
  - Tensions: CLA (zombie risk) ↔ Sovereign (strategic autonomy) ↔ Economist (ROI)
  - Resolution: 10-year sunset clause + performance milestones + market share targets + independent audit

## Documentation

Comprehensive architecture documentation available in [`docs/`](docs/):
- [`ARCHITECTURE_PART1.md`](docs/ARCHITECTURE_PART1.md) - State schema, graph topology, interfaces
- [`ARCHITECTURE_PART2.md`](docs/ARCHITECTURE_PART2.md) - Memory & knowledge strategy
- [`ARCHITECTURE_PART3.md`](docs/ARCHITECTURE_PART3.md) - Configuration, testing, observability
- [`ARCHITECTURE_CRITICAL_FIXES.md`](docs/ARCHITECTURE_CRITICAL_FIXES.md) - Multi-tension support
- [`PSEUDOCODE.md`](docs/PSEUDOCODE.md) - Algorithmic logic
- [`ITERATION_3_SUMMARY.md`](docs/ITERATION_3_SUMMARY.md) - Big Three agents implementation

## License

MIT

## Contributing

This project follows SPARC methodology. See architecture documentation for contribution guidelines.
