from typing import Protocol
from uuid import UUID

from kavunbet_optimizer.domain.optimization_job import OptimizationJob


class OptimizationJobRepository(Protocol):
    def create(self, job: OptimizationJob) -> OptimizationJob: ...

    def get(self, job_id: UUID) -> OptimizationJob: ...

    def get_by_idempotency_key(self, idempotency_key: str) -> OptimizationJob | None: ...

    def save(self, job: OptimizationJob) -> OptimizationJob: ...
