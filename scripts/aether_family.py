#!/usr/bin/env python3
"""The Aether 본체와 직접 연동 표시 경로를 수동 재검수한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import aether_lore
import aether_quests
import five_family_goal as family_goal
import twilight_family
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/aether"
LANG_ROOT = WORK_ROOT / "aether"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"

# 현재 설치본의 영어 원문을 기준으로 확정한 The Aether 고유 용어예요.
TERM_REPLACEMENTS = (
    ("에더", "The Aether"),
    ("에테르", "The Aether"),
    ("스카이 루트", "스카이루트"),
    ("앰브로시움", "암브로슘"),
    ("그라비타이트", "그래비타이트"),
    ("제나이트", "자나이트"),
)

NAME_PHRASES = {
    "The Aether": "The Aether",
    "Aether": "The Aether",
    "Aether Loot": "The Aether 전리품",
    "Aether Portal": "The Aether 차원문",
    "Aether Portal Frame": "The Aether 차원문 틀",
    "Aether Dirt": "The Aether 흙",
    "Aether Dirt Path": "The Aether 흙길",
    "Aether Farmland": "The Aether 농지",
    "Aether Grass Block": "The Aether 잔디 블록",
    "Enchanted Aether Grass Block": "마법이 부여된 The Aether 잔디 블록",
    "Aerogel": "에어로젤",
    "Blue Aercloud": "푸른 에어클라우드",
    "Cold Aercloud": "차가운 에어클라우드",
    "Golden Aercloud": "황금 에어클라우드",
    "Skyroot": "스카이루트",
    "Skyroot Boat with Chest": "상자가 실린 스카이루트 보트",
    "Skyroot Bucket of Axolotl": "아홀로틀이 담긴 스카이루트 양동이",
    "Skyroot Bucket of Cod": "대구가 담긴 스카이루트 양동이",
    "Skyroot Bucket of Pufferfish": "복어가 담긴 스카이루트 양동이",
    "Skyroot Bucket of Salmon": "연어가 담긴 스카이루트 양동이",
    "Skyroot Bucket of Tadpole": "올챙이가 담긴 스카이루트 양동이",
    "Skyroot Bucket of Tropical Fish": "열대어가 담긴 스카이루트 양동이",
    "Holystone": "홀리스톤",
    "Ambrosium": "암브로슘",
    "Zanite": "자나이트",
    "Gravitite": "그래비타이트",
    "Enchanted Gravitite": "마법이 부여된 그래비타이트",
    "Icestone": "빙석",
    "Quicksoil": "퀵소일",
    "Angelic Stone": "천사석",
    "Light Angelic Stone": "빛나는 천사석",
    "Carved Stone": "조각된 돌",
    "Hellfire Stone": "지옥불 돌",
    "Light Hellfire Stone": "빛나는 지옥불 돌",
    "Sentry Stone": "센트리 돌",
    "Angelic Slab": "천사석 반 블록",
    "Angelic Stairs": "천사석 계단",
    "Angelic Wall": "천사석 담장",
    "Carved Slab": "조각된 돌 반 블록",
    "Carved Stairs": "조각된 돌 계단",
    "Carved Wall": "조각된 돌 담장",
    "Hellfire Slab": "지옥불 돌 반 블록",
    "Hellfire Stairs": "지옥불 돌 계단",
    "Hellfire Wall": "지옥불 돌 담장",
    "Frosted Ice": "서리 낀 얼음",
    "Unstable Obsidian": "불안정한 흑요석",
    "Golden Oak": "황금 참나무",
    "Crystal Fruit Leaves": "수정 열매 나뭇잎",
    "Crystal Leaves": "수정 나뭇잎",
    "Holiday Leaves": "축제 나뭇잎",
    "Decorated Holiday Leaves": "장식된 축제 나뭇잎",
    "Mossy Holystone": "이끼 낀 홀리스톤",
    "Aechor Plant": "에이코르 식물",
    "Aechor Petal": "에이코르 꽃잎",
    "Aerwhale": "에어웨일",
    "Aerbunny": "에어버니",
    "Sheepuff": "쉽퍼프",
    "Flying Cow": "날아다니는 소",
    "Blue Swet": "푸른 스웨트",
    "Golden Swet": "황금 스웨트",
    "Swet": "스웨트",
    "Moa": "모아",
    "Phyg": "피그",
    "Zephyr": "제피르",
    "Slider": "슬라이더",
    "Sentry": "센트리",
    "Valkyrie Queen": "발키리 여왕",
    "Valkyrie": "발키리",
    "Sun Spirit": "태양 정령",
    "Cockatrice": "코카트리스",
    "Mimic": "미믹",
    "Whirlwind": "회오리바람",
    "Evil Whirlwind": "사악한 회오리바람",
    "Cloud Minion": "구름 하수인",
    "Fire Minion": "불 하수인",
    "Cloud Crystal": "구름 수정",
    "Fire Crystal": "불 수정",
    "Ice Crystal": "얼음 수정",
    "Thunder Crystal": "천둥 수정",
    "Floating Block": "떠다니는 블록",
    "Floating %s": "떠다니는 %s",
    "Hammer Projectile": "망치 투사체",
    "Poison Needle": "독침",
    "Zephyr Snowball": "제피르 눈덩이",
    "TNT Present": "TNT 선물",
    "Neptune": "넵튠",
    "Phoenix": "피닉스",
    "Obsidian": "흑요석",
    "Golden Amber": "황금 호박",
    "Bronze Dungeon": "청동 던전",
    "Silver Dungeon": "은 던전",
    "Gold Dungeon": "황금 던전",
    "Bronze Key": "청동 열쇠",
    "Silver Key": "은 열쇠",
    "Gold Key": "황금 열쇠",
    "Dungeon Trap": "던전 함정",
    "Water": "물",
    "Crystal": "수정",
    "Dart": "다트",
    "Saddle": "안장",
    "Item": "아이템",
    "Gold Pendant": "금 펜던트",
    "Gold Ring": "금 반지",
    "Gravitite armor": "그래비타이트 갑옷",
    "Neptune armor": "넵튠 갑옷",
    "Obsidian armor": "흑요석 갑옷",
    "Phoenix armor": "피닉스 갑옷",
    "Sentry armor": "센트리 갑옷",
    "Valkyrie armor": "발키리 갑옷",
    "Zanite armor": "자나이트 갑옷",
    "Hammer": "망치",
    "Book of Lore": "전승의 책",
    "Altar": "제단",
    "Freezer": "냉동고",
    "Incubator": "부화기",
    "Sun Altar": "태양 제단",
    "Treasure Chest": "보물 상자",
    "Chest Mimic": "상자 미믹",
    "Life Shard": "생명 조각",
    "Healing Stone": "치유석",
    "Regeneration Stone": "재생석",
    "Nature Staff": "자연의 지팡이",
    "Cloud Staff": "구름 지팡이",
    "Hammer of Kingbdogz": "Kingbdogz의 망치",
    "Shield of Repulsion": "반발의 방패",
    "Iron Bubble": "철 공기방울",
    "Victory Medal": "승리의 메달",
    "Pig Slayer": "돼지 학살자",
    "Vampire Blade": "흡혈검",
    "Holy Sword": "성검",
    "Flaming Sword": "화염검",
    "Lightning Sword": "번개검",
    "Lightning Knife": "번개 칼",
    "Agility Cape": "민첩의 망토",
    "Invisibility Cloak": "투명 망토",
    "White Apple": "하얀 사과",
    "Blue Berry": "푸른 베리",
    "Enchanted Berry": "마법이 부여된 베리",
    "Candy Cane Sword": "사탕 지팡이 검",
    "Candy Cane": "사탕 지팡이",
    "Ginger Bread Man": "진저브레드 맨",
    "Remedy": "해독제",
    "Inebriation": "만취",
    "Black Moa Egg": "검은 모아 알",
    "Blue Moa Egg": "푸른 모아 알",
    "White Moa Egg": "하얀 모아 알",
    "Chainmail Gloves": "사슬 장갑",
    "Diamond Gloves": "다이아몬드 장갑",
    "Iron Gloves": "철 장갑",
    "Leather Gloves": "가죽 장갑",
    "Netherite Gloves": "네더라이트 장갑",
    "Golden Feather": "황금 깃털",
    "Ice Pendant": "얼음 펜던트",
    "Ice Ring": "얼음 반지",
    "Iron Pendant": "철 펜던트",
    "Iron Ring": "철 반지",
    "Blue Music Disc": "푸른 음반",
    "Valkyrie Music Disc": "발키리 음반",
    "Sepia Music Disc": "세피아 음반",
    "Super Music Disc": "슈퍼 음반",
    "Blackened Music Disc": "검게 그을린 음반",
    "Carved Music Disc": "조각된 음반",
    "Aether Armor & Accessories": "The Aether 갑옷 및 장신구",
    "Aether Building Blocks": "The Aether 건축 블록",
    "Aether Dungeon Blocks": "The Aether 던전 블록",
    "Aether Equipment & Utilities": "The Aether 장비 및 도구",
    "Aether Food & Drinks": "The Aether 음식 및 음료",
    "Aether Functional Blocks": "The Aether 기능 블록",
    "Aether Ingredients": "The Aether 재료",
    "Aether Natural Blocks": "The Aether 자연 블록",
    "Aether Redstone Blocks": "The Aether 레드스톤 블록",
    "Aether Spawn Eggs": "The Aether 생성 알",
    "Bronze Treasure Chest": "청동 보물 상자",
    "Silver Treasure Chest": "은 보물 상자",
    "Gold Treasure Chest": "황금 보물 상자",
    "Accessory": "장신구",
    "Cape": "망토",
    "Gloves": "장갑",
    "Pendant": "펜던트",
    "Ring": "반지",
    "Shield": "방패",
}

WORD_TRANSLATIONS = {
    "Boss Doorway": "보스 출입구",
    "Treasure Doorway": "보물방 출입구",
    "Locked": "잠긴",
    "Trapped": "함정",
    "Block of": "블록",
    "Ore": "광석",
    "Torch": "횃불",
    "Brick Slab": "벽돌 반 블록",
    "Brick Stairs": "벽돌 계단",
    "Brick Wall": "벽돌 담장",
    "Bricks": "벽돌",
    "Slab": "반 블록",
    "Stairs": "계단",
    "Wall": "담장",
    "Button": "버튼",
    "Pressure Plate": "압력판",
    "Glass Pane": "유리판",
    "Glass": "유리",
    "Bush Stem": "덤불 줄기",
    "Berry Bush": "베리 덤불",
    "Pillar Top": "기둥 꼭대기",
    "Pillar": "기둥",
    "Present": "선물",
    "Purple Flower": "보라색 꽃",
    "White Flower": "하얀 꽃",
    "Bed": "침대",
    "Bookshelf": "책장",
    "Door": "문",
    "Fence Gate": "울타리 문",
    "Fence": "울타리",
    "Hanging Sign": "매달린 표지판",
    "Leaves": "나뭇잎",
    "Log": "원목",
    "Planks": "판자",
    "Sapling": "묘목",
    "Sign": "표지판",
    "Trapdoor": "다락문",
    "Wood": "목재",
    "Stripped": "껍질 벗긴",
    "Spawn Egg": "생성 알",
    "Egg": "알",
    "Shard": "조각",
    "Blue Cape": "푸른 망토",
    "Red Cape": "붉은 망토",
    "White Cape": "하얀 망토",
    "Yellow Cape": "노란 망토",
    "Swet Cape": "스웨트 망토",
    "Valkyrie Cape": "발키리 망토",
    "Blue Gummy Swet": "푸른 스웨트 젤리",
    "Golden Gummy Swet": "황금 스웨트 젤리",
    "Dart Shooter": "다트 발사기",
    "Dart": "다트",
    "Poison": "독",
    "Golden": "황금",
    "Enchanted": "마법이 부여된",
    "Cold Parachute": "차가운 낙하산",
    "Golden Parachute": "황금 낙하산",
    "Parachute": "낙하산",
    "Helmet": "투구",
    "Chestplate": "흉갑",
    "Leggings": "각반",
    "Boots": "장화",
    "Axe": "도끼",
    "Hoe": "괭이",
    "Pickaxe": "곡괭이",
    "Shovel": "삽",
    "Sword": "검",
    "Lance": "창",
    "Bow": "활",
    "Gemstone": "보석",
    "Ball": "공",
    "Boat with Chest": "상자가 실린 보트",
    "Boat": "보트",
    "Bucket of Axolotl": "아홀로틀이 담긴 양동이",
    "Bucket of Cod": "대구가 담긴 양동이",
    "Bucket of Pufferfish": "복어가 담긴 양동이",
    "Bucket of Salmon": "연어가 담긴 양동이",
    "Bucket of Tadpole": "올챙이가 담긴 양동이",
    "Bucket of Tropical Fish": "열대어가 담긴 양동이",
    "Milk Bucket": "우유 양동이",
    "Poison Bucket": "독 양동이",
    "Powder Snow Bucket": "가루눈 양동이",
    "Remedy Bucket": "해독제 양동이",
    "Water Bucket": "물 양동이",
    "Bucket": "양동이",
    "Stick": "막대기",
    "Material": "재료",
    "Forest": "숲",
    "Grove": "수풀",
    "Meadow": "초원",
    "Woodland": "삼림",
}

ADVANCEMENTS = {
    "advancement.aether.aether_sleep": "마땅히 누릴 휴식",
    "advancement.aether.aether_sleep.desc": "마침내 The Aether에서 잠드세요.",
    "advancement.aether.black_moa": "날아 보자!",
    "advancement.aether.black_moa.desc": "검은 모아를 타세요.",
    "advancement.aether.blue_aercloud": "무한한 공간 저 너머로!",
    "advancement.aether.blue_aercloud.desc": "푸른 에어클라우드에서 튀어 오르세요.",
    "advancement.aether.bronze_dungeon": "보스답게!",
    "advancement.aether.bronze_dungeon.desc": "청동 던전의 보스를 처치하세요.",
    "advancement.aether.craft_altar": "마법을 믿나요?",
    "advancement.aether.craft_altar.desc": "제단을 제작하세요.",
    "advancement.aether.enchanted_gravitite": "분홍색이 새로운 파란색",
    "advancement.aether.enchanted_gravitite.desc": (
        "제단에서 마법이 부여된 그래비타이트를 만드세요."
    ),
    "advancement.aether.enter_aether": "적대적인 낙원",
    "advancement.aether.enter_aether.desc": "The Aether에 들어가세요.",
    "advancement.aether.gold_dungeon": "꺼져 버린 불꽃",
    "advancement.aether.gold_dungeon.desc": "황금 던전의 보스를 처치하세요.",
    "advancement.aether.gravitite_armor": "중력을 거슬러",
    "advancement.aether.gravitite_armor.desc": (
        "그래비타이트 갑옷 한 벌을 인벤토리에 갖추세요."
    ),
    "advancement.aether.hammer_loot": "신들의 힘",
    "advancement.aether.hammer_loot.desc": (
        "청동 던전에서 Kingbdogz의 망치를 얻으세요."
    ),
    "advancement.aether.ice_accessory": "시원한 보석!",
    "advancement.aether.ice_accessory.desc": ("냉동고와 빙석으로 장신구를 얼리세요."),
    "advancement.aether.icestone": "얼음처럼 차갑게",
    "advancement.aether.icestone.desc": "빙석을 얻으세요.",
    "advancement.aether.incubate_moa": "...부화할 때까지!",
    "advancement.aether.incubate_moa.desc": "모아를 부화시키세요.",
    "advancement.aether.lance_loot": "왕좌의 도전자",
    "advancement.aether.lance_loot.desc": (
        "청동 던전에서 발키리 창을 얻으세요. 이제 은 던전에 도전할 차례입니다!"
    ),
    "advancement.aether.loreception": "책 속의 책!",
    "advancement.aether.loreception.desc": "전승의 책 안에 전승의 책을 넣으세요.",
    "advancement.aether.mount_phyg": "피그가 날 때",
    "advancement.aether.mount_phyg.desc": "피그를 타고 날아 보세요!",
    "advancement.aether.obsidian_armor": "얼음 양동이 갑옷",
    "advancement.aether.obsidian_armor.desc": "흑요석 갑옷 한 벌을 인벤토리에 갖추세요.",
    "advancement.aether.obtain_egg": "모아가 부화하기 전에는...",
    "advancement.aether.obtain_egg.desc": "모아 알을 얻으세요.",
    "advancement.aether.obtain_petal": "아기 먹이",
    "advancement.aether.obtain_petal.desc": (
        "에이코르 식물에서 에이코르 꽃잎을 수확하세요."
    ),
    "advancement.aether.phoenix_armor": "불에 끄떡없음",
    "advancement.aether.phoenix_armor.desc": "황금 던전에서 피닉스 갑옷 한 부위를 얻으세요.",
    "advancement.aether.prevent_aechor_petal_spawning": "정원 돌보기",
    "advancement.aether.prevent_aechor_petal_spawning.desc": (
        "마법이 부여된 잔디에 꽃을 심어 에이코르 식물이 나타나지 않게 하세요."
    ),
    "advancement.aether.prevent_swet_spawning": "내 잔디밭에서 나가!",
    "advancement.aether.prevent_swet_spawning.desc": (
        "스웨트 깃발을 놓아 스웨트가 나타나지 않게 하세요."
    ),
    "advancement.aether.read_lore": "알면 알수록!",
    "advancement.aether.read_lore.desc": "전승의 책을 읽으세요.",
    "advancement.aether.regen_stone": "전투로 단련됨",
    "advancement.aether.regen_stone.desc": (
        "은 던전에서 재생석을 얻으세요. 마지막 던전이 기다립니다..."
    ),
    "advancement.aether.silver_dungeon": "왕좌에서 끌어내리다",
    "advancement.aether.silver_dungeon.desc": "은 던전의 보스를 처치하세요.",
    "advancement.aether.the_aether": "The Aether",
    "advancement.aether.the_aether.desc": "아직 죽지 않았습니다!",
    "advancement.aether.valkyrie_hoe": "약탈자의 후회",
    "advancement.aether.valkyrie_hoe.desc": (
        "은 던전을 정복했는데 얻은 건 이 바보 같은 괭이뿐입니다."
    ),
    "advancement.aether.valkyrie_loot": "날개를 얻을 자격",
    "advancement.aether.valkyrie_loot.desc": "은 던전에서 발키리 장비 한 부위를 얻으세요.",
    "advancement.aether.zanite": "이국적인 장비",
    "advancement.aether.zanite.desc": "자나이트 보석을 인벤토리에 넣으세요.",
    "advancement.aether.zephyr_hammer": "궁극의 제재 망치",
    "advancement.aether.zephyr_hammer.desc": (
        "Kingbdogz의 망치로 제피르를 처치하세요. 통쾌한 복수입니다!"
    ),
}

AETHER_CORE = {
    "aether.attribute.name.moa_max_jumps": "모아 최대 도약 횟수",
    "aether.banned_item": "이 환경에서는 %s을(를) 사용할 수 없습니다.",
    "aether.block.aether.swet_banner": "스웨트 깃발",
    "aether.bronze_treasure_chest_locked": "이 보물 상자는 청동 열쇠로 열어야 합니다.",
    "aether.configuration.Audio": "오디오",
    "aether.configuration.Audio.button": "설정",
    "aether.configuration.Audio.tooltip": "모드의 일부 오디오 기능을 조정하는 설정입니다.",
    "aether.configuration.Data Pack": "데이터 팩",
    "aether.configuration.Data Pack.button": "설정",
    "aether.configuration.Data Pack.tooltip": "일부 기본 데이터 팩의 활성화를 조정하는 설정입니다.",
    "aether.configuration.Gameplay": "게임플레이",
    "aether.configuration.Gameplay.button": "설정",
    "aether.configuration.Gameplay.tooltip": "모드의 게임플레이 방식에 영향을 주는 설정입니다.",
    "aether.configuration.Gui": "GUI",
    "aether.configuration.Gui.button": "설정",
    "aether.configuration.Gui.tooltip": "모드의 GUI를 조정하는 설정입니다.",
    "aether.configuration.Loot": "전리품",
    "aether.configuration.Loot.button": "설정",
    "aether.configuration.Loot.tooltip": "모드의 전리품에 영향을 주는 설정입니다.",
    "aether.configuration.Miscellaneous": "기타",
    "aether.configuration.Miscellaneous.button": "설정",
    "aether.configuration.Miscellaneous.tooltip": "다른 분류에 속하지 않는 설정입니다.",
    "aether.configuration.Modpack": "모드팩",
    "aether.configuration.Modpack.button": "설정",
    "aether.configuration.Modpack.tooltip": "모드팩 제작자에게 유용한 설정입니다.",
    "aether.configuration.Multiplayer": "멀티플레이",
    "aether.configuration.Multiplayer.button": "설정",
    "aether.configuration.Multiplayer.tooltip": "멀티플레이 서버용 설정입니다.",
    "aether.configuration.Rendering": "렌더링",
    "aether.configuration.Rendering.button": "설정",
    "aether.configuration.Rendering.tooltip": "모드의 일부 요소가 표시되는 방식을 바꾸는 설정입니다.",
    "aether.configuration.World Generation": "월드 생성",
    "aether.configuration.World Generation.button": "설정",
    "aether.configuration.World Generation.tooltip": "모드의 월드 생성에 영향을 주는 설정입니다.",
    "aether.configuration.section.aether.client.toml": "클라이언트 설정",
    "aether.configuration.section.aether.client.toml.title": "The Aether 클라이언트 설정",
    "aether.configuration.section.aether.common.toml": "공통 설정",
    "aether.configuration.section.aether.common.toml.title": "The Aether 공통 설정",
    "aether.configuration.section.aether.server.toml": "서버 설정",
    "aether.configuration.section.aether.server.toml.title": "The Aether 서버 설정",
    "aether.configuration.title": "The Aether 설정",
    "aether.dungeon.bronze_dungeon": "청동 던전",
    "aether.dungeon.gold_dungeon": "황금 던전",
    "aether.dungeon.silver_dungeon": "은 던전",
    "aether.gold_treasure_chest_locked": "이 보물 상자는 황금 열쇠로 열어야 합니다.",
    "aether.hammer_of_kingbdogz_cooldown": "재사용 대기시간",
    "aether.life_shard_limit": "생명 조각은 총 %s개까지만 사용할 수 있습니다.",
    "aether.loot": "The Aether 전리품",
    "aether.menu_title.minecraft_left": "Minecraft(왼쪽)",
    "aether.menu_title.the_aether": "The Aether",
    "aether.menu_title.the_aether_left": "The Aether(왼쪽)",
    "aether.pro_tips.line.aether.aerogel_explosion_resistance": (
        "에어로젤은 폭발에 강한 투명 블록입니다."
    ),
    "aether.pro_tips.line.aether.aether_day_length": (
        "The Aether의 하루는 지상의 하루보다 3배 깁니다."
    ),
    "aether.pro_tips.line.aether.altar_repairing": (
        "제단은 손상된 아이템을 수리하고 기존 아이템을 강화할 수 있습니다."
    ),
    "aether.pro_tips.line.aether.ambrosium_shard_fuel": (
        "암브로슘 조각은 제단의 훌륭한 연료입니다."
    ),
    "aether.pro_tips.line.aether.blue_aerclouds": (
        "푸른 에어클라우드는 탄성이 있어 몹을 아주 높이 띄웁니다."
    ),
    "aether.pro_tips.line.aether.champs": "챔프와 챔페트는 꽤 끝내줍니다.",
    "aether.pro_tips.line.aether.check_surroundings": "싸움을 시작하기 전에 항상 주변을 확인하세요.",
    "aether.pro_tips.line.aether.close_door": "외출할 때는 문을 닫으세요.",
    "aether.pro_tips.line.aether.cold_parachute_crafting": (
        "차가운 낙하산은 차가운 에어클라우드 블록 4개로 제작할 수 있습니다."
    ),
    "aether.pro_tips.line.aether.creepers": "크리퍼를 두려워하지 마세요.",
    "aether.pro_tips.line.aether.dart_shooter_crafting": (
        "다트 발사기는 스카이루트 판자와 황금 호박으로 제작할 수 있습니다."
    ),
    "aether.pro_tips.line.aether.darts_no_gravity": (
        "황금·독·마법 다트는 중력의 영향을 받지 않습니다."
    ),
    "aether.pro_tips.line.aether.difficulty": "쉬운 길이 더 재미있는 경우는 드뭅니다.",
    "aether.pro_tips.line.aether.dig_straight_down": "절대로 발밑을 곧장 파지 마세요.",
    "aether.pro_tips.line.aether.do_things": "무엇이든 하기 가장 좋은 때는 너무 늦기 전입니다.",
    "aether.pro_tips.line.aether.drops": "낙차가 너무 커 보인다면 아마 실제로도 큽니다.",
    "aether.pro_tips.line.aether.dungeon_rewards": (
        "던전에는 매우 강력하고 독특한 보상이 있을 수 있습니다."
    ),
    "aether.pro_tips.line.aether.dungeon_tiers": (
        "던전은 청동, 은, 황금 순으로 난이도가 나뉩니다."
    ),
    "aether.pro_tips.line.aether.enchant_blue_disk": (
        "일반 음반에 마법을 부여하면 푸른 음반으로 만들 수 있습니다."
    ),
    "aether.pro_tips.line.aether.enchanted_gravitite_crafting": (
        "마법이 부여된 그래비타이트로 갑옷과 도구를 만들 수 있습니다."
    ),
    "aether.pro_tips.line.aether.enchanted_gravitite_floating": (
        "마법이 부여된 그래비타이트는 신호를 받을 때만 위로 떠오릅니다."
    ),
    "aether.pro_tips.line.aether.expectations": "자리를 비운 동안 아무 일도 없을 거라고 생각하지 마세요.",
    "aether.pro_tips.line.aether.glowstone_portal_forming": (
        "발광석 틀에 물을 부으면 적대적인 낙원으로 가는 길이 열립니다."
    ),
    "aether.pro_tips.line.aether.golden_apples": (
        "황금 참나무 잎에서는 가끔 황금 사과가 떨어집니다."
    ),
    "aether.pro_tips.line.aether.golden_oak_amber": (
        "황금 참나무 원목에는 귀중한 황금 호박이 들어 있습니다."
    ),
    "aether.pro_tips.line.aether.golden_parachute_durability": (
        "황금 낙하산은 한 번이 아니라 20번 사용할 수 있습니다."
    ),
    "aether.pro_tips.line.aether.gravitite_armour_ability": (
        "그래비타이트 갑옷은 더 높이 뛰게 하고 낙하 피해를 막아 줍니다."
    ),
    "aether.pro_tips.line.aether.gravitite_ore_enchanting": (
        "그래비타이트 광석에 마법을 부여하면 마법이 부여된 그래비타이트가 됩니다."
    ),
    "aether.pro_tips.line.aether.gravitite_tool_ability": (
        "그래비타이트 도구로 블록을 우클릭하면 공중에 띄울 수 있습니다."
    ),
    "aether.pro_tips.line.aether.harvest_aechor_poison": (
        "스카이루트 양동이로 에이코르 식물의 독을 채취할 수 있습니다."
    ),
    "aether.pro_tips.line.aether.holystone_tool_ability": (
        "홀리스톤 도구는 가끔 암브로슘 조각을 만들어 냅니다."
    ),
    "aether.pro_tips.line.aether.icestone_freezing_blocks": (
        "빙석은 물을 얼음으로, 용암을 흑요석으로 얼립니다."
    ),
    "aether.pro_tips.line.aether.mimic_chest": (
        "The Aether의 일부 던전에는 상자 미믹으로 변하는 상자가 있습니다."
    ),
    "aether.pro_tips.line.aether.mining": "나중에 돌아와서 더 채굴해도 됩니다.",
    "aether.pro_tips.line.aether.moa_egg_incubation": (
        "모아 알을 부화기에 넣으면 아기 모아가 태어납니다."
    ),
    "aether.pro_tips.line.aether.moa_nature_staff": (
        "아기 모아를 자연의 지팡이로 우클릭하면 그 자리에 머뭅니다."
    ),
    "aether.pro_tips.line.aether.parachute_activation": (
        "섬에서 떨어지면 낙하산이 자동으로 펼쳐집니다."
    ),
    "aether.pro_tips.line.aether.phoenix_armor_submerging": (
        "피닉스 갑옷을 입고 물속에 들어가 보세요."
    ),
    "aether.pro_tips.line.aether.phyg_saddle": "날아다니는 돼지에 안장을 달면 탈것이 됩니다.",
    "aether.pro_tips.line.aether.portal_misclick": "차원문을 만들 때 잘못 클릭하지 않도록 조심하세요.",
    "aether.pro_tips.line.aether.quicksoil_sliding": (
        "퀵소일은 걷는 몹과 미끄러지는 아이템의 속도를 높입니다."
    ),
    "aether.pro_tips.line.aether.raw_meat": "생고기라도 고기가 없는 것보다는 낫습니다.",
    "aether.pro_tips.line.aether.remedy_bucket_enchanting": (
        "독 양동이에 마법을 부여하면 스카이루트 해독제 양동이를 얻을 수 있습니다."
    ),
    "aether.pro_tips.line.aether.respect": "모드 제작자를 항상 존중하세요.",
    "aether.pro_tips.line.aether.risk_taking": "집에서 멀리 떨어졌을 때 큰 위험을 감수하지 마세요.",
    "aether.pro_tips.line.aether.security": "개인 정보는 PayPal에만 넘기세요.",
    "aether.pro_tips.line.aether.sheepuff_puff": (
        "쉽퍼프는 가끔 털을 부풀려 공중에 뜹니다."
    ),
    "aether.pro_tips.line.aether.shelter": "흙으로 지은 피난처도 피난처입니다.",
    "aether.pro_tips.line.aether.skyroot_tool_ability": (
        "스카이루트 도구로 블록을 캐면 드롭이 두 배가 됩니다."
    ),
    "aether.pro_tips.line.aether.slimes": "슬라임은 존재합니다... 아마도요.",
    "aether.pro_tips.line.aether.spare_stack": "단축바에 여분의 블록 한 스택을 항상 두세요.",
    "aether.pro_tips.line.aether.the_game": "게임은 즐기려는 만큼 재미있어집니다.",
    "aether.pro_tips.line.aether.victory_medal_drop": (
        "발키리를 처치하면 승리의 메달을 떨어뜨립니다."
    ),
    "aether.pro_tips.line.aether.watch_your_step": "발밑을 조심하세요. 깊은 구덩이는 어디에나 있습니다.",
    "aether.pro_tips.line.aether.white_aerclouds": (
        "차가운 에어클라우드 위에 착지하면 낙하 피해를 받지 않습니다."
    ),
    "aether.pro_tips.line.aether.zanite_tool_ability": (
        "자나이트 도구는 많이 사용할수록 강해집니다."
    ),
    "aether.pro_tips.line.aether.zephyr_shooting": (
        "제피르가 쏘는 눈덩이는 플레이어를 섬 밖으로 밀어낼 만큼 강합니다."
    ),
    "aether.silver_treasure_chest_locked": "이 보물 상자는 은 열쇠로 열어야 합니다.",
    "aether.sun_altar.in_control": "태양 정령이 아직 이 차원을 지배하고 있습니다.",
    "aether.sun_altar.no_permission": "이것을 사용할 권한이 없습니다.",
    "aether.sun_altar.no_power": "태양 정령은 이 차원에 영향력을 행사할 수 없습니다.",
}

CONFIG_VALUES = {
    "Makes Blue Aerclouds have their wobbly sounds that play when bouncing on them": (
        "푸른 에어클라우드에서 튀어 오를 때 출렁이는 효과음을 재생합니다."
    ),
    "Disables the Aether's boss fight music, only works if 'Disables Aether music manager' is false": (
        "The Aether 보스전 음악을 끕니다. 'The Aether 음악 관리자 비활성화'가 꺼져 있을 때만 적용됩니다."
    ),
    "Disables the Aether's menu music in case another mod implements its own, only works if 'Disables Aether music manager' is false": (
        "다른 모드가 자체 메뉴 음악을 제공할 때 The Aether 메뉴 음악을 끕니다. 'The Aether 음악 관리자 비활성화'가 꺼져 있을 때만 적용됩니다."
    ),
    "Disables the menu music on the Aether world preview menu, only works if 'Disables Aether music manager' is false": (
        "The Aether 월드 미리보기 메뉴의 음악을 끕니다. 'The Aether 음악 관리자 비활성화'가 꺼져 있을 때만 적용됩니다."
    ),
    "Disables the Aether's internal music manager, if true, this overrides all other audio configs": (
        "The Aether의 내부 음악 관리자를 끕니다. 활성화하면 다른 모든 오디오 설정보다 우선합니다."
    ),
    "Disables the menu music on the vanilla world preview menu, only works if 'Disables Aether music manager' is false": (
        "바닐라 월드 미리보기 메뉴의 음악을 끕니다. 'The Aether 음악 관리자 비활성화'가 꺼져 있을 때만 적용됩니다."
    ),
    "Sets the maximum delay for the Aether's music manager to use if needing to reset the song delay outside the Aether": (
        "The Aether 밖에서 곡 재생 간격을 초기화할 때 음악 관리자가 사용할 최대 지연 시간을 설정합니다."
    ),
    "Sets the minimum delay for the Aether's music manager to use if needing to reset the song delay outside the Aether": (
        "The Aether 밖에서 곡 재생 간격을 초기화할 때 음악 관리자가 사용할 최소 지연 시간을 설정합니다."
    ),
    "Aligns the elements of the Aether menu to the left, only works if 'Align menu left with world preview' is set to false": (
        "The Aether 메뉴 요소를 왼쪽에 정렬합니다. '월드 미리보기에 맞춰 메뉴 왼쪽 정렬'이 꺼져 있을 때만 적용됩니다."
    ),
    "Aligns the elements of the vanilla menu to the left, only works if 'Align menu left with world preview' is set to false": (
        "바닐라 메뉴 요소를 왼쪽에 정렬합니다. '월드 미리보기에 맞춰 메뉴 왼쪽 정렬'이 꺼져 있을 때만 적용됩니다."
    ),
    "The x-coordinate of the accessories button in the accessories menu": "장신구 메뉴에 있는 장신구 버튼의 X 좌표입니다.",
    "The y-coordinate of the accessories button in the accessories menu": "장신구 메뉴에 있는 장신구 버튼의 Y 좌표입니다.",
    "The x-coordinate of the accessories button in the creative menu": "크리에이티브 메뉴에 있는 장신구 버튼의 X 좌표입니다.",
    "The y-coordinate of the accessories button in the creative menu": "크리에이티브 메뉴에 있는 장신구 버튼의 Y 좌표입니다.",
    "The x-coordinate of the accessories button in the inventory and accessories menus": (
        "인벤토리 및 장신구 메뉴에 있는 장신구 버튼의 X 좌표입니다."
    ),
    "The y-coordinate of the accessories button in the inventory and accessories menus": (
        "인벤토리 및 장신구 메뉴에 있는 장신구 버튼의 Y 좌표입니다."
    ),
    "Disables the Aether's accessories button from appearing in GUIs": "GUI에 The Aether 장신구 버튼이 나타나지 않게 합니다.",
    "Disables the Aether's Moa Skins button from appearing in GUIs": "GUI에 The Aether 모아 스킨 버튼이 나타나지 않게 합니다.",
    "Enables the overlay at the top of the screen for the Hammer of Kingbdogz' cooldown": (
        "화면 위쪽에 Kingbdogz의 망치 재사용 대기시간 오버레이를 표시합니다."
    ),
    "Makes the extra hearts given by life shards display as silver colored": "생명 조각으로 얻은 추가 하트를 은색으로 표시합니다.",
    "Adds random trivia and tips to the bottom of loading screens": "로딩 화면 아래쪽에 무작위 상식과 팁을 추가합니다.",
    "The x-coordinate of the layout of perks buttons when in the pause menu": "일시 정지 메뉴 특전 버튼 배치의 X 좌표입니다.",
    "The y-coordinate of the layout of perks buttons when in the pause menu": "일시 정지 메뉴 특전 버튼 배치의 Y 좌표입니다.",
    "Determines that menu elements will align left if the menu's world preview is active, if true, this overrides 'Align menu elements left'": (
        "메뉴의 월드 미리보기가 활성화되면 메뉴 요소를 왼쪽에 정렬합니다. 활성화하면 '메뉴 요소 왼쪽 정렬'보다 우선합니다."
    ),
    "The y-coordinate of the Ascending to the Aether and Descending from the Aether text in loading screens": (
        "로딩 화면의 'The Aether로 올라가는 중' 및 'The Aether에서 내려가는 중' 문구의 Y 좌표입니다."
    ),
    "Enables a direct join button for the official server": "공식 서버에 바로 접속하는 버튼을 활성화합니다.",
    "Removes warm-tinting of the lightmap in the Aether, giving the lighting a colder feel": (
        "The Aether 라이트맵의 따뜻한 색조를 없애 조명을 더 차갑게 보이게 합니다."
    ),
    "Disables the Aether's custom skybox in case you have a shader that is incompatible with custom skyboxes": (
        "사용 중인 셰이더가 사용자 지정 스카이박스와 호환되지 않을 때 The Aether의 사용자 지정 스카이박스를 끕니다."
    ),
    "Disables the cloud rendering in the Aether": "The Aether의 구름 렌더링을 끕니다.",
    "Enables a green-tinted sunrise and sunset in the Aether, similar to the original mod": (
        "원본 모드처럼 The Aether의 일출과 일몰에 녹색 색조를 적용합니다."
    ),
    "Changes Zephyr and Aerwhale rendering to use their old models from the b1.7.3 version of the mod": (
        "제피르와 에어웨일을 모드 b1.7.3 버전의 구형 모델로 렌더링합니다."
    ),
    "Sets the Aether Ruined Portals data pack to be added to new worlds automatically": (
        "새 월드에 The Aether 무너진 차원문 데이터 팩을 자동으로 추가합니다."
    ),
    "Sets the Aether Temporary Freezing data pack to be added to new worlds automatically": (
        "새 월드에 The Aether 임시 빙결 데이터 팩을 자동으로 추가합니다."
    ),
    "When the player enters the Aether, they are given a Book of Lore and Golden Parachutes as starting loot": (
        "플레이어가 The Aether에 들어가면 시작 전리품으로 전승의 책과 황금 낙하산을 줍니다."
    ),
    "Determines whether the Sun Spirit's dialogue when meeting him should play through every time you meet him": (
        "태양 정령을 만날 때마다 첫 만남 대화를 전부 재생할지 정합니다."
    ),
    "Moves the message for when a player attacks the Slider with an incorrect item to be above the hotbar instead of in chat": (
        "플레이어가 잘못된 아이템으로 슬라이더를 공격했을 때의 메시지를 채팅 대신 단축바 위에 표시합니다."
    ),
    "Determines if a message that links The Aether mod's Patreon should show": "The Aether 모드의 Patreon 링크 메시지를 표시할지 정합니다.",
    "On world creation, the player is given an Aether Portal Frame item to automatically go to the Aether with": (
        "월드를 만들 때 플레이어에게 The Aether 차원문 틀을 지급하여 바로 The Aether로 갈 수 있게 합니다."
    ),
    "Use the default accessories menu instead of the Aether's Accessories Menu. WARNING: Do not enable this without emptying your equipped accessories": (
        "The Aether 장신구 메뉴 대신 기본 장신구 메뉴를 사용합니다. 경고: 장착한 장신구를 모두 빼기 전에는 활성화하지 마세요."
    ),
    "Enables code and data pack features used for modifying Aether Portals when Immersive Portals is installed": (
        "Immersive Portals가 설치된 경우 The Aether 차원문을 수정하는 코드와 데이터 팩 기능을 활성화합니다."
    ),
    "Makes Berry Bushes and Bush Stems behave consistently with Sweet Berry Bushes": "베리 덤불과 덤불 줄기가 달콤한 열매 덤불과 같은 방식으로 작동하게 합니다.",
    "Determines the cooldown in ticks for the Cloud Staff's ability": "구름 지팡이 능력의 재사용 대기시간을 틱 단위로 정합니다.",
    "Makes Crystal Fruit Leaves behave consistently with Sweet Berry Bushes": "수정 열매 나뭇잎이 달콤한 열매 덤불과 같은 방식으로 작동하게 합니다.",
    "Ambrosium Shards can be eaten to restore a half heart of health": "암브로슘 조각을 먹으면 체력을 반 칸 회복합니다.",
    "Vanilla's beds will explode in the Aether": "The Aether에서 바닐라 침대가 폭발하게 합니다.",
    "Determines the cooldown in ticks for the Hammer of Kingbdogz's ability": "Kingbdogz의 망치 능력 재사용 대기시간을 틱 단위로 정합니다.",
    "Gummy Swets when eaten restore full health instead of full hunger": "스웨트 젤리를 먹으면 허기 대신 체력을 모두 회복합니다.",
    "Determines the limit of the amount of Life Shards a player can consume to increase their health": "플레이어가 체력을 늘리기 위해 사용할 수 있는 생명 조각의 최대 개수를 정합니다.",
    "Makes armor abilities depend on wearing the respective gloves belonging to an armor set": "갑옷 능력을 사용하려면 해당 세트의 장갑까지 착용해야 하게 합니다.",
    "Tools that aren't from the Aether will mine Aether blocks slower than tools that are from the Aether": (
        "The Aether에서 만든 것이 아닌 도구로 The Aether 블록을 캐면 "
        "The Aether 도구보다 느리게 채굴합니다."
    ),
    "Allows the Golden Feather to spawn in the Silver Dungeon loot table": "은 던전 전리품 목록에 황금 깃털이 나오게 합니다.",
    "Allows the Valkyrie Cape to spawn in the Silver Dungeon loot table": "은 던전 전리품 목록에 발키리 망토가 나오게 합니다.",
    "Prevents the Aether Portal from being created normally in the mod": "The Aether 차원문을 일반적인 방법으로 만들 수 없게 합니다.",
    "Removes eternal day so that the Aether has a normal daylight cycle even before defeating the Sun Spirit": "영원한 낮을 없애 태양 정령을 처치하기 전에도 The Aether에 일반적인 낮밤 주기가 흐르게 합니다.",
    "Prevents the player from falling back to the Overworld when they fall out of the Aether": "플레이어가 The Aether 아래로 떨어져도 오버월드로 돌아가지 않게 합니다.",
    "Sets the Aether's time cycle to be the same length as the Overworld's": "The Aether의 시간 주기를 오버월드와 같은 길이로 설정합니다.",
    "Sets the ID of the dimension that the Aether Portal will send the player to": "The Aether 차원문이 플레이어를 보낼 차원의 ID를 설정합니다.",
    "Sets the ID of the dimension that the Aether Portal will return the player to": "The Aether 차원문이 플레이어를 돌려보낼 차원의 ID를 설정합니다.",
    "Spawns the player in the Aether dimension; this is best enabled alongside other modpack configuration to avoid issues": "플레이어를 The Aether 차원에서 생성합니다. 문제를 피하려면 다른 모드팩 설정과 함께 활성화하는 것이 좋습니다.",
    "Syncs the Aether's time cycle to the Overworld's": "The Aether의 시간 주기를 오버월드와 동기화합니다.",
    "Makes the Invisibility Cloak more balanced in PVP by disabling equipment invisibility temporarily after attacks": "공격 후 장비 투명화를 잠시 해제해 PVP에서 투명 망토의 균형을 조정합니다.",
    "Sets the time in ticks that it takes for the player to become fully invisible again after attacking when wearing an Invisibility Cloak; only works with 'Balance Invisibility Cloak for PVP'": "투명 망토를 입고 공격한 뒤 다시 완전히 투명해질 때까지의 시간을 틱 단위로 정합니다. 'PVP용 투명 망토 균형 조정'과 함께 사용해야 합니다.",
    "Configures what dimensions are able to have their time changed by the Sun Altar": "태양 제단으로 시간을 바꿀 수 있는 차원을 설정합니다.",
    "Makes it so that only whitelisted users or anyone with permission level 4 can use the Sun Altar on a server": "서버에서 허용 목록의 사용자 또는 권한 레벨 4 이상인 사용자만 태양 제단을 사용하게 합니다.",
    "Determines whether Holiday Trees should always be able to generate when exploring new chunks in the Aether, if true, this overrides 'Generate Holiday Trees seasonally'": "The Aether의 새 청크를 탐험할 때 축제 나무가 항상 생성될 수 있게 합니다. 활성화하면 '축제 나무를 계절에 따라 생성'보다 우선합니다.",
    "Determines whether Holiday Trees should be able to generate during the time frame of December and January when exploring new chunks in the Aether, only works if 'Generate Holiday Trees always' is set to false": "12월과 1월에 The Aether의 새 청크를 탐험할 때 축제 나무가 생성될 수 있게 합니다. '축제 나무를 항상 생성'이 꺼져 있을 때만 적용됩니다.",
    "Determines whether the Aether should generate Tall Grass blocks on terrain or not": "The Aether 지형에 키 큰 잔디 블록을 생성할지 정합니다.",
}

EFFECTS_AND_JUKEBOX = {
    "effect.aether.inebriation": "만취",
    "effect.aether.inebriation.description": "지속 피해를 주고 무작위로 움직이게 합니다.",
    "effect.aether.remedy": "해독",
    "effect.aether.remedy.description": "만취를 치료하고 면역을 부여합니다.",
    "jukebox_song.aether.aether_tune": "Noisestorm - Aether Tune",
    "jukebox_song.aether.ascending_dawn": "Emile van Krieken - Ascending Dawn",
    "jukebox_song.aether.chinchilla": "RENREN - chinchilla",
    "jukebox_song.aether.high": "RENREN - high",
    "jukebox_song.aether.klepto": "sunsette - klepto",
    "jukebox_song.aether.sliders_wrath": "sunsette - Slider's Wrath",
}

GUI_VALUES = {
    "Customization": "꾸미기",
    "Moa Skins": "모아 스킨",
    "Ascending to the Aether": "The Aether로 올라가는 중",
    "Book": "책",
    "Item:": "아이템:",
    "Next": "다음",
    "Of Lore": "전승",
    "Prev.": "이전",
    "Hex Color": "16진수 색상",
    "Developer Glow Color": "개발자 광채 색상",
    "Developer Glow: OFF": "개발자 광채: 꺼짐",
    "Developer Glow: ON": "개발자 광채: 켜짐",
    "Halo Color": "후광 색상",
    "Player Halo: OFF": "플레이어 후광: 꺼짐",
    "Player Halo: ON": "플레이어 후광: 켜짐",
    "Save": "저장",
    "Undo": "되돌리기",
    "Descending from the Aether": "The Aether에서 내려가는 중",
    "Accessory Freezable": "얼릴 수 있는 장신구",
    "Enchanting": "마법 부여",
    "Repairing": "수리",
    "Ambrosium Enchanting": "암브로슘 마법 부여",
    "Blocked in Biomes:": "차단되는 생물 군계:",
    "Requires Biomes:": "필요한 생물 군계:",
    "Biome": "생물 군계",
    "Biomes in Tag": "태그의 생물 군계",
    "Biome Tag": "생물 군계 태그",
    "Block Place Prevention": "블록 설치 방지",
    "Except On:": "예외:",
    "Freezing": "빙결",
    "Aether Fuel": "The Aether 연료",
    "Icestone Freezable": "빙석으로 얼릴 수 있음",
    "Incubating": "부화",
    "Item Use Prevention": "아이템 사용 방지",
    "Placement Conversion": "설치 시 변환",
    "With Properties:": "속성 조건:",
    "Swet Ball Conversion": "스웨트 공 변환",
    "Q": "Q",
    "W": "W",
    "Quick Load": "빠른 불러오기",
    "Toggle World": "월드 전환",
    "Official Aether Testing Server": "The Aether 공식 테스트 서버",
    "Apply": "적용",
    "Donate": "후원",
    "Help": "도움말",
    "Refresh": "새로 고침",
    "Remove": "제거",
    "Lifetime Angel Moa Skins": "Lifetime Angel 모아 스킨",
    "Lifetime Valkyrie Moa Skins": "Lifetime Valkyrie 모아 스킨",
    "Natural Moa Skins": "자연 모아 스킨",
    "Arctic Moa": "북극 모아",
    "Battle Sentry Moa": "전투 센트리 모아",
    "Black Moa": "검은 모아",
    "Blue Moa": "푸른 모아",
    "Boko Yellow": "Boko 노랑",
    "Bronze Moa": "청동 모아",
    "Brown Moa": "갈색 모아",
    "Chicken Moa": "닭 모아",
    "Cockatrice": "코카트리스",
    "Construction Bot": "건설 로봇",
    "Crookjaw Purple": "Crookjaw 보라",
    "Frozen Phoenix": "얼어붙은 피닉스",
    "Gargoyle Moa": "가고일 모아",
    "Gharrix Red": "Gharrix 빨강",
    "Gilded Gharrix": "도금된 Gharrix",
    "Gold Moa": "황금 모아",
    "Green Moa": "초록 모아",
    "Halcian Pink": "Halcian 분홍",
    "Medical Bot": "의료 로봇",
    "Molten Moa": "용융 모아",
    "Mossy Statue Moa": "이끼 낀 조각상 모아",
    "Orange Moa": "주황 모아",
    "Peacock Moa": "공작 모아",
    "Phoenix Moa": "피닉스 모아",
    "Pink Moa": "분홍 모아",
    "Prehistoric Moa": "선사 시대 모아",
    "Purple Moa": "보라 모아",
    "Red Moa": "붉은 모아",
    "Sentry Moa": "센트리 모아",
    "Silver Moa": "은 모아",
    "Skeleton Moa": "스켈레톤 모아",
    "Stratus": "Stratus",
    "Tivalier Green": "Tivalier 초록",
    "Undead Moa": "언데드 모아",
    "Valkyrie Moa": "발키리 모아",
    "White Moa": "하얀 모아",
    "Donate to the project to get Moa Skins!": "프로젝트를 후원하고 모아 스킨을 받으세요!",
    "Thank you for donating to the project!": "프로젝트를 후원해 주셔서 감사합니다!",
    "Pledging to the %s tier will give you lifetime access to this skin!": (
        "%s 등급을 후원하면 이 스킨을 평생 사용할 수 있습니다!"
    ),
    "Pledging to the %s tier will give you access to this skin during the pledge duration!": (
        "%s 등급을 후원하는 동안 이 스킨을 사용할 수 있습니다!"
    ),
    "You have lifetime access to this skin!": "이 스킨을 평생 사용할 수 있습니다!",
    "You have access to this skin while pledging to the %s tier!": (
        "%s 등급을 후원하는 동안 이 스킨을 사용할 수 있습니다!"
    ),
    "Lifetime Access": "평생 이용 권한",
    "Pledge Access": "후원 이용 권한",
    "Enjoying %s1? Check out our %s2 and %s3!": "%s1을(를) 즐기고 계신가요? %s2와 %s3도 확인해 보세요!",
    "This message will only display once.": "이 메시지는 한 번만 표시됩니다.",
    "I wish to fight you!": "당신과 싸우고 싶습니다!",
    "On second thought, I'd rather not.": "다시 생각해 보니 그만두겠습니다.",
    "I'm ready, I have the medals right here!": "준비됐습니다. 메달도 여기 있습니다!",
    "Nevermind": "아무것도 아닙니다",
    "I'll return when I have them.": "메달을 모으면 돌아오겠습니다.",
    "What can you tell me about this place?": "이곳에 대해 알려 주실 수 있나요?",
    "Pro Tip:": "전문가 팁:",
    "This is a sanctuary for us Valkyries who seek rest.": "이곳은 안식을 찾는 우리 발키리의 성소입니다.",
    "Now then, let's begin!": "그럼 시작하죠!",
    "Very well then. Bring me ten medals from my subordinates to prove your worth, then we'll see.": (
        "좋습니다. 내 부하들에게서 메달 열 개를 가져와 자격을 증명하세요. 그다음에 보죠."
    ),
    "You are truly... a mighty warrior...": "당신은 정말... 강한 전사군요...",
    "So be it then. Goodbye adventurer.": "그렇다면 어쩔 수 없군요. 잘 가세요, 모험가여.",
    "This will be your final battle!": "이것이 당신의 마지막 전투가 될 겁니다!",
    "Goodbye adventurer.": "잘 가세요, 모험가여.",
    "Take your time.": "천천히 하세요.",
    "Sorry, I don't fight with weaklings.": "미안하지만 약자와는 싸우지 않습니다.",
    "As expected of a human.": "역시 인간답군요.",
    "If you wish to challenge me, strike at any time.": "도전하고 싶다면 언제든 공격하세요.",
    "the Valkyrie Queen": "발키리 여왕",
    "Showing Enchantable": "마법 부여 가능 항목 표시 중",
    "Showing Freezable": "빙결 가능 항목 표시 중",
    "Showing Incubatable": "부화 가능 항목 표시 중",
    "Hmm. Perhaps I need to attack it with a Pickaxe?": "흠. 곡괭이로 공격해야 하나?",
    "the Slider": "슬라이더",
    "Time": "시간",
    "Such bitter cold... is this the feeling... of pain?": "이토록 매서운 추위라니... 이것이... 고통인가?",
    "You are certainly a brave soul to have entered this chamber.": "이 방에 들어오다니 분명 용감한 영혼이군.",
    "Begone human, you serve no purpose here.": "물러가라, 인간. 이곳에서 네게는 아무 쓸모도 없다.",
    "Did your previous death not satisfy your curiosity, human?": "지난번 죽음으로도 호기심이 풀리지 않았나, 인간?",
    "Your presence annoys me. Do you not fear my burning aura?": "네 존재가 성가시구나. 나의 불타는 기운이 두렵지 않느냐?",
    "I have nothing to offer you, fool. Leave me at peace.": "네게 줄 것은 없다, 어리석은 자여. 나를 내버려 둬라.",
    "Perhaps you are ignorant. Do you wish to know who I am?": "아무것도 모르는 모양이군. 내가 누구인지 알고 싶으냐?",
    "I am a sun spirit, embodiment of Aether's eternal daylight. As": "나는 The Aether의 영원한 낮을 구현한 태양 정령이다. 내가",
    "long as I am alive, the sun will never set on this world.": "살아 있는 한 이 세계의 해는 결코 지지 않는다.",
    "My body burns with the anger of a thousand beasts. No man,": "내 몸은 수천 짐승의 분노로 타오른다. 그 어떤 인간도,",
    "hero, or villain can harm me. You are no exception.": "영웅도 악당도 나를 해칠 수 없다. 너도 예외가 아니다.",
    "You wish to challenge the might of the sun? You are mad.": "태양의 힘에 도전하려는가? 미쳤군.",
    "Do not further insult me or you will feel my wrath.": "더는 나를 모욕하지 마라. 그렇지 않으면 내 분노를 맛볼 것이다.",
    "This is your final warning. Leave now, or prepare to burn.": "마지막 경고다. 지금 떠나지 않으면 불탈 준비를 해라.",
    "As you wish, your death will be slow and agonizing.": "원한다면 그렇게 해 주지. 네 죽음은 느리고 고통스러울 것이다.",
    "I should try attacking the Sun Spirit while it's frozen!": "태양 정령이 얼어붙었을 때 공격해 봐야겠어!",
    "Such is the fate of a being who opposes the might of the sun.": "태양의 힘에 맞선 존재의 운명은 이런 것이다.",
    "the Sun Spirit": "태양 정령",
    "What's that? You want to fight? Aww, what a cute little human.": "뭐라고? 싸우고 싶다고? 어머, 정말 귀여운 꼬마 인간이네.",
    "You're not thinking of fighting a big, strong Valkyrie are you?": "설마 크고 강한 발키리와 싸울 생각은 아니겠지?",
    "I don't think you should bother me, you could get really hurt.": "나를 건드리지 않는 게 좋을걸. 정말 크게 다칠 수 있어.",
    "I'm not going easy on you!": "봐주지 않을 거야!",
    "You're gonna regret that!": "후회하게 될 거야!",
    "Now you're in for it!": "이제 큰일 난 줄 알아!",
    "Alright, alright! You win!": "알았어, 알았어! 네가 이겼어!",
    "Okay, I give up! Geez!": "좋아, 항복할게! 정말!",
    "Oww! Fine, here's your medal...": "아야! 좋아, 여기 메달 받아...",
    "Umm... that's a nice pile of medallions you have there...": "음... 메달을 꽤 많이 모았네...",
    "That's pretty impressive, but you won't defeat me.": "꽤 대단하지만 나를 이기지는 못할 거야.",
    "You think you're a tough guy, eh? Well, bring it on!": "네가 강하다고 생각하나 보지? 좋아, 덤벼!",
    "You want a medallion? Try being less pathetic.": "메달을 원해? 한심하게 굴지 않는 것부터 해 봐.",
    "Maybe some day, %s... maybe some day.": "언젠가는 가능할지도 모르지, %s... 언젠가는.",
    "Humans aren't nearly as cute when they're dead.": "인간은 죽으면 별로 귀엽지 않네.",
}

CREATE_DRAGONS_PLUS = {
    "create.item_attributes.create_dragons_plus.aether_enchantable": "대량 마법 부여 가능",
    "create.item_attributes.create_dragons_plus.aether_enchantable.inverted": "대량 마법 부여 불가",
    "create_dragons_plus.ponder.bulk_enchanting.text_1": (
        "황금 에어클라우드를 통과하는 바람으로 대량 마법 부여 설비를 만듭니다."
    ),
    "create_dragons_plus.ponder.bulk_enchanting.text_2": (
        "대량 마법 부여는 팬 가공으로 The Aether 제단 조합법을 처리합니다."
    ),
    "recipe.create_dragons_plus.aether_fan_enchanting": "대량 마법 부여",
    "recipe.create_dragons_plus.aether_fan_enchanting.fan": "황금 에어클라우드 뒤의 팬",
    "recipe.create_dragons_plus.aether_fan_enchanting.repairing": "아이템 내구도 수리",
    "recipe.create_dragons_plus.aether_fan_incubation": "대량 마법 부여 부화",
    "recipe.create_dragons_plus.aether_fan_incubation.entity": "생성 대상: %s",
    "recipe.create_dragons_plus.aether_fan_incubation.fan": "황금 에어클라우드 뒤의 팬",
}

THEURGY = {
    "item.theurgy.alchemical_sulfur_skyroot": "연금술 유황 %s",
    "item.theurgy.alchemical_sulfur_skyroot.source": "스카이루트",
    "item.theurgy.alchemical_sulfur_skyroot.tooltip": "%s %s %s에서 만든 연금술 유황입니다.",
    "item.theurgy.alchemical_sulfur_skyroot.tooltip.extended": "유황은 물체의 '개념' 또는 '영혼'을 나타냅니다.",
    "item.theurgy.alchemical_sulfur_skyroot.tooltip.usage": (
        "유황은 스파지릭스 공정에 사용되는 핵심 원소입니다.\n\n"
        "§o힌트: 광석이나 주괴처럼 같은 재료의 서로 다른 상태로 만든 유황은 서로 바꿔 쓸 수 있습니다.§r"
    ),
}

SMALL_INTEGRATIONS = {
    "auroras": {
        "jar_pattern": "Auroras-*.jar",
        "translations": {
            "auroras.key.reload_aurora_configs": "오로라 설정 다시 불러오기"
        },
    },
    "rainbows": {
        "jar_pattern": "Rainbows-*.jar",
        "translations": {
            "rainbows.key.reload_rainbow_configs": "무지개 설정 다시 불러오기"
        },
    },
    "create_dragons_plus": {
        "jar_pattern": "CreateDragonsPlus-*.jar",
        "translations": CREATE_DRAGONS_PLUS,
    },
    "theurgy": {
        "jar_pattern": "theurgy-*.jar",
        "translations": THEURGY,
    },
}

COMMANDS_AND_DEATH = {
    "commands.aether.capability.player.life_shards.set": "%s의 생명 조각 사용 횟수를 %s(으)로 설정했습니다",
    "commands.aether.capability.time.eternal_day.query": "영원한 낮 설정: %s",
    "commands.aether.capability.time.eternal_day.set": "영원한 낮을 %s(으)로 설정했습니다",
    "commands.aether.menu.fix": "월드 미리보기 값을 초기화했습니다",
    "commands.aether.sun_altar_whitelist.add.failed": "플레이어가 이미 태양 제단 허용 목록에 있습니다",
    "commands.aether.sun_altar_whitelist.add.success": "%s을(를) 태양 제단 허용 목록에 추가했습니다",
    "commands.aether.sun_altar_whitelist.alreadyOff": "태양 제단 허용 목록이 이미 꺼져 있습니다",
    "commands.aether.sun_altar_whitelist.alreadyOn": "태양 제단 허용 목록이 이미 켜져 있습니다",
    "commands.aether.sun_altar_whitelist.disabled": "태양 제단 허용 목록을 껐습니다",
    "commands.aether.sun_altar_whitelist.enabled": "태양 제단 허용 목록을 켰습니다",
    "commands.aether.sun_altar_whitelist.list": "허용된 플레이어 %s명: %s",
    "commands.aether.sun_altar_whitelist.none": "허용된 플레이어가 없습니다",
    "commands.aether.sun_altar_whitelist.reloaded": "태양 제단 허용 목록을 다시 불러왔습니다",
    "commands.aether.sun_altar_whitelist.remove.failed": "플레이어가 태양 제단 허용 목록에 없습니다",
    "commands.aether.sun_altar_whitelist.remove.success": "%s을(를) 태양 제단 허용 목록에서 제거했습니다",
    "death.attack.aether.cloud_crystal": "%1$s이(가) %2$s의 구름 수정에 얼어붙었습니다",
    "death.attack.aether.crush": "%1$s이(가) %2$s에게 짓눌렸습니다",
    "death.attack.aether.fire_crystal": "%1$s이(가) %2$s의 불 수정에 타 버렸습니다",
    "death.attack.aether.floating_block": "%1$s이(가) 떠다니는 블록에 깔렸습니다",
    "death.attack.aether.floating_block.player": (
        "%1$s이(가) %2$s와 싸우다가 떠다니는 블록에 깔렸습니다"
    ),
    "death.attack.aether.ice_crystal": "%1$s이(가) %2$s의 얼음 수정에 얼어붙었습니다",
    "death.attack.aether.incineration": "%1$s이(가) %2$s에게 타 버렸습니다",
    "death.attack.aether.inebriation": "%1$s이(가) 만취했습니다",
    "death.attack.aether.inebriation.player": "%1$s이(가) %2$s 때문에 만취했습니다",
    "death.attack.aether.thunder_crystal": "%1$s이(가) %2$s의 천둥 수정에 감전되었습니다",
}

PACK_AND_KEYS = {
    "key.aether.category": "The Aether",
    "key.aether.gravitite_jump_ability.desc": "그래비타이트 도약 활성화",
    "key.aether.invisibility_toggle.desc": "투명화 전환",
    "key.aether.open_accessories.desc": "장신구 인벤토리 열기/닫기",
    "pack.aether.125.description": "The Aether 1.2.5의 고전적인 모습입니다.",
    "pack.aether.125.title": "The Aether 1.2.5 텍스처",
    "pack.aether.aether_accessories.description": "기본 장신구를 등록합니다.",
    "pack.aether.aether_accessories.title": "The Aether 고유 장신구",
    "pack.aether.b173.description": "The Aether b1.7.3의 원래 모습입니다.",
    "pack.aether.b173.title": "The Aether b1.7.3 텍스처",
    "pack.aether.colorblind.description": "색각 보정용으로 텍스처를 변경합니다.",
    "pack.aether.colorblind.title": "The Aether 색각 보정 텍스처",
    "pack.aether.ctm.description": "CTM 사용 시 퀵소일 유리판을 수정합니다.",
    "pack.aether.ctm.title": "The Aether CTM 수정",
    "pack.aether.default_accessories.description": "The Aether의 장신구 메뉴를 교체합니다.",
    "pack.aether.default_accessories.title": "기본 장신구 메뉴 덮어쓰기",
    "pack.aether.freezing.description": "얼음 장신구가 임시 블록을 만듭니다.",
    "pack.aether.freezing.title": "The Aether 임시 빙결",
    "pack.aether.imm_ptl_compat.description": "Immersive Portals 호환 데이터입니다.",
    "pack.aether.imm_ptl_compat.title": "Immersive Portals 호환",
    "pack.aether.mod.description": "The Aether 리소스",
    "pack.aether.ruined_portal.description": "무너진 발광석 차원문을 생성합니다.",
    "pack.aether.ruined_portal.title": "The Aether 무너진 차원문",
    "pack.aether.tips.description": "전문가 팁을 Tips의 UI로 옮깁니다.",
    "pack.aether.tips.title": "The Aether 팁",
    "pack.aether.tooltips.description": "아이템 능력 툴팁을 추가합니다.",
    "pack.aether.tooltips.title": "The Aether 아이템 툴팁",
}

SUBTITLE_ACTIONS = {
    "wobbles": "출렁임",
    "whooshes": "휙 소리를 냄",
    "noise intensifies": "소리가 커짐",
    "crackles": "타닥거림",
    "awakens": "깨어남",
    "activated": "작동함",
    "evaporated": "증발함",
    "dies": "죽음",
    "hurts": "다침",
    "shoots": "발사함",
    "squeals": "꽥 소리를 냄",
    "squeaks": "찍찍거림",
    "whistles": "휘파람 소리를 냄",
    "cries": "울음",
    "explodes": "폭발함",
    "spits": "내뱉음",
    "calls": "울음",
    "flaps": "날갯짓함",
    "hit": "명중함",
    "hits": "명중함",
    "moos": "음매 소리를 냄",
    "gets milked": "젖을 짬",
    "equips": "장착함",
    "Footsteps": "발소리",
    "plops": "툭 떨어짐",
    "attacks": "공격함",
    "burps": "트림함",
    "oinks": "꿀꿀거림",
    "squishes": "물컹거림",
    "baahs": "매애 소리를 냄",
    "drones": "웅웅거림",
    "smashes": "충돌함",
    "breaks": "부서짐",
    "slides": "미끄러짐",
    "rumbles": "우르릉거림",
    "speaks": "말함",
    "shoots Fire Crystal": "불 수정을 발사함",
    "shoots Ice Crystal": "얼음 수정을 발사함",
    "blows": "바람을 뿜음",
    "rustles": "펄럭임",
    "jingles": "짤랑거림",
    "used": "사용함",
    "clinks": "찰그락거림",
    "clanks": "철컹거림",
    "clangs": "쨍그랑거림",
    "fired": "발사함",
    "flies": "날아감",
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없이 JSON을 기록한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize_terms(value: object) -> object:
    """확정한 공통 용어를 문자열 또는 목록에 적용한다."""
    if isinstance(value, str):
        for old, new in TERM_REPLACEMENTS:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [normalize_terms(item) for item in value]
    return value


def translate_name(source: str) -> str | None:
    """규칙적인 블록·아이템·개체 이름을 조합한다."""
    if source in NAME_PHRASES:
        return NAME_PHRASES[source]
    value = source
    replacements = {**NAME_PHRASES, **WORD_TRANSLATIONS}
    for original, translated in sorted(
        replacements.items(), key=lambda row: -len(row[0])
    ):
        value = re.sub(
            rf"(?<![A-Za-z]){re.escape(original)}(?![A-Za-z])", translated, value
        )
    value = value.replace("블록 암브로슘", "암브로슘 블록")
    value = value.replace("블록 자나이트", "자나이트 블록")
    value = value.replace("스카이루트 보트 with Chest", "상자가 실린 스카이루트 보트")
    value = re.sub(r"\s+", " ", value).strip()
    if re.search(r"[A-Za-z]{3,}", value):
        return None
    return value


def translate_subtitle(source: str) -> str | None:
    """자막의 대상 이름과 동작을 조합한다."""
    if source == "Footsteps":
        return "발소리"
    for action, translated_action in sorted(
        SUBTITLE_ACTIONS.items(), key=lambda row: -len(row[0])
    ):
        marker = f" {action}"
        if source.endswith(marker):
            subject = source[: -len(marker)]
            translated_subject = translate_name(subject)
            if translated_subject is not None:
                return f"{translated_subject} {translated_action}"
    return None


def translate_new(key: str, source: object) -> object:
    """현재 JAR의 영어 원문을 검수된 수동 사전과 규칙으로 번역한다."""
    if not isinstance(source, str):
        raise TypeError(f"문자열이 아닌 언어 값: {key}")
    for mapping in (
        ADVANCEMENTS,
        AETHER_CORE,
        COMMANDS_AND_DEATH,
        EFFECTS_AND_JUKEBOX,
        PACK_AND_KEYS,
    ):
        if key in mapping:
            return mapping[key]
    if key.startswith("config.") and source in CONFIG_VALUES:
        return CONFIG_VALUES[source]
    if key.startswith("gui.") and source in GUI_VALUES:
        return GUI_VALUES[source]
    if key.startswith("lore."):
        translated = aether_lore.translate(key)
        if translated is not None:
            return translated
    if key.startswith(
        (
            "block.",
            "item.",
            "entity.",
            "biome.",
            "dimension.",
            "structure.",
            "trim_material.",
            "itemGroup.",
            "accessories.",
            "rarity.",
            "menu.",
        )
    ):
        translated = translate_name(source)
        if translated is not None:
            return translated
    if key.startswith("subtitles."):
        translated = translate_subtitle(source)
        if translated is not None:
            return translated
    raise KeyError(f"수동 번역 규칙이 없는 키: {key} = {source!r}")


def review_language() -> dict[str, object]:
    """현재 설치 JAR의 1,238개 언어 키를 전수 재검수한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    sources = load_json(LANG_ROOT / "candidate_sources.json")
    instance = resolve_source_root()
    jar = find_one(instance / "mods", "aether-*.jar", "The Aether")
    with ZipFile(jar) as archive:
        bundled = json.loads(
            archive.read("assets/aether/lang/ko_kr.json").decode("utf-8-sig")
        )
    for key, source in english.items():
        korean[key] = translate_new(key, source)
        if key not in bundled:
            sources[key] = "manual_review"
        elif korean[key] == bundled[key]:
            sources[key] = "bundled_ko_kr"
        else:
            sources[key] = "manual_quality_review"
        errors = family_goal.validate_value(key, source, korean[key])
        if errors:
            raise ValueError("; ".join(errors))
    write_json(LANG_ROOT / "ko_kr.json", korean)
    write_json(LANG_ROOT / "candidate_sources.json", sources)
    counts = Counter(sources.values())
    return {
        "keys_reviewed": len(english),
        "bundled_exact_reuse": counts["bundled_ko_kr"],
        "quality_edited": counts["manual_quality_review"],
        "new_translation": counts["manual_review"],
        "source_counts": dict(sorted(counts.items())),
    }


def quest_text(value: object) -> str:
    """퀘스트 표시 값의 첫 문구를 반환한다."""
    if isinstance(value, str):
        return value
    if isinstance(value, list) and value and isinstance(value[0], str):
        return value[0]
    raise TypeError(f"지원하지 않는 퀘스트 표시 값: {value!r}")


def restore_quest_linebreaks(source: object, replacement: str) -> str:
    """원문의 문단 수만큼 한국어 문장 경계에 줄바꿈을 배치한다."""
    required = quest_text(source).count("\\n\\n")
    while replacement.count("\\n\\n") < required:
        segments = replacement.split("\\n\\n")
        candidates: list[tuple[int, int, int]] = []
        for index, segment in enumerate(segments):
            boundaries = []
            for match in re.finditer(r"[.!?…](?:[\"'])?\s+", segment):
                position = (
                    match.end() - len(match.group(0)) + len(match.group(0).rstrip())
                )
                if segment[:position].strip() and segment[position:].strip():
                    boundaries.append(position)
            for position in boundaries:
                candidates.append((len(segment), index, position))
        if not candidates:
            raise ValueError(
                "원문 문단 수를 보존할 한국어 문장 경계를 찾지 못했습니다: "
                f"{replacement!r}"
            )
        _, index, position = max(candidates)
        segment = segments[index]
        segments[index : index + 1] = [
            segment[:position].rstrip(),
            segment[position:].lstrip(),
        ]
        replacement = "\\n\\n".join(segments)
    return replacement


def replace_quest_text(source: object, value: object, replacement: str) -> object:
    """퀘스트 목록의 첫 표시 문구만 바꾸고 뒤따르는 이미지 요소를 보존한다."""
    replacement = restore_quest_linebreaks(source, replacement)
    if isinstance(value, str):
        return replacement
    if isinstance(value, list) and value and isinstance(value[0], str):
        return [replacement, *value[1:]]
    raise TypeError(f"지원하지 않는 퀘스트 표시 값: {value!r}")


def review_quests() -> dict[str, object]:
    """The Aether 전용 퀘스트의 161개 표시 키를 전수 검수한다."""
    root = WORK_ROOT / "quests/aether"
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    sources = load_json(root / "candidate_sources.json")
    for key, source in english.items():
        translated = aether_quests.translate(key, source)
        korean[key] = replace_quest_text(source, korean[key], translated)
        sources[key] = "manual_review"
        errors = family_goal.quest_snbt.validate_value(key, source, korean[key])
        if errors:
            raise ValueError("; ".join(errors))
    write_json(root / "ko_kr.json", korean)
    write_json(root / "candidate_sources.json", sources)
    return {
        "keys_reviewed": len(english),
        "new_translation": len(english),
        "source_counts": dict(sorted(Counter(sources.values()).items())),
    }


def find_one(root: Path, pattern: str, label: str) -> Path:
    """현재 설치본에서 파일 패턴과 일치하는 JAR 하나를 찾는다."""
    matches = sorted(root.glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"{label} JAR 검색 결과가 하나가 아닙니다: {matches}")
    return matches[0]


def build_bibliowoods() -> dict[str, object]:
    """BiblioWoods의 스카이루트 직접 연동 157개 키를 생성한다."""
    instance = resolve_source_root()
    jar = find_one(instance / "mods", "bibliowoods-*.jar", "BiblioWoods")
    with ZipFile(jar) as archive:
        all_english = json.loads(
            archive.read("assets/bibliowoods/lang/en_us.json").decode("utf-8-sig")
        )
    english = {
        key: value for key, value in all_english.items() if "aether_skyroot" in key
    }
    old_woods = twilight_family.WOOD_NAMES
    try:
        twilight_family.WOOD_NAMES = {"Skyroot": "스카이루트"}
        korean = {
            key: twilight_family.translate_bibliowoods_value(value)
            for key, value in english.items()
        }
    finally:
        twilight_family.WOOD_NAMES = old_woods
    root = WORK_ROOT / "bibliowoods"
    write_json(root / "en_us.json", english)
    write_json(root / "ko_kr.json", korean)
    write_json(
        root / "candidate_sources.json",
        {key: "generated_reviewed_translation" for key in english},
    )
    output = OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json"
    merged = load_json(output) if output.is_file() else {}
    preserved = sum(key not in english for key in merged)
    merged.update(korean)
    write_json(output, merged)
    report = {
        "jar": jar.name,
        "all_english_keys": len(all_english),
        "aether_skyroot_keys": len(english),
        "existing_keys_preserved": preserved,
        "merged_output_keys": len(merged),
    }
    if len(english) != 157:
        raise ValueError(
            f"BiblioWoods 스카이루트 키 수가 예상과 다릅니다: {len(english)}"
        )
    write_json(WORK_ROOT / "bibliowoods_scope.json", report)
    return report


def build_small_integrations() -> dict[str, object]:
    """The Aether에 직접 의존하는 네 모드의 표시 키만 부분 번역한다."""
    instance = resolve_source_root()
    reports: dict[str, object] = {}
    for namespace, spec in SMALL_INTEGRATIONS.items():
        jar = find_one(instance / "mods", str(spec["jar_pattern"]), namespace)
        path = f"assets/{namespace}/lang/en_us.json"
        with ZipFile(jar) as archive:
            all_english = json.loads(archive.read(path).decode("utf-8-sig"))
        translations = dict(spec["translations"])
        missing = sorted(set(translations) - set(all_english))
        if missing:
            raise KeyError(f"{namespace} 현재 원문에 없는 연동 키: {missing}")
        english = {key: all_english[key] for key in translations}
        for key, source in english.items():
            errors = family_goal.validate_value(key, source, translations[key])
            if errors:
                raise ValueError("; ".join(errors))
        root = WORK_ROOT / namespace
        write_json(root / "en_us.json", english)
        write_json(root / "ko_kr.json", translations)
        write_json(
            root / "candidate_sources.json",
            {key: "manual_direct_integration" for key in translations},
        )
        output = OUTPUT_ASSETS / namespace / "lang/ko_kr.json"
        merged = load_json(output) if output.is_file() else {}
        preserved = sum(key not in translations for key in merged)
        merged.update(translations)
        write_json(output, merged)
        reports[namespace] = {
            "jar": jar.name,
            "keys_reviewed": len(translations),
            "existing_keys_preserved": preserved,
            "merged_output_keys": len(merged),
        }
    write_json(WORK_ROOT / "direct_integrations.json", reports)
    return reports


def build_kubejs() -> dict[str, object]:
    """활성 공지의 The Aether 추가 안내 한 줄만 한국어로 교정한다."""
    instance = resolve_source_root()
    relative = Path("kubejs/server_scripts/announcements/announcements.js")
    source = instance / relative
    text = source.read_text(encoding="utf-8-sig")
    old = 'addAnnouncement("4.6", "Added mods: Aether, BotanyPots, BotanyTrees and RefinedTypes")'
    new = 'addAnnouncement("4.6", "추가된 모드: The Aether, BotanyPots, BotanyTrees, RefinedTypes")'
    if text.count(old) == 1 and new not in text:
        translated = text.replace(old, new)
        source_state = "english_source"
    elif text.count(new) == 1 and old not in text:
        translated = text
        source_state = "already_applied"
    else:
        raise ValueError(
            "The Aether 추가 공지 원문 또는 적용본을 정확히 확인할 수 없습니다."
        )
    working = WORK_ROOT / relative
    output = PROJECT_ROOT / "output/overrides" / relative
    working.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    working.write_text(translated, encoding="utf-8")
    output.write_text(translated, encoding="utf-8")
    report = {
        "source": relative.as_posix(),
        "references_checked": 2,
        "direct_display_lines_translated": 1,
        "source_state": source_state,
        "output": output.relative_to(PROJECT_ROOT).as_posix(),
    }
    write_json(WORK_ROOT / "kubejs_scope.json", report)
    return report


def review() -> dict[str, object]:
    """본체와 모든 직접 표시 연동 경로의 검수 결과를 기록한다."""
    report = {
        "family": "The Aether",
        "language": review_language(),
        "ftbquests": review_quests(),
        "bibliowoods": build_bibliowoods(),
        "direct_integrations": build_small_integrations(),
        "kubejs": build_kubejs(),
    }
    write_json(WORK_ROOT / "manual_review_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("review",))
    parser.parse_args()
    report = review()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
