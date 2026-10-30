from collections import Counter


class ReelSet:
    def __init__(self, reels: list[list[str]]) -> None:
        if not reels or any(not reel for reel in reels):
            raise ValueError("a reel set must contain non-empty reels")

        self.reels = [reel.copy() for reel in reels]

    @property
    def reel_count(self) -> int:
        return len(self.reels)

    def copy(self) -> "ReelSet":
        return ReelSet(self.reels)

    def counts(self) -> Counter[str]:
        return Counter(symbol for reel in self.reels for symbol in reel)


def cyclic_max_run(reel: list[str], symbol: str) -> int:
    if not reel:
        return 0

    if all(value == symbol for value in reel):
        return len(reel)

    doubled = reel + reel
    best = 0
    current = 0

    for value in doubled:
        current = current + 1 if value == symbol else 0
        best = max(best, current)
    return min(best, len(reel))
