# KavunBet Optimizer Service — Project Status

## Project goal

Build the Optimizer as an independent microservice that allows the frontend to configure,
start, and monitor slot-math optimization runs.

The intended communication flow is:

```text
Frontend
   |
   | REST
   v
Nginx / API gateway
   |
   | REST
   v
Optimizer service
   |
   | gRPC
   v
MathEngine service
```

Responsibilities are separated as follows:

- **Nginx** routes requests, terminates TLS, and later exposes HTTP/2 or HTTP/3. It does not
  contain application or optimization logic.
- **Optimizer** owns configuration, optimization orchestration, run state, candidate selection,
  progress, and results.
- **MathEngine** performs mathematical evaluation requested by the Optimizer.
- **Frontend** edits configuration and displays optimization progress and output.

The Optimizer and MathEngine are separate services and should remain independently deployable.

## Current stage

We are building the **Optimizer configuration API foundation**.

At this stage, the service can represent, validate, and persistently modify the configuration used
by the existing slot optimizer. It does not yet start optimization runs or communicate with
MathEngine.

Production configuration changes survive service restarts through atomic JSON persistence. Tests
use an isolated in-memory repository.

## Completed

### Repository and service foundation

- Created a separate Python repository for the Optimizer microservice.
- Added a `src` package layout under `src/kavunbet_optimizer`.
- Added FastAPI and Uvicorn application startup.
- Added `uv` dependency management through `pyproject.toml`.
- Added Ruff configuration.
- Added a health endpoint:

```text
GET /health
```

### Configuration schemas

Pydantic models now represent the structures that already exist in `base_config.json` and
`free_config.json`:

- `optimization`
- `objective`
- `targets`
- `expected_ways_targets`
- `group_rtp_targets`
- `constraints`

No invented `algorithm` field is used.

The schemas validate local rules such as:

- positive iteration and temperature values;
- valid move weights;
- valid minimum/maximum ranges;
- valid target kinds;
- positive target weights;
- unique group RTP symbols;
- positive constraint limits;
- valid global count ranges;
- rejection of unknown JSON fields.

The complete configuration aggregate validates unique identities and symbol references across
sections. Validation that requires the physical reel count remains deferred until reel metadata is
available to this service.

### Default configuration

Packaged `base_config.json` and `free_config.json` files contain the initial SDK configuration.
Production loads and writes these documents through the JSON repository, while preserving fields
outside the managed API sections.

### Implemented HTTP API

Singleton configuration sections support reading and partial updates:

```text
GET   /optimization-configs/{mode}/optimization
PATCH /optimization-configs/{mode}/optimization

GET   /optimization-configs/{mode}/objective
PATCH /optimization-configs/{mode}/objective

GET   /optimization-configs/{mode}/constraints
PATCH /optimization-configs/{mode}/constraints
```

`{mode}` is currently either:

```text
base
free
```

The three target collections support listing, creation, complete replacement, partial updates,
and deletion through HTTP.

### Existing test foundation

The repository contains reusable unit and integration test infrastructure for singleton sections,
target collections, complete-configuration validation, dependency injection, and persistence. The
current suite covers 132 behaviors.

## Completed collection lifecycle API

All three collection-based configuration sections now support their complete current lifecycle.

### Targets

Identity: `(symbol, kind)`

```text
GET    /optimization-configs/{mode}/targets
POST   /optimization-configs/{mode}/targets
PUT    /optimization-configs/{mode}/targets/{symbol}/{kind}
PATCH  /optimization-configs/{mode}/targets/{symbol}/{kind}
DELETE /optimization-configs/{mode}/targets/{symbol}/{kind}
```

### Expected-ways targets

Identity: `(symbol, kind)`

```text
GET    /optimization-configs/{mode}/expected-ways-targets
POST   /optimization-configs/{mode}/expected-ways-targets
PUT    /optimization-configs/{mode}/expected-ways-targets/{symbol}/{kind}
PATCH  /optimization-configs/{mode}/expected-ways-targets/{symbol}/{kind}
DELETE /optimization-configs/{mode}/expected-ways-targets/{symbol}/{kind}
```

### Group RTP targets

Identity: `name`

```text
GET    /optimization-configs/{mode}/group-rtp-targets
POST   /optimization-configs/{mode}/group-rtp-targets
PUT    /optimization-configs/{mode}/group-rtp-targets/{name}
PATCH  /optimization-configs/{mode}/group-rtp-targets/{name}
DELETE /optimization-configs/{mode}/group-rtp-targets/{name}
```

Expected HTTP behavior:

- `201 Created` after adding a resource;
- `200 OK` after replacing or patching a resource;
- `204 No Content` after deleting a resource;
- `404 Not Found` when the requested resource does not exist;
- `409 Conflict` when adding a resource with an existing identity;
- `422 Unprocessable Entity` when request data or the resulting configuration is invalid.

Resource identities are immutable during PUT and PATCH. Changing `symbol`, `kind`, or `name`
requires deleting the old resource and creating a new one.

## Roadmap

### Phase 1 — Complete configuration API

- [x] Implement collection lifecycle endpoints.
- [x] Add service-level not-found, duplicate-resource, and identity-mismatch errors.
- [x] Map domain errors to correct HTTP responses.
- Add aggregate validation across all configuration sections.
- [x] Finish tests for the currently implemented configuration API and schemas.

### Phase 2 — Persistent configuration

- [x] Define a configuration repository interface.
- [x] Keep the in-memory implementation for tests.
- [x] Implement JSON-backed persistence.
- [x] Load initial `base` and `free` configuration files.
- [x] Use atomic file replacement to prevent corrupted configuration files.
- Decide how configuration revisions and concurrent edits are handled.

### Phase 3 — Optimization business logic

- Define an optimization run model and lifecycle.
- Create run identifiers.
- Start and stop optimization runs.
- Track run status and progress.
- Generate and manage candidate configurations.
- Apply configured stopping conditions.
- Select the best candidate and retain its metrics.
- Expose run status and output APIs.

Possible lifecycle:

```text
pending -> running -> completed
                   -> failed
                   -> cancelled
```

### Phase 4 — MathEngine integration

- Define the protobuf contract.
- Generate Python gRPC clients and servers.
- Send candidate evaluations from Optimizer to MathEngine.
- Add deadlines, error mapping, retry policy, and health checks.
- Keep mathematical calculation out of the Optimizer service.

### Phase 5 — Delivery and deployment

- Add Docker images for each service.
- Add Docker Compose for local development.
- Add CI for Ruff and pytest.
- Add deployment automation for the Raspberry Pi.
- Configure Nginx as the external reverse proxy.
- Add TLS and HTTP/2; evaluate HTTP/3 when the REST services are stable.
- Add VPN access for remote administration of the Pi.
- Add logs, metrics, backups, and recovery procedures.

## Definition of done for the current phase

The configuration API phase is complete when:

- every existing JSON configuration section has an exact schema;
- BASE and FREE configurations can be read through HTTP;
- singleton sections can be patched;
- collection sections support GET, POST, PUT, PATCH, and DELETE;
- invalid combined configurations are rejected;
- API errors use consistent HTTP status codes;
- changes persist after a service restart;
- tests cover the finalized behavior;
- no configuration fields are invented outside the SDK contract.

## Important current limitations

- Reel-count-dependent constraint validation is not implemented.
- Configuration revisions and concurrent-edit protection are not implemented.
- Optimization execution is not implemented.
- MathEngine gRPC communication is not implemented.
- Output and progress APIs are not implemented.
- Authentication and authorization are not implemented.
- Nginx, Docker, CI/CD, and Raspberry Pi deployment are not configured yet.

## Next task

Define the optimization-run lifecycle and application service:

1. Create the run identity, status, timestamps, progress, and error models.
2. Define allowed state transitions such as pending, running, completed, failed, and cancelled.
3. Add an application service that starts and tracks runs without implementing mathematics.
4. Define the MathEngine gRPC contract required to evaluate one candidate.
5. Add run creation, status, cancellation, and result endpoints.
