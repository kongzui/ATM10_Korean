#!/usr/bin/env python3
"""이전 검수 번역을 현재 ATM10의 분할 FTB Quests 언어 구조로 재기준화한다."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from build_ae2_quests import TranslationValue
from build_ae2_quests import parse_language_snbt
from build_ae2_quests import serialize_snbt
from build_ae2_quests import validate_value
from ftbquests_layout import output_merged_locale_file
from ftbquests_layout import split_locale_files
from local_paths import resolve_source_root
from version_context import active_manifest_dir
from version_context import active_output_root
from version_context import active_pack_version
from version_context import active_report_dir
from version_context import baseline_pack_version

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_SPLIT_ROOT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr"
)
BASELINE_TRANSLATION = (
    PROJECT_ROOT
    / "output"
    / baseline_pack_version()
    / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
MANUAL_OVERRIDES = (
    PROJECT_ROOT / "working/ftbquests" / f"{active_pack_version()}_overrides.json"
)
REVIEWED_BASELINE_KEYS = (
    PROJECT_ROOT
    / "working/ftbquests"
    / f"{active_pack_version()}_reviewed_baseline_keys.json"
)
OMITTED_KEYS = (
    PROJECT_ROOT / "working/ftbquests" / f"{active_pack_version()}_omitted_keys.json"
)
REVIEW_QUEUE = (
    PROJECT_ROOT / "working/ftbquests" / f"{active_pack_version()}_review_queue.json"
)
REPORT_JSON = active_report_dir() / "ftbquests_rebase.json"
REPORT_MD = active_report_dir() / "ftbquests_rebase.md"
ENGLISH_MANIFEST = active_manifest_dir() / "ftbquests_english_hashes.json"


def load_split(
    instance: Path, locale: str
) -> tuple[dict[str, TranslationValue], dict[str, str]]:
    """분할 언어 파일 전체와 키별 소속 파일을 읽는다."""
    values: dict[str, TranslationValue] = {}
    key_files: dict[str, str] = {}
    for relative, path in split_locale_files(instance, locale).items():
        for key, value in parse_language_snbt(path).items():
            if key in values:
                raise ValueError(
                    f"{locale} 키가 여러 파일에 있습니다: "
                    f"{key} ({key_files[key]}, {relative})"
                )
            values[key] = value
            key_files[key] = relative
    return values, key_files


def value_hash(value: TranslationValue) -> str:
    """문자열 또는 문단 배열을 안정적인 해시로 만든다."""
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def serialize_file(entries: list[tuple[str, TranslationValue]]) -> str:
    """키 순서를 보존한 분할 언어 SNBT를 만든다."""
    lines = ["{"]
    for key, value in entries:
        serialized = serialize_snbt(value).replace("\n", "\n\t")
        lines.append(f"\t{key}: {serialized}")
    lines.append("}")
    return "\n".join(lines) + "\n"


def write_outputs(
    english_files: dict[str, Path],
    selected: dict[str, TranslationValue],
) -> None:
    """현재 영어 파일과 같은 분할 구조로 검증된 번역만 기록한다."""
    OUTPUT_SPLIT_ROOT.mkdir(parents=True, exist_ok=True)
    expected_paths: set[Path] = set()
    for relative, english_path in english_files.items():
        english_entries = parse_language_snbt(english_path)
        translated = [
            (key, selected[key]) for key in english_entries if key in selected
        ]
        output_path = OUTPUT_SPLIT_ROOT / relative
        expected_paths.add(output_path.resolve())
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(serialize_file(translated), encoding="utf-8")

    for path in sorted(OUTPUT_SPLIT_ROOT.rglob("*"), reverse=True):
        if path.is_file() and path.resolve() not in expected_paths:
            path.unlink()
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()

    stale_merged = output_merged_locale_file()
    if stale_merged.is_file():
        stale_merged.unlink()


def write_reports(
    english: dict[str, TranslationValue],
    key_files: dict[str, str],
    source_by_key: dict[str, str],
    omitted: dict[str, str],
    queue: dict[str, dict[str, Any]],
    validation_errors: list[str],
) -> dict[str, Any]:
    """재사용 근거, 검토 대기열과 현재 진행률을 기록한다."""
    source_counts = Counter(source_by_key.values())
    unresolved_by_file = Counter(item["file"] for item in queue.values())
    report = {
        "pack_version": active_pack_version(),
        "baseline_pack_version": baseline_pack_version(),
        "english_keys": len(english),
        "selected_keys": len(source_by_key),
        "intentionally_omitted_keys": len(omitted),
        "unresolved_keys": len(queue),
        "source_counts": dict(sorted(source_counts.items())),
        "unresolved_by_file": dict(
            sorted(unresolved_by_file.items(), key=lambda item: (-item[1], item[0]))
        ),
        "validation_errors": validation_errors,
        "full_translation_ready": not queue and not validation_errors,
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    REVIEW_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_QUEUE.write_text(
        json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    manifest = {
        "pack_version": active_pack_version(),
        "key_count": len(english),
        "keys": {
            key: {"file": key_files[key], "sha256": value_hash(value)}
            for key, value in english.items()
        },
    }
    ENGLISH_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    ENGLISH_MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        f"# ATM10 {active_pack_version()} FTB Quests 재기준화",
        "",
        f"- 현재 영어 키: {len(english):,}개",
        f"- 검증되어 분할 산출물에 포함된 키: {len(source_by_key):,}개",
        f"- 자동 fallback을 위해 의도적으로 생략한 키: {len(omitted):,}개",
        f"- 수동 검토 대기 키: {len(queue):,}개",
        f"- 구조 검증 오류: {len(validation_errors):,}개",
        f"- 전체 번역 준비: {'예' if report['full_translation_ready'] else '아니요'}",
        "",
        "## 번역 출처",
        "",
    ]
    lines.extend(f"- {source}: {count:,}개" for source, count in source_counts.items())
    lines.extend(["", "## 검토 대기 파일", ""])
    lines.extend(
        f"- `{path}`: {count:,}개" for path, count in unresolved_by_file.items()
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--base-instance", type=Path, required=True)
    parser.add_argument(
        "--write-output",
        action="store_true",
        help="검증된 키를 현재 버전의 분할 output에 기록한다.",
    )
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    base_instance = args.base_instance.resolve()
    base_english_path = base_instance / "config/ftbquests/quests/lang/en_us.snbt"
    if not base_english_path.is_file():
        raise FileNotFoundError(f"기준 영어 파일이 없습니다: {base_english_path}")
    if not BASELINE_TRANSLATION.is_file():
        raise FileNotFoundError(f"기준 번역 파일이 없습니다: {BASELINE_TRANSLATION}")

    english_files = split_locale_files(instance, "en_us")
    if not english_files:
        raise FileNotFoundError(f"현재 영어 분할 언어 파일이 없습니다: {instance}")
    english, key_files = load_split(instance, "en_us")
    installed_korean, _ = load_split(instance, "ko_kr")
    base_english = parse_language_snbt(base_english_path)
    baseline_korean = parse_language_snbt(BASELINE_TRANSLATION)
    manual: dict[str, TranslationValue] = {}
    if MANUAL_OVERRIDES.is_file():
        manual = json.loads(MANUAL_OVERRIDES.read_text(encoding="utf-8"))
    reviewed_baseline_keys: set[str] = set()
    if REVIEWED_BASELINE_KEYS.is_file():
        reviewed_baseline_keys = set(
            json.loads(REVIEWED_BASELINE_KEYS.read_text(encoding="utf-8"))
        )
    omitted: dict[str, str] = {}
    if OMITTED_KEYS.is_file():
        omitted = json.loads(OMITTED_KEYS.read_text(encoding="utf-8"))
    unknown_manual = sorted(set(manual) - set(english))
    if unknown_manual:
        raise ValueError(f"현재 영어 원문에 없는 수동 번역 키: {unknown_manual}")
    invalid_reviewed = sorted(
        key
        for key in reviewed_baseline_keys
        if key not in english or key not in baseline_korean
    )
    if invalid_reviewed:
        raise ValueError(f"재사용할 수 없는 검수 키: {invalid_reviewed}")
    unknown_omitted = sorted(set(omitted) - set(english))
    if unknown_omitted:
        raise ValueError(f"현재 영어 원문에 없는 생략 키: {unknown_omitted}")
    overlap = sorted(set(manual) & set(omitted))
    if overlap:
        raise ValueError(f"수동 번역과 생략 목록에 동시에 있는 키: {overlap}")

    selected: dict[str, TranslationValue] = {}
    source_by_key: dict[str, str] = {}
    queue: dict[str, dict[str, Any]] = {}
    validation_errors: list[str] = []
    for key, source in english.items():
        if key in omitted:
            continue
        translated: TranslationValue | None = None
        source_name = ""
        if key in manual:
            translated = manual[key]
            source_name = "8.1 수동 검수"
        elif key in reviewed_baseline_keys:
            translated = baseline_korean[key]
            source_name = "8.1 변경 확인 후 7.1 검수 번역 재사용"
        elif base_english.get(key) == source and key in baseline_korean:
            translated = baseline_korean[key]
            source_name = "7.1 검수 번역 재사용"

        if translated is not None:
            errors = validate_value(key, source, translated)
            if not errors:
                selected[key] = translated
                source_by_key[key] = source_name
                continue
            validation_errors.extend(errors)

        reason = "신규 키"
        if key in base_english:
            reason = "영어 원문 변경"
        elif key in baseline_korean:
            reason = "기준 영어에 없는 기존 번역"
        queue[key] = {
            "file": key_files[key],
            "reason": reason,
            "english": source,
            "baseline_english": base_english.get(key),
            "baseline_translation": baseline_korean.get(key),
            "installed_korean_candidate": installed_korean.get(key),
        }

    if args.write_output:
        write_outputs(english_files, selected)
    report = write_reports(
        english,
        key_files,
        source_by_key,
        omitted,
        queue,
        validation_errors,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
