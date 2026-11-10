import math
import random
from collections.abc import Mapping

from kavunbet_optimizer.application.optimization_runner import (
    CancellationCheck,
    OptimizationCancelledError,
    OptimizationProgress,
    OptimizationRunnerResult,
    ProgressCallback,
)
from kavunbet_optimizer.domain.optimization import CandidateMutator, ConstraintChecker
from kavunbet_optimizer.domain.optimization_input import OptimizationInput
from kavunbet_optimizer.domain.scoring import OptimizationScorer
from kavunbet_optimizer.schemas.configuration import OptimizationConfig


class SimulatedAnnealingRunner:
    def __init__(
        self,
        paytable: Mapping[tuple[int, str], float] | None = None,
    ) -> None:
        self._paytable = paytable

    def optimize(
        self,
        config: OptimizationConfig,
        optimization_input: OptimizationInput,
        *,
        progress_callback: ProgressCallback | None = None,
        cancellation_check: CancellationCheck | None = None,
    ) -> OptimizationRunnerResult:
        scorer = OptimizationScorer(config, optimization_input, self._paytable)
        source = optimization_input.source.reels
        scorer.validate_shape(source)

        constraint_checker = ConstraintChecker(config.constraints, source.reel_count)
        if not constraint_checker.is_valid(source):
            raise ValueError("source reels violate configured hard constraints")

        random_source = random.Random(config.optimization.seed)
        mutator = CandidateMutator(
            config.optimization.moves,
            config.constraints.composition_symbols,
            random_source,
        )

        current = source.copy()
        best = source.copy()
        current_penalty = scorer.penalty(current)
        initial_penalty = current_penalty
        best_penalty = current_penalty
        accepted_moves = 0
        completed_iterations = 0
        settings = config.optimization

        for iteration in range(1, settings.iterations + 1):
            if cancellation_check is not None and cancellation_check():
                raise OptimizationCancelledError("optimization was cancelled")

            completed_iterations = iteration
            candidate = current.copy()
            if mutator.mutate(candidate) and constraint_checker.is_valid(candidate):
                candidate_penalty = scorer.penalty(candidate)
                progress = iteration / settings.iterations
                temperature = settings.start_temperature * (
                    (settings.end_temperature / settings.start_temperature) ** progress
                )
                delta = candidate_penalty - current_penalty

                if delta <= 0 or random_source.random() < math.exp(-delta / temperature):
                    current = candidate
                    current_penalty = candidate_penalty
                    accepted_moves += 1

                    if current_penalty < best_penalty:
                        best = current.copy()
                        best_penalty = current_penalty

            if (
                progress_callback is not None
                and settings.report_every > 0
                and iteration % settings.report_every == 0
            ):
                progress_callback(
                    OptimizationProgress(
                        iteration=iteration,
                        best_penalty=best_penalty,
                        accepted_moves=accepted_moves,
                    )
                )

            if best_penalty <= 1e-15:
                break

        return OptimizationRunnerResult(
            reels=best,
            initial_penalty=initial_penalty,
            final_penalty=best_penalty,
            iterations=completed_iterations,
            accepted_moves=accepted_moves,
        )
