import pytest
from pydantic import ValidationError

from kavunbet_optimizer.infrastructure.default_configs import create_default_configs
from kavunbet_optimizer.schemas import GameMode, IntervalTarget, OptimizationConfig


def test_default_complete_configs_are_valid() -> None:
    configs = create_default_configs()

    assert configs[GameMode.BASE].symbols
    assert configs[GameMode.FREE].symbols


def test_unknown_referenced_symbol_is_rejected() -> None:
    config_data = create_default_configs()[GameMode.BASE].model_dump()
    config_data["targets"].append(
        IntervalTarget(
            symbol="UNKNOWN",
            kind=3,
            min_interval=1,
            max_interval=2,
        ).model_dump()
    )

    with pytest.raises(ValidationError):
        OptimizationConfig.model_validate(config_data)


def test_duplicate_target_identity_is_rejected() -> None:
    config_data = create_default_configs()[GameMode.BASE].model_dump()
    config_data["targets"].append(config_data["targets"][0].copy())

    with pytest.raises(ValidationError):
        OptimizationConfig.model_validate(config_data)
