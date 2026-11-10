import pytest

from kavunbet_optimizer.application.optimization_runner import (
    OptimizationCancelledError,
    OptimizationProgress,
)
from kavunbet_optimizer.application.simulated_annealing_runner import (
    SimulatedAnnealingRunner,
)
from kavunbet_optimizer.domain.optimization_input import (
    OptimizationInput,
    ReelSetComponent,
)
from kavunbet_optimizer.domain.reel_set import ReelSet
from kavunbet_optimizer.schemas.configuration import OptimizationConfig
from kavunbet_optimizer.schemas.constraints import Constraints
from kavunbet_optimizer.schemas.objectives import ObjectiveSettings
from kavunbet_optimizer.schemas.optimization import MoveWeights, OptimizationSettings


def make_config(*, constraints: Constraints | None = None) -> OptimizationConfig:
    return OptimizationConfig(
        symbols=["A", "B"],
        optimization=OptimizationSettings(
            iterations=5,
            seed=7,
            start_temperature=0.2,
            end_temperature=0.01,
            report_every=1,
            moves=MoveWeights(
                within_reel=1.0,
                cross_reel=0.0,
                composition=0.0,
            ),
        ),
        objective=ObjectiveSettings(
            progression_weight=0.0,
            symbol_order_weight=0.0,
            preserve_untargeted_weight=0.0,
            preserve_untargeted_tolerance=0.2,
            preserve_untargeted_ways_weight=0.0,
            preserve_untargeted_ways_tolerance=0.1,
            frequency_orders=[],
        ),
        constraints=constraints or Constraints(),
    )


def make_input() -> OptimizationInput:
    return OptimizationInput(
        source=ReelSetComponent(
            reels=ReelSet([["A", "B"] for _ in range(6)]),
            weight=1.0,
        ),
        fixed_reel_sets=(),
        window_size=1,
    )


def test_runner_returns_result_without_mutating_source() -> None:
    optimization_input = make_input()
    original_reels = optimization_input.source.reels.copy().reels
    progress_updates: list[OptimizationProgress] = []

    result = SimulatedAnnealingRunner().optimize(
        make_config(),
        optimization_input,
        progress_callback=progress_updates.append,
    )

    assert optimization_input.source.reels.reels == original_reels
    assert result.initial_penalty == 0.0
    assert result.final_penalty == 0.0
    assert result.iterations == 1
    assert result.accepted_moves == 1
    assert progress_updates == [
        OptimizationProgress(iteration=1, best_penalty=0.0, accepted_moves=1)
    ]


def test_runner_is_deterministic_for_configured_seed() -> None:
    first = SimulatedAnnealingRunner().optimize(make_config(), make_input())
    second = SimulatedAnnealingRunner().optimize(make_config(), make_input())

    assert first.reels.reels == second.reels.reels
    assert first.initial_penalty == second.initial_penalty
    assert first.final_penalty == second.final_penalty
    assert first.iterations == second.iterations
    assert first.accepted_moves == second.accepted_moves


def test_runner_honors_cancellation_before_first_iteration() -> None:
    with pytest.raises(OptimizationCancelledError, match="cancelled"):
        SimulatedAnnealingRunner().optimize(
            make_config(),
            make_input(),
            cancellation_check=lambda: True,
        )


def test_runner_rejects_source_that_violates_constraints() -> None:
    config = make_config(constraints=Constraints(last_allowed_reel={"A": 1}))

    with pytest.raises(ValueError, match="source reels violate"):
        SimulatedAnnealingRunner().optimize(config, make_input())
