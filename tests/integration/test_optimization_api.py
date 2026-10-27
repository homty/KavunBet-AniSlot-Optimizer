from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.contracts.config_section_contract import (
    ConfigSectionContract,
)


class TestOptimizationConfigAPI(ConfigSectionContract):
    @property
    def section_name(self) -> str:
        return "optimization"

    def expected_initial_body(self) -> dict[str, Any]:
        return {
            "iterations": 50_000,
            "seed": 42,
            "start_temperature": 0.2,
            "end_temperature": 0.0001,
            "report_every": 5_000,
            "moves": {
                "within_reel": 0.55,
                "cross_reel": 0.45,
                "composition": 0.0,
            },
        }

    def valid_patch_body(self) -> dict[str, Any]:
        return {
            "iterations": 5_000,
            "moves": {
                "composition": 0.75,
            },
        }

    def expected_patched_body(self) -> dict[str, Any]:
        return {
            "iterations": 5_000,
            "seed": 42,
            "start_temperature": 0.2,
            "end_temperature": 0.0001,
            "report_every": 5_000,
            "moves": {
                "within_reel": 0.55,
                "cross_reel": 0.45,
                "composition": 0.75,
            },
        }


@pytest.mark.parametrize(
    "payload",
    [
        {"iterations": 0},
        {"moves": {"within_reel": 0, "cross_reel": 0, "composition": 0}},
        {"moves": {"within_reel": None}},
        {"moves": None},
        {"unknown": 1},
    ],
)
def test_invalid_optimization_patch_is_rejected(
    client: TestClient,
    payload: dict[str, object],
) -> None:
    response = client.patch(
        "/optimization-configs/base/optimization",
        json=payload,
    )

    assert response.status_code == 422
