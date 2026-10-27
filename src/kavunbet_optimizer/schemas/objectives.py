from pydantic import BaseModel, ConfigDict, Field, field_validator


class ObjectiveSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    progression_weight: float = Field(ge=0)
    symbol_order_weight: float = Field(ge=0)
    preserve_untargeted_weight: float = Field(ge=0)
    preserve_untargeted_tolerance: float = Field(ge=0, lt=1)
    preserve_untargeted_ways_weight: float = Field(ge=0)
    preserve_untargeted_ways_tolerance: float = Field(ge=0, lt=1)
    frequency_orders: list[list[str]]

    @field_validator("frequency_orders")
    @classmethod
    def validate_frequency_orders(
        cls,
        orders: list[list[str]],
    ) -> list[list[str]]:
        for order in orders:
            if len(order) < 2:
                raise ValueError("every frequency order needs at least two symbols")

            if len(set(order)) != len(order):
                raise ValueError("symbols in a frequency order must be unique")

        return orders


class ObjectiveSettingsPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    progression_weight: float | None = Field(default=None, ge=0)
    symbol_order_weight: float | None = Field(default=None, ge=0)
    preserve_untargeted_weight: float | None = Field(default=None, ge=0)
    preserve_untargeted_tolerance: float | None = Field(default=None, ge=0, lt=1)
    preserve_untargeted_ways_weight: float | None = Field(default=None, ge=0)
    preserve_untargeted_ways_tolerance: float | None = Field(default=None, ge=0, lt=1)
    frequency_orders: list[list[str]] | None = None

    @field_validator("frequency_orders")
    @classmethod
    def validate_frequency_orders(
        cls,
        orders: list[list[str]] | None,
    ) -> list[list[str]] | None:
        if orders is None:
            return None

        for order in orders:
            if len(order) < 2:
                raise ValueError("every frequency order needs at least two symbols")

            if len(set(order)) != len(order):
                raise ValueError("symbols in a frequency order must be unique")

        return orders
