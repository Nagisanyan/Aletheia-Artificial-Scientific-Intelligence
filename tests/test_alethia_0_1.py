from __future__ import annotations

import pytest

from alethia.core.cognition.cognitive_state import CognitiveState, TaskStateMachine, TaskStatus
from alethia.core.cognition.types import Fact, Hypothesis, Inference
from alethia.core.orchestration.orchestrator import Orchestrator
from alethia.memory.working_memory import WorkingMemory
from alethia.tools.python.tool import PythonTool
from alethia.verification.logical.verifier import VerificationEngine


def test_cognitive_state_and_machine():
    state = CognitiveState(task="Solve 2x + 4 = 10")
    assert state.status == TaskStatus.CREATED
    state.record_transition(TaskStatus.UNDERSTANDING)
    assert state.status == TaskStatus.UNDERSTANDING
    assert TaskStateMachine.can_transition(TaskStatus.UNDERSTANDING, TaskStatus.REASONING)
    with pytest.raises(ValueError):
        state.record_transition(TaskStatus.COMPLETED)


def test_working_memory_crud_and_isolation():
    state_a = CognitiveState(task="Task A", task_id="task-a")
    state_b = CognitiveState(task="Task B", task_id="task-b")

    memory = WorkingMemory(state_a)
    memory.add("goal", "solve equation", task_id="task-a")
    memory.add("goal", "differentiate expression", task_id="task-b")

    assert memory.get("goal", task_id="task-a") == "solve equation"
    assert memory.get("goal", task_id="task-b") == "differentiate expression"

    memory.update("goal", "new answer", task_id="task-a")
    assert memory.get("goal", task_id="task-a") == "new answer"

    removed = memory.remove("goal", task_id="task-a")
    assert removed == "new answer"
    assert memory.get("goal", task_id="task-a") is None

    snapshot = memory.snapshot(task_id="task-b")
    assert snapshot == {"goal": "differentiate expression"}

    memory.clear(task_id="task-b")
    assert memory.snapshot(task_id="task-b") == {}


def test_python_tool_success_and_blocked_execution():
    tool = PythonTool(timeout=2.0)
    result = tool.execute("print(2 + 2)")
    assert result.succeeded is True
    assert result.stdout == "4"

    blocked = tool.execute("import os; os.system('echo blocked')")
    assert blocked.blocked is True
    assert blocked.succeeded is False

    blocked_eval = tool.execute("eval('print(123)')")
    assert blocked_eval.blocked is True

    timeout_result = tool.execute("import time; time.sleep(2)")
    assert timeout_result.succeeded is False


def test_verification_logic():
    state = CognitiveState(task="Check logic")
    state.conclusion = "x = 3"
    state.reasoning_steps.append(Inference(id="inf-1", content="Solve the equation", source="test", confidence="supported", status="inference"))
    state.unknowns = []

    verification = VerificationEngine().verify(state)
    assert verification.uncertainty in {"verified", "supported"}
    assert verification.verification_status in {"VALID", "UNVERIFIED"}

    contradiction_state = CognitiveState(task="Contradiction check")
    contradiction_state.conclusion = "x = 3"
    contradiction_state.known_facts.append(Fact(id="fact-1", content="not x = 3", source="test", confidence="supported", status="fact"))
    contradiction_state.reasoning_steps.append(Inference(id="inf-2", content="This conclusion conflicts with existing data", source="test", confidence="supported", status="inference"))
    contradiction_state.unknowns = []

    contradicted = VerificationEngine().verify(contradiction_state)
    assert contradicted.uncertainty == "contradictory"
    assert contradicted.verification_status == "CONTRADICTORY"

    unproven = CognitiveState(task="Needs evidence")
    unproven.conclusion = "x = 42"
    unproven.unknowns = []
    unproven_check = VerificationEngine().verify(unproven)
    assert unproven_check.verification_status == "INSUFFICIENT_EVIDENCE"


def test_hypothesis_is_not_treated_as_fact():
    state = CognitiveState(task="Hypothesis test")
    hypothesis = Hypothesis(id="hyp-1", content="The system may be wrong.", source="test", confidence="uncertain", status="hypothesis")
    state.add_hypothesis(hypothesis)
    assert hypothesis in state.hypotheses
    assert hypothesis not in state.known_facts


def test_orchestrator_derivative_task():
    orchestrator = Orchestrator()
    result = orchestrator.run("Calculate the derivative of x² + 3x + 2")
    assert result.status == TaskStatus.COMPLETED
    assert "2*x + 3" in result.conclusion


def test_orchestrator_equation_task():
    orchestrator = Orchestrator()
    result = orchestrator.run("Solve 2x + 4 = 10")
    assert result.status == TaskStatus.COMPLETED
    assert "3" in result.conclusion


def test_orchestrator_handles_generalized_cases():
    orchestrator = Orchestrator()
    for task, expected in [
        ("Solve 3x + 7 = 22", "5"),
        ("Solve 5x - 10 = 15", "5"),
        ("Calculate the derivative of x^3 + 2x", "3*x**2 + 2"),
    ]:
        result = orchestrator.run(task)
        assert result.status == TaskStatus.COMPLETED
        assert expected in result.conclusion
