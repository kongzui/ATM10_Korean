#!/usr/bin/env python3
"""Moog's 구조물 시리즈의 언어·구조물 표시 문구를 번역하고 검증해요."""

from __future__ import annotations

import argparse
import gzip
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from dungeons_arise_family import (
    VISIBLE_DATA_KEYS,
    VISIBLE_NBT_LIST_NAMES,
    VISIBLE_NBT_STRING_NAMES,
    component_literal_text,
    nbt_component_literal,
    replace_component_literal,
    scan_visible_nbt,
    walk_json,
)
from gateways_hellish_family import Tag, read_nbt, write_nbt
from local_paths import PROJECT_ROOT, resolve_source_root

FAMILY = "moogs_structures"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
RESOURCEPACK_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean"
OVERRIDE_ROOT = PROJECT_ROOT / "output/overrides/kubejs"
REVIEWED_TEXT = WORK_ROOT / "reviewed_text.json"
SUNZI_TRANSLATION = WORK_ROOT / "sunzi_ko_kr.json"
JARS = {
    "common": ("moogs_structures-neoforge-*.jar", None),
    "mes": ("MoogsEndStructures*.jar", "mes"),
    "mns": ("MoogsNetherStructures*.jar", "mns"),
    "mss": ("MoogsSoaringStructures*.jar", "mss"),
    "mvs": ("MoogsVoyagerStructures*.jar", "mvs"),
}
SUNZI_FILE = "data/mvs/structure/sunzi_gate.nbt"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[./xX×+]\d+)*")
HAN_SCRIPT = re.compile(r"[\u3400-\u9fff]")
BOOK_LINE_WIDTH = 114
BOOK_MAX_LINES = 14
BOOK_MAX_PAGES = 100


def find_jar(label: str) -> Path:
    """현재 설치본에서 지정한 JAR 하나를 찾아요."""
    pattern = JARS[label][0]
    matches = sorted((resolve_source_root() / "mods").glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"{label} JAR이 정확히 한 개가 아니에요: {matches}")
    return matches[0]


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없는 JSON을 안정된 형식으로 기록해요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_json(path: Path) -> object:
    """UTF-8 JSON 파일을 읽어요."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_reviewed() -> (
    tuple[dict[str, str], dict[str, dict[str, str]], dict[str, set[str]]]
):
    """검수된 언어·NBT 번역표와 보존 목록을 읽어요."""
    value = load_json(REVIEWED_TEXT)
    if not isinstance(value, dict):
        raise TypeError("검수 번역표가 객체가 아니에요")
    language = {
        str(row["source"]): str(row["target"]) for row in value["language_values"]
    }
    nbt = {
        namespace: {
            str(row["source"]): str(row["target"])
            for row in value["nbt_values"].get(namespace, [])
        }
        for namespace in ("mes", "mns", "mss", "mvs")
    }
    preserved = {
        namespace: set(value["preserved_nbt_values"].get(namespace, []))
        for namespace in ("mes", "mns", "mss", "mvs")
    }
    return language, nbt, preserved


def read_language(label: str, locale: str) -> dict[str, str]:
    """지정한 모듈 JAR의 언어 파일을 읽어요."""
    namespace = JARS[label][1]
    if namespace is None:
        return {}
    internal = f"assets/{namespace}/lang/{locale}.json"
    with ZipFile(find_jar(label)) as archive:
        try:
            value = json.loads(archive.read(internal))
        except KeyError:
            return {}
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise TypeError(f"언어 파일 형식이 올바르지 않아요: {internal}")
    return value


def prepare() -> dict[str, object]:
    """다섯 JAR의 언어·데이터·NBT 표시 표면을 전부 추출해요."""
    reports = []
    errors = []
    for label, (_, namespace) in JARS.items():
        jar = find_jar(label)
        language_files = []
        english = {}
        bundled_korean = {}
        invalid_json = []
        data_json_files = []
        data_direct = []
        data_localized = []
        nbt_files = []
        nbt_rows = []
        guide_candidates = []
        with ZipFile(jar) as archive:
            for name in sorted(archive.namelist()):
                lower = name.lower()
                if "/lang/" in lower and lower.endswith(".json"):
                    language_files.append(name)
                if namespace and name == f"assets/{namespace}/lang/en_us.json":
                    english = json.loads(archive.read(name))
                if namespace and name == f"assets/{namespace}/lang/ko_kr.json":
                    bundled_korean = json.loads(archive.read(name))
                if lower.endswith((".md", ".txt", ".json")) and any(
                    part in lower
                    for part in ("/book/", "/guide/", "/manual/", "patchouli")
                ):
                    guide_candidates.append(name)
                if lower.startswith("data/") and lower.endswith(".json"):
                    data_json_files.append(name)
                    try:
                        value = json.loads(archive.read(name))
                    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                        invalid_json.append(f"{name}: {exc}")
                        continue
                    for key, path, child in walk_json(value):
                        if key not in VISIBLE_DATA_KEYS:
                            continue
                        row = {"file": name, "path": path, "value": child}
                        if isinstance(child, dict) and isinstance(
                            child.get("translate"), str
                        ):
                            data_localized.append(row)
                        else:
                            literal = component_literal_text(child)
                            if literal and literal.strip():
                                data_direct.append({**row, "literal": literal})
                if not lower.endswith(".nbt"):
                    continue
                nbt_files.append(name)
                value = archive.read(name)
                try:
                    raw = gzip.decompress(value)
                except gzip.BadGzipFile:
                    raw = value
                for row in scan_visible_nbt(raw):
                    nbt_rows.append({"file": name, **row})
        current_errors = []
        expected_language = (
            {f"assets/{namespace}/lang/en_us.json"} if namespace else set()
        )
        unexpected_language = sorted(set(language_files) - expected_language)
        missing_language = sorted(expected_language - set(language_files))
        if unexpected_language or missing_language:
            current_errors.append(
                "언어 파일 목록이 달라요: "
                f"missing={missing_language}, unexpected={unexpected_language}"
            )
        if invalid_json:
            current_errors.append(f"읽지 못한 데이터 JSON이 있어요: {invalid_json}")
        if guide_candidates:
            current_errors.append(f"별도 가이드 후보가 있어요: {guide_candidates}")
        errors.extend(f"{label}: {message}" for message in current_errors)
        report = {
            "label": label,
            "namespace": namespace,
            "jar": jar.name,
            "jar_size": jar.stat().st_size,
            "jar_mtime_ns": jar.stat().st_mtime_ns,
            "language_files": language_files,
            "english_language": english,
            "bundled_korean": bundled_korean,
            "data_json_files": len(data_json_files),
            "data_direct_fields": data_direct,
            "data_localized_fields": data_localized,
            "invalid_json": invalid_json,
            "nbt_files": len(nbt_files),
            "nbt_visible_fields": nbt_rows,
            "guide_candidates": guide_candidates,
            "errors": current_errors,
        }
        reports.append(report)
        if namespace:
            write_json(WORK_ROOT / namespace / "en_us.json", english)
            write_json(WORK_ROOT / namespace / "bundled_ko_kr.json", bundled_korean)
    catalog = {
        "family": FAMILY,
        "jars": reports,
        "errors": errors,
        "status": "prepared" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "source_surface_catalog.json", catalog)
    summary = {
        "family": FAMILY,
        "jars": [
            {
                "label": row["label"],
                "jar": row["jar"],
                "language_keys": len(row["english_language"]),
                "bundled_korean_keys": len(row["bundled_korean"]),
                "data_json_files": row["data_json_files"],
                "data_direct_fields": len(row["data_direct_fields"]),
                "data_localized_fields": len(row["data_localized_fields"]),
                "nbt_files": row["nbt_files"],
                "nbt_visible_fields": len(row["nbt_visible_fields"]),
            }
            for row in reports
        ],
        "errors": errors,
        "status": catalog["status"],
    }
    write_json(WORK_ROOT / "inventory.json", summary)
    return summary


def book_character_width(character: str) -> int:
    """기본 글꼴에서 책 줄바꿈을 보수적으로 어림잡아요."""
    if character == " ":
        return 4
    if ord(character) < 128:
        return 6
    return 9


def book_line_count(text: str) -> int:
    """책의 114픽셀 폭을 기준으로 예상 줄 수를 계산해요."""
    lines = 1
    width = 0
    for character in text:
        if character == "\n":
            lines += 1
            width = 0
            continue
        character_width = book_character_width(character)
        if width and width + character_width > BOOK_LINE_WIDTH:
            lines += 1
            width = 0
        width += character_width
    return lines


def split_book_page(text: str) -> list[str]:
    """한국어 본문을 문장 경계에서 최대 14줄짜리 페이지로 나눠요."""
    pages = []
    remaining = text
    while remaining and book_line_count(remaining) > BOOK_MAX_LINES:
        best = 0
        for index in range(1, len(remaining) + 1):
            if book_line_count(remaining[:index]) <= BOOK_MAX_LINES:
                best = index
            else:
                break
        candidates = [
            index
            for index in range(max(1, best - 48), best + 1)
            if remaining[index - 1] in ".!?다요임음됨함\n;；。"
        ]
        if not candidates:
            candidates = [
                index
                for index in range(max(1, best - 48), best + 1)
                if remaining[index - 1].isspace()
            ]
        cut = candidates[-1] if candidates else best
        while cut < len(remaining) and remaining[cut] == " ":
            cut += 1
        pages.append(remaining[:cut])
        remaining = remaining[cut:]
    if remaining or not pages:
        pages.append(remaining)
    return pages


def translated_book_pages() -> list[str]:
    """47쪽 검수본을 읽기 좋은 페이지로 나눠 반환해요."""
    reviewed = load_json(SUNZI_TRANSLATION)
    if not isinstance(reviewed, list) or not all(
        isinstance(page, str) for page in reviewed
    ):
        raise TypeError("손자병법 검수본이 문자열 배열이 아니에요")
    if len(reviewed) != 47:
        raise ValueError(f"손자병법 검수본이 47쪽이 아니에요: {len(reviewed)}")
    pages = [piece for page in reviewed for piece in split_book_page(page)]
    if len(pages) > BOOK_MAX_PAGES:
        raise ValueError(f"손자병법 출력이 100쪽을 넘어요: {len(pages)}")
    if any(book_line_count(page) > BOOK_MAX_LINES for page in pages):
        raise ValueError("손자병법 출력에 14줄을 넘는 페이지가 있어요")
    return pages


def translate_written_book(content: Tag, source_pages: list[str]) -> int:
    """손자병법 47쪽과 제목을 검수한 한국어 책으로 바꿔요."""
    if content.kind != 10:
        raise TypeError("written_book_content가 컴파운드 태그가 아니에요")
    pages_tag = content.value.get("pages")
    title_tag = content.value.get("title")
    if not isinstance(pages_tag, Tag) or pages_tag.kind != 9:
        raise TypeError("손자병법 pages 태그가 목록이 아니에요")
    child_kind, page_tags = pages_tag.value
    if child_kind != 10:
        raise TypeError("손자병법 페이지가 컴파운드 목록이 아니에요")
    actual_pages = []
    for page in page_tags:
        raw = page.value.get("raw") if page.kind == 10 else None
        if not isinstance(raw, Tag) or raw.kind != 8:
            raise TypeError("손자병법 페이지 raw 태그를 읽지 못했어요")
        actual_pages.append(nbt_component_literal(str(raw.value)))
    if actual_pages != source_pages:
        raise ValueError("손자병법 현재 페이지 원문이 추출 당시와 달라요")
    target_pages = translated_book_pages()
    pages_tag.value = (
        10,
        [
            Tag(10, {"raw": Tag(8, json.dumps(page, ensure_ascii=False))})
            for page in target_pages
        ],
    )
    if not isinstance(title_tag, Tag) or title_tag.kind != 10:
        raise TypeError("손자병법 제목 태그가 컴파운드가 아니에요")
    raw_title = title_tag.value.get("raw")
    if not isinstance(raw_title, Tag) or raw_title.kind != 8:
        raise TypeError("손자병법 제목 raw 태그를 읽지 못했어요")
    if str(raw_title.value) != "The Art of War":
        raise ValueError("손자병법 현재 제목이 달라요")
    raw_title.value = "손자병법"
    return len(source_pages) + 1


def transform_nbt_tag(
    tag: Tag,
    namespace: str,
    mapping: dict[str, str],
    source_pages: list[str],
    name: str | None = None,
) -> int:
    """표시 경로의 검수된 값과 Voyager의 책만 번역해요."""
    count = 0
    if tag.kind == 8 and name in VISIBLE_NBT_STRING_NAMES:
        source = str(tag.value)
        literal = nbt_component_literal(source)
        if literal in mapping:
            tag.value = replace_component_literal(source, mapping[literal])
            return 1
    if tag.kind == 10:
        if namespace == "mvs":
            written = tag.value.get("minecraft:written_book_content")
            if isinstance(written, Tag):
                count += translate_written_book(written, source_pages)
        for child_name, child in tag.value.items():
            count += transform_nbt_tag(
                child, namespace, mapping, source_pages, child_name
            )
    elif tag.kind == 9:
        child_kind, children = tag.value
        if child_kind == 8 and name in VISIBLE_NBT_LIST_NAMES:
            for child in children:
                source = str(child.value)
                literal = nbt_component_literal(source)
                if literal in mapping:
                    child.value = replace_component_literal(source, mapping[literal])
                    count += 1
        else:
            for child in children:
                count += transform_nbt_tag(
                    child, namespace, mapping, source_pages, name
                )
    return count


def source_book_pages(catalog: dict[str, object]) -> list[str]:
    """추출 목록에서 손자병법 47쪽 원문을 순서대로 반환해요."""
    rows = [
        row
        for row in catalog["nbt_visible_fields"]
        if row["file"] == SUNZI_FILE and "/pages/" in row["path"]
    ]
    rows.sort(key=lambda row: int(row["path"].split("/pages/")[1].split("/")[0]))
    pages = [row["literal"] for row in rows]
    if len(pages) != 47:
        raise ValueError(f"손자병법 원문 페이지가 47쪽이 아니에요: {len(pages)}")
    return pages


def assert_current_jar(row: dict[str, object]) -> None:
    """원문 추출 뒤 JAR이 바뀌지 않았는지 확인해요."""
    jar = find_jar(str(row["label"]))
    if (
        row["jar"] != jar.name
        or row["jar_size"] != jar.stat().st_size
        or row["jar_mtime_ns"] != jar.stat().st_mtime_ns
    ):
        raise RuntimeError(f"{row['label']} JAR이 원문 추출 당시와 달라요")


def build() -> dict[str, object]:
    """언어 파일 네 개와 번역이 필요한 구조물 NBT를 만들어요."""
    catalog = load_json(WORK_ROOT / "source_surface_catalog.json")
    if not isinstance(catalog, dict):
        raise TypeError("원문 목록이 객체가 아니에요")
    by_label = {row["label"]: row for row in catalog["jars"]}
    for row in by_label.values():
        assert_current_jar(row)
    language_map, nbt_maps, preserved = load_reviewed()
    all_language_values = {
        source
        for label in ("mes", "mns", "mss", "mvs")
        for source in by_label[label]["english_language"].values()
    }
    if all_language_values != set(language_map):
        raise KeyError(
            "언어 번역표 원문이 달라요: "
            f"missing={sorted(all_language_values - set(language_map))}, "
            f"extra={sorted(set(language_map) - all_language_values)}"
        )
    language_reports = []
    for label in ("mes", "mns", "mss", "mvs"):
        english = by_label[label]["english_language"]
        target = {key: language_map[value] for key, value in english.items()}
        work = WORK_ROOT / label / "ko_kr.json"
        output = RESOURCEPACK_ROOT / f"assets/{label}/lang/ko_kr.json"
        write_json(work, target)
        write_json(output, target)
        language_reports.append(
            {
                "namespace": label,
                "keys": len(target),
                "output": output.relative_to(PROJECT_ROOT).as_posix(),
            }
        )
    source_pages = source_book_pages(by_label["mvs"])
    sunzi_values = set(source_pages) | {"The Art of War"}
    for namespace in ("mes", "mns", "mss", "mvs"):
        actual = {row["literal"] for row in by_label[namespace]["nbt_visible_fields"]}
        expected = set(nbt_maps[namespace]) | preserved[namespace]
        if namespace == "mvs":
            expected |= sunzi_values
        if actual != expected:
            raise KeyError(
                f"{namespace} NBT 표시 원문이 달라요: "
                f"missing={sorted(actual - expected)}, extra={sorted(expected - actual)}"
            )
    nbt_reports = []
    for namespace in ("mes", "mns", "mss", "mvs"):
        rows = by_label[namespace]["nbt_visible_fields"]
        translatable_files = {
            row["file"]
            for row in rows
            if row["literal"] in nbt_maps[namespace]
            or (namespace == "mvs" and row["file"] == SUNZI_FILE)
        }
        with ZipFile(find_jar(namespace)) as archive:
            for internal in sorted(translatable_files):
                source_bytes = archive.read(internal)
                compressed = source_bytes.startswith(b"\x1f\x8b")
                raw = gzip.decompress(source_bytes) if compressed else source_bytes
                root_name, root = read_nbt(raw)
                replacements = transform_nbt_tag(
                    root, namespace, nbt_maps[namespace], source_pages
                )
                if not replacements:
                    raise RuntimeError(f"번역할 값이 없는 NBT가 선택됐어요: {internal}")
                target_raw = write_nbt(root_name, root)
                output = OVERRIDE_ROOT / internal
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(
                    gzip.compress(target_raw, mtime=0) if compressed else target_raw
                )
                nbt_reports.append(
                    {
                        "namespace": namespace,
                        "source": internal,
                        "output": output.relative_to(PROJECT_ROOT).as_posix(),
                        "source_visible_replacements": replacements,
                    }
                )
    write_json(WORK_ROOT / "translated_language_files.json", language_reports)
    write_json(WORK_ROOT / "translated_nbt_files.json", nbt_reports)
    replacement_count = sum(row["source_visible_replacements"] for row in nbt_reports)
    report = {
        "family": FAMILY,
        "reviewed_language_keys": sum(row["keys"] for row in language_reports),
        "bundled_korean_candidate_keys": sum(
            len(by_label[label]["bundled_korean"])
            for label in ("mes", "mns", "mss", "mvs")
        ),
        "existing_korean_values_reused": 0,
        "new_language_values": sum(row["keys"] for row in language_reports),
        "translated_nbt_source_fields": replacement_count,
        "translated_nbt_files": len(nbt_reports),
        "sunzi_source_pages": len(source_pages),
        "sunzi_output_pages": len(translated_book_pages()),
        "errors": [],
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def preserved_errors(label: str, source: str, target: str) -> list[str]:
    """자리표시자·서식·숫자·줄바꿈을 보존했는지 확인해요."""
    errors = []
    for name, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식 코드", FORMAT_CODE),
        ("숫자", NUMBER),
    ):
        source_values = Counter(pattern.findall(source))
        target_values = Counter(pattern.findall(target))
        if source_values != target_values:
            errors.append(
                f"{label} {name} 불일치: {dict(source_values)} != {dict(target_values)}"
            )
    if source.count("\n") != target.count("\n"):
        errors.append(f"{label} 실제 줄바꿈 수가 달라요")
    if source.count("\\n") != target.count("\\n"):
        errors.append(f"{label} 이스케이프 줄바꿈 수가 달라요")
    return errors


def audit_references() -> tuple[dict[str, object], list[str]]:
    """FTB Quests와 KubeJS의 관련 참조 및 직접 표시 후보를 확인해요."""
    instance = resolve_source_root()
    errors = []
    report: dict[str, object] = {"ftbquests": [], "kubejs": [], "read_errors": []}
    suffixes = {".cfg", ".js", ".json", ".snbt", ".toml", ".txt"}
    namespaces = {"mes", "mns", "mss", "mvs"}
    for label, base in (
        ("ftbquests", instance / "config/ftbquests/quests"),
        ("kubejs", instance / "kubejs"),
    ):
        rows = report[label]
        if not isinstance(rows, list) or not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                report["read_errors"].append(f"{path}: {exc}")
                continue
            counts = {
                namespace: text.lower().count(f"{namespace}:")
                for namespace in namespaces
            }
            if not any(counts.values()):
                continue
            visible_lines = []
            for number, line in enumerate(text.splitlines(), 1):
                if not any(f"{namespace}:" in line.lower() for namespace in namespaces):
                    continue
                if re.search(
                    r"(?i)(?:custom_name|displayname|display_name|lore|subtitle|title|tooltip)"
                    r"\s*[:=(]",
                    line,
                ):
                    visible_lines.append(number)
            row = {
                "path": path.relative_to(instance).as_posix(),
                "namespace_occurrences": counts,
                "visible_namespace_candidate_lines": visible_lines,
            }
            rows.append(row)
            if visible_lines:
                errors.append(f"{label}에 직접 표시 문구 후보가 있어요: {row}")
    errors.extend(str(message) for message in report["read_errors"])
    return report, errors


def audit() -> tuple[dict[str, object], list[str]]:
    """현재 원문 목록과 별도 표시 경로를 감사해요."""
    catalog = load_json(WORK_ROOT / "source_surface_catalog.json")
    by_label = {row["label"]: row for row in catalog["jars"]}
    errors = []
    for row in by_label.values():
        try:
            assert_current_jar(row)
        except RuntimeError as exc:
            errors.append(str(exc))
        if row["invalid_json"] or row["guide_candidates"]:
            errors.append(f"{row['label']} 데이터 또는 가이드 감사를 완료하지 못했어요")
        if row["data_direct_fields"]:
            errors.append(f"{row['label']}에 직접 데이터 표시 문구가 있어요")
    references, reference_errors = audit_references()
    errors.extend(reference_errors)
    report = {
        "family": FAMILY,
        "source_catalog": {
            label: {
                "language_keys": len(row["english_language"]),
                "data_localized_fields": len(row["data_localized_fields"]),
                "data_direct_fields": len(row["data_direct_fields"]),
                "nbt_visible_fields": len(row["nbt_visible_fields"]),
            }
            for label, row in by_label.items()
        },
        "references": references,
        "ftbquests_display_work": (
            "no_related_references"
            if not references["ftbquests"]
            else "namespace_ids_only"
        ),
        "kubejs_display_work": (
            "no_related_references"
            if not references["kubejs"]
            else "namespace_ids_only"
        ),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def verify_language() -> tuple[dict[str, object], list[str]]:
    """현재 영어 28키와 네 한국어 산출물을 전부 검증해요."""
    language_map, _, _ = load_reviewed()
    errors = []
    reviewed = 0
    same_keys = []
    for label in ("mes", "mns", "mss", "mvs"):
        english = read_language(label, "en_us")
        expected = {key: language_map[source] for key, source in english.items()}
        work = load_json(WORK_ROOT / label / "ko_kr.json")
        output = load_json(RESOURCEPACK_ROOT / f"assets/{label}/lang/ko_kr.json")
        if work != expected or output != expected:
            errors.append(f"{label} 작업본·산출물·확정 번역이 서로 달라요")
        if list(work) != list(english) or list(output) != list(english):
            errors.append(f"{label} 언어 키 또는 순서가 영어 원문과 달라요")
        for key, source in english.items():
            target = expected[key]
            errors.extend(preserved_errors(f"{label}:{key}", source, target))
            if source == target:
                same_keys.append(f"{label}:{key}")
            elif not re.search(r"[가-힣]", target):
                errors.append(f"{label}:{key} 번역에 한국어가 없어요")
        reviewed += len(english)
    report = {
        "reviewed_english_keys": reviewed,
        "output_keys": reviewed,
        "bundled_korean_candidate_keys": 0,
        "existing_korean_values_reused": 0,
        "new_language_values": reviewed,
        "intentional_same_keys": sorted(same_keys),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify_book_translation(source_pages: list[str]) -> list[str]:
    """손자병법 검수본의 순서·줄바꿈·출력 페이지 안전성을 검사해요."""
    errors = []
    reviewed = load_json(SUNZI_TRANSLATION)
    if len(reviewed) != len(source_pages):
        return ["손자병법 원문과 검수본 페이지 수가 달라요"]
    for index, (source, target) in enumerate(zip(source_pages, reviewed, strict=True)):
        if source.count("\n") != target.count("\n"):
            errors.append(f"손자병법 원문 {index}쪽의 줄바꿈 수가 달라요")
    output_pages = translated_book_pages()
    if len(output_pages) > BOOK_MAX_PAGES:
        errors.append(f"손자병법 출력이 100쪽을 넘어요: {len(output_pages)}")
    if any(book_line_count(page) > BOOK_MAX_LINES for page in output_pages):
        errors.append("손자병법 출력에 14줄을 넘는 페이지가 있어요")
    if "".join(output_pages) != "".join(reviewed):
        errors.append("손자병법 페이지 분할 과정에서 본문이 바뀌었어요")
    allowed_han = set("始計作戰謀攻軍形兵勢虛實軍爭九變行地火用間")
    remaining_han = sorted(set(HAN_SCRIPT.findall("".join(reviewed))) - allowed_han)
    if remaining_han:
        errors.append(f"손자병법 한국어 검수본에 한문 본문이 남았어요: {remaining_han}")
    return errors


def transform_source_nbt(
    namespace: str,
    internal: str,
    source_bytes: bytes,
    mapping: dict[str, str],
    source_pages: list[str],
) -> tuple[str, Tag, int]:
    """원본 NBT에 확정 변환을 적용해 예상 태그를 만들어요."""
    compressed = source_bytes.startswith(b"\x1f\x8b")
    raw = gzip.decompress(source_bytes) if compressed else source_bytes
    root_name, root = read_nbt(raw)
    replacements = transform_nbt_tag(root, namespace, mapping, source_pages)
    if not replacements:
        raise RuntimeError(f"번역할 표시 문구가 없어요: {internal}")
    return root_name, root, replacements


def verify_nbt_outputs() -> tuple[dict[str, object], list[str]]:
    """모든 NBT 산출물을 원본에 대한 확정 변환과 비교해요."""
    catalog = load_json(WORK_ROOT / "source_surface_catalog.json")
    by_label = {row["label"]: row for row in catalog["jars"]}
    _, nbt_maps, _ = load_reviewed()
    source_pages = source_book_pages(by_label["mvs"])
    rows = load_json(WORK_ROOT / "translated_nbt_files.json")
    errors = verify_book_translation(source_pages)
    replacements = 0
    for row in rows:
        namespace = row["namespace"]
        with ZipFile(find_jar(namespace)) as archive:
            source_bytes = archive.read(row["source"])
        try:
            expected_name, expected_root, count = transform_source_nbt(
                namespace,
                row["source"],
                source_bytes,
                nbt_maps[namespace],
                source_pages,
            )
            output_bytes = (PROJECT_ROOT / row["output"]).read_bytes()
            output_raw = (
                gzip.decompress(output_bytes)
                if output_bytes.startswith(b"\x1f\x8b")
                else output_bytes
            )
            actual_name, actual_root = read_nbt(output_raw)
        except (EOFError, OSError, TypeError, ValueError) as exc:
            errors.append(
                f"NBT 산출물을 읽거나 변환하지 못했어요: {row['output']}: {exc}"
            )
            continue
        if actual_name != expected_name or actual_root != expected_root:
            errors.append(f"NBT 산출물이 확정 변환과 달라요: {row['output']}")
        if count != row["source_visible_replacements"]:
            errors.append(f"NBT 번역 수가 기록과 달라요: {row['output']}")
        replacements += count
    if replacements != 257:
        errors.append(f"NBT 원문 표시 필드 번역 수가 달라요: {replacements} != 257")
    expected_outputs = {row["output"] for row in rows}
    actual_outputs = {
        path.relative_to(PROJECT_ROOT).as_posix()
        for namespace in ("mes", "mns", "mss", "mvs")
        for path in (OVERRIDE_ROOT / f"data/{namespace}").rglob("*.nbt")
    }
    if actual_outputs != expected_outputs:
        errors.append(
            "Moog's NBT 산출물 목록이 달라요: "
            f"missing={sorted(expected_outputs - actual_outputs)}, "
            f"extra={sorted(actual_outputs - expected_outputs)}"
        )
    report = {
        "files": len(rows),
        "translated_source_visible_fields": replacements,
        "sunzi_source_pages": len(source_pages),
        "sunzi_output_pages": len(translated_book_pages()),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def deployment_paths() -> set[str]:
    """이 패밀리가 실제 인스턴스에 적용할 정확한 상대 경로를 반환해요."""
    paths = {
        f"resourcepacks/ATM10_Korean/assets/{namespace}/lang/ko_kr.json"
        for namespace in ("mes", "mns", "mss", "mvs")
    }
    manifest = WORK_ROOT / "translated_nbt_files.json"
    if manifest.is_file():
        paths.update(
            row["output"].removeprefix("output/overrides/")
            for row in load_json(manifest)
        )
    return paths


def verify() -> tuple[dict[str, object], list[str]]:
    """언어·NBT·별도 표시 경로와 적용 기록을 모두 검증해요."""
    language, language_errors = verify_language()
    nbt, nbt_errors = verify_nbt_outputs()
    surface, surface_errors = audit()
    errors = language_errors + nbt_errors + surface_errors
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = load_json(deployment_path) if deployment_path.is_file() else None
    report = {
        "family": FAMILY,
        "language": language,
        "nbt": nbt,
        "surface_audit": surface["status"],
        "ftbquests": surface["ftbquests_display_work"],
        "kubejs": surface["kubejs_display_work"],
        "output_files": len(deployment_paths()),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    completion = {
        "family": FAMILY,
        "reviewed_language_keys": language["reviewed_english_keys"],
        "bundled_korean_candidate_keys": 0,
        "existing_korean_values_reused": 0,
        "new_language_values": language["new_language_values"],
        "translated_nbt_source_fields": nbt["translated_source_visible_fields"],
        "sunzi_source_pages": nbt["sunzi_source_pages"],
        "sunzi_output_pages": nbt["sunzi_output_pages"],
        "ftbquests_work": surface["ftbquests_display_work"],
        "kubejs_work": surface["kubejs_display_work"],
        "output_files": sorted(deployment_paths()),
        "deployment": deployment,
        "errors": errors,
        "status": (
            "complete"
            if not errors
            and (
                deployment is None or deployment.get("status") == "applied_and_verified"
            )
            else "incomplete"
        ),
    }
    write_json(WORK_ROOT / "family_completion.json", completion)
    return report, errors


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 매니페스트의 대상·백업·해시 결과를 작업 기록에 연결해요."""
    manifest_path = manifest_path.resolve()
    manifest = load_json(manifest_path)
    errors = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 매니페스트 상태가 완료가 아니에요")
    if manifest.get("java_processes"):
        errors.append(
            f"적용 당시 Java 프로세스가 있었어요: {manifest['java_processes']}"
        )
    expected = deployment_paths()
    targets = manifest.get("targets", [])
    if not isinstance(targets, list) or not targets:
        errors.append("적용 대상 기록이 없어요")
        targets = []
    summaries = []
    for target in targets:
        records = {
            row.get("relative_path"): row
            for row in target.get("files", [])
            if isinstance(row, dict)
        }
        missing = sorted(expected - set(records))
        extra = sorted(set(records) - expected)
        if missing or extra:
            errors.append(f"적용 경로가 달라요: missing={missing}, extra={extra}")
        hash_errors = sorted(
            path
            for path in expected & set(records)
            if records[path].get("source_sha256") != records[path].get("after_sha256")
        )
        if hash_errors:
            errors.append(f"적용 후 해시가 달라요: {hash_errors}")
        if target.get("unexpected_changes"):
            errors.append(f"예상 밖 적용 변경이 있어요: {target['unexpected_changes']}")
        summaries.append(
            {
                "target_type": target.get("target_type"),
                "target_root": target.get("target_root"),
                "changed_paths": target.get("changed_paths", []),
                "unexpected_changes": target.get("unexpected_changes", []),
                "hash_verified_paths": sorted(expected - set(hash_errors)),
            }
        )
    try:
        manifest_name = manifest_path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        manifest_name = str(manifest_path)
    report = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "backup_manifest": manifest_name,
        "expected_paths": sorted(expected),
        "targets": summaries,
        "errors": errors,
    }
    write_json(WORK_ROOT / "deployment_report.json", report)
    return report, errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "build", "audit", "verify", "record-deployment"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare()
    elif args.command == "build":
        result = build()
    elif args.command == "audit":
        result, _ = audit()
    elif args.command == "verify":
        result, _ = verify()
    else:
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        result, _ = record_deployment(args.manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return (
        0 if result["status"] in {"prepared", "complete", "applied_and_verified"} else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
