#!/usr/bin/env python3
"""Actually Additions Patchouli·발전 과제·KubeJS 표시 경로를 조사하고 검증한다."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
from pathlib import Path, PurePosixPath
import zipfile

import ars_family
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root


WORK_ROOT = PROJECT_ROOT / "working/actually_additions/guide"
OUTPUT_ROOT = (
    active_output_root()
    / "resourcepack/ATM10_Korean/assets/actuallyadditions/patchouli_books/booklet/ko_kr"
)
BOOK_OUTPUT = (
    active_output_root()
    / "overrides/kubejs/data/actuallyadditions/patchouli_books/booklet/book.json"
)
BOOK_PREFIX = "assets/actuallyadditions/patchouli_books/booklet/en_us/"
BOOK_SOURCE = "data/actuallyadditions/patchouli_books/booklet/book.json"
ADVANCEMENT_PREFIX = "data/actuallyadditions/advancement/"
LANDING_TEXT = (
    "<i>솔직히 말하면 Actually Additions에 이렇게 콘텐츠가 많은 줄 저도 "
    "몰랐습니다.<r><n> - Ellpeck"
)
TRANSLATION_KEY = re.compile(r"^[a-z0-9_.-]+$")
VISIBLE_KEYS = {"name", "description", "title", "text", "link_text"}
VISIBLE_API = re.compile(
    r"displayName|tooltip|custom_name|Text\.of|literal|title|description",
    re.IGNORECASE,
)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def installed_jar() -> Path:
    mods = resolve_source_root() / "mods"
    matches = sorted(mods.glob("actuallyadditions-*.jar"))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Actually Additions JAR 개수가 1이 아닙니다: {matches}"
        )
    return matches[0]


def visible_values(value: object) -> list[str]:
    rows: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in VISIBLE_KEYS and isinstance(child, str) and child:
                rows.append(child)
            rows.extend(visible_values(child))
    elif isinstance(value, list):
        for child in value:
            rows.extend(visible_values(child))
    return rows


def advancement_translate_keys(value: object) -> list[str]:
    rows: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "translate" and isinstance(child, str):
                rows.append(child)
            rows.extend(advancement_translate_keys(child))
    elif isinstance(value, list):
        for child in value:
            rows.extend(advancement_translate_keys(child))
    return rows


def kubejs_audit(root: Path) -> dict[str, object]:
    kubejs = root / "kubejs"
    relevant: list[Path] = []
    for path in kubejs.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if (
            "actuallyadditions" in text.casefold()
            or "actually additions" in text.casefold()
        ):
            relevant.append(path)
    foreign_lang = [
        path
        for path in relevant
        if "assets/actuallyadditions/lang/" in path.as_posix().casefold()
    ]
    direct_visible: list[str] = []
    unrelated_visible: list[str] = []
    for path in relevant:
        if path in foreign_lang:
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        aa_lines = {
            index
            for index, line in enumerate(lines)
            if "actuallyadditions" in line.casefold()
            or "actually additions" in line.casefold()
        }
        for index, line in enumerate(lines):
            if not VISIBLE_API.search(line):
                continue
            row = f"{path.relative_to(kubejs).as_posix()}:{index + 1}"
            if any(abs(index - aa_index) <= 2 for aa_index in aa_lines):
                direct_visible.append(row)
            else:
                unrelated_visible.append(row)
    return {
        "reference_files": len(relevant),
        "non_language_reference_files": len(relevant) - len(foreign_lang),
        "foreign_language_files_excluded": len(foreign_lang),
        "direct_visible_literals": direct_visible,
        "unrelated_visible_literals_in_shared_files": unrelated_visible,
    }


def build() -> dict[str, object]:
    """현재 JAR의 가이드 구조를 복제하고 언어 키와 책 표지를 한국어용으로 준비한다."""
    jar = installed_jar()
    english_lang = ars_family.load_json(
        PROJECT_ROOT / "working/actually_additions/actuallyadditions/en_us.json"
    )
    korean_lang = ars_family.load_json(
        PROJECT_ROOT / "working/actually_additions/actuallyadditions/ko_kr.json"
    )
    guide_files: list[str] = []
    guide_values: list[str] = []
    advancement_rows: list[dict[str, object]] = []
    with zipfile.ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            if name.startswith(BOOK_PREFIX) and name.endswith(".json"):
                data = json.loads(archive.read(name).decode("utf-8"))
                relative = PurePosixPath(name.removeprefix(BOOK_PREFIX))
                work_en = WORK_ROOT / "en_us" / Path(*relative.parts)
                work_ko = WORK_ROOT / "ko_kr" / Path(*relative.parts)
                output = OUTPUT_ROOT / Path(*relative.parts)
                write_json(work_en, data)
                write_json(work_ko, data)
                write_json(output, data)
                guide_files.append(relative.as_posix())
                guide_values.extend(visible_values(data))
            elif name.startswith(ADVANCEMENT_PREFIX) and name.endswith(".json"):
                data = json.loads(archive.read(name).decode("utf-8"))
                display = data.get("display") if isinstance(data, dict) else None
                advancement_rows.append(
                    {
                        "path": name,
                        "has_display": isinstance(display, dict),
                        "translation_keys": advancement_translate_keys(display),
                        "literal_display": (
                            isinstance(display, dict)
                            and not advancement_translate_keys(display)
                        ),
                    }
                )
        book = json.loads(archive.read(BOOK_SOURCE).decode("utf-8"))
    book["name"] = "item.actuallyadditions.booklet"
    book["landing_text"] = LANDING_TEXT
    write_json(WORK_ROOT / "book.json", book)
    write_json(BOOK_OUTPUT, book)
    write_json(WORK_ROOT / "advancements.json", advancement_rows)
    missing_guide_keys = sorted(
        {
            value
            for value in guide_values
            if TRANSLATION_KEY.fullmatch(value)
            and (value not in english_lang or value not in korean_lang)
        }
    )
    kubejs = kubejs_audit(resolve_source_root())
    report = {
        "jar": jar.name,
        "guide_files": len(guide_files),
        "guide_visible_values": len(guide_values),
        "guide_translation_keys": sum(
            1 for value in guide_values if TRANSLATION_KEY.fullmatch(value)
        ),
        "missing_guide_translation_keys": missing_guide_keys,
        "book_name_key": book["name"],
        "book_landing_text_translated": True,
        "advancements": len(advancement_rows),
        "advancements_with_display": sum(
            row["has_display"] for row in advancement_rows
        ),
        "advancements_with_literal_display": sum(
            row["literal_display"] for row in advancement_rows
        ),
        "kubejs": kubejs,
    }
    write_json(WORK_ROOT / "audit.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    """가이드 구조·언어 키·책 표지·발전 과제 표시 경로를 검증한다."""
    english_lang = ars_family.load_json(
        PROJECT_ROOT / "working/actually_additions/actuallyadditions/en_us.json"
    )
    korean_lang = ars_family.load_json(
        PROJECT_ROOT / "working/actually_additions/actuallyadditions/ko_kr.json"
    )
    errors: list[str] = []
    files = sorted((WORK_ROOT / "en_us").rglob("*.json"))
    visible_count = 0
    for source_file in files:
        relative = source_file.relative_to(WORK_ROOT / "en_us")
        target_file = WORK_ROOT / "ko_kr" / relative
        output_file = OUTPUT_ROOT / relative
        if not target_file.is_file() or not output_file.is_file():
            errors.append(f"가이드 파일 누락: {relative.as_posix()}")
            continue
        source = json.loads(source_file.read_text(encoding="utf-8"))
        target = json.loads(target_file.read_text(encoding="utf-8"))
        output = json.loads(output_file.read_text(encoding="utf-8"))
        if source != target or target != output:
            errors.append(f"가이드 구조 불일치: {relative.as_posix()}")
        for value in visible_values(source):
            visible_count += 1
            if TRANSLATION_KEY.fullmatch(value):
                if value not in english_lang or value not in korean_lang:
                    errors.append(f"가이드 번역 키 누락: {value}")
                elif english_lang[value] == korean_lang[value]:
                    errors.append(f"가이드 연결 키 미번역: {value}")
    book = json.loads(BOOK_OUTPUT.read_text(encoding="utf-8"))
    if book.get("name") != "item.actuallyadditions.booklet":
        errors.append("책 이름 키가 유효한 언어 키가 아닙니다.")
    if book.get("landing_text") != LANDING_TEXT:
        errors.append("책 첫 화면 번역이 다릅니다.")
    source_tags = Counter(re.findall(r"<[^>]+>", LANDING_TEXT))
    if source_tags != Counter({"<i>": 1, "<r>": 1, "<n>": 1}):
        errors.append("책 첫 화면 태그가 다릅니다.")
    advancements = json.loads(
        (WORK_ROOT / "advancements.json").read_text(encoding="utf-8")
    )
    for row in advancements:
        for key in row["translation_keys"]:
            if key not in english_lang or key not in korean_lang:
                errors.append(f"발전 과제 번역 키 누락: {key}")
            elif english_lang[key] == korean_lang[key]:
                errors.append(f"발전 과제 번역 키 미번역: {key}")
        if row["literal_display"]:
            errors.append(f"발전 과제 리터럴 표시 발견: {row['path']}")
    audit = json.loads((WORK_ROOT / "audit.json").read_text(encoding="utf-8"))
    if audit["kubejs"]["direct_visible_literals"]:
        errors.append("KubeJS의 Actually Additions 직접 표시 리터럴이 남았습니다.")
    report = {
        "guide_files": len(files),
        "guide_visible_values": visible_count,
        "advancements": len(advancements),
        "advancements_with_display": sum(row["has_display"] for row in advancements),
        "kubejs_reference_files": audit["kubejs"]["reference_files"],
        "kubejs_direct_visible_literals": len(
            audit["kubejs"]["direct_visible_literals"]
        ),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "validation.json", report)
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    args = parser.parse_args()
    if args.command == "build":
        report = build()
        status = 0
    else:
        report, status = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
