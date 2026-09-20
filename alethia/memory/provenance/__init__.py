from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProvenanceRelation:
    source_id: str
    target_id: str
    relation_type: str
    created_at: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "created_at": self.created_at,
        }


__all__ = ["ProvenanceRelation"]
