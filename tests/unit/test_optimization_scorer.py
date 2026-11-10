import math

import pytest

from kavunbet_optimizer.domain.analysis import CombinationMetric
from kavunbet_optimizer.domain.optimization_input import (
    OptimizationInput,
    ReelSetComponent,
)
from kavunbet_optimizer.domain.reel_set import ReelSet
from kavunbet_optimizer.domain.scoring import OptimizationScorer
from kavunbet_optimizer.infrastructure.default_configs import create_default_configs
from kavunbet_optimizer.schemas.expected_ways_targets import ExpectedWaysTarget
from kavunbet_optimizer.schemas.group_rtp_targets import GroupRtpTarget
from kavunbet_optimizer.schemas.optimization import GameMode
from kavunbet_optimizer.schemas.targets import IntervalTarget


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
) -> OptimizationScorer:
    return OptimizationScorer(
        config=create_default_configs()[GameMode.BASE],
        optimization_input=make_input(
            window_size=window_size,
            reel_count=reel_count,
            reel_length=reel_length,
        ),
    )


def repeated_reels(stops: list[str]) -> ReelSet:
    return ReelSet([stops.copy() for _ in range(6)])


def make_probability_analyzer(
    source_reels: ReelSet,
    *,
    source_weight: float = 1.0,
    source_substitutes: tuple[str, ...] = (),
    fixed_reel_sets: tuple[ReelSetComponent, ...] = (),
) -> OptimizationScorer:
    return OptimizationScorer(
        config=create_default_configs()[GameMode.BASE],
        optimization_input=OptimizationInput(
            source=ReelSetComponent(
                reels=source_reels,
                weight=source_weight,
                substitutes=source_substitutes,
            ),
            fixed_reel_sets=fixed_reel_sets,
            window_size=1,
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
        OptimizationScorer(
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


def test_matrix_calculates_source_only_exact_probabilities() -> None:
    candidate = repeated_reels(["H1", "X"])
    analyzer = make_probability_analyzer(candidate)

    matrix = analyzer.matrix(candidate)

    assert matrix["H1"][3].probability == pytest.approx(0.0625)
    assert matrix["H1"][4].probability == pytest.approx(0.03125)
    assert matrix["H1"][5].probability == pytest.approx(0.015625)
    assert matrix["H1"][6].probability == pytest.approx(0.015625)


def test_matrix_combines_weighted_source_and_fixed_components() -> None:
    candidate = repeated_reels(["H1", "X"])
    fixed = ReelSetComponent(
        reels=repeated_reels(["H1"]),
        weight=0.2,
    )
    analyzer = make_probability_analyzer(
        candidate,
        source_weight=0.8,
        fixed_reel_sets=(fixed,),
    )

    matrix = analyzer.matrix(candidate)

    assert matrix["H1"][3].probability == pytest.approx(0.05)
    assert matrix["H1"][6].probability == pytest.approx(0.2125)


def test_matrix_applies_fixed_component_substitutes() -> None:
    candidate = repeated_reels(["X", "Y"])
    fixed = ReelSetComponent(
        reels=repeated_reels(["W", "X"]),
        weight=0.5,
        substitutes=("W",),
    )
    analyzer = make_probability_analyzer(
        candidate,
        source_weight=0.5,
        fixed_reel_sets=(fixed,),
    )

    metric = analyzer.metric(candidate, "H1", 3)

    assert metric.probability == pytest.approx(0.03125)


def test_matrix_applies_source_substitutes() -> None:
    candidate = repeated_reels(["W", "X"])
    analyzer = make_probability_analyzer(
        candidate,
        source_substitutes=("W",),
    )

    metric = analyzer.metric(candidate, "H1", 3)

    assert metric.probability == pytest.approx(0.0625)


def test_metric_matches_matrix_cell() -> None:
    candidate = repeated_reels(["H1", "X"])
    analyzer = make_probability_analyzer(candidate)

    metric = analyzer.metric(candidate, "H1", 4)
    matrix = analyzer.matrix(candidate)

    assert metric == matrix["H1"][4]


def test_matrix_contains_every_configured_symbol_and_exact_kind() -> None:
    candidate = repeated_reels(["H1", "X"])
    analyzer = make_probability_analyzer(candidate)

    matrix = analyzer.matrix(candidate)

    assert set(matrix) == set(analyzer.config.symbols)
    assert all(set(symbol_metrics) == {3, 4, 5, 6} for symbol_metrics in matrix.values())


def test_band_error_is_zero_inside_target_range() -> None:
    error = OptimizationScorer._band_error(
        value=30.0,
        minimum=25.0,
        maximum=35.0,
    )

    assert error == 0.0


def test_band_error_measures_value_below_target_range() -> None:
    error = OptimizationScorer._band_error(
        value=20.0,
        minimum=25.0,
        maximum=35.0,
    )

    assert error == pytest.approx(math.log(25.0 / 20.0))


def test_band_error_measures_value_above_target_range() -> None:
    error = OptimizationScorer._band_error(
        value=50.0,
        minimum=25.0,
        maximum=35.0,
    )

    assert error == pytest.approx(math.log(50.0 / 35.0))


def test_evaluate_returns_weighted_target_penalty() -> None:
    candidate = repeated_reels(["H1", "X"])
    analyzer = make_probability_analyzer(candidate)

    evaluations = analyzer.evaluate(candidate)
    evaluation = next(
        item for item in evaluations if item.target.symbol == "H1" and item.target.kind == 3
    )
    expected_error = math.log(25.0 / 16.0)

    assert evaluation.metric.interval == pytest.approx(16.0)
    assert evaluation.error == pytest.approx(expected_error)
    assert evaluation.penalty == pytest.approx(4.0 * expected_error * expected_error)
    assert not evaluation.passes


def test_evaluate_marks_target_inside_band_as_passing() -> None:
    candidate = repeated_reels(["H1", "H1", "X", "X", "X"])
    analyzer = make_probability_analyzer(candidate)

    evaluations = analyzer.evaluate(candidate)
    evaluation = next(
        item for item in evaluations if item.target.symbol == "H1" and item.target.kind == 3
    )

    assert 25.0 <= evaluation.metric.interval <= 35.0
    assert evaluation.error == 0.0
    assert evaluation.penalty == 0.0
    assert evaluation.passes


def test_expected_exact_ways_uses_visible_symbol_multiplicity() -> None:
    candidate = repeated_reels(["H1", "H1", "X", "X"])
    analyzer = OptimizationScorer(
        config=create_default_configs()[GameMode.BASE],
        optimization_input=OptimizationInput(
            source=ReelSetComponent(reels=candidate, weight=1.0),
            fixed_reel_sets=(),
            window_size=2,
        ),
    )

    expected_ways = analyzer.expected_exact_ways(candidate, "H1", 3)
    hit_probability = analyzer.metric(candidate, "H1", 3).probability

    assert expected_ways == pytest.approx(0.25)
    assert hit_probability == pytest.approx(0.75**3 * 0.25)
    assert expected_ways != pytest.approx(hit_probability)


def test_expected_exact_ways_combines_source_and_fixed_components() -> None:
    candidate = repeated_reels(["H1", "X"])
    fixed = ReelSetComponent(
        reels=repeated_reels(["H1"]),
        weight=0.2,
    )
    analyzer = make_probability_analyzer(
        candidate,
        source_weight=0.8,
        fixed_reel_sets=(fixed,),
    )

    expected_ways = analyzer.expected_exact_ways(candidate, "H1", 6)

    assert expected_ways == pytest.approx(0.8 * 0.5**6 + 0.2)


def test_evaluate_expected_ways_returns_weighted_penalty() -> None:
    candidate = repeated_reels(["H1", "X"])
    config = create_default_configs()[GameMode.BASE].model_copy(
        update={
            "expected_ways_targets": [
                ExpectedWaysTarget(
                    symbol="H1",
                    kind=3,
                    min_ways=0.1,
                    max_ways=0.2,
                    weight=3.0,
                )
            ]
        }
    )
    analyzer = OptimizationScorer(
        config=config,
        optimization_input=OptimizationInput(
            source=ReelSetComponent(reels=candidate, weight=1.0),
            fixed_reel_sets=(),
            window_size=1,
        ),
    )

    evaluation = analyzer.evaluate_expected_ways(candidate)[0]
    expected_error = math.log(0.1 / 0.0625)

    assert evaluation.expected_ways == pytest.approx(0.0625)
    assert evaluation.error == pytest.approx(expected_error)
    assert evaluation.penalty == pytest.approx(3.0 * expected_error * expected_error)
    assert not evaluation.passes


def test_evaluate_expected_ways_marks_value_inside_band_as_passing() -> None:
    candidate = repeated_reels(["H1", "X"])
    config = create_default_configs()[GameMode.BASE].model_copy(
        update={
            "expected_ways_targets": [
                ExpectedWaysTarget(
                    symbol="H1",
                    kind=3,
                    min_ways=0.05,
                    max_ways=0.07,
                )
            ]
        }
    )
    analyzer = OptimizationScorer(
        config=config,
        optimization_input=OptimizationInput(
            source=ReelSetComponent(reels=candidate, weight=1.0),
            fixed_reel_sets=(),
            window_size=1,
        ),
    )

    evaluation = analyzer.evaluate_expected_ways(candidate)[0]

    assert evaluation.error == 0.0
    assert evaluation.penalty == 0.0
    assert evaluation.passes


@pytest.mark.parametrize(
    ("symbol", "kind", "message"),
    [
        ("UNKNOWN", 3, "unknown symbol"),
        ("H1", 2, "kind must be one of"),
    ],
)
def test_expected_exact_ways_rejects_invalid_cell(
    symbol: str,
    kind: int,
    message: str,
) -> None:
    candidate = repeated_reels(["H1", "X"])
    analyzer = make_probability_analyzer(candidate)

    with pytest.raises(ValueError, match=message):
        analyzer.expected_exact_ways(candidate, symbol, kind)


def make_group_rtp_analyzer(
    candidate: ReelSet,
    target: GroupRtpTarget,
    paytable: dict[tuple[int, str], float],
) -> OptimizationScorer:
    config = create_default_configs()[GameMode.BASE].model_copy(
        update={"group_rtp_targets": [target]}
    )
    return OptimizationScorer(
        config=config,
        optimization_input=OptimizationInput(
            source=ReelSetComponent(reels=candidate, weight=1.0),
            fixed_reel_sets=(),
            window_size=1,
        ),
        paytable=paytable,
    )


def test_evaluate_group_rtp_calculates_natural_rtp_percentage() -> None:
    candidate = repeated_reels(["H1", "X"])
    target = GroupRtpTarget(
        name="premium",
        symbols=["H1"],
        min_natural_rtp_pct=24.0,
        max_natural_rtp_pct=26.0,
    )
    paytable = {(kind, "H1"): 2.0 for kind in (3, 4, 5, 6)}
    analyzer = make_group_rtp_analyzer(candidate, target, paytable)

    evaluation = analyzer.evaluate_group_rtp(candidate)[0]

    assert evaluation.natural_rtp_pct == pytest.approx(25.0)
    assert evaluation.error == 0.0
    assert evaluation.penalty == 0.0
    assert evaluation.passes


def test_evaluate_group_rtp_returns_weighted_penalty() -> None:
    candidate = repeated_reels(["H1", "X"])
    target = GroupRtpTarget(
        name="premium",
        symbols=["H1"],
        min_natural_rtp_pct=30.0,
        max_natural_rtp_pct=40.0,
        weight=2.0,
    )
    paytable = {(kind, "H1"): 2.0 for kind in (3, 4, 5, 6)}
    analyzer = make_group_rtp_analyzer(candidate, target, paytable)

    evaluation = analyzer.evaluate_group_rtp(candidate)[0]
    expected_error = math.log(30.0 / 25.0)

    assert evaluation.natural_rtp_pct == pytest.approx(25.0)
    assert evaluation.error == pytest.approx(expected_error)
    assert evaluation.penalty == pytest.approx(2.0 * expected_error * expected_error)
    assert not evaluation.passes


def test_evaluate_group_rtp_requires_every_paytable_cell() -> None:
    candidate = repeated_reels(["H1", "X"])
    target = GroupRtpTarget(
        name="premium",
        symbols=["H1"],
        min_natural_rtp_pct=24.0,
        max_natural_rtp_pct=26.0,
    )
    analyzer = make_group_rtp_analyzer(candidate, target, {(3, "H1"): 2.0})

    with pytest.raises(ValueError, match="missing paytable entry for H1 E4"):
        analyzer.evaluate_group_rtp(candidate)


def test_evaluate_group_rtp_rejects_negative_payout() -> None:
    candidate = repeated_reels(["H1", "X"])
    target = GroupRtpTarget(
        name="premium",
        symbols=["H1"],
        min_natural_rtp_pct=24.0,
        max_natural_rtp_pct=26.0,
    )
    paytable = {(kind, "H1"): 2.0 for kind in (3, 4, 5, 6)}
    paytable[(5, "H1")] = -1.0
    analyzer = make_group_rtp_analyzer(candidate, target, paytable)

    with pytest.raises(ValueError, match="cannot be negative for H1 E5"):
        analyzer.evaluate_group_rtp(candidate)


def make_penalty_analyzer(
    candidate: ReelSet,
    *,
    interval_target: IntervalTarget,
    expected_ways_target: ExpectedWaysTarget,
    group_rtp_target: GroupRtpTarget,
) -> OptimizationScorer:
    config = create_default_configs()[GameMode.BASE].model_copy(
        update={
            "targets": [interval_target],
            "expected_ways_targets": [expected_ways_target],
            "group_rtp_targets": [group_rtp_target],
        }
    )
    return OptimizationScorer(
        config=config,
        optimization_input=OptimizationInput(
            source=ReelSetComponent(reels=candidate, weight=1.0),
            fixed_reel_sets=(),
            window_size=1,
        ),
        paytable={(kind, "H1"): 2.0 for kind in (3, 4, 5, 6)},
    )


def test_penalty_components_combines_all_target_penalties() -> None:
    candidate = repeated_reels(["H1", "X"])
    analyzer = make_penalty_analyzer(
        candidate,
        interval_target=IntervalTarget(
            symbol="H1",
            kind=3,
            min_interval=20.0,
            max_interval=30.0,
            weight=4.0,
        ),
        expected_ways_target=ExpectedWaysTarget(
            symbol="H1",
            kind=3,
            min_ways=0.1,
            max_ways=0.2,
            weight=3.0,
        ),
        group_rtp_target=GroupRtpTarget(
            name="premium",
            symbols=["H1"],
            min_natural_rtp_pct=30.0,
            max_natural_rtp_pct=40.0,
            weight=2.0,
        ),
    )

    components = analyzer.penalty_components(candidate)
    target_penalty = sum(item.penalty for item in analyzer.evaluate(candidate))
    expected_ways_penalty = sum(item.penalty for item in analyzer.evaluate_expected_ways(candidate))
    group_rtp_penalty = sum(item.penalty for item in analyzer.evaluate_group_rtp(candidate))

    assert components["targets"] == pytest.approx(target_penalty)
    assert components["expected_ways"] == pytest.approx(expected_ways_penalty)
    assert components["group_rtp"] == pytest.approx(group_rtp_penalty)
    assert components["total"] == pytest.approx(
        target_penalty + expected_ways_penalty + group_rtp_penalty
    )
    assert analyzer.penalty(candidate) == pytest.approx(components["total"])


def test_penalty_is_zero_when_every_target_passes() -> None:
    candidate = repeated_reels(["H1", "X"])
    analyzer = make_penalty_analyzer(
        candidate,
        interval_target=IntervalTarget(
            symbol="H1",
            kind=3,
            min_interval=15.0,
            max_interval=17.0,
        ),
        expected_ways_target=ExpectedWaysTarget(
            symbol="H1",
            kind=3,
            min_ways=0.05,
            max_ways=0.07,
        ),
        group_rtp_target=GroupRtpTarget(
            name="premium",
            symbols=["H1"],
            min_natural_rtp_pct=24.0,
            max_natural_rtp_pct=26.0,
        ),
    )

    components = analyzer.penalty_components(candidate)

    assert components == {
        "targets": 0.0,
        "expected_ways": 0.0,
        "group_rtp": 0.0,
        "progression": 0.0,
        "symbol_order": 0.0,
        "preservation": 0.0,
        "expected_ways_preservation": 0.0,
        "total": 0.0,
    }
    assert analyzer.penalty(candidate) == 0.0


def test_penalty_components_apply_configured_objective_weight() -> None:
    candidate = repeated_reels(["H1", "H1", "X"])
    base_config = create_default_configs()[GameMode.BASE]
    config = base_config.model_copy(
        update={
            "targets": [],
            "expected_ways_targets": [],
            "group_rtp_targets": [],
            "objective": base_config.objective.model_copy(
                update={
                    "progression_weight": 2.0,
                    "symbol_order_weight": 0.0,
                    "preserve_untargeted_weight": 0.0,
                    "preserve_untargeted_ways_weight": 0.0,
                    "frequency_orders": [],
                }
            ),
        }
    )
    scorer = OptimizationScorer(
        config,
        OptimizationInput(
            source=ReelSetComponent(reels=candidate, weight=1.0),
            fixed_reel_sets=(),
            window_size=1,
        ),
    )

    components = scorer.penalty_components(candidate)

    assert components["progression"] == pytest.approx(2.0 * math.log(2.0) ** 2)
    assert components["total"] == pytest.approx(components["progression"])
