from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from kavunbet_optimizer.api import optimization_configs
from kavunbet_optimizer.infrastructure.config_repository import OptimizationConfigRepository
from kavunbet_optimizer.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    repository = OptimizationConfigRepository()
    monkeypatch.setattr(optimization_configs, "config_repository", repository)

    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_optimization_config(client: TestClient) -> None:
    response = client.get("/optimization-configs/base/optimization")

    assert response.status_code == 200

    body = response.json()

    assert body["iterations"] == 50_000
    assert body["seed"] == 42
    assert body["moves"] == {
        "within_reel": 0.55,
        "cross_reel": 0.45,
        "composition": 0.0,
    }


def test_get_free_optimization_settings(client: TestClient) -> None:
    response = client.get("/optimization-configs/free/optimization")

    assert response.status_code == 200

    body = response.json()

    assert body["iterations"] == 50_000
    assert body["moves"] == {
        "within_reel": 0.15,
        "cross_reel": 0.1,
        "composition": 0.75,
    }


def test_unknown_game_mode_is_rejected(client: TestClient) -> None:
    response = client.get("/optimization-configs/unknown/optimization")

    assert response.status_code == 422


def test_patching_optimization_settings(client: TestClient) -> None:
    response = client.patch(
        "/optimization-configs/base/optimization",
        json={
            "iterations": 5_000,
            "moves": {
                "composition": 0.75,
            },
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["iterations"] == 5_000
    assert body["seed"] == 42
    assert body["moves"] == {
        "within_reel": 0.55,
        "cross_reel": 0.45,
        "composition": 0.75,
    }

    stored = client.get("/optimization-configs/base/optimization")

    assert stored.status_code == 200
    assert stored.json() == body


def test_patch_requires_request_body(client: TestClient) -> None:
    response = client.patch("/optimization-configs/base/optimization")

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {"iterations": 0},
        {"moves": {"within_reel": 0, "cross_reel": 0, "composition": 0}},
        {"moves": {"within_reel": None}},
        {"unknown": 1},
    ],
)
def test_invalid_patch_is_rejected(client: TestClient, payload: dict[str, object]) -> None:
    response = client.patch(
        "/optimization-configs/base/optimization",
        json=payload,
    )

    assert response.status_code == 422


def test_patch_rejects_unknown_game_mode(client: TestClient) -> None:
    response = client.patch(
        "/optimization-configs/unknown/optimization",
        json={"iterations": 5_000},
    )

    assert response.status_code == 422
