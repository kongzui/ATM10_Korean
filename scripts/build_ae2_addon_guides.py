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

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCEPACK_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean"
ADDON_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/ae2wtlib"
GUIDE_WORKING_ROOT = ADDON_WORKING_ROOT / "ae2guide/_ko_kr"
LANG_WORKING_FILE = ADDON_WORKING_ROOT / "lang/ko_kr.json"
CORE_COMPAT_WORKING_FILE = (
    PROJECT_ROOT
    / "working/ae2/ae2guide/_ko_kr/items-blocks-machines/wireless_terminals.md"
)
PROGRESS_FILE = PROJECT_ROOT / "working/ae2_addons/guide_progress.json"

ACTIVE_BATCH = 12
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
NUMBER_RE = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?(?:\^\d+)?(?:k|K)?")
EXTENDEDAE_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/extendedae"
EXTENDEDAE_LANG_WORKING_FILE = EXTENDEDAE_WORKING_ROOT / "lang/ko_kr.json"
EXTENDEDAE_LANG_RELATIVE = "assets/extendedae/lang/ko_kr.json"
EXTENDEDAE_LANG_OUTPUT_FILE = RESOURCEPACK_ROOT / EXTENDEDAE_LANG_RELATIVE
EXTENDEDAE_GUIDE_WORKING_ROOT = EXTENDEDAE_WORKING_ROOT / "ae2guide/_ko_kr"
EXTENDEDAE_GUIDE_OUTPUT_ROOT = RESOURCEPACK_ROOT / "assets/extendedae/ae2guide/_ko_kr"
EXTENDEDAE_QUEST_OVERRIDES_FILE = EXTENDEDAE_WORKING_ROOT / "quest_overrides.json"
EXTENDEDAE_INFINITY_CELLS_RELATIVE = Path(
    "kubejs/startup_scripts/ExtendedAE/InfinityCells.js"
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
ADVANCEDAE_LANGUAGE_COMPLETION_FILE = (
    ADVANCEDAE_WORKING_ROOT / "language_completion.json"
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
    PROJECT_ROOT / "output/overrides" / EXPANDEDAE_KUBEJS_RELATIVE
)
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
        "status": "batch_01_completed",
        "scope": "AE2WTLib GuideME guide batch 01",
        "batch": ACTIVE_BATCH,
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
            "terminology_mismatch_found": True,
            "mismatch": "유니버설 무선 터미널 -> 무선 범용 터미널",
            "keys_updated": 3,
            "handled_separately": True,
        },
        "kubejs_user_visible_literals_found": 0,
        "validation_errors": 0,
    }
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def validate_numbers(relative: str, source: str, translated: str) -> list[str]:
    expected = sorted(NUMBER_RE.findall(core.extract_visible_text(source)))
    actual = sorted(NUMBER_RE.findall(core.extract_visible_text(translated)))
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
            "existing_korean_reused": 0,
            "new_or_revised_translations": len(translated_lang),
            "guide_pages": len(ENDERDRIVES_GUIDE_FILES),
            "new_guide_pages": len(ENDERDRIVES_GUIDE_FILES),
            "core_compatibility_updates": 0,
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
    }
    result = {
        "status": "batch_02_completed",
        "scope": "EnderDrives GuideME guide batch 02",
        "batch": ACTIVE_BATCH,
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": len(ENDERDRIVES_GUIDE_FILES),
        "new_guide_pages": len(ENDERDRIVES_GUIDE_FILES),
        "core_compatibility_updates": 0,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "new_or_revised_translations": validation["new_or_revised_translations"],
        "guide_files": list(ENDERDRIVES_GUIDE_FILES),
        "output_sha256": output_files,
        "ftbquests_review": {"related_content_found": False, "keys_updated": 0},
        "kubejs_user_visible_literals_found": 0,
        "validation_errors": 0,
    }
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(
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
    return len(quest_overrides), 0


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
        "legacy_reference_keys": 57,
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
    if len(source_lines) != len(working_lines) or changed_lines != [17]:
        errors.append("ExpandedAE KubeJS 덮어쓰기 범위가 한 공지 문장을 벗어났습니다.")
    expected_announcement = (
        '  addAnnouncement("4.5", "추가된 모드: Expanded AE, '
        'Industrialization Overdrive, RFTools Storage")'
    )
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
        elif (
            EXPANDEDAE_KUBEJS_WORKING_FILE.read_bytes()
            != EXPANDEDAE_KUBEJS_OUTPUT_FILE.read_bytes()
        ):
            errors.append("ExpandedAE KubeJS 작업본과 출력이 다릅니다.")

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
        "legacy_reference_keys": 69,
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
    raise ValueError(f"지원하지 않는 연동 모드 가이드 배치입니다: {ACTIVE_BATCH}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--language-only", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    if args.language_only and ACTIVE_BATCH in {7, 8}:
        result = build_advancedae_language(instance)
    elif args.language_only and ACTIVE_BATCH in {9, 10}:
        result = build_megacells_language(instance)
    elif args.language_only and ACTIVE_BATCH == 11:
        result = build_appflux_language(instance)
    elif args.language_only and ACTIVE_BATCH == 12:
        result = build_expandedae_language(instance)
    elif args.language_only:
        raise ValueError(f"{ACTIVE_BATCH}차는 언어 전용 빌드를 지원하지 않습니다.")
    else:
        result = build(instance)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
