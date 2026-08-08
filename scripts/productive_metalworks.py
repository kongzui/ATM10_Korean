#!/usr/bin/env python3
"""Productive Metalworks 언어 작업본을 생성하고 전체 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

from five_family_goal import PROJECT_ROOT, load_json, validate_value
from local_paths import resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/productive_metalworks"
LANG_ROOT = WORK_ROOT / "productivemetalworks"
INTEGRATION_ROOT = WORK_ROOT / "integrations/dyenamicsandfriends"
DYENAMICS_OUTPUT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/dyenamicsandfriends/lang/ko_kr.json"
)

COLORS = {
    "black": "검은색",
    "blue": "파란색",
    "brown": "갈색",
    "cyan": "청록색",
    "gray": "회색",
    "green": "초록색",
    "light_blue": "하늘색",
    "light_gray": "회백색",
    "lime": "연두색",
    "magenta": "자홍색",
    "orange": "주황색",
    "pink": "분홍색",
    "purple": "보라색",
    "red": "빨간색",
    "white": "하얀색",
    "yellow": "노란색",
}

FOUNDRY_BLOCKS = {
    "fire_bricks": "내화 벽돌",
    "foundry_capacitor": "주조소 축전기",
    "foundry_controller": "주조소 제어기",
    "foundry_drain": "주조소 배출구",
    "foundry_tank": "주조소 탱크",
    "foundry_window": "주조소 창",
}

MATERIALS = {
    "aluminum": "알루미늄",
    "amethyst": "자수정",
    "ancient_debris": "고대 잔해",
    "blaze": "블레이즈",
    "brass": "황동",
    "bronze": "청동",
    "carbon": "탄소",
    "constantan": "콘스탄탄",
    "copper": "구리",
    "diamond": "다이아몬드",
    "electrum": "일렉트럼",
    "emerald": "에메랄드",
    "ender": "엔더",
    "enderium": "엔더리움",
    "glass": "유리",
    "glowstone": "발광석",
    "gold": "금",
    "heavy_core": "무거운 핵",
    "invar": "인바",
    "iridium": "이리듐",
    "iron": "철",
    "lapis": "청금석",
    "lead": "납",
    "lumium": "루미움",
    "magma_cream": "마그마 크림",
    "netherite": "네더라이트",
    "nickel": "니켈",
    "obsidian": "흑요석",
    "osmium": "오스뮴",
    "platinum": "백금",
    "quartz": "석영",
    "redstone": "레드스톤",
    "refined_glowstone": "정제된 발광석",
    "refined_obsidian": "정제된 흑요석",
    "shulker_shell": "셜커 껍데기",
    "signalum": "시그널륨",
    "silver": "은",
    "slime": "슬라임",
    "steel": "강철",
    "tin": "주석",
    "uranium": "우라늄",
    "wax": "밀랍",
    "zinc": "아연",
}

UNITS = {
    "ball": "구",
    "block": "블록",
    "chunk": "덩어리",
    "gem": "보석",
    "hunk": "큰 덩어리",
    "ingot": "주괴",
    "nugget": "조각",
    "pane": "판유리",
    "pearl": "진주",
    "pile": "더미",
    "rod": "막대기",
    "scrap": "파편",
    "shell": "껍데기",
}

DYENAMICS_COLORS = {
    "amber": "호박색",
    "aquamarine": "아쿠아마린",
    "bubblegum": "풍선껌색",
    "cherenkov": "체렌코프",
    "conifer": "침엽수색",
    "fluorescent": "형광색",
    "honey": "꿀색",
    "icy_blue": "얼음빛 파란색",
    "lavender": "라벤더색",
    "maroon": "적갈색",
    "mint": "민트색",
    "navy": "남색",
    "peach": "복숭아색",
    "persimmon": "감색",
    "rose": "장미색",
    "spring_green": "봄 초록색",
    "ultramarine": "울트라마린",
    "wine": "와인색",
}

EXACT = {
    "block.productivemetalworks.casting_basin": "주조 대야",
    "block.productivemetalworks.casting_table": "주조대",
    "block.productivemetalworks.fire_clay": "내화 점토",
    "block.productivemetalworks.foundry_tap": "주조소 꼭지",
    "block.productivemetalworks.high_powered_heating_coil": "고출력 가열 코일",
    "block.productivemetalworks.liquid_heating_coil": "액체 가열 코일",
    "block.productivemetalworks.meat": "고기",
    "block.productivemetalworks.meat_block": "고기 블록",
    "block.productivemetalworks.powered_heating_coil": "전동 가열 코일",
    "block.productivemetalworksfoundry_tank.fluid_tooltip": "%s mB의 %s가 들어 있음",
    "book.productivemetalworks.intro_category.text": "주조소 건설의 기초부터 시작합니다.",
    "book.productivemetalworks.intro_category.title": "소개",
    "book.productivemetalworks.intro_page.building": "주조소를 완성하려면 다음 블록이 필요합니다.$(br)* 주조소 제어기$(br)* 주조소 탱크$(br)* 액체 가열 코일$(br)* 내화 벽돌 또는 주조소 창$(br)* 주조소 배출구와 꼭지$(br)* 주조 대야와 주조대$(br2)주조소 내부는 1x1까지 작게 만들 수 있으며 직사각형이라면 어떤 모양도 가능합니다. 오른쪽에는 정사각형 3x3 구조의 예시가 있습니다.",
    "book.productivemetalworks.intro_page.casting": "녹인 재료를 쓸 수 있는 자원으로 만들려면 주형을 놓은 주조 대야나 주조대에서 주괴 또는 블록으로 주조해야 합니다.$(br2)꼭지에 레드스톤 펄스나 시계를 연결하거나 꼭지를 다른 유체 운송 파이프로 교체하면 주조소를 쉽게 자동화할 수 있습니다.",
    "book.productivemetalworks.intro_page.metalworks": "Productive Metalworks에 오신 것을 환영합니다. Tinkers' Construct의 제련소에서 영감을 얻은 모드로, 다른 점도 있지만 비슷한 점도 많습니다. 이 모드는 도구 제작 모드가 아니며 주조소만 추가한다는 점을 기억하세요.",
    "book.productivemetalworks.intro_page.multiblock": "3x3 주조소",
    "book.productivemetalworks.intro_page.obtaining": "주조소를 건설하려면 내화 점토를 구워 얻는 내화 벽돌이 필요합니다. 먼저 검은색 내화 벽돌을 만드세요. 검은색 블록이 기본형이며 염색해 다른 색으로 바꿀 수 있습니다.",
    "book.productivemetalworks.intro_page.sgearmetalworks": "Productive Metalworks에 오신 것을 환영합니다. Tinkers' Construct의 제련소에서 영감을 얻은 모드로, 다른 점도 있지만 비슷한 점도 많습니다. 이 모드는 도구나 무기를 추가하지 않지만 Silent Gear와 연동되어 장비 부품을 얻는 방식을 바꿉니다. 자세한 내용은 $(l:sgear)Silent Gear 항목$(/l)을 확인하세요.",
    "book.productivemetalworks.intro_page.structure": "주조소의 맨 아래층은 가열 코일로 만들어야 합니다. 가열 코일이 있어야 주조소를 실제로 가열할 수 있습니다. 주조소 멀티블록의 모서리는 비워도 됩니다.$(br)기본적으로 주조소는 원석을 2배 비율로 제련하며, 용해 속도는 사용한 연료에 따라 달라집니다. 모든 용해 조합법은 JEI에서 확인하세요.",
    "book.productivemetalworks.intro_page.title": "주조소",
    "book.productivemetalworks.landing_text": "금속 가공의 세계를 가볍게 살펴봅니다.$(br2)뜨거워질 테니 장갑을 착용하세요.",
    "book.productivemetalworks.name": "금속공학 대백과",
    "book.productivemetalworks.sgear_category.text": "주조소에서 Silent Gear 부품을 주조합니다.",
    "book.productivemetalworks.sgear_category.title": "Silent Gear 금속 가공",
    "book.productivemetalworks.sgear_page.casts": "주조가 필요한 장비 종류마다 전용 주형이 있으며, 팁과 도구 막대도 포함됩니다. 도구 막대 주형은 일반 막대기 주형과 다르니 주의하세요.",
    "book.productivemetalworks.sgear_page.grading": "이 모드는 Silent Gear의 다른 부분도 몇 가지 바꿉니다. 앞서 설명한 주조 외에도 도구의 등급을 매기거나 별빛을 충전하려면 개별 재료가 아니라 완성된 장비 부품에 작업해야 합니다. 장비 부품에 들어간 각 재료를 한 번에 하나씩 처리하므로 등급 부여와 별빛 충전을 여러 번 해야 합니다.",
    "book.productivemetalworks.sgear_page.parts": "용융 형태가 있는 재료를 사용하는 장비 부품은 주조소에서 만들어야 합니다. 곡괭이, 삽, 팁 등 장비 종류마다 주형이 필요합니다. 주형을 만들려면 돌, 나무, 부싯돌, 뼈처럼 단순한 재료로 장비 부품을 만든 다음 그 부품을 사용하세요.",
    "book.productivemetalworks.sgear_page.title": "장비 부품 주조",
    "config.jade.plugin_productivemetalworks.casting": "Productive Metalworks",
    "death.attack.productivemetalworks.foundry_damage": "%1$s이(가) 녹아 버렸습니다",
    "death.attack.productivemetalworks.foundry_damage.1": "%1$s이(가) 녹아 버렸습니다",
    "death.attack.productivemetalworks.foundry_damage.2": "%1$s이(가) 수상할 정도로 뜨거운 온천을 발견했습니다",
    "death.attack.productivemetalworks.foundry_damage.3": "%1$s이(가) 맛있는 용융 간식이 되었습니다",
    "death.attack.productivemetalworks.foundry_damage.4": "%1$s이(가) 너무 익어 버렸습니다",
    "death.attack.productivemetalworks.foundry_damage.5": "%1$s이(가) 너무 오래 구워졌습니다",
    "death.attack.productivemetalworks.foundry_damage.6": "%1$s이(가) 주조소에서 볶아졌습니다",
    "death.attack.productivemetalworks.foundry_damage.7": "%1$s, 구워진 채 편히 잠드세요",
    "death.attack.productivemetalworks.foundry_damage.8": '그레이비가 %1$s에게 뭐라고 했을까요? "넌 내 고기를 완성해"',
    "death.attack.productivemetalworks.foundry_damage.player.1": "%1$s이(가) %2$s와 숨바꼭구이를 하다가 녹아 버렸습니다",
    "death.attack.productivemetalworks.foundry_damage.player.2": "%1$s이(가) %2$s와 뛰놀다가 수상할 정도로 뜨거운 온천을 발견했습니다",
    "death.attack.productivemetalworks.foundry_damage.player.3": "%1$s이(가) %2$s와 소풍을 즐기다가 맛있는 용융 간식이 되었습니다",
    "death.attack.productivemetalworks.foundry_damage.player.4": "%1$s이(가) %2$s와 야영하다가 너무 익어 버렸습니다",
    "death.attack.productivemetalworks.foundry_damage.player.5": "%1$s이(가) %2$s에게 구워졌습니다",
    "death.attack.productivemetalworks.foundry_damage.player.6": "%2$s은(는) %1$s이(가) 주조소에서 볶아지는 모습을 지켜봤습니다",
    "death.attack.productivemetalworks.foundry_damage.player.7": "%2$s이(가) %1$s와의 앙금을 구워 없앴습니다",
    "death.attack.productivemetalworks.foundry_damage.player.8": "%2$s이(가) %1$s을(를) 절망의 그릴 구덩이로 보냈습니다",
    "fluid_type.productivemetalworks.meat": "고기",
    "gui.productivemetalworks.required_fuel": "필요한 연료: %s",
    "gui.productivemetalworks.temperature": "온도: %s C",
    "item.productivemetalworks.fire_brick": "내화 벽돌",
    "item.productivemetalworks.gear_cast": "기어 주형",
    "item.productivemetalworks.gem_cast": "보석 주형",
    "item.productivemetalworks.ingot_cast": "주괴 주형",
    "item.productivemetalworks.meat_bucket": "고기 양동이",
    "item.productivemetalworks.meat_ingot": "고기 주괴",
    "item.productivemetalworks.meat_nugget": "고기 조각",
    "item.productivemetalworks.nugget_cast": "조각 주형",
    "item.productivemetalworks.plate_cast": "판 주형",
    "item.productivemetalworks.rod_cast": "막대기 주형",
    "item.productivemetalworks.shiny_meat_ingot": "빛나는 고기 주괴",
    "itemGroup.productivemetalworks": "Productive Metalworks",
    "jade.productivemetalworks.cooling": "냉각 중",
    "jei.productivemetalworks.block_casting": "블록 주조",
    "jei.productivemetalworks.entity_melting": "개체 용해",
    "jei.productivemetalworks.fluid_alloying": "유체 합금화",
    "jei.productivemetalworks.item_casting": "아이템 주조",
    "jei.productivemetalworks.item_melting": "아이템 용해",
    "jei.productivemetalworks.sg_casting": "Silent Gear 주조",
    "jei.productivemetalworks.temperature": "온도: %s C",
    "productivemetalworks.devices.foundry_controller": "주조소",
    "productivemetalworks.information.upgrade.upgrade_stability.foundry_controller": "주조소의 유체 합금화를 비활성화합니다.",
    "productivemetalworks.information.upgrade.upgrade_time.foundry_controller": "용해 및 합금화 속도를 높입니다.\n   여러 업그레이드를 설치할 수 있습니다.",
    "productivemetalworks.information.upgrade.upgrade_time_2.foundry_controller": "다른 업그레이드보다 효과가 두 배 좋습니다.",
    "productivemetalworks.message.foundry_formed": "주조소 구조가 완성되었습니다",
    "productivemetalworks.message.foundry_invalid": "주조소 구조가 올바르지 않습니다. %s",
    "productivemetalworks.ponder.foundry_building.header": "주조소 건설",
    "productivemetalworks.ponder.foundry_building.text_1": "구조 안에 공기 블록이 하나 이상 있어야 하므로 주조소의 최소 크기는 3x3x2입니다. 모서리는 비워도 됩니다.",
    "productivemetalworks.ponder.foundry_building.text_2": "주조소 바닥은 가열 코일로 만들어야 합니다.",
    "productivemetalworks.ponder.foundry_building.text_3": "또한 주조소에는 주조소 제어기가 있어야 하고...",
    "productivemetalworks.ponder.foundry_building.text_4": "...주조소 탱크도 있어야 하며...",
    "productivemetalworks.ponder.foundry_building.text_5": "...주조소 배출구가 하나 이상 필요합니다.",
    "productivemetalworks.ponder.foundry_casting.header": "주조소에서 아이템 주조",
    "productivemetalworks.ponder.foundry_casting.text_1": "유체를 블록으로 만들려면 주조 대야를 사용해야 합니다.",
    "productivemetalworks.ponder.foundry_casting.text_2": "배출구에 연결된 주조소 꼭지를 우클릭하면 유체가 나옵니다.",
    "productivemetalworks.ponder.foundry_casting.text_3": "주조 대야가 유체를 천천히 식혀 블록으로 만듭니다.",
    "productivemetalworks.ponder.foundry_casting.text_4": "대야를 우클릭해 아이템을 꺼내세요. 파이프나 호퍼를 사용해도 됩니다.",
    "productivemetalworks.ponder.foundry_casting.text_5": "주조대를 사용하면 유체를 여러 주형에 부을 수도 있습니다.",
    "productivemetalworks.ponder.foundry_casting.text_6": "주형을 손에 들고 우클릭해 추가하세요.",
    "productivemetalworks.ponder.foundry_casting.text_7": "주조대나 주조 대야에 놓은 아이템 위로 액체를 부으면 새로운 아이템을 만들 수도 있습니다.",
    "productivemetalworks.ponder.foundry_fueling.header": "주조소에 연료 공급",
    "productivemetalworks.ponder.foundry_fueling.text_1": "주조소가 작동하려면 주조소 탱크 안에 연료가 있어야 합니다.",
    "productivemetalworks.ponder.foundry_fueling.text_2": "양동이로 탱크를 우클릭하거나 파이프로 연료를 공급할 수 있습니다.",
    "productivemetalworks.ponder.foundry_fueling.text_3": "액체 가열 코일을 전동 가열 코일로 바꾸면 액체 연료 대신 에너지를 사용할 수 있습니다...",
    "productivemetalworks.ponder.foundry_fueling.text_4": "...고출력 가열 코일을 사용하면 더 많은 열을 만들 수 있습니다.",
    "productivemetalworks.ponder.foundry_fueling.text_5": "전동 가열 코일을 사용하려면 주조소 탱크를 주조소 축전기로 교체해야 합니다.",
    "productivemetalworks.ponder.foundry_fueling.text_6": "축전기에 연결한 케이블로 에너지를 공급할 수 있습니다.",
    "productivemetalworks.ponder.foundry_smelting.header": "주조소에서 아이템 용해",
    "productivemetalworks.ponder.foundry_smelting.text_1": "제어기 GUI를 통해 주조소에 아이템을 넣거나...",
    "productivemetalworks.ponder.foundry_smelting.text_2": "...주조소 안으로 직접 떨어뜨릴 수 있습니다.",
    "productivemetalworks.ponder.foundry_smelting.text_3": "시간이 지나면 주조소 안의 아이템이 액체로 변합니다.",
    "productivemetalworks.ponder.foundry_smelting.text_4": "두 번째 액체를 추가하면 일부는 합금 반응을 일으킬 수 있습니다. 안정성 업그레이드를 추가하면 이를 막을 수 있습니다.",
    "productivemetalworks.ponder.foundry_smelting.text_5": "도움말: 양동이로 배출구를 우클릭하면 유체를 직접 넣을 수 있습니다.",
    "productivemetalworks.ponder.foundry_smelting.text_6": "예를 들어 철 2/3와 니켈 1/3을 섞으면 인바가 됩니다.",
    "productivemetalworks.ponder.tag.foundry_building_blocks": "주조소 건설 블록",
    "productivemetalworks.ponder.tag.foundry_building_blocks.description": "주조소 건설에 사용하는 기본 블록",
    "productivemetalworks.ponder.tag.foundry_casting_blocks": "주조소 주조 블록",
    "productivemetalworks.ponder.tag.foundry_casting_blocks.description": "주조 과정에 사용하는 블록",
    "productivemetalworks.ponder.tag.foundry_controller_blocks": "주조소 제어기",
    "productivemetalworks.ponder.tag.foundry_controller_blocks.description": "주조소의 제어기 블록",
    "productivemetalworks.ponder.tag.foundry_tank_blocks": "주조소 탱크 블록",
    "productivemetalworks.ponder.tag.foundry_tank_blocks.description": "주조소 연료를 저장하는 블록",
}

QUEST_REPLACEMENTS = {
    "quest.036D5767E07005BC.quest_desc": (
        ("&7탭&r", "&7꼭지&r"),
        ("탭을", "꼭지를"),
        ("&7꼭지&r을", "&7꼭지&r를"),
    ),
    "quest.26F9DB31A835B69C.quest_desc": (
        ("&7탭&r", "&7꼭지&r"),
        ("&7꼭지&r과", "&7꼭지&r와"),
        ("&7꼭지&r을", "&7꼭지&r를"),
    ),
}


def dump_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 안정된 형식으로 기록한다."""
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def translate(key: str, source: str) -> str:
    """키 구조와 검수된 용어를 이용해 한 언어 값을 번역한다."""
    if key in EXACT:
        return EXACT[key]
    colored = re.fullmatch(
        r"block\.productivemetalworks\.([a-z_]+)_(fire_bricks|foundry_capacitor|"
        r"foundry_controller|foundry_drain|foundry_tank|foundry_window)",
        key,
    )
    if colored:
        color, block = colored.groups()
        return f"{COLORS[color]} {FOUNDRY_BLOCKS[block]}"
    molten = re.fullmatch(
        r"(?:block|fluid_type)\.productivemetalworks\.molten_(.+)", key
    )
    if molten:
        return f"용융 {MATERIALS[molten.group(1)]}"
    bucket = re.fullmatch(r"item\.productivemetalworks\.molten_(.+)_bucket", key)
    if bucket:
        return f"용융 {MATERIALS[bucket.group(1)]} 양동이"
    if key.startswith("productivebees.ingredient.description."):
        return "이 벌을 얻으려면 생성 알의 조합법을 확인하세요."
    unit = re.fullmatch(
        r"productivemetalworks\.unit\.([a-z_]+)\.(?:single|multiple)", key
    )
    if unit:
        return f"%s {UNITS[unit.group(1)]}"
    if key == "productivemetalworks.unit.leftover":
        return "%s mB"
    raise KeyError(f"검수되지 않은 언어 키: {key}={source}")


def normalize() -> dict[str, int]:
    """영어 376키와 관련 퀘스트를 검수한 한국어로 재생성한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    changed = 0
    for key, source in english.items():
        if not isinstance(source, str):
            raise TypeError(f"문자열이 아닌 언어 값: {key}")
        translated = translate(key, source)
        errors = validate_value(key, source, translated)
        if errors:
            raise ValueError("; ".join(errors))
        if korean[key] != translated:
            korean[key] = translated
            changed += 1
    dump_json(LANG_ROOT / "ko_kr.json", korean)

    quest_root = WORK_ROOT / "quests/related"
    quests = load_json(quest_root / "ko_kr.json")
    quest_changed = 0
    for key, replacements in QUEST_REPLACEMENTS.items():
        values = quests[key] if isinstance(quests[key], list) else [quests[key]]
        translated_values = []
        for value in values:
            for old, new in replacements:
                value = value.replace(old, new)
            translated_values.append(value)
        translated = (
            translated_values if isinstance(quests[key], list) else translated_values[0]
        )
        if translated != quests[key]:
            quests[key] = translated
            quest_changed += 1
    dump_json(quest_root / "ko_kr.json", quests)
    integration = normalize_dyenamics()
    return {
        "language_keys": len(english),
        "language_changed": changed,
        "quest_keys": len(quests),
        "quest_changed": quest_changed,
        **integration,
    }


def normalize_dyenamics() -> dict[str, int]:
    """Dyenamics and Friends의 Productive Metalworks 연동 109키를 번역한다."""
    instance = resolve_source_root()
    jar = next((instance / "mods").glob("dyenamicsandfriends-*.jar"))
    with ZipFile(jar) as archive:
        full_english = json.loads(
            archive.read("assets/dyenamicsandfriends/lang/en_us.json").decode("utf-8")
        )
    english = {
        key: value
        for key, value in full_english.items()
        if key.startswith("block.dyenamicsandfriends.productivemetalworks_")
        or key == "resourcePack.dyenamicsandfriends.productivemetalworks"
    }
    korean = {}
    for key, source in english.items():
        if key == "resourcePack.dyenamicsandfriends.productivemetalworks":
            translated = "Dyenamics And Friends - Productive Metalworks"
        else:
            match = re.fullmatch(
                r"block\.dyenamicsandfriends\.productivemetalworks_([a-z_]+)_"
                r"(fire_bricks|foundry_capacitor|foundry_controller|foundry_drain|"
                r"foundry_tank|foundry_window)",
                key,
            )
            if not match:
                raise KeyError(f"검수되지 않은 Dyenamics 연동 키: {key}")
            color, block = match.groups()
            korean[key] = f"{DYENAMICS_COLORS[color]} {FOUNDRY_BLOCKS[block]}"
            continue
        korean[key] = translated
    INTEGRATION_ROOT.mkdir(parents=True, exist_ok=True)
    dump_json(INTEGRATION_ROOT / "en_us.json", english)
    dump_json(INTEGRATION_ROOT / "ko_kr.json", korean)
    dump_json(
        INTEGRATION_ROOT / "candidate_sources.json",
        {key: "new_translation_required" for key in english},
    )
    return {"dyenamics_integration_keys": len(english)}


def build_integration() -> dict[str, int]:
    """연동 키를 기존 Dyenamics 누적 출력에 보존 병합한다."""
    existing = load_json(DYENAMICS_OUTPUT) if DYENAMICS_OUTPUT.is_file() else {}
    integration = load_json(INTEGRATION_ROOT / "ko_kr.json")
    preserved = len(set(existing) - set(integration))
    merged = {**existing, **integration}
    DYENAMICS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    dump_json(DYENAMICS_OUTPUT, merged)
    return {
        "integration_keys": len(integration),
        "preserved_existing_keys": preserved,
        "output_keys": len(merged),
    }


def audit_jar() -> tuple[dict[str, object], list[str]]:
    """안내서·발전 과제·조합법의 표시 문구 경로를 검사한다."""
    instance = resolve_source_root()
    jar = next((instance / "mods").glob("productivemetalworks-*.jar"))
    errors = []
    guide_files = []
    guide_translation_keys = []
    advancements_checked = 0
    advancement_displays = []
    recipes_checked = 0
    recipe_visible_fields = []
    with ZipFile(jar) as archive:
        for name in archive.namelist():
            if not name.endswith(".json"):
                continue
            if "patchouli_books/guide/en_us/" in name:
                guide_files.append(name)
                data = json.loads(archive.read(name).decode("utf-8"))
                for value in flatten_strings(data):
                    if value.startswith("book.productivemetalworks."):
                        guide_translation_keys.append(value)
            elif "data/productivemetalworks/advancement/" in name:
                advancements_checked += 1
                data = json.loads(archive.read(name).decode("utf-8"))
                if isinstance(data, dict) and "display" in data:
                    advancement_displays.append(name)
            elif "data/productivemetalworks/recipe/" in name:
                recipes_checked += 1
                data = json.loads(archive.read(name).decode("utf-8"))
                visible = named_strings(data, {"name", "title", "description", "text"})
                if visible:
                    recipe_visible_fields.append(name)
        book_data = json.loads(
            archive.read("data/productivemetalworks/patchouli_books/guide/book.json")
        )
        guide_translation_keys.extend(
            value
            for value in flatten_strings(book_data)
            if value.startswith("book.productivemetalworks.")
        )
    english = load_json(LANG_ROOT / "en_us.json")
    missing_guide_keys = sorted(set(guide_translation_keys) - set(english))
    if missing_guide_keys:
        errors.append(f"언어 파일에 없는 안내서 키: {missing_guide_keys}")
    if advancement_displays:
        errors.append("표시 정보가 있는 발전 과제가 남음")
    if recipe_visible_fields:
        errors.append("표시 문구가 있는 조합법이 남음")

    kubejs_reference_files = []
    kubejs_visible_fields = []
    for path in (instance / "kubejs").rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json", ".snbt"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if not re.search(r"productive\s*metalworks|productivemetalworks", text, re.I):
            continue
        relative = path.relative_to(instance / "kubejs").as_posix()
        kubejs_reference_files.append(relative)
        if path.suffix.lower() == ".json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                continue
            if named_strings(data, {"name", "title", "description", "text"}):
                kubejs_visible_fields.append(relative)
    if kubejs_visible_fields:
        errors.append(f"KubeJS 표시 필드 발견: {kubejs_visible_fields[:20]}")

    sgear_work = PROJECT_ROOT / "working/silentgear/sgearmetalworks/ko_kr.json"
    sgear_output = (
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/sgearmetalworks/lang/ko_kr.json"
    )
    sgear_keys = len(load_json(sgear_work)) if sgear_work.is_file() else 0
    sgear_output_matches = (
        sgear_work.is_file()
        and sgear_output.is_file()
        and load_json(sgear_work) == load_json(sgear_output)
    )
    if sgear_keys != 132 or not sgear_output_matches:
        errors.append("기존 Silent Gear Metalworks 연동 산출물 불일치")
    report = {
        "jar": jar.name,
        "guide_files_checked": len(guide_files) + 1,
        "guide_translation_keys": len(set(guide_translation_keys)),
        "missing_guide_keys": missing_guide_keys,
        "advancements_checked": advancements_checked,
        "advancement_display_entries": len(advancement_displays),
        "recipes_checked": recipes_checked,
        "recipe_visible_field_entries": len(recipe_visible_fields),
        "kubejs_reference_files_checked": len(kubejs_reference_files),
        "kubejs_visible_field_entries": len(kubejs_visible_fields),
        "existing_sgearmetalworks_keys": sgear_keys,
        "existing_sgearmetalworks_output_matches": sgear_output_matches,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    dump_json(WORK_ROOT / "data_audit.json", report)
    return report, errors


def flatten_strings(value: object) -> list[str]:
    """중첩 JSON의 모든 문자열을 평탄화한다."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [item for child in value.values() for item in flatten_strings(child)]
    if isinstance(value, list):
        return [item for child in value for item in flatten_strings(child)]
    return []


def named_strings(value: object, names: set[str]) -> list[str]:
    """중첩 JSON에서 지정한 필드의 문자열을 모은다."""
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in names and isinstance(child, str):
                found.append(child)
            found.extend(named_strings(child, names))
    elif isinstance(value, list):
        for child in value:
            found.extend(named_strings(child, names))
    return found


def verify() -> tuple[dict[str, object], list[str]]:
    """언어·퀘스트·안내서 구조와 미번역을 검사한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    errors = []
    if list(english) != list(korean):
        errors.append("언어 키 또는 순서 불일치")
    for key, source in english.items():
        target = korean[key]
        errors.extend(validate_value(key, source, target))
        if source == target and source != "Productive Metalworks":
            errors.append(f"미번역: {key}")
        if key.startswith("book."):
            source_tokens = re.findall(r"\$\([^)]+\)", source)
            target_tokens = re.findall(r"\$\([^)]+\)", target)
            if source_tokens != target_tokens:
                errors.append(f"Patchouli 토큰 불일치: {key}")

    quest_root = WORK_ROOT / "quests/related"
    quest_english = load_json(quest_root / "en_us.json")
    quest_korean = load_json(quest_root / "ko_kr.json")
    if list(quest_english) != list(quest_korean):
        errors.append("퀘스트 키 또는 순서 불일치")
    for key, source in quest_english.items():
        target = quest_korean[key]
        errors.extend(validate_value(key, source, target))
        if source == target:
            errors.append(f"미번역 퀘스트: {key}")

    integration_english = load_json(INTEGRATION_ROOT / "en_us.json")
    integration_korean = load_json(INTEGRATION_ROOT / "ko_kr.json")
    if list(integration_english) != list(integration_korean):
        errors.append("Dyenamics 연동 키 또는 순서 불일치")
    output = load_json(DYENAMICS_OUTPUT) if DYENAMICS_OUTPUT.is_file() else {}
    for key, source in integration_english.items():
        target = integration_korean[key]
        errors.extend(validate_value(key, source, target))
        if (
            source == target
            and key != "resourcePack.dyenamicsandfriends.productivemetalworks"
        ):
            errors.append(f"미번역 Dyenamics 연동: {key}")
        if output.get(key) != target:
            errors.append(f"Dyenamics 누적 출력 불일치: {key}")
    data_report, data_errors = audit_jar()
    errors.extend(data_errors)
    report = {
        "language_keys": len(english),
        "quest_keys": len(quest_english),
        "dyenamics_integration_keys": len(integration_english),
        "data_audit": data_report,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    dump_json(WORK_ROOT / "specialized_validation.json", report)
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("normalize", "build-integration", "verify"))
    args = parser.parse_args()
    if args.command == "normalize":
        report = normalize()
        errors = []
    elif args.command == "build-integration":
        report = build_integration()
        errors = []
    else:
        report, errors = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
