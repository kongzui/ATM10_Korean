#!/usr/bin/env python3
"""Crafting Tweaks 번역과 설정·제작 칸 연동 표시 경로를 검증한다."""

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

WORK_ROOT = PROJECT_ROOT / "working/common_ui/convenience/craftingtweaks"
WORKING = WORK_ROOT / "ko_kr.json"
OVERRIDES = WORK_ROOT / "recheck_overrides.json"
REPORT = WORK_ROOT / "recheck_20260820.json"
OUTPUT = (
    active_output_root()
    / "resourcepack/ATM10_Korean/assets/craftingtweaks/lang/ko_kr.json"
)
GLOSSARY = PROJECT_ROOT / "glossary/README.md"

EXPECTED_JAR = "craftingtweaks-neoforge-1.21.1-21.1.10.jar"
EXPECTED_JAR_SHA256 = "e3b5e22c2389f7fb8567b0caaaff43fa87f60ae004685de876180226fbbe63b0"
EXPECTED_CONFIG_SHA256 = (
    "88a669f3aa6e8ffa05c4e1dbefc1f372ca26cea0fd493c16f33d94e37c513f8c"
)
EXPECTED_OVERRIDE_SHA256 = (
    "1d0712c13297754ee205f0df3171b622f92f325571864b0b2c1f16f874dd508e"
)
EXPECTED_OUTPUT_SHA256 = (
    "23038ab497d069195d2e65ca31b2281f358d2570a4cfdc036ca9017c52f257ef"
)
EXPECTED_GRID_FILES = {
    "craftingtweaks/grids/ae2.json",
    "craftingtweaks/grids/ae2_wireless.json",
    "craftingtweaks/grids/extendedcrafting.json",
    "craftingtweaks/grids/extendedcrafting_advanced.json",
    "craftingtweaks/grids/extendedcrafting_advanced_auto.json",
    "craftingtweaks/grids/extendedcrafting_auto.json",
    "craftingtweaks/grids/extendedcrafting_elite.json",
    "craftingtweaks/grids/extendedcrafting_elite_auto.json",
    "craftingtweaks/grids/extendedcrafting_ultimate.json",
    "craftingtweaks/grids/extendedcrafting_ultimate_auto.json",
    "craftingtweaks/grids/storagenetwork.json",
    "craftingtweaks/grids/toms_storage.json",
}
EXPECTED_DIRECT_CLASS_KEYS = {
    "tooltip.craftingtweaks.rotate",
    "tooltip.craftingtweaks.balance",
    "tooltip.craftingtweaks.spread",
    "tooltip.craftingtweaks.clear",
    "tooltip.craftingtweaks.forceClear",
    "tooltip.craftingtweaks.forceClearInfo",
}
EXPECTED_UNTRANSLATED = {"key.categories.craftingtweaks"}
GLOSSARY_ROWS = (
    "| Crafting Tweaks | Crafting Tweaks | 공식 모드명 |",
    "| Crafting Grid | 제작 칸 | 제작 UI 용어 |",
    "| Stack (items) | 한 묶음 | 아이템 수량 단위 |",
    "| Recipe Book | 제작법 책 | Minecraft UI 용어 |",
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
CONFIG_OPTION = re.compile(r"^\s*[A-Za-z0-9_]+\s*=", re.MULTILINE)
ENGLISH_LANGUAGE = re.compile(r"assets/[^/]+/lang/en_us\.json")
DIRECT_REFERENCE = re.compile(r"(?i)\bcrafting[ _-]?tweaks\b|craftingtweaks:")
RELATED_EXTENSIONS = {".js", ".json", ".snbt", ".toml", ".txt"}
FORBIDDEN_TRANSLATIONS = re.compile(
    r"스택 압축|스택 재보충|제작 가이드|제작 칸으로 전송|"
    r"마지막으로 사용한 아이템|비활성화된 애드온|한 묶음을 모두 제작|"
    r"필요하면 아이템을 버립니다|제작 칸 회전 \(반시계 방향\)"
)
REQUIRED_LITERALS = {
    "craftingtweaks.configuration.common.compressRequiresCraftingGrid.tooltip": (
        "false",
    ),
    "craftingtweaks.configuration.common.compressDenylist.tooltip": ("modid:name",),
    "craftingtweaks.configuration.client.rightClickCraftsStack.tooltip": ("true",),
    "craftingtweaks.configuration.client.hideVanillaCraftingGuide.tooltip": ("JEI",),
    "craftingtweaks.configuration.client.mode.tooltip": (
        "DEFAULT",
        "BUTTONS",
        "HOTKEYS",
        "DISABLED",
    ),
    "craftingtweaks.configuration.client.disabledAddons.tooltip": ("Crafting Tweaks",),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_language(data: bytes, label: str) -> dict[str, str]:
    duplicates: list[str] = []

    def reject_duplicate(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        return result

    value = json.loads(data.decode("utf-8-sig"), object_pairs_hook=reject_duplicate)
    if duplicates:
        raise ValueError(f"중복 JSON 키: {label}: {sorted(set(duplicates))}")
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise TypeError(f"문자열 언어 객체가 아닙니다: {label}")
    return value


def load_path(path: Path) -> dict[str, str]:
    return load_language(path.read_bytes(), str(path))


def find_related_files(root: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in RELATED_EXTENSIONS
        ),
        key=lambda path: path.as_posix(),
    )


def direct_references(root: Path, files: list[Path]) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in files
        if DIRECT_REFERENCE.search(
            path.read_text(encoding="utf-8-sig", errors="replace")
        )
    }


def verify_language_owners(instance: Path, english: dict[str, str]) -> tuple[int, int]:
    jar_count = 0
    language_count = 0
    conflicts: list[str] = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        jar_count += 1
        try:
            with ZipFile(jar_path) as archive:
                for name in archive.namelist():
                    if not ENGLISH_LANGUAGE.fullmatch(name):
                        continue
                    language_count += 1
                    if name == "assets/craftingtweaks/lang/en_us.json":
                        continue
                    value = json.loads(archive.read(name).decode("utf-8-sig"))
                    if not isinstance(value, dict):
                        continue
                    for key in set(english) & set(value):
                        if isinstance(value[key], str) and english[key] != value[key]:
                            conflicts.append(f"{jar_path.name}:{name}:{key}")
        except BadZipFile as error:
            raise RuntimeError(f"손상된 모드 JAR: {jar_path}") from error
    if conflicts:
        raise RuntimeError(f"다른 언어 소유자 충돌: {conflicts[:20]}")
    return jar_count, language_count


def verify(pre_apply: bool) -> dict[str, object]:
    instance = resolve_source_root(None)
    errors: list[str] = []
    source_jar = instance / "mods" / EXPECTED_JAR
    if sha256(source_jar) != EXPECTED_JAR_SHA256:
        errors.append("Crafting Tweaks 원본 JAR 해시가 변경되었습니다")
    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        english = load_language(
            archive.read("assets/craftingtweaks/lang/en_us.json"),
            "Crafting Tweaks en_us",
        )
        classes = [name for name in names if name.endswith(".class")]
        class_bytes = [archive.read(name) for name in classes]
        direct_class_keys = {
            key
            for key in english
            if any(key.encode("utf-8") in data for data in class_bytes)
        }
        language_files = [
            name
            for name in names
            if name.startswith("assets/craftingtweaks/lang/") and name.endswith(".json")
        ]
        korean_files = [name for name in language_files if name.endswith("/ko_kr.json")]
        grid_files = {
            name
            for name in names
            if name.startswith("craftingtweaks/grids/") and name.endswith(".json")
        }
        for name in grid_files:
            value = json.loads(archive.read(name).decode("utf-8-sig"))
            if not isinstance(value, dict):
                errors.append(f"제작 칸 연동 JSON 객체 아님: {name}")

    working = load_path(WORKING)
    output = load_path(OUTPUT)
    overrides = load_path(OVERRIDES)
    if len(names) != 150 or len(classes) != 101 or len(language_files) != 10:
        errors.append("Crafting Tweaks JAR 엔트리·클래스·언어 파일 수 불일치")
    if korean_files or len(english) != 40:
        errors.append("Crafting Tweaks 내장 한국어 또는 영어 키 수 불일치")
    if set(working) != set(english) or working != output:
        errors.append("Crafting Tweaks 작업본·산출물·영어 키 집합 불일치")
    if (
        len(overrides) != 24
        or sha256(OVERRIDES) != EXPECTED_OVERRIDE_SHA256
        or any(output.get(key) != value for key, value in overrides.items())
    ):
        errors.append("Crafting Tweaks 교정표 수·해시·반영값 불일치")
    if sha256(OUTPUT) != EXPECTED_OUTPUT_SHA256:
        errors.append("Crafting Tweaks 산출물 해시 불일치")
    untranslated = {key for key in english if english[key] == output[key]}
    if untranslated != EXPECTED_UNTRANSLATED:
        errors.append(f"Crafting Tweaks 원문 유지 키 불일치: {untranslated}")
    if direct_class_keys != EXPECTED_DIRECT_CLASS_KEYS:
        errors.append(f"Crafting Tweaks 직접 클래스 키 불일치: {direct_class_keys}")
    if grid_files != EXPECTED_GRID_FILES:
        errors.append(f"Crafting Tweaks 제작 칸 연동 파일 불일치: {grid_files}")
    for key in english:
        if PLACEHOLDER.findall(english[key]) != PLACEHOLDER.findall(output[key]):
            errors.append(f"자리표시자 불일치: {key}")
        if english[key].count("\n") != output[key].count("\n"):
            errors.append(f"줄바꿈 불일치: {key}")
        if Counter(FORMAT_CODE.findall(english[key])) != Counter(
            FORMAT_CODE.findall(output[key])
        ):
            errors.append(f"서식 코드 불일치: {key}")
    forbidden = FORBIDDEN_TRANSLATIONS.findall("\n".join(output.values()))
    if forbidden:
        errors.append(f"Crafting Tweaks 금지 번역 잔존: {sorted(set(forbidden))}")
    for key, literals in REQUIRED_LITERALS.items():
        for literal in literals:
            if literal not in output[key]:
                errors.append(f"Crafting Tweaks 리터럴 누락: {key}:{literal}")

    config = instance / "config/craftingtweaks-common.toml"
    config_text = config.read_text(encoding="utf-8-sig")
    config_options = len(CONFIG_OPTION.findall(config_text))
    if sha256(config) != EXPECTED_CONFIG_SHA256 or config_options != 8:
        errors.append("Crafting Tweaks 실제 설정 스냅샷 불일치")
    for phrase in (
        "(de)compress feature to work outside of crafting GUIs",
        "right-clicking the result slot",
        "hides Vanilla's crafting book button instead of moving it",
        "disable Crafting Tweaks support",
    ):
        if phrase not in config_text:
            errors.append(f"Crafting Tweaks 설정 의미 근거 누락: {phrase}")

    quest_files = find_related_files(instance / "config/ftbquests/quests")
    quest_refs = direct_references(instance, quest_files)
    kube_files = find_related_files(instance / "kubejs")
    kube_refs = direct_references(instance, kube_files)
    if len(quest_files) != 142 or quest_refs:
        errors.append(f"Crafting Tweaks FTB Quests 참조 불일치: {quest_refs}")
    if len(kube_files) != 892 or kube_refs:
        errors.append(f"Crafting Tweaks KubeJS 참조 불일치: {kube_refs}")

    jar_count, english_count = verify_language_owners(instance, english)
    project_languages = list(
        (active_output_root() / "resourcepack/ATM10_Korean/assets").glob(
            "*/lang/ko_kr.json"
        )
    )
    if jar_count != 480 or english_count != 388 or len(project_languages) != 285:
        errors.append(
            "설치·프로젝트 언어 집계 변경: "
            f"jars={jar_count}, english={english_count}, project={len(project_languages)}"
        )
    glossary = GLOSSARY.read_text(encoding="utf-8")
    for row in GLOSSARY_ROWS:
        if row not in glossary:
            errors.append(f"Crafting Tweaks 용어집 행 누락: {row}")

    if not pre_apply:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        if not isinstance(report, dict) or report.get("validation") != "passed":
            errors.append("Crafting Tweaks 재검수 보고서 상태 불일치")
        application = report.get("application") if isinstance(report, dict) else None
        if (
            not isinstance(application, dict)
            or application.get("status") != "applied_and_verified"
            or application.get("craftingtweaks_sha256") != EXPECTED_OUTPUT_SHA256
            or application.get("unexpected_changes") != 0
        ):
            errors.append("Crafting Tweaks 재검수 보고서 적용 집계 불일치")
        target = (
            instance
            / "resourcepacks/ATM10_Korean/assets/craftingtweaks/lang/ko_kr.json"
        )
        if not target.exists() or target.read_bytes() != OUTPUT.read_bytes():
            errors.append("실제 source_root의 Crafting Tweaks 산출물이 다릅니다")

    if errors:
        raise RuntimeError(
            "Crafting Tweaks 재검수 검증 실패:\n" + "\n".join(errors[:80])
        )
    return {
        "scope": "Crafting Tweaks 전체 번역 재검수",
        "source_jar": source_jar.name,
        "source_jar_sha256": sha256(source_jar),
        "source_jar_bytes": source_jar.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(classes),
        "language_files_reviewed": len(language_files),
        "source_keys_reviewed": len(english),
        "bundled_korean_candidates_reviewed": 0,
        "project_candidates_retained": len(english) - len(overrides),
        "project_candidates_corrected": len(overrides),
        "newly_translated": 0,
        "effective_output_keys": len(output),
        "direct_class_language_keys": len(direct_class_keys),
        "configuration_options_reviewed": config_options,
        "embedded_grid_integrations_reviewed": len(grid_files),
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_reference_files": len(quest_refs),
        "kubejs_files_reviewed": len(kube_files),
        "kubejs_reference_files": len(kube_refs),
        "installed_mod_jars_reviewed": jar_count,
        "installed_english_language_files_reviewed": english_count,
        "other_language_owner_conflicts": 0,
        "project_language_files_reviewed": len(project_languages),
        "glossary_terms_added": len(GLOSSARY_ROWS),
        "output_sha256": sha256(OUTPUT),
        "validation": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pre-apply", action="store_true")
    args = parser.parse_args()
    print(json.dumps(verify(args.pre_apply), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
