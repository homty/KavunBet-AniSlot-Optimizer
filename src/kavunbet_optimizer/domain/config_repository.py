from typing import Protocol

from kavunbet_optimizer.schemas.configuration import OptimizationConfig
from kavunbet_optimizer.schemas.constraints import Constraints, ConstraintsPatch
from kavunbet_optimizer.schemas.expected_ways_targets import (
    ExpectedWaysTarget,
    ExpectedWaysTargetPatch,
)
from kavunbet_optimizer.schemas.group_rtp_targets import GroupRtpTarget, GroupRtpTargetPatch
from kavunbet_optimizer.schemas.objectives import ObjectiveSettings, ObjectiveSettingsPatch
from kavunbet_optimizer.schemas.optimization import (
    GameMode,
    OptimizationSettings,
    OptimizationSettingsPatch,
)
from kavunbet_optimizer.schemas.targets import IntervalTarget, IntervalTargetPatch


class OptimizationConfigRepository(Protocol):
    def get_config(self, mode: GameMode) -> OptimizationConfig: ...

    def get_optimization_settings(self, mode: GameMode) -> OptimizationSettings: ...

    def patch_optimization_settings(
        self,
        mode: GameMode,
        patch: OptimizationSettingsPatch,
    ) -> OptimizationSettings: ...

    def get_objective_settings(self, mode: GameMode) -> ObjectiveSettings: ...

    def patch_objective_settings(
        self,
        mode: GameMode,
        patch: ObjectiveSettingsPatch,
    ) -> ObjectiveSettings: ...

    def get_targets(self, mode: GameMode) -> list[IntervalTarget]: ...

    def add_target(self, mode: GameMode, target: IntervalTarget) -> IntervalTarget: ...

    def replace_target(
        self,
        mode: GameMode,
        symbol: str,
        kind: int,
        target: IntervalTarget,
    ) -> IntervalTarget: ...

    def patch_target(
        self,
        mode: GameMode,
        symbol: str,
        kind: int,
        patch: IntervalTargetPatch,
    ) -> IntervalTarget: ...

    def delete_target(self, mode: GameMode, symbol: str, kind: int) -> None: ...

    def get_expected_ways_targets(self, mode: GameMode) -> list[ExpectedWaysTarget]: ...

    def add_expected_ways_target(
        self,
        mode: GameMode,
        target: ExpectedWaysTarget,
    ) -> ExpectedWaysTarget: ...

    def replace_expected_ways_target(
        self,
        mode: GameMode,
        symbol: str,
        kind: int,
        target: ExpectedWaysTarget,
    ) -> ExpectedWaysTarget: ...

    def patch_expected_ways_target(
        self,
        mode: GameMode,
        symbol: str,
        kind: int,
        patch: ExpectedWaysTargetPatch,
    ) -> ExpectedWaysTarget: ...

    def delete_expected_ways_target(
        self,
        mode: GameMode,
        symbol: str,
        kind: int,
    ) -> None: ...

    def get_group_rtp_targets(self, mode: GameMode) -> list[GroupRtpTarget]: ...

    def add_group_rtp_target(
        self,
        mode: GameMode,
        target: GroupRtpTarget,
    ) -> GroupRtpTarget: ...

    def replace_group_rtp_target(
        self,
        mode: GameMode,
        name: str,
        target: GroupRtpTarget,
    ) -> GroupRtpTarget: ...

    def patch_group_rtp_target(
        self,
        mode: GameMode,
        name: str,
        patch: GroupRtpTargetPatch,
    ) -> GroupRtpTarget: ...

    def delete_group_rtp_target(self, mode: GameMode, name: str) -> None: ...

    def get_constraints(self, mode: GameMode) -> Constraints: ...

    def patch_constraints(
        self,
        mode: GameMode,
        patch: ConstraintsPatch,
    ) -> Constraints: ...
