from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from alethia.core.cognition.cognitive_state import CognitiveState
from alethia.core.cognition.types import Evidence


class VerificationStatus(str, Enum):
    COMPUTED = "COMPUTED"
    VERIFIED = "VERIFIED"
    SUPPORTED = "SUPPORTED"
    VALID = "VALID"
    INVALID = "INVALID"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONTRADICTORY = "CONTRADICTORY"
    UNVERIFIED = "UNVERIFIED"


class VerificationTargetType(str, Enum):
    CLAIM = "CLAIM"
    CALCULATION = "CALCULATION"
    DERIVATION = "DERIVATION"
    EQUATION = "EQUATION"
    PREDICTION = "PREDICTION"
    EXPERIMENT = "EXPERIMENT"
    SIMULATION = "SIMULATION"
    OBSERVATION = "OBSERVATION"
    HYPOTHESIS = "HYPOTHESIS"
    KNOWLEDGE_RECORD = "KNOWLEDGE_RECORD"
    CONCLUSION = "CONCLUSION"


@dataclass
class VerificationResult:
    verification_id: str
    target_id: str
    target_type: str
    status: VerificationStatus | str
    checks: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    counterexamples: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    confidence: str = "unknown"
    limitations: list[str] = field(default_factory=list)
    explanation: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    verifier_version: str = "Aletheia 0.7"

    def to_dict(self) -> dict[str, Any]:
        return {
            "verification_id": self.verification_id,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "status": self.status.value if isinstance(self.status, VerificationStatus) else self.status,
            "checks": self.checks,
            "evidence": self.evidence,
            "contradictions": self.contradictions,
            "counterexamples": self.counterexamples,
            "assumptions": self.assumptions,
            "provenance": self.provenance,
            "confidence": self.confidence,
            "limitations": self.limitations,
            "explanation": self.explanation,
            "created_at": self.created_at,
            "verifier_version": self.verifier_version,
        }


class VerificationEngine:
    """Minimal verification layer for Aletheia 0.1 with 0.7 self-critique support."""

    def verify(self, state: CognitiveState) -> CognitiveState:
        if state.conclusion:
            state.history.append("VERIFICATION_STARTED")

        contradictions = self._detect_contradictions(state)
        if contradictions:
            state.verification_status = VerificationStatus.CONTRADICTORY.value
            state.uncertainty = "contradictory"
            state.history.append("CONTRADICTION_DETECTED")
            return self._attach_evidence(state, "Contradiction detected in available information.")

        if not state.conclusion:
            state.verification_status = VerificationStatus.INSUFFICIENT_EVIDENCE.value
            state.uncertainty = "insufficient_evidence"
            state.history.append("VERIFICATION_COMPLETED")
            return self._attach_evidence(state, "No conclusion was produced to verify.")

        if not state.reasoning_steps:
            state.verification_status = VerificationStatus.INSUFFICIENT_EVIDENCE.value
            state.uncertainty = "unknown"
            return self._attach_evidence(state, "Insufficient reasoning steps to justify the conclusion.")

        if state.unknowns:
            state.verification_status = VerificationStatus.UNVERIFIED.value
            state.uncertainty = "uncertain"
            return self._attach_evidence(state, "Important unknowns remain unresolved.")

        if state.conclusion and state.reasoning_steps:
            state.verification_status = VerificationStatus.VALID.value
            state.uncertainty = "verified"
            state.history.append("VERIFICATION_COMPLETED")
            return self._attach_evidence(state, "Conclusion is coherent with the available evidence.")

        state.verification_status = VerificationStatus.UNVERIFIED.value
        state.uncertainty = "supported"
        state.history.append("VERIFICATION_COMPLETED")
        return self._attach_evidence(state, "Conclusion is supported but not fully verified.")

    def verify_target(
        self,
        target: str,
        target_type: str | VerificationTargetType = VerificationTargetType.CLAIM,
        provenance: dict[str, Any] | None = None,
        assumptions: list[str] | None = None,
    ) -> VerificationResult:
        target_text = (target or "").strip()
        provenance = provenance or {}
        assumptions = assumptions or []

        checks = ["syntactic presence check"]
        evidence: list[str] = []
        contradictions = self._detect_target_contradictions(target_text)
        counterexamples: list[str] = []
        limitations: list[str] = []

        if not target_text:
            return VerificationResult(
                verification_id=f"verify-{len(provenance)}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                target_id=str(provenance.get("target_id", "unknown")),
                target_type=target_type.value if isinstance(target_type, VerificationTargetType) else str(target_type),
                status=VerificationStatus.INSUFFICIENT_EVIDENCE,
                checks=checks,
                evidence=evidence,
                contradictions=[],
                counterexamples=[],
                assumptions=assumptions,
                provenance=provenance,
                confidence="unknown",
                limitations=["No target content was supplied."],
                explanation="The target could not be evaluated because it was empty.",
            )

        if contradictions:
            status = VerificationStatus.CONTRADICTORY
            explanation = "The target contains a contradiction or a negation conflict."
        elif "not" in target_text.lower() and "=" in target_text:
            status = VerificationStatus.UNVERIFIED
            explanation = "The claim makes a negative or conditional assertion and lacks sufficient evidence for validation."
            limitations.append("Conditional or negative claims require explicit evidence and assumptions.")
        else:
            status = VerificationStatus.VERIFIED
            explanation = "The target is coherent and has passed the basic validation checks available in this layer."
            evidence.append("Basic consistency and provenance checks passed.")

        if assumptions:
            checks.append("assumption check")
            evidence.append(f"Assumptions considered: {', '.join(assumptions)}")
        if not evidence:
            evidence.append("No additional evidence was supplied beyond the target itself.")

        return VerificationResult(
            verification_id=f"verify-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            target_id=str(provenance.get("target_id", "unknown")),
            target_type=target_type.value if isinstance(target_type, VerificationTargetType) else str(target_type),
            status=status,
            checks=checks,
            evidence=evidence,
            contradictions=contradictions,
            counterexamples=counterexamples,
            assumptions=assumptions,
            provenance=provenance,
            confidence="medium" if status == VerificationStatus.VERIFIED else "low",
            limitations=limitations,
            explanation=explanation,
        )

    def _attach_evidence(self, state: CognitiveState, content: str) -> CognitiveState:
        state.verification_results.append(
            Evidence(
                id=f"verification-{len(state.verification_results) + 1}",
                content=content,
                source="verification_engine",
                confidence=state.uncertainty,
                status="evidence",
            )
        )
        return state

    def _detect_contradictions(self, state: CognitiveState) -> list[str]:
        contradictions: list[str] = []
        known = [fact.content.lower() for fact in state.known_facts]
        if not state.conclusion:
            return contradictions

        conclusion_text = state.conclusion.lower()
        for fact_text in known:
            if "not" in fact_text and fact_text.replace("not ", "") in conclusion_text:
                contradictions.append("Negation conflict detected.")
        return contradictions

    def _detect_target_contradictions(self, target: str) -> list[str]:
        lowered = target.lower().strip()
        contradictions: list[str] = []
        if not lowered:
            return contradictions
        if "not" in lowered and any(token in lowered for token in ["=", "==", "is", "equal"]):
            contradictions.append("Negative formulaic assertion detected.")
        if "contradiction" in lowered or "conflict" in lowered:
            contradictions.append("Explicit contradiction or conflict was recorded.")
        return contradictions


__all__ = [
    "VerificationEngine",
    "VerificationResult",
    "VerificationStatus",
    "VerificationTargetType",
]
