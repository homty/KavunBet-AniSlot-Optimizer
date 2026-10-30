from collections import Counter

import pytest

from kavunbet_optimizer.domain.reel_set import ReelSet, cyclic_max_run


def test_empty_reel_set_error() -> None:
    with pytest.raises(ValueError, match="a reel set must contain non-empty reels"):
        ReelSet([])


def test_reel_without_stops() -> None:
    with pytest.raises(ValueError, match="a reel set must contain non-empty reels"):
        ReelSet(
            [
                ["H1", "L1"],
                [],
            ]
        )


def test_constructor_copies_input_reels() -> None:
    source = [
        ["H1", "L1"],
        ["H2", "L2"],
    ]

    reel_set = ReelSet(source)
    source[0][0] = "CHANGED"

    assert reel_set.reels == [
        ["H1", "L1"],
        ["H2", "L2"],
    ]


def test_copy_creates_independent_reels() -> None:
    original = ReelSet(
        [
            ["H1", "L1"],
            ["H2", "L2"],
        ]
    )

    copied = original.copy()
    copied.reels[0][0] = "CHANGED"

    assert copied is not original
    assert copied.reels[0] is not original.reels[0]
    assert original.reels[0][0] == "H1"
    assert copied.reels[0][0] == "CHANGED"


def test_reel_count_returns_number_of_reels() -> None:
    reel_set = ReelSet(
        [
            ["H1"],
            ["H2"],
            ["H3"],
        ]
    )

    assert reel_set.reel_count == 3


def test_counts_counts_symbols_across_all_reels() -> None:
    reel_set = ReelSet(
        [
            ["H1", "L1", "H1"],
            ["L1", "H2", "H1"],
        ]
    )

    assert reel_set.counts() == Counter(
        {
            "H1": 3,
            "L1": 2,
            "H2": 1,
        }
    )


def test_cyclic_max_run_detects_ordinary_run() -> None:
    reel = ["H1", "L1", "L1", "L1", "H2"]

    result = cyclic_max_run(reel, "L1")

    assert result == 3


def test_cyclic_max_run_detects_wrapped_run() -> None:
    reel = ["L1", "L1", "H1", "H2", "L1"]

    result = cyclic_max_run(reel, "L1")

    assert result == 3


def test_cyclic_max_run_returns_full_length_for_single_symbol_reel() -> None:
    reel = ["L1", "L1", "L1", "L1"]

    result = cyclic_max_run(reel, "L1")

    assert result == 4


def test_cyclic_max_run_returns_zero_for_empty_reel() -> None:
    assert cyclic_max_run([], "L1") == 0


def test_cyclic_max_run_returns_zero_when_symbol_is_absent() -> None:
    reel = ["H1", "H2", "L1"]

    assert cyclic_max_run(reel, "W") == 0
