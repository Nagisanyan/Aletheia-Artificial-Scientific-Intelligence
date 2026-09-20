from __future__ import annotations

from alethia.core.orchestration.orchestrator import Orchestrator
from alethia.memory.manager import MemoryManager
from alethia.memory.storage.repository import MemoryRepository


def test_memory_repository_persistence_and_retrieval(tmp_path):
    repo = MemoryRepository(tmp_path / "memory.db")
    repo.save_knowledge({
        "knowledge_id": "k-1",
        "statement": "The equation solver can resolve linear equations.",
        "kind": "RULE",
        "domain": "mathematics",
        "confidence": "supported",
        "status": "VERIFIED",
        "source": "internal",
        "assumptions": ["linear equations"],
        "related_concepts": ["equation", "solver"],
    })
    repo.save_episode({
        "episode_id": "ep-1",
        "timestamp": "2026-09-20T00:00:00Z",
        "task": "Solve 3x + 7 = 22",
        "goal": "Solve the equation.",
        "actions": ["understand", "tool"],
        "tool_calls": ["sympy"],
        "observations": ["solution found"],
        "verification": {"status": "VALID"},
        "conclusion": {"text": "x = 5"},
        "outcome": "x = 5",
        "uncertainty": "verified",
        "metadata": {"status": "completed"},
    })

    knowledge = repo.search_knowledge("equation solver", limit=5)
    episodes = repo.search_episodes("Solve 3x + 7 = 22", limit=5)
    assert any("equation solver" in item["statement"].lower() for item in knowledge)
    assert episodes and episodes[0]["task"] == "Solve 3x + 7 = 22"


def test_memory_manager_handles_contradiction_and_procedures(tmp_path):
    manager = MemoryManager(repository=MemoryRepository(tmp_path / "memory.db"))
    manager.store_contradiction("x = 5", "x = 7")
    manager.remember_procedure("proc-1", "linear_equation_solver", "Solve linear equations symbolically.", {"method": "sympy"})

    contradiction_matches = manager.retrieve("x = 5")
    procedures = manager.retrieve_procedures()

    assert contradiction_matches
    assert any(proc["name"] == "linear_equation_solver" for proc in procedures)


def test_orchestrator_retrieves_previous_experience(tmp_path):
    repo = MemoryRepository(tmp_path / "memory.db")
    manager = MemoryManager(repository=repo)
    orchestrator = Orchestrator(memory_manager=manager)

    first = orchestrator.run("Solve 3x + 7 = 22")
    assert first.status.value == "COMPLETED"

    second = orchestrator.run("What did you learn from the previous task?")
    assert second.status.value in {"COMPLETED", "FAILED"}
    assert "No relevant memory found." not in second.context
