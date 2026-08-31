#!/usr/bin/env python3
"""The Aether 본체와 직접 연동 표시 경로의 완성 산출물을 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import aether_family as review
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/aether"
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"
QUEST_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)


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
    """파일 패턴과 일치하는 현재 JAR 하나를 찾는다."""
    matches = sorted(root.glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"{label} 검색 결과가 하나가 아닙니다: {matches}")
    return matches[0]


def verify_language(instance: Path) -> tuple[dict[str, object], list[str]]:
    """작업 영어 원문과 한국어 산출물이 현재 JAR에 정확히 대응하는지 검사한다."""
    jar = find_one(instance / "mods", "aether-*.jar", "The Aether JAR")
    english = load_json(WORK_ROOT / "aether/en_us.json")
    korean = load_json(WORK_ROOT / "aether/ko_kr.json")
    output = load_json(OUTPUT_ASSETS / "aether/lang/ko_kr.json")
    with ZipFile(jar) as archive:
        current = json.loads(
            archive.read("assets/aether/lang/en_us.json").decode("utf-8-sig")
        )
    errors = []
    if list(current.items()) != list(english.items()):
        errors.append("작업 영어 원문이 현재 설치 JAR과 다릅니다.")
    if list(korean.items()) != list(output.items()):
        errors.append("검수 작업본과 The Aether 리소스팩 산출물이 다릅니다.")
    for key, source in english.items():
        errors.extend(family_goal.validate_value(key, source, korean[key]))
    return {
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_sha256": sha256(jar),
        "english_keys": len(english),
        "korean_keys": len(korean),
        "source_matches_installed_jar": english == current,
        "output_matches_working_copy": korean == output,
        "output_sha256": sha256(OUTPUT_ASSETS / "aether/lang/ko_kr.json"),
    }, errors


def verify_advancements(instance: Path) -> tuple[dict[str, object], list[str]]:
    """발전 과제 표시 요소가 모두 번역 키를 거치는지 검사한다."""
    jar = find_one(instance / "mods", "aether-*.jar", "The Aether JAR")
    catalog = load_json(OUTPUT_ASSETS / "aether/lang/ko_kr.json")
    visible_literals = []
    missing = []
    display_fields = 0
    with ZipFile(jar) as archive:
        names = [
            name
            for name in archive.namelist()
            if name.startswith(
                ("data/aether/advancement/", "data/aether/advancements/")
            )
            and name.endswith(".json")
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
                    if isinstance(key, str) and key not in catalog:
                        missing.append(f"{name}:{field}:{key}")
    errors = []
    if len(names) != 343:
        errors.append(f"발전 과제 파일 수가 예상과 다릅니다: {len(names)}/343")
    if display_fields != 60:
        errors.append(f"발전 과제 표시 필드 수가 예상과 다릅니다: {display_fields}/60")
    if visible_literals:
        errors.append(
            "직접 표시되는 발전 과제 문구가 있습니다: "
            + " | ".join(visible_literals[:20])
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
    """별도 Patchouli 또는 GuideME 가이드 표시 경로가 없는지 검사한다."""
    jar = find_one(instance / "mods", "aether-*.jar", "The Aether JAR")
    candidates = []
    with ZipFile(jar) as archive:
        for name in archive.namelist():
            lower = name.lower()
            if "patchouli_books/" in lower or "ae2guide/" in lower:
                candidates.append(name)
    errors = []
    if candidates:
        errors.append(
            "별도 가이드 표시 경로가 있습니다: " + " | ".join(candidates[:20])
        )
    return {
        "patchouli_or_guideme_paths": len(candidates),
        "book_of_lore_display_path": "assets/aether/lang의 lore.* 키 242개",
    }, errors


def verify_kubejs(instance: Path) -> tuple[dict[str, object], list[str]]:
    """KubeJS 참조 파일과 공지 직접 표시 문구를 검사한다."""
    references = []
    pattern = re.compile(r"\baether\b|aether:", re.IGNORECASE)
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
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        if pattern.search(text):
            references.append(path.relative_to(instance).as_posix())
    relative = Path("kubejs/server_scripts/announcements/announcements.js")
    source = (instance / relative).read_text(encoding="utf-8-sig")
    output = (active_output_root() / "overrides" / relative).read_text(encoding="utf-8")
    old = 'addAnnouncement("4.6", "Added mods: Aether, BotanyPots, BotanyTrees and RefinedTypes")'
    new = 'addAnnouncement("4.6", "추가된 모드: The Aether, BotanyPots, BotanyTrees, RefinedTypes")'
    errors = []
    if len(references) != 2:
        errors.append(
            f"The Aether KubeJS 참조 파일 수가 예상과 다릅니다: {len(references)}/2"
        )
    original_source = source.count(old) == 1 and new not in source
    applied_source = source == output and source.count(new) == 1 and old not in source
    if (
        not (original_source or applied_source)
        or output.count(new) != 1
        or old in output
    ):
        errors.append(
            "The Aether 추가 공지 한 줄이 원문과 산출물에 정확히 대응하지 않습니다."
        )
    if original_source and output != source.replace(old, new):
        errors.append("KubeJS 공지 산출물에 The Aether 한 줄 이외의 차이가 있습니다.")
    return {
        "files_referencing_family": len(references),
        "referenced_paths": references,
        "direct_display_lines_translated": output.count(new),
        "recipe_only_reference_files": 1,
        "source_state": "english_source" if original_source else "already_applied",
    }, errors


def verify_bibliowoods(instance: Path) -> tuple[dict[str, object], list[str]]:
    """BiblioWoods 스카이루트 가구 157개 키와 누적 병합을 검사한다."""
    jar = find_one(instance / "mods", "bibliowoods-*.jar", "BiblioWoods JAR")
    with ZipFile(jar) as archive:
        all_english = json.loads(
            archive.read("assets/bibliowoods/lang/en_us.json").decode("utf-8-sig")
        )
    scoped = {
        key: value for key, value in all_english.items() if "aether_skyroot" in key
    }
    working_en = load_json(WORK_ROOT / "bibliowoods/en_us.json")
    working_ko = load_json(WORK_ROOT / "bibliowoods/ko_kr.json")
    output = load_json(OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json")
    errors = []
    if len(scoped) != 157 or scoped != working_en:
        errors.append("BiblioWoods 스카이루트 현재 원문 157개와 작업 범위가 다릅니다.")
    if any(output.get(key) != value for key, value in working_ko.items()):
        errors.append("BiblioWoods 스카이루트 작업본과 누적 산출물이 다릅니다.")
    return {
        "jar": jar.name,
        "keys_checked": len(scoped),
        "merged_output_keys": len(output),
        "previous_completed_keys_preserved": len(output) - len(scoped),
    }, errors


def verify_small_integrations(instance: Path) -> tuple[dict[str, object], list[str]]:
    """네 직접 연동 모드의 현재 영어 키와 부분 산출물을 검사한다."""
    rows = {}
    errors = []
    for namespace, spec in review.SMALL_INTEGRATIONS.items():
        jar = find_one(instance / "mods", str(spec["jar_pattern"]), namespace)
        with ZipFile(jar) as archive:
            current = json.loads(
                archive.read(f"assets/{namespace}/lang/en_us.json").decode("utf-8-sig")
            )
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        output = load_json(OUTPUT_ASSETS / namespace / "lang/ko_kr.json")
        if any(current.get(key) != value for key, value in english.items()):
            errors.append(f"{namespace} 작업 원문이 현재 JAR과 다릅니다.")
        if any(output.get(key) != value for key, value in korean.items()):
            errors.append(f"{namespace} 작업본과 누적 산출물이 다릅니다.")
        rows[namespace] = {
            "jar": jar.name,
            "keys_checked": len(english),
            "merged_output_keys": len(output),
        }
    return rows, errors


def verify_live(instance: Path) -> tuple[dict[str, object], list[str]]:
    """적용 뒤 실제 인스턴스와 저장소 산출물의 해시 일치를 검사한다."""
    pairs = {
        "aether": (
            OUTPUT_ASSETS / "aether/lang/ko_kr.json",
            instance / "resourcepacks/ATM10_Korean/assets/aether/lang/ko_kr.json",
        ),
        "bibliowoods": (
            OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json",
            instance / "resourcepacks/ATM10_Korean/assets/bibliowoods/lang/ko_kr.json",
        ),
        "auroras": (
            OUTPUT_ASSETS / "auroras/lang/ko_kr.json",
            instance / "resourcepacks/ATM10_Korean/assets/auroras/lang/ko_kr.json",
        ),
        "rainbows": (
            OUTPUT_ASSETS / "rainbows/lang/ko_kr.json",
            instance / "resourcepacks/ATM10_Korean/assets/rainbows/lang/ko_kr.json",
        ),
        "create_dragons_plus": (
            OUTPUT_ASSETS / "create_dragons_plus/lang/ko_kr.json",
            instance
            / "resourcepacks/ATM10_Korean/assets/create_dragons_plus/lang/ko_kr.json",
        ),
        "theurgy": (
            OUTPUT_ASSETS / "theurgy/lang/ko_kr.json",
            instance / "resourcepacks/ATM10_Korean/assets/theurgy/lang/ko_kr.json",
        ),
        "ftbquests": (
            QUEST_OUTPUT,
            instance / "config/ftbquests/quests/lang/ko_kr.snbt",
        ),
        "kubejs": (
            active_output_root()
            / "overrides/kubejs/server_scripts/announcements/announcements.js",
            instance / "kubejs/server_scripts/announcements/announcements.js",
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
        ("bibliowoods", verify_bibliowoods),
        ("direct_integrations", verify_small_integrations),
    ):
        row, found = verifier(instance)
        report[label] = row
        errors.extend(found)
    quests, quest_errors = family_goal.verify_quests(instance, "aether")
    report["ftbquests"] = quests
    errors.extend(quest_errors)
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
