from fastapi import FastAPI
from enum import StrEnum

optimizer = FastAPI(
    title="KavunBet Optimizer",
    version="0.1.0",
)

class GameMode(StrEnum):
    BASE = "base"
    FREE = "free"

@optimizer.get("/health")
def healh_check() -> dict[str,str]:
    return {"status": "ok"}

@optimizer.get("/optimization-configs/{mode}")
def get_config(mode: GameMode) -> dict[str, str]:
    return {"mode":mode}

# @optimizer.post("/optimization-runs")