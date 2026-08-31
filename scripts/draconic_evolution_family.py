#!/usr/bin/env python3
"""Draconic Evolution 언어와 관련 표시 문구를 번역하고 검증한다."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
from pathlib import Path
from zipfile import ZipFile

import five_family_goal as family_goal
from draconic_evolution_quests import QUEST_DESCRIPTIONS
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root


FAMILY = "draconic_evolution"
WORK_ROOT = PROJECT_ROOT / "working/draconic_evolution"
PLACEHOLDER = re.compile(
    r"%(?:\d+\$)?(?:\.\d+)?[A-Za-z%]|\{[A-Za-z0-9_]+\}|"
    r"§[0-9A-FK-ORa-fk-or]|&[0-9A-FK-ORa-fk-or]"
)
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")

SOURCE_OVERRIDES = {
    "Draconic Evolution": "Draconic Evolution",
    "Draconium": "드라코늄",
    "Wyvern": "와이번",
    "Draconic": "드라코닉",
    "Chaotic": "카오틱",
    "Chaos": "카오스",
    "AOE": "효과 범위",
    "AOE:": "효과 범위:",
    "Damage": "피해",
    "False": "아니요",
    "True": "예",
    "No": "아니요",
    "Yes": "예",
    "Active": "활성",
    "Inactive": "비활성",
    "Enabled": "활성화",
    "Disabled": "비활성화",
    "Charge": "충전",
    "Shutdown": "정지",
    "Stopping": "정지 중",
    "Apply": "적용",
    "Craft": "제작",
    "Identify": "식별",
    "Input": "입력",
    "Output": "출력",
    "Unlink": "연결 해제",
    "Configure": "설정",
    "Reset": "초기화",
    "Frequency": "주파수",
    "Owner": "소유자",
    "Creative": "크리에이티브",
    "Normal": "일반",
    "Scale": "크기",
    "On": "켜기",
    "Off": "끄기",
    " Kilo ": " 킬로 ",
    " Mega ": " 메가 ",
    " Giga ": " 기가 ",
    " Tera ": " 테라 ",
    " Peta ": " 페타 ",
    " Exa ": " 엑사 ",
    " Zetta ": " 제타 ",
    " Yotta ": " 요타 ",
    " Octillion ": " 옥틸리언 ",
    " Nonillion ": " 노닐리언 ",
    " Decillion ": " 데실리언 ",
    " Undecillion ": " 운데실리언 ",
    " Duodecillion ": " 듀오데실리언 ",
    " Tredecillion ": " 트레데실리언 ",
    " Quattuordecillion ": " 콰투오르데실리언 ",
    " Quindecillion ": " 퀸데실리언 ",
    " Sexdecillion ": " 섹스데실리언 ",
    " Septendecillion ": " 셉텐데실리언 ",
    " Octodecillion ": " 옥토데실리언 ",
    " Novemdecillion ": " 노벰데실리언 ",
    " Vigintillion ": " 비긴틸리언 ",
}

TERM_REPLACEMENTS = (
    ("용의 진화", "Draconic Evolution"),
    ("드라코닉 진화", "Draconic Evolution"),
    ("용의 ", "드라코닉 "),
    ("Draconic ", "드라코닉 "),
    ("드라코닉 Evolution", "Draconic Evolution"),
    ("혼돈의 ", "카오틱 "),
    ("혼돈 ", "카오틱 "),
    ("혼란스러운 ", "카오틱 "),
    ("Chaotic ", "카오틱 "),
    ("Shield", "보호막"),
    ("Undying", "불사"),
    ("AOE", "효과 범위"),
    ("Dislocator", "전위기"),
    ("Sneak", "웅크린 채"),
    ("Blink", "점멸"),
    ("쉴드", "보호막"),
    ("실드", "보호막"),
    ("방패", "보호막"),
    ("데미지", "피해"),
    ("손상", "피해"),
    ("엔터티", "엔티티"),
    ("항목", "아이템"),
    ("재고", "인벤토리"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("마우스 왼쪽 버튼을 클릭", "좌클릭"),
    ("오른쪽 버튼을 클릭", "우클릭"),
    ("왼쪽 버튼을 클릭", "좌클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("왼쪽 클릭", "좌클릭"),
    ("타일 개체", "블록 엔티티"),
    ("TileEntity", "블록 엔티티"),
    ("창의적인 비행", "크리에이티브 비행"),
    ("나이트 비전", "야간 투시"),
    ("Elytra", "겉날개"),
    ("인젝터", "주입기"),
    ("크래프팅", "제작"),
    ("링크드", "연결된"),
    ("쿨타임", "재사용 대기시간"),
    ("건강 포인트", "체력"),
    ("건강 증진", "체력 증가"),
    ("정확도 모듈", "명중률 모듈"),
    ("발사체 정확도", "발사체 명중률"),
    ("투사체", "발사체"),
    ("광산 안정", "채굴 안정"),
    ("자동 급지", "자동 섭취"),
    ("공급 모듈", "섭취 모듈"),
    ("호기심", "Curios 장비"),
    ("레드 스톤", "레드스톤"),
    ("GUI", "화면"),
    ("OP/샷", "OP/발"),
    ("구성 가능한", "설정 가능한"),
    ("구성 모드", "설정 모드"),
    ("구성 사전 설정", "설정 프리셋"),
    ("장비 구성", "장비 설정"),
    ("모듈 구성", "모듈 설정"),
    ("도구 구성", "도구 설정"),
)

KEY_OVERRIDES = {
    "block.draconicevolution.awakened_crafting_injector": "드라코닉 융합 제작 주입기",
    "block.draconicevolution.awakened_draconium_block": "각성 드라코늄 블록",
    "block.draconicevolution.basic_crafting_injector": "드라코늄 융합 제작 주입기",
    "block.draconicevolution.basic_io_crystal": "기본 에너지 입출력 수정",
    "block.draconicevolution.basic_relay_crystal": "기본 에너지 중계 수정",
    "block.draconicevolution.basic_wireless_crystal": "기본 무선 에너지 수정",
    "block.draconicevolution.chaotic_crafting_injector": "카오틱 융합 제작 주입기",
    "block.draconicevolution.chaos_crystal": "카오스 수정",
    "block.draconicevolution.creative_op_capacitor": "크리에이티브 동력원",
    "block.draconicevolution.deepslate_draconium_ore": "심층암 드라코늄 광석",
    "block.draconicevolution.disenchanter": "마법 추출기",
    "block.draconicevolution.dislocation_inhibitor": "전위 정상화장 투사기",
    "block.draconicevolution.dislocator_pedestal": "전위기 받침대",
    "block.draconicevolution.dislocator_receptacle": "전위기 수용기",
    "block.draconicevolution.draconic_io_crystal": "드라코닉 에너지 입출력 수정",
    "block.draconicevolution.draconic_relay_crystal": "드라코닉 에너지 중계 수정",
    "block.draconicevolution.draconic_wireless_crystal": "드라코닉 무선 에너지 수정",
    "block.draconicevolution.end_draconium_ore": "엔드 드라코늄 광석",
    "block.draconicevolution.energy_pylon": "에너지 파일런",
    "block.draconicevolution.energy_transfuser": "에너지 전송기",
    "block.draconicevolution.entity_detector": "엔티티 감지기",
    "block.draconicevolution.entity_detector_advanced": "고급 엔티티 감지기",
    "block.draconicevolution.grinder": "몹 분쇄기",
    "block.draconicevolution.portal": "포털",
    "block.draconicevolution.rain_sensor": "비 감지기",
    "block.draconicevolution.reactor_core": "드라코닉 반응로 코어",
    "block.draconicevolution.stabilized_spawner": "안정화된 스포너",
    "block.draconicevolution.wyvern_crafting_injector": "와이번 융합 제작 주입기",
    "block.draconicevolution.wyvern_io_crystal": "와이번 에너지 입출력 수정",
    "block.draconicevolution.wyvern_relay_crystal": "와이번 에너지 중계 수정",
    "block.draconicevolution.wyvern_wireless_crystal": "와이번 무선 에너지 수정",
    "death.attack.draconicevolution.guardian_laser": (
        "%1$s님이 %2$s님의 엄청난 레이저 광선에 증발했습니다."
    ),
    "enchantment.draconicevolution.reaper": "영혼 수확",
    "entity.draconicevolution.draconic_arrow": "드라코닉 화살",
    "entity.draconicevolution.guardian_crystal": "수호자 수정",
    "entity.draconicevolution.guardian_projectile": "수호자 발사체",
    "entity.draconicevolution.guardian_wither": "수호자 위더",
    "entity.draconicevolution.persistent_item": "소멸하지 않는 아이템",
    "item.draconicevolution.advanced_dislocator": "고급 전위기",
    "item.draconicevolution.advanced_magnet": "각성 아이템 전위기",
    "item.draconicevolution.awakened_core": "드라코닉 코어",
    "item.draconicevolution.awakened_draconium_dust": "각성 드라코늄 가루",
    "item.draconicevolution.awakened_draconium_ingot": "각성 드라코늄 주괴",
    "item.draconicevolution.awakened_draconium_nugget": "각성 드라코늄 조각",
    "item.draconicevolution.chaos_shard": "카오스 조각",
    "item.draconicevolution.chaotic_chestpiece": "카오틱 흉갑",
    "item.draconicevolution.draconic_chestpiece": "드라코닉 흉갑",
    "item.draconicevolution.creative_capacitor": "크리에이티브 축전기",
    "item.draconicevolution.dislocator": "전위기",
    "item.draconicevolution.draconium_nugget": "드라코늄 조각",
    "item.draconicevolution.dragon_heart": "드래곤 심장",
    "item.draconicevolution.info_tablet": "정보판",
    "item.draconicevolution.crystal_binder": "수정 연결기",
    "item.draconicevolution.item_chaotic_energy_link": "카오스 얽힘 양자 에너지 통로",
    "item.draconicevolution.item_chaotic_aoe": "카오틱 효과 범위 모듈",
    "item.draconicevolution.item_chaotic_shield_capacity": ("카오틱 보호막 용량 모듈"),
    "item.draconicevolution.item_chaotic_shield_recovery": ("카오틱 보호막 회복 모듈"),
    "item.draconicevolution.item_draconic_energy_link": "양자 에너지 통로",
    "item.draconicevolution.item_draconic_aoe": "드라코닉 효과 범위 모듈",
    "item.draconicevolution.item_draconic_shield_capacity": (
        "드라코닉 보호막 용량 모듈"
    ),
    "item.draconicevolution.item_draconium_aoe": "효과 범위 모듈",
    "item.draconicevolution.item_draconic_tree_harvest": "드라코닉 산림 정리 모듈",
    "item.draconicevolution.item_chaotic_tree_harvest": "카오틱 산림 벌목 모듈",
    "item.draconicevolution.item_wyvern_energy_link": "무선 에너지 연결기",
    "item.draconicevolution.item_wyvern_aoe": "와이번 효과 범위 모듈",
    "item.draconicevolution.item_wyvern_aqua_adapt": "수중 채굴 모듈",
    "item.draconicevolution.item_wyvern_hill_step": "자동 오르기 모듈",
    "item.draconicevolution.item_wyvern_tree_harvest": "와이번 나무 수확기",
    "item.draconicevolution.large_chaos_frag": "대형 카오스 파편",
    "item.draconicevolution.magnet": "아이템 전위기",
    "item.draconicevolution.medium_chaos_frag": "소형 카오스 파편",
    "item.draconicevolution.p2p_dislocator": "연결된 전위기(지점 간)",
    "item.draconicevolution.p2p_dislocator_unbound": "연결되지 않은 전위기(지점 간)",
    "item.draconicevolution.player_dislocator": "연결된 전위기(플레이어)",
    "item.draconicevolution.player_dislocator_unbound": "연결되지 않은 전위기(플레이어)",
    "item.draconicevolution.small_chaos_frag": "초소형 카오스 파편",
    "item.draconicevolution.wyvern_chestpiece": "와이번 흉갑",
    "itemGroup.draconicevolution.blocks": "Draconic Evolution 블록",
    "itemGroup.draconicevolution.items": "Draconic Evolution 아이템",
    "itemGroup.draconicevolution.modules": "Draconic Evolution 모듈",
    "fusion_status.draconicevolution.canceled": "제작 취소",
    "generic.configureRedstone": "레드스톤 설정",
    "dislocate.draconicevolution.already_bound": (
        "오류: 이 부적은 한 위치에만 연결할 수 있습니다."
    ),
    "dislocate.draconicevolution.un_set_info2": "웅크린 채 우클릭하여 현재",
    "dislocate.draconicevolution.un_set_info3": "X, Y, Z 좌표와",
    "dislocate.draconicevolution.un_set_info4": "바라보는 방향,",
    "dislocate.draconicevolution.un_set_info5": "현재 차원을 연결하세요.",
    "gui.draconicevolution.energy_net.hud_links": "연결 수",
    "gui.draconicevolution.dislocator.mode_blink": "사용 모드:\n점멸",
    "gui.draconicevolution.dislocator.mode_tp": "사용 모드:\n순간이동",
    "gui.draconicevolution.dislocator.right_click_mode.info": (
        "우클릭 동작을 '선택 위치로 순간이동'과 '점멸' 사이에서 전환합니다.\n"
        "단축키도 설정할 수 있습니다."
    ),
    "gui.draconicevolution.draconium_chest.color_picker": "상자 색상 변경",
    "gui.draconicevolution.draconium_chest.feed.all.info": (
        "자동 제련: 모두\n제련할 수 있는 모든 아이템을 화로에 넣습니다."
    ),
    "gui.draconicevolution.energy_core.build_guide": "건설 안내 표시 전환",
    "gui.draconicevolution.energy_core.config_colour": "색상 설정",
    "gui.draconicevolution.energy_core.energy_target_info": (
        "표시할 '에너지 목표'를 정합니다.\n이 값은 표시에만 사용됩니다.\n일반 "
        "숫자나\n다음과 같은 과학적 표기법을 사용할 수 있습니다.\n'9.223E18'은\n"
        "9223000000000000000을 뜻합니다."
    ),
    "gui.draconicevolution.energy_net.pos_saved_to_tool": (
        "블록 위치를 도구에 저장했습니다. (웅크린 채 허공을 우클릭하면 삭제)"
    ),
    "gui.draconicevolution.energy_net.tool_not_bound": (
        "도구가 연결되지 않았습니다! 웅크린 채 우클릭하여 연결하세요."
    ),
    "gui.draconicevolution.entity_detector.pulse_mode.off": "연속",
    "gui.draconicevolution.entity_detector.pulse_mode.on": "펄스",
    "gui.draconicevolution.entity_detector.pulse_mode": "모드",
    "gui.draconicevolution.entity_detector.pulse_rate": "주기",
    "gui.draconicevolution.entity_detector.pulse_mode.info": (
        "출력 강도는 감지한 유효 엔티티 수와 최소·최대 레드스톤 강도 설정에 따라 "
        "결정됩니다.\n펄스 모드는 스캔할 때마다 1틱 신호를 내보냅니다.\n연속 "
        "모드는 스캔할 때마다 갱신되는 신호를 계속 내보냅니다."
    ),
    "gui.draconicevolution.entity_detector.rsmax": "최대 강도",
    "gui.draconicevolution.entity_detector.rsmin": "최소 강도",
    "gui.draconicevolution.fusion_craft.tier.chaotic": "등급: 카오틱",
    "gui.draconicevolution.grinder.aoe.info": (
        "분쇄기의 효과 범위를 바꿉니다.\n(이 범위 안의 몹을 처치합니다.)"
    ),
    "gui.draconicevolution.grinder.claim.xp": "경험치 받기",
    "gui.draconicevolution.grinder.claim.xp.info": "저장된 경험치를 모두 받습니다.",
    "gui.draconicevolution.grinder.claim.xp.level.info": "경험치 1레벨 받기",
    "gui.draconicevolution.grinder.claim.xp.levels.info": "경험치 %s레벨 받기",
    "gui.draconicevolution.grinder.collect.items.info": (
        "활성화하면 분쇄기가 처치 범위 안의 아이템을 모아 인접한 인벤토리에 넣습니다."
    ),
    "gui.draconicevolution.grinder.collect.xp.info": (
        "활성화하면 분쇄기가 처치 범위 안에 떨어진 경험치를 내부에 저장합니다.\n"
        "플레이어가 직접 받거나, 액체 경험치를 추가하는 모드가 설치되어 있으면 "
        "파이프로 꺼낼 수 있습니다."
    ),
    "gui.draconicevolution.generator.mode_performance_plus.info": (
        "오버드라이브 모드\n최대한 많은 동력이 필요한가요?\n태울 연료가 충분한가요?\n"
        "그렇다면 이 모드를 사용하세요!"
    ),
    "gui.draconicevolution.item_config.delete_zone.info": (
        "삭제할 속성이나 그룹을 여기에 놓으세요."
    ),
    "gui.draconicevolution.item_config.disable_snapping.info": (
        "속성/그룹 위치 맞춤 전환"
    ),
    "gui.draconicevolution.item_config.disable_visualization.info": (
        "속성을 가리키거나 편집할 때 관련 아이템에 나타나는 강조 표시와 애니메이션을 "
        "전환합니다."
    ),
    "gui.draconicevolution.item_config.global.info": (
        "전체 적용 모드 전환\n전체 적용 모드에서는 같은 유형의 모든 장비에 속성을 "
        "적용합니다.\n표시된 값이 아이템의 실제 값과 다를 수 있습니다."
    ),
    "gui.draconicevolution.item_config.toggle_global_binding.info": (
        "전역 단축키\n이 화면을 닫은 뒤에도 이 단축키를 사용할 수 있습니다.\n"
        "다른 단축키와 충돌하는 키도 사용할 수 있습니다."
    ),
    "gui.draconicevolution.item_config.drop_prop_here": "여기에 속성 놓기",
    "gui.draconicevolution.item_config.open_modules.info": "모듈 설정 화면 열기",
    "gui.draconicevolution.modular_item.open_item_config.info": "아이템 설정 화면 열기",
    "gui.draconicevolution.reactor.charge": "충전",
    "gui.draconicevolution.reactor.chaos_out": "카오스(출력)",
    "gui.draconicevolution.reactor.field_rate": "격리장 입력률",
    "gui.draconicevolution.reactor.fuel_in": "연료(입력)",
    "gui.draconicevolution.reactor.go_boom_now": (
        "비상 보호막 예비분이 활성화됐지만 오래 버티지 못합니다! 과부하는 멈출 수 "
        "없고 안정기는 이미 타 버렸습니다. 당장 도망치세요!"
    ),
    "gui.draconicevolution.reactor.reaction_temp": "코어 온도",
    "gui.draconicevolution.reactor.convert_rate.info": (
        "반응로가 현재 연료를 사용하는 속도입니다. 반응로 포화도가 높아지면 감소합니다."
    ),
    "gui.draconicevolution.reactor.core_volume.info": (
        "반응로 안의 총 물질 부피(드라코늄 + 카오스)를 세제곱미터 단위로 표시합니다. "
        "연료를 넣거나 뺄 때만 바뀝니다."
    ),
    "gui.draconicevolution.reactor.field_rate.info": (
        "현재 격리장 강도를 유지하는 데 필요한 정확한 입력량(OP/t)입니다. 격리장 "
        "강도가 높아질수록 기하급수적으로 증가합니다."
    ),
    "gui.draconicevolution.reactor.gen_rate.info": (
        "반응로가 현재 생산하는 동력(OP/t)입니다."
    ),
    "gui.draconicevolution.reactor.rs_mode_field.info": (
        "보호막 강도가 0~100% 사이에서 변할 때 0~15의 신호를 출력합니다. "
        "신호 1은 보호막이 10% 초과, 신호 15는 90% 이상임을 뜻합니다."
    ),
    "gui.draconicevolution.reactor.rs_mode_sat.info": (
        "포화도가 0~100% 사이에서 변할 때 0~15의 신호를 출력합니다."
    ),
    "gui.draconicevolution.reactor.rs_mode": "레드스톤\n모드",
    "gui.draconicevolution.reactor.rs_mode_field_inv.info": (
        "보호막 모드와 같지만 신호가 반전됩니다."
    ),
    "gui.draconicevolution.reactor.rs_mode_temp_inv.info": (
        "온도 모드와 같지만 신호가 반전됩니다."
    ),
    "gui.draconicevolution.reactor.sas.info": (
        "반자동 정지 기능입니다. 활성화하면 온도가 2500C 아래로 내려가고 포화도가 "
        "99%에 도달했을 때 반응로가 자동으로 정지하기 시작합니다. 오작동하거나 "
        "연료를 다시 넣어야 할 때 반응로를 자동으로 정지하는 데 사용할 수 있습니다."
    ),
    "gui.draconicevolution.reactor.title": "드라코닉 반응로",
    "gui.draconicevolution.transfuser.mode_buffer": (
        "완충\n - 외부 공급원의 동력 수용\n - 방전 슬롯의 동력 수용\n - 외부 "
        "소비자에게 방전\n - 충전 슬롯으로 방전"
    ),
    "gui.draconicevolution.transfuser.mode_charge": (
        "충전\n - 외부 공급원의 동력 수용\n - 완충 슬롯의 동력 수용\n - 완전히 "
        "충전되면 꺼낼 수 있음"
    ),
    "hud_armor.draconicevolution.energy.2": "에너지 표시: 합계",
    "hud.draconicevolution.open_hud_config": "HUD 설정 화면을 엽니다.",
    "hud.draconicevolution.shield_hud.info": (
        "이 HUD는 드라코닉 보호막의 현재 상태와 남은 에너지, 불사 모듈을 표시합니다."
    ),
    "item_prop.draconicevolution.charge_held_item": "손에 든 아이템 충전",
    "item_prop.draconicevolution.aoe_safe.info": (
        "활성화하면 효과 범위 안에서 블록 엔티티를 감지했을 때 아무것도 부수지 "
        "않습니다. 한 번의 잘못된 클릭으로 기지의 절반을 부수는 사고를 막을 수 있습니다."
    ),
    "item_prop.draconicevolution.aoe_safe.blocked": (
        "§9(§a효과 범위 안전 모드가 활성화되었습니다.§9)§c효과 범위 안에 블록 "
        "엔티티가 있어 작업을 취소했습니다."
    ),
    "item_prop.draconicevolution.attack_aoe.info": (
        "무기를 휘두를 때 공격하는 범위를 조정합니다.\n바라보는 방향을 중심으로 "
        "100도 부채꼴 영역을 공격합니다."
    ),
    "item_prop.draconicevolution.charge_hot_bar": "단축바 충전",
    "item_prop.draconicevolution.charge_main": "주 인벤토리 충전",
    "item_prop.draconicevolution.junk_filter_mod.enabled": "소각",
    "item_prop.draconicevolution.feed_mod.consume_food.info": (
        "활성화하면 인벤토리의 음식을 자동으로 먹어 모듈의 내부 저장량을 채웁니다."
    ),
    "item_prop.draconicevolution.mining_speed": "채굴 속도 배수",
    "item_prop.draconicevolution.mining_aoe": "채굴 효과 범위",
    "item_prop.draconicevolution.night_vision.light_level": "야간 투시 밝기 기준",
    "item_prop.draconicevolution.night_vision.enabled.info": (
        "야간 투시를 켜거나 끕니다. 활성화한 동안 다른 야간 투시 효과보다 우선합니다."
    ),
    "item_prop.draconicevolution.night_vision.light_level.info": (
        "야간 투시가 활성화되는 밝기 기준을 정합니다. 활성화된 동안 매 틱 소량의 "
        "OP를 소모합니다."
    ),
    "item_prop.draconicevolution.shield_mod.always_visible": "보호막 항상 표시",
    "item_prop.draconicevolution.shield_mod.always_visible.info": (
        "표시만 바꾸는 설정입니다. 비활성화하면 보호막이 피해를 흡수할 때만 보입니다."
    ),
    "item_prop.draconicevolution.shield_mod.enabled.info": (
        "보호막을 비활성화할 수 있습니다. 동력은 아끼지만 피해에 그대로 노출됩니다."
    ),
    "item_prop.draconicevolution.tree_harvest_mod.leaves": "나뭇잎 수확",
    "module.draconicevolution.ender_storage.about_compat2": (
        "(모듈을 든 채 엔더 상자를 Shift+우클릭)"
    ),
    "module.draconicevolution.ender_storage.how_to_clear": (
        "모듈을 Shift+우클릭하여 연결 해제"
    ),
    "module.draconicevolution.energy_link.dimensional": "차원 간",
    "module.draconicevolution.energy_link.link_to_core": (
        "모듈을 든 채 에너지 코어를 Shift+우클릭하여 연결하세요."
    ),
    "module.draconicevolution.energy.transfer": "에너지 전송",
    "module.draconicevolution.energy_link.operation": "운용 에너지",
    "module.draconicevolution.filtered_module.filter_example": "예: c:stone",
    "module.draconicevolution.proj_accuracy.name": "오차",
    "module.draconicevolution.proj_grav_comp.name": "중력 상쇄",
    "module.draconicevolution.undying.invuln.name": "무적 시간",
    "module_type.draconicevolution.aqua_adept.name": "수중 채굴",
    "module_type.draconicevolution.hill_step.name": "자동 오르기",
    "module_type.draconicevolution.junk_filter.name": "소각 필터",
    "module_type.draconicevolution.night_vision.name": "야간 투시",
    "module_type.draconicevolution.proj_modifier.name": "발사체 강화",
    "module_type.draconicevolution.proj_anti_immune.name": "발사체 면역 무효화",
    "module_type.draconicevolution.undying.name": "불사",
    "tooltip.draconicevolution.bow.damage": "%s 최대 공격 피해",
    "item.draconicevolution.item_draconic_proj_anti_immune": (
        "발사체 면역 무효화 모듈"
    ),
    "tile.draconicevolution.dislocation_inhibitor.info": (
        "5블록 안에 떨어진 아이템을 아이템 전위기가 수집하지 못하게 합니다."
    ),
}

ALLOWED_ORIGINALS = {
    "AOE",
    "SAS",
    "%sOP @%s OP/t",
}

RELATED_QUEST_OVERRIDES: dict[str, object] = {
    "quest.677D0C23D53A77CA.quest_desc": [
        "&bDraconic Evolution&r은 &d에너지 코어&r라는 멀티블록을 추가합니다.",
        "",
        "구조가 복잡해 보일 수 있지만 최종 등급은 &m9,223,372,036,854,775,808 FE&r, "
        "사실상 무한한 에너지를 저장합니다.",
        "",
        "자세한 내용은 Draconic Evolution 챕터에서 확인하세요.",
        "{image:atm:textures/questpics/draconic/draconic_core_8on.png width:100 "
        "height:100 align:1}",
    ],
    "quest.677D0C23D53A77CA.quest_subtitle": "사실상 무한한 저장 공간",
    "quest.677D0C23D53A77CA.title": "&9Draconic Evolution: &d에너지 코어",
}

QUEST_TEXT_OVERRIDES = {
    "quest.0000A88BB40B2149.title": "강적을 상대할 준비",
    "quest.01612963DBBAC9A1.title": "카오틱 흉갑",
    "quest.04BF68E4554D69AA.quest_subtitle": "저장 용량: 거의 무한",
    "quest.0817FD6E45C127E8.title": "파일런 추가(선택 사항)",
    "quest.106D08542AAFA166.title": "수호자 수정 14개 찾아 파괴하기",
    "quest.12469CC0CCFBA1C5.title": "카오틱 힘의 지팡이",
    "quest.131AA933D59D3017.quest_subtitle": "저장 용량: 59,300,000,000 RF",
    "quest.1F7D147C9AF6A4FC.quest_subtitle": "저장 용량: 9,880,000,000 RF",
    "quest.22D383BAEF8A2B39.title": "드라코닉 힘의 지팡이",
    "quest.26DF1427AC3966DE.title": "Draconic Evolution",
    "quest.2D9AF97C03C5AEC7.title": "고급 안정기",
    "quest.2DB2A4A1182FE0BB.quest_subtitle": "저장 용량: 356,000,000,000 RF",
    "quest.35767977FB9E0B1B.quest_subtitle": "저장 용량: 273,000,000 RF",
    "quest.389655CD41C7A691.quest_subtitle": "저장 용량: 45,500,000 RF",
    "quest.39865681B03CABAA.title": "수중 채굴 모듈",
    "quest.3B4CEE8A8CE0D6CB.quest_subtitle": "저장 용량: 2,140,000,000,000 RF",
    "quest.3DF794EBCAA7AE1A.title": "드라코닉 산림 정리 모듈",
    "quest.41BD497108CA109F.title": "각성 드라코늄",
    "quest.421954D7D46FAAD6.title": "에너지 코어 안정기",
    "quest.45EE60207C466D6C.quest_subtitle": "카오스 섬 찾기",
    "quest.45EE60207C466D6C.title": "카오스 가디언은 어디에?",
    "quest.4AB564420C48579B.title": "와이번 흉갑",
    "quest.4E27182763DA83DC.title": "드라코닉 흉갑",
    "quest.5443E15E226DFC86.title": "OP가 드나드는 장치",
    "quest.5ADFC45B03BAB852.title": "드라코닉 등급",
    "quest.5BC6CC3C09F512A7.quest_subtitle": "무한한 동력",
    "quest.5D87088E8D71DB9B.title": "OP 전송",
    "quest.6601ACCDDF6CA5FF.title": "가동 준비",
    "quest.6B8F2E05429C185F.title": "카오스 조각{s}",
    "quest.713D3B3954E58C4A.quest_subtitle": "저장 용량: 1,640,000,000 RF",
    "quest.7496B2380A23FDC6.title": "카오틱 산림 벌목 모듈",
    "quest.7A4ABFCD12202A91.title": "에너지, 즉 OP란?",
    "quest.7D159D333B2AC57E.quest_subtitle": "이제 성공을 기도할 차례...",
    "quest.7F757CD6F8C57733.quest_subtitle": "드라코닉 에너지 저장소",
}


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def reviewed_text(key: str, source: str, candidate: str) -> str:
    if source.startswith(("{image:", "{@")):
        return source
    value = KEY_OVERRIDES.get(key, SOURCE_OVERRIDES.get(source, candidate))
    if not isinstance(value, str):
        raise TypeError(f"문자열 확정값이 아닙니다: {key}")
    for old, new in TERM_REPLACEMENTS:
        value = value.replace(old, new)
    value = value.replace(".,", ".").replace(". ,", ".")
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    leading = source[: len(source) - len(source.lstrip())]
    trailing = source[len(source.rstrip()) :]
    return leading + value.strip() + trailing


def normalize_value(key: str, source: object, candidate: object) -> object:
    if isinstance(source, str) and isinstance(candidate, str):
        return reviewed_text(key, source, candidate)
    if isinstance(source, list) and isinstance(candidate, list):
        if len(source) != len(candidate):
            raise ValueError(f"목록 길이 불일치: {key}")
        return [
            normalize_value(key, source_item, candidate_item)
            for source_item, candidate_item in zip(source, candidate)
        ]
    if isinstance(source, dict) and isinstance(candidate, dict):
        if list(source) != list(candidate):
            raise ValueError(f"객체 키 불일치: {key}")
        return {
            child_key: normalize_value(key, source[child_key], candidate[child_key])
            for child_key in source
        }
    if type(source) is not type(candidate):
        raise TypeError(f"자료형 불일치: {key}")
    return source


def normalize_language() -> dict[str, object]:
    root = WORK_ROOT / "draconicevolution"
    english = load_json(root / "en_us.json")
    candidates = load_json(root / "auto_candidates.json")
    korean = {
        key: normalize_value(key, source, candidates[key])
        for key, source in english.items()
    }
    write_json(root / "ko_kr.json", korean)
    report = {
        "language_keys_reviewed": len(english),
        "bundled_korean_reused_without_review": 0,
        "status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "language_normalization.json", report)
    return report


def translated_name_map() -> dict[str, str]:
    """확정한 아이템·블록 이름을 영어 표시 이름으로 찾을 수 있게 만든다."""
    root = WORK_ROOT / "draconicevolution"
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    candidates: dict[str, set[str]] = {}
    for key, source in english.items():
        target = korean[key]
        if not key.startswith(("item.", "block.", "entity.")):
            continue
        if isinstance(source, str) and isinstance(target, str) and source:
            candidates.setdefault(source, set()).add(target)
    return {
        source: next(iter(values))
        for source, values in candidates.items()
        if len(values) == 1
    }


def quest_description_value(key: str, source: object) -> object:
    """직접 검수한 설명을 태그 구조에 맞춰 적용한다."""
    override = QUEST_DESCRIPTIONS[key]
    if isinstance(override, list):
        if not isinstance(source, list) or len(source) != len(override):
            raise ValueError(f"퀘스트 설명 목록 길이 불일치: {key}")
        return override
    if not isinstance(source, list):
        raise TypeError(f"퀘스트 설명 원문이 목록이 아닙니다: {key}")
    prose_indexes = [
        index
        for index, item in enumerate(source)
        if isinstance(item, str) and item and not item.startswith(("{image:", "{@"))
    ]
    if len(prose_indexes) != 1:
        raise ValueError(f"단일 설명 적용 대상을 찾을 수 없습니다: {key}")
    result = list(source)
    result[prose_indexes[0]] = override
    return result


def normalize_quests() -> dict[str, object]:
    """전용·관련 퀘스트 표시 문구를 모두 확정한다."""
    name_map = translated_name_map()
    dedicated = WORK_ROOT / "quests/draconic_evolution"
    english = load_json(dedicated / "en_us.json")
    candidates = load_json(dedicated / "auto_candidates.json")
    description_keys = {key for key in english if key.endswith(".quest_desc")}
    if description_keys != set(QUEST_DESCRIPTIONS):
        missing = sorted(description_keys - set(QUEST_DESCRIPTIONS))
        extra = sorted(set(QUEST_DESCRIPTIONS) - description_keys)
        raise RuntimeError(
            f"퀘스트 설명 확정 키 불일치: missing={missing}, extra={extra}"
        )
    korean: dict[str, object] = {}
    item_titles = 0
    for key, source in english.items():
        if key in QUEST_TEXT_OVERRIDES:
            korean[key] = QUEST_TEXT_OVERRIDES[key]
        elif key in QUEST_DESCRIPTIONS:
            korean[key] = quest_description_value(key, source)
        elif isinstance(source, str) and source in name_map:
            korean[key] = name_map[source]
            item_titles += 1
        else:
            value = normalize_value(key, source, candidates[key])
            if isinstance(value, str):
                value = value.replace("티어", "등급").replace("효과 영역", "효과 범위")
            korean[key] = value
    write_json(dedicated / "ko_kr.json", korean)

    related = WORK_ROOT / "quests/related"
    related_english = load_json(related / "en_us.json")
    related_current = load_json(related / "ko_kr.json")
    related_korean: dict[str, object] = {}
    for key in related_english:
        value = RELATED_QUEST_OVERRIDES.get(key, related_current[key])
        if key == "quest.47043AF7D1FABC43.quest_desc" and isinstance(value, list):
            value = [
                item.replace(
                    "Draconic Evolution 마법 해제기", "Draconic Evolution 마법 추출기"
                )
                if isinstance(item, str)
                else item
                for item in value
            ]
        related_korean[key] = value
    write_json(related / "ko_kr.json", related_korean)
    report = {
        "dedicated_display_keys_reviewed": len(english),
        "dedicated_descriptions_manually_reviewed": len(QUEST_DESCRIPTIONS),
        "item_titles_matched_to_resourcepack": item_titles,
        "related_display_keys_reviewed": len(related_english),
        "bundled_korean_reused_without_review": 0,
        "status": "all_current_quest_display_keys_reviewed",
    }
    write_json(WORK_ROOT / "quest_normalization.json", report)
    return report


def verify_quests() -> tuple[dict[str, object], list[str]]:
    """퀘스트 키, 구조, 서식과 미번역 표시 문구를 검사한다."""
    errors: list[str] = []
    untranslated: list[str] = []
    display_keys = 0
    for scope in ("draconic_evolution", "related"):
        root = WORK_ROOT / "quests" / scope
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        display_keys += len(english)
        if list(english) != list(korean):
            errors.append(f"{scope}: 퀘스트 키 또는 순서 불일치")
            continue
        for key, source in english.items():
            target = korean[key]
            source_text = family_goal.quest_snbt.flatten(source)
            target_text = family_goal.quest_snbt.flatten(target)
            if Counter(FORMAT_CODE.findall(source_text)) != Counter(
                FORMAT_CODE.findall(target_text)
            ):
                errors.append(f"{scope}:{key}: 서식 코드 불일치")
            if Counter(PLACEHOLDER.findall(source_text)) != Counter(
                PLACEHOLDER.findall(target_text)
            ):
                errors.append(f"{scope}:{key}: 자리표시자 불일치")
            if source_text.count("\\n") != target_text.count("\\n"):
                errors.append(f"{scope}:{key}: 줄바꿈 불일치")
            if isinstance(source, list) and isinstance(target, list):
                source_markup = [
                    item
                    for item in source
                    if isinstance(item, str) and item.startswith(("{image:", "{@"))
                ]
                target_markup = [
                    item
                    for item in target
                    if isinstance(item, str) and item.startswith(("{image:", "{@"))
                ]
                if source_markup != target_markup:
                    errors.append(f"{scope}:{key}: 이미지 또는 페이지 태그 불일치")
            if (
                source_text == target_text
                and LATIN_WORD.search(source_text)
                and source_text != "Draconic Evolution"
            ):
                untranslated.append(f"{scope}:{key}")
    if untranslated:
        errors.append("미번역 퀘스트 표시 키: " + ", ".join(untranslated[:30]))
    forbidden = (
        "용의 진화",
        "용의 ",
        "혼돈의 ",
        "Chaotic Shield",
        "Draconic Shield",
        "데미지",
        "상점:",
        "너비:",
        "높이:",
        "정렬:",
        "합법적인 점프",
        "작전 가능성",
        "가슴갑옷",
    )
    for scope in ("draconic_evolution", "related"):
        korean = load_json(WORK_ROOT / "quests" / scope / "ko_kr.json")
        for key, value in korean.items():
            text = family_goal.quest_snbt.flatten(value)
            if any(term in text for term in forbidden):
                errors.append(f"{scope}:{key}: 기계번역 흔적")
    report = {
        "quest_display_keys_reviewed": display_keys,
        "dedicated_descriptions_manually_reviewed": len(QUEST_DESCRIPTIONS),
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_quest_validation.json", report)
    return report, errors


def verify_language() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    untranslated: list[str] = []
    root = WORK_ROOT / "draconicevolution"
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    if list(english) != list(korean):
        errors.append("언어 키 또는 순서 불일치")
    for key, source in english.items():
        target = korean.get(key)
        errors.extend(
            f"draconicevolution:{key}: {error}"
            for error in family_goal.validate_family_value(FAMILY, key, source, target)
        )
        if (
            isinstance(source, str)
            and isinstance(target, str)
            and source == target
            and LATIN_WORD.search(source)
            and source not in ALLOWED_ORIGINALS
            and not family_goal.is_allowed_original(source)
        ):
            untranslated.append(key)
    if untranslated:
        errors.append("분류되지 않은 영어 유지: " + ", ".join(untranslated[:30]))
    forbidden = (
        "용의 진화",
        "용의 ",
        "혼돈의 ",
        "혼란스러운",
        "쉴드",
        "실드",
        "데미지",
        "엔터티",
        "재고",
        "장바구니",
        "마피아 그라인더",
        "가슴 색상",
        "유료보유",
        "모래밭",
        "십이지장",
        "400분의 1",
        "11월10일",
    )
    for key, target in korean.items():
        if isinstance(target, str) and any(term in target for term in forbidden):
            errors.append(f"draconicevolution:{key}: 기계번역 흔적")
    report = {
        "language_keys_reviewed": len(english),
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_language_validation.json", report)
    return report, errors


def audit() -> dict[str, object]:
    instance = resolve_source_root()
    jar = next((instance / "mods").glob("Draconic-Evolution-*.jar"))
    advancements = display_nodes = 0
    with ZipFile(jar) as archive:
        for name in archive.namelist():
            if "/advancement/" not in name or not name.endswith(".json"):
                continue
            advancements += 1
            data = json.loads(archive.read(name))
            if isinstance(data, dict) and isinstance(data.get("display"), dict):
                display_nodes += 1
    references: list[str] = []
    direct_display: list[str] = []
    unhandled_display: list[str] = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not re.search(r"draconicevolution:|draconic evolution", text, re.I):
            continue
        relative = path.relative_to(instance).as_posix()
        references.append(relative)
        if path.suffix.lower() == ".js":
            for number, line in enumerate(text.splitlines(), start=1):
                if "draconic evolution" not in line.lower():
                    continue
                if re.search(
                    r"addAnnouncement|displayName|setHoverName|tooltip|"
                    r"Text\.(?:of|literal)",
                    line,
                    re.I,
                ):
                    location = f"{relative}:{number}"
                    direct_display.append(location)
                    if not (
                        relative
                        == "kubejs/server_scripts/announcements/announcements.js"
                        and 'addAnnouncement("4.7"' in line
                    ):
                        unhandled_display.append(location)
    announcement = (
        active_output_root()
        / "overrides/kubejs/server_scripts/announcements/announcements.js"
    )
    announcement_verified = announcement.is_file() and (
        'addAnnouncement("4.7", "추가된 모드: Draconic Evolution, '
        'BotanyPots-Mystical")' in announcement.read_text(encoding="utf-8")
    )
    if direct_display and not announcement_verified:
        unhandled_display.append("Draconic Evolution 추가 공지 번역 누락")
    report = {
        "advancement_files": advancements,
        "advancement_display_nodes": display_nodes,
        "kubejs_reference_files": references,
        "kubejs_direct_display_lines": direct_display,
        "existing_kubejs_translations_verified": int(announcement_verified),
        "unhandled_kubejs_display": unhandled_display,
        "status": "complete" if not unhandled_display else "review_required",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report


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
        report = normalize_language()
        code = 0
    elif args.command == "normalize-quests":
        report = normalize_quests()
        code = 0
    elif args.command == "verify-language":
        report, errors = verify_language()
        code = 1 if errors else 0
    elif args.command == "verify-quests":
        report, errors = verify_quests()
        code = 1 if errors else 0
    else:
        report = audit()
        code = 0 if report["status"] == "complete" else 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
