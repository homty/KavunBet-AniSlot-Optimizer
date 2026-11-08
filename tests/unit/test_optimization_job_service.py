import pytest

from kavunbet_optimizer.application.optimization_job_service import (
    OptimizationJobService,
)
from kavunbet_optimizer.domain.exceptions import OptimizationJobErrors
from kavunbet_optimizer.domain.optimization_job import JobStatus
from kavunbet_optimizer.infrastructure.in_memory_config_repository import (
    InMemoryOptimizationConfigRepository,
)
from kavunbet_optimizer.infrastructure.in_memory_optimization_job_repository import (
    InMemoryOptimizationJobRepository,
)
from kavunbet_optimizer.schemas.optimization import GameMode


def create_service() -> OptimizationJobService:
    return OptimizationJobService(
        job_repository=InMemoryOptimizationJobRepository(),
        config_repository=InMemoryOptimizationConfigRepository(),
    )


def test_submit_creates_queued_job_with_configuration_snapshot() -> None:
    service = create_service()

    job = service.submit(
        project_id="giantesses-attack",
        engine_id="giantesses-math-engine",
        game_mode=GameMode.BASE,
        idempotency_key="request-1",
    )

    assert job.project_id == "giantesses-attack"
    assert job.engine_id == "giantesses-math-engine"
    assert job.game_mode == GameMode.BASE
    assert job.status == JobStatus.QUEUED
    assert job.idempotency_key == "request-1"
    assert job.created_at == job.updated_at
    assert job.created_at.tzinfo is not None


def test_submit_returns_existing_job_for_repeated_request() -> None:
    service = create_service()
    request = {
        "project_id": "giantesses-attack",
        "engine_id": "giantesses-math-engine",
        "game_mode": GameMode.BASE,
        "idempotency_key": "request-1",
    }

    first = service.submit(**request)
    repeated = service.submit(**request)

    assert repeated == first
    assert repeated.id == first.id


def test_submit_rejects_reused_key_for_different_request() -> None:
    service = create_service()
    service.submit(
        project_id="giantesses-attack",
        engine_id="giantesses-math-engine",
        game_mode=GameMode.BASE,
        idempotency_key="request-1",
    )

    with pytest.raises(
        OptimizationJobErrors.IdempotencyKeyConflictError,
        match="request-1",
    ):
        service.submit(
            project_id="giantesses-attack",
            engine_id="another-engine",
            game_mode=GameMode.BASE,
            idempotency_key="request-1",
        )
