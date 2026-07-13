#!/usr/bin/env python3
"""검증된 AE2 연동 모드 가이드 배치를 백업 후 ATM10 인스턴스에 적용한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import apply_ae2_guide as core_apply
import build_ae2_addon_guides as guides
from snapshot_instance import collect

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPTS = (
    PROJECT_ROOT / "scripts/verify_ae2_guide.py",
    PROJECT_ROOT / "scripts/verify_ae2_addon_guides.py",
    PROJECT_ROOT / "scripts/verify_ftbquests_titles.py",
)
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
KUBEJS_OUTPUT = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/kubejs/lang/ko_kr.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def deployment_sources() -> dict[str, Path]:
    if guides.ACTIVE_BATCH == 3:
        files = {
            "resourcepacks/ATM10_Korean/"
            + guides.EXTENDEDAE_LANG_RELATIVE: guides.EXTENDEDAE_LANG_OUTPUT_FILE,
            "resourcepacks/ATM10_Korean/assets/kubejs/lang/ko_kr.json": (KUBEJS_OUTPUT),
            "config/ftbquests/quests/lang/ko_kr.snbt": QUEST_OUTPUT,
        }
        files.update(
            {
                "resourcepacks/ATM10_Korean/assets/extendedae/ae2guide/_ko_kr/"
                + relative: guides.EXTENDEDAE_GUIDE_OUTPUT_ROOT / relative
                for relative in guides.EXTENDEDAE_BATCH_03_GUIDE_FILES
            }
        )
        return files
    if guides.ACTIVE_BATCH == 2:
        files = {
            "resourcepacks/ATM10_Korean/"
            + guides.ENDERDRIVES_LANG_RELATIVE: guides.ENDERDRIVES_LANG_OUTPUT_FILE,
        }
        files.update(
            {
                "resourcepacks/ATM10_Korean/assets/enderdrives/ae2guide/_ko_kr/"
                + relative: guides.ENDERDRIVES_GUIDE_OUTPUT_ROOT / relative
                for relative in guides.ENDERDRIVES_GUIDE_FILES
            }
        )
        return files
    if guides.ACTIVE_BATCH != 1:
        raise ValueError(
            f"지원하지 않는 연동 모드 가이드 배치입니다: {guides.ACTIVE_BATCH}"
        )
    files = {
        "resourcepacks/ATM10_Korean/assets/ae2/ae2guide/_ko_kr/"
        + guides.CORE_COMPAT_RELATIVE: guides.CORE_COMPAT_OUTPUT_FILE,
        "resourcepacks/ATM10_Korean/" + guides.LANG_RELATIVE: (guides.LANG_OUTPUT_FILE),
        "config/ftbquests/quests/lang/ko_kr.snbt": QUEST_OUTPUT,
    }
    files.update(
        {
            "resourcepacks/ATM10_Korean/assets/ae2wtlib/ae2guide/_ko_kr/"
            + relative: guides.GUIDE_OUTPUT_ROOT / relative
            for relative in guides.ADDON_GUIDE_FILES
        }
    )
    return files


def validate_source(instance: Path) -> None:
    for script in VERIFY_SCRIPTS:
        subprocess.run(
            [sys.executable, str(script), "--instance", str(instance)],
            check=True,
        )


def apply(instance: Path, snapshot_path: Path, dry_run: bool) -> dict[str, object]:
    instance = instance.resolve()
    snapshot_path = snapshot_path.resolve()
    if not snapshot_path.is_file():
        raise FileNotFoundError(f"적용 전 스냅샷이 없습니다: {snapshot_path}")

    processes = core_apply.running_java_processes()
    if processes:
        raise RuntimeError(f"Java 또는 Minecraft가 실행 중입니다: {processes}")
    validate_source(instance)

    previous = json.loads(snapshot_path.read_text(encoding="utf-8-sig"))
    before = collect(instance)
    if before != previous:
        raise RuntimeError("실제 인스턴스가 적용 전 스냅샷과 다릅니다.")

    deployments = []
    expected_changes = set()
    for relative, source in deployment_sources().items():
        target = (instance / relative).resolve()
        if not target.is_relative_to(instance):
            raise ValueError(f"적용 경로가 인스턴스 밖입니다: {target}")
        if not source.is_file():
            raise FileNotFoundError(f"적용할 산출물이 없습니다: {source}")
        existed = target.is_file()
        source_hash = sha256(source)
        before_hash = sha256(target) if existed else None
        changed = source_hash != before_hash
        if changed:
            expected_changes.add(relative)
        deployments.append(
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
            "status": "dry_run_ready",
            "instance": str(instance),
            "files": len(deployments),
            "expected_changes": sorted(expected_changes),
            "java_processes": [],
            "snapshot_matches": True,
        }

    processes = core_apply.running_java_processes()
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
                backup = backup_root / str(record["relative_path"])
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
        changes = core_apply.inventory_changes(previous, after)
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
                shutil.copy2(Path(str(backup_value)), target)
            elif target.is_file():
                target.unlink()
                core_apply.remove_empty_directories(target.parent, instance)
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
