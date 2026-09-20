# Aletheia

Aletheia is a research-oriented artificial scientific intelligence project. This repository currently contains the first operational foundation for Aletheia 0.1, with a structured cognitive state, a working-memory layer, a minimal orchestration loop, controlled Python execution, and a verification engine.

## Current implementation status

Implemented in Aletheia 0.1:

- `CognitiveState` and explicit knowledge types for facts, assumptions, hypotheses, evidence and conclusions.
- task state machine with valid and invalid transitions.
- working memory with task-scoped isolation and CRUD operations.
- cognitive core for understanding, reasoning and conclusion generation.
- orchestrator executing: Input → Understand → Reason → Tool → Verify → Response.
- controlled Python tool with timeout and blocked-pattern safeguards.
- logical verification layer for coherence, unresolved unknowns and contradiction detection.
- CLI entry point via `python -m alethia`.
- pytest suite covering the first working loop.

## Installation

```bash
python -m pip install -r requirements.txt
```

## Run a task

```bash
python -m alethia "Calculate the derivative of x^2 + 3x + 2"
```

or:

```bash
python -m alethia "Solve 2x + 4 = 10"
```

## Run tests

```bash
python -m pytest -q
```

## Project structure

```text
Aletheia/
├── README.md
├── ARCHITECTURE.md
├── ROADMAP.md
├── RESEARCH.md
├── requirements.txt
├── alethia/
│   ├── __init__.py
│   ├── __main__.py
│   ├── core/
│   │   ├── cognition/
│   │   │   ├── __init__.py
│   │   │   ├── cognitive_core.py
│   │   │   ├── cognitive_state.py
│   │   │   └── types.py
│   │   └── orchestration/
│   │       ├── __init__.py
│   │       └── orchestrator.py
│   ├── memory/
│   │   ├── __init__.py
│   │   └── working_memory/
│   │       └── __init__.py
│   ├── tools/
│   │   ├── __init__.py
│   │   └── python/
│   │       ├── __init__.py
│   │       └── tool.py
│   └── verification/
│       ├── __init__.py
│       └── logical/
│           ├── __init__.py
│           └── verifier.py
├── docs/
│   └── cognitive_core.md
├── tests/
│   └── test_alethia_0_1.py
├── .gitignore
└── .pytest_cache/
```

## Current capabilities

Aletheia 0.7 extends the 0.1–0.6 foundation with a first explicit verification and self-criticism layer.

It currently supports:

- structured task representation via `CognitiveState`;
- explicit separation between `Fact`, `Hypothesis`, `Assumption`, `Observation`, `Evidence`, `Inference` and `Conclusion`;
- valid task transitions enforced by the state machine;
- working memory with task-scoped isolation;
- persistent memory storage using SQLite via `MemoryRepository`;
- episodic memory storage for completed tasks and outcomes;
- semantic memory for structured knowledge objects with epistemic status;
- provenance tracking to record `DERIVED_FROM` and `CONTRADICTS` relations;
- retrieval of relevant previous experience through `MemoryManager.retrieve()`;
- explicit formal reasoning traces with a `ReasoningEngine`;
- symbolic mathematics through SymPy: solving, differentiation, simplification, integration and limits;
- scientific knowledge objects such as `LAW`, `THEORY`, `MODEL`, `EQUATION`, `HYPOTHESIS`, `ASSUMPTION`, `CONSTRAINT` and `OBSERVATION`;
- scientific knowledge persistence and retrieval by domain, subdomain, concept and equation;
- controlled hypothesis generation from questions and contradictions;
- explicit hypothesis evaluation status (`PROPOSED`, `UNDER_EVALUATION`, `SUPPORTED`, `CONTRADICTED`, `UNRESOLVED`, etc.);
- prediction and provenance tracking for generated hypotheses;
- a first experiment and simulation model (`Experiment`, `Simulation`, `ObservationRecord`, `PredictionComparison`);
- a minimal execution backend abstraction for local deterministic compute;
- reproducibility metadata and parameter tracking for experiments;
- explicit verification result records with status, checks, evidence, contradictions, assumptions, and provenance;
- a self-criticism engine that reviews outputs before treating them as sufficiently supported;
- controlled Python execution with timeout and static analysis against dangerous patterns;
- verification output labeled by structured status such as `VALID`, `VERIFIED`, `SUPPORTED`, `INSUFFICIENT_EVIDENCE` or `CONTRADICTORY`;
- command-line execution through `python -m alethia`.

## Known limitations

Aletheia 0.7 is still not a general scientific intelligence system. It remains a controlled prototype with:

- no autonomous multi-domain research engine;
- no large-scale scientific knowledge graph or vector retrieval yet;
- no unrestricted system access;
- no real-world experimentation or dangerous tool execution;
- a non-sandboxed Python execution model that should be replaced by a real isolated worker in later versions;
- scientific knowledge, hypothesis, experimental and verification results are still limited to structured and keyword-based reasoning rather than full epistemic automation;
- the simulation layer remains a controlled computational model rather than a general-purpose scientific simulator;
- verification is explicit and bounded rather than universal, and it is designed to prevent overconfidence rather than to claim certainty.

The goal is to provide a disciplined verification and self-criticism layer for future research loops without overstating the system's intelligence.
