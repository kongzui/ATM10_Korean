#!/usr/bin/env python3
"""Iron Jetpacks와 장비 편의 모드군의 검수 번역을 적용한다."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from five_family_goal import is_allowed_original
from local_paths import PROJECT_ROOT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/iron_jetpacks_equipment"
OVERRIDES_FILE = WORK_ROOT / "manual_overrides.json"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


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
            target = overrides.get(key)
            if target is not None:
                korean[key] = preserve_line_break_style(source, target)
                sources[key] = "manual_translation"
                changed += 1
            elif source == korean[key]:
                if isinstance(source, str) and is_allowed_original(source):
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
