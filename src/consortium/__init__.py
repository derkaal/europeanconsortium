"""Consortium - Multi-agent decision-making system."""

# Load environment variables at package import
from dotenv import load_dotenv
load_dotenv()

from .graph import create_consortium_graph
from .state import ConsortiumState, create_initial_state
from .llm_provider import get_llm_provider

__version__ = "0.1.0"

__all__ = [
    "create_consortium_graph",
    "ConsortiumState",
    "create_initial_state",
    "get_llm_provider",
]
