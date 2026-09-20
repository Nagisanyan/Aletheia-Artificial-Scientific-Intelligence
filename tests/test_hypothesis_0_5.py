from __future__ import annotations

from alethia.core.hypotheses.engine import HypothesisEngine, HypothesisStatus, ResearchQuestion


def test_hypothesis_generation_from_question():
    engine = HypothesisEngine()
    question = ResearchQuestion(
        question_id="q-1",
        statement="Why does the observed value differ from the predicted value?",
        domain="physics",
        known_information=["A known law exists."],
        unknowns=["missing condition"],
        constraints=["use the current model"],
        related_knowledge=["law: F = m*a"],
    )

    hypothesis = engine.generate_from_question(question, knowledge=["F = m*a"])

    assert hypothesis.statement.startswith("The question")
    assert hypothesis.status == HypothesisStatus.PROPOSED
    assert hypothesis.falsifiable is True


def test_hypothesis_generation_from_contradiction():
    engine = HypothesisEngine()
    hypothesis = engine.generate_from_contradiction("x = 2", "x = 3")

    assert hypothesis.premises == ["x = 2", "x = 3"]
    assert hypothesis.status == HypothesisStatus.PROPOSED
    assert hypothesis.predictions


def test_hypothesis_evaluation_statuses():
    engine = HypothesisEngine()
    question = ResearchQuestion(
        question_id="q-2",
        statement="Does the simplified model remain valid?",
        domain="mathematics",
        known_information=["The baseline model is known."],
        unknowns=["validity domain"],
        constraints=["assume local approximation"],
    )
    hypothesis = engine.generate_from_question(question, knowledge=["local approximation"])

    evaluation = engine.evaluate(hypothesis, evidence=["the approximation matches observation"], counterevidence=[])
    assert evaluation.status == HypothesisStatus.SUPPORTED

    contradicted = engine.evaluate(hypothesis, evidence=[], counterevidence=["the condition is violated"])
    assert contradicted.status == HypothesisStatus.CONTRADICTED


def test_hypothesis_record_serialization():
    engine = HypothesisEngine()
    question = ResearchQuestion(
        question_id="q-3",
        statement="Can the assumption be relaxed?",
        domain="physics",
        known_information=["Assumption is currently fixed."],
        unknowns=["new domain"],
        constraints=["keep the model simple"],
    )
    hypothesis = engine.generate_from_question(question)

    payload = hypothesis.to_dict()
    assert payload["hypothesis_id"]
    assert payload["status"] == HypothesisStatus.PROPOSED.value
    assert payload["predictions"][0]["statement"]
