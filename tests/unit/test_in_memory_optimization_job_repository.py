from datetime import UTC, datetime
from uuid import uuid4

import pytest

from kavunbet_optimizer.domain.exceptions import (
    IdempotencyKeyConflictError,
    OptimizationJobAlreadyExistsError,
    OptimizationJobNotFoundError,
)
from kavunbet_optimizer.domain.optimization_job import (
    JobStatus,
    OptimizationJob,
)
from kavunbet_optimizer.infrastructure.default_configs import (
    create_default_configs,
)
from kavunbet_optimizer.infrastructure.in_memory_optimization_job_repository import (
    InMemoryOptimizationJobRepository,
)
from kavunbet_optimizer.schemas.optimization import GameMode


def make_job(
    idempotency_key: str = "request-1",
) -> OptimizationJob:
    now = datetime.now(UTC)

    return OptimizationJob(
        id=uuid4(),
        project_id="giantesses-attack",
        engine_id="giantesses-math-engine",
        game_mode=GameMode.BASE,
        config_snapshot=create_default_configs()[GameMode.BASE],
        status=JobStatus.QUEUED,
        idempotency_key=idempotency_key,
        created_at=now,
        updated_at=now,
    )


def test_create_stores_and_returns_job() -> None:
    repository = InMemoryOptimizationJobRepository()
    job = make_job()

    created = repository.create(job)
    retrieved = repository.get(job.id)

    assert created == job
    assert retrieved == job
    assert created is not job
    assert retrieved is not created
    assert retrieved.config_snapshot is not job.config_snapshot


def test_create_rejects_duplicate_job_id() -> None:
    repository = InMemoryOptimizationJobRepository()
    job = make_job()

    repository.create(job)

    with pytest.raises(OptimizationJobAlreadyExistsError, match=str(job.id)):
        repository.create(job)


def test_create_rejects_duplicate_idempotency_key() -> None:
    repository = InMemoryOptimizationJobRepository()
    first_job = make_job(idempotency_key="same-request")
    second_job = make_job(idempotency_key="same-request")

    repository.create(first_job)

    with pytest.raises(
        IdempotencyKeyConflictError,
        match="same-request",
    ):
        repository.create(second_job)


def test_get_rejects_unknown_job_id() -> None:
    repository = InMemoryOptimizationJobRepository()
    unknown_id = uuid4()

    with pytest.raises(
        OptimizationJobNotFoundError,
        match=str(unknown_id),
    ):
        repository.get(unknown_id)


def test_get_by_idempotency_key_returns_none_when_unknown() -> None:
    repository = InMemoryOptimizationJobRepository()

    result = repository.get_by_idempotency_key("unknown-request")

    assert result is None


def test_get_by_idempotency_key_returns_independent_job() -> None:
    repository = InMemoryOptimizationJobRepository()
    job = make_job(idempotency_key="known-request")
    repository.create(job)

    retrieved = repository.get_by_idempotency_key("known-request")

    assert retrieved == job
    assert retrieved is not job
    assert retrieved.config_snapshot is not job.config_snapshot


def test_save_updates_existing_job() -> None:
    repository = InMemoryOptimizationJobRepository()
    job = make_job()
    repository.create(job)

    updated = job.model_copy(
        update={
            "status": JobStatus.RUNNING,
            "updated_at": datetime.now(UTC),
        },
        deep=True,
    )

    saved = repository.save(updated)
    retrieved = repository.get(job.id)

    assert saved == updated
    assert retrieved == updated
    assert saved is not updated
    assert retrieved is not saved
    assert retrieved.status == JobStatus.RUNNING


def test_save_rejects_unknown_job() -> None:
    repository = InMemoryOptimizationJobRepository()
    job = make_job()

    with pytest.raises(
        OptimizationJobNotFoundError,
        match=str(job.id),
    ):
        repository.save(job)


def test_save_rejects_idempotency_key_owned_by_another_job() -> None:
    repository = InMemoryOptimizationJobRepository()
    first_job = make_job(idempotency_key="first-request")
    second_job = make_job(idempotency_key="second-request")

    repository.create(first_job)
    repository.create(second_job)

    conflicting_update = second_job.model_copy(update={"idempotency_key": "first-request"})

    with pytest.raises(
        IdempotencyKeyConflictError,
        match="first-request",
    ):
        repository.save(conflicting_update)


def test_save_reindexes_changed_idempotency_key() -> None:
    repository = InMemoryOptimizationJobRepository()
    job = make_job(idempotency_key="old-request")
    repository.create(job)

    updated = job.model_copy(update={"idempotency_key": "new-request"})
    repository.save(updated)

    assert repository.get_by_idempotency_key("old-request") is None
    assert repository.get_by_idempotency_key("new-request") == updated
