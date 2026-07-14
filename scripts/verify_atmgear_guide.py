#!/usr/bin/env python3
"""Allthemodium Patchouli 한국어 안내서의 구조와 보호 문자열을 검증한다."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from atmgear_catalog import TARGETS
from build_atmgear_guide import (
    BOOK_OUTPUT,
    BOOK_SOURCE,
    OUTPUT_ROOT,
    SOURCE_PREFIX,
    USER_FIELDS,
)
from local_paths import resolve_source_root
from prepare_atmgear import find_jar

PATCHOULI_TOKEN = re.compile(r"\$\([^)]+\)")
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?%?")
INTENTIONAL_ENGLISH = {"Discord", "Reddit"}


def load_json(path: Path) -> object:
    """BOM과 중복 키를 거부하며 JSON을 읽는다."""
    if path.read_bytes().startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"UTF-8 BOM이 있습니다: {path}")

    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"중복 키가 있습니다: {path}:{key}")
            result[key] = value
        return result

    return json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates
    )


def validate_string(label: str, source: str, translated: str) -> list[str]:
    """태그, 자리표시자, 숫자와 줄바꿈을 비교한다."""
    errors: list[str] = []
    for name, pattern in (
        ("Patchouli 태그", PATCHOULI_TOKEN),
        ("자리표시자", PLACEHOLDER),
        ("숫자", NUMBER),
    ):
        if Counter(pattern.findall(source)) != Counter(pattern.findall(translated)):
            errors.append(f"{label}: {name} 불일치")
    if source.count("\n") != translated.count("\n"):
        errors.append(f"{label}: 줄바꿈 수 불일치")
    if (
        source == translated
        and re.search(r"[A-Za-z]", source)
        and source not in INTENTIONAL_ENGLISH
    ):
        errors.append(f"{label}: 영어와 같은 미번역 값")
    return errors


def walk(source: object, translated: object, label: str, errors: list[str]) -> int:
    """표시 필드만 바뀌었는지 재귀적으로 확인한다."""
    if type(source) is not type(translated):
        errors.append(f"{label}: 자료형 불일치")
        return 0
    if isinstance(source, dict):
        if list(source) != list(translated):
            errors.append(f"{label}: 키 또는 순서 불일치")
            return 0
        count = 0
        for key in source:
            child = f"{label}.{key}"
            if key in USER_FIELDS and isinstance(source[key], str):
                count += 1
                errors.extend(validate_string(child, source[key], translated[key]))
            else:
                count += walk(source[key], translated[key], child, errors)
        return count
    if isinstance(source, list):
        if len(source) != len(translated):
            errors.append(f"{label}: 배열 길이 불일치")
            return 0
        return sum(
            walk(left, right, f"{label}[{index}]", errors)
            for index, (left, right) in enumerate(zip(source, translated, strict=True))
        )
    if source != translated:
        errors.append(f"{label}: 비번역 필드 변경")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    jar_path = find_jar(instance, TARGETS[0])
    errors: list[str] = []
    files = fields = 0
    with ZipFile(jar_path) as jar:
        names = sorted(
            name
            for name in jar.namelist()
            if name.startswith(SOURCE_PREFIX) and name.endswith(".json")
        )
        outputs = sorted(
            path.relative_to(OUTPUT_ROOT).as_posix()
            for path in OUTPUT_ROOT.rglob("*.json")
        )
        sources = sorted(name.removeprefix(SOURCE_PREFIX) for name in names)
        if sources != outputs:
            errors.append("안내서 파일 집합이 영어 원문과 다릅니다.")
        for name in names:
            relative = Path(name.removeprefix(SOURCE_PREFIX))
            source = json.loads(jar.read(name).decode("utf-8-sig"))
            translated = load_json(OUTPUT_ROOT / relative)
            fields += walk(source, translated, relative.as_posix(), errors)
            files += 1

        source_book = json.loads(jar.read(BOOK_SOURCE).decode("utf-8-sig"))
        translated_book = load_json(BOOK_OUTPUT)
        if list(source_book) != list(translated_book):
            errors.append("book.json 키 또는 순서 불일치")
        for key in source_book:
            if key == "landing_text":
                fields += 1
                errors.extend(
                    validate_string(
                        f"{BOOK_SOURCE}.{key}", source_book[key], translated_book[key]
                    )
                )
            elif source_book[key] != translated_book[key]:
                errors.append(f"{BOOK_SOURCE}.{key}: 비번역 필드 변경")

    if errors:
        raise RuntimeError("안내서 검증 실패:\n" + "\n".join(errors[:80]))
    print(
        json.dumps(
            {
                "guide_files": files,
                "book_metadata_overrides": 1,
                "translated_fields": fields,
                "validation": "passed",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
