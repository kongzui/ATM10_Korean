#!/usr/bin/env python3
"""Relics·Artifacts 계열 FTB Quests와 모든 fallback 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import audit_ftbquests_titles as audit
import build_ae2_quests as snbt
import build_relics_quests as build
import prepare_relics_quests as prepare
from local_paths import resolve_source_root
from prepare_relics import find_jar
from relics_catalog import TARGETS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_FILE = PROJECT_ROOT / "working/relics/quest_validation.json"
LATIN_WORD_RE = re.compile(r"[A-Za-z]{3,}")
INTENTIONAL_FALLBACK_QUESTS = {"5FD6A738754F6013", "3E99F4CD379DE9D7"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    quest_root = instance / "config/ftbquests/quests"
    output = snbt.parse_language_snbt(build.OUTPUT_FILE)
    output_text = build.OUTPUT_FILE.read_text(encoding="utf-8")
    english = json.loads(prepare.ENGLISH_FILE.read_text(encoding="utf-8"))
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
        errors.append("작업 JSON과 영어 표시 키 집합이 다릅니다.")
    for key, source in english.items():
        if output.get(key) != overrides.get(key):
            errors.append(f"누적 출력값이 작업 번역과 다릅니다: {key}")
        elif key in overrides:
            errors.extend(build.validate_value(key, source, overrides[key]))

    chapters, _ = audit.parse_chapters(quest_root)
    target_chapters = [
        chapter
        for chapter in chapters
        if chapter["filename"].removesuffix(".snbt") in prepare.CHAPTERS
    ]
    if len(target_chapters) != len(prepare.CHAPTERS):
        errors.append(
            f"대상 챕터 구조를 모두 찾지 못했습니다: {len(target_chapters)}개"
        )

    target_namespaces = {"artifacts", "relics", "reliquified_artifacts"}
    related_tasks = [
        (chapter, quest, task)
        for chapter in chapters
        if chapter not in target_chapters
        for quest in chapter["quests"]
        for task in quest["tasks"]
        if task["item_id"].partition(":")[0] in target_namespaces
    ]
    item_ids = {
        task["item_id"]
        for chapter in target_chapters
        for quest in chapter["quests"]
        for task in quest["tasks"]
        if task["item_id"]
    } | {task["item_id"] for _, _, task in related_tasks}
    installed_en, installed_ko, item_keys = audit.load_installed_item_languages(
        instance, item_ids
    )
    _, project_ko = audit.load_project_languages()

    fallback_checks = 0
    item_title_checks = 0
    explicit_task_titles = 0
    redundant_item_task_titles = []
    custom_names = []
    for chapter in target_chapters:
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
                if (
                    audit.looks_untranslated(fallback)
                    and quest["id"] not in INTENTIONAL_FALLBACK_QUESTS
                ):
                    errors.append(
                        f"첫 Task quest fallback이 영어입니다: {quest['id']}={fallback}"
                    )

            if len(quest["tasks"]) == 1 and first_task and first_task["item_id"]:
                language_key = item_keys.get(first_task["item_id"], "")
                source_item_name = installed_en.get(language_key, "")
                resource_name = project_ko.get(language_key, "")
                if source_item_name and source_title and resource_name:
                    source_matches_item = audit.strip_formatting(source_title) in {
                        source_item_name,
                        "Steadfast Boots",
                        "Chorus Belt",
                        "Whoopie Cushion",
                    }
                    if source_matches_item:
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
                if source_item_name and (
                    audit.strip_formatting(source_task_title)
                    == audit.strip_formatting(source_item_name)
                ):
                    redundant_item_task_titles.append(task["id"])

    for chapter, quest, task in related_tasks:
        language_key = item_keys.get(task["item_id"], "")
        fallback = task["custom_name"] or project_ko.get(language_key, "")
        if task["custom_name"] or not fallback or audit.looks_untranslated(fallback):
            errors.append(
                "전용 챕터 밖 직접 관련 Task fallback을 번역하지 못했습니다: "
                f"{chapter['filename']}:{quest['id']}:{task['id']}={fallback!r}"
            )
    if custom_names:
        errors.append(f"대상 챕터에 custom_name이 있습니다: {custom_names}")
    if redundant_item_task_titles:
        errors.append(
            "단일 아이템명을 반복하는 task.title이 있습니다: "
            f"{redundant_item_task_titles}"
        )

    source_chapter = quest_root / "chapters/relics.snbt"
    source_text = source_chapter.read_text(encoding="utf-8-sig")
    literal_text = build.CHAPTER_OUTPUT.read_text(encoding="utf-8")
    restored = literal_text
    for source, target in build.HOVER_TRANSLATIONS.items():
        if literal_text.count(f'hover: ["{target}"]') != 1:
            errors.append(f"번역된 literal hover가 정확히 하나가 아닙니다: {target}")
        restored = restored.replace(f'hover: ["{target}"]', f'hover: ["{source}"]')
    if restored != source_text:
        errors.append("Relics 챕터 산출물에 hover 이외의 구조 변경이 있습니다.")

    advancements_checked = 0
    artifacts_target = next(target for target in TARGETS if target.batch == "artifacts")
    with ZipFile(find_jar(instance, artifacts_target)) as archive:
        advancement_paths = [
            name
            for name in archive.namelist()
            if name.startswith("data/artifacts/advancement/") and name.endswith(".json")
        ]
        for path in advancement_paths:
            raw = archive.read(path).decode("utf-8")
            advancements_checked += 1
            for key in re.findall(r'"translate"\s*:\s*"([^"]+)"', raw):
                if key not in project_ko:
                    errors.append(
                        f"Artifacts 발전 과제 번역 키가 없습니다: {path}:{key}"
                    )

    intended = build.INTENTIONAL_ORIGINAL_KEYS
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
        "scope": "Relics and Artifacts family FTB Quests",
        "chapters_checked": [chapter["filename"] for chapter in target_chapters],
        "display_keys_checked": len(english),
        "duplicate_keys": len(duplicate_keys),
        "custom_names": len(custom_names),
        "literal_hover_translated": len(build.HOVER_TRANSLATIONS),
        "explicit_task_titles_checked": explicit_task_titles,
        "redundant_single_item_task_titles": len(redundant_item_task_titles),
        "quest_fallbacks_checked": fallback_checks,
        "item_resourcepack_title_matches_checked": item_title_checks,
        "related_tasks_outside_chapters_checked": len(related_tasks),
        "advancements_checked": advancements_checked,
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
