#!/usr/bin/env python3
"""AE2 연동 모드 가이드 작업본과 리소스팩 산출물을 읽기 전용으로 검증한다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import build_ae2_addon_guides as guides
from local_paths import resolve_source_root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    validation = guides.validate(instance, compare_output=True)
    errors = validation["errors"]
    assert isinstance(errors, list)

    if not guides.PROGRESS_FILE.is_file():
        errors.append(f"진행 기록이 없습니다: {guides.PROGRESS_FILE}")
    else:
        progress = json.loads(guides.PROGRESS_FILE.read_text(encoding="utf-8"))
        if progress.get("batch") != guides.ACTIVE_BATCH:
            errors.append("진행 기록의 배치 번호가 다릅니다.")
        if progress.get("guide_pages") != validation["guide_pages"]:
            errors.append("진행 기록의 가이드 페이지 수가 다릅니다.")
        if progress.get("language_keys") != len(validation["translated_lang"]):
            errors.append("진행 기록의 언어 키 수가 다릅니다.")
        if progress.get("validation_errors") != 0:
            errors.append("진행 기록에 검증 오류가 남아 있습니다.")

    if errors:
        raise ValueError("\n".join(errors))

    result = {
        "batch": guides.ACTIVE_BATCH,
        "guide_pages": validation["guide_pages"],
        "new_guide_pages": validation["new_guide_pages"],
        "core_compatibility_updates": validation["core_compatibility_updates"],
        "language_keys": len(validation["translated_lang"]),
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
