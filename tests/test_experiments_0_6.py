from __future__ import annotations

from alethia.experiments import (
    Experiment,
    ExperimentRunner,
    ExperimentStatus,
    ExperimentType,
    ObservationRecord,
    Parameter,
    PredictionComparison,
)


def test_experiment_model_and_runner():
    experiment = Experiment(
        experiment_id="exp-1",
        name="linear check",
        description="Check a linear prediction under a simple controlled input.",
        hypothesis_id="hyp-1",
        objective="Test y = x + 1",
        domain="mathematics",
        inputs={"x": 5},
        parameters=[Parameter(name="x", symbol="x", value=5, unit=None, description="test value")],
        assumptions=["the model is linear"],
        constraints=["simple deterministic evaluation"],
        method="evaluate linear model",
        expected_results=["y = 6"],
        experiment_type=ExperimentType.COMPUTATIONAL,
    )

    result = ExperimentRunner().run_experiment(experiment, {"expression": "linear", "value": 5})

    assert experiment.status == ExperimentStatus.COMPLETED
    assert result.status == ExperimentStatus.COMPLETED
    assert result.outputs["result"] == 5
    assert experiment.observations


def test_prediction_comparison_tracks_compatibility():
    observation = ObservationRecord(
        observation_id="obs-1",
        experiment_id="exp-1",
        variable="y",
        value=10,
        source="SIMULATION",
        provenance={"source": "test"},
    )
    comparison = ExperimentRunner().compare_prediction(10, observation, tolerance=0.1)

    assert comparison.compatible is True
    assert comparison.method == "numeric"
    assert comparison.difference == 0


def test_experiment_supports_deterministic_metadata():
    experiment = Experiment(
        experiment_id="exp-2",
        name="reproducibility check",
        description="Ensure reproducibility metadata is carried through.",
        hypothesis_id="hyp-2",
        objective="Check reproducibility",
        domain="general",
        reproducibility_metadata={"random_seed": 12345, "software_version": "alethia-test"},
        parameters=[Parameter(name="mass", symbol="m", value=2, unit="kg")],
    )

    assert experiment.reproducibility_metadata["random_seed"] == 12345
    assert experiment.to_dict()["experiment_type"] == ExperimentType.COMPUTATIONAL.value
