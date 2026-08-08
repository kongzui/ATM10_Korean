#!/usr/bin/env python3
"""Chipped와 Rechiseled Chipped의 전체 표시 이름을 번역·검증해요."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

from dungeons_arise_family import (
    VISIBLE_DATA_KEYS,
    component_literal_text,
    scan_visible_nbt,
    walk_json,
)
from local_paths import PROJECT_ROOT, resolve_source_root

FAMILY = "chipped"
MOD_ID = "chipped"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
RESOURCE_OUTPUT = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/chipped/lang/ko_kr.json"
)
DEPLOYMENT_PATH = "resourcepacks/ATM10_Korean/assets/chipped/lang/ko_kr.json"
JARS = {
    "chipped": ("chipped-neoforge-*.jar", "chipped"),
    "rechiseled_chipped": ("rechiseled_chipped-*.jar", "rechiseled_chipped"),
}
LANGUAGE_PATH = "assets/chipped/lang/en_us.json"
RUSSIAN_CANDIDATE = "kubejs/assets/chipped/lang/ru_ru.json"
MODIFIER_TERMS = WORK_ROOT / "modifier_terms_ko.json"
BLOCK_EXCEPTIONS = WORK_ROOT / "block_exceptions_ko.json"
NONBLOCK_TRANSLATIONS = WORK_ROOT / "nonblock_ko.json"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[./xX×+]\d+)*")
MISSING_BASE_TRANSLATIONS = {
    "borderless_bricks": "테두리 없는 벽돌",
    "special_lantern": "특수 랜턴",
    "special_soul_lantern": "특수 영혼 랜턴",
    "waxed_exposed_copper_block": "밀랍칠한 노출된 구리",
}


def find_jar(label: str) -> Path:
    """현재 설치본에서 지정한 JAR 하나를 찾아요."""
    pattern = JARS[label][0]
    matches = sorted((resolve_source_root() / "mods").glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"{label} JAR이 정확히 한 개가 아니에요: {matches}")
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


def read_language(label: str, locale: str) -> dict[str, str]:
    """현재 JAR의 지정 언어 파일을 읽어요."""
    namespace = JARS[label][1]
    internal = f"assets/{namespace}/lang/{locale}.json"
    with ZipFile(find_jar(label)) as archive:
        try:
            value = json.loads(archive.read(internal))
        except KeyError:
            return {}
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise TypeError(f"언어 파일 형식이 올바르지 않아요: {internal}")
    return value


def minecraft_assets() -> tuple[Path, dict[str, str], dict[str, object]]:
    """현재 Minecraft 1.21.1의 공식 한국어 언어 자산을 읽어요."""
    instance = resolve_source_root()
    install = instance.parent.parent / "Install"
    version_path = install / "versions/1.21.1/1.21.1.json"
    version = load_json(version_path)
    if not isinstance(version, dict) or version.get("assets") != "17":
        raise RuntimeError("Minecraft 1.21.1 자산 인덱스가 예상한 17이 아니에요")
    asset_index = version.get("assetIndex")
    if not isinstance(asset_index, dict):
        raise RuntimeError("Minecraft 1.21.1 자산 인덱스 정보가 없어요")
    index_path = install / "assets/indexes" / f"{asset_index['id']}.json"
    index = load_json(index_path)
    if not isinstance(index, dict):
        raise TypeError("Minecraft 자산 인덱스가 객체가 아니에요")
    row = index.get("objects", {}).get("minecraft/lang/ko_kr.json")
    if not isinstance(row, dict) or not isinstance(row.get("hash"), str):
        raise RuntimeError("Minecraft 공식 ko_kr.json 자산을 찾지 못했어요")
    digest = row["hash"]
    language_path = install / "assets/objects" / digest[:2] / digest
    language = load_json(language_path)
    if not isinstance(language, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in language.items()
    ):
        raise TypeError("Minecraft 공식 ko_kr.json 형식이 올바르지 않아요")
    metadata = {
        "version_json": version_path.as_posix(),
        "asset_index_id": asset_index["id"],
        "asset_index_sha1": asset_index["sha1"],
        "language_object_hash": digest,
        "language_object_size": language_path.stat().st_size,
    }
    return language_path, language, metadata


def base_slugs(english: dict[str, str]) -> list[str]:
    """Chipped 태그 키에 정의된 276개 기본 재료 ID를 반환해요."""
    return [
        key.removeprefix("tag.item.chipped.")
        for key in english
        if key.startswith("tag.item.chipped.")
    ]


def official_base_translations(
    english: dict[str, str], official: dict[str, str]
) -> tuple[dict[str, str], dict[str, str]]:
    """기본 재료명을 현재 Minecraft 공식 한국어 키와 연결해요."""
    translations = {}
    official_keys = {}
    for slug in base_slugs(english):
        candidates = (f"block.minecraft.{slug}", f"item.minecraft.{slug}")
        key = next((value for value in candidates if value in official), None)
        if key is not None:
            translations[slug] = official[key]
            official_keys[slug] = key
        elif slug in MISSING_BASE_TRANSLATIONS:
            translations[slug] = MISSING_BASE_TRANSLATIONS[slug]
            official_keys[slug] = "project_reviewed_missing_official_key"
        else:
            raise KeyError(f"공식 한국어 기본 재료명을 찾지 못했어요: {slug}")
    return translations, official_keys


def parse_block_slug(
    slug: str, known_bases: list[str]
) -> tuple[str, list[str], list[str]] | None:
    """블록 ID를 앞 수식어·기본 재료·뒤 수식어로 분해해요."""
    tokens = slug.split("_")
    matches = []
    for base in known_bases:
        base_tokens = base.split("_")
        for index in range(len(tokens) - len(base_tokens) + 1):
            if tokens[index : index + len(base_tokens)] == base_tokens:
                matches.append((len(base_tokens), len(base), base, index))
    if not matches:
        return None
    _, _, base, index = max(matches)
    base_length = len(base.split("_"))
    return base, tokens[:index], tokens[index + base_length :]


def collect_surface(label: str) -> dict[str, object]:
    """지정한 JAR의 데이터·NBT·가이드 표시 표면을 전수 추출해요."""
    jar = find_jar(label)
    language_files = []
    data_json_files = []
    data_direct = []
    data_localized = []
    invalid_json = []
    nbt_files = []
    nbt_rows = []
    guide_candidates = []
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            lower = name.lower()
            if "/lang/" in lower and lower.endswith(".json"):
                language_files.append(name)
            if lower.endswith((".md", ".txt", ".json")) and any(
                part in lower for part in ("/book/", "/guide/", "/manual/", "patchouli")
            ):
                guide_candidates.append(name)
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
    return {
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
        "guide_candidates": guide_candidates,
    }


def prepare() -> dict[str, object]:
    """영어 7,265키와 공식 재료명·조합 구조·표시 표면을 기록해요."""
    english = read_language("chipped", "en_us")
    integration_english = read_language("rechiseled_chipped", "en_us")
    language_path, official, asset_metadata = minecraft_assets()
    bases, official_keys = official_base_translations(english, official)
    known_bases = base_slugs(english)
    modifier_counts = Counter()
    unmatched = {}
    parsed_blocks = 0
    for key, source in english.items():
        if not key.startswith("block.chipped."):
            continue
        slug = key.removeprefix("block.chipped.")
        parsed = parse_block_slug(slug, known_bases)
        if parsed is None:
            unmatched[key] = source
            continue
        _, prefix, suffix = parsed
        modifier_counts.update(prefix)
        modifier_counts.update(suffix)
        parsed_blocks += 1
    surfaces = [collect_surface(label) for label in JARS]
    errors = []
    expected_languages = {
        "chipped": ["assets/chipped/lang/en_us.json"],
        "rechiseled_chipped": ["assets/rechiseled_chipped/lang/en_us.json"],
    }
    for row in surfaces:
        if row["language_files"] != expected_languages[row["label"]]:
            errors.append(
                f"{row['label']} 언어 파일 목록이 달라요: {row['language_files']}"
            )
        if row["invalid_json"] or row["guide_candidates"]:
            errors.append(f"{row['label']} 데이터 또는 가이드 감사를 완료하지 못했어요")
    instance = resolve_source_root()
    candidate_path = instance / RUSSIAN_CANDIDATE
    russian = load_json(candidate_path) if candidate_path.is_file() else {}
    write_json(WORK_ROOT / "en_us.json", english)
    write_json(WORK_ROOT / "rechiseled_chipped_en_us.json", integration_english)
    write_json(WORK_ROOT / "official_base_ko.json", bases)
    write_json(WORK_ROOT / "official_base_keys.json", official_keys)
    write_json(
        WORK_ROOT / "modifier_inventory.json",
        {
            "modifier_tokens": dict(sorted(modifier_counts.items())),
            "unmatched_blocks": unmatched,
        },
    )
    catalog = {
        "family": FAMILY,
        "jars": surfaces,
        "english_keys": len(english),
        "block_keys": sum(key.startswith("block.chipped.") for key in english),
        "tag_keys": sum(key.startswith("tag.item.chipped.") for key in english),
        "other_keys": sum(
            not key.startswith(("block.chipped.", "tag.item.chipped."))
            for key in english
        ),
        "integration_language_keys": len(integration_english),
        "base_materials": len(bases),
        "official_base_materials": sum(
            key != "project_reviewed_missing_official_key"
            for key in official_keys.values()
        ),
        "project_reviewed_base_materials": sum(
            key == "project_reviewed_missing_official_key"
            for key in official_keys.values()
        ),
        "parsed_blocks": parsed_blocks,
        "unmatched_blocks": len(unmatched),
        "modifier_tokens": len(modifier_counts),
        "minecraft_asset": {
            **asset_metadata,
            "language_path": language_path.as_posix(),
            "language_sha1_verified": hashlib.sha1(
                language_path.read_bytes(), usedforsecurity=False
            ).hexdigest()
            == asset_metadata["language_object_hash"],
        },
        "korean_candidates": {
            "current_jar_korean_keys": len(read_language("chipped", "ko_kr")),
            "project_korean_before_family": False,
            "instance_russian_candidate": {
                "path": RUSSIAN_CANDIDATE,
                "keys": len(russian) if isinstance(russian, dict) else 0,
                "used_for_korean_translation": False,
            },
        },
        "errors": errors,
        "status": "prepared" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "source_surface_catalog.json", catalog)
    summary = {
        key: catalog[key]
        for key in (
            "family",
            "english_keys",
            "block_keys",
            "tag_keys",
            "other_keys",
            "integration_language_keys",
            "base_materials",
            "official_base_materials",
            "project_reviewed_base_materials",
            "parsed_blocks",
            "unmatched_blocks",
            "modifier_tokens",
            "errors",
            "status",
        )
    }
    write_json(WORK_ROOT / "inventory.json", summary)
    return summary


def translate_modifier(tokens: list[str], terms: dict[str, str]) -> str:
    """수식어 토큰을 검수된 한국어 순서 그대로 결합해요."""
    return " ".join(terms[token] for token in tokens if terms[token])


def translate_blocks(
    english: dict[str, str],
    bases: dict[str, str],
    terms: dict[str, str],
    exceptions: dict[str, str],
) -> dict[str, str]:
    """6,967개 블록 이름을 공식 재료명과 검수된 수식어로 만들어요."""
    translated = {}
    known_bases = list(bases)
    for key, source in english.items():
        if not key.startswith("block.chipped."):
            continue
        if key in exceptions:
            translated[key] = exceptions[key]
            continue
        slug = key.removeprefix("block.chipped.")
        parsed = parse_block_slug(slug, known_bases)
        if parsed is None:
            raise KeyError(f"예외 번역이 없는 블록이에요: {key}={source}")
        base, prefix, suffix = parsed
        pieces = [
            translate_modifier(prefix, terms),
            bases[base],
            translate_modifier(suffix, terms),
        ]
        translated[key] = " ".join(piece for piece in pieces if piece)
    return translated


def build() -> dict[str, object]:
    """현재 영어 7,265키 전체의 검수된 한국어 산출물을 만들어요."""
    english = load_json(WORK_ROOT / "en_us.json")
    bases = load_json(WORK_ROOT / "official_base_ko.json")
    modifier_inventory = load_json(WORK_ROOT / "modifier_inventory.json")
    terms = load_json(MODIFIER_TERMS)
    exceptions = load_json(BLOCK_EXCEPTIONS)
    nonblock = load_json(NONBLOCK_TRANSLATIONS)
    if not all(
        isinstance(value, dict)
        for value in (english, bases, modifier_inventory, terms, exceptions, nonblock)
    ):
        raise TypeError("Chipped 작업 JSON 중 객체가 아닌 파일이 있어요")
    expected_terms = set(modifier_inventory["modifier_tokens"])
    if set(terms) != expected_terms:
        raise KeyError(
            "수식어 번역표가 달라요: "
            f"missing={sorted(expected_terms - set(terms))}, "
            f"extra={sorted(set(terms) - expected_terms)}"
        )
    expected_exceptions = set(modifier_inventory["unmatched_blocks"])
    if set(exceptions) != expected_exceptions:
        raise KeyError(
            "블록 예외 번역표가 달라요: "
            f"missing={sorted(expected_exceptions - set(exceptions))}, "
            f"extra={sorted(set(exceptions) - expected_exceptions)}"
        )
    expected_nonblock = {
        key for key in english if not key.startswith(("block.", "tag.item.chipped."))
    }
    if set(nonblock) != expected_nonblock:
        raise KeyError(
            "비블록 번역표가 달라요: "
            f"missing={sorted(expected_nonblock - set(nonblock))}, "
            f"extra={sorted(set(nonblock) - expected_nonblock)}"
        )
    blocks = translate_blocks(english, bases, terms, exceptions)
    target = {}
    for key in english:
        if key.startswith("block.chipped."):
            target[key] = blocks[key]
        elif key.startswith("tag.item.chipped."):
            target[key] = bases[key.removeprefix("tag.item.chipped.")]
        else:
            target[key] = nonblock[key]
    write_json(WORK_ROOT / "ko_kr.json", target)
    write_json(RESOURCE_OUTPUT, target)
    report = {
        "reviewed_language_keys": len(english),
        "existing_korean_values_reused": 0,
        "new_language_values": len(target),
        "official_base_names": len(bases) - len(MISSING_BASE_TRANSLATIONS),
        "project_reviewed_base_names": len(MISSING_BASE_TRANSLATIONS),
        "composed_block_names": len(blocks) - len(exceptions),
        "exception_block_names": len(exceptions),
        "tag_names": sum(key.startswith("tag.item.chipped.") for key in target),
        "other_names": len(nonblock),
        "errors": [],
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def preserved_errors(key: str, source: str, target: str) -> list[str]:
    """자리표시자·서식·숫자·줄바꿈을 보존했는지 확인해요."""
    errors = []
    for name, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식 코드", FORMAT_CODE),
        ("숫자", NUMBER),
    ):
        if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
            errors.append(f"{key} {name}이 달라요")
    if source.count("\n") != target.count("\n"):
        errors.append(f"{key} 실제 줄바꿈 수가 달라요")
    if source.count("\\n") != target.count("\\n"):
        errors.append(f"{key} 이스케이프 줄바꿈 수가 달라요")
    return errors


def audit_references() -> tuple[dict[str, object], list[str]]:
    """FTB Quests와 KubeJS의 관련 참조 및 직접 표시 후보를 확인해요."""
    instance = resolve_source_root()
    errors = []
    report: dict[str, object] = {"ftbquests": [], "kubejs": [], "read_errors": []}
    suffixes = {".cfg", ".js", ".json", ".snbt", ".toml", ".txt"}
    excluded = (instance / RUSSIAN_CANDIDATE).resolve()
    for label, base in (
        ("ftbquests", instance / "config/ftbquests/quests"),
        ("kubejs", instance / "kubejs"),
    ):
        rows = report[label]
        if not isinstance(rows, list) or not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if (
                not path.is_file()
                or path.suffix.lower() not in suffixes
                or path.resolve() == excluded
            ):
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                report["read_errors"].append(f"{path}: {exc}")
                continue
            count = text.lower().count("chipped:")
            if not count:
                continue
            visible_lines = []
            for number, line in enumerate(text.splitlines(), 1):
                if "chipped:" not in line.lower():
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


def assert_current_sources(catalog: dict[str, object]) -> list[str]:
    """원문 추출 뒤 JAR과 공식 한국어 자산이 바뀌지 않았는지 확인해요."""
    errors = []
    by_label = {row["label"]: row for row in catalog["jars"]}
    for label, row in by_label.items():
        jar = find_jar(label)
        if (
            row["jar"] != jar.name
            or row["jar_size"] != jar.stat().st_size
            or row["jar_mtime_ns"] != jar.stat().st_mtime_ns
        ):
            errors.append(f"{label} JAR이 원문 추출 당시와 달라요")
    language_path, _, metadata = minecraft_assets()
    if (
        metadata["language_object_hash"]
        != catalog["minecraft_asset"]["language_object_hash"]
        or language_path.stat().st_size
        != catalog["minecraft_asset"]["language_object_size"]
    ):
        errors.append("Minecraft 공식 한국어 자산이 원문 추출 당시와 달라요")
    return errors


def audit() -> tuple[dict[str, object], list[str]]:
    """두 JAR의 데이터·NBT·가이드와 별도 표시 경로를 감사해요."""
    catalog = load_json(WORK_ROOT / "source_surface_catalog.json")
    errors = assert_current_sources(catalog)
    surface_summary = {}
    for row in catalog["jars"]:
        current_errors = []
        if row["invalid_json"] or row["guide_candidates"]:
            current_errors.append("데이터 또는 가이드 감사를 완료하지 못했어요")
        if row["data_direct_fields"]:
            current_errors.append("직접 데이터 표시 문구가 있어요")
        if row["nbt_visible_fields"]:
            current_errors.append("구조물 NBT 표시 문구가 있어요")
        errors.extend(f"{row['label']}: {message}" for message in current_errors)
        surface_summary[row["label"]] = {
            "data_json_files": row["data_json_files"],
            "data_localized_fields": len(row["data_localized_fields"]),
            "data_direct_fields": len(row["data_direct_fields"]),
            "nbt_files": row["nbt_files"],
            "nbt_visible_fields": len(row["nbt_visible_fields"]),
            "guide_candidates": len(row["guide_candidates"]),
        }
    references, reference_errors = audit_references()
    errors.extend(reference_errors)
    report = {
        "family": FAMILY,
        "jar_surfaces": surface_summary,
        "references": references,
        "ftbquests_display_work": (
            "no_related_references"
            if not references["ftbquests"]
            else "item_ids_use_resourcepack_names"
        ),
        "kubejs_display_work": (
            "no_related_references"
            if not references["kubejs"]
            else "item_ids_use_resourcepack_names"
        ),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def verify_language() -> tuple[dict[str, object], list[str]]:
    """현재 영어 7,265키와 작업본·산출물·이름 충돌을 검증해요."""
    english = read_language("chipped", "en_us")
    work = load_json(WORK_ROOT / "ko_kr.json")
    output = load_json(RESOURCE_OUTPUT)
    errors = []
    if list(work) != list(english) or list(output) != list(english):
        errors.append("한국어 키 또는 순서가 현재 영어 원문과 달라요")
    if work != output:
        errors.append("작업 한국어와 리소스팩 산출물이 달라요")
    same = []
    no_hangul = []
    for key, source in english.items():
        target = output.get(key)
        if not isinstance(target, str):
            errors.append(f"문자열 한국어 값이 없어요: {key}")
            continue
        errors.extend(preserved_errors(key, source, target))
        if source == target:
            same.append(key)
        if not re.search(r"[가-힣]", target):
            no_hangul.append(key)
    expected_same = ["itemGroup.chipped.main"]
    if same != expected_same or no_hangul != expected_same:
        errors.append(
            "영어 유지값 검토 결과가 달라요: "
            f"same={same}, no_hangul={no_hangul}, expected={expected_same}"
        )
    collisions = defaultdict(list)
    for key, target in output.items():
        if key.startswith("block.chipped."):
            collisions[target].append(key)
    unexpected_collisions = {
        target: keys for target, keys in collisions.items() if len(keys) > 1
    }
    if unexpected_collisions:
        errors.append(f"블록 검색명이 충돌해요: {unexpected_collisions}")
    report = {
        "reviewed_english_keys": len(english),
        "output_keys": len(output),
        "bundled_korean_candidate_keys": len(read_language("chipped", "ko_kr")),
        "existing_korean_values_reused": 0,
        "new_language_values": len(output),
        "intentional_same_keys": same,
        "unexpected_name_collisions": unexpected_collisions,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """언어·표시 표면과 적용 기록을 함께 검증해요."""
    catalog = load_json(WORK_ROOT / "source_surface_catalog.json")
    source_errors = assert_current_sources(catalog)
    language, language_errors = verify_language()
    surface, surface_errors = audit()
    errors = source_errors + language_errors + surface_errors
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = load_json(deployment_path) if deployment_path.is_file() else None
    report = {
        "family": FAMILY,
        "language": language,
        "surface_audit": surface["status"],
        "ftbquests": surface["ftbquests_display_work"],
        "kubejs": surface["kubejs_display_work"],
        "output_files": [DEPLOYMENT_PATH],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    completion = {
        "family": FAMILY,
        "reviewed_language_keys": language["reviewed_english_keys"],
        "bundled_korean_candidate_keys": language["bundled_korean_candidate_keys"],
        "existing_korean_values_reused": 0,
        "new_language_values": language["new_language_values"],
        "ftbquests_work": surface["ftbquests_display_work"],
        "kubejs_work": surface["kubejs_display_work"],
        "output_files": [DEPLOYMENT_PATH],
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
    """적용 매니페스트의 백업·해시 결과를 완료 기록에 연결해요."""
    manifest_path = manifest_path.resolve()
    manifest = load_json(manifest_path)
    errors = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 매니페스트 상태가 완료가 아니에요")
    if manifest.get("java_processes"):
        errors.append(
            f"적용 당시 Java 프로세스가 있었어요: {manifest['java_processes']}"
        )
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
        missing = [DEPLOYMENT_PATH] if DEPLOYMENT_PATH not in records else []
        extra = sorted(set(records) - {DEPLOYMENT_PATH})
        if missing or extra:
            errors.append(f"적용 경로가 달라요: missing={missing}, extra={extra}")
        record = records.get(DEPLOYMENT_PATH, {})
        hash_verified = record.get("source_sha256") == record.get("after_sha256")
        if not hash_verified:
            errors.append("적용 후 Chipped 언어 파일 해시가 달라요")
        if target.get("unexpected_changes"):
            errors.append(f"예상 밖 적용 변경이 있어요: {target['unexpected_changes']}")
        summaries.append(
            {
                "target_type": target.get("target_type"),
                "target_root": target.get("target_root"),
                "changed_paths": target.get("changed_paths", []),
                "unexpected_changes": target.get("unexpected_changes", []),
                "hash_verified": hash_verified,
            }
        )
    try:
        manifest_name = manifest_path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        manifest_name = str(manifest_path)
    report = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "backup_manifest": manifest_name,
        "expected_paths": [DEPLOYMENT_PATH],
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
        choices=("prepare", "build", "audit", "verify", "record-deployment"),
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
    else:
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        result, _ = record_deployment(args.manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return (
        0 if result["status"] in {"prepared", "complete", "applied_and_verified"} else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
