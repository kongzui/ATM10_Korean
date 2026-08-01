#!/usr/bin/env python3
"""Allthemodium·ATM 장비 계열 언어 검수본을 전체 번역한다."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile

from atmgear_catalog import BATCHES, TARGETS
from local_paths import resolve_source_root
from prepare_atmgear import WORK_ROOT, find_jar, load_json

ALLOY_NAMES = {
    "Vibranium - Allthemodium Alloy": "Vibranium-Allthemodium 합금",
    "Vibranium-Allthemodium Alloy": "Vibranium-Allthemodium 합금",
    "Unobtainium - Allthemodium Alloy": "Unobtainium-Allthemodium 합금",
    "Unobtainium-Allthemodium Alloy": "Unobtainium-Allthemodium 합금",
    "Unobtainium - Vibranium Alloy": "Unobtainium-Vibranium 합금",
    "Unobtainium-Vibranium Alloy": "Unobtainium-Vibranium 합금",
}
MATERIALS = {"Allthemodium", "Vibranium", "Unobtainium"}

EXPLICIT = {
    "itemGroup.allthemodium": "Allthemodium",
    "itemGroup.allthemodium_mek": "Allthemodium Mekanism 호환",
    "allthemodium.description": "Allthemodium 조각! 수많은 단계 중 첫걸음입니다!",
    "item.allthemodium.smithing_template.allthemodium_upgrade.applies_to": "네더라이트 장비",
    "item.allthemodium.smithing_template.allthemodium_upgrade.ingredients": "Allthemodium 주괴",
    "item.allthemodium.smithing_template.vibranium_upgrade.applies_to": "Allthemodium 장비",
    "item.allthemodium.smithing_template.vibranium_upgrade.ingredients": "Vibranium 주괴",
    "item.allthemodium.smithing_template.unobtainium_upgrade.applies_to": "Vibranium 장비",
    "item.allthemodium.smithing_template.unobtainium_upgrade.ingredients": "Unobtainium 주괴",
    "item.allthemodium.smithing_template.allthemodium_upgrade.base_slot_description": "네더라이트 방어구, 무기 또는 도구를 추가하세요",
    "item.allthemodium.smithing_template.allthemodium_upgrade.additions_slot_description": "Allthemodium 주괴를 추가하세요",
    "item.allthemodium.smithing_template.vibranium_upgrade.base_slot_description": "Allthemodium 방어구, 무기 또는 도구를 추가하세요",
    "item.allthemodium.smithing_template.vibranium_upgrade.additions_slot_description": "Vibranium 주괴를 추가하세요",
    "item.allthemodium.smithing_template.unobtainium_upgrade.base_slot_description": "Vibranium 방어구, 무기 또는 도구를 추가하세요",
    "item.allthemodium.smithing_template.unobtainium_upgrade.additions_slot_description": "Unobtainium 주괴를 추가하세요",
    "piglin.friend": "피글린이 중립적으로 변합니다",
    "quick.snack": "빠르게 먹을 수 있습니다",
    "indestructible": "파괴 불가",
    "low.cal": "언제든 먹을 수 있습니다",
    "steel.skin": "흡수",
    "cats.eyes": "야간 투시",
    "troll.blood": "재생",
    "fire.proof": "화염 및 용암 피해에 면역입니다",
    "wither.proof": "시듦 피해로부터 보호합니다",
    "magic.resistance": "마법 피해 저항",
    "breath.proof": "브레스 무기 피해를 받지 않습니다",
    "steady.legs": "셜커의 공중 부양 공격으로부터 보호합니다",
    "steady.guts": "멀미에 면역입니다",
    "light.step": "낙하 피해를 받지 않습니다",
    "hard.head": "겉날개 비행 중 충돌 피해를 받지 않습니다",
    "aqua.lungs": "수중 호흡",
    "teleport.pad": "채굴 차원 및 기타 장소",
    "how.to.teleport": "오버월드에 설치한 뒤 양손을 비우고 웅크린 채 우클릭하세요",
    "allthemodium.loc": "딥 다크 생물 군계의 동굴 벽과 천장에 고르게 생성됩니다",
    "vibranium.loc": "네더의 Y 64 이상 동굴 벽에 생성됩니다",
    "vibranium.other.loc": "디 아더의 모든 생물 군계에서 Y 0~40에 생성됩니다",
    "unobtainium.loc": "엔드 고지대 생물 군계에만 생성됩니다",
    "allthemodium.mine": "플레이어만 채굴할 수 있으며 채석기로 캘 수 없습니다",
    "config.jade.plugin_allthemodium.teleport_pad": "텔레포트 패드",
    "jade.allthemodium.teleport_pad.tip": "양손을 비우고 Shift+우클릭하세요",
    "jade.allthemodium.teleport_pad.no_drop": "채굴해도 드롭되지 않습니다!",
    "jade.allthemodium.teleport_pad.transports_to": "이동 대상",
    "tooltip.allthemodium.teleport_pad": "양손을 비우고 웅크린 채 우클릭하면 순간이동합니다",
    "dimension.allthemodium.unknown": "알 수 없는 차원",
    "dimension.allthemodium.mining": "채굴 차원",
    "dimension.allthemodium.the_other": "디 아더",
    "dimension.allthemodium.the_beyond": "The Beyond",
    "biome.allthemodium.mining": "ATM 채굴 차원",
    "biome.allthemodium.the_beyond": "The Beyond",
    "biome.allthemodium.the_other": "디 아더",
    "block.allthemodium.allthemodium_source_jar": "Allthemodium 마나 단지",
}

BIOMES = {
    "The Other: Badlands": "디 아더: 악지",
    "The Other: Badlands Plateau": "디 아더: 악지 고원",
    "Ancient Basalt Deltas": "고대 현무암 삼각주",
    "Ancient Crimson Forest": "고대 진홍빛 숲",
    "The Other Desert": "디 아더 사막",
    "The Other Desert Hills": "디 아더 사막 언덕",
    "The Other: Eroded Badlands": "디 아더: 침식된 악지",
    "The Other: Gravelly Mountains": "디 아더: 자갈 산",
    "The Other: Modified Badlands Plateau": "디 아더: 변형된 악지 고원",
    "The Other: Modified Gravelly Mountains": "디 아더: 변형된 자갈 산",
    "The Other: Mountains Edge": "디 아더: 산 가장자리",
    "The Other: Mountains": "디 아더: 산",
    "The Other: Wastelands": "디 아더: 황무지",
    "The Other Soul Sand Valley": "디 아더 영혼 모래 골짜기",
    "Ancient Warped Forest": "고대 뒤틀린 숲",
}

WORLD_PREFIXES = {
    "Ancient": "고대",
    "Demonic": "악마",
    "Soul": "영혼",
}
WORLD_NOUNS = {
    "Bookshelf": "책장",
    "Leaves": "나뭇잎",
    "Log": "원목",
    "Planks": "판자",
    "Herbs": "약초",
    "Sapling": "묘목",
    "Door": "문",
    "Trapdoor": "다락문",
    "Dirt": "흙",
    "Grass": "잔디",
    "Podzol": "회백토",
    "Stone": "돌",
    "Smooth Stone": "매끄러운 돌",
    "Polished Stone": "윤나는 돌",
    "Chiseled Stone Bricks": "조각된 석재 벽돌",
    "Stone Bricks": "석재 벽돌",
    "Cracked Stone Bricks": "금 간 석재 벽돌",
    "Mossy Stone": "이끼 낀 돌",
    "Stone Wall": "돌 담장",
    "Smooth Stone Wall": "매끄러운 돌 담장",
    "Polished Stone Wall": "윤나는 돌 담장",
    "Chiseled Stone Brick Wall": "조각된 석재 벽돌 담장",
    "Stone Brick Wall": "석재 벽돌 담장",
    "Cracked Stone Brick Wall": "금 간 석재 벽돌 담장",
    "Mossy Stone Wall": "이끼 낀 돌 담장",
    "Wooden Fence": "나무 울타리",
    "Wooden Fence Gate": "나무 울타리 문",
    "Wooden Stairs": "나무 계단",
    "Stone Stairs": "돌 계단",
    "Smooth Stone Stairs": "매끄러운 돌 계단",
    "Polished Stone Stairs": "윤나는 돌 계단",
    "Chiseled Stone Brick Stairs": "조각된 석재 벽돌 계단",
    "Stone Brick Stairs": "석재 벽돌 계단",
    "Cracked Stone Brick Stairs": "금 간 석재 벽돌 계단",
    "Mossy Stone Stairs": "이끼 낀 돌 계단",
    "Wooden Slab": "나무 반 블록",
    "Stone Slab": "돌 반 블록",
    "Smooth Stone Slab": "매끄러운 돌 반 블록",
    "Polished Stone Slab": "윤나는 돌 반 블록",
    "Chiseled Stone Brick Slab": "조각된 석재 벽돌 반 블록",
    "Stone Brick Slab": "석재 벽돌 반 블록",
    "Cracked Stone Brick Slab": "금 간 석재 벽돌 반 블록",
    "Mossy Stone Slab": "이끼 낀 돌 반 블록",
    "Vines": "덩굴",
    "Fern": "고사리",
}

SUFFIXES = {
    " Upgrade": " 업그레이드",
    " Smithing Template": " 대장장이 형판",
    " Trident": " 삼지창",
    " Crossbow": " 쇠뇌",
    " Shield": " 방패",
    " Pickaxe": " 곡괭이",
    " Pick": " 곡괭이",
    " Shovel": " 삽",
    " Helmet": " 투구",
    " Chestplate": " 흉갑",
    " Leggings": " 레깅스",
    " Boots": " 부츠",
    " Nugget Pile": " 조각 더미",
    " Nugget": " 조각",
    " Ingot": " 주괴",
    " Plate": " 판",
    " Rod": " 막대",
    " Gear": " 톱니바퀴",
    " Dust": " 가루",
    " Clump": " 덩어리",
    " Shard": " 파편",
    " Crystal": " 결정",
    " Bucket": " 양동이",
    " Apple": " 사과",
    " Carrot": " 당근",
    " Bow": " 활",
    " Mace": " 철퇴",
    " Axe": " 도끼",
    " Hoe": " 괭이",
    " Sword": " 검",
    " Blade": " 칼날",
    " Paxel": " 팩셀",
}


def core_name(source: str) -> str:
    """재료나 합금 이름을 확정 표기로 바꾼다."""
    source = source.replace("AllTheModium", "Allthemodium")
    if source == "Piglich Hearts":
        return "피글리치 심장"
    if source in ALLOY_NAMES:
        return ALLOY_NAMES[source]
    if source == "Allthemodium Alloy":
        return "Allthemodium 합금"
    if source in MATERIALS:
        return source
    return source


def translate_world_name(source: str) -> str | None:
    """고대·악마·영혼 계열 건축 블록명을 번역한다."""
    stripped = False
    if source.startswith("Stripped "):
        stripped = True
        source = source.removeprefix("Stripped ")
    for prefix, korean_prefix in WORLD_PREFIXES.items():
        marker = f"{prefix} "
        if source.startswith(marker):
            noun = source.removeprefix(marker)
            if noun in WORLD_NOUNS:
                result = f"{korean_prefix} {WORLD_NOUNS[noun]}"
                return f"껍질 벗긴 {result}" if stripped else result
    return None


def translate_name(key: str, source: str) -> str:
    """아이템·블록·재료의 구조화된 이름을 번역한다."""
    if source in BIOMES:
        return BIOMES[source]
    world = translate_world_name(source)
    if world:
        return world
    if source == "Ancient Soul Berries":
        return "고대 영혼 열매"
    if source == "Piglich":
        return "피글리치"
    if source == "Piglich Heart":
        return "피글리치 심장"
    if source == "Teleport Pad":
        return "텔레포트 패드"
    if source == "Soul Lava":
        return "영혼 용암"
    if source == "Soul Lava Bucket":
        return "영혼 용암 양동이"
    if source == "Suspicious Clay":
        return "수상한 점토"
    if source == "Suspicious Soul Sand":
        return "수상한 영혼 모래"
    if source == "ATM Mining Dim":
        return "ATM 채굴 차원"
    if source == "The Beyond":
        return "The Beyond"
    if source == "The Other":
        return "디 아더"
    if source.startswith("Block of Raw "):
        return f"{core_name(source.removeprefix('Block of Raw '))} 원석 블록"
    if source.startswith("Block of "):
        return f"{core_name(source.removeprefix('Block of '))} 블록"
    if source.startswith("Raw ") and source.endswith(" Ore"):
        return f"{core_name(source[4:-4])} 원석"
    if source.startswith("Crushed "):
        return f"분쇄된 {core_name(source.removeprefix('Crushed '))}"
    if source.endswith(" Deepslate Ore"):
        return f"심층암 {core_name(source.removesuffix(' Deepslate Ore'))} 광석"
    if source == "Other Vibranium Ore":
        return "디 아더 Vibranium 광석"
    if source.endswith(" Ore"):
        return f"{core_name(source.removesuffix(' Ore'))} 광석"
    match = re.fullmatch(r"(Clean|Dirty) (.+) Slurry", source)
    if match:
        adjective = "정제된" if match.group(1) == "Clean" else "불순물 섞인"
        return f"{adjective} {core_name(match.group(2))} 슬러리"
    if source.startswith("Dirty ") and source.endswith(" Dust"):
        return f"불순물 섞인 {core_name(source[6:-5])} 가루"
    if source.startswith("Molten "):
        body = source.removeprefix("Molten ")
        if body.endswith(" Bucket"):
            return f"용융 {core_name(body.removesuffix(' Bucket'))} 양동이"
        return f"용융 {core_name(body)}"
    if source.endswith(" Vapor Bucket"):
        return f"{core_name(source.removesuffix(' Vapor Bucket'))} 증기 양동이"
    if source.endswith(" Vapor"):
        return f"{core_name(source.removesuffix(' Vapor'))} 증기"
    for suffix, korean in SUFFIXES.items():
        if source.endswith(suffix):
            return f"{core_name(source.removesuffix(suffix))}{korean}"
    if source in MATERIALS or source in ALLOY_NAMES:
        return core_name(source)
    raise KeyError(f"구조화된 이름을 번역할 수 없습니다: {key}={source}")


ARCANIST = {
    "allthearcanistgear.perk_desc.thread_flight": "크리에이티브 비행을 부여합니다. 최소 4레벨 슬롯에 장착해야 합니다.",
    "allthearcanistgear.perk_desc.thread_spectral_sight": "분광 시야를 부여하여 벽 너머의 생물을 볼 수 있습니다. 레벨당 반경 8블록까지 볼 수 있습니다.",
    "allthearcanistgear.perk_desc.thread_truesight": "진실의 시야를 부여하여 주변을 더 잘 볼 수 있습니다. 1단계는 야간 투시, 2단계는 실명 면역, 3단계는 어둠 면역, 4단계는 용암 투시를 부여합니다.",
    "allthearcanistgear.perk_desc.thread_vitality": "레벨마다 최대 체력이 하트 1개 증가합니다.",
    "allthearcanistgear.thread_of": "%s의 실타래",
    "chat.allthearcanistgear.low_tier": "이 블록을 부수려면 더 강력한 주문서가 필요합니다.",
    "chat.allthearcanistgear.too_weak": "이 블록을 부수려면 증폭 수치가 더 높아야 합니다.",
    "item.allthearcanistgear.creative_spell_book": "크리에이티브 주문서",
    "item.allthearcanistgear.thread_flight": "비행",
    "item.allthearcanistgear.thread_spectral_sight": "분광 시야",
    "item.allthearcanistgear.thread_truesight": "진실의 시야",
    "item.allthearcanistgear.thread_vitality": "활력",
    "tab.allthearcanistgear.armor": "All The Arcanist Gear",
}


def translate_arcanist(key: str, source: str) -> str:
    """All The Arcanist Gear 이름과 설명을 번역한다."""
    if key in ARCANIST:
        return ARCANIST[key]
    match = re.fullmatch(
        r"item\.allthearcanistgear\.(allthemodium|vibranium|unobtainium)_(.+)", key
    )
    if not match:
        raise KeyError(f"All The Arcanist Gear 키를 번역할 수 없습니다: {key}")
    material = {
        "allthemodium": "Allthemodium",
        "vibranium": "Vibranium",
        "unobtainium": "Unobtainium",
    }[match.group(1)]
    item = {
        "boots": "비전술사 부츠",
        "hat": "비전술사 모자",
        "leggings": "비전술사 레깅스",
        "robes": "비전술사 로브",
        "spell_book": "주문서",
    }[match.group(2)]
    return f"{material} {item}"


def translate_wizard(key: str, source: str) -> str:
    """All the Wizard Gear 아이템 이름을 확정 표기로 통일한다."""
    if key == "tab.allthewizardarmor.armor":
        return "All the Wizard Gear"
    match = re.fullmatch(
        r"item\.allthewizardgear\.(allthemodium|vibranium|unobtainium)_(.+)", key
    )
    if not match:
        raise KeyError(f"All the Wizard Gear 키를 번역할 수 없습니다: {key}")
    material = {
        "allthemodium": "Allthemodium",
        "vibranium": "Vibranium",
        "unobtainium": "Unobtainium",
    }[match.group(1)]
    item = {
        "mage_helmet": "마법사 모자",
        "mage_chestplate": "마법사 로브",
        "mage_leggings": "마법사 레깅스",
        "mage_boots": "마법사 부츠",
        "spell_book": "주문서",
    }[match.group(2)]
    return f"{material} {item}"


def translate(instance: Path, batch: str) -> dict[str, int | str]:
    """한 언어 네임스페이스를 전수 번역한다."""
    path = WORK_ROOT / batch / "ko_kr.json"
    before = json.loads(path.read_text(encoding="utf-8"))
    target = next(target for target in TARGETS if target.batch == batch)
    with ZipFile(find_jar(instance, target)) as archive:
        data = load_json(archive, f"assets/{batch}/lang/en_us.json")
    for key, source in list(data.items()):
        if not isinstance(source, str):
            raise TypeError(f"문자열이 아닌 언어 값: {key}")
        if batch == "allthemodium":
            data[key] = (
                EXPLICIT[key] if key in EXPLICIT else translate_name(key, source)
            )
        elif batch == "allthearcanistgear":
            data[key] = translate_arcanist(key, source)
        else:
            data[key] = translate_wizard(key, source)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "namespace": batch,
        "keys": len(data),
        "changed": sum(before[key] != value for key, value in data.items()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", choices=BATCHES + ("all",))
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    selected = BATCHES if args.batch == "all" else (args.batch,)
    print(
        json.dumps(
            [translate(instance, batch) for batch in selected],
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
