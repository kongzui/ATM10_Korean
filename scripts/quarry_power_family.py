#!/usr/bin/env python3
"""QuarryPlus, Generator Galore와 Energy Meter의 표시 문자열을 번역·검증한다."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "quarry_power"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
RESOURCEPACK_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
GUIDE_INTERNAL = "assets/energymeter/guideme_guides/guide.json"
GUIDE_OUTPUT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/energymeter/guideme_guides/guide.json"
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[./xX×]\d+)*")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
ALLOWED_LATIN = {
    "Energy",
    "FastTransferLib",
    "Galore",
    "Generator",
    "GuideME",
    "Meter",
    "QuarryPlus",
    "RebornCore",
    "Shift",
    "smB",
}

NAMESPACES = {
    "quarryplus": "AdditionalEnchantedMiner-*.jar",
    "generatorgalore": "generatorgalore-*.jar",
    "energymeter": "energymeter-*.jar",
}

QUARRY_OVERRIDES = {
    "_comment": "한국어 언어 파일입니다.",
    "block.quarryplus.InfMJSrc": "무한 MJ 전원",
    "block.quarryplus.book_mover": "책 마법 부여 이동기",
    "block.quarryplus.debug_storage": "쿼리 디버그 저장소",
    "block.quarryplus.frame": "QuarryPlus 프레임",
    "block.quarryplus.mining_well": "마이닝 웰 플러스",
    "block.quarryplus.mover": "마법 부여 이동기",
    "block.quarryplus.plainpipe": "마이닝 웰 플러스 파이프",
    "block.quarryplus.quarry": "QuarryPlus",
    "block.quarryplus.quarryplus": "구형 QuarryPlus",
    "block.quarryplus.remote_placer": "원격 배치기",
    "block.quarryplus.spawner_controller": "생성기 제어기",
    "block.quarryplus.waterlogged_chunk_marker": "물에 잠긴 청크 마커",
    "block.quarryplus.waterlogged_flexible_marker": "물에 잠긴 유연한 마커",
    "block.quarryplus.waterlogged_marker": "물에 잠긴 마커 플러스",
    "chat.flexiblemarker.area": "새 영역을 설정했습니다.",
    "chat.flexiblemarker.pos": "새 기계 위치를 %s(으)로 설정했습니다.",
    "chat.flexiblemarker.reset": "제어기 설정을 초기화했습니다.",
    "config.jade.plugin_quarryplus.jade_plugin": "QuarryPlus 플러그인",
    "enchantment.quarryplus.quarry_pickaxe": "쿼리 마법 부여",
    "gui.forward": "앞으로",
    "gui.infmjsrc.itv": "간격(틱)",
    "gui.infmjsrc.tickinfo": "20틱 = 1초",
    "item.quarryplus.dimensionmirror": "차원 거울",
    "item.quarryplus.electric_armor": "전기 갑옷 플러스",
    "item.quarryplus.filter_module": "공허 모듈",
    "item.quarryplus.liquidselector": "액체 선택기",
    "item.quarryplus.listeditor": "목록 편집기",
    "item.quarryplus.magicmirror": "마법 거울",
    "item.quarryplus.overworldmirror": "오버월드 거울",
    "item.quarryplus.remote_controller": "원격 제어기",
    "item.quarryplus.repeat_tick_module": "고속 작업 모듈",
    "item.quarryplus.status_checker": "상태 확인기",
    "itemGroup.flexiblemarker": "유연한 마커",
    "pp.copy": "설정 복사하기",
    "pp.copy.select": "설정을 복사할 원본 방향을 선택하세요",
    "pp.list.setting": "정렬된 펌프 플러스 추출 가능 유체 목록 - 방향:",
    "pp.set.select": "설정을 변경할 방향을 선택하세요",
    "qp.list.setting": "플러스 기계의 %s 활성 블록 목록",
    "quarryplus.chat.adv_quarry_no_space": "이 기계에는 작업할 공간이 부족합니다",
    "quarryplus.chat.bedrock_module_description": (
        "기계에 설치하면 기반암을 제거합니다."
    ),
    "quarryplus.chat.current_mode": "현재 %s 모드로 작업 중입니다",
    "quarryplus.chat.disable_item_message": "이 아이템은 비활성화되었습니다",
    "quarryplus.chat.disable_message": (
        "%s이(가) 비활성화되어 있습니다. 설정에서 활성화하세요."
    ),
    "quarryplus.chat.give_exp": "%s 경험치를 지급했습니다.",
    "quarryplus.chat.give_exp_point": "%s 경험치 지급",
    "quarryplus.chat.marker_already_connected": "이 마커는 이미 연결되어 있습니다",
    "quarryplus.chat.marker_connected": "마커를 연결했습니다",
    "quarryplus.chat.marker_failed": "마커를 연결하지 못했습니다",
    "quarryplus.chat.not_available_platform": "이 아이템은 %s에서 사용할 수 없습니다",
    "quarryplus.chat.plus_enchantments": (
        "---- 이 플러스 기계에는 다음 마법 부여가 있습니다"
    ),
    "quarryplus.chat.pump_range.num": ("현재 펌프 플러스가 반경 %s청크를 탐색합니다"),
    "quarryplus.chat.pump_range.quarry": (
        "현재 펌프 플러스가 쿼리 영역의 청크를 탐색합니다"
    ),
    "quarryplus.chat.quarry.restart": "쿼리를 재시작했습니다",
    "quarryplus.chat.quarry_no_space": "이 쿼리에는 작업할 공간이 부족합니다",
    "quarryplus.chat.replacer_module": "교체 모듈: %s.",
    "quarryplus.chat.set_remove_bedrock": "기반암 제거 설정: %s",
    "quarryplus.chat.warn_cd_limit": "영역이 설정의 제한값보다 너무 큽니다.",
    "quarryplus.chat.warn_protected_area": (
        "영역에 보호된 청크가 있어 쿼리가 중지되었습니다."
    ),
    "quarryplus.chat.y_level": "쿼리가 Y=%s까지 채굴합니다.",
    "quarryplus.gui.adv_quarry.area_frame": "영역 프레임",
    "quarryplus.gui.adv_quarry.chunk_by_chunk": "청크 단위",
    "quarryplus.gui.adv_quarry.experimental": "실험적",
    "quarryplus.gui.adv_quarry.modules": "모듈",
    "quarryplus.gui.adv_quarry.ready_to_start": "시작 준비 완료",
    "quarryplus.gui.adv_quarry.start": "시작",
    "quarryplus.gui.blacklist": "차단 목록",
    "quarryplus.gui.mover.move_enchantment": "이 마법 부여 이동",
    "quarryplus.gui.mover.next": "다음",
    "quarryplus.gui.mover.previous": "이전",
    "quarryplus.gui.of": "%2$s 중 %1$s",
    "quarryplus.status.fluid_empty": "유체 저장소가 비어 있습니다.",
    "quarryplus.status.item": "총 아이템 %s개",
    "quarryplus.status.item_empty": "아이템 저장소가 비어 있습니다.",
    "quarryplus.tooltip.advpump": (
        "이 블록은 독립형 펌프입니다.%1$s유체 블록 위에 설치하세요."
    ),
    "quarryplus.tooltip.advpump.gui_delete": (
        "켜짐: 유체를 제거합니다...\n물을 제거할 때 유용합니다\n"
        "꺼짐: 유체를 탱크로 옮깁니다."
    ),
    "quarryplus.tooltip.blockpump": (
        "이 블록은 %1$s의 부착물입니다.%2$s%1$s 옆에 설치하세요."
    ),
    "quarryplus.tooltip.creative_generator": "쿼리에서만 작동합니다",
    "quarryplus.tooltip.debug_only": "디버그 전용",
    "quarryplus.tooltip.debug_storage": "삽입만 가능하며 추출할 수 없습니다",
    "quarryplus.tooltip.exp_module": "경험치: ",
    "quarryplus.tooltip.exp_pump": (
        "이 블록은 %1$s와(과) %2$s의 부착물입니다.%3$s기계 옆에 설치하세요."
    ),
    "quarryplus.tooltip.filter_module_1": "우클릭해 등록",
    "quarryplus.tooltip.filter_module_2": "쿼리가 채굴한 아이템을 제거합니다",
    "quarryplus.tooltip.filter_module_rows": "행: %s",
    "quarryplus.tooltip.item_disable_message": ("비활성화됨. 설정에서 활성화하세요."),
    "quarryplus.tooltip.placer_plus": ("레드스톤 횃불로 우클릭해 모드를 변경합니다."),
    "quarryplus.tooltip.quarry_dont_place": "월드에 절대 설치하지 마세요.",
    "quarryplus.tooltip.quarry_may_crash": "이 블록은 충돌을 일으킬 수 있습니다.",
    "quarryplus.tooltip.quarry_screen.bedrock_toggle": (
        "기반암 모듈을 든 채 쿼리를 우클릭해 전환합니다"
    ),
    "quarryplus.tooltip.quarry_screen.remove_fluids": (
        "영역의 유체를 제거하려면 선택하세요"
    ),
    "quarryplus.tooltip.remove_bedrock_off": "기반암 제거: 꺼짐",
    "quarryplus.tooltip.remove_bedrock_on": "기반암 제거: 켜짐",
    "quarryplus.tooltip.repeat_tick_module": "기계의 작업 속도를 높입니다",
    "quarryplus.tooltip.replacer": (
        "이 블록은 %1$s와(과) %2$s의 부착물입니다.%3$s기계 옆에 설치하세요."
    ),
    "tag.block.quarryplus.markers": "쿼리 마커",
    "tag.item.quarryplus.markers": "쿼리 마커",
    "tag.item.quarryplus.quarry_pickaxes": "쿼리 곡괭이",
    "text.autoconfig.quarryplus.option.adv_pump": "고급 펌프",
    "text.autoconfig.quarryplus.option.adv_pump.advPumpEnergyCapacity": (
        "고급 펌프 에너지 용량"
    ),
    "text.autoconfig.quarryplus.option.adv_pump.advPumpEnergyRemoveFluid": (
        "고급 펌프 유체 제거 에너지"
    ),
    "text.autoconfig.quarryplus.option.adv_quarry": "청크 파괴자",
    "text.autoconfig.quarryplus.option.adv_quarry.advQuarryEnergyBreakBlock": (
        "청크 파괴자 블록 파괴 에너지"
    ),
    "text.autoconfig.quarryplus.option.adv_quarry.advQuarryEnergyCapacity": (
        "청크 파괴자 에너지 용량"
    ),
    "text.autoconfig.quarryplus.option.adv_quarry.advQuarryEnergyMakeFrame": (
        "청크 파괴자 프레임 생성 에너지"
    ),
    "text.autoconfig.quarryplus.option.adv_quarry.advQuarryEnergyMoveHead": (
        "청크 파괴자 헤드 이동 에너지"
    ),
    "text.autoconfig.quarryplus.option.adv_quarry.advQuarryEnergyRemoveFluid": (
        "청크 파괴자 유체 제거 에너지"
    ),
    "text.autoconfig.quarryplus.option.common.convertDeepslateOres": (
        "심층암 광석 변환"
    ),
    "text.autoconfig.quarryplus.option.common.removeFrameAfterQuarryIsRemoved": (
        "쿼리 제거 후 프레임 제거"
    ),
    "text.autoconfig.quarryplus.option.common.removesCommonMaterialAdvQuarry": (
        "청크 파괴자의 일반 재료 제거"
    ),
    "text.autoconfig.quarryplus.option.filler": "필러",
    "text.autoconfig.quarryplus.option.filler.fillerEnergyBreakBlock": (
        "필러 블록 파괴 에너지"
    ),
    "text.autoconfig.quarryplus.option.filler.fillerEnergyCapacity": (
        "필러 에너지 용량"
    ),
    "text.autoconfig.quarryplus.option.power.creativeGeneratorGeneration": (
        "크리에이티브 발전기 발전량"
    ),
    "text.autoconfig.quarryplus.option.quarry.quarryEnergyBreakBlock": (
        "QuarryPlus 블록 파괴 에너지"
    ),
    "text.autoconfig.quarryplus.option.quarry.quarryEnergyCapacity": (
        "QuarryPlus 에너지 용량"
    ),
    "text.autoconfig.quarryplus.option.quarry.quarryEnergyMakeFrame": (
        "QuarryPlus 프레임 생성 에너지"
    ),
    "text.autoconfig.quarryplus.option.quarry.quarryEnergyMoveHead": (
        "QuarryPlus 헤드 이동 에너지"
    ),
    "text.autoconfig.quarryplus.option.quarry.quarryEnergyRemoveFluid": (
        "QuarryPlus 유체 제거 에너지"
    ),
    "tof.already_error": "이 블록은 이미 추가되어 있습니다!!",
    "tof.block_id": "블록 ID",
    "tof.bottom": "맨 아래로",
    "tof.error": "오류",
    "tof.fluid_id": "유체 이름(간격)",
    "tof.meta": "메타데이터",
    "tof.tips_meta": "팁: 메타데이터는 대부분 0입니다",
    "tof.top": "맨 위로",
    "tooltip.flexiblemarker.remote_pos": "위치 %s, %s, %s / %s",
    "yog.armor.hover.off": "호버 모드를 비활성화했습니다.",
    "yog.armor.hover.on": "호버 모드를 활성화했습니다.",
    "yog.spawner.setting": "생성기에서 생성할 개체를 선택하세요",
}

GENERATOR_NAMES = {
    "copper": "구리",
    "culinary": "요리",
    "diamond": "다이아몬드",
    "emerald": "에메랄드",
    "enchantment": "마법 부여",
    "ender": "엔더",
    "gold": "금",
    "halitosis": "구취",
    "honey": "꿀",
    "iron": "철",
    "magmatic": "마그마",
    "netherite": "네더라이트",
    "netherstar": "네더의 별",
    "obsidian": "흑요석",
    "potion": "물약",
}

GENERATOR_STATIC = {
    "generatorgalore.recipe.fluid_fuel": "액체 연료",
    "generatorgalore.recipe.solid_fuel": "고체 연료",
    "generatorgalore.screen.empty": "비어 있음",
    "generatorgalore.screen.energy_level": "에너지: %s",
    "generatorgalore.screen.fluid_level": "%s: %s",
    "generatorgalore.screen.fuel_time": "남은 연료 시간: %s",
    "generatorgalore.screen.fuel_type": "연료 종류: %s",
    "generatorgalore.screen.generation_rate": "발전량: %s FE/t",
    "generatorgalore.screen.max_energy": "최대 에너지: %s FE",
    "generatorgalore.screen.transfer_rate": "전송 속도: %s FE/t",
    "itemGroup.generatorgalore": "Generator Galore",
}

UPGRADES = {
    "copper_to_iron": ("구리", "철"),
    "culinary_to_honey": ("요리", "꿀"),
    "culinary_to_potion": ("요리", "물약"),
    "diamond_to_emerald": ("다이아몬드", "에메랄드"),
    "diamond_to_netherite": ("다이아몬드", "네더라이트"),
    "diamond_to_obsidian": ("다이아몬드", "흑요석"),
    "ender_to_halitosis": ("엔더", "구취"),
    "gold_to_culinary": ("금", "요리"),
    "gold_to_diamond": ("금", "다이아몬드"),
    "iron_to_gold": ("철", "금"),
    "netherite_to_netherstar": ("네더라이트", "네더의 별"),
    "obsidian_to_enchantment": ("흑요석", "마법 부여"),
    "obsidian_to_ender": ("흑요석", "엔더"),
    "obsidian_to_magmatic": ("흑요석", "마그마"),
}

ENERGY_METER = {
    "block.energymeter.meter": "에너지 측정기",
    "block.energymeter.monitor": "외부 모니터",
    "block_side.energymeter.back": "뒤쪽",
    "block_side.energymeter.bottom": "아래쪽",
    "block_side.energymeter.front": "앞쪽",
    "block_side.energymeter.left": "왼쪽",
    "block_side.energymeter.right": "오른쪽",
    "block_side.energymeter.top": "위쪽",
    "button.energymeter.reset_total": "누적값 초기화",
    "connection_status.energymeter.consuming": "소비 중",
    "connection_status.energymeter.disconnected": "연결 끊김",
    "connection_status.energymeter.idle": "대기",
    "connection_status.energymeter.splitting": "분배 중",
    "connection_status.energymeter.transferring": "전송 중",
    "direction.energymeter.down": "아래쪽",
    "direction.energymeter.east": "동쪽",
    "direction.energymeter.north": "북쪽",
    "direction.energymeter.south": "남쪽",
    "direction.energymeter.up": "위쪽",
    "direction.energymeter.west": "서쪽",
    "io_setting.energymeter.in": "입력",
    "io_setting.energymeter.off": "꺼짐",
    "io_setting.energymeter.out": "출력",
    "item.energymeter.guide": "Energy Meter 가이드",
    "item.energymeter.meter": "에너지 측정기",
    "item.energymeter.monitor": "외부 모니터",
    "label.energymeter.graph_interval": "간격",
    "label.energymeter.graph_no_data": "표시할 데이터 없음",
    "label.energymeter.graph_paused": "일시 정지",
    "label.energymeter.header_current": "현재값",
    "label.energymeter.header_io": "I/O",
    "label.energymeter.header_modes": "모드",
    "label.energymeter.header_settings": "설정",
    "label.energymeter.header_status": "상태",
    "label.energymeter.header_total": "누적",
    "label.energymeter.setting_interval": "간격",
    "label.energymeter.setting_limit": "제한",
    "label.energymeter.setting_tolerance": "허용 오차",
    "label.energymeter.sub_header_measuring": "측정",
    "label.energymeter.sub_header_transferring": "전송",
    "measure_mode.energymeter.instant": "순간값",
    "measure_mode.energymeter.smoothed": "평활값",
    "tab.energymeter.main": "에너지 측정기",
    "tab_type.energymeter.configuration": "설정",
    "tab_type.energymeter.graph": "그래프",
    "tab_type.energymeter.redstone": "레드스톤",
    "tooltip.energymeter.button_guide_missing": (
        "가이드를 보려면 GuideME를 설치하세요."
    ),
    "tooltip.energymeter.button_guide_open": "가이드 열기",
    "tooltip.energymeter.button_reset_total": (
        "이 버튼을 누르면 누적 전송 에너지가 영으로 초기화됩니다. "
        "되돌릴 수 없는 작업입니다."
    ),
    "tooltip.energymeter.control_desc_cycle_next_setting": "다음 설정",
    "tooltip.energymeter.control_desc_cycle_previous_setting": "이전 설정",
    "tooltip.energymeter.control_desc_reset_all_settings": "모든 설정 초기화",
    "tooltip.energymeter.control_desc_reset_setting": "설정 초기화",
    "tooltip.energymeter.control_desc_select_setting": "설정 선택",
    "tooltip.energymeter.control_key_lmb": "클릭",
    "tooltip.energymeter.control_key_rmb": "우클릭",
    "tooltip.energymeter.control_key_shift": "Shift",
    "tooltip.energymeter.key_current_setting": "현재 설정",
    "tooltip.energymeter.key_direction": "방향",
    "tooltip.energymeter.key_output_priority": "출력 우선순위",
    "tooltip.energymeter.textbox_max": "최댓값으로 제한됨",
    "transfer_mode.energymeter.consume": "소비",
    "transfer_mode.energymeter.split": "분배",
    "transfer_mode.energymeter.transfer": "전송",
}

QUEST_CORRECTIONS = {
    "quest.1843C79133DFB024.quest_desc": [
        "가장 강력하고 효율적인 네더의 별 발전기입니다. 무엇을 연료로 에너지를 만드는지 "
        "맞혀 보세요!"
    ],
    "quest.1C73E60FC70408D4.quest_desc": [
        "드디어 색다른 발전기입니다! 이름처럼 요리를 활용하죠. 이 발전기는 석탄이나 용암, "
        "통나무가 아니라 음식을 연료로 사용합니다. 허기를 회복하는 음식이라면 무엇이든 "
        "에너지를 만들 수 있고, 발전량은 음식의 허기 회복량에 따라 달라집니다. 스테이크는 "
        "당근보다 더 많은 에너지를 만듭니다."
    ],
    "quest.5792CC9E3AFAB229.quest_desc": [
        "&aGenerator Galore&r라는 모드도 있습니다! 석탄이나 다른 아이템을 연료로 사용하는 "
        "여러 독특한 발전기를 추가합니다."
    ],
    "quest.72A287DCAEEFE49F.quest_desc": [
        "8배 발전기 8개를 전달체와 함께 제작하면 1개의 거대한 발전기로 합쳐집니다! "
        "일반 발전기 64개와 동일하게 작동하지만 공간은 1개만 차지합니다.",
        "",
        "ATM의 별을 제작하려면 64배 마그마틱 발전기가 필요합니다.",
    ],
    "quest.76C63670624C3C56.title": "&c&lGenerator Galore",
}

RELATED_QUEST_IDS = {
    "1843C79133DFB024",
    "1C73E60FC70408D4",
    "4CB488E5CF10F3A4",
    "5792CC9E3AFAB229",
    "72A287DCAEEFE49F",
    "76C63670624C3C56",
    "7CE86300AF8E9BCA",
}

INTENTIONAL_SAME = {
    "quarryplus": {
        "itemGroup.quarryplus",
        "itemGroup.quarryplus.quarryplus",
        "key.yoglib",
        "quarryplus.chat.indent",
        "quarryplus.status.fluid",
        "quarryplus.tooltip.filter_module_more",
        "text.autoconfig.quarryplus.option.power.fastTransferEnergyConversionCoefficient",
        "text.autoconfig.quarryplus.option.power.rebornEnergyConversionCoefficient",
        "text.autoconfig.quarryplus.option.quarry",
        "text.autoconfig.quarryplus.title",
        "yog.pump.liquid",
    },
    "generatorgalore": {
        "generatorgalore.screen.fluid_level",
        "itemGroup.generatorgalore",
    },
    "energymeter": {
        "label.energymeter.header_io",
        "tooltip.energymeter.control_key_shift",
    },
}

ALLOWED_COLLISIONS = {
    "quarryplus": {
        frozenset(
            {
                "block.quarryplus.quarry",
                "itemGroup.quarryplus",
                "itemGroup.quarryplus.quarryplus",
                "key.yoglib",
                "text.autoconfig.quarryplus.option.quarry",
                "text.autoconfig.quarryplus.title",
            }
        ),
    },
    "generatorgalore": set(),
    "energymeter": {
        frozenset(
            {
                "block_side.energymeter.bottom",
                "direction.energymeter.down",
            }
        ),
        frozenset(
            {
                "block_side.energymeter.top",
                "direction.energymeter.up",
            }
        ),
        frozenset(
            {
                "label.energymeter.header_settings",
                "tab_type.energymeter.configuration",
            }
        ),
        frozenset(
            {
                "label.energymeter.sub_header_transferring",
                "transfer_mode.energymeter.transfer",
            }
        ),
    },
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없이 JSON을 기록한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    """파일의 SHA-256을 계산한다."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric_tokens(value: str) -> list[str]:
    """서식 코드의 색상 숫자를 제외한 표시 숫자를 찾는다."""
    return NUMBER.findall(FORMAT_CODE.sub("", value))


def source_jar(instance: Path, pattern: str) -> Path:
    """현재 설치본에서 패턴에 맞는 JAR 하나를 찾는다."""
    jars = sorted((instance / "mods").glob(pattern))
    if len(jars) != 1:
        raise RuntimeError(
            f"대상 JAR 수가 1개가 아닙니다: {[path.name for path in jars]}"
        )
    return jars[0]


def read_jar_language(
    jar: Path, namespace: str, locale: str = "en_us"
) -> dict[str, object]:
    """현재 JAR의 언어 파일을 읽는다."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read(f"assets/{namespace}/lang/{locale}.json"))
    if not isinstance(value, dict):
        raise TypeError(f"JAR 언어 파일이 객체가 아닙니다: {jar}:{locale}")
    return value


def generator_translations() -> dict[str, str]:
    """발전기 등급과 업그레이드 이름을 일관된 규칙으로 만든다."""
    translations = dict(GENERATOR_STATIC)
    for identifier, name in GENERATOR_NAMES.items():
        base_key = f"block.generatorgalore.{identifier}_generator"
        translations[base_key] = f"{name} 발전기"
        translations[f"{base_key}_8x"] = f"8배 {name} 발전기"
        translations[f"{base_key}_64x"] = f"64배 {name} 발전기"
    for identifier, (source, target) in UPGRADES.items():
        translations[f"item.generatorgalore.{identifier}_upgrade"] = (
            f"{source} → {target} 업그레이드"
        )
    return translations


def prepare() -> dict[str, object]:
    """현재 세 JAR 영어와 QuarryPlus 한국어 후보를 작업본에 기록한다."""
    instance = resolve_source_root()
    rows = []
    for namespace, pattern in NAMESPACES.items():
        jar = source_jar(instance, pattern)
        english = read_jar_language(jar, namespace)
        with ZipFile(jar) as archive:
            bundled_korean = f"assets/{namespace}/lang/ko_kr.json" in archive.namelist()
        write_json(WORK_ROOT / namespace / "en_us.json", english)
        if bundled_korean:
            candidate = read_jar_language(jar, namespace, "ko_kr")
            write_json(WORK_ROOT / namespace / "bundled_ko_kr.json", candidate)
        write_json(
            WORK_ROOT / namespace / "candidate_sources.json",
            {
                key: "bundled_ko_kr_reviewed"
                if bundled_korean and key not in QUARRY_OVERRIDES
                else "manual_current_en_us"
                for key in english
            },
        )
        rows.append(
            {
                "namespace": namespace,
                "jar": jar.name,
                "jar_size": jar.stat().st_size,
                "jar_mtime_ns": jar.stat().st_mtime_ns,
                "english_keys": len(english),
                "bundled_korean": bundled_korean,
            }
        )
    report = {
        "family": FAMILY,
        "namespaces": rows,
        "english_keys": sum(int(row["english_keys"]) for row in rows),
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", report)
    return report


def build() -> dict[str, object]:
    """세 언어 파일과 Energy Meter 가이드 머리말을 만든다."""
    instance = resolve_source_root()
    translations_by_namespace = {
        "generatorgalore": generator_translations(),
        "energymeter": ENERGY_METER,
    }
    counts = {}
    reused = 0
    for namespace in NAMESPACES:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        if namespace == "quarryplus":
            candidate = load_json(WORK_ROOT / namespace / "bundled_ko_kr.json")
            if list(candidate) != list(english):
                raise KeyError("QuarryPlus 한국어 후보 키가 현재 영어와 다릅니다")
            translations = {
                key: QUARRY_OVERRIDES.get(key, candidate[key]) for key in english
            }
            reused += sum(translations[key] == candidate[key] for key in english)
        else:
            translations = translations_by_namespace[namespace]
        missing = sorted(set(english) - set(translations))
        extra = sorted(set(translations) - set(english))
        if missing or extra:
            raise KeyError(f"{namespace} 번역표 불일치: 누락={missing}, 초과={extra}")
        korean = {key: translations[key] for key in english}
        write_json(WORK_ROOT / namespace / "ko_kr.json", korean)
        write_json(RESOURCEPACK_ROOT / namespace / "lang/ko_kr.json", korean)
        counts[namespace] = len(korean)

    energy_jar = source_jar(instance, NAMESPACES["energymeter"])
    with ZipFile(energy_jar) as archive:
        guide_source = json.loads(archive.read(GUIDE_INTERNAL))
    guide_output = deepcopy(guide_source)
    tooltip = guide_output["item_settings"]["tooltip_lines"][0]
    if tooltip.get("text") != "An introduction to the mod":
        raise RuntimeError("Energy Meter 가이드 직접 문구가 현재 원문과 다릅니다")
    tooltip["text"] = "이 모드를 소개하는 안내서"
    write_json(WORK_ROOT / "energymeter_guide_en_us.json", guide_source)
    write_json(GUIDE_OUTPUT, guide_output)
    report = {
        "reviewed_language_keys": sum(counts.values()),
        "namespace_keys": counts,
        "quarryplus_existing_korean_reused": reused,
        "quarryplus_corrected": counts["quarryplus"] - reused,
        "new_language_translations": counts["generatorgalore"] + counts["energymeter"],
        "guide_direct_strings": 1,
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def collect_family_references(instance: Path) -> dict[str, object]:
    """퀘스트와 KubeJS에서 세 모드의 참조 위치와 표시 후보를 수집한다."""
    patterns = ("quarryplus:", "generatorgalore:", "energymeter:")
    quest_references = []
    kubejs_references = []
    custom_names = []
    read_errors = []
    for relative, output in (
        ("config/ftbquests", quest_references),
        ("kubejs", kubejs_references),
    ):
        root = instance / relative
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            if path.suffix.lower() not in {".json", ".snbt", ".js", ".txt"}:
                continue
            try:
                lines = path.read_text(encoding="utf-8-sig").splitlines()
            except UnicodeDecodeError as exc:
                read_errors.append(f"{path.relative_to(instance).as_posix()}: {exc}")
                continue
            for number, line in enumerate(lines, 1):
                if not any(pattern in line.lower() for pattern in patterns):
                    continue
                row = f"{path.relative_to(instance).as_posix()}:{number}:{line.strip()}"
                output.append(row)
                if "minecraft:custom_name" in line:
                    custom_names.append(row)
    return {
        "quest_references": quest_references,
        "kubejs_references": kubejs_references,
        "custom_name_candidates": custom_names,
        "read_errors": read_errors,
    }


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR 데이터, GuideME, 퀘스트 fallback과 KubeJS 참조를 감사한다."""
    instance = resolve_source_root()
    errors = []
    jar_rows = []
    for namespace, pattern in NAMESPACES.items():
        jar = source_jar(instance, pattern)
        advancement_files = []
        direct_advancement_text = []
        with ZipFile(jar) as archive:
            for name in sorted(
                item
                for item in archive.namelist()
                if "/advancement" in item and item.endswith(".json")
            ):
                value = json.loads(archive.read(name))
                advancement_files.append(name)
                serialized = json.dumps(value, ensure_ascii=False)
                direct_advancement_text.extend(
                    match.group(0)
                    for match in re.finditer(
                        r'"text"\s*:\s*"[^"]*[A-Za-z][^"]*"', serialized
                    )
                )
        if direct_advancement_text:
            errors.append(
                f"{namespace} 발전 과제에 직접 영문이 있습니다: {direct_advancement_text}"
            )
        jar_rows.append(
            {
                "namespace": namespace,
                "jar": jar.name,
                "advancement_recipe_files": advancement_files,
                "direct_advancement_text": direct_advancement_text,
            }
        )

    references = collect_family_references(instance)
    errors.extend(references["read_errors"])
    if references["custom_name_candidates"]:
        errors.append(
            "관련 퀘스트에 별도 custom_name 표시 후보가 있습니다: "
            + " | ".join(references["custom_name_candidates"])
        )
    quest_text = "\n".join(references["quest_references"])
    generator_ids = sorted(
        identifier
        for identifier in set(re.findall(r"generatorgalore:([a-z0-9_]+)", quest_text))
        if "generator" in identifier
    )
    generator_language = generator_translations()
    missing_generator_items = sorted(
        identifier
        for identifier in generator_ids
        if f"block.generatorgalore.{identifier}" not in generator_language
    )
    if missing_generator_items:
        errors.append(
            f"퀘스트 발전기 이름 번역이 누락됐습니다: {missing_generator_items}"
        )

    english_quests = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean_quests = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    related_quest_keys = sorted(
        key
        for key in english_quests
        if any(key.startswith(f"quest.{quest_id}.") for quest_id in RELATED_QUEST_IDS)
    )
    for key, expected in QUEST_CORRECTIONS.items():
        if korean_quests.get(key) != expected:
            errors.append(f"Generator Galore 관련 퀘스트 교정값이 다릅니다: {key}")
    for key in related_quest_keys:
        if key not in korean_quests:
            errors.append(f"Generator Galore 관련 퀘스트 한국어가 없습니다: {key}")
            continue
        source_value = english_quests[key]
        target_value = korean_quests[key]
        source_text = json.dumps(source_value, ensure_ascii=False)
        target_text = json.dumps(target_value, ensure_ascii=False)
        for label, pattern in (("자리표시자", PLACEHOLDER), ("서식 코드", FORMAT_CODE)):
            if Counter(pattern.findall(source_text)) != Counter(
                pattern.findall(target_text)
            ):
                errors.append(f"퀘스트 {label} 보존이 다릅니다: {key}")
        if Counter(numeric_tokens(source_text)) != Counter(numeric_tokens(target_text)):
            errors.append(f"퀘스트 숫자 보존이 다릅니다: {key}")

    report = {
        "family": FAMILY,
        "jars": jar_rows,
        "energymeter_guide_direct_strings": 1,
        "references": references,
        "generator_item_ids_in_quests": generator_ids,
        "generator_item_ids_missing_translation": missing_generator_items,
        "related_quest_keys": related_quest_keys,
        "related_quest_keys_corrected": len(QUEST_CORRECTIONS),
        "related_quest_keys_reviewed_reused": len(related_quest_keys)
        - len(QUEST_CORRECTIONS),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def verify_guide(instance: Path) -> tuple[dict[str, object], list[str]]:
    """Energy Meter 가이드가 직접 문구 하나 외에는 원본과 같은지 검증한다."""
    jar = source_jar(instance, NAMESPACES["energymeter"])
    with ZipFile(jar) as archive:
        source = json.loads(archive.read(GUIDE_INTERNAL))
    expected = deepcopy(source)
    expected["item_settings"]["tooltip_lines"][0]["text"] = "이 모드를 소개하는 안내서"
    output = load_json(GUIDE_OUTPUT)
    errors = []
    if output != expected:
        errors.append("Energy Meter 가이드 산출물에 지정하지 않은 차이가 있습니다")
    return {
        "source": GUIDE_INTERNAL,
        "translated_direct_strings": 1,
        "matches_expected": output == expected,
    }, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """현재 JAR·작업본·산출물과 문자열 보존 규칙을 검증한다."""
    instance = resolve_source_root()
    audit_report = load_json(WORK_ROOT / "surface_audit.json")
    errors = []
    namespace_reports = []
    total_keys = 0
    total_reused = 0
    for namespace, pattern in NAMESPACES.items():
        jar = source_jar(instance, pattern)
        jar_english = read_jar_language(jar, namespace)
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        output = load_json(RESOURCEPACK_ROOT / namespace / "lang/ko_kr.json")
        current_errors = []
        untranslated = []
        latin_residue = {}
        if jar_english != english:
            current_errors.append("작업 영어가 현재 설치 JAR 영어와 다릅니다")
        if list(english) != list(korean):
            current_errors.append("한국어 키 또는 키 순서가 영어 원문과 다릅니다")
        if korean != output:
            current_errors.append("작업 한국어와 리소스팩 산출물이 다릅니다")
        for key in english.keys() & korean.keys():
            source = english[key]
            target = korean[key]
            if type(source) is not type(target):
                current_errors.append(f"자료형 불일치: {key}")
                continue
            if not isinstance(source, str) or not isinstance(target, str):
                continue
            for label, source_tokens, target_tokens in (
                (
                    "자리표시자",
                    PLACEHOLDER.findall(source),
                    PLACEHOLDER.findall(target),
                ),
                ("서식 코드", FORMAT_CODE.findall(source), FORMAT_CODE.findall(target)),
                ("숫자", numeric_tokens(source), numeric_tokens(target)),
            ):
                if Counter(source_tokens) != Counter(target_tokens):
                    current_errors.append(f"{label} 불일치: {key}")
            if source.count("\n") != target.count("\n"):
                current_errors.append(f"줄바꿈 불일치: {key}")
            if source == target and key not in INTENTIONAL_SAME[namespace]:
                untranslated.append(key)
            residue = sorted(set(LATIN_WORD.findall(target)) - ALLOWED_LATIN)
            if residue:
                latin_residue[key] = residue
        collisions = defaultdict(list)
        for key, target in korean.items():
            if isinstance(target, str):
                collisions[target].append(key)
        unexpected_collisions = {
            target: keys
            for target, keys in collisions.items()
            if len(keys) > 1
            and len({english[key] for key in keys}) > 1
            and frozenset(keys) not in ALLOWED_COLLISIONS[namespace]
        }
        if untranslated:
            current_errors.append(f"영어와 같은 미번역 후보: {untranslated}")
        if latin_residue:
            current_errors.append(f"허용하지 않은 영문 잔여: {latin_residue}")
        if unexpected_collisions:
            current_errors.append(
                f"서로 다른 영어의 한국어 충돌: {unexpected_collisions}"
            )
        reused = 0
        if namespace == "quarryplus":
            candidate = load_json(WORK_ROOT / namespace / "bundled_ko_kr.json")
            reused = sum(korean[key] == candidate[key] for key in korean)
            total_reused += reused
        namespace_reports.append(
            {
                "namespace": namespace,
                "keys": len(english),
                "existing_korean_reused": reused,
                "new_or_corrected": len(english) - reused,
                "untranslated_candidates": untranslated,
                "latin_residue": latin_residue,
                "unexpected_name_collisions": unexpected_collisions,
                "errors": current_errors,
            }
        )
        total_keys += len(english)
        errors.extend(f"{namespace}: {message}" for message in current_errors)
    guide_report, guide_errors = verify_guide(instance)
    errors.extend(guide_errors)
    if audit_report.get("status") != "complete":
        errors.append("표시 표면 감사가 완료되지 않았습니다")
    report = {
        "family": FAMILY,
        "namespaces": namespace_reports,
        "guide": guide_report,
        "keys": total_keys,
        "existing_korean_reused": total_reused,
        "new_or_corrected_language_keys": total_keys - total_reused,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "language_validation.json", report)
    related_quest_keys = audit_report.get("related_quest_keys", [])
    completion = {
        "family": FAMILY,
        "language_keys": total_keys,
        "namespace_keys": {row["namespace"]: row["keys"] for row in namespace_reports},
        "existing_korean_reused": total_reused
        + int(audit_report.get("related_quest_keys_reviewed_reused", 0)),
        "new_or_corrected_translations": total_keys
        - total_reused
        + 1
        + len(QUEST_CORRECTIONS),
        "guide_direct_strings": 1,
        "ftbquests": {
            "reviewed_keys": len(related_quest_keys),
            "corrected_keys": len(QUEST_CORRECTIONS),
            "reviewed_reused_keys": audit_report.get(
                "related_quest_keys_reviewed_reused", 0
            ),
        },
        "kubejs_references": len(
            audit_report.get("references", {}).get("kubejs_references", [])
        ),
        "output_files": [
            f"resourcepacks/ATM10_Korean/assets/{namespace}/lang/ko_kr.json"
            for namespace in NAMESPACES
        ]
        + [
            "resourcepacks/ATM10_Korean/assets/energymeter/guideme_guides/guide.json",
            "config/ftbquests/quests/lang/ko_kr.snbt",
        ],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    completion_path = WORK_ROOT / "family_completion.json"
    if completion_path.is_file():
        previous = load_json(completion_path)
        if "deployment" in previous:
            completion["deployment"] = previous["deployment"]
    write_json(completion_path, completion)
    return report, errors


def output_source(relative: str) -> Path:
    """적용 상대 경로를 저장소 산출물 경로로 바꾼다."""
    prefix = "resourcepacks/"
    if relative.startswith(prefix):
        return PROJECT_ROOT / "output/resourcepack" / relative.removeprefix(prefix)
    return PROJECT_ROOT / "output/overrides" / relative


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 스크립트의 백업·해시 결과를 완료 기록에 반영한다."""
    resolved = manifest_path.resolve()
    try:
        relative_manifest = resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError as exc:
        raise ValueError(f"프로젝트 밖의 적용 기록입니다: {resolved}") from exc
    manifest = load_json(resolved)
    completion_path = WORK_ROOT / "family_completion.json"
    completion = load_json(completion_path)
    expected = set(completion["output_files"])
    errors = []
    matched = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 기록 상태가 applied_and_verified가 아닙니다")
    targets = manifest.get("targets")
    if not isinstance(targets, list):
        targets = []
        errors.append("적용 기록의 targets가 목록이 아닙니다")
    for target in targets:
        if not isinstance(target, dict) or not isinstance(target.get("files"), list):
            continue
        files = {
            str(row.get("relative_path")): row
            for row in target["files"]
            if isinstance(row, dict) and row.get("relative_path") in expected
        }
        if set(files) != expected:
            continue
        for relative, row in files.items():
            source = output_source(relative)
            target_file = Path(str(row.get("target")))
            if not target_file.is_file() or sha256(target_file) != sha256(source):
                errors.append(f"적용 대상과 산출물의 해시가 다릅니다: {relative}")
            if row.get("source_sha256") != row.get("after_sha256"):
                errors.append(f"적용 기록의 전후 해시가 다릅니다: {relative}")
        matched.append(target)
    if len(matched) != 1:
        errors.append(f"일치하는 적용 대상 기록 수가 1개가 아닙니다: {len(matched)}")
    target = matched[0] if matched else {}
    deployment = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "target": target.get("target_root"),
        "changed_paths": target.get("changed_paths", []),
        "backup_manifest": relative_manifest,
        "errors": errors,
    }
    completion["deployment"] = deployment
    if errors:
        completion["status"] = "incomplete"
    write_json(completion_path, completion)
    return deployment, errors


def run_all() -> tuple[dict[str, object], list[str]]:
    """준비, 생성, 감사와 검증을 순서대로 실행한다."""
    prepare_report = prepare()
    build_report = build()
    audit_report, audit_errors = audit()
    verify_report, verify_errors = verify()
    report = {
        "prepare": prepare_report,
        "build": build_report,
        "audit": audit_report,
        "verify": verify_report,
        "status": "complete"
        if not audit_errors and not verify_errors
        else "incomplete",
    }
    return report, audit_errors + verify_errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "build", "audit", "verify", "record-deployment", "all"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        report, errors = prepare(), []
    elif args.command == "build":
        report, errors = build(), []
    elif args.command == "audit":
        report, errors = audit()
    elif args.command == "verify":
        report, errors = verify()
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요합니다")
        report, errors = record_deployment(args.manifest)
    else:
        report, errors = run_all()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
