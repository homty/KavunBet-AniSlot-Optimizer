import math
from collections.abc import Mapping, Sequence

from kavunbet_optimizer.domain.analysis.models import CombinationMetric
from kavunbet_optimizer.domain.analysis.natural_rtp import group_natural_rtp_pct
from kavunbet_optimizer.domain.scoring.models import (
    ExpectedWaysEvaluation,
    GroupRtpEvaluation,
    TargetEvaluation,
)
from kavunbet_optimizer.schemas.expected_ways_targets import ExpectedWaysTarget
from kavunbet_optimizer.schemas.group_rtp_targets import GroupRtpTarget
from kavunbet_optimizer.schemas.targets import IntervalTarget


def band_error(value: float, minimum: float, maximum: float) -> float:
    if value < minimum:
        return math.log(minimum / max(value, 1e-300))
    if value > maximum:
        return math.log(value / maximum)
    return 0.0


def evaluate_interval_targets(
    targets: Sequence[IntervalTarget],
    matrix: dict[str, dict[int, CombinationMetric]],
) -> tuple[TargetEvaluation, ...]:
    evaluations = []
    for target in targets:
        metric = matrix[target.symbol][target.kind]
        error = band_error(metric.interval, target.min_interval, target.max_interval)
        evaluations.append(
            TargetEvaluation(
                target=target,
                metric=metric,
                error=error,
                penalty=target.weight * error * error,
            )
        )
    return tuple(evaluations)


def evaluate_expected_ways_targets(
    targets: Sequence[ExpectedWaysTarget],
    matrix: dict[str, dict[int, float]],
) -> tuple[ExpectedWaysEvaluation, ...]:
    evaluations = []
    for target in targets:
        expected_ways = matrix[target.symbol][target.kind]
        error = band_error(expected_ways, target.min_ways, target.max_ways)
        evaluations.append(
            ExpectedWaysEvaluation(
                target=target,
                expected_ways=expected_ways,
                error=error,
                penalty=target.weight * error * error,
            )
        )
    return tuple(evaluations)


def evaluate_group_rtp_targets(
    targets: Sequence[GroupRtpTarget],
    expected_ways_matrix: dict[str, dict[int, float]],
    paytable: Mapping[tuple[int, str], float] | None,
) -> tuple[GroupRtpEvaluation, ...]:
    if paytable is None:
        if targets:
            raise ValueError("group RTP targets require the scaled game paytable")
        return ()

    evaluations = []
    for target in targets:
        natural_rtp_pct = group_natural_rtp_pct(target, expected_ways_matrix, paytable)
        error = band_error(
            natural_rtp_pct,
            target.min_natural_rtp_pct,
            target.max_natural_rtp_pct,
        )
        evaluations.append(
            GroupRtpEvaluation(
                target=target,
                natural_rtp_pct=natural_rtp_pct,
                error=error,
                penalty=target.weight * error * error,
            )
        )
    return tuple(evaluations)
