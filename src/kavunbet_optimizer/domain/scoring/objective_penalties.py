import math
from itertools import pairwise

from kavunbet_optimizer.domain.analysis import CombinationMetric


def progression_penalty(
    matrix: dict[str, dict[int, CombinationMetric]], symbols: list[str]
) -> float:
    penalty = 0.0

    for symbol in symbols:
        for kind in (3, 4, 5):
            current_probability = matrix[symbol][kind].probability
            following_probability = matrix[symbol][kind + 1].probability

            if following_probability > current_probability > 0:
                ratio = following_probability / current_probability
                penalty += math.log(ratio) ** 2
            elif following_probability > 0 and current_probability <= 0:
                penalty += 100.0

    return penalty


def symbol_order_penalty(
    matrix: dict[str, dict[int, CombinationMetric]], frequency_orders: list[list[str]]
) -> float:
    penalty = 0.0

    for order in frequency_orders:
        for kind in (3, 4, 5, 6):
            for more_common, less_common in pairwise(order):
                common_probability = matrix[more_common][kind].probability
                rare_probability = matrix[less_common][kind].probability

                if rare_probability > common_probability > 0:
                    ratio = rare_probability / common_probability
                    penalty += math.log(ratio) ** 2
                elif rare_probability > 0 and common_probability <= 0:
                    penalty += 100.0

    return penalty


def interval_preservation_penalty(
    candidate_matrix: dict[str, dict[int, CombinationMetric]],
    baseline_intervals: dict[tuple[str, int], float],
    targeted_cells: set[tuple[str, int]],
    tolerance: float,
) -> float:
    penalty = 0.0

    if not 0 <= tolerance < 1:
        raise ValueError("tolerance must be between 0 inclusive and 1 exclusive")

    allowed_log_change = 0.0

    if tolerance > 0:
        allowed_log_change = -math.log(1.0 - tolerance)

    for symbol, symbol_metrics in candidate_matrix.items():
        for kind, metric in symbol_metrics.items():
            key = (symbol, kind)

            if key in targeted_cells:
                continue

            baseline_interval = baseline_intervals[key]
            candidate_interval = metric.interval

            if not math.isfinite(baseline_interval) or not math.isfinite(candidate_interval):
                if baseline_interval != candidate_interval:
                    penalty += 100.0

                continue

            log_change = abs(math.log(candidate_interval / baseline_interval))
            excess = max(0.0, log_change - allowed_log_change)
            penalty += excess**2

    return penalty


def expected_ways_preservation_penalty(
    candidate_expected_ways: dict[str, dict[int, float]],
    baseline_expected_ways: dict[tuple[str, int], float],
    targeted_cells: set[tuple[str, int]],
    tolerance: float,
) -> float:
    if not 0 <= tolerance < 1:
        raise ValueError("tolerance must be between 0 inclusive and 1 exclusive")

    allowed_log_change = 0.0
    if tolerance > 0:
        allowed_log_change = -math.log(1.0 - tolerance)

    penalty = 0.0
    for symbol, symbol_values in candidate_expected_ways.items():
        for kind, candidate_value in symbol_values.items():
            key = (symbol, kind)
            if key in targeted_cells:
                continue

            baseline_value = baseline_expected_ways[key]
            if baseline_value <= 0 or candidate_value <= 0:
                if baseline_value != candidate_value:
                    penalty += 100.0
                continue

            log_change = abs(math.log(candidate_value / baseline_value))
            excess = max(0.0, log_change - allowed_log_change)
            penalty += excess**2

    return penalty
