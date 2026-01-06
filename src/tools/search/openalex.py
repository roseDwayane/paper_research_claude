"""
OpenAlex API search tool.

OpenAlex is a free, open catalog of the global research system.
https://docs.openalex.org/
"""

import uuid
import asyncio
from typing import Optional
from datetime import datetime

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import config
from src.tools.base import BaseTool, ToolResult
from src.schemas.paper import Paper, Author, SourceAPI


class OpenAlexSearchTool(BaseTool):
    """Search OpenAlex for academic papers."""

    name = "search_openalex"
    description = "Search OpenAlex API for academic papers. Returns papers with DOIs, abstracts, and citation counts."

    BASE_URL = "https://api.openalex.org"

    def __init__(self):
        self.email = config.api.openalex_email

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
                "year_to": {
                    "type": "integer",
                    "description": "Filter papers up to this year",
                },
                "cited_by_count_min": {
                    "type": "integer",
                    "description": "Minimum citation count",
                },
                "open_access": {
                    "type": "boolean",
                    "description": "Filter to only open access papers",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 50)",
                    "default": 50,
                },
            },
            "required": ["query"],
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _fetch(self, url: str, params: dict) -> dict:
        """Fetch from OpenAlex API with retry logic."""
        async with httpx.AsyncClient() as client:
            # Add polite email if configured
            if self.email:
                params["mailto"] = self.email

            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()

    async def execute(
        self,
        query: str,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        cited_by_count_min: Optional[int] = None,
        open_access: Optional[bool] = None,
        limit: int = 50,
    ) -> ToolResult[list[Paper]]:
        """
        Execute OpenAlex search.

        Args:
            query: Search terms
            year_from: Start year filter
            year_to: End year filter
            cited_by_count_min: Minimum citations
            open_access: Filter to OA only
            limit: Max results

        Returns:
            ToolResult containing list of Paper objects
        """
        try:
            # Build filter string
            filters = []
            if year_from and year_to:
                filters.append(f"publication_year:{year_from}-{year_to}")
            elif year_from:
                filters.append(f"publication_year:>{year_from - 1}")
            elif year_to:
                filters.append(f"publication_year:<{year_to + 1}")

            if cited_by_count_min:
                filters.append(f"cited_by_count:>{cited_by_count_min - 1}")

            if open_access:
                filters.append("is_oa:true")

            # Build request params
            params = {
                "search": query,
                "per_page": min(limit, 200),  # OpenAlex max is 200
                "sort": "relevance_score:desc",
            }

            if filters:
                params["filter"] = ",".join(filters)

            # Fetch results
            data = await self._fetch(f"{self.BASE_URL}/works", params)

            # Parse results
            papers = []
            for work in data.get("results", []):
                paper = self._parse_work(work)
                if paper:
                    papers.append(paper)

            await asyncio.sleep(config.agent.api_delay_seconds)

            return ToolResult.ok(
                papers,
                total_results=data.get("meta", {}).get("count", 0),
                query=query,
                source="openalex",
            )

        except httpx.HTTPStatusError as e:
            return ToolResult.fail(f"OpenAlex API error: {e.response.status_code}")
        except Exception as e:
            return ToolResult.fail(f"OpenAlex search failed: {str(e)}")

    def _parse_work(self, work: dict) -> Optional[Paper]:
        """Parse OpenAlex work object into Paper."""
        try:
            # Extract authors
            authors = []
            for authorship in work.get("authorships", [])[:10]:  # Limit to 10 authors
                author_data = authorship.get("author", {})
                if author_data.get("display_name"):
                    authors.append(
                        Author(
                            name=author_data["display_name"],
                            orcid=author_data.get("orcid"),
                            affiliation=(
                                authorship.get("institutions", [{}])[0].get(
                                    "display_name"
                                )
                                if authorship.get("institutions")
                                else None
                            ),
                        )
                    )

            # Extract DOI
            doi = work.get("doi")
            if doi and doi.startswith("https://doi.org/"):
                doi = doi.replace("https://doi.org/", "")

            # Get journal/source
            primary_location = work.get("primary_location") or {}
            source = primary_location.get("source") or {}

            return Paper(
                id=f"openalex_{uuid.uuid4().hex[:12]}",
                doi=doi,
                openalex_id=work.get("id"),
                title=work.get("title") or work.get("display_name", "Untitled"),
                authors=authors,
                year=work.get("publication_year"),
                abstract=self._reconstruct_abstract(work.get("abstract_inverted_index")),
                journal=source.get("display_name"),
                citation_count=work.get("cited_by_count", 0),
                is_open_access=work.get("open_access", {}).get("is_oa", False),
                source_api=SourceAPI.OPENALEX,
                source_url=work.get("id"),
                raw_response=work,
            )
        except Exception:
            return None

    def _reconstruct_abstract(self, inverted_index: Optional[dict]) -> Optional[str]:
        """
        Reconstruct abstract from OpenAlex inverted index format.

        OpenAlex stores abstracts as {word: [positions]} for space efficiency.
        """
        if not inverted_index:
            return None

        try:
            # Find max position
            max_pos = 0
            for positions in inverted_index.values():
                if positions:
                    max_pos = max(max_pos, max(positions))

            # Build word list
            words = [""] * (max_pos + 1)
            for word, positions in inverted_index.items():
                for pos in positions:
                    words[pos] = word

            return " ".join(words).strip()
        except Exception:
            return None


# Convenience function for direct use
async def search_openalex(
    query: str,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    cited_by_count_min: Optional[int] = None,
    open_access: Optional[bool] = None,
    limit: int = 50,
) -> ToolResult[list[Paper]]:
    """Convenience function to search OpenAlex."""
    tool = OpenAlexSearchTool()
    return await tool.execute(
        query=query,
        year_from=year_from,
        year_to=year_to,
        cited_by_count_min=cited_by_count_min,
        open_access=open_access,
        limit=limit,
    )
