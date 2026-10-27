from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GameMode(StrEnum):
    BASE = "base"
    FREE = "free"


class MoveWeights(BaseModel):
    within_reel: float = Field(ge=0)
    cross_reel: float = Field(ge=0)
    composition: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_total_weight(self) -> Self:
        total = self.within_reel + self.cross_reel + self.composition
        if total <= 0:
            raise ValueError("move weights must sum above zero")
        return self


class MoveWeightsPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    within_reel: float | None = Field(default=None, ge=0)
    cross_reel: float | None = Field(default=None, ge=0)
    composition: float | None = Field(default=None, ge=0)


class OptimizationSettings(BaseModel):
    iterations: int = Field(gt=0)
    seed: int
    start_temperature: float = Field(gt=0)
    end_temperature: float = Field(gt=0)
    report_every: int = Field(ge=0)
    moves: MoveWeights


class OptimizationSettingsPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    iterations: int | None = Field(default=None, gt=0)
    seed: int | None = None
    start_temperature: float | None = Field(default=None, gt=0)
    end_temperature: float | None = Field(default=None, gt=0)
    report_every: int | None = Field(default=None, ge=0)
    moves: MoveWeightsPatch | None = None
