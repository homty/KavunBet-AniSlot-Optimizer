from abc import ABC, abstractmethod
from typing import Any

from fastapi.testclient import TestClient


class TargetCollectionContract(ABC):
    @property
    @abstractmethod
    def mode(self) -> str:
        """Return the game mode used by the collection tests."""

    @property
    @abstractmethod
    def collection_name(self) -> str:
        """Return the collection URL section."""

    @property
    @abstractmethod
    def item_identity(self) -> str:
        """Return the path segments that identify an existing item."""

    @property
    @abstractmethod
    def missing_item_identity(self) -> str:
        """Return path segments that do not identify an existing item."""

    @abstractmethod
    def expected_collection_size(self) -> int:
        """Return the number of default items in this mode."""

    @abstractmethod
    def expected_initial_item(self) -> dict[str, Any]:
        """Return an item expected in the initial collection."""

    @abstractmethod
    def valid_patch_body(self) -> dict[str, Any]:
        """Return a valid partial update."""

    @abstractmethod
    def expected_patched_item(self) -> dict[str, Any]:
        """Return the complete item expected after the update."""

    @abstractmethod
    def invalid_merged_patch_body(self) -> dict[str, Any]:
        """Return a patch that becomes invalid after merging with stored data."""

    @abstractmethod
    def new_item_body(self) -> dict[str, Any]:
        """Return a complete resource with a new identity."""

    @abstractmethod
    def replacement_body(self) -> dict[str, Any]:
        """Return a complete replacement with the existing identity."""

    @abstractmethod
    def missing_replacement_body(self) -> dict[str, Any]:
        """Return a complete replacement matching the missing URL identity."""

    @abstractmethod
    def identity_mismatch_body(self) -> dict[str, Any]:
        """Return a complete resource whose identity differs from the URL."""

    def collection_url(self, mode: str | None = None) -> str:
        selected_mode = mode or self.mode
        return f"/optimization-configs/{selected_mode}/{self.collection_name}"

    def item_url(self, identity: str | None = None) -> str:
        selected_identity = identity or self.item_identity
        return f"{self.collection_url()}/{selected_identity}"

    def test_get_collection(self, client: TestClient) -> None:
        response = client.get(self.collection_url())

        assert response.status_code == 200
        assert len(response.json()) == self.expected_collection_size()
        assert self.expected_initial_item() in response.json()

    def test_patch_item(self, client: TestClient) -> None:
        response = client.patch(
            self.item_url(),
            json=self.valid_patch_body(),
        )

        assert response.status_code == 200
        assert response.json() == self.expected_patched_item()

    def test_add_item(self, client: TestClient) -> None:
        response = client.post(
            self.collection_url(),
            json=self.new_item_body(),
        )

        assert response.status_code == 201
        assert response.json() == self.new_item_body()

        get_response = client.get(self.collection_url())

        assert get_response.status_code == 200
        assert self.new_item_body() in get_response.json()

    def test_add_duplicate_item_returns_conflict(self, client: TestClient) -> None:
        response = client.post(
            self.collection_url(),
            json=self.expected_initial_item(),
        )

        assert response.status_code == 409

    def test_replace_item(self, client: TestClient) -> None:
        response = client.put(
            self.item_url(),
            json=self.replacement_body(),
        )

        assert response.status_code == 200
        assert response.json() == self.replacement_body()

        get_response = client.get(self.collection_url())

        assert get_response.status_code == 200
        assert self.replacement_body() in get_response.json()
        assert self.expected_initial_item() not in get_response.json()

    def test_replace_missing_item_returns_not_found(self, client: TestClient) -> None:
        response = client.put(
            self.item_url(self.missing_item_identity),
            json=self.missing_replacement_body(),
        )

        assert response.status_code == 404

    def test_replace_identity_mismatch_returns_conflict(self, client: TestClient) -> None:
        response = client.put(
            self.item_url(),
            json=self.identity_mismatch_body(),
        )

        assert response.status_code == 409

    def test_delete_item(self, client: TestClient) -> None:
        response = client.delete(self.item_url())

        assert response.status_code == 204
        assert response.content == b""

        get_response = client.get(self.collection_url())

        assert get_response.status_code == 200
        assert self.expected_initial_item() not in get_response.json()

    def test_delete_missing_item_returns_not_found(self, client: TestClient) -> None:
        response = client.delete(self.item_url(self.missing_item_identity))

        assert response.status_code == 404

    def test_patch_is_persisted(self, client: TestClient) -> None:
        patch_response = client.patch(
            self.item_url(),
            json=self.valid_patch_body(),
        )

        assert patch_response.status_code == 200

        get_response = client.get(self.collection_url())

        assert get_response.status_code == 200
        assert self.expected_patched_item() in get_response.json()

    def test_invalid_merged_patch_is_rejected(self, client: TestClient) -> None:
        response = client.patch(
            self.item_url(),
            json=self.invalid_merged_patch_body(),
        )

        assert response.status_code == 422

    def test_missing_item_returns_not_found(self, client: TestClient) -> None:
        response = client.patch(
            self.item_url(self.missing_item_identity),
            json=self.valid_patch_body(),
        )

        assert response.status_code == 404

    def test_unknown_mode_is_rejected(self, client: TestClient) -> None:
        response = client.get(self.collection_url(mode="unknown"))

        assert response.status_code == 422
