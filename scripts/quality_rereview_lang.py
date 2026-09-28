#!/usr/bin/env python3
"""8.1 품질 재검수 계열의 언어 파일 수정본을 현재 JAR 영어로 검증하고 산출물에 반영한다."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from typing import Any

from local_paths import resolve_source_root
from quality_rereview_quests import STYLE_SIGNALS
from verify_quality_rereview import PACK_ASSETS
from verify_quality_rereview import git_text
from version_context import active_output_root
from version_context import active_report_dir

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REREVIEW_ROOT = PROJECT_ROOT / "working/quality_rereview"
PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{\d+\}")
FORMAT_RE = re.compile(r"[&§][0-9a-fk-or]", re.IGNORECASE)


def jar_english(instance: Path, namespaces: list[str]) -> dict[str, dict[str, str]]:
    """설치된 JAR의 네임스페이스별 영어 언어 파일을 읽는다."""
    english: dict[str, dict[str, str]] = {namespace: {} for namespace in namespaces}
    wanted = {
        f"assets/{namespace}/lang/en_us.json": namespace for namespace in namespaces
    }
    for jar in sorted((instance / "mods").glob("*.jar")):
        with zipfile.ZipFile(jar) as archive:
            for name in set(archive.namelist()) & set(wanted):
                data = json.loads(archive.read(name).decode("utf-8-sig"))
                english[wanted[name]].update(
                    {
                        key: value
                        for key, value in data.items()
                        if isinstance(value, str)
                    }
                )
    return english


def check(key: str, english: str | None, old: str, new: str) -> list[str]:
    """자리표시자·서식 코드·줄바꿈을 영어(없으면 기존 번역) 기준으로 검사한다."""
    source = english if english is not None else old
    errors = []
    if sorted(PLACEHOLDER_RE.findall(new)) != sorted(PLACEHOLDER_RE.findall(source)):
        errors.append(f"{key}: 자리표시자 불일치")
    if sorted(FORMAT_RE.findall(new)) != sorted(FORMAT_RE.findall(source)):
        errors.append(f"{key}: 서식 코드 불일치")
    if new.count("\\n") != source.count("\\n") or new.count("\n") != source.count("\n"):
        errors.append(f"{key}: 줄바꿈 개수 불일치")
    if not new.strip() and source.strip():
        errors.append(f"{key}: 빈 번역")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", help="working/quality_rereview 아래 계열 폴더 이름")
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--write-output", action="store_true")
    args = parser.parse_args()

    root = REREVIEW_ROOT / args.family
    scope = json.loads((root / "scope.json").read_text(encoding="utf-8"))
    namespaces = list(scope["language_namespaces"])
    sources: dict[str, list[str]] = scope.get("language_sources", {})
    english = jar_english(resolve_source_root(args.instance), namespaces)
    output_root = active_output_root() / PACK_ASSETS

    errors: list[str] = []
    report_files: dict[str, dict[str, Any]] = {}
    signals: dict[str, list[str]] = {}
    writes: dict[Path, dict[str, str]] = {}
    for namespace in namespaces:
        output_path = output_root / namespace / "lang/ko_kr.json"
        current = json.loads(output_path.read_text(encoding="utf-8"))
        baseline = json.loads(
            git_text(
                scope["baseline_commit"], f"{PACK_ASSETS}/{namespace}/lang/ko_kr.json"
            )
        )
        revision_path = root / "lang" / f"{namespace}.json"
        revisions = (
            json.loads(revision_path.read_text(encoding="utf-8"))
            if revision_path.is_file()
            else {}
        )
        updated = dict(current)
        for key, value in revisions.items():
            if key not in current:
                errors.append(f"{namespace}: 기존 산출물에 없는 키 {key}")
                continue
            errors.extend(
                f"{namespace}: {error}"
                for error in check(
                    key, english[namespace].get(key), baseline[key], value
                )
            )
            updated[key] = value
        if list(updated) != list(baseline):
            errors.append(f"{namespace}: 기준 대비 키 목록이 달라요")
        writes[output_path] = updated
        for source in sources.get(namespace, []):
            source_path = PROJECT_ROOT / source
            source_data = json.loads(source_path.read_text(encoding="utf-8"))
            for key, value in revisions.items():
                if key in source_data:
                    if source_data[key] not in {baseline[key], current[key], value}:
                        errors.append(f"{source}:{key}: 작업 원본이 산출물과 달라요")
                    source_data[key] = value
            writes[source_path] = source_data
        for key, value in updated.items():
            hits = [signal for signal in STYLE_SIGNALS if signal in value]
            if hits:
                signals[f"{namespace}:{key}"] = hits
        revised = [key for key in updated if updated[key] != baseline[key]]
        report_files[namespace] = {
            "english_keys": len(english[namespace]),
            "translated_keys": len(updated),
            "keys_without_jar_english": len(set(updated) - set(english[namespace])),
            "revised": len(revised),
            "kept": len(updated) - len(revised),
            "revised_keys": revised,
        }

    report = {
        "family": args.family,
        "files": report_files,
        "translated_keys": sum(
            item["translated_keys"] for item in report_files.values()
        ),
        "revised": sum(item["revised"] for item in report_files.values()),
        "kept": sum(item["kept"] for item in report_files.values()),
        "remaining_style_signals": signals,
        "errors": errors,
    }
    report_path = active_report_dir() / f"quality_rereview_{args.family}_lang.json"
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
        for path, data in writes.items():
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
