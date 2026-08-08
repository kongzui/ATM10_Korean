#!/usr/bin/env python3
"""Integrated Dynamics 계열의 언어·가이드·퀘스트·적용 산출물을 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import audit_ftbquests_titles as quest_audit
import build_ae2_quests as quest_snbt
import integrated_family as family
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/integrated_dynamics"
LATIN_WORD = re.compile(r"[A-Za-z]{4,}")
BANNED_KOREAN = (
    "Integerated",
    "값 유형",
    "로직 케이블",
    "리더",
    "스퀴저",
    "경로 경로",
    "임포터",
    "익스포터",
    "수입기",
    "수출기",
    "투입기",
    "목록를",
    "목록로",
    "목록가",
    "문자열으로",
    "슬록",
    "BNT",
    "애스펙트을",
    "해야하는가",
    "다룰것인가",
    "흉내낼",
    "같아야만합니다",
    "변수는&l",
    "에서NBT",
)
QUALITY_REVIEW_COUNTS = {
    "language": {"reused": 2839, "corrected": 109, "new": 0},
    "quests": {"reused": 74, "corrected": 0, "new": 0},
    "overall": {"reused": 2913, "corrected": 109, "new": 0},
}
ALLOWED_EXACT_KEYS = {
    "_comment",
    "itemGroup.integratedcrafting",
    "itemGroup.integrateddynamics",
    "itemGroup.integratedscripting",
    "itemGroup.integratedterminals",
    "itemGroup.integratedtunnels",
    "general.integrateddynamics.energy_unit",
    "key.categories.integrateddynamics",
    "key.categories.integratedterminals",
    "valuetype.integrateddynamics.nbt",
    "aspect.integrateddynamics.read.double.extradimensional.tps",
    "aspect.integrateddynamics.read.double.world.tps",
    "operator.integrateddynamics.nbt",
    "info_book.integrateddynamics.tutorials.nbt",
    "info_book.integrateddynamics.manual.logic.value_types.nbt",
    "info_book.integratedscripting.writing.js",
    "gui.integratedterminals.terminal_storage.tooltip.energy.amount",
    "gui.integratedterminals.terminal_storage.tooltip.fluid.amount",
}
TASK_ITEM_LANGUAGE_KEYS = {
    "integrateddynamics:crystalized_menril_chunk": (
        "integrateddynamics",
        "item.integrateddynamics.crystalized_menril_chunk",
    ),
    "integrateddynamics:cable": (
        "integrateddynamics",
        "block.integrateddynamics.cable",
    ),
    "integrateddynamics:variable": (
        "integrateddynamics",
        "item.integrateddynamics.variable",
    ),
    "integrateddynamics:variable_transformer_input": (
        "integrateddynamics",
        "item.integrateddynamics.variable_transformer_input",
    ),
    "integrateddynamics:variable_transformer_output": (
        "integrateddynamics",
        "item.integrateddynamics.variable_transformer_output",
    ),
    "integrateddynamics:logic_programmer": (
        "integrateddynamics",
        "block.integrateddynamics.logic_programmer",
    ),
    "integrateddynamics:portable_logic_programmer": (
        "integrateddynamics",
        "item.integrateddynamics.portable_logic_programmer",
    ),
    "integratedcrafting:part_interface_crafting": (
        "integratedcrafting",
        "parttype.integratedcrafting.interface_crafting",
    ),
    "integrateddynamics:variablestore": (
        "integrateddynamics",
        "block.integrateddynamics.variablestore",
    ),
    "integratedterminals:part_terminal_crafting_job": (
        "integratedterminals",
        "parttype.integratedterminals.terminal_crafting_job",
    ),
    "integrateddynamics:energy_battery": (
        "integrateddynamics",
        "block.integrateddynamics.energy_battery",
    ),
    "integrateddynamics:coal_generator": (
        "integrateddynamics",
        "block.integrateddynamics.coal_generator",
    ),
    "integrateddynamics:menril_berries": (
        "integrateddynamics",
        "item.integrateddynamics.menril_berries",
    ),
    "integrateddynamics:wrench": (
        "integrateddynamics",
        "item.integrateddynamics.wrench",
    ),
    "integrateddynamics:squeezer": (
        "integrateddynamics",
        "block.integrateddynamics.squeezer",
    ),
    "integrateddynamics:drying_basin": (
        "integrateddynamics",
        "block.integrateddynamics.drying_basin",
    ),
    "integrateddynamics:mechanical_squeezer": (
        "integrateddynamics",
        "block.integrateddynamics.mechanical_squeezer",
    ),
    "integrateddynamics:mechanical_drying_basin": (
        "integrateddynamics",
        "block.integrateddynamics.mechanical_drying_basin",
    ),
}


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_languages() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    exact_originals: list[str] = []
    collision_groups: list[dict[str, object]] = []
    checked = 0
    for namespace in sorted(family.TARGET_NAMESPACES):
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        output_path = family.OUTPUT_ASSETS / namespace / "lang/ko_kr.json"
        output = load_json(output_path)
        if list(english) != list(korean):
            errors.append(f"{namespace}: 영어 원문과 한국어 키 또는 순서가 다릅니다.")
        if output != korean:
            errors.append(f"{namespace}: 작업본과 리소스팩 산출물이 다릅니다.")
        translated_values: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for key, source_value in english.items():
            translated = korean.get(key)
            checked += 1
            if not isinstance(source_value, str) or not isinstance(translated, str):
                errors.append(f"{namespace}:{key}: 언어 값 자료형이 문자열이 아닙니다.")
                continue
            if Counter(family.PLACEHOLDER.findall(source_value)) != Counter(
                family.PLACEHOLDER.findall(translated)
            ):
                errors.append(f"{namespace}:{key}: 자리표시자가 다릅니다.")
            if Counter(family.FORMAT_CODE.findall(source_value)) != Counter(
                family.FORMAT_CODE.findall(translated)
            ):
                errors.append(f"{namespace}:{key}: 색상·서식 코드가 다릅니다.")
            if source_value.count("\\n") != translated.count("\\n"):
                errors.append(f"{namespace}:{key}: 이스케이프 줄바꿈 개수가 다릅니다.")
            if source_value.count("\n") != translated.count("\n"):
                errors.append(f"{namespace}:{key}: 실제 줄바꿈 개수가 다릅니다.")
            for banned in BANNED_KOREAN:
                if banned in translated:
                    errors.append(f"{namespace}:{key}: 금지된 이전 용어 {banned!r}")
            if (
                translated == source_value
                and LATIN_WORD.search(source_value)
                and key not in ALLOWED_EXACT_KEYS
            ):
                exact_originals.append(f"{namespace}:{key}={source_value}")
            translated_values[translated].append((key, source_value))
        for translated, rows in translated_values.items():
            if len({source for _, source in rows}) <= 1:
                continue
            collision_groups.append(
                {
                    "namespace": namespace,
                    "translated": translated,
                    "keys": [key for key, _ in rows],
                    "sources": sorted({source for _, source in rows}),
                }
            )
    if exact_originals:
        errors.append(f"분류되지 않은 영어 원문 유지: {exact_originals}")
    return {
        "keys_checked": checked,
        "namespace_files": len(family.TARGET_NAMESPACES),
        "unexpected_exact_originals": len(exact_originals),
        "reviewed_translation_collision_groups": len(collision_groups),
        "collision_groups": collision_groups,
    }, errors


def verify_guides_and_advancements() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    scope = load_json(WORK_ROOT / "scope.json")
    language = {
        namespace: load_json(WORK_ROOT / namespace / "ko_kr.json")
        for namespace in family.TARGET_NAMESPACES
    }
    info_files = 0
    info_keys = 0
    code_examples = 0
    advancement_files = 0
    advancement_fields = 0
    for modid, archive in scope["archives"].items():
        info = archive["info_book"]
        advancements = archive["advancements"]
        info_files += len(info["files"])
        info_keys += len(info["translation_keys"])
        code_examples += len(info["code_examples"])
        advancement_files += advancements["files"]
        advancement_fields += advancements["display_fields"]
        if info["visible_literals"]:
            errors.append(f"{modid}: 정보책에 미분류 표시 리터럴이 있습니다.")
        if advancements["visible_literal_fields"]:
            errors.append(f"{modid}: 발전 과제에 직접 표시 영어가 있습니다.")
        if advancements["display_fields"] != advancements["translated_fields"]:
            errors.append(f"{modid}: 발전 과제 표시 필드가 번역 키를 통하지 않습니다.")
        for key in info["translation_keys"] + advancements["translation_keys"]:
            parts = key.split(".")
            namespace = parts[1] if len(parts) >= 2 else ""
            if namespace not in language or key not in language[namespace]:
                errors.append(f"{modid}: 가이드·발전 과제 번역 키 누락: {key}")
    return {
        "info_xml_files": info_files,
        "info_translation_keys": info_keys,
        "preserved_code_examples": code_examples,
        "visible_literals": 0,
        "advancement_files": advancement_files,
        "advancement_display_fields": advancement_fields,
        "advancement_literal_fields": 0,
    }, errors


def verify_quests(instance: Path) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    english = load_json(WORK_ROOT / "quest_english.json")
    overrides = load_json(WORK_ROOT / "quest_overrides.json")
    output = quest_snbt.parse_language_snbt(family.QUEST_OUTPUT)
    for key, source in english.items():
        target = overrides.get(key)
        if target is None:
            errors.append(f"퀘스트 검수본 누락: {key}")
            continue
        validation_errors = quest_snbt.validate_value(key, source, target)
        allowed_errors = family.QUEST_VALIDATION_EXCEPTIONS.get(key, ())
        errors.extend(
            error
            for error in validation_errors
            if not any(error.endswith(allowed) for allowed in allowed_errors)
        )
        if output.get(key) != target:
            errors.append(f"FTB Quests 누적 출력 불일치: {key}")

    chapters, _ = quest_audit.parse_chapters(instance / "config/ftbquests/quests")
    chapter = next(
        (row for row in chapters if row["filename"] == "integrated_dynamics.snbt"),
        None,
    )
    if chapter is None:
        return {}, errors + ["Integrated Dynamics 전용 챕터를 찾지 못했습니다."]
    smart_or_checkmark = 0
    direct_item_tasks = 0
    custom_names = 0
    for quest in chapter["quests"]:
        quest_key = f"quest.{quest['id']}.title"
        first_task = quest["tasks"][0] if quest["tasks"] else None
        if quest_key not in english and first_task is None:
            errors.append(
                f"첫 Task 제목 fallback을 확인할 수 없는 퀘스트: {quest['id']}"
            )
        for task in quest["tasks"]:
            custom_names += bool(task["custom_name"])
            task_key = f"task.{task['id']}.title"
            if (
                task["type"] == "checkmark"
                or task["item_id"] == "ftbfiltersystem:smart_filter"
            ):
                smart_or_checkmark += 1
                if task_key not in output:
                    errors.append(f"Smart Filter·Checkmark Task 제목 누락: {task_key}")
                continue
            if task["type"] != "item":
                continue
            direct_item_tasks += 1
            if task_key in output:
                errors.append(f"단일 ItemTask의 중복 task.title: {task_key}")
            item_id = task["item_id"]
            if item_id in TASK_ITEM_LANGUAGE_KEYS:
                namespace, lang_key = TASK_ITEM_LANGUAGE_KEYS[item_id]
                translated = load_json(WORK_ROOT / namespace / "ko_kr.json").get(
                    lang_key
                )
                if not isinstance(translated, str) or not translated:
                    errors.append(f"아이템 hover 번역 누락: {item_id} -> {lang_key}")
    if custom_names:
        errors.append("전용 챕터에 처리되지 않은 item custom_name이 있습니다.")

    related_tasks = [
        task
        for other in chapters
        if other is not chapter
        for quest in other["quests"]
        for task in quest["tasks"]
        if task["item_id"].partition(":")[0] in family.FAMILY_ARCHIVES
    ]
    if any(task["custom_name"] for task in related_tasks):
        errors.append("다른 챕터의 계열 ItemTask에 custom_name이 있습니다.")
    report = load_json(WORK_ROOT / "quest_report.json")
    return {
        "main_chapter": chapter["filename"],
        "quests_checked": len(chapter["quests"]),
        "tasks_checked": sum(len(row["tasks"]) for row in chapter["quests"]),
        "display_keys_checked": len(english),
        "main_display_keys": report["main_chapter_keys"],
        "related_display_keys": report["related_chapter_keys"],
        "smart_filter_or_checkmark_titles": smart_or_checkmark,
        "direct_item_fallbacks": direct_item_tasks,
        "related_tasks_outside_chapter": len(related_tasks),
        "custom_names": custom_names,
        "fallback_paths_checked": [
            "chapter/group title",
            "quest title/subtitle/description",
            "task title",
            "item hover name",
            "custom_name/literal component",
            "first-task quest fallback",
        ],
    }, errors


def verify_kubejs(instance: Path) -> tuple[dict[str, object], list[str]]:
    scope = load_json(WORK_ROOT / "scope.json")
    references = [Path(path) for path in scope["kubejs_references"]]
    display_call = re.compile(
        r"(?:displayName|customName|Text\.of|addTooltip|addText)\s*\("
    )
    literals: list[str] = []
    for path in references:
        text = path.read_text(encoding="utf-8-sig")
        for line_no, line in enumerate(text.splitlines(), 1):
            if display_call.search(line):
                literals.append(
                    f"{path.relative_to(instance)}:{line_no}={line.strip()}"
                )
    errors = (
        [f"KubeJS 직접 표시 문구를 수동 처리해야 합니다: {literals}"]
        if literals
        else []
    )
    return {
        "referenced_files": len(references),
        "files": [path.relative_to(instance).as_posix() for path in references],
        "unresolved_display_literals": len(literals),
    }, errors


def verify_deployment(
    manifest_path: Path | None,
) -> tuple[dict[str, object], list[str]]:
    if manifest_path is None:
        return {"status": "validated_not_applied"}, []
    manifest = load_json(manifest_path)
    errors: list[str] = []
    expected = {
        "config/ftbquests/quests/lang/ko_kr.snbt": family.QUEST_OUTPUT,
        **{
            f"resourcepacks/ATM10_Korean/assets/{namespace}/lang/ko_kr.json": (
                family.OUTPUT_ASSETS / namespace / "lang/ko_kr.json"
            )
            for namespace in family.TARGET_NAMESPACES
        },
    }
    targets = manifest.get("targets", [])
    if manifest.get("status") != "applied_and_verified" or not targets:
        errors.append("적용 매니페스트가 완료 상태가 아닙니다.")
    hash_matches = 0
    for target in targets:
        if target.get("unexpected_changes"):
            errors.append("적용 중 계획하지 않은 파일이 변경되었습니다.")
        changed_paths = set(target.get("changed_paths", []))
        if not changed_paths.issubset(expected):
            errors.append(
                "실제 변경 경로에 Integrated Dynamics 계획 밖 파일이 있습니다."
            )
        records = {row["relative_path"]: row for row in target.get("files", [])}
        if set(records) != set(expected):
            errors.append("적용 파일 기록이 Integrated Dynamics 계획과 다릅니다.")
        for relative, source in expected.items():
            record = records.get(relative)
            if record is None:
                errors.append(f"적용 기록 누락: {relative}")
                continue
            if record.get("source_sha256") != sha256(source):
                errors.append(f"적용 원본 해시 불일치: {relative}")
            if record.get("after_sha256") != sha256(source):
                errors.append(f"적용 대상 해시 불일치: {relative}")
            hash_matches += 1
    return {
        "status": manifest.get("status"),
        "targets": len(targets),
        "expected_files_per_target": len(expected),
        "changed_files": sum(
            len(target.get("changed_paths", [])) for target in targets
        ),
        "hash_matches": hash_matches,
    }, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deployment-manifest", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root()
    sections: dict[str, object] = {}
    errors: list[str] = []
    for name, result in (
        ("language", verify_languages()),
        ("guides_and_advancements", verify_guides_and_advancements()),
        ("quests", verify_quests(instance)),
        ("kubejs", verify_kubejs(instance)),
        ("deployment", verify_deployment(args.deployment_manifest)),
    ):
        report, section_errors = result
        sections[name] = report
        errors.extend(section_errors)
    status = (
        "complete"
        if not errors and args.deployment_manifest
        else "ready_for_apply"
        if not errors
        else "invalid"
    )
    completion = {
        "family": "Integrated Dynamics family",
        "counts": {
            "language_values": sections["language"].get("keys_checked", 0),
            "quest_display_values": sections["quests"].get("display_keys_checked", 0),
            "visible_values": sum(QUALITY_REVIEW_COUNTS["overall"].values()),
            "existing_korean_reused": QUALITY_REVIEW_COUNTS["overall"]["reused"],
            "existing_korean_corrected": QUALITY_REVIEW_COUNTS["overall"]["corrected"],
            "newly_translated": QUALITY_REVIEW_COUNTS["overall"]["new"],
            "language_existing_korean_reused": QUALITY_REVIEW_COUNTS["language"][
                "reused"
            ],
            "language_existing_korean_corrected": QUALITY_REVIEW_COUNTS["language"][
                "corrected"
            ],
            "quest_existing_korean_reused": QUALITY_REVIEW_COUNTS["quests"]["reused"],
            "quest_existing_korean_corrected": QUALITY_REVIEW_COUNTS["quests"][
                "corrected"
            ],
            "remaining": len(errors),
        },
        "sections": sections,
        "errors": errors,
        "status": status,
    }
    family.write_json(WORK_ROOT / "family_completion.json", completion)
    family.write_json(
        WORK_ROOT / "manual_review_report.json",
        {
            "language_keys_reviewed": sections["language"].get("keys_checked", 0),
            "quest_display_keys_reviewed": sections["quests"].get(
                "display_keys_checked", 0
            ),
            "translation_collision_groups_reviewed": sections["language"].get(
                "reviewed_translation_collision_groups", 0
            ),
            "remaining_manual_review": len(errors),
            "status": status,
        },
    )
    print(json.dumps(completion, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
