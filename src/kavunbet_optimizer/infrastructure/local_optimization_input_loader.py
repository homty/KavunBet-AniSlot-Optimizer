from dataclasses import dataclass
from pathlib import Path

from kavunbet_optimizer.domain.optimization_input import (
    OptimizationInput,
    ReelSetComponent,
)
from kavunbet_optimizer.domain.reel_set import ReelSet
from kavunbet_optimizer.infrastructure.reel_csv_codec import ReelCsvCodec
from kavunbet_optimizer.schemas.optimization import GameMode


@dataclass(frozen=True, slots=True)
class LocalReelFile:
    filename: str
    weight: float
    substitutes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class LocalOptimizationInputDefinition:
    source: LocalReelFile
    fixed_reel_sets: tuple[LocalReelFile, ...]
    window_size: int


LOCAL_INPUT_DEFINITIONS = {
    GameMode.BASE: LocalOptimizationInputDefinition(
        source=LocalReelFile(filename="BR0.csv", weight=0.95),
        fixed_reel_sets=(
            LocalReelFile(
                filename="BRW0.csv",
                weight=0.05,
                substitutes=("W",),
            ),
        ),
        window_size=6,
    ),
    GameMode.FREE: LocalOptimizationInputDefinition(
        source=LocalReelFile(filename="FR6_0.csv", weight=0.95),
        fixed_reel_sets=(
            LocalReelFile(
                filename="FR6W_0.csv",
                weight=0.05,
                substitutes=("W",),
            ),
        ),
        window_size=6,
    ),
}


class LocalOptimizationInputLoader:
    def __init__(self, reel_directory: Path) -> None:
        self._reel_directory = reel_directory

    def load(self, mode: GameMode) -> OptimizationInput:
        definition = LOCAL_INPUT_DEFINITIONS[mode]

        return OptimizationInput(
            source=self._load_component(definition.source),
            fixed_reel_sets=tuple(
                self._load_component(component) for component in definition.fixed_reel_sets
            ),
            window_size=definition.window_size,
        )

    def _load_component(self, definition: LocalReelFile) -> ReelSetComponent:
        return ReelSetComponent(
            reels=self._load_reels(definition.filename),
            weight=definition.weight,
            substitutes=definition.substitutes,
        )

    def _load_reels(self, filename: str) -> ReelSet:
        csv_content = (self._reel_directory / filename).read_text(encoding="utf-8")
        return ReelCsvCodec.decode(csv_content)
