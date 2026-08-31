#!/usr/bin/env python3
"""The Undergarden 본체와 직접 연동 표시 경로의 완성 산출물을 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
import five_family_goal as family_goal
import undergarden_family as quality_review
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/undergarden"
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"
QUEST_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없이 JSON을 기록한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    """파일의 SHA-256 해시를 계산한다."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_one(root: Path, pattern: str, label: str) -> Path:
    """현재 설치본에서 패턴과 일치하는 파일 하나를 찾는다."""
    matches = sorted(root.glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"{label} 검색 결과가 하나가 아닙니다: {matches}")
    return matches[0]


def translated_collisions(
    english: dict[str, object], korean: dict[str, object]
) -> list[dict[str, object]]:
    """서로 다른 영어 이름이 번역 때문에 같은 이름이 된 경우를 찾는다."""
    values: dict[str, list[str]] = defaultdict(list)
    for key, value in korean.items():
        if isinstance(value, str):
            values[value].append(key)
    rows = []
    for value, keys in values.items():
        originals = {english.get(key) for key in keys}
        if len(keys) > 1 and len(originals) > 1:
            rows.append({"translation": value, "keys": sorted(keys)})
    return rows


def verify_language_source(instance: Path) -> tuple[dict[str, object], list[str]]:
    """작업 영어 원문이 현재 설치된 JAR과 정확히 같은지 확인한다."""
    jar = find_one(instance / "mods", "The_Undergarden-*.jar", "The Undergarden JAR")
    english = load_json(WORK_ROOT / "undergarden/en_us.json")
    korean = load_json(WORK_ROOT / "undergarden/ko_kr.json")
    output = load_json(OUTPUT_ASSETS / "undergarden/lang/ko_kr.json")
    with ZipFile(jar) as archive:
        current = json.loads(
            archive.read("assets/undergarden/lang/en_us.json").decode("utf-8-sig")
        )
    errors = []
    if list(current.items()) != list(english.items()):
        errors.append("작업 영어 원문이 현재 설치 JAR과 다릅니다.")
    if list(korean.items()) != list(output.items()):
        errors.append("검수 작업본과 The Undergarden 리소스팩 산출물이 다릅니다.")
    return {
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_sha256": sha256(jar),
        "english_keys": len(english),
        "korean_keys": len(korean),
        "source_matches_installed_jar": english == current,
        "output_matches_working_copy": korean == output,
        "output_sha256": sha256(OUTPUT_ASSETS / "undergarden/lang/ko_kr.json"),
    }, errors


def verify_advancements(instance: Path) -> tuple[dict[str, object], list[str]]:
    """발전 과제 표시 요소가 번역 키를 거쳐 표시되는지 검사한다."""
    jar = find_one(instance / "mods", "The_Undergarden-*.jar", "The Undergarden JAR")
    catalog = load_json(OUTPUT_ASSETS / "undergarden/lang/ko_kr.json")
    files = 0
    display_fields = 0
    empty_literals = 0
    visible_literals: list[str] = []
    missing: list[str] = []
    with ZipFile(jar) as archive:
        names = [
            name
            for name in archive.namelist()
            if name.endswith(".json")
            and name.startswith(
                ("data/undergarden/advancement/", "data/undergarden/advancements/")
            )
        ]
        files = len(names)
        for name in names:
            data = json.loads(archive.read(name).decode("utf-8-sig"))
            display = data.get("display") if isinstance(data, dict) else None
            if not isinstance(display, dict):
                continue
            for field in ("title", "description"):
                shown = display.get(field)
                if shown is None:
                    continue
                display_fields += 1
                if isinstance(shown, str):
                    if shown:
                        visible_literals.append(f"{name}:{field}:{shown}")
                    else:
                        empty_literals += 1
                elif isinstance(shown, dict):
                    key = shown.get("translate")
                    if isinstance(key, str) and key not in catalog:
                        missing.append(f"{name}:{field}:{key}")
    errors = []
    if files != 377:
        errors.append(f"발전 과제 파일 수가 예상과 다릅니다: {files}/377")
    if display_fields != 74:
        errors.append(f"발전 과제 표시 필드 수가 예상과 다릅니다: {display_fields}/74")
    if visible_literals:
        errors.append(
            "번역 불가능한 발전 과제 직접 문구가 있습니다: "
            + " | ".join(visible_literals[:20])
        )
    if missing:
        errors.append("발전 과제 번역 키가 빠졌습니다: " + " | ".join(missing[:20]))
    return {
        "files_checked": files,
        "display_fields_checked": display_fields,
        "empty_literal_fields": empty_literals,
        "visible_literal_fields": len(visible_literals),
        "missing_translation_keys": len(missing),
    }, errors


def verify_guides(instance: Path) -> tuple[dict[str, object], list[str]]:
    """JAR 안의 별도 가이드 또는 Patchouli 표시 경로 존재 여부를 검사한다."""
    jar = find_one(instance / "mods", "The_Undergarden-*.jar", "The Undergarden JAR")
    candidates = []
    with ZipFile(jar) as archive:
        for name in archive.namelist():
            lower = name.lower()
            if not lower.endswith((".json", ".snbt", ".txt", ".md")):
                continue
            if "patchouli_books/" in lower or re.search(r"(^|/)(book|guide)s?/", lower):
                candidates.append(name)
    errors = []
    if candidates:
        errors.append(
            "별도 가이드 표시 경로를 수동 검토해야 합니다: "
            + " | ".join(candidates[:20])
        )
    return {
        "separate_guide_candidates": len(candidates),
        "candidate_paths": candidates,
        "display_path": "모드 언어 파일 및 FTB Quests",
    }, errors


def verify_kubejs(instance: Path) -> tuple[dict[str, object], list[str]]:
    """KubeJS 참조와 직접 표시 문구 후보를 분리한다."""
    family = re.compile(r"undergarden", re.IGNORECASE)
    display = re.compile(
        r"displayName|tooltip|Text\.(?:of|literal)|custom_name|\bname\s*:",
        re.IGNORECASE,
    )
    references: list[str] = []
    candidates: list[str] = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".js",
            ".json",
            ".snbt",
            ".md",
            ".txt",
        }:
            continue
        relative = path.relative_to(instance).as_posix()
        if "/lang/" in relative:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        if not family.search(text):
            continue
        references.append(relative)
        for number, line in enumerate(text.splitlines(), 1):
            if family.search(line) and display.search(line):
                candidates.append(f"{relative}:{number}:{line.strip()}")
    errors = []
    if candidates:
        errors.append(
            "KubeJS 직접 표시 문구 후보가 있습니다: " + " | ".join(candidates[:20])
        )
    return {
        "files_referencing_family": len(references),
        "referenced_paths": references,
        "direct_display_candidates": len(candidates),
    }, errors


def verify_bibliowoods(instance: Path) -> tuple[dict[str, object], list[str]]:
    """BiblioWoods의 The Undergarden 목재 연동 471개 키를 전수 검사한다."""
    jar = find_one(instance / "mods", "bibliowoods-*.jar", "BiblioWoods JAR")
    with ZipFile(jar) as archive:
        all_english = json.loads(
            archive.read("assets/bibliowoods/lang/en_us.json").decode("utf-8-sig")
        )
    scoped = {key: value for key, value in all_english.items() if "undergarden" in key}
    english = load_json(WORK_ROOT / "bibliowoods/en_us.json")
    korean = load_json(WORK_ROOT / "bibliowoods/ko_kr.json")
    output = load_json(OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json")
    twilight = load_json(WORK_ROOT.parent / "twilight_forest/bibliowoods/ko_kr.json")
    errors = []
    if list(scoped.items()) != list(english.items()):
        errors.append("BiblioWoods 설치본 연동 키와 작업 원문이 다릅니다.")
    if set(korean) != set(scoped):
        errors.append("BiblioWoods 연동 번역 키 집합이 원문과 다릅니다.")
    if any(output.get(key) != value for key, value in korean.items()):
        errors.append("BiblioWoods 연동 번역과 누적 산출물이 다릅니다.")
    if any(output.get(key) != value for key, value in twilight.items()):
        errors.append(
            "기존 The Twilight Forest BiblioWoods 번역이 보존되지 않았습니다."
        )
    untranslated = [key for key in scoped if scoped[key] == korean.get(key)]
    formatting = []
    for key, source in scoped.items():
        target = korean.get(key)
        if not isinstance(source, str) or not isinstance(target, str):
            formatting.append(key)
            continue
        if Counter(PLACEHOLDER.findall(source)) != Counter(
            PLACEHOLDER.findall(target)
        ) or Counter(FORMAT_CODE.findall(source)) != Counter(
            FORMAT_CODE.findall(target)
        ):
            formatting.append(key)
    collisions = translated_collisions(scoped, korean)
    if untranslated:
        errors.append("BiblioWoods 연동 영어 유지: " + " | ".join(untranslated[:20]))
    if formatting:
        errors.append("BiblioWoods 서식 불일치: " + " | ".join(formatting[:20]))
    if collisions:
        errors.append("BiblioWoods 번역 유발 이름 충돌이 있습니다.")
    return {
        "jar": jar.name,
        "all_english_keys": len(all_english),
        "undergarden_keys": len(scoped),
        "translated_keys": len(korean),
        "existing_twilight_forest_keys_preserved": len(twilight),
        "merged_output_keys": len(output),
        "untranslated": len(untranslated),
        "formatting_errors": len(formatting),
        "translation_induced_name_collisions": len(collisions),
    }, errors


def verify_productive_bees(instance: Path) -> tuple[dict[str, object], list[str]]:
    """Productive Bees의 직접 연동 언어 8개와 퀘스트 4개를 검사한다."""
    jar = find_one(instance / "mods", "productivebees-*.jar", "Productive Bees JAR")
    with ZipFile(jar) as archive:
        english = json.loads(
            archive.read("assets/productivebees/lang/en_us.json").decode("utf-8-sig")
        )
    working = load_json(
        PROJECT_ROOT / "working/productivebees/productivebees/ko_kr.json"
    )
    output = load_json(OUTPUT_ASSETS / "productivebees/lang/ko_kr.json")
    quest_output = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    errors = []
    missing_source = [
        key for key in quality_review.PRODUCTIVE_BEES if key not in english
    ]
    language_mismatch = [
        key
        for key, value in quality_review.PRODUCTIVE_BEES.items()
        if working.get(key) != value or output.get(key) != value
    ]
    quest_mismatch = [
        key
        for key, value in quality_review.PRODUCTIVE_QUESTS.items()
        if quest_output.get(key) != value
    ]
    if missing_source:
        errors.append(
            "Productive Bees 설치본 연동 원문 키가 빠졌습니다: "
            + " | ".join(missing_source)
        )
    if language_mismatch:
        errors.append(
            "Productive Bees 연동 언어 산출물이 다릅니다: "
            + " | ".join(language_mismatch)
        )
    if quest_mismatch:
        errors.append(
            "Productive Bees 연동 퀘스트 산출물이 다릅니다: "
            + " | ".join(quest_mismatch)
        )
    return {
        "jar": jar.name,
        "language_keys_checked": len(quality_review.PRODUCTIVE_BEES),
        "quest_keys_checked": len(quality_review.PRODUCTIVE_QUESTS),
        "missing_source_keys": len(missing_source),
        "language_mismatches": len(language_mismatch),
        "quest_mismatches": len(quest_mismatch),
    }, errors


def verify_live(
    instance: Path, require_live: bool
) -> tuple[dict[str, object], list[str]]:
    """완성 산출물과 실제 적용 파일의 해시 일치를 확인한다."""
    pairs = {
        "undergarden_language": (
            OUTPUT_ASSETS / "undergarden/lang/ko_kr.json",
            instance / "resourcepacks/ATM10_Korean/assets/undergarden/lang/ko_kr.json",
        ),
        "bibliowoods_integration": (
            OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json",
            instance / "resourcepacks/ATM10_Korean/assets/bibliowoods/lang/ko_kr.json",
        ),
        "productivebees_integration": (
            OUTPUT_ASSETS / "productivebees/lang/ko_kr.json",
            instance
            / "resourcepacks/ATM10_Korean/assets/productivebees/lang/ko_kr.json",
        ),
        "ftbquests_language": (
            QUEST_OUTPUT,
            instance / "config/ftbquests/quests/lang/ko_kr.snbt",
        ),
    }
    rows = {}
    errors = []
    for label, (source, target) in pairs.items():
        source_hash = sha256(source)
        target_hash = sha256(target) if target.is_file() else None
        matches = source_hash == target_hash
        rows[label] = {
            "source": source.relative_to(PROJECT_ROOT).as_posix(),
            "target": target.relative_to(instance).as_posix(),
            "source_sha256": source_hash,
            "target_sha256": target_hash,
            "matches": matches,
        }
        if require_live and not matches:
            errors.append(f"실제 적용 파일이 산출물과 다릅니다: {label}")
    return rows, errors


def verify(require_live: bool) -> tuple[dict[str, object], int]:
    """전체 검증 결과를 보고서로 저장한다."""
    instance = resolve_source_root()
    generic, generic_code = family_goal.verify(instance, "undergarden")
    sections = {}
    errors: list[str] = []
    for name, function in (
        ("language_source", verify_language_source),
        ("advancements", verify_advancements),
        ("guides", verify_guides),
        ("kubejs", verify_kubejs),
        ("bibliowoods", verify_bibliowoods),
        ("productive_bees", verify_productive_bees),
    ):
        report, found = function(instance)
        sections[name] = report
        errors.extend(found)
    live, found = verify_live(instance, require_live)
    sections["live_parity"] = live
    errors.extend(found)
    if generic_code:
        errors.extend(str(value) for value in generic.get("errors", []))
    report = {
        "family": "The Undergarden",
        "installed_source": instance.as_posix(),
        "require_live_parity": require_live,
        "generic_validation": generic,
        **sections,
        "validation_errors": len(errors),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    completion = {
        "family": "The Undergarden",
        "status": report["status"],
        "language_keys": 679,
        "ftbquest_display_keys": generic.get("ftbquests", {}).get(
            "display_keys_checked", 0
        ),
        "bibliowoods_direct_integration_keys": 471,
        "productive_bees_direct_integration_keys": 12,
        "guide_candidates": sections["guides"]["separate_guide_candidates"],
        "kubejs_direct_display_candidates": sections["kubejs"][
            "direct_display_candidates"
        ],
        "live_parity_required": require_live,
    }
    write_json(WORK_ROOT / "family_completion.json", completion)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report, 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-live", action="store_true")
    args = parser.parse_args()
    _, code = verify(args.require_live)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
