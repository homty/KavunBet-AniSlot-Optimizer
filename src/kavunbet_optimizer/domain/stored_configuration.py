from dataclasses import dataclass

from kavunbet_optimizer.schemas.configuration import OptimizationConfig


@dataclass(frozen=True, slots=True)
class StoredOptimizationConfig:
    config: OptimizationConfig
    version: str
