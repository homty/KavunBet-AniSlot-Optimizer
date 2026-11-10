from kavunbet_optimizer.domain.reel_set import ReelSet, cyclic_max_run
from kavunbet_optimizer.schemas.constraints import Constraints


class ConstraintChecker:
    def __init__(self, constraints: Constraints, reel_count: int) -> None:
        if reel_count <= 0:
            raise ValueError("reel count must be positive")

        for symbol, last_reel in constraints.last_allowed_reel.items():
            if last_reel > reel_count:
                raise ValueError(f"{symbol}: last allowed reel exceeds the reel count")

        self._constraints = constraints
        self._reel_count = reel_count

    def is_valid(self, candidate: ReelSet) -> bool:
        if candidate.reel_count != self._reel_count:
            return False

        counts = candidate.counts()
        for symbol, (minimum, maximum) in self._constraints.global_count_ranges.items():
            if not minimum <= counts.get(symbol, 0) <= maximum:
                return False

        for reel_number, reel in enumerate(candidate.reels, start=1):
            for symbol, last_reel in self._constraints.last_allowed_reel.items():
                if reel_number > last_reel and symbol in reel:
                    return False

            for symbol, maximum in self._constraints.max_consecutive.items():
                if cyclic_max_run(reel, symbol) > maximum:
                    return False

        return True
