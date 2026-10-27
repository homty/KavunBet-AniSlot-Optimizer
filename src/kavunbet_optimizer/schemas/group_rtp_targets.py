from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class GroupRtpTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    symbols: list[str] = Field(min_length=1)
    min_natural_rtp_pct: float = Field(gt=0)
    max_natural_rtp_pct: float = Field(gt=0)
    weight: float = Field(default=1.0, gt=0)

    @field_validator("symbols")
    @classmethod
    def validate_unique_symbols(
        cls,
        symbols: list[str],
    ) -> list[str]:
        if len(set(symbols)) != len(symbols):
            raise ValueError("group RTP target symbols must be unique")

        return symbols

    @model_validator(mode="after")
    def validate_rtp_range(self) -> Self:
        if self.max_natural_rtp_pct < self.min_natural_rtp_pct:
            raise ValueError("max_natural_rtp_pct cannot be less than min_natural_rtp_pct")

        return self


class GroupRtpTargetPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbols: list[str] | None = Field(default=None, min_length=1)
    min_natural_rtp_pct: float | None = Field(default=None, gt=0)
    max_natural_rtp_pct: float | None = Field(default=None, gt=0)
    weight: float | None = Field(default=None, gt=0)

    @field_validator("symbols")
    @classmethod
    def validate_unique_symbols(
        cls,
        symbols: list[str] | None,
    ) -> list[str] | None:
        if symbols is None:
            return None

        if len(set(symbols)) != len(symbols):
            raise ValueError("group RTP target symbols must be unique")

        return symbols
