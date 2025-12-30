"""
Web search tools for The Scout.

Supports multiple providers with automatic failover:
1. Tavily (primary) - Best for AI-optimized search results
2. Brave (secondary) - Privacy-focused, good EU coverage, no tracking

Set environment variables:
- TAVILY_API_KEY: For Tavily search
- BRAVE_API_KEY: For Brave search

The SearchToolFactory will use available providers with failover.
"""

from typing import List, Dict, Any, Optional, Protocol
from abc import ABC, abstractmethod
import os
import logging
import asyncio
import aiohttp

logger = logging.getLogger(__name__)


class SearchProvider(Protocol):
    """Protocol for search providers."""

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Execute search and return results."""
        ...

    def is_available(self) -> bool:
        """Check if provider is configured and available."""
        ...


class BaseSearchTool(ABC):
    """Base class for search tools with common utilities."""

    # Known authoritative sources for source extraction
    SOURCE_MAPPING = {
        # EU Official
        "eur-lex.europa.eu": "EUR-Lex",
        "ec.europa.eu": "European Commission",
        "edpb.europa.eu": "EDPB",
        "enisa.europa.eu": "ENISA",
        "europarl.europa.eu": "European Parliament",
        "curia.europa.eu": "ECJ",

        # AI Providers
        "mistral.ai": "Mistral AI",
        "anthropic.com": "Anthropic",
        "openai.com": "OpenAI",
        "huggingface.co": "Hugging Face",
        "aleph-alpha.com": "Aleph Alpha",

        # News
        "reuters.com": "Reuters",
        "bloomberg.com": "Bloomberg",
        "politico.eu": "Politico EU",
        "euractiv.com": "Euractiv",
        "ft.com": "Financial Times",
        "theregister.com": "The Register",
        "arstechnica.com": "Ars Technica",

        # Tech
        "techcrunch.com": "TechCrunch",
        "wired.com": "Wired",
        "github.com": "GitHub",

        # Cloud Providers
        "aws.amazon.com": "AWS",
        "cloud.google.com": "Google Cloud",
        "azure.microsoft.com": "Microsoft Azure",
        "ovhcloud.com": "OVHcloud",
        "scaleway.com": "Scaleway"
    }

    def _extract_source(self, url: str) -> str:
        """Extract source name from URL."""
        if not url:
            return "Unknown"

        for domain, name in self.SOURCE_MAPPING.items():
            if domain in url:
                return name

        # Extract domain as fallback
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace("www.", "")
        except Exception:
            return "Web"

    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Execute search."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check availability."""
        pass


class TavilySearchTool(BaseSearchTool):
    """
    Tavily search integration for Scout research.

    Tavily is optimized for AI applications and provides
    high-quality, structured search results.

    Requires: pip install tavily-python
    Environment: TAVILY_API_KEY
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.client = None

        if self.api_key:
            try:
                from tavily import TavilyClient
                self.client = TavilyClient(api_key=self.api_key)
                logger.info("Tavily search initialized")
            except ImportError:
                logger.warning("tavily-python not installed: pip install tavily-python")

    def is_available(self) -> bool:
        return self.client is not None

    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic"
    ) -> List[Dict[str, Any]]:
        """
        Execute Tavily web search.

        Args:
            query: Search query
            max_results: Maximum results to return
            search_depth: "basic" or "advanced"

        Returns:
            List of search results with title, snippet, url
        """
        if not self.client:
            logger.warning("Tavily client not available")
            return []

        try:
            # Tavily client is sync, run in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.search(
                    query=query,
                    max_results=max_results,
                    search_depth=search_depth
                )
            )

            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("content", ""),
                    "url": item.get("url", ""),
                    "score": item.get("score", 0),
                    "source": self._extract_source(item.get("url", "")),
                    "provider": "tavily"
                })

            logger.info(f"Tavily returned {len(results)} results for: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []


class BraveSearchTool(BaseSearchTool):
    """
    Brave Search integration for Scout research.

    Brave Search is privacy-focused, has good European coverage,
    and provides an independent index (not Google/Bing based).

    Benefits:
    - Privacy-focused (no tracking)
    - Independent index
    - Good for European queries
    - Supports goggles for customized ranking

    Requires: aiohttp (pip install aiohttp)
    Environment: BRAVE_API_KEY
    API Docs: https://brave.com/search/api/
    """

    BASE_URL = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")

        if self.api_key:
            logger.info("Brave search initialized")
        else:
            logger.warning("BRAVE_API_KEY not set")

    def is_available(self) -> bool:
        return self.api_key is not None

    async def search(
        self,
        query: str,
        max_results: int = 5,
        country: str = "DE",  # Default to Germany for EU focus
        search_lang: str = "en",
        freshness: Optional[str] = None  # "pd" (past day), "pw" (past week), "pm" (past month)
    ) -> List[Dict[str, Any]]:
        """
        Execute Brave web search.

        Args:
            query: Search query
            max_results: Maximum results to return (max 20)
            country: Country code for results (DE, FR, NL, etc.)
            search_lang: Language for results
            freshness: Time filter (pd=day, pw=week, pm=month, py=year)

        Returns:
            List of search results with title, snippet, url
        """
        if not self.api_key:
            logger.warning("Brave API key not available")
            return []

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }

        params = {
            "q": query,
            "count": min(max_results, 20),  # Brave max is 20
            "country": country,
            "search_lang": search_lang,
            "text_decorations": False,  # No bold markers in snippets
            "safesearch": "moderate"
        }

        if freshness:
            params["freshness"] = freshness

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.BASE_URL,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Brave search failed: {response.status} - {error_text}")
                        return []

                    data = await response.json()

            results = []
            web_results = data.get("web", {}).get("results", [])

            for item in web_results[:max_results]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("description", ""),
                    "url": item.get("url", ""),
                    "age": item.get("age", ""),  # Brave provides age like "2 days ago"
                    "source": self._extract_source(item.get("url", "")),
                    "provider": "brave",
                    # Brave-specific metadata
                    "language": item.get("language", ""),
                    "family_friendly": item.get("family_friendly", True)
                })

            logger.info(f"Brave returned {len(results)} results for: {query[:50]}...")
            return results

        except asyncio.TimeoutError:
            logger.error("Brave search timed out")
            return []
        except Exception as e:
            logger.error(f"Brave search failed: {e}")
            return []


class MultiProviderSearchTool(BaseSearchTool):
    """
    Search tool with multiple providers and automatic failover.

    Tries providers in order until one succeeds.
    Can also aggregate results from multiple providers.
    """

    def __init__(
        self,
        providers: Optional[List[BaseSearchTool]] = None,
        mode: str = "failover"  # "failover" or "aggregate"
    ):
        """
        Initialize with providers.

        Args:
            providers: List of search providers (in priority order)
            mode: "failover" (use first available) or "aggregate" (combine results)
        """
        self.mode = mode

        if providers:
            self.providers = providers
        else:
            # Default: Try Tavily first, then Brave
            self.providers = []

            tavily = TavilySearchTool()
            if tavily.is_available():
                self.providers.append(tavily)

            brave = BraveSearchTool()
            if brave.is_available():
                self.providers.append(brave)

        available = [type(p).__name__ for p in self.providers if p.is_available()]
        logger.info(f"MultiProviderSearchTool initialized with: {available}")

    def is_available(self) -> bool:
        return any(p.is_available() for p in self.providers)

    async def search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Execute search with failover or aggregation.
        """
        if self.mode == "failover":
            return await self._search_failover(query, max_results)
        else:
            return await self._search_aggregate(query, max_results)

    async def _search_failover(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Try each provider until one succeeds."""
        for provider in self.providers:
            if not provider.is_available():
                continue

            try:
                results = await provider.search(query, max_results)
                if results:
                    return results
            except Exception as e:
                logger.warning(f"{type(provider).__name__} failed, trying next: {e}")
                continue

        logger.error("All search providers failed")
        return []

    async def _search_aggregate(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Aggregate results from all available providers."""
        tasks = []

        for provider in self.providers:
            if provider.is_available():
                tasks.append(provider.search(query, max_results))

        if not tasks:
            return []

        all_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine and deduplicate by URL
        seen_urls = set()
        combined = []

        for result_set in all_results:
            if isinstance(result_set, Exception):
                logger.warning(f"Provider failed during aggregation: {result_set}")
                continue

            for item in result_set:
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    combined.append(item)

        # Sort by score if available, take top max_results
        combined.sort(key=lambda x: x.get("score", 0), reverse=True)
        return combined[:max_results]


class SearchToolFactory:
    """
    Factory to create the best available search tool.

    Usage:
        search_tool = SearchToolFactory.create()
        results = await search_tool.search("EU AI Act 2025")
    """

    @staticmethod
    def create(
        mode: str = "failover",
        preferred_provider: Optional[str] = None
    ) -> BaseSearchTool:
        """
        Create a search tool based on available API keys.

        Args:
            mode: "failover" or "aggregate"
            preferred_provider: "tavily", "brave", or None (auto)

        Returns:
            Configured search tool
        """
        providers = []

        # Check for specific preference
        if preferred_provider == "tavily":
            tavily = TavilySearchTool()
            if tavily.is_available():
                return tavily

        if preferred_provider == "brave":
            brave = BraveSearchTool()
            if brave.is_available():
                return brave

        # Auto-detect available providers
        tavily = TavilySearchTool()
        brave = BraveSearchTool()

        if tavily.is_available():
            providers.append(tavily)

        if brave.is_available():
            providers.append(brave)

        if not providers:
            logger.error("No search providers available. Set TAVILY_API_KEY or BRAVE_API_KEY")
            # Return a no-op tool
            return NoOpSearchTool()

        if len(providers) == 1:
            return providers[0]

        return MultiProviderSearchTool(providers=providers, mode=mode)


class NoOpSearchTool(BaseSearchTool):
    """Fallback search tool when no providers are available."""

    def is_available(self) -> bool:
        return False

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        logger.warning("No search provider configured - returning empty results")
        return []
