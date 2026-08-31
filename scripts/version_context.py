"""ATM10 활성 버전, 버전별 작업 공간과 배포 호환 정보를 관리한다."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTEXT_PATH = PROJECT_ROOT / "version_context.json"
CONTEXT_KEYS = {
    "schema_version",
    "active_pack_version",
    "baseline_pack_version",
    "active_workspace",
}
RELEASE_KEYS = {
    "schema_version",
    "pack_version",
    "resourcepack_name",
    "validated_pack_version",
    "rebase_target_version",
    "status",
    "full_apply_allowed",
    "baseline_commit",
    "note",
}


def _read_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"버전 설정 파일이 없습니다: {path}")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"버전 설정의 최상위 값은 객체여야 합니다: {path}")
    return value


def _project_path(value: str, field: str) -> Path:
    path = (PROJECT_ROOT / value).resolve()
    try:
        path.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError(f"{field}는 프로젝트 내부 경로여야 합니다: {value}") from exc
    return path


def load_version_context() -> dict[str, Any]:
    context = _read_object(CONTEXT_PATH)
    unknown = sorted(set(context) - CONTEXT_KEYS)
    if unknown:
        raise ValueError(f"version_context.json에 알 수 없는 키가 있습니다: {unknown}")
    if context.get("schema_version") != 1:
        raise ValueError("지원하지 않는 version_context.json 스키마입니다.")
    for key in ("active_pack_version", "baseline_pack_version", "active_workspace"):
        if not isinstance(context.get(key), str) or not context[key].strip():
            raise ValueError(f"{key}는 비어 있지 않은 문자열이어야 합니다.")
    context["workspace_path"] = _project_path(
        context["active_workspace"], "active_workspace"
    )
    return context


def output_root(pack_version: str) -> Path:
    if not isinstance(pack_version, str) or not pack_version.strip():
        raise ValueError("ATM10 output 버전은 비어 있지 않은 문자열이어야 합니다.")
    return _project_path(f"output/{pack_version}", "output 버전")


def active_output_root() -> Path:
    return output_root(load_version_context()["active_pack_version"])


def output_relative_path(value: str | Path) -> Path:
    """구형·버전형 output 참조를 활성 output 내부 상대 경로로 정규화한다."""
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"output 참조는 안전한 상대 경로여야 합니다: {value}")
    parts = relative.parts
    if parts and parts[0] in {"resourcepack", "overrides"}:
        normalized = parts
    elif (
        len(parts) >= 2
        and parts[0] == "output"
        and parts[1]
        in {
            "resourcepack",
            "overrides",
        }
    ):
        normalized = parts[1:]
    elif (
        len(parts) >= 3
        and parts[0] == "output"
        and parts[2]
        in {
            "resourcepack",
            "overrides",
        }
    ):
        normalized = parts[2:]
    else:
        raise ValueError(f"알 수 없는 output 참조입니다: {value}")
    return Path(*normalized)


def resolve_active_output_path(value: str | Path) -> Path:
    """구형·버전형 output 참조를 현재 활성 버전의 실제 경로로 바꾼다."""
    return active_output_root() / output_relative_path(value)


def output_deployment_path(value: str | Path) -> str:
    """output 참조를 실제 인스턴스에 적용할 상대 경로로 바꾼다."""
    relative = output_relative_path(value)
    if relative.parts[0] == "resourcepack":
        return (Path("resourcepacks") / Path(*relative.parts[1:])).as_posix()
    return Path(*relative.parts[1:]).as_posix()


def load_output_release(pack_version: str | None = None) -> dict[str, Any]:
    selected_version = pack_version or load_version_context()["active_pack_version"]
    release_path = output_root(selected_version) / "release.json"
    release = _read_object(release_path)
    unknown = sorted(set(release) - RELEASE_KEYS)
    if unknown:
        raise ValueError(f"{release_path}에 알 수 없는 키가 있습니다: {unknown}")
    if release.get("schema_version") != 1:
        raise ValueError(f"지원하지 않는 {release_path} 스키마입니다.")
    if release.get("pack_version") != selected_version:
        raise ValueError(
            f"output 버전과 release.json이 다릅니다: {selected_version}, "
            f"{release.get('pack_version')}"
        )
    if not isinstance(release.get("full_apply_allowed"), bool):
        raise ValueError("full_apply_allowed는 true 또는 false여야 합니다.")
    return release


def active_workspace() -> Path:
    return load_version_context()["workspace_path"]


def active_manifest_dir() -> Path:
    return active_workspace() / "manifests"


def active_report_dir() -> Path:
    return active_workspace() / "reports"


def read_instance_version(root: Path) -> str:
    manifest = root / "manifest.json"
    if not manifest.is_file():
        raise FileNotFoundError(f"ATM10 manifest.json이 없습니다: {manifest}")
    value = _read_object(manifest)
    version = value.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"ATM10 버전을 읽을 수 없습니다: {manifest}")
    return version
