#!/usr/bin/env python3
"""Mama's MerryMaking의 언어와 Patchouli 안내서를 번역하고 검증해요."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

FAMILY = "merrymaking"
MOD_ID = "merrymaking"
JAR_PATTERN = "merrymaking-*.jar"
EXPECTED_KEYS = 472
WORK_ROOT = PROJECT_ROOT / "working/merrymaking"
OUTPUT_ROOT = active_output_root() / "resourcepack/ATM10_Korean/assets/merrymaking"
LANG_OUTPUT = OUTPUT_ROOT / "lang/ko_kr.json"
PATCHOULI_PREFIX = "assets/merrymaking/patchouli_books/merrymanual/en_us/"
PATCHOULI_OUTPUT = OUTPUT_ROOT / "patchouli_books/merrymanual/ko_kr"
VISIBLE_FIELDS = {"name", "description", "text", "title"}
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z]|\{\d+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
PATCHOULI_TOKEN = re.compile(r"\$\([^)]+\)")
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?")
URL = re.compile(r"https?://[^\s\"']+")
VISIBLE_DATA_KEYS = {
    "custom_name",
    "minecraft:custom_name",
    "minecraft:item_name",
    "item_name",
    "title",
    "description",
    "literal_text",
}

MATERIALS = {
    "Acacia": "아카시아나무",
    "Andesite": "안산암",
    "Bamboo": "대나무",
    "Birch": "자작나무",
    "BlackStone": "흑암",
    "Brick": "벽돌",
    "Cherry": "벚나무",
    "Cobbled Deepslate": "심층암 조약돌",
    "Cobblestone": "조약돌",
    "Crimson": "진홍빛",
    "Dark Oak": "짙은 참나무",
    "Deepslate Brick": "심층암 벽돌",
    "Deepslate Tile": "심층암 타일",
    "Diorite": "섬록암",
    "End Stone Brick": "엔드 석재 벽돌",
    "Granite": "화강암",
    "Iron": "철",
    "Jungle": "정글나무",
    "Mangrove": "맹그로브나무",
    "Mossy Cobblestone": "이끼 낀 조약돌",
    "Nether Brick": "네더 벽돌",
    "Oak": "참나무",
    "Pine": "소나무",
    "Polished Blackstone": "윤나는 흑암",
    "Polished Blackstone Brick": "윤나는 흑암 벽돌",
    "Polished Deepslate": "윤나는 심층암",
    "Prismarine": "프리즈머린",
    "Red Nether Brick": "붉은 네더 벽돌",
    "Red Sandstone": "붉은 사암",
    "Sandstone": "사암",
    "Spruce": "가문비나무",
    "Stone Brick": "석재 벽돌",
    "Warped": "뒤틀린",
}

EXACT_NAMES = {
    "Mama's MerryMaking": "Mama's MerryMaking",
    "Christmas Creeper": "크리스마스 크리퍼",
    "Merry-Maker's Manual": "메리메이커 안내서",
    "Smithing Template": "대장장이 형판",
    "Left Vertical Template": "왼쪽 세로 형판",
    "Right Vertical Template": "오른쪽 세로 형판",
    "Left Diagonal Template": "왼쪽 대각선 형판",
    "Right Diagonal Template": "오른쪽 대각선 형판",
    "Left Vertical Corner Template": "왼쪽 세로 모서리 형판",
    "Right Vertical Corner Template": "오른쪽 세로 모서리 형판",
    "Reindeer Antlers": "순록 뿔",
    "Red Santa Hat": "빨간 산타 모자",
    "Ugly Christmas Sweater-Penguin": "펭귄 못난이 크리스마스 스웨터",
    "Ugly Christmas Sweater-Snowman": "눈사람 못난이 크리스마스 스웨터",
    "Plaid Pajama Pants": "체크무늬 파자마 바지",
    "Striped Pajama Pants": "줄무늬 파자마 바지",
    "Santa Slippers": "산타 슬리퍼",
    "Reindeer Slippers": "순록 슬리퍼",
    "Bright Colored Ornaments": "화려한 색상 장식구",
    "Classic Colored Ornaments": "전통 색상 장식구",
    "Dried Sweet Berries": "말린 달콤한 열매",
    "Sweet Berry Garland": "달콤한 열매 가랜드",
    "Christmas Tree": "크리스마스트리",
    "Snowy Christmas Tree": "눈 덮인 크리스마스트리",
    "Christmas Tree Lights White": "흰색 크리스마스트리 조명",
    "Christmas Tree Lights Multi": "다색 크리스마스트리 조명",
    "Roof Tiles": "지붕 타일",
    "Green Wire": "초록색 전선",
    "White Wire": "흰색 전선",
    "Multi Bulbs": "다색 전구",
    "White Bulbs": "흰색 전구",
    "Classic Bulbs White": "흰색 클래식 전구",
    "Classic Bulbs Multi": "다색 클래식 전구",
    "Mini Bulbs Multi": "다색 미니 전구",
    "Mini Bulbs White": "흰색 미니 전구",
    "Icicle Bulbs White": "흰색 고드름 전구",
    "Icicle Bulbs Multi": "다색 고드름 전구",
    "Twinkling Icicle Bulbs Multi": "다색 반짝이는 고드름 전구",
    "Twinkling Icicle Bulbs White": "흰색 반짝이는 고드름 전구",
    "Classic Lights White": "흰색 클래식 조명",
    "Classic Lights Multi": "다색 클래식 조명",
    "Tree Lights White": "흰색 트리 조명",
    "Tree Lights Multi": "다색 트리 조명",
    "Mini Lights Multi": "다색 미니 조명",
    "Mini Lights White": "흰색 미니 조명",
    "Icicle Lights White": "흰색 고드름 조명",
    "Icicle Lights Multi": "다색 고드름 조명",
    "Twinkling Icicle Lights Multi": "다색 반짝이는 고드름 조명",
    "Twinkling Icicle Lights White": "흰색 반짝이는 고드름 조명",
    "Star": "별",
    "Bow": "리본",
    "Christmas Stocking": "크리스마스 양말",
    "Peppermint Extract": "페퍼민트 추출물",
    "Bottle of Mint": "민트 한 병",
    "Raw Ham": "익히지 않은 햄",
    "Cooked Ham": "익힌 햄",
    "Holiday Music": "연말 음악",
    "Holiday Music Mix (Various Artists)": "연말 음악 모음(여러 음악가)",
    "Lofi Holiday Music": "로파이 연말 음악",
    "Assortment of Holiday Songs by LofiGeek": "LofiGeek의 연말 음악 모음",
    "Ground Ginger": "간 생강",
    "Gingerbread Dough": "진저브레드 반죽",
    "Cookie Dough": "쿠키 반죽",
    "Gingerbread Cookie": "진저브레드 쿠키",
    "Christmas Tree Cookie": "크리스마스트리 쿠키",
    "Christmas Stocking Cookie": "크리스마스 양말 쿠키",
    "Christmas Mitten Cookie": "크리스마스 벙어리장갑 쿠키",
    "Fudge": "퍼지",
    "Egg Nog": "에그노그",
    "Mug of unheated Cocoa": "데우지 않은 코코아 한 잔",
    "Hold §bSHIFT§b for more Information!": "자세한 정보를 보려면 §bSHIFT§b 키를 누르세요!",
    "§ A cold mug of cocoa...do you really want to drink this? §": (
        "§ 차가운 코코아 한 잔... 정말 마시고 싶나요? §"
    ),
    "Hot Cocoa": "핫 코코아",
    "Peppermint Hot Cocoa": "페퍼민트 핫 코코아",
    "Candy Cane": "막대사탕",
    "Icing": "아이싱",
    "Fruitcake": "과일 케이크",
    "Corn": "옥수수",
    "Sweet Potato Pie": "고구마 파이",
    "Latke": "라트케",
    "Rugelach": "루겔라흐",
    "Quartz Platter": "석영 플래터",
    "Wood Tray": "나무 쟁반",
    "Stuffed Poultry Dinner": "속을 채운 가금류 만찬",
    "Holiday Ham Dinner": "연말 햄 만찬",
    "Mug": "머그잔",
    "Mug of Hot Cocoa": "핫 코코아 머그잔",
    "Mug of Peppermint Hot Cocoa": "페퍼민트 핫 코코아 머그잔",
    "Mug of Eggnog": "에그노그 머그잔",
    "Mkeka": "음케카",
    "Chalice": "성배",
    "Kinara": "키나라",
    "Menorah": "메노라",
    "Harvest Tray": "수확물 쟁반",
    "Cookie Tray": "쿠키 쟁반",
    "Dreidels": "드레이들",
    "Gelt": "겔트",
    "Small Spruce Sapling": "작은 가문비나무 묘목",
    "Holly Tree Sapling": "호랑가시나무 묘목",
    "Christmas Present": "크리스마스 선물",
    "Tree Stand": "트리 받침대",
    "Wreath": "리스",
    "Wreath (White Lights)": "리스(흰색 조명)",
    "Wreath (Multi Lights)": "리스(다색 조명)",
    "Bow Tree Topper": "리본 트리 꼭대기 장식",
    "Star Tree Topper": "별 트리 꼭대기 장식",
    "Fireplace Logs": "벽난로 장작",
    "Fireplace Logs Burning": "타는 벽난로 장작",
    "Fireplace Logs Burned": "다 탄 벽난로 장작",
    "Lamp Post": "가로등",
    "Candle Holders Mantel Decoration": "촛대 벽난로 선반 장식",
    "Gingerbread House Mantel Decoration": "진저브레드 집 벽난로 선반 장식",
    "Lantern and Poinsetta Mantel Decoration": "랜턴과 포인세티아 벽난로 선반 장식",
    "Joy Mantel Decoration": "기쁨 벽난로 선반 장식",
    "Christmas Tree Mantel Decoration": "크리스마스트리 벽난로 선반 장식",
    "Lantern and Ornament Mantel Decoration": "랜턴과 장식구 벽난로 선반 장식",
    "Cherry Wreath Fence with Garland": "가랜드를 두른 벚나무 울타리",
    "Bamboo Wreath Fence with Garland": "가랜드를 두른 대나무 울타리",
    "End Stone BrickWall with Lit Garland (Multi Lights)": (
        "다색 조명 가랜드를 두른 엔드 석재 벽돌 담장"
    ),
    "Mini Lights Multi Cap": "다색 미니 조명 (지붕 꼭대기)",
    "Spruce Leaves (White Lights)": "가문비나무 잎(흰색 조명)",
    "Spruce Leaves (Multicolored Lights)": "가문비나무 잎(다색 조명)",
    "Spruce Leaves (Classic White Lights)": "가문비나무 잎(흰색 클래식 조명)",
    "Spruce Leaves (Classic Multicolored Lights)": ("가문비나무 잎(다색 클래식 조명)"),
    "Spruce Leaves (Holly Berries)": "가문비나무 잎(호랑가시나무 열매)",
}

PATCHOULI_TEXT = {
    "Ugly Sweater Armor": "못난이 스웨터 방어구",
    "Mix and match for the ultimate cringe factor.": (
        "마음대로 조합해 최고의 민망함을 연출해 보세요."
    ),
    "Book Recipe": "안내서 제작법",
    "How to craft the Merry-Maker's Manual": "메리메이커 안내서 제작 방법",
    "Decorated Doors": "장식한 문",
    "Greet your guests with a festive wreath on your door.": (
        "문에 축제 리스를 달아 손님을 맞이하세요."
    ),
    "Picket Fences and Gates": "울타리와 울타리 문",
    "Beautify your boundaries with picket fences and their decorations.": (
        "울타리와 장식으로 경계를 아름답게 꾸며 보세요."
    ),
    "Holiday Foods": "연말 음식",
    "Delicous Foods and Drinks for your Holiday Celebrations.": (
        "연말 축하 행사에 어울리는 맛있는 음식과 음료예요."
    ),
    "Garlands": "가랜드",
    "Garlands add greenery and a lovely aesthetic to your build.": (
        "가랜드로 건축물에 푸른 장식과 사랑스러운 분위기를 더할 수 있어요."
    ),
    "Hanukkah": "하누카",
    "Celebrate Hanukkah in Minecraft with special blocks and items.": (
        "특별한 블록과 아이템으로 Minecraft에서 하누카를 기념하세요."
    ),
    "Kwanzaa": "콴자",
    "Celebrate Kwanzaa in Minecraft with special blocks and items.": (
        "특별한 블록과 아이템으로 Minecraft에서 콴자를 기념하세요."
    ),
    "What better way to light your path than an old-fashioned lamp post?": (
        "고풍스러운 가로등만큼 길을 멋지게 밝히는 방법이 또 있을까요?"
    ),
    "Lights": "조명",
    "There are several types of colored lights to illuminate your world with.": (
        "세계를 밝힐 여러 종류의 색색 조명이 있어요."
    ),
    "Fireplaces": "벽난로",
    "Special Mantels and Fireplace logs create cozy, beautiful fireplaces.": (
        "특별한 벽난로 선반과 장작으로 아늑하고 아름다운 벽난로를 만들 수 있어요."
    ),
    "Misc": "기타",
    "Miscellaneous": "기타 장식",
    "Festive Monsters": "축제 괴물",
    "The Monsters have decided to join in with the Holiday festivities!": (
        "괴물들도 연말 축제에 함께하기로 했나 봐요!"
    ),
    "Holiday Music Discs": "연말 음악 음반",
    "Pleasant tunes to get you in the Holiday Spirit.": (
        "연말 분위기를 살려 주는 즐거운 음악이에요."
    ),
    "Other Blocks": "기타 블록",
    "Other Decorative Blocks": "기타 장식 블록",
    "Present": "선물",
    "It's not the Holidays without some gift-giving! Surprise, impress, and disappoint your friends or loved ones with a Present!": (
        "선물 없는 연말은 상상할 수 없죠! 친구나 사랑하는 사람에게 선물을 주어 놀라게 "
        "하거나 감동시키거나 실망시켜 보세요!"
    ),
    "Roof Stairs and Slabs": "지붕 계단과 반 블록",
    "Have you ever wished for a way to make a snowy rooftop? If you have, your wish has been granted.": (
        "눈 덮인 지붕을 만들고 싶었던 적이 있나요? 이제 그 소원을 이룰 수 있어요."
    ),
    "Christmas Trees": "크리스마스트리",
    "Chop down a tree and decorate it for the Holidays!": (
        "나무를 베어 연말 장식으로 꾸며 보세요!"
    ),
    "Wreaths": "리스",
    'Nothing says "Home for the Holidays" like a pretty wreath.': (
        "예쁜 리스만큼 포근한 연말의 집을 잘 보여 주는 장식도 없어요."
    ),
    "A set of Ugly Christmas Armor": "못난이 크리스마스 방어구 세트",
    "Smithing Templates": "대장장이 형판",
    "Template Duplication": "형판 복제",
    "Helmets": "투구",
    "Chestplates": "흉갑",
    "Leggings": "각반",
    "Boots": "장화",
    "Tier 2 Upgrade Examples": "2단계 업그레이드 예시",
    "Tier 3 Upgrade Examples": "3단계 업그레이드 예시",
    "Smithing recipes for Tier 2 use the Iron Upgrade Smithing Template.": (
        "2단계 대장장이 레시피에는 철 업그레이드 대장장이 형판을 사용해요."
    ),
    "Smithing recipes for Tier 3 use the Diamond Upgrade Smithing Template.": (
        "3단계 대장장이 레시피에는 다이아몬드 업그레이드 대장장이 형판을 사용해요."
    ),
    "Book Crafting Recipe": "안내서 제작법",
    "The Chalice can be placed down by itself, or placed on an Mkeka.": (
        "성배는 단독으로 설치하거나 음케카 위에 놓을 수 있어요."
    ),
    "In the spirit of the Holidays, this little fellow has a special surprise for players--if they will let him get close enough, that is.": (
        "연말 분위기에 맞춰 이 작은 친구가 플레이어를 위한 특별한 선물을 준비했어요. "
        "충분히 가까이 다가오게 둔다면 말이죠."
    ),
    "Just...don't make him angry. You won't like him when he's angry.": (
        "그저... 화나게 하지는 마세요. 화난 모습은 마음에 들지 않을 테니까요."
    ),
    "Decorated Spruce Door!": "장식한 가문비나무 문!",
    "Doors with Wreaths": "리스가 달린 문",
    "Door with Wreaths": "리스가 달린 문",
    "Hanukkah Decorations": "하누카 장식",
    "Decorated Oak Picket Fence!": "장식한 참나무 울타리!",
    "Picket Fences": "울타리",
    "Decorated Picket Fences": "장식한 울타리",
    "Sweets, Treats, and Sips": "달콤한 간식과 음료",
    "Placeable Drinks": "설치할 수 있는 음료",
    "Drinks": "음료",
    "Heat a Mug of Cocoa to make Hot Cocoa.": (
        "코코아 머그잔을 데우면 핫 코코아가 돼요."
    ),
    "Ingredient Recipes": "재료 레시피",
    "To make Peppermint Extract, use a Bottle of Mint on Water.": (
        "페퍼민트 추출물을 만들려면 물에 민트 한 병을 사용하세요."
    ),
    "Cookie Recipes": "쿠키 레시피",
    "Other Desserts": "기타 디저트",
    "Cooked Ham": "익힌 햄",
    "Dinners": "만찬",
    "Food Trays": "음식 쟁반",
    "Horizontal Garlands": "가로 가랜드",
    "Diagonal Garlands": "대각선 가랜드",
    "Vertical Garlands": "세로 가랜드",
    "Vertical Corner Garlands": "세로 모서리 가랜드",
    "Vertical Garland will line up with the left or right side of a block.": (
        "세로 가랜드는 블록의 왼쪽이나 오른쪽에 맞춰져요."
    ),
    "Garland and Bows": "가랜드와 리본",
    "Lighting the Kinara": "키나라 밝히기",
    "Troubleshooting": "문제 해결",
    "Lamp Post with Bow Decoration!": "리본으로 장식한 가로등!",
    "Decorating the Post": "가로등 장식하기",
    "Leaves with Lights": "조명이 달린 잎",
    "Leaves With Lights": "조명이 달린 잎",
    "Festive Lights": "축제 조명",
    "Horizontal Lights": "가로 조명",
    "Diagonal Lights": "대각선 조명",
    "Vertical Lights": "세로 조명",
    "Vertical Corner Lights": "세로 모서리 조명",
    "Cap Lights": "지붕 꼭대기 조명",
    "Wires": "전선",
    "Bulbs": "전구",
    "Classic Lights": "클래식 조명",
    "Mini (Tree) Lights": "미니(트리) 조명",
    "Icicle Lights": "고드름 조명",
    "Twinkling Icicle Lights": "반짝이는 고드름 조명",
    "Vertical Lights (Right)": "세로 조명(오른쪽)",
    "Vertical Corner (Left)": "세로 모서리(왼쪽)",
    "Vertical Corner (Right)": "세로 모서리(오른쪽)",
    "Merry Mantels": "축제 벽난로 선반",
    "Decorating the Mantels": "벽난로 선반 장식하기",
    "Read on to learn about the Mantel Decorations...": (
        "계속 읽으며 벽난로 선반 장식을 알아보세요..."
    ),
    "Mantel Decorations": "벽난로 선반 장식",
    "Lighting the Menorah": "메노라 밝히기",
    "To remove objects from the Mkeka, just click on it with an empty hand.": (
        "음케카 위의 물건을 치우려면 빈손으로 클릭하세요."
    ),
    "Red Holiday Music Disc": "빨간 연말 음악 음반",
    "The Red Disc plays an assortment of Lofi Holiday Songs by LofiGeek.": (
        "빨간 음반에서는 LofiGeek의 여러 로파이 연말 음악이 재생돼요."
    ),
    "Green Holiday Music Disc": "초록색 연말 음악 음반",
    "The Green Disc plays more traditional Holiday music.": (
        "초록색 음반에서는 좀 더 전통적인 연말 음악이 재생돼요."
    ),
    "Decorative Food Trays": "장식용 음식 쟁반",
    "Kwanzaa Foods": "콴자 음식",
    "Hanukkah Foods": "하누카 음식",
    "Roof Stairs/Slabs that have been snowed on": "눈이 쌓인 지붕 계단과 반 블록",
    "Roof Stairs changed via Snowball assault": "눈덩이로 바뀐 지붕 계단",
    "Stocking": "크리스마스 양말",
    "The stockings were hung on the Merry Mantel with care...": (
        "크리스마스 양말을 축제 벽난로 선반에 정성껏 걸었어요..."
    ),
    "Templates": "형판",
    "Diagonal Templates": "대각선 형판",
    "Vertical Templates": "세로 형판",
    "Vertical Corner Templates": "세로 모서리 형판",
    "Small Spruce Trees": "작은 가문비나무",
    "Trees in Tree Stands": "트리 받침대에 놓은 나무",
    "Ornaments": "장식구",
    "Decorated Christmas Tree": "장식한 크리스마스트리",
    "Mobs in Ugly Christmas Armor": "못난이 크리스마스 방어구를 입은 몹",
    "A Zombie in an Ugly Sweater. He's ready to party!": (
        "못난이 스웨터를 입은 좀비예요. 파티 준비가 끝났네요!"
    ),
    "Walls": "담장",
    "Walls with Garland": "가랜드를 두른 담장",
    "Wreath": "리스",
    "Lit Wreath": "조명 리스",
    "To craft a wreath, you'll need 8 Spruce Leaves and a Bow.": (
        "리스를 만들려면 가문비나무 잎 8개와 리본 1개가 필요해요."
    ),
    "Next, you'll craft the bulbs for the lights, using the recipes here:": (
        "다음 레시피로 조명에 사용할 전구를 제작하세요:"
    ),
}

PATCHOULI_TEXT.update(
    {
        "This delightfully tacky Holiday-themed armor comes in 2 colors but can be "
        "mixed and matched. $(br2)Hats and Sweaters (Helmets and Chestplates) have a "
        "chance to drop from Mobs that are wearing it. ": (
            "이 유쾌하고 촌스러운 연말 방어구는 2가지 색상이 있으며 서로 섞어 입을 수 "
            "있어요. $(br2)모자와 스웨터(투구와 흉갑)는 이를 착용한 몹에게서 일정 확률로 "
            "떨어져요."
        ),
        "The armor has several tiers and can be upgraded using a Smithing Table.$(br2)"
        "$(li)Tier 1 (Leather): crafted or obtained by drop $(li)Tier 2 (Iron): "
        "upgraded in Smithing Table $(li)Tier 3 (Diamond): upgraded in Smithing Table "
        "$(li)Tier 4 (Netherite): upgraded in Smithing Table": (
            "방어구는 여러 단계로 나뉘며 대장장이 작업대에서 업그레이드할 수 있어요."
            "$(br2)$(li)1단계(가죽): 제작하거나 몹에게서 획득 $(li)2단계(철): 대장장이 "
            "작업대에서 업그레이드 $(li)3단계(다이아몬드): 대장장이 작업대에서 업그레이드 "
            "$(li)4단계(네더라이트): 대장장이 작업대에서 업그레이드"
        ),
        "To upgrade your armor to Tier 2 or above, you will need a special Smithing "
        "Template. These are found in chests throughout the Overworld and can be "
        "replicated with the following recipes:": (
            "방어구를 2단계 이상으로 업그레이드하려면 특별한 대장장이 형판이 필요해요. 이 "
            "형판은 오버월드 곳곳의 상자에서 찾을 수 있으며 다음 레시피로 복제할 수 있어요:"
        ),
        'The "Red" set of Ugly Christmas Armor is crafted with Leather and Red Wool. '
        '$(br2)The "Green" set is crafted with Leather and Green Wool. $(br2)The '
        "recipes for crafting the Tier 1 pieces are:": (
            '"빨간색" 못난이 크리스마스 방어구 세트는 가죽과 빨간색 양털로 제작해요. '
            '$(br2)"초록색" 세트는 가죽과 초록색 양털로 제작해요. $(br2)1단계 부위별 '
            "제작법은 다음과 같아요:"
        ),
        "If you lose this book, or need to make another for any reason, all it takes "
        "is: 1 book, 1 green dye, and a candy cane.": (
            "이 안내서를 잃어버렸거나 하나 더 필요하다면 책 1권, 초록색 염료 1개, "
            "막대사탕 1개로 만들 수 있어요."
        ),
        "To add a wreath to any kind of Vanilla door, combine the door and a wreath in "
        "a crafting table. $(br2)Doors with Lit Wreaths on them will also give off "
        "light.": (
            "기본 게임의 어떤 문이든 리스를 달려면 조합대에서 문과 리스를 조합하세요. "
            "$(br2)조명 리스가 달린 문은 빛도 내요."
        ),
        "The Picket Fence is a special decorative type of Fence block. It has a "
        "matching gate and comes in all Vanilla wood colors.$(br2)These pretty fences "
        "can be decorated with greenery and lights to spruce them up for the holidays.": (
            "울타리는 특별한 장식용 울타리 블록이에요. 어울리는 울타리 문이 있고 기본 "
            "게임의 모든 나무 색상으로 만들 수 있어요.$(br2)예쁜 울타리에 푸른 가랜드와 "
            "조명을 둘러 연말 분위기로 꾸밀 수 있어요."
        ),
        "To decorate a Picket Fence, combine it with any type of Horizontal Garland in "
        "a crafting table. $(br2)The Picket Fence Gate can be combined with a wreath "
        "of your choice for decoration.": (
            "울타리를 장식하려면 조합대에서 원하는 종류의 가로 가랜드와 조합하세요. "
            "$(br2)울타리 문은 원하는 리스와 조합해 장식할 수 있어요."
        ),
        "Hot Cocoa, Peppermint Cocoa, and Eggnog are all placeable as a decoration."
        "$(br2)To pick them up, shift-click. To drink them, use as normal. They will "
        "return an empty mug when you are finished drinking.": (
            "핫 코코아, 페퍼민트 코코아, 에그노그는 모두 장식으로 설치할 수 있어요."
            "$(br2)다시 집으려면 Shift 키를 누른 채 클릭하고, 마시려면 평소처럼 "
            "사용하세요. 다 마시면 빈 머그잔이 돌아와요."
        ),
        "Ham is a new drop from Pigs, and can be cooked in a Furnace or Smoker.$(br2)"
        "Eat it as is, or prepare it as a fancy dinner to share with those around you.": (
            "돼지에게서 새롭게 햄이 떨어지며, 화로나 훈연기에서 익힐 수 있어요.$(br2)"
            "그대로 먹거나 근사한 만찬으로 차려 주변 사람들과 나눠 드세요."
        ),
        "The Ham Dinner and Stuffed Poultry Dinner are now consumable decorations. "
        "$(br2)Eat them the same way you do a Cake, and when there is nothing left, you "
        "can take your Platter back to use for the next serving.": (
            "햄 만찬과 속을 채운 가금류 만찬은 먹을 수 있는 장식이에요. $(br2)케이크와 "
            "같은 방법으로 먹고, 모두 먹은 뒤에는 플래터를 회수해 다음 상차림에 사용할 수 "
            "있어요."
        ),
        "The Cookie Tray and Harvest Tray are now interactable decorations. $(br2)Each "
        "time you click on the tray, you will receive the topmost item on the tray. "
        "When there are no more items left, you can take it back to use for the next "
        "serving.": (
            "쿠키 쟁반과 수확물 쟁반은 상호작용할 수 있는 장식이에요. $(br2)쟁반을 클릭할 "
            "때마다 가장 위의 아이템을 받아요. 아이템이 모두 없어지면 쟁반을 회수해 다음 "
            "상차림에 사용할 수 있어요."
        ),
        "Garlands are very similar to lights. They have the same shape placements as "
        "Classic/Mini lights, with the exception of the Cap shape, as a horizontal "
        "works for a peak. They come in three styles: $(li)Plain $(li)White lights "
        "$(li)Multi Lights": (
            "가랜드는 조명과 매우 비슷해요. 지붕 꼭대기에는 가로형을 쓰므로 지붕 꼭대기 "
            "모양만 빼고 클래식/미니 조명과 같은 모양으로 설치할 수 있어요. 다음 3가지 "
            "종류가 있어요: $(li)일반 $(li)흰색 조명 $(li)다색 조명"
        ),
        "Horizontal garlands will connect in and around corners, just like the lights.": (
            "가로 가랜드는 조명처럼 모서리 안팎으로 이어져요."
        ),
        "Diagonal garlands will extend slightly under their placement, similar to "
        "Icicle Lights. This is done so that they line up with eachother better.": (
            "대각선 가랜드는 고드름 조명처럼 설치한 곳의 아래쪽으로 조금 뻗어요. 서로 더 "
            "잘 맞물리게 하기 위한 모양이에요."
        ),
        "Vertical Corner Garland will create two sections of garland at a 90 degree "
        "angle, lining up with the left side or right side of a block.": (
            "세로 모서리 가랜드는 90도 각도로 두 갈래 가랜드를 만들며 블록의 왼쪽이나 "
            "오른쪽에 맞춰져요."
        ),
        "You'll start by crafting a Horizontal Garland.$(br2)To craft this, you'll need "
        "three spruce leaves and two bows.$(br2)You will also need a template for the "
        "other shapes of garland, just like you did for the lights. Read on for the "
        "recipes...": (
            "먼저 가로 가랜드를 제작하세요.$(br2)여기에는 가문비나무 잎 3개와 리본 "
            "2개가 필요해요.$(br2)조명과 마찬가지로 다른 모양의 가랜드를 만들려면 형판도 "
            "필요해요. 계속해서 레시피를 살펴보세요..."
        ),
        "To create the lit versions of the garlands, combine a horizontal garland with "
        "the 'Tree' light of your choice in a crafting table.$(br2)To make other shapes, "
        "combine 3 garlands with a template in a crafting table, as shown here:": (
            "조명 가랜드를 만들려면 조합대에서 가로 가랜드와 원하는 '트리' 조명을 "
            "조합하세요.$(br2)다른 모양은 다음과 같이 조합대에서 가랜드 3개와 형판을 "
            "조합해 만들어요:"
        ),
        "The Kinara has a directional facing and can be placed upon an Mkeka if desired."
        "$(br2)It is fully functional and is designed to emulate the lighting of the "
        "Kwanzaa candles in order.": (
            "키나라는 방향을 바꿔 설치할 수 있으며 원한다면 음케카 위에 놓을 수 있어요."
            "$(br2)실제로 사용할 수 있고 콴자 촛불을 순서대로 밝히는 방식을 재현했어요."
        ),
        "To light the Kinara, you will need the following: $(li)1 Black Candle $(li) 3 "
        "Red Candles $(li) 3 Green Candles $(li)Flint and Steel $(br2)The candles go "
        "into the Kinara in the following color order: Black, Red, Green, Red, Green, "
        "Red, Green.": (
            "키나라를 밝히려면 다음이 필요해요: $(li)검은색 초 1개 $(li)빨간색 초 3개 "
            "$(li)초록색 초 3개 $(li)부싯돌과 부시 $(br2)초는 검은색, 빨간색, 초록색, "
            "빨간색, 초록색, 빨간색, 초록색 순서로 키나라에 놓으세요."
        ),
        "Begin by placing the first candle, and then light it. Then place the second, "
        "and light it. Repeat this process until all candles are lit.$(br2)A chat "
        "message will appear denoting each candle as it is lit.The more candles that "
        "are lit, the more light the Kinara will give off.": (
            "첫 번째 초를 놓고 불을 붙인 다음, 두 번째 초를 놓고 불을 붙이세요. 모든 초에 "
            "불이 붙을 때까지 반복하세요.$(br2)초를 밝힐 때마다 채팅 메시지가 나타나요. "
            "밝힌 초가 많을수록 키나라가 더 밝은 빛을 내요."
        ),
        "If you use the wrong color candle, it will give the most recently placed "
        "candle back to you and you can try again.$(br2)If your Kinara does not light "
        "up, remove all of the candles (just click with an empty hand) and place them/"
        "light them again in the proper order.": (
            "잘못된 색상의 초를 사용하면 가장 최근에 놓은 초가 돌아오므로 다시 시도할 수 "
            "있어요.$(br2)키나라가 켜지지 않으면 빈손으로 클릭해 모든 초를 꺼낸 뒤 올바른 "
            "순서로 다시 놓고 불을 붙이세요."
        ),
        "The Lamp Post block extends upward when placed on top of itself and a has "
        "directional facing for decorating purposes. $(br)The top of a Lamp Post will "
        'light up if you use a Torch on it. $(br2)Remove the torch and "turn off" the '
        "Lamp Post by clicking on it with an empty hand.": (
            "가로등 블록 위에 같은 블록을 놓으면 위로 이어지며 장식에 맞게 방향을 바꿀 수 "
            "있어요. $(br)가로등 꼭대기에 횃불을 사용하면 불이 켜져요. $(br2)빈손으로 "
            "클릭하면 횃불을 빼고 가로등을 '끌' 수 있어요."
        ),
        "When a Lamp Post Block is 3 blocks tall, the thin pole section can be decorated "
        "by using either a bow or any type of wreath on it. $(br2)Remove the decoration "
        "by clicking on the pole with an empty hand.": (
            "가로등 블록을 3블록 높이로 쌓으면 가는 기둥 부분에 리본이나 원하는 리스를 "
            "사용해 장식할 수 있어요. $(br2)기둥을 빈손으로 클릭하면 장식을 제거해요."
        ),
        "Give your winter trees and bushes a festive glow. Spruce Leaves can combined "
        "with Lights in a crafting table to create Leaves with Lights. $(br2)To make "
        "the large light versions, use Classic base lights. To make the regular sized "
        "versions, use Tree Lights.": (
            "겨울 나무와 덤불에 축제의 빛을 더해 보세요. 조합대에서 가문비나무 잎과 "
            "조명을 조합하면 조명이 달린 잎을 만들 수 있어요. $(br2)큰 조명 버전에는 "
            "클래식 기본 조명을, 보통 크기 버전에는 트리 조명을 사용하세요."
        ),
        "Light up your world with festive, bright lights. These lights come in 4 styles: "
        "$(li)Classic (Large bulbs) $(li)Mini (Small bulbs) $(li)Icicle $(li)Twinkling "
        "Icicle": (
            "밝고 축제 분위기가 나는 조명으로 세계를 밝혀 보세요. 조명은 다음 4가지 "
            "종류가 있어요: $(li)클래식(큰 전구) $(li)미니(작은 전구) $(li)고드름 "
            "$(li)반짝이는 고드름"
        ),
        "All light versions come in a set of white, or a set of multi-colors. For the "
        "Classic and Mini styles, there are 8 shapes: $(li)Horizontal $(li)Diagonal "
        "(Left) $(li)Diagonal (Right) $(li)Vertical (Left) $(li)Vertical (Right) "
        "$(li)Vertical Corner (Left) $(li)Vertical Corner (Right) $(li)Cap (Roof Peak)": (
            "모든 조명은 흰색이나 다색 세트로 나와요. 클래식과 미니 조명에는 다음 8가지 "
            "모양이 있어요: $(li)가로 $(li)대각선(왼쪽) $(li)대각선(오른쪽) "
            "$(li)세로(왼쪽) $(li)세로(오른쪽) $(li)세로 모서리(왼쪽) "
            "$(li)세로 모서리(오른쪽) $(li)지붕 꼭대기"
        ),
        "For the Icicle and Twinkling Icicle lights, there are 4 shapes: $(li)Horizontal "
        "$(li)Diagonal (Left) $(li)Diagonal (Right) $(li)Cap (Roof Peak)": (
            "고드름과 반짝이는 고드름 조명에는 다음 4가지 모양이 있어요: $(li)가로 "
            "$(li)대각선(왼쪽) $(li)대각선(오른쪽) $(li)지붕 꼭대기"
        ),
        "Horizontal lights will connect in and around corners. They are placed "
        "similarly to vines.": (
            "가로 조명은 모서리 안팎으로 이어지며 덩굴과 비슷한 방식으로 설치해요."
        ),
        "Diagonal Icicle/Twinkling Icicle Lights have a somewhat odd placement and "
        "will extend under the block they are placed on. This is done so that they "
        "connect better when placed.": (
            "대각선 고드름/반짝이는 고드름 조명은 설치 방식이 조금 특이하며 설치한 블록 "
            "아래로 뻗어요. 서로 더 잘 이어지도록 만든 모양이에요."
        ),
        "Vertical Lights will line up with the left or right side of a block.": (
            "세로 조명은 블록의 왼쪽이나 오른쪽에 맞춰져요."
        ),
        "Vertical Corner Lights will create two sections of lights at a 90 degree "
        "angle, lining up with the left side or right side of a block.": (
            "세로 모서리 조명은 90도 각도로 두 갈래 조명을 만들며 블록의 왼쪽이나 "
            "오른쪽에 맞춰져요."
        ),
        "Cap lights can be used to fill in a gap that is left when a roof peak has an "
        "odd number of blocks. $(br2) Read on for the recipes...": (
            "지붕 꼭대기의 블록 수가 홀수일 때 남는 틈은 지붕 꼭대기 조명으로 채울 수 "
            "있어요. $(br2) 계속해서 레시피를 살펴보세요..."
        ),
        "To craft the lights, you'll start with the wire. Green Wire is used for Classic "
        "Lights and Mini Lights, and White Wire is used for Icicle Lights and Twinkling "
        "Icicle Lights. $(br2) The recipes for the 2 kinds of wire are shown here:": (
            "조명 제작은 전선부터 시작해요. 초록색 전선은 클래식 조명과 미니 조명에, "
            "흰색 전선은 고드름 조명과 반짝이는 고드름 조명에 사용해요. $(br2) 2가지 "
            "전선의 레시피는 다음과 같아요:"
        ),
        "Now you will craft the base type of lights. These are what you will use to "
        "create the placement shapes that were mentioned previously.$(br2)There is a "
        "different base type for every style of lights: Classic, Mini, Icicle, and "
        "Twinkling Icicle.$(br2)Special note: The Mini base types are also used for the "
        "Christmas Trees, and are named as such.": (
            "이제 기본형 조명을 제작할 차례예요. 앞에서 설명한 설치 모양을 만들 때 이 "
            "조명을 사용해요.$(br2)클래식, 미니, 고드름, 반짝이는 고드름 조명마다 서로 "
            "다른 기본형이 있어요.$(br2)참고: 미니 기본형은 크리스마스트리에도 사용되므로 "
            "트리 조명이라는 이름이 붙어 있어요."
        ),
        "You have your base lights, now you're ready to craft the light blocks.$(br2)"
        "Horizontal and Cap shapes have standard crafting recipes. Shapes defined as "
        "'Left' or 'Right' will require a template to craft.$(br2)To craft a template "
        "light recipe, just place 3 of your base lights along with the correct template "
        "into the crafting table.": (
            "기본형 조명을 마련했으니 이제 조명 블록을 제작할 수 있어요.$(br2)가로형과 "
            "지붕 꼭대기 모양에는 일반 제작법이 있어요. '왼쪽' 또는 '오른쪽'으로 나뉜 "
            "모양은 제작할 때 형판이 필요해요.$(br2)형판을 사용하는 조명은 기본형 조명 "
            "3개와 알맞은 형판을 조합대에 넣어 제작하세요."
        ),
        "Only one example of each type will be shown here, but the recipe shapes are "
        "the same for all of the lights.$(br2)The only exceptions are Icicles and "
        "Twinkling Icicles, which do not have any vertical or corner versions.": (
            "여기에는 종류별 예시 하나만 나오지만 모든 조명의 레시피 모양은 같아요."
            "$(br2)세로형이나 모서리형이 없는 고드름과 반짝이는 고드름 조명만 예외예요."
        ),
    }
)

PATCHOULI_TEXT.update(
    {
        "Fireplace Logs fit perfectly with Merry Mantels. They have a directional "
        "facing and can be lit with a Flint and Steel, or doused with a Bucket of "
        "Water. $(br2)Fireplace logs can also be connected to Redstone if desired. "
        "$(br2)The recipe for the Fireplace Logs follows:": (
            "벽난로 장작은 축제 벽난로 선반과 꼭 맞아요. 방향을 바꿔 설치할 수 있으며 "
            "부싯돌과 부시로 불을 붙이거나 물 양동이로 끌 수 있어요. $(br2)원한다면 "
            "벽난로 장작을 레드스톤에 연결할 수도 있어요. $(br2)벽난로 장작의 레시피는 "
            "다음과 같아요:"
        ),
        "Cozy up on a cold night, next to a beautiful fireplace. These Merry Mantels "
        "can be decorated and are perfect for sipping cocoa by the fire. $(br2) The "
        "mantels are 3 blocks wide, 3 blocks high, and 1 block deep, and are centered "
        "around where you place the block. $(br2) Read on for how to decorate them...": (
            "추운 밤에는 아름다운 벽난로 곁에서 몸을 녹여 보세요. 축제 벽난로 선반은 "
            "장식할 수 있고 불가에서 코코아를 마시기에 딱 좋아요. $(br2) 선반은 너비 "
            "3블록, 높이 3블록, 깊이 1블록이며 블록을 설치한 위치를 중심으로 생겨요. "
            "$(br2) 계속해서 장식 방법을 알아보세요..."
        ),
        "Merry Mantels can be decorated by clicking on each section with Horizontal "
        "Garlands of any type, and/or stockings. $(br2) To form a corner on the ends, "
        "just place a second piece of the same garland.$(br2) To remove the decorations, "
        "click on the mantel with an empty hand. $(br2) Read on for the Recipe...": (
            "축제 벽난로 선반의 각 부분에 원하는 가로 가랜드나 크리스마스 양말을 사용해 "
            "장식할 수 있어요. $(br2) 양끝에 모서리를 만들려면 같은 가랜드를 하나 더 "
            "놓으세요.$(br2) 장식을 제거하려면 선반을 빈손으로 클릭하세요. $(br2) "
            "계속해서 레시피를 살펴보세요..."
        ),
        "The Merry Mantels come in every color of the Vanilla woods. They can be "
        "crafted with 4 planks and 3 slabs, as shown here.": (
            "축제 벽난로 선반은 기본 게임의 모든 나무 색상으로 만들 수 있어요. 다음과 "
            "같이 판자 4개와 반 블록 3개로 제작해요."
        ),
        "There are some specific decoration blocks that are made to fit perfectly atop "
        "a Merry Mantel. They are: $(br) $(li)Candle Holders Decoration "
        "$(li)Gingerbread House Decoration $(li)Lantern and Poinsetta Decoration "
        "$(li)Christmas Tree Decoration $(li)Lantern and Ornament Decoration $(li)Joy "
        "Decoration": (
            "축제 벽난로 선반 위에 꼭 맞도록 만든 전용 장식 블록이 있어요: $(br) "
            "$(li)촛대 장식 $(li)진저브레드 집 장식 $(li)랜턴과 포인세티아 장식 "
            "$(li)크리스마스트리 장식 $(li)랜턴과 장식구 장식 $(li)기쁨 장식"
        ),
        "Because clicking on a decorated Mantel removes one of its decorations, you'll "
        "need to shift-click when placing down Mantel Deco Blocks or any others on the "
        "Mantels.": (
            "장식한 벽난로 선반을 클릭하면 장식 하나가 제거되므로, 선반 장식 블록이나 "
            "다른 블록을 선반 위에 놓을 때는 Shift 키를 누른 채 클릭해야 해요."
        ),
        "The Menorah has a directional facing is designed to emulate the lighting of "
        "the Shamash, followed by each subsequent candle, going from right to left."
        "$(br2).": (
            "메노라는 방향을 바꿔 설치할 수 있으며 샤마시부터 시작해 오른쪽에서 왼쪽으로 "
            "초를 하나씩 밝히는 방식을 재현했어요.$(br2)"
        ),
        "To light the Menorah, you will need the following: $(li)1 Blue Candle $(li) 8 "
        "White Candles $(li)Flint and Steel $(br2)The candles go into the Menorah as "
        "follows: Blue first, then the remaining White Candles.": (
            "메노라를 밝히려면 다음이 필요해요: $(li)파란색 초 1개 $(li)흰색 초 8개 "
            "$(li)부싯돌과 부시 $(br2)메노라에는 파란색 초를 먼저 놓고 나머지 흰색 "
            "초를 차례로 놓으세요."
        ),
        "Begin by placing the Shamash, the Blue Candle, and then light it. Then place "
        "the second, and light it. Repeat this process until all candles are lit."
        "$(br2)The more candles that are lit, the more light the Menorah will give off.": (
            "샤마시인 파란색 초를 먼저 놓고 불을 붙이세요. 그런 다음 두 번째 초를 놓고 "
            "불을 붙이세요. 모든 초에 불이 붙을 때까지 반복하세요.$(br2)밝힌 초가 "
            "많을수록 메노라가 더 밝은 빛을 내요."
        ),
        "If you use the wrong color candle, it will give the most recently placed "
        "candle back to you and you can try again.$(br2)If your Menorah does not light "
        "up, remove all of the candles (just click with an empty hand) and place them/"
        "light them again in the proper order.": (
            "잘못된 색상의 초를 사용하면 가장 최근에 놓은 초가 돌아오므로 다시 시도할 수 "
            "있어요.$(br2)메노라가 켜지지 않으면 빈손으로 클릭해 모든 초를 꺼낸 뒤 "
            "올바른 순서로 다시 놓고 불을 붙이세요."
        ),
        "The Mkeka has a directional facing and can interact with the Kinara, Chalice, "
        "and Corn.$(br2)An Mkeka has the capacity to hold a single Kinara, or: $(li)A "
        "Chalice by itself $(li)Up to 3 Corn $(li)A combination of a Chalice and up to "
        "3 Corn.": (
            "음케카는 방향을 바꿔 설치할 수 있으며 키나라, 성배, 옥수수와 상호작용해요."
            "$(br2)음케카에는 키나라 1개를 놓거나 다음 조합을 놓을 수 있어요: "
            "$(li)성배 1개 $(li)옥수수 최대 3개 $(li)성배 1개와 옥수수 최대 3개"
        ),
        "Holiday Music Discs can be found in chests throughout the Overworld, or can be "
        "dropped when a Skeleton kills a Creeper.": (
            "연말 음악 음반은 오버월드 곳곳의 상자에서 찾거나 스켈레톤이 크리퍼를 "
            "처치할 때 얻을 수 있어요."
        ),
        "The following blocks are decorative only, but are used in Dinner and Food Tray "
        "recipes: $(br2)$(li)Quartz Platter $(li)Wood Tray": (
            "다음 블록은 장식용이지만 만찬과 음식 쟁반 레시피에도 사용해요: "
            "$(br2)$(li)석영 플래터 $(li)나무 쟁반"
        ),
        "Presents are found in Chests throughout the Overworld. $(br2) When a Present "
        "is placed, the wrapping colors are chosen randomly. Presents can be picked up "
        "with Silk Touch. $(br2)Breaking a Present open will reveal the gift inside. "
        'Gifts rang from really good to "Gee, you sholdn\'t have!"': (
            "선물은 오버월드 곳곳의 상자에서 찾을 수 있어요. $(br2) 선물을 설치하면 "
            "포장 색상이 무작위로 정해져요. 섬세한 손길로 선물을 다시 집을 수 있어요. "
            "$(br2)선물을 부수어 열면 안에 든 물건이 나와요. 아주 좋은 선물부터 "
            '"아, 이런 것까지 안 주셔도 되는데!" 싶은 선물까지 다양해요.'
        ),
        "Roof Stairs and Slabs are special blocks that change to become topped with "
        "snow.$(br2)They come in all Vanilla wood colors, along with the Stone Bricks, "
        "Polished Blackstone Bricks, and Deepslate Bricks varieties.": (
            "지붕 계단과 반 블록은 위에 눈이 쌓인 모습으로 바뀌는 특별한 블록이에요."
            "$(br2)기본 게임의 모든 나무 색상과 석재 벽돌, 윤나는 흑암 벽돌, 심층암 "
            "벽돌 종류가 있어요."
        ),
        " $(br2)To craft the Roof Stairs and Roof Slabs, combine the Vanilla stairs or "
        "slabs with some Roof Tiles in a crafting table.$(br2) The Roof Tiles recipe "
        "is shown here:": (
            " $(br2)지붕 계단과 지붕 반 블록은 조합대에서 기본 게임의 계단이나 반 블록을 "
            "지붕 타일과 조합해 만들어요.$(br2) 지붕 타일 레시피는 다음과 같아요:"
        ),
        "If it is snowing, the slabs and stairs will automatically change to a snowy "
        "version over time. $(br2)If you're somewhere without snow, never fear: You can "
        "manually change them by hitting them with a snowball.": (
            "눈이 내리면 계단과 반 블록이 시간이 지나면서 눈 덮인 모습으로 자동으로 "
            "바뀌어요. $(br2)눈이 오지 않는 곳이라도 걱정하지 마세요. 눈덩이를 던져 "
            "맞히면 직접 바꿀 수 있어요."
        ),
        "Templates are used to define a left or right shape of a light/garland block "
        "when crafting. Templates are reusable and will remain after crafting. "
        "Template recipes require green dye and paper, and can be used for both lights "
        "and garlands. The template recipes are:": (
            "형판은 조명/가랜드 블록을 제작할 때 왼쪽 또는 오른쪽 모양을 정하는 데 "
            "사용해요. 형판은 재사용할 수 있어 제작 후에도 남아요. 초록색 염료와 종이로 "
            "형판을 만들며 조명과 가랜드에 모두 사용할 수 있어요. 형판 레시피는 다음과 "
            "같아요:"
        ),
        "To decorate a Christmas Tree, you will first need to locate and cut down a "
        "Small Spruce Tree. These can be found growing in cold biomes, and sometimes "
        "their saplings will drop from Spruce Leaves.": (
            "크리스마스트리를 장식하려면 먼저 작은 가문비나무를 찾아 베어야 해요. 작은 "
            "가문비나무는 추운 생물군계에서 자라며 가문비나무 잎에서 묘목이 떨어질 때도 "
            "있어요."
        ),
        "Once you have your tree, you can leave it as is, or dye it with White Dye for "
        "a Snowy Christmas Tree. $(br2) Next, you'll need to craft a stand to place the "
        "Tree in:": (
            "나무를 구했다면 그대로 쓰거나 흰색 염료로 염색해 눈 덮인 크리스마스트리로 "
            "만들 수 있어요. $(br2) 다음으로 트리를 놓을 받침대를 제작하세요:"
        ),
        "Now you're ready to decorate your tree. $(br2)Tree Decorations are: "
        "$(li)Lights $(li)Ornaments $(li)Sweet Berry Garland $(li)Tree Topper$(br2)"
        "There are two color choices for Tree Lights and Ornaments: White and Bright "
        "Colored, and you have your choice of either a Star or a Bow for a Tree Topper.": (
            "이제 트리를 장식할 준비가 됐어요. $(br2)트리 장식은 다음과 같아요: "
            "$(li)조명 $(li)장식구 $(li)달콤한 열매 가랜드 $(li)트리 꼭대기 장식"
            "$(br2)트리 조명과 장식구는 흰색과 밝은 다색 중에서 고를 수 있고, 트리 "
            "꼭대기 장식은 별과 리본 중에서 고를 수 있어요."
        ),
        " The Trees have 3 sections, and each section can take one set of Tree Lights, "
        "one set of Ornaments, and one set of Sweet Berry Garland. Clicking on the Top "
        "section with a Topper will place the Topper Block above the tree. To remove/"
        "change the topper, interact with the topper itself.$(br2)To decorate, you place "
        "the item onto the desired Tree section. To remove an item you have placed on "
        "the tree, click on it with an empty hand.": (
            " 트리는 3개 부분으로 나뉘며 각 부분에 트리 조명 1세트, 장식구 1세트, "
            "달콤한 열매 가랜드 1세트를 달 수 있어요. 꼭대기 부분에 트리 꼭대기 장식을 "
            "사용하면 트리 위에 장식 블록이 놓여요. 장식을 제거하거나 바꾸려면 장식 자체와 "
            "상호작용하세요.$(br2)원하는 트리 부분에 아이템을 사용해 장식하세요. 트리에 "
            "놓은 아이템은 빈손으로 클릭하면 제거할 수 있어요."
        ),
        "Zombies and Skeletons of all kinds, Creepers, and even the Zombie Piglins are "
        "all showing their Holiday Spirit by wearing Ugly Sweaters and Santa Hats! "
        "$(br2)Mobs wearing the armor have a random chance to drop the armor pieces.": (
            "온갖 좀비와 스켈레톤, 크리퍼, 심지어 좀비화 피글린까지 못난이 스웨터와 산타 "
            "모자를 쓰고 연말 분위기를 뽐내요! $(br2)방어구를 착용한 몹은 일정 확률로 "
            "방어구 부위를 떨어뜨려요."
        ),
        "Note: This feature is customizable and can be disabled in the config file. "
        "$(br2)Ugly Armor drops from mobs can also be disabled in the config file.": (
            "참고: 이 기능은 설정할 수 있으며 설정 파일에서 비활성화할 수 있어요. "
            "$(br2)몹이 못난이 방어구를 떨어뜨리는 기능도 설정 파일에서 끌 수 있어요."
        ),
        "Any Vanilla Wall block can be decorated with Garland.$(br2)Just combine the "
        "wall with your choice of garland in a crafting table.": (
            "기본 게임의 모든 담장 블록을 가랜드로 장식할 수 있어요.$(br2)조합대에서 "
            "담장과 원하는 가랜드를 조합하세요."
        ),
        "Wreaths are very versatile. With a wreath, you can place it as-is, use it on a "
        "Lamp Post, or combine it other blocks such as Doors and Picket Fence Gates to "
        "decorate them.$(br2)They come in three styles: $(li)Plain $(li)White Lights "
        "$(li)Multicolored Lights": (
            "리스는 여러 용도로 쓸 수 있어요. 그대로 설치하거나 가로등에 달 수 있고, 문이나 "
            "울타리 문 같은 블록과 조합해 장식할 수도 있어요.$(br2)다음 3가지 종류가 "
            "있어요: $(li)일반 $(li)흰색 조명 $(li)다색 조명"
        ),
        "Once you have your wreath, you can give it an extra pop with some lights."
        "$(br2)To make a lit wreath, combine a wreath with Tree Lights of your choice in "
        "a crafting table:": (
            "리스를 만들었다면 조명을 더해 한층 돋보이게 할 수 있어요.$(br2)조명 리스는 "
            "조합대에서 리스와 원하는 트리 조명을 조합해 만들어요:"
        ),
    }
)


def find_jar() -> Path:
    """현재 설치본에서 MerryMaking JAR 하나를 찾아요."""
    matches = sorted((resolve_source_root() / "mods").glob(JAR_PATTERN))
    if len(matches) != 1:
        raise FileNotFoundError(f"대상 JAR이 정확히 한 개가 아니에요: {matches}")
    return matches[0]


def read_language(jar: Path) -> dict[str, str]:
    """현재 영어 언어 파일을 읽어요."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read("assets/merrymaking/lang/en_us.json"))
    if not isinstance(value, dict) or len(value) != EXPECTED_KEYS:
        raise ValueError(f"영어 키 수가 달라요: {len(value)}")
    if not all(
        isinstance(key, str) and isinstance(text, str) for key, text in value.items()
    ):
        raise TypeError("언어 키 또는 값이 문자열이 아니에요")
    return value


def material_name(source: str) -> str:
    """장식 블록의 바탕 재료를 번역해요."""
    try:
        return MATERIALS[source]
    except KeyError as exc:
        raise KeyError(f"알 수 없는 재료: {source}") from exc


def translate_name(source: str) -> str:
    """아이템·블록의 조합형 영어 이름을 한국어로 옮겨요."""
    leading = source[: len(source) - len(source.lstrip())]
    trailing = source[len(source.rstrip()) :]
    text = source.strip()
    if text in EXACT_NAMES:
        return f"{leading}{EXACT_NAMES[text]}{trailing}"

    armor = re.fullmatch(r"(.+) \((Leather|Iron|Diamond)\)", text)
    if armor:
        tier = {"Leather": "가죽", "Iron": "철", "Diamond": "다이아몬드"}[
            armor.group(2)
        ]
        return f"{leading}{translate_name(armor.group(1))} ({tier}){trailing}"
    reinforced = re.fullmatch(r"Reinforced (.+)", text)
    if reinforced:
        return f"{leading}강화 {translate_name(reinforced.group(1))}{trailing}"
    spawn_egg = re.fullmatch(r"(.+) Spawn Egg", text)
    if spawn_egg:
        return f"{leading}{translate_name(spawn_egg.group(1))} 생성 알{trailing}"

    patterns = (
        (r"Exposed (.+) Mantel", lambda m: f"노출된 {material_name(m[1])} 벽난로 선반"),
        (
            r"Weathered (.+) Mantel",
            lambda m: f"풍화된 {material_name(m[1])} 벽난로 선반",
        ),
        (r"Aged (.+) Mantel", lambda m: f"낡은 {material_name(m[1])} 벽난로 선반"),
        (r"(.+) Fireplace Mantel", lambda m: f"{material_name(m[1])} 벽난로 선반"),
        (r"(.+) Mantel", lambda m: f"{material_name(m[1])} 벽난로 선반"),
        (r"(.+) Roofed Stairs", lambda m: f"{material_name(m[1])} 지붕 계단"),
        (r"(.+) Snowy Stairs", lambda m: f"{material_name(m[1])} 눈 덮인 계단"),
        (r"(.+) Roofed Slab", lambda m: f"{material_name(m[1])} 지붕 반 블록"),
        (r"(.+) Snowy Slab", lambda m: f"{material_name(m[1])} 눈 덮인 반 블록"),
        (
            r"(.+) Wall with Garland",
            lambda m: f"가랜드를 두른 {material_name(m[1])} 담장",
        ),
        (
            r"(.+) Wall with Lit Garland",
            lambda m: f"흰색 조명 가랜드를 두른 {material_name(m[1])} 담장",
        ),
        (
            r"(.+) Wall with Multi Lit Garland",
            lambda m: f"다색 조명 가랜드를 두른 {material_name(m[1])} 담장",
        ),
        (
            r"(.+) Wall with Lit Garland \(White Lights\)",
            lambda m: f"흰색 조명 가랜드를 두른 {material_name(m[1])} 담장",
        ),
        (
            r"(.+) Wall with Lit Garland \(Multi Lights\)",
            lambda m: f"다색 조명 가랜드를 두른 {material_name(m[1])} 담장",
        ),
        (r"(.+) Door with Wreath", lambda m: f"리스가 달린 {material_name(m[1])} 문"),
        (
            r"(.+) Door with Lit Wreath",
            lambda m: f"흰색 조명 리스가 달린 {material_name(m[1])} 문",
        ),
        (
            r"(.+) Door with Multi Lit Wreath",
            lambda m: f"다색 조명 리스가 달린 {material_name(m[1])} 문",
        ),
        (r"(.+) Picket Fence", lambda m: f"{material_name(m[1])} 울타리"),
        (r"(.+) Picket Fence Gate", lambda m: f"{material_name(m[1])} 울타리 문"),
        (
            r"(.+) Fence with Garland",
            lambda m: f"가랜드를 두른 {material_name(m[1])} 울타리",
        ),
        (
            r"(.+) Wreath Fence with Garland",
            lambda m: f"가랜드를 두른 {material_name(m[1])} 울타리",
        ),
        (
            r"(.+) Fence with Lit Garland",
            lambda m: f"흰색 조명 가랜드를 두른 {material_name(m[1])} 울타리",
        ),
        (
            r"(.+) Fence with Multi Lit Garland",
            lambda m: f"다색 조명 가랜드를 두른 {material_name(m[1])} 울타리",
        ),
        (
            r"(.+) Fence Gate with Wreath",
            lambda m: f"리스가 달린 {material_name(m[1])} 울타리 문",
        ),
        (
            r"(.+) Fence with Gate Wreath",
            lambda m: f"리스가 달린 {material_name(m[1])} 울타리 문",
        ),
        (
            r"(.+) Fence Gate with Lit Wreath",
            lambda m: f"흰색 조명 리스가 달린 {material_name(m[1])} 울타리 문",
        ),
        (
            r"(.+) Fence with Gate Lit Wreath",
            lambda m: f"흰색 조명 리스가 달린 {material_name(m[1])} 울타리 문",
        ),
        (
            r"(.+) Fence Gate with Multi Lit Wreath",
            lambda m: f"다색 조명 리스가 달린 {material_name(m[1])} 울타리 문",
        ),
        (
            r"(.+) Fence with Gate Multi Lit Wreath",
            lambda m: f"다색 조명 리스가 달린 {material_name(m[1])} 울타리 문",
        ),
    )
    for pattern, render in patterns:
        match = re.fullmatch(pattern, text)
        if match:
            return f"{leading}{render(match)}{trailing}"

    orientation = re.fullmatch(r"(.+) \((.+)\)", text)
    if orientation:
        base = translate_light_base(orientation.group(1))
        direction = {
            "Horizontal": "가로",
            "Vertical Left": "왼쪽 세로",
            "Vertical Lefthand": "왼쪽 세로",
            "Vertical Right": "오른쪽 세로",
            "Vertical Righthand": "오른쪽 세로",
            "Vertical Corner Left": "왼쪽 세로 모서리",
            "Vertical Corner Lefthand": "왼쪽 세로 모서리",
            "Vertical Corner Right": "오른쪽 세로 모서리",
            "Vertical Corner Righthand": "오른쪽 세로 모서리",
            "Diagonal Left": "왼쪽 대각선",
            "Diagonal_Left": "왼쪽 대각선",
            "Diagonal Right": "오른쪽 대각선",
            "Diagonal_Right": "오른쪽 대각선",
            "Cap": "지붕 꼭대기",
        }.get(orientation.group(2))
        if direction is None:
            raise KeyError(source)
        return f"{leading}{base} ({direction}){trailing}"
    raise KeyError(source)


def translate_light_base(source: str) -> str:
    """가랜드와 전구 묶음의 기본 이름을 번역해요."""
    values = {
        "Garland": "가랜드",
        "Garland White Lights": "흰색 조명 가랜드",
        "Garland Multi Lights": "다색 조명 가랜드",
        "Mini Lights": "미니 조명",
        "Classic Lights": "클래식 조명",
        "Icicle Lights": "고드름 조명",
        "Twinkling Icicle Lights": "반짝이는 고드름 조명",
        "Mini Multicolored Lights": "다색 미니 조명",
        "Mini MultiColored Lights": "다색 미니 조명",
        "Classic Multicolored Lights": "다색 클래식 조명",
        "Icicle Multicolored Lights": "다색 고드름 조명",
        "Twinkling Multicolored Icicle Lights": "다색 반짝이는 고드름 조명",
        "Twinkling MulticoloredIcicle Lights": "다색 반짝이는 고드름 조명",
    }
    try:
        return values[source]
    except KeyError as exc:
        raise KeyError(source) from exc


def prepare() -> dict[str, object]:
    """현재 영어 원문과 Patchouli 범위를 작업 폴더에 기록해요."""
    jar = find_jar()
    english = read_language(jar)
    with ZipFile(jar) as archive:
        patchouli = sorted(
            name
            for name in archive.namelist()
            if name.startswith(PATCHOULI_PREFIX) and name.endswith(".json")
        )
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    (WORK_ROOT / "en_us.json").write_text(
        json.dumps(english, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    report = {
        "family": FAMILY,
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_mtime_ns": jar.stat().st_mtime_ns,
        "english_keys": len(english),
        "bundled_korean_keys": 0,
        "patchouli_files": len(patchouli),
        "status": "prepared",
    }
    (WORK_ROOT / "inventory.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def build_language() -> dict[str, object]:
    """현재 영어 472개 값을 모두 번역해요."""
    english = read_language(find_jar())
    korean = {}
    errors = []
    for key, source in english.items():
        if source == "":
            korean[key] = ""
            continue
        try:
            korean[key] = translate_name(source)
        except (KeyError, RecursionError) as exc:
            errors.append(f"{key}={source!r}: {exc}")
    if not errors:
        for path in (WORK_ROOT / "ko_kr.json", LANG_OUTPUT):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(korean, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    report = {
        "translated": len(korean),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "language_build.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def read_patchouli(jar: Path) -> dict[str, object]:
    """현재 영어 Patchouli 파일 48개를 JSON으로 읽어요."""
    with ZipFile(jar) as archive:
        names = sorted(
            name
            for name in archive.namelist()
            if name.startswith(PATCHOULI_PREFIX) and name.endswith(".json")
        )
        return {name: json.loads(archive.read(name)) for name in names}


def translate_patchouli_value(source: str) -> str:
    """Patchouli의 제목·설명·본문 한 값을 번역해요."""
    if source in PATCHOULI_TEXT:
        return PATCHOULI_TEXT[source]
    return translate_name(source)


def translate_patchouli_object(
    value: object, source_path: str, json_path: str, errors: list[str]
) -> object:
    """Patchouli JSON에서 사용자 표시 문자열만 재귀적으로 바꿔요."""
    if isinstance(value, dict):
        translated = {}
        for key, child in value.items():
            path = f"{json_path}.{key}" if json_path else key
            if key in VISIBLE_FIELDS and isinstance(child, str):
                try:
                    translated[key] = translate_patchouli_value(child)
                except (KeyError, RecursionError) as exc:
                    errors.append(f"{source_path}:{path}={child!r}: {exc}")
                    translated[key] = child
            else:
                translated[key] = translate_patchouli_object(
                    child, source_path, path, errors
                )
        return translated
    if isinstance(value, list):
        return [
            translate_patchouli_object(
                child, source_path, f"{json_path}[{index}]", errors
            )
            for index, child in enumerate(value)
        ]
    return value


def build_patchouli() -> dict[str, object]:
    """영어 Patchouli 48개 파일을 한국어 전용 경로로 생성해요."""
    sources = read_patchouli(find_jar())
    rendered = {}
    errors = []
    visible_occurrences = 0
    visible_sources = set()
    for name, value in sources.items():
        for _, _, child in walk_visible_fields(value):
            visible_occurrences += 1
            visible_sources.add(child)
        rendered[name] = translate_patchouli_object(value, name, "", errors)
    if not errors:
        for name, value in rendered.items():
            relative = Path(name).relative_to(PATCHOULI_PREFIX)
            path = PATCHOULI_OUTPUT / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    report = {
        "files": len(sources),
        "visible_occurrences": visible_occurrences,
        "visible_unique_sources": len(visible_sources),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "patchouli_build.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def walk_visible_fields(value: object, path: str = "") -> list[tuple[str, str, str]]:
    """Patchouli 사용자 표시 필드를 경로와 함께 펼쳐요."""
    rows = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if key in VISIBLE_FIELDS and isinstance(child, str):
                rows.append((key, child_path, child))
            rows.extend(walk_visible_fields(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(walk_visible_fields(child, f"{path}[{index}]"))
    return rows


def walk_json(value: object, path: str = "") -> list[tuple[str, str, object]]:
    """JSON 안의 모든 값을 키와 경로와 함께 펼쳐요."""
    rows = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            rows.append((key, child_path, child))
            rows.extend(walk_json(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(walk_json(child, f"{path}[{index}]"))
    return rows


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR 데이터와 FTB Quests·KubeJS의 별도 표시 문구를 감사해요."""
    instance = resolve_source_root()
    jar = find_jar()
    errors = []
    data_counts: defaultdict[str, int] = defaultdict(int)
    advancement_displays = []
    visible_data_fields = []
    localized_data_fields = []
    invalid_data_json = []
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            if not name.startswith("data/merrymaking/") or not name.endswith(".json"):
                continue
            parts = name.split("/")
            if len(parts) >= 3:
                data_counts[parts[2]] += 1
            try:
                value = json.loads(archive.read(name))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                invalid_data_json.append(f"{name}: {exc}")
                continue
            if "/advancement/" in name and isinstance(value, dict):
                display = value.get("display")
                if display is not None:
                    advancement_displays.append({"path": name, "display": display})
            for key, path, child in walk_json(value):
                if key in VISIBLE_DATA_KEYS:
                    row = {"file": name, "path": path, "value": child}
                    if isinstance(child, dict) and isinstance(
                        child.get("translate"), str
                    ):
                        localized_data_fields.append(row)
                    else:
                        visible_data_fields.append(row)

    references = {"ftbquests": [], "kubejs": [], "read_errors": []}
    for label, base in (
        ("ftbquests", instance / "config/ftbquests"),
        ("kubejs", instance / "kubejs"),
    ):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {
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
                references["read_errors"].append(f"{path}: {exc}")
                continue
            namespace_count = text.count("merrymaking:")
            visible_candidates = []
            name_candidates = []
            for line_number, line in enumerate(text.splitlines(), 1):
                if line.strip().startswith("//"):
                    continue
                if re.search(r"Mama['’]s\s+MerryMaking|\bMerryMaking\b", line):
                    name_candidates.append(line_number)
                if "merrymaking:" in line and any(
                    marker in line
                    for marker in (
                        "custom_name",
                        "customName",
                        "displayName",
                        "title",
                        "tooltip",
                        "lore",
                    )
                ):
                    visible_candidates.append(line_number)
            if namespace_count or name_candidates:
                references[label].append(
                    {
                        "path": path.relative_to(instance).as_posix(),
                        "namespace_occurrences": namespace_count,
                        "direct_name_candidate_lines": name_candidates,
                        "visible_namespace_candidate_lines": visible_candidates,
                    }
                )

    if invalid_data_json:
        errors.extend(invalid_data_json)
    if advancement_displays:
        errors.append(f"표시형 발전 과제가 있어요: {advancement_displays}")
    if visible_data_fields:
        errors.append(f"데이터 파일에 직접 표시 문구가 있어요: {visible_data_fields}")
    errors.extend(str(value) for value in references["read_errors"])
    for label in ("ftbquests", "kubejs"):
        for row in references[label]:
            if row["direct_name_candidate_lines"]:
                errors.append(f"{label}에 직접 모드명 후보가 있어요: {row}")
            if row["visible_namespace_candidate_lines"]:
                errors.append(f"{label}에 직접 표시 후보가 있어요: {row}")

    report = {
        "family": FAMILY,
        "jar": jar.name,
        "data_json_files": sum(data_counts.values()),
        "data_counts": dict(sorted(data_counts.items())),
        "advancement_files": data_counts["advancement"],
        "advancement_displays": advancement_displays,
        "recipe_files": data_counts["recipe"],
        "visible_data_fields": visible_data_fields,
        "localized_data_fields": localized_data_fields,
        "references": references,
        "ftbquests_display_work": "not_present",
        "kubejs_display_work": "ids_only",
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "surface_audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report, errors


def preserved_errors(label: str, source: str, target: str) -> list[str]:
    """자리표시자·서식·Patchouli 토큰·숫자·줄바꿈·URL을 확인해요."""
    errors = []
    for name, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식 코드", FORMAT_CODE),
        ("Patchouli 토큰", PATCHOULI_TOKEN),
        ("URL", URL),
    ):
        if pattern.findall(source) != pattern.findall(target):
            errors.append(
                f"{label} {name} 불일치: "
                f"{pattern.findall(source)} != {pattern.findall(target)}"
            )
    source_numbers = Counter(NUMBER.findall(source))
    target_numbers = Counter(NUMBER.findall(target))
    missing_numbers = source_numbers - target_numbers
    if missing_numbers:
        errors.append(
            f"{label} 원문 숫자 누락: {dict(missing_numbers)}; "
            f"target={NUMBER.findall(target)}"
        )
    if source.count("\n") != target.count("\n"):
        errors.append(
            f"{label} 줄바꿈 수 불일치: "
            f"{source.count(chr(10))} != {target.count(chr(10))}"
        )
    return errors


def load_json_without_duplicates(path: Path) -> tuple[object | None, list[str]]:
    """JSON을 읽으며 같은 객체 안의 중복 키를 찾아요."""
    duplicates = []

    def object_hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        value = {}
        for key, child in pairs:
            if key in value:
                duplicates.append(key)
            value[key] = child
        return value

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=object_hook
        )
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"{path}: {exc}"]
    return value, [f"{path} 중복 키: {key}" for key in duplicates]


def verify_language() -> tuple[dict[str, object], list[str]]:
    """472개 언어 키의 구조·확정값·보존 요소·영문 잔여를 검증해요."""
    errors = []
    english = read_language(find_jar())
    work_value, work_errors = load_json_without_duplicates(WORK_ROOT / "ko_kr.json")
    output_value, output_errors = load_json_without_duplicates(LANG_OUTPUT)
    errors.extend(work_errors + output_errors)
    if not isinstance(work_value, dict) or not isinstance(output_value, dict):
        report = {"errors": errors, "status": "incomplete"}
        return report, errors
    expected = {
        key: "" if source == "" else translate_name(source)
        for key, source in english.items()
    }
    if list(english) != list(work_value) or list(english) != list(output_value):
        errors.append("언어 키 또는 순서가 현재 영어 원문과 달라요")
    if work_value != output_value or output_value != expected:
        errors.append("작업본·산출물·확정 번역값이 서로 달라요")

    intentional_same = {"creativeTabs.winter"}
    allowed_latin = {"Mama", "MerryMaking", "LofiGeek", "bSHIFT"}
    untranslated = []
    latin_residue = {}
    collisions: defaultdict[str, list[str]] = defaultdict(list)
    for key, source in english.items():
        target = output_value.get(key)
        if not isinstance(target, str):
            errors.append(f"문자열이 아닌 언어 값이 있어요: {key}")
            continue
        errors.extend(preserved_errors(key, source, target))
        if source == target and source and key not in intentional_same:
            untranslated.append(key)
        residue = sorted(set(LATIN_WORD.findall(target)) - allowed_latin)
        if residue:
            latin_residue[key] = residue
        if key.startswith(("block.", "item.")) and not key.endswith(".tooltip"):
            collisions[target].append(key)
    unexpected_collisions = {}
    for target, keys in collisions.items():
        if len({english[key] for key in keys}) > 1:
            unexpected_collisions[target] = keys
    if untranslated:
        errors.append(f"영어와 같은 번역값이 남았어요: {untranslated}")
    if latin_residue:
        errors.append(f"허용하지 않은 영문 잔여가 있어요: {latin_residue}")
    if unexpected_collisions:
        errors.append(f"서로 다른 검색명이 충돌해요: {unexpected_collisions}")
    report = {
        "keys": len(output_value),
        "expected_keys": EXPECTED_KEYS,
        "untranslated_candidates": untranslated,
        "latin_residue": latin_residue,
        "unexpected_name_collisions": unexpected_collisions,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def mask_visible_fields(value: object) -> object:
    """표시 문자열만 표식으로 바꿔 나머지 Patchouli 구조를 비교해요."""
    if isinstance(value, dict):
        return {
            key: "__VISIBLE__"
            if key in VISIBLE_FIELDS and isinstance(child, str)
            else mask_visible_fields(child)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [mask_visible_fields(child) for child in value]
    return value


def verify_patchouli() -> tuple[dict[str, object], list[str]]:
    """Patchouli 48개 파일의 경로·구조·표시 문구·보존 요소를 검증해요."""
    errors = []
    sources = read_patchouli(find_jar())
    expected_paths = {
        PATCHOULI_OUTPUT / Path(name).relative_to(PATCHOULI_PREFIX) for name in sources
    }
    actual_paths = set(PATCHOULI_OUTPUT.rglob("*.json"))
    if expected_paths != actual_paths:
        errors.append(
            "Patchouli 파일 경로가 달라요: "
            f"missing={sorted(str(path) for path in expected_paths - actual_paths)}, "
            f"extra={sorted(str(path) for path in actual_paths - expected_paths)}"
        )

    allowed_latin = {
        "Minecraft",
        "Shift",
        "LofiGeek",
        "Mama",
        "MerryMaking",
        "br",
        "li",
    }
    latin_residue = {}
    untranslated = []
    translated_occurrences = 0
    source_values = []
    for name, source_value in sources.items():
        output_path = PATCHOULI_OUTPUT / Path(name).relative_to(PATCHOULI_PREFIX)
        if not output_path.is_file():
            continue
        output_value, output_errors = load_json_without_duplicates(output_path)
        errors.extend(output_errors)
        if not isinstance(output_value, dict):
            continue
        if mask_visible_fields(source_value) != mask_visible_fields(output_value):
            errors.append(f"표시 문구 밖의 Patchouli 구조가 바뀌었어요: {name}")
        source_rows = walk_visible_fields(source_value)
        output_rows = walk_visible_fields(output_value)
        if len(source_rows) != len(output_rows):
            errors.append(f"표시 필드 수가 달라요: {name}")
            continue
        for index, (source_row, output_row) in enumerate(
            zip(source_rows, output_rows, strict=True)
        ):
            source_field, source_path, source = source_row
            target_field, target_path, target = output_row
            label = f"{name}#{index}"
            source_values.append(source)
            if (source_field, source_path) != (target_field, target_path):
                errors.append(f"표시 필드 경로가 달라요: {label}")
            try:
                expected = translate_patchouli_value(source)
            except (KeyError, RecursionError) as exc:
                errors.append(f"Patchouli 번역표에 원문이 없어요: {label}: {exc}")
                continue
            if target != expected:
                errors.append(f"Patchouli 확정 번역값이 달라요: {label}")
            errors.extend(preserved_errors(label, source, target))
            if source == target and source != "Mama's MerryMaking":
                untranslated.append(label)
            if source != target:
                translated_occurrences += 1
            residue = sorted(set(LATIN_WORD.findall(target)) - allowed_latin)
            if residue:
                latin_residue[label] = residue
    if untranslated:
        errors.append(f"영어와 같은 Patchouli 값이 남았어요: {untranslated}")
    if latin_residue:
        errors.append(f"Patchouli에 허용하지 않은 영문 잔여가 있어요: {latin_residue}")
    report = {
        "files": len(sources),
        "visible_occurrences": len(source_values),
        "visible_unique_sources": len(set(source_values)),
        "translated_occurrences": translated_occurrences,
        "proper_name_retained_occurrences": len(source_values) - translated_occurrences,
        "non_visible_structure_preserved": not any(
            "구조가 바뀌었어요" in error for error in errors
        ),
        "untranslated_candidates": untranslated,
        "latin_residue": latin_residue,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """언어·Patchouli·전체 표시 표면을 함께 검증해요."""
    language, language_errors = verify_language()
    patchouli, patchouli_errors = verify_patchouli()
    surface, surface_errors = audit()
    errors = language_errors + patchouli_errors + surface_errors
    report = {
        "family": FAMILY,
        "language": language,
        "patchouli": patchouli,
        "surface_audit": surface["status"],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "family_validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = (
        json.loads(deployment_path.read_text(encoding="utf-8"))
        if deployment_path.is_file()
        else None
    )
    translation_report = {
        "family": FAMILY,
        "reviewed_language_keys": language.get("keys", 0),
        "existing_korean_reused": 0,
        "new_language_translations": language.get("keys", 0),
        "patchouli_direct_translations": patchouli.get("translated_occurrences", 0),
        "patchouli_proper_names_retained": patchouli.get(
            "proper_name_retained_occurrences", 0
        ),
        "ftbquests_work": "not_present",
        "kubejs_work": "ids_only",
        "status": report["status"],
    }
    (WORK_ROOT / "translation_report.json").write_text(
        json.dumps(translation_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    completion = {
        "family": FAMILY,
        "language_keys": language.get("keys", 0),
        "patchouli_direct_occurrences": patchouli.get("translated_occurrences", 0),
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
        json.dumps(completion, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report, errors


def deployment_paths() -> set[str]:
    """이 모드가 실제 인스턴스에 적용할 정확한 상대 경로를 반환해요."""
    paths = {"resourcepacks/ATM10_Korean/assets/merrymaking/lang/ko_kr.json"}
    paths.update(
        "resourcepacks/ATM10_Korean/assets/merrymaking/patchouli_books/"
        "merrymanual/ko_kr/" + Path(name).relative_to(PATCHOULI_PREFIX).as_posix()
        for name in read_patchouli(find_jar())
    )
    return paths


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
        "status": (
            "complete" if not errors and not verification_errors else "incomplete"
        ),
    }, errors + verification_errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "prepare",
            "build-language",
            "build-patchouli",
            "build-all",
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
    elif args.command == "build-language":
        result = build_language()
    elif args.command == "build-patchouli":
        result = build_patchouli()
    elif args.command == "build-all":
        language = build_language()
        patchouli = build_patchouli()
        result = {
            "language": language,
            "patchouli": patchouli,
            "status": (
                "complete"
                if language["status"] == patchouli["status"] == "complete"
                else "incomplete"
            ),
        }
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
        language = build_language()
        patchouli = build_patchouli()
        surface, surface_errors = audit()
        verification, verification_errors = verify()
        result = {
            "prepare": prepared,
            "language": language,
            "patchouli": patchouli,
            "audit": surface,
            "verify": verification,
            "status": (
                "complete"
                if not surface_errors and not verification_errors
                else "incomplete"
            ),
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"prepared", "complete"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
