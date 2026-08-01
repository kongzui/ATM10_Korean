#!/usr/bin/env python3
"""Functional Storage·Pocket Storage·EnderStorage 검수 번역을 적용한다."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from five_family_goal import is_allowed_original
from local_paths import PROJECT_ROOT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/functional_storage"
OVERRIDES_FILE = WORK_ROOT / "manual_overrides.json"

REPLACEMENTS = (
    ("액체", "유체"),
    ("텍스쳐", "텍스처"),
    ("웅크린채로", "웅크린 채로"),
)


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize(value: object) -> object:
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if not isinstance(value, str):
        return value
    for source, target in REPLACEMENTS:
        value = value.replace(source, target)
    return value


def preserve_line_break_style(source: object, target: object) -> object:
    if isinstance(source, list) and isinstance(target, list):
        return [
            preserve_line_break_style(source_item, target_item)
            for source_item, target_item in zip(source, target)
        ]
    if not isinstance(source, str) or not isinstance(target, str):
        return target
    if source.count("\\n") == target.count("\n") and "\n" not in source:
        return target.replace("\n", "\\n")
    return target


def main() -> int:
    overrides = read_json(OVERRIDES_FILE)
    unresolved: list[str] = []
    changed = 0
    for english_file in sorted(WORK_ROOT.rglob("en_us.json")):
        root = english_file.parent
        korean_file = root / "ko_kr.json"
        sources_file = root / "candidate_sources.json"
        if not korean_file.is_file() or not sources_file.is_file():
            continue
        english = read_json(english_file)
        korean = read_json(korean_file)
        sources = read_json(sources_file)
        for key, source in english.items():
            if key in overrides:
                target = preserve_line_break_style(source, overrides[key])
                korean[key] = target
                sources[key] = "manual_translation"
                changed += 1
                continue
            normalized = normalize(korean[key])
            if normalized != korean[key]:
                korean[key] = normalized
                sources[key] = "manual_translation"
                changed += 1
            if source == korean[key]:
                source_text = "\n".join(source) if isinstance(source, list) else source
                if isinstance(source_text, str) and is_allowed_original(source_text):
                    sources[key] = "reviewed_original"
                else:
                    unresolved.append(key)
        write_json(korean_file, korean)
        write_json(sources_file, sources)
    report = {"changed": changed, "unresolved": unresolved}
    write_json(WORK_ROOT / "manual_translation_report.json", report)
    print(f"수동 검수 번역 반영: {changed}키, 미해결 {len(unresolved)}키")
    for key in unresolved:
        print(f"- {key}")
    return 1 if unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
