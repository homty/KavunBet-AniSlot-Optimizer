import pytest
from pydantic import ValidationError

from kavunbet_optimizer.schemas import ObjectiveSettings, ObjectiveSettingsPatch


def test_valid_objective_settings() -> None:
    objective = ObjectiveSettings(
        progression_weight=1.0,
        symbol_order_weight=1.0,
        preserve_untargeted_weight=0.25,
        preserve_untargeted_tolerance=0.2,
        preserve_untargeted_ways_weight=4.0,
        preserve_untargeted_ways_tolerance=0.1,
        frequency_orders=[["H1", "H2", "H3"]],
    )

    assert objective.frequency_orders == [["H1", "H2", "H3"]]


@pytest.mark.parametrize(
    "payload",
    [
        {"progression_weight": -1},
        {"preserve_untargeted_tolerance": 1},
        {"preserve_untargeted_ways_tolerance": 1},
        {"frequency_orders": [["H1"]]},
        {"frequency_orders": [["H1", "H1"]]},
        {"unknown": 1},
    ],
)
def test_invalid_objective_patch_schema_is_rejected(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        ObjectiveSettingsPatch(**payload)
