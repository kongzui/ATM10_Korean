#!/usr/bin/env python3
"""Allthemodium·ATM 장비 관련 KubeJS 표시 문구만 번역한다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

OUTPUT_ROOT = active_output_root() / "overrides"
REPORT_FILE = PROJECT_ROOT / "working/atmgear/kubejs_audit.json"

REPLACEMENTS: dict[str, list[tuple[str, str, int]]] = {
    "kubejs/client_scripts/tooltips.js": [
        (
            "§7Needs at least Netherite to be mined",
            "§7채굴하려면 네더라이트 등급 이상이 필요합니다",
            1,
        ),
        (
            "§6Found in the Deep Dark Biome and will always spawn air exposed",
            "§6딥 다크 생물 군계에서 공기에 노출된 상태로 생성됩니다",
            1,
        ),
        (
            "§6Also found in the Deep Slate Layer of Mining Dimension",
            "§6채굴 차원의 심층암 지층에서도 발견됩니다",
            1,
        ),
        (
            "§7Needs at least AllTheModium to be mined",
            "§7채굴하려면 Allthemodium 등급 이상이 필요합니다",
            1,
        ),
        ("§bFound in any Nether biome", "§b모든 네더 생물 군계에서 발견됩니다", 1),
        ("§bAlso found in The Other", "§b디 아더에서도 발견됩니다", 1),
        (
            "§7Needs at least Vibranium to be mined",
            "§7채굴하려면 Vibranium 등급 이상이 필요합니다",
            1,
        ),
        ("§dFound in the End Highlands", "§d엔드 고지대에서 발견됩니다", 1),
        ("§7§oIt's less... talkative now", "§7§o이제 덜... 시끄럽네요", 3),
        (
            "§7§oThese arent the ingots you are looking for",
            "§7§o찾으시는 주괴가 아닙니다",
            3,
        ),
        (
            "§6Look for the [Silent Allthemodium Plate]",
            "§6[Silent Gear Allthemodium 판]을 찾아보세요",
            1,
        ),
        (
            "§6Look for the [Silent Vibranium Plate]",
            "§6[Silent Gear Vibranium 판]을 찾아보세요",
            1,
        ),
        (
            "§6Look for the [Silent Unobtainium Plate]",
            "§6[Silent Gear Unobtainium 판]을 찾아보세요",
            1,
        ),
        (
            "§6Found in Suspicious Clay in Ancient Cities",
            "§6고대 도시의 수상한 점토에서 발견됩니다",
            1,
        ),
        (
            "§bFound in Suspicious Soul Sand in Bastions",
            "§b보루 잔해의 수상한 영혼 모래에서 발견됩니다",
            1,
        ),
        (
            "§dDropped by the Trial Spawner in the Library of the Dungeon within The Other",
            "§d디 아더 던전의 도서관에 있는 시험 생성기에서 나옵니다",
            1,
        ),
    ],
    "kubejs/startup_scripts/CustomAdditions.js": [
        ("Silent Allthemodium Plate", "Silent Gear Allthemodium 판", 1),
        ("Silent Vibranium Plate", "Silent Gear Vibranium 판", 1),
        ("Silent Unobtainium Plate", "Silent Gear Unobtainium 판", 1),
        ("ATM Star Fragment", "ATM의 별 조각", 5),
        ("Allthemodium Solar Sail Package", "Allthemodium 태양 돛 패키지", 1),
        ("Allthemodium Beam Package", "Allthemodium 빔 패키지", 1),
    ],
    "kubejs/startup_scripts/Modern-Industrialization/atm_stuff.js": [
        ("Allthemodium Drill Head", "Allthemodium 드릴 헤드", 1),
        ("Allthemodium Curved Plate", "Allthemodium 곡면 판", 1),
        ("Allthemodium Drill", "Allthemodium 드릴", 1),
        ("Allthemodium Bolt", "Allthemodium 볼트", 1),
        ("Vibranium Drill Head", "Vibranium 드릴 헤드", 1),
        ("Vibranium Curved Plate", "Vibranium 곡면 판", 1),
        ("Vibranium Drill", "Vibranium 드릴", 1),
        ("Vibranium Bolt", "Vibranium 볼트", 1),
        ("Unobtainium Drill Head", "Unobtainium 드릴 헤드", 1),
        ("Unobtainium Curved Plate", "Unobtainium 곡면 판", 1),
        ("Unobtainium Drill", "Unobtainium 드릴", 1),
        ("Unobtainium Bolt", "Unobtainium 볼트", 1),
    ],
    "kubejs/server_scripts/modpack/runic_multis/recipes/star_altar.js": [
        (
            "Awakened Unobtainium-Vibranium Alloy Block",
            "각성한 Unobtainium-Vibranium 합금 블록",
            2,
        )
    ],
}

LEGACY_REPLACEMENTS = {
    "§6Look for the [Silent Allthemodium Plate]": (
        "§6[고요한 Allthemodium 판]을 찾아보세요",
    ),
    "§6Look for the [Silent Vibranium Plate]": (
        "§6[고요한 Vibranium 판]을 찾아보세요",
    ),
    "§6Look for the [Silent Unobtainium Plate]": (
        "§6[고요한 Unobtainium 판]을 찾아보세요",
    ),
    "Silent Allthemodium Plate": ("고요한 Allthemodium 판",),
    "Silent Vibranium Plate": ("고요한 Vibranium 판",),
    "Silent Unobtainium Plate": ("고요한 Unobtainium 판",),
}


def literal_count(source: str, value: str) -> int:
    """JavaScript의 완전한 작은따옴표·큰따옴표 문자열 수를 센다."""
    return source.count(f"'{value}'") + source.count(f'"{value}"')


def translate_file(
    instance: Path, relative: str, rules: list[tuple[str, str, int]]
) -> int:
    """기대한 원문 수를 확인한 뒤 지정 문자열만 바꾼다."""
    source_path = instance / relative
    source = source_path.read_bytes().decode("utf-8-sig")
    translated = source
    changes = 0
    for original, replacement, expected in rules:
        original_count = literal_count(translated, original)
        replacement_count = literal_count(translated, replacement)
        legacy = LEGACY_REPLACEMENTS.get(original, ())
        legacy_count = sum(literal_count(translated, value) for value in legacy)
        if original_count + replacement_count + legacy_count != expected:
            raise RuntimeError(
                f"예상한 KubeJS 원문 수와 다릅니다: {relative}:{original!r} "
                f"expected={expected} "
                f"actual={original_count + replacement_count + legacy_count}"
            )
        translated = translated.replace(original, replacement)
        for value in legacy:
            translated = translated.replace(value, replacement)
        changes += expected
    for original, _, _ in rules:
        if original in translated:
            raise RuntimeError(f"KubeJS 원문이 남았습니다: {relative}:{original!r}")
    output = OUTPUT_ROOT / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(translated.encode("utf-8"))
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    per_file = {
        relative: translate_file(instance, relative, rules)
        for relative, rules in REPLACEMENTS.items()
    }
    report = {
        "files": len(per_file),
        "translated_literal_occurrences": sum(
            expected for rules in REPLACEMENTS.values() for _, _, expected in rules
        ),
        "per_file": per_file,
        "custom_name_literals": 2,
        "remaining": 0,
        "status": "passed",
    }
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
