from __future__ import annotations

import re
from uuid import uuid4

from .cognitive_state import CognitiveState, TaskStatus
from .types import Assumption, Evidence, Fact, Hypothesis, Inference, Observation


class CognitiveCore:
    """Minimal deterministic cognitive layer for Aletheia 0.1."""

    def create_state(self, task: str) -> CognitiveState:
        state = CognitiveState(task=task, task_id=f"task-{uuid4().hex[:8]}")
        state.history.append("TASK_CREATED")
        return state

    def understand(self, state: CognitiveState) -> CognitiveState:
        state.record_transition(TaskStatus.UNDERSTANDING)
        state.history.append("UNDERSTANDING_STARTED")
        task_lower = state.task.lower()

        if "derivative" in task_lower:
            state.goal = "Differentiate the expression with respect to x."
        elif "solve" in task_lower or "=" in task_lower:
            state.goal = "Solve the equation for the unknown variable."
        else:
            state.goal = "Answer the user task with explicit reasoning and verification."

        state.context = "Minimal scientific reasoning loop for Aletheia 0.1."
        state.known_facts.extend(
            [
                Fact(
                    id=f"fact-{uuid4().hex[:6]}",
                    content=f"Request type identified: {task_lower}",
                    source="task",
                    confidence="supported",
                    status="fact",
                )
            ]
        )

        if not state.goal:
            state.unknowns.append("The requested action is not explicit enough to determine a method.")

        if "derivative" in task_lower:
            state.assumptions.append(
                Assumption(
                    id=f"assumption-{uuid4().hex[:6]}",
                    content="The task requires differentiation with respect to x unless another variable is specified.",
                    source="task_analysis",
                    confidence="supported",
                    status="assumption",
                )
            )
        elif "solve" in task_lower or "=" in task_lower:
            state.assumptions.append(
                Assumption(
                    id=f"assumption-{uuid4().hex[:6]}",
                    content="The equation should be solved symbolically if a single-variable algebraic solution exists.",
                    source="task_analysis",
                    confidence="supported",
                    status="assumption",
                )
            )

        state.history.append("UNDERSTANDING_COMPLETED")
        return state

    def reason(self, state: CognitiveState) -> CognitiveState:
        state.record_transition(TaskStatus.REASONING)
        state.history.append("REASONING_STARTED")

        task = state.task
        task_lower = task.lower()
        if "derivative" in task_lower:
            expression = self._extract_derivative_expression(task)
            state.hypotheses.append(
                Hypothesis(
                    id=f"hypothesis-{uuid4().hex[:6]}",
                    content=f"The expression {expression} should be differentiated symbolically.",
                    source="reasoning",
                    confidence="supported",
                    status="hypothesis",
                )
            )
            state.reasoning_steps.append(
                Inference(
                    id=f"inference-{uuid4().hex[:6]}",
                    content="Use the power rule and linearity of differentiation to compute the derivative.",
                    source="reasoning",
                    confidence="supported",
                    status="inference",
                )
            )
        elif "solve" in task_lower or "=" in task_lower:
            equation = self._extract_equation(task)
            state.hypotheses.append(
                Hypothesis(
                    id=f"hypothesis-{uuid4().hex[:6]}",
                    content=f"The equation {equation} can be solved algebraically for the unknown variable.",
                    source="reasoning",
                    confidence="supported",
                    status="hypothesis",
                )
            )
            state.reasoning_steps.append(
                Inference(
                    id=f"inference-{uuid4().hex[:6]}",
                    content="Isolate the variable by moving constants and dividing by the coefficient.",
                    source="reasoning",
                    confidence="supported",
                    status="inference",
                )
            )
        else:
            state.hypotheses.append(
                Hypothesis(
                    id=f"hypothesis-{uuid4().hex[:6]}",
                    content="A direct reasoning or tool-assisted approach is required.",
                    source="reasoning",
                    confidence="uncertain",
                    status="hypothesis",
                )
            )

        state.history.append("REASONING_COMPLETED")
        return state

    def observe(self, state: CognitiveState, content: str, source: str = "tool") -> CognitiveState:
        state.observations.append(
            Observation(
                id=f"observation-{uuid4().hex[:6]}",
                content=content,
                source=source,
                confidence="supported",
                status="observation",
            )
        )
        return state

    def conclude(
        self,
        state: CognitiveState,
        content: str,
        confidence: str = "verified",
        evidence: str | None = None,
    ) -> CognitiveState:
        state.conclusion = content
        state.uncertainty = confidence
        if evidence:
            state.verification_results.append(
                Evidence(
                    id=f"evidence-{uuid4().hex[:6]}",
                    content=evidence,
                    source="verification",
                    confidence=confidence,
                    status="evidence",
                )
            )
        return state

    def _extract_derivative_expression(self, task: str) -> str:
        match = re.search(r"derivative\s+of\s*(.+)", task, flags=re.IGNORECASE)
        if match:
            expression = match.group(1).strip().rstrip(".")
        else:
            expression = task
        return self._normalize_expression(expression)

    def _extract_equation(self, task: str) -> str:
        match = re.search(r"(?:solve|Solve)\s*(?:[:=\-])?\s*(.+)", task, flags=re.IGNORECASE)
        if match:
            return self._normalize_expression(match.group(1).strip())
        return self._normalize_expression(task)

    def _normalize_expression(self, expression: str) -> str:
        normalized = expression.strip()
        normalized = normalized.replace("−", "-").replace("–", "-").replace("—", "-")
        normalized = normalized.replace("·", "*").replace("×", "*")
        normalized = normalized.replace("√", "sqrt").replace("π", "pi")
        normalized = normalized.replace("\n", " ")
        normalized = re.sub(r"(?<=\d)\s*(?=[A-Za-z])", "*", normalized)
        normalized = re.sub(r"(?P<num>\d+)(?P<var>[A-Za-z])", r"\g<num>*\g<var>", normalized)
        normalized = re.sub(r"(?P<base>[A-Za-z0-9\)])\^(?P<exp>\d+)", r"\g<base>**\g<exp>", normalized)
        normalized = normalized.replace("²", "**2").replace("³", "**3").replace("⁴", "**4")
        normalized = normalized.replace("⁵", "**5").replace("⁶", "**6").replace("⁷", "**7")
        normalized = normalized.replace("⁸", "**8").replace("⁹", "**9")
        normalized = normalized.replace("^", "**")
        normalized = re.sub(r"(?<![A-Za-z])x(?=\d)", "x*", normalized)
        normalized = re.sub(r"(?<=\d)\s*\*\s*(?=[A-Za-z])", "*", normalized)
        return normalized.strip()
