"""
PubMed/NCBI API search tool.

PubMed is a free search engine for biomedical and life sciences literature.
https://www.ncbi.nlm.nih.gov/home/develop/api/
"""

import uuid
import asyncio
import xml.etree.ElementTree as ET
from typing import Optional
from datetime import datetime

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import config
from src.tools.base import BaseTool, ToolResult
from src.schemas.paper import Paper, Author, SourceAPI


class PubMedSearchTool(BaseTool):
    """Search PubMed/NCBI for biomedical literature."""

    name = "search_pubmed"
    description = "Search PubMed for biomedical and life sciences literature. Best for medical, biological, and health-related research."

    ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    def __init__(self):
        self.api_key = config.api.ncbi_api_key
        self.email = config.api.ncbi_email

    def _get_parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query terms",
                },
                "mesh_terms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "MeSH terms for filtering",
                },
                "date_range": {
                    "type": "string",
                    "description": "Date range in format 'YYYY:YYYY' (e.g., '2020:2024')",
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
    async def _fetch(self, url: str, params: dict) -> str:
        """Fetch from NCBI API with retry logic."""
        async with httpx.AsyncClient() as client:
            # Add API key and email if configured
            if self.api_key:
                params["api_key"] = self.api_key
            if self.email:
                params["email"] = self.email

            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.text

    async def execute(
        self,
        query: str,
        mesh_terms: Optional[list[str]] = None,
        date_range: Optional[str] = None,
        limit: int = 50,
    ) -> ToolResult[list[Paper]]:
        """
        Execute PubMed search.

        Args:
            query: Search terms
            mesh_terms: MeSH terms for filtering
            date_range: Date range as 'YYYY:YYYY'
            limit: Max results

        Returns:
            ToolResult containing list of Paper objects
        """
        try:
            # Build search query
            search_query = query

            if mesh_terms:
                mesh_query = " AND ".join(f'"{term}"[MeSH Terms]' for term in mesh_terms)
                search_query = f"({search_query}) AND ({mesh_query})"

            # Search parameters
            search_params = {
                "db": "pubmed",
                "term": search_query,
                "retmax": min(limit, 100),
                "retmode": "json",
                "sort": "relevance",
            }

            if date_range:
                try:
                    start_year, end_year = date_range.split(":")
                    search_params["mindate"] = f"{start_year}/01/01"
                    search_params["maxdate"] = f"{end_year}/12/31"
                    search_params["datetype"] = "pdat"
                except ValueError:
                    pass

            # Step 1: Search for PMIDs
            search_response = await self._fetch(self.ESEARCH_URL, search_params)

            import json
            search_data = json.loads(search_response)
            pmids = search_data.get("esearchresult", {}).get("idlist", [])

            if not pmids:
                return ToolResult.ok([], total_results=0, query=query, source="pubmed")

            # Step 2: Fetch article details
            await asyncio.sleep(config.agent.api_delay_seconds)

            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml",
                "rettype": "abstract",
            }

            fetch_response = await self._fetch(self.EFETCH_URL, fetch_params)

            # Parse XML response
            papers = self._parse_pubmed_xml(fetch_response)

            await asyncio.sleep(config.agent.api_delay_seconds)

            return ToolResult.ok(
                papers,
                total_results=int(
                    search_data.get("esearchresult", {}).get("count", len(papers))
                ),
                query=query,
                source="pubmed",
            )

        except httpx.HTTPStatusError as e:
            return ToolResult.fail(f"PubMed API error: {e.response.status_code}")
        except Exception as e:
            return ToolResult.fail(f"PubMed search failed: {str(e)}")

    def _parse_pubmed_xml(self, xml_text: str) -> list[Paper]:
        """Parse PubMed XML response into Paper objects."""
        papers = []

        try:
            root = ET.fromstring(xml_text)

            for article in root.findall(".//PubmedArticle"):
                paper = self._parse_article(article)
                if paper:
                    papers.append(paper)

        except ET.ParseError:
            pass

        return papers

    def _parse_article(self, article: ET.Element) -> Optional[Paper]:
        """Parse a single PubMed article."""
        try:
            medline = article.find("MedlineCitation")
            if medline is None:
                return None

            article_data = medline.find("Article")
            if article_data is None:
                return None

            # PMID
            pmid_elem = medline.find("PMID")
            pmid = pmid_elem.text if pmid_elem is not None else None

            # Title
            title_elem = article_data.find("ArticleTitle")
            title = title_elem.text if title_elem is not None else "Untitled"

            # Authors
            authors = []
            author_list = article_data.find("AuthorList")
            if author_list is not None:
                for author in author_list.findall("Author")[:10]:
                    last_name = author.find("LastName")
                    first_name = author.find("ForeName")
                    if last_name is not None:
                        name = last_name.text
                        if first_name is not None:
                            name = f"{first_name.text} {name}"
                        authors.append(Author(name=name))

            # Abstract
            abstract_elem = article_data.find(".//AbstractText")
            abstract = abstract_elem.text if abstract_elem is not None else None

            # Journal
            journal_elem = article_data.find(".//Journal/Title")
            journal = journal_elem.text if journal_elem is not None else None

            # Year
            year = None
            pub_date = article_data.find(".//PubDate/Year")
            if pub_date is not None and pub_date.text:
                try:
                    year = int(pub_date.text)
                except ValueError:
                    pass

            # DOI
            doi = None
            for article_id in article.findall(".//ArticleIdList/ArticleId"):
                if article_id.get("IdType") == "doi":
                    doi = article_id.text
                    break

            return Paper(
                id=f"pubmed_{uuid.uuid4().hex[:12]}",
                pmid=pmid,
                doi=doi,
                title=title,
                authors=authors,
                year=year,
                abstract=abstract,
                journal=journal,
                source_api=SourceAPI.PUBMED,
                source_url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None,
            )

        except Exception:
            return None


# Convenience function
async def search_pubmed(
    query: str,
    mesh_terms: Optional[list[str]] = None,
    date_range: Optional[str] = None,
    limit: int = 50,
) -> ToolResult[list[Paper]]:
    """Convenience function to search PubMed."""
    tool = PubMedSearchTool()
    return await tool.execute(
        query=query,
        mesh_terms=mesh_terms,
        date_range=date_range,
        limit=limit,
    )
