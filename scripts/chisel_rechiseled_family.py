#!/usr/bin/env python3
"""Chisel·Rechiseled·Rechiseled: Create의 표시 문구를 번역·검증해요."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
from chipped_family import load_json, minecraft_assets, write_json
from dungeons_arise_family import (
    VISIBLE_DATA_KEYS,
    component_literal_text,
    scan_visible_nbt,
    walk_json,
)
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

FAMILY = "chisel_rechiseled"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
JARS = {
    "chisel": ("chisel-neoforge-*.jar", "chisel"),
    "rechiseled": ("rechiseled-*.jar", "rechiseled"),
    "rechiseledcreate": ("rechiseledcreate-*.jar", "rechiseledcreate"),
}
OUTPUTS = {
    namespace: (
        active_output_root()
        / f"resourcepack/ATM10_Korean/assets/{namespace}/lang/ko_kr.json"
    )
    for namespace in JARS
}
DEPLOYMENT_PATHS = [
    f"resourcepacks/ATM10_Korean/assets/{namespace}/lang/ko_kr.json"
    for namespace in JARS
]
QUEST_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
QUEST_DEPLOYMENT_PATH = "config/ftbquests/quests/lang/ko_kr.snbt"
DEPLOYMENT_PATHS.append(QUEST_DEPLOYMENT_PATH)
CREATE_ENGLISH = PROJECT_ROOT / "working/create/create/en_us.json"
CREATE_KOREAN = PROJECT_ROOT / "working/create/create/ko_kr.json"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[./xX×+]\d+)*")
NAME_TOKEN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

UI_TRANSLATIONS = {
    "chisel.deprecated": "사용 중단됨 - 사용하지 마세요",
    "gui.chisel.chisel": "끌",
    "item.chisel.chisel": "끌",
    "itemGroup.chisel.chisel": "Chisel",
    "rei.chisel.category": "끌 조합법",
    "subtitles.chisel.chisel_sound": "블록을 끌로 깎음",
    "rechiseled.item_group": "Rechiseled",
    "rechiseled.tooltip.connecting": "연결형",
    "rechiseled.chiseling.preview.mode_0": "1 × 1 미리보기",
    "rechiseled.chiseling.preview.mode_1": "3 × 1 미리보기",
    "rechiseled.chiseling.preview.mode_2": "3 × 3 미리보기",
    "rechiseled.chiseling.connecting": "연결 텍스처: %s",
    "rechiseled.chiseling.connecting.on": "켜짐",
    "rechiseled.chiseling.connecting.off": "꺼짐",
    "rechiseled.chiseling.chisel_all": "모두 끌로 가공",
    "rechiseled.chiseling.chisel_all.shift": "모든 모양에 %s",
    "rechiseled.chiseling.chisel_all.items": "%s개 아이템",
    "rechiseled.chiseling.select_block": "%s 선택",
    "rechiseled.chiseling.preview": "블록 미리보기",
    "rechiseled.chiseling.select_shape": "모양: %s",
    "rechiseled.chiseling.filter": "필터 옵션",
    "rechiseled.chiseling.filter.clear": "우클릭하여 지우기",
    "rechiseled.chiseling.filter.show_blocks": "블록 표시",
    "rechiseled.chiseling.filter.show_stairs": "계단 표시",
    "rechiseled.chiseling.filter.show_slabs": "반 블록 표시",
    "rechiseled.chiseling.filter.show_non_connecting": "비연결형 표시",
    "rechiseled.chiseling.scrollbar": "스크롤 막대",
    "rechiseled.chiseling.entry.recipe": "조합법: %s",
    "rechiseled.chiseling.entry.owner": "플러그인: %s",
    "rechiseled.recipe_category.title": "끌 가공",
    "rechiseled.recipe_category.conversion_value": "변환값: %s",
    "rechiseled.item.chisel": "끌",
    "rechiseled.chiseling.shape.block": "블록",
    "rechiseled.chiseling.shape.stairs": "계단",
    "rechiseled.chiseling.shape.slab": "반 블록",
    "rechiseledcreate.item_group": "Rechiseled: Create 연동",
    "block.rechiseledcreate.mechanical_chisel": "기계식 끌",
}

FTB_TRANSLATIONS: dict[str, quest_snbt.TranslationValue] = {
    "quest.09F49ED309152E24.quest_desc": [
        "&l&cChisel Reborn&r은 &lChiseled&r를 바탕으로 만든 또 다른 모드입니다. "
        "\\n\\n이 모드에서는 끌로 여러 블록의 무늬를 바꿀 수 있습니다. "
        "\\n\\n끌을 들고 우클릭하면 GUI가 열립니다. 블록을 한 묶음까지 넣고 원하는 "
        "무늬를 고른 뒤 꺼내세요. 블록을 끌 안에 보관할 수도 있지만, 굳이 그럴 "
        "이유는 없겠죠. \\n\\n끌로 블록을 좌클릭하면 GUI를 열지 않고도 무늬를 바꿀 "
        "수 있습니다! \\n\\n이 끌은 내구도를 소모하지 않으니 걱정하지 마세요."
    ],
    "quest.09F49ED309152E24.title": "&l&cChisel Reborn",
    "quest.3497C2E05DF5A87C.quest_desc": [
        "&c레드스톤&r, &9청금석&r, 석영, &5자수정&r, &a에메랄드&r, 그리고 "
        "&b다이아몬드&r는 모두 귀한 보석입니다. \\n\\n그러니 보기 좋고 반듯한 장식 "
        "블록으로 바꿔 봅시다!"
    ],
    "quest.3497C2E05DF5A87C.title": "&l&bChipped&r 보석 블록",
    "quest.5EB488C393B084C4.quest_desc": [
        "&lChiseled&r를 잇는 모드, &4&lRechiseled&r입니다! \\n\\n이 모드의 기능은 "
        "모두 끌에서 사용할 수 있습니다. 끌을 들고 우클릭하면 GUI가 열립니다. "
        "\\n왼쪽에서 무늬를 고르고 오른쪽 아래 칸에 블록을 넣으세요. \\n\\n위쪽에서는 "
        "무늬를 1개 블록, 3x1 블록, 또는 3x3 벽 형태로 미리 볼 수 있습니다. "
        "버튼을 눌러 미리보기의 회전 여부도 바꿀 수 있습니다! \\n\\n블록을 넣는 칸 "
        "옆의 끌 버튼을 누르면 선택한 무늬를 인벤토리에 있는 가공 가능한 모든 "
        "블록에 적용합니다. \\n\\n이 끌도 내구도를 소모하지 않습니다!"
    ],
    "quest.5EB488C393B084C4.title": "&4&lRechiseled&r",
    "task.41FF171C7D97B574.title": "Chipped 보석 블록",
}

REVIEWED_PHRASES = {
    ("No", "Border"): "테두리 없는",
    ("Block", "of", "Diamonds"): "다이아몬드 무늬 블록",
    ("Coal", "Large", "Bricks"): "큰 석탄 벽돌",
    ("Stone", "Large", "Bricks"): "큰 석재 벽돌",
    ("Encased", "Brick"): "벽돌로 둘러싼",
    ("Cobbled", "Stone"): "조약돌형 돌",
    ("Slated", "Stone"): "판석형 돌",
    ("Stone", "Brick"): "석재 벽돌형",
    ("Stone", "Brick", "Pattern"): "석재 벽돌 무늬",
    ("Stone", "Brick", "Paving"): "석재 벽돌 포장",
    ("Smooth", "Stone", "Brick"): "매끄러운 석재 벽돌",
    ("Diamond", "Block", "Gem"): "보석형 다이아몬드 블록",
    ("Stone", "Gem"): "보석형 돌",
}

# 장식 이름은 영어 원문의 단어를 모두 검수한 뒤 같은 뜻을 한 용어로 고정해요.
WORD_TRANSLATIONS = {
    "Acacia": "아카시아나무",
    "Amethyst": "자수정",
    "Andesite": "안산암",
    "Array": "배열형",
    "Asurine": "담청암",
    "Bamboo": "대나무",
    "Bars": "창살",
    "Basalt": "현무암",
    "Beams": "들보",
    "Bevel": "모서리 깎은",
    "Birch": "자작나무",
    "Bismuth": "비스무트",
    "Black": "검은색",
    "Blackstone": "흑암",
    "Blobs": "얼룩",
    "Block": "블록",
    "Blocks": "블록",
    "Blue": "파란색",
    "Bone": "뼈",
    "Border": "테두리",
    "Bordered": "테두리 두른",
    "Braid": "땋은 무늬",
    "Brick": "벽돌",
    "Bricks": "벽돌",
    "Brown": "갈색",
    "Bubble": "거품 무늬",
    "Bundled": "묶은",
    "Calcite": "방해석",
    "Cart": "수레 무늬",
    "Carved": "새긴",
    "Cells": "격자 칸",
    "Chaotic": "불규칙한",
    "Cherry": "벚나무",
    "Chinese": "중국식",
    "Chisel": "끌",
    "Chiseled": "조각된",
    "Chrono": "시계 무늬",
    "Chunks": "덩어리",
    "Chunky": "덩어리진",
    "Circles": "원 무늬",
    "Circular": "원형",
    "Classic": "고전식",
    "Clovers": "클로버 무늬",
    "Clumps": "뭉친",
    "Coal": "석탄",
    "Cobble": "조약돌형",
    "Cobbled": "조약돌",
    "Cobblestone": "조약돌",
    "Coin": "동전",
    "Compacted": "다져진",
    "Compressed": "압축된",
    "Concrete": "콘크리트",
    "Cone": "원뿔 무늬",
    "Copper": "구리",
    "Covered": "덮인",
    "Cracked": "금이 간",
    "Crate": "상자",
    "Creeper": "크리퍼",
    "Crimsite": "진홍암",
    "Crimson": "진홍빛",
    "Crosses": "십자 무늬",
    "Crude": "거친",
    "Crushed": "부순",
    "Crystal": "수정",
    "Cubes": "정육면체 무늬",
    "Cut": "깎인",
    "Cyan": "청록색",
    "Dark": "짙은",
    "Decorated": "장식된",
    "Deepslate": "심층암",
    "Dent": "움푹 들어간",
    "Dented": "움푹 팬",
    "Diamond": "다이아몬드",
    "Diamonds": "다이아몬드 무늬",
    "Diagonal": "대각선",
    "Diorite": "섬록암",
    "Dirt": "흙",
    "Dotted": "점무늬",
    "Dripstone": "점적석",
    "Dungeon": "던전",
    "Edged": "테두리형",
    "Embossed": "양각",
    "Emerald": "에메랄드",
    "Encased": "테두리 두른",
    "End": "엔드",
    "Fabric": "직물 무늬",
    "Face": "얼굴 무늬",
    "Flooring": "바닥재",
    "Four": "네 칸",
    "Framed": "액자형",
    "French": "프랑스식",
    "Gears": "톱니바퀴",
    "Gem": "보석",
    "Glass": "유리",
    "Glossy": "광택 있는",
    "Glowstone": "발광석",
    "Glyphs": "문양",
    "Gold": "금",
    "Granite": "화강암",
    "Gray": "회색",
    "Green": "초록색",
    "Grid": "격자",
    "Grooves": "홈",
    "Happy": "웃는 얼굴",
    "Hard": "단단한",
    "Heads": "앞면",
    "Horizontal": "가로",
    "Ice": "얼음",
    "Indented": "오목한",
    "Ingot": "주괴",
    "Inverted": "반전된",
    "Iron": "철",
    "Jagged": "들쭉날쭉한",
    "Japanese": "일본식",
    "Jellybean": "젤리빈",
    "Jewel": "보석",
    "Jungle": "정글나무",
    "Lapis": "청금석",
    "Large": "큰",
    "Layer": "겹",
    "Layered": "층진",
    "Lazuli": "",
    "Legacy": "구형",
    "Light": "밝은",
    "Lime": "연두색",
    "Limestone": "석회암",
    "Lines": "선 무늬",
    "Llama": "라마",
    "Log": "원목",
    "Magenta": "자홍색",
    "Mangrove": "맹그로브나무",
    "Masonry": "석조",
    "Mechanical": "기계식",
    "Medium": "중간 크기",
    "Mesh": "그물",
    "Meteoric": "운석",
    "Moon": "달",
    "Mosaic": "모자이크",
    "Mossy": "이끼 낀",
    "Muddy": "진흙 묻은",
    "Neon": "네온",
    "Nether": "네더",
    "Netherite": "네더라이트",
    "Netherrack": "네더랙",
    "Oak": "참나무",
    "Obsidian": "흑요석",
    "Ochrum": "황토암",
    "Orange": "주황색",
    "Organic": "유기적",
    "Ornate": "화려한",
    "Ovals": "타원 무늬",
    "Panel": "패널",
    "Paneling": "패널형",
    "Panes": "판유리",
    "Path": "길",
    "Pattern": "무늬",
    "Patterned": "무늬 있는",
    "Paving": "포장",
    "Piglin": "피글린",
    "Pillar": "기둥",
    "Pillars": "기둥",
    "Pink": "분홍색",
    "Pipes": "파이프",
    "Plank": "판자",
    "Planks": "판자",
    "Plated": "판을 댄",
    "Plates": "판",
    "Plating": "판금",
    "Poison": "독성",
    "Polished": "윤나는",
    "Prism": "프리즘",
    "Prismarine": "프리즈머린",
    "Processed": "가공한",
    "Pulverized": "분쇄한",
    "Purple": "보라색",
    "Purpur": "퍼퍼",
    "Quartz": "석영",
    "Raw": "가공하지 않은",
    "Red": "빨간색",
    "Redstone": "레드스톤",
    "Reinforced": "보강한",
    "Rhombuses": "마름모 무늬",
    "Ribs": "늑골 무늬",
    "Rivets": "리벳",
    "Road": "도로",
    "Rocky": "바위투성이",
    "Rose": "장밋빛",
    "Rotated": "회전한",
    "Rounded": "둥근",
    "Rows": "가로줄 무늬",
    "Sandstone": "사암",
    "Scales": "비늘 무늬",
    "Scorchia": "그을린 스코리아",
    "Scoria": "스코리아",
    "Screen": "망",
    "Shafts": "축",
    "Shale": "셰일",
    "Sheared": "잘린",
    "Sheets": "판",
    "Shiny": "빛나는",
    "Shipping": "운송용",
    "Sided": "면",
    "Simple": "단순한",
    "Skeleton": "스켈레톤",
    "Skull": "해골",
    "Slab": "반 블록",
    "Slanted": "비스듬한",
    "Slated": "판석",
    "Slim": "가느다란",
    "Small": "작은",
    "Smooth": "매끄러운",
    "Soft": "부드러운",
    "Soil": "흙",
    "Solid": "통짜",
    "Space": "우주",
    "Spiral": "나선",
    "Spotted": "얼룩무늬",
    "Spruce": "가문비나무",
    "Squares": "사각형 무늬",
    "Stacked": "쌓은",
    "Stairs": "계단",
    "Star": "별",
    "Steel": "강철",
    "Stone": "돌",
    "Streaked": "줄진",
    "Striped": "줄무늬",
    "Stripes": "줄무늬",
    "Sunken": "오목한",
    "Swirling": "소용돌이",
    "Tails": "뒷면",
    "Thick": "두꺼운",
    "Thin": "얇은",
    "Tile": "타일",
    "Tiled": "타일형",
    "Tiles": "타일",
    "Tilled": "경작된",
    "Triple": "세 겹",
    "Tuff": "응회암",
    "Twisted": "비틀린",
    "Vents": "환기구",
    "Veridium": "심록암",
    "Vertical": "세로",
    "Warped": "뒤틀린",
    "Waves": "물결",
    "Wavy": "물결무늬",
    "Waxed": "밀랍칠한",
    "Weathered": "풍화된",
    "Weaver": "직조 무늬",
    "White": "하얀색",
    "Window": "창문",
    "Wool": "양털",
    "Woven": "엮은",
    "Yellow": "노란색",
    "Zag": "지그재그",
    "Zelda": "젤다",
}

WINDOW_MATERIALS = {
    "acacia": "아카시아나무",
    "birch": "자작나무",
    "crimson": "진홍빛",
    "dark_oak": "짙은 참나무",
    "jungle": "정글나무",
    "mangrove": "맹그로브나무",
    "oak": "참나무",
    "spruce": "가문비나무",
    "warped": "뒤틀린",
}
WINDOW_STYLES = {
    "bars": "창살",
    "covered": "덮인",
    "diagonal": "대각선",
    "large": "큰",
    "panes": "격자형",
    "rounded": "둥근",
    "slim": "가느다란",
    "swirling": "소용돌이",
    "tiles": "타일형",
}


def find_jar(label: str) -> Path:
    """현재 설치본에서 지정한 JAR 하나를 찾아요."""
    matches = sorted((resolve_source_root() / "mods").glob(JARS[label][0]))
    if len(matches) != 1:
        raise FileNotFoundError(f"{label} JAR이 정확히 한 개가 아니에요: {matches}")
    return matches[0]


def read_language(label: str, locale: str) -> dict[str, str]:
    """현재 JAR의 지정 언어 파일을 읽어요."""
    namespace = JARS[label][1]
    path = f"assets/{namespace}/lang/{locale}.json"
    with ZipFile(find_jar(label)) as archive:
        try:
            value = json.loads(archive.read(path))
        except KeyError:
            return {}
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise TypeError(f"언어 파일 형식이 올바르지 않아요: {path}")
    return value


def collect_surface(label: str) -> dict[str, object]:
    """JAR의 언어·데이터·NBT·가이드 표시 표면을 전수 추출해요."""
    jar = find_jar(label)
    language_files = []
    data_files = []
    direct_fields = []
    localized_fields = []
    invalid_json = []
    nbt_files = []
    nbt_rows = []
    guide_candidates = []
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            lower = name.lower()
            if "/lang/" in lower and lower.endswith(".json"):
                language_files.append(name)
            if lower.endswith((".md", ".txt", ".json")) and any(
                token in lower
                for token in ("/book/", "/guide/", "/manual/", "patchouli")
            ):
                guide_candidates.append(name)
            if lower.startswith("data/") and lower.endswith(".json"):
                data_files.append(name)
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
                        localized_fields.append(row)
                    else:
                        literal = component_literal_text(child)
                        if literal and literal.strip():
                            direct_fields.append({**row, "literal": literal})
            if not lower.endswith(".nbt"):
                continue
            nbt_files.append(name)
            raw = archive.read(name)
            try:
                raw = gzip.decompress(raw)
            except gzip.BadGzipFile:
                pass
            for row in scan_visible_nbt(raw):
                nbt_rows.append({"file": name, **row})
    return {
        "label": label,
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_mtime_ns": jar.stat().st_mtime_ns,
        "language_files": language_files,
        "data_json_files": len(data_files),
        "data_direct_fields": direct_fields,
        "data_localized_fields": localized_fields,
        "invalid_json": invalid_json,
        "nbt_files": len(nbt_files),
        "nbt_visible_fields": nbt_rows,
        "guide_candidates": guide_candidates,
    }


def minecraft_english_asset() -> tuple[Path, dict[str, str]]:
    """현재 Minecraft 1.21.1 클라이언트 JAR의 영어 원문을 읽어요."""
    instance = resolve_source_root()
    path = instance.parent.parent / "Install/versions/1.21.1/1.21.1.jar"
    with ZipFile(path) as archive:
        value = json.loads(archive.read("assets/minecraft/lang/en_us.json"))
    if not isinstance(value, dict):
        raise TypeError("Minecraft 공식 영어 언어 파일이 객체가 아니에요")
    return path, value


def reference_phrases() -> tuple[dict[tuple[str, ...], str], dict[str, object]]:
    """현재 Minecraft와 검수된 Create의 이름 대응표를 만들어요."""
    client_path, official_en = minecraft_english_asset()
    official_ko_path, official_ko, metadata = minecraft_assets()
    create_en = load_json(CREATE_ENGLISH)
    create_ko = load_json(CREATE_KOREAN)
    if not all(
        isinstance(value, dict) for value in (official_en, create_en, create_ko)
    ):
        raise TypeError("공식 또는 Create 언어 파일이 객체가 아니에요")
    pairs = {}
    source_counts = Counter()
    for label, english, korean in (
        ("minecraft", official_en, official_ko),
        ("create", create_en, create_ko),
    ):
        for key, source in english.items():
            target = korean.get(key)
            if (
                not key.startswith(("block.", "item."))
                or not isinstance(source, str)
                or not isinstance(target, str)
                or not re.search(r"[가-힣]", target)
            ):
                continue
            tokens = tuple(NAME_TOKEN.findall(source))
            if len(tokens) < 2:
                continue
            pairs[tokens] = target
            source_counts[label] += 1
    pairs.update(REVIEWED_PHRASES)
    provenance = {
        "minecraft_client_jar": client_path.as_posix(),
        "minecraft_client_sha256": hashlib.sha256(client_path.read_bytes()).hexdigest(),
        "minecraft_korean_asset": official_ko_path.as_posix(),
        "minecraft_korean_asset_hash": metadata["language_object_hash"],
        "minecraft_phrase_pairs": source_counts["minecraft"],
        "create_english": CREATE_ENGLISH.relative_to(PROJECT_ROOT).as_posix(),
        "create_korean": CREATE_KOREAN.relative_to(PROJECT_ROOT).as_posix(),
        "create_phrase_pairs": source_counts["create"],
    }
    return pairs, provenance


def prepare() -> dict[str, object]:
    """세 JAR의 현재 영어와 한국어 후보·전체 표시 표면을 기록해요."""
    languages = {label: read_language(label, "en_us") for label in JARS}
    surfaces = [collect_surface(label) for label in JARS]
    _, provenance = reference_phrases()
    errors = []
    instance = resolve_source_root()
    quest_english_path = instance / "config/ftbquests/quests/lang/en_us.snbt"
    quest_candidate_path = QUEST_OUTPUT
    quest_english = quest_snbt.parse_language_snbt(quest_english_path)
    quest_candidate = quest_snbt.parse_language_snbt(quest_candidate_path)
    missing_quest_source = sorted(set(FTB_TRANSLATIONS) - set(quest_english))
    missing_quest_candidate = sorted(set(FTB_TRANSLATIONS) - set(quest_candidate))
    if missing_quest_source:
        errors.append(
            f"영어 원문에 없는 FTB Quests 키가 있어요: {missing_quest_source}"
        )
    if missing_quest_candidate:
        errors.append(
            f"기존 한국어에 없는 FTB Quests 키가 있어요: {missing_quest_candidate}"
        )
    for row in surfaces:
        expected = f"assets/{JARS[row['label']][1]}/lang/en_us.json"
        if expected not in row["language_files"]:
            errors.append(f"{row['label']} 영어 언어 파일을 찾지 못했어요")
        if any(path.endswith("/lang/ko_kr.json") for path in row["language_files"]):
            errors.append(f"{row['label']}에 예상하지 못한 현재 한국어 후보가 있어요")
        if row["invalid_json"] or row["guide_candidates"]:
            errors.append(f"{row['label']} 데이터 또는 가이드 감사를 완료하지 못했어요")
    for label, value in languages.items():
        write_json(WORK_ROOT / f"{label}_en_us.json", value)
    write_json(
        WORK_ROOT / "ftb_candidate_ko.json",
        {
            key: quest_candidate[key]
            for key in FTB_TRANSLATIONS
            if key in quest_candidate
        },
    )
    catalog = {
        "family": FAMILY,
        "jars": surfaces,
        "language_keys": {label: len(value) for label, value in languages.items()},
        "total_english_keys": sum(len(value) for value in languages.values()),
        "bundled_korean_candidate_keys": {
            label: len(read_language(label, "ko_kr")) for label in JARS
        },
        "reference_sources": provenance,
        "ftbquests": {
            "english_path": quest_english_path.as_posix(),
            "english_size": quest_english_path.stat().st_size,
            "english_sha256": hashlib.sha256(
                quest_english_path.read_bytes()
            ).hexdigest(),
            "reviewed_keys": list(FTB_TRANSLATIONS),
            "candidate_keys": len(FTB_TRANSLATIONS) - len(missing_quest_candidate),
        },
        "errors": errors,
        "status": "prepared" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "source_surface_catalog.json", catalog)
    return {
        "family": FAMILY,
        "language_keys": catalog["language_keys"],
        "total_english_keys": catalog["total_english_keys"],
        "bundled_korean_candidate_keys": catalog["bundled_korean_candidate_keys"],
        "ftbquests_reviewed_keys": len(FTB_TRANSLATIONS),
        "errors": errors,
        "status": catalog["status"],
    }


def window_translation(key: str) -> str | None:
    """Rechiseled: Create의 창문 이름을 키 구조에 맞춰 번역해요."""
    prefixes = ("rechiseledcreate.block.", "block.rechiseledcreate.")
    prefix = next((value for value in prefixes if key.startswith(value)), None)
    if prefix is None:
        return None
    slug = key.removeprefix(prefix).removesuffix("_connecting")
    for material_slug, material in WINDOW_MATERIALS.items():
        marker = f"{material_slug}_window_"
        if not slug.startswith(marker):
            continue
        style_slug = slug.removeprefix(marker)
        style = WINDOW_STYLES.get(style_slug)
        if style is None:
            raise KeyError(f"검수하지 않은 창문 무늬예요: {key}")
        if style_slug in {"bars", "panes", "tiles"}:
            return f"{material} {style} 창문"
        return f"{style} {material} 창문"
    return None


def translate_name(source: str, phrases: dict[tuple[str, ...], str]) -> str:
    """검수된 구와 단어를 긴 순서로 적용해 장식 이름을 번역해요."""
    tokens = NAME_TOKEN.findall(source)
    if "".join(tokens).lower() != re.sub(r"[^A-Za-z]", "", source).lower():
        raise ValueError(f"처리하지 못한 이름 문자가 있어요: {source}")
    pieces = []
    index = 0
    while index < len(tokens):
        matched = None
        for length in range(min(8, len(tokens) - index), 1, -1):
            candidate = tuple(tokens[index : index + length])
            if candidate in phrases:
                matched = (length, phrases[candidate])
                break
        if matched is not None:
            length, target = matched
            pieces.append(target)
            index += length
            continue
        token = tokens[index]
        if token not in WORD_TRANSLATIONS:
            raise KeyError(f"검수하지 않은 이름 단어예요: {token} ({source})")
        target = WORD_TRANSLATIONS[token]
        if target:
            pieces.append(target)
        index += 1
    return " ".join(pieces)


def translate_value(
    key: str, source: str, phrases: dict[tuple[str, ...], str]
) -> tuple[str, str]:
    """키별 UI·창문 예외를 우선하고 나머지 이름을 조합해요."""
    if key in UI_TRANSLATIONS:
        return UI_TRANSLATIONS[key], "reviewed_ui"
    window = window_translation(key)
    if window is not None:
        return window, "reviewed_window_pattern"
    return translate_name(source, phrases), "reviewed_name_composition"


def build() -> dict[str, object]:
    """세 영어 언어 파일 6,673키 전체의 한국어 산출물을 만들어요."""
    phrases, provenance = reference_phrases()
    method_counts = Counter()
    output_counts = {}
    for label, (_, namespace) in JARS.items():
        english = load_json(WORK_ROOT / f"{label}_en_us.json")
        if not isinstance(english, dict):
            raise TypeError(f"{label} 영어 작업 파일이 객체가 아니에요")
        target = {}
        for key, source in english.items():
            value, method = translate_value(key, source, phrases)
            target[key] = value
            method_counts[method] += 1
        write_json(WORK_ROOT / f"{label}_ko_kr.json", target)
        write_json(OUTPUTS[namespace], target)
        output_counts[label] = len(target)
    quest_english = quest_snbt.parse_language_snbt(
        resolve_source_root() / "config/ftbquests/quests/lang/en_us.snbt"
    )
    quest_errors = []
    for key, target in FTB_TRANSLATIONS.items():
        if key not in quest_english:
            quest_errors.append(f"영어 원문에 없는 FTB Quests 키예요: {key}")
            continue
        quest_errors.extend(quest_snbt.validate_value(key, quest_english[key], target))
    if quest_errors:
        raise ValueError("\n".join(quest_errors))
    merged = quest_snbt.merge_into_full_snbt(QUEST_OUTPUT, FTB_TRANSLATIONS)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    reparsed = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    for key, target in FTB_TRANSLATIONS.items():
        if reparsed.get(key) != target:
            raise ValueError(f"FTB Quests 병합 결과가 달라요: {key}")
    candidate = load_json(WORK_ROOT / "ftb_candidate_ko.json")
    if not isinstance(candidate, dict):
        raise TypeError("FTB Quests 기존 한국어 후보 기록이 객체가 아니에요")
    kept_quest_values = sum(
        candidate.get(key) == value for key, value in FTB_TRANSLATIONS.items()
    )
    revised_quest_values = sum(
        key in candidate and candidate[key] != value
        for key, value in FTB_TRANSLATIONS.items()
    )
    new_quest_values = sum(key not in candidate for key in FTB_TRANSLATIONS)
    write_json(WORK_ROOT / "ftb_ko.json", FTB_TRANSLATIONS)
    report = {
        "reviewed_language_keys": sum(output_counts.values()),
        "existing_korean_values_reused": 0,
        "new_language_values": sum(output_counts.values()),
        "output_keys": output_counts,
        "translation_methods": dict(sorted(method_counts.items())),
        "ftbquests": {
            "reviewed_keys": len(FTB_TRANSLATIONS),
            "existing_korean_values_reused": kept_quest_values,
            "existing_korean_values_revised": revised_quest_values,
            "new_values": new_quest_values,
        },
        "reference_sources": provenance,
        "errors": [],
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def preserved_errors(key: str, source: str, target: str) -> list[str]:
    """자리표시자·서식·숫자·줄바꿈을 보존했는지 확인해요."""
    errors = []
    for label, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식 코드", FORMAT_CODE),
        ("숫자", NUMBER),
    ):
        if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
            errors.append(f"{key} {label}이 달라요")
    if source.count("\n") != target.count("\n"):
        errors.append(f"{key} 실제 줄바꿈 수가 달라요")
    if source.count("\\n") != target.count("\\n"):
        errors.append(f"{key} 이스케이프 줄바꿈 수가 달라요")
    return errors


def audit_references() -> tuple[dict[str, object], list[str]]:
    """FTB Quests와 KubeJS의 세 네임스페이스 참조를 확인해요."""
    instance = resolve_source_root()
    namespaces = tuple(namespace for _, namespace in JARS.values())
    namespace_pattern = re.compile(
        rf"(?<![a-z0-9_])(?P<namespace>{'|'.join(namespaces)}):[a-z0-9_./-]+",
        re.IGNORECASE,
    )
    report: dict[str, object] = {"ftbquests": [], "kubejs": [], "read_errors": []}
    errors = []
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
                report["read_errors"].append(f"{path}: {exc}")
                continue
            matches = list(namespace_pattern.finditer(text))
            counts = Counter(match.group("namespace").lower() for match in matches)
            if not counts:
                continue
            visible_lines = []
            for number, line in enumerate(text.splitlines(), 1):
                if namespace_pattern.search(line) is None:
                    continue
                if re.search(
                    r"(?i)(?:custom_name|displayname|display_name|lore|subtitle|title|tooltip)"
                    r"\s*[:=(]",
                    line,
                ):
                    visible_lines.append(number)
            row = {
                "path": path.relative_to(instance).as_posix(),
                "namespace_occurrences": dict(sorted(counts.items())),
                "visible_namespace_candidate_lines": visible_lines,
            }
            rows.append(row)
            if visible_lines:
                errors.append(f"{label}에 직접 표시 문구 후보가 있어요: {row}")
    errors.extend(str(value) for value in report["read_errors"])
    return report, errors


def assert_current_sources(catalog: dict[str, object]) -> list[str]:
    """원문 추출 뒤 JAR과 참조 자산이 바뀌지 않았는지 확인해요."""
    errors = []
    for row in catalog["jars"]:
        jar = find_jar(row["label"])
        if (
            row["jar"] != jar.name
            or row["jar_size"] != jar.stat().st_size
            or row["jar_mtime_ns"] != jar.stat().st_mtime_ns
        ):
            errors.append(f"{row['label']} JAR이 원문 추출 당시와 달라요")
    _, provenance = reference_phrases()
    if provenance != catalog["reference_sources"]:
        errors.append("Minecraft 또는 Create 참조 번역이 원문 추출 당시와 달라요")
    quest_source = Path(catalog["ftbquests"]["english_path"])
    if (
        not quest_source.is_file()
        or quest_source.stat().st_size != catalog["ftbquests"]["english_size"]
        or hashlib.sha256(quest_source.read_bytes()).hexdigest()
        != catalog["ftbquests"]["english_sha256"]
    ):
        errors.append("FTB Quests 영어 원문이 추출 당시와 달라요")
    return errors


def audit() -> tuple[dict[str, object], list[str]]:
    """세 JAR의 데이터·NBT·가이드와 외부 표시 경로를 감사해요."""
    catalog = load_json(WORK_ROOT / "source_surface_catalog.json")
    errors = assert_current_sources(catalog)
    summary = {}
    for row in catalog["jars"]:
        current = []
        if row["invalid_json"] or row["guide_candidates"]:
            current.append("데이터 또는 가이드 감사를 완료하지 못했어요")
        if row["data_direct_fields"]:
            current.append("직접 데이터 표시 문구가 있어요")
        if row["nbt_visible_fields"]:
            current.append("NBT 직접 표시 문구가 있어요")
        errors.extend(f"{row['label']}: {value}" for value in current)
        summary[row["label"]] = {
            "data_json_files": row["data_json_files"],
            "data_localized_fields": len(row["data_localized_fields"]),
            "localized_field_classification": (
                "silent_recipe_advancement_metadata"
                if row["data_localized_fields"]
                and all(
                    "/advancement/recipes/" in value["file"]
                    for value in row["data_localized_fields"]
                )
                else "none"
            ),
            "data_direct_fields": len(row["data_direct_fields"]),
            "nbt_files": row["nbt_files"],
            "nbt_visible_fields": len(row["nbt_visible_fields"]),
            "guide_candidates": len(row["guide_candidates"]),
        }
    references, reference_errors = audit_references()
    errors.extend(reference_errors)
    report = {
        "family": FAMILY,
        "jar_surfaces": summary,
        "references": references,
        "ftbquests_display_work": (
            "no_related_references"
            if not references["ftbquests"]
            else "item_ids_use_resourcepack_names"
        ),
        "kubejs_display_work": (
            "no_related_references"
            if not references["kubejs"]
            else "item_ids_use_resourcepack_names"
        ),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def verify_language() -> tuple[dict[str, object], list[str]]:
    """현재 영어와 작업본·산출물·이름 충돌을 함께 검증해요."""
    errors = []
    total = 0
    same = []
    no_hangul = []
    collapsed = {}
    by_mod = {}
    for label, (_, namespace) in JARS.items():
        english = read_language(label, "en_us")
        work = load_json(WORK_ROOT / f"{label}_ko_kr.json")
        output = load_json(OUTPUTS[namespace])
        total += len(english)
        if list(work) != list(english) or list(output) != list(english):
            errors.append(f"{label} 한국어 키 또는 순서가 현재 영어 원문과 달라요")
        if work != output:
            errors.append(f"{label} 작업 한국어와 리소스팩 산출물이 달라요")
        collisions = defaultdict(lambda: defaultdict(list))
        for key, source in english.items():
            target = output.get(key)
            if not isinstance(target, str):
                errors.append(f"문자열 한국어 값이 없어요: {key}")
                continue
            errors.extend(preserved_errors(key, source, target))
            if source == target:
                same.append(key)
            if not re.search(r"[가-힣]", target):
                no_hangul.append(key)
            if key.startswith(("block.", "item.")) or ".block." in key:
                collisions[target][source].append(key)
        unexpected = {
            target: dict(sources)
            for target, sources in collisions.items()
            if len(sources) > 1
        }
        if unexpected:
            collapsed[label] = unexpected
            errors.append(f"{label}에서 서로 다른 영어 이름이 합쳐졌어요")
        by_mod[label] = {
            "english_keys": len(english),
            "output_keys": len(output),
            "bundled_korean_candidate_keys": len(read_language(label, "ko_kr")),
            "collapsed_name_count": len(unexpected),
        }
    expected_same = ["itemGroup.chisel.chisel", "rechiseled.item_group"]
    if same != expected_same or no_hangul != expected_same:
        errors.append(
            "영어 유지값 검토 결과가 달라요: "
            f"same={same}, no_hangul={no_hangul}, expected={expected_same}"
        )
    report = {
        "reviewed_english_keys": total,
        "mods": by_mod,
        "existing_korean_values_reused": 0,
        "new_language_values": total,
        "intentional_same_keys": same,
        "collapsed_names": collapsed,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify_ftbquests() -> tuple[dict[str, object], list[str]]:
    """관련 FTB Quests 7개 키의 전체 재검수 결과를 확인해요."""
    english = quest_snbt.parse_language_snbt(
        resolve_source_root() / "config/ftbquests/quests/lang/en_us.snbt"
    )
    output = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    candidate = load_json(WORK_ROOT / "ftb_candidate_ko.json")
    work = load_json(WORK_ROOT / "ftb_ko.json")
    errors = []
    if not isinstance(candidate, dict) or not isinstance(work, dict):
        return {
            "errors": ["FTB Quests 작업 기록 형식이 올바르지 않아요"],
            "status": "incomplete",
        }, ["FTB Quests 작업 기록 형식이 올바르지 않아요"]
    if work != FTB_TRANSLATIONS:
        errors.append("FTB Quests 작업 기록이 검수된 번역표와 달라요")
    for key, target in FTB_TRANSLATIONS.items():
        if key not in english:
            errors.append(f"FTB Quests 영어 원문에 키가 없어요: {key}")
            continue
        errors.extend(quest_snbt.validate_value(key, english[key], target))
        if output.get(key) != target:
            errors.append(f"FTB Quests 산출물이 검수 번역과 달라요: {key}")
    kept = sum(candidate.get(key) == value for key, value in FTB_TRANSLATIONS.items())
    revised = sum(
        key in candidate and candidate[key] != value
        for key, value in FTB_TRANSLATIONS.items()
    )
    new = sum(key not in candidate for key in FTB_TRANSLATIONS)
    report = {
        "reviewed_keys": len(FTB_TRANSLATIONS),
        "existing_korean_values_reused": kept,
        "existing_korean_values_revised": revised,
        "new_values": new,
        "remaining": 0 if not errors else len(errors),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """언어·표시 표면과 적용 기록을 함께 검증해요."""
    catalog = load_json(WORK_ROOT / "source_surface_catalog.json")
    source_errors = assert_current_sources(catalog)
    language, language_errors = verify_language()
    quests, quest_errors = verify_ftbquests()
    surface, surface_errors = audit()
    errors = source_errors + language_errors + quest_errors + surface_errors
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = load_json(deployment_path) if deployment_path.is_file() else None
    report = {
        "family": FAMILY,
        "language": language,
        "ftbquest_validation": quests,
        "surface_audit": surface["status"],
        "ftbquests": surface["ftbquests_display_work"],
        "kubejs": surface["kubejs_display_work"],
        "output_files": DEPLOYMENT_PATHS,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    completion = {
        "family": FAMILY,
        "reviewed_language_keys": language["reviewed_english_keys"],
        "bundled_korean_candidate_keys": sum(
            row["bundled_korean_candidate_keys"] for row in language["mods"].values()
        ),
        "existing_korean_values_reused": 0,
        "new_language_values": language["new_language_values"],
        "ftbquests_reviewed_keys": quests["reviewed_keys"],
        "ftbquests_existing_values_reused": quests["existing_korean_values_reused"],
        "ftbquests_existing_values_revised": quests["existing_korean_values_revised"],
        "ftbquests_new_values": quests["new_values"],
        "ftbquests_work": surface["ftbquests_display_work"],
        "kubejs_work": surface["kubejs_display_work"],
        "output_files": DEPLOYMENT_PATHS,
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
    """적용 매니페스트의 백업·해시 결과를 완료 기록에 연결해요."""
    manifest_path = manifest_path.resolve()
    manifest = load_json(manifest_path)
    report_path = WORK_ROOT / "deployment_report.json"
    previous = load_json(report_path) if report_path.is_file() else None
    errors = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 매니페스트 상태가 완료가 아니에요")
    if manifest.get("java_processes"):
        errors.append(
            f"적용 당시 Java 프로세스가 있었어요: {manifest['java_processes']}"
        )
    targets = manifest.get("targets", [])
    if not isinstance(targets, list) or not targets:
        errors.append("적용 대상 기록이 없어요")
        targets = []
    summaries = []
    expected = set(DEPLOYMENT_PATHS)
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
        hash_verified = all(
            records.get(path, {}).get("source_sha256")
            == records.get(path, {}).get("after_sha256")
            for path in expected
        )
        if not hash_verified:
            errors.append("적용 후 네 산출물 중 해시가 다른 파일이 있어요")
        if target.get("unexpected_changes"):
            errors.append(f"예상 밖 적용 변경이 있어요: {target['unexpected_changes']}")
        summaries.append(
            {
                "target_type": target.get("target_type"),
                "target_root": target.get("target_root"),
                "changed_paths": target.get("changed_paths", []),
                "unexpected_changes": target.get("unexpected_changes", []),
                "hash_verified": hash_verified,
            }
        )
    try:
        manifest_name = manifest_path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        manifest_name = str(manifest_path)
    backup_manifests = []
    if isinstance(previous, dict):
        previous_manifests = previous.get("backup_manifests")
        if isinstance(previous_manifests, list):
            backup_manifests.extend(
                value for value in previous_manifests if isinstance(value, str)
            )
        elif isinstance(previous.get("backup_manifest"), str):
            backup_manifests.append(previous["backup_manifest"])
    if manifest_name not in backup_manifests:
        backup_manifests.append(manifest_name)
    report = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "backup_manifest": backup_manifests[0],
        "final_apply_manifest": manifest_name,
        "backup_manifests": backup_manifests,
        "expected_paths": DEPLOYMENT_PATHS,
        "targets": summaries,
        "errors": errors,
    }
    write_json(report_path, report)
    return report, errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("prepare", "build", "audit", "verify", "record-deployment")
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
