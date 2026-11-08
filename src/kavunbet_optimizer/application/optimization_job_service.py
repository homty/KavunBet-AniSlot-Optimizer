from kavunbet_optimizer.domain.optimization_job import OptimizationJob
from kavunbet_optimizer.schemas.optimization import GameMode


class OptimizationJobService:
    def submit(
        self, project_id: str, engine_id: str, game_mode: GameMode, idempotency_key: str
    ) -> OptimizationJob:
        """
        Read config, copy into config_snapshot, generate UUID, set status, timestamp, save job and then return it
        """
        raise NotImplementedError
