#!/usr/bin/env python3
"""Pipez·Modern Dynamics·XNet 계열의 검수 번역을 적용한다."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from five_family_goal import is_allowed_original
from local_paths import PROJECT_ROOT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/basic_logistics"
OVERRIDES_FILE = WORK_ROOT / "manual_overrides.json"

TRANSLATIONS = {
    "EV EU Cable": "EV EU 케이블",
    "Fluid Pipe": "유체 파이프",
    "HV EU Cable": "HV EU 케이블",
    "Item Pipe": "아이템 파이프",
    "LV EU Cable": "LV EU 케이블",
    "Machine Extender": "기계 확장기",
    "MV EU Cable": "MV EU 케이블",
    "Superconductor EU Cable": "초전도체 EU 케이블",
    "Item Pipes": "아이템 파이프",
    "Modern Dynamics Upgrades": "Modern Dynamics 업그레이드",
    "Ignore Damage": "내구도 무시",
    "Match Damage": "내구도 일치",
    "Ignore Mod": "모드 무시",
    "Include Listed Mods": "목록의 모드 포함",
    "Blacklist": "차단 목록",
    "Whitelist": "허용 목록",
    "Ignore Tag Data": "태그 데이터 무시",
    "Match Tag Data": "태그 데이터 일치",
    "Don't Include Similar Items": "비슷한 아이템 포함 안 함",
    "Include Similar Items": "비슷한 아이템 포함",
    "Maximum Amount Extracted per Operation": "작업당 최대 추출량",
    "Infinite": "무한",
    "Maximum Total Number of Items in Inventory": "인벤토리의 최대 아이템 총수",
    "Allow Over-sending": "과다 전송 허용",
    "Prevent Over-sending": "과다 전송 방지",
    "Disabled": "비활성화",
    "Enabled": "활성화",
    "Redstone Control": "레드스톤 제어",
    "High": "높음",
    "Ignored": "무시",
    "Low": "낮음",
    "Signal Required:": "필요한 신호:",
    "Control Status:": "제어 상태:",
    "Closest First": "가까운 곳부터",
    "Furthest First": "먼 곳부터",
    "Random": "무작위",
    "Round-Robin": "순환 분배",
    "Available": "사용 가능",
    "Press U in EMI/JEI/REI to view upgrades.": "EMI/JEI/REI에서 U 키를 눌러 업그레이드를 확인하세요.",
    "Damage": "내구도",
    "Invert": "반전",
    "Mod": "모드",
    "NBT": "NBT",
    "Similar": "비슷한 항목",
    "  Filters: %s": "  필터: %s",
    "Max Items Extracted": "최대 추출 아이템 수",
    "Max Items in Inventory": "인벤토리의 최대 아이템 수",
    "Hold %s for Details": "자세한 정보를 보려면 %s 키를 누르세요",
    "Shift": "Shift",
    "Oversending Mode": "과다 전송 모드",
    "Requires Advanced Behavior Upgrade": "고급 동작 업그레이드 필요",
    "Routing Mode": "경로 지정 모드",
    "Upgrade Slot": "업그레이드 슬롯",
    "Press U on an Attractor/Extractor/Filter": "유인기/추출기/필터에서 U 키를 누르면",
    "in EMI/JEI/REI to view available upgrades.": "EMI/JEI/REI에서 사용 가능한 업그레이드를 확인합니다.",
    "Stuffed %s": "포화 상태: %s",
    "Filter Slots: %s": "필터 슬롯: %s",
    "Base Fluid Transfer: %s": "기본 유체 전송량: %s",
    "Max Moved Items: %s": "최대 이동 아이템 수: %s",
    "Item Speed: %s": "아이템 속도: %s",
    "Item Transfer Frequency: %s": "아이템 전송 주기: %s",
    "Advanced Behavior: %s": "고급 동작: %s",
    "Total Fluid Transfer: %s": "총 유체 전송량: %s",
    "Upgrade Effects": "업그레이드 효과",
    "Up to %s supported": "최대 %s개 지원",
    "Attractor": "유인기",
    "Debug Tool": "디버그 도구",
    "Extractor": "추출기",
    "Filter": "필터",
    "Inhibitor": "억제기",
    "Wrench": "렌치",
    "Not": "아님",
    "Transferring %s items every %s tick(s)": "아이템 %s개를 %s틱마다 전송",
    "Transferring %s mB every tick": "매 틱 %s mB 전송",
    "Transferring %s FE every tick": "매 틱 %s FE 전송",
    "Transferring %s mB gas every tick": "매 틱 가스 %s mB 전송",
    "NBT: %s": "NBT: %s",
    "Pipe": "파이프",
    "The base block for automation in XNet": "XNet 자동화의 중심 블록입니다",
    "With this block you can connect multiple channels (controllers)": "이 블록으로 여러 채널(컨트롤러)을 연결할 수 있습니다",
    "Energy": "에너지",
    "Fluid": "유체",
    "Item": "아이템",
    "Logic": "논리",
    "Min": "최소",
    "Max": "최대",
    "Number of ticks for each operation": "작업당 틱 수",
    "Pri": "우선",
    "Insertion priority": "삽입 우선순위",
    "Rate": "속도",
    "extraction": "추출",
    "insertion": "삽입",
    "Max energy %s rate|(limited to %d per tick)": "최대 에너지 %s 속도|(틱당 %d로 제한)",
    "low": "낮음",
    "high": "높음",
    "Disable %s if energy|is too %s": "%s 비활성화:|에너지가 너무 %s일 때",
    "Fluid %s rate|(max %d mb)": "유체 %s 속도|(최대 %d mb)",
    "Disable %s if fluid|is too %s": "%s 비활성화:|유체가 너무 %s일 때",
    "Amount of items to extract|per operation": "작업당 추출할|아이템 수",
    "Disable %s if destination|inventory has too %s items": "%s 비활성화:|대상 인벤토리의 아이템이 너무 %s일 때",
    "BL": "차단",
    "Enable blacklist mode": "차단 목록 모드 활성화",
    "Tags": "태그",
    "Tag matching": "태그 일치",
    "Meta": "메타",
    "Metadata matching": "메타데이터 일치",
    "NBT matching": "NBT 일치",
    "Filter Index": "필터 인덱스",
    "<Off>": "<꺼짐>",
    "Input RS channel": "입력 레드스톤 채널",
    "Count inputs before output impulse": "출력 임펄스 전 입력 횟수",
    "Count ticks before output impulse": "출력 임펄스 전 틱 수",
    "Redstone:": "레드스톤:",
    "Redstone output value": "레드스톤 출력값",
    "Operator": "연산자",
    "Amount to compare with": "비교할 수량",
    "Output color": "출력 색상",
    "Impulse mode:": "임펄스 모드:",
    "If enabled, connector will output a short impulse|instead of a constant signal": "활성화하면 연결기가 일정한 신호 대신|짧은 임펄스를 출력합니다",
    "Length of impulse in ticks": "임펄스 길이(틱)",
    "Redstone mode:\nIgnored": "레드스톤 모드:\n무시",
    "Redstone mode:\nOff to activate": "레드스톤 모드:\n꺼지면 활성화",
    "Redstone mode:\nOn to activate": "레드스톤 모드:\n켜지면 활성화",
    "Do one operation\non a pulse": "펄스마다\n한 번 작업",
    "Set the name of this connector": "이 연결기의 이름을 설정합니다",
    "Copy this connector|to the clipboard": "이 연결기를|클립보드에 복사합니다",
    "Remove this connector": "이 연결기를 제거합니다",
    "Create a new connector|from the clipboard": "클립보드에서|새 연결기를 만듭니다",
    "Create": "생성",
    "Paste": "붙여넣기",
    "Channel %d": "채널 %d",
    "Enable processing on this channel": "이 채널의 처리를 활성화합니다",
    "Channel name": "채널 이름",
    "Remove this channel": "이 채널을 제거합니다",
    "Copy this channel to|the clipboard": "이 채널을|클립보드에 복사합니다",
    "Create a new channel|from the clipboard": "클립보드에서|새 채널을 만듭니다",
    "Facade is now mimicking %s": "파사드가 이제 %s을(를) 모방합니다",
    "Directions: ": "방향: ",
    "Cancel": "취소",
    "Name: ": "이름: ",
    "Connector: ": "연결기: ",
    "Block: ": "블록: ",
    "Position: ": "위치: ",
    "Pos": "위치",
    "Index": "인덱스",
    "(doubleclick to highlight)": "(두 번 클릭하여 강조)",
    "Priority": "우선순위",
    "Item distribution mode|Current:Priority": "아이템 분배 모드|현재: 우선순위",
    "Roundrobin": "순환 분배",
    "Item distribution mode|Current:Roundrobin": "아이템 분배 모드|현재: 순환 분배",
    "Ins": "삽입",
    "Insert items to|connected block": "연결된 블록에|아이템 삽입",
    "Ext": "추출",
    "Extract items from|connected block": "연결된 블록에서|아이템 추출",
    "First": "첫 슬롯",
    "Extract from first|available slot": "사용 가능한 첫 슬롯에서|추출",
    "Rnd": "무작위",
    "Extract from random slot": "무작위 슬롯에서 추출",
    "Order": "순서대로",
    "Extract from slots|in order": "슬롯 순서대로|추출",
    "Single": "한 개",
    "Items per operation|Single item": "작업당 아이템 수|한 개",
    "Stack": "한 스택",
    "Items per operation|Stack": "작업당 아이템 수|한 스택",
    "Count": "지정 수량",
    "Items per operation|Specified count": "작업당 아이템 수|지정 수량",
    "Output value when have input": "입력이 있을 때 값 출력",
    "Inverse input signal|0 -> specified value|1-15 -> 0": "입력 신호 반전|0 -> 지정값|1-15 -> 0",
    "Apply to input signal|logical OR operation": "입력 신호에|논리 OR 연산 적용",
    "Apply to input signal|logical AND operation": "입력 신호에|논리 AND 연산 적용",
    "Apply to input signal|logical NOR operation": "입력 신호에|논리 NOR 연산 적용",
    "Apply to input signal|logical NAND operation": "입력 신호에|논리 NAND 연산 적용",
    "Apply to input signal|logical XOR operation": "입력 신호에|논리 XOR 연산 적용",
    "Apply to input signal|logical XNOR operation": "입력 신호에|논리 XNOR 연산 적용",
    "Toggles the output signal|every time it receives|an input signal": "입력 신호를 받을 때마다|출력 신호를|전환합니다",
    "Outputs signal every|time it receives specified|count input signals": "지정한 횟수만큼|입력 신호를 받을 때마다|신호를 출력합니다",
    "Outputs signal every|specified count game ticks|normally 20 ticks = 1 sec": "지정한 게임 틱마다|신호를 출력합니다|일반적으로 20틱 = 1초",
    "Always outputs the specified value": "항상 지정한 값을 출력합니다",
    "Sensor": "센서",
    "Sensor connected block|and output redstone signal": "연결된 블록을 감지하고|레드스톤 신호 출력",
    "Output": "출력",
    "Output redstone signal|to connected block": "연결된 블록으로|레드스톤 신호 출력",
    "Off": "꺼짐",
    "Not used": "사용 안 함",
    "Scans the number of items|in connected inventory|Target item can be set|in right field": "연결된 인벤토리의|아이템 수를 감지합니다|오른쪽 칸에서|대상 아이템 설정 가능",
    "Scans the amount of fluid|in connected block (mb)": "연결된 블록의|유체 양을 감지합니다(mb)",
    "Scans the amount of energy|in connected block": "연결된 블록의|에너지 양을 감지합니다",
    "Rs": "레드스톤",
    "Scans redstone signal|in connected block": "연결된 블록의|레드스톤 신호를 감지합니다",
    "The block is now highlighted": "블록을 강조 표시했습니다",
    "Copied channel": "채널을 복사했습니다",
    "Really remove channel %d?": "채널 %d을(를) 정말 제거할까요?",
    "Nothing selected!": "선택한 항목이 없습니다!",
    "Error copying to clipboard!": "클립보드에 복사하지 못했습니다!",
    "Error reading from clipboard!": "클립보드에서 읽지 못했습니다!",
    "Clipboard too large!": "클립보드 내용이 너무 큽니다!",
    "Unsupported channel type: %s!": "지원하지 않는 채널 유형: %s!",
    "Sneak right click this on a|normal connector to upgrade it|to an advanced connector": "일반 연결기에 이 아이템을 들고|웅크린 채 우클릭하면|고급 연결기로 업그레이드합니다",
    "Connector was upgraded": "연결기를 업그레이드했습니다",
    "This connector is already advanced!": "이 연결기는 이미 고급 등급입니다!",
    "Use this item on a connector to upgrade it!": "연결기에 이 아이템을 사용하여 업그레이드하세요!",
    "Edit channel %d|Type: %s": "채널 %d 편집|유형: %s",
    "Edit channel %d": "채널 %d 편집",
}


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
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
                source_text = "\n".join(source) if isinstance(source, list) else source
                if isinstance(source_text, str) and is_allowed_original(source_text):
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
