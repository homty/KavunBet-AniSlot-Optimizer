"""Read configuration snapshots and submit durable optimization jobs."""

from datetime import UTC, datetime
from uuid import uuid4

from kavunbet_optimizer.domain.config_repository import OptimizationConfigRepository
from kavunbet_optimizer.domain.exceptions import OptimizationJobErrors
from kavunbet_optimizer.domain.optimization_job import JobStatus, OptimizationJob
from kavunbet_optimizer.domain.optimization_job_repository import (
    OptimizationJobRepository,
)
from kavunbet_optimizer.schemas.optimization import GameMode


class OptimizationJobService:
    def __init__(self, job_repository: OptimizationJobRepository, config_repository: OptimizationConfigRepository) -> None:
        self._job_repository = job_repository
        self._config_repository = config_repository

    def submit(self, project_id: str, engine_id: str, game_mode: GameMode, idempotency_key: str) -> OptimizationJob:
        existing_job = self._job_repository.get_by_idempotency_key(idempotency_key)

        if existing_job is not None:
            if (
                existing_job.project_id == project_id
                and existing_job.engine_id == engine_id
                and existing_job.game_mode == game_mode
            ):
                return existing_job

            raise OptimizationJobErrors.IdempotencyKeyConflictError(
                f"idempotency key is already used by another request: {idempotency_key}"
            )

        stored_config = self._config_repository.get(game_mode)
        config_snapshot = stored_config.config.model_copy(deep=True)  # deep configuration snapshot
        now = datetime.now(UTC)
        job = OptimizationJob(
            id=uuid4(),
            project_id=project_id,
            engine_id=engine_id,
            game_mode=game_mode,
            config_snapshot=config_snapshot,
            status=JobStatus.QUEUED,
            idempotency_key=idempotency_key,
            created_at=now,
            updated_at=now,
        )

        return self._job_repository.create(job)
