#!/usr/bin/env python3
"""Ad Astra 계열의 현재 JAR과 언어·가이드 검수 산출물을 읽기 전용으로 대조해요."""

from __future__ import annotations

import argparse
import json
import re
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from snapshot_instance import collect
from verify_compat_release import read_json, sha256, strict_object
from verify_stage1_translation import check_review, check_value

MODS = ("ad_astra", "ad_astra_giselle_addon")
GUIDE = "assets/ad_astra/patchouli_books/astrodux"
PACK = "resourcepack/ATM10_Korean"
DISPLAY_FIELDS = {"name", "description", "text", "title"}


def allowed_paths():
    """현재 영어 가이드와 두 언어 파일만 누적 배포의 변경 범위로 허용해요."""
    paths = {f"{PACK}/assets/{mod}/lang/ko_kr.json" for mod in MODS}
    source = PROJECT_ROOT / "working/ad_astra/guide/en_us"
    paths.update(
        f"{PACK}/{GUIDE}/ko_kr/{p.relative_to(source).as_posix()}"
        for p in source.rglob("*.json")
    )
    return paths


def scan_instance_routes(instance, pattern=None):
    """퀘스트와 KubeJS의 관련 참조·조사 파일 목록을 재현해요."""
    if pattern is None:
        pattern = re.compile(
            r"ad[ _-]?astra|astrodux|giselle|아드 ?아스트라", re.IGNORECASE
        )
    hashes = {}
    matches = []
    counts = {"quest_files": 0, "kubejs_files": 0, "quest_chapters": 0}
    for folder, label in (
        ("config/ftbquests", "quest_files"),
        ("kubejs", "kubejs_files"),
    ):
        for path in sorted((instance / folder).rglob("*")):
            if not path.is_file() or path.suffix not in {
                ".snbt",
                ".snbt_merged",
                ".js",
                ".json",
            }:
                continue
            relative = path.relative_to(instance).as_posix()
            text = path.read_text(encoding="utf-8-sig")
            hashes[relative] = sha256(path)
            counts[label] += 1
            if relative.startswith("config/ftbquests/quests/chapters/"):
                counts["quest_chapters"] += 1
            for number, line in enumerate(text.splitlines(), 1):
                if pattern.search(line):
                    matches.append(
                        {"file": relative, "line": number, "text": line.strip()}
                    )
    return {"source_sha256": hashes, "matches": matches, "counts": counts}


def display_strings(value, pointer=""):
    """가이드에서 사용자에게 표시하는 문자열만 수집해요."""
    if isinstance(value, dict):
        for key, child in value.items():
            location = f"{pointer}/{key}"
            if key in DISPLAY_FIELDS and isinstance(child, str):
                yield location, child
            else:
                yield from display_strings(child, location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from display_strings(child, f"{pointer}/{index}")


def masked(value):
    """번역 가능한 표시 문자열을 제외한 구조와 값을 보존 검사해요."""
    if isinstance(value, dict):
        return {
            k: "<표시 문자열>"
            if k in DISPLAY_FIELDS and isinstance(v, str)
            else masked(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [masked(v) for v in value]
    return value


def verify(*, language_only=False, evidence_hash=None):
    instance = resolve_source_root()
    before = collect(instance)
    output = PROJECT_ROOT / "output/8.1"
    counts = {}
    evidence = {}

    def record(path, root, prefix):
        evidence[f"{prefix}/{path.relative_to(root).as_posix()}"] = sha256(path)
        if evidence_hash:
            evidence_hash(path, root, prefix)

    try:
        for mod in MODS:
            work = PROJECT_ROOT / "working" / mod
            source = read_json(work / "source.json")
            jar = instance / "mods" / source["jar"]
            if sha256(jar) != source["jar_sha256"]:
                raise ValueError(f"{mod}: 현재 JAR이 검수 원본과 달라요")
            record(jar, instance, "instance")
            with ZipFile(jar) as archive:
                member = f"assets/{mod}/lang/en_us.json"
                if archive.namelist().count(member) != 1:
                    raise ValueError(f"{mod}: 영어 멤버가 없거나 중복돼요")
                english = json.loads(
                    archive.read(member), object_pairs_hook=strict_object
                )
                korean_path = output / PACK / f"assets/{mod}/lang/ko_kr.json"
                korean = read_json(korean_path)
                if read_json(work / "en_us.json") != english or set(english) != set(
                    korean
                ):
                    raise ValueError(f"{mod}: 원문 또는 산출물 키 불일치")
                if read_json(work / "ko_kr.json") != korean:
                    raise ValueError(f"{mod}: working과 배포 번역이 달라요")
                review = read_json(work / "review.json")
                counts[mod] = {
                    "language_keys": check_review(mod, review, english, korean)
                }
                references = []

                def check_references(value):
                    if isinstance(value, dict):
                        for key, child in value.items():
                            if key in {"translate", "subtitle"} and isinstance(
                                child, str
                            ):
                                if child not in korean:
                                    raise ValueError(
                                        f"표시 언어 참조 누락: {mod}: {child}"
                                    )
                                references.append(child)
                            else:
                                check_references(child)
                    elif isinstance(value, list):
                        for child in value:
                            check_references(child)

                for name in archive.namelist():
                    if name.endswith(".json") and (
                        "/advancement/" in name
                        or "/enchantment/" in name
                        or name == f"assets/{mod}/sounds.json"
                    ):
                        check_references(
                            json.loads(
                                archive.read(name), object_pairs_hook=strict_object
                            )
                        )
                counts[mod]["display_references"] = len(references)
                for name in ("source.json", "en_us.json", "ko_kr.json", "review.json"):
                    record(work / name, PROJECT_ROOT, "project")
                record(korean_path, output, "output")
                if mod == "ad_astra" and not language_only:
                    names = sorted(
                        n
                        for n in archive.namelist()
                        if n.startswith(f"{GUIDE}/en_us/") and n.endswith(".json")
                    )
                    guide_review = read_json(work / "guide/review.json")
                    rows = guide_review["entries"]
                    expected = {}
                    for name in names:
                        relative = name.removeprefix(f"{GUIDE}/en_us/")
                        original = json.loads(
                            archive.read(name), object_pairs_hook=strict_object
                        )
                        target_path = output / PACK / GUIDE / "ko_kr" / relative
                        translated = read_json(target_path)
                        if masked(original) != masked(translated):
                            raise ValueError(
                                f"가이드 구조·제작법·식별자 변경: {relative}"
                            )
                        if read_json(work / "guide/en_us" / relative) != original:
                            raise ValueError(f"가이드 원문 변경: {relative}")
                        if read_json(work / "guide/ko_kr" / relative) != translated:
                            raise ValueError(
                                f"가이드 working·산출물 불일치: {relative}"
                            )
                        targets = dict(display_strings(translated))
                        for pointer, english_value in display_strings(original):
                            check_value(
                                f"{relative}{pointer}", english_value, targets[pointer]
                            )
                            expected[(relative, pointer)] = (
                                english_value,
                                targets[pointer],
                            )
                        record(target_path, output, "output")
                        record(work / "guide/en_us" / relative, PROJECT_ROOT, "project")
                        record(work / "guide/ko_kr" / relative, PROJECT_ROOT, "project")
                    actual = {}
                    for row in rows:
                        key = (row["file"], row["pointer"])
                        if key in actual or row.get("reviewed") is not True:
                            raise ValueError("가이드 검수 중복 또는 미완료")
                        actual[key] = (row["english"], row["translation"])
                    if actual != expected:
                        raise ValueError("가이드 전체 검수 기록 불일치")
                    target_names = {
                        p.relative_to(output / PACK / GUIDE / "ko_kr").as_posix()
                        for p in (output / PACK / GUIDE / "ko_kr").rglob("*.json")
                    }
                    if target_names != {
                        n.removeprefix(f"{GUIDE}/en_us/") for n in names
                    }:
                        raise ValueError("가이드 파일 누락 또는 추가")
                    book = json.loads(
                        archive.read("data/ad_astra/patchouli_books/astrodux/book.json")
                    )
                    if book.get("use_resource_pack") is not True:
                        raise ValueError("가이드의 리소스팩 로딩 경로가 달라요")
                    for field in ("name", "landing_text"):
                        if book[field] not in korean:
                            raise ValueError("책 이름·시작 안내 언어 누락")
                    record(work / "guide/review.json", PROJECT_ROOT, "project")
                    counts[mod].update(
                        guide_files=len(names), guide_strings=len(expected)
                    )
        if not language_only:
            audit_path = PROJECT_ROOT / "working/ad_astra/display_audit.json"
            audit = read_json(audit_path)
            current = scan_instance_routes(instance)
            if any(current[key] != audit[key] for key in current):
                raise ValueError("퀘스트·KubeJS 파일 목록 또는 참조 조사 결과 변경")
            for relative, digest in audit["source_sha256"].items():
                path = instance / relative
                if sha256(path) != digest:
                    raise ValueError(f"관련 표시 경로 조사 후 원문 변경: {relative}")
                record(path, instance, "instance")
            record(audit_path, PROJECT_ROOT, "project")
    finally:
        if collect(instance) != before:
            raise ValueError("검증 중 실제 인스턴스 경로·크기·수정 시각 변경")
    return {
        "status": "passed",
        "counts": counts,
        "evidence_sha256": evidence,
        "instance_unchanged": True,
        "language_only": language_only,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language-only", action="store_true")
    args = parser.parse_args()
    result = verify(language_only=args.language_only)
    name = (
        "ad_astra_language_validation.json"
        if args.language_only
        else "ad_astra_validation.json"
    )
    path = PROJECT_ROOT / "versions/8.1/reports" / name
    path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
