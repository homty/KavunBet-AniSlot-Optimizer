from dataclasses import dataclass

from kavunbet_optimizer.domain.analysis.models import CombinationMetric
from kavunbet_optimizer.schemas.expected_ways_targets import ExpectedWaysTarget
from kavunbet_optimizer.schemas.group_rtp_targets import GroupRtpTarget
from kavunbet_optimizer.schemas.targets import IntervalTarget


@dataclass(frozen=True, slots=True)
class TargetEvaluation:
    target: IntervalTarget
    metric: CombinationMetric
    error: float
    penalty: float

    @property
    def passes(self) -> bool:
        return self.error == 0.0


@dataclass(frozen=True, slots=True)
class ExpectedWaysEvaluation:
    target: ExpectedWaysTarget
    expected_ways: float
    error: float
    penalty: float

    @property
    def passes(self) -> bool:
        return self.error == 0.0


@dataclass(frozen=True, slots=True)
class GroupRtpEvaluation:
    target: GroupRtpTarget
    natural_rtp_pct: float
    error: float
    penalty: float

    @property
    def passes(self) -> bool:
        return self.error == 0.0
