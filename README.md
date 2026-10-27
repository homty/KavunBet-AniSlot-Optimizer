# KavunBet Optimizer Service

Independent FastAPI microservice that owns optimization configuration and will
orchestrate optimization runs for KavunBet slot mathematics.

## Responsibilities

- expose the frontend-facing REST API;
- validate base and free-game optimization settings;
- own optimization objectives, constraints, runs, and reports;
- generate candidate configurations;
- call the separate MathEngine service over gRPC.

This repository does not contain MathEngine implementation or deployment
infrastructure.

## Requirements

- Python 3.12
- uv

## Install

```powershell
uv sync --extra dev
```

## Run

```powershell
uv run uvicorn kavunbet_optimizer.main:app --reload
```

The local API is available at `http://127.0.0.1:8000` and its OpenAPI UI at
`http://127.0.0.1:8000/docs`.

## Test

```powershell
uv run pytest
```

## Current endpoints

- `GET /health`
- `GET /optimization-configs/{mode}/optimization`
- `PATCH /optimization-configs/{mode}/optimization`

Supported modes are `base` and `free`.

The current configuration store is intentionally in memory. Persistent storage
and the MathEngine gRPC client will be introduced behind separate interfaces.
