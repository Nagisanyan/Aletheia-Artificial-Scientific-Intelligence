from __future__ import annotations

from alethia.core.reasoning.engine import ReasoningEngine
from alethia.mathematics.symbolic.engine import CounterexampleSearch, MathematicalEngine, MathematicalVerification


def test_reasoning_engine_builds_derivation_trace():
    engine = ReasoningEngine()
    trace = engine.build_trace("Solve x + 2 = 5", result="x = 3")

    assert trace.conclusion.content == "x = 3"
    assert trace.premises and trace.rules
    assert "Premise" in trace.summary()


def test_mathematical_engine_solves_simple_equation():
    engine = MathematicalEngine()
    result = engine.solve_linear("2*x + 4 = 10")

    assert result.success is True
    assert "x" in result.simplified


def test_mathematical_engine_differentiates_expression():
    engine = MathematicalEngine()
    result = engine.differentiate("x**2")

    assert result.success is True
    assert "2*x" in result.simplified


def test_mathematical_verification_returns_expected_status():
    verifier = MathematicalVerification()

    assert verifier.verify_claim("2 + 2 = 4", expected="2 + 2 = 4")["status"] == "VERIFIED"
    assert verifier.verify_claim("x = x")["status"] == "VERIFIED"


def test_counterexample_search_handles_basic_values():
    engine = CounterexampleSearch()
    result = engine.search("x**2 > x")

    assert result["status"] in {"CONTRADICTED", "NOT_DISPROVEN"}
