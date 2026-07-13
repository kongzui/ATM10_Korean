#!/usr/bin/env python3
"""FTB Quests 목차·제목 수정 범위와 fallback 정합성을 읽기 전용으로 검증한다."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import audit_ftbquests_titles as audit
import build_ae2_quests as snbt
import build_ftbquests_titles as builder
from local_paths import resolve_source_root

REDUNDANT_SINGLE_ITEM_TASK_IDS = {
    "03EB390E79866058",
    "065E5450AC87F1D5",
    "0F2BCC279B5731AB",
    "17B0E19125FCFA1A",
    "17C7DC04BC22C0D7",
    "181135E3A83C5B9E",
    "263F0E416A8E1110",
    "299DE26FF7293F34",
    "2CC38211F4C54ED8",
    "2EA19C4E46380CDA",
    "345245C32DB7B4D4",
    "3B35F86B42989063",
    "4203F7ED807F3D30",
    "429FA8057B666565",
    "4471A530B55D4140",
    "46C7D666D3A4A3D9",
    "47BAD4AA76F9CF82",
    "4DA6445DB5F3B85E",
    "4EF5B261BAD2AC7D",
    "4FCEB24FC83D22A9",
    "50823C029014781A",
    "55F718D796CEB1B1",
    "5B5DBA0A7644A551",
    "5BFAA4BB6651F71A",
    "5C358DFF9CD0D1D9",
    "5E017E6B7E3F56B7",
    "6D4F62833424ADC0",
    "79AEDC66EB312BCA",
    "7B7C1C5BFEC92058",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    quest_root = instance / "config/ftbquests/quests"
    lang_root = quest_root / "lang"
    english = snbt.parse_language_snbt(lang_root / "en_us.snbt")
    baseline = snbt.parse_language_snbt(lang_root / "ko_kr.snbt")
    output = snbt.parse_language_snbt(builder.OUTPUT_LANG)
    chapters, object_ids = audit.parse_chapters(quest_root)
    tasks_by_id = {
        task["id"]: task
        for chapter in chapters
        for quest in chapter["quests"]
        for task in quest["tasks"]
    }
    group_ids = set(
        re.findall(
            r"[0-9A-F]{16}",
            (quest_root / "chapter_groups.snbt").read_text(encoding="utf-8-sig"),
        )
    )
    object_ids.update(group_ids)

    raw_output = builder.OUTPUT_LANG.read_text(encoding="utf-8")
    keys = snbt.ENTRY_RE.findall(raw_output)
    duplicates = sorted(key for key, count in Counter(keys).items() if count > 1)
    if duplicates:
        raise ValueError(f"중복 번역 키: {duplicates}")
    if builder.OUTPUT_LANG.read_bytes().startswith(b"\xef\xbb\xbf"):
        raise ValueError("출력 SNBT에 UTF-8 BOM이 있습니다.")

    changed_keys = {
        key
        for key in set(baseline) | set(output)
        if baseline.get(key) != output.get(key)
    }
    invalid_scope = sorted(
        key for key in changed_keys if not builder.TITLE_KEY_RE.fullmatch(key)
    )
    invalid_ids = sorted(
        key for key in changed_keys if key.split(".")[1] not in object_ids
    )
    if invalid_scope or invalid_ids:
        raise ValueError(
            f"제목 범위 밖 변경={invalid_scope}, 잘못된 객체 ID={invalid_ids}"
        )
    description_changes = sorted(
        key for key in changed_keys if key.endswith(".quest_desc")
    )
    if description_changes:
        raise ValueError(f"설명문이 변경됐습니다: {description_changes}")

    validation_errors: list[str] = []
    for key in changed_keys & english.keys() & output.keys():
        validation_errors.extend(snbt.validate_value(key, english[key], output[key]))
    if validation_errors:
        raise ValueError("\n".join(validation_errors))

    navigation_checked = 0
    for kind, prefix, ids in (
        ("group", "chapter_group", group_ids),
        ("chapter", "chapter", {chapter["id"] for chapter in chapters}),
    ):
        for object_id in ids:
            key = f"{prefix}.{object_id}.title"
            source = audit.text_value(english, key)
            if not source:
                continue
            expected = audit.canonical_navigation(source, kind)
            if audit.text_value(output, key) != expected:
                raise ValueError(f"목차 표기가 기준과 다릅니다: {key}")
            navigation_checked += 1

    expected_ae2 = {
        "quest.69B7DE2283B4EE6C.title": "제작 보조 처리 유닛",
    }
    for key, value in expected_ae2.items():
        if output.get(key) != value:
            raise ValueError(f"AE2 자동 제목 수정이 없습니다: {key}")

    redundant_ae2_item_task_titles = sorted(
        f"task.{task['id']}.title"
        for chapter in chapters
        if chapter["filename"] == "applied_energistics_2.snbt"
        for quest in chapter["quests"]
        for task in quest["tasks"]
        if task["type"] == "item"
        and task["item_id"]
        and f"task.{task['id']}.title" not in english
        and f"task.{task['id']}.title" in output
    )
    if redundant_ae2_item_task_titles:
        raise ValueError(
            "AE2 ItemTask에 중복 아이템 제목이 있습니다: "
            f"{redundant_ae2_item_task_titles}"
        )

    invalid_removed_tasks = sorted(
        task_id
        for task_id in REDUNDANT_SINGLE_ITEM_TASK_IDS
        if task_id not in tasks_by_id
        or tasks_by_id[task_id]["type"] != "item"
        or not tasks_by_id[task_id]["item_id"]
        or tasks_by_id[task_id]["item_id"] == "ftbfiltersystem:smart_filter"
    )
    restored_redundant_titles = sorted(
        task_id
        for task_id in REDUNDANT_SINGLE_ITEM_TASK_IDS
        if f"task.{task_id}.title" in output
    )
    if invalid_removed_tasks or restored_redundant_titles:
        raise ValueError(
            f"단일 ItemTask 검증 실패={invalid_removed_tasks}, "
            f"중복 제목 재생성={restored_redundant_titles}"
        )

    report = json.loads(audit.REPORT_JSON.read_text(encoding="utf-8"))
    resolved_problem_types = {
        "목차 표기 불일치",
        "리소스팩 아이템명과 quest.title 불일치",
        "같은 아이템의 quest.title 표기 불일치",
        "제목/부제 형식 불일치: 색상/서식 코드 불일치",
        "제목/부제 형식 불일치: 숫자 불일치",
        "한국어 파일의 영어 subtitle",
    }
    unresolved_fixed_types = sorted(
        problem_type
        for problem_type in resolved_problem_types
        if report["problem_counts"].get(problem_type, 0)
    )
    if unresolved_fixed_types:
        raise ValueError(
            f"확정 수정 범주의 문제가 남았습니다: {unresolved_fixed_types}"
        )

    result = {
        "changed_title_keys": len(changed_keys),
        "description_keys_changed": 0,
        "duplicate_keys": 0,
        "invalid_object_ids": 0,
        "navigation_titles_checked": navigation_checked,
        "ae2_fallback_titles_checked": len(expected_ae2),
        "redundant_ae2_item_task_titles": 0,
        "redundant_single_item_task_titles": 0,
        "removed_single_item_task_titles_checked": len(REDUNDANT_SINGLE_ITEM_TASK_IDS),
        "placeholder_number_format_errors": 0,
        "utf8_bom_files": 0,
        "audit_candidates_remaining": report["remaining_issue_count"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
