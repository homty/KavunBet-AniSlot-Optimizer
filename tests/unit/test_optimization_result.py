from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from kavunbet_optimizer.domain.optimization_result import OptimizationResultArtifact
from kavunbet_optimizer.domain.reel_artifact import StoredReelArtifact
from kavunbet_optimizer.schemas.optimization import GameMode


def make_artifact(**changes: object) -> OptimizationResultArtifact:
    values: dict[str, object] = {
        "id": uuid4(),
        "job_id": uuid4(),
        "game_mode": GameMode.BASE,
        "reels": StoredReelArtifact(
            storage_key="projects/test/jobs/job/results/result/reels.csv",
            sha256="a" * 64,
            size_bytes=24,
        ),
        "initial_penalty": 10.0,
        "final_penalty": 2.0,
        "iterations": 100,
        "accepted_moves": 25,
        "created_at": datetime.now(UTC),
    }
    values.update(changes)

    return OptimizationResultArtifact.model_validate(values)


def test_optimization_result_accepts_valid_artifact() -> None:
    artifact = make_artifact()

    assert artifact.game_mode == GameMode.BASE
    assert artifact.reels.storage_key.endswith("reels.csv")
    assert artifact.final_penalty == 2.0
    assert artifact.iterations == 100
    assert artifact.accepted_moves == 25


def test_optimization_result_is_immutable() -> None:
    artifact = make_artifact()

    with pytest.raises(ValidationError, match="frozen"):
        artifact.final_penalty = 1.0


def test_optimization_result_rejects_worse_final_penalty() -> None:
    with pytest.raises(ValidationError, match="final penalty cannot exceed"):
        make_artifact(initial_penalty=2.0, final_penalty=3.0)


def test_optimization_result_rejects_more_accepted_moves_than_iterations() -> None:
    with pytest.raises(ValidationError, match="accepted moves cannot exceed"):
        make_artifact(iterations=10, accepted_moves=11)


def test_optimization_result_requires_timezone_aware_timestamp() -> None:
    naive_timestamp = datetime.now(UTC).replace(tzinfo=None)

    with pytest.raises(ValidationError, match="timezone-aware"):
        make_artifact(created_at=naive_timestamp)


def test_optimization_result_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        make_artifact(unknown_field="value")
