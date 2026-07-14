#!/usr/bin/env python3
"""Relics·Artifacts 계열 FTB Quests 원문과 기존 한국어를 작업 JSON으로 준비한다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import build_ae2_quests as snbt
from local_paths import resolve_source_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = PROJECT_ROOT / "working/relics"
OVERRIDES_FILE = WORK_ROOT / "quest_overrides.json"
ENGLISH_FILE = WORK_ROOT / "quest_english.json"
CATALOG_FILE = WORK_ROOT / "quest_catalog.json"
CHAPTERS = ("artifacts", "relics")
ADDITIONAL_KEYS = (
    "chapter.11919EBB416B2BD0.title",
    "chapter.7AF827D2D101D343.title",
    "chapter_group.15E5B587D291A4AA.title",
    "quest.51E77B9CD3FB6DEA.quest_desc",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    lang_root = instance / "config/ftbquests/quests/lang"
    if OVERRIDES_FILE.exists() and not args.force:
        parser.error(f"기존 작업 파일을 덮어쓰지 않습니다: {OVERRIDES_FILE}")

    english_all: dict[str, snbt.TranslationValue] = {}
    draft: dict[str, snbt.TranslationValue] = {}
    rows = []
    for chapter in CHAPTERS:
        english = snbt.parse_language_snbt(
            lang_root / f"en_us/chapters/{chapter}.snbt_merged"
        )
        korean_path = lang_root / f"ko_kr/chapters/{chapter}.snbt_merged"
        korean = snbt.parse_language_snbt(korean_path) if korean_path.is_file() else {}
        overlap = sorted(set(draft) & set(english))
        if overlap:
            raise ValueError(f"챕터 사이에 중복 키가 있습니다: {overlap}")
        for key, source in english.items():
            english_all[key] = source
            draft[key] = korean.get(key, source)
        rows.append(
            {
                "chapter": chapter,
                "english_keys": len(english),
                "existing_korean": sum(key in korean for key in english),
                "missing_korean": sum(key not in korean for key in english),
            }
        )

    full_english = snbt.parse_language_snbt(lang_root / "en_us.snbt")
    full_korean = snbt.parse_language_snbt(lang_root / "ko_kr.snbt")
    for key in ADDITIONAL_KEYS:
        english_all[key] = full_english[key]
        draft[key] = full_korean.get(key, full_english[key])

    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    OVERRIDES_FILE.write_text(
        json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    ENGLISH_FILE.write_text(
        json.dumps(english_all, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    catalog = {
        "scope": "Relics and Artifacts family FTB Quests",
        "chapters": rows,
        "additional_keys": len(ADDITIONAL_KEYS),
        "total_keys": len(draft),
        "existing_korean": sum(row["existing_korean"] for row in rows)
        + sum(key in full_korean for key in ADDITIONAL_KEYS),
        "missing_korean": sum(row["missing_korean"] for row in rows)
        + sum(key not in full_korean for key in ADDITIONAL_KEYS),
    }
    CATALOG_FILE.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(catalog, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
