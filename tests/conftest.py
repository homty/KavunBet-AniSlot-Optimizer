"""Shared pytest fixtures."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from kavunbet_optimizer.api import optimization_configs
from kavunbet_optimizer.infrastructure.config_repository import (
    OptimizationConfigRepository,
)
from kavunbet_optimizer.main import app


# Fixtures can provide a configured environment or known test data.
# This fixture provides an isolated in-memory repository for each API test.
@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[TestClient]:
    repository = OptimizationConfigRepository()

    # Replace the global in-memory repository for this test.
    # Pytest restores the original object after the test finishes.
    monkeypatch.setattr(
        optimization_configs,
        "config_repository",
        repository,
    )

    with TestClient(app) as test_client:
        yield test_client
