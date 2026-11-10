import math
from collections.abc import Mapping
from dataclasses import dataclass

from kavunbet_optimizer.domain.optimization_input import OptimizationInput
from kavunbet_optimizer.domain.reel_set import ReelSet
from kavunbet_optimizer.schemas.configuration import OptimizationConfig


@dataclass(frozen=True, slots=True)
class CombinationMetric:
    symbol: str
    kind: int
    probability: float

    @property
    def interval(self) -> float:
        return 1.0 / self.probability if self.probability > 0 else math.inf


class CombinationAnalyzer:
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
        self, reel: list[str], symbol: str, substitutes: tuple[str, ...] = ()
    ) -> tuple[int, ...]:
        accepted_symbols = {symbol, *substitutes}
        reel_length = len(reel)

        return tuple(
            sum(
                reel[(start + offset) % reel_length] in accepted_symbols
                for offset in range(self.optimization_input.window_size)
            )
            for start in range(reel_length)
        )

    def reel_presence(
        self, reel: list[str], symbol: str, substitutes: tuple[str, ...] = ()
    ) -> float:
        multiplicities = self.reel_multiplicity(reel, symbol, substitutes)

        covered_stops = sum(multiplicity > 0 for multiplicity in multiplicities)

        return covered_stops / len(multiplicities)
