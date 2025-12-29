"""
LLM Provider Adapter for European Strategy Consortium

Multi-provider LLM access with failover, exponential backoff retry,
and conversation history preservation for multi-turn debates.

Based on ARCHITECTURE_PART2.md Section 6 and CRITICAL_FIXES.
"""

import os
import time
import random
import threading
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

from src.consortium.config import ProvidersConfig, ProviderConfig


# ==============================================================================
# EXCEPTIONS
# ==============================================================================

class ProviderError(Exception):
    """Base exception for provider errors"""
    pass


class ProviderTimeoutError(ProviderError):
    """Provider request timeout"""
    pass


class ProviderRateLimitError(ProviderError):
    """Provider rate limit exceeded"""
    pass


class ProviderAPIError(ProviderError):
    """Provider API error"""
    pass


class AllProvidersFailedError(ProviderError):
    """All configured providers failed"""
    pass


# ==============================================================================
# PROVIDER IMPLEMENTATIONS
# ==============================================================================

class LLMProvider:
    """Base class for LLM provider implementations"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.name = config.name
        self.api_key = os.getenv(config.api_key_env)
        
        if not self.api_key:
            raise ValueError(
                f"API key not found in environment: {config.api_key_env}"
            )
    
    def invoke(
        self,
        messages: List[Dict[str, str]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Invoke LLM with messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            config: Invocation config (max_tokens, temperature, etc.)
        
        Returns:
            Dict with 'response', 'latency_ms', 'token_count', 'model_used'
        
        Raises:
            ProviderTimeoutError: Request timeout
            ProviderRateLimitError: Rate limit exceeded
            ProviderAPIError: Other API errors
        """
        raise NotImplementedError("Subclasses must implement invoke()")
    
    def health_check(self) -> bool:
        """Check if provider is healthy"""
        return True


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "anthropic package not installed. "
                "Install with: pip install anthropic"
            )
    
    def invoke(
        self,
        messages: List[Dict[str, str]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke Claude API"""
        start_time = time.time()
        
        try:
            model = self.config.models.get("default", "claude-sonnet-4-20250514")
            
            response = self.client.messages.create(
                model=model,
                max_tokens=config.get("max_tokens", 4096),
                temperature=config.get("temperature", 0.7),
                messages=messages,
                timeout=config.get("timeout", self.config.timeout_seconds)
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "response": response.content[0].text,
                "latency_ms": latency_ms,
                "token_count": response.usage.input_tokens + response.usage.output_tokens,
                "model_used": model
            }
        
        except Exception as e:
            error_str = str(e).lower()
            
            if "timeout" in error_str:
                raise ProviderTimeoutError(f"Anthropic timeout: {e}")
            elif "rate" in error_str or "429" in error_str:
                raise ProviderRateLimitError(f"Anthropic rate limit: {e}")
            else:
                raise ProviderAPIError(f"Anthropic API error: {e}")


class MistralProvider(LLMProvider):
    """Mistral AI provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        try:
            from mistralai import Mistral
            self.client = Mistral(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "mistralai package not installed. "
                "Install with: pip install mistralai"
            )
    
    def invoke(
        self,
        messages: List[Dict[str, str]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke Mistral API"""
        start_time = time.time()
        
        try:
            model = self.config.models.get("default", "mistral-large-latest")
            
            response = self.client.chat.complete(
                model=model,
                messages=messages,
                max_tokens=config.get("max_tokens", 4096),
                temperature=config.get("temperature", 0.7)
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "response": response.choices[0].message.content,
                "latency_ms": latency_ms,
                "token_count": response.usage.total_tokens,
                "model_used": model
            }
        
        except Exception as e:
            error_str = str(e).lower()
            
            if "timeout" in error_str:
                raise ProviderTimeoutError(f"Mistral timeout: {e}")
            elif "rate" in error_str or "429" in error_str:
                raise ProviderRateLimitError(f"Mistral rate limit: {e}")
            else:
                raise ProviderAPIError(f"Mistral API error: {e}")


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "openai package not installed. "
                "Install with: pip install openai"
            )
    
    def invoke(
        self,
        messages: List[Dict[str, str]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke OpenAI API"""
        start_time = time.time()
        
        try:
            model = self.config.models.get("default", "gpt-4-turbo-preview")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=config.get("max_tokens", 4096),
                temperature=config.get("temperature", 0.7),
                timeout=config.get("timeout", self.config.timeout_seconds)
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "response": response.choices[0].message.content,
                "latency_ms": latency_ms,
                "token_count": response.usage.total_tokens,
                "model_used": model
            }
        
        except Exception as e:
            error_str = str(e).lower()
            
            if "timeout" in error_str:
                raise ProviderTimeoutError(f"OpenAI timeout: {e}")
            elif "rate" in error_str or "429" in error_str:
                raise ProviderRateLimitError(f"OpenAI rate limit: {e}")
            else:
                raise ProviderAPIError(f"OpenAI API error: {e}")


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model_name = self.config.models.get("default", "gemini-pro")
            self.client = genai.GenerativeModel(model_name)
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Install with: pip install google-generativeai"
            )
    
    def invoke(
        self,
        messages: List[Dict[str, str]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke Gemini API"""
        start_time = time.time()
        
        try:
            # Convert messages to Gemini format
            gemini_messages = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                gemini_messages.append({
                    "role": role,
                    "parts": [msg["content"]]
                })
            
            response = self.client.generate_content(
                gemini_messages,
                generation_config={
                    "max_output_tokens": config.get("max_tokens", 4096),
                    "temperature": config.get("temperature", 0.7)
                }
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "response": response.text,
                "latency_ms": latency_ms,
                "token_count": 0,  # Gemini doesn't provide token count easily
                "model_used": self.config.models.get("default", "gemini-pro")
            }
        
        except Exception as e:
            error_str = str(e).lower()
            
            if "timeout" in error_str:
                raise ProviderTimeoutError(f"Gemini timeout: {e}")
            elif "rate" in error_str or "429" in error_str:
                raise ProviderRateLimitError(f"Gemini rate limit: {e}")
            else:
                raise ProviderAPIError(f"Gemini API error: {e}")


# ==============================================================================
# PROVIDER ADAPTER
# ==============================================================================

class LLMProviderAdapter:
    """
    Manages multi-provider LLM access with failover and conversation history.
    
    CRITICAL: Preserves conversation history during provider failover
    to support multi-turn tension protocol debates.
    
    Thread-safe for parallel agent execution.
    """
    
    def __init__(self, providers_config: ProvidersConfig):
        """
        Initialize provider adapter.
        
        Args:
            providers_config: Validated providers configuration
        """
        self.config = providers_config
        
        # Initialize providers in priority order
        self.providers: List[Tuple[ProviderConfig, LLMProvider]] = []
        
        for provider_config in sorted(
            providers_config.providers,
            key=lambda p: p.priority
        ):
            try:
                provider = self._create_provider(provider_config)
                self.providers.append((provider_config, provider))
            except Exception as e:
                print(f"Warning: Failed to initialize provider "
                      f"{provider_config.name}: {e}")
        
        if not self.providers:
            raise ValueError("No providers successfully initialized")
        
        # Conversation history storage (thread-safe)
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        self.history_lock = threading.Lock()
    
    def _create_provider(self, config: ProviderConfig) -> LLMProvider:
        """Create provider instance based on config"""
        provider_map = {
            "anthropic": AnthropicProvider,
            "mistral": MistralProvider,
            "openai": OpenAIProvider,
            "gemini": GeminiProvider
        }
        
        provider_class = provider_map.get(config.name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {config.name}")
        
        return provider_class(config)
    
    def invoke(
        self,
        agent_id: str,
        messages: List[Dict[str, str]],
        config: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Invoke LLM with full conversation history and failover.
        
        CRITICAL: Preserves conversation history during provider failover.
        
        Args:
            agent_id: Agent identifier for history tracking
            messages: New messages to add to conversation
            config: Invocation config (max_tokens, temperature, timeout)
        
        Returns:
            Tuple of (response_text, metadata)
            metadata includes: provider, latency_ms, token_count, model_used
        
        Raises:
            AllProvidersFailedError: All providers failed
        """
        if config is None:
            config = {}
        
        # Get full conversation history for this agent
        with self.history_lock:
            history = self.conversation_history.get(agent_id, [])
            full_messages = history + messages
        
        last_exception = None
        
        # Try each provider in priority order
        for provider_config, provider in self.providers:
            # Attempt with retry and exponential backoff
            for attempt in range(provider_config.max_retries):
                try:
                    result = provider.invoke(full_messages, config)
                    
                    # Success! Update conversation history
                    with self.history_lock:
                        # Add new messages to history
                        if agent_id not in self.conversation_history:
                            self.conversation_history[agent_id] = []
                        
                        self.conversation_history[agent_id].extend(messages)
                        
                        # Add assistant response to history
                        self.conversation_history[agent_id].append({
                            "role": "assistant",
                            "content": result["response"]
                        })
                    
                    # Add provider info to metadata
                    result["provider"] = provider_config.name
                    result["attempt"] = attempt + 1
                    
                    return result["response"], result
                
                except (ProviderTimeoutError, ProviderRateLimitError,
                        ProviderAPIError) as e:
                    last_exception = e
                    
                    # Exponential backoff before retry
                    if attempt < provider_config.max_retries - 1:
                        delay = self._calculate_backoff_delay(attempt)
                        time.sleep(delay)
            
            # Provider failed after all retries, try next provider
            # Conversation history is preserved for next provider
        
        # All providers failed
        raise AllProvidersFailedError(
            f"All {len(self.providers)} providers failed. "
            f"Last error: {last_exception}"
        )
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay with jitter.
        
        Args:
            attempt: Attempt number (0-indexed)
        
        Returns:
            Delay in seconds
        """
        retry_config = self.config.retry_strategy
        
        # Exponential backoff
        delay = min(
            retry_config.base_delay_seconds * (2 ** attempt),
            retry_config.max_delay_seconds
        )
        
        # Add jitter
        if retry_config.jitter > 0:
            jitter_amount = delay * retry_config.jitter
            delay += random.uniform(-jitter_amount, jitter_amount)
        
        return max(0.1, delay)  # Minimum 0.1s delay
    
    def get_conversation_history(self, agent_id: str) -> List[Dict[str, str]]:
        """
        Get conversation history for an agent.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            List of message dicts
        """
        with self.history_lock:
            return self.conversation_history.get(agent_id, []).copy()
    
    def clear_conversation_history(self, agent_id: Optional[str] = None):
        """
        Clear conversation history.
        
        Args:
            agent_id: Agent to clear history for, or None to clear all
        """
        with self.history_lock:
            if agent_id is None:
                self.conversation_history.clear()
            elif agent_id in self.conversation_history:
                del self.conversation_history[agent_id]
    
    def get_provider_health(self) -> Dict[str, bool]:
        """
        Check health of all providers.
        
        Returns:
            Dict mapping provider name to health status
        """
        health = {}
        for provider_config, provider in self.providers:
            try:
                health[provider_config.name] = provider.health_check()
            except Exception:
                health[provider_config.name] = False
        
        return health


# ==============================================================================
# GLOBAL INSTANCE
# ==============================================================================

_provider_adapter: Optional[LLMProviderAdapter] = None


def get_provider_adapter(
    providers_config: Optional[ProvidersConfig] = None
) -> LLMProviderAdapter:
    """
    Get global LLMProviderAdapter instance (singleton pattern).
    
    Args:
        providers_config: Providers configuration (required on first call)
    
    Returns:
        LLMProviderAdapter instance
    """
    global _provider_adapter
    
    if _provider_adapter is None:
        if providers_config is None:
            raise ValueError(
                "providers_config required on first call to get_provider_adapter"
            )
        _provider_adapter = LLMProviderAdapter(providers_config)
    
    return _provider_adapter
