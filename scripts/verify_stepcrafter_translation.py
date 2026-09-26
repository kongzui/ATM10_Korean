#!/usr/bin/env python3
"""Step Crafter의 현재 JAR·전체 언어·가이드·퀘스트 표시 경로를 대조해요."""

from __future__ import annotations

import json
import re
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from snapshot_instance import collect
from verify_ad_astra_translation import scan_instance_routes
from verify_compat_release import read_json, sha256, strict_object
from verify_stage1_translation import check_review

MOD = "stepcrafter"
WORK = PROJECT_ROOT / "working" / MOD
LANGUAGE = f"resourcepack/ATM10_Korean/assets/{MOD}/lang/ko_kr.json"
ROUTE_PATTERN = re.compile(r"step[ _-]?crafter|단계 제작기", re.IGNORECASE)


def allowed_paths():
    """검수한 한국어 언어 파일 하나만 누적 변경 범위로 허용해요."""
    return {LANGUAGE}


def scan_jar(archive):
    """별도 책·가이드와 발전 과제의 표시 문구 유무를 현재 원본에서 재현해요."""
    names = [n for n in archive.namelist() if not n.endswith("/")]
    result = {
        "language_members": sorted(n for n in names if f"assets/{MOD}/lang/" in n),
        "guide_members": sorted(
            n
            for n in names
            if n.endswith((".json", ".md", ".snbt"))
            and re.search(r"guide|patchouli|modonomicon|book", n, re.IGNORECASE)
        ),
        "advancement_files": sorted(
            n for n in names if "/advancement/" in n and n.endswith(".json")
        ),
        "references": [],
        "literal_components": [],
    }

    def visit(value, name, pointer=""):
        if isinstance(value, dict):
            for key, child in value.items():
                location = f"{pointer}/{key}"
                if key in {"translate", "subtitle", "text"} and isinstance(child, str):
                    label = "literal_components" if key == "text" else "references"
                    result[label].append(
                        {"file": name, "pointer": location, "value": child}
                    )
                else:
                    visit(child, name, location)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, name, f"{pointer}/{index}")

    for name in result["advancement_files"]:
        visit(json.loads(archive.read(name), object_pairs_hook=strict_object), name)
    return result


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
            raise ValueError("Step Crafter JAR이 검수 원본과 달라요")
        record(jar, instance, "instance")
        with ZipFile(jar) as archive:
            member = f"assets/{MOD}/lang/en_us.json"
            if archive.namelist().count(member) != 1:
                raise ValueError("영어 언어 멤버가 없거나 중복돼요")
            english = json.loads(archive.read(member), object_pairs_hook=strict_object)
            content = scan_jar(archive)
        if content != read_json(WORK / "jar_audit.json"):
            raise ValueError("가이드·발전 과제 표시 경로 조사 후 원본 변경")
        if (
            content["language_members"] != [member]
            or content["guide_members"]
            or content["references"]
            or content["literal_components"]
            or read_json(WORK / "jar_ko_kr.json") != {}
        ):
            raise ValueError("새 언어 후보 또는 표시 문구를 별도로 검수해야 해요")
        korean = read_json(WORK / "ko_kr.json")
        if (
            len(english) != 79
            or read_json(WORK / "en_us.json") != english
            or list(korean) != list(english)
            or read_json(output / LANGUAGE) != korean
        ):
            raise ValueError("현재 영어·한국어 키 또는 배포 번역 불일치")
        keys = check_review(MOD, read_json(WORK / "review.json"), english, korean)
        audit = read_json(WORK / "display_audit.json")
        current = scan_instance_routes(instance, ROUTE_PATTERN)
        if current != audit or current["matches"]:
            raise ValueError("FTB Quests·KubeJS 관련 표시 경로를 다시 검토해야 해요")
        for name in (
            "source.json",
            "en_us.json",
            "jar_ko_kr.json",
            "ko_kr.json",
            "review.json",
            "jar_audit.json",
            "display_audit.json",
        ):
            record(WORK / name, PROJECT_ROOT, "project")
        record(output / LANGUAGE, output, "output")
        for relative in current["source_sha256"]:
            record(instance / relative, instance, "instance")
        return {
            "status": "passed",
            "counts": {MOD: {"language_keys": keys, "guide_files": 0}},
            "recipe_advancement_files_without_display": len(
                content["advancement_files"]
            ),
            "related_instance_references": len(current["matches"]),
            "instance_unchanged": True,
            "evidence_sha256": evidence,
        }
    finally:
        if before != collect(instance):
            raise ValueError("검증 중 실제 인스턴스 경로·크기·수정 시각 변경")


if __name__ == "__main__":
    result = verify()
    path = PROJECT_ROOT / "versions/8.1/reports/stepcrafter_validation.json"
    path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["counts"], ensure_ascii=False))
