from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class MemoryRepository:
    """SQLite-backed repository for Aletheia 0.2 memory layers."""

    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            db_path = Path(__file__).resolve().parents[2] / "alethia_memory.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS working_memory (
                    task_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS episodic_memory (
                    episode_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    task TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    actions TEXT,
                    tool_calls TEXT,
                    observations TEXT,
                    verification TEXT,
                    conclusion TEXT,
                    outcome TEXT,
                    uncertainty TEXT,
                    metadata TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_memory (
                    knowledge_id TEXT PRIMARY KEY,
                    statement TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    domain TEXT,
                    confidence TEXT,
                    status TEXT,
                    source TEXT,
                    assumptions TEXT,
                    related_concepts TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS procedural_memory (
                    procedure_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    content TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS provenance (
                    relation_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scientific_knowledge (
                    knowledge_id TEXT PRIMARY KEY,
                    statement TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    domain TEXT,
                    subdomain TEXT,
                    concepts TEXT,
                    variables TEXT,
                    constants TEXT,
                    equations TEXT,
                    assumptions TEXT,
                    constraints TEXT,
                    conditions TEXT,
                    status TEXT,
                    confidence TEXT,
                    provenance TEXT,
                    relations TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scientific_relations (
                    relation_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save_working_memory(self, task_id: str, payload: dict[str, Any]) -> None:
        entry = json.dumps(payload, sort_keys=True)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO working_memory(task_id, payload, updated_at) VALUES(?, ?, datetime('now')) ON CONFLICT(task_id) DO UPDATE SET payload = excluded.payload, updated_at = datetime('now')",
                (task_id, entry),
            )

    def load_working_memory(self, task_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM working_memory WHERE task_id = ?", (task_id,)).fetchone()
        if row is None:
            return {}
        return json.loads(row["payload"])

    def remove_working_memory(self, task_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM working_memory WHERE task_id = ?", (task_id,))

    def save_episode(self, episode: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO episodic_memory(
                    episode_id, timestamp, task, goal, actions, tool_calls, observations,
                    verification, conclusion, outcome, uncertainty, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(episode_id) DO UPDATE SET
                    timestamp = excluded.timestamp,
                    task = excluded.task,
                    goal = excluded.goal,
                    actions = excluded.actions,
                    tool_calls = excluded.tool_calls,
                    observations = excluded.observations,
                    verification = excluded.verification,
                    conclusion = excluded.conclusion,
                    outcome = excluded.outcome,
                    uncertainty = excluded.uncertainty,
                    metadata = excluded.metadata
                """,
                (
                    episode["episode_id"],
                    episode["timestamp"],
                    episode["task"],
                    episode["goal"],
                    json.dumps(episode.get("actions", []), sort_keys=True),
                    json.dumps(episode.get("tool_calls", []), sort_keys=True),
                    json.dumps(episode.get("observations", []), sort_keys=True),
                    json.dumps(episode.get("verification", {}), sort_keys=True),
                    json.dumps(episode.get("conclusion", {}), sort_keys=True),
                    episode.get("outcome", ""),
                    episode.get("uncertainty", "unknown"),
                    json.dumps(episode.get("metadata", {}), sort_keys=True),
                ),
            )

    def list_episodes(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM episodic_memory ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_episode(row) for row in rows]

    def search_episodes(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        text = f"%{query.lower()}%"
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM episodic_memory
                WHERE lower(task) LIKE ? OR lower(goal) LIKE ? OR lower(outcome) LIKE ?
                ORDER BY timestamp DESC LIMIT ?
                """,
                (text, text, text, limit),
            ).fetchall()
        return [self._row_to_episode(row) for row in rows]

    def save_knowledge(self, knowledge: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO semantic_memory(
                    knowledge_id, statement, kind, domain, confidence, status, source,
                    assumptions, related_concepts, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                ON CONFLICT(knowledge_id) DO UPDATE SET
                    statement = excluded.statement,
                    kind = excluded.kind,
                    domain = excluded.domain,
                    confidence = excluded.confidence,
                    status = excluded.status,
                    source = excluded.source,
                    assumptions = excluded.assumptions,
                    related_concepts = excluded.related_concepts,
                    updated_at = datetime('now')
                """,
                (
                    knowledge["knowledge_id"],
                    knowledge.get("statement", ""),
                    knowledge.get("kind", "FACT"),
                    knowledge.get("domain", "general"),
                    knowledge.get("confidence", "unknown"),
                    knowledge.get("status", "UNVERIFIED"),
                    knowledge.get("source", "internal"),
                    json.dumps(knowledge.get("assumptions", []), sort_keys=True),
                    json.dumps(knowledge.get("related_concepts", []), sort_keys=True),
                ),
            )

    def search_knowledge(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        term = f"%{query.lower()}%"
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM semantic_memory
                WHERE lower(statement) LIKE ? OR lower(kind) LIKE ?
                ORDER BY updated_at DESC LIMIT ?
                """,
                (term, term, limit),
            ).fetchall()
        return [self._row_to_knowledge(row) for row in rows]

    def save_provenance(self, source_id: str, target_id: str, relation_type: str) -> None:
        relation_id = f"prov-{source_id}-{target_id}-{relation_type}"
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO provenance(relation_id, source_id, target_id, relation_type, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
                (relation_id, source_id, target_id, relation_type),
            )

    def get_provenance(self, knowledge_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM provenance WHERE source_id = ? OR target_id = ? ORDER BY created_at DESC",
                (knowledge_id, knowledge_id),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_procedure(self, procedure: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO procedural_memory(procedure_id, name, description, content, created_at, updated_at)
                VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
                ON CONFLICT(procedure_id) DO UPDATE SET
                    name = excluded.name,
                    description = excluded.description,
                    content = excluded.content,
                    updated_at = datetime('now')
                """,
                (
                    procedure["procedure_id"],
                    procedure.get("name", ""),
                    procedure.get("description", ""),
                    json.dumps(procedure.get("content", {}), sort_keys=True),
                ),
            )

    def list_procedures(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM procedural_memory ORDER BY updated_at DESC").fetchall()
        return [dict(row) for row in rows]

    def save_scientific_knowledge(self, knowledge: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO scientific_knowledge(
                    knowledge_id, statement, kind, domain, subdomain, concepts, variables,
                    constants, equations, assumptions, constraints, conditions, status,
                    confidence, provenance, relations, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                ON CONFLICT(knowledge_id) DO UPDATE SET
                    statement = excluded.statement,
                    kind = excluded.kind,
                    domain = excluded.domain,
                    subdomain = excluded.subdomain,
                    concepts = excluded.concepts,
                    variables = excluded.variables,
                    constants = excluded.constants,
                    equations = excluded.equations,
                    assumptions = excluded.assumptions,
                    constraints = excluded.constraints,
                    conditions = excluded.conditions,
                    status = excluded.status,
                    confidence = excluded.confidence,
                    provenance = excluded.provenance,
                    relations = excluded.relations,
                    updated_at = datetime('now')
                """,
                (
                    knowledge["knowledge_id"],
                    knowledge.get("statement", ""),
                    knowledge.get("kind", "DEFINITION"),
                    knowledge.get("domain", "general"),
                    knowledge.get("subdomain", "general"),
                    json.dumps(knowledge.get("concepts", []), sort_keys=True),
                    json.dumps(knowledge.get("variables", []), sort_keys=True),
                    json.dumps(knowledge.get("constants", []), sort_keys=True),
                    json.dumps(knowledge.get("equations", []), sort_keys=True),
                    json.dumps(knowledge.get("assumptions", []), sort_keys=True),
                    json.dumps(knowledge.get("constraints", []), sort_keys=True),
                    json.dumps(knowledge.get("conditions", []), sort_keys=True),
                    knowledge.get("status", "UNVERIFIED"),
                    knowledge.get("confidence", "unknown"),
                    json.dumps(knowledge.get("provenance", {}), sort_keys=True),
                    json.dumps(knowledge.get("relations", []), sort_keys=True),
                ),
            )

    def search_scientific_knowledge(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        term = f"%{query.lower()}%"
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM scientific_knowledge
                WHERE lower(statement) LIKE ? OR lower(kind) LIKE ? OR lower(domain) LIKE ? OR lower(subdomain) LIKE ?
                ORDER BY updated_at DESC LIMIT ?
                """,
                (term, term, term, term, limit),
            ).fetchall()
        return [self._row_to_scientific_knowledge(row) for row in rows]

    def save_scientific_relation(self, relation_id: str, source_id: str, target_id: str, relation_type: str, metadata: dict[str, Any] | None = None) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO scientific_relations(relation_id, source_id, target_id, relation_type, metadata, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
                (relation_id, source_id, target_id, relation_type, json.dumps(metadata or {}, sort_keys=True)),
            )

    def list_scientific_relations(self, knowledge_id: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as conn:
            if knowledge_id is None:
                rows = conn.execute("SELECT * FROM scientific_relations ORDER BY created_at DESC").fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM scientific_relations WHERE source_id = ? OR target_id = ? ORDER BY created_at DESC",
                    (knowledge_id, knowledge_id),
                ).fetchall()
        return [dict(row) for row in rows]

    def _row_to_episode(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "episode_id": row["episode_id"],
            "timestamp": row["timestamp"],
            "task": row["task"],
            "goal": row["goal"],
            "actions": json.loads(row["actions"] or "[]"),
            "tool_calls": json.loads(row["tool_calls"] or "[]"),
            "observations": json.loads(row["observations"] or "[]"),
            "verification": json.loads(row["verification"] or "{}"),
            "conclusion": json.loads(row["conclusion"] or "{}"),
            "outcome": row["outcome"],
            "uncertainty": row["uncertainty"],
            "metadata": json.loads(row["metadata"] or "{}"),
        }

    def _row_to_knowledge(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "knowledge_id": row["knowledge_id"],
            "statement": row["statement"],
            "kind": row["kind"],
            "domain": row["domain"],
            "confidence": row["confidence"],
            "status": row["status"],
            "source": row["source"],
            "assumptions": json.loads(row["assumptions"] or "[]"),
            "related_concepts": json.loads(row["related_concepts"] or "[]"),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _row_to_scientific_knowledge(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "knowledge_id": row["knowledge_id"],
            "statement": row["statement"],
            "kind": row["kind"],
            "domain": row["domain"],
            "subdomain": row["subdomain"],
            "concepts": json.loads(row["concepts"] or "[]"),
            "variables": json.loads(row["variables"] or "[]"),
            "constants": json.loads(row["constants"] or "[]"),
            "equations": json.loads(row["equations"] or "[]"),
            "assumptions": json.loads(row["assumptions"] or "[]"),
            "constraints": json.loads(row["constraints"] or "[]"),
            "conditions": json.loads(row["conditions"] or "[]"),
            "status": row["status"],
            "confidence": row["confidence"],
            "provenance": json.loads(row["provenance"] or "{}"),
            "relations": json.loads(row["relations"] or "[]"),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
