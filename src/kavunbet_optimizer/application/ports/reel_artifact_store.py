from typing import Protocol

from kavunbet_optimizer.domain.reel_artifact import StoredReelArtifact


class ReelArtifactStore(Protocol):
    def put(
        self,
        storage_key: str,
        csv_content: str,
    ) -> StoredReelArtifact: ...

    def get(
        self,
        storage_key: str,
    ) -> str: ...
