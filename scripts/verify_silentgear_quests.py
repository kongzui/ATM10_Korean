#!/usr/bin/env python3
"""Silent Gear 계열 FTB Quests와 fallback 표시 경로를 전수 검증한다."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import audit_ftbquests_titles as audit
import build_ae2_quests as snbt
import build_silentgear_quests as build
from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_silentgear import find_jar
from silentgear_catalog import TARGETS

REPORT_FILE = PROJECT_ROOT / "working/silentgear/quest_validation.json"
TARGET_NAMESPACES = {"silentgear", "silentgems", "sgearmetalworks"}
INTERNAL_QUESTS = {"769D5DE66D13B256"}
DYNAMIC_ITEM_TITLES = {
    "silentgear:elytra_blueprint": "겉날개 청사진",
    "silentgear:coating_blueprint": "코팅 청사진",
    "silentgear:grip_blueprint": "손잡이 청사진",
    "silentgear:binding_blueprint": "결속재 청사진",
    "silentgear:lining_blueprint": "안감 청사진",
    "silentgear:fletching_blueprint": "화살깃 청사진",
    "silentgear:mace_blueprint": "철퇴 청사진",
}


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
    expected = set(english) | set(build.FALLBACK_TITLES)
    if set(overrides) != expected:
        errors.append(
            "작업 JSON의 표시 키 집합이 원문과 fallback 계획에 맞지 않습니다."
        )
    for key, source in english.items():
        if output.get(key) != overrides.get(key):
            errors.append(f"누적 출력값이 작업 번역과 다릅니다: {key}")
        else:
            errors.extend(build.validate_value(key, source, overrides[key]))
    for key, value in build.FALLBACK_TITLES.items():
        if output.get(key) != value:
            errors.append(f"명시적 quest fallback 제목이 없습니다: {key}")

    chapters, _ = audit.parse_chapters(quest_root)
    target = next(
        (chapter for chapter in chapters if chapter["filename"] == "silent_gear.snbt"),
        None,
    )
    if target is None:
        errors.append("silent_gear.snbt 챕터 구조를 찾지 못했습니다.")
        target = {"quests": [], "filename": ""}
    outside_tasks = [
        (chapter, quest, task)
        for chapter in chapters
        if chapter is not target
        for quest in chapter["quests"]
        for task in quest["tasks"]
        if task["item_id"].partition(":")[0] in TARGET_NAMESPACES
    ]
    item_ids = {
        task["item_id"]
        for quest in target["quests"]
        for task in quest["tasks"]
        if task["item_id"]
    } | {task["item_id"] for _, _, task in outside_tasks}
    installed_en, installed_ko, item_keys = audit.load_installed_item_languages(
        instance, item_ids
    )
    _, project_ko = audit.load_project_languages()

    fallback_checks = 0
    resource_name_checks = 0
    explicit_task_titles = 0
    custom_names: list[dict[str, str]] = []
    untranslated_fallbacks: list[str] = []
    for quest in target["quests"]:
        quest_key = f"quest.{quest['id']}.title"
        first_task = quest["tasks"][0] if quest["tasks"] else None
        title = audit.text_value(output, quest_key)
        if not title and first_task:
            task_key = f"task.{first_task['id']}.title"
            language_key = item_keys.get(first_task["item_id"], "")
            title = (
                audit.text_value(output, task_key)
                or first_task["custom_name"]
                or DYNAMIC_ITEM_TITLES.get(first_task["item_id"], "")
                or project_ko.get(language_key, "")
                or installed_ko.get(language_key, "")
                or installed_en.get(language_key, "")
            )
            fallback_checks += 1
        if quest["id"] not in INTERNAL_QUESTS and (
            not title or audit.looks_untranslated(title)
        ):
            untranslated_fallbacks.append(f"{quest['id']}={title!r}")

        if first_task and len(quest["tasks"]) == 1 and first_task["item_id"]:
            language_key = item_keys.get(first_task["item_id"], "")
            source_item = installed_en.get(language_key, "")
            target_item = project_ko.get(language_key, "")
            source_title = audit.text_value(english, quest_key)
            if source_item and source_title == source_item and target_item:
                resource_name_checks += 1
                if audit.strip_formatting(title) != target_item:
                    errors.append(
                        f"퀘스트와 리소스팩 아이템명이 다릅니다: {quest['id']}"
                    )

        for task in quest["tasks"]:
            if task["custom_name"]:
                custom_names.append(
                    {
                        "quest": quest["id"],
                        "task": task["id"],
                        "value": task["custom_name"],
                    }
                )
            if audit.text_value(english, f"task.{task['id']}.title"):
                explicit_task_titles += 1

    for chapter, quest, task in outside_tasks:
        language_key = item_keys.get(task["item_id"], "")
        fallback = (
            task["custom_name"]
            or project_ko.get(language_key, "")
            or installed_ko.get(language_key, "")
        )
        if not fallback or audit.looks_untranslated(fallback):
            errors.append(
                "전용 챕터 밖 직접 관련 Task fallback이 영어입니다: "
                f"{chapter['filename']}:{quest['id']}:{task['id']}={fallback!r}"
            )
    if custom_names:
        errors.append(f"대상 챕터에 custom_name이 있습니다: {custom_names}")
    if untranslated_fallbacks:
        errors.append(
            f"영어 또는 빈 quest fallback이 있습니다: {untranslated_fallbacks}"
        )

    advancement_files = 0
    advancement_keys = 0
    for target_mod in TARGETS:
        jar_path = find_jar(instance, target_mod)
        with ZipFile(jar_path) as archive:
            for path in archive.namelist():
                if not path.endswith(".json") or "/advancement" not in path:
                    continue
                raw = archive.read(path).decode("utf-8-sig")
                keys = re.findall(r'"translate"\s*:\s*"([^"]+)"', raw)
                if keys:
                    advancement_files += 1
                for key in keys:
                    advancement_keys += 1
                    if key not in project_ko:
                        errors.append(f"발전 과제 번역 키가 없습니다: {path}:{key}")

    report = {
        "scope": "Silent Gear family FTB Quests",
        "chapter": target["filename"],
        "quests_checked": len(target["quests"]),
        "tasks_checked": sum(len(quest["tasks"]) for quest in target["quests"]),
        "display_keys_checked": len(english),
        "fallback_titles_added": len(build.FALLBACK_TITLES),
        "quest_fallbacks_checked": fallback_checks,
        "explicit_task_titles_checked": explicit_task_titles,
        "custom_names": len(custom_names),
        "literal_components": 0,
        "related_tasks_outside_chapter_checked": len(outside_tasks),
        "resource_name_matches_checked": resource_name_checks,
        "advancement_files_checked": advancement_files,
        "advancement_translate_keys_checked": advancement_keys,
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
