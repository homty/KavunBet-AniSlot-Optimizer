from datetime import UTC, datetime
from uuid import uuid4

import pytest

from kavunbet_optimizer.domain.exceptions import OptimizationJobErrors
from kavunbet_optimizer.domain.optimization_job import JobStatus, OptimizationJob
from kavunbet_optimizer.infrastructure.default_configs import create_default_configs
from kavunbet_optimizer.schemas.optimization import GameMode


def make_job(status: JobStatus) -> OptimizationJob:
    created_at = datetime(2026, 1, 1, tzinfo=UTC)

    return OptimizationJob(
        id=uuid4(),
        project_id="giantesses-attack",
        engine_id="giantesses-math-engine",
        game_mode=GameMode.BASE,
        config_snapshot=create_default_configs()[GameMode.BASE],
        status=status,
        idempotency_key="request-1",
        created_at=created_at,
        updated_at=created_at,
    )


@pytest.mark.parametrize(
    "initial_status",
    [JobStatus.QUEUED, JobStatus.RUNNING],
)
def test_request_cancellation_moves_active_job_to_cancellation_requested(
    initial_status: JobStatus,
) -> None:
    job = make_job(initial_status)
    changed_at = datetime(2026, 1, 2, tzinfo=UTC)

    updated = job.request_cancellation(changed_at)

    assert updated.status == JobStatus.CANCELLATION_REQUESTED
    assert updated.updated_at == changed_at
    assert updated is not job
    assert job.status == initial_status
    assert job.updated_at != changed_at


def test_repeated_cancellation_request_returns_unchanged_copy() -> None:
    job = make_job(JobStatus.CANCELLATION_REQUESTED)
    changed_at = datetime(2026, 1, 2, tzinfo=UTC)

    repeated = job.request_cancellation(changed_at)

    assert repeated == job
    assert repeated is not job
    assert repeated.updated_at == job.updated_at


@pytest.mark.parametrize(
    "terminal_status",
    [
        JobStatus.COMPLETED,
        JobStatus.FAILED,
        JobStatus.CANCELLED,
        JobStatus.TIMED_OUT,
    ],
)
def test_request_cancellation_rejects_terminal_job(
    terminal_status: JobStatus,
) -> None:
    job = make_job(terminal_status)

    with pytest.raises(
        OptimizationJobErrors.InvalidJobStatusTransitionError,
        match=terminal_status.value,
    ):
        job.request_cancellation(datetime(2026, 1, 2, tzinfo=UTC))


@pytest.mark.parametrize(
    ("initial_status", "new_status"),
    [
        (JobStatus.QUEUED, JobStatus.RUNNING),
        (JobStatus.RUNNING, JobStatus.COMPLETED),
        (JobStatus.RUNNING, JobStatus.FAILED),
        (JobStatus.RUNNING, JobStatus.TIMED_OUT),
        (
            JobStatus.CANCELLATION_REQUESTED,
            JobStatus.CANCELLED,
        ),
    ],
)
def test_transition_to_allows_worker_transition(
    initial_status: JobStatus,
    new_status: JobStatus,
) -> None:
    job = make_job(initial_status)
    changed_at = datetime(2026, 1, 2, tzinfo=UTC)

    updated = job.transition_to(new_status, changed_at)

    assert updated.status == new_status
    assert updated.updated_at == changed_at
    assert updated is not job
    assert job.status == initial_status
    assert job.updated_at != changed_at


def test_transition_to_same_status_returns_unchanged_copy() -> None:
    job = make_job(JobStatus.COMPLETED)
    changed_at = datetime(2026, 1, 2, tzinfo=UTC)

    repeated = job.transition_to(
        JobStatus.COMPLETED,
        changed_at,
    )

    assert repeated == job
    assert repeated is not job
    assert repeated.updated_at == job.updated_at


@pytest.mark.parametrize(
    ("initial_status", "new_status"),
    [
        (JobStatus.QUEUED, JobStatus.COMPLETED),
        (JobStatus.RUNNING, JobStatus.CANCELLED),
        (
            JobStatus.CANCELLATION_REQUESTED,
            JobStatus.COMPLETED,
        ),
        (JobStatus.COMPLETED, JobStatus.RUNNING),
        (JobStatus.FAILED, JobStatus.COMPLETED),
        (JobStatus.CANCELLED, JobStatus.RUNNING),
        (JobStatus.TIMED_OUT, JobStatus.RUNNING),
    ],
)
def test_transition_to_rejects_forbidden_transition(
    initial_status: JobStatus,
    new_status: JobStatus,
) -> None:
    job = make_job(initial_status)

    with pytest.raises(
        OptimizationJobErrors.InvalidJobStatusTransitionError,
        match=f"from {initial_status} to {new_status}",
    ):
        job.transition_to(
            new_status,
            datetime(2026, 1, 2, tzinfo=UTC),
        )
