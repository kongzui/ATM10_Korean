#!/usr/bin/env python3
"""Apotheosis 그림자의 연대기 영어 원문을 한국어 검수 작업본으로 준비한다."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_apotheosis import find_jar
from apotheosis_catalog import TARGETS

WORK_ROOT = PROJECT_ROOT / "working/apotheosis/guide/ko_kr"
REVIEW_QUEUE = PROJECT_ROOT / "working/apotheosis/guide/8.1_review_queue.json"
SOURCE_PREFIX = "assets/apotheosis/patchouli_books/apoth_chronicle/en_us/"
CORE_TARGET = next(target for target in TARGETS if target.namespace == "apotheosis")
TRANSLATABLE_FIELDS = {"name", "description", "title", "text"}


def rebase_value(
    current: object,
    baseline: object,
    previous: object,
    label: str,
    queue: dict[str, dict[str, Any]],
    counts: Counter[str],
) -> object:
    """현재 구조를 따르면서 원문이 같은 기존 검수 번역만 재사용한다."""
    if isinstance(current, dict):
        baseline_dict = baseline if isinstance(baseline, dict) else {}
        previous_dict = previous if isinstance(previous, dict) else {}
        result: dict[str, object] = {}
        for key, value in current.items():
            child = f"{label}.{key}"
            baseline_value = baseline_dict.get(key)
            previous_value = previous_dict.get(key)
            if key in TRANSLATABLE_FIELDS and isinstance(value, str):
                if baseline_value == value and isinstance(previous_value, str):
                    result[key] = previous_value
                    counts["reused"] += 1
                else:
                    result[key] = value
                    queue[child] = {
                        "current_english": value,
                        "baseline_english": baseline_value,
                        "previous_translation": previous_value,
                    }
                    counts["review_required"] += 1
            else:
                result[key] = rebase_value(
                    value,
                    baseline_value,
                    previous_value,
                    child,
                    queue,
                    counts,
                )
        return result
    if isinstance(current, list):
        baseline_list = baseline if isinstance(baseline, list) else []
        previous_list = previous if isinstance(previous, list) else []
        return [
            rebase_value(
                value,
                baseline_list[index] if index < len(baseline_list) else None,
                previous_list[index] if index < len(previous_list) else None,
                f"{label}[{index}]",
                queue,
                counts,
            )
            for index, value in enumerate(current)
        ]
    return current


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--base-instance", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    jar_path = find_jar(instance, CORE_TARGET)
    base_jar_path = find_jar(args.base_instance.resolve(), CORE_TARGET)
    rows = []
    queue: dict[str, dict[str, Any]] = {}
    counts: Counter[str] = Counter()
    with ZipFile(jar_path) as jar, ZipFile(base_jar_path) as base_jar:
        names = sorted(
            name
            for name in jar.namelist()
            if name.startswith(SOURCE_PREFIX) and name.endswith(".json")
        )
        for name in names:
            relative = Path(name.removeprefix(SOURCE_PREFIX))
            output = WORK_ROOT / relative
            if output.exists() and not args.force:
                raise FileExistsError(
                    f"기존 가이드 작업본을 덮어쓰지 않습니다: {output}"
                )
            current = json.loads(jar.read(name).decode("utf-8-sig"))
            base_name = f"{SOURCE_PREFIX}{relative.as_posix()}"
            baseline = (
                json.loads(base_jar.read(base_name).decode("utf-8-sig"))
                if base_name in base_jar.namelist()
                else None
            )
            previous = (
                json.loads(output.read_text(encoding="utf-8-sig"))
                if output.is_file()
                else None
            )
            value = rebase_value(
                current,
                baseline,
                previous,
                relative.as_posix(),
                queue,
                counts,
            )
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            rows.append(relative.as_posix())
    REVIEW_QUEUE.write_text(
        json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "jar": jar_path.name,
                "base_jar": base_jar_path.name,
                "guide_files": len(rows),
                "reused_fields": counts["reused"],
                "review_required_fields": counts["review_required"],
                "review_queue": str(REVIEW_QUEUE.relative_to(PROJECT_ROOT)),
                "work_root": str(WORK_ROOT),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
