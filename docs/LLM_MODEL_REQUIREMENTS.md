# LLM Model Requirements - European Strategy Consortium

## Overview

The European Strategy Consortium uses a **tiered LLM strategy** to optimize costs while maintaining quality. The system supports multiple providers with automatic failover.

**Latest Update**: December 30, 2024 - Added tiered LLM cost optimization and Feature Subsidy agents (Founder & Alchemist)

---

## 🎯 Tiered Model Strategy (NEW)

The system now implements a sophisticated tiered approach based on task complexity:

### Tier Breakdown

| Tier | Purpose | Primary Model | Cost Strategy | Use Cases |
|------|---------|---------------|---------------|-----------|
| **Reasoning** | Complex analysis, adversarial debate | Mistral Large (EU-first) | Premium quality | All 11 agents |
| **Standard** | Synthesis, formatting | Gemini Flash (cheapest) | Cost optimization | Synthesizer, CLA Gate, Architect Revision |
| **Fast** | Classification, routing | Gemini Flash (cheapest) | Maximum speed | Router, Convergence Test |
| **Embedding** | Vector embeddings | Google text-embedding-004 | Minimal cost | Memory operations |

---

## 📋 Required LLM Models by Provider

### 1. **Mistral AI** (EU Sovereignty - PRIMARY for Reasoning)

**Priority**: Primary for reasoning tasks (EU-first strategy)

#### Models Required:
- **`mistral-large-latest`**
  - **Purpose**: Primary reasoning model for all 11 agents
  - **Usage**: Complex agent analysis, adversarial debate, strategic reasoning
  - **Configuration**: 
    - Max tokens: 4096
    - Temperature: 0.7
    - Cost: €2.00/1M input tokens, €6.00/1M output tokens
  - **Agents using this**: Sovereign, Intelligence Sovereign, Economist, Jurist, Architect, Ecosystem, Philosopher, Ethnographer, Technologist, Consumer Voice, Founder, Alchemist

- **`mistral-small-latest`**
  - **Purpose**: Fallback for standard/fast tasks
  - **Usage**: Synthesis, routing (fallback #2)
  - **Configuration**:
    - Max tokens: 1024-4096
    - Temperature: 0.1-0.3

- **`mistral-embed`**
  - **Purpose**: Fallback embedding model
  - **Usage**: Vector embeddings for memory operations (fallback #2)
  - **Configuration**:
    - Dimensions: 1024

**API Key Required**: `MISTRAL_API_KEY`

**Why Mistral First?**
- European sovereignty preference
- GDPR-native infrastructure
- Competitive pricing for reasoning tasks
- Strategic alignment with EU digital autonomy

---

### 2. **Anthropic Claude** (Fallback #1 for Reasoning)

**Priority**: Secondary (fallback for reasoning tasks)

#### Models Required:
- **`claude-sonnet-4-20250514`**
  - **Purpose**: Fallback reasoning model
  - **Usage**: Complex analysis when Mistral unavailable
  - **Configuration**:
    - Max tokens: 4096
    - Temperature: 0.7
    - Timeout: 60 seconds

- **`claude-3-5-sonnet-20241022`**
  - **Purpose**: Alternative reasoning model
  - **Usage**: Agent analysis, debate facilitation
  - **Configuration**:
    - Max tokens: 4096
    - Temperature: 0.7

**API Key Required**: `ANTHROPIC_API_KEY`

**Note**: While Anthropic is listed as fallback in the tiered system, it's still the recommended provider in the legacy [`providers.yaml`](../config/providers.yaml) configuration.

---

### 3. **Google Gemini** (PRIMARY for Standard/Fast/Embedding)

**Priority**: Primary for cost-optimized tasks

#### Models Required:
- **`gemini-1.5-flash`**
  - **Purpose**: Primary model for standard and fast tasks
  - **Usage**: 
    - Synthesis and formatting (standard tier)
    - Classification and routing (fast tier)
  - **Configuration**:
    - Max tokens: 1024-4096
    - Temperature: 0.1-0.3
    - Cost: $0.075/1M input tokens, $0.30/1M output tokens
  - **Tasks**: Synthesizer, CLA Gate, Architect Revision, Router, Convergence Test

- **`text-embedding-004`**
  - **Purpose**: Primary embedding model
  - **Usage**: Vector embeddings for ChromaDB memory operations
  - **Configuration**:
    - Dimensions: 768
    - Cost: $0.00625/1M tokens
  - **Tasks**: Memory store, memory retrieve, knowledge retrieval

- **`gemini-pro`** (Legacy)
  - **Purpose**: Fallback in legacy provider configuration
  - **Usage**: General-purpose tasks
  - **Configuration**:
    - Max tokens: 4096
    - Temperature: 0.3

**API Key Required**: `GOOGLE_API_KEY`

**Why Gemini for Standard/Fast?**
- Lowest cost per token
- Fast response times
- Sufficient quality for non-reasoning tasks
- Excellent for embeddings

---

### 4. **OpenAI** (Fallback #1 for Standard/Fast, Fallback #2 for Reasoning)

**Priority**: Tertiary (fallback across all tiers)

#### Models Required:
- **`gpt-4o`**
  - **Purpose**: Fallback reasoning model
  - **Usage**: Complex analysis (fallback #2 after Claude)
  - **Configuration**:
    - Max tokens: 4096
    - Temperature: 0.7

- **`gpt-4o-mini`**
  - **Purpose**: Fallback for standard/fast tasks
  - **Usage**: Synthesis, routing (fallback #1 after Gemini)
  - **Configuration**:
    - Max tokens: 1024-4096
    - Temperature: 0.1-0.3

- **`gpt-4-turbo-preview`** (Legacy)
  - **Purpose**: Legacy fallback in provider configuration
  - **Usage**: General-purpose tasks
  - **Configuration**:
    - Max tokens: 4096
    - Temperature: 0.3

- **`text-embedding-3-small`**
  - **Purpose**: Fallback embedding model
  - **Usage**: Vector embeddings (fallback #1 after Google)
  - **Configuration**:
    - Dimensions: 1536

**API Key Required**: `OPENAI_API_KEY`

---

## 🔑 API Keys Summary

### Required (At Least ONE of These)
```bash
# Primary recommendation for tiered system
MISTRAL_API_KEY=your-mistral-key-here
GOOGLE_API_KEY=your-gemini-key-here

# OR legacy single-provider approach
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Recommended (For Full Failover)
```bash
# All four providers for maximum reliability
MISTRAL_API_KEY=your-mistral-key-here
GOOGLE_API_KEY=your-gemini-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-proj-your-key-here
```

### Optional (For Embeddings)
```bash
# If using OpenAI embeddings instead of Google
OPENAI_EMBEDDING_KEY=sk-your-openai-key-here
```

---

## ⚙️ Configuration Files

### 1. Tiered LLM Configuration
**File**: [`config/model_tiers.yaml`](../config/model_tiers.yaml)

Defines the tiered strategy with:
- Model tier definitions (reasoning, standard, fast, embedding)
- Primary and fallback models per tier
- Task routing (which tasks use which tier)
- Cost tracking settings

**Key Settings**:
```yaml
model_tiers:
  reasoning:
    primary: mistral/mistral-large-latest
    fallback_1: anthropic/claude-3-5-sonnet-20241022
    fallback_2: openai/gpt-4o
  
  standard:
    primary: google/gemini-1.5-flash
    fallback_1: openai/gpt-4o-mini
    fallback_2: mistral/mistral-small-latest
  
  fast:
    primary: google/gemini-1.5-flash
    fallback_1: openai/gpt-4o-mini
    fallback_2: mistral/mistral-small-latest
  
  embedding:
    primary: google/text-embedding-004
    fallback_1: openai/text-embedding-3-small
    fallback_2: mistral/mistral-embed
```

### 2. Legacy Provider Configuration
**File**: [`config/providers.yaml`](../config/providers.yaml)

Defines provider priority for legacy single-provider approach:
1. Anthropic (Priority 1)
2. Mistral (Priority 2)
3. OpenAI (Priority 3)
4. Gemini (Priority 4)

### 3. Environment Variables
**File**: [`.env.example`](../.env.example)

Template for all required environment variables.

---

## 🏗️ System Architecture

### Two LLM Provider Systems

The system now supports **two parallel LLM provider implementations**:

#### 1. **Tiered LLM Provider** (NEW - Recommended)
**File**: [`src/consortium/tiered_llm_provider.py`](../src/consortium/tiered_llm_provider.py)

- Cost-optimized multi-model strategy
- Task-based tier routing
- Built-in cost tracking
- EU-first for reasoning, cheapest-first for other tasks

**Usage**:
```python
from consortium.tiered_llm_provider import TieredLLMProvider

provider = TieredLLMProvider()
response = provider.invoke(
    task_name="agent_sovereign",  # Routes to reasoning tier
    messages=[...]
)
```

#### 2. **Legacy LLM Provider** (Original)
**File**: [`src/consortium/llm_provider.py`](../src/consortium/llm_provider.py)

- Simple failover with priority order
- Single model per provider
- Manual retry logic
- Conversation history preservation

**Usage**:
```python
from consortium.llm_provider import LLMProviderManager

provider = LLMProviderManager()
response = provider.invoke(
    system_prompt="...",
    user_message="...",
    conversation_history=[...]
)
```

---

## 📊 Cost Optimization Strategy

### Estimated Costs per Query

Based on typical token usage:

| Tier | Tokens In | Tokens Out | Cost per Call | Use Cases |
|------|-----------|------------|---------------|-----------|
| **Reasoning** | 2000 | 1000 | ~$0.010 | Agent analysis (11 agents) |
| **Standard** | 1500 | 800 | ~$0.0003 | Synthesis (3 tasks) |
| **Fast** | 500 | 200 | ~$0.0001 | Routing (2 tasks) |
| **Embedding** | 500 | 0 | ~$0.000003 | Memory ops (3 tasks) |

### Cost Tracking

The tiered system includes built-in cost tracking:

```yaml
cost_tracking:
  enabled: true
  log_every_call: true
  alert_threshold_per_query: 0.50  # Alert if single query > $0.50
  daily_budget: 100.00  # Daily budget in USD
```

**Access cost summary**:
```python
provider = TieredLLMProvider()
# ... run queries ...
summary = provider.cost_tracker.summary()
print(f"Total cost: ${summary['total_cost_usd']:.2f}")
```

---

## 🤖 Agent-to-Model Mapping

### Reasoning Tier (Mistral Large Primary)

All 11 agents use the reasoning tier:

1. **Sovereign** - Guardian of Digital Sovereignty
2. **Intelligence Sovereign** - Meta-strategic oversight
3. **Economist** - Pragmatist of Sustainable Value
4. **Jurist** - Master of Regulatory Compliance
5. **Architect** - Systems Design Specialist
6. **Ecosystem** - Environmental Sustainability Guardian
7. **Philosopher** - Ethics & Values Advocate
8. **Ethnographer** - Cultural Ergonomics Specialist
9. **Technologist** - Operational Security Expert (CISO)
10. **Consumer Voice** - Consumer Protection Champion
11. **Founder** - Feature Hunter & Regulatory Arbitrage (NEW)
12. **Alchemist** - Regulation-to-Value Converter (NEW)

### Standard Tier (Gemini Flash Primary)

System tasks requiring synthesis:

- **Synthesizer** - Combines agent outputs into coherent recommendations
- **CLA Gate** - Conservative Legalese Advocate zombie detection
- **Architect Revision** - Technical feasibility review

### Fast Tier (Gemini Flash Primary)

System tasks requiring speed:

- **Router** - Determines which agents to invoke
- **Convergence Test** - Checks if consensus reached

### Embedding Tier (Google Embedding Primary)

Memory operations:

- **Memory Store** - Store case outcomes in ChromaDB
- **Memory Retrieve** - Retrieve similar past cases
- **Knowledge Retrieval** - RAG for agent knowledge

---

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```bash
# Core LangChain
pip install langchain-core

# Provider packages (install all for full failover)
pip install langchain-anthropic      # Claude
pip install langchain-mistralai      # Mistral
pip install langchain-openai         # OpenAI
pip install langchain-google-genai   # Gemini

# Or install all at once
pip install -e .
```

### Step 2: Configure API Keys

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

**Minimum configuration** (tiered system):
```bash
MISTRAL_API_KEY=your-mistral-key-here
GOOGLE_API_KEY=your-gemini-key-here
```

**Recommended configuration** (full failover):
```bash
MISTRAL_API_KEY=your-mistral-key-here
GOOGLE_API_KEY=your-gemini-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-proj-your-key-here
```

### Step 3: Choose Provider System

**Option A: Tiered System (Recommended)**
```python
from consortium.tiered_llm_provider import TieredLLMProvider

provider = TieredLLMProvider()
```

**Option B: Legacy System**
```python
from consortium.llm_provider import LLMProviderManager

provider = LLMProviderManager()
```

### Step 4: Verify Setup

```bash
# Run provider tests
python -m pytest tests/test_providers.py -v

# Run tiered LLM tests
python -m pytest tests/test_tiered_llm.py -v
```

---

## 🔄 Failover Behavior

### Reasoning Tier Failover Chain
1. **Mistral Large** (EU-first) → 
2. **Claude Sonnet 4** (quality fallback) → 
3. **GPT-4o** (final fallback) → 
4. **Error** (all providers failed)

### Standard/Fast Tier Failover Chain
1. **Gemini Flash** (cheapest) → 
2. **GPT-4o Mini** (quality fallback) → 
3. **Mistral Small** (final fallback) → 
4. **Error** (all providers failed)

### Embedding Tier Failover Chain
1. **Google text-embedding-004** (cheapest) → 
2. **OpenAI text-embedding-3-small** (quality fallback) → 
3. **Mistral Embed** (final fallback) → 
4. **Error** (all providers failed)

### Retry Strategy

```yaml
retry_strategy:
  base_delay_seconds: 1.0
  exponential_backoff: true  # 1s, 2s, 4s, ...
  max_delay_seconds: 10.0
  jitter: 0.1  # ±10% random jitter
  max_retries: 2  # Per provider
```

---

## 📈 Performance Considerations

### Response Times (Typical)

| Tier | Model | Avg Response Time | Use Case |
|------|-------|-------------------|----------|
| Reasoning | Mistral Large | 3-8 seconds | Complex agent analysis |
| Reasoning | Claude Sonnet 4 | 2-6 seconds | Fallback reasoning |
| Standard | Gemini Flash | 1-3 seconds | Synthesis |
| Fast | Gemini Flash | 0.5-2 seconds | Routing |
| Embedding | Google Embedding | 0.2-1 second | Memory ops |

### Throughput

- **Parallel agent execution**: Up to 11 agents simultaneously
- **Rate limiting**: Handled by provider SDKs
- **Timeout**: 30-60 seconds per call (configurable)

---

## 🛡️ Security & Compliance

### API Key Management

- **Never commit API keys** to version control
- Use `.env` file (gitignored)
- Rotate keys regularly
- Use separate keys for dev/staging/production

### Data Residency

The tiered system prioritizes EU providers:

- **Mistral AI**: EU-based (Paris, France)
- **Anthropic**: US-based (but GDPR-compliant)
- **OpenAI**: US-based (GDPR-compliant)
- **Google**: Global (GDPR-compliant)

**Configuration**:
```bash
# In .env
DATA_RESIDENCY=eu-only  # Prefer EU providers
# OR
DATA_RESIDENCY=eu-preferred  # EU first, global fallback
# OR
DATA_RESIDENCY=global  # No preference
```

---

## 🐛 Troubleshooting

### Issue: "No providers available"

**Cause**: No API keys configured or all providers failed initialization

**Solution**:
```bash
# Check .env file exists
ls -la .env

# Verify API keys are set
grep API_KEY .env

# Test provider initialization
python -c "from consortium.tiered_llm_provider import TieredLLMProvider; p = TieredLLMProvider(); print(p.available_providers)"
```

### Issue: "Rate limit exceeded"

**Cause**: Too many requests to provider

**Solution**:
- System automatically retries with exponential backoff
- Falls back to next provider in chain
- Consider upgrading API tier with provider

### Issue: "High costs"

**Cause**: Using reasoning tier for all tasks

**Solution**:
- Verify task routing in [`config/model_tiers.yaml`](../config/model_tiers.yaml)
- Check cost tracking logs
- Consider adjusting `daily_budget` threshold

### Issue: "Slow responses"

**Cause**: Using premium models for simple tasks

**Solution**:
- Verify tasks are routed to correct tier
- Use fast tier for classification/routing
- Consider increasing timeout for reasoning tasks

---

## 📚 Additional Resources

### Documentation
- [Architecture Overview](ARCHITECTURE_INTEGRATED.md)
- [Agent Documentation](AGENTS.md)
- [LangChain Research Findings](LANGCHAIN_RESEARCH_FINDINGS.md)
- [Iteration 5 Summary](ITERATION_5_COMPLETE.md)

### Configuration Files
- [Model Tiers](../config/model_tiers.yaml)
- [Providers](../config/providers.yaml)
- [System Config](../config/system.yaml)
- [Environment Template](../.env.example)

### Source Code
- [Tiered LLM Provider](../src/consortium/tiered_llm_provider.py)
- [Legacy LLM Provider](../src/consortium/llm_provider.py)
- [Provider Adapter](../src/consortium/providers.py)

### Tests
- [Tiered LLM Tests](../tests/test_tiered_llm.py)
- [Provider Tests](../tests/test_providers.py)
- [LLM Failover Tests](../tests/test_llm_failover.py)

---

## 📝 Summary Checklist

### Minimum Setup (Single Provider)
- [ ] Install `langchain-core`
- [ ] Install at least one provider package (`langchain-anthropic` OR `langchain-mistralai`)
- [ ] Set one API key in `.env`
- [ ] Run tests to verify

### Recommended Setup (Tiered System)
- [ ] Install `langchain-core`
- [ ] Install `langchain-mistralai` (reasoning)
- [ ] Install `langchain-google-genai` (standard/fast/embedding)
- [ ] Set `MISTRAL_API_KEY` in `.env`
- [ ] Set `GOOGLE_API_KEY` in `.env`
- [ ] Run tiered LLM tests

### Production Setup (Full Failover)
- [ ] Install all provider packages
- [ ] Set all four API keys in `.env`
- [ ] Configure cost tracking
- [ ] Set up monitoring/alerting
- [ ] Test failover behavior
- [ ] Review data residency requirements

---

**Last Updated**: December 30, 2024  
**System Version**: Phase 2 Complete + Tiered LLM Optimization  
**Agents**: 11 (9 core + CLA + Founder + Alchemist)
