from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from alethia.core.cognition.cognitive_state import CognitiveState
from alethia.memory.storage.repository import MemoryRepository
from alethia.memory.working_memory import WorkingMemory


class MemoryManager:
    """Central memory coordinator for Aletheia 0.2."""

    def __init__(self, repository: MemoryRepository | None = None):
        self.repository = repository or MemoryRepository()
        self.working = WorkingMemory()

    def remember_working(self, state: CognitiveState, key: str, value: object) -> None:
        self.working.add(key, value, task_id=state.task_id)
        payload = self.working.snapshot(task_id=state.task_id)
        self.repository.save_working_memory(state.task_id, payload)

    def load_working(self, task_id: str) -> dict[str, object]:
        return self.repository.load_working_memory(task_id)

    def clear_working(self, task_id: str) -> None:
        self.working.clear(task_id=task_id)
        self.repository.remove_working_memory(task_id)

    def retrieve(self, query: str, limit: int = 5) -> list[str]:
        normalized = query.lower()
        results: list[str] = []

        if "learn" in normalized or "remember" in normalized or "previous" in normalized:
            for episode in self.repository.list_episodes(limit=limit):
                results.append(f"Episode: {episode['task']} -> {episode['outcome']}")
            return results

        for knowledge in self.repository.search_knowledge(query, limit=limit):
            results.append(knowledge["statement"])
        for episode in self.repository.search_episodes(query, limit=limit):
            results.append(f"Episode: {episode['task']} -> {episode['outcome']}")
        return results

    def consolidate_task(self, state: CognitiveState) -> dict[str, object]:
        if not state.task_id:
            raise ValueError("Task must have a task_id before consolidation.")

        episode = {
            "episode_id": f"episode-{uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task": state.task,
            "goal": state.goal or "unknown",
            "actions": state.history,
            "tool_calls": state.tool_calls,
            "observations": [obs.to_dict() for obs in state.observations],
            "verification": {"status": state.verification_status, "uncertainty": state.uncertainty},
            "conclusion": {"text": state.conclusion, "uncertainty": state.uncertainty},
            "outcome": state.conclusion or "No conclusion produced.",
            "uncertainty": state.uncertainty,
            "metadata": {"task_id": state.task_id, "status": state.status.value},
        }
        self.repository.save_episode(episode)

        if state.status.value == "COMPLETED" and state.conclusion:
            knowledge = {
                "knowledge_id": f"knowledge-{uuid4().hex[:8]}",
                "statement": state.conclusion,
                "kind": "CONCLUSION" if state.uncertainty == "verified" else "HYPOTHESIS",
                "domain": "general",
                "confidence": state.uncertainty,
                "status": state.verification_status,
                "source": "task_completion",
                "assumptions": [item.content for item in state.assumptions],
                "related_concepts": [item.content for item in state.reasoning_steps],
            }
            self.repository.save_knowledge(knowledge)
            for fact in state.known_facts:
                self.repository.save_provenance(knowledge["knowledge_id"], fact.id, "DERIVED_FROM")

        return episode

    def remember_procedure(self, procedure_id: str, name: str, description: str, content: dict[str, object]) -> None:
        self.repository.save_procedure({
            "procedure_id": procedure_id,
            "name": name,
            "description": description,
            "content": content,
        })

    def retrieve_procedures(self) -> list[dict[str, object]]:
        return self.repository.list_procedures()

    def store_contradiction(self, left: str, right: str) -> None:
        left_id = f"knowledge-{uuid4().hex[:8]}"
        right_id = f"knowledge-{uuid4().hex[:8]}"
        self.repository.save_knowledge({
            "knowledge_id": left_id,
            "statement": left,
            "kind": "FACT",
            "domain": "general",
            "confidence": "supported",
            "status": "SUPPORTED",
            "source": "contradiction",
            "assumptions": [],
            "related_concepts": [],
        })
        self.repository.save_knowledge({
            "knowledge_id": right_id,
            "statement": right,
            "kind": "FACT",
            "domain": "general",
            "confidence": "supported",
            "status": "SUPPORTED",
            "source": "contradiction",
            "assumptions": [],
            "related_concepts": [],
        })
        self.repository.save_provenance(left_id, right_id, "CONTRADICTS")

    def retrieve_memory_context(self, task: str, limit: int = 5) -> str:
        matches = self.retrieve(task, limit=limit)
        if not matches:
            return "No relevant memory found."
        return " ; ".join(matches)
