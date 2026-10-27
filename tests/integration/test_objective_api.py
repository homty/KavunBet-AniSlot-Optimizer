from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.contracts.config_section_contract import (
    ConfigSectionContract,
)


class TestObjectiveConfigAPI(ConfigSectionContract):
    @property
    def section_name(self) -> str:
        return "objective"

    def expected_initial_body(self) -> dict[str, Any]:
        return {
            "progression_weight": 1.0,
            "symbol_order_weight": 1.0,
            "preserve_untargeted_weight": 0.25,
            "preserve_untargeted_tolerance": 0.2,
            "preserve_untargeted_ways_weight": 4.0,
            "preserve_untargeted_ways_tolerance": 0.1,
            "frequency_orders": [
                ["H1", "H2", "H3", "H4", "H5"],
            ],
        }

    def valid_patch_body(self) -> dict[str, Any]:
        return {
            "progression_weight": 2.0,
            "frequency_orders": [
                ["L1", "L2"],
            ],
        }

    def expected_patched_body(self) -> dict[str, Any]:
        return {
            "progression_weight": 2.0,
            "symbol_order_weight": 1.0,
            "preserve_untargeted_weight": 0.25,
            "preserve_untargeted_tolerance": 0.2,
            "preserve_untargeted_ways_weight": 4.0,
            "preserve_untargeted_ways_tolerance": 0.1,
            "frequency_orders": [
                ["L1", "L2"],
            ],
        }


@pytest.mark.parametrize(
    "payload",
    [
        {"progression_weight": -1},
        {"preserve_untargeted_tolerance": 1},
        {"preserve_untargeted_ways_tolerance": 1},
        {"frequency_orders": [["H1"]]},
        {"frequency_orders": [["H1", "H1"]]},
        {"frequency_orders": None},
        {"unknown": 1},
    ],
)
def test_invalid_objective_patch_is_rejected(
    client: TestClient,
    payload: dict[str, object],
) -> None:
    response = client.patch(
        "/optimization-configs/base/objective",
        json=payload,
    )

    assert response.status_code == 422
