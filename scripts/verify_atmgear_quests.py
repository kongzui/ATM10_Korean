#!/usr/bin/env python3
"""Allthemodium·ATM 장비 관련 퀘스트와 fallback 표시 경로를 전수 검증한다."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import audit_ftbquests_titles as audit
import build_ae2_quests as snbt
import build_atmgear_quests as build
from atmgear_catalog import TARGETS
from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_atmgear import find_jar

REPORT_FILE = PROJECT_ROOT / "working/atmgear/quest_validation.json"
TARGET_NAMESPACES = {target.namespace for target in TARGETS}
OFFICIAL_EXACT = {"Allthemodium", "Vibranium", "Unobtainium", "The Beyond"}
SPECIAL_ITEM_KEYS = {
    "forbidden_arcanus:hephaestus_forge_tier_1": (
        "block.forbidden_arcanus.hephaestus_forge"
    ),
}
VANILLA_ITEM_NAMES = {"minecraft:netherite_ingot": "네더라이트 주괴"}


def component_literals(value: snbt.TranslationValue) -> list[str]:
    """설명 배열에서 JSON literal component 문자열을 찾는다."""
    if not isinstance(value, list):
        return []
    return [part for part in value if part.lstrip().startswith('{ "text"')]


def walk_components(value: object) -> tuple[list[str], list[str]]:
    """JSON 안의 translate 키와 literal text를 재귀 수집한다."""
    translate_keys: list[str] = []
    literals: list[str] = []
    if isinstance(value, dict):
        if isinstance(value.get("translate"), str):
            translate_keys.append(value["translate"])
        if isinstance(value.get("text"), str) and value["text"]:
            literals.append(value["text"])
        for child in value.values():
            left, right = walk_components(child)
            translate_keys.extend(left)
            literals.extend(right)
    elif isinstance(value, list):
        for child in value:
            left, right = walk_components(child)
            translate_keys.extend(left)
            literals.extend(right)
    return translate_keys, literals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    quest_root = instance / "config/ftbquests/quests"
    output = snbt.parse_language_snbt(build.OUTPUT_FILE)
    output_text = build.OUTPUT_FILE.read_text(encoding="utf-8")
    english = json.loads(build.ENGLISH_FILE.read_text(encoding="utf-8"))
    overrides = json.loads(build.OVERRIDES_FILE.read_text(encoding="utf-8"))
    errors: list[str] = []

    if build.OUTPUT_FILE.read_bytes().startswith(b"\xef\xbb\xbf"):
        errors.append("누적 ko_kr.snbt에 UTF-8 BOM이 있습니다.")
    duplicate_keys = sorted(
        key
        for key, count in Counter(snbt.ENTRY_RE.findall(output_text)).items()
        if count > 1
    )
    if duplicate_keys:
        errors.append(f"누적 ko_kr.snbt에 중복 키가 있습니다: {duplicate_keys}")
    if set(overrides) != set(english):
        errors.append("작업 번역 키 집합이 선택한 영어 표시 키와 다릅니다.")
    for key, source in english.items():
        if output.get(key) != overrides.get(key):
            errors.append(f"누적 출력값이 작업 번역과 다릅니다: {key}")
        else:
            errors.extend(build.validate_value(key, source, overrides[key]))
    if output.get(build.CHAPTER_TITLE_KEY) != "&a2장&r: &eAllthemodium":
        errors.append("Allthemodium 챕터 제목이 확정 번역과 다릅니다.")
    if output.get(build.GROUP_TITLE_KEY) != "주요 퀘스트라인":
        errors.append("관련 chapter group 제목이 번역되지 않았습니다.")

    chapters, _ = audit.parse_chapters(quest_root)
    dedicated = next(
        (chapter for chapter in chapters if chapter["filename"] == "allthemodium.snbt"),
        None,
    )
    if dedicated is None:
        errors.append("allthemodium.snbt 챕터 구조를 찾지 못했습니다.")
        dedicated = {"quests": [], "filename": ""}
    selected: list[tuple[dict[str, object], dict[str, object]]] = []
    for chapter in chapters:
        for quest in chapter["quests"]:
            if chapter is dedicated or quest["id"] in build.RELATED_QUEST_IDS:
                selected.append((chapter, quest))
    expected_cross = len(build.RELATED_QUEST_IDS)
    actual_cross = sum(quest["id"] in build.RELATED_QUEST_IDS for _, quest in selected)
    if actual_cross != expected_cross:
        errors.append(
            f"관련 챕터 퀘스트 선택 수가 다릅니다: {actual_cross}/{expected_cross}"
        )

    item_ids = {
        task["item_id"]
        for _, quest in selected
        for task in quest["tasks"]
        if task["item_id"]
    }
    installed_en, installed_ko, item_keys = audit.load_installed_item_languages(
        instance, item_ids
    )
    _, project_ko = audit.load_project_languages()
    item_keys.update(SPECIAL_ITEM_KEYS)

    def target_item_name(item_id: str) -> str:
        language_key = item_keys.get(item_id, "")
        return (
            project_ko.get(language_key, "")
            or installed_ko.get(language_key, "")
            or VANILLA_ITEM_NAMES.get(item_id, "")
        )

    fallback_checks = 0
    task_fallback_checks = 0
    resource_name_checks = 0
    explicit_task_titles = 0
    custom_names: list[dict[str, str]] = []
    untranslated_fallbacks: list[str] = []
    redundant_task_titles: list[str] = []

    for chapter, quest in selected:
        quest_key = f"quest.{quest['id']}.title"
        first_task = quest["tasks"][0] if quest["tasks"] else None
        title = audit.text_value(output, quest_key)
        if not title and first_task:
            task_key = f"task.{first_task['id']}.title"
            language_key = item_keys.get(first_task["item_id"], "")
            title = (
                audit.text_value(output, task_key)
                or first_task["custom_name"]
                or target_item_name(first_task["item_id"])
                or installed_en.get(language_key, "")
            )
            fallback_checks += 1
        plain_title = audit.strip_formatting(title)
        if quest["id"] != "552F0B9B00F4F914" and (
            not title
            or (audit.looks_untranslated(title) and plain_title not in OFFICIAL_EXACT)
        ):
            untranslated_fallbacks.append(
                f"{chapter['filename']}:{quest['id']}={title!r}"
            )

        if first_task and len(quest["tasks"]) == 1 and first_task["item_id"]:
            language_key = item_keys.get(first_task["item_id"], "")
            source_item = installed_en.get(language_key, "")
            target_item = target_item_name(first_task["item_id"])
            source_title = audit.strip_formatting(audit.text_value(english, quest_key))
            if source_item and source_title == source_item and target_item:
                resource_name_checks += 1
                if plain_title != target_item:
                    errors.append(
                        f"퀘스트와 리소스팩 아이템명이 다릅니다: {quest['id']} "
                        f"{plain_title!r}!={target_item!r}"
                    )

        for task in quest["tasks"]:
            task_key = f"task.{task['id']}.title"
            source_task_title = audit.text_value(english, task_key)
            target_task_title = audit.text_value(output, task_key)
            language_key = item_keys.get(task["item_id"], "")
            source_item = installed_en.get(language_key, "")
            target_item = target_item_name(task["item_id"])
            if task["custom_name"]:
                custom_names.append(
                    {
                        "quest": quest["id"],
                        "task": task["id"],
                        "value": task["custom_name"],
                    }
                )
            if source_task_title:
                explicit_task_titles += 1
                if (
                    task["item_id"]
                    and audit.strip_formatting(source_task_title) == source_item
                ):
                    redundant_task_titles.append(task["id"])
            elif task["item_id"]:
                task_fallback_checks += 1
                fallback = target_item or source_item
                namespace = task["item_id"].partition(":")[0]
                if namespace in TARGET_NAMESPACES and not project_ko.get(language_key):
                    errors.append(
                        f"대상 아이템 리소스팩 번역이 없습니다: {task['item_id']}"
                    )
                if not fallback or (
                    audit.looks_untranslated(fallback)
                    and fallback not in OFFICIAL_EXACT
                    and not project_ko.get(language_key)
                ):
                    errors.append(
                        f"Task 자동 아이템 fallback이 영어입니다: {chapter['filename']}:"
                        f"{quest['id']}:{task['id']}={fallback!r}"
                    )
            if target_task_title and audit.looks_untranslated(target_task_title):
                if task_key not in build.INTERNAL_KEYS:
                    errors.append(f"명시적 Task 제목이 영어입니다: {task_key}")

    if custom_names:
        errors.append(f"선택 퀘스트 Task에 custom_name이 있습니다: {custom_names}")
    if redundant_task_titles:
        errors.append(f"단순 ItemTask 중복 제목이 남았습니다: {redundant_task_titles}")
    if untranslated_fallbacks:
        errors.append(
            f"영어 또는 빈 quest fallback이 있습니다: {untranslated_fallbacks}"
        )

    literal_components = 0
    for key, source in english.items():
        source_literals = component_literals(source)
        target_literals = component_literals(overrides[key])
        if len(source_literals) != len(target_literals):
            errors.append(f"literal component 수가 다릅니다: {key}")
            continue
        for source_raw, target_raw in zip(
            source_literals, target_literals, strict=True
        ):
            source_component = json.loads(source_raw)
            target_component = json.loads(target_raw)
            source_text = source_component.pop("text")
            target_text = target_component.pop("text")
            if source_component != target_component:
                errors.append(f"literal component 구조가 바뀌었습니다: {key}")
            if source_text == target_text or not re.search(r"[가-힣]", target_text):
                errors.append(f"literal component가 번역되지 않았습니다: {key}")
            literal_components += 1

    advancement_files = 0
    advancement_translate_keys = 0
    advancement_literals = 0
    for target in TARGETS:
        jar_path = find_jar(instance, target)
        with ZipFile(jar_path) as archive:
            for name in archive.namelist():
                if not name.endswith(".json") or "/advancement" not in name:
                    continue
                value = json.loads(archive.read(name).decode("utf-8-sig"))
                keys, literals = walk_components(value)
                if keys or literals:
                    advancement_files += 1
                for key in keys:
                    advancement_translate_keys += 1
                    if key not in project_ko:
                        errors.append(f"발전 과제 번역 키가 없습니다: {name}:{key}")
                for literal in literals:
                    advancement_literals += 1
                    if re.search(r"[A-Za-z]{3,}", literal):
                        errors.append(
                            f"발전 과제에 영어 literal이 있습니다: {name}:{literal}"
                        )

    report = {
        "scope": "Allthemodium and ATM gear related FTB Quests",
        "dedicated_chapter": dedicated["filename"],
        "dedicated_quests_checked": len(dedicated["quests"]),
        "related_quests_outside_chapter_checked": actual_cross,
        "tasks_checked": sum(len(quest["tasks"]) for _, quest in selected),
        "display_keys_checked": len(english),
        "quest_fallbacks_checked": fallback_checks,
        "task_item_fallbacks_checked": task_fallback_checks,
        "explicit_task_titles_checked": explicit_task_titles,
        "resource_name_matches_checked": resource_name_checks,
        "custom_names": len(custom_names),
        "literal_components_checked": literal_components,
        "redundant_task_titles": len(redundant_task_titles),
        "advancement_files_checked": advancement_files,
        "advancement_translate_keys_checked": advancement_translate_keys,
        "advancement_literals": advancement_literals,
        "duplicate_keys": len(duplicate_keys),
        "untranslated_fallbacks": len(untranslated_fallbacks),
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
