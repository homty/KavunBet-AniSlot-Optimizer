from typing import Any

from fastapi.testclient import TestClient

from tests.contracts.target_collection_contract import TargetCollectionContract


class TestTargetsAPI(TargetCollectionContract):
    @property
    def mode(self) -> str:
        return "base"

    @property
    def collection_name(self) -> str:
        return "targets"

    @property
    def item_identity(self) -> str:
        return "H1/3"

    @property
    def missing_item_identity(self) -> str:
        return "UNKNOWN/3"

    def expected_collection_size(self) -> int:
        return 6

    def expected_initial_item(self) -> dict[str, Any]:
        return {
            "symbol": "H1",
            "kind": 3,
            "min_interval": 25.0,
            "max_interval": 35.0,
            "weight": 4.0,
        }

    def valid_patch_body(self) -> dict[str, Any]:
        return {"min_interval": 30}

    def expected_patched_item(self) -> dict[str, Any]:
        return {
            "symbol": "H1",
            "kind": 3,
            "min_interval": 30.0,
            "max_interval": 35.0,
            "weight": 4.0,
        }

    def invalid_merged_patch_body(self) -> dict[str, Any]:
        return {"min_interval": 40}

    def new_item_body(self) -> dict[str, Any]:
        return {
            "symbol": "H4",
            "kind": 4,
            "min_interval": 20.0,
            "max_interval": 30.0,
            "weight": 2.0,
        }

    def replacement_body(self) -> dict[str, Any]:
        return {
            "symbol": "H1",
            "kind": 3,
            "min_interval": 20.0,
            "max_interval": 40.0,
            "weight": 2.0,
        }

    def missing_replacement_body(self) -> dict[str, Any]:
        return {
            "symbol": "UNKNOWN",
            "kind": 3,
            "min_interval": 20.0,
            "max_interval": 40.0,
            "weight": 2.0,
        }

    def identity_mismatch_body(self) -> dict[str, Any]:
        return {
            "symbol": "H2",
            "kind": 3,
            "min_interval": 20.0,
            "max_interval": 40.0,
            "weight": 2.0,
        }


def test_invalid_target_kind_is_rejected(client: TestClient) -> None:
    response = client.patch(
        "/optimization-configs/base/targets/H1/2",
        json={"weight": 2},
    )

    assert response.status_code == 422


def test_target_with_unknown_symbol_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/optimization-configs/base/targets",
        json={
            "symbol": "UNKNOWN",
            "kind": 3,
            "min_interval": 1,
            "max_interval": 2,
            "weight": 1,
        },
    )

    assert response.status_code == 422

    collection_response = client.get("/optimization-configs/base/targets")
    assert all(target["symbol"] != "UNKNOWN" for target in collection_response.json())
