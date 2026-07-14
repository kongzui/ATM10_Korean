#!/usr/bin/env python3
"""Sophisticated 계열 언어 파일의 구조와 보호 문자열을 검증하고 반영한다."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_sophisticated import WORK_ROOT, find_jar, load_json
from sophisticated_catalog import BATCHES, TARGETS, Target

OUTPUT_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
ALLOWED_IDENTICAL_KEYS = {
    "itemGroup.sophisticatedcore",
    "item.sophisticatedcore.storage.tooltip.energy",
    "item.sophisticatedcore.storage.tooltip.fluid",
    "key.category.sophisticatedcore.main",
    "itemGroup.sophisticatedbackpacks",
    "key.category.sophisticatedbackpacks.main",
    "gui.sophisticatedbackpacks.upgrades.refill.target_slot.any",
    "gui.sophisticatedbackpacks.upgrades.refill.target_slot.main_hand",
    "gui.sophisticatedbackpacks.upgrades.refill.target_slot.off_hand",
}


def protected(value: object, pattern: re.Pattern[str]) -> list[str]:
    return pattern.findall(value) if isinstance(value, str) else []


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
        if protected(english, PLACEHOLDER) != protected(korean, PLACEHOLDER):
            errors.append(f"자리표시자 불일치: {key}")
        if protected(english, FORMAT_CODE) != protected(korean, FORMAT_CODE):
            errors.append(f"서식 코드 불일치: {key}")
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
    if target.namespace is None:
        with ZipFile(jar_path) as jar:
            language_files = [
                name
                for name in jar.namelist()
                if re.fullmatch(r"assets/[^/]+/lang/(?:en_us|ko_kr)\.json", name)
            ]
        if language_files:
            raise RuntimeError(
                f"언어 파일 없음으로 분류한 JAR에 대상 파일이 있습니다: {jar_path.name}"
            )
        return {
            "batch": target.batch,
            "jar": jar_path.name,
            "namespace": None,
            "validation": "언어 파일 없음 확인",
        }

    with ZipFile(jar_path) as jar:
        english = load_json(jar, f"assets/{target.namespace}/lang/en_us.json")
        candidate = load_json(jar, f"assets/{target.namespace}/lang/ko_kr.json")
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
        if key not in ALLOWED_IDENTICAL_KEYS
        and isinstance(value, str)
        and value == english.get(key)
        and re.search(r"[A-Za-z]", value)
    ]
    if untranslated:
        errors.append(f"영어와 같은 미번역 값: {untranslated}")
    bad_upgrade = [
        key
        for key, value in korean.items()
        if isinstance(value, str)
        and "Upgrade" in str(english.get(key, ""))
        and "업그레이드" not in value
    ]
    if bad_upgrade:
        errors.append(f"Upgrade 용어 불일치: {bad_upgrade}")
    if errors:
        raise RuntimeError(f"{target.namespace} 검증 실패:\n" + "\n".join(errors[:30]))

    output = OUTPUT_ROOT / target.namespace / "lang/ko_kr.json"
    if copy_output:
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(working_path, output)
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
