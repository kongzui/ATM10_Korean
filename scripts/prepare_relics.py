#!/usr/bin/env python3
"""현재 설치 JAR과 검수된 프로젝트 산출물에서 Relics 검수 초안을 만든다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from relics_catalog import BATCHES, TARGETS, Target

WORK_ROOT = PROJECT_ROOT / "working/relics"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"


def load_json(archive: ZipFile, name: str) -> dict[str, object]:
    """ZIP 내부 JSON 객체를 읽는다."""
    if name not in archive.namelist():
        return {}
    value = json.loads(archive.read(name).decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {name}")
    return value


def duplicate_keys(archive: ZipFile, name: str) -> set[str]:
    """원본 JSON에 존재하는 중복 키를 찾는다."""
    if name not in archive.namelist():
        return set()
    pairs = json.loads(
        archive.read(name).decode("utf-8-sig"), object_pairs_hook=lambda rows: rows
    )
    if not isinstance(pairs, list):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {name}")
    seen: set[str] = set()
    duplicates: set[str] = set()
    for key, _ in pairs:
        if key in seen:
            duplicates.add(key)
        seen.add(key)
    return duplicates


def find_jar(instance: Path, target: Target) -> Path:
    """파일명 접두사로 설치 JAR 하나를 확정한다."""
    matches = [
        path
        for path in (instance / "mods").glob("*.jar")
        if path.name.lower().startswith(target.jar_prefix.lower())
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"JAR을 하나로 확정할 수 없습니다: {target.jar_prefix} -> {matches}"
        )
    return matches[0]


def prepare_target(
    instance: Path,
    target: Target,
    force: bool,
) -> dict[str, object]:
    """한 네임스페이스의 영어 키 순서를 보존한 검수 초안을 만든다."""
    jar_path = find_jar(instance, target)
    english_path = f"assets/{target.namespace}/lang/en_us.json"
    korean_path = f"assets/{target.namespace}/lang/ko_kr.json"
    with ZipFile(jar_path) as jar:
        english = load_json(jar, english_path)
        jar_korean = load_json(jar, korean_path)
        english_duplicates = duplicate_keys(jar, english_path)
        korean_duplicates = duplicate_keys(jar, korean_path)
    if not english:
        raise FileNotFoundError(f"영어 언어 파일이 비었습니다: {jar_path.name}")
    if english_duplicates:
        raise ValueError(
            f"영어 표시 키에 중복이 있습니다: {jar_path.name}:{english_duplicates}"
        )
    project_path = OUTPUT_ASSETS / target.namespace / "lang/ko_kr.json"
    project_korean = (
        json.loads(project_path.read_text(encoding="utf-8"))
        if project_path.is_file()
        else {}
    )
    draft = {
        key: project_korean.get(key, jar_korean.get(key, value))
        for key, value in english.items()
    }
    output = WORK_ROOT / target.namespace / "ko_kr.json"
    if output.exists() and not force:
        raise FileExistsError(f"기존 검수 파일을 덮어쓰지 않습니다: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(draft, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "batch": target.batch,
        "jar": jar_path.name,
        "namespace": target.namespace,
        "english_keys": len(english),
        "project_output_candidates": len(set(english) & set(project_korean)),
        "jar_korean_candidates": len(
            (set(english) - set(project_korean)) & set(jar_korean)
        ),
        "english_fallbacks": sum(draft[key] == value for key, value in english.items()),
        "source_korean_duplicate_keys": sorted(korean_duplicates),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", choices=BATCHES + ("all",))
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    instance = resolve_source_root(args.instance)
    selected = [
        target
        for target in TARGETS
        if args.batch == "all" or target.batch == args.batch
    ]
    rows = [prepare_target(instance, target, args.force) for target in selected]
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
