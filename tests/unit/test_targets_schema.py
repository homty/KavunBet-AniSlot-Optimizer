import pytest
from pydantic import ValidationError

from kavunbet_optimizer.schemas.targets import IntervalTarget, IntervalTargetPatch




def test_valid_interval() -> None:
    target = IntervalTarget(
        symbol="H1",
        kind=3,
        min_interval=25,
        max_interval=35,
        weight=4.0,
    )
    assert target.min_interval == 25
    assert target.max_interval == 35

def test_valid_interval_target_patch() -> None:
    patch = IntervalTargetPatch(
        min_interval=20,
        max_interval=35,
    )

    assert patch.max_interval == 35
    assert patch.min_interval == 20

@pytest.mark.parametrize(
    "payload",
    [
        {"min_interval": 50},
        {"max_interval": 0}
    ],
)
def test_invalid_interval_target_patch(payload: dict[str, object]) -> None:
   with pytest.raises(ValidationError):
       IntervalTargetPatch(**payload)

def test_invalid_expected_ways_range_is_rejected() -> None:
    with pytest.raises(ValidationError):
        IntervalTarget(
            symbol="H3",
            kind=3,
            min_interval=50,
            max_interval=5,
        )

