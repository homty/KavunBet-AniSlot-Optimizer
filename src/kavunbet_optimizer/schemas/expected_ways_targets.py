from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExpectedWaysTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1)
    kind: Literal[3, 4, 5, 6]
    min_ways: float = Field(gt=0)
    max_ways: float = Field(gt=0)
    weight: float = Field(default=1.0, gt=0)

    @model_validator(mode="after")
    def validate_ways_range(self) -> Self:
        if self.max_ways < self.min_ways:
            raise ValueError("max_ways cannot be less than min_ways")

        return self


class ExpectedWaysTargetPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_ways: float | None = Field(default=None, gt=0)
    max_ways: float | None = Field(default=None, gt=0)
    weight: float | None = Field(default=None, gt=0)
