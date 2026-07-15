#!/usr/bin/env python3
"""Mystical Agriculture 계열을 준비·번역·검증하고 누적 산출물에 반영한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import audit_ftbquests_titles as quest_audit
import build_ae2_quests as snbt
from local_paths import PROJECT_ROOT, resolve_source_root

WORK_ROOT = PROJECT_ROOT / "working/mystical"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
OUTPUT_OVERRIDES = PROJECT_ROOT / "output/overrides"
QUEST_OUTPUT = OUTPUT_OVERRIDES / "config/ftbquests/quests/lang/ko_kr.snbt"
QUEST_CHAPTER = "elmystical_agriculturerr"
TARGETS = (
    ("MysticalAgriculture-", "mysticalagriculture"),
    ("MysticalAgradditions-", "mysticalagradditions"),
)
RELATED_JARS = (
    "MysticalCustomization-",
    "botanypotsmystical-",
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")

TIER_NAMES = {
    "Inferium": "인퍼륨",
    "Prudentium": "프루덴튬",
    "Tertium": "터튬",
    "Imperium": "임퍼륨",
    "Supremium": "수프레뮴",
    "Awakened Supremium": "각성 수프레뮴",
    "Insanium": "인사늄",
    "Soulium": "소울륨",
}

CROP_NAMES = {
    "Air": "공기",
    "Earth": "대지",
    "Water": "물",
    "Fire": "불",
    "Inferium": "인퍼륨",
    "Stone": "돌",
    "Dirt": "흙",
    "Wood": "나무",
    "Ice": "얼음",
    "Deepslate": "심층암",
    "Nature": "자연",
    "Dye": "염료",
    "Nether": "네더",
    "Coal": "석탄",
    "Coral": "산호",
    "Honey": "꿀",
    "Amethyst": "자수정",
    "Pig": "돼지",
    "Chicken": "닭",
    "Cow": "소",
    "Sheep": "양",
    "Squid": "오징어",
    "Fish": "물고기",
    "Slime": "슬라임",
    "Turtle": "거북",
    "Armadillo": "아르마딜로",
    "Iron": "철",
    "Nether Quartz": "네더 석영",
    "Glowstone": "발광석",
    "Redstone": "레드스톤",
    "Obsidian": "흑요석",
    "Prismarine": "프리즈머린",
    "Sculk": "스컬크",
    "Zombie": "좀비",
    "Skeleton": "스켈레톤",
    "Creeper": "크리퍼",
    "Spider": "거미",
    "Phantom": "팬텀",
    "Rabbit": "토끼",
    "Gold": "금",
    "Lapis Lazuli": "청금석",
    "End": "엔드",
    "Experience": "경험치",
    "Breeze": "브리즈",
    "Blaze": "블레이즈",
    "Ghast": "가스트",
    "Enderman": "엔더맨",
    "Diamond": "다이아몬드",
    "Emerald": "에메랄드",
    "Netherite": "네더라이트",
    "Wither Skeleton": "위더 스켈레톤",
    "Rubber": "고무",
    "Silicon": "실리콘",
    "Sulfur": "황",
    "Aluminum": "알루미늄",
    "Copper": "구리",
    "Saltpeter": "초석",
    "Tin": "주석",
    "Bronze": "청동",
    "Zinc": "아연",
    "Brass": "황동",
    "Silver": "은",
    "Lead": "납",
    "Graphite": "흑연",
    "Steel": "강철",
    "Nickel": "니켈",
    "Constantan": "콘스탄탄",
    "Electrum": "일렉트럼",
    "Invar": "인바",
    "Uranium": "우라늄",
    "Platinum": "백금",
    "Iridium": "이리듐",
    "Apatite": "인회석",
    "Ruby": "루비",
    "Sapphire": "사파이어",
    "Peridot": "페리도트",
    "Soulium": "소울륨",
    "Signalum": "시그날룸",
    "Lumium": "루미움",
    "Enderium": "엔더리움",
    "Flux-Infused Ingot": "플럭스 주입 주괴",
    "Flux-Infused Gem": "플럭스 주입 보석",
    "HOP Graphite": "HOP 흑연",
    "Amethyst Bronze": "자수정 청동",
    "Pig Iron": "선철",
    "Cobalt": "코발트",
    "Rose Gold": "장미 금",
    "Grains of Infinity": "무한의 알갱이",
    "Copper Alloy": "구리 합금",
    "Redstone Alloy": "레드스톤 합금",
    "Conductive Alloy": "전도성 합금",
    "Soularium": "솔라리움",
    "Dark Steel": "다크 스틸",
    "Pulsating Alloy": "맥동 합금",
    "Energetic Alloy": "에너지 합금",
    "Vibrant Alloy": "활기찬 합금",
    "End Steel": "엔드 스틸",
    "Mystical Flower": "신비로운 꽃",
    "Manasteel": "마나스틸",
    "Refined Glowstone": "정제된 발광석",
    "Refined Obsidian": "정제된 흑요석",
    "Marble": "대리석",
    "Limestone": "석회암",
    "Basalt": "현무암",
    "Steeleaf": "강철잎",
    "Ironwood": "철나무",
    "Fiery Ingot": "불꽃 주괴",
    "Aquamarine": "아쿠아마린",
    "Rock Crystal": "암석 수정",
    "Compressed Iron": "압축 철",
    "Sky Stone": "스카이 스톤",
    "Certus Quartz": "서투스 석영",
    "Quartz Enriched Iron": "석영 강화 철",
    "Energized Steel": "에너지화 강철",
    "Blazing Crystal": "타오르는 수정",
    "Niotic Crystal": "나이오틱 수정",
    "Spirited Crystal": "스피리티드 수정",
    "Fluorite": "형석",
}

# 정착된 한국어가 불명확한 모드 고유 재료명은 원문을 유지한다.
INTENTIONAL_CROP_ORIGINALS = {
    "Blizz",
    "Blitz",
    "Basalz",
    "Slimesteel",
    "Manyullyn",
    "Queen's Slime",
    "Hepatizon",
    "Elementium",
    "Terrasteel",
    "Osmium",
    "Menril",
    "Starmetal",
    "Draconium",
    "Yellorium",
    "Cyanite",
    "Fluix",
    "Uraninite",
    "Knightmetal",
}

AUGMENT_NAMES = {
    "absorption": "흡수",
    "luck": "행운",
    "health_boost": "생명력 강화",
    "pathing_aoe": "길 만들기 범위",
    "nausea_resistance": "멀미 저항",
    "night_vision": "야간 투시",
    "water_breathing": "수중 호흡",
    "jump_boost": "점프 강화",
    "speed": "신속",
    "mining_aoe": "채굴 범위",
    "tilling_aoe": "경작 범위",
    "blindness_resistance": "실명 저항",
    "fire_resistance": "화염 저항",
    "step_assist": "단차 오르기",
    "strength": "힘",
    "haste": "성급함",
    "no_fall_damage": "추락 피해 무효",
    "slow_falling": "느린 낙하",
    "attack_aoe": "공격 범위",
    "weakness_resistance": "나약함 저항",
    "slowness_resistance": "구속 저항",
    "poison_resistance": "독 저항",
    "mining_fatigue_resistance": "채굴 피로 저항",
    "hunger_resistance": "허기 저항",
    "wither_resistance": "시듦 저항",
    "flight": "비행",
}
ROMAN = {"i": "I", "ii": "II", "iii": "III", "iv": "IV", "v": "V"}

LANG_OVERRIDES = {
    "itemGroup.mysticalagriculture": "Mystical Agriculture",
    "book.mysticalagriculture.name": "Mystical Agriculture",
    "item.mysticalagriculture.unattuned_augment": "미조율 증강",
    "item.mysticalagriculture.augment": "%s 증강",
    "block.mysticalagriculture.awakened_supremium_block": "각성 수프레뮴 블록",
    "block.mysticalagriculture.awakened_supremium_ingot_block": "각성 수프레뮴 주괴 블록",
    "block.mysticalagriculture.awakened_supremium_gemstone_block": "각성 수프레뮴 보석 블록",
    "block.mysticalagriculture.awakened_supremium_growth_accelerator": "각성 수프레뮴 성장 가속기",
    "block.mysticalagriculture.deepslate_prosperity_ore": "심층암 번영 광석",
    "block.mysticalagriculture.deepslate_inferium_ore": "심층암 인퍼륨 광석",
    "block.mysticalagriculture.awakening_pedestal": "각성 받침대",
    "block.mysticalagriculture.awakening_altar": "각성 제단",
    "block.mysticalagriculture.essence_vessel": "에센스 용기",
    "block.mysticalagriculture.enchanter": "인챈터",
    "block.mysticalagriculture.seed_reprocessor": "씨앗 재처리기",
    "block.mysticalagriculture.soul_extractor": "영혼 추출기",
    "block.mysticalagriculture.harvester": "수확기",
    "block.mysticalagriculture.soulium_spawner": "소울륨 소환기",
    "block.mysticalagriculture.mystical_crop": "%s 작물",
    "item.mysticalagriculture.awakened_supremium_essence": "각성 수프레뮴 에센스",
    "item.mysticalagriculture.awakened_supremium_ingot": "각성 수프레뮴 주괴",
    "item.mysticalagriculture.awakened_supremium_nugget": "각성 수프레뮴 조각",
    "item.mysticalagriculture.awakened_supremium_gemstone": "각성 수프레뮴 보석",
    "item.mysticalagriculture.cognizant_dust": "인지의 가루",
    "item.mysticalagriculture.honey_agglomeratio": "꿀 응집체",
    "item.mysticalagriculture.mystical_flower_agglomeratio": "신비로운 꽃 응집체",
    "item.mysticalagriculture.wand": "마법봉",
    "item.mysticalagriculture.diamond_sickle": "다이아몬드 낫",
    "item.mysticalagriculture.diamond_scythe": "다이아몬드 대낫",
    "item.mysticalagriculture.upgrade_base": "기계 업그레이드 기반",
    "item.mysticalagriculture.awakened_supremium_upgrade": "각성 수프레뮴 기계 업그레이드",
    "container.mysticalagriculture.enchanter": "인챈터",
    "container.mysticalagriculture.soul_extractor": "영혼 추출기",
    "container.mysticalagriculture.harvester": "수확기",
    "container.mysticalagriculture.soulium_spawner": "소울륨 소환기",
    "enchantment.mysticalagriculture.mystical_enlightenment": "신비한 깨달음",
    "enchantment.mysticalagriculture.mystical_enlightenment.desc": "에센스 무기로 엔더 드래곤이나 위더를 처치하면 인지의 가루를 떨어뜨립니다.",
    "enchantment.mysticalagriculture.soul_siphoner": "영혼 흡수",
    "enchantment.mysticalagriculture.soul_siphoner.desc": "레벨마다 몹을 처치해 얻는 영혼이 10퍼센트 증가합니다.",
    "tooltip.mysticalagriculture.augment_id": "증강 ID: %s",
    "tooltip.mysticalagriculture.set_bonus": "세트 보너스: %s",
    "tooltip.mysticalagriculture.augments": "증강:",
    "tooltip.mysticalagriculture.required_biomes": "필요한 생물군계:",
    "tooltip.mysticalagriculture.chance": "확률: %s",
    "tooltip.mysticalagriculture.requires_effective_farmland": "%s에 심어야 합니다",
    "tooltip.mysticalagriculture.invalid_biome": "잘못된 생물군계",
    "tooltip.mysticalagriculture.machine_fuel_usage": "연료 사용량: %s",
    "tooltip.mysticalagriculture.machine_scan_fuel_usage": "탐색 연료 사용량: %s",
    "tooltip.mysticalagriculture.machine_area": "범위: %s",
    "tooltip.mysticalagriculture.machine_spawn_radius": "소환 반경: %s",
    "tooltip.mysticalagriculture.hostile_soulium_dagger": "적대적 생물에게서 추가 영혼을 얻습니다.",
    "tooltip.mysticalagriculture.creative_soulium_dagger": "모든 생물에게서 *무한한* 영혼을 얻습니다.",
    "tooltip.mysticalagriculture.passive_attuned": "비적대 조율",
    "tooltip.mysticalagriculture.hostile_attuned": "적대 조율",
    "tooltip.mysticalagriculture.creative_attuned": "크리에이티브 조율",
    "tooltip.mysticalagriculture.awakened_supremium_set_bonus": "광역 작물 성장",
    "tooltip.mysticalagriculture.upgrade_speed": "작동 속도: %sx",
    "tooltip.mysticalagriculture.upgrade_fuel_rate": "연료 사용량: %sx",
    "tooltip.mysticalagriculture.upgrade_fuel_capacity": "연료 용량: %sx",
    "tooltip.mysticalagriculture.upgrade_area": "범위: +%s",
    "tooltip.mysticalagriculture.missing_essences": "부족한 에센스",
    "tooltip.mysticalagriculture.aoe_offset": "중심 이동: %s, %s",
    "jei.category.mysticalagriculture.awakening": "각성",
    "jei.category.mysticalagriculture.enchanter": "인챈터",
    "jei.category.mysticalagriculture.soul_extractor": "영혼 추출",
    "jei.category.mysticalagriculture.soulium_spawner": "소울륨 소환기",
    "jei.category.mysticalagriculture.crux": "크룩스",
    "jei.desc.mysticalagriculture.cognizant_dust": "신비한 깨달음 마법이 부여된 에센스 무기로 위더나 엔더 드래곤을 처치하면 떨어집니다.",
    "config.jade.plugin_mysticalagriculture.crop": "자원 작물 추가 정보",
    "config.jade.plugin_mysticalagriculture.inferium_crop": "인퍼륨 작물 보조 생산물",
    "config.jade.plugin_mysticalagriculture.infused_farmland": "에센스 경작지 등급",
    "config.jade.plugin_mysticalagriculture.essence_vessel": "에센스 용기 정보",
    "mobSoulType.mysticalagriculture.slime": "슬라임",
    "mobSoulType.mysticalagriculture.zombie": "좀비",
    "mobSoulType.mysticalagriculture.skeleton": "스켈레톤",
    "mobSoulType.mysticalagriculture.spider": "거미",
    "itemGroup.mysticalagradditions": "Mystical Agradditions",
}

BOOK_OVERRIDES = {
    "book.mysticalagriculture.landing_text": "Mystical Agriculture는 자원을 작물로 재배하는 모드입니다. 이 책에서는 Mystical Agriculture의 모든 기능을 안내합니다. $(br2)$(l:https://blakesmods.com/wiki/mysticalagriculture)더 자세한 가이드를 보려면 여기를 클릭하세요.$()",
    "book.mysticalagriculture.category.basics.description": "이 장에서는 Mystical Agriculture를 시작하는 데 필요한 내용을 설명합니다. $(br2)$(l:https://blakesmods.com/wiki/mysticalagriculture/guides/getting-started)자세한 시작 가이드를 보려면 여기를 클릭하세요.$()",
    "book.mysticalagriculture.category.souls.description": "이 장에서는 몹 전리품 작물을 만들고 사용하는 데 필요한 네더 콘텐츠와 몹 영혼 시스템을 설명합니다. $(br2)$(l:https://blakesmods.com/wiki/mysticalagriculture/guides/collecting-mob-souls)몹 영혼 수집 가이드를 자세히 보려면 여기를 클릭하세요.$()",
    "book.mysticalagriculture.category.elemental.description": "이 장에서는 각성 수프레뮴과 원소 에센스 관련 콘텐츠를 설명합니다. $(br2)$(l:https://blakesmods.com/wiki/mysticalagriculture/guides/awakened-supremium)각성 수프레뮴 제작 가이드를 자세히 보려면 여기를 클릭하세요.$()",
    "book.mysticalagriculture.category.tinkering.description": "이 장에서는 에센스 도구·방어구와 개조 시스템을 설명합니다. $(br2)$(l:https://blakesmods.com/wiki/mysticalagriculture/guides/upgrading-essence-gear)에센스 장비 업그레이드 가이드를 자세히 보려면 여기를 클릭하세요.$()",
    "book.mysticalagriculture.entry.essence_farmland.page.2": "$(li)작물은 모든 등급의 에센스 경작지에서 $(bold)보통$() 10퍼센트 확률로 두 번째 씨앗을 떨어뜨립니다. $$(li)작물과 같은 등급의 에센스 경작지에서는 두 번째 씨앗을 떨어뜨릴 확률이 10퍼센트 추가됩니다. $(li)인퍼륨 씨앗은 더 높은 등급의 에센스 경작지에서 더 많은 에센스를 떨어뜨립니다.",
    "book.mysticalagriculture.entry.growth_accelerators.page.1": "성장 가속기는 식물의 성장 속도를 높입니다. 지정된 범위 안에서 자신보다 위에 있는 첫 번째 식물에 무작위 성장 틱을 적용합니다. $(br2)식물이 범위 안에 있기만 하면 등급과 관계없이 성장 가속기를 여러 개 쌓을 수 있습니다.",
    "book.mysticalagriculture.entry.growth_accelerators.page.2": "성장 가속기의 범위는 경작지 아래에 설치했을 때를 기준으로 합니다. $(br2)$(l:https://blakesmods.com/wiki/mysticalagriculture/guides/speeding-up-crop-growth)성장 가속기 사용법을 자세히 보려면 여기를 클릭하세요.$()",
    "book.mysticalagriculture.entry.sickles": "낫",
    "book.mysticalagriculture.entry.sickles.page.1": "낫은 넓은 범위의 식물을 수확하거나 제거하는 도구입니다. $(br2)등급이 높은 낫일수록 효과 범위가 넓습니다.",
    "book.mysticalagriculture.entry.scythes": "대낫",
    "book.mysticalagriculture.entry.scythes.page.1": "대낫을 들고 우클릭하면 넓은 범위의 작물을 수확합니다. 효과 범위 안에서 다 자란 작물은 뽑히지 않고 수확됩니다. $(br2)대낫은 공격 범위가 넓은 효과적인 무기이기도 합니다. $(br2)등급이 높은 대낫일수록 효과 범위가 넓습니다.",
    "book.mysticalagriculture.entry.soulium_dagger.page.1": "소울륨 단검은 몹의 영혼을 모으는 도구입니다. 영혼은 $(l:souls/soul_jars)영혼 항아리$()에 저장되며, 소울륨 단검으로 몹을 처치하면 모을 수 있습니다. $(br2)소울륨 단검은 $(l:basics/infusion_altar)주입 제단$()에서 업그레이드하여 영혼 수집 효율을 높일 수 있습니다.",
    "book.mysticalagriculture.entry.infusion_altar.page.3": "주입 제단을 월드에 설치하면 받침대를 놓을 위치가 표시됩니다. $(br2)$(l:https://blakesmods.com/wiki/mysticalagriculture/guides/creating-seeds)주입 제단 사용법을 자세히 보려면 여기를 클릭하세요.$()",
    "book.mysticalagriculture.entry.soulium_ore.page.1": "소울륨 광석은 $(bold)보통$() 네더의 $(l:souls/soulstone)영혼석$() 광맥 안에서 생성됩니다.",
    "book.mysticalagriculture.entry.soul_jars.page.1": "영혼 항아리는 $(l:souls/soulium_dagger)소울륨 단검$()과 함께 사용해 몹 영혼을 모읍니다. 가득 찬 영혼 항아리는 해당 생물의 $(l:basics/resource_crops)자원 작물$()을 만드는 데 사용할 수 있습니다. $(br2)$(l:machines/soul_extractor)영혼 추출기$()에 몹 전리품을 넣어 영혼 항아리를 채울 수도 있습니다.",
    "book.mysticalagriculture.entry.soulium_dagger.page.3": "비적대 조율 소울륨 단검은 비적대적 몹에게서 얻는 영혼을 50퍼센트 추가로 제공합니다.",
    "book.mysticalagriculture.entry.soulium_dagger.page.4": "적대 조율 소울륨 단검은 적대적 몹에게서 얻는 영혼을 50퍼센트 추가로 제공합니다.",
    "book.mysticalagriculture.entry.elemental_essences.page.1": "공기, 대지, 물, 불 에센스는 $(l:elemental/essence_vessel)에센스 용기$()에 담아 $(l:elemental/awakening_altar)각성 제단$() 조합법에 사용할 수 있습니다. $(br2)원소 씨앗을 $(l:basics/essence_farmland)1등급 에센스 경작지$()에 심으면 추가 생산물을 얻을 수 있습니다.",
    "book.mysticalagriculture.entry.experience_capsule": "경험치 캡슐",
    "book.mysticalagriculture.entry.experience_capsule.page.1": "경험치 캡슐은 경험치 씨앗을 만드는 데 필요한 경험치를 모으는 아이템입니다. $(br2)인벤토리에 경험치 캡슐을 넣고 경험치 구슬을 획득하면 경험치가 저장됩니다.",
    "book.mysticalagriculture.entry.enchanter": "인챈터",
    "book.mysticalagriculture.entry.enchanter.page.1": "인챈터는 여러 조합 재료와 경험치 에센스를 사용해 도구와 방어구에 마법을 부여하는 블록입니다. $(br2)모루와 비슷하게 책과 도구·방어구 모두에 마법을 부여할 수 있습니다.",
    "book.mysticalagriculture.entry.cognizant_dust": "인지의 가루",
    "book.mysticalagriculture.entry.cognizant_dust.page.1": "인지의 가루는 $(bold)보통$() 신비한 깨달음 마법이 부여된 $(l:tinkering/essence_tools)에센스 무기$()로 위더나 엔더 드래곤을 처치해 얻습니다. $(br2)신비한 깨달음의 레벨이 높을수록 처치 시 떨어지는 가루의 양이 증가합니다.",
    "book.mysticalagriculture.entry.essence_vessel": "에센스 용기",
    "book.mysticalagriculture.entry.essence_vessel.page.1": "에센스 용기는 $(l:elemental/awakening_altar)각성 제단$() 구조에서 아이템 제작에 필요한 원소 에센스를 담는 데 사용합니다. 용기 하나에는 한 종류의 원소 에센스를 최대 40개까지 담을 수 있습니다.",
    "book.mysticalagriculture.entry.awakening_altar": "각성 제단",
    "book.mysticalagriculture.entry.awakening_altar.page.1": "각성 제단은 $(bold)보통$() $(l:elemental/awakened_supremium)각성 수프레뮴$()을 만드는 조합 구조입니다. 주입 제단 1개, 주입 받침대 4개, $(l:elemental/essence_vessel)에센스 용기$() 4개로 구성됩니다. $(br2)조합법에 맞게 재료를 놓은 뒤 레드스톤 신호로 제단을 작동하세요.",
    "book.mysticalagriculture.entry.awakening_altar.page.3": "각성 제단을 월드에 설치하면 받침대와 용기를 놓을 위치가 표시됩니다.",
    "book.mysticalagriculture.entry.awakened_supremium": "각성 수프레뮴",
    "book.mysticalagriculture.entry.awakened_supremium.page.1": "각성 수프레뮴은 여러 수프레뮴 아이템의 상위 버전을 만드는 고등급 조합 재료입니다. $(br2)$(bold)보통$() $(l:elemental/awakening_altar)각성 제단$()에서 수프레뮴 블록에 $(l:elemental/cognizant_dust)인지의 가루$()를 주입해 만듭니다.",
    "book.mysticalagriculture.entry.machine_upgrades": "기계 업그레이드",
    "book.mysticalagriculture.entry.machine_upgrades.page.1": "기계 업그레이드를 적용할 수 있는 기계에 넣으면 성능이 향상됩니다. $(br2)등급이 높은 기계는 동력 사용과 생성 속도가 모두 빨라집니다.",
    "book.mysticalagriculture.entry.essence_furnace": "화로",
    "book.mysticalagriculture.entry.essence_furnace.page.1": "기본 화로를 업그레이드하면 $(l:machines/machine_upgrades)기계 업그레이드$()를 사용해 제련 속도를 높일 수 있습니다. 고체 연료로 작동하며 내부에 동력 저장 공간이 있습니다.",
    "book.mysticalagriculture.entry.soul_extractor": "영혼 추출기",
    "book.mysticalagriculture.entry.soul_extractor.page.1": "영혼 추출기는 몹 전리품을 몹 영혼으로 바꿉니다. 고체 연료로 작동하며 내부에 동력 저장 공간이 있습니다. $(br2)남는 몹 전리품을 활용할 수 있지만, 일반적으로 $(l:souls/soulium_dagger)소울륨 단검$()보다 효율은 낮습니다.",
    "book.mysticalagriculture.entry.harvester": "수확기",
    "book.mysticalagriculture.entry.harvester.page.1": "수확기는 다 자란 작물을 자동으로 수확합니다. 고체 연료로 작동하며 내부에 동력 저장 공간이 있습니다. $(br2)수확한 작물은 자동으로 다시 심습니다. $(br2)생산물은 내부 인벤토리에 넣으며, 공간이 없으면 작물 위에 놓습니다.",
    "book.mysticalagriculture.entry.harvester.page.2": "수확기는 작물의 성장 상태를 확인할 때마다 소량의 동력을 사용하고, 다 자란 작물을 수확할 때는 더 많은 동력을 사용합니다. $(br2)$(l:machines/machine_upgrades)기계 업그레이드$()로 강화할 수 있습니다. $(br2)레드스톤 신호를 보내면 작동을 멈춥니다.",
    "book.mysticalagriculture.entry.soulium_spawner": "소울륨 소환기",
    "book.mysticalagriculture.entry.soulium_spawner.page.1": "소울륨 소환기는 에센스를 사용해 적대적·비적대적 몹을 소환합니다. 고체 연료로 작동하며 내부에 동력 저장 공간이 있습니다. $(br2)내부 인벤토리에는 아이템을 최대 512개까지 보관할 수 있습니다. 작업마다 정해진 아이템과 동력을 소비해 해당 몹을 소환합니다.",
    "book.mysticalagriculture.entry.soulium_spawner.page.2": "소환기는 주변 3블록 반경의 무작위 위치에 몹을 소환합니다. $(br2)$(l:machines/machine_upgrades)기계 업그레이드$()로 강화할 수 있습니다. $(br2)레드스톤 신호를 보내면 작동을 멈춥니다.",
    "book.mysticalagriculture.entry.pathing_aoe_augment.page.1": "길 만들기 범위 증강은 삽이 흙길을 만드는 범위를 최대 9x9까지 늘립니다. $(br2)삽을 사용하면서 웅크리면 광역 효과가 활성화됩니다. $(br2)CTRL + 방향키를 눌러 효과 범위의 중심을 옮길 수 있습니다.",
    "book.mysticalagriculture.entry.mining_aoe_augment.page.1": "채굴 범위 증강은 도구가 블록을 부수는 범위를 최대 9x9까지 늘립니다. $(br2)웅크리면 광역 효과를 잠시 무효화할 수 있습니다. $(br2)CTRL + 방향키를 눌러 효과 범위의 중심을 옮길 수 있습니다.",
    "book.mysticalagriculture.entry.tilling_aoe_augment.page.1": "경작 범위 증강은 괭이가 경작지를 만드는 범위를 최대 9x9까지 늘립니다. $(br2)괭이를 사용하면서 웅크리면 광역 효과가 활성화됩니다. $(br2)CTRL + 방향키를 눌러 효과 범위의 중심을 옮길 수 있습니다.",
    "book.mysticalagriculture.entry.step_assist_augment.page.1": "단차 오르기 증강은 방어구를 착용한 동안 점프하지 않고 1블록 높이의 단차를 오르게 하는 레깅스 또는 부츠 증강입니다. $(br2)Shift 키를 누르면 이 효과를 잠시 무효화할 수 있습니다.",
}

RESISTANCE_BOOK = {
    "blindness": ("실명", "투구"),
    "hunger": ("허기", "투구"),
    "nausea": ("멀미", "투구"),
    "slowness": ("구속", "레깅스"),
    "weakness": ("나약함", "흉갑"),
}

AGRADDITIONS_OVERRIDES = {
    "block.mysticalagradditions.nether_prosperity_ore": "네더 번영 광석",
    "block.mysticalagradditions.nether_inferium_ore": "네더 인퍼륨 광석",
    "block.mysticalagradditions.end_prosperity_ore": "엔드 번영 광석",
    "block.mysticalagradditions.end_inferium_ore": "엔드 인퍼륨 광석",
    "block.mysticalagradditions.gaia_spirit_crux": "가이아의 영혼 크룩스",
    "block.mysticalagradditions.awakened_draconium_crux": "각성 드라코늄 크룩스",
    "block.mysticalagradditions.neutronium_crux": "뉴트로늄 크룩스",
    "block.mysticalagradditions.nitro_crystal_crux": "니트로 수정 크룩스",
    "item.mysticalagradditions.awakened_supremium_paxel": "각성 수프레뮴 팩셀",
    "tooltip.mysticalagradditions.gives_buffs": "부여 효과:",
    "config.jade.plugin_mysticalagradditions.infused_farmland": "에센스 경작지 등급",
    "book.mysticalagriculture.category.agradditions.name": "Mystical Agradditions",
    "book.mysticalagriculture.category.agradditions.description": "이 장에서는 Mystical Agradditions가 추가하는 콘텐츠를 설명합니다.",
    "book.mysticalagriculture.entry.insanium": "인사늄 에센스",
    "book.mysticalagriculture.entry.insanium.page.1": "인사늄 에센스는 수프레뮴보다 높은 추가 에센스 등급이며 6등급 작물을 만드는 데 사용합니다. $(br2)6등급 작물에는 낮은 등급에 없는 특별한 성질이 있습니다. $(br)$(li)자라려면 경작지 아래에 $(l:mysticalagriculture:agradditions/cruxes)크룩스$()가 필요합니다.$() $(li)수확해도 두 번째 씨앗을 떨어뜨리지 않습니다.$()",
    "book.mysticalagriculture.entry.insanium.page.2": "$(li)$(bold)보통$() $(l:advances/mystical_fertilizer)신비로운 비료$()나 $(l:basics/fertilized_essence)비옥한 에센스$()로 성장시킬 수 없습니다.$()",
    "book.mysticalagriculture.entry.cruxes": "크룩스",
    "book.mysticalagriculture.entry.cruxes.page.1": "$(l:mysticalagriculture:agradditions/insanium)6등급 작물$()이 자랄 수 있도록 아래에 놓는 블록입니다.",
    "book.mysticalagriculture.entry.paxels": "에센스 팩셀",
    "book.mysticalagriculture.entry.paxels.page.1": "에센스 팩셀은 곡괭이, 도끼, 삽 기능을 하나로 합친 도구입니다.",
    "book.mysticalagriculture.entry.ore_variants": "광석 변형",
    "book.mysticalagriculture.entry.ore_variants.page.1": "네더 번영 광석과 네더 인퍼륨 광석은 $(bold)보통$() 네더의 모든 Y 높이에서 생성됩니다.",
    "book.mysticalagriculture.entry.ore_variants.page.2": "엔드 번영 광석과 엔드 인퍼륨 광석은 $(bold)보통$() 엔드의 모든 Y 높이에서 생성됩니다.",
    "book.mysticalagriculture.entry.essence_apples": "에센스 사과",
    "book.mysticalagriculture.entry.essence_apples.page.1": "에센스 사과는 일반 사과보다 훨씬 '건강한' 대안으로, 여러 효과와 추가 영양을 제공합니다.",
    "modifier.mysticalagradditions.prosperous": "번영",
    "modifier.mysticalagradditions.prosperous.flavor": "번영을!",
    "modifier.mysticalagradditions.prosperous.description": "도구와 무기로 작업할 때 일정 확률로 번영 파편을 떨어뜨립니다.",
    "modifier.mysticalagradditions.soul_siphoner": "영혼 흡수",
    "modifier.mysticalagradditions.soul_siphoner.flavor": "영혼을!",
    "modifier.mysticalagradditions.soul_siphoner.description": "무기가 소울륨 단검처럼 몹의 영혼을 흡수합니다.",
    "crop.mysticalagradditions.gaia_spirit": "가이아의 영혼",
    "crop.mysticalagradditions.awakened_draconium": "각성 드라코늄",
    "crop.mysticalagradditions.neutronium": "뉴트로늄",
    "crop.mysticalagradditions.nitro_crystal": "니트로 수정",
}

QUEST_OVERRIDES = {
    "quest.4821419D44F8083F.quest_desc": [
        "&9성장 가속기&r는 경작지 바로 아래에 놓으면 씨앗의 성장 속도를 조금 높입니다. 각 등급은 위쪽으로 가속할 수 있는 범위가 다르며, 인퍼륨의 범위가 9블록으로 가장 짧습니다. ",
        "",
        "참고: 모든 등급의 성장 가속기는 같은 빈도로 성장 틱을 제공합니다. 높은 등급은 범위가 더 넓어 한 작물 아래에 더 많이 쌓을 수 있습니다. 성장 가속기가 최대 범위 안에 있기만 하면 어느 등급을 사용해도 됩니다.",
    ],
    "quest.6D0A876D4E4D35AB.quest_desc": [
        "크리에이티브 에센스는 &6ATM의 별&r을 제작하는 데 필요합니다."
    ],
}

CUSTOM_NAMES = {
    "allthemodium.json": "Allthemodium",
    "azure_silver.json": "하늘빛 은",
    "black_quartz.json": "검은 석영",
    "crimson_iron.json": "진홍빛 철",
    "darkstone.json": "어둠돌",
    "entro.json": "엔트로",
    "kivi.json": "키비",
    "sky_steel.json": "스카이 스틸",
    "unexplored_wood.json": "미탐사 목재",
    "unobtainium.json": "Unobtainium",
    "vibranium.json": "Vibranium",
    "xychorium_gem.json": "자이코륨 보석",
    "magical.json": "§b마법",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_jar(instance: Path, prefix: str) -> Path:
    matches = [
        p for p in (instance / "mods").glob("*.jar") if p.name.startswith(prefix)
    ]
    if len(matches) != 1:
        raise RuntimeError(f"JAR을 하나로 확정할 수 없습니다: {prefix} -> {matches}")
    return matches[0]


def load_json(archive: ZipFile, name: str) -> dict[str, object]:
    if name not in archive.namelist():
        return {}

    def reject(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"중복 키가 있습니다: {name}:{key}")
            result[key] = value
        return result

    value = json.loads(archive.read(name).decode("utf-8-sig"), object_pairs_hook=reject)
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {name}")
    return value


def normalize_existing(value: object) -> object:
    if not isinstance(value, str):
        return value
    replacements = (
        ("신비한 농업", "Mystical Agriculture"),
        ("신비 농업", "Mystical Agriculture"),
        ("신비농업", "Mystical Agriculture"),
        ("부적", "증강"),
        ("증가 슬롯", "증강 슬롯"),
        ("정수", "에센스"),
    )
    for old, new in replacements:
        value = value.replace(old, new)
    return value


def translate_augment(key: str, english: str) -> str:
    short = key.removeprefix("augment.mysticalagriculture.")
    description = short.endswith(".description")
    base = short.removesuffix(".description")
    parts = base.rsplit("_", 1)
    level = ROMAN.get(parts[-1]) if len(parts) == 2 else None
    name_key = parts[0] if level else base
    name = AUGMENT_NAMES[name_key]
    if not description:
        return f"{name} {level}" if level else name
    if name_key == "absorption":
        hearts = {"I": 2, "II": 4, "III": 6, "IV": 8, "V": 10}[level]
        return f"8분마다 흡수 체력 {hearts}칸을 부여합니다."
    if name_key == "health_boost":
        hearts = {"I": 2, "II": 4, "III": 6, "IV": 8, "V": 10}[level]
        return f"최대 생명력이 하트 {hearts}칸 증가합니다."
    if name_key.endswith("_aoe"):
        size = {"I": "3x3", "II": "5x5", "III": "7x7", "IV": "9x9"}[level]
        action = " 웅크리는 동안" if name_key in {"pathing_aoe", "tilling_aoe"} else ""
        return f"{action.strip() + ' ' if action else ''}{name}를 {size}으로 늘립니다."
    grants = {
        "luck": "행운",
        "night_vision": "야간 투시",
        "water_breathing": "수중 호흡",
        "jump_boost": "점프 강화",
        "speed": "신속",
        "fire_resistance": "화염 저항",
        "strength": "힘",
        "haste": "성급함",
        "slow_falling": "느린 낙하",
    }
    if name_key in grants:
        suffix = f" {level}" if level else ""
        return f"{grants[name_key]}{suffix} 효과를 부여합니다."
    prevents = {
        "nausea_resistance": "멀미",
        "blindness_resistance": "실명",
        "weakness_resistance": "나약함",
        "slowness_resistance": "구속",
        "poison_resistance": "독",
        "mining_fatigue_resistance": "채굴 피로",
        "hunger_resistance": "허기",
        "wither_resistance": "시듦",
    }
    if name_key in prevents:
        return f"{prevents[name_key]} 효과를 받지 않습니다."
    exact = {
        "step_assist": "점프하지 않고 1블록 높이의 단차를 오를 수 있습니다.",
        "no_fall_damage": "모든 추락 피해를 무효화합니다.",
        "flight": "크리에이티브 비행을 부여합니다.",
    }
    return exact[name_key]


def add_generated_language(data: dict[str, object], english: dict[str, object]) -> None:
    for key, source in english.items():
        if key.startswith("crop.mysticalagriculture.") and isinstance(source, str):
            data[key] = CROP_NAMES.get(source, source)
        elif key.startswith("augment.mysticalagriculture.") and isinstance(source, str):
            data[key] = translate_augment(key, source)

    tools = {
        "bow": "활",
        "crossbow": "쇠뇌",
        "shears": "가위",
        "fishing_rod": "낚싯대",
        "sickle": "낫",
        "scythe": "대낫",
        "sword": "검",
        "pickaxe": "곡괭이",
        "shovel": "삽",
        "axe": "도끼",
        "hoe": "괭이",
        "staff": "지팡이",
        "watering_can": "물뿌리개",
        "helmet": "투구",
        "chestplate": "흉갑",
        "leggings": "레깅스",
        "boots": "부츠",
    }
    for key, source in english.items():
        if key in data and data[key] != source:
            continue
        if key.startswith("item.mysticalagriculture.") and isinstance(source, str):
            for tier_en, tier_ko in sorted(
                TIER_NAMES.items(), key=lambda row: -len(row[0])
            ):
                if source.startswith(tier_en + " "):
                    rest = source[len(tier_en) + 1 :]
                    if rest == "Machine Upgrade":
                        data[key] = f"{tier_ko} 기계 업그레이드"
                    elif rest == "Awakened Machine Supremium Upgrade":
                        data[key] = "각성 수프레뮴 기계 업그레이드"
                    else:
                        for suffix, korean in tools.items():
                            if key.endswith("_" + suffix):
                                data[key] = f"{tier_ko} {korean}"
                                break
                    break


def add_book_overrides(data: dict[str, object]) -> None:
    data.update(BOOK_OVERRIDES)
    for effect, (effect_ko, slot) in RESISTANCE_BOOK.items():
        key = f"book.mysticalagriculture.entry.{effect}_resistance_augment"
        data[key] = f"{effect_ko} 저항 증강"
        data[key + ".page.1"] = (
            f"{effect_ko} 저항 증강은 방어구를 착용한 동안 {effect_ko} 효과를 "
            f"받지 않게 하는 {slot} 증강입니다."
        )
    simple = {
        "luck": ("행운", "낚시나 전리품 상자에서 얻는 전리품의 품질을 높입니다."),
        "haste": ("성급함", "채굴 속도를 높입니다."),
        "slow_falling": (
            "느린 낙하",
            "천천히 떨어지게 합니다. $(br2)Shift 키를 누르면 이 효과를 잠시 무효화할 수 있습니다.",
        ),
    }
    for name, (title, sentence) in simple.items():
        key = f"book.mysticalagriculture.entry.{name}_augment"
        data[key] = f"{title} 증강"
        data[key + ".page.1"] = f"{title} 증강은 방어구를 착용한 동안 {sentence}"


def build_language(instance: Path) -> tuple[list[dict[str, object]], set[str]]:
    rows: list[dict[str, object]] = []
    intentional: set[str] = set()
    for prefix, namespace in TARGETS:
        jar_path = find_jar(instance, prefix)
        with ZipFile(jar_path) as archive:
            english = load_json(archive, f"assets/{namespace}/lang/en_us.json")
            candidate = load_json(archive, f"assets/{namespace}/lang/ko_kr.json")
        data = {
            key: normalize_existing(candidate.get(key, value))
            for key, value in english.items()
        }
        if namespace == "mysticalagriculture":
            add_generated_language(data, english)
            data.update(
                {key: value for key, value in LANG_OVERRIDES.items() if key in english}
            )
            add_book_overrides(data)
        else:
            data.update(
                {key: value for key, value in LANG_OVERRIDES.items() if key in english}
            )
            data.update(
                {
                    key: value
                    for key, value in AGRADDITIONS_OVERRIDES.items()
                    if key in english
                }
            )
            for key, source in english.items():
                if not isinstance(source, str):
                    continue
                for tier_en, tier_ko in TIER_NAMES.items():
                    if source == f"{tier_en} Apple":
                        data[key] = f"{tier_ko} 사과"
                    elif source == f"Molten {tier_en} Bucket":
                        data[key] = f"용융 {tier_ko} 양동이"
                    elif source == f"Molten {tier_en}":
                        data[key] = f"용융 {tier_ko}"
                    elif source == tier_en:
                        data[key] = tier_ko
        for key, source in english.items():
            if (
                key.startswith("crop.mysticalagriculture.")
                and source in INTENTIONAL_CROP_ORIGINALS
            ):
                intentional.add(key)
        work = WORK_ROOT / namespace / "ko_kr.json"
        output = OUTPUT_ASSETS / namespace / "lang/ko_kr.json"
        for path in (work, output):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        reused = sum(
            key in candidate and candidate[key] == data[key] for key in english
        )
        corrected = sum(
            key in candidate and candidate[key] != data[key] for key in english
        )
        new = sum(key not in candidate for key in english)
        rows.append(
            {
                "namespace": namespace,
                "jar": jar_path.name,
                "english_keys": len(english),
                "existing_korean_reused": reused,
                "existing_korean_corrected": corrected,
                "newly_translated": new,
                "output": output.relative_to(PROJECT_ROOT).as_posix(),
            }
        )
    return rows, intentional


def build_customization(instance: Path) -> list[str]:
    source_root = instance / "config/mysticalcustomization"
    changed: list[str] = []
    for relative in [
        Path("crops") / name for name in CUSTOM_NAMES if name != "magical.json"
    ] + [Path("tiers/magical.json")]:
        source = source_root / relative
        data = json.loads(source.read_text(encoding="utf-8-sig"))
        expected = CUSTOM_NAMES[relative.name]
        if "name" not in data:
            raise KeyError(f"name 표시 필드가 없습니다: {source}")
        data["name"] = expected
        output = OUTPUT_OVERRIDES / "config/mysticalcustomization" / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        changed.append(output.relative_to(PROJECT_ROOT).as_posix())
    return changed


def build_kubejs(instance: Path) -> dict[str, object]:
    relative = Path("kubejs/client_scripts/tooltips.js")
    source = instance / relative
    text = source.read_text(encoding="utf-8-sig")
    replacements = {
        'Text.of("§cDisabled for Fake Player")': 'Text.of("§c가짜 플레이어로 사용할 수 없습니다")',
        'Text.of("§c(Blocks like Modular Routers, Clickers, etc)")': 'Text.of("§c(Modular Routers, Clickers 같은 블록 포함)")',
    }
    output_text = text
    for old, new in replacements.items():
        if output_text.count(old) != 1:
            raise ValueError(f"KubeJS 원문을 하나로 확정하지 못했습니다: {old}")
        output_text = output_text.replace(old, new)
    output = OUTPUT_OVERRIDES / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(output_text, encoding="utf-8")
    return {
        "source": relative.as_posix(),
        "output": output.relative_to(PROJECT_ROOT).as_posix(),
        "translated_literals": len(replacements),
        "output_sha256": sha256(output),
    }


def quest_normalize(value: snbt.TranslationValue) -> snbt.TranslationValue:
    if isinstance(value, str):
        return normalize_existing(value)
    return [normalize_existing(part) for part in value]


def build_quests(instance: Path) -> dict[str, object]:
    lang_root = instance / "config/ftbquests/quests/lang"
    english = snbt.parse_language_snbt(
        lang_root / f"en_us/chapters/{QUEST_CHAPTER}.snbt_merged"
    )
    installed = snbt.parse_language_snbt(
        lang_root / f"ko_kr/chapters/{QUEST_CHAPTER}.snbt_merged"
    )
    overrides = {
        key: quest_normalize(installed.get(key, source))
        for key, source in english.items()
    }
    overrides.update(QUEST_OVERRIDES)
    work_en = WORK_ROOT / "quest_english.json"
    work_ko = WORK_ROOT / "quest_overrides.json"
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    work_en.write_text(
        json.dumps(english, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    work_ko.write_text(
        json.dumps(overrides, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    base = QUEST_OUTPUT if QUEST_OUTPUT.is_file() else lang_root / "ko_kr.snbt"
    merged = snbt.merge_into_full_snbt(base, overrides)
    QUEST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    reparsed = snbt.parse_language_snbt(QUEST_OUTPUT)
    if any(reparsed.get(key) != value for key, value in overrides.items()):
        raise ValueError("Mystical Agriculture 퀘스트 누적 병합 결과가 다릅니다.")
    return {
        "chapter": QUEST_CHAPTER,
        "display_keys": len(english),
        "existing_korean_reused": sum(
            installed.get(k) == v for k, v in overrides.items()
        ),
        "existing_korean_corrected": sum(
            k in installed and installed[k] != v for k, v in overrides.items()
        ),
        "newly_translated": sum(k not in installed for k in overrides),
        "internal_original_keys": [
            "task.518B9569DCE0A771.title",
            "task.773CA1FDC4CEFCEF.title",
        ],
        "output": QUEST_OUTPUT.relative_to(PROJECT_ROOT).as_posix(),
    }


def validate_value(key: str, source: object, target: object, errors: list[str]) -> None:
    if type(source) is not type(target):
        errors.append(f"자료형 불일치: {key}")
        return
    if not isinstance(source, str):
        if source != target:
            errors.append(f"비문자 값 변경: {key}")
        return
    assert isinstance(target, str)
    if PLACEHOLDER.findall(source) != PLACEHOLDER.findall(target):
        errors.append(f"자리표시자 불일치: {key}")
    if Counter(FORMAT_CODE.findall(source)) != Counter(FORMAT_CODE.findall(target)):
        errors.append(f"서식 코드 불일치: {key}")
    if source.count("\n") != target.count("\n"):
        errors.append(f"줄바꿈 수 불일치: {key}")
    source_patchouli = Counter(re.findall(r"\$\([^)]*\)", source))
    target_patchouli = Counter(re.findall(r"\$\([^)]*\)", target))
    if source_patchouli != target_patchouli:
        errors.append(f"Patchouli 태그 불일치: {key}")


def verify_language(
    instance: Path, intentional: set[str]
) -> tuple[list[dict[str, object]], list[str]]:
    rows: list[dict[str, object]] = []
    errors: list[str] = []
    all_names: dict[str, list[str]] = {}
    for prefix, namespace in TARGETS:
        jar_path = find_jar(instance, prefix)
        with ZipFile(jar_path) as archive:
            english = load_json(archive, f"assets/{namespace}/lang/en_us.json")
        path = WORK_ROOT / namespace / "ko_kr.json"
        if path.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"UTF-8 BOM이 있습니다: {path}")
        korean = json.loads(path.read_text(encoding="utf-8"))
        if list(korean) != list(english):
            errors.append(f"키 또는 순서 불일치: {namespace}")
        for key, source in english.items():
            if key not in korean:
                continue
            validate_value(key, source, korean[key], errors)
            if (
                isinstance(source, str)
                and korean[key] == source
                and LATIN_WORD.search(source)
                and key not in intentional
                and source not in {"Mystical Agriculture", "Mystical Agradditions"}
            ):
                errors.append(f"분류되지 않은 영어 유지 키: {key}={source}")
            if key.startswith(("item.", "block.")) and isinstance(korean[key], str):
                all_names.setdefault(korean[key], []).append(key)
        output = OUTPUT_ASSETS / namespace / "lang/ko_kr.json"
        if sha256(path) != sha256(output):
            errors.append(f"작업본과 산출물 해시가 다릅니다: {namespace}")
        rows.append(
            {"namespace": namespace, "keys": len(english), "validation": "passed"}
        )
    collisions = {
        name: keys
        for name, keys in all_names.items()
        if len(keys) > 1
        and not all("mysticalagradditions.molten_" in key for key in keys)
    }
    if collisions:
        errors.append(f"아이템·블록 이름 충돌: {collisions}")
    return rows, errors


def verify_related(
    instance: Path, translations: dict[str, object]
) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    installed = [find_jar(instance, prefix).name for prefix, _ in TARGETS]
    installed.extend(find_jar(instance, prefix).name for prefix in RELATED_JARS)
    guide_files = 0
    guide_keys: set[str] = set()
    advancement_files = 0
    advancement_keys: set[str] = set()
    for prefix in ("MysticalAgriculture-", "MysticalAgradditions-"):
        jar = find_jar(instance, prefix)
        with ZipFile(jar) as archive:
            for name in archive.namelist():
                if "patchouli_books/guide/en_us/" in name and name.endswith(".json"):
                    guide_files += 1
                    raw = archive.read(name).decode("utf-8")
                    guide_keys.update(
                        re.findall(r'"(book\.mysticalagriculture\.[^"]+)"', raw)
                    )
                if "/advancement/" in name and name.endswith(".json"):
                    advancement_files += 1
                    raw = archive.read(name).decode("utf-8")
                    advancement_keys.update(
                        re.findall(r'"translate"\s*:\s*"([^"]+)"', raw)
                    )
    missing_guide = sorted(guide_keys - set(translations))
    missing_advancements = sorted(advancement_keys - set(translations))
    if missing_guide:
        errors.append(f"가이드 번역 키 누락: {missing_guide}")
    if missing_advancements:
        errors.append(f"발전 과제 번역 키 누락: {missing_advancements}")

    botany = find_jar(instance, "botanypotsmystical-")
    with ZipFile(botany) as archive:
        botany_recipes = [
            n
            for n in archive.namelist()
            if n.startswith("data/botanypots/recipe/") and n.endswith(".json")
        ]
        display_literals = []
        for name in botany_recipes:
            data = json.loads(archive.read(name).decode("utf-8"))
            for key in ("name", "title", "description", "text"):
                if key in data:
                    display_literals.append(f"{name}:{key}")
    if display_literals:
        errors.append(
            f"Botany Pots Mystical 레시피에 예상 밖 표시 literal이 있습니다: {display_literals}"
        )

    customization_files = []
    for filename, expected in CUSTOM_NAMES.items():
        relative = (
            Path("tiers/magical.json")
            if filename == "magical.json"
            else Path("crops") / filename
        )
        output = OUTPUT_OVERRIDES / "config/mysticalcustomization" / relative
        data = json.loads(output.read_text(encoding="utf-8"))
        if data.get("name") != expected:
            errors.append(f"Mystical Customization 이름이 다릅니다: {relative}")
        customization_files.append(relative.as_posix())
    if len(set(CUSTOM_NAMES.values())) != len(CUSTOM_NAMES):
        errors.append("Mystical Customization 이름 충돌이 있습니다.")

    return {
        "installed": installed,
        "guides": {
            "files_checked": guide_files,
            "translation_keys_checked": len(guide_keys),
            "missing": len(missing_guide),
        },
        "advancements": {
            "files_checked": advancement_files,
            "translation_keys_checked": len(advancement_keys),
            "missing": len(missing_advancements),
        },
        "botany_pots_mystical": {
            "recipes_checked": len(botany_recipes),
            "display_literals": len(display_literals),
        },
        "mystical_customization": {
            "display_name_files": customization_files,
            "names": len(CUSTOM_NAMES),
        },
    }, errors


def verify_quests(
    instance: Path, translations: dict[str, object]
) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    english = json.loads((WORK_ROOT / "quest_english.json").read_text(encoding="utf-8"))
    overrides = json.loads(
        (WORK_ROOT / "quest_overrides.json").read_text(encoding="utf-8")
    )
    output = snbt.parse_language_snbt(QUEST_OUTPUT)
    internal = {
        "task.518B9569DCE0A771.title",
        "task.773CA1FDC4CEFCEF.title",
        "quest.54735C5FCD2077B3.title",
    }
    for key, source in english.items():
        target = overrides.get(key)
        if output.get(key) != target:
            errors.append(f"퀘스트 누적 출력 불일치: {key}")
        if target is not None:
            errors.extend(snbt.validate_value(key, source, target))
        if (
            source == target
            and LATIN_WORD.search(snbt.flatten(source))
            and key not in internal
        ):
            errors.append(f"분류되지 않은 퀘스트 영어 유지 키: {key}")

    chapters, _ = quest_audit.parse_chapters(instance / "config/ftbquests/quests")
    chapter = next(
        (c for c in chapters if c["filename"] == QUEST_CHAPTER + ".snbt"), None
    )
    if chapter is None:
        errors.append("Mystical Agriculture 전용 챕터 구조를 찾지 못했습니다.")
        return {}, errors
    target_namespaces = {
        "mysticalagriculture",
        "mysticalagradditions",
        "mysticalcustomization",
        "botanypotsmystical",
    }
    related = [
        (c, q, t)
        for c in chapters
        if c is not chapter
        for q in c["quests"]
        for t in q["tasks"]
        if t["item_id"].partition(":")[0] in target_namespaces
    ]
    custom_names = [
        t for q in chapter["quests"] for t in q["tasks"] if t["custom_name"]
    ]
    if custom_names:
        errors.append(f"전용 챕터에 custom_name이 있습니다: {custom_names}")
    redundant = []
    explicit = 0
    for q in chapter["quests"]:
        for task in q["tasks"]:
            key = f"task.{task['id']}.title"
            if key not in english:
                continue
            explicit += 1
            if task["type"] == "item" and len(q["tasks"]) == 1:
                item_id = task["item_id"]
                namespace, _, item_path = item_id.partition(":")
                item_name = translations.get(
                    f"item.{namespace}.{item_path}",
                    translations.get(f"block.{namespace}.{item_path}", ""),
                )
                if (
                    item_name
                    and quest_audit.strip_formatting(snbt.flatten(overrides[key]))
                    == item_name
                ):
                    redundant.append(task["id"])
    if redundant:
        errors.append(
            f"단일 ItemTask 이름을 반복하는 task.title이 있습니다: {redundant}"
        )
    if any(t["custom_name"] for _, _, t in related):
        errors.append("전용 챕터 밖 직접 관련 Task에 custom_name이 있습니다.")
    return {
        "chapter": chapter["filename"],
        "quests_checked": len(chapter["quests"]),
        "tasks_checked": sum(len(q["tasks"]) for q in chapter["quests"]),
        "display_keys_checked": len(english),
        "explicit_task_titles_checked": explicit,
        "internal_original_task_titles": len(internal),
        "custom_names": len(custom_names),
        "redundant_single_item_task_titles": len(redundant),
        "related_tasks_outside_chapter_checked": len(related),
    }, errors


def command_build(instance: Path) -> int:
    language_rows, intentional = build_language(instance)
    customization = build_customization(instance)
    kubejs = build_kubejs(instance)
    quests = build_quests(instance)
    build_report = {
        "scope": "Mystical Agriculture family",
        "languages": language_rows,
        "intentional_original_crop_keys": sorted(intentional),
        "customization_outputs": customization,
        "kubejs": kubejs,
        "ftbquests": quests,
    }
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    (WORK_ROOT / "build_report.json").write_text(
        json.dumps(build_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(build_report, ensure_ascii=False, indent=2))
    return 0


def verify_deployment(
    instance: Path, manifest_path: Path | None
) -> tuple[dict[str, object], list[str]]:
    if manifest_path is None:
        return {"status": "not_checked"}, ["적용 매니페스트가 지정되지 않았습니다."]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target = next(
        (row for row in manifest["targets"] if Path(row["target_root"]) == instance),
        None,
    )
    if target is None:
        return {"status": "not_found"}, ["적용 매니페스트에 현재 인스턴스가 없습니다."]
    expected_sources = {
        "config/ftbquests/quests/lang/ko_kr.snbt": QUEST_OUTPUT,
        "kubejs/client_scripts/tooltips.js": OUTPUT_OVERRIDES
        / "kubejs/client_scripts/tooltips.js",
        "resourcepacks/ATM10_Korean/assets/mysticalagriculture/lang/ko_kr.json": (
            OUTPUT_ASSETS / "mysticalagriculture/lang/ko_kr.json"
        ),
        "resourcepacks/ATM10_Korean/assets/mysticalagradditions/lang/ko_kr.json": (
            OUTPUT_ASSETS / "mysticalagradditions/lang/ko_kr.json"
        ),
    }
    for filename in CUSTOM_NAMES:
        relative = (
            Path("tiers/magical.json")
            if filename == "magical.json"
            else Path("crops") / filename
        )
        expected_sources[
            (Path("config/mysticalcustomization") / relative).as_posix()
        ] = OUTPUT_OVERRIDES / "config/mysticalcustomization" / relative
    errors: list[str] = []
    changed = set(target["changed_paths"])
    if changed != set(expected_sources):
        errors.append(f"Mystical 계열 적용 경로가 계획과 다릅니다: {sorted(changed)}")
    if target["unexpected_changes"]:
        errors.append("적용 매니페스트에 계획 밖 변경이 기록되었습니다.")
    hash_matches = 0
    for relative, source in expected_sources.items():
        live = instance / relative
        if not live.is_file() or sha256(source) != sha256(live):
            errors.append(f"실제 적용 파일 해시가 산출물과 다릅니다: {relative}")
        else:
            hash_matches += 1
    return {
        "status": "applied_and_verified" if not errors else "invalid",
        "target": str(instance),
        "backup_manifest": str(manifest_path),
        "changed_paths": sorted(changed),
        "hash_matches": hash_matches,
        "unexpected_changes": target["unexpected_changes"],
    }, errors


def command_verify(instance: Path, manifest_path: Path | None) -> int:
    build = json.loads((WORK_ROOT / "build_report.json").read_text(encoding="utf-8"))
    intentional = set(build["intentional_original_crop_keys"])
    language_rows, errors = verify_language(instance, intentional)
    translations: dict[str, object] = {}
    for _, namespace in TARGETS:
        translations.update(
            json.loads(
                (WORK_ROOT / namespace / "ko_kr.json").read_text(encoding="utf-8")
            )
        )
    related, related_errors = verify_related(instance, translations)
    quests, quest_errors = verify_quests(instance, translations)
    deployment, deployment_errors = verify_deployment(instance, manifest_path)
    errors.extend(related_errors)
    errors.extend(quest_errors)
    errors.extend(deployment_errors)
    report = {
        "scope": "Mystical Agriculture family completion",
        "languages": language_rows,
        "related_content": related,
        "ftbquests": quests,
        "kubejs_literals_checked": build["kubejs"]["translated_literals"],
        "deployment": deployment,
        "remaining": len(errors),
        "validation_errors": len(errors),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "family_validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    counts = {
        "language_english_keys": sum(row["english_keys"] for row in build["languages"]),
        "language_existing_korean_reused": sum(
            row["existing_korean_reused"] for row in build["languages"]
        ),
        "language_existing_korean_corrected": sum(
            row["existing_korean_corrected"] for row in build["languages"]
        ),
        "language_newly_translated": sum(
            row["newly_translated"] for row in build["languages"]
        ),
        "quest_display_keys": build["ftbquests"]["display_keys"],
        "customization_literals": len(CUSTOM_NAMES),
        "kubejs_literals": build["kubejs"]["translated_literals"],
        "remaining": len(errors),
    }
    completion = {
        "scope": "Mystical Agriculture family",
        "installed": related.get("installed", []),
        "counts": counts,
        "related_content": related,
        "deployment": deployment,
        "review_items": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "family_completion.json").write_text(
        json.dumps(completion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    return (
        command_build(instance)
        if args.command == "build"
        else command_verify(instance, args.manifest)
    )


if __name__ == "__main__":
    raise SystemExit(main())
