from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ArtifactDeclaration:
    name: str
    path: str
    format: str
    category: str
    required: bool = True
    control_objectives: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProjectProfile:
    project_type: str
    test_command: str | None = None
    security_test_command: str | None = None
    benchmark_command: str | None = None
    scanner_commands: dict[str, str] = field(default_factory=dict)
    artifacts: list[ArtifactDeclaration] = field(default_factory=list)

    @classmethod
    def load(cls, project_path: Path) -> "ProjectProfile":
        project_path = project_path.resolve()
        for name in (".keen-eyes.yaml", ".keen-eyes.yml"):
            path = project_path / name
            if path.exists():
                return cls.from_mapping(_parse_small_yaml(path.read_text(encoding="utf-8")))
        json_path = project_path / ".keen-eyes.json"
        if json_path.exists():
            return cls.from_mapping(json.loads(json_path.read_text(encoding="utf-8")))
        return cls.infer(project_path)

    @classmethod
    def from_mapping(cls, data: dict[str, object]) -> "ProjectProfile":
        commands = data.get("commands", {})
        if not isinstance(commands, dict):
            commands = {}
        scanners = data.get("scanners", {})
        if not isinstance(scanners, dict):
            scanners = {}
        return cls(
            project_type=str(data.get("project_type", "custom")),
            test_command=_as_str(commands.get("test") or data.get("test_command")),
            security_test_command=_as_str(commands.get("security_test") or data.get("security_test_command")),
            benchmark_command=_as_str(commands.get("benchmark") or data.get("benchmark_command")),
            scanner_commands={str(key): str(value) for key, value in scanners.items()},
            artifacts=_artifact_declarations(data.get("artifacts", [])),
        )

    @classmethod
    def infer(cls, project_path: Path) -> "ProjectProfile":
        if (project_path / "package.json").exists():
            package = json.loads((project_path / "package.json").read_text(encoding="utf-8"))
            scripts = package.get("scripts", {}) if isinstance(package, dict) else {}
            return cls(
                project_type="node",
                test_command="npm test" if "test" in scripts else None,
                security_test_command="npm run test:security" if "test:security" in scripts else None,
                benchmark_command="npm run benchmark" if "benchmark" in scripts else None,
            )
        if (project_path / "go.mod").exists():
            return cls(project_type="go", test_command="go test ./...")
        if (project_path / "Cargo.toml").exists():
            return cls(project_type="rust", test_command="cargo test")
        if (project_path / "pom.xml").exists():
            return cls(project_type="java-maven", test_command="mvn test")
        if (project_path / "gradlew").exists() or (project_path / "build.gradle").exists():
            return cls(project_type="java-gradle", test_command="./gradlew test")
        if list(project_path.glob("*.csproj")) or list(project_path.glob("*.sln")):
            return cls(project_type="dotnet", test_command="dotnet test")
        if (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
            requirements = (project_path / "requirements.txt").read_text(encoding="utf-8", errors="ignore") if (project_path / "requirements.txt").exists() else ""
            uses_pytest = (project_path / "tests" / "conftest.py").exists() or "pytest" in requirements
            security_dir = project_path / "tests" / "security"
            return cls(
                project_type="python",
                test_command="python -m pytest" if uses_pytest else "python -m unittest discover -s tests -p test_*.py",
                security_test_command="python -m pytest tests/security" if uses_pytest and security_dir.exists() else (
                    "python -m unittest discover -s tests/security" if security_dir.exists() else None
                ),
            )
        if (project_path / "docker-compose.yml").exists() or (project_path / "compose.yaml").exists():
            return cls(project_type="container", test_command=None)
        return cls(project_type="custom")


def _as_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_small_yaml(text: str) -> dict[str, object]:
    data: dict[str, object] = {}
    current: str | None = None
    current_list_item: dict[str, object] | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith(" ") and ":" in raw:
            key, value = raw.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                data[key] = _unquote(value)
                current = None
            else:
                data[key] = {}
                current = key
            current_list_item = None
            continue
        if current and raw.startswith("  - "):
            items = data.setdefault(current, [])
            if not isinstance(items, list):
                items = []
                data[current] = items
            current_list_item = {}
            items.append(current_list_item)
            rest = raw.strip()[2:].strip()
            if ":" in rest:
                key, value = rest.split(":", 1)
                current_list_item[key.strip()] = _unquote(value.strip())
            continue
        if current_list_item is not None and raw.startswith("    ") and ":" in raw:
            key, value = raw.split(":", 1)
            current_list_item[key.strip()] = _unquote(value.strip())
            continue
        if current and raw.startswith("  ") and ":" in raw:
            key, value = raw.split(":", 1)
            nested = data.setdefault(current, {})
            if isinstance(nested, dict):
                nested[key.strip()] = _unquote(value.strip())
    return data


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _artifact_declarations(value: object) -> list[ArtifactDeclaration]:
    declarations: list[ArtifactDeclaration] = []
    if not isinstance(value, list):
        return declarations
    for item in value:
        if not isinstance(item, dict):
            continue
        controls = item.get("control_objectives", item.get("controls", []))
        if isinstance(controls, str):
            controls = [part.strip() for part in controls.split(",") if part.strip()]
        if not isinstance(controls, list):
            controls = []
        declarations.append(
            ArtifactDeclaration(
                name=str(item.get("name", item.get("path", "artifact"))),
                path=str(item.get("path", "")),
                format=str(item.get("format", "text")).lower(),
                category=str(item.get("category", "artifact")),
                required=str(item.get("required", "true")).lower() != "false",
                control_objectives=[str(control) for control in controls],
            )
        )
    return declarations
