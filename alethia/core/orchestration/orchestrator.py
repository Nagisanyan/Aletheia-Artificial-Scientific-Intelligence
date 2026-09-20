from __future__ import annotations

import re
from uuid import uuid4

from alethia.core.cognition.cognitive_core import CognitiveCore
from alethia.core.cognition.cognitive_state import CognitiveState, TaskStatus
from alethia.core.reasoning.engine import ReasoningEngine
from alethia.mathematics.symbolic.engine import CounterexampleSearch, MathematicalEngine, MathematicalVerification
from alethia.memory.manager import MemoryManager
from alethia.tools.python.tool import PythonTool
from alethia.verification.logical.verifier import VerificationEngine


class Orchestrator:
    def __init__(
        self,
        cognitive_core: CognitiveCore | None = None,
        tool: PythonTool | None = None,
        verifier: VerificationEngine | None = None,
        memory_manager: MemoryManager | None = None,
    ):
        self.cognitive_core = cognitive_core or CognitiveCore()
        self.tool = tool or PythonTool(timeout=10.0)
        self.verifier = verifier or VerificationEngine()
        self.memory_manager = memory_manager or MemoryManager()
        self.reasoning_engine = ReasoningEngine()
        self.mathematical_engine = MathematicalEngine()
        self.mathematical_verifier = MathematicalVerification()
        self.counterexample_search = CounterexampleSearch()

    def run(self, task: str) -> CognitiveState:
        state = self.cognitive_core.create_state(task)
        state.task_id = f"task-{uuid4().hex[:8]}"
        state.context = self.memory_manager.retrieve_memory_context(task)

        state = self.cognitive_core.understand(state)
        state = self.cognitive_core.reason(state)

        trace = self.reasoning_engine.build_trace(task)
        state.history.append(f"FORMAL_TRACE:{trace.summary()}")
        state.context = state.context or "No relevant memory found."

        if any(keyword in task.lower() for keyword in ["learn", "remember", "previous", "history"]):
            memory_context = self.memory_manager.retrieve_memory_context(task)
            state = self.cognitive_core.conclude(
                state,
                f"Relevant memory: {memory_context}",
                confidence="supported",
                evidence="Retrieved previous task information from persistent memory.",
            )
            state.record_transition(TaskStatus.VERIFICATION)
            state = self.verifier.verify(state)
            state.record_transition(TaskStatus.COMPLETED)
            state.history.append("TASK_COMPLETED")
            state.status = TaskStatus.COMPLETED
            self.memory_manager.remember_working(state, "current_task", state.to_dict())
            self.memory_manager.consolidate_task(state)
            state.history.append("MEMORY_CONSOLIDATED")
            return state

        if "derivative" in task.lower():
            expression = self.cognitive_core._extract_derivative_expression(task)
            derivative_result = self.mathematical_engine.differentiate(expression)
            state.tool_calls.append(f"sympy.diff({expression}, x)")
            state = self.cognitive_core.observe(state, derivative_result.simplified, source="mathematical_engine")
            state = self.cognitive_core.conclude(
                state,
                derivative_result.simplified,
                confidence="verified",
                evidence=f"Derivative computed symbolically: {derivative_result.simplified}",
            )
            state.record_transition(TaskStatus.TOOL_EXECUTION)
            state.record_transition(TaskStatus.VERIFICATION)
            verification = self.verifier.verify(state)
            if verification.uncertainty in {"verified", "supported"}:
                verification.record_transition(TaskStatus.COMPLETED)
                verification.history.append("TASK_COMPLETED")
                verification.status = TaskStatus.COMPLETED
            else:
                verification.status = TaskStatus.FAILED
                verification.history.append("TASK_FAILED")
            self.memory_manager.remember_working(verification, "current_task", verification.to_dict())
            self.memory_manager.consolidate_task(verification)
            verification.history.append("MEMORY_CONSOLIDATED")
            return verification

        if "solve" in task.lower() or "=" in task.lower():
            equation = self.cognitive_core._extract_equation(task)
            equation_result = self.mathematical_engine.solve_linear(equation)
            state.tool_calls.append(f"sympy.solve({equation})")
            state = self.cognitive_core.observe(state, equation_result.simplified, source="mathematical_engine")
            state = self.cognitive_core.conclude(
                state,
                equation_result.simplified,
                confidence="verified",
                evidence=f"Equation solved symbolically: {equation_result.simplified}",
            )
            state.record_transition(TaskStatus.TOOL_EXECUTION)
            state.record_transition(TaskStatus.VERIFICATION)
            verification = self.verifier.verify(state)
            if verification.uncertainty in {"verified", "supported"}:
                verification.record_transition(TaskStatus.COMPLETED)
                verification.history.append("TASK_COMPLETED")
                verification.status = TaskStatus.COMPLETED
            else:
                verification.status = TaskStatus.FAILED
                verification.history.append("TASK_FAILED")
            self.memory_manager.remember_working(verification, "current_task", verification.to_dict())
            self.memory_manager.consolidate_task(verification)
            verification.history.append("MEMORY_CONSOLIDATED")
            return verification

        if "counterexample" in task.lower() or "disprove" in task.lower():
            expression = task.lower().replace("counterexample", "").replace("disprove", "").strip()
            counterexample = self.counterexample_search.search(expression or "x**2 > x")
            state = self.cognitive_core.conclude(
                state,
                str(counterexample),
                confidence="supported",
                evidence="Counterexample search executed on the supplied claim.",
            )
            state.record_transition(TaskStatus.VERIFICATION)
            state = self.verifier.verify(state)
            state.record_transition(TaskStatus.COMPLETED)
            return state

        state = self.cognitive_core.conclude(
            state,
            "No explicit tool route was identified from the current task.",
            confidence="uncertain",
            evidence="Task could not be mapped to a supported minimal tool pattern.",
        )
        state.status = TaskStatus.BLOCKED
        state.history.append("TASK_BLOCKED")
        return state

    def _build_derivative_code(self, expression: str) -> str:
        cleaned = self._normalize_expression(expression)
        return (
            "import sympy as sp\n"
            "x = sp.Symbol('x')\n"
            f"expr = {cleaned}\n"
            "print(sp.diff(expr, x).simplify())"
        )

    def _build_equation_code(self, equation: str) -> str:
        if "=" not in equation:
            equation = f"{equation} = 0"
        left, right = [piece.strip() for piece in equation.split("=", 1)]
        left_expr = self._normalize_expression(left)
        right_expr = self._normalize_expression(right)
        return (
            "import sympy as sp\n"
            "x = sp.Symbol('x')\n"
            f"solution = sp.solve(sp.Eq({left_expr}, {right_expr}), x)\n"
            "print(solution)"
        )

    def _normalize_expression(self, expression: str) -> str:
        normalized = expression.strip()
        normalized = normalized.replace("−", "-").replace("–", "-").replace("—", "-")
        normalized = normalized.replace("·", "*").replace("×", "*")
        normalized = normalized.replace("√", "sqrt").replace("π", "pi")
        normalized = normalized.replace("\n", " ")
        normalized = normalized.replace("sin", "sp.sin").replace("cos", "sp.cos")
        normalized = normalized.replace("exp", "sp.exp").replace("log", "sp.log")
        normalized = re.sub(r"(?<=\d)\s*(?=[A-Za-z])", "*", normalized)
        normalized = re.sub(r"(?P<num>\d+)(?P<var>[A-Za-z])", r"\g<num>*\g<var>", normalized)
        normalized = re.sub(r"(?P<base>[A-Za-z0-9\)])\^(?P<exp>\d+)", r"\g<base>**\g<exp>", normalized)
        normalized = normalized.replace("²", "**2").replace("³", "**3").replace("⁴", "**4")
        normalized = normalized.replace("⁵", "**5").replace("⁶", "**6").replace("⁷", "**7")
        normalized = normalized.replace("⁸", "**8").replace("⁹", "**9")
        normalized = normalized.replace("^", "**")
        normalized = re.sub(r"(?<![A-Za-z])x(?=\d)", "x*", normalized)
        return normalized.strip()
