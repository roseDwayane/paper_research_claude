"""
Configuration management for the Research Agent.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class APIConfig:
    """API configuration for external services."""

    # Anthropic (Claude)
    anthropic_api_key: str = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", "")
    )
    claude_model: str = field(
        default_factory=lambda: os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    )

    # OpenAlex (free, no key required but email recommended)
    openalex_email: str = field(
        default_factory=lambda: os.getenv("OPENALEX_EMAIL", "")
    )

    # PubMed/NCBI
    ncbi_api_key: str = field(
        default_factory=lambda: os.getenv("NCBI_API_KEY", "")
    )
    ncbi_email: str = field(
        default_factory=lambda: os.getenv("NCBI_EMAIL", "")
    )

    # SerpAPI (for Google Scholar)
    serpapi_key: str = field(
        default_factory=lambda: os.getenv("SERPAPI_KEY", "")
    )


@dataclass
class StorageConfig:
    """Storage configuration."""

    base_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv("RESEARCH_AGENT_DATA_DIR", "./data")
        )
    )

    @property
    def database_path(self) -> Path:
        return self.base_dir / "research.db"

    @property
    def outputs_dir(self) -> Path:
        return self.base_dir / "outputs"

    def ensure_dirs(self) -> None:
        """Create necessary directories if they don't exist."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class AgentConfig:
    """Agent behavior configuration."""

    # Search settings
    max_papers_per_source: int = 50
    min_relevance_score: float = 0.6
    target_paper_count: int = 25

    # Analysis settings
    max_concepts_in_graph: int = 30
    target_gaps: int = 3
    target_journals: int = 5

    # Rate limiting
    api_delay_seconds: float = 0.5


@dataclass
class Config:
    """Main configuration container."""

    api: APIConfig = field(default_factory=APIConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)

    def __post_init__(self):
        self.storage.ensure_dirs()


# Global config instance
config = Config()
