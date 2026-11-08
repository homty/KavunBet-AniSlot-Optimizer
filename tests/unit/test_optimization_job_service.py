from uuid import uuid4

import pytest

from kavunbet_optimizer.application.optimization_job_service import (
    OptimizationJobService,
)
from kavunbet_optimizer.domain.exceptions import OptimizationJobErrors
from kavunbet_optimizer.domain.optimization_job import JobStatus, OptimizationJob
from kavunbet_optimizer.infrastructure.in_memory_config_repository import (
    InMemoryOptimizationConfigRepository,
)
from kavunbet_optimizer.infrastructure.in_memory_optimization_job_repository import (
    InMemoryOptimizationJobRepository,
)
from kavunbet_optimizer.schemas.optimization import GameMode


@pytest.fixture
def job_repository() -> InMemoryOptimizationJobRepository:
    return InMemoryOptimizationJobRepository()


@pytest.fixture
def service(
    job_repository: InMemoryOptimizationJobRepository,
) -> OptimizationJobService:
    return OptimizationJobService(
        job_repository=job_repository,
        config_repository=InMemoryOptimizationConfigRepository(),
    )


def submit_job(
    service: OptimizationJobService,
    *,
    project_id: str = "giantesses-attack",
    engine_id: str = "giantesses-math-engine",
    game_mode: GameMode = GameMode.BASE,
    idempotency_key: str = "request-1",
) -> OptimizationJob:
    return service.submit(
        project_id=project_id,
        engine_id=engine_id,
        game_mode=game_mode,
        idempotency_key=idempotency_key,
    )


def test_submit_creates_queued_job_with_configuration_snapshot(
    service: OptimizationJobService,
) -> None:
    job = submit_job(service)

    assert job.project_id == "giantesses-attack"
    assert job.engine_id == "giantesses-math-engine"
    assert job.game_mode == GameMode.BASE
    assert job.status == JobStatus.QUEUED
    assert job.idempotency_key == "request-1"
    assert job.created_at == job.updated_at
    assert job.created_at.tzinfo is not None


def test_submit_returns_existing_job_for_repeated_request(
    service: OptimizationJobService,
) -> None:
    first = submit_job(service)
    repeated = submit_job(service)

    assert repeated == first
    assert repeated.id == first.id


def test_submit_rejects_reused_key_for_different_request(
    service: OptimizationJobService,
) -> None:
    submit_job(service)

    with pytest.raises(
        OptimizationJobErrors.IdempotencyKeyConflictError,
        match="request-1",
    ):
        submit_job(service, engine_id="another-engine")


def test_get_job_returns_submitted_job(
    service: OptimizationJobService,
) -> None:
    submitted = submit_job(service)

    retrieved = service.get_job(submitted.id)

    assert retrieved == submitted
    assert retrieved is not submitted


def test_get_job_rejects_unknown_job_id(
    service: OptimizationJobService,
) -> None:
    unknown_id = uuid4()

    with pytest.raises(
        OptimizationJobErrors.OptimizationJobNotFoundError,
        match=str(unknown_id),
    ):
        service.get_job(unknown_id)


def test_request_cancellation_updates_and_persists_job(
    service: OptimizationJobService,
) -> None:
    submitted = submit_job(service)

    cancellation_requested = service.request_cancellation(submitted.id)
    persisted = service.get_job(submitted.id)

    assert cancellation_requested.status == JobStatus.CANCELLATION_REQUESTED
    assert cancellation_requested.updated_at >= submitted.updated_at
    assert persisted == cancellation_requested
    assert submitted.status == JobStatus.QUEUED


def test_repeated_cancellation_request_returns_unchanged_job(
    service: OptimizationJobService,
) -> None:
    submitted = submit_job(service)
    first = service.request_cancellation(submitted.id)

    repeated = service.request_cancellation(submitted.id)

    assert repeated == first
    assert repeated.updated_at == first.updated_at


def test_request_cancellation_rejects_unknown_job(
    service: OptimizationJobService,
) -> None:
    unknown_id = uuid4()

    with pytest.raises(
        OptimizationJobErrors.OptimizationJobNotFoundError,
        match=str(unknown_id),
    ):
        service.request_cancellation(unknown_id)


def test_request_cancellation_rejects_terminal_job(
    service: OptimizationJobService,
    job_repository: InMemoryOptimizationJobRepository,
) -> None:
    submitted = submit_job(service)
    completed = submitted.model_copy(update={"status": JobStatus.COMPLETED})
    job_repository.save(completed)

    with pytest.raises(
        OptimizationJobErrors.InvalidJobStatusTransitionError,
        match=JobStatus.COMPLETED.value,
    ):
        service.request_cancellation(submitted.id)


def test_transition_job_updates_and_persists_status(
    service: OptimizationJobService,
) -> None:
    submitted = submit_job(service)

    running = service.transition_job(
        submitted.id,
        JobStatus.RUNNING,
    )
    persisted = service.get_job(submitted.id)

    assert running.status == JobStatus.RUNNING
    assert running.updated_at >= submitted.updated_at
    assert persisted == running
    assert submitted.status == JobStatus.QUEUED


def test_transition_job_retry_returns_unchanged_job(
    service: OptimizationJobService,
) -> None:
    submitted = submit_job(service)
    first = service.transition_job(
        submitted.id,
        JobStatus.RUNNING,
    )

    repeated = service.transition_job(
        submitted.id,
        JobStatus.RUNNING,
    )

    assert repeated == first
    assert repeated.updated_at == first.updated_at


def test_transition_job_rejects_invalid_transition(
    service: OptimizationJobService,
) -> None:
    submitted = submit_job(service)

    with pytest.raises(
        OptimizationJobErrors.InvalidJobStatusTransitionError,
        match="queued to completed",
    ):
        service.transition_job(
            submitted.id,
            JobStatus.COMPLETED,
        )
