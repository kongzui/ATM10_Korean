#!/usr/bin/env python3
"""Dungeon Crawl의 번역 가능한 표시 표면이 없는지 전수 감사해요."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

from dungeons_arise_family import (
    VISIBLE_DATA_KEYS,
    component_literal_text,
    scan_visible_nbt,
    walk_json,
)
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

FAMILY = "dungeon_crawl"
NAMESPACE = "dungeoncrawl"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
JAR_PATTERN = "DungeonCrawl-NeoForge-*.jar"
MOD_METADATA = "META-INF/neoforge.mods.toml"
EXPECTED_METADATA = {
    "modId": "dungeoncrawl",
    "displayName": "Dungeon Crawl",
    "credits": "Original Mod by Greymerk (Roguelike Dungeons)",
    "authors": "xiroc",
    "description": "Dungeon Crawl, a spiritual successor to Roguelike Dungeons.",
}


def find_jar() -> Path:
    """현재 설치본에서 Dungeon Crawl JAR 하나를 찾아요."""
    matches = sorted((resolve_source_root() / "mods").glob(JAR_PATTERN))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Dungeon Crawl JAR이 정확히 한 개가 아니에요: {matches}"
        )
    return matches[0]


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없는 JSON을 안정된 형식으로 기록해요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_json(path: Path) -> object:
    """UTF-8 JSON 파일을 읽어요."""
    return json.loads(path.read_text(encoding="utf-8"))


def parse_metadata(text: str) -> dict[str, str]:
    """현재 JAR의 고정 모드 메타데이터 표시값을 읽어요."""
    result = {}
    for key in ("modId", "displayName", "credits", "authors"):
        match = re.search(rf'(?m)^{key}="([^"]*)"$', text)
        if match:
            result[key] = match.group(1)
    description = re.search(r"(?s)^description='''(.*?)'''$", text, re.MULTILINE)
    if description:
        result["description"] = description.group(1).strip()
    return result


def prepare() -> dict[str, object]:
    """JAR의 언어·데이터·NBT·가이드·메타데이터 표면을 전부 추출해요."""
    jar = find_jar()
    language_files = []
    data_json_files = []
    data_direct = []
    data_localized = []
    invalid_json = []
    nbt_files = []
    nbt_rows = []
    guide_candidates = []
    metadata = {}
    metadata_sha256 = None
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            lower = name.lower()
            if "/lang/" in lower and lower.endswith(".json"):
                language_files.append(name)
            if lower.endswith((".md", ".txt", ".json")) and any(
                part in lower for part in ("/book/", "/guide/", "/manual/", "patchouli")
            ):
                guide_candidates.append(name)
            if name == MOD_METADATA:
                raw_metadata = archive.read(name)
                metadata_sha256 = hashlib.sha256(raw_metadata).hexdigest()
                metadata = parse_metadata(raw_metadata.decode("utf-8"))
            if lower.startswith("data/") and lower.endswith(".json"):
                data_json_files.append(name)
                try:
                    value = json.loads(archive.read(name))
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    invalid_json.append(f"{name}: {exc}")
                    continue
                for key, path, child in walk_json(value):
                    if key not in VISIBLE_DATA_KEYS:
                        continue
                    row = {"file": name, "path": path, "value": child}
                    if isinstance(child, dict) and isinstance(
                        child.get("translate"), str
                    ):
                        data_localized.append(row)
                    else:
                        literal = component_literal_text(child)
                        if literal and literal.strip():
                            data_direct.append({**row, "literal": literal})
            if not lower.endswith(".nbt"):
                continue
            nbt_files.append(name)
            value = archive.read(name)
            try:
                raw = gzip.decompress(value)
            except gzip.BadGzipFile:
                raw = value
            for row in scan_visible_nbt(raw):
                nbt_rows.append({"file": name, **row})
    errors = []
    if language_files:
        errors.append(f"예상하지 않은 언어 파일이 있어요: {language_files}")
    if invalid_json:
        errors.append(f"읽지 못한 데이터 JSON이 있어요: {invalid_json}")
    if guide_candidates:
        errors.append(f"별도 가이드 후보가 있어요: {guide_candidates}")
    if metadata != EXPECTED_METADATA:
        errors.append(
            "모드 메타데이터가 예상과 달라요: "
            f"actual={metadata}, expected={EXPECTED_METADATA}"
        )
    report = {
        "family": FAMILY,
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_mtime_ns": jar.stat().st_mtime_ns,
        "language_files": language_files,
        "data_json_files": len(data_json_files),
        "data_direct_fields": data_direct,
        "data_localized_fields": data_localized,
        "invalid_json": invalid_json,
        "nbt_files": len(nbt_files),
        "nbt_visible_fields": nbt_rows,
        "guide_candidates": guide_candidates,
        "mod_metadata_file": MOD_METADATA,
        "mod_metadata_sha256": metadata_sha256,
        "mod_metadata": metadata,
        "errors": errors,
        "status": "prepared" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "source_surface_catalog.json", report)
    summary = {
        "family": FAMILY,
        "jar": jar.name,
        "language_files": len(language_files),
        "data_json_files": len(data_json_files),
        "data_direct_fields": len(data_direct),
        "data_localized_fields": len(data_localized),
        "nbt_files": len(nbt_files),
        "nbt_visible_fields": len(nbt_rows),
        "guide_candidates": len(guide_candidates),
        "metadata_surface": "jar_metadata_not_resourcepack_localizable",
        "errors": errors,
        "status": report["status"],
    }
    write_json(WORK_ROOT / "inventory.json", summary)
    return summary


def assert_current_jar(catalog: dict[str, object]) -> None:
    """원문 추출 뒤 JAR이 바뀌지 않았는지 확인해요."""
    jar = find_jar()
    if (
        catalog.get("jar") != jar.name
        or catalog.get("jar_size") != jar.stat().st_size
        or catalog.get("jar_mtime_ns") != jar.stat().st_mtime_ns
    ):
        raise RuntimeError("Dungeon Crawl JAR이 원문 추출 당시와 달라요")


def audit_references() -> tuple[dict[str, object], list[str]]:
    """FTB Quests와 KubeJS의 관련 참조 및 직접 표시 후보를 확인해요."""
    instance = resolve_source_root()
    errors = []
    report: dict[str, object] = {"ftbquests": [], "kubejs": [], "read_errors": []}
    suffixes = {".cfg", ".js", ".json", ".snbt", ".toml", ".txt"}
    for label, base in (
        ("ftbquests", instance / "config/ftbquests/quests"),
        ("kubejs", instance / "kubejs"),
    ):
        rows = report[label]
        if not isinstance(rows, list) or not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                report["read_errors"].append(f"{path}: {exc}")
                continue
            count = text.lower().count(f"{NAMESPACE}:")
            if not count:
                continue
            visible_lines = []
            for number, line in enumerate(text.splitlines(), 1):
                if f"{NAMESPACE}:" not in line.lower():
                    continue
                if re.search(
                    r"(?i)(?:custom_name|displayname|display_name|lore|subtitle|title|tooltip)"
                    r"\s*[:=(]",
                    line,
                ):
                    visible_lines.append(number)
            row = {
                "path": path.relative_to(instance).as_posix(),
                "namespace_occurrences": count,
                "visible_namespace_candidate_lines": visible_lines,
            }
            rows.append(row)
            if visible_lines:
                errors.append(f"{label}에 직접 표시 문구 후보가 있어요: {row}")
    errors.extend(str(message) for message in report["read_errors"])
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """번역 가능한 표시 표면이 없고 산출물도 만들지 않았는지 검증해요."""
    catalog = load_json(WORK_ROOT / "source_surface_catalog.json")
    if not isinstance(catalog, dict):
        return {"status": "incomplete"}, ["원문 목록이 객체가 아니에요"]
    errors = []
    try:
        assert_current_jar(catalog)
    except RuntimeError as exc:
        errors.append(str(exc))
    for key in (
        "language_files",
        "data_direct_fields",
        "data_localized_fields",
        "invalid_json",
        "nbt_visible_fields",
        "guide_candidates",
    ):
        if catalog.get(key):
            errors.append(f"{key}가 비어 있지 않아요")
    if catalog.get("data_json_files") != 174:
        errors.append(
            f"데이터 JSON 수가 달라요: {catalog.get('data_json_files')} != 174"
        )
    if catalog.get("nbt_files") != 115:
        errors.append(f"NBT 파일 수가 달라요: {catalog.get('nbt_files')} != 115")
    if catalog.get("mod_metadata") != EXPECTED_METADATA:
        errors.append("모드 메타데이터가 현재 검수값과 달라요")
    output_paths = [
        active_output_root()
        / "resourcepack/ATM10_Korean/assets/dungeoncrawl/lang/ko_kr.json",
        active_output_root() / "overrides/kubejs/data/dungeoncrawl",
    ]
    unexpected_outputs = [
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in output_paths
        if path.exists()
    ]
    if unexpected_outputs:
        errors.append(f"만들지 말아야 할 번역 산출물이 있어요: {unexpected_outputs}")
    references, reference_errors = audit_references()
    errors.extend(reference_errors)
    report = {
        "family": FAMILY,
        "reviewed_language_keys": 0,
        "bundled_korean_candidate_keys": 0,
        "existing_korean_values_reused": 0,
        "new_translations": 0,
        "data_json_files_audited": catalog.get("data_json_files"),
        "nbt_files_audited": catalog.get("nbt_files"),
        "localizable_visible_fields": 0,
        "metadata_surface": {
            "classification": "jar_metadata_not_resourcepack_localizable",
            "official_name_preserved": EXPECTED_METADATA["displayName"],
            "english_description": EXPECTED_METADATA["description"],
        },
        "ftbquests_work": (
            "no_related_references"
            if not references["ftbquests"]
            else "namespace_ids_only"
        ),
        "kubejs_work": (
            "no_related_references"
            if not references["kubejs"]
            else "namespace_ids_only"
        ),
        "references": references,
        "output_files": [],
        "deployment": "not_applicable_no_outputs",
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    write_json(WORK_ROOT / "family_validation.json", report)
    completion = {
        **report,
        "completion_kind": "audit_only_no_localizable_surface",
    }
    write_json(WORK_ROOT / "family_completion.json", completion)
    return report, errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "verify"))
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare()
    else:
        result, _ = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"prepared", "complete"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
