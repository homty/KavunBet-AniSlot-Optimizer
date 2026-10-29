import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

from kavunbet_optimizer.infrastructure.in_memory_config_repository import (
    InMemoryOptimizationConfigRepository,
)
from kavunbet_optimizer.schemas.configuration import OptimizationConfig
from kavunbet_optimizer.schemas.optimization import GameMode


class JsonOptimizationConfigRepository(InMemoryOptimizationConfigRepository):
    """Configuration repository backed by separate BASE and FREE JSON files."""

    def __init__(self, config_directory: Path) -> None:
        self._config_paths = {
            GameMode.BASE: config_directory / "base_config.json",
            GameMode.FREE: config_directory / "free_config.json",
        }
        self._documents = {
            mode: self._read_document(path) for mode, path in self._config_paths.items()
        }
        configs = {mode: self._parse_config(document) for mode, document in self._documents.items()}
        super().__init__(configs)

    @staticmethod
    def _read_document(path: Path) -> dict[str, Any]:
        with path.open(encoding="utf-8") as config_file:
            document = json.load(config_file)

        if not isinstance(document, dict):
            raise TypeError(f"configuration root must be an object: {path}")

        return document

    @staticmethod
    def _parse_config(document: dict[str, Any]) -> OptimizationConfig:
        return OptimizationConfig.model_validate(
            {
                "symbols": document["symbols"],
                "optimization": document["optimization"],
                "objective": document["objective"],
                "targets": document.get("targets", []),
                "expected_ways_targets": document.get("expected_ways_targets", []),
                "group_rtp_targets": document.get("group_rtp_targets", []),
                "constraints": document.get("constraints", {}),
            }
        )

    def _after_change(self, mode: GameMode) -> None:
        document = deepcopy(self._documents[mode])
        config = self._configs[mode]

        document["symbols"] = config.symbols
        document["optimization"] = config.optimization.model_dump(mode="json")
        document["objective"] = config.objective.model_dump(mode="json")
        document["targets"] = [target.model_dump(mode="json") for target in config.targets]
        document["expected_ways_targets"] = [
            target.model_dump(mode="json") for target in config.expected_ways_targets
        ]
        if "group_rtp_targets" in document or config.group_rtp_targets:
            document["group_rtp_targets"] = [
                target.model_dump(mode="json") for target in config.group_rtp_targets
            ]
        document["constraints"] = config.constraints.model_dump(mode="json")

        self._atomic_write(self._config_paths[mode], document)
        self._documents[mode] = document

    @staticmethod
    def _atomic_write(path: Path, document: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
        )
        temporary_path = Path(temporary_name)

        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as config_file:
                json.dump(document, config_file, indent=2, ensure_ascii=False)
                config_file.write("\n")
                config_file.flush()
                os.fsync(config_file.fileno())

            os.replace(temporary_path, path)
        finally:
            temporary_path.unlink(missing_ok=True)
