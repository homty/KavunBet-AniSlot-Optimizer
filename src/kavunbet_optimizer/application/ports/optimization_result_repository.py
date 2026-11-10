from typing import Protocol
from uuid import UUID

from kavunbet_optimizer.domain.optimization_result import OptimizationResultArtifact


class OptimizationResultRepository(Protocol):
    def create(
        self,
        artifact: OptimizationResultArtifact,
    ) -> OptimizationResultArtifact: ...

    def get(
        self,
        artifact_id: UUID,
    ) -> OptimizationResultArtifact: ...

    def get_by_job_id(
        self,
        job_id: UUID,
    ) -> OptimizationResultArtifact | None: ...
