#!/usr/bin/env python3
"""Farmer's Delight 계열 언어와 관련 퀘스트를 현재 영어 원문으로 전면 재검수해요."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "farmers_delight"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
QUEST_ROOT = WORK_ROOT / "quests/related"
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
NUMBER = re.compile(r"\d+(?:[.,/xX×]\d+)*")

EXACT = {
    "farmersdelight": {
        "itemGroup.farmersdelight": "Farmer's Delight",
        "advancements.farmersdelight.root.title": "Farmer's Delight",
        "block.farmersdelight.onions": "양파 작물",
        "block.farmersdelight.rice": "벼 작물",
        "block.farmersdelight.rice_panicles": "벼 이삭 작물",
        "farmersdelight.configuration.enableVanillaCropCrates.tooltip": "활성화하면 바닐라 작물용 3x3 저장 상자(Quark와 Thermal Cultivation의 상자와 유사)를 제작할 수 있습니다.",
        "farmersdelight.configuration.richSoilBoostChance.tooltip": "비옥한 토양이 그 위에 심은 작물에 뼛가루 성장 효과를 줄 확률(소수)입니다. 0.0이면 비활성화됩니다.",
        "advancements.farmersdelight.get_fd_seed.description": "여러 기후의 야생이나 어딘가의 상자에서 새로운 작물 네 가지를 찾아보세요.",
        "farmersdelight.configuration.cuttingBoardFortuneBonus.tooltip": "행운 레벨마다 도마에서 희귀 결과를 얻을 확률이 얼마나 증가하는지 정합니다. 0.0이면 비활성화됩니다.",
    },
    "cookingforblockheads": {
        "item.cookingforblockheads.no_filter_edition": "Cooking for Blockheads",
        "item.cookingforblockheads.recipe_book": "Cooking for Blockheads I",
        "item.cookingforblockheads.crafting_book": "Cooking for Blockheads II",
        "itemGroup.cookingforblockheads.cookingforblockheads": "Cooking for Blockheads",
        "gui.cookingforblockheads.moved_to_oven": "오븐으로 옮겼습니다",
        "gui.cookingforblockheads.moved_to_cooking_pot": "요리 냄비로 옮겼습니다",
        "gui.cookingforblockheads.cooking_pot_obstructed": "요리 냄비가 막혀 있습니다",
        "gui.cookingforblockheads.feedback_stacked": "%s x%d",
        "tooltip.cookingforblockheads.missing_cooking_pot": "요리할 요리 냄비가 없습니다",
        "tooltip.cookingforblockheads.sort_by_eatenness": "먹은 음식순 정렬",
        "tooltip.cookingforblockheads.kitchen_upgrade": "주방 업그레이드",
        "container.cookingforblockheads.cooking_table": "요리 테이블",
        "config.jade.plugin_cookingforblockheads.preservation_chamber": "보존실",
        "waila.cookingforblockheads.toast_progress": "굽는 중... (%s %%)",
        "cookingforblockheads.configuration.ovenFuelTimeMultiplier.tooltip": "요리 오븐의 연료 지속 시간 배수입니다. 값이 클수록 오래 타며, 화로 기본값은 1.0입니다.",
        "cookingforblockheads.configuration.cowJarMilkPerTick.tooltip": "병 속의 소가 매 틱 생성하는 우유의 양입니다.",
    },
    "farmingforblockheads": {
        "itemGroup.farmingforblockheads.farmingforblockheads": "Farming for Blockheads",
        "commands.farmingforblockheads.reload.success": "Farming for Blockheads 레지스트리를 다시 불러왔습니다.",
        "tooltip.farmingforblockheads.red_fertilizer": "성장 속도를 높입니다",
        "tooltip.farmingforblockheads.green_fertilizer": "작물 생산량을 늘립니다",
        "tooltip.farmingforblockheads.yellow_fertilizer": "농지가 짓밟히지 않게 합니다",
        "tooltip.farmingforblockheads.payment": "비용: %s",
        "tooltip.farmingforblockheads.payment_item": "%dx %s",
        "gui.farmingforblockheads.market.cost": "%s",
        "category.farmingforblockheads.seeds": "씨앗",
        "category.farmingforblockheads.saplings": "묘목",
        "category.farmingforblockheads.flowers": "꽃",
        "category.farmingforblockheads.other": "기타",
        "farmingforblockheads.configuration.title": "Farming for Blockheads",
        "farmingforblockheads.configuration.enabledOptionalPresets": "활성화할 선택 사전 설정",
        "farmingforblockheads.configuration.enabledOptionalPresets.tooltip": "활성화할 선택 사전 설정 목록입니다.",
        "farmingforblockheads.configuration.disabledDefaultPresets": "비활성화할 기본 사전 설정",
        "farmingforblockheads.configuration.disabledDefaultPresets.tooltip": "비활성화할 기본 사전 설정 목록입니다.",
        "farmingforblockheads.configuration.merchantNames": "상인 이름",
        "farmingforblockheads.configuration.merchantNames.tooltip": "상인에게 붙을 수 있는 이름 목록입니다.",
        "farmingforblockheads.configuration.feedingTroughRange": "먹이통 범위",
        "farmingforblockheads.configuration.feedingTroughRange.tooltip": "먹이통이 동물에게 먹이를 줄 수 있는 범위입니다.",
        "farmingforblockheads.configuration.feedingTroughMaxAnimals": "먹이통 최대 동물 수",
        "farmingforblockheads.configuration.feedingTroughMaxAnimals.tooltip": "먹이통이 먹이 주기를 멈추는 종류별 최대 동물 수입니다.",
        "farmingforblockheads.configuration.chickenNestRange": "닭 둥지 범위",
        "farmingforblockheads.configuration.chickenNestRange.tooltip": "닭 둥지가 낳은 알을 수집하는 범위입니다.",
        "farmingforblockheads.configuration.fertilizerBonusCropChance": "초록색 비료 추가 작물 확률",
        "farmingforblockheads.configuration.fertilizerBonusCropChance.tooltip": "초록색 비료 사용 시 작물을 추가로 얻을 확률입니다.",
        "farmingforblockheads.configuration.fertilizerBonusGrowthChance": "빨간색 비료 추가 성장 확률",
        "farmingforblockheads.configuration.fertilizerBonusGrowthChance.tooltip": "빨간색 비료 사용 시 한 단계 더 성장할 확률입니다.",
        "farmingforblockheads.configuration.fertilizerRegressionChance": "비료 효과 소멸 확률",
        "farmingforblockheads.configuration.fertilizerRegressionChance.tooltip": "비료로 강화된 농지가 추가 효과를 낼 때마다 일반 농지로 돌아갈 확률입니다.",
        "farmingforblockheads.configuration.treatMerchantsLikeBabies": "상인을 아기로 취급",
        "farmingforblockheads.configuration.treatMerchantsLikeBabies.tooltip": "상인을 기술적으로만 아기로 취급해 피 같은 사망 전리품을 이용한 악용을 막을 수 있습니다.",
        "farmingforblockheads.configuration.excludedGroups": "제외할 그룹",
        "farmingforblockheads.configuration.excludedGroups.tooltip": "비활성화할 그룹 목록입니다. includedGroups보다 우선하며, 예를 들어 'selling.seeds'는 시장의 모든 씨앗을 비활성화합니다.",
        "farmingforblockheads.configuration.includedGroups": "포함할 그룹",
        "farmingforblockheads.configuration.includedGroups.tooltip": "활성화할 그룹 목록입니다. 'default'는 내장 기본 그룹(selling.seeds, selling.saplings, selling.fertilizers.minecraft)을 뜻합니다.",
    },
}

QUEST_EXACT = {
    "quest.1591013DDD4766E1.quest_desc": [
        "&l&cCooking for Blockheads&r는 주방을 집처럼 편리한 공간으로 만들어 줍니다. \\n\\n모든 아이템이 쓸모 있고 멋지니 빠짐없이 활용해 보세요!"
    ],
    "quest.1591013DDD4766E1.title": "&l&cCooking for Blockheads&r",
    "quest.5D5563142917495A.quest_desc": [
        "&l&eFarmer's Delight&r는 농사와 음식 요리에 초점을 맞춘 모드입니다! 같은 아이템을 장식에도 활용할 수 있습니다. \\n\\n화덕, 냄비와 프라이팬은 주방에 잘 어울립니다. \\n\\n음식 통은 식료품 저장실에 좋습니다. \\n\\n농장 용품은 야외 장식에, 찬장은 어디에나 잘 어울립니다!"
    ],
    "quest.5D5563142917495A.title": "&l&eFarmer's Delight&r",
    "task.225F53F8A0E9E822.title": "Cooking for Blockheads",
    "task.4B274207A9646FE9.title": "Farmer's Delight",
    "quest.13AFCD3B6F62B986.quest_desc": ["얼음과 눈 제작법을 사용할 수 있게 합니다!"],
    "quest.13AFCD3B6F62B986.title": "얼음 업그레이드",
    "quest.1515B32545F51266.quest_desc": ["화덕에 전력을 연결할 수 있게 합니다."],
    "quest.1F114EB0AAB86DB4.quest_desc": [
        "시장을 설치하면 에메랄드로 여러 농자재를 파는 상인이 나타납니다.\\n\\n다행히 보통 아이템 하나에 에메랄드 1개이며, 정말 다양한 물품을 판매합니다."
    ],
    "quest.45F83C2750F70F9B.quest_subtitle": "절대 불붙지 않을 거예요...",
    "quest.45F83C2750F70F9B.title": "책으로 주방 만들기",
    "quest.47764EFC822E462A.quest_subtitle": "엄청난 착유 능력... 아주 작은 생활 공간",
    "quest.58D5BD3106BFD94A.quest_subtitle": "충분히 값어치가 있습니다",
}

REPLACEMENTS = (
    ("멍청이도 가능한 요리", "Cooking for Blockheads"),
    ("멍청이도 가능한 농사", "Farming for Blockheads"),
    ("레시피", "제작법"),
    ("멀티 블록", "멀티블록"),
    ("아이템들", "아이템"),
    ("오른쪽 클릭", "우클릭"),
    ("왼쪽 클릭", "좌클릭"),
    ("꺼져있", "꺼져 있"),
    ("켜져있", "켜져 있"),
)


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def transform(value: object) -> object:
    if isinstance(value, str):
        for old, new in REPLACEMENTS:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [transform(item) for item in value]
    return value


def normalize() -> dict[str, object]:
    rows = []
    for namespace in EXACT:
        root = WORK_ROOT / namespace
        english, korean = load(root / "en_us.json"), load(root / "ko_kr.json")
        auto, sources = (
            load(root / "auto_candidates.json"),
            load(root / "candidate_sources.json"),
        )
        reviewed = {}
        for key in english:
            value = EXACT[namespace].get(key)
            if value is None:
                value = (
                    auto[key]
                    if sources[key] == "new_translation_required"
                    else korean[key]
                )
            reviewed[key] = transform(value)
        write(root / "ko_kr.json", reviewed)
        rows.append(
            {
                "namespace": namespace,
                "reviewed_keys": len(reviewed),
                "reused_candidates": sum(
                    v == "bundled_ko_kr" for v in sources.values()
                ),
                "new_translations": sum(
                    v == "new_translation_required" for v in sources.values()
                ),
            }
        )
    english, korean = load(QUEST_ROOT / "en_us.json"), load(QUEST_ROOT / "ko_kr.json")
    write(
        QUEST_ROOT / "ko_kr.json",
        {k: transform(QUEST_EXACT.get(k, korean[k])) for k in english},
    )
    result = {"languages": rows, "quest_keys": len(english), "status": "complete"}
    write(WORK_ROOT / "normalization.json", result)
    return result


def verify_pair(root: Path) -> tuple[dict[str, object], list[str]]:
    english, korean = load(root / "en_us.json"), load(root / "ko_kr.json")
    errors, untranslated = [], []
    if list(english) != list(korean):
        errors.append(f"키 또는 순서 불일치: {root.name}")
    for key in english.keys() & korean.keys():
        source, target = english[key], korean[key]
        errors.extend(family_goal.validate_value(key, source, target))
        if isinstance(source, str) and isinstance(target, str):
            if Counter(NUMBER.findall(source)) != Counter(NUMBER.findall(target)):
                errors.append(f"숫자 불일치: {root.name}:{key}")
            branded = any(
                name in source
                for name in (
                    "Farmer's Delight",
                    "Cooking for Blockheads",
                    "Farming for Blockheads",
                )
            )
            if (
                source == target
                and LATIN_WORD.search(source)
                and not branded
                and not family_goal.is_allowed_original(source)
            ):
                untranslated.append(key)
    if untranslated:
        errors.append(f"분류되지 않은 영어 유지: {root.name}:{untranslated[:20]}")
    return {
        "scope": root.name,
        "keys": len(english),
        "untranslated": untranslated,
    }, errors


def verify() -> tuple[dict[str, object], list[str]]:
    rows, errors = [], []
    for root in [*(WORK_ROOT / ns for ns in EXACT), QUEST_ROOT]:
        row, current = verify_pair(root)
        rows.append(row)
        errors.extend(current)
    result = {
        "scopes": rows,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write(WORK_ROOT / "specialized_validation.json", result)
    return result, errors


def audit() -> tuple[dict[str, object], list[str]]:
    instance = resolve_source_root()
    rows = []
    for target in family_goal.targets_for(FAMILY):
        jar = family_goal.find_jar(instance, target.jar_prefix)
        with ZipFile(jar) as archive:
            names = archive.namelist()
            advancements = [
                n for n in names if n.endswith(".json") and "/advancement" in n
            ]
            guides = [
                n
                for n in names
                if n.endswith((".json", ".md"))
                and any(t in n.lower() for t in ("guide", "book", "manual"))
            ]
        rows.append(
            {
                "jar": jar.name,
                "advancements": len(advancements),
                "guide_candidates": len(guides),
            }
        )
    visible = []
    pattern = re.compile(
        r"farmersdelight:|cookingforblockheads:|farmingforblockheads:", re.I
    )
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json", ".snbt"}:
            continue
        for number, line in enumerate(
            path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1
        ):
            if pattern.search(line) and any(
                t in line.lower()
                for t in ("name", "display", "tooltip", "lore", "text")
            ):
                visible.append(
                    f"{path.relative_to(instance).as_posix()}:{number}:{line.strip()}"
                )
    result = {
        "jars": rows,
        "kubejs_direct_display_lines": visible,
        "status": "complete",
    }
    write(WORK_ROOT / "surface_audit.json", result)
    return result, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("normalize", "verify", "audit"))
    args = parser.parse_args()
    if args.command == "normalize":
        report, errors = normalize(), []
    elif args.command == "verify":
        report, errors = verify()
    else:
        report, errors = audit()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
