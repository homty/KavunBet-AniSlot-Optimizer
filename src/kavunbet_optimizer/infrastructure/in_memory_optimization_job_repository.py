from threading import RLock
from uuid import UUID

from kavunbet_optimizer.domain.exceptions import OptimizationJobErrors
from kavunbet_optimizer.domain.optimization_job import OptimizationJob


class InMemoryOptimizationJobRepository:
    def __init__(self) -> None:
        self._jobs: dict[UUID, OptimizationJob] = {}
        self._idempotency_keys: dict[str, UUID] = {}
        self._lock = RLock()

    def create(self, job: OptimizationJob) -> OptimizationJob:
        with self._lock:
            if job.id in self._jobs:
                raise OptimizationJobErrors.OptimizationJobAlreadyExistsError(
                    f"optimization job already exists: {job.id}"
                )

            if job.idempotency_key in self._idempotency_keys:
                raise OptimizationJobErrors.IdempotencyKeyConflictError(
                    f"idempotency key already exists: {job.idempotency_key}"
                )

            stored = job.model_copy(deep=True)
            self._jobs[job.id] = stored
            self._idempotency_keys[job.idempotency_key] = job.id

            return stored.model_copy(deep=True)  # belong to the caller

    def get(self, job_id: UUID) -> OptimizationJob:
        with self._lock:
            job = self._jobs.get(job_id)

            if job is None:
                raise OptimizationJobErrors.OptimizationJobNotFoundError(
                    f"optimization job not found: {job_id}"
                )
            return job.model_copy(deep=True)

    def get_by_idempotency_key(self, idempotency_key: str) -> OptimizationJob | None:
        with self._lock:
            job_id = self._idempotency_keys.get(idempotency_key)

            if job_id is None:
                return None

            job = self._jobs[job_id]
            return job.model_copy(deep=True)

    def save(self, job: OptimizationJob) -> OptimizationJob:
        with self._lock:
            current = self._jobs.get(job.id)

            if current is None:
                raise OptimizationJobErrors.OptimizationJobNotFoundError(
                    f"optimization job not found: {job.id}"
                )

            key_owner = self._idempotency_keys.get(job.idempotency_key)

            if key_owner is not None and key_owner != job.id:
                raise OptimizationJobErrors.IdempotencyKeyConflictError(
                    f"idempotency key already exists: {job.idempotency_key}"
                )

            if current.idempotency_key != job.idempotency_key:
                del self._idempotency_keys[current.idempotency_key]
                self._idempotency_keys[job.idempotency_key] = job.id

            stored = job.model_copy(deep=True)
            self._jobs[job.id] = stored

            return stored.model_copy(deep=True)
