#!/usr/bin/env python3
"""Mahou Tsukai 언어 파일과 FTB Quests를 현재 영어 원문으로 전면 재검수한다."""

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

FAMILY = "mahou_tsukai"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
LANG_ROOT = WORK_ROOT / "mahoutsukai"
QUEST_ROOTS = (WORK_ROOT / "quests/mahou_tsukai", WORK_ROOT / "quests/related")
CACHE_PATH = PROJECT_ROOT / "temp/mahou_tsukai_candidate_cache_v1.json"
BUNDLED_PATH = LANG_ROOT / "bundled_ko_kr.json"
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
PLACEHOLDER = re.compile(r"%%[A-Za-z]|%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[.,/xX×]\d+)*")
URL = re.compile(r"https?://\S+")

ALLOWED_ORIGINALS = {
    "Mahou Tsukai",
    "Mahou Tsukai Config",
    "/maxmahou player_name new_mahou_limit",
    "/mahoukodoku player_name kodoku_value",
    "Caliburn",
    "Morgan",
    "Clarent",
    "Nobu",
    "Gandr",
    "Rho Aias",
    "William",
    "R'lyeh",
    "Kodoku",
}

EXACT_SOURCE = {
    "Mahou Tsukai": "Mahou Tsukai",
    "Attuner": "조율기",
    "Spell Cloth": "양피지",
    "Dagger": "단검",
    "Mortar and Pestle": "절구와 막자",
    "Powdered Iron": "빻은 철",
    "Powdered Gold": "빻은 금",
    "Powdered Diamond": "빻은 다이아몬드",
    "Powdered Emerald": "빻은 에메랄드",
    "Powdered Quartz": "빻은 석영",
    "Powdered Ender": "빻은 엔더 진주",
    "Attuned Emerald": "조율된 에메랄드",
    "Caliburn": "칼리번",
    "Morgan": "모르간",
    "Clarent": "클라렌트",
    "Emrys": "엠리스",
    "Murky Water": "탁한 물",
    "Mana": "마력",
    "Mahou": "마력",
}

EXACT_KEYS = {
    "item.mahoutsukai.nobu": "Nobu",
    "entity.mahoutsukai.nobu_entity": "Nobu",
    "mahoutsukai.book.nobu.name": "Nobu",
    "mahoutsukai.configuration.title": "Mahou Tsukai 설정",
    "chapter.43BB00A7A7E1042C.title": "Mahou Tsukai",
    "block.mahoutsukai.mahoujin_mystic_staff": "폭발성 마력 응축",
    "block.mahoutsukai.mahoujin_proximity_projection": "근접 투영",
    "block.mahoutsukai.mahoujin_spatial_disorientation": "공간 조작",
    "item.mahoutsukai.mystic_staff": "폭발성 마력 응축의 지팡이",
    "item.mahoutsukai.proximity_projection_keys": "근접 투영의 적흑 열쇠",
    "item.mahoutsukai.scroll_mystic_staff": "「폭발성 마력 응축」두루마리",
    "item.mahoutsukai.scroll_proximity_projection": "「근접 투영」두루마리",
    "item.mahoutsukai.scroll_spatial_disorientation": "「공간 조작」두루마리",
    "item.mahoutsukai.spatial_disorientation_staff": "공간 조작의 지팡이",
    "item.mahoutsukai.weapon_projectile_bow": "무기 사출의 활",
    "mahoutsukai.book.nobu3.desc": (
        "반면 자율 모드는 대상을 따라가지 않지만, 일정 시간 동안 시전자가 다른 "
        "아이템을 사용할 수 있게 합니다. Nobu의 자동 조준 모드와 함께 사용하면 "
        "자동 조준과 동시에 발사합니다.%%n%%n또한 %%k0과 %%k1을 사용해 자율 "
        "구조물을 각각 위아래로 조정할 수 있습니다."
    ),
}

EXACT_KEYS.update(
    {
        "mahoutsukai.book.boundaries.desc": (
            "경계는 설치한 마법진 주위에서 작동하며 일정한 간격으로 마력을 소모하는 범위 주문입니다. "
            "우클릭으로 켜거나 끌 수 있고, 레드스톤 신호를 보내면 작동 상태가 반전됩니다. "
            "%%n%%n경계가 꺼져 있으면 비교기 신호 0, 켜져 있으면 신호 1을 출력합니다. "
            "%%n%%n경계 두루마리를 사용하면 다른 위치에 경계를 빠르게 설치할 수도 있습니다."
        ),
        "mahoutsukai.book.catalysts.desc": (
            "알려진 일곱 가지 마법 계열을 나타내는 촉매가 하나씩 있습니다. 촉매를 망치나 "
            "절구와 막자로 부수면 가루 촉매를 만들 수 있습니다."
        ),
        "mahoutsukai.book.fae_essence.desc": (
            "요정 정수는 요정이 떨어뜨립니다. 요정 정수를 들고 우클릭하면 요정 마법진을 "
            "설치합니다. 요정 정수로 만든 두루마리와 고정 마법진은 누구나 사용할 수 있습니다. "
            "요정 마법진을 우클릭해 소유권을 얻으면 사용할 때 자신의 마력이 소모됩니다. 요정 "
            "정수는 특정 사용자에게 귀속되지 않으므로 두루마리 제작 자동화에 특히 유용합니다."
        ),
        "mahoutsukai.book.fun2.desc": (
            "다음 페이지에서 자신의 부대를 찾으세요. 진행 상황이 기록되므로 부대의 요구 조건을 "
            "충족했는지 확인할 수 있습니다."
        ),
        "mahoutsukai.book.kodoku2.desc": (
            "고독 수치가 높은 몹의 정수를 벌레가 먹으면 우클릭해 회수할 수 있습니다. 고독 "
            "수치가 높은 벌레는 여러 용도로 쓰입니다. %%n %%n벌레를 태우면 근처의 마력 회로에 "
            "마력을 생성합니다. 생성량은 태운 장소가 지맥에서 얼마나 가까운지에 따라 달라집니다. "
            "%%n%%n이 벌레는 공감 마법에도 사용할 수 있습니다."
        ),
        "mahoutsukai.book.kodoku4.desc": (
            "아래에 고독 벌레를 둔 천리안 마법진을 활성화한 뒤, 원하는 효과에 맞는 아이템을 "
            "마법진 위에 던지세요. %%n%%n블레이즈 가루 - 화염%%n%%n토끼 발 - 도약%%n%%n투척용 "
            "물약 - 물약 효과%%n%%n발광석 가루 - 발광%%n%%n(효과 목록은 다음 페이지에 이어집니다.)"
        ),
        "mahoutsukai.book.kodoku5.desc": (
            "%%n썩은 살점 - 허기%%n%%n고독 벌레 - 불운 %%n%%n불운은 번개 맞기, 아이템 떨어뜨리기, "
            "약탈 수치 감소, 넘어지기, 도구 파손, 적대 대상이 되기 쉬워지는 효과 등을 일으킵니다. "
            "발생 확률은 벌레의 품질에 따라 달라집니다.%%n%%n(효과 목록은 다음 페이지에 이어집니다.)"
        ),
        "mahoutsukai.book.magic.desc": (
            "마법을 사용하려면 마력, 핏빛 마법진, 가루 촉매 3개가 필요하며 제작법에 따라 "
            "양피지가 추가로 필요합니다. 두루마리를 만들 때는 먼저 양피지를 놓고 그 위에 핏빛 "
            "마법진을 그리세요. 그 밖의 경우에는 마법진을 바닥에 그리면 됩니다. 가루 촉매를 "
            "들고 마법진을 우클릭해 하나씩 넣으세요."
        ),
        "mahoutsukai.book.mystic_code.desc": (
            "신비의 법전에는 두루마리 세 묶음을 넣을 수 있습니다. Shift를 누른 채 우클릭하면 "
            "보관함이 열립니다. %%k 단축키로 두루마리를 전환하며, 우클릭하거나 길게 누르면 현재 "
            "선택한 두루마리를 사용합니다."
        ),
        "mahoutsukai.book.probability_alter.desc": (
            "시전자의 범위 안에 이 마법진을 2개 이상 설치하고 각각의 위에 후렴과를 올리세요"
            "(설정 참조).%%n%%n이 주문의 두루마리를 사용할 때 후렴과가 놓인 인접 마법진의 "
            "수가 두루마리로 얻는 룰 브레이커의 법이 됩니다. 두루마리 사용에는 %%val0 마력이 "
            "필요합니다. 자세한 내용은 룰 브레이커 페이지를 확인하세요."
        ),
        "mahoutsukai.book.rule_breaker.desc": (
            "확률 변환 주문으로 얻는 이 단검은 법과 피제수를 이용해 사용자의 확률을 조절합니다. "
            "법은 생성할 때 정해지지만 Shift를 누른 채 우클릭하면 피제수를 높일 수 있습니다. "
            "룰 브레이커를 우클릭하면 일정 시간 동안, 플레이어에게 난수가 필요할 때 지정된 수를 "
            "반환하는 효과를 얻습니다."
        ),
        "mahoutsukai.book.rule_breaker2.desc": (
            "이 효과는 단검으로 대상을 공격할 때도 적용됩니다. %%n%%n무작위 정수가 필요할 때는 "
            "%%n(피제수 %% 법)의 결과를 대신 반환합니다. %%n%%n무작위 소수가 필요할 때는"
            "%%n(피제수 / 법)의 결과를 반환합니다."
        ),
        "mahoutsukai.book.selective_displacement.desc": (
            "이 두루마리를 사용하면 강화 효과를 얻습니다. 효과가 유지되는 동안 %%k0 단축키를 "
            "짧게 눌러 대상 개체와 자리를 바꿀 수 있습니다. 단축키를 길게 누르면 개체 두 마리를 "
            "선택해 서로의 자리를 바꿉니다.%%n%%n자리 교환에는 짧은 재사용 대기시간이 있습니다. "
            "두루마리 사용에는 %%val0 마력이 필요합니다."
        ),
        "mahoutsukai.book.spatial_disorientation.desc": (
            "이 두루마리를 사용하면 개체를 시전자가 바라보는 방향으로 날리는 지팡이를 소환합니다. "
            "오래 충전할수록 더 빠르게 날립니다. 블록에 사용하면 충전한 뒤 주변 개체를 끌어와 "
            "날립니다. %%n두루마리 사용에는 %%val0 마력, 개체 하나에 사용할 때는 %%val1 마력, "
            "범위 모드에서는 초당 %%val2 마력이 필요합니다."
        ),
        "mahoutsukai.book.william.desc": (
            " 최고의 글을 쓰는 이에게 영광 있으리!%%n 그대는 누구보다 우뚝 서리라.%%n 강화한 "
            "책을 독서대 위에 놓으면 -%%n 글마다 하나씩 평가받으리라.%%n%%n 명성은, 그대의 "
            "소설이 얼마나 널리 알려졌는가?%%n 어휘는, 익숙한 말과 처음 듣는 말 모두,%%n 형식은, "
            "구두점을 얼마나 잘 썼는가,%%n 간격은, 생각과 생각이 흐려지지 않게 나뉘었는가."
        ),
    }
)

EXACT_KEYS.update(
    {
        "mahoutsukai.config.kodoku_armor_factor.comment": (
            "방어구 수치에 이 값을 곱해 사망 시 고독 수치에 더합니다."
        ),
        "mahoutsukai.config.kodoku_armor_factor_mob.comment": (
            "다른 방어구 계수와 같지만 적대적인 몹에만 적용합니다."
        ),
        "mahoutsukai.config.kodoku_armor_factor_mob.name": "적대적 몹 고독 방어구 계수",
        "mahoutsukai.config.kodoku_confuse_chance.comment": (
            "고독 수치가 1일 때 대상을 혼란시키는 기본 확률"
        ),
        "mahoutsukai.config.kodoku_fire_chance.comment": (
            "고독 수치가 1일 때 대상에게 불을 붙이는 기본 확률"
        ),
        "mahoutsukai.config.kodoku_glow_chance.comment": (
            "고독 수치가 1일 때 대상을 발광시키는 기본 확률"
        ),
        "mahoutsukai.config.kodoku_health_factor.comment": (
            "대상의 최대 체력에 이 값을 곱해 고독 수치에 더합니다."
        ),
        "mahoutsukai.config.kodoku_health_factor_mob.comment": (
            "다른 체력 계수와 같지만 몹에만 적용합니다."
        ),
        "mahoutsukai.config.kodoku_health_factor_mob.name": "적대적 몹 고독 체력 계수",
        "mahoutsukai.config.kodoku_hop_chance.comment": (
            "고독 수치가 1일 때 대상을 뛰게 하는 기본 확률"
        ),
        "mahoutsukai.config.kodoku_hunger_chance.comment": (
            "고독 수치가 1일 때 대상의 허기를 낮추는 기본 확률"
        ),
        "mahoutsukai.config.kodoku_loot_divisor.comment": (
            "고독 수치를 이 값으로 나눈 수만큼 전리품 목록에서 드롭을 제거합니다."
        ),
        "mahoutsukai.config.kodoku_loot_divisor.name": "고독 불운 전리품 제수",
        "mahoutsukai.config.kodoku_misfortune_aggro_chance.comment": (
            "고독 수치가 1일 때 주변 몹의 적대 대상이 되는 기본 확률"
        ),
        "mahoutsukai.config.kodoku_misfortune_aggro_chance.name": (
            "고독 불운 적대 확률"
        ),
        "mahoutsukai.config.kodoku_misfortune_drop_chance.comment": (
            "고독 수치가 1일 때 무작위 아이템을 떨어뜨리는 기본 확률"
        ),
        "mahoutsukai.config.kodoku_misfortune_drop_chance.name": (
            "고독 불운 아이템 드롭 확률"
        ),
        "mahoutsukai.config.kodoku_misfortune_lightning_chance.comment": (
            "고독 수치가 1일 때 대상에게 번개가 치는 기본 확률"
        ),
        "mahoutsukai.config.kodoku_misfortune_lightning_chance.name": (
            "고독 불운 번개 확률"
        ),
        "mahoutsukai.config.kodoku_misfortune_trip_chance.comment": (
            "고독 수치가 1일 때 넘어지는 기본 확률"
        ),
        "mahoutsukai.config.kodoku_misfortune_trip_chance.name": "고독 불운 넘어짐 확률",
        "mahoutsukai.config.kodoku_splash_chance.comment": (
            "고독 수치가 1일 때 대상에게 물약 효과를 적용하는 기본 확률"
        ),
        "mahoutsukai.config.kodoku_teleport_chance.comment": (
            "고독 수치가 1일 때 대상을 순간이동시키는 기본 확률"
        ),
        "mahoutsukai.config.kodoku_tool_break_divisor.comment": (
            "고독 수치를 이 값으로 나눈 만큼 사용 중인 도구에 추가 피해를 줍니다."
        ),
        "mahoutsukai.config.kodoku_tool_break_divisor.name": "고독 불운 도구 피해 제수",
        "mahoutsukai.config.nobu_adjustment_ticks_per_degree.comment": (
            "Nobu 소환체를 1도 움직이는 데 걸리는 틱 수"
        ),
        "mahoutsukai.config.nobu_adjustment_ticks_per_degree.name": (
            "Nobu 1도당 조정 시간(틱)"
        ),
        "mahoutsukai.config.nobu_allowed_bows.name": "Nobu 제작 가능 활",
        "mahoutsukai.config.nobu_aoe_factor.name": "Nobu 범위 피해 계수",
        "mahoutsukai.config.nobu_aoe_hit.name": "Nobu 범위 공격 반경",
        "mahoutsukai.config.nobu_autonomous_life_ticks.comment": (
            "소환된 총이 유지되는 시간"
        ),
        "mahoutsukai.config.nobu_autonomous_life_ticks.name": (
            "Nobu 소환 총 지속 시간(틱)"
        ),
        "mahoutsukai.config.nobu_bullet_damage.comment": "총알 한 발의 피해",
        "mahoutsukai.config.nobu_bullet_damage.name": "Nobu 총알 피해",
        "mahoutsukai.config.nobu_circle_radius.comment": (
            "Nobu가 소환하는 총의 원형 배치 반경"
        ),
        "mahoutsukai.config.nobu_circle_radius.name": "Nobu 총기 배치 반경",
        "mahoutsukai.config.nobu_drum_volume.name": "Nobu 북소리 가청 거리",
        "mahoutsukai.config.nobu_enabled.comment": (
            "생존 모드에서 이 무기를 얻을 수 있는지 여부"
        ),
        "mahoutsukai.config.nobu_firing_line_space.comment": (
            "사격 대열 모드에서 Nobu가 총을 소환할 수 있는 간격"
        ),
        "mahoutsukai.config.nobu_firing_line_space.name": "Nobu 사격 대열 간격",
        "mahoutsukai.config.nobu_is_unbreakable.name": "Nobu 파괴 불가",
        "mahoutsukai.config.nobu_mana_per_construct.comment": (
            "Nobu 소환체 하나를 소환할 때 드는 마력"
        ),
        "mahoutsukai.config.nobu_mana_per_construct.name": "Nobu 소환체당 마력",
        "mahoutsukai.config.nobu_mana_per_shot.comment": "총알 한 발에 드는 마력",
        "mahoutsukai.config.nobu_mana_per_shot.name": "Nobu 발사당 마력 비용",
        "mahoutsukai.config.nobu_max_guns.name": "Nobu 최대 총 수",
        "mahoutsukai.config.nobu_max_spawn_height.comment": (
            "플레이어나 대상의 머리 위에 총이 생성될 수 있는 최대 높이"
        ),
        "mahoutsukai.config.nobu_max_spawn_height.name": "Nobu 소환체 최대 생성 높이",
        "mahoutsukai.config.nobu_personal_drum.comment": (
            "발사할 때 소환체뿐 아니라 Nobu도 북소리를 내는지 여부"
        ),
        "mahoutsukai.config.nobu_personal_drum.name": "Nobu 자체 북소리",
        "mahoutsukai.config.nobu_pitch_increment.comment": (
            "Nobu 소환체를 위아래로 움직일 때의 각도 단위"
        ),
        "mahoutsukai.config.nobu_pitch_increment.name": "Nobu 상하 조정 각도",
        "mahoutsukai.config.nobu_power_damage_factor.name": (
            "Nobu 힘 마법 부여 피해 계수"
        ),
        "mahoutsukai.config.nobu_recoil_time.comment": (
            "Nobu 소환체가 총을 연속 발사할 때의 틱 간격"
        ),
        "mahoutsukai.config.nobu_recoil_time.name": "Nobu 발사 간격",
        "mahoutsukai.config.nobu_spawn_and_fire_freq.comment": (
            "총 소환과 총알 발사 사이의 틱 수"
        ),
        "mahoutsukai.config.nobu_spawn_and_fire_freq.name": "Nobu 소환 및 발사 간격(틱)",
    }
)

EXACT_KEYS.update(
    {
        "quest.002B8F2DE2CB4D2C.quest_desc": [
            "보조 손에 방패를, 주 손에 &7「강화」두루마리&r를 들고 우클릭을 길게 누르세요."
        ],
        "quest.002B8F2DE2CB4D2C.title": "강화된 방패",
        "quest.012912FDAFCD1C66.quest_desc": [
            r"&e&l칼리번&r은 처음에는 &b다이아몬드 검&r보다 크게 강하지 않지만, 업그레이드하면 &b다이아몬드 검&r이 &e&l칼리번&r 앞에서 평범한 막대기처럼 느껴질 만큼 강해집니다! \n&4&l모르간&r과 &e&l칼리번&r에는 실제 피해와 고유 한도가 있습니다. \n\n고유 한도는 올릴 수 있는 최대 피해입니다. &e&l칼리번&r의 고유 한도를 높이려면 &5강타&r를 부여한 뒤 네더의 별과 함께 &3호수&r에 던지세요. \n\n최대 한도를 얻으려면 네더의 별 6개가 필요합니다. 한 번 업그레이드하면 다시 올릴 수 없으므로 6개를 한꺼번에 넣으세요! \n\n일반 피해를 높이려면 &5강타&r를 부여한 뒤 다시 &3호수&r에 던지면 됩니다! 더 높은 피해가 필요한 이유는..."
        ],
        "quest.012912FDAFCD1C66.title": "&l&e칼리번 업그레이드",
        "quest.03DCDFB32CD4BD85.quest_desc": [
            r"&e&l칼리번&r을 얻으려면 몇 가지 조건이 필요합니다. 일부는 앞 퀘스트에서 설명했고 일부는 아직입니다. \n먼저 &3마력 호수&r와 5000 &4마력&r을 준비하세요. \n\n그다음 &5강타&r가 부여된 &b다이아몬드 검&r이 필요합니다. 강타 레벨은 높을수록 좋습니다. \n\n마지막으로 &b검&r을 &3호수&r에 던지면 바닥에서 &e&l칼리번&r을 찾을 수 있습니다!"
        ],
        "quest.03DCDFB32CD4BD85.title": "&e&l칼리번",
        "quest.0A1FBDA0C1314DE1.quest_desc": [
            r"조율된 &b다이아몬드&r와 &a에메랄드&r는 &4마력&r을 저장하는 배터리이며, &4&l모르간&r을 얻으려면 많은 &4마력&r이 필요합니다. \n\n조율된 &b다이아몬드&r는 2000 &4마력&r, 조율된 &a에메랄드&r는 1000을 저장합니다. \n\n의식에는 5000 &4마력&r이 필요하므로 여러 개를 준비하세요!"
        ],
        "quest.0A1FBDA0C1314DE1.title": "&4마력&r이 충분할까요? 아마도요!",
        "quest.0D19FB62C2C1D9F7.quest_desc": [
            r"&4마력&r이 200 이상이 되면 생명력 흡수 결계를 만들어 보세요. \n\n결계 안에서 몹이 죽을 때마다 10 &4마력&r을 회복하지만, 속도는 매우 느립니다."
        ],
        "quest.0D19FB62C2C1D9F7.title": "생명력 흡수 결계",
        "quest.146AF0937D9C63DE.quest_desc": [
            "보조 손에 활을, 주 손에 &7「강화」두루마리&r를 들고 우클릭을 길게 누르세요."
        ],
        "quest.146AF0937D9C63DE.title": "강화된 활",
        "quest.21D323D95F5A7DB3.quest_desc": [
            "보조 손에 막대기를, 주 손에 &7「강화」두루마리&r를 들고 우클릭을 길게 "
            "누르세요."
        ],
        "quest.21D323D95F5A7DB3.title": "강화된 막대기",
        "quest.2D08BCF993B241B8.quest_desc": [
            r"&8&l암야의 복제&r를 얻기 위해 두 번째로 활성화할 주문은 &7「면역 변환」두루마리&r입니다. \n\n&3빻은 눈&r 1개와 &a빻은 에메랄드&r 2개로 면역 변환 의식을 수행해 만드세요."
        ],
        "quest.2D08BCF993B241B8.title": "&7「면역 변환」두루마리",
        "quest.34DACB973CBDE129.quest_desc": [
            r"포스를 사용하세요! \n\n이 재미있는 &a&l지팡이&r로 개체를 날려 보낼 수 있으며, 자신도 대상이 될 수 있습니다! \n\n날릴 대상을 조준하고 우클릭을 길게 누르세요. 자신을 날리려면 땅을 조준합니다. 그다음 마우스를 날아갈 방향으로 움직이세요! \n\n오래 누를수록 더 강하게 날아가며, 최대 충전에 도달하면 자동으로 발동합니다."
        ],
        "quest.34DACB973CBDE129.title": "&a&l공간 조작",
        "quest.378105383747DD48.quest_desc": [
            r"이번 과정은 조금 복잡합니다. \n\n&8&l암야의 복제&r를 얻으려면 영혼 5개를 모으고 피해 변환과 면역 변환을 활성화하세요. \n\n그 상태에서 강화된 방패로 공격을 막으면 &8&l암야의 복제&r를 얻습니다!"
        ],
        "quest.378105383747DD48.title": "&8&l암야의 복제",
        "quest.3907E68572324333.quest_desc": [
            r"&4&l모르간&r을 얻으려면 &e&l칼리번&r이 필요합니다. \n\n&e&l칼리번&r을 얻으려면 &3마력 호수&r가 필요합니다. \n\n&3마력 호수&r를 만들려면 힘의 집약 의식을 수행해야 합니다. \n\n다른 의식과 마찬가지로 빻은 다이아몬드 2개와 빻은 에메랄드 1개를 사용하면 됩니다. \n\n참고로 기지 근처에서는 하지 마세요. 의식 위치가 &3호수&r의 중앙이 됩니다!"
        ],
        "quest.3907E68572324333.title": "힘의 집약 의식",
        "quest.3E89BC6875790952.quest_desc": [
            r"&b빻은 다이아몬드&r 2개와 &3빻은 엔더 진주&r 1개만 있으면 됩니다. &3엔더 진주&r가 핵심 재료예요! \n\n3가지 가루를 &7양피지&r에 사용해 &7두루마리&r를 만드세요! \n\n&7두루마리&r를 사용하면 &7&l열쇠&r를 얻습니다. 이제 어떤 문이든 열 수 있겠네요! \n\n아니, 잠깐만요. 그 열쇠가 아니군요..."
        ],
        "quest.3E89BC6875790952.title": "&7「근접 투영」두루마리",
        "quest.3FB0F22BEF7FE622.quest_desc": [
            r"&8&l암야의 복제&r를 얻으려면 활성화할 &7두루마리&r 가운데 하나인 &7「피해 변환」두루마리&r가 필요합니다. \n\n빻은 철 1개와 &a빻은 에메랄드&r 2개로 피해 변환 의식을 수행해 만드세요."
        ],
        "quest.3FB0F22BEF7FE622.title": "&7「피해 변환」두루마리",
        "quest.3FF97A4B5029C0E7.quest_desc": [
            r"&c&l폭발성 마력 응축의 지팡이&r와 반대로 &b빻은 다이아몬드&r 2개와 &e빻은 금&r 1개가 필요합니다! \n\n재료를 &7양피지&r에 사용해 &7두루마리&r를 만든 뒤, &7두루마리&r로 &b&l활&r을 만드세요!"
        ],
        "quest.3FF97A4B5029C0E7.title": "&7「무기 사출」두루마리",
        "quest.4A88472F1581EE7E.quest_desc": [
            r"&4&lMahou Tsukai&r에 오신 것을 환영합니다. \n\n&4&l모르간&r을 곧바로 얻을 수는 없습니다. 먼저 모드를 조금 진행해야 합니다. \n\n시작하려면 피해를 받아 출혈 효과를 얻으세요. 효과가 사라지기 전에 Shift를 누른 채 단단한 블록을 바라보고 M 키를 눌러 첫 &c마법진&r을 배치하세요. \n\n이것이 바로 &c마법진&r입니다!"
        ],
        "quest.4A88472F1581EE7E.title": "&4&lMahou Tsukai",
        "quest.4C647369D976E67E.quest_desc": [
            r"이 &c&l지팡이&r에는 광선, 범위, 대폭발의 3가지 모드가 있으며 Shift-우클릭으로 바꿉니다. 모두 폭발을 일으키니 안심하세요! \n\n광선 모드는 조준한 곳으로 거대한 광선을 발사해 경로상의 블록과 몹을 모조리 파괴합니다! \n\n범위 모드는 앞쪽에 마법진 12개를 소환하고 각 마법진이 조준 지점으로 폭발을 발사합니다. \n\n대폭발 모드는 가장 재미있습니다. 대상을 조준하고 우클릭을 계속 누르세요. 모든 선이 자랄 때까지 기다렸다가 손을 떼면 됩니다! \n\n쾅! 거대한 폭발이 넓은 지역을 날려 버립니다. 기지 근처에서는 어떤 모드도 사용하지 마세요..."
        ],
        "quest.4C647369D976E67E.title": "&c&l폭발성 마력 응축",
        "quest.5149BDF6BC4B3857.quest_desc": [
            r"다른 방법으로는 내구도 교환 마법진을 만들고 내구도가 높은 아이템을 던지세요. 너무 높은 아이템은 피하는 편이 좋습니다. \n\n&5네더라이트 삽&r 같은 아이템을 권장합니다!"
        ],
        "quest.5149BDF6BC4B3857.title": "내구도 교환",
        "quest.5212A4D67B1851EF.quest_desc": [
            r"이 재미있는 &7&l열쇠&r는 생김새처럼 울버린의 발톱과 비슷하게 작동합니다! \n\n들고 있으면 대상 주위에 마법진이 나타납니다. 좌클릭하면 대상으로 순간이동해 공격합니다! \n\n백 블록이 넘는 아주 먼 거리에서도 사용할 수 있습니다. \n\n피해는 철 검과 비슷합니다."
        ],
        "quest.5212A4D67B1851EF.title": "&7&l근접 투영의 적흑 열쇠",
        "quest.53829B3E51936ACD.quest_desc": [
            "보조 손에 &b다이아몬드 검&r을, 주 손에 &7「강화」두루마리&r를 들고 "
            "우클릭을 길게 누르세요."
        ],
        "quest.53829B3E51936ACD.title": "강화된 검",
        "quest.54E6C0D1BB442184.quest_desc": [
            r"&e주문&r을 만들려면 빻은 재료가 필요합니다. \n\n재료를 빻으려면 &9절구와 막자&r를 만드세요."
        ],
        "quest.54E6C0D1BB442184.title": "&9절구와 막자",
        "quest.565703CBB06CEABF.quest_desc": [
            r"여러분이 &4&l모르간&r을 얻으러 왔다는 것을 알고 있습니다. \n\n&6&lATM 모드팩&r을 대표하는 강력한 검 가운데 하나죠. \n\n이 퀘스트를 따라가면 누구도 막을 수 없는 힘을 얻게 됩니다!"
        ],
        "quest.565703CBB06CEABF.title": "&4&l모르간 얻기",
        "quest.59FD3C4E415EEDDD.quest_desc": [
            r"의식이 시작되면 &3호수&r가 만들어지는 모습을 볼 수 있습니다. \n\n&3탁한 물&r로 가득 찬 약 20x20블록 크기까지 자랍니다. \n\n&3탁한 물&r 자체는 해롭지 않지만, 숨 쉬러 나오는 것을 잊으면 익사할 수 있습니다."
        ],
        "quest.59FD3C4E415EEDDD.title": "&3마력 호수",
        "quest.5EF54E0EB14024D1.quest_desc": [
            r"&e빻은 금&r 2개와 &3빻은 엔더 진주&r 1개가 필요합니다. 순서를 헷갈리면 승천 주문이 만들어지니 주의하세요! \n\n재료를 &7양피지&r에 사용해 &7두루마리&r를 만드세요! \n\n그 &7두루마리&r로 폭발력은 덜하지만 여전히 재미있는 &a&l지팡이&r를 만들 수 있습니다!"
        ],
        "quest.5EF54E0EB14024D1.title": "&7「공간 조작」두루마리",
        "quest.5F9B8ACCE0C8389E.quest_desc": [
            r"&4&lMahou Tsukai&r의 재미있는 무기를 더 만들려면 &7「강화」두루마리&r가 필요합니다. \n\n&7양피지&r를 놓고 그 위에서 강화 의식을 수행한 뒤 &7양피지&r를 회수하세요."
        ],
        "quest.5F9B8ACCE0C8389E.title": "&7「강화」두루마리",
        "quest.5FD4FB9D24586B9B.quest_desc": [
            r"&9번개 지팡이&r를 얻으려면 무엇을 해야 할까요? \n\n강화된 막대기를 든 채 &9번개&r를 맞으면 되지 않을까요?\n\n맞습니다! \n\n&9&l엠리스&r를 얻었다면 보조 손에 들고 우클릭을 길게 누르세요. 결과는 짜릿할 겁니다!"
        ],
        "quest.5FD4FB9D24586B9B.title": "&9&l엠리스",
        "quest.63768C7B988ED22B.quest_desc": [
            r"&b강화된 다이아몬드 검&r을 &d드래곤의 숨결&r 웅덩이에 넣으면 &d&l클라렌트&r를 얻습니다! \n\n&d&l클라렌트&r는 검이자 방패로 작동합니다. \n\n우클릭을 길게 눌러 공격을 막으면, &d&l클라렌트&r가 막은 피해만큼 적에게 되돌려 줍니다."
        ],
        "quest.63768C7B988ED22B.title": "&d&l클라렌트",
        "quest.667B95A687703D6D.quest_desc": [
            r"활로 다이아몬드 검을 쏘고 싶으셨나요? 네더라이트 괭이나 다른 어떤 '무기'라도요? \n\n그렇다면 &b&l무기 사출의 활&r이 정답입니다! \n\nShift-우클릭으로 일반과 투영의 두 모드를 전환합니다. 일반 모드는 인벤토리의 무기를, 투영 모드는 보조 손의 무기만 사용합니다. \n\n&b&l활&r에서 쏜 무기는 던진 삼지창처럼 날아가며 다시 회수할 수 있습니다. \n\n발사한 무기는 직접 휘둘렀을 때와 같은 피해를 줍니다!"
        ],
        "quest.667B95A687703D6D.title": "&b&l무기 사출의 활",
        "quest.6AD061C4331BE1F8.quest_desc": [
            r"&4마력&r은 &4&lMahou Tsukai&r의 모든 활동에 쓰이는 생명력입니다. &e주문&r을 사용하고 무기를 만들려면 최대량을 높이고 충분히 모아야 합니다. \n\n&4마력&r을 사용할수록 최대량이 증가합니다. \n조율된 &a에메랄드&r나 &b다이아몬드&r에 &4마력&r을 저장하면 &4마력&r을 손쉽게 소모할 수 있습니다. \n\n최대 &4마력&r이 충분히 높아지면 다음 &e주문&r을 시도하세요..."
        ],
        "quest.6AD061C4331BE1F8.title": "&4마력&r 최대량 늘리기",
        "quest.6E04A314CD796254.quest_desc": [
            r"마법 모드에 꼭 필요한 것이 뭘까요? 총이라고 하셨나요? 총이라고 해 주세요! \n\nNobu는 3가지 발사 모드를 가진 총입니다."
        ],
        "quest.6E04A314CD796254.title": "&5&lNobu",
        "quest.731A4846BC556AE1.quest_desc": [
            r"&8&l암야의 복제&r에 필요한 마지막 조건도 또 다른 &7두루마리&r와 관련됩니다. \n\n바로 &7「사취의 마안」두루마리&r입니다. \n\n이 주문을 활성화하면 몹이 죽는 모습을 지켜보며 영혼을 모을 수 있습니다. \n\n한 번의 죽음으로는 아주 조금만 모이므로 많은 죽음을 목격해야 합니다. \n\n영혼 5개를 모두 모으면 &8&l암야의 복제&r를 얻을 준비가 끝납니다."
        ],
        "quest.731A4846BC556AE1.title": "영혼",
        "quest.73325912C84F64A5.quest_desc": [
            r"또 다른 방법은 시간 교환입니다. 12시간 동안 &4마력&r을 얻은 뒤 다음 12시간 동안 소모합니다. \n\n시간 교환 마법진을 하나 더 만들면 첫 마법진이 소모 단계에 들어갈 때 서로 순환하게 됩니다."
        ],
        "quest.73325912C84F64A5.title": "시간 교환",
        "quest.777BB82B56038ED3.quest_desc": [
            r"&4&l모르간&r의 피해를 높이는 유일한 방법은 주민을 처치하는 것입니다. 아기 주민은 피해를 더 많이 올려 줍니다! \n\n주민 농장이 준비되어 있기를 바랍니다. 아주 많은 주민을 처치하면 &4&l모르간&r의 피해를 최대로 높일 수 있습니다. \n\n&4&l모르간&r을 들고 우클릭을 길게 누르면 특수 공격도 사용할 수 있습니다."
        ],
        "quest.777BB82B56038ED3.title": "최대로 강화한 &4&l모르간",
        "quest.795FA102F6577368.quest_desc": [
            r"&4&l모르간&r을 얻으려면 길들인 늑대를 &e&l칼리번&r으로 처치해야 합니다. \n\n&e&l칼리번&r의 고유 한도가 그대로 &4&l모르간&r의 고유 한도가 됩니다. \n\n행운을 빕니다!"
        ],
        "quest.795FA102F6577368.title": "&4&l모르간 획득",
        "quest.7992C63F063BE908.quest_desc": [
            r"강력한 효과에 비해 &7두루마리&r 제작법은 간단합니다! &e빻은 금&r 2개와 &b빻은 다이아몬드&r 1개만 있으면 됩니다. \n\n&c마법진&r이 그려진 &7양피지&r에 재료를 사용한 뒤 우클릭해 &7두루마리&r를 얻으세요! \n\n그 &7두루마리&r를 사용하면 &c&l폭발성 마력 응축의 지팡이&r를 얻습니다!"
        ],
        "quest.7992C63F063BE908.title": "&7「폭발성 마력 응축」두루마리",
        "quest.7F7ED94590B5B857.quest_desc": [
            r"일부 &e주문&r은 &7두루마리&r에 담아 필요할 때 사용할 수 있습니다. \n\n먼저 &7양피지&r를 바닥에 놓고 그 &7양피지&r 위에서 원하는 의식을 수행하세요. \n\n&4피&r와 &b가루&r 배치를 마쳤다면 &7양피지&r를 우클릭하세요. 짠, &7두루마리&r입니다! \n\n모든 &e주문&r을 &7두루마리&r로 만들 수 있는 것은 아니며, 잘못 시도해 낭비한 재료는 보상해 드리지 않습니다."
        ],
        "quest.7F7ED94590B5B857.title": "휴대하는 &e주문&r!",
    }
)

REPLACEMENTS = (
    ("내설정", "내구도"),
    ("얼마력", "얼마나"),
    ("마력가", "마력이"),
    ("마력를", "마력을"),
    ("두루마리을", "두루마리를"),
    ("요정가", "요정이"),
    ("피해이", "피해가"),
    ("요정지", "페이지"),
    ("후렴과일", "후렴과"),
    ("엔터티", "개체"),
    ("키 바인딩", "단축키"),
    ("키 바인드", "단축키"),
    ("스왑", "교환"),
    ("블로킹", "방어"),
    ("친숙한 사람", "사역마"),
    ("요정 서클", "요정 마법진"),
    ("경계선", "지맥"),
    ("레이 포인트", "지맥 지점"),
    ("수맥", "지맥"),
    ("프로젝션", "투영"),
    ("규칙 차단기", "룰 브레이커"),
    ("신비한 코드", "신비의 법전"),
    ("성서대", "독서대"),
    ("마력 Circuit", "마력 회로"),
    ("Fae Essence", "요정 정수"),
    ("Fae Circle", "요정 마법진"),
    ("마호진", "마법진"),
    ("사출기", "투영기"),
    ("조율사", "조율기"),
    ("마법에 걸린", "마법이 부여된"),
    ("무기 투사체 활", "무기 사출의 활"),
    ("코도쿠", "고독"),
    ("Kodoku", "고독"),
    ("노부", "Nobu"),
    ("Rhongomyniad", "롱고미니아드"),
    ("Shift 오른쪽 버튼을 클릭하세요", "Shift를 누른 채 우클릭하세요"),
    ("웅크리고 오른쪽 버튼을 눌러", "Shift를 누른 채 우클릭해"),
    ("오른쪽 버튼을 클릭하세요", "우클릭하세요"),
    ("오른쪽 버튼을 눌러", "우클릭해"),
    ("오른쪽 버튼을 누르면", "우클릭하면"),
    ("오른쪽 버튼 :", "우클릭:"),
    ("친숙한", "사역마"),
    ("당신의 몸", "플레이어가 지닌 것"),
    ("귀하의", "자신의"),
    ("쿨타임", "재사용 대기시간"),
    ("한 덩어리", "한 청크"),
    ("항목 이름", "아이템 이름"),
    ("모양 벡터", "시선 벡터"),
    ("직원을 사용", "지팡이를 사용"),
    ("벨소리 속도", "마법진 회전 속도"),
    ("호수가 호수를 만드는 일을", "호수가 확장되는 작업을"),
    ("마호츠카이", "Mahou Tsukai"),
    ("마호우 츠카이", "Mahou Tsukai"),
    ("마호우", "마력"),
    ("아튜너", "조율기"),
    ("어튜너", "조율기"),
    ("스펠 천", "양피지"),
    ("주문 천", "양피지"),
    ("모르타르와 유봉", "절구와 막자"),
    ("박격포와 유봉", "절구와 막자"),
    ("칼리번", "칼리번"),
    ("캘리번", "칼리번"),
    ("모건", "모르간"),
    ("클라렌트", "클라렌트"),
    ("에므리스", "엠리스"),
    ("엠리스 스태프", "엠리스 지팡이"),
    ("스태프", "지팡이"),
    ("스크롤", "두루마리"),
    ("마법진 프로젝터", "마법진 투영기"),
    ("마법 원", "마법진"),
    ("마법 서클", "마법진"),
    ("레이 라인", "지맥"),
    ("레이라인", "지맥"),
    ("페이 에센스", "요정 정수"),
    ("페이 서클", "요정 마법진"),
    ("패밀리어", "사역마"),
    ("배리어", "결계"),
    ("바운더리", "경계"),
    ("텔레포트", "순간이동"),
    ("쿨다운", "재사용 대기시간"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("왼쪽 클릭", "좌클릭"),
    ("웅크린 상태에서", "Shift를 누른 채"),
    ("은신 상태에서", "Shift를 누른 채"),
    ("구성", "설정"),
    ("피해량", "피해"),
    ("데미지", "피해"),
    ("Aoe", "범위"),
    ("AOE", "범위"),
    ("틱당", "매 틱"),
    ("엔티티", "개체"),
    ("개체들", "개체"),
    ("아이템들", "아이템"),
    ("블럭", "블록"),
    ("유저", "사용자"),
    ("캐스터", "시전자"),
    ("재생성", "재생"),
    ("획득 가능", "얻을 수 있음"),
    ("서바이벌", "생존 모드"),
)

SURFACE_BLOCKED = (
    "\u200b",
    "\ufeff",
    "마호츠카이",
    "마호우 츠카이",
    "마우스 오른쪽 버튼을 클릭",
    "마우스 오른쪽 버튼으로 클릭",
    "박격포와 유봉",
    "모르타르와 유봉",
    "스펠 천",
    "주문 천",
    "블럭",
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


def strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value for text in strings(item)]
    return []


def structurally_usable(source: str, target: str) -> bool:
    for pattern in (PLACEHOLDER, FORMAT_CODE, URL):
        if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
            return False
    if source.count("\n") != target.count("\n"):
        return False
    source_plain = FORMAT_CODE.sub("", URL.sub("", source))
    target_plain = FORMAT_CODE.sub("", URL.sub("", target))
    return not (
        Counter(NUMBER.findall(source_plain)) - Counter(NUMBER.findall(target_plain))
    )


def normalize_text(value: str) -> str:
    value = EXACT_SOURCE.get(value, value)
    value = value.replace("\u200b", "").replace("\ufeff", "")
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    value = re.sub(r"(?<!얼)마나", "마력", value)
    value = re.sub(r"\bMana\b", "마력", value)
    value = re.sub(r"\bMahou\b(?! Tsukai)", "마력", value)
    value = re.sub(r"\bCooldown\b", "재사용 대기시간", value)
    value = re.sub(r"\bDuration\b", "지속 시간", value)
    value = re.sub(r"\bRange\b", "범위", value)
    for old, new in (
        ("마력가", "마력이"),
        ("마력를", "마력을"),
        ("마력는", "마력은"),
        ("마력로", "마력으로"),
        ("내구도은", "내구도는"),
        ("두루마리이", "두루마리가"),
    ):
        value = value.replace(old, new)
    return value


def transform(value: object) -> object:
    if isinstance(value, str):
        return normalize_text(value)
    if isinstance(value, list):
        return [transform(item) for item in value]
    return value


def extract_bundled() -> dict[str, object]:
    jar = next((resolve_source_root() / "mods").glob("mahoutsukai-*.jar"))
    with ZipFile(jar) as archive:
        bundled = json.loads(archive.read("assets/mahoutsukai/lang/ko_kr.json"))
    write_json(BUNDLED_PATH, bundled)
    return {"jar": jar.name, "bundled_keys": len(bundled)}


def candidates() -> dict[str, object]:
    if not BUNDLED_PATH.is_file():
        extract_bundled()
    cache = load_json(CACHE_PATH) if CACHE_PATH.is_file() else {}
    roots = (LANG_ROOT, *QUEST_ROOTS)
    sources = {
        text
        for root in roots
        for value in load_json(root / "en_us.json").values()
        for text in strings(value)
        if text and LATIN_WORD.search(text)
    }
    requests = sorted(sources - cache.keys())
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
                    candidate = future.result()
                    cache[source] = (
                        candidate if structurally_usable(source, candidate) else source
                    )
                    if cache[source] == source:
                        failures.append(f"구조 불일치: {source[:120]}")
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스 보고용
                    cache[source] = source
                    failures.append(f"{source[:120]}: {exc}")
                if number % 25 == 0:
                    write_json(CACHE_PATH, cache)
        write_json(CACHE_PATH, cache)
    for root in roots:
        english = load_json(root / "en_us.json")
        write_json(
            root / "auto_candidates_direct.json",
            {
                key: (
                    normalize_text(cache.get(value, value))
                    if isinstance(value, str)
                    else [normalize_text(cache.get(text, text)) for text in value]
                )
                for key, value in english.items()
            },
        )
    report = {
        "unique_strings": len(sources),
        "candidate_requests": len(requests),
        "candidate_failures": failures,
        "status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "direct_candidate_report.json", report)
    return report


def normalize() -> dict[str, object]:
    if not BUNDLED_PATH.is_file():
        extract_bundled()
    bundled = load_json(BUNDLED_PATH)
    counts = {}
    for root in (LANG_ROOT, *QUEST_ROOTS):
        english = load_json(root / "en_us.json")
        auto = load_json(root / "auto_candidates_direct.json")
        reviewed = {}
        for key, source in english.items():
            if key in EXACT_KEYS:
                reviewed[key] = EXACT_KEYS[key]
                continue
            candidate = bundled.get(key) if root == LANG_ROOT else None
            if (
                isinstance(source, str)
                and isinstance(candidate, str)
                and candidate != source
                and structurally_usable(source, candidate)
            ):
                reviewed[key] = normalize_text(candidate)
            else:
                reviewed[key] = transform(auto[key])
        write_json(root / "ko_kr.json", reviewed)
        counts[root.relative_to(WORK_ROOT).as_posix()] = len(reviewed)
    report = {"reviewed_keys": counts, "status": "complete"}
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def pairs(source: object, target: object, path: str) -> list[tuple[str, str, str]]:
    if isinstance(source, str) and isinstance(target, str):
        return [(path, source, target)]
    if (
        isinstance(source, list)
        and isinstance(target, list)
        and len(source) == len(target)
    ):
        return [
            row
            for index, (left, right) in enumerate(zip(source, target, strict=True))
            for row in pairs(left, right, f"{path}[{index}]")
        ]
    return []


def verify_root(root: Path) -> tuple[dict[str, object], list[str]]:
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    errors = []
    untranslated = []
    if list(english) != list(korean):
        errors.append("키 또는 키 순서가 영어 원문과 다릅니다")
    for key in english.keys() & korean.keys():
        source_value = english[key]
        target_value = korean[key]
        if type(source_value) is not type(target_value):
            errors.append(f"자료형 불일치: {key}")
            continue
        if isinstance(source_value, list) and len(source_value) != len(target_value):
            errors.append(f"목록 길이 불일치: {key}")
            continue
        for path, source, target in pairs(source_value, target_value, key):
            if not structurally_usable(source, target):
                errors.append(f"표시 토큰 불일치: {path}")
            if (
                source == target
                and LATIN_WORD.search(source)
                and FORMAT_CODE.sub("", source) not in ALLOWED_ORIGINALS
                and not re.fullmatch(r"[A-Z0-9_+./:%() -]+", source.strip())
            ):
                untranslated.append(path)
            blocked = [token for token in SURFACE_BLOCKED if token in target]
            if blocked:
                errors.append(f"표시 품질 금지 문자열 {blocked}: {path}")
    if untranslated:
        errors.append(f"미번역 후보: {untranslated[:30]}")
    report = {
        "keys": len(english),
        "untranslated_candidates": untranslated,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    reports = []
    errors = []
    for root in (LANG_ROOT, *QUEST_ROOTS):
        report, current = verify_root(root)
        report["scope"] = root.relative_to(WORK_ROOT).as_posix()
        reports.append(report)
        errors.extend(current)
    result = {
        "scopes": reports,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", result)
    return result, errors


def audit() -> tuple[dict[str, object], list[str]]:
    jar = next((resolve_source_root() / "mods").glob("mahoutsukai-*.jar"))
    language = load_json(LANG_ROOT / "en_us.json")
    references = []
    literals = []
    with ZipFile(jar) as archive:
        advancement_files = [
            name
            for name in archive.namelist()
            if name.startswith("data/mahoutsukai/advancement/")
            and name.endswith(".json")
        ]
        for name in advancement_files:
            value = json.loads(archive.read(name))
            display = value.get("display", {}) if isinstance(value, dict) else {}
            for field in ("title", "description"):
                component = display.get(field)
                if isinstance(component, dict) and isinstance(
                    component.get("translate"), str
                ):
                    references.append(component["translate"])
                elif isinstance(component, str):
                    literals.append((name, field, component))
    missing = sorted(set(references) - set(language))
    errors = []
    if missing:
        errors.append(f"업적 표시 참조 키 누락: {missing}")
    if literals:
        errors.append(f"업적 직접 영문 표시값: {literals[:10]}")
    report = {
        "jar": jar.name,
        "advancement_files": len(advancement_files),
        "translated_display_references": len(references),
        "literal_display_values": len(literals),
        "missing_language_references": missing,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("extract-bundled", "candidates", "normalize", "verify", "audit"),
    )
    args = parser.parse_args()
    if args.command == "extract-bundled":
        report, errors = extract_bundled(), []
    elif args.command == "candidates":
        report, errors = candidates(), []
    elif args.command == "normalize":
        report, errors = normalize(), []
    elif args.command == "verify":
        report, errors = verify()
    else:
        report, errors = audit()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
