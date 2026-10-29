from typing import Any

from tests.contracts.target_collection_contract import TargetCollectionContract


class TestGroupRtpTargetsAPI(TargetCollectionContract):
    @property
    def mode(self) -> str:
        return "free"

    @property
    def collection_name(self) -> str:
        return "group-rtp-targets"

    @property
    def item_identity(self) -> str:
        return "default"

    @property
    def missing_item_identity(self) -> str:
        return "unknown"

    def expected_collection_size(self) -> int:
        return 2

    def expected_initial_item(self) -> dict[str, Any]:
        return {
            "name": "default",
            "symbols": ["L1", "L2", "L3", "L4", "L5", "L6"],
            "min_natural_rtp_pct": 10.5,
            "max_natural_rtp_pct": 11.5,
            "weight": 8.0,
        }

    def valid_patch_body(self) -> dict[str, Any]:
        return {"max_natural_rtp_pct": 12}

    def expected_patched_item(self) -> dict[str, Any]:
        return {
            "name": "default",
            "symbols": ["L1", "L2", "L3", "L4", "L5", "L6"],
            "min_natural_rtp_pct": 10.5,
            "max_natural_rtp_pct": 12.0,
            "weight": 8.0,
        }

    def invalid_merged_patch_body(self) -> dict[str, Any]:
        return {"min_natural_rtp_pct": 12}

    def new_item_body(self) -> dict[str, Any]:
        return {
            "name": "middle",
            "symbols": ["H3", "L3"],
            "min_natural_rtp_pct": 2.0,
            "max_natural_rtp_pct": 3.0,
            "weight": 4.0,
        }

    def replacement_body(self) -> dict[str, Any]:
        return {
            "name": "default",
            "symbols": ["L1", "L2"],
            "min_natural_rtp_pct": 9.0,
            "max_natural_rtp_pct": 12.0,
            "weight": 4.0,
        }

    def missing_replacement_body(self) -> dict[str, Any]:
        return {
            "name": "unknown",
            "symbols": ["L1", "L2"],
            "min_natural_rtp_pct": 9.0,
            "max_natural_rtp_pct": 12.0,
            "weight": 4.0,
        }

    def identity_mismatch_body(self) -> dict[str, Any]:
        return {
            "name": "premium",
            "symbols": ["L1", "L2"],
            "min_natural_rtp_pct": 9.0,
            "max_natural_rtp_pct": 12.0,
            "weight": 4.0,
        }
