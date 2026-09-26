#!/usr/bin/env python3
"""Logistics Networks의 현재 원문과 검수한 번역·표시 경로를 대조해요."""

from __future__ import annotations

import argparse
import json
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from snapshot_instance import collect
from verify_compat_release import read_json, sha256, strict_object
from verify_stage1_translation import check_review

MOD = "logisticsnetworks"
PACK = "resourcepack/ATM10_Korean"
WORK = PROJECT_ROOT / "working" / MOD
GUIDE = f"assets/{MOD}/guides/{MOD}/guide"
REGISTRY = f"assets/{MOD}/guideme_guides/guide.json"


def allowed_paths():
    """언어 파일과 현재 영어 가이드에 대응하는 경로만 허용해요."""
    paths = {f"{PACK}/assets/{MOD}/lang/ko_kr.json"}
    return paths


def verify(*, language_only=False, evidence_hash=None):
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
            raise ValueError("Logistics Networks JAR이 검수 원본과 달라요")
        record(jar, instance, "instance")
        with ZipFile(jar) as archive:
            member = f"assets/{MOD}/lang/en_us.json"
            if archive.namelist().count(member) != 1:
                raise ValueError("영어 언어 멤버가 없거나 중복돼요")
            english = json.loads(archive.read(member), object_pairs_hook=strict_object)
        korean_path = output / PACK / f"assets/{MOD}/lang/ko_kr.json"
        korean = read_json(korean_path)
        if read_json(WORK / "en_us.json") != english or set(english) != set(korean):
            raise ValueError("현재 원문 또는 번역 키가 달라요")
        if read_json(WORK / "ko_kr.json") != korean:
            raise ValueError("작업 번역과 배포 번역이 달라요")
        review = read_json(WORK / "review.json")
        keys = check_review(MOD, review, english, korean)
        for name in ("source.json", "en_us.json", "ko_kr.json", "review.json"):
            record(WORK / name, PROJECT_ROOT, "project")
        record(korean_path, output, "output")
        return {
            "status": "passed",
            "scope": "language",
            "counts": {MOD: {"language_keys": keys}},
            "source_sha256": evidence,
        }
    finally:
        if before != collect(instance):
            raise ValueError("검증 중 실제 인스턴스의 파일이 변경됐어요")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language-only", action="store_true")
    args = parser.parse_args()
    report = verify(language_only=args.language_only)
    suffix = "language_validation" if args.language_only else "validation"
    path = PROJECT_ROOT / f"versions/8.1/reports/{MOD}_{suffix}.json"
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
