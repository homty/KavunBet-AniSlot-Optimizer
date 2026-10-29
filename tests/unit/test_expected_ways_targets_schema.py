import pytest
from pydantic import ValidationError

from kavunbet_optimizer.schemas import ExpectedWaysTarget, ExpectedWaysTargetPatch


def test_valid_expected_ways_target_settings() -> None:
    target = ExpectedWaysTarget(
        symbol="H3",
        kind=3,
        min_ways=5,
        max_ways=40,
        weight=4.0,
    )

    assert target.symbol == "H3"
    assert target.kind == 3
    assert target.min_ways == 5
    assert target.max_ways == 40
    assert target.weight == 4.0

def test_valid_expected_ways_target_patch() -> None:
    patch = ExpectedWaysTargetPatch(
        min_ways=10,
        weight=2.0,
    )

    assert patch.min_ways == 10
    assert patch.weight == 2.0
    assert patch.max_ways is None

@pytest.mark.parametrize(
    "payload",
    [
        {"min_ways": 0},
        {"min_ways": -1},
        {"max_ways": 0},
        {"max_ways": -1},
        {"weight": 0},
        {"weight": -1},
        {"unknown": 1},
    ],
)
def test_invalid_expected_ways_target_patch_is_rejected(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        ExpectedWaysTargetPatch(**payload)


def test_invalid_expected_ways_range_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ExpectedWaysTarget(
            symbol="H3",
            kind=3,
            min_ways=40,
            max_ways=5,
        )
