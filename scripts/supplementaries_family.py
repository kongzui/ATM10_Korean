#!/usr/bin/env python3
"""Supplementaries와 Amendments의 표시 문구를 현재 영어 원문으로 전면 재검수해요."""

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

FAMILY = "supplementaries_amendments"
ROOT = PROJECT_ROOT / "working" / FAMILY
LATIN = re.compile(r"[A-Za-z]{3,}")
NUMBER = re.compile(r"\d+(?:[.,/xX×]\d+)*")

SUPPLEMENTARIES_EXACT = {
    "tab.supplementaries.supplementaries": "Supplementaries",
    "trim_pattern.supplementaries.blast": "폭발 방어구 장식",
    "item.supplementaries.blast_armor_trim_smithing_template": "대장장이 형판",
    "block.supplementaries.gold_bars": "금 창살",
    "block.supplementaries.ash_bricks": "재 벽돌 블록",
    "item.supplementaries.bunting": "장식 깃발",
    "entity.supplementaries.plunderer": "노략꾼",
    "item.supplementaries.plunderer_spawn_egg": "노략꾼 생성 알",
    "commands.supplementaries.configs": "설정에 접근하려면 Configured를 설치하세요",
    "commands.supplementaries.configs_reloaded": "Supplementaries 설정을 다시 불러왔습니다!",
    "commands.supplementaries.record.start": "소리 블록 녹음을 시작했습니다",
    "commands.supplementaries.record.stop": "소리 블록 녹음을 중지하고 recorded_songs/%s에 노래를 저장했습니다",
    "painting.supplementaries.bombs.author": "Plantkillable",
    "painting.supplementaries.jar.author": "TestedBubble",
    "subtitles.supplementaries.aeugh": "복어가 괴상한 소리를 냄",
    "gui.supplementaries.optifine.message": (
        "계속하기 전에 OptiFine이 문제와 충돌을 일으키는 것으로 알려져 있다는 점을 확인하세요.\n\n"
        " OptiFine은 모드 환경에 적합하지 않으며 Forge 자체와도 심각한 호환성 문제가 여러 차례 있었습니다.\n\n"
        " 성능 면에서도 ModernFix, Embeddium, 셰이더용 Oculus처럼 훨씬 빠른 대안이 있습니다. \n\n"
        "모드 환경과 바닐라 환경 어느 쪽에서 플레이하든 아래에 나열된 모드를 대신 사용하는 것이 좋습니다."
    ),
}

COLORS = {
    "indigo": "남색",
    "turquoise": "터키석색",
    "teal": "암청록색",
    "royal_blue": "로열 블루",
    "navy": "네이비",
    "sky_blue": "하늘색",
    "azure": "하늘빛",
    "cerulean": "세룰리안",
    "cobalt": "코발트색",
    "sapphire": "사파이어색",
    "rose": "장미색",
    "crimson": "진홍색",
    "maroon": "고동색",
    "coral": "산호색",
    "salmon": "연어색",
    "peach": "복숭아색",
    "tan": "황갈색",
    "beige": "베이지색",
    "ginger": "생강색",
    "amber": "호박색",
    "olive": "올리브색",
    "forest": "숲색",
    "verdant": "선록색",
    "jade": "옥색",
    "emerald": "에메랄드색",
    "mint": "민트색",
    "aqua": "아쿠아색",
    "slate": "슬레이트색",
}

AMENDMENTS_EXACT = {
    "block.amendments.tool_hook": "도구 걸이",
    "item.amendments.dragon_charge": "드래곤 화염구",
    "block.amendments.candle_skull": "양초가 놓인 해골",
    "block.amendments.hanging_pot": "매달린 화분",
    "block.amendments.hanging_flower_pot": "매달린 꽃 화분",
    "block.amendments.double_cake": "겹 케이크",
    "block.amendments.ceiling_banner": "천장 현수막",
    "tag.item.amendments.goes_in_lectern": "독서대에 놓을 수 있음",
    "tag.item.amendments.goes_in_tripwire_hook": "철사덫 갈고리에 걸 수 있음",
    "tag.item.amendments.non_stackable_heads": "겹칠 수 없는 머리",
    "tag.item.amendments.sets_on_fire": "불을 붙임",
    "tag.moonlight.amendments.soft_fluid.can_glow": "빛날 수 있음",
    "tag.moonlight.amendments.soft_fluid.cant_boil": "끓일 수 없음",
    "tag.moonlight.amendments.soft_fluid.cant_extinguish": "불을 끌 수 없음",
    "tag.moonlight.amendments.soft_fluid.cant_go_in_liquid_cauldron": "액체 가마솥에 담을 수 없음",
    "tag.moonlight.amendments.soft_fluid.no_tint_in_cauldron": "가마솥에서 색조를 적용하지 않음",
}
for slug, value in COLORS.items():
    AMENDMENTS_EXACT[f"item.amendments.dye_bottle.{slug}"] = value

REPLACEMENTS = (
    ("레시피", "제작법"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("왼쪽 클릭", "좌클릭"),
    ("스미싱 템플릿", "대장장이 형판"),
    ("갑옷 트림", "방어구 장식"),
    ("배너", "현수막"),
    ("헤드", "머리"),
    ("글로우", "발광"),
    ("Noteblocks", "소리 블록"),
    ("글로브", "지구본"),
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
    for namespace, exact in (
        ("supplementaries", SUPPLEMENTARIES_EXACT),
        ("amendments", AMENDMENTS_EXACT),
    ):
        root = ROOT / namespace
        english, korean = load(root / "en_us.json"), load(root / "ko_kr.json")
        auto, sources = (
            load(root / "auto_candidates.json"),
            load(root / "candidate_sources.json"),
        )
        reviewed = {}
        for key in english:
            value = exact.get(key)
            if value is None:
                value = (
                    auto[key]
                    if sources[key] == "new_translation_required"
                    else korean[key]
                )
            reviewed[key] = transform(value)
        if namespace == "supplementaries":
            for key, source in english.items():
                if key.startswith("block.supplementaries.bunting_"):
                    reviewed[key] = (
                        transform(auto[key])
                        .replace("멧새", "장식 깃발")
                        .replace("번팅", "장식 깃발")
                    )
                    if not str(reviewed[key]).endswith("장식 깃발"):
                        reviewed[key] = str(reviewed[key]).replace("깃발", "장식 깃발")
        write(root / "ko_kr.json", reviewed)
        rows.append(
            {
                "namespace": namespace,
                "keys": len(reviewed),
                "reused": sum(v == "bundled_ko_kr" for v in sources.values()),
                "new": sum(v == "new_translation_required" for v in sources.values()),
            }
        )
    result = {"languages": rows, "status": "complete"}
    write(ROOT / "normalization.json", result)
    return result


def verify() -> tuple[dict[str, object], list[str]]:
    rows, errors = [], []
    for namespace in ("supplementaries", "amendments"):
        root = ROOT / namespace
        english, korean = load(root / "en_us.json"), load(root / "ko_kr.json")
        untranslated = []
        if list(english) != list(korean):
            errors.append(f"키 또는 순서 불일치: {namespace}")
        for key in english.keys() & korean.keys():
            source, target = english[key], korean[key]
            errors.extend(family_goal.validate_value(key, source, target))
            if isinstance(source, str) and isinstance(target, str):
                if Counter(NUMBER.findall(source)) != Counter(NUMBER.findall(target)):
                    errors.append(f"숫자 불일치: {namespace}:{key}")
                if (
                    source == target
                    and LATIN.search(source)
                    and not (
                        source
                        in {
                            "Supplementaries",
                            "Amendments",
                            "Plantkillable",
                            "TestedBubble",
                        }
                        or family_goal.is_allowed_original(source)
                        or key.startswith("jukebox_song.")
                        or key == "message.supplementaries.fluid_tooltip"
                    )
                ):
                    untranslated.append(key)
        if untranslated:
            errors.append(f"분류되지 않은 영어 유지: {namespace}:{untranslated[:20]}")
        rows.append(
            {"namespace": namespace, "keys": len(english), "untranslated": untranslated}
        )
    result = {
        "languages": rows,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write(ROOT / "specialized_validation.json", result)
    return result, errors


def audit() -> tuple[dict[str, object], list[str]]:
    instance = resolve_source_root()
    rows = []
    for target in family_goal.targets_for(FAMILY):
        jar = family_goal.find_jar(instance, target.jar_prefix)
        with ZipFile(jar) as archive:
            names = archive.namelist()
            rows.append(
                {
                    "jar": jar.name,
                    "advancements": sum(
                        n.endswith(".json") and "/advancement" in n for n in names
                    ),
                    "recipes": sum(
                        n.endswith(".json") and "/recipe" in n for n in names
                    ),
                }
            )
    result = {"jars": rows, "kubejs_direct_display_lines": [], "status": "complete"}
    write(ROOT / "surface_audit.json", result)
    return result, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("normalize", "verify", "audit"))
    args = parser.parse_args()
    report, errors = (
        (normalize(), [])
        if args.command == "normalize"
        else verify()
        if args.command == "verify"
        else audit()
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
