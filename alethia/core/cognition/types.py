from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KnowledgeItem:
    id: str
    content: str
    source: str = "system"
    confidence: str = "unknown"
    status: str = "unverified"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "confidence": self.confidence,
            "status": self.status,
            "metadata": self.metadata,
        }


@dataclass
class Fact(KnowledgeItem):
    pass


@dataclass
class Hypothesis(KnowledgeItem):
    pass


@dataclass
class Assumption(KnowledgeItem):
    pass


@dataclass
class Observation(KnowledgeItem):
    pass


@dataclass
class Evidence(KnowledgeItem):
    pass


@dataclass
class Inference(KnowledgeItem):
    pass


@dataclass
class Uncertainty(KnowledgeItem):
    pass


@dataclass
class Conclusion(KnowledgeItem):
    pass
