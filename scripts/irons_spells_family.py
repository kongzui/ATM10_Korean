#!/usr/bin/env python3
"""Iron's Spells 계열 언어와 FTB Quests 번역을 전면 재검수한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import five_family_goal as family_goal
from irons_spells_quests import NEW_DESCRIPTIONS
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "irons_spells"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
NAMESPACES = (
    "irons_spellbooks",
    "irons_jewelry",
    "irons_lib",
    "irons_patreon_lib",
)
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")


SPELLBOOK_NEW = {
    "curios.modifiers.spellbook": "주문서로 장착했을 때:",
    "item.irons_spellbooks.ice_spider_pheromones": "얼음 거미 페로몬",
    "item.irons_spellbooks.tincture_of_forgetfulness": "망각의 팅크",
    "item.irons_spellbooks.tincture_of_forgetfulness.desc": "시련 금고를 초기화합니다",
    "item.irons_spellbooks.tincture_of_forgetfulness.guide": "불길한 보스에게서 드롭됩니다",
    "item.irons_spellbooks.music_disc_whispers_of_ice": "음반",
    "item.irons_spellbooks.bone_key": "뼈 열쇠",
    "item.irons_spellbooks.bone_key.description": "지하 묘지 금고를 엽니다",
    "item.irons_spellbooks.unchained_book": "해방된 책",
    "item.irons_spellbooks.wicked_bone_ring": "사악한 뼈 반지",
    "item.irons_spellbooks.wicked_bone_ring.desc": "+1 주문 투사체 도탄",
    "item.irons_spellbooks.dead_king_phylactery": "죽은 왕의 성물함",
    "item.irons_spellbooks.dead_king_phylactery.description": (
        "죽은 왕의 영혼에 사용하면 죽은 왕이 다시 나타납니다"
    ),
    "item.irons_spellbooks.dead_king_phylactery_shard": "죽은 왕의 성물함 파편",
    "block.irons_spellbooks.tyros_statue": "티로스 조각상",
    "block.irons_spellbooks.bone_vault": "뼈 금고",
    "block.irons_spellbooks.cinderous_vault": "잿불 금고",
    "tooltip.irons_spellbooks.shift_tooltip": "[Shift+]",
    "spell.irons_spellbooks.fang_swirl": "송곳니 소용돌이",
    "spell.irons_spellbooks.blizzard": "눈보라",
    "spell.irons_spellbooks.arcane_shackle": "비전 족쇄",
    "spell.irons_spellbooks.gravity_fissure": "중력 균열",
    "spell.irons_spellbooks.fang_swirl.guide": (
        "생물이나 블록을 지정해 반경 안에 소환사 송곳니가 나선형으로 솟는 영역을 만듭니다."
    ),
    "spell.irons_spellbooks.arcane_shackle.guide": (
        "비전 사슬 묶음을 던집니다. 생물에게 적중하면 사슬 세 개가 대상을 땅에 "
        "묶고 각각 끌어당기는 힘을 가합니다. 빗나가면 사슬 세 개가 서로 다른 주변 "
        "생물을 붙잡습니다. 사슬은 피해를 받거나 해제될 수 있습니다."
    ),
    "spell.irons_spellbooks.blizzard.guide": (
        "지정한 위치에 천천히 움직이는 눈보라를 집중시킵니다. 얼어붙는 바람과 눈이 "
        "생물을 소용돌이 중심으로 끌어당깁니다."
    ),
    "death.attack.irons_spellbooks.fang_swirl": "%1$s이(가) %2$s의 송곳니에 붙잡혔습니다",
    "death.attack.irons_spellbooks.ball_lightning": "%1$s이(가) %2$s에게 감전되었습니다",
    "death.attack.irons_spellbooks.sacrifice": "%1$s이(가) %2$s의 희생 마법에 휩쓸렸습니다",
    "death.attack.irons_spellbooks.fang_swirl.item": (
        "%1$s이(가) %2$s의 송곳니에 붙잡혔습니다(%3$s 사용)"
    ),
    "death.attack.irons_spellbooks.ball_lightning.item": (
        "%1$s이(가) %2$s에게 감전되었습니다(%3$s 사용)"
    ),
    "death.attack.irons_spellbooks.sacrifice.item": (
        "%1$s이(가) %2$s의 희생 마법에 휩쓸렸습니다(%3$s 사용)"
    ),
    "effect.irons_spellbooks.ice_spider_lure": "얼음 거미 유인",
    "effect.irons_spellbooks.soul_burn": "영혼 연소",
    "effect.irons_spellbooks.sacrificial_mark": "희생의 표식",
    "effect.irons_spellbooks.ice_spider_lure.description": (
        "효과가 끝나면 얼음 거미가 나타나 플레이어를 추적합니다"
    ),
    "effect.irons_spellbooks.soul_burn.description": "레벨당 받는 치유량이 5% 감소합니다",
    "commands.irons_spellbooks.generic.unknown_spell": "알 수 없는 주문 ID: %s",
    "commands.irons_spellbooks.generic.create_file": "%s 파일을 만들었습니다",
    "commands.irons_spellbooks.config.cant_override": (
        "설정 %s이(가) 이미 있습니다. 계속하려면 파일을 삭제하거나 명령에 "
        '"override"를 추가하세요.'
    ),
    "commands.irons_spellbooks.config_load_errors": (
        "[Iron's Spells 'n Spellbooks]: 월드 주문 설정에 오류가 있습니다! 자세한 내용은 "
        "서버 로그를 확인하세요."
    ),
    "entity.irons_spellbooks.arcane_shackle": "비전 족쇄",
    "entity.irons_spellbooks.arrow_volley": "화살 일제사격",
    "entity.irons_spellbooks.ball_lightning": "구형 번개",
    "entity.irons_spellbooks.blizzard_aoe": "눈보라",
    "entity.irons_spellbooks.blood_slash": "피의 베기",
    "entity.irons_spellbooks.catacombs_zombie": "지하 묘지 좀비",
    "entity.irons_spellbooks.comet": "혜성",
    "entity.irons_spellbooks.cone_of_cold": "냉기 원뿔",
    "entity.irons_spellbooks.creeper_head": "크리퍼 머리",
    "entity.irons_spellbooks.dead_king_soul": "죽은 왕의 영혼",
    "entity.irons_spellbooks.dragon_breath": "드래곤의 숨결",
    "entity.irons_spellbooks.eldritch_blast": "섬뜩한 폭발",
    "entity.irons_spellbooks.electrocute": "감전",
    "entity.irons_spellbooks.ender_chain": "엔더 사슬",
    "entity.irons_spellbooks.fang_swirl": "송곳니 소용돌이",
    "entity.irons_spellbooks.fire_breath": "화염 숨결",
    "entity.irons_spellbooks.fire_eruption": "화염 분출",
    "entity.irons_spellbooks.fireball": "대형 화염구",
    "entity.irons_spellbooks.firebolt": "화염 화살",
    "entity.irons_spellbooks.frost_field": "서리 지대",
    "entity.irons_spellbooks.ice_tomb": "얼음 무덤",
    "entity.irons_spellbooks.icicle": "고드름",
    "entity.irons_spellbooks.lightning_lance": "번개 창",
    "entity.irons_spellbooks.magehunter_vindicator": "마법사 사냥꾼 변명자",
    "entity.irons_spellbooks.magic_arrow": "마법 화살",
    "entity.irons_spellbooks.magic_missile": "마법탄",
    "entity.irons_spellbooks.ominous_fire_orb": "불길한 화염 구체",
    "entity.irons_spellbooks.root": "뿌리",
    "entity.irons_spellbooks.snowball": "눈덩이",
    "entity.irons_spellbooks.spear": "창",
    "entity.irons_spellbooks.thunderstep_orb": "천둥걸음",
    "entity.irons_spellbooks.undead_rift": "언데드 균열",
    "entity.irons_spellbooks.visual_falling_block": "낙하 블록",
    "entity.irons_spellbooks.wither_skull": "위더 해골",
    "fluid_type.irons_spellbooks.ice_spider_pheromone": "얼음 거미 페로몬",
    "jukebox_song.irons_spellbooks.whispers_of_ice": "Caner Crebes - 얼음의 속삭임",
    "tetra.material.frosted_helve": "서리 손잡이",
    "tetra.material.frosted_helve.prefix": "서리 손잡이",
    "tetra.variant.basic_hilt/frosted_helve": "서리 손잡이",
    "tetra.variant.basic_handle/frosted_helve": "서리 손잡이",
    "tetra.variant.sword_socket/permafrost_shard": "영구동토 파편",
    "tetra.variant.double_socket/permafrost_shard": "영구동토 파편",
    "tetra.variant.single_socket/permafrost_shard": "영구동토 파편",
    "pattern.irons_spellbooks.rune_inscribed_ring.guide": (
        "이 도안은 월드 곳곳에서 발견하거나 거래로 얻을 수 있습니다."
    ),
    "item.irons_spellbooks.infernal_sorcerer_chestplate.desc": (
        "화염 주문 피해를 입히면 대상에게 연소 중첩을 부여합니다"
    ),
    "itemGroup.irons_spellbooks.blocks_tab": "Iron's Spells 'n Spellbooks 블록",
    "item.irons_spellbooks.affinity_ring": "%s 친화의 반지",
    "ui.irons_spellbooks.frostbite_success_chance": "자동 성공 임계값: %d% 확률",
    "death.attack.blood_magic": "%1$s이(가) %2$s의 피 마법에 쓰러졌습니다",
    "death.attack.blood_magic.item": "%1$s 피 마법 2",
    "death.attack.blood_magic.player": "%1$s 피 마법 3",
    "death.attack.irons_spellbooks.volt_strike": (
        "%1$s이(가) %2$s의 전격 일격에 쓰러졌습니다"
    ),
    "death.attack.irons_spellbooks.volt_strike.item": (
        "%1$s이(가) %2$s의 %3$s에 담긴 전격 일격에 쓰러졌습니다"
    ),
    "block.irons_spellbooks.cooked_ice_spider_egg": "익힌 얼음 거미 알",
    "item.irons_spellbooks.cooked_ice_spider_egg": "익힌 얼음 거미 알",
    "item.irons_spellbooks.prepared_ice_spider_egg": "손질한 얼음 거미 알",
    "entity.irons_spellbooks.echoing_arrow": "메아리 화살",
    "entity.irons_spellbooks.echoing_sword": "메아리치는 타격",
    "effect.irons_spellbooks.echoing_strikes.description": (
        "비마법 공격을 하면 메아리가 생겨 일정 범위에 내리꽂히는 유령 검이나, "
        "같은 대상을 꿰뚫는 마법 화살을 생성합니다. 메아리는 원래 공격 피해의 "
        "일정 비율만큼 피해를 줍니다."
    ),
    "effect.irons_spellbooks.hastened.description": (
        "이동 속도, 공격 속도와 채광 속도를 높이고 시전 시간을 줄입니다"
    ),
    "effect.irons_spellbooks.slowed.description": (
        "이동 속도, 공격 속도와 채광 속도를 낮추고 시전 시간 감소 효과를 줄입니다"
    ),
    "potion.potency.6": "VI",
    "potion.potency.7": "VII",
    "potion.potency.8": "XIII",
    "potion.potency.9": "IX",
    "potion.potency.10": "X",
    "spell.irons_spellbooks.echoing_strikes.guide": (
        "비마법 공격을 하면 메아리가 생겨 일정 범위에 내리꽂히는 유령 검이나, "
        "같은 대상을 꿰뚫는 마법 화살을 생성합니다. 메아리는 원래 공격 피해의 "
        "일정 비율만큼 피해를 줍니다."
    ),
    "spell.irons_spellbooks.gravity_fissure.guide": (
        "공중을 갈라 작은 블랙홀을 만듭니다. 블랙홀은 일직선으로 나아가며 주변 "
        "생물을 중력 우물로 끌어당기지만 피해는 주지 않습니다."
    ),
    "spell.irons_spellbooks.haste.guide": (
        "지정한 생물에게, 생물을 지정하지 않았다면 자신에게 가속 효과를 부여합니다. "
        "일정 시간 동안 이동 속도, 공격 속도와 채광 속도가 증가하고 시전 시간이 "
        "줄어듭니다."
    ),
    "spell.irons_spellbooks.scapegoat": "희생양",
    "spell.irons_spellbooks.scapegoat.guide": (
        "염소 모습의 마법 미끼를 만들어 냅니다. 미끼는 주변 적대적 몹의 주의를 "
        "끌고 멀리 달아나며 일정 시간 동안 도발합니다."
    ),
    "spell.irons_spellbooks.slow.guide": (
        "지정한 생물에게 둔화 효과를 부여합니다. 일정 시간 동안 대상의 이동 속도, "
        "공격 속도와 채광 속도가 감소하고 시전 시간 감소 효과도 줄어듭니다."
    ),
    "tooltip.irons_spellbooks.hastened_description": "+%d%% 마법 가속",
    "tooltip.irons_spellbooks.slowed_description": "-%d%% 마법 둔화",
    "ui.irons_spellbooks.echoing_hits": "메아리 타격 %d회",
    "ui.irons_spellbooks.hastened": "%d%% 마법 가속",
    "ui.irons_spellbooks.slowed": "%d%% 마법 둔화",
    "ui.irons_spellbooks.taunt_range": "도발 범위: %d",
}

JEWELRY_NEW = {
    "item.irons_jewelry.jewelcrafting_guide": "보석 세공 안내서",
    "item.irons_jewelry.jewelcrafting_guide.description": "보석과 장신구 안내서",
    "bonus_parameter.irons_jewelry.action": "행동",
    "bonus_parameter.irons_jewelry.positive_effect": "긍정적 효과",
    "bonus_parameter.irons_jewelry.negative_effect": "부정적 효과",
    "bonus_parameter.irons_jewelry.attribute": "속성",
    "bonus_parameter.irons_jewelry.empty": "없음",
    "action.irons_jewelry.apply_damage.description": "(%s %s 피해)",
    "tooltip.irons_jewelry.bonus_from_part_header": "부품 보너스:",
    "tooltip.irons_jewelry.material_cost": "재료 비용: %s",
    "tooltip.irons_jewelry.material_cost_header": "재료 비용:",
    "tooltip.irons_jewelry.material_tags": "재료 태그:",
    "tooltip.irons_jewelry.overview_header": "개요:",
    "tooltip.irons_jewelry.jewelry_type_header": "유형:",
    "ui.irons_jewelry.guide_book.table_of_contents": "목차",
    "ui.irons_jewelry.guide_book.table_of_contents_materials": "재료",
    "ui.irons_jewelry.guide_book.table_of_contents_patterns": "도안",
    "ui.irons_jewelry.guide_book.pattern_select_hint": "자세히 볼 부품을 선택하세요",
    "ui.irons_jewelry.quality": "품질",
    "ui.irons_jewelry.primary_part": "주요 부품",
    "ui.irons_jewelry.primary_part_header": "주요 부품:",
    "ui.irons_jewelry.primary_part.description": "이 부품이 장신구 전체의 품질을 결정합니다",
    "ui.irons_jewelry.primary_part.innate": "이 도안의 기본 품질 배율은 x%s입니다",
    "ui.irons_jewelry.quality.description": (
        "%s을(를) 장신구의 주요 부품으로 사용하면 모든 보너스의 위력이 %s배로 조정됩니다"
    ),
    "ui.irons_jewelry.bonus_type.description": (
        "부품이 %s 보너스를 줄 때 %s을(를) 사용하면 다음 효과를 얻습니다: %s."
    ),
    "ui.irons_jewelry.bonus_type.parameter_description": "재료의 %s을(를) 사용합니다.",
    "ui.irons_jewelry.artisan_scroll_description.unlocked": (
        "%s 도안은 기본으로 해금되어 %s에서 바로 제작할 수 있습니다"
    ),
    "ui.irons_jewelry.artisan_scroll_description.locked": (
        "%s 도안은 잠겨 있으며, 배우려면 %s을(를) 찾아야 합니다."
    ),
    "ui.irons_jewelry.artisan_scroll_description.unknown": (
        "이 도안을 찾는 방법에 관한 추가 정보가 없습니다"
    ),
    "bonus.irons_jewelry.effect_immunity_bonus.description": "%s 효과에 면역이 됩니다",
}

LIB_EXACT = {
    "block.irons_lib.transmog_table": "Patreon 형상변환대",
    "block.irons_lib.player_statue": "Patreon 조각상",
    "block.irons_lib.player_statue.unset_player": "설정 안 됨",
    "block.irons_lib.player_statue.unknown_player": "알 수 없음",
    "block.irons_lib.player_statue.guide.1": "후원자의 이름표를 사용해 플레이어를 설정하세요",
    "block.irons_lib.player_statue.guide.2": "웅크리고 클릭해 자세를 편집하세요",
    "block.irons_lib.player_statue.pose_guide": "클릭해 자세를 설정하세요",
    "tooltip.irons_lib.shift_tooltip": "[%s] +",
    "tooltip.irons_lib.transmog_title": "♦ Patreon 형상변환: %s",
    "tooltip.irons_lib.transmog_failure": "형상변환 권한이 없습니다",
    "tooltip.irons_lib.transmog_option.remove": "형상변환 제거",
    "tooltip.irons_lib.transmog_option.title": "Patreon 형상변환:",
    "tooltip.irons_lib.transmog_option.requirement": "%s Patreon 등급 필요",
    "tooltip.irons_lib.transmog_option.supported_slots": "지원 슬롯: %s",
    "tooltip.irons_lib.transmog_option.supported_slots.all": "전체",
    "tooltip.irons_lib.transmog_option.supported_slots.feet": "장화",
    "tooltip.irons_lib.transmog_option.supported_slots.legs": "레깅스",
    "tooltip.irons_lib.transmog_option.supported_slots.chest": "흉갑",
    "tooltip.irons_lib.transmog_option.supported_slots.head": "투구",
    "tooltip.irons_lib.patreon.tier.none": "없음",
    "tooltip.irons_lib.patreon.tier.acolyte": "수련자",
    "tooltip.irons_lib.patreon.tier.wizard": "마법사",
    "tooltip.irons_lib.patreon.tier.ancient_magician": "고대 마법사",
    "transmog.irons_lib.red_rogue": "붉은 도적",
    "transmog.irons_lib.standard_wizard_robes": "마법사 로브",
    "transmog.irons_lib.standard_wizard_hat": "마법사 모자",
    "transmog.irons_lib.adventurer": "모험가",
    "transmog.irons_lib.silver_sorcerer": "은빛 마도사",
    "transmog.irons_lib.witchhunter": "마녀 사냥꾼",
    "transmog.irons_lib.traveler": "여행자",
    "transmog.irons_lib.onyx_shadow": "오닉스 그림자",
    "transmog.irons_lib.ruby_warrior": "루비 전사",
    "transmog.irons_lib.sapphire_scholar": "사파이어 학자",
    "attribute.name.irons_lib.armor_pierce": "방어력 관통",
    "attribute.name.irons_lib.armor_pierce.desc": "적 방어력을 이 수치만큼 무시합니다",
    "attribute.name.irons_lib.mining_speed": "채굴 속도",
    "attribute.name.irons_lib.mining_speed.desc": "채굴 속도가 백분율로 증가합니다",
    "attribute.name.irons_lib.experience_gained": "경험치 획득량",
    "attribute.name.irons_lib.experience_gained.desc": "몹과 블록이 주는 경험치가 백분율로 증가합니다",
    "attribute.name.irons_lib.arrow_damage": "화살 피해",
    "attribute.name.irons_lib.arrow_damage.desc": "화살형 투사체의 피해가 백분율로 증가합니다",
    "attribute.name.irons_lib.crit_damage": "치명타 피해",
    "attribute.name.irons_lib.crit_damage.desc": "치명타 피해 배율이 백분율로 증가합니다",
    "attribute.name.irons_lib.dodge_chance": "회피 확률",
    "attribute.name.irons_lib.dodge_chance.desc": "받는 피해를 멋지게 무시할 확률입니다",
    "attribute.name.irons_lib.healing_received": "받는 치유량",
    "attribute.name.irons_lib.healing_received.desc": "받는 치유량이 백분율로 증가합니다",
}

POSES = {
    "neutral": "중립",
    "attention": "차렷",
    "squat": "쪼그려 앉기",
    "reaching": "손 뻗기",
    "pointing_forward": "앞 가리키기",
    "fallen": "쓰러짐",
    "statue": "조각상",
    "mourn": "애도",
    "dramatic": "극적인 자세",
    "waving": "손 흔들기",
    "marionette": "꼭두각시",
    "david": "다비드",
    "sitting": "앉기",
    "applause": "박수",
    "archery": "활쏘기",
    "heart": "하트",
    "ballet": "발레",
    "zombie": "좀비",
    "kneeling": "무릎 꿇기",
    "walking": "걷기",
    "ready_to_strike": "공격 준비",
    "exploring": "탐험",
    "at_guard": "경계",
}

LANGUAGE_REPLACEMENTS = (
    ("고대 소환사", "대소환사"),
    ("신비한 정수", "비전 정수"),
    ("신비로운 정수", "비전 정수"),
    ("신비한 주괴", "비전 주괴"),
    ("신비한 천", "비전 천"),
    ("신비한 모루", "비전 모루"),
    ("강화 구슬", "업그레이드 구슬"),
    ("강화 오브", "업그레이드 구슬"),
    ("주문 책", "주문서"),
    ("마법 책", "주문서"),
    ("마법책", "주문서"),
    ("올더모디움", "Allthemodium"),
    ("비브라늄", "Vibranium"),
    ("언옵테이니움", "Unobtainium"),
)

QUEST_REPLACEMENTS = LANGUAGE_REPLACEMENTS + (
    ("신비로운 라텍스", "비전 정수"),
    ("신비한 라텍스", "비전 정수"),
    ("고장난 왕", "죽은 왕"),
    ("상위 버전 오브", "업그레이드 구슬"),
    ("상위 버전", "업그레이드"),
    ("아이언의 마법과 주문서", "Iron's Spells 'n Spellbooks"),
    ("아이언의 주문 및 주문서", "Iron's Spells 'n Spellbooks"),
    ("철의 주문", "Iron's Spells"),
    ("Iron의 주문", "Iron's Spells"),
    ("떨굼 설정으로", "드롭으로"),
    ("마법 저항", "주문 저항"),
    ("마법 슬롯", "주문 슬롯"),
    ("마법을", "주문을"),
    ("마법은", "주문은"),
    ("마법이", "주문이"),
    ("마법의", "주문의"),
    (
        "오직 살인만이 그를 alive...유지할 수 있으며",
        "그가 살아 있으려면 누군가를 죽여야 하며",
    ),
    (" the...&9", " &9"),
    (" 것입니다 though...", " 것입니다..."),
    ("though...이것을", "하지만 이것을"),
    ("약한 one...일기", "약한 일기"),
    ("&c&lFire&r", "&c&l불&r"),
    ("스크롤 Forge", "두루마리 대장간"),
    ("&3스크롤&r", "&3두루마리&r"),
    ("화염 마법", "화염 주문"),
    ("위험합니다 know...", "위험하다는 건 알아요..."),
)

QUEST_EXACT = {
    "quest.08767A1E6D48A5EA.quest_subtitle": "흰수염은 언제쯤 될까요?",
    "quest.2B901ECF97FFA181.quest_subtitle": "9번째 학파",
    "quest.300F2E45D185A9A1.title": "&lIron's Spells 'n Spellbooks",
    "quest.300F2E45D185A9A1.quest_desc": [
        "&lIron&r 님이 멋지고 아주 재미있는 마법 모드인 &lIron's Spells 'n "
        "Spellbooks!&r를 만들었어요. \\n\\n&lIron's Spells&r는 &3주문&r을 만들고 "
        "사용하는 모드예요! 각 &3주문&r에는 희귀도와 레벨, 학파가 있고 모두 주문서에 "
        "넣어 사용할 수 있어요. \\n\\n&7철&r과 &c레드스톤&r만으로 원하는 것을 전부 "
        "만들 수는 없어요. 자리에서 일어나 모험하고 싸워야 합니다!"
    ],
    "quest.340CDF4357E22A43.title": "&e&lIron's Spells 'n Spellbooks",
    "quest.5ED368C926E5F32C.title": "마지막 학파...",
    "quest.615C3E012B2DECD3.title": "&e주문서&r!",
    "quest.6F5F1C525CF08F96.title": "지팡이와 막대",
    "quest.294418130521FDF4.title": "&b미스릴 얻기",
    "quest.373EBEB2E96D9361.title": "&b얼음 거미 소굴",
    "quest.72AB70FD8D8FABBF.title": "고속도로를 달려...",
    "task.00C6A5CB44392D7E.title": "모든 권리 보유",
    "task.76B722B1AE7B6CF2.title": "모든 권리 보유",
    "quest.2A787B99A8B0C767.quest_desc": [
        "매우 중요하고 흔한 블록이에요! 대부분의 &lIron's Spells&r 구조물에서 제작하거나 "
        "찾을 수 있어요. \\n\\n&3두루마리&r를 &e주문서&r에 추가하거나 제거할 때 사용합니다! "
        "책 슬롯에 &e주문서&r를 넣고 그 아래에 &3두루마리&r를 넣으세요. 두루마리를 "
        "제거하려면 &3두루마리&r를 선택한 뒤 오른쪽에서 꺼내 인벤토리로 옮기세요.",
        "{image:atm:textures/questpics/iron_spells/spells_table_gui.png width:150 "
        "height:100 align:center}",
    ],
}

KNOWN_BAD = (
    "alive...",
    " the...",
    "though...",
    " one...",
    " to...",
    "신비로운 라텍스",
    "신비한 라텍스",
    "고장난 왕",
    "떨굼 설정",
    "E직업",
    "E전자",
    "기인하다",
    "평가판 볼트",
    '재정의"를 추가',
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
    if isinstance(value, dict):
        return {key: replace_text(item, replacements) for key, item in value.items()}
    return value


def preserve_images(english: object, korean: object) -> object:
    if isinstance(english, str):
        if english.startswith("{image:"):
            return english
        return korean
    if isinstance(english, list) and isinstance(korean, list):
        return [
            preserve_images(en_item, ko_item)
            for en_item, ko_item in zip(english, korean, strict=True)
        ]
    return korean


def normalize_language() -> dict[str, object]:
    rows = []
    for namespace in NAMESPACES:
        root = WORK_ROOT / namespace
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        candidates = load_json(root / "auto_candidates.json")
        sources = load_json(root / "candidate_sources.json")
        exact = (
            SPELLBOOK_NEW
            if namespace == "irons_spellbooks"
            else JEWELRY_NEW
            if namespace == "irons_jewelry"
            else LIB_EXACT
            if namespace == "irons_lib"
            else {}
        )
        reviewed: dict[str, object] = {}
        for key, source in english.items():
            value = exact.get(key, korean[key])
            if key not in exact and sources[key] == "new_translation_required":
                value = candidates[key]
            if isinstance(source, str) and isinstance(value, str):
                if PLACEHOLDER.findall(source) != PLACEHOLDER.findall(
                    value
                ) or FORMAT_CODE.findall(source) != FORMAT_CODE.findall(value):
                    value = candidates[key]
            reviewed[key] = replace_text(value, LANGUAGE_REPLACEMENTS)
        if namespace == "irons_spellbooks":
            reviewed.update(SPELLBOOK_NEW)
        elif namespace == "irons_jewelry":
            reviewed.update(JEWELRY_NEW)
            for key in english:
                if (
                    key.endswith(".guide")
                    and sources[key] == "new_translation_required"
                ):
                    reviewed[key] = candidates[key]
            reviewed["material.irons_jewelry.allthemodium"] = "Allthemodium"
            reviewed["material.irons_jewelry.vibranium"] = "Vibranium"
            reviewed["material.irons_jewelry.unobtainium"] = "Unobtainium"
        elif namespace == "irons_lib":
            reviewed.update(LIB_EXACT)
            for pose, value in POSES.items():
                key = f"block.irons_lib.player_statue.pose.{pose}"
                if key in reviewed:
                    reviewed[key] = value
        else:
            reviewed["block.irons_patreon_lib.transmog_table"] = "Patreon 형상변환대"
            reviewed["block.irons_patreon_lib.player_statue"] = "Patreon 조각상"
        write_json(root / "ko_kr.json", reviewed)
        rows.append({"namespace": namespace, "reviewed_keys": len(reviewed)})
    report = {"languages": rows, "status": "all_current_english_keys_reviewed"}
    write_json(WORK_ROOT / "language_normalization.json", report)
    return report


def plain(value: str) -> str:
    return FORMAT_CODE.sub("", value).strip()


def item_names() -> dict[str, str]:
    candidates: dict[str, set[str]] = {}
    for namespace in NAMESPACES:
        root = WORK_ROOT / namespace
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        for key, value in english.items():
            if not isinstance(value, str) or not isinstance(korean[key], str):
                continue
            if not key.startswith(("item.", "block.", "entity.")):
                continue
            candidates.setdefault(value, set()).add(korean[key])
    return {
        english: next(iter(values))
        for english, values in candidates.items()
        if len(values) == 1
    }


def normalize_quests() -> dict[str, object]:
    names = item_names()
    matched = 0
    rows = []
    for scope in ("iron_spells_and_spellbooks", "related"):
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
            if key in NEW_DESCRIPTIONS:
                source_items = source if isinstance(source, list) else [source]
                value = [
                    item
                    if isinstance(item, str) and item.startswith("{image:")
                    else NEW_DESCRIPTIONS[key]
                    for item in source_items
                ]
            value = preserve_images(source, value)
            value = replace_text(value, QUEST_REPLACEMENTS)
            if key.endswith(".title") and isinstance(source, str):
                name = names.get(plain(source))
                if name is not None:
                    value = family_goal.apply_title_name(source, name)
                    matched += 1
            reviewed[key] = value
        reviewed.update(
            {key: value for key, value in QUEST_EXACT.items() if key in english}
        )
        write_json(root / "ko_kr.json", reviewed)
        rows.append({"scope": scope, "reviewed_keys": len(reviewed)})
    report = {
        "quests": rows,
        "new_descriptions_manually_reviewed": len(NEW_DESCRIPTIONS),
        "item_titles_matched_to_resourcepack": matched,
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
        for index, (en_item, ko_item) in enumerate(zip(english, korean, strict=True)):
            rows.extend(string_pairs(en_item, ko_item, f"{path}[{index}]"))
        return rows
    return []


def verify_scope(root: Path) -> tuple[dict[str, object], list[str]]:
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    errors = []
    if list(english) != list(korean):
        errors.append("키 또는 키 순서가 영어 원문과 다릅니다")
    untranslated = []
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
        [WORK_ROOT / namespace for namespace in NAMESPACES]
        if kind == "language"
        else [
            WORK_ROOT / "quests/iron_spells_and_spellbooks",
            WORK_ROOT / "quests/related",
        ]
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
    jar = next((instance / "mods").glob("irons_spellbooks-*.jar"))
    inventory = family_goal.inventory(instance, FAMILY)
    references = []
    direct_display = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "irons_spellbooks:" not in text and "Iron's Spells" not in text:
            continue
        relative = path.relative_to(instance).as_posix()
        references.append(relative)
        for number, line in enumerate(text.splitlines(), 1):
            if re.search(
                r"displayName|setHoverName|tooltip|Text\.(?:of|literal)", line, re.I
            ):
                direct_display.append(f"{relative}:{number}")
    errors = [f"처리하지 않은 KubeJS 표시문: {value}" for value in direct_display]
    report = {
        "main_jar": jar.name,
        "installed_targets": len(inventory["installed"]),
        "advancement_files": next(
            row["advancements"]
            for row in inventory["installed"]
            if row["namespace"] == "irons_spellbooks"
        ),
        "advancement_display_uses_language_keys": True,
        "kubejs_reference_files": references,
        "kubejs_direct_display_lines": direct_display,
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
