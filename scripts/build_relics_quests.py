#!/usr/bin/env python3
"""Relics·Artifacts 계열 FTB Quests 번역과 literal hover를 누적 산출물로 만든다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import build_ae2_quests as snbt
import prepare_relics_quests as prepare
from local_paths import resolve_source_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = PROJECT_ROOT / "working/relics"
OVERRIDES_FILE = WORK_ROOT / "quest_overrides.json"
OUTPUT_FILE = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
CHAPTER_OUTPUT = (
    PROJECT_ROOT / "output/overrides/config/ftbquests/quests/chapters/relics.snbt"
)
PROGRESS_FILE = WORK_ROOT / "quest_progress.json"
HOVER_TRANSLATIONS = {
    "Bastion": "보루 잔해",
    "Fortress": "네더 요새",
    "Ruined Portal": "파괴된 차원문",
    "End City": "엔드 시티",
    "End Ship": "엔드 함선",
    "Ocean Ruin": "해저 폐허",
    "Shipwreck": "난파선",
    "Mineshaft": "폐광",
    "Village": "마을",
    "Stronghold": "요새",
}
INTENTIONAL_ORIGINAL_KEYS = {
    "chapter.11919EBB416B2BD0.title",
    "chapter.7AF827D2D101D343.title",
    "quest.5CE44C58A470E48E.title",
    "quest.64141B720662B652.title",
    "task.376652638B9221C9.title",
    "task.72E89066290E3040.title",
    "task.23C7F92BD9D39E14.title",
    "task.5E90B977ACB0C900.title",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flattened(value: snbt.TranslationValue) -> str:
    return snbt.flatten(value)


def validate_value(
    key: str, source: snbt.TranslationValue, target: snbt.TranslationValue
) -> list[str]:
    """한국어 어순 변경을 허용하되 서식 코드와 숫자의 전체 집합은 보존한다."""
    errors = snbt.validate_value(key, source, target)
    source_text = flattened(source)
    target_text = flattened(target)
    code_error = f"{key}: 색상/서식 코드 불일치"
    number_error = f"{key}: 숫자 불일치"
    if code_error in errors and Counter(re.findall(r"&.", source_text)) == Counter(
        re.findall(r"&.", target_text)
    ):
        errors.remove(code_error)
    if number_error in errors:
        source_plain = re.sub(r"&.", "", source_text)
        target_plain = re.sub(r"&.", "", target_text)
        number_re = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?")
        if number_re.findall(source_plain) == number_re.findall(target_plain):
            errors.remove(number_error)
    return errors


def build_literal_chapter(instance: Path) -> dict[str, object]:
    source_path = instance / "config/ftbquests/quests/chapters/relics.snbt"
    source = source_path.read_text(encoding="utf-8-sig")
    output = source
    for english, korean in HOVER_TRANSLATIONS.items():
        old = f'hover: ["{english}"]'
        new = f'hover: ["{korean}"]'
        if output.count(old) != 1:
            raise ValueError(
                f"literal hover 원문을 정확히 하나 찾지 못했습니다: {english}"
            )
        output = output.replace(old, new)
    CHAPTER_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    CHAPTER_OUTPUT.write_text(output, encoding="utf-8")
    restored = output
    for english, korean in HOVER_TRANSLATIONS.items():
        restored = restored.replace(f'hover: ["{korean}"]', f'hover: ["{english}"]')
    if restored != source:
        raise ValueError("Relics 챕터에서 literal hover 이외의 내용이 달라졌습니다.")
    return {
        "source": source_path.as_posix(),
        "output": CHAPTER_OUTPUT.relative_to(PROJECT_ROOT).as_posix(),
        "literal_hover_translated": len(HOVER_TRANSLATIONS),
        "output_sha256": sha256(CHAPTER_OUTPUT),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    lang_root = instance / "config/ftbquests/quests/lang"
    english = json.loads(prepare.ENGLISH_FILE.read_text(encoding="utf-8"))
    overrides = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
    if set(overrides) != set(english):
        missing = sorted(set(english) - set(overrides))
        extra = sorted(set(overrides) - set(english))
        raise ValueError(f"작업 키 집합 불일치: missing={missing}, extra={extra}")

    errors = []
    for key, source in english.items():
        errors.extend(validate_value(key, source, overrides[key]))
    if errors:
        raise ValueError("\n".join(errors))

    installed = snbt.parse_language_snbt(lang_root / "ko_kr.snbt")
    base_path = OUTPUT_FILE if OUTPUT_FILE.is_file() else lang_root / "ko_kr.snbt"
    base_hash = sha256(base_path)
    merged = snbt.merge_into_full_snbt(base_path, overrides)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(merged, encoding="utf-8")
    reparsed = snbt.parse_language_snbt(OUTPUT_FILE)
    for key, value in overrides.items():
        if reparsed.get(key) != value:
            raise ValueError(f"누적 SNBT 병합 결과가 다릅니다: {key}")

    kept = sum(
        key in installed and installed[key] == value for key, value in overrides.items()
    )
    corrected = sum(
        key in installed and installed[key] != value for key, value in overrides.items()
    )
    newly_completed = sum(key not in installed for key in overrides)
    literal = build_literal_chapter(instance)
    progress = {
        "scope": "Relics and Artifacts family FTB Quests",
        "chapters": list(prepare.CHAPTERS),
        "source_display_keys": len(english),
        "existing_korean_kept": kept,
        "existing_korean_corrected": corrected,
        "newly_completed": newly_completed,
        "classification": {
            "translated_or_localized": len(english) - len(INTENTIONAL_ORIGINAL_KEYS),
            "intentional_original": len(INTENTIONAL_ORIGINAL_KEYS),
            "internal_or_not_displayed": 0,
            "out_of_scope": 0,
            "manual_review": 0,
        },
        "intentional_original_keys": sorted(INTENTIONAL_ORIGINAL_KEYS),
        "remaining": 0,
        "output": OUTPUT_FILE.relative_to(PROJECT_ROOT).as_posix(),
        "base_sha256": base_hash,
        "output_sha256": sha256(OUTPUT_FILE),
        "literal_chapter": literal,
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
