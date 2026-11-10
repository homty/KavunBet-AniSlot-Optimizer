from collections.abc import Mapping

from kavunbet_optimizer.domain.analysis.expected_ways import (
    component_expected_exact_ways_matrix,
    expected_ways_matrix,
)
from kavunbet_optimizer.domain.analysis.models import CombinationMetric
from kavunbet_optimizer.domain.analysis.probability import (
    PresenceProfile,
    exact_from_presence,
    metric_from_profiles,
    presence_profile,
    probability_matrix,
    reel_multiplicity,
    reel_presence,
)
from kavunbet_optimizer.domain.optimization_input import OptimizationInput
from kavunbet_optimizer.domain.reel_set import ReelSet
from kavunbet_optimizer.domain.scoring.evaluations import (
    band_error,
    evaluate_expected_ways_targets,
    evaluate_group_rtp_targets,
    evaluate_interval_targets,
)
from kavunbet_optimizer.domain.scoring.models import (
    ExpectedWaysEvaluation,
    GroupRtpEvaluation,
    TargetEvaluation,
)
from kavunbet_optimizer.domain.scoring.objective_penalties import (
    expected_ways_preservation_penalty,
    interval_preservation_penalty,
    progression_penalty,
    symbol_order_penalty,
)
from kavunbet_optimizer.schemas.configuration import OptimizationConfig


class OptimizationScorer:
    _band_error = staticmethod(band_error)

    def __init__(
        self,
        config: OptimizationConfig,
        optimization_input: OptimizationInput,
        paytable: Mapping[tuple[int, str], float] | None = None,
    ) -> None:
        if config.group_rtp_targets and paytable is None:
            raise ValueError("group RTP targets require the scaled game paytable")

        self.config = config
        self.optimization_input = optimization_input
        self.paytable = paytable
        self._fixed_profiles = tuple(
            (
                component.weight,
                self._presence_profile(component.reels, component.substitutes),
            )
            for component in optimization_input.fixed_reel_sets
        )
        self._target_keys = {(target.symbol, target.kind) for target in config.targets}
        self._expected_ways_target_keys = {
            (target.symbol, target.kind) for target in config.expected_ways_targets
        }

        source_profile = self._presence_profile(
            optimization_input.source.reels,
            optimization_input.source.substitutes,
        )
        source_matrix = probability_matrix(
            source_profile,
            self._fixed_profiles,
            optimization_input.source.weight,
            config.symbols,
        )
        self._source_intervals = {
            (symbol, kind): source_matrix[symbol][kind].interval
            for symbol in config.symbols
            for kind in (3, 4, 5, 6)
        }
        source_expected_ways = expected_ways_matrix(
            optimization_input.source.reels,
            config.symbols,
            optimization_input.window_size,
            optimization_input.source.weight,
            optimization_input.source.substitutes,
            optimization_input.fixed_reel_sets,
            self._fixed_profiles,
            source_profile,
        )
        self._source_expected_ways = {
            (symbol, kind): source_expected_ways[symbol][kind]
            for symbol in config.symbols
            for kind in (3, 4, 5, 6)
        }

    def validate_shape(self, candidate: ReelSet) -> None:
        if candidate.reel_count < 6:
            raise ValueError("the optimizer requires at least six reels")
        if any(self.optimization_input.window_size > len(reel) for reel in candidate.reels):
            raise ValueError("window size exceeds a candidate reel length")

        components = (
            self.optimization_input.source,
            *self.optimization_input.fixed_reel_sets,
        )
        for component in components:
            if component.reels.reel_count != candidate.reel_count:
                raise ValueError("all reel sets must have the same reel count")

    def reel_multiplicity(
        self,
        reel: list[str],
        symbol: str,
        substitutes: tuple[str, ...] = (),
    ) -> tuple[int, ...]:
        return reel_multiplicity(
            reel,
            symbol,
            self.optimization_input.window_size,
            substitutes,
        )

    def reel_presence(
        self,
        reel: list[str],
        symbol: str,
        substitutes: tuple[str, ...] = (),
    ) -> float:
        return reel_presence(
            reel,
            symbol,
            self.optimization_input.window_size,
            substitutes,
        )

    def _presence_profile(
        self,
        reels: ReelSet,
        substitutes: tuple[str, ...] = (),
    ) -> PresenceProfile:
        return presence_profile(
            reels,
            self.config.symbols,
            self.optimization_input.window_size,
            substitutes,
        )

    @staticmethod
    def _exact_from_presence(presence: tuple[float, ...], kind: int) -> float:
        return exact_from_presence(presence, kind)

    def _metric_from_profile(
        self,
        candidate_profile: PresenceProfile,
        symbol: str,
        kind: int,
    ) -> CombinationMetric:
        return metric_from_profiles(
            candidate_profile,
            self._fixed_profiles,
            self.optimization_input.source.weight,
            symbol,
            kind,
        )

    def metric(self, candidate: ReelSet, symbol: str, kind: int) -> CombinationMetric:
        self.validate_shape(candidate)
        profile = self._presence_profile(
            candidate,
            self.optimization_input.source.substitutes,
        )
        return self._metric_from_profile(profile, symbol, kind)

    def matrix(self, candidate: ReelSet) -> dict[str, dict[int, CombinationMetric]]:
        self.validate_shape(candidate)
        profile = self._presence_profile(
            candidate,
            self.optimization_input.source.substitutes,
        )
        return probability_matrix(
            profile,
            self._fixed_profiles,
            self.optimization_input.source.weight,
            self.config.symbols,
        )

    def _evaluate_matrix(
        self,
        matrix: dict[str, dict[int, CombinationMetric]],
    ) -> tuple[TargetEvaluation, ...]:
        return evaluate_interval_targets(self.config.targets, matrix)

    def evaluate(self, candidate: ReelSet) -> tuple[TargetEvaluation, ...]:
        return self._evaluate_matrix(self.matrix(candidate))

    def _component_expected_exact_ways_matrix(
        self,
        reels: ReelSet,
        substitutes: tuple[str, ...],
        symbol: str,
        presence: tuple[float, ...] | None = None,
    ) -> dict[int, float]:
        return component_expected_exact_ways_matrix(
            reels,
            self.optimization_input.window_size,
            substitutes,
            symbol,
            presence,
        )

    def _expected_ways_matrix(
        self,
        candidate: ReelSet,
        candidate_profile: PresenceProfile | None = None,
    ) -> dict[str, dict[int, float]]:
        self.validate_shape(candidate)
        if candidate_profile is None:
            candidate_profile = self._presence_profile(
                candidate,
                self.optimization_input.source.substitutes,
            )
        return expected_ways_matrix(
            candidate,
            self.config.symbols,
            self.optimization_input.window_size,
            self.optimization_input.source.weight,
            self.optimization_input.source.substitutes,
            self.optimization_input.fixed_reel_sets,
            self._fixed_profiles,
            candidate_profile,
        )

    def expected_exact_ways(
        self,
        candidate: ReelSet,
        symbol: str,
        kind: int,
    ) -> float:
        if symbol not in self.config.symbols:
            raise ValueError(f"unknown symbol: {symbol}")
        if kind not in (3, 4, 5, 6):
            raise ValueError("kind must be one of 3, 4, 5, or 6")
        return self._expected_ways_matrix(candidate)[symbol][kind]

    def _evaluate_expected_ways_matrix(
        self,
        matrix: dict[str, dict[int, float]],
    ) -> tuple[ExpectedWaysEvaluation, ...]:
        return evaluate_expected_ways_targets(self.config.expected_ways_targets, matrix)

    def evaluate_expected_ways(
        self,
        candidate: ReelSet,
    ) -> tuple[ExpectedWaysEvaluation, ...]:
        return self._evaluate_expected_ways_matrix(self._expected_ways_matrix(candidate))

    def _evaluate_group_rtp_matrix(
        self,
        matrix: dict[str, dict[int, float]],
    ) -> tuple[GroupRtpEvaluation, ...]:
        return evaluate_group_rtp_targets(
            self.config.group_rtp_targets,
            matrix,
            self.paytable,
        )

    def evaluate_group_rtp(
        self,
        candidate: ReelSet,
    ) -> tuple[GroupRtpEvaluation, ...]:
        return self._evaluate_group_rtp_matrix(self._expected_ways_matrix(candidate))

    def penalty_components(self, candidate: ReelSet) -> dict[str, float]:
        self.validate_shape(candidate)
        candidate_profile = self._presence_profile(
            candidate,
            self.optimization_input.source.substitutes,
        )
        matrix = probability_matrix(
            candidate_profile,
            self._fixed_profiles,
            self.optimization_input.source.weight,
            self.config.symbols,
        )
        expected_ways = self._expected_ways_matrix(candidate, candidate_profile)

        target_penalty = sum(evaluation.penalty for evaluation in self._evaluate_matrix(matrix))
        expected_ways_penalty = sum(
            evaluation.penalty for evaluation in self._evaluate_expected_ways_matrix(expected_ways)
        )
        group_rtp_penalty = sum(
            evaluation.penalty for evaluation in self._evaluate_group_rtp_matrix(expected_ways)
        )

        objective = self.config.objective
        weighted_progression = (
            progression_penalty(matrix, self.config.symbols) * objective.progression_weight
        )
        weighted_symbol_order = (
            symbol_order_penalty(matrix, objective.frequency_orders) * objective.symbol_order_weight
        )
        weighted_preservation = (
            interval_preservation_penalty(
                matrix,
                self._source_intervals,
                self._target_keys,
                objective.preserve_untargeted_tolerance,
            )
            * objective.preserve_untargeted_weight
        )
        weighted_ways_preservation = (
            expected_ways_preservation_penalty(
                expected_ways,
                self._source_expected_ways,
                self._expected_ways_target_keys,
                objective.preserve_untargeted_ways_tolerance,
            )
            * objective.preserve_untargeted_ways_weight
        )
        total_penalty = (
            target_penalty
            + expected_ways_penalty
            + group_rtp_penalty
            + weighted_progression
            + weighted_symbol_order
            + weighted_preservation
            + weighted_ways_preservation
        )

        return {
            "targets": target_penalty,
            "expected_ways": expected_ways_penalty,
            "group_rtp": group_rtp_penalty,
            "progression": weighted_progression,
            "symbol_order": weighted_symbol_order,
            "preservation": weighted_preservation,
            "expected_ways_preservation": weighted_ways_preservation,
            "total": total_penalty,
        }

    def penalty(self, candidate: ReelSet) -> float:
        return self.penalty_components(candidate)["total"]
