from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from kavunbet_optimizer.domain.reel_artifact import StoredReelArtifact
from kavunbet_optimizer.schemas.optimization import GameMode


class OptimizationResultArtifact(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True
    )  # Once stored, the result represents an immutable historical output.

    id: UUID
    job_id: UUID
    game_mode: GameMode
    reels: StoredReelArtifact
    initial_penalty: float = Field(ge=0)
    final_penalty: float = Field(ge=0)
    iterations: int = Field(ge=0)
    accepted_moves: int = Field(ge=0)
    created_at: datetime

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if self.final_penalty > self.initial_penalty:
            raise ValueError("final penalty cannot exceed initial penalty")

        if self.accepted_moves > self.iterations:
            raise ValueError("accepted moves cannot exceed completed iterations")

        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")

        return self
