#!/usr/bin/env python3
"""Oh The Biomes We've Gone과 Regions Unexplored를 번역하고 검증해요."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

import audit_ftbquests_titles as quest_audit
import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

FAMILY = "biomes_regions"
WORK_ROOT = PROJECT_ROOT / "working/biomes_regions"
OUTPUT_ROOT = active_output_root() / "resourcepack/ATM10_Korean/assets"
QUEST_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?")
URL = re.compile(r"https?://[^\s\"']+")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")
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
MODS = {
    "biomeswevegone": {
        "jar": "Oh-The-Biomes-Weve-Gone-NeoForge-*.jar",
        "keys": 1169,
    },
    "regions_unexplored": {
        "jar": "regions_unexplored-neoforge-*.jar",
        "keys": 836,
    },
}

QUEST_CORRECTIONS = {
    "quest.0589911EB4D30FAD.quest_desc": [
        "&l&cRegions Unexplored&r에서는 판자를 양털이나 유리처럼 색칠할 수도 있어요!"
    ],
    "quest.0589911EB4D30FAD.title": "색칠한 판자",
    "quest.0BC106B34AD386E5.quest_desc": [
        "&l&cRegions Unexplored&r는 &l&6AllTheMods!&r에 새로 합류한 또 하나의 "
        "생물군계 모드예요! \\n\\n새 생물군계가 생기면 당연히 나무도 더 많아지죠!"
    ],
    "quest.0BC106B34AD386E5.title": "&l&cRegions Unexplored&r 원목",
    "quest.1625C3A30E69D634.quest_desc": [
        "이 새로운 돌은 &l&cRegions Unexplored&r 생물군계에서 찾을 수 있어요! "
        "\\n\\n이끼 낀 돌은 &l&aOh The Biomes We've Gone&r의 이끼 낀 돌과 다릅니다. "
        "\\n\\n이끼 낀 석재 벽돌과도 달라요."
    ],
    "quest.1625C3A30E69D634.title": "&l&cRegions Unexplored&r 돌",
    "quest.4EA2DB12E8F0068F.quest_desc": [
        "&l&aOh The Biomes We've Gone&r은 &l&aOh The Biomes You'll Go&r의 후속 "
        '모드이며, 그 이름은 Dr. Seuss의 책 "Oh the Places You\'ll Go"를 비튼 '
        "말장난이에요.\\n\\n새로운 식물과 바위, 나무가 어우러진 아름다운 생물군계를 "
        "아주 많이 추가합니다!"
    ],
    "quest.4EA2DB12E8F0068F.title": "&l&aOh The Biomes We've Gone&r 목재",
    "quest.537B39B42C7D21ED.quest_desc": [
        "&l&aOh The Biomes We've Gone&r이 추가한 생물군계에서는 데이사이트, 붉은 "
        "바위, 이끼 낀 돌, 울퉁불퉁한 돌의 4가지 새로운 돌을 찾을 수 있어요. "
        "\\n\\n그런데 울퉁불퉁한 돌은 다른 돌보다 무엇이 더 울퉁불퉁해서 그런 이름을 "
        "얻었을까요?"
    ],
    "quest.537B39B42C7D21ED.title": "&l&aOh The Biomes We've Gone&r 돌",
    "quest.6E17595887A051C2.quest_desc": [
        "&l&2모드가 적용된 Minecraft&r는 새로운 주민 직업을 소개합니다!\\n\\nForge "
        "망치: &5산업가&r\\n\\n충전기: &b플루익스 연구원&r\\n\\n고급 벌통: &6양봉가&r"
        "\\n\\n커피 메이커: &9엔지니어&r\\n\\n아케인 코어: &d으슥한 마법사&r"
        "\\n\\n채집가 작업대: &a채집가&r\\n\\n동력 롤링 기계: &e카트맨&r\\n수동 "
        "롤링 기계: &e궤도 기술자&r\\n\\n엔지니어 작업대: &7총기 제작자&r\\n하얀색 "
        "현수막: &7현수막 제작자&r\\n엔지니어 회로 작업대: &7전기기사&r\\n엔지니어 "
        "제작대: &7기계공&r\\n턴테이블: &7구조물 엔지니어&r\\n\\n충전소: &4압력 "
        "기능공&r\\n\\n톱: &8목수&r"
    ],
    "task.0740BC10E4D2568F.title": "Regions Unexplored 돌",
    "task.1AD43F80F89DF9D9.title": "Oh The Biomes We've Gone 돌",
    "task.4892144C32DCEB55.title": "색칠한 판자",
    "task.61FFB3326113FE18.title": "Oh The Biomes We've Gone 목재",
    "task.78F0D5822BF96CA9.title": "Regions Unexplored 원목",
}

COLORS = {
    "Black": "검은색",
    "Blue": "파란색",
    "Brown": "갈색",
    "Cyan": "청록색",
    "Gray": "회색",
    "Green": "초록색",
    "Indigo": "남색",
    "Light Blue": "하늘색",
    "Light Gray": "회백색",
    "Lime": "연두색",
    "Magenta": "자홍색",
    "Orange": "주황색",
    "Peach": "복숭아색",
    "Pink": "분홍색",
    "Purple": "보라색",
    "Red": "빨간색",
    "Silver": "은빛",
    "Violet": "보라색",
    "White": "흰색",
    "Yellow": "노란색",
}

ADJECTIVES = {
    "Alpine": "고산",
    "Apple": "사과가 열린",
    "Attached": "붙어 있는",
    "Blooming": "꽃이 핀",
    "Carved": "조각된",
    "Chiseled": "조각된",
    "Cracked": "금이 간",
    "Cut": "깎인",
    "Dead": "말라 죽은",
    "Deepslate": "심층암",
    "Flowering": "꽃피는",
    "Fluorescent": "형광",
    "Frozen": "얼어붙은",
    "Giant": "거대한",
    "Glistering": "반짝이는",
    "Glowing": "빛나는",
    "Golden Spined": "황금 가시",
    "Hanging": "매달린",
    "Imbued": "마력이 깃든",
    "Large": "큰",
    "Lush": "무성한",
    "Medium": "중간 크기",
    "Mossy": "이끼 낀",
    "Mycotoxic": "균독성",
    "Overgrown": "뒤덮인",
    "Polished": "윤나는",
    "Raw": "원시",
    "Sandy": "모래투성이",
    "Small": "작은",
    "Smooth": "매끄러운",
    "Tall": "키 큰",
    "Volcanic": "화산",
    "Wilting": "시든",
    "Windswept": "바람에 깎인",
}

BASES = {
    "Acacia": "아카시아나무",
    "Alpha": "알파 나무",
    "Apple Oak": "사과 참나무",
    "Araucaria": "아라우카리아",
    "Ashen": "잿빛 나무",
    "Aspen": "아스펜",
    "Bamboo": "대나무",
    "Baobab": "바오밥",
    "Birch": "자작나무",
    "Blackwood": "블랙우드",
    "Blue Enchanted": "파란 마법 나무",
    "Brimwood": "브림우드",
    "Cika": "치카",
    "Cobalt": "코발트 나무",
    "Crimson": "진홍빛 나무",
    "Cypress": "사이프러스",
    "Dark Oak": "짙은 참나무",
    "Dead": "고사목",
    "Dead Pine": "고사한 소나무",
    "Ebony": "흑단",
    "Enchanted Birch": "마법 자작나무",
    "Eucalyptus": "유칼립투스",
    "Fir": "전나무",
    "Florus": "플로러스",
    "Flowering": "꽃피는 나무",
    "Golden Larch": "황금 낙엽송",
    "Green Enchanted": "초록 마법 나무",
    "Holly": "호랑가시나무",
    "Ironwood": "아이언우드",
    "Jacaranda": "자카란다",
    "Joshua": "여호수아나무",
    "Jungle": "정글나무",
    "Kapok": "카폭",
    "Larch": "낙엽송",
    "Magnolia": "목련",
    "Mahogany": "마호가니",
    "Maple": "단풍나무",
    "Mangrove": "맹그로브나무",
    "Mauve": "모브 나무",
    "Oak": "참나무",
    "Orchard": "과수원 나무",
    "Palm": "야자나무",
    "Palo Verde": "팔로베르데",
    "Pine": "소나무",
    "Rainbow Eucalyptus": "무지개 유칼립투스",
    "Redwood": "레드우드",
    "Sakura": "벚나무",
    "Silver Birch": "은빛 자작나무",
    "Skyris": "스카이리스",
    "Small Oak": "작은 참나무",
    "Socotra": "소코트라",
    "Spirit": "영혼 나무",
    "Spruce": "가문비나무",
    "White Mangrove": "흰 맹그로브나무",
    "Willow": "버드나무",
    "Witch Hazel": "풍년화",
    "Yucca": "유카",
    "Zelkova": "느티나무",
}

BASE_NOUNS = {
    "Aloe Vera": "알로에 베라",
    "Allium": "알리움",
    "Amaranth": "아마란스",
    "Angelica": "당귀",
    "Anemone": "아네모네",
    "Apple": "사과",
    "Barrel Cactus": "통 선인장",
    "Bellflower": "초롱꽃",
    "Begonia": "베고니아",
    "Bioshroom": "바이오버섯",
    "Bistort": "범꼬리",
    "Black Ice": "검은 얼음",
    "Borealis Ice": "북극광 얼음",
    "Blue Glowcane": "파란 발광수수",
    "Blueberry": "블루베리",
    "California Poppy": "캘리포니아 양귀비",
    "Cattail": "부들",
    "Chalk": "백악",
    "Clover": "클로버",
    "Coneflower": "에키네시아",
    "Crocus": "크로커스",
    "Cyclamen": "시클라멘",
    "Daffodil": "수선화",
    "Dacite": "데이사이트",
    "Daisy": "데이지",
    "Dorcel": "도르셀",
    "Dreid": "드레이드",
    "Earlight": "얼라이트",
    "Firecracker": "폭죽꽃",
    "Glowcane": "발광수수",
    "Guzmania": "구즈마니아",
    "Horseweed": "망초",
    "Hydrangea": "수국",
    "Hyacinth": "히아신스",
    "Hyssop": "히솝",
    "Iris": "붓꽃",
    "Jacaranda": "자카란다",
    "Leather Flower": "가죽꽃",
    "Lily": "백합",
    "Lupine": "루핀",
    "Magnolia": "목련",
    "Maple": "단풍나무",
    "Pale Pumpkin": "창백한 호박",
    "Peat": "이탄",
    "Pitcher Plant": "벌레잡이통풀",
    "Poppy": "양귀비",
    "Prickly Pear Cactus": "백년초 선인장",
    "Prismarite": "프리즈머라이트",
    "Prismoss": "프리즈모스",
    "Red Glowcane": "빨간 발광수수",
    "Red Rock": "붉은 바위",
    "Richea": "리케아",
    "Rose": "장미",
    "Sage": "세이지",
    "Saguaro Cactus": "사와로 선인장",
    "Scilla": "무릇",
    "Snowbelle": "스노벨",
    "Snowdrops": "스노드롭",
    "Stone": "돌",
    "Silt": "실트",
    "Steppe": "스텝",
    "Spanish Moss": "스페인 이끼",
    "Succulent": "다육식물",
    "Trillium": "연령초",
    "Tulip": "튤립",
    "White Puffball": "흰 말불버섯",
    "Viridescent": "초록빛",
    "Yellow Glowcane": "노란 발광수수",
}

SUFFIXES = (
    ("Wall Hanging Sign", "벽걸이 표지판"),
    ("Bioshroom Hyphae", "바이오버섯 균사"),
    ("Bioshroom Stem", "바이오버섯 줄기"),
    ("Bioshroom Block", "바이오버섯 블록"),
    ("Chiseled Bookshelf", "조각된 책장"),
    ("Sandstone Stairs", "사암 계단"),
    ("Sandstone Slab", "사암 반 블록"),
    ("Sandstone Wall", "사암 담장"),
    ("Painted Planks", "칠한 판자"),
    ("Painted Stairs", "칠한 계단"),
    ("Painted Slab", "칠한 반 블록"),
    ("Crafting Table", "제작대"),
    ("Pressure Plate", "감압판"),
    ("Hanging Sign", "매다는 표지판"),
    ("Flower Bush", "꽃덤불"),
    ("Brick Stairs", "벽돌 계단"),
    ("Brick Slab", "벽돌 반 블록"),
    ("Brick Wall", "벽돌 담장"),
    ("Fence Gate", "울타리 문"),
    ("Leaf Pile", "낙엽 더미"),
    ("Grass Block", "잔디 블록"),
    ("Tall Grass", "키 큰 잔디"),
    ("Dirt Path", "흙길"),
    ("Coarse Dirt", "거친 흙"),
    ("Wall Sign", "벽 표지판"),
    ("Bookshelf", "책장"),
    ("Trapdoor", "다락문"),
    ("Cobblestone", "조약돌"),
    ("Sandstone", "사암"),
    ("Farmland", "경작지"),
    ("Sapling", "묘목"),
    ("Planks", "판자"),
    ("Stairs", "계단"),
    ("Slab", "반 블록"),
    ("Fence", "울타리"),
    ("Button", "버튼"),
    ("Door", "문"),
    ("Leaves", "잎"),
    ("Lily Pads", "수련잎"),
    ("Lily Pad", "수련잎"),
    ("Branch", "가지"),
    ("Shrub", "관목"),
    ("Mushroom Block", "버섯 블록"),
    ("Mushroom Stem", "버섯 줄기"),
    ("Mushroom", "버섯"),
    ("Glow Bottle", "발광 병"),
    ("Glowcane Powder", "발광수수 가루"),
    ("Glowcane Shoot", "발광수수 순"),
    ("Mushrooms", "버섯"),
    ("Snowbelle", "스노벨"),
    ("Coneflower", "에키네시아"),
    ("Bellflower", "초롱꽃"),
    ("Pitcher Plant", "벌레잡이통풀"),
    ("Leather Flower", "가죽꽃"),
    ("Flower Patch", "꽃 군락"),
    ("Flower", "꽃"),
    ("Flowers", "꽃"),
    ("Petal Block", "꽃잎 블록"),
    ("Thatch Carpet", "이엉 카펫"),
    ("Thatch", "이엉"),
    ("Tile Stairs", "타일 계단"),
    ("Tile Slab", "타일 반 블록"),
    ("Tile Wall", "타일 담장"),
    ("Tiles", "타일"),
    ("Pillar", "기둥"),
    ("Bricks", "벽돌"),
    ("Cluster", "군집"),
    ("Vines", "덩굴"),
    ("Roots", "뿌리"),
    ("Webbing", "거미줄"),
    ("Earlight", "얼라이트"),
    ("Prismoss", "프리즈모스"),
    ("Sprout", "새싹"),
    ("Patch", "군락"),
    ("Plant", "식물"),
    ("Fruit", "열매"),
    ("Powder", "가루"),
    ("Shoot", "순"),
    ("Bottle", "병"),
    ("Cactus", "선인장"),
    ("Daisy", "데이지"),
    ("Lupine", "루핀"),
    ("Trillium", "연령초"),
    ("Dirt", "흙"),
    ("Mud", "진흙"),
    ("Podzol", "회백토"),
    ("Sand", "모래"),
    ("Ice", "얼음"),
    ("Bloom", "꽃송이"),
    ("Bulb", "알뿌리"),
    ("Bud", "싹"),
    ("Fern", "고사리"),
    ("Wart", "사마귀"),
    ("Pad", "잎"),
    ("Beard", "수염"),
    ("Wall", "담장"),
    ("Sign", "표지판"),
    ("Wood", "나무"),
    ("Log", "원목"),
    ("Stem", "줄기"),
    ("Hyphae", "균사"),
    ("Nylium", "네사체"),
    ("Grass", "잔디"),
    ("Bush", "덤불"),
    ("Block", "블록"),
)

BIOMES = {
    "Allium Shrubland": "알리움 관목지",
    "Amaranth Grassland": "아마란스 초원",
    "Araucaria Savanna": "아라우카리아 사바나",
    "Aspen Boreal": "아스펜 한대림",
    "Atacama Outback": "아타카마 오지",
    "Baobab Savanna": "바오밥 사바나",
    "Basalt Barrera": "현무암 장벽",
    "Bayou": "바이유",
    "Black Forest": "검은 숲",
    "Canadian Shield": "캐나다 순상지",
    "Cika Woods": "치카 숲",
    "Coconino Meadow": "코코니노 목초지",
    "Coniferous Forest": "침엽수림",
    "Crag Gardens": "바위 봉우리 정원",
    "Crimson Tundra": "진홍빛 툰드라",
    "Cypress Swamplands": "사이프러스 늪지",
    "Cypress Wetlands": "사이프러스 습지",
    "Dacite Ridges": "데이사이트 산등성이",
    "Dacite Shore": "데이사이트 해안",
    "Dead Sea": "죽은 바다",
    "Ebony Woods": "흑단 숲",
    "Enchanted Tangle": "마법에 걸린 덤불숲",
    "Eroded Borealis": "침식된 북녘 지대",
    "Firecracker Chaparral": "폭죽꽃 관목림",
    "Forgotten Forest": "잊힌 숲",
    "Fragment Jungle": "파편 정글",
    "Frosted Coniferous Forest": "서리 덮인 침엽수림",
    "Frosted Taiga": "서리 덮인 타이가",
    "Howling Peaks": "울부짖는 봉우리",
    "Ironwood Gour": "아이언우드 구르",
    "Jacaranda Jungle": "자카란다 정글",
    "Lush Stacks": "무성한 해식 기둥",
    "Maple Taiga": "단풍나무 타이가",
    "Mojave Desert": "모하비 사막",
    "Orchard": "과수원",
    "Overgrowth Woodlands": "우거진 삼림",
    "Pale Bog": "창백한 습원",
    "Prairie": "프레리",
    "Pumpkin Valley": "호박 골짜기",
    "Rainbow Beach": "무지개 해변",
    "Red Rock Peaks": "붉은 바위 봉우리",
    "Red Rock Valley": "붉은 바위 골짜기",
    "Redwood Thicket": "레드우드 덤불숲",
    "Rose Fields": "장미 들판",
    "Rugged Badlands": "험준한 악지",
    "Sakura Grove": "벚나무 숲",
    "Shattered Glacier": "부서진 빙하",
    "Sierra Badlands": "시에라 악지",
    "Skyris Vale": "스카이리스 골짜기",
    "Temperate Grove": "온대 숲",
    "Tropical Rainforest": "열대 우림",
    "Weeping Witch Forest": "흐느끼는 마녀 숲",
    "White Mangrove Marshes": "흰 맹그로브 습지",
    "Windswept Desert": "바람 부는 사막",
    "Zelkova Forest": "느티나무 숲",
    "Alpha Grove": "알파 숲",
    "Ancient Delta": "고대 삼각주",
    "Arid Mountains": "건조한 산맥",
    "Ashen Woodland": "잿빛 삼림",
    "Autumnal Maple Forest": "가을 단풍나무 숲",
    "Bamboo Forest": "대나무 숲",
    "Barley Fields": "보리 들판",
    "Bioshroom Caves": "바이오버섯 동굴",
    "Blackstone Basin": "흑암 분지",
    "Blackwood Taiga": "블랙우드 타이가",
    "Boreal Taiga": "한대 타이가",
    "Chalk Cliffs": "백악 절벽",
    "Clover Plains": "클로버 평원",
    "Cold Boreal Taiga": "추운 한대 타이가",
    "Cold Deciduous Forest": "추운 낙엽수림",
    "Cold River": "차가운 강",
    "Deciduous Forest": "낙엽수림",
    "Dry Bushland": "건조 관목지",
    "Eucalyptus Forest": "유칼립투스 숲",
    "Fen": "소택지",
    "Flower Fields": "꽃 들판",
    "Frozen Pine Taiga": "얼어붙은 소나무 타이가",
    "Frozen Tundra": "얼어붙은 툰드라",
    "Fungal Fen": "균류 소택지",
    "Glistering Meadow": "반짝이는 목초지",
    "Golden Boreal Taiga": "황금빛 한대 타이가",
    "Grassland": "초원",
    "Grassy Beach": "풀이 우거진 해변",
    "Gravel Beach": "자갈 해변",
    "Highland Fields": "고원 들판",
    "Hyacinth Deeps": "히아신스 심층 지대",
    "Icy Heights": "얼어붙은 고지",
    "Infernal Holt": "지옥 숲",
    "Joshua Desert": "여호수아나무 사막",
    "Magnolia Woodland": "목련 삼림",
    "Maple Forest": "단풍나무 숲",
    "Marsh": "습지",
    "Mauve Hills": "연보라 언덕",
    "Mountains": "산맥",
    "Muddy River": "진흙 강",
    "Mycotoxic Undergrowth": "균독성 덤불",
    "Old Growth Bayou": "오래된 바이유",
    "Outback": "오지",
    "Pine Slopes": "소나무 비탈",
    "Pine Taiga": "소나무 타이가",
    "Poppy Fields": "양귀비 들판",
    "Prismachasm": "프리즈마 협곡",
    "Pumpkin Fields": "호박 들판",
    "Rainforest": "우림",
    "Redstone Abyss": "레드스톤 심연",
    "Redstone Caves": "레드스톤 동굴",
    "Redwoods": "레드우드 숲",
    "Rocky Meadow": "바위 목초지",
    "Rocky Reef": "바위 암초",
    "Saguaro Desert": "사와로 사막",
    "Scorching Caves": "이글거리는 동굴",
    "Shrubland": "관목지",
    "Silver Birch Forest": "은빛 자작나무 숲",
    "Sparse Rainforest": "드문드문한 우림",
    "Sparse Redwoods": "드문드문한 레드우드 숲",
    "Spires": "첨탑 지대",
    "Steppe": "스텝",
    "Towering Cliffs": "우뚝 솟은 절벽",
    "Tropical River": "열대 강",
    "Tropics": "열대 지방",
    "Willow Forest": "버드나무 숲",
}

EXACT_TEXT = {
    "Dead Boat": "고사목 보트",
    "Dead Boat with Chest": "상자가 실린 고사목 보트",
    "Oh The Biomes We've Gone": "Oh The Biomes We've Gone",
    "Biomes We've Gone": "Biomes We've Gone",
    "Biomes We've Gone Wood": "Biomes We've Gone 목재",
    "Regions Unexplored": "Regions Unexplored",
    "Boat": "보트",
    "Boat with Chest": "상자가 실린 보트",
    "Boat With Chest": "상자가 실린 보트",
    "Forager": "채집가",
    "Green Apple": "초록 사과",
    "Music Disc": "음반",
    "AOCAWOL - Better Days": "AOCAWOL - Better Days",
    "AOCAWOL - Pixie Club": "AOCAWOL - Pixie Club",
    "Hatch Chance: %s": "부화 확률: %s",
}

EXACT_TEXT.update(
    {
        "Find a Pixie Club Music Disc": "픽시 클럽 음반 찾기",
        "Forgotten Fae": "잊힌 요정",
        "Fall into quicksand": "유사에 빠지기",
        "I'm Sinking?": "가라앉고 있나?",
        "Find all the Prairie houses": "모든 프레리 주택 찾기",
        "Little House on the Prairie": "프레리의 작은 집",
        "Explore all of the BWG biomes": "BWG의 모든 생물군계 탐험하기",
        "So you’ve found a Pale Bog..": "창백한 습원을 찾았군요..",
        "Pale in Comparison": "비교가 안 될 만큼 창백하게",
        "The root of all things BWG adventure": "BWG 모험의 모든 시작",
        "Adventure": "모험",
        "Find all the inhabited BWG Villages": "주민이 사는 모든 BWG 마을 찾기",
        "True Traveler": "진정한 여행자",
        "In the Pale Bog lies a different kind of challenge.": (
            "창백한 습원에는 색다른 도전이 기다리고 있어요."
        ),
        "Down The Witches Road": "마녀의 길을 따라",
        "Launch a world with the Oh The Biomes We've Gone": (
            "Oh The Biomes We've Gone이 적용된 세계 시작하기"
        ),
        "Obtain Blueberries": "블루베리 얻기",
        "Berrily Alive": "베리 덕분에 살아 있어",
        "Obtain White Puffball Caps": "흰 말불버섯 갓 얻기",
        "Reminds them of a childhood they never got..": (
            "누리지 못했던 어린 시절을 떠올리게 해요.."
        ),
        "Forgotten Nostalgia": "잊힌 향수",
        "Obtain a Green Apple from the Skyris Vale": (
            "스카이리스 골짜기에서 초록 사과 얻기"
        ),
        "Granny Smith?": "그래니 스미스?",
        "Cook a Cattail on a campfire, you might wanna back away...": (
            "모닥불에 부들을 구워 보세요. 조금 물러나는 게 좋을지도 몰라요..."
        ),
        "Hot Diggity Not Dog": "이건 핫도그가 아니야",
        "Find All 3 Apples": "사과 3종 모두 찾기",
        "Johnny Appleseed": "조니 애플시드",
        "Craft both of the BWG pies.": "BWG 파이를 모두 만들기",
        "Just Like Grandma's": "할머니가 만든 것처럼",
        "The root of all things BWG husbandry": "BWG 농업의 모든 시작",
        "Husbandry": "농업",
        "Successfully reloaded misc config": "기타 설정을 다시 불러왔어요",
        "Successfully reloaded Mob Spawn config": "몹 생성 설정을 다시 불러왔어요",
        "Successfully reloaded all configs": "모든 설정을 다시 불러왔어요",
        "Apple Fruit": "사과 열매",
        "Beach Grass": "해변 잔디",
        "Chiseled Windswept Sandstone": "조각된 바람맞이 사암",
        "Cracked Red Sand": "갈라진 붉은 모래",
        "Cracked Sand": "갈라진 모래",
        "Cut Windswept Sandstone": "깎인 바람맞이 사암",
        "Cut Windswept Sandstone Slab": "깎인 바람맞이 사암 반 블록",
        "Dacite Tile Slab": "데이사이트 타일 반 블록",
        "Dacite Tile Stairs": "데이사이트 타일 계단",
        "Delphinium": "델피니움",
        "Fairy Slipper": "요정 슬리퍼꽃",
        "Flower Patch": "꽃 군락",
        "Flowering Tiny Lily Pads": "꽃이 핀 작은 수련잎",
        "Firecracker Flower Bush": "폭죽꽃 덤불",
        "Foragers Table": "채집가 작업대",
        "Foxglove": "디기탈리스",
        "Golden Spined Cactus": "황금 가시 선인장",
        "Green Apple Fruit": "초록 사과 열매",
        "Holly Berry Leaves": "호랑가시나무 열매 잎",
        "Hydrangea Hedge": "수국 생울타리",
        "Incan Lily": "잉카 백합",
        "Japanese Orchid": "일본 난초",
        "Kovan Flower": "코반 꽃",
        "Lazarus Bellflower": "라자루스 초롱꽃",
        "Leaf Pile": "낙엽 더미",
        "Lollipop Flower": "롤리팝 꽃",
        "Lush Dirt": "무성한 흙",
        "Lush Dirt Path": "무성한 흙길",
        "Lush Farmland": "무성한 경작지",
        "Lush Grass Block": "무성한 잔디 블록",
        "Mini Cactus": "미니 선인장",
        "Oddion Crop": "오디온 작물",
        "Osiria Rose": "오시리아 장미",
        "Packed Black Ice": "꽁꽁 언 검은 얼음",
        "Packed Borealis Ice": "꽁꽁 언 북극광 얼음",
        "Packed Pale Mud": "다져진 창백한 진흙",
        "Pale Jack O Lantern": "창백한 잭오랜턴",
        "Pale Mud": "창백한 진흙",
        "Pale Mud Bricks": "창백한 진흙 벽돌",
        "Pale Mud Bricks Slab": "창백한 진흙 벽돌 반 블록",
        "Pale Mud Bricks Stairs": "창백한 진흙 벽돌 계단",
        "Pale Mud Bricks Wall": "창백한 진흙 벽돌 담장",
        "Podzol Dacite": "회백토 데이사이트",
        "Poison Ivy": "독성 담쟁이덩굴",
        "Potted Fairy Slipper": "화분에 심은 요정 슬리퍼꽃",
        "Potted Golden Spined Cactus": "화분에 심은 황금 가시 선인장",
        "Potted Incan Lily": "화분에 심은 잉카 백합",
        "Potted Kovan Flower": "화분에 심은 코반 꽃",
        "Potted Lazarus Bellflower": "화분에 심은 라자루스 초롱꽃",
        "Potted Lollipop Flower": "화분에 심은 롤리팝 꽃",
        "Potted Mini Cactus": "화분에 심은 미니 선인장",
        "Potted Osiria Rose": "화분에 심은 오시리아 장미",
        "Potted Protea Flower": "화분에 심은 프로테아 꽃",
        "Potted Shrub": "화분에 심은 관목",
        "Potted Silver Vase Flower": "화분에 심은 은빛 화병꽃",
        "Potted Winter Cyclamen": "화분에 심은 겨울 시클라멘",
        "Potted Winter Rose": "화분에 심은 겨울 장미",
        "Potted Winter Scilla": "화분에 심은 겨울 무릇",
        "Potted Winter Succulent": "화분에 심은 겨울 다육식물",
        "Prairie Grass": "프레리 잔디",
        "Protea Flower": "프로테아 꽃",
        "Pumpkin Burrow": "호박 굴",
        "Quicksand": "유사",
        "Red Quicksand": "붉은 유사",
        "Red Rock Tile Slab": "붉은 바위 타일 반 블록",
        "Red Rock Tile Stairs": "붉은 바위 타일 계단",
        "Ripe Baobab Leaves": "열매가 익은 바오밥 잎",
        "Ripe Orchard Leaves": "열매가 익은 과수원 나무 잎",
        "Ripe Yucca Leaves": "열매가 익은 유카 잎",
        "Rocky Stone": "울퉁불퉁한 돌",
        "Rocky Stone Slab": "울퉁불퉁한 돌 반 블록",
        "Rocky Stone Stairs": "울퉁불퉁한 돌 계단",
        "Rocky Stone Wall": "울퉁불퉁한 돌 담장",
        "Sandy Dirt": "모래투성이 흙",
        "Sandy Dirt Path": "모래투성이 흙길",
        "Sandy Farmland": "모래투성이 경작지",
        "Shelf Fungi": "선반버섯",
        "Shrub": "관목",
        "Silver Vase Flower": "은빛 화병꽃",
        "Skyris Vine": "스카이리스 덩굴",
        "Smooth Windswept Sandstone": "매끄러운 바람맞이 사암",
        "Smooth Windswept Sandstone Slab": "매끄러운 바람맞이 사암 반 블록",
        "Smooth Windswept Sandstone Stairs": "매끄러운 바람맞이 사암 계단",
        "Soul Fruit": "영혼 열매",
        "Tall Beach Grass": "키 큰 해변 잔디",
        "Tall Prairie Grass": "키 큰 프레리 잔디",
        "Tiny Lily Pads": "작은 수련잎",
        "Water Silk": "물실크",
        "Weeping Milkcap": "눈물젖버섯",
        "Weeping Milkcap Mushroom Block": "눈물젖버섯 블록",
        "White Dacite Tile Slab": "흰색 데이사이트 타일 반 블록",
        "White Dacite Tile Stairs": "흰색 데이사이트 타일 계단",
        "White Overgrown Dacite": "흰색 식생으로 뒤덮인 데이사이트",
        "White Podzol Dacite": "흰 회백토 데이사이트",
        "White Sakura Petals": "흰 벚꽃잎",
        "Windswept Sand": "바람맞이 모래",
        "Windswept Sandstone": "바람맞이 사암",
        "Windswept Sandstone Pillar": "바람맞이 사암 기둥",
        "Windswept Sandstone Slab": "바람맞이 사암 반 블록",
        "Windswept Sandstone Stairs": "바람맞이 사암 계단",
        "Windswept Sandstone Wall": "바람맞이 사암 담장",
        "Winter Cyclamen": "겨울 시클라멘",
        "Winter Rose": "겨울 장미",
        "Winter Scilla": "겨울 무릇",
        "Winter Succulent": "겨울 다육식물",
        "Witch Hazel Blossom": "풍년화 꽃",
        "Wood Blewit": "자주방망이버섯",
        "Wood Blewit Mushroom Block": "자주방망이버섯 블록",
        "Yellow Sakura Petals": "노란 벚꽃잎",
    }
)

EXACT_TEXT.update(
    {
        "Collect every Bioshroom Stem type.": "모든 바이오버섯 줄기 종류 모으기",
        "Ancient Specimens": "고대 표본",
        "Consume a Duskmelon.": "황혼멜론 먹기",
        "Blind as a Bat": "박쥐처럼 눈먼",
        "Discover the many biomes and explore the world!": (
            "수많은 생물군계를 발견하고 세계를 탐험하세요!"
        ),
        "Walk through and take damage from a Dorcel Flower.": (
            "도르셀 꽃을 지나가며 피해 입기"
        ),
        "Downer": "기분을 가라앉히는 것",
        "Venture into all Nether biomes from Regions Unexplored!": (
            "Regions Unexplored의 모든 네더 생물군계 탐험하기!"
        ),
        "Eternal Expedition": "영원한 원정",
        "Collect or craft every colour of the Snowbelle Flower.": (
            "모든 색상의 스노벨 꽃을 모으거나 제작하기"
        ),
        "Every Bit of the Rainbow": "무지개의 모든 빛깔",
        "Hang from a Kapok tree's vines.": "카폭나무 덩굴에 매달리기",
        "From the Tree Tops": "나무 꼭대기에서",
        "Collect every log from Regions Unexplored.": (
            "Regions Unexplored의 모든 원목 모으기"
        ),
        "Got Wood?": "나무 좀 있나?",
        "Walk or bounce on a Giant Lily Pad.": "거대한 수련잎 위를 걷거나 튀어 오르기",
        "Light as a Frog": "개구리처럼 가볍게",
        "Consume a Hanging Earlight Fruit.": "매달린 얼라이트 열매 먹기",
        "Light Snack": "가벼운 간식",
        "Collect every Bioshroom type.": "모든 바이오버섯 종류 모으기",
        "Mycologist": "균류학자",
        "Explore all Surface biomes from Regions Unexplored!": (
            "Regions Unexplored의 모든 지표 생물군계 탐험하기!"
        ),
        "Pioneer": "개척자",
        "You've explored all the biomes from Regions Unexplored": (
            "Regions Unexplored의 모든 생물군계를 탐험했어요"
        ),
        "Regions Explored": "탐험한 지역들",
        "Find all Cave biomes from Regions Unexplored!": (
            "Regions Unexplored의 모든 동굴 생물군계 찾기!"
        ),
        "Spelunker": "동굴 탐험가",
        "Chop down a Socotra tree.": "소코트라 나무 베기",
        "This Tree Bleeds Red": "이 나무는 붉은 피를 흘린다",
        "Alpha Dandelion": "알파 민들레",
        "Alpha Grass Block": "알파 잔디 블록",
        "Alpha Rose": "알파 장미",
        "Argillite": "이판암",
        "Argillite Grass Block": "이판암 잔디 블록",
        "Ash": "재",
        "Ash Vent": "화산재 분출구",
        "Ashen Dirt": "잿빛 흙",
        "Ashen Grass": "잿빛 잔디",
        "Ashen Shrub": "잿빛 관목",
        "Aster": "과꽃",
        "Barley": "보리",
        "Blackstone Cluster": "흑암 군집",
        "Bladed Grass": "칼날 잔디",
        "Bladed Tall Grass": "키 큰 칼날 잔디",
        "Bleeding Heart": "금낭화",
        "Brimsprout": "브림 새싹",
        "Brimsprout Nylium": "브림 새싹 네사체",
        "Brimwood Log Magma": "마그마가 밴 브림우드 원목",
        "Cactus Flower": "선인장 꽃",
        "Cave Hyssop": "동굴 히솝",
        "Cherry Branch": "벚나무 가지",
        "Cherry Shrub": "벚나무 관목",
        "Cobalt Obsidian": "코발트 흑요석",
        "Cobalt Earlight": "코발트 얼라이트",
        "Cobalt Nylium": "코발트 네사체",
        "Cobalt Roots": "코발트 뿌리",
        "Cobalt Webbing": "코발트 거미줄",
        "Corpse Flower": "시체꽃",
        "Day Lily": "원추리",
        "Dead Branch": "고사목 가지",
        "Dead Button": "고사목 버튼",
        "Dead Door": "고사목 문",
        "Dead Fence": "고사목 울타리",
        "Dead Fence Gate": "고사목 울타리 문",
        "Dead Hanging Sign": "고사목 매다는 표지판",
        "Dead Leaves": "마른 잎",
        "Dead Log": "고사목 원목",
        "Dead Planks": "고사목 판자",
        "Dead Pressure Plate": "고사목 감압판",
        "Dead Sapling": "고사목 묘목",
        "Dead Shrub": "말라 죽은 관목",
        "Dead Sign": "고사목 표지판",
        "Dead Slab": "고사목 반 블록",
        "Dead Stairs": "고사목 계단",
        "Dead Trapdoor": "고사목 다락문",
        "Dead Wood": "고사목",
        "Deepslate Grass Block": "심층암 잔디 블록",
        "Dropleaf": "물방울잎",
        "Duckweed": "개구리밥",
        "Duskmelon Slice": "황혼멜론 조각",
        "Dusktrap": "황혼덫",
        "Elephant Ear": "코끼리귀",
        "Felicia Daisy": "펠리시아 데이지",
        "Fireweed": "분홍바늘꽃",
        "Flowering Leaves": "꽃피는 나무 잎",
        "Flowering Lily Pad": "꽃이 핀 수련잎",
        "Flowering Sapling": "꽃피는 나무 묘목",
        "Flowering Shrub": "꽃피는 관목",
        "Frozen Grass": "얼어붙은 잔디",
        "Giant Lily Pad": "거대한 수련잎",
        "Glister Bulb": "글리스터 알뿌리",
        "Glister Spire": "글리스터 첨탑",
        "Glistering Bloom": "반짝이는 꽃송이",
        "Glistering Fern": "반짝이는 고사리",
        "Glistering Ivy": "반짝이는 담쟁이덩굴",
        "Glistering Nylium": "반짝이는 네사체",
        "Glistering Sprout": "반짝이는 새싹",
        "Glistering Wart": "반짝이는 사마귀",
        "Hibiscus": "히비스커스",
        "Hyacinth Lamp": "히아신스 램프",
        "Icicle": "고드름",
        "Mallow": "아욱",
        "Meadow Sage": "목초지 세이지",
        "Medium Grass": "중간 크기 잔디",
        "Mycotoxic Grass": "균독성 잔디",
        "Mycotoxic Moss": "균독성 이끼",
        "Mycotoxic Mushrooms": "균독성 버섯",
        "Overgrown Bone Block": "식생으로 뒤덮인 뼈 블록",
        "Peat Coarse Dirt": "거친 이탄 흙",
        "Pointed Redstone": "뾰족한 레드스톤",
        "Prismaglass": "프리즈마유리",
        "Raw Redstone Block": "원시 레드스톤 블록",
        "Redstone Bud": "레드스톤 싹",
        "Redstone Bulb": "레드스톤 알뿌리",
        "Salmon Poppy Bush": "연어색 양귀비 덤불",
        "Salmonberry": "새먼베리",
        "Sandy Grass": "모래투성이 잔디",
        "Sandy Tall Grass": "키 큰 모래투성이 잔디",
        "Silt Coarse Dirt": "거친 실트 흙",
        "Small Desert Shrub": "작은 사막 관목",
        "Stripped Dead Log": "껍질 벗긴 고사목 원목",
        "Stripped Dead Wood": "껍질 벗긴 고사목",
        "Steppe Tall Grass": "키 큰 스텝 잔디",
        "Tall Hyacinth Stock": "키 큰 히아신스 줄기",
        "Tassel": "술 장식",
        "Tsubaki": "동백꽃",
        "Volcanic Ash": "화산재",
        "Waratah": "와라타",
        "Windswept Grass": "바람에 휩쓸린 잔디",
        "%s was dragged underground by Dorcel": "%s이(가) 도르셀에게 땅속으로 끌려갔어요",
        "%s was eaten by a Dusktrap": "%s이(가) 황혼덫에게 먹혔어요",
    }
)

EXACT_TEXT.update(
    {
        "%s got too curious and put a cattail in a campfire": (
            "%s이(가) 호기심을 못 참고 모닥불에 부들을 넣었어요"
        ),
        "%s tried to swim in the desert": "%s이(가) 사막에서 헤엄치려 했어요",
        "Man O' War": "군함해파리",
        "Oddion": "오디온",
        "Pumpkin Warden": "호박 감시자",
        "Bog Trial Explorer Map": "습원 시련 탐험 지도",
        "Allium Oddion Soup": "알리움 오디온 수프",
        "Aloe Vera Juice": "알로에 베라 주스",
        "Blooming Oddion": "꽃이 핀 오디온",
        "Blueberries": "블루베리",
        "Blueberry Pie": "블루베리 파이",
        "Cooked Oddion Bulb": "익힌 오디온 알뿌리",
        "Cooked White Puffball Cap": "익힌 흰 말불버섯 갓",
        "Cooked Yucca Fruit": "익힌 유카 열매",
        "Green Apple Pie": "초록 사과 파이",
        "Holly Wreath": "호랑가시나무 리스",
        "Man O War Bucket": "군함해파리 양동이",
        "Man O War Spawn Egg": "군함해파리 생성 알",
        "Mushroom Wreath": "버섯 리스",
        "Oddion Bulb": "오디온 알뿌리",
        "Oddion Spawn Egg": "오디온 생성 알",
        "Oddion Wreath": "오디온 리스",
        "Pale Pumpkin Seeds": "창백한 호박씨",
        "Petal Wreath": "꽃잎 리스",
        "Pumpkin Warden Spawn Egg": "호박 감시자 생성 알",
        "Rosy Wreath": "장밋빛 리스",
        "White Puffball Cap": "흰 말불버섯 갓",
        "White Puffball Spores": "흰 말불버섯 포자",
        "White Puffball Stew": "흰 말불버섯 스튜",
        "Winter Rosy Wreath": "겨울 장밋빛 리스",
        "Wreath": "리스",
        "Soul Fruit wails": "영혼 열매가 울부짖음",
        "Oddion purrs": "오디온이 가르랑거림",
        "Oddion dies": "오디온이 죽음",
        "Oddion happy purrs": "오디온이 기분 좋게 가르랑거림",
        "Oddion hurts": "오디온이 다침",
    }
)


def find_jar(modid: str) -> Path:
    """현재 설치본에서 모드 JAR 하나를 찾아요."""
    pattern = str(MODS[modid]["jar"])
    matches = sorted((resolve_source_root() / "mods").glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"{modid} JAR이 정확히 한 개가 아니에요: {matches}")
    return matches[0]


def read_language(modid: str) -> dict[str, str]:
    """현재 영어 언어 파일을 읽어요."""
    with ZipFile(find_jar(modid)) as archive:
        value = json.loads(archive.read(f"assets/{modid}/lang/en_us.json"))
    expected = int(MODS[modid]["keys"])
    if not isinstance(value, dict) or len(value) != expected:
        raise ValueError(f"{modid} 영어 키 수가 달라요: {len(value)} != {expected}")
    if not all(
        isinstance(key, str) and isinstance(text, str) for key, text in value.items()
    ):
        raise TypeError(f"{modid} 언어 키 또는 값이 문자열이 아니에요")
    return value


def translate_base(source: str) -> str:
    """목재·식물·색상으로 이루어진 이름의 바탕 부분을 번역해요."""
    if source in COLORS:
        return COLORS[source]
    if source in ADJECTIVES:
        return ADJECTIVES[source]
    if source in BASES:
        return BASES[source]
    if source in BASE_NOUNS:
        return BASE_NOUNS[source]
    for color in sorted(COLORS, key=len, reverse=True):
        prefix = f"{color} "
        if source.startswith(prefix):
            rest = source[len(prefix) :]
            return f"{COLORS[color]} {translate_base(rest)}"
    for adjective in sorted(ADJECTIVES, key=len, reverse=True):
        prefix = f"{adjective} "
        if source.startswith(prefix):
            rest = source[len(prefix) :]
            return f"{ADJECTIVES[adjective]} {translate_name(rest)}"
    raise KeyError(source)


def translate_name(source: str) -> str:
    """블록·아이템 검색명을 조합 규칙으로 번역해요."""
    if source in EXACT_TEXT:
        return EXACT_TEXT[source]
    if source in COLORS or source in ADJECTIVES:
        return translate_base(source)
    if source in BASES or source in BASE_NOUNS:
        return translate_base(source)
    if source.startswith("Potted "):
        return f"화분에 심은 {translate_name(source.removeprefix('Potted '))}"
    if source.startswith("Stripped "):
        return f"껍질 벗긴 {translate_name(source.removeprefix('Stripped '))}"
    for adjective in sorted(ADJECTIVES, key=len, reverse=True):
        prefix = f"{adjective} "
        if source.startswith(prefix):
            return f"{ADJECTIVES[adjective]} {translate_name(source[len(prefix) :])}"
    if source.endswith(" Boat with Chest"):
        base = source.removesuffix(" Boat with Chest")
        return f"상자가 실린 {translate_base(base)} 보트"
    if source.endswith(" Boat"):
        return f"{translate_base(source.removesuffix(' Boat'))} 보트"
    if source.endswith(" Spawn Egg"):
        return f"{translate_name(source.removesuffix(' Spawn Egg'))} 생성 알"
    for suffix, translated_suffix in SUFFIXES:
        marker = f" {suffix}"
        if source.endswith(marker):
            base = source.removesuffix(marker)
            if suffix.startswith("Painted"):
                return f"{translate_name(base)}으로 {translated_suffix}"
            translated_base = translate_name(base)
            if suffix == "Wood" and translated_base.endswith("나무"):
                return translated_base
            return f"{translated_base} {translated_suffix}"
    for color in sorted(COLORS, key=len, reverse=True):
        prefix = f"{color} "
        if source.startswith(prefix):
            return f"{COLORS[color]} {translate_name(source[len(prefix) :])}"
    raise KeyError(source)


def translate_value(key: str, source: str) -> str:
    """언어 키와 현재 영어 원문을 기준으로 확정 번역을 반환해요."""
    if source == "":
        return ""
    if source in EXACT_TEXT:
        return EXACT_TEXT[source]
    if key.startswith("biome."):
        return BIOMES[source]
    if key.startswith(("block.", "item.")):
        return translate_name(source)
    raise KeyError(source)


def prepare() -> dict[str, object]:
    """현재 JAR과 영어 원문 범위를 작업 폴더에 기록해요."""
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    inventory = {"family": FAMILY, "mods": {}, "status": "prepared"}
    for modid in MODS:
        jar = find_jar(modid)
        english = read_language(modid)
        (WORK_ROOT / modid).mkdir(parents=True, exist_ok=True)
        (WORK_ROOT / modid / "en_us.json").write_text(
            json.dumps(english, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        inventory["mods"][modid] = {
            "jar": jar.name,
            "jar_size": jar.stat().st_size,
            "jar_mtime_ns": jar.stat().st_mtime_ns,
            "english_keys": len(english),
            "bundled_korean_keys": 0,
        }
    (WORK_ROOT / "inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return inventory


def build() -> dict[str, object]:
    """두 모드의 현재 영어 2,005개를 모두 번역해요."""
    reports = {}
    all_errors = []
    for modid in MODS:
        english = read_language(modid)
        korean = {}
        errors = []
        for key, source in english.items():
            try:
                korean[key] = translate_value(key, source)
            except (KeyError, RecursionError) as exc:
                errors.append(f"{key}={source!r}: {exc}")
        if not errors:
            paths = (
                WORK_ROOT / modid / "ko_kr.json",
                OUTPUT_ROOT / modid / "lang/ko_kr.json",
            )
            for path in paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    json.dumps(korean, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        reports[modid] = {
            "translated": len(korean),
            "expected": MODS[modid]["keys"],
            "errors": errors,
            "status": "complete" if not errors else "incomplete",
        }
        all_errors.extend(f"{modid}: {error}" for error in errors)
    report = {
        "family": FAMILY,
        "mods": reports,
        "errors": all_errors,
        "status": "complete" if not all_errors else "incomplete",
    }
    (WORK_ROOT / "language_build.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def walk_json(value: object, path: str = "$") -> list[tuple[str, str, object]]:
    """JSON 안의 모든 키와 경로를 재귀적으로 모아요."""
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


def related_quest_review(instance: Path) -> tuple[dict[str, object], list[str]]:
    """두 모드와 연결된 퀘스트·Task의 실제 표시 키를 전부 검수해요."""
    quest_root = instance / "config/ftbquests/quests"
    related_ids = set()
    contexts = []
    for path in sorted((quest_root / "chapters").glob("*.snbt")):
        text = path.read_text(encoding="utf-8-sig")
        for quest_block in quest_audit.list_objects(text, "quests"):
            if not any(f"{modid}:" in quest_block for modid in MODS):
                continue
            quest_id = quest_audit.scalar_string(quest_block, "id")
            task_ids = []
            related_ids.add(quest_id)
            for task_block in quest_audit.list_objects(quest_block, "tasks"):
                task_id = quest_audit.scalar_string(task_block, "id")
                related_ids.add(task_id)
                task_ids.append(task_id)
            contexts.append(
                {
                    "chapter": path.name,
                    "quest_id": quest_id,
                    "task_ids": task_ids,
                }
            )

    english = quest_snbt.parse_language_snbt(quest_root / "lang/en_us.snbt")
    korean = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    related_keys = sorted(
        key
        for key, value in english.items()
        if key.split(".", 2)[1] in related_ids
        or any(
            name in json.dumps(value, ensure_ascii=False)
            for name in ("Regions Unexplored", "Oh The Biomes We've Gone")
        )
    )
    errors = []
    for key in related_keys:
        target = korean.get(key)
        if target is None:
            errors.append(f"관련 퀘스트 한국어 키가 없어요: {key}")
            continue
        source_text = json.dumps(english[key], ensure_ascii=False)
        target_text = json.dumps(target, ensure_ascii=False)
        errors.extend(preserved_errors(f"FTB Quests {key}", source_text, target_text))
    for key, expected in QUEST_CORRECTIONS.items():
        if korean.get(key) != expected:
            errors.append(f"관련 퀘스트 확정 번역값이 달라요: {key}")

    forbidden = {
        "리전스 언익스플로어드",
        "오 더 바이옴스 위브 곤",
        "데사이트",
        "바위 돌",
        "채집가 테이블",
        "페인트 칠한 판자",
    }
    forbidden_hits = {}
    for key in related_keys:
        target_text = json.dumps(korean.get(key), ensure_ascii=False)
        hits = sorted(term for term in forbidden if term in target_text)
        if hits:
            forbidden_hits[key] = hits
    if forbidden_hits:
        errors.append(f"관련 퀘스트에 폐기한 번역이 남았어요: {forbidden_hits}")

    report = {
        "quest_contexts": contexts,
        "related_object_ids": sorted(related_ids),
        "related_keys": related_keys,
        "reviewed_keys": len(related_keys),
        "corrected_keys": len(QUEST_CORRECTIONS),
        "reviewed_reused_keys": len(related_keys) - len(QUEST_CORRECTIONS),
        "forbidden_translation_hits": forbidden_hits,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR 데이터와 FTB Quests·KubeJS의 별도 표시 문구를 감사해요."""
    instance = resolve_source_root()
    errors = []
    jar_reports = []
    for modid in MODS:
        jar = find_jar(modid)
        data_counts: defaultdict[str, int] = defaultdict(int)
        advancement_displays = []
        localized_fields = []
        direct_fields = []
        invalid_json = []
        with ZipFile(jar) as archive:
            for name in sorted(archive.namelist()):
                if not name.startswith(f"data/{modid}/") or not name.endswith(".json"):
                    continue
                parts = name.split("/")
                if len(parts) >= 3:
                    data_counts[parts[2]] += 1
                try:
                    value = json.loads(archive.read(name))
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    invalid_json.append(f"{name}: {exc}")
                    continue
                if "/advancement/" in name and isinstance(value, dict):
                    display = value.get("display")
                    if display is not None:
                        advancement_displays.append({"file": name, "display": display})
                for key, path, child in walk_json(value):
                    if key not in VISIBLE_DATA_KEYS:
                        continue
                    row = {"file": name, "path": path, "value": child}
                    if isinstance(child, dict) and isinstance(
                        child.get("translate"), str
                    ):
                        localized_fields.append(row)
                    elif isinstance(child, str) or child is not None:
                        direct_fields.append(row)
        if invalid_json:
            errors.extend(f"{modid}: {message}" for message in invalid_json)
        if direct_fields:
            errors.append(f"{modid} 데이터에 직접 표시 문구가 있어요: {direct_fields}")
        jar_reports.append(
            {
                "modid": modid,
                "jar": jar.name,
                "data_json_files": sum(data_counts.values()),
                "data_counts": dict(sorted(data_counts.items())),
                "advancement_files": data_counts["advancement"],
                "advancement_displays": advancement_displays,
                "recipe_files": data_counts["recipe"],
                "localized_data_fields": localized_fields,
                "direct_visible_data_fields": direct_fields,
                "invalid_json": invalid_json,
            }
        )

    references = {"ftbquests": [], "kubejs": [], "read_errors": []}
    suffixes = {".cfg", ".js", ".json", ".snbt", ".toml", ".txt"}
    for label, base in (
        ("ftbquests", instance / "config/ftbquests/quests/chapters"),
        ("kubejs", instance / "kubejs"),
    ):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                references["read_errors"].append(f"{path}: {exc}")
                continue
            counts = {modid: text.count(f"{modid}:") for modid in MODS}
            if not any(counts.values()):
                continue
            visible_lines = []
            for number, line in enumerate(text.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("//") or not any(
                    f"{modid}:" in line for modid in MODS
                ):
                    continue
                if re.search(
                    r"(?i)(?:custom_name|displayname|display_name|lore|title|tooltip)"
                    r"\s*[:=(]",
                    line,
                ):
                    visible_lines.append(number)
            row = {
                "path": path.relative_to(instance).as_posix(),
                "namespace_occurrences": counts,
                "visible_namespace_candidate_lines": visible_lines,
            }
            references[label].append(row)
            if visible_lines:
                errors.append(f"{label}에 직접 표시 문구 후보가 있어요: {row}")
    errors.extend(str(value) for value in references["read_errors"])

    quests, quest_errors = related_quest_review(instance)
    errors.extend(quest_errors)
    report = {
        "family": FAMILY,
        "jars": jar_reports,
        "references": references,
        "ftbquests": quests,
        "ftbquests_display_work": "related_keys_reviewed_and_corrected",
        "kubejs_display_work": "ids_only",
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "surface_audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
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
        errors.append(
            f"{label} 실제 줄바꿈 수 불일치: "
            f"{source.count(chr(10))} != {target.count(chr(10))}"
        )
    source_escaped_lines = source.count("\\n")
    target_escaped_lines = target.count("\\n")
    if source_escaped_lines != target_escaped_lines:
        errors.append(
            f"{label} 이스케이프 줄바꿈 수 불일치: "
            f"{source_escaped_lines} != {target_escaped_lines}"
        )
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
    """두 모드 2,005개 키의 구조와 확정 번역값을 전부 검증해요."""
    errors = []
    mod_reports = []
    all_names: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
    allowed_latin = {
        "AOCAWOL",
        "BWG",
        "Better",
        "Biomes",
        "Club",
        "Days",
        "Gone",
        "Oh",
        "Pixie",
        "Regions",
        "The",
        "Unexplored",
        "We",
        "ve",
    }
    intentional_same = {
        "AOCAWOL - Better Days",
        "AOCAWOL - Pixie Club",
        "Biomes We've Gone",
        "Oh The Biomes We've Gone",
        "Regions Unexplored",
    }
    total_keys = 0
    for modid in MODS:
        english = read_language(modid)
        work, work_errors = load_json_without_duplicates(
            WORK_ROOT / modid / "ko_kr.json"
        )
        output, output_errors = load_json_without_duplicates(
            OUTPUT_ROOT / modid / "lang/ko_kr.json"
        )
        current_errors = work_errors + output_errors
        if not isinstance(work, dict) or not isinstance(output, dict):
            errors.extend(f"{modid}: {message}" for message in current_errors)
            continue
        expected = {
            key: translate_value(key, source) for key, source in english.items()
        }
        if list(english) != list(work) or list(english) != list(output):
            current_errors.append("언어 키 또는 순서가 현재 영어 원문과 달라요")
        if work != output or output != expected:
            current_errors.append("작업본·산출물·확정 번역값이 서로 달라요")
        untranslated = []
        latin_residue = {}
        repeated_words = {}
        for key, source in english.items():
            target = output.get(key)
            if not isinstance(target, str):
                current_errors.append(f"문자열이 아닌 번역값이 있어요: {key}")
                continue
            current_errors.extend(preserved_errors(key, source, target))
            if source == target and source and source not in intentional_same:
                untranslated.append(key)
            residue = sorted(set(LATIN_WORD.findall(target)) - allowed_latin)
            if residue:
                latin_residue[key] = residue
            repeated = re.findall(r"\b([가-힣]{2,})\s+\1\b", target)
            if repeated:
                repeated_words[key] = repeated
            if key.startswith(("block.", "item.", "biome.")):
                all_names[target].append((modid, key))
        if untranslated:
            current_errors.append(f"영어와 같은 미번역 후보가 있어요: {untranslated}")
        if latin_residue:
            current_errors.append(f"허용하지 않은 영문 잔여가 있어요: {latin_residue}")
        if repeated_words:
            current_errors.append(f"연속 중복 단어가 있어요: {repeated_words}")
        mod_reports.append(
            {
                "modid": modid,
                "keys": len(output),
                "expected_keys": MODS[modid]["keys"],
                "bundled_korean_reused": 0,
                "new_translations": len(output),
                "untranslated_candidates": untranslated,
                "latin_residue": latin_residue,
                "repeated_words": repeated_words,
                "errors": current_errors,
                "status": "complete" if not current_errors else "incomplete",
            }
        )
        total_keys += len(output)
        errors.extend(f"{modid}: {message}" for message in current_errors)

    collisions = {}
    english_by_key = {
        (modid, key): source
        for modid in MODS
        for key, source in read_language(modid).items()
    }
    for target, rows in all_names.items():
        sources = {english_by_key[row] for row in rows}
        if len(sources) > 1:
            collisions[target] = [{"modid": modid, "key": key} for modid, key in rows]
    if collisions:
        errors.append(f"서로 다른 검색명이 같은 한국어로 충돌해요: {collisions}")
    report = {
        "mods": mod_reports,
        "keys": total_keys,
        "expected_keys": sum(int(value["keys"]) for value in MODS.values()),
        "unexpected_name_collisions": collisions,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """언어·퀘스트·전체 표시 표면을 함께 검증해요."""
    language, language_errors = verify_language()
    surface, surface_errors = audit()
    errors = language_errors + surface_errors
    report = {
        "family": FAMILY,
        "language": language,
        "ftbquests": surface["ftbquests"],
        "surface_audit": surface["status"],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "family_validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    quest_report = surface["ftbquests"]
    translation_report = {
        "family": FAMILY,
        "reviewed_language_keys": language.get("keys", 0),
        "existing_korean_reused": quest_report["reviewed_reused_keys"],
        "new_language_translations": language.get("keys", 0),
        "ftbquests_reviewed_keys": quest_report["reviewed_keys"],
        "ftbquests_corrected_keys": quest_report["corrected_keys"],
        "ftbquests_reviewed_reused_keys": quest_report["reviewed_reused_keys"],
        "kubejs_work": "ids_only",
        "status": report["status"],
    }
    (WORK_ROOT / "translation_report.json").write_text(
        json.dumps(translation_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = (
        json.loads(deployment_path.read_text(encoding="utf-8"))
        if deployment_path.is_file()
        else None
    )
    completion = {
        "family": FAMILY,
        "language_keys": language.get("keys", 0),
        "existing_korean_reused": quest_report["reviewed_reused_keys"],
        "new_or_corrected_translations": language.get("keys", 0)
        + quest_report["corrected_keys"],
        "ftbquests": quest_report,
        "kubejs_work": "ids_only",
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
    (WORK_ROOT / "family_completion.json").write_text(
        json.dumps(completion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report, errors


def deployment_paths() -> set[str]:
    """이 모드 묶음이 실제 인스턴스에 적용할 정확한 상대 경로를 반환해요."""
    return {
        "config/ftbquests/quests/lang/ko_kr.snbt",
        "resourcepacks/ATM10_Korean/assets/biomeswevegone/lang/ko_kr.json",
        "resourcepacks/ATM10_Korean/assets/regions_unexplored/lang/ko_kr.json",
    }


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 매니페스트의 대상·백업·해시 결과를 작업 기록에 연결해요."""
    errors = []
    manifest_path = manifest_path.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 매니페스트 상태가 완료가 아니에요")
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
    (WORK_ROOT / "deployment_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    verification, verification_errors = verify()
    return {
        "deployment": report,
        "verification": verification["status"],
        "status": "complete"
        if not errors and not verification_errors
        else "incomplete",
    }, errors + verification_errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "prepare",
            "build",
            "audit",
            "verify",
            "record-deployment",
            "all",
        ),
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
