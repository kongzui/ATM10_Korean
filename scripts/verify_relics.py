#!/usr/bin/env python3
"""Relics·Artifacts 계열 언어 파일의 구조와 보호 문자열을 검증하고 반영한다."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_relics import WORK_ROOT, duplicate_keys, find_jar, load_json
from relics_catalog import BATCHES, TARGETS, Target
from version_context import active_output_root

OUTPUT_ROOT = active_output_root() / "resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?%?")
ALLOWED_IDENTICAL_VALUES = {
    "Artifacts",
    "Relics",
    "Reliquified Artifacts",
    "Curios",
    "Mimic",
    "Mimic!",
    "Steve",
}
ALLOWED_IDENTICAL_KEYS: set[str] = set()
ALLOWED_IDENTICAL_KEYS.update(
    {
        "artifacts.tooltip.plus_mob_effect",
        "artifacts.tooltip.plus_mob_effect_chance",
        "relics.message.rider_flute.slot",
    }
)


def protected(value: object, pattern: re.Pattern[str]) -> Counter[str]:
    """한 값에서 검증해야 할 보호 문자열을 센다."""
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
    """자료형과 자리표시자·서식·숫자·줄바꿈을 비교한다."""
    if type(english) is not type(korean):
        errors.append(f"자료형 불일치: {key}")
        return
    if isinstance(english, str):
        for name, pattern in (
            ("자리표시자", PLACEHOLDER),
            ("서식 코드", FORMAT_CODE),
            ("숫자", NUMBER),
        ):
            english_parts = protected(english, pattern)
            korean_parts = protected(korean, pattern)
            if name == "숫자":
                if any(
                    korean_parts[token] < count
                    for token, count in english_parts.items()
                ):
                    errors.append(f"{name} 불일치: {key}")
            elif english_parts != korean_parts:
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
    """한 네임스페이스를 원문과 전수 대조하고 선택적으로 출력에 복사한다."""
    jar_path = find_jar(instance, target)
    english_path = f"assets/{target.namespace}/lang/en_us.json"
    korean_path = f"assets/{target.namespace}/lang/ko_kr.json"
    with ZipFile(jar_path) as jar:
        english = load_json(jar, english_path)
        candidate = load_json(jar, korean_path)
        english_duplicates = duplicate_keys(jar, english_path)
    if english_duplicates:
        raise RuntimeError(
            f"영어 표시 키에 중복이 있습니다: {target.namespace}:{english_duplicates}"
        )
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
    ]
    if untranslated:
        errors.append(f"영어와 같은 미분류 값: {untranslated}")
    if errors:
        raise RuntimeError(f"{target.namespace} 검증 실패:\n" + "\n".join(errors[:60]))

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
