import json
import os
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import ValidationError

import kavunbet_optimizer
from kavunbet_optimizer.infrastructure.json_config_repository import (
    JsonOptimizationConfigRepository,
)
from kavunbet_optimizer.schemas import (
    GameMode,
    IntervalTarget,
    IntervalTargetPatch,
    OptimizationSettingsPatch,
)


@pytest.fixture
def config_directory(tmp_path: Path) -> Iterator[Path]:
    source_directory = Path(kavunbet_optimizer.__file__).resolve().parent / "configs"
    destination = tmp_path / "configs"
    destination.mkdir()

    for mode in GameMode:
        shutil.copy2(
            source_directory / f"{mode.value}_config.json",
            destination / f"{mode.value}_config.json",
        )

    yield destination


def read_document(config_directory: Path, mode: GameMode) -> dict[str, object]:
    path = config_directory / f"{mode.value}_config.json"
    with path.open(encoding="utf-8") as config_file:
        return json.load(config_file)


def test_patch_survives_repository_recreation(config_directory: Path) -> None:
    repository = JsonOptimizationConfigRepository(config_directory)
    repository.patch_optimization_settings(
        GameMode.BASE,
        OptimizationSettingsPatch(iterations=12_345),
    )

    reloaded = JsonOptimizationConfigRepository(config_directory)

    assert reloaded.get_optimization_settings(GameMode.BASE).iterations == 12_345


def test_add_survives_repository_recreation(config_directory: Path) -> None:
    target = IntervalTarget(
        symbol="H4",
        kind=4,
        min_interval=10,
        max_interval=20,
        weight=2,
    )
    repository = JsonOptimizationConfigRepository(config_directory)
    repository.add_target(GameMode.BASE, target)

    reloaded = JsonOptimizationConfigRepository(config_directory)

    assert target in reloaded.get_targets(GameMode.BASE)


def test_replace_survives_repository_recreation(config_directory: Path) -> None:
    replacement = IntervalTarget(
        symbol="H1",
        kind=3,
        min_interval=20,
        max_interval=40,
        weight=2,
    )
    repository = JsonOptimizationConfigRepository(config_directory)
    repository.replace_target(GameMode.BASE, "H1", 3, replacement)

    reloaded = JsonOptimizationConfigRepository(config_directory)

    assert replacement in reloaded.get_targets(GameMode.BASE)


def test_delete_survives_repository_recreation(config_directory: Path) -> None:
    repository = JsonOptimizationConfigRepository(config_directory)
    repository.delete_target(GameMode.BASE, "H1", 3)

    reloaded = JsonOptimizationConfigRepository(config_directory)

    assert all(
        target.symbol != "H1" or target.kind != 3 for target in reloaded.get_targets(GameMode.BASE)
    )


def test_unmanaged_json_fields_are_preserved(config_directory: Path) -> None:
    before = read_document(config_directory, GameMode.BASE)
    repository = JsonOptimizationConfigRepository(config_directory)
    repository.patch_target(
        GameMode.BASE,
        "H1",
        3,
        IntervalTargetPatch(weight=2),
    )
    after = read_document(config_directory, GameMode.BASE)

    for field in ("source", "output_directory", "source_weight", "fixed_reel_sets"):
        assert after[field] == before[field]


def test_base_change_does_not_modify_free_document(config_directory: Path) -> None:
    free_path = config_directory / "free_config.json"
    original_free_bytes = free_path.read_bytes()
    repository = JsonOptimizationConfigRepository(config_directory)
    repository.patch_optimization_settings(
        GameMode.BASE,
        OptimizationSettingsPatch(iterations=999),
    )

    assert free_path.read_bytes() == original_free_bytes


def test_invalid_aggregate_change_is_not_written(config_directory: Path) -> None:
    base_path = config_directory / "base_config.json"
    original_bytes = base_path.read_bytes()
    repository = JsonOptimizationConfigRepository(config_directory)

    with pytest.raises(ValidationError):
        repository.add_target(
            GameMode.BASE,
            IntervalTarget(
                symbol="UNKNOWN",
                kind=3,
                min_interval=1,
                max_interval=2,
            ),
        )

    assert base_path.read_bytes() == original_bytes
    assert (
        repository.get_config(GameMode.BASE).model_dump()
        == JsonOptimizationConfigRepository(config_directory).get_config(GameMode.BASE).model_dump()
    )


def test_failed_atomic_replace_rolls_back_memory_and_file(
    config_directory: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    base_path = config_directory / "base_config.json"
    original_bytes = base_path.read_bytes()
    repository = JsonOptimizationConfigRepository(config_directory)
    original_iterations = repository.get_optimization_settings(GameMode.BASE).iterations

    def fail_replace(_source: os.PathLike[str], _destination: os.PathLike[str]) -> None:
        raise OSError("simulated replace failure")

    monkeypatch.setattr(os, "replace", fail_replace)

    with pytest.raises(OSError, match="simulated replace failure"):
        repository.patch_optimization_settings(
            GameMode.BASE,
            OptimizationSettingsPatch(iterations=123),
        )

    assert base_path.read_bytes() == original_bytes
    assert repository.get_optimization_settings(GameMode.BASE).iterations == original_iterations
    assert list(config_directory.glob("*.tmp")) == []
