#!/usr/bin/env python3
"""Little Big Redstone과 Redstone Pen의 현재 JAR 영어 전체를 번역·검증한다."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "little_redstone"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
RESOURCEPACK_ROOT = active_output_root() / "resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[./xX×]\d+)*")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
ALLOWED_LATIN = {
    "AND",
    "Big",
    "Ctrl",
    "Little",
    "NAND",
    "NOR",
    "NOT",
    "Pen",
    "PLC",
    "RCA",
    "RUN",
    "Redstone",
    "STOP",
    "Shift",
    "XOR",
}
CODE_HEAVY_PREFIX = "block.redstonepen.control_box.help."

COLORS = {
    "black": "검은색",
    "blue": "파란색",
    "brown": "갈색",
    "cyan": "청록색",
    "gray": "회색",
    "green": "초록색",
    "light_blue": "하늘색",
    "light_gray": "밝은 회색",
    "lime": "연두색",
    "magenta": "자홍색",
    "orange": "주황색",
    "pink": "분홍색",
    "purple": "보라색",
    "red": "빨간색",
    "white": "하얀색",
    "yellow": "노란색",
}

LITTLE_ITEMS = {
    "and_gate": "AND 게이트",
    "calculator": "계산기",
    "comparator": "비교기",
    "debugger": "디버거",
    "io": "I/O 포트",
    "nand_gate": "NAND 게이트",
    "nor_gate": "NOR 게이트",
    "not_gate": "NOT 게이트",
    "or_gate": "OR 게이트",
    "pulse_throttler": "펄스 조절기",
    "randomizer": "무작위 선택기",
    "reader": "판독기",
    "redstone_bit": "레드스톤 비트",
    "redstone_circuit_board": "레드스톤 회로 기판",
    "rs_nor_latch": "RS NOR 래치",
    "selector": "선택기",
    "sequencer": "시퀀서",
    "t_flip_flop": "T 플립플롭",
    "tag": "태그",
    "xor_gate": "XOR 게이트",
}

LITTLE_TEXT = {
    "itemGroup.little_big_redstone.little_big_redstone": "Little Big Redstone",
    "key.categories.little_big_redstone.little_big_redstone": "Little Big Redstone",
    "key.little_big_redstone.open_note_board": "메모판 열기",
    "text.little_big_redstone.all": "모두",
    "text.little_big_redstone.any": "하나 이상",
    "text.little_big_redstone.capability_comparator": "비교기",
    "text.little_big_redstone.capability_energy": "에너지",
    "text.little_big_redstone.capability_fluid": "유체",
    "text.little_big_redstone.capability_item": "아이템",
    "text.little_big_redstone.count_and_percentage": "%s (%s)",
    "text.little_big_redstone.direction_down": "아래쪽",
    "text.little_big_redstone.direction_east": "동쪽",
    "text.little_big_redstone.direction_north": "북쪽",
    "text.little_big_redstone.direction_south": "남쪽",
    "text.little_big_redstone.direction_up": "위쪽",
    "text.little_big_redstone.direction_west": "서쪽",
    "text.little_big_redstone.emitter": "송신기",
    "text.little_big_redstone.floppy_disk": "플로피 디스크",
    "text.little_big_redstone.floppy_disk_apply_failure": (
        "마이크로칩 프로그램을 설치하지 못했습니다."
    ),
    "text.little_big_redstone.floppy_disk_apply_failure_malformed": (
        "마이크로칩 프로그램이 손상되어 설치할 수 없습니다."
    ),
    "text.little_big_redstone.floppy_disk_apply_success": (
        "플로피 디스크의 프로그램을 마이크로칩에 설치했습니다."
    ),
    "text.little_big_redstone.floppy_disk_button_close": "닫기",
    "text.little_big_redstone.floppy_disk_button_load": "불러오기",
    "text.little_big_redstone.floppy_disk_button_save": "저장",
    "text.little_big_redstone.floppy_disk_clear": (
        "플로피 디스크의 마이크로칩 프로그램을 지웠습니다."
    ),
    "text.little_big_redstone.floppy_disk_file_doesnt_exist": (
        "이름이 %s인 마이크로칩 프로그램 파일이 없습니다."
    ),
    "text.little_big_redstone.floppy_disk_file_failed_to_load": (
        "파일에서 마이크로칩 프로그램을 불러오는 중 오류가 발생했습니다. "
        "자세한 내용은 로그를 확인하세요."
    ),
    "text.little_big_redstone.floppy_disk_file_failed_to_save": (
        "플로피 디스크의 내용을 파일로 저장하는 중 오류가 발생했습니다. "
        "자세한 내용은 로그를 확인하세요."
    ),
    "text.little_big_redstone.floppy_disk_file_loaded": (
        "마이크로칩 프로그램 %s을(를) 불러왔습니다!"
    ),
    "text.little_big_redstone.floppy_disk_file_saved": (
        "플로피 디스크의 내용을 %s(으)로 저장했습니다!"
    ),
    "text.little_big_redstone.floppy_disk_help_1": (
        "마이크로칩 프로그램을 저장·복사·붙여넣기할 수 있습니다."
    ),
    "text.little_big_redstone.floppy_disk_help_2": (
        "마이크로칩에서 %s + %s을(를) 눌러 디스크에 저장하세요."
    ),
    "text.little_big_redstone.floppy_disk_help_3": (
        "마이크로칩에 %s을(를) 사용해 프로그램을 설치하세요. 필요한 부품과 전선을 "
        "모두 인벤토리에 가지고 있어야 합니다."
    ),
    "text.little_big_redstone.floppy_disk_help_4": (
        "%s을(를) 사용해 로컬 파일로 프로그램을 저장하거나 불러오는 메뉴를 여세요."
    ),
    "text.little_big_redstone.floppy_disk_input_program_name": "프로그램 이름",
    "text.little_big_redstone.floppy_disk_more_items": "+%s",
    "text.little_big_redstone.floppy_disk_program_name": "프로그램: %s",
    "text.little_big_redstone.floppy_disk_save": (
        "마이크로칩 프로그램을 플로피 디스크에 저장했습니다."
    ),
    "text.little_big_redstone.guide_button_pause": "일시 정지",
    "text.little_big_redstone.guide_button_resume": "계속",
    "text.little_big_redstone.guide_tooltip_input_a": "입력 A",
    "text.little_big_redstone.guide_tooltip_input_b": "입력 B",
    "text.little_big_redstone.guide_tooltip_output": "출력",
    "text.little_big_redstone.indefinite": "무기한",
    "text.little_big_redstone.input": "입력",
    "text.little_big_redstone.logic_array_help_1": (
        "모든 레드스톤 비트와 논리 부품을 보관합니다!"
    ),
    "text.little_big_redstone.logic_array_help_2": (
        "마이크로칩 메뉴에서도 열 수 있습니다."
    ),
    "text.little_big_redstone.logic_array_help_3": ("들고 %s을(를) 사용해 여세요."),
    "text.little_big_redstone.logic_array_help_4": (
        "인벤토리에 있는 동안 %s을(를) 사용해 아이템을 넣고 뺄 수 있습니다."
    ),
    "text.little_big_redstone.logic_comparison_mode_equal_to": "=",
    "text.little_big_redstone.logic_comparison_mode_greater_than_or_equal_to": "≥",
    "text.little_big_redstone.logic_comparison_mode_less_than_or_equal_to": "≤",
    "text.little_big_redstone.logic_config_button_label_cancel": "취소",
    "text.little_big_redstone.logic_config_button_label_chance": "확률: ",
    "text.little_big_redstone.logic_config_button_label_comparator_output_override": (
        "출력 재정의: "
    ),
    "text.little_big_redstone.logic_config_button_label_direction": "방향",
    "text.little_big_redstone.logic_config_button_label_duration": "지속 시간: ",
    "text.little_big_redstone.logic_config_button_label_inputs": "입력: ",
    "text.little_big_redstone.logic_config_button_label_io_signal_strength": (
        "신호 세기: "
    ),
    "text.little_big_redstone.logic_config_button_label_mode": "모드",
    "text.little_big_redstone.logic_config_button_label_output_power": "전력",
    "text.little_big_redstone.logic_config_button_label_outputs": "출력: ",
    "text.little_big_redstone.logic_config_button_label_pass_signal": "신호 통과",
    "text.little_big_redstone.logic_config_button_label_reader_fill_threshold": (
        "채움 임계값: "
    ),
    "text.little_big_redstone.logic_config_button_label_reader_signal_threshold": (
        "신호 임계값: "
    ),
    "text.little_big_redstone.logic_config_button_label_save": "저장",
    "text.little_big_redstone.logic_config_button_label_sequencer_auto_reset": (
        "자동 초기화"
    ),
    "text.little_big_redstone.logic_config_button_label_sequencer_delay": "지연: ",
    "text.little_big_redstone.logic_config_button_label_sequencer_reset_port": (
        "초기화 포트"
    ),
    "text.little_big_redstone.logic_config_button_label_tag_global": "전역",
    "text.little_big_redstone.logic_config_button_label_tag_label": "레이블: ",
    "text.little_big_redstone.logic_config_button_label_tag_threshold": "임계값: ",
    "text.little_big_redstone.logic_config_button_label_ticks_and_seconds": (
        "%s틱 (%s초)"
    ),
    "text.little_big_redstone.logic_config_button_label_ticks_and_seconds_singular": (
        "%s틱 (%s초)"
    ),
    "text.little_big_redstone.logic_config_button_tooltip_calculator_mode": (
        "이 부품이 입력 신호 세기에 수행할 수학 연산입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_all_pass_signal_comparison_mode_equal_to": (
        "모든 입력 신호가 첫 번째 입력 신호와 같아야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_all_pass_signal_comparison_mode_greater_than_or_equal_to": (
        "모든 입력 신호가 첫 번째 입력 신호 이상이어야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_all_pass_signal_comparison_mode_less_than_or_equal_to": (
        "모든 입력 신호가 첫 번째 입력 신호 이하여야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_all_signal_comparison_mode_equal_to": (
        "모든 입력 신호가 %s와(과) 같아야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_all_signal_comparison_mode_greater_than_or_equal_to": (
        "모든 입력 신호가 %s 이상이어야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_all_signal_comparison_mode_less_than_or_equal_to": (
        "모든 입력 신호가 %s 이하여야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_any_pass_signal_comparison_mode_equal_to": (
        "입력 신호 중 하나 이상이 첫 번째 입력 신호와 같아야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_any_pass_signal_comparison_mode_greater_than_or_equal_to": (
        "입력 신호 중 하나 이상이 첫 번째 입력 신호 이상이어야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_any_pass_signal_comparison_mode_less_than_or_equal_to": (
        "입력 신호 중 하나 이상이 첫 번째 입력 신호 이하여야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_any_signal_comparison_mode_equal_to": (
        "입력 신호 중 하나 이상이 %s와(과) 같아야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_any_signal_comparison_mode_greater_than_or_equal_to": (
        "입력 신호 중 하나 이상이 %s 이상이어야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_any_signal_comparison_mode_less_than_or_equal_to": (
        "입력 신호 중 하나 이상이 %s 이하여야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_mode": (
        "하나 이상의 입력 또는 모든 입력이 신호 세기 비교와 일치해야 출력을 켤지 설정합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_comparator_output_override": (
        "비교기가 입력과 일치할 때 내보낼 출력 신호입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_duration": (
        "출력이 켜져 있는 시간입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_inputs": (
        "이 부품이 받을 수 있는 입력 수입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_io_direction": (
        "이 포트가 레드스톤 전력과 상호작용할 방향입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_io_mode": (
        "이 포트로 레드스톤 전력을 입력할지 출력할지 설정합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_io_signal_comparison_mode_equal_to": (
        "입력 신호가 %s와(과) 같아야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_io_signal_comparison_mode_greater_than_or_equal_to": (
        "입력 신호가 %s 이상이어야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_io_signal_comparison_mode_less_than_or_equal_to": (
        "입력 신호가 %s 이하여야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_io_signal_comparison_output": (
        "출력 신호는 %s와(과) 같습니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_io_signal_comparison_output_pass": (
        "출력 신호는 포트에 전력을 공급하는 전선의 신호 세기와 같습니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_io_signal_strength_input": (
        "출력을 켜는 데 필요한 레드스톤 신호 세기입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_io_signal_strength_output": (
        "내보낼 레드스톤 신호 세기입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_output_power_strong": (
        "출력이 켜지면 이 출력의 블록에 강한 전력이 공급됩니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_output_power_weak": (
        "출력이 켜지면 이 출력의 블록에 약한 전력이 공급됩니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_outputs": (
        "이 부품이 내보낼 수 있는 출력 수입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_pass_signal": (
        "선택기가 입력 세기를 출력으로 그대로 보낼지, 출력 신호를 출력 포트의 "
        "번호(1부터 시작)로 정할지 설정합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_randomizer_chance": (
        "입력이 켜진 동안 각 틱에 출력 하나가 켜질 확률입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_reader_direction": (
        "판독기가 블록의 저장량을 읽을 방향입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_reader_fill_threshold": (
        "출력을 켜는 데 필요한 컨테이너의 채움량 또는 채움 비율입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_reader_mode": (
        "인접한 블록에서 읽을 정보의 종류입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_reader_signal_comparison_mode_equal_to": (
        "입력 신호가 %s와(과) 같아야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_reader_signal_comparison_mode_greater_than_or_equal_to": (
        "입력 신호가 %s 이상이어야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_reader_signal_comparison_mode_less_than_or_equal_to": (
        "입력 신호가 %s 이하여야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_reader_signal_threshold": (
        "출력을 켜는 데 필요한 비교기 기준 입력 신호입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_reader_threshold_comparison_mode_equal_to": (
        "컨테이너 내용물이 %s와(과) 같아야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_reader_threshold_comparison_mode_greater_than_or_equal_to": (
        "컨테이너 내용물이 %s 이상이어야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_reader_threshold_comparison_mode_less_than_or_equal_to": (
        "컨테이너 내용물이 %s 이하여야 합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_selector_mode_counter": (
        "첫 번째 입력이 켜지면 선택한 출력이 위로 이동하고, 두 번째 입력이 켜지면 "
        "아래로 이동합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_selector_mode_setter": (
        "켜진 입력에 대응하는 출력 중 번호가 가장 낮은 출력이 켜집니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_sequencer_auto_reset": (
        "시퀀서가 출력을 켠 직후 진행도를 자동으로 초기화할지 설정합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_sequencer_delay": (
        "출력이 켜지기 전까지 기다릴 시간입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_sequencer_mode_counter": (
        "입력이 켜진 동안 시퀀서가 X틱까지 증가한 뒤 출력을 켭니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_sequencer_mode_strong": (
        "입력이 켜진 동안 시퀀서가 X틱까지 증가한 뒤 출력을 켭니다. 입력이 꺼지면 "
        "시퀀서가 감소합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_sequencer_mode_weak": (
        "입력 신호가 켜지면 시퀀서가 X틱을 기다린 뒤 출력을 켭니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_sequencer_reset_port": (
        "시퀀서의 진행도를 강제로 초기화하는 두 번째 전선 포트를 추가할지 설정합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_tag_global": (
        "태그 감지기가 자신이 설치한 마이크로칩의 송신기만 감지할지, 다른 사람이 설치한 "
        "송신기도 감지할지 설정합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_tag_label": (
        "이 태그가 송신하거나 감지할 레이블입니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_tag_mode": (
        "이 태그가 신호를 감지할지 송신할지 설정합니다."
    ),
    "text.little_big_redstone.logic_config_button_tooltip_tag_threshold": (
        "출력을 켜기 위해 이 감지기가 감지해야 하는 태그 송신기 수입니다."
    ),
    "text.little_big_redstone.logic_config_calculator_mode_addition": "덧셈",
    "text.little_big_redstone.logic_config_calculator_mode_subtraction": "뺄셈",
    "text.little_big_redstone.logic_config_selector_mode_counter": "카운터",
    "text.little_big_redstone.logic_config_selector_mode_setter": "설정기",
    "text.little_big_redstone.logic_config_sequencer_mode_counter": "카운터",
    "text.little_big_redstone.logic_config_sequencer_mode_strong": "강함",
    "text.little_big_redstone.logic_config_sequencer_mode_weak": "약함",
    "text.little_big_redstone.logic_config_tooltip": "설정:",
    "text.little_big_redstone.logic_config_tooltip_chance": "  확률: %s",
    "text.little_big_redstone.logic_config_tooltip_click_to_open": (
        "마우스 오른쪽 버튼으로 설정을 편집하세요."
    ),
    "text.little_big_redstone.logic_config_tooltip_comparator_output_override": (
        "  출력 재정의: %s"
    ),
    "text.little_big_redstone.logic_config_tooltip_direction": "  방향: %s",
    "text.little_big_redstone.logic_config_tooltip_duration": "  지속 시간: %s",
    "text.little_big_redstone.logic_config_tooltip_global": "  전역: %s",
    "text.little_big_redstone.logic_config_tooltip_inputs": "  입력: %s",
    "text.little_big_redstone.logic_config_tooltip_io_power_output": "  전력: %s",
    "text.little_big_redstone.logic_config_tooltip_label": "  레이블: %s",
    "text.little_big_redstone.logic_config_tooltip_mode": "  모드: %s",
    "text.little_big_redstone.logic_config_tooltip_outputs": "  출력: %s",
    "text.little_big_redstone.logic_config_tooltip_pass_signal": "  신호 통과: %s",
    "text.little_big_redstone.logic_config_tooltip_reader_fill_comparison": (
        "  채움: %s %s"
    ),
    "text.little_big_redstone.logic_config_tooltip_reader_signal_comparison": (
        "  신호: %s %s"
    ),
    "text.little_big_redstone.logic_config_tooltip_sequencer_auto_reset": (
        "  자동 초기화: %s"
    ),
    "text.little_big_redstone.logic_config_tooltip_sequencer_delay": "  지연: %s",
    "text.little_big_redstone.logic_config_tooltip_sequencer_reset_port": (
        "  초기화 포트: %s"
    ),
    "text.little_big_redstone.logic_config_tooltip_signal": "  신호: %s",
    "text.little_big_redstone.logic_config_tooltip_signal_comparison": (
        "  신호: %s %s"
    ),
    "text.little_big_redstone.logic_config_tooltip_threshold": "  임계값: %s",
    "text.little_big_redstone.logic_gate_algebra": "Q = %s",
    "text.little_big_redstone.logic_gate_algebra_and": "A ∧ B",
    "text.little_big_redstone.logic_gate_algebra_nand": "A ↑ B",
    "text.little_big_redstone.logic_gate_algebra_nor": "A ↓ B",
    "text.little_big_redstone.logic_gate_algebra_not": "¬A",
    "text.little_big_redstone.logic_gate_algebra_or": "A ∨ B",
    "text.little_big_redstone.logic_gate_algebra_xor": "A ⊻ B",
    "text.little_big_redstone.logic_help_and_gate": (
        "모든 입력이 켜지면 출력이 켜지고, 그렇지 않으면 꺼집니다."
    ),
    "text.little_big_redstone.logic_help_calculator_1": (
        "모드에 따라 입력 신호 세기 값을 더하거나 뺍니다."
    ),
    "text.little_big_redstone.logic_help_calculator_2": (
        "출력 신호 세기는 계산한 합계 값이 됩니다."
    ),
    "text.little_big_redstone.logic_help_comparator_1": (
        "모드에 따라 모든 입력 또는 하나 이상의 입력이 비교와 일치해야 합니다."
    ),
    "text.little_big_redstone.logic_help_comparator_2": (
        "출력이 켜지면 신호 세기는 출력 재정의 값과 같습니다. 출력 재정의를 통과로 "
        "설정하면 출력 신호 세기는 비교 대상의 세기와 같습니다."
    ),
    "text.little_big_redstone.logic_help_io_port_1": (
        "한 면에서 월드의 레드스톤 신호를 입력하거나 출력할 수 있습니다. I/O 포트를 "
        "여러 개 사용하면 서로 다른 면으로 신호를 입출력할 수 있습니다."
    ),
    "text.little_big_redstone.logic_help_io_port_2": (
        "마이크로칩의 같은 면에는 입력 포트와 출력 포트를 함께 둘 수 없습니다."
    ),
    "text.little_big_redstone.logic_help_nand_gate": (
        "모든 입력이 켜지면 출력이 꺼지고, 그렇지 않으면 켜집니다."
    ),
    "text.little_big_redstone.logic_help_nor_gate": (
        "모든 입력이 꺼지면 출력이 켜지고, 그렇지 않으면 꺼집니다."
    ),
    "text.little_big_redstone.logic_help_not_gate": (
        "입력이 꺼지면 출력이 켜지고, 입력이 켜지면 출력이 꺼집니다."
    ),
    "text.little_big_redstone.logic_help_or_gate": (
        "입력 하나라도 켜지면 출력이 켜지고, 그렇지 않으면 꺼집니다."
    ),
    "text.little_big_redstone.logic_help_pulse_throttler_1": (
        "입력 신호를 조절해 설정한 시간 동안 출력을 냅니다. 무기한으로 설정하면 입력이 "
        "켜져 있는 동안 출력도 켜집니다."
    ),
    "text.little_big_redstone.logic_help_pulse_throttler_2": (
        "출력 신호는 입력을 그대로 통과시키거나 특정 값으로 설정할 수 있습니다."
    ),
    "text.little_big_redstone.logic_help_randomizer": (
        "입력이 켜지면 설정한 확률에 따라 무작위 출력 하나가 켜집니다."
    ),
    "text.little_big_redstone.logic_help_reader_1": (
        "인접한 블록의 채움량을 확인하고, 설정한 채움 임계값 이상이면 신호를 켭니다."
    ),
    "text.little_big_redstone.logic_help_reader_2": (
        "아이템·유체·에너지 저장소에 사용할 수 있습니다."
    ),
    "text.little_big_redstone.logic_help_rs_nor_latch_1": (
        "초기화(R) 입력이 켜지면 출력은 항상 꺼집니다."
    ),
    "text.little_big_redstone.logic_help_rs_nor_latch_2": (
        "설정(S) 입력이 켜지고 초기화(R) 입력이 꺼지면 출력이 켜지며, 초기화(R) 입력이 "
        "켜질 때까지 켜진 상태를 유지합니다."
    ),
    "text.little_big_redstone.logic_help_selector": (
        "출력 하나를 켜고, 선택한 모드의 방식에 따라 인접한 포트로 전환합니다."
    ),
    "text.little_big_redstone.logic_help_sequencer_1": (
        "설정한 지연 시간만큼 출력 신호를 늦춥니다."
    ),
    "text.little_big_redstone.logic_help_sequencer_2": (
        "모드에 따라 시퀀서의 동작이 달라지며 약함, 강함 또는 카운터로 설정할 수 있습니다."
    ),
    "text.little_big_redstone.logic_help_sequencer_3": (
        "기본적으로 시퀀서는 출력을 낸 뒤 초기화되지 않습니다. 자동 초기화를 켜면 출력을 "
        "켠 직후 진행도가 초기화됩니다. 초기화 포트를 켜면 두 번째 입력 포트도 사용할 수 "
        "있습니다. 두 번째 입력 포트가 켜지면 시퀀서의 진행도가 초기화됩니다. 이 입력이 "
        "켜져 있는 동안에는 시퀀서가 진행되지 않습니다."
    ),
    "text.little_big_redstone.logic_help_t_flip_flop": (
        "입력이 꺼짐에서 켜짐으로 바뀌면 출력 신호의 상태가 전환됩니다."
    ),
    "text.little_big_redstone.logic_help_tag_1": (
        "모드에 따라 태그가 감지기 또는 송신기로 작동합니다."
    ),
    "text.little_big_redstone.logic_help_tag_2": (
        "같은 레이블을 사용하며 켜진 송신기를 임계값 이상 감지해야 감지기의 출력이 켜집니다."
    ),
    "text.little_big_redstone.logic_help_tag_3": (
        "태그 송신기는 차원을 무시하고 월드 전체로 신호를 보냅니다."
    ),
    "text.little_big_redstone.logic_help_xor_gate": (
        "켜진 입력 수가 홀수이면 출력이 켜지고, 그렇지 않으면 꺼집니다."
    ),
    "text.little_big_redstone.no": "아니요",
    "text.little_big_redstone.output": "출력",
    "text.little_big_redstone.pass": "통과",
    "text.little_big_redstone.power_type_strong": "강함",
    "text.little_big_redstone.power_type_weak": "약함",
    "text.little_big_redstone.sealed": "봉인됨",
    "text.little_big_redstone.sensor": "감지기",
    "text.little_big_redstone.sticky_note": "점착 메모지",
    "text.little_big_redstone.sticky_note_edit": "편집",
    "text.little_big_redstone.thermometer_complexity_high": "높음 (%s)",
    "text.little_big_redstone.thermometer_complexity_low": "낮음 (%s)",
    "text.little_big_redstone.thermometer_complexity_moderate": "보통 (%s)",
    "text.little_big_redstone.thermometer_complexity_very_high": "매우 높음 (%s)",
    "text.little_big_redstone.thermometer_tooltip_complexity": "  복잡도: %s",
    "text.little_big_redstone.thermometer_tooltip_header": "온도계",
    "text.little_big_redstone.thermometer_tooltip_loading_wires": (
        "전선을 불러오는 중입니다... 불러오는 동안에도 마이크로칩을 조작할 수 있습니다."
    ),
    "text.little_big_redstone.thermometer_tooltip_logic": "  논리: %s",
    "text.little_big_redstone.thermometer_tooltip_notes": "  메모: %s",
    "text.little_big_redstone.thermometer_tooltip_wires": "  전선: %s",
    "text.little_big_redstone.yes": "예",
}


def formatted_lines(*lines: str) -> str:
    """인게임 설명의 명시적 줄 구성을 그대로 만든다."""
    return "\n".join(lines)


REDSTONE_PEN = {
    "language": "한국어",
    "language.code": "ko_kr",
    "language.region": "대한민국",
    "itemGroup.tabredstonepen": "Redstone Pen",
    "redstonepen.tooltip.hint.extended": "§6[§9Shift§r 자세히§6]§r",
    "redstonepen.tooltip.hint.help": "§6[§9Ctrl+Shift§r 도움말§6]§r",
    "block.redstonepen.basic_button": "기본 버튼",
    "block.redstonepen.basic_button.help": "어디에나 잘 맞습니다. 아마도요.",
    "block.redstonepen.basic_gauge": "기본 레드스톤 게이지",
    "block.redstonepen.basic_gauge.help": (
        "받은 레드스톤 신호를 표시하는, 블록 전체를 차지하는 단순한 유리 게이지입니다. "
        "신호를 절연합니다."
    ),
    "block.redstonepen.basic_lever": "기본 레버",
    "block.redstonepen.basic_lever.help": "어디에나 잘 맞습니다. 아마도요.",
    "block.redstonepen.basic_pulse_button": "기본 펄스 버튼",
    "block.redstonepen.basic_pulse_button.help": "한 틱 동안 레드스톤 신호를 냅니다.",
    "block.redstonepen.bistable_relay": "쌍안정 레드스톤 릴레이",
    "block.redstonepen.bistable_relay.help": (
        "뒤와 옆에서 들어오는 신호를 출력 세기 15로 앞에 전달합니다. 상승 신호 에지"
        "(꺼짐에서 켜짐으로 바뀌는 펄스)를 감지할 때마다 켜짐과 꺼짐이 전환됩니다."
    ),
    "block.redstonepen.bridge_relay": "브리지 레드스톤 릴레이",
    "block.redstonepen.bridge_relay.help": (
        "뒤에서 들어오는 신호를 출력 세기 15로 앞에 전달합니다. 왼쪽에서 오른쪽으로 "
        "일반 레드스톤 신호를 통과시킵니다."
    ),
    "block.redstonepen.control_box": "레드스톤 논리 제어기",
    "block.redstonepen.control_box.error.expected_assignment": "대입식이 필요합니다",
    "block.redstonepen.control_box.error.invalid_character": "잘못된 문자입니다",
    "block.redstonepen.control_box.error.invalid_number_of_arguments": (
        "함수 인수 개수가 잘못되었습니다"
    ),
    "block.redstonepen.control_box.error.missing_closing_function_parenthesis": (
        "함수를 닫는 괄호 ')'가 필요합니다"
    ),
    "block.redstonepen.control_box.error.missing_closing_parenthesis": (
        "닫는 괄호 ')'가 필요합니다"
    ),
    "block.redstonepen.control_box.error.missing_function_arguments": (
        "괄호를 포함한 함수 인수가 필요합니다"
    ),
    "block.redstonepen.control_box.error.parse_error": "구문 분석 오류",
    "block.redstonepen.control_box.error.symbol_readonly": (
        "기호 또는 변수는 읽기 전용입니다"
    ),
    "block.redstonepen.control_box.error.unexpected_character": "예상하지 못한 문자입니다",
    "block.redstonepen.control_box.error.unknown_function": "알 수 없는 함수입니다",
    "block.redstonepen.control_box.help": "단순화된 PLC형 제어기입니다.",
    "block.redstonepen.control_box.help.1": formatted_lines(
        "§n기초:§r§7 RLC는 모든 방향으로 디지털(켜짐/꺼짐)과",
        "§7아날로그(신호 세기, 비교기 출력) 레드스톤 I/O를",
        "§7제공합니다. 포트는 빨강, 파랑, 노랑, 초록, 위,",
        "§7아래의 영어 첫 글자 R, B, Y, G, U, D를 사용합니다.",
        "§7수식 모음으로 프로그래밍합니다. 모든 코드 줄은",
        "§7같은 틱에 계산됩니다(입력 읽기 ->",
        "§7계산 -> 출력 쓰기). 코드는 대소문자를 구분하지 않으며",
        '§7("R"과 "r"은 같습니다). 사용자 변수를 설정할 수도 있고,',
        "§7그 값은 RLC가 멈출 때까지 유지됩니다.",
        "§7구문 오류는 표시되며(커서를 올려 확인) 프로그램을",
        "§7시작하지 못하게 합니다.",
        "",
        "§7RUN/STOP 버튼을 클릭해 프로그램을 시작하거나 멈추세요.",
        "§7RLC 기호에 커서를 올리면 내부 변수 값을 볼 수 있습니다",
        "§7(실행 중일 때만). 포트 목록에는 현재 신호 값과 포트가",
        "§7입력, 출력 또는 미사용 상태인지 표시됩니다.",
        "§7클립보드 복사/붙여넣기 버튼은 설명이 필요 없겠죠 ;)",
    ),
    "block.redstonepen.control_box.help.10": formatted_lines(
        "§n추가 정보:§r§7 제어기는 보통 4틱마다 계산합니다.",
        "§7입력 포트가 켜짐->꺼짐 또는 꺼짐->켜짐으로 바뀌면",
        "§7실행 주기를 가능한 다음 틱으로 다시 예약합니다.",
        '§7"TICKRATE" 변수에 값을 지정해 기본 틱 속도를',
        "§72틱에서 20틱 사이로 바꿀 수 있습니다.",
        "§7",
        "§7비교기 입력은 이 재예약을 일으키지 않습니다.",
    ),
    "block.redstonepen.control_box.help.2": formatted_lines(
        '§n수식§r§7은 "RESULT=TERM" 형태의 대입식으로 작성합니다.',
        '§7예: "R = G & B". 모든 코드 줄은 이 형식이어야 합니다.',
        '§7"#" 뒤의 내용은 그 줄의 주석으로 처리됩니다.',
        '§7TERM에는 괄호 "(...)"와 포트, 변수, 연산자,',
        "§7함수를 사용할 수 있습니다.",
        "",
        "§7포트 변수(R, B, Y, G, U, D)에 값을 대입하면",
        "§7자동으로 출력 포트가 되며",
        "§7그 포트의 입력 신호 변화는 무시됩니다.",
        "§7아직 출력이 아닌 포트 변수를 수식에 사용하면 자동으로",
        "§7입력 포트가 됩니다.",
        "§7인접 블록의 비교기 출력은",
        '§7".CO" 접미사로 읽습니다. 예: "Y = MAX( B.CO, R, g.co, MyVar )".',
        "§7CO는 값을 대입해도 RLC 출력이 되지 않습니다.",
    ),
    "block.redstonepen.control_box.help.3": formatted_lines(
        "§n산술 연산:§r§7 RLC는 정수 산술을 사용하므로",
        '§7"A * 1.5"는 사용할 수 없고 나눗셈은 영 쪽으로',
        "§7반올림됩니다. 지원하는 연산은 다음과 같습니다:",
        "",
        '§7  "+", "-", "*", "/", "%"(%는 나머지 연산).',
        "",
        "§7변수에는 양수 또는 음수 32비트 정수 값을",
        "§7저장할 수 있습니다(필요한 범위보다 큽니다).",
        "§7포트 값은 자동으로 유효한 레드스톤 값 범위인",
        "§70..15로 제한됩니다.",
        "§7Int32 오버플로가 적용되며 영으로 나누면",
        "§70과 던전 차원으로 가는 특이점이 생깁니다.",
    ),
    "block.redstonepen.control_box.help.4": formatted_lines(
        "§n관계 연산자:§r§7 숫자를 비교합니다:",
        "§7",
        '§7  "=="(같음), "!="(다름),',
        '§7  ">="(크거나 같음), "<="(작거나 같음),',
        '§7  ">"(큼), "<"(작음).',
        "§7",
        "§7비교 결과가 거짓이면 0, 참이면 15가 됩니다.",
        "§7결과도 숫자이므로 바로 계산에 사용할 수 있습니다.",
        '§7예: "G=(R>11)/3"의 결과는 5 또는 0입니다.',
        "§7하지만 IF 함수를 사용하는 편이 좋습니다:",
        '§7"G = IF( R>11, 5, 0 )".',
    ),
    "block.redstonepen.control_box.help.5": formatted_lines(
        '§n논리 연산:§r§7 "레드스톤 불리언" 값을 사용합니다.',
        "§7피연산자는 정수이며 0보다 크면 참으로 간주합니다.",
        "§7연산 결과는 거짓일 때 0, 참일 때 15입니다.",
        "§7지원하는 연산은 다음과 같습니다:",
        "§7",
        '§7 AND: "AND", "&&", "&"',
        '§7 OR: "OR", "||", "|"',
        '§7 XOR: "XOR", "^"',
        '§7 NOT: "NOT", "!"',
        "§7",
        "§7간단히 말해 연산자는 입력을 레드스톤 램프처럼 보고",
        "§7출력을 레버처럼 냅니다. 프로그래머 참고: 비트 단위",
        "§7연산은 없습니다.",
    ),
    "block.redstonepen.control_box.help.6": formatted_lines(
        "§n에지 감지:§r§7 입력이 꺼짐[0]에서 켜짐[>0]으로 또는",
        "§7그 반대로 바뀌는 순간을 추적합니다.",
        '§7상승 에지 트리거는 ".RE" 접미사로 설정하며, 입력이',
        "§7꺼짐에서 켜짐으로 바뀔 때 한 틱 동안 15가 됩니다.",
        '§7하강 에지 트리거는 ".FE" 접미사로 설정하며, 입력이',
        "§7켜짐에서 꺼짐으로 바뀔 때 한 틱 동안 15가 됩니다.",
        "§7예:",
        "§7",
        "§7 C = C+IF(R.RE OR G.FE OR Y.CO.RE, 1, 0) # C 증가",
        "§7 C = CNT1(G.RE, B.RE, 10) # 업다운 카운터1 사용",
        "§7",
        "§7참고: RLC가 매 틱 실행되지 않아도 입력 포트의 에지는",
        '§7계속 감지됩니다("인터럽트"). PLC에서는 이를 RTRIG와',
        "§7FTRIG라고 합니다.",
    ),
    "block.redstonepen.control_box.help.7": formatted_lines(
        "§n타이머:§r§7 PLC의 타이머는 신호를 기반으로 합니다. 주요",
        "§7세 종류인 TON, TOF, TP가 RLC에 구현되어 있습니다:",
        "§7TON은 켜짐 지연입니다. 입력 신호가 지정한 시간 동안",
        "§7계속 켜져 있어야 타이머 출력이 켜집니다.",
        "§7입력이 꺼지면 타이머는 즉시 초기화됩니다. TOF는",
        "§7반대인 꺼짐 지연입니다. TP는 입력의 상승 에지를",
        "§7감지하면 지정한 시간 동안 펄스를 만듭니다.",
        "§7펄스 도중의 신호 변화는 무시됩니다.",
        "§7RLC에는 각 종류의 단순화된 인스턴스가 5개씩 있습니다:",
        "§7",
        "§7 A = TON3( INPUT_TERM, ON_DELAY_TICKS )",
        "§7 A = TOF2( INPUT_TERM, OFF_DELAY_TICKS )",
        "§7 A = TP4( INPUT_TERM, PULSE_TIME_TICKS )",
        "§7 R = TON1( Y.CO<3, 30*20 ) # 30초 후 호퍼 부족 경보",
        "§7 R = TP1( Y.RE, 20 ) # 관찰자 펄스를 1초로 연장",
        "",
        "§7타이머가 작동 중일 때도 타이머 설정(PT)을",
        "§7바꿀 수 있습니다.",
    ),
    "block.redstonepen.control_box.help.8": formatted_lines(
        "§n카운터:§r§7 이벤트 발생 횟수를 추적합니다. RLC에는 선택적",
        "§7업다운 카운터 CNT1..5가 있으며 선택적 입력 인수를",
        "§7받습니다:",
        "§7",
        "§7N = CNTx(Iup)   # Iup이 >0이면 증가",
        "§7N = CNTx(Iup, Idown)   # Idown>0이면 0으로 감소",
        "§7N = CNTx(Iup, Idown, Max)   # 0..Max 범위",
        "§7N = CNTx(Iup, Idown, Min, Max)   # Min..Max 범위",
        "§7N = CNTx(Iup, Idown, Min, Max, Reset) # Min으로 초기화",
        "§7",
        "§7N에는 새 카운터 값이 저장됩니다. 참고: 이벤트를 셀 때는",
        "§7신호 에지(예: G.RE)를 입력으로 사용하세요. 카운터는 틱",
        "§7시간 정확도를 보장하지 않습니다(시간 측정은 타이머 사용).",
    ),
    "block.redstonepen.control_box.help.9": formatted_lines(
        "§n함수 참고:§r",
        "§7IF(X,A,B)   # X>0이면 A, 아니면 B",
        "§7INV(X)   # 레드스톤 반전: 15-X, 결과 0..15.",
        "§7MAX(A,B,...), MIN(...), MEAN(...) # 최솟값, 최댓값, 평균",
        "§7LIM(X), LIM(X,B), LIM(X,A,B) # 0..15, 0..B, A..B로 제한",
        "§7TIME(), CLOCK()    # 낮 시간, 게임 시간",
        "§7RND()   # 0..15의 무작위 값",
        "§7",
        "§7§nRLC 전용 함수 블록§r",
        "§7",
        "§7TIVx(T) # T틱마다 펄스(TIV1/TIV2/TIV3)§r",
        "§7TIVx(T, EN) # EN이 설정되면 T틱마다 펄스",
        "§7# (최소 간격은 3틱입니다).",
    ),
    "block.redstonepen.control_box.tooltips.copyall": "코드를 클립보드에 복사",
    "block.redstonepen.control_box.tooltips.pasteall": ("클립보드의 코드를 붙여넣기"),
    "block.redstonepen.control_box.tooltips.rcaplayer": ("플레이어 %1$s에게 RCA 연결"),
    "block.redstonepen.control_box.tooltips.runstop": "RUN/STOP",
    "block.redstonepen.inverted_relay": "반전 레드스톤 릴레이",
    "block.redstonepen.inverted_relay.help": formatted_lines(
        "뒤와 옆에서 들어오는 신호를 출력 세기 15로 앞에 전달합니다. 출력은 반전됩니다"
        "(입력 신호가 있으면 0, 없으면 15). 꺼짐 지연은 레드스톤 한 틱이며 즉시 켜집니다.",
        "트랙을 통해 들어오는 간접 전력도 받습니다(레드스톤 신호를 전달하는 블록에 연결).",
    ),
    "block.redstonepen.pulse_relay": "펄스 레드스톤 릴레이",
    "block.redstonepen.pulse_relay.help": (
        "상승 신호 에지(꺼짐에서 켜짐으로 바뀌는 펄스)를 감지하면 출력에서 짧은 펄스를 "
        "냅니다. 펄스 길이는 레드스톤 1틱입니다."
    ),
    "block.redstonepen.relay": "레드스톤 릴레이",
    "block.redstonepen.relay.help": formatted_lines(
        "뒤와 옆에서 들어오는 신호를 출력 세기 15로 앞에 전달합니다. 즉시 켜지며 꺼짐 "
        "지연은 레드스톤 한 틱입니다.",
        "트랙을 통해 들어오는 간접 전력도 받습니다(레드스톤 신호를 전달하는 블록에 연결).",
    ),
    "block.redstonepen.track": "레드스톤 트랙",
    "item.redstonepen.pen": "레드스톤 펜",
    "item.redstonepen.pen.help": formatted_lines(
        "모든 방향으로 가느다란 레드스톤 트랙을 그리거나 지우는 충전식 펜입니다."
        "\n우클릭=설치, 좌클릭=제거, 웅크리기: 중앙 연결부 허용."
        "\n트랙은 보통 설치된 블록에 §l전력을 공급하지 않습니다§r(트랙 중앙을 클릭해 "
        "연결부를 직접 설치하거나 제거). 블록을 보며 웅크리면 현재 레드스톤 신호를 "
        "볼 수 있습니다. 제작 인벤토리에서 레드스톤으로 수리하세요."
        "\n블록 하나의 연결되지 않은 면에 트랙이 너무 많으면 신호 간섭으로 작동하지 않으니 "
        "경로를 바꾸세요."
    ),
    "item.redstonepen.pen.tooltip.numstored": "레드스톤 %1$s개 저장됨",
    "item.redstonepen.pen.tooltip.rsfrominventory": "인벤토리의 레드스톤 사용",
    "item.redstonepen.quill": "레드스톤 깃펜",
    "item.redstonepen.quill.help": formatted_lines(
        "모든 방향으로 가느다란 레드스톤 트랙을 그리거나 지웁니다. 트랙은 보통 설치된 "
        "블록에 §l전력을 공급하지 않습니다§r(트랙 중앙을 클릭해 연결부를 직접 설치하거나 "
        "제거). 블록을 보며 웅크리면 현재 레드스톤 신호를 볼 수 있습니다."
        "\n블록 하나의 연결되지 않은 면에 트랙이 너무 많으면 신호 간섭으로 작동하지 않으니 "
        "경로를 바꾸세요."
    ),
    "item.redstonepen.remote": "레드스톤 리모컨",
    "item.redstonepen.remote.help": (
        "버튼과 레버를 작동하거나 전환합니다. 블록을 좌클릭해 위치를 저장한 뒤 리모컨으로 "
        "작동하세요. 해당 블록의 청크가 불러와져 있어야 하며 차원 간에는 작동하지 않습니다."
    ),
    "item.redstonepen.remote.tooltip.linkedto": "%4$s [%1$s,%2$s,%3$s]에 연결됨",
    "item.redstonepen.remote.tooltip.notlinked": (
        "§o§7연결되지 않음. 버튼이나 레버를 좌클릭해 연결하세요."
    ),
    "advancement.redstonepen.craft_redstonepen": "모든 것을 그리는 단 하나의 펜",
    "advancement.redstonepen.craft_redstonepen.desc": "레드스톤 펜 제작하기",
    "redstonepen.overlay.comparator_compare": " 비교",
    "redstonepen.overlay.comparator_subtract": " 감산",
    "redstonepen.overlay.direct_power": "[%1$s]",
    "redstonepen.overlay.direct_power_at": "[%1$s] @ %2$s",
    "redstonepen.overlay.indirect_power": "(%1$s) @ %2$s",
    "redstonepen.overlay.remote_saved": "연결 저장됨: %4$s [%1$s, %2$s, %3$s]",
    "redstonepen.overlay.repeater_delay": " %1$s틱",
    "redstonepen.overlay.track_power": "<%1$s>",
    "redstonepen.overlay.wire_power": "<%1$s>",
}

NAMESPACES = {
    "little_big_redstone": {
        "jar_pattern": "little-big-redstone-*.jar",
        "translations": None,
    },
    "redstonepen": {
        "jar_pattern": "redstonepen-*.jar",
        "translations": REDSTONE_PEN,
    },
}

INTENTIONAL_SAME = {
    "little_big_redstone": {
        "itemGroup.little_big_redstone.little_big_redstone",
        "key.categories.little_big_redstone.little_big_redstone",
        "text.little_big_redstone.count_and_percentage",
        "text.little_big_redstone.floppy_disk_more_items",
        "text.little_big_redstone.logic_comparison_mode_equal_to",
        "text.little_big_redstone.logic_comparison_mode_greater_than_or_equal_to",
        "text.little_big_redstone.logic_comparison_mode_less_than_or_equal_to",
        "text.little_big_redstone.logic_gate_algebra",
        "text.little_big_redstone.logic_gate_algebra_and",
        "text.little_big_redstone.logic_gate_algebra_nand",
        "text.little_big_redstone.logic_gate_algebra_nor",
        "text.little_big_redstone.logic_gate_algebra_not",
        "text.little_big_redstone.logic_gate_algebra_or",
        "text.little_big_redstone.logic_gate_algebra_xor",
    },
    "redstonepen": {
        "block.redstonepen.control_box.tooltips.runstop",
        "itemGroup.tabredstonepen",
        "redstonepen.overlay.direct_power",
        "redstonepen.overlay.direct_power_at",
        "redstonepen.overlay.indirect_power",
        "redstonepen.overlay.track_power",
        "redstonepen.overlay.wire_power",
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
    """서식 코드의 색상 숫자를 제외한 실제 표시 숫자만 찾는다."""
    return NUMBER.findall(FORMAT_CODE.sub("", value))


def source_jar(instance: Path, pattern: str) -> Path:
    """현재 설치본에서 패턴에 맞는 JAR 하나를 찾는다."""
    jars = sorted((instance / "mods").glob(pattern))
    if len(jars) != 1:
        raise RuntimeError(
            f"대상 JAR 수가 1개가 아닙니다: {[path.name for path in jars]}"
        )
    return jars[0]


def read_jar_language(jar: Path, namespace: str) -> dict[str, object]:
    """현재 JAR의 영어 언어 파일을 읽는다."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read(f"assets/{namespace}/lang/en_us.json"))
    if not isinstance(value, dict):
        raise TypeError(f"JAR 영어 언어 파일이 객체가 아닙니다: {jar}")
    return value


def little_translations() -> dict[str, str]:
    """색상별 항목과 개별 검수값을 합쳐 Little Big Redstone 번역표를 만든다."""
    translations = {}
    for identifier, color in COLORS.items():
        translations[f"block.little_big_redstone.{identifier}_microchip"] = (
            f"{color} 마이크로칩"
        )
        translations[f"item.little_big_redstone.{identifier}_floppy_disk"] = (
            f"{color} 플로피 디스크"
        )
        translations[f"item.little_big_redstone.{identifier}_logic_array"] = (
            f"{color} 논리 배열"
        )
        translations[f"item.little_big_redstone.{identifier}_sticky_note"] = (
            f"{color} 점착 메모지"
        )
    translations.update(
        {
            f"item.little_big_redstone.{key}": value
            for key, value in LITTLE_ITEMS.items()
        }
    )
    translations.update(LITTLE_TEXT)
    return translations


def translations_for(namespace: str) -> dict[str, str]:
    """네임스페이스별 검수 번역표를 반환한다."""
    if namespace == "little_big_redstone":
        return little_translations()
    return REDSTONE_PEN


def prepare() -> dict[str, object]:
    """현재 두 JAR의 영어와 후보 출처를 작업본에 기록한다."""
    instance = resolve_source_root()
    rows = []
    for namespace, config in NAMESPACES.items():
        jar = source_jar(instance, str(config["jar_pattern"]))
        english = read_jar_language(jar, namespace)
        with ZipFile(jar) as archive:
            bundled_korean = f"assets/{namespace}/lang/ko_kr.json" in archive.namelist()
        write_json(WORK_ROOT / namespace / "en_us.json", english)
        write_json(
            WORK_ROOT / namespace / "candidate_sources.json",
            {key: "manual_current_en_us" for key in english},
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
        "existing_korean_reused": 0,
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", report)
    return report


def build() -> dict[str, object]:
    """현재 영어 키 순서대로 두 한국어 언어 파일을 만든다."""
    counts = {}
    for namespace in NAMESPACES:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        translations = translations_for(namespace)
        missing = sorted(set(english) - set(translations))
        extra = sorted(set(translations) - set(english))
        if missing or extra:
            raise KeyError(f"{namespace} 번역표 불일치: 누락={missing}, 초과={extra}")
        korean = {key: translations[key] for key in english}
        write_json(WORK_ROOT / namespace / "ko_kr.json", korean)
        write_json(RESOURCEPACK_ROOT / namespace / "lang/ko_kr.json", korean)
        counts[namespace] = len(korean)
    report = {
        "reviewed_keys": sum(counts.values()),
        "namespace_keys": counts,
        "existing_korean_reused": 0,
        "new_translation_keys": sum(counts.values()),
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def scan_instance_references(instance: Path) -> tuple[list[str], list[str]]:
    """관련 FTB Quests와 KubeJS 직접 참조를 찾는다."""
    patterns = ("little_big_redstone", "little-big-redstone", "redstonepen")
    references = []
    errors = []
    for relative in ("config/ftbquests", "kubejs"):
        root = instance / relative
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            if path.suffix.lower() not in {".json", ".snbt", ".js", ".txt", ".toml"}:
                continue
            try:
                lines = path.read_text(encoding="utf-8-sig").splitlines()
            except UnicodeDecodeError as exc:
                errors.append(f"{path.relative_to(instance).as_posix()}: {exc}")
                continue
            for number, line in enumerate(lines, 1):
                if any(pattern in line.lower() for pattern in patterns):
                    references.append(
                        f"{path.relative_to(instance).as_posix()}:{number}:{line.strip()}"
                    )
    return references, errors


def audit() -> tuple[dict[str, object], list[str]]:
    """인게임 가이드·발전 과제와 관련 퀘스트·KubeJS 표시 경로를 감사한다."""
    instance = resolve_source_root()
    little = source_jar(instance, str(NAMESPACES["little_big_redstone"]["jar_pattern"]))
    pen = source_jar(instance, str(NAMESPACES["redstonepen"]["jar_pattern"]))
    errors = []
    with ZipFile(little) as archive:
        guide_classes = sorted(
            name
            for name in archive.namelist()
            if "guide" in name.lower() and name.endswith(".class")
        )
        class_data = b"".join(
            archive.read(name) for name in archive.namelist() if name.endswith(".class")
        )
        referenced_language_keys = sorted(
            {
                match.decode("ascii")
                for match in re.findall(
                    rb"text\.little_big_redstone\.[a-z0-9_.]+", class_data
                )
            }
        )
        dynamic_translation_api = (
            b"net/swedz/little_big_redstone/LBRText" in class_data
            and b"translate" in class_data
        )
    guide_keys = sorted(key for key in LITTLE_TEXT if ".logic_help_" in key)
    if not dynamic_translation_api:
        errors.append("Little Big Redstone의 동적 번역 API 사용을 확인하지 못했습니다")

    advancement_files = []
    direct_advancement_text = []
    with ZipFile(pen) as archive:
        for name in sorted(
            item
            for item in archive.namelist()
            if "/advancements/" in item and item.endswith(".json")
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
        errors.append(f"발전 과제에 직접 영문이 있습니다: {direct_advancement_text}")

    references, read_errors = scan_instance_references(instance)
    errors.extend(read_errors)
    if references:
        errors.append(f"관련 FTB Quests·KubeJS 직접 참조가 있습니다: {references}")
    report = {
        "family": FAMILY,
        "little_big_redstone": {
            "guide_classes": guide_classes,
            "language_keys_referenced_by_classes": len(referenced_language_keys),
            "dynamic_translation_api": dynamic_translation_api,
            "guide_help_keys": len(guide_keys),
            "guide_help_keys_fully_translated": all(
                key in little_translations() for key in guide_keys
            ),
        },
        "redstonepen": {
            "advancement_files": advancement_files,
            "direct_advancement_text": direct_advancement_text,
        },
        "ftbquests_kubejs_references": references,
        "read_errors": read_errors,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """현재 JAR·작업본·산출물과 문자열 보존 규칙을 검증한다."""
    instance = resolve_source_root()
    audit_report = load_json(WORK_ROOT / "surface_audit.json")
    errors = []
    namespace_reports = []
    total_keys = 0
    for namespace, config in NAMESPACES.items():
        jar = source_jar(instance, str(config["jar_pattern"]))
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
            for label, pattern in (
                ("자리표시자", PLACEHOLDER),
                ("서식 코드", FORMAT_CODE),
                ("숫자", None),
            ):
                source_tokens = (
                    numeric_tokens(source)
                    if pattern is None
                    else pattern.findall(source)
                )
                target_tokens = (
                    numeric_tokens(target)
                    if pattern is None
                    else pattern.findall(target)
                )
                if Counter(source_tokens) != Counter(target_tokens):
                    current_errors.append(f"{label} 불일치: {key}")
            if source.count("\n") != target.count("\n"):
                current_errors.append(f"줄바꿈 불일치: {key}")
            if source == target and key not in INTENTIONAL_SAME[namespace]:
                untranslated.append(key)
            if not key.startswith(CODE_HEAVY_PREFIX):
                residue = sorted(set(LATIN_WORD.findall(target)) - ALLOWED_LATIN)
                if residue:
                    latin_residue[key] = residue
        collisions = defaultdict(list)
        for key, target in korean.items():
            if isinstance(target, str):
                collisions[target].append(key)
        allowed_collision = {
            frozenset(
                {
                    "text.little_big_redstone.logic_config_button_label_ticks_and_seconds",
                    "text.little_big_redstone.logic_config_button_label_ticks_and_seconds_singular",
                }
            )
        }
        unexpected_collisions = {
            target: keys
            for target, keys in collisions.items()
            if len(keys) > 1
            and len({english[key] for key in keys}) > 1
            and frozenset(keys) not in allowed_collision
        }
        if untranslated:
            current_errors.append(f"영어와 같은 미번역 후보: {untranslated}")
        if latin_residue:
            current_errors.append(f"허용하지 않은 영문 잔여: {latin_residue}")
        if unexpected_collisions:
            current_errors.append(
                f"서로 다른 영어의 한국어 충돌: {unexpected_collisions}"
            )
        namespace_reports.append(
            {
                "namespace": namespace,
                "keys": len(english),
                "untranslated_candidates": untranslated,
                "latin_residue": latin_residue,
                "unexpected_name_collisions": unexpected_collisions,
                "errors": current_errors,
            }
        )
        total_keys += len(english)
        errors.extend(f"{namespace}: {message}" for message in current_errors)
    if audit_report.get("status") != "complete":
        errors.append("표시 표면 감사가 완료되지 않았습니다")
    report = {
        "family": FAMILY,
        "namespaces": namespace_reports,
        "keys": total_keys,
        "existing_korean_reused": 0,
        "new_translation_keys": total_keys,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "language_validation.json", report)
    completion = {
        "family": FAMILY,
        "language_keys": total_keys,
        "namespace_keys": {row["namespace"]: row["keys"] for row in namespace_reports},
        "existing_korean_reused": 0,
        "new_translation_keys": total_keys,
        "ftbquests_kubejs_references": len(
            audit_report.get("ftbquests_kubejs_references", [])
        ),
        "guide_help_keys": audit_report.get("little_big_redstone", {}).get(
            "guide_help_keys"
        ),
        "advancement_files": len(
            audit_report.get("redstonepen", {}).get("advancement_files", [])
        ),
        "output_files": [
            f"resourcepacks/ATM10_Korean/assets/{namespace}/lang/ko_kr.json"
            for namespace in NAMESPACES
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


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 스크립트의 두 산출물 백업·해시 결과를 완료 기록에 반영한다."""
    resolved = manifest_path.resolve()
    try:
        relative_manifest = resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError as exc:
        raise ValueError(f"프로젝트 밖의 적용 기록입니다: {resolved}") from exc
    manifest = load_json(resolved)
    expected = {
        f"resourcepacks/ATM10_Korean/assets/{namespace}/lang/ko_kr.json": (
            RESOURCEPACK_ROOT / namespace / "lang/ko_kr.json"
        )
        for namespace in NAMESPACES
    }
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
        if set(files) != set(expected):
            continue
        for relative, source in expected.items():
            row = files[relative]
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
        "output_sha256": {
            namespace: sha256(RESOURCEPACK_ROOT / namespace / "lang/ko_kr.json")
            for namespace in NAMESPACES
        },
        "errors": errors,
    }
    completion_path = WORK_ROOT / "family_completion.json"
    completion = load_json(completion_path)
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
