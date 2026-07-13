"""기기별 ATM10 원본 조회 및 번역 적용 경로를 불러온다."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "local_paths.json"
PATH_KEYS = ("source_root", "game_root")


def load_local_paths() -> dict[str, Path | None]:
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(
            f"로컬 경로 설정이 없습니다: {CONFIG_PATH} "
            "(local_paths.example.json을 복사해 작성하세요.)"
        )

    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict):
        raise ValueError("local_paths.json의 최상위 값은 객체여야 합니다.")

    unknown = sorted(set(raw) - set(PATH_KEYS))
    if unknown:
        raise ValueError(f"local_paths.json에 알 수 없는 키가 있습니다: {unknown}")

    paths: dict[str, Path | None] = {}
    for key in PATH_KEYS:
        value = raw.get(key)
        if value is None:
            paths[key] = None
            continue
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key}는 절대 경로 문자열 또는 null이어야 합니다.")
        path = Path(value)
        if not path.is_absolute():
            raise ValueError(f"{key}는 절대 경로여야 합니다: {value}")
        paths[key] = path.resolve()
    return paths


def resolve_source_root(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    paths = load_local_paths()
    source = paths["source_root"] or paths["game_root"]
    if source is None:
        raise ValueError("원본 조회에 사용할 source_root 또는 game_root가 필요합니다.")
    return source


def resolve_apply_roots(explicit: Path | None = None) -> list[tuple[str, Path]]:
    if explicit is not None:
        return [("instance", explicit.resolve())]

    paths = load_local_paths()
    roots: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for key in PATH_KEYS:
        path = paths[key]
        if path is not None and path not in seen:
            roots.append((key, path))
            seen.add(path)
    if not roots:
        raise ValueError("번역을 적용할 source_root 또는 game_root가 필요합니다.")
    return roots
