from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Episode:
    episode_id: str
    timestamp: str
    task: str
    goal: str
    actions: list[str] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    verification: dict[str, Any] = field(default_factory=dict)
    conclusion: dict[str, Any] = field(default_factory=dict)
    outcome: str = ""
    uncertainty: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "timestamp": self.timestamp,
            "task": self.task,
            "goal": self.goal,
            "actions": self.actions,
            "tool_calls": self.tool_calls,
            "observations": self.observations,
            "verification": self.verification,
            "conclusion": self.conclusion,
            "outcome": self.outcome,
            "uncertainty": self.uncertainty,
            "metadata": self.metadata,
        }


__all__ = ["Episode"]
