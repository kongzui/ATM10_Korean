#!/usr/bin/env python3
"""주요 모드군의 설치 범위와 언어 작업본을 준비하고 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

import audit_ftbquests_titles as quest_audit
import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
TRANSLATION_KEY = re.compile(r"^[a-z0-9_.-]+(?:\.[a-z0-9_.-]+)+$")


@dataclass(frozen=True)
class Target:
    family: str
    jar_prefix: str
    namespace: str
    label: str
    direct_integration: bool = False
    language_target: bool = True


TARGETS = (
    Target("mekanism", "Mekanism-", "mekanism", "Mekanism"),
    Target(
        "mekanism",
        "MekanismGenerators-",
        "mekanismgenerators",
        "Mekanism Generators",
    ),
    Target("mekanism", "MekanismTools-", "mekanismtools", "Mekanism Tools"),
    Target("mekanism", "mekanismcovers-", "mekanismcovers", "Mekanism Covers"),
    Target(
        "mekanism",
        "mekanisticrouters-",
        "mekanisticrouters",
        "Mekanistic Routers",
    ),
    Target(
        "mekanism",
        "JustEnoughMekanismMultiblocks-",
        "jei_mekanism_multiblocks",
        "Just Enough Mekanism Multiblocks",
    ),
    Target("mekanism", "mekmm-", "mekmm", "MEKMM"),
    Target(
        "mekanism",
        "GravitationalModulatingAdditionalUnit-",
        "gmut",
        "Gravitational Modulating Additional Unit",
        True,
    ),
    Target(
        "mekanism",
        "Applied-Mekanistics-",
        "appmek",
        "Applied Mekanistics",
        True,
    ),
    Target(
        "mekanism",
        "refinedstorage-mekanism-integration-",
        "refinedstorage_mekanism_integration",
        "Refined Storage - Mekanism Integration",
        True,
    ),
    Target("powah_flux", "Powah-", "powah", "Powah!"),
    Target("powah_flux", "Powah-", "lollipop", "Lollipop"),
    Target("powah_flux", "FluxNetworks-", "fluxnetworks", "Flux Networks"),
    Target("ars_nouveau", "ars_nouveau-", "ars_nouveau", "Ars Nouveau"),
    Target("ars_nouveau", "ars_additions-", "ars_additions", "Ars Additions"),
    Target("ars_nouveau", "ars_controle-", "ars_controle", "Ars Controle"),
    Target("ars_nouveau", "ars_creo-", "ars_creo", "Ars Creo"),
    Target("ars_nouveau", "ars_elemancy-", "ars_elemancy", "Ars Elemancy"),
    Target("ars_nouveau", "ars_elemental-", "ars_elemental", "Ars Elemental"),
    Target("ars_nouveau", "ars_ocultas-", "ars_ocultas", "Ars Ocultas"),
    Target("ars_nouveau", "ars_technica-", "ars_technica", "Ars Technica"),
    Target("ars_nouveau", "ars_unification-", "ars_unification", "Ars Unification"),
    Target(
        "ars_nouveau",
        "not_enough_glyphs-",
        "not_enough_glyphs",
        "Not Enough Glyphs",
    ),
    Target(
        "ars_nouveau",
        "starbunclemania-",
        "starbunclemania",
        "Starbuncle Mania",
    ),
    Target("ars_nouveau", "arseng-", "arseng", "Ars Énergistique", True),
    Target(
        "ars_nouveau",
        "allthearcanistgear-",
        "allthearcanistgear",
        "All the Arcanist Gear",
        True,
    ),
    Target("evilcraft", "evilcraft-", "evilcraft", "EvilCraft"),
    Target("evilcraft", "evilcraft-", "evilcraftcompat", "EvilCraft Compat"),
    Target(
        "twilight_forest",
        "twilightforest-",
        "twilightforest",
        "The Twilight Forest",
    ),
    Target(
        "cataclysm",
        "L_Ender's Cataclysm ",
        "cataclysm",
        "L_Ender's Cataclysm",
    ),
    Target(
        "undergarden",
        "The_Undergarden-",
        "undergarden",
        "The Undergarden",
    ),
    Target("aether", "aether-", "aether", "The Aether"),
    Target(
        "bumblezone",
        "the_bumblezone-",
        "the_bumblezone",
        "The Bumblezone",
    ),
    Target(
        "eternal_starlight",
        "eternalstarlight-",
        "eternal_starlight",
        "Eternal Starlight",
    ),
    Target(
        "deeper_and_darker",
        "deeperdarker-",
        "deeperdarker",
        "Deeper and Darker",
    ),
    Target(
        "refined_storage",
        "refinedstorage-neoforge-",
        "refinedstorage",
        "Refined Storage 2",
    ),
    Target(
        "refined_storage",
        "ExtraDisks-",
        "extradisks",
        "Extra Disks",
    ),
    Target(
        "refined_storage",
        "ExtraStorage-",
        "extrastorage",
        "Extra Storage",
    ),
    Target(
        "refined_storage",
        "refined-types-",
        "refinedtypes",
        "Refined Types",
    ),
    Target(
        "refined_storage",
        "universalgrid-",
        "universalgrid",
        "Universal Grid",
    ),
    Target(
        "refined_storage",
        "refinedstorage-curios-integration-",
        "refinedstorage_curios_integration",
        "Refined Storage - Curios Integration",
        True,
    ),
    Target(
        "refined_storage",
        "refinedstorage-jei-integration-",
        "refinedstorage_jei_integration",
        "Refined Storage - JEI Integration",
        True,
    ),
    Target(
        "refined_storage",
        "refinedstorage-mekanism-integration-",
        "refinedstorage_mekanism_integration",
        "Refined Storage - Mekanism Integration",
        True,
    ),
    Target(
        "refined_storage",
        "refinedstorage-quartz-arsenal-",
        "refinedstorage_quartz_arsenal",
        "Quartz Arsenal",
        True,
    ),
    Target(
        "refined_storage",
        "cabletiers-",
        "cabletiers",
        "Cable Tiers",
        True,
    ),
    Target(
        "refined_storage",
        "interdimensionalwirelesstransmitter-",
        "interdimensionalwirelesstransmitter",
        "Interdimensional Wireless Transmitter",
        True,
    ),
    Target(
        "functional_storage",
        "functionalstorage-",
        "functionalstorage",
        "Functional Storage",
    ),
    Target(
        "functional_storage",
        "pocketstorage-",
        "pocketstorage",
        "Pocket Storage",
    ),
    Target(
        "functional_storage",
        "EnderStorage-",
        "enderstorage",
        "EnderStorage",
    ),
    Target("basic_logistics", "pipez-", "pipez", "Pipez"),
    Target(
        "basic_logistics",
        "Modern-Dynamics-",
        "moderndynamics",
        "Modern Dynamics",
    ),
    Target("basic_logistics", "xnet-", "xnet", "XNet"),
    Target(
        "modular_routers",
        "modular-routers-",
        "modularrouters",
        "Modular Routers",
    ),
    Target(
        "hostile_neural_networks",
        "HostileNeuralNetworks-",
        "hostilenetworks",
        "Hostile Neural Networks",
    ),
    Target(
        "iron_jetpacks_equipment",
        "IronJetpacks-",
        "ironjetpacks",
        "Iron Jetpacks",
    ),
    Target(
        "iron_jetpacks_equipment",
        "baubley-heart-canisters-",
        "bhc",
        "Baubley Heart Canisters",
    ),
    Target(
        "iron_jetpacks_equipment",
        "ToolBelt-",
        "toolbelt",
        "Tool Belt",
    ),
    Target(
        "iron_jetpacks_equipment",
        "simplemagnets-",
        "simplemagnets",
        "Simple Magnets",
    ),
    Target(
        "early_midgame_infrastructure",
        "ironfurnaces-neoforge-",
        "ironfurnaces",
        "Iron Furnaces",
    ),
    Target(
        "early_midgame_infrastructure",
        "easy-villagers-neoforge-",
        "easy_villagers",
        "Easy Villagers",
    ),
    Target(
        "early_midgame_infrastructure",
        "mininggadgets-",
        "mininggadgets",
        "Mining Gadgets",
    ),
    Target(
        "early_midgame_infrastructure",
        "buildinggadgets2-",
        "buildinggadgets2",
        "Building Gadgets",
    ),
    Target(
        "early_midgame_infrastructure",
        "mob_grinding_utils-",
        "mob_grinding_utils",
        "Mob Grinding Utils",
    ),
    Target(
        "early_midgame_infrastructure",
        "itemcollectors-",
        "itemcollectors",
        "Item Collectors",
    ),
    Target(
        "botany_pots_trees",
        "botanypots-neoforge-",
        "botanypots",
        "Botany Pots",
    ),
    Target(
        "botany_pots_trees",
        "botanytrees-neoforge-",
        "botanytrees",
        "Botany Trees",
        False,
        False,
    ),
    Target(
        "all_the_ores_compressed",
        "alltheores-",
        "alltheores",
        "All The Ores",
    ),
    Target(
        "all_the_ores_compressed",
        "allthecompressed-",
        "allthecompressed",
        "All The Compressed",
    ),
    Target(
        "productive_metalworks",
        "productivemetalworks-",
        "productivemetalworks",
        "Productive Metalworks",
    ),
    Target(
        "compact_machines",
        "compactmachines-neoforge-",
        "compactmachines",
        "Compact Machines",
    ),
    Target("create", "create-1.21.1-", "create", "Create"),
    Target(
        "create",
        "CreateDragonsPlus-",
        "create_dragons_plus",
        "Create: Dragons Plus",
    ),
    Target(
        "create",
        "createaddition-",
        "createaddition",
        "Create Crafts & Additions",
    ),
    Target(
        "create",
        "create-enchantment-industry-",
        "create_enchantment_industry",
        "Create Enchantment Industry",
    ),
    Target(
        "create",
        "create_aquatic_ambitions-",
        "create_aquatic_ambitions",
        "Create Aquatic Ambitions",
    ),
    Target(
        "create",
        "create_hypertube-",
        "create_hypertube",
        "Create Hypertube",
    ),
    Target(
        "create",
        "bellsandwhistles-",
        "bellsandwhistles",
        "Create: Bells & Whistles",
    ),
    Target(
        "modern_industrialization",
        "Modern-Industrialization-",
        "modern_industrialization",
        "Modern Industrialization",
    ),
    Target(
        "modern_industrialization",
        "extended-industrialization-",
        "extended_industrialization",
        "Extended Industrialization",
    ),
    Target(
        "modern_industrialization",
        "industrialization_overdrive-",
        "industrialization_overdrive",
        "Industrialization Overdrive",
    ),
    Target(
        "immersive_engineering",
        "ImmersiveEngineering-",
        "immersiveengineering",
        "Immersive Engineering",
    ),
    Target(
        "pneumaticcraft",
        "pneumaticcraft-repressurized-",
        "pneumaticcraft",
        "PneumaticCraft: Repressurized",
    ),
    Target(
        "industrial_foregoing",
        "industrialforegoing-",
        "industrialforegoing",
        "Industrial Foregoing",
    ),
    Target(
        "industrial_foregoing",
        "industrial-foregoing-souls-",
        "industrialforegoingsouls",
        "Industrial Foregoing Souls",
    ),
    Target(
        "industrial_foregoing",
        "mifa-neoforge-",
        "mifa",
        "More Industrial Foregoing Addons",
        True,
    ),
    Target(
        "industrial_foregoing",
        "soulplied_energistics-",
        "soulplied_energistics",
        "Soulplied Energistics",
        True,
    ),
    Target(
        "just_dire_things",
        "justdirethings-",
        "justdirethings",
        "Just Dire Things",
    ),
    Target(
        "actually_additions",
        "actuallyadditions-",
        "actuallyadditions",
        "Actually Additions",
    ),
    Target("oritech", "oritech-neoforge-", "oritech", "Oritech"),
    Target(
        "extreme_reactors",
        "ExtremeReactors2-",
        "bigreactors",
        "Extreme Reactors",
    ),
    Target("extreme_reactors", "ZeroCore2-", "zerocore", "ZeroCore"),
    Target(
        "railcraft_reborn",
        "railcraft-reborn-",
        "railcraft",
        "Railcraft Reborn",
    ),
    Target(
        "cc_tweaked",
        "cc-tweaked-1.21.1-forge-1.120.0",
        "computercraft",
        "CC: Tweaked",
    ),
    Target(
        "cc_tweaked",
        "AdvancedPeripherals-",
        "advancedperipherals",
        "Advanced Peripherals",
    ),
    Target("cc_tweaked", "morered-1.21.1-6.0", "morered", "More Red"),
    Target(
        "cc_tweaked",
        "MoreRed-CCT-Compat-",
        "moreredxcctcompat",
        "More Red × CC: Tweaked Compat",
        True,
        False,
    ),
    Target(
        "super_factory_manager",
        "Super Factory Manager (SFM)-MC1.21.1-",
        "sfm",
        "Super Factory Manager",
    ),
    Target("rftools", "rftoolsbase-", "rftoolsbase", "RFTools Base"),
    Target("rftools", "rftoolsbuilder-", "rftoolsbuilder", "RFTools Builder"),
    Target("rftools", "rftoolspower-", "rftoolspower", "RFTools Power"),
    Target("rftools", "rftoolsstorage-", "rftoolsstorage", "RFTools Storage"),
    Target("rftools", "rftoolsutility-", "rftoolsutility", "RFTools Utility"),
    Target("xycraft", "xycraft_core-", "xycraft_core", "XyCraft Core"),
    Target("xycraft", "xycraft_machines-", "xycraft_machines", "XyCraft Machines"),
    Target("xycraft", "xycraft_world-", "xycraft_world", "XyCraft World"),
    Target("xycraft", "xycraft_override-", "xycraft_override", "XyCraft Override"),
    Target("laser_io_mffs", "laserio-", "laserio", "LaserIO"),
    Target("laser_io_mffs", "mffs-", "mffs", "MFFS"),
    Target("pylons", "pylons-", "pylons", "Pylons"),
    Target("steves_carts", "stevescarts-", "stevescarts", "Steve's Carts"),
    Target(
        "draconic_evolution",
        "Draconic-Evolution-",
        "draconicevolution",
        "Draconic Evolution",
    ),
    Target(
        "draconic_evolution",
        "BrandonsCore-",
        "brandonscore",
        "Brandon's Core",
        True,
        False,
    ),
    Target(
        "irons_spells",
        "irons_spellbooks-",
        "irons_spellbooks",
        "Iron's Spells 'n Spellbooks",
    ),
    Target(
        "irons_spells",
        "irons_jewelry-",
        "irons_jewelry",
        "Iron's Jewelry",
        True,
    ),
    Target(
        "irons_spells",
        "irons_lib-",
        "irons_lib",
        "Iron's Lib",
        True,
    ),
    Target(
        "irons_spells",
        "irons_lib-",
        "irons_patreon_lib",
        "Iron's Patreon Lib",
        True,
    ),
    Target(
        "forbidden_arcanus",
        "forbidden_arcanus-",
        "forbidden_arcanus",
        "Forbidden and Arcanus",
    ),
    Target(
        "natures_aura",
        "NaturesAura-",
        "naturesaura",
        "Nature's Aura",
    ),
)

FAMILY_LABELS = {
    "mekanism": "Mekanism",
    "powah_flux": "Powah!·Flux Networks",
    "ars_nouveau": "Ars Nouveau",
    "evilcraft": "EvilCraft",
    "twilight_forest": "The Twilight Forest",
    "cataclysm": "L_Ender's Cataclysm",
    "undergarden": "The Undergarden",
    "aether": "The Aether",
    "bumblezone": "The Bumblezone",
    "eternal_starlight": "Eternal Starlight",
    "deeper_and_darker": "Deeper and Darker",
    "refined_storage": "Refined Storage 2",
    "functional_storage": "Functional Storage·Pocket Storage·EnderStorage",
    "basic_logistics": "Pipez·Modern Dynamics·XNet",
    "modular_routers": "Modular Routers",
    "hostile_neural_networks": "Hostile Neural Networks",
    "iron_jetpacks_equipment": "Iron Jetpacks·장비 편의",
    "early_midgame_infrastructure": "초중반 기반 시설",
    "botany_pots_trees": "Botany Pots·Botany Trees",
    "all_the_ores_compressed": "All The Ores·All The Compressed",
    "productive_metalworks": "Productive Metalworks",
    "compact_machines": "Compact Machines",
    "create": "Create",
    "modern_industrialization": "Modern Industrialization",
    "immersive_engineering": "Immersive Engineering",
    "pneumaticcraft": "PneumaticCraft: Repressurized",
    "industrial_foregoing": "Industrial Foregoing·Industrial Foregoing Souls",
    "just_dire_things": "Just Dire Things",
    "actually_additions": "Actually Additions",
    "oritech": "Oritech",
    "extreme_reactors": "Extreme Reactors·ZeroCore",
    "railcraft_reborn": "Railcraft Reborn",
    "cc_tweaked": "CC: Tweaked·Advanced Peripherals·More Red",
    "super_factory_manager": "Super Factory Manager",
    "rftools": "RFTools",
    "xycraft": "XyCraft",
    "laser_io_mffs": "LaserIO·MFFS",
    "pylons": "Pylons",
    "steves_carts": "Steve's Carts",
    "draconic_evolution": "Draconic Evolution",
    "irons_spells": "Iron's Spells 'n Spellbooks",
    "forbidden_arcanus": "Forbidden and Arcanus",
    "natures_aura": "Nature's Aura",
}

QUEST_CHAPTERS = {
    "mekanism": ("mekanism", "mekanism_reactors"),
    "powah_flux": ("powah",),
    "ars_nouveau": ("ars_nouveau",),
    "evilcraft": ("evilcraft",),
    "twilight_forest": ("twilight_forest",),
    "cataclysm": ("cataclysm",),
    "undergarden": ("undergarden",),
    "aether": ("aether",),
    "bumblezone": ("bumblezone",),
    "eternal_starlight": ("eternal_starlight",),
    "deeper_and_darker": ("deeper_and_darker",),
    "refined_storage": ("refined_storage",),
    "functional_storage": (),
    "basic_logistics": (),
    "modular_routers": ("modular_router",),
    "hostile_neural_networks": ("hostile_neural_networks",),
    "iron_jetpacks_equipment": (),
    "early_midgame_infrastructure": (),
    "botany_pots_trees": (),
    "all_the_ores_compressed": (),
    "productive_metalworks": (),
    "compact_machines": (),
    "create": ("create",),
    "modern_industrialization": (
        "mi_steam",
        "mi_electric",
        "mi_digital",
        "mi_endgame",
    ),
    "immersive_engineering": ("immersive_engineering",),
    "pneumaticcraft": ("pneumaticcraft",),
    "industrial_foregoing": ("industrial_foregoing",),
    "just_dire_things": ("justdirethings",),
    "actually_additions": (),
    "oritech": ("oritech",),
    "extreme_reactors": ("extreme_reactors",),
    "railcraft_reborn": ("railcraft",),
    "cc_tweaked": (),
    "super_factory_manager": (),
    "rftools": (),
    "xycraft": ("xycraft",),
    "laser_io_mffs": (),
    "pylons": ("pylons",),
    "steves_carts": (),
    "draconic_evolution": ("draconic_evolution",),
    "irons_spells": ("iron_spells_and_spellbooks",),
    "forbidden_arcanus": ("forbidden__arcanus",),
    "natures_aura": ("natures_aura",),
}

QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
QUEST_CHAPTER_OUTPUT = (
    PROJECT_ROOT / "output/overrides/config/ftbquests/quests/chapters"
)

QUEST_VALIDATION_TEXT_EQUIVALENTS = {
    "quest.7B3613C01F0B1373.quest_desc": (("1 Billion", "10억"),),
}

QUEST_TEXT_MARKERS = {
    "functional_storage": (
        "functional storage",
        "pocket storage",
        "enderstorage",
        "ender storage",
    ),
    "basic_logistics": ("pipez", "modern dynamics", "xnet"),
    "modular_routers": ("modular routers", "modularrouters"),
    "hostile_neural_networks": (
        "hostile neural networks",
        "hostilenetworks",
    ),
    "iron_jetpacks_equipment": (
        "iron jetpacks",
        "ironjetpacks",
        "baubley heart canisters",
        "baubley-heart-canisters",
        "tool belt",
        "toolbelt",
        "simple magnets",
        "simplemagnets",
    ),
    "early_midgame_infrastructure": (
        "iron furnaces",
        "ironfurnaces",
        "easy villagers",
        "easy_villagers",
        "mining gadgets",
        "mininggadgets",
        "building gadgets",
        "buildinggadgets2",
        "mob grinding utils",
        "mob_grinding_utils",
        "item collectors",
        "itemcollectors",
    ),
    "botany_pots_trees": (
        "botany pots",
        "botanypots",
        "botany trees",
        "botanytrees",
    ),
    "all_the_ores_compressed": (
        "all the ores",
        "alltheores",
        "all the compressed",
        "allthecompressed",
    ),
    "productive_metalworks": (
        "productive metalworks",
        "productivemetalworks",
    ),
    "compact_machines": (
        "compact machines",
        "compactmachines",
    ),
    "create": (
        "&6&lcreate",
        "create:",
        "create dragons plus",
        "createaddition",
        "create enchantment industry",
        "create aquatic ambitions",
        "create hypertube",
        "bells and whistles",
        "bellsandwhistles",
    ),
    "modern_industrialization": (
        "modern industrialization",
        "modern_industrialization",
        "extended industrialization",
        "extended_industrialization",
        "industrialization overdrive",
        "industrialization_overdrive",
    ),
    "immersive_engineering": (
        "immersive engineering",
        "immersiveengineering",
    ),
    "pneumaticcraft": (
        "pneumaticcraft",
        "pneumaticcraft: repressurized",
    ),
    "industrial_foregoing": (
        "industrial foregoing",
        "industrialforegoing",
        "industrial foregoing souls",
        "industrialforegoingsouls",
    ),
    "just_dire_things": (
        "just dire things",
        "justdirethings",
    ),
    "actually_additions": (
        "actually additions",
        "actuallyadditions",
    ),
    "oritech": ("oritech",),
    "extreme_reactors": (
        "extreme reactors",
        "big reactors",
        "bigreactors",
        "zerocore",
    ),
    "railcraft_reborn": (
        "railcraft",
        "rail craft",
    ),
    "cc_tweaked": (
        "cc: tweaked",
        "computercraft",
        "advanced peripherals",
        "advancedperipherals",
        "more red",
        "morered",
    ),
    "super_factory_manager": (
        "super factory manager",
        "sfm:",
    ),
    "rftools": (
        "rftools",
        "rftoolsbase",
        "rftoolsbuilder",
        "rftoolspower",
        "rftoolsstorage",
        "rftoolsutility",
    ),
    "xycraft": (
        "xycraft",
        "xycraft_core",
        "xycraft_machines",
        "xycraft_world",
        "xycraft_override",
        "xychorium",
    ),
    "laser_io_mffs": (
        "laserio",
        "laser io",
        "mffs",
        "modular force field system",
        "modular force fields",
    ),
    "pylons": (
        "pylons:",
        "expulsion pylon",
        "harvester pylon",
        "infusion pylon",
        "interdiction pylon",
        "protection pylon",
    ),
    "steves_carts": ("stevescarts", "steve's carts"),
    "draconic_evolution": (
        "draconic evolution",
        "draconicevolution",
        "draconic reactor",
        "chaos guardian",
        "draconium",
    ),
    "irons_spells": (
        "iron's spells",
        "irons_spellbooks",
        "iron's jewelry",
        "irons_jewelry",
        "irons_lib",
    ),
    "forbidden_arcanus": (
        "forbidden and arcanus",
        "forbidden_arcanus",
        "hephaestus forge",
        "eternal stella",
    ),
    "natures_aura": (
        "nature's aura",
        "naturesaura",
        "aura cache",
        "aura altar",
        "natural altar",
    ),
}

EXTRA_SCOPE = {
    "ars_nouveau": (
        {
            "label": "Ars Polymorphia",
            "jar_prefix": "ars_polymorphia-",
            "expected": True,
        },
    ),
    "immersive_engineering": (
        {
            "label": "Immersive Energistics",
            "jar_prefix": "Immersive-Energistics-",
            "expected": True,
        },
    ),
}

ALLOWED_ORIGINALS = {
    "Discord",
    "FALSE: %s",
    "FORGET %s",
    "TRUE: %s",
    "Super Factory Manager",
    "SFM",
    "XyCraft",
    "Pylons",
    "Steve's Carts",
    "Draconic Evolution",
    "Mekanism",
    "Mekanism: Generators",
    "Mekanism: Tools",
    "Powah",
    "Powah!",
    "Flux Networks",
    "Ars Nouveau",
    "Ars Additions",
    "Ars Controle",
    "Ars Creo",
    "Ars Elemancy",
    "Ars Elemental",
    "Ars Ocultas",
    "Ars Technica",
    "Ars Unification",
    "Not Enough Glyphs",
    "Starbuncle Mania",
    "StarbuncleMania",
    "Ars Énergistique",
    "EvilCraft",
    "The Twilight Forest",
    "L_Ender's Cataclysm",
    "The Undergarden",
    "The Aether",
    "The Bumblezone",
    "Eternal Starlight",
    "Deeper and Darker",
    "Refined Storage",
    "Refined Storage 2",
    "Extra Disks",
    "Extra Storage",
    "Refined Types",
    "Universal Grid",
    "Quartz Arsenal",
    "Cable Tiers",
    "Interdimensional Wireless Transmitter",
    "Refined Storage - Quartz Arsenal",
    "Functional Storage",
    "Pocket Storage",
    "EnderStorage",
    "Modular Routers",
    "FTB Filter System",
    "Hostile Neural Networks",
    "Thermal",
    "Iron Jetpacks",
    "Baubley Heart Canisters",
    "Tool Belt",
    "Simple Magnets",
    "Iron Furnaces",
    "Easy Villagers",
    "Mining Gadgets",
    "Building Gadgets",
    "Building Gadgets 2",
    "Mob Grinding Utils",
    "Item Collectors",
    "Botany Pots",
    "Botany Trees",
    "[§aBotany Pots§r] %s",
    "All The Ores",
    "AllTheOres",
    "All The Compressed",
    "AllTheCompressed",
    "Extreme Reactors",
    "Railcraft Reborn",
    "CC: Tweaked",
    "ComputerCraft",
    "Advanced Peripherals",
    "More Red",
    "Productive Metalworks",
    "Compact Machines",
    "Create",
    "Create 1.21",
    "Create: Dragons Plus",
    "Create Crafts & Additions",
    "Create: Enchantment Industry",
    "Create: Aquatic Ambitions",
    "Create: Hypertube",
    "Bells & Whistles",
    "Modern Industrialization",
    "Extended Industrialization",
    "Industrialization Overdrive",
    "Immersive Engineering",
    "PneumaticCraft: Repressurized",
    "PneumaticCraft",
    "&4&lPneumaticCraft",
    "Industrial Foregoing",
    "Industrial Foregoing Souls",
    "Industrial Foregoing &#27AEB9Souls",
    "Industrial Foregoing: Souls",
    "Soulplied Energistics",
    "Just Dire Things",
    "Actually Additions",
    "Oritech",
    "&lIndustrial Foregoing",
    "&bIndustrial Foregoing &#27AEB9Souls",
    "XOR",
    "Xor",
    "ME Wire",
    "Vajra",
    "Alt",
    "[CurseForge]",
    "%s / %s %sEU",
    "LE MOX 막대",
    "HE MOX 막대",
    "killtps",
    "tickTime",
    "Ctrl",
    "&6&lCreate&r 1.21",
    "&6&lCreate&r",
    "&6&lCreate",
    "Shift",
    "enderstorage <freq>|(<colour> <colour> <colour>) [owner]",
    "Pipez",
    "Modern Dynamics",
    "XNet",
    "Pedro Ricardo",
    "TohokuAlpha",
    "KuLou_D",
    "KrLite - Whisper of The Stars",
    "KrLite - Dusk o' Ereyesterday",
    "TohokuAlpha - Tranquility",
    "Binke - Nest",
    "KrLite - Posterity",
    "KrLite - The Thorny Reign",
    "Binke - Profundity",
    "Depus - Wailing Well",
    "Strantran - Stars Shining upon the Sea",
    "Depus - Optimized Option",
    "Depus - Mechanical Fossil",
    "Depus - Fake Light",
    "TohokuAlpha - Tranquility II",
    "TohokuAlpha - Atlantis",
    "Binke - Sacred Desert",
    "Binke - Spirit",
    "TohokuAlpha - Ether Rain",
    "Binke - Brisk",
    "Binke - Moonlight",
    "Stratus",
    "Noisestorm - Aether Tune",
    "Emile van Krieken - Ascending Dawn",
    "RENREN - chinchilla",
    "RENREN - high",
    "sunsette - klepto",
    "sunsette - Slider's Wrath",
    "Screem - Gloomper Anthem",
    "Screem - Limax Maximus",
    "Screem - Mammoth",
    "Screem - Relict",
    "Rimsky Korsakov - Flight of the Bumblebee",
    "Rat Faced Boy - Honey Bee",
    "Moserao - Rivers of Honey",
    "LudoCrypt - La Bee-da Loca",
    "LudoCrypt - Bee-laxing with the Hom-bees",
    "LudoCrypt - Bee-ware of the Temple",
    "RenRen - Knowing",
    "RenRen - Radiance",
    "RenRen - Life",
    "Punpudle - A Last First Last",
    "Punpudle - Drowning in Despair",
    "Punpudle - Beenna Box",
    "The Bumblezone!",
    "A Last First Last",
    "Drowning in Despair",
    "Radiance",
    "Knowing",
    "Bee-laxing with the Hom-bees",
    "Honey Bee",
    "Life",
    "Flight of the Bumblebee",
    "Bee-ware of the Temple",
    "La Bee-da Loca",
    "Baubles",
    "Blood Magic",
    "Equivalent Exchange 3",
    "Forestry",
    "Ender IO",
    "Industrial Craft 2",
    "Just Enough Items",
    "Immersive Engineering",
    "Thermal Expansion",
    "Thaumcraft",
    "Tinkers' Construct",
    "Jade",
    "MrCompost - Findings",
    "MrCompost - Home",
    "MrCompost - Maker",
    "MrCompost - Motion",
    "Rotch Gwylt - Radiance",
    "Rotch Gwylt - Steps",
    "Rotch Gwylt - Superstitious",
    "Rotch Gwylt - Maledictus",
    "Rotch Gwylt - Scylla",
    "Yuri_O - Spawn Of Hell",
    "Yuri_O - Defender of the Outer Realm",
    "Yuri_O - Light My Fire",
    "Yuri_O - Self-Destruction Sequence",
    "Yuri_O - Predator of the Abyss",
    "Yuri_O - The Dryest Beast",
    "Yuri_O - The Cataclysmfarer",
    "MrCompost - Thread",
    "MrCompost - Wayfarer",
    "HexaBlu",
    "Androsa",
    "TripleHeadedSheep",
    "/%s <info | reactivate | conquer | center>",
    "Thistle - The Sound of Glass",
    "AllRightsReserved",
    "Ctrl+C, Ctrl+V",
    "LostMyself",
    "TedXenon",
    "Applied Mekanistics",
    "Mekanism CC2C",
    "Mekanism C2C",
    "Mekanism IC2I",
    "Mekanism I2C",
    "Mekanism PRC",
    "SPS",
    "Gravitational Modulating Additional Unit",
    "Mekanism - Gravitational Modulating Additional Unit",
}
ALLOWED_ORIGINALS.update({f"Kivi {level}x" for level in range(1, 10)})

ALLOWED_NAME_COLLISIONS = {
    frozenset({"Energised Steel", "Energized Steel"}),
    frozenset({"Amethyst Golem", "The Amethyst Golem"}),
    frozenset({"Drygmy", "The Drygmy"}),
    frozenset({"Starbuncle", "The Starbuncle"}),
    frozenset({"Whirlisprig", "The Whirlisprig"}),
    frozenset({"Wixie", "The Wixie"}),
    frozenset({"Liveroot", "Liveroots"}),
    frozenset({"Naga Scale", "Naga Scales"}),
    frozenset({"Has: %s %s Candle", "Has: %s %s Candles"}),
    frozenset({"R-Click", "When R-Clicked"}),
    frozenset({"When Used on Blocks", "When used on Blocks"}),
    frozenset({"Copper Backtank", "Copper Backtank Placeable"}),
    frozenset({"Netherite Backtank", "Netherite Backtank Placeable"}),
    frozenset(
        {
            "Will create a wire link between them and return an _Empty Spool_.",
            "Will create a wire link between them, while retaining the _Empty Spool_.",
        }
    ),
    frozenset({"ELECTRUM_AMULET", "Pale Gold Amulet"}),
    frozenset({"BRASS_FIGURINE", "Brass Figurine"}),
    frozenset({"COPPER_GOBLET", "Copper Goblet"}),
    frozenset({"GOLD_GOBLET", "Ornate Goblet"}),
    frozenset({"Bucket of Seed Oil", "SEED_OIL_BUCKET"}),
    frozenset({"BIOETHANOL_BUCKET", "Bucket of Biofuel"}),
    frozenset({"BIOMASS_PELLET", "Biomass Pellet"}),
    frozenset({"CREATIVE_GENERATOR", "Creative Generator"}),
    frozenset(
        {
            "Provides _⚡_ to _wires_ connected to the _connector_ marked with a upwards arrow.",
            "Provides _⚡_ to _wires_ connected to the _connector_ marked with an upwards arrow.",
        }
    ),
    frozenset({"REDSTONE_RELAY", "Redstone Relay"}),
    frozenset({"DIGITAL_ADAPTER", "Digital Adapter"}),
    frozenset({"BARBED_WIRE", "Barbed Wire"}),
    frozenset({"ACCUMULATOR", "Accumulator"}),
}

MEKANISM_QUEST_WORDS = {
    "Ultimate": "궁극",
    "Tier": "단계",
    "Steam": "증기",
    "Reactors": "반응기",
    "Reactor": "반응기",
    "Modpack": "모드팩",
    "Modded": "모드가 추가된",
    "Mod": "모드",
    "Slurry": "슬러리",
    "Ore": "광석",
    "Metallurgic": "금속공학",
    "Infuser": "주입기",
    "Atomic": "원자",
    "Fusion": "핵융합",
    "Redstone": "레드스톤",
    "Basic": "기본",
    "Quantum": "양자",
    "Creative": "크리에이티브",
    "Bins": "단일 아이템 창고",
    "Bin": "단일 아이템 창고",
    "Configurator": "설정 장치",
    "Portal": "포털",
    "Itemstack": "아이템 스택",
    "Item": "아이템",
    "Robit": "로빗",
    "Multiblock": "멀티블록",
    "Mutliblock": "멀티블록",
    "Dissambler": "분해기",
    "Paxel": "팍셀",
    "Induction": "유도",
    "Cell": "셀",
    "Hohlraum": "홀로륨",
    "Casing": "케이싱",
    "Heat": "열",
    "Shears": "가위",
    "Drive": "드라이브",
    "Type": "유형",
    "Bodyarmor": "흉갑",
    "Teleport": "순간이동",
    "Home": "귀환",
    "Chargepad": "충전 패드",
    "Rename": "이름 변경",
    "Mob": "몹",
    "Appearance": "외형",
    "Crafting": "제작",
    "Windows": "창",
    "Craft": "제작",
    "Pants": "바지",
    "Neutral": "중립",
    "Glowing": "발광",
    "Sword": "검",
    "Unit": "유닛",
    "Side": "측면",
    "Configs": "설정",
    "Machine": "기계",
    "Empty": "빈",
    "Bar": "막대",
    "Set": "설정",
    "Network": "네트워크",
    "Name": "이름",
    "Entangloporters": "양자 전송기",
    "Entangloporter": "양자 전송기",
    "Glass": "유리",
    "Part": "부품",
    "DUMP": "버리기",
    "Bedrock": "기반암",
    "X-Ray": "투시",
    "ETC": "기타",
    "Paxels": "팍셀",
    "Armor": "방어구",
    "Offhand": "보조 손",
    "Walls": "벽",
    "Idle": "대기",
    "Damage": "피해",
    "Chemical": "화학 물질",
    "Netherite": "네더라이트",
    "Types": "유형",
    "Tag": "태그",
    "Activate": "가동",
    "Time-Dilating": "시간 확장",
    "Flight": "비행",
    "Wind": "풍력",
}

MEKANISM_QUEST_TEXT_REPLACEMENTS = {
    "quest.06210B6FD0F9989B.quest_desc": (
        ("궁극티어", "궁극 등급"),
        ("각 &d&l궁극 단계&r", "각 &d&l궁극 등급&r 장비"),
        ("20mb", "20mB"),
        ("2 &d원자합금&r", "&d원자 합금&r 2개"),
        ("1 &b엘리트 제어회로&r", "&b엘리트 제어 회로&r 1개"),
        ("&d궁극의 제어회로&r", "&d궁극 제어 회로&r"),
        ("2개과", "2개와"),
    ),
    "quest.0650996C7818ADB5.quest_desc": (
        ("2 모드", "2가지 방식"),
        ("패시브", "수동"),
        ("라바 소스 블록", "용암 근원 블록"),
        ("활성:", "능동 발전:"),
        ("이제 320FE/t가 생성됩니다.", "이 방식은 320FE/t를 생산합니다."),
    ),
    "quest.07084582F9562740.quest_desc": (
        ("컬러링", "염색"),
        ("3 &5기계&r", "3종의 &5기계&r"),
        ("2 안료", "안료 2개"),
        ("&c화학탱크&r", "&c화학 물질 탱크&r"),
        ("&b&l염색 기계&r", "&b&l염색기&r"),
        (
            "해당 안료를 가져와 &cD&ey&ae&bd&r, &cD&ey&be&r일 수 있는 "
            "블록 및 아이템에 적용합니다.",
            "안료를 사용해 &cD&ey&ae&bd&r 가능한 블록과 아이템을 &cD&ey&be&r합니다.",
        ),
    ),
    "quest.08DDE018A804BFE7.quest_desc": (
        ("&d&l강화실&r", "&d&l농축기&r"),
        ("&d강화된 아이템&r", "&d농축된 아이템&r"),
        ("&d강화아이템&r", "&d농축 아이템&r"),
        ("&d강화&r", "&d농축&r"),
        ("1 광석에서 2 먼지", "광석 1개에서 가루 2개"),
        ("한 번에 &d강화&f 더 많은", "한 번에 &d농축&f할 더 많은"),
        ("이 버튼을 누르면!", "버튼 하나로"),
        ("더 효율적이도록", "더 효율적으로 작동하도록"),
        ("이를 통과하는 &d&e아이템&r을 강화합니다", "투입된 &d&e아이템&r을 농축합니다"),
        ("&4레드 슬롯&r", "&4빨간색 슬롯&r"),
        ("&9블루 슬롯&r", "&9파란색 슬롯&r"),
        ("1 광석에서 2 가루", "광석 1개에서 가루 2개"),
        (
            "한 번에 &d농축&f할 더 많은 &e아이템&r을 위한 더 많은 슬롯",
            "더 많은 슬롯으로 한 번에 더 많은 &e아이템&r을 &d농축&f",
        ),
    ),
    "quest.0E175356D43E6A10.quest_desc": (
        (
            "&3염화수소&r를 &c&l화학 물질로 파이프로 연결 주입실&r에서 &c로 "
            "&7광석&r을 주입하여 &7조각&r을 얻습니다.",
            "&3염화수소&r를 &c&l화학 주입실&r로 보내 &7광석&r에 &c주입하면 "
            "&7광석 조각&r을 얻습니다.",
        ),
        ("단계 1처럼", "1단계와 마찬가지로"),
        ("4 &7광석 파편&r", "&7광석 조각&r 4개"),
        ("3 &7원석 광석&f은 8 &7광석 파편&r", "&7원석&f 3개에서는 &7광석 조각&r 8개"),
        ("4개을", "4개를"),
        ("8개을", "8개를"),
    ),
    "quest.0F326EEEC2EBE4E5.quest_desc": (
        ("&d&l강화실&r", "&d&l농축기&r"),
        ("&d강화&r 변형", "&d농축 물질&r"),
        ("&d강화된 아이템&r", "&d농축 물질&r"),
        ("8x만큼의 MB", "일반 재료의 8배에 해당하는 mB"),
        ("&d풍부한 &0석탄&r", "&d농축 &0탄소&r"),
        ("&d강화된 &4레드스톤&r", "&d농축 &4레드스톤&r"),
        ("&d풍부한 &5정제된 오비시디언&r", "&d농축 &5정제된 흑요석&r"),
        ("&d궁극의&r", "&d궁극 등급&r"),
    ),
    "quest.27512B0434531195.quest_desc": (
        (
            "1 &e아이템&r 플러스일 뿐입니다. 1 &c화학&r으로 1 새로운",
            "&e아이템&r 1개와 &c화학 물질&r 1개로 1개의 새로운",
        ),
        ("죽은 산호초", "죽은 산호"),
        ("&9&l전해분리기&r", "&9&l전해 분리기&r"),
        ("광석 파편", "광석 조각"),
        (
            "&e아이템&r 1개와 &c화학 물질&r 1개로 1개의 새로운 "
            "&e아이템&r을 만들어보세요",
            "&e아이템&r 1개와 &c화학 물질&r 1개로 새로운 &e아이템&r 1개를 만듭니다",
        ),
        ("&c&l로터리 &b응축기&r", "&c&l회전 &b콘덴서&r"),
    ),
    "quest.47F38E606AD3FF53.quest_desc": (
        ("우리는 &4분쇄&r &7주괴&f를", "&7주괴&f를 &4분쇄&r해"),
        ("&7먼지&r", "&7가루&r"),
        ("&d풍부하게&r &7광석 블록&r을 얻어", "&7광석 블록&r을 &d농축&r해"),
    ),
    "quest.566C1DBA9829E328.quest_desc": (
        ("&e&l컴바이너&r", "&e&l결합기&r"),
        ("간단한 2 &e아이템&r", "&e아이템&r 2개를 사용하는 간단한"),
        ("2 다른 염료", "서로 다른 염료 2개"),
        ("포장된 진흙", "단단한 진흙"),
        ("&7자갈&f 및 &0플린트&r", "&7조약돌&f과 &0부싯돌&r"),
        ("4 &5흑요석 가루 &f 및 &8딥슬레이트&f", "&5흑요석 가루 &f4개와 &8심층암&f"),
    ),
    "quest.5B556192F060F3F1.quest_desc": (
        ("&4&l크러셔&r", "&4&l분쇄기&r"),
        ("&3&5흑요석&f을 분쇄", "&5흑요석&f을 &3분쇄"),
        ("&b화학 다이아몬드&r", "&b다이아몬드&r"),
        ("&b강화 다이아몬드&r", "&b농축 다이아몬드&r"),
        ("몇 가지 선택권을 얻었습니다.", "몇 가지 방법으로 활용할 수 있습니다."),
        ("&d풍부하게&r", "&d농축&r해"),
        ("&5화학적으로 정제된 흑요석&r", "&5주입용 정제된 흑요석&r"),
    ),
    "quest.67E7A9A65B14C933.quest_desc": (
        ("&4각 &7덩어리&f를 &f부서서", "각 &7덩어리&f를 &4분쇄&f해"),
        ("&7더러운 광석 가루&r", "&7오염된 광석 가루&r"),
        (
            "우리는 &6제련할 수 없습니다. &7더러운 먼지&r,",
            "&7오염된 가루&r는 바로 &6제련할 수 없습니다.",
        ),
        ("&d풍부&r해야", "&d농축&r해야"),
        ("&6&f제련하여 &7먼지&f를 제련하여", "&7가루&f를 &6제련&f해"),
    ),
    "quest.7AE502EDB73BD57A.quest_desc": (
        ("&4&l크러셔&r", "&4&l분쇄기&r"),
        ("&4크러셔&r", "&4분쇄기&r"),
        ("먼지", "가루"),
        ("이것이 꼭 필요할 것입니다.", "꼭 마련해 두세요."),
        (
            "특히 &8업그레이드&r를 만들기 위해!",
            "특히 &8업그레이드&r 제작에 많이 필요합니다!",
        ),
    ),
    "quest.13A5748DF69D832E.quest_desc": (
        (
            "자체적으로 많은 작업을 수행하지 않으며 대신",
            "단독으로는 아이템을 이용할 수 없으므로",
        ),
        ("동일한 네트워크로", "QIO 드라이브 어레이와 같은 네트워크로"),
        ("입금하고 액세스할", "넣고 꺼낼"),
        ("2 행부터 7까지", "2행부터 7행까지"),
        (
            "스택의 최소부터 최대 &e아이템&r까지",
            "스택의 &e아이템&r 수량이 적은 순서나 많은 순서",
        ),
        ("3 제작 창가 나옵니다", "최대 3개의 제작 창이 열립니다"),
        ("이동 효과를 줍니다", "어디로 이동할지 정합니다"),
        ("레시피", "조합법"),
        ("조합법를", "조합법을"),
    ),
    "quest.4869D9DBDD1A15CD.quest_desc": (
        ("16진수", "헥스"),
        (
            "&cC&6o&el&ao&br &cM&6o&ed&au&bl&ca&6t&ei&ao&bn &7유닛&r을 "
            "사용하면 &cC&6o&el&ao&br&r의 &a&l메카슈트 부품&r에 있습니다.",
            "&cC&6o&el&ao&br &cM&6o&ed&au&bl&ca&6t&ei&ao&bn &7유닛&r은 "
            "설치된 &a&l메카슈트 부품&r의 &cC&6o&el&ao&br&r을 바꿀 수 있게 해 줍니다.",
        ),
        ("해당 구성에 액세스하려면", "설정을 열려면"),
        ("사용 가능한", "선택할 수 있는"),
        ("몇 개나 있는지 모르겠습니다", "수만큼 다양합니다"),
        ("자체 &7유닛&r", "각각의 &7유닛&r"),
    ),
    "quest.4BAF44FCA0894DE8.quest_desc": (
        ("2 레시피", "2가지 조합법"),
        ("그 중 1은", "그중 1가지는"),
        ("태양전지", "태양 전지"),
        ("&8핵 폐기물&r", "&8핵폐기물&r"),
        ("&8핵폐기물&r의 모든 5mB", "&8핵폐기물&r 5mB"),
    ),
    "quest.5194A067BEA98E79.quest_desc": (
        ("이봐, 난 당신을 기억해요!", "다시 만났네요!"),
        ("알고 보니 2 레시피에는", "알고 보니"),
        ("사용되었습니다.", "에는 2가지 조합법이 있습니다."),
        ("&8핵 폐기물&r의 각 5mB에 대해", "&8핵폐기물&r 5mB마다"),
        ("1,000mB 가치의", "1,000mB에 해당하는"),
        (
            "필요하며, &2핵분열성 연료&r.",
            "필요하고 &2핵분열성 연료&r도 같은 양이 필요합니다.",
        ),
        (
            "알고 보니 2 조합법에는 &5&l동위원소 원심분리기&r가 에는 2가지 "
            "조합법이 있습니다.",
            "알고 보니 &5&l동위원소 원심분리기&r에는 2가지 조합법이 있습니다.",
        ),
    ),
    "quest.53E929BF89209CFC.quest_desc": (
        ("&e수입업자", "&eQIO 가져오기 장치"),
        ("&e수출업자", "&eQIO 내보내기 장치"),
        ("재고가 있는 블록", "인벤토리가 있는 블록"),
        ("자동으로 가져오거나 가져옵니다", "자동으로 가져오거나 내보냅니다"),
        ("&e아이템&r이 있는 모드", "&e아이템&r이 속한 모드"),
        (
            "모든 &2&l바닐라&r 블록에 대한 &2&l마인크래프트&r와 같습니다",
            "&2&lMinecraft&r 아이템을 넣어 모든 &2&l바닐라&r 블록을 지정하는 식입니다",
        ),
    ),
    "quest.56DB53F255100136.quest_desc": (
        ("메카슈트팬츠", "메카슈트 각반"),
        ("메카슈트 팬츠", "메카슈트 각반"),
        ("네더라이트 레깅스", "네더라이트 각반"),
        ("4 업그레이드", "4단계나 높은 장비"),
        ("응... 그건... 그렇구나!", "네, 충분히 가치가 있습니다!"),
        (
            "그럼 마법 피해를 제외한 모든 피해..",
            "마법 피해를 제외한 모든 피해에 적용됩니다.",
        ),
        ("대부분의 이동을 업그레이드하는", "주로 이동 능력을 강화하는"),
    ),
    "quest.6A1174845810C7A1.quest_desc": (
        ("방어구 및 보조 손를", "방어구와 보조 손을"),
        ("스크린과 2 추가 슬롯", "화면과 추가 슬롯 2개"),
        ("2 추가 슬롯", "추가 슬롯 2개"),
        ("방어구 또는 도구가 가는 곳", "방어구 또는 도구를 넣는 곳"),
        ("&7모듈 장치&r", "&7모듈 유닛&r"),
        ("해당 구성을 가져올", "모듈 설정을 열"),
        ("2개은", "2개는"),
        ("유닛&r가", "유닛&r이"),
    ),
    "quest.6C1F7A0B330B3F42.quest_desc": (
        (
            "&a&l메카슈트 &f&m체스트플레이트&r &a&l흉갑&r",
            "&a&l메카슈트 &f&m흉갑&r &a&l흉갑&r",
        ),
        (
            "&5Unobtainium &f&m흉갑&r로 업그레이드됩니다. &5가슴판&r",
            "&5언옵테이니움 &f&m흉갑&r &5흉갑&r의 상위 장비입니다",
        ),
        ("&d반물질 펠릿&r", "&d반물질 펠릿&r"),
        ("에너지가 없는", "충전되지 않은"),
        ("&a에너지&r는 어떻습니까?", "&a에너지&r가 있다면"),
        ("사용하게 될 수도 있습니다", "사용합니다"),
        ("던질 수 있습니다", "넣을 수 있습니다"),
    ),
    "quest.6D7D0A5313284B53.quest_desc": (
        ("Fall 피해", "낙하 피해"),
        ("안녕, 멋진 킥스!", "멋진 부츠네요!"),
        ("언옵테이니엄", "언옵테이니움"),
        ("언옵테이늄", "언옵테이니움"),
        ("부츠의 통계", "부츠의 능력치"),
        (
            "누가 발을 때리나요! 아 맞다 낙하 피해를 깜빡했네요.",
            "발을 공격받을 일은 드물지만, 낙하 피해는 중요하죠!",
        ),
        ("같은 양을 보호하지만", "비슷한 방어력을 제공하지만"),
        ("당신을 보호합니다", "피해를 막습니다"),
        ("&a&l부츠&r. 이러한", "&a&l부츠&r도 포함됩니다. 이러한"),
        ("인챈트", "마법 부여"),
    ),
    "quest.7177653B736AB10E.quest_desc": (
        ("&c포팅&r", "&c포트로 전송&r"),
        ("&c포트 &5D-T 연료&r", "&c포트로 &5D-T 연료&r"),
        ("&c포트&r 속도", "&c포트&r로 넣는 속도"),
        ("&e홀라움&r", "&e홀로륨&r"),
        ("&9&f4 &e금가루&r", "&9&f4개의 &e금 가루&r"),
        ("10mb", "10mB"),
        ("제작하세요. &e홀로륨&r.", "&e홀로륨&r으로 제작하세요."),
        ("아 잠깐만 비어 있으면", "완성된 홀로륨은 비어 있으므로"),
        (
            "&c화학 물질&r을 모두 &c&l융합 반응기&r에 &c포트로 전송&r하고",
            "두 &c화학 물질&r을 모두 &c&l핵융합로&r의 &c포트&r로 넣고",
        ),
        (
            "&c포트로 &5D-T 연료&r만 사용하면 &c포트&r로 넣는 속도로 주입됩니다",
            "&c포트로 &5D-T 연료&r를 넣으면 투입한 &c포트&r 속도대로 주입됩니다",
        ),
        ("&c포트로 전송&r &c중수소&r", "&c포트&r로 &c중수소&r"),
        (
            "&e홀로륨&r 내에서 약간의 &5D-T 연료&r가 필요하고",
            "&e홀로륨&r에 약간의 &5D-T 연료&r를 채우고",
        ),
        ("에 던져서 채우세요", "에 넣어 채우세요"),
    ),
    "quest.7846B7FFC3DD85C5.quest_desc": (
        ("각각에 대해 &d포트&r", "각 용도에 맞는 &d포트&r"),
        ("2 &d포트&r", "&d포트&r 2개"),
        ("1 &d포트&r", "&d포트&r 1개"),
        (
            "&d&lSPS&r &a폴로늄&r을 제공하기 위한 것이고 마지막은 &d반물질&r이 나왔습니다",
            "&d&lSPS&r에 &a폴로늄&r을 넣고, 마지막 포트로 &d반물질&r을 꺼냅니다",
        ),
    ),
    "quest.7864C8F2CBC910CB.quest_desc": (
        ("메카슈트헬멧", "메카슈트 투구"),
        ("메카슈트 헬멧", "메카슈트 투구"),
        ("Unobtainium 헬멧", "언옵테이니움 투구"),
        ("네더라이트 헬멧", "네더라이트 투구"),
        ("방어점", "방어력"),
        ("여기에 재미있는 부분이 있습니다", "충전하면 진가가 드러납니다"),
        ("업그레이드할 수 있습니다.,", "업그레이드할 수 있습니다."),
        (
            "더 적은 피해를 받으려면 &a에너지&r를 더 많이 사용하세요",
            "&a에너지&r 용량을 늘려 더 많은 피해를 막을 수 있습니다",
        ),
    ),
    "quest.795B80BF12D23897.quest_desc": (
        ("프로스트 워커", "차가운 걸음"),
        ("Frost Walker", "차가운 걸음"),
        ("&a&l메카슈트 부츠&r 위를 걸을 때", "&a&l메카슈트 부츠&r를 신고 걸을 때"),
        ("&9물&r이 &b얼음&r!", "&9물&r이 &b얼음&r으로 변합니다!"),
        ("곧 녹을 것입니다", "곧 녹습니다"),
        ("차가운 걸음가 많을수록", "차가운 걸음 단계가 높을수록"),
    ),
    "quest.7ECE00D12CFC50A4.quest_desc": (
        ("&b실크 터치", "&b섬세한 손길"),
        ("실크 터치 인챈트", "섬세한 손길 마법 부여"),
        ("삽과 기타 도구도 있습니다", "삽을 비롯한 다른 도구 기능에도 적용됩니다"),
        (
            "돌과 광석, 풀과 균사체를 선택할",
            "돌과 광석은 물론 잔디 블록과 균사체도 그대로 채취할",
        ),
    ),
    "quest.120572510F525930.quest_desc": (
        ("열증발 플랜트", "열 증발 플랜트"),
        ("&e소금물&r", "&e염수&r"),
        (
            "베이스는 4x4이고 &6열 증발 블록&r의 4x4뿐입니다",
            "바닥은 4x4 크기이며 &6열 증발 블록&r도 4x4로 배치합니다",
        ),
        ("최소한 3 블록, 최대 18", "최소 3블록, 최대 18블록"),
        ("GUI에 액세스하는 방법입니다", "GUI를 여는 블록입니다"),
        (
            "거기에서 우리는 &6열&r을 볼 수 있습니다",
            "GUI에서 내부의 &6열&r을 확인할 수 있습니다",
        ),
        ("1 &6컨트롤러&r", "&6컨트롤러&r 1개"),
        ("&e 염수&f", "&e염수&f"),
        ("&b파이프 &f 및 &6도체&r", "&b파이프&f와 &6전도체&r"),
        ("상단 레이어", "맨 위층"),
    ),
    "quest.162CE44400A63575.quest_desc": (
        ("첫 번째이자 가장 중요한", "가장 먼저 알아볼"),
        ("&c화학 물질&f또는", "&c화학 물질&f 또는"),
        ("&e노란색 사각형&r", "&e노란색 슬롯&r"),
        ("&4붉은 광장&r", "&4빨간색 슬롯&r"),
        ("&9다크블루스퀘어&r", "&9진한 파란색 슬롯&r"),
        ("제품이 도착하게 됩니다", "완성품이 나옵니다"),
        ("&a연두색 슬롯&r", "&a초록색 슬롯&r"),
    ),
    "quest.166971866A9234C7.quest_desc": (
        ("3 가장 중요한 주입 아이템 중 하나", "가장 중요한 주입 재료 3가지 중 하나"),
        ("그것을 만들기 위해서는", "이를 만들려면"),
        ("레드스톤 아이템", "레드스톤 재료"),
        ("아이템&r마다 제공되는 양", "재료&r마다 주입되는 양"),
    ),
    "quest.1AEFF93A398B8BBF.quest_desc": (
        ("&c&l어드밴스드&r", "&c&l고급 등급&r"),
        (
            "동일한 버프가 있습니다... 그 이상입니다",
            "같은 장점을 더 높은 성능으로 제공합니다",
        ),
        ("20mb", "20mB"),
        ("그것이 바로", "필요한 양은"),
        ("2 &b다이아몬드 가루&r", "&b다이아몬드 가루&r 2개"),
        ("&b강화 합금&r(그 중 2)", "&b강화 합금&r 2개"),
    ),
    "quest.75E4751F7A802A44.quest_desc": (
        (
            "우리는 월터 화이트(Walter White)란 무엇인가?",
            "월터 화이트(Walter White)라도 된 기분이네요!",
        ),
        ("가장 중요한 &a황산&r은 &e황&r입니다", "&a황산&r의 출발점은 &e황&r입니다"),
        ("&9물&r을 공급하여 좀 더 확보해 보겠습니다", "&9물&r을 분해해 확보하세요"),
        ("새로 발견한 &b산소&r", "생성된 &b산소&r"),
        (
            "수증기가 나올 때까지 잠시 동안 &e황&r을 남겨두세요",
            "이제 &e황&r 이야기는 잠시 미뤄 두고 수증기를 준비하세요",
        ),
        ("&c&l회전형 &b응축기&r", "&c&l회전 &b콘덴서&r"),
    ),
    "quest.77FB313845779AED.quest_desc": (
        (
            "&a산&r이 포함된 &7광석 &f 아래로 &3용해&r합니다",
            "&7광석&f을 &a산&r으로 &3용해&r합니다",
        ),
        ("&7광석&r의 &c화학&r 형태", "&7광석&r이 &c화학 물질&r로 녹은 형태"),
        ("3 &7원석&r은 2 양동이", "&7원석&r 3개는 2양동이"),
        ("1 &7광석 블록&r은 1 양동이", "&7광석 블록&r 1개는 1양동이"),
        ("청소해야합니다", "정제해야 합니다"),
        ("모든 5mB", "5mB마다"),
        ("3mB로", "3mB로"),
        (
            "예, &7조각&f및 &7덩어리&r와는 다릅니다",
            "앞에서 만든 &7조각&f이나 &7덩어리&r와는 다른 물질입니다",
        ),
        ("각 200mB는 1 &7결정&r과 같습니다", "200mB마다 &7결정&r 1개가 만들어집니다"),
    ),
    "quest.7934873E784C4B3C.quest_desc": (
        ("&9&l분리기&r", "&9&l전해 분리기&r"),
        ("&b&l정수기&r", "&b&l정화기&r"),
        ("당신의 &7조각 &f을", "&7조각&f을"),
        ("지금, &c그 &7덩어리&f를 부수고&r", "이제 &c&7덩어리&f를 분쇄해&r"),
        ("&7더러운 가루&r", "&7오염된 가루&r"),
        ("&d&f&7오염된 더스트&f를 풍부하게 하여", "&d&f&7오염된 가루&f를 농축해"),
        ("&7광석 더스트&r", "&7광석 가루&r"),
        ("아름답게 &l가공된 광석&r", "완성된 &l주괴&r"),
    ),
    "quest.6DC1E08D019FD543.quest_desc": (
        (
            "&c&l화학 주입기&r를 사용하면 &c&f&7결정&f에 &3염화수소&r를 "
            "주입하여 2 &7광석을 얻을 수 있습니다. 각 &7광석 수정&r에서 나온 "
            "파편&r입니다",
            "&c&l화학 주입실&r에서 &7광석 결정&f에 &3염화수소&r를 "
            "&c주입&f하면 &7광석 결정&r 하나마다 &7광석 조각&r 2개를 얻습니다",
        ),
    ),
    "quest.0306D25C7407FE88.quest_desc": (
        ("1년", "오랫동안"),
        ("&c포팅&6열&r", "&c포트로 &6열&r을 전달하는 방식"),
        ("&c포팅&6열", "&c포트로 &6열을 전달하는 방식"),
        ("오랫동안을 기다리는 대신", "오랫동안 기다리는 대신"),
        (
            "여러 &4레이저 증폭기&r로 촬영하는 여러 &4레이저&r",
            "여러 &4레이저 증폭기&r에 여러 &4레이저&r를 연결하는 방법",
        ),
        ("모두 4 &4레이저&r가", "각각 &4레이저&r 4개가"),
    ),
    "quest.02C6132919DEAF2A.quest_desc": (
        ("증기을", "증기를"),
        ("그 레이어", "그 층"),
        (
            "서로 함께 움직이는 것은 자기력을 통해 &a에너지&r를 발전시키는 것입니다",
            "회전 운동이 자기장을 통과하면서 &a에너지&r를 생산합니다",
        ),
    ),
    "quest.369DADE3B3D8416F.quest_desc": (
        ("2 그중 하나입니다. 1는", "2개가 필요합니다. 1개는"),
        ("다른 하나는", "나머지는"),
        (
            "&6액체 리튬&r, &c화학 물질 &6리튬&r",
            "&6액체 리튬&r이 아니라 &c화학 물질인 &6리튬&r",
        ),
        ("&c&l로터리&b응축기&r", "&c&l회전 &b콘덴서&r"),
        ("더 단단하지만", "얻기 어렵지만"),
    ),
    "quest.4E18E28BDF6B7983.quest_desc": (
        (
            "사용하기 위해 &c&l핵융합로&r 내의 반응기 유리를 대체합니다",
            "사용하려면 &c&l핵융합로&r의 반응기 유리를 포트로 교체합니다",
        ),
        (
            "연료의 경우 &c중수소&r 및 &a삼중수소&r(또는 그냥 &5D-T "
            "연료&r)의 경우 2(또는 1)입니다",
            "연료에는 &c중수소&r와 &a삼중수소&r용 포트 2개(또는 &5D-T "
            "연료&r용 포트 1개)가 필요합니다",
        ),
        (
            "&a에너지&r를 출력하려면 1도 필요합니다",
            "&a에너지&r 출력용 포트도 1개 필요합니다",
        ),
        ("2 더 많은 &c포트&r", "&c포트&r 2개가 더"),
        (
            "1는 &9물을 입력하기 위한 &r과 증기를 출력하기 위한 1입니다",
            "1개는 &9물&r 입력용이고 나머지 1개는 증기 출력용입니다",
        ),
        ("&3구성기&r", "&3설정 장치&r"),
    ),
    "quest.60A1AEEDB0C44663.quest_desc": (
        ("레시피", "조합법"),
        ("시간 카운터 블록", "시간 계수기 블록"),
        ("일반적인 것이", "일반 기계가"),
        ("이것도 동일합니까?", "이 멀티블록도 그럴까요?"),
        ("네, 실행하려면", "네. 작동하려면"),
        ("3 광석 블록", "광석 블록 3개"),
        ("16를", "16개를"),
        ("그렇다면 멀티블록", "이것이 멀티블록의 장점입니다"),
    ),
    "quest.6B56F92E28C92A0F.quest_desc": (
        ("레시피", "조합법"),
        ("시간 카운터 블록", "시간 계수기 블록"),
        ("일반적인 것이", "일반 기계가"),
        ("이것도 동일합니까?", "이 멀티블록도 그럴까요?"),
        ("네, 실행하려면", "네. 작동하려면"),
    ),
    "quest.62B29AEF8468750E.quest_desc": (
        (
            "&6열원&r에서 &m피해&r &a에너지&r를 덜 받아 &a에너지&r를 "
            "만든다는 건가요? 가입하세요!",
            "&6열원&r에서 &m피해&r를 막는 데 쓸 &a에너지&r를 아끼면서 "
            "&a에너지&r도 얻는다고요? 정말 좋네요!",
        ),
        (
            "&6마그마&f 위를 걸을 때, &6불&f 또는 &6용암&r을 통과하면",
            "&6마그마&f를 밟거나 &6불&f 또는 &6용암&r 속에 있으면",
        ),
    ),
    "quest.6CCE920735187234.quest_desc": (
        ("그게 진짜 머니메이커다!", "내부 구조가 발전량을 결정하는 핵심입니다!"),
        ("가장 작은 것에는 2이 필요합니다", "최소 크기에는 2개가 필요합니다"),
        ("총 4 부착합니다", "총 4개를 부착합니다"),
        ("빌드보다", "건설보다"),
        ("일부 증기에 넣으면", "증기를 넣으면"),
        ("전체 &9&l터빈&r 빌드", "전체 &9&l터빈&r 구조물"),
        ("&9로터 &f 및 &9블레이드&r", "&9로터&f와 &9블레이드&r"),
        ("2번째 &9포트&r", "2번 &9포트&r"),
        ("증기을", "증기를"),
        ("대기이 있습니다", "대기 모드가 있습니다"),
        ("유휴 상태가 아닌 것을 사용하면", "대기 이외의 모드를 사용하면"),
    ),
    "quest.7E3C84D7FCEC9D52.quest_desc": (
        ("4 다양한 바", "4개의 막대"),
        ("2 버튼", "버튼 2개"),
        ("가동라고 말하면서", "가동이라고 표시되며"),
        ("&2&l리액터&r", "&2&l핵분열로&r"),
        ("&2&l원자로&r", "&2&l핵분열로&r"),
        ("붕괴!", "노심 용융!"),
        ("그것을 피하자!", "반드시 피해야 합니다!"),
        ("확인하십시오", "확인하세요"),
    ),
    "quest.20054D077AFE3F56.quest_desc": (
        (
            "나머지는 이미 가지고 있어야 하는 것입니다",
            "나머지 재료도 이미 갖추었을 거예요",
        ),
        ("A &2&lP.R.C.&r", "&2&lP.R.C.&r"),
        ("1,000mB&9물&r", "&9물&r 1,000mB"),
        ("1,000mB&3플루토늄&r", "&3플루토늄&r 1,000mB"),
        ("1&d형석 가루&r", "&d형석 가루&r 1개"),
        ("1를 만듭니다. &3플루토늄 펠릿&r 및", "&3플루토늄 펠릿&r 1개와"),
        ("만들 수 있습니다:", "만들 수 있습니다."),
        ("심지어는 광석 망치도 가능합니다", "광석 망치도 사용할 수 있습니다"),
    ),
    "quest.078B69E9362A5496.quest_desc": (
        ("&5&lMekanism&r이 그렇게 크네요", "&5&lMekanism&r은 정말 방대한 모드죠"),
        ("&2&l리액터&r와 무적 갑옷", "&2&l원자로&r와 강력한 방어구"),
        (
            "&b산소&r와 &e이산화황&r을 &c튜브&r로 &c&l화학 주입기&r로 만들어",
            "&b산소&r와 &e이산화황&r을 &c튜브&r로 &c&l화학 주입기&r에 넣어",
        ),
    ),
    "quest.106C4EB6002B8B41.quest_desc": (
        ("꼭 많이 필요합니다", "여러 대가 필요할 수 있습니다"),
        ("그냥 1 멀티블록", "멀티블록 1개"),
        (
            "걱정하지 마십시오. 출력은 쉽습니다. 단지 &c화학&r 출력입니다",
            "출력에는 &c화학 물질&r 출력 해치만 있으면 됩니다",
        ),
        ("더 빠르게 나눕니다", "훨씬 빠르게 분리합니다"),
    ),
    "quest.302E9BC711779A4A.quest_desc": (
        ("&e유황&r", "&e황&r"),
        (
            "&2방사성&r, 풍부하고 &6&lATO&r에서 사용되므로 모든 버전이 작동합니까?",
            "&2방사성&r이고 &6&lATO&r에도 쓰이는 광물이라면 무엇일까요?",
        ),
        (
            "&a우라늄 광석&r을 채굴하고 &d&l농축기&r에서 &a우라늄 주괴&r를 사용하여",
            "&a우라늄 광석&r을 채굴한 뒤 &d&l농축기&r에서 &a우라늄 주괴&r를 처리해",
        ),
        ("아니예요", "아니에요"),
        ("에 구워", "에서 산화시켜"),
    ),
    "quest.505799C894C771B2.quest_desc": (
        (
            "이러한 카드는 &8업그레이드&r 카드만 사용할 수 있습니다",
            "이런 기계는 &8업그레이드&r만 설치할 수 있습니다",
        ),
        ("50 &9&l전해 분리기&r", "&9&l전해 분리기&r 50대"),
        ("1 멀티블록", "멀티블록 1개"),
        (
            "이전 멀티블록이 필요합니다. &c&l자동 헤파이스토스 대장간&r.",
            "선행 멀티블록인 &c&l자동 헤파이스토스 대장간&r이 필요합니다.",
        ),
        ("다른 컨트롤러와 함께 동일한 구조", "제어기만 다르고 구조는 동일"),
        ("빌드 지침", "건설 방법"),
        ("호스팅하므로", "배치되므로"),
        (
            "내 말이 맞았다. 이보다 더 단순해질 수는 없다. 그것은 단지 똑같은 양의 단순함을 유지합니다",
            "말 그대로 이전 층과 똑같습니다",
        ),
        ("동일를 사용합니다", "동일합니다"),
        ("&c기계 케이싱&r을 배치되므로", "&c기계 케이싱&r이 배치되므로"),
        ("4 외부 &7룬 블록&r", "바깥쪽 &7룬 블록&r 4개"),
        ("&9암석", "&9다크스톤"),
        ("&6금박 조각으로 연마된 암흑석&r", "&6금박 조각된 윤이 나는 다크스톤&r"),
        ("그들을 둘러싸고 있습니다", "그 주위를 둘러쌉니다"),
    ),
    "quest.50F23B2688D7E699.quest_desc": (
        ("1,000mB의 &d반물질&r", "&d반물질&r 1,000mB"),
        ("1 &d반물질 펠릿&r", "&d반물질 펠릿&r 1개"),
        ("1,000,000mB &a폴로늄&r", "&a폴로늄&r 1,000,000mB"),
        ("1MmB &a폴로늄&r", "&a폴로늄&r 1MmB"),
        (
            "&a폴로늄&r에 대해 5,000,000mB &8핵폐기물&r과 "
            "&2핵분열성 연료&r가 필요하여 &8핵폐기물&r을 만들 수 있습니다",
            "이 &a폴로늄&r을 만들려면 &8핵폐기물&r 5,000,000mB와, 그 "
            "&8핵폐기물&r을 만들 &2핵분열성 연료&r가 필요합니다",
        ),
        (
            "오직 5MmB &2핵분열성 연료&r... 오직!",
            "&2핵분열성 연료&r가 고작 5MmB나 필요하죠!",
        ),
        ("하지만 마침내 우리는 그것을 얻었습니다", "마침내 완성했습니다"),
        ("메카슈트를 만들 수 있고", "메카슈트를 만들고"),
        ("1,000mB을", "1,000mB를"),
        ("1개을", "1개를"),
        ("1MmB이", "1MmB가"),
    ),
    "quest.0AEC181F5E21A299.quest_desc": (
        ("수박 파워", "수박 발전"),
        ("&9에틸렌&r을 주입하여", "&9에틸렌&r을 연료로 사용해"),
        ("만드십시오", "만드세요"),
        ("그런 다음 이것을", "그런 다음 바이오 연료를"),
        ("로 펌핑합니다", "에 넣으세요"),
        ("전력 생성을 시작하십시오", "발전을 시작하세요"),
    ),
    "quest.34D14B807A2DAC0F.quest_desc": (
        (
            "당신은 &5&lMekanism&r과 &l&7Modern Industrialization&r만 재미있을 "
            "거라고 생각하십니까?",
            "&5&lMekanism&r과 &l&7Modern Industrialization&r만 강력한 장비를 "
            "가질 수 있다고 생각하셨나요?",
        ),
        ("당신을 더욱 강력하게 만들어 줄", "플레이어를 더욱 강하게 만드는"),
        ("어디에 있든 자동으로 에너지를 빼내고", "어디서든 자동으로 에너지를 공급받고"),
    ),
    "quest.71C552678A0F649F.quest_desc": (
        ("심층암 주변에 스폰되며", "심층암 지대에 생성되며"),
        ("광물을 채굴하는 데 철만 필요하지만", "철 곡괭이로도 캘 수 있지만"),
        ("보다 더 좋은 능력치", "보다 높은 능력치"),
    ),
    "quest.476755275B948A5F.quest_desc": (
        ("&b증기&r와 같은 &b증기&r", "&b기체&r인 &b증기&r"),
        (
            "3x3x3 원자로를 만든 것과 같은 방식으로 제작되지만",
            "3x3x3 원자로와 같은 방식으로 만들되",
        ),
        ("모든 부품은 대신", "모든 부품을"),
        ("3x3x3보다 큰 것을 제안합니다", "3x3x3보다 크게 짓는 편이 좋습니다"),
        (
            "이는 물과 같은 유체를 반응기로 유입시킵니다. 이는 또한",
            "이 포트로 물 같은 유체를 원자로에 넣고,",
        ),
        (
            "생성하여 대신 유체 증기를 Mekanism 가스 증기로 변환",
            "사용하면 유체 형태의 증기를 Mekanism 화학 물질 형태로 변환",
        ),
    ),
    "quest.48DC9E8E9D21A2FA.quest_desc": (
        ("힘을 만드는", "전력을 생산하는"),
        ("태양의 힘", "태양광"),
        ("기본적인 힘의 필요", "기본적인 전력 수요"),
        ("바람을 통해 힘", "바람으로 전력"),
        ("하늘에 액세스할 수 있어야 합니다", "하늘이 트여 있어야 합니다"),
        ("하늘에 직접 액세스할 수 있어야 합니다", "하늘이 직접 보여야 합니다"),
    ),
    "quest.1796E08BBDC09B84.quest_desc": (
        ("1톤", "아주 많은 양"),
        (
            "밀거나 당기는 것에 따라 걸리거나 장소가 결정됩니다.",
            "유체나 화학 물질의 입출력 방향은 연결된 파이프가 밀어 넣는지 "
            "끌어내는지에 따라 결정됩니다.",
        ),
    ),
    "quest.7B500E0577BDFF8F.quest_desc": (("12가지", "열두 가지"),),
    "task.09788D3638E59F3B.title": (("계층 설치 프로그램", "등급 설치기"),),
    "task.11EF7663818B6CC6.title": (("쓰레기통", "단일 아이템 창고"),),
    "task.36B9FB74D9BF26E4.title": (("열역학적 도체", "열역학 전도체"),),
    "task.4558919345C3BE5D.title": (("강화제", "농축기"),),
    "task.4632192573FD8501.title": (("기계 파이프", "기계식 파이프"),),
    "task.4B60ACBCC3B46D1D.title": (("강화된 아이템", "농축 물질"),),
    "task.4B6C5B2099B18AB7.title": (("제련소", "제련기"),),
    "task.564D0E533237E951.title": (("정수기", "정화기"),),
    "task.729C1974AE346ECA.title": (("정수기", "정화기"),),
    "task.151AF2F49AAEBBDA.title": (("유도세포", "유도 셀"),),
    "task.496C4FDD2515EB24.title": (("유도 공급자", "유도 공급기"),),
    "quest.477B411F84342EEA.quest_desc": (
        ("mekanism은", "Mekanism은"),
        ("[best] 적합한", "가장 적합한"),
        ("[기본 Energy Cube]", "기본 에너지 큐브"),
        ("[Configure]하기", "설정하기"),
        ("[craft]하기", "제작하기"),
        ("[Power]", "에너지"),
        ("[upgrading]", "업그레이드"),
        ("[interface]", "GUI"),
        ("[아이템]", "아이템"),
        ("[Charge]", "충전"),
        ("[Energy Cube]", "에너지 큐브"),
        ("[chapter]", "챕터"),
    ),
    "quest.493D04D954E4FBA0.quest_desc": (("기술 모드od...인데", "기술 모드인데"),),
    "quest.6718043D0F2D1830.quest_desc": (
        (
            "DireWolf는 그의 카드 &5&lMekanism&r 및 its... 다른 물질 상태와 함께 "
            "작동하도록 요청받았습니다.",
            "DireWolf는 자신의 카드를 &5&lMekanism&r의 여러 물질 상태와 함께 "
            "사용할 수 있게 해 달라는 요청을 받았습니다.",
        ),
        (
            "모든 가압 튜브가 움직일 수 있는 것은 이 카드도 할 수 있습니다.",
            "이 카드는 가압 튜브가 운반하는 모든 물질을 옮길 수 있습니다.",
        ),
        ("가스, 주입 유형 및 안료.", "화학 물질, 주입 유형, 안료가 대상입니다."),
    ),
    "quest.3E32450DBB7529AA.quest_desc": (
        ("&eBatcher&r", "&e아이템 배처&r"),
        ("필터와 금액", "필터와 수량"),
    ),
    "quest.4A1C8125896F7F1A.quest_desc": (
        ("AllTheMods Staff", "AllTheMods 운영진"),
        ("All Rights Reserved", "모든 권리 보유"),
        ("AllTheMods Team", "AllTheMods 팀"),
        ("AllTheMods Modpack", "AllTheMods 모드팩"),
    ),
    "quest.4F7F0A5162D70082.quest_desc": (("만들어야 though...하며", "만들어야 하며"),),
    "quest.49F08DE190AAD0D8.quest_desc": (("mekanism의", "Mekanism의"),),
    "quest.14385D3D359224BC.quest_desc": (("Craft에", "제작할 때"),),
    "quest.16DDAE318535D0F9.quest_desc": (("스위핑 엣지(Sweeping Edge)", "휩쓸기"),),
    "quest.1FC88A3BFCE6C9D7.quest_desc": (
        ("Swift Sneaking Enchantment", "신속한 잠행 마법"),
    ),
    "quest.359934E888495E5E.quest_desc": (
        ("Dirty 광석 슬러리", "오염된 광석 슬러리"),
        ("Clean 광석 슬러리", "정제된 광석 슬러리"),
    ),
    "quest.3B936CA3F0F7B26B.quest_desc": (
        ("보이드 마이너(Void Miners)", "공허 채굴기"),
    ),
    "quest.459AEC4C2A611824.quest_desc": (("Night Vision", "야간 투시"),),
    "quest.5B9F3F32AB28A83A.title": (("Thermo 부분", "열 전달부"),),
    "quest.795B80BF12D23897.title": (("프로스트 워커", "차가운 걸음"),),
    "quest.69B5D716568AA9EB.quest_desc": (
        ("Mekanism Cables", "Mekanism 케이블"),
        ("ATM Stars", "ATM Star"),
    ),
    "quest.65A529C8238E89F1.quest_desc": (("좀 별로네요 though...", "좀 별로네요..."),),
    "quest.2DE7CC686B56881F.quest_desc": (("mekanism", "Mekanism"),),
    "quest.081DC030A0546549.quest_desc": (
        (
            "우리는 &a전력&r에 &2&l바이오 발전기&r, &9&l주입&r 아이템에 "
            "&2화학 바이오 연료&r를 사용하거나...",
            "&2&l바이오 발전기&r에서 &a전력&r을 만들거나, 아이템에 "
            "&2화학 바이오 연료&r를 &9&l주입&r하는 데 사용할 수 있고...",
        ),
    ),
    "quest.109310AF19AAC482.quest_desc": (
        (
            "&4화염방사기&r는 원거리 무기 &5&lMekanism&r 제공 중 하나입니다.",
            "&4화염 방사기&r는 &5&lMekanism&r이 제공하는 원거리 무기 중 하나입니다.",
        ),
        ("몹을 &6불&r로 설정하고", "몹에게 &6불&r을 붙이고"),
        (
            "&6열&r: 내가 알 수 있는 바는 똑같은 일을 할 수 있다는 것뿐입니다.",
            "&6가열&r: 대상 블록을 가열합니다.",
        ),
        ("&4인페르노&r: 모든 것을 불태운다!", "&4인페르노&r: 모든 것을 불태웁니다!"),
    ),
    "quest.119BED334E331C25.quest_desc": (
        (
            "최초이자 가장 간단한 &l광석 처리&r는 바로 2 &5기계&r입니다!",
            "가장 간단한 &l광석 처리&r에는 &5기계&r 2대만 있으면 됩니다!",
        ),
        ("&d&l강화제&r", "&d&l농축기&r"),
        ("&6&l제련소&r", "&6&l전동 제련기&r"),
        ("3 &7원석&f을 사용하여 4 &7가루&r", "&7원석&f 3개로 &7가루&r 4개"),
        (
            "&7가루&r를 &6제련&r하여 &7주괴&r를 획득하세요!",
            "&7가루&r를 &6제련&r해 &7주괴&r를 얻으세요!",
        ),
    ),
    "quest.1922623A26E08078.quest_desc": (
        (
            "&b유체탱크&r와 비슷하지만 &b유체&r를 조이면 다른 모든 것이 필요합니다!",
            "&b유체 탱크&r와 비슷하지만, 이번에는 &b유체&r가 아닌 물질을 저장합니다!",
        ),
        (
            "모든 &c가압관&r은 움직일 수 있고, &c화학탱크&r는 담을 수 있습니다.",
            "&c가압 튜브&r가 운반하는 모든 화학 물질을 &c화학 물질 탱크&r에 "
            "담을 수 있습니다.",
        ),
        ("64 화학 물질 버킷", "화학 물질 64버킷"),
        ("256 화학 물질 버킷", "화학 물질 256버킷"),
        ("1,024 화학 물질 버킷", "화학 물질 1,024버킷"),
        ("8,192 버킷을 보유합니다", "화학 물질 8,192버킷을 담습니다"),
    ),
    "quest.195729280394ABFB.quest_desc": (
        (
            "&7&r에 &e아이템&r에 &7오스뮴&r을 주입합니다. 더욱 강력한 잉곳을 "
            "만들 수 있습니다.",
            "&7오스뮴&r을 &e아이템&r에 주입하면 더욱 강력한 &7주괴&r를 만들 수 "
            "있습니다.",
        ),
        (
            "&7오스뮴 주괴&f, &7오스뮴 블록&f, 또는 &7오스뮴 화학 물질&r이 "
            "들어 있는 &c화학 탱크&f를 배치해야 합니다. &l&7컴프레서&r "
            "&7오스뮴&r!",
            "&7오스뮴 주괴&f, &7오스뮴 블록&f 또는 &7오스뮴 화학 물질&r이 든 "
            "&c화학 물질 탱크&f를 &l&7오스뮴 압축기&r에 넣어 &7오스뮴&r을 "
            "공급하세요!",
        ),
    ),
    "quest.1ABD22AA58E093A6.quest_desc": (
        ("&d&l궁극기&r &e아이템&r", "&d&l궁극 등급&r &e아이템&r"),
        (
            "예, 당신은 이 &5기계&r를 원할 것입니다. 시간과 재료의 가치가 있습니다!",
            "이 &5기계&r들은 제작에 든 시간과 재료가 아깝지 않을 만큼 강력합니다!",
        ),
    ),
    "quest.2A793B35FE25003C.quest_desc": (
        ("&l&c회전식 &b응축기&r", "&l&c회전 &b콘덴서&r"),
        (
            "&c&l화학적 &e산화 장치&r는 (일부) 회전할 수 있습니다. 아이템을 가스로!",
            "&c&l화학적 &e산화 장치&r는 일부 아이템을 화학 물질로 바꿉니다!",
        ),
        (
            "폐 빗과 리튬 빗을 &c화학 물질&r로 가져가는 데에도 필요합니다!",
            "사용한 벌집 조각과 리튬 벌집 조각을 &c화학 물질&r로 바꿀 때도 필요합니다!",
        ),
        (
            "새로운 &c가스&r 형태는 &9블루 바&r",
            "새로운 &c화학 물질&r은 &9파란색 막대&r",
        ),
    ),
    "quest.445CC9AAA6F8AAB6.quest_desc": (
        ("&b&l정수기&r", "&b&l정화기&r"),
        (
            "&7광석 블록&f에서 3 &7광석 덩어리&f를 얻을 수 있습니다. "
            "2 &7&7원광석&r에서 나온 &f광석 덩어리입니다.",
            "&7광석 블록&f에서는 &7광석 덩어리&f 3개를, &7&7원석&r에서는 "
            "&f광석 덩어리 2개를 얻습니다.",
        ),
    ),
    "quest.4B35C01F5D0AAC58.quest_desc": (
        ("&9&l야금 주입&r", "&9&l금속공학 주입&r"),
        (
            "10mB의 &0탄소&r를 추가하여 지금 이 단계를 반복해야 합니다!",
            "이 단계에서 &0탄소&r 10mB를 한 번 더 주입해야 합니다!",
        ),
        (
            "&8철&r은 거의 모든 곳에 사용됩니다!",
            "&8강철&r은 거의 모든 곳에 사용됩니다!",
        ),
    ),
    "quest.602A6CF9D5B66AD3.quest_desc": (
        ("&5&l화학결정기&r", "&5&l화학적 결정화 장치&r"),
        (
            "그리고 그렇습니다. 이것은 &l광석 처리&r에만 사용되는 것이 아닙니다! "
            "글쎄요, 일부는... 하지만 전부는 아닙니다.",
            "이 기계는 &l광석 처리&r뿐 아니라 다른 화학 물질을 고체로 만드는 데도 "
            "사용됩니다.",
        ),
        ("&5&l결정화 장치&r", "&5&l화학적 결정화 장치&r"),
    ),
    "quest.6B8040401B512E50.quest_desc": (
        ("&3&l화학 용해 챔버&r", "&3&l화학적 용해 장치&r"),
        ("&9블루 바&r", "&9파란색 막대&r"),
    ),
    "quest.7ECA0633AF1AEC19.quest_desc": (
        ("&6목재 품목&r", "&6목재 아이템&r"),
        (
            "침대를 3 &6나무 판자&r와 3 양모로 바꿔줍니다.",
            "침대에서 &6나무 판자&r 3개와 양털 3개를 회수합니다.",
        ),
        ("&6문&r을 &6나무 판자&r로.", "&6문&r도 &6나무 판자&r로 되돌립니다."),
        (
            "그리고 4 대신 &2&f을 6 &6판자&r에 로그인합니다!",
            "그리고 &2원목&f 하나로 &6판자&r를 4개 대신 6개 만듭니다!",
        ),
    ),
    "quest.008E65AF545A706E.quest_desc": (
        (
            "&a케이블&r &m일부&r 막대한 양의 &a에너지&r를 &dSPS 포트&r에 연결하여",
            "&a케이블&r로 &m아주&r 많은 &a에너지&r를 &dSPS 포트&r에 공급하여",
        ),
        (
            "각 &d과급 코일&r은 &a에너지&r만큼만 사용할 수 있으므로",
            "각 &d과급 코일&r이 처리할 수 있는 &a에너지&r에는 한계가 있으므로",
        ),
        ("2 사용하세요", "2개를 사용하세요"),
        ("1을 사용할 수 있지만", "1개만 사용할 수도 있지만"),
        (
            "&a폴로늄&r에 &m충분한&r 수백만 개의 FE를 폭파하면",
            "&a폴로늄&r에 수백만 FE의 에너지를 &m충분히&r 공급하면",
        ),
        ("&c화학&r &d반물질&r", "&c화학 물질&r인 &d반물질&r"),
    ),
    "quest.3CCBE9BBCA8ADA38.quest_desc": (
        ("수억 개의 FE", "수억 FE"),
        ("최소한 1(2 권장)", "최소 1개(2개 권장)"),
        ("&d슈퍼차지 코일&r", "&d과급 코일&r"),
        (
            "&d포트&r는 &d과급 코일 &a에너지&r를 공급해야 합니다.",
            "&d포트&r를 통해 &d과급 코일&r에 &a에너지&r를 공급해야 합니다.",
        ),
        (
            "그리고 &d반물질&r을 위해서는 그것들이 엄청나게 많이 필요할 것입니다!",
            "&d반물질&r을 만들려면 이 에너지가 엄청나게 많이 필요합니다!",
        ),
    ),
    "quest.234C2C3144817018.quest_desc": (
        (
            "&6열&r을 제외한 모든 것. 게다가 &e아이템&r 출력과 &c화학&r 출력 해치까지!",
            "&6열&r을 제외한 모든 입력과 &e아이템&r 출력, &c화학 물질&r 출력 "
            "해치가 필요합니다!",
        ),
        (
            "32 &b폴로늄 펠릿&r을 한 번에 만들거나, 8 &a기재&r를 64으로 만드세요!",
            "&b폴로늄 펠릿&r 32개를 한 번에 만들거나, &a기질&r 8개로 64개를 만드세요!",
        ),
    ),
    "quest.3561A33758A1E8C3.quest_desc": (
        (
            "먼저, 우리는 구축합니다. 둘째, 시작합니다. 셋째, 사용합니다.",
            "첫째, 구조를 짓습니다. 둘째, 가동합니다. 셋째, 사용합니다.",
        ),
        ("5 블록 롱 다이아몬드 형태", "한 변이 5블록인 마름모 형태"),
        ("팔! 지어졌습니다! 이제 이 강아지를", "쾅! 완성됐습니다! 이제 이 녀석을"),
        (
            "최소한 1GFE를 갖춘 &4레이저 증폭기&r를 &c레이저 초점 매트릭스&r로 "
            "폭발시킬 수 있습니다.",
            "&4레이저 증폭기&r에 최소 1GFE를 모아 &c레이저 초점 매트릭스&r로 "
            "발사하세요.",
        ),
        (
            "이것은 &a에너지&r의 양을 결정하거나 스팀이 생성됩니다!",
            "이 온도에 따라 생성되는 &a에너지&r 또는 증기의 양이 달라집니다!",
        ),
        (
            "그것들은 괴상한 사람들에게만 중요하므로 우리는 그들에게 집중하지 "
            "않을 것입니다!",
            "이 수치는 전문적인 조정에 쓰이므로 여기서는 자세히 다루지 않겠습니다!",
        ),
    ),
    "quest.3D2B4D9FD2086B9B.quest_desc": (
        ("&2핵분열로 논리 어댑터&r", "&2핵분열로 로직 어댑터&r"),
        ("&2&l리액터&r", "&2&l핵분열로&r"),
        ("중요 폐기물 수준", "핵폐기물 위험 수준"),
        ("손상 심각", "심각한 손상"),
        ("&4신호&r를 제공합니다", "&4신호&r를 출력합니다"),
    ),
    "quest.4211F29561F21643.quest_desc": (
        (
            "&9포트&r를 통해 증기에서 작동하고 증기이 &9로터&r의 "
            "&9블레이드&r를 이동시키는 것입니다.",
            "&9포트&r로 증기를 받아, 그 증기로 &9로터&r의 &9블레이드&r를 "
            "회전시키는 방식입니다.",
        ),
        ("2 &9블레이드&r", "&9블레이드&r 2개"),
        (
            "내부가 더 큰 5x5 베이스는 사용할 수 없습니다.",
            "5x5 바닥으로는 더 넓은 내부 구조를 만들 수 없습니다.",
        ),
    ),
    "quest.54255B7820A0F0B1.quest_desc": (
        (
            "10,240 &8핵폐기물&r에서 2,048 &b폴로늄&r로.",
            "&8핵폐기물&r 10,240을 &b폴로늄&r 2,048로 바꿉니다.",
        ),
        (
            "게다가 2,048 &a육불화우라늄&r를 2,048 &2핵분열성 연료&r에 추가합니다.",
            "또 &a육불화우라늄&r 2,048을 &2핵분열성 연료&r 2,048로 바꿉니다.",
        ),
    ),
    "quest.593CB120B657126C.quest_desc": (
        (
            "이제 드디어 &a방사능&r에 대해 걱정할 수 있게 되었습니다!",
            "이제 &a방사능&r 안전을 반드시 신경 써야 합니다!",
        ),
        ("&8핵폐기물&r(및 그 제품)", "&8핵폐기물&r과 그 부산물"),
        ("&e방사성 폐기물 통&r", "&e방사성 폐기물 배럴&r"),
        (
            "&a방사성&r 물질을 담는 &e통&r 또는 &c튜브&r를 깨뜨릴 수 없습니다.",
            "&a방사성&r 물질이 든 &e배럴&r이나 &c튜브&r를 부수면 안 됩니다.",
        ),
        ("&2&l원자로&r가 누출되거나 녹아서", "&2&l반응기&r가 누출되거나 노심 용융되어"),
    ),
    "quest.5A088F8402230BA5.quest_desc": (
        ("&2핵분열로 포트&r 꽤 중요해요.", "&2핵분열로 포트&r는 매우 중요합니다."),
        (
            "&2연료&f용 포트가 필요합니다., &b냉각수&f, 그리고 &8폐기물&r...",
            "&2연료&f, &b냉각수&f, &8폐기물&r을 처리할 포트가 필요합니다...",
        ),
        ("그 중 4이 필요하고", "포트는 4개가 필요하며"),
        ("&3구성자&r", "&3설정 장치&r"),
        ("Shift 오른쪽 클릭", "Shift+우클릭"),
        ("&e 배출 폐기물&r", "&e폐기물 출력&r"),
        ("&b출력 냉각수&r", "&b냉각재 출력&r"),
    ),
    "quest.5AEA705D6A64A982.quest_desc": (
        (
            "작동하려면 &e일광&r이 필요하다고 말할 수 있습니다!",
            "이 기계는 작동하려면 &e일광&r이 필요합니다!",
        ),
        (
            "야간에는 &2&l반응기&r를 끌 수 있습니다!",
            "밤에는 &2&l반응기&r를 끄게 만드세요!",
        ),
        ("&2&l리액터&r", "&2&l핵분열로&r"),
        ("그럼 붐, 준비됐어요!", "이제 안전 장치가 완성됐습니다!"),
    ),
    "quest.67A9329C05F98633.quest_desc": (
        ("&2&l리액터&r", "&2&l반응기&r"),
        ("그냥 삭제하세요!", "증기를 그냥 버리세요!"),
        ("그냥 스팀 삭제하세요!", "증기를 폐기하라는 뜻입니다!"),
        (
            "필요하지 않습니까? 그런 다음 최종 쓰레기통에 튜브로 담아보세요!",
            "필요하지 않다면 가압 튜브로 궁극 쓰레기통에 보내세요!",
        ),
    ),
    "quest.7B0764DDE94E73D0.quest_desc": (
        ("&2&l리액터&r", "&2&l반응기&r"),
        ("5 블록 너비", "너비 5블록"),
        ("2 &2FRLA&r에 대한 3 블록 너비", "&2FRLA&r 2개를 놓을 3블록 너비"),
        ("&2FRLA&r의 1을 배치하고", "&2FRLA&r 하나를 배치하고"),
        ("최소한 1 블록", "최소 1블록"),
        ("손상 심각", "심각한 손상"),
        ("&4리피터&r", "&4중계기&r"),
    ),
    "quest.7D279FC39DA5C630.quest_desc": (
        ("&c&l회전식 &b응축기&r", "&c&l회전 &b콘덴서&r"),
        ("더 &c주입&r!", "다시 &c주입&r할 차례입니다!"),
        (
            "글쎄요, 지금은 애시드지만... 올바른 애시드는 아닙니다...",
            "산을 만들긴 했지만... 아직 필요한 산은 아닙니다...",
        ),
        ("&3&l화학적 용해 챔버&r", "&3&l화학적 용해 장치&r"),
    ),
    "quest.603BEDD49070ECAD.quest_desc": (
        ("&c&l로터리 &b콘덴스트레이터&r", "&c&l회전 &b콘덴서&r"),
        ("&c가스&r는 왼쪽 바", "&c화학 물질&r은 왼쪽 막대"),
        ("&c화학 탱크&r", "&c화학 물질 탱크&r"),
        ("&c가스&r는 &b액체&r", "&c화학 물질&r은 &b액체&r"),
        ("&b액체&r는 &c가스&r", "&b액체&r는 &c화학 물질&r"),
        ("&b유체탱크&r", "&b유체 탱크&r"),
    ),
    "quest.7952DA35B4F5C598.quest_desc": (
        (
            "&7버킷&r만으로는 충분하지 않은 것이 무엇입니까?",
            "&7양동이&r 하나로는 부족하다고요?",
        ),
        ("&7버킷&r 한 뭉치", "&7양동이&r 한 묶음"),
        ("&b유체탱크&r", "&b유체 탱크&r"),
        (
            "&b유체 탱크&r는 하나의 &b유체&r 중 여러 &7버킷&r을 수용할 수 있으며 "
            "&7버킷&r처럼 이동할 수 있습니다.",
            "&b유체 탱크&r는 한 종류의 &b유체&r를 &7양동이&r 여러 개분 저장하고 "
            "&7양동이&r처럼 들고 옮길 수 있습니다.",
        ),
        (
            "&b유체&r를 추가하거나 제거하려면 또는 중 하나를 수행하도록 구성된 "
            "&b기계 파이프&r가 필요합니다.",
            "&b유체&r를 넣거나 빼려면 해당 방향으로 설정한 &b기계 파이프&r가 "
            "필요합니다.",
        ),
    ),
    "quest.3EC9D0DA61B45328.quest_subtitle": (
        ("가스를 태워서 힘을 얻으세요", "기체를 태워 전력을 생산하세요"),
    ),
    "quest.3EC9D0DA61B45328.title": (("가스발전기", "기체 연소 발전기"),),
    "quest.2F4458E9921DEB86.quest_desc": (
        ("&a가스&r 형태의 마지막 물질 상태", "&a화학 물질&r이라는 별도 전송 형식"),
        ("&a가스&r는 다른", "&a화학 물질&r은 다른"),
        ("&a가스 파이프&r", "&a화학 물질 파이프&r"),
        ("&a가스&r인지", "&a화학 물질&r인지"),
        ("&a가스&r 또는 &b액체&r", "&a화학 물질&r 또는 &b액체&r"),
    ),
}

MEKANISM_CUSTOM_NAMES = {
    "Crushers": ("분쇄기", 3),
    "Enrichers": ("농축기", 3),
    "Smelters": ("제련기", 3),
    "Purifiers": ("정화기", 1),
    "Purificaters": ("정화기", 1),
}

EARLY_INFRASTRUCTURE_CUSTOM_NAMES = {
    "Spooky Pumpkin": ("으스스한 호박", 1),
    "Christmas Tree Sapling": ("크리스마스트리 묘목", 1),
}

MODERN_INDUSTRIALIZATION_CUSTOM_NAMES = {
    "Item Input": ("아이템 입력", 5),
    "Item Output": ("아이템 출력", 4),
    "Energy Input": ("에너지 입력", 6),
    "Fluid Input": ("유체 입력", 4),
    "Fluid Output": ("유체 출력", 4),
    "Uranium Rods": ("우라늄 막대", 1),
    "HE Uranium Rods": ("HE 우라늄 막대", 1),
    "LE Uranium Rods": ("LE 우라늄 막대", 1),
    "LE Mox Rods": ("LE MOX 막대", 1),
    "HE Mox Rods": ("HE MOX 막대", 1),
}

MODERN_INDUSTRIALIZATION_QUEST_FALLBACK_TITLES = {
    "quest.4F870252E9FB1A41.title": "우라늄 막대",
    "quest.5E7682F4C95DCDCA.title": "HE 우라늄 막대",
    "quest.5C36DA71C58A5365.title": "LE 우라늄 막대",
    "quest.44ED74C0F2F43B3B.title": "LE MOX 막대",
    "quest.6F9C270C3794BAD1.title": "HE MOX 막대",
}

INDUSTRIAL_FOREGOING_QUEST_FALLBACK_TITLES = {
    "quest.2E8E292ED596A104.title": "&5보라색 레이저 렌즈",
}

MEKANISM_QUEST_ITEM_TITLES = {
    "quest.162CE44400A63575.title": "금속공학 주입기",
    "quest.08DDE018A804BFE7.title": "농축기",
    "quest.7AE502EDB73BD57A.title": "분쇄기",
    "quest.166971866A9234C7.title": "주입 합금",
    "quest.488DBE69595F38F8.title": "전동 제련기",
    "quest.001DE8028CAF0A08.title": "방음 업그레이드",
    "quest.09830BB2A23E94B4.title": "화학 물질 업그레이드",
    "quest.515A60B89ED5440D.title": "돌 생성 업그레이드",
    "quest.74200A48498DD7F8.title": "태양광 발전기",
    "quest.0650996C7818ADB5.title": "열 발전기",
    "quest.6CD1720B76F47806.title": "바이오연료 발전기",
    "quest.4EDD96EB60EF5814.title": "고급 태양광 발전기",
    "quest.7778937DF377C1B4.title": "풍력 발전기",
    "quest.7ECA0633AF1AEC19.title": "정밀 제재기",
    "quest.33415CB421F7620A.title": "정화기",
    "quest.27512B0434531195.title": "화학 주입실",
    "quest.566C1DBA9829E328.title": "결합기",
    "quest.60B52705049D1BA5.title": "화학적 세척 장치",
    "quest.6B8040401B512E50.title": "화학적 용해 장치",
    "quest.602A6CF9D5B66AD3.title": "화학적 결정화 장치",
    "quest.18783C62009934DB.title": "전해 분리기",
    "quest.2A793B35FE25003C.title": "화학적 산화 장치",
    "quest.376532CD98D39781.title": "화학적 반응 장치",
    "quest.71869B1D81D6A7EF.title": "가압 반응 장치",
    "quest.603BEDD49070ECAD.title": "회전 콘덴서",
    "quest.2D1CBCEC82F1B37D.title": "장작 가열기",
    "quest.21F3379C904BFD50.title": "전기 저항 가열기",
    "quest.4274E777FB60BA28.title": "충전 패드",
    "quest.041365A540BF5A03.title": "광석 사전",
    "quest.424B3E3B299D3999.title": "스포이트",
    "quest.109310AF19AAC482.title": "화염 방사기",
    "quest.4E7823C2FCEBE4DC.title": "전동 활",
    "quest.3D2B4D9FD2086B9B.title": "핵분열로 로직 어댑터",
    "quest.5A088F8402230BA5.title": "핵분열로 포트",
    "quest.6A1174845810C7A1.title": "모듈 제어기",
    "quest.7864C8F2CBC910CB.title": "메카슈트 투구",
    "quest.6C1F7A0B330B3F42.title": "메카슈트 흉갑",
    "quest.56DB53F255100136.title": "메카슈트 각반",
    "quest.6D7D0A5313284B53.title": "메카슈트 부츠",
    "quest.0306D25C7407FE88.title": "레이저 초점 매트릭스",
}

MEKANISM_QUEST_ELEMENT_OVERRIDES = {
    "quest.0095422BC87AA135.quest_desc": {
        0: (
            "다시요? 필요한 건 &7주괴&f이지, &7덩어리&f나 &7조각&r이 아니에요! "
            "&7주괴&r 말입니다! \\n\\n"
            "&7광석 조각&r을 &b산소&r와 함께 &b&l정화기&r에 넣으면 "
            "&7광석 덩어리&r가 됩니다. 산소는 앞서 만든 &9&l전해 분리기&r에서 "
            "가져오면 됩니다. \\n\\n"
            "이제 이전 단계와 같은 과정을 반복하세요. &7덩어리&f를 &4분쇄&f해 "
            "&7오염된 가루&r를 얻습니다. \\n\\n"
            "&7오염된 가루&r를 &d농축&f해 깨끗하게 만드세요. \\n\\n"
            "마지막으로 &7가루&f를 &6제련&f하면 &7주괴&r가 완성됩니다!"
        ),
    },
    "quest.18783C62009934DB.quest_desc": {
        0: (
            "&9&l전해 분리기&r는 1종의 &b유체&r를 2종의 &c화학 물질&r로 "
            "분리합니다! \\n\\n"
            "&b유체&r는 &4빨간색 막대&r로 들어가고, 생성된 &c화학 물질&r은 "
            "&9파란색&f과 &3청록색 막대&r에 표시됩니다. \\n\\n"
            "GUI 아래쪽의 버튼으로 두 출력 막대의 동작을 각각 바꿀 수 있습니다. "
            "\\n\\n대기는 저장 한도에 도달하면 생산을 멈춥니다. 예를 들어 수소가 가득 "
            "차면 더 이상 &9물&r을 소비하지 않습니다. \\n\\n"
            "초과분 버리기는 막대가 가득 차도 넘치는 양만 버려 각 &c화학 물질&r "
            "생산을 계속합니다. "
            "수소보다 &b산소&r가 많이 필요할 때 유용합니다. \\n\\n"
            "모두 버리기는 생성되는 &c화학 물질&r을 전부 삭제합니다."
        ),
    },
    "quest.03840E4C74731E0C.quest_desc": {
        0: (
            "지금까지 대부분의 &5&lMekanism&r 퀘스트에서 &9전기 펌프&r를 "
            "사용하라고 했습니다. \\n\\n하지만 이제 졸업할 때예요. &2&l반응기&r에는 "
            "훨씬 많은 &9물&r이 필요하니 &9싱크대&r를 사용하세요! \\n\\n"
            "&9싱크대&r는 &9물&r을 무한히 공급하며 거의 모든 모드의 파이프로 "
            "&b추출&r할 수 있습니다. 사용할 수 있다면 틱마다 &9물&r을 2빌리언 mB "
            "넘게 끌어오는 &9&lID&r를 권장합니다! \\n\\n"
            "앞에서 &9전기 펌프&r를 사용한 이유는 여러분에게 &9싱크대&r를 맡길 "
            "수 없어서가 아니라 두 가지입니다. 1. &9싱크대&r가 "
            "없는 모드팩에서도 설명이 유효하고, 2. 전기 펌프가 &5&lMekanism&r의 "
            "기계이기 때문입니다. "
        ),
    },
    "quest.438F734D16DA9638.quest_desc": {
        0: (
            "&a폴로늄&r을 얻었으니 나머지 재료는 이미 갖추었을 거예요! \\n\\n"
            "&2&lP.R.C.&r, &9물&r, &d형석 가루&r가 필요합니다. \\n\\n"
            "1,000mB의 &9물&r, 1,000mB의 &a폴로늄&r, 1개의 &d형석 가루&r를 "
            "조합하면 1개의 &a폴로늄 펠릿&r과 1,000mB의 &8사용후핵폐기물&r을 "
            "얻습니다. \\n\\n"
            "&d형석 가루&r는 다른 금속 가루처럼 &4&l분쇄기&r, "
            "&d&l농축기&r 또는 광석 망치로 만들 수 있습니다!"
        ),
    },
    "quest.7B0DFA55B4D8B16D.quest_desc": {
        0: (
            "&a&l텔레포터&r는 &5기계&r를 완성하고 &a전원을 공급&r하면 어느 "
            "차원이든 원하는 곳으로 순간이동할 수 있게 해 줍니다! \\n\\n"
            "그럼 어떻게 만들고 전원을 공급하는지 알아봅시다. \\n\\n"
            "&a&l텔레포터&r 하나에는 1개의 &a텔레포터 블록&f과 9개의 "
            "&a텔레포터 프레임&r이 필요합니다. \\n\\n"
            "&a텔레포터 블록&r은 &a&l텔레포터&r의 주 &a제어기&r이며 "
            "&a에너지&r를 받는 블록입니다. &a전원이 공급&r되면 GUI를 열어 "
            "&5양자 전송기&r처럼 네트워크 이름을 입력하고 체크 표시를 눌러 "
            "네트워크를 만들 수 있습니다. \\n\\n"
            "다른 &a&l텔레포터 구조물&r이나 &a텔레포터 블록&r도 GUI에서 같은 "
            "네트워크를 선택하면, &a&l텔레포터&r를 통해 같은 네트워크의 다른 "
            "&a&l텔레포터&r로 이동할 수 있습니다. \\n\\n"
            "&a&l텔레포터 구조물&r을 만들려면 &a텔레포터 블록&r 양옆에 "
            "&a텔레포터 프레임&r을 하나씩 놓고, 그 위로 3개씩 더 쌓아 전체 높이를 "
            "4블록으로 만드세요. &a텔레포터 블록&r 위에 2블록 높이의 빈 공간을 "
            "남기고 마지막 &a텔레포터 프레임&r으로 위쪽을 연결합니다. \\n\\n"
            "전원을 공급하고 네트워크를 설정하면 &a&l텔레포터&r에 색깔 있는 "
            "포털이 나타납니다! \\n\\n포털 색상은 &a&l텔레포터&r GUI에서 바꿀 수 있습니다."
        ),
    },
    "quest.7E4367252A39BE6C.quest_desc": {
        0: (
            "&c&lPowah!&r는 전력을 생산하는 모드입니다! 생산한 FE로 "
            "&5&lMekanism&r이나 &lIndustrial Foregoing&r 같은 다른 모드의 "
            "기계를 작동할 수 있습니다. \\n\\n여러 등급을 차례로 제작해야 하며, "
            "마지막 등급은 물론 &6&lATM Star&r에 필요합니다!"
        ),
    },
}

TIER_KO = {
    "Basic": "기본",
    "Advanced": "고급",
    "Elite": "엘리트",
    "Ultimate": "궁극",
    "Overclocked": "오버클럭",
    "Quantum": "양자",
    "Dense": "고밀도",
    "Multiversal": "다중우주",
    "Creative": "크리에이티브",
}

MEKANISM_EXACT = {
    "Damage": "피해",
    "Efficiency": "효율",
    "Enchantability": "마법 부여 적합성",
    "Applied Mekanistics": "Applied Mekanistics",
    "Chemical": "화학 물질",
    "Large Antiprotonic Nucleosynthesizer": "대형 반양성자 핵합성기",
    "Large Pigment Mixer": "대형 안료 혼합기",
    "Large Wind Generator": "대형 풍력 발전기",
    "Pigment Extracting": "안료 추출",
    "Painting": "염색",
    "Max Chemical Tanks": "최대 화학 물질 탱크",
    "Edit Max Chemical Tanks": "최대 화학 물질 탱크 편집",
    "Settings for configuring Max Chemical Tanks": "최대 화학 물질 탱크 설정",
    "Mid Chemical Tanks": "중간 화학 물질 탱크",
    "Edit Mid Chemical Tanks": "중간 화학 물질 탱크 편집",
    "Settings for configuring Mid Chemical Tanks": "중간 화학 물질 탱크 설정",
    "Tier Config": "등급 설정",
    "Mekanism: MoreMachine - Tier Config": "Mekanism: MoreMachine - 등급 설정",
    "Mekanism Config": "Mekanism 설정",
    "Mekanism - Client Config": "Mekanism - 클라이언트 설정",
    "Mekanism - Common Config": "Mekanism - 공통 설정",
    "Mekanism - General Config": "Mekanism - 일반 설정",
    "Client Config": "클라이언트 설정",
    "Common Config": "공통 설정",
    "General Config": "일반 설정",
    "LostMyself": "LostMyself",
    "TedXenon": "TedXenon",
    "Supercharging Elements: %s": "초충전 소자: %s",
    "Processing Speed": "처리 속도",
}

MEKANISM_KEY_OVERRIDES = {
    "constants.gmut.key_category": (
        "Mekanism - Gravitational Modulating Additional Unit"
    ),
    "constants.gmut.mod_name": "Gravitational Modulating Additional Unit",
    "block.mekanism.chemical_injection_chamber": "화학 주입실",
    "block.mekanismgenerators.control_rod_assembly": "제어봉 집합체",
    "block.mekanismgenerators.fission_fuel_assembly": "핵분열 연료 집합체",
    "block.mekanismgenerators.fission_reactor_casing": "핵분열로 케이싱",
    "block.mekanismgenerators.fission_reactor_logic_adapter": "핵분열로 로직 어댑터",
    "block.mekanismgenerators.fission_reactor_port": "핵분열로 포트",
    "command.mekanism.error.retrogen.disabled": (
        "소급 생성이 비활성화되어 있습니다. 설정에서 활성화해 주세요."
    ),
    "command.mekanism.error.retrogen.failure": (
        "소급 생성할 청크를 대기열에 추가하지 못했습니다."
    ),
    "configuration.mekanism.client.qio.rejects.destination.tooltip": (
        "조합법 뷰어로 조합 격자의 아이템을 교체할 때, QIO 조합 창에 있던 "
        "아이템을 플레이어 인벤토리와 QIO 주파수 중 어디로 먼저 옮길지 결정합니다."
    ),
    "configuration.mekanism.gear.meka_suit.damage_absorption.unspecified.tooltip": (
        "메카슈트에 에너지가 충분하고 전 부위를 착용했을 때, 방어구를 무시하지 "
        "않으면서 별도로 지원되지 않는 기타 피해 유형에서 흡수할 피해 비율입니다. "
        "특정 피해 유형은 mekanism:mekasuit_absorption 데이터 맵에 항목을 추가해 "
        "지원할 수 있습니다."
    ),
    "configuration.mekanism.general.security.ops_bypass": "관리자 보안 우회",
    "configuration.mekanism.general.security.ops_bypass.tooltip": (
        "활성화하면 'mekanism.bypass_security' 권한이 있는 플레이어가 블록과 "
        "아이템의 보안 제한을 우회할 수 있습니다. 이 권한은 기본적으로 서버 "
        "관리자에게 부여됩니다."
    ),
    "description.mekanism.solar_neutron_activator": (
        "태양의 중성자 방사선을 내부 저장소에 집중시켜 여러 동위원소를 천천히 "
        "생성하는 기계입니다."
    ),
    "configuration.mekanism.usage.fluidic_plenisher.energy.tooltip": (
        "액체 방출기의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.usage.formulaic_assemblicator.energy.tooltip": (
        "공식 조합기의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.usage.isotopic_centrifuge.energy.tooltip": (
        "동위원소 원심분리기의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.usage.laser.energy.tooltip": (
        "레이저의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.usage.modification_station.energy.tooltip": (
        "모듈 제어기의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.usage.nucleosynthesizer.energy.tooltip": (
        "반양성자 핵합성기의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.usage.nutritional_liquifier.energy.tooltip": (
        "영양 액화기의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.usage.osmium_compressor.energy.tooltip": (
        "오스뮴 압축기의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.usage.painting_machine.energy.tooltip": (
        "염색기의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.usage.pigment_extractor.energy.tooltip": (
        "안료 추출기의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.usage.pigment_mixer.energy.tooltip": (
        "안료 혼합기의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.usage.precision_sawmill.energy.tooltip": (
        "정밀 제재기의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.usage.pressurized_reaction_chamber.energy.tooltip": (
        "가압 반응 장치의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.usage.purification_chamber.energy.tooltip": (
        "정화기의 작업당 에너지 사용량(J)입니다."
    ),
    "configuration.mekanism.world.retrogen.tooltip": (
        "기존 청크에 Mekanism 소금과 광석 블록을 소급 생성합니다. 일반적으로 이 "
        "기능을 활성화할 때는 userWorldGenVersion 값도 올려야 합니다."
    ),
    "chemical.mekanism.brine": "소금물",
    "description.mekanismgenerators.reactor.logic.depleted": (
        "반응기가 핵분열을 계속할 연료가 부족할 때 신호를 출력합니다."
    ),
    "description.mekanismgenerators.reactor.logic.ready": (
        "핵융합로가 가동에 필요한 온도에 도달했을 때 신호를 출력합니다."
    ),
    "block.mekanismgenerators.advanced_solar_generator": "고급 태양광 발전기",
    "block.mekanismgenerators.heat_generator": "열 발전기",
    "gui.mekanism.digital_miner.max": "최대 Y 높이: %1$s",
    "gui.mekanism.digital_miner.min": "최소 Y 높이: %1$s",
    "miner.mekanism.radius": "블록 반경: %1$s",
    "multiblock.mekanism.invalid_inner": (
        "내부 구조의 %1$s 위치에 잘못된 블록(%2$s)이 있습니다."
    ),
    "mekanisticrouters.itemText.usage.item.chemical_module_mk1": (
        "모듈 방향에 있는 인접 블록과 라우터 사이에서 화학 물질을 전송합니다.\n"
        "• 라우터 버퍼에 화학 물질 용기 아이템이 있어야 합니다."
    ),
    "mekanisticrouters.itemText.usage.item.chemical_module_mk2": (
        "주변 블록과 라우터 사이에서 화학 물질을 전송합니다.\n"
        "• 라우터 버퍼에 화학 물질 용기 아이템이 있어야 합니다.\n"
        "• 탱크와도 주고받을 수 있습니다."
    ),
    "mekanisticrouters.guiText.popup.chemical_refill.control": (
        "§a§C화학 물질 재충전 모듈§r\n\n여기에서 다음 항목을 정할 수 있습니다: "
        "\n- 플레이어 인벤토리에서 상호작용할 구역\n\n필터는 이 모듈에서 "
        "화학 물질을 받을 수 있는 아이템을 제어합니다."
    ),
    "block.mekmm.ambient_gas_collector": "대기 가스 수집기",
    "configuration.mekmm.general.collect.amount.tooltip": (
        "대기 가스 수집기가 수집하는 불안정 차원 가스의 양(mB)입니다."
    ),
    "configuration.mekmm.storage.ambient_gas_collector.energy": (
        "대기 가스 수집기 에너지 저장소"
    ),
    "configuration.mekmm.storage.ambient_gas_collector.energy.tooltip": (
        "대기 가스 수집기의 기본 에너지 저장량(J)입니다."
    ),
    "configuration.mekmm.usage.ambient_gas_collector.energy": (
        "대기 가스 수집기 에너지 사용량"
    ),
    "configuration.mekmm.usage.ambient_gas_collector.energy.tooltip": (
        "대기 가스 수집기의 작업당 에너지 사용량(J)입니다."
    ),
    "info.mekmm.jei.unstable_dimensional_gas": (
        "대기 가스 수집기로 수집합니다(%1$s mB/t). 기계 위에는 블록을 놓지 마세요."
    ),
    "item.refinedstorage_mekanism_integration.chemical_storage_disk.help": (
        "%s버킷을 저장합니다. 비어 있을 때 손에 들고 사용하면 화학 물질 저장 부품을 "
        "돌려받습니다. 화학 물질 저장 부품과 조합해 더 높은 등급으로 업그레이드할 수 "
        "있습니다."
    ),
    "item.refinedstorage_mekanism_integration.creative_chemical_storage_disk.help": (
        "버킷을 무한히 저장합니다."
    ),
    "item.refinedstorage_mekanism_integration.chemical_storage_block.help": (
        "%s버킷을 저장합니다. 비어 있을 때 손에 들고 사용하면 화학 물질 저장 부품과 "
        "기계 케이싱을 돌려받습니다. 화학 물질 저장 부품과 조합해 더 높은 등급으로 "
        "업그레이드할 수 있습니다."
    ),
    "item.refinedstorage_mekanism_integration.creative_chemical_storage_block.help": (
        "버킷을 무한히 저장합니다."
    ),
    "advancements.refinedstorage_mekanism_integration.storing_chemicals": (
        "화학 물질 저장"
    ),
    "advancements.refinedstorage_mekanism_integration.storing_chemicals.description": (
        "화학 물질 저장 디스크를 제작해 디스크 드라이브에 넣으세요."
    ),
    "refinedstorage_mekanism_integration.configuration.title": (
        "Refined Storage - Mekanism Integration 설정"
    ),
    "refinedstorage_mekanism_integration.configuration.section.refinedstorage_mekanism_integration.common.toml": (
        "Refined Storage - Mekanism Integration 설정"
    ),
    "refinedstorage_mekanism_integration.configuration.section.refinedstorage_mekanism_integration.common.toml.title": (
        "Refined Storage - Mekanism Integration 설정"
    ),
    "config.refinedstorage_mekanism_integration.option.chemicalStorageBlock.tooltip": (
        "화학 물질 저장 블록 설정입니다."
    ),
}


def sha256(path: Path) -> str:
    """파일 SHA-256을 계산한다."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def duplicate_keys(raw: str) -> list[str]:
    """JSON 객체의 중복 키를 찾는다."""
    duplicates: list[str] = []

    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        counts = Counter(key for key, _ in pairs)
        duplicates.extend(key for key, count in counts.items() if count > 1)
        return dict(pairs)

    json.loads(raw, object_pairs_hook=hook)
    return sorted(set(duplicates))


def load_json_bytes(raw: bytes) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError("언어 JSON 최상위 값이 객체가 아닙니다.")
    return value


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 파일에서 읽는다."""
    return load_json_bytes(path.read_bytes())


def find_jar(instance: Path, prefix: str) -> Path:
    """접두사로 설치 JAR 하나를 확정한다."""
    matches = sorted(
        path
        for path in (instance / "mods").glob("*.jar")
        if path.name.lower().startswith(prefix.lower())
    )
    if len(matches) != 1:
        raise RuntimeError(f"JAR을 하나로 확정하지 못했습니다: {prefix}:{matches}")
    return matches[0]


def targets_for(family: str) -> tuple[Target, ...]:
    """모드군의 언어 대상을 반환한다."""
    return tuple(target for target in TARGETS if target.family == family)


def language_paths(namespace: str) -> tuple[str, str]:
    """영어와 한국어 언어 파일 경로를 반환한다."""
    return (
        f"assets/{namespace}/lang/en_us.json",
        f"assets/{namespace}/lang/ko_kr.json",
    )


def read_mod_metadata(archive: ZipFile) -> str:
    """모드 메타데이터 원문을 가능한 위치에서 읽는다."""
    candidates = (
        "META-INF/neoforge.mods.toml",
        "META-INF/mods.toml",
        "fabric.mod.json",
    )
    for name in candidates:
        if name in archive.namelist():
            return archive.read(name).decode("utf-8-sig", errors="replace")
    return ""


def asset_inventory(archive: ZipFile, namespace: str) -> dict[str, object]:
    """가이드·발전 과제·사용자 표시 JSON 후보를 센다."""
    names = archive.namelist()
    guide_tokens = ("patchouli", "guide", "book", "manual")
    guides = sorted(
        name
        for name in names
        if name.lower().endswith((".json", ".md"))
        and any(token in name.lower() for token in guide_tokens)
        and (f"/{namespace}/" in name or name.startswith(f"assets/{namespace}/"))
    )
    advancements = sorted(
        name
        for name in names
        if name.lower().endswith(".json")
        and ("/advancement/" in name or "/advancements/" in name)
        and f"data/{namespace}/" in name
    )
    recipes = sum(
        name.lower().endswith(".json")
        and ("/recipe/" in name or "/recipes/" in name)
        and f"data/{namespace}/" in name
        for name in names
    )
    return {
        "guide_candidates": len(guides),
        "guide_examples": guides[:20],
        "advancements": len(advancements),
        "advancement_examples": advancements[:20],
        "recipes": recipes,
    }


def dependency_scan(instance: Path, modids: set[str]) -> list[dict[str, object]]:
    """모든 설치 JAR 메타데이터에서 대상 모드 의존성을 찾는다."""
    rows: list[dict[str, object]] = []
    target_prefixes = {target.jar_prefix.lower() for target in TARGETS}
    for jar in sorted((instance / "mods").glob("*.jar")):
        if any(jar.name.lower().startswith(prefix) for prefix in target_prefixes):
            continue
        try:
            with ZipFile(jar) as archive:
                metadata = read_mod_metadata(archive)
        except Exception as exc:  # pragma: no cover - 실제 손상 JAR 보고용
            rows.append({"jar": jar.name, "error": str(exc)})
            continue
        lowered = metadata.lower()
        hits = sorted(modid for modid in modids if modid.lower() in lowered)
        if hits:
            rows.append({"jar": jar.name, "dependency_mentions": hits})
    return rows


def inventory(instance: Path, family: str) -> dict[str, object]:
    """실제 설치본의 버전·네임스페이스·부가 자산을 조사한다."""
    rows: list[dict[str, object]] = []
    modids: set[str] = set()
    for target in targets_for(family):
        jar = find_jar(instance, target.jar_prefix)
        english_path, korean_path = language_paths(target.namespace)
        with ZipFile(jar) as archive:
            names = set(archive.namelist())
            english = (
                load_json_bytes(archive.read(english_path))
                if english_path in names
                else {}
            )
            korean = (
                load_json_bytes(archive.read(korean_path))
                if korean_path in names
                else {}
            )
            metadata = read_mod_metadata(archive)
            assets = asset_inventory(archive, target.namespace)
        modids.add(target.namespace)
        rows.append(
            {
                "label": target.label,
                "jar": jar.name,
                "namespace": target.namespace,
                "direct_integration": target.direct_integration,
                "language_target": target.language_target,
                "english_keys": len(english),
                "bundled_korean_keys": len(korean),
                "metadata_mentions_family": sorted(
                    modid for modid in modids if modid.lower() in metadata.lower()
                ),
                **assets,
            }
        )
    extra_scope: list[dict[str, object]] = []
    installed_jars = sorted((instance / "mods").glob("*.jar"))
    for extra in EXTRA_SCOPE.get(family, ()):
        matches = [
            path
            for path in installed_jars
            if path.name.lower().startswith(str(extra["jar_prefix"]).lower())
        ]
        extra_scope.append(
            {
                "label": extra["label"],
                "installed": bool(matches),
                "jars": [path.name for path in matches],
                "language_target": False,
            }
        )
    return {
        "family": FAMILY_LABELS[family],
        "installed": rows,
        "extra_scope": extra_scope,
        "other_dependency_mentions": dependency_scan(instance, modids),
    }


def prepare(
    instance: Path,
    family: str,
    force: bool,
    namespaces: list[str] | None = None,
) -> dict[str, object]:
    """검수된 프로젝트 산출물과 현재 JAR 한국어를 영어 원문에 맞춰 준비한다."""
    work_root = PROJECT_ROOT / "working" / family
    rows: list[dict[str, object]] = []
    targets = tuple(target for target in targets_for(family) if target.language_target)
    if namespaces:
        requested = set(namespaces)
        targets = tuple(target for target in targets if target.namespace in requested)
        missing = requested - {target.namespace for target in targets}
        if missing:
            raise ValueError("알 수 없는 네임스페이스: " + ", ".join(sorted(missing)))
    for target in targets:
        jar = find_jar(instance, target.jar_prefix)
        english_path, korean_path = language_paths(target.namespace)
        with ZipFile(jar) as archive:
            english = load_json_bytes(archive.read(english_path))
            bundled = (
                load_json_bytes(archive.read(korean_path))
                if korean_path in archive.namelist()
                else {}
            )
        project_output = OUTPUT_ASSETS / target.namespace / "lang/ko_kr.json"
        project_korean = load_json(project_output) if project_output.is_file() else {}
        target_root = work_root / target.namespace
        english_file = target_root / "en_us.json"
        korean_file = target_root / "ko_kr.json"
        source_file = target_root / "candidate_sources.json"
        if korean_file.exists() and not force:
            raise FileExistsError(
                f"기존 작업본을 덮어쓰지 않습니다. --force 필요: {korean_file}"
            )
        korean: dict[str, object] = {}
        sources: dict[str, str] = {}
        for key, value in english.items():
            candidates = (
                ("project_output_review", project_korean),
                ("bundled_ko_kr", bundled),
            )
            for source_name, candidate in candidates:
                if key not in candidate:
                    continue
                candidate_value = candidate[key]
                if (
                    isinstance(value, str)
                    and candidate_value == value
                    and not is_allowed_original(value)
                ):
                    continue
                korean[key] = candidate_value
                sources[key] = source_name
                break
            else:
                korean[key] = value
                sources[key] = "new_translation_required"
        target_root.mkdir(parents=True, exist_ok=True)
        english_file.write_text(
            json.dumps(english, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        korean_file.write_text(
            json.dumps(korean, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        source_file.write_text(
            json.dumps(sources, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        counts = Counter(sources.values())
        rows.append(
            {
                "label": target.label,
                "jar": jar.name,
                "namespace": target.namespace,
                "english_keys": len(english),
                **dict(sorted(counts.items())),
            }
        )
    work_root.mkdir(parents=True, exist_ok=True)
    scope_path = work_root / "scope.json"
    if namespaces and scope_path.is_file():
        previous = load_json(scope_path)
        candidates = {
            row["namespace"]: row for row in previous.get("language_candidates", [])
        }
        candidates.update({row["namespace"]: row for row in rows})
        rows = [
            candidates[target.namespace]
            for target in targets_for(family)
            if target.language_target
            if target.namespace in candidates
        ]
    report = {**inventory(instance, family), "language_candidates": rows}
    scope_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def quest_candidate_is_translation(source: object, candidate: object) -> bool:
    """퀘스트 후보가 영어 원문을 그대로 둔 값이 아닌지 판정한다."""
    if type(source) is not type(candidate):
        return False
    if isinstance(source, list) and len(source) != len(candidate):
        return False
    if quest_snbt.validate_value("candidate", source, candidate):
        return False
    source_text = quest_snbt.flatten(source)
    candidate_text = quest_snbt.flatten(candidate)
    return source_text != candidate_text or is_allowed_original(source_text)


def write_quest_candidates(
    root: Path,
    english: dict[str, object],
    bundled: dict[str, object],
    project: dict[str, object],
    force: bool,
) -> dict[str, object]:
    """퀘스트 영어·한국어 후보·출처 파일을 쓴다."""
    korean_file = root / "ko_kr.json"
    if korean_file.exists() and not force:
        raise FileExistsError(f"기존 퀘스트 작업본을 덮어쓰지 않습니다: {korean_file}")
    korean: dict[str, object] = {}
    sources: dict[str, str] = {}
    for key, value in english.items():
        for source_name, candidate in (
            ("project_output_review", project),
            ("installed_ko_kr_candidate", bundled),
        ):
            if key in candidate and quest_candidate_is_translation(
                value, candidate[key]
            ):
                korean[key] = candidate[key]
                sources[key] = source_name
                break
        else:
            korean[key] = value
            sources[key] = "new_translation_required"
    root.mkdir(parents=True, exist_ok=True)
    for name, value in (
        ("en_us.json", english),
        ("ko_kr.json", korean),
        ("candidate_sources.json", sources),
    ):
        (root / name).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return {
        "display_keys": len(english),
        **dict(sorted(Counter(sources.values()).items())),
    }


def related_quest_keys(instance: Path, family: str) -> dict[str, object]:
    """전용 챕터 밖에서 대상 네임스페이스를 쓰는 퀘스트 표시 키를 모은다."""
    namespaces = {target.namespace for target in targets_for(family)}
    dedicated = set(QUEST_CHAPTERS[family])
    chapters, _ = quest_audit.parse_chapters(instance / "config/ftbquests/quests")
    lang_root = instance / "config/ftbquests/quests/lang/en_us/chapters"
    related: dict[str, object] = {}
    for chapter in chapters:
        chapter_name = Path(chapter["filename"]).stem
        if chapter_name in dedicated:
            continue
        task_ids: set[str] = set()
        quest_ids: set[str] = set()
        for quest in chapter["quests"]:
            matched_tasks = {
                task["id"]
                for task in quest["tasks"]
                if task["item_id"].partition(":")[0] in namespaces
            }
            if matched_tasks:
                task_ids.update(matched_tasks)
                quest_ids.add(quest["id"])
        language_file = lang_root / f"{chapter_name}.snbt_merged"
        if not language_file.is_file():
            continue
        language = quest_snbt.parse_language_snbt(language_file)
        for key, value in language.items():
            if any(
                key.startswith(f"quest.{object_id}.") for object_id in quest_ids
            ) or any(key.startswith(f"task.{object_id}.") for object_id in task_ids):
                related[key] = value
            elif (
                family == "mekanism" and "mekanism" in quest_snbt.flatten(value).lower()
            ):
                related[key] = value
            elif any(
                marker in quest_snbt.flatten(value).lower()
                for marker in QUEST_TEXT_MARKERS.get(family, ())
            ):
                related[key] = value
    return related


def prepare_quests(instance: Path, family: str, force: bool) -> dict[str, object]:
    """전용·관련 FTB Quests 표시 문구 작업본을 준비한다."""
    lang_root = instance / "config/ftbquests/quests/lang"
    project = (
        quest_snbt.parse_language_snbt(QUEST_OUTPUT) if QUEST_OUTPUT.is_file() else {}
    )
    rows: dict[str, object] = {}
    for chapter in QUEST_CHAPTERS[family]:
        english = quest_snbt.parse_language_snbt(
            lang_root / f"en_us/chapters/{chapter}.snbt_merged"
        )
        bundled_path = lang_root / f"ko_kr/chapters/{chapter}.snbt_merged"
        bundled = (
            quest_snbt.parse_language_snbt(bundled_path)
            if bundled_path.is_file()
            else {}
        )
        rows[chapter] = write_quest_candidates(
            PROJECT_ROOT / "working" / family / "quests" / chapter,
            english,
            bundled,
            project,
            force,
        )
    related = related_quest_keys(instance, family)
    installed_full = quest_snbt.parse_language_snbt(lang_root / "ko_kr.snbt")
    rows["related"] = write_quest_candidates(
        PROJECT_ROOT / "working" / family / "quests/related",
        related,
        installed_full,
        project,
        force,
    )
    report = {"family": FAMILY_LABELS[family], "chapters": rows}
    path = PROJECT_ROOT / "working" / family / "quest_scope.json"
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def redundant_item_task_title_keys(instance: Path, family: str) -> set[str]:
    """대상 범위의 단일 ItemTask 중 중복 제목 키를 반환한다."""
    english_keys: set[str] = set()
    for root in sorted((PROJECT_ROOT / "working" / family / "quests").glob("*")):
        english_file = root / "en_us.json"
        if english_file.is_file():
            english_keys.update(load_json(english_file))
    chapters, _ = quest_audit.parse_chapters(instance / "config/ftbquests/quests")
    namespaces = {target.namespace for target in targets_for(family)}
    dedicated_names = set(QUEST_CHAPTERS[family])
    scoped_quests = []
    for chapter in chapters:
        if Path(chapter["filename"]).stem in dedicated_names:
            scoped_quests.extend(chapter["quests"])
        elif not dedicated_names:
            scoped_quests.extend(
                quest
                for quest in chapter["quests"]
                if any(
                    task["item_id"].partition(":")[0] in namespaces
                    for task in quest["tasks"]
                )
            )
    keys: set[str] = set()
    for quest in scoped_quests:
        for task in quest["tasks"]:
            if (
                task["type"] == "item"
                and task["item_id"] != "ftbfiltersystem:smart_filter"
                and f"task.{task['id']}.title" in english_keys
            ):
                keys.add(f"task.{task['id']}.title")
    return keys


def remove_language_keys(text: str, keys: set[str]) -> str:
    """SNBT 언어 객체에서 지정한 최상위 키를 제거한다."""
    matches = list(quest_snbt.ENTRY_RE.finditer(text))
    replacements: list[tuple[int, int]] = []
    for index, match in enumerate(matches):
        if match.group(1) not in keys:
            continue
        end = (
            matches[index + 1].start() if index + 1 < len(matches) else text.rfind("}")
        )
        replacements.append((match.start(), end))
    for start, end in reversed(replacements):
        text = text[:start] + text[end:]
    return text


def build_quests(instance: Path, family: str) -> dict[str, object]:
    """검수한 퀘스트 번역을 누적 ko_kr.snbt에 병합한다."""
    redundant_keys = redundant_item_task_title_keys(instance, family)
    combined: dict[str, object] = {}
    for root in sorted((PROJECT_ROOT / "working" / family / "quests").glob("*")):
        korean_file = root / "ko_kr.json"
        if korean_file.is_file():
            combined.update(
                {
                    key: value
                    for key, value in load_json(korean_file).items()
                    if key not in redundant_keys
                }
            )
    if family == "modern_industrialization":
        combined.update(MODERN_INDUSTRIALIZATION_QUEST_FALLBACK_TITLES)
    if family == "industrial_foregoing":
        combined.update(INDUSTRIAL_FOREGOING_QUEST_FALLBACK_TITLES)
    installed_base = instance / "config/ftbquests/quests/lang/ko_kr.snbt"
    base = QUEST_OUTPUT if QUEST_OUTPUT.is_file() else installed_base
    restored: dict[str, object] = {}
    if QUEST_OUTPUT.is_file():
        installed = quest_snbt.parse_language_snbt(installed_base)
        current = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
        restored = {
            key: value for key, value in installed.items() if key not in current
        }
    merged = quest_snbt.merge_into_full_snbt(base, {**restored, **combined})
    merged = remove_language_keys(merged, redundant_keys)
    QUEST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    reparsed = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    if any(reparsed.get(key) != value for key, value in combined.items()):
        raise ValueError("퀘스트 누적 병합 결과가 작업본과 다릅니다.")
    remaining_redundant = sorted(redundant_keys & set(reparsed))
    if remaining_redundant:
        raise ValueError(f"중복 단일 ItemTask 제목 제거 실패: {remaining_redundant}")
    structure_overrides: list[str] = []
    if family == "mekanism":
        source = instance / "config/ftbquests/quests/chapters/mekanism.snbt"
        text = source.read_text(encoding="utf-8-sig")
        for english_name, (korean_name, expected) in MEKANISM_CUSTOM_NAMES.items():
            english_needle = f'\\"{english_name}\\"'
            english_count = text.count(english_needle)
            if english_count not in {0, expected}:
                raise ValueError(
                    f"Smart Filter 이름 개수 불일치: {english_name}="
                    f"{english_count} (예상 {expected})"
                )
            text = text.replace(english_needle, f'\\"{korean_name}\\"')
        for korean_name in {value[0] for value in MEKANISM_CUSTOM_NAMES.values()}:
            expected = sum(
                count
                for name, count in MEKANISM_CUSTOM_NAMES.values()
                if name == korean_name
            )
            actual = text.count(f'\\"{korean_name}\\"')
            if actual != expected:
                raise ValueError(
                    f"Smart Filter 번역 이름 개수 불일치: {korean_name}="
                    f"{actual} (예상 {expected})"
                )
        destination = QUEST_CHAPTER_OUTPUT / "mekanism.snbt"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        structure_overrides.append(str(destination.relative_to(PROJECT_ROOT)))
    if family == "early_midgame_infrastructure":
        source = instance / "config/ftbquests/quests/chapters/generators.snbt"
        text = source.read_text(encoding="utf-8-sig")
        for english_name, (
            korean_name,
            expected,
        ) in EARLY_INFRASTRUCTURE_CUSTOM_NAMES.items():
            english_needle = f'\\"{english_name}\\"'
            english_count = text.count(english_needle)
            if english_count not in {0, expected}:
                raise ValueError(
                    f"퀘스트 사용자 지정 이름 개수 불일치: {english_name}="
                    f"{english_count} (예상 {expected})"
                )
            text = text.replace(english_needle, f'\\"{korean_name}\\"')
        destination = QUEST_CHAPTER_OUTPUT / "generators.snbt"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        structure_overrides.append(str(destination.relative_to(PROJECT_ROOT)))
    if family == "modern_industrialization":
        source_root = instance / "config/ftbquests/quests/chapters"
        source_texts: dict[str, str] = {}
        for chapter in ("mi_digital", "mi_electric"):
            source = source_root / f"{chapter}.snbt"
            source_texts[chapter] = source.read_text(encoding="utf-8-sig")
        for english_name, (
            korean_name,
            expected,
        ) in MODERN_INDUSTRIALIZATION_CUSTOM_NAMES.items():
            english_needle = f'\\"{english_name}\\"'
            korean_needle = f'\\"{korean_name}\\"'
            english_count = sum(
                text.count(english_needle) for text in source_texts.values()
            )
            korean_count = sum(
                text.count(korean_needle) for text in source_texts.values()
            )
            if (english_count, korean_count) not in {(expected, 0), (0, expected)}:
                raise ValueError(
                    "Modern Industrialization 사용자 지정 이름 개수 불일치: "
                    f"{english_name}=영어 {english_count}, 한국어 {korean_count} "
                    f"(예상 {expected})"
                )
            for chapter, text in source_texts.items():
                source_texts[chapter] = text.replace(english_needle, korean_needle)
        for chapter, text in source_texts.items():
            destination = QUEST_CHAPTER_OUTPUT / f"{chapter}.snbt"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(text, encoding="utf-8")
            structure_overrides.append(str(destination.relative_to(PROJECT_ROOT)))
    return {
        "family": FAMILY_LABELS[family],
        "merged_keys": len(combined),
        "removed_redundant_item_task_titles": len(redundant_keys),
        "structure_overrides": structure_overrides,
    }


def verify_quests(instance: Path, family: str) -> tuple[dict[str, object], list[str]]:
    """전용·관련 퀘스트와 fallback 표시 경로를 검증한다."""
    errors: list[str] = []
    output = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    redundant_keys = redundant_item_task_title_keys(instance, family)
    display_keys = 0
    english_display: dict[str, object] = {}
    for root in sorted((PROJECT_ROOT / "working" / family / "quests").glob("*")):
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        if not english_file.is_file() or not korean_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        english_display.update(english)
        display_keys += len(english)
        if list(english) != list(korean):
            errors.append(f"퀘스트 키 또는 순서 불일치: {root.name}")
            continue
        for key, source in english.items():
            target = korean[key]
            validation_source = source
            for source_text, target_text in QUEST_VALIDATION_TEXT_EQUIVALENTS.get(
                key,
                (),
            ):
                if isinstance(validation_source, str):
                    validation_source = validation_source.replace(
                        source_text,
                        target_text,
                    )
                else:
                    validation_source = [
                        paragraph.replace(source_text, target_text)
                        for paragraph in validation_source
                    ]
            errors.extend(
                quest_snbt.validate_value(
                    key,
                    validation_source,
                    target,
                )
            )
            if key in redundant_keys:
                if key in output:
                    errors.append(f"중복 단일 ItemTask 제목이 출력에 남음: {key}")
                continue
            if output.get(key) != target:
                errors.append(f"퀘스트 누적 출력 불일치: {key}")
            source_text = quest_snbt.flatten(source)
            target_text = quest_snbt.flatten(target)
            if source_text == target_text and not is_allowed_original(
                quest_audit.strip_formatting(source_text)
            ):
                errors.append(f"분류되지 않은 퀘스트 영어 유지: {key}")
            expected_title = MEKANISM_QUEST_ITEM_TITLES.get(key)
            if (
                expected_title
                and quest_audit.strip_formatting(target_text) != expected_title
            ):
                errors.append(
                    f"퀘스트 제목과 아이템명 불일치: {key}="
                    f"{quest_audit.strip_formatting(target_text)!r}, 예상={expected_title!r}"
                )
    chapters, _ = quest_audit.parse_chapters(instance / "config/ftbquests/quests")
    dedicated = [
        chapter
        for chapter in chapters
        if Path(chapter["filename"]).stem in QUEST_CHAPTERS[family]
    ]
    if not QUEST_CHAPTERS[family]:
        namespaces = {target.namespace for target in targets_for(family)}
        dedicated = [
            {
                **chapter,
                "quests": [
                    quest
                    for quest in chapter["quests"]
                    if any(
                        task["item_id"].partition(":")[0] in namespaces
                        for task in quest["tasks"]
                    )
                ],
            }
            for chapter in chapters
        ]
        dedicated = [chapter for chapter in dedicated if chapter["quests"]]
    custom_names = [
        task
        for chapter in dedicated
        for quest in chapter["quests"]
        for task in quest["tasks"]
        if task["custom_name"] and LATIN_WORD.search(task["custom_name"])
    ]
    tasks = [
        task
        for chapter in dedicated
        for quest in chapter["quests"]
        for task in quest["tasks"]
    ]
    explicit_task_titles = [
        task for task in tasks if f"task.{task['id']}.title" in english_display
    ]
    redundant_single_item_titles = [
        task
        for task in explicit_task_titles
        if task["type"] == "item" and task["item_id"] != "ftbfiltersystem:smart_filter"
    ]
    unremoved_titles = [
        task
        for task in redundant_single_item_titles
        if f"task.{task['id']}.title" in output
    ]
    if unremoved_titles:
        errors.append(
            "중복 단일 ItemTask 제목이 남아 있습니다: "
            + ", ".join(task["id"] for task in unremoved_titles)
        )
    first_task_fallbacks = [
        quest
        for chapter in dedicated
        for quest in chapter["quests"]
        if f"quest.{quest['id']}.title" not in english_display
    ]
    for quest in first_task_fallbacks:
        quest_title_key = f"quest.{quest['id']}.title"
        if quest_title_key in output:
            title_text = quest_snbt.flatten(output[quest_title_key])
            if LATIN_WORD.search(quest_audit.strip_formatting(title_text)) and not (
                is_allowed_original(title_text)
            ):
                errors.append(
                    "분류되지 않은 명시적 퀘스트 fallback 제목: "
                    f"{quest['id']}={title_text}"
                )
            continue
        if not quest["tasks"]:
            errors.append(f"제목과 Task가 모두 없는 퀘스트: {quest['id']}")
            continue
        first_task = quest["tasks"][0]
        task_title_key = f"task.{first_task['id']}.title"
        if task_title_key in english_display:
            continue
        item_id = first_task["item_id"]
        if first_task["type"] != "item" or ":" not in item_id:
            errors.append(f"번역 경로를 확인할 수 없는 퀘스트 fallback: {quest['id']}")
            continue
        namespace, item_path = item_id.split(":", 1)
        language_path = OUTPUT_ASSETS / namespace / "lang" / "ko_kr.json"
        language = load_json(language_path) if language_path.is_file() else {}
        item_keys = (
            f"item.{namespace}.{item_path}",
            f"block.{namespace}.{item_path}",
            f"{namespace}.glyph_name.{item_path}",
        )
        if not any(key in language for key in item_keys):
            errors.append(
                f"아이템 이름이 없는 퀘스트 fallback: {quest['id']}={item_id}"
            )
    unresolved_custom_names = custom_names
    if family == "mekanism" and custom_names:
        structure_path = QUEST_CHAPTER_OUTPUT / "mekanism.snbt"
        if not structure_path.is_file():
            errors.append("Mekanism Smart Filter 구조 오버라이드 누락")
        else:
            structure_text = structure_path.read_text(encoding="utf-8")
            remaining = [
                name
                for name in MEKANISM_CUSTOM_NAMES
                if f'\\"{name}\\"' in structure_text
            ]
            expected_korean = sum(
                expected for _, expected in MEKANISM_CUSTOM_NAMES.values()
            )
            actual_korean = sum(
                structure_text.count(f'\\"{name}\\"')
                for name in {value[0] for value in MEKANISM_CUSTOM_NAMES.values()}
            )
            if remaining or actual_korean != expected_korean:
                errors.append(
                    "Smart Filter 구조 오버라이드 검증 실패: "
                    f"영어={remaining}, 한국어={actual_korean}/{expected_korean}"
                )
            else:
                unresolved_custom_names = []
    if family == "early_midgame_infrastructure" and custom_names:
        structure_path = QUEST_CHAPTER_OUTPUT / "generators.snbt"
        if not structure_path.is_file():
            errors.append("초중반 기반 시설 퀘스트 구조 오버라이드 누락")
        else:
            structure_text = structure_path.read_text(encoding="utf-8")
            remaining = [
                name
                for name in EARLY_INFRASTRUCTURE_CUSTOM_NAMES
                if f'\\"{name}\\"' in structure_text
            ]
            expected_korean = sum(
                expected for _, expected in EARLY_INFRASTRUCTURE_CUSTOM_NAMES.values()
            )
            actual_korean = sum(
                structure_text.count(f'\\"{name}\\"')
                for name in {
                    value[0] for value in EARLY_INFRASTRUCTURE_CUSTOM_NAMES.values()
                }
            )
            if remaining or actual_korean != expected_korean:
                errors.append(
                    "초중반 기반 시설 사용자 지정 이름 검증 실패: "
                    f"영어={remaining}, 한국어={actual_korean}/{expected_korean}"
                )
            else:
                unresolved_custom_names = []
    if family == "modern_industrialization" and custom_names:
        structure_paths = [
            QUEST_CHAPTER_OUTPUT / f"{chapter}.snbt"
            for chapter in ("mi_digital", "mi_electric")
        ]
        missing_paths = [path for path in structure_paths if not path.is_file()]
        if missing_paths:
            errors.append(
                "Modern Industrialization 퀘스트 구조 오버라이드 누락: "
                + ", ".join(path.name for path in missing_paths)
            )
        else:
            structure_text = "\n".join(
                path.read_text(encoding="utf-8") for path in structure_paths
            )
            remaining = [
                name
                for name in MODERN_INDUSTRIALIZATION_CUSTOM_NAMES
                if f'\\"{name}\\"' in structure_text
            ]
            expected_korean = sum(
                expected
                for _, expected in MODERN_INDUSTRIALIZATION_CUSTOM_NAMES.values()
            )
            actual_korean = sum(
                structure_text.count(f'\\"{name}\\"')
                for name in {
                    value[0] for value in MODERN_INDUSTRIALIZATION_CUSTOM_NAMES.values()
                }
            )
            if remaining or actual_korean != expected_korean:
                errors.append(
                    "Modern Industrialization 사용자 지정 이름 검증 실패: "
                    f"영어={remaining}, 한국어={actual_korean}/{expected_korean}"
                )
            else:
                unresolved_custom_names = []
    report = {
        "chapters": [chapter["filename"] for chapter in dedicated],
        "quests_checked": sum(len(chapter["quests"]) for chapter in dedicated),
        "tasks_checked": sum(
            len(quest["tasks"]) for chapter in dedicated for quest in chapter["quests"]
        ),
        "display_keys_checked": display_keys,
        "source_english_custom_names": len(custom_names),
        "unresolved_english_custom_names": len(unresolved_custom_names),
        "explicit_task_titles": len(explicit_task_titles),
        "source_redundant_single_item_task_titles": len(redundant_single_item_titles),
        "remaining_redundant_single_item_task_titles": len(unremoved_titles),
        "first_task_quest_fallbacks": len(first_task_fallbacks),
        "fallback_paths_checked": [
            "chapter/group title",
            "quest title/subtitle/description",
            "task title",
            "item hover name",
            "custom_name/literal component",
            "first-task quest fallback",
        ],
    }
    return report, errors


def normalize_mekanism_value(key: str, english: str, korean: str) -> str:
    """Mekanism 계열의 확정 용어와 반복 패턴을 적용한다."""
    if key in MEKANISM_KEY_OVERRIDES:
        return MEKANISM_KEY_OVERRIDES[key]
    if english in MEKANISM_EXACT:
        return MEKANISM_EXACT[english]
    factory = re.fullmatch(
        r"(Basic|Advanced|Elite|Ultimate|Overclocked|Quantum|Dense|Multiversal|Creative) "
        r"(Pigment Extracting|Painting) Factory",
        english,
    )
    if factory:
        process = "안료 추출" if factory.group(2) == "Pigment Extracting" else "염색"
        return f"{TIER_KO[factory.group(1)]} {process} 시스템"
    storage = re.fullmatch(r"(Basic|Advanced|Elite|Ultimate) Storage", english)
    if storage:
        return f"{TIER_KO[storage.group(1)]} 저장소"
    rate = re.fullmatch(r"(Basic|Advanced|Elite|Ultimate) Output Rate", english)
    if rate:
        return f"{TIER_KO[rate.group(1)]} 출력 속도"
    tank_tooltip = re.fullmatch(
        r"(Storage size|Output rate) of (Basic|Advanced|Elite|Ultimate) "
        r"(max|mid) chemical tanks in mb\.",
        english,
    )
    if tank_tooltip:
        label = "저장 용량" if tank_tooltip.group(1) == "Storage size" else "출력 속도"
        size = "최대" if tank_tooltip.group(3) == "max" else "중간"
        return f"{TIER_KO[tank_tooltip.group(2)]} {size} 화학 물질 탱크의 {label}(mB)입니다."
    rs_item = re.fullmatch(
        r"(64B|256B|1024B|8192B) Chemical Storage (Part|Disk|Block)", english
    )
    if rs_item:
        kind = {"Part": "부품", "Disk": "디스크", "Block": "블록"}[rs_item.group(2)]
        return f"{rs_item.group(1)} 화학 물질 저장 {kind}"
    rs_creative = re.fullmatch(r"Creative Chemical Storage (Disk|Block)", english)
    if rs_creative:
        kind = "디스크" if rs_creative.group(1) == "Disk" else "블록"
        return f"크리에이티브 화학 물질 저장 {kind}"
    rs_energy = re.fullmatch(r"(64B|256B|1024B|8192B|Creative) energy usage", english)
    if rs_energy:
        tier = (
            "크리에이티브" if rs_energy.group(1) == "Creative" else rs_energy.group(1)
        )
        return f"{tier} 에너지 사용량"
    rs_energy_tooltip = re.fullmatch(
        r"The energy used by the (64B|256B|1024B|8192B|Creative) "
        r"Chemical Storage Block\.",
        english,
    )
    if rs_energy_tooltip:
        tier = (
            "크리에이티브"
            if rs_energy_tooltip.group(1) == "Creative"
            else rs_energy_tooltip.group(1)
        )
        return f"{tier} 화학 물질 저장 블록이 사용하는 에너지입니다."
    replacements = (
        ("정제된 저장소", "Refined Storage"),
        ("메카니즘", "Mekanism"),
        ("메커니즘", "Mekanism"),
        ("메카슈츠", "메카슈트"),
        ("메카수트", "메카슈트"),
        ("MekaSuits", "메카슈트"),
        ("MekaSuit", "메카슈트"),
        ("Meka-Tool", "메카툴"),
        ("메카-툴", "메카툴"),
        ("메카 도구", "메카툴"),
        ("수정 스테이션", "모듈 제어기"),
        ("개조 스테이션", "모듈 제어기"),
        ("동위 원소 원심 분리기", "동위원소 원심분리기"),
        ("동위 원소 원심분리기", "동위원소 원심분리기"),
        ("태양중성자활성기", "태양열 중성자 활성기"),
        ("태양 중성자 활성제", "태양열 중성자 활성기"),
        ("태양 중성자 활성기", "태양열 중성자 활성기"),
        ("화학화학 물질", "화학 물질"),
        ("화학품", "화학 물질"),
        ("방탄복", "흉갑"),
        ("보디아머", "흉갑"),
        ("펠렛", "펠릿"),
        ("메카슈트 바지", "메카슈트 각반"),
        ("핵 폐기물", "핵폐기물"),
        ("레시피", "조합법"),
        ("조합법를", "조합법을"),
        ("방식가 있습니다", "방식이 있습니다"),
        ("&d농축&f을 얻을 수 있습니다", "&d농축&f할 수 있습니다"),
        ("&d&e아이템&r을 강화하여", "&d&e아이템&r을 농축하여"),
        ("오비시디언", "흑요석"),
        ("&b유체&f또는", "&b유체&f 또는"),
        (
            "&c화학 물질&r의 버킷을 몇 개나 담을 수 있습니까? 그것은 크기에 중요합니다.",
            "&c화학 물질&r을 몇 버킷이나 담을지는 구조 크기에 따라 달라집니다.",
        ),
        (
            "&5흑요석 가루 &f4개와 &8심층암&f를 만들 수도 있습니다. &5흑요석&r!",
            "&5흑요석 가루 &f4개와 &8심층암&f으로 &5흑요석&r을 만들 수도 있습니다!",
        ),
        ("인챈트", "마법 부여"),
        ("스탯", "능력치"),
        ("얼티밋티어", "궁극 등급"),
        ("어드밴스드 티어", "고급 등급"),
        ("얼티밋 티어", "궁극 등급"),
        ("엘리트 티어", "엘리트 등급"),
        ("고급 티어", "고급 등급"),
        ("기본티어", "기본 등급"),
        ("티어", "등급"),
        ("계층", "등급"),
        ("궁극 단계", "궁극 등급"),
        ("궁극등급", "궁극 등급"),
        ("리액터", "반응기"),
        ("사용후핵폐기물", "사용한 핵폐기물"),
        ("홀라움", "홀로륨"),
        ("구성자", "설정 장치"),
        ("증기를 여기저기에 적용해", "증기를 구조 전체에 흐르게"),
        (
            "&3플루토늄 펠릿&r 1개와 1,000mB &8사용한 핵폐기물&r.",
            "&3플루토늄 펠릿&r 1개와 1,000mB &8사용한 핵폐기물&r을 얻습니다.",
        ),
        ("2 조합법에만", "조합법 2개에만"),
        ("그중 1가지는", "그중 1개는"),
        ("버튼 2개이 있습니다", "버튼 2개가 있습니다"),
        ("250% 피해를 입으면", "손상도가 250%에 도달하면"),
        (
            "&d포트&r를 통해 &d과급 코일&r에 &a에너지&r",
            "&d포트&r를 통해 &d과급 코일에 &a에너지&r",
        ),
        ("&2FRLA&r 하나를 배치하고", "&2FRLA&r 1개를 배치하고"),
        ("금속 주입기", "금속공학 주입기"),
        ("야금 주입기", "금속공학 주입기"),
        ("농축실", "농축기"),
        ("강화실", "농축기"),
        ("정제실", "정화기"),
        ("화학 물질 주입실", "화학 주입실"),
        ("전해분리기", "전해 분리기"),
        ("화학 산화기", "화학적 산화 장치"),
        ("화학 세척기", "화학적 세척 장치"),
        ("화학 세탁기", "화학적 세척 장치"),
        ("화학 결정화기", "화학적 결정화 장치"),
        ("Mekanism 결정화기", "Mekanism 화학적 결정화 장치"),
        ("가압 반응 챔버", "가압 반응 장치"),
        ("화학제품", "화학 물질"),
        ("더티", "오염된"),
        ("먼지", "가루"),
        ("크리스탈", "결정"),
        ("샤드", "조각"),
        ("클럼프", "덩어리"),
        ("다이아몬드 더스트", "다이아몬드 가루"),
        ("풍부한", "농축"),
        ("강화된 다이아몬드", "농축 다이아몬드"),
        ("염수", "소금물"),
        ("기계을", "기계를"),
        ("개을", "개를"),
        ("능력치을", "능력치를"),
        ("화학 물질 &e산화제", "화학적 &e산화 장치"),
        ("화학 물질 &e산화기", "화학적 &e산화 장치"),
        ("화학물질", "화학 물질"),
        ("약품", "화학 물질"),
        ("케미컬", "화학 물질"),
        ("데미지", "피해"),
        ("대미지", "피해"),
        ("멀티블럭", "멀티블록"),
        ("반양자성", "반양성자"),
        ("페인팅", "염색"),
        ("회화", "염색"),
        ("팩토리", "시스템"),
        ("스토리지", "저장소"),
        ("창의적인", "크리에이티브"),
        ("창조적", "크리에이티브"),
        ("창의", "크리에이티브"),
        ("첨단", "고급"),
        ("기초", "기본"),
        ("궁극적인", "궁극"),
        ("궁극적", "궁극"),
        ("항목", "아이템"),
        ("물류 운송업자", "물류 수송기"),
        ("동적 탱크", "다이나믹 탱크"),
        ("기계장치", "기계"),
        ("머신", "기계"),
        ("강괴", "강철 주괴"),
        ("케이싱 글래스", "케이싱 유리"),
        ("업그레이드 제거", "업그레이드 회수"),
        ("절삭유", "냉각재"),
        ("AllTheMods Staff", "AllTheMods 운영진"),
        ("All Rights Reserved", "모든 권리 보유"),
        ("AllTheMods Team", "AllTheMods 팀"),
        ("(MB)", "(mB)"),
        ("(mb)", "(mB)"),
    )
    for old, new in replacements:
        korean = korean.replace(old, new)
    for old, new in MEKANISM_QUEST_WORDS.items():
        pattern = (
            rf"(^|\\n|[^A-Za-z]|[&§][0-9A-FK-ORa-fk-or])"
            rf"{re.escape(old)}(?![A-Za-z])"
        )
        korean = re.sub(pattern, lambda match: match.group(1) + new, korean)
    korean = re.sub(r"단계 ([1-9])", r"\1단계", korean)
    korean = korean.replace("Tier ", "단계 ")
    return korean


def apply_title_name(value: str, name: str) -> str:
    """제목의 서식 코드 개수를 보존하면서 표시 이름을 확정명으로 맞춘다."""
    codes = FORMAT_CODE.findall(value)
    prefix = "".join(code for code in codes if code.lower() not in {"&r", "§r"})
    suffix = "".join(code for code in codes if code.lower() in {"&r", "§r"})
    return prefix + name + suffix


BOTANY_FIXED_TRANSLATIONS = {
    "container.botanypots.botany_pot": "식물 화분",
    "itemGroup.botanypots.tab": "Botany Pots",
    "gui.jei.category.botanypots.crop": "작물",
    "gui.jei.category.botanypots.interaction": "화분 상호작용",
    "tooltip.botanypots.growth_time": "성장 시간: %s",
    "tooltip.botanypots.wrong_soil": "%s에는 심을 수 없습니다",
    "tooltip.botanypots.growth_modifier": "%s 성장 속도",
    "tooltip.botanypots.yield_modifier": "%s 생산량",
    "tooltip.botanypots.loot.chance": "확률: %s",
    "tooltip.botanypots.base_rate": "성장 시간: %s",
    "tooltip.botanypots.crop_id": "작물 ID: %s",
    "tooltip.botanypots.soil_id": "토양 ID: %s",
    "tooltip.botanypots.wrong_pot": "%d에서는 자랄 수 없습니다.",
    "tooltip.botanypots.percent": "x%d%%",
    "tooltip.botanypots.yield.scale": "생산량 배율: %d%%",
    "tooltip.botanypots.yield.total": "생산량: %d%%",
    "tooltip.botanypots.yield.source.base": "기본값: %d%%",
    "tooltip.botanypots.yield.source.pot": "화분: %d%%",
    "tooltip.botanypots.yield.source.soil": "토양: %d%%",
    "tooltip.botanypots.yield.source.tool": "도구: %d%%",
    "commands.botanypots.mod_message": "[§aBotany Pots§r] %s",
    "commands.botanypots.dump.no_results": "결과를 찾지 못했습니다.",
    "commands.botanypots.dump.missing_crops": (
        "잠재적으로 누락된 작물 %d개를 찾았습니다. 이 목록은 완전하지 않으며 "
        "잘못 포함되거나 누락된 항목이 있을 수 있습니다. 이 메시지를 클릭하면 "
        "목록이 클립보드에 복사됩니다."
    ),
    "commands.botanypots.dump.generated": (
        "작물 파일 %d개를 생성했습니다. 클릭하여 폴더를 엽니다."
    ),
    "commands.botanypots.dump.missing_soils": (
        "잠재적으로 누락된 토양 %d개를 찾았습니다. 이 목록은 완전하지 않으며 "
        "잘못 포함되거나 누락된 항목이 있을 수 있습니다. 이 메시지를 클릭하면 "
        "목록이 클립보드에 복사됩니다."
    ),
    "commands.botanypots.debug.crop_errors": (
        "작물 %d개를 검사했으며 오류 %d개를 찾았습니다! 자세한 내용은 로그에 "
        "기록되었습니다."
    ),
    "commands.botanypots.debug.crop_success": (
        "작물 %d개를 검사했으며 오류가 없습니다!"
    ),
    "attribute.botanypots.growth": "식물 화분 성장",
    "attribute.botanypots.yield": "식물 화분 생산량",
    "enchantment.botanypots.idle_hands": "게으른 손의 저주",
    "enchantment.botanypots.idle_hands.desc": (
        "플레이어가 사용하면 아이템이 사실상 쓸모없어집니다. 식물 화분에서 "
        "사용하면 내구도 소모를 무효화합니다."
    ),
    "tag.item.botanypots.soil.mushroom": "버섯용 토양",
    "tag.item.botanypots.soil.snow": "눈 덮인 토양",
    "tag.item.botanypots.soil.jungle_log": "정글나무 토양",
    "tag.item.botanypots.soil.water": "물 토양",
    "tag.item.botanypots.botany_pots": "모든 식물 화분",
    "tag.item.botanypots.soil.moss": "이끼 낀 토양",
    "tag.item.botanypots.soil.end": "엔드 토양",
    "tag.item.botanypots.soil.nether": "네더 토양",
    "tag.item.botanypots.soil.soul_sand": "영혼 토양",
    "tag.item.botanypots.soil.sand": "모래 토양",
    "tag.item.botanypots.soil.dirt": "흙 토양",
    "tag.item.botanypots.harvest_items": "사용 가능한 수확 도구",
    "tag.item.botanypots.soil.lava": "용암 토양",
    "tag.item.botanypots.crop_generator_ignores": "제외된 작물 후보",
    "tag.item.botanypots.soil_generator_ignores": "제외된 토양 후보",
    "tag.enchantment.botanypots.negate_harvest_damage": "수확 내구도 소모 무효화",
    "tag.enchantment.botanypots.increase_pot_growth": "성장 속도 증가",
    "tag.block.botanypots.botany_pots": "모든 식물 화분",
}

BOTANY_COLORS = {
    "white": "하얀색",
    "orange": "주황색",
    "magenta": "자홍색",
    "light_blue": "하늘색",
    "yellow": "노란색",
    "lime": "연두색",
    "pink": "분홍색",
    "gray": "회색",
    "light_gray": "회백색",
    "cyan": "청록색",
    "purple": "보라색",
    "blue": "파란색",
    "brown": "갈색",
    "green": "초록색",
    "red": "빨간색",
    "black": "검은색",
}

BOTANY_BRICK_MATERIALS = {
    "bricks": "벽돌",
    "stone_bricks": "석재 벽돌",
    "mossy_stone_bricks": "이끼 낀 석재 벽돌",
    "deepslate_bricks": "심층암 벽돌",
    "tuff_bricks": "응회암 벽돌",
    "mud_bricks": "진흙 벽돌",
    "prismarine_bricks": "프리즈머린 벽돌",
    "nether_bricks": "네더 벽돌",
    "red_nether_bricks": "붉은 네더 벽돌",
    "polished_blackstone_bricks": "윤나는 흑암 벽돌",
    "end_stone_bricks": "엔드 석재 벽돌",
    "quartz_bricks": "석영 벽돌",
}


def translate_botany_block(key: str) -> str:
    """Botany Pots 블록 이름을 검수한 공식 색상·재료 용어로 만든다."""
    prefix = "block.botanypots."
    if not key.startswith(prefix):
        raise KeyError(key)
    name = key.removeprefix(prefix)
    if name == "terracotta_botany_pot":
        return "식물 화분"
    if name == "terracotta_hopper_botany_pot":
        return "식물 호퍼 화분"
    if name == "terracotta_waxed_botany_pot":
        return "밀랍칠한 식물 화분"

    variants = (
        ("_hopper_botany_pot", "hopper"),
        ("_waxed_botany_pot", "waxed"),
        ("_botany_pot", "normal"),
    )
    for suffix, variant in variants:
        if name.endswith(suffix):
            material = name.removesuffix(suffix)
            break
    else:
        raise ValueError(f"알 수 없는 Botany Pots 블록 변형: {key}")

    descriptor = BOTANY_BRICK_MATERIALS.get(material)
    if descriptor is None:
        material_suffixes = (
            ("_glazed_terracotta", "유광 테라코타"),
            ("_terracotta", ""),
            ("_concrete", "콘크리트"),
        )
        for material_suffix, material_name in material_suffixes:
            if material.endswith(material_suffix):
                color = material.removesuffix(material_suffix)
                if color not in BOTANY_COLORS:
                    raise ValueError(f"알 수 없는 Botany Pots 색상: {key}")
                descriptor = " ".join(
                    part for part in (BOTANY_COLORS[color], material_name) if part
                )
                break
    if descriptor is None:
        raise ValueError(f"알 수 없는 Botany Pots 재료: {key}")

    if variant == "hopper":
        return f"{descriptor} 식물 호퍼 화분"
    if variant == "waxed":
        return f"밀랍칠한 {descriptor} 식물 화분"
    return f"{descriptor} 식물 화분"


def normalize_botany_pots() -> int:
    """검수한 Botany Pots 고정 문구와 블록 이름을 작업본에 반영한다."""
    root = PROJECT_ROOT / "working/botany_pots_trees/botanypots"
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    changed = 0
    for key, source in english.items():
        if key.startswith("block.botanypots."):
            translated = translate_botany_block(key)
        elif key in BOTANY_FIXED_TRANSLATIONS:
            translated = BOTANY_FIXED_TRANSLATIONS[key]
        elif key.startswith("_") and source == "":
            translated = source
        else:
            raise ValueError(f"검수되지 않은 Botany Pots 언어 키: {key}")
        if korean[key] != translated:
            korean[key] = translated
            changed += 1
    (root / "ko_kr.json").write_text(
        json.dumps(korean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return changed


def normalize(family: str) -> dict[str, object]:
    """모드군별 검수에서 확정한 반복 용어와 패턴을 작업본에 적용한다."""
    if family == "botany_pots_trees":
        return {"family": FAMILY_LABELS[family], "changed": normalize_botany_pots()}
    if family != "mekanism":
        return {"family": FAMILY_LABELS[family], "changed": 0}
    changed = 0
    for target in targets_for(family):
        if not target.language_target:
            continue
        root = PROJECT_ROOT / "working" / family / target.namespace
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        for key, source in english.items():
            if not isinstance(source, str) or not isinstance(korean[key], str):
                continue
            normalized = normalize_mekanism_value(key, source, korean[key])
            if normalized != korean[key]:
                korean[key] = normalized
                changed += 1
        (root / "ko_kr.json").write_text(
            json.dumps(korean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    quest_root = PROJECT_ROOT / "working" / family / "quests"
    for root in sorted(quest_root.glob("*")):
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        if not english_file.is_file() or not korean_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        for key, source in english.items():
            source_values = source if isinstance(source, list) else [source]
            target_values = (
                korean[key] if isinstance(korean[key], list) else [korean[key]]
            )
            if len(source_values) != len(target_values):
                continue
            normalized_values = [
                normalize_mekanism_value(key, source_text, target_text)
                if isinstance(source_text, str) and isinstance(target_text, str)
                else target_text
                for source_text, target_text in zip(
                    source_values, target_values, strict=True
                )
            ]
            for old, new in MEKANISM_QUEST_TEXT_REPLACEMENTS.get(key, ()):
                normalized_values = [
                    value.replace(old, new) for value in normalized_values
                ]
            if key in MEKANISM_QUEST_ITEM_TITLES:
                normalized_values = [
                    apply_title_name(value, MEKANISM_QUEST_ITEM_TITLES[key])
                    for value in normalized_values
                ]
            for index, value in MEKANISM_QUEST_ELEMENT_OVERRIDES.get(key, {}).items():
                normalized_values[index] = value
            normalized: object = (
                normalized_values
                if isinstance(korean[key], list)
                else normalized_values[0]
            )
            if normalized != korean[key]:
                korean[key] = normalized
                changed += 1
        korean_file.write_text(
            json.dumps(korean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return {"family": FAMILY_LABELS[family], "changed": changed}


def validate_value(key: str, source: object, target: object) -> list[str]:
    """자료형·자리표시자·줄바꿈·서식 코드를 검사한다."""
    errors: list[str] = []
    if type(source) is not type(target):
        return [f"자료형 불일치: {key}"]
    if isinstance(source, list):
        assert isinstance(target, list)
        if len(source) != len(target):
            return [f"목록 길이 불일치: {key}"]
        for index, (source_item, target_item) in enumerate(zip(source, target)):
            errors.extend(validate_value(f"{key}[{index}]", source_item, target_item))
        return errors
    if isinstance(source, dict):
        assert isinstance(target, dict)
        if source.keys() != target.keys():
            return [f"객체 키 불일치: {key}"]
        for child_key in source:
            errors.extend(
                validate_value(
                    f"{key}.{child_key}", source[child_key], target[child_key]
                )
            )
        return errors
    if not isinstance(source, str):
        return errors
    assert isinstance(target, str)
    source_placeholders = PLACEHOLDER.findall(source)
    target_placeholders = PLACEHOLDER.findall(target)
    if Counter(source_placeholders) != Counter(target_placeholders):
        errors.append(f"자리표시자 불일치: {key}")
    elif source_placeholders != target_placeholders and any(
        token.startswith("%") and re.fullmatch(r"%\d+\$[a-zA-Z]", token) is None
        for token in source_placeholders
    ):
        errors.append(f"비순번 자리표시자 순서 불일치: {key}")
    if source.count("\n") != target.count("\n"):
        errors.append(f"줄바꿈 불일치: {key}")
    if Counter(FORMAT_CODE.findall(source)) != Counter(FORMAT_CODE.findall(target)):
        errors.append(f"서식 코드 불일치: {key}")
    return errors


def validate_family_value(
    family: str, key: str, source: object, target: object
) -> list[str]:
    """모드별 표시 문법을 반영해 자료형과 보호 토큰을 검사한다."""
    if (
        family == "industrial_foregoing"
        and key.startswith("text.industrialforegoing.book.")
        and isinstance(source, str)
        and isinstance(target, str)
    ):
        source_braces = re.findall(r"\{[^{}]+\}", source)
        target_braces = re.findall(r"\{[^{}]+\}", target)
        if len(source_braces) != len(target_braces):
            return [f"설명서 강조 구문 개수 불일치: {key}"]
        source = re.sub(r"\{[^{}]+\}", "{}", source)
        target = re.sub(r"\{[^{}]+\}", "{}", target)
    return validate_value(key, source, target)


def is_allowed_original(source: str) -> bool:
    """고유명사·키·식별자처럼 의도적으로 유지 가능한 값을 판정한다."""
    stripped = source.strip()
    return (
        stripped in ALLOWED_ORIGINALS
        or re.fullmatch(r"(?:https?://|www\.)\S+", stripped) is not None
        or TRANSLATION_KEY.fullmatch(stripped) is not None
        or re.fullmatch(r"\{image:[^}]+\}", stripped) is not None
        or not LATIN_WORD.search(stripped)
        or bool(re.fullmatch(r"[A-Z0-9_+./:%×() -]+", stripped))
    )


def is_family_allowed_original(family: str, key: str, source: str) -> bool:
    """모드 고유 식별명처럼 키 문맥에서만 원문 유지가 필요한 값을 판정한다."""
    if family == "xycraft" and (
        key.startswith("itemGroup.xycraft_")
        or key == "key.category.xycraft_core.key_binds"
        or key == "unit.xycraft.xynergy"
    ):
        return True
    if family == "rftools" and (
        key.startswith("itemGroup.rftools") or key == "key.categories.rftools"
    ):
        return True
    if family == "laser_io_mffs" and key in {
        "itemGroup.laserio",
        "advancements.mffs.root.title",
    }:
        return True
    if family == "pylons" and key == "itemGroup.pylons":
        return True
    if family == "steves_carts" and key.startswith("stevescarts.creativetab."):
        return True
    if family == "draconic_evolution" and key == (
        "module.draconicevolution.undying.energy.value"
    ):
        return True
    if family == "irons_spells" and (
        key == "tooltip.irons_spellbooks.shift_tooltip"
        or key
        in {
            "material.irons_jewelry.allthemodium",
            "material.irons_jewelry.vibranium",
            "material.irons_jewelry.unobtainium",
        }
    ):
        return True
    if family == "forbidden_arcanus" and key == "itemGroup.forbidden_arcanus.main":
        return True
    if family == "natures_aura" and key in {
        "item_group.naturesaura.tab",
        "advancement.naturesaura.root",
        "command.naturesaura.aura.usage",
    }:
        return True
    if family == "actually_additions" and key in {
        "misc.actuallyadditions.energy_name",
        "misc.actuallyadditions.power_long",
        "misc.actuallyadditions.power_single",
        "misc.actuallyadditions.power_double",
        "misc.actuallyadditions.power_name_long",
        "booklet.actuallyadditions.chapter.rf",
    }:
        return True
    if family == "immersive_engineering" and (
        key.startswith("item.immersiveengineering.shader.name.")
        or key
        in {
            "desc.immersiveengineering.flavour.fluidStack",
            "gui.immersiveengineering.config.radio_tower.khz",
            "item.immersiveengineering.revolver.einhorn",
        }
    ):
        return True
    return is_allowed_original(source)


def verify_language(
    instance: Path, family: str
) -> tuple[list[dict[str, object]], list[str]]:
    """모드군 언어 파일과 누적 출력의 완전성을 검사한다."""
    rows: list[dict[str, object]] = []
    errors: list[str] = []
    for target in targets_for(family):
        if not target.language_target:
            continue
        root = PROJECT_ROOT / "working" / family / target.namespace
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        if not english_file.is_file() or not korean_file.is_file():
            errors.append(f"작업본 누락: {target.namespace}")
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        sources = load_json(root / "candidate_sources.json")
        if list(english) != list(korean):
            errors.append(f"키 또는 순서 불일치: {target.namespace}")
            continue
        raw = korean_file.read_text(encoding="utf-8")
        duplicates = duplicate_keys(raw)
        if duplicates:
            errors.append(f"중복 키: {target.namespace}:{duplicates}")
        if korean_file.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"UTF-8 BOM: {target.namespace}")
        untranslated: list[str] = []
        names_by_korean: dict[str, list[str]] = defaultdict(list)
        for key, source in english.items():
            target_value = korean[key]
            errors.extend(validate_family_value(family, key, source, target_value))
            if (
                key.startswith(("item.", "block."))
                and isinstance(source, str)
                and isinstance(target_value, str)
            ):
                names_by_korean[target_value].append(key)
            if (
                isinstance(source, str)
                and isinstance(target_value, str)
                and source == target_value
                and not is_family_allowed_original(family, key, source)
            ):
                untranslated.append(key)
        collisions = []
        for translated, keys in names_by_korean.items():
            source_names = {english[key] for key in keys}
            if (
                len(source_names) > 1
                and frozenset(source_names) not in ALLOWED_NAME_COLLISIONS
            ):
                collisions.append(
                    {
                        "translation": translated,
                        "keys": keys,
                        "english": sorted(source_names),
                    }
                )
        if collisions:
            errors.append(f"번역으로 생긴 이름 충돌: {target.namespace}:{collisions}")
        output = OUTPUT_ASSETS / target.namespace / "lang/ko_kr.json"
        expected_output = dict(korean)
        guide_extra_path = PROJECT_ROOT / "working/ars_nouveau/guide_extra_ko_kr.json"
        guide_extra_keys = 0
        integration_extra_keys = 0
        if family == "ars_nouveau" and guide_extra_path.is_file():
            guide_extra = {
                key: value
                for key, value in load_json(guide_extra_path).items()
                if key.startswith(f"{target.namespace}.")
            }
            expected_output.update(guide_extra)
            guide_extra_keys = len(guide_extra)
        hostile_integration_path = (
            PROJECT_ROOT
            / "working/eternal_starlight/integrations/hostilenetworks/ko_kr.json"
        )
        if (
            family == "hostile_neural_networks"
            and target.namespace == "hostilenetworks"
            and hostile_integration_path.is_file()
        ):
            hostile_integration = load_json(hostile_integration_path)
            expected_output.update(hostile_integration)
            integration_extra_keys = len(hostile_integration)
        compact_extra_path = (
            PROJECT_ROOT / "working/compact_machines/kubejs_extra_ko_kr.json"
        )
        if (
            family == "compact_machines"
            and target.namespace == "compactmachines"
            and compact_extra_path.is_file()
        ):
            compact_extra = load_json(compact_extra_path)
            expected_output.update(compact_extra)
            integration_extra_keys = len(compact_extra)
        create_extra_path = (
            PROJECT_ROOT
            / "working/create/integrations/create_enchantment_industry"
            / target.namespace
            / "ko_kr.json"
        )
        if family == "create" and create_extra_path.is_file():
            create_extra = load_json(create_extra_path)
            create_extra_source_path = create_extra_path.with_name("en_us.json")
            if not create_extra_source_path.is_file():
                errors.append(f"통합 원문 누락: {target.namespace}")
            else:
                create_extra_source = load_json(create_extra_source_path)
                if set(create_extra_source) != set(create_extra):
                    errors.append(f"통합 키 불일치: {target.namespace}")
                for key, source_value in create_extra_source.items():
                    if key not in create_extra:
                        continue
                    target_value = create_extra[key]
                    errors.extend(validate_value(key, source_value, target_value))
                    if (
                        isinstance(source_value, str)
                        and isinstance(target_value, str)
                        and source_value == target_value
                        and not is_allowed_original(source_value)
                    ):
                        errors.append(f"통합 미번역: {target.namespace}:{key}")
            expected_output.update(create_extra)
            integration_extra_keys += len(create_extra)
        modern_industrialization_extra_path = (
            PROJECT_ROOT / "working/modern_industrialization/kubejs_extra_ko_kr.json"
        )
        if (
            family == "modern_industrialization"
            and target.namespace == "modern_industrialization"
            and modern_industrialization_extra_path.is_file()
        ):
            modern_industrialization_extra = load_json(
                modern_industrialization_extra_path
            )
            expected_output.update(modern_industrialization_extra)
            integration_extra_keys += len(modern_industrialization_extra)
        output_matches = output.is_file() and load_json(output) == expected_output
        if not output_matches:
            errors.append(f"누적 출력 불일치: {target.namespace}")
        jar = find_jar(instance, target.jar_prefix)
        _, korean_path = language_paths(target.namespace)
        with ZipFile(jar) as archive:
            bundled = (
                load_json_bytes(archive.read(korean_path))
                if korean_path in archive.namelist()
                else {}
            )
        provenance = Counter()
        for key, target_value in korean.items():
            source_value = english[key]
            reusable = target_value != source_value or is_family_allowed_original(
                family, key, str(target_value)
            )
            if key in bundled and target_value == bundled[key] and reusable:
                provenance["bundled_exact_reuse"] += 1
            elif sources.get(key) == "project_output_review" and reusable:
                provenance["project_output_reuse"] += 1
            else:
                provenance["new_or_edited"] += 1
        rows.append(
            {
                "label": target.label,
                "jar": jar.name,
                "namespace": target.namespace,
                "english_keys": len(english),
                "korean_keys": len(korean),
                "untranslated": len(untranslated),
                "untranslated_examples": untranslated[:30],
                "duplicate_keys": len(duplicates),
                "translation_induced_name_collisions": len(collisions),
                "output_matches": output_matches,
                "guide_extra_keys": guide_extra_keys,
                "integration_extra_keys": integration_extra_keys,
                **dict(provenance),
            }
        )
        if untranslated:
            errors.append(
                f"분류되지 않은 영어 유지: {target.namespace}:{untranslated[:30]}"
            )
    return rows, errors


def build(family: str) -> dict[str, object]:
    """검수한 작업본을 누적 리소스팩에 반영한다."""
    copied: list[str] = []
    for target in targets_for(family):
        if not target.language_target:
            continue
        source = PROJECT_ROOT / "working" / family / target.namespace / "ko_kr.json"
        if not source.is_file():
            raise FileNotFoundError(source)
        destination = OUTPUT_ASSETS / target.namespace / "lang/ko_kr.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        guide_extra_path = PROJECT_ROOT / "working/ars_nouveau/guide_extra_ko_kr.json"
        if family == "ars_nouveau" and guide_extra_path.is_file():
            merged = load_json(destination)
            merged.update(
                {
                    key: value
                    for key, value in load_json(guide_extra_path).items()
                    if key.startswith(f"{target.namespace}.")
                }
            )
            destination.write_text(
                json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        hostile_integration_path = (
            PROJECT_ROOT
            / "working/eternal_starlight/integrations/hostilenetworks/ko_kr.json"
        )
        if (
            family == "hostile_neural_networks"
            and target.namespace == "hostilenetworks"
            and hostile_integration_path.is_file()
        ):
            merged = load_json(destination)
            merged.update(load_json(hostile_integration_path))
            destination.write_text(
                json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        create_extra_path = (
            PROJECT_ROOT
            / "working/create/integrations/create_enchantment_industry"
            / target.namespace
            / "ko_kr.json"
        )
        if family == "create" and create_extra_path.is_file():
            merged = load_json(destination)
            merged.update(load_json(create_extra_path))
            destination.write_text(
                json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        copied.append(destination.relative_to(PROJECT_ROOT).as_posix())
    return {"family": FAMILY_LABELS[family], "copied": copied}


def verify_botany_recipe_data(instance: Path) -> tuple[dict[str, object], list[str]]:
    """Botany 계열 레시피와 기존 KubeJS 표시 문구를 검증한다."""
    errors: list[str] = []
    recipe_rows = []
    unexpected_literals = []
    for label, prefix, namespace in (
        ("Botany Pots", "botanypots-neoforge-", "botanypots"),
        ("Botany Trees", "botanytrees-neoforge-", "botanytrees"),
        ("Botany Pots Mystical", "botanypotsmystical-", "botanypots"),
    ):
        jar = find_jar(instance, prefix)
        with ZipFile(jar) as archive:
            recipes = sorted(
                name
                for name in archive.namelist()
                if name.endswith(".json")
                and name.startswith(f"data/{namespace}/")
                and ("/recipe/" in name or "/recipes/" in name)
            )
            for name in recipes:
                data = load_json_bytes(archive.read(name))
                for key in ("name", "title", "description", "text"):
                    if key in data:
                        unexpected_literals.append(f"{jar.name}:{name}:{key}")
        recipe_rows.append({"label": label, "jar": jar.name, "recipes": len(recipes)})
    if unexpected_literals:
        errors.append(
            "Botany 계열 레시피의 예상 밖 표시 literal: "
            + ", ".join(unexpected_literals[:30])
        )

    kubejs_root = instance / "kubejs"
    pattern = re.compile(r"botanypots|botanytrees|botany pots|botany trees", re.I)
    kubejs_files = []
    for path in sorted(kubejs_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json", ".snbt"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if pattern.search(text):
            kubejs_files.append(path.relative_to(instance).as_posix())

    announcements = (
        PROJECT_ROOT
        / "output/overrides/kubejs/server_scripts/announcements/announcements.js"
    )
    tooltip = PROJECT_ROOT / "output/overrides/kubejs/client_scripts/tooltips.js"
    expected_snippets = {
        announcements: "추가된 모드: The Aether, BotanyPots, BotanyTrees, RefinedTypes",
        tooltip: "식물 화분에서 수확하려면 섬세한 손길이 부여된 괭이가 필요합니다",
    }
    for path, snippet in expected_snippets.items():
        if not path.is_file() or snippet not in path.read_text(encoding="utf-8"):
            errors.append(f"기존 Botany 계열 KubeJS 번역 누락: {path}")
    return (
        {
            "recipe_sets": recipe_rows,
            "recipes_checked": sum(int(row["recipes"]) for row in recipe_rows),
            "unexpected_display_literals": unexpected_literals,
            "kubejs_files_reviewed": len(kubejs_files),
            "kubejs_reference_paths": kubejs_files,
            "new_kubejs_visible_literals": 0,
            "existing_kubejs_translations_verified": len(expected_snippets),
        },
        errors,
    )


def verify(instance: Path, family: str) -> tuple[dict[str, object], int]:
    """모드군 언어 산출물을 검증하고 보고서를 기록한다."""
    languages, errors = verify_language(instance, family)
    quests, quest_errors = verify_quests(instance, family)
    errors.extend(quest_errors)
    family_data: dict[str, object] = {}
    if family == "botany_pots_trees":
        family_data, family_errors = verify_botany_recipe_data(instance)
        errors.extend(family_errors)
    provenance = {
        key: sum(int(row.get(key, 0)) for row in languages)
        for key in (
            "bundled_exact_reuse",
            "project_output_reuse",
            "new_or_edited",
        )
    }
    report = {
        "family": FAMILY_LABELS[family],
        "languages": languages,
        "language_provenance": provenance,
        "ftbquests": quests,
        "family_data": family_data,
        "validation_errors": len(errors),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    path = PROJECT_ROOT / "working" / family / "language_validation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "inventory",
            "prepare",
            "prepare-quests",
            "normalize",
            "build",
            "build-quests",
            "verify",
        ),
    )
    parser.add_argument("family", choices=tuple(FAMILY_LABELS))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--namespace", action="append")
    args = parser.parse_args()
    instance = resolve_source_root()
    if args.command == "inventory":
        result = inventory(instance, args.family)
        report_path = PROJECT_ROOT / "working" / args.family / "inventory.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        status = 0
    elif args.command == "prepare":
        result = prepare(instance, args.family, args.force, args.namespace)
        status = 0
    elif args.command == "prepare-quests":
        result = prepare_quests(instance, args.family, args.force)
        status = 0
    elif args.command == "normalize":
        result = normalize(args.family)
        status = 0
    elif args.command == "build-quests":
        result = build_quests(instance, args.family)
        status = 0
    elif args.command == "build":
        result = build(args.family)
        status = 0
    else:
        result, status = verify(instance, args.family)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
