from __future__ import annotations

from alethia.core.cognition.cognitive_state import CognitiveState
from alethia.core.cognition.types import Assumption, Fact, Inference
from alethia.verification.logical.verifier import VerificationEngine, VerificationResult, VerificationStatus, VerificationTargetType
from alethia.verification.self_criticism import SelfCriticismEngine


def test_verification_result_model_contains_required_fields():
    result = VerificationResult(
        verification_id="vr-1",
        target_id="claim-1",
        target_type=VerificationTargetType.CLAIM.value,
        status=VerificationStatus.VERIFIED,
        checks=["provenance check"],
        evidence=["basic consistency observed"],
        contradictions=[],
        counterexamples=[],
        assumptions=["the model is valid"],
        provenance={"source": "unit_test"},
        confidence="medium",
        limitations=["not externally validated"],
        explanation="The result is coherent.",
    )

    payload = result.to_dict()
    assert payload["verification_id"] == "vr-1"
    assert payload["status"] == VerificationStatus.VERIFIED.value
    assert payload["assumptions"] == ["the model is valid"]


def test_verification_engine_detects_contradictions_and_evidence_gap():
    state = CognitiveState(task="Self-check contradiction")
    state.conclusion = "x = 2"
    state.known_facts.append(Fact(id="fact-1", content="not x = 2", source="test", confidence="supported", status="fact"))
    state.reasoning_steps.append(Inference(id="inf-1", content="This is a direct derivation", source="test", confidence="supported", status="inference"))

    contradictory = VerificationEngine().verify(state)
    assert contradictory.verification_status == VerificationStatus.CONTRADICTORY.value
    assert contradictory.uncertainty == "contradictory"

    incomplete = CognitiveState(task="Self-check insufficiency")
    incomplete.conclusion = "hypothesis remains plausible"
    incomplete.reasoning_steps = []
    insufficient = VerificationEngine().verify(incomplete)
    assert insufficient.verification_status == VerificationStatus.INSUFFICIENT_EVIDENCE.value


def test_self_critique_classifies_conclusion_reliability():
    state = CognitiveState(task="Critique conclusion")
    state.task_id = "task-critique"
    state.conclusion = "The model is acceptable."
    state.reasoning_steps.append(Inference(id="inf-1", content="Reasoning trace present", source="test", confidence="supported", status="inference"))
    state.assumptions.append(Assumption(id="ass-1", content="the assumptions hold", source="test", confidence="supported", status="assumption"))

    critique = SelfCriticismEngine().critique(state)
    assert critique.status in {VerificationStatus.VERIFIED, VerificationStatus.SUPPORTED}
    assert critique.provenance["task"] == "Critique conclusion"


def test_verification_target_evaluation_supports_explicit_provenance():
    result = VerificationEngine().verify_target(
        "The claim x = 3 is true under assumption A.",
        target_type=VerificationTargetType.CLAIM,
        provenance={"target_id": "claim-42", "source": "unit_test"},
        assumptions=["A is valid"],
    )

    assert result.target_id == "claim-42"
    assert result.target_type == VerificationTargetType.CLAIM.value
    assert result.assumptions == ["A is valid"]
    assert result.explanation
