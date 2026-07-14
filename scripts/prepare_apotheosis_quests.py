#!/usr/bin/env python3
"""Apotheosis 계열 FTB Quests 원문과 기존 한국어를 작업 JSON으로 준비한다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import build_ae2_quests as snbt
from local_paths import resolve_source_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = PROJECT_ROOT / "working/apotheosis"
OVERRIDES_FILE = WORK_ROOT / "quest_overrides.json"
CATALOG_FILE = WORK_ROOT / "quest_catalog.json"
CHAPTERS = ("apotheosis_2", "apotheosis_gear", "apothic_enchanting")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--reset-chapter", choices=CHAPTERS)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    lang_root = instance / "config/ftbquests/quests/lang"
    if args.reset_chapter:
        if not OVERRIDES_FILE.is_file():
            parser.error(f"초기 작업 파일이 없습니다: {OVERRIDES_FILE}")
        draft = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
        english = snbt.parse_language_snbt(
            lang_root / f"en_us/chapters/{args.reset_chapter}.snbt_merged"
        )
        draft.update(english)
        OVERRIDES_FILE.write_text(
            json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"영어 원문으로 되돌린 챕터: {args.reset_chapter} ({len(english)}개 키)")
        return 0
    if OVERRIDES_FILE.exists() and not args.force:
        parser.error(f"기존 작업 파일을 덮어쓰지 않습니다: {OVERRIDES_FILE}")

    draft: dict[str, snbt.TranslationValue] = {}
    rows = []
    for chapter in CHAPTERS:
        english_path = lang_root / f"en_us/chapters/{chapter}.snbt_merged"
        korean_path = lang_root / f"ko_kr/chapters/{chapter}.snbt_merged"
        english = snbt.parse_language_snbt(english_path)
        korean = snbt.parse_language_snbt(korean_path) if korean_path.is_file() else {}
        overlap = sorted(set(draft) & set(english))
        if overlap:
            raise ValueError(f"챕터 사이에 중복 키가 있습니다: {overlap}")
        for key, source in english.items():
            draft[key] = korean.get(key, source)
        rows.append(
            {
                "chapter": chapter,
                "english_keys": len(english),
                "existing_korean": sum(key in korean for key in english),
                "missing_korean": sum(key not in korean for key in english),
            }
        )

    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    OVERRIDES_FILE.write_text(
        json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    catalog = {
        "scope": "Apotheosis family FTB Quests",
        "chapters": rows,
        "total_keys": len(draft),
        "existing_korean": sum(row["existing_korean"] for row in rows),
        "missing_korean": sum(row["missing_korean"] for row in rows),
    }
    CATALOG_FILE.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(catalog, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
