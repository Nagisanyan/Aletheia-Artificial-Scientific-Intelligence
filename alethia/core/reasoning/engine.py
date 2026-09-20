from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class FormalKnowledge:
    identifier: str
    content: str
    kind: str
    source: str = "system"
    provenance: list[str] = field(default_factory=list)
    epistemic_status: str = "UNVERIFIED"
    dependencies: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "identifier": self.identifier,
            "content": self.content,
            "kind": self.kind,
            "source": self.source,
            "provenance": self.provenance,
            "epistemic_status": self.epistemic_status,
            "dependencies": self.dependencies,
            "created_at": self.created_at,
        }


@dataclass
class DerivationTrace:
    premises: list[FormalKnowledge]
    rules: list[FormalKnowledge]
    derivation_steps: list[str]
    conclusion: FormalKnowledge

    def summary(self) -> str:
        return " | ".join(self.derivation_steps) + f" => {self.conclusion.content}"


class ReasoningEngine:
    """Minimal formal reasoning layer for Aletheia 0.3."""

    def build_trace(self, task: str, result: str | None = None) -> DerivationTrace:
        label = task.strip()
        premise_text = self._extract_premise(label)
        conclusion_text = result or self._extract_conclusion(label)

        premise = FormalKnowledge(
            identifier="premise-1",
            content=premise_text,
            kind="Premise",
            source="task",
            provenance=["user_input"],
            epistemic_status="SUPPORTED",
            dependencies=[],
        )

        rule = FormalKnowledge(
            identifier="rule-1",
            content="Apply the relevant symbolic or algebraic transformation to derive the result.",
            kind="Rule",
            source="reasoning_engine",
            provenance=["internal_derivation"],
            epistemic_status="SUPPORTED",
            dependencies=[premise.identifier],
        )

        steps = [
            f"Premise: {premise.content}",
            f"Rule: {rule.content}",
            f"Result: {conclusion_text}",
        ]

        conclusion = FormalKnowledge(
            identifier="conclusion-1",
            content=conclusion_text,
            kind="Conclusion",
            source="reasoning_engine",
            provenance=["internal_derivation"],
            epistemic_status="VERIFIED" if result else "UNVERIFIED",
            dependencies=[premise.identifier, rule.identifier],
        )

        return DerivationTrace(
            premises=[premise],
            rules=[rule],
            derivation_steps=steps,
            conclusion=conclusion,
        )

    def _extract_premise(self, task: str) -> str:
        if "=" in task:
            return task.strip()
        return f"Task context: {task.strip()}"

    def _extract_conclusion(self, task: str) -> str:
        if "=" in task:
            return task.strip()
        return "The task requires formal reasoning and symbolic verification."


__all__ = ["FormalKnowledge", "DerivationTrace", "ReasoningEngine"]
