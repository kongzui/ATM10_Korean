#!/usr/bin/env python3
"""Relics·Artifacts 계열의 완료 보고와 실제 적용 상태를 교차 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import build_ae2_quests as snbt
import verify_relics
from local_paths import PROJECT_ROOT, resolve_source_root
from relics_catalog import TARGETS

WORK_ROOT = PROJECT_ROOT / "working/relics"
COMPLETION_FILE = WORK_ROOT / "family_completion.json"
RELATED_FILE = WORK_ROOT / "related_content_audit.json"
QUEST_REPORT = WORK_ROOT / "quest_validation.json"
REPORT_FILE = WORK_ROOT / "family_validation.json"
EXPECTED_DEPLOYMENTS = {
    "resourcepacks/ATM10_Korean/assets/artifacts/lang/ko_kr.json": (
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/artifacts/lang/ko_kr.json"
    ),
    "resourcepacks/ATM10_Korean/assets/relics/lang/ko_kr.json": (
        PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/relics/lang/ko_kr.json"
    ),
    "resourcepacks/ATM10_Korean/assets/reliquified_artifacts/lang/ko_kr.json": (
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/reliquified_artifacts/lang/ko_kr.json"
    ),
    "config/ftbquests/quests/lang/ko_kr.snbt": (
        PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
    ),
    "config/ftbquests/quests/chapters/relics.snbt": (
        PROJECT_ROOT / "output/overrides/config/ftbquests/quests/chapters/relics.snbt"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    completion = json.loads(COMPLETION_FILE.read_text(encoding="utf-8"))
    related = json.loads(RELATED_FILE.read_text(encoding="utf-8"))
    quest = json.loads(QUEST_REPORT.read_text(encoding="utf-8"))
    errors: list[str] = []

    language_rows = [
        verify_relics.verify_target(instance, target, copy_output=False)
        for target in TARGETS
    ]
    language_keys = sum(int(row["keys"]) for row in language_rows)
    if language_keys != completion["counts"]["language_keys"]:
        errors.append("언어 키 합계가 완료 보고와 다릅니다.")
    count_sum = sum(
        completion["counts"][key]
        for key in (
            "language_existing_korean_reused",
            "language_existing_korean_corrected",
            "language_newly_translated",
        )
    )
    if count_sum != language_keys:
        errors.append("언어 재사용·교정·신규 분류 합계가 전체 키 수와 다릅니다.")
    if quest["validation_errors"] or quest["unclassified_english"]:
        errors.append("FTB Quests 검증 보고에 해결되지 않은 오류가 있습니다.")
    if related["kubejs"]["direct_user_literals_remaining"] != 0:
        errors.append("KubeJS 직접 표시 문구가 남았습니다.")
    if related["review_items"] or completion["review_items"]:
        errors.append("수동 검토 항목이 남았습니다.")
    if completion["status"] != "complete":
        errors.append("모드군 완료 상태가 complete가 아닙니다.")

    snbt.parse_language_snbt(
        EXPECTED_DEPLOYMENTS["config/ftbquests/quests/lang/ko_kr.snbt"]
    )
    live_hash_matches = 0
    for relative, source in EXPECTED_DEPLOYMENTS.items():
        target = instance / relative
        if not target.is_file():
            errors.append(f"실제 적용 파일이 없습니다: {target}")
        elif sha256(source) != sha256(target):
            errors.append(f"실제 적용 파일 해시가 산출물과 다릅니다: {relative}")
        else:
            live_hash_matches += 1

    report = {
        "scope": "Relics and Artifacts family completion",
        "language_namespaces_checked": len(language_rows),
        "language_keys_checked": language_keys,
        "quest_display_keys_checked": quest["display_keys_checked"],
        "literal_hover_checked": quest["literal_hover_translated"],
        "live_hash_matches": live_hash_matches,
        "expected_live_files": len(EXPECTED_DEPLOYMENTS),
        "remaining": completion["counts"]["remaining"],
        "validation_errors": len(errors),
        "errors": errors,
    }
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
