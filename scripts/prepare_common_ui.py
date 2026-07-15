#!/usr/bin/env python3
"""현재 설치 JAR과 검수된 프로젝트 산출물에서 공통 UI 검수 초안을 만든다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile

from common_ui_catalog import GROUPS, TARGETS, Target
from local_paths import PROJECT_ROOT, resolve_source_root

WORK_ROOT = PROJECT_ROOT / "working/common_ui"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"


def load_json(archive: ZipFile, name: str) -> dict[str, object]:
    if name not in archive.namelist():
        return {}
    value = json.loads(archive.read(name).decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {name}")
    return value


def find_jar(instance: Path, target: Target) -> Path:
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
    instance: Path, target: Target, force: bool
) -> list[dict[str, object]]:
    jar_path = find_jar(instance, target)
    rows = []
    with ZipFile(jar_path) as jar:
        for namespace in target.namespaces:
            english_path = f"assets/{namespace}/lang/en_us.json"
            korean_path = f"assets/{namespace}/lang/ko_kr.json"
            english = load_json(jar, english_path)
            if target.key_prefixes:
                english = {
                    key: value
                    for key, value in english.items()
                    if key.startswith(target.key_prefixes)
                }
            if not english:
                raise FileNotFoundError(
                    f"영어 언어 파일이 없거나 비었습니다: {jar_path.name}:{english_path}"
                )
            jar_korean = load_json(jar, korean_path)
            project_path = OUTPUT_ASSETS / namespace / "lang/ko_kr.json"
            project_korean = (
                json.loads(project_path.read_text(encoding="utf-8"))
                if project_path.is_file()
                else {}
            )
            draft = {
                key: project_korean.get(key, jar_korean.get(key, value))
                for key, value in english.items()
            }
            output = WORK_ROOT / target.group / namespace / "ko_kr.json"
            if output.exists() and not force:
                raise FileExistsError(f"기존 검수 파일을 덮어쓰지 않습니다: {output}")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(draft, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            rows.append(
                {
                    "group": target.group,
                    "jar": jar_path.name,
                    "namespace": namespace,
                    "english_keys": len(english),
                    "project_output_candidates": len(
                        set(english) & set(project_korean)
                    ),
                    "jar_korean_candidates": len(
                        (set(english) - set(project_korean)) & set(jar_korean)
                    ),
                    "untranslated_draft": sum(
                        draft[key] == value for key, value in english.items()
                    ),
                }
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("group", choices=GROUPS + ("all",))
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    instance = resolve_source_root(args.instance)
    selected = [
        target
        for target in TARGETS
        if args.group == "all" or target.group == args.group
    ]
    rows = []
    for target in selected:
        rows.extend(prepare_target(instance, target, args.force))
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
