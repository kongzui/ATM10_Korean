#!/usr/bin/env python3
"""Apotheosis 그림자의 연대기 영어 원문을 한국어 검수 작업본으로 준비한다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_apotheosis import find_jar
from apotheosis_catalog import TARGETS

WORK_ROOT = PROJECT_ROOT / "working/apotheosis/guide/ko_kr"
SOURCE_PREFIX = "assets/apotheosis/patchouli_books/apoth_chronicle/en_us/"
CORE_TARGET = next(target for target in TARGETS if target.namespace == "apotheosis")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    jar_path = find_jar(instance, CORE_TARGET)
    rows = []
    with ZipFile(jar_path) as jar:
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
            value = json.loads(jar.read(name).decode("utf-8-sig"))
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            rows.append(relative.as_posix())
    print(
        json.dumps(
            {
                "jar": jar_path.name,
                "guide_files": len(rows),
                "work_root": str(WORK_ROOT),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
