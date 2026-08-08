#!/usr/bin/env python3
"""설치된 Macaw's 건축 모드 11종의 전체 표시 문자열을 번역·검증해요."""

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
from chipped_family import load_json, write_json
from dungeons_arise_family import (
    VISIBLE_DATA_KEYS,
    component_literal_text,
    scan_visible_nbt,
    walk_json,
)
from local_paths import PROJECT_ROOT, resolve_source_root

FAMILY = "macaws_family"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
MODS = {
    "mcwbridges": "mcw-bridges-*.jar",
    "mcwdoors": "mcw-doors-*.jar",
    "mcwfurnitures": "mcw-furniture-*.jar",
    "mcwholidays": "mcw-holidays-*.jar",
    "mcwlights": "mcw-lights-*.jar",
    "mcwfences": "mcw-mcwfences-*.jar",
    "mcwpaths": "mcw-mcwpaths-*.jar",
    "mcwstairs": "mcw-mcwstairs-*.jar",
    "mcwwindows": "mcw-mcwwindows-*.jar",
    "mcwroofs": "mcw-roofs-*.jar",
    "mcwtrpdoors": "mcw-trapdoors-*.jar",
}
OUTPUTS = {
    namespace: (
        PROJECT_ROOT
        / f"output/resourcepack/ATM10_Korean/assets/{namespace}/lang/ko_kr.json"
    )
    for namespace in MODS
}
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
DEPLOYMENT_PATHS = [
    f"resourcepacks/ATM10_Korean/assets/{namespace}/lang/ko_kr.json"
    for namespace in MODS
] + ["config/ftbquests/quests/lang/ko_kr.snbt"]

PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]|&#[0-9A-Fa-f]{6}")
NUMBER = re.compile(r"\d+(?:[.+xX×-]\d+)*")
HANGUL = re.compile(r"[가-힣]")
NAME_TOKEN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+")

UI_TRANSLATIONS = {
    "itemGroup.mcwbridges": "Macaw's Bridges",
    "mcwbridges.pliers.desc": (
        "너비가 2블록 이상인 다리를 우클릭하면 난간에 입구를 만들 수 있습니다."
    ),
    "mcwbridges.bridges.desc": "펜치나 가위로 입구를 조정할 수 있습니다.",
    "mcwbridges.light.desc": "다리와 계단 난간에 사용합니다.",
    "itemGroup.mcwdoors": "Macaw's Doors",
    "mcwdoors.crafting.desc": "제작 재료",
    "subtitle.mcwdoors.shoji": "장지문이 열림",
    "subtitle.mcwdoors.garage": "차고 문이 열림",
    "mcwdoors.metaldoor.desc": "열려면 레드스톤 신호가 필요합니다.",
    "mcwdoors.garage.desc": ("천장에 하나만 설치하세요. 문을 열면 아래로 펼쳐집니다."),
    "itemGroup.mcwfurnitures": "Macaw's Furniture",
    "subtitle.mcwfurnitures.drawer_open": "서랍이 열림",
    "subtitle.mcwfurnitures.drawer_close": "서랍이 닫힘",
    "subtitle.mcwfurnitures.cabinet_open": "수납장이 열림",
    "subtitle.mcwfurnitures.cabinet_close": "수납장이 닫힘",
    "mcwfurnitures.container.threerows": "가구 보관함",
    "mcwfurnitures.furnitureitem.desc": "제작 재료",
    "itemGroup.halloween": "Macaw's Holidays (Autumn)",
    "itemGroup.christmas": "Macaw's Holidays (Christmas)",
    "mcwholidays.toggle.desc": "우클릭하여 변형을 전환합니다.",
    "itemGroup.mcwlights": "Macaw's Lights and Lamps",
    "subtitle.mcwlights.light_switch": "조명 스위치를 누름",
    "subtitle.mcwlights.torch_on": "티키 횃불을 점화함",
    "mcwlights.lights.tikitorchinfo": (
        "위에 같은 블록을 놓으면 더 높게 쌓을 수 있습니다."
    ),
    "mcwlights.lights.dyeableinfo": "염료로 우클릭하여 색을 바꿀 수 있습니다.",
    "mcwlights.lights.stackableinfo": (
        "위에 같은 블록을 놓으면 더 높게 쌓을 수 있습니다."
    ),
    "itemGroup.mcwfences": "Macaw's Fences & Walls",
    "death.attack.wired_fence": "%1$s이(가) 철조망을 넘으려다 다쳤습니다.",
    "death.attack.wired_fence.player": (
        "%1$s이(가) %2$s에게서 달아나다 철조망을 넘으려 했습니다."
    ),
    "mcwfences.stackable.desc": "위로 쌓아 더 높게 만들 수 있습니다.",
    "itemGroup.mcwpaths": "Macaw's Paths & Pavings",
    "mcwpaths.engraved.desc": "곡괭이로 우클릭하여 무늬를 새깁니다.",
    "mcwpaths.flattened.desc": "삽으로 우클릭하여 평평하게 만듭니다.",
    "itemGroup.mcwstairs": "Macaw's Stairs and Balconies",
    "mcwstairs.balcony.desc": (
        "같은 블록에 최대 4번 겹쳐 놓을 수 있습니다. 가위로 모양을 바꿀 수 있습니다."
    ),
    "mcwstairs.railing.desc": ("계단 옆면에 놓습니다. 가위로 모양을 바꿀 수 있습니다."),
    "mcwstairs.platform.desc": (
        "새 계단으로 모퉁이를 만들 때 쓰는 발판입니다. 위에 발코니를 놓을 수 있습니다."
    ),
    "itemGroup.mcwwindows": "Macaw's Windows",
    "itemGroup.windows2": "Macaw's Windows Additions",
    "subtitle.mcwwindows.bars_close": "철창이 전환됨",
    "subtitle.mcwwindows.bars_open": "철창이 전환됨",
    "subtitle.mcwwindows.blinds_close": "블라인드가 닫힘",
    "subtitle.mcwwindows.blinds_open": "블라인드가 열림",
    "subtitle.mcwwindows.window_close": "창문이 닫힘",
    "subtitle.mcwwindows.window_open": "창문이 열림",
    "mcwwindows.hammer.desc": "창문을 우클릭하여 모양을 바꿉니다.",
    "mcwwindows.key.desc": "창문을 우클릭하여 잠급니다.",
    "mcwwindows.crafting.desc": "제작 재료",
    "itemGroup.mcwroofs": "Macaw's Roofs",
    "mcwroofs.hammer.desc": "지붕 상단을 우클릭하여 상태를 전환합니다.",
    "mcwroofs.roofitem.desc": "제작 재료",
    "itemGroup.mcwtrpdoors": "Macaw's Trapdoors",
    "mcwtrpdoors.crafting.desc": "제작 재료",
}

INTENTIONAL_NO_HANGUL_KEYS = {
    key for key in UI_TRANSLATIONS if key.startswith("itemGroup.")
}

NAME_OVERRIDES = {
    "Window Base": "창문 틀",
    "Window Four Pane Base": "네 칸 창문 틀",
    "Window Half Pane Base": "반쪽 창문 틀",
    "Pair of Pumpkins": "호박 한 쌍",
    "Three Pumpkins": "호박 세 개",
    "Pair of Potions": "물약 한 쌍",
    "Three Potions": "물약 세 개",
    "Pile Of Oak Wood": "참나무 목재 더미",
    "Pile Of Spruce Wood": "가문비나무 목재 더미",
    "Pile Of Birch Wood": "자작나무 목재 더미",
    "Snowman With Pan": "프라이팬을 쓴 눈사람",
    "Snowman With Santa Hat": "산타 모자를 쓴 눈사람",
    "Snowman With Ushanka": "우샨카를 쓴 눈사람",
    "Snowman With Top Hat": "실크해트를 쓴 눈사람",
}

# 긴 구를 먼저 찾은 뒤 남은 단어를 번역해 재료·형태 구분을 모두 보존해요.
NAME_PHRASES = {
    "Mossy Stone Bricks": "이끼 낀 석재 벽돌",
    "Mossy Stone Brick": "이끼 낀 석재 벽돌",
    "Red Nether Bricks": "붉은 네더 벽돌",
    "Red Nether Brick": "붉은 네더 벽돌",
    "End Stone Bricks": "엔드 석재 벽돌",
    "Prismarine Bricks": "프리즈머린 벽돌",
    "Prismarine Brick": "프리즈머린 벽돌",
    "Mossy Cobblestone": "이끼 낀 조약돌",
    "Cobbled Deepslate": "조약돌형 심층암",
    "Red Sandstone": "붉은 사암",
    "Dark Prismarine": "짙은 프리즈머린",
    "Stone Bricks": "석재 벽돌",
    "Stone Brick": "석재 벽돌",
    "Nether Bricks": "네더 벽돌",
    "Mud Brick": "진흙 벽돌",
    "Dark Oak": "짙은 참나무",
    "Pale Oak": "창백한 참나무",
    "Crimson Stem": "진홍빛 자루",
    "Warped Stem": "뒤틀린 자루",
    "Light Blue": "하늘색",
    "Light Gray": "회백색",
    "Dark Blue": "짙은 파란색",
    "Lower Base Roof": "낮은 하부 지붕",
    "Steep Base Roof": "가파른 하부 지붕",
    "Lower Top Roof": "낮은 상부 지붕",
    "Steep Top Roof": "가파른 상부 지붕",
    "Rain Gutter Downspout": "빗물받이 수직관",
    "Base Rain Gutter": "기본 빗물받이",
    "Rain Gutter": "빗물받이",
    "Attic Roof": "다락 지붕",
    "Top Roof": "상부 지붕",
    "Roof Block": "지붕 블록",
    "Roof Slab": "지붕 반 블록",
    "Cheval De Frise": "방책",
    "Running Bond": "통줄눈 쌓기",
    "Crystal Floor": "수정 바닥",
    "Windmill Weave": "바람개비 엮기 무늬",
    "Basket Weave": "바구니 엮기 무늬",
    "One Way Glass": "단방향 유리",
    "One Way Glass Pane": "단방향 유리판",
    "Glass Pane": "유리판",
    "Pane Window": "판유리 창문",
    "Four Pane": "네 칸",
    "Half Pane": "반쪽",
    "Curtain Rod": "커튼 봉",
    "Four Panel": "네 패널",
    "Horse Stable": "마구간",
    "Shoji Whole Door": "통짜 장지문",
    "Shoji Door": "장지문",
    "Fence Gate": "울타리 문",
    "Sliding Glass Door": "유리 미닫이문",
    "Wooden Portcullis": "목재 내리닫이 창살문",
    "Iron Portcullis": "철 내리닫이 창살문",
    "Coffee Table": "커피 테이블",
    "End Table": "협탁",
    "Kitchen Counter": "주방 조리대",
    "Cupboard Counter": "찬장 달린 조리대",
    "Glass Cabinet": "유리 수납장",
    "Lower Cabinet": "하부 수납장",
    "Double Drawer": "이중 서랍",
    "Triple Drawer": "삼중 서랍",
    "Covered Desk": "덮개형 책상",
    "Large Desk": "큰 책상",
    "Tiki Torch": "티키 횃불",
    "Candle Holder": "촛대",
    "Ceiling Fan": "천장 선풍기",
    "Street Lamp Post": "가로등",
    "Sea Lantern": "바다 랜턴",
    "Wall Candle Holder": "벽걸이 촛대",
    "Wall Lantern": "벽걸이 랜턴",
    "Wall Lamp": "벽걸이 램프",
    "Wall Deco": "벽 장식",
    "Christmas Tree Base": "크리스마스 트리 받침대",
    "Christmas Tree Middle": "크리스마스 트리 중앙",
    "Christmas Tree Top": "크리스마스 트리 상단",
    "Christmas Tree": "크리스마스 트리",
    "Grass Topped": "잔디 덮인",
}

WORD_TRANSLATIONS = {
    "Acacia": "아카시아나무",
    "Acorn": "도토리형",
    "Additions": "추가",
    "Andesite": "안산암",
    "Arrow": "화살표형",
    "Asian": "동양식",
    "Attic": "다락",
    "Autumn": "가을",
    "Awakened": "깨어난",
    "Awning": "차양",
    "Azalea": "진달래",
    "Bale": "더미",
    "Balloon": "풍선",
    "Balcony": "발코니",
    "Balustrade": "난간형",
    "Bamboo": "대나무",
    "Bark": "나무껍질 무늬",
    "Barn": "헛간",
    "Barred": "창살",
    "Barrel": "통",
    "Base": "기본",
    "Basket": "바구니",
    "Bastion": "성채형",
    "Bat": "박쥐",
    "Beach": "해변",
    "Bell": "종",
    "Bells": "방울",
    "Big": "큰",
    "Birch": "자작나무",
    "Black": "검은색",
    "Blackstone": "흑암",
    "Blinds": "블라인드",
    "Block": "블록",
    "Blue": "파란색",
    "Bond": "벽돌쌓기",
    "Bookshelf": "책장",
    "Bottom": "하단",
    "Brick": "벽돌",
    "Bricks": "벽돌",
    "Bridge": "다리",
    "Bridges": "다리",
    "Broomstick": "빗자루",
    "Brown": "갈색",
    "Bulk": "통짜",
    "Cabinet": "수납장",
    "Can": "깡통",
    "Candle": "양초",
    "Candy": "사탕",
    "Cane": "지팡이",
    "Carpet": "카펫",
    "Carved": "조각된",
    "Cat": "고양이",
    "Cathedral": "대성당형",
    "Cauldron": "가마솥",
    "Ceiling": "천장",
    "Chain": "사슬",
    "Chaise": "긴 의자",
    "Chandelier": "샹들리에",
    "Chaotic": "혼돈의",
    "Chair": "의자",
    "Cherry": "벚나무",
    "Christmas": "크리스마스",
    "Classic": "클래식",
    "Clover": "클로버",
    "Cobble": "조약돌",
    "Cobbled": "조약돌형",
    "Cobblestone": "조약돌",
    "Cobweb": "거미줄",
    "Coffee": "커피",
    "Colorful": "알록달록한",
    "Compact": "소형",
    "Concrete": "콘크리트",
    "Copper": "구리",
    "Cornered": "모서리형",
    "Cottage": "전원풍",
    "Couch": "소파",
    "Counter": "조리대",
    "Couple": "한 쌍의",
    "Covered": "덮개형",
    "Crafting": "제작",
    "Crimson": "진홍빛",
    "Cross": "십자형",
    "Crystal": "수정",
    "Cube": "큐브",
    "Cupboard": "찬장",
    "Curtain": "커튼",
    "Curved": "곡선형",
    "Cyan": "청록색",
    "Dark": "짙은",
    "De": "드",
    "Deco": "장식",
    "Decorated": "장식된",
    "Deepslate": "심층암",
    "Diamond": "마름모형",
    "Diorite": "섬록암",
    "Dirt": "흙",
    "Disc": "음반",
    "Door": "문",
    "Doormat": "현관 매트",
    "Double": "이중",
    "Downspout": "수직관",
    "Drawer": "서랍",
    "Desk": "책상",
    "Dry": "마른",
    "Dumble": "덤블",
    "Ear": "귀",
    "End": "엔드",
    "Evil": "사악한",
    "Expanded": "확장형",
    "Fairy": "요정",
    "Fan": "선풍기",
    "Fence": "울타리",
    "Fences": "울타리",
    "Fern": "고사리",
    "Festive": "축제용",
    "Flagstone": "판석",
    "Flat": "평평한",
    "Flowering": "꽃 핀",
    "Floor": "바닥",
    "Fortress": "요새형",
    "Four": "네",
    "Framed": "프레임형",
    "Friendly": "친근한",
    "Frise": "프리즈",
    "Furniture": "가구",
    "Garage": "차고",
    "Garden": "정원",
    "Garland": "화환",
    "Gate": "울타리 문",
    "Ghost": "유령",
    "Glass": "유리",
    "Glassed": "유리 달린",
    "Glowstone": "발광석",
    "Golden": "금",
    "Gothic": "고딕풍",
    "Granite": "화강암",
    "Grass": "잔디",
    "Gravestone": "묘비",
    "Gravel": "자갈",
    "Gray": "회색",
    "Green": "초록색",
    "Grinch": "그린치",
    "Ground": "바닥",
    "Guardian": "수호자형",
    "Gutter": "빗물받이",
    "Half": "반쪽",
    "Hanging": "매달린",
    "Happy": "행복한",
    "Hammer": "망치",
    "Hat": "모자",
    "Haunting": "으스스한",
    "Hay": "건초",
    "Hedge": "생울타리",
    "Highley": "반원형",
    "Holder": "받침대",
    "Honeycomb": "벌집",
    "Horizontal": "가로형",
    "Horse": "목장형",
    "Hospital": "병원",
    "Icicle": "고드름",
    "Ingredient": "재료",
    "Inventory": "보관함",
    "Iron": "철",
    "Jail": "감옥",
    "Jungle": "정글나무",
    "Key": "열쇠",
    "Kitchen": "주방",
    "Lamp": "램프",
    "Lamps": "램프",
    "Lantern": "랜턴",
    "Large": "큰",
    "Lava": "용암",
    "Laying": "누운",
    "Leaves": "나뭇잎",
    "Light": "조명",
    "Lights": "조명",
    "Lime": "연두색",
    "Lit": "불 켜진",
    "Loft": "로프트",
    "Louvered": "루버형",
    "Low": "낮은",
    "Lower": "하부",
    "Magenta": "자홍색",
    "Majestic": "웅장한",
    "Mangrove": "맹그로브나무",
    "Medium": "중간 크기",
    "Mesh": "격자",
    "Metal": "금속",
    "Middle": "가운데",
    "Mistletoe": "겨우살이",
    "Mixed": "혼합",
    "Modern": "현대식",
    "Mosaic": "모자이크",
    "Mossy": "이끼 낀",
    "Mud": "진흙",
    "Muffs": "귀마개",
    "Mystic": "신비로운",
    "Nether": "네더",
    "Oak": "참나무",
    "of": "",
    "Of": "",
    "One": "하나",
    "Open": "열린",
    "Orange": "주황색",
    "Orn": "장식된",
    "Ornament": "장식 방울",
    "Ornate": "화려한",
    "Outlined": "테두리형",
    "Pair": "한 쌍의",
    "Pan": "팬",
    "Pane": "유리판",
    "Panel": "패널",
    "Panelled": "패널형",
    "Paper": "종이",
    "Parapet": "난간벽",
    "Path": "길",
    "Paving": "포장재",
    "Pavings": "포장재",
    "Picket": "말뚝형",
    "Pier": "교각",
    "Pile": "더미",
    "Pillar": "기둥",
    "Pine": "소나무",
    "Pink": "분홍색",
    "Pliers": "펜치",
    "Planks": "판자",
    "Platform": "플랫폼",
    "Podzol": "회백토",
    "Portcullis": "내리닫이 창살문",
    "Post": "기둥",
    "Potion": "물약",
    "Potions": "물약",
    "Present": "선물",
    "Presents": "선물",
    "Print": "양식",
    "Prismarine": "프리즈머린",
    "Pumpkin": "호박",
    "Pumpkins": "호박",
    "Purple": "보라색",
    "Pyramid": "피라미드형",
    "Quartz": "석영",
    "Rail": "난간",
    "Railing": "난간",
    "Rake": "갈퀴",
    "Ranch": "목장풍",
    "Rectangle": "직사각형",
    "Red": "빨간색",
    "Redstone": "레드스톤",
    "Reindeer": "순록",
    "Reinforced": "강화",
    "Remote": "리모컨",
    "Resizeable": "크기 조절형",
    "Right": "오른쪽",
    "Rocky": "바위무늬",
    "Rod": "봉",
    "Roof": "지붕",
    "Roofing": "지붕용",
    "Rope": "밧줄",
    "Round": "원형",
    "Running": "통줄눈",
    "Rustic": "소박한",
    "Sand": "모래",
    "Sandstone": "사암",
    "Santa": "산타",
    "Scarecrow": "허수아비",
    "Screaming": "비명 지르는",
    "Sharp": "날카로운",
    "Shears": "가위",
    "Shoji": "장지",
    "Shocked": "놀란",
    "Shovel": "삽",
    "Shroomlight": "버섯불",
    "Shutter": "덧문",
    "Silver": "은색",
    "Single": "단일",
    "Sink": "싱크대",
    "Sitting": "앉은",
    "Skeleton": "스켈레톤",
    "Skyline": "스카이라인형",
    "Slab": "반 블록",
    "Slanted": "기울어진",
    "Sled": "썰매",
    "Sleeping": "잠든",
    "Slit": "틈새형",
    "Sliding": "미닫이",
    "Slim": "가느다란",
    "Small": "작은",
    "Smiling": "미소 짓는",
    "Snow": "눈",
    "Snowman": "눈사람",
    "Snowy": "눈 덮인",
    "Sock": "양말",
    "Soul": "영혼",
    "Spider": "거미",
    "Spooky": "오싹한",
    "Spruce": "가문비나무",
    "Square": "사각형",
    "Stable": "마구간",
    "Stair": "계단",
    "Stairs": "계단",
    "Standing": "서 있는",
    "Star": "별",
    "Stars": "별무늬",
    "Stem": "줄기",
    "Steep": "가파른",
    "Stockade": "방책형",
    "Stocking": "긴 양말",
    "Stockings": "긴 양말",
    "Stone": "돌",
    "Store": "상점",
    "Straight": "곧은",
    "Strewn": "흩뿌린",
    "String": "줄",
    "Striped": "줄무늬",
    "Stripped": "껍질 벗긴",
    "Stool": "스툴",
    "Support": "지지대",
    "Swamp": "늪",
    "Switch": "스위치",
    "Table": "테이블",
    "Tall": "높은",
    "Tavern": "선술집",
    "Terrace": "테라스",
    "Terracotta": "테라코타",
    "Thatch": "초가",
    "Thick": "두꺼운",
    "Thin": "얇은",
    "Three": "세 개의",
    "Tiki": "티키",
    "Tile": "타일",
    "Tiles": "타일",
    "Tiny": "아주 작은",
    "Top": "상단",
    "Topped": "상단형",
    "Torch": "횃불",
    "Tower": "탑",
    "Trapdoor": "다락문",
    "Trapdoors": "다락문",
    "Tree": "트리",
    "Triangle": "삼각형",
    "Triple": "삼중",
    "Tropical": "열대풍",
    "Twilight": "황혼형",
    "Unmeltable": "녹지 않는",
    "Upgraded": "업그레이드된",
    "Ushanka": "우샨카",
    "Vertical": "세로형",
    "Vintage": "빈티지",
    "Waffle": "와플형",
    "Wall": "담장",
    "Walls": "담장",
    "Wardrobe": "옷장",
    "Warped": "뒤틀린",
    "Warning": "경고",
    "Wavy": "물결무늬",
    "Way": "방향",
    "Weave": "엮기 무늬",
    "Western": "서부풍",
    "Wheelbarrow": "외바퀴 손수레",
    "Whispering": "속삭이는",
    "White": "하얀색",
    "Window": "창문",
    "Windowed": "창문 달린",
    "Windmill": "바람개비",
    "Wired": "철조망형",
    "Witch": "마녀",
    "With": "달린",
    "Wood": "목재",
    "Wooden": "목재",
    "Whole": "통짜",
    "Wreath": "리스",
    "Yellow": "노란색",
}

QUEST_TRANSLATIONS: dict[str, quest_snbt.TranslationValue] = {
    "quest.1FD60B7448CED1EB.quest_desc": [
        "이 &b&lMacaw's Fences and Walls&r 모드는 새로운 울타리, 울타리 문과 "
        "담장을 추가합니다. \\n\\n철조망에 닿으면 피해를 받습니다. \\n\\n어느 것이든 "
        "평범하게 점프해서 넘을 수는 없습니다."
    ],
    "quest.1FD60B7448CED1EB.title": "&b&lMacaw's Fences and Walls",
    "task.78ECC6C98CA985D7.title": "Macaw's Fences and Walls",
    "quest.04F5846E2468E807.quest_desc": [
        "&b&lMacaw's Doors&r는 여러 종류와 모양의 문을 추가합니다. \\n자작나무 "
        "무늬를 가문비나무 재질로 만들고 싶나요? 그렇게 만들 수 있습니다! "
        "\\n\\n심지어 병원 문도 있습니다!"
    ],
    "quest.04F5846E2468E807.title": "&b&lMacaw's Doors",
    "task.0896EE64F92CCD86.title": "Macaw's Doors",
    "quest.55160BAFFD9E2988.quest_desc": [
        "대표적인 &9Macaw&r 모드인 &9&lMacaw's Furniture&r입니다! \\n\\n의자, "
        "테이블, 책장과 서랍까지 필요한 가구를 두루 추가합니다!"
    ],
    "quest.55160BAFFD9E2988.title": "&l&9Macaw's Furniture&r",
    "task.30933620783092A5.title": "Macaw's Furniture",
    "quest.027E6E294D9E1375.quest_desc": [
        "&lCorail&r님, 잘 보세요! 명절 장식은 이렇게 만드는 겁니다! (100% 애정을 "
        "담아 하는 말이에요. 사랑해요, &lCorail&r!) \\n\\n이 모드는 크리스마스와 "
        "할로윈 장식을 다양하게 추가합니다. \\n\\n크리스마스트리, 선물과 조명부터 "
        "할로윈 호박, 거미와 마녀 모자까지 있습니다."
    ],
    "quest.027E6E294D9E1375.title": "&b&lMacaw's Holidays&r",
    "task.2F94B8FED9BF6698.title": "Macaw's Holidays",
    "quest.3889D0255074CE85.quest_desc": [
        "&bMacaw&r는 가구만으로는 부족하다고 생각했습니다. &b&lMacaw's "
        "Windows&r로 들어오는 자연광 말고도 집에 더 많은 조명이 필요했죠. "
        "\\n\\n그래서 여러 광원을 추가하는 &b&lMacaw's Lights and Lamps&r가 "
        "나왔습니다. \\n\\n램프부터 랜턴, 샹들리에까지 있습니다!"
    ],
    "quest.3889D0255074CE85.title": "&l&bMacaw's Lights and Lamps&r",
    "task.1BA8C5F08A824C08.title": "Macaw's Lights and Lamps",
    "quest.616ED6C49C37EB91.quest_desc": [
        "&b&lPaths and Pathways&r는 카펫처럼 얇은 블록을 다양하게 추가하며, "
        "각각 온전한 블록과 반 블록 형태도 제공합니다. \\n\\n당연히 길을 꾸미는 데 "
        "쓰며, &2&lMinecraft&r의 흙 길 블록보다 훨씬 보기 좋습니다."
    ],
    "quest.616ED6C49C37EB91.title": "&b&lMacaw's Paths and Pavings",
    "task.436475D6C527A458.title": "Macaw's Paths and Pavings",
    "quest.08C66BCA3AAE765B.quest_desc": [
        "이 모드는 &2&lMinecraft&r에 없는 블록을 추가하니 자세한 설명은 "
        "생략하겠습니다."
    ],
    "quest.08C66BCA3AAE765B.title": "&b&lMacaw's Roofs",
    "task.00A904FBEDE80712.title": "Macaw's Roofs",
    "quest.3D1D5CB45D81A6E4.quest_desc": [
        "&b&lMacaw's Doors&r처럼 이 모드도 여러 종류와 모양의 다락문을 추가합니다. "
        "\\n\\n정글나무 다락문에 가문비나무 무늬를 쓰고 싶나요? 이제 그렇게 만들 "
        "수 있습니다!"
    ],
    "quest.3D1D5CB45D81A6E4.title": "&b&lMacaw's Trapdoors",
    "task.20374000F8ADE952.title": "Macaw's Trapdoors",
    "quest.156605859D553276.quest_desc": [
        "창문, 유리판, 덧문, 커튼, 블라인드, 심지어 난간벽까지 있습니다! "
        "\\n\\n난간벽이 뭔지는 저도 모르겠네요!"
    ],
    "quest.156605859D553276.title": "&l&bMacaw's Windows&r",
    "task.46905D1E23255397.title": "Macaw's Windows",
    "quest.30B3BC91460C9B19.quest_desc": [
        "&bMacaw Sketch&r는 장식 모드로 잘 알려진 인기 모드 개발자입니다. "
        "\\n창문부터 길, 서랍까지 거의 모든 것을 만듭니다. \\n\\n전부 제작할 수 "
        "있을까요?"
    ],
    "quest.30B3BC91460C9B19.title": "&bMacaw's Mods",
    "task.6F475689ED4EDF59.title": "Macaw's Mods 아이템",
    "quest.6AC85C203E7C3482.quest_desc": [
        "&b&lMacaw's Mods&r의 모든 아이템을 하나씩 모았습니다. 보상을 받을 "
        "자격이 충분하군요. \\n\\n그 보상이란 바로 나만의 &b마코앵무새&r입니다!"
    ],
    "quest.6AC85C203E7C3482.title": "&b마코앵무새 획득 완료&r",
    "task.49F387C7EAD579A2.title": "마코앵무새 획득 완료",
}


def find_jar(namespace: str) -> Path:
    """현재 설치본에서 지정한 Macaw's JAR 하나를 찾아요."""
    matches = sorted((resolve_source_root() / "mods").glob(MODS[namespace]))
    if len(matches) != 1:
        raise FileNotFoundError(f"{namespace} JAR이 정확히 한 개가 아니에요: {matches}")
    return matches[0]


def language_path(namespace: str, locale: str) -> str:
    """JAR 내부 언어 파일 경로를 만들어요."""
    return f"assets/{namespace}/lang/{locale}.json"


def read_english(namespace: str) -> dict[str, str]:
    """현재 JAR 영어 원문을 읽어요."""
    with ZipFile(find_jar(namespace)) as archive:
        value = json.loads(archive.read(language_path(namespace, "en_us")))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise TypeError(f"{namespace} 영어 언어 파일 형식이 올바르지 않아요")
    return value


def salvage_string_pairs(raw: str) -> dict[str, str]:
    """문법이 깨진 후보 JSON에서도 문자열 키·값 쌍만 안전하게 회수해요."""
    result = {}
    pattern = re.compile(r'"((?:\\.|[^"\\])*)"\s*:\s*"((?:\\.|[^"\\])*)"')
    for match in pattern.finditer(raw):
        try:
            key = json.loads(f'"{match.group(1)}"')
            value = json.loads(f'"{match.group(2)}"')
        except json.JSONDecodeError:
            continue
        result[key] = value
    return result


def read_candidate(namespace: str) -> tuple[dict[str, str], str]:
    """JAR의 기존 한국어를 낮은 품질의 후보로 읽어요."""
    with ZipFile(find_jar(namespace)) as archive:
        path = language_path(namespace, "ko_kr")
        if path not in archive.namelist():
            return {}, "absent"
        raw = archive.read(path).decode("utf-8-sig")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return salvage_string_pairs(raw), "invalid_json_salvaged"
    if not isinstance(value, dict):
        raise TypeError(f"{namespace} 한국어 후보가 JSON 객체가 아니에요")
    return {
        key: item
        for key, item in value.items()
        if isinstance(key, str) and isinstance(item, str)
    }, "valid_json"


def collect_surface(namespace: str) -> dict[str, object]:
    """JAR의 언어·데이터·NBT·가이드 표시 표면을 전수 확인해요."""
    jar = find_jar(namespace)
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
        "namespace": namespace,
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_mtime_ns": jar.stat().st_mtime_ns,
        "jar_sha256": hashlib.sha256(jar.read_bytes()).hexdigest(),
        "language_files": language_files,
        "data_json_files": len(data_files),
        "data_direct_fields": direct_fields,
        "data_localized_fields": localized_fields,
        "invalid_json": invalid_json,
        "nbt_files": len(nbt_files),
        "nbt_visible_fields": nbt_rows,
        "guide_candidates": guide_candidates,
    }


def audit_references() -> tuple[dict[str, object], list[str]]:
    """FTB Quests와 KubeJS의 정확한 네임스페이스 참조를 확인해요."""
    instance = resolve_source_root()
    namespaces = "|".join(re.escape(value) for value in MODS)
    pattern = re.compile(
        rf"(?<![a-z0-9_])(?:{namespaces}):[a-z0-9_./-]+", re.IGNORECASE
    )
    report: dict[str, object] = {"ftbquests": [], "kubejs": [], "read_errors": []}
    errors = []
    for label, base in (
        ("ftbquests", instance / "config/ftbquests/quests"),
        ("kubejs", instance / "kubejs"),
    ):
        rows = report[label]
        if not isinstance(rows, list) or not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {
                ".cfg",
                ".js",
                ".json",
                ".snbt",
                ".toml",
                ".txt",
            }:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                report["read_errors"].append(f"{path}: {exc}")
                continue
            matches = pattern.findall(text)
            if not matches:
                continue
            rows.append(
                {
                    "path": path.relative_to(instance).as_posix(),
                    "occurrences": len(matches),
                    "unique_identifiers": len(set(matches)),
                    "classification": (
                        "quest_item_and_smart_filter_references"
                        if label == "ftbquests"
                        else "identifier_reference"
                    ),
                }
            )
    errors.extend(str(value) for value in report["read_errors"])
    return report, errors


def prepare() -> dict[str, object]:
    """현재 영어·기존 한국어 후보와 전체 표시 표면을 기록해요."""
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    counts = {}
    candidate_counts = {}
    candidate_status = {}
    for namespace in MODS:
        english = read_english(namespace)
        candidate, status = read_candidate(namespace)
        write_json(WORK_ROOT / f"{namespace}_en_us.json", english)
        write_json(WORK_ROOT / f"{namespace}_candidate_ko_kr.json", candidate)
        rows.append(collect_surface(namespace))
        counts[namespace] = len(english)
        candidate_counts[namespace] = len(set(english) & set(candidate))
        candidate_status[namespace] = status
    references, reference_errors = audit_references()
    quest_english = quest_snbt.parse_language_snbt(
        resolve_source_root() / "config/ftbquests/quests/lang/en_us.snbt"
    )
    quest_korean = quest_snbt.parse_language_snbt(
        resolve_source_root() / "config/ftbquests/quests/lang/ko_kr.snbt"
    )
    related_quest_candidate = {
        key: quest_korean[key] for key in QUEST_TRANSLATIONS if key in quest_korean
    }
    write_json(WORK_ROOT / "ftb_candidate_ko.json", related_quest_candidate)
    catalog = {
        "family": FAMILY,
        "jars": rows,
        "language_keys": counts,
        "bundled_korean_candidate_keys": candidate_counts,
        "candidate_status": candidate_status,
        "ftbquests": {
            "english_path": "config/ftbquests/quests/lang/en_us.snbt",
            "english_size": (
                resolve_source_root() / "config/ftbquests/quests/lang/en_us.snbt"
            )
            .stat()
            .st_size,
            "related_keys": len(QUEST_TRANSLATIONS),
            "missing_english_keys": sorted(
                set(QUEST_TRANSLATIONS) - set(quest_english)
            ),
        },
        "references": references,
        "reference_errors": reference_errors,
        "status": (
            "prepared"
            if not reference_errors
            and not (set(QUEST_TRANSLATIONS) - set(quest_english))
            else "incomplete"
        ),
    }
    write_json(WORK_ROOT / "source_surface_catalog.json", catalog)
    return catalog


def translate_name(source: str) -> str:
    """검수된 긴 구와 단어표로 한 아이템·블록 이름을 번역해요."""
    if source in NAME_OVERRIDES:
        return NAME_OVERRIDES[source]
    bridge_match = re.fullmatch(r"Rope (.+) Bridge( Stair)?", source)
    if bridge_match:
        suffix = " 밧줄 다리 계단" if bridge_match.group(2) else " 밧줄 다리"
        return f"{translate_name(bridge_match.group(1))}{suffix}"
    balustrade_match = re.fullmatch(r"Balustrade (.+) Bridge", source)
    if balustrade_match:
        return f"{translate_name(balustrade_match.group(1))} 난간형 다리"
    light_garland_match = re.fullmatch(
        r"(?:(White) )?(?:(Wavy) )?Garland "
        r"(Colorful|Blue|Green|Red|Orange|Yellow|Purple) Lights",
        source,
    )
    if light_garland_match:
        light_color = translate_name(light_garland_match.group(3))
        white = "하얀색 " if light_garland_match.group(1) else ""
        wavy = "물결무늬 " if light_garland_match.group(2) else ""
        return f"{light_color} 조명이 달린 {white}{wavy}화환"
    ornament_garland_match = re.fullmatch(
        r"(?:(White) )?Orn (Golden|Silver|Red|Blue) (?:(Wavy) )?Garland",
        source,
    )
    if ornament_garland_match:
        ornament_color = translate_name(ornament_garland_match.group(2))
        white = "하얀색 " if ornament_garland_match.group(1) else ""
        wavy = "물결무늬 " if ornament_garland_match.group(3) else ""
        return f"{ornament_color} 장식이 달린 {white}{wavy}화환"
    tokens = NAME_TOKEN.findall(source)
    result = []
    index = 0
    while index < len(tokens):
        matched = False
        for width in range(min(4, len(tokens) - index), 1, -1):
            phrase = " ".join(tokens[index : index + width])
            if phrase in NAME_PHRASES:
                result.append(NAME_PHRASES[phrase])
                index += width
                matched = True
                break
        if matched:
            continue
        token = tokens[index]
        if token.isdigit():
            result.append(token)
        elif token in WORD_TRANSLATIONS:
            if WORD_TRANSLATIONS[token]:
                result.append(WORD_TRANSLATIONS[token])
        else:
            raise KeyError(token)
        index += 1
    return " ".join(result)


def build() -> dict[str, object]:
    """11개 JAR의 영어 키 전체와 관련 FTB Quests를 번역해요."""
    missing_words = defaultdict(set)
    outputs = {}
    methods = Counter()
    reused = 0
    revised = 0
    new = 0
    for namespace in MODS:
        english = read_english(namespace)
        candidate, _ = read_candidate(namespace)
        translated = {}
        for key, source in english.items():
            if key in UI_TRANSLATIONS:
                translated[key] = UI_TRANSLATIONS[key]
                methods["reviewed_ui"] += 1
                continue
            if not key.startswith(("block.", "item.")):
                missing_words[key].add(source)
                continue
            try:
                translated[key] = translate_name(source)
            except KeyError as exc:
                missing_words[str(exc)].add(source)
                continue
            methods["reviewed_name_grammar"] += 1
        if missing_words:
            continue
        write_json(WORK_ROOT / f"{namespace}_ko_kr.json", translated)
        write_json(OUTPUTS[namespace], translated)
        outputs[namespace] = len(translated)
        reused += sum(candidate.get(key) == value for key, value in translated.items())
        revised += sum(
            key in candidate and candidate[key] != value
            for key, value in translated.items()
        )
        new += sum(key not in candidate for key in translated)
    if missing_words:
        details = {key: sorted(values) for key, values in sorted(missing_words.items())}
        raise KeyError(f"번역하지 못한 이름 단어 또는 키가 있어요: {details}")
    quest_english = quest_snbt.parse_language_snbt(
        resolve_source_root() / "config/ftbquests/quests/lang/en_us.snbt"
    )
    quest_errors = []
    for key, target in QUEST_TRANSLATIONS.items():
        if key not in quest_english:
            quest_errors.append(f"영어 원문에 없는 FTB Quests 키예요: {key}")
            continue
        quest_errors.extend(quest_snbt.validate_value(key, quest_english[key], target))
    if quest_errors:
        raise ValueError("\n".join(quest_errors))
    merged = quest_snbt.merge_into_full_snbt(QUEST_OUTPUT, QUEST_TRANSLATIONS)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    reparsed = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    for key, target in QUEST_TRANSLATIONS.items():
        if reparsed.get(key) != target:
            raise ValueError(f"FTB Quests 병합 결과가 달라요: {key}")
    candidate_quests = load_json(WORK_ROOT / "ftb_candidate_ko.json")
    quest_reused = sum(
        candidate_quests.get(key) == value for key, value in QUEST_TRANSLATIONS.items()
    )
    quest_revised = sum(
        key in candidate_quests and candidate_quests[key] != value
        for key, value in QUEST_TRANSLATIONS.items()
    )
    quest_new = sum(key not in candidate_quests for key in QUEST_TRANSLATIONS)
    write_json(WORK_ROOT / "ftb_ko.json", QUEST_TRANSLATIONS)
    report = {
        "family": FAMILY,
        "reviewed_language_keys": sum(outputs.values()),
        "output_keys": outputs,
        "bundled_candidate_values_reused": reused,
        "bundled_candidate_values_revised": revised,
        "new_language_values": new,
        "translation_methods": dict(sorted(methods.items())),
        "ftbquests": {
            "reviewed_keys": len(QUEST_TRANSLATIONS),
            "existing_values_reused": quest_reused,
            "existing_values_revised": quest_revised,
            "new_values": quest_new,
        },
        "errors": [],
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def preserved_errors(key: str, source: str, target: str) -> list[str]:
    """자리표시자·서식·숫자·줄바꿈이 보존됐는지 확인해요."""
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


def source_is_current(catalog: dict[str, object]) -> list[str]:
    """원문 준비 이후 JAR이 바뀌지 않았는지 확인해요."""
    errors = []
    for row in catalog["jars"]:
        jar = find_jar(row["namespace"])
        if (
            row["jar"] != jar.name
            or row["jar_size"] != jar.stat().st_size
            or row["jar_mtime_ns"] != jar.stat().st_mtime_ns
            or row["jar_sha256"] != hashlib.sha256(jar.read_bytes()).hexdigest()
        ):
            errors.append(f"{row['namespace']} JAR이 원문 추출 당시와 달라요")
    return errors


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR 데이터와 관련 FTB Quests·KubeJS 표시 경로를 감사해요."""
    catalog = load_json(WORK_ROOT / "source_surface_catalog.json")
    errors = source_is_current(catalog)
    surfaces = {}
    for row in catalog["jars"]:
        namespace = row["namespace"]
        if row["invalid_json"]:
            errors.append(f"{namespace}에 읽지 못한 데이터 JSON이 있어요")
        if row["guide_candidates"]:
            errors.append(f"{namespace}에 별도 가이드 후보가 있어요")
        if row["data_direct_fields"]:
            errors.append(f"{namespace} 데이터에 직접 표시 문구가 있어요")
        if row["nbt_visible_fields"]:
            errors.append(f"{namespace} NBT에 직접 표시 문구가 있어요")
        surfaces[namespace] = {
            "data_json_files": row["data_json_files"],
            "data_localized_fields": len(row["data_localized_fields"]),
            "data_direct_fields": len(row["data_direct_fields"]),
            "nbt_files": row["nbt_files"],
            "nbt_visible_fields": len(row["nbt_visible_fields"]),
            "guide_candidates": len(row["guide_candidates"]),
        }
    references, reference_errors = audit_references()
    errors.extend(reference_errors)
    english_quests = quest_snbt.parse_language_snbt(
        resolve_source_root() / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean_quests = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    for key, target in QUEST_TRANSLATIONS.items():
        if key not in english_quests:
            errors.append(f"FTB Quests 영어 원문에 키가 없어요: {key}")
        if korean_quests.get(key) != target:
            errors.append(f"FTB Quests 산출물이 검수 번역과 달라요: {key}")
    report = {
        "family": FAMILY,
        "jar_surfaces": surfaces,
        "references": references,
        "ftbquests_display_work": "complete",
        "kubejs_display_work": (
            "no_related_references"
            if not references["kubejs"]
            else "identifier_references_only"
        ),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def canonical_source(source: str) -> str:
    """표시상 같은 단복수형만 이름 충돌 검사에서 동등하게 봐요."""
    return re.sub(r"\b(?:Bricks|Bridges|Fences|Walls|Pavings|Trapdoors)\b", "X", source)


def verify_language() -> tuple[dict[str, object], list[str]]:
    """11개 언어 파일의 키·보존 요소·영문 잔여·이름 구분을 검증해요."""
    errors = []
    by_mod = {}
    no_hangul = []
    same = []
    collapsed = {}
    total = 0
    total_reused = 0
    total_revised = 0
    total_new = 0
    for namespace in MODS:
        english = read_english(namespace)
        candidate, candidate_status = read_candidate(namespace)
        work = load_json(WORK_ROOT / f"{namespace}_ko_kr.json")
        output = load_json(OUTPUTS[namespace])
        total += len(english)
        if list(work) != list(english) or list(output) != list(english):
            errors.append(f"{namespace} 한국어 키 또는 순서가 영어 원문과 달라요")
        if work != output:
            errors.append(f"{namespace} 작업본과 산출물이 달라요")
        collisions = defaultdict(lambda: defaultdict(list))
        for key, source in english.items():
            target = output.get(key)
            if not isinstance(target, str):
                errors.append(f"문자열 번역이 없어요: {key}")
                continue
            errors.extend(preserved_errors(key, source, target))
            if source == target:
                same.append(key)
            if not HANGUL.search(target):
                no_hangul.append(key)
            if key.startswith(("block.", "item.")):
                collisions[target][source].append(key)
        invalid = {}
        for target, sources in collisions.items():
            if len({canonical_source(source) for source in sources}) > 1:
                invalid[target] = dict(sources)
        if invalid:
            collapsed[namespace] = invalid
            errors.append(f"{namespace}에서 서로 다른 영어 이름이 합쳐졌어요")
        reused = sum(candidate.get(key) == value for key, value in output.items())
        revised = sum(
            key in candidate and candidate[key] != value
            for key, value in output.items()
        )
        new = sum(key not in candidate for key in output)
        total_reused += reused
        total_revised += revised
        total_new += new
        by_mod[namespace] = {
            "english_keys": len(english),
            "output_keys": len(output),
            "bundled_candidate_keys": len(set(english) & set(candidate)),
            "candidate_status": candidate_status,
            "candidate_values_reused": reused,
            "candidate_values_revised": revised,
            "new_values": new,
            "unexpected_collapsed_name_count": len(invalid),
        }
    if set(no_hangul) != INTENTIONAL_NO_HANGUL_KEYS:
        errors.append(
            "공식 영문 유지 키가 검수 목록과 달라요: "
            f"actual={sorted(no_hangul)}, expected={sorted(INTENTIONAL_NO_HANGUL_KEYS)}"
        )
    if set(same) != INTENTIONAL_NO_HANGUL_KEYS:
        errors.append(f"영어 원문 유지값이 검수 목록과 달라요: {same}")
    report = {
        "reviewed_english_keys": total,
        "mods": by_mod,
        "bundled_candidate_values_reused": total_reused,
        "bundled_candidate_values_revised": total_revised,
        "new_language_values": total_new,
        "intentional_no_hangul_keys": sorted(no_hangul),
        "unexpected_collapsed_names": collapsed,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify_ftbquests() -> tuple[dict[str, object], list[str]]:
    """관련 FTB Quests 33개 키의 전체 재검수 결과를 확인해요."""
    english = quest_snbt.parse_language_snbt(
        resolve_source_root() / "config/ftbquests/quests/lang/en_us.snbt"
    )
    output = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    candidate = load_json(WORK_ROOT / "ftb_candidate_ko.json")
    work = load_json(WORK_ROOT / "ftb_ko.json")
    errors = []
    if work != QUEST_TRANSLATIONS:
        errors.append("FTB Quests 작업 기록이 검수 번역표와 달라요")
    for key, target in QUEST_TRANSLATIONS.items():
        if key not in english:
            errors.append(f"FTB Quests 영어 원문에 키가 없어요: {key}")
            continue
        errors.extend(quest_snbt.validate_value(key, english[key], target))
        if output.get(key) != target:
            errors.append(f"FTB Quests 산출물이 검수 번역과 달라요: {key}")
    reused = sum(
        candidate.get(key) == value for key, value in QUEST_TRANSLATIONS.items()
    )
    revised = sum(
        key in candidate and candidate[key] != value
        for key, value in QUEST_TRANSLATIONS.items()
    )
    new = sum(key not in candidate for key in QUEST_TRANSLATIONS)
    report = {
        "reviewed_keys": len(QUEST_TRANSLATIONS),
        "existing_values_reused": reused,
        "existing_values_revised": revised,
        "new_values": new,
        "remaining": len(errors),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """언어·퀘스트·표시 표면과 적용 기록을 함께 검증해요."""
    catalog = load_json(WORK_ROOT / "source_surface_catalog.json")
    source_errors = source_is_current(catalog)
    language, language_errors = verify_language()
    quests, quest_errors = verify_ftbquests()
    surface, surface_errors = audit()
    errors = source_errors + language_errors + quest_errors + surface_errors
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = load_json(deployment_path) if deployment_path.is_file() else None
    report = {
        "family": FAMILY,
        "language": language,
        "ftbquests": quests,
        "surface_audit": surface["status"],
        "kubejs": surface["kubejs_display_work"],
        "output_files": DEPLOYMENT_PATHS,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    completion = {
        "family": FAMILY,
        "reviewed_language_keys": language["reviewed_english_keys"],
        "bundled_candidate_values_reused": language["bundled_candidate_values_reused"],
        "bundled_candidate_values_revised": language[
            "bundled_candidate_values_revised"
        ],
        "new_language_values": language["new_language_values"],
        "ftbquests_reviewed_keys": quests["reviewed_keys"],
        "ftbquests_existing_values_reused": quests["existing_values_reused"],
        "ftbquests_existing_values_revised": quests["existing_values_revised"],
        "ftbquests_new_values": quests["new_values"],
        "kubejs_work": surface["kubejs_display_work"],
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
    """적용 매니페스트의 백업·해시 검증을 완료 기록에 연결해요."""
    manifest_path = manifest_path.resolve()
    manifest = load_json(manifest_path)
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
            errors.append("적용 후 12개 산출물 중 해시가 다른 파일이 있어요")
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
        relative_manifest = manifest_path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        relative_manifest = str(manifest_path)
    report = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "backup_manifest": relative_manifest,
        "expected_paths": DEPLOYMENT_PATHS,
        "targets": summaries,
        "errors": errors,
    }
    write_json(WORK_ROOT / "deployment_report.json", report)
    verify_report, verify_errors = verify()
    return {
        "deployment": report,
        "verification": verify_report["status"],
        "status": "applied_and_verified"
        if not errors and not verify_errors
        else "incomplete",
    }, errors + verify_errors


def run_all() -> tuple[dict[str, object], list[str]]:
    """준비·생성·감사·검증을 순서대로 실행해요."""
    prepared = prepare()
    built = build()
    audit_report, audit_errors = audit()
    verify_report, verify_errors = verify()
    errors = audit_errors + verify_errors
    return {
        "prepare": prepared["status"],
        "build": built["status"],
        "audit": audit_report["status"],
        "verify": verify_report["status"],
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
