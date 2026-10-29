from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from kavunbet_optimizer.schemas.constraints import Constraints
from kavunbet_optimizer.schemas.expected_ways_targets import ExpectedWaysTarget
from kavunbet_optimizer.schemas.group_rtp_targets import GroupRtpTarget
from kavunbet_optimizer.schemas.objectives import ObjectiveSettings
from kavunbet_optimizer.schemas.optimization import OptimizationSettings
from kavunbet_optimizer.schemas.targets import IntervalTarget


class OptimizationConfig(BaseModel):
    """Complete configuration owned and validated by the Optimizer service."""

    model_config = ConfigDict(extra="forbid")

    symbols: list[str] = Field(min_length=1)
    optimization: OptimizationSettings
    objective: ObjectiveSettings
    targets: list[IntervalTarget] = Field(default_factory=list)
    expected_ways_targets: list[ExpectedWaysTarget] = Field(default_factory=list)
    group_rtp_targets: list[GroupRtpTarget] = Field(default_factory=list)
    constraints: Constraints = Field(default_factory=Constraints)

    @model_validator(mode="after")
    def validate_complete_configuration(self) -> Self:
        symbol_set = set(self.symbols)
        if len(symbol_set) != len(self.symbols):
            raise ValueError("symbols must be unique")

        target_identities = [(target.symbol, target.kind) for target in self.targets]
        if len(set(target_identities)) != len(target_identities):
            raise ValueError("target identities must be unique")

        expected_identities = [
            (target.symbol, target.kind) for target in self.expected_ways_targets
        ]
        if len(set(expected_identities)) != len(expected_identities):
            raise ValueError("expected-ways target identities must be unique")

        group_names = [target.name for target in self.group_rtp_targets]
        if len(set(group_names)) != len(group_names):
            raise ValueError("group RTP target names must be unique")

        referenced_symbols = {
            target.symbol for target in [*self.targets, *self.expected_ways_targets]
        }
        for target in self.group_rtp_targets:
            referenced_symbols.update(target.symbols)
        for order in self.objective.frequency_orders:
            referenced_symbols.update(order)
        referenced_symbols.update(self.constraints.last_allowed_reel)
        referenced_symbols.update(self.constraints.max_consecutive)
        referenced_symbols.update(self.constraints.global_count_ranges)
        referenced_symbols.update(self.constraints.composition_symbols)

        unknown_symbols = referenced_symbols - symbol_set
        if unknown_symbols:
            raise ValueError(f"configuration uses unknown symbols: {sorted(unknown_symbols)}")

        return self
