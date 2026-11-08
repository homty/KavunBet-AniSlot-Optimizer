from uuid import uuid4

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


def test_get_job_returns_submitted_job() -> None:
    service = create_service()
    submitted = service.submit(
        project_id="giantesses-attack",
        engine_id="giantesses-math-engine",
        game_mode=GameMode.BASE,
        idempotency_key="request-1",
    )

    retrieved = service.get_job(submitted.id)

    assert retrieved == submitted
    assert retrieved is not submitted


def test_get_job_rejects_unknown_job_id() -> None:
    service = create_service()
    unknown_id = uuid4()

    with pytest.raises(
        OptimizationJobErrors.OptimizationJobNotFoundError,
        match=str(unknown_id),
    ):
        service.get_job(unknown_id)


def test_request_cancellation_updates_and_persists_job() -> None:
    service = create_service()
    submitted = service.submit(
        project_id="giantesses-attack",
        engine_id="giantesses-math-engine",
        game_mode=GameMode.BASE,
        idempotency_key="request-1",
    )

    cancellation_requested = service.request_cancellation(submitted.id)
    persisted = service.get_job(submitted.id)

    assert cancellation_requested.status == JobStatus.CANCELLATION_REQUESTED
    assert cancellation_requested.updated_at >= submitted.updated_at
    assert persisted == cancellation_requested
    assert submitted.status == JobStatus.QUEUED


def test_repeated_cancellation_request_returns_unchanged_job() -> None:
    service = create_service()
    submitted = service.submit(
        project_id="giantesses-attack",
        engine_id="giantesses-math-engine",
        game_mode=GameMode.BASE,
        idempotency_key="request-1",
    )
    first = service.request_cancellation(submitted.id)

    repeated = service.request_cancellation(submitted.id)

    assert repeated == first
    assert repeated.updated_at == first.updated_at


def test_request_cancellation_rejects_unknown_job() -> None:
    service = create_service()
    unknown_id = uuid4()

    with pytest.raises(
        OptimizationJobErrors.OptimizationJobNotFoundError,
        match=str(unknown_id),
    ):
        service.request_cancellation(unknown_id)


def test_request_cancellation_rejects_terminal_job() -> None:
    job_repository = InMemoryOptimizationJobRepository()
    service = OptimizationJobService(
        job_repository=job_repository,
        config_repository=InMemoryOptimizationConfigRepository(),
    )
    submitted = service.submit(
        project_id="giantesses-attack",
        engine_id="giantesses-math-engine",
        game_mode=GameMode.BASE,
        idempotency_key="request-1",
    )
    completed = submitted.model_copy(update={"status": JobStatus.COMPLETED})
    job_repository.save(completed)

    with pytest.raises(
        OptimizationJobErrors.InvalidJobStatusTransitionError,
        match=JobStatus.COMPLETED.value,
    ):
        service.request_cancellation(submitted.id)
