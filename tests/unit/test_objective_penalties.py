import math

import pytest

from kavunbet_optimizer.domain.analysis import CombinationMetric
from kavunbet_optimizer.domain.scoring.objective_penalties import (
    expected_ways_preservation_penalty,
    interval_preservation_penalty,
    progression_penalty,
    symbol_order_penalty,
)


def make_probability_matrix(
    symbol: str,
    probabilities: tuple[float, float, float, float],
) -> dict[str, dict[int, CombinationMetric]]:
    return {
        symbol: {
            kind: CombinationMetric(
                symbol=symbol,
                kind=kind,
                probability=probability,
            )
            for kind, probability in zip(
                (3, 4, 5, 6),
                probabilities,
                strict=True,
            )
        }
    }


def test_progression_penalty_is_zero_for_decreasing_probabilities() -> None:
    matrix = make_probability_matrix("H1", (0.40, 0.30, 0.20, 0.10))

    result = progression_penalty(matrix, ["H1"])

    assert result == 0.0


def test_progression_penalty_measures_increasing_probability() -> None:
    matrix = make_probability_matrix("H1", (0.40, 0.80, 0.20, 0.10))

    result = progression_penalty(matrix, ["H1"])

    assert result == pytest.approx(math.log(2.0) ** 2)


def test_progression_penalty_uses_fixed_penalty_after_zero_probability() -> None:
    matrix = make_probability_matrix("H1", (0.0, 0.20, 0.10, 0.05))

    result = progression_penalty(matrix, ["H1"])

    assert result == 100.0


def test_symbol_order_penalty_is_zero_for_correct_frequency_order() -> None:
    matrix = {
        **make_probability_matrix("H1", (0.40, 0.30, 0.20, 0.10)),
        **make_probability_matrix("H2", (0.20, 0.15, 0.10, 0.05)),
    }

    result = symbol_order_penalty(matrix, [["H1", "H2"]])

    assert result == 0.0


def test_symbol_order_penalty_measures_reversed_order_for_every_kind() -> None:
    matrix = {
        **make_probability_matrix("H1", (0.20, 0.20, 0.20, 0.20)),
        **make_probability_matrix("H2", (0.40, 0.40, 0.40, 0.40)),
    }

    result = symbol_order_penalty(matrix, [["H1", "H2"]])

    assert result == pytest.approx(4 * math.log(2.0) ** 2)


def test_symbol_order_penalty_uses_fixed_penalty_after_zero_probability() -> None:
    matrix = {
        **make_probability_matrix("H1", (0.0, 0.0, 0.0, 0.0)),
        **make_probability_matrix("H2", (0.10, 0.10, 0.10, 0.10)),
    }

    result = symbol_order_penalty(matrix, [["H1", "H2"]])

    assert result == 400.0


def baseline_intervals(
    symbol: str,
    interval: float,
) -> dict[tuple[str, int], float]:
    return {(symbol, kind): interval for kind in (3, 4, 5, 6)}


def test_interval_preservation_penalty_is_zero_for_unchanged_intervals() -> None:
    matrix = make_probability_matrix("H1", (0.10, 0.10, 0.10, 0.10))

    result = interval_preservation_penalty(
        candidate_matrix=matrix,
        baseline_intervals=baseline_intervals("H1", 10.0),
        targeted_cells=set(),
        tolerance=0.20,
    )

    assert result == 0.0


def test_interval_preservation_penalty_is_zero_inside_tolerance() -> None:
    matrix = make_probability_matrix("H1", (1 / 12, 0.10, 0.10, 0.10))

    result = interval_preservation_penalty(
        candidate_matrix=matrix,
        baseline_intervals=baseline_intervals("H1", 10.0),
        targeted_cells=set(),
        tolerance=0.20,
    )

    assert result == 0.0


def test_interval_preservation_penalty_measures_change_outside_tolerance() -> None:
    matrix = make_probability_matrix("H1", (0.05, 0.10, 0.10, 0.10))

    result = interval_preservation_penalty(
        candidate_matrix=matrix,
        baseline_intervals=baseline_intervals("H1", 10.0),
        targeted_cells=set(),
        tolerance=0.20,
    )
    expected_excess = math.log(2.0) - (-math.log(0.80))

    assert result == pytest.approx(expected_excess**2)


def test_interval_preservation_penalty_ignores_targeted_cell() -> None:
    matrix = make_probability_matrix("H1", (0.05, 0.10, 0.10, 0.10))

    result = interval_preservation_penalty(
        candidate_matrix=matrix,
        baseline_intervals=baseline_intervals("H1", 10.0),
        targeted_cells={("H1", 3)},
        tolerance=0.20,
    )

    assert result == 0.0


def test_interval_preservation_penalty_accepts_unchanged_infinite_intervals() -> None:
    matrix = make_probability_matrix("H1", (0.0, 0.0, 0.0, 0.0))

    result = interval_preservation_penalty(
        candidate_matrix=matrix,
        baseline_intervals=baseline_intervals("H1", math.inf),
        targeted_cells=set(),
        tolerance=0.20,
    )

    assert result == 0.0


def test_interval_preservation_penalty_handles_finite_to_infinite_change() -> None:
    matrix = make_probability_matrix("H1", (0.0, 0.10, 0.10, 0.10))

    result = interval_preservation_penalty(
        candidate_matrix=matrix,
        baseline_intervals=baseline_intervals("H1", 10.0),
        targeted_cells=set(),
        tolerance=0.20,
    )

    assert result == 100.0


@pytest.mark.parametrize("tolerance", [-0.01, 1.0, 1.01])
def test_interval_preservation_penalty_rejects_invalid_tolerance(
    tolerance: float,
) -> None:
    matrix = make_probability_matrix("H1", (0.10, 0.10, 0.10, 0.10))

    with pytest.raises(ValueError, match="tolerance must be between"):
        interval_preservation_penalty(
            candidate_matrix=matrix,
            baseline_intervals=baseline_intervals("H1", 10.0),
            targeted_cells=set(),
            tolerance=tolerance,
        )


def test_expected_ways_preservation_penalty_is_zero_for_unchanged_values() -> None:
    candidate = {"H1": {3: 0.50, 4: 0.25}}
    baseline = {("H1", 3): 0.50, ("H1", 4): 0.25}

    result = expected_ways_preservation_penalty(
        candidate,
        baseline,
        targeted_cells=set(),
        tolerance=0.10,
    )

    assert result == 0.0


def test_expected_ways_preservation_penalty_measures_excess_change() -> None:
    candidate = {"H1": {3: 1.00}}
    baseline = {("H1", 3): 0.50}

    result = expected_ways_preservation_penalty(
        candidate,
        baseline,
        targeted_cells=set(),
        tolerance=0.10,
    )
    expected_excess = math.log(2.0) - (-math.log(0.90))

    assert result == pytest.approx(expected_excess**2)


def test_expected_ways_preservation_penalty_ignores_targeted_cell() -> None:
    result = expected_ways_preservation_penalty(
        {"H1": {3: 1.00}},
        {("H1", 3): 0.50},
        targeted_cells={("H1", 3)},
        tolerance=0.10,
    )

    assert result == 0.0


def test_expected_ways_preservation_penalty_handles_zero_to_positive() -> None:
    result = expected_ways_preservation_penalty(
        {"H1": {3: 0.50}},
        {("H1", 3): 0.0},
        targeted_cells=set(),
        tolerance=0.10,
    )

    assert result == 100.0
