from __future__ import annotations

from pathlib import Path

from alethia.memory.storage.repository import MemoryRepository
from alethia.science.knowledge import (
    KnowledgeRelation,
    ScientificDomain,
    ScientificKnowledge,
    ScientificKnowledgeStatus,
    ScientificKnowledgeType,
)


def test_scientific_knowledge_representation_and_persistence(tmp_path):
    repo = MemoryRepository(tmp_path / "science.db")
    knowledge = ScientificKnowledge(
        knowledge_id="science-law-1",
        statement="Force equals mass times acceleration.",
        kind=ScientificKnowledgeType.LAW,
        domain=ScientificDomain.PHYSICS,
        subdomain="Classical Mechanics",
        concepts=["force", "mass", "acceleration"],
        variables=["F", "m", "a"],
        constants=[],
        equations=["F = m*a"],
        assumptions=["classical regime", "inertial frame"],
        constraints=[],
        conditions=["non-relativistic regime"],
        status=ScientificKnowledgeStatus.SUPPORTED,
        confidence="supported",
        provenance={"source": "internal_derivation"},
        relations=[KnowledgeRelation.EXPRESSED_BY.value],
    )

    repo.save_scientific_knowledge(knowledge.to_dict())
    results = repo.search_scientific_knowledge("force equals mass", limit=5)

    assert any(item["statement"] == "Force equals mass times acceleration." for item in results)
    assert results[0]["kind"] == "LAW"
    assert results[0]["domain"] == "PHYSICS"


def test_scientific_relations_and_status_distinction():
    relation = KnowledgeRelation.DERIVED_FROM.value
    knowledge = ScientificKnowledge(
        knowledge_id="science-hyp-1",
        statement="A new model predicts a stable orbit.",
        kind=ScientificKnowledgeType.HYPOTHESIS,
        domain=ScientificDomain.PHYSICS,
        status=ScientificKnowledgeStatus.PROPOSED,
        confidence="proposed",
        provenance={"source": "model"},
        relations=[relation],
    )

    assert knowledge.kind != ScientificKnowledgeType.LAW
    assert knowledge.status != ScientificKnowledgeStatus.VERIFIED
    assert relation in {item.value for item in KnowledgeRelation}


def test_scientific_repository_roundtrip_after_restart(tmp_path):
    path = tmp_path / "roundtrip.db"
    repo1 = MemoryRepository(path)
    repo1.save_scientific_knowledge({
        "knowledge_id": "science-eq-1",
        "statement": "The mechanical work formula is W = F*d.",
        "kind": "EQUATION",
        "domain": "PHYSICS",
        "subdomain": "Classical Mechanics",
        "concepts": ["work", "force", "distance"],
        "variables": ["W", "F", "d"],
        "constants": [],
        "equations": ["W = F*d"],
        "assumptions": ["constant force"],
        "constraints": [],
        "conditions": ["linear path"],
        "status": "SUPPORTED",
        "confidence": "supported",
        "provenance": {"source": "internal_derivation"},
        "relations": ["DEFINED_BY:W = F*d"],
    })

    repo2 = MemoryRepository(path)
    matches = repo2.search_scientific_knowledge("mechanical work formula", limit=10)
    assert any("W = F*d" in item["equations"] for item in matches)
