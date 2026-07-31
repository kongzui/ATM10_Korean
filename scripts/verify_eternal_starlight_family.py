#!/usr/bin/env python3
"""Eternal Starlight 본체와 모든 직접 표시 경로의 완성 산출물을 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
import eternal_starlight_advancements
import eternal_starlight_art
import eternal_starlight_book
import eternal_starlight_family
import eternal_starlight_prose
import eternal_starlight_quests
import eternal_starlight_ui
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/eternal_starlight"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
OUTPUT_OVERRIDES = PROJECT_ROOT / "output/overrides"
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
EXPECTED_JAR = "eternalstarlight-0.8.1+1.21.1+neoforge.jar"
EXPECTED_JAR_SIZE = 57_350_115
EXPECTED_JAR_SHA256 = "acb8fa7a69c4f7d4f1dfa3fba1dbdc96976478ea80b2f9025e43f0c4ee1ceb19"
EXPECTED_KUBEJS_PATHS = {
    "kubejs/assets/hostilenetworks/lang/en_us.json",
    "kubejs/assets/hostilenetworks/lang/ja_jp.json",
    "kubejs/assets/hostilenetworks/lang/pt_br.json",
    "kubejs/assets/hostilenetworks/lang/zh_cn.json",
    "kubejs/client_scripts/tooltips.js",
    "kubejs/server_scripts/announcements/announcements.js",
    "kubejs/server_scripts/modpack/att_items.js",
    "kubejs/server_scripts/modpack/runic_multis/controllers.js",
    "kubejs/server_scripts/modpack/runic_multis/recipes/runic_crucible.js",
    "kubejs/server_scripts/mods/Eternal Starlight/Datapacks.js",
    "kubejs/server_scripts/mods/Eternal Starlight/Recipes.js",
    "kubejs/server_scripts/mods/modular_machinery/multiblocks/atm/runic_enchanter.js",
    "kubejs/server_scripts/mods/modular_machinery/recipes/atm/runic_crucible.js",
    "kubejs/server_scripts/Tweaks/tags.js",
    "kubejs/startup_scripts/CustomAdditions.js",
    "kubejs/startup_scripts/eternal_starlight/eternal_starlight.js",
}
BOOK_FORMAT_FRAGMENTS = {
    "${color: #acfffc}",
    "${color: #acfffc}${link: eternal_starlight:index}",
    "${color: #acfffc}${link: eternal_starlight:lunar_monstrosity_display}",
    "${color: #acfffc}${link: eternal_starlight:starlight_golem_display}",
}


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
    jar = find_one(instance / "mods", "eternalstarlight-*.jar", "Eternal Starlight JAR")
    english = load_json(WORK_ROOT / "eternal_starlight/en_us.json")
    korean = load_json(WORK_ROOT / "eternal_starlight/ko_kr.json")
    sources = load_json(WORK_ROOT / "eternal_starlight/candidate_sources.json")
    output_path = OUTPUT_ASSETS / "eternal_starlight/lang/ko_kr.json"
    output = load_json(output_path)
    with ZipFile(jar) as archive:
        current = json.loads(
            archive.read("assets/eternal_starlight/lang/en_us.json").decode("utf-8-sig")
        )
        bundled_korean = [
            name
            for name in archive.namelist()
            if name == "assets/eternal_starlight/lang/ko_kr.json"
        ]
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
        errors.append("검수 작업본과 Eternal Starlight 리소스팩 산출물이 다릅니다.")
    if list(english) != list(korean) or list(english) != list(sources):
        errors.append("영어·한국어·출처 키 또는 순서가 서로 다릅니다.")
    if bundled_korean:
        errors.append("예상하지 않은 JAR 내장 한국어가 생겼습니다.")
    if "unresolved" in sources.values():
        errors.append("미해결 언어 키가 남았습니다.")
    for key, source in english.items():
        errors.extend(family_goal.validate_value(key, source, korean[key]))
    exact_maps = {
        **eternal_starlight_advancements.TRANSLATIONS,
        **eternal_starlight_book.TRANSLATIONS,
        **eternal_starlight_prose.TRANSLATIONS,
        **eternal_starlight_ui.DEATH_TRANSLATIONS,
        **eternal_starlight_ui.SUBTITLE_TRANSLATIONS,
        **eternal_starlight_art.PAINTING_TITLES,
    }
    mismatches = [key for key, value in exact_maps.items() if korean.get(key) != value]
    if mismatches:
        errors.append(
            "직접 검수 번역표와 언어 산출물이 다릅니다: " + str(mismatches[:20])
        )
    return {
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_sha256": current_hash,
        "english_keys": len(english),
        "korean_keys": len(korean),
        "bundled_korean_files": len(bundled_korean),
        "output_matches_working_copy": korean == output,
        "exact_manual_entries": len(exact_maps),
        "review_sources": dict(Counter(sources.values())),
        "output_sha256": sha256(output_path),
    }, errors


def verify_advancements(instance: Path) -> tuple[dict[str, object], list[str]]:
    """발전 과제 1,327개 파일의 모든 표시 필드가 번역 키를 거치는지 검사한다."""
    jar = find_one(instance / "mods", "eternalstarlight-*.jar", "Eternal Starlight JAR")
    catalog = load_json(OUTPUT_ASSETS / "eternal_starlight/lang/ko_kr.json")
    literal_fields = []
    missing = []
    translated_keys = []
    display_fields = 0
    with ZipFile(jar) as archive:
        names = sorted(
            name
            for name in archive.namelist()
            if name.endswith(".json")
            and name.startswith(
                (
                    "data/eternal_starlight/advancement/",
                    "data/eternal_starlight/advancements/",
                )
            )
        )
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
                    literal_fields.append(f"{name}:{field}:{shown}")
                elif isinstance(shown, dict):
                    key = shown.get("translate")
                    if not isinstance(key, str) or key not in catalog:
                        missing.append(f"{name}:{field}:{key}")
                    else:
                        translated_keys.append(key)
    errors = []
    if len(names) != 1327:
        errors.append(f"발전 과제 파일 수가 예상과 다릅니다: {len(names)}/1327")
    if display_fields != 122:
        errors.append(f"발전 과제 표시 필드 수가 예상과 다릅니다: {display_fields}/122")
    if literal_fields:
        errors.append(
            "발전 과제 직접 표시 문구가 있습니다: " + str(literal_fields[:20])
        )
    if missing:
        errors.append("발전 과제 번역 키가 빠졌습니다: " + str(missing[:20]))
    if set(translated_keys) != set(eternal_starlight_advancements.TRANSLATIONS):
        errors.append("발전 과제 표시 키와 직접 검수 번역표의 범위가 다릅니다.")
    return {
        "files_checked": len(names),
        "display_fields_checked": display_fields,
        "unique_translation_keys": len(set(translated_keys)),
        "visible_literal_fields": len(literal_fields),
        "missing_translation_keys": len(missing),
    }, errors


def verify_guide(instance: Path) -> tuple[dict[str, object], list[str]]:
    """희미하게 빛나는 서판의 내장 가이드 표시 경로를 검사한다."""
    jar = find_one(instance / "mods", "eternalstarlight-*.jar", "Eternal Starlight JAR")
    catalog = load_json(OUTPUT_ASSETS / "eternal_starlight/lang/ko_kr.json")
    with ZipFile(jar) as archive:
        path = "assets/eternal_starlight/eternal_starlight/books/main.json"
        guide = json.loads(archive.read(path).decode("utf-8-sig"))
        other_guides = [
            name
            for name in archive.namelist()
            if (
                "patchouli_books/" in name.lower()
                or "ae2guide/" in name.lower()
                or "/books/" in name.lower()
            )
            and name != path
            and name.endswith((".json", ".xml", ".md"))
        ]
    rows: list[tuple[bool, str]] = []

    def walk(value: object) -> None:
        if isinstance(value, dict):
            if "content" in value and "translation" in value:
                content = value["content"]
                translated = value["translation"]
                if isinstance(content, str) and isinstance(translated, bool):
                    rows.append((translated, content))
            for nested in value.values():
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    walk(guide)
    translated = [content for flag, content in rows if flag]
    literals = [content for flag, content in rows if not flag]
    missing = sorted({key for key in translated if key not in catalog})
    book_keys = {key for key in translated if key.startswith("book.")}
    errors = []
    if len(translated) != 88 or len(set(translated)) != 60:
        errors.append(
            f"가이드 번역 참조 수가 예상과 다릅니다: {len(translated)}/88, "
            f"고유 {len(set(translated))}/60"
        )
    if len(literals) != 88 or set(literals) != BOOK_FORMAT_FRAGMENTS:
        errors.append("가이드 비번역 조각이 확정 서식·링크 목록과 다릅니다.")
    if missing:
        errors.append("가이드 번역 키가 빠졌습니다: " + str(missing))
    guide_ui_keys = {
        "book.eternal_starlight.unlock",
        "book.eternal_starlight.unlock.multiple",
        "book.eternal_starlight.update",
    }
    if book_keys != set(eternal_starlight_book.TRANSLATIONS) - guide_ui_keys:
        errors.append("가이드 본문 31개와 직접 검수 번역표의 범위가 다릅니다.")
    if other_guides:
        errors.append("예상하지 않은 추가 가이드가 있습니다: " + str(other_guides[:20]))
    return {
        "guide": path,
        "translation_references": len(translated),
        "unique_translation_keys": len(set(translated)),
        "reviewed_book_content_keys": len(book_keys),
        "reviewed_book_ui_keys": len(guide_ui_keys),
        "reviewed_book_keys_total": len(eternal_starlight_book.TRANSLATIONS),
        "format_or_link_fragments": len(literals),
        "unique_format_or_link_fragments": len(set(literals)),
        "missing_translation_keys": len(missing),
        "additional_guide_files": len(other_guides),
    }, errors


def verify_bibliowoods(instance: Path) -> tuple[dict[str, object], list[str]]:
    """BiblioWoods 직접 연동 1,099개와 이전 모드 범위 보존을 검사한다."""
    jar = find_one(instance / "mods", "bibliowoods-*.jar", "BiblioWoods JAR")
    with ZipFile(jar) as archive:
        all_english = json.loads(
            archive.read("assets/bibliowoods/lang/en_us.json").decode("utf-8-sig")
        )
    current = {
        key: value for key, value in all_english.items() if "eternal_starlight" in key
    }
    english = load_json(WORK_ROOT / "integrations/bibliowoods/en_us.json")
    korean = load_json(WORK_ROOT / "integrations/bibliowoods/ko_kr.json")
    output_path = OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json"
    output = load_json(output_path)
    preserved: dict[str, object] = {}
    for path in (
        PROJECT_ROOT / "working/twilight_forest/bibliowoods/ko_kr.json",
        PROJECT_ROOT / "working/undergarden/bibliowoods/ko_kr.json",
        PROJECT_ROOT / "working/aether/bibliowoods/ko_kr.json",
    ):
        preserved.update(load_json(path))
    errors = []
    if len(current) != 1099 or list(current.items()) != list(english.items()):
        errors.append(
            "현재 BiblioWoods Eternal Starlight 원문 1,099개와 범위가 다릅니다."
        )
    if set(korean) != set(english):
        errors.append("BiblioWoods 작업 영어·한국어 키가 다릅니다.")
    for key, source in english.items():
        errors.extend(family_goal.validate_value(key, source, korean[key]))
        if output.get(key) != korean[key]:
            errors.append(f"BiblioWoods 누적 출력 불일치: {key}")
    preserved_mismatches = [
        key for key, value in preserved.items() if output.get(key) != value
    ]
    if len(preserved) != 1884 or preserved_mismatches:
        errors.append(
            f"BiblioWoods 이전 범위 보존 실패: {len(preserved)}/1884, "
            f"불일치={preserved_mismatches[:20]}"
        )
    if len(output) < 2983:
        errors.append(
            f"BiblioWoods 누적 출력 키가 기존 완료 범위보다 적습니다: {len(output)}/2983"
        )
    return {
        "jar": jar.name,
        "direct_keys_checked": len(current),
        "prior_keys_preserved": len(preserved),
        "merged_output_keys": len(output),
        "output_sha256": sha256(output_path),
    }, errors


def verify_kubejs(instance: Path) -> tuple[dict[str, object], list[str]]:
    """KubeJS 참조 16개와 실제 표시 리터럴 네 경로를 검사한다."""
    family = re.compile(r"eternal_starlight|Eternal Starlight", re.IGNORECASE)
    references = set()
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
        if family.search(content):
            references.add(path.relative_to(instance).as_posix())
    errors = []
    if references != EXPECTED_KUBEJS_PATHS:
        errors.append(
            "KubeJS 참조 경로가 예상과 다릅니다: "
            f"누락={sorted(EXPECTED_KUBEJS_PATHS - references)}, "
            f"추가={sorted(references - EXPECTED_KUBEJS_PATHS)}"
        )
    replacement_rows = {}
    for relative, (old, new) in eternal_starlight_family.KUBE_REPLACEMENTS.items():
        output = OUTPUT_OVERRIDES / relative
        source = instance / relative
        source_text = source.read_text(encoding="utf-8")
        output_text = output.read_text(encoding="utf-8")
        source_is_english = source_text.count(old) == 1 and source_text.count(new) == 0
        source_is_applied = source_text.count(old) == 0 and source_text.count(new) == 1
        valid = (
            (source_is_english or source_is_applied)
            and output_text.count(old) == 0
            and output_text.count(new) == 1
        )
        replacement_rows[relative] = {
            "valid": valid,
            "source_state": "applied" if source_is_applied else "english",
        }
        if not valid:
            errors.append(f"KubeJS 직접 표시 문구 치환이 맞지 않습니다: {relative}")
    hostile_source = load_json(
        instance / "kubejs/assets/hostilenetworks/lang/en_us.json"
    )
    hostile_current = {
        key: value
        for key, value in hostile_source.items()
        if key.startswith("hostilenetworks.trivia.eternal_starlight.")
    }
    hostile_work = load_json(WORK_ROOT / "integrations/hostilenetworks/ko_kr.json")
    hostile_output_path = OUTPUT_ASSETS / "hostilenetworks/lang/ko_kr.json"
    hostile_output = load_json(hostile_output_path)
    if set(hostile_current) != set(eternal_starlight_family.HOSTILE_NETWORKS):
        errors.append(
            "Hostile Neural Networks 현재 Eternal Starlight 키가 달라졌습니다."
        )
    if hostile_work != eternal_starlight_family.HOSTILE_NETWORKS:
        errors.append("Hostile Neural Networks 작업본이 직접 검수 번역표와 다릅니다.")
    for key, value in hostile_work.items():
        if hostile_output.get(key) != value:
            errors.append(f"Hostile Neural Networks 누적 출력 불일치: {key}")
    datapacks = (
        instance / "kubejs/server_scripts/mods/Eternal Starlight/Datapacks.js"
    ).read_text(encoding="utf-8")
    trivia_refs = set(
        re.findall(r'"(hostilenetworks\.trivia\.eternal_starlight\.[^"]+)"', datapacks)
    )
    unreferenced_trivia = set(hostile_current) - trivia_refs
    expected_unreferenced = {"hostilenetworks.trivia.eternal_starlight.tangled_hatred"}
    if trivia_refs != set(hostile_current) - expected_unreferenced:
        errors.append("Datapacks.js의 퀴즈 번역 키 참조가 현재 16개 범위와 다릅니다.")
    if unreferenced_trivia != expected_unreferenced:
        errors.append("Hostile Neural Networks 미참조 퀴즈 키 구성이 달라졌습니다.")
    commented = (
        instance / "kubejs/startup_scripts/eternal_starlight/eternal_starlight.js"
    ).read_text(encoding="utf-8")
    active_lines = [
        line
        for line in commented.splitlines()
        if line.strip() and not line.lstrip().startswith("//")
    ]
    if active_lines:
        errors.append(
            "주석 전용 Eternal Starlight 시작 스크립트에 활성 코드가 생겼습니다."
        )
    return {
        "files_referencing_family": len(references),
        "referenced_paths": sorted(references),
        "direct_literal_overrides": replacement_rows,
        "hostile_networks_trivia_keys": len(hostile_current),
        "datapack_trivia_references": len(trivia_refs),
        "unreferenced_trivia_keys": sorted(unreferenced_trivia),
        "commented_warning_script_active_lines": len(active_lines),
        "hostile_networks_output_sha256": sha256(hostile_output_path),
    }, errors


def verify_quests(instance: Path) -> tuple[dict[str, object], list[str]]:
    """FTB Quests 표시 키 174개와 fallback 제목 11개를 검사한다."""
    report, errors = family_goal.verify_quests(instance, "eternal_starlight")
    output = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    fallback = load_json(WORK_ROOT / "quests/fallback/ko_kr.json")
    mismatches = [key for key, value in fallback.items() if output.get(key) != value]
    if fallback != eternal_starlight_quests.EXTRA_FALLBACK_TITLES:
        errors.append("명시적 fallback 작업본이 직접 검수 번역표와 다릅니다.")
    if len(fallback) != 11 or mismatches:
        errors.append(
            f"명시적 퀘스트 fallback 제목이 맞지 않습니다: {len(fallback)}/11, "
            f"불일치={mismatches}"
        )
    report["source_display_keys_reviewed"] = 174
    report["explicit_fallback_titles"] = len(fallback)
    report["merged_keys_checked"] = 174 + len(fallback)
    report["stale_item_fallbacks_localized"] = len(fallback)
    return report, errors


def verify_live(instance: Path) -> tuple[dict[str, object], list[str]]:
    """실제 인스턴스의 일곱 적용 파일과 저장소 산출물 해시를 비교한다."""
    pairs = {
        "eternal_starlight": (
            OUTPUT_ASSETS / "eternal_starlight/lang/ko_kr.json",
            instance
            / "resourcepacks/ATM10_Korean/assets/eternal_starlight/lang/ko_kr.json",
        ),
        "bibliowoods": (
            OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json",
            instance / "resourcepacks/ATM10_Korean/assets/bibliowoods/lang/ko_kr.json",
        ),
        "hostilenetworks": (
            OUTPUT_ASSETS / "hostilenetworks/lang/ko_kr.json",
            instance
            / "resourcepacks/ATM10_Korean/assets/hostilenetworks/lang/ko_kr.json",
        ),
        "ftbquests": (
            QUEST_OUTPUT,
            instance / "config/ftbquests/quests/lang/ko_kr.snbt",
        ),
        "custom_additions": (
            OUTPUT_OVERRIDES / "kubejs/startup_scripts/CustomAdditions.js",
            instance / "kubejs/startup_scripts/CustomAdditions.js",
        ),
        "tooltips": (
            OUTPUT_OVERRIDES / "kubejs/client_scripts/tooltips.js",
            instance / "kubejs/client_scripts/tooltips.js",
        ),
        "announcements": (
            OUTPUT_OVERRIDES / "kubejs/server_scripts/announcements/announcements.js",
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
        ("guide", verify_guide),
        ("bibliowoods", verify_bibliowoods),
        ("kubejs", verify_kubejs),
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
