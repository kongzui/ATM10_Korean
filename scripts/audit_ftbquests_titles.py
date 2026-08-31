#!/usr/bin/env python3
"""FTB Quests 제목과 자동 fallback 표시 경로를 감사해 JSON/CSV로 기록한다."""

from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import build_ae2_quests as lang_snbt
import ftbquests_title_rules as title_rules
import rebase_ftbquests
from local_paths import resolve_source_root
from version_context import active_report_dir
from version_context import active_output_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_LANG = active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr"
REPORT_JSON = active_report_dir() / "ftbquests_title_audit.json"
REPORT_CSV = active_report_dir() / "ftbquests_title_audit.csv"
FORMAT_RE = re.compile(r"&[0-9a-fklmnor]", re.IGNORECASE)
LATIN_WORD_RE = re.compile(r"[A-Za-z]{3,}")
STRING_RE = re.compile(r'"((?:\\.|[^"\\])*)"')

GENERAL_GROUP_TITLES = {
    "Magic": "마법",
    "Tools and Gear": "도구 및 장비",
    "Storage": "저장소",
    "Main Questline": "주요 퀘스트라인",
    "Tools and Weapons": "도구 및 무기",
    "Tech": "기술",
    "Logistics": "물류",
    "Power": "전력",
    "Exploration": "탐험",
    "Resources": "자원",
}

GENERAL_CHAPTER_TITLES = {
    "Food and Farming": "음식과 농사",
    "Steam Age: New Beginnings": "증기 시대: 새로운 시작",
    "Tips and Tricks": "팁과 요령",
    "Basic Storage": "기본 저장소",
    "Bounty Board": "현상금 게시판",
    "End Game": "최종 단계",
    "The Electric Age": "전기 시대",
    "Basic Logistics": "기본 물류",
    "Getting Started": "시작하기",
    "Basic Armor": "기본 방어구",
    "Implosion Power": "내파 전력",
    "Basic Tools": "기본 도구",
    "Digital Age": "디지털 시대",
    "Welcome": "환영합니다",
    "Electric Age: No more rookie": "전기 시대: 초보 탈출",
    "Basic Power": "기본 전력",
    "Generators N Furnaces": "발전기 및 화로",
    "Building Tips": "건축 팁",
}

MIXED_CHAPTER_TITLES = {
    "Apotheosis Gear": "Apotheosis 장비",
    "Cataclysm": "L_Ender's Cataclysm",
    "Forbidden \\& Arcanus": "Forbidden Arcanus",
    "Forbidden & Arcanus": "Forbidden Arcanus",
    "Mekanism: Reactors": "Mekanism: 원자로",
    "PneumaticCraft": "PneumaticCraft: Repressurized",
    "RailCraft": "Railcraft Reborn",
    "Extended \\& Advanced AE": "Extended AE 및 Advanced AE",
    "Extended & Advanced AE": "Extended AE 및 Advanced AE",
}

GENERAL_STYLED_TITLES = {
    "&aChapter 1&r: &bThe Beginning": "&a1장&r: &b시작",
    "&aChapter 2&r: &6The ATM Star": "&a2장&r: &6ATM Star",
    "&aChapter 2&r: &eAllthemodium": "&a2장&r: &eAllthemodium",
    "&aChapter 3&r: &6The ATM Star": "&a3장&r: &6ATM Star",
    "&aChapter 4&r: &dCreative": "&a4장&r: &d크리에이티브",
}

OFFICIAL_TITLE_EXEMPTIONS = {
    "AE2",
    "Allthemodium",
    "Applied Energistics 2",
    "Apothic Enchanting",
    "ATM Star",
    "Chisel Reborn",
    "Deorum",
    "Forbidden \\& Arcanus",
    "Garmonbozia",
    "Integrated Dynamics",
    "LaserIO",
    "LPG",
    "Luminax",
    "Macaw's Windows",
    "Mekanism",
    "MEGA Cells",
    "Productive Metalworks",
    "XyCraft",
    "Xeovrenth Adjure",
    "Eziveus' Spectral Compulsion",
}


def decode_snbt_string(raw: str) -> str:
    """JSON에 없는 SNBT 이스케이프를 보존 가능한 문자로 풀어낸다."""
    raw = re.sub(r"\\([^\"\\/bfnrtu])", r"\1", raw)
    return json.loads(f'"{raw}"')


def strip_formatting(value: str) -> str:
    return FORMAT_RE.sub("", value).strip()


def find_matching(text: str, start: int, opening: str, closing: str) -> int:
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index
    raise ValueError(f"닫는 {closing}를 찾지 못했습니다: {start}")


def skip_quoted_string(text: str, start: int) -> int:
    escaped = False
    for index in range(start + 1, len(text)):
        if escaped:
            escaped = False
        elif text[index] == "\\":
            escaped = True
        elif text[index] == '"':
            return index + 1
    raise ValueError(f"문자열의 닫는 따옴표를 찾지 못했습니다: {start}")


def list_objects(text: str, key: str) -> list[str]:
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*\[", text)
    if not match:
        return []
    start = text.find("[", match.start())
    end = find_matching(text, start, "[", "]")
    body = text[start + 1 : end]
    objects: list[str] = []
    index = 0
    while index < len(body):
        if body[index] == '"':
            index = skip_quoted_string(body, index)
        elif body[index] == "{":
            object_end = find_matching(body, index, "{", "}")
            objects.append(body[index : object_end + 1])
            index = object_end + 1
        else:
            index += 1
    return objects


def top_level_lines(block: str) -> list[str]:
    lines: list[str] = []
    curly = 0
    square = 0
    quoted = False
    escaped = False
    line_start = 0
    for index, char in enumerate(block):
        if index == line_start and curly == 1 and square == 0:
            line_end = block.find("\n", index)
            lines.append(block[index : line_end if line_end >= 0 else len(block)])
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "{":
            curly += 1
        elif char == "}":
            curly -= 1
        elif char == "[":
            square += 1
        elif char == "]":
            square -= 1
        if char == "\n":
            line_start = index + 1
    return lines


def scalar_string(block: str, key: str) -> str:
    for line in top_level_lines(block):
        match = re.match(rf"\s*{re.escape(key)}:\s*\"((?:\\.|[^\"\\])*)\"", line)
        if match:
            return decode_snbt_string(match.group(1))
    return ""


def item_data(task: str) -> tuple[str, str]:
    match = re.search(r"(?m)^\s*item:\s*\{", task)
    if not match:
        return "", ""
    start = task.find("{", match.start())
    end = find_matching(task, start, "{", "}")
    item = task[start : end + 1]
    ids = re.findall(r'\bid:\s*"([a-z0-9_.-]+:[a-z0-9_./-]+)"', item)
    item_id = ids[-1] if ids else ""
    custom_match = re.search(
        r'"minecraft:custom_name"\s*:\s*("(?:\\.|[^"\\])*"|\{.*?\})',
        item,
        re.DOTALL,
    )
    custom_name = custom_match.group(1) if custom_match else ""
    if custom_name.startswith('"'):
        custom_name = decode_snbt_string(custom_name[1:-1])
    return item_id, custom_name


def parse_chapters(quest_root: Path) -> tuple[list[dict[str, Any]], set[str]]:
    chapters: list[dict[str, Any]] = []
    object_ids: set[str] = set()
    for path in sorted((quest_root / "chapters").glob("*.snbt")):
        text = path.read_text(encoding="utf-8-sig")
        chapter_id = re.search(r'(?m)^\tid:\s*"([0-9A-F]{16})"', text)
        group_id = re.search(r'(?m)^\tgroup:\s*"([0-9A-F]{16})"', text)
        if not chapter_id:
            raise ValueError(f"챕터 ID를 찾지 못했습니다: {path}")
        chapter: dict[str, Any] = {
            "id": chapter_id.group(1),
            "group_id": group_id.group(1) if group_id else "",
            "filename": path.name,
            "quests": [],
        }
        object_ids.add(chapter["id"])
        for quest_block in list_objects(text, "quests"):
            quest_id = scalar_string(quest_block, "id")
            if not quest_id:
                raise ValueError(f"Quest ID를 찾지 못했습니다: {path}")
            quest: dict[str, Any] = {"id": quest_id, "tasks": []}
            object_ids.add(quest_id)
            for task_block in list_objects(quest_block, "tasks"):
                task_id = scalar_string(task_block, "id")
                task_type = scalar_string(task_block, "type")
                item_id, custom_name = item_data(task_block)
                if not task_id:
                    raise ValueError(f"Task ID를 찾지 못했습니다: {path}:{quest_id}")
                object_ids.add(task_id)
                quest["tasks"].append(
                    {
                        "id": task_id,
                        "type": task_type,
                        "item_id": item_id,
                        "custom_name": custom_name,
                    }
                )
            chapter["quests"].append(quest)
        chapters.append(chapter)
    return chapters, object_ids


def load_project_languages() -> tuple[dict[str, str], dict[str, str]]:
    english: dict[str, str] = {}
    korean: dict[str, str] = {}
    root = active_output_root() / "resourcepack/ATM10_Korean/assets"
    for path in root.glob("*/lang/ko_kr.json"):
        values = json.loads(path.read_text(encoding="utf-8"))
        korean.update(
            {key: value for key, value in values.items() if isinstance(value, str)}
        )
    return english, korean


def load_installed_item_languages(
    instance: Path, item_ids: set[str]
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    candidates: dict[str, list[str]] = {}
    wanted: set[str] = set()
    for item_id in item_ids:
        namespace, path = item_id.split(":", 1)
        keys = [f"item.{namespace}.{path}", f"block.{namespace}.{path}"]
        candidates[item_id] = keys
        wanted.update(keys)
    english: dict[str, str] = {}
    korean: dict[str, str] = {}
    errors: list[str] = []
    for jar in sorted((instance / "mods").glob("*.jar")):
        try:
            with zipfile.ZipFile(jar) as archive:
                for name in archive.namelist():
                    match = re.fullmatch(r"assets/[^/]+/lang/(en_us|ko_kr)\.json", name)
                    if not match:
                        continue
                    try:
                        values = json.loads(archive.read(name).decode("utf-8-sig"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as error:
                        errors.append(f"{jar.name}:{name}:{error}")
                        continue
                    target = english if match.group(1) == "en_us" else korean
                    for key in wanted & values.keys():
                        if isinstance(values[key], str):
                            target.setdefault(key, values[key])
        except zipfile.BadZipFile as error:
            errors.append(f"{jar.name}:{error}")
    resolved_keys: dict[str, str] = {}
    for item_id, keys in candidates.items():
        resolved_keys[item_id] = next((key for key in keys if key in english), "")
    return english, korean, resolved_keys


def text_value(values: dict[str, lang_snbt.TranslationValue], key: str) -> str:
    value = values.get(key, "")
    return "\n".join(value) if isinstance(value, list) else value


def load_output_language(root: Path) -> dict[str, lang_snbt.TranslationValue]:
    """현재 버전의 분할 FTB Quests 산출물을 중복 없이 읽는다."""
    values: dict[str, lang_snbt.TranslationValue] = {}
    key_files: dict[str, Path] = {}
    for path in sorted(root.rglob("*.snbt"), key=lambda item: item.as_posix().lower()):
        for key, value in lang_snbt.parse_language_snbt(path).items():
            if key in values:
                raise ValueError(
                    f"출력 키가 여러 파일에 있습니다: {key} "
                    f"({key_files[key]}, {path})"
                )
            values[key] = value
            key_files[key] = path
    if not values:
        raise FileNotFoundError(f"분할 FTB Quests 출력이 없습니다: {root}")
    return values


def canonical_navigation(source: str, kind: str) -> str:
    if kind == "group":
        return GENERAL_GROUP_TITLES.get(source, source)
    return (
        GENERAL_CHAPTER_TITLES.get(source)
        or MIXED_CHAPTER_TITLES.get(source)
        or GENERAL_STYLED_TITLES.get(source)
        or source
    )


def looks_untranslated(value: str) -> bool:
    plain = strip_formatting(value).replace("\\", "")
    if "Forbidden" in plain and "Arcanus" in plain:
        return False
    if plain in OFFICIAL_TITLE_EXEMPTIONS:
        return False
    return bool(LATIN_WORD_RE.search(plain)) and not re.search(r"[가-힣]", plain)


def add_issue(issues: list[dict[str, str]], **values: str) -> None:
    row = {
        "kind": "",
        "object_id": "",
        "chapter_id": "",
        "chapter_file": "",
        "source_value": "",
        "current_korean": "",
        "fallback_value": "",
        "item_id": "",
        "resourcepack_translation": "",
        "problem_type": "",
        "applied_fix": "",
    }
    row.update(values)
    issues.append(row)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    quest_root = instance / "config/ftbquests/quests"
    english, _ = rebase_ftbquests.load_split(instance, "en_us")
    current = load_output_language(OUTPUT_LANG)
    baseline, _ = rebase_ftbquests.load_split(instance, "ko_kr")
    omitted_keys = set(
        json.loads(rebase_ftbquests.OMITTED_KEYS.read_text(encoding="utf-8"))
    )
    chapters, object_ids = parse_chapters(quest_root)
    group_ids = set(
        re.findall(r"[0-9A-F]{16}", (quest_root / "chapter_groups.snbt").read_text())
    )
    object_ids.update(group_ids)

    item_ids = {
        task["item_id"]
        for chapter in chapters
        for quest in chapter["quests"]
        for task in quest["tasks"]
        if task["item_id"] and task["item_id"] != "ftbfiltersystem:smart_filter"
    }
    installed_en, installed_ko, item_keys = load_installed_item_languages(
        instance, item_ids
    )
    _, project_ko = load_project_languages()
    issues: list[dict[str, str]] = []
    object_context: dict[str, dict[str, str]] = {}
    for chapter in chapters:
        for quest in chapter["quests"]:
            first_task = quest["tasks"][0] if quest["tasks"] else {}
            object_context[quest["id"]] = {
                "chapter_id": chapter["id"],
                "chapter_file": chapter["filename"],
                "item_id": first_task.get("item_id", ""),
            }
            for task in quest["tasks"]:
                object_context[task["id"]] = {
                    "chapter_id": chapter["id"],
                    "chapter_file": chapter["filename"],
                    "item_id": task["item_id"],
                }

    for kind, prefix, ids in (
        ("group", "chapter_group", group_ids),
        ("chapter", "chapter", {chapter["id"] for chapter in chapters}),
    ):
        for object_id in sorted(ids):
            key = f"{prefix}.{object_id}.title"
            if key in omitted_keys:
                continue
            source = text_value(english, key)
            if not source:
                continue
            target = canonical_navigation(source, kind)
            present = text_value(current, key)
            if present != target:
                add_issue(
                    issues,
                    kind=kind,
                    object_id=object_id,
                    source_value=source,
                    current_korean=present,
                    problem_type="목차 표기 불일치",
                    applied_fix=target,
                )

    item_quest_titles: dict[str, set[str]] = defaultdict(set)
    for chapter in chapters:
        for quest in chapter["quests"]:
            quest_id = quest["id"]
            title_key = f"quest.{quest_id}.title"
            desc_key = f"quest.{quest_id}.quest_desc"
            source_title = text_value(english, title_key)
            current_title = text_value(current, title_key)
            first_task = quest["tasks"][0] if quest["tasks"] else None
            single_item_task = first_task if len(quest["tasks"]) == 1 else None
            fallback = ""
            resource_name = ""
            item_id = ""
            if first_task:
                task_key = f"task.{first_task['id']}.title"
                fallback = text_value(current, task_key)
                item_id = first_task["item_id"]
                language_key = item_keys.get(item_id, "")
                resource_name = project_ko.get(language_key, "")
                fallback = (
                    fallback
                    or first_task["custom_name"]
                    or resource_name
                    or installed_ko.get(language_key, "")
                    or installed_en.get(language_key, "")
                    or first_task["type"]
                )
            fallback_needs_title = not fallback or looks_untranslated(fallback)
            if (
                text_value(current, desc_key)
                and not current_title
                and fallback_needs_title
            ):
                add_issue(
                    issues,
                    kind="quest",
                    object_id=quest_id,
                    chapter_id=chapter["id"],
                    chapter_file=chapter["filename"],
                    source_value=source_title,
                    fallback_value=fallback,
                    item_id=item_id,
                    resourcepack_translation=resource_name,
                    problem_type="설명은 있으나 명시적 quest.title 없음",
                    applied_fix=(
                        resource_name
                        if resource_name and not first_task["custom_name"]
                        else ""
                    ),
                )
            if current_title and looks_untranslated(current_title):
                add_issue(
                    issues,
                    kind="quest",
                    object_id=quest_id,
                    chapter_id=chapter["id"],
                    chapter_file=chapter["filename"],
                    source_value=source_title,
                    current_korean=current_title,
                    problem_type="한국어 파일의 영어 quest.title",
                )
            source_item_name = ""
            if single_item_task:
                language_key = item_keys.get(single_item_task["item_id"], "")
                source_item_name = installed_en.get(language_key, "")
            item_based_title = bool(
                single_item_task
                and (
                    not source_title
                    or strip_formatting(source_title)
                    == strip_formatting(source_item_name)
                )
            )
            if current_title and item_id and item_based_title:
                item_quest_titles[item_id].add(strip_formatting(current_title))
                if resource_name and strip_formatting(current_title) != resource_name:
                    add_issue(
                        issues,
                        kind="quest",
                        object_id=quest_id,
                        chapter_id=chapter["id"],
                        chapter_file=chapter["filename"],
                        source_value=source_title,
                        current_korean=current_title,
                        item_id=item_id,
                        resourcepack_translation=resource_name,
                        problem_type="리소스팩 아이템명과 quest.title 불일치",
                        applied_fix=resource_name,
                    )

            for task in quest["tasks"]:
                task_key = f"task.{task['id']}.title"
                current_task_title = text_value(current, task_key)
                source_task_title = text_value(english, task_key)
                language_key = item_keys.get(task["item_id"], "")
                resource_task_name = project_ko.get(language_key, "")
                hover = (
                    task["custom_name"]
                    or resource_task_name
                    or installed_ko.get(language_key, "")
                    or installed_en.get(language_key, "")
                )
                hover_needs_title = not hover or looks_untranslated(hover)
                source_item_name = installed_en.get(language_key, "")
                redundant_item_title = bool(
                    task["id"] in title_rules.REDUNDANT_SINGLE_ITEM_TASK_IDS
                    or (
                        task["item_id"]
                        and source_item_name
                        and strip_formatting(source_task_title)
                        == strip_formatting(source_item_name)
                    )
                )
                if (
                    not current_task_title
                    and source_task_title
                    and task_key not in omitted_keys
                    and not redundant_item_title
                    and strip_formatting(source_task_title) != "AllRightsReserved"
                ):
                    add_issue(
                        issues,
                        kind="task",
                        object_id=task["id"],
                        chapter_id=chapter["id"],
                        chapter_file=chapter["filename"],
                        source_value=source_task_title,
                        fallback_value=hover,
                        item_id=task["item_id"],
                        resourcepack_translation=resource_task_name,
                        problem_type="영어 원문 task.title에 대응하는 한국어 없음",
                    )
                if not current_task_title and task["item_id"] and hover_needs_title:
                    add_issue(
                        issues,
                        kind="task",
                        object_id=task["id"],
                        chapter_id=chapter["id"],
                        chapter_file=chapter["filename"],
                        source_value=source_task_title,
                        fallback_value=hover,
                        item_id=task["item_id"],
                        resourcepack_translation=resource_task_name,
                        problem_type="명시적 task.title 없이 아이템 hover 사용",
                        applied_fix=(
                            resource_task_name
                            if resource_task_name and not task["custom_name"]
                            else ""
                        ),
                    )
                if current_task_title and looks_untranslated(current_task_title):
                    add_issue(
                        issues,
                        kind="task",
                        object_id=task["id"],
                        chapter_id=chapter["id"],
                        chapter_file=chapter["filename"],
                        source_value=source_task_title,
                        current_korean=current_task_title,
                        item_id=task["item_id"],
                        resourcepack_translation=resource_task_name,
                        problem_type="한국어 파일의 영어 task.title",
                    )
                if (
                    not current_task_title
                    and task["custom_name"]
                    and looks_untranslated(task["custom_name"])
                ):
                    add_issue(
                        issues,
                        kind="task",
                        object_id=task["id"],
                        chapter_id=chapter["id"],
                        chapter_file=chapter["filename"],
                        fallback_value=task["custom_name"],
                        item_id=task["item_id"],
                        resourcepack_translation=resource_task_name,
                        problem_type="영어 custom_name 또는 literal component",
                    )

    checked_text_keys = {
        key
        for key in set(english) & set(current)
        if key.endswith(".title")
        or key.endswith(".quest_subtitle")
        or key.endswith(".chapter_subtitle")
    }
    for key in sorted(checked_text_keys):
        errors = lang_snbt.validate_value(key, english[key], current[key])
        for error in errors:
            add_issue(
                issues,
                kind=key.split(".", 1)[0],
                object_id=key.split(".")[1],
                source_value=text_value(english, key),
                current_korean=text_value(current, key),
                problem_type=f"제목/부제 형식 불일치: {error.split(': ', 1)[-1]}",
            )
        if (
            key.endswith("quest_subtitle") or key.endswith("chapter_subtitle")
        ) and looks_untranslated(text_value(current, key)):
            add_issue(
                issues,
                kind=key.split(".", 1)[0],
                object_id=key.split(".")[1],
                source_value=text_value(english, key),
                current_korean=text_value(current, key),
                problem_type="한국어 파일의 영어 subtitle",
            )

    for item_id, titles in sorted(item_quest_titles.items()):
        if len(titles) > 1:
            add_issue(
                issues,
                kind="item",
                object_id=item_id,
                item_id=item_id,
                current_korean=" | ".join(sorted(titles)),
                problem_type="같은 아이템의 quest.title 표기 불일치",
            )

    changed_title_keys = {
        key
        for key in (set(baseline) | set(current)) & set(english)
        if baseline.get(key) != current.get(key)
        and key.split(".")[1] in object_ids
        and (
            key.endswith(".title")
            or key.endswith(".quest_subtitle")
            or key.endswith(".chapter_subtitle")
        )
    }
    for key in sorted(changed_title_keys):
        parts = key.split(".")
        kind = parts[0]
        object_id = parts[1]
        context = object_context.get(object_id, {})
        item_id = context.get("item_id", "")
        language_key = item_keys.get(item_id, "")
        add_issue(
            issues,
            kind=kind,
            object_id=object_id,
            chapter_id=context.get("chapter_id", ""),
            chapter_file=context.get("chapter_file", ""),
            source_value=text_value(english, key),
            current_korean=text_value(baseline, key),
            item_id=item_id,
            resourcepack_translation=project_ko.get(language_key, ""),
            problem_type="적용한 제목 정상화",
            applied_fix=text_value(current, key),
        )

    invalid_ids = sorted(
        row["object_id"]
        for row in issues
        if row["kind"] in {"group", "chapter", "quest", "task"}
        and row["object_id"] not in object_ids
    )
    if invalid_ids:
        raise ValueError(f"유효하지 않은 객체 ID: {invalid_ids}")

    counts = Counter(row["problem_type"] for row in issues)
    report = {
        "instance": str(instance),
        "source": str(quest_root),
        "korean_output": str(OUTPUT_LANG),
        "chapter_count": len(chapters),
        "quest_count": sum(len(chapter["quests"]) for chapter in chapters),
        "task_count": sum(
            len(quest["tasks"]) for chapter in chapters for quest in chapter["quests"]
        ),
        "object_ids_valid": True,
        "problem_counts": dict(sorted(counts.items())),
        "applied_change_count": len(changed_title_keys),
        "remaining_issue_count": sum(
            row["problem_type"] != "적용한 제목 정상화" for row in issues
        ),
        "issues": issues,
    }
    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with REPORT_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(issues[0]) if issues else [],
            quoting=csv.QUOTE_ALL,
        )
        if issues:
            writer.writeheader()
            writer.writerows(issues)
    print(
        json.dumps(
            {key: value for key, value in report.items() if key != "issues"},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
