from fastapi import FastAPI

from kavunbet_optimizer.api.health import router as health_router
from kavunbet_optimizer.api.optimization_configs import router as optimization_configs_router

app = FastAPI(
    title="KavunBet Optimizer",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(optimization_configs_router)
