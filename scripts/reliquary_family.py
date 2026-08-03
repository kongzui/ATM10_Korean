#!/usr/bin/env python3
"""Reliquary 언어 파일과 관련 표시 경로를 현재 영어 원문으로 전면 재검수해요."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "reliquary"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
LANG_ROOT = WORK_ROOT / "reliquary"
QUEST_ROOT = WORK_ROOT / "quests/related"
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
NUMBER = re.compile(r"\d+(?:[.,/xX×]\d+)*")

EXACT_BY_KEY = {
    "itemGroup.reliquary": "Reliquary",
    "block.reliquary.alkahestry_altar": "빛의 제단",
    "block.reliquary.alkahestry_altar.tooltip": "레드스톤을 공급하면 발광석이 자랍니다.",
    "block.reliquary.apothecary_cauldron": "약제사의 가마솥",
    "block.reliquary.apothecary_cauldron.tooltip": "물약 정수로 물약을 제조합니다.",
    "block.reliquary.apothecary_mortar": "약제사의 절구",
    "block.reliquary.apothecary_mortar.tooltip": "재료를 갈아 물약 정수로 만듭니다.",
    "block.reliquary.fertile_lily_pad": "비옥의 수련잎",
    "block.reliquary.interdiction_torch": "차단의 횃불",
    "item.reliquary.alkahestry_tome": "알카헤스트리의 고서",
    "item.reliquary.angelheart_vial": "천사의 심장 약병",
    "item.reliquary.barrel_assembly": "총신 조립부",
    "item.reliquary.bullets.neutral_bullet": "일반 탄환",
    "item.reliquary.bullets.exorcism_bullet": "퇴마 탄환",
    "item.reliquary.bullets.blaze_bullet": "블레이즈 탄환",
    "item.reliquary.bullets.ender_bullet": "엔더 탄환",
    "item.reliquary.bullets.concussive_bullet": "충격 탄환",
    "item.reliquary.bullets.buster_bullet": "파괴 탄환",
    "item.reliquary.bullets.seeker_bullet": "추적 탄환",
    "item.reliquary.bullets.sand_bullet": "모래 탄환",
    "item.reliquary.bullets.storm_bullet": "폭풍 탄환",
    "item.reliquary.chelicerae": "거미 협각",
    "item.reliquary.infernal_claw": "지옥의 발톱 조각",
    "item.reliquary.molten_core": "용융 핵",
    "item.reliquary.glowing_water": "성수",
    "item.reliquary.glowing_bread": "성스러운 빵",
    "item.reliquary.ender_staff": "엔더 지팡이",
    "item.reliquary.glacial_staff": "빙하 지팡이",
    "item.reliquary.harvest_rod": "수확의 지팡이",
    "item.reliquary.ice_magus_rod": "빙결 마도사의 지팡이",
    "item.reliquary.infernal_chalice": "지옥의 성배",
    "item.reliquary.lantern_of_paranoia": "불안의 등불",
    "item.reliquary.magicbane": "매직베인",
    "item.reliquary.magazines.empty_magazine": "빈 탄창",
    "item.reliquary.magazines.neutral_magazine": "일반 탄창",
    "item.reliquary.magazines.exorcism_magazine": "퇴마 탄창",
    "item.reliquary.magazines.blaze_magazine": "블레이즈 탄창",
    "item.reliquary.magazines.ender_magazine": "엔더 탄창",
    "item.reliquary.magazines.concussive_magazine": "충격 탄창",
    "item.reliquary.magazines.buster_magazine": "파괴 탄창",
    "item.reliquary.magazines.seeker_magazine": "추적 탄창",
    "item.reliquary.magazines.sand_magazine": "모래 탄창",
    "item.reliquary.magazines.storm_magazine": "폭풍 탄창",
    "item.reliquary.midas_touchstone": "미다스의 시금석",
    "item.reliquary.empty_potion_vial": "농축 물약 약병",
    "item.reliquary.potion": "농축 물약",
    "item.reliquary.splash_potion": "투척용 농축 물약",
    "item.reliquary.lingering_potion": "잔류형 농축 물약",
    "item.reliquary.potion_essence": "물약 정수",
    "item.reliquary.rending_gale": "찢어발기는 돌풍",
    "item.reliquary.rod_of_lyssa": "리사의 지팡이",
    "item.reliquary.salamander_eye": "살라맨더의 눈",
    "item.reliquary.mob_charm": "%s 부적",
    "item.reliquary.mob_charm_fragment": "%s 부적 조각",
    "item.reliquary.mob_charm_belt": "부적 허리띠",
    "item.reliquary.tipped_arrow": "물약 묻은 화살",
    "item.reliquary.witherless_rose": "시들지 않는 장미",
    "item.reliquary.xp_bucket": "경험치 양동이",
    "item.reliquary.ender_staff.tooltip.position": "현재 좌표 %s, %s, %s에 연결됨(차원: %s)",
    "item.reliquary.emperor_chalice.tooltip2": (
        "활성화하면 물을 흡수합니다.\n비활성화하면 물을 놓습니다.\n"
        "마시면 생명력을 대가로 허기를 회복합니다."
    ),
    "item.reliquary.pyromancer_staff.tooltip.charges": "충전 횟수: %s",
    "item.reliquary.mob_charm.tooltip": "이 부적을 지니면 %s이(가) 플레이어를 감지하지 못합니다.",
    "item.reliquary.mob_charm_belt.tooltip": "모든 몹 부적을 보관합니다.",
    "gui.reliquary.alkahestry_tome.text": (
        "고서와 특정 아이템 또는 블록을 함께 제작해 복제할 수 있습니다.\n"
        "빛의 제단을 우클릭하면 고서에 든 레드스톤을 공급합니다."
    ),
    "keybind.reliquary.category": "Reliquary",
    "reliquary.configuration.potionMap.tooltip": (
        "어떤 재료가 어떤 물약 효과를 부여하는지 설정합니다.\n"
        "형식: item_id=effect|duration|amplifier;effect|duration|amplifier\n"
        "예: minecraft:sugar=speed|3|0;haste|3|0\n"
        "지속 시간은 15초 단위입니다."
    ),
    "jei.reliquary.recipe.alkahest_crafting": "알카헤스트리의 고서 제작",
    "jei.reliquary.recipe.alkahest_charging": "알카헤스트리의 고서 충전",
    "jei.reliquary.recipe.mortar": "약제사의 절구",
    "jei.reliquary.recipe.cauldron": "약제사의 가마솥",
    "jei.reliquary.description.ammo_potion": "\n명중한 대상에게 물약 효과를 부여합니다.",
    "jei.reliquary.description.apothecary_cauldron": (
        "이 가마솥에서 물약 정수와 네더 사마귀를 섞어 물약을 만듭니다. 시작하려면 "
        "가마솥 아래에 불을 피우고 안에 물을 채워야 하며, 완성된 물약은 빈 물약 약병에 담습니다."
    ),
    "jei.reliquary.description.destruction_catalyst": (
        "화약을 소모해 '일반' 블록만 파괴하고 다른 블록은 그대로 둡니다. "
        "이 방식으로 파괴한 블록에서는 아이템이 나오지 않습니다."
    ),
    "jei.reliquary.description.emperor_chalice": (
        "사실상 무한 물 양동이입니다. 물 양동이를 쓸 때처럼 블록을 직접 조준하지 않으면 "
        "성배의 물을 마시며, 생명력을 대가로 허기를 회복합니다."
    ),
    "jei.reliquary.description.fortune_coin": (
        "약 5블록 반경의 아이템과 경험치 구슬을 플레이어에게 순간이동시킵니다. "
        "Shift+우클릭으로 켜거나 끕니다.\n\n손에 든 채 우클릭을 누르면 범위가 약 15블록으로 "
        "세 배가 되어 빠르게 수집할 수 있습니다."
    ),
    "jei.reliquary.description.glacial_staff": (
        "빙하 지팡이는 빙결 마도사의 지팡이를 업그레이드한 도구입니다. 눈덩이를 발사하고, "
        "물을 꽁꽁 언 얼음으로, 용암을 흑요석으로 바꿉니다. 이렇게 생긴 블록은 지팡이를 든 "
        "플레이어의 범위에서 벗어나면 녹습니다."
    ),
    "jei.reliquary.description.ender_staff": (
        "Shift+우클릭하면 인벤토리의 엔더 진주를 흡수해 충전하고, 이 충전을 소모해 순간이동합니다. "
        "Shift+스크롤로 세 가지 모드를 바꿀 수 있습니다.  \n엔더 진주 모드에서는 우클릭으로 일반 엔더 "
        "진주를 던집니다. 일반 진주와 달리 플레이어가 피해를 받지 않고 블록에 끼일 가능성도 낮습니다. \n"
        "엔더의 눈 모드에서는 엔더 진주가 중력의 영향을 덜 받아 더 멀리 날아갑니다. \n망령 노드 모드에서는 "
        "우클릭을 누르면 엔더 지팡이에 연결된 망령 노드로 순간이동합니다. 망령 노드에 엔더 지팡이를 "
        "우클릭해 목적지를 연결할 수 있습니다."
    ),
    "jei.reliquary.description.harvest_rod": (
        "수확의 지팡이는 농사를 돕는 도구입니다. 뼛가루와 심을 수 있는 씨앗·작물을 보관하며, "
        "내구도가 무한인 괭이 모드도 제공합니다. Shift+스크롤로 모드를 바꿀 수 있습니다.\n"
        "조준한 블록 하나에 사용하거나 우클릭을 누른 채 효과 범위(기본 반경 3) 전체에 사용할 수 있습니다.\n"
        "활성화하면 플레이어 인벤토리의 뼛가루와 심을 수 있는 아이템을 흡수합니다."
    ),
    "jei.reliquary.description.mob_charm_fragment": "%s 부적 조각은 %s 부적의 제작 재료입니다.",
    "jei.reliquary.description.mob_charm_belt": (
        "몹 부적을 보관하며, 안에 넣은 부적도 그대로 작동합니다. 허리띠를 우클릭해 여는 화면에서 "
        "부적을 넣을 수 있고, 장신구 허리띠 슬롯에 착용할 수 있습니다."
    ),
    "jei.reliquary.description.mob_charm": "플레이어가 공격해도 %s이(가) 플레이어를 무시합니다.",
    "jei.reliquary.description.infernal_tear": (
        "Shift+우클릭하면 보유량이 가장 많으면서 지옥의 눈물 허용 목록에 있는 아이템을 흡수해 "
        "경험치로 바꿉니다."
    ),
    "jei.reliquary.description.lantern_of_paranoia": (
        "여행자의 지팡이와 짝을 이루는 도구로, 위험할 만큼 어두운 곳에 횃불을 자동으로 놓습니다. "
        "횃불은 여행자의 지팡이나 플레이어 인벤토리에서 가져옵니다."
    ),
    "jei.reliquary.description.magicbane": (
        "매직베인은 NetHack의 유물 단검에 경의를 표해 만든 무기입니다.\n\n"
        "내구도가 16이라 매우 쉽게 부서집니다. 공격할 때 50%% 확률로 혼란, 실명, 둔화, 나약함 중 "
        "하나를 부여합니다.\n\n검에 부여된 각 마법의 레벨이 총 피해에 더해집니다. 예를 들어 발화 II를 "
        "부여한 매직베인은 기본 피해에 2의 피해를 더 줍니다.\n\n금으로 만든 무기이므로 미다스의 시금석으로 "
        "수리할 수 있고, 금 장비와 같은 마법 부여 특성을 가집니다."
    ),
    "jei.reliquary.description.potion_essence": (
        "여러 종류의 물약 정수입니다. 약제사의 절구에서 재료 두세 가지를 조합해 만들며, 그중 하나로 "
        "다른 물약 정수를 사용할 수도 있습니다.\n\nJEI에 보이는 물약 정수는 가능한 모든 조합의 일부일 뿐입니다. "
        "JEI에는 효과가 1개인 정수만 나오지만, 정수 하나에 여러 효과를 담을 수 있습니다.\n\n"
        "설정 화면에서 사용할 수 있는 재료와 각각의 보조 효과를 확인할 수 있습니다. 두 가지 이상의 재료에서 "
        "같은 보조 효과를 얻으면 활성 효과가 되어 절구에서 만든 물약 정수에 들어갑니다."
    ),
    "jei.reliquary.description.rending_gale": (
        "가고 싶은 방향을 조준해 비행할 수 있습니다. 가벼운 착지 효과는 없지만, 땅을 향해 조준한 채 "
        "버튼을 누르면 낙하 피해를 막을 수 있습니다.\n\n개체를 밀거나 당기고, 뇌우가 칠 때 조준한 곳에 "
        "번개를 내리칠 수도 있습니다. Shift+스크롤로 모드를 바꿉니다.\n\n깃털을 흡수시켜 비행과 번개에 "
        "사용할 충전을 채웁니다."
    ),
    "jei.reliquary.description.rod_of_lyssa": (
        "강화된 낚싯대입니다. 개체를 훨씬 높이 끌어올리고 아이템도 당깁니다. "
        "웅크린 채 사용하면 개체의 소지품을 훔칠 수 있습니다."
    ),
    "jei.reliquary.description.sojourner_staff": (
        "횃불을 최대 1500개 흡수합니다.\n\n최대 30블록 떨어진 곳에 횃불이나 블록을 놓을 수 있지만, "
        "거리가 6블록 늘 때마다 설치 비용이 하나씩 증가합니다. 따라서 30블록 거리에 횃불 하나를 놓으면 "
        "횃불 6개를 소모합니다.\n\n불안의 등불과 함께 가지고 있으면 불안의 등불이 여행자의 지팡이에 "
        "저장된 횃불부터 사용합니다."
    ),
    "jei.reliquary.description.twilight_cloak": (
        "빛이 어두울 때 망토를 인벤토리에 지닌 플레이어가 투명해집니다. 투명한 동안에는 플레이어가 "
        "공격해도 몹이 플레이어를 대상으로 삼지 못합니다.\n\nShift+우클릭으로 활성화해야 합니다."
    ),
    "jei.reliquary.description.tipped_arrow": (
        "Reliquary의 잔류형 물약으로 만드는 물약 묻은 화살입니다. 바닐라보다 훨씬 다양한 물약 효과 "
        "조합을 사용할 수 있습니다."
    ),
}

REPLACEMENTS = (
    ("연금술사의 서적", "알카헤스트리의 고서"),
    ("연금술사의 가마솥", "약제사의 가마솥"),
    ("연금술사의 절구", "약제사의 절구"),
    ("약제의 가마솥", "약제사의 가마솥"),
    ("약제의 절구", "약제사의 절구"),
    ("포션", "물약"),
    ("글로우스톤", "발광석"),
    ("레시피", "제작법"),
    ("드랍", "드롭"),
    ("스태프", "지팡이"),
    ("엔티티", "개체"),
    ("엔터티", "개체"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("왼쪽 클릭", "좌클릭"),
    ("쿨타임", "재사용 대기시간"),
    ("기아", "허기"),
    ("골드 아이템", "금 아이템"),
    ("레드스톤 더스트", "레드스톤 가루"),
    ("플린트와 강철", "부싯돌과 부시"),
    ("조리법", "제작법"),
    ("몹의 매력", "몹 부적"),
    ("매력 벨트", "부적 허리띠"),
    ("매력의 조각", "부적 조각"),
    ("성물 물약", "Reliquary 물약"),
    ("성물 아이템", "Reliquary 아이템"),
    ("성물 드롭", "Reliquary 전리품"),
    ("릴리패드", "수련잎"),
    ("버프", "강화 효과"),
    ("디버프", "약화 효과"),
    ("PVP", "PvP"),
    ("xp", "경험치"),
)

CONFIG_EXACT = {
    "Sneak for Extra Details": "웅크리면 자세한 정보 표시",
    "Sojourner's Staff": "여행자의 지팡이",
    "Alkahestry Tome": "알카헤스트리의 고서",
    "Destruction Catalyst": "파괴 촉매",
    "Ender Staff": "엔더 지팡이",
    "Ice Magus Rod": "빙결 마도사의 지팡이",
    "Glacial Staff": "빙하 지팡이",
    "Midas Touchstone": "미다스의 시금석",
    "Harvest Rod": "수확의 지팡이",
    "Infernal Chalice": "지옥의 성배",
    "Mob Charm": "몹 부적",
    "Charm Fragments": "부적 조각",
    "Lilypad of Fertility": "비옥의 수련잎",
    "Interdiction Torch": "차단의 횃불",
    "Max JEI/Creative Effects": "JEI/크리에이티브 최대 효과 수",
    "Show 3-Ingredient in JEI": "JEI에 3재료 조합 표시",
    "Items": "아이템",
    "Hunger Cost (%)": "허기 비용(%)",
    "Heal % of Max Health": "최대 체력 대비 회복량(%)",
    "Ender Pearl Worth": "엔더 진주 충전 가치",
    "Lucky Harvest Chance": "행운 수확 확률",
    "Lucky Harvest Rolls": "행운 수확 굴림 횟수",
    "Area Cooldown": "범위 효과 재사용 대기시간",
    "Repair XP Per Step": "단계당 수리 경험치",
    "Min Light Level": "최소 밝기",
    "Drop Repair Amount": "전리품 내구도 회복량",
    "Max Charms Displayed": "표시할 최대 부적 수",
    "Blocked Entities": "차단할 개체",
    "Fishing Retract Delay": "낚싯줄 회수 지연",
    "Seconds Between Growth Ticks": "성장 처리 간격(초)",
    "Full Potency Radius": "최대 효과 반경",
    "Bucket Range": "양동이 작동 범위",
    "Disable Alkahestry Tome": "알카헤스트리의 고서 비활성화",
    "Disable Display Pedestals": "전시용 받침대 비활성화",
    "Disable Spawn Egg Recipes": "생성 알 제작법 비활성화",
    "Disable Charms": "부적 비활성화",
    "Angelheart Vial": "천사의 심장 약병",
    "Infernal Claws": "지옥의 발톱",
    "Infernal Tear": "지옥의 눈물",
    "Kraken Shell": "크라켄 껍데기",
    "Lantern of Paranoia": "불안의 등불",
    "Phoenix Down": "피닉스의 깃털",
    "Rending Gale": "찢어발기는 돌풍",
    "Rod of Lyssa": "리사의 지팡이",
    "Seeker Shot": "추적 탄환",
    "Apothecary Cauldron": "약제사의 가마솥",
    "Leaping Potency": "도약 효과 강도",
    "Mundane Blocks": "일반 블록",
    "Gunpowder Worth": "화약 충전 가치",
    "Centered Explosion": "폭발 중심 고정",
    "Ender Pearl Limit": "엔더 진주 한도",
    "Snowball Worth": "눈덩이 충전 가치",
    "Snowball Fire-Immune Bonus": "화염 면역 대상 눈덩이 추가 피해",
    "Snowball Blaze Bonus": "블레이즈 대상 눈덩이 추가 피해",
    "Bone Meal Worth": "뼛가루 충전 가치",
    "Area Radius": "효과 반경",
    "Max Capacity Per Plantable": "재배 가능 아이템당 최대 용량",
    "Pedestal Cooldown": "받침대 재사용 대기시간",
    "Repair Cooldown": "수리 재사용 대기시간",
    "Glowstone Worth": "발광석 충전 가치",
    "Glowstone Limit": "발광석 한도",
    "Damage Per Kill": "처치당 내구도 소모량",
    "Give Temporary Resistance": "임시 저항 효과 부여",
    "Give Temporary Regeneration": "임시 재생 효과 부여",
    "Give Temporary Fire Resistance": "임시 화염 저항 효과 부여",
    "Give Temporary Water Breathing": "임시 수중 호흡 효과 부여",
    "Fire Charge Limit": "화염구 한도",
    "Fire Charge Cost": "화염구 비용",
    "Fire Charge Worth": "화염구 충전 가치",
    "Blaze Powder Limit": "블레이즈 가루 한도",
    "Blaze Powder Worth": "블레이즈 가루 충전 가치",
    "Flight Cast Cost": "비행 사용 비용",
    "Lightning Bolt Cost": "번개 사용 비용",
    "Lightning Target Range": "번개 대상 지정 범위",
    "Blocked Push Entities": "밀어낼 수 없는 개체",
    "Blocked Push Projectiles": "밀어낼 수 없는 발사체",
    "Flat Steal Failure Rate (%)": "기본 훔치기 실패율(%)",
    "Anger On Failed Steal": "훔치기 실패 시 대상 분노",
    "Steal From Players": "플레이어에게서 훔치기",
    "Max Capacity Per Item": "아이템 종류당 최대 용량",
    "Max Light Level": "최대 밝기",
    "Active Light Level": "활성화 시 밝기",
    "Push Radius": "밀어내기 반경",
    "Melee Cooldown": "근접 공격 재사용 대기시간",
    "Bucket Cooldown": "양동이 재사용 대기시간",
    "Shears Cooldown": "가위 재사용 대기시간",
    "Fishing Success Rate (%)": "낚시 성공률(%)",
}


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 객체가 아니에요: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def normalize_text(value: str) -> str:
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    return value


def transform(value: object) -> object:
    if isinstance(value, str):
        return normalize_text(value)
    if isinstance(value, list):
        return [transform(item) for item in value]
    return value


def normalize_language() -> dict[str, object]:
    english = load_json(LANG_ROOT / "en_us.json")
    current = load_json(LANG_ROOT / "ko_kr.json")
    auto = load_json(LANG_ROOT / "auto_candidates.json")
    sources = load_json(LANG_ROOT / "candidate_sources.json")
    reviewed: dict[str, object] = {}
    for key, source in english.items():
        if key in EXACT_BY_KEY:
            value = EXACT_BY_KEY[key]
        elif key.startswith("reliquary.configuration.") and source in CONFIG_EXACT:
            value = CONFIG_EXACT[str(source)]
        elif sources[key] == "new_translation_required":
            value = auto[key]
        else:
            value = current[key]
        reviewed[key] = transform(value)
    write_json(LANG_ROOT / "ko_kr.json", reviewed)
    report = {
        "reviewed_keys": len(reviewed),
        "bundled_candidates_reviewed": sum(
            source == "bundled_ko_kr" for source in sources.values()
        ),
        "new_translations_reviewed": sum(
            source == "new_translation_required" for source in sources.values()
        ),
        "status": "complete",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def normalize_quests() -> dict[str, object]:
    english = load_json(QUEST_ROOT / "en_us.json")
    korean = load_json(QUEST_ROOT / "ko_kr.json")
    reviewed = {key: transform(korean[key]) for key in english}
    write_json(QUEST_ROOT / "ko_kr.json", reviewed)
    report = {"reviewed_keys": len(reviewed), "status": "complete"}
    write_json(WORK_ROOT / "quest_normalization.json", report)
    return report


def verify_scope(root: Path) -> tuple[dict[str, object], list[str]]:
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    errors: list[str] = []
    untranslated: list[str] = []
    if list(english) != list(korean):
        errors.append("키 또는 키 순서가 영어 원문과 달라요")
    for key in english.keys() & korean.keys():
        source = english[key]
        target = korean[key]
        errors.extend(family_goal.validate_value(key, source, target))
        if isinstance(source, str) and isinstance(target, str):
            if Counter(NUMBER.findall(source)) != Counter(NUMBER.findall(target)):
                errors.append(f"숫자 불일치: {key}")
            if (
                source == target
                and LATIN_WORD.search(source)
                and not (
                    family_goal.is_allowed_original(source)
                    or source in {"Reliquary", "Shift", "ON", "OFF"}
                )
            ):
                untranslated.append(key)
    if untranslated:
        errors.append(f"분류되지 않은 영어 유지: {untranslated[:30]}")
    return (
        {
            "keys": len(english),
            "untranslated": untranslated,
            "validation_errors": len(errors),
            "status": "complete" if not errors else "incomplete",
        },
        errors,
    )


def verify() -> tuple[dict[str, object], list[str]]:
    rows = []
    errors: list[str] = []
    for label, root in (("language", LANG_ROOT), ("quests", QUEST_ROOT)):
        row, current = verify_scope(root)
        row["scope"] = label
        rows.append(row)
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
    jar = next((instance / "mods").glob("reliquary-*.jar"))
    with ZipFile(jar) as archive:
        advancement_files = [
            name
            for name in archive.namelist()
            if name.startswith("data/reliquary/advancement/") and name.endswith(".json")
        ]
        advancement_display = [
            name
            for name in advancement_files
            if "display" in json.loads(archive.read(name))
        ]
    visible_lines = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json", ".snbt"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            if "reliquary:" in line.lower() and any(
                token in line.lower()
                for token in ("name", "display", "tooltip", "lore", "text")
            ):
                visible_lines.append(
                    f"{path.relative_to(instance).as_posix()}:{number}:{line.strip()}"
                )
    report = {
        "jar": jar.name,
        "advancement_files": len(advancement_files),
        "advancement_display_files": advancement_display,
        "kubejs_direct_display_lines": visible_lines,
        "status": "complete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("normalize-language", "normalize-quests", "verify", "audit")
    )
    args = parser.parse_args()
    if args.command == "normalize-language":
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
