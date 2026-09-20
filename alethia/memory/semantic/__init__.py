from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SemanticKnowledge:
    knowledge_id: str
    statement: str
    kind: str = "FACT"
    domain: str = "general"
    confidence: str = "unknown"
    status: str = "UNVERIFIED"
    source: str = "internal"
    assumptions: list[str] = field(default_factory=list)
    related_concepts: list[str] = field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "knowledge_id": self.knowledge_id,
            "statement": self.statement,
            "kind": self.kind,
            "domain": self.domain,
            "confidence": self.confidence,
            "status": self.status,
            "source": self.source,
            "assumptions": self.assumptions,
            "related_concepts": self.related_concepts,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


__all__ = ["SemanticKnowledge"]
