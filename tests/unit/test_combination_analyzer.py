import math

import pytest

from kavunbet_optimizer.domain.combination_analyzer import (
    CombinationAnalyzer,
    CombinationMetric,
)
from kavunbet_optimizer.domain.optimization_input import (
    OptimizationInput,
    ReelSetComponent,
)
from kavunbet_optimizer.domain.reel_set import ReelSet
from kavunbet_optimizer.infrastructure.default_configs import create_default_configs
from kavunbet_optimizer.schemas.optimization import GameMode


def make_reel_set(
    *,
    reel_count: int = 6,
    reel_length: int = 4,
) -> ReelSet:
    return ReelSet(
        [
            [f"S{reel_index}-{stop}" for stop in range(reel_length)]
            for reel_index in range(reel_count)
        ]
    )


def make_input(
    *,
    window_size: int = 2,
    reel_count: int = 6,
    reel_length: int = 4,
) -> OptimizationInput:
    return OptimizationInput(
        source=ReelSetComponent(
            reels=make_reel_set(
                reel_count=reel_count,
                reel_length=reel_length,
            ),
            weight=1.0,
        ),
        fixed_reel_sets=(),
        window_size=window_size,
    )


def make_analyzer(
    *,
    window_size: int = 2,
    reel_count: int = 6,
    reel_length: int = 4,
) -> CombinationAnalyzer:
    return CombinationAnalyzer(
        config=create_default_configs()[GameMode.BASE],
        optimization_input=make_input(
            window_size=window_size,
            reel_count=reel_count,
            reel_length=reel_length,
        ),
    )


def test_combination_metric_returns_probability_interval() -> None:
    metric = CombinationMetric(symbol="A", kind=3, probability=0.25)

    assert metric.interval == 4.0


def test_combination_metric_returns_infinite_interval_for_zero_probability() -> None:
    metric = CombinationMetric(symbol="A", kind=3, probability=0.0)

    assert math.isinf(metric.interval)


def test_reel_multiplicity_counts_each_cyclic_window() -> None:
    analyzer = make_analyzer(window_size=2)

    multiplicities = analyzer.reel_multiplicity(
        ["A", "A", "B", "C"],
        "A",
    )

    assert multiplicities == (2, 1, 0, 1)


def test_reel_multiplicity_counts_substitutes() -> None:
    analyzer = make_analyzer(window_size=2)

    multiplicities = analyzer.reel_multiplicity(
        ["W", "A", "B", "C"],
        "A",
        substitutes=("W",),
    )

    assert multiplicities == (2, 1, 0, 1)


def test_reel_presence_measures_covered_cyclic_stops() -> None:
    analyzer = make_analyzer(window_size=2)

    presence = analyzer.reel_presence(
        ["A", "A", "B", "C"],
        "A",
    )

    assert presence == 0.75


def test_group_rtp_targets_require_paytable() -> None:
    with pytest.raises(ValueError, match="paytable"):
        CombinationAnalyzer(
            config=create_default_configs()[GameMode.FREE],
            optimization_input=make_input(),
        )


def test_validate_shape_requires_six_reels() -> None:
    analyzer = make_analyzer()

    with pytest.raises(ValueError, match="at least six reels"):
        analyzer.validate_shape(make_reel_set(reel_count=5))


def test_validate_shape_requires_matching_reel_count() -> None:
    analyzer = make_analyzer(reel_count=7)

    with pytest.raises(ValueError, match="same reel count"):
        analyzer.validate_shape(make_reel_set(reel_count=6))


def test_validate_shape_requires_window_to_fit_candidate() -> None:
    analyzer = make_analyzer(window_size=4, reel_length=4)

    with pytest.raises(ValueError, match="window size exceeds"):
        analyzer.validate_shape(make_reel_set(reel_length=3))
