"""Shared pytest fixtures."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from kavunbet_optimizer.infrastructure.in_memory_config_repository import (
    InMemoryOptimizationConfigRepository,
)
from kavunbet_optimizer.main import create_app


# Fixtures can provide a configured environment or known test data.
# This fixture provides an isolated in-memory repository for each API test.
@pytest.fixture
def client() -> Iterator[TestClient]:
    repository = InMemoryOptimizationConfigRepository()

    # Inject a fresh in-memory repository into a fresh application for this test.
    # The production application uses the JSON-backed repository instead.
    app = create_app(repository)

    with TestClient(app) as test_client:
        yield test_client
