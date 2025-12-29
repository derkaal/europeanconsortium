"""Simplified LLM Provider Manager with manual failover.

Based on LangChain research findings:
- No built-in provider failover in LangChain
- Must implement manual try/except loop
- Use SystemMessage + HumanMessage pattern
- API keys read from environment variables
"""

import os
import logging
from typing import Optional, List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Import LangChain providers
try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("langchain-anthropic not installed")

try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("langchain-openai not installed")

try:
    from langchain_mistralai import ChatMistralAI
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False
    logger.warning("langchain-mistralai not installed")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logger.warning("langchain-google-genai not installed")

try:
    from langchain_core.messages import SystemMessage, HumanMessage
    LANGCHAIN_CORE_AVAILABLE = True
except ImportError:
    LANGCHAIN_CORE_AVAILABLE = False
    logger.error("langchain-core not installed - LLM functionality disabled")


class LLMProviderManager:
    """
    Simple LLM provider manager with manual failover.
    
    PATTERN FROM LANGCHAIN RESEARCH:
    - Initialize provider-specific clients (ChatAnthropic, ChatOpenAI, etc.)
    - API keys read automatically from environment variables
    - Manual failover loop (no built-in support in LangChain)
    - Use SystemMessage + HumanMessage pattern
    """
    
    def __init__(self):
        """Initialize available LLM providers."""
        self.providers: List[Tuple[str, any]] = []
        
        if not LANGCHAIN_CORE_AVAILABLE:
            raise ImportError(
                "langchain-core is required. "
                "Install with: pip install langchain-core"
            )
        
        # Initialize Anthropic (Claude)
        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            try:
                client = ChatAnthropic(
                    model="claude-sonnet-4-20250514",
                    temperature=0.3,
                    max_tokens=4096,
                    timeout=60
                )
                self.providers.append(("anthropic", client))
                logger.info("✓ Anthropic provider initialized")
            except Exception as e:
                logger.warning(f"✗ Anthropic initialization failed: {e}")
        
        # Initialize OpenAI (GPT-4)
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            try:
                client = ChatOpenAI(
                    model="gpt-4",
                    temperature=0.3,
                    max_tokens=4096,
                    timeout=60
                )
                self.providers.append(("openai", client))
                logger.info("✓ OpenAI provider initialized")
            except Exception as e:
                logger.warning(f"✗ OpenAI initialization failed: {e}")
        
        # Initialize Mistral
        if MISTRAL_AVAILABLE and os.getenv("MISTRAL_API_KEY"):
            try:
                client = ChatMistralAI(
                    model="mistral-large-latest",
                    temperature=0.3,
                    max_tokens=4096,
                    timeout=60
                )
                self.providers.append(("mistral", client))
                logger.info("✓ Mistral provider initialized")
            except Exception as e:
                logger.warning(f"✗ Mistral initialization failed: {e}")
        
        # Initialize Google Gemini
        if GOOGLE_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
            try:
                client = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    temperature=0.3,
                    max_tokens=4096,
                    timeout=60
                )
                self.providers.append(("gemini", client))
                logger.info("✓ Gemini provider initialized")
            except Exception as e:
                logger.warning(f"✗ Gemini initialization failed: {e}")
        
        if not self.providers:
            raise ValueError(
                "No LLM providers available. "
                "Please set at least one API key in .env file. "
                "See .env.example for details."
            )
        
        logger.info(
            f"LLMProviderManager initialized with {len(self.providers)} "
            f"provider(s): {[p[0] for p in self.providers]}"
        )
    
    def invoke(
        self,
        system_prompt: str,
        user_message: str,
        agent_id: Optional[str] = None
    ) -> str:
        """
        Invoke LLM with manual failover across providers.
        
        PATTERN FROM LANGCHAIN RESEARCH:
        - Build messages list with SystemMessage + HumanMessage
        - Try each provider in sequence
        - Log failures and continue to next provider
        - Raise exception if all providers fail
        
        Args:
            system_prompt: System prompt defining agent role
            user_message: User message with query and context
            agent_id: Optional agent ID for logging
            
        Returns:
            LLM response content as string
            
        Raises:
            Exception: If all providers fail
        """
        # Build messages using LangChain pattern
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        agent_label = f" for agent {agent_id}" if agent_id else ""
        
        # Manual failover loop
        last_error = None
        for provider_name, provider_client in self.providers:
            try:
                logger.debug(
                    f"Attempting {provider_name}{agent_label}"
                )
                
                # Invoke provider
                response = provider_client.invoke(messages)
                
                # Extract content from AIMessage
                content = response.content
                
                logger.info(
                    f"✓ {provider_name} succeeded{agent_label} "
                    f"({len(content)} chars)"
                )
                
                return content
                
            except Exception as e:
                logger.warning(
                    f"✗ {provider_name} failed{agent_label}: {e}"
                )
                last_error = e
                continue
        
        # All providers failed
        error_msg = (
            f"All {len(self.providers)} LLM provider(s) failed{agent_label}. "
            f"Last error: {last_error}"
        )
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [name for name, _ in self.providers]


# Singleton instance
_provider_manager: Optional[LLMProviderManager] = None


def get_llm_provider() -> LLMProviderManager:
    """Get singleton LLM provider manager instance."""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = LLMProviderManager()
    return _provider_manager
