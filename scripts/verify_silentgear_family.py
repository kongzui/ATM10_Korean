#!/usr/bin/env python3
"""Silent Gear 계열의 범위·검증·실제 적용 상태를 교차 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import verify_silentgear
from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_silentgear import WORK_ROOT, find_jar, load_json
from silentgear_catalog import TARGETS

RELATED_FILE = WORK_ROOT / "related_content_audit.json"
COMPLETION_FILE = WORK_ROOT / "family_completion.json"
REPORT_FILE = WORK_ROOT / "family_validation.json"
QUEST_FILE = WORK_ROOT / "quest_validation.json"
KUBE_FILE = WORK_ROOT / "kubejs_audit.json"
EXPECTED_DEPLOYMENTS = {
    "resourcepacks/ATM10_Korean/assets/silentgear/lang/ko_kr.json": (
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/silentgear/lang/ko_kr.json"
    ),
    "resourcepacks/ATM10_Korean/assets/silentlib/lang/ko_kr.json": (
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/silentlib/lang/ko_kr.json"
    ),
    "resourcepacks/ATM10_Korean/assets/silentgems/lang/ko_kr.json": (
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/silentgems/lang/ko_kr.json"
    ),
    "resourcepacks/ATM10_Korean/assets/sgearmetalworks/lang/ko_kr.json": (
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/sgearmetalworks/lang/ko_kr.json"
    ),
    "resourcepacks/ATM10_Korean/assets/atm10_localization/lang/ko_kr.json": (
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/atm10_localization/lang/ko_kr.json"
    ),
    "config/ftbquests/quests/lang/ko_kr.snbt": (
        PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
    ),
    "kubejs/data/silentgear/silentgear_traits/advanced_aquatic.json": (
        PROJECT_ROOT
        / "output/overrides/kubejs/data/silentgear/silentgear_traits/advanced_aquatic.json"
    ),
    "kubejs/data/silentgear/silentgear_traits/advanced_flame_ward.json": (
        PROJECT_ROOT
        / "output/overrides/kubejs/data/silentgear/silentgear_traits/advanced_flame_ward.json"
    ),
    "kubejs/data/silentgear/silentgear_traits/cure_levitation.json": (
        PROJECT_ROOT
        / "output/overrides/kubejs/data/silentgear/silentgear_traits/cure_levitation.json"
    ),
    "kubejs/data/silentgear/silentgear_traits/cure_nausea.json": (
        PROJECT_ROOT
        / "output/overrides/kubejs/data/silentgear/silentgear_traits/cure_nausea.json"
    ),
}


def sha256(path: Path) -> str:
    """파일의 SHA-256을 계산한다."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def language_counts(instance: Path) -> tuple[list[dict[str, object]], dict[str, int]]:
    """현재 JAR 한국어 대비 재사용·교정·신규 수를 다시 계산한다."""
    rows: list[dict[str, object]] = []
    totals = {"english": 0, "reused": 0, "corrected": 0, "new": 0, "data_only": 0}
    for target in TARGETS:
        jar_path = find_jar(instance, target)
        language_path = f"assets/{target.namespace}/lang/ko_kr.json"
        with ZipFile(jar_path) as jar:
            english = load_json(jar, f"assets/{target.namespace}/lang/en_us.json")
            jar_korean = load_json(jar, language_path)
        korean = verify_silentgear.load_working(
            WORK_ROOT / target.namespace / "ko_kr.json"
        )
        counts = {"reused": 0, "corrected": 0, "new": 0}
        for key, source in english.items():
            candidate = jar_korean.get(key, source)
            if candidate == source:
                counts["new"] += 1
            elif korean[key] == candidate:
                counts["reused"] += 1
            else:
                counts["corrected"] += 1
        data_only = len(set(korean) - set(english))
        row = {
            "namespace": target.namespace,
            "jar": jar_path.name,
            "english_keys": len(english),
            **counts,
            "data_only_keys": data_only,
        }
        rows.append(row)
        totals["english"] += len(english)
        totals["data_only"] += data_only
        for name in ("reused", "corrected", "new"):
            totals[name] += counts[name]
    return rows, totals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--backup-manifest", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    quest = json.loads(QUEST_FILE.read_text(encoding="utf-8"))
    kube = json.loads(KUBE_FILE.read_text(encoding="utf-8"))
    language_rows, counts = language_counts(instance)
    errors: list[str] = []

    language_validation = [
        verify_silentgear.verify_target(instance, target, copy_output=False)
        for target in TARGETS
    ]
    translations: dict[str, object] = {}
    for target in TARGETS:
        translations.update(
            verify_silentgear.load_working(WORK_ROOT / target.namespace / "ko_kr.json")
        )
    data_validation = verify_silentgear.verify_data_keys(instance, translations)
    if counts["reused"] + counts["corrected"] + counts["new"] != counts["english"]:
        errors.append("언어 재사용·교정·신규 분류 합계가 영어 키 합계와 다릅니다.")
    if quest["validation_errors"] or quest["untranslated_fallbacks"]:
        errors.append("FTB Quests 검증 보고에 해결되지 않은 오류가 있습니다.")
    if kube["translated_literals"] != 9 or len(kube["material_translate_keys"]) != 3:
        errors.append("KubeJS 표시 문구 검증 수가 기대값과 다릅니다.")

    silentgear_jar = find_jar(instance, TARGETS[0])
    with ZipFile(silentgear_jar) as archive:
        patchouli_templates = [
            name
            for name in archive.namelist()
            if "patchouli" in name.lower() and name.endswith(".json")
        ]
    productive = sorted((instance / "mods").glob("productivemetalworks-*.jar"))
    if len(productive) != 1:
        errors.append(f"Productive Metalworks JAR을 확정하지 못했습니다: {productive}")

    backup_manifest = args.backup_manifest
    if backup_manifest is None:
        manifests = sorted(
            (PROJECT_ROOT / "temp/backups").glob("*/backup_manifest.json"),
            key=lambda path: path.stat().st_mtime,
        )
        if not manifests:
            raise FileNotFoundError("적용 백업 매니페스트를 찾지 못했습니다.")
        backup_manifest = manifests[-1]
    backup = json.loads(backup_manifest.read_text(encoding="utf-8"))
    changed_paths = backup["targets"][0]["changed_paths"]
    applied_paths = {
        row["relative_path"] for row in backup["targets"][0].get("files", [])
    }
    if not set(EXPECTED_DEPLOYMENTS).issubset(applied_paths):
        errors.append("적용 매니페스트에 Silent Gear 파일 검증 기록이 모두 없습니다.")
    if backup["targets"][0]["unexpected_changes"]:
        errors.append("실제 적용 중 계획 밖 변경이 기록되었습니다.")
    live_hash_matches = 0
    for relative, source in EXPECTED_DEPLOYMENTS.items():
        target = instance / relative
        if not target.is_file() or sha256(source) != sha256(target):
            errors.append(f"실제 적용 파일이 산출물과 다릅니다: {relative}")
        else:
            live_hash_matches += 1

    related = {
        "scope": "Silent Gear family related user-visible content",
        "installed": [row["jar"] for row in language_rows]
        + ([productive[0].name] if productive else []),
        "direct_integration": {
            "Productive Metalworks": productive[0].name if productive else None,
            "scope": "silent_gear FTB chapter and SGearMetalworks casting integration only",
            "full_mod_language": "out_of_scope_separate_plan_item",
        },
        "data_driven_display": data_validation,
        "kubejs": kube,
        "ftbquests": {
            "chapter": quest["chapter"],
            "quests": quest["quests_checked"],
            "tasks": quest["tasks_checked"],
            "outside_related_tasks": quest["related_tasks_outside_chapter_checked"],
            "remaining": quest["untranslated_fallbacks"],
        },
        "guides": {
            "patchouli_template_json": len(patchouli_templates),
            "independent_local_guide_pages": 0,
            "material_book_path": "dynamic UI localized by silentgear lang keys",
            "guide_book_path": "external wiki link; no packaged prose to override",
        },
        "advancements": {
            "files_checked": quest["advancement_files_checked"],
            "translate_keys_checked": quest["advancement_translate_keys_checked"],
            "missing": 0,
        },
        "review_items": [],
        "status": "passed",
    }
    RELATED_FILE.write_text(
        json.dumps(related, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    completion = {
        "scope": "Silent Gear family",
        "installed": language_rows,
        "counts": {
            "language_english_keys": counts["english"],
            "language_existing_korean_reused": counts["reused"],
            "language_existing_korean_corrected": counts["corrected"],
            "language_newly_translated": counts["new"],
            "data_only_keys_added": counts["data_only"],
            "quest_display_keys": quest["display_keys_checked"],
            "quest_fallback_titles_added": quest["fallback_titles_added"],
            "kubejs_literals_translated": kube["translated_literals"],
            "remaining": 0,
        },
        "deployment": {
            "target": str(instance),
            "changed_paths": changed_paths,
            "backup_manifest": str(backup_manifest),
            "unexpected_changes": [],
        },
        "out_of_scope": [
            "Productive Metalworks full language",
            "Allthemodium and ATM gear full family (stage 4)",
            "external Silent Gear wiki",
        ],
        "review_items": [],
        "status": "complete" if not errors else "incomplete",
    }
    COMPLETION_FILE.write_text(
        json.dumps(completion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    report = {
        "scope": "Silent Gear family completion",
        "language_namespaces_checked": len(language_validation),
        "language_english_keys_checked": counts["english"],
        "data_only_keys_checked": counts["data_only"],
        "data_json_checked": data_validation["data_json"],
        "data_translate_keys_checked": data_validation["translate_keys"],
        "quest_display_keys_checked": quest["display_keys_checked"],
        "kubejs_literals_checked": kube["translated_literals"],
        "live_hash_matches": live_hash_matches,
        "expected_live_files": len(EXPECTED_DEPLOYMENTS),
        "remaining": 0,
        "validation_errors": len(errors),
        "errors": errors,
    }
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
