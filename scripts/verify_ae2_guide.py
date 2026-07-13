#!/usr/bin/env python3
"""AE2 내장 가이드 작업본과 리소스팩 산출물을 읽기 전용으로 검증한다."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

import build_ae2_guide as guide
import build_ae2_addon_guides as addon_guides
from local_paths import resolve_source_root

HEADING_TEXT_RE = re.compile(r"(?m)^#{1,6}\s+(.+?)\s*$")
ANCHOR_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)#([^)]+)\)")


def heading_anchors(text: str) -> set[str]:
    anchors = set()
    for heading in HEADING_TEXT_RE.findall(text):
        visible = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", heading)
        visible = re.sub(r"<[^>]+>|`([^`]*)`", r"\1", visible)
        visible = re.sub(r"[*_~]", "", visible).lower()
        anchor = re.sub(r"[^a-z0-9 -]", "", visible)
        anchor = re.sub(r"[\s-]+", "-", anchor).strip("-")
        if anchor:
            anchors.add(anchor)
    return anchors


def validate_anchor_references(
    archives: dict[str, zipfile.ZipFile], namespace: str, page: str, text: str
) -> list[str]:
    errors = []
    for target, anchor in ANCHOR_LINK_RE.findall(text):
        resolved = addon_guides.resolve_guide_reference(namespace, page, target)
        if not resolved:
            continue
        target_namespace = resolved.split("/", 2)[1]
        archive = archives.get(target_namespace)
        if archive is None or resolved not in archive.namelist():
            continue
        target_source = archive.read(resolved).decode("utf-8-sig")
        if anchor not in heading_anchors(target_source):
            errors.append(f"{page}: 대상 페이지에 앵커가 없습니다: {target}#{anchor}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    jar = guide.find_ae2_jar(instance)
    ae2wtlib_jar = guide.find_ae2wtlib_jar(instance)
    errors = []

    working_files = {
        path.relative_to(guide.WORKING_ROOT).as_posix()
        for path in guide.WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    output_files = {
        path.relative_to(guide.OUTPUT_ROOT).as_posix()
        for path in guide.OUTPUT_ROOT.rglob("*.md")
        if path.is_file()
    }
    expected = set(guide.BATCH_FILES)
    if working_files != expected:
        errors.append("작업본 파일 목록이 첫 배치와 다릅니다.")
    if output_files != expected:
        errors.append("출력 파일 목록이 첫 배치와 다릅니다.")

    with (
        zipfile.ZipFile(jar) as archive,
        (
            zipfile.ZipFile(ae2wtlib_jar) if ae2wtlib_jar else zipfile.ZipFile(jar)
        ) as compatibility_archive,
    ):
        ae2wtlib_archive = compatibility_archive if ae2wtlib_jar else None
        archive_names = set(archive.namelist())
        addon_archive_names = (
            {
                "ae2": archive_names,
                "ae2wtlib": set(ae2wtlib_archive.namelist()),
            }
            if ae2wtlib_archive
            else None
        )
        resource_names = addon_archive_names or {"ae2": archive_names}
        source_archives = {"ae2": archive}
        if ae2wtlib_archive:
            source_archives["ae2wtlib"] = ae2wtlib_archive
        for relative in guide.BATCH_FILES:
            source = guide.load_effective_source(archive, ae2wtlib_archive, relative)
            working_path = guide.WORKING_ROOT / relative
            output_path = guide.OUTPUT_ROOT / relative
            if not working_path.is_file() or not output_path.is_file():
                continue
            working = working_path.read_text(encoding="utf-8")
            output = output_path.read_text(encoding="utf-8")
            errors.extend(guide.validate_pair(relative, source, working))
            errors.extend(addon_guides.validate_tag_nesting(relative, working))
            errors.extend(
                addon_guides.validate_resources(
                    resource_names, "ae2", relative, working
                )
            )
            errors.extend(
                validate_anchor_references(source_archives, "ae2", relative, working)
            )
            if working != output:
                errors.append(f"{relative}: 작업본과 출력이 다릅니다.")
            for path in (working_path, output_path):
                if path.read_bytes().startswith(b"\xef\xbb\xbf"):
                    errors.append(f"{path}: UTF-8 BOM이 있습니다.")

    progress = json.loads(guide.PROGRESS_FILE.read_text(encoding="utf-8"))
    if progress.get("pages") != len(guide.BATCH_FILES):
        errors.append("진행 기록의 페이지 수가 다릅니다.")
    if progress.get("validation_errors") != 0:
        errors.append("진행 기록에 검증 오류가 남아 있습니다.")
    if errors:
        raise ValueError("\n".join(errors))

    result = {
        "source_jar": jar.name,
        "pages": len(guide.BATCH_FILES),
        "working_output_match": True,
        "missing_files": 0,
        "extra_files": 0,
        "broken_references": 0,
        "broken_anchors": 0,
        "resource_id_errors": 0,
        "tag_nesting_errors": 0,
        "protected_syntax_errors": 0,
        "english_paragraph_candidates": 0,
        "utf8_bom_files": 0,
        "validation_errors": 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
