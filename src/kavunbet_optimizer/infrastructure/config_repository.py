from kavunbet_optimizer.infrastructure.default_configs import (
    create_default_constraints,
    create_default_expected_ways_targets,
    create_default_group_rtp_targets,
    create_default_objectives,
    create_default_optimization_settings,
    create_default_targets,
)
from kavunbet_optimizer.schemas.constraints import Constraints, ConstraintsPatch
from kavunbet_optimizer.schemas.expected_ways_targets import (
    ExpectedWaysTarget,
    ExpectedWaysTargetPatch,
)
from kavunbet_optimizer.schemas.group_rtp_targets import GroupRtpTarget, GroupRtpTargetPatch
from kavunbet_optimizer.schemas.objectives import (
    ObjectiveSettings,
    ObjectiveSettingsPatch,
)
from kavunbet_optimizer.schemas.optimization import (
    GameMode,
    OptimizationSettings,
    OptimizationSettingsPatch,
)
from kavunbet_optimizer.schemas.targets import (
    IntervalTarget,
    IntervalTargetPatch,
)


class OptimizationConfigRepository:
    """Temporary in-memory repository until persistent storage is added."""

    def __init__(self) -> None:
        self._settings = create_default_optimization_settings()
        self._objectives = create_default_objectives()
        self._targets = create_default_targets()
        self._expected_ways_targets = create_default_expected_ways_targets()
        self._group_rtp_targets = create_default_group_rtp_targets()
        self._constraints = create_default_constraints()

    def get_optimization_settings(self, mode: GameMode) -> OptimizationSettings:
        return self._settings[mode]

    def get_objective_settings(self, mode: GameMode) -> ObjectiveSettings:
        return self._objectives[mode]

    def get_targets(self, mode: GameMode) -> list[IntervalTarget]:
        return self._targets[mode]

    def get_expected_ways_targets(self, mode: GameMode) -> list[ExpectedWaysTarget]:
        return self._expected_ways_targets[mode]

    def get_group_rtp_targets(self, mode: GameMode) -> list[GroupRtpTarget]:
        return self._group_rtp_targets[mode]

    def get_constraints(self, mode: GameMode) -> Constraints:
        return self._constraints[mode]

    def patch_optimization_settings(
        self,
        mode: GameMode,
        patch: OptimizationSettingsPatch,
    ) -> OptimizationSettings:
        current = self._settings[mode]
        current_data = current.model_dump()
        patch_data = patch.model_dump(
            exclude_unset=True
        )  # Include only fields explicitly supplied in the PATCH request.

        # Remove moves from the top-level patch because nested move fields
        # must be merged separately instead of replacing the entire object.
        moves_was_provided = "moves" in patch_data
        moves_patch = patch_data.pop("moves", None)
        current_data.update(patch_data)

        if moves_was_provided:
            if moves_patch is None:
                current_data["moves"] = None
            else:
                current_data["moves"].update(moves_patch)

        updated = OptimizationSettings.model_validate(current_data)
        self._settings[mode] = updated

        return updated

    def patch_objective_settings(
        self,
        mode: GameMode,
        patch: ObjectiveSettingsPatch,
    ) -> ObjectiveSettings:
        current = self._objectives[mode]
        current_data = current.model_dump()
        patch_data = patch.model_dump(exclude_unset=True)

        current_data.update(patch_data)
        updated = ObjectiveSettings.model_validate(current_data)
        self._objectives[mode] = updated

        return updated

    def patch_target(
        self,
        mode: GameMode,
        symbol: str,
        kind: int,
        patch: IntervalTargetPatch,
    ) -> IntervalTarget:
        for index, current in enumerate(self._targets[mode]):
            if current.symbol == symbol and current.kind == kind:
                current_data = current.model_dump()
                patch_data = patch.model_dump(exclude_unset=True)

                current_data.update(patch_data)
                updated = IntervalTarget.model_validate(current_data)
                self._targets[mode][index] = updated

                return updated

        raise KeyError(f"target not found: {symbol}/{kind}")

    def patch_expected_ways_targets(
        self, mode: GameMode, symbol: str, kind: int, patch: ExpectedWaysTargetPatch
    ) -> ExpectedWaysTarget:
        for index, current in enumerate(self._expected_ways_targets[mode]):
            if current.symbol == symbol and current.kind == kind:
                current_data = current.model_dump()
                patch_data = patch.model_dump(exclude_unset=True)

                current_data.update(patch_data)
                updated = ExpectedWaysTarget.model_validate(current_data)
                self._expected_ways_targets[mode][index] = updated

                return updated
        raise KeyError(f"target not found: {symbol}/{kind}")

    def patch_group_rtp_target(
        self, mode: GameMode, name: str, patch: GroupRtpTargetPatch
    ) -> GroupRtpTarget:
        for index, current in enumerate(self._group_rtp_targets[mode]):
            if current.name == name:
                current_data = current.model_dump()
                patch_data = patch.model_dump(exclude_unset=True)

                current_data.update(patch_data)
                updated = GroupRtpTarget.model_validate(current_data)
                self._group_rtp_targets[mode][index] = updated

                return updated
        raise KeyError(f"group RTP target not found: {name}")

    def patch_constraints(
        self,
        mode: GameMode,
        patch: ConstraintsPatch,
    ) -> Constraints:
        current = self._constraints[mode]
        current_data = current.model_dump()
        patch_data = patch.model_dump(exclude_unset=True)

        current_data.update(patch_data)
        updated = Constraints.model_validate(current_data)
        self._constraints[mode] = updated

        return updated
