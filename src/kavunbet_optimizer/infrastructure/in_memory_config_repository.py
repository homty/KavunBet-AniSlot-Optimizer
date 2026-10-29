from collections.abc import Callable
from threading import RLock
from typing import TypeVar

from kavunbet_optimizer.domain.exceptions import (
    ConfigResourceAlreadyExistsError,
    ConfigResourceIdentityMismatchError,
    ConfigResourceNotFoundError,
    ConfigVersionConflictError,
)
from kavunbet_optimizer.domain.stored_configuration import StoredOptimizationConfig
from kavunbet_optimizer.infrastructure.default_configs import create_default_configs
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

ResultT = TypeVar("ResultT")


class InMemoryOptimizationConfigRepository:
    """In-memory implementation used by tests and local isolated workflows."""

    def __init__(
        self,
        configs: dict[GameMode, OptimizationConfig] | None = None,
    ) -> None:
        initial_configs = configs or create_default_configs()
        self._configs = {
            mode: config.model_copy(deep=True) for mode, config in initial_configs.items()
        }
        self._versions = {mode: 1 for mode in self._configs}
        self._lock = RLock()

    def _after_change(self, mode: GameMode) -> None:
        """Allow persistent repositories to commit a validated mutation."""

    def _commit_mutation(
        self,
        mode: GameMode,
        mutation: Callable[[], ResultT],
    ) -> ResultT:
        with self._lock:
            previous_config = self._configs[mode].model_copy(deep=True)
            previous_version = self._versions[mode]

            try:
                result = mutation()
                self._configs[mode] = OptimizationConfig.model_validate(
                    self._configs[mode].model_dump()
                )
                self._after_change(mode)
                self._versions[mode] = previous_version + 1
                return result
            except Exception:
                self._configs[mode] = previous_config
                self._versions[mode] = previous_version
                raise

    def get(self, mode: GameMode) -> StoredOptimizationConfig:
        with self._lock:
            return StoredOptimizationConfig(
                config=self._configs[mode].model_copy(deep=True),
                version=str(self._versions[mode]),
            )

    def save(
        self,
        mode: GameMode,
        config: OptimizationConfig,
        expected_version: str,
    ) -> StoredOptimizationConfig:
        with self._lock:
            current_version = str(self._versions[mode])
            if expected_version != current_version:
                raise ConfigVersionConflictError(
                    f"configuration version conflict for {mode}: "
                    f"expected {expected_version}, current {current_version}"
                )

            replacement = config.model_copy(deep=True)

            def replace_config() -> None:
                self._configs[mode] = replacement

            self._commit_mutation(mode, replace_config)
            return self.get(mode)

    def get_config(self, mode: GameMode) -> OptimizationConfig:
        with self._lock:
            return self._configs[mode].model_copy(deep=True)

    def get_optimization_settings(self, mode: GameMode) -> OptimizationSettings:
        return self._configs[mode].optimization.model_copy(deep=True)

    def get_objective_settings(self, mode: GameMode) -> ObjectiveSettings:
        return self._configs[mode].objective.model_copy(deep=True)

    def get_targets(self, mode: GameMode) -> list[IntervalTarget]:
        return [target.model_copy(deep=True) for target in self._configs[mode].targets]

    def get_expected_ways_targets(self, mode: GameMode) -> list[ExpectedWaysTarget]:
        return [
            target.model_copy(deep=True) for target in self._configs[mode].expected_ways_targets
        ]

    def get_group_rtp_targets(self, mode: GameMode) -> list[GroupRtpTarget]:
        return [target.model_copy(deep=True) for target in self._configs[mode].group_rtp_targets]

    def get_constraints(self, mode: GameMode) -> Constraints:
        return self._configs[mode].constraints.model_copy(deep=True)

    def _find_target_index(self, mode: GameMode, symbol: str, kind: int) -> int:
        for index, target in enumerate(self._configs[mode].targets):
            if target.symbol == symbol and target.kind == kind:
                return index

        raise ConfigResourceNotFoundError(f"target not found: {symbol}/{kind}")

    def _find_expected_ways_target_index(
        self,
        mode: GameMode,
        symbol: str,
        kind: int,
    ) -> int:
        for index, target in enumerate(self._configs[mode].expected_ways_targets):
            if target.symbol == symbol and target.kind == kind:
                return index

        raise ConfigResourceNotFoundError(f"expected-ways target not found: {symbol}/{kind}")

    def _find_group_rtp_target_index(self, mode: GameMode, name: str) -> int:
        for index, target in enumerate(self._configs[mode].group_rtp_targets):
            if target.name == name:
                return index

        raise ConfigResourceNotFoundError(f"group RTP target not found: {name}")

    def patch_optimization_settings(
        self,
        mode: GameMode,
        patch: OptimizationSettingsPatch,
    ) -> OptimizationSettings:
        def mutation() -> OptimizationSettings:
            current_data = self._configs[mode].optimization.model_dump()
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
            self._configs[mode].optimization = updated
            return updated

        return self._commit_mutation(mode, mutation)

    def patch_objective_settings(
        self,
        mode: GameMode,
        patch: ObjectiveSettingsPatch,
    ) -> ObjectiveSettings:
        def mutation() -> ObjectiveSettings:
            current_data = self._configs[mode].objective.model_dump()
            current_data.update(patch.model_dump(exclude_unset=True))
            updated = ObjectiveSettings.model_validate(current_data)
            self._configs[mode].objective = updated
            return updated

        return self._commit_mutation(mode, mutation)

    def patch_target(
        self,
        mode: GameMode,
        symbol: str,
        kind: int,
        patch: IntervalTargetPatch,
    ) -> IntervalTarget:
        def mutation() -> IntervalTarget:
            index = self._find_target_index(mode, symbol, kind)
            current_data = self._configs[mode].targets[index].model_dump()
            current_data.update(patch.model_dump(exclude_unset=True))
            updated = IntervalTarget.model_validate(current_data)
            self._configs[mode].targets[index] = updated
            return updated

        return self._commit_mutation(mode, mutation)

    def add_target(self, mode: GameMode, target: IntervalTarget) -> IntervalTarget:
        def mutation() -> IntervalTarget:
            if any(
                current.symbol == target.symbol and current.kind == target.kind
                for current in self._configs[mode].targets
            ):
                raise ConfigResourceAlreadyExistsError(
                    f"target already exists: {target.symbol}/{target.kind}"
                )

            self._configs[mode].targets.append(target.model_copy(deep=True))
            return target

        return self._commit_mutation(mode, mutation)

    def replace_target(
        self,
        mode: GameMode,
        symbol: str,
        kind: int,
        target: IntervalTarget,
    ) -> IntervalTarget:
        if target.symbol != symbol or target.kind != kind:
            raise ConfigResourceIdentityMismatchError(
                "target body identity must match the URL identity"
            )

        def mutation() -> IntervalTarget:
            index = self._find_target_index(mode, symbol, kind)
            self._configs[mode].targets[index] = target.model_copy(deep=True)
            return target

        return self._commit_mutation(mode, mutation)

    def delete_target(self, mode: GameMode, symbol: str, kind: int) -> None:
        def mutation() -> None:
            index = self._find_target_index(mode, symbol, kind)
            self._configs[mode].targets.pop(index)

        self._commit_mutation(mode, mutation)

    def patch_expected_ways_target(
        self,
        mode: GameMode,
        symbol: str,
        kind: int,
        patch: ExpectedWaysTargetPatch,
    ) -> ExpectedWaysTarget:
        def mutation() -> ExpectedWaysTarget:
            index = self._find_expected_ways_target_index(mode, symbol, kind)
            current_data = self._configs[mode].expected_ways_targets[index].model_dump()
            current_data.update(patch.model_dump(exclude_unset=True))
            updated = ExpectedWaysTarget.model_validate(current_data)
            self._configs[mode].expected_ways_targets[index] = updated
            return updated

        return self._commit_mutation(mode, mutation)

    def add_expected_ways_target(
        self,
        mode: GameMode,
        target: ExpectedWaysTarget,
    ) -> ExpectedWaysTarget:
        def mutation() -> ExpectedWaysTarget:
            if any(
                current.symbol == target.symbol and current.kind == target.kind
                for current in self._configs[mode].expected_ways_targets
            ):
                raise ConfigResourceAlreadyExistsError(
                    f"expected-ways target already exists: {target.symbol}/{target.kind}"
                )

            self._configs[mode].expected_ways_targets.append(target.model_copy(deep=True))
            return target

        return self._commit_mutation(mode, mutation)

    def replace_expected_ways_target(
        self,
        mode: GameMode,
        symbol: str,
        kind: int,
        target: ExpectedWaysTarget,
    ) -> ExpectedWaysTarget:
        if target.symbol != symbol or target.kind != kind:
            raise ConfigResourceIdentityMismatchError(
                "expected-ways target body identity must match the URL identity"
            )

        def mutation() -> ExpectedWaysTarget:
            index = self._find_expected_ways_target_index(mode, symbol, kind)
            self._configs[mode].expected_ways_targets[index] = target.model_copy(deep=True)
            return target

        return self._commit_mutation(mode, mutation)

    def delete_expected_ways_target(
        self,
        mode: GameMode,
        symbol: str,
        kind: int,
    ) -> None:
        def mutation() -> None:
            index = self._find_expected_ways_target_index(mode, symbol, kind)
            self._configs[mode].expected_ways_targets.pop(index)

        self._commit_mutation(mode, mutation)

    def patch_group_rtp_target(
        self,
        mode: GameMode,
        name: str,
        patch: GroupRtpTargetPatch,
    ) -> GroupRtpTarget:
        def mutation() -> GroupRtpTarget:
            index = self._find_group_rtp_target_index(mode, name)
            current_data = self._configs[mode].group_rtp_targets[index].model_dump()
            current_data.update(patch.model_dump(exclude_unset=True))
            updated = GroupRtpTarget.model_validate(current_data)
            self._configs[mode].group_rtp_targets[index] = updated
            return updated

        return self._commit_mutation(mode, mutation)

    def add_group_rtp_target(
        self,
        mode: GameMode,
        target: GroupRtpTarget,
    ) -> GroupRtpTarget:
        def mutation() -> GroupRtpTarget:
            if any(
                current.name == target.name for current in self._configs[mode].group_rtp_targets
            ):
                raise ConfigResourceAlreadyExistsError(
                    f"group RTP target already exists: {target.name}"
                )

            self._configs[mode].group_rtp_targets.append(target.model_copy(deep=True))
            return target

        return self._commit_mutation(mode, mutation)

    def replace_group_rtp_target(
        self,
        mode: GameMode,
        name: str,
        target: GroupRtpTarget,
    ) -> GroupRtpTarget:
        if target.name != name:
            raise ConfigResourceIdentityMismatchError(
                "group RTP target body identity must match the URL identity"
            )

        def mutation() -> GroupRtpTarget:
            index = self._find_group_rtp_target_index(mode, name)
            self._configs[mode].group_rtp_targets[index] = target.model_copy(deep=True)
            return target

        return self._commit_mutation(mode, mutation)

    def delete_group_rtp_target(self, mode: GameMode, name: str) -> None:
        def mutation() -> None:
            index = self._find_group_rtp_target_index(mode, name)
            self._configs[mode].group_rtp_targets.pop(index)

        self._commit_mutation(mode, mutation)

    def patch_constraints(
        self,
        mode: GameMode,
        patch: ConstraintsPatch,
    ) -> Constraints:
        def mutation() -> Constraints:
            current_data = self._configs[mode].constraints.model_dump()
            current_data.update(patch.model_dump(exclude_unset=True))
            updated = Constraints.model_validate(current_data)
            self._configs[mode].constraints = updated
            return updated

        return self._commit_mutation(mode, mutation)
