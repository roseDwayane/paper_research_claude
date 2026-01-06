"""
Google Scholar search tool via SerpAPI.

Note: Google Scholar doesn't have an official API.
This uses SerpAPI (https://serpapi.com/) as a proxy.
Requires a SerpAPI key for production use.
"""

import uuid
import asyncio
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import config
from src.tools.base import BaseTool, ToolResult
from src.schemas.paper import Paper, Author, SourceAPI


class GoogleScholarSearchTool(BaseTool):
    """Search Google Scholar via SerpAPI proxy."""

    name = "search_google_scholar"
    description = "Search Google Scholar for academic papers. Broader coverage than OpenAlex/PubMed but less structured metadata."

    SERPAPI_URL = "https://serpapi.com/search.json"

    def __init__(self):
        self.api_key = config.api.serpapi_key

    def _get_parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query terms",
                },
                "year_from": {
                    "type": "integer",
                    "description": "Filter papers from this year onwards",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 20)",
                    "default": 20,
                },
            },
            "required": ["query"],
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _fetch(self, params: dict) -> dict:
        """Fetch from SerpAPI with retry logic."""
        async with httpx.AsyncClient() as client:
            response = await client.get(self.SERPAPI_URL, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()

    async def execute(
        self,
        query: str,
        year_from: Optional[int] = None,
        limit: int = 20,
    ) -> ToolResult[list[Paper]]:
        """
        Execute Google Scholar search.

        Args:
            query: Search terms
            year_from: Start year filter
            limit: Max results (SerpAPI returns up to 20 per page)

        Returns:
            ToolResult containing list of Paper objects
        """
        # Check for API key
        if not self.api_key:
            return ToolResult.fail(
                "Google Scholar search requires SerpAPI key. "
                "Set SERPAPI_KEY in environment or use OpenAlex/PubMed instead."
            )

        try:
            # Build request params
            params = {
                "engine": "google_scholar",
                "q": query,
                "api_key": self.api_key,
                "num": min(limit, 20),  # SerpAPI max is 20 per page
            }

            if year_from:
                params["as_ylo"] = year_from

            # Fetch results
            data = await self._fetch(params)

            # Parse results
            papers = []
            for result in data.get("organic_results", []):
                paper = self._parse_result(result)
                if paper:
                    papers.append(paper)

            await asyncio.sleep(config.agent.api_delay_seconds)

            return ToolResult.ok(
                papers,
                total_results=data.get("search_information", {}).get(
                    "total_results", len(papers)
                ),
                query=query,
                source="google_scholar",
            )

        except httpx.HTTPStatusError as e:
            return ToolResult.fail(f"SerpAPI error: {e.response.status_code}")
        except Exception as e:
            return ToolResult.fail(f"Google Scholar search failed: {str(e)}")

    def _parse_result(self, result: dict) -> Optional[Paper]:
        """Parse a Google Scholar result into Paper."""
        try:
            title = result.get("title", "Untitled")

            # Parse authors from publication_info
            authors = []
            pub_info = result.get("publication_info", {})
            authors_str = pub_info.get("authors", [])
            if isinstance(authors_str, list):
                for author_info in authors_str[:10]:
                    if isinstance(author_info, dict):
                        authors.append(Author(name=author_info.get("name", "Unknown")))
                    elif isinstance(author_info, str):
                        authors.append(Author(name=author_info))

            # Extract year from summary
            year = None
            summary = pub_info.get("summary", "")
            import re
            year_match = re.search(r"\b(19|20)\d{2}\b", summary)
            if year_match:
                year = int(year_match.group())

            # Extract snippet as abstract
            abstract = result.get("snippet")

            # Try to extract DOI from link or resources
            doi = None
            link = result.get("link", "")
            doi_match = re.search(r"10\.\d{4,}/[^\s]+", link)
            if doi_match:
                doi = doi_match.group()

            return Paper(
                id=f"gscholar_{uuid.uuid4().hex[:12]}",
                doi=doi,
                title=title,
                authors=authors,
                year=year,
                abstract=abstract,
                citation_count=result.get("inline_links", {}).get("cited_by", {}).get("total"),
                source_api=SourceAPI.GOOGLE_SCHOLAR,
                source_url=result.get("link"),
                raw_response=result,
            )

        except Exception:
            return None


# Convenience function
async def search_google_scholar(
    query: str,
    year_from: Optional[int] = None,
    limit: int = 20,
) -> ToolResult[list[Paper]]:
    """Convenience function to search Google Scholar."""
    tool = GoogleScholarSearchTool()
    return await tool.execute(
        query=query,
        year_from=year_from,
        limit=limit,
    )
