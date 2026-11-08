from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from kavunbet_optimizer.domain.optimization_job import JobStatus


def submit_job(
    client: TestClient,
    *,
    idempotency_key: str = "request-1",
    engine_id: str = "giantesses-math-engine",
):
    return client.post(
        "/optimization-jobs",
        headers={"Idempotency-Key": idempotency_key},
        json={
            "project_id": "giantesses-attack",
            "engine_id": engine_id,
            "game_mode": "base",
        },
    )


def test_submit_optimization_job_returns_accepted_job(client: TestClient) -> None:
    response = submit_job(client)

    assert response.status_code == 202
    body = response.json()
    assert body["project_id"] == "giantesses-attack"
    assert body["engine_id"] == "giantesses-math-engine"
    assert body["game_mode"] == "base"
    assert body["status"] == "queued"
    assert body["created_at"] == body["updated_at"]
    assert "id" in body
    assert "config_snapshot" not in body


def test_submit_optimization_job_requires_idempotency_key(client: TestClient) -> None:
    response = client.post(
        "/optimization-jobs",
        json={
            "project_id": "giantesses-attack",
            "engine_id": "giantesses-math-engine",
            "game_mode": "base",
        },
    )

    assert response.status_code == 422


def test_repeated_submission_returns_same_job(client: TestClient) -> None:
    first = submit_job(client)
    repeated = submit_job(client)

    assert first.status_code == 202
    assert repeated.status_code == 202
    assert repeated.json() == first.json()


def test_reused_key_for_different_request_returns_conflict(client: TestClient) -> None:
    first = submit_job(client, idempotency_key="same-request")
    conflicting = submit_job(
        client,
        idempotency_key="same-request",
        engine_id="another-engine",
    )

    assert first.status_code == 202
    assert conflicting.status_code == 409
    assert "same-request" in conflicting.json()["detail"]


def test_get_optimization_job_returns_submitted_job(
    client: TestClient,
) -> None:
    submitted = submit_job(client)
    submitted_body = submitted.json()

    response = client.get(f"/optimization-jobs/{submitted_body['id']}")

    assert response.status_code == 200
    assert response.json() == submitted_body


def test_get_optimization_job_returns_not_found(
    client: TestClient,
) -> None:
    unknown_id = uuid4()

    response = client.get(f"/optimization-jobs/{unknown_id}")

    assert response.status_code == 404
    assert str(unknown_id) in response.json()["detail"]


def test_get_optimization_job_rejects_invalid_uuid(
    client: TestClient,
) -> None:
    response = client.get("/optimization-jobs/not-a-uuid")

    assert response.status_code == 422


def test_request_cancellation_returns_accepted_updated_job(client: TestClient) -> None:
    submitted = submit_job(client).json()

    response = client.post(f"/optimization-jobs/{submitted['id']}/cancel")

    assert response.status_code == 202
    body = response.json()
    assert body["id"] == submitted["id"]
    assert body["status"] == "cancellation_requested"

    persisted = client.get(f"/optimization-jobs/{submitted['id']}")
    assert persisted.status_code == 200
    assert persisted.json() == body


def test_repeated_cancellation_request_returns_same_job(client: TestClient) -> None:
    submitted = submit_job(client).json()
    first = client.post(f"/optimization-jobs/{submitted['id']}/cancel")

    repeated = client.post(f"/optimization-jobs/{submitted['id']}/cancel")

    assert first.status_code == 202
    assert repeated.status_code == 202
    assert repeated.json() == first.json()


def test_request_cancellation_returns_not_found(client: TestClient) -> None:
    unknown_id = uuid4()

    response = client.post(f"/optimization-jobs/{unknown_id}/cancel")

    assert response.status_code == 404
    assert str(unknown_id) in response.json()["detail"]


def test_request_cancellation_rejects_invalid_uuid(client: TestClient) -> None:
    response = client.post("/optimization-jobs/not-a-uuid/cancel")

    assert response.status_code == 422


def test_request_cancellation_rejects_terminal_job(client: TestClient) -> None:
    submitted = submit_job(client).json()
    job_id = UUID(submitted["id"])
    repository = client.app.state.optimization_job_repository
    job = repository.get(job_id)
    repository.save(job.model_copy(update={"status": JobStatus.COMPLETED}))

    response = client.post(f"/optimization-jobs/{job_id}/cancel")

    assert response.status_code == 409
    assert JobStatus.COMPLETED.value in response.json()["detail"]
