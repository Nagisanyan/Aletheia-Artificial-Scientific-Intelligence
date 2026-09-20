from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ScientificKnowledgeType(str, Enum):
    DEFINITION = "DEFINITION"
    LAW = "LAW"
    THEORY = "THEORY"
    MODEL = "MODEL"
    EQUATION = "EQUATION"
    OBSERVATION = "OBSERVATION"
    EXPERIMENT = "EXPERIMENT"
    CONSTANT = "CONSTANT"
    VARIABLE = "VARIABLE"
    HYPOTHESIS = "HYPOTHESIS"
    THEOREM = "THEOREM"
    PROPOSITION = "PROPOSITION"
    CONJECTURE = "CONJECTURE"
    ASSUMPTION = "ASSUMPTION"
    CONSTRAINT = "CONSTRAINT"
    MEASUREMENT = "MEASUREMENT"


class ScientificKnowledgeStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    ASSUMED = "ASSUMED"
    PROPOSED = "PROPOSED"
    UNVERIFIED = "UNVERIFIED"
    SUPPORTED = "SUPPORTED"
    VERIFIED = "VERIFIED"
    CONTRADICTED = "CONTRADICTED"
    REJECTED = "REJECTED"


class ScientificDomain(str, Enum):
    MATHEMATICS = "MATHEMATICS"
    PHYSICS = "PHYSICS"
    CLASSICAL_MECHANICS = "CLASSICAL_MECHANICS"
    CHEMISTRY = "CHEMISTRY"
    BIOLOGY = "BIOLOGY"
    COMPUTATIONAL_SCIENCE = "COMPUTATIONAL_SCIENCE"
    GENERAL = "GENERAL"


class KnowledgeRelation(str, Enum):
    RELATED_TO = "RELATED_TO"
    DERIVED_FROM = "DERIVED_FROM"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    SPECIALIZES = "SPECIALIZES"
    GENERALIZES = "GENERALIZES"
    USES = "USES"
    DEPENDS_ON = "DEPENDS_ON"
    PREDICTS = "PREDICTS"
    OBSERVED_BY = "OBSERVED_BY"
    DEFINED_BY = "DEFINED_BY"
    EXPRESSED_BY = "EXPRESSED_BY"


@dataclass
class ScientificKnowledge:
    knowledge_id: str
    statement: str
    kind: ScientificKnowledgeType | str
    domain: ScientificDomain | str
    subdomain: str = "general"
    concepts: list[str] = field(default_factory=list)
    variables: list[str] = field(default_factory=list)
    constants: list[str] = field(default_factory=list)
    equations: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    status: ScientificKnowledgeStatus | str = ScientificKnowledgeStatus.UNVERIFIED
    confidence: str = "unknown"
    provenance: dict[str, Any] = field(default_factory=dict)
    relations: list[str] = field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "knowledge_id": self.knowledge_id,
            "statement": self.statement,
            "kind": self.kind.value if isinstance(self.kind, ScientificKnowledgeType) else self.kind,
            "domain": self.domain.value if isinstance(self.domain, ScientificDomain) else self.domain,
            "subdomain": self.subdomain,
            "concepts": self.concepts,
            "variables": self.variables,
            "constants": self.constants,
            "equations": self.equations,
            "assumptions": self.assumptions,
            "constraints": self.constraints,
            "conditions": self.conditions,
            "status": self.status.value if isinstance(self.status, ScientificKnowledgeStatus) else self.status,
            "confidence": self.confidence,
            "provenance": self.provenance,
            "relations": self.relations,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


__all__ = [
    "ScientificKnowledge",
    "ScientificKnowledgeType",
    "ScientificKnowledgeStatus",
    "ScientificDomain",
    "KnowledgeRelation",
]
