import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CombinationMetric:
    symbol: str
    kind: int
    probability: float

    @property
    def interval(self) -> float:
        return 1.0 / self.probability if self.probability > 0 else math.inf
