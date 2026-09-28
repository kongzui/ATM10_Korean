#!/usr/bin/env python3
"""Better Advanced Tooltips의 현재 원문·검수·관련 표시 경로를 검증해요."""

from __future__ import annotations

import json
import re
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from snapshot_instance import collect
from verify_ad_astra_translation import scan_instance_routes
from verify_compat_release import read_json, sha256, strict_object
from verify_stage1_translation import check_review

MOD = "betteradvancedtooltips"
WORK = PROJECT_ROOT / "working" / MOD
LANGUAGE = f"resourcepack/ATM10_Korean/assets/{MOD}/lang/ko_kr.json"
ROUTE_PATTERN = re.compile(r"better[ _-]?advanced[ _-]?tooltips", re.IGNORECASE)


def allowed_paths():
    """이번 모드의 한국어 언어 파일만 허용해요."""
    return {LANGUAGE}


def verify(*, evidence_hash=None):
    instance = resolve_source_root()
    before = collect(instance)
    output = PROJECT_ROOT / "output/8.1"
    evidence = {}

    def record(path, root, prefix):
        evidence[f"{prefix}/{path.relative_to(root).as_posix()}"] = sha256(path)
        if evidence_hash:
            evidence_hash(path, root, prefix)

    try:
        source = read_json(WORK / "source.json")
        jar = instance / "mods" / source["jar"]
        if sha256(jar) != source["jar_sha256"]:
            raise ValueError("Better Advanced Tooltips JAR이 검수 원본과 달라요")
        record(jar, instance, "instance")
        with ZipFile(jar) as archive:
            members = sorted(n for n in archive.namelist() if not n.endswith("/"))
            member = f"assets/{MOD}/lang/en_us.json"
            if members.count(member) != 1 or members != read_json(
                WORK / "jar_audit.json"
            ):
                raise ValueError("언어·가이드·클래스 목록이 검수 원본과 달라요")
            english = json.loads(archive.read(member), object_pairs_hook=strict_object)
            if f"assets/{MOD}/lang/ko_kr.json" in members:
                raise ValueError("새 내장 한국어 후보의 검수가 필요해요")
        korean = read_json(WORK / "ko_kr.json")
        if (
            len(english) != 5
            or read_json(WORK / "en_us.json") != english
            or read_json(WORK / "jar_ko_kr.json") != {}
            or list(korean) != list(english)
            or read_json(output / LANGUAGE) != korean
        ):
            raise ValueError("현재 영어·한국어·배포 파일 불일치")
        keys = check_review(MOD, read_json(WORK / "review.json"), english, korean)
        routes = scan_instance_routes(instance, ROUTE_PATTERN)
        if routes != read_json(WORK / "display_audit.json") or routes["matches"]:
            raise ValueError("FTB Quests·KubeJS 표시 경로를 다시 검수해야 해요")
        for name in (
            "source",
            "en_us",
            "ko_kr",
            "jar_ko_kr",
            "review",
            "jar_audit",
            "display_audit",
        ):
            record(WORK / f"{name}.json", PROJECT_ROOT, "project")
        record(output / LANGUAGE, output, "output")
        for relative in routes["source_sha256"]:
            record(instance / relative, instance, "instance")
        return {
            "status": "passed",
            "counts": {MOD: {"language_keys": keys, "guide_files": 0}},
            "related_instance_references": 0,
            "hardcoded_tooltips": "source_retained_see_betteradvancedtooltips_translation.md",
            "instance_unchanged": True,
            "evidence_sha256": evidence,
        }
    finally:
        if before != collect(instance):
            raise ValueError("검증 중 인스턴스 파일 목록·크기·수정 시각 변경")


if __name__ == "__main__":
    result = verify()
    report = (
        PROJECT_ROOT / "versions/8.1/reports/betteradvancedtooltips_validation.json"
    )
    report.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["counts"], ensure_ascii=False))
