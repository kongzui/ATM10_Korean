#!/usr/bin/env python3
"""현재 MI JAR의 GuideME 가이드 전체를 한국어로 재검수해 생성한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

from five_family_goal import PROJECT_ROOT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/modern_industrialization/guides"
OUTPUT_ROOT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/modern_industrialization/mi_guidebook/_ko_kr"
)
JAR_PREFIX = "assets/modern_industrialization/mi_guidebook/"

HEADINGS = {
    "Introduction": "소개",
    "Modern Industrialization": "Modern Industrialization",
    "The Electric Age": "전기 시대",
    "Electric Machines": "전기 기계",
    "Advanced Pipe Configuration": "고급 파이프 설정",
    "Portable Storage Unit": "휴대용 저장 유닛",
    "Advanced Machines": "고급 기계",
    "Aluminum": "알루미늄",
    "Redstone Control Modules": "레드스톤 제어 모듈",
    "Overclock Upgrades": "오버클럭 업그레이드",
    "Electric Blast Furnace": "전기 용광로",
    "Better Multiblocks": "더 나은 멀티블록",
    "Electric Quarry": "전기 채석기",
    "Advanced Large Steam Boiler": "고급 대형 증기 보일러",
    "Electricity Generation": "전력 생산",
    "Electricity": "전기",
    "Diesel Jetpack and Tools": "디젤 제트팩과 도구",
    "Large Steam Boiler": "대형 증기 보일러",
    "Large Tank": "대형 탱크",
    "Making Cables": "케이블 만들기",
    "Oil Processing": "석유 처리",
    "Endgame": "최종 단계",
    "The Endgame": "최종 단계",
    "Fusion": "핵융합",
    "FUUUUUSION": "핵융합",
    "Fusion Reactor": "핵융합로",
    "Plasma Turbine": "플라즈마 터빈",
    "Gravichestplate": "중력 흉갑",
    "Quantum Tier": "양자 등급",
    "Midgame": "중반",
    "The Midgame": "중반",
    "Better Diesel": "더 나은 디젤",
    "HV Diesel Generator": "HV 디젤 발전기",
    "Large Diesel Generator": "대형 디젤 발전기",
    "Fluid Pipe Transfer Rates": "유체 파이프 전송 속도",
    "Fluid Pipe Speed": "유체 파이프 속도",
    "High Pressure!": "고압!",
    "Pressurizer": "가압기",
    "HP Large Steam Boiler": "고압 대형 증기 보일러",
    "HP Advanced Large Steam Boiler": "고압 고급 대형 증기 보일러",
    "Large Steam Turbine": "대형 증기 터빈",
    "Heat Exchanger": "열교환기",
    "HV Steam Turbine": "HV 증기 터빈",
    "Implosion Compressor!": "폭발 압축기!",
    "A Familiar Blue Gem": "익숙한 파란 보석",
    "Nuclear Reactor": "원자로",
    "The Nuclear Reactor": "원자로",
    "Stainless Steel": "스테인리스강",
    "Vacuum Freezer": "진공 냉각기",
    "Distillation Tower": "증류탑",
    "Upgrades!": "업그레이드!",
    "Machine Hull Upgrades": "기계 외피 업그레이드",
    "Overdrive Modules": "오버드라이브 모듈",
    "The Steam Age": "증기 시대",
    "Heating Water": "물 데우기",
    "Hot Water": "물 데우기",
    "Making Coke": "코크스 만들기",
    "Do You Like Coke?": "코크스가 좋나요?",
    "Coke Oven!": "코크스로!",
    "Getting Started": "시작하기",
    "First Bronze!": "첫 청동!",
    "Your First Bronze!": "첫 청동!",
    "Pipes": "파이프",
    "Fluid Pipes": "유체 파이프",
    "Item Pipes": "아이템 파이프",
    "Important Note": "중요 참고 사항",
    "Note": "참고 사항",
    "Unlimited Resources?": "무제한 자원?",
    "Infinite Resources?": "무한 자원?",
    "Steam Quarry": "증기 채석기",
    "The Steam Quarry": "증기 채석기",
    "Steam Machines": "증기 기계",
    "First Steel": "첫 강철",
    "Your First Steel": "첫 강철",
    "Steel Upgrade": "강철 업그레이드",
    "Upgrading To Steel": "강철로 업그레이드",
    "Tanks and Barrels": "탱크와 배럴",
    "Tanks & Barrels": "탱크와 배럴",
    "Infinite Water?": "무한한 물?",
    "E = mc²": "E = mc²",
}

REPLACEMENTS = (
    ("발전된", "고급"),
    ("고도로 고급", "초고급"),
    ("포지 해머", "단조 망치"),
    ("조합기", "조립기"),
    ("조합법", "제작법"),
    ("레시피", "제작법"),
    ("기계 껍데기", "기계 외피"),
    ("채광용 드릴", "채굴 드릴"),
    ("채광 드릴", "채굴 드릴"),
    ("채광", "채굴"),
    ("액체 파이프", "유체 파이프"),
    ("액체 반입", "유체 입력"),
    ("액체 반출", "유체 출력"),
    ("아이템 반입", "아이템 입력"),
    ("아이템 반출", "아이템 출력"),
    ("에너지 반입", "에너지 입력"),
    ("에너지 반출", "에너지 출력"),
    ("반입면", "입력면"),
    ("반출면", "출력면"),
    ("반입", "입력"),
    ("반출", "출력"),
    ("자동 반출", "자동 출력"),
    ("선재압연기", "선재 압연기"),
    ("원자력 발전소", "원자로"),
    ("원자력 합금", "핵 합금"),
    ("원자력 케이싱", "핵 합금 케이싱"),
    ("원자력 아이템 해치", "원자로 아이템 해치"),
    ("원자력 액체 해치", "원자로 유체 해치"),
    ("융합 원자로", "핵융합로"),
    ("이중수소", "중수소"),
    ("퀀텀", "양자"),
    ("데미지", "피해"),
    ("정맣", "정말"),
    ("없에", "없애"),
    ("고압 뮬", "고압수"),
    ("원요", "원유"),
    ("함쳐", "합쳐"),
    ("필요없", "필요 없"),
    ("한동안은", "잠시 동안은"),
    ("20배 더 효율적으로", "10배 더 효율적으로"),
)

NEW_PROSE = {
    "electric_age.md": [
        "증기를 새로운 에너지로 바꿀 수 있다는 사실을 발견했습니다. 이 혁신으로 기계는 훨씬 복잡하고 빠르게 작동합니다. **전기 시대**에 오신 것을 환영합니다!"
    ],
    "endgame.md": [
        "여기까지 왔다면 Modern Industrialization의 가장 강력한 기술을 사용할 준비가 된 것입니다.",
        "양자 기술과 핵융합을 활용하여 산업의 마지막 단계에 도전하세요.",
    ],
    "midgame.md": [
        "전기 생산과 자동화가 안정되었다면 더 높은 전압, 고압 증기와 원자력 기술로 나아갈 차례입니다.",
        "중반의 설비는 이후 최종 단계까지 계속 확장하여 사용할 수 있습니다.",
    ],
    "steam_age.md": [
        "증기 시대에는 첫 공장을 세우고 이후 전기 시대에 필요한 자원을 생산합니다. 자원 관리와 처리 시간 최적화가 핵심입니다."
    ],
    "index.md": [
        "**Modern Industrialization**에 오신 것을 환영합니다!",
        "Modern Industrialization은 자동화 모드입니다! 언젠가는 모든 자원을 자동화할 수 있고, 또 자동화해야 합니다.",
        "진행은 게임 초반의 **증기 시대**와 그 이후로 나뉩니다. 증기 시대에는 두 번째 단계에 필요한 자원을 생산할 첫 공장을 만듭니다. 이 단계에서는 자원 관리와 처리 시간 최적화가 중요합니다.",
        "증기 시대를 마치면 대부분의 설비가 쓸모없어지므로 너무 많은 노력을 들이지 마세요.",
        "두 번째 단계는 **전기 시대**입니다. 이 단계에서는 모든 처리 공정을 적극적으로 자동화하는 것이 좋습니다.",
        "전기 시대의 설비는 계속 업그레이드할 수 있으므로 영구적으로 사용할 수 있습니다. 전기 기계의 오버클럭 시스템은 소비량에 맞춰 생산량이 자동으로 늘어나게 합니다.",
        "효율적이고 균형 잡힌 처리 공정을 만들고 가장 유용한 공정을 먼저 구축하는 것이 과제입니다.",
        "전기 기계는 계속 작동할 때 성능을 온전히 발휘합니다. AE2나 Refined Storage 같은 주문형 자동화 모드와 함께 사용하면 진행이 매우 느리고 비효율적이므로 **강력히 권장하지 않습니다**.",
    ],
    "electric_age/config_card.md": [
        "설정 카드는 파이프를 위장하고 아이템 파이프의 설정을 복사하는 데 사용합니다.",
        "카드를 보조 손에 들고 있으면 새로 설치하는 아이템 파이프에 설정이 자동으로 적용됩니다.",
    ],
    "electric_age/portable_storage_unit.md": [
        "휴대용 저장 유닛(PSU)은 인벤토리에서 에너지를 운반하는 장치입니다. 저장 유닛을 우클릭하여 충전하거나 방전할 수 있습니다.",
        "기본 상태에서는 에너지 용량이 없습니다. 배터리로 PSU를 우클릭하거나 PSU로 배터리를 우클릭하여 배터리를 넣으면 용량이 생깁니다. 높은 등급의 배터리일수록 더 많은 용량을 추가합니다. 빈 슬롯을 우클릭하면 배터리를 되찾을 수 있지만, 남는 에너지는 사라집니다.",
    ],
}

# 현재 영어판에서 추가·변경된 문단을 기존 한국어 후보와 결합하는 계획이다.
# 정수는 검수한 기존 한국어 문단의 인덱스이고, 문자열은 새 확정 번역이다.
PLANS: dict[str, list[int | str | tuple[int, ...]]] = {
    "electric_age/advanced_machines.md": [
        0,
        1,
        2,
        3,
        (4, 5),
        "설정 가능한 탱크는 설정 가능한 상자의 유체 버전입니다.",
        "설정 가능한 슬롯 9개는 각각 16양동이를 저장할 수 있고 자동 출력 기능도 있습니다. 여러 유체를 자동화할 때 유용합니다!",
    ],
    "electric_age/basic_machines.md": [
        "전기 기계는 증기 기계와 같은 작업을 하지만 증기 대신 전기를 사용하며 제작법을 최대 32 EU/t까지 점진적으로 오버클럭합니다.",
        "REI에서 익숙한 기계의 전기 버전 제작법을 확인할 수 있습니다.",
        "윤활유는 크레오소트와 레드스톤을 혼합하여 얻는 유체입니다. 윤활유 양동이 같은 용기로 전기 기계를 우클릭하면 수동으로 오버클럭합니다.",
        "윤활유 25 mb마다 기계에 오버클럭 효율 틱 1회를 추가합니다.",
        "설정 가능한 상자는 기계가 아니지만 아날로그 회로를 만들면 제작할 수 있습니다!",
        "설정 가능한 슬롯 27개와 자동 출력 기능이 있어 자동화에 매우 유용합니다!",
        "자화기는 물질을 자화합니다. 제작법은 많지 않지만 모터 자동화에 유용합니다!",
        "가장 먼저 많이 만들 기계입니다! 조립기는 거의 모든 제작법을 자동화하며 슬롯 고정을 사용하면 조립기 하나에서 최대 3개를 처리할 수 있습니다.",
        "기계 외피, 아날로그 회로, 모터, 피스톤, 로봇 팔과 컨베이어 벨트를 조립기로 빨리 자동화하세요. 전기 기계 제작이 사실상 무료가 됩니다!",
        "레드스톤 제어 모듈은 레드스톤 신호로 전기 기계와 멀티블록의 동작을 제어합니다.",
        "손에 든 모듈을 설정한 뒤 기계나 멀티블록 제어기에 넣으세요.",
        "일반 전기 기계의 오버클럭 상한은 32 EU/t이고 전기 멀티블록의 상한은 128 EU/t입니다.",
        "기계나 멀티블록 메뉴에 업그레이드를 넣어 최대 오버클럭을 높이세요! 정확한 증가량은 REI에서 확인할 수 있습니다.",
    ],
    "electric_age/electricity.md": [
        0,
        1,
        "모든 전기 케이블에는 전송 가능한 EU/t와 연결 가능한 기계를 정하는 등급이 있습니다. 구리·은·주석은 LV, 백동·일렉트럼은 MV 등급입니다...",
        "디젤 발전기는 증기 터빈의 대안입니다. 여러 연료로 전기를 생산하며 현재는 크레오소트를 태울 수 있습니다. 사용할 수 있는 연료는 REI에서 확인하세요.",
        3,
        4,
        5,
        "낮은 등급에서 높은 등급으로 바꾸는 변압기(예: LV→MV)는 입력 5개와 출력 1개가 있습니다. 높은 등급에서 낮은 등급으로 바꾸는 변압기(예: MV→LV)는 입력 1개와 출력 5개가 있습니다.",
    ],
    "electric_age/jetpack.md": [(0, 1), 2, 3, 4, 5],
    "electric_age/large_steam_boiler.md": [
        0,
        "단일 블록 보일러와 달리 대형 증기 보일러는 사용하지 않은 열의 80%를 잃습니다. 최대 출력보다 적게 사용하면 연료당 생산 에너지가 크게 줄어드므로 최대 출력으로 계속 가동하는 것이 좋습니다.",
        1,
        2,
        3,
        4,
        5,
    ],
    "electric_age/large_tank.md": [
        0,
        "대형 탱크는 필요한 용량에 따라 여러 크기로 만들 수 있습니다. 제어기의 버튼을 눌러 크기 설정 패널을 여세요.",
        "제어기 또는 대형 탱크 해치를 통해 연결한 파이프만 탱크에 접근할 수 있습니다.",
        3,
        "대형 탱크 해치는 대형 탱크 블록의 연장 장치입니다. 우클릭하여 대형 탱크 메뉴를 열 수 있고, 연결한 파이프는 탱크 저장소에 직접 접근합니다.",
    ],
    "lategame/quantum_tier.md": [0, (1, 2), 3, 4, 5, 6, 7],
    "midgame/fluid_transfer.md": [
        0,
        1,
        "Modern Industrialization의 일반 탱크와 대형 탱크도 양방향 연결로 파이프 네트워크에 연결하면 내부 저장소를 공유합니다. 메뉴의 I/O 또는 파이프의 양방향 화살표가 양방향 연결입니다.",
        "탱크의 내부 버퍼는 파이프보다 훨씬 커서 더 많은 유체를 저장합니다.",
        2,
        "I/O 연결을 사용한 강철 탱크 하나(16양동이)를 추가하면 네트워크 전송량이 총 41000 mb/t가 됩니다.",
        3,
    ],
    "midgame/high_pressure.md": [
        0,
        1,
        "고압 증기 1밀리버킷은 일반 증기 8 mb, 즉 8 EU에 해당합니다.",
        "나중에는 고압 대형 증기 보일러의 고급 버전도 만들 수 있습니다.",
        3,
        4,
        5,
    ],
    "midgame/nuclear_reactor.md": [
        0,
        "원자로에서 전력을 생산하려면 원자로 유체 해치에 물을 넣으세요. 물은 증기로 바뀌며, 필요하면 열교환기를 거쳐 전력을 생산할 수 있습니다.",
        "원자로는 플루토늄 같은 일부 물질을 생산하는 유일한 방법이기도 합니다.",
        "또한 핵융합에 사용하는 중수소와 삼중수소를 생산할 수 있습니다.",
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
    ],
    "midgame/stainless_steel.md": [
        0,
        1,
        2,
        3,
        "다음은 가장 작은 증류탑과 가장 큰 증류탑을 나란히 놓은 예시입니다.",
        "크기가 2인 증류탑은 제작법의 첫 번째 산출물만 내고, 크기가 3이면 첫 두 산출물을 내는 식으로 늘어납니다...",
    ],
    "steam_age/coke_oven.md": [
        0,
        1,
        2,
        "크레오소트를 수집하려면 유체 출력 해치를 선택 사항으로 추가하세요.",
        3,
        "크레오소트는 확률 산출물이므로 유체 출력 해치에 공간이 없으면 사라집니다.",
        4,
        5,
        6,
        7,
        8,
        9,
    ],
    "steam_age/making_bronze.md": [
        "먼저 단조 망치에서 구리와 주석 주괴(조각)를 두드려 구리와 주석 (작은) 가루를 만드세요. 두 가루를 합치면 청동 (작은) 가루가 됩니다. 이 과정은 [혼합기](./steam_machines.md)에서 더 효율적입니다.",
        "작은 가루 9개가 가루 하나라는 점을 항상 기억하세요.",
        1,
    ],
    "steam_age/steam_machines.md": [
        "이제 청동 기계를 만들 차례입니다. 보일러는 틱당 최대 8밀리버킷의 증기를 자동으로 생산해 인접한 기계로 보냅니다.",
        "청동 기계는 최대 2 EU/t의 제작법을 처리합니다. 증기 1밀리버킷은 1 EU이므로 최대 온도의 보일러 하나로 기계 4대를 동시에 가동할 수 있습니다!",
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
    ],
    "steam_age/steel_machines.md": [
        0,
        1,
        "강철 업그레이드를 든 채 청동 기계를 웅크리고 우클릭하여 바로 적용할 수도 있습니다.",
        2,
        3,
        "강철 탱크는 최대 16양동이를 저장합니다.",
        "모든 제작법은 REI에서 확인할 수 있습니다!",
        6,
        7,
        8,
        9,
        "또한 기계의 유체 탱크 위에 쓰레기통을 들고 클릭하면 그 탱크를 쓰레기통에 바로 비울 수 있습니다.",
    ],
    "steam_age/tanks.md": [
        0,
        1,
        2,
        3,
        "설치한 배럴을 우클릭하면 한 스택을 넣습니다(Shift를 누르면 가능한 만큼 넣음).",
        "설치한 배럴을 좌클릭하면 한 스택을 꺼냅니다(Shift를 누르면 아이템 하나만 꺼냄).",
        4,
        5,
        6,
    ],
}


def load_local_paths() -> dict[str, object]:
    return json.loads((PROJECT_ROOT / "local_paths.json").read_text(encoding="utf-8"))


def find_jar() -> Path:
    paths = load_local_paths()
    root = paths.get("source_root") or paths.get("game_root")
    if not isinstance(root, str):
        raise FileNotFoundError("source_root 또는 game_root가 설정되지 않았습니다.")
    jars = sorted((Path(root) / "mods").glob("Modern-Industrialization-*.jar"))
    if len(jars) != 1:
        raise FileNotFoundError(f"MI JAR을 하나로 확정할 수 없습니다: {jars}")
    return jars[0]


def normalize_candidate(text: str) -> str:
    for before, after in REPLACEMENTS:
        text = text.replace(before, after)
    return text


def prose_lines(text: str) -> list[str]:
    result = []
    front = False
    for index, line in enumerate(text.splitlines()):
        if index == 0 and line == "---":
            front = True
            continue
        if front:
            if line == "---":
                front = False
            continue
        stripped = line.strip()
        if stripped and not stripped.startswith(("<", "!", "#", "---")):
            result.append(stripped)
    return result


def planned_prose(relative: str, bundled: str | None, count: int) -> list[str]:
    if relative in NEW_PROSE:
        values = NEW_PROSE[relative]
    else:
        if bundled is None:
            raise ValueError(f"번들 후보와 신규 번역이 모두 없습니다: {relative}")
        candidates = [normalize_candidate(value) for value in prose_lines(bundled)]
        plan = PLANS.get(relative, list(range(len(candidates))))
        values = []
        for item in plan:
            if isinstance(item, int):
                values.append(candidates[item])
            elif isinstance(item, tuple):
                values.append(" ".join(candidates[index] for index in item))
            else:
                values.append(item)
    if len(values) != count:
        raise ValueError(f"가이드 문단 수 불일치: {relative}:{len(values)} != {count}")
    return values


def translate_page(relative: str, english: str, bundled: str | None) -> str:
    expected_prose = prose_lines(english)
    translated_prose = iter(planned_prose(relative, bundled, len(expected_prose)))
    result = []
    front = False
    for index, line in enumerate(english.splitlines()):
        if index == 0 and line == "---":
            front = True
            result.append(line)
            continue
        if front:
            if line == "---":
                front = False
                result.append(line)
                continue
            match = re.fullmatch(r'(\s*title:\s*)"(.+)"', line)
            if match:
                title = HEADINGS.get(match.group(2), match.group(2))
                result.append(f'{match.group(1)}"{title}"')
            else:
                result.append(line)
            continue
        stripped = line.strip()
        if stripped.startswith("#"):
            prefix, title = re.match(r"^(#+\s+)(.*)$", stripped).groups()
            result.append(prefix + HEADINGS.get(title, title))
        elif stripped and not stripped.startswith(("<", "!", "---")):
            result.append(next(translated_prose))
        else:
            result.append(line)
    return normalize_candidate("\n".join(result).rstrip("\n") + "\n")


def build() -> dict[str, object]:
    jar = find_jar()
    pages: dict[str, str] = {}
    bundled_pages: dict[str, str] = {}
    with zipfile.ZipFile(jar) as archive:
        for name in archive.namelist():
            if not name.endswith(".md"):
                continue
            if name.startswith(JAR_PREFIX + "_ko_kr/"):
                bundled_pages[name[len(JAR_PREFIX + "_ko_kr/") :]] = archive.read(
                    name
                ).decode("utf-8")
            elif name.startswith(JAR_PREFIX) and "/_" not in name:
                pages[name[len(JAR_PREFIX) :]] = archive.read(name).decode("utf-8")
    for relative, english in pages.items():
        translated = translate_page(relative, english, bundled_pages.get(relative))
        for root in (WORK_ROOT / "ko_kr", OUTPUT_ROOT):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(translated, encoding="utf-8")
    report = {
        "jar": str(jar),
        "english_pages": len(pages),
        "bundled_candidates_reviewed": len(bundled_pages),
        "new_pages": len(set(pages) - set(bundled_pages)),
    }
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    (WORK_ROOT / "build_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def structural_tokens(text: str) -> list[str]:
    """표시 문구를 제외한 GuideME 태그와 링크 대상을 반환한다."""
    tokens = re.findall(r"<[^>]+>|\{[^\n]+\}", text)
    tokens.extend(
        f"image:{value}" for value in re.findall(r"!\[[^]]*\]\(([^)]+)\)", text)
    )
    tokens.extend(
        f"link:{value}" for value in re.findall(r"(?<!!)\[[^]]+\]\(([^)]+)\)", text)
    )
    return tokens


def verify() -> tuple[dict[str, object], list[str]]:
    jar = find_jar()
    errors = []
    english_pages = {}
    with zipfile.ZipFile(jar) as archive:
        for name in archive.namelist():
            if (
                name.startswith(JAR_PREFIX)
                and "/_" not in name
                and name.endswith(".md")
            ):
                english_pages[name[len(JAR_PREFIX) :]] = archive.read(name).decode(
                    "utf-8"
                )
    actual = {
        path.relative_to(OUTPUT_ROOT).as_posix(): path
        for path in OUTPUT_ROOT.rglob("*.md")
    }
    if set(actual) != set(english_pages):
        errors.append("가이드 페이지 경로 불일치")
    for relative, english in english_pages.items():
        path = actual.get(relative)
        if path is None:
            continue
        korean = path.read_text(encoding="utf-8")
        if structural_tokens(english) != structural_tokens(korean):
            errors.append(f"가이드 구조 토큰 불일치: {relative}")
        if english == korean:
            errors.append(f"가이드 미번역: {relative}")
        if re.search(r"\b(The|This|You|Your|It|will|can|with|from|into)\b", korean):
            errors.append(f"가이드 영어 문장 잔존: {relative}")
    report = {
        "pages": len(english_pages),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    args = parser.parse_args()
    if args.command == "build":
        report = build()
        errors = []
    else:
        report, errors = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
