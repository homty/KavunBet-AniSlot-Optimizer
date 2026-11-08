from fastapi.testclient import TestClient


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
