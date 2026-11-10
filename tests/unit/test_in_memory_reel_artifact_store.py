from hashlib import sha256

import pytest

from kavunbet_optimizer.application.exceptions import ReelArtifactErrors
from kavunbet_optimizer.infrastructure.in_memory_reel_artifact_store import (
    InMemoryReelArtifactStore,
)


def test_store_puts_and_retrieves_csv_content() -> None:
    store = InMemoryReelArtifactStore()
    csv_content = "H1,H2,H3\nL1,L2,L3\n"

    metadata = store.put("results/job-1/reels.csv", csv_content)

    assert store.get(metadata.storage_key) == csv_content
    assert metadata.sha256 == sha256(csv_content.encode("utf-8")).hexdigest()
    assert metadata.size_bytes == len(csv_content.encode("utf-8"))


def test_store_uses_utf8_byte_size() -> None:
    store = InMemoryReelArtifactStore()
    csv_content = "H1,€\n"

    metadata = store.put("results/job-1/unicode.csv", csv_content)

    assert metadata.size_bytes == len(csv_content.encode("utf-8"))
    assert metadata.size_bytes > len(csv_content)


def test_store_is_idempotent_for_identical_content() -> None:
    store = InMemoryReelArtifactStore()
    csv_content = "H1,H2\n"

    first = store.put("results/job-1/reels.csv", csv_content)
    second = store.put("results/job-1/reels.csv", csv_content)

    assert first == second
    assert first is not second


def test_store_rejects_different_content_for_existing_key() -> None:
    store = InMemoryReelArtifactStore()
    storage_key = "results/job-1/reels.csv"
    store.put(storage_key, "H1,H2\n")

    with pytest.raises(ReelArtifactErrors.ReelArtifactConflictError):
        store.put(storage_key, "L1,L2\n")


def test_store_raises_not_found_for_unknown_key() -> None:
    store = InMemoryReelArtifactStore()

    with pytest.raises(ReelArtifactErrors.ReelArtifactNotFoundError):
        store.get("missing/reels.csv")


@pytest.mark.parametrize("storage_key", ["", "   "])
def test_store_rejects_blank_storage_key(storage_key: str) -> None:
    store = InMemoryReelArtifactStore()

    with pytest.raises(ValueError, match="storage key cannot be blank"):
        store.put(storage_key, "H1,H2\n")


@pytest.mark.parametrize("csv_content", ["", "  \n"])
def test_store_rejects_blank_csv_content(csv_content: str) -> None:
    store = InMemoryReelArtifactStore()

    with pytest.raises(ValueError, match="CSV content cannot be blank"):
        store.put("results/job-1/reels.csv", csv_content)
