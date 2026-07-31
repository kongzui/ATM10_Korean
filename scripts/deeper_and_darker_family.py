#!/usr/bin/env python3
"""Deeper and Darker 본체와 직접 연동 표시 경로를 전수 재검수한다."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import deeper_and_darker_language
import deeper_and_darker_quests
import five_family_goal as family_goal
import twilight_family
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/deeper_and_darker"
LANG_ROOT = WORK_ROOT / "deeperdarker"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
OUTPUT_OVERRIDES = PROJECT_ROOT / "output/overrides"

BIBLIOWOODS = {"Bloom": "개화목", "Echo": "메아리나무"}

KUBE_RELATIVE = "kubejs/client_scripts/tooltips.js"
KUBE_OLD = 'Text.of("§9In a Botany Pot: Requires a hoe enchanted with Silk Touch to be harvested")'
KUBE_NEW = (
    'Text.of("§9식물 화분에서 수확하려면 섬세한 손길이 부여된 괭이가 필요합니다")'
)


def load_json(path: Path) -> dict[str, str]:
    """문자열 값으로 이루어진 UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(text, str) for key, text in value.items()
    ):
        raise TypeError(f"문자열 JSON 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 무BOM JSON을 저장한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def find_mod_jar() -> Path:
    """현재 설치된 Deeper and Darker JAR 하나를 찾는다."""
    jars = sorted((resolve_source_root() / "mods").glob("deeperdarker-*.jar"))
    if len(jars) != 1:
        raise RuntimeError(f"Deeper and Darker JAR 수가 1이 아닙니다: {jars}")
    return jars[0]


def review_language() -> dict[str, object]:
    """현재 영어 원문 369개를 모두 검수하고 완성본을 생성한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    jar = find_mod_jar()
    with ZipFile(jar) as archive:
        bundled = json.loads(
            archive.read("assets/deeperdarker/lang/ko_kr.json").decode("utf-8-sig")
        )
    reviewed: dict[str, str] = {}
    provenance: dict[str, str] = {}
    unresolved: list[dict[str, str]] = []
    for key, source in english.items():
        translated = deeper_and_darker_language.translate_name(source)
        if translated is None:
            reviewed[key] = source
            provenance[key] = "unresolved"
            unresolved.append({"key": key, "source": source})
            continue
        errors = family_goal.validate_value(key, source, translated)
        if errors:
            raise ValueError("; ".join(errors))
        reviewed[key] = translated
        if translated == source:
            provenance[key] = "keep_original"
        elif bundled.get(key) == translated:
            provenance[key] = "bundled_reviewed_reuse"
        elif source in deeper_and_darker_language.EXACT_TRANSLATIONS:
            provenance[key] = "manual_review"
        else:
            provenance[key] = "manual_pattern_review"
    if len(english) != 369:
        raise RuntimeError(f"영어 키 수가 369개가 아닙니다: {len(english)}")
    write_json(LANG_ROOT / "ko_kr.json", reviewed)
    write_json(LANG_ROOT / "candidate_sources.json", provenance)
    write_json(WORK_ROOT / "unresolved_language.json", unresolved)
    output = OUTPUT_ASSETS / "deeperdarker/lang/ko_kr.json"
    write_json(output, reviewed)
    report = {
        "family": "Deeper and Darker",
        "keys_reviewed": len(english),
        "bundled_korean_candidates": len(bundled),
        "resolved": len(english) - len(unresolved),
        "unresolved": len(unresolved),
        "source_counts": dict(sorted(Counter(provenance.values()).items())),
        "output": output.relative_to(PROJECT_ROOT).as_posix(),
    }
    write_json(WORK_ROOT / "manual_review_report.json", report)
    return report


def build_bibliowoods() -> dict[str, object]:
    """BiblioWoods의 Deeper and Darker 목재 직접 연동 314개를 병합한다."""
    jars = sorted((resolve_source_root() / "mods").glob("bibliowoods-*.jar"))
    if len(jars) != 1:
        raise RuntimeError(f"BiblioWoods JAR 수가 1이 아닙니다: {jars}")
    with ZipFile(jars[0]) as archive:
        all_english = json.loads(
            archive.read("assets/bibliowoods/lang/en_us.json").decode("utf-8-sig")
        )
    english = {
        key: value for key, value in all_english.items() if "deeperdarker" in key
    }
    old_woods = twilight_family.WOOD_NAMES
    try:
        twilight_family.WOOD_NAMES = BIBLIOWOODS
        korean = {
            key: twilight_family.translate_bibliowoods_value(value)
            for key, value in english.items()
        }
    finally:
        twilight_family.WOOD_NAMES = old_woods
    if len(english) != 314:
        raise RuntimeError(f"BiblioWoods 연동 키가 314개가 아닙니다: {len(english)}")
    unresolved = {
        key: value
        for key, value in korean.items()
        if "Bloom" in value or "Echo" in value or family_goal.LATIN_WORD.search(value)
    }
    if unresolved:
        raise RuntimeError(f"BiblioWoods 영문 잔존: {list(unresolved.items())[:10]}")
    root = WORK_ROOT / "integrations/bibliowoods"
    write_json(root / "en_us.json", english)
    write_json(root / "ko_kr.json", korean)
    write_json(
        root / "candidate_sources.json",
        {key: "generated_reviewed_translation" for key in english},
    )
    output = OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json"
    merged = load_json(output) if output.is_file() else {}
    preserved = sum(key not in english for key in merged)
    merged.update(korean)
    write_json(output, merged)
    return {
        "jar": jars[0].name,
        "keys": len(english),
        "existing_keys_preserved": preserved,
        "merged_output_keys": len(merged),
    }


def scan_kube_references() -> list[dict[str, object]]:
    """KubeJS에서 Deeper and Darker를 직접 참조하는 파일을 분류한다."""
    kube_root = resolve_source_root() / "kubejs"
    results: list[dict[str, object]] = []
    for path in sorted(kube_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        count = text.lower().count("deeperdarker")
        if not count:
            continue
        relative = path.relative_to(resolve_source_root()).as_posix()
        results.append(
            {
                "path": relative,
                "reference_count": count,
                "classification": (
                    "user_visible_literal"
                    if relative == KUBE_RELATIVE
                    else "identifier_only"
                ),
            }
        )
    return results


def build_kube_override() -> dict[str, object]:
    """식물 화분 수확 조건으로 실제 표시되는 KubeJS 문구 1개를 교정한다."""
    source = resolve_source_root() / KUBE_RELATIVE
    output = OUTPUT_OVERRIDES / KUBE_RELATIVE
    base = output if output.is_file() else source
    text = base.read_text(encoding="utf-8")
    old_count = text.count(KUBE_OLD)
    new_count = text.count(KUBE_NEW)
    if old_count == 1 and new_count == 0:
        text = text.replace(KUBE_OLD, KUBE_NEW)
    elif old_count == 0 and new_count == 1:
        pass
    else:
        raise RuntimeError(f"KubeJS 치환 기준 불일치: old={old_count} new={new_count}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    return {
        "source": source.relative_to(resolve_source_root()).as_posix(),
        "output": output.relative_to(PROJECT_ROOT).as_posix(),
        "replacement_count": 1,
        "references": scan_kube_references(),
    }


def audit_advancements() -> dict[str, object]:
    """발전 과제의 title·description 표시 컴포넌트를 검사한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    files = 0
    displayed = 0
    translate_keys: list[str] = []
    literal_texts: list[str] = []
    with ZipFile(find_mod_jar()) as archive:
        names = [
            name
            for name in archive.namelist()
            if name.startswith("data/deeperdarker/advancement/")
            and name.endswith(".json")
        ]
        files = len(names)
        for name in names:
            value = json.loads(archive.read(name).decode("utf-8"))
            display = value.get("display")
            if not isinstance(display, dict):
                continue
            displayed += 1
            for field in ("title", "description"):
                component = display.get(field)
                if isinstance(component, dict) and isinstance(
                    component.get("translate"), str
                ):
                    translate_keys.append(component["translate"])
                elif isinstance(component, dict) and isinstance(
                    component.get("text"), str
                ):
                    literal_texts.append(component["text"])
                elif isinstance(component, str):
                    literal_texts.append(component)
    missing = sorted(set(translate_keys) - set(english))
    report = {
        "advancement_files": files,
        "displayed_advancements": displayed,
        "display_fields": len(translate_keys) + len(literal_texts),
        "translate_references": len(translate_keys),
        "unique_translate_keys": len(set(translate_keys)),
        "literal_display_texts": literal_texts,
        "missing_translation_keys": missing,
        "guide_candidates": 0,
    }
    if literal_texts or missing:
        raise RuntimeError(f"발전 과제 표시 경로 검증 실패: {report}")
    write_json(WORK_ROOT / "advancement_report.json", report)
    return report


def build_integrations() -> dict[str, object]:
    """BiblioWoods·KubeJS·발전 과제 표시 경로를 생성하고 기록한다."""
    report = {
        "bibliowoods": build_bibliowoods(),
        "kubejs": build_kube_override(),
        "advancements": audit_advancements(),
    }
    write_json(WORK_ROOT / "integration_report.json", report)
    return report


def load_object_json(path: Path) -> dict[str, object]:
    """문자열과 목록을 포함하는 UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError(f"JSON 객체가 아닙니다: {path}")
    return value


def review_quests() -> dict[str, object]:
    """전용·관련 퀘스트 표시 문구 97개와 Smart Filter 제목을 검수한다."""
    reviewed = 0
    scope_counts: dict[str, int] = {}
    for scope in ("deeper_and_darker", "related"):
        root = WORK_ROOT / f"quests/{scope}"
        english = load_object_json(root / "en_us.json")
        korean = load_object_json(root / "ko_kr.json")
        sources = load_object_json(root / "candidate_sources.json")
        for key, source in english.items():
            translated = deeper_and_darker_quests.translate(scope, key)
            errors = family_goal.quest_snbt.validate_value(key, source, translated)
            if errors:
                raise ValueError("; ".join(errors))
            korean[key] = translated
            sources[key] = (
                "keep_original_numeric" if translated == source else "manual_review"
            )
            reviewed += 1
        write_json(root / "ko_kr.json", korean)
        write_json(root / "candidate_sources.json", sources)
        scope_counts[scope] = len(english)
    fallback_root = WORK_ROOT / "quests/fallback"
    write_json(
        fallback_root / "ko_kr.json", deeper_and_darker_quests.EXTRA_FALLBACK_TITLES
    )
    write_json(
        fallback_root / "candidate_sources.json",
        {
            key: "manual_fallback_review"
            for key in deeper_and_darker_quests.EXTRA_FALLBACK_TITLES
        },
    )
    report = {
        "keys_reviewed": reviewed,
        "scope_counts": scope_counts,
        "new_or_edited": reviewed - 1,
        "keep_original_numeric": 1,
        "explicit_fallback_task_titles": len(
            deeper_and_darker_quests.EXTRA_FALLBACK_TITLES
        ),
    }
    write_json(WORK_ROOT / "quest_review_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("review", "build-integrations", "audit-advancements", "review-quests"),
    )
    args = parser.parse_args()
    if args.command == "review":
        report = review_language()
    elif args.command == "build-integrations":
        report = build_integrations()
    elif args.command == "review-quests":
        report = review_quests()
    else:
        report = audit_advancements()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
