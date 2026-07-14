#!/usr/bin/env python3
"""Allthemodium·ATM 장비 언어 파일의 구조와 보호 문자열을 검증하고 반영한다."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from atmgear_catalog import BATCHES, TARGETS, Target
from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_atmgear import WORK_ROOT, duplicate_keys, find_jar, load_json

OUTPUT_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?%?")
ALLOWED_IDENTICAL_KEYS = {
    "biome.allthemodium.the_beyond",
    "dimension.allthemodium.the_beyond",
    "material.allthemodium.allthemodium",
    "material.silentgear.allthemodium",
    "tetra.material.allthemodium",
    "material.allthemodium.vibranium",
    "material.silentgear.vibranium",
    "tetra.material.vibranium",
    "stat.tconstruct.harvest_tier.allthemodium.allthemodium",
    "stat.tconstruct.harvest_tier.allthemodium.vibranium",
    "stat.tconstruct.harvest_tier.allthemodium.unobtainium",
    "material.allthemodium.unobtainium",
    "material.silentgear.unobtainium",
    "tetra.material.unobtainium",
    "tab.allthearcanistgear.armor",
}


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
    """값에 포함된 보호 문자열 빈도를 센다."""
    return Counter(pattern.findall(value)) if isinstance(value, str) else Counter()


def verify_target(
    instance: Path, target: Target, copy_output: bool
) -> dict[str, object]:
    """언어 네임스페이스 하나를 영어 원문과 전수 대조한다."""
    jar_path = find_jar(instance, target)
    english_path = f"assets/{target.namespace}/lang/en_us.json"
    with ZipFile(jar_path) as jar:
        english = load_json(jar, english_path)
        source_duplicates = duplicate_keys(jar, english_path)
    if source_duplicates:
        raise RuntimeError(f"영어 원문 중복 키: {target.namespace}:{source_duplicates}")
    korean = load_working(WORK_ROOT / target.namespace / "ko_kr.json")
    errors: list[str] = []
    if list(korean) != list(english):
        errors.append(
            f"키 집합 또는 순서 불일치: 누락={sorted(set(english) - set(korean))}, "
            f"초과={sorted(set(korean) - set(english))}"
        )
    for key, source in english.items():
        target_value = korean.get(key)
        if type(source) is not type(target_value):
            errors.append(f"자료형 불일치: {key}")
            continue
        if isinstance(source, str):
            for name, pattern in (
                ("자리표시자", PLACEHOLDER),
                ("서식 코드", FORMAT_CODE),
            ):
                if protected(source, pattern) != protected(target_value, pattern):
                    errors.append(f"{name} 불일치: {key}")
            source_numbers = protected(source, NUMBER)
            target_numbers = protected(target_value, NUMBER)
            if any(
                target_numbers[token] < count for token, count in source_numbers.items()
            ):
                errors.append(f"숫자 불일치: {key}")
            if source.count("\n") != target_value.count("\n"):
                errors.append(f"줄바꿈 수 불일치: {key}")
            if source == target_value and key not in ALLOWED_IDENTICAL_KEYS:
                errors.append(f"분류되지 않은 영어 원문 유지: {key}")
        elif source != target_value:
            errors.append(f"비문자 값 변경: {key}")
    if errors:
        raise RuntimeError("\n".join(errors))
    if copy_output:
        output = OUTPUT_ROOT / target.namespace / "lang/ko_kr.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(WORK_ROOT / target.namespace / "ko_kr.json", output)
    return {
        "namespace": target.namespace,
        "jar": jar_path.name,
        "english_keys": len(english),
        "intentional_original": sum(english[key] == korean[key] for key in english),
        "status": "passed",
    }


def verify_cross_namespace() -> dict[str, object]:
    """Silent Gear와 ATM 로컬라이제이션의 공통 재료명 여섯 개를 대조한다."""
    allthemodium = load_working(WORK_ROOT / "allthemodium/ko_kr.json")
    atm_localization_path = (
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/atm10_localization/lang/ko_kr.json"
    )
    atm_localization = load_working(atm_localization_path)
    keys = sorted(key for key in allthemodium if key.startswith("material.silentgear."))
    errors = [
        key
        for key in keys
        if key not in atm_localization or allthemodium[key] != atm_localization[key]
    ]
    if errors:
        raise RuntimeError(f"Silent Gear 공통 재료명이 다릅니다: {errors}")
    return {"shared_material_keys": len(keys), "mismatches": 0, "status": "passed"}


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
    if args.batch == "all":
        rows.append(verify_cross_namespace())
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
