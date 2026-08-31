#!/usr/bin/env python3
"""ATM10 두 버전의 모드 언어 원문과 현재 번역 산출물의 재검토 범위를 계산한다."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from local_paths import resolve_source_root
from version_context import active_output_root, active_pack_version, active_report_dir
from version_context import baseline_pack_version

LANG_RE = re.compile(r"^assets/([^/]+)/lang/(en_us|ko_kr)\.json$", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_RE = re.compile(r"(?:§|&)[0-9a-fk-or]", re.IGNORECASE)
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"
REPORT_JSON = active_report_dir() / "mod_language_rebase_audit.json"
REPORT_MD = active_report_dir() / "mod_language_rebase_audit.md"


def load_languages(
    instance: Path,
) -> tuple[
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    dict[str, list[str]],
    list[str],
    list[str],
]:
    """모든 JAR의 영어·한국어 언어 파일을 네임스페이스별로 합친다."""
    english: dict[str, dict[str, str]] = defaultdict(dict)
    korean: dict[str, dict[str, str]] = defaultdict(dict)
    sources: dict[str, list[str]] = defaultdict(list)
    conflicts: list[str] = []
    read_errors: list[str] = []
    for jar in sorted(
        (instance / "mods").glob("*.jar"), key=lambda item: item.name.lower()
    ):
        with zipfile.ZipFile(jar) as archive:
            for name in sorted(archive.namelist()):
                match = LANG_RE.fullmatch(name)
                if not match:
                    continue
                namespace = match.group(1).lower()
                locale = match.group(2).lower()
                try:
                    raw = json.loads(archive.read(name).decode("utf-8-sig"))
                except (UnicodeDecodeError, json.JSONDecodeError) as error:
                    read_errors.append(
                        f"{jar.name}:{name}:{type(error).__name__}:{error}"
                    )
                    continue
                if not isinstance(raw, dict):
                    raise TypeError(
                        f"언어 JSON 최상위 값이 객체가 아닙니다: {jar.name}:{name}"
                    )
                target = english if locale == "en_us" else korean
                for key, value in raw.items():
                    if not isinstance(value, str):
                        continue
                    previous = target[namespace].get(key)
                    if previous is not None and previous != value:
                        conflicts.append(
                            f"{namespace}:{locale}:{key}:{jar.name}:{name}"
                        )
                        continue
                    target[namespace][key] = value
                sources[namespace].append(f"{jar.name}:{name}")
    return dict(english), dict(korean), dict(sources), conflicts, read_errors


def load_output(namespace: str) -> dict[str, str]:
    """현재 버전의 프로젝트 한국어 언어 파일을 읽는다."""
    path = OUTPUT_ASSETS / namespace / "lang/ko_kr.json"
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"번역 JSON 최상위 값이 객체가 아닙니다: {path}")
    return {key: item for key, item in value.items() if isinstance(item, str)}


def validation_errors(
    namespace: str,
    english: dict[str, str],
    korean: dict[str, str],
) -> list[str]:
    """현재 영어와 번역의 자리표시자·서식 코드를 비교한다."""
    errors: list[str] = []
    for key in sorted(set(english) & set(korean)):
        source = english[key]
        translated = korean[key]
        if PLACEHOLDER_RE.findall(source) != PLACEHOLDER_RE.findall(translated):
            errors.append(f"{namespace}:{key}: 자리표시자 불일치")
        if FORMAT_RE.findall(source) != FORMAT_RE.findall(translated):
            errors.append(f"{namespace}:{key}: 서식 코드 불일치")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--base-instance", type=Path, required=True)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    base_instance = args.base_instance.resolve()

    current_en, current_ko, current_sources, current_conflicts, current_errors = (
        load_languages(instance)
    )
    base_en, _, _, base_conflicts, base_errors = load_languages(base_instance)
    translated_namespaces = {
        path.parent.parent.name.lower()
        for path in OUTPUT_ASSETS.glob("*/lang/ko_kr.json")
    }

    rows: list[dict[str, Any]] = []
    all_errors: list[str] = []
    for namespace in sorted(set(current_en) | translated_namespaces):
        current = current_en.get(namespace, {})
        baseline = base_en.get(namespace, {})
        output = load_output(namespace)
        unchanged = {
            key for key, value in current.items() if baseline.get(key) == value
        }
        changed = {
            key
            for key, value in current.items()
            if key in baseline and baseline[key] != value
        }
        added = set(current) - set(baseline)
        removed = set(baseline) - set(current)
        reusable = unchanged & set(output)
        unchanged_missing = unchanged - set(output)
        queue = changed | added
        installed_candidates = queue & set(current_ko.get(namespace, {}))
        errors = validation_errors(namespace, current, output)
        all_errors.extend(errors)
        rows.append(
            {
                "namespace": namespace,
                "translated_output": namespace in translated_namespaces,
                "current_english_keys": len(current),
                "output_korean_keys": len(output),
                "unchanged_reusable_keys": len(reusable),
                "unchanged_missing_keys": len(unchanged_missing),
                "unchanged_missing_key_names": sorted(unchanged_missing),
                "changed_source_keys": len(changed),
                "changed_source_key_names": sorted(changed),
                "added_source_keys": len(added),
                "added_source_key_names": sorted(added),
                "review_queue_keys": len(queue),
                "review_queue_key_names": sorted(queue),
                "installed_korean_candidates": len(installed_candidates),
                "removed_source_keys": len(removed),
                "removed_source_key_names": sorted(removed),
                "output_only_keys": len(set(output) - set(current)),
                "output_only_key_names": sorted(set(output) - set(current)),
                "validation_errors": len(errors),
                "validation_error_details": errors,
                "sources": current_sources.get(namespace, []),
            }
        )

    affected = [
        row
        for row in rows
        if row["translated_output"]
        and (
            row["review_queue_keys"]
            or row["removed_source_keys"]
            or row["unchanged_missing_keys"]
        )
    ]
    added_candidates = [
        row
        for row in rows
        if not row["translated_output"]
        and row["namespace"] not in base_en
        and row["current_english_keys"]
    ]
    report = {
        "pack_version": active_pack_version(),
        "baseline_pack_version": baseline_pack_version(),
        "translated_output_namespaces": len(translated_namespaces),
        "affected_translated_namespaces": len(affected),
        "review_queue_keys": sum(int(row["review_queue_keys"]) for row in affected),
        "unchanged_reusable_keys": sum(
            int(row["unchanged_reusable_keys"]) for row in affected
        ),
        "removed_source_keys": sum(int(row["removed_source_keys"]) for row in affected),
        "validation_errors": all_errors,
        "validation_error_counts": dict(
            sorted(Counter(error.partition(":")[0] for error in all_errors).items())
        ),
        "source_conflicts": {
            "current": current_conflicts,
            "baseline": base_conflicts,
        },
        "source_read_errors": {
            "current": current_errors,
            "baseline": base_errors,
        },
        "affected": sorted(
            affected,
            key=lambda row: (-int(row["review_queue_keys"]), str(row["namespace"])),
        ),
        "new_namespace_candidates": sorted(
            added_candidates,
            key=lambda row: (-int(row["current_english_keys"]), str(row["namespace"])),
        ),
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        f"# ATM10 {active_pack_version()} 모드 언어 재검토 감사",
        "",
        f"- 기존 번역 네임스페이스: {len(translated_namespaces):,}개",
        f"- 변경 영향 네임스페이스: {len(affected):,}개",
        f"- 변경·신규 원문 검토 키: {report['review_queue_keys']:,}개",
        f"- 그대로 재사용 가능한 키: {report['unchanged_reusable_keys']:,}개",
        f"- 현재 원문에서 제거된 키: {report['removed_source_keys']:,}개",
        f"- 자리표시자·서식 오류: {len(all_errors):,}개",
        f"- 신규 네임스페이스 후보: {len(added_candidates):,}개 "
        f"({sum(int(row['current_english_keys']) for row in added_candidates):,}키)",
        "",
        "## 변경 영향 네임스페이스",
        "",
        "| 네임스페이스 | 검토 키 | 변경 | 신규 | 제거 | 그대로 재사용 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["affected"]:
        lines.append(
            f"| {row['namespace']} | {row['review_queue_keys']} | "
            f"{row['changed_source_keys']} | {row['added_source_keys']} | "
            f"{row['removed_source_keys']} | {row['unchanged_reusable_keys']} |"
        )
    lines.extend(
        [
            "",
            "## 신규 네임스페이스 후보",
            "",
            "| 네임스페이스 | 영어 키 | 설치본 한국어 후보 |",
            "|---|---:|---:|",
        ]
    )
    for row in report["new_namespace_candidates"]:
        lines.append(
            f"| {row['namespace']} | {row['current_english_keys']} | "
            f"{row['installed_korean_candidates']} |"
        )
    lines.extend(
        [
            "",
            "## 자동 검사 주의 사항",
            "",
            f"- 현재 JAR 중복 원문 충돌 기록: {len(current_conflicts):,}개",
            f"- 기준 JAR 중복 원문 충돌 기록: {len(base_conflicts):,}개",
            f"- 현재 JAR 언어 파일 읽기 오류: {len(current_errors):,}개",
            f"- 기준 JAR 언어 파일 읽기 오류: {len(base_errors):,}개",
            "- 자세한 키와 파일 경로는 같은 이름의 JSON 보고서에 기록했습니다.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: value
                for key, value in report.items()
                if key
                not in {"affected", "new_namespace_candidates", "validation_errors"}
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
