#!/usr/bin/env python3
"""Silent Gear 계열 언어 파일과 동적 데이터 표시 키를 검증하고 반영한다."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_silentgear import WORK_ROOT, duplicate_keys, find_jar, load_json
from silentgear_catalog import BATCHES, TARGETS, Target

OUTPUT_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?%?")
ALLOWED_IDENTICAL_KEYS = {
    "advancements.silentgear.root.title",
    "command.silentgear.mats.describe.id",
    "command.silentgear.parts.describe.id",
    "command.silentgear.stats.info.format",
    "command.silentgear.stats.info.formatPart",
    "command.silentgear.traits.describe.id",
    "item.silentgear.blueprint.fishing_rod.desc",
    "item.silentgear.custom_gem",
    "item.silentgear.repair_kit.material",
    "item.silentgems.gem",
    "itemGroup.silentgems",
    "key.categories.silentgear",
    "misc.silentgear.key",
    "misc.silentgear.space",
    "misc.silentgear.spaceBrackets",
    "misc.silentgear.tooltip.material.keyHint",
    "property.silentgear.armorFormat",
    "property.silentgear.displayFormat",
    "property.silentgear.durabilityFormat",
    "property.silentgear.harvest_tier.withLevelHint",
    "property.silentgear.traits.displayWithDescription",
    "trait.silentgear.displayFormat",
}
DATA_ONLY_KEYS = {
    "silentgear": {
        "trait.silentgear.dulling",
        "trait.silentgear.dulling.desc",
        "trait.silentgear.flutter",
        "trait.silentgear.flutter.desc",
        "trait.silentgear.red_card.desc",
    },
    "silentgems": {
        "material.silentgems.reinforced_gold",
        "material.silentgems.reinforced_silver",
    },
}
EXTERNAL_DATA_KEYS = {"block.minecraft.barrier"}


def load_working(path: Path) -> dict[str, object]:
    """중복 키와 BOM을 거부하며 작업 JSON을 읽는다."""
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


def protected(value: object, pattern: re.Pattern[str]) -> Counter[str]:
    """값에 포함된 보호 문자열의 빈도를 센다."""
    return Counter(pattern.findall(value)) if isinstance(value, str) else Counter()


def validate_value(
    key: str, english: object, korean: object, errors: list[str]
) -> None:
    """자료형과 자리표시자·서식·숫자·줄바꿈을 비교한다."""
    if type(english) is not type(korean):
        errors.append(f"자료형 불일치: {key}")
        return
    if not isinstance(english, str):
        if english != korean:
            errors.append(f"비문자 값 변경: {key}")
        return
    for name, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식 코드", FORMAT_CODE),
        ("숫자", NUMBER),
    ):
        source = protected(english, pattern)
        target = protected(korean, pattern)
        if name == "숫자":
            if any(target[token] < count for token, count in source.items()):
                errors.append(f"{name} 불일치: {key}")
        elif source != target:
            errors.append(f"{name} 불일치: {key}")
    if english.count("\n") != korean.count("\n"):
        errors.append(f"줄바꿈 수 불일치: {key}")


def verify_target(
    instance: Path, target: Target, copy_output: bool
) -> dict[str, object]:
    """언어 네임스페이스 하나를 원문과 전수 대조한다."""
    jar_path = find_jar(instance, target)
    english_path = f"assets/{target.namespace}/lang/en_us.json"
    korean_path = f"assets/{target.namespace}/lang/ko_kr.json"
    with ZipFile(jar_path) as jar:
        english = load_json(jar, english_path)
        jar_korean = load_json(jar, korean_path)
        source_duplicates = duplicate_keys(jar, english_path)
    if source_duplicates:
        raise RuntimeError(f"영어 원문 중복 키: {target.namespace}:{source_duplicates}")
    korean = load_working(WORK_ROOT / target.namespace / "ko_kr.json")
    errors: list[str] = []
    extra = set(korean) - set(english)
    if list(korean)[: len(english)] != list(english) or extra != DATA_ONLY_KEYS.get(
        target.namespace, set()
    ):
        errors.append(
            f"키 집합 또는 순서 불일치: 누락={sorted(set(english) - set(korean))}, "
            f"초과={sorted(set(korean) - set(english))}"
        )
    for key, value in english.items():
        if key not in korean:
            continue
        validate_value(key, value, korean[key], errors)
        if value == korean[key] and key not in ALLOWED_IDENTICAL_KEYS:
            if not (
                key.startswith("grade.silentgear.")
                and value in {"A", "B", "C", "D", "E", "S", "SS", "SSS"}
            ):
                errors.append(f"분류되지 않은 영어 원문 유지: {key}")
    if errors:
        raise RuntimeError("\n".join(errors))
    if copy_output:
        output = OUTPUT_ROOT / target.namespace / "lang/ko_kr.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(WORK_ROOT / target.namespace / "ko_kr.json", output)
    source_overlap = set(english) & set(jar_korean)
    return {
        "namespace": target.namespace,
        "jar": jar_path.name,
        "english_keys": len(english),
        "jar_korean_overlap": len(source_overlap),
        "intentional_original": sum(english[key] == korean[key] for key in english),
        "status": "passed",
    }


def collect_translate_keys(value: object) -> set[str]:
    """JSON 값에서 translate 컴포넌트가 참조하는 키를 재귀적으로 모은다."""
    result: set[str] = set()
    if isinstance(value, dict):
        translate = value.get("translate")
        if isinstance(translate, str):
            result.add(translate)
        for child in value.values():
            result.update(collect_translate_keys(child))
    elif isinstance(value, list):
        for child in value:
            result.update(collect_translate_keys(child))
    return result


def verify_data_keys(
    instance: Path, translations: dict[str, object]
) -> dict[str, object]:
    """설치 JAR의 재료·특성 데이터가 쓰는 모든 번역 키를 확인한다."""
    scanned = 0
    keys: set[str] = set()
    literals: list[str] = []
    targets = (TARGETS[0], TARGETS[2], TARGETS[3])
    for target in targets:
        jar_path = find_jar(instance, target)
        with ZipFile(jar_path) as jar:
            for name in jar.namelist():
                if not name.endswith(".json") or not any(
                    part in name
                    for part in ("/silentgear_materials/", "/silentgear_traits/")
                ):
                    continue
                scanned += 1
                value = json.loads(jar.read(name).decode("utf-8-sig"))
                keys.update(collect_translate_keys(value))
                if isinstance(value, dict) and isinstance(value.get("text"), str):
                    literals.append(f"{jar_path.name}:{name}")
    missing = sorted(
        key for key in keys if key not in translations and key not in EXTERNAL_DATA_KEYS
    )
    if missing or literals:
        raise RuntimeError(
            f"동적 데이터 표시 경로 오류: 누락={missing}, JAR literal={literals}"
        )
    return {
        "data_json": scanned,
        "translate_keys": len(keys),
        "missing_keys": 0,
        "jar_literals": 0,
        "status": "passed",
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
    results = [verify_target(instance, target, args.copy_output) for target in selected]
    if args.batch == "all":
        translations: dict[str, object] = {}
        for target in TARGETS:
            translations.update(
                load_working(WORK_ROOT / target.namespace / "ko_kr.json")
            )
        results.append(verify_data_keys(instance, translations))
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
