from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

PositiveInt = Annotated[int, Field(gt=0)]
NonNegativeInt = Annotated[int, Field(ge=0)]
GlobalCountRange = tuple[NonNegativeInt, NonNegativeInt]


class Constraints(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # The upper bound for each reel number depends on the complete game's reel count.
    last_allowed_reel: dict[str, PositiveInt] = Field(default_factory=dict)
    max_consecutive: dict[str, PositiveInt] = Field(default_factory=dict)
    global_count_ranges: dict[str, GlobalCountRange] = Field(default_factory=dict)
    composition_symbols: list[str] = Field(default_factory=list)

    @field_validator("global_count_ranges")
    @classmethod
    def validate_global_count_ranges(
        cls,
        ranges: dict[str, GlobalCountRange],
    ) -> dict[str, GlobalCountRange]:
        for symbol, (minimum, maximum) in ranges.items():
            if maximum < minimum:
                raise ValueError(f"{symbol}: global count maximum cannot be less than minimum")

        return ranges


class ConstraintsPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    last_allowed_reel: dict[str, PositiveInt] | None = None
    max_consecutive: dict[str, PositiveInt] | None = None
    global_count_ranges: dict[str, GlobalCountRange] | None = None
    composition_symbols: list[str] | None = None

    @field_validator("global_count_ranges")
    @classmethod
    def validate_global_count_ranges(
        cls,
        ranges: dict[str, GlobalCountRange] | None,
    ) -> dict[str, GlobalCountRange] | None:
        if ranges is None:
            return None

        for symbol, (minimum, maximum) in ranges.items():
            if maximum < minimum:
                raise ValueError(f"{symbol}: global count maximum cannot be less than minimum")

        return ranges
