#!/usr/bin/env python3
"""Roots Classic 언어 파일과 연관 FTB Quests를 전면 재검수한다."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import ars_family
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "roots_classic"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
LANG_ROOT = WORK_ROOT / "rootsclassic"
QUEST_ROOT = WORK_ROOT / "quests" / "related"
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[./xX×]\d+)*")


EXACT_BY_SOURCE = {
    "Roots Classic": "Roots Classic",
    "Spell Powder": "주문 가루",
    "Pestle": "막자",
    "Staff": "지팡이",
    "Old Root": "오래된 뿌리",
    "Verdant Sprig": "초록빛 가지",
    "Verdant Sprigs": "초록빛 가지",
    "Infernal Bulb": "지옥의 구근",
    "Infernal Bulbs": "지옥의 구근",
    "Dragon's Eye": "용의 눈",
    "Dragon's Eyes": "용의 눈",
    "Acacia Bark": "아카시아나무 껍질",
    "Dark Oak Bark": "짙은 참나무 껍질",
    "Birch Bark": "자작나무 껍질",
    "Jungle Bark": "정글나무 껍질",
    "Oak Bark": "참나무 껍질",
    "Spruce Bark": "가문비나무 껍질",
    "Bark Knife": "나무껍질 칼",
    "Crystal Staff": "수정 지팡이",
    "Living Pickaxe": "살아 있는 곡괭이",
    "Living Axe": "살아 있는 도끼",
    "Living Sword": "살아 있는 검",
    "Living Hoe": "살아 있는 괭이",
    "Living Shovel": "살아 있는 삽",
    "Sylvan Hood": "실반 두건",
    "Sylvan Robe": "실반 로브",
    "Sylvan Tunic": "실반 튜닉",
    "Sylvan Boots": "실반 장화",
    "Wildwood Mask": "와일드우드 가면",
    "Wildwood Plate": "와일드우드 흉갑",
    "Wildwood Leggings": "와일드우드 레깅스",
    "Wildwood Boots": "와일드우드 장화",
    "Runic Tablet": "룬 석판",
    "Growth Powder": "성장 가루",
    "Mutating Powder": "변이 가루",
    "Nightshade": "나이트셰이드",
    "Blackcurrant": "블랙커런트",
    "Redcurrant": "레드커런트",
    "Whitecurrant": "화이트커런트",
    "Elderberry": "엘더베리",
    "Healing Poultice": "치유 습포",
    "Rooty Stew": "뿌리 스튜",
    "Engraved Blade": "각인된 검",
    "Runic Focus": "룬 초점",
    "Charged Runic Focus": "충전된 룬 초점",
    "Fruit Salad": "과일 샐러드",
    "Mana Research Icon": "마나 연구 아이콘",
    "Mortar": "절구",
    "Casting Altar": "시전 제단",
    "Incense Brazier": "향로",
    "Imbuer": "주입기",
    "Mundane Standing Stone": "평범한 선돌",
    "Attuned Standing Stone": "조율된 선돌",
    "Midnight Bloom": "한밤의 꽃",
    "Flare Orchid": "불꽃 난초",
    "Radiant Daisy": "빛나는 데이지",
    "Repulsing Standing Stone": "밀어내는 선돌",
    "Vacuum Standing Stone": "끌어당기는 선돌",
    "Entangling Standing Stone": "속박하는 선돌",
    "Accelerating Standing Stone": "가속하는 선돌",
    "Igniting Standing Stone": "점화하는 선돌",
    "Growing Standing Stone": "성장시키는 선돌",
    "Healing Standing Stone": "치유하는 선돌",
    "Standing Stone": "선돌",
    "When full set equipped:": "한 세트를 모두 착용했을 때:",
    "When equipped:": "착용했을 때:",
    "Increased Health Regeneration": "체력 재생 증가",
    "Increased Terra Regeneration": "테라 재생 증가",
    "Potency": "위력",
    "Type": "종류",
    "potency": "위력",
    "efficiency": "효율",
    "size": "범위",
    "uses remaining": "남은 사용 횟수",
    "Spikes": "가시",
    "Forceful": "완력",
    "Holy": "신성",
    "Aquatic": "수생",
    "Shadow Step": "그림자 걸음",
    "Unbound": "연결되지 않음",
    "Ritual started": "의식을 시작했습니다",
    "Rending Strike": "분쇄의 일격",
    "Nature's Cure": "자연의 치유",
    "Shatter": "산산조각",
    "Earth Spike": "대지 가시",
    "Ender Warp": "엔더 도약",
    "Dandelion Winds": "민들레 바람",
    "Combustion": "연소",
    "Growth": "성장",
    "Water Blast": "물 폭발",
    "Time Stop": "시간 정지",
    "Inferno": "업화",
    "Shielding": "보호막",
    "Acceleration": "가속",
    "Regeneration": "재생",
    "Life Drain": "생명력 흡수",
    "Electric Spark": "전기 불꽃",
    "Insanity": "광기",
    "Shining Ray": "빛나는 광선",
    "Devil's Flower": "악마의 꽃",
    "Rose's Thorns": "장미 가시",
    "Solar Smite": "태양 강타",
    "Blistering Cold": "혹한",
    "Natural Arts": "자연의 비술",
    "Bark Harvesting": "나무껍질 채취",
    "Rare Materials": "희귀 재료",
    "Roots of Magic": "마법의 뿌리",
    "Old Roots": "오래된 뿌리",
    "Lawn Care": "잔디 관리",
    "New Plants": "새로운 식물",
    "Berries": "열매",
    "Foraging": "채집",
    "Medicine": "약",
    "Spellcraft": "주문 제작",
    "The Mortar": "절구",
    "The Pestle": "막자",
    "Usage": "사용법",
    "Imbuing a Staff": "지팡이 주입",
    "The Imbuer": "주입기",
    "Staff Mechanics": "지팡이 사용법",
    "Modifiers": "변형자",
    "Base Ingredients": "기본 재료",
    "Terra": "테라",
    "Casting Costs": "시전 비용",
    "Ritual": "의식",
    "Living Tools": "살아 있는 도구",
    "Self-Repairing": "자가 수리",
    "Growth Ritual": "성장 의식",
    "Standing Stones": "선돌",
    "Engraved Stones": "각인된 돌",
    "Animal Reanimation": "동물 소생",
    "Life Giver": "생명을 주는 자",
    "The Crystal Staff": "수정 지팡이",
    "Reusable Magic": "재사용 가능한 마법",
    "Adding Spells": "주문 추가",
    "Limitations": "제약",
    "Downfall Control": "강우 조절",
    "Weather Magic": "날씨 마법",
    "Fire Blast": "화염 폭발",
    "Offensive Rituals": "공격 의식",
    "Enhanced Standing Stones": "강화된 선돌",
    "The Next Level": "다음 단계",
    "Monster Reanimation": "몬스터 소생",
    "Undeath": "불사",
    "Sylvan Armor": "실반 방어구",
    "Druidic Robes": "드루이드 로브",
    "Wildwood Armor": "와일드우드 방어구",
    "Wooden Armor": "나무 방어구",
    "Energized Stones": "활성화된 선돌",
    "Accelerator": "가속기",
    "Entangler": "속박기",
    "Grower": "성장기",
    "Healer": "치유기",
    "Igniter": "점화기",
    "Repulsor": "밀어내기 장치",
    "Vacuum": "끌어당기기 장치",
    "Mass Breeding": "대량 번식",
    "Animal Farm": "동물 농장",
    "Taking It Back": "되찾기",
    "Sacrifice": "희생",
    "Runic Foci": "룬 초점",
    "Stored Power": "저장된 힘",
    "Charging It Up": "충전하기",
    "Modular Weapon": "모듈식 무기",
    "Time Shift": "시간 이동",
    "Timey Wimey Stuff": "시간이 뒤죽박죽",
    "Phantom Skeleton": "환영 스켈레톤",
    "Tile Accelerator": "블록 가속기",
    "Entity Accelerator": "개체 가속기",
    "Item added": "아이템을 추가했습니다",
    "Empty": "비어 있음",
    "Not Burning": "타고 있지 않음",
    "Brazier is now burning": "향로가 타기 시작했습니다",
    "Cause Rain": "비 내리기",
    "Banish Rain": "비 그치기",
    "Flare": "불꽃",
    "Shift Time": "시간 이동",
    "Radiance": "광휘",
    "A combination of ingredients that makes up a spell, see Runic Tablet.": "주문을 구성하는 재료의 조합입니다. 룬 석판을 참고하세요.",
    "Used with Mortar to create spells, see Runic Tablet.": "절구와 함께 사용해 주문을 만듭니다. 룬 석판을 참고하세요.",
    "Created using Spell Powder on the Imbuer, see Runic Tablet.": "주입기에서 주문 가루로 만듭니다. 룬 석판을 참고하세요.",
    "Basic spell component; drops from tall grass; see Runic Tablet.": "키 큰 잔디에서 나오는 기본 주문 구성 요소입니다. 룬 석판을 참고하세요.",
    "Spell component; see Runic Tablet.": "주문 구성 요소입니다. 룬 석판을 참고하세요.",
    "Advanced spell component; see Runic Tablet.": "고급 주문 구성 요소입니다. 룬 석판을 참고하세요.",
    "Use a Bark Knife on a log.": "통나무에 나무껍질 칼을 사용하세요.",
    "Peels bark from logs to be used in magic rituals": "통나무에서 마법 의식에 사용할 나무껍질을 벗깁니다",
    "Used to obtain bark from logs.": "통나무에서 나무껍질을 얻는 데 사용합니다.",
    "Self-repairing tool; obtained using a magic ritual; see Runic Tablet.": "마법 의식으로 얻는 자가 수리 도구입니다. 룬 석판을 참고하세요.",
    "Obtained using a magic ritual; see Runic Tablet.": "마법 의식으로 얻습니다. 룬 석판을 참고하세요.",
    "The guidebook for Roots Classic that explains all spells and rituals.": "Roots Classic의 모든 주문과 의식을 설명하는 안내서입니다.",
    "Mutates flora in magical ways; see Runic Tablet.": "식물을 마법으로 변이시킵니다. 룬 석판을 참고하세요.",
    "A pugnant mysterious berry; see Runic Tablet.": "향이 강한 신비로운 열매입니다. 룬 석판을 참고하세요.",
    "Stores energy for Roots Rituals; see Runic Tablet.": "Roots 의식에 사용할 에너지를 저장합니다. 룬 석판을 참고하세요.",
    "Delicious and filling.": "맛있고 든든합니다.",
    "Used with Pestle to create spells, see Runic Tablet.": "막자와 함께 사용해 주문을 만듭니다. 룬 석판을 참고하세요.",
    "Center piece for casting rituals; see Runic Tablet.": "의식을 시전하는 중심 장치입니다. 룬 석판을 참고하세요.",
    "Holds incense to burn during rituals; see Runic Tablet.": "의식 중에 태울 향을 담습니다. 룬 석판을 참고하세요.",
    "Create any magical Staff using Spell Powder, see Runic Tablet.": "주문 가루로 마법 지팡이를 만듭니다. 룬 석판을 참고하세요.",
    "Basic ritual stone, used to create ritual patterns as shown in the Runic Tablet.": "룬 석판에 표시된 의식 패턴을 구성하는 기본 선돌입니다.",
    "Advanced ritual stone, used to create ritual patterns as shown in the Runic Tablet.": "룬 석판에 표시된 의식 패턴을 구성하는 고급 선돌입니다.",
    "Repulse nearby stuff, crafting ritual defined in Runic Tablet.": "근처의 물체를 밀어냅니다. 제작 의식은 룬 석판을 참고하세요.",
    "Vacuum nearby stuff, crafting ritual defined in Runic Tablet.": "근처의 물체를 끌어당깁니다. 제작 의식은 룬 석판을 참고하세요.",
    "Slowness beacon, crafting ritual defined in Runic Tablet.": "주변에 둔화를 부여합니다. 제작 의식은 룬 석판을 참고하세요.",
    "Speed beacon, crafting ritual defined in Runic Tablet.": "주변에 신속을 부여합니다. 제작 의식은 룬 석판을 참고하세요.",
    "Burn your enemies, crafting ritual defined in Runic Tablet.": "주변의 적을 불태웁니다. 제작 의식은 룬 석판을 참고하세요.",
    "Growth booster for your plants, crafting ritual defined in Runic Tablet.": "주변 식물의 성장을 촉진합니다. 제작 의식은 룬 석판을 참고하세요.",
    "Regeneration beacon, crafting ritual defined in Runic Tablet.": "주변에 재생을 부여합니다. 제작 의식은 룬 석판을 참고하세요.",
    "Standing Stone for decoration": "장식용 선돌",
    "No ritual found with these central ingredients": "이 중심 재료에 맞는 의식이 없습니다",
    "Ritual found but stones are not placed correctly": "의식은 맞지만 선돌 배치가 올바르지 않습니다",
    "Ritual found, but brazier ingredients are missing or not lit": "의식은 맞지만 향로 재료가 없거나 불이 붙지 않았습니다",
    "Disabled By Config!": "설정에서 비활성화됨!",
    "The Entangler stone will grant all nearby creatures the Slowness II potion effect.": "속박하는 선돌은 주변의 모든 생물에게 둔화 II 효과를 부여합니다.",
}


RITUAL_NAMES = {
    "Grow": "성장",
    "Pig Summoning": "돼지 소환",
    "Cow Summoning": "소 소환",
    "Sheep Summoning": "양 소환",
    "Chicken Summoning": "닭 소환",
    "Rabbit Summoning": "토끼 소환",
    "Crystal Forge": "수정 단조",
    "Crystal Imbue": "수정 주입",
    "Summon Rain": "비 내리기",
    "Banish Rain": "비 그치기",
    "Flare": "불꽃",
    "Zombie Summoning": "좀비 소환",
    "Skeleton Summoning": "스켈레톤 소환",
    "Spider Summoning": "거미 소환",
    "Creeper Summoning": "크리퍼 소환",
    "Cave Spider Summoning": "동굴 거미 소환",
    "Slime Summoning": "슬라임 소환",
    "Enderman Summoning": "엔더맨 소환",
    "Accelerator Stone": "가속하는 선돌",
    "Entangler Stone": "속박하는 선돌",
    "Grower Stone": "성장시키는 선돌",
    "Healer Stone": "치유하는 선돌",
    "Igniter Stone": "점화하는 선돌",
    "Repulsor Stone": "밀어내는 선돌",
    "Vacuum Stone": "끌어당기는 선돌",
    "Standing Stone": "선돌",
    "Mass Breeding": "대량 번식",
    "Life Drain": "생명력 흡수",
    "Sacrifice": "희생",
    "Runic Focus": "룬 초점",
    "Runic Focus Charging": "룬 초점 충전",
    "Engraved Blade": "각인된 검",
    "Time Shift": "시간 이동",
}


REPLACEMENTS = (
    ("루츠 클래식", "Roots Classic"),
    ("룬 태블릿", "룬 석판"),
    ("룬 문자판", "룬 석판"),
    ("룬문자 서판", "룬 석판"),
    ("룬 문자 서판", "룬 석판"),
    ("룬 문자 태블릿", "룬 석판"),
    ("스펠 파우더", "주문 가루"),
    ("주문 분말", "주문 가루"),
    ("철자", "주문"),
    ("스태프", "지팡이"),
    ("모르타르", "절구"),
    ("박격포", "절구"),
    ("유봉", "막자"),
    ("임뷰어", "주입기"),
    ("주조 제단", "시전 제단"),
    ("캐스팅 제단", "시전 제단"),
    ("입석", "선돌"),
    ("스탠딩 스톤", "선돌"),
    ("의례", "의식"),
    ("마법", "마법"),
    ("마나", "테라"),
    ("수정자", "변형자"),
    ("효능", "위력"),
    ("녹색 가지", "초록빛 가지"),
    ("푸른 가지", "초록빛 가지"),
    ("지옥 전구", "지옥의 구근"),
    ("용의 눈알", "용의 눈"),
    ("살아있는", "살아 있는"),
    ("와일드 우드", "와일드우드"),
    ("실반 갑옷", "실반 방어구"),
    ("와일드우드 갑옷", "와일드우드 방어구"),
    ("뿌리 의식", "Roots 의식"),
    ("마술 의식", "마법 의식"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("레시피", "제작법"),
    ("네더별", "네더의 별"),
    ("이 태블릿", "룬 석판"),
    ("베리", "열매"),
    ("막자사발", "절구"),
    ("직원", "지팡이"),
    ("서있는 돌", "선돌"),
    ("지옥불 전구", "지옥의 구근"),
    ("지옥불 구근", "지옥의 구근"),
    ("후렴꽃", "코러스 꽃"),
    ("후렴과", "코러스 열매"),
    ("드래곤의 눈", "용의 눈"),
    ("신록 가지", "초록빛 가지"),
    ("황천", "네더"),
    ("야생나무 갑옷", "와일드우드 방어구"),
    ("효율성 수정치", "효율 변형자"),
    ("가속기 돌", "가속하는 선돌"),
    ("인탱글러 스톤", "속박하는 선돌"),
    ("재배자석", "성장시키는 선돌"),
    ("힐러 스톤", "치유하는 선돌"),
    ("점화석", "점화하는 선돌"),
    ("리펄서 스톤", "밀어내는 선돌"),
    ("진공석", "끌어당기는 선돌"),
    ("조명탄 의식", "불꽃 의식"),
    ("제작법를", "제작법을"),
    ("대지 스파이크", "대지 가시"),
    ("주문 구성요소", "주문 구성 요소"),
)


EXACT_QUESTS = {
    "quest.1EBF234015B26F15.quest_desc": [
        "&a&lRoots Classic&r에서 추가하는 기본 방어구로, 얻으려면 의식이 필요합니다!"
    ],
    "quest.1EBF234015B26F15.title": "&2실반 장비",
    "quest.3A2047CC0F59C6CC.quest_desc": ["&a&lRoots Classic&r의 후반 방어구입니다."],
    "quest.3A2047CC0F59C6CC.title": "&a와일드우드 장비",
    "quest.2171DC0B13C4BD43.quest_desc": [
        "&a&lRoots Classic&r은 JEI에서 작아 보일 수 있지만 실제로는 할 일이 아주 많습니다! \\n\\nRoots는 자연의 선물로 의식을 치르는 모드입니다.\\n\\n필요한 아이템은 곳곳에서 찾을 수 있습니다!"
    ],
    "quest.2171DC0B13C4BD43.title": "&a&lRoots Classic",
    "quest.2D474F8075E9DBD0.quest_desc": [
        "먼저 JEI에 표시된 패턴대로 시전 제단과 선돌을 배치하세요. \\n\\n그런 다음 제단에 다이아몬드 블록, 막대기, 블레이즈 가루를 넣으세요. \\n\\n제단 주위에 향로 4개를 놓고 각각 석탄 블록, 아카시아나무 껍질, 초록빛 나무껍질, 자작나무 껍질을 넣은 뒤 부싯돌과 부시로 모두 불을 붙이세요! \\n\\n마지막으로 Shift를 누른 채 제단을 우클릭해 의식을 시작하세요. 작동하지 않으면 선돌 패턴을 확인하세요."
    ],
}


EXACT_BY_KEY = {
    "rootsclassic.research.nature.bark_harvesting.page1info": "나무는 자연 마법에서 매우 중요합니다. 나무와 묘목으로 나무껍질을 조심스럽게 벗기는 칼을 만들 수 있으며, 얻은 껍질은 제작법과 의식에 사용합니다. 통나무를 우클릭하면 나무껍질을 채취하며, 낮은 확률로 통나무가 부서질 수 있습니다.",
    "rootsclassic.research.nature.magical_materials.page3info": "완전히 자란 작물을 수확하면 1/30 확률로 초록빛 가지가 나옵니다. 채취한 뒤에도 생명력을 품고 있어, 물체에 생명을 불어넣는 용도로 자주 사용합니다.",
    "rootsclassic.research.nature.magical_materials.page4info": "다 자란 네더 사마귀를 수확하면 1/20 확률로 지옥의 구근이 나옵니다. 네더의 불길이 깃들어 많은 에너지가 필요할 때 유용합니다. 화로 연료로 쓰거나 스켈레톤에게 주어 위더 스켈레톤으로 만들 수도 있습니다.",
    "rootsclassic.research.nature.magical_materials.page5info": "코러스 꽃을 수확하면 1/10 확률로 용의 눈이 나옵니다. 엔더 드래곤과 같은 기묘한 에너지가 깃들어 있습니다. 주문 재료 외에도 먹으면 코러스 열매보다 강한 효과를 내며, 제련하면 엔더 진주 하나를 얻습니다.",
    "rootsclassic.research.nature.growth_powder.page1info": "이 간단한 혼합물은 흙에 잔디를 자라게 합니다. 우클릭하면 플레이어에게서 4블록 안에 가루를 던져 작은 범위에 잔디를 만듭니다.",
    "rootsclassic.research.nature.mutating_powder.page1info": "네더의 별의 힘으로 새로운 식물을 변이시키는 가루를 만들었습니다. 이 가루는 룬 석판의 주문 구성 요소 항목에 설명된 특정 상황에서만 사용합니다.",
    "rootsclassic.research.nature.berries.page1info": "나뭇잎을 맨손으로 부수면 가끔 무작위 열매를 얻습니다. 서로 다른 특성을 지닌 열매가 다섯 종류 있으며, 일부는 나중에 주문이나 의식에도 사용합니다...",
    "rootsclassic.research.nature.poultice.page1info": "초록빛 가지는 생명과 관련된 성질 때문에 자주 사용합니다. 가지를 으깬 내용물을 습포로 상처에 바르면 체력을 조금 회복합니다.",
    "rootsclassic.research.spells.mortar.page2info": "앞에서 설명한 식물을 으깨려면 도구가 필요합니다. 매끄러운 흰 돌로 만든 이 막자라면 충분합니다.",
    "rootsclassic.research.spells.mortar.page3info": "절구와 막자의 사용법은 간단합니다. 룬 석판에는 여러 주문의 제작법이 실려 있습니다. 주문 재료와 특정 기본 재료를 모두 준비하세요. 가장 기본적인 주문은 제작법의 재료와 오래된 뿌리를 절구에 넣으면 되며, 변형자는 붙일 수 없습니다.",
    "rootsclassic.research.spells.imbuer.page1info": "절구와 막자로 주문 가루를 만들지만 가루만으로는 주문을 사용할 수 없습니다. 주입기는 가루의 자연 에너지를 나뭇가지에 옮깁니다. 막대기와 주문 가루를 넣고 지팡이가 완성될 때까지 기다리세요.",
    "rootsclassic.research.spells.imbuer.page2info": "마법 지팡이는 간단하게 사용합니다. 우클릭을 누른 채 주문을 충전하고 약 일 초 뒤에 손을 떼면 시전합니다. 지팡이는 사용 횟수가 제한되어 있으며 모두 소모하면 파괴됩니다. 효율 변형자를 사용하면 사용 횟수를 늘릴 수 있습니다.",
    "rootsclassic.research.spells.modifiers.page2info": "주문에 변형자를 붙이려면 알맞은 기본 재료가 필요합니다. 오래된 뿌리는 주문을 만들 수 있지만 변형자 슬롯이 없습니다. 초록빛 가지는 슬롯 하나, 지옥의 구근은 둘, 용의 눈은 셋을 제공합니다. 다른 변형자보다 기본 재료를 먼저 절구에 넣어야 합니다.",
    "rootsclassic.research.spells.mana.page1info": "새 지팡이를 들면 몸속에서 깨어난 힘과 화면의 막대를 확인할 수 있습니다. 잎 모양 막대는 주문에 힘을 공급하는 생명력인 테라를 나타냅니다. 모든 주문은 일정량의 테라를 소모하지만 시간이 지나면 빠르게 회복됩니다.",
    "rootsclassic.research.spells.oxeye_daisy.page1info": "데이지는 시간의 흐름과 조율되어 있습니다. 위 제작법으로 화로, 양조기 등 대상 장치의 작동 속도를 높이는 주문을 만들 수 있습니다. 기본 상태에서는 장치의 속도를 세 배로 높입니다.",
    "rootsclassic.research.spells.lily_pad.page1info": "수련잎에는 물과 관련된 힘이 있습니다. 위 제작법으로 플레이어 앞 4블록 지점에 잠시 물을 만들어 내는 주문을 만들 수 있습니다. 불을 끄거나 주변 몹을 밀어낼 때 유용합니다.",
    "rootsclassic.research.spells.radiant_daisy.page1info": "오버월드에서 데이지를 심으세요. 정오에 꽃 옆으로 발광석 블록과 프리즈머린 수정을 하나씩 던진 뒤, 야간 투시 효과를 받은 상태로 변이 가루를 사용하면 빛나는 흰 꽃이 됩니다.",
    "rootsclassic.research.spells.midnight_bloom.page1info": "엔드에서 흑요석보다 두 블록 위에 양귀비를 심으세요. 둔화 효과를 받은 상태로 꽃 옆에 석탄 블록을 던지고 변이 가루를 사용하면 밤처럼 검은 꽃이 됩니다.",
    "rootsclassic.research.ritual.ritual.page2info": "대부분의 의식에는 향이 필요합니다. 향로는 제단과 같은 높이의 9x9 범위 안에 있어야 인식됩니다. 향로에 아이템을 넣고 부싯돌과 부시로 불을 붙이세요. 빈손으로 Shift를 누른 채 우클릭하면 불을 끕니다.",
    "rootsclassic.research.ritual.ritual.page3info": "의식에 필요한 아이템은 제단에 놓고 향 재료에는 불을 붙이세요. 제단에 불필요한 재료가 있거나 주변에 여분의 향이 타고 있으면 의식이 실패합니다. 준비가 끝나면 빈손으로 Shift를 누른 채 제단을 우클릭해 의식을 시작하세요.",
    "rootsclassic.research.ritual.animal_summoning.page1info": "선돌의 향상된 전달 능력으로 죽은 생물의 몸에 충분한 치유 에너지를 주입해 되살릴 수 있습니다. 수동적 몹의 살과 뼈를 재료로 사용하면 해당 몹이 제단 위에서 되살아납니다.",
    "rootsclassic.research.ritual.crystal_staff.page1info": "일반 지팡이의 제한된 사용 횟수에서 벗어나기 위해 땅속 깊은 곳의 희귀 수정을 사용했습니다. 그 결과 주문을 영구히 보관하고 한 번에 최대 네 개까지 담는 수정 지팡이를 만들었습니다.",
    "rootsclassic.research.ritual.crystal_staff.page3info": "지팡이에 주문을 넣으려면 별도 의식이 필요합니다. 표시된 구성 요소 외에 주문 가루를 향 재료로 최대 네 개까지 추가할 수 있습니다. 각 주문은 지팡이에 저장되며 필요하면 기존 주문을 덮어씁니다. Shift를 누른 채 우클릭하면 저장된 주문을 바꿉니다.",
    "rootsclassic.research.ritual.crystal_staff.page5info": "수정 지팡이는 흙, 잔디, 나뭇잎, 통나무 같은 자연 블록 위에 서서 사용해야 합니다. 그렇지 않으면 주문을 시전할 때 사용자의 생명력을 소모합니다.",
    "rootsclassic.research.ritual.monster_summoning.page1info": "더 강력한 제단에서는 소생 의식을 강하고 사악한 대상에게도 적용할 수 있습니다. 뼈와 해당 몬스터가 떨어뜨리는 재료를 공급하면 원하는 몹을 제단 위에 소환합니다.",
    "rootsclassic.research.ritual.sylvan_armor.page1info": "강해진 제단으로 방어구도 개선할 수 있습니다. 가죽 방어구를 바탕으로 마법과 조화를 이루는 로브를 만들었습니다. 방어력은 높지 않지만 스스로 수리되며 주문의 효율 변형자를 둘만큼 높입니다.",
    "rootsclassic.research.ritual.wildwood_armor.page1info": "화려한 로브보다 높은 방어력이 필요할 때는 와일드우드 방어구를 사용하세요. 철 방어구를 바탕으로 만들며 철과 다이아몬드 방어구 사이의 방어력을 가집니다. 스스로 수리되고 배고픈 상태에서도 자연 회복을 높입니다.",
    "rootsclassic.research.ritual.powered_stones.page1info": "선돌로 생명 에너지를 전달해 왔지만 선돌 하나만으로 작동시키지는 못했습니다. 지옥의 구근이 지닌 힘과 의식의 재생 효과를 사용하면 비용 없이 영구적으로 주변에 간단한 효과를 주는 선돌을 만들 수 있습니다.",
    "rootsclassic.research.ritual.life_drain.page1info": "적대적 몹의 생명력은 부패하고 오염되어 있습니다. 이 의식은 넓은 범위의 적대적 몹에게 피해를 주고, 준 피해를 주변 플레이어에게 고르게 나누어 체력을 회복시킵니다.",
    "rootsclassic.research.ritual.sacrifice.page1info": "주문에 필요한 특정 식물을 찾아 긴 모험을 떠나는 일에 지쳤다면 이 불길한 의식을 사용할 수 있습니다. 입자 효과가 끝나면 근처의 몹을 즉시 죽이고, 그 대가로 제단에서 무작위 식물이 나올 수 있습니다. 그 식물의 출처는 알 수 없습니다...",
    "rootsclassic.research.ritual.runic_focus.page1info": "돌에 룬을 새기고 중심에 희귀한 보석을 놓아 생명 에너지를 저장하는 아이템을 만들었습니다. 제단 의식으로 충전한 뒤 에너지를 방출하거나 다른 의식과 제작 과정의 재료로 사용할 수 있습니다.",
    "rootsclassic.research.ritual.runic_focus.page3info": "룬 초점을 충전하려면 오버월드와 네더에서 각각 에너지가 깃든 가루가 필요합니다. 지옥의 구근이 지닌 불의 힘으로 두 가루의 에너지와 의식의 생명 에너지를 룬 초점에 밀어 넣습니다.",
    "rootsclassic.research.ritual.engraved_blade.page1info": "룬 초점의 성질로 새로운 무기를 만들었습니다. 제작할 때 서로 다른 나무껍질을 향 재료로 최대 네 종류까지 태워 검에 여러 효과를 더할 수 있습니다. 효과는 자유롭게 조합할 수 있으며 같은 껍질을 하나 넘게 넣으면 중첩됩니다.",
    "rootsclassic.clearpotionsitem.tooltip": "먹으면 물약 효과를 제거합니다",
    "rootsclassic.healingitem.tooltip": "먹으면 플레이어를 치유합니다",
    "rootsclassic.poisonitem.tooltip": "먹으면 중독됩니다",
    "rootsclassic.mortar.invalid": "제작법이 올바르지 않습니다. 아이템과 순서를 확인하세요",
    "rootsclassic.mortar.disabled": "비활성화된 제작법입니다",
    "rootsclassic.mortar.mixin": "제작법은 맞지만 희귀 재료가 빠졌습니다",
    "death.attack.rootsclassic.fire": "%1$s이(가) 불에 타 사망했습니다",
    "death.attack.rootsclassic.fire.player": "%1$s이(가) %2$s 때문에 불에 타 사망했습니다",
    "death.attack.rootsclassic.wither": "%1$s이(가) 말라 죽었습니다",
    "death.attack.rootsclassic.wither.player": "%1$s이(가) %2$s 때문에 말라 죽었습니다",
    "rootsclassic.configuration.dragonsEyeDropChance": "용의 눈 드롭 확률",
    "rootsclassic.configuration.disablePVP": "PVP 비활성화",
    "rootsclassic.configuration.ticksPerManaRegen": "테라 재생 주기(틱)",
    "rootsclassic.configuration.staffUsesEfficiency": "효율 지팡이 사용 횟수",
    "rootsclassic.configuration.client": "클라이언트",
    "rootsclassic.configuration.infernalStemDropChance": "지옥 줄기 드롭 확률",
    "rootsclassic.configuration.staffUses": "지팡이 사용 횟수",
    "rootsclassic.configuration.barkKnifeBlockStripChance": "나무껍질 칼 통나무 벗김 확률",
    "rootsclassic.configuration.oldRootDropChance": "오래된 뿌리 드롭 확률",
    "rootsclassic.configuration.staffUsesBasic": "기본 지팡이 사용 횟수",
    "rootsclassic.configuration.staffChargeTicks": "지팡이 충전 시간(틱)",
    "rootsclassic.configuration.showTabletWave": "룬 석판 파동 표시",
    "rootsclassic.configuration.manaBarOffset": "테라 막대 위치 조정",
    "rootsclassic.configuration.items": "아이템",
    "rootsclassic.configuration.berriesDropChance": "열매 드롭 확률",
    "rootsclassic.configuration.efficiencyBonusUses": "효율 변형자 추가 사용 횟수",
    "rootsclassic.configuration.magic": "마법",
    "rootsclassic.configuration.verdantSprigDropChance": "초록빛 가지 드롭 확률",
}


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def repair_mojibake(value: str) -> str:
    if not any(mark in value for mark in ("À", "Á", "¿", "¾", "°", "±", "È", "¡")):
        return value
    for encoding in ("euc-kr", "cp949"):
        try:
            repaired = value.encode("latin1").decode(encoding)
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        if any("가" <= char <= "힣" for char in repaired):
            return repaired
    return value


def normalize_text(value: str) -> str:
    value = repair_mojibake(value)
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    return value


def transform(value: object) -> object:
    if isinstance(value, str):
        return normalize_text(value)
    if isinstance(value, list):
        return [transform(item) for item in value]
    return value


def candidates() -> dict[str, object]:
    english = load_json(LANG_ROOT / "en_us.json")
    cache_path = PROJECT_ROOT / "temp/roots_classic_direct_candidate_cache_v2.json"
    cache = load_json(cache_path) if cache_path.is_file() else {}
    requests = sorted(
        source
        for source in set(english.values())
        if isinstance(source, str)
        and source
        and LATIN_WORD.search(source)
        and source not in cache
    )
    failures = []
    if requests:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(ars_family.request_translation, source): source
                for source in requests
            }
            for number, future in enumerate(as_completed(futures), 1):
                source = futures[future]
                try:
                    cache[source] = repair_mojibake(future.result())
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스 보고용
                    cache[source] = source
                    failures.append(f"{source}: {exc}")
                if number % 25 == 0:
                    write_json(cache_path, cache)
        write_json(cache_path, cache)
    output = {
        key: cache.get(source, source) if isinstance(source, str) else source
        for key, source in english.items()
    }
    write_json(LANG_ROOT / "auto_candidates_direct.json", output)
    return {
        "unique_strings": len(set(english.values())),
        "candidate_requests": len(requests),
        "candidate_failures": failures,
        "status": "candidate_requires_full_review",
    }


def normalize_language() -> dict[str, object]:
    english = load_json(LANG_ROOT / "en_us.json")
    auto = load_json(LANG_ROOT / "auto_candidates_direct.json")
    reviewed = {}
    for key, source in english.items():
        if key in EXACT_BY_KEY:
            value = EXACT_BY_KEY[key]
        elif isinstance(source, str) and source.startswith("Spell Component: "):
            name = source.removeprefix("Spell Component: ")
            value = f"주문 구성 요소: {EXACT_BY_SOURCE.get(name, name)}"
        elif isinstance(source, str) and source.startswith("Ritual: "):
            name = source.removeprefix("Ritual: ")
            translated = EXACT_BY_SOURCE.get(name, RITUAL_NAMES.get(name, name))
            value = f"의식: {translated}"
        else:
            value = EXACT_BY_SOURCE.get(source, auto[key])
        reviewed[key] = transform(value)
    write_json(LANG_ROOT / "ko_kr.json", reviewed)
    report = {"reviewed_keys": len(reviewed), "status": "complete"}
    write_json(WORK_ROOT / "language_normalization.json", report)
    return report


def normalize_quests() -> dict[str, object]:
    english = load_json(QUEST_ROOT / "en_us.json")
    korean = load_json(QUEST_ROOT / "ko_kr.json")
    reviewed = {}
    for key, source in english.items():
        value = EXACT_QUESTS.get(key, korean[key])
        reviewed[key] = transform(value)
    write_json(QUEST_ROOT / "ko_kr.json", reviewed)
    report = {"reviewed_keys": len(reviewed), "status": "complete"}
    write_json(WORK_ROOT / "quest_normalization.json", report)
    return report


def string_pairs(
    source: object, target: object, path: str
) -> list[tuple[str, str, str]]:
    if isinstance(source, str) and isinstance(target, str):
        return [(path, source, target)]
    if isinstance(source, list) and isinstance(target, list):
        rows = []
        for index, (left, right) in enumerate(zip(source, target, strict=True)):
            rows.extend(string_pairs(left, right, f"{path}[{index}]"))
        return rows
    return []


def verify_scope(root: Path) -> tuple[dict[str, object], list[str]]:
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    errors = []
    untranslated = []
    if list(english) != list(korean):
        errors.append("키 또는 키 순서가 영어 원문과 다릅니다")
    for key in english.keys() & korean.keys():
        for path, source, target in string_pairs(english[key], korean[key], key):
            for label, pattern in (
                ("자리표시자", PLACEHOLDER),
                ("서식 코드", FORMAT_CODE),
                ("숫자", NUMBER),
            ):
                if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
                    errors.append(f"{label} 불일치: {path}")
            if source.count("\\n") != target.count("\\n"):
                errors.append(f"줄바꿈 불일치: {path}")
            if source == target and LATIN_WORD.search(source):
                untranslated.append(path)
    report = {
        "keys": len(english),
        "untranslated_candidates": untranslated,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    rows = []
    errors = []
    for label, root in (("language", LANG_ROOT), ("quests", QUEST_ROOT)):
        report, current = verify_scope(root)
        report["scope"] = label
        rows.append(report)
        errors.extend(current)
    result = {
        "scopes": rows,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", result)
    return result, errors


def audit() -> tuple[dict[str, object], list[str]]:
    instance = resolve_source_root()
    jar = next((instance / "mods").glob("RootsClassic-*.jar"))
    with ZipFile(jar) as archive:
        advancement_files = [
            name
            for name in archive.namelist()
            if name.startswith("data/rootsclassic/advancement/")
            and name.endswith(".json")
        ]
        advancement_display = []
        for name in advancement_files:
            value = json.loads(archive.read(name))
            if isinstance(value, dict) and "display" in value:
                advancement_display.append(name)
    kubejs_lines = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json"}:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, 1):
            if "rootsclassic:" in line.lower() and any(
                token in line.lower()
                for token in ("name", "display", "tooltip", "lore", "text")
            ):
                kubejs_lines.append(
                    f"{path.relative_to(instance).as_posix()}:{number}:{line.strip()}"
                )
    report = {
        "jar": jar.name,
        "advancement_files": len(advancement_files),
        "advancement_display_files": advancement_display,
        "kubejs_direct_display_lines": kubejs_lines,
        "errors": [],
        "status": "complete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "candidates",
            "normalize-language",
            "normalize-quests",
            "verify",
            "audit",
        ),
    )
    args = parser.parse_args()
    if args.command == "candidates":
        report, errors = candidates(), []
    elif args.command == "normalize-language":
        report, errors = normalize_language(), []
    elif args.command == "normalize-quests":
        report, errors = normalize_quests(), []
    elif args.command == "verify":
        report, errors = verify()
    else:
        report, errors = audit()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
