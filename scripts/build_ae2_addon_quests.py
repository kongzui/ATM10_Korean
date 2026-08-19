#!/usr/bin/env python3
"""AE2 연동 모드의 검증된 FTB Quests 번역을 전체 한국어 파일에 병합한다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import build_ae2_quests as quests
from local_paths import resolve_source_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
MODS = {
    "ae2": {
        "scope": "Applied Energistics 2 core related FTB Quests",
        "working": "working/ae2",
    },
    "ae2wtlib": {
        "scope": "AE2WTLib 전체 관련 FTB Quests 재검수",
        "working": "working/ae2_addons/ae2wtlib",
    },
    "aeinfinitybooster": {
        "scope": "AEInfinityBooster 전체 관련 FTB Quests",
        "working": "working/ae2_addons/aeinfinitybooster",
    },
    "soulplied_energistics": {
        "scope": "Soulplied Energistics 전체 관련 FTB Quests",
        "working": "working/ae2_addons/soulplied_energistics",
    },
    "extendedae": {
        "scope": "Extended AE related FTB Quests quality review",
        "working": "working/ae2_addons/extendedae",
    },
    "advanced_ae": {
        "scope": "Advanced AE related FTB Quests quality review",
        "working": "working/ae2_addons/advanced_ae",
    },
    "megacells": {
        "scope": "MEGA Cells full related FTB Quests before guide batch 09",
        "working": "working/ae2_addons/megacells",
    },
    "appflux": {
        "scope": "Applied Flux full related FTB Quests before guide batch 11",
        "working": "working/ae2_addons/appflux",
    },
    "expandedae": {
        "scope": "ExpandedAE full related FTB Quests before guide batch 12",
        "working": "working/ae2_addons/expandedae",
    },
    "ae2importexportcard": {
        "scope": "AE2 Import Export Card full related FTB Quests before guide batch 13",
        "working": "working/ae2_addons/ae2importexportcard",
    },
    "ae2netanalyser": {
        "scope": "AE2 Network Analyser full related FTB Quests before guide batch 13",
        "working": "working/ae2_addons/ae2netanalyser",
    },
    "merequester": {
        "scope": "ME Requester full related FTB Quests before guide batch 14",
        "working": "working/ae2_addons/merequester",
    },
    "arseng": {
        "scope": "Ars Énergistique full related FTB Quests before guide batch 15",
        "working": "working/ae2_addons/arseng",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--mod", choices=sorted(MODS), default="extendedae")
    args = parser.parse_args()
    mod = MODS[args.mod]
    working_root = PROJECT_ROOT / mod["working"]
    overrides_file = working_root / "quest_overrides.json"
    progress_file = working_root / "quest_progress.json"
    instance = resolve_source_root(args.instance)
    english_path = instance / "config/ftbquests/quests/lang/en_us.snbt"
    baseline_path = instance / "config/ftbquests/quests/lang/ko_kr.snbt"
    english = quests.parse_language_snbt(english_path)
    baseline = quests.parse_language_snbt(baseline_path)
    before = quests.parse_language_snbt(OUTPUT_FILE)
    overrides = json.loads(overrides_file.read_text(encoding="utf-8"))

    missing_source = sorted(set(overrides) - set(english))
    if missing_source:
        raise ValueError(f"영어 원문에 없는 퀘스트 키: {missing_source}")
    errors: list[str] = []
    for key, translated in overrides.items():
        errors.extend(quests.validate_value(key, english[key], translated))
    if errors:
        raise ValueError("\n".join(errors))

    before_text = OUTPUT_FILE.read_text(encoding="utf-8-sig")
    merged = quests.merge_into_full_snbt(OUTPUT_FILE, overrides)
    OUTPUT_FILE.write_text(merged, encoding="utf-8")
    after = quests.parse_language_snbt(OUTPUT_FILE)
    for key, value in overrides.items():
        if after.get(key) != value:
            OUTPUT_FILE.write_text(before_text, encoding="utf-8")
            raise ValueError(f"FTB Quests 병합 결과가 다릅니다: {key}")
    changed = {
        key for key in set(before) | set(after) if before.get(key) != after.get(key)
    }
    unexpected = sorted(changed - set(overrides))
    if unexpected:
        OUTPUT_FILE.write_text(before_text, encoding="utf-8")
        raise ValueError(f"지정 범위 밖의 퀘스트 키가 변경됐습니다: {unexpected}")

    if args.mod == "ae2":
        lang_root = instance / "config/ftbquests/quests/lang"
        chapter_english = quests.parse_language_snbt(
            lang_root / "en_us/chapters/applied_energistics_2.snbt_merged"
        )
        chapter_current = quests.parse_language_snbt(
            lang_root / "ko_kr/chapters/applied_energistics_2.snbt_merged"
        )
        chapter_final = {key: after[key] for key in chapter_english}
        kept = sum(
            key in chapter_current and chapter_final[key] == chapter_current[key]
            for key in chapter_english
        )
        corrected = sum(
            key in chapter_current and chapter_final[key] != chapter_current[key]
            for key in chapter_english
        )
        progress = {
            "scope": "FTB Quests applied_energistics_2 chapter",
            "total_keys": len(chapter_english),
            "existing_korean_kept": kept,
            "existing_korean_corrected": corrected,
            "newly_completed": sum(
                key not in chapter_current for key in chapter_english
            ),
            "remaining": 0,
            "output": OUTPUT_FILE.relative_to(PROJECT_ROOT).as_posix(),
            "output_sha256": quests.sha256(OUTPUT_FILE),
            "validation_errors": 0,
            "review_items": [],
        }
    else:
        progress = {
            "scope": mod["scope"],
            "source_keys": len(overrides),
            "changed_keys": sum(
                baseline.get(key) != after.get(key) for key in overrides
            ),
            "output": OUTPUT_FILE.relative_to(PROJECT_ROOT).as_posix(),
            "output_sha256": quests.sha256(OUTPUT_FILE),
            "validation_errors": 0,
        }
    progress_file.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(progress, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
