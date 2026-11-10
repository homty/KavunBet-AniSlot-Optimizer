from pathlib import Path

import pytest

from kavunbet_optimizer.infrastructure.local_optimization_input_loader import (
    LocalOptimizationInputLoader,
)
from kavunbet_optimizer.schemas.optimization import GameMode

CSV_CONTENT = "A1,B1\nA2,B2\nA3,B3\nA4,B4\nA5,B5\nA6,B6\n"


def write_mode_files(reel_directory: Path, filenames: tuple[str, str]) -> None:
    for filename in filenames:
        (reel_directory / filename).write_text(CSV_CONTENT, encoding="utf-8")


@pytest.mark.parametrize(
    ("mode", "filenames"),
    [
        (GameMode.BASE, ("BR0.csv", "BRW0.csv")),
        (GameMode.FREE, ("FR6_0.csv", "FR6W_0.csv")),
    ],
)
def test_load_reads_mode_specific_reel_files(
    tmp_path: Path,
    mode: GameMode,
    filenames: tuple[str, str],
) -> None:
    write_mode_files(tmp_path, filenames)
    loader = LocalOptimizationInputLoader(tmp_path)

    optimization_input = loader.load(mode)

    assert optimization_input.source.reels.reels == [
        ["A1", "A2", "A3", "A4", "A5", "A6"],
        ["B1", "B2", "B3", "B4", "B5", "B6"],
    ]
    assert optimization_input.source.weight == 0.95
    assert optimization_input.source.substitutes == ()
    assert len(optimization_input.fixed_reel_sets) == 1
    assert optimization_input.fixed_reel_sets[0].weight == 0.05
    assert optimization_input.fixed_reel_sets[0].substitutes == ("W",)
    assert optimization_input.window_size == 6


def test_load_rejects_missing_reel_file(tmp_path: Path) -> None:
    loader = LocalOptimizationInputLoader(tmp_path)

    with pytest.raises(FileNotFoundError):
        loader.load(GameMode.BASE)
