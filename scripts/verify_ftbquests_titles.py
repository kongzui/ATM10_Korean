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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, type=Path)
    args = parser.parse_args()
    instance = args.instance.resolve()
    quest_root = instance / "config/ftbquests/quests"
    lang_root = quest_root / "lang"
    english = snbt.parse_language_snbt(lang_root / "en_us.snbt")
    baseline = snbt.parse_language_snbt(lang_root / "ko_kr.snbt")
    output = snbt.parse_language_snbt(builder.OUTPUT_LANG)
    chapters, object_ids = audit.parse_chapters(quest_root)
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
    for key in changed_keys & english.keys():
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
        "task.39BC572CE6FCFE92.title": "제작 보조 처리 유닛",
    }
    for key, value in expected_ae2.items():
        if output.get(key) != value:
            raise ValueError(f"AE2 자동 제목 수정이 없습니다: {key}")

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
        "placeholder_number_format_errors": 0,
        "utf8_bom_files": 0,
        "audit_candidates_remaining": report["remaining_issue_count"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
