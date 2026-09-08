#!/usr/bin/env python3
"""검증된 호환판을 설치 가능한 두 ZIP으로 만들고 내부 경로와 해시를 확인해요."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from local_paths import PROJECT_ROOT
from verify_compat_release import read_json, sha256
from version_context import load_output_release


def package(version: str = "8.1") -> dict[str, object]:
    output = PROJECT_ROOT / "output" / version
    release = load_output_release(version)
    release_name = release["release_id"]
    destination_root = PROJECT_ROOT / "temp/releases" / release_name
    report_dir = PROJECT_ROOT / "versions" / version / "reports"
    if (
        not release["full_apply_allowed"]
        or release["validated_pack_version"] != version
    ):
        raise ValueError("호환판 파일 검증과 배포 상태 설정을 먼저 완료하세요")
    report = read_json(report_dir / "stable_validation.json")
    if report["status"] != "passed" or report["release"] != release_name:
        raise ValueError("실패한 검증 보고서로는 배포할 수 없어요")
    actual = {
        p.relative_to(output).as_posix(): sha256(p)
        for p in output.rglob("*")
        if p.is_file() and p.name != ".gitkeep"
    }
    if actual != report["output_sha256"]:
        raise ValueError("검증 후 산출물이 바뀌었어요. 검증을 다시 실행하세요")
    if version == "8.1":
        compatibility = report.get("compatibility_validation") or {}
        if (
            compatibility.get("mode") != "inherited_for_unchanged_files"
            or compatibility.get("commit") != report["baseline_commit"]
            or compatibility.get("unchanged_data_hashes_verified") is not True
        ):
            raise ValueError(
                "8.1의 변경 없는 배포 데이터에 대한 원문 검증 근거가 없어요"
            )
    destination_root.mkdir(parents=True, exist_ok=True)
    packages = []
    for kind, relative in (
        ("resourcepack", "resourcepack/ATM10_Korean"),
        ("overrides", "overrides"),
    ):
        root = output / relative
        files = {
            p.relative_to(root).as_posix(): p
            for p in sorted(root.rglob("*"))
            if p.is_file() and p.name != ".gitkeep"
        }
        if not files:
            raise ValueError(f"배포할 파일이 없어요: {kind}")
        if kind == "resourcepack" and (
            "pack.mcmeta" not in files
            or not any(n.startswith("assets/") for n in files)
        ):
            raise ValueError("리소스팩 ZIP 루트에 pack.mcmeta와 assets가 필요해요")
        if kind == "overrides" and any(
            Path(name).parts[0] not in {"config", "kubejs"} for name in files
        ):
            raise ValueError("override ZIP에 config/kubejs 이외의 경로가 있어요")
        destination = destination_root / f"ATM10_Korean_{release_name}_{kind}.zip"
        temporary = destination.with_suffix(".zip.tmp")
        with ZipFile(
            temporary, "w", compression=ZIP_DEFLATED, compresslevel=9
        ) as archive:
            for name, path in files.items():
                info = ZipInfo(name, date_time=(2026, 9, 8, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
        with ZipFile(temporary) as archive:
            if archive.testzip() is not None or set(archive.namelist()) != set(files):
                raise ValueError(f"ZIP 무결성 또는 파일 목록 오류: {kind}")
            for name, path in files.items():
                if archive.read(name) != path.read_bytes():
                    raise ValueError(f"ZIP 내부 내용이 검증본과 달라요: {name}")
        temporary.replace(destination)
        packages.append(
            {
                "name": destination.name,
                "bytes": destination.stat().st_size,
                "files": len(files),
                "sha256": sha256(destination),
                "zip_crc_and_content_verified": True,
            }
        )
    instructions = PROJECT_ROOT / "docs/releases" / f"{release_name}.md"
    (destination_root / "INSTALL.md").write_bytes(instructions.read_bytes())
    manifest = {
        "release": release_name,
        "minecraft": "1.21.1",
        "atm10": version,
        "packages": packages,
        "game_screen_validation": "not_run",
        "auxiliary_translation_scripts_active": False,
        "old_scripts_neutralized_by_overwrite": True,
        "deployment": "not_applied_user_will_install",
    }
    content = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    (destination_root / "SHA256.json").write_text(content, encoding="utf-8")
    manifest_path = (
        PROJECT_ROOT
        / "versions"
        / version
        / "manifests"
        / f"{release_name}_packages.json"
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(content, encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", choices=("7.1", "8.1"), default="8.1")
    args = parser.parse_args()
    print(json.dumps(package(args.version), ensure_ascii=False, indent=2))
