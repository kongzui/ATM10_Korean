#!/usr/bin/env python3
"""Forbidden and Arcanus 언어와 FTB Quests 번역을 전면 재검수한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "forbidden_arcanus"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
LANG_ROOT = WORK_ROOT / "forbidden_arcanus"
QUEST_SCOPES = ("forbidden__arcanus", "related")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")


NAME_PARTS = {
    "Light Blue": "하늘색",
    "Light Gray": "연회색",
    "Apply Item Modifier": "아이템 특성 적용",
    "Smithing Template": "대장장이 형판",
    "Blacksmith Gavel": "대장장이 망치",
    "Hephaestus Forge": "헤파이스토스 대장간",
    "Arcane Polished Darkstone": "비전 광택 다크스톤",
    "Polished Darkstone": "광택 다크스톤",
    "Arcane Crystal": "비전 수정",
    "Quantum Catcher": "양자 포획기",
    "Obsidiansteel": "흑요석강",
    "Soul Binding": "영혼 결속",
    "Soul Crimson": "영혼 크림슨",
    "Stella Arcanum": "스텔라 아르카눔",
    "Eternal Stella": "이터널 스텔라",
    "Draco Arcanus": "드라코 아르카누스",
    "Maledictus Pact": "말레딕투스 계약",
    "Divine Pact": "신성한 계약",
    "Corrupti Dust": "코럽티 가루",
    "Mundabitur Dust": "문다비투르 가루",
    "Xpetrified Orb": "엑스페트리파이드 구슬",
    "Dark Nether Star": "어둠의 네더의 별",
    "Ender Pearl": "엔더 진주",
    "Dragon Scale": "드래곤 비늘",
    "Spawner Scrap": "생성기 파편",
    "Test Tube": "시험관",
    "Pressure Plate": "압력판",
    "Fence Gate": "울타리 문",
    "Glass Pane": "유리판",
    "Soul Lantern": "영혼 랜턴",
    "Chest Boat": "상자 보트",
    "Bone Meal": "뼛가루",
    "Lost Soul": "길 잃은 영혼",
    "Soul Looting": "영혼 약탈",
    "Aureal Regeneration": "아우레알 재생",
    "Aurealic": "아우레알",
    "Aureal": "아우레알",
    "Aurum": "아우룸",
    "Deorum": "데오룸",
    "Edelwood": "에델우드",
    "Fungyss": "펀지스",
    "Clibano": "클리바노",
    "Elementarium": "엘레멘타리움",
    "Ferrognetic": "페로마그네틱",
    "Maledictus": "말레딕투스",
    "Mundabitur": "문다비투르",
    "Corrupti": "코럽티",
    "Terrastomp": "테라스톰프",
    "Xpetrified": "엑스페트리파이드",
    "Stellarite": "스텔라라이트",
    "Mortem": "모르템",
    "Utrem": "우트렘",
    "Tyr": "티르",
    "Arcane": "비전",
    "Runic": "룬",
    "Rune": "룬",
    "Darkstone": "다크스톤",
    "Black": "검은색",
    "Blue": "파란색",
    "Brown": "갈색",
    "Cyan": "청록색",
    "Gray": "회색",
    "Green": "초록색",
    "Lime": "연두색",
    "Magenta": "자홍색",
    "Orange": "주황색",
    "Pink": "분홍색",
    "Purple": "보라색",
    "Red": "빨간색",
    "White": "흰색",
    "Yellow": "노란색",
    "Aquatic": "수생",
    "Artisan": "장인",
    "Boom": "폭발",
    "Boss": "보스",
    "Carved": "조각된",
    "Chiseled": "조각된",
    "Cooked": "익힌",
    "Corrupted": "타락한",
    "Corrupt": "타락한",
    "Cracked": "금이 간",
    "Crescent": "초승달",
    "Crimson": "크림슨",
    "Cut": "깎인",
    "Dark": "어둠의",
    "Demolishing": "파괴",
    "Diamond": "다이아몬드",
    "Enchanted": "마법이 부여된",
    "Eternal": "불멸",
    "Fading": "희미한",
    "Fiery": "불타는",
    "Fragmented": "조각난",
    "Gilded": "금박",
    "Golden": "금",
    "Growing": "자라나는",
    "Iron": "철",
    "Magical": "마법",
    "Magnetized": "자화된",
    "Netherite": "네더라이트",
    "Nuggety": "금 조각이 열린",
    "Polished": "광택",
    "Reinforced": "강화된",
    "Silver": "은",
    "Soulless": "영혼 없는",
    "Spectral": "영체",
    "Splash": "투척용",
    "Stripped": "껍질 벗긴",
    "Tiled": "타일",
    "Wooden": "나무",
    "Activated": "활성화됨",
    "Deactivated": "비활성화됨",
    "Amulet": "부적",
    "Arrow": "화살",
    "Axe": "도끼",
    "Block": "블록",
    "Blood": "피",
    "Boat": "보트",
    "Boots": "부츠",
    "Bottle": "병",
    "Branch": "가지",
    "Brick": "벽돌",
    "Bricks": "벽돌",
    "Bucket": "양동이",
    "Button": "버튼",
    "Catcher": "포획기",
    "Chain": "사슬",
    "Chestplate": "흉갑",
    "Core": "코어",
    "Crystal": "수정",
    "Deepslate": "심층암",
    "Door": "문",
    "Dust": "가루",
    "Egg": "알",
    "Experience": "경험치",
    "Extractor": "추출기",
    "Eye": "눈",
    "Farmland": "경작지",
    "Fence": "울타리",
    "Fragment": "조각",
    "Gavel": "망치",
    "Glass": "유리",
    "Head": "머리",
    "Helmet": "투구",
    "Hoe": "괭이",
    "Hyphae": "균사",
    "Ingot": "주괴",
    "Injector": "주입기",
    "Jar": "항아리",
    "Ladder": "사다리",
    "Lantern": "랜턴",
    "Lava": "용암",
    "Leaves": "잎",
    "Leggings": "레깅스",
    "Log": "통나무",
    "Looting": "약탈",
    "Magic": "마법",
    "Matter": "물질",
    "Meal": "가루",
    "Milk": "우유",
    "Mixture": "혼합물",
    "Modifier": "특성",
    "Moon": "달",
    "Mortar": "절구",
    "Nugget": "조각",
    "Obelisk": "오벨리스크",
    "Obsidian": "흑요석",
    "Oil": "기름",
    "Orb": "구슬",
    "Orchid": "난초",
    "Ore": "광석",
    "Pact": "계약",
    "Pane": "판",
    "Pearl": "진주",
    "Pedestal": "받침대",
    "Pickaxe": "곡괭이",
    "Piece": "조각",
    "Pillar": "기둥",
    "Planks": "판자",
    "Prism": "프리즘",
    "Relic": "유물",
    "Sand": "모래",
    "Sandstone": "사암",
    "Sapling": "묘목",
    "Scale": "비늘",
    "Scepter": "홀",
    "Scrap": "파편",
    "Sea": "바다",
    "Shovel": "삽",
    "Skull": "해골",
    "Slab": "반 블록",
    "Smelter": "제련",
    "Soulbound": "귀속",
    "Souls": "영혼",
    "Soul": "영혼",
    "Soup": "수프",
    "Spawner": "생성기",
    "Speck": "작은 알갱이",
    "Staff": "지팡이",
    "Stairs": "계단",
    "Star": "별",
    "Stem": "자루",
    "Stick": "막대기",
    "Stone": "돌",
    "Sword": "검",
    "Tank": "탱크",
    "Template": "형판",
    "Tentacle": "촉수",
    "Trader": "상인",
    "Trapdoor": "다락문",
    "Tube": "관",
    "Wall": "담장",
    "Wand": "완드",
    "Wardstone": "수호석",
    "Water": "물",
    "Wax": "밀랍",
    "Whirlwind": "회오리바람",
    "Wing": "날개",
    "Wood": "나무",
}


LANG_EXACT = {
    "itemGroup.forbidden_arcanus.main": "Forbidden & Arcanus",
    "block.forbidden_arcanus.hephaestus_forge.slot_unlocked_at": "%s티어에서 해금",
    "block.forbidden_arcanus.hephaestus_forge.tier": "%s티어",
    "block.forbidden_arcanus.hephaestus_forge.tier.at_least": "최소 %s티어 필요",
    "block.forbidden_arcanus.hephaestus_forge.tier.match_exact": "정확히 %s티어 필요",
    "forbidden_arcanus.ponder.forge_building.header": "헤파이스토스 대장간 만들기",
    "forbidden_arcanus.ponder.forge_building.text_1": "기초 구조물을 만드세요",
    "forbidden_arcanus.ponder.forge_building.text_2": "금박 조각된 광택 다크스톤 9개",
    "forbidden_arcanus.ponder.forge_building.text_3": "조각된 비전 광택 다크스톤 4개",
    "forbidden_arcanus.ponder.forge_building.text_4": "광택 다크스톤 45개",
    "forbidden_arcanus.ponder.forge_building.text_5": "가운데에 대장장이 작업대를 놓으세요",
    "forbidden_arcanus.ponder.forge_building.text_6": "변환할 수 있도록 이 공간을 비워 두세요",
    "forbidden_arcanus.ponder.forge_usage.header": "헤파이스토스 대장간 사용하기",
    "forbidden_arcanus.ponder.forge_usage.text_1": (
        "다크스톤 받침대를 이렇게 배치하면 의식에 쓰는 아이템을 올려둘 수 있습니다"
    ),
    "forbidden_arcanus.ponder.forge_usage.text_2": (
        "비전 수정 오벨리스크도 같은 자리에 놓을 수 있으며 아우레알을 자동 생성합니다"
    ),
    "item.forbidden_arcanus.enhancer.artisan_relic.clibano": "새로운 합금을 만들 수 있습니다.",
    "item.forbidden_arcanus.enhancer.artisan_relic.hephaestus_forge": (
        "필요한 경험치를 크게 줄입니다."
    ),
    "item.forbidden_arcanus.enhancer.clibano_effect": "클리바노 효과:",
    "item.forbidden_arcanus.enhancer.crescent_moon.hephaestus_forge": (
        "시간대에 따라 필요한 아우레알을 줄입니다."
    ),
    "item.forbidden_arcanus.enhancer.crimson_stone.clibano": (
        "사용한 영혼이 더 오래 유지됩니다. (추후 지원)"
    ),
    "item.forbidden_arcanus.enhancer.crimson_stone.hephaestus_forge": (
        "필요한 영혼의 양을 크게 줄입니다."
    ),
    "item.forbidden_arcanus.enhancer.divine_pact.hephaestus_forge": (
        "천상의 아이템을 만들 수 있습니다."
    ),
    "item.forbidden_arcanus.enhancer.elementarium.hephaestus_forge": (
        "원소 아이템을 만들 수 있습니다."
    ),
    "item.forbidden_arcanus.enhancer.hephaestus_forge_effect": "헤파이스토스 대장간 효과:",
    "item.forbidden_arcanus.enhancer.maledictus_pact.hephaestus_forge": (
        "저주받은 아이템을 만들 수 있습니다."
    ),
    "item.forbidden_arcanus.enhancer.soul_crimson_stone.hephaestus_forge": (
        "의식 하나의 정수 요구량을 완전히 없앱니다."
    ),
    "item.forbidden_arcanus.smithing_template.darkstone_upgrade.additions_slot_description": (
        "특성 아이템을 추가하세요"
    ),
    "item.forbidden_arcanus.smithing_template.darkstone_upgrade.applies_to": "장비",
    "item.forbidden_arcanus.smithing_template.darkstone_upgrade.base_slot_description": (
        "방어구, 무기 또는 도구를 추가하세요"
    ),
    "item.forbidden_arcanus.smithing_template.darkstone_upgrade.ingredients": "특성 아이템",
    "item.forbidden_arcanus.stored_entity": "개체: %s",
    "item.forbidden_arcanus.stored_entity.with_name": "개체: %s (%s)",
    "item.forbidden_arcanus.toggle_state": "(우클릭으로 전환)",
    "jei.forbidden_arcanus.category.hephaestus_forge_upgrading": "헤파이스토스 대장간 업그레이드",
    "jei.forbidden_arcanus.category.hephaestus_smithing": "헤파이스토스 대장간 제련",
    "jei.forbidden_arcanus.hephaestus_smithing.required_essence": "필요한 %s: %s",
}


QUEST_REPLACEMENTS = (
    ("Forbidden and Arcanus", "Forbidden & Arcanus"),
    ("Forbidden Arcanus", "Forbidden & Arcanus"),
    ("신비로운 라텍스", "아우레알"),
    ("신비한 라텍스", "아우레알"),
    ("포비든 앤 아르카누스", "Forbidden & Arcanus"),
    ("아케인 크리스탈", "비전 수정"),
    ("아케인 연마된 다크스톤", "비전 광택 다크스톤"),
    ("금박이 입혀진 조각된 연마된 다크스톤", "금박 조각된 광택 다크스톤"),
    ("조각된 연마된 다크스톤", "조각된 광택 다크스톤"),
    ("연마된 다크스톤", "광택 다크스톤"),
    ("헤파에스토스 용광로", "헤파이스토스 대장간"),
    ("아케인 광택나는 암흑석", "비전 광택 다크스톤"),
    ("아케인 광택 암흑석", "비전 광택 다크스톤"),
    ("아케인 광택 다크스톤", "비전 광택 다크스톤"),
    ("신비한 수정", "비전 수정"),
    ("아케인 수정", "비전 수정"),
    ("광택나는 암흑석", "광택 다크스톤"),
    ("광택나는 다크스톤", "광택 다크스톤"),
    ("헤파이스토스 포지", "헤파이스토스 대장간"),
    ("헤파이스토스 용광로", "헤파이스토스 대장간"),
    ("퀀텀 캐처", "양자 포획기"),
    ("양자 포수", "양자 포획기"),
    ("부패한 먼지", "코럽티 가루"),
    ("부패 먼지", "코럽티 가루"),
    ("흑요석 강철", "흑요석강"),
    ("룬의 도가니", "룬 도가니"),
    ("룬 인챈터", "룬 마법부여기"),
    ("룬문자", "룬"),
    ("상위 버전", "업그레이드"),
    ("E터널 스텔라", "이터널 스텔라"),
    ("영원한 스텔라", "이터널 스텔라"),
    ("Liquid 아우레알", "액체 아우레알"),
    ("Source Condenser", "마나 응축기"),
    ("Source Hatches", "마나 해치"),
    ("Source Hatch", "마나 해치"),
    ("Source Jars", "마나 단지"),
    ("Source Jar", "마나 단지"),
    ("Liquefied Source", "액체 마나"),
    ("Source", "마나"),
    ("Eternal Stella", "이터널 스텔라"),
    ("더럼", "데오룸"),
    ("오리얼", "아우레알"),
    ("오레알", "아우레알"),
    ("오렐", "아우레알"),
    ("Aureal", "아우레알"),
    ("Arcane Crystal", "비전 수정"),
    ("Polished Darkstone", "광택 다크스톤"),
    ("Darkstone", "다크스톤"),
    ("Hephaestus Forge", "헤파이스토스 대장간"),
    ("Quantum Injector", "양자 주입기"),
    ("Quantum Catcher", "양자 포획기"),
    ("Mundabitur Dust", "문다비투르 가루"),
    ("Corrupti Dust", "코럽티 가루"),
    ("Corrupti", "코럽티"),
    ("Obsidiansteel", "흑요석강"),
    ("Xpetrified Orb", "엑스페트리파이드 구슬"),
    ("Stellarite Piece", "스텔라라이트 조각"),
    ("Utrem Jar", "우트렘 항아리"),
    ("Smelter Prism", "제련 프리즘"),
    ("Elementarium", "엘레멘타리움"),
    ("Soul Extractor", "영혼 추출기"),
    ("Soul Looting", "영혼 약탈"),
    ("Runic Crucible", "룬 도가니"),
    ("Runic Enchanter", "룬 마법부여기"),
    ("Runic Star Altar", "룬 별 제단"),
    ("ATM Star", "ATM 별"),
    ("Soul Binding Crystal", "영혼 결속 수정"),
    ("Darkstone Pedestal", "다크스톤 받침대"),
    ("Arcane", "비전"),
    ("Dark Matter", "어둠의 물질"),
    ("Black Hole", "블랙홀"),
    ("Quantum", "양자"),
    ("Deorum", "데오룸"),
    ("Chiseled", "조각된"),
    ("chiseled", "조각된"),
    ("Corrupt", "타락한"),
    ("Forge", "대장간"),
    ("forge", "대장간"),
    ("Tier", "티어"),
    ("Souls", "영혼"),
    ("Soul", "영혼"),
    ("Experience", "경험치"),
    ("올더모듐", "Allthemodium"),
    ("엑스페트리파이드 오브", "엑스페트리파이드 구슬"),
    ("떨굼 설정", "전리품"),
    ("라텍스", "정수"),
    ("홀드", "저장"),
    ("그로우 에델우드", "자라나는 에델우드"),
    ("그로우", "기르"),
    ("more...", "그 밖의 재료"),
    ("underground... 깊은 지하", "아주 깊은 지하"),
    ("iquid...물", "물"),
    ("doing...", "찾으러 가는 것"),
    ("happen...", "일이에요."),
    ("Helmets...", "투구"),
    ("work...", "작동하지 않습니다."),
    ("first...", "첫 번째 층"),
    ("though...", "."),
)


NEW_QUEST_VALUES = {
    "quest.03C54B07106091DD.quest_desc": [
        "&c제련 프리즘&r은 이 의식에서 가장 많이 쓰는 아이템일 거예요. &6&lATM 별&r에도 필요합니다! "
        "\\n\\n제작에는 &c블레이즈 가루&r 4개, &8석탄&r 2개, &b비전 수정 블록&r과 "
        "&3엘레멘타리움&r 유물이 필요해요. \\n&c제련 프리즘&r은 도구에 적용하면 부순 아이템을 "
        "바로 제련합니다. 원석은 주괴로, 통나무는 숯으로, 모래는 유리로 바뀌어요. "
        "&6&lATM 별&r 제작에 특히 유용합니다. "
        "\\n\\n화로 연료로도 쓸 수 있지만 효율은 좋지 않습니다."
    ],
    "quest.12256A90B1CE3F90.quest_desc": [
        "채석장이나 공허 채굴기로 광석을 얻을 수도 있지만, &b비전 수정&r을 가장 효율적으로 "
        "자동화하려면 &6&l벌&r을 이용하세요. 정확히는 &b다이아몬드 벌&r이 필요합니다. "
        "\\n&b다이아몬드 벌&r에게 &b비전 수정 블록&r을 "
        "먹이면 &bArcanus 벌&r이 됩니다. \\n\\n&bArcanus 벌&r은 &b비전 수정 블록&r을 "
        "꽃 블록으로 사용해 &bArcanus 벌집 조각&r을 만들며, 이를 &b비전 수정&r으로 가공할 수 있어요."
    ],
    "quest.29434DB0CC2E30E6.title": "&6데오룸",
    "quest.2ADA491A2485061C.quest_desc": [
        "&a경험치&r는 &6&l대장간&r에 필요한 4번째 정수예요. \\n\\n&a경험치 슬롯&r에는 다음 "
        "3가지 중 1가지를 넣어 &a경험치&r를 채울 수 있습니다. \\n\\n1. &a엑스페트리파이드 구슬&r: "
        "가장 많은 &a경험치&r를 줍니다. \\n\\n2. &a경험치 병&r: 적은 &a경험치&r를 주지만 구하기 "
        "쉽습니다. \\n\\n3. &5마법이 부여된 아이템&r: &6&l대장간&r이 &5마법 부여&r를 제거하고 "
        "&a경험치&r로 저장합니다.",
        "{image:atm:textures/questpics/forbidden/forbidden_experience.png width:135 height:100 align:center}",
    ],
    "quest.3B5DEB942752B3BF.quest_subtitle": "자동 헤파이스토스 대장간은 업그레이드 없이 작동하지 않습니다",
    "quest.3B5DEB942752B3BF.title": "업그레이드",
    "quest.40B757772D0FBAC9.quest_desc": [
        "&4피&r는 &6&l대장간&r에서 채워야 하는 3번째 정수예요. \\n\\n대장간 위나 가까이에서 "
        "몹을 처치해 &6&l대장간&r에 &4피&r를 넣을 수 있습니다. \\n\\n&4피&r가 든 시험관을 "
        "&6&l대장간&r에 넣는 방법도 있어요. \\n\\n시험관을 보조 손에 든 채 몹을 처치하면 피가 채워집니다.",
        "{image:atm:textures/questpics/forbidden/forbidden_blood.png width:135 height:100 align:center}",
    ],
    "quest.4A564E8FE587C7E4.quest_desc": [
        "영혼을 얻는 가장 좋은 방법은 영혼 추출기를 쓰는 거예요. \\n\\n네더의 아이템과 블록, "
        "그리고 우트렘 항아리를 조합해 영혼 추출기를 만드세요. 우트렘 항아리에는 에델우드가 "
        "필요합니다. \\n\\n영혼 모래에 대고 우클릭을 누르고 있으면 영혼을 추출합니다. "
        "\\n\\n그러면 영혼 없는 모래가 남습니다."
    ],
    "quest.539266A1C03C2EBA.quest_desc": [
        "영혼은 &6&l대장간&r의 2번째 정수이며, 최대 10만 채우면 됩니다. \\n\\n일반 영혼과 "
        "타락한 영혼은 각각 1로 계산되고, 마법이 부여된 영혼 하나는 10을 모두 채워요.",
        "{image:atm:textures/questpics/forbidden/forbidden_souls.png width:135 height:100 align:center}",
    ],
    "quest.580148D1141446A6.quest_desc": [
        "&c&l네더&r가 부담스럽다면 &2&l오버월드&r에서 영혼을 찾아보세요. \\n\\n월드를 돌아다니다 "
        "보면 길 잃은 영혼을 만날 수 있어요. 예전 &l&6Forbidden \\& Arcanus&r의 블록이 "
        "어두운 숲에 있었기 때문에 이 퀘스트는 그곳으로 안내합니다. 길 잃은 영혼을 처치하면 "
        "영혼을 떨어뜨리지만 효율은 낮아요.\\n\\n\\n",
        "영혼을 찾기 어렵다면 검에 영혼 약탈 마법을 부여하세요. 이 마법이 부여된 무기로 몹을 "
        "처치하면 가끔 영혼이 나타납니다.",
    ],
    "quest.5A6FF0D4BA894306.quest_desc": [
        "&6&lForbidden \\& Arcanus&r의 대표 아이템은 &a이터널 스텔라&r예요. \\n\\n"
        "&6Allthemodium 주괴&r 1개, &a엑스페트리파이드 구슬&r 3개, &2스텔라라이트 조각&r로 "
        "만들 수 있습니다. \\n\\n&a이터널 스텔라&r와 대상 아이템을 아이템 특성 적용 형판으로 "
        "합치면 내구도가 줄지 않게 됩니다. &b다이아몬드 도끼&r, 낚싯대, "
        "&e정제된 발광석 방어구&r처럼 "
        "내구도가 있는 대부분의 아이템에 적용할 수 있어요. \\n\\n다만 제한도 있습니다. \\n\\n주입 수정처럼 사용 횟수를 "
        "소모하거나 Meka-Tool처럼 에너지를 쓰는 아이템에는 적용되지 않습니다."
    ],
    "quest.63C95FDAA447CA47.quest_desc": [
        "&3&l2티어&r에서만 만드는 &7테라스톰프 프리즘&r이에요. \\n\\n&7점적석&r과 "
        "&7점적석 블록&r, "
        "&8부싯돌&r, &b다이아몬드 블록&r이 필요하며 &3엘레멘타리움&r 유물도 넣어야 합니다. "
        "\\n\\n&c불타는 프리즘&r처럼 &7테라스톰프 프리즘&r도 도구에 적용할 수 있고, \\n적용한 도구는 "
        "블록 1개 대신 3x3 영역의 9개를 채굴합니다."
    ],
    "task.3C7296E2E064C061.title": "",
    "quest.0EF9C391EE42824A.quest_desc": [
        "조금 더 비싸지만 만드는 과정도 재미있는 프리즘이에요. \\n\\n&b다이아몬드&r는 여러 모드로 "
        "자동화할 수 있고, &7부싯돌&r은 자갈을 압착·분쇄·농축하는 여러 방법으로 얻을 수 있습니다. "
        "\\n\\n점적석과 점적석 블록은 추출기나 혼합기로 늘릴 수 있어요. 점적석 블록은 점적석 "
        "4개로 만들 수 있습니다. \\n\\n다만 시작할 점적석은 먼저 구해야 해요."
    ],
    "quest.173541B0765DA13E.quest_desc": [
        "자동화하기 가장 쉬운 프리즘이에요. \\n\\n팬텀 막, 깃털, 양털은 &b&lHNN&r으로 "
        "자동화할 수 있습니다. \\n\\n&7박쥐 날개&r만 생성기를 이용해 따로 모아야 해요."
    ],
    "quest.1FCC474860587169.quest_desc": [
        "후반 제작법에는 &6제련 프리즘&r이 필요하지만 1티어 대장간으로 만들 수 있어요. "
        "\\n\\nJEI에서 필요한 대장간 정수 수치를 확인하세요. &6블레이즈 가루&r 4개, &8석탄&r 2개, "
        "&b비전 수정&r도 필요합니다. \\n\\n마지막 재료인 &9엘레멘타리움&r은 정글 사원, "
        "사막 피라미드, 해저 폐허에서 찾을 수 있어요."
    ],
}


KNOWN_BAD = (
    "신비한 라텍스",
    "신비로운 라텍스",
    "청각 재생",
    "룬문자 심판",
    "양자 포수",
    "퀀텀 캐처",
    "헤파이스토스 포지",
    "상위 버전",
    "E터널",
)


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


def replace_text(value: object, replacements: tuple[tuple[str, str], ...]) -> object:
    if isinstance(value, str):
        for old, new in replacements:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [replace_text(item, replacements) for item in value]
    return value


def preserve_images(english: object, korean: object) -> object:
    if isinstance(english, str):
        return english if english.startswith("{image:") else korean
    if isinstance(english, list) and isinstance(korean, list):
        return [
            preserve_images(source, target)
            for source, target in zip(english, korean, strict=True)
        ]
    return korean


def normalize_format_codes(english: object, korean: object) -> object:
    if isinstance(english, str) and isinstance(korean, str):
        source_codes = FORMAT_CODE.findall(english)
        target_codes = FORMAT_CODE.findall(korean)
        if len(source_codes) != len(target_codes):
            return korean
        code_iter = iter(source_codes)
        return FORMAT_CODE.sub(lambda _match: next(code_iter), korean)
    if isinstance(english, list) and isinstance(korean, list):
        return [
            normalize_format_codes(source, target)
            for source, target in zip(english, korean, strict=True)
        ]
    return korean


def translate_name(source: str) -> str:
    value = source
    for english, korean in sorted(NAME_PARTS.items(), key=lambda item: -len(item[0])):
        value = re.sub(rf"\b{re.escape(english)}\b", korean, value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def is_name_key(key: str, source: str) -> bool:
    if key in LANG_EXACT or any(mark in source for mark in ("%", ":", ".", "(")):
        return False
    return key.startswith(
        (
            "attribute.",
            "block.",
            "container.",
            "enchantment.",
            "entity.",
            "essence.",
            "item.",
            "modifier.",
            "upgrade.",
        )
    )


def normalize_language() -> dict[str, object]:
    english = load_json(LANG_ROOT / "en_us.json")
    candidates = load_json(LANG_ROOT / "auto_candidates.json")
    reviewed: dict[str, object] = {}
    for key, source in english.items():
        value = LANG_EXACT.get(key, candidates[key])
        if isinstance(source, str) and is_name_key(key, source):
            value = translate_name(source)
        reviewed[key] = value
    write_json(LANG_ROOT / "ko_kr.json", reviewed)
    report = {
        "namespace": "forbidden_arcanus",
        "reviewed_keys": len(reviewed),
        "status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "language_normalization.json", report)
    return report


def plain(value: str) -> str:
    return FORMAT_CODE.sub("", value).strip()


def item_names() -> dict[str, str]:
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    names: dict[str, str] = {}
    for key, source in english.items():
        target = korean[key]
        if (
            key.startswith(("item.", "block.", "entity."))
            and isinstance(source, str)
            and isinstance(target, str)
        ):
            names[source] = target
    return names


def normalize_quests() -> dict[str, object]:
    names = item_names()
    item_matches = 0
    rows = []
    for scope in QUEST_SCOPES:
        root = WORK_ROOT / "quests" / scope
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        candidates = load_json(root / "auto_candidates.json")
        sources = load_json(root / "candidate_sources.json")
        reviewed: dict[str, object] = {}
        for key, source in english.items():
            value = korean[key]
            if sources[key] == "new_translation_required":
                value = candidates[key]
            if key in NEW_QUEST_VALUES:
                value = NEW_QUEST_VALUES[key]
            value = replace_text(value, QUEST_REPLACEMENTS)
            value = preserve_images(source, value)
            value = normalize_format_codes(source, value)
            if key.endswith(".title") and isinstance(source, str):
                name = names.get(plain(source))
                if name is not None:
                    value = family_goal.apply_title_name(source, name)
                    item_matches += 1
            reviewed[key] = value
        write_json(root / "ko_kr.json", reviewed)
        rows.append({"scope": scope, "reviewed_keys": len(reviewed)})
    report = {
        "quests": rows,
        "new_values_manually_reviewed": len(NEW_QUEST_VALUES),
        "item_titles_matched_to_resourcepack": item_matches,
        "status": "all_current_quest_display_keys_reviewed",
    }
    write_json(WORK_ROOT / "quest_normalization.json", report)
    return report


def string_pairs(
    english: object, korean: object, path: str = ""
) -> list[tuple[str, str, str]]:
    if isinstance(english, str) and isinstance(korean, str):
        return [(path, english, korean)]
    if isinstance(english, list) and isinstance(korean, list):
        rows = []
        for index, (source, target) in enumerate(zip(english, korean, strict=True)):
            rows.extend(string_pairs(source, target, f"{path}[{index}]"))
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
            if PLACEHOLDER.findall(source) != PLACEHOLDER.findall(target):
                errors.append(f"자리표시자 불일치: {path}")
            if FORMAT_CODE.findall(source) != FORMAT_CODE.findall(target):
                errors.append(f"서식 코드 불일치: {path}")
            if source.startswith("{image:") and source != target:
                errors.append(f"이미지 태그 변경: {path}")
            if source == target and LATIN_WORD.search(source):
                untranslated.append(path)
            for fragment in KNOWN_BAD:
                if fragment in target:
                    errors.append(f"저품질 후보 흔적({fragment}): {path}")
    report = {
        "keys": len(english),
        "untranslated_candidates": untranslated,
        "errors": errors,
    }
    return report, errors


def verify(kind: str) -> tuple[dict[str, object], list[str]]:
    roots = (
        [LANG_ROOT]
        if kind == "language"
        else [WORK_ROOT / "quests" / scope for scope in QUEST_SCOPES]
    )
    rows = []
    errors = []
    for root in roots:
        report, current = verify_scope(root)
        report["scope"] = root.relative_to(WORK_ROOT).as_posix()
        rows.append(report)
        errors.extend(current)
    result = {
        "kind": kind,
        "scopes": rows,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / f"specialized_{kind}_validation.json", result)
    return result, errors


def audit() -> tuple[dict[str, object], list[str]]:
    instance = resolve_source_root()
    jar = next((instance / "mods").glob("forbidden_arcanus-*.jar"))
    inventory = family_goal.inventory(instance, FAMILY)
    references = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "forbidden_arcanus:" not in text and "Forbidden & Arcanus" not in text:
            continue
        relative = path.relative_to(instance).as_posix()
        references.append(relative)
    source_tooltips = instance / "kubejs/client_scripts/tooltips.js"
    override_tooltips = (
        PROJECT_ROOT / "output/overrides/kubejs/client_scripts/tooltips.js"
    )

    def relevant_lines(path: Path) -> list[tuple[int, str]]:
        rows = []
        active = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "allthemods.add(" in line:
                active = "forbidden_arcanus:" in line
            elif active and line.strip() == "])":
                active = False
            elif active and "Text.of" in line:
                rows.append((number, line))
        return rows

    source_display = relevant_lines(source_tooltips)
    override_display = relevant_lines(override_tooltips)
    english_fingerprint = re.compile(
        r"\b(?:the|with|from|on|use|found|right|left|top|bottom|spawns|"
        r"obtainable|unobtainable|dropped|only|will|most|rarely|feed|make|hold|kill)\b",
        re.I,
    )
    untranslated_override = [
        f"{override_tooltips.relative_to(PROJECT_ROOT).as_posix()}:{number}"
        for number, line in override_display
        if english_fingerprint.search(line)
    ]
    errors = [f"처리하지 않은 KubeJS 표시문: {line}" for line in untranslated_override]
    installed = inventory["installed"][0]
    report = {
        "main_jar": jar.name,
        "advancement_files": installed["advancements"],
        "advancement_display_uses_language_keys": True,
        "kubejs_reference_files": references,
        "kubejs_source_display_lines": len(source_display),
        "kubejs_override_display_lines": len(override_display),
        "kubejs_untranslated_override_lines": untranslated_override,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "normalize-language",
            "normalize-quests",
            "verify-language",
            "verify-quests",
            "audit",
        ),
    )
    args = parser.parse_args()
    if args.command == "normalize-language":
        result = normalize_language()
        errors = []
    elif args.command == "normalize-quests":
        result = normalize_quests()
        errors = []
    elif args.command == "verify-language":
        result, errors = verify("language")
    elif args.command == "verify-quests":
        result, errors = verify("quest")
    else:
        result, errors = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
