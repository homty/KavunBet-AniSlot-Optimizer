from kavunbet_optimizer.domain.config_repository import OptimizationConfigRepository


class OptimizationConfigService:
    def __init__(self, repository: OptimizationConfigRepository) -> None:
        self._repository = repository
