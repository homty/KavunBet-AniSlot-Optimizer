from datetime import datetime
from enum import StrEnum
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from kavunbet_optimizer.domain.exceptions import OptimizationJobErrors
from kavunbet_optimizer.schemas.configuration import OptimizationConfig
from kavunbet_optimizer.schemas.optimization import GameMode


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLATION_REQUESTED = "cancellation_requested"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


WORKER_STATUS_TRANSITIONS: dict[JobStatus, frozenset[JobStatus]] = {
    JobStatus.QUEUED: frozenset(
        {
            JobStatus.RUNNING,
        }
    ),
    JobStatus.RUNNING: frozenset(
        {
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.TIMED_OUT,
        }
    ),
    JobStatus.CANCELLATION_REQUESTED: frozenset({JobStatus.CANCELLED}),
}


class OptimizationJob(BaseModel):
    id: UUID
    project_id: str
    engine_id: str
    game_mode: GameMode
    config_snapshot: OptimizationConfig
    status: JobStatus
    idempotency_key: str
    created_at: datetime
    updated_at: datetime

    def request_cancellation(self, changed_at: datetime) -> Self:
        if self.status == JobStatus.CANCELLATION_REQUESTED:
            return self.model_copy(deep=True)

        if self.status not in {
            JobStatus.QUEUED,
            JobStatus.RUNNING,
        }:
            raise OptimizationJobErrors.InvalidJobStatusTransitionError(
                f"cannot request cancellation for job {self.id} with status {self.status}"
            )
        return self.model_copy(
            update={"status": JobStatus.CANCELLATION_REQUESTED, "updated_at": changed_at},
            deep=True,
        )

    def transition_to(self, new_status: JobStatus, changed_at: datetime) -> Self:
        if self.status == new_status:
            return self.model_copy(deep=True)

        allowed_statuses = WORKER_STATUS_TRANSITIONS.get(self.status, frozenset())
        if new_status not in allowed_statuses:
            raise OptimizationJobErrors.InvalidJobStatusTransitionError(
                f"cannot transition job {self.id} from {self.status} to {new_status}"
            )

        return self.model_copy(
            update={
                "status": new_status,
                "updated_at": changed_at,
            },
            deep=True,
        )
