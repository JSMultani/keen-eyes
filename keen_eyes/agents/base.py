from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from keen_eyes.models import RequirementPlan
from keen_eyes.project_profile import ProjectProfile


class CodingAgent(ABC):
    @abstractmethod
    def execute(self, plan: RequirementPlan, project_path: Path, out_dir: Path, profile: ProjectProfile) -> list[dict[str, str]]:
        """Execute or verify a TDD coding workflow and return an audit trace."""
