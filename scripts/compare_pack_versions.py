#!/usr/bin/env python3
"""두 ATM10 인스턴스의 모드·언어·퀘스트·override 차이를 비교한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any

from ftbquests_layout import detect_layout, merged_locale_file, split_locale_files
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root, active_report_dir

LANG_RE = re.compile(r"^assets/([^/]+)/lang/(en_us|ko_kr)\.json$", re.IGNORECASE)
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"
OUTPUT_OVERRIDES = active_output_root() / "overrides"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def project_output(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError(f"보고서 경로는 프로젝트 안이어야 합니다: {resolved}") from exc
    return resolved


def pack_info(root: Path) -> dict[str, Any]:
    manifest = read_json_object(root / "manifest.json")
    minecraft = manifest.get("minecraft", {})
    loaders = minecraft.get("modLoaders", []) if isinstance(minecraft, dict) else []
    loader = (
        loaders[0].get("id", "") if loaders and isinstance(loaders[0], dict) else ""
    )
    return {
        "profile": root.name,
        "name": manifest.get("name", ""),
        "version": manifest.get("version", ""),
        "minecraft": minecraft.get("version", "")
        if isinstance(minecraft, dict)
        else "",
        "loader": loader,
        "manifest_projects": len(manifest.get("files", [])),
        "jar_files": len(list((root / "mods").glob("*.jar"))),
    }


def addon_inventory(root: Path) -> dict[str, dict[str, Any]]:
    metadata = read_json_object(root / "minecraftinstance.json")
    addons = metadata.get("installedAddons", [])
    result: dict[str, dict[str, Any]] = {}
    for addon in addons:
        if not isinstance(addon, dict):
            continue
        installed = addon.get("installedFile", {})
        if not isinstance(installed, dict):
            installed = {}
        addon_id = str(addon.get("addonID", ""))
        if not addon_id:
            continue
        result[addon_id] = {
            "addon_id": addon_id,
            "name": addon.get("name", ""),
            "file_id": installed.get("id"),
            "file": installed.get("fileName", ""),
        }
    return result


def compare_addons(
    base: dict[str, dict[str, Any]], target: dict[str, dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {
        "added": [],
        "removed": [],
        "updated": [],
        "unchanged": [],
    }
    for addon_id in sorted(set(base) | set(target), key=int):
        old = base.get(addon_id)
        new = target.get(addon_id)
        if old is None:
            state = "added"
        elif new is None:
            state = "removed"
        elif old["file_id"] != new["file_id"]:
            state = "updated"
        else:
            state = "unchanged"
        result[state].append(
            {
                "addon_id": addon_id,
                "name": (new or old or {}).get("name", ""),
                "base_file": old.get("file", "") if old else "",
                "target_file": new.get("file", "") if new else "",
            }
        )
    for rows in result.values():
        rows.sort(key=lambda row: str(row["name"]).lower())
    return result


def language_inventory(root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    entries: dict[str, list[dict[str, Any]]] = defaultdict(list)
    errors: list[str] = []
    for jar in sorted(
        (root / "mods").glob("*.jar"), key=lambda path: path.name.lower()
    ):
        try:
            with zipfile.ZipFile(jar) as archive:
                names = set(archive.namelist())
                for name in sorted(names):
                    match = LANG_RE.match(name)
                    if not match or match.group(2).lower() != "en_us":
                        continue
                    namespace = match.group(1).lower()
                    raw = archive.read(name)
                    try:
                        value = json.loads(raw.decode("utf-8-sig"))
                        keys = len(value) if isinstance(value, dict) else 0
                    except Exception as exc:
                        errors.append(f"{jar.name}:{name}: {type(exc).__name__}: {exc}")
                        keys = 0
                    ko_name = name[: -len("en_us.json")] + "ko_kr.json"
                    entries[namespace].append(
                        {
                            "jar": jar.name,
                            "path": name,
                            "sha256": sha256_bytes(raw),
                            "keys": keys,
                            "ko_exists": ko_name in names,
                        }
                    )
        except Exception as exc:
            errors.append(f"{jar.name}: {type(exc).__name__}: {exc}")

    result: dict[str, dict[str, Any]] = {}
    for namespace, rows in entries.items():
        rows.sort(key=lambda row: (str(row["jar"]).lower(), str(row["path"]).lower()))
        content_rows = sorted(f"{row['path']}|{row['sha256']}" for row in rows)
        combined = "\n".join(content_rows).encode("utf-8")
        result[namespace] = {
            "namespace": namespace,
            "sha256": sha256_bytes(combined),
            "english_keys": sum(int(row["keys"]) for row in rows),
            "korean_in_jar": all(bool(row["ko_exists"]) for row in rows),
            "sources": rows,
        }
    return result, errors


def output_namespaces() -> set[str]:
    if not OUTPUT_ASSETS.is_dir():
        return set()
    return {
        path.parent.parent.name.lower()
        for path in OUTPUT_ASSETS.glob("*/lang/ko_kr.json")
        if path.is_file()
    }


def compare_languages(
    base: dict[str, dict[str, Any]],
    target: dict[str, dict[str, Any]],
    translated: set[str],
) -> dict[str, Any]:
    states: dict[str, list[str]] = {
        "added": [],
        "removed": [],
        "changed": [],
        "unchanged": [],
    }
    for namespace in sorted(set(base) | set(target)):
        old = base.get(namespace)
        new = target.get(namespace)
        if old is None:
            state = "added"
        elif new is None:
            state = "removed"
        elif old["sha256"] != new["sha256"]:
            state = "changed"
        else:
            state = "unchanged"
        states[state].append(namespace)
    changed_translated = sorted(translated & set(states["changed"]))
    removed_translated = sorted(translated & set(states["removed"]))
    unchanged_translated = sorted(translated & set(states["unchanged"]))
    new_translation_candidates = sorted(
        namespace
        for namespace in states["added"]
        if int(target[namespace]["english_keys"]) > 0 and namespace not in translated
    )
    return {
        "states": states,
        "translated_output_namespaces": len(translated),
        "changed_translated_namespaces": changed_translated,
        "removed_translated_namespaces": removed_translated,
        "unchanged_translated_namespaces": unchanged_translated,
        "new_translation_candidates": new_translation_candidates,
    }


def ftb_inventory(root: Path) -> dict[str, Any]:
    en_merged = merged_locale_file(root, "en_us")
    ko_merged = merged_locale_file(root, "ko_kr")
    en_split = set(split_locale_files(root, "en_us"))
    ko_split = set(split_locale_files(root, "ko_kr"))
    chapters = root / "config/ftbquests/quests/chapters"
    return {
        "layout": detect_layout(root),
        "chapter_files": len(list(chapters.glob("*.snbt"))) if chapters.is_dir() else 0,
        "en_merged_exists": en_merged.is_file(),
        "ko_merged_exists": ko_merged.is_file(),
        "en_split_files": len(en_split),
        "ko_split_files": len(ko_split),
        "split_files_missing_in_ko": sorted(en_split - ko_split),
        "split_files_only_in_ko": sorted(ko_split - en_split),
    }


def override_inventory(target_root: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    if not OUTPUT_OVERRIDES.is_dir():
        return {"counts": {}, "files": rows}
    for source in sorted(OUTPUT_OVERRIDES.rglob("*"), key=lambda path: path.as_posix()):
        if not source.is_file() or source.name == ".gitkeep":
            continue
        relative = source.relative_to(OUTPUT_OVERRIDES).as_posix()
        target = target_root / relative
        if not target.is_file():
            state = "target_missing"
        elif sha256_file(source) == sha256_file(target):
            state = "same"
        else:
            state = "target_different"
        if relative.startswith("config/ftbquests/"):
            category = "ftbquests"
        elif relative.startswith("kubejs/"):
            category = "kubejs"
        else:
            category = "other"
        rows.append({"path": relative, "category": category, "state": state})
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[f"{row['category']}:{row['state']}"] += 1
        counts[f"all:{row['state']}"] += 1
    return {"counts": dict(sorted(counts.items())), "files": rows}


def markdown_report(report: dict[str, Any]) -> str:
    base = report["base"]
    target = report["target"]
    addons = report["addons"]
    languages = report["languages"]
    target_ftb = report["ftbquests"]["target"]
    overrides = report["overrides"]
    lines = [
        f"# ATM10 {base['version']} → {target['version']} 실제 파일 비교",
        "",
        "## 요약",
        "",
        f"- 비교한 프로젝트 산출물: `{report['output']['root']}`",
        f"- 모드 프로젝트: 추가 {len(addons['added'])}, 제거 {len(addons['removed'])}, "
        f"업데이트 {len(addons['updated'])}, 동일 {len(addons['unchanged'])}",
        f"- JAR: {base['jar_files']} → {target['jar_files']}",
        f"- 영어 네임스페이스: {report['language_counts']['base']} → "
        f"{report['language_counts']['target']}",
        f"- 기존 출력 중 영어 원문 변경 네임스페이스: "
        f"{len(languages['changed_translated_namespaces'])}",
        f"- 새 번역 후보 네임스페이스: {len(languages['new_translation_candidates'])}",
        f"- 8.1 FTB Quests 언어 구조: {target_ftb['layout']}",
        "",
        "## 추가된 모드",
        "",
    ]
    lines.extend(f"- {row['name']}" for row in addons["added"])
    lines.extend(["", "## 제거된 모드", ""])
    lines.extend(f"- {row['name']}" for row in addons["removed"])
    lines.extend(["", "## 먼저 재검수할 기존 번역 네임스페이스", ""])
    lines.extend(
        f"- `{namespace}`" for namespace in languages["changed_translated_namespaces"]
    )
    lines.extend(["", "## 새 번역 후보 네임스페이스", ""])
    lines.extend(
        f"- `{namespace}`" for namespace in languages["new_translation_candidates"]
    )
    lines.extend(
        [
            "",
            "## FTB Quests 구조 변경",
            "",
            f"- 영어 분할 파일: {target_ftb['en_split_files']}",
            f"- 한국어 분할 파일: {target_ftb['ko_split_files']}",
            f"- 한국어에 없는 영어 파일: {len(target_ftb['split_files_missing_in_ko'])}",
            f"- 영어에 없는 한국어 파일: {len(target_ftb['split_files_only_in_ko'])}",
            "",
            "## 기존 override와 8.1 원본 충돌",
            "",
            f"- 8.1 원본과 다른 파일: {overrides['counts'].get('all:target_different', 0)}",
            f"- 8.1에 같은 경로가 없는 파일: "
            f"{overrides['counts'].get('all:target_missing', 0)}",
            f"- 8.1 원본과 같은 파일: {overrides['counts'].get('all:same', 0)}",
            "",
            "전체 목록과 파일명은 같은 디렉터리의 JSON 보고서를 확인한다.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-instance", type=Path, required=True)
    parser.add_argument("--target-instance", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=active_report_dir() / "pack_comparison.json",
    )
    args = parser.parse_args()

    base_root = args.base_instance.resolve()
    target_root = resolve_source_root(args.target_instance)
    for root in (base_root, target_root):
        for required in (
            "manifest.json",
            "minecraftinstance.json",
            "mods",
            "config",
            "kubejs",
        ):
            if not (root / required).exists():
                parser.error(f"비교에 필요한 경로가 없습니다: {root / required}")

    base_languages, base_errors = language_inventory(base_root)
    target_languages, target_errors = language_inventory(target_root)
    addons = compare_addons(addon_inventory(base_root), addon_inventory(target_root))
    report = {
        "schema_version": 1,
        "output": {
            "root": active_output_root().relative_to(PROJECT_ROOT).as_posix(),
            "pack_version": active_output_root().name,
        },
        "base": pack_info(base_root),
        "target": pack_info(target_root),
        "addons": addons,
        "language_counts": {
            "base": len(base_languages),
            "target": len(target_languages),
        },
        "languages": compare_languages(
            base_languages,
            target_languages,
            output_namespaces(),
        ),
        "ftbquests": {
            "base": ftb_inventory(base_root),
            "target": ftb_inventory(target_root),
        },
        "overrides": override_inventory(target_root),
        "errors": {
            "base_language_scan": base_errors,
            "target_language_scan": target_errors,
        },
    }
    output = project_output(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    markdown = output.with_suffix(".md")
    markdown.write_text(markdown_report(report), encoding="utf-8")
    print(
        json.dumps({"json": str(output), "markdown": str(markdown)}, ensure_ascii=False)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
