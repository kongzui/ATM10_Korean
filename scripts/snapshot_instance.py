#!/usr/bin/env python3
"""번역 관련 원본 경로의 메타데이터 스냅샷을 만들고 비교한다."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from local_paths import resolve_source_root

TRACKED_ROOTS = ("mods", "config/ftbquests", "kubejs", "resourcepacks")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SNAPSHOT = PROJECT_ROOT / "temp" / "instance_snapshot.json"


def inside_project(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError(f"스냅샷은 프로젝트 안에만 쓸 수 있습니다: {resolved}") from exc
    return resolved


def collect(instance: Path) -> dict[str, object]:
    roots: dict[str, list[dict[str, object]]] = {}
    for relative in TRACKED_ROOTS:
        root = instance / relative
        if not root.is_dir():
            raise FileNotFoundError(f"필수 원본 폴더가 없습니다: {root}")
        rows = []
        for path in sorted((item for item in root.rglob("*") if item.is_file()), key=lambda p: p.as_posix().lower()):
            stat = path.stat()
            rows.append(
                {
                    "path": path.relative_to(instance).as_posix(),
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                }
            )
        roots[relative] = rows
    return {"instance": str(instance.resolve()), "tracked_roots": list(TRACKED_ROOTS), "files": roots}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("create", "compare"))
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    args = parser.parse_args()

    instance = resolve_source_root(args.instance)
    if not instance.is_dir():
        parser.error(f"인스턴스 경로에 접근할 수 없습니다: {instance}")
    snapshot = inside_project(args.snapshot)
    current = collect(instance)

    if args.mode == "create":
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
        count = sum(len(rows) for rows in current["files"].values())
        print(f"스냅샷 생성: {snapshot} ({count}개 파일)")
        return 0

    if not snapshot.is_file():
        parser.error(f"비교할 스냅샷이 없습니다: {snapshot}")
    previous = json.loads(snapshot.read_text(encoding="utf-8-sig"))
    if previous == current:
        count = sum(len(rows) for rows in current["files"].values())
        print(f"원본 변경 없음: {count}개 파일의 경로/크기/수정 시각이 일치합니다.")
        return 0

    print("원본 상태가 스냅샷과 다릅니다.", file=sys.stderr)
    for relative in TRACKED_ROOTS:
        old = {row["path"]: (row["size"], row["mtime_ns"]) for row in previous["files"].get(relative, [])}
        new = {row["path"]: (row["size"], row["mtime_ns"]) for row in current["files"].get(relative, [])}
        added = sorted(new.keys() - old.keys())
        removed = sorted(old.keys() - new.keys())
        changed = sorted(path for path in old.keys() & new.keys() if old[path] != new[path])
        if added or removed or changed:
            print(f"- {relative}: 추가 {len(added)}, 삭제 {len(removed)}, 변경 {len(changed)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
