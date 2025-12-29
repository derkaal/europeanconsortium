# LangChain LLM Integration - Research Findings

## Research Summary

Context7 research on LangChain revealed key patterns for LLM integration. However, **LangChain does not have built-in provider failover** - we must implement it ourselves.

---

## Key Finding 1: LLM Initialization Patterns

### Pattern Discovered:
```python
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# API keys from environment variables
os.environ["ANTHROPIC_API_KEY"] = "sk-..."
os.environ["OPENAI_API_KEY"] = "sk-..."

# Initialize with parameters
model = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    temperature=0.3,
    max_tokens=4096
)
```

### Key Points:
- ✅ API keys read from environment variables automatically
- ✅ Each provider has its own class (ChatAnthropic, ChatOpenAI, etc.)
- ✅ Common parameters: `temperature`, `max_tokens`, `timeout`
- ✅ Model name passed as first parameter

---

## Key Finding 2: Message Structure

### Pattern Discovered:
```python
from langchain_core.messages import SystemMessage, HumanMessage

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="User query here")
]

response = model.invoke(messages)
# response is AIMessage with .content attribute
```

### Key Points:
- ✅ Use `SystemMessage` for system prompts
- ✅ Use `HumanMessage` for user input
- ✅ `model.invoke(messages)` returns `AIMessage`
- ✅ Access response text via `response.content`

---

## Key Finding 3: Error Handling

### Pattern Discovered:
LangChain has retry middleware for **agents**, but NOT for direct model calls:

```python
# This is for agents, not direct model.invoke()
from langchain.agents.middleware import ModelRetryMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[ModelRetryMiddleware(max_retries=3)]
)
```

### Key Points:
- ❌ **No built-in failover for model.invoke()**
- ❌ **No automatic provider switching**
- ✅ Must implement try/except ourselves
- ✅ Can catch provider-specific exceptions

---

## Key Finding 4: Provider Failover (NOT BUILT-IN)

### What We Need to Implement:
```python
providers = [
    ("anthropic", ChatAnthropic(...)),
    ("openai", ChatOpenAI(...)),
]

for provider_name, provider_client in providers:
    try:
        response = provider_client.invoke(messages)
        return response.content
    except Exception as e:
        logger.warning(f"{provider_name} failed: {e}")
        continue

raise Exception("All providers failed")
```

### Key Points:
- ❌ LangChain does NOT provide this
- ✅ We must implement manual failover loop
- ✅ Try each provider in sequence
- ✅ Log failures and continue to next

---

## Implementation Decision

Based on research, we will:

1. **Simplify LLMProviderManager** - Remove complex retry logic, use simple try/except
2. **Use environment variables** - Let LangChain read API keys automatically
3. **Implement manual failover** - Loop through providers on failure
4. **Keep it simple** - No complex middleware, just basic error handling

---

## Revised Implementation Plan

### What We CAN Deliver (Iteration 6 Scope):

✅ **Simple LLM Integration**
- Initialize ChatAnthropic, ChatOpenAI, ChatMistralAI
- Use SystemMessage + HumanMessage pattern
- Basic try/except error handling
- Manual provider failover loop

✅ **Agent Updates**
- Connect agents to LLMProviderManager
- Build prompts with memory context
- Parse LLM responses

✅ **Environment Setup**
- .env file for API keys
- python-dotenv integration
- Graceful handling of missing keys

### What We CANNOT Deliver (Future Scope):

❌ **Complex Retry Logic** - LangChain doesn't provide this for direct model calls
❌ **Sophisticated Failover** - Would require custom middleware
❌ **Memory Integration** - MemoryManager needs vector store setup (separate iteration)
❌ **Tension Resolution** - TensionOrchestrator needs more work

---

## Simplified Code Patterns

### 1. LLMProviderManager (Simplified)

```python
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os
import logging

logger = logging.getLogger(__name__)

class LLMProviderManager:
    """Simple LLM provider with manual failover."""
    
    def __init__(self):
        self.providers = []
        
        # Initialize available providers
        if os.getenv("ANTHROPIC_API_KEY"):
            self.providers.append(("anthropic", ChatAnthropic(
                model="claude-sonnet-4-20250514",
                temperature=0.3,
                max_tokens=4096
            )))
        
        if os.getenv("OPENAI_API_KEY"):
            self.providers.append(("openai", ChatOpenAI(
                model="gpt-4",
                temperature=0.3,
                max_tokens=4096
            )))
        
        if not self.providers:
            raise ValueError("No LLM providers available")
        
        logger.info(f"Initialized {len(self.providers)} providers")
    
    def invoke(self, system_prompt: str, user_message: str) -> str:
        """Invoke LLM with manual failover."""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        last_error = None
        for provider_name, client in self.providers:
            try:
                response = client.invoke(messages)
                logger.info(f"✓ {provider_name} succeeded")
                return response.content
            except Exception as e:
                logger.warning(f"✗ {provider_name} failed: {e}")
                last_error = e
                continue
        
        raise Exception(f"All providers failed. Last error: {last_error}")
```

### 2. Agent Integration

```python
class Agent(ABC):
    def __init__(self, config: Dict[str, Any]):
        # ... existing init ...
        self.provider = LLMProviderManager()
    
    def invoke(self, state: ConsortiumState) -> AgentResponse:
        """Invoke agent with LLM."""
        # Build prompt
        user_message = self._build_prompt(state)
        
        # Call LLM
        try:
            raw_response = self.provider.invoke(
                system_prompt=self.system_prompt,
                user_message=user_message
            )
        except Exception as e:
            raise AgentInvocationError(f"LLM call failed: {e}")
        
        # Parse response
        return self._parse_response(raw_response)
```

---

## Conclusion

LangChain provides excellent LLM client abstractions but **does not provide built-in failover**. We must implement it ourselves with simple try/except logic.

This is actually **better for our use case** because:
1. More control over failover behavior
2. Simpler code (no complex middleware)
3. Easier to debug
4. Matches our existing provider abstraction

**Recommendation**: Proceed with simplified implementation focusing on basic LLM integration. Save advanced features (memory, tensions) for future iterations.
