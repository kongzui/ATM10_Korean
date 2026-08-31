#!/usr/bin/env python3
"""Eternal Starlight 본체와 직접 연동 표시 경로를 전수 재검수한다."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import eternal_starlight_advancements
import eternal_starlight_art
import eternal_starlight_book
import eternal_starlight_names
import eternal_starlight_prose
import eternal_starlight_quests
import eternal_starlight_ui
import five_family_goal as family_goal
import twilight_family
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/eternal_starlight"
LANG_ROOT = WORK_ROOT / "eternal_starlight"
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"
OUTPUT_OVERRIDES = active_output_root() / "overrides"

BIBLIOWOODS = {
    "Banyin": "바닌나무",
    "Cradlewood": "요람나무",
    "Jinglestem": "방울줄기",
    "Lunar": "달빛나무",
    "Northland": "북방나무",
    "Scarlet": "진홍나무",
    "Torreya": "개비자나무",
}

HOSTILE_NETWORKS = {
    "hostilenetworks.trivia.eternal_starlight.lonestar_skeleton": (
        "별빛 차원을 떠돌아다닙니다.\n산산조각 칼날을 던져 공격합니다."
    ),
    "hostilenetworks.trivia.eternal_starlight.aurora_deer": (
        "별빛 영구동토 숲에서 온\n신비로운 생물입니다.\n염소처럼 들이받습니다."
    ),
    "hostilenetworks.trivia.eternal_starlight.crystallized_moth": (
        "어떻게 워든의 음파 충격파를\n배운 걸까요?\n결정화 사막의 신비한 힘\n덕분인지도 모릅니다..."
    ),
    "hostilenetworks.trivia.eternal_starlight.ent": (
        "별빛 차원에서 발견되는\n작고 귀여운 생물입니다.\n달빛나무 잎을\n모자처럼 쓰고 있습니다."
    ),
    "hostilenetworks.trivia.eternal_starlight.freeze": (
        "골렘 제련소의 수호자입니다.\n얼음으로 만들어졌지만\n불에 면역입니다.\n강력한 기술력이군요!"
    ),
    "hostilenetworks.trivia.eternal_starlight.gleech": (
        "결정화 사막에 사는\n작은 곤충입니다.\n새끼는 적에게 달라붙습니다."
    ),
    "hostilenetworks.trivia.eternal_starlight.grimstone_golem": (
        "응회암 골렘은 몹 투표에서\n탈락했습니다.\n이제 별빛 차원에서\n다시 태어났습니다."
    ),
    "hostilenetworks.trivia.eternal_starlight.luminaris": (
        "심연에 삽니다.\n미지의 세계를 밝힙니다."
    ),
    "hostilenetworks.trivia.eternal_starlight.luminofish": (
        "심연에 삽니다.\n복어처럼 적을 중독시켜\n스스로를 보호합니다."
    ),
    "hostilenetworks.trivia.eternal_starlight.lunar_monstrosity": (
        "저주받은 정원의 우두머리입니다.\n포자와 가시로 공격합니다.\n불태우지 않으면 거의 무적입니다."
    ),
    "hostilenetworks.trivia.eternal_starlight.nightfall_spider": (
        "별빛 차원을 기어 다닙니다.\n외별 스켈레톤이 타고 다닙니다."
    ),
    "hostilenetworks.trivia.eternal_starlight.ratlin": (
        "피글린이나 호글린과 비슷한\n소리를 냅니다.\n하지만 그들만큼 공격적이지는 않습니다."
    ),
    "hostilenetworks.trivia.eternal_starlight.starlight_golem": (
        "골렘 제련소의 우두머리입니다.\n에너지가 어디서 오는지는\n아무도 모릅니다."
    ),
    "hostilenetworks.trivia.eternal_starlight.tangled": (
        "저주받은 정원의 수호자입니다.\n죽은 뒤에도 해골이\n적을 공격할 수 있습니다."
    ),
    "hostilenetworks.trivia.eternal_starlight.tangled_hatred": (
        "깁니다.\n아주 깁니다.\n아주아주 기이이이이이이이이이일어요."
    ),
    "hostilenetworks.trivia.eternal_starlight.thirst_walker": (
        "엔더맨을 닮은 생물입니다.\n세상의 모든 것을\n먹고 싶어 합니다.\n당신도 포함해서요."
    ),
    "hostilenetworks.trivia.eternal_starlight.yeti": (
        "하얀 예티 털은 양털처럼\n가위로 깎을 수 있습니다.\n하지만 염색할 수는 없습니다."
    ),
}

KUBE_REPLACEMENTS = {
    "kubejs/startup_scripts/CustomAdditions.js": (
        "allthemods.create('starlight_prediction').displayName('Generalized Starlight Prediction');",
        "allthemods.create('starlight_prediction').displayName('범용 별빛 예측');",
    ),
    "kubejs/client_scripts/tooltips.js": (
        "Text.of('This loot bag is from the \\\"Lunar Monstrosity\\\".')",
        "Text.of('이 전리품 가방은 \\\"달빛 괴수\\\"에게서 나옵니다.')",
    ),
    "kubejs/server_scripts/announcements/announcements.js": (
        'Text.of("We are preparing to ").append(Text.red("REMOVE")).append(" mods ").append(Text.blue("Eternal Starlight")).append(" and ").append(Text.blue("Hyperbox")).append(", be ready when updating to version 6.0+")',
        'Text.of("버전 6.0 이상으로 업데이트할 때를 대비해 ").append(Text.blue("Eternal Starlight")).append("와 ").append(Text.blue("Hyperbox")).append(" 모드를 ").append(Text.red("제거")).append("할 준비를 하고 있습니다")',
    ),
}


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


def reviewed_value(key: str, source: str) -> tuple[str | None, str | None]:
    """키 유형별 검수 번역과 출처를 돌려준다."""
    exact_maps = (
        eternal_starlight_advancements.TRANSLATIONS,
        eternal_starlight_book.TRANSLATIONS,
        eternal_starlight_prose.TRANSLATIONS,
        eternal_starlight_ui.DEATH_TRANSLATIONS,
        eternal_starlight_ui.SUBTITLE_TRANSLATIONS,
        eternal_starlight_art.PAINTING_TITLES,
    )
    for translations in exact_maps:
        if key in translations:
            return translations[key], "manual_review"
    if key.startswith(eternal_starlight_art.KEEP_ORIGINAL_PREFIXES) or key.endswith(
        eternal_starlight_art.KEEP_ORIGINAL_SUFFIXES
    ):
        return source, "keep_original"
    if key.startswith("item.eternal_starlight.music_disc_") and key.endswith(".desc"):
        return source, "keep_original"
    translated = eternal_starlight_names.translate_name(source)
    if translated is not None:
        origin = "keep_original" if translated == source else "manual_pattern_review"
        return translated, origin
    return None, None


def review_language() -> dict[str, object]:
    """현재 영어 원문 1,788개를 모두 검수하고 완성본을 생성한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    reviewed: dict[str, str] = {}
    provenance: dict[str, str] = {}
    unresolved: list[dict[str, str]] = []
    for key, source in english.items():
        translated, origin = reviewed_value(key, source)
        if translated is None or origin is None:
            reviewed[key] = source
            provenance[key] = "unresolved"
            unresolved.append({"key": key, "source": source})
            continue
        errors = family_goal.validate_value(key, source, translated)
        if errors:
            raise ValueError("; ".join(errors))
        reviewed[key] = translated
        provenance[key] = origin
    write_json(LANG_ROOT / "ko_kr.json", reviewed)
    write_json(LANG_ROOT / "candidate_sources.json", provenance)
    write_json(WORK_ROOT / "unresolved_language.json", unresolved)
    output = OUTPUT_ASSETS / "eternal_starlight/lang/ko_kr.json"
    write_json(output, reviewed)
    report = {
        "family": "Eternal Starlight",
        "keys_reviewed": len(english),
        "resolved": len(english) - len(unresolved),
        "unresolved": len(unresolved),
        "source_counts": dict(sorted(Counter(provenance.values()).items())),
        "output": output.relative_to(PROJECT_ROOT).as_posix(),
    }
    write_json(WORK_ROOT / "manual_review_report.json", report)
    return report


def build_bibliowoods() -> dict[str, object]:
    """BiblioWoods의 Eternal Starlight 목재 직접 연동 1,099개를 병합한다."""
    jars = sorted((resolve_source_root() / "mods").glob("bibliowoods-*.jar"))
    if len(jars) != 1:
        raise RuntimeError(f"BiblioWoods JAR 수가 1이 아닙니다: {jars}")
    with ZipFile(jars[0]) as archive:
        all_english = json.loads(
            archive.read("assets/bibliowoods/lang/en_us.json").decode("utf-8-sig")
        )
    english = {
        key: value for key, value in all_english.items() if "eternal_starlight" in key
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
    if len(english) != 1099:
        raise RuntimeError(f"BiblioWoods 연동 키가 1,099개가 아닙니다: {len(english)}")
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


def build_hostile_networks() -> dict[str, object]:
    """ATM10 KubeJS의 Hostile Neural Networks 퀴즈 문구 17개를 생성한다."""
    source = resolve_source_root() / "kubejs/assets/hostilenetworks/lang/en_us.json"
    all_english = load_json(source)
    scoped = {
        key: value
        for key, value in all_english.items()
        if key.startswith("hostilenetworks.trivia.eternal_starlight.")
    }
    if set(scoped) != set(HOSTILE_NETWORKS):
        raise RuntimeError(
            "Hostile Neural Networks Eternal Starlight 키가 달라졌습니다"
        )
    for key, value in scoped.items():
        errors = family_goal.validate_value(key, value, HOSTILE_NETWORKS[key])
        if errors:
            raise ValueError("; ".join(errors))
    root = WORK_ROOT / "integrations/hostilenetworks"
    write_json(root / "en_us.json", scoped)
    write_json(root / "ko_kr.json", HOSTILE_NETWORKS)
    write_json(
        root / "candidate_sources.json",
        {key: "manual_review" for key in HOSTILE_NETWORKS},
    )
    output = OUTPUT_ASSETS / "hostilenetworks/lang/ko_kr.json"
    merged = load_json(output) if output.is_file() else {}
    preserved = sum(key not in scoped for key in merged)
    merged.update(HOSTILE_NETWORKS)
    write_json(output, merged)
    return {
        "keys": len(scoped),
        "existing_keys_preserved": preserved,
        "merged_output_keys": len(merged),
    }


def build_kube_overrides() -> dict[str, object]:
    """실제 표시되는 Eternal Starlight 관련 KubeJS 리터럴만 교정한다."""
    source_root = resolve_source_root()
    results: dict[str, object] = {}
    for relative, (old, new) in KUBE_REPLACEMENTS.items():
        output = OUTPUT_OVERRIDES / relative
        source = source_root / relative
        base = output if output.is_file() else source
        text = base.read_text(encoding="utf-8")
        old_count = text.count(old)
        new_count = text.count(new)
        if old_count == 1 and new_count == 0:
            text = text.replace(old, new)
        elif old_count == 0 and new_count == 1:
            pass
        else:
            raise RuntimeError(
                f"KubeJS 치환 기준 불일치: {relative} old={old_count} new={new_count}"
            )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        results[relative] = {
            "source": source.relative_to(source_root).as_posix(),
            "output": output.relative_to(PROJECT_ROOT).as_posix(),
            "replacement_count": 1,
        }
    return results


def build_integrations() -> dict[str, object]:
    """모든 직접 연동과 KubeJS 표시 경로를 생성한다."""
    report = {
        "bibliowoods": build_bibliowoods(),
        "hostilenetworks": build_hostile_networks(),
        "kubejs": build_kube_overrides(),
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
    """전용 챕터와 관련 챕터의 표시 문구 174개를 영어 원문과 대조한다."""
    reviewed = 0
    scope_counts: dict[str, int] = {}
    for scope in ("eternal_starlight", "related"):
        root = WORK_ROOT / f"quests/{scope}"
        english = load_object_json(root / "en_us.json")
        korean = load_object_json(root / "ko_kr.json")
        sources = load_object_json(root / "candidate_sources.json")
        for key, source in english.items():
            source_text = source if isinstance(source, str) else source[0]
            if not isinstance(source_text, str):
                raise TypeError(f"지원하지 않는 퀘스트 원문 값: {key}={source!r}")
            translated = eternal_starlight_quests.translate(scope, key, source_text)
            current = korean[key]
            if isinstance(current, str):
                replacement: object = translated
            elif isinstance(current, list) and current and isinstance(current[0], str):
                replacement = [translated, *current[1:]]
            else:
                raise TypeError(f"지원하지 않는 퀘스트 표시 값: {key}={current!r}")
            errors = family_goal.quest_snbt.validate_value(key, source, replacement)
            if errors:
                raise ValueError("; ".join(errors))
            korean[key] = replacement
            sources[key] = "manual_review"
            reviewed += 1
        write_json(root / "ko_kr.json", korean)
        write_json(root / "candidate_sources.json", sources)
        scope_counts[scope] = len(english)
    fallback_root = WORK_ROOT / "quests/fallback"
    write_json(
        fallback_root / "ko_kr.json", eternal_starlight_quests.EXTRA_FALLBACK_TITLES
    )
    write_json(
        fallback_root / "candidate_sources.json",
        {
            key: "manual_fallback_review"
            for key in eternal_starlight_quests.EXTRA_FALLBACK_TITLES
        },
    )
    report = {
        "keys_reviewed": reviewed,
        "scope_counts": scope_counts,
        "new_translation": reviewed,
        "explicit_fallback_titles": len(eternal_starlight_quests.EXTRA_FALLBACK_TITLES),
    }
    write_json(WORK_ROOT / "quest_review_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("review", "build-integrations", "review-quests")
    )
    args = parser.parse_args()
    if args.command == "review":
        report = review_language()
    elif args.command == "build-integrations":
        report = build_integrations()
    else:
        report = review_quests()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
