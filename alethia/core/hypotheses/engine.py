from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class HypothesisStatus(str, Enum):
    PROPOSED = "PROPOSED"
    UNDER_EVALUATION = "UNDER_EVALUATION"
    SUPPORTED = "SUPPORTED"
    WEAKLY_SUPPORTED = "WEAKLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    FALSIFIED = "FALSIFIED"
    UNRESOLVED = "UNRESOLVED"
    REJECTED = "REJECTED"


class HypothesisSource(str, Enum):
    OBSERVATION = "OBSERVATION"
    CONTRADICTION = "CONTRADICTION"
    KNOWLEDGE_GAP = "KNOWLEDGE_GAP"
    PATTERN = "PATTERN"
    DERIVATION = "DERIVATION"
    MODEL_COMPARISON = "MODEL_COMPARISON"
    USER_PROPOSAL = "USER_PROPOSAL"
    SIMULATION_RESULT = "SIMULATION_RESULT"


@dataclass
class Prediction:
    prediction_id: str
    statement: str
    equation: str | None = None
    expected_value: str | None = None
    expected_range: str | None = None
    conditions: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "statement": self.statement,
            "equation": self.equation,
            "expected_value": self.expected_value,
            "expected_range": self.expected_range,
            "conditions": self.conditions,
            "assumptions": self.assumptions,
            "provenance": self.provenance,
            "created_at": self.created_at,
        }


@dataclass
class HypothesisRecord:
    hypothesis_id: str
    statement: str
    domain: str = "general"
    subdomain: str = "general"
    concepts: list[str] = field(default_factory=list)
    premises: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    motivation: str = ""
    predictions: list[Prediction] = field(default_factory=list)
    expected_observations: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    counterevidence: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    confidence: str = "unknown"
    falsifiable: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "statement": self.statement,
            "domain": self.domain,
            "subdomain": self.subdomain,
            "concepts": self.concepts,
            "premises": self.premises,
            "assumptions": self.assumptions,
            "constraints": self.constraints,
            "motivation": self.motivation,
            "predictions": [item.to_dict() for item in self.predictions],
            "expected_observations": self.expected_observations,
            "evidence": self.evidence,
            "counterevidence": self.counterevidence,
            "provenance": self.provenance,
            "status": self.status.value,
            "confidence": self.confidence,
            "falsifiable": self.falsifiable,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class ResearchQuestion:
    question_id: str
    statement: str
    domain: str = "general"
    known_information: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    related_knowledge: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "question_id": self.question_id,
            "statement": self.statement,
            "domain": self.domain,
            "known_information": self.known_information,
            "unknowns": self.unknowns,
            "constraints": self.constraints,
            "related_knowledge": self.related_knowledge,
            "provenance": self.provenance,
            "created_at": self.created_at,
        }


@dataclass
class HypothesisEvaluation:
    hypothesis_id: str
    status: HypothesisStatus
    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    unresolved_items: list[str] = field(default_factory=list)
    evaluated_predictions: list[str] = field(default_factory=list)
    reasoning_trace: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "status": self.status.value,
            "supporting_evidence": self.supporting_evidence,
            "contradicting_evidence": self.contradicting_evidence,
            "unresolved_items": self.unresolved_items,
            "evaluated_predictions": self.evaluated_predictions,
            "reasoning_trace": self.reasoning_trace,
            "provenance": self.provenance,
            "timestamp": self.timestamp,
        }


class HypothesisEngine:
    """Minimal hypothesis generation and evaluation layer for Aletheia 0.5."""

    def generate_from_question(self, question: ResearchQuestion, knowledge: list[str] | None = None) -> HypothesisRecord:
        knowledge = knowledge or []
        hypothesis = HypothesisRecord(
            hypothesis_id=f"hyp-{len(knowledge) + 1}",
            statement=f"The question '{question.statement}' can be explained by a structured causal relation within {question.domain}.",
            domain=question.domain,
            subdomain=question.domain,
            concepts=[question.statement.lower()],
            premises=knowledge,
            assumptions=["the available knowledge is relevant"],
            constraints=question.constraints,
            motivation="Derived from a research question and existing context.",
            predictions=[
                Prediction(
                    prediction_id="pred-1",
                    statement="The relevant pattern explains the requested outcome under the stated conditions.",
                    equation=None,
                    expected_value="Unknown without additional evaluation.",
                    expected_range=None,
                    conditions=question.constraints,
                    assumptions=["the available knowledge is relevant"],
                    provenance={"source": "question_generation"},
                )
            ],
            expected_observations=["The model explains the observed pattern."],
            evidence=[],
            counterevidence=[],
            provenance={"source": "question_generation", "question_id": question.question_id},
            status=HypothesisStatus.PROPOSED,
            confidence="proposed",
            falsifiable=True,
        )
        return hypothesis

    def generate_from_contradiction(self, left: str, right: str) -> HypothesisRecord:
        return HypothesisRecord(
            hypothesis_id=f"hyp-contradiction-{abs(hash(left + right))}",
            statement=f"The apparent contradiction between '{left}' and '{right}' can be resolved by a missing validity condition.",
            domain="general",
            subdomain="general",
            concepts=[left.lower(), right.lower()],
            premises=[left, right],
            assumptions=["the contradiction is due to an omitted condition"],
            constraints=[],
            motivation="Contradictory statements suggest a hidden constraint or domain restriction.",
            predictions=[
                Prediction(
                    prediction_id="pred-contradiction-1",
                    statement="A missing validity condition resolves the contradiction.",
                    expected_value="Condition discovered during further analysis.",
                    conditions=["missing validity condition"],
                    assumptions=["the contradiction is not fundamental"],
                    provenance={"source": "contradiction_generation"},
                )
            ],
            expected_observations=["The contradiction disappears when the missing condition is added."],
            evidence=[],
            counterevidence=[],
            provenance={"source": "contradiction_generation"},
            status=HypothesisStatus.PROPOSED,
            confidence="proposed",
            falsifiable=True,
        )

    def evaluate(self, hypothesis: HypothesisRecord, evidence: list[str] | None = None, counterevidence: list[str] | None = None) -> HypothesisEvaluation:
        evidence = evidence or hypothesis.evidence
        counterevidence = counterevidence or hypothesis.counterevidence
        status = HypothesisStatus.UNRESOLVED

        if counterevidence:
            status = HypothesisStatus.CONTRADICTED
        elif evidence:
            status = HypothesisStatus.SUPPORTED
        elif hypothesis.assumptions:
            status = HypothesisStatus.UNDER_EVALUATION

        return HypothesisEvaluation(
            hypothesis_id=hypothesis.hypothesis_id,
            status=status,
            supporting_evidence=evidence,
            contradicting_evidence=counterevidence,
            unresolved_items=["need additional evidence or falsification tests"],
            evaluated_predictions=[p.statement for p in hypothesis.predictions],
            reasoning_trace=[f"Evaluated hypothesis: {hypothesis.statement}"],
            provenance={"source": "hypothesis_evaluation", "status": status.value},
        )


__all__ = [
    "HypothesisStatus",
    "HypothesisSource",
    "Prediction",
    "HypothesisRecord",
    "ResearchQuestion",
    "HypothesisEvaluation",
    "HypothesisEngine",
]
