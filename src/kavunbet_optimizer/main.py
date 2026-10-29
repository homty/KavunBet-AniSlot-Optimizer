import os
from pathlib import Path

from fastapi import FastAPI

from kavunbet_optimizer.api.health import router as health_router
from kavunbet_optimizer.api.optimization_configs import router as optimization_configs_router
from kavunbet_optimizer.domain.config_repository import OptimizationConfigRepository
from kavunbet_optimizer.infrastructure.json_config_repository import (
    JsonOptimizationConfigRepository,
)


def create_app(
    repository: OptimizationConfigRepository | None = None,
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

    app.state.config_repository = repository
    app.include_router(health_router)
    app.include_router(optimization_configs_router)

    return app


app = create_app()
