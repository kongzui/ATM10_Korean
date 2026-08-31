#!/usr/bin/env python3
"""YUNG's 구조물 시리즈의 현재 표시 문구를 번역하고 전체 표면을 검증해요."""

from __future__ import annotations

import argparse
import gzip
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from gateways_hellish_family import Tag, read_nbt
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

FAMILY = "yungs_structures"
WORK_ROOT = PROJECT_ROOT / "working/yungs_structures"
OUTPUT_ROOT = active_output_root() / "resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-Za-z]")
NUMBER = re.compile(r"(?<![A-Za-z§&])\d+(?:\.\d+)?")
URL = re.compile(r"https?://[^\s\]\[<>{}\"']+")
FOREIGN_SCRIPT = re.compile(r"[\u0600-\u06ff\u3040-\u30ff\u4e00-\u9fff]")
JSONC_LINE = re.compile(r"(?m)^\s*//.*(?:\r?\n|$)")
VISIBLE_DATA_KEYS = {
    "custom_name",
    "description",
    "item_name",
    "literal_text",
    "minecraft:custom_name",
    "minecraft:item_name",
    "text",
    "title",
}

JARS = {
    "yungsapi": {"jar": "YungsApi-*.jar", "namespace": None, "keys": 0},
    "betterdeserttemples": {
        "jar": "YungsBetterDesertTemples-*.jar",
        "namespace": "betterdeserttemples",
        "keys": 13,
    },
    "betterdungeons": {
        "jar": "YungsBetterDungeons-*.jar",
        "namespace": "betterdungeons",
        "keys": 86,
    },
    "betterendisland": {
        "jar": "YungsBetterEndIsland-*.jar",
        "namespace": "betterendisland",
        "keys": 13,
    },
    "betterjungletemples": {
        "jar": "YungsBetterJungleTemples-*.jar",
        "namespace": "betterjungletemples",
        "keys": 11,
    },
    "bettermineshafts": {
        "jar": "YungsBetterMineshafts-*.jar",
        "namespace": "bettermineshafts",
        "keys": 60,
    },
    "betterfortresses": {
        "jar": "YungsBetterNetherFortresses-*.jar",
        "namespace": "betterfortresses",
        "keys": 4,
    },
    "betteroceanmonuments": {
        "jar": "YungsBetterOceanMonuments-*.jar",
        "namespace": "betteroceanmonuments",
        "keys": 4,
    },
    "betterstrongholds": {
        "jar": "YungsBetterStrongholds-*.jar",
        "namespace": "betterstrongholds",
        "keys": 11,
    },
    "betterwitchhuts": {
        "jar": "YungsBetterWitchHuts-*.jar",
        "namespace": "betterwitchhuts",
        "keys": 4,
    },
    "yungsextras": {"jar": "YungsExtras-*.jar", "namespace": None, "keys": 0},
}

TEXT = {
    "YUNG's Better Desert Temples": "YUNG's Better Desert Temples",
    "Somewhere deep in the desert...": "사막 깊은 곳 어딘가에서...",
    "Eternal Slumber": "영원한 안식",
    "Slay the Pharaoh and free the Temple from his curse": (
        "파라오를 처치하고 사원을 저주에서 해방하세요"
    ),
    "An Ancient Tomb": "고대의 무덤",
    "Discover a Better Desert Temple": "개선된 사막 사원을 발견하세요",
    "Use /locate structure betterdeserttemples:desert_temple instead!": (
        "대신 /locate structure betterdeserttemples:desert_temple 명령을 사용하세요!"
    ),
    "Disable Vanilla Pyramids": "바닐라 사막 피라미드 비활성화",
    "Whether or not vanilla desert pyramids should be disabled.": (
        "바닐라 사막 피라미드를 비활성화할지 설정합니다."
    ),
    "Apply Mining Fatigue": "채굴 피로 적용",
    "Whether or not mining fatigue is applied to players in the temple": (
        "아직 공략하지 않은 사원 안의 플레이어에게"
    ),
    "if it has not yet been cleared.": "채굴 피로를 적용할지 설정합니다.",
    "Small Nether Dungeons are currently disabled by default. You can enable them in the mod's config.": (
        "작은 네더 던전은 현재 기본적으로 비활성화되어 있습니다. 모드 설정에서 활성화할 수 있습니다."
    ),
    "Foul Banner": "불결한 깃발",
    "Vengeful Banner": "복수의 깃발",
    "Haunted Banner": "유령 들린 깃발",
    "Banner of Decay": "부패의 깃발",
    "Banner of Pork": "돼지고기의 깃발",
    "Banner of Rage": "분노의 깃발",
    "YUNG's Better Dungeons": "YUNG's Better Dungeons",
    "Adventure awaits...": "모험이 기다립니다...",
    "Professional Dungeoneer": "전문 던전 탐험가",
    "Explore all of the Better Dungeons!": "개선된 던전을 모두 탐험하세요!",
    "Quite the Renovation": "제법 멋진 개조",
    "Find an upgraded Monster Room": "개선된 몬스터 방을 찾으세요",
    "A Bone to Pick": "따질 게 있어",
    "Enter a Fortress of the Undead": "언데드 요새에 들어가세요",
    "Cobweb Entanglement": "거미줄에 얽히다",
    "Discover a Spider Cave": "거미 동굴을 발견하세요",
    "When in Rome": "로마에 가면",
    "Set foot in a Catacomb": "지하 묘지에 발을 들이세요",
    "A Special Addition": "특별한 추가 요소",
    "Find a Small Nether Dungeon": "작은 네더 던전을 찾으세요",
    "General Settings": "일반 설정",
    "Zombie Dungeons": "좀비 던전",
    "Small Dungeons": "작은 던전",
    "Small Nether Dungeons": "작은 네더 던전",
    "Enable Skulls & Heads": "해골과 머리 활성화",
    "Whether or not dungeons should be allowed to place skeleton skulls and other mob heads.": (
        "던전에 스켈레톤 해골과 다른 몹 머리를 배치할 수 있게 할지 설정합니다."
    ),
    "This option may be useful for some modpack creators.": (
        "일부 모드팩 제작자에게 유용할 수 있는 설정입니다."
    ),
    "Default: true": "기본값: true",
    "Remove Vanilla Dungeons": "바닐라 던전 제거",
    "Whether or not vanilla dungeons should be prevented from spawning in the world.": (
        "월드에 바닐라 던전이 생성되지 않게 할지 설정합니다."
    ),
    "It is recommended to disable these, since the Small Dungeons are very similar in design.": (
        "작은 던전과 구조가 매우 비슷하므로 바닐라 던전을 비활성화하는 것을 권장합니다."
    ),
    "Enable Nether Blocks in Dungeons": "던전에 네더 블록 활성화",
    "Some dungeons can rarely spawn Nether-related blocks such as soul sand, soul campfires, and soul lanterns.": (
        "일부 던전에는 영혼 모래, 영혼 모닥불, 영혼 랜턴 같은 네더 관련 블록이 드물게 생성될 수 있습니다."
    ),
    "Note that the blocks will be purely decorative - nothing progression-breaking like Ancient Debris.": (
        "이 블록은 장식용일 뿐이며, 고대 잔해처럼 진행 순서를 무너뜨리는 블록은 생성되지 않습니다."
    ),
    "Set this to false to prevent any Nether-related blocks from spawning in dungeons.": (
        "던전에 네더 관련 블록이 생성되지 않게 하려면 false로 설정하세요."
    ),
    "Zombie Dungeon Surface Entrance Staircase Max Length": (
        "좀비 던전 지상 입구 계단 최대 길이"
    ),
    "The longest distance that can be checked when attempting to generate a surface entrance staircase.": (
        "지상 입구 계단을 생성할 때 확인할 수 있는 최대 거리입니다."
    ),
    "Making this too large may cause problems.": "값을 너무 크게 하면 문제가 생길 수 있습니다.",
    "Default: 20": "기본값: 20",
    "Small Dungeon Max Banner Count": "작은 던전 최대 깃발 수",
    "The maximum number of banners that can spawn in a single small dungeon.": (
        "작은 던전 하나에 생성될 수 있는 최대 깃발 수입니다."
    ),
    "Default: 2": "기본값: 2",
    "Small Dungeon Min Chest Count": "작은 던전 최소 상자 수",
    "The minimum number of chests that are guaranteed to spawn in a single small dungeon.": (
        "작은 던전 하나에 반드시 생성되는 최소 상자 수입니다."
    ),
    "Default: 1": "기본값: 1",
    "Small Dungeon Max Chest Count": "작은 던전 최대 상자 수",
    "The maximum number of chests that are guaranteed to spawn in a single small dungeon.": (
        "작은 던전 하나에 반드시 생성되는 최대 상자 수입니다."
    ),
    "Allow Ore Blocks in Corners": "모서리에 광석 블록 허용",
    "Whether or not Small Dungeons can rarely place ore blocks in the corners of the dungeon.": (
        "작은 던전의 모서리에 광석 블록을 드물게 배치할 수 있게 할지 설정합니다."
    ),
    "If this is set to false, any ore blocks that spawn as part of a corner prop will instead be replaced with air.": (
        "false로 설정하면 모서리 장식으로 생성되는 모든 광석 블록을 공기로 대체합니다."
    ),
    "Small Nether Dungeon Max Banner Count": "작은 네더 던전 최대 깃발 수",
    "The maximum number of banners that can spawn in a single small Nether dungeon.": (
        "작은 네더 던전 하나에 생성될 수 있는 최대 깃발 수입니다."
    ),
    "Enable Small Nether Dungeons": "작은 네더 던전 활성화",
    "Whether or not small Nether dungeons should spawn.": (
        "작은 네더 던전을 생성할지 설정합니다."
    ),
    "Wither Skeletons From Spawners Drop Skulls": (
        "생성기에서 나온 위더 스켈레톤의 해골 드롭"
    ),
    "Whether wither skeletons spawned from small Nether dungeons can drop wither skeleton skulls.": (
        "작은 네더 던전에서 생성된 위더 스켈레톤이 위더 스켈레톤 해골을 떨어뜨릴 수 있게 할지 설정합니다."
    ),
    "Blazes From Spawners Drop Blaze Rods": "생성기에서 나온 블레이즈의 블레이즈 막대 드롭",
    "Whether blazes spawned from small Nether dungeons have a chance to drop blaze rods.": (
        "작은 네더 던전에서 생성된 블레이즈가 블레이즈 막대를 떨어뜨릴 수 있게 할지 설정합니다."
    ),
    "YUNG's Better End Island": "YUNG's Better End Island",
    "Resummoned Dragon Drops Egg": "재소환한 드래곤의 알 드롭",
    "Whether the Ender Dragon drops an egg every time it's defeated": (
        "엔더 드래곤을 처치할 때마다 드래곤 알을 떨어뜨릴지 설정합니다"
    ),
    "Spawn Vanilla Obsidian Platform": "바닐라 흑요석 발판 생성",
    "Whether the vanilla obsidian platform should spawn in the End instead of the revamped platform": (
        "엔드에 개선된 발판 대신 바닐라 흑요석 발판을 생성할지 설정합니다"
    ),
    "Spawn Vanilla End Gateways": "바닐라 엔드 관문 생성",
    "Whether the vanilla End Gateways should spawn in the End instead of the revamped gateways": (
        "엔드에 개선된 관문 대신 바닐라 엔드 관문을 생성할지 설정합니다"
    ),
    "Play Bell Sound": "종소리 재생",
    "Whether the bell sound should play before the Ender Dragon is summoned for the first time and during re-summonings": (
        "엔더 드래곤을 처음 소환하기 전과 다시 소환하는 동안 종소리를 재생할지 설정합니다"
    ),
    "Spawn Central Tower Initially": "처음에 중앙 탑 생성",
    "Whether the central tower should spawn in the End when the world is first generated": (
        "월드를 처음 생성할 때 엔드에 중앙 탑을 생성할지 설정합니다"
    ),
    "Respawn Central Tower on Resummon": "재소환 시 중앙 탑 재생성",
    "Whether the central tower should respawn in the End when the Ender Dragon is re-summoned": (
        "엔더 드래곤을 다시 소환할 때 엔드에 중앙 탑을 재생성할지 설정합니다"
    ),
    "Use /locate structure betterjungletemples:jungle_temple instead!": (
        "대신 /locate structure betterjungletemples:jungle_temple 명령을 사용하세요!"
    ),
    "YUNG's Better Jungle Temples": "YUNG's Better Jungle Temples",
    "General": "일반",
    "Mod Compatibility": "모드 호환성",
    "Mod Compatibility Settings": "모드 호환성 설정",
    "Disable Vanilla Jungle Temples": "바닐라 정글 사원 비활성화",
    "Whether vanilla Jungle Temples should be disabled.": (
        "바닐라 정글 사원을 비활성화할지 설정합니다."
    ),
    "Enable Pick Your Poison Compatibility": "Pick Your Poison 호환성 활성화",
    "Whether PYP poison darts should spawn in Better Jungle Temples.": (
        "개선된 정글 사원에 PYP 독침이 생성될지 설정합니다."
    ),
    "Use /locate structure #bettermineshafts:better_mineshafts instead!": (
        "대신 /locate structure #bettermineshafts:better_mineshafts 명령을 사용하세요!"
    ),
    "YUNG's Better Mineshafts": "YUNG's Better Mineshafts",
    "Main Settings": "주요 설정",
    "Spawn Rates & More": "생성률 및 기타 설정",
    "Ore Deposits": "광상",
    "Minimum y-coordinate": "최소 Y 좌표",
    "The lowest the floor of a mineshaft can be.": "폐광 바닥이 생성될 수 있는 최저 높이입니다.",
    "Maximum y-coordinate": "최대 Y 좌표",
    "The highest the floor of a mineshaft can be.": "폐광 바닥이 생성될 수 있는 최고 높이입니다.",
    "Disable Vanilla Mineshafts": "바닐라 폐광 비활성화",
    "Whether or not vanilla mineshafts should be disabled.": (
        "바닐라 폐광을 비활성화할지 설정합니다."
    ),
    "Customize spawn rates for various mineshaft parts and decorations.": (
        "여러 폐광 부품과 장식의 생성률을 조정합니다."
    ),
    "Configure ore deposit spawn chances.": "광상 생성 확률을 설정합니다.",
    "MAKE SURE ALL THE VALUES ADD UP TO 100,": "모든 값을 더한 합이 반드시 100이어야 합니다.",
    "or things won't work the way you want them to!!": "그렇지 않으면 원하는 대로 작동하지 않습니다!!",
    "Lantern Spawn Rate": "랜턴 생성률",
    "The spawn rate for lanterns in the main shaft.": "주 갱도에 랜턴이 생성되는 비율입니다.",
    "Torch Spawn Rate": "횃불 생성률",
    "The spawn rate for torches in small shafts.": "작은 갱도에 횃불이 생성되는 비율입니다.",
    "Workstation Spawn Rate": "작업장 생성률",
    "The spawn rate for workstation side rooms along the main shaft.": (
        "주 갱도 옆에 작업장 방이 생성되는 비율입니다."
    ),
    "Workstation Cellar Spawn Rate": "작업장 지하실 생성률",
    "The spawn rate for workstation cellars below workstations along the main shaft.": (
        "주 갱도의 작업장 아래에 작업장 지하실이 생성되는 비율입니다."
    ),
    "Small Shaft Spawn Rate": "작은 갱도 생성률",
    "The spawn rate for smaller tunnels that generate along the main shaft.": (
        "주 갱도 옆에 작은 굴이 생성되는 비율입니다."
    ),
    "Cobweb Spawn Rate": "거미줄 생성률",
    "The spawn rate for cobwebs.": "거미줄이 생성되는 비율입니다.",
    "Small Shaft Chest Minecart Spawn Rate": "작은 갱도 상자 광산 수레 생성률",
    "The spawn rate for minecarts holding chests in small shafts.": (
        "작은 갱도에 상자를 실은 광산 수레가 생성되는 비율입니다."
    ),
    "Main Shaft Chest Minecart Spawn Rate": "주 갱도 상자 광산 수레 생성률",
    "The spawn rate for minecarts holding chests in the main shaft.": (
        "주 갱도에 상자를 실은 광산 수레가 생성되는 비율입니다."
    ),
    "Small Shaft TNT Minecart Spawn Rate": "작은 갱도 TNT 광산 수레 생성률",
    "The spawn rate for minecarts holding TNT in small shafts.": (
        "작은 갱도에 TNT를 실은 광산 수레가 생성되는 비율입니다."
    ),
    "Main Shaft TNT  Minecart Spawn Rate": "주 갱도 TNT 광산 수레 생성률",
    "The spawn rate for minecarts holding TNT in the main shaft.": (
        "주 갱도에 TNT를 실은 광산 수레가 생성되는 비율입니다."
    ),
    "Abandoned Miners' Outpost Spawn Rate": "버려진 광부 전초기지 생성률",
    "Percent chance of an Abandoned Miners' Outpost to spawn": (
        "작은 폐광 굴 끝에 버려진 광부 전초기지가"
    ),
    "at the end of a small mineshaft tunnel.": "생성될 백분율 확률입니다.",
    "Small Shaft Piece Chain Length": "작은 갱도 조각 연결 길이",
    'The number of "pieces" (e.g. straight, turn, etc) in a single small shaft.': (
        "작은 갱도 하나를 이루는 조각(직선, 회전 등)의 수입니다."
    ),
    "This determines the overall size of small shafts.": "작은 갱도의 전체 크기를 결정합니다.",
    "Enable Ore Deposits": "광상 활성화",
    "Cobble Spawn Chance (Empty deposit)": "조약돌 생성 확률(빈 광상)",
    "Percent chance of an ore deposit being cobblestone only.": (
        "광상이 조약돌로만 이루어질 백분율 확률입니다."
    ),
    "Coal Spawn Chance": "석탄 생성 확률",
    "Percent chance of an ore deposit containing coal.": "광상에 석탄이 포함될 백분율 확률입니다.",
    "Iron Spawn Chance": "철 생성 확률",
    "Percent chance of an ore deposit containing iron.": "광상에 철이 포함될 백분율 확률입니다.",
    "Redstone Spawn Chance": "레드스톤 생성 확률",
    "Percent chance of an ore deposit containing redstone.": (
        "광상에 레드스톤이 포함될 백분율 확률입니다."
    ),
    "Gold Spawn Chance": "금 생성 확률",
    "Percent chance of an ore deposit containing gold.": "광상에 금이 포함될 백분율 확률입니다.",
    "Lapis Spawn Chance": "청금석 생성 확률",
    "Percent chance of an ore deposit containing lapis.": (
        "광상에 청금석이 포함될 백분율 확률입니다."
    ),
    "Emerald Spawn Chance": "에메랄드 생성 확률",
    "Percent chance of an ore deposit containing emerald.": (
        "광상에 에메랄드가 포함될 백분율 확률입니다."
    ),
    "Diamond Spawn Chance": "다이아몬드 생성 확률",
    "Percent chance of an ore deposit containing diamond.": (
        "광상에 다이아몬드가 포함될 백분율 확률입니다."
    ),
    "Use /locate structure betterfortresses:fortress instead!": (
        "대신 /locate structure betterfortresses:fortress 명령을 사용하세요!"
    ),
    "YUNG's Better Nether Fortresses": "YUNG's Better Nether Fortresses",
    "Disable Vanilla Nether Fortresses": "바닐라 네더 요새 비활성화",
    "Whether vanilla Nether Fortresses should be disabled.": (
        "바닐라 네더 요새를 비활성화할지 설정합니다."
    ),
    "Use /locate structure betteroceanmonuments:ocean_monument instead!": (
        "대신 /locate structure betteroceanmonuments:ocean_monument 명령을 사용하세요!"
    ),
    "YUNG's Better Ocean Monuments": "YUNG's Better Ocean Monuments",
    "Disable Vanilla Ocean Monuments": "바닐라 해저 유적 비활성화",
    "Whether or not vanilla ocean monuments should be disabled.": (
        "바닐라 해저 유적을 비활성화할지 설정합니다."
    ),
    "Use /locate structure betterstrongholds:stronghold instead!": (
        "대신 /locate structure betterstrongholds:stronghold 명령을 사용하세요!"
    ),
    "YUNG's Better Strongholds": "YUNG's Better Strongholds",
    "General settings.": "일반 설정입니다.",
    "Enable Structure Ruin": "구조물 훼손 활성화",
    "Allows strongholds to be slightly destroyed by small noodle caves.": (
        "작은 구불구불한 동굴이 요새를 약간 훼손할 수 있게 합니다."
    ),
    "Note that they will remain unaffected by large caverns.": (
        "큰 동굴에는 영향을 받지 않습니다."
    ),
    "Filled Portal Frame Chance": "채워진 엔드 차원문 틀 확률",
    "The chance for each End Portal Frame block to spawn already filled with an Eye of Ender.": (
        "각 엔드 차원문 틀이 엔더의 눈으로 채워진 상태로 생성될 확률입니다."
    ),
    "YUNG's Better Witch Huts": "YUNG's Better Witch Huts",
    "Disable Vanilla Witch Huts": "바닐라 마녀 오두막 비활성화",
    "Whether or not vanilla witch huts should be disabled.": (
        "바닐라 마녀 오두막을 비활성화할지 설정합니다."
    ),
    "Use /locate structure betterwitchhuts:witch_hut instead!": (
        "대신 /locate structure betterwitchhuts:witch_hut 명령을 사용하세요!"
    ),
}

INTENTIONAL_SAME_VALUES = {value for source, value in TEXT.items() if source == value}

EXPECTED_JSONC = {
    (
        "betterjungletemples",
        "data/betterjungletemples/worldgen/template_pool/floor_1_room.json",
    ),
    (
        "betterjungletemples",
        "data/betterjungletemples/worldgen/template_pool/floor_2_pit.json",
    ),
    (
        "betterjungletemples",
        "data/betterjungletemples/worldgen/template_pool/floor_2_room.json",
    ),
    (
        "betterfortresses",
        "data/betterfortresses/worldgen/template_pool/bridge.json",
    ),
    (
        "betterfortresses",
        "data/betterfortresses/worldgen/template_pool/halls.json",
    ),
    (
        "betterfortresses",
        "data/betterfortresses/worldgen/template_pool/halls_terminators.json",
    ),
}

VISIBLE_NBT_STRING_NAMES = {
    "CustomName",
    "LastOutput",
    "Text1",
    "Text2",
    "Text3",
    "Text4",
    "author",
    "minecraft:custom_name",
    "raw",
    "title",
}
VISIBLE_NBT_LIST_NAMES = {"messages", "minecraft:lore"}


def find_jar(label: str) -> Path:
    """현재 설치본에서 지정한 YUNG's JAR 하나를 찾아요."""
    matches = sorted((resolve_source_root() / "mods").glob(str(JARS[label]["jar"])))
    if len(matches) != 1:
        raise FileNotFoundError(f"{label} JAR이 정확히 한 개가 아니에요: {matches}")
    return matches[0]


def read_language(label: str, locale: str) -> dict[str, str]:
    """현재 JAR의 언어 JSON 객체를 읽어요."""
    namespace = JARS[label]["namespace"]
    if not isinstance(namespace, str):
        return {}
    with ZipFile(find_jar(label)) as archive:
        internal = f"assets/{namespace}/lang/{locale}.json"
        if internal not in archive.namelist():
            return {}
        value = json.loads(archive.read(internal))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(text, str) for key, text in value.items()
    ):
        raise TypeError(f"{namespace} {locale} 언어 파일이 문자열 객체가 아니에요")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없는 JSON을 안정된 형식으로 기록해요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def prepare() -> dict[str, object]:
    """11개 설치 JAR과 9개 영어 언어 파일을 작업 폴더에 기록해요."""
    rows = []
    total = 0
    for label, metadata in JARS.items():
        jar = find_jar(label)
        english = read_language(label, "en_us")
        korean = read_language(label, "ko_kr")
        expected = int(metadata["keys"])
        if len(english) != expected:
            raise ValueError(
                f"{label} 영어 키 수가 달라요: {len(english)} != {expected}"
            )
        if english:
            write_json(WORK_ROOT / label / "en_us.json", english)
        if korean:
            write_json(WORK_ROOT / label / "bundled_ko_kr.json", korean)
        rows.append(
            {
                "label": label,
                "namespace": metadata["namespace"],
                "jar": jar.name,
                "jar_size": jar.stat().st_size,
                "jar_mtime_ns": jar.stat().st_mtime_ns,
                "english_keys": len(english),
                "bundled_korean_keys": len(korean),
            }
        )
        total += len(english)
    report = {
        "family": FAMILY,
        "jars": rows,
        "english_keys": total,
        "bundled_korean_candidate_keys": sum(
            int(row["bundled_korean_keys"]) for row in rows
        ),
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", report)
    return report


def translated_language(label: str) -> dict[str, str]:
    """현재 영어 원문 순서대로 확정 번역을 만들어요."""
    english = read_language(label, "en_us")
    missing_values = sorted(set(english.values()) - set(TEXT))
    if missing_values:
        raise KeyError(f"{label}에 번역하지 않은 원문이 있어요: {missing_values}")
    return {key: TEXT[source] for key, source in english.items()}


def build() -> dict[str, object]:
    """9개 네임스페이스의 영어 206키를 모두 번역해요."""
    used_values = set()
    rows = []
    errors = []
    for label, metadata in JARS.items():
        namespace = metadata["namespace"]
        if not isinstance(namespace, str):
            continue
        english = read_language(label, "en_us")
        try:
            korean = translated_language(label)
        except KeyError as exc:
            errors.append(str(exc))
            continue
        used_values.update(english.values())
        write_json(WORK_ROOT / label / "ko_kr.json", korean)
        write_json(OUTPUT_ROOT / namespace / "lang/ko_kr.json", korean)
        rows.append(
            {
                "label": label,
                "namespace": namespace,
                "translated_keys": len(korean),
                "status": "complete",
            }
        )
    unused_values = sorted(set(TEXT) - used_values)
    if unused_values:
        errors.append(f"현재 원문에서 쓰지 않는 번역표 값이 있어요: {unused_values}")
    report = {
        "family": FAMILY,
        "mods": rows,
        "translated_keys": sum(int(row["translated_keys"]) for row in rows),
        "errors": errors,
        "status": "complete" if not errors and len(rows) == 9 else "incomplete",
    }
    write_json(WORK_ROOT / "language_build.json", report)
    return report


def walk_json(value: object, path: str = "$") -> list[tuple[str, str, object]]:
    """JSON 안의 모든 키와 값을 경로와 함께 모아요."""
    rows = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            rows.append((key, child_path, child))
            rows.extend(walk_json(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(walk_json(child, f"{path}[{index}]"))
    return rows


def read_data_json(raw: bytes) -> tuple[object, bool]:
    """표준 JSON을 읽고, 필요한 경우 주석 줄만 제거한 JSONC도 읽어요."""
    text = raw.decode("utf-8-sig")
    try:
        return json.loads(text), False
    except json.JSONDecodeError:
        return json.loads(JSONC_LINE.sub("", text)), True


def visible_nbt_strings(
    tag: Tag,
    path: tuple[str | int, ...] = (),
    parent_name: str | None = None,
) -> list[dict[str, str]]:
    """구조물 NBT에서 책·표지판·이름처럼 직접 보일 수 있는 문자열을 모아요."""
    rows = []
    if tag.kind == 10:
        for name, child in tag.value.items():
            child_path = path + (name,)
            if (
                child.kind == 8
                and name in VISIBLE_NBT_STRING_NAMES
                and str(child.value).strip()
            ):
                rows.append(
                    {
                        "path": "/" + "/".join(map(str, child_path)),
                        "value": str(child.value),
                    }
                )
            rows.extend(visible_nbt_strings(child, child_path, name))
    elif tag.kind == 9:
        child_kind, children = tag.value
        if child_kind == 8 and parent_name in VISIBLE_NBT_LIST_NAMES:
            for index, child in enumerate(children):
                if str(child.value).strip():
                    rows.append(
                        {
                            "path": "/" + "/".join(map(str, path + (index,))),
                            "value": str(child.value),
                        }
                    )
        else:
            for index, child in enumerate(children):
                rows.extend(visible_nbt_strings(child, path + (index,), parent_name))
    return rows


def nbt_literal_text(value: str) -> str:
    """NBT 텍스트 컴포넌트에서 실제 직접 표시 문자열만 꺼내요."""
    try:
        component = json.loads(value)
    except json.JSONDecodeError:
        return value

    def collect(child: object) -> list[str]:
        if isinstance(child, str):
            return [child]
        if isinstance(child, list):
            return [text for item in child for text in collect(item)]
        if not isinstance(child, dict):
            return []
        rows = []
        if isinstance(child.get("text"), str):
            rows.append(child["text"])
        if "extra" in child:
            rows.extend(collect(child["extra"]))
        return rows

    return "".join(collect(component))


def audit_references(instance: Path) -> tuple[dict[str, object], list[str]]:
    """FTB Quests와 KubeJS에서 YUNG's 네임스페이스 참조를 확인해요."""
    errors = []
    report: dict[str, object] = {"ftbquests": [], "kubejs": [], "read_errors": []}
    namespaces = {
        str(metadata["namespace"])
        for metadata in JARS.values()
        if isinstance(metadata["namespace"], str)
    }
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
            lower = text.lower()
            counts = {
                namespace: lower.count(f"{namespace.lower()}:")
                for namespace in namespaces
            }
            if not any(counts.values()):
                continue
            visible_lines = []
            for number, line in enumerate(text.splitlines(), 1):
                line_lower = line.lower()
                if not any(
                    f"{namespace.lower()}:" in line_lower for namespace in namespaces
                ):
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
    read_errors = report["read_errors"]
    if isinstance(read_errors, list):
        errors.extend(str(message) for message in read_errors)
    return report, errors


def audit() -> tuple[dict[str, object], list[str]]:
    """11개 JAR의 데이터 JSON·NBT·가이드와 외부 참조를 전체 감사해요."""
    errors = []
    jar_reports = []
    found_jsonc = set()
    for label, metadata in JARS.items():
        jar = find_jar(label)
        namespace = metadata["namespace"]
        english = read_language(label, "en_us")
        data_json_files = []
        invalid_json = []
        jsonc_files = []
        localized_fields = []
        direct_fields = []
        guide_entries = []
        nbt_files = []
        nbt_visible_rows = []
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
                        value, used_jsonc = read_data_json(archive.read(name))
                    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                        invalid_json.append(f"{name}: {exc}")
                        continue
                    if used_jsonc:
                        jsonc_files.append(name)
                        found_jsonc.add((label, name))
                    for key, path, child in walk_json(value):
                        if key not in VISIBLE_DATA_KEYS:
                            continue
                        row = {"file": name, "path": path, "value": child}
                        if isinstance(child, dict) and isinstance(
                            child.get("translate"), str
                        ):
                            localized_fields.append(row)
                            translate_key = child["translate"]
                            if (
                                isinstance(namespace, str)
                                and translate_key.startswith(f"{namespace}.")
                                and translate_key not in english
                            ):
                                errors.append(
                                    f"{label} 데이터가 없는 번역 키를 참조해요: "
                                    f"{name} {translate_key}"
                                )
                        elif isinstance(child, str):
                            direct_fields.append(row)
                if not lower.endswith(".nbt"):
                    continue
                nbt_files.append(name)
                try:
                    compressed = archive.read(name)
                    try:
                        raw = gzip.decompress(compressed)
                    except gzip.BadGzipFile:
                        raw = compressed
                    _, root = read_nbt(raw)
                    for row in visible_nbt_strings(root):
                        literal = nbt_literal_text(row["value"])
                        if literal.strip():
                            nbt_visible_rows.append(
                                {"file": name, **row, "literal_text": literal}
                            )
                except (EOFError, OSError, UnicodeError, ValueError) as exc:
                    errors.append(f"{label} NBT를 읽지 못했어요: {name}: {exc}")
        latin_nbt = [
            row
            for row in nbt_visible_rows
            if re.search(r"[A-Za-z]", row["literal_text"])
        ]
        if invalid_json:
            errors.extend(f"{label}: {message}" for message in invalid_json)
        if direct_fields:
            errors.append(f"{label} 데이터에 직접 표시 문구가 있어요: {direct_fields}")
        if guide_entries:
            errors.append(f"{label} JAR에 별도 가이드 후보가 있어요: {guide_entries}")
        if latin_nbt:
            errors.append(f"{label} NBT에 번역할 라틴 문자 문구가 있어요: {latin_nbt}")
        jar_reports.append(
            {
                "label": label,
                "namespace": namespace,
                "jar": jar.name,
                "data_json_files": len(data_json_files),
                "localized_visible_fields": localized_fields,
                "direct_visible_fields": direct_fields,
                "jsonc_files": jsonc_files,
                "invalid_json": invalid_json,
                "nbt_files": len(nbt_files),
                "nbt_visible_fields": nbt_visible_rows,
                "nbt_latin_literal_fields": latin_nbt,
                "guide_candidates": guide_entries,
            }
        )
    missing_jsonc = sorted(EXPECTED_JSONC - found_jsonc)
    unexpected_jsonc = sorted(found_jsonc - EXPECTED_JSONC)
    if missing_jsonc or unexpected_jsonc:
        errors.append(
            "JSONC 파일 목록이 검수값과 달라요: "
            f"missing={missing_jsonc}, unexpected={unexpected_jsonc}"
        )
    references, reference_errors = audit_references(resolve_source_root())
    errors.extend(reference_errors)
    report = {
        "family": FAMILY,
        "jars": jar_reports,
        "jsonc_files": sorted(f"{label}:{name}" for label, name in found_jsonc),
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


def preserved_errors(label: str, source: str, target: str) -> list[str]:
    """자리표시자·서식·숫자·줄바꿈·URL 보존을 확인해요."""
    errors = []
    for name, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식 코드", FORMAT_CODE),
        ("숫자", NUMBER),
        ("URL", URL),
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


def verify_language() -> tuple[dict[str, object], list[str]]:
    """9개 모드 206키의 구조와 확정 번역값을 전부 검증해요."""
    errors = []
    mod_reports = []
    for label, metadata in JARS.items():
        namespace = metadata["namespace"]
        if not isinstance(namespace, str):
            continue
        english = read_language(label, "en_us")
        candidate = read_language(label, "ko_kr")
        expected = translated_language(label)
        work, work_errors = load_json_without_duplicates(
            WORK_ROOT / label / "ko_kr.json"
        )
        output, output_errors = load_json_without_duplicates(
            OUTPUT_ROOT / namespace / "lang/ko_kr.json"
        )
        current_errors = work_errors + output_errors
        if not isinstance(work, dict) or not isinstance(output, dict):
            errors.extend(f"{label}: {message}" for message in current_errors)
            continue
        if list(english) != list(work) or list(english) != list(output):
            current_errors.append("언어 키 또는 순서가 현재 영어 원문과 달라요")
        if work != output or output != expected:
            current_errors.append("작업본·산출물·확정 번역값이 서로 달라요")
        same_as_source = set()
        no_hangul = set()
        foreign_script = {}
        empty_values = []
        for key, source in english.items():
            target = output.get(key)
            if not isinstance(target, str):
                current_errors.append(f"문자열이 아닌 번역값이 있어요: {key}")
                continue
            current_errors.extend(preserved_errors(key, source, target))
            if source and not target:
                empty_values.append(key)
            if source and source == target:
                same_as_source.add(key)
            if target and not re.search(r"[가-힣]", target):
                no_hangul.add(key)
            foreign = sorted(set(FOREIGN_SCRIPT.findall(target)))
            if foreign:
                foreign_script[key] = foreign
        expected_same = {
            key for key, source in english.items() if TEXT[source] == source
        }
        if same_as_source != expected_same:
            current_errors.append(
                "영어와 같은 값 검토 결과가 달라요: "
                f"missing={sorted(expected_same - same_as_source)}, "
                f"unexpected={sorted(same_as_source - expected_same)}"
            )
        unexpected_no_hangul = no_hangul - expected_same
        if unexpected_no_hangul:
            current_errors.append(
                f"한국어가 없는 값이 있어요: {sorted(unexpected_no_hangul)}"
            )
        if empty_values:
            current_errors.append(f"빈 번역값이 있어요: {empty_values}")
        if foreign_script:
            current_errors.append(f"한국어 외 문자권 문자가 남았어요: {foreign_script}")
        reused = sum(
            1 for key, target in output.items() if candidate.get(key) == target
        )
        mod_reports.append(
            {
                "label": label,
                "namespace": namespace,
                "keys": len(output),
                "expected_keys": metadata["keys"],
                "bundled_candidate_keys": len(candidate),
                "bundled_candidate_values_reused": reused,
                "new_or_corrected_values": len(output) - reused,
                "intentional_same_keys": sorted(same_as_source),
                "errors": current_errors,
                "status": "complete" if not current_errors else "incomplete",
            }
        )
        errors.extend(f"{label}: {message}" for message in current_errors)
    report = {
        "mods": mod_reports,
        "keys": sum(int(row["keys"]) for row in mod_reports),
        "expected_keys": sum(
            int(metadata["keys"])
            for metadata in JARS.values()
            if isinstance(metadata["namespace"], str)
        ),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def deployment_paths() -> set[str]:
    """이 모음이 실제 인스턴스에 적용할 정확한 상대 경로를 반환해요."""
    return {
        f"resourcepacks/ATM10_Korean/assets/{metadata['namespace']}/lang/ko_kr.json"
        for metadata in JARS.values()
        if isinstance(metadata["namespace"], str)
    }


def verify() -> tuple[dict[str, object], list[str]]:
    """언어 구조와 전체 표시 표면 감사를 함께 검증해요."""
    language, language_errors = verify_language()
    surface, surface_errors = audit()
    errors = language_errors + surface_errors
    report = {
        "family": FAMILY,
        "language": language,
        "surface_audit": surface["status"],
        "ftbquests": surface["ftbquests_display_work"],
        "kubejs": surface["kubejs_display_work"],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    reused = sum(
        int(row["bundled_candidate_values_reused"]) for row in language["mods"]
    )
    changed = sum(int(row["new_or_corrected_values"]) for row in language["mods"])
    translation_report = {
        "family": FAMILY,
        "reviewed_language_keys": language["keys"],
        "bundled_korean_candidate_keys": sum(
            int(row["bundled_candidate_keys"]) for row in language["mods"]
        ),
        "existing_korean_values_reused": reused,
        "new_or_corrected_language_values": changed,
        "ftbquests_work": surface["ftbquests_display_work"],
        "kubejs_work": surface["kubejs_display_work"],
        "status": report["status"],
    }
    write_json(WORK_ROOT / "translation_report.json", translation_report)
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = (
        json.loads(deployment_path.read_text(encoding="utf-8"))
        if deployment_path.is_file()
        else None
    )
    completion = {
        "family": FAMILY,
        "language_keys": language["keys"],
        "existing_korean_values_reused": reused,
        "new_or_corrected_translations": changed,
        "ftbquests_work": surface["ftbquests_display_work"],
        "kubejs_work": surface["kubejs_display_work"],
        "output_files": sorted(deployment_paths()),
        "surface_audit": surface["status"],
        "family_validation": report["status"],
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
    verification, verification_errors = verify()
    result = {
        "deployment": report,
        "verification": verification["status"],
        "status": "complete"
        if not errors and not verification_errors
        else "incomplete",
    }
    return result, errors + verification_errors


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
    return 0 if result["status"] in {"prepared", "complete"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
