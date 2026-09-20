from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ExperimentType(str, Enum):
    COMPUTATIONAL = "COMPUTATIONAL"
    SYMBOLIC = "SYMBOLIC"
    NUMERICAL = "NUMERICAL"
    SIMULATION = "SIMULATION"
    DATA_ANALYSIS = "DATA_ANALYSIS"
    PHYSICAL = "PHYSICAL"
    OBSERVATIONAL = "OBSERVATIONAL"


class ExperimentStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class Parameter:
    name: str
    symbol: str
    value: Any
    unit: str | None = None
    allowed_range: list[Any] | None = None
    description: str = ""
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "symbol": self.symbol,
            "value": self.value,
            "unit": self.unit,
            "allowed_range": self.allowed_range,
            "description": self.description,
            "provenance": self.provenance,
        }


@dataclass
class ObservationRecord:
    observation_id: str
    experiment_id: str
    variable: str
    value: Any
    unit: str | None = None
    uncertainty: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "SIMULATION"
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "experiment_id": self.experiment_id,
            "variable": self.variable,
            "value": self.value,
            "unit": self.unit,
            "uncertainty": self.uncertainty,
            "timestamp": self.timestamp,
            "source": self.source,
            "provenance": self.provenance,
        }


@dataclass
class PredictionComparison:
    prediction_id: str
    observation_id: str
    expected: Any
    observed: Any
    difference: Any | None = None
    tolerance: Any | None = None
    compatible: bool = False
    method: str = "numeric"
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "observation_id": self.observation_id,
            "expected": self.expected,
            "observed": self.observed,
            "difference": self.difference,
            "tolerance": self.tolerance,
            "compatible": self.compatible,
            "method": self.method,
            "provenance": self.provenance,
        }


@dataclass
class Simulation:
    simulation_id: str
    experiment_id: str
    model: str
    parameters: list[Parameter] = field(default_factory=list)
    initial_conditions: dict[str, Any] = field(default_factory=dict)
    equations: list[str] = field(default_factory=list)
    numerical_method: str = "simple_iterative_eval"
    execution_backend: str = "LocalExecutionBackend"
    outputs: dict[str, Any] = field(default_factory=dict)
    runtime_metadata: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "experiment_id": self.experiment_id,
            "model": self.model,
            "parameters": [param.to_dict() for param in self.parameters],
            "initial_conditions": self.initial_conditions,
            "equations": self.equations,
            "numerical_method": self.numerical_method,
            "execution_backend": self.execution_backend,
            "outputs": self.outputs,
            "runtime_metadata": self.runtime_metadata,
            "provenance": self.provenance,
        }


@dataclass
class Experiment:
    experiment_id: str
    name: str
    description: str
    hypothesis_id: str | None
    objective: str
    domain: str
    inputs: dict[str, Any] = field(default_factory=dict)
    parameters: list[Parameter] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    method: str = "simple computation"
    expected_results: list[str] = field(default_factory=list)
    actual_results: list[str] = field(default_factory=list)
    observations: list[ObservationRecord] = field(default_factory=list)
    status: ExperimentStatus = ExperimentStatus.NOT_STARTED
    provenance: dict[str, Any] = field(default_factory=dict)
    reproducibility_metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str | None = None
    experiment_type: ExperimentType = ExperimentType.COMPUTATIONAL

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "description": self.description,
            "hypothesis_id": self.hypothesis_id,
            "objective": self.objective,
            "domain": self.domain,
            "inputs": self.inputs,
            "parameters": [param.to_dict() for param in self.parameters],
            "assumptions": self.assumptions,
            "constraints": self.constraints,
            "method": self.method,
            "expected_results": self.expected_results,
            "actual_results": self.actual_results,
            "observations": [obs.to_dict() for obs in self.observations],
            "status": self.status.value,
            "provenance": self.provenance,
            "reproducibility_metadata": self.reproducibility_metadata,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "experiment_type": self.experiment_type.value,
        }


@dataclass
class ExperimentResult:
    experiment_id: str
    status: ExperimentStatus = ExperimentStatus.NOT_STARTED
    outputs: dict[str, Any] = field(default_factory=dict)
    observations: list[ObservationRecord] = field(default_factory=list)
    comparisons: list[PredictionComparison] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    runtime: float = 0.0
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "status": self.status.value,
            "outputs": self.outputs,
            "observations": [obs.to_dict() for obs in self.observations],
            "comparisons": [item.to_dict() for item in self.comparisons],
            "errors": self.errors,
            "warnings": self.warnings,
            "runtime": self.runtime,
            "provenance": self.provenance,
        }


@dataclass
class ModelValidation:
    model_id: str
    experiment_id: str
    predictions: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    discrepancies: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    conclusion: str = "insufficient_data"

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "experiment_id": self.experiment_id,
            "predictions": self.predictions,
            "observations": self.observations,
            "assumptions": self.assumptions,
            "discrepancies": self.discrepancies,
            "metrics": self.metrics,
            "conclusion": self.conclusion,
        }


class ExecutionBackend:
    """Execution backend abstraction for lightweight computational experiments."""

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def validate(self, payload: dict[str, Any]) -> bool:
        return bool(payload)

    def collect_output(self, payload: dict[str, Any]) -> dict[str, Any]:
        return payload

    def metadata(self) -> dict[str, Any]:
        return {"backend": self.__class__.__name__, "mode": "controlled"}


class LocalExecutionBackend(ExecutionBackend):
    """Simple local backend for deterministic numeric computations.

    This remains intentionally constrained and does not claim to provide secure sandboxing.
    """

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        expression = payload.get("expression")
        if expression is None:
            raise ValueError("Execution payload requires an expression.")
        value = payload.get("value")
        if value is not None:
            try:
                result = float(value)
            except (TypeError, ValueError):
                result = str(value)
            return {"expression": expression, "value": value, "result": result, "status": "COMPLETED"}
        return {"expression": expression, "result": expression, "status": "COMPLETED"}


class ExperimentRunner:
    """Minimal runner for computational experiments and simulations."""

    def __init__(self, backend: ExecutionBackend | None = None):
        self.backend = backend or LocalExecutionBackend()

    def run_experiment(self, experiment: Experiment, payload: dict[str, Any] | None = None) -> ExperimentResult:
        if not experiment.experiment_id:
            raise ValueError("Experiment requires an experiment_id.")

        if not experiment.parameters and not experiment.inputs:
            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                status=ExperimentStatus.INVALID_CONFIGURATION,
                errors=["Experiment requires parameters or inputs to be defined."],
                provenance={"source": "experiment_runner"},
            )

        experiment.status = ExperimentStatus.RUNNING
        started = datetime.now(timezone.utc)
        runtime_payload = payload or {"expression": experiment.method or "result", "value": experiment.inputs}

        try:
            result = self.backend.execute(runtime_payload)
            converted = result.get("result")
            if converted is not None:
                observation = ObservationRecord(
                    observation_id=f"obs-{experiment.experiment_id}",
                    experiment_id=experiment.experiment_id,
                    variable=experiment.objective or "result",
                    value=converted,
                    source="SIMULATION",
                    provenance={"backend": self.backend.__class__.__name__},
                )
                experiment.observations.append(observation)
                experiment.actual_results.append(str(converted))
            experiment.status = ExperimentStatus.COMPLETED
            completed_at = datetime.now(timezone.utc)
            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                status=ExperimentStatus.COMPLETED,
                outputs={"result": converted},
                observations=experiment.observations,
                warnings=[],
                errors=[],
                runtime=(completed_at - started).total_seconds(),
                provenance={"source": "experiment_runner", "backend": self.backend.__class__.__name__},
            )
        except Exception as exc:  # pragma: no cover - defensive
            experiment.status = ExperimentStatus.FAILED
            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                status=ExperimentStatus.FAILED,
                outputs={},
                observations=experiment.observations,
                comparisons=[],
                errors=[str(exc)],
                warnings=[],
                runtime=(datetime.now(timezone.utc) - started).total_seconds(),
                provenance={"source": "experiment_runner", "backend": self.backend.__class__.__name__},
            )

    def compare_prediction(self, prediction: Any, observation: ObservationRecord, tolerance: Any | None = None) -> PredictionComparison:
        observed = observation.value
        difference = None if prediction is None or observed is None else observed - prediction if isinstance(prediction, (int, float)) and isinstance(observed, (int, float)) else None
        compatible = False
        if difference is not None:
            if tolerance is None:
                compatible = abs(difference) <= 1e-9
            else:
                compatible = abs(difference) <= tolerance
        elif isinstance(prediction, str) and isinstance(observed, str):
            compatible = prediction.lower() == observed.lower()
        else:
            compatible = prediction == observed
        return PredictionComparison(
            prediction_id=f"pred-{observation.observation_id}",
            observation_id=observation.observation_id,
            expected=prediction,
            observed=observed,
            difference=difference,
            tolerance=tolerance,
            compatible=compatible,
            method="numeric" if difference is not None else "qualitative",
            provenance={"source": "experiment_runner", "observation_variable": observation.variable},
        )


__all__ = [
    "Experiment",
    "ExperimentResult",
    "ExperimentRunner",
    "ExperimentStatus",
    "ExperimentType",
    "ExecutionBackend",
    "LocalExecutionBackend",
    "ModelValidation",
    "ObservationRecord",
    "Parameter",
    "PredictionComparison",
    "Simulation",
]
