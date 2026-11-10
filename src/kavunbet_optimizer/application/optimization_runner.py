from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from kavunbet_optimizer.domain.optimization_input import OptimizationInput
from kavunbet_optimizer.domain.reel_set import ReelSet
from kavunbet_optimizer.schemas.configuration import OptimizationConfig


@dataclass(frozen=True, slots=True)
class OptimizationProgress:
    iteration: int
    best_penalty: float
    accepted_moves: int


@dataclass(frozen=True, slots=True)
class OptimizationRunnerResult:
    reels: ReelSet
    initial_penalty: float
    final_penalty: float
    iterations: int
    accepted_moves: int


ProgressCallback = Callable[[OptimizationProgress], None]
CancellationCheck = Callable[[], bool]


class OptimizationCancelledError(RuntimeError):
    """Raised when cancellation is requested during a local optimization run."""


class OptimizationRunner(Protocol):
    def optimize(
        self,
        config: OptimizationConfig,
        optimization_input: OptimizationInput,
        *,
        progress_callback: ProgressCallback | None = None,
        cancellation_check: CancellationCheck | None = None,
    ) -> OptimizationRunnerResult: ...
