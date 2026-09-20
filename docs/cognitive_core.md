# Cognitive Core

The cognitive core is intentionally minimal in Aletheia 0.1. It exists to transform a user task into a structured internal state that distinguishes between facts, assumptions, hypotheses and conclusions.

## Components

### CognitiveState

A `CognitiveState` object stores:

- task
- goal
- context
- known facts
- unknowns
- assumptions
- hypotheses
- reasoning steps
- tool calls
- observations
- verification results
- conclusion
- uncertainty
- status
- history

### Knowledge types

The first version provides explicit typed objects for:

- `Fact`
- `Hypothesis`
- `Assumption`
- `Observation`
- `Evidence`
- `Inference`
- `Uncertainty`
- `Conclusion`

These are not interchangeable; an assumption is not treated as a verified fact.

### State machine

The task lifecycle is intentionally explicit:

```text
CREATED -> UNDERSTANDING -> REASONING -> TOOL_EXECUTION -> VERIFICATION -> COMPLETED
```

Failure and blocking transitions are also represented for explicit handling.

## Current capabilities

This version performs a controlled reasoning loop for a narrow class of tasks, especially algebraic equation solving and differentiation. It is deterministic, inspectable and structured around explicit knowledge types and validation.

## Current scope

This version is deterministic and narrow. It is designed so that future versions can replace the reasoning logic without rewriting the task model or orchestration flow.

## Known limitations

- no full autonomous research engine;
- no generalized long-term memory graph yet;
- no external system execution other than controlled local Python code;
- no true security sandbox for Python execution; the current helper blocks the most obvious dangerous patterns but cannot guarantee isolation;
- no claim of general scientific intelligence.
