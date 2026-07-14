#!/usr/bin/env python3
"""그림자의 연대기 한국어 JSON 구조와 보호 문자열을 검증하고 반영한다."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_apotheosis import find_jar
from prepare_apotheosis_guide import CORE_TARGET, SOURCE_PREFIX, WORK_ROOT

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/apotheosis/patchouli_books/apoth_chronicle/ko_kr"
)
TRANSLATABLE_FIELDS = {"name", "description", "title", "text"}
PATCHOULI_TOKEN = re.compile(r"\$\([^)]+\)")
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?%?")


def load_json(path: Path) -> object:
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


def validate_pair(label: str, source: str, translated: str) -> list[str]:
    errors = []
    for name, pattern in (
        ("Patchouli 태그", PATCHOULI_TOKEN),
        ("자리표시자", PLACEHOLDER),
        ("숫자", NUMBER),
    ):
        if Counter(pattern.findall(source)) != Counter(pattern.findall(translated)):
            errors.append(f"{label}: {name} 불일치")
    if source.count("\n") != translated.count("\n"):
        errors.append(f"{label}: 줄바꿈 수 불일치")
    return errors


def walk(source: object, translated: object, label: str, errors: list[str]) -> int:
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
            if key in TRANSLATABLE_FIELDS and isinstance(source[key], str):
                count += 1
                errors.extend(validate_pair(child, source[key], translated[key]))
                if source[key] == translated[key] and re.search(
                    r"[A-Za-z]", source[key]
                ):
                    errors.append(f"{child}: 영어와 같은 미번역 값")
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
    parser.add_argument("--copy-output", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    jar_path = find_jar(instance, CORE_TARGET)
    errors: list[str] = []
    files = strings = 0
    with ZipFile(jar_path) as jar:
        names = sorted(
            name
            for name in jar.namelist()
            if name.startswith(SOURCE_PREFIX) and name.endswith(".json")
        )
        working_files = sorted(
            path.relative_to(WORK_ROOT).as_posix() for path in WORK_ROOT.rglob("*.json")
        )
        source_files = sorted(name.removeprefix(SOURCE_PREFIX) for name in names)
        if working_files != source_files:
            raise ValueError("가이드 파일 집합이 영어 원문과 다릅니다.")
        for name in names:
            relative = Path(name.removeprefix(SOURCE_PREFIX))
            source = json.loads(jar.read(name).decode("utf-8-sig"))
            translated = load_json(WORK_ROOT / relative)
            strings += walk(source, translated, relative.as_posix(), errors)
            files += 1
    if errors:
        raise RuntimeError("가이드 검증 실패:\n" + "\n".join(errors[:80]))
    if args.copy_output:
        shutil.copytree(WORK_ROOT, OUTPUT_ROOT, dirs_exist_ok=True)
    print(
        json.dumps(
            {
                "guide_files": files,
                "translated_fields": strings,
                "validation": "passed",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
