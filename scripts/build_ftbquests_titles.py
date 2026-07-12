#!/usr/bin/env python3
"""검증된 목차 기준과 아이템 이름으로 FTB Quests 제목 번역을 갱신한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import audit_ftbquests_titles as audit
import build_ae2_quests as snbt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_LANG = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
MANUAL_OVERRIDES = PROJECT_ROOT / "working/ftbquests/title_overrides.json"
PROGRESS_FILE = PROJECT_ROOT / "working/ftbquests/title_progress.json"
TITLE_KEY_RE = re.compile(
    r"^(?:chapter_group|chapter|quest|task)\.[0-9A-F]{16}\."
    r"(?:title|quest_subtitle|chapter_subtitle)$"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, type=Path)
    args = parser.parse_args()
    instance = args.instance.resolve()
    quest_root = instance / "config/ftbquests/quests"
    lang_root = quest_root / "lang"
    english = snbt.parse_language_snbt(lang_root / "en_us.snbt")
    current = snbt.parse_language_snbt(OUTPUT_LANG)
    baseline = snbt.parse_language_snbt(lang_root / "ko_kr.snbt")
    chapters, object_ids = audit.parse_chapters(quest_root)
    group_ids = set(
        re.findall(
            r"[0-9A-F]{16}",
            (quest_root / "chapter_groups.snbt").read_text(encoding="utf-8-sig"),
        )
    )
    object_ids.update(group_ids)

    overrides: dict[str, snbt.TranslationValue] = {}
    navigation_changes = 0
    official_name_changes = 0
    for kind, prefix, ids in (
        ("group", "chapter_group", group_ids),
        ("chapter", "chapter", {chapter["id"] for chapter in chapters}),
    ):
        for object_id in sorted(ids):
            key = f"{prefix}.{object_id}.title"
            source = audit.text_value(english, key)
            if not source:
                continue
            target = audit.canonical_navigation(source, kind)
            overrides[key] = target
            if audit.text_value(baseline, key) != target:
                navigation_changes += 1
                if target == source or source in audit.MIXED_CHAPTER_TITLES:
                    official_name_changes += 1

    item_ids = {
        task["item_id"]
        for chapter in chapters
        if chapter["filename"] == "applied_energistics_2.snbt"
        for quest in chapter["quests"]
        for task in quest["tasks"]
        if task["item_id"] and task["item_id"] != "ftbfiltersystem:smart_filter"
    }
    installed_en, _, item_keys = audit.load_installed_item_languages(instance, item_ids)
    _, project_ko = audit.load_project_languages()
    ae2_quest_titles = 0
    ae2_task_titles = 0
    ae2_item_name_corrections = 0
    for chapter in chapters:
        if chapter["filename"] != "applied_energistics_2.snbt":
            continue
        for quest in chapter["quests"]:
            translated_tasks: list[tuple[dict[str, str], str, str]] = []
            for task in quest["tasks"]:
                language_key = item_keys.get(task["item_id"], "")
                translated_name = project_ko.get(language_key, "")
                if not translated_name:
                    continue
                task_key = f"task.{task['id']}.title"
                if audit.text_value(baseline, task_key) != translated_name:
                    ae2_task_titles += 1
                overrides[task_key] = translated_name
                translated_tasks.append(
                    (task, translated_name, installed_en.get(language_key, ""))
                )

            if len(quest["tasks"]) != 1 or len(translated_tasks) != 1:
                continue
            _, translated_name, english_item_name = translated_tasks[0]
            quest_key = f"quest.{quest['id']}.title"
            source_title = audit.text_value(english, quest_key)
            current_title = audit.text_value(baseline, quest_key)
            item_based = not source_title or (
                audit.strip_formatting(source_title)
                == audit.strip_formatting(english_item_name)
            )
            if not item_based:
                continue
            if current_title != translated_name:
                ae2_quest_titles += 1
                if current_title:
                    ae2_item_name_corrections += 1
            overrides[quest_key] = translated_name

    manual = json.loads(MANUAL_OVERRIDES.read_text(encoding="utf-8"))
    overrides.update(manual)
    invalid_keys = sorted(key for key in overrides if not TITLE_KEY_RE.fullmatch(key))
    invalid_ids = sorted(
        key for key in overrides if key.split(".")[1] not in object_ids
    )
    if invalid_keys or invalid_ids:
        raise ValueError(f"잘못된 제목 키={invalid_keys}, 잘못된 객체 ID={invalid_ids}")

    validation_errors: list[str] = []
    for key, translated in overrides.items():
        if key in english:
            validation_errors.extend(snbt.validate_value(key, english[key], translated))
    if validation_errors:
        raise ValueError("\n".join(validation_errors))

    before_text = OUTPUT_LANG.read_text(encoding="utf-8-sig")
    merged = snbt.merge_into_full_snbt(OUTPUT_LANG, overrides)
    OUTPUT_LANG.write_text(merged, encoding="utf-8")
    reparsed = snbt.parse_language_snbt(OUTPUT_LANG)
    for key, value in overrides.items():
        if reparsed.get(key) != value:
            raise ValueError(f"SNBT 병합 결과가 다릅니다: {key}")
    changed_keys = {
        key
        for key in set(current) | set(reparsed)
        if current.get(key) != reparsed.get(key)
    }
    unexpected = sorted(changed_keys - overrides.keys())
    if unexpected:
        OUTPUT_LANG.write_text(before_text, encoding="utf-8")
        raise ValueError(f"제목 범위 밖의 키가 변경됐습니다: {unexpected}")
    baseline_changed_keys = {
        key
        for key in set(baseline) | set(reparsed)
        if baseline.get(key) != reparsed.get(key)
    }

    progress = {
        "scope": "FTB Quests navigation and title fallback consistency",
        "navigation_titles_changed": navigation_changes,
        "official_mod_names_corrected": official_name_changes,
        "ae2_quest_titles_added_or_corrected": ae2_quest_titles,
        "ae2_task_titles_added_or_corrected": ae2_task_titles,
        "ae2_item_name_mismatches_corrected": ae2_item_name_corrections,
        "manual_title_fixes": sum(
            baseline.get(key) != value for key, value in manual.items()
        ),
        "total_changed_keys": len(baseline_changed_keys),
        "output_sha256": sha256(OUTPUT_LANG),
        "validation_errors": 0,
    }
    PROGRESS_FILE.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(progress, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
