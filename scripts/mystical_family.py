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
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?%?")
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
    "Sky Stone": "천령석",
    "Certus Quartz": "서투스 석영",
    "Fluix": "플루익스",
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
    "block.mysticalagriculture.witherproof_block": "위더 방호 블록",
    "block.mysticalagriculture.witherproof_bricks": "위더 방호 벽돌",
    "block.mysticalagriculture.witherproof_glass": "위더 방호 유리",
    "item.mysticalagriculture.awakened_supremium_essence": "각성 수프레뮴 에센스",
    "item.mysticalagriculture.awakened_supremium_ingot": "각성 수프레뮴 주괴",
    "item.mysticalagriculture.awakened_supremium_nugget": "각성 수프레뮴 조각",
    "item.mysticalagriculture.awakened_supremium_gemstone": "각성 수프레뮴 보석",
    "item.mysticalagriculture.cognizant_dust": "인지의 가루",
    "item.mysticalagriculture.fertilized_essence": "비옥한 에센스",
    "item.mysticalagriculture.prosperity_seed_base": "번영 씨앗 기반재",
    "item.mysticalagriculture.soulium_seed_base": "소울륨 씨앗 기반재",
    "item.mysticalagriculture.honey_agglomeratio": "꿀 응집체",
    "item.mysticalagriculture.mystical_flower_agglomeratio": "신비로운 꽃 응집체",
    "item.mysticalagriculture.wand": "마법봉",
    "item.mysticalagriculture.diamond_sickle": "다이아몬드 낫",
    "item.mysticalagriculture.diamond_scythe": "다이아몬드 대낫",
    "item.mysticalagriculture.upgrade_base": "기계 업그레이드 기반재",
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
    "tooltip.mysticalagriculture.secondary_chance": "2차 확률: %s",
    "tooltip.mysticalagriculture.requires_effective_farmland": "%s에 심어야 합니다",
    "tooltip.mysticalagriculture.invalid_biome": "유효하지 않은 생물군계",
    "tooltip.mysticalagriculture.machine_speed": "작동 속도: %st",
    "tooltip.mysticalagriculture.machine_fuel_usage": "연료 사용량: %s",
    "tooltip.mysticalagriculture.machine_scan_fuel_usage": "탐색 연료 사용량: %s",
    "tooltip.mysticalagriculture.machine_area": "범위: %s",
    "tooltip.mysticalagriculture.machine_spawn_radius": "소환 반경: %s",
    "tooltip.mysticalagriculture.passive_soulium_dagger": "비적대적 생물에게서 추가 영혼을 얻습니다.",
    "tooltip.mysticalagriculture.hostile_soulium_dagger": "적대적 생물에게서 추가 영혼을 얻습니다.",
    "tooltip.mysticalagriculture.creative_soulium_dagger": "모든 생물에게서 *무한한* 영혼을 얻습니다.",
    "tooltip.mysticalagriculture.passive_attuned": "비적대적 조율",
    "tooltip.mysticalagriculture.hostile_attuned": "적대 조율",
    "tooltip.mysticalagriculture.creative_attuned": "크리에이티브 조율",
    "tooltip.mysticalagriculture.activate_with_redstone": "마법봉이나 레드스톤 신호로 활성화합니다.",
    "tooltip.mysticalagriculture.fertilized_essence_chance": "드롭 확률: %s",
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
    "augmentType.mysticalagriculture.leggings": "레깅스",
    "item.mysticalagriculture.inferium_leggings": "인퍼륨 레깅스",
    "item.mysticalagriculture.prudentium_leggings": "프루덴튬 레깅스",
    "item.mysticalagriculture.tertium_leggings": "터튬 레깅스",
    "item.mysticalagriculture.imperium_leggings": "임퍼륨 레깅스",
    "item.mysticalagriculture.supremium_leggings": "수프레뮴 레깅스",
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
    "book.mysticalagriculture.category.advances.description": "이 장에서는 기본 자원 생산 체계를 갖춘 뒤 이용할 수 있는 심화 콘텐츠를 설명합니다.",
    "book.mysticalagriculture.category.machines.description": "이 장에서는 Mystical Agriculture의 여러 기계 블록을 설명합니다.",
    "book.mysticalagriculture.category.augments.description": "이 장에서는 각 증강의 기능을 설명합니다.",
    "book.mysticalagriculture.entry.inferium_essence.page.1": "인퍼륨 에센스는 Mystical Agriculture의 두 가지 기본 재료 중 하나이며 모드의 거의 모든 아이템을 만드는 데 사용됩니다. 적대적·비적대적 몹을 처치하거나, 광석을 채굴하거나, 작물을 재배해 $(bold)일반적으로$() 얻을 수 있습니다.",
    "book.mysticalagriculture.entry.overworld_ores.page.1": "인퍼륨 광석은 오버월드의 Y -32에서 64 사이에 $(bold)일반적으로$() 생성됩니다.",
    "book.mysticalagriculture.entry.overworld_ores.page.2": "번영 광석은 오버월드의 Y -60에서 24 사이에 $(bold)일반적으로$() 생성됩니다.",
    "book.mysticalagriculture.entry.resource_crops.page.1": "자원 작물은 Mystical Agriculture의 핵심 콘텐츠입니다. 다만 다음과 같은 특성이 있습니다. $(br2)$(li)뼛가루로 성장시킬 수 없습니다. $(li)$(l:basics/essence_farmland)에센스 경작지$()에 심어야만 두 번째 씨앗을 떨어뜨릴 수 있습니다.",
    "book.mysticalagriculture.entry.essence_farmland.page.1": "에센스 경작지는 여러 방식으로 Mystical Agriculture 작물의 생산 효율을 높입니다. 자세한 효과는 다음 페이지에 나옵니다. $(br2)에센스를 들고 월드의 경작지를 오른쪽 클릭하거나 조합해서 만들 수 있습니다.",
    "book.mysticalagriculture.entry.watering_can.page.1": "물뿌리개는 수작업*으로 작물의 성장을 가속합니다. 물 원천 블록을 오른쪽 클릭하면 물을 채울 수 있습니다.",
    "book.mysticalagriculture.entry.infusion_altar.page.1": "주입 제단은 Mystical Agriculture 씨앗을 만드는 데 $(bold)일반적으로$() 사용하는 조합 구조입니다. 주입 제단 1개와 주입 받침대 8개로 구성됩니다. $(br2)조합법에 맞게 재료를 놓은 뒤 마법봉이나 레드스톤 신호로 제단을 활성화하세요.",
    "book.mysticalagriculture.entry.fertilized_essence": "비옥한 에센스",
    "book.mysticalagriculture.entry.fertilized_essence.page.1": "비옥한 에센스는 $(bold)인퍼륨을 제외한$() 모든 $(l:basics/resource_crops)자원 작물$()에서 $(bold)일반적으로$() 떨어집니다. 뼛가루처럼 작동하며 $(l:basics/resource_crops)자원 작물$()에도 사용할 수 있습니다! $(br2)$(l:advances/mystical_fertilizer)신비로운 비료$()를 더 효율적으로 만드는 재료로도 사용됩니다.",
    "book.mysticalagriculture.entry.master_infusion_crystal.page.1": "마스터 주입 수정은 내구도가 무한합니다. 이게 갖고 싶으시죠? 다 알아요.",
    "book.mysticalagriculture.entry.essence_watering_cans.page.1": "일반 $(l:basics/watering_can)물뿌리개$()를 에센스와 $(l:advances/mystical_fertilizer)신비로운 비료$()로 업그레이드하면 농사가 훨씬 편해집니다. $(br2)업그레이드된 물뿌리개는 범위와 성장 가속 속도가 증가합니다. 블록을 겨냥하지 않은 상태에서 물뿌리개를 들고 Shift + 오른쪽 클릭하면 자동 물 주기를 켜거나 끌 수 있습니다.",
    "book.mysticalagriculture.entry.soulstone.page.1": "영혼석은 네더의 모든 Y 높이에서 큰 광맥으로 생성되는 특별한 돌입니다. $(br2)여러 변형이 있는 장식 블록이며, $(l:souls/witherproof_blocks)위더 방호 블록$()을 만드는 데도 필요합니다.",
    "book.mysticalagriculture.entry.soulstone.page.2": "제련하면 여러 용도로 쓰이는 영혼 가루를 얻을 수도 있습니다.",
    "book.mysticalagriculture.entry.witherproof_blocks": "위더 방호 블록",
    "book.mysticalagriculture.entry.witherproof_blocks.page.1": "위더 방호 블록은 위더가 파괴할 수 없어 보스를 안전하게 공략할 때 매우 유용합니다. $(br2)엔더 드래곤의 피해에도 면역이지만, 엔더 드래곤은 여전히 블록을 통과해 날 수 있습니다.",
    "book.mysticalagriculture.entry.seed_reprocessors.page.1": "씨앗 재처리기는 남는 씨앗을 해당 에센스로 변환합니다. 고체 연료로 작동하며 내부에 동력 저장 공간이 있습니다.",
    "book.mysticalagriculture.entry.essence_tools.page.1": "다이아몬드* 도구를 에센스로 업그레이드하면 내구도와 채굴 속도가 향상되고 $(l:tinkering/augments)증강$()을 장착할 수 있습니다. $(br2)에센스 도구는 해당 에센스 주괴를 사용해 모루에서 수리할 수 있으며, 각각 증강 슬롯이 1개 있습니다.",
    "book.mysticalagriculture.entry.essence_armor.page.1": "다이아몬드* 방어구를 에센스로 업그레이드하면 내구도와 방어력이 향상되고 $(l:tinkering/augments)증강$()을 장착할 수 있습니다. $(br2)에센스 방어구는 해당 에센스 주괴를 사용해 모루에서 수리할 수 있으며, 각 부위에 증강 슬롯이 1개 있습니다.",
    "book.mysticalagriculture.entry.tinkering_table.page.1": "땜장이 작업대는 $(l:tinkering/essence_tools)에센스 도구$()와 $(l:tinkering/essence_armor)에센스 방어구$()에 $(l:tinkering/augments)증강$()을 장착하는 데 사용됩니다.",
    "book.mysticalagriculture.entry.augments.page.1": "증강은 $(l:tinkering/essence_tools)에센스 도구$()와 $(l:tinkering/essence_armor)에센스 방어구$()에 장착하는 업그레이드입니다. $(l:tinkering/tinkering_table)땜장이 작업대$()에서 장비에 장착할 수 있습니다. $(br2)각 증강에는 장착 가능한 장비의 최소 등급이 정해져 있습니다. ",
    "book.mysticalagriculture.entry.augments.page.2": "이 가이드의 '증강' 장에서 각 증강의 기능을 확인할 수 있습니다.",
    "book.mysticalagriculture.entry.health_boost_augment.page.1": "생명력 강화 증강은 방어구를 착용한 동안 착용자의 하트를 2~10개 늘리는 방어구 증강입니다.",
    "book.mysticalagriculture.entry.night_vision_augment.page.1": "야간 투시 증강은 방어구를 착용한 동안 야간 투시 효과를 부여하는 투구 증강입니다.",
    "book.mysticalagriculture.entry.water_breathing_augment.page.1": "수중 호흡 증강은 방어구를 착용한 동안 수중 호흡 효과를 부여하는 투구 증강입니다.",
    "book.mysticalagriculture.entry.pathing_aoe_augment": "길 만들기 범위 증강",
    "book.mysticalagriculture.entry.speed_augment.page.1": "신속 증강은 방어구를 착용한 동안 이동 속도와 비행 속도를 높이는 레깅스 증강입니다.",
    "book.mysticalagriculture.entry.mining_aoe_augment": "채굴 범위 증강",
    "book.mysticalagriculture.entry.tilling_aoe_augment": "경작 범위 증강",
    "book.mysticalagriculture.entry.step_assist_augment": "단차 오르기 증강",
    "book.mysticalagriculture.entry.strength_augment.page.1": "힘 증강은 검이 주는 피해를 5~20만큼 늘리는 검 증강입니다.",
    "book.mysticalagriculture.entry.attack_aoe_augment": "공격 범위 증강",
    "book.mysticalagriculture.entry.attack_aoe_augment.page.1": "공격 범위 증강은 검의 공격 반경을 최대 6블록까지 늘리는 검 증강입니다.",
    "book.mysticalagriculture.entry.poison_resistance_augment": "독 저항 증강",
    "book.mysticalagriculture.entry.poison_resistance_augment.page.1": "독 저항 증강은 방어구를 착용한 동안 독 효과를 받지 않게 하는 방어구 증강입니다.",
    "book.mysticalagriculture.entry.mining_fatigue_resistance_augment.page.1": "채굴 피로 저항 증강은 방어구를 착용한 동안 채굴 피로 효과를 받지 않게 하는 방어구 증강입니다.",
    "book.mysticalagriculture.entry.wither_resistance_augment.page.1": "시듦 저항 증강은 방어구를 착용한 동안 시듦 효과를 받지 않게 하는 방어구 증강입니다.",
    "book.mysticalagriculture.entry.flight_augment.page.1": "비행 증강은 방어구를 착용한 동안 크리에이티브 비행을 사용할 수 있게 하는 흉갑 증강입니다.",
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
    "item.mysticalagradditions.dragon_scale": "드래곤 비늘",
    "item.mysticalagradditions.withering_soul": "시듦의 영혼",
    "item.mysticalagradditions.inferium_paxel": "인퍼륨 팩셀",
    "item.mysticalagradditions.prudentium_paxel": "프루덴튬 팩셀",
    "item.mysticalagradditions.tertium_paxel": "터튬 팩셀",
    "item.mysticalagradditions.imperium_paxel": "임퍼륨 팩셀",
    "item.mysticalagradditions.supremium_paxel": "수프레뮴 팩셀",
    "item.mysticalagradditions.awakened_supremium_paxel": "각성 수프레뮴 팩셀",
    "tooltip.mysticalagradditions.drop_chance": "드롭 확률: %s",
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
    "jei.desc.mysticalagradditions.withering_soul": "위더를 처치하면 떨어집니다.",
    "jei.desc.mysticalagradditions.dragon_scale": "엔더 드래곤을 처치하면 떨어집니다.",
    "modifier.mysticalagradditions.prosperous": "번영",
    "modifier.mysticalagradditions.prosperous.flavor": "번영을!",
    "modifier.mysticalagradditions.prosperous.description": "도구나 무기를 사용할 때 일정 확률로 번영 파편이 떨어집니다.",
    "modifier.mysticalagradditions.soul_siphoner": "영혼 흡수",
    "modifier.mysticalagradditions.soul_siphoner.flavor": "영혼을!",
    "modifier.mysticalagradditions.soul_siphoner.description": "무기가 소울륨 단검처럼 몹의 영혼을 흡수합니다.",
    "crop.mysticalagradditions.gaia_spirit": "가이아의 영혼",
    "crop.mysticalagradditions.awakened_draconium": "각성 드라코늄",
    "crop.mysticalagradditions.neutronium": "뉴트로늄",
    "crop.mysticalagradditions.nitro_crystal": "니트로 수정",
}

QUEST_OVERRIDES = {
    "quest.04A7AA70C23830FF.quest_desc": [
        "낫은 넓은 범위의 식물을 한꺼번에 제거하는 도구입니다. 채굴한 블록 주변의 식물 블록도 함께 파괴합니다."
    ],
    "quest.0B37355262121DD5.quest_subtitle": "씨앗 만들기",
    "quest.140DADB32EF10D58.quest_desc": [
        "드래곤 알 씨앗이 자라려면 경작지 아래에 드래곤 알 크룩스를 놓아야 합니다."
    ],
    "quest.1636F3F12E92CAEA.quest_desc": [
        "물뿌리개를 사용하려면 물 원천 블록을 오른쪽 클릭해 물을 채우세요. 작물을 겨냥한 채 오른쪽 버튼을 누르고 있으면 물뿌리개의 효과 범위 안에 있는 작물에 물을 줍니다.",
        "",
        "에센스 물뿌리개에는 자동 물 주기 기능이 있습니다. 블록을 겨냥하지 않은 상태에서 Shift + 오른쪽 클릭하면 이 기능을 켜거나 끌 수 있습니다. 켜져 있을 때는 물뿌리개가 마법 부여된 것처럼 빛납니다.",
    ],
    "quest.16E3031D800B40D5.quest_desc": [
        "소울륨 소환기는 몹 에센스를 사용해 몹을 소환합니다. 예를 들어 가스트 에센스를 넣으면 가스트를 소환할 수 있습니다."
    ],
    "quest.1CC4F8570A7A99EB.quest_desc": [
        "&d에센스&r는 Mystical Agriculture에서 자원을 재배하는 출발점입니다.\\n\\n&e인퍼륨 에센스&r는 모든 에센스의 기본 등급입니다. 광석을 채굴하거나 몹을 처치하거나 씨앗을 만들어 재배하면 얻을 수 있습니다! \\n\\n더 높은 등급의 에센스를 만들려면 &9주입 수정&r이 필요합니다. "
    ],
    "quest.1CF8263756EE8F2A.title": "&5인지의 가루&r",
    "quest.1E0F92F07FDD162E.quest_desc": [
        "자원 작물을 만들려면 &b번영 씨앗 기반재&r가 필요합니다."
    ],
    "quest.1E0F92F07FDD162E.quest_subtitle": "씨앗의 기반부터 다져요",
    "quest.1E0F92F07FDD162E.title": "&b번영 씨앗 기반재",
    "quest.1E414D285E7A5FE2.title": "&c터튬 도구",
    "quest.1F7591DB6D8EC1E7.title": "&5인사늄 사과",
    "quest.1F88C697817A7680.title": "&a인퍼륨 사과",
    "quest.202B1F54D3F06DAB.quest_desc": [
        "6등급 에센스입니다. 수프레뮴 4개와 주입 수정을 조합해 만듭니다."
    ],
    "quest.212EF8601746C500.title": "&9임퍼륨 사과",
    "quest.217DB12EA32E1724.quest_desc": [
        "&b주입 수정&r은 에센스의 등급을 올리는 데 필요합니다. 예를 들어 인퍼륨 에센스 4개와 주입 수정을 조합하면 프루덴튬 에센스 1개를 얻습니다.\\n\\n나중에는 내구도가 무한한 주입 수정도 만들 수 있습니다."
    ],
    "quest.21A90474590FCDB8.quest_desc": [
        '"화로"는 바닐라 화로의 상위 버전입니다. 기계 업그레이드를 장착해 속도와 연료 효율을 높일 수 있습니다.'
    ],
    "quest.224CE21E56703F6E.quest_desc": [
        "마법봉으로 주입 제단을 활성화할 수 있습니다. 제단을 오른쪽 클릭해 주입 과정을 시작하세요."
    ],
    "quest.2A7E3F2CD335EAD0.quest_desc": [
        "&a에센스 장비&r 제작은 인퍼륨 방어구부터 시작합니다.\\n\\n에센스처럼 더 높은 등급으로 업그레이드할 수 있으며, &b땜장이 작업대&r에서 &9증강&r도 장착할 수 있습니다!"
    ],
    "quest.2C9C9CB71941DC01.quest_desc": [
        "3등급 에센스입니다. 프루덴튬 4개와 주입 수정을 조합해 만듭니다."
    ],
    "quest.2FA6B8A1C8713DE0.quest_desc": [
        "6등급 또는 마법 등급 씨앗이 자라려면 경작지 바로 아래에 해당 크룩스를 놓아야 합니다."
    ],
    "quest.30E9255DEC69C061.title": "&4수프레뮴 도구",
    "quest.31A370550BD592B6.quest_desc": [
        "니트로 수정 씨앗이 자라려면 경작지 아래에 니트로 수정 크룩스를 놓아야 합니다."
    ],
    "quest.32B01BD789F0B037.quest_desc": [
        "각성 수프레뮴과 다른 등급의 에센스는 &6Productive Bees&r를 이용해 생산할 수 있습니다."
    ],
    "quest.32B01BD789F0B037.title": "각성 수프레뮴 자동화",
    "quest.33D23C65E7274A8F.quest_desc": [
        "수프레뮴 에센스를 각성하려면 새 제단과 받침대 4개, &c에센스 용기&r 4개가 필요합니다.\\n\\n에센스 용기에는 기본 원소 에센스인 불, 물, 대지, 공기를 채워야 합니다."
    ],
    "quest.37B297640F537383.quest_desc": [
        "미조율 증강은 주입 제단에서 여러 증강을 만드는 재료입니다. 이 증강으로 &e성급함&r, &1야간 투시&r, &b추락 피해 무효&r, &6화염 저항&r 등 다양한 효과를 얻을 수 있습니다!"
    ],
    "quest.37B297640F537383.title": "&f미조율 증강",
    "quest.3C9F5EB59D72AC90.quest_desc": [
        "각성 수프레뮴 주괴 블록은 &6ATM의 별&r을 제작하는 데 필요합니다."
    ],
    "quest.44B22160850ACAB2.quest_desc": [
        "네더의 별 씨앗이 자라려면 경작지 아래에 네더의 별 크룩스를 놓아야 합니다."
    ],
    "quest.45549E52B3CE2D23.quest_desc": [
        "대낫은 넓은 범위의 작물을 한 번에 수확하는 도구이며 무기로도 쓸 수 있습니다."
    ],
    "quest.48BF71269DEA1AB1.title": "&4수프레뮴 경작지",
    "quest.4EF5DE3FBA2A7AE3.quest_desc": [
        "인퍼륨 에센스로 주괴를 만들면 에센스 &9도구&r와 &9방어구&r를 제작할 수 있습니다.\\n\\n에센스 도구는 더 높은 등급으로 업그레이드할 수 있으며, 방어구처럼 &3땜장이 작업대&r에서 &5증강&r을 장착할 수 있습니다."
    ],
    "quest.4EF5DE3FBA2A7AE3.title": "&a인퍼륨 도구",
    "quest.52BB58D470560219.title": "&6각성 수프레뮴 성장 가속기",
    "quest.54735C5FCD2077B3.quest_desc": [
        "&aMystical Agriculture&r는 &a씨앗&r을 재배해 바닐라와 여러 모드의 다양한 자원을 생산하는 모드입니다."
    ],
    "quest.5B1E0E3E876339E7.title": "&4수프레뮴 갑옷",
    "quest.5C590DB2F3D935E5.quest_desc": [
        "씨앗 재처리기는 에센스 씨앗을 다시 해당 에센스로 변환합니다."
    ],
    "quest.6235B9923BE0AAEB.quest_desc": [
        "인챈터는 아이템과 에센스를 사용해 마법 부여 가능한 아이템에 마법을 부여하는 블록입니다."
    ],
    "quest.6235B9923BE0AAEB.title": "&b인챈터",
    "quest.6501A410F1543C70.quest_desc": [
        "신비로운 비료는 뼛가루보다 강력합니다. 사용한 작물이나 묘목을 즉시 완전히 성장시킵니다."
    ],
    "quest.66C52B137A4FF869.quest_desc": [
        "4등급 에센스입니다. 터튬 4개와 주입 수정을 조합해 만듭니다."
    ],
    "quest.66C52B137A4FF869.title": "&9임퍼륨",
    "quest.67DBE6C59C0D9D1B.quest_desc": [
        "4등급 에센스입니다. 임퍼륨 4개와 주입 수정을 조합해 만듭니다."
    ],
    "quest.67DDFA6FB1F9EECA.title": "&9임퍼륨 도구",
    "quest.685C4A646E092A82.title": "&6각성 수프레뮴 갑옷",
    "quest.4821419D44F8083F.quest_desc": [
        "&9성장 가속기&r는 경작지 바로 아래에 놓으면 씨앗의 성장 속도를 조금 높입니다. 각 등급은 위쪽으로 가속할 수 있는 범위가 다르며, 인퍼륨의 범위가 9블록으로 가장 짧습니다. ",
        "",
        "참고: 모든 등급의 성장 가속기는 같은 빈도로 성장 틱을 제공합니다. 높은 등급은 범위가 더 넓어 한 작물 아래에 더 많이 쌓을 수 있습니다. 성장 가속기가 최대 범위 안에 있기만 하면 어느 등급을 사용해도 됩니다.",
    ],
    "quest.6D0A876D4E4D35AB.quest_desc": [
        "크리에이티브 에센스는 &6ATM의 별&r을 제작하는 데 필요합니다."
    ],
    "quest.73350AD668200E99.quest_desc": [
        "2등급 에센스입니다. 인퍼륨 4개와 주입 수정을 조합해 만듭니다."
    ],
    "quest.75560045ED084900.quest_desc": [
        "대부분의 씨앗은 쉽게 만들 수 있지만, &9몹 씨앗&r을 만들려면 네더에서 &8소울륨&r을 구해야 합니다. ",
        "",
        "찾은 영혼석과 소울륨 광석으로 &3소울륨 단검&r과 &3영혼 항아리&r를 만드세요. 단검으로 몹을 처치하면 &b영혼&r을 모을 수 있으며, 주입 제단에서 해당 몹의 씨앗을 만들 때 사용합니다. ",
        "",
        "다른 방법으로는 &3영혼 추출기&r에 영혼 항아리와 몹 전리품을 넣어 채울 수 있습니다. 예를 들어 썩은 살점을 넣으면 좀비 영혼의 일부를 얻습니다.",
    ],
    "quest.75560045ED084900.title": "몹 씨앗 만들기",
    "quest.7580037DB8ADEB3C.quest_desc": ["야옹 야옹, 나는 소야..."],
    "quest.77C6667B4C37589C.quest_desc": [
        "기계 업그레이드는 &aMystical Agriculture&r 기계의 작동 속도를 높입니다."
    ],
    "quest.7A103577EAE7B3F1.quest_desc": [
        "5등급 각성 에센스입니다. 각성 제단에서 인지의 가루 4개, 각 원소 에센스 10개, 수프레뮴 블록 1개를 조합해 만듭니다."
    ],
    "quest.7A103577EAE7B3F1.title": "&6각성 수프레뮴",
    "quest.7DFF18CFEB0B8DBE.quest_desc": [
        "가능한 한 빨리 &a인퍼륨&r 재배를 시작하세요!\\n\\n씨앗을 기르는 데 꼭 필요하지는 않지만, &e에센스 경작지&r를 만들면 씨앗, 특히 인퍼륨 씨앗의 성장 속도가 증가합니다. 다만 일부 씨앗은 정해진 등급의 경작지에만 심을 수 있습니다."
    ],
    "quest.3F55F3CC8519D783.quest_subtitle": "Mystical Agriculture 소환기",
    "quest.3F55F3CC8519D783.quest_desc": [
        "소울륨 소환기는 Mystical Agriculture가 제공하는 소환기입니다. 몹 에센스와 에너지를 사용해 몹을 소환합니다. 몹 에센스는 영혼 항아리로 만든 몹 작물을 수확해 얻습니다. 따라서 먼저 몹을 처치하거나 영혼 추출기를 사용해야 합니다."
    ],
    "quest.13517D17E6BF015F.quest_desc": [
        "&b다이아몬드 방어구&r와 몇 가지 &a인퍼륨 아이템&r으로 &a인퍼륨 방어구&r를 만들 수 있습니다! \\n\\n땜장이 작업대에서 증강도 장착할 수 있습니다!"
    ],
    "quest.52B61FB01D7C12A4.quest_desc": ["&a인퍼륨&r 방어구의 상위 등급입니다."],
    "quest.1D27EE427ECFD6CE.quest_desc": ["&c터튬&r 방어구의 상위 등급입니다."],
    "quest.5064D5F99E2C69C8.title": "&4수프레뮴 갑옷",
    "quest.5064D5F99E2C69C8.quest_desc": ["&9임퍼륨&r 방어구의 상위 등급입니다."],
    "quest.4A9CB8778D37049F.title": "&6각성 수프레뮴 갑옷",
    "quest.4A9CB8778D37049F.quest_desc": [
        "&4수프레뮴 갑옷&r에 각성 의식을 진행하려면, 먼저 다른 각성 의식으로 필요한 재료를 만들어야 합니다. \\n\\n그만한 가치가 있습니다. &2&lMystical Agriculture&r에서 얻을 수 있는 최고의 방어구니까요!"
    ],
    "quest.7EDF2CC08FC774F9.quest_subtitle": "&f10 &c공격 피해",
    "quest.57F107892FFA1F52.quest_desc": [
        "네더의 별 씨앗을 재배하려면 경작지 아래에 크룩스가 필요합니다. 네, 네더의 별 재배 비용이 더 비싸졌습니다! \\n\\n네더의 별 크룩스를 만들려면 &7시듦의 영혼&r이 필요하며, &8위더&r가 1/3 확률로 떨어뜨립니다."
    ],
    "quest.5791F3000D18E2C9.title": "&8위더 방호 벽돌",
    "quest.5791F3000D18E2C9.quest_desc": [
        "&8위더&r는 블록을 부수고 폭발시키는 습성이 있습니다. \\n\\n이를 막고 싶다면 &8위더 방호 벽돌&r이 알맞습니다! \\n\\n&8위더 방호 블록&r과 기능은 같지만 모양이 더 멋집니다!"
    ],
    "quest.7766E66A14643F4D.title": "&6각성 수프레뮴 주괴 블록",
    "quest.7766E66A14643F4D.quest_desc": [
        "&6각성&r은 &2&lMystical Agriculture&r에 비교적 최근 추가된 기능입니다. &6각성 의식&r으로 &6각성 에센스&r를 만들 수 있습니다. \\n\\n그 에센스와 주괴를 조합하면 이 블록을 얻습니다!"
    ],
    "quest.3145B847A15F97F2.quest_desc": [
        "&2&lMystical Agriculture&r의 에센스를 조합해... &8석탄&r을 만들 수 있습니다. \\n\\n훌륭한 연료지만 &5인사늄 석탄&r은 이름처럼 정말 엄청납니다. "
    ],
    "quest.09D76E9B8CABC31E.quest_desc": [
        "&5&l크리에이티브 에센스&r를 만들려면 &5인사늄 에센스 블록&r 4개가 필요합니다. 블록 하나에는 &5에센스&r 9개가 들어갑니다. 계산해 보면... \\n\\n블록 하나에 &a인퍼륨 에센스&r 9,216개가 필요하므로, 총 &a인퍼륨 에센스&r 36,864개가 필요합니다!"
    ],
    "quest.215AD616E6847E9A.quest_desc": [
        "&5인사늄 보석&r 하나에는 &5인사늄 에센스&r 2개가 필요합니다. 따라서 &5보석 블록&r 하나에는 &5인사늄 에센스&r 18개가 들어갑니다. \\n\\n&5인사늄 블록&r에 필요한 &a인퍼륨 에센스&r 9,216개의 두 배, 즉 &5인사늄 보석 블록&r 4개에는 &a인퍼륨 에센스&r 18,432개가 필요합니다."
    ],
    "quest.6E3AD764A67829CB.quest_desc": [
        "하위 등급인 &b주입 수정&r처럼 &c마스터 주입 수정&r도 같은 작업을 할 수 있습니다. \\n\\n사용 횟수가 무한하며 에센스 블록 4개를 다음 등급의 블록으로 올릴 수 있습니다! \\n\\n제작에는 &c수프레뮴&r이 필요하지만 충분히 가치가 있습니다!"
    ],
    "quest.7377C657CED885AC.title": "&2&lMystical Agriculture",
    "quest.7377C657CED885AC.quest_desc": [
        "&2&lMystical Agriculture&r는 농사를 통해 자원을 얻는 모드입니다. 무엇을 재배할 수 있냐고요?\\n\\n꿀부터 강철, 위더 스켈레톤까지 거의 모든 것을 얻을 수 있습니다.\\n\\n&6&lATM의 별&r을 만들려면 이 모드에서 많은 자원을 재배해야 합니다!"
    ],
    "quest.232A06C9FF0EE7B2.quest_desc": [
        "멘릴 씨앗으로 멘릴 열매, 멘릴 원목, 멘릴 묘목 생산을 자동화할 수 있습니다."
    ],
    "quest.1A96C595CBA42840.title": "키비 자동화",
    "quest.1A96C595CBA42840.quest_desc": [
        "키비 씨앗을 재배하면 키비로 조합할 수 있는 키비 에센스를 얻습니다!"
    ],
    "task.231C01B33E5B4FF0.title": "각성 수프레뮴 벌 생성 알",
    "task.011F410922A4D859.title": "대낫",
    "task.34551E919FD101CF.title": "임퍼륨 도구",
    "task.3E133AC7B615971D.title": "수프레뮴 도구",
    "task.4F6E8F2EC33DB910.title": "각성 수프레뮴 도구",
    "task.7D9A58EBADE91F54.title": "인퍼륨 도구",
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


def load_file_json(path: Path) -> dict[str, object]:
    """BOM과 중복 키를 거부하며 작업 JSON 객체를 읽는다."""
    if path.read_bytes().startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"UTF-8 BOM이 있습니다: {path}")

    def reject(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"중복 키가 있습니다: {path}:{key}")
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject)
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
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
        return f"8분마다 흡수 하트 {hearts}개를 부여합니다."
    if name_key == "health_boost":
        hearts = {"I": 2, "II": 4, "III": 6, "IV": 8, "V": 10}[level]
        return f"최대 생명력이 하트 {hearts}개만큼 증가합니다."
    if name_key.endswith("_aoe"):
        size = {"I": "3x3", "II": "5x5", "III": "7x7", "IV": "9x9"}[level]
        action = " 웅크리는 동안" if name_key in {"pathing_aoe", "tilling_aoe"} else ""
        return f"{action.strip() + ' ' if action else ''}{name}를 {size}로 늘립니다."
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
        old_count = output_text.count(old)
        new_count = output_text.count(new)
        if (old_count, new_count) == (1, 0):
            output_text = output_text.replace(old, new)
        elif (old_count, new_count) != (0, 1):
            raise ValueError(
                f"KubeJS 표시 문구를 하나로 확정하지 못했습니다: {old} / {new}"
            )
    output = OUTPUT_OVERRIDES / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(output_text, encoding="utf-8")

    startup_relative = Path("kubejs/startup_scripts/CustomAdditions.js")
    startup_source = instance / startup_relative
    startup_text = startup_source.read_text(encoding="utf-8-sig")
    magical_soil_variants = (
        ".displayName('∽bMagical Soil')",
        ".displayName('§bMagical Soil')",
        ".displayName('§b마법 토양')",
    )
    if sum(startup_text.count(value) for value in magical_soil_variants) != 1:
        raise ValueError("마법 토양 KubeJS 표시 이름을 하나로 확정하지 못했습니다.")
    for old in magical_soil_variants[:2]:
        startup_text = startup_text.replace(old, magical_soil_variants[2])
    essence_blocks = {
        ".displayName('공기 정수 블록')": ".displayName('공기 에센스 블록')",
        ".displayName('대지 정수 블록')": ".displayName('대지 에센스 블록')",
        ".displayName('화염 정수 블록')": ".displayName('불 에센스 블록')",
        ".displayName('물 정수 블록')": ".displayName('물 에센스 블록')",
    }
    for old, new in essence_blocks.items():
        old_count = startup_text.count(old)
        new_count = startup_text.count(new)
        if (old_count, new_count) == (1, 0):
            startup_text = startup_text.replace(old, new)
        elif (old_count, new_count) != (0, 1):
            raise ValueError(f"KubeJS 에센스 블록 이름을 확정하지 못했습니다: {old}")
    startup_output = OUTPUT_OVERRIDES / startup_relative
    startup_output.parent.mkdir(parents=True, exist_ok=True)
    startup_output.write_text(startup_text, encoding="utf-8")
    return {
        "source": relative.as_posix(),
        "output": output.relative_to(PROJECT_ROOT).as_posix(),
        "startup_source": startup_relative.as_posix(),
        "startup_output": startup_output.relative_to(PROJECT_ROOT).as_posix(),
        "translated_literals": len(replacements) + 1 + len(essence_blocks),
        "output_sha256": sha256(output),
        "startup_output_sha256": sha256(startup_output),
    }


def quest_normalize(value: snbt.TranslationValue) -> snbt.TranslationValue:
    if isinstance(value, str):
        return normalize_existing(value)
    return [normalize_existing(part) for part in value]


def mystical_item_hover_name(item_id: str, translations: dict[str, object]) -> str:
    """Mystical 동적 작물 아이템을 포함한 실제 hover 이름을 계산한다."""
    namespace, separator, item_path = item_id.partition(":")
    if not separator:
        return ""
    for key in (f"item.{namespace}.{item_path}", f"block.{namespace}.{item_path}"):
        value = translations.get(key)
        if isinstance(value, str):
            return value
    if namespace == "kubejs" and item_path == "magical_soil":
        return "§b마법 토양"
    if namespace != "mysticalagriculture":
        return ""
    for suffix, template_key in (
        ("_seeds", "item.mysticalagriculture.mystical_seeds"),
        ("_essence", "item.mysticalagriculture.mystical_essence"),
    ):
        if not item_path.endswith(suffix):
            continue
        crop_id = item_path.removesuffix(suffix)
        crop_name = next(
            (
                translations[key]
                for key in (
                    f"crop.mysticalagriculture.{crop_id}",
                    f"crop.mysticalagradditions.{crop_id}",
                )
                if isinstance(translations.get(key), str)
            ),
            None,
        )
        if crop_name is None:
            crop_name = CUSTOM_NAMES.get(f"{crop_id}.json")
        template = translations.get(template_key)
        if isinstance(crop_name, str) and isinstance(template, str):
            return template % crop_name
    return ""


def remove_snbt_entries(text: str, keys: set[str]) -> str:
    """현재 작업에서 잘못 추가된 SNBT 키만 누적 파일에서 제거한다."""
    matches = list(snbt.ENTRY_RE.finditer(text))
    removals = []
    for index, match in enumerate(matches):
        if match.group(1) not in keys:
            continue
        end = (
            matches[index + 1].start() if index + 1 < len(matches) else text.rfind("}")
        )
        removals.append((match.start(), end))
    for start, end in reversed(removals):
        text = text[:start] + text[end:]
    return text


def build_quests(instance: Path) -> dict[str, object]:
    lang_root = instance / "config/ftbquests/quests/lang"
    dedicated_english = snbt.parse_language_snbt(
        lang_root / f"en_us/chapters/{QUEST_CHAPTER}.snbt_merged"
    )
    dedicated_installed = snbt.parse_language_snbt(
        lang_root / f"ko_kr/chapters/{QUEST_CHAPTER}.snbt_merged"
    )
    english = dict(dedicated_english)
    installed = dict(dedicated_installed)
    global_english = snbt.parse_language_snbt(lang_root / "en_us.snbt")
    global_installed = snbt.parse_language_snbt(lang_root / "ko_kr.snbt")
    chapters, _ = quest_audit.parse_chapters(instance / "config/ftbquests/quests")
    target_namespaces = {
        "mysticalagriculture",
        "mysticalagradditions",
        "mysticalcustomization",
        "botanypotsmystical",
    }
    related_quests = [
        quest
        for chapter in chapters
        if chapter["filename"] != QUEST_CHAPTER + ".snbt"
        for quest in chapter["quests"]
        if any(
            task["item_id"].partition(":")[0] in target_namespaces
            for task in quest["tasks"]
        )
    ]
    related_keys = {
        key
        for quest in related_quests
        for key in (
            f"quest.{quest['id']}.title",
            f"quest.{quest['id']}.quest_subtitle",
            f"quest.{quest['id']}.quest_desc",
            *(f"task.{task['id']}.title" for task in quest["tasks"]),
        )
        if key in global_english
    }
    for key in sorted(related_keys):
        english[key] = global_english[key]
        if key in global_installed:
            installed[key] = global_installed[key]
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
    merged = remove_snbt_entries(
        merged,
        {
            "quest.1E0F92F07FDD162.quest_desc",
            "quest.1E0F92F07FDD162.quest_subtitle",
            "quest.1E0F92F07FDD162.title",
        },
    )
    QUEST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    reparsed = snbt.parse_language_snbt(QUEST_OUTPUT)
    if any(reparsed.get(key) != value for key, value in overrides.items()):
        raise ValueError("Mystical Agriculture 퀘스트 누적 병합 결과가 다릅니다.")
    return {
        "chapter": QUEST_CHAPTER,
        "dedicated_display_keys": len(dedicated_english),
        "related_display_keys": len(related_keys),
        "display_keys": len(english),
        "existing_korean_reused": sum(
            installed.get(k) == v for k, v in overrides.items()
        ),
        "existing_korean_corrected": sum(
            k in installed and installed[k] != v for k, v in overrides.items()
        ),
        "newly_translated": sum(k not in installed for k in overrides),
        "fallback_title_additions": len(set(QUEST_OVERRIDES) - set(english)),
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
    source_numbers = Counter(NUMBER.findall(source))
    target_numbers = Counter(NUMBER.findall(target))
    if any(target_numbers[token] < count for token, count in source_numbers.items()):
        errors.append(f"숫자 불일치: {key}")
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
        korean = load_file_json(path)
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

    kubejs_root = instance / "kubejs"
    kubejs_pattern = re.compile(
        r"mysticalagriculture|mysticalagradditions|mysticalcustomization|"
        r"botanypotsmystical|magical_soil",
        re.IGNORECASE,
    )
    kubejs_reference_files = []
    for path in kubejs_root.rglob("*"):
        if path.suffix not in {".js", ".json"} or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig")
        if kubejs_pattern.search(text):
            kubejs_reference_files.append(path.relative_to(kubejs_root).as_posix())
    tooltip_output = (OUTPUT_OVERRIDES / "kubejs/client_scripts/tooltips.js").read_text(
        encoding="utf-8"
    )
    startup_output = (
        OUTPUT_OVERRIDES / "kubejs/startup_scripts/CustomAdditions.js"
    ).read_text(encoding="utf-8")
    expected_kubejs_literals = (
        "§c가짜 플레이어로 사용할 수 없습니다",
        "§c(Modular Routers, Clickers 같은 블록 포함)",
        "§b마법 토양",
        "공기 에센스 블록",
        "대지 에센스 블록",
        "불 에센스 블록",
        "물 에센스 블록",
    )
    combined_kubejs_output = tooltip_output + startup_output
    for literal in expected_kubejs_literals:
        if combined_kubejs_output.count(literal) != 1:
            errors.append(f"Mystical KubeJS 표시 문구 불일치: {literal}")

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
        "kubejs": {
            "reference_files_checked": len(kubejs_reference_files),
            "direct_display_literals_checked": len(expected_kubejs_literals),
            "missing": sum(
                combined_kubejs_output.count(value) != 1
                for value in expected_kubejs_literals
            ),
        },
    }, errors


def verify_quests(
    instance: Path, translations: dict[str, object]
) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    english = load_file_json(WORK_ROOT / "quest_english.json")
    overrides = load_file_json(WORK_ROOT / "quest_overrides.json")
    output = snbt.parse_language_snbt(QUEST_OUTPUT)
    internal = {
        "task.518B9569DCE0A771.title",
        "task.773CA1FDC4CEFCEF.title",
        "quest.54735C5FCD2077B3.title",
        "quest.7377C657CED885AC.title",
    }
    for key, target in overrides.items():
        if output.get(key) != target:
            errors.append(f"퀘스트 누적 출력 불일치: {key}")
    for key, source in english.items():
        target = overrides.get(key)
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
    related_quests = {
        quest["id"]: quest
        for related_chapter in chapters
        if related_chapter is not chapter
        for quest in related_chapter["quests"]
        if any(
            task["item_id"].partition(":")[0] in target_namespaces
            for task in quest["tasks"]
        )
    }
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

    quest_fallbacks = 0
    task_item_fallbacks = 0
    resource_name_matches = 0
    for quest in [*chapter["quests"], *related_quests.values()]:
        quest_title = snbt.flatten(output.get(f"quest.{quest['id']}.title", ""))
        first_task = quest["tasks"][0] if quest["tasks"] else None
        if not quest_title and first_task is not None:
            task_title = snbt.flatten(output.get(f"task.{first_task['id']}.title", ""))
            hover_name = mystical_item_hover_name(first_task["item_id"], translations)
            if not (task_title or hover_name):
                errors.append(
                    f"퀘스트 fallback 제목을 확인할 수 없습니다: {quest['id']}"
                )
            quest_fallbacks += 1
        if quest_title and first_task is not None and first_task["item_id"]:
            hover_name = mystical_item_hover_name(first_task["item_id"], translations)
            if hover_name and quest_audit.strip_formatting(quest_title) == hover_name:
                resource_name_matches += 1
        for task in quest["tasks"]:
            if not task["item_id"]:
                continue
            task_title = snbt.flatten(output.get(f"task.{task['id']}.title", ""))
            if task_title:
                continue
            hover_name = mystical_item_hover_name(task["item_id"], translations)
            if not hover_name:
                errors.append(f"ItemTask hover 이름을 확인할 수 없습니다: {task['id']}")
            task_item_fallbacks += 1
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
        "related_quests_outside_chapter_checked": len(related_quests),
        "quest_fallbacks_checked": quest_fallbacks,
        "task_item_fallbacks_checked": task_item_fallbacks,
        "resource_name_matches_checked": resource_name_matches,
        "literal_components_checked": len(custom_names)
        + sum(bool(t["custom_name"]) for _, _, t in related),
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
    manifest = load_file_json(manifest_path)
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
        "kubejs/startup_scripts/CustomAdditions.js": OUTPUT_OVERRIDES
        / "kubejs/startup_scripts/CustomAdditions.js",
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
    allowed_changes = {
        "config/ftbquests/quests/lang/ko_kr.snbt",
        "kubejs/startup_scripts/CustomAdditions.js",
        "resourcepacks/ATM10_Korean/assets/mysticalagriculture/lang/ko_kr.json",
        "resourcepacks/ATM10_Korean/assets/mysticalagradditions/lang/ko_kr.json",
    }
    if not changed or not changed <= allowed_changes:
        errors.append(f"Mystical 계열 적용 경로가 계획과 다릅니다: {sorted(changed)}")
    if target["unexpected_changes"]:
        errors.append("적용 매니페스트에 계획 밖 변경이 기록되었습니다.")
    file_records = {
        record["relative_path"]: record for record in target.get("files", [])
    }
    for relative in changed:
        record = file_records.get(relative)
        if record is None:
            errors.append(f"Mystical 계열 적용 기록이 없습니다: {relative}")
            continue
        if record.get("source_sha256") != record.get("after_sha256"):
            errors.append(f"Mystical 계열 적용 기록 해시가 다릅니다: {relative}")
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
    build = load_file_json(WORK_ROOT / "build_report.json")
    intentional = set(build["intentional_original_crop_keys"])
    language_rows, errors = verify_language(instance, intentional)
    translations: dict[str, object] = {}
    for _, namespace in TARGETS:
        translations.update(load_file_json(WORK_ROOT / namespace / "ko_kr.json"))
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
