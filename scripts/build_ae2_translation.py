#!/usr/bin/env python3
"""AE2 원문과 기존 번역을 비교해 검증된 누적 리소스팩 파일을 만든다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

from local_paths import resolve_source_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_LANG = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/ae2/lang/ko_kr.json"
)
PROGRESS_FILE = PROJECT_ROOT / "working/ae2/progress.json"
PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{\d+\}")

# 5.4 번역에서 반복되는 표기만 기계적으로 통일한다. 의미 변경은 OVERRIDES에서 처리한다.
TERM_REPLACEMENTS = (
    ("세르투스", "서투스"),
    ("Spatial", "공간"),
    ("시공", "공간"),
    ("액체", "유체"),
    ("저장고", "저장소"),
    ("패턴 제공기", "패턴 공급기"),
    ("패턴 공급자", "패턴 공급기"),
    ("보조처리", "보조 처리"),
    ("우선 순위", "우선순위"),
    ("포멧", "포맷"),
    ("엑세스", "액세스"),
    ("컨텐츠", "콘텐츠"),
    ("드랍", "드롭"),
    ("타겟", "대상"),
    ("p2p", "P2P"),
)

# 자동 치환으로 뜻을 보장할 수 없는 항목은 현재 영어 원문을 확인해 직접 교정한다.
OVERRIDES = {
    "achievement.ae2.ChargedQuartz": "충격적!",
    "achievement.ae2.Fluix": "부자연스러운 결정",
    "achievement.ae2.PatternTerminal": "제작의 거장",
    "achievement.ae2.Root": "Applied Energistics 2",
    "achievement.ae2.SpatialIO": "공간 조정",
    "achievement.ae2.SpatialIOExplorer.desc": "공간 저장 셀 안에 저장되기",
    "achievement.ae2.StorageCell": "상자보다 좋은 것",
    "ae2.rei_jei_integration.spatial_io_never_causes_any_decay": "공간 I/O를 사용해도 등급이 떨어지지 않습니다.",
    "block.ae2.cable_bus": "AE2 케이블 및/또는 버스",
    "block.ae2.growth_accelerator": "수정 성장 가속기",
    "block.ae2.pattern_provider": "ME 패턴 공급기",
    "chat.ae2.LastTransitionUnknown": "마지막 전환을 알 수 없음",
    "chat.ae2.UnsupportedUpgrade": "이 업그레이드는 이 기계에서 지원되지 않습니다.",
    "chat.ae2.When": "시점",
    "commands.ae2.usage": "Applied Energistics 2 명령어입니다. 목록은 /ae2 list, 명령어 도움말은 /ae2 help _____를 사용하세요.",
    "death.attack.matter_cannon": "%1$s이(가) %2$s에게 사살당했습니다",
    "death.attack.matter_cannon.item": "%1$s이(가) %2$s의 %3$s에 맞아 사망했습니다",
    "entity.ae2.tiny_tnt_primed": "점화된 소형 TNT",
    "entity.minecraft.villager.ae2.fluix_researcher": "플루익스 연구원",
    "gui.ae2.And": "및",
    "gui.ae2.CreativeTab": "Applied Energistics 2",
    "gui.ae2.CreativeTabFacades": "Applied Energistics 2 - 덮개",
    "gui.ae2.CompatibleUpgrades": "호환 업그레이드:",
    "gui.ae2.Crafts": "제작:",
    "gui.ae2.CraftingTerminal": "제작 터미널",
    "gui.ae2.EnergyLevelEmitter": "ME 에너지 레벨 방출기",
    "gui.ae2.LevelEmitter": "ME 레벨 방출기",
    "gui.ae2.NotSoMysteriousQuote": '"아무리 가까워도, 아직 멀다."',
    "gui.ae2.PatternTooltipSubstitutions": "대체 아이템을 사용합니다",
    "gui.ae2.Produces": "생산:",
    "gui.ae2.QuartzCuttingKnife": "석영 절단 칼",
    "gui.ae2.Set": "설정",
    "gui.ae2.With": "포함",
    "gui.ae2.inWorldCraftingPresses": "각인기 프레스는 신비한 큐브를 부수어 얻을 수 있습니다. 신비한 큐브는 세계 곳곳의 운석 중심부에서 찾을 수 있으며, 운석 탐지기로 위치를 파악할 수 있습니다.",
    "gui.tooltips.ae2.CpuStatusCraftedIn": "%s을(를) %s 만에 제작",
    "gui.tooltips.ae2.LockCraftingModeNone": "사용 안 함",
    "gui.tooltips.ae2.NonBlocking": "대상 인벤토리의 내용을 무시합니다.",
    "gui.tooltips.ae2.Off": "끔",
    "gui.tooltips.ae2.On": "켬",
    "gui.tooltips.ae2.Serial": "일련번호: %d",
    "gui.tooltips.ae2.StashToPlayerDesc": "제작 격자의 아이템을 플레이어 인벤토리로 가져옵니다.",
    "gui.tooltips.ae2.SupportedBy": "지원 장치:",
    "item.ae2.certus_quartz_cutting_knife": "서투스 석영 절단 칼",
    "item.ae2.dark_monitor": "어두운 발광 패널",
    "item.ae2.missing_content": "누락된 콘텐츠",
    "item.ae2.nether_quartz_cutting_knife": "네더 석영 절단 칼",
    "item.ae2.semi_dark_monitor": "발광 패널",
    "item.ae2.void_card": "초과분 파괴 카드",
    "item.ae2.wrapped_generic_stack": "포장된 일반 스택",
    "key.ae2.category": "Applied Energistics 2",
    "key.ae2.mouse_wheel_item_modifier": "마우스 휠 아이템 보조 키",
}


def load_zip_json(path: Path, entry: str) -> dict[str, str]:
    with zipfile.ZipFile(path) as archive:
        value = json.loads(archive.read(entry).decode("utf-8-sig"))
    if not isinstance(value, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in value.items()
    ):
        raise ValueError(f"문자열 JSON 객체가 아닙니다: {path}!{entry}")
    return value


def normalize(value: str) -> str:
    for old, new in TERM_REPLACEMENTS:
        value = value.replace(old, new)
    value = re.sub(r"조합(?!법)", "제작", value)
    value = value.replace("제작중", "제작 중")
    value = value.replace("아이템 당", "아이템당")
    value = re.sub(r"(\d+k) 유체 휴대용 셀", r"\1 휴대용 유체 셀", value)
    value = re.sub(r"(\d+k) 아이템 휴대용 셀", r"\1 휴대용 아이템 셀", value)
    return value


def validate_pair(key: str, source: str, translated: str) -> list[str]:
    errors = []
    if Counter(PLACEHOLDER_RE.findall(source)) != Counter(
        PLACEHOLDER_RE.findall(translated)
    ):
        errors.append(f"{key}: 자리표시자 불일치")
    if source.count("\n") != translated.count("\n"):
        errors.append(f"{key}: 줄바꿈 개수 불일치")
    return errors


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    jar = instance / "mods/appliedenergistics2-19.2.17.jar"
    legacy_pack = instance / "resourcepacks/all-the-mods-10_5.4_resourcepack.zip"

    english = load_zip_json(jar, "assets/ae2/lang/en_us.json")
    native = load_zip_json(jar, "assets/ae2/lang/ko_kr.json")
    legacy = load_zip_json(legacy_pack, "assets/ae2/lang/ko_kr.json")
    if set(english) != set(legacy):
        raise ValueError("7.1 영어와 5.4 한국어의 AE2 키 집합이 다릅니다.")
    unknown_overrides = set(OVERRIDES) - set(english)
    if unknown_overrides:
        raise ValueError(f"현재 원문에 없는 교정 키: {sorted(unknown_overrides)}")

    final = {key: OVERRIDES.get(key, normalize(legacy[key])) for key in english}
    errors = []
    batches = []
    keys = list(english)
    for number, start in enumerate(range(0, len(keys), 400), 1):
        batch_keys = keys[start : start + 400]
        batch_errors = []
        for key in batch_keys:
            batch_errors.extend(validate_pair(key, english[key], final[key]))
        batches.append(
            {
                "batch": number,
                "start_index": start,
                "end_index": start + len(batch_keys) - 1,
                "keys": len(batch_keys),
                "validation_errors": len(batch_errors),
                "status": "completed" if not batch_errors else "failed",
            }
        )
        errors.extend(batch_errors)
    if errors:
        raise ValueError("\n".join(errors))

    OUTPUT_LANG.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_LANG.write_text(
        json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    kept = sum(key in native and final[key] == native[key] for key in english)
    corrected = sum(key in native and final[key] != native[key] for key in english)
    new = sum(key not in native for key in english)
    progress = {
        "scope": "Applied Energistics 2 core (ae2 namespace)",
        "source_jar": jar.name,
        "total_keys": len(english),
        "native_ko_keys": len(native),
        "existing_korean_kept": kept,
        "existing_korean_corrected": corrected,
        "newly_completed": new,
        "remaining": 0,
        "batches": batches,
        "output": OUTPUT_LANG.relative_to(PROJECT_ROOT).as_posix(),
        "output_sha256": sha256(OUTPUT_LANG),
        "review_items": [],
    }
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(progress, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
