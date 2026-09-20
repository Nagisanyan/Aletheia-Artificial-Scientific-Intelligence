from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Procedure:
    procedure_id: str
    name: str
    description: str = ""
    content: dict[str, Any] = field(default_factory=dict)
    created_at: str | None = None
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "procedure_id": self.procedure_id,
            "name": self.name,
            "description": self.description,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


__all__ = ["Procedure"]
