#!/usr/bin/env python3
"""8.1 품질 재검수 계열의 FTB Quests 수정본을 검증하고 분할 산출물에 반영한다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from build_ae2_quests import TranslationValue
from build_ae2_quests import parse_language_snbt
from build_ae2_quests import validate_value
from ftbquests_layout import split_locale_files
from local_paths import resolve_source_root
from rebase_ftbquests import MANUAL_OVERRIDES
from rebase_ftbquests import OUTPUT_SPLIT_ROOT
from rebase_ftbquests import VALIDATION_ERROR_EXCEPTIONS
from rebase_ftbquests import serialize_file
from verify_quality_rereview import QUEST_LANG
from verify_quality_rereview import git_language_snbt
from version_context import active_report_dir

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REREVIEW_ROOT = PROJECT_ROOT / "working/quality_rereview"
LICENSE_PREFIX = "This Quest has been authored by"
LICENSE_TEXT = (
    "이 퀘스트는 AllTheMods 모드팩에 쓰기 위해 &6AllTheMods 스태프&r 또는 "
    "&2커뮤니티 기여자&r가 작성했습니다.\\n\\n모든 &6AllTheMods&r 모드팩은 "
    "&eAll Rights Reserved&r 라이선스를 따르므로, &6AllTheMods 팀&r이 배포하지 "
    "않은 공개 모드팩에서는 명시적인 허가 없이 이 퀘스트를 사용할 수 없습니다."
    "\\n\\n이 퀘스트는 일부러 숨겨 두었습니다. 이 메시지가 보인다면 편집 모드인 "
    "상태입니다."
)
# 번역체·오역을 찾는 신호. 오류 목록이 아니라 남은 문장을 다시 확인하기 위한 검색어다.
STYLE_SIGNALS = (
    "당신",
    "그것은",
    "그것을",
    "그것이",
    "여러분",
    "것입니다",
    "하십시오",
    "에 의해",
    "를 위한",
    "을 위한",
    "하는 것이 가능",
    "을 가지고 있",
    "를 가지고 있",
    "상위 버전으로 변환",
    "어플라이드 에너제틱스",
    "레이저IO",
    "모던 인더스트리얼라이제이션",
    "신비농업",
)


def load_revisions(family: str) -> dict[str, dict[str, TranslationValue]]:
    """계열 작업 폴더의 파일별 수정본을 읽는다."""
    root = REREVIEW_ROOT / family / "quests"
    revisions: dict[str, dict[str, TranslationValue]] = {}
    for path in sorted(root.glob("*.json")):
        relative = path.stem + ".snbt"
        if path.stem not in {"chapter", "chapter_group", "file", "reward_table"}:
            relative = f"chapters/{relative}"
        revisions[relative] = json.loads(path.read_text(encoding="utf-8"))
    return revisions


def load_scope(family: str) -> dict[str, Any]:
    """계열이 검수 대상으로 삼는 분할 언어 파일 목록과 기준 커밋을 읽는다."""
    path = REREVIEW_ROOT / family / "scope.json"
    return json.loads(path.read_text(encoding="utf-8"))


def signal_hits(value: TranslationValue) -> list[str]:
    text = "\n".join(value) if isinstance(value, list) else value
    return [signal for signal in STYLE_SIGNALS if signal in text]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", help="working/quality_rereview 아래 계열 폴더 이름")
    parser.add_argument("--instance", type=Path)
    parser.add_argument(
        "--write-output",
        action="store_true",
        help="검증된 수정본을 output 분할 파일과 8.1 수동 검수 목록에 기록한다.",
    )
    args = parser.parse_args()

    instance = resolve_source_root(args.instance)
    english_files = split_locale_files(instance, "en_us")
    scope_data = load_scope(args.family)
    scope = list(scope_data["quest_files"])
    revisions = load_revisions(args.family)
    english_by_relative: dict[str, str] = {}
    for relative in english_files:
        english_by_relative[relative.removesuffix("_merged")] = relative
    unknown_files = sorted(set(revisions) - set(scope))
    if unknown_files:
        raise ValueError(f"검수 범위 밖의 수정 파일: {unknown_files}")

    manual: dict[str, TranslationValue] = json.loads(
        MANUAL_OVERRIDES.read_text(encoding="utf-8")
    )
    errors: list[str] = []
    report_files: dict[str, dict[str, Any]] = {}
    remaining_signals: dict[str, list[str]] = {}
    outputs: dict[Path, str] = {}
    for relative in scope:
        english_path = english_files[english_by_relative[relative]]
        english = parse_language_snbt(english_path)
        output_path = OUTPUT_SPLIT_ROOT / relative
        current = parse_language_snbt(output_path)
        baseline = git_language_snbt(
            scope_data["baseline_commit"], f"{QUEST_LANG}/{relative}"
        )
        file_revisions = dict(revisions.get(relative, {}))
        for key, source in english.items():
            if (
                key in current
                and key not in file_revisions
                and isinstance(source, list)
                and source
                and source[0].startswith(LICENSE_PREFIX)
            ):
                file_revisions[key] = [LICENSE_TEXT]

        changed: list[str] = []
        updated = dict(current)
        for key, value in file_revisions.items():
            if key not in english:
                errors.append(f"{relative}: 영어 원문에 없는 키 {key}")
                continue
            if key not in current:
                errors.append(f"{relative}: 기존 산출물에 없는 키 {key}")
                continue
            ignored = VALIDATION_ERROR_EXCEPTIONS.get(key, set())
            errors.extend(
                f"{relative}: {error}"
                for error in validate_value(key, english[key], value)
                if not any(error.endswith(reason) for reason in ignored)
            )
            if value != current[key]:
                updated[key] = value
                changed.append(key)

        entries = [(key, updated[key]) for key in english if key in updated]
        outputs[output_path] = serialize_file(entries)
        for key, value in updated.items():
            hits = signal_hits(value)
            if hits:
                remaining_signals[f"{relative}:{key}"] = hits
        for key in changed:
            manual[key] = updated[key]
        # 수정 수는 재실행해도 같도록 계열 시작 기준 커밋과 비교한다.
        revised = [key for key in updated if updated[key] != baseline.get(key)]
        report_files[relative] = {
            "english_keys": len(english),
            "translated_keys": len(updated),
            "revised": len(revised),
            "kept": len(updated) - len(revised),
            "revised_keys": revised,
        }

    report = {
        "family": args.family,
        "files": report_files,
        "english_keys": sum(item["english_keys"] for item in report_files.values()),
        "translated_keys": sum(
            item["translated_keys"] for item in report_files.values()
        ),
        "revised": sum(item["revised"] for item in report_files.values()),
        "kept": sum(item["kept"] for item in report_files.values()),
        "remaining_style_signals": remaining_signals,
        "errors": errors,
    }
    report_path = active_report_dir() / f"quality_rereview_{args.family}_quests.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {key: value for key, value in report.items() if key != "files"},
            ensure_ascii=False,
            indent=2,
        )
    )
    if errors:
        return 1
    if args.write_output:
        for path, text in outputs.items():
            path.write_text(text, encoding="utf-8")
        MANUAL_OVERRIDES.write_text(
            json.dumps(manual, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
