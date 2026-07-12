#!/usr/bin/env python3
"""검증된 AE2 가이드 파일을 백업 후 실제 ATM10 인스턴스에 적용한다."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import build_ae2_guide as guide
from snapshot_instance import collect

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_ROOT = Path("resourcepacks/ATM10_Korean/assets/ae2/ae2guide/_ko_kr")
VERIFY_SCRIPT = PROJECT_ROOT / "scripts/verify_ae2_guide.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def running_java_processes() -> list[str]:
    if sys.platform != "win32":
        return []
    result = subprocess.run(
        ["tasklist", "/FO", "CSV", "/NH"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    found = []
    for row in csv.reader(result.stdout.splitlines()):
        if not row:
            continue
        name = row[0].lower()
        if name in {"java.exe", "javaw.exe", "minecraft.exe", "minecraftlauncher.exe"}:
            found.append(row[0])
    return sorted(set(found))


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


def validate_source(instance: Path) -> None:
    subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT), "--instance", str(instance)],
        check=True,
    )


def remove_empty_directories(root: Path, stop: Path) -> None:
    current = root
    while current != stop and current.is_relative_to(stop):
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def apply(instance: Path, snapshot_path: Path, dry_run: bool) -> dict[str, object]:
    instance = instance.resolve()
    snapshot_path = snapshot_path.resolve()
    target_root = (instance / TARGET_ROOT).resolve()
    resourcepacks_root = (instance / "resourcepacks").resolve()
    if not target_root.is_relative_to(resourcepacks_root):
        raise ValueError(f"적용 경로가 resourcepacks 밖입니다: {target_root}")
    if not snapshot_path.is_file():
        raise FileNotFoundError(f"적용 전 스냅샷이 없습니다: {snapshot_path}")

    processes = running_java_processes()
    if processes:
        raise RuntimeError(f"Java 또는 Minecraft가 실행 중입니다: {processes}")
    validate_source(instance)

    previous = json.loads(snapshot_path.read_text(encoding="utf-8-sig"))
    before = collect(instance)
    if before != previous:
        raise RuntimeError("실제 인스턴스가 적용 전 스냅샷과 다릅니다.")

    deployments = []
    expected_changes = set()
    for relative in guide.BATCH_FILES:
        source = guide.OUTPUT_ROOT / relative
        target = target_root / relative
        existed = target.is_file()
        source_hash = sha256(source)
        before_hash = sha256(target) if existed else None
        instance_relative = target.relative_to(instance).as_posix()
        changed = source_hash != before_hash
        if changed:
            expected_changes.add(instance_relative)
        deployments.append(
            {
                "relative_path": instance_relative,
                "source": str(source),
                "target": str(target),
                "existed_before": existed,
                "changed": changed,
                "source_sha256": source_hash,
                "before_sha256": before_hash,
            }
        )

    if dry_run:
        return {
            "status": "dry_run_ready",
            "instance": str(instance),
            "files": len(deployments),
            "expected_changes": sorted(expected_changes),
            "java_processes": [],
            "snapshot_matches": True,
        }

    processes = running_java_processes()
    if processes:
        raise RuntimeError(
            f"적용 직전에 Java 또는 Minecraft가 실행됐습니다: {processes}"
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = PROJECT_ROOT / "temp/backups" / timestamp
    backup_root.mkdir(parents=True, exist_ok=False)
    applied: list[dict[str, object]] = []
    try:
        for record in deployments:
            if not record["changed"]:
                record["after_sha256"] = record["before_sha256"]
                continue
            source = Path(record["source"])
            target = Path(record["target"])
            if record["existed_before"]:
                backup = backup_root / record["relative_path"]
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
                record["backup"] = str(backup)
            else:
                record["backup"] = None
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            record["after_sha256"] = sha256(target)
            if record["after_sha256"] != record["source_sha256"]:
                raise RuntimeError(f"적용 파일 해시가 다릅니다: {target}")
            applied.append(record)

        after = collect(instance)
        changes = inventory_changes(previous, after)
        if changes != expected_changes:
            raise RuntimeError(
                f"예상 밖 인스턴스 변경입니다: 실제={sorted(changes)}, "
                f"예상={sorted(expected_changes)}"
            )
    except Exception:
        for record in reversed(applied):
            target = Path(record["target"])
            backup_value = record.get("backup")
            if backup_value:
                shutil.copy2(Path(backup_value), target)
            elif target.is_file():
                target.unlink()
                remove_empty_directories(target.parent, resourcepacks_root)
        raise

    manifest = {
        "applied_at": datetime.now().isoformat(timespec="seconds"),
        "instance": str(instance),
        "backup_root": str(backup_root),
        "status": "applied_and_verified",
        "changed_paths": sorted(changes),
        "unexpected_changes": [],
        "files": deployments,
    }
    manifest_path = backup_root / "backup_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    manifest["backup_manifest"] = str(manifest_path)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, type=Path)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = apply(args.instance, args.snapshot, args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
