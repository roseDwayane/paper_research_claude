"""
SQLite database operations for the Research Agent.
"""

import json
import uuid
import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from src.config import config
from src.schemas.paper import Paper, Author, SourceAPI
from src.schemas.handoff_payload import (
    HandoffPayload,
    Gap,
    Concept,
    TargetJournal,
    HypothesisSpecification,
    ExpectedSignificance,
)


# SQL Schema
SCHEMA = """
-- Research session tracking
CREATE TABLE IF NOT EXISTS research_sessions (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',
    handoff_payload JSON
);

-- Paper storage with full provenance
CREATE TABLE IF NOT EXISTS papers (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES research_sessions(id),
    doi TEXT,
    pmid TEXT,
    openalex_id TEXT,
    title TEXT NOT NULL,
    authors JSON,
    year INTEGER,
    abstract TEXT,
    journal TEXT,
    source_api TEXT,
    raw_response JSON,
    relevance_score REAL,
    relevance_rationale TEXT,
    themes JSON,
    key_contributions JSON,
    citation_count INTEGER,
    is_open_access BOOLEAN DEFAULT FALSE,
    is_selected BOOLEAN DEFAULT FALSE,
    selection_reason TEXT,
    retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge graph nodes
CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES research_sessions(id),
    term TEXT NOT NULL,
    definition TEXT,
    relationships JSON
);

-- Identified gaps
CREATE TABLE IF NOT EXISTS gaps (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES research_sessions(id),
    title TEXT,
    description TEXT,
    evidence_paper_ids JSON,
    severity TEXT,
    novelty_potential TEXT
);

-- Hypotheses
CREATE TABLE IF NOT EXISTS hypotheses (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES research_sessions(id),
    problem_statement TEXT,
    research_questions JSON,
    hypothesis TEXT,
    theoretical_significance TEXT,
    practical_significance TEXT,
    scope_boundaries JSON
);

-- Target journals
CREATE TABLE IF NOT EXISTS target_journals (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES research_sessions(id),
    name TEXT,
    impact_factor REAL,
    review_cycle_days INTEGER,
    fit_rationale TEXT,
    style_guide_url TEXT,
    word_limit INTEGER
);

-- Debug/audit log
CREATE TABLE IF NOT EXISTS agent_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES research_sessions(id),
    agent_name TEXT,
    action TEXT,
    input_summary TEXT,
    output_summary TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_papers_session ON papers(session_id);
CREATE INDEX IF NOT EXISTS idx_papers_doi ON papers(doi);
CREATE INDEX IF NOT EXISTS idx_papers_selected ON papers(session_id, is_selected);
CREATE INDEX IF NOT EXISTS idx_gaps_session ON gaps(session_id);
CREATE INDEX IF NOT EXISTS idx_concepts_session ON concepts(session_id);
"""


class Database:
    """Async SQLite database wrapper for research data."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.storage.database_path
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """Connect to the database and ensure schema exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA)
        await self._conn.commit()

    async def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if not self._conn:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._conn

    # =========================================================================
    # Session Management
    # =========================================================================

    async def create_session(self, topic: str) -> str:
        """Create a new research session."""
        session_id = str(uuid.uuid4())
        await self.conn.execute(
            "INSERT INTO research_sessions (id, topic) VALUES (?, ?)",
            (session_id, topic),
        )
        await self.conn.commit()
        return session_id

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session by ID."""
        cursor = await self.conn.execute(
            "SELECT * FROM research_sessions WHERE id = ?", (session_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def update_session_status(self, session_id: str, status: str) -> None:
        """Update session status."""
        await self.conn.execute(
            "UPDATE research_sessions SET status = ? WHERE id = ?",
            (status, session_id),
        )
        await self.conn.commit()

    async def save_handoff_payload(
        self, session_id: str, payload: HandoffPayload
    ) -> None:
        """Save the complete handoff payload to the session."""
        payload_json = payload.model_dump_json()
        await self.conn.execute(
            "UPDATE research_sessions SET handoff_payload = ? WHERE id = ?",
            (payload_json, session_id),
        )
        await self.conn.commit()

    # =========================================================================
    # Paper Operations
    # =========================================================================

    async def save_paper(self, session_id: str, paper: Paper) -> None:
        """Save a paper to the database."""
        await self.conn.execute(
            """
            INSERT OR REPLACE INTO papers (
                id, session_id, doi, pmid, openalex_id, title, authors, year,
                abstract, journal, source_api, raw_response, relevance_score,
                relevance_rationale, themes, key_contributions, citation_count,
                is_open_access, is_selected, selection_reason, retrieved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                paper.id,
                session_id,
                paper.doi,
                paper.pmid,
                paper.openalex_id,
                paper.title,
                json.dumps([a.model_dump() for a in paper.authors]),
                paper.year,
                paper.abstract,
                paper.journal,
                paper.source_api.value,
                json.dumps(paper.raw_response) if paper.raw_response else None,
                paper.relevance_score,
                paper.relevance_rationale,
                json.dumps(paper.themes),
                json.dumps(paper.key_contributions),
                paper.citation_count,
                paper.is_open_access,
                paper.is_selected,
                paper.selection_reason,
                paper.retrieved_at.isoformat(),
            ),
        )
        await self.conn.commit()

    async def save_papers(self, session_id: str, papers: list[Paper]) -> None:
        """Save multiple papers."""
        for paper in papers:
            await self.save_paper(session_id, paper)

    async def get_papers(
        self,
        session_id: str,
        selected_only: bool = False,
        min_relevance: Optional[float] = None,
    ) -> list[Paper]:
        """Get papers for a session with optional filters."""
        query = "SELECT * FROM papers WHERE session_id = ?"
        params: list = [session_id]

        if selected_only:
            query += " AND is_selected = TRUE"
        if min_relevance is not None:
            query += " AND relevance_score >= ?"
            params.append(min_relevance)

        query += " ORDER BY relevance_score DESC"

        cursor = await self.conn.execute(query, params)
        rows = await cursor.fetchall()

        return [self._row_to_paper(row) for row in rows]

    def _row_to_paper(self, row: aiosqlite.Row) -> Paper:
        """Convert database row to Paper object."""
        authors_data = json.loads(row["authors"]) if row["authors"] else []
        authors = [Author(**a) for a in authors_data]

        return Paper(
            id=row["id"],
            doi=row["doi"],
            pmid=row["pmid"],
            openalex_id=row["openalex_id"],
            title=row["title"],
            authors=authors,
            year=row["year"],
            abstract=row["abstract"],
            journal=row["journal"],
            source_api=SourceAPI(row["source_api"]),
            relevance_score=row["relevance_score"],
            relevance_rationale=row["relevance_rationale"],
            themes=json.loads(row["themes"]) if row["themes"] else [],
            key_contributions=(
                json.loads(row["key_contributions"])
                if row["key_contributions"]
                else []
            ),
            citation_count=row["citation_count"],
            is_open_access=bool(row["is_open_access"]),
            is_selected=bool(row["is_selected"]),
            selection_reason=row["selection_reason"],
            retrieved_at=datetime.fromisoformat(row["retrieved_at"]),
        )

    async def update_paper_analysis(
        self,
        paper_id: str,
        relevance_score: float,
        relevance_rationale: str,
        themes: list[str],
        key_contributions: list[str],
    ) -> None:
        """Update paper with analysis results."""
        await self.conn.execute(
            """
            UPDATE papers SET
                relevance_score = ?,
                relevance_rationale = ?,
                themes = ?,
                key_contributions = ?
            WHERE id = ?
            """,
            (
                relevance_score,
                relevance_rationale,
                json.dumps(themes),
                json.dumps(key_contributions),
                paper_id,
            ),
        )
        await self.conn.commit()

    async def select_paper(
        self, paper_id: str, selected: bool, reason: Optional[str] = None
    ) -> None:
        """Mark paper as selected/deselected for the manifest."""
        await self.conn.execute(
            "UPDATE papers SET is_selected = ?, selection_reason = ? WHERE id = ?",
            (selected, reason, paper_id),
        )
        await self.conn.commit()

    # =========================================================================
    # Gap Operations
    # =========================================================================

    async def save_gap(self, session_id: str, gap: Gap) -> None:
        """Save an identified gap."""
        await self.conn.execute(
            """
            INSERT OR REPLACE INTO gaps (
                id, session_id, title, description, evidence_paper_ids,
                severity, novelty_potential
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                gap.gap_id,
                session_id,
                gap.title,
                gap.description,
                json.dumps(gap.evidence_papers),
                gap.severity.value,
                gap.novelty_potential.value,
            ),
        )
        await self.conn.commit()

    async def get_gaps(self, session_id: str) -> list[Gap]:
        """Get all gaps for a session."""
        cursor = await self.conn.execute(
            "SELECT * FROM gaps WHERE session_id = ?", (session_id,)
        )
        rows = await cursor.fetchall()

        from src.schemas.handoff_payload import Severity, NoveltyPotential

        return [
            Gap(
                gap_id=row["id"],
                title=row["title"],
                description=row["description"],
                evidence_papers=json.loads(row["evidence_paper_ids"]),
                severity=Severity(row["severity"]),
                novelty_potential=NoveltyPotential(row["novelty_potential"]),
            )
            for row in rows
        ]

    # =========================================================================
    # Concept Operations
    # =========================================================================

    async def save_concept(self, session_id: str, concept: Concept) -> None:
        """Save a knowledge graph concept."""
        concept_id = f"{session_id}:{concept.term}"
        await self.conn.execute(
            """
            INSERT OR REPLACE INTO concepts (id, session_id, term, definition, relationships)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                concept_id,
                session_id,
                concept.term,
                concept.definition,
                json.dumps(concept.relationships),
            ),
        )
        await self.conn.commit()

    async def get_concepts(self, session_id: str) -> list[Concept]:
        """Get all concepts for a session."""
        cursor = await self.conn.execute(
            "SELECT * FROM concepts WHERE session_id = ?", (session_id,)
        )
        rows = await cursor.fetchall()
        return [
            Concept(
                term=row["term"],
                definition=row["definition"],
                relationships=json.loads(row["relationships"]),
            )
            for row in rows
        ]

    # =========================================================================
    # Journal Operations
    # =========================================================================

    async def save_journal(self, session_id: str, journal: TargetJournal) -> None:
        """Save a target journal."""
        journal_id = f"{session_id}:{journal.name}"
        await self.conn.execute(
            """
            INSERT OR REPLACE INTO target_journals (
                id, session_id, name, impact_factor, review_cycle_days,
                fit_rationale, style_guide_url, word_limit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                journal_id,
                session_id,
                journal.name,
                journal.impact_factor,
                journal.review_cycle_days,
                journal.fit_rationale,
                journal.style_guide_url,
                journal.word_limit,
            ),
        )
        await self.conn.commit()

    async def get_journals(self, session_id: str) -> list[TargetJournal]:
        """Get all target journals for a session."""
        cursor = await self.conn.execute(
            "SELECT * FROM target_journals WHERE session_id = ?", (session_id,)
        )
        rows = await cursor.fetchall()
        return [
            TargetJournal(
                name=row["name"],
                impact_factor=row["impact_factor"],
                review_cycle_days=row["review_cycle_days"],
                fit_rationale=row["fit_rationale"],
                style_guide_url=row["style_guide_url"],
                word_limit=row["word_limit"],
            )
            for row in rows
        ]

    # =========================================================================
    # Logging
    # =========================================================================

    async def log_agent_action(
        self,
        session_id: str,
        agent_name: str,
        action: str,
        input_summary: str,
        output_summary: str,
    ) -> None:
        """Log an agent action for debugging/audit."""
        await self.conn.execute(
            """
            INSERT INTO agent_logs (session_id, agent_name, action, input_summary, output_summary)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, agent_name, action, input_summary, output_summary),
        )
        await self.conn.commit()

    # =========================================================================
    # Debug Export
    # =========================================================================

    async def export_debug_view(
        self, session_id: str, format: str = "markdown"
    ) -> str:
        """Export session data in human-readable format for debugging."""
        papers = await self.get_papers(session_id)
        selected_papers = [p for p in papers if p.is_selected]
        gaps = await self.get_gaps(session_id)

        if format == "markdown":
            lines = [
                f"# Research Session Debug View",
                f"",
                f"**Session ID:** {session_id}",
                f"**Total Papers:** {len(papers)}",
                f"**Selected Papers:** {len(selected_papers)}",
                f"**Gaps Identified:** {len(gaps)}",
                f"",
                f"## Selected Papers",
                f"",
            ]

            for i, paper in enumerate(selected_papers, 1):
                lines.append(f"### {i}. {paper.title}")
                lines.append(f"- **Year:** {paper.year}")
                lines.append(f"- **DOI:** {paper.doi or 'N/A'}")
                lines.append(f"- **Source:** {paper.source_api.value}")
                lines.append(f"- **Relevance:** {paper.relevance_score:.2f}")
                lines.append(f"- **Rationale:** {paper.relevance_rationale}")
                lines.append(f"- **Themes:** {', '.join(paper.themes)}")
                lines.append("")

            lines.append("## Identified Gaps")
            lines.append("")

            for gap in gaps:
                lines.append(f"### {gap.gap_id}: {gap.title}")
                lines.append(f"- **Severity:** {gap.severity.value}")
                lines.append(f"- **Description:** {gap.description}")
                lines.append(f"- **Evidence Papers:** {', '.join(gap.evidence_papers)}")
                lines.append("")

            return "\n".join(lines)

        elif format == "json":
            return json.dumps(
                {
                    "session_id": session_id,
                    "papers": [p.model_dump() for p in selected_papers],
                    "gaps": [g.model_dump() for g in gaps],
                },
                indent=2,
                default=str,
            )

        else:
            raise ValueError(f"Unknown format: {format}")


# Global database instance
_db: Optional[Database] = None


@asynccontextmanager
async def get_db():
    """Get a database connection context manager."""
    global _db
    if _db is None:
        _db = Database()
        await _db.connect()
    try:
        yield _db
    finally:
        pass  # Keep connection open for reuse
