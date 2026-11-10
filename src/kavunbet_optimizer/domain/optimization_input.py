from dataclasses import dataclass

from kavunbet_optimizer.domain.reel_set import ReelSet


@dataclass(frozen=True, slots=True)
class ReelSetComponent:
    reels: ReelSet
    weight: float
    substitutes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0 < self.weight <= 1:
            raise ValueError("reel-set component weight must be in (0, 1]")
        if len(set(self.substitutes)) != len(self.substitutes):
            raise ValueError("reel-set component substitutes must be unique")

        object.__setattr__(self, "reels", self.reels.copy())
        object.__setattr__(self, "substitutes", tuple(self.substitutes))


@dataclass(frozen=True, slots=True)
class OptimizationInput:
    source: ReelSetComponent
    fixed_reel_sets: tuple[ReelSetComponent, ...]
    window_size: int

    def __post_init__(self) -> None:
        fixed_reel_sets = tuple(self.fixed_reel_sets)
        object.__setattr__(self, "fixed_reel_sets", fixed_reel_sets)

        if self.window_size <= 0:
            raise ValueError("window size must be positive")

        components = (self.source, *fixed_reel_sets)
        total_weight = sum(component.weight for component in components)
        if abs(total_weight - 1.0) > 1e-9:
            raise ValueError("source and fixed reel-set weights must sum to 1")

        reel_count = self.source.reels.reel_count
        if any(component.reels.reel_count != reel_count for component in components):
            raise ValueError("all reel-set components must have the same reel count")

        if any(
            self.window_size > len(reel)
            for component in components
            for reel in component.reels.reels
        ):
            raise ValueError("window size exceeds a reel length")
