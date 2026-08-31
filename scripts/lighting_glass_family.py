#!/usr/bin/env python3
"""조명·유리 장식 모음 5개의 전체 표시 문자열을 번역하고 검증해요."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

FAMILY = "lighting_glass"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"
QUEST_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
MODS = {
    "luminax": "luminax-*.jar",
    "simplylight": "simplylight-*.jar",
    "additional_lights": "additional_lights-*.jar",
    "glassential": "Glassential-*.jar",
    "connectedglass": "connectedglass-*.jar",
}
EXPECTED_COUNTS = {
    "luminax": 193,
    "simplylight": 192,
    "additional_lights": 157,
    "glassential": 151,
    "connectedglass": 120,
}
OUTPUTS = {mod_id: OUTPUT_ASSETS / mod_id / "lang/ko_kr.json" for mod_id in MODS}
DEPLOYMENT_PATHS = {
    f"resourcepacks/ATM10_Korean/assets/{mod_id}/lang/ko_kr.json" for mod_id in MODS
} | {"config/ftbquests/quests/lang/ko_kr.snbt"}
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[.]\d+)?")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")

COLORS = {
    "Black": "검은색",
    "Blue": "파란색",
    "Brown": "갈색",
    "Cyan": "청록색",
    "Gray": "회색",
    "Green": "초록색",
    "Light Blue": "하늘색",
    "Light Gray": "회백색",
    "Lime": "연두색",
    "Magenta": "자홍색",
    "Orange": "주황색",
    "Pink": "분홍색",
    "Purple": "보라색",
    "Red": "빨간색",
    "White": "하얀색",
    "Yellow": "노란색",
}
COLOR_SLUGS = {
    name.lower().replace(" ", "_"): target for name, target in COLORS.items()
}

LUMINAX_OBJECTS = {
    "block": "블록",
    "button": "버튼",
    "pressure_plate": "감압판",
    "slab": "반 블록",
    "stairs": "계단",
    "wall": "담장",
}

SIMPLY_COLORED = {
    "Dynamic {color} Edge Light (bottom)": "{color} 동적 가장자리 조명(아래)",
    "Dynamic {color} Edge Light (top)": "{color} 동적 가장자리 조명(위)",
    "Illuminant {color} Block": "{color} 발광 블록",
    "Illuminant {color} Block (Inverted)": "{color} 발광 블록(반전)",
    "Illuminant {color} Column": "{color} 발광 기둥",
    "Illuminant {color} Fixture": "{color} 발광 조명기구",
    "Illuminant {color} Panel": "{color} 발광 패널",
    "Illuminant {color} Rod": "{color} 발광 막대",
    "Illuminant {color} Slab": "{color} 발광 반 블록",
    "Simple {color} Light Bulb": "{color} 단순 전구",
}

SIMPLY_STATIC = {
    "Dynamic Edge Light (bottom)": "동적 가장자리 조명(아래)",
    "Dynamic Edge Light (top)": "동적 가장자리 조명(위)",
    "Follows walls around itself,": "주변 벽을 따라 이어지며,",
    "perfect for hallways.": "복도에 잘 어울립니다.",
    "Will morph depending on the blocks present around itself on placement.\n"
    "Shape will persist afterward, letting you make shapes using temporary blocks.": (
        "설치할 때 주변 블록에 맞춰 모양이 바뀝니다.\n"
        "그 뒤에는 모양이 유지되므로 임시 블록으로 원하는 형태를 만들 수 있습니다."
    ),
    "Illuminant Block": "발광 블록",
    "Illuminant Block(Inverted)": "발광 블록(반전)",
    "Simple light block,": "단순한 조명 블록이며,",
    "Activates by %s.": "%s 신호로 활성화됩니다.",
    "Deactivates by %s.": "%s 신호로 비활성화됩니다.",
    "Illuminant Column": "발광 기둥",
    "3 Block tall lamp post.": "높이가 3블록인 가로등입니다.",
    "Top block emits light.": "맨 위 블록에서 빛을 냅니다.",
    "Illuminant Fixture": "발광 조명기구",
    "Hangs from walls, or sticks to ceilings and floors.": (
        "벽에 걸거나 천장과 바닥에 붙일 수 있습니다."
    ),
    "Illuminant Panel": "발광 패널",
    "Simple LED panel light,": "단순한 LED 패널 조명이며,",
    "Place in any direction.": "어느 방향으로든 설치할 수 있습니다.",
    "Illuminant Rod": "발광 막대",
    "A simple rod of light.": "단순한 막대형 조명입니다.",
    "Can be placed in any direction.": "어느 방향으로든 설치할 수 있습니다.",
    "Illuminant Slab": "발광 반 블록",
    "Simple half-slab light,": "단순한 반 블록 조명이며,",
    "Simple Light Bulb": "단순 전구",
    "Just a simple light bulb,": "단순한 전구이며,",
    "place in any direction.": "어느 방향으로든 설치할 수 있습니다.",
    "Simply Light": "Simply Light",
    "Exit": "나가기",
    "East": "동쪽",
    "Facing": "방향",
    "North": "북쪽",
    "South": "남쪽",
    "West": "서쪽",
    "Shift": "Shift",
    "Simply Light Full block CTM": "Simply Light 전체 블록 CTM",
    "Redstone": "레드스톤",
    "Press <%s> for info.": "정보를 보려면 <%s> 키를 누르세요.",
}

ADDITIONAL_MATERIALS = {
    "acacia_planks": "아카시아나무 판자",
    "birch_planks": "자작나무 판자",
    "blackstone": "흑암",
    "cobblestone": "조약돌",
    "crimson_planks": "진홍빛 판자",
    "cut_sandstone": "깎인 사암",
    "dark_oak_planks": "짙은 참나무 판자",
    "diamond_block": "다이아몬드 블록",
    "end_stone": "엔드 돌",
    "end_stone_bricks": "엔드 석재 벽돌",
    "glass": "유리",
    "gold_block": "금 블록",
    "iron_block": "철 블록",
    "jungle_planks": "정글나무 판자",
    "magenta_wool": "자홍색 양털",
    "mossy_cobblestone": "이끼 낀 조약돌",
    "mossy_stone_bricks": "이끼 낀 석재 벽돌",
    "nether_bricks": "네더 벽돌",
    "oak_planks": "참나무 판자",
    "packed_ice": "꽁꽁 언 얼음",
    "pink_wool": "분홍색 양털",
    "polished_andesite": "윤나는 안산암",
    "polished_blackstone": "윤나는 흑암",
    "polished_diorite": "윤나는 섬록암",
    "polished_granite": "윤나는 화강암",
    "red_nether_bricks": "붉은 네더 벽돌",
    "sandstone": "사암",
    "smooth_stone": "매끄러운 돌",
    "spruce_planks": "가문비나무 판자",
    "stone": "돌",
    "stone_bricks": "석재 벽돌",
    "warped_planks": "뒤틀린 판자",
}

ADDITIONAL_STATIC = {
    "itemGroup.additional_lights": "Additional Lights",
    "additional_lights.txt.shift": ("§7정보를 보려면 <§3Shift§r§7> 키를 누르세요."),
    "additional_lights.txt.usage": "§6사용법:",
    "additional_lights.txt.tips": "§6팁:",
    "additional_lights.txt.item.soul_wand.rightclick": (
        "- §9우클릭:§r 영혼 불로 바꿉니다."
    ),
    "additional_lights.txt.item.soul_wand.lefthand": (
        "- §9보조 손에 들기:§r 설치한 조명에 자동으로 적용됩니다."
    ),
    "additional_lights.txt.item.soul_wand.piglin": (
        "- 피글린은 영혼 불을 두려워합니다. (횃불에는 적용되지 않습니다)"
    ),
    "additional_lights.txt.block.pedestal.rightclick": ("- §9우클릭:§r 불을 붙입니다."),
    "additional_lights.txt.block.pedestal.sneaking": (
        "- §9웅크리기:§r 불 없이 설치하며 신호를 받지 않습니다."
    ),
    "additional_lights.txt.block.pedestal.signals": ("- 레드스톤 신호를 지원합니다."),
    "item.additional_lights.soul_wand": "영혼 지팡이",
    "block.additional_lights.fire_for_fire_pit_l": "대형 화덕용 불",
    "block.additional_lights.fire_for_fire_pit_s": "화덕용 불",
    "block.additional_lights.fire_for_standing_torch_l": ("대형 스탠딩 횃불용 불"),
    "block.additional_lights.fire_for_standing_torch_s": "스탠딩 횃불용 불",
    "block.additional_lights.soul_fire_for_fire_pit_l": "대형 화덕용 영혼 불",
    "block.additional_lights.soul_fire_for_fire_pit_s": "화덕용 영혼 불",
    "block.additional_lights.soul_fire_for_standing_torch_l": (
        "대형 스탠딩 횃불용 영혼 불"
    ),
    "block.additional_lights.soul_fire_for_standing_torch_s": ("스탠딩 횃불용 영혼 불"),
}

GLASSENTIAL_WOODS = {
    "acacia": "아카시아나무",
    "bamboo": "대나무",
    "birch": "자작나무",
    "cherry": "벚나무",
    "crimson": "진홍빛",
    "dark_oak": "짙은 참나무",
    "jungle": "정글나무",
    "mangrove": "맹그로브나무",
    "oak": "참나무",
    "spruce": "가문비나무",
    "warped": "뒤틀린",
}

GLASSENTIAL_STATIC = {
    "Tinted Ethereal Glass": "차광 에테리얼 유리",
    "Tinted Reverse Ethereal Glass": "차광 역방향 에테리얼 유리",
    "Ethereal Glass": "에테리얼 유리",
    "Reverse Ethereal Glass": "역방향 에테리얼 유리",
    "Ghostly Glass": "유령 유리",
    "Luminous Glass": "발광 유리",
    "Tinted Luminous Glass": "차광 발광 유리",
    "Redstone Glass": "레드스톤 유리",
    "Tinted Redstone Glass": "차광 레드스톤 유리",
    "Stone Glass": "돌 유리",
    "Sandstone Glass": "사암 유리",
    "Obsidian Glass": "흑요석 유리",
    "Ice Glass": "얼음 유리",
    "Iron Glass": "철 유리",
    "Gravity Glass": "중력 유리",
    "One Way Glass": "단방향 유리",
    "Tinted One Way Glass": "차광 단방향 유리",
    "Clear Fluid Glass": "투명 유체 유리",
    "Clear Fluid Fake Glass": "가짜 투명 유체 유리",
    "Colorable Glass": "염색 가능 유리",
    "Colorable Stained Glass": "염색 가능 색유리",
    "Colorable Glass Pane": "염색 가능 유리판",
    "Colorable Stained Glass Pane": "염색 가능 색유리 판",
    "Lava Lamp": "용암 램프",
    "Tinted Lava Lamp": "차광 용암 램프",
    "Glowstone Lamp": "발광석 램프",
    "Glowstone Tinted lamp": "차광 발광석 램프",
    "Glass slab": "유리 반 블록",
    "Ethereal Glass Pane": "에테리얼 유리판",
    "Reverse Ethereal Glass Pane": "역방향 에테리얼 유리판",
    "Ghostly Glass Pane": "유령 유리판",
    "Luminous Glass Pane": "발광 유리판",
    "Tinted Luminous Glass Pane": "차광 발광 유리판",
    "Redstone Glass Pane": "레드스톤 유리판",
    "Tinted Redstone Glass Pane": "차광 레드스톤 유리판",
    "Tinted Ethereal Glass Pane": "차광 에테리얼 유리판",
    "Tinted Reverse Ethereal Glass Pane": "차광 역방향 에테리얼 유리판",
    "Glass Door": "유리 문",
    "Glass TrapDoor": "유리 다락문",
    "Iron Glass Door": "철 유리 문",
    "Iron Glass Trapdoor": "철 유리 다락문",
    "Tinted Glass Door": "차광 유리 문",
    "Tinted Glass Trapdoor": "차광 유리 다락문",
    "Ethereal Glass Door": "에테리얼 유리 문",
    "Ethereal Glass TrapDoor": "에테리얼 유리 다락문",
    "Ethereal Reverse Glass Door": "역방향 에테리얼 유리 문",
    "Ethereal Reverse Glass TrapDoor": "역방향 에테리얼 유리 다락문",
    "Ghostly Glass Door": "유령 유리 문",
    "Ghostly Glass TrapDoor": "유령 유리 다락문",
    "Luminous Glass Door": "발광 유리 문",
    "Luminous Glass TrapDoor": "발광 유리 다락문",
    "Redstone Glass Door": "레드스톤 유리 문",
    "Redstone Glass TrapDoor": "레드스톤 유리 다락문",
    "Obsidian Glass Door": "흑요석 유리 문",
    "Obsidian Glass TrapDoor": "흑요석 유리 다락문",
    "Tinted Ethereal Glass Door": "차광 에테리얼 유리 문",
    "Tinted Ethereal Glass TrapDoor": "차광 에테리얼 유리 다락문",
    "Tinted Reverse Ethereal Glass Door": "차광 역방향 에테리얼 유리 문",
    "Tinted Reverse Ethereal Glass TrapDoor": "차광 역방향 에테리얼 유리 다락문",
    "Blocks light": "빛을 막습니다.",
    "Not solid to players": "플레이어가 통과할 수 있습니다.",
    "Only solid to players": "플레이어에게만 고체로 작용합니다.",
    "Not solid to entities": "엔티티가 통과할 수 있습니다.",
    "Emits light": "빛을 냅니다.",
    "Emits a redstone signal": "레드스톤 신호를 냅니다.",
    "Resistant to explosions": "폭발에 강합니다.",
    "Ice in thermal glass, not melt": "단열 유리 속 얼음이라 녹지 않습니다.",
    "Softens the fall, no collision": "충돌 없이 낙하 충격을 줄입니다.",
    "A secret window. Transparent from one side, solid from the other.": (
        "한쪽에서는 투명하고 반대쪽에서는 막혀 있는 비밀 창입니다."
    ),
    "Right-click a face with any block to disguise that side.": (
        "아무 블록으로 한쪽 면을 우클릭하면 그 면을 위장합니다."
    ),
    "Removes the near-surface water face behind the glass for a crystal-clear view": (
        "유리 뒤 수면을 숨겨 물속을 선명하게 볼 수 있습니다."
    ),
    "Change color and properties with Glassential Brush": (
        "Glassential 브러시로 색상과 속성을 바꿀 수 있습니다."
    ),
    "Natural lantern, burns like magma": "마그마처럼 타오르는 천연 램프입니다.",
    "Blocks light a bit": "빛을 일부 막습니다.",
    "Frameless when inserted between blocks": (
        "블록 사이에 놓으면 테두리가 사라집니다."
    ),
    "Resistant to explosions, works like an iron door": (
        "폭발에 강하고 철문처럼 작동합니다."
    ),
    "Resistant to explosions, works like an iron trapdoor": (
        "폭발에 강하고 철 다락문처럼 작동합니다."
    ),
    "Glassential Brush": "Glassential 브러시",
    "Glassential Brush Tuning": "Glassential 브러시 조정",
    "Emit Light": "빛 방출",
    "Emit Redstone Signal": "레드스톤 신호 방출",
    "Pass Player": "플레이어 통과",
    "Pass All Entities": "모든 엔티티 통과",
    "Apply": "적용",
    "Color: %s": "색상: %s",
    "✦ Emits Light": "✦ 빛 방출",
    "⚡ Emits Redstone": "⚡ 레드스톤 신호 방출",
    "◯ Player Passthrough": "◯ 플레이어 통과",
    "◈ Entity Passthrough": "◈ 엔티티 통과",
    "Right-click to configure": "우클릭하여 설정",
    "Shift + right-click any block to copy its color": (
        "Shift를 누른 채 아무 블록이나 우클릭하여 색상 복사"
    ),
    "Color %s copied to brush": "%s 색상을 브러시에 복사했습니다.",
    "Couldn't copy a color from this block": "이 블록의 색상을 복사할 수 없습니다.",
    "Glassential Renewed - Functional": "Glassential Renewed - 기능성",
    "Glassential Renewed - Blocks": "Glassential Renewed - 블록",
}

CONNECTED_COLORED = {
    "Clear {color} Stained Glass": "투명 {color} 색유리",
    "Clear {color} Stained Glass Pane": "투명 {color} 색유리 판",
    "Connecting Tinted {color} Stained Glass": "연결 차광 {color} 색유리",
    "Connecting {color} Stained Glass": "연결 {color} 색유리",
    "Connecting {color} Stained Glass Pane": "연결 {color} 색유리 판",
    "Scratched {color} Stained Glass": "긁힌 {color} 색유리",
    "Scratched {color} Stained Glass Pane": "긁힌 {color} 색유리 판",
}

CONNECTED_STATIC = {
    "Connected Glass": "Connected Glass",
    "Clear Glass": "투명 유리",
    "Clear Glass Pane": "투명 유리판",
    "Connecting Glass": "연결 유리",
    "Connecting Glass Pane": "연결 유리판",
    "Connecting Tinted Glass": "연결 차광 유리",
    "Scratched Glass": "긁힌 유리",
    "Scratched Glass Pane": "긁힌 유리판",
}

QUEST_CORRECTIONS = {
    "quest.3EEF17C57375CC39.quest_desc": [
        "&lSimply Light&r는 만들기 쉽고 사용하기 간단한 조명을 추가합니다."
        "\\n\\n반전형은 레드스톤 신호 없이 켜지고, 레드스톤 신호를 받으면 꺼집니다."
        "\\n\\n여러 색상과 모양의 조명을 선택할 수 있습니다!"
    ],
    "quest.3EEF17C57375CC39.title": "&lSimply Light&r",
    "task.32CB6A7BC1AB644E.title": "Simply Light",
    "quest.72DB967E59EEA729.quest_desc": [
        "&3&lGlassential Renewed&r는 장식뿐 아니라 기능성 건축에도 매우 유용한 "
        "모드입니다! \\n일반 유리와 달리 각 유리에는 특별한 기능이 있으며, 아이템에 "
        "마우스를 올리면 설명을 확인할 수 있습니다!\\n\\n예를 들어 에테리얼 유리는 "
        "플레이어는 통과할 수 있지만 몹은 통과하지 못합니다. "
        "(9sky의 벌 돔에 사용했습니다!)"
    ],
    "quest.72DB967E59EEA729.title": "&3&lGlassential Renewed&r",
    "task.53A682560123F9B6.title": "Glassential Renewed",
    "quest.7DABD82393713B5A.quest_desc": [
        "&c&lLuminax&r는 아주 단순한 모드입니다. 색색의 조명을 좋아한다면 원하는 "
        "색상의 조명을 만들 수 있습니다. \\n\\n모든 조명은 질감이 없는 단색이며, "
        "계단, 반 블록, 심지어 감압판 같은 여러 모양으로 만들 수 있습니다! "
        "\\n\\n&l&cDy&6en&ea&ami&bcs&r 색상과도 연동됩니다!"
    ],
    "quest.7DABD82393713B5A.title": "&l&cLuminax",
    "task.022D9FAD58AEE2C8.title": "Luminax 블록",
}

RELATED_QUEST_IDS = {
    "3EEF17C57375CC39",
    "32CB6A7BC1AB644E",
    "72DB967E59EEA729",
    "53A682560123F9B6",
    "7DABD82393713B5A",
    "022D9FAD58AEE2C8",
}

ALLOWED_LATIN = {
    "Additional",
    "Connected",
    "CTM",
    "Glass",
    "Glassential",
    "LED",
    "Light",
    "Lights",
    "Luminax",
    "Renewed",
    "Shift",
    "Simply",
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽어요."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아니에요: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 읽기 쉬운 형태로 기록해요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    """파일 SHA-256을 계산해요."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_jars(instance: Path) -> dict[str, Path]:
    """현재 설치된 다섯 JAR을 하나씩 찾아요."""
    found = {}
    for mod_id, pattern in MODS.items():
        matches = sorted((instance / "mods").glob(pattern))
        if len(matches) != 1:
            raise FileNotFoundError(f"{mod_id} JAR 수가 1개가 아니에요: {matches}")
        found[mod_id] = matches[0]
    return found


def read_jar_language(jar: Path, mod_id: str, locale: str) -> dict[str, object]:
    """JAR의 지정 언어 파일을 읽어요."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read(f"assets/{mod_id}/lang/{locale}.json"))
    if not isinstance(value, dict):
        raise TypeError(f"JAR 언어 파일이 객체가 아니에요: {jar.name}:{locale}")
    return value


def normalize_color(source: str) -> tuple[str, str] | None:
    """영어 이름 속의 바닐라 색상을 템플릿으로 바꿔요."""
    for color in sorted(COLORS, key=len, reverse=True):
        pattern = re.compile(rf"\b{re.escape(color)}\b")
        if pattern.search(source):
            return pattern.sub("{color}", source), COLORS[color]
    return None


def translate_luminax(english: dict[str, object]) -> dict[str, str]:
    """Luminax 16색 밝은·은은한 조명 193키를 번역해요."""
    translated = {}
    pattern = re.compile(
        r"block[.]luminax[.](dim_)?([a-z_]+)_luminax_"
        r"(block|button|pressure_plate|slab|stairs|wall)"
    )
    for key, source in english.items():
        if key == "itemGroup.luminax" and source == "Luminax":
            translated[key] = "Luminax"
            continue
        match = pattern.fullmatch(key)
        if not match or not isinstance(source, str):
            raise KeyError(f"검수되지 않은 Luminax 키예요: {key}={source}")
        color = COLOR_SLUGS.get(match.group(2))
        if color is None:
            raise KeyError(f"검수되지 않은 Luminax 색상이에요: {key}")
        dim = "은은한 " if match.group(1) else ""
        translated[key] = f"{dim}{color} Luminax {LUMINAX_OBJECTS[match.group(3)]}"
    if len(translated) != EXPECTED_COUNTS["luminax"]:
        raise ValueError(f"Luminax 키 수가 달라요: {len(translated)}")
    return translated


def translate_simplylight(english: dict[str, object]) -> dict[str, str]:
    """Simply Light 블록·도움말·GUI 192키를 번역해요."""
    translated = {}
    for key, source in english.items():
        if not isinstance(source, str):
            raise TypeError(f"문자열이 아닌 Simply Light 값이에요: {key}")
        normalized = normalize_color(source)
        if normalized and normalized[0] in SIMPLY_COLORED:
            template, color = normalized
            translated[key] = SIMPLY_COLORED[template].format(color=color)
        elif source in SIMPLY_STATIC:
            translated[key] = SIMPLY_STATIC[source]
        else:
            raise KeyError(f"검수되지 않은 Simply Light 값이에요: {key}={source}")
    if len(translated) != EXPECTED_COUNTS["simplylight"]:
        raise ValueError(f"Simply Light 키 수가 달라요: {len(translated)}")
    return translated


def translate_additional_lights(english: dict[str, object]) -> dict[str, str]:
    """Additional Lights 전체 157키를 현재 바닐라 재료명으로 번역해요."""
    translated = {}
    block_prefixes = {
        "al_lamp_": "전등",
        "al_torch_": "횃불 장식",
        "fire_pit_s_": "화덕",
        "fire_pit_l_": "대형 화덕",
        "standing_torch_s_": "스탠딩 횃불",
        "standing_torch_l_": "대형 스탠딩 횃불",
    }
    for key, source in english.items():
        if key in ADDITIONAL_STATIC:
            translated[key] = ADDITIONAL_STATIC[key]
            continue
        if not isinstance(source, str) or not key.startswith(
            "block.additional_lights."
        ):
            raise KeyError(f"검수되지 않은 Additional Lights 키예요: {key}")
        name = key.removeprefix("block.additional_lights.")
        match = next(
            (
                (prefix, suffix)
                for prefix, suffix in block_prefixes.items()
                if name.startswith(prefix)
            ),
            None,
        )
        if match is None:
            raise KeyError(f"검수되지 않은 Additional Lights 블록이에요: {key}")
        prefix, object_name = match
        material = ADDITIONAL_MATERIALS.get(name.removeprefix(prefix))
        if material is None:
            raise KeyError(f"검수되지 않은 Additional Lights 재료예요: {key}")
        translated[key] = f"{material} {object_name}"
    if len(translated) != EXPECTED_COUNTS["additional_lights"]:
        raise ValueError(f"Additional Lights 키 수가 달라요: {len(translated)}")
    return translated


def translate_glassential(english: dict[str, object]) -> dict[str, str]:
    """Glassential Renewed 기능성 유리 151키를 번역해요."""
    translated = {}
    color_pattern = re.compile(r"block[.]glassential[.]([a-z_]+)_glass_(door|trapdoor)")
    for key, source in english.items():
        if not isinstance(source, str):
            raise TypeError(f"문자열이 아닌 Glassential 값이에요: {key}")
        match = color_pattern.fullmatch(key)
        if match and match.group(1) in COLOR_SLUGS:
            object_name = "유리 문" if match.group(2) == "door" else "유리 다락문"
            translated[key] = f"{COLOR_SLUGS[match.group(1)]} {object_name}"
            continue
        if match and match.group(1) in GLASSENTIAL_WOODS:
            object_name = "유리 문" if match.group(2) == "door" else "유리 다락문"
            translated[key] = f"{GLASSENTIAL_WOODS[match.group(1)]} {object_name}"
            continue
        target = GLASSENTIAL_STATIC.get(source)
        if target is None:
            raise KeyError(f"검수되지 않은 Glassential 값이에요: {key}={source}")
        translated[key] = target
    if len(translated) != EXPECTED_COUNTS["glassential"]:
        raise ValueError(f"Glassential 키 수가 달라요: {len(translated)}")
    return translated


def translate_connectedglass(english: dict[str, object]) -> dict[str, str]:
    """Connected Glass의 연결·투명·긁힌 유리 120키를 번역해요."""
    translated = {}
    for key, source in english.items():
        if not isinstance(source, str):
            raise TypeError(f"문자열이 아닌 Connected Glass 값이에요: {key}")
        normalized = normalize_color(source)
        if normalized and normalized[0] in CONNECTED_COLORED:
            template, color = normalized
            translated[key] = CONNECTED_COLORED[template].format(color=color)
        elif source in CONNECTED_STATIC:
            translated[key] = CONNECTED_STATIC[source]
        else:
            raise KeyError(f"검수되지 않은 Connected Glass 값이에요: {key}={source}")
    if len(translated) != EXPECTED_COUNTS["connectedglass"]:
        raise ValueError(f"Connected Glass 키 수가 달라요: {len(translated)}")
    return translated


TRANSLATORS = {
    "luminax": translate_luminax,
    "simplylight": translate_simplylight,
    "additional_lights": translate_additional_lights,
    "glassential": translate_glassential,
    "connectedglass": translate_connectedglass,
}


def prepare() -> dict[str, object]:
    """현재 다섯 JAR 영어와 내장 한국어 후보를 작업 폴더에 기록해요."""
    instance = resolve_source_root()
    jars = find_jars(instance)
    rows = []
    candidate_summary = {}
    for mod_id, jar in jars.items():
        english = read_jar_language(jar, mod_id, "en_us")
        with ZipFile(jar) as archive:
            languages = sorted(
                name
                for name in archive.namelist()
                if name.startswith(f"assets/{mod_id}/lang/") and name.endswith(".json")
            )
        ko_path = f"assets/{mod_id}/lang/ko_kr.json"
        bundled_korean = (
            read_jar_language(jar, mod_id, "ko_kr") if ko_path in languages else {}
        )
        write_json(WORK_ROOT / mod_id / "en_us.json", english)
        write_json(WORK_ROOT / mod_id / "candidate_ko_kr.json", bundled_korean)
        rows.append(
            {
                "mod_id": mod_id,
                "jar": jar.name,
                "jar_size": jar.stat().st_size,
                "jar_mtime_ns": jar.stat().st_mtime_ns,
                "english_keys": len(english),
                "bundled_languages": languages,
                "bundled_korean_keys": len(bundled_korean),
            }
        )
        candidate_summary[mod_id] = {
            "candidate_keys": len(bundled_korean),
            "missing_current_keys": len(set(english) - set(bundled_korean)),
            "extra_candidate_keys": len(set(bundled_korean) - set(english)),
        }
    inventory = {
        "family": FAMILY,
        "mods": rows,
        "english_keys": sum(row["english_keys"] for row in rows),
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", inventory)
    write_json(WORK_ROOT / "candidate_sources.json", candidate_summary)
    return inventory


def build_quests(instance: Path) -> dict[str, object]:
    """관련 퀘스트 9키를 현재 전체 한국어 언어 파일에 병합해요."""
    candidate_path = instance / "config/ftbquests/quests/lang/ko_kr.snbt"
    candidate = quest_snbt.parse_language_snbt(candidate_path)
    merge_source = QUEST_OUTPUT if QUEST_OUTPUT.is_file() else candidate_path
    merged = quest_snbt.merge_into_full_snbt(merge_source, QUEST_CORRECTIONS)
    QUEST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    merged_values = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    for key, expected in QUEST_CORRECTIONS.items():
        if merged_values.get(key) != expected:
            raise ValueError(f"퀘스트 병합 결과가 달라요: {key}")
    reused = sum(
        candidate.get(key) == value for key, value in QUEST_CORRECTIONS.items()
    )
    existing = sum(key in candidate for key in QUEST_CORRECTIONS)
    return {
        "reviewed_keys": len(QUEST_CORRECTIONS),
        "existing_korean_reused": reused,
        "existing_korean_corrected": existing - reused,
        "new_translations": len(QUEST_CORRECTIONS) - existing,
    }


def build() -> dict[str, object]:
    """다섯 모드 813키 전체와 관련 퀘스트 산출물을 만들어요."""
    reports = {}
    for mod_id, translator in TRANSLATORS.items():
        english = load_json(WORK_ROOT / mod_id / "en_us.json")
        candidate = load_json(WORK_ROOT / mod_id / "candidate_ko_kr.json")
        korean = translator(english)
        write_json(WORK_ROOT / mod_id / "ko_kr.json", korean)
        write_json(OUTPUTS[mod_id], korean)
        reused = sum(candidate.get(key) == value for key, value in korean.items())
        existing = sum(key in candidate for key in korean)
        reports[mod_id] = {
            "reviewed_keys": len(korean),
            "existing_korean_reused": reused,
            "existing_korean_corrected": existing - reused,
            "new_translations": len(korean) - existing,
        }
    quests = build_quests(resolve_source_root())
    report = {
        "family": FAMILY,
        "mods": reports,
        "reviewed_language_keys": sum(row["reviewed_keys"] for row in reports.values()),
        "existing_korean_reused": sum(
            row["existing_korean_reused"] for row in reports.values()
        ),
        "new_or_corrected_language_keys": sum(
            row["existing_korean_corrected"] + row["new_translations"]
            for row in reports.values()
        ),
        "quests": quests,
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def advancement_surfaces(
    jar: Path, english: dict[str, object]
) -> tuple[dict[str, object], list[str]]:
    """발전 과제의 직접 문구와 번역 키를 감사해요."""
    errors = []
    files = []
    translation_keys = []
    recipe_only_translation_keys = []
    direct_text = []
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            if "/advancement" not in name or not name.endswith(".json"):
                continue
            files.append(name)
            value = json.loads(archive.read(name))
            display = value.get("display") if isinstance(value, dict) else None
            if not isinstance(display, dict):
                continue
            recipe_only = (
                value.get("parent") == "minecraft:recipes/root"
                and display.get("show_toast") is False
                and display.get("announce_to_chat") is False
            )
            for field in ("title", "description"):
                component = display.get(field)
                if isinstance(component, dict) and isinstance(
                    component.get("translate"), str
                ):
                    key = component["translate"]
                    if recipe_only:
                        recipe_only_translation_keys.append(key)
                    else:
                        translation_keys.append(key)
                    if not recipe_only and key not in english:
                        errors.append(
                            f"발전 과제 번역 키가 영어 파일에 없어요: {name}:{key}"
                        )
                elif isinstance(component, str):
                    direct_text.append(f"{name}:{field}={component}")
    if direct_text:
        errors.append(f"발전 과제에 직접 영어 문구가 있어요: {direct_text}")
    return {
        "files": len(files),
        "translation_keys": translation_keys,
        "recipe_only_translation_keys": recipe_only_translation_keys,
        "direct_text": direct_text,
    }, errors


def audit_references(instance: Path) -> dict[str, object]:
    """FTB Quests·KubeJS의 다섯 네임스페이스 참조를 모아요."""
    references = {"ftbquests": [], "kubejs": [], "read_errors": []}
    for label, base in (
        ("ftbquests", instance / "config/ftbquests/quests/chapters"),
        ("kubejs", instance / "kubejs"),
    ):
        for path in sorted(base.rglob("*"), key=lambda item: item.as_posix().lower()):
            if not path.is_file() or path.suffix.lower() not in {
                ".js",
                ".json",
                ".snbt",
            }:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                references["read_errors"].append(
                    f"{path.relative_to(instance).as_posix()}: {exc}"
                )
                continue
            namespaces = [mod_id for mod_id in MODS if mod_id in text.lower()]
            if namespaces:
                references[label].append(
                    {
                        "path": path.relative_to(instance).as_posix(),
                        "namespaces": namespaces,
                        "custom_name_literals": text.count('"minecraft:custom_name"'),
                    }
                )
    return references


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR 표시 표면과 퀘스트·KubeJS 참조를 감사해요."""
    instance = resolve_source_root()
    jars = find_jars(instance)
    errors = []
    advancements = {}
    for mod_id, jar in jars.items():
        english = read_jar_language(jar, mod_id, "en_us")
        report, report_errors = advancement_surfaces(jar, english)
        advancements[mod_id] = report
        errors.extend(report_errors)
    references = audit_references(instance)
    errors.extend(str(value) for value in references["read_errors"])
    english_quests = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean_quests = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    related_keys = sorted(
        key
        for key in english_quests
        if any(identifier in key for identifier in RELATED_QUEST_IDS)
    )
    if set(related_keys) != set(QUEST_CORRECTIONS):
        errors.append(
            "관련 퀘스트 키 범위가 예상과 달라요: "
            f"{sorted(set(related_keys) ^ set(QUEST_CORRECTIONS))}"
        )
    for key, expected in QUEST_CORRECTIONS.items():
        if korean_quests.get(key) != expected:
            errors.append(f"관련 퀘스트 번역값이 달라요: {key}")
    building = (
        instance / "config/ftbquests/quests/chapters/building_tips.snbt"
    ).read_text(encoding="utf-8")
    filters = {
        "simplylight": (
            'id: "32CB6A7BC1AB644E"' in building and "or(mod(simplylight))" in building
        ),
        "glassential": (
            'id: "53A682560123F9B6"' in building and "or(mod(glassential))" in building
        ),
        "luminax": (
            'id: "022D9FAD58AEE2C8"' in building and "or(mod(luminax))" in building
        ),
    }
    if not all(filters.values()):
        errors.append(f"관련 스마트 필터 구조를 확인하지 못했어요: {filters}")
    productive = (
        instance / "config/ftbquests/quests/chapters/productive_bees.snbt"
    ).read_text(encoding="utf-8")
    reference_only_icon = (
        'id: "683B58B699D4D381"' in productive
        and 'id: "luminax:red_luminax_block"' in productive
    )
    if not reference_only_icon:
        errors.append("Productive Bees의 Luminax 아이콘 참조를 확인하지 못했어요")
    report = {
        "family": FAMILY,
        "advancements": advancements,
        "references": references,
        "related_quest_keys": related_keys,
        "smart_filter_tasks": filters,
        "productive_bees_luminax_reference_only_icon": reference_only_icon,
        "ftbquests_display_work": "complete",
        "kubejs_display_work": "aliases_and_recipe_ids_only",
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def validate_preserved(key: str, source: str, target: str) -> list[str]:
    """자리표시자·숫자·서식·줄바꿈 보존 여부를 확인해요."""
    errors = []
    for label, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("숫자", NUMBER),
        ("서식 코드", FORMAT_CODE),
    ):
        if pattern.findall(source) != pattern.findall(target):
            errors.append(f"{label} 불일치: {key}")
    if source.count("\\n") != target.count("\\n"):
        errors.append(f"이스케이프 줄바꿈 불일치: {key}")
    if source.count("\n") != target.count("\n"):
        errors.append(f"실제 줄바꿈 불일치: {key}")
    return errors


def verify_mod(mod_id: str, jar: Path) -> tuple[dict[str, object], list[str]]:
    """한 모드의 현재 영어와 작업본·산출물을 완전 대조해요."""
    errors = []
    jar_english = read_jar_language(jar, mod_id, "en_us")
    working_english = load_json(WORK_ROOT / mod_id / "en_us.json")
    korean = load_json(WORK_ROOT / mod_id / "ko_kr.json")
    output = load_json(OUTPUTS[mod_id])
    expected = TRANSLATORS[mod_id](jar_english)
    if jar_english != working_english:
        errors.append(f"{mod_id} 작업 영어가 현재 JAR과 달라요")
    if list(jar_english) != list(korean):
        errors.append(f"{mod_id} 한국어 키 또는 순서가 영어와 달라요")
    if korean != output or korean != expected:
        errors.append(f"{mod_id} 작업본·산출물·확정 번역이 서로 달라요")
    intentional_same = {
        "itemGroup.luminax",
        "itemGroup.additional_lights",
        "connectedglass.item_group",
        "simplylight.key.shift",
        "itemGroup.simplylight",
    }
    untranslated = []
    latin_residue = {}
    collisions = defaultdict(list)
    for key in jar_english.keys() & korean.keys():
        source = jar_english[key]
        target = korean[key]
        if not isinstance(source, str) or not isinstance(target, str):
            errors.append(f"{mod_id} 문자열이 아닌 값이 있어요: {key}")
            continue
        errors.extend(validate_preserved(key, source, target))
        if source == target and key not in intentional_same:
            untranslated.append(key)
        stripped = PLACEHOLDER.sub("", FORMAT_CODE.sub("", target))
        residue = sorted(set(LATIN_WORD.findall(stripped)) - ALLOWED_LATIN)
        if residue:
            latin_residue[key] = residue
        if key.startswith(("block.", "item.")) and ".info" not in key:
            collisions[target].append(key)
    unexpected_collisions = {
        target: keys
        for target, keys in collisions.items()
        if len(keys) > 1 and len({jar_english[key] for key in keys}) > 1
    }
    if untranslated:
        errors.append(f"{mod_id} 영어 동일값이 남았어요: {untranslated}")
    if latin_residue:
        errors.append(f"{mod_id} 허용하지 않은 영문 잔여가 있어요: {latin_residue}")
    if unexpected_collisions:
        errors.append(f"{mod_id} 검색명이 충돌해요: {unexpected_collisions}")
    return {
        "keys": len(korean),
        "untranslated_candidates": untranslated,
        "latin_residue": latin_residue,
        "unexpected_name_collisions": unexpected_collisions,
        "errors": errors,
    }, errors


def verify_quests(instance: Path) -> tuple[dict[str, object], list[str]]:
    """관련 퀘스트 9키의 값과 보존 요소를 확인해요."""
    errors = []
    english = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    latin_residue = {}
    allowed = {
        "Dyenamics",
        "Glassential",
        "Luminax",
        "Renewed",
        "Simply",
        "Light",
        "sky",
    }
    for key, expected in QUEST_CORRECTIONS.items():
        if korean.get(key) != expected:
            errors.append(f"퀘스트 번역값이 달라요: {key}")
            continue
        errors.extend(quest_snbt.validate_value(key, english[key], expected))
        text = "\n".join(expected) if isinstance(expected, list) else expected
        stripped = PLACEHOLDER.sub("", FORMAT_CODE.sub("", text.replace("\\n", " ")))
        residue = sorted(set(LATIN_WORD.findall(stripped)) - allowed)
        if residue:
            latin_residue[key] = residue
    if latin_residue:
        errors.append(f"퀘스트에 허용하지 않은 영문 잔여가 있어요: {latin_residue}")
    return {
        "keys": len(QUEST_CORRECTIONS),
        "latin_residue": latin_residue,
        "errors": errors,
    }, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """다섯 모드·퀘스트·표면 감사 결과를 함께 검증해요."""
    instance = resolve_source_root()
    jars = find_jars(instance)
    mod_reports = {}
    errors = []
    for mod_id, jar in jars.items():
        report, report_errors = verify_mod(mod_id, jar)
        mod_reports[mod_id] = report
        errors.extend(report_errors)
    quests, quest_errors = verify_quests(instance)
    errors.extend(quest_errors)
    audit_report = load_json(WORK_ROOT / "surface_audit.json")
    audit_errors = audit_report.get("errors", [])
    if isinstance(audit_errors, list):
        errors.extend(str(value) for value in audit_errors)
    report = {
        "family": FAMILY,
        "mods": mod_reports,
        "language_keys": sum(row["keys"] for row in mod_reports.values()),
        "quests": quests,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = load_json(deployment_path) if deployment_path.is_file() else None
    completion = {
        "family": FAMILY,
        "language_keys": report["language_keys"],
        "quest_keys": quests["keys"],
        "surface_audit": audit_report.get("status"),
        "family_validation": report["status"],
        "deployment": deployment,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_completion.json", completion)
    return report, errors


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 스크립트의 백업·해시 결과를 완료 기록에 반영해요."""
    resolved = manifest_path.resolve()
    try:
        relative_manifest = resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        relative_manifest = str(resolved)
    manifest = load_json(resolved)
    errors = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 매니페스트가 완료 상태가 아니에요")
    if manifest.get("java_processes"):
        errors.append(f"적용 당시 Java 프로세스가 있어요: {manifest['java_processes']}")
    targets = manifest.get("targets")
    if not isinstance(targets, list) or not targets:
        errors.append("적용 대상 기록이 없어요")
        targets = []
    summarized = []
    for target in targets:
        if not isinstance(target, dict):
            errors.append("적용 대상 기록 형식이 잘못됐어요")
            continue
        records = {
            value.get("relative_path"): value
            for value in target.get("files", [])
            if isinstance(value, dict)
        }
        missing = sorted(DEPLOYMENT_PATHS - set(records))
        if missing:
            errors.append(f"적용 기록에 산출물이 없어요: {missing}")
        hash_errors = sorted(
            path
            for path in DEPLOYMENT_PATHS & set(records)
            if records[path].get("source_sha256") != records[path].get("after_sha256")
        )
        if hash_errors:
            errors.append(f"적용 후 해시가 달라요: {hash_errors}")
        if target.get("status") != "applied_and_verified":
            errors.append(
                f"적용 대상 상태가 완료가 아니에요: {target.get('target_root')}"
            )
        if target.get("unexpected_changes"):
            errors.append(
                f"예상 밖 적용 변경이 있어요: {target.get('unexpected_changes')}"
            )
        summarized.append(
            {
                "target_type": target.get("target_type"),
                "target_root": target.get("target_root"),
                "changed_paths": target.get("changed_paths", []),
                "unexpected_changes": target.get("unexpected_changes", []),
                "hash_verified_paths": sorted(
                    path
                    for path in DEPLOYMENT_PATHS & set(records)
                    if records[path].get("source_sha256")
                    == records[path].get("after_sha256")
                ),
            }
        )
    report = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "backup_manifest": relative_manifest,
        "targets": summarized,
        "errors": errors,
    }
    write_json(WORK_ROOT / "deployment_report.json", report)
    verify_report, verify_errors = verify()
    return {
        "deployment": report,
        "verification": verify_report["status"],
    }, errors + verify_errors


def run_all() -> tuple[dict[str, object], list[str]]:
    """준비·생성·표면 감사·검증을 순서대로 실행해요."""
    prepared = prepare()
    built = build()
    audit_report, audit_errors = audit()
    verify_report, verify_errors = verify()
    errors = audit_errors + verify_errors
    return {
        "prepare": prepared,
        "build": built,
        "audit": audit_report,
        "verify": verify_report,
        "status": "complete" if not errors else "incomplete",
    }, errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "build", "audit", "verify", "record-deployment", "all"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    if args.command == "prepare":
        result = prepare()
    elif args.command == "build":
        result = build()
    elif args.command == "audit":
        result, errors = audit()
    elif args.command == "verify":
        result, errors = verify()
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        result, errors = record_deployment(args.manifest)
    else:
        result, errors = run_all()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
