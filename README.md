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

- Python 3.12 or 3.13
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
uv run ruff check .
uv run ruff format --check .
```

## Current endpoints

- `GET /health`
- `GET /optimization-configs/{mode}/optimization`
- `PATCH /optimization-configs/{mode}/optimization`
- `GET /optimization-configs/{mode}/objective`
- `PATCH /optimization-configs/{mode}/objective`
- `GET /optimization-configs/{mode}/targets`
- `POST /optimization-configs/{mode}/targets`
- `PUT /optimization-configs/{mode}/targets/{symbol}/{kind}`
- `PATCH /optimization-configs/{mode}/targets/{symbol}/{kind}`
- `DELETE /optimization-configs/{mode}/targets/{symbol}/{kind}`
- `GET /optimization-configs/{mode}/expected-ways-targets`
- `POST /optimization-configs/{mode}/expected-ways-targets`
- `PUT /optimization-configs/{mode}/expected-ways-targets/{symbol}/{kind}`
- `PATCH /optimization-configs/{mode}/expected-ways-targets/{symbol}/{kind}`
- `DELETE /optimization-configs/{mode}/expected-ways-targets/{symbol}/{kind}`
- `GET /optimization-configs/{mode}/group-rtp-targets`
- `POST /optimization-configs/{mode}/group-rtp-targets`
- `PUT /optimization-configs/{mode}/group-rtp-targets/{name}`
- `PATCH /optimization-configs/{mode}/group-rtp-targets/{name}`
- `DELETE /optimization-configs/{mode}/group-rtp-targets/{name}`
- `GET /optimization-configs/{mode}/constraints`
- `PATCH /optimization-configs/{mode}/constraints`

Supported modes are `base` and `free`.

By default, production configuration is stored in packaged `base_config.json` and
`free_config.json` files through an atomic JSON repository. Tests inject an
isolated in-memory repository. The MathEngine gRPC client is not implemented yet.

Set `KAVUNBET_CONFIG_DIRECTORY` to use a writable external configuration directory,
such as a Docker volume or Raspberry Pi data directory. That directory must contain
both JSON configuration files before the service starts.
