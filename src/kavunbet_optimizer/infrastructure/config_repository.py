from kavunbet_optimizer.schemas.optimization import (
    GameMode,
    MoveWeights,
    OptimizationSettings,
    OptimizationSettingsPatch,
)


class OptimizationConfigRepository:
    """Temporary in-memory repository until persistent storage is added."""

    def __init__(self) -> None:
        self._settings: dict[GameMode, OptimizationSettings] = {
            GameMode.BASE: OptimizationSettings(
                iterations=50_000,
                seed=42,
                start_temperature=0.2,
                end_temperature=0.0001,
                report_every=5_000,
                moves=MoveWeights(
                    within_reel=0.55,
                    cross_reel=0.45,
                    composition=0.0,
                ),
            ),
            GameMode.FREE: OptimizationSettings(
                iterations=50_000,
                seed=42,
                start_temperature=0.2,
                end_temperature=0.0001,
                report_every=5_000,
                moves=MoveWeights(
                    within_reel=0.15,
                    cross_reel=0.10,
                    composition=0.75,
                ),
            ),
        }

    def get_optimization_settings(self, mode: GameMode) -> OptimizationSettings:
        return self._settings[mode]

    def patch_optimization_settings(
        self,
        mode: GameMode,
        patch: OptimizationSettingsPatch,
    ) -> OptimizationSettings:
        current = self._settings[mode]
        current_data = current.model_dump()
        patch_data = patch.model_dump(exclude_unset=True)

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
