from __future__ import annotations

from typing import Any

from alethia.core.cognition.cognitive_state import CognitiveState
from alethia.verification.logical.verifier import VerificationEngine, VerificationResult, VerificationStatus


class SelfCriticismEngine:
    """Aletheia 0.7 critique layer for checking the reliability of its own outputs."""

    def __init__(self, verifier: VerificationEngine | None = None):
        self.verifier = verifier or VerificationEngine()

    def critique(self, state: CognitiveState, target_type: str = "CONCLUSION") -> VerificationResult:
        checks: list[str] = []
        evidence: list[str] = []
        contradictions = self.verifier._detect_contradictions(state)
        assumptions = [item.content for item in state.assumptions]
        uncertainty = state.uncertainty or "supported"

        if not state.conclusion:
            status = VerificationStatus.INSUFFICIENT_EVIDENCE
            explanation = "The result was not produced, so there is no basis for evaluation."
        elif contradictions:
            status = VerificationStatus.CONTRADICTORY
            explanation = "The expected result conflicts with recorded facts or prior information."
        elif not state.reasoning_steps:
            status = VerificationStatus.INSUFFICIENT_EVIDENCE
            explanation = "The output lacks enough reasoning steps to justify confidence."
        elif state.unknowns:
            status = VerificationStatus.UNVERIFIED
            explanation = "Unresolved unknowns mean the conclusion should remain provisional."
        elif uncertainty in {"verified", "supported"}:
            status = VerificationStatus.VERIFIED if uncertainty == "verified" else VerificationStatus.SUPPORTED
            explanation = "The result passed the minimal critique checks available in the current framework."
        else:
            status = VerificationStatus.SUPPORTED
            explanation = "The result is coherent enough to be treated as supported, though not fully proven."

        checks.append("trace presence check")
        if state.reasoning_steps:
            checks.append("reasoning sufficiency check")
            evidence.append(f"Reasoning steps: {len(state.reasoning_steps)}")
        if assumptions:
            checks.append("assumption review")
            evidence.append(f"Assumptions reviewed: {', '.join(assumptions)}")
        if contradictions:
            evidence.extend(contradictions)

        return VerificationResult(
            verification_id=f"critique-{state.task_id or 'unknown'}",
            target_id=state.task_id or state.task,
            target_type=target_type,
            status=status,
            checks=checks,
            evidence=evidence,
            contradictions=contradictions,
            counterexamples=[],
            assumptions=assumptions,
            provenance={"task": state.task, "status": state.status.value},
            confidence=uncertainty,
            limitations=["No secure external validation backend is available in this version."] if status != VerificationStatus.CONTRADICTORY else ["Contradiction detected; interpretation is limited."],
            explanation=explanation,
        )

    def examine(self, target: Any, target_type: str = "CLAIM") -> VerificationResult:
        text = str(target).strip() if target is not None else ""
        return self.verifier.verify_target(text, target_type=target_type, provenance={"target_type": target_type})
