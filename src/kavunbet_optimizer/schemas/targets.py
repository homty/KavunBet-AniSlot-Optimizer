from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class IntervalTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1)
    kind: Literal[3, 4, 5, 6]
    min_interval: float = Field(gt=0)
    max_interval: float = Field(gt=0)
    weight: float = Field(default=1.0, gt=0)

    @model_validator(mode="after")
    def validate_interval(self) -> Self:
        if self.max_interval < self.min_interval:
            raise ValueError("max_interval cannot be less than min_interval")
        return self


class IntervalTargetPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_interval: float | None = Field(default=None, gt=0)
    max_interval: float | None = Field(default=None, gt=0)
    weight: float | None = Field(default=None, gt=0)
