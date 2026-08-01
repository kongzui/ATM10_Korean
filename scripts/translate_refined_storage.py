#!/usr/bin/env python3
"""Refined Storage 2 계열의 수동 검수 번역과 반복 이름 규칙을 적용한다."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from five_family_goal import is_allowed_original
from local_paths import PROJECT_ROOT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/refined_storage"
OVERRIDES_FILE = WORK_ROOT / "manual_overrides.json"

NAMES = {
    "Cable": "케이블",
    "Disk Drive": "디스크 드라이브",
    "Machine Casing": "기계 케이싱",
    "Grid": "그리드",
    "Pattern Grid": "패턴 그리드",
    "Crafting Grid": "제작 그리드",
    "Controller": "컨트롤러",
    "Storage Block": "저장 블록",
    "Fluid Storage Block": "유체 저장 블록",
    "Chemical Storage Block": "화학 물질 저장 블록",
    "Energy Storage Block": "에너지 저장 블록",
    "Source Storage Block": "소스 저장 블록",
    "Soul Storage Block": "소울 저장 블록",
    "Importer": "반입기",
    "Exporter": "반출기",
    "Interface": "인터페이스",
    "External Storage": "외부 저장소",
    "Detector": "감지기",
    "Constructor": "설치기",
    "Destructor": "파괴기",
    "Wireless Transmitter": "무선 송신기",
    "Storage Monitor": "저장소 모니터",
    "Network Receiver": "네트워크 수신기",
    "Network Transmitter": "네트워크 송신기",
    "Portable Grid": "휴대용 그리드",
    "Security Manager": "보안 관리자",
    "Relay": "릴레이",
    "Disk Interface": "디스크 인터페이스",
    "Autocrafter": "자동 제작기",
    "Autocrafter Manager": "자동 제작기 관리자",
    "Autocrafting Monitor": "자동 제작 모니터",
    "Storage Part": "저장 부품",
    "Storage Disk": "저장 디스크",
    "Fluid Storage Part": "유체 저장 부품",
    "Fluid Storage Disk": "유체 저장 디스크",
    "Chemical Storage Part": "화학 물질 저장 부품",
    "Chemical Storage Disk": "화학 물질 저장 디스크",
    "Energy Storage Part": "에너지 저장 부품",
    "Energy Storage Disk": "에너지 저장 디스크",
    "Source Storage Part": "소스 저장 부품",
    "Source Storage Disk": "소스 저장 디스크",
    "Soul Storage Part": "소울 저장 부품",
    "Soul Storage Disk": "소울 저장 디스크",
    "Storage Housing": "저장소 하우징",
    "Advanced Storage Housing": "고급 저장소 하우징",
    "Advanced Machine Casing": "고급 기계 케이싱",
    "Wireless Grid": "무선 그리드",
    "Wireless Autocrafting Monitor": "무선 자동 제작 모니터",
    "Universal Grid": "통합 그리드",
    "Wireless Universal Grid": "무선 통합 그리드",
    "Network Card": "네트워크 카드",
    "Configuration Card": "설정 카드",
    "Security Card": "보안 카드",
    "Fallback Security Card": "기본 보안 카드",
    "Pattern": "패턴",
    "Crafting Pattern": "제작 패턴",
    "Processing Pattern": "처리 패턴",
    "Stonecutter Pattern": "석재 절단기 패턴",
    "Smithing Table Pattern": "대장장이 작업대 패턴",
    "Upgrade": "업그레이드",
    "Speed Upgrade": "속도 업그레이드",
    "Stack Upgrade": "스택 업그레이드",
    "Silk Touch Upgrade": "섬세한 손길 업그레이드",
    "Regulator Upgrade": "조절 업그레이드",
    "Range Upgrade": "범위 업그레이드",
    "Autocrafting Upgrade": "자동 제작 업그레이드",
    "Quartz Enriched Iron": "석영 농축 철",
    "Quartz Enriched Copper": "석영 농축 구리",
    "Processor Binding": "프로세서 결합재",
    "Silicon": "실리콘",
    "Basic Processor": "기본 프로세서",
    "Improved Processor": "개선된 프로세서",
    "Advanced Processor": "고급 프로세서",
    "Withering Processor": "위더링 프로세서",
    "Neural Processor": "신경 프로세서",
    "Construction Core": "설치 코어",
    "Destruction Core": "파괴 코어",
    "Wrench": "렌치",
    "Debug Stick": "디버그 막대",
    "Crafter": "제작기",
    "Advanced Crafter": "고급 제작기",
    "Iron Autocrafter": "철 자동 제작기",
    "Gold Autocrafter": "금 자동 제작기",
    "Diamond Autocrafter": "다이아몬드 자동 제작기",
    "Netherite Autocrafter": "네더라이트 자동 제작기",
    "Wireless Crafting Grid": "무선 제작 그리드",
    "Chemical Parts": "화학 물질 저장 부품",
    "Chemical Disks": "화학 물질 저장 디스크",
    "Chemical Blocks": "화학 물질 저장 블록",
    "Fluid Parts": "유체 저장 부품",
    "Fluid Disks": "유체 저장 디스크",
    "Fluid Blocks": "유체 저장 블록",
    "Storage Parts": "저장 부품",
    "Storage Disks": "저장 디스크",
    "Storage Blocks": "저장 블록",
    "Parts": "부품",
    "Disks": "디스크",
}

SIMPLE = {
    "All": "전체",
    "Allowlist": "허용 목록",
    "Blocklist": "차단 목록",
    "Cancel": "취소",
    "Cancel all": "모두 취소",
    "Cancelling": "취소 중",
    "Chained": "연결됨",
    "Clear": "지우기",
    "Completed": "완료",
    "Configure amount": "수량 설정",
    "Craft": "제작",
    "Crafting": "제작 중",
    "Debug": "디버그",
    "Default": "기본값",
    "Disks": "디스크",
    "Edit": "편집",
    "Empty filter": "빈 필터",
    "Empty pattern slot": "빈 패턴 슬롯",
    "Empty upgrade slot": "빈 업그레이드 슬롯",
    "Expand": "펼치기",
    "Extract": "꺼내기",
    "Extract only": "꺼내기만",
    "Fuzzy mode": "유사 일치 모드",
    "High": "높음",
    "Inactive": "비활성",
    "In": "입력",
    "Insert": "넣기",
    "Insert and extract": "넣기 및 꺼내기",
    "Insert only": "넣기만",
    "Large": "큼",
    "List": "목록",
    "Low": "낮음",
    "Max": "최대",
    "Medium": "중간",
    "Missing Network Card": "네트워크 카드 없음",
    "Mode": "모드",
    "Modified": "변경됨",
    "Name": "이름",
    "Never": "사용 안 함",
    "No permission": "권한 없음",
    "Notify": "알림",
    "Off": "꺼짐",
    "On": "켜짐",
    "Out": "출력",
    "Outputs": "출력",
    "Pass-through": "그대로 전달",
    "Pending": "대기 중",
    "Priority": "우선순위",
    "Processing": "처리 중",
    "Quantity": "수량",
    "Random": "무작위",
    "Ready": "준비됨",
    "Reset": "초기화",
    "Round robin": "순환",
    "Running": "실행 중",
    "Scheduled": "예약됨",
    "Security": "보안",
    "Set": "설정",
    "Small": "작음",
    "Start": "시작",
    "Stretch": "늘이기",
    "Tree": "트리",
    "Unreachable": "연결할 수 없음",
    "View type": "표시 유형",
    "Zoom": "확대/축소",
    "Energy usage": "에너지 사용량",
    "Energy capacity": "에너지 용량",
    "Resource type": "자원 유형",
    "Sorting direction": "정렬 방향",
    "Sorting type": "정렬 방식",
    "Search mode": "검색 모드",
    "Screen size": "화면 크기",
    "Smooth scrolling": "부드러운 스크롤",
    "Require energy": "에너지 필요",
    "Auto-selected search box": "검색창 자동 선택",
    "Autocrafting notification": "자동 제작 알림",
    "Autocrafting preview style": "자동 제작 미리 보기 형식",
    "Large font": "큰 글꼴",
    "Detailed tooltip": "자세한 툴팁",
    "Remember search query": "검색어 기억",
    "Synchronizer": "동기화 방식",
    "Crafting matrix close behavior": "제작 격자를 닫을 때의 동작",
    "Energy usage per disk": "디스크당 에너지 사용량",
    "Creative energy usage": "크리에이티브 에너지 사용량",
    "Open energy usage": "열기 에너지 사용량",
    "Insert energy usage": "넣기 에너지 사용량",
    "Extract energy usage": "꺼내기 에너지 사용량",
    "Base range": "기본 범위",
    "Input network energy usage": "입력 네트워크 에너지 사용량",
    "Output network energy usage (if not in pass through mode)": (
        "출력 네트워크 에너지 사용량(그대로 전달 모드가 아닐 때)"
    ),
    "Energy usage per pattern": "패턴당 에너지 사용량",
    "Cancel energy usage": "취소 에너지 사용량",
    "Cancel all energy usage": "전체 취소 에너지 사용량",
    "Crafting energy usage": "제작 에너지 사용량",
    "Autocrafting energy usage": "자동 제작 에너지 사용량",
    "Clear matrix energy usage": "제작 격자 비우기 에너지 사용량",
    "Recipe transfer energy usage": "조합법 전송 에너지 사용량",
    "Grid Type": "그리드 유형",
    "Tag Filter": "태그 필터",
    "Done": "완료",
    "Click to open advanced filter": "클릭하여 고급 필터 열기",
    "Import mode": "반입 모드",
    "Do not import": "반입하지 않음",
    "Import everything": "모두 반입",
    "Import outputs from inserted pattern": "삽입된 패턴의 결과물 반입",
    "Import only requested resources": "요청된 자원만 반입",
    "Import only requested resources including sub-ingredients": (
        "하위 재료를 포함하여 요청된 자원만 반입"
    ),
    "Change input sides (Cable Tiers)": "입력 면 변경(Cable Tiers)",
    "Allows changing the side from which resources are inserted in autocrafting.": (
        "자동 제작에서 자원이 들어오는 면을 변경할 수 있습니다."
    ),
    "The resources that will be inserted into the target inventory.": (
        "대상 인벤토리에 넣을 자원입니다."
    ),
    "None": "없음",
    "Down": "아래",
    "North": "북쪽",
    "South": "남쪽",
    "West": "서쪽",
    "East": "동쪽",
    "Is %s faster than a normal one and has a total of %s filter slots.": (
        "일반 장치보다 %s 빠르며 필터 슬롯이 총 %s개 있습니다."
    ),
    "Has a total of %s filter slots.": "필터 슬롯이 총 %s개 있습니다.",
    "Is %s faster than a normal one and has a total of %s input slots.": (
        "일반 장치보다 %s 빠르며 입력 슬롯이 총 %s개 있습니다."
    ),
    "Has a transfer quota multiplier of %s and a total of %s input/output slots.": (
        "전송 할당량 배수가 %s이고 입출력 슬롯이 총 %s개 있습니다."
    ),
    "Has a Stack Upgrade integrated.": "스택 업그레이드가 내장되어 있습니다.",
    "Cable Tiers Configuration": "Cable Tiers 설정",
    "Infinite": "무한",
    "Provides wireless network access for items like the Wireless Grid. Has infinite range and is cross-dimensional.": (
        "무선 그리드 같은 아이템으로 네트워크에 무선 접근할 수 있습니다. "
        "범위가 무한하고 차원을 넘어 연결됩니다."
    ),
    "Configuration for the Interdimensional Wireless Transmitter.": (
        "차원간 무선 송신기 설정입니다."
    ),
    "The energy usage of the Interdimensional Wireless Transmitter.": (
        "차원간 무선 송신기의 에너지 사용량입니다."
    ),
    "INTERDIMENSIONAL >>POWER<<": "차원을 넘나드는 >>힘<<",
    "Transmit a network signal with an Interdimensional Wireless Transmitter cross-dimensional with infinite range": (
        "차원간 무선 송신기로 범위 제한 없이 차원을 넘어 네트워크 신호를 전송하세요"
    ),
}


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def translate_name(value: str) -> str | None:
    if value in NAMES:
        return NAMES[value]
    format_prefix = ""
    format_suffix = ""
    rest = value
    prefix_match = re.match(r"^([&§][0-9A-FK-ORa-fk-or])", rest)
    if prefix_match:
        format_prefix = prefix_match.group(1)
        rest = rest[len(format_prefix) :]
    suffix_match = re.search(r"([&§][0-9A-FK-ORa-fk-or])$", rest)
    if suffix_match:
        format_suffix = suffix_match.group(1)
        rest = rest[: -len(format_suffix)]
    prefix = ""
    for english, korean in (
        ("Creative", "크리에이티브"),
        ("Advanced", "고급"),
        ("Elite", "엘리트"),
        ("Ultra", "울트라"),
        ("Mega", "메가"),
        ("Infinite", "무한"),
        ("Raw", "미가공"),
        ("Large", "대용량"),
    ):
        if rest.startswith(f"{english} "):
            prefix = f"{korean} "
            rest = rest.removeprefix(f"{english} ")
            break
    match = re.fullmatch(r"([0-9]+[kKmMbB]{0,2}) (.+)", rest)
    amount = ""
    if match:
        amount = f"{match.group(1)} "
        rest = match.group(2)
    translated = NAMES.get(rest)
    if not translated and rest.endswith("s"):
        translated = NAMES.get(rest[:-1])
    if not translated:
        return None
    return f"{format_prefix}{prefix}{amount}{translated}{format_suffix}"


def translate_config(value: str) -> str | None:
    tier_names = {
        "Elite": "엘리트",
        "Ultra": "울트라",
        "Mega": "메가",
        "Creative": "크리에이티브",
    }
    match = re.fullmatch(r"Tiered (.+)", value)
    if match:
        name = translate_name(match.group(1))
        if name:
            return f"등급별 {name}"
    match = re.fullmatch(r"Configuration for the tiered (.+)\.", value)
    if match:
        name = translate_name(match.group(1))
        if name:
            return f"등급별 {name} 설정입니다."
    match = re.fullmatch(r"(Elite|Ultra|Mega) Energy usage", value)
    if match:
        return f"{tier_names[match.group(1)]} 에너지 사용량"
    match = re.fullmatch(r"(Elite|Ultra|Mega|Creative) Speed", value)
    if match:
        return f"{tier_names[match.group(1)]} 속도"
    match = re.fullmatch(r"The speed of the (Elite|Ultra|Mega|Creative) (.+)\.", value)
    if match:
        name = translate_name(f"{match.group(1)} {match.group(2)}")
        if name:
            return f"{name}의 작동 속도입니다."
    match = re.fullmatch(r"(Elite|Ultra|Mega) Stack Upgrade Integrated", value)
    if match:
        return f"{tier_names[match.group(1)]} 스택 업그레이드 내장"
    match = re.fullmatch(
        r"If the Stack Upgrade is integrated in the " r"(Elite|Ultra|Mega) (.+)\.",
        value,
    )
    if match:
        name = translate_name(f"{match.group(1)} {match.group(2)}")
        if name:
            return f"{name}에 스택 업그레이드를 내장할지 설정합니다."
    match = re.fullmatch(
        r"(Elite|Ultra|Mega|Creative) Transfer Quota Multiplier", value
    )
    if match:
        return f"{tier_names[match.group(1)]} 전송 할당량 배수"
    match = re.fullmatch(
        r"The transfer quota multiplier by the "
        r"(Elite|Ultra|Mega|Creative) Interface\.",
        value,
    )
    if match:
        return f"{tier_names[match.group(1)]} 인터페이스의 전송 할당량 배수입니다."
    match = re.fullmatch(r"Configuration for the (.+)s?\.", value)
    if match:
        name = translate_name(match.group(1))
        if name:
            return f"{name} 설정입니다."
    match = re.fullmatch(r"The energy used by the (.+)\.", value)
    if match:
        name = translate_name(match.group(1))
        if name:
            return f"{name}이 사용하는 에너지입니다."
    match = re.fullmatch(r"The energy capacity of the (.+)\.", value)
    if match:
        name = translate_name(match.group(1))
        if name:
            return f"{name}의 에너지 용량입니다."
    match = re.fullmatch(r"The source used by the (.+)\.", value)
    if match:
        name = translate_name(match.group(1))
        if name:
            return f"{name}이 사용하는 소스입니다."
    match = re.fullmatch(r"([0-9]+[KkBb]?|Creative|Infinite) energy usage", value)
    if match:
        prefix = {"Creative": "크리에이티브", "Infinite": "무한"}.get(
            match.group(1), match.group(1)
        )
        return f"{prefix} 에너지 사용량"
    match = re.fullmatch(r"([0-9]+B|Infinite) source usage", value)
    if match:
        prefix = "무한" if match.group(1) == "Infinite" else match.group(1)
        return f"{prefix} 소스 사용량"
    match = re.fullmatch(r"(.+) energy usage", value)
    if match:
        name = translate_name(match.group(1))
        if name:
            return f"{name} 에너지 사용량"
    return None


def translated_value(
    key: str, value: object, overrides: dict[str, object]
) -> object | None:
    if key in overrides:
        return overrides[key]
    if not isinstance(value, str):
        return None
    return SIMPLE.get(value) or translate_name(value) or translate_config(value)


def preserve_line_break_style(source: object, target: object) -> object:
    """퀘스트 원문의 이스케이프 줄바꿈 형식을 번역에도 그대로 적용한다."""
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
    overrides = read_json(OVERRIDES_FILE) if OVERRIDES_FILE.is_file() else {}
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
            target = translated_value(key, source, overrides)
            if target is not None:
                korean[key] = preserve_line_break_style(source, target)
                sources[key] = "manual_translation"
                changed += 1
            elif isinstance(source, str) and is_allowed_original(source):
                korean[key] = source
                sources[key] = "reviewed_original"
            elif source == korean[key]:
                unresolved.append(key)
        write_json(korean_file, korean)
        write_json(sources_file, sources)
    report = {"changed": changed, "unresolved": unresolved}
    write_json(WORK_ROOT / "manual_translation_report.json", report)
    print(f"수동 번역 규칙 반영: {changed}키, 미해결 {len(unresolved)}키")
    for key in unresolved[:80]:
        print(f"- {key}")
    return 1 if unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
