#!/usr/bin/env python3
"""공통 UI 언어 파일의 구조와 보호 문자열을 검증하고 산출물에 반영한다."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from zipfile import ZipFile

from common_ui_catalog import (
    GROUPS,
    PACK_LANGUAGE_TARGETS,
    TARGETS,
    PackLanguageTarget,
    Target,
)
from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_common_ui import WORK_ROOT, find_jar, load_json

OUTPUT_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")


def protected(value: object, pattern: re.Pattern[str]) -> list[str]:
    return pattern.findall(value) if isinstance(value, str) else []


def validate_value(
    key: str,
    english: object,
    korean: object,
    errors: list[str],
    path: str = "",
    translatable: bool = True,
) -> None:
    """중첩 텍스트 컴포넌트까지 자료형과 보호 문자열을 검증한다."""
    location = f"{key}{path}"
    if type(english) is not type(korean):
        errors.append(f"자료형 불일치: {location}")
        return
    if isinstance(english, str):
        if not translatable and english != korean:
            errors.append(f"비번역 필드 변경: {location}")
        if protected(english, PLACEHOLDER) != protected(korean, PLACEHOLDER):
            errors.append(f"자리표시자 불일치: {location}")
        if protected(english, FORMAT_CODE) != protected(korean, FORMAT_CODE):
            errors.append(f"서식 코드 불일치: {location}")
        if english.count("\n") != korean.count("\n"):
            errors.append(f"줄바꿈 수 불일치: {location}")
        return
    if isinstance(english, list):
        if len(english) != len(korean):
            errors.append(f"목록 길이 불일치: {location}")
            return
        for index, (english_item, korean_item) in enumerate(zip(english, korean)):
            validate_value(
                key,
                english_item,
                korean_item,
                errors,
                f"{path}[{index}]",
                translatable,
            )
        return
    if isinstance(english, dict):
        if list(english) != list(korean):
            errors.append(f"객체 키 또는 순서 불일치: {location}")
            return
        for field in english:
            validate_value(
                key,
                english[field],
                korean[field],
                errors,
                f"{path}.{field}",
                field == "text",
            )
        return
    if english != korean:
        errors.append(f"비문자 값 변경: {location}")


def verify_target(
    instance: Path, target: Target, copy_output: bool
) -> list[dict[str, object]]:
    jar_path = find_jar(instance, target)
    rows = []
    with ZipFile(jar_path) as jar:
        for namespace in target.namespaces:
            english = load_json(jar, f"assets/{namespace}/lang/en_us.json")
            if target.key_prefixes:
                english = {
                    key: value
                    for key, value in english.items()
                    if key.startswith(target.key_prefixes)
                }
            working = WORK_ROOT / target.group / namespace / "ko_kr.json"
            korean = json.loads(working.read_text(encoding="utf-8"))
            errors = []
            if list(korean) != list(english):
                missing = sorted(set(english) - set(korean))
                extra = sorted(set(korean) - set(english))
                errors.append(f"키 또는 순서 불일치: 누락={missing}, 초과={extra}")
            for key in english.keys() & korean.keys():
                validate_value(key, english[key], korean[key], errors)
            if working.read_bytes().startswith(b"\xef\xbb\xbf"):
                errors.append("UTF-8 BOM이 있습니다")
            if errors:
                raise RuntimeError(f"{namespace} 검증 실패:\n" + "\n".join(errors[:30]))
            output = OUTPUT_ROOT / namespace / "lang/ko_kr.json"
            if copy_output:
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(working, output)
            rows.append(
                {
                    "group": target.group,
                    "jar": jar_path.name,
                    "namespace": namespace,
                    "keys": len(english),
                    "output": output.relative_to(PROJECT_ROOT).as_posix(),
                    "validation": "passed",
                }
            )
    return rows


def verify_pack_target(
    instance: Path, target: PackLanguageTarget, copy_output: bool
) -> dict[str, object]:
    """팩의 KubeJS 언어 파일도 JAR 언어 파일과 같은 기준으로 검증한다."""
    english_path = instance / target.relative_dir / "en_us.json"
    english = json.loads(english_path.read_text(encoding="utf-8-sig"))
    working = WORK_ROOT / target.group / target.namespace / "ko_kr.json"
    korean = json.loads(working.read_text(encoding="utf-8"))
    errors = []
    if list(korean) != list(english):
        missing = sorted(set(english) - set(korean))
        extra = sorted(set(korean) - set(english))
        errors.append(f"키 또는 순서 불일치: 누락={missing}, 초과={extra}")
    for key in english.keys() & korean.keys():
        validate_value(key, english[key], korean[key], errors)
    if working.read_bytes().startswith(b"\xef\xbb\xbf"):
        errors.append("UTF-8 BOM이 있습니다")
    if errors:
        raise RuntimeError(f"{target.namespace} 검증 실패:\n" + "\n".join(errors[:30]))
    output = OUTPUT_ROOT / target.namespace / "lang/ko_kr.json"
    if copy_output:
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(working, output)
    return {
        "group": target.group,
        "source": target.relative_dir,
        "namespace": target.namespace,
        "keys": len(english),
        "output": output.relative_to(PROJECT_ROOT).as_posix(),
        "validation": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("group", choices=GROUPS + ("all",))
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--copy-output", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    selected = [
        target
        for target in TARGETS
        if args.group == "all" or target.group == args.group
    ]
    rows = []
    for target in selected:
        rows.extend(verify_target(instance, target, args.copy_output))
    pack_selected = [
        target
        for target in PACK_LANGUAGE_TARGETS
        if args.group == "all" or target.group == args.group
    ]
    for target in pack_selected:
        rows.append(verify_pack_target(instance, target, args.copy_output))
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
