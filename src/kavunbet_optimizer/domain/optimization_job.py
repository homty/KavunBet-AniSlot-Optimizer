from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel

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
