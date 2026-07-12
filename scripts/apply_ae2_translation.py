#!/usr/bin/env python3
"""검증된 AE2 번역 네 파일을 백업 후 실제 ATM10 인스턴스에 적용한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from snapshot_instance import collect

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PREAPPLY_SNAPSHOT = PROJECT_ROOT / "temp/ae2_preapply_snapshot.json"
RESOURCEPACK_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean"
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"

DEPLOYMENTS = {
    "resourcepacks/ATM10_Korean/pack.mcmeta": RESOURCEPACK_ROOT / "pack.mcmeta",
    "resourcepacks/ATM10_Korean/assets/ae2/lang/ko_kr.json": (
        RESOURCEPACK_ROOT / "assets/ae2/lang/ko_kr.json"
    ),
    "resourcepacks/ATM10_Korean/assets/kubejs/lang/ko_kr.json": (
        RESOURCEPACK_ROOT / "assets/kubejs/lang/ko_kr.json"
    ),
    "config/ftbquests/quests/lang/ko_kr.snbt": QUEST_OUTPUT,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory_changes(
    previous: dict[str, object], current: dict[str, object]
) -> set[str]:
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


def remove_empty_pack_directories(instance: Path) -> None:
    pack_root = instance / "resourcepacks/ATM10_Korean"
    if not pack_root.is_dir():
        return
    directories = sorted(
        (path for path in pack_root.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for directory in directories:
        try:
            directory.rmdir()
        except OSError:
            pass
    try:
        pack_root.rmdir()
    except OSError:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, type=Path)
    args = parser.parse_args()
    instance = args.instance.resolve()
    if not instance.is_dir():
        parser.error(f"인스턴스 경로가 없습니다: {instance}")
    if not PREAPPLY_SNAPSHOT.is_file():
        parser.error(f"적용 전 스냅샷이 없습니다: {PREAPPLY_SNAPSHOT}")
    for source in DEPLOYMENTS.values():
        if not source.is_file():
            parser.error(f"배포 산출물이 없습니다: {source}")

    previous = json.loads(PREAPPLY_SNAPSHOT.read_text(encoding="utf-8-sig"))
    before = collect(instance)
    if before != previous:
        raise RuntimeError("적용 전 인스턴스 상태가 작업 시작 스냅샷과 다릅니다.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = PROJECT_ROOT / "temp/backups" / timestamp
    backup_root.mkdir(parents=True, exist_ok=False)
    records = []
    for relative, source in DEPLOYMENTS.items():
        target = instance / relative
        existed = target.is_file()
        backup = backup_root / relative
        record = {
            "relative_path": relative,
            "target": str(target),
            "source": str(source),
            "existed_before": existed,
            "source_sha256": sha256(source),
            "before_sha256": sha256(target) if existed else None,
            "backup": str(backup) if existed else None,
        }
        if existed:
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup)
        records.append(record)

    applied: list[dict[str, object]] = []
    try:
        for record in records:
            target = Path(record["target"])
            source = Path(record["source"])
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            record["after_sha256"] = sha256(target)
            if record["after_sha256"] != record["source_sha256"]:
                raise RuntimeError(f"적용 파일 해시가 다릅니다: {target}")
            applied.append(record)

        after = collect(instance)
        changes = inventory_changes(previous, after)
        allowed = set(DEPLOYMENTS)
        unexpected = sorted(changes - allowed)
        missing_expected = sorted(allowed - changes)
        if unexpected or missing_expected:
            raise RuntimeError(
                f"예상 밖 변경={unexpected}, 적용되지 않은 대상={missing_expected}"
            )
    except Exception:
        for record in reversed(applied):
            target = Path(record["target"])
            if record["existed_before"]:
                shutil.copy2(Path(record["backup"]), target)
            elif target.is_file():
                target.unlink()
        remove_empty_pack_directories(instance)
        raise

    manifest = {
        "applied_at": datetime.now().isoformat(timespec="seconds"),
        "instance": str(instance),
        "backup_root": str(backup_root),
        "changed_paths": sorted(changes),
        "files": records,
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
