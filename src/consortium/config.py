"""
Configuration Loader for European Strategy Consortium

Loads and validates YAML configuration files for agents, tensions,
and system settings using Pydantic for validation.

Based on ARCHITECTURE_PART3.md Section 8.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Literal
import yaml
from pydantic import BaseModel, Field, validator


# ==============================================================================
# PYDANTIC MODELS FOR VALIDATION
# ==============================================================================

class AgentConfig(BaseModel):
    """Configuration for a single agent"""
    agent_id: str
    name: str
    mandate: str
    system_prompt: str
    red_lines: List[str]
    acceptance_criteria: Dict[str, Any]  # Changed from Dict[str, str] to Dict[str, Any] to support both strings and lists
    knowledge_domains: List[str]
    example_attack_patterns: Optional[List[str]] = []

    class Config:
        extra = "allow"  # Allow additional fields


class TensionTriggerCondition(BaseModel):
    """Single trigger condition for tension protocol"""
    agent: str
    rating: Optional[str] = None
    keywords: Optional[List[str]] = None
    threshold_mentioned: Optional[float] = None


class TensionResolutionStep(BaseModel):
    """Single step in tension resolution"""
    step: int
    action: str
    inputs: Optional[List[str]] = None
    outputs: Optional[List[str]] = None
    logic: Optional[str] = None
    participants: Optional[List[str]] = None
    success_criteria: Optional[List[str]] = None


class TensionEscalation(BaseModel):
    """Escalation configuration for tension protocol"""
    condition: str
    report_includes: List[str]


class TensionProtocolConfig(BaseModel):
    """Configuration for a tension protocol"""
    protocol_id: str
    name: str
    description: str
    agents: List[str]
    trigger: Dict[str, Any]
    max_iterations: int
    resolution_steps: List[TensionResolutionStep]
    escalation: TensionEscalation
    
    @validator('agents')
    def validate_agents_count(cls, v):
        """Ensure exactly 2 agents for tension protocol"""
        if len(v) != 2:
            raise ValueError(f"Tension protocol must have exactly 2 agents, got {len(v)}")
        return v


class ConvergenceCriterion(BaseModel):
    """Single convergence criterion"""
    name: str
    check: str
    failure_message: str


class FailureMode(BaseModel):
    """Failure mode detection and action"""
    detection: str
    action: str


class ConvergenceConfig(BaseModel):
    """Convergence testing configuration"""
    convergence_criteria: Dict[str, ConvergenceCriterion]
    failure_modes: Dict[str, FailureMode]


class PerformanceTargets(BaseModel):
    """Performance targets for the system"""
    simple_query_seconds: int = 30
    medium_query_seconds: int = 120
    complex_query_seconds: int = 300
    memory_retrieval_ms: int = 500


class DebugConfig(BaseModel):
    """Debug configuration"""
    log_level: Literal["DEBUG", "INFO", "WARN", "ERROR"] = "INFO"
    enable_trace_logging: bool = True
    save_intermediate_states: bool = True


class MemoryConfig(BaseModel):
    """Memory system configuration"""
    persist_directory: str = "./chroma_db"
    embedding_model: str = "text-embedding-3-small"
    quality_threshold: float = 3.5
    progressive_fallback_enabled: bool = True


class KnowledgeConfig(BaseModel):
    """Knowledge system configuration"""
    static_db_path: str = "./knowledge_db"
    dynamic_cache_ttl_hours: int = 24
    confidence_threshold: float = 0.7


class RoutingConfig(BaseModel):
    """Routing configuration"""
    max_agents_per_query: int = 7
    always_engaged_agents: List[str] = ["economist", "architect"]
    keyword_confidence_threshold: float = 0.6
    semantic_similarity_threshold: float = 0.6


class SystemConfig(BaseModel):
    """System-wide configuration"""
    name: str = "European Strategy Consortium"
    version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"
    performance_targets: PerformanceTargets = Field(default_factory=PerformanceTargets)
    debug: DebugConfig = Field(default_factory=DebugConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    knowledge: KnowledgeConfig = Field(default_factory=KnowledgeConfig)
    routing: RoutingConfig = Field(default_factory=RoutingConfig)


class ProviderConfig(BaseModel):
    """Single LLM provider configuration"""
    name: str
    priority: int
    api_key_env: str
    models: Dict[str, str]
    timeout_seconds: int = 30
    max_retries: int = 2


class RetryStrategy(BaseModel):
    """Retry strategy configuration"""
    base_delay_seconds: float = 1.0
    exponential_backoff: bool = True
    max_delay_seconds: float = 10.0
    jitter: float = 0.1


class ProvidersConfig(BaseModel):
    """Multi-provider configuration"""
    providers: List[ProviderConfig]
    retry_strategy: RetryStrategy = Field(default_factory=RetryStrategy)
    
    @validator('providers')
    def validate_priorities(cls, v):
        """Ensure unique priorities"""
        priorities = [p.priority for p in v]
        if len(priorities) != len(set(priorities)):
            raise ValueError("Provider priorities must be unique")
        return v


class ChromaConfig(BaseModel):
    """Chroma database configuration"""
    persist_directory: str = "./data/chroma"
    collection_name: str = "strategic_cases"


class EmbeddingConfig(BaseModel):
    """Embedding configuration"""
    provider: str = "openai"
    model: str = "text-embedding-3-small"
    dimensions: int = 1536


class RetrievalConfig(BaseModel):
    """Retrieval configuration"""
    top_k: int = 3
    similarity_threshold: float = 0.7
    quality_score_threshold: float = 3.5
    progressive_fallback: bool = True
    verified_outcome_boost: float = 1.5


class StorageConfig(BaseModel):
    """Storage configuration"""
    capture_immediate_feedback: bool = True
    enable_outcome_updates: bool = True
    max_cases: int = 10000


class FallbackConfig(BaseModel):
    """Progressive fallback configuration"""
    tier_1_threshold: float = 3.5
    tier_1_penalty: float = 0.0
    tier_2_threshold: float = 3.0
    tier_2_penalty: float = -0.20
    tier_3_threshold: float = 2.5
    tier_3_penalty: float = -0.25
    cold_start_penalty: float = -0.15


class MemoryConfig(BaseModel):
    """Memory system configuration"""
    chroma: ChromaConfig = Field(default_factory=ChromaConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    fallback: FallbackConfig = Field(default_factory=FallbackConfig)


# ==============================================================================
# CONFIGURATION LOADER
# ==============================================================================

class ConfigLoader:
    """
    Loads and validates configuration files from YAML.
    
    Supports:
    - Agent configurations (hot-reload capable)
    - Tension protocol configurations
    - System configuration
    - Provider configuration
    """
    
    def __init__(self, config_dir: str = "./config"):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Root directory for configuration files
        """
        self.config_dir = Path(config_dir)
        self.agents_dir = self.config_dir / "agents"
        self.tensions_dir = self.config_dir / "tensions"
        
        # Cache for loaded configurations
        self._agent_cache: Dict[str, AgentConfig] = {}
        self._tension_cache: Dict[str, TensionProtocolConfig] = {}
        self._system_config: Optional[SystemConfig] = None
        self._providers_config: Optional[ProvidersConfig] = None
    
    def load_agent_config(self, agent_id: str, use_cache: bool = True) -> AgentConfig:
        """
        Load agent configuration from YAML file.
        
        Args:
            agent_id: Agent identifier (e.g., "sovereign")
            use_cache: Whether to use cached config (False for hot-reload)
        
        Returns:
            Validated AgentConfig object
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config validation fails
        """
        # Check cache
        if use_cache and agent_id in self._agent_cache:
            return self._agent_cache[agent_id]
        
        # Load from file
        config_path = self.agents_dir / f"{agent_id}.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(
                f"Agent config not found: {config_path}"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)
        
        # Validate with Pydantic
        try:
            agent_config = AgentConfig(**raw_config)
        except Exception as e:
            raise ValueError(
                f"Invalid agent config for {agent_id}: {e}"
            )
        
        # Cache and return
        self._agent_cache[agent_id] = agent_config
        return agent_config
    
    def load_tension_config(
        self,
        protocol_id: str,
        use_cache: bool = True
    ) -> TensionProtocolConfig:
        """
        Load tension protocol configuration from YAML file.
        
        Args:
            protocol_id: Protocol identifier (e.g., "sovereign_economist")
            use_cache: Whether to use cached config
        
        Returns:
            Validated TensionProtocolConfig object
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config validation fails
        """
        # Check cache
        if use_cache and protocol_id in self._tension_cache:
            return self._tension_cache[protocol_id]
        
        # Load from file
        config_path = self.tensions_dir / f"{protocol_id}.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(
                f"Tension config not found: {config_path}"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)
        
        # Validate with Pydantic
        try:
            tension_config = TensionProtocolConfig(**raw_config)
        except Exception as e:
            raise ValueError(
                f"Invalid tension config for {protocol_id}: {e}"
            )
        
        # Cache and return
        self._tension_cache[protocol_id] = tension_config
        return tension_config
    
    def load_system_config(self, use_cache: bool = True) -> SystemConfig:
        """
        Load system configuration from YAML file.
        
        Args:
            use_cache: Whether to use cached config
        
        Returns:
            Validated SystemConfig object
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config validation fails
        """
        # Check cache
        if use_cache and self._system_config is not None:
            return self._system_config
        
        # Load from file
        config_path = self.config_dir / "system.yaml"
        
        if not config_path.exists():
            # Return default config if file doesn't exist
            self._system_config = SystemConfig()
            return self._system_config
        
        with open(config_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)
        
        # Validate with Pydantic
        try:
            system_config = SystemConfig(**raw_config.get('system', {}))
        except Exception as e:
            raise ValueError(f"Invalid system config: {e}")
        
        # Cache and return
        self._system_config = system_config
        return system_config
    
    def load_providers_config(self, use_cache: bool = True) -> ProvidersConfig:
        """
        Load providers configuration from YAML file.
        
        Args:
            use_cache: Whether to use cached config
        
        Returns:
            Validated ProvidersConfig object
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config validation fails
        """
        # Check cache
        if use_cache and self._providers_config is not None:
            return self._providers_config
        
        # Load from file
        config_path = self.config_dir / "providers.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(
                f"Providers config not found: {config_path}"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)
        
        # Validate with Pydantic
        try:
            providers_config = ProvidersConfig(**raw_config)
        except Exception as e:
            raise ValueError(f"Invalid providers config: {e}")
        
        # Cache and return
        self._providers_config = providers_config
        return providers_config
    
    def load_memory_config(self, use_cache: bool = True) -> MemoryConfig:
        """
        Load memory configuration from YAML file.
        
        Args:
            use_cache: Whether to use cached config
        
        Returns:
            Validated MemoryConfig object
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config validation fails
        """
        # Check cache
        if use_cache and hasattr(self, '_memory_config') and self._memory_config is not None:
            return self._memory_config
        
        # Load from file
        config_path = self.config_dir / "memory.yaml"
        
        if not config_path.exists():
            # Return default config if file doesn't exist
            self._memory_config = MemoryConfig()
            return self._memory_config
        
        with open(config_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)
        
        # Validate with Pydantic
        try:
            memory_config = MemoryConfig(**raw_config)
        except Exception as e:
            raise ValueError(f"Invalid memory config: {e}")
        
        # Cache and return
        self._memory_config = memory_config
        return memory_config
    
    def load_all_agent_configs(self) -> Dict[str, AgentConfig]:
        """
        Load all agent configurations from agents directory.
        
        Returns:
            Dictionary mapping agent_id to AgentConfig
        """
        agent_configs = {}
        
        if not self.agents_dir.exists():
            return agent_configs
        
        for config_file in self.agents_dir.glob("*.yaml"):
            agent_id = config_file.stem
            try:
                agent_configs[agent_id] = self.load_agent_config(agent_id)
            except Exception as e:
                print(f"Warning: Failed to load agent config {agent_id}: {e}")
        
        return agent_configs
    
    def reload_agent_config(self, agent_id: str) -> AgentConfig:
        """
        Force reload agent configuration (hot-reload).
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Freshly loaded AgentConfig
        """
        return self.load_agent_config(agent_id, use_cache=False)
    
    def clear_cache(self):
        """Clear all cached configurations"""
        self._agent_cache.clear()
        self._tension_cache.clear()
        self._system_config = None
        self._providers_config = None


# ==============================================================================
# GLOBAL INSTANCE
# ==============================================================================

# Global config loader instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader(config_dir: str = "./config") -> ConfigLoader:
    """
    Get global ConfigLoader instance (singleton pattern).
    
    Args:
        config_dir: Root directory for configuration files
    
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    
    if _config_loader is None:
        _config_loader = ConfigLoader(config_dir)
    
    return _config_loader
