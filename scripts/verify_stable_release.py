#!/usr/bin/env python3
"""보조 번역 코드가 없는 안정판과 기존 설치의 덮어쓰기 전환을 검사해요."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path

from local_paths import PROJECT_ROOT
from verify_compat_release import SnbtReader, read_json, sha256
import verify_stage1_translation as stage1
from version_context import load_output_release

BASELINE = "cfe93e1"
DISABLED_PATHS = (
    "overrides/kubejs/startup_scripts/appleskin_debug_labels.js",
    "overrides/kubejs/startup_scripts/mousetweaks_config_labels.js",
    "overrides/kubejs/startup_scripts/enderdrives_messages.js",
    "overrides/kubejs/client_scripts/enderdrives_tooltips.js",
)
DISABLED_CONTENT = (
    "// 안정 배포판: 보조 번역 기능을 사용하지 않아요.\n"
    "// 기존 설치의 같은 이름 스크립트를 비활성화하기 위한 덮어쓰기 파일이에요.\n"
)


def verify(version: str, *, write_report: bool = True) -> dict:
    output = PROJECT_ROOT / "output" / version
    release = load_output_release(version)
    cumulative = version == "8.1" and release["release_id"] in stage1.RELEASE_MODS
    if not cumulative and release["release_id"] != f"{version}-stable.1":
        raise ValueError("지원하지 않는 안정판 배포예요")
    previous = subprocess.run(
        [
            "git",
            "show",
            f"{BASELINE}:versions/{version}/reports/startup_hotfix_validation.json",
        ],
        capture_output=True,
        check=True,
        cwd=PROJECT_ROOT,
    )
    baseline = json.loads(previous.stdout)["output_sha256"]
    inventory = {}
    errors = []
    counts = Counter()
    node = shutil.which("node")
    if node is None:
        raise ValueError("JavaScript 문법 검사용 Node.js가 필요해요")
    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        relative = path.relative_to(output).as_posix()
        inventory[relative] = sha256(path)
        try:
            if path.suffix in {".json", ".mcmeta"}:
                value = read_json(path)
                counts["json"] += 1
                if "/lang/" in relative and path.suffix == ".json":
                    label = (
                        "language_values" if cumulative else "unchanged_language_values"
                    )
                    counts[label] += len(value)
            elif path.suffix in {".snbt", ".snbt_merged"}:
                SnbtReader(path.read_text(encoding="utf-8")).parse()
                counts["snbt"] += 1
            elif path.suffix == ".js":
                result = subprocess.run(
                    [node, "--check", str(path)], capture_output=True
                )
                if result.returncode:
                    raise ValueError(result.stderr.decode("utf-8", errors="replace"))
                counts["javascript"] += 1
                if relative not in DISABLED_PATHS:
                    counts["unchanged_existing_scripts"] += 1
        except (ValueError, UnicodeError) as exc:
            errors.append(f"{relative}: {exc}")
    if not cumulative and set(inventory) != set(baseline):
        errors.append("이전 배포와 파일 목록이 달라요")
    allowed = set(DISABLED_PATHS) | {
        "release.json",
        "resourcepack/ATM10_Korean/pack.mcmeta",
    }
    for relative, digest in inventory.items():
        if (
            not cumulative
            and relative not in allowed
            and digest != baseline.get(relative)
        ):
            errors.append(f"보조 기능 제외 범위 밖 변경: {relative}")
    compatibility = None
    stage1_validation = None
    if cumulative:
        try:
            stage1_validation = stage1.verify(release["release_id"], inventory)
            compatibility = {
                "mode": "current_stage1_and_inherited_unchanged_files",
                "commit": stage1.BASELINE,
                "release": "8.1-stable.1",
                "unchanged_data_hashes_verified": True,
            }
        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            subprocess.SubprocessError,
        ) as exc:
            errors.append(f"단계1 원문·검수 검증 실패: {exc}")
    elif version == "8.1":
        # 실행 후 재작성된 인스턴스 대신, 변경 없는 배포 데이터의 이전 원문 검증을 계승해요.
        previous_compat = subprocess.run(
            ["git", "show", f"{BASELINE}:versions/8.1/reports/compat_validation.json"],
            capture_output=True,
            check=True,
            cwd=PROJECT_ROOT,
        )
        compat = json.loads(previous_compat.stdout)
        if compat["status"] != "passed" or compat["output_sha256"] != baseline:
            errors.append("8.1의 이전 원문 검증과 수정 전 산출물이 일치하지 않아요")
        compatibility = {
            "mode": "inherited_for_unchanged_files",
            "commit": BASELINE,
            "release": compat["release"],
            "unchanged_data_hashes_verified": True,
            "current_instance_audit": "current_instance_compat_audit.json",
        }
    for relative in DISABLED_PATHS:
        path = output / relative
        if not path.is_file() or path.read_bytes() != DISABLED_CONTENT.encode("utf-8"):
            errors.append(f"보조 코드가 남아 있거나 교체 파일이 없어요: {relative}")
    metadata = read_json(output / "resourcepack/ATM10_Korean/pack.mcmeta")
    if (
        metadata["pack"]["pack_format"] != 34
        or release["release_id"] not in metadata["pack"]["description"]
    ):
        errors.append("팩 메타데이터 오류")
    if (
        output
        / "resourcepack/ATM10_Korean/assets/modernui/font/gyeonggi_title_medium.ttf"
    ).exists():
        errors.append("개인 Modern UI 글꼴이 남아 있어요")

    # 실제 인스턴스 대신 temp에 구버전 파일을 넣고 ZIP과 같은 파일 병합을 재현해요.
    temp = PROJECT_ROOT / "temp/stable_transition" / version
    for relative in DISABLED_PATHS:
        old = subprocess.run(
            ["git", "show", f"{BASELINE}:output/{version}/{relative}"],
            capture_output=True,
            check=True,
            cwd=PROJECT_ROOT,
        ).stdout
        if write_report:
            target = temp / Path(relative).relative_to("overrides")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(old)
            shutil.copyfile(output / relative, target)
            replaced = target.read_bytes()
        else:
            # 읽기 전용 실행은 기존 원본을 읽고 덮어쓸 내용만 메모리에서 확인해요.
            replaced = (output / relative).read_bytes()
        if replaced != DISABLED_CONTENT.encode("utf-8"):
            errors.append(f"기존 설치 교체 실패: {relative}")
        else:
            counts["old_scripts_neutralized"] += 1
    # API가 전혀 없는 환경에서 실행해도 변수·이벤트를 만들지 않아야 해요.
    command = (
        "const fs=require('fs'),vm=require('vm'); const c=vm.createContext({});"
        "for(const f of process.argv.slice(1)) vm.runInContext(fs.readFileSync(f,'utf8'),c);"
        "if(Object.keys(c).length) throw Error('실행 코드가 남아 있어요');"
    )
    checked = subprocess.run(
        [node, "-e", command, *[str(output / p) for p in DISABLED_PATHS]],
        capture_output=True,
    )
    if checked.returncode:
        errors.append(checked.stderr.decode("utf-8", errors="replace"))
    report = {
        "release": release["release_id"],
        "status": "passed" if not errors else "failed",
        "baseline_commit": stage1.BASELINE if cumulative else BASELINE,
        "compatibility_validation": compatibility,
        "counts": dict(counts),
        "disabled_scripts": list(DISABLED_PATHS),
        "auxiliary_translation_scripts_active": False,
        "game_screen_validation": "not_run",
        "deployment": (
            "not_verified_by_release_validator_see_apply_report"
            if release["release_id"]
            in {
                "8.1-stable.4",
                "8.1-stable.5",
                "8.1-stable.6",
                "8.1-stable.7",
                "8.1-stable.8",
                "8.1-stable.9",
                "8.1-stable.10",
                "8.1-stable.11",
                "8.1-stable.12",
                "8.1-stable.13",
                "8.1-stable.14",
                "8.1-stable.15",
                "8.1-stable.16",
            }
            else "not_applied_user_will_install"
        ),
        "transition_validation": (
            "temp_overwrite_and_comment_only_vm"
            if write_report
            else "read_only_content_and_comment_only_vm_no_temp_overwrite"
        ),
        "errors": errors,
        "output_sha256": inventory,
    }
    if cumulative:
        report["stage1_validation"] = stage1_validation
    final_inventory = {
        p.relative_to(output).as_posix(): sha256(p)
        for p in output.rglob("*")
        if p.is_file() and p.name != ".gitkeep"
    }
    if final_inventory != inventory:
        errors.append("검증 중 output 파일 목록이나 내용이 바뀌었어요")
        report["status"] = "failed"
    destination = PROJECT_ROOT / "versions" / version / "reports/stable_validation.json"
    if write_report:
        content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        if report["status"] == "passed":
            (
                destination.parent / f"{release['release_id']}_stable_validation.json"
            ).write_text(content, encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", choices=("7.1", "8.1"), required=True)
    parser.add_argument(
        "--no-write", action="store_true", help="보고서·임시 파일을 쓰지 않아요"
    )
    args = parser.parse_args()
    result = verify(args.version, write_report=not args.no_write)
    print(
        json.dumps(
            {k: v for k, v in result.items() if k != "output_sha256"},
            ensure_ascii=False,
            indent=2,
        )
    )
    raise SystemExit(0 if result["status"] == "passed" else 1)
