#!/usr/bin/env python3
"""Modular Routers 언어 파일의 검수 번역을 적용한다."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from five_family_goal import is_allowed_original
from local_paths import PROJECT_ROOT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/modular_routers"
LANG_ROOT = WORK_ROOT / "modularrouters"
OVERRIDES_FILE = WORK_ROOT / "manual_overrides.json"

TRANSLATIONS = {
    "Tag Filter": "태그 필터",
    "Invalid camouflage block!": "사용할 수 없는 위장 블록입니다!",
    "Added player [%s]": "플레이어 [%s]을(를) 추가했습니다",
    "Player [%s] is already on this upgrade!": "플레이어 [%s]은(는) 이미 이 업그레이드에 등록되어 있습니다!",
    "Couldn't add player [%s] (internal error)": "플레이어 [%s]을(를) 추가하지 못했습니다(내부 오류)",
    "Security upgrade items full!": "보안 업그레이드의 플레이어 목록이 가득 찼습니다!",
    "Player [%s] is not on this uprade!": "플레이어 [%s]은(는) 이 업그레이드에 등록되어 있지 않습니다!",
    "Removed player [%s]": "플레이어 [%s]을(를) 제거했습니다",
    "✘ No Inventory": "✘ 인벤토리 없음",
    "✘ Not Loaded": "✘ 불러오지 않음",
    "✔ Target OK": "✔ 대상 정상",
    "✘ Out of Range": "✘ 범위 밖",
    "✘ Dimension Blacklisted": "✘ 차단된 차원",
    "JEI text": "JEI 문구",
    "General": "일반",
    "General client settings": "일반 클라이언트 설정",
    "Sound": "소리",
    "Sound settings": "소리 설정",
    "Modules": "모듈",
    "Config settings for Router Modules": "라우터 모듈 설정",
    "Routers": "라우터",
    "Config settings for Routers": "라우터 설정",
    "Module Energy Costs": "모듈 에너지 비용",
    "FE costs for Router Modules": "라우터 모듈의 FE 비용",
    "Always show settings in module tooltip?": "모듈 툴팁에 설정을 항상 표시할까요?",
    "Breaker XP drops?": "파괴기에서 경험치를 드롭할까요?",
    "Base Range for Extruder Mk1 (no Range Upgrades)": "압출기 Mk1 기본 범위(범위 업그레이드 없음)",
    "Hard Max Range for Extruder Mk1 (with Range Upgrades)": "압출기 Mk1 절대 최대 범위(범위 업그레이드 적용)",
    "Energy Upgrade storage increase": "에너지 업그레이드당 저장 용량 증가량",
    "Energy Upgrade transfer rate increase": "에너지 업그레이드당 전송 속도 증가량",
    "Fluid Module transfer rate mB/tick (no upgrades)": "유체 모듈 전송 속도(mB/틱, 업그레이드 없음)",
    "Base Range for Fluid Mk2 (no upgrades)": "유체 모듈 Mk2 기본 범위(업그레이드 없음)",
    "Hard Max Range for Fluid Mk2 (with upgrades)": "유체 모듈 Mk2 절대 최대 범위(업그레이드 적용)",
    "Highlight Camouflaged Routers?": "위장한 라우터를 강조 표시할까요?",
    "Fluid Upgrade increase in mB/tick": "유체 업그레이드당 증가량(mB/틱)",
    "Module bind sound volume": "모듈 연결 소리 음량",
    "Render items in transit?": "운반 중인 아이템을 표시할까요?",
    "Match by Block": "블록 기준 일치",
    "Match by Dropped Item(s)": "드롭 아이템 기준 일치",
    "Durability": "내구도",
    "Enchantment": "마법 부여",
    "Energy Level": "에너지 수준",
    "Fluid Level": "유체 수준",
    "Food Value": "음식 회복량",
    "No Item Tags": "아이템 태그 없음",
    "Armor Slots": "방어구 슬롯",
    "Ender Inventory": "엔더 인벤토리",
    "Main Inventory": "주 인벤토리",
    "Main Inventory (no Hotbar)": "주 인벤토리(단축바 제외)",
    "Offhand Slot": "보조 손 슬롯",
    "Select an Item Tag": "아이템 태그 선택",
    "Back": "뒤",
    "Whitelist\nThe module will run only if the filter matches.\nAn empty whitelist will never allow the module to run.": "허용 목록\n필터 조건이 일치할 때만 모듈이 작동합니다.\n빈 허용 목록에서는 모듈이 작동하지 않습니다.",
    "Blacklist\nThe module will not run if the filter matches.\nAn empty blacklist will always allow the module to run.": "차단 목록\n필터 조건이 일치하면 모듈이 작동하지 않습니다.\n빈 차단 목록에서는 모듈이 항상 작동합니다.",
    "Down": "아래",
    "Front": "앞",
    "Ignore Item Damage\nTreat damageable items of the same type but different damage levels as the same": "아이템 내구도 무시\n같은 종류의 아이템은 내구도가 달라도 동일하게 취급합니다",
    "Match Item Damage\nDistinguish between damageable items of the same type with different damage levels": "아이템 내구도 일치\n같은 종류의 아이템도 내구도가 다르면 구분합니다",
    "Ignore Item Components\nIgnore item component data on an item when matching": "아이템 구성 요소 무시\n일치 여부를 판단할 때 아이템 구성 요소 데이터를 무시합니다",
    "Match Item Components\nTake item component data, e.g. enchantments, into account when matching": "아이템 구성 요소 일치\n마법 부여 같은 아이템 구성 요소 데이터를 고려합니다",
    "Tag Matching Disabled": "태그 일치 꺼짐",
    "Tag Matching Enabled\nItems which share a common item tag with any item in the filter will match\nUse a Tag Filter for more precise item tag matching": "태그 일치 켜짐\n필터의 아이템과 같은 아이템 태그를 공유하면 일치합니다\n더 정밀하게 태그를 지정하려면 태그 필터를 사용하세요",
    "Left": "왼쪽",
    "Match Any\nAny item in the filter may match for the filter to match.\nUse this under most circumstances.": "하나라도 일치\n필터 안의 아이템 중 하나라도 맞으면 필터 조건이 일치합니다.\n대부분의 상황에서는 이 설정을 사용하세요.",
    "Match All\nALL items in the filter must match for the filter to match.\nUsed in specific circumstances, e.g. if you want to test for enchanted leather armor.": "모두 일치\n필터 안의 모든 아이템이 맞아야 필터 조건이 일치합니다.\n마법이 부여된 가죽 방어구를 판별할 때 같은 특정 상황에 사용합니다.",
    "None": "없음",
    "Always": "항상",
    "High": "높음",
    "Low": "낮음",
    "Never": "안 함",
    "Pulsed": "펄스",
    "Right": "오른쪽",
    "Always continue executing subsequent modules on this tick, regardless of whether this module did anything.": "이 모듈의 작동 여부와 관계없이 같은 틱에 다음 모듈을 계속 실행합니다.",
    "Always Continue": "항상 계속",
    "Don't execute any subsequent modules on this tick if this module did NOT do anything.": "이 모듈이 작동하지 않았다면 같은 틱에 다음 모듈을 실행하지 않습니다.",
    "Terminate on no Match": "불일치 시 중단",
    "Don't execute any subsequent modules on this tick if this module did something.": "이 모듈이 작동했다면 같은 틱에 다음 모듈을 실행하지 않습니다.",
    "Terminate on Match": "일치 시 중단",
    "Up": "위",
    "Right-click": "우클릭",
    "Right-click entity": "엔티티 우클릭",
    "Attack nearby entity": "주변 엔티티 공격",
    "Look Above": "위쪽 보기",
    "Look Below": "아래쪽 보기",
    "Look Level": "수평 보기",
    "Nearest in-range entity": "범위 내 가장 가까운 엔티티",
    "Random in-range entity": "범위 내 무작위 엔티티",
    "Round Robin in-range entities": "범위 내 엔티티 순환 선택",
    "Furthest First": "먼 곳부터",
    "Nearest First": "가까운 곳부터",
    "Random": "무작위",
    "Round Robin": "순환 분배",
    "Extend: §bWith redstone signal > 0": "확장: §b레드스톤 신호 > 0",
    "Extend: §bWith redstone signal = 15": "확장: §b레드스톤 신호 = 15",
    "Extend: §bWith redstone signal = 0": "확장: §b레드스톤 신호 = 0",
    "Extend: §bNever": "확장: §b안 함",
    "Transfer Direction: %s": "전송 방향: %s",
    "Transfer into Router": "라우터로 전송",
    "Transfer out of Router": "라우터에서 전송",
    "Damage": "내구도",
    "Components": "구성 요소",
    "Tags": "태그",
    "Middle-Click": "가운데 클릭",
    "▶ %d x %s": "▶ %d x %s",
    "Filter items by the item tags to which they belong.": "아이템이 속한 아이템 태그를 기준으로 필터링합니다.",
}


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def preserve_line_break_style(source: object, target: object) -> object:
    if isinstance(source, list) and isinstance(target, list):
        return [
            preserve_line_break_style(source_item, target_item)
            for source_item, target_item in zip(source, target)
        ]
    if not isinstance(source, str) or not isinstance(target, str):
        return target
    if source.count("\\n") == target.count("\n") and "\n" not in source:
        return target.replace("\n", "\\n")
    return target


def main() -> int:
    overrides = read_json(OVERRIDES_FILE)
    unresolved: list[str] = []
    changed = 0

    for english_file in sorted(WORK_ROOT.rglob("en_us.json")):
        root = english_file.parent
        korean_file = root / "ko_kr.json"
        sources_file = root / "candidate_sources.json"
        if not korean_file.is_file() or not sources_file.is_file():
            continue
        english = read_json(english_file)
        korean = read_json(korean_file)
        sources = read_json(sources_file)
        for key, source in english.items():
            target = overrides.get(key)
            if target is None and isinstance(source, str):
                target = TRANSLATIONS.get(source)
            if target is not None:
                korean[key] = preserve_line_break_style(source, target)
                sources[key] = "manual_translation"
                changed += 1
            elif source == korean[key]:
                if isinstance(source, str) and is_allowed_original(source):
                    sources[key] = "reviewed_original"
                else:
                    unresolved.append(key)

        write_json(korean_file, korean)
        write_json(sources_file, sources)
    report = {"changed": changed, "unresolved": unresolved}
    write_json(WORK_ROOT / "manual_translation_report.json", report)
    print(f"수동 검수 번역 반영: {changed}키, 미해결 {len(unresolved)}키")
    for key in unresolved:
        print(f"- {key}")
    return 1 if unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
