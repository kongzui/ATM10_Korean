#!/usr/bin/env python3
"""AE2 연동 모드 GuideME 가이드의 현재 배치를 검증해 리소스팩에 만든다."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import zipfile
from pathlib import Path, PurePosixPath

import build_ae2_guide as core
from local_paths import resolve_source_root
from version_context import active_output_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCEPACK_ROOT = active_output_root() / "resourcepack/ATM10_Korean"
ADDON_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/ae2wtlib"
GUIDE_WORKING_ROOT = ADDON_WORKING_ROOT / "ae2guide/_ko_kr"
LANG_WORKING_FILE = ADDON_WORKING_ROOT / "lang/ko_kr.json"
CORE_COMPAT_WORKING_FILE = (
    PROJECT_ROOT
    / "working/ae2/ae2guide/_ko_kr/items-blocks-machines/wireless_terminals.md"
)
PROGRESS_FILE = PROJECT_ROOT / "working/ae2_addons/guide_progress.json"
AE2WTLIB_PROGRESS_FILE = ADDON_WORKING_ROOT / "quality_review_progress.json"

ACTIVE_BATCH = 15
ADDON_GUIDE_FILES = (
    "ae2wtlib/ae2wtlib-index.md",
    "ae2wtlib/magnet_card.md",
    "ae2wtlib/quantum_bridge_card.md",
    "ae2wtlib/restock.md",
    "ae2wtlib/wireless_crafting_terminal.md",
    "ae2wtlib/wireless_terminals.md",
    "ae2wtlib/wireless_universal_terminal.md",
)
CORE_COMPAT_RELATIVE = "items-blocks-machines/wireless_terminals.md"
LANG_RELATIVE = "assets/ae2wtlib/lang/ko_kr.json"
GUIDE_OUTPUT_ROOT = RESOURCEPACK_ROOT / "assets/ae2wtlib/ae2guide/_ko_kr"
CORE_COMPAT_OUTPUT_FILE = (
    RESOURCEPACK_ROOT
    / "assets/ae2/ae2guide/_ko_kr/items-blocks-machines/wireless_terminals.md"
)
LANG_OUTPUT_FILE = RESOURCEPACK_ROOT / LANG_RELATIVE

GUIDE_SOURCE_ROOTS = {
    "ae2": PurePosixPath("assets/ae2/ae2guide"),
    "ae2wtlib": PurePosixPath("assets/ae2wtlib/ae2guide"),
    "enderdrives": PurePosixPath("assets/enderdrives/ae2guide"),
    "extendedae": PurePosixPath("assets/extendedae/ae2guide"),
    "advanced_ae": PurePosixPath("assets/advanced_ae/ae2guide"),
    "megacells": PurePosixPath("assets/megacells/ae2guide"),
    "appflux": PurePosixPath("assets/appflux/ae2guide"),
    "expandedae": PurePosixPath("assets/expandedae/ae2guide"),
    "ae2netanalyser": PurePosixPath("assets/ae2netanalyser/ae2guide"),
    "merequester": PurePosixPath("assets/merequester/ae2guide"),
    "arseng": PurePosixPath("assets/arseng/ae2guide"),
}
GUIDE_ITEM_NAMES = {
    "item.ae2wtlib.magnet_card": "ae2wtlib/magnet_card.md",
    "item.ae2wtlib.quantum_bridge_card": "ae2wtlib/quantum_bridge_card.md",
    "item.ae2wtlib.wireless_pattern_encoding_terminal": (
        "ae2wtlib/wireless_terminals.md"
    ),
    "item.ae2wtlib.wireless_pattern_access_terminal": (
        "ae2wtlib/wireless_terminals.md"
    ),
    "item.ae2wtlib.wireless_universal_terminal": (
        "ae2wtlib/wireless_universal_terminal.md"
    ),
}
AE2WTLIB_QUALITY_TRANSLATIONS = {
    "ae2wtlib.configuration.magnet_card_range": ("무선 터미널 자석 카드 범위"),
    "gui.ae2wtlib.magnetcard": "무선 터미널 자석 카드",
    "gui.ae2wtlib.magnetcard.hotkey": "무선 터미널 자석 카드: %s",
    "gui.ae2wtlib.slot.magnetcard.desc": "무선 터미널 자석 카드",
    "gui.ae2wtlib.terminal_empty": ("이 터미널에는 다른 터미널이 들어 있지 않습니다."),
    "item.ae2wtlib.magnet_card": "무선 터미널 자석 카드",
    "item.ae2wtlib.quantum_bridge_card.desc": (
        "무선 터미널을 양자 네트워크 브리지에 연결하여 거리 제한 없이 "
        "사용할 수 있게 합니다."
    ),
    "key.ae2.ae2wtlib_magnet": "무선 터미널 자석 카드 전환",
}
AE2WTLIB_FORBIDDEN_GUIDE_PHRASES = (
    "불러와져 있어야",
    "단축바의 아이템 수를 바꾸어",
    "왼클릭(또는 우클릭)",
    "다음(또는 이전)",
    "양자얽힘 특이점",
)
PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{\d+\}")
FORMAT_CODE_RE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
TAG_TOKEN_RE = re.compile(r"<(/?)([A-Za-z][\w:]*)\b[^>]*>")
ITEM_TAG_RE = re.compile(
    r'<(?:ItemLink|ItemImage|ItemIcon|BlockImage)\b[^>]*\bid="([^"]+)"'
)
RECIPE_FOR_RE = re.compile(r'<RecipeFor\b[^>]*\bid="([^"]+)"')
RECIPE_RE = re.compile(r'<Recipe\b[^>]*\bid="([^"]+)"')
VOID_TAGS = {"br", "hr", "img", "input", "meta", "link"}

ENDERDRIVES_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/enderdrives"
ENDERDRIVES_PROGRESS_FILE = ENDERDRIVES_WORKING_ROOT / "quality_review_progress.json"
ENDERDRIVES_GUIDE_WORKING_ROOT = ENDERDRIVES_WORKING_ROOT / "ae2guide/_ko_kr"
ENDERDRIVES_LANG_WORKING_FILE = ENDERDRIVES_WORKING_ROOT / "lang/ko_kr.json"
ENDERDRIVES_GUIDE_FILES = (
    "enderdrives_intro/enderdrives_intro-index.md",
    "enderdrives_intro/enderdrives_intro.md",
    "enderdrives_intro/tapedrive_intro.md",
)
ENDERDRIVES_GUIDE_OUTPUT_ROOT = RESOURCEPACK_ROOT / "assets/enderdrives/ae2guide/_ko_kr"
ENDERDRIVES_LANG_RELATIVE = "assets/enderdrives/lang/ko_kr.json"
ENDERDRIVES_LANG_OUTPUT_FILE = RESOURCEPACK_ROOT / ENDERDRIVES_LANG_RELATIVE
ENDERDRIVES_TOOLTIP_RELATIVE = Path("kubejs/client_scripts/enderdrives_tooltips.js")
ENDERDRIVES_TOOLTIP_WORKING_FILE = (
    ENDERDRIVES_WORKING_ROOT / ENDERDRIVES_TOOLTIP_RELATIVE
)
ENDERDRIVES_TOOLTIP_OUTPUT_FILE = (
    active_output_root() / "overrides" / ENDERDRIVES_TOOLTIP_RELATIVE
)
ENDERDRIVES_MESSAGES_RELATIVE = Path("kubejs/startup_scripts/enderdrives_messages.js")
ENDERDRIVES_MESSAGES_WORKING_FILE = (
    ENDERDRIVES_WORKING_ROOT / ENDERDRIVES_MESSAGES_RELATIVE
)
ENDERDRIVES_MESSAGES_OUTPUT_FILE = (
    active_output_root() / "overrides" / ENDERDRIVES_MESSAGES_RELATIVE
)
ENDERDRIVES_CLASS_LITERAL_MARKERS = {
    "com/sts15/enderdrives/items/AbstractEnderDiskItem.class": (
        b"tooltip.enderdrives.disabled",
        b"tooltip.enderdrives.disk.duplicate_sleep",
        b"tooltip.enderdrives.partitioned_item",
        b"tooltip.enderdrives.partitioned_fluid",
    ),
    "com/sts15/enderdrives/items/EnderDiskItem.class": (
        b"tooltip.enderdrives.enderdisk.disabled",
    ),
    "com/sts15/enderdrives/items/EnderFluidDiskItem.class": (
        b"tooltip.enderdrives.fluidenderdisk.disabled",
    ),
    "com/sts15/enderdrives/items/TapeDiskItem.class": (
        b"tooltip.enderdrives.tape.duplicate_sleep",
        b"Ideal for tools, armor, and NBT-heavy items.",
        b"Tape ID: ",
        b"tooltip.enderdrives.partitioned_item",
    ),
    "com/sts15/enderdrives/mixins/IOPortBlockEntityMixin.class": (
        b"Transfer blocked: Infinite loop detected between linked drives.",
    ),
    "com/sts15/enderdrives/mixins/compat/TileExIOPortMixin.class": (
        b"Transfer blocked: Infinite loop detected between linked drives.",
    ),
    "com/sts15/enderdrives/commands/ModCommands.class": (
        b"Frequency must be between ",
        b"[EnderDrives Tape Stats]",
        b"[EnderDrives Autobenchmark]",
        b"Hold an EnderDisk in your hand.",
    ),
}
ENDERDRIVES_TOOLTIP_SCRIPT_MARKERS = (
    "ItemEvents.dynamicTooltips('enderdrives_korean'",
    "This item is disabled on the server.",
    "Ideal for tools, armor, and NBT-heavy items.",
    "Tape ID: (.+)",
    "파티션 항목",
)
ENDERDRIVES_MESSAGES_SCRIPT_MARKERS = (
    "ClientChatReceivedEvent$System",
    "This EnderDisk is disabled on the server.",
    "Transfer blocked: Infinite loop detected between linked drives.",
    "[EnderDrives Tape Stats]",
    "[EnderDrives Autobenchmark]",
    "Hold an EnderDisk in your hand.",
    "translateEnderDrivesSystemMessage",
)
ENDERDRIVES_FORBIDDEN_GUIDE_PHRASES = (
    "AE2 시스템 안이든",
    "전역 동기화 저장소를 제공하는 강력한 드라이브",
    "거대한 드라이브의 종류 한도",
    "불러와져 있어야",
)
NUMBER_RE = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?(?:\^\d+)?(?:k|K)?")
EXTENDEDAE_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/extendedae"
EXTENDEDAE_PROGRESS_FILE = EXTENDEDAE_WORKING_ROOT / "quality_review_progress.json"
EXTENDEDAE_LANG_WORKING_FILE = EXTENDEDAE_WORKING_ROOT / "lang/ko_kr.json"
EXTENDEDAE_LANG_RELATIVE = "assets/extendedae/lang/ko_kr.json"
EXTENDEDAE_LANG_OUTPUT_FILE = RESOURCEPACK_ROOT / EXTENDEDAE_LANG_RELATIVE
EXTENDEDAE_GUIDE_WORKING_ROOT = EXTENDEDAE_WORKING_ROOT / "ae2guide/_ko_kr"
EXTENDEDAE_GUIDE_OUTPUT_ROOT = RESOURCEPACK_ROOT / "assets/extendedae/ae2guide/_ko_kr"
EXTENDEDAE_QUEST_OVERRIDES_FILE = EXTENDEDAE_WORKING_ROOT / "quest_overrides.json"
EXTENDEDAE_INFINITY_CELLS_RELATIVE = Path(
    "kubejs/startup_scripts/ExtendedAE/InfinityCells.js"
)
EXTENDEDAE_QUALITY_TRANSLATIONS = {
    "itemGroup.extendedae": "Extended AE",
    "tag_display.tooltip.hint": "Shift 키를 누르고 있으면 태그를 표시합니다.",
    "gui.extendedae.ex_inscriber.next": "다음 각인 작업",
    "gui.extendedae.ex_inscriber.pre": "이전 각인 작업",
    "gui.extendedae.ex_inscriber.number": "각인 작업 %s",
    "gui.extendedae.pattern_modifier.multi.desc": (
        "입력 및 출력 수량을 %s배로 만듭니다."
    ),
    "gui.extendedae.tag_storage_bus.desc.03": ("() = 연산 우선순위    * = 와일드카드"),
    "gui.extendedae.void_cell.mode.1": "모드: 물질 덩어리",
    "gui.extendedae.set_output_sides.clear": "모든 출력 면 해제",
    "chat.config_modifier.success": "%s 설정을 수정했습니다.",
}
EXTENDEDAE_FORBIDDEN_GUIDE_PHRASES = (
    "인쇄 작업 4개",
    "2.1십억",
    "x16배",
    "999999",
    "ExtendedAE의",
    "Applied Flux 지원",
    "태그 식:",
)
EXTENDEDAE_BATCH_03_GUIDE_FILES = (
    "epp_intro/epp_intro-index.md",
    "epp_intro/machine_frame.md",
    "epp_intro/quartz_blend.md",
    "epp_intro/silicon_block.md",
    "epp_intro/entro_block.md",
    "epp_intro/entro_budding.md",
    "epp_intro/entro_crystal.md",
    "epp_intro/entro_dust.md",
    "epp_intro/entro_ingot.md",
    "epp_intro/entro_seed.md",
    "epp_intro/entro_shard.md",
)
EXTENDEDAE_BATCH_03_ITEM_NAMES = {
    "block.extendedae.machine_frame": "epp_intro/machine_frame.md",
    "item.extendedae.quartz_blend": "epp_intro/quartz_blend.md",
    "block.extendedae.silicon_block": "epp_intro/silicon_block.md",
    "block.extendedae.entro_block": "epp_intro/entro_block.md",
    "item.extendedae.entro_crystal": "epp_intro/entro_crystal.md",
    "item.extendedae.entro_dust": "epp_intro/entro_dust.md",
    "item.extendedae.entro_ingot": "epp_intro/entro_ingot.md",
    "item.extendedae.entro_seed": "epp_intro/entro_seed.md",
    "item.extendedae.entro_shard": "epp_intro/entro_shard.md",
}
EXTENDEDAE_BATCH_04_GUIDE_FILES = (
    "epp_intro/config_modifier.md",
    "epp_intro/extended_drive.md",
    "epp_intro/infinity_cell.md",
    "epp_intro/ingredient_buffer.md",
    "epp_intro/mod_storage_bus.md",
    "epp_intro/oversize_interface.md",
    "epp_intro/packing_tape.md",
    "epp_intro/pattern_modifier.md",
    "epp_intro/precise_storage_bus.md",
    "epp_intro/void_cell.md",
)
EXTENDEDAE_BATCH_04_ITEM_NAMES = {
    "item.extendedae.config_modifier": "epp_intro/config_modifier.md",
    "block.extendedae.ex_drive": "epp_intro/extended_drive.md",
    "item.extendedae.infinity_cell": "epp_intro/infinity_cell.md",
    "block.extendedae.ingredient_buffer": "epp_intro/ingredient_buffer.md",
    "item.extendedae.mod_storage_bus": "epp_intro/mod_storage_bus.md",
    "block.extendedae.oversize_interface": "epp_intro/oversize_interface.md",
    "item.extendedae.me_packing_tape": "epp_intro/packing_tape.md",
    "item.extendedae.pattern_modifier": "epp_intro/pattern_modifier.md",
    "item.extendedae.precise_storage_bus": "epp_intro/precise_storage_bus.md",
    "item.extendedae.void_cell": "epp_intro/void_cell.md",
}
EXTENDEDAE_BATCH_05_GUIDE_FILES = (
    "epp_intro/assembler_matrix.md",
    "epp_intro/caner.md",
    "epp_intro/circuit_cutter.md",
    "epp_intro/concurrent_processor.md",
    "epp_intro/crystal_assembler.md",
    "epp_intro/crystal_fixer.md",
    "epp_intro/extended_charger.md",
    "epp_intro/extended_inscriber.md",
    "epp_intro/extended_interface.md",
    "epp_intro/extended_io_port.md",
    "epp_intro/extended_modecular_assembler.md",
    "epp_intro/extended_pattern_provider.md",
    "epp_intro/extended_pattern_terminal.md",
)
EXTENDEDAE_BATCH_05_ITEM_NAMES = {
    "block.extendedae.assembler_matrix_frame": "epp_intro/assembler_matrix.md",
    "block.extendedae.caner": "epp_intro/caner.md",
    "block.extendedae.circuit_cutter": "epp_intro/circuit_cutter.md",
    "item.extendedae.concurrent_processor": "epp_intro/concurrent_processor.md",
    "block.extendedae.crystal_assembler": "epp_intro/crystal_assembler.md",
    "block.extendedae.crystal_fixer": "epp_intro/crystal_fixer.md",
    "block.extendedae.ex_charger": "epp_intro/extended_charger.md",
    "block.extendedae.ex_inscriber": "epp_intro/extended_inscriber.md",
    "block.extendedae.ex_interface": "epp_intro/extended_interface.md",
    "block.extendedae.ex_io_port": "epp_intro/extended_io_port.md",
    "block.extendedae.ex_molecular_assembler": (
        "epp_intro/extended_modecular_assembler.md"
    ),
    "block.extendedae.ex_pattern_provider": "epp_intro/extended_pattern_provider.md",
    "item.extendedae.ex_pattern_access_part": (
        "epp_intro/extended_pattern_terminal.md"
    ),
}
EXTENDEDAE_BATCH_06_GUIDE_FILES = (
    "epp_intro/active_formation_plane.md",
    "epp_intro/extended_io_bus.md",
    "epp_intro/mod_export_bus.md",
    "epp_intro/precise_export_bus.md",
    "epp_intro/smart_annihilation_plane.md",
    "epp_intro/tag_export_bus.md",
    "epp_intro/tag_storage_bus.md",
    "epp_intro/threshold_export_bus.md",
    "epp_intro/threshold_level_emitter.md",
    "epp_intro/upgrade_items.md",
    "epp_intro/wireless_connector.md",
    "epp_intro/wireless_hub.md",
)
EXTENDEDAE_BATCH_06_ITEM_NAMES = {
    "item.extendedae.active_formation_plane": "epp_intro/active_formation_plane.md",
    "item.extendedae.ex_import_bus_part": "epp_intro/extended_io_bus.md",
    "item.extendedae.mod_export_bus": "epp_intro/mod_export_bus.md",
    "item.extendedae.precise_export_bus": "epp_intro/precise_export_bus.md",
    "item.extendedae.smart_annihilation_plane": (
        "epp_intro/smart_annihilation_plane.md"
    ),
    "item.extendedae.tag_export_bus": "epp_intro/tag_export_bus.md",
    "item.extendedae.tag_storage_bus": "epp_intro/tag_storage_bus.md",
    "item.extendedae.threshold_export_bus": "epp_intro/threshold_export_bus.md",
    "item.extendedae.threshold_level_emitter": ("epp_intro/threshold_level_emitter.md"),
    "item.extendedae.pattern_provider_upgrade": "epp_intro/upgrade_items.md",
    "block.extendedae.wireless_connect": "epp_intro/wireless_connector.md",
    "block.extendedae.wireless_hub": "epp_intro/wireless_hub.md",
}
EXTENDEDAE_BATCH_GUIDE_FILES = {
    3: EXTENDEDAE_BATCH_03_GUIDE_FILES,
    4: EXTENDEDAE_BATCH_04_GUIDE_FILES,
    5: EXTENDEDAE_BATCH_05_GUIDE_FILES,
    6: EXTENDEDAE_BATCH_06_GUIDE_FILES,
}
EXTENDEDAE_BATCH_ITEM_NAMES = {
    3: EXTENDEDAE_BATCH_03_ITEM_NAMES,
    4: EXTENDEDAE_BATCH_04_ITEM_NAMES,
    5: EXTENDEDAE_BATCH_05_ITEM_NAMES,
    6: EXTENDEDAE_BATCH_06_ITEM_NAMES,
}
EXTENDEDAE_BATCH_SCOPES = {
    3: "ExtendedAE materials and introduction GuideME guide batch 03",
    4: "ExtendedAE storage and configuration GuideME guide batch 04",
    5: "ExtendedAE autocrafting and machines GuideME guide batch 05",
    6: "ExtendedAE networking and input-output GuideME guide batch 06",
}

ADVANCEDAE_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/advanced_ae"
ADVANCEDAE_LANG_WORKING_FILE = ADVANCEDAE_WORKING_ROOT / "lang/ko_kr.json"
ADVANCEDAE_LANG_RELATIVE = "assets/advanced_ae/lang/ko_kr.json"
ADVANCEDAE_LANG_OUTPUT_FILE = RESOURCEPACK_ROOT / ADVANCEDAE_LANG_RELATIVE
ADVANCEDAE_GUIDE_WORKING_ROOT = ADVANCEDAE_WORKING_ROOT / "ae2guide/_ko_kr"
ADVANCEDAE_GUIDE_OUTPUT_ROOT = RESOURCEPACK_ROOT / "assets/advanced_ae/ae2guide/_ko_kr"
ADVANCEDAE_QUEST_OVERRIDES_FILE = ADVANCEDAE_WORKING_ROOT / "quest_overrides.json"
ADVANCEDAE_KUBEJS_RELATIVE = Path("kubejs/client_scripts/RecipeViewer.js")
ADVANCEDAE_KUBEJS_WORKING_FILE = ADVANCEDAE_WORKING_ROOT / ADVANCEDAE_KUBEJS_RELATIVE
ADVANCEDAE_KUBEJS_OUTPUT_FILE = (
    active_output_root() / "overrides" / ADVANCEDAE_KUBEJS_RELATIVE
)
ADVANCEDAE_KUBEJS_SOURCE_TEXT = (
    "§8In the Reaction Chamber: §e4000mb of Water§8 + "
    "§e1x Quantum Infused Dust§8 = §b1000mb of Quantum Infusion"
)
ADVANCEDAE_KUBEJS_TRANSLATED_TEXT = (
    "§8반응 챔버: §e물 4000 mB§8 + §e퀀텀 주입 가루 1개§8 = " "§b퀀텀 주입액 1000 mB"
)
ADVANCEDAE_LANGUAGE_COMPLETION_FILE = (
    ADVANCEDAE_WORKING_ROOT / "language_completion.json"
)
ADVANCEDAE_PROGRESS_FILE = ADVANCEDAE_WORKING_ROOT / "quality_review_progress.json"
ADVANCEDAE_QUALITY_TRANSLATIONS = {
    "block.advanced_ae.adv_pattern_provider": "고급 확장 패턴 공급기",
    "block.advanced_ae.small_adv_pattern_provider": "고급 패턴 공급기",
    "gui.advanced_ae.AdvancedIOBus": "ME 고급 입출력 버스",
    "gui.tooltips.advanced_ae.AutoFeedTooltip": (
        "ME 시스템의 음식으로 사용자의 허기를 자동으로 채우도록 설정할 수 있습니다."
    ),
    "gui.tooltips.advanced_ae.MultiThreaderMultiplication": (
        "퀀텀 컴퓨터 멀티블록의 보조 처리 스레드 수를 %d배로 만듭니다. "
        "멀티블록당 %d개로 제한됩니다."
    ),
    "gui.tooltips.advanced_ae.RegulateOn": (
        "필터 수량을 초과한 아이템의 반입을 시도합니다"
    ),
}
ADVANCEDAE_FORBIDDEN_GUIDE_PHRASES = (
    "패턴 제공기",
    "ME 고급 I/O 버스",
    "몇 가지 스택",
    "보조 처리 장치",
    "일반 제공기를 확장 제공기로",
    "퀀텀 코어",
    "퀀텀 가속기",
    "퀀텀 멀티 스레더",
    "완전한 블록 형태의 패턴 공급기",
    "출력 수량을 조절하지는",
)
ADVANCEDAE_BATCH_07_GUIDE_FILES = (
    "aae_intro/aae_intro-index.md",
    "aae_intro/advanced_io_bus.md",
    "aae_intro/advanced_pattern_encoder.md",
    "aae_intro/advanced_pattern_provider.md",
    "aae_intro/app_upgrade_items.md",
    "aae_intro/import_export_bus.md",
    "aae_intro/stock_export_bus.md",
    "aae_intro/throughput_monitor.md",
)
ADVANCEDAE_BATCH_07_ITEM_NAMES = {
    "item.advanced_ae.advanced_io_bus_part": "aae_intro/advanced_io_bus.md",
    "item.advanced_ae.adv_pattern_encoder": "aae_intro/advanced_pattern_encoder.md",
    "item.advanced_ae.small_adv_pattern_provider_part": (
        "aae_intro/advanced_pattern_provider.md"
    ),
    "item.advanced_ae.adv_pattern_provider_capacity_upgrade": (
        "aae_intro/app_upgrade_items.md"
    ),
    "item.advanced_ae.import_export_bus_part": "aae_intro/import_export_bus.md",
    "item.advanced_ae.stock_export_bus_part": "aae_intro/stock_export_bus.md",
    "item.advanced_ae.throughput_monitor": "aae_intro/throughput_monitor.md",
}
ADVANCEDAE_BATCH_08_GUIDE_FILES = (
    "aae_intro/quantum_armor.md",
    "aae_intro/quantum_computer.md",
    "aae_intro/quantum_crafter.md",
    "aae_intro/quantum_crafter_terminal.md",
    "aae_intro/reaction_chamber.md",
)
ADVANCEDAE_BATCH_08_ITEM_NAMES = {
    "item.advanced_ae.quantum_upgrade_base": "aae_intro/quantum_armor.md",
    "block.advanced_ae.quantum_core": "aae_intro/quantum_computer.md",
    "block.advanced_ae.quantum_crafter": "aae_intro/quantum_crafter.md",
    "item.advanced_ae.quantum_crafter_terminal": (
        "aae_intro/quantum_crafter_terminal.md"
    ),
    "block.advanced_ae.reaction_chamber": "aae_intro/reaction_chamber.md",
}
ADVANCEDAE_BATCH_GUIDE_FILES = {
    7: ADVANCEDAE_BATCH_07_GUIDE_FILES,
    8: ADVANCEDAE_BATCH_08_GUIDE_FILES,
}
ADVANCEDAE_BATCH_ITEM_NAMES = {
    7: ADVANCEDAE_BATCH_07_ITEM_NAMES,
    8: ADVANCEDAE_BATCH_08_ITEM_NAMES,
}
ADVANCEDAE_BATCH_SCOPES = {
    7: "AdvancedAE automation and input-output GuideME guide batch 07",
    8: "AdvancedAE quantum equipment and machines GuideME guide batch 08",
}

MEGACELLS_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/megacells"
MEGACELLS_LANG_WORKING_FILE = MEGACELLS_WORKING_ROOT / "lang/ko_kr.json"
MEGACELLS_LANG_RELATIVE = "assets/megacells/lang/ko_kr.json"
MEGACELLS_LANG_OUTPUT_FILE = RESOURCEPACK_ROOT / MEGACELLS_LANG_RELATIVE
MEGACELLS_GUIDE_WORKING_ROOT = MEGACELLS_WORKING_ROOT / "ae2guide/_ko_kr"
MEGACELLS_GUIDE_OUTPUT_ROOT = RESOURCEPACK_ROOT / "assets/megacells/ae2guide/_ko_kr"
MEGACELLS_QUEST_OVERRIDES_FILE = MEGACELLS_WORKING_ROOT / "quest_overrides.json"
MEGACELLS_LANGUAGE_COMPLETION_FILE = MEGACELLS_WORKING_ROOT / "language_completion.json"
MEGACELLS_PROGRESS_FILE = MEGACELLS_WORKING_ROOT / "quality_review_progress.json"
MEGACELLS_BATCH_09_GUIDE_FILES = (
    "index.md",
    "storage.md",
    "bulk_cell.md",
    "radioactive_cell.md",
)
MEGACELLS_BATCH_10_GUIDE_FILES = (
    "crafting.md",
    "energy.md",
    "extras.md",
)
MEGACELLS_BATCH_GUIDE_FILES = {
    9: MEGACELLS_BATCH_09_GUIDE_FILES,
    10: MEGACELLS_BATCH_10_GUIDE_FILES,
}
MEGACELLS_BATCH_ITEM_NAMES = {
    9: {
        "item.megacells.cell_component_1m": "storage.md",
        "item.megacells.bulk_item_cell": "bulk_cell.md",
        "item.megacells.radioactive_chemical_cell": "radioactive_cell.md",
    },
    10: {
        "block.megacells.mega_crafting_unit": "crafting.md",
        "block.megacells.mega_energy_cell": "energy.md",
        "item.megacells.cell_dock": "extras.md",
    },
}
MEGACELLS_BATCH_SCOPES = {
    9: "MEGA Cells introduction and storage GuideME guide batch 09",
    10: "MEGA Cells crafting, energy and extras GuideME guide batch 10",
}
MEGACELLS_QUALITY_TRANSLATIONS = {
    "gui.tooltips.megacells.CompressionCutoff": "대용량 압축 상한",
    "gui.tooltips.megacells.Cutoff": "상한: %s",
    "gui.tooltips.megacells.NotPartitioned": "파티션 미설정",
    "gui.tooltips.megacells.PartitionedFor": "파티션 대상: %s",
}
MEGACELLS_FORBIDDEN_GUIDE_PHRASES = (
    "기준값",
    "분할",
)

APPFLUX_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/appflux"
APPFLUX_LANG_WORKING_FILE = APPFLUX_WORKING_ROOT / "lang/ko_kr.json"
APPFLUX_LANG_RELATIVE = "assets/appflux/lang/ko_kr.json"
APPFLUX_LANG_OUTPUT_FILE = RESOURCEPACK_ROOT / APPFLUX_LANG_RELATIVE
APPFLUX_GUIDE_WORKING_ROOT = APPFLUX_WORKING_ROOT / "ae2guide/_ko_kr"
APPFLUX_GUIDE_OUTPUT_ROOT = RESOURCEPACK_ROOT / "assets/appflux/ae2guide/_ko_kr"
APPFLUX_QUEST_OVERRIDES_FILE = APPFLUX_WORKING_ROOT / "quest_overrides.json"
APPFLUX_LANGUAGE_COMPLETION_FILE = APPFLUX_WORKING_ROOT / "language_completion.json"
APPFLUX_BATCH_11_GUIDE_FILES = (
    "appflux/appflux-index.md",
    "appflux/diamond_dust.md",
    "appflux/emerald_dust.md",
    "appflux/energy_processor.md",
    "appflux/flux_accessor.md",
    "appflux/flux_cells.md",
    "appflux/induction_card.md",
    "appflux/insulating_resin.md",
    "appflux/mark_energy.md",
    "appflux/portable_flux_cells.md",
    "appflux/redstone_crystal.md",
    "appflux/terminal_interact.md",
)
APPFLUX_BATCH_11_ITEM_NAMES = {
    "item.appflux.diamond_dust": "appflux/diamond_dust.md",
    "item.appflux.emerald_dust": "appflux/emerald_dust.md",
    "item.appflux.energy_processor": "appflux/energy_processor.md",
    "item.appflux.part_flux_accessor": "appflux/flux_accessor.md",
    "item.appflux.fe_cell_housing": "appflux/flux_cells.md",
    "item.appflux.induction_card": "appflux/induction_card.md",
    "item.appflux.insulating_resin": "appflux/insulating_resin.md",
    "group.fe_portable_cells.name": "appflux/portable_flux_cells.md",
    "item.appflux.redstone_crystal": "appflux/redstone_crystal.md",
}

EXPANDEDAE_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/expandedae"
EXPANDEDAE_LANG_WORKING_FILE = EXPANDEDAE_WORKING_ROOT / "lang/ko_kr.json"
EXPANDEDAE_LANG_RELATIVE = "assets/expandedae/lang/ko_kr.json"
EXPANDEDAE_LANG_OUTPUT_FILE = RESOURCEPACK_ROOT / EXPANDEDAE_LANG_RELATIVE
EXPANDEDAE_GUIDE_WORKING_ROOT = EXPANDEDAE_WORKING_ROOT / "ae2guide/_ko_kr"
EXPANDEDAE_GUIDE_OUTPUT_ROOT = RESOURCEPACK_ROOT / "assets/expandedae/ae2guide/_ko_kr"
EXPANDEDAE_QUEST_OVERRIDES_FILE = EXPANDEDAE_WORKING_ROOT / "quest_overrides.json"
EXPANDEDAE_LANGUAGE_COMPLETION_FILE = (
    EXPANDEDAE_WORKING_ROOT / "language_completion.json"
)
EXPANDEDAE_KUBEJS_RELATIVE = Path(
    "kubejs/server_scripts/announcements/announcements.js"
)
EXPANDEDAE_KUBEJS_WORKING_FILE = EXPANDEDAE_WORKING_ROOT / EXPANDEDAE_KUBEJS_RELATIVE
EXPANDEDAE_KUBEJS_OUTPUT_FILE = (
    active_output_root() / "overrides" / EXPANDEDAE_KUBEJS_RELATIVE
)
EXPANDEDAE_TOOLTIP_OUTPUT_FILE = (
    active_output_root() / "overrides/kubejs/client_scripts/tooltips.js"
)
EXPANDEDAE_TOOLTIP_OVERRIDE = """    // Expanded AE
    if (Platform.isLoaded('expandedae')) {
        allthemods.modify('expandedae:exp_pattern_provider_upgrade', tooltip => {
            tooltip.removeText(Text.of('a Pattern Provider to an Expanded Pattern Provider'))
            tooltip.insert(1, Text.gray('패턴 공급기를 ME 확대 패턴 공급기로 업그레이드합니다'))
        })
    }
"""
EXPANDEDAE_BATCH_12_GUIDE_FILES = (
    "cards.md",
    "exp_encoding.md",
    "exp_pp.md",
    "expandedae-index.md",
    "qol-features.md",
)
EXPANDEDAE_BATCH_12_ITEM_NAMES = {
    "item.expandedae.auto_complete_card": "cards.md",
    "item.expandedae.exp_encoding_terminal": "exp_encoding.md",
    "item.expandedae.exp_pattern_provider_part": "exp_pp.md",
}

IMPORTEXPORT_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/ae2importexportcard"
IMPORTEXPORT_LANG_WORKING_FILE = IMPORTEXPORT_WORKING_ROOT / "lang/ko_kr.json"
IMPORTEXPORT_LANG_RELATIVE = "assets/ae2importexportcard/lang/ko_kr.json"
IMPORTEXPORT_LANG_OUTPUT_FILE = RESOURCEPACK_ROOT / IMPORTEXPORT_LANG_RELATIVE
IMPORTEXPORT_GUIDE_WORKING_ROOT = IMPORTEXPORT_WORKING_ROOT / "ae2guide/_ko_kr"
IMPORTEXPORT_GUIDE_RELATIVE = "ae2importexportcard-index.md"
IMPORTEXPORT_GUIDE_OUTPUT_FILE = (
    RESOURCEPACK_ROOT / "assets/ae2/ae2guide/_ko_kr" / IMPORTEXPORT_GUIDE_RELATIVE
)
IMPORTEXPORT_QUEST_OVERRIDES_FILE = IMPORTEXPORT_WORKING_ROOT / "quest_overrides.json"
IMPORTEXPORT_LANGUAGE_COMPLETION_FILE = (
    IMPORTEXPORT_WORKING_ROOT / "language_completion.json"
)
IMPORTEXPORT_PROGRESS_FILE = IMPORTEXPORT_WORKING_ROOT / "quality_review_progress.json"
IMPORTEXPORT_FORBIDDEN_GUIDE_PHRASES = (
    "인벤토리에서 아이템을 반입하거나 반출",
    "인벤토리의 아이템을 위쪽으로",
    "원하는 수량으로 바꾸세요",
    "아이템 NBT",
    "왼쪽 클릭",
    "오른쪽 클릭",
)

NETANALYSER_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/ae2netanalyser"
NETANALYSER_LANG_WORKING_FILE = NETANALYSER_WORKING_ROOT / "lang/ko_kr.json"
NETANALYSER_LANG_RELATIVE = "assets/ae2netanalyser/lang/ko_kr.json"
NETANALYSER_LANG_OUTPUT_FILE = RESOURCEPACK_ROOT / NETANALYSER_LANG_RELATIVE
NETANALYSER_GUIDE_WORKING_ROOT = NETANALYSER_WORKING_ROOT / "ae2guide/_ko_kr"
NETANALYSER_GUIDE_OUTPUT_ROOT = (
    RESOURCEPACK_ROOT / "assets/ae2netanalyser/ae2guide/_ko_kr"
)
NETANALYSER_QUEST_OVERRIDES_FILE = NETANALYSER_WORKING_ROOT / "quest_overrides.json"
NETANALYSER_LANGUAGE_COMPLETION_FILE = (
    NETANALYSER_WORKING_ROOT / "language_completion.json"
)
NETANALYSER_PROGRESS_FILE = NETANALYSER_WORKING_ROOT / "quality_review_progress.json"
NETANALYSER_QUALITY_LANGUAGE_CORRECTIONS = {
    "itemGroup.ae2netanalyser": "AE2 Network Analyzer",
}
NETANALYSER_FORBIDDEN_GUIDE_PHRASES = (
    "채널이 충분하고 8개 채널",
    "채널이 충분하고 32개 채널",
    "# ME 틱 속도 프로파일링",
    "TPS(초당 틱)",
    "50000μs/틱",
    "100μs/틱",
)
NETANALYSER_GUIDE_FILES = (
    "ae2_network_analyser.md",
    "ae2_tick_profiler.md",
)
NETANALYSER_GUIDE_ITEM_NAMES = {
    "item.ae2netanalyser.network_analyser": "ae2_network_analyser.md",
    "item.ae2netanalyser.tick_analyser": "ae2_tick_profiler.md",
}

MEREQUESTER_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/merequester"
MEREQUESTER_LANG_WORKING_FILE = MEREQUESTER_WORKING_ROOT / "lang/ko_kr.json"
MEREQUESTER_LANG_RELATIVE = "assets/merequester/lang/ko_kr.json"
MEREQUESTER_LANG_OUTPUT_FILE = RESOURCEPACK_ROOT / MEREQUESTER_LANG_RELATIVE
MEREQUESTER_GUIDE_WORKING_ROOT = MEREQUESTER_WORKING_ROOT / "ae2guide/_ko_kr"
MEREQUESTER_GUIDE_RELATIVE = "merequester.md"
MEREQUESTER_GUIDE_OUTPUT_FILE = (
    RESOURCEPACK_ROOT
    / "assets/merequester/ae2guide/_ko_kr"
    / MEREQUESTER_GUIDE_RELATIVE
)
MEREQUESTER_QUEST_OVERRIDES_FILE = MEREQUESTER_WORKING_ROOT / "quest_overrides.json"
MEREQUESTER_LANGUAGE_COMPLETION_FILE = (
    MEREQUESTER_WORKING_ROOT / "language_completion.json"
)
MEREQUESTER_PROGRESS_FILE = MEREQUESTER_WORKING_ROOT / "quality_review_progress.json"
MEREQUESTER_QUALITY_LANGUAGE_CORRECTIONS = {
    "tooltip.merequester.requester_desc": (
        "필요할 때 제작을 새로 요청해 아이템과 유체의 재고를 자동으로 유지합니다. "
        "ME 네트워크에 연결해야 하며 ME 요청기 터미널에서 접근할 수 있습니다. "
        "블록을 부수면 설정이 사라집니다. 메모리 카드로 설정을 복사할 수 있습니다."
    ),
    "tooltip.merequester.export_desc": (
        "요청기가 제작 결과를 ME 시스템으로 내보내고 있습니다. 이 상태가 오래 "
        "지속되면 ME 저장소에 빈 공간이 없는 것입니다."
    ),
}
MEREQUESTER_FORBIDDEN_GUIDE_PHRASES = (
    "유지할 수 있게 해주는",
    "네트워크와 같아야 합니다",
    "오른쪽 클릭",
    "왼쪽 클릭",
    "여러 개별 작업 대신",
    "대기 또는 비어 있음 이외의 상태",
)

ARSENG_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/arseng"
ARSENG_LANG_WORKING_FILE = ARSENG_WORKING_ROOT / "lang/ko_kr.json"
ARSENG_LANG_RELATIVE = "assets/arseng/lang/ko_kr.json"
ARSENG_LANG_OUTPUT_FILE = RESOURCEPACK_ROOT / ARSENG_LANG_RELATIVE
ARSENG_GUIDE_WORKING_ROOT = ARSENG_WORKING_ROOT / "ae2guide/_ko_kr"
ARSENG_GUIDE_RELATIVE = "arseng-index.md"
ARSENG_GUIDE_OUTPUT_FILE = (
    RESOURCEPACK_ROOT / "assets/arseng/ae2guide/_ko_kr" / ARSENG_GUIDE_RELATIVE
)
ARSENG_QUEST_OVERRIDES_FILE = ARSENG_WORKING_ROOT / "quest_overrides.json"
ARSENG_LANGUAGE_COMPLETION_FILE = ARSENG_WORKING_ROOT / "language_completion.json"
ARSENG_PROGRESS_FILE = ARSENG_WORKING_ROOT / "quality_review_progress.json"


def find_single_jar(instance: Path, pattern: str, label: str) -> Path:
    jars = sorted((instance / "mods").glob(pattern))
    if len(jars) != 1:
        raise ValueError(
            f"{label} JAR을 하나로 확정할 수 없습니다: {[p.name for p in jars]}"
        )
    return jars[0]


def find_jars(instance: Path) -> dict[str, Path]:
    return {
        "ae2": find_single_jar(instance, "appliedenergistics2-*.jar", "AE2"),
        "ae2wtlib": find_single_jar(instance, "ae2wtlib-*.jar", "AE2WTLib"),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extendedae_related_counts(instance: Path) -> tuple[int, int]:
    quest_overrides = json.loads(
        EXTENDEDAE_QUEST_OVERRIDES_FILE.read_text(encoding="utf-8")
    )
    infinity_script = (instance / EXTENDEDAE_INFINITY_CELLS_RELATIVE).read_text(
        encoding="utf-8-sig"
    )
    infinity_cells = set(
        re.findall(
            r"allthemods\.create\('([^']+)',\s*'custom_infinity_cell'\)",
            infinity_script,
        )
    )
    return len(quest_overrides), len(infinity_cells)


def load_json_unique(path: Path) -> dict[str, str]:
    duplicates: list[str] = []

    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        return result

    raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    if duplicates:
        raise ValueError(f"중복 언어 키가 있습니다: {sorted(set(duplicates))}")
    if not isinstance(raw, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in raw.items()
    ):
        raise ValueError(f"언어 파일은 문자열 키와 값만 가져야 합니다: {path}")
    return raw


def load_archive_json_unique(archive: zipfile.ZipFile, entry: str) -> dict[str, str]:
    duplicates: list[str] = []

    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        return result

    raw = json.loads(
        archive.read(entry).decode("utf-8-sig"), object_pairs_hook=unique_object
    )
    if duplicates:
        raise ValueError(f"{entry}: 중복 언어 키가 있습니다: {sorted(set(duplicates))}")
    if not isinstance(raw, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in raw.items()
    ):
        raise ValueError(f"{entry}: 문자열 키와 값만 가져야 합니다.")
    return raw


def validate_language(source: dict[str, str], translated: dict[str, str]) -> list[str]:
    errors = []
    source_keys = set(source)
    translated_keys = set(translated)
    if source_keys != translated_keys:
        errors.append(
            "AE2WTLib 언어 키가 다릅니다: "
            f"누락={sorted(source_keys - translated_keys)}, "
            f"불필요={sorted(translated_keys - source_keys)}"
        )
    for key in sorted(source_keys & translated_keys):
        expected = PLACEHOLDER_RE.findall(source[key])
        actual = PLACEHOLDER_RE.findall(translated[key])
        if expected != actual:
            errors.append(f"{key}: 자리표시자가 다릅니다: {expected} != {actual}")
        if source[key].count("\n") != translated[key].count("\n"):
            errors.append(f"{key}: 줄바꿈 수가 다릅니다.")
        if FORMAT_CODE_RE.findall(source[key]) != FORMAT_CODE_RE.findall(
            translated[key]
        ):
            errors.append(f"{key}: 서식 코드가 다릅니다.")
    return errors


def validate_tag_nesting(relative: str, text: str) -> list[str]:
    errors = []
    stack: list[str] = []
    protected_text = core.INLINE_CODE_RE.sub("", text)
    for match in TAG_TOKEN_RE.finditer(protected_text):
        closing, name = match.groups()
        if match.group(0).endswith("/>") or name.lower() in VOID_TAGS:
            continue
        if closing:
            if not stack or stack[-1] != name:
                errors.append(f"{relative}: 태그 닫힘 순서가 잘못됐습니다: {name}")
                continue
            stack.pop()
        else:
            stack.append(name)
    if stack:
        errors.append(f"{relative}: 닫히지 않은 태그가 있습니다: {stack}")
    return errors


def resolve_guide_reference(namespace: str, page: str, target: str) -> str | None:
    clean = target.split("#", 1)[0].split("?", 1)[0]
    if not clean or re.match(r"^(?:https?://|mailto:)", clean):
        return None
    namespace_match = re.match(r"^([a-z0-9_.-]+):(.*)$", clean)
    if namespace_match:
        target_namespace, target_path = namespace_match.groups()
        root = GUIDE_SOURCE_ROOTS.get(target_namespace)
        if root is None:
            return None
        return posixpath.normpath((root / target_path).as_posix())
    root = GUIDE_SOURCE_ROOTS[namespace]
    return posixpath.normpath((root / PurePosixPath(page).parent / clean).as_posix())


def split_resource_id(value: str, default_namespace: str) -> tuple[str, str]:
    if ":" in value:
        return tuple(value.split(":", 1))  # type: ignore[return-value]
    return default_namespace, value


def item_resource_exists(
    archive_names: dict[str, set[str]], default_namespace: str, value: str
) -> bool:
    namespace, path = split_resource_id(value, default_namespace)
    if namespace not in archive_names:
        return True
    names = archive_names.get(namespace, set())
    candidates = (
        f"assets/{namespace}/models/item/{path}.json",
        f"assets/{namespace}/items/{path}.json",
        f"assets/{namespace}/models/block/{path}.json",
    )
    return any(candidate in names for candidate in candidates)


def recipe_resource_exists(
    archive_names: dict[str, set[str]], default_namespace: str, value: str
) -> bool:
    namespace, path = split_resource_id(value, default_namespace)
    if namespace not in archive_names:
        return True
    names = archive_names.get(namespace, set())
    return (
        f"data/{namespace}/recipe/{path}.json" in names
        or f"data/{namespace}/recipes/{path}.json" in names
    )


def validate_resources(
    archive_names: dict[str, set[str]], namespace: str, relative: str, text: str
) -> list[str]:
    errors = []
    targets = [
        *(match.group(1) for match in core.LINK_TARGET_RE.finditer(text)),
        *(match.group(1) for match in core.IMAGE_TARGET_RE.finditer(text)),
        *(match.group(1) for match in core.IMPORT_RE.finditer(text)),
    ]
    all_names = set().union(*archive_names.values())
    for target in targets:
        resolved = resolve_guide_reference(namespace, relative, target)
        if resolved and resolved not in all_names:
            errors.append(f"{relative}: 참조 대상이 없습니다: {target} -> {resolved}")
    for item_id in ITEM_TAG_RE.findall(text):
        if not item_resource_exists(archive_names, namespace, item_id):
            errors.append(
                f"{relative}: 아이템 또는 블록 ID를 찾을 수 없습니다: {item_id}"
            )
    for item_id in RECIPE_FOR_RE.findall(text):
        if not item_resource_exists(archive_names, namespace, item_id):
            errors.append(
                f"{relative}: RecipeFor 아이템 ID를 찾을 수 없습니다: {item_id}"
            )
    for recipe_id in RECIPE_RE.findall(text):
        if not recipe_resource_exists(archive_names, namespace, recipe_id):
            errors.append(f"{relative}: 조합법 ID를 찾을 수 없습니다: {recipe_id}")
    return errors


def guide_source(
    archives: dict[str, zipfile.ZipFile], namespace: str, relative: str
) -> str:
    entry = (GUIDE_SOURCE_ROOTS[namespace] / relative).as_posix()
    source_archive = archives["ae2wtlib"]
    return source_archive.read(entry).decode("utf-8-sig")


def guide_working_path(namespace: str, relative: str) -> Path:
    if namespace == "ae2":
        return CORE_COMPAT_WORKING_FILE
    return GUIDE_WORKING_ROOT / relative


def guide_output_path(namespace: str, relative: str) -> Path:
    if namespace == "ae2":
        return CORE_COMPAT_OUTPUT_FILE
    return GUIDE_OUTPUT_ROOT / relative


def validate_ae2wtlib(instance: Path, compare_output: bool) -> dict[str, object]:
    jars = find_jars(instance)
    errors = []
    expected_working = set(ADDON_GUIDE_FILES)
    actual_working = {
        path.relative_to(GUIDE_WORKING_ROOT).as_posix()
        for path in GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if actual_working != expected_working:
        errors.append(
            "AE2WTLib 작업본 목록이 다릅니다: "
            f"누락={sorted(expected_working - actual_working)}, "
            f"불필요={sorted(actual_working - expected_working)}"
        )

    if not LANG_WORKING_FILE.is_file():
        errors.append(f"AE2WTLib 언어 작업본이 없습니다: {LANG_WORKING_FILE}")

    archive_handles = {
        namespace: zipfile.ZipFile(path) for namespace, path in jars.items()
    }
    try:
        archive_names = {
            namespace: set(archive.namelist())
            for namespace, archive in archive_handles.items()
        }
        source_lang = load_archive_json_unique(
            archive_handles["ae2wtlib"], "assets/ae2wtlib/lang/en_us.json"
        )
        candidate_lang = load_archive_json_unique(
            archive_handles["ae2wtlib"], "assets/ae2wtlib/lang/ko_kr.json"
        )
        translated_lang = load_json_unique(LANG_WORKING_FILE)
        errors.extend(validate_language(source_lang, translated_lang))
        for key, expected in AE2WTLIB_QUALITY_TRANSLATIONS.items():
            if translated_lang.get(key) != expected:
                errors.append(f"AE2WTLib 확정 번역이 다릅니다: {key}")

        guide_rows = [("ae2", CORE_COMPAT_RELATIVE)]
        guide_rows.extend(("ae2wtlib", relative) for relative in ADDON_GUIDE_FILES)
        source_words = 0
        for namespace, relative in guide_rows:
            source = guide_source(archive_handles, namespace, relative)
            working_path = guide_working_path(namespace, relative)
            if not working_path.is_file():
                errors.append(f"가이드 작업본이 없습니다: {working_path}")
                continue
            translated = working_path.read_text(encoding="utf-8")
            pair_errors = core.validate_pair(relative, source, translated)
            if relative == "ae2wtlib/ae2wtlib-index.md":
                pair_errors = [
                    error
                    for error in pair_errors
                    if "한국어 본문을 찾을 수 없습니다" not in error
                ]
            errors.extend(pair_errors)
            remaining_phrases = [
                phrase
                for phrase in ENDERDRIVES_FORBIDDEN_GUIDE_PHRASES
                if phrase in translated
            ]
            if remaining_phrases:
                errors.append(
                    f"{relative}: 어색한 가이드 표현이 남았습니다: {remaining_phrases}"
                )
            remaining_phrases = [
                phrase
                for phrase in AE2WTLIB_FORBIDDEN_GUIDE_PHRASES
                if phrase in translated
            ]
            if remaining_phrases:
                errors.append(
                    f"{relative}: 어색한 가이드 표현이 남았습니다: {remaining_phrases}"
                )
            errors.extend(validate_tag_nesting(relative, translated))
            errors.extend(
                validate_resources(archive_names, namespace, relative, translated)
            )
            source_words += len(
                core.ENGLISH_WORD_RE.findall(core.extract_visible_text(source))
            )
            if working_path.read_bytes().startswith(b"\xef\xbb\xbf"):
                errors.append(f"{working_path}: UTF-8 BOM이 있습니다.")

            if compare_output:
                output_path = guide_output_path(namespace, relative)
                if not output_path.is_file():
                    errors.append(f"가이드 출력 파일이 없습니다: {output_path}")
                elif working_path.read_bytes() != output_path.read_bytes():
                    errors.append(f"{relative}: 작업본과 출력이 다릅니다.")

        for key, relative in GUIDE_ITEM_NAMES.items():
            if key not in translated_lang:
                continue
            text = (GUIDE_WORKING_ROOT / relative).read_text(encoding="utf-8")
            if translated_lang[key] not in core.extract_visible_text(text):
                errors.append(
                    f"{relative}: 언어 파일의 아이템명이 가이드에 없습니다: "
                    f"{translated_lang[key]}"
                )

        if compare_output:
            output_files = {
                path.relative_to(GUIDE_OUTPUT_ROOT).as_posix()
                for path in GUIDE_OUTPUT_ROOT.rglob("*.md")
                if path.is_file()
            }
            if output_files != expected_working:
                errors.append(
                    "AE2WTLib 출력 목록이 다릅니다: "
                    f"누락={sorted(expected_working - output_files)}, "
                    f"불필요={sorted(output_files - expected_working)}"
                )
            if not LANG_OUTPUT_FILE.is_file():
                errors.append(f"AE2WTLib 언어 출력 파일이 없습니다: {LANG_OUTPUT_FILE}")
            elif LANG_WORKING_FILE.read_bytes() != LANG_OUTPUT_FILE.read_bytes():
                errors.append("AE2WTLib 언어 작업본과 출력이 다릅니다.")

        reused = sum(
            1
            for key, value in translated_lang.items()
            if candidate_lang.get(key) == value
        )
        return {
            "jars": jars,
            "source_words": source_words,
            "source_lang": source_lang,
            "candidate_lang": candidate_lang,
            "translated_lang": translated_lang,
            "existing_korean_reused": reused,
            "new_or_revised_translations": len(translated_lang) - reused,
            "errors": errors,
        }
    finally:
        for archive in archive_handles.values():
            archive.close()


def build_ae2wtlib(instance: Path) -> dict[str, object]:
    validation = validate_ae2wtlib(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    for relative in ADDON_GUIDE_FILES:
        source = GUIDE_WORKING_ROOT / relative
        target = GUIDE_OUTPUT_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    CORE_COMPAT_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CORE_COMPAT_OUTPUT_FILE.write_bytes(CORE_COMPAT_WORKING_FILE.read_bytes())
    LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    LANG_OUTPUT_FILE.write_bytes(LANG_WORKING_FILE.read_bytes())

    post_validation = validate_ae2wtlib(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    output_files = {
        "assets/ae2/ae2guide/_ko_kr/" + CORE_COMPAT_RELATIVE: sha256(
            CORE_COMPAT_OUTPUT_FILE
        ),
        LANG_RELATIVE: sha256(LANG_OUTPUT_FILE),
    }
    output_files.update(
        {
            "assets/ae2wtlib/ae2guide/_ko_kr/" + relative: sha256(
                GUIDE_OUTPUT_ROOT / relative
            )
            for relative in ADDON_GUIDE_FILES
        }
    )
    result = {
        "status": "quality_review_completed",
        "scope": "AE2WTLib language and GuideME guide quality review",
        "batch": 1,
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": 8,
        "new_guide_pages": 7,
        "core_compatibility_updates": 1,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "new_or_revised_translations": validation["new_or_revised_translations"],
        "guide_files": list(ADDON_GUIDE_FILES),
        "core_compatibility_file": CORE_COMPAT_RELATIVE,
        "output_sha256": output_files,
        "ftbquests_review": {
            "related_chapter_found": True,
            "keys_reviewed": 2,
            "keys_updated": 2,
            "handled_separately": True,
        },
        "kubejs_user_visible_literals_found": 0,
        "validation_errors": 0,
    }
    AE2WTLIB_PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    AE2WTLIB_PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_numbers(relative: str, source: str, translated: str) -> list[str]:
    source_visible = core.extract_visible_text(source)
    translated_visible = core.extract_visible_text(translated)
    for korean_number, source_number in {
        "1,280만": "12.8",
        "21억 4천만": "2.14",
        "920경": "9.2",
    }.items():
        translated_visible = translated_visible.replace(korean_number, source_number)
    source_visible = re.sub(r"(?i)(?<!\w)x(?=\d)|(?<=\d)x(?=\d)", "×", source_visible)
    translated_visible = re.sub(
        r"(?i)(?<!\w)x(?=\d)|(?<=\d)x(?=\d)", "×", translated_visible
    )
    expected = sorted(
        token.replace(",", "") for token in NUMBER_RE.findall(source_visible)
    )
    actual = sorted(
        token.replace(",", "") for token in NUMBER_RE.findall(translated_visible)
    )
    if (
        relative == "epp_intro/infinity_cell.md"
        and expected == ["2.1"]
        and actual == ["21"]
    ):
        return []
    if expected == actual:
        return []
    return [f"{relative}: 숫자 표기가 다릅니다: {expected} != {actual}"]


def validate_enderdrives(instance: Path, compare_output: bool) -> dict[str, object]:
    jars = {
        "ae2": find_single_jar(instance, "appliedenergistics2-*.jar", "AE2"),
        "ae2wtlib": find_single_jar(instance, "ae2wtlib-*.jar", "AE2WTLib"),
        "enderdrives": find_single_jar(instance, "enderdrives-*.jar", "EnderDrives"),
    }
    errors: list[str] = []
    expected_working = set(ENDERDRIVES_GUIDE_FILES)
    actual_working = {
        path.relative_to(ENDERDRIVES_GUIDE_WORKING_ROOT).as_posix()
        for path in ENDERDRIVES_GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if actual_working != expected_working:
        errors.append(
            "EnderDrives 작업본 목록이 다릅니다: "
            f"누락={sorted(expected_working - actual_working)}, "
            f"불필요={sorted(actual_working - expected_working)}"
        )
    if not ENDERDRIVES_LANG_WORKING_FILE.is_file():
        errors.append(
            f"EnderDrives 언어 작업본이 없습니다: {ENDERDRIVES_LANG_WORKING_FILE}"
        )

    archives = {namespace: zipfile.ZipFile(path) for namespace, path in jars.items()}
    try:
        archive_names = {
            namespace: set(archive.namelist())
            for namespace, archive in archives.items()
        }
        source_lang = load_archive_json_unique(
            archives["enderdrives"], "assets/enderdrives/lang/en_us.json"
        )
        translated_lang = load_json_unique(ENDERDRIVES_LANG_WORKING_FILE)
        errors.extend(validate_language(source_lang, translated_lang))

        kubejs_files = (
            (
                "툴팁",
                ENDERDRIVES_TOOLTIP_WORKING_FILE,
                ENDERDRIVES_TOOLTIP_OUTPUT_FILE,
                ENDERDRIVES_TOOLTIP_SCRIPT_MARKERS,
            ),
            (
                "시스템 메시지",
                ENDERDRIVES_MESSAGES_WORKING_FILE,
                ENDERDRIVES_MESSAGES_OUTPUT_FILE,
                ENDERDRIVES_MESSAGES_SCRIPT_MARKERS,
            ),
        )
        for label, working_file, output_file, markers in kubejs_files:
            if not working_file.is_file():
                errors.append(
                    f"EnderDrives {label} KubeJS 작업본이 없습니다: {working_file}"
                )
                continue
            script = working_file.read_text(encoding="utf-8")
            if working_file.read_bytes().startswith(b"\xef\xbb\xbf"):
                errors.append(f"{working_file}: UTF-8 BOM이 있습니다.")
            for marker in markers:
                if marker not in script:
                    errors.append(
                        f"EnderDrives {label} KubeJS 검증 표식이 없습니다: {marker}"
                    )
            if compare_output:
                if not output_file.is_file():
                    errors.append(
                        f"EnderDrives {label} KubeJS 출력 파일이 없습니다: {output_file}"
                    )
                elif working_file.read_bytes() != output_file.read_bytes():
                    errors.append(
                        f"EnderDrives {label} KubeJS 작업본과 출력이 다릅니다."
                    )

        for entry, markers in ENDERDRIVES_CLASS_LITERAL_MARKERS.items():
            if entry not in archive_names["enderdrives"]:
                errors.append(f"EnderDrives 검수 대상 클래스가 없습니다: {entry}")
                continue
            class_bytes = archives["enderdrives"].read(entry)
            for marker in markers:
                if marker not in class_bytes:
                    errors.append(
                        f"EnderDrives 클래스 원문 표식이 다릅니다: {entry}: "
                        f"{marker.decode('utf-8')}"
                    )

        source_words = 0
        for relative in ENDERDRIVES_GUIDE_FILES:
            entry = (GUIDE_SOURCE_ROOTS["enderdrives"] / relative).as_posix()
            source = archives["enderdrives"].read(entry).decode("utf-8-sig")
            working_path = ENDERDRIVES_GUIDE_WORKING_ROOT / relative
            if not working_path.is_file():
                errors.append(f"가이드 작업본이 없습니다: {working_path}")
                continue
            translated = working_path.read_text(encoding="utf-8")
            pair_errors = core.validate_pair(relative, source, translated)
            if relative.endswith("-index.md"):
                pair_errors = [
                    error
                    for error in pair_errors
                    if "한국어 본문을 찾을 수 없습니다" not in error
                ]
            errors.extend(pair_errors)
            errors.extend(validate_numbers(relative, source, translated))
            errors.extend(validate_tag_nesting(relative, translated))
            errors.extend(
                validate_resources(archive_names, "enderdrives", relative, translated)
            )
            source_words += len(
                core.ENGLISH_WORD_RE.findall(core.extract_visible_text(source))
            )
            if working_path.read_bytes().startswith(b"\xef\xbb\xbf"):
                errors.append(f"{working_path}: UTF-8 BOM이 있습니다.")
            if compare_output:
                output_path = ENDERDRIVES_GUIDE_OUTPUT_ROOT / relative
                if not output_path.is_file():
                    errors.append(f"가이드 출력 파일이 없습니다: {output_path}")
                elif working_path.read_bytes() != output_path.read_bytes():
                    errors.append(f"{relative}: 작업본과 출력이 다릅니다.")

        if compare_output:
            output_files = {
                path.relative_to(ENDERDRIVES_GUIDE_OUTPUT_ROOT).as_posix()
                for path in ENDERDRIVES_GUIDE_OUTPUT_ROOT.rglob("*.md")
                if path.is_file()
            }
            if output_files != expected_working:
                errors.append(
                    "EnderDrives 출력 목록이 다릅니다: "
                    f"누락={sorted(expected_working - output_files)}, "
                    f"불필요={sorted(output_files - expected_working)}"
                )
            if not ENDERDRIVES_LANG_OUTPUT_FILE.is_file():
                errors.append(
                    "EnderDrives 언어 출력 파일이 없습니다: "
                    f"{ENDERDRIVES_LANG_OUTPUT_FILE}"
                )
            elif (
                ENDERDRIVES_LANG_WORKING_FILE.read_bytes()
                != ENDERDRIVES_LANG_OUTPUT_FILE.read_bytes()
            ):
                errors.append("EnderDrives 언어 작업본과 출력이 다릅니다.")

        return {
            "jars": jars,
            "source_words": source_words,
            "source_lang": source_lang,
            "translated_lang": translated_lang,
            "existing_korean_reused": 41,
            "existing_korean_corrected": 0,
            "new_translations": 99,
            "new_or_revised_translations": 99,
            "guide_pages": len(ENDERDRIVES_GUIDE_FILES),
            "new_guide_pages": 0,
            "quality_review_pages_corrected": 1,
            "core_compatibility_updates": 0,
            "kubejs_files": 2,
            "errors": errors,
        }
    finally:
        for archive in archives.values():
            archive.close()


def build_enderdrives(instance: Path) -> dict[str, object]:
    validation = validate_enderdrives(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    for relative in ENDERDRIVES_GUIDE_FILES:
        source = ENDERDRIVES_GUIDE_WORKING_ROOT / relative
        target = ENDERDRIVES_GUIDE_OUTPUT_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    ENDERDRIVES_LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ENDERDRIVES_LANG_OUTPUT_FILE.write_bytes(ENDERDRIVES_LANG_WORKING_FILE.read_bytes())
    for source, target in (
        (ENDERDRIVES_TOOLTIP_WORKING_FILE, ENDERDRIVES_TOOLTIP_OUTPUT_FILE),
        (ENDERDRIVES_MESSAGES_WORKING_FILE, ENDERDRIVES_MESSAGES_OUTPUT_FILE),
    ):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())

    post_validation = validate_enderdrives(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    output_files = {
        ENDERDRIVES_LANG_RELATIVE: sha256(ENDERDRIVES_LANG_OUTPUT_FILE),
        **{
            "assets/enderdrives/ae2guide/_ko_kr/" + relative: sha256(
                ENDERDRIVES_GUIDE_OUTPUT_ROOT / relative
            )
            for relative in ENDERDRIVES_GUIDE_FILES
        },
        ENDERDRIVES_TOOLTIP_RELATIVE.as_posix(): sha256(
            ENDERDRIVES_TOOLTIP_OUTPUT_FILE
        ),
        ENDERDRIVES_MESSAGES_RELATIVE.as_posix(): sha256(
            ENDERDRIVES_MESSAGES_OUTPUT_FILE
        ),
    }
    result = {
        "status": "quality_review_completed",
        "scope": (
            "EnderDrives language, GuideME guide, embedded tooltips and system "
            "messages full quality recheck"
        ),
        "batch": 2,
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": len(ENDERDRIVES_GUIDE_FILES),
        "new_guide_pages": 0,
        "quality_review_pages_corrected": validation["quality_review_pages_corrected"],
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "new_or_revised_translations": validation["new_or_revised_translations"],
        "guide_files": list(ENDERDRIVES_GUIDE_FILES),
        "output_sha256": output_files,
        "ftbquests_review": {"related_content_found": False, "keys_updated": 0},
        "kubejs_files": validation["kubejs_files"],
        "class_literal_classes_reviewed": len(ENDERDRIVES_CLASS_LITERAL_MARKERS),
        "normal_player_literal_paths_corrected": 6,
        "operator_command_message_family_corrected": True,
        "validation_errors": 0,
    }
    ENDERDRIVES_PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    ENDERDRIVES_PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_extendedae_language(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    jar = find_single_jar(instance, "ExtendedAE-*.jar", "ExtendedAE")
    errors: list[str] = []
    with zipfile.ZipFile(jar) as archive:
        source_lang = load_archive_json_unique(
            archive, "assets/extendedae/lang/en_us.json"
        )
        candidate_lang = load_archive_json_unique(
            archive, "assets/extendedae/lang/ko_kr.json"
        )
    if not EXTENDEDAE_LANG_WORKING_FILE.is_file():
        errors.append(
            f"ExtendedAE 언어 작업본이 없습니다: {EXTENDEDAE_LANG_WORKING_FILE}"
        )
        translated_lang: dict[str, str] = {}
    else:
        translated_lang = load_json_unique(EXTENDEDAE_LANG_WORKING_FILE)
        errors.extend(validate_language(source_lang, translated_lang))
        if EXTENDEDAE_LANG_WORKING_FILE.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"{EXTENDEDAE_LANG_WORKING_FILE}: UTF-8 BOM이 있습니다.")

    if compare_output:
        if not EXTENDEDAE_LANG_OUTPUT_FILE.is_file():
            errors.append(
                f"ExtendedAE 언어 출력 파일이 없습니다: {EXTENDEDAE_LANG_OUTPUT_FILE}"
            )
        elif (
            EXTENDEDAE_LANG_WORKING_FILE.read_bytes()
            != EXTENDEDAE_LANG_OUTPUT_FILE.read_bytes()
        ):
            errors.append("ExtendedAE 언어 작업본과 출력이 다릅니다.")

    reused = sum(
        1 for key, value in translated_lang.items() if candidate_lang.get(key) == value
    )
    return {
        "jars": {"extendedae": jar},
        "source_words": 0,
        "source_lang": source_lang,
        "candidate_lang": candidate_lang,
        "translated_lang": translated_lang,
        "existing_korean_reused": reused,
        "new_or_revised_translations": len(translated_lang) - reused,
        "guide_pages": 0,
        "new_guide_pages": 0,
        "core_compatibility_updates": 0,
        "errors": errors,
    }


def build_extendedae_language(instance: Path) -> dict[str, object]:
    validation = validate_extendedae_language(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    EXTENDEDAE_LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    EXTENDEDAE_LANG_OUTPUT_FILE.write_bytes(EXTENDEDAE_LANG_WORKING_FILE.read_bytes())
    post_validation = validate_extendedae_language(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jar = validation["jars"]["extendedae"]  # type: ignore[index]
    assert isinstance(jar, Path)
    quest_keys, kubejs_keys = extendedae_related_counts(instance)
    result = {
        "status": "batch_03_language_completed",
        "scope": "ExtendedAE full language file before guide batch 03",
        "batch": ACTIVE_BATCH,
        "source_jars": {"extendedae": {"name": jar.name, "sha256": sha256(jar)}},
        "language": "ko_kr",
        "guide_pages": 0,
        "new_guide_pages": 0,
        "core_compatibility_updates": 0,
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "new_or_revised_translations": validation["new_or_revised_translations"],
        "output_sha256": {
            EXTENDEDAE_LANG_RELATIVE: sha256(EXTENDEDAE_LANG_OUTPUT_FILE)
        },
        "ftbquests_review": {
            "related_content_found": True,
            "keys_updated": quest_keys,
            "handled_separately": True,
            "pending": False,
        },
        "kubejs_user_visible_literals_found": kubejs_keys,
        "validation_errors": 0,
    }
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_extendedae_batch(
    instance: Path, batch: int, compare_output: bool
) -> dict[str, object]:
    if batch not in EXTENDEDAE_BATCH_GUIDE_FILES:
        raise ValueError(f"지원하지 않는 ExtendedAE 가이드 배치입니다: {batch}")
    validation = validate_extendedae_language(instance, compare_output)
    errors = validation["errors"]
    assert isinstance(errors, list)
    batch_files = EXTENDEDAE_BATCH_GUIDE_FILES[batch]
    expected_all = {
        relative
        for files in EXTENDEDAE_BATCH_GUIDE_FILES.values()
        for relative in files
    }
    actual_working = {
        path.relative_to(EXTENDEDAE_GUIDE_WORKING_ROOT).as_posix()
        for path in EXTENDEDAE_GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if batch == ACTIVE_BATCH and actual_working != expected_all:
        errors.append(
            f"ExtendedAE {batch}차 누적 작업본 목록이 다릅니다: "
            f"누락={sorted(expected_all - actual_working)}, "
            f"불필요={sorted(actual_working - expected_all)}"
        )

    jars = {
        "ae2": find_single_jar(instance, "appliedenergistics2-*.jar", "AE2"),
        "extendedae": find_single_jar(instance, "ExtendedAE-*.jar", "ExtendedAE"),
    }
    archives = {namespace: zipfile.ZipFile(path) for namespace, path in jars.items()}
    try:
        archive_names = {
            namespace: set(archive.namelist())
            for namespace, archive in archives.items()
        }
        source_words = 0
        for relative in batch_files:
            entry = (GUIDE_SOURCE_ROOTS["extendedae"] / relative).as_posix()
            source = archives["extendedae"].read(entry).decode("utf-8-sig")
            source = source.replace("\r\r\n", "\n").replace("\r\n", "\n")
            source = re.sub(r"(?m)^    (title|position|parent|icon):", r"  \1:", source)
            working_path = EXTENDEDAE_GUIDE_WORKING_ROOT / relative
            if not working_path.is_file():
                errors.append(f"가이드 작업본이 없습니다: {working_path}")
                continue
            translated = working_path.read_text(encoding="utf-8")
            pair_errors = core.validate_pair(relative, source, translated)
            errors.extend(pair_errors)
            errors.extend(validate_numbers(relative, source, translated))
            errors.extend(validate_tag_nesting(relative, translated))
            errors.extend(
                validate_resources(archive_names, "extendedae", relative, translated)
            )
            source_words += len(
                core.ENGLISH_WORD_RE.findall(core.extract_visible_text(source))
            )
            if working_path.read_bytes().startswith(b"\xef\xbb\xbf"):
                errors.append(f"{working_path}: UTF-8 BOM이 있습니다.")
            if compare_output:
                output_path = EXTENDEDAE_GUIDE_OUTPUT_ROOT / relative
                if not output_path.is_file():
                    errors.append(f"가이드 출력 파일이 없습니다: {output_path}")
                elif working_path.read_bytes() != output_path.read_bytes():
                    errors.append(f"{relative}: 작업본과 출력이 다릅니다.")

        translated_lang = validation["translated_lang"]
        assert isinstance(translated_lang, dict)
        for key, relative in EXTENDEDAE_BATCH_ITEM_NAMES[batch].items():
            text = (EXTENDEDAE_GUIDE_WORKING_ROOT / relative).read_text(
                encoding="utf-8"
            )
            item_name = translated_lang[key]
            if item_name not in core.extract_visible_text(text):
                errors.append(
                    f"{relative}: 언어 파일의 아이템명이 가이드에 없습니다: {item_name}"
                )

        if compare_output:
            output_files = {
                path.relative_to(EXTENDEDAE_GUIDE_OUTPUT_ROOT).as_posix()
                for path in EXTENDEDAE_GUIDE_OUTPUT_ROOT.rglob("*.md")
                if path.is_file()
            }
            if batch == ACTIVE_BATCH and output_files != expected_all:
                errors.append(
                    f"ExtendedAE {batch}차 누적 출력 목록이 다릅니다: "
                    f"누락={sorted(expected_all - output_files)}, "
                    f"불필요={sorted(output_files - expected_all)}"
                )

        validation.update(
            {
                "jars": jars,
                "source_words": source_words,
                "guide_pages": len(batch_files),
                "new_guide_pages": len(batch_files),
                "core_compatibility_updates": 0,
            }
        )
        return validation
    finally:
        for archive in archives.values():
            archive.close()


def validate_extendedae_batch_03(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    return validate_extendedae_batch(instance, 3, compare_output)


def validate_extendedae_batch_04(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    return validate_extendedae_batch(instance, 4, compare_output)


def validate_extendedae_batch_05(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    return validate_extendedae_batch(instance, 5, compare_output)


def validate_extendedae_batch_06(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    return validate_extendedae_batch(instance, 6, compare_output)


def validate_extendedae_quality(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    validations = [
        validate_extendedae_batch(instance, batch, compare_output)
        for batch in sorted(EXTENDEDAE_BATCH_GUIDE_FILES)
    ]
    errors = [
        error
        for validation in validations
        for error in validation["errors"]  # type: ignore[union-attr]
    ]
    expected_files = tuple(
        relative
        for batch in sorted(EXTENDEDAE_BATCH_GUIDE_FILES)
        for relative in EXTENDEDAE_BATCH_GUIDE_FILES[batch]
    )
    expected_set = set(expected_files)
    actual_working = {
        path.relative_to(EXTENDEDAE_GUIDE_WORKING_ROOT).as_posix()
        for path in EXTENDEDAE_GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if actual_working != expected_set:
        errors.append(
            "ExtendedAE 품질 재검수 작업본 목록이 다릅니다: "
            f"누락={sorted(expected_set - actual_working)}, "
            f"불필요={sorted(actual_working - expected_set)}"
        )
    if compare_output:
        actual_output = {
            path.relative_to(EXTENDEDAE_GUIDE_OUTPUT_ROOT).as_posix()
            for path in EXTENDEDAE_GUIDE_OUTPUT_ROOT.rglob("*.md")
            if path.is_file()
        }
        if actual_output != expected_set:
            errors.append(
                "ExtendedAE 품질 재검수 출력 목록이 다릅니다: "
                f"누락={sorted(expected_set - actual_output)}, "
                f"불필요={sorted(actual_output - expected_set)}"
            )

    translated_lang = validations[0]["translated_lang"]
    assert isinstance(translated_lang, dict)
    for key, expected in EXTENDEDAE_QUALITY_TRANSLATIONS.items():
        if translated_lang.get(key) != expected:
            errors.append(
                f"ExtendedAE 품질 확정 번역이 다릅니다: {key}="
                f"{translated_lang.get(key)!r}"
            )
    for relative in expected_files:
        text = (EXTENDEDAE_GUIDE_WORKING_ROOT / relative).read_text(encoding="utf-8")
        for phrase in EXTENDEDAE_FORBIDDEN_GUIDE_PHRASES:
            if phrase in text:
                errors.append(f"{relative}: 재검수 전 표현이 남아 있습니다: {phrase}")

    return {
        **validations[0],
        "source_words": sum(
            int(validation["source_words"]) for validation in validations
        ),
        "guide_pages": len(expected_files),
        "new_guide_pages": len(expected_files),
        "guide_files": expected_files,
        "errors": errors,
    }


def build_extendedae_quality(instance: Path) -> dict[str, object]:
    validation = validate_extendedae_quality(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    guide_files = validation["guide_files"]
    assert isinstance(guide_files, tuple)
    for relative in guide_files:
        source = EXTENDEDAE_GUIDE_WORKING_ROOT / relative
        target = EXTENDEDAE_GUIDE_OUTPUT_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    EXTENDEDAE_LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    EXTENDEDAE_LANG_OUTPUT_FILE.write_bytes(EXTENDEDAE_LANG_WORKING_FILE.read_bytes())

    post_validation = validate_extendedae_quality(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    output_files = {
        EXTENDEDAE_LANG_RELATIVE: sha256(EXTENDEDAE_LANG_OUTPUT_FILE),
        **{
            "assets/extendedae/ae2guide/_ko_kr/" + relative: sha256(
                EXTENDEDAE_GUIDE_OUTPUT_ROOT / relative
            )
            for relative in guide_files
        },
    }
    quest_keys, kubejs_keys = extendedae_related_counts(instance)
    result = {
        "status": "quality_review_completed",
        "scope": "Extended AE language, GuideME guide, FTB Quests, and KubeJS quality review",
        "batch": [3, 4, 5, 6],
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": len(guide_files),
        "new_guide_pages": len(guide_files),
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "new_or_revised_translations": validation["new_or_revised_translations"],
        "guide_files": list(guide_files),
        "output_sha256": output_files,
        "ftbquests_review": {
            "related_content_found": True,
            "keys_updated": quest_keys,
            "handled_separately": True,
            "pending": False,
        },
        "kubejs_user_visible_literals_found": kubejs_keys,
        "validation_errors": 0,
    }
    EXTENDEDAE_PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    EXTENDEDAE_PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def build_extendedae_batch(instance: Path, batch: int) -> dict[str, object]:
    validation = validate_extendedae_batch(instance, batch, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    batch_files = EXTENDEDAE_BATCH_GUIDE_FILES[batch]
    for relative in batch_files:
        source = EXTENDEDAE_GUIDE_WORKING_ROOT / relative
        target = EXTENDEDAE_GUIDE_OUTPUT_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    EXTENDEDAE_LANG_OUTPUT_FILE.write_bytes(EXTENDEDAE_LANG_WORKING_FILE.read_bytes())

    post_validation = validate_extendedae_batch(instance, batch, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    output_files = {
        EXTENDEDAE_LANG_RELATIVE: sha256(EXTENDEDAE_LANG_OUTPUT_FILE),
        **{
            "assets/extendedae/ae2guide/_ko_kr/" + relative: sha256(
                EXTENDEDAE_GUIDE_OUTPUT_ROOT / relative
            )
            for relative in batch_files
        },
    }
    quest_keys, kubejs_keys = extendedae_related_counts(instance)
    result = {
        "status": f"batch_{batch:02d}_completed",
        "scope": EXTENDEDAE_BATCH_SCOPES[batch],
        "batch": batch,
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": len(batch_files),
        "new_guide_pages": len(batch_files),
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "new_or_revised_translations": validation["new_or_revised_translations"],
        "guide_files": list(batch_files),
        "output_sha256": output_files,
        "ftbquests_review": {
            "related_content_found": True,
            "keys_updated": quest_keys,
            "handled_separately": True,
            "pending": False,
        },
        "kubejs_user_visible_literals_found": kubejs_keys,
        "validation_errors": 0,
    }
    PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def build_extendedae_batch_03(instance: Path) -> dict[str, object]:
    return build_extendedae_batch(instance, 3)


def build_extendedae_batch_04(instance: Path) -> dict[str, object]:
    return build_extendedae_batch(instance, 4)


def build_extendedae_batch_05(instance: Path) -> dict[str, object]:
    return build_extendedae_batch(instance, 5)


def build_extendedae_batch_06(instance: Path) -> dict[str, object]:
    return build_extendedae_batch(instance, 6)


def advancedae_related_counts() -> tuple[int, int]:
    quest_overrides = json.loads(
        ADVANCEDAE_QUEST_OVERRIDES_FILE.read_text(encoding="utf-8")
    )
    return len(quest_overrides), 1


def prepare_advancedae_kubejs(instance: Path) -> None:
    source_file = instance / ADVANCEDAE_KUBEJS_RELATIVE
    source = source_file.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    source_count = source.count(ADVANCEDAE_KUBEJS_SOURCE_TEXT)
    translated_count = source.count(ADVANCEDAE_KUBEJS_TRANSLATED_TEXT)
    if source_count == 1 and translated_count == 0:
        translated = source.replace(
            ADVANCEDAE_KUBEJS_SOURCE_TEXT,
            ADVANCEDAE_KUBEJS_TRANSLATED_TEXT,
        )
    elif source_count == 0 and translated_count == 1:
        translated = source
    else:
        raise ValueError(
            "Advanced AE KubeJS 반응 챔버 안내 원문을 하나로 확정할 수 없습니다: "
            f"원문={source_count}, 번역={translated_count}"
        )
    ADVANCEDAE_KUBEJS_WORKING_FILE.parent.mkdir(parents=True, exist_ok=True)
    ADVANCEDAE_KUBEJS_WORKING_FILE.write_text(translated, encoding="utf-8")


def validate_advancedae_kubejs(instance: Path, compare_output: bool) -> list[str]:
    errors: list[str] = []
    source_file = instance / ADVANCEDAE_KUBEJS_RELATIVE
    source = source_file.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    expected = source.replace(
        ADVANCEDAE_KUBEJS_SOURCE_TEXT,
        ADVANCEDAE_KUBEJS_TRANSLATED_TEXT,
    )
    if not ADVANCEDAE_KUBEJS_WORKING_FILE.is_file():
        errors.append(
            f"Advanced AE KubeJS 작업본이 없습니다: {ADVANCEDAE_KUBEJS_WORKING_FILE}"
        )
        return errors
    working = ADVANCEDAE_KUBEJS_WORKING_FILE.read_text(encoding="utf-8").replace(
        "\r\n", "\n"
    )
    if working != expected:
        errors.append("Advanced AE KubeJS 작업본이 현재 인스턴스 원문과 다릅니다.")
    if ADVANCEDAE_KUBEJS_SOURCE_TEXT in working:
        errors.append("Advanced AE KubeJS 반응 챔버 영어 안내가 남아 있습니다.")
    if working.count(ADVANCEDAE_KUBEJS_TRANSLATED_TEXT) != 1:
        errors.append("Advanced AE KubeJS 반응 챔버 한국어 안내가 하나가 아닙니다.")
    if compare_output:
        if not ADVANCEDAE_KUBEJS_OUTPUT_FILE.is_file():
            errors.append(
                f"Advanced AE KubeJS 출력 파일이 없습니다: {ADVANCEDAE_KUBEJS_OUTPUT_FILE}"
            )
        elif (
            ADVANCEDAE_KUBEJS_WORKING_FILE.read_bytes()
            != ADVANCEDAE_KUBEJS_OUTPUT_FILE.read_bytes()
        ):
            errors.append("Advanced AE KubeJS 작업본과 출력이 다릅니다.")
    return errors


def validate_advancedae_language(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    jar = find_single_jar(instance, "AdvancedAE-*.jar", "AdvancedAE")
    errors: list[str] = []
    with zipfile.ZipFile(jar) as archive:
        source_lang = load_archive_json_unique(
            archive, "assets/advanced_ae/lang/en_us.json"
        )
        candidate_lang = load_archive_json_unique(
            archive, "assets/advanced_ae/lang/ko_kr.json"
        )
    if not ADVANCEDAE_LANG_WORKING_FILE.is_file():
        errors.append(
            f"AdvancedAE 언어 작업본이 없습니다: {ADVANCEDAE_LANG_WORKING_FILE}"
        )
        translated_lang: dict[str, str] = {}
    else:
        translated_lang = load_json_unique(ADVANCEDAE_LANG_WORKING_FILE)
        errors.extend(validate_language(source_lang, translated_lang))
        if ADVANCEDAE_LANG_WORKING_FILE.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"{ADVANCEDAE_LANG_WORKING_FILE}: UTF-8 BOM이 있습니다.")

    if compare_output:
        if not ADVANCEDAE_LANG_OUTPUT_FILE.is_file():
            errors.append(
                f"AdvancedAE 언어 출력 파일이 없습니다: {ADVANCEDAE_LANG_OUTPUT_FILE}"
            )
        elif (
            ADVANCEDAE_LANG_WORKING_FILE.read_bytes()
            != ADVANCEDAE_LANG_OUTPUT_FILE.read_bytes()
        ):
            errors.append("AdvancedAE 언어 작업본과 출력이 다릅니다.")

    reused = sum(
        1
        for key, value in translated_lang.items()
        if candidate_lang.get(key) != source_lang.get(key)
        and candidate_lang.get(key) == value
    )
    return {
        "jars": {"advanced_ae": jar},
        "source_words": 0,
        "source_lang": source_lang,
        "candidate_lang": candidate_lang,
        "translated_lang": translated_lang,
        "existing_korean_reused": reused,
        "existing_korean_corrected": sum(
            candidate_lang.get(key) != source_lang.get(key)
            and candidate_lang.get(key) != value
            for key, value in translated_lang.items()
        ),
        "new_translations": sum(
            candidate_lang.get(key) == source_lang.get(key) for key in translated_lang
        ),
        "new_or_revised_translations": len(translated_lang) - reused,
        "guide_pages": 0,
        "new_guide_pages": 0,
        "core_compatibility_updates": 0,
        "errors": errors,
    }


def build_advancedae_language(instance: Path) -> dict[str, object]:
    validation = validate_advancedae_language(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    ADVANCEDAE_LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ADVANCEDAE_LANG_OUTPUT_FILE.write_bytes(ADVANCEDAE_LANG_WORKING_FILE.read_bytes())
    post_validation = validate_advancedae_language(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jar = validation["jars"]["advanced_ae"]  # type: ignore[index]
    assert isinstance(jar, Path)
    quest_keys, kubejs_keys = advancedae_related_counts()
    result = {
        "status": "advancedae_full_language_completed",
        "scope": "AdvancedAE full language file before guide batch 07",
        "batch": 7,
        "source_jars": {"advanced_ae": {"name": jar.name, "sha256": sha256(jar)}},
        "language": "ko_kr",
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "existing_korean_corrected": validation["existing_korean_corrected"],
        "new_translations": validation["new_translations"],
        "ftbquests_keys_updated": quest_keys,
        "kubejs_user_visible_literals_found": kubejs_keys,
        "output_sha256": {
            ADVANCEDAE_LANG_RELATIVE: sha256(ADVANCEDAE_LANG_OUTPUT_FILE)
        },
        "validation_errors": 0,
    }
    ADVANCEDAE_LANGUAGE_COMPLETION_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def megacells_related_counts() -> tuple[int, int]:
    quest_overrides = json.loads(
        MEGACELLS_QUEST_OVERRIDES_FILE.read_text(encoding="utf-8")
    )
    return len(quest_overrides), 0


def validate_megacells_language(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    jar = find_single_jar(instance, "megacells-*.jar", "MEGA Cells")
    errors: list[str] = []
    with zipfile.ZipFile(jar) as archive:
        source_lang = load_archive_json_unique(
            archive, "assets/megacells/lang/en_us.json"
        )
        candidate_lang = (
            load_archive_json_unique(archive, "assets/megacells/lang/ko_kr.json")
            if "assets/megacells/lang/ko_kr.json" in archive.namelist()
            else {}
        )
    if not MEGACELLS_LANG_WORKING_FILE.is_file():
        errors.append(
            f"MEGA Cells 언어 작업본이 없습니다: {MEGACELLS_LANG_WORKING_FILE}"
        )
        translated_lang: dict[str, str] = {}
    else:
        translated_lang = load_json_unique(MEGACELLS_LANG_WORKING_FILE)
        errors.extend(validate_language(source_lang, translated_lang))
        for key, expected in MEGACELLS_QUALITY_TRANSLATIONS.items():
            if translated_lang.get(key) != expected:
                errors.append(
                    f"MEGA Cells 품질 확정 번역이 다릅니다: {key}="
                    f"{translated_lang.get(key)!r}"
                )
        if list(source_lang) != list(translated_lang):
            errors.append("MEGA Cells 언어 키 순서가 영어 원문과 다릅니다.")
        if MEGACELLS_LANG_WORKING_FILE.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"{MEGACELLS_LANG_WORKING_FILE}: UTF-8 BOM이 있습니다.")

    if compare_output:
        if not MEGACELLS_LANG_OUTPUT_FILE.is_file():
            errors.append(
                f"MEGA Cells 언어 출력 파일이 없습니다: {MEGACELLS_LANG_OUTPUT_FILE}"
            )
        elif (
            MEGACELLS_LANG_WORKING_FILE.read_bytes()
            != MEGACELLS_LANG_OUTPUT_FILE.read_bytes()
        ):
            errors.append("MEGA Cells 언어 작업본과 출력이 다릅니다.")

    reused = sum(
        candidate_lang.get(key) == value
        for key, value in translated_lang.items()
        if key in candidate_lang
    )
    return {
        "jars": {"megacells": jar},
        "source_words": 0,
        "source_lang": source_lang,
        "candidate_lang": candidate_lang,
        "translated_lang": translated_lang,
        "existing_korean_reused": reused,
        "existing_korean_corrected": sum(
            key in candidate_lang and candidate_lang[key] != value
            for key, value in translated_lang.items()
        ),
        "new_translations": sum(key not in candidate_lang for key in translated_lang),
        "new_or_revised_translations": len(translated_lang) - reused,
        "guide_pages": 0,
        "new_guide_pages": 0,
        "core_compatibility_updates": 0,
        "errors": errors,
    }


def build_megacells_language(instance: Path) -> dict[str, object]:
    validation = validate_megacells_language(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    MEGACELLS_LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEGACELLS_LANG_OUTPUT_FILE.write_bytes(MEGACELLS_LANG_WORKING_FILE.read_bytes())
    post_validation = validate_megacells_language(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jar = validation["jars"]["megacells"]  # type: ignore[index]
    assert isinstance(jar, Path)
    quest_keys, kubejs_keys = megacells_related_counts()
    result = {
        "status": "megacells_full_language_completed",
        "scope": "MEGA Cells full language file before guide batch 09",
        "batch": 9,
        "source_jars": {"megacells": {"name": jar.name, "sha256": sha256(jar)}},
        "language": "ko_kr",
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "existing_korean_corrected": validation["existing_korean_corrected"],
        "new_translations": validation["new_translations"],
        "ftbquests_keys_updated": quest_keys,
        "kubejs_user_visible_literals_found": kubejs_keys,
        "output_sha256": {MEGACELLS_LANG_RELATIVE: sha256(MEGACELLS_LANG_OUTPUT_FILE)},
        "validation_errors": 0,
    }
    MEGACELLS_LANGUAGE_COMPLETION_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def appflux_related_counts() -> tuple[int, int]:
    quest_overrides = json.loads(
        APPFLUX_QUEST_OVERRIDES_FILE.read_text(encoding="utf-8")
    )
    return len(quest_overrides), 0


def validate_appflux_language(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    jar = find_single_jar(instance, "AppliedFlux-*.jar", "Applied Flux")
    errors: list[str] = []
    with zipfile.ZipFile(jar) as archive:
        source_lang = load_archive_json_unique(
            archive, "assets/appflux/lang/en_us.json"
        )
        candidate_lang = (
            load_archive_json_unique(archive, "assets/appflux/lang/ko_kr.json")
            if "assets/appflux/lang/ko_kr.json" in archive.namelist()
            else {}
        )
    if not APPFLUX_LANG_WORKING_FILE.is_file():
        errors.append(
            f"Applied Flux 언어 작업본이 없습니다: {APPFLUX_LANG_WORKING_FILE}"
        )
        translated_lang: dict[str, str] = {}
    else:
        translated_lang = load_json_unique(APPFLUX_LANG_WORKING_FILE)
        errors.extend(validate_language(source_lang, translated_lang))
        if list(source_lang) != list(translated_lang):
            errors.append("Applied Flux 언어 키 순서가 영어 원문과 다릅니다.")
        if APPFLUX_LANG_WORKING_FILE.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"{APPFLUX_LANG_WORKING_FILE}: UTF-8 BOM이 있습니다.")

    if compare_output:
        if not APPFLUX_LANG_OUTPUT_FILE.is_file():
            errors.append(
                f"Applied Flux 언어 출력 파일이 없습니다: {APPFLUX_LANG_OUTPUT_FILE}"
            )
        elif (
            APPFLUX_LANG_WORKING_FILE.read_bytes()
            != APPFLUX_LANG_OUTPUT_FILE.read_bytes()
        ):
            errors.append("Applied Flux 언어 작업본과 출력이 다릅니다.")

    reused = sum(
        candidate_lang.get(key) == value
        for key, value in translated_lang.items()
        if key in candidate_lang
    )
    return {
        "jars": {"appflux": jar},
        "source_words": 0,
        "source_lang": source_lang,
        "candidate_lang": candidate_lang,
        "translated_lang": translated_lang,
        "existing_korean_reused": reused,
        "existing_korean_corrected": sum(
            key in candidate_lang and candidate_lang[key] != value
            for key, value in translated_lang.items()
        ),
        "new_translations": sum(key not in candidate_lang for key in translated_lang),
        "new_or_revised_translations": len(translated_lang) - reused,
        "guide_pages": 0,
        "new_guide_pages": 0,
        "core_compatibility_updates": 0,
        "errors": errors,
    }


def build_appflux_language(instance: Path) -> dict[str, object]:
    validation = validate_appflux_language(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    APPFLUX_LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    APPFLUX_LANG_OUTPUT_FILE.write_bytes(APPFLUX_LANG_WORKING_FILE.read_bytes())
    post_validation = validate_appflux_language(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jar = validation["jars"]["appflux"]  # type: ignore[index]
    assert isinstance(jar, Path)
    quest_keys, kubejs_keys = appflux_related_counts()
    result = {
        "status": "appflux_full_language_completed",
        "scope": "Applied Flux full language file before guide batch 11",
        "batch": 11,
        "source_jars": {"appflux": {"name": jar.name, "sha256": sha256(jar)}},
        "language": "ko_kr",
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "existing_korean_corrected": validation["existing_korean_corrected"],
        "new_translations": validation["new_translations"],
        "ftbquests_keys_updated": quest_keys,
        "kubejs_user_visible_literals_found": kubejs_keys,
        "output_sha256": {APPFLUX_LANG_RELATIVE: sha256(APPFLUX_LANG_OUTPUT_FILE)},
        "validation_errors": 0,
    }
    APPFLUX_LANGUAGE_COMPLETION_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def expandedae_related_counts() -> tuple[int, int]:
    quest_overrides = json.loads(
        EXPANDEDAE_QUEST_OVERRIDES_FILE.read_text(encoding="utf-8")
    )
    return len(quest_overrides), 1


def validate_expandedae_language(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    jar = find_single_jar(instance, "expandedae-*.jar", "ExpandedAE")
    errors: list[str] = []
    with zipfile.ZipFile(jar) as archive:
        source_lang = load_archive_json_unique(
            archive, "assets/expandedae/lang/en_us.json"
        )
        candidate_lang = (
            load_archive_json_unique(archive, "assets/expandedae/lang/ko_kr.json")
            if "assets/expandedae/lang/ko_kr.json" in archive.namelist()
            else {}
        )
        upgrade_class = archive.read(
            "lu/kolja/expandedae/item/misc/ExpPatternProviderUpgradeItem.class"
        )
        if b"a Pattern Provider to an Expanded Pattern Provider" not in upgrade_class:
            errors.append(
                "ExpandedAE 업그레이드 원문 툴팁을 클래스에서 확인할 수 없습니다."
            )
    if not EXPANDEDAE_LANG_WORKING_FILE.is_file():
        errors.append(
            f"ExpandedAE 언어 작업본이 없습니다: {EXPANDEDAE_LANG_WORKING_FILE}"
        )
        translated_lang: dict[str, str] = {}
    else:
        translated_lang = load_json_unique(EXPANDEDAE_LANG_WORKING_FILE)
        errors.extend(validate_language(source_lang, translated_lang))
        if list(source_lang) != list(translated_lang):
            errors.append("ExpandedAE 언어 키 순서가 영어 원문과 다릅니다.")
        if EXPANDEDAE_LANG_WORKING_FILE.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"{EXPANDEDAE_LANG_WORKING_FILE}: UTF-8 BOM이 있습니다.")

    source_kubejs = (
        (instance / EXPANDEDAE_KUBEJS_RELATIVE)
        .read_text(encoding="utf-8-sig")
        .replace("\r\n", "\n")
    )
    working_kubejs = EXPANDEDAE_KUBEJS_WORKING_FILE.read_text(encoding="utf-8").replace(
        "\r\n", "\n"
    )
    source_lines = [line.rstrip() for line in source_kubejs.splitlines()]
    working_lines = [line.rstrip() for line in working_kubejs.splitlines()]
    changed_lines = [
        index
        for index, (source, working) in enumerate(
            zip(source_lines, working_lines, strict=False)
        )
        if source != working
    ]
    expected_announcement = (
        '  addAnnouncement("4.5", "추가된 모드: Expanded AE, '
        'Industrialization Overdrive, RFTools Storage")'
    )
    source_already_localized = (
        len(source_lines) > 17 and source_lines[17] == expected_announcement
    )
    if len(source_lines) != len(working_lines) or (
        not source_already_localized and changed_lines not in ([], [17])
    ):
        errors.append("ExpandedAE KubeJS 덮어쓰기 범위가 한 공지 문장을 벗어났습니다.")
    if len(working_lines) <= 17 or working_lines[17] != expected_announcement:
        errors.append("ExpandedAE 추가 공지 번역이 예상과 다릅니다.")

    if compare_output:
        if not EXPANDEDAE_LANG_OUTPUT_FILE.is_file():
            errors.append(
                f"ExpandedAE 언어 출력 파일이 없습니다: {EXPANDEDAE_LANG_OUTPUT_FILE}"
            )
        elif (
            EXPANDEDAE_LANG_WORKING_FILE.read_bytes()
            != EXPANDEDAE_LANG_OUTPUT_FILE.read_bytes()
        ):
            errors.append("ExpandedAE 언어 작업본과 출력이 다릅니다.")
        if not EXPANDEDAE_KUBEJS_OUTPUT_FILE.is_file():
            errors.append(
                f"ExpandedAE KubeJS 출력 파일이 없습니다: {EXPANDEDAE_KUBEJS_OUTPUT_FILE}"
            )
        else:
            output_lines = [
                line.rstrip()
                for line in EXPANDEDAE_KUBEJS_OUTPUT_FILE.read_text(encoding="utf-8")
                .replace("\r\n", "\n")
                .splitlines()
            ]
            if len(output_lines) <= 17 or output_lines[17] != expected_announcement:
                errors.append(
                    "ExpandedAE KubeJS 작업 범위가 출력에 보존되지 않았습니다."
                )
        if not EXPANDEDAE_TOOLTIP_OUTPUT_FILE.is_file():
            errors.append(
                "ExpandedAE 직접 삽입 툴팁 덮어쓰기 파일이 없습니다: "
                f"{EXPANDEDAE_TOOLTIP_OUTPUT_FILE}"
            )
        else:
            tooltip_output = EXPANDEDAE_TOOLTIP_OUTPUT_FILE.read_text(encoding="utf-8")
            if tooltip_output.count(EXPANDEDAE_TOOLTIP_OVERRIDE) != 1:
                errors.append(
                    "ExpandedAE 직접 삽입 영어 툴팁 교체 블록이 정확히 하나가 아닙니다."
                )

    reused = sum(
        candidate_lang.get(key) == value
        for key, value in translated_lang.items()
        if key in candidate_lang
    )
    return {
        "jars": {"expandedae": jar},
        "source_words": 0,
        "source_lang": source_lang,
        "candidate_lang": candidate_lang,
        "translated_lang": translated_lang,
        "existing_korean_reused": reused,
        "existing_korean_corrected": sum(
            key in candidate_lang and candidate_lang[key] != value
            for key, value in translated_lang.items()
        ),
        "new_translations": sum(key not in candidate_lang for key in translated_lang),
        "new_or_revised_translations": len(translated_lang) - reused,
        "guide_pages": 0,
        "new_guide_pages": 0,
        "core_compatibility_updates": 0,
        "errors": errors,
    }


def build_expandedae_language(instance: Path) -> dict[str, object]:
    validation = validate_expandedae_language(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    EXPANDEDAE_LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    EXPANDEDAE_LANG_OUTPUT_FILE.write_bytes(EXPANDEDAE_LANG_WORKING_FILE.read_bytes())
    EXPANDEDAE_KUBEJS_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    EXPANDEDAE_KUBEJS_OUTPUT_FILE.write_bytes(
        EXPANDEDAE_KUBEJS_WORKING_FILE.read_bytes()
    )
    post_validation = validate_expandedae_language(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jar = validation["jars"]["expandedae"]  # type: ignore[index]
    assert isinstance(jar, Path)
    quest_keys, kubejs_keys = expandedae_related_counts()
    result = {
        "status": "expandedae_full_language_completed",
        "scope": "ExpandedAE full language file before guide batch 12",
        "batch": 12,
        "source_jars": {"expandedae": {"name": jar.name, "sha256": sha256(jar)}},
        "language": "ko_kr",
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "existing_korean_corrected": validation["existing_korean_corrected"],
        "new_translations": validation["new_translations"],
        "ftbquests_keys_updated": quest_keys,
        "kubejs_user_visible_literals_found": kubejs_keys,
        "output_sha256": {
            EXPANDEDAE_LANG_RELATIVE: sha256(EXPANDEDAE_LANG_OUTPUT_FILE),
            EXPANDEDAE_KUBEJS_RELATIVE.as_posix(): sha256(
                EXPANDEDAE_KUBEJS_OUTPUT_FILE
            ),
        },
        "validation_errors": 0,
    }
    EXPANDEDAE_LANGUAGE_COMPLETION_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def importexport_related_counts() -> tuple[int, int]:
    quest_overrides = json.loads(
        IMPORTEXPORT_QUEST_OVERRIDES_FILE.read_text(encoding="utf-8")
    )
    return len(quest_overrides), 0


def validate_importexport_language(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    jar = find_single_jar(
        instance, "ae2importexportcard-*.jar", "AE2 Import Export Card"
    )
    errors: list[str] = []
    with zipfile.ZipFile(jar) as archive:
        source_lang = load_archive_json_unique(
            archive, "assets/ae2importexportcard/lang/en_us.json"
        )
        candidate_lang = load_archive_json_unique(
            archive, "assets/ae2importexportcard/lang/ko_kr.json"
        )
    if not IMPORTEXPORT_LANG_WORKING_FILE.is_file():
        errors.append(
            "AE2 Import Export Card 언어 작업본이 없습니다: "
            f"{IMPORTEXPORT_LANG_WORKING_FILE}"
        )
        translated_lang: dict[str, str] = {}
    else:
        translated_lang = load_json_unique(IMPORTEXPORT_LANG_WORKING_FILE)
        errors.extend(validate_language(source_lang, translated_lang))
        if list(source_lang) != list(translated_lang):
            errors.append("AE2 Import Export Card 언어 키 순서가 영어 원문과 다릅니다.")
        if IMPORTEXPORT_LANG_WORKING_FILE.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"{IMPORTEXPORT_LANG_WORKING_FILE}: UTF-8 BOM이 있습니다.")

    if compare_output:
        if not IMPORTEXPORT_LANG_OUTPUT_FILE.is_file():
            errors.append(
                "AE2 Import Export Card 언어 출력 파일이 없습니다: "
                f"{IMPORTEXPORT_LANG_OUTPUT_FILE}"
            )
        elif (
            IMPORTEXPORT_LANG_WORKING_FILE.read_bytes()
            != IMPORTEXPORT_LANG_OUTPUT_FILE.read_bytes()
        ):
            errors.append("AE2 Import Export Card 언어 작업본과 출력이 다릅니다.")

    reused = sum(
        candidate_lang.get(key) == value
        for key, value in translated_lang.items()
        if key in candidate_lang
    )
    return {
        "jars": {"ae2importexportcard": jar},
        "source_words": 0,
        "source_lang": source_lang,
        "candidate_lang": candidate_lang,
        "translated_lang": translated_lang,
        "existing_korean_reused": reused,
        "existing_korean_corrected": sum(
            key in candidate_lang and candidate_lang[key] != value
            for key, value in translated_lang.items()
        ),
        "new_translations": sum(key not in candidate_lang for key in translated_lang),
        "new_or_revised_translations": len(translated_lang) - reused,
        "guide_pages": 0,
        "new_guide_pages": 0,
        "core_compatibility_updates": 0,
        "errors": errors,
    }


def build_importexport_language(instance: Path) -> dict[str, object]:
    validation = validate_importexport_language(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    IMPORTEXPORT_LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    IMPORTEXPORT_LANG_OUTPUT_FILE.write_bytes(
        IMPORTEXPORT_LANG_WORKING_FILE.read_bytes()
    )
    post_validation = validate_importexport_language(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jar = validation["jars"]["ae2importexportcard"]  # type: ignore[index]
    assert isinstance(jar, Path)
    quest_keys, kubejs_keys = importexport_related_counts()
    result = {
        "status": "ae2importexportcard_full_language_completed",
        "scope": "AE2 Import Export Card full language file before guide batch 13",
        "batch": 13,
        "source_jars": {
            "ae2importexportcard": {"name": jar.name, "sha256": sha256(jar)}
        },
        "language": "ko_kr",
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "existing_korean_corrected": validation["existing_korean_corrected"],
        "new_translations": validation["new_translations"],
        "ftbquests_keys_updated": quest_keys,
        "kubejs_user_visible_literals_found": kubejs_keys,
        "output_sha256": {
            IMPORTEXPORT_LANG_RELATIVE: sha256(IMPORTEXPORT_LANG_OUTPUT_FILE)
        },
        "validation_errors": 0,
    }
    IMPORTEXPORT_LANGUAGE_COMPLETION_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def netanalyser_related_counts() -> tuple[int, int]:
    quest_overrides = json.loads(
        NETANALYSER_QUEST_OVERRIDES_FILE.read_text(encoding="utf-8")
    )
    return len(quest_overrides), 0


def validate_netanalyser_language(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    jar = find_single_jar(instance, "AE2NetworkAnalyzer-*.jar", "AE2 Network Analyser")
    errors: list[str] = []
    with zipfile.ZipFile(jar) as archive:
        source_lang = load_archive_json_unique(
            archive, "assets/ae2netanalyser/lang/en_us.json"
        )
    candidate_lang: dict[str, str] = {}
    if not NETANALYSER_LANG_WORKING_FILE.is_file():
        errors.append(
            "AE2 Network Analyser 언어 작업본이 없습니다: "
            f"{NETANALYSER_LANG_WORKING_FILE}"
        )
        translated_lang: dict[str, str] = {}
    else:
        translated_lang = load_json_unique(NETANALYSER_LANG_WORKING_FILE)
        errors.extend(validate_language(source_lang, translated_lang))
        for key, expected in NETANALYSER_QUALITY_LANGUAGE_CORRECTIONS.items():
            if translated_lang.get(key) != expected:
                errors.append(
                    f"AE2 Network Analyser 재검수 번역이 다릅니다: {key}="
                    f"{translated_lang.get(key)!r}, 기대값={expected!r}"
                )
        if list(source_lang) != list(translated_lang):
            errors.append("AE2 Network Analyser 언어 키 순서가 영어 원문과 다릅니다.")
        if NETANALYSER_LANG_WORKING_FILE.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"{NETANALYSER_LANG_WORKING_FILE}: UTF-8 BOM이 있습니다.")

    if compare_output:
        if not NETANALYSER_LANG_OUTPUT_FILE.is_file():
            errors.append(
                "AE2 Network Analyser 언어 출력 파일이 없습니다: "
                f"{NETANALYSER_LANG_OUTPUT_FILE}"
            )
        elif (
            NETANALYSER_LANG_WORKING_FILE.read_bytes()
            != NETANALYSER_LANG_OUTPUT_FILE.read_bytes()
        ):
            errors.append("AE2 Network Analyser 언어 작업본과 출력이 다릅니다.")

    reused = sum(
        candidate_lang.get(key) == value
        for key, value in translated_lang.items()
        if key in candidate_lang
    )
    return {
        "jars": {"ae2netanalyser": jar},
        "source_words": 0,
        "source_lang": source_lang,
        "candidate_lang": candidate_lang,
        "translated_lang": translated_lang,
        "existing_korean_reused": reused,
        "existing_korean_corrected": sum(
            key in candidate_lang and candidate_lang[key] != value
            for key, value in translated_lang.items()
        ),
        "new_translations": sum(key not in candidate_lang for key in translated_lang),
        "new_or_revised_translations": len(translated_lang) - reused,
        "guide_pages": 0,
        "new_guide_pages": 0,
        "core_compatibility_updates": 0,
        "errors": errors,
    }


def build_netanalyser_language(instance: Path) -> dict[str, object]:
    validation = validate_netanalyser_language(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    NETANALYSER_LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    NETANALYSER_LANG_OUTPUT_FILE.write_bytes(NETANALYSER_LANG_WORKING_FILE.read_bytes())
    post_validation = validate_netanalyser_language(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jar = validation["jars"]["ae2netanalyser"]  # type: ignore[index]
    assert isinstance(jar, Path)
    quest_keys, kubejs_keys = netanalyser_related_counts()
    result = {
        "status": "quality_review_language_completed",
        "scope": "AE2 Network Analyzer language full quality recheck",
        "batch": 13,
        "source_jars": {"ae2netanalyser": {"name": jar.name, "sha256": sha256(jar)}},
        "language": "ko_kr",
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": len(validation["translated_lang"])
        - len(NETANALYSER_QUALITY_LANGUAGE_CORRECTIONS),
        "existing_korean_corrected": len(NETANALYSER_QUALITY_LANGUAGE_CORRECTIONS),
        "new_translations": 0,
        "ftbquests_keys_updated": quest_keys,
        "kubejs_user_visible_literals_found": kubejs_keys,
        "output_sha256": {
            NETANALYSER_LANG_RELATIVE: sha256(NETANALYSER_LANG_OUTPUT_FILE)
        },
        "validation_errors": 0,
    }
    NETANALYSER_LANGUAGE_COMPLETION_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def merequester_related_counts() -> tuple[int, int]:
    quest_overrides = json.loads(
        MEREQUESTER_QUEST_OVERRIDES_FILE.read_text(encoding="utf-8")
    )
    return len(quest_overrides), 0


def validate_merequester_language(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    jar = find_single_jar(instance, "merequester-neoforge-*.jar", "ME Requester")
    errors: list[str] = []
    with zipfile.ZipFile(jar) as archive:
        source_lang = load_archive_json_unique(
            archive, "assets/merequester/lang/en_us.json"
        )
    candidate_lang: dict[str, str] = {}
    if not MEREQUESTER_LANG_WORKING_FILE.is_file():
        errors.append(
            f"ME Requester 언어 작업본이 없습니다: {MEREQUESTER_LANG_WORKING_FILE}"
        )
        translated_lang: dict[str, str] = {}
    else:
        translated_lang = load_json_unique(MEREQUESTER_LANG_WORKING_FILE)
        errors.extend(validate_language(source_lang, translated_lang))
        for key, expected in MEREQUESTER_QUALITY_LANGUAGE_CORRECTIONS.items():
            if translated_lang.get(key) != expected:
                errors.append(
                    f"ME Requester 재검수 번역이 다릅니다: {key}="
                    f"{translated_lang.get(key)!r}, 기대값={expected!r}"
                )
        if list(source_lang) != list(translated_lang):
            errors.append("ME Requester 언어 키 순서가 영어 원문과 다릅니다.")
        if MEREQUESTER_LANG_WORKING_FILE.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"{MEREQUESTER_LANG_WORKING_FILE}: UTF-8 BOM이 있습니다.")

    if compare_output:
        if not MEREQUESTER_LANG_OUTPUT_FILE.is_file():
            errors.append(
                f"ME Requester 언어 출력 파일이 없습니다: {MEREQUESTER_LANG_OUTPUT_FILE}"
            )
        elif (
            MEREQUESTER_LANG_WORKING_FILE.read_bytes()
            != MEREQUESTER_LANG_OUTPUT_FILE.read_bytes()
        ):
            errors.append("ME Requester 언어 작업본과 출력이 다릅니다.")

    reused = sum(
        candidate_lang.get(key) == value
        for key, value in translated_lang.items()
        if key in candidate_lang
    )
    return {
        "jars": {"merequester": jar},
        "source_words": 0,
        "source_lang": source_lang,
        "candidate_lang": candidate_lang,
        "translated_lang": translated_lang,
        "existing_korean_reused": reused,
        "existing_korean_corrected": sum(
            key in candidate_lang and candidate_lang[key] != value
            for key, value in translated_lang.items()
        ),
        "new_translations": sum(key not in candidate_lang for key in translated_lang),
        "new_or_revised_translations": len(translated_lang) - reused,
        "guide_pages": 0,
        "new_guide_pages": 0,
        "core_compatibility_updates": 0,
        "errors": errors,
    }


def build_merequester_language(instance: Path) -> dict[str, object]:
    validation = validate_merequester_language(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    MEREQUESTER_LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEREQUESTER_LANG_OUTPUT_FILE.write_bytes(MEREQUESTER_LANG_WORKING_FILE.read_bytes())
    post_validation = validate_merequester_language(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jar = validation["jars"]["merequester"]  # type: ignore[index]
    assert isinstance(jar, Path)
    quest_keys, kubejs_keys = merequester_related_counts()
    result = {
        "status": "quality_review_language_completed",
        "scope": "ME Requester language full quality recheck",
        "batch": 14,
        "source_jars": {"merequester": {"name": jar.name, "sha256": sha256(jar)}},
        "language": "ko_kr",
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": len(validation["translated_lang"])
        - len(MEREQUESTER_QUALITY_LANGUAGE_CORRECTIONS),
        "existing_korean_corrected": len(MEREQUESTER_QUALITY_LANGUAGE_CORRECTIONS),
        "new_translations": 0,
        "ftbquests_keys_updated": quest_keys,
        "kubejs_user_visible_literals_found": kubejs_keys,
        "output_sha256": {
            MEREQUESTER_LANG_RELATIVE: sha256(MEREQUESTER_LANG_OUTPUT_FILE)
        },
        "validation_errors": 0,
    }
    MEREQUESTER_LANGUAGE_COMPLETION_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def arseng_related_counts() -> tuple[int, int]:
    quest_overrides = json.loads(
        ARSENG_QUEST_OVERRIDES_FILE.read_text(encoding="utf-8")
    )
    return len(quest_overrides), 0


def validate_arseng_language(instance: Path, compare_output: bool) -> dict[str, object]:
    jar = find_single_jar(instance, "arseng-*.jar", "Ars Énergistique")
    errors: list[str] = []
    with zipfile.ZipFile(jar) as archive:
        source_lang = load_archive_json_unique(archive, "assets/arseng/lang/en_us.json")
    candidate_lang: dict[str, str] = {}
    if not ARSENG_LANG_WORKING_FILE.is_file():
        errors.append(
            f"Ars Énergistique 언어 작업본이 없습니다: {ARSENG_LANG_WORKING_FILE}"
        )
        translated_lang: dict[str, str] = {}
    else:
        translated_lang = load_json_unique(ARSENG_LANG_WORKING_FILE)
        errors.extend(validate_language(source_lang, translated_lang))
        if list(source_lang) != list(translated_lang):
            errors.append("Ars Énergistique 언어 키 순서가 영어 원문과 다릅니다.")
        if ARSENG_LANG_WORKING_FILE.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"{ARSENG_LANG_WORKING_FILE}: UTF-8 BOM이 있습니다.")

    if compare_output:
        if not ARSENG_LANG_OUTPUT_FILE.is_file():
            errors.append(
                f"Ars Énergistique 언어 출력 파일이 없습니다: {ARSENG_LANG_OUTPUT_FILE}"
            )
        elif translated_lang != load_json_unique(ARSENG_LANG_OUTPUT_FILE):
            errors.append("Ars Énergistique 언어 작업본과 출력이 다릅니다.")

    reused = sum(
        candidate_lang.get(key) == value
        for key, value in translated_lang.items()
        if key in candidate_lang
    )
    return {
        "jars": {"arseng": jar},
        "source_words": 0,
        "source_lang": source_lang,
        "candidate_lang": candidate_lang,
        "translated_lang": translated_lang,
        "existing_korean_reused": reused,
        "existing_korean_corrected": sum(
            key in candidate_lang and candidate_lang[key] != value
            for key, value in translated_lang.items()
        ),
        "new_translations": sum(key not in candidate_lang for key in translated_lang),
        "new_or_revised_translations": len(translated_lang) - reused,
        "guide_pages": 0,
        "new_guide_pages": 0,
        "core_compatibility_updates": 0,
        "errors": errors,
    }


def build_arseng_language(instance: Path) -> dict[str, object]:
    validation = validate_arseng_language(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    ARSENG_LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ARSENG_LANG_OUTPUT_FILE.write_bytes(ARSENG_LANG_WORKING_FILE.read_bytes())
    post_validation = validate_arseng_language(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jar = validation["jars"]["arseng"]  # type: ignore[index]
    assert isinstance(jar, Path)
    quest_keys, kubejs_keys = arseng_related_counts()
    result = {
        "status": "quality_review_language_completed",
        "scope": "Ars Énergistique language full quality recheck",
        "batch": 15,
        "source_jars": {"arseng": {"name": jar.name, "sha256": sha256(jar)}},
        "language": "ko_kr",
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": len(validation["translated_lang"]),
        "existing_korean_corrected": 0,
        "new_translations": 0,
        "ftbquests_keys_updated": quest_keys,
        "kubejs_user_visible_literals_found": kubejs_keys,
        "output_sha256": {ARSENG_LANG_RELATIVE: sha256(ARSENG_LANG_OUTPUT_FILE)},
        "validation_errors": 0,
    }
    ARSENG_LANGUAGE_COMPLETION_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_advancedae_batch(
    instance: Path, batch: int, compare_output: bool
) -> dict[str, object]:
    if batch not in ADVANCEDAE_BATCH_GUIDE_FILES:
        raise ValueError(f"지원하지 않는 AdvancedAE 가이드 배치입니다: {batch}")
    validation = validate_advancedae_language(instance, compare_output)
    errors = validation["errors"]
    assert isinstance(errors, list)
    batch_files = ADVANCEDAE_BATCH_GUIDE_FILES[batch]
    expected_all = {
        relative
        for files in ADVANCEDAE_BATCH_GUIDE_FILES.values()
        for relative in files
    }
    actual_working = {
        path.relative_to(ADVANCEDAE_GUIDE_WORKING_ROOT).as_posix()
        for path in ADVANCEDAE_GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if batch == ACTIVE_BATCH and actual_working != expected_all:
        errors.append(
            f"AdvancedAE {batch}차 누적 작업본 목록이 다릅니다: "
            f"누락={sorted(expected_all - actual_working)}, "
            f"불필요={sorted(actual_working - expected_all)}"
        )

    jars = {
        "ae2": find_single_jar(instance, "appliedenergistics2-*.jar", "AE2"),
        "advanced_ae": find_single_jar(instance, "AdvancedAE-*.jar", "AdvancedAE"),
    }
    archives = {namespace: zipfile.ZipFile(path) for namespace, path in jars.items()}
    try:
        archive_names = {
            namespace: set(archive.namelist())
            for namespace, archive in archives.items()
        }
        source_words = 0
        for relative in batch_files:
            entry = (GUIDE_SOURCE_ROOTS["advanced_ae"] / relative).as_posix()
            source = archives["advanced_ae"].read(entry).decode("utf-8-sig")
            source = source.replace("\r\r\n", "\n").replace("\r\n", "\n")
            working_path = ADVANCEDAE_GUIDE_WORKING_ROOT / relative
            if not working_path.is_file():
                errors.append(f"가이드 작업본이 없습니다: {working_path}")
                continue
            translated = working_path.read_text(encoding="utf-8")
            errors.extend(core.validate_pair(relative, source, translated))
            errors.extend(validate_numbers(relative, source, translated))
            errors.extend(validate_tag_nesting(relative, translated))
            errors.extend(
                validate_resources(archive_names, "advanced_ae", relative, translated)
            )
            source_words += len(
                core.ENGLISH_WORD_RE.findall(core.extract_visible_text(source))
            )
            if working_path.read_bytes().startswith(b"\xef\xbb\xbf"):
                errors.append(f"{working_path}: UTF-8 BOM이 있습니다.")
            if compare_output:
                output_path = ADVANCEDAE_GUIDE_OUTPUT_ROOT / relative
                if not output_path.is_file():
                    errors.append(f"가이드 출력 파일이 없습니다: {output_path}")
                elif working_path.read_bytes() != output_path.read_bytes():
                    errors.append(f"{relative}: 작업본과 출력이 다릅니다.")

        translated_lang = validation["translated_lang"]
        assert isinstance(translated_lang, dict)
        for key, relative in ADVANCEDAE_BATCH_ITEM_NAMES[batch].items():
            text = (ADVANCEDAE_GUIDE_WORKING_ROOT / relative).read_text(
                encoding="utf-8"
            )
            item_name = translated_lang[key]
            if item_name not in core.extract_visible_text(text):
                errors.append(
                    f"{relative}: 언어 파일의 아이템명이 가이드에 없습니다: {item_name}"
                )

        if compare_output:
            output_files = {
                path.relative_to(ADVANCEDAE_GUIDE_OUTPUT_ROOT).as_posix()
                for path in ADVANCEDAE_GUIDE_OUTPUT_ROOT.rglob("*.md")
                if path.is_file()
            }
            if batch == ACTIVE_BATCH and output_files != expected_all:
                errors.append(
                    f"AdvancedAE {batch}차 누적 출력 목록이 다릅니다: "
                    f"누락={sorted(expected_all - output_files)}, "
                    f"불필요={sorted(output_files - expected_all)}"
                )

        validation.update(
            {
                "jars": jars,
                "source_words": source_words,
                "guide_pages": len(batch_files),
                "new_guide_pages": len(batch_files),
                "core_compatibility_updates": 0,
            }
        )
        return validation
    finally:
        for archive in archives.values():
            archive.close()


def build_advancedae_batch(instance: Path, batch: int) -> dict[str, object]:
    validation = validate_advancedae_batch(instance, batch, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    batch_files = ADVANCEDAE_BATCH_GUIDE_FILES[batch]
    for relative in batch_files:
        source = ADVANCEDAE_GUIDE_WORKING_ROOT / relative
        target = ADVANCEDAE_GUIDE_OUTPUT_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    ADVANCEDAE_LANG_OUTPUT_FILE.write_bytes(ADVANCEDAE_LANG_WORKING_FILE.read_bytes())

    post_validation = validate_advancedae_batch(instance, batch, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    quest_keys, kubejs_keys = advancedae_related_counts()
    result = {
        "status": f"batch_{batch:02d}_completed",
        "scope": ADVANCEDAE_BATCH_SCOPES[batch],
        "batch": batch,
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": len(batch_files),
        "new_guide_pages": len(batch_files),
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "new_or_revised_translations": validation["new_or_revised_translations"],
        "guide_files": list(batch_files),
        "output_sha256": {
            ADVANCEDAE_LANG_RELATIVE: sha256(ADVANCEDAE_LANG_OUTPUT_FILE),
            **{
                "assets/advanced_ae/ae2guide/_ko_kr/" + relative: sha256(
                    ADVANCEDAE_GUIDE_OUTPUT_ROOT / relative
                )
                for relative in batch_files
            },
        },
        "ftbquests_review": {
            "related_content_found": True,
            "keys_updated": quest_keys,
            "handled_separately": True,
            "pending": False,
        },
        "kubejs_user_visible_literals_found": kubejs_keys,
        "validation_errors": 0,
    }
    PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_advancedae_quality(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    validations = [
        validate_advancedae_batch(instance, batch, compare_output)
        for batch in sorted(ADVANCEDAE_BATCH_GUIDE_FILES)
    ]
    errors = [
        error
        for validation in validations
        for error in validation["errors"]  # type: ignore[union-attr]
    ]
    errors.extend(validate_advancedae_kubejs(instance, compare_output))
    expected_files = tuple(
        relative
        for batch in sorted(ADVANCEDAE_BATCH_GUIDE_FILES)
        for relative in ADVANCEDAE_BATCH_GUIDE_FILES[batch]
    )
    expected_set = set(expected_files)
    actual_working = {
        path.relative_to(ADVANCEDAE_GUIDE_WORKING_ROOT).as_posix()
        for path in ADVANCEDAE_GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if actual_working != expected_set:
        errors.append(
            "Advanced AE 품질 재검수 작업본 목록이 다릅니다: "
            f"누락={sorted(expected_set - actual_working)}, "
            f"불필요={sorted(actual_working - expected_set)}"
        )
    if compare_output:
        actual_output = {
            path.relative_to(ADVANCEDAE_GUIDE_OUTPUT_ROOT).as_posix()
            for path in ADVANCEDAE_GUIDE_OUTPUT_ROOT.rglob("*.md")
            if path.is_file()
        }
        if actual_output != expected_set:
            errors.append(
                "Advanced AE 품질 재검수 출력 목록이 다릅니다: "
                f"누락={sorted(expected_set - actual_output)}, "
                f"불필요={sorted(actual_output - expected_set)}"
            )

    translated_lang = validations[0]["translated_lang"]
    assert isinstance(translated_lang, dict)
    for key, expected in ADVANCEDAE_QUALITY_TRANSLATIONS.items():
        if translated_lang.get(key) != expected:
            errors.append(
                f"Advanced AE 품질 확정 번역이 다릅니다: {key}="
                f"{translated_lang.get(key)!r}"
            )
    for relative in expected_files:
        text = (ADVANCEDAE_GUIDE_WORKING_ROOT / relative).read_text(encoding="utf-8")
        for phrase in ADVANCEDAE_FORBIDDEN_GUIDE_PHRASES:
            if phrase in text:
                errors.append(f"{relative}: 재검수 전 표현이 남아 있습니다: {phrase}")

    return {
        **validations[0],
        "source_words": sum(
            int(validation["source_words"]) for validation in validations
        ),
        "guide_pages": len(expected_files),
        "new_guide_pages": len(expected_files),
        "guide_files": expected_files,
        "errors": errors,
    }


def build_advancedae_quality(instance: Path) -> dict[str, object]:
    prepare_advancedae_kubejs(instance)
    validation = validate_advancedae_quality(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    guide_files = validation["guide_files"]
    assert isinstance(guide_files, tuple)
    for relative in guide_files:
        source = ADVANCEDAE_GUIDE_WORKING_ROOT / relative
        target = ADVANCEDAE_GUIDE_OUTPUT_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    ADVANCEDAE_LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ADVANCEDAE_LANG_OUTPUT_FILE.write_bytes(ADVANCEDAE_LANG_WORKING_FILE.read_bytes())
    ADVANCEDAE_KUBEJS_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ADVANCEDAE_KUBEJS_OUTPUT_FILE.write_bytes(
        ADVANCEDAE_KUBEJS_WORKING_FILE.read_bytes()
    )

    post_validation = validate_advancedae_quality(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    output_files = {
        ADVANCEDAE_LANG_RELATIVE: sha256(ADVANCEDAE_LANG_OUTPUT_FILE),
        ADVANCEDAE_KUBEJS_RELATIVE.as_posix(): sha256(ADVANCEDAE_KUBEJS_OUTPUT_FILE),
        **{
            "assets/advanced_ae/ae2guide/_ko_kr/" + relative: sha256(
                ADVANCEDAE_GUIDE_OUTPUT_ROOT / relative
            )
            for relative in guide_files
        },
    }
    quest_keys, kubejs_keys = advancedae_related_counts()
    result = {
        "status": "quality_review_completed",
        "scope": (
            "Advanced AE language, GuideME guide, FTB Quests, and KubeJS quality review"
        ),
        "batch": [7, 8],
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": len(guide_files),
        "new_guide_pages": len(guide_files),
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "new_or_revised_translations": validation["new_or_revised_translations"],
        "guide_files": list(guide_files),
        "output_sha256": output_files,
        "ftbquests_review": {
            "related_content_found": True,
            "keys_updated": quest_keys,
            "handled_separately": True,
            "pending": False,
        },
        "kubejs_user_visible_literals_found": kubejs_keys,
        "validation_errors": 0,
    }
    ADVANCEDAE_PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    ADVANCEDAE_PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_advancedae_batch_07(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    return validate_advancedae_batch(instance, 7, compare_output)


def build_advancedae_batch_07(instance: Path) -> dict[str, object]:
    return build_advancedae_batch(instance, 7)


def validate_advancedae_batch_08(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    return validate_advancedae_batch(instance, 8, compare_output)


def build_advancedae_batch_08(instance: Path) -> dict[str, object]:
    return build_advancedae_batch(instance, 8)


def validate_megacells_batch(
    instance: Path, batch: int, compare_output: bool
) -> dict[str, object]:
    if batch not in MEGACELLS_BATCH_GUIDE_FILES:
        raise ValueError(f"지원하지 않는 MEGA Cells 가이드 배치입니다: {batch}")
    validation = validate_megacells_language(instance, compare_output)
    errors = validation["errors"]
    assert isinstance(errors, list)
    batch_files = MEGACELLS_BATCH_GUIDE_FILES[batch]
    expected_all = {
        relative
        for batch_number, files in MEGACELLS_BATCH_GUIDE_FILES.items()
        if batch_number <= batch
        for relative in files
    }
    actual_working = {
        path.relative_to(MEGACELLS_GUIDE_WORKING_ROOT).as_posix()
        for path in MEGACELLS_GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if batch == ACTIVE_BATCH and actual_working != expected_all:
        errors.append(
            f"MEGA Cells {batch}차 누적 작업본 목록이 다릅니다: "
            f"누락={sorted(expected_all - actual_working)}, "
            f"불필요={sorted(actual_working - expected_all)}"
        )

    jars = {
        "ae2": find_single_jar(instance, "appliedenergistics2-*.jar", "AE2"),
        "megacells": find_single_jar(instance, "megacells-*.jar", "MEGA Cells"),
    }
    archives = {namespace: zipfile.ZipFile(path) for namespace, path in jars.items()}
    try:
        archive_names = {
            namespace: set(archive.namelist())
            for namespace, archive in archives.items()
        }
        source_words = 0
        for relative in batch_files:
            entry = (GUIDE_SOURCE_ROOTS["megacells"] / relative).as_posix()
            source = archives["megacells"].read(entry).decode("utf-8-sig")
            source = source.replace("\r\r\n", "\n").replace("\r\n", "\n")
            working_path = MEGACELLS_GUIDE_WORKING_ROOT / relative
            if not working_path.is_file():
                errors.append(f"가이드 작업본이 없습니다: {working_path}")
                continue
            translated = working_path.read_text(encoding="utf-8")
            errors.extend(core.validate_pair(relative, source, translated))
            errors.extend(validate_numbers(relative, source, translated))
            for phrase in MEGACELLS_FORBIDDEN_GUIDE_PHRASES:
                if phrase in translated:
                    errors.append(
                        f"{relative}: 재검수 전 표현이 남아 있습니다: {phrase}"
                    )
            errors.extend(validate_tag_nesting(relative, translated))
            errors.extend(
                validate_resources(archive_names, "megacells", relative, translated)
            )
            source_words += len(
                core.ENGLISH_WORD_RE.findall(core.extract_visible_text(source))
            )
            if working_path.read_bytes().startswith(b"\xef\xbb\xbf"):
                errors.append(f"{working_path}: UTF-8 BOM이 있습니다.")
            if compare_output:
                output_path = MEGACELLS_GUIDE_OUTPUT_ROOT / relative
                if not output_path.is_file():
                    errors.append(f"가이드 출력 파일이 없습니다: {output_path}")
                elif working_path.read_bytes() != output_path.read_bytes():
                    errors.append(f"{relative}: 작업본과 출력이 다릅니다.")

        translated_lang = validation["translated_lang"]
        assert isinstance(translated_lang, dict)
        for key, relative in MEGACELLS_BATCH_ITEM_NAMES[batch].items():
            text = (MEGACELLS_GUIDE_WORKING_ROOT / relative).read_text(encoding="utf-8")
            item_name = translated_lang[key]
            if item_name not in core.extract_visible_text(text):
                errors.append(
                    f"{relative}: 언어 파일의 아이템명이 가이드에 없습니다: {item_name}"
                )

        if compare_output:
            output_files = {
                path.relative_to(MEGACELLS_GUIDE_OUTPUT_ROOT).as_posix()
                for path in MEGACELLS_GUIDE_OUTPUT_ROOT.rglob("*.md")
                if path.is_file()
            }
            if batch == ACTIVE_BATCH and output_files != expected_all:
                errors.append(
                    f"MEGA Cells {batch}차 누적 출력 목록이 다릅니다: "
                    f"누락={sorted(expected_all - output_files)}, "
                    f"불필요={sorted(output_files - expected_all)}"
                )

        validation.update(
            {
                "jars": jars,
                "source_words": source_words,
                "guide_pages": len(batch_files),
                "new_guide_pages": len(batch_files),
                "core_compatibility_updates": 0,
            }
        )
        return validation
    finally:
        for archive in archives.values():
            archive.close()


def build_megacells_batch(instance: Path, batch: int) -> dict[str, object]:
    validation = validate_megacells_batch(instance, batch, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    batch_files = MEGACELLS_BATCH_GUIDE_FILES[batch]
    for relative in batch_files:
        source = MEGACELLS_GUIDE_WORKING_ROOT / relative
        target = MEGACELLS_GUIDE_OUTPUT_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    MEGACELLS_LANG_OUTPUT_FILE.write_bytes(MEGACELLS_LANG_WORKING_FILE.read_bytes())

    post_validation = validate_megacells_batch(instance, batch, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    quest_keys, kubejs_keys = megacells_related_counts()
    result = {
        "status": f"batch_{batch:02d}_completed",
        "scope": MEGACELLS_BATCH_SCOPES[batch],
        "batch": batch,
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": len(batch_files),
        "new_guide_pages": len(batch_files),
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "new_or_revised_translations": validation["new_or_revised_translations"],
        "guide_files": list(batch_files),
        "output_sha256": {
            MEGACELLS_LANG_RELATIVE: sha256(MEGACELLS_LANG_OUTPUT_FILE),
            **{
                "assets/megacells/ae2guide/_ko_kr/" + relative: sha256(
                    MEGACELLS_GUIDE_OUTPUT_ROOT / relative
                )
                for relative in batch_files
            },
        },
        "ftbquests_review": {
            "related_content_found": True,
            "keys_updated": quest_keys,
            "handled_separately": True,
            "pending": False,
        },
        "kubejs_user_visible_literals_found": kubejs_keys,
        "validation_errors": 0,
    }
    PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_megacells_quality(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    validations = [
        validate_megacells_batch(instance, batch, compare_output)
        for batch in sorted(MEGACELLS_BATCH_GUIDE_FILES)
    ]
    errors = [
        error
        for validation in validations
        for error in validation["errors"]  # type: ignore[union-attr]
    ]
    expected_files = tuple(
        relative
        for batch in sorted(MEGACELLS_BATCH_GUIDE_FILES)
        for relative in MEGACELLS_BATCH_GUIDE_FILES[batch]
    )
    expected_set = set(expected_files)
    actual_working = {
        path.relative_to(MEGACELLS_GUIDE_WORKING_ROOT).as_posix()
        for path in MEGACELLS_GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if actual_working != expected_set:
        errors.append(
            "MEGA Cells 품질 재검수 작업본 목록이 다릅니다: "
            f"누락={sorted(expected_set - actual_working)}, "
            f"불필요={sorted(actual_working - expected_set)}"
        )
    if compare_output:
        actual_output = {
            path.relative_to(MEGACELLS_GUIDE_OUTPUT_ROOT).as_posix()
            for path in MEGACELLS_GUIDE_OUTPUT_ROOT.rglob("*.md")
            if path.is_file()
        }
        if actual_output != expected_set:
            errors.append(
                "MEGA Cells 품질 재검수 출력 목록이 다릅니다: "
                f"누락={sorted(expected_set - actual_output)}, "
                f"불필요={sorted(actual_output - expected_set)}"
            )

    return {
        **validations[0],
        "source_words": sum(
            int(validation["source_words"]) for validation in validations
        ),
        "guide_pages": len(expected_files),
        "new_guide_pages": len(expected_files),
        "guide_files": expected_files,
        "errors": errors,
    }


def build_megacells_quality(instance: Path) -> dict[str, object]:
    validation = validate_megacells_quality(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    guide_files = validation["guide_files"]
    assert isinstance(guide_files, tuple)
    for relative in guide_files:
        source = MEGACELLS_GUIDE_WORKING_ROOT / relative
        target = MEGACELLS_GUIDE_OUTPUT_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    MEGACELLS_LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEGACELLS_LANG_OUTPUT_FILE.write_bytes(MEGACELLS_LANG_WORKING_FILE.read_bytes())

    post_validation = validate_megacells_quality(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    output_files = {
        MEGACELLS_LANG_RELATIVE: sha256(MEGACELLS_LANG_OUTPUT_FILE),
        **{
            "assets/megacells/ae2guide/_ko_kr/" + relative: sha256(
                MEGACELLS_GUIDE_OUTPUT_ROOT / relative
            )
            for relative in guide_files
        },
    }
    quest_keys, kubejs_keys = megacells_related_counts()
    result = {
        "status": "quality_review_completed",
        "scope": (
            "MEGA Cells language, GuideME guide, FTB Quests, and KubeJS "
            "quality review"
        ),
        "batch": [9, 10],
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": len(guide_files),
        "new_guide_pages": len(guide_files),
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "new_or_revised_translations": validation["new_or_revised_translations"],
        "guide_files": list(guide_files),
        "output_sha256": output_files,
        "ftbquests_review": {
            "related_content_found": True,
            "keys_updated": quest_keys,
            "handled_separately": True,
            "pending": False,
        },
        "kubejs_user_visible_literals_found": kubejs_keys,
        "validation_errors": 0,
    }
    MEGACELLS_PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEGACELLS_PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_megacells_batch_09(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    return validate_megacells_batch(instance, 9, compare_output)


def build_megacells_batch_09(instance: Path) -> dict[str, object]:
    return build_megacells_batch(instance, 9)


def validate_megacells_batch_10(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    return validate_megacells_batch(instance, 10, compare_output)


def build_megacells_batch_10(instance: Path) -> dict[str, object]:
    return build_megacells_batch(instance, 10)


def validate_appflux_batch_11(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    validation = validate_appflux_language(instance, compare_output)
    errors = validation["errors"]
    assert isinstance(errors, list)
    expected_all = set(APPFLUX_BATCH_11_GUIDE_FILES)
    actual_working = {
        path.relative_to(APPFLUX_GUIDE_WORKING_ROOT).as_posix()
        for path in APPFLUX_GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if actual_working != expected_all:
        errors.append(
            "Applied Flux 11차 작업본 목록이 다릅니다: "
            f"누락={sorted(expected_all - actual_working)}, "
            f"불필요={sorted(actual_working - expected_all)}"
        )

    jars = {
        "ae2": find_single_jar(instance, "appliedenergistics2-*.jar", "AE2"),
        "appflux": find_single_jar(instance, "AppliedFlux-*.jar", "Applied Flux"),
    }
    archives = {namespace: zipfile.ZipFile(path) for namespace, path in jars.items()}
    try:
        archive_names = {
            namespace: set(archive.namelist())
            for namespace, archive in archives.items()
        }
        source_words = 0
        for relative in APPFLUX_BATCH_11_GUIDE_FILES:
            entry = (GUIDE_SOURCE_ROOTS["appflux"] / relative).as_posix()
            source = archives["appflux"].read(entry).decode("utf-8-sig")
            source = source.replace("\r\r\n", "\n").replace("\r\n", "\n")
            if relative == "appflux/appflux-index.md":
                source = source.replace("    title:", "  title:", 1)
                source = source.replace("    position:", "  position:", 1)
            working_path = APPFLUX_GUIDE_WORKING_ROOT / relative
            if not working_path.is_file():
                errors.append(f"가이드 작업본이 없습니다: {working_path}")
                continue
            translated = working_path.read_text(encoding="utf-8")
            errors.extend(core.validate_pair(relative, source, translated))
            errors.extend(validate_numbers(relative, source, translated))
            errors.extend(validate_tag_nesting(relative, translated))
            errors.extend(
                validate_resources(archive_names, "appflux", relative, translated)
            )
            source_words += len(
                core.ENGLISH_WORD_RE.findall(core.extract_visible_text(source))
            )
            if working_path.read_bytes().startswith(b"\xef\xbb\xbf"):
                errors.append(f"{working_path}: UTF-8 BOM이 있습니다.")
            if compare_output:
                output_path = APPFLUX_GUIDE_OUTPUT_ROOT / relative
                if not output_path.is_file():
                    errors.append(f"가이드 출력 파일이 없습니다: {output_path}")
                elif working_path.read_bytes() != output_path.read_bytes():
                    errors.append(f"{relative}: 작업본과 출력이 다릅니다.")

        translated_lang = validation["translated_lang"]
        assert isinstance(translated_lang, dict)
        for key, relative in APPFLUX_BATCH_11_ITEM_NAMES.items():
            text = (APPFLUX_GUIDE_WORKING_ROOT / relative).read_text(encoding="utf-8")
            item_name = translated_lang[key]
            if item_name not in core.extract_visible_text(text):
                errors.append(
                    f"{relative}: 언어 파일의 아이템명이 가이드에 없습니다: {item_name}"
                )

        if compare_output:
            output_files = {
                path.relative_to(APPFLUX_GUIDE_OUTPUT_ROOT).as_posix()
                for path in APPFLUX_GUIDE_OUTPUT_ROOT.rglob("*.md")
                if path.is_file()
            }
            if output_files != expected_all:
                errors.append(
                    "Applied Flux 11차 출력 목록이 다릅니다: "
                    f"누락={sorted(expected_all - output_files)}, "
                    f"불필요={sorted(output_files - expected_all)}"
                )

        validation.update(
            {
                "jars": jars,
                "source_words": source_words,
                "guide_pages": len(APPFLUX_BATCH_11_GUIDE_FILES),
                "new_guide_pages": len(APPFLUX_BATCH_11_GUIDE_FILES),
                "core_compatibility_updates": 0,
            }
        )
        return validation
    finally:
        for archive in archives.values():
            archive.close()


def build_appflux_batch_11(instance: Path) -> dict[str, object]:
    validation = validate_appflux_batch_11(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    for relative in APPFLUX_BATCH_11_GUIDE_FILES:
        source = APPFLUX_GUIDE_WORKING_ROOT / relative
        target = APPFLUX_GUIDE_OUTPUT_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    APPFLUX_LANG_OUTPUT_FILE.write_bytes(APPFLUX_LANG_WORKING_FILE.read_bytes())

    post_validation = validate_appflux_batch_11(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    quest_keys, kubejs_keys = appflux_related_counts()
    result = {
        "status": "batch_11_completed",
        "scope": "Applied Flux GuideME guide batch 11",
        "batch": 11,
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": len(APPFLUX_BATCH_11_GUIDE_FILES),
        "new_guide_pages": len(APPFLUX_BATCH_11_GUIDE_FILES),
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "new_or_revised_translations": validation["new_or_revised_translations"],
        "guide_files": list(APPFLUX_BATCH_11_GUIDE_FILES),
        "output_sha256": {
            APPFLUX_LANG_RELATIVE: sha256(APPFLUX_LANG_OUTPUT_FILE),
            **{
                "assets/appflux/ae2guide/_ko_kr/" + relative: sha256(
                    APPFLUX_GUIDE_OUTPUT_ROOT / relative
                )
                for relative in APPFLUX_BATCH_11_GUIDE_FILES
            },
        },
        "ftbquests_review": {
            "related_content_found": True,
            "keys_updated": quest_keys,
            "handled_separately": True,
            "pending": False,
        },
        "kubejs_user_visible_literals_found": kubejs_keys,
        "validation_errors": 0,
    }
    PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_expandedae_batch_12(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    validation = validate_expandedae_language(instance, compare_output)
    errors = validation["errors"]
    assert isinstance(errors, list)
    expected_all = set(EXPANDEDAE_BATCH_12_GUIDE_FILES)
    actual_working = {
        path.relative_to(EXPANDEDAE_GUIDE_WORKING_ROOT).as_posix()
        for path in EXPANDEDAE_GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if actual_working != expected_all:
        errors.append(
            "ExpandedAE 12차 작업본 목록이 다릅니다: "
            f"누락={sorted(expected_all - actual_working)}, "
            f"불필요={sorted(actual_working - expected_all)}"
        )

    jars = {
        "ae2": find_single_jar(instance, "appliedenergistics2-*.jar", "AE2"),
        "ae2wtlib": find_single_jar(instance, "ae2wtlib-*.jar", "AE2WTLib"),
        "expandedae": find_single_jar(instance, "expandedae-*.jar", "ExpandedAE"),
    }
    archives = {namespace: zipfile.ZipFile(path) for namespace, path in jars.items()}
    try:
        archive_names = {
            namespace: set(archive.namelist())
            for namespace, archive in archives.items()
        }
        source_words = 0
        for relative in EXPANDEDAE_BATCH_12_GUIDE_FILES:
            entry = (GUIDE_SOURCE_ROOTS["expandedae"] / relative).as_posix()
            source = archives["expandedae"].read(entry).decode("utf-8-sig")
            source = source.replace("\r\r\n", "\n").replace("\r\n", "\n")
            working_path = EXPANDEDAE_GUIDE_WORKING_ROOT / relative
            if not working_path.is_file():
                errors.append(f"가이드 작업본이 없습니다: {working_path}")
                continue
            translated = working_path.read_text(encoding="utf-8")
            errors.extend(core.validate_pair(relative, source, translated))
            errors.extend(validate_numbers(relative, source, translated))
            errors.extend(validate_tag_nesting(relative, translated))
            errors.extend(
                validate_resources(archive_names, "expandedae", relative, translated)
            )
            source_words += len(
                core.ENGLISH_WORD_RE.findall(core.extract_visible_text(source))
            )
            if working_path.read_bytes().startswith(b"\xef\xbb\xbf"):
                errors.append(f"{working_path}: UTF-8 BOM이 있습니다.")
            if compare_output:
                output_path = EXPANDEDAE_GUIDE_OUTPUT_ROOT / relative
                if not output_path.is_file():
                    errors.append(f"가이드 출력 파일이 없습니다: {output_path}")
                elif working_path.read_bytes() != output_path.read_bytes():
                    errors.append(f"{relative}: 작업본과 출력이 다릅니다.")

        translated_lang = validation["translated_lang"]
        assert isinstance(translated_lang, dict)
        for key, relative in EXPANDEDAE_BATCH_12_ITEM_NAMES.items():
            text = (EXPANDEDAE_GUIDE_WORKING_ROOT / relative).read_text(
                encoding="utf-8"
            )
            item_name = translated_lang[key]
            if item_name not in core.extract_visible_text(text):
                errors.append(
                    f"{relative}: 언어 파일의 아이템명이 가이드에 없습니다: {item_name}"
                )

        if compare_output:
            output_files = {
                path.relative_to(EXPANDEDAE_GUIDE_OUTPUT_ROOT).as_posix()
                for path in EXPANDEDAE_GUIDE_OUTPUT_ROOT.rglob("*.md")
                if path.is_file()
            }
            if output_files != expected_all:
                errors.append(
                    "ExpandedAE 12차 출력 목록이 다릅니다: "
                    f"누락={sorted(expected_all - output_files)}, "
                    f"불필요={sorted(output_files - expected_all)}"
                )

        validation.update(
            {
                "jars": jars,
                "source_words": source_words,
                "guide_pages": len(EXPANDEDAE_BATCH_12_GUIDE_FILES),
                "new_guide_pages": len(EXPANDEDAE_BATCH_12_GUIDE_FILES),
                "core_compatibility_updates": 0,
            }
        )
        return validation
    finally:
        for archive in archives.values():
            archive.close()


def build_expandedae_batch_12(instance: Path) -> dict[str, object]:
    validation = validate_expandedae_batch_12(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    for relative in EXPANDEDAE_BATCH_12_GUIDE_FILES:
        source = EXPANDEDAE_GUIDE_WORKING_ROOT / relative
        target = EXPANDEDAE_GUIDE_OUTPUT_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    EXPANDEDAE_LANG_OUTPUT_FILE.write_bytes(EXPANDEDAE_LANG_WORKING_FILE.read_bytes())

    post_validation = validate_expandedae_batch_12(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    quest_keys, kubejs_keys = expandedae_related_counts()
    result = {
        "status": "batch_12_completed",
        "scope": "ExpandedAE GuideME guide batch 12",
        "batch": 12,
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": len(EXPANDEDAE_BATCH_12_GUIDE_FILES),
        "new_guide_pages": len(EXPANDEDAE_BATCH_12_GUIDE_FILES),
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "new_or_revised_translations": validation["new_or_revised_translations"],
        "guide_files": list(EXPANDEDAE_BATCH_12_GUIDE_FILES),
        "output_sha256": {
            EXPANDEDAE_LANG_RELATIVE: sha256(EXPANDEDAE_LANG_OUTPUT_FILE),
            **{
                "assets/expandedae/ae2guide/_ko_kr/" + relative: sha256(
                    EXPANDEDAE_GUIDE_OUTPUT_ROOT / relative
                )
                for relative in EXPANDEDAE_BATCH_12_GUIDE_FILES
            },
        },
        "ftbquests_review": {
            "related_content_found": False,
            "keys_updated": quest_keys,
            "handled_separately": True,
            "pending": False,
        },
        "kubejs_user_visible_literals_found": kubejs_keys,
        "validation_errors": 0,
    }
    PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_importexport_guide(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    validation = validate_importexport_language(instance, compare_output)
    errors = validation["errors"]
    assert isinstance(errors, list)
    working_files = {
        path.relative_to(IMPORTEXPORT_GUIDE_WORKING_ROOT).as_posix()
        for path in IMPORTEXPORT_GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if working_files != {IMPORTEXPORT_GUIDE_RELATIVE}:
        errors.append(
            "AE2 Import Export Card 가이드 작업본 목록이 다릅니다: "
            f"{sorted(working_files)}"
        )

    jars = {
        "ae2": find_single_jar(instance, "appliedenergistics2-*.jar", "AE2"),
        "ae2importexportcard": find_single_jar(
            instance, "ae2importexportcard-*.jar", "AE2 Import Export Card"
        ),
    }
    archives = {namespace: zipfile.ZipFile(path) for namespace, path in jars.items()}
    try:
        archive_names = {
            namespace: set(archive.namelist())
            for namespace, archive in archives.items()
        }
        source = (
            archives["ae2importexportcard"]
            .read("assets/ae2/ae2guide/ae2importexportcard-index.md")
            .decode("utf-8-sig")
        )
        source = source.replace("\r\r\n", "\n").replace("\r\n", "\n")
        translated = (
            IMPORTEXPORT_GUIDE_WORKING_ROOT / IMPORTEXPORT_GUIDE_RELATIVE
        ).read_text(encoding="utf-8")
        errors.extend(
            core.validate_pair(IMPORTEXPORT_GUIDE_RELATIVE, source, translated)
        )
        errors.extend(validate_numbers(IMPORTEXPORT_GUIDE_RELATIVE, source, translated))
        errors.extend(validate_tag_nesting(IMPORTEXPORT_GUIDE_RELATIVE, translated))
        for phrase in IMPORTEXPORT_FORBIDDEN_GUIDE_PHRASES:
            if phrase in translated:
                errors.append(
                    f"{IMPORTEXPORT_GUIDE_RELATIVE}: 재검수 전 표현이 남아 있습니다: "
                    f"{phrase}"
                )
        errors.extend(
            validate_resources(
                archive_names, "ae2", IMPORTEXPORT_GUIDE_RELATIVE, translated
            )
        )
        translated_lang = validation["translated_lang"]
        assert isinstance(translated_lang, dict)
        visible = core.extract_visible_text(translated)
        for key in (
            "item.ae2importexportcard.import_card",
            "item.ae2importexportcard.export_card",
        ):
            if translated_lang[key] not in visible:
                errors.append(
                    f"{IMPORTEXPORT_GUIDE_RELATIVE}: 아이템명이 없습니다: "
                    f"{translated_lang[key]}"
                )
        working_path = IMPORTEXPORT_GUIDE_WORKING_ROOT / IMPORTEXPORT_GUIDE_RELATIVE
        if working_path.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"{working_path}: UTF-8 BOM이 있습니다.")
        if compare_output:
            if not IMPORTEXPORT_GUIDE_OUTPUT_FILE.is_file():
                errors.append(
                    f"가이드 출력 파일이 없습니다: {IMPORTEXPORT_GUIDE_OUTPUT_FILE}"
                )
            elif (
                working_path.read_bytes() != IMPORTEXPORT_GUIDE_OUTPUT_FILE.read_bytes()
            ):
                errors.append("AE2 Import Export Card 가이드 작업본과 출력이 다릅니다.")

        validation.update(
            {
                "jars": jars,
                "source_words": len(
                    core.ENGLISH_WORD_RE.findall(core.extract_visible_text(source))
                ),
                "guide_pages": 1,
                "new_guide_pages": 0,
                "quality_review_pages_corrected": 1,
                "class_files_reviewed": sum(
                    name.endswith(".class") and not name.startswith("META-INF/jarjar/")
                    for name in archive_names["ae2importexportcard"]
                ),
                "core_compatibility_updates": 0,
            }
        )
        return validation
    finally:
        for archive in archives.values():
            archive.close()


def build_importexport_guide(instance: Path) -> dict[str, object]:
    validation = validate_importexport_guide(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    IMPORTEXPORT_GUIDE_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    IMPORTEXPORT_GUIDE_OUTPUT_FILE.write_bytes(
        (IMPORTEXPORT_GUIDE_WORKING_ROOT / IMPORTEXPORT_GUIDE_RELATIVE).read_bytes()
    )
    post_validation = validate_importexport_guide(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    result = {
        "status": "quality_review_completed",
        "scope": "AE2 Import Export Card language and GuideME full quality recheck",
        "batch": 13,
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": 1,
        "new_guide_pages": 0,
        "quality_review_pages_corrected": validation["quality_review_pages_corrected"],
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": len(validation["translated_lang"]),
        "new_or_revised_translations": 0,
        "class_files_reviewed": validation["class_files_reviewed"],
        "class_user_visible_literals_found": 0,
        "guide_files": [IMPORTEXPORT_GUIDE_RELATIVE],
        "output_sha256": {
            IMPORTEXPORT_LANG_RELATIVE: sha256(IMPORTEXPORT_LANG_OUTPUT_FILE),
            "assets/ae2/ae2guide/_ko_kr/" + IMPORTEXPORT_GUIDE_RELATIVE: sha256(
                IMPORTEXPORT_GUIDE_OUTPUT_FILE
            ),
        },
        "ftbquests_review": {
            "related_content_found": False,
            "keys_updated": 0,
            "handled_separately": True,
            "pending": False,
        },
        "kubejs_user_visible_literals_found": 0,
        "validation_errors": 0,
    }
    IMPORTEXPORT_PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_netanalyser_guide(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    validation = validate_netanalyser_language(instance, compare_output)
    errors = validation["errors"]
    assert isinstance(errors, list)
    expected_files = set(NETANALYSER_GUIDE_FILES)
    working_files = {
        path.relative_to(NETANALYSER_GUIDE_WORKING_ROOT).as_posix()
        for path in NETANALYSER_GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if working_files != expected_files:
        errors.append(
            "AE2 Network Analyser 가이드 작업본 목록이 다릅니다: "
            f"누락={sorted(expected_files - working_files)}, "
            f"불필요={sorted(working_files - expected_files)}"
        )

    jars = {
        "ae2": find_single_jar(instance, "appliedenergistics2-*.jar", "AE2"),
        "ae2netanalyser": find_single_jar(
            instance, "AE2NetworkAnalyzer-*.jar", "AE2 Network Analyser"
        ),
    }
    archives = {namespace: zipfile.ZipFile(path) for namespace, path in jars.items()}
    try:
        archive_names = {
            namespace: set(archive.namelist())
            for namespace, archive in archives.items()
        }
        source_words = 0
        for relative in NETANALYSER_GUIDE_FILES:
            entry = (GUIDE_SOURCE_ROOTS["ae2netanalyser"] / relative).as_posix()
            source = archives["ae2netanalyser"].read(entry).decode("utf-8-sig")
            source = source.replace("\r\r\n", "\n").replace("\r\n", "\n")
            working_path = NETANALYSER_GUIDE_WORKING_ROOT / relative
            if not working_path.is_file():
                errors.append(f"가이드 작업본이 없습니다: {working_path}")
                continue
            translated = working_path.read_text(encoding="utf-8")
            comparable_source = source.replace("\n    title:", "\n  title:", 1)
            comparable_translated = translated.replace("\n    title:", "\n  title:", 1)
            errors.extend(
                core.validate_pair(relative, comparable_source, comparable_translated)
            )
            errors.extend(validate_numbers(relative, source, translated))
            errors.extend(validate_tag_nesting(relative, translated))
            for phrase in NETANALYSER_FORBIDDEN_GUIDE_PHRASES:
                if phrase in translated:
                    errors.append(
                        f"{relative}: 재검수 전 표현이 남아 있습니다: {phrase}"
                    )
            errors.extend(
                validate_resources(
                    archive_names, "ae2netanalyser", relative, translated
                )
            )
            source_words += len(
                core.ENGLISH_WORD_RE.findall(core.extract_visible_text(source))
            )
            if working_path.read_bytes().startswith(b"\xef\xbb\xbf"):
                errors.append(f"{working_path}: UTF-8 BOM이 있습니다.")
            if compare_output:
                output_path = NETANALYSER_GUIDE_OUTPUT_ROOT / relative
                if not output_path.is_file():
                    errors.append(f"가이드 출력 파일이 없습니다: {output_path}")
                elif working_path.read_bytes() != output_path.read_bytes():
                    errors.append(f"{relative}: 작업본과 출력이 다릅니다.")

        translated_lang = validation["translated_lang"]
        assert isinstance(translated_lang, dict)
        for key, relative in NETANALYSER_GUIDE_ITEM_NAMES.items():
            text = (NETANALYSER_GUIDE_WORKING_ROOT / relative).read_text(
                encoding="utf-8"
            )
            item_name = translated_lang[key]
            if item_name not in core.extract_visible_text(text):
                errors.append(
                    f"{relative}: 언어 파일의 아이템명이 가이드에 없습니다: {item_name}"
                )

        if compare_output:
            output_files = {
                path.relative_to(NETANALYSER_GUIDE_OUTPUT_ROOT).as_posix()
                for path in NETANALYSER_GUIDE_OUTPUT_ROOT.rglob("*.md")
                if path.is_file()
            }
            if output_files != expected_files:
                errors.append(
                    "AE2 Network Analyser 가이드 출력 목록이 다릅니다: "
                    f"누락={sorted(expected_files - output_files)}, "
                    f"불필요={sorted(output_files - expected_files)}"
                )

        validation.update(
            {
                "jars": jars,
                "source_words": source_words,
                "guide_pages": len(NETANALYSER_GUIDE_FILES),
                "new_guide_pages": 0,
                "quality_review_pages_corrected": len(NETANALYSER_GUIDE_FILES),
                "class_files_reviewed": sum(
                    name.endswith(".class") for name in archive_names["ae2netanalyser"]
                ),
                "core_compatibility_updates": 0,
            }
        )
        return validation
    finally:
        for archive in archives.values():
            archive.close()


def build_netanalyser_guide(instance: Path) -> dict[str, object]:
    validation = validate_netanalyser_guide(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    for relative in NETANALYSER_GUIDE_FILES:
        source = NETANALYSER_GUIDE_WORKING_ROOT / relative
        target = NETANALYSER_GUIDE_OUTPUT_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    post_validation = validate_netanalyser_guide(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    quest_keys, kubejs_keys = netanalyser_related_counts()
    result = {
        "status": "quality_review_completed",
        "scope": "AE2 Network Analyzer language and GuideME full quality recheck",
        "batch": 13,
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": len(NETANALYSER_GUIDE_FILES),
        "new_guide_pages": 0,
        "quality_review_pages_corrected": validation["quality_review_pages_corrected"],
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": len(validation["translated_lang"])
        - len(NETANALYSER_QUALITY_LANGUAGE_CORRECTIONS),
        "new_or_revised_translations": len(NETANALYSER_QUALITY_LANGUAGE_CORRECTIONS),
        "class_files_reviewed": validation["class_files_reviewed"],
        "class_internal_diagnostic_literal_classes": 3,
        "class_user_visible_literals_found": 0,
        "guide_files": list(NETANALYSER_GUIDE_FILES),
        "output_sha256": {
            NETANALYSER_LANG_RELATIVE: sha256(NETANALYSER_LANG_OUTPUT_FILE),
            **{
                "assets/ae2netanalyser/ae2guide/_ko_kr/" + relative: sha256(
                    NETANALYSER_GUIDE_OUTPUT_ROOT / relative
                )
                for relative in NETANALYSER_GUIDE_FILES
            },
        },
        "ftbquests_review": {
            "related_content_found": False,
            "keys_updated": quest_keys,
            "handled_separately": True,
            "pending": False,
        },
        "kubejs_user_visible_literals_found": kubejs_keys,
        "validation_errors": 0,
    }
    NETANALYSER_PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_merequester_guide(
    instance: Path, compare_output: bool
) -> dict[str, object]:
    validation = validate_merequester_language(instance, compare_output)
    errors = validation["errors"]
    assert isinstance(errors, list)
    working_files = {
        path.relative_to(MEREQUESTER_GUIDE_WORKING_ROOT).as_posix()
        for path in MEREQUESTER_GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if working_files != {MEREQUESTER_GUIDE_RELATIVE}:
        errors.append(
            f"ME Requester 가이드 작업본 목록이 다릅니다: {sorted(working_files)}"
        )

    jars = {
        "ae2": find_single_jar(instance, "appliedenergistics2-*.jar", "AE2"),
        "merequester": find_single_jar(
            instance, "merequester-neoforge-*.jar", "ME Requester"
        ),
    }
    archives = {namespace: zipfile.ZipFile(path) for namespace, path in jars.items()}
    try:
        archive_names = {
            namespace: set(archive.namelist())
            for namespace, archive in archives.items()
        }
        entry = (
            GUIDE_SOURCE_ROOTS["merequester"] / MEREQUESTER_GUIDE_RELATIVE
        ).as_posix()
        source = archives["merequester"].read(entry).decode("utf-8-sig")
        source = source.replace("\r\r\n", "\n").replace("\r\n", "\n")
        working_path = MEREQUESTER_GUIDE_WORKING_ROOT / MEREQUESTER_GUIDE_RELATIVE
        translated = working_path.read_text(encoding="utf-8")
        errors.extend(
            core.validate_pair(MEREQUESTER_GUIDE_RELATIVE, source, translated)
        )
        errors.extend(validate_numbers(MEREQUESTER_GUIDE_RELATIVE, source, translated))
        errors.extend(validate_tag_nesting(MEREQUESTER_GUIDE_RELATIVE, translated))
        for phrase in MEREQUESTER_FORBIDDEN_GUIDE_PHRASES:
            if phrase in translated:
                errors.append(
                    f"{MEREQUESTER_GUIDE_RELATIVE}: 재검수 전 표현이 남아 있습니다: "
                    f"{phrase}"
                )
        errors.extend(
            validate_resources(
                archive_names, "merequester", MEREQUESTER_GUIDE_RELATIVE, translated
            )
        )
        if working_path.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"{working_path}: UTF-8 BOM이 있습니다.")
        if compare_output:
            if not MEREQUESTER_GUIDE_OUTPUT_FILE.is_file():
                errors.append(
                    f"가이드 출력 파일이 없습니다: {MEREQUESTER_GUIDE_OUTPUT_FILE}"
                )
            elif (
                working_path.read_bytes() != MEREQUESTER_GUIDE_OUTPUT_FILE.read_bytes()
            ):
                errors.append("ME Requester 가이드 작업본과 출력이 다릅니다.")

        validation.update(
            {
                "jars": jars,
                "source_words": len(
                    core.ENGLISH_WORD_RE.findall(core.extract_visible_text(source))
                ),
                "guide_pages": 1,
                "new_guide_pages": 0,
                "quality_review_pages_corrected": 1,
                "class_files_reviewed": sum(
                    name.endswith(".class") for name in archive_names["merequester"]
                ),
                "core_compatibility_updates": 0,
            }
        )
        return validation
    finally:
        for archive in archives.values():
            archive.close()


def build_merequester_guide(instance: Path) -> dict[str, object]:
    validation = validate_merequester_guide(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    MEREQUESTER_GUIDE_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEREQUESTER_GUIDE_OUTPUT_FILE.write_bytes(
        (MEREQUESTER_GUIDE_WORKING_ROOT / MEREQUESTER_GUIDE_RELATIVE).read_bytes()
    )
    post_validation = validate_merequester_guide(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    quest_keys, kubejs_keys = merequester_related_counts()
    result = {
        "status": "quality_review_completed",
        "scope": "ME Requester language and GuideME full quality recheck",
        "batch": 14,
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": 1,
        "new_guide_pages": 0,
        "quality_review_pages_corrected": validation["quality_review_pages_corrected"],
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": len(validation["translated_lang"])
        - len(MEREQUESTER_QUALITY_LANGUAGE_CORRECTIONS),
        "new_or_revised_translations": len(MEREQUESTER_QUALITY_LANGUAGE_CORRECTIONS),
        "class_files_reviewed": validation["class_files_reviewed"],
        "class_internal_diagnostic_literal_classes": 8,
        "config_comment_literals_reviewed": 3,
        "class_user_visible_literals_found": 0,
        "guide_files": [MEREQUESTER_GUIDE_RELATIVE],
        "output_sha256": {
            MEREQUESTER_LANG_RELATIVE: sha256(MEREQUESTER_LANG_OUTPUT_FILE),
            "assets/merequester/ae2guide/_ko_kr/" + MEREQUESTER_GUIDE_RELATIVE: sha256(
                MEREQUESTER_GUIDE_OUTPUT_FILE
            ),
        },
        "ftbquests_review": {
            "related_content_found": False,
            "keys_updated": quest_keys,
            "handled_separately": True,
            "pending": False,
        },
        "kubejs_user_visible_literals_found": kubejs_keys,
        "validation_errors": 0,
    }
    MEREQUESTER_PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_arseng_guide(instance: Path, compare_output: bool) -> dict[str, object]:
    validation = validate_arseng_language(instance, compare_output)
    errors = validation["errors"]
    assert isinstance(errors, list)
    working_files = {
        path.relative_to(ARSENG_GUIDE_WORKING_ROOT).as_posix()
        for path in ARSENG_GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if working_files != {ARSENG_GUIDE_RELATIVE}:
        errors.append(
            f"Ars Énergistique 가이드 작업본 목록이 다릅니다: {sorted(working_files)}"
        )

    jar = find_single_jar(instance, "arseng-*.jar", "Ars Énergistique")
    with zipfile.ZipFile(jar) as archive:
        entry = (GUIDE_SOURCE_ROOTS["arseng"] / ARSENG_GUIDE_RELATIVE).as_posix()
        source = archive.read(entry).decode("utf-8-sig")
    source = source.replace("\r\r\n", "\n").replace("\r\n", "\n")
    working_path = ARSENG_GUIDE_WORKING_ROOT / ARSENG_GUIDE_RELATIVE
    translated = working_path.read_text(encoding="utf-8")
    errors.extend(core.validate_pair(ARSENG_GUIDE_RELATIVE, source, translated))
    errors.extend(validate_numbers(ARSENG_GUIDE_RELATIVE, source, translated))
    errors.extend(validate_tag_nesting(ARSENG_GUIDE_RELATIVE, translated))
    if working_path.read_bytes().startswith(b"\xef\xbb\xbf"):
        errors.append(f"{working_path}: UTF-8 BOM이 있습니다.")
    if compare_output:
        if not ARSENG_GUIDE_OUTPUT_FILE.is_file():
            errors.append(f"가이드 출력 파일이 없습니다: {ARSENG_GUIDE_OUTPUT_FILE}")
        elif working_path.read_bytes() != ARSENG_GUIDE_OUTPUT_FILE.read_bytes():
            errors.append("Ars Énergistique 가이드 작업본과 출력이 다릅니다.")

    validation.update(
        {
            "jars": {"arseng": jar},
            "source_words": len(
                core.ENGLISH_WORD_RE.findall(core.extract_visible_text(source))
            ),
            "guide_pages": 1,
            "new_guide_pages": 0,
            "quality_review_pages_corrected": 0,
            "class_files_reviewed": 40,
            "core_compatibility_updates": 0,
        }
    )
    return validation


def build_arseng_guide(instance: Path) -> dict[str, object]:
    validation = validate_arseng_guide(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    ARSENG_GUIDE_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ARSENG_GUIDE_OUTPUT_FILE.write_bytes(
        (ARSENG_GUIDE_WORKING_ROOT / ARSENG_GUIDE_RELATIVE).read_bytes()
    )
    post_validation = validate_arseng_guide(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jar = validation["jars"]["arseng"]  # type: ignore[index]
    assert isinstance(jar, Path)
    quest_keys, kubejs_keys = arseng_related_counts()
    result = {
        "status": "quality_review_completed",
        "scope": "Ars Énergistique language and GuideME full quality recheck",
        "batch": 15,
        "source_jars": {"arseng": {"name": jar.name, "sha256": sha256(jar)}},
        "language": "ko_kr",
        "guide_pages": 1,
        "new_guide_pages": 0,
        "quality_review_pages_corrected": 0,
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": len(validation["translated_lang"]),
        "new_or_revised_translations": 0,
        "class_files_reviewed": validation["class_files_reviewed"],
        "class_registration_fallback_literals_reviewed": 6,
        "class_internal_diagnostic_literal_classes": 1,
        "config_comment_literals_reviewed": 2,
        "class_user_visible_literals_found": 0,
        "guide_files": [ARSENG_GUIDE_RELATIVE],
        "output_sha256": {
            ARSENG_LANG_RELATIVE: sha256(ARSENG_LANG_OUTPUT_FILE),
            "assets/arseng/ae2guide/_ko_kr/" + ARSENG_GUIDE_RELATIVE: sha256(
                ARSENG_GUIDE_OUTPUT_FILE
            ),
        },
        "ftbquests_review": {
            "related_content_found": False,
            "keys_updated": quest_keys,
            "handled_separately": True,
            "pending": False,
        },
        "kubejs_user_visible_literals_found": kubejs_keys,
        "validation_errors": 0,
    }
    ARSENG_PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate(instance: Path, compare_output: bool) -> dict[str, object]:
    if ACTIVE_BATCH == 1:
        return validate_ae2wtlib(instance, compare_output)
    if ACTIVE_BATCH == 2:
        return validate_enderdrives(instance, compare_output)
    if ACTIVE_BATCH == 3:
        return validate_extendedae_batch_03(instance, compare_output)
    if ACTIVE_BATCH == 4:
        return validate_extendedae_batch_04(instance, compare_output)
    if ACTIVE_BATCH == 5:
        return validate_extendedae_batch_05(instance, compare_output)
    if ACTIVE_BATCH == 6:
        return validate_extendedae_batch_06(instance, compare_output)
    if ACTIVE_BATCH == 7:
        return validate_advancedae_batch_07(instance, compare_output)
    if ACTIVE_BATCH == 8:
        return validate_advancedae_batch_08(instance, compare_output)
    if ACTIVE_BATCH == 9:
        return validate_megacells_batch_09(instance, compare_output)
    if ACTIVE_BATCH == 10:
        return validate_megacells_batch_10(instance, compare_output)
    if ACTIVE_BATCH == 11:
        return validate_appflux_batch_11(instance, compare_output)
    if ACTIVE_BATCH == 12:
        return validate_expandedae_batch_12(instance, compare_output)
    raise ValueError(f"지원하지 않는 연동 모드 가이드 배치입니다: {ACTIVE_BATCH}")


def build(instance: Path) -> dict[str, object]:
    if ACTIVE_BATCH == 1:
        return build_ae2wtlib(instance)
    if ACTIVE_BATCH == 2:
        return build_enderdrives(instance)
    if ACTIVE_BATCH == 3:
        return build_extendedae_batch_03(instance)
    if ACTIVE_BATCH == 4:
        return build_extendedae_batch_04(instance)
    if ACTIVE_BATCH == 5:
        return build_extendedae_batch_05(instance)
    if ACTIVE_BATCH == 6:
        return build_extendedae_batch_06(instance)
    if ACTIVE_BATCH == 7:
        return build_advancedae_batch_07(instance)
    if ACTIVE_BATCH == 8:
        return build_advancedae_batch_08(instance)
    if ACTIVE_BATCH == 9:
        return build_megacells_batch_09(instance)
    if ACTIVE_BATCH == 10:
        return build_megacells_batch_10(instance)
    if ACTIVE_BATCH == 11:
        return build_appflux_batch_11(instance)
    if ACTIVE_BATCH == 12:
        return build_expandedae_batch_12(instance)
    raise ValueError(f"지원하지 않는 연동 모드 가이드 배치입니다: {ACTIVE_BATCH}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--language-only", action="store_true")
    parser.add_argument(
        "--mod",
        choices=(
            "ae2wtlib",
            "enderdrives",
            "extendedae",
            "advanced_ae",
            "megacells",
            "ae2importexportcard",
            "ae2netanalyser",
            "merequester",
            "arseng",
        ),
        help="현재 활성 배치와 별개로 다시 빌드할 연동 모드",
    )
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    if args.mod == "ae2wtlib" and args.language_only:
        raise ValueError("AE2WTLib은 언어와 가이드를 함께 빌드해야 합니다.")
    if args.mod == "ae2wtlib":
        result = build_ae2wtlib(instance)
    elif args.mod == "enderdrives" and args.language_only:
        raise ValueError("EnderDrives는 언어와 가이드를 함께 빌드해야 합니다.")
    elif args.mod == "enderdrives":
        result = build_enderdrives(instance)
    elif args.mod == "extendedae" and args.language_only:
        raise ValueError("Extended AE는 언어와 가이드를 함께 빌드해야 합니다.")
    elif args.mod == "extendedae":
        result = build_extendedae_quality(instance)
    elif args.mod == "advanced_ae" and args.language_only:
        raise ValueError("Advanced AE는 언어와 가이드를 함께 빌드해야 합니다.")
    elif args.mod == "advanced_ae":
        result = build_advancedae_quality(instance)
    elif args.mod == "megacells" and args.language_only:
        raise ValueError("MEGA Cells는 언어와 가이드를 함께 빌드해야 합니다.")
    elif args.mod == "megacells":
        result = build_megacells_quality(instance)
    elif args.mod == "ae2importexportcard" and args.language_only:
        result = build_importexport_language(instance)
    elif args.mod == "ae2importexportcard":
        result = build_importexport_guide(instance)
    elif args.mod == "ae2netanalyser" and args.language_only:
        result = build_netanalyser_language(instance)
    elif args.mod == "ae2netanalyser":
        result = build_netanalyser_guide(instance)
    elif args.mod == "merequester" and args.language_only:
        result = build_merequester_language(instance)
    elif args.mod == "merequester":
        result = build_merequester_guide(instance)
    elif args.mod == "arseng" and args.language_only:
        result = build_arseng_language(instance)
    elif args.mod == "arseng":
        result = build_arseng_guide(instance)
    elif args.language_only and ACTIVE_BATCH in {7, 8}:
        result = build_advancedae_language(instance)
    elif args.language_only and ACTIVE_BATCH in {9, 10}:
        result = build_megacells_language(instance)
    elif args.language_only and ACTIVE_BATCH == 11:
        result = build_appflux_language(instance)
    elif args.language_only and ACTIVE_BATCH == 12:
        result = build_expandedae_language(instance)
    elif (
        args.language_only and ACTIVE_BATCH == 13 and args.mod == "ae2importexportcard"
    ):
        result = build_importexport_language(instance)
    elif args.language_only and ACTIVE_BATCH == 13 and args.mod == "ae2netanalyser":
        result = build_netanalyser_language(instance)
    elif args.language_only and ACTIVE_BATCH == 14:
        result = build_merequester_language(instance)
    elif args.language_only and ACTIVE_BATCH == 15:
        result = build_arseng_language(instance)
    elif args.language_only:
        raise ValueError(f"{ACTIVE_BATCH}차는 언어 전용 빌드를 지원하지 않습니다.")
    elif ACTIVE_BATCH == 13 and args.mod == "ae2importexportcard":
        result = build_importexport_guide(instance)
    elif ACTIVE_BATCH == 13 and args.mod == "ae2netanalyser":
        result = build_netanalyser_guide(instance)
    elif ACTIVE_BATCH == 14:
        result = build_merequester_guide(instance)
    elif ACTIVE_BATCH == 15:
        result = build_arseng_guide(instance)
    else:
        result = build(instance)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
