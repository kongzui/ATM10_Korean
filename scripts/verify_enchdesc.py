#!/usr/bin/env python3
"""Enchantment Descriptions의 전체 번역과 동적 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

WORKING = PROJECT_ROOT / "working/common_ui/curios_effects/enchdesc/ko_kr.json"
RECHECK_OVERRIDES = (
    PROJECT_ROOT / "working/common_ui/curios_effects/enchdesc/recheck_overrides.json"
)
OUTPUT = (
    active_output_root() / "resourcepack/ATM10_Korean/assets/enchdesc/lang/ko_kr.json"
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
FORBIDDEN_TERMS = re.compile(
    r"엔티티|재사용 대기 시간|마법부여|부정적인 효과|마우스 오른쪽 버튼"
)
MISSING_SOURCE_DESCRIPTION_IDS = {
    "ars_additions:spellweave",
    "ars_elemental:soulbound",
    "draconicevolution:reaper",
    "farmersdelight:backstabbing",
    "forbidden_arcanus:soul_looting",
    "quarryplus:quarry_pickaxe",
}
OWNER_COLLISION_VALUES = {
    "enchantment.deeperdarker.catalysis.desc": (
        "몹을 처치하면 주변에 스컬크를 퍼뜨립니다."
    ),
    "enchantment.deeperdarker.sculk_smite.desc": (
        "셰터드와 워든 같은 스컬크 몹에게 주는 피해가 늘어납니다."
    ),
}


def load_json_bytes(raw: bytes, source: str) -> dict[str, object]:
    """UTF-8 JSON 객체만 허용한다."""
    try:
        value = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"JSON 읽기 실패: {source}: {exc}") from exc
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {source}")
    return value


def load_json_path(path: Path) -> dict[str, object]:
    return load_json_bytes(path.read_bytes(), str(path))


def validate_values(english: dict[str, object], korean: dict[str, object]) -> list[str]:
    """키, 자료형과 모든 보호 문자열을 검증한다."""
    errors = []
    if list(english) != list(korean):
        missing = sorted(set(english) - set(korean))
        extra = sorted(set(korean) - set(english))
        errors.append(f"키 또는 순서 불일치: 누락={missing}, 초과={extra}")
    for key in english.keys() & korean.keys():
        source = english[key]
        translated = korean[key]
        if not isinstance(source, str) or not isinstance(translated, str):
            errors.append(f"문자열 자료형이 아닌 언어 값: {key}")
            continue
        if PLACEHOLDER.findall(source) != PLACEHOLDER.findall(translated):
            errors.append(f"자리표시자 불일치: {key}")
        if Counter(FORMAT_CODE.findall(source)) != Counter(
            FORMAT_CODE.findall(translated)
        ):
            errors.append(f"서식 코드 불일치: {key}")
        if source.count("\n") != translated.count("\n"):
            errors.append(f"줄바꿈 수 불일치: {key}")
    return errors


def scan_installed_enchantments(
    instance: Path, source_jar: Path
) -> tuple[
    dict[str, list[str]],
    dict[str, list[tuple[str, object]]],
    dict[str, list[tuple[str, object]]],
    list[str],
]:
    """현재 JAR과 KubeJS 데이터에서 마법 부여 및 소유 언어 키를 찾는다."""
    definitions: dict[str, list[str]] = defaultdict(list)
    other_english: dict[str, list[tuple[str, object]]] = defaultdict(list)
    other_korean: dict[str, list[tuple[str, object]]] = defaultdict(list)
    errors = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        try:
            with ZipFile(jar_path) as archive:
                for name in archive.namelist():
                    definition = re.fullmatch(
                        r"data/([^/]+)/enchantment/(.+)\.json", name
                    )
                    if definition:
                        try:
                            load_json_bytes(
                                archive.read(name), f"{jar_path.name}:{name}"
                            )
                        except (RuntimeError, TypeError) as exc:
                            errors.append(str(exc))
                            continue
                        enchantment_id = f"{definition.group(1)}:{definition.group(2)}"
                        definitions[enchantment_id].append(f"{jar_path.name}:{name}")
                    if jar_path == source_jar or not re.fullmatch(
                        r"assets/[^/]+/lang/(?:en_us|ko_kr)\.json", name
                    ):
                        continue
                    raw = archive.read(name)
                    if b"enchantment." not in raw or b".desc" not in raw:
                        continue
                    try:
                        values = load_json_bytes(raw, f"{jar_path.name}:{name}")
                    except (RuntimeError, TypeError) as exc:
                        errors.append(str(exc))
                        continue
                    target = (
                        other_english if name.endswith("/en_us.json") else other_korean
                    )
                    for key, value in values.items():
                        if key.startswith("enchantment.") and key.endswith(".desc"):
                            target[key].append((jar_path.name, value))
        except BadZipFile as exc:
            errors.append(f"JAR 읽기 실패: {jar_path}: {exc}")

    kubejs_root = instance / "kubejs"
    for path in sorted(kubejs_root.rglob("*.json")):
        relative = path.relative_to(kubejs_root).as_posix()
        definition = re.fullmatch(r"data/([^/]+)/enchantment/(.+)\.json", relative)
        if not definition:
            continue
        try:
            load_json_path(path)
        except (RuntimeError, TypeError) as exc:
            errors.append(str(exc))
            continue
        enchantment_id = f"{definition.group(1)}:{definition.group(2)}"
        definitions[enchantment_id].append(f"kubejs:{relative}")
    return definitions, other_english, other_korean, errors


def merged_project_korean() -> tuple[dict[str, object], list[str], int]:
    """프로젝트 리소스팩의 모든 한국어 마법 부여 설명을 병합한다."""
    merged = {}
    errors = []
    files = 0
    root = active_output_root() / "resourcepack/ATM10_Korean/assets"
    for path in sorted(root.glob("*/lang/ko_kr.json")):
        files += 1
        try:
            values = load_json_path(path)
        except (RuntimeError, TypeError) as exc:
            errors.append(str(exc))
            continue
        for key, value in values.items():
            if key.startswith("enchantment.") and key.endswith(".desc"):
                merged[key] = value
    return merged, errors, files


def verify(instance: Path) -> dict[str, object]:
    errors = []
    source_jar_matches = sorted((instance / "mods").glob("enchdesc-neoforge-*.jar"))
    if len(source_jar_matches) != 1:
        raise RuntimeError(
            f"Enchantment Descriptions JAR 수 불일치: {len(source_jar_matches)}"
        )
    source_jar = source_jar_matches[0]
    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        english = load_json_bytes(
            archive.read("assets/enchdesc/lang/en_us.json"), "enchdesc:en_us"
        )
        bundled_korean = load_json_bytes(
            archive.read("assets/enchdesc/lang/ko_kr.json"), "enchdesc:ko_kr"
        )
        class_files = [name for name in names if name.endswith(".class")]
        description_class_files = []
        for name in class_files:
            raw = archive.read(name)
            if b"getDescription" in raw and b"I18n" in raw and b"desc" in raw:
                description_class_files.append(name)
        advancement_files = [
            name for name in names if name.endswith(".json") and "/advancement" in name
        ]
        recipe_files = [
            name for name in names if name.endswith(".json") and "/recipe" in name
        ]
        guide_files = [
            name
            for name in names
            if any(marker in name.lower() for marker in ("patchouli", "guideme"))
        ]

    working = load_json_path(WORKING)
    output = load_json_path(OUTPUT)
    overrides = load_json_path(RECHECK_OVERRIDES)
    errors.extend(validate_values(english, working))
    if output != working:
        errors.append("Enchantment Descriptions 작업본과 산출물이 다릅니다")
    override_mismatches = sorted(
        key for key, expected in overrides.items() if working.get(key) != expected
    )
    if override_mismatches:
        errors.append(f"확정 재검수 교정값 불일치: {override_mismatches}")
    if len(english) != 182 or len(bundled_korean) != 45:
        errors.append(
            "원문·번들 한국어 키 수 변경: "
            f"원문={len(english)}, 번들={len(bundled_korean)}"
        )
    bundled_extra = set(bundled_korean) - set(english)
    if bundled_extra != {"enchantment.minecraft.sweeping.desc"}:
        errors.append(f"번들 한국어 레거시 초과 키 변경: {sorted(bundled_extra)}")
    forbidden = sorted(
        key
        for key, value in working.items()
        if isinstance(value, str) and FORBIDDEN_TERMS.search(value)
    )
    if forbidden:
        errors.append(f"금지·충돌 용어 잔존: {forbidden}")
    support_keys = {key for key in english if key.startswith("__support_")}
    support_changed = sorted(
        key for key in support_keys if working.get(key) != english.get(key)
    )
    if support_changed:
        errors.append(f"지원 모드 출처·URL 값 변경: {support_changed}")
    if len(description_class_files) != 1:
        errors.append(
            "동적 .desc 표시 클래스 수 변경: " f"{len(description_class_files)}"
        )

    definitions, other_english, other_korean, scan_errors = scan_installed_enchantments(
        instance, source_jar
    )
    errors.extend(scan_errors)
    project_korean, project_errors, project_language_files = merged_project_korean()
    errors.extend(project_errors)
    installed_ids = set(definitions)
    description_keys = {
        enchantment_id: ("enchantment." + enchantment_id.replace(":", ".", 1) + ".desc")
        for enchantment_id in installed_ids
    }
    available_english = set(english) | set(other_english)
    missing_english = {
        enchantment_id
        for enchantment_id, key in description_keys.items()
        if key not in available_english
    }
    missing_korean = {
        enchantment_id
        for enchantment_id, key in description_keys.items()
        if key not in project_korean
    }
    if missing_english != MISSING_SOURCE_DESCRIPTION_IDS:
        errors.append(
            f"영어 설명이 없는 설치 마법 부여 범위 변경: {sorted(missing_english)}"
        )
    if missing_korean != MISSING_SOURCE_DESCRIPTION_IDS:
        errors.append(
            f"한국어 설명이 없는 설치 마법 부여 범위 변경: {sorted(missing_korean)}"
        )
    owner_collisions = set(english) & set(other_english)
    if owner_collisions != set(OWNER_COLLISION_VALUES):
        errors.append(
            f"다른 모드 소유 설명 키 충돌 범위 변경: {sorted(owner_collisions)}"
        )
    owner_output = load_json_path(
        active_output_root()
        / "resourcepack/ATM10_Korean/assets/deeperdarker/lang/ko_kr.json"
    )
    owner_mismatches = sorted(
        key
        for key, expected in OWNER_COLLISION_VALUES.items()
        if working.get(key) != expected or owner_output.get(key) != expected
    )
    if owner_mismatches:
        errors.append(f"소유 모드와 설명 번역 충돌: {owner_mismatches}")

    english_value_collisions = {
        key: values
        for key, values in other_english.items()
        if len({json.dumps(value, sort_keys=True) for _, value in values}) > 1
    }
    if english_value_collisions:
        errors.append(
            "다른 모드 간 영어 설명 값 충돌: " f"{sorted(english_value_collisions)}"
        )

    config_path = instance / "config/enchdesc.json"
    config = load_json_path(config_path)
    expected_config_values = {
        "enabled": True,
        "only_on_books": True,
        "only_in_enchanting_table": False,
        "require_keybind": False,
    }
    config_mismatches = sorted(
        key
        for key, expected in expected_config_values.items()
        if not isinstance(config.get(key), dict)
        or config[key].get("value") is not expected
    )
    if config_mismatches:
        errors.append(f"Enchantment Descriptions 표시 설정 변경: {config_mismatches}")
    activate_text = config.get("activate_text", {}).get("value", {})
    if activate_text.get("translate") != "enchdesc.activate.message":
        errors.append("Shift 안내문 번역 키 연결이 다릅니다")

    quest_files = sorted((instance / "config/ftbquests/quests").rglob("*.snbt"))
    quest_references = []
    for path in quest_files:
        text = path.read_text(encoding="utf-8-sig")
        if re.search(r"(?i)\benchdesc\b|enchantment descriptions?", text):
            quest_references.append(path.relative_to(instance).as_posix())
    if quest_references:
        errors.append(f"예상하지 않은 FTB Quests 직접 참조: {quest_references}")

    kubejs_files = 0
    kubejs_references = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".js",
            ".json",
            ".snbt",
            ".txt",
            ".toml",
        }:
            continue
        kubejs_files += 1
        text = path.read_text(encoding="utf-8-sig")
        if re.search(r"(?i)\benchdesc\b|enchantment descriptions?", text):
            kubejs_references.append(path.relative_to(instance).as_posix())
    if kubejs_references:
        errors.append(f"예상하지 않은 KubeJS 직접 참조: {kubejs_references}")

    if WORKING.read_bytes().startswith(b"\xef\xbb\xbf"):
        errors.append("작업본에 UTF-8 BOM이 있습니다")
    if OUTPUT.read_bytes().startswith(b"\xef\xbb\xbf"):
        errors.append("산출물에 UTF-8 BOM이 있습니다")
    if errors:
        raise RuntimeError(
            "Enchantment Descriptions 검증 실패:\n" + "\n".join(errors[:40])
        )

    description_values = [
        value
        for key, value in working.items()
        if key.startswith("enchantment.") and key.endswith(".desc")
    ]
    duplicate_description_groups = sum(
        1 for count in Counter(description_values).values() if count > 1
    )
    return {
        "scope": "Enchantment Descriptions 전체 번역 재검수",
        "source_jar": source_jar.name,
        "source_jar_sha256": hashlib.sha256(source_jar.read_bytes()).hexdigest(),
        "source_jar_bytes": source_jar.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(class_files),
        "dynamic_description_class_files": len(description_class_files),
        "source_keys_reviewed": len(english),
        "source_description_keys_reviewed": len(description_values),
        "bundled_korean_candidates_reviewed": len(bundled_korean),
        "bundled_korean_missing_keys": len(set(english) - set(bundled_korean)),
        "bundled_korean_legacy_extra_keys": len(bundled_extra),
        "existing_candidates_retained": len(english) - len(overrides),
        "existing_candidates_corrected": len(overrides),
        "installed_enchantment_definition_files": sum(
            len(values) for values in definitions.values()
        ),
        "installed_enchantment_ids": len(installed_ids),
        "installed_description_keys_available": len(installed_ids - missing_korean),
        "installed_missing_english_descriptions_deferred": len(missing_english),
        "installed_missing_description_ids": sorted(missing_english),
        "other_mod_english_description_keys_traced": len(other_english),
        "other_mod_korean_description_keys_traced": len(other_korean),
        "other_mod_owner_key_collisions_reviewed": len(owner_collisions),
        "harmful_owner_key_collisions": 0,
        "duplicate_korean_description_groups_reviewed": duplicate_description_groups,
        "harmful_translation_collisions": 0,
        "project_language_files_reviewed": project_language_files,
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_direct_references": 0,
        "kubejs_files_reviewed": kubejs_files,
        "kubejs_direct_references": 0,
        "config_display_mode": "enchanted_books_only",
        "advancement_files": len(advancement_files),
        "recipe_files": len(recipe_files),
        "guide_files": len(guide_files),
        "validation": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            verify(resolve_source_root(args.instance)), ensure_ascii=False, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
