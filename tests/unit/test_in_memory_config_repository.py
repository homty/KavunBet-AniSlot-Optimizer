import pytest
from pydantic import ValidationError

from kavunbet_optimizer.domain.exceptions import ConfigVersionConflictError
from kavunbet_optimizer.infrastructure.in_memory_config_repository import (
    InMemoryOptimizationConfigRepository,
)
from kavunbet_optimizer.schemas.optimization import GameMode, OptimizationSettingsPatch


def test_get_returns_versioned_defensive_copy() -> None:
    repository = InMemoryOptimizationConfigRepository()

    first = repository.get(GameMode.BASE)
    original_target_count = len(first.config.targets)
    first.config.targets.clear()

    second = repository.get(GameMode.BASE)

    assert first.version == "1"
    assert second.version == "1"
    assert len(second.config.targets) == original_target_count


def test_save_persists_config_and_increments_version() -> None:
    repository = InMemoryOptimizationConfigRepository()
    stored = repository.get(GameMode.BASE)
    stored.config.optimization.iterations += 1

    saved = repository.save(
        GameMode.BASE,
        stored.config,
        expected_version=stored.version,
    )

    assert saved.version == "2"
    assert repository.get(GameMode.BASE) == saved


def test_save_rejects_stale_version_without_changing_config() -> None:
    repository = InMemoryOptimizationConfigRepository()
    first = repository.get(GameMode.BASE)
    second = repository.get(GameMode.BASE)
    first.config.optimization.iterations += 1
    repository.save(GameMode.BASE, first.config, expected_version=first.version)
    saved = repository.get(GameMode.BASE)
    second.config.optimization.iterations += 2

    with pytest.raises(ConfigVersionConflictError):
        repository.save(GameMode.BASE, second.config, expected_version=second.version)

    assert repository.get(GameMode.BASE) == saved


def test_save_rolls_back_invalid_config_and_version() -> None:
    repository = InMemoryOptimizationConfigRepository()
    stored = repository.get(GameMode.BASE)
    stored.config.optimization.iterations = 0

    with pytest.raises(ValidationError):
        repository.save(
            GameMode.BASE,
            stored.config,
            expected_version=stored.version,
        )

    current = repository.get(GameMode.BASE)
    assert current.version == stored.version
    assert current.config.optimization.iterations > 0


def test_legacy_mutation_increments_version() -> None:
    repository = InMemoryOptimizationConfigRepository()

    repository.patch_optimization_settings(
        GameMode.BASE,
        OptimizationSettingsPatch(iterations=1),
    )

    assert repository.get(GameMode.BASE).version == "2"
