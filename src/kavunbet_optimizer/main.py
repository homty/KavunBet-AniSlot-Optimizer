import os
from pathlib import Path

from fastapi import FastAPI

from kavunbet_optimizer.api.health import router as health_router
from kavunbet_optimizer.api.optimization_configs import router as optimization_configs_router
from kavunbet_optimizer.api.optimization_jobs import router as optimization_jobs_router
from kavunbet_optimizer.application.optimization_job_service import (
    OptimizationJobService,
)
from kavunbet_optimizer.domain.config_repository import OptimizationConfigRepository
from kavunbet_optimizer.domain.optimization_job_repository import (
    OptimizationJobRepository,
)
from kavunbet_optimizer.infrastructure.in_memory_optimization_job_repository import (
    InMemoryOptimizationJobRepository,
)
from kavunbet_optimizer.infrastructure.json_config_repository import (
    JsonOptimizationConfigRepository,
)


def create_app(
    repository: OptimizationConfigRepository | None = None,
    job_repository: OptimizationJobRepository | None = None,
) -> FastAPI:
    app = FastAPI(
        title="KavunBet Optimizer",
        version="0.1.0",
    )

    if repository is None:
        default_config_directory = Path(__file__).resolve().parent / "configs"
        config_directory = Path(
            os.environ.get("KAVUNBET_CONFIG_DIRECTORY", default_config_directory)
        )
        repository = JsonOptimizationConfigRepository(config_directory)

    if job_repository is None:
        job_repository = InMemoryOptimizationJobRepository()

    app.state.config_repository = repository
    app.state.optimization_job_repository = job_repository
    app.state.optimization_job_service = OptimizationJobService(
        job_repository=job_repository,
        config_repository=repository,
    )
    app.include_router(health_router)
    app.include_router(optimization_configs_router)
    app.include_router(optimization_jobs_router)

    return app


app = create_app()
