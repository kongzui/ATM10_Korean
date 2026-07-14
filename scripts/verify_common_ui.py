#!/usr/bin/env python3
"""공통 UI 언어 파일의 구조와 보호 문자열을 검증하고 산출물에 반영한다."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from zipfile import ZipFile

from common_ui_catalog import GROUPS, TARGETS, Target
from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_common_ui import WORK_ROOT, find_jar, load_json

OUTPUT_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{\d+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")


def protected(value: object, pattern: re.Pattern[str]) -> list[str]:
    return pattern.findall(value) if isinstance(value, str) else []


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
                if type(english[key]) is not type(korean[key]):
                    errors.append(f"자료형 불일치: {key}")
                    continue
                if protected(english[key], PLACEHOLDER) != protected(
                    korean[key], PLACEHOLDER
                ):
                    errors.append(f"자리표시자 불일치: {key}")
                if protected(english[key], FORMAT_CODE) != protected(
                    korean[key], FORMAT_CODE
                ):
                    errors.append(f"서식 코드 불일치: {key}")
                if isinstance(english[key], str) and english[key].count("\n") != korean[
                    key
                ].count("\n"):
                    errors.append(f"줄바꿈 수 불일치: {key}")
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
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
