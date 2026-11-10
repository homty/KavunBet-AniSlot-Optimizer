import pytest

from kavunbet_optimizer.domain.optimization_input import (
    OptimizationInput,
    ReelSetComponent,
)
from kavunbet_optimizer.domain.reel_set import ReelSet


def component(
    *,
    weight: float,
    reel_count: int = 2,
    reel_length: int = 3,
) -> ReelSetComponent:
    return ReelSetComponent(
        reels=ReelSet(
            [
                [f"S{reel_index}-{stop}" for stop in range(reel_length)]
                for reel_index in range(reel_count)
            ]
        ),
        weight=weight,
    )


def test_optimization_input_accepts_valid_components() -> None:
    source = component(weight=0.95)
    fixed = component(weight=0.05)

    optimization_input = OptimizationInput(
        source=source,
        fixed_reel_sets=(fixed,),
        window_size=3,
    )

    assert optimization_input.source.weight == 0.95
    assert optimization_input.fixed_reel_sets == (fixed,)
    assert optimization_input.window_size == 3


@pytest.mark.parametrize("weight", [0, -0.1, 1.1])
def test_reel_set_component_rejects_invalid_weight(weight: float) -> None:
    with pytest.raises(ValueError, match="weight"):
        component(weight=weight)


def test_optimization_input_requires_weights_to_sum_to_one() -> None:
    with pytest.raises(ValueError, match="sum to 1"):
        OptimizationInput(
            source=component(weight=0.8),
            fixed_reel_sets=(component(weight=0.1),),
            window_size=3,
        )


def test_optimization_input_requires_matching_reel_counts() -> None:
    with pytest.raises(ValueError, match="same reel count"):
        OptimizationInput(
            source=component(weight=0.95, reel_count=2),
            fixed_reel_sets=(component(weight=0.05, reel_count=3),),
            window_size=3,
        )


def test_optimization_input_rejects_window_larger_than_reel() -> None:
    with pytest.raises(ValueError, match="window size exceeds"):
        OptimizationInput(
            source=component(weight=1.0, reel_length=3),
            fixed_reel_sets=(),
            window_size=4,
        )
