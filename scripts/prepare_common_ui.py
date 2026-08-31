#!/usr/bin/env python3
"""현재 설치 JAR과 검수된 프로젝트 산출물에서 공통 UI 검수 초안을 만든다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile

from common_ui_catalog import (
    GROUPS,
    PACK_LANGUAGE_TARGETS,
    TARGETS,
    PackLanguageTarget,
    Target,
)
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root, active_pack_version

WORK_ROOT = PROJECT_ROOT / "working/common_ui"
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"


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


def load_recheck_values(
    group: str, namespace: str, english: dict[str, object]
) -> dict[str, object]:
    """현재 팩 버전에서 확정한 공통 UI 재검토 값을 읽는다."""
    version = active_pack_version().replace(".", "_")
    path = WORK_ROOT / group / namespace / f"recheck_{version}.json"
    if not path.is_file():
        return {}
    values = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(values, dict):
        raise TypeError(f"재검토 JSON 최상위 값이 객체가 아닙니다: {path}")
    unknown = sorted(set(values) - set(english))
    if unknown:
        raise KeyError(f"현재 영어 원문에 없는 재검토 키: {unknown}")
    return values


def load_allowed_source_equal_keys(
    group: str, namespace: str, english: dict[str, object]
) -> set[str] | None:
    """현재 버전에서 원문 유지가 필요한 고유명사·단위·명령 키를 읽는다."""
    version = active_pack_version().replace(".", "_")
    path = WORK_ROOT / group / namespace / f"allowed_source_equal_{version}.json"
    if not path.is_file():
        return None
    values = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(values, list) or not all(isinstance(key, str) for key in values):
        raise TypeError(f"원문 유지 허용 목록은 문자열 배열이어야 합니다: {path}")
    if len(values) != len(set(values)):
        raise ValueError(f"원문 유지 허용 목록에 중복 키가 있습니다: {path}")
    unknown = sorted(set(values) - set(english))
    if unknown:
        raise KeyError(f"현재 영어 원문에 없는 원문 유지 허용 키: {unknown}")
    return set(values)


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
            recheck_values = load_recheck_values(target.group, namespace, english)
            draft.update(recheck_values)
            allowed_source_equal = load_allowed_source_equal_keys(
                target.group, namespace, english
            )
            source_equal = {
                key for key, value in english.items() if draft[key] == value
            }
            untranslated = (
                source_equal - allowed_source_equal
                if allowed_source_equal is not None
                else source_equal
            )
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
                    "version_recheck_values": len(recheck_values),
                    "allowed_source_equal": len(allowed_source_equal or ()),
                    "untranslated_draft": len(untranslated),
                }
            )
    return rows


def prepare_pack_target(
    instance: Path, target: PackLanguageTarget, force: bool
) -> dict[str, object]:
    """팩의 KubeJS 언어 파일을 현재 원문에 맞춰 검수 초안으로 만든다."""
    source_dir = instance / target.relative_dir
    english_path = source_dir / "en_us.json"
    korean_path = source_dir / "ko_kr.json"
    english = json.loads(english_path.read_text(encoding="utf-8-sig"))
    jar_korean = (
        json.loads(korean_path.read_text(encoding="utf-8-sig"))
        if korean_path.is_file()
        else {}
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
    allowed_source_equal = load_allowed_source_equal_keys(
        target.group, target.namespace, english
    )
    source_equal = {key for key, value in english.items() if draft[key] == value}
    untranslated = (
        source_equal - allowed_source_equal
        if allowed_source_equal is not None
        else source_equal
    )
    output = WORK_ROOT / target.group / target.namespace / "ko_kr.json"
    if output.exists() and not force:
        raise FileExistsError(f"기존 검수 파일을 덮어쓰지 않습니다: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(draft, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "group": target.group,
        "source": target.relative_dir,
        "namespace": target.namespace,
        "english_keys": len(english),
        "project_output_candidates": len(set(english) & set(project_korean)),
        "pack_korean_candidates": len(
            (set(english) - set(project_korean)) & set(jar_korean)
        ),
        "allowed_source_equal": len(allowed_source_equal or ()),
        "untranslated_draft": len(untranslated),
    }


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
    pack_selected = [
        target
        for target in PACK_LANGUAGE_TARGETS
        if args.group == "all" or target.group == args.group
    ]
    for target in pack_selected:
        rows.append(prepare_pack_target(instance, target, args.force))
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
