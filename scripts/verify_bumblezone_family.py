#!/usr/bin/env python3
"""The Bumblezone 본체와 직접 연동 표시 경로의 완성 산출물을 검증한다."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/bumblezone"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
EXPECTED_JAR = "the_bumblezone-7.15.0+1.21.1-neoforge.jar"
EXPECTED_JAR_SIZE = 69_665_511
EXPECTED_JAR_SHA256 = "ceb71eab0a738dceb4c3916051a1dc50ad5951ee1ea8ac2f09b04f0406ff5839"
EXPECTED_KUBEJS_PATHS = {
    "kubejs/assets/the_bumblezone/lang/ru_ru.json",
    "kubejs/data/the_bumblezone/bz_bee_queen_trades/revival/dead_bush.json",
    "kubejs/server_scripts/Tweaks/tags.js",
    "kubejs/server_scripts/Unification/tools.js",
    "kubejs/server_scripts/mods/Bumblezone/Recipes.js",
    "kubejs/server_scripts/mods/Bumblezone/tags.js",
    "kubejs/server_scripts/mods/MysticalAgriculture/Tags.js",
    "kubejs/server_scripts/mods/The Bumblezone/Tags.js",
}
BEE_MODIFIED_UTF8 = b"\xed\xa0\xbd\xed\xb0\x9d"


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def sha256(path: Path) -> str:
    """파일의 SHA-256 해시를 계산한다."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_one(root: Path, pattern: str, label: str) -> Path:
    """현재 설치본에서 패턴과 일치하는 파일 하나를 찾는다."""
    matches = sorted(root.glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"{label} 검색 결과가 하나가 아닙니다: {matches}")
    return matches[0]


def verify_language(instance: Path) -> tuple[dict[str, object], list[str]]:
    """현재 JAR 영어 원문과 1,788개 검수 산출물의 일치를 검사한다."""
    jar = find_one(instance / "mods", "the_bumblezone-*.jar", "The Bumblezone JAR")
    english = load_json(WORK_ROOT / "the_bumblezone/en_us.json")
    korean = load_json(WORK_ROOT / "the_bumblezone/ko_kr.json")
    sources = load_json(WORK_ROOT / "the_bumblezone/candidate_sources.json")
    output_path = OUTPUT_ASSETS / "the_bumblezone/lang/ko_kr.json"
    output = load_json(output_path)
    with ZipFile(jar) as archive:
        current = json.loads(
            archive.read("assets/the_bumblezone/lang/en_us.json").decode("utf-8-sig")
        )
        bundled = json.loads(
            archive.read("assets/the_bumblezone/lang/ko_kr.json").decode("utf-8-sig")
        )
    errors = []
    current_hash = sha256(jar)
    if jar.name != EXPECTED_JAR:
        errors.append(f"현재 JAR 이름이 예상과 다릅니다: {jar.name}")
    if jar.stat().st_size != EXPECTED_JAR_SIZE:
        errors.append(f"현재 JAR 크기가 예상과 다릅니다: {jar.stat().st_size}")
    if current_hash != EXPECTED_JAR_SHA256:
        errors.append(f"현재 JAR SHA-256이 예상과 다릅니다: {current_hash}")
    if list(current.items()) != list(english.items()):
        errors.append("작업 영어 원문이 현재 설치 JAR과 다릅니다.")
    if list(korean.items()) != list(output.items()):
        errors.append("검수 작업본과 The Bumblezone 리소스팩 산출물이 다릅니다.")
    if list(english) != list(korean) or list(english) != list(sources):
        errors.append("영어·한국어·출처 키 또는 순서가 서로 다릅니다.")
    for key, source in english.items():
        errors.extend(family_goal.validate_value(key, source, korean[key]))
    exact_reuse = sum(
        1 for key, value in korean.items() if key in bundled and bundled[key] == value
    )
    return {
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_sha256": current_hash,
        "english_keys": len(english),
        "korean_keys": len(korean),
        "source_matches_installed_jar": english == current,
        "output_matches_working_copy": korean == output,
        "bundled_exact_reuse": exact_reuse,
        "new_or_edited": len(korean) - exact_reuse,
        "review_sources": dict(Counter(sources.values())),
        "output_sha256": sha256(output_path),
    }, errors


def verify_advancements(instance: Path) -> tuple[dict[str, object], list[str]]:
    """발전 과제 133개의 모든 표시 요소가 번역 키를 거치는지 검사한다."""
    jar = find_one(instance / "mods", "the_bumblezone-*.jar", "The Bumblezone JAR")
    catalog = load_json(OUTPUT_ASSETS / "the_bumblezone/lang/ko_kr.json")
    visible_literals = []
    missing = []
    display_fields = 0
    with ZipFile(jar) as archive:
        names = [
            name
            for name in archive.namelist()
            if name.endswith(".json")
            and name.startswith(
                (
                    "data/the_bumblezone/advancement/",
                    "data/the_bumblezone/advancements/",
                )
            )
        ]
        for name in names:
            data = json.loads(archive.read(name).decode("utf-8-sig"))
            display = data.get("display") if isinstance(data, dict) else None
            if not isinstance(display, dict):
                continue
            for field in ("title", "description"):
                shown = display.get(field)
                if shown is None:
                    continue
                display_fields += 1
                if isinstance(shown, str) and shown:
                    visible_literals.append(f"{name}:{field}:{shown}")
                elif isinstance(shown, dict):
                    key = shown.get("translate")
                    if not isinstance(key, str) or key not in catalog:
                        missing.append(f"{name}:{field}:{key}")
    errors = []
    if len(names) != 133:
        errors.append(f"발전 과제 파일 수가 예상과 다릅니다: {len(names)}/133")
    if display_fields != 266:
        errors.append(f"발전 과제 표시 필드 수가 예상과 다릅니다: {display_fields}/266")
    if visible_literals:
        errors.append(
            "발전 과제 직접 표시 문구가 있습니다: " + " | ".join(visible_literals[:20])
        )
    if missing:
        errors.append("발전 과제 번역 키가 빠졌습니다: " + " | ".join(missing[:20]))
    return {
        "files_checked": len(names),
        "display_fields_checked": display_fields,
        "visible_literal_fields": len(visible_literals),
        "missing_translation_keys": len(missing),
    }, errors


def verify_guides(instance: Path) -> tuple[dict[str, object], list[str]]:
    """가이드 후보와 영원 성소의 장식용 벌 책을 구분해 검사한다."""
    jar = find_one(instance / "mods", "the_bumblezone-*.jar", "The Bumblezone JAR")
    errors = []
    with ZipFile(jar) as archive:
        names = archive.namelist()
        guide_paths = [
            name
            for name in names
            if "patchouli_books/" in name.lower() or "ae2guide/" in name.lower()
        ]
        processors = sorted(
            name
            for name in names
            if "worldgen/processor_list/sempiternal_sanctum/" in name
            and "book_" in name
            and name.endswith(".json")
        )
        structures = sorted(
            name
            for name in names
            if "structure/sempiternal_sanctum/" in name
            and "/book_" in name
            and name.endswith(".nbt")
        )
        invalid_processors = []
        for name in processors:
            data = json.loads(archive.read(name).decode("utf-8-sig"))
            if not isinstance(data, dict) or set(data) != {"processors"}:
                invalid_processors.append(name)
        invalid_books = []
        for name in structures:
            raw = gzip.decompress(archive.read(name))
            pages = re.findall(rb'\{"text":"(.*?)"\}', raw)
            expected_pages = [BEE_MODIFIED_UTF8 * count for count in range(1, 16)]
            if (
                raw.count(b"Bee Drone") != 1
                or raw.count(b"Bee Record") != 2
                or pages != expected_pages
            ):
                invalid_books.append(name)
    if guide_paths:
        errors.append(
            "별도 Patchouli/GuideME 가이드 경로가 있습니다: "
            + " | ".join(guide_paths[:20])
        )
    if len(processors) != 84 or invalid_processors:
        errors.append(
            f"장식용 책 processor 검수가 맞지 않습니다: {len(processors)}/84, "
            f"오류 {len(invalid_processors)}개"
        )
    if len(structures) != 84 or invalid_books:
        errors.append(
            f"장식용 벌 책 구조 검수가 맞지 않습니다: {len(structures)}/84, "
            f"오류 {len(invalid_books)}개"
        )
    return {
        "patchouli_or_guideme_paths": len(guide_paths),
        "decorative_book_processors": len(processors),
        "decorative_book_structures": len(structures),
        "invalid_decorative_books": len(invalid_books),
        "direct_literals": ["Bee Drone", "Bee Record", "1~15개의 벌 그림"],
        "classification": "영원 성소 퍼즐용 장식 책이며 설명형 가이드가 아님",
    }, errors


def verify_kubejs(instance: Path) -> tuple[dict[str, object], list[str]]:
    """The Bumblezone KubeJS 참조 8개가 비표시 데이터 경로인지 검사한다."""
    family = re.compile(r"the_bumblezone|bumblezone", re.IGNORECASE)
    references = set()
    display_candidates = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".js",
            ".json",
            ".snbt",
            ".txt",
            ".md",
        }:
            continue
        try:
            content = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        if not family.search(content):
            continue
        relative = path.relative_to(instance).as_posix()
        references.add(relative)
        if "/assets/the_bumblezone/lang/" in f"/{relative}":
            continue
        for number, line in enumerate(content.splitlines(), 1):
            if family.search(line) and re.search(
                r"displayName|tooltip|Text\.(?:of|literal)|custom_name|\bname\s*:",
                line,
                re.IGNORECASE,
            ):
                display_candidates.append(f"{relative}:{number}:{line.strip()}")
    errors = []
    if references != EXPECTED_KUBEJS_PATHS:
        missing = sorted(EXPECTED_KUBEJS_PATHS - references)
        extra = sorted(references - EXPECTED_KUBEJS_PATHS)
        errors.append(
            f"KubeJS 참조 경로가 예상과 다릅니다: 누락={missing}, 추가={extra}"
        )
    if display_candidates:
        errors.append(
            "KubeJS 직접 표시 후보가 있습니다: " + " | ".join(display_candidates[:20])
        )
    return {
        "files_referencing_family": len(references),
        "referenced_paths": sorted(references),
        "foreign_language_assets": 1,
        "data_recipe_tag_files": len(references) - 1,
        "direct_display_candidates": len(display_candidates),
    }, errors


def verify_dyenamics(instance: Path) -> tuple[dict[str, object], list[str]]:
    """Dyenamics and Friends의 직접 연동 표시 키 37개를 검사한다."""
    jar = find_one(
        instance / "mods", "dyenamicsandfriends-*.jar", "Dyenamics and Friends JAR"
    )
    with ZipFile(jar) as archive:
        current = json.loads(
            archive.read("assets/dyenamicsandfriends/lang/en_us.json").decode(
                "utf-8-sig"
            )
        )
    scoped = {
        key: value
        for key, value in current.items()
        if key.startswith("block.dyenamicsandfriends.bumblezone_")
        or key == "resourcePack.dyenamicsandfriends.the_bumblezone"
    }
    english = load_json(WORK_ROOT / "integrations/dyenamicsandfriends/en_us.json")
    korean = load_json(WORK_ROOT / "integrations/dyenamicsandfriends/ko_kr.json")
    output_path = OUTPUT_ASSETS / "dyenamicsandfriends/lang/ko_kr.json"
    output = load_json(output_path)
    errors = []
    if len(scoped) != 37 or list(scoped.items()) != list(english.items()):
        errors.append(
            "Dyenamics and Friends 현재 연동 원문 37개와 작업 범위가 다릅니다."
        )
    if list(korean.items()) != list(output.items()):
        errors.append("Dyenamics and Friends 작업본과 리소스팩 산출물이 다릅니다.")
    for key, source in english.items():
        errors.extend(family_goal.validate_value(key, source, korean[key]))
    return {
        "jar": jar.name,
        "keys_checked": len(scoped),
        "output_matches_working_copy": korean == output,
        "output_sha256": sha256(output_path),
    }, errors


def verify_quests(instance: Path) -> tuple[dict[str, object], list[str]]:
    """FTB Quests 195개 원문 표시 키와 16개 fallback 제목을 검사한다."""
    report, errors = family_goal.verify_quests(instance, "bumblezone")
    output = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    fallback = load_json(WORK_ROOT / "quests/fallback/ko_kr.json")
    mismatches = [key for key, value in fallback.items() if output.get(key) != value]
    if len(fallback) != 16 or mismatches:
        errors.append(
            f"명시적 퀘스트 fallback 제목이 맞지 않습니다: {len(fallback)}/16, "
            f"불일치={mismatches}"
        )
    report["source_display_keys_reviewed"] = 195
    report["explicit_fallback_titles"] = len(fallback)
    report["merged_keys_checked"] = 195 + len(fallback)
    return report, errors


def verify_live(instance: Path) -> tuple[dict[str, object], list[str]]:
    """실제 인스턴스의 세 적용 파일과 저장소 산출물 해시를 비교한다."""
    pairs = {
        "the_bumblezone": (
            OUTPUT_ASSETS / "the_bumblezone/lang/ko_kr.json",
            instance
            / "resourcepacks/ATM10_Korean/assets/the_bumblezone/lang/ko_kr.json",
        ),
        "dyenamicsandfriends": (
            OUTPUT_ASSETS / "dyenamicsandfriends/lang/ko_kr.json",
            instance
            / "resourcepacks/ATM10_Korean/assets/dyenamicsandfriends/lang/ko_kr.json",
        ),
        "ftbquests": (
            QUEST_OUTPUT,
            instance / "config/ftbquests/quests/lang/ko_kr.snbt",
        ),
    }
    rows = {}
    errors = []
    for label, (source, target) in pairs.items():
        source_hash = sha256(source)
        target_hash = sha256(target) if target.is_file() else None
        matches = source_hash == target_hash
        rows[label] = {
            "source_sha256": source_hash,
            "live_sha256": target_hash,
            "matches": matches,
        }
        if not matches:
            errors.append(f"실제 적용 파일 해시가 다릅니다: {label}")
    return rows, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-live", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root()
    report = {}
    errors = []
    for label, verifier in (
        ("language", verify_language),
        ("advancements", verify_advancements),
        ("guides", verify_guides),
        ("kubejs", verify_kubejs),
        ("dyenamicsandfriends", verify_dyenamics),
        ("ftbquests", verify_quests),
    ):
        row, found = verifier(instance)
        report[label] = row
        errors.extend(found)
    if args.require_live:
        live, live_errors = verify_live(instance)
        report["live_parity"] = live
        errors.extend(live_errors)
    report["validation_errors"] = len(errors)
    report["errors"] = errors
    report["status"] = "complete" if not errors else "incomplete"
    path = WORK_ROOT / "family_validation.json"
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
