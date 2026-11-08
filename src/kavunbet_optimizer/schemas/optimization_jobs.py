from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from kavunbet_optimizer.domain.optimization_job import JobStatus
from kavunbet_optimizer.schemas.optimization import GameMode


class OptimizationJobCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    project_id: str = Field(min_length=1)
    engine_id: str = Field(min_length=1)
    game_mode: GameMode


class OptimizationJobResponse(BaseModel):
    id: UUID
    project_id: str
    engine_id: str
    game_mode: GameMode
    status: JobStatus
    created_at: datetime
    updated_at: datetime
