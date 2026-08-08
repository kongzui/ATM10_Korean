#!/usr/bin/env python3
"""Industrial Foregoing 계열 언어 파일을 영어 원문 기준으로 전체 재검수한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path
from zipfile import ZipFile

import ars_family
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root


FAMILY = "industrial_foregoing"
WORK_ROOT = PROJECT_ROOT / "working/industrial_foregoing"
CACHE_FILE = PROJECT_ROOT / "temp/industrial_foregoing_language_candidate_cache.json"
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"

NAMESPACES = (
    "industrialforegoing",
    "industrialforegoingsouls",
    "mifa",
    "soulplied_energistics",
)

KEY_OVERRIDES = {
    "itemGroup.industrialforegoing_core": "Industrial Foregoing: 핵심",
    "itemGroup.industrialforegoing_tool": "Industrial Foregoing: 도구",
    "itemGroup.industrialforegoing_transport": "Industrial Foregoing: 운송",
    "itemGroup.industrialforegoing_generator": "Industrial Foregoing: 발전기",
    "itemGroup.industrialforegoing_ag_hus": "Industrial Foregoing: 농업 및 축산",
    "itemGroup.industrialforegoing_resource_production": "Industrial Foregoing: 자원 생산",
    "itemGroup.industrialforegoing_misc": "Industrial Foregoing: 기타",
    "key.industrialforegoing.category": "Industrial Foregoing",
    "block.industrialforegoing.machine_frame_pity": "조악한 기계 프레임",
    "block.industrialforegoing.machine_frame_simple": "기본 기계 프레임",
    "block.industrialforegoing.machine_frame_advanced": "고급 기계 프레임",
    "block.industrialforegoing.machine_frame_supreme": "최고급 기계 프레임",
    "block.industrialforegoing.pink_slime_block": "분홍색 슬라임 블록",
    "block.industrialforegoing.sludge_refiner": "슬러지 정제기",
    "block.industrialforegoing.protein_reactor": "단백질 반응기",
    "block.industrialforegoing.simulated_hydroponic_bed": "모의 수경 재배대",
    "block.industrialforegoing.hydroponic_bed": "수경 재배대",
    "block.industrialforegoing.pitiful_generator": "조악한 발전기",
    "block.industrialforegoing.stasis_chamber": "정지장",
    "block.industrialforegoing.ore_laser_base": "광석 레이저 베이스",
    "block.industrialforegoing.fluid_laser_base": "유체 레이저 베이스",
    "block.industrialforegoing.material_stonework_factory": "자재 석재 가공 공장",
    "block.industrialforegoing.froster": "냉동기",
    "block.industrialforegoing.washing_factory": "광석 세척 공장",
    "block.industrialforegoing.fluid_sieving_machine": "유체 체질기",
    "block.industrialforegoing.mycelial_furnace": "화로 균사 발전기",
    "block.industrialforegoing.mycelial_potion": "물약 균사 발전기",
    "block.industrialforegoing.mycelial_culinary": "요리 균사 발전기",
    "block.industrialforegoing.mycelial_slimey": "점액 균사 발전기",
    "block.industrialforegoing.mycelial_disenchantment": "마법 추출 균사 발전기",
    "block.industrialforegoing.mycelial_ender": "엔더 균사 발전기",
    "block.industrialforegoing.mycelial_explosive": "폭발 균사 발전기",
    "block.industrialforegoing.mycelial_frosty": "냉기 균사 발전기",
    "block.industrialforegoing.mycelial_halitosis": "구취 균사 발전기",
    "block.industrialforegoing.mycelial_magma": "마그마 균사 발전기",
    "block.industrialforegoing.mycelial_pink": "분홍색 균사 발전기",
    "block.industrialforegoing.mycelial_death": "죽음 균사 발전기",
    "block.industrialforegoing.mycelial_netherstar": "네더의 별 균사 발전기",
    "block.industrialforegoing.mycelial_rocket": "로켓 균사 발전기",
    "block.industrialforegoing.mycelial_crimed": "범죄 균사 발전기",
    "block.industrialforegoing.mycelial_meatallurgic": "육금술 균사 발전기",
    "block.industrialforegoing.mycelial_reactor": "균사 반응기",
    "block.essence": "정수",
    "block.sludge": "슬러지",
    "item.industrialforegoing.hydroponic_simulation_processor": "수경 재배 모의 처리기",
    "item.industrialforegoing.machine_settings_copier": "기계 설정 복사기",
    "item.industrialforegoing.dryrubber": "건조 고무",
    "item.industrialforegoing.sludge_bucket": "슬러지 양동이",
    "item.industrialforegoing.adult_filter": "성체 필터",
    "item.industrialforegoing.book_manual": "Industrial Foregoing 설명서",
    "item.industrialforegoing.energy_field_addon": "에너지장 업그레이드",
    "item.industrialforegoing.laser_lens": "%s 레이저 렌즈",
    "item.industrialforegoing.laser_lens_inverted": "레이저 렌즈(반전)",
    "item.industrialforegoing.machinehull": "기계 외장",
    "item.industrialforegoing.iron_gear": "철 기어",
    "item.industrialforegoing.gold_gear": "금 기어",
    "item.industrialforegoing.diamond_gear": "다이아몬드 기어",
    "item.industrialforegoing.processing": "처리 ",
    "item.industrialforegoing.tier": "등급 ",
    "item.industrialforegoing.addon": "업그레이드: ",
    "fluid_type.industrialforegoing.sludge": "슬러지",
    "entity.industrialforegoing.launcher_projectile_entity": "뚫어뻥",
    "text.industrialforegoing.tooltip.accepts_fluid_on_top": (
        "기계 위에 놓인 탱크의 유체를 사용합니다"
    ),
    "text.industrialforegoing.machine_settings_copier.settings_stored": "설정을 저장했습니다",
    "text.industrialforegoing.machine_settings_copier.settings_copied": "설정을 복사했습니다",
    "text.industrialforegoing.machine_settings_copier.settings_clear": (
        "* 웅크리고 우클릭하면 복사한 설정을 지웁니다"
    ),
    "text.industrialforegoing.machine_settings_copier.settings_can_copy": (
        "* 기계를 웅크리고 우클릭하면 설정을 복사합니다"
    ),
    "text.industrialforegoing.tooltip.fortune_addon": "* 행운 업그레이드 사용 가능",
    "text.industrialforegoing.tooltip.energy_field_right_click": (
        "연결하려면 에너지장 공급기를 우클릭하세요"
    ),
    "text.industrialforegoing.tooltip.ctrl_left": ("(변경하려면 Ctrl + 좌클릭하세요)"),
    "text.industrialforegoing.tooltip.ctrl_right": ("(변경하려면 Ctrl + 우클릭하세요)"),
    "text.industrialforegoing.tooltip.fermentation_station.tank_full": (
        "§6밀봉 조건: §f가득 참"
    ),
    "text.industrialforegoing.plant.any": "- 모든 바닐라식 작물",
    "text.industrialforegoing.plant.any_tree": "- 모든 바닐라식 나무",
    "text.industrialforegoing.plant.slime_tree": ("- Tinkers' Construct 슬라임 나무"),
    "tooltip.industrialforegoing.backpack.pickup_extra_1": (
        "Ctrl + 백팩 열기 키를 눌러 비활성화"
    ),
    "industrialforegoing.subtitle.nuke_explosion": (
        "인피니티 핵의 죽음과 파괴를 받아들이세요"
    ),
    "tooltip.industrialforegoing.hydroponic.function_1": (
        "* 수경 재배대에서 작물 데이터를 수집할 때 사용합니다"
    ),
    "tooltip.industrialforegoing.hydroponic.function_2": (
        "* 모의 수경 재배대에서 생산물을 얻을 때 사용합니다"
    ),
    "tooltip.titanium.facing_handler.simulation": "수경 재배 모의 처리기",
    "tooltip.titanium.facing_handler.seed": "모의 재배 씨앗",
    "tooltip.titanium.facing_handler.essence": "정수",
    "block.industrialforegoingsouls.soul_laser_base": "영혼 레이저 베이스",
    "block.industrialforegoingsouls.soul_network_pipe": "영혼 네트워크 파이프",
    "block.industrialforegoingsouls.soul_surge": "영혼 가속기",
    "industrialforegoingsouls.soul_storage": "영혼 저장량: ",
    "itemGroup.industrialforegoingsouls": "Industrial Foregoing: Souls",
    "item.mifa.netherite_gear": "네더라이트 기어",
    "itemGroup.industrialforegoing_addons": "Industrial Foregoing 추가 업그레이드",
    "itemGroup.mifa_addons": "Industrial Foregoing 추가 업그레이드",
    "soulkey.name": "워든 영혼",
    "soulkey.description": "영혼",
    "soulpliedenergistics.can_be_used_filter": (
        "*ME 인터페이스에서 영혼을 요청하는 데 사용할 수 있습니다*"
    ),
    "soulpliedenergistics.storage_bus": (
        "*상단에 ME 저장 버스를 연결하면 영혼에 접근할 수 있습니다*"
    ),
    "tag.item.industrialforegoing.machine_frame.pity": "조악한 기계 프레임",
    "tag.item.industrialforegoing.machine_frame.simple": "기본 기계 프레임",
    "tag.item.industrialforegoing.machine_frame.advanced": "고급 기계 프레임",
    "tag.item.industrialforegoing.machine_frame.supreme": "최고급 기계 프레임",
    "tag.item.industrialforegoing.sludge": "슬러지",
    "text.industrialforegoing.display.mob": "몹: ",
    "text.industrialforegoing.display.health": "체력: ",
    "text.industrialforegoing.display.efficiency_2": "효율: ",
    "text.industrialforegoing.display.enchantment_level": "마법 레벨: ",
    "text.industrialforegoing.display.moving_babies": "새끼 이동 중",
    "text.industrialforegoing.display.moving_adults": "성체 이동 중",
    "text.industrialforegoing.display.mb_of_biofuel": " mb의 바이오연료",
    "text.industrialforegoing.display.mb_of_meat": "mb의 액상 고기",
    "text.industrialforegoing.jei.recipe.any": "- 모두",
    "text.industrialforegoing.jei.recipe.laser_drill_items": "레이저 드릴 아이템",
    "text.industrialforegoing.jei.recipe.stonework_generation": "석재 가공 생산",
    "text.industrialforegoing.jei.recipe.up_to_500mb": "최대 500mb",
    "text.industrialforegoing.donation.click_for": "*자세한 내용을 보려면 누르세요*",
    "tooltip.industrialforegoing.hydroponic.executions": "작업 횟수: ",
    "tooltip.industrialforegoing.hydroponic.potential_drops": "가능한 생산물: ",
    "tooltip.industrialforegoing.hydroponic.next_efficiency": "다음 효율 보너스: ",
    "emi.category.industrialforegoing.stone_work": "석재 가공 조합법",
    "emi.category.industrialforegoing.stone_work_generator": "석재 가공 생산",
}

KEY_OVERRIDES.update(
    {
        "text.industrialforegoing.display.producing": "생산 중:",
        "text.industrialforegoing.display.fluid": "유체:",
        "text.industrialforegoing.display.dye_amount": "염료 양:",
        "text.industrialforegoing.display.work": "작동 중:",
        "text.industrialforegoing.display.power": "전력:",
        "text.industrialforegoing.display.tier": "등급:",
        "text.industrialforegoing.display.current_area": "현재 영역:",
        "text.industrialforegoing.display.next_tier": "다음 등급까지",
        "text.industrialforegoing.button.blackhole.empty": "플레이어 인벤토리 비우기",
        "text.industrialforegoing.tooltip.can_hold": "보관 가능",
        "text.industrialforegoing.tooltip.max_tier": "최대 등급:",
        "text.industrialforegoing.tooltip.no_wither_skull": (
            "직접 놓을 수 없는 아이템입니다. 기계라면 놓을 수 있을지도 모릅니다."
        ),
        "text.industrialforegoing.tooltip.power_optional": "* 전력 공급 선택 사항",
        "text.industrialforegoing.down": "아래로",
        "text.industrialforegoing.launcher.damage": " 피해",
        "text.industrialforegoing.plant.chorus": "- 후렴초",
        "text.industrialforegoing.plant.melon": "- 멜론 §o(다시 심을 필요 없음)",
        "text.industrialforegoing.plant.pumpkin": "- 호박 §o(다시 심을 필요 없음)",
        "tooltip.industrialforegoing.hydroponic.efficiency": "효율: ",
        "tooltip.industrialforegoing.backpack.pickup_all": (
            "아이템 및 경험치 자동 줍기 활성화"
        ),
        "tooltip.industrialforegoing.backpack.xp_pickup_enabled": (
            "경험치 자동 줍기 활성화"
        ),
        "tooltip.industrialforegoing.backpack.pickup_disabled": "자동 줍기 비활성화",
        "tooltip.industrialforegoing.backpack.pickup_extra": (
            "웅크린 상태에서 백팩 열기 키를 눌러 모드 전환"
        ),
        "tooltip.industrialforegoing.backpack.needs_biofuel": (
            "작동하려면 바이오연료가 필요합니다"
        ),
        "tooltip.industrialforegoing.backpack.void": "무효화: ",
        "tooltip.industrialforegoing.mob_crusher.consume_extra_1": (
            "몹은 정수를 생성하지 않지만, 처치할 때마다"
        ),
        "conveyor.upgrade.industrialforegoing.conveyor_bouncing_upgrade": (
            "튕김 컨베이어 업그레이드"
        ),
        "conveyor.upgrade.industrialforegoing.conveyor_blinking_upgrade": (
            "순간이동 컨베이어 업그레이드"
        ),
        "conveyor.upgrade.industrialforegoing.tooltip.increase": "증가",
        "conveyor.upgrade.industrialforegoing.tooltip.decrease": "감소",
        "block.industrialforegoing.potion_brewer": "물약 양조기",
        "block.industrialforegoing.animal_rancher": "동물 목장기",
        "block.industrialforegoing.ore_processor": "광석 처리기",
        "block.industrialforegoing.villager_trade_exchanger": "주민 거래기",
        "block.industrialforegoing.energy_field_provider": "에너지장 공급기",
        "block.industrialforegoing.oredictionary_converter": "광석 사전 변환기",
        "item.industrialforegoing.artificial_dye": "인공 염료",
        "item.industrialforegoing.leaf_shearing": "나뭇잎 깎기 업그레이드",
        "item.industrialforegoing.itemstack_transfer_addon": "아이템 전송 업그레이드",
        "tooltip.industrialforegoing.stonework.none": "작업 없음",
        "tag.item.industrialforegoing.bioreactor": "생물 반응기 투입물",
        "emi.category.industrialforegoing.dissolution_chamber": "용해 챔버",
        "emi.category.industrialforegoing.bioreactor": "생물 반응기",
        "text.industrialforegoing.jei.recipe.title.bioreactor": (
            "생물 반응기 투입 가능 아이템"
        ),
        "text.industrialforegoing.tooltip.fermentation_station.tank_half": (
            "§6밀봉 조건: §f절반 이상"
        ),
        "text.industrialforegoing.tooltip.fermentation_station.tank_one": (
            "§6밀봉 조건: §f1 양동이"
        ),
        "item.industrialforegoing.fluid_transfer_addon": "유체 전송 업그레이드",
        "tooltip.industrialforegoing.mb_of": "mb의 %s",
        "text.industrialforegoing.jei.recipe.mb_work": "mb/작업",
    }
)

KEY_OVERRIDES.update(
    {
        f"industrialforegoing.jei.category.{key}": value
        for key, value in {
            "furnace": "화로 균사 발전기",
            "potion": "물약 균사 발전기",
            "culinary": "요리 균사 발전기",
            "slimey": "점액 균사 발전기",
            "disenchantment": "마법 추출 균사 발전기",
            "ender": "엔더 균사 발전기",
            "explosive": "폭발 균사 발전기",
            "frosty": "냉기 균사 발전기",
            "halitosis": "구취 균사 발전기",
            "magma": "마그마 균사 발전기",
            "pink": "분홍색 균사 발전기",
            "death": "죽음 균사 발전기",
            "netherstar": "네더의 별 균사 발전기",
            "rocket": "로켓 균사 발전기",
            "crimed": "범죄 균사 발전기",
            "meatallurgic": "육금술 균사 발전기",
        }.items()
    }
)

KEY_OVERRIDES.update(
    {
        f"tooltip.titanium.facing_handler.{key}": value
        for key, value in {
            "sludge": "슬러지",
            "meat": "액상 고기",
            "input_books": "책 입력",
            "potions_items": "물약 출력",
            "sludge_tank": "슬러지 탱크",
            "crops_output": "작물 출력",
            "fish_output": "물고기 출력",
            "meat_tank": "액상 고기 탱크",
            "lava_tank": "용암 탱크",
            "processed_ores_output": "가공 광석 출력",
            "trade_output": "거래 출력",
            "dye_items": "염료 입력",
            "lens_items": "렌즈 입력",
            "change": "변환된 아이템",
            "wither_skulls": "위더 해골",
            "crafting": "조합 격자",
            "output": "출력",
            "inputbook": "책 입력",
            "outputnoenchanteditem": "마법이 없는 아이템 출력",
            "noenchanted": "마법이 없는 아이템 출력",
            "potion.input_0": "물약 입력",
            "disenchantment.input_0": "마법이 부여된 아이템 입력",
            "disenchantment.input_1": "출력",
            "magma.input_0": "용암 입력",
            "meatallurgic.input_0": "액상 고기 입력",
        }.items()
    }
)

BOOK_OVERRIDES = {
    "text.industrialforegoing.book.title": "Industrial Foregoing 설명서",
    "text.industrialforegoing.book.category.items": "아이템",
    "text.industrialforegoing.book.sewer": (
        "전력을 공급하면 위쪽의 동물에게서 {오물}을 수집합니다."
    ),
    "text.industrialforegoing.book.animal_growth_increaser": (
        "전력과 {번식}용 먹이를 공급하면 새끼 동물에게 먹이를 주어 더 빨리 "
        "{성장}시킵니다."
    ),
    "text.industrialforegoing.book.animal_independence_selector": (
        "전력을 공급하면 {새끼} 동물을 뒤쪽에서 앞쪽으로 옮깁니다.@L@@L@"
        "{성체 필터}를 설치하면 새끼 대신 성체 동물을 옮깁니다."
    ),
    "text.industrialforegoing.book.animal_resource_harvester": (
        "전력을 공급하면 동물에게 {양동이}와 {가위}를 사용해 소의 젖을 짜고 양의 "
        "털을 깎습니다.@L@@L@오징어에게서는 {먹물 주머니}도 얻습니다."
    ),
    "text.industrialforegoing.book.animal_stock_increaser": (
        "전력과 동물의 {먹이}를 공급하면 먹이를 주어 번식시킵니다. 각 동물에 맞는 "
        "번식 아이템이 필요합니다.\\@L@\\@L@작업 영역에는 동시에 최대 {35}마리만 "
        "둘 수 있습니다."
    ),
    "text.industrialforegoing.book.biofuel_generator": (
        "바이오연료를 공급하면 전력을 생산합니다. 바이오연료 {양동이} 하나로 "
        "160RF/t, 총 {640,000}RF를 생산합니다. {생물 반응기} 하나로 발전기 약 "
        "{28}대를 가동할 수 있습니다."
    ),
    "text.industrialforegoing.book.bioreactor": (
        "{전력}과 {생물 자원}을 공급하면 {바이오연료}를 생산합니다.@L@@L@"
        "서로 다른 아이템 하나마다 전체 효율이 {10}mb씩 증가하며, 서로 다른 아이템 "
        "{9}개를 사용하면 최대 효율로 {1440}mb를 생산합니다."
    ),
    "text.industrialforegoing.book.black_hole_controller": (
        "{블랙홀 유닛} 9개를 장착해 내용물에 접근할 수 있습니다. 따라서 아이템을 "
        "{2,147,483,647}개의 9배까지 저장할 수 있습니다."
    ),
    "text.industrialforegoing.book.black_hole_tank": (
        "한 종류의 유체를 최대 {2,147,483,647}mb까지 저장할 수 있습니다."
    ),
    "text.industrialforegoing.book.black_hole_unit": (
        "한 종류의 아이템을 최대 {2,147,483,647}개까지 저장할 수 있습니다."
    ),
    "text.industrialforegoing.book.block_destroyer": (
        "전력을 공급하면 앞의 블록을 {파괴}해 내부 인벤토리로 옮깁니다."
    ),
    "text.industrialforegoing.book.block_placer": (
        "전력을 공급하면 내부 인벤토리의 블록을 앞쪽에 {배치}합니다."
    ),
    "text.industrialforegoing.book.crop_enrich_material_injector": (
        "전력과 비료를 공급하면 작물과 묘목에 뼛가루 효과를 적용합니다.@L@@L@"
        "사용 가능한 비료: {뼛가루}, {Industrial Foregoing} 비료, {Forestry} 비료."
    ),
    "text.industrialforegoing.book.crop_recolector": (
        "전력을 공급하면 다 자란 작물을 {수확}하고 나무를 벱니다. 호박, 수박, 네더 "
        "사마귀도 처리합니다. 작업할 때마다 {슬러지 정제기}에서 재료로 바꿀 수 있는 "
        "{슬러지}가 조금 생성됩니다. 탱크가 가득 차도 기계 속도는 {느려지지 않습니다}."
    ),
    "text.industrialforegoing.book.crop_sower": (
        "{식물 수확기}가 수확할 씨앗과 묘목을 심습니다. 자물쇠를 눌러 슬롯을 "
        "{잠그면} 입력 아이템을 {필터링}할 수 있습니다.@L@@L@배경의 {색상}은 블록 "
        "{윗면}의 같은 색 영역을 나타냅니다."
    ),
    "text.industrialforegoing.book.dye_mixer": (
        "일반 조합보다 효율적으로 {염료}를 생산합니다.@L@@L@{빨간색}, {초록색}, "
        "{파란색} 염료를 넣으면 각 색상 버퍼가 채워집니다. {레이저 렌즈}를 넣으면 "
        "해당 색에 집중해 지정한 염료를 생산합니다."
    ),
    "text.industrialforegoing.book.enchantment_aplicator": (
        "전력을 공급하면 {모루}처럼 작동하되, 플레이어 경험치 대신 {정수}를 "
        "사용합니다."
    ),
    "text.industrialforegoing.book.enchantment_extractor": (
        "전력, {책}, {마법이 부여된} 아이템을 공급하면 아이템의 마법 부여 {1}개를 "
        "제거해 책에 옮깁니다.@L@@L@이 과정에서 아이템은 손상되지 않습니다."
    ),
    "text.industrialforegoing.book.enchantment_invoker": (
        "전력, {마법 부여 가능한} 아이템, {정수}를 공급하면 {마법 부여대}처럼 "
        "아이템에 마법을 부여합니다.@L@@L@레벨 {30} 마법 부여에는 정수 "
        "{3}양동이를 사용합니다."
    ),
    "text.industrialforegoing.book.enchantment_refiner": (
        "전력과 {아무} 아이템이나 공급하면 마법이 부여된 아이템과 그렇지 않은 "
        "아이템을 {분류}합니다.@L@@L@마법이 부여된 아이템은 {위쪽} 줄로, 그렇지 "
        "않은 아이템은 {아래쪽} 줄로 이동합니다."
    ),
    "text.industrialforegoing.book.energy_field_provider": (
        "{에너지장 업그레이드}는 작동하는 기계의 업그레이드 슬롯에 넣는 아이템으로, "
        "내부 버퍼의 {전력}을 기계에 공급합니다.@L@@L@{에너지장 공급기}는 자신과 "
        "{연결}되어 있고 {범위} 안에 있는 업그레이드의 내부 버퍼를 충전합니다."
    ),
    "text.industrialforegoing.book.fluid_crafter": (
        "{유체 조합기}는 조합법에서 {한} 종류의 유체가 든 {양동이}를 대신해 "
        "조합합니다. 격자에 아이템을 놓고 {잠근} 다음, 격자에 아이템을 공급하고 "
        "탱크에 유체를 넣으세요.@L@@L@같은 아이템이 여러 개 필요한 조합법은 "
        "{아이템 분할기}를 사용하면 편리합니다."
    ),
    "text.industrialforegoing.book.fluid_pump": (
        "유체 위에 설치하면 그 유체를 {필터}로 삼아 작업 영역의 같은 유체를 모두 "
        "퍼 올립니다. 작업 영역 안의 유체 {아래쪽}까지 찾아 함께 배출합니다.@L@@L@"
        "배출한 자리는 모두 {조약돌}로 바뀝니다."
    ),
    "text.industrialforegoing.book.hydrator": (
        "전력을 공급하면 작업 영역에 있는 작물의 {성장 속도}를 높입니다."
    ),
    "text.industrialforegoing.book.item_splitter": (
        "허용한 {출력} 면의 각 슬롯에 지정한 스택 크기로 아이템을 {분할}합니다."
    ),
    "text.industrialforegoing.book.laser_base": (
        "{레이저 드릴}로 완전히 충전하면 깊이와 생물군계에 따라 광석을 생산합니다."
        "@L@@L@{레이저 렌즈}를 넣으면 특정 광석의 생산 확률을 높일 수 있습니다."
        "@L@@L@{레이저 렌즈(반전)}를 사용하면 해당 광석의 확률을 낮추고 다른 광석의 "
        "확률을 조금 높입니다.@L@@L@{확률은 JEI에서 확인하세요}."
    ),
    "text.industrialforegoing.book.laser_drill": (
        "{레이저 베이스}에서 {1}블록 떨어진 곳에 설치하면 전력을 보내 충전합니다."
        "@L@@L@잘못 설치하면 위에 이를 알리는 이름표가 표시됩니다."
    ),
    "text.industrialforegoing.book.latex_processing_unit": (
        "{전력}, {물}, {라텍스}를 공급하면 작은 건조 고무를 생산합니다.@L@@L@"
        "작은 건조 고무 {1}개를 만드는 데 라텍스 {75}mb와 물 {1000}mb를 사용합니다."
    ),
    "text.industrialforegoing.book.lava_fabricator": (
        "많은 양의 전력을 공급하면 {용암}을 생산합니다."
    ),
    "text.industrialforegoing.book.material_stonework_factory": (
        "전력을 공급하면 {조약돌}을 생성합니다. 기계는 {4}가지 작업, 즉 아이템 "
        "{제련}, {2x2} 조합, {분쇄}, {3x3} 조합을 수행할 수 있습니다.@L@@L@예를 "
        "들어 첫 슬롯에 조약돌이 있고 첫 작업이 '제련'이면 돌로 바뀝니다. 두 번째 "
        "작업을 2x2 조합으로 정하면 돌은 돌 벽돌로 바뀝니다."
    ),
    "text.industrialforegoing.book.mob_detector": (
        "앞에 있는 개체 수에 따라 뒤쪽으로 {레드스톤 신호}를 출력합니다."
    ),
    "text.industrialforegoing.book.mob_duplicator": (
        "전력, {정수}, 개체가 든 {몹 포획기}를 공급하면 주변에 해당 개체를 "
        "생성합니다.@L@@L@주변 개체 수를 {계산}해 너무 많으면 생성을 멈춥니다."
    ),
    "text.industrialforegoing.book.mob_relocator": (
        "전력을 공급하면 플레이어가 공격한 것처럼 앞의 개체를 {처치}합니다.@L@@L@"
        "떨어진 아이템을 {수집}하고 경험치 구슬을 {정수}로 바꿉니다. "
        "{성체 필터 업그레이드}를 장착하면 성체 몹만 처치합니다."
    ),
    "text.industrialforegoing.book.mob_slaughter_factory": (
        "전력을 공급하면 앞의 개체를 {분쇄}해 {액상 고기}를 생산합니다.@L@@L@"
        "이 과정에서는 아이템이나 경험치를 {떨어뜨리지 않습니다}.@L@@L@"
        "{약간의 분홍색} 슬라임도 함께 생산합니다."
    ),
    "text.industrialforegoing.book.oredictionary_converter": (
        "같은 {광물 사전} 항목을 가진 아이템을 필터에 지정한 아이템으로 바꿉니다."
    ),
    "text.industrialforegoing.book.ore_processor": (
        "{섬세한 손길}로 채굴한 광석을 일반 생산물로 분해합니다.@L@@L@{정수}를 "
        "공급하면 행운 효과를 적용해 분해합니다."
    ),
    "text.industrialforegoing.book.petrified_fuel_generator": (
        "{고체 연료}를 공급하면 전력을 생산합니다. 틱당 {RF} 생산량은 연료의 "
        "{연소 시간}으로 정해지며, 연소 시간이 길수록 틱당 {RF} 생산량이 "
        "늘어납니다.@L@@L@참고: 모든 연료는 같은 시간 동안 연소합니다."
    ),
    "text.industrialforegoing.book.potion_enervator": (
        "전력을 공급하면 고급 {양조기}처럼 작동합니다.@L@@L@먼저 유리병을 물로 "
        "{채우고}, 위쪽 줄의 재료를 왼쪽부터 {순서대로} {양조}합니다.@L@@L@"
        "현재 작업은 {화살표}를 따라 확인하세요."
    ),
    "text.industrialforegoing.book.protein_generator": (
        '"단백질을 공급하면 전력을 생산합니다. 단백질 {양동이} 하나로 320RF/t, '
        "총 {1,280,000}RF를 생산합니다."
    ),
    "text.industrialforegoing.book.protein_reactor": (
        "{전력}과 {동물 생산물}을 공급하면 {단백질}을 생산합니다.@L@@L@서로 다른 "
        "아이템 하나마다 전체 효율이 {10}mb씩 증가하며, 서로 다른 아이템 {9}개를 "
        "사용하면 최대 효율로 {1440}mb를 생산합니다."
    ),
    "text.industrialforegoing.book.resourceful_furnace": (
        "일반 {화로}처럼 작동하지만 아이템을 한 번에 {3}개 제련하며, 아이템을 "
        "제련할 때마다 소량의 {정수}를 생산합니다."
    ),
    "text.industrialforegoing.book.sewage_composter_solidifier": (
        "전력과 오물 {2}양동이를 공급하면 {비료}로 굳힙니다."
    ),
    "text.industrialforegoing.book.sludge_refiner": (
        "전력과 슬러지 {1}양동이(식물 수확기에서 생산)를 공급하면 {흙 계열} 재료를 "
        "생산합니다.@L@@L@{생산 재료와 확률은 JEI의 슬러지 정제기 사용처에서 "
        "확인하세요}."
    ),
    "text.industrialforegoing.book.spores_recreator": (
        "전력, 물 {1}양동이, 아무 종류의 {버섯}이나 공급하면 내부에서 증식시킵니다."
    ),
    "text.industrialforegoing.book.tree_fluid_extractor": (
        "{원목} 앞에 설치하면 {액상 라텍스}를 생산합니다.@L@@L@원목을 천천히 "
        "{소모}하며, 같은 원목에 연결된 나무 유체 추출기마다 소모 속도가 빨라집니다."
    ),
    "text.industrialforegoing.book.villager_trade_exchanger": (
        "전력과 {주민}이 든 {몹 포획기}를 공급하면 주민과 자동으로 거래할 수 "
        "있습니다."
    ),
    "text.industrialforegoing.book.water_condensator": (
        "물 원천 블록과 맞닿은 면이 {2}개 이상이면 물을 모으기 시작합니다.@L@@L@"
        "원천 블록과 맞닿은 면이 많을수록 더 많은 물을 생산합니다."
    ),
    "text.industrialforegoing.book.water_resources_collector": (
        "{3x3} 크기의 물 웅덩이 위에 설치하면 자동으로 {낚시}합니다."
    ),
    "text.industrialforegoing.book.wither_builder": (
        "전력, 위더 해골 {3}개, 영혼 모래 {4}개를 공급하면 작업 영역에 위더 소환 "
        "구조물을 완성합니다."
    ),
    "text.industrialforegoing.book.accepted_items": "사용 가능 아이템:",
    "text.industrialforegoing.book.produced_items": "생산 아이템:",
    "text.industrialforegoing.book.welcome_manual": (
        "Industrial Foregoing 설명서에 오신 것을 환영합니다!@L@@L@먼저 원목 앞에 "
        "나무 유체 추출기를 설치해 라텍스를 모으세요. 라텍스 처리 장치에 라텍스와 "
        "물을 넣으면 작은 고무를 얻을 수 있습니다.@L@@L@{참고: 기계는 자동으로 "
        "배출하거나 끌어오지 않습니다! RF, FE, Tesla, Mek 전력을 사용할 수 있습니다.}"
    ),
    "text.industrialforegoing.book.mob_imprisonment_tool": (
        "손에 든 채 개체를 우클릭하면 해당 개체를 내부에 {보관}합니다."
    ),
    "text.industrialforegoing.book.meat_feeder": (
        "고기 공급기를 {인벤토리}에 넣고 {액상 고기}를 채우면 자동으로 플레이어에게 "
        "{먹이를 공급}합니다.@L@@L@일반 유체 용기처럼 작동합니다."
    ),
    "text.industrialforegoing.book.range_addon": (
        "일부 기계의 작업 {범위}를 늘립니다. 모든 기계가 이 업그레이드를 받는 것은 "
        "아닙니다."
    ),
    "text.industrialforegoing.book.straw": (
        "월드의 유체나 탱크 속 유체를 {마실} 수 있습니다. 유체에 따라 서로 다른 "
        "{효과}가 생길 수 있습니다.@L@@L@@L@@L@@L@(빨대로 생긴 나쁜 효과는 "
        "책임지지 않습니다.)"
    ),
    "text.industrialforegoing.book.pink_slime": (
        "월드에 {분홍색 슬라임 유체}를 놓으면 생성되는 {분홍색 슬라임}을 처치해 "
        "얻을 수 있습니다."
    ),
    "text.industrialforegoing.book.upgrades": (
        "Industrial Foregoing 자체에는 속도 업그레이드가 없지만, Tesla Core Lib의 "
        "{에너지 업그레이드}와 {속도 업그레이드}로 기계 속도를 높일 수 있습니다. "
        "다음 등급을 장착하려면 이전 등급이 먼저 설치되어 있어야 합니다."
    ),
    "text.industrialforegoing.book.plant_interactor": (
        "전력을 공급하면 작물과 과일을 {우클릭}해 수확하고 내부 인벤토리에 "
        "저장합니다. 저장할 수 없으면 땅에 떨어뜨립니다.@L@@L@{기본적으로 Pam's "
        "HarvestCraft의 과일과 식물도 지원합니다.}"
    ),
    "text.industrialforegoing.book.transfer_addon": (
        "전송 업그레이드는 형태가 다양하지만 {아이템}과 {유체}만 끌어오거나 밀어낼 "
        "수 있습니다.@L@@L@업그레이드를 {우클릭}하면 방향을 순환하고, 블록 면을 "
        "{웅크리고 우클릭}하면 그 방향을 선택합니다. 업그레이드에 {효율} 마법을 "
        "부여하면 전송량이 증가합니다."
    ),
    "text.industrialforegoing.book.fluiddictionary_converter": (
        "서로 다른 모드의 같은 계열 유체를 변환합니다. 가능한 조합법은 {JEI}에서 "
        "확인할 수 있습니다. 버튼을 눌러 원하는 유체를 선택하세요."
    ),
    "text.industrialforegoing.book.conveyors": (
        "컨베이어는 개체를 바라보는 방향으로 {밀어냅니다}. 여러 색상과 수직형이 "
        "있습니다.@L@@L@{발광석 가루}로 우클릭하면 더 빨라지고, {플라스틱}으로 "
        "우클릭하면 위의 아이템을 주울 수 없게 합니다.@PAGE@컨베이어의 옆면이나 "
        "가운데에는 여러 {업그레이드}를 장착할 수 있습니다. 업그레이드는 컨베이어의 "
        "{먼 쪽}에 놓이며, 웅크리고 우클릭하면 제거할 수 있습니다."
    ),
    "text.industrialforegoing.book.conveyor_upgrade_extraction": (
        "추출 업그레이드는 맞닿은 인벤토리에서 아이템을 {추출}해 컨베이어 위에 "
        "놓습니다.@L@@L@허용 목록이나 차단 목록 {필터}를 사용할 수 있으며, "
        "{발광석 가루}로 업그레이드하면 추출 속도가 빨라집니다. 수거되지 않은 "
        "아이템을 너무 많이 꺼냈다면 추출을 멈춥니다."
    ),
    "text.industrialforegoing.book.conveyor_upgrade_insertion": (
        "삽입 업그레이드는 자신과 닿은 아이템을 업그레이드 쪽에 맞닿은 인벤토리로 "
        "{삽입}합니다.@L@@L@허용 목록이나 차단 목록 {필터}를 사용할 수 있습니다. "
        "GUI에서 {범위}를 늘리면 업그레이드에 직접 닿은 아이템뿐 아니라 컨베이어 "
        "위의 모든 아이템을 가져옵니다."
    ),
    "text.industrialforegoing.book.conveyor_upgrade_detection": (
        "감지 업그레이드는 컨베이어 가운데에 장착하며, 개체가 지나가면 {레드스톤} "
        "신호를 출력합니다.@L@@L@허용 목록이나 차단 목록 {필터}를 사용할 수 있고, "
        "개체가 든 {몹 포획기}로 몹을 지정할 수 있습니다. GUI에서 {레드스톤 제어}를 "
        "반전할 수도 있습니다."
    ),
    "text.industrialforegoing.book.conveyor_upgrade_bouncing": (
        "튕김 업그레이드는 컨베이어 가운데에 장착하며, 개체를 컨베이어가 향한 "
        "방향의 공중으로 {발사}합니다.@L@@L@허용 목록이나 차단 목록 {필터}를 사용할 "
        "수 있고, 개체가 든 {몹 포획기}로 몹을 지정할 수 있습니다. GUI에서 수평과 "
        "수직 {속도}를 바꿀 수 있습니다."
    ),
    "text.industrialforegoing.book.conveyor_upgrade_dropping": (
        "낙하 업그레이드는 컨베이어 가운데에 장착하며, 개체를 바로 아래로 "
        "{떨어뜨리거나} 아래쪽 인벤토리에 아이템을 넣습니다.@L@@L@허용 목록이나 "
        "차단 목록 {필터}를 사용할 수 있고, 개체가 든 {몹 포획기}로 몹을 지정할 수 "
        "있습니다."
    ),
    "text.industrialforegoing.book.conveyor_upgrade_blinking": (
        "순간이동 업그레이드는 컨베이어 가운데에 장착하며, 개체를 컨베이어 앞의 "
        "짧은 거리로 {순간이동}시킵니다.@L@@L@허용 목록이나 차단 목록 {필터}를 "
        "사용할 수 있고, 개체가 든 {몹 포획기}로 몹을 지정할 수 있습니다. GUI에서 "
        "순간이동 {거리}를 설정할 수 있습니다."
    ),
    "text.industrialforegoing.book.conveyor_upgrade_splitting": (
        "분배 업그레이드는 개체를 업그레이드가 장착된 쪽으로 균등하게, 또는 설정한 "
        "비율에 따라 {분배}합니다.@L@@L@{비율}이 높을수록 그 방향으로 더 많은 "
        "개체가 이동합니다. GUI에서 비율을 설정할 수 있습니다."
    ),
    "text.industrialforegoing.book.froster": (
        "공급된 {물}을 매우 빠르게 회전시키고 {전력}으로 온도를 낮춰 차가운 물질을 "
        "만듭니다."
    ),
    "text.industrialforegoing.book.ore_washer": (
        "{액상 고기}와 {광석}을 공급하면 광석 조각을 고기로 씻어 추가 가공용 "
        "{생광석 고기}로 만듭니다."
    ),
    "text.industrialforegoing.book.ore_fermenter": (
        "{생광석 고기}를 {발효 광석 고기}로 가공해 크기를 키웁니다. 아래쪽에는 "
        "{열원}(뜨거운 유체, 불, 마그마 블록)이, 다른 면에는 {차가운 유체}(냉각 "
        "유체, 얼음 등)가 필요합니다."
    ),
    "text.industrialforegoing.book.ore_sieve": (
        "{발효 광석 고기}와 소량의 {모래}를 공급하면 고기에서 광석을 걸러 {가루}로 "
        "만듭니다."
    ),
    "text.industrialforegoing.book.fortune_addon": (
        "이 업그레이드를 지원하는 기계에 {행운/약탈} 효과를 추가합니다. "
        "업그레이드에 {행운} 마법을 부여해야 하며, 기계 작업에는 그 마법 레벨이 "
        "적용됩니다."
    ),
    "text.industrialforegoing.book.pitiful_fuel_generator": (
        "석화 연료 발전기와 같은 방식으로 작동하지만 {나무} 계열 연료만 받습니다."
    ),
    "text.industrialforegoing.book.infinity_drill": (
        "힘을 모두 잃은 강력한 드릴입니다. 충전할수록 더 빠르고 넓게 채굴할 수 "
        "있습니다. 전력을 아끼려면 {바이오연료}를 더 효율적인 연료로 사용할 수 "
        "있습니다. Shift+우클릭하면 채굴 범위를 바꿉니다.@L@@L@{후원자와 월드의 "
        "일부 희귀 몹을 통해 쉽게 달성할 수 있는 비밀이 숨겨져 있습니다.}"
    ),
}

TEXT_REPLACEMENTS = (
    ("인더스트리얼 포고잉", "Industrial Foregoing"),
    ("인더스트리얼 포어고잉", "Industrial Foregoing"),
    ("인더스트리얼 포어 고잉", "Industrial Foregoing"),
    ("산업 전술", "Industrial Foregoing"),
    ("머신 프레임", "기계 프레임"),
    ("기계 틀", "기계 프레임"),
    ("미천한", "조악한"),
    ("간단한 기계 프레임", "기본 기계 프레임"),
    ("발전된 기계 프레임", "고급 기계 프레임"),
    ("핑크 슬라임", "분홍색 슬라임"),
    ("핑크색 슬라임", "분홍색 슬라임"),
    ("드라이 러버", "건조 고무"),
    ("인첸트", "마법 부여"),
    ("인챈트", "마법 부여"),
    ("디스인챈트", "마법 추출"),
    ("에센스", "정수"),
    ("정수 양동이", "정수 양동이"),
    ("액체 고기", "액상 고기"),
    ("애드온", "업그레이드"),
    ("상위 버전으로 변환", "업그레이드"),
    ("업그레이드 기능", "업그레이드"),
    ("스포너", "생성기"),
    ("몹 감금 도구", "몹 포획기"),
    ("몹 투옥 도구", "몹 포획기"),
    ("소울샌드", "영혼 모래"),
    ("용광로", "화로"),
    ("아이언 기어", "철 기어"),
    ("골드 기어", "금 기어"),
    ("프로세싱", "처리"),
    ("클릭", "누르기"),
    ("마우스 오른쪽 버튼으로 누르기", "우클릭"),
    ("마우스 오른쪽 버튼을 누르기", "우클릭"),
    ("마우스 오른쪽 버튼", "우클릭"),
    ("몰래 우클릭", "웅크리고 우클릭"),
    ("몰래", "웅크린 상태로"),
)

BRACE_OVERRIDES = {
    "Adult Filter": "성체 필터",
    "Adult Filter Addon": "성체 필터 업그레이드",
    "Biofuel": "바이오연료",
    "Bioreactor": "생물 반응기",
    "Black Hole Units": "블랙홀 유닛",
    "Efficiency": "효율",
    "Energy Field Addon": "에너지장 업그레이드",
    "Energy Field Provider": "에너지장 공급기",
    "Energy Upgrades": "에너지 업그레이드",
    "Essence": "정수",
    "Fertilizer": "비료",
    "Fortune": "행운",
    "Industrial Foregoing's": "Industrial Foregoing의",
    "Item Splitter": "아이템 분할기",
    "Laser Base": "레이저 베이스",
    "Laser Drills": "레이저 드릴",
    "Laser Lens": "레이저 렌즈",
    "Laser Lens (Inverted)": "레이저 렌즈(반전)",
    "Liquid Latex": "액상 라텍스",
    "Liquid Meat": "액상 고기",
    "Mob Imprisonent Tool": "몹 포획기",
    "Mob Imprisonment Tool": "몹 포획기",
    "Pink Slime": "분홍색 슬라임",
    "Pink Slime Fluid": "분홍색 슬라임 유체",
    "Plant Gatherer": "식물 수확기",
    "Redstone Signal": "레드스톤 신호",
    "Sewage": "오물",
    "Silk Touched": "섬세한 손길",
    "Sludge Refiner": "슬러지 정제기",
    "Speed Upgrades": "속도 업그레이드",
    "Villager": "주민",
    "anvil": "모루",
    "baby": "새끼",
    "bio materials": "생물 자원",
    "biofuel": "바이오연료",
    "bonemeal": "뼛가루",
    "book": "책",
    "breeding": "번식",
    "brewing stand": "양조기",
    "bucket": "양동이",
    "cobblestone": "조약돌",
    "collect": "수집",
    "consume": "소비",
    "drop": "생산물",
    "dust": "가루",
    "dye": "염료",
    "enchanted": "마법이 부여된",
    "enchanting table": "마법 부여대",
    "extract": "추출",
    "feed": "먹이 공급",
    "fermented ore meat": "발효 광석 고기",
    "filter": "필터",
    "fish": "물고기",
    "fluid crafter": "유체 조합기",
    "fluids": "유체",
    "food": "음식",
    "fortune/looting": "행운/약탈",
    "furnace": "화로",
    "glowstone dust": "발광석 가루",
    "grow": "성장",
    "harvest": "수확",
    "insert": "삽입",
    "inventory": "인벤토리",
    "items": "아이템",
    "kill": "처치",
    "latex": "라텍스",
    "lava": "용암",
    "liquid meat": "액상 고기",
    "log": "원목",
    "mushroom": "버섯",
    "ore": "광석",
    "output": "출력",
    "place": "배치",
    "plastic": "플라스틱",
    "power": "전력",
    "protein": "단백질",
    "range": "범위",
    "raw ore meat": "생광석 고기",
    "redstone": "레드스톤",
    "redstone control": "레드스톤 제어",
    "sand": "모래",
    "shears": "가위",
    "sludge": "슬러지",
    "smelt": "제련",
    "solid fuel": "고체 연료",
    "split": "분할",
    "teleport": "순간이동",
    "upgrades": "업그레이드",
    "water": "물",
    "wood": "나무",
}

ALLOWED_EXACT_KEYS = {
    "__comment",
    "__comment1",
    "__comment2",
    "__comment3",
    "__comment4",
    "itemGroup.industrialforegoingsouls",
    "text.industrialforegoing.proxy.client.alt_f4",
}


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def candidate() -> dict[str, object]:
    """기존 한국어까지 포함한 전 항목의 독립 자동 번역 후보를 만든다."""
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    english_by_namespace = {
        namespace: load_json(WORK_ROOT / namespace / "en_us.json")
        for namespace in NAMESPACES
    }
    requests = {
        value
        for english in english_by_namespace.values()
        for value in english.values()
        if isinstance(value, str)
        and value not in KEY_OVERRIDES.values()
        and not family_goal.is_allowed_original(value)
        and not isinstance(cache.get(value), str)
    }
    failures: list[str] = []
    if requests:
        completed = 0
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(ars_family.request_translation, source): source
                for source in sorted(requests)
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                    completed += 1
                    if completed % 25 == 0:
                        write_json(CACHE_FILE, cache)
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("자동 번역 후보 생성 실패:\n" + "\n".join(failures))

    candidates: dict[str, dict[str, str]] = {}
    for namespace, english in english_by_namespace.items():
        namespace_candidates: dict[str, str] = {}
        for key, source in english.items():
            if not isinstance(source, str):
                raise TypeError(f"문자열이 아닌 언어 값: {namespace}:{key}")
            if key in KEY_OVERRIDES:
                translated = KEY_OVERRIDES[key]
            elif family_goal.is_allowed_original(source):
                translated = source
            else:
                translated = cache[source]
            namespace_candidates[key] = translated
        candidates[namespace] = namespace_candidates
    write_json(CANDIDATE_FILE, candidates)
    report = {
        "keys": sum(len(value) for value in english_by_namespace.values()),
        "candidate_keys": sum(len(value) for value in candidates.values()),
        "review_scope": "bundled_and_missing_korean_all_retranslated_for_review",
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "auto_candidate_report.json", report)
    return report


def reviewed_name(key: str, bundled: str, candidate_value: str) -> str:
    """아이템·블록 이름을 기존 후보와 영어 원문을 함께 대조해 정규화한다."""
    value = (
        bundled
        if bundled and not re.search(r"[A-Za-z]{3,}", bundled)
        else candidate_value
    )
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    value = value.replace("바이오 리액터", "생물 반응기")
    value = value.replace("컨트롤러", "제어기")
    value = value.replace("레이블", "라벨")
    value = value.replace("어두운 유리", "암흑 유리")
    value = value.replace("오물", "오물")
    if key.startswith("block.industrialforegoing.machine_frame_"):
        raise AssertionError(f"기계 프레임은 명시적 번역이 필요합니다: {key}")
    return value


def translate_braces(value: str) -> str:
    """설명서 강조용 중괄호 본문을 검수된 한국어로 바꾼다."""

    def replace(match: re.Match[str]) -> str:
        source = match.group(1)
        if re.fullmatch(r"[\d,]+(?:x\d+)?", source, re.I):
            return match.group(0)
        translated = BRACE_OVERRIDES.get(source)
        if translated is None:
            return match.group(0)
        return "{" + translated + "}"

    return re.sub(r"\{([^{}]+)\}", replace, value)


def reviewed_value(
    key: str,
    source: str,
    bundled: str,
    candidate_value: str,
) -> str:
    if key in BOOK_OVERRIDES:
        return BOOK_OVERRIDES[key]
    if key in KEY_OVERRIDES:
        return KEY_OVERRIDES[key]
    if key.startswith(("block.", "item.", "fluid_type.", "entity.")):
        value = reviewed_name(key, bundled, candidate_value)
    elif bundled and source != bundled:
        value = bundled
    else:
        value = candidate_value
    value = translate_braces(value)
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    value = value.replace("기계 위에 배치 된", "기계 위에 놓인")
    value = value.replace("할 수 있습니다.", "할 수 있습니다.")
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    return value


def normalize() -> dict[str, object]:
    """모든 기존·신규 한국어를 영어 원문과 대조한 검수값으로 교체한다."""
    candidates = load_json(CANDIDATE_FILE)
    changed = 0
    reviewed = 0
    unresolved: list[str] = []
    source_root = resolve_source_root()
    bundled_by_namespace: dict[str, dict[str, object]] = {}
    for target in family_goal.targets_for(FAMILY):
        jar = family_goal.find_jar(source_root, target.jar_prefix)
        _, korean_path = family_goal.language_paths(target.namespace)
        with ZipFile(jar) as archive:
            bundled_by_namespace[target.namespace] = (
                family_goal.load_json_bytes(archive.read(korean_path))
                if korean_path in archive.namelist()
                else {}
            )
    for namespace in NAMESPACES:
        root = WORK_ROOT / namespace
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        namespace_candidates = candidates[namespace]
        for key, source in english.items():
            if not isinstance(source, str) or not isinstance(korean[key], str):
                raise TypeError(f"문자열이 아닌 언어 값: {namespace}:{key}")
            bundled = bundled_by_namespace[namespace].get(key, "")
            if not isinstance(bundled, str):
                raise TypeError(f"문자열이 아닌 기존 한국어 값: {namespace}:{key}")
            translated = reviewed_value(key, source, bundled, namespace_candidates[key])
            errors = family_goal.validate_family_value(FAMILY, key, source, translated)
            if errors:
                raise ValueError("; ".join(errors))
            reviewed += 1
            if korean[key] != translated:
                korean[key] = translated
                changed += 1
            if (
                source == translated
                and key not in ALLOWED_EXACT_KEYS
                and not family_goal.is_allowed_original(source)
            ):
                unresolved.append(f"{namespace}:{key}")
        write_json(root / "ko_kr.json", korean)
    report = {
        "keys_reviewed": reviewed,
        "changed": changed,
        "unresolved": len(unresolved),
        "unresolved_examples": unresolved[:30],
        "review_status": "full_existing_korean_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    untranslated: list[str] = []
    reviewed = 0
    for namespace in NAMESPACES:
        root = WORK_ROOT / namespace
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        if list(english) != list(korean):
            errors.append(f"키 또는 순서 불일치: {namespace}")
            continue
        for key, source in english.items():
            target = korean[key]
            errors.extend(
                family_goal.validate_family_value(FAMILY, key, source, target)
            )
            reviewed += 1
            if (
                source == target
                and key not in ALLOWED_EXACT_KEYS
                and not family_goal.is_allowed_original(source)
            ):
                untranslated.append(f"{namespace}:{key}")
    if untranslated:
        errors.append(f"미번역 키: {untranslated[:30]}")
    report = {
        "keys_reviewed": reviewed,
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", report)
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("candidate", "normalize", "verify"))
    args = parser.parse_args()
    resolve_source_root()
    if args.command == "candidate":
        result = candidate()
        status = 0
    elif args.command == "normalize":
        result = normalize()
        status = 0
    else:
        result, status = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
