#!/usr/bin/env python3
"""Apotheosis 계열 FTB Quests 번역과 fallback 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import audit_ftbquests_titles as audit
import build_ae2_quests as snbt
import build_apotheosis_quests as build
from local_paths import resolve_source_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_FILE = PROJECT_ROOT / "working/apotheosis/quest_validation.json"
DIRECT_ITEMS_FILE = PROJECT_ROOT / "working/apotheosis/direct_quest_item_names.json"
LATIN_WORD_RE = re.compile(r"[A-Za-z]{3,}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    quest_root = instance / "config/ftbquests/quests"
    lang_root = quest_root / "lang"
    output = snbt.parse_language_snbt(build.OUTPUT_FILE)
    output_text = build.OUTPUT_FILE.read_text(encoding="utf-8")
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

    full_english = snbt.parse_language_snbt(lang_root / "en_us.snbt")
    english: dict[str, snbt.TranslationValue] = {}
    for chapter in build.CHAPTERS:
        english.update(
            snbt.parse_language_snbt(
                lang_root / f"en_us/chapters/{chapter}.snbt_merged"
            )
        )
    english.update({key: full_english[key] for key in build.NAVIGATION_KEYS})
    if set(overrides) != set(english):
        errors.append("작업 JSON과 영어 표시 키 집합이 다릅니다.")
    for key, source in english.items():
        if output.get(key) != overrides.get(key):
            errors.append(f"누적 출력값이 작업 번역과 다릅니다: {key}")
        elif key in overrides:
            errors.extend(snbt.validate_value(key, source, overrides[key]))

    chapters, _ = audit.parse_chapters(quest_root)
    target_chapters = [
        chapter
        for chapter in chapters
        if chapter["filename"].removesuffix(".snbt") in build.CHAPTERS
    ]
    if len(target_chapters) != len(build.CHAPTERS):
        errors.append(
            f"대상 챕터 구조를 모두 찾지 못했습니다: {len(target_chapters)}개"
        )

    item_ids = {
        task["item_id"]
        for chapter in target_chapters
        for quest in chapter["quests"]
        for task in quest["tasks"]
        if task["item_id"] and task["item_id"] != "ftbfiltersystem:smart_filter"
    }
    installed_en, installed_ko, item_keys = audit.load_installed_item_languages(
        instance, item_ids
    )
    _, project_ko = audit.load_project_languages()
    direct_items = json.loads(DIRECT_ITEMS_FILE.read_text(encoding="utf-8"))["items"]
    for item_id, translated_name in direct_items.items():
        language_key = item_keys.get(item_id, "")
        if not language_key or language_key not in installed_en:
            errors.append(
                f"직접 연동 아이템의 영어 원문 키를 찾지 못했습니다: {item_id}"
            )
        elif project_ko.get(language_key) != translated_name:
            errors.append(
                f"직접 연동 아이템 번역이 출력과 다릅니다: {item_id}={translated_name}"
            )
    custom_names = []
    redundant_item_task_titles = []
    fallback_checks = 0
    item_title_checks = 0
    explicit_task_titles = 0

    for chapter in target_chapters:
        chapter_path = quest_root / "chapters" / chapter["filename"]
        raw = chapter_path.read_text(encoding="utf-8-sig")
        if re.search(r'"minecraft:custom_name"\s*:', raw) or re.search(
            r'"literal"\s*:', raw
        ):
            errors.append(
                f"별도 literal/custom_name 검토가 필요한 챕터입니다: {chapter_path}"
            )
        for quest in chapter["quests"]:
            quest_key = f"quest.{quest['id']}.title"
            source_title = audit.text_value(english, quest_key)
            target_title = audit.text_value(output, quest_key)
            first_task = quest["tasks"][0] if quest["tasks"] else None
            if not target_title and first_task:
                task_key = f"task.{first_task['id']}.title"
                language_key = item_keys.get(first_task["item_id"], "")
                fallback = (
                    audit.text_value(output, task_key)
                    or first_task["custom_name"]
                    or project_ko.get(language_key, "")
                    or installed_ko.get(language_key, "")
                    or installed_en.get(language_key, "")
                )
                fallback_checks += 1
                if audit.looks_untranslated(fallback):
                    errors.append(
                        f"첫 Task quest fallback이 영어입니다: {quest['id']}={fallback}"
                    )

            if len(quest["tasks"]) == 1 and first_task and first_task["item_id"]:
                language_key = item_keys.get(first_task["item_id"], "")
                source_item_name = installed_en.get(language_key, "")
                resource_name = project_ko.get(language_key, "")
                if (
                    source_item_name
                    and audit.strip_formatting(source_title)
                    == audit.strip_formatting(source_item_name)
                    and resource_name
                ):
                    item_title_checks += 1
                    if audit.strip_formatting(target_title) != resource_name:
                        errors.append(
                            "리소스팩 아이템명과 quest.title이 다릅니다: "
                            f"{quest['id']}={target_title!r}, resource={resource_name!r}"
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
                task_key = f"task.{task['id']}.title"
                source_task_title = audit.text_value(english, task_key)
                if not source_task_title:
                    continue
                explicit_task_titles += 1
                language_key = item_keys.get(task["item_id"], "")
                source_item_name = installed_en.get(language_key, "")
                if (
                    task["item_id"] != "ftbfiltersystem:smart_filter"
                    and source_item_name
                    and audit.strip_formatting(source_task_title)
                    == audit.strip_formatting(source_item_name)
                ):
                    redundant_item_task_titles.append(task["id"])

    if custom_names:
        errors.append(f"대상 챕터에 custom_name이 있습니다: {custom_names}")
    if redundant_item_task_titles:
        errors.append(
            "단일 아이템명을 반복하는 task.title이 있습니다: "
            f"{redundant_item_task_titles}"
        )

    intended = set(build.INTENTIONAL_ORIGINAL_KEYS)
    unclassified_english = []
    for key, source in english.items():
        target = overrides.get(key)
        if (
            target == source
            and LATIN_WORD_RE.search(snbt.flatten(source))
            and key not in intended
        ):
            unclassified_english.append(key)
    if unclassified_english:
        errors.append(f"분류되지 않은 영어 유지 키가 있습니다: {unclassified_english}")

    report = {
        "scope": "Apotheosis family FTB Quests",
        "chapters_checked": [chapter["filename"] for chapter in target_chapters],
        "display_keys_checked": len(english),
        "duplicate_keys": len(duplicate_keys),
        "custom_or_literal_components": len(custom_names),
        "explicit_task_titles_checked": explicit_task_titles,
        "redundant_single_item_task_titles": len(redundant_item_task_titles),
        "quest_fallbacks_checked": fallback_checks,
        "item_resourcepack_title_matches_checked": item_title_checks,
        "direct_quest_item_names_checked": len(direct_items),
        "unclassified_english": len(unclassified_english),
        "validation_errors": len(errors),
        "errors": errors,
    }
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
