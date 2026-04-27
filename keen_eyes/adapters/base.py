from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from keen_eyes.models import NormalizedEvidence


class EvidenceAdapter(ABC):
    formats: set[str]

    def supports(self, artifact_format: str) -> bool:
        return artifact_format.lower() in self.formats

    @abstractmethod
    def parse(self, artifact_path: Path, source: str, category: str) -> list[NormalizedEvidence]:
        """Parse one raw artifact into normalized evidence records."""


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: list[EvidenceAdapter] = []

    def register(self, adapter: EvidenceAdapter) -> None:
        self._adapters.append(adapter)

    def parse(self, artifact_format: str, artifact_path: Path, source: str, category: str) -> list[NormalizedEvidence]:
        for adapter in self._adapters:
            if adapter.supports(artifact_format):
                return adapter.parse(artifact_path, source, category)
        raise ValueError(f"No evidence adapter registered for format {artifact_format}")

