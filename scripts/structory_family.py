#!/usr/bin/env python3
"""Structory와 Structory: Towers의 직접 표시 문구를 번역·검증해요."""

from __future__ import annotations

import argparse
import gzip
import json
import re
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from dungeons_arise_family import (
    VISIBLE_DATA_KEYS,
    VISIBLE_NBT_LIST_NAMES,
    VISIBLE_NBT_STRING_NAMES,
    component_literal_text,
    nbt_component_literal,
    replace_component_literal,
    scan_visible_nbt,
    walk_json,
)
from gateways_hellish_family import Tag, read_nbt, write_nbt
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import (
    active_output_root,
    output_deployment_path,
    resolve_active_output_path,
)

FAMILY = "structory"
WORK_ROOT = PROJECT_ROOT / "working/structory"
OVERRIDE_ROOT = active_output_root() / "overrides/kubejs"
JARS = {
    "structory": "Structory_[0-9]*.jar",
    "structory_towers": "Structory_Towers_*.jar",
}
DATA_TEXT = {
    "Splash Potion of Eternal Glowing": "투척용 영원한 발광의 물약",
    "Glowing (∞)": "발광 (∞)",
    "Potion of Heroism": "영웅심의 물약",
    "Splash Potion of Darkness": "투척용 어둠의 물약",
    "Potion of Bad Omen": "흉조의 물약",
}
NBT_TEXT = {
    "Bandit": "도적",
    "Outlander": "외지인",
    "Vagabond": "떠돌이",
}
EXPECTED_DECORATION_VALUES = {
    ".                    ",
    ".                   ",
    "I    r   e a",
    " e a",
}


def find_jar(label: str) -> Path:
    """현재 설치본에서 지정한 Structory JAR 하나를 찾아요."""
    matches = sorted((resolve_source_root() / "mods").glob(JARS[label]))
    if len(matches) != 1:
        raise FileNotFoundError(f"{label} JAR이 정확히 한 개가 아니에요: {matches}")
    return matches[0]


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없는 JSON을 안정된 형식으로 기록해요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def prepare() -> dict[str, object]:
    """두 JAR의 데이터 JSON·구조물 NBT 표시 원문을 전부 추출해요."""
    jar_reports = []
    errors = []
    for label in JARS:
        jar = find_jar(label)
        language_files = []
        data_json_files = []
        data_direct = []
        data_localized = []
        invalid_json = []
        nbt_files = []
        nbt_rows = []
        guide_entries = []
        with ZipFile(jar) as archive:
            for name in sorted(archive.namelist()):
                lower = name.lower()
                if "/lang/" in lower and lower.endswith(".json"):
                    language_files.append(name)
                if lower.endswith((".md", ".txt", ".json")) and any(
                    segment in lower
                    for segment in ("/book/", "/guide/", "/manual/", "patchouli")
                ):
                    guide_entries.append(name)
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
        current_errors = []
        if language_files:
            current_errors.append(f"예상하지 않은 언어 파일이 있어요: {language_files}")
        if invalid_json:
            current_errors.append(f"읽지 못한 데이터 JSON이 있어요: {invalid_json}")
        if guide_entries:
            current_errors.append(f"별도 가이드 후보가 있어요: {guide_entries}")
        errors.extend(f"{label}: {message}" for message in current_errors)
        jar_reports.append(
            {
                "label": label,
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
                "guide_candidates": guide_entries,
                "errors": current_errors,
            }
        )
    report = {
        "family": FAMILY,
        "jars": jar_reports,
        "errors": errors,
        "status": "prepared" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "source_surface_catalog.json", report)
    summary = {
        "family": FAMILY,
        "jars": [
            {
                "label": row["label"],
                "jar": row["jar"],
                "language_files": len(row["language_files"]),
                "data_json_files": row["data_json_files"],
                "data_direct_fields": len(row["data_direct_fields"]),
                "data_localized_fields": len(row["data_localized_fields"]),
                "nbt_files": row["nbt_files"],
                "nbt_visible_fields": len(row["nbt_visible_fields"]),
            }
            for row in jar_reports
        ],
        "errors": errors,
        "status": report["status"],
    }
    write_json(WORK_ROOT / "inventory.json", summary)
    return summary


def transform_data_value(value: object) -> tuple[object, int]:
    """검수한 Towers 직접 표시 필드만 번역해요."""
    count = 0

    def transform(child: object, parent_key: str | None = None) -> object:
        nonlocal count
        if isinstance(child, dict):
            return {key: transform(item, key) for key, item in child.items()}
        if isinstance(child, list):
            return [transform(item, parent_key) for item in child]
        if (
            isinstance(child, str)
            and parent_key in VISIBLE_DATA_KEYS
            and child in DATA_TEXT
        ):
            count += 1
            return DATA_TEXT[child]
        return child

    return transform(value), count


def translate_nbt_tag(tag: Tag, name: str | None = None) -> int:
    """Structory NBT의 몹 이름 세 개만 스타일을 보존해 번역해요."""
    count = 0
    if tag.kind == 8 and name in VISIBLE_NBT_STRING_NAMES:
        source = str(tag.value)
        literal = nbt_component_literal(source)
        if literal in NBT_TEXT:
            tag.value = replace_component_literal(source, NBT_TEXT[literal])
            return 1
    if tag.kind == 10:
        for child_name, child in tag.value.items():
            count += translate_nbt_tag(child, child_name)
    elif tag.kind == 9:
        child_kind, children = tag.value
        if child_kind == 8 and name in VISIBLE_NBT_LIST_NAMES:
            for child in children:
                source = str(child.value)
                literal = nbt_component_literal(source)
                if literal in NBT_TEXT:
                    child.value = replace_component_literal(source, NBT_TEXT[literal])
                    count += 1
        else:
            for child in children:
                count += translate_nbt_tag(child, name)
    return count


def build() -> dict[str, object]:
    """Towers 데이터 네 파일과 Structory NBT 세 파일을 번역해요."""
    catalog = json.loads(
        (WORK_ROOT / "source_surface_catalog.json").read_text(encoding="utf-8")
    )
    by_label = {row["label"]: row for row in catalog["jars"]}
    for label, row in by_label.items():
        jar = find_jar(label)
        if (
            row["jar"] != jar.name
            or row["jar_size"] != jar.stat().st_size
            or row["jar_mtime_ns"] != jar.stat().st_mtime_ns
        ):
            raise RuntimeError(f"{label} JAR이 원문 추출 당시와 달라요")
    data_sources = {
        row["literal"] for row in by_label["structory_towers"]["data_direct_fields"]
    }
    if data_sources != set(DATA_TEXT):
        raise KeyError(
            f"Towers 번역표가 달라요: missing={sorted(data_sources - set(DATA_TEXT))}, "
            f"extra={sorted(set(DATA_TEXT) - data_sources)}"
        )
    nbt_sources = {
        row["literal"]
        for row in by_label["structory"]["nbt_visible_fields"]
        if row["literal"] in NBT_TEXT
    }
    if nbt_sources != set(NBT_TEXT):
        raise KeyError(
            f"Structory 번역표가 달라요: missing={sorted(nbt_sources - set(NBT_TEXT))}, "
            f"extra={sorted(set(NBT_TEXT) - nbt_sources)}"
        )
    data_files = sorted(
        {row["file"] for row in by_label["structory_towers"]["data_direct_fields"]}
    )
    nbt_files = sorted(
        {
            row["file"]
            for row in by_label["structory"]["nbt_visible_fields"]
            if row["literal"] in NBT_TEXT
        }
    )
    data_reports = []
    with ZipFile(find_jar("structory_towers")) as archive:
        for internal in data_files:
            source = json.loads(archive.read(internal))
            target, replacements = transform_data_value(source)
            output = OVERRIDE_ROOT / internal
            write_json(output, target)
            data_reports.append(
                {
                    "source": internal,
                    "output": output.relative_to(PROJECT_ROOT).as_posix(),
                    "replacements": replacements,
                }
            )
    nbt_reports = []
    with ZipFile(find_jar("structory")) as archive:
        for internal in nbt_files:
            source_bytes = archive.read(internal)
            compressed = source_bytes.startswith(b"\x1f\x8b")
            raw = gzip.decompress(source_bytes) if compressed else source_bytes
            root_name, root = read_nbt(raw)
            replacements = translate_nbt_tag(root)
            target_raw = write_nbt(root_name, root)
            output = OVERRIDE_ROOT / internal
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(
                gzip.compress(target_raw, mtime=0) if compressed else target_raw
            )
            nbt_reports.append(
                {
                    "source": internal,
                    "output": output.relative_to(PROJECT_ROOT).as_posix(),
                    "replacements": replacements,
                }
            )
    write_json(WORK_ROOT / "translated_data_files.json", data_reports)
    write_json(WORK_ROOT / "translated_nbt_files.json", nbt_reports)
    data_count = sum(int(row["replacements"]) for row in data_reports)
    nbt_count = sum(int(row["replacements"]) for row in nbt_reports)
    errors = []
    if data_count != 5:
        errors.append(f"Towers 데이터 번역 수가 달라요: {data_count} != 5")
    if nbt_count != 3:
        errors.append(f"Structory NBT 번역 수가 달라요: {nbt_count} != 3")
    report = {
        "family": FAMILY,
        "language_keys": 0,
        "existing_korean_values_reused": 0,
        "new_direct_translations": data_count + nbt_count,
        "data_files": len(data_reports),
        "data_replacements": data_count,
        "nbt_files": len(nbt_reports),
        "nbt_replacements": nbt_count,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def audit_references() -> tuple[dict[str, object], list[str]]:
    """FTB Quests와 KubeJS에서 두 네임스페이스의 표시 후보를 확인해요."""
    instance = resolve_source_root()
    errors = []
    report: dict[str, object] = {"ftbquests": [], "kubejs": [], "read_errors": []}
    suffixes = {".cfg", ".js", ".json", ".snbt", ".toml", ".txt"}
    namespaces = {"structory", "structory_towers"}
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
                read_errors = report["read_errors"]
                if isinstance(read_errors, list):
                    read_errors.append(f"{path}: {exc}")
                continue
            lower = text.lower()
            counts = {
                namespace: lower.count(f"{namespace}:") for namespace in namespaces
            }
            if not any(counts.values()):
                continue
            visible_lines = []
            for number, line in enumerate(text.splitlines(), 1):
                if not any(f"{namespace}:" in line.lower() for namespace in namespaces):
                    continue
                if re.search(
                    r"(?i)(?:custom_name|displayname|display_name|lore|subtitle|title|tooltip)"
                    r"\s*[:=(]",
                    line,
                ):
                    visible_lines.append(number)
            row = {
                "path": path.relative_to(instance).as_posix(),
                "namespace_occurrences": counts,
                "visible_namespace_candidate_lines": visible_lines,
            }
            rows.append(row)
            if visible_lines:
                errors.append(f"{label}에 직접 표시 문구 후보가 있어요: {row}")
    read_errors = report["read_errors"]
    if isinstance(read_errors, list):
        errors.extend(str(message) for message in read_errors)
    return report, errors


def audit() -> tuple[dict[str, object], list[str]]:
    """현재 원문 목록과 별도 표시 경로를 감사해요."""
    errors = []
    catalog = json.loads(
        (WORK_ROOT / "source_surface_catalog.json").read_text(encoding="utf-8")
    )
    by_label = {row["label"]: row for row in catalog["jars"]}
    for label, row in by_label.items():
        jar = find_jar(label)
        if (
            row["jar"] != jar.name
            or row["jar_size"] != jar.stat().st_size
            or row["jar_mtime_ns"] != jar.stat().st_mtime_ns
        ):
            errors.append(f"{label} JAR이 원문 추출 당시와 달라요")
        if row["language_files"]:
            errors.append(f"{label}에 예상하지 않은 언어 파일이 있어요")
        if row["invalid_json"] or row["guide_candidates"]:
            errors.append(f"{label}의 데이터 또는 가이드 감사가 완료되지 않았어요")
    if by_label["structory"]["data_direct_fields"]:
        errors.append("Structory에 예상하지 않은 직접 데이터 문구가 있어요")
    if by_label["structory"]["data_localized_fields"]:
        errors.append("Structory에 예상하지 않은 번역 키 데이터가 있어요")
    if by_label["structory_towers"]["data_localized_fields"]:
        errors.append("Structory: Towers에 예상하지 않은 번역 키 데이터가 있어요")
    data_values = {
        row["literal"] for row in by_label["structory_towers"]["data_direct_fields"]
    }
    if data_values != set(DATA_TEXT):
        errors.append("Structory: Towers 직접 표시 문구 목록이 달라요")
    nbt_values = {row["literal"] for row in by_label["structory"]["nbt_visible_fields"]}
    expected_nbt = set(NBT_TEXT) | EXPECTED_DECORATION_VALUES
    if nbt_values != expected_nbt:
        errors.append(
            "Structory NBT 표시 문구 목록이 달라요: "
            f"missing={sorted(expected_nbt - nbt_values)}, "
            f"extra={sorted(nbt_values - expected_nbt)}"
        )
    references, reference_errors = audit_references()
    errors.extend(reference_errors)
    report = {
        "family": FAMILY,
        "language_work": "no_language_files",
        "data_direct_fields": len(by_label["structory_towers"]["data_direct_fields"]),
        "nbt_visible_fields": len(by_label["structory"]["nbt_visible_fields"]),
        "translated_nbt_fields": sum(
            row["literal"] in NBT_TEXT
            for row in by_label["structory"]["nbt_visible_fields"]
        ),
        "preserved_decoration_fields": sum(
            row["literal"] in EXPECTED_DECORATION_VALUES
            for row in by_label["structory"]["nbt_visible_fields"]
        ),
        "references": references,
        "ftbquests_display_work": (
            "no_related_references"
            if not references["ftbquests"]
            else "namespace_ids_only"
        ),
        "kubejs_display_work": (
            "no_related_references"
            if not references["kubejs"]
            else "namespace_ids_only"
        ),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def verify_data_outputs() -> tuple[dict[str, object], list[str]]:
    """네 데이터 JSON 산출물이 확정 변환값과 같은지 확인해요."""
    errors = []
    rows = json.loads(
        (WORK_ROOT / "translated_data_files.json").read_text(encoding="utf-8")
    )
    replacements = 0
    with ZipFile(find_jar("structory_towers")) as archive:
        for row in rows:
            source = json.loads(archive.read(row["source"]))
            expected, count = transform_data_value(source)
            try:
                output = json.loads(
                    resolve_active_output_path(row["output"]).read_text(
                        encoding="utf-8"
                    )
                )
            except (OSError, json.JSONDecodeError, UnicodeError) as exc:
                errors.append(f"데이터 산출물을 읽지 못했어요: {row['output']}: {exc}")
                continue
            if output != expected:
                errors.append(f"데이터 산출물이 확정 변환값과 달라요: {row['output']}")
            replacements += count
    if replacements != 5:
        errors.append(f"데이터 번역 수가 달라요: {replacements} != 5")
    report = {
        "files": len(rows),
        "replacements": replacements,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify_nbt_outputs() -> tuple[dict[str, object], list[str]]:
    """세 NBT 산출물의 표시 경로와 번역값을 다시 확인해요."""
    errors = []
    catalog = json.loads(
        (WORK_ROOT / "source_surface_catalog.json").read_text(encoding="utf-8")
    )
    structory = next(row for row in catalog["jars"] if row["label"] == "structory")
    rows = json.loads(
        (WORK_ROOT / "translated_nbt_files.json").read_text(encoding="utf-8")
    )
    expected_by_file: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in structory["nbt_visible_fields"]:
        expected_by_file[row["file"]].append(
            (row["path"], NBT_TEXT.get(row["literal"], row["literal"]))
        )
    expected_files = {
        row["file"]
        for row in structory["nbt_visible_fields"]
        if row["literal"] in NBT_TEXT
    }
    if {row["source"] for row in rows} != expected_files:
        errors.append("NBT 산출물 파일 목록이 달라요")
    translated = 0
    for row in rows:
        output_path = resolve_active_output_path(row["output"])
        try:
            value = output_path.read_bytes()
            raw = gzip.decompress(value) if value.startswith(b"\x1f\x8b") else value
            actual = [(item["path"], item["literal"]) for item in scan_visible_nbt(raw)]
        except (EOFError, OSError, UnicodeError, ValueError) as exc:
            errors.append(f"NBT 산출물을 읽지 못했어요: {row['output']}: {exc}")
            continue
        if actual != expected_by_file[row["source"]]:
            errors.append(f"NBT 표시 경로나 번역값이 달라요: {row['output']}")
        translated += int(row["replacements"])
    if translated != 3:
        errors.append(f"NBT 번역 수가 달라요: {translated} != 3")
    report = {
        "files": len(rows),
        "replacements": translated,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def deployment_paths() -> set[str]:
    """이 가족이 실제 인스턴스에 적용할 정확한 상대 경로를 반환해요."""
    paths = set()
    for manifest_name in ("translated_data_files.json", "translated_nbt_files.json"):
        path = WORK_ROOT / manifest_name
        if not path.is_file():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        paths.update(output_deployment_path(row["output"]) for row in rows)
    return paths


def verify() -> tuple[dict[str, object], list[str]]:
    """데이터·NBT·외부 표시 경로를 함께 검증해요."""
    data, data_errors = verify_data_outputs()
    nbt, nbt_errors = verify_nbt_outputs()
    surface, surface_errors = audit()
    errors = data_errors + nbt_errors + surface_errors
    expected_files = {path.removeprefix("kubejs/") for path in deployment_paths()}
    actual_files = {
        path.relative_to(OVERRIDE_ROOT).as_posix()
        for namespace in ("structory", "structory_towers")
        for path in (OVERRIDE_ROOT / f"data/{namespace}").rglob("*")
        if path.is_file()
    }
    if actual_files != expected_files:
        errors.append(
            "덮어쓰기 산출물 목록이 달라요: "
            f"missing={sorted(expected_files - actual_files)}, "
            f"extra={sorted(actual_files - expected_files)}"
        )
    report = {
        "family": FAMILY,
        "language_keys": 0,
        "data": data,
        "nbt": nbt,
        "surface_audit": surface["status"],
        "ftbquests": surface["ftbquests_display_work"],
        "kubejs": surface["kubejs_display_work"],
        "output_files": len(deployment_paths()),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = (
        json.loads(deployment_path.read_text(encoding="utf-8"))
        if deployment_path.is_file()
        else None
    )
    completion = {
        "family": FAMILY,
        "language_keys": 0,
        "existing_korean_values_reused": 0,
        "new_direct_translations": data["replacements"] + nbt["replacements"],
        "ftbquests_work": surface["ftbquests_display_work"],
        "kubejs_work": surface["kubejs_display_work"],
        "output_files": sorted(deployment_paths()),
        "deployment": deployment,
        "errors": errors,
        "status": (
            "complete"
            if not errors
            and (
                deployment is None or deployment.get("status") == "applied_and_verified"
            )
            else "incomplete"
        ),
    }
    write_json(WORK_ROOT / "family_completion.json", completion)
    return report, errors


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 매니페스트의 대상·백업·해시 결과를 작업 기록에 연결해요."""
    errors = []
    manifest_path = manifest_path.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 매니페스트 상태가 완료가 아니에요")
    if manifest.get("java_processes"):
        errors.append(
            f"적용 당시 Java 프로세스가 있었어요: {manifest['java_processes']}"
        )
    expected = deployment_paths()
    targets = manifest.get("targets", [])
    if not isinstance(targets, list) or not targets:
        errors.append("적용 대상 기록이 없어요")
        targets = []
    summaries = []
    for target in targets:
        records = {
            row.get("relative_path"): row
            for row in target.get("files", [])
            if isinstance(row, dict)
        }
        missing = sorted(expected - set(records))
        extra = sorted(set(records) - expected)
        if missing or extra:
            errors.append(f"적용 경로가 달라요: missing={missing}, extra={extra}")
        hash_errors = sorted(
            path
            for path in expected & set(records)
            if records[path].get("source_sha256") != records[path].get("after_sha256")
        )
        if hash_errors:
            errors.append(f"적용 후 해시가 달라요: {hash_errors}")
        if target.get("status") != "applied_and_verified":
            errors.append(
                f"대상 적용 상태가 완료가 아니에요: {target.get('target_root')}"
            )
        if target.get("unexpected_changes"):
            errors.append(f"예상 밖 적용 변경이 있어요: {target['unexpected_changes']}")
        summaries.append(
            {
                "target_type": target.get("target_type"),
                "target_root": target.get("target_root"),
                "changed_paths": target.get("changed_paths", []),
                "unexpected_changes": target.get("unexpected_changes", []),
                "hash_verified_paths": sorted(expected - set(hash_errors)),
            }
        )
    try:
        manifest_name = manifest_path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        manifest_name = str(manifest_path)
    report = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "backup_manifest": manifest_name,
        "expected_paths": sorted(expected),
        "targets": summaries,
        "errors": errors,
    }
    write_json(WORK_ROOT / "deployment_report.json", report)
    return report, errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "build", "audit", "verify", "record-deployment", "all"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare()
    elif args.command == "build":
        result = build()
    elif args.command == "audit":
        result, _ = audit()
    elif args.command == "verify":
        result, _ = verify()
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        result, _ = record_deployment(args.manifest)
    else:
        prepared = prepare()
        built = build()
        verification, verification_errors = verify()
        result = {
            "prepare": prepared,
            "build": built,
            "verify": verification,
            "status": "complete" if not verification_errors else "incomplete",
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return (
        0 if result["status"] in {"prepared", "complete", "applied_and_verified"} else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
