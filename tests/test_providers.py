"""
Unit tests for LLM provider adapter
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.consortium.providers import (
    LLMProviderAdapter,
    ProviderTimeoutError,
    ProviderRateLimitError,
    ProviderAPIError,
    AllProvidersFailedError,
    LLMProvider
)
from src.consortium.config import (
    ProvidersConfig,
    ProviderConfig,
    RetryStrategy
)


class MockProvider(LLMProvider):
    """Mock provider for testing"""
    
    def __init__(self, config: ProviderConfig, should_fail: bool = False):
        self.config = config
        self.name = config.name
        self.should_fail = should_fail
        self.invocation_count = 0
        self.api_key = "mock_key"
    
    def invoke(self, messages, config):
        """Mock invoke"""
        self.invocation_count += 1
        
        if self.should_fail:
            raise ProviderTimeoutError("Mock timeout")
        
        return {
            "response": f"Mock response from {self.name}",
            "latency_ms": 100.0,
            "token_count": 50,
            "model_used": "mock-model"
        }
    
    def health_check(self):
        """Mock health check"""
        return not self.should_fail


class TestLLMProviderAdapter:
    """Test LLMProviderAdapter class"""
    
    @pytest.fixture
    def mock_providers_config(self):
        """Create mock providers configuration"""
        return ProvidersConfig(
            providers=[
                ProviderConfig(
                    name="mock_primary",
                    priority=1,
                    api_key_env="MOCK_KEY_1",
                    models={"default": "mock-model-1"},
                    timeout_seconds=30,
                    max_retries=2
                ),
                ProviderConfig(
                    name="mock_secondary",
                    priority=2,
                    api_key_env="MOCK_KEY_2",
                    models={"default": "mock-model-2"},
                    timeout_seconds=30,
                    max_retries=2
                )
            ],
            retry_strategy=RetryStrategy(
                base_delay_seconds=0.1,  # Fast for testing
                exponential_backoff=True,
                max_delay_seconds=1.0,
                jitter=0.0  # No jitter for predictable tests
            )
        )
    
    @pytest.fixture
    def adapter_with_mocks(self, mock_providers_config):
        """Create adapter with mock providers"""
        adapter = LLMProviderAdapter.__new__(LLMProviderAdapter)
        adapter.config = mock_providers_config
        adapter.conversation_history = {}
        
        import threading
        adapter.history_lock = threading.Lock()
        
        # Create mock providers
        mock_primary = MockProvider(
            mock_providers_config.providers[0],
            should_fail=False
        )
        mock_secondary = MockProvider(
            mock_providers_config.providers[1],
            should_fail=False
        )
        
        adapter.providers = [
            (mock_providers_config.providers[0], mock_primary),
            (mock_providers_config.providers[1], mock_secondary)
        ]
        
        return adapter, mock_primary, mock_secondary
    
    def test_invoke_success(self, adapter_with_mocks):
        """Test successful invocation"""
        adapter, mock_primary, mock_secondary = adapter_with_mocks
        
        messages = [{"role": "user", "content": "Test message"}]
        
        response, metadata = adapter.invoke("test_agent", messages)
        
        assert response == "Mock response from mock_primary"
        assert metadata["provider"] == "mock_primary"
        assert metadata["latency_ms"] == 100.0
        assert mock_primary.invocation_count == 1
        assert mock_secondary.invocation_count == 0
    
    def test_conversation_history_preservation(self, adapter_with_mocks):
        """Test conversation history is preserved"""
        adapter, _, _ = adapter_with_mocks
        
        # First message
        messages1 = [{"role": "user", "content": "First message"}]
        response1, _ = adapter.invoke("test_agent", messages1)
        
        # Check history
        history = adapter.get_conversation_history("test_agent")
        assert len(history) == 2  # User message + assistant response
        assert history[0]["content"] == "First message"
        assert history[1]["role"] == "assistant"
        
        # Second message
        messages2 = [{"role": "user", "content": "Second message"}]
        response2, _ = adapter.invoke("test_agent", messages2)
        
        # Check history includes both exchanges
        history = adapter.get_conversation_history("test_agent")
        assert len(history) == 4  # 2 user messages + 2 assistant responses
    
    def test_failover_on_provider_failure(self, adapter_with_mocks):
        """Test failover to secondary provider on primary failure"""
        adapter, mock_primary, mock_secondary = adapter_with_mocks
        
        # Make primary fail
        mock_primary.should_fail = True
        
        messages = [{"role": "user", "content": "Test message"}]
        
        response, metadata = adapter.invoke("test_agent", messages)
        
        # Should use secondary provider
        assert response == "Mock response from mock_secondary"
        assert metadata["provider"] == "mock_secondary"
        assert mock_primary.invocation_count == 2  # 2 retries
        assert mock_secondary.invocation_count == 1
    
    def test_conversation_history_preserved_during_failover(
        self,
        adapter_with_mocks
    ):
        """Test conversation history preserved during provider failover"""
        adapter, mock_primary, mock_secondary = adapter_with_mocks
        
        # First message succeeds with primary
        messages1 = [{"role": "user", "content": "First message"}]
        adapter.invoke("test_agent", messages1)
        
        # Make primary fail
        mock_primary.should_fail = True
        
        # Second message fails over to secondary
        messages2 = [{"role": "user", "content": "Second message"}]
        response, metadata = adapter.invoke("test_agent", messages2)
        
        # Verify secondary provider received full history
        assert metadata["provider"] == "mock_secondary"
        
        # Check conversation history is complete
        history = adapter.get_conversation_history("test_agent")
        assert len(history) == 4
        assert history[0]["content"] == "First message"
        assert history[2]["content"] == "Second message"
    
    def test_all_providers_fail(self, adapter_with_mocks):
        """Test exception when all providers fail"""
        adapter, mock_primary, mock_secondary = adapter_with_mocks
        
        # Make both providers fail
        mock_primary.should_fail = True
        mock_secondary.should_fail = True
        
        messages = [{"role": "user", "content": "Test message"}]
        
        with pytest.raises(AllProvidersFailedError):
            adapter.invoke("test_agent", messages)
        
        # Both providers should have been tried
        assert mock_primary.invocation_count == 2  # 2 retries
        assert mock_secondary.invocation_count == 2  # 2 retries
    
    def test_exponential_backoff_calculation(self, adapter_with_mocks):
        """Test exponential backoff delay calculation"""
        adapter, _, _ = adapter_with_mocks
        
        # Test backoff delays
        delay0 = adapter._calculate_backoff_delay(0)
        delay1 = adapter._calculate_backoff_delay(1)
        delay2 = adapter._calculate_backoff_delay(2)
        
        # Should be exponential: 0.1, 0.2, 0.4
        assert delay0 == pytest.approx(0.1, abs=0.01)
        assert delay1 == pytest.approx(0.2, abs=0.01)
        assert delay2 == pytest.approx(0.4, abs=0.01)
    
    def test_clear_conversation_history(self, adapter_with_mocks):
        """Test clearing conversation history"""
        adapter, _, _ = adapter_with_mocks
        
        # Add some history
        messages = [{"role": "user", "content": "Test"}]
        adapter.invoke("agent1", messages)
        adapter.invoke("agent2", messages)
        
        # Clear specific agent
        adapter.clear_conversation_history("agent1")
        
        assert len(adapter.get_conversation_history("agent1")) == 0
        assert len(adapter.get_conversation_history("agent2")) > 0
        
        # Clear all
        adapter.clear_conversation_history()
        
        assert len(adapter.get_conversation_history("agent2")) == 0
    
    def test_get_provider_health(self, adapter_with_mocks):
        """Test provider health check"""
        adapter, mock_primary, mock_secondary = adapter_with_mocks
        
        health = adapter.get_provider_health()
        
        assert health["mock_primary"] is True
        assert health["mock_secondary"] is True
        
        # Make primary unhealthy
        mock_primary.should_fail = True
        
        health = adapter.get_provider_health()
        
        assert health["mock_primary"] is False
        assert health["mock_secondary"] is True
    
    def test_multiple_agents_parallel(self, adapter_with_mocks):
        """Test multiple agents can use adapter in parallel"""
        adapter, _, _ = adapter_with_mocks
        
        messages = [{"role": "user", "content": "Test"}]
        
        # Simulate parallel invocations
        adapter.invoke("agent1", messages)
        adapter.invoke("agent2", messages)
        adapter.invoke("agent3", messages)
        
        # Each agent should have separate history
        assert len(adapter.get_conversation_history("agent1")) == 2
        assert len(adapter.get_conversation_history("agent2")) == 2
        assert len(adapter.get_conversation_history("agent3")) == 2
        
        # Histories should be independent
        history1 = adapter.get_conversation_history("agent1")
        history2 = adapter.get_conversation_history("agent2")
        
        assert history1 is not history2


class TestProviderExceptions:
    """Test provider exception types"""
    
    def test_provider_timeout_error(self):
        """Test ProviderTimeoutError"""
        error = ProviderTimeoutError("Timeout occurred")
        assert str(error) == "Timeout occurred"
        assert isinstance(error, Exception)
    
    def test_provider_rate_limit_error(self):
        """Test ProviderRateLimitError"""
        error = ProviderRateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
    
    def test_provider_api_error(self):
        """Test ProviderAPIError"""
        error = ProviderAPIError("API error")
        assert str(error) == "API error"
    
    def test_all_providers_failed_error(self):
        """Test AllProvidersFailedError"""
        error = AllProvidersFailedError("All failed")
        assert str(error) == "All failed"


class TestProviderPriority:
    """Test provider priority ordering"""
    
    def test_providers_sorted_by_priority(self):
        """Test providers are sorted by priority"""
        # Create config with reversed priorities
        config = ProvidersConfig(
            providers=[
                ProviderConfig(
                    name="low_priority",
                    priority=3,
                    api_key_env="KEY3",
                    models={"default": "model3"}
                ),
                ProviderConfig(
                    name="high_priority",
                    priority=1,
                    api_key_env="KEY1",
                    models={"default": "model1"}
                ),
                ProviderConfig(
                    name="medium_priority",
                    priority=2,
                    api_key_env="KEY2",
                    models={"default": "model2"}
                )
            ],
            retry_strategy=RetryStrategy()
        )
        
        # Mock the provider creation
        adapter = LLMProviderAdapter.__new__(LLMProviderAdapter)
        adapter.config = config
        adapter.conversation_history = {}
        
        import threading
        adapter.history_lock = threading.Lock()
        
        # Create mock providers in priority order
        adapter.providers = []
        for provider_config in sorted(config.providers, key=lambda p: p.priority):
            mock_provider = MockProvider(provider_config)
            adapter.providers.append((provider_config, mock_provider))
        
        # Verify order
        assert adapter.providers[0][0].name == "high_priority"
        assert adapter.providers[1][0].name == "medium_priority"
        assert adapter.providers[2][0].name == "low_priority"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
