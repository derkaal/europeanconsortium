# European Strategy Consortium Multi-Agent System

A sophisticated multi-agent system for strategic decision-making following European values and regulatory frameworks.

## Overview

The European Strategy Consortium is a LangGraph-based multi-agent system designed to provide strategic recommendations for European businesses. It features 11 specialized agents that debate proposals through structured tension protocols, ensuring decisions balance sovereignty, economics, legal compliance, and other critical factors.

## Project Status

**Phase**: SPARC Refinement - Iteration 1 (Core Infrastructure) ✅ COMPLETE

**Completion**: 38% of total system (3 of 8 iterations)

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

4. **Agent Configurations**
   - [`config/agents/sovereign.yaml`](config/agents/sovereign.yaml) - Guardian of Digital Autonomy
   - [`config/agents/economist.yaml`](config/agents/economist.yaml) - Pragmatist of Sustainable Value
   - [`config/agents/jurist.yaml`](config/agents/jurist.yaml) - Master of Regulatory Compliance

5. **Comprehensive Test Suite**
   - 34 unit tests covering all core components
   - 78% code coverage
   - All tests passing ✅

## Installation

```bash
# Clone repository
git clone <repository-url>
cd european-strategy-consortium

# Install dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Set up environment variables
export ANTHROPIC_API_KEY="your-key"
export MISTRAL_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
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

## Next Steps

### Iteration 2: Memory System
- Chroma vector database integration
- Hybrid B+C memory architecture
- Case storage and retrieval
- Outcome-based weighting

### Iteration 4: Tension Protocols
- 5 tension protocol handlers
- Sovereign ↔ Economist protocol
- Eco-System ↔ Architect protocol
- Jurist ↔ Philosopher protocol
- Operator ↔ Strategy protocol
- Futurist ↔ All protocol

### Iteration 5: Supervisor & Routing
- LangGraph main orchestration graph
- Agent routing logic
- Convergence testing
- Escalation handling

### Iterations 6-7: Remaining Agents
- Architect (System Design Specialist)
- Philosopher (Ethics & Values Guardian)
- Ethnographer (Cultural Context Expert)
- Technologist (Innovation Assessor)
- Consumer Voice (User Experience Advocate)
- Futurist (Long-term Impact Analyst)
- Operator (Operational Feasibility Expert)
- Eco-System (Environmental Impact Assessor)

### Iteration 8: Historical Test Cases
- 8 comprehensive test scenarios
- End-to-end validation
- Performance benchmarking

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
