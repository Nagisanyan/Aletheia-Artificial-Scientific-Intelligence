from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .types import Assumption, Conclusion, Evidence, Fact, Hypothesis, Inference, Observation, Uncertainty


class TaskStatus(str, Enum):
    CREATED = "CREATED"
    UNDERSTANDING = "UNDERSTANDING"
    REASONING = "REASONING"
    TOOL_EXECUTION = "TOOL_EXECUTION"
    VERIFICATION = "VERIFICATION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class TaskStateMachine:
    _ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
        TaskStatus.CREATED: {TaskStatus.UNDERSTANDING, TaskStatus.FAILED, TaskStatus.BLOCKED},
        TaskStatus.UNDERSTANDING: {TaskStatus.REASONING, TaskStatus.FAILED, TaskStatus.BLOCKED},
        TaskStatus.REASONING: {TaskStatus.TOOL_EXECUTION, TaskStatus.VERIFICATION, TaskStatus.FAILED, TaskStatus.BLOCKED},
        TaskStatus.TOOL_EXECUTION: {TaskStatus.VERIFICATION, TaskStatus.FAILED, TaskStatus.BLOCKED},
        TaskStatus.VERIFICATION: {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.BLOCKED},
        TaskStatus.COMPLETED: set(),
        TaskStatus.FAILED: set(),
        TaskStatus.BLOCKED: set(),
    }

    @classmethod
    def can_transition(cls, current: TaskStatus, target: TaskStatus) -> bool:
        return target in cls._ALLOWED_TRANSITIONS.get(current, set())

    @classmethod
    def transition(cls, current: TaskStatus, target: TaskStatus) -> TaskStatus:
        if not cls.can_transition(current, target):
            raise ValueError(f"Invalid transition from {current.value} to {target.value}")
        return target


@dataclass
class CognitiveState:
    task: str
    task_id: str = ""
    goal: str = ""
    context: str = ""
    known_facts: list[Fact] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    assumptions: list[Assumption] = field(default_factory=list)
    hypotheses: list[Hypothesis] = field(default_factory=list)
    reasoning_steps: list[Inference] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)
    observations: list[Observation] = field(default_factory=list)
    verification_results: list[Evidence] = field(default_factory=list)
    conclusion: str = ""
    uncertainty: str = "unknown"
    verification_status: str = "UNVERIFIED"
    status: TaskStatus = TaskStatus.CREATED
    history: list[str] = field(default_factory=list)

    def record_transition(self, new_status: TaskStatus) -> None:
        self.status = TaskStateMachine.transition(self.status, new_status)
        self.history.append(new_status.value)

    def add_fact(self, fact: Fact) -> None:
        self.known_facts.append(fact)

    def add_hypothesis(self, hypothesis: Hypothesis) -> None:
        self.hypotheses.append(hypothesis)

    def add_observation(self, observation: Observation) -> None:
        self.observations.append(observation)

    def add_verification_result(self, evidence: Evidence) -> None:
        self.verification_results.append(evidence)

    def add_reasoning_step(self, step: Inference) -> None:
        self.reasoning_steps.append(step)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "task_id": self.task_id,
            "goal": self.goal,
            "context": self.context,
            "known_facts": [item.to_dict() for item in self.known_facts],
            "unknowns": self.unknowns,
            "assumptions": [item.to_dict() for item in self.assumptions],
            "hypotheses": [item.to_dict() for item in self.hypotheses],
            "reasoning_steps": [item.to_dict() for item in self.reasoning_steps],
            "tool_calls": self.tool_calls,
            "observations": [item.to_dict() for item in self.observations],
            "verification_results": [item.to_dict() for item in self.verification_results],
            "conclusion": self.conclusion,
            "uncertainty": self.uncertainty,
            "verification_status": self.verification_status,
            "status": self.status.value,
            "history": self.history,
        }
