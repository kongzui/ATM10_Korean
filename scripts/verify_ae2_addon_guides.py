#!/usr/bin/env python3
"""AE2 연동 모드 가이드 작업본과 리소스팩 산출물을 읽기 전용으로 검증한다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import build_ae2_addon_guides as guides
from local_paths import resolve_source_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BATCHES = (
    (
        1,
        "AE2WTLib",
        guides.validate_ae2wtlib,
        PROJECT_ROOT / "working/ae2_addons/batch_01_completion.json",
        8,
    ),
    (
        2,
        "EnderDrives",
        guides.validate_enderdrives,
        PROJECT_ROOT / "working/ae2_addons/batch_02_completion.json",
        3,
    ),
    (
        3,
        "ExtendedAE",
        guides.validate_extendedae_batch_03,
        PROJECT_ROOT / "working/ae2_addons/batch_03_completion.json",
        11,
    ),
    (
        4,
        "ExtendedAE",
        guides.validate_extendedae_batch_04,
        PROJECT_ROOT / "working/ae2_addons/batch_04_completion.json",
        10,
    ),
    (
        5,
        "ExtendedAE",
        guides.validate_extendedae_batch_05,
        PROJECT_ROOT / "working/ae2_addons/batch_05_completion.json",
        13,
    ),
    (
        6,
        "ExtendedAE",
        guides.validate_extendedae_batch_06,
        PROJECT_ROOT / "working/ae2_addons/batch_06_completion.json",
        12,
    ),
    (
        7,
        "AdvancedAE",
        guides.validate_advancedae_batch_07,
        PROJECT_ROOT / "working/ae2_addons/batch_07_completion.json",
        8,
    ),
    (
        8,
        "AdvancedAE",
        guides.validate_advancedae_batch_08,
        PROJECT_ROOT / "working/ae2_addons/batch_08_completion.json",
        5,
    ),
    (
        9,
        "MEGA Cells",
        guides.validate_megacells_batch_09,
        PROJECT_ROOT / "working/ae2_addons/batch_09_completion.json",
        4,
    ),
    (
        10,
        "MEGA Cells",
        guides.validate_megacells_batch_10,
        PROJECT_ROOT / "working/ae2_addons/batch_10_completion.json",
        3,
    ),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    errors: list[str] = []
    batch_results = []
    for batch, mod_name, validator, completion_path, expected_guide_pages in BATCHES:
        validation = validator(instance, compare_output=True)
        validation_errors = validation["errors"]
        assert isinstance(validation_errors, list)
        errors.extend(f"{mod_name}: {error}" for error in validation_errors)

        if not completion_path.is_file():
            errors.append(f"{mod_name}: 완료 기록이 없습니다: {completion_path}")
        else:
            completion = json.loads(completion_path.read_text(encoding="utf-8"))
            if completion.get("guide_pages") != expected_guide_pages:
                errors.append(f"{mod_name}: 완료 기록의 가이드 페이지 수가 다릅니다.")
            if completion.get("language_keys") != len(validation["translated_lang"]):
                errors.append(f"{mod_name}: 완료 기록의 언어 키 수가 다릅니다.")
            if completion.get("validation", {}).get("utf8_bom_files") != 0:
                errors.append(f"{mod_name}: 완료 기록에 UTF-8 BOM 오류가 있습니다.")

        batch_results.append(
            {
                "batch": batch,
                "mod": mod_name,
                "guide_pages": expected_guide_pages,
                "language_keys": len(validation["translated_lang"]),
            }
        )

    if errors:
        raise ValueError("\n".join(errors))

    result = {
        "batches": batch_results,
        "guide_pages": sum(row["guide_pages"] for row in batch_results),
        "language_keys": sum(row["language_keys"] for row in batch_results),
        "working_output_match": True,
        "missing_files": 0,
        "extra_files": 0,
        "broken_references": 0,
        "resource_id_errors": 0,
        "protected_syntax_errors": 0,
        "placeholder_errors": 0,
        "english_paragraph_candidates": 0,
        "utf8_bom_files": 0,
        "validation_errors": 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
