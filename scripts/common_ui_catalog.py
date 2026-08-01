"""공통 문구와 공통 UI 번역 대상 목록이다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    """계획서 한 행에 속하는 설치 모드 언어 파일 정보."""

    group: str
    jar_prefix: str
    namespaces: tuple[str, ...]
    key_prefixes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PackLanguageTarget:
    """모드 JAR 밖의 팩 언어 파일 정보."""

    group: str
    namespace: str
    relative_dir: str


TARGETS = (
    Target("atm10_common", "ftb-quests-neoforge-", ("ftbquests",)),
    Target("atm10_common", "ftbquestslangsplitter-", ("ftbquestslangsplitter",)),
    Target(
        "atm10_common",
        "allthetweaks-",
        ("allthetweaks",),
        ("allthetweaks.valhelsia_core.",),
    ),
    Target("jei", "jei-1.21.1-neoforge-", ("jei",)),
    Target(
        "jei",
        "refinedstorage-jei-integration-neoforge-",
        ("refinedstorage_jei_integration",),
    ),
    Target("jade", "Jade-", ("jade",)),
    Target("map_team", "journeymap-neoforge-", ("journeymap",)),
    Target("map_team", "ftb-chunks-neoforge-", ("ftbchunks",)),
    Target("map_team", "ftb-teams-neoforge-", ("ftbteams",)),
    Target("compass", "waystones-neoforge-", ("waystones",)),
    Target("compass", "NaturesCompass-", ("naturescompass",)),
    Target("compass", "ExplorersCompass-", ("explorerscompass",)),
    Target("curios_effects", "curios-neoforge-", ("curios",)),
    Target("curios_effects", "moreoverlays-", ("moreoverlays",)),
    Target("guide_ui", "guideme-", ("guideme",)),
    Target(
        "guide_ui",
        "modonomicon-",
        ("modonomicon",),
        (
            "item.modonomicon.",
            "itemGroup.modonomicon",
            "modonomicon.command.",
            "modonomicon.configuration.",
            "modonomicon.gui.",
            "modonomicon.multiblock.",
            "modonomicon.subtitle.",
            "tooltip.modonomicon.",
        ),
    ),
    Target(
        "guide_ui",
        "Patchouli-",
        ("patchouli",),
        (
            "item.patchouli.guide_book",
            "patchouli.subtitle.",
            "patchouli.gui.",
            "patchouli.networking.",
        ),
    ),
    Target("guide_ui", "AkashicTome-", ("akashictome",)),
    Target("convenience", "ftb-ultimine-neoforge-", ("ftbultimine",)),
    Target("convenience", "tombstone-neoforge-", ("tombstone",)),
    Target("convenience", "lootr-neoforge-", ("lootr",)),
    Target("convenience", "polymorph-neoforge-", ("polymorph",)),
    Target("convenience", "craftingtweaks-neoforge-", ("craftingtweaks",)),
    Target("inventory_controls", "Controlling-neoforge-", ("controlling",)),
    Target(
        "inventory_controls",
        "BetterAdvancements-NeoForge-",
        ("betteradvancements",),
    ),
    Target("inventory_controls", "appleskin-neoforge-", ("appleskin",)),
    Target("inventory_controls", "invtweaks-", ("invtweaks",)),
    Target("inventory_controls", "trashslot-neoforge-", ("trashslot",)),
    Target("tempad", "tempad-", ("tempad", "tempad_static")),
)


PACK_LANGUAGE_TARGETS = (
    PackLanguageTarget("atm10_common", "atm", "kubejs/assets/atm/lang"),
)


NO_LANGUAGE_TARGETS = {
    "jei": ("FTB JEI Extras", "AE2 JEI Integration"),
    "curios_effects": ("Enchantment Descriptions (설치되지 않음)",),
    "convenience": ("Ars Polymorphia",),
    "inventory_controls": ("Mouse Tweaks",),
}


GROUPS = tuple(dict.fromkeys(target.group for target in TARGETS))
