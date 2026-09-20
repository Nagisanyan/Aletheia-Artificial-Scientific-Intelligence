# Aletheia 0.1 Architecture

## 1. Architecture overview

Aletheia 0.1 is intentionally minimal and verifiable. The goal is not full scientific intelligence; it is to establish the first reliable loop for understanding a task, selecting a tool, verifying the result, and reporting an uncertainty-aware conclusion.

```text
Task
  ↓
Cognitive Core
  ↓
Working Memory
  ↓
Reasoning
  ↓
Python Tool
  ↓
Verification Engine
  ↓
Structured Response
```

## 2. Implemented modules

### 2.1 Cognitive core

The cognitive core is implemented in:

- `alethia/core/cognition/cognitive_state.py`
- `alethia/core/cognition/cognitive_core.py`
- `alethia/core/cognition/types.py`

It provides:

- explicit `CognitiveState` for a task;
- knowledge types: `Fact`, `Hypothesis`, `Assumption`, `Observation`, `Evidence`, `Inference`, `Uncertainty`, `Conclusion`;
- state-machine transitions for valid task lifecycle handling;
- deterministic reasoning and conclusion generation for structured tasks.

### 2.2 Working memory

The working memory module is implemented in:

- `alethia/memory/working_memory/__init__.py`

It provides:

- task-scoped storage;
- add/update/remove/get/clear/snapshot operations;
- isolation between tasks.

### 2.3 Orchestration

The orchestrator is implemented in:

- `alethia/core/orchestration/orchestrator.py`

It executes the sequence:

Input → Understand → Reason → Tool → Verify → Response

This implementation supports mathematics tasks such as derivatives and simple equation solving using SymPy.

### 2.4 Python tool

The controlled Python tool is implemented in:

- `alethia/tools/python/tool.py`

It provides:

- local execution only;
- timeout handling;
- stdout/stderr capture;
- blocked-pattern detection for unsafe operations;
- structured execution results.

### 2.5 Verification engine

The logical verification layer is implemented in:

- `alethia/verification/logical/verifier.py`

It checks:

- reasoning sufficiency;
- unresolved unknowns;
- contradiction detection;
- confidence classification (`verified`, `supported`, `uncertain`, `unknown`, `contradictory`).

## 3. Data model

A `CognitiveState` contains the following core fields:

```python
{
    "task": "...",
    "goal": "...",
    "context": "...",
    "known_facts": [],
    "unknowns": [],
    "assumptions": [],
    "hypotheses": [],
    "reasoning_steps": [],
    "tool_calls": [],
    "observations": [],
    "verification_results": [],
    "conclusion": "...",
    "uncertainty": "...",
    "status": "CREATED",
    "history": ["TASK_CREATED"]
}
```

The system preserves a strict difference between:

- a verified fact;
- an assumption;
- a hypothesis;
- an observation;
- a conclusion.

## 4. Task lifecycle

The supported lifecycle is explicit:

```text
CREATED
  -> UNDERSTANDING
  -> REASONING
  -> TOOL_EXECUTION
  -> VERIFICATION
  -> COMPLETED
```

Additional failure states exist:

```text
FAILED
BLOCKED
```

No invalid transition is allowed by the `TaskStateMachine`.

## 5. Aletheia 0.5 hypothesis generation and evaluation architecture

Aletheia 0.5 extends the 0.1–0.4 foundations with a minimal explicit hypothesis engine while preserving the earlier cognitive core, memory, scientific knowledge layer, and symbolic verification model.

```text
Task
  ↓
Cognitive Core
  ↓
Scientific Knowledge Layer
  ↓
Hypothesis Engine
  ├── Question-driven generation
  ├── Contradiction-driven generation
  ├── Prediction generation
  ├── Evidence tracking
  ├── Counterevidence tracking
  └── Evaluation status
  ↓
Reasoning + Mathematics + Verification
  ↓
Persistent Memory
  ↓
Response
```

### 5.1 Hypothesis model

Hypotheses are represented as explicit objects with:

- statement,
- domain,
- subdomain,
- concepts,
- premises,
- assumptions,
- constraints,
- motivation,
- predictions,
- expected observations,
- evidence,
- counterevidence,
- provenance,
- status,
- confidence,
- falsifiability.

This keeps generation and evaluation separate from verification and fact storage.

### 5.2 Hypothesis status model

The system distinguishes statuses such as:

- `PROPOSED`
- `UNDER_EVALUATION`
- `SUPPORTED`
- `WEAKLY_SUPPORTED`
- `UNSUPPORTED`
- `CONTRADICTED`
- `FALSIFIED`
- `UNRESOLVED`
- `REJECTED`

This prevents a generated hypothesis from being silently treated as a fact.

### 5.3 Prediction and evaluation layer

Generated hypotheses produce structured predictions, and each evaluation records:

- supporting evidence,
- contradicting evidence,
- unresolved items,
- evaluated predictions,
- reasoning trace,
- provenance.

The engine remains bounded and deterministic rather than open-ended.

## 6. Aletheia 0.6 experiment and simulation architecture

Aletheia 0.6 adds a lightweight computational experimentation layer to connect hypotheses, predictions, experiments, and observations.

```text
Hypothesis
  ↓
Prediction
  ↓
Experiment
  ├── parameters
  ├── assumptions
  ├── constraints
  ├── method
  ├── expected_results
  ├── reproducibility metadata
  └── execution backend
  ↓
Simulation / execution
  ↓
ObservationRecord
  ↓
PredictionComparison
  ↓
HypothesisEvaluation update
```

### 6.1 Experiment model

Experiments are represented as explicit records containing:

- unique experiment id,
- name and description,
- objective,
- domain,
- hypothesis association,
- inputs and parameters,
- assumptions and constraints,
- execution method,
- expected results,
- actual results,
- status,
- provenance,
- reproducibility metadata.

### 6.2 Simulation abstraction

The simulation layer is separate from real-world experimentation and explicitly labels simulations as computational rather than physical measurements.

It carries:

- model description,
- parameters,
- initial conditions,
- equations,
- numerical method,
- backend,
- outputs,
- runtime metadata,
- provenance.

### 6.3 Execution backend abstraction

The system separates the experiment from the execution mechanism via an `ExecutionBackend` interface.

This keeps future implementations possible without changing the experiment schema, for example:

- `LocalExecutionBackend`
- `SandboxBackend`
- `ContainerBackend`
- `RemoteComputeBackend`

The current implementation remains intentionally constrained and does not claim secure sandboxing.

### 6.4 Observation and comparison model

A simulation produces observations with provenance, and comparisons are kept explicit:

- `ObservationRecord`
- `PredictionComparison`
- expected vs observed values
- difference and tolerance
- compatibility flag
- method metadata

These remain explicit and auditable rather than hidden inside a single opaque result object.

## 7. Current capabilities

Aletheia 0.6 currently performs a structured, inspectable pipeline with controlled experimentation support:

- parse the task into a `CognitiveState`;
- retrieve relevant memory and scientific knowledge when applicable;
- generate hypotheses from ideas, contradictions, or research questions;
- maintain explicit assumptions, constraints, parameters and provenance;
- instantiate experiments with typed domain-specific metadata;
- execute simple local computations through a lightweight `ExecutionBackend` abstraction;
- record observations with explicit source provenance (`SIMULATION`);
- compare predicted and observed values with structured compatibility checks;
- keep reproducibility metadata and deterministic execution context explicit;
- retain the existing reasoning, math, memory and hypothesis foundations.

This remains an experimental computational-science layer, not a general scientific discovery engine.

## 8. Known limitations

This version is intentionally limited:

- no autonomous experiment selection loop;
- no secure sandbox for Python execution; the execution backend is still a constrained helper rather than a true isolated environment;
- no domain-general numerical solver beyond simple deterministic computations;
- no real physical instrumentation or external lab integration;
- no large-scale scientific knowledge graph or vector retrieval yet;
- no universal proof or model-truth engine.

## 9. Next development step

The recommended next step is to expand beyond the current explicit computational experimentation layer by adding:

- richer experiment persistence in SQLite;
- parameter sweeps and sensitivity analysis;
- more structured hypothesis update logic from observation comparisons;
- stronger falsification and inconclusive-case handling.
