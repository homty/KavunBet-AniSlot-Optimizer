from hashlib import sha256
from threading import RLock

from kavunbet_optimizer.application.exceptions import ReelArtifactErrors
from kavunbet_optimizer.domain.reel_artifact import StoredReelArtifact


class InMemoryReelArtifactStore:
    def __init__(self) -> None:
        self._contents: dict[str, bytes] = {}
        self._metadata: dict[str, StoredReelArtifact] = {}
        self._lock = RLock()

    def put(
        self,
        storage_key: str,
        csv_content: str,
    ) -> StoredReelArtifact:
        if not storage_key.strip():
            raise ValueError("storage key cannot be blank")
        if not csv_content.strip():
            raise ValueError("CSV content cannot be blank")

        encoded_content = csv_content.encode("utf-8")
        metadata = StoredReelArtifact(
            storage_key=storage_key,
            sha256=sha256(encoded_content).hexdigest(),
            size_bytes=len(encoded_content),
        )

        with self._lock:
            existing_content = self._contents.get(storage_key)
            if existing_content is not None:
                if existing_content != encoded_content:
                    raise ReelArtifactErrors.ReelArtifactConflictError(
                        f"storage key already contains different content: {storage_key}"
                    )

                return self._metadata[storage_key].model_copy(deep=True)

            self._contents[storage_key] = encoded_content
            self._metadata[storage_key] = metadata
            return metadata.model_copy(deep=True)

    def get(self, storage_key: str) -> str:
        with self._lock:
            content = self._contents.get(storage_key)
            if content is None:
                raise ReelArtifactErrors.ReelArtifactNotFoundError(
                    f"reel artifact not found: {storage_key}"
                )

            return content.decode("utf-8")
