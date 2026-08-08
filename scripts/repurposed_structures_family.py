#!/usr/bin/env python3
"""Repurposed Structures의 현재 표시 문구를 번역하고 전체 표면을 검증해요."""

from __future__ import annotations

import argparse
import gzip
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

from dungeons_arise_family import (
    FORMAT_CODE,
    NUMBER,
    PLACEHOLDER,
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

FAMILY = "repurposed_structures"
NAMESPACE = "repurposed_structures"
JAR_PATTERN = "repurposed_structures-*.jar"
EXPECTED_LANGUAGE_KEYS = 163
WORK_ROOT = PROJECT_ROOT / "working/repurposed_structures"
LANG_OUTPUT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/repurposed_structures/lang/ko_kr.json"
)
OVERRIDE_ROOT = PROJECT_ROOT / "output/overrides/kubejs"
FOREIGN_SCRIPT = re.compile(r"[\u0600-\u06ff\u3040-\u30ff\u4e00-\u9fff]")

TEXT = {
    "Start exploring for structures!": "구조물 탐험을 시작하세요!",
    "Repurposed Structures": "Repurposed Structures",
    "Civilization from the Beyond": "저 너머의 문명",
    "Bastions, Evil, and Bones...": "보루, 악과 뼈...",
    "Blazing Cities": "불타는 도시",
    "Skyward Cities": "하늘을 향한 도시",
    "Decaying Glory": "쇠락하는 영광",
    "The Useless Portal": "쓸모없는 차원문",
    "Having a Hobbit Time!": "호빗처럼 즐거운 시간!",
    "Lavish Livings": "호화로운 삶",
    "Toiling in the Mines": "광산에서의 고된 노동",
    "Territory Control": "영토 지배",
    "Raider of the Tombs": "무덤 약탈자",
    "Remains of the Past": "과거의 흔적",
    "Interdimensional Pirates": "차원을 넘나드는 해적",
    "Following the Eyes": "눈을 따라서",
    "Tributes and Sacrifices": "공물과 희생",
    "Unanswered Prayers": "응답 없는 기도",
    "Sprawling Civilizations": "뻗어 나가는 문명",
    "Hexes and Curses": "주술과 저주",
    "Find all new Ancient Cities": "새로운 고대 도시를 모두 찾으세요",
    "Enter an Underground Bastion": "지하 보루에 들어가세요",
    "Enter an Overworld City": "오버월드 도시에 들어가세요",
    "Enter a Nether City": "네더 도시에 들어가세요",
    "Enter a Jungle Fortress": "정글 요새에 들어가세요",
    "Find an End themed Ruined Portal!": "엔드 분위기의 무너진 차원문을 찾으세요!",
    "Find all new Igloos!": "새로운 이글루를 모두 찾으세요!",
    "Find all new Mansions!": "새로운 대저택을 모두 찾으세요!",
    "Find all new Mineshafts!": "새로운 폐광을 모두 찾으세요!",
    "Find all new Outposts!": "새로운 전초기지를 모두 찾으세요!",
    "Find all new Pyramids!": "새로운 피라미드를 모두 찾으세요!",
    "Find all new Ruins!": "새로운 폐허를 모두 찾으세요!",
    "Find all new Shipwrecks!": "새로운 난파선을 모두 찾으세요!",
    "Find all new Strongholds!": "새로운 요새를 모두 찾으세요!",
    "Find all new Monuments!": "새로운 유적을 모두 찾으세요!",
    "Find all new Temples!": "새로운 사원을 모두 찾으세요!",
    "Find all new Villages!": "새로운 마을을 모두 찾으세요!",
    "Find all new Witch Huts!": "새로운 마녀 오두막을 모두 찾으세요!",
    "Locating... (Do not buy this map until finished)": (
        "찾는 중... (완료되기 전에는 이 지도를 구매하지 마세요)"
    ),
    "Bastion Remnant Map": "보루 잔해 지도",
    "End City Map": "엔드 도시 지도",
    "Nether Fortress Map": "네더 요새 지도",
    "Ruined Portal Map": "무너진 차원문 지도",
    "RS Mansion Map": "RS 대저택 지도",
    "Jungle Fortress Map": "정글 요새 지도",
    "Underground Bastion Map": "지하 보루 지도",
    "Mushroom Village Map": "버섯 마을 지도",
    "Overworld City Map": "오버월드 도시 지도",
    "Nether City Map": "네더 도시 지도",
    "End Stronghold Map": "엔드 요새 지도",
    "Nether Ruins Map": "네더 폐허 지도",
    "End Pyramid Map": "엔드 피라미드 지도",
    "RS Monument Map": "RS 유적 지도",
    "End Ancient City Map": "엔드 고대 도시 지도",
    "Nether Ancient City Map": "네더 고대 도시 지도",
    "Ocean Ancient City Map": "해양 고대 도시 지도",
    "Unknown Ocean Structure Map": "알 수 없는 해양 구조물 지도",
    "End Ancient City": "엔드 고대 도시",
    "Nether Ancient City": "네더 고대 도시",
    "Ocean Ancient City": "해양 고대 도시",
    "Underground Bastion": "지하 보루",
    "Nether City": "네더 도시",
    "Overworld City": "오버월드 도시",
    "Jungle Fortress": "정글 요새",
    "Grassy Igloo": "초원 이글루",
    "Mangrove Igloo": "맹그로브 이글루",
    "Mushroom Igloo": "버섯 이글루",
    "Stone Igloo": "돌 이글루",
    "Birch Mansion": "자작나무 대저택",
    "Desert Mansion": "사막 대저택",
    "Jungle Mansion": "정글 대저택",
    "Mangrove Mansion": "맹그로브 대저택",
    "Oak Mansion": "참나무 대저택",
    "Savanna Mansion": "사바나 대저택",
    "Snowy Mansion": "눈 덮인 대저택",
    "Taiga Mansion": "타이가 대저택",
    "Birch Mineshaft": "자작나무 폐광",
    "Crimson Mineshaft": "진홍빛 폐광",
    "Dark Forest Mineshaft": "어두운 숲 폐광",
    "Desert Mineshaft": "사막 폐광",
    "End Mineshaft": "엔드 폐광",
    "Icy Mineshaft": "얼음 폐광",
    "Jungle Mineshaft": "정글 폐광",
    "Nether Mineshaft": "네더 폐광",
    "Ocean Mineshaft": "해양 폐광",
    "Savanna Mineshaft": "사바나 폐광",
    "Stone Mineshaft": "돌 폐광",
    "Swamp Mineshaft": "늪 폐광",
    "Taiga Mineshaft": "타이가 폐광",
    "Warped Mineshaft": "뒤틀린 폐광",
    "Desert Monument": "사막 유적",
    "Icy Monument": "얼음 유적",
    "Jungle Monument": "정글 유적",
    "Nether Monument": "네더 유적",
    "Badlands Outpost": "악지 전초기지",
    "Birch Outpost": "자작나무 전초기지",
    "Crimson Outpost": "진홍빛 전초기지",
    "Desert Outpost": "사막 전초기지",
    "End Outpost": "엔드 전초기지",
    "Giant Tree Taiga Outpost": "거대 나무 타이가 전초기지",
    "Icy Outpost": "얼음 전초기지",
    "Jungle Outpost": "정글 전초기지",
    "Mangrove Outpost": "맹그로브 전초기지",
    "Nether Brick Outpost": "네더 벽돌 전초기지",
    "Oak Outpost": "참나무 전초기지",
    "Snowy Outpost": "눈 덮인 전초기지",
    "Taiga Outpost": "타이가 전초기지",
    "Warped Outpost": "뒤틀린 전초기지",
    "Badlands Pyramid": "악지 피라미드",
    "Dark Forest Pyramid": "어두운 숲 피라미드",
    "End Pyramid": "엔드 피라미드",
    "Forest Pyramid Flower": "꽃 숲 피라미드",
    "Giant Tree Taiga Pyramid": "거대 나무 타이가 피라미드",
    "Icy Pyramid": "얼음 피라미드",
    "Jungle Pyramid": "정글 피라미드",
    "Mushroom Pyramid": "버섯 피라미드",
    "Nether Pyramid": "네더 피라미드",
    "Ocean Pyramid": "해양 피라미드",
    "Snowy Pyramid": "눈 덮인 피라미드",
    "End Ruined Portal": "엔드 무너진 차원문",
    "Cold Ruins Land": "추운 육지 폐허",
    "Hot Ruins Land": "뜨거운 육지 폐허",
    "Icy Ruins Land": "얼어붙은 육지 폐허",
    "Warm Ruins Land": "따뜻한 육지 폐허",
    "Nether Ruins": "네더 폐허",
    "Crimson Shipwreck": "진홍빛 난파선",
    "End Shipwreck": "엔드 난파선",
    "Nether Bricks Shipwreck": "네더 벽돌 난파선",
    "Warped Shipwreck": "뒤틀린 난파선",
    "End Stronghold": "엔드 요새",
    "Nether Stronghold": "네더 요새",
    "Basalt Temple": "현무암 사원",
    "Crimson Temple": "진홍빛 사원",
    "Soul Temple": "영혼 사원",
    "Warped Temple": "뒤틀린 사원",
    "Nether Wasteland Temple": "네더 황무지 사원",
    "Ocean Temple": "해양 사원",
    "Taiga Temple": "타이가 사원",
    "Badlands Village": "악지 마을",
    "Bamboo Village": "대나무 마을",
    "Birch Village": "자작나무 마을",
    "Cherry Village": "벚나무 마을",
    "Crimson Village": "진홍빛 마을",
    "Dark Forest Village": "어두운 숲 마을",
    "Giant Taiga Village": "거대 타이가 마을",
    "Jungle Village": "정글 마을",
    "Mountains Village": "산악 마을",
    "Mushroom Village": "버섯 마을",
    "Oak Village": "참나무 마을",
    "Ocean Village": "해양 마을",
    "Swamp Village": "늪 마을",
    "Warped Village": "뒤틀린 마을",
    "Birch Witch Hut": "자작나무 마녀 오두막",
    "Dark Forest Witch Hut": "어두운 숲 마녀 오두막",
    "Giant Tree Taiga Witch Hut": "거대 나무 타이가 마녀 오두막",
    "Mangrove Witch Hut": "맹그로브 마녀 오두막",
    "Oak Witch Hut": "참나무 마녀 오두막",
    "Taiga Witch Hut": "타이가 마녀 오두막",
    "Import Modded Items": "모드 아이템 가져오기",
    "RS Loottables That Disables Importing Modded Items": (
        "모드 아이템 가져오기를 비활성화할 RS 전리품 표"
    ),
    "Adds modded loot from vanilla structure's loot tables and\ninjects them into Repurposed Structure's loot tables.\nExample: Snowy Pyramid gets all modded items that\nvanilla Desert Temple can have": (
        "바닐라 구조물의 전리품 표에 있는 모드 전리품을 가져와\n"
        "Repurposed Structures 구조물의 전리품 표에 추가합니다.\n"
        "예: 눈 덮인 피라미드에 바닐라 사막 사원에서 얻을 수 있는\n"
        "모든 모드 아이템을 추가합니다"
    ),
    'Add the identifiers for Repurposed Structures\'s loot table you\nwant to turn off the automatic modded item importing code for.\nSeparate multiple entries with a comma.\nExample:\n"repurposed_structures:chests/mansions/birch,\nrepurposed_structures:chests/mineshafts/jungle"': (
        "자동 모드 아이템 가져오기를 끌 Repurposed Structures\n"
        "전리품 표의 식별자를 추가합니다.\n"
        "여러 항목은 쉼표로 구분하세요.\n"
        "예:\n"
        '"repurposed_structures:chests/mansions/birch,\n'
        'repurposed_structures:chests/mineshafts/jungle"'
    ),
}

NBT_TEXT = {"Dry Whisky": "드라이 위스키"}


def find_jar() -> Path:
    """현재 설치본에서 Repurposed Structures JAR 하나를 찾아요."""
    matches = sorted((resolve_source_root() / "mods").glob(JAR_PATTERN))
    if len(matches) != 1:
        raise FileNotFoundError(f"JAR이 정확히 한 개가 아니에요: {matches}")
    return matches[0]


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없는 JSON을 안정된 형식으로 기록해요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def read_language(locale: str) -> dict[str, str]:
    """현재 JAR의 언어 JSON 객체를 읽어요."""
    with ZipFile(find_jar()) as archive:
        internal = f"assets/{NAMESPACE}/lang/{locale}.json"
        if internal not in archive.namelist():
            return {}
        value = json.loads(archive.read(internal))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(text, str) for key, text in value.items()
    ):
        raise TypeError(f"{locale} 언어 파일이 문자열 객체가 아니에요")
    return value


def prepare() -> dict[str, object]:
    """현재 언어·데이터 JSON·구조물 NBT의 표시 원문을 전부 추출해요."""
    jar = find_jar()
    english = read_language("en_us")
    korean = read_language("ko_kr")
    if len(english) != EXPECTED_LANGUAGE_KEYS:
        raise ValueError(
            f"영어 키 수가 달라요: {len(english)} != {EXPECTED_LANGUAGE_KEYS}"
        )
    write_json(WORK_ROOT / "en_us.json", english)
    write_json(WORK_ROOT / "bundled_ko_kr.json", korean)
    data_localized = []
    data_direct = []
    invalid_json = []
    nbt_rows = []
    guide_entries = []
    data_json_files = []
    nbt_files = []
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            lower = name.lower()
            if lower.endswith((".md", ".txt", ".json")) and any(
                segment in lower
                for segment in ("/book/", "/guide/", "/manual/", "patchouli")
            ):
                guide_entries.append(name)
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
    report = {
        "family": FAMILY,
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_mtime_ns": jar.stat().st_mtime_ns,
        "language_keys": len(english),
        "bundled_korean_candidate_keys": len(korean),
        "data_json_files": len(data_json_files),
        "data_localized_fields": data_localized,
        "data_direct_fields": data_direct,
        "nbt_files": len(nbt_files),
        "nbt_visible_fields": nbt_rows,
        "guide_candidates": guide_entries,
        "invalid_json": invalid_json,
        "errors": invalid_json,
        "status": "prepared"
        if not invalid_json and not guide_entries
        else "incomplete",
    }
    write_json(WORK_ROOT / "source_surface_catalog.json", report)
    summary = {
        "family": FAMILY,
        "jar": jar.name,
        "language_keys": len(english),
        "bundled_korean_candidate_keys": len(korean),
        "data_json_files": len(data_json_files),
        "data_localized_fields": len(data_localized),
        "data_direct_fields": len(data_direct),
        "nbt_files": len(nbt_files),
        "nbt_visible_fields": len(nbt_rows),
        "nbt_unique_values": len({row["literal"] for row in nbt_rows}),
        "guide_candidates": len(guide_entries),
        "errors": invalid_json,
        "status": report["status"],
    }
    write_json(WORK_ROOT / "inventory.json", summary)
    return summary


def translate_nbt_tag(tag: Tag, name: str | None = None) -> int:
    """NBT 태그 안의 Dry Whisky 표시 이름만 스타일을 보존해 번역해요."""
    count = 0
    if tag.kind == 8 and name in VISIBLE_NBT_STRING_NAMES:
        source = str(tag.value)
        literal = nbt_component_literal(source)
        if literal in NBT_TEXT:
            tag.value = replace_component_literal(source, NBT_TEXT[literal])
            return 1
    if tag.kind == 10:
        for child_name, child in tag.value.items():
            count += translate_nbt_tag(child, child_name)
    elif tag.kind == 9:
        child_kind, children = tag.value
        if child_kind == 8 and name in VISIBLE_NBT_LIST_NAMES:
            for child in children:
                source = str(child.value)
                literal = nbt_component_literal(source)
                if literal in NBT_TEXT:
                    child.value = replace_component_literal(source, NBT_TEXT[literal])
                    count += 1
        else:
            for child in children:
                count += translate_nbt_tag(child, name)
    return count


def build() -> dict[str, object]:
    """언어 163키와 구조물 NBT 세 파일을 확정 번역으로 만들어요."""
    catalog_path = WORK_ROOT / "source_surface_catalog.json"
    if not catalog_path.is_file():
        raise FileNotFoundError("prepare로 만든 현재 원문 목록이 없어요")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    jar = find_jar()
    if (
        catalog.get("jar") != jar.name
        or catalog.get("jar_size") != jar.stat().st_size
        or catalog.get("jar_mtime_ns") != jar.stat().st_mtime_ns
    ):
        raise RuntimeError(
            "현재 JAR이 원문 추출 당시와 달라요. prepare를 다시 실행하세요"
        )
    english = read_language("en_us")
    missing = sorted(set(english.values()) - set(TEXT))
    extra = sorted(set(TEXT) - set(english.values()))
    if missing or extra:
        raise KeyError(f"언어 번역표가 달라요: missing={missing}, extra={extra}")
    korean = {key: TEXT[source] for key, source in english.items()}
    write_json(WORK_ROOT / "ko_kr.json", korean)
    write_json(LANG_OUTPUT, korean)

    nbt_rows = [
        row for row in catalog["nbt_visible_fields"] if row["literal"] in NBT_TEXT
    ]
    nbt_files = sorted({row["file"] for row in nbt_rows})
    reports = []
    with ZipFile(jar) as archive:
        for internal in nbt_files:
            source_bytes = archive.read(internal)
            compressed = source_bytes.startswith(b"\x1f\x8b")
            raw = gzip.decompress(source_bytes) if compressed else source_bytes
            root_name, root = read_nbt(raw)
            replacements = translate_nbt_tag(root)
            target_raw = write_nbt(root_name, root)
            output = OVERRIDE_ROOT / internal
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(
                gzip.compress(target_raw, mtime=0) if compressed else target_raw
            )
            reports.append(
                {
                    "source": internal,
                    "output": output.relative_to(PROJECT_ROOT).as_posix(),
                    "replacements": replacements,
                }
            )
    errors = []
    replacement_count = sum(int(row["replacements"]) for row in reports)
    if replacement_count != len(nbt_rows):
        errors.append(f"NBT 번역 수가 달라요: {replacement_count} != {len(nbt_rows)}")
    write_json(WORK_ROOT / "translated_nbt_files.json", reports)
    candidate = read_language("ko_kr")
    reused = sum(1 for key, target in korean.items() if candidate.get(key) == target)
    report = {
        "family": FAMILY,
        "reviewed_language_keys": len(english),
        "bundled_korean_candidate_keys": len(candidate),
        "existing_korean_values_reused": reused,
        "new_or_corrected_language_values": len(korean) - reused,
        "nbt_files": len(reports),
        "nbt_replacements": replacement_count,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def load_json_without_duplicates(path: Path) -> tuple[object, list[str]]:
    """중복 키를 놓치지 않고 JSON을 읽어요."""
    duplicates = []

    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        value = {}
        for key, child in pairs:
            if key in value:
                duplicates.append(key)
            value[key] = child
        return value

    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook)
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        return {}, [f"{path}: JSON을 읽지 못했어요: {exc}"]
    return value, [f"{path} 중복 키: {key}" for key in duplicates]


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
    """FTB Quests와 KubeJS의 관련 참조와 직접 표시 후보를 확인해요."""
    instance = resolve_source_root()
    errors = []
    report: dict[str, object] = {"ftbquests": [], "kubejs": [], "read_errors": []}
    suffixes = {".cfg", ".js", ".json", ".snbt", ".toml", ".txt"}
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
                read_errors = report["read_errors"]
                if isinstance(read_errors, list):
                    read_errors.append(f"{path}: {exc}")
                continue
            count = text.lower().count(f"{NAMESPACE}:")
            if not count:
                continue
            visible_lines = []
            for number, line in enumerate(text.splitlines(), 1):
                if f"{NAMESPACE}:" not in line.lower():
                    continue
                if re.search(
                    r"(?i)(?:custom_name|displayname|display_name|lore|subtitle|title|tooltip)"
                    r"\s*[:=(]",
                    line,
                ):
                    visible_lines.append(number)
            row = {
                "path": path.relative_to(instance).as_posix(),
                "namespace_occurrences": count,
                "visible_namespace_candidate_lines": visible_lines,
            }
            rows.append(row)
            if visible_lines:
                errors.append(f"{label}에 직접 표시 문구 후보가 있어요: {row}")
    read_errors = report["read_errors"]
    if isinstance(read_errors, list):
        errors.extend(str(message) for message in read_errors)
    return report, errors


def audit() -> tuple[dict[str, object], list[str]]:
    """현재 원문 목록과 별도 표시 경로를 감사해요."""
    errors = []
    catalog = json.loads(
        (WORK_ROOT / "source_surface_catalog.json").read_text(encoding="utf-8")
    )
    jar = find_jar()
    if (
        catalog.get("jar") != jar.name
        or catalog.get("jar_size") != jar.stat().st_size
        or catalog.get("jar_mtime_ns") != jar.stat().st_mtime_ns
    ):
        errors.append("현재 JAR이 원문 추출 당시와 달라요")
    if catalog["invalid_json"]:
        errors.append(f"읽지 못한 데이터 JSON이 있어요: {catalog['invalid_json']}")
    if catalog["guide_candidates"]:
        errors.append(f"별도 가이드 후보가 있어요: {catalog['guide_candidates']}")
    if catalog["data_direct_fields"]:
        errors.append(
            f"예상하지 않은 직접 데이터 문구가 있어요: {catalog['data_direct_fields']}"
        )
    english = read_language("en_us")
    missing_keys = sorted(
        {
            row["value"]["translate"]
            for row in catalog["data_localized_fields"]
            if row["value"]["translate"] not in english
        }
    )
    if missing_keys:
        errors.append(
            f"데이터가 참조하지만 제공되지 않는 언어 키가 있어요: {missing_keys}"
        )
    expected_nbt_values = {"<----", "---->", "-->  <--", "Dry Whisky"}
    actual_nbt_values = {row["literal"] for row in catalog["nbt_visible_fields"]}
    if actual_nbt_values != expected_nbt_values:
        errors.append(
            "NBT 표시 원문 목록이 달라요: "
            f"missing={sorted(expected_nbt_values - actual_nbt_values)}, "
            f"extra={sorted(actual_nbt_values - expected_nbt_values)}"
        )
    dry_whisky = sum(
        row["literal"] == "Dry Whisky" for row in catalog["nbt_visible_fields"]
    )
    if dry_whisky != 15:
        errors.append(f"Dry Whisky 표시 수가 달라요: {dry_whisky} != 15")
    references, reference_errors = audit_references()
    errors.extend(reference_errors)
    report = {
        "family": FAMILY,
        "data_localized_fields": len(catalog["data_localized_fields"]),
        "data_direct_fields": len(catalog["data_direct_fields"]),
        "nbt_visible_fields": len(catalog["nbt_visible_fields"]),
        "nbt_translated_fields": dry_whisky,
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
    """현재 영어 163키와 번들 후보 전체를 대조한 확정 번역을 검증해요."""
    errors = []
    english = read_language("en_us")
    candidate = read_language("ko_kr")
    expected = {key: TEXT[source] for key, source in english.items()}
    work, work_errors = load_json_without_duplicates(WORK_ROOT / "ko_kr.json")
    output, output_errors = load_json_without_duplicates(LANG_OUTPUT)
    errors.extend(work_errors + output_errors)
    if not isinstance(work, dict) or not isinstance(output, dict):
        return {"status": "incomplete"}, errors
    if list(work) != list(english) or list(output) != list(english):
        errors.append("언어 키 또는 순서가 현재 영어 원문과 달라요")
    if work != output or output != expected:
        errors.append("작업본·산출물·확정 번역값이 서로 달라요")
    same_as_source = set()
    no_hangul = set()
    foreign_script = {}
    for key, source in english.items():
        target = output.get(key)
        if not isinstance(target, str):
            errors.append(f"문자열이 아닌 번역값이 있어요: {key}")
            continue
        errors.extend(preserved_errors(key, source, target))
        if source == target:
            same_as_source.add(key)
        if target and not re.search(r"[가-힣]", target):
            no_hangul.add(key)
        foreign = sorted(set(FOREIGN_SCRIPT.findall(target)))
        if foreign:
            foreign_script[key] = foreign
    expected_same = {key for key, source in english.items() if TEXT[source] == source}
    if same_as_source != expected_same:
        errors.append(
            "영어와 같은 값 검토 결과가 달라요: "
            f"missing={sorted(expected_same - same_as_source)}, "
            f"unexpected={sorted(same_as_source - expected_same)}"
        )
    if no_hangul - expected_same:
        errors.append(f"한국어가 없는 값이 있어요: {sorted(no_hangul - expected_same)}")
    if foreign_script:
        errors.append(f"한국어 외 문자권 문자가 남았어요: {foreign_script}")
    reused = sum(1 for key, target in output.items() if candidate.get(key) == target)
    report = {
        "reviewed_english_keys": len(english),
        "bundled_korean_candidate_keys": len(candidate),
        "existing_korean_values_reused": reused,
        "new_or_corrected_values": len(output) - reused,
        "intentional_same_keys": sorted(same_as_source),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify_nbt_outputs() -> tuple[dict[str, object], list[str]]:
    """세 NBT 산출물의 경로·스타일·번역값을 다시 확인해요."""
    errors = []
    catalog = json.loads(
        (WORK_ROOT / "source_surface_catalog.json").read_text(encoding="utf-8")
    )
    rows = json.loads(
        (WORK_ROOT / "translated_nbt_files.json").read_text(encoding="utf-8")
    )
    expected_by_file: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in catalog["nbt_visible_fields"]:
        target = NBT_TEXT.get(row["literal"], row["literal"])
        expected_by_file[row["file"]].append((row["path"], target))
    expected_files = {
        file
        for file, values in expected_by_file.items()
        if any(literal == "드라이 위스키" for _path, literal in values)
    }
    manifest_files = {row["source"] for row in rows}
    if manifest_files != expected_files:
        errors.append(
            "NBT 산출물 목록이 달라요: "
            f"missing={sorted(expected_files - manifest_files)}, "
            f"extra={sorted(manifest_files - expected_files)}"
        )
    translated = 0
    for row in rows:
        output_path = PROJECT_ROOT / row["output"]
        try:
            value = output_path.read_bytes()
            raw = gzip.decompress(value) if value.startswith(b"\x1f\x8b") else value
            actual = [(item["path"], item["literal"]) for item in scan_visible_nbt(raw)]
        except (EOFError, OSError, UnicodeError, ValueError) as exc:
            errors.append(f"NBT 산출물을 읽지 못했어요: {row['output']}: {exc}")
            continue
        if actual != expected_by_file[row["source"]]:
            errors.append(f"NBT 표시 경로나 번역값이 달라요: {row['output']}")
        translated += int(row["replacements"])
    if translated != 15:
        errors.append(f"NBT 번역 수가 달라요: {translated} != 15")
    report = {
        "files": len(rows),
        "translated_visible_fields": translated,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def deployment_paths() -> set[str]:
    """이 모드가 실제 인스턴스에 적용할 정확한 상대 경로를 반환해요."""
    paths = {"resourcepacks/ATM10_Korean/assets/repurposed_structures/lang/ko_kr.json"}
    manifest_path = WORK_ROOT / "translated_nbt_files.json"
    if manifest_path.is_file():
        rows = json.loads(manifest_path.read_text(encoding="utf-8"))
        paths.update(row["output"].removeprefix("output/overrides/") for row in rows)
    return paths


def verify() -> tuple[dict[str, object], list[str]]:
    """언어·NBT·외부 표시 경로를 함께 검증해요."""
    language, language_errors = verify_language()
    nbt, nbt_errors = verify_nbt_outputs()
    surface, surface_errors = audit()
    errors = language_errors + nbt_errors + surface_errors
    expected_override_files = {
        path.removeprefix("kubejs/")
        for path in deployment_paths()
        if path.startswith("kubejs/data/repurposed_structures/")
    }
    actual_override_files = {
        path.relative_to(OVERRIDE_ROOT).as_posix()
        for path in (OVERRIDE_ROOT / "data/repurposed_structures").rglob("*")
        if path.is_file()
    }
    if actual_override_files != expected_override_files:
        errors.append(
            "덮어쓰기 산출물 목록이 달라요: "
            f"missing={sorted(expected_override_files - actual_override_files)}, "
            f"extra={sorted(actual_override_files - expected_override_files)}"
        )
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
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = (
        json.loads(deployment_path.read_text(encoding="utf-8"))
        if deployment_path.is_file()
        else None
    )
    completion = {
        "family": FAMILY,
        "language_keys": language["reviewed_english_keys"],
        "existing_korean_values_reused": language["existing_korean_values_reused"],
        "new_or_corrected_translations": language["new_or_corrected_values"],
        "translated_nbt_fields": nbt["translated_visible_fields"],
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
    errors = []
    manifest_path = manifest_path.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
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
        if target.get("status") != "applied_and_verified":
            errors.append(
                f"대상 적용 상태가 완료가 아니에요: {target.get('target_root')}"
            )
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
        choices=("prepare", "build", "audit", "verify", "record-deployment", "all"),
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
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        result, _ = record_deployment(args.manifest)
    else:
        prepared = prepare()
        built = build()
        verification, verification_errors = verify()
        result = {
            "prepare": prepared,
            "build": built,
            "verify": verification,
            "status": "complete" if not verification_errors else "incomplete",
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return (
        0 if result["status"] in {"prepared", "complete", "applied_and_verified"} else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
