#!/usr/bin/env python3
"""RFTools 계열 언어 파일을 현재 영어 원문 기준으로 번역하고 검증한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path

import actually_additions_family as candidate_helper
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT


FAMILY = "rftools"
WORK_ROOT = PROJECT_ROOT / "working/rftools"
NAMESPACES = (
    "rftoolsbase",
    "rftoolsbuilder",
    "rftoolspower",
    "rftoolsstorage",
    "rftoolsutility",
)
CACHE_FILE = PROJECT_ROOT / "temp/rftools_language_candidate_cache.json"
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?(?:\.\d+)?[a-zA-Z%]|\{[^{}]*\}|@[0-9A-Za-z]")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")

EXACT_NAMES = {
    "RF Network Monitor": "RF 네트워크 모니터",
    "Teleporter Probe": "텔레포터 탐침",
    "Filter Module": "필터 모듈",
    "Developers Delight": "개발자의 기쁨",
    "Shard Wand": "차원 조각 완드",
    "Orphaning Card": "연결 해제 카드",
    "Security Card": "보안 카드",
    "Infused Diamond": "주입된 다이아몬드",
    "Infused Enderpearl": "주입된 엔더 진주",
    "Smart Wrench": "스마트 렌치",
    "Smart Wrench (Select)": "스마트 렌치(선택)",
    "Dimensional Shard": "차원 조각",
    "Dimensional Shard Ore": "차원 조각 광석",
    "Machine Frame": "기계 프레임",
    "Machine Base": "기계 기반",
    "Crafting Card": "제작 카드",
    "Tablet (empty)": "태블릿(비어 있음)",
    "Tablet (filled)": "태블릿(정보 포함)",
    "Technology Guide": "기술 가이드",
    "Machine Infuser": "기계 주입기",
    "Security Manager": "보안 관리자",
    "Information Screen": "정보 화면",
    "Blue Shield Template": "파란색 방어막 틀",
    "Green Shield Template": "초록색 방어막 틀",
    "Red Shield Template": "빨간색 방어막 틀",
    "Yellow Shield Template": "노란색 방어막 틀",
    "Builder": "빌더",
    "Composer": "컴포저",
    "Projector": "프로젝터",
    "Scanner": "스캐너",
    "Space Chamber": "공간 챔버",
    "Space Chamber Controller": "공간 챔버 제어기",
    "Shield Projector Tier 1": "1티어 방어막 프로젝터",
    "Shield Projector Tier 2": "2티어 방어막 프로젝터",
    "Shield Projector Tier 3": "3티어 방어막 프로젝터",
    "Shield Projector Tier 4": "4티어 방어막 프로젝터",
    "Shield": "방어막",
    "Support Block": "지지 블록",
    "Mover": "무버",
    "Mover Controller": "무버 제어기",
    "Vehicle Builder": "탈것 빌더",
    "Vehicle": "탈것",
    "Mover Control": "무버 제어판",
    "Mover Control (Page 2)": "무버 제어판(2쪽)",
    "Mover Control (Page 3)": "무버 제어판(3쪽)",
    "Mover Control (Page 4)": "무버 제어판(4쪽)",
    "Mover Status": "무버 상태 화면",
    "Shape Card": "형상 카드",
    "Shape Card (Placing Liquids)": "형상 카드(유체 설치)",
    "Shape Card (Pump)": "형상 카드(펌프)",
    "Shape Card (Clearing Pump)": "형상 카드(제거형 펌프)",
    "Shape Card (Quarry)": "형상 카드(채석장)",
    "Shape Card (Clearing Quarry)": "형상 카드(제거형 채석장)",
    "Shape Card (Clearing Fortune Quarry)": "형상 카드(제거형 행운 채석장)",
    "Shape Card (Clearing Silk Quarry)": "형상 카드(제거형 섬세한 손길 채석장)",
    "Shape Card (Fortune Quarry)": "형상 카드(행운 채석장)",
    "Shape Card (Silk Quarry)": "형상 카드(섬세한 손길 채석장)",
    "Shape Card (Void)": "형상 카드(공허)",
    "Space Card": "공간 카드",
    "Vehicle Card": "탈것 카드",
    "Vehicle Control Module": "탈것 제어 모듈",
    "Vehicle Status Module": "탈것 상태 모듈",
    "Power Core (Low)": "저급 전력 코어",
    "Power Core (Medium)": "중급 전력 코어",
    "Power Core (High)": "고급 전력 코어",
    "Blazing Rod": "가열된 블레이즈 막대",
    "Powercell Card": "파워셀 카드",
    "Dimensional Cell": "차원 셀",
    "Dimensional Cell (Simple)": "차원 셀(기본)",
    "Dimensional Cell (Advanced)": "차원 셀(고급)",
    "Dimensional Cell (Creative)": "차원 셀(크리에이티브)",
    "Powercell (Low)": "저급 파워셀",
    "Powercell (Medium)": "중급 파워셀",
    "Powercell (High)": "고급 파워셀",
    "Coal Generator": "석탄 발전기",
    "Power Monitor": "전력 모니터",
    "Power Level": "전력 수준 표시기",
    "Endergenic": "엔더제닉 발전기",
    "Ender Monitor": "엔더 모니터",
    "Pearl Injector": "진주 주입기",
    "Blazing Generator": "블레이징 발전기",
    "Blazing Agitator": "블레이징 교반기",
    "Blazing Infuser": "블레이징 주입기",
    "Tier 1 Storage Module": "1티어 저장 모듈",
    "Tier 2 Storage Module": "2티어 저장 모듈",
    "Tier 3 Storage Module": "3티어 저장 모듈",
    "Tier 4 Storage Module": "4티어 저장 모듈",
    "Remote Storage Module (DO NOT USE)": "원격 저장 모듈(사용 금지)",
    "Storage Tablet": "저장소 태블릿",
    "Ore Dictionary Type Module": "광석 사전 유형 모듈",
    "Generic Type Module": "일반 유형 모듈",
    "Tablet (scanner)": "태블릿(스캐너)",
    "Storage Control Screen Module": "저장소 제어 화면 모듈",
    "Dump Screen Module": "비우기 화면 모듈",
    "Modular Storage": "모듈식 저장소",
    "Remote Storage": "원격 저장소",
    "Storage Scanner": "저장소 스캐너",
    "Charged Porter": "충전된 포터",
    "Advanced Charged Porter": "고급 충전된 포터",
    "Module Template": "모듈 틀",
    "ModulePlus Template": "고급 모듈 틀",
    "Syringe": "주사기",
    "Redstone Module": "레드스톤 모듈",
    "Tablet (redstone)": "태블릿(레드스톤)",
    "Tablet (screen)": "태블릿(화면)",
    "Screen Link": "화면 연결기",
    "Crafter Tier 1": "1티어 제작기",
    "Crafter Tier 2": "2티어 제작기",
    "Crafter Tier 3": "3티어 제작기",
    "Matter Booster": "물질 부스터",
    "Matter Transmitter": "물질 송신기",
    "Matter Receiver": "물질 수신기",
    "Destination Analyzer": "목적지 분석기",
    "Dialing Device": "다이얼링 장치",
    "Simple Dialer": "간이 다이얼러",
    "Tank": "탱크",
    "Screen": "화면",
    "Screen Controller": "화면 제어기",
    "Creative Screen": "크리에이티브 화면",
    "Matter Beamer": "물질 빔 발사기",
    "Spawner": "생성기",
    "Environmental Controller": "환경 제어기",
    "Analog": "아날로그 연산기",
    "Counter": "카운터",
    "Digit": "숫자 표시기",
    "Inventory Checker": "인벤토리 검사기",
    "Sensor": "센서",
    "Sequencer": "시퀀서",
    "Logic": "논리 연산기",
    "Timer": "타이머",
    "Wire": "와이어",
    "Redstone Receiver": "레드스톤 수신기",
    "Redstone Transmitter": "레드스톤 송신기",
}

SOURCE_OVERRIDES = {
    **EXACT_NAMES,
    "RFTools Base": "RFTools Base",
    "RFTools Builder": "RFTools Builder",
    "RFTools Power": "RFTools Power",
    "RFTools Storage": "RFTools Storage",
    "RFTools Utility": "RFTools Utility",
    "RFTools": "RFTools",
    "Messages": "메시지",
    "<Press Shift>": "<Shift 누르기>",
    "Item: ": "아이템: ",
    "Mode: ": "모드: ",
    "Block: ": "블록: ",
    "Channel: ": "채널: ",
    "Name: ": "이름: ",
    "Contents: ": "내용물: ",
    "Power: ": "전력: ",
    "Energy: ": "에너지: ",
    "Time: ": "시간: ",
    "Duration: ": "지속 시간: ",
    "Infused: ": "주입률: ",
    "Power usage: ": "전력 사용량: ",
    "Uses: ": "사용량: ",
    "Target: ": "대상: ",
    "Level: ": "수준: ",
    "Recipes: ": "조합법: ",
    "Screen: ": "화면: ",
    "Channels: ": "채널: ",
    "Text: ": "텍스트: ",
    "Counter: ": "카운터: ",
    "Monitoring: ": "감시 대상: ",
    "Producing: ": "생산량: ",
    "Link: ": "연결: ",
    "Base cost: ": "기본 비용: ",
    "Shape: ": "형상: ",
    "Dimension: ": "차원: ",
    "Offset: ": "오프셋: ",
    "Formulas: ": "수식: ",
    "Scan id: ": "스캔 ID: ",
    "Supported blocks: ": "지원 블록 수: ",
    "Storage scanner: ": "저장소 스캐너: ",
    "Supported stacks: ": "지원 스택 수: ",
    "Remote ID: ": "원격 ID: ",
    "UUID: ": "UUID: ",
    "Version: ": "버전: ",
    "Advanced: ": "고급: ",
    "Once: ": "일회성: ",
    "Dialed to: ": "연결 대상: ",
    "Transmitter: ": "송신기: ",
    "Receiver: ": "수신기: ",
}

KEY_OVERRIDES = {
    "message.rftoolsbase.filter_module.header": (
        "이 필터 모듈은 XNet, 저장소, 빌더, 제작기 등 여러 곳에서 사용합니다. "
        "블록이 지정한 아이템만 받도록 제한할 수 있습니다."
    ),
    "message.rftoolsbase.filter_module.gold": (
        "인벤토리를 웅크린 채 우클릭하면 내용물을 기준으로 설정하고, 블록을 웅크린 채 "
        "우클릭하면 해당 블록을 필터에 추가합니다."
    ),
    "message.rftoolsbase.security_manager": (
        "@a내용물: %s스택\n@f이 블록은 보안 카드를 관리합니다."
    ),
    "message.rftoolspower.blazing_infuser.header": (
        "이 장치는 가열된 블레이즈 막대에 차원 조각, 레드스톤 또는 발광석 가루를 "
        "주입합니다. 블레이징 발전기에서 사용할 때 발전량이나 발전 지속 시간이 늘어납니다."
    ),
    "message.rftoolspower.power_monitor.header": (
        "대상 블록의 전력량에 따라 레드스톤 신호를 출력합니다."
    ),
    "message.rftoolspower.blazing_generator.header": (
        "블레이즈 막대로 전력을 생산합니다. 막대는 먼저 블레이징 교반기에서 처리해야 합니다."
    ),
    "message.rftoolspower.endergenic.header": (
        "엔더 진주로 전력을 생산합니다. 작동하려면 발전기가 최소 두 개 필요하고 구성이 "
        "비교적 복잡합니다. 정확한 타이밍이 중요합니다."
    ),
    "message.rftoolspower.endergenic.gold": (
        "주입 보너스: 발전량 증가 및 진주를 보관할 때의 전력 손실 감소"
    ),
    "message.rftoolspower.pearl_injector.header": (
        "레드스톤 신호를 받으면 인접한 엔더제닉 발전기에 엔더 진주를 주입합니다."
    ),
    "message.rftoolspower.dimensionalcell.header": (
        "전력을 저장하며, 필요하면 여러 차원에 걸친 대형 구조로 연결할 수 있습니다."
    ),
    "message.rftoolspower.dimensionalcell_advanced.header": (
        "전력을 저장하며, 필요하면 여러 차원에 걸친 대형 구조로 연결할 수 있습니다."
    ),
    "message.rftoolspower.dimensionalcell_simple.header": (
        "전력을 저장하며, 필요하면 여러 차원에 걸친 대형 구조로 연결할 수 있습니다."
    ),
    "message.rftoolspower.dimensionalcell_creative.header": (
        "전력을 저장하며, 필요하면 여러 차원에 걸친 대형 구조로 연결할 수 있습니다."
    ),
    "message.rftoolsstorage.storage_control_module.header": (
        "저장소 스캐너를 통해 서로 다른 아이템을 최대 9종까지 감시하는 화면 모듈입니다. "
        "태블릿과 결합하면 저장소 스캐너의 제어 화면을 원격으로 열 수 있습니다."
    ),
    "message.rftoolsstorage.crafting_manager.header": "짜잔! 제작 관리자(개발 중)",
    "message.rftoolsstorage.storage_scanner.header": (
        "주변의 모든 인벤토리를 검색해 목록으로 보여 줍니다. 목록에서 아이템을 검색하고 "
        "해당 인벤토리의 내용물에 접근할 수 있습니다."
    ),
    "message.rftoolsstorage.dump_module.header": (
        "많은 아이템을 연결된 저장소 스캐너로 한꺼번에 넣는 화면 모듈입니다."
    ),
    "message.rftoolsbuilder.shape_card.header": (
        "방어막이나 빌더가 사용할 영역을 나타내는 카드입니다. 빌더를 웅크린 채 우클릭해 "
        "표시 모드를 시작한 뒤, 원하는 영역의 두 모서리를 우클릭하세요."
    ),
    "message.rftoolsbuilder.vehicle_builder.header": (
        "공간 챔버에 연결된 공간 카드를 사용해 탈것 카드에 탈것을 만듭니다."
    ),
    "message.rftoolsbuilder.mover_control.header": (
        "무버 제어 화면 1쪽입니다. 이 블록으로 플랫폼의 움직임을 제어합니다."
    ),
    "message.rftoolsbuilder.mover_control2.header": (
        "무버 제어 화면 2쪽입니다. 이 블록으로 플랫폼의 움직임을 제어합니다."
    ),
    "message.rftoolsbuilder.mover_control3.header": (
        "무버 제어 화면 3쪽입니다. 이 블록으로 플랫폼의 움직임을 제어합니다."
    ),
    "message.rftoolsbuilder.mover_control4.header": (
        "무버 제어 화면 4쪽입니다. 이 블록으로 플랫폼의 움직임을 제어합니다."
    ),
    "message.rftoolsutility.sensor.header": (
        "몹, 플레이어, 블록, 유체와 작물 성장 상태 등을 감지하고 조건에 따라 레드스톤 "
        "신호를 보냅니다."
    ),
    "message.rftoolsutility.wire.header": (
        "지연을 거의 만들지 않는 단순한 레드스톤 와이어입니다. 직선으로만 연결됩니다."
    ),
    "message.rftoolsutility.charged_porter.header": (
        "RF로 충전해 미리 지정한 물질 수신기로 순간이동하는 아이템입니다. 수신기를 "
        "웅크린 채 우클릭해 목적지를 지정하고, 우클릭해 순간이동하세요."
    ),
    "message.rftoolsutility.advanced_charged_porter.header": (
        "RF로 충전해 미리 지정한 물질 수신기로 순간이동하는 아이템입니다. 수신기를 "
        "웅크린 채 우클릭해 목적지를 지정하고, 우클릭해 순간이동하세요."
    ),
    "message.rftoolsutility.syringe.header": (
        "몹에게 사용해 정수를 채우는 주사기입니다. 완전히 채운 뒤 생성기에 넣어 사용합니다."
    ),
    "message.rftoolsutility.dialing_device.header": (
        "주변의 물질 송신기와 Minecraft 세계의 물질 수신기를 연결합니다. 전력이 필요하며, "
        "목적지 분석기를 인접하게 놓으면 목적지의 전력이 안전한 수준인지 확인할 수 있습니다."
    ),
    "message.rftoolsutility.matter_transmitter.header": (
        "다이얼링 장치 근처에 놓고 물질 수신기와 연결하는 송신기입니다. 충분한 전력을 "
        "공급하세요. 인접한 목적지 분석기는 목적지 상태를 빨간색(위험), 초록색(안전), "
        "노란색(알 수 없음)으로 표시합니다. 인접한 물질 부스터가 있으면 전력이 없는 "
        "수신기로도 순간이동할 수 있습니다."
    ),
    "message.rftoolsutility.matter_receiver.header": (
        "월드 어디에든 설치한 뒤 다이얼링 장치로 연결할 수 있는 수신기입니다. "
        "순간이동하기 전에 반드시 전력을 공급하세요!"
    ),
    "message.rftoolsutility.simple_dialer.header": (
        "레드스톤 신호를 받으면 송신기의 연결을 시작하거나 끊습니다. 이 블록을 들고 "
        "송신기나 연결된 수신기를 웅크린 채 우클릭해 목적지를 지정하세요."
    ),
    "message.rftoolsutility.matter_beamer.header": (
        "물질을 에너지 빔으로 바꿔 연결된 생성기로 보냅니다. 렌치로 연결하세요."
    ),
    "message.rftoolsutility.matter_beamer.gold": (
        "주입 보너스: 전력 사용량과 필요 재료 감소, 처리 속도 증가"
    ),
    "message.rftoolsutility.screen.header": (
        "모듈을 넣어 표시 내용을 정하는 모듈식 화면입니다. 직접 전력을 받을 수 없으며, "
        "근처의 화면 제어기에서 무선으로 전력을 공급받아야 합니다."
    ),
    "message.rftoolsutility.creative_screen.header": (
        "모듈을 넣어 표시 내용을 정하는 모듈식 화면입니다. 크리에이티브 버전은 전력이 "
        "필요하지 않습니다."
    ),
    "message.rftoolsutility.screen_controller.header": (
        "화면에 전력을 공급하는 제어기입니다. 전력을 쓰지 않는 모듈만 넣은 화면에도 "
        "제어기가 필요합니다. 범위 안의 여러 화면에 전력을 공급할 수 있습니다."
    ),
    "message.rftoolsutility.featherfalling_module.gold": (
        "받는 낙하 피해가 절반으로 줄어듭니다."
    ),
    "message.rftoolsutility.featherfallingplus_module.gold": (
        "낙하 피해를 받지 않습니다."
    ),
    "message.rftoolsutility.crafter1.header": (
        "조합법을 한 번에 최대 2개 처리하며, 앞 단계의 제작 결과를 다음 조합법에서 사용할 "
        "수 있습니다."
    ),
    "message.rftoolsutility.crafter2.header": (
        "조합법을 한 번에 최대 4개 처리하며, 앞 단계의 제작 결과를 다음 조합법에서 사용할 "
        "수 있습니다."
    ),
    "message.rftoolsutility.crafter3.header": (
        "조합법을 한 번에 최대 8개 처리하며, 앞 단계의 제작 결과를 다음 조합법에서 사용할 "
        "수 있습니다."
    ),
}

TERM_REPLACEMENTS = (
    ("RFTools 도구", "RFTools"),
    ("파워 셀", "파워셀"),
    ("전원 셀", "파워셀"),
    ("차원 샤드", "차원 조각"),
    ("디멘셔널 샤드", "차원 조각"),
    ("기계 주입기", "기계 주입기"),
    ("인퓨징 보너스", "주입 보너스"),
    ("주입 보너스", "주입 보너스"),
    ("에너지 소비", "전력 소비"),
    ("전력 소비량", "전력 소비"),
    ("멀티 블록", "멀티블록"),
    ("GUI의", "GUI의"),
    ("GUI 를", "GUI를"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("웅크리고 우클릭", "웅크린 채 우클릭"),
    ("레시피", "조합법"),
    ("엔터티", "엔티티"),
    ("구성", "설정"),
    ("액체", "유체"),
    ("텔레포트", "순간이동"),
    ("스폰", "생성"),
    ("항목", "아이템"),
    ("선수", "플레이어"),
    ("체액", "유체"),
    ("우주실", "공간 챔버"),
    ("우주 챔버", "공간 챔버"),
    ("차량", "탈것"),
    ("스토리지", "저장소"),
    ("스크린", "화면"),
    ("컨트롤러", "제어기"),
    ("몰래 우클릭", "웅크린 채 우클릭"),
    ("살짝 우클릭", "웅크린 채 우클릭"),
    ("다중 블록", "멀티블록"),
    ("순간 이동", "순간이동"),
    ("조합법를", "조합법을"),
    ("순간이동를", "순간이동을"),
    ("구성에서", "설정에서"),
    ("하십시오", "하세요"),
    ("매뉴얼", "가이드"),
    ("데미지", "피해"),
    ("목표를 설정", "대상을 설정"),
)


def load_json(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(text, str) for key, text in value.items()
    ):
        raise TypeError(f"문자열 JSON 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def request_candidate(source: str) -> str:
    tokens: list[str] = []

    def hide(match: re.Match[str]) -> str:
        tokens.append(match.group(0))
        return f"QXRFT{len(tokens) - 1}QX"

    protected = PLACEHOLDER.sub(hide, source).replace("\n", " QXRFTNEWLINEQX ")
    translated = candidate_helper.request_translation_candidate(protected)
    translated = translated.replace(" QXRFTNEWLINEQX ", "\n").replace(
        "QXRFTNEWLINEQX", "\n"
    )
    for index, token in enumerate(tokens):
        marker = f"QXRFT{index}QX"
        if marker not in translated:
            raise ValueError(f"보호 표식이 사라졌습니다: {source}: {marker}")
        translated = translated.replace(marker, token)
    return translated


def candidate() -> dict[str, object]:
    sources = {
        namespace: load_json(WORK_ROOT / namespace / "en_us.json")
        for namespace in NAMESPACES
    }
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests = {
        source
        for english in sources.values()
        for source in english.values()
        if source not in SOURCE_OVERRIDES
        and LATIN_WORD.search(source)
        and not isinstance(cache.get(source), str)
    }
    failures: list[str] = []
    if requests:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(request_candidate, source): source
                for source in sorted(requests)
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("번역 후보 생성 실패:\n" + "\n".join(failures))
    candidates = {
        namespace: {
            key: SOURCE_OVERRIDES.get(source, cache.get(source, source))
            for key, source in english.items()
        }
        for namespace, english in sources.items()
    }
    write_json(CANDIDATE_FILE, candidates)
    report = {
        "keys": sum(len(values) for values in sources.values()),
        "manual_name_and_ui_sources": len(SOURCE_OVERRIDES),
        "candidate_sources": len(requests),
        "status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


def structured_name(source: str, value: str) -> str:
    screen_modules = {
        "Text": "텍스트",
        "Energy": "에너지",
        "Energy Plus": "고급 에너지",
        "Inventory": "인벤토리",
        "Inventory Plus": "고급 인벤토리",
        "Clock": "시계",
        "Fluid": "유체",
        "Fluid Plus": "고급 유체",
        "Counter": "카운터",
        "Counter Plus": "고급 카운터",
        "Redstone": "레드스톤",
        "Machine Information": "기계 정보",
        "Computer": "컴퓨터",
        "Button": "버튼",
    }
    match = re.fullmatch(r"(.+) Screen Module", source)
    if match and match.group(1) in screen_modules:
        return f"{screen_modules[match.group(1)]} 화면 모듈"
    effects = {
        "Regeneration": "재생",
        "Regeneration+": "고급 재생",
        "Speed": "속도",
        "Speed+": "고급 속도",
        "Haste": "성급함",
        "Haste+": "고급 성급함",
        "Saturation": "포화",
        "Saturation+": "고급 포화",
        "Featherfalling": "가벼운 착지",
        "Featherfalling+": "고급 가벼운 착지",
        "Flight": "비행",
        "Peaceful": "평화",
        "Waterbreathing": "수중 호흡",
        "Nightvision": "야간 투시",
        "Glowing": "발광",
        "Luck": "행운",
        "Noteleport": "순간이동 방지",
        "Blindness": "실명",
        "Weakness": "나약함",
        "Poison": "독",
        "Slowness": "구속",
    }
    match = re.fullmatch(r"(.+) Module", source)
    if match and match.group(1) in effects:
        return f"{effects[match.group(1)]} 모듈"
    return value


def reviewed_value(key: str, source: str, candidate_value: str) -> str:
    value = KEY_OVERRIDES.get(key, SOURCE_OVERRIDES.get(source, candidate_value))
    effect_headers = {
        "regeneration_module": "재생",
        "regenerationplus_module": "재생 III",
        "speed_module": "신속",
        "speedplus_module": "신속 III",
        "haste_module": "성급함",
        "hasteplus_module": "성급함 III",
        "saturation_module": "포화",
        "saturationplus_module": "포화 III",
        "featherfalling_module": "가벼운 착지",
        "featherfallingplus_module": "가벼운 착지",
        "flight_module": "크리에이티브 비행",
        "waterbreathing_module": "수중 호흡",
        "nightvision_module": "야간 투시",
        "glowing_module": "발광",
        "luck_module": "행운",
        "blindness_module": "실명",
        "weakness_module": "나약함",
        "poison_module": "독",
        "slowness_module": "구속",
    }
    match = re.fullmatch(r"message\.rftoolsutility\.(.+)\.header", key)
    if match and match.group(1) in effect_headers:
        value = (
            f"환경 제어기에 장착하면 대상에게 {effect_headers[match.group(1)]} "
            "효과를 부여합니다."
        )
    if key == "message.rftoolsutility.peaceful_module.header":
        value = "환경 제어기에 장착하면 범위 안에서 적대적 몹이 생성되지 않습니다."
    if key == "message.rftoolsutility.noteleport_module.header":
        value = "환경 제어기에 장착하면 셜커와 엔더맨의 순간이동을 막습니다."
    value = structured_name(source, value)
    for old, new in TERM_REPLACEMENTS:
        value = value.replace(old, new)
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    value = value.replace(".,", ",").replace("합니다..", "합니다.")
    value = value.replace("있습니다..", "있습니다.").replace(" ​​", " ")
    leading = source[: len(source) - len(source.lstrip())]
    trailing = source[len(source.rstrip()) :]
    value = leading + value.strip() + trailing
    return value


def normalize() -> dict[str, object]:
    candidates = json.loads(CANDIDATE_FILE.read_text(encoding="utf-8"))
    reviewed = 0
    for namespace in NAMESPACES:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        namespace_candidates = candidates.get(namespace)
        if not isinstance(namespace_candidates, dict):
            raise TypeError(f"후보 네임스페이스가 없습니다: {namespace}")
        korean = {
            key: reviewed_value(key, source, str(namespace_candidates[key]))
            for key, source in english.items()
        }
        write_json(WORK_ROOT / namespace / "ko_kr.json", korean)
        reviewed += len(english)
    report = {
        "keys_reviewed": reviewed,
        "bundled_korean_reused_without_review": 0,
        "status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    untranslated: list[str] = []
    reviewed = 0
    for namespace in NAMESPACES:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        if list(english) != list(korean):
            errors.append(f"영어와 한국어 키 또는 순서가 다릅니다: {namespace}")
        for key, source in english.items():
            target = korean.get(key, "")
            reviewed += 1
            errors.extend(
                family_goal.validate_family_value(FAMILY, key, source, target)
            )
            if (
                source == target
                and LATIN_WORD.search(source)
                and source not in SOURCE_OVERRIDES
                and not family_goal.is_allowed_original(source)
            ):
                untranslated.append(f"{namespace}:{key}")
    if untranslated:
        errors.append(f"미번역 키: {untranslated[:30]}")
    report = {
        "keys_reviewed": reviewed,
        "bundled_korean_reused_without_review": 0,
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", report)
    return report, 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("candidate", "normalize", "verify"))
    args = parser.parse_args()
    if args.action == "candidate":
        result = candidate()
        status = 0
    elif args.action == "normalize":
        result = normalize()
        status = 0
    else:
        result, status = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
