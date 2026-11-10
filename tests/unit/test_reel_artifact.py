import pytest
from pydantic import ValidationError

from kavunbet_optimizer.domain.reel_artifact import StoredReelArtifact


def make_reel_artifact(**changes: object) -> StoredReelArtifact:
    values: dict[str, object] = {
        "storage_key": "projects/test/jobs/job/results/result/reels.csv",
        "sha256": "a" * 64,
        "size_bytes": 24,
    }
    values.update(changes)

    return StoredReelArtifact.model_validate(values)


def test_stored_reel_artifact_accepts_valid_metadata() -> None:
    artifact = make_reel_artifact()

    assert artifact.sha256 == "a" * 64
    assert artifact.size_bytes == 24


def test_stored_reel_artifact_is_immutable() -> None:
    artifact = make_reel_artifact()

    with pytest.raises(ValidationError, match="frozen"):
        artifact.size_bytes = 25


@pytest.mark.parametrize("storage_key", ["", "   "])
def test_stored_reel_artifact_rejects_blank_storage_key(storage_key: str) -> None:
    with pytest.raises(ValidationError, match="storage key cannot be blank|at least 1 character"):
        make_reel_artifact(storage_key=storage_key)


@pytest.mark.parametrize(
    "sha256",
    [
        "a" * 63,
        "a" * 65,
        "G" * 64,
    ],
)
def test_stored_reel_artifact_rejects_invalid_sha256(sha256: str) -> None:
    with pytest.raises(ValidationError) as error:
        make_reel_artifact(sha256=sha256)

    assert error.value.errors()[0]["type"] == "string_pattern_mismatch"


@pytest.mark.parametrize("size_bytes", [0, -1])
def test_stored_reel_artifact_requires_positive_size(size_bytes: int) -> None:
    with pytest.raises(ValidationError, match="greater than 0"):
        make_reel_artifact(size_bytes=size_bytes)


def test_stored_reel_artifact_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        make_reel_artifact(unknown_field="value")
