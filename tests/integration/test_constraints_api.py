from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.contracts.config_section_contract import ConfigSectionContract


class TestConstraintsAPI(ConfigSectionContract):
    @property
    def section_name(self) -> str:
        return "constraints"

    def expected_initial_body(self) -> dict[str, Any]:
        return {
            "last_allowed_reel": {"H4": 3, "H5": 2},
            "max_consecutive": {},
            "global_count_ranges": {},
            "composition_symbols": ["L1", "L2", "L3", "L4", "L5", "L6"],
        }

    def valid_patch_body(self) -> dict[str, Any]:
        return {
            "max_consecutive": {"H1": 2},
            "global_count_ranges": {"L1": [1, 10]},
        }

    def expected_patched_body(self) -> dict[str, Any]:
        return {
            "last_allowed_reel": {"H4": 3, "H5": 2},
            "max_consecutive": {"H1": 2},
            "global_count_ranges": {"L1": [1, 10]},
            "composition_symbols": ["L1", "L2", "L3", "L4", "L5", "L6"],
        }


@pytest.mark.parametrize(
    "payload",
    [
        {"last_allowed_reel": {"H4": 0}},
        {"max_consecutive": {"H1": 0}},
        {"global_count_ranges": {"L1": [-1, 10]}},
        {"global_count_ranges": {"L1": [10, 1]}},
        {"max_consecutive": None},
        {"unknown": 1},
    ],
)
def test_invalid_constraints_patch_is_rejected(
    client: TestClient,
    payload: dict[str, object],
) -> None:
    response = client.patch(
        "/optimization-configs/base/constraints",
        json=payload,
    )

    assert response.status_code == 422
