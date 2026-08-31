#!/usr/bin/env python3
"""Akashic Tome의 전체 번역과 실제 표시·연동 경로를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

WORK_ROOT = PROJECT_ROOT / "working/common_ui/guide_ui/akashictome"
WORKING = WORK_ROOT / "ko_kr.json"
OVERRIDES = WORK_ROOT / "recheck_overrides.json"
REPORT = WORK_ROOT / "recheck_20260820.json"
OUTPUT = (
    active_output_root()
    / "resourcepack/ATM10_Korean/assets/akashictome/lang/ko_kr.json"
)
GLOSSARY = PROJECT_ROOT / "glossary/README.md"

EXPECTED_JAR = "AkashicTome-1.8-30.jar"
EXPECTED_JAR_SHA256 = "c60f58fba975fe22681d69bd06dc93818e53a67830d9118167979852206f6ca8"
EXPECTED_CONFIG_SHA256 = (
    "b196f1a6510c850c0c6e39422d544a5fda0b3a119f179d4c8159a315787b1124"
)
EXPECTED_CONFIG_OPTIONS = {
    "Allow all items to be added",
    "Whitelisted Items",
    "Whitelisted Names",
    "Blacklisted Mods",
    "Blacklisted Items",
    "Mod Aliases",
    "Hide Book Render",
}
EXPECTED_CLASS_REFERENCES = {
    "akashictome.sudo_name": "vazkii/akashictome/MorphingHandler.class",
    "akashictome.click_morph": "vazkii/akashictome/client/HUDHandler.class",
    "akashictome.misc.shift_for_info": "vazkii/akashictome/TomeItem.class",
}
EXPECTED_OVERRIDES = {
    "akashictome.click_morph": "Shift+우클릭하여 책을 전환하세요.",
    "akashictome.misc.shift_for_info": (
        "§7§bSHIFT§7 키를 누르고 있으면 자세한 정보가 표시됩니다"
    ),
    "akashictome.configuration.Hide Book Render": "책 모델 숨기기",
}
EXPECTED_UNTRANSLATED = {
    "akashictome.sudo_name",
    "item.akashictome.tome",
}
EXPECTED_CONFIG_REFERENCES = {
    "config/crash_assistant/modlist.json",
    "config/jei/ingredient-list-mod-sort-order.ini",
}
GLOSSARY_ROWS = (
    "| Akashic Tome | Akashic Tome | 공식 모드명 |",
    "| Whitelist / Blacklist | 허용 목록 / 차단 목록 | 필터·설정 용어 |",
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
LANGUAGE_FILE = re.compile(r"assets/akashictome/lang/[a-z_]+\.json")
OTHER_ENGLISH_LANGUAGE = re.compile(r"assets/[^/]+/lang/en_us\.json")
DIRECT_REFERENCE = re.compile(r"(?i)akashic.?tome|akashictome")
RELATED_EXTENSIONS = {".ini", ".js", ".json", ".snbt", ".toml", ".txt"}


def load_json_bytes(raw: bytes, source: str) -> dict[str, object]:
    """중복 키가 없는 UTF-8 JSON 객체만 허용한다."""
    duplicates: list[str] = []

    def object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result = {}
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        return result

    try:
        value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=object_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"JSON 읽기 실패: {source}: {exc}") from exc
    if duplicates:
        raise RuntimeError(f"JSON 중복 키: {source}: {sorted(set(duplicates))}")
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {source}")
    return value


def load_json_path(path: Path) -> dict[str, object]:
    return load_json_bytes(path.read_bytes(), str(path))


def validate_language(
    english: dict[str, object], korean: dict[str, object]
) -> list[str]:
    """키, 순서, 자료형과 보호 문자열을 검증한다."""
    errors = []
    if list(english) != list(korean):
        errors.append(
            "키 또는 순서 불일치: "
            f"누락={sorted(set(english) - set(korean))}, "
            f"초과={sorted(set(korean) - set(english))}"
        )
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


def find_related_files(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.suffix.lower() in RELATED_EXTENSIONS
    ]


def verify_other_language_owners(
    instance: Path, source_jar: Path, english: dict[str, object], errors: list[str]
) -> tuple[int, int]:
    """다른 JAR의 영어 언어 파일에 같은 소유 키나 이름이 있는지 확인한다."""
    language_files = 0
    conflicts = []
    unreadable = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        try:
            with ZipFile(jar_path) as archive:
                for name in archive.namelist():
                    if not OTHER_ENGLISH_LANGUAGE.fullmatch(name):
                        continue
                    language_files += 1
                    raw = archive.read(name)
                    try:
                        values = json.loads(raw.decode("utf-8-sig"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                        unreadable.append(f"{jar_path.name}:{name}:{exc}")
                        continue
                    if not isinstance(values, dict):
                        unreadable.append(
                            f"{jar_path.name}:{name}:JSON 최상위 값이 객체가 아님"
                        )
                        continue
                    if jar_path == source_jar:
                        continue
                    shared_keys = sorted(set(values) & set(english))
                    name_rows = sorted(
                        key
                        for key, value in values.items()
                        if isinstance(value, str) and "akashic tome" in value.lower()
                    )
                    if shared_keys or name_rows:
                        conflicts.append(
                            f"{jar_path.name}:{name}:키={shared_keys}:이름={name_rows}"
                        )
        except (BadZipFile, KeyError, OSError, RuntimeError, TypeError) as exc:
            unreadable.append(f"{jar_path.name}:{exc}")
    if unreadable:
        errors.append("설치 JAR 언어 파일 읽기 오류: " + " | ".join(unreadable[:10]))
    if conflicts:
        errors.append(
            "다른 모드의 Akashic Tome 표시 소유 충돌: " + " | ".join(conflicts)
        )
    if language_files != 388:
        errors.append(f"설치 영어 언어 파일 수 변경: {language_files}")
    return language_files, len(conflicts)


def verify(instance: Path, pre_apply: bool = False) -> dict[str, object]:
    """현재 설치 영어 원문과 프로젝트 산출물을 전수 검증한다."""
    errors: list[str] = []
    jar_matches = sorted((instance / "mods").glob("AkashicTome-*.jar"))
    if [path.name for path in jar_matches] != [EXPECTED_JAR]:
        raise RuntimeError(
            f"Akashic Tome JAR 범위 변경: {[path.name for path in jar_matches]}"
        )
    source_jar = jar_matches[0]
    source_sha256 = hashlib.sha256(source_jar.read_bytes()).hexdigest()
    if source_sha256 != EXPECTED_JAR_SHA256:
        errors.append(f"Akashic Tome JAR SHA-256 변경: {source_sha256}")

    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        english = load_json_bytes(
            archive.read("assets/akashictome/lang/en_us.json"),
            "Akashic Tome en_us",
        )
        bundled = load_json_bytes(
            archive.read("assets/akashictome/lang/ko_kr.json"),
            "Akashic Tome ko_kr",
        )
        class_files = {
            name: archive.read(name) for name in names if name.endswith(".class")
        }
        language_files = sorted(name for name in names if LANGUAGE_FILE.fullmatch(name))
        recipe_files = [
            name for name in names if name.endswith(".json") and "/recipe/" in name
        ]
        advancement_files = [
            name for name in names if name.endswith(".json") and "/advancement" in name
        ]
        guide_files = [
            name
            for name in names
            if any(
                marker in name.lower()
                for marker in ("patchouli", "guideme", "modonomicon")
            )
        ]

    if (len(names), len(class_files), len(language_files)) != (53, 17, 10):
        errors.append(
            "Akashic Tome JAR 구성 변경: "
            f"항목={len(names)}, 클래스={len(class_files)}, 언어={len(language_files)}"
        )
    if len(english) != 11 or len(bundled) != 3:
        errors.append(
            f"언어 키 수 변경: 영어={len(english)}, 내장 한국어={len(bundled)}"
        )
    if set(bundled) != {
        "akashictome.sudo_name",
        "akashictome.click_morph",
        "item.akashictome.tome",
    }:
        errors.append(f"내장 한국어 후보 범위 변경: {sorted(bundled)}")
    if len(recipe_files) != 2 or advancement_files or guide_files:
        errors.append(
            "Akashic Tome 데이터 범위 변경: "
            f"제작법={recipe_files}, 발전={advancement_files}, 가이드={guide_files}"
        )

    class_references = {
        key: sorted(name for name, raw in class_files.items() if key.encode() in raw)
        for key in english
        if any(key.encode() in raw for raw in class_files.values())
    }
    expected_references = {
        key: [class_name] for key, class_name in EXPECTED_CLASS_REFERENCES.items()
    }
    if class_references != expected_references:
        errors.append(f"클래스 언어 키 참조 범위 변경: {class_references}")
    config_class = class_files.get("vazkii/akashictome/ConfigHandler.class", b"")
    missing_config_markers = sorted(
        key for key in EXPECTED_CONFIG_OPTIONS if key.encode() not in config_class
    )
    if missing_config_markers:
        errors.append(f"설정 필드 바이트코드 변경: {missing_config_markers}")
    client_class = class_files.get(
        "vazkii/akashictome/client/AkashicTomeClient.class", b""
    )
    if b"ConfigurationScreen" not in client_class:
        errors.append("NeoForge 설정 화면 등록 경로를 찾지 못했습니다")
    if b"tome" not in class_files.get("vazkii/akashictome/Registries.class", b""):
        errors.append("Akashic Tome 아이템 등록 경로를 찾지 못했습니다")

    working = load_json_path(WORKING)
    output = load_json_path(OUTPUT)
    overrides = load_json_path(OVERRIDES)
    errors.extend(validate_language(english, working))
    errors.extend(validate_language(english, output))
    if working != output:
        errors.append("Akashic Tome working과 output 언어 파일이 다릅니다")
    if overrides != EXPECTED_OVERRIDES:
        errors.append(f"Akashic Tome 재검수 교정 목록 변경: {overrides}")
    override_mismatches = sorted(
        key for key, value in EXPECTED_OVERRIDES.items() if output.get(key) != value
    )
    if override_mismatches:
        errors.append(f"Akashic Tome 교정값 불일치: {override_mismatches}")
    untranslated = {key for key in english if output.get(key) == english.get(key)}
    if untranslated != EXPECTED_UNTRANSLATED:
        errors.append(f"영어 원문 유지 범위 변경: {sorted(untranslated)}")
    if OUTPUT.read_bytes().startswith(b"\xef\xbb\xbf"):
        errors.append("Akashic Tome 산출물에 UTF-8 BOM이 있습니다")

    config_path = instance / "config/akashictome-common.toml"
    config_bytes = config_path.read_bytes()
    config_text = config_bytes.decode("utf-8-sig")
    config_options = {
        match.group(1)
        for line in config_text.splitlines()
        if (match := re.match(r'"([^"]+)"\s*=', line))
    }
    if hashlib.sha256(config_bytes).hexdigest() != EXPECTED_CONFIG_SHA256:
        errors.append("Akashic Tome 실제 설정 파일이 바뀌었습니다")
    if config_options != EXPECTED_CONFIG_OPTIONS:
        errors.append(f"Akashic Tome 설정 옵션 범위 변경: {config_options}")
    missing_config_keys = sorted(
        f"akashictome.configuration.{key}"
        for key in config_options
        if f"akashictome.configuration.{key}" not in output
    )
    if missing_config_keys:
        errors.append(f"설정 화면 번역 키 누락: {missing_config_keys}")

    quest_files = sorted((instance / "config/ftbquests/quests").rglob("*.snbt"))
    quest_references = [
        path.relative_to(instance).as_posix()
        for path in quest_files
        if DIRECT_REFERENCE.search(path.read_text(encoding="utf-8-sig"))
    ]
    if len(quest_files) != 142 or quest_references:
        errors.append(f"Akashic Tome FTB Quests 참조 범위 변경: {quest_references}")

    kube_files = find_related_files(instance / "kubejs")
    kube_references = [
        path.relative_to(instance).as_posix()
        for path in kube_files
        if DIRECT_REFERENCE.search(path.read_text(encoding="utf-8-sig"))
    ]
    if kube_references:
        errors.append(f"Akashic Tome KubeJS 표시 참조 발견: {kube_references}")

    config_files = find_related_files(instance / "config")
    config_references = {
        path.relative_to(instance).as_posix()
        for path in config_files
        if DIRECT_REFERENCE.search(path.read_text(encoding="utf-8-sig"))
    }
    if config_references != EXPECTED_CONFIG_REFERENCES:
        errors.append(
            f"Akashic Tome 설정·메타데이터 참조 범위 변경: {config_references}"
        )

    installed_language_files, owner_conflicts = verify_other_language_owners(
        instance, source_jar, english, errors
    )
    project_language_files = sorted(
        (active_output_root() / "resourcepack/ATM10_Korean/assets").glob(
            "*/lang/ko_kr.json"
        )
    )
    item_name_rows = []
    for path in project_language_files:
        values = load_json_path(path)
        for key, value in values.items():
            if key.startswith(("item.", "block.")) and value == "Akashic Tome":
                item_name_rows.append(f"{path.parent.parent.name}:{key}")
    if len(project_language_files) != 285:
        errors.append(f"프로젝트 언어 파일 수 변경: {len(project_language_files)}")
    if item_name_rows != ["akashictome:item.akashictome.tome"]:
        errors.append(f"Akashic Tome 아이템 이름 충돌: {item_name_rows}")

    glossary_text = GLOSSARY.read_text(encoding="utf-8")
    for row in GLOSSARY_ROWS:
        if row not in glossary_text:
            errors.append(f"Akashic Tome 용어집 행 누락: {row}")

    output_sha256 = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    if not pre_apply:
        report = load_json_path(REPORT)
        language_review = report.get("language_review")
        if report.get("validation") != "passed":
            errors.append("Akashic Tome 재검수 보고서 상태가 passed가 아닙니다")
        if (
            not isinstance(language_review, dict)
            or language_review.get("project_candidates_retained") != 8
            or language_review.get("project_candidates_corrected")
            != len(EXPECTED_OVERRIDES)
        ):
            errors.append("Akashic Tome 재검수 보고서 번역 집계 불일치")
        application = report.get("application")
        if (
            not isinstance(application, dict)
            or application.get("status") != "applied_and_verified"
            or application.get("sha256") != output_sha256
            or application.get("unexpected_changes") != 0
        ):
            errors.append("Akashic Tome 재검수 보고서 적용 집계 불일치")

    if errors:
        raise RuntimeError("Akashic Tome 재검수 검증 실패:\n" + "\n".join(errors[:50]))
    return {
        "scope": "Akashic Tome 전체 번역 재검수",
        "source_jar": source_jar.name,
        "source_jar_sha256": source_sha256,
        "source_jar_bytes": source_jar.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(class_files),
        "source_keys_reviewed": len(english),
        "bundled_korean_candidates_reviewed": len(bundled),
        "bundled_korean_candidates_reused": 0,
        "project_candidates_retained": len(english) - len(EXPECTED_OVERRIDES),
        "project_candidates_corrected": len(EXPECTED_OVERRIDES),
        "effective_output_keys": len(output),
        "class_referenced_language_keys": len(class_references),
        "configuration_options_reviewed": len(config_options),
        "configuration_screen_registration_found": True,
        "recipe_files_reviewed": len(recipe_files),
        "advancement_files_reviewed": len(advancement_files),
        "guide_files_reviewed": len(guide_files),
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_reference_files": len(quest_references),
        "kubejs_files_reviewed": len(kube_files),
        "kubejs_reference_files": len(kube_references),
        "configuration_reference_files": len(config_references),
        "installed_english_language_files_reviewed": installed_language_files,
        "other_language_owner_conflicts": owner_conflicts,
        "project_language_files_reviewed": len(project_language_files),
        "harmful_item_name_collisions": 0,
        "glossary_terms_added": len(GLOSSARY_ROWS),
        "output_sha256": output_sha256,
        "validation": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--pre-apply", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    print(
        json.dumps(
            verify(instance, pre_apply=args.pre_apply),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
