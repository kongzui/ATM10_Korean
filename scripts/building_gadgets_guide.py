#!/usr/bin/env python3
"""Building Gadgets 2 Patchouli 설명서를 준비하고 빌드·검증한다."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from five_family_goal import is_allowed_original
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

JAR_PREFIX = "buildinggadgets2-"
SOURCE_PREFIX = "assets/buildinggadgets2/patchouli_books/buildinggadgets2book/en_us/"
WORK_ROOT = PROJECT_ROOT / "working/early_midgame_infrastructure/buildinggadgets2_guide"
ENGLISH_ROOT = WORK_ROOT / "en_us"
KOREAN_ROOT = WORK_ROOT / "ko_kr"
OUTPUT_ROOT = (
    active_output_root() / "resourcepack/ATM10_Korean/assets/buildinggadgets2/"
    "patchouli_books/buildinggadgets2book/ko_kr"
)
TRANSLATIONS_FILE = WORK_ROOT / "translations.json"
LANG_ENGLISH = (
    PROJECT_ROOT / "working/early_midgame_infrastructure/buildinggadgets2/en_us.json"
)
LANG_KOREAN = (
    PROJECT_ROOT / "working/early_midgame_infrastructure/buildinggadgets2/ko_kr.json"
)
TRANSLATABLE_FIELDS = {"name", "description", "text", "title", "link_text"}
PATCHOULI_TOKEN = re.compile(r"\$\([^)]*\)")
NUMBER = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?%?")
URL = re.compile(r"https?://[^\s)]+")


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def find_jar() -> Path:
    mods = resolve_source_root() / "mods"
    matches = sorted(path for path in mods.glob(f"{JAR_PREFIX}*.jar") if path.is_file())
    if len(matches) != 1:
        raise RuntimeError(
            f"Building Gadgets 2 JAR을 하나로 확정할 수 없습니다: {matches}"
        )
    return matches[0]


def walk_strings(value: object, path: str = "") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if key in TRANSLATABLE_FIELDS and isinstance(child, str):
                rows.append((child_path, child))
            rows.extend(walk_strings(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(walk_strings(child, f"{path}[{index}]"))
    return rows


def set_path(value: object, path: str, replacement: str) -> None:
    tokens = re.findall(r"[^.\[\]]+|\d+(?=\])", path)
    current = value
    for token in tokens[:-1]:
        current = current[int(token)] if isinstance(current, list) else current[token]
    last = tokens[-1]
    if isinstance(current, list):
        current[int(last)] = replacement
    else:
        current[last] = replacement


def language_value_map() -> dict[str, str]:
    english = read_json(LANG_ENGLISH)
    korean = read_json(LANG_KOREAN)
    grouped: dict[str, set[str]] = {}
    for key, source in english.items():
        target = korean[key]
        if isinstance(source, str) and isinstance(target, str):
            grouped.setdefault(source, set()).add(target)
    return {
        source: next(iter(targets))
        for source, targets in grouped.items()
        if len(targets) == 1
    }


def prepare() -> int:
    for root in (ENGLISH_ROOT, KOREAN_ROOT):
        resolved = root.resolve()
        if WORK_ROOT.resolve() not in resolved.parents:
            raise RuntimeError(f"설명서 작업 경로가 범위를 벗어났습니다: {resolved}")
        if root.exists():
            shutil.rmtree(root)
    translations = read_json(TRANSLATIONS_FILE) if TRANSLATIONS_FILE.is_file() else {}
    value_map = language_value_map()
    sources: dict[str, str] = {}
    unresolved: list[str] = []
    files = 0

    with ZipFile(find_jar()) as jar:
        names = sorted(
            name
            for name in jar.namelist()
            if name.startswith(SOURCE_PREFIX) and name.endswith(".json")
        )
        for name in names:
            relative = name.removeprefix(SOURCE_PREFIX)
            source_data = json.loads(jar.read(name).decode("utf-8-sig"))
            target_data = json.loads(jar.read(name).decode("utf-8-sig"))
            for json_path, source in walk_strings(source_data):
                identity = f"{relative}|{json_path}"
                target = translations.get(identity, value_map.get(source))
                if target is not None:
                    set_path(target_data, json_path, target)
                    sources[identity] = (
                        "manual_translation"
                        if identity in translations
                        else "reviewed_language_name"
                    )
                elif is_allowed_original(source):
                    sources[identity] = "reviewed_original"
                else:
                    sources[identity] = "unresolved"
                    unresolved.append(identity)
            write_json(ENGLISH_ROOT / relative, source_data)
            write_json(KOREAN_ROOT / relative, target_data)
            files += 1

    report = {
        "files": files,
        "display_strings": len(sources),
        "sources": dict(sorted(sources.items())),
        "unresolved": unresolved,
    }
    write_json(WORK_ROOT / "candidate_sources.json", report)
    print(
        f"설명서 준비: {files}개 파일, {len(sources)}개 표시 문구, "
        f"미해결 {len(unresolved)}개"
    )
    return 1 if unresolved else 0


def build() -> int:
    resolved = OUTPUT_ROOT.resolve()
    output_base = (active_output_root() / "resourcepack").resolve()
    if output_base not in resolved.parents:
        raise RuntimeError(f"설명서 출력 경로가 범위를 벗어났습니다: {resolved}")
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    shutil.copytree(KOREAN_ROOT, OUTPUT_ROOT)
    files = len(list(OUTPUT_ROOT.rglob("*.json")))
    print(f"설명서 빌드: {files}개 파일")
    return 0


def verify_pair(source: str, target: str, identity: str) -> list[str]:
    errors: list[str] = []
    if source == target and not is_allowed_original(source):
        errors.append(f"미번역: {identity}")

    def token_signature(value: str) -> list[str]:
        signatures = []
        for token in PATCHOULI_TOKEN.findall(value):
            signatures.append("$(t:)" if token.startswith("$(t:") else token)
        return signatures

    checks = (
        ("Patchouli 토큰", token_signature(source), token_signature(target)),
        ("숫자", NUMBER.findall(source), NUMBER.findall(target)),
        ("URL", URL.findall(source), URL.findall(target)),
    )
    for label, source_values, target_values in checks:
        if Counter(source_values) != Counter(target_values):
            errors.append(f"{identity}: {label} 불일치")
    return errors


def verify() -> int:
    english_files = sorted(
        path.relative_to(ENGLISH_ROOT) for path in ENGLISH_ROOT.rglob("*.json")
    )
    korean_files = sorted(
        path.relative_to(KOREAN_ROOT) for path in KOREAN_ROOT.rglob("*.json")
    )
    output_files = sorted(
        path.relative_to(OUTPUT_ROOT) for path in OUTPUT_ROOT.rglob("*.json")
    )
    errors: list[str] = []
    if english_files != korean_files:
        errors.append("작업본 영어/한국어 파일 목록 불일치")
    if korean_files != output_files:
        errors.append("한국어 작업본/산출물 파일 목록 불일치")

    checked = 0
    for relative in english_files:
        english = read_json(ENGLISH_ROOT / relative)
        korean = read_json(KOREAN_ROOT / relative)
        output = read_json(OUTPUT_ROOT / relative)
        if korean != output:
            errors.append(f"산출물 불일치: {relative.as_posix()}")
        english_rows = dict(walk_strings(english))
        korean_rows = dict(walk_strings(korean))
        if english_rows.keys() != korean_rows.keys():
            errors.append(f"표시 필드 구조 불일치: {relative.as_posix()}")
            continue
        for json_path, source in english_rows.items():
            identity = f"{relative.as_posix()}|{json_path}"
            errors.extend(verify_pair(source, korean_rows[json_path], identity))
            checked += 1

    report = {
        "files": len(english_files),
        "display_strings": checked,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "validation.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "build", "verify"))
    args = parser.parse_args()
    if args.mode == "prepare":
        return prepare()
    if args.mode == "build":
        return build()
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())
