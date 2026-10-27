from abc import ABC, abstractmethod
from typing import Any

from fastapi.testclient import TestClient


class ConfigSectionContract(ABC):
    @property
    @abstractmethod
    def section_name(self) -> str:
        """Return the URL section, such as optimization or objective."""

    @abstractmethod
    def expected_initial_body(self) -> dict[str, Any]:
        """Return the expected initial base-mode response."""

    @abstractmethod
    def valid_patch_body(self) -> dict[str, Any]:
        """Return a valid partial PATCH request."""

    @abstractmethod
    def expected_patched_body(self) -> dict[str, Any]:
        """Return the complete response expected after PATCH."""

    def section_url(self, mode: str = "base") -> str:
        return f"/optimization-configs/{mode}/{self.section_name}"

    def test_get_section(self, client: TestClient) -> None:
        response = client.get(self.section_url())

        assert response.status_code == 200
        assert response.json() == self.expected_initial_body()

    def test_patch_section(self, client: TestClient) -> None:
        response = client.patch(
            self.section_url(),
            json=self.valid_patch_body(),
        )

        assert response.status_code == 200
        assert response.json() == self.expected_patched_body()

    def test_patch_is_persisted(self, client: TestClient) -> None:
        patch_response = client.patch(
            self.section_url(),
            json=self.valid_patch_body(),
        )

        assert patch_response.status_code == 200

        get_response = client.get(self.section_url())

        assert get_response.status_code == 200
        assert get_response.json() == self.expected_patched_body()

    def test_patch_requires_body(self, client: TestClient) -> None:
        response = client.patch(self.section_url())

        assert response.status_code == 422

    def test_unknown_mode_is_rejected(
        self,
        client: TestClient,
    ) -> None:
        response = client.get(self.section_url(mode="unknown"))

        assert response.status_code == 422
