"""
Unit tests for configuration loader
"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml

from src.consortium.config import (
    ConfigLoader,
    AgentConfig,
    TensionProtocolConfig,
    SystemConfig,
    ProvidersConfig,
    get_config_loader
)


class TestConfigLoader:
    """Test ConfigLoader class"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            
            # Create subdirectories
            (config_dir / "agents").mkdir()
            (config_dir / "tensions").mkdir()
            
            yield config_dir
    
    @pytest.fixture
    def sample_agent_config(self, temp_config_dir):
        """Create sample agent config file"""
        agent_config = {
            "agent_id": "test_agent",
            "name": "Test Agent",
            "mandate": "Test mandate",
            "system_prompt": "You are a test agent",
            "red_lines": ["Test red line"],
            "acceptance_criteria": {
                "block": "Test block",
                "warn": "Test warn",
                "accept": "Test accept",
                "endorse": "Test endorse"
            },
            "knowledge_domains": ["Test domain"]
        }
        
        config_path = temp_config_dir / "agents" / "test_agent.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(agent_config, f)
        
        return config_path
    
    @pytest.fixture
    def sample_tension_config(self, temp_config_dir):
        """Create sample tension protocol config file"""
        tension_config = {
            "protocol_id": "test_protocol",
            "name": "Test Protocol",
            "description": "Test description",
            "agents": ["agent1", "agent2"],
            "trigger": {
                "conditions": [
                    {"agent": "agent1", "rating": "BLOCK"}
                ]
            },
            "max_iterations": 3,
            "resolution_steps": [
                {
                    "step": 1,
                    "action": "Test action",
                    "inputs": ["input1"],
                    "outputs": ["output1"]
                }
            ],
            "escalation": {
                "condition": "Max iterations reached",
                "report_includes": ["positions", "tradeoffs"]
            }
        }
        
        config_path = temp_config_dir / "tensions" / "test_protocol.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(tension_config, f)
        
        return config_path
    
    @pytest.fixture
    def sample_providers_config(self, temp_config_dir):
        """Create sample providers config file"""
        providers_config = {
            "providers": [
                {
                    "name": "anthropic",
                    "priority": 1,
                    "api_key_env": "ANTHROPIC_API_KEY",
                    "models": {"default": "claude-sonnet-4"},
                    "timeout_seconds": 30,
                    "max_retries": 2
                }
            ],
            "retry_strategy": {
                "base_delay_seconds": 1.0,
                "exponential_backoff": True,
                "max_delay_seconds": 10.0,
                "jitter": 0.1
            }
        }
        
        config_path = temp_config_dir / "providers.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(providers_config, f)
        
        return config_path
    
    def test_load_agent_config(self, temp_config_dir, sample_agent_config):
        """Test loading agent configuration"""
        loader = ConfigLoader(str(temp_config_dir))
        
        config = loader.load_agent_config("test_agent")
        
        assert isinstance(config, AgentConfig)
        assert config.agent_id == "test_agent"
        assert config.name == "Test Agent"
        assert config.mandate == "Test mandate"
        assert len(config.red_lines) == 1
        assert len(config.knowledge_domains) == 1
    
    def test_load_agent_config_not_found(self, temp_config_dir):
        """Test loading non-existent agent config"""
        loader = ConfigLoader(str(temp_config_dir))
        
        with pytest.raises(FileNotFoundError):
            loader.load_agent_config("nonexistent_agent")
    
    def test_load_agent_config_caching(
        self,
        temp_config_dir,
        sample_agent_config
    ):
        """Test agent config caching"""
        loader = ConfigLoader(str(temp_config_dir))
        
        # First load
        config1 = loader.load_agent_config("test_agent")
        
        # Second load (should use cache)
        config2 = loader.load_agent_config("test_agent")
        
        assert config1 is config2  # Same object from cache
    
    def test_reload_agent_config(self, temp_config_dir, sample_agent_config):
        """Test hot-reload of agent config"""
        loader = ConfigLoader(str(temp_config_dir))
        
        # First load
        config1 = loader.load_agent_config("test_agent")
        
        # Modify config file
        with open(sample_agent_config, 'r') as f:
            data = yaml.safe_load(f)
        data["name"] = "Modified Test Agent"
        with open(sample_agent_config, 'w') as f:
            yaml.dump(data, f)
        
        # Reload
        config2 = loader.reload_agent_config("test_agent")
        
        assert config2.name == "Modified Test Agent"
        assert config1.name != config2.name
    
    def test_load_tension_config(
        self,
        temp_config_dir,
        sample_tension_config
    ):
        """Test loading tension protocol configuration"""
        loader = ConfigLoader(str(temp_config_dir))
        
        config = loader.load_tension_config("test_protocol")
        
        assert isinstance(config, TensionProtocolConfig)
        assert config.protocol_id == "test_protocol"
        assert config.name == "Test Protocol"
        assert len(config.agents) == 2
        assert config.max_iterations == 3
        assert len(config.resolution_steps) == 1
    
    def test_load_tension_config_validation(self, temp_config_dir):
        """Test tension config validation (must have 2 agents)"""
        # Create invalid config with 3 agents
        invalid_config = {
            "protocol_id": "invalid_protocol",
            "name": "Invalid Protocol",
            "description": "Invalid",
            "agents": ["agent1", "agent2", "agent3"],  # Invalid: 3 agents
            "trigger": {"conditions": []},
            "max_iterations": 3,
            "resolution_steps": [],
            "escalation": {
                "condition": "test",
                "report_includes": []
            }
        }
        
        config_path = temp_config_dir / "tensions" / "invalid_protocol.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(invalid_config, f)
        
        loader = ConfigLoader(str(temp_config_dir))
        
        with pytest.raises(ValueError, match="exactly 2 agents"):
            loader.load_tension_config("invalid_protocol")
    
    def test_load_system_config_default(self, temp_config_dir):
        """Test loading system config with defaults"""
        loader = ConfigLoader(str(temp_config_dir))
        
        config = loader.load_system_config()
        
        assert isinstance(config, SystemConfig)
        assert config.name == "European Strategy Consortium"
        assert config.version == "1.0.0"
        assert config.environment == "development"
    
    def test_load_providers_config(
        self,
        temp_config_dir,
        sample_providers_config
    ):
        """Test loading providers configuration"""
        loader = ConfigLoader(str(temp_config_dir))
        
        config = loader.load_providers_config()
        
        assert isinstance(config, ProvidersConfig)
        assert len(config.providers) == 1
        assert config.providers[0].name == "anthropic"
        assert config.providers[0].priority == 1
        assert config.retry_strategy.exponential_backoff is True
    
    def test_load_providers_config_priority_validation(
        self,
        temp_config_dir
    ):
        """Test providers config validates unique priorities"""
        # Create invalid config with duplicate priorities
        invalid_config = {
            "providers": [
                {
                    "name": "anthropic",
                    "priority": 1,
                    "api_key_env": "KEY1",
                    "models": {"default": "model1"}
                },
                {
                    "name": "openai",
                    "priority": 1,  # Duplicate priority
                    "api_key_env": "KEY2",
                    "models": {"default": "model2"}
                }
            ],
            "retry_strategy": {
                "base_delay_seconds": 1.0,
                "exponential_backoff": True,
                "max_delay_seconds": 10.0,
                "jitter": 0.1
            }
        }
        
        config_path = temp_config_dir / "providers.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(invalid_config, f)
        
        loader = ConfigLoader(str(temp_config_dir))
        
        with pytest.raises(ValueError, match="priorities must be unique"):
            loader.load_providers_config()
    
    def test_load_all_agent_configs(
        self,
        temp_config_dir,
        sample_agent_config
    ):
        """Test loading all agent configs"""
        # Create second agent config
        agent_config2 = {
            "agent_id": "test_agent2",
            "name": "Test Agent 2",
            "mandate": "Test mandate 2",
            "system_prompt": "You are test agent 2",
            "red_lines": [],
            "acceptance_criteria": {
                "block": "b", "warn": "w", "accept": "a", "endorse": "e"
            },
            "knowledge_domains": []
        }
        
        config_path2 = temp_config_dir / "agents" / "test_agent2.yaml"
        with open(config_path2, 'w') as f:
            yaml.dump(agent_config2, f)
        
        loader = ConfigLoader(str(temp_config_dir))
        
        all_configs = loader.load_all_agent_configs()
        
        assert len(all_configs) == 2
        assert "test_agent" in all_configs
        assert "test_agent2" in all_configs
    
    def test_clear_cache(self, temp_config_dir, sample_agent_config):
        """Test clearing configuration cache"""
        loader = ConfigLoader(str(temp_config_dir))
        
        # Load config
        config1 = loader.load_agent_config("test_agent")
        
        # Clear cache
        loader.clear_cache()
        
        # Load again (should be new object)
        config2 = loader.load_agent_config("test_agent")
        
        assert config1 is not config2


class TestGlobalConfigLoader:
    """Test global config loader singleton"""
    
    def test_get_config_loader_singleton(self):
        """Test that get_config_loader returns singleton"""
        loader1 = get_config_loader()
        loader2 = get_config_loader()
        
        assert loader1 is loader2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
