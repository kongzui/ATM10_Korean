#!/usr/bin/env python3
"""Apotheosis 계열 언어 파일의 구조와 보호 문자열을 검증하고 반영한다."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from apotheosis_catalog import BATCHES, TARGETS, Target
from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_apotheosis import WORK_ROOT, duplicate_keys, find_jar, load_json

OUTPUT_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
INTEGRATION_OUTPUT_SOURCES = {
    "create_enchantment_industry": (
        PROJECT_ROOT / "working/create/create_enchantment_industry/ko_kr.json"
    ),
    "irons_spellbooks": (
        PROJECT_ROOT / "working/irons_spells/irons_spellbooks/ko_kr.json"
    ),
}
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?%?")
ALLOWED_IDENTICAL_VALUES = {
    "Apotheosis",
    "Apothic Attributes",
    "Apothic Enchanting",
    "Apothic Spawners",
    "Arcana",
    "ARCANA",
    "Eterna",
    "ETERNA",
    "Quanta",
    "QUANTA",
}
ALLOWED_IDENTICAL_KEYS = {
    "button.apotheosis.return",
    "chat.apotheosis.link_item_with_count",
    "misc.apotheosis.affix_name.two",
    "misc.apotheosis.affix_name.three",
    "misc.apotheosis.affix_name.four",
    "misc.apotheosis.affix_bounds",
    "affix.apotheosis.cooldown",
    "text.apotheosis.cost",
    "text.apotheosis.dot_prefix",
    "text.apotheosis.star_prefix",
    "info.apotheosis.criteria_done",
    "info.apotheosis.criteria_unfinished",
    "info.apotheosis.criteria_unknown",
    "item.apotheosis.gem.normal",
    "jukebox_song.apotheosis.flash",
    "subtitle.apotheosis.music_disc.flash",
    "jukebox_song.apotheosis.glimmer",
    "subtitle.apotheosis.music_disc.glimmer",
    "jukebox_song.apotheosis.shimmer",
    "subtitle.apotheosis.music_disc.shimmer",
    "painting.apotheosis.gems.author",
    "painting.apotheosis.craig.author",
    "painting.apotheosis.tower.author",
    "painting.apotheosis.enchanting_table.author",
    "painting.apotheosis.window.author",
    "info.apothic_enchanting.weight",
    "info.apothic_enchanting.leashed_entity_title",
    "jukebox_song.apothic_enchanting.eterna",
    "subtitle.apothic_enchanting.music_disc.eterna",
    "jukebox_song.apothic_enchanting.quanta",
    "subtitle.apothic_enchanting.music_disc.quanta",
    "jukebox_song.apothic_enchanting.arcana",
    "subtitle.apothic_enchanting.music_disc.arcana",
    "misc.apothic_spawners.concat",
    "misc.apothic_spawners.value_concat",
    "create_enchantment_industry.gui.goggles.affix_augmentor.rejected",
    "create_enchantment_industry.gui.goggles.blaze_composer.result.rejected_affix",
    "create_enchantment_industry.gui.goggles.gem_cutter.result_line",
    "create_enchantment_industry.gui.goggles.gem_cutter.result_purity",
    "tooltip.create_enchantment_industry.affix_template.effect.line",
    "itemGroup.create_enchantment_industry.apotheotic",
}


def protected(value: object, pattern: re.Pattern[str]) -> Counter[str]:
    if not isinstance(value, str):
        return Counter()
    return Counter(pattern.findall(value))


def load_working(path: Path) -> dict[str, object]:
    """중복 키와 BOM을 거부하며 작업 파일을 읽는다."""
    if path.read_bytes().startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"UTF-8 BOM이 있습니다: {path}")

    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"중복 키가 있습니다: {path}:{key}")
            result[key] = value
        return result

    value = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates
    )
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def validate_value(
    key: str, english: object, korean: object, errors: list[str]
) -> None:
    if type(english) is not type(korean):
        errors.append(f"자료형 불일치: {key}")
        return
    if isinstance(english, str):
        for name, pattern in (
            ("자리표시자", PLACEHOLDER),
            ("서식 코드", FORMAT_CODE),
            ("숫자", NUMBER),
        ):
            if (name != "숫자" or protected(english, pattern)) and protected(
                english, pattern
            ) != protected(korean, pattern):
                errors.append(f"{name} 불일치: {key}")
        if english.count("\n") != korean.count("\n"):
            errors.append(f"줄바꿈 수 불일치: {key}")
        return
    if english != korean:
        errors.append(f"비문자 값 변경: {key}")


def verify_target(
    instance: Path,
    target: Target,
    copy_output: bool,
) -> dict[str, object]:
    jar_path = find_jar(instance, target)
    with ZipFile(jar_path) as jar:
        english_all = load_json(jar, f"assets/{target.namespace}/lang/en_us.json")
        candidate = load_json(jar, f"assets/{target.namespace}/lang/ko_kr.json")
        english_duplicates = {
            key
            for key in duplicate_keys(jar, f"assets/{target.namespace}/lang/en_us.json")
            if target.includes(key)
        }
    if english_duplicates:
        raise RuntimeError(
            f"영어 표시 키에 중복이 있습니다: {target.namespace}:{english_duplicates}"
        )
    english = {key: value for key, value in english_all.items() if target.includes(key)}
    working_path = WORK_ROOT / target.namespace / "ko_kr.json"
    korean = load_working(working_path)
    errors: list[str] = []
    if list(korean) != list(english):
        missing = sorted(set(english) - set(korean))
        extra = sorted(set(korean) - set(english))
        errors.append(f"키 또는 순서 불일치: 누락={missing}, 초과={extra}")
    for key in english.keys() & korean.keys():
        validate_value(key, english[key], korean[key], errors)
    untranslated = [
        key
        for key, value in korean.items()
        if isinstance(value, str)
        and value == english.get(key)
        and re.search(r"[A-Za-z]", value)
        and value not in ALLOWED_IDENTICAL_VALUES
        and key not in ALLOWED_IDENTICAL_KEYS
        and not key.startswith("enchantment.level.")
    ]
    if untranslated:
        errors.append(f"영어와 같은 미번역 값: {untranslated}")
    if errors:
        raise RuntimeError(f"{target.namespace} 검증 실패:\n" + "\n".join(errors[:40]))

    output = OUTPUT_ROOT / target.namespace / "lang/ko_kr.json"
    if copy_output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output_source = INTEGRATION_OUTPUT_SOURCES.get(target.namespace, working_path)
        if output_source != working_path:
            complete_korean = load_working(output_source)
            mismatched = [
                key
                for key, value in korean.items()
                if complete_korean.get(key) != value
            ]
            if mismatched:
                raise RuntimeError(
                    f"{target.namespace} 주 계열 작업본과 불일치: {mismatched[:40]}"
                )
        shutil.copyfile(output_source, output)
    reused = sum(candidate.get(key) == value for key, value in korean.items())
    return {
        "batch": target.batch,
        "jar": jar_path.name,
        "namespace": target.namespace,
        "keys": len(english),
        "jar_korean_reused": reused,
        "new_or_revised": len(english) - reused,
        "output": output.relative_to(PROJECT_ROOT).as_posix(),
        "validation": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", choices=BATCHES + ("all",))
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--copy-output", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    selected = [
        target
        for target in TARGETS
        if args.batch == "all" or target.batch == args.batch
    ]
    rows = [verify_target(instance, target, args.copy_output) for target in selected]
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
