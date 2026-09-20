from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

from alethia.core.cognition.cognitive_state import CognitiveState


class WorkingMemory(MutableMapping[str, Any]):
    """Working memory used during the active task lifecycle."""

    def __init__(self, state: CognitiveState | None = None):
        self._state = state
        self._store: dict[str, dict[str, Any]] = {}

    def _task_scope(self, task_id: str | None = None) -> dict[str, Any]:
        target = task_id or (self._state.task_id if self._state else "default")
        if target not in self._store:
            self._store[target] = {}
        return self._store[target]

    def add(self, key: str, value: Any, task_id: str | None = None) -> None:
        self._task_scope(task_id)[key] = value

    def remove(self, key: str, task_id: str | None = None) -> Any:
        return self._task_scope(task_id).pop(key)

    def update(self, key: str, value: Any, task_id: str | None = None) -> None:
        self._task_scope(task_id)[key] = value

    def get(self, key: str, default: Any = None, task_id: str | None = None) -> Any:
        return self._task_scope(task_id).get(key, default)

    def clear(self, task_id: str | None = None) -> None:
        self._task_scope(task_id).clear()

    def snapshot(self, task_id: str | None = None) -> dict[str, Any]:
        return dict(self._task_scope(task_id))

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.add(key, value)

    def __delitem__(self, key: str) -> None:
        self.remove(key)

    def __iter__(self):
        return iter(self._task_scope())

    def __len__(self) -> int:
        return len(self._task_scope())

    def __repr__(self) -> str:
        return f"WorkingMemory({self.snapshot()})"


__all__ = ["WorkingMemory"]
