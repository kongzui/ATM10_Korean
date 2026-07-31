#!/usr/bin/env python3
"""The Twilight Forest 연동, 발전 과제, 표시 경로와 적용 상태를 검증한다."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
import twilight_family as quality_review
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/twilight_forest"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[&§][0-9A-FK-ORa-fk-or]")


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def find_jar(instance: Path, pattern: str, label: str) -> Path:
    """설치본에서 지정한 JAR 하나를 찾는다."""
    matches = sorted((instance / "mods").glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"{label} JAR 검색 결과가 하나가 아닙니다: {matches}")
    return matches[0]


def translated_collisions(
    english: dict[str, object], korean: dict[str, object]
) -> list[dict[str, object]]:
    """원문에서는 달랐지만 번역 후 같은 이름이 된 항목을 찾는다."""
    values: dict[str, list[str]] = defaultdict(list)
    for key, value in korean.items():
        if isinstance(value, str):
            values[value].append(key)
    collisions = []
    for value, keys in values.items():
        originals = {english.get(key) for key in keys}
        if len(keys) > 1 and len(originals) > 1:
            collisions.append({"translation": value, "keys": sorted(keys)})
    return collisions


def verify_bibliowoods(instance: Path) -> tuple[dict[str, object], list[str]]:
    """Bibliowoods의 Twilight Forest 직접 연동 키만 전수 검사한다."""
    jar = find_jar(instance, "bibliowoods-*.jar", "Bibliowoods")
    with ZipFile(jar) as archive:
        all_english = json.loads(
            archive.read("assets/bibliowoods/lang/en_us.json").decode("utf-8-sig")
        )
    scoped = {
        key: value for key, value in all_english.items() if "twilightforest" in key
    }
    working_english = load_json(WORK_ROOT / "bibliowoods/en_us.json")
    working_korean = load_json(WORK_ROOT / "bibliowoods/ko_kr.json")
    output_korean = load_json(OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json")
    errors = []
    if list(scoped.items()) != list(working_english.items()):
        errors.append("Bibliowoods 설치본 연동 키와 작업 원문이 다릅니다.")
    if any(output_korean.get(key) != value for key, value in working_korean.items()):
        errors.append("Bibliowoods 작업 번역과 누적 산출물이 다릅니다.")
    if set(working_korean) != set(scoped):
        errors.append("Bibliowoods 연동 번역 키 집합이 원문과 다릅니다.")
    untranslated = [key for key in scoped if scoped[key] == working_korean.get(key)]
    formatting = []
    for key, source in scoped.items():
        target = working_korean.get(key)
        if not isinstance(source, str) or not isinstance(target, str):
            formatting.append(key)
            continue
        if Counter(PLACEHOLDER.findall(source)) != Counter(
            PLACEHOLDER.findall(target)
        ) or Counter(FORMAT_CODE.findall(source)) != Counter(
            FORMAT_CODE.findall(target)
        ):
            formatting.append(key)
    collisions = translated_collisions(scoped, working_korean)
    if untranslated:
        errors.append("Bibliowoods 연동 영어 유지: " + " | ".join(untranslated[:30]))
    if formatting:
        errors.append(
            "Bibliowoods 자리표시자·서식 불일치: " + " | ".join(formatting[:30])
        )
    if collisions:
        errors.append(
            "Bibliowoods 번역 유발 이름 충돌: "
            + " | ".join(row["translation"] for row in collisions[:30])
        )
    return {
        "jar": jar.name,
        "all_english_keys": len(all_english),
        "twilight_forest_keys": len(scoped),
        "other_mod_keys_excluded": len(all_english) - len(scoped),
        "translated_keys": len(working_korean),
        "untranslated": len(untranslated),
        "formatting_errors": len(formatting),
        "translation_induced_name_collisions": len(collisions),
        "output_matches": all(
            output_korean.get(key) == value for key, value in working_korean.items()
        ),
    }, errors


def translations() -> dict[str, object]:
    """The Twilight Forest 본체의 확정 번역을 읽는다."""
    return load_json(OUTPUT_ASSETS / "twilightforest/lang/ko_kr.json")


def verify_lore_book() -> tuple[dict[str, object], list[str]]:
    """별도 가이드 시스템 대신 언어 파일에 포함된 탐험 수첩을 검사한다."""
    english = load_json(WORK_ROOT / "twilightforest/en_us.json")
    korean = translations()
    keys = sorted(key for key in english if key.startswith("twilightforest.book."))
    missing = [key for key in keys if key not in korean]
    untranslated = [key for key in keys if english[key] == korean.get(key)]
    errors = []
    if missing:
        errors.append("탐험 수첩 번역 키 누락: " + " | ".join(missing[:30]))
    if untranslated:
        errors.append("탐험 수첩 영어 유지: " + " | ".join(untranslated[:30]))
    return {
        "system": "언어 파일 기반 탐험 수첩",
        "external_guide_files": 0,
        "language_keys_checked": len(keys),
        "missing_translation_keys": len(missing),
        "untranslated_keys": len(untranslated),
    }, errors


def verify_advancements(instance: Path) -> tuple[dict[str, object], list[str]]:
    """발전 과제 표시 필드가 확정 번역 키를 사용하는지 검사한다."""
    jar = find_jar(instance, "twilightforest-*.jar", "The Twilight Forest")
    catalog = translations()
    files = 0
    fields = 0
    empty_literals = 0
    literals: list[str] = []
    missing: list[str] = []
    with ZipFile(jar) as archive:
        names = [
            name
            for name in archive.namelist()
            if name.startswith("data/twilightforest/advancement/")
            and name.endswith(".json")
        ]
        files = len(names)
        for name in names:
            data = json.loads(archive.read(name).decode("utf-8-sig"))
            display = data.get("display", {})
            if not isinstance(display, dict):
                continue
            for field in ("title", "description"):
                shown = display.get(field)
                if shown is None:
                    continue
                fields += 1
                if isinstance(shown, str):
                    if shown:
                        literals.append(f"{name}:{field}:{shown}")
                    else:
                        empty_literals += 1
                elif isinstance(shown, dict) and isinstance(
                    shown.get("translate"), str
                ):
                    key = shown["translate"]
                    if key not in catalog:
                        missing.append(f"{name}:{key}")
    errors = []
    if literals:
        errors.append("발전 과제 literal 표시 문구: " + " | ".join(literals[:30]))
    if missing:
        errors.append("발전 과제 번역 키 누락: " + " | ".join(missing[:30]))
    return {
        "files_checked": files,
        "display_fields": fields,
        "empty_literal_fields": empty_literals,
        "visible_literal_fields": len(literals),
        "missing_translation_keys": len(missing),
    }, errors


def verify_kubejs(instance: Path) -> tuple[dict[str, object], list[str]]:
    """KubeJS의 Twilight Forest 참조와 직접 표시 문자열 후보를 전수 분류한다."""
    family = re.compile(r"twilightforest|twilight_forest", re.IGNORECASE)
    display = re.compile(
        r"displayName|tooltip|Text\.(?:of|literal)|custom_name|\bname\s*:",
        re.IGNORECASE,
    )
    references: list[str] = []
    candidates: list[str] = []
    root = instance / "kubejs"
    for path in sorted(root.rglob("*")):
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
        errors.append("KubeJS 직접 표시 문자열 후보: " + " | ".join(candidates[:30]))
    return {
        "files_referencing_family": len(references),
        "referenced_paths": references,
        "direct_display_candidates": len(candidates),
    }, errors


def verify_quality_review() -> tuple[dict[str, object], list[str]]:
    """품질 재검수 확정값과 금지된 번역기식 표현이 없는지 검사한다."""
    english = load_json(WORK_ROOT / "twilightforest/en_us.json")
    korean = translations()
    sources = load_json(WORK_ROOT / "twilightforest/candidate_sources.json")
    errors: list[str] = []
    missing_overrides = sorted(
        set(quality_review.QUALITY_LANGUAGE_OVERRIDES) - set(english)
    )
    mismatched_overrides = sorted(
        key
        for key, expected in quality_review.QUALITY_LANGUAGE_OVERRIDES.items()
        if key in english
        and korean.get(key) != quality_review.normalize_quality_value(expected)
    )
    if missing_overrides:
        errors.append(
            "품질 검수 언어 키가 원문에 없음: " + " | ".join(missing_overrides[:30])
        )
    if mismatched_overrides:
        errors.append(
            "품질 검수 확정값 불일치: " + " | ".join(mismatched_overrides[:30])
        )

    quest_output = quest_snbt.parse_language_snbt(
        PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
    )
    missing_quest_overrides = sorted(
        set(quality_review.QUALITY_QUEST_OVERRIDES) - set(quest_output)
    )
    mismatched_quest_overrides = sorted(
        key
        for key, expected in quality_review.QUALITY_QUEST_OVERRIDES.items()
        if key in quest_output and quest_output[key] != expected
    )
    if missing_quest_overrides:
        errors.append(
            "품질 검수 퀘스트 키가 산출물에 없음: "
            + " | ".join(missing_quest_overrides[:30])
        )
    if mismatched_quest_overrides:
        errors.append(
            "품질 검수 퀘스트 확정값 불일치: "
            + " | ".join(mismatched_quest_overrides[:30])
        )

    forbidden = (
        "속 속 빈 언덕",
        "가스트유체",
        "로얄 좀비",
        "팬텀 기사",
        "기사 팬텀",
        "황혼의 지배",
        "무장의 지배",
        "불사의 지배",
        "생명의 지배",
        "지도 집중체",
        "지도 깃털",
        "구현 블록",
        "은폐 블록",
        "창 막기",
        "매야플",
        "미네우드",
        "돌 트위스트",
        "지방이",
        "극지동물의 털",
        "리버뿌리",
        "횃불딸기",
        "할로우 힐",
        "퀘스트 양",
        "광석 미터",
        "[Home]",
        "[Fast]",
        "탈출하는 동안",
        "가스트링가",
        "기사 유령가",
        "홀가",
        "홀를",
    )
    scoped_values = [value for value in korean.values() if isinstance(value, str)]
    for root in sorted((WORK_ROOT / "quests").glob("*")):
        path = root / "ko_kr.json"
        if not path.is_file():
            continue
        for value in load_json(path).values():
            scoped_values.extend(value if isinstance(value, list) else [value])
    forbidden_hits = sorted(
        phrase
        for phrase in forbidden
        if any(phrase in value for value in scoped_values)
    )
    if forbidden_hits:
        errors.append("금지된 번역기식 표현 잔존: " + " | ".join(forbidden_hits))

    quality_keys = sum(source == "manual_quality_review" for source in sources.values())
    if quality_keys == 0:
        errors.append("품질 재검수 출처로 기록된 언어 키가 없습니다.")
    return {
        "language_keys_checked": len(english),
        "quality_language_overrides": len(quality_review.QUALITY_LANGUAGE_OVERRIDES),
        "manual_quality_review_keys": quality_keys,
        "quest_keys_checked": sum(
            len(load_json(path)) for path in (WORK_ROOT / "quests").glob("*/ko_kr.json")
        ),
        "quality_quest_overrides": len(quality_review.QUALITY_QUEST_OVERRIDES),
        "forbidden_phrases_checked": len(forbidden),
        "forbidden_phrase_hits": forbidden_hits,
    }, errors


def sha256(path: Path) -> str:
    """파일 SHA-256을 계산한다."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def deployment_report(instance: Path) -> dict[str, object]:
    """가장 최근 적용 기록과 실제 파일에서 관련 산출물의 해시를 검사한다."""
    manifests = sorted(
        (PROJECT_ROOT / "temp/backups").glob("*/backup_manifest.json"),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )
    if not manifests:
        return {"status": "not_applied", "files_checked": 0, "hash_matches": 0}
    manifest_path = manifests[0]
    manifest = load_json(manifest_path)
    targets = manifest.get("targets", [])
    expected = (
        (
            PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt",
            instance / "config/ftbquests/quests/lang/ko_kr.snbt",
        ),
        (
            OUTPUT_ASSETS / "twilightforest/lang/ko_kr.json",
            instance
            / "resourcepacks/ATM10_Korean/assets/twilightforest/lang/ko_kr.json",
        ),
        (
            OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json",
            instance / "resourcepacks/ATM10_Korean/assets/bibliowoods/lang/ko_kr.json",
        ),
    )
    matches = sum(
        source.is_file() and target.is_file() and sha256(source) == sha256(target)
        for source, target in expected
    )
    target_manifest = targets[0] if isinstance(targets, list) and targets else {}
    if not isinstance(target_manifest, dict):
        target_manifest = {}
    return {
        "status": "applied_and_verified" if matches == len(expected) else "incomplete",
        "target": str(instance),
        "backup_manifest": manifest_path.relative_to(PROJECT_ROOT).as_posix(),
        "files_checked": len(expected),
        "hash_matches": matches,
        "unexpected_changes": target_manifest.get("unexpected_changes", []),
    }


def verify(instance: Path) -> tuple[dict[str, object], int]:
    """모든 관련 표시 경로를 검사해 단계 완료 보고서를 만든다."""
    errors: list[str] = []
    core = load_json(WORK_ROOT / "language_validation.json")
    if core.get("status") != "complete":
        errors.append("언어·FTB Quests 핵심 검증이 완료되지 않았습니다.")
    bibliowoods, found = verify_bibliowoods(instance)
    errors.extend(found)
    lore_book, found = verify_lore_book()
    errors.extend(found)
    advancements, found = verify_advancements(instance)
    errors.extend(found)
    kubejs, found = verify_kubejs(instance)
    errors.extend(found)
    quality, found = verify_quality_review()
    errors.extend(found)
    deployment = deployment_report(instance)
    if deployment.get("status") != "applied_and_verified":
        errors.append(
            "The Twilight Forest 산출물이 실제 설치본에 아직 적용되지 않았습니다."
        )
    report = {
        "family": "The Twilight Forest",
        "language_provenance": core.get("language_provenance", {}),
        "ftbquests": core.get("ftbquests", {}),
        "direct_integration": {"Bibliowoods": bibliowoods},
        "guide_and_lore": lore_book,
        "advancements": advancements,
        "kubejs": kubejs,
        "quality_review": quality,
        "deployment": deployment,
        "validation_errors": len(errors),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "family_completion.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report, 1 if errors else 0


def main() -> int:
    report, status = verify(resolve_source_root())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
