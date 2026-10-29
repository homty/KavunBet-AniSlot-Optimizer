import pytest
from pydantic import ValidationError

from kavunbet_optimizer.schemas import Constraints, ConstraintsPatch


def test_valid_constraints() -> None:
    constraints = Constraints(
        last_allowed_reel={"H4": 3},
        max_consecutive={"H1": 2},
        global_count_ranges={"L1": [1, 10]},
        composition_symbols=["L1", "L2"],
    )

    assert constraints.last_allowed_reel == {"H4": 3}
    assert constraints.max_consecutive == {"H1": 2}
    assert constraints.global_count_ranges == {"L1": (1, 10)}
    assert constraints.composition_symbols == ["L1", "L2"]


def test_constraints_use_empty_defaults() -> None:
    constraints = Constraints()

    assert constraints.last_allowed_reel == {}
    assert constraints.max_consecutive == {}
    assert constraints.global_count_ranges == {}
    assert constraints.composition_symbols == []


@pytest.mark.parametrize(
    "payload",
    [
        {"last_allowed_reel": {"H4": 0}},
        {"max_consecutive": {"H1": 0}},
        {"global_count_ranges": {"L1": [-1, 10]}},
        {"global_count_ranges": {"L1": [10, 1]}},
        {"unknown": 1},
    ],
)
def test_invalid_constraints_patch_is_rejected(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        ConstraintsPatch(**payload)
