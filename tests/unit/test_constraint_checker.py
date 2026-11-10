import pytest

from kavunbet_optimizer.domain.optimization import ConstraintChecker
from kavunbet_optimizer.domain.reel_set import ReelSet
from kavunbet_optimizer.schemas.constraints import Constraints


def test_constraint_checker_accepts_valid_reels() -> None:
    checker = ConstraintChecker(
        Constraints(
            last_allowed_reel={"H1": 2},
            max_consecutive={"L1": 2},
            global_count_ranges={"H1": (1, 2)},
        ),
        reel_count=3,
    )
    candidate = ReelSet([["H1", "L1"], ["L1", "X"], ["L1", "X"]])

    assert checker.is_valid(candidate)


def test_constraint_checker_enforces_global_count_range() -> None:
    checker = ConstraintChecker(
        Constraints(global_count_ranges={"H1": (2, 3)}),
        reel_count=2,
    )

    assert not checker.is_valid(ReelSet([["H1"], ["X"]]))


def test_constraint_checker_enforces_last_allowed_reel() -> None:
    checker = ConstraintChecker(
        Constraints(last_allowed_reel={"H1": 1}),
        reel_count=2,
    )

    assert not checker.is_valid(ReelSet([["X"], ["H1"]]))


def test_constraint_checker_enforces_cyclic_maximum_run() -> None:
    checker = ConstraintChecker(
        Constraints(max_consecutive={"H1": 1}),
        reel_count=1,
    )

    assert not checker.is_valid(ReelSet([["H1", "X", "H1"]]))


def test_constraint_checker_rejects_last_reel_outside_reel_set() -> None:
    with pytest.raises(ValueError, match="exceeds the reel count"):
        ConstraintChecker(
            Constraints(last_allowed_reel={"H1": 3}),
            reel_count=2,
        )
