#!/usr/bin/env python3
"""Apotheosis 계열 FTB Quests 번역을 누적 ko_kr.snbt에 병합한다."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import build_ae2_quests as snbt
from local_paths import resolve_source_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = PROJECT_ROOT / "working/apotheosis"
OVERRIDES_FILE = WORK_ROOT / "quest_overrides.json"
OUTPUT_FILE = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
PROGRESS_FILE = WORK_ROOT / "quest_progress.json"
CATALOG_FILE = WORK_ROOT / "quest_catalog.json"
CHAPTERS = ("apotheosis_2", "apotheosis_gear", "apothic_enchanting")
NAVIGATION_KEYS = (
    "chapter.0E81CBCD6B1D1895.title",
    "chapter.0E81CBCD6B1D1895.chapter_subtitle",
    "chapter.0731FA8830F28280.title",
    "chapter.12AD9789D962B179.title",
)
RELATED_QUEST_KEYS = (
    "quest.4A6B585C2394A89A.quest_desc",
    "quest.14B7EEBE0F6C2776.title",
    "quest.14B7EEBE0F6C2776.quest_desc",
)
INTENTIONAL_ORIGINAL_KEYS = (
    "quest.310969B8FE0A94DE.title",
    "quest.1FAFDB20F504688E.title",
    "chapter.0E81CBCD6B1D1895.title",
    "chapter.12AD9789D962B179.title",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    lang_root = instance / "config/ftbquests/quests/lang"
    full_english = snbt.parse_language_snbt(lang_root / "en_us.snbt")
    overrides = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))

    english: dict[str, snbt.TranslationValue] = {}
    chapter_counts = []
    for chapter in CHAPTERS:
        source_path = lang_root / f"en_us/chapters/{chapter}.snbt_merged"
        current_path = lang_root / f"ko_kr/chapters/{chapter}.snbt_merged"
        source = snbt.parse_language_snbt(source_path)
        installed = (
            snbt.parse_language_snbt(current_path) if current_path.is_file() else {}
        )
        overlap = set(english) & set(source)
        if overlap:
            raise ValueError(f"챕터 사이에 중복 키가 있습니다: {sorted(overlap)}")
        english.update(source)
        chapter_counts.append(
            {
                "chapter": chapter,
                "keys": len(source),
                "existing_korean": sum(key in installed for key in source),
                "missing_korean": sum(key not in installed for key in source),
            }
        )

    for key in NAVIGATION_KEYS + RELATED_QUEST_KEYS:
        if key not in full_english:
            raise ValueError(f"영어 목차 키를 찾지 못했습니다: {key}")
        english[key] = full_english[key]

    if set(overrides) != set(english):
        missing = sorted(set(english) - set(overrides))
        extra = sorted(set(overrides) - set(english))
        raise ValueError(f"작업 키 집합 불일치: missing={missing}, extra={extra}")

    errors = []
    for key, source in english.items():
        errors.extend(snbt.validate_value(key, source, overrides[key]))
    if errors:
        raise ValueError("\n".join(errors))

    base_path = OUTPUT_FILE if OUTPUT_FILE.is_file() else lang_root / "ko_kr.snbt"
    base_hash = sha256(base_path)
    merged = snbt.merge_into_full_snbt(base_path, overrides)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(merged, encoding="utf-8")
    reparsed = snbt.parse_language_snbt(OUTPUT_FILE)
    for key, value in overrides.items():
        if reparsed.get(key) != value:
            raise ValueError(f"누적 SNBT 병합 결과가 다릅니다: {key}")

    intended = set(INTENTIONAL_ORIGINAL_KEYS)
    completion_counts = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))[
        "completion_counts"
    ]
    progress = {
        "scope": "Apotheosis family FTB Quests",
        "chapters": chapter_counts,
        "source_display_keys": len(english),
        "existing_korean_kept": completion_counts["existing_korean_kept"],
        "existing_korean_corrected": completion_counts["existing_korean_corrected"],
        "newly_completed": completion_counts["newly_completed"],
        "classification": {
            "translated_or_localized": len(english) - len(intended),
            "intentional_original": len(intended),
            "internal_or_not_displayed": 0,
            "out_of_scope": 0,
            "manual_review": 0,
        },
        "intentional_original_keys": list(INTENTIONAL_ORIGINAL_KEYS),
        "remaining": 0,
        "output": OUTPUT_FILE.relative_to(PROJECT_ROOT).as_posix(),
        "base_sha256": base_hash,
        "output_sha256": sha256(OUTPUT_FILE),
        "validation_errors": 0,
        "review_items": [],
    }
    PROGRESS_FILE.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(progress, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
