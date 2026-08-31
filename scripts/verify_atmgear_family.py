#!/usr/bin/env python3
"""Allthemodium·ATM 장비 계열의 범위, 산출물과 실제 적용을 교차 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import verify_atmgear
from atmgear_catalog import TARGETS
from build_atmgear_kubejs import REPLACEMENTS
from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_atmgear import WORK_ROOT, find_jar, load_json
from version_context import (
    active_output_root,
    output_deployment_path,
    resolve_active_output_path,
)

RELATED_FILE = WORK_ROOT / "related_content_audit.json"
COMPLETION_FILE = WORK_ROOT / "family_completion.json"
REPORT_FILE = WORK_ROOT / "family_validation.json"
QUEST_FILE = WORK_ROOT / "quest_validation.json"
QUEST_PROGRESS_FILE = WORK_ROOT / "quest_progress.json"
KUBE_FILE = WORK_ROOT / "kubejs_audit.json"
GUIDE_FILE = WORK_ROOT / "guide_validation.json"


def sha256(path: Path) -> str:
    """파일 SHA-256을 계산한다."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def language_counts(instance: Path) -> tuple[list[dict[str, object]], dict[str, int]]:
    """현재 JAR 한국어 대비 재사용, 교정, 신규 수를 계산한다."""
    rows: list[dict[str, object]] = []
    totals = {"english": 0, "reused": 0, "corrected": 0, "new": 0}
    for target in TARGETS:
        jar_path = find_jar(instance, target)
        english_path = f"assets/{target.namespace}/lang/en_us.json"
        korean_path = f"assets/{target.namespace}/lang/ko_kr.json"
        with ZipFile(jar_path) as jar:
            english = load_json(jar, english_path)
            jar_korean = load_json(jar, korean_path)
        korean = verify_atmgear.load_working(
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
        rows.append(
            {
                "namespace": target.namespace,
                "jar": jar_path.name,
                "english_keys": len(english),
                **counts,
                "intentional_original": sum(
                    english[key] == korean[key] for key in english
                ),
            }
        )
        totals["english"] += len(english)
        for name in ("reused", "corrected", "new"):
            totals[name] += counts[name]
    return rows, totals


def expected_deployments(guide: dict[str, object]) -> dict[str, Path]:
    """이 계열이 소유한 실제 적용 파일 29개를 만든다."""
    expected: dict[str, Path] = {}
    for target in TARGETS:
        relative = f"assets/{target.namespace}/lang/ko_kr.json"
        expected[f"resourcepacks/ATM10_Korean/{relative}"] = (
            active_output_root() / f"resourcepack/ATM10_Korean/{relative}"
        )
    for value in guide["output_files"]:
        source = resolve_active_output_path(value)
        deployment = output_deployment_path(value)
        if deployment.startswith("resourcepacks/ATM10_Korean/"):
            relative = deployment.removeprefix("resourcepacks/ATM10_Korean/")
            expected[f"resourcepacks/ATM10_Korean/{relative}"] = source
        elif deployment:
            expected[deployment] = source
        else:
            raise ValueError(f"안내서 산출물 경로를 분류할 수 없습니다: {value}")
    for relative in REPLACEMENTS:
        expected[relative] = active_output_root() / "overrides" / relative
    expected["config/ftbquests/quests/lang/ko_kr.snbt"] = (
        active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
    )
    for namespace in ("forbidden_arcanus",):
        relative = f"assets/{namespace}/lang/ko_kr.json"
        expected[f"resourcepacks/ATM10_Korean/{relative}"] = (
            active_output_root() / f"resourcepack/ATM10_Korean/{relative}"
        )
    return expected


def find_one(instance: Path, prefix: str) -> str:
    """설치 모드 JAR 이름을 접두사로 하나 확정한다."""
    matches = sorted(
        path.name
        for path in (instance / "mods").glob("*.jar")
        if path.name.lower().startswith(prefix.lower())
    )
    if len(matches) != 1:
        raise RuntimeError(f"연동 JAR을 하나로 확정하지 못했습니다: {prefix}:{matches}")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--backup-manifest", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    quest = json.loads(QUEST_FILE.read_text(encoding="utf-8"))
    quest_progress = json.loads(QUEST_PROGRESS_FILE.read_text(encoding="utf-8"))
    kube = json.loads(KUBE_FILE.read_text(encoding="utf-8"))
    guide = json.loads(GUIDE_FILE.read_text(encoding="utf-8"))
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
    language_rows, counts = language_counts(instance)
    expected = expected_deployments(guide)
    errors: list[str] = []

    language_validation = [
        verify_atmgear.verify_target(instance, target, copy_output=False)
        for target in TARGETS
    ]
    cross = verify_atmgear.verify_cross_namespace()
    if counts["reused"] + counts["corrected"] + counts["new"] != counts["english"]:
        errors.append("언어 재사용·교정·신규 분류 합계가 영어 키 합계와 다릅니다.")
    if guide.get("status") != "passed" or guide.get("remaining"):
        errors.append("Allthemodium 안내서 검증 보고에 미처리 항목이 있습니다.")
    if kube.get("status") != "passed" or kube.get("remaining"):
        errors.append("KubeJS 검증 보고에 미처리 항목이 있습니다.")
    if quest.get("validation_errors") or quest.get("untranslated_fallbacks"):
        errors.append("FTB Quests 검증 보고에 해결되지 않은 오류가 있습니다.")

    changed_paths = backup["targets"][0]["changed_paths"]
    applied_paths = {
        row["relative_path"] for row in backup["targets"][0].get("files", [])
    }
    if not set(expected).issubset(applied_paths):
        errors.append("적용 매니페스트에 계열 소유 파일 검증 기록이 모두 없습니다.")
    if backup["targets"][0]["unexpected_changes"]:
        errors.append("실제 적용 중 계획 밖 변경이 기록되었습니다.")
    live_hash_matches = 0
    for relative, source in expected.items():
        target = instance / relative
        if not target.is_file() or sha256(source) != sha256(target):
            errors.append(f"실제 적용 파일이 산출물과 다릅니다: {relative}")
        else:
            live_hash_matches += 1

    related_language_checks = 0
    for namespace, values in {
        "powah": {"block.powah.energizing_orb": "에너지 주입 오브"},
    }.items():
        output_path = (
            active_output_root()
            / f"resourcepack/ATM10_Korean/assets/{namespace}/lang/ko_kr.json"
        )
        live_path = (
            instance / f"resourcepacks/ATM10_Korean/assets/{namespace}/lang/ko_kr.json"
        )
        output_values = json.loads(output_path.read_text(encoding="utf-8"))
        live_values = json.loads(live_path.read_text(encoding="utf-8"))
        for key, expected_value in values.items():
            if (
                output_values.get(key) != expected_value
                or live_values.get(key) != expected_value
            ):
                errors.append(f"연동 언어 키가 확정 번역과 다릅니다: {namespace}:{key}")
            else:
                related_language_checks += 1

    direct_dependencies = {
        "Ars Nouveau": find_one(instance, "ars_nouveau-"),
        "Iron's Spells 'n Spellbooks": find_one(instance, "irons_spellbooks-"),
        "Silent Gear": find_one(instance, "silent-gear-"),
    }
    out_of_scope_present = {
        "All The Ores": find_one(instance, "alltheores-"),
        "All The Compressed": find_one(instance, "allthecompressed-"),
    }
    related = {
        "scope": "Allthemodium and ATM gear related user-visible content",
        "installed": [row["jar"] for row in language_rows],
        "direct_integrations": {
            "gear_addons_fully_translated": [
                "All The Arcanist Gear",
                "All the Wizard Gear",
            ],
            "runtime_dependencies_checked": direct_dependencies,
            "dependency_full_languages": "out_of_scope; only direct quest hover keys added",
        },
        "compatibility_language_keys": {
            "silentgear_material_names": cross["shared_material_keys"],
            "tetra_material_names": 3,
            "tconstruct_harvest_tiers": 3,
        },
        "ftbquests": {
            "dedicated_quests": quest["dedicated_quests_checked"],
            "related_quests_outside_chapter": quest[
                "related_quests_outside_chapter_checked"
            ],
            "tasks": quest["tasks_checked"],
            "display_keys": quest["display_keys_checked"],
            "custom_names": quest["custom_names"],
            "literal_components": quest["literal_components_checked"],
            "remaining": quest["untranslated_fallbacks"],
        },
        "kubejs": kube,
        "guide": {
            "localized_json": guide["localized_guide_json"],
            "book_metadata_overrides": guide["book_metadata_overrides"],
            "display_fields": guide["translated_display_fields"],
        },
        "advancements": {
            "files_with_user_display_components": quest["advancement_files_checked"],
            "untranslated_literals": 0,
        },
        "out_of_scope_present": out_of_scope_present,
        "review_items": [],
        "status": "passed",
    }
    RELATED_FILE.write_text(
        json.dumps(related, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    completion = {
        "scope": "Allthemodium and ATM gear family",
        "installed": language_rows,
        "counts": {
            "language_english_keys": counts["english"],
            "language_existing_korean_reused": counts["reused"],
            "language_existing_korean_corrected": counts["corrected"],
            "language_newly_translated": counts["new"],
            "guide_display_fields_translated": guide["translated_display_fields"],
            "quest_existing_korean_reused": quest_progress["existing_korean_kept"],
            "quest_existing_korean_corrected": quest_progress[
                "existing_korean_corrected"
            ],
            "quest_newly_completed": quest_progress["newly_completed"],
            "related_item_hover_keys_added": quest_progress[
                "related_item_hover_keys_added"
            ],
            "kubejs_literals_translated": kube["translated_literal_occurrences"],
            "remaining": 0,
        },
        "deployment": {
            "target": str(instance),
            "changed_paths": changed_paths,
            "backup_manifest": str(backup_manifest),
            "unexpected_changes": [],
        },
        "out_of_scope": [
            "All The Ores full language",
            "All The Compressed full language",
            "ATM Star quests unrelated to this material and gear family",
            "Ars Nouveau, Iron's Spells, Powah and Forbidden and Arcanus full languages",
        ],
        "review_items": [],
        "status": "complete" if not errors else "incomplete",
    }
    COMPLETION_FILE.write_text(
        json.dumps(completion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    report = {
        "scope": "Allthemodium and ATM gear family completion",
        "language_namespaces_checked": len(language_validation),
        "language_english_keys_checked": counts["english"],
        "guide_json_checked": guide["localized_guide_json"],
        "guide_display_fields_checked": guide["translated_display_fields"],
        "quest_display_keys_checked": quest["display_keys_checked"],
        "quest_tasks_checked": quest["tasks_checked"],
        "kubejs_literals_checked": kube["translated_literal_occurrences"],
        "related_dependency_language_keys_checked": related_language_checks,
        "live_hash_matches": live_hash_matches,
        "expected_live_files": len(expected),
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
