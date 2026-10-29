from typing import Any

from tests.contracts.target_collection_contract import TargetCollectionContract


class TestExpectedWaysTargetsAPI(TargetCollectionContract):
    @property
    def mode(self) -> str:
        return "base"

    @property
    def collection_name(self) -> str:
        return "expected-ways-targets"

    @property
    def item_identity(self) -> str:
        return "L1/5"

    @property
    def missing_item_identity(self) -> str:
        return "UNKNOWN/5"

    def expected_collection_size(self) -> int:
        return 2

    def expected_initial_item(self) -> dict[str, Any]:
        return {
            "symbol": "L1",
            "kind": 5,
            "min_ways": 2.15,
            "max_ways": 2.3,
            "weight": 16.0,
        }

    def valid_patch_body(self) -> dict[str, Any]:
        return {"min_ways": 2.2}

    def expected_patched_item(self) -> dict[str, Any]:
        return {
            "symbol": "L1",
            "kind": 5,
            "min_ways": 2.2,
            "max_ways": 2.3,
            "weight": 16.0,
        }

    def invalid_merged_patch_body(self) -> dict[str, Any]:
        return {"min_ways": 3}

    def new_item_body(self) -> dict[str, Any]:
        return {
            "symbol": "H3",
            "kind": 4,
            "min_ways": 1.0,
            "max_ways": 2.0,
            "weight": 3.0,
        }

    def replacement_body(self) -> dict[str, Any]:
        return {
            "symbol": "L1",
            "kind": 5,
            "min_ways": 1.5,
            "max_ways": 2.5,
            "weight": 8.0,
        }

    def missing_replacement_body(self) -> dict[str, Any]:
        return {
            "symbol": "UNKNOWN",
            "kind": 5,
            "min_ways": 1.5,
            "max_ways": 2.5,
            "weight": 8.0,
        }

    def identity_mismatch_body(self) -> dict[str, Any]:
        return {
            "symbol": "L2",
            "kind": 5,
            "min_ways": 1.5,
            "max_ways": 2.5,
            "weight": 8.0,
        }
