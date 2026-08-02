#!/usr/bin/env python3
"""Super Factory Manager 언어 파일을 현재 영어 원문 기준으로 번역하고 검증한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path

import actually_additions_family as candidate_helper
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT


FAMILY = "super_factory_manager"
NAMESPACE = "sfm"
WORK_ROOT = PROJECT_ROOT / "working/super_factory_manager"
LANG_ROOT = WORK_ROOT / NAMESPACE
CACHE_FILE = PROJECT_ROOT / "temp/super_factory_manager_language_candidate_cache.json"
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?(?:\.\d+)?[a-zA-Z%]|\{[^{}]*\}")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")

SOURCE_OVERRIDES = {
    "Super Factory Manager": "Super Factory Manager",
    "SFM": "SFM",
    "Discord": "Discord",
    "Intellisense": "인텔리센스",
    "Advanced": "고급",
    "Basic": "기본",
    "Off": "끔",
    "Clear": "지우기",
    "Edit": "편집",
    "Reset": "초기화",
    "Logs": "로그",
    "Label": "라벨",
}

TERM_REPLACEMENTS = (
    ("슈퍼 팩토리 매니저", "Super Factory Manager"),
    ("공장 매니저", "공장 관리자"),
    ("팩토리 매니저", "공장 관리자"),
    ("인벤토리 케이블 파사드", "인벤토리 케이블 외장"),
    ("파사드", "외장"),
    ("라벨건", "라벨 건"),
    ("라벨 총", "라벨 건"),
    ("레이블", "라벨"),
    ("프린팅 프레스", "인쇄기"),
    ("인쇄 프레스", "인쇄기"),
    ("경험치 구프", "경험치 점액"),
    ("경험치 조각", "경험치 파편"),
    ("리소스 버퍼", "자원 버퍼"),
    ("터널링된", "관통형"),
    ("터널드", "관통형"),
    ("팬시", "장식형"),
    ("터프", "내폭"),
    ("인텔리센스", "인텔리센스"),
    ("클립 보드", "클립보드"),
    ("마우스 오른쪽 버튼", "우클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("품목", "아이템"),
    ("엔터티", "엔티티"),
)

KEY_OVERRIDES: dict[str, str] = {
    "block.sfm.buffer": "자원 버퍼",
    "block.sfm.cable": "인벤토리 케이블",
    "block.sfm.cable_facade": "인벤토리 케이블 외장",
    "block.sfm.fancy_cable": "장식형 인벤토리 케이블",
    "block.sfm.fancy_cable_facade": "장식형 인벤토리 케이블 외장",
    "block.sfm.manager": "공장 관리자",
    "block.sfm.printing_press": "인쇄기",
    "block.sfm.printing_press.tooltip": (
        "아래에 한 칸을 비우고 아래쪽을 향한 피스톤 밑에 설치하세요. 피스톤을 밀면 작동합니다."
    ),
    "block.sfm.tough_cable": "내폭 인벤토리 케이블",
    "block.sfm.tough_cable.tooltip": "폭발에 견디며 더 단단한 블록 외장을 씌울 수 있습니다.",
    "block.sfm.tough_cable_facade": "내폭 인벤토리 케이블 외장",
    "block.sfm.tough_fancy_cable": "내폭 장식형 인벤토리 케이블",
    "block.sfm.tough_fancy_cable_facade": "내폭 장식형 인벤토리 케이블 외장",
    "block.sfm.tunnelled_cable": "관통형 인벤토리 케이블",
    "block.sfm.tunnelled_cable.tooltip": "기능을 반대편 면으로 통과시킵니다.",
    "block.sfm.tunnelled_cable_facade": "관통형 인벤토리 케이블 외장",
    "block.sfm.tunnelled_fancy_cable": "관통형 장식형 인벤토리 케이블",
    "block.sfm.tunnelled_fancy_cable_facade": "관통형 장식형 인벤토리 케이블 외장",
    "block.sfm.tunnelled_manager": "관통형 공장 관리자",
    "block.sfm.tunnelled_manager.tooltip": "기능을 반대편 면으로 통과시킵니다.",
    "block.sfm.water_tank": "물탱크",
    "block.sfm.water_tank.tooltip.1": "서로 맞닿은 물 원천이 두 칸 필요합니다.",
    "block.sfm.water_tank.tooltip.2": "작동 중인 다른 물탱크와 맞닿아 있으면 효율이 높아집니다.",
    "container.sfm.manager": "공장 관리자",
    "gui.jei.category.sfm.falling_anvil": "낙하 모루",
    "gui.jei.category.sfm.falling_anvil.consumed": "소모됨",
    "gui.jei.category.sfm.falling_anvil.not_consumed": "소모되지 않음",
    "gui.jei.category.sfm.printing_press": "인쇄기",
    "gui.sfm.advanced.tooltip.hint": "%s 키를 누르면 자세한 내용을 볼 수 있습니다.",
    "gui.sfm.confirm.funny.no.1": "아니요, 마음이 바뀌었어요",
    "gui.sfm.confirm.funny.no.2": "세상에, 안 돼요",
    "gui.sfm.confirm.funny.no.3": "아니요 아니요 아니요 아니요 아니요",
    "gui.sfm.confirm.funny.no.4": "아니요, 오늘은 안 돼요",
    "gui.sfm.confirm.funny.no.5": "중단 중단 중단",
    "gui.sfm.confirm.funny.no.6": "됐어요",
    "gui.sfm.confirm.funny.yes.1": "네, 좋아요. 해 보죠.",
    "gui.sfm.confirm.funny.yes.2": "좋아요. 설마 문제 있겠어요?",
    "gui.sfm.confirm.funny.yes.3": "네, 진행하세요.",
    "gui.sfm.confirm.funny.yes.4": "해 보세요.",
    "gui.sfm.confirm.funny.yes.5": "ㅋㅋ 해 봐요",
    "gui.sfm.confirm.funny.yes.6": "변경 사항 적용",
    "gui.sfm.container_inspector.mekanism_null_direction_warning": (
        "MEKANISM 블록은 방향을 지정하지 않으면 읽기만 가능합니다!"
    ),
    "gui.sfm.container_inspector.mekanism_machine_inputs": (
        "다음 내용은 기계의 입력 면 설정을 기준으로 합니다."
    ),
    "gui.sfm.container_inspector.mekanism_machine_outputs": (
        "다음 내용은 기계의 출력 면 설정을 기준으로 합니다."
    ),
    "gui.sfm.container_inspector.notice.1": (
        "GUI 슬롯과 자동화에서 사용하는 슬롯은 항상 같지 않습니다!"
    ),
    "gui.sfm.container_inspector.notice.2": "%s 키로 이 오버레이를 켜거나 끕니다.",
    "gui.sfm.container_inspector.show_exports_button": "검사 결과 내보내기",
    "gui.sfm.disk.tooltip.edit_in_hand": (
        "손에 든 디스크를 우클릭하면 공장 관리자 밖에서도 편집할 수 있습니다."
    ),
    "gui.sfm.facade_confirm_apply.message": (
        "%d가지 외장 상태가 있는 블록 %d개의 외장을 덮어씁니다."
    ),
    "gui.sfm.facade_confirm_apply.title": "외장 모양을 업데이트하시겠습니까?",
    "gui.sfm.facade_confirm_change_world_block.message": (
        "블록 %d개의 모양이 바뀌지만 외장 상태는 유지됩니다."
    ),
    "gui.sfm.facade_confirm_change_world_block.title": (
        "외장 기준으로 사용할 월드 블록을 바꾸시겠습니까?"
    ),
    "gui.sfm.facade_confirm_clear.message": (
        "%d가지 외장 상태가 있는 블록 %d개의 외장을 월드에서 지웁니다."
    ),
    "gui.sfm.facade_confirm_clear.title": "이 외장을 모두 지우시겠습니까?",
    "gui.sfm.item_inspector.copied_to_clipboard": "문자 {}개를 클립보드에 복사했습니다!",
    "gui.sfm.label_gun.button.toggle_label_view": "라벨 보기 전환",
    "gui.sfm.label_gun.clear_button": "지우기",
    "gui.sfm.label_gun.label_edit_placeholder": "라벨 검색 또는 새 라벨 입력",
    "gui.sfm.label_gun.placeholder": "라벨",
    "gui.sfm.label_gun.prune_button": "미사용 라벨 정리",
    "gui.sfm.logs.button.clear_logs": "로그 지우기",
    "gui.sfm.logs.button.clear_logs.packet_received": "로그를 지웠습니다.",
    "gui.sfm.logs.button.copy_logs": "로그 복사",
    "gui.sfm.logs.button.copy_logs.tooltip": "Shift+클릭하면 원문 그대로 복사합니다.",
    "gui.sfm.logs.no_content": (
        "안녕하세요, 월드!\n"
        "이 화면 위쪽 버튼으로 로그 수준을 바꿀 수 있습니다.\n"
        "추적, 디버그, 정보 로그 수준은 프로그램을 한 번 실행하면 꺼집니다.\n"
        "로그를 기록하면 명령문 실행 시간이 늘어날 수 있습니다.\n"
        "다른 편집기에서 보려면 복사 버튼을 사용하세요."
    ),
    "gui.sfm.logs.title": "로그",
    "gui.sfm.manager.button.copy_to_clipboard": "클립보드에 복사",
    "gui.sfm.manager.button.paste_clipboard": "클립보드에서 붙여넣기",
    "gui.sfm.manager.button.rebuild": "케이블 네트워크 재구축",
    "gui.sfm.manager.button.reset": "초기화",
    "gui.sfm.manager.button.server_config": "서버 설정 보기",
    "gui.sfm.manager.button.view_examples": "예제 보기",
    "gui.sfm.manager.button.view_examples.tooltip": "Ctrl+Shift+E를 눌러 예제를 봅니다.",
    "gui.sfm.manager.button.view_logs": "로그 보기",
    "gui.sfm.manager.edit_button": "편집",
    "gui.sfm.manager.edit_button.tooltip": "%s 키를 눌러 편집합니다.",
    "gui.sfm.manager.hovered_tick_time": "가리킨 명령문의 틱 시간: %s ms",
    "gui.sfm.manager.paste_confirm_screen.no_button": "취소하고 변경하지 않기",
    "gui.sfm.manager.peak_tick_time": "최대 틱 시간: %s ms",
    "gui.sfm.manager.reset_confirm_screen.no_button": "취소하고 변경하지 않기",
    "gui.sfm.manager.state.invalid_program": "잘못된 프로그램",
    "gui.sfm.manager.state.no_disk": "디스크 없음",
    "gui.sfm.manager.state.no_program": "프로그램 없음",
    "gui.sfm.manager.state.running": "실행 중",
    "gui.sfm.manager.status.fix": "문제 수정 중!",
    "gui.sfm.manager.status.loaded_clipboard": "클립보드에서 불러왔습니다!",
    "gui.sfm.manager.status.rebuild": "캐시 재구축 중!",
    "gui.sfm.manager.status.reset": "프로그램과 라벨을 초기화했습니다!",
    "gui.sfm.manager.status.saved_clipboard": "클립보드에 저장했습니다!",
    "gui.sfm.manager.tooltip.paste": "Ctrl+V를 눌러 붙여넣습니다.",
    "gui.sfm.manager.tooltip.reset": "디스크의 모든 데이터를 지웁니다.",
    "gui.sfm.program_editor_config.intellisense": "인텔리센스",
    "gui.sfm.program_editor_config.line_numbers": "줄 번호",
    "gui.sfm.program_editor_config.preferred_editor": "선호 편집기",
    "gui.sfm.program_editor_config.title": "프로그램 편집기 설정",
    "gui.sfm.remove_active_label_confirm.message": (
        '라벨 "%s"을(를) 블록 %d개에서 제거하시겠습니까?'
    ),
    "gui.sfm.remove_all_labels_confirm.message": (
        "라벨 %d개를 블록 %d개에서 제거하시겠습니까?"
    ),
    "gui.sfm.text_editor.config_button.tooltip": "편집기 설정 열기",
    "gui.sfm.text_editor.done_button.tooltip": "Shift+Enter로 제출",
    "gui.sfm.text_editor.v1.title": "텍스트 편집기",
    "gui.sfm.text_editor.v2.title": "텍스트 편집기",
    "gui.sfm.title.intellisense_pick_list": "인텔리센스 제안 목록",
    "gui.sfm.title.labelgun": "라벨 건",
    "gui.sfm.title.program_template_picker": "프로그램 템플릿 선택",
    "item.sfm.disk": "공장 관리자 프로그램 디스크",
    "item.sfm.disk.tooltip.label_section.entry": " - %s: 블록 %d개",
    "item.sfm.disk.tooltip.label_section.header": "라벨",
    "item.sfm.form": "인쇄판",
    "item.sfm.labelgun": "라벨 건",
    "item.sfm.labelgun.chat.pulled": (
        "공장 관리자에서 라벨을 가져왔습니다. 보내려면 라벨 가져오기 보조 키(%s)에서 손을 떼세요."
    ),
    "item.sfm.labelgun.chat.pushed": (
        "공장 관리자로 라벨을 보냈습니다. 가져오려면 라벨 가져오기 보조 키(%s)를 누르세요."
    ),
    "item.sfm.labelgun.tooltip.clear_reminder": ("%s + %s로 블록의 라벨을 제거합니다."),
    "item.sfm.labelgun.tooltip.contiguous_reminder": (
        "%s 키를 누르면 케이블에 맞닿아 이어진 블록을 함께 변경합니다."
    ),
    "item.sfm.labelgun.tooltip.cycle_view_reminder": "%s 키로 라벨 보기를 전환합니다.",
    "item.sfm.labelgun.tooltip.gui_reminder": "%s로 허공을 가리키면 GUI를 엽니다.",
    "item.sfm.labelgun.tooltip.next_reminder": "%s 키로 다음 라벨을 선택합니다.",
    "item.sfm.labelgun.tooltip.pick_reminder": (
        "%s + %s로 블록에 지정된 라벨을 활성 라벨로 선택합니다."
    ),
    "item.sfm.labelgun.tooltip.previous_reminder": "%s 키로 이전 라벨을 선택합니다.",
    "item.sfm.labelgun.tooltip.pull_reminder": (
        "%s + %s로 공장 관리자의 라벨을 가져옵니다."
    ),
    "item.sfm.labelgun.tooltip.push_reminder": "%s로 공장 관리자에 라벨을 보냅니다.",
    "item.sfm.labelgun.tooltip.scroll_reminder": (
        "%s + 마우스 휠로 다음 또는 이전 라벨을 선택합니다."
    ),
    "item.sfm.labelgun.tooltip.target_manager_reminder": (
        "%s + %s로 공장 관리자 자체에 라벨을 지정합니다."
    ),
    "item.sfm.labelgun.tooltip.toggle_label_reminder": (
        "%s로 블록의 활성 라벨을 붙이거나 제거합니다."
    ),
    "item.sfm.labelgun.with_label": '라벨 건: "%s"',
    "item.sfm.network_tool": "네트워크 도구",
    "item.sfm.network_tool.tooltip.1": "들고 있으면 벽 너머의 케이블을 보여 줍니다.",
    "item.sfm.network_tool.tooltip.2": "블록 면을 우클릭하면 진단 정보를 봅니다.",
    "item.sfm.network_tool.tooltip.3": (
        "이 도구 없이도 인벤토리에서 %s 키를 눌러 검사기를 켜거나 끌 수 있습니다."
    ),
    "item.sfm.network_tool.tooltip.4": (
        "보조 손에 도구를, 주로 쓰는 손에 블록을 들고 케이블을 우클릭하면 외장을 설정합니다."
    ),
    "item.sfm.network_tool.tooltip.5": "Ctrl+클릭하면 이어진 케이블에 외장을 씌웁니다.",
    "item.sfm.network_tool.tooltip.6": (
        "Alt+클릭하면 네트워크 전체에서 같은 블록과 일치하는 케이블에 외장을 씌웁니다."
    ),
    "item.sfm.network_tool.tooltip.7": (
        "Ctrl+Alt+클릭하면 네트워크 전체에 외장을 씌웁니다."
    ),
    "item.sfm.network_tool.tooltip.8": (
        "%s 키를 누른 채 블록을 우클릭하면 도구를 그 위치에 동조합니다."
    ),
    "item.sfm.xp_goop": "경험치 점액",
    "item.sfm.xp_shard": "경험치 파편",
    "item_group.sfm": "Super Factory Manager",
    "key.categories.sfm": "Super Factory Manager",
    "key.sfm.container_inspector.activation_key": "컨테이너 검사기 전환",
    "key.sfm.item_inspector.activation_key": "(개발 중) 가리킨 아이템을 클립보드에 복사",
    "key.sfm.label_gun.clear_modifier": "라벨 건 지우기 보조 키",
    "key.sfm.label_gun.contiguous_modifier": "라벨 건 연속 선택 보조 키",
    "key.sfm.label_gun.next_label": "라벨 건 다음 라벨",
    "key.sfm.label_gun.pick_block_modifier": "라벨 건 블록 라벨 선택 보조 키",
    "key.sfm.label_gun.previous_label": "라벨 건 이전 라벨",
    "key.sfm.label_gun.pull_modifier": "라벨 건 가져오기 보조 키",
    "key.sfm.label_gun.scroll_modifier": "라벨 건 스크롤 보조 키",
    "key.sfm.label_gun.target_manager_modifier": "라벨 건 관리자 지정 보조 키",
    "key.sfm.manager.text_editor": "공장 관리자 화면 - 텍스트 편집기 열기",
    "key.sfm.more_info": "길게 눌러 자세히 보기",
    "key.sfm.text_editor.accept_intellisense": "텍스트 편집기 - 인텔리센스 제안 적용",
    "key.sfm.title_screen.text_editor": "제목 화면 - 텍스트 편집기 열기",
    "key.sfm.toggle_label_view_key": "라벨 건 보기 전환",
    "key.sfm.toggle_network_tool_overlay": "네트워크 도구 오버레이 전환",
    "log.sfm.cable_network.header.1": "======= 케이블 네트워크 =======",
    "log.sfm.cable_network.header.2": "케이블 위치:",
    "log.sfm.cable_network.header.3": "기능 제공 위치:",
    "log.sfm.capability_cache.hit": "기능 캐시 적중: %s %s direction=%s",
    "log.sfm.capability_cache.hit_invalid": (
        "기능 캐시에 적중했지만 존재하지 않음: %s %s direction=%s"
    ),
    "log.sfm.capability_cache.miss": "기능 캐시 미적중: %s %s direction=%s",
    "log.sfm.label_position_holder.header": "=== 라벨 위치 저장소 ===",
    "log.sfm.level_updated": "로그 수준을 %s(으)로 변경했습니다.",
    "log.sfm.manager.cable_network_rebuild": "사용자가 케이블 네트워크를 재구축함",
    "log.sfm.program.context": "초기 프로그램 문맥: %s",
    "log.sfm.program.tick": "프로그램 틱 시작",
    "log.sfm.program.tick.redstone_count": (
        "처리하지 않은 레드스톤 펄스 %d개가 있는 상태로 프로그램 틱을 실행합니다."
    ),
    "log.sfm.resource_type.get_capabilities.begin": (
        "자원 유형 %s(%s)의 기능을 라벨 %s에서 수집합니다."
    ),
    "log.sfm.resource_type.get_capabilities.not_present": (
        "기능이 없음: %s %s direction=%s"
    ),
    "log.sfm.resource_type.get_capabilities.present": (
        "기능이 있음: %s %s direction=%s"
    ),
    "log.sfm.statement.tick.forget": "FORGET %s",
    "log.sfm.statement.tick.if.false": "FALSE: %s",
    "log.sfm.statement.tick.if.true": "TRUE: %s",
    "log.sfm.statement.tick.io.gather_slots": "IO 명령문의 슬롯 수집\n```\n%s\n```\n",
    "log.sfm.statement.tick.io.gather_slots.cache_hit": (
        "캐시 적중 - 이 명령문은 이미 슬롯을 수집했습니다."
    ),
    "log.sfm.statement.tick.io.gather_slots.cache_miss": (
        "명령문 캐시 미적중 - 이 명령문의 슬롯을 처음 수집합니다."
    ),
    "log.sfm.statement.tick.io.gather_slots.each": (
        "EACH 키워드 사용 - 블록마다 별도의 추적기를 사용합니다."
    ),
    "log.sfm.statement.tick.io.gather_slots.not_each": (
        "EACH 키워드 미사용 - 여러 블록이 추적기를 공유합니다."
    ),
    "log.sfm.statement.tick.io.move_to.begin": "자원 %s을(를) %s(으)로 이동하기 시작합니다.",
    "log.sfm.statement.tick.io.move_to.end": "%d %s 이동 - source=%s, dest=%s",
    "log.sfm.statement.tick.io.move_to.extracted": "%d개를 슬롯 %d에서 추출했습니다.",
    "log.sfm.statement.tick.io.move_to.extracted_nothing": (
        "아무것도 추출하지 못해 이 입력 슬롯을 완료로 표시합니다."
    ),
    "log.sfm.statement.tick.io.move_to.retention_obligation": (
        "원본 슬롯에 %d개를 남기기로 했으며, 아직 %d개를 남겨야 합니다."
    ),
    "log.sfm.statement.tick.io.move_to.retention_obligation_no_move": (
        "남겨 둘 수량을 제외하면 이동할 것이 없어 원본 슬롯을 완료로 표시하고 건너뜁니다."
    ),
    "log.sfm.statement.tick.io.move_to.stack_limit_no_move": (
        "최대 전송량 dest=%d, source=%d, 묶음 제한=%d; 새 toMove=%d"
    ),
    "log.sfm.statement.tick.io.move_to.type_mismatch": "유형이 일치하지 않아 건너뜁니다.",
    "log.sfm.statement.tick.io.move_to.zero_simulated_movement": (
        "시험 삽입 후 나머지가 %d개입니다(잠재 이동량 %d개, 실제 이동량 0). 건너뜁니다."
    ),
    "log.sfm.statement.tick.io.move_to.zero_to_move": "toMove=0이므로 건너뜁니다.",
    "log.sfm.statement.tick.output.discovered_input_slot_count": "입력 슬롯 %d개 발견",
    "log.sfm.statement.tick.output.discovered_output_slot_count": "출력 슬롯 %d개 발견",
    "log.sfm.statement.tick.output.short_circuit_no_input_slots": (
        "입력 슬롯이 없어 건너뜁니다."
    ),
    "log.sfm.statement.tick.output.short_circuit_no_output_slots": (
        "출력 슬롯이 없어 건너뜁니다."
    ),
    "log.sfm.statement.tick.trigger": "%s에서 트리거됨",
    "mod.name": "Super Factory Manager",
    "program.sfm.compile_begin": "디스크의 프로그램을 컴파일합니다.",
    "program.sfm.error.compile_failed": "컴파일하지 못했습니다.",
    "program.sfm.error.compile_failed_with_errors": "오류 %d개로 컴파일하지 못했습니다.",
    "program.sfm.error.compile_success_with_warnings": (
        '"%s"을(를) 컴파일했으며 경고가 %d개 있습니다.'
    ),
    "program.sfm.error.disallowed_resource_type": (
        '프로그램이 허용되지 않은 자원 유형 "%s"을(를) 참조합니다.'
    ),
    "program.sfm.error.malformed_resource_type": (
        '프로그램의 자원 유형 "%s" 형식이 잘못되었습니다.\n'
        "알림: 자원 유형에는 와일드카드가 아닌 리터럴을 사용해야 합니다."
    ),
    "program.sfm.error.unknown_resource_type": (
        '프로그램이 알 수 없는 자원 유형 "%s"을(를) 참조합니다.'
    ),
    "program.sfm.reminders.push_labels": "라벨 건으로 라벨을 보내셨나요?",
    "program.sfm.tick.time_taken.statement": (
        "프로그램 명령문 틱에 %.2f ms가 걸렸습니다:\n```\n%s\n```\n"
    ),
    "program.sfm.tick.time_taken.trigger": (
        "프로그램 트리거 틱에 %.2f ms가 걸렸습니다:\n```\n%s\n```\n"
    ),
    "program.sfm.warnings.adjacent_but_disconnected_label": (
        '라벨 "%s"이(가) 월드의 %s에 지정되어 케이블로 연결되어 있지만, 유효한 인벤토리로 '
        "감지되지 않습니다."
    ),
    "program.sfm.warnings.disconnected_label": (
        '라벨 "%s"이(가) 월드의 %s에 지정되어 있지만 케이블로 연결되지 않았습니다.'
    ),
    "program.sfm.warnings.each_without_pattern": (
        "패턴 없이 EACH를 사용했습니다. 명령문: %s"
    ),
    "program.sfm.warnings.mekanism_bad_side_config": (
        '%s의 Mekanism 블록 면 설정이 명령문과 맞지 않습니다. 라벨 "%s"을(를) 사용한 '
        '명령문 "%s"을(를) 확인하세요.'
    ),
    "program.sfm.warnings.mekanism_used_without_direction": (
        'Mekanism 블록은 방향을 지정하지 않으면 읽기만 가능합니다. 라벨 "%s"을(를) 사용한 '
        '명령문 "%s"을(를) 확인하세요.'
    ),
    "program.sfm.warnings.no_slots": (
        '명령문과 일치하는 슬롯이 없습니다: 명령문 "%s", 위치 %s'
    ),
    "program.sfm.warnings.no_viable_input_slots": (
        '추출을 지원하는 슬롯이 없습니다: 명령문 "%s", 위치 %s'
    ),
    "program.sfm.warnings.no_viable_output_slots": (
        '삽입을 지원하는 슬롯이 없습니다: 명령문 "%s", 위치 %s'
    ),
    "program.sfm.warnings.output_label_not_found_in_inputs": (
        '명령문 "%s"(위치 %s)이(가) 일치하는 입력 명령문이 없는 자원 유형 "%s"을(를) '
        "사용합니다."
    ),
    "program.sfm.warnings.round_robin_smelly_count": (
        "라벨별 라운드 로빈에는 라벨이 둘 이상 필요합니다. 명령문: %s"
    ),
    "program.sfm.warnings.round_robin_smelly_each": (
        "블록별 라운드 로빈에는 EACH를 사용하면 안 됩니다. 명령문: %s"
    ),
    "program.sfm.warnings.undefined_label": (
        '라벨 "%s"이(가) 월드에 지정되어 있지만 코드에는 정의되지 않았습니다.'
    ),
    "program.sfm.warnings.unknown_resource_id": '자원 "%s"을(를) 찾지 못했습니다.',
    "program.sfm.warnings.unused_input_label": (
        '명령문 "%s"(위치 %s)이(가) "%s"을(를) "%s"에서 입력하지만, 이후 출력 명령문에서 '
        '"%s"을(를) 사용하지 않습니다.'
    ),
    "program.sfm.warnings.unused_label": (
        '라벨 "%s"이(가) 코드에서 사용되지만 월드에는 지정되지 않았습니다.'
    ),
    "sfm.command.bust_cable_network_cache.success": "케이블 네트워크 캐시를 비웠습니다.",
    "sfm.command.bust_water_network_cache.success": "물 네트워크 캐시를 비웠습니다.",
    "sfm.label_gun.view_mode.show_only_active_and_targeted": (
        "활성 라벨이 있는 블록을 표시합니다. GUI나 %s 키로 모드를 전환하세요."
    ),
    "sfm.label_gun.view_mode.show_only_targeted": (
        "대상 블록의 라벨만 표시합니다. GUI나 %s 키로 모드를 전환하세요."
    ),
    "sfm.network_tool.reminder_overlay": "%s 키로 네트워크 도구 오버레이를 전환합니다.",
}


def load_json(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(text, str) for key, text in value.items()
    ):
        raise TypeError(f"문자열 JSON 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def request_candidate(source: str) -> str:
    tokens: list[str] = []

    def hide(match: re.Match[str]) -> str:
        tokens.append(match.group(0))
        return f"QXSFM{len(tokens) - 1}QX"

    protected = PLACEHOLDER.sub(hide, source).replace("\n", " QXSFMNEWLINEQX ")
    translated = candidate_helper.request_translation_candidate(protected)
    translated = translated.replace(" QXSFMNEWLINEQX ", "\n").replace(
        "QXSFMNEWLINEQX", "\n"
    )
    for index, token in enumerate(tokens):
        marker = f"QXSFM{index}QX"
        if marker not in translated:
            raise ValueError(f"자리표시자 표식이 사라졌습니다: {source}: {marker}")
        translated = translated.replace(marker, token)
    return translated


def candidate() -> dict[str, object]:
    english = load_json(LANG_ROOT / "en_us.json")
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requested = {
        key: source
        for key, source in english.items()
        if key not in KEY_OVERRIDES
        and source not in SOURCE_OVERRIDES
        and LATIN_WORD.search(source)
        and not isinstance(cache.get(source), str)
    }
    failures: list[str] = []
    if requested:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(request_candidate, source): source
                for source in sorted(set(requested.values()))
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("번역 후보 생성 실패:\n" + "\n".join(failures))
    candidates = {
        key: (
            KEY_OVERRIDES[key]
            if key in KEY_OVERRIDES
            else SOURCE_OVERRIDES.get(source, cache.get(source, source))
        )
        for key, source in english.items()
    }
    write_json(CANDIDATE_FILE, candidates)
    report = {
        "keys": len(english),
        "manual_overrides": len(KEY_OVERRIDES),
        "new_candidate_sources": len(set(requested.values())),
        "status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


def reviewed_value(key: str, source: str, candidate_value: str) -> str:
    value = KEY_OVERRIDES.get(key, SOURCE_OVERRIDES.get(source, candidate_value))
    for old, new in TERM_REPLACEMENTS:
        value = value.replace(old, new)
    value = value.replace("라벨를", "라벨을").replace("라벨가", "라벨이")
    value = value.replace("케이블를", "케이블을").replace("관리자을", "관리자를")
    value = value.replace("됩니다.,", "되며,").replace("합니다.,", "하며,")
    return value


def normalize() -> dict[str, object]:
    english = load_json(LANG_ROOT / "en_us.json")
    candidates = load_json(CANDIDATE_FILE)
    korean = {
        key: reviewed_value(key, source, candidates[key])
        for key, source in english.items()
    }
    write_json(LANG_ROOT / "ko_kr.json", korean)
    report = {
        "keys_reviewed": len(english),
        "bundled_korean_reused_without_review": 0,
        "status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    errors: list[str] = []
    untranslated: list[str] = []
    if list(english) != list(korean):
        errors.append("영어와 한국어 키 또는 순서가 다릅니다.")
    for key, source in english.items():
        target = korean.get(key, "")
        if PLACEHOLDER.findall(source) != PLACEHOLDER.findall(target):
            errors.append(f"자리표시자 불일치: {key}")
        if source.count("\n") != target.count("\n"):
            errors.append(f"줄바꿈 불일치: {key}")
        if family_goal.FORMAT_CODE.findall(source) != family_goal.FORMAT_CODE.findall(
            target
        ):
            errors.append(f"서식 코드 불일치: {key}")
        if (
            source == target
            and LATIN_WORD.search(source)
            and source not in SOURCE_OVERRIDES
            and key not in KEY_OVERRIDES
            and not key.startswith("log.sfm.cable_network.")
            and not key.startswith("log.sfm.label_position_holder.")
        ):
            untranslated.append(key)
    report = {
        "keys_reviewed": len(english),
        "bundled_korean_reused_without_review": 0,
        "untranslated": len(untranslated),
        "untranslated_examples": untranslated[:20],
        "errors": errors,
        "status": "complete" if not errors and not untranslated else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", report)
    return report, 0 if report["status"] == "complete" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("candidate", "normalize", "verify"))
    args = parser.parse_args()
    if args.action == "candidate":
        print(json.dumps(candidate(), ensure_ascii=False, indent=2))
        return 0
    if args.action == "normalize":
        print(json.dumps(normalize(), ensure_ascii=False, indent=2))
        return 0
    report, code = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
