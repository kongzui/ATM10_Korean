#!/usr/bin/env python3
"""Deeper and Darker와 모든 직접 표시 경로의 완성 산출물을 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
import deeper_and_darker_family
import deeper_and_darker_language
import deeper_and_darker_quests
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/deeper_and_darker"
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"
OUTPUT_OVERRIDES = active_output_root() / "overrides"
QUEST_OUTPUT = OUTPUT_OVERRIDES / "config/ftbquests/quests/lang/ko_kr.snbt"
EXPECTED_JAR = "deeperdarker-neoforge-1.21.1-1.4.1.jar"
EXPECTED_JAR_SIZE = 3_906_057
EXPECTED_JAR_SHA256 = "eee3f51222b0bcc714def002ff089ac9e131d3cae4575b542fd0a7dd101fe0af"
EXPECTED_KUBEJS_PATHS = {
    "kubejs/client_scripts/tooltips.js",
    "kubejs/data/hostilenetworks/data_models/warden.json",
    "kubejs/server_scripts/modpack/att_items.js",
    "kubejs/server_scripts/mods/minecraft/recipes.js",
    "kubejs/server_scripts/Tweaks/recipes_fix.js",
    "kubejs/server_scripts/Unification/ingots.js",
    "kubejs/server_scripts/Unification/sawing.js",
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def sha256(path: Path) -> str:
    """파일의 SHA-256 해시를 계산한다."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_one(root: Path, pattern: str, label: str) -> Path:
    """패턴과 일치하는 현재 설치 파일 하나를 찾는다."""
    matches = sorted(root.glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"{label} 검색 결과가 하나가 아닙니다: {matches}")
    return matches[0]


def verify_current_language(instance: Path) -> tuple[dict[str, object], list[str]]:
    """현재 JAR 영어 원문과 369개 검수 산출물의 일치를 검사한다."""
    jar = find_one(instance / "mods", "deeperdarker-*.jar", "Deeper and Darker JAR")
    english = load_json(WORK_ROOT / "deeperdarker/en_us.json")
    korean = load_json(WORK_ROOT / "deeperdarker/ko_kr.json")
    sources = load_json(WORK_ROOT / "deeperdarker/candidate_sources.json")
    output_path = OUTPUT_ASSETS / "deeperdarker/lang/ko_kr.json"
    output = load_json(output_path)
    with ZipFile(jar) as archive:
        current = json.loads(
            archive.read("assets/deeperdarker/lang/en_us.json").decode("utf-8-sig")
        )
        bundled = json.loads(
            archive.read("assets/deeperdarker/lang/ko_kr.json").decode("utf-8-sig")
        )
    errors = []
    current_hash = sha256(jar)
    if jar.name != EXPECTED_JAR:
        errors.append(f"현재 JAR 이름이 예상과 다릅니다: {jar.name}")
    if jar.stat().st_size != EXPECTED_JAR_SIZE:
        errors.append(f"현재 JAR 크기가 예상과 다릅니다: {jar.stat().st_size}")
    if current_hash != EXPECTED_JAR_SHA256:
        errors.append(f"현재 JAR SHA-256이 예상과 다릅니다: {current_hash}")
    if list(current.items()) != list(english.items()):
        errors.append("작업 영어 원문이 현재 설치 JAR과 다릅니다.")
    if list(korean.items()) != list(output.items()):
        errors.append("검수 작업본과 리소스팩 산출물이 다릅니다.")
    if list(english) != list(korean) or list(english) != list(sources):
        errors.append("영어·한국어·출처 키 또는 순서가 서로 다릅니다.")
    if "unresolved" in sources.values():
        errors.append("미해결 언어 키가 남았습니다.")
    mismatches = [
        key
        for key, source in english.items()
        if deeper_and_darker_language.translate_name(str(source)) != korean.get(key)
    ]
    if mismatches:
        errors.append(
            "검수 번역 규칙과 언어 산출물이 다릅니다: " + str(mismatches[:20])
        )
    for key, source in english.items():
        errors.extend(family_goal.validate_value(key, source, korean[key]))
    return {
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_sha256": current_hash,
        "english_keys": len(english),
        "bundled_korean_candidates": len(bundled),
        "korean_keys": len(korean),
        "output_matches_working_copy": korean == output,
        "review_sources": dict(Counter(sources.values())),
        "output_sha256": sha256(output_path),
    }, errors


def verify_advancements_and_guides(
    instance: Path,
) -> tuple[dict[str, object], list[str]]:
    """발전 과제 표시 키와 가이드 부재를 현재 JAR에서 다시 검사한다."""
    report = deeper_and_darker_family.audit_advancements()
    jar = find_one(instance / "mods", "deeperdarker-*.jar", "Deeper and Darker JAR")
    with ZipFile(jar) as archive:
        guides = [
            name
            for name in archive.namelist()
            if any(
                marker in name.lower()
                for marker in (
                    "patchouli_books/",
                    "ae2guide/",
                    "modonomicon/",
                    "/books/",
                )
            )
            and name.endswith((".json", ".md", ".xml"))
        ]
    errors = []
    if report != {
        "advancement_files": 263,
        "displayed_advancements": 11,
        "display_fields": 22,
        "translate_references": 22,
        "unique_translate_keys": 22,
        "literal_display_texts": [],
        "missing_translation_keys": [],
        "guide_candidates": 0,
    }:
        errors.append(f"발전 과제 표시 범위가 확정값과 다릅니다: {report}")
    if guides:
        errors.append("예상하지 않은 내장 가이드가 있습니다: " + str(guides[:20]))
    report["embedded_guide_files"] = len(guides)
    return report, errors


def verify_bibliowoods(instance: Path) -> tuple[dict[str, object], list[str]]:
    """BiblioWoods 직접 연동 314개와 이전 2,983개 보존을 검사한다."""
    jar = find_one(instance / "mods", "bibliowoods-*.jar", "BiblioWoods JAR")
    with ZipFile(jar) as archive:
        all_english = json.loads(
            archive.read("assets/bibliowoods/lang/en_us.json").decode("utf-8-sig")
        )
    current = {
        key: value for key, value in all_english.items() if "deeperdarker" in key
    }
    english = load_json(WORK_ROOT / "integrations/bibliowoods/en_us.json")
    korean = load_json(WORK_ROOT / "integrations/bibliowoods/ko_kr.json")
    output_path = OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json"
    output = load_json(output_path)
    prior: dict[str, object] = {}
    for path in (
        PROJECT_ROOT / "working/twilight_forest/bibliowoods/ko_kr.json",
        PROJECT_ROOT / "working/undergarden/bibliowoods/ko_kr.json",
        PROJECT_ROOT / "working/aether/bibliowoods/ko_kr.json",
        PROJECT_ROOT / "working/eternal_starlight/integrations/bibliowoods/ko_kr.json",
    ):
        prior.update(load_json(path))
    errors = []
    if len(current) != 314 or list(current.items()) != list(english.items()):
        errors.append(
            "현재 BiblioWoods Deeper and Darker 원문 314개와 범위가 다릅니다."
        )
    if set(korean) != set(english):
        errors.append("BiblioWoods 작업 영어·한국어 키가 다릅니다.")
    for key, source in english.items():
        errors.extend(family_goal.validate_value(key, source, korean[key]))
        if output.get(key) != korean[key]:
            errors.append(f"BiblioWoods 직접 연동 누적 출력 불일치: {key}")
    prior_mismatches = [key for key, value in prior.items() if output.get(key) != value]
    if len(prior) != 2983 or prior_mismatches:
        errors.append(
            f"BiblioWoods 이전 범위 보존 실패: {len(prior)}/2983, "
            f"불일치={prior_mismatches[:20]}"
        )
    if len(output) != 3297:
        errors.append(f"BiblioWoods 누적 출력 키가 예상과 다릅니다: {len(output)}/3297")
    return {
        "jar": jar.name,
        "direct_keys_checked": len(current),
        "prior_keys_preserved": len(prior),
        "merged_output_keys": len(output),
        "output_sha256": sha256(output_path),
    }, errors


def verify_kubejs(instance: Path) -> tuple[dict[str, object], list[str]]:
    """KubeJS 참조 7개와 사용자 표시 리터럴 1개를 검사한다."""
    references = {
        str(row["path"]) for row in deeper_and_darker_family.scan_kube_references()
    }
    errors = []
    if references != EXPECTED_KUBEJS_PATHS:
        errors.append(
            "KubeJS 참조 경로가 예상과 다릅니다: "
            f"누락={sorted(EXPECTED_KUBEJS_PATHS - references)}, "
            f"추가={sorted(references - EXPECTED_KUBEJS_PATHS)}"
        )
    relative = deeper_and_darker_family.KUBE_RELATIVE
    source = instance / relative
    output = OUTPUT_OVERRIDES / relative
    source_text = source.read_text(encoding="utf-8")
    output_text = output.read_text(encoding="utf-8")
    old = deeper_and_darker_family.KUBE_OLD
    new = deeper_and_darker_family.KUBE_NEW
    source_is_english = source_text.count(old) == 1 and source_text.count(new) == 0
    source_is_applied = source_text.count(old) == 0 and source_text.count(new) == 1
    valid = (
        (source_is_english or source_is_applied)
        and output_text.count(old) == 0
        and output_text.count(new) == 1
    )
    if not valid:
        errors.append("KubeJS 식물 화분 표시 문구 치환이 맞지 않습니다.")
    return {
        "files_referencing_family": len(references),
        "referenced_paths": sorted(references),
        "direct_literal_overrides": 1,
        "source_state": "applied" if source_is_applied else "english",
        "output_sha256": sha256(output),
    }, errors


def verify_quests(instance: Path) -> tuple[dict[str, object], list[str]]:
    """전용·관련 FTB Quests 97개와 fallback Task 제목 2개를 검사한다."""
    report, errors = family_goal.verify_quests(instance, "deeper_and_darker")
    output = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    fallback = load_json(WORK_ROOT / "quests/fallback/ko_kr.json")
    mismatches = [key for key, value in fallback.items() if output.get(key) != value]
    if fallback != deeper_and_darker_quests.EXTRA_FALLBACK_TITLES:
        errors.append("명시적 fallback 작업본이 검수 번역표와 다릅니다.")
    if len(fallback) != 2 or mismatches:
        errors.append(
            f"명시적 Task fallback 제목이 맞지 않습니다: {len(fallback)}/2, "
            f"불일치={mismatches}"
        )
    report["source_display_keys_reviewed"] = 97
    report["explicit_fallback_task_titles"] = len(fallback)
    report["merged_keys_checked"] = 97 + len(fallback)
    return report, errors


def verify_live(instance: Path) -> tuple[dict[str, object], list[str]]:
    """실제 인스턴스의 네 적용 파일과 저장소 산출물 해시를 비교한다."""
    pairs = {
        "deeperdarker": (
            OUTPUT_ASSETS / "deeperdarker/lang/ko_kr.json",
            instance / "resourcepacks/ATM10_Korean/assets/deeperdarker/lang/ko_kr.json",
        ),
        "bibliowoods": (
            OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json",
            instance / "resourcepacks/ATM10_Korean/assets/bibliowoods/lang/ko_kr.json",
        ),
        "ftbquests": (
            QUEST_OUTPUT,
            instance / "config/ftbquests/quests/lang/ko_kr.snbt",
        ),
        "tooltips": (
            OUTPUT_OVERRIDES / deeper_and_darker_family.KUBE_RELATIVE,
            instance / deeper_and_darker_family.KUBE_RELATIVE,
        ),
    }
    rows = {}
    errors = []
    for label, (source, target) in pairs.items():
        source_hash = sha256(source)
        target_hash = sha256(target) if target.is_file() else None
        matches = source_hash == target_hash
        rows[label] = {
            "source_sha256": source_hash,
            "live_sha256": target_hash,
            "matches": matches,
        }
        if not matches:
            errors.append(f"실제 적용 파일 해시가 다릅니다: {label}")
    return rows, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-live", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root()
    generic, generic_code = family_goal.verify(instance, "deeper_and_darker")
    report: dict[str, object] = {"generic": generic}
    errors = list(generic["errors"]) if generic_code else []
    for label, verifier in (
        ("language", verify_current_language),
        ("advancements_and_guides", verify_advancements_and_guides),
        ("bibliowoods", verify_bibliowoods),
        ("kubejs", verify_kubejs),
        ("ftbquests", verify_quests),
    ):
        row, found = verifier(instance)
        report[label] = row
        errors.extend(found)
    if args.require_live:
        live, live_errors = verify_live(instance)
        report["live_parity"] = live
        errors.extend(live_errors)
    report["validation_errors"] = len(errors)
    report["errors"] = errors
    report["status"] = "complete" if not errors else "incomplete"
    path = WORK_ROOT / "family_validation.json"
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if args.require_live and not errors:
        completion = {
            "family": "Deeper and Darker",
            "status": "complete",
            "language_keys": 369,
            "bundled_reviewed_reuse": 113,
            "new_or_edited_language": 247,
            "kept_original_names": 9,
            "bibliowoods_keys": 314,
            "quest_display_keys": 97,
            "fallback_task_titles": 2,
            "kubejs_literal_overrides": 1,
            "live_files_verified": 4,
        }
        (WORK_ROOT / "family_completion.json").write_text(
            json.dumps(completion, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
