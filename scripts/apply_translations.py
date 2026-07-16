#!/usr/bin/env python3
"""검증된 누적 번역 산출물을 설정된 모든 ATM10 대상에 안전하게 적용한다."""

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

from local_paths import PROJECT_ROOT, resolve_apply_roots
from snapshot_instance import collect

OUTPUT_RESOURCEPACK = PROJECT_ROOT / "output/resourcepack"
OUTPUT_OVERRIDES = PROJECT_ROOT / "output/overrides"
REQUIRED_ROOTS = ("mods", "config/ftbquests", "kubejs", "resourcepacks")


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
        if row and row[0].lower() in {
            "java.exe",
            "javaw.exe",
            "minecraft.exe",
            "minecraftlauncher.exe",
        }:
            found.append(row[0])
    return sorted(set(found))


def deployment_files(selected_paths: set[str] | None = None) -> dict[str, Path]:
    deployments: dict[str, Path] = {}
    for output_root, target_prefix in (
        (OUTPUT_RESOURCEPACK, Path("resourcepacks")),
        (OUTPUT_OVERRIDES, Path()),
    ):
        for source in sorted(output_root.rglob("*"), key=lambda path: path.as_posix()):
            if source.is_file() and source.name != ".gitkeep":
                relative = (target_prefix / source.relative_to(output_root)).as_posix()
                deployments[relative] = source
    if not deployments:
        raise FileNotFoundError("output/ 아래에 적용할 번역 산출물이 없습니다.")
    if selected_paths is not None:
        missing = sorted(selected_paths - set(deployments))
        if missing:
            raise FileNotFoundError(f"선택한 적용 산출물이 없습니다: {missing}")
        deployments = {
            relative: source
            for relative, source in deployments.items()
            if relative in selected_paths
        }
    return deployments


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


def validate_target(root: Path) -> None:
    if not root.is_dir():
        raise FileNotFoundError(f"적용 대상 경로가 없습니다: {root}")
    for relative in REQUIRED_ROOTS:
        if not (root / relative).is_dir():
            raise FileNotFoundError(f"필수 ATM10 경로가 없습니다: {root / relative}")


def apply_to_root(
    label: str,
    root: Path,
    deployments: dict[str, Path],
    backup_base: Path,
    dry_run: bool,
) -> dict[str, object]:
    validate_target(root)
    before = collect(root)
    records: list[dict[str, object]] = []
    expected_changes: set[str] = set()
    for relative, source in deployments.items():
        target = root / relative
        existed = target.is_file()
        source_hash = sha256(source)
        before_hash = sha256(target) if existed else None
        changed = source_hash != before_hash
        if changed:
            expected_changes.add(relative)
        records.append(
            {
                "relative_path": relative,
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
            "target_type": label,
            "target_root": str(root),
            "status": "dry_run_ready",
            "files": len(records),
            "expected_changes": sorted(expected_changes),
        }

    backup_root = backup_base / label
    applied: list[dict[str, object]] = []
    try:
        for record in records:
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

        after = collect(root)
        changes = inventory_changes(before, after)
        tracked_prefixes = tuple(f"{root}/" for root in before["tracked_roots"])
        expected_inventory_changes = {
            path for path in expected_changes if path.startswith(tracked_prefixes)
        }
        if changes != expected_inventory_changes:
            raise RuntimeError(
                f"계획 밖의 대상 변경입니다: 실제={sorted(changes)}, "
                f"예상={sorted(expected_inventory_changes)}"
            )
    except Exception:
        for record in reversed(applied):
            target = Path(record["target"])
            backup_value = record.get("backup")
            if backup_value:
                shutil.copy2(Path(backup_value), target)
            elif target.is_file():
                target.unlink()
        raise

    return {
        "target_type": label,
        "target_root": str(root),
        "status": "applied_and_verified",
        "backup_root": str(backup_root) if expected_changes else None,
        "changed_paths": sorted(expected_changes),
        "files": records,
        "unexpected_changes": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--instance",
        type=Path,
        help="local_paths.json 대신 적용할 단일 ATM10 경로",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--path",
        action="append",
        dest="paths",
        help="적용할 output 상대 경로를 하나씩 선택",
    )
    args = parser.parse_args()

    deployments = deployment_files(set(args.paths) if args.paths else None)
    roots = resolve_apply_roots(args.instance)
    processes = running_java_processes()
    if processes and any(label in {"game_root", "instance"} for label, _ in roots):
        raise RuntimeError(f"Java 또는 Minecraft가 실행 중입니다: {processes}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_base = PROJECT_ROOT / "temp/backups" / timestamp
    results = [
        apply_to_root(label, root, deployments, backup_base, args.dry_run)
        for label, root in roots
    ]
    manifest = {
        "applied_at": datetime.now().isoformat(timespec="seconds"),
        "status": "dry_run_ready" if args.dry_run else "applied_and_verified",
        "configured_targets": [label for label, _ in roots],
        "game_root_configured": any(label == "game_root" for label, _ in roots),
        "java_processes": processes,
        "targets": results,
    }
    if not args.dry_run:
        backup_base.mkdir(parents=True, exist_ok=True)
        manifest_path = backup_base / "backup_manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        manifest["backup_manifest"] = str(manifest_path)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
