#!/usr/bin/env python3
"""검증된 FTB Quests 제목 번역을 백업 후 실제 ATM10 인스턴스에 적용한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from snapshot_instance import collect

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
SNAPSHOT = PROJECT_ROOT / "temp/ftbquests_titles_preapply_snapshot.json"
RELATIVE_TARGET = "config/ftbquests/quests/lang/ko_kr.snbt"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_paths(previous: dict[str, object], current: dict[str, object]) -> set[str]:
    changed: set[str] = set()
    previous_files = previous["files"]
    current_files = current["files"]
    assert isinstance(previous_files, dict) and isinstance(current_files, dict)
    for root in previous["tracked_roots"]:
        old_rows = previous_files.get(root, [])
        new_rows = current_files.get(root, [])
        old = {row["path"]: (row["size"], row["mtime_ns"]) for row in old_rows}
        new = {row["path"]: (row["size"], row["mtime_ns"]) for row in new_rows}
        changed.update(old.keys() ^ new.keys())
        changed.update(
            path for path in old.keys() & new.keys() if old[path] != new[path]
        )
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, type=Path)
    args = parser.parse_args()
    instance = args.instance.resolve()
    target = instance / RELATIVE_TARGET
    if not instance.is_dir() or not target.is_file() or not SOURCE.is_file():
        parser.error("인스턴스, 기존 번역 또는 검증 산출물이 없습니다.")
    if not SNAPSHOT.is_file():
        parser.error(f"적용 전 스냅샷이 없습니다: {SNAPSHOT}")

    expected_before = json.loads(SNAPSHOT.read_text(encoding="utf-8-sig"))
    before = collect(instance)
    if before != expected_before:
        raise RuntimeError("적용 전 인스턴스 상태가 스냅샷과 다릅니다.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = PROJECT_ROOT / "temp/backups" / timestamp
    backup = backup_root / RELATIVE_TARGET
    backup.parent.mkdir(parents=True, exist_ok=False)
    shutil.copy2(target, backup)
    before_hash = sha256(target)
    source_hash = sha256(SOURCE)
    try:
        shutil.copy2(SOURCE, target)
        after_hash = sha256(target)
        if after_hash != source_hash:
            raise RuntimeError("적용 파일 해시가 산출물과 다릅니다.")
        after = collect(instance)
        changes = changed_paths(before, after)
        if changes != {RELATIVE_TARGET}:
            raise RuntimeError(f"계획 밖의 인스턴스 변경이 있습니다: {sorted(changes)}")
    except Exception:
        shutil.copy2(backup, target)
        raise

    manifest = {
        "applied_at": datetime.now().isoformat(timespec="seconds"),
        "instance": str(instance),
        "backup_root": str(backup_root),
        "changed_paths": [RELATIVE_TARGET],
        "before_sha256": before_hash,
        "source_sha256": source_hash,
        "after_sha256": after_hash,
        "backup": str(backup),
        "unexpected_changes": [],
        "status": "applied_and_verified",
    }
    manifest_path = backup_root / "backup_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
