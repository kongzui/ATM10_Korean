#!/usr/bin/env python3
"""PneumaticCraft 언어 파일의 번역 후보를 만들고 전체 검수한다."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import ars_family
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root


FAMILY = "pneumaticcraft"
WORK_ROOT = PROJECT_ROOT / "working/pneumaticcraft/pneumaticcraft"
ENGLISH_FILE = WORK_ROOT / "en_us.json"
KOREAN_FILE = WORK_ROOT / "ko_kr.json"
SOURCE_FILE = WORK_ROOT / "candidate_sources.json"
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"
CACHE_FILE = PROJECT_ROOT / "temp/pneumaticcraft_language_candidate_cache.json"

ALLOWED_EXACT_KEYS = {
    "key.pneumaticcraft.category.main",
    "pneumaticcraft.gui.misc.amineLabel",
    "pneumaticcraft.gui.misc.checkbox.false",
    "pneumaticcraft.gui.misc.checkbox.true",
    "pneumaticcraft.gui.redstoneModule.operation_xor",
}

VALUE_OVERRIDES = {
    "PneumaticCraft: Repressurized": "PneumaticCraft: Repressurized",
    "PneumaticCraft": "PneumaticCraft",
    "Compressed Iron": "압축 철",
    "Compressed Iron Ingot": "압축 철 주괴",
    "Block of Compressed Iron": "압축 철 블록",
    "Pneumatic Wrench": "공압 렌치",
    "Pneumatic Armor": "공압 방어구",
    "Pneumatic Helmet": "공압 헬멧",
    "Pneumatic Chestplate": "공압 흉갑",
    "Pneumatic Leggings": "공압 각반",
    "Pneumatic Boots": "공압 부츠",
    "Pneumatic Jackhammer": "공압식 착암기",
    "Pressure Tube": "압력 튜브",
    "Advanced Pressure Tube": "고급 압력 튜브",
    "Pressure Chamber": "압력 챔버",
    "Pressure Chamber Wall": "압력 챔버 벽",
    "Pressure Chamber Glass": "압력 챔버 유리",
    "Pressure Chamber Valve": "압력 챔버 밸브",
    "Pressure Chamber Interface": "압력 챔버 인터페이스",
    "Air Compressor": "공기 압축기",
    "Advanced Air Compressor": "고급 공기 압축기",
    "Liquid Compressor": "액체 압축기",
    "Advanced Liquid Compressor": "고급 액체 압축기",
    "Manual Compressor": "수동 압축기",
    "Electric Compressor": "전기 압축기",
    "Flux Compressor": "플럭스 압축기",
    "Creative Compressor": "크리에이티브 압축기",
    "Creative Compressed Iron Block": "크리에이티브 압축 철 블록",
    "Electrostatic Compressor": "정전기 압축기",
    "Thermal Compressor": "열 압축기",
    "Solar Compressor": "태양열 압축기",
    "Charging Station": "충전소",
    "Security Upgrade": "보안 업그레이드",
    "Speed Upgrade": "속도 업그레이드",
    "Range Upgrade": "범위 업그레이드",
    "Volume Upgrade": "용량 업그레이드",
    "Dispenser Upgrade": "발사기 업그레이드",
    "Pressure Gauge": "압력계",
    "Manometer": "휴대용 압력계",
    "Air Canister": "공기 용기",
    "Reinforced Air Canister": "강화 공기 용기",
    "Small Fluid Tank": "소형 유체 탱크",
    "Medium Fluid Tank": "중형 유체 탱크",
    "Large Fluid Tank": "대형 유체 탱크",
    "Huge Fluid Tank": "초대형 유체 탱크",
    "Aerial Interface": "공중 인터페이스",
    "Air Cannon": "에어 캐논",
    "Assembly Controller": "조립 제어기",
    "Assembly Drill": "조립 드릴",
    "Assembly IO Unit": "조립 입출력 장치",
    "Assembly IO Unit (export)": "조립 입출력 장치(출력)",
    "Assembly IO Unit (import)": "조립 입출력 장치(입력)",
    "Assembly Laser": "조립 레이저",
    "Assembly Platform": "조립 플랫폼",
    "Display Shelf": "진열 선반",
    "Display Table": "진열대",
    "Drone Interface": "드론 인터페이스",
    "Elevator Base": "엘리베이터 기반",
    "Elevator Caller": "엘리베이터 호출기",
    "Elevator Frame": "엘리베이터 프레임",
    "Etching Acid": "에칭 산",
    "Etching Tank": "에칭 탱크",
    "Fluid Mixer": "유체 혼합기",
    "Gas Lift": "가스 리프트",
    "Heat Pipe": "열 파이프",
    "Heat Sink": "방열판",
    "Kerosene Lamp": "등유 램프",
    "Liquid Hopper": "유체 호퍼",
    "Omnidirectional Hopper": "전방향 호퍼",
    "Pneumatic Door": "공압 문",
    "Pneumatic Door Base": "공압 문 기반",
    "Pneumatic Dynamo": "공압 다이너모",
    "Pneumatic Generator": "공압 발전기",
    "Pressurized Spawner": "가압 생성기",
    "Programmable Controller": "프로그래밍 가능 제어기",
    "Programmer": "프로그래머",
    "Refinery Controller": "정유기 제어기",
    "Refinery Output": "정유기 출력부",
    "Reinforced Chest": "강화 상자",
    "Security Station": "보안 스테이션",
    "Sentry Turret": "감시 포탑",
    "Smart Chest": "스마트 상자",
    "Tag Workbench": "태그 작업대",
    "Thermopneumatic Processing Plant": "열공압 처리 공장",
    "Universal Sensor": "범용 센서",
    "UV Light Box": "UV 라이트 박스",
    "Vacuum Pump": "진공 펌프",
    "Vacuum Trap": "진공 덫",
    "Vortex Tube": "볼텍스 튜브",
    "Biodiesel": "바이오디젤",
    "Diesel": "디젤",
    "Ethanol": "에탄올",
    "Gasoline": "휘발유",
    "Glycerol": "글리세롤",
    "Kerosene": "등유",
    "LPG": "LPG",
    "Lubricant": "윤활유",
    "Crude Oil": "원유",
    "Vegetable Oil": "식물성 기름",
    "Molten Plastic": "용융 플라스틱",
    "Reinforced Stone": "강화석",
    "Reinforced Stone Slab": "강화석 반 블록",
    "Compressed Stone": "압축 돌",
    "Compressed Stone Slab": "압축 돌 반 블록",
    "Thermal Lagging": "단열재",
    "Tube Junction": "튜브 접합부",
    "Spawner Extractor": "생성기 추출기",
    "Yeast Culture": "효모 배양액",
    "Air Canister Array": "공기 용기 배열",
    "Air Conditioning Upgrade": "공기 조절 업그레이드",
    "Air Grate Tube Module": "에어 그레이트 튜브 모듈",
    "Amadron Tablet": "아마드론 태블릿",
    "Biodiesel Bucket": "바이오디젤 양동이",
    "Camouflage Applicator": "위장 도포기",
    "Cannon Barrel": "포신",
    "Capacitor": "축전기",
    "Chips": "감자튀김",
    "Classify Filter": "분류 필터",
    "Collector Drone": "수집 드론",
    "Compressed Iron Boots": "압축 철 부츠",
    "Compressed Iron Chestplate": "압축 철 흉갑",
    "Compressed Iron Gear": "압축 철 기어",
    "Compressed Iron Helmet": "압축 철 헬멧",
    "Compressed Iron Leggings": "압축 철 각반",
    "Compressed Iron Drill Bit": "압축 철 드릴 비트",
    "Copper Nugget": "구리 조각",
    "Crop Support": "작물 지지대",
    "Diesel Bucket": "디젤 양동이",
    "Drone": "드론",
    "Entity Tracker Upgrade": "개체 추적기 업그레이드",
    "Etching Acid Bucket": "에칭 산 양동이",
    "Ethanol Bucket": "에탄올 양동이",
    "Gasoline Bucket": "휘발유 양동이",
    "Freezing Minigun Ammo": "빙결 미니건 탄약",
    "Weighted Minigun Ammo": "중량 미니건 탄약",
    "Heat Frame": "열 프레임",
    "Jet Boots Upgrade: Tier I": "제트 부츠 업그레이드: 1단계",
    "Jet Boots Upgrade: Tier II": "제트 부츠 업그레이드: 2단계",
    "Jet Boots Upgrade: Tier III": "제트 부츠 업그레이드: 3단계",
    "Jet Boots Upgrade: Tier IV": "제트 부츠 업그레이드: 4단계",
    "Jet Boots Upgrade: Tier V": "제트 부츠 업그레이드: 5단계",
    "Jumping Upgrade: Tier I": "도약 업그레이드: 1단계",
    "Jumping Upgrade: Tier II": "도약 업그레이드: 2단계",
    "Jumping Upgrade: Tier III": "도약 업그레이드: 3단계",
    "Jumping Upgrade: Tier IV": "도약 업그레이드: 4단계",
    "Kerosene Bucket": "등유 양동이",
    "Logistics Configurator": "물류 설정기",
    "Logistics Core": "물류 코어",
    "Logistics Drone": "물류 드론",
    "Logistic Active Provider Frame": "능동 공급자 물류 프레임",
    "Logistic Default Storage Frame": "기본 저장 물류 프레임",
    "Logistic Passive Provider Frame": "수동 공급자 물류 프레임",
    "Logistic Requester Frame": "요청자 물류 프레임",
    "Logistic Storage Frame": "저장 물류 프레임",
    "Logistics Active Provider Frame": "능동 공급자 물류 프레임",
    "Logistics Default Storage Frame": "기본 저장 물류 프레임",
    "Logistics Passive Provider Frame": "수동 공급자 물류 프레임",
    "Logistics Requester Frame": "요청자 물류 프레임",
    "Logistics Storage Frame": "저장 물류 프레임",
    "LPG Bucket": "LPG 양동이",
    "Lubricant Bucket": "윤활유 양동이",
    "Network Component": "네트워크 부품",
    "Night Vision Upgrade": "야간 투시 업그레이드",
    "Nuke Virus": "Nuke 바이러스",
    "Crude Oil Bucket": "원유 양동이",
    "PCB Blueprint": "PCB 설계도",
    "Bucket of Molten Plastic": "용융 플라스틱 양동이",
    "Finished PCB": "완성 PCB",
    "Raw Salmon Tempura": "생연어 튀김",
    "Regulator Tube Module": "조절기 튜브 모듈",
    "Reinforced Air Canister Array": "강화 공기 용기 배열",
    "Reinforced Chest Upgrade Kit": "강화 상자 업그레이드 키트",
    "Remote": "리모컨",
    "Salmon Tempura": "연어 튀김",
    "Smart Chest Upgrade Kit": "스마트 상자 업그레이드 키트",
    "Solar Cell": "태양 전지",
    "Solar Wafer": "태양 전지 웨이퍼",
    "Sourdough": "사워도우",
    "Sourdough Bread": "사워도우 빵",
    "Spawner Agitator": "생성기 교반기",
    "Spawner Core Shell": "생성기 코어 외피",
    "Stomp Upgrade": "짓밟기 업그레이드",
    "Stone Base": "돌 기반",
    "STOP! Worm": "STOP! 웜",
    "Turbine Blade": "터빈 날개",
    "Unassembled Netherite Drill Bit": "미조립 네더라이트 드릴 비트",
    "Unassembled PCB": "미조립 PCB",
    "Unassembled Reinforced Pressure Chamber Valve": "미조립 강화 압력 챔버 밸브",
    "Vacuum Tube Module": "진공 튜브 모듈",
    "Vegetable Oil Bucket": "식물성 기름 양동이",
    "Vortex Cannon": "볼텍스 캐논",
    "Yeast Culture Bucket": "효모 배양액 양동이",
    "Comment": "주석",
    "Condition: Block": "조건: 블록",
    "Condition: Items": "조건: 아이템",
    "Condition: Light Level": "조건: 밝기",
    "Coordinate": "좌표",
    "Dig Area": "영역 굴착",
    "Drone Condition: Fluid": "드론 조건: 유체",
    "Export Entity": "개체 내보내기",
    "Import Entity": "개체 가져오기",
    "Harvest": "수확",
    "Item Assignment": "아이템 할당",
    "Label": "레이블",
    "Export Fluid": "유체 내보내기",
    "Logistics": "물류",
    "Pick up Items": "아이템 줍기",
    "Place": "배치",
    "Export RF": "RF 내보내기",
    "Suicide": "자폭",
    "Void Item": "아이템 폐기",
    "Void Fluid": "유체 폐기",
    "Wait": "대기",
    "Charging Armor": "방어구 충전",
    "Charging Held": "손에 든 아이템 충전",
    "Charging Armor + Held": "방어구 및 손에 든 아이템 충전",
    "Item/Fluid Amount": "아이템/유체 수량",
    "Insert:": "삽입:",
    "Item...": "아이템...",
    "Advanced": "고급",
    "Recipes": "제작법",
    "Bar": "bar",
    "Facing: %s": "방향: %s",
    "Fluid Blacklist": "유체 차단 목록",
    "Fluid Whitelist": "유체 허용 목록",
    "Item Blacklist": "아이템 차단 목록",
    "Item Whitelist": "아이템 허용 목록",
    "Requesting Fluids": "요청 중인 유체",
    "Requesting Items": "요청 중인 아이템",
    "Stock Fluid (mB)": "재고 유체(mB)",
    "Stock Items": "재고 아이템",
    "Damage": "피해",
    "Dumb": "직선",
    "Smart": "유도",
    "Any": "임의",
    "Margin": "여백",
    "Progress:": "진행도:",
    "Search Inv...": "인벤토리 검색...",
    "Search Item...": "아이템 검색...",
    "Retrieved from clipboard": "클립보드에서 불러옴",
    "Retrieved from Pastebin": "Pastebin에서 불러옴",
    "Current Extension: %sM": "현재 높이: %sM",
    "Floor %d / %d": "%d층 / %d층",
    "Max Extension: %sM": "최대 높이: %sM",
    "No Elevator Callers found": "엘리베이터 호출기를 찾을 수 없음",
    "Charge Held Item": "손에 든 아이템 충전",
    "Excluded Pieces": "제외된 조각",
    "Door Powering": "문 동력 설정",
    "Fire Upon": "발사 조건",
    "Iron Door Behaviour": "철문 동작",
    "Open when": "열기 조건",
    "Wooden Door Behaviour": "나무문 동작",
    "Inverted": "반전",
    "Struck by Lightning": "번개에 맞음",
    "No Action": "동작 없음",
    "Pulling Items": "아이템 가져오는 중",
    "Pushing Items": "아이템 내보내는 중",
    "Fluid: ": "유체: ",
    "Fortified": "강화됨",
    "Transfer: In": "전송: 입력",
    "Transfer: Out": "전송: 출력",
    "Advanced config": "고급 설정",
    "Threshold:": "임계값:",
    "Setup": "설정",
    "Tiering It Up": "단계 올리기",
    "Building up the Pressure!": "압력을 높여라!",
    "Better Than Villagers": "주민보다 낫다",
    "Production Line!": "생산 라인!",
    "Plausible Deniability": "모르는 척하기",
    "You spin me right round": "빙글빙글 돌려요",
    "This is the Best Bit": "최고의 비트",
    "Won't Know What Hit 'em": "무엇에 맞았는지도 모르게",
    "Up And Away!": "이륙!",
    "Digging with Jack": "잭과 함께 굴착",
    "Smart Configuration": "스마트 설정",
    "Smart Storage": "스마트 저장소",
    "Born Slippy": "미끄러움의 탄생",
    "You Vandal!": "이 기계 파괴범!",
    "Black Gold": "검은 황금",
    "And You're Done": "이제 끝!",
    "Let's Torque About Tools": "도구와 토크 이야기",
    "Totally Tubular Transfer": "완벽한 튜브 운송",
    "Not a Jigsaw": "직소 퍼즐은 아닙니다",
    "A Little Refinement": "약간의 정제",
    "The First Explosion (of many?)": "첫 폭발(수많은 폭발 중 하나?)",
    "Try saying that three times fast": "세 번 빨리 말해 보세요",
    "'Cause you're hot then you're cold": "뜨거웠다 차가웠다",
    "Feeling Cultured": "배양된 기분",
    (
        "Emits a redstone signal of which the strength is proportional to the day time "
        "of the world (0..23999):\nstrength = time / 1500\nExample: If the time is "
        "6000 (noon), the redstone strength will be 4."
    ): (
        "월드의 낮 시간(0..23999)에 비례하는 세기의 레드스톤 신호를 출력합니다:\n"
        "세기 = 시간 / 1500\n예: 시간이 6000(정오)이면 레드스톤 신호 세기는 "
        "4입니다."
    ),
    (
        "\nBonus output chance!\n%5.2f%% chance of an extra %s per degree below "
        "%d°C\n (multiplier limit: x%5.2f)"
    ): (
        "\n보너스 출력 확률!\n%5.2f%% 확률로 %s 추가(%d°C보다 1도 "
        "낮을 때마다)\n (배수 제한: x%5.2f)"
    ),
}

KEY_OVERRIDES = {
    "pneumaticcraft.gui.tab.upgrades.charging_station.dispenser": (
        "충전소에 충전 패드를 추가합니다. 그러면 충전소 바로 위의 드론과 아이템, "
        "플레이어 인벤토리의 아이템을 충전하거나 방전할 수 있습니다."
    ),
    "gui.tooltip.block.pneumaticcraft.advanced_air_compressor": (
        "공기 압축기의 2등급 버전입니다. 화로에서 태울 수 있는 모든 연료로 압축 공기를 "
        "틱당 50mL 생산하며 열도 발생합니다. 온도가 높을수록 효율이 낮아집니다. 온도계의 "
        "아래쪽 화살표는 효율이 감소하기 시작하는 지점이고, 위쪽 화살표는 효율이 "
        "0%%가 되는 지점입니다.\n\n이 모드의 다른 기계와 달리 온도가 너무 높아져도 "
        "폭발하지 않습니다."
    ),
    "gui.tooltip.block.pneumaticcraft.advanced_liquid_compressor": (
        "액체 압축기의 고급 버전입니다. 압축 공기를 틱당 50mL로 훨씬 빠르게 생산하지만 "
        "열도 발생합니다. 온도가 높을수록 효율이 낮아집니다. 온도계의 아래쪽 화살표는 "
        "효율이 감소하기 시작하는 지점이고, 위쪽 화살표는 효율이 0%%가 되는 "
        "지점입니다.\n\n이 모드의 다른 기계와 달리 온도가 너무 높아져도 폭발하지 "
        "않습니다."
    ),
    "gui.tooltip.block.pneumaticcraft.air_compressor": (
        "화로에서 태울 수 있는 고체 연료를 연료 슬롯에 넣어 압축 공기를 생산합니다. "
        "용암 양동이 같은 유체 연료는 사용할 수 없으므로 액체 압축기를 사용하세요."
    ),
    "gui.tooltip.block.pneumaticcraft.assembly_drill": (
        "조립 라인의 일부입니다. 상하좌우로 바로 인접한 조립 플랫폼 위의 아이템을 "
        "드릴로 가공합니다. 대각선으로 놓인 플랫폼에는 작동하지 않습니다."
    ),
    "gui.tooltip.block.pneumaticcraft.assembly_laser": (
        "조립 라인의 일부입니다. 상하좌우로 바로 인접한 조립 플랫폼 위의 아이템을 "
        "레이저로 가공합니다. 대각선으로 놓인 플랫폼에는 작동하지 않습니다."
    ),
    "gui.tooltip.block.pneumaticcraft.charging_station": (
        "드론, 공압 렌치, 볼텍스 캐논처럼 압축 공기로 작동하는 아이템을 충전하거나 "
        "방전합니다.\n\n업그레이드를 지원하는 아이템의 업그레이드를 설치하고 관리할 "
        "때도 사용합니다."
    ),
    "gui.tooltip.block.pneumaticcraft.electrostatic_compressor": (
        "현실에서는 매우 어려운 일이지만, 여기서는 번개로 압축 공기를 만들 수 있습니다. "
        "이 압축기는 번개를 맞으면 즉시 공기 200,000mL를 생산합니다. 번개가 칠 확률을 "
        "높이려면 압축기에 연결된 철창이나 피뢰침 격자를 설치하세요(기본 설정이며 "
        "모드팩에서 바뀔 수 있으므로 JEI를 확인하세요).\n\n참고:\n"
        "• 같은 격자에 정전기 압축기를 여러 개 설치하면 생산된 공기를 서로 나눕니다.\n"
        "• 격자는 압축기에서 수평 반경 5블록, 수직 5블록까지 유효합니다. 격자당 최대 "
        "250블록까지 설치할 수 있으며, 블록이 많을수록 번개가 칠 확률이 높아집니다.\n"
        "• 압축기 바로 위에 철창이나 피뢰침을 최대 10개까지 기둥처럼 쌓아 확률을 더 "
        "높일 수 있습니다.\n"
        "• 남는 에너지를 방출해 폭발을 막으려면 압축기 바로 아래에 격자 블록 기둥을 "
        "설치해 접지하세요. 필요한 블록 수는 연결된 압축기 수에 따라 달라집니다(‘정전기 "
        "정보’ GUI 탭 참조).\n"
        "• 번개가 칠 확률은 맑은 날에는 매우 낮고, 비가 오면 높아지며, 뇌우가 오면 "
        "훨씬 높아집니다."
    ),
    "gui.tooltip.block.pneumaticcraft.etching_tank": (
        "에칭 산을 채우고 UV 라이트 박스에 노출한 빈 PCB를 넣으세요. 50°C보다 높게 "
        "가열하면 온도가 오를수록 에칭이 빨라지지만 에칭 산이 조금씩 소모됩니다.\n"
        "미조립 PCB는 옆면에서, 실패한 PCB는 위아래에서 꺼낼 수 있습니다."
    ),
    "gui.tooltip.block.pneumaticcraft.fluid_mixer": (
        "압력을 사용해 두 유체를 혼합하여 유체나 아이템을 생산합니다.\n\n압력이 높을수록 "
        "빠르게 작동하지만 공기도 더 빨리 소모합니다."
    ),
    "gui.tooltip.block.pneumaticcraft.gas_lift": (
        "가스 리프트는 압력으로 유체를 퍼 올리는 펌프입니다. 작동하려면 압력과 드릴 "
        "파이프가 필요합니다. 유체에 닿을 때까지 드릴 파이프를 아래로 설치하며, 단단한 "
        "블록을 만나면 블록 경도에 비례하는 압력을 소모해 굴착합니다.\n작업 깊이가 "
        "깊어질수록 필요한 최소 압력도 비례해 증가합니다."
    ),
    "gui.tooltip.block.pneumaticcraft.liquid_compressor": (
        "여러 유체 연료로 압축 공기를 생산합니다. 사용할 수 있는 연료는 ‘사용 가능한 "
        "연료’ 탭에서 효율이 높은 순서대로 확인할 수 있습니다. x1.5 같은 배수는 기준 "
        "연료보다 그만큼 빠르게 연소해 공기를 더 빨리 생산하지만 연료도 더 빨리 "
        "소모한다는 뜻입니다.\n\n연료는 파이프로 주입하거나, 유체 용기를 든 채 기계를 "
        "우클릭하거나, 유체 용기를 위쪽 슬롯에 넣어 공급할 수 있습니다."
    ),
    "gui.tooltip.block.pneumaticcraft.liquid_hopper": (
        "유체를 옮기는 전방향 호퍼입니다.\n\n탱크 사이에서 유체를 운반할 뿐 아니라 "
        "입력 쪽에 있는 양동이 같은 유체 용기는 비우고, 출력 쪽의 유체 용기는 채우려고 "
        "시도합니다."
    ),
    "gui.tooltip.block.pneumaticcraft.security_station": (
        "범위 안의 모든 블록을 다른 플레이어가 사용하거나 파괴하지 못하게 보호합니다. "
        "‘신뢰하는 플레이어’ 탭에 친구를 추가하면 허용 목록에 넣을 수 있습니다.\n"
        "가장 효과적인 네트워크 구성법은 설명서(Patchouli 필요)를 확인하세요. 보안 "
        "스테이션은 적대적인 플레이어의 해킹을 100%% 막지는 못합니다. ‘테스트’ 버튼으로 "
        "실제 해킹 전에 네트워크의 방어 성능을 시험할 수 있습니다."
    ),
    "gui.tooltip.block.pneumaticcraft.sentry_turret": (
        "감시 포탑은 자동 방어 무기입니다. 총기 탄약을 공급하면 16블록 이내의 살아 있는 "
        "개체를 공격하며, 범위 업그레이드로 사거리를 늘릴 수 있습니다. ‘필터’ 입력란에서 "
        "공격할 개체를 지정할 수 있습니다. 보안 스테이션의 보호 범위 안에서는 해당 "
        "스테이션이 허용한 플레이어를 공격하지 않습니다."
    ),
    "gui.tooltip.block.pneumaticcraft.thermal_compressor": (
        "열 압축기는 블록의 서로 마주 보는 면 사이의 온도 차이로 압축 공기를 만듭니다. "
        "한쪽에는 고온 블록을, 반대쪽에는 저온 블록을 놓으세요.\n\n남북 면끼리, 동서 "
        "면끼리는 열적으로 연결되지만 NS와 EW 사이에는 교차 연결이 없습니다. 연결된 두 "
        "면은 온도가 같아지려고 하므로 충분한 온도 차이를 계속 유지해야 합니다."
    ),
    "gui.tooltip.block.pneumaticcraft.thermopneumatic_processing_plant": (
        "열공압 처리 공장은 유체를 다른 유체로 가공합니다. LPG와 석탄으로 용융 "
        "플라스틱을 만들 수 있으며, 무거운 연료를 가벼운 연료로 분해할 수도 있습니다. "
        "디젤은 등유로, 등유는 휘발유로, 휘발유는 LPG로 바꿀 수 있습니다."
    ),
    "gui.tooltip.block.pneumaticcraft.universal_sensor": (
        "여러 용도로 사용할 수 있는 센서입니다. 알맞은 업그레이드를 넣고 폴더 구조를 "
        "탐색해 센서를 선택하세요. 센서는 노란색 글자의 버튼으로 표시됩니다.\n\n블록 "
        "센서는 지정한 블록 위치에 따라 레드스톤 신호를 출력하므로 GPS 도구나 GPS 영역 "
        "도구도 넣어야 합니다. GPS 영역 도구를 넣으면 감시 영역을 지정하며, 서버 성능을 "
        "보호하기 위해 측정 간격이 길어집니다. 모든 블록 위치는 센서 범위 안에 있어야 "
        "하므로 필요하면 범위 업그레이드를 설치하세요."
    ),
    "gui.tooltip.block.pneumaticcraft.uv_light_box": (
        "빈 PCB에 UV를 쬐어 에칭 탱크에서 처리할 수 있게 합니다. 오래 노출할수록 에칭에 "
        "성공할 확률이 높아지지만 진행 속도는 점점 느려집니다.\n\nPCB를 완료로 판단할 "
        "임계값을 설정할 수 있습니다. 값을 낮추면 빨리 처리하는 대신 에칭에 실패할 "
        "가능성이 커집니다. 실패한 PCB는 용광로에서 재활용해 다시 시도할 수 있습니다."
    ),
    "gui.tooltip.block.pneumaticcraft.vortex_tube": (
        "들어오는 공기를 뜨거운 쪽과 차가운 쪽으로 나눕니다. 공기 소모량은 압력에 따라 "
        "달라집니다. 두 면은 약하게 열이 통하므로 뜨거운 쪽을 이용하려면 차가운 쪽에 "
        "방열판을 달아 냉각하고, 차가운 쪽을 이용하려면 반대로 해야 효율이 좋습니다."
    ),
    "gui.tooltip.item.pneumaticcraft.amadron_tablet": (
        "아마드론 태블릿은 주민 거래처럼 아이템과 유체를 주문하는 데 사용합니다. 다만 "
        "거래품은 주민보다 훨씬 멋진 드론이 배달합니다. 태블릿을 들고 인벤토리나 탱크를 "
        "우클릭해 수거 및 배송 위치를 지정해야 합니다."
    ),
    "gui.tooltip.item.pneumaticcraft.heat_frame": (
        "인벤토리에 부착할 수 있습니다. 인접한 열원으로 가열하면 인벤토리의 아이템을 "
        "제련하고, 냉각하면 아이템을 얼리려고 합니다. 결과 아이템이 들어갈 공간이 있어야 "
        "작동합니다. 열을 더 많이 공급할수록 빨라지며 초당 최대 1개를 제련할 수 "
        "있습니다. 냉각도 온도가 낮을수록 빨라집니다."
    ),
    "gui.tooltip.item.pneumaticcraft.charging_module": (
        "이 모듈이 가리키는 인벤토리의 가압 가능한 아이템을 가압하거나 감압합니다. "
        "튜브와 아이템의 압력 차이에 따라 공기가 아이템으로 들어가거나 아이템에서 "
        "나옵니다.\n\n모듈 확장 카드를 설치하면 공기가 훨씬 빠르게 흐릅니다."
    ),
    "pneumaticcraft.armor.hacking.finished.disabled": "비활성화됨",
    "pneumaticcraft.config.common.advanced.dont_update_infinite_water_sources": (
        "무한 물 생성 블록의 상태를 갱신하지 않음"
    ),
    "pneumaticcraft.gui.programmer.button.import": (
        "프로그램 가져오기\n§7§oShift를 누르면 프로그램 병합"
    ),
    "pneumaticcraft.gui.tab.problems.solar_compressor.efficiency": (
        "§f압축기가 최적 효율보다 낮게 작동하고 있습니다.\n효율: %s\n\n"
        "§0최대 효율에 도달하려면 기계를 약 350°C까지 가열하되 %s°C를 넘기지 "
        "마세요!\n"
    ),
    "pneumaticcraft.gui.remote.tooltip.boundToSecurityStation": (
        "%s의 보안 스테이션에 연결됨"
    ),
    "pneumaticcraft.gui.progWidget.comment.tooltip.freeToUse": (
        "§a이 조각은 퍼즐 조각을 소모하지 않습니다"
    ),
    "gui.tooltip.item.pneumaticcraft.transfer_gadget": (
        "인벤토리나 탱크 옆면에 설치하면 부착된 블록과 인접한 인벤토리/탱크 사이에서 "
        "아이템(2초당 1개)과 유체(2초당 100mB)를 천천히 옮깁니다. 별도의 블록 공간은 "
        "차지하지 않습니다.\n빈손이나 물류 설정기로 우클릭: 전송 방향 전환\n물류 "
        "설정기를 들고 몸을 숙인 채 우클릭: 가젯 분리(또는 그냥 공격해도 됩니다!)"
    ),
    "pneumaticcraft.armor.gui.coordinateTracker.navigateToSurface": "지상으로 이동...",
    "pneumaticcraft.gui.micromissile.modeTooltip": (
        "§e유도 모드: §f미사일이 개체 필터와 일치하는 가장 가까운 대상을 적극적으로 "
        "탐색해 추적합니다. 최고 속도, 회전 속도, 피해량의 균형을 조절할 수 있습니다.\n"
        "§e직선 모드: §f미사일이 직선으로만 날아가지만 매우 빠르고 큰 피해를 줍니다."
    ),
    "pneumaticcraft.gui.pastebin.retrievingFromPastebin": "Pastebin에서 불러오는 중...",
    "pneumaticcraft.gui.redstoneModule.operation_compare": "상수 비교",
    "pneumaticcraft.gui.remote.tooltip.sneakRightClickToEdit": (
        "§a몸을 숙인 채 우클릭하여 편집"
    ),
    "pneumaticcraft.gui.tab.info.item.armor.feet.jet_bootsUpgrade": (
        "§0부츠에 제트 부츠 업그레이드를 설치하면 많은 공기를 소모하는 대신 제한적으로 "
        "비행할 수 있습니다. 업그레이드가 활성화된 동안 점프 키(기본값: Space)를 누르면 "
        "바라보는 방향으로 추진됩니다. 점프 키를 놓으면 천천히 안전하게 내려가며, 몸을 "
        "숙이면 더 빨리 하강합니다.\n더 빠르게 비행하고 공기를 더 많이 소모하는 5단계의 "
        "업그레이드가 있습니다. 3단계 이상에서는 방어구 GUI에서 건축가 모드를 켤 수 "
        "있습니다. 크리에이티브 비행에 가까운 조작과 빠른 공중 블록 파괴 기능을 제공하지만 "
        "이동 속도는 낮아집니다. 5단계에서는 하강하지 않고 제자리에 떠 있을 수도 "
        "있습니다.\n제트 부츠는 수중에서도 작동하지만 공기를 훨씬 더 많이 소모합니다."
    ),
    "pneumaticcraft.gui.tab.info.item.armor.legs.jumpingUpgrade": (
        "§0각반에 도약 업그레이드를 설치하면 더 높이 점프할 수 있습니다. 더 높이 "
        "점프하고 공기를 더 많이 소모하는 4단계가 있습니다. 점프하면서 몸을 숙이면 "
        "1단계 업그레이드와 같은 높이로만 점프합니다. 낙하 피해 방지 기능도 포함되므로 "
        "공압 부츠를 따로 신지 않아도 됩니다."
    ),
    "gui.tooltip.item.pneumaticcraft.jackhammer": (
        "강력하고 다재다능한 굴착 도구입니다. 사용하려면 드릴 비트를 설치하세요.\n"
        "▶ 몸을 숙인 채 우클릭: 설정 GUI 열기\n"
        "▶ 몸을 숙인 채 마우스 휠: 굴착 모드 전환"
    ),
    "gui.tooltip.item.pneumaticcraft.memory_stick": (
        "플레이어 경험치를 저장합니다.\n▶ 우클릭: 1레벨 저장\n"
        "▶ 몸을 숙인 채 우클릭: 1레벨 회수\n▶ 좌클릭: 경험치 구슬 자동 흡수 전환"
    ),
    "gui.tooltip.item.pneumaticcraft.minigun": (
        "손에 들고 사용하는 무기입니다. 총기 탄약을 탄창에 넣어야 작동합니다.\n"
        "▶ 몸을 숙인 채 우클릭: 탄창 열기\n"
        "▶ 몸을 숙인 채 마우스 휠: 잠글 탄약 슬롯 순환\n"
        "충전소에서 이 미니건에 업그레이드를 설치할 수 있습니다."
    ),
    "gui.tooltip.item.pneumaticcraft.network_api": (
        "드론 프로그램을 저장하는 부품입니다. 네트워크 데이터 저장소와 달리 프로그래밍할 "
        "때 퍼즐 조각을 소모합니다. 프로그래밍 가능 제어기에서 실행할 프로그램으로 "
        "사용하거나, 외부 프로그램 조각을 사용하는 드론에 연결할 수 있습니다."
    ),
    "pneumaticcraft.armor.gui.misc.colors.resetTooltip": (
        "이전 색상으로 되돌립니다. Shift를 누르면 모든 색상을 초기값으로 되돌립니다."
    ),
    "pneumaticcraft.death.drone": "드론이 %s [%s, %s %s]에서 파괴되었습니다.",
    "pneumaticcraft.gui.amadron.addTrade.problems.noSellingOrPayingBlock": (
        "재입고하거나 대금을 받을 위치를 선택하지 않았습니다.\n§0아마드론 태블릿으로 "
        "아이템/유체 위치를 선택하거나 GPS 버튼으로 사용자 지정 위치를 선택하세요."
    ),
    "pneumaticcraft.gui.amadron.button.selectPaymentBlock.tooltip": (
        "플레이어가 판매 제안을 구매했을 때 아마드론이 대금을 넣을 인벤토리나 탱크를 "
        "선택하세요.\n§7기본적으로 이 아마드론 태블릿에 지정된 인벤토리/탱크를 사용합니다."
    ),
    "pneumaticcraft.gui.amadron.button.selectSellingBlock.tooltip": (
        "아마드론이 판매 제안을 재입고할 자원을 가져올 인벤토리나 탱크를 선택하세요.\n"
        "§7기본적으로 이 아마드론 태블릿에 지정된 인벤토리/탱크를 사용합니다."
    ),
    "pneumaticcraft.gui.logistics_frame.min_fluid.tooltip": (
        "이 프레임은 한 번에 이 양보다 적은 유체를 주문하지 않습니다. 드론이 적은 양을 "
        "여러 번 나르는 대신 한 번에 효율적으로 운반하게 할 때 유용합니다. 요청 수량보다 "
        "작은 값으로 설정하세요."
    ),
    "pneumaticcraft.gui.logistics_frame.stock_items.tooltip": (
        "이 프레임은 항상 지정한 수량의 아이템을 재고로 유지하며, 이 수량보다 적게 "
        "남으면 아이템을 공급하지 않습니다."
    ),
    "pneumaticcraft.gui.tab.info.item.armor.generic.airConditioningUpgrade": (
        "§0공기 조절 업그레이드는 적당한 공기를 소모해 체온을 조절합니다. 방어구 각 "
        "부위가 필요에 따라 몸을 식히거나 데워 쾌적한 체온을 유지합니다. 모든 부위에 "
        "설치하면 가장 효과적이지만 일부만 설치해도 효과가 있습니다."
    ),
    "pneumaticcraft.gui.tab.info.item.armor.generic.armorUpgrade": (
        "§0방어구 업그레이드는 해당 부위의 방어력을 조금 높입니다. 2개를 설치하면 "
        "다이아몬드 방어구와 같은 방어력이 되며, 최대 개수를 설치하면 방어력이 크게 "
        "높아집니다."
    ),
    "pneumaticcraft.gui.tab.info.item.armor.generic.creativeUpgrade": (
        "§0방어구 부위에 크리에이티브 업그레이드를 설치하면 해당 부위의 내구도가 "
        "줄지 않고 공기도 소모하지 않습니다."
    ),
    "pneumaticcraft.gui.tab.info.item.armor.generic.gildedUpgrade": (
        "§0방어구 부위에 도금 업그레이드를 설치하면 피글린이 해당 부위를 금 방어구로 "
        "인식합니다."
    ),
    "pneumaticcraft.gui.tab.info.item.armor.generic.item_lifeUpgrade": (
        "§0아이템 수명 업그레이드는 공기를 소모해 해당 방어구 부위를 천천히 자동 "
        "수리합니다. 여러 개를 설치하면 더 빨리 수리하지만 공기 효율은 점점 낮아집니다."
    ),
    "pneumaticcraft.gui.tab.info.item.armor.generic.thaumcraftUpgrade": (
        "§0Thaumcraft 업그레이드를 설치하면 해당 마도사 방어구 부위와 같은 비스 할인을 "
        "받습니다."
    ),
    "pneumaticcraft.gui.tab.info.item.drone.armorUpgrade": (
        "§0방어구 업그레이드는 드론이 받는 물리 피해를 줄입니다. 하나만 설치해도 "
        "플라스틱 건축 벽돌™에 착륙할 때 받는 피해를 막습니다. 업그레이드 하나당 방어력 "
        "1이므로 15개는 철 방어구 한 벌과 같습니다.\n다만 6개를 초과해 설치하면 드론의 "
        "이동 속도가 조금 느려지므로 방어력과 속도의 균형을 맞춰야 합니다."
    ),
    "pneumaticcraft.gui.tab.info.item.drone.chunkloaderUpgrade": (
        "§0청크 로더 업그레이드 1개를 설치하면 드론이 있는 청크를 계속 불러옵니다. "
        "2개는 동서남북 십자 모양의 5청크를, 3개는 3x3 영역의 9청크를 불러옵니다.${br}"
        "이 기능으로 드론이 불러오지 않은 청크로 순간이동할 수는 없습니다. 필요하면 설정의 "
        "'allow_navigate_to_unloaded_chunks'를 확인하세요."
    ),
    "pneumaticcraft.gui.tab.info.item.jackhammer.magnetUpgrade": (
        "§0자석 업그레이드를 설치하고 광맥 굴착 모드를 사용하면 부서진 모든 블록이 처음 "
        "캔 블록의 위치에 떨어집니다. 이 모드에서만 공기를 조금 더 소모합니다."
    ),
    "pneumaticcraft.gui.tab.problems.amadron.noInventory": (
        "§f인벤토리 또는 유체 탱크가 없습니다.\n§0아마드론 태블릿을 들고 인벤토리나 "
        "유체 탱크를 우클릭하세요."
    ),
    "pneumaticcraft.gui.universalSensor.desc.block_heat": (
        "GPS (영역) 도구로 지정한 블록의 온도를 감시합니다. 감시하는 블록의 온도가 "
        "입력란의 온도(°C)보다 높으면 레드스톤 신호 세기 15를, 아니면 0을 출력합니다.\n"
        "입력란이 비어 있으면 0°C에서 신호 0, 400°C에서 신호 15가 되도록 온도에 "
        "비례해 출력합니다.\n위치가 여러 개면 가장 온도가 높은 위치를 사용합니다."
    ),
    "pneumaticcraft.message.amadron.playerBought": (
        "§e[Amadron] §6%s§b이(가) 다음 제안을 §6%d§b회 구매했습니다: §6%s§b, 대금: "
        "§6%s§b."
    ),
    "pneumaticcraft.message.dispenser.direction": "§e배출 방향: %s",
    "gui.tooltip.block.pneumaticcraft.programmable_controller": (
        "프로그래밍 가능 제어기는 드론을 대신할 수 있는 기계입니다. 네트워크 API 또는 "
        "드론을 프로그래밍해 기어 슬롯에 넣으세요. 제어기는 10mL/틱의 공기를 사용하며 "
        "대부분의 프로그램 조각을 실행합니다(사용할 수 없는 조각은 ‘제외된 조각’ 탭을 "
        "참조하세요). 아이템과 유체는 ‘드론’ 인벤토리에 연결된 블록을 통해 넣거나 뺄 수 "
        "있습니다.\n\n이 기계는 개체의 길 찾기를 사용하지 않으므로 채석장 같은 대규모 "
        "작업에 특히 적합합니다."
    ),
    "gui.tooltip.block.pneumaticcraft.refinery": (
        "정유기는 유체를 여러 유체로 정제합니다. 기본적으로 원유를 디젤, 등유, 휘발유 "
        "및 LPG(액화 석유 가스)로 정제합니다.\n\n정유기 출력부를 2개, 3개 또는 4개 "
        "수직으로 쌓아야 작동하며, 4개를 사용하면 가장 좋은 결과를 얻습니다. 정유기에 "
        "더 많은 열을 공급할수록 더 빠르게 작동합니다."
    ),
    "gui.tooltip.block.pneumaticcraft.vacuum_trap.brief": (
        "근처의 개체를 흡수합니다. 음압과 설치된 생성기 코어가 필요합니다.\n"
        "몸을 숙인 채 우클릭하거나 레드스톤 신호를 보내 활성/비활성 상태를 전환합니다."
    ),
    "pneumaticcraft.gui.entityFilter.helpText": (
        "§a§n개체 필터링\n\n"
        "§e@player§f: 모든 플레이어와 일치\n"
        "§e@mob§f: 모든 적대적 생물과 일치\n"
        "§e@animal§f: 모든 비적대적 생물과 일치\n"
        "§e@animal(age=adult)§f: 모든 성체 동물과 일치\n"
        "§e@animal(age=baby)§f: 모든 새끼 동물과 일치\n"
        "§e@living(aquatic=yes)§f: 모든 수생 생물과 일치\n"
        "§e@mob(undead=yes)§f: 모든 언데드 몹과 일치\n"
        "§e@living(arthropod=yes)§f: 모든 절지동물 생물과 일치\n"
        "§e@animal(breedable=yes)§f: 번식할 준비가 된 모든 동물과 일치\n"
        "§e@player(holding=minecraft:stick)§f: 막대기를 든 모든 플레이어와 일치\n"
        "§e@player(holding!=minecraft:stick)§f: 막대기를 들지 않은 모든 플레이어와 일치\n"
        "§e@minecart§f: 모든 광산 수레와 일치\n"
        "§e@boat§f: 모든 보트와 일치\n"
        "§e@living§f: 모든 살아 있는 개체와 일치\n"
        "§e@item§f: 모든 아이템 개체와 일치\n"
        "§e@drone§f: 모든 드론 개체와 일치\n"
        "§e@orb§f: 모든 경험치 구슬과 일치\n"
        "§e@mob(mod=minecraft)§f: Minecraft가 추가한 몹만 일치\n"
        "§eCreeper§f: 크리퍼와 일치\n"
        "§e'MineMaarten'§f: 이름이 'MineMaarten'인 개체와 일치\n"
        "§ec*§f: 이름이 'c'로 시작하는 모든 개체와 일치(예: 크리퍼, 소)\n"
        "§e*pig*§f: 이름에 'pig'가 들어가는 모든 개체와 일치(예: 돼지, 좀비화 피글린)\n"
        "§ecreeper;zombie§f: 크리퍼와 좀비 모두 일치\n"
        "§e!@player§f: 플레이어를 제외한 모든 개체와 일치\n"
        "§e!creeper;zombie§f 크리퍼와 좀비를 제외한 모든 개체와 일치\n\n"
        "• 대소문자를 구분하지 않습니다\n"
        '• 필터 맨 앞에 "!"를 붙이면 판정을 반대로 합니다\n'
        '• 하나의 필터에서 여러 조건을 쓰려면 ";"(세미콜론)로 구분합니다(OR 조건)'
    ),
    "pneumaticcraft.gui.tab.info.heat": (
        "이 기계는 열이 필요하거나 열을 생성합니다. 기계 옆에 열을 내는 블록을 놓아 열을 "
        "공급할 수 있습니다. 볼텍스 튜브는 빠르지만 동력이 필요하고, 용암은 빠르지만 "
        "굳으며, 횃불은 매우 느립니다. 기계를 식히려면 열원을 치우고 방열판이나 얼음, "
        "꽁꽁 언 얼음, 푸른얼음 같은 차가운 블록을 놓으세요."
    ),
    "pneumaticcraft.gui.tab.minigun.slotInfo": (
        "미니건은 보통 탄약이 들어 있는 슬롯 중 번호가 가장 낮은 슬롯에서 탄약을 "
        "꺼냅니다.\n\n슬롯에서 §a%s§f 키를 누르면 해당 슬롯의 잠금을 전환합니다. "
        "잠그면 미니건은 그 슬롯의 탄약만 사용합니다.\n\n여러 탄약 종류를 가지고 다닐 "
        "때 슬롯 잠금이 유용합니다."
    ),
    "pneumaticcraft.gui.tab.problems.assembly_controller.missingMachine": (
        "§f기계 누락!\n§0삽입한 프로그램에 필요한 기계가 모두 갖춰지지 않았습니다. "
        "조립 시스템에 %s 기계를 하나 추가하세요."
    ),
    "pneumaticcraft.gui.thermopneumatic.moveInput": (
        "유체 이동\n§7가능하면 입력 탱크의 유체를 출력 탱크로 옮깁니다\n"
        "§oShift를 누르면 유체를 버립니다"
    ),
    "pneumaticcraft.gui.universalSensor.desc.within_range": (
        "범위 안에 있는 개체마다 레드스톤 신호 세기를 1씩 높입니다. 텍스트 입력란에 "
        "이름을 입력해 특정 개체를 선택할 수 있습니다.\n개체 필터 문법의 자세한 도움말은 "
        "F1을 누르세요."
    ),
    "pneumaticcraft.gui.universalSensor.desc.world_tick_time": (
        "이 범용 센서가 있는 월드를 서버가 갱신하는 데 걸린 시간에 따라 레드스톤 신호를 "
        "출력합니다. 시간은 Forge의 /tps 명령과 같은 방식으로 계산합니다. 텍스트 입력란에서 "
        "다음과 같이 해상도를 정할 수 있습니다:\n신호 세기 = 틱 시간(ms) × 입력값\n"
        "예: 틱 시간 = 20ms, 입력값 = '0.5'\n신호 세기 = 20 × 0.5 = 10"
    ),
    "pneumaticcraft.gui.universalSensor.desc.world_weather_forecast": (
        "비가 내리기까지 남은 시간에 따라 레드스톤 신호를 출력합니다.\n"
        "신호 세기 = 15 - 비가 내리기까지 남은 시간(분)\n"
        "예: 10분 뒤에 비가 내리면 신호 세기는 5입니다."
    ),
    "gui.tooltip.block.pneumaticcraft.vacuum_trap": (
        "근처의 개체를 흡수합니다. 음압과 설치된 생성기 코어가 필요합니다.\n\n"
        "덫의 유체 탱크에 기억의 정수가 100mB 이상 들어 있으면 개체를 흡수할 때 "
        "무작위로 큰 보너스가 적용되며 기억의 정수가 소모됩니다.\n\n플레이어, 드론, "
        "바닐라 생성기에서 생성된 몹은 흡수할 수 없습니다.\n\n몸을 숙인 채 우클릭하거나 "
        "레드스톤 신호를 보내 활성/비활성 상태를 전환합니다."
    ),
    "gui.tooltip.item.pneumaticcraft.drill_bit_compressed_iron": (
        "철보다 빠름\n굴착 모드: 1x1, 1x2, 1x3"
    ),
    "pneumaticcraft.gui.aphorismTile.helpText": (
        "§a§n격언 타일 편집기§r\n\n"
        "§e← → ↑ ↓:§r 커서 이동\n§eHome:§r 줄 처음\n§eEnd:§r 줄 끝\n"
        "§eReturn:§r 줄바꿈 삽입\n§eBackspace:§r 커서 앞 문자 삭제\n"
        "§eDelete:§r 커서 뒤 문자 삭제\n§eAlt-Delete:§r 현재 줄 삭제\n"
        "§eShift-Delete:§r 모두 지우기\n§eEscape:§r 편집 끝내기\n"
        "§eAlt + §ochr§r: 제어 코드 삽입\n §f- 코드: 0-9, a-f, l, m, n, o, r\n"
        "§eCtrl-V:§r 클립보드 텍스트 붙여넣기\n§eCtrl-D:§r 극적인 문구 불러오기!"
    ),
    "pneumaticcraft.gui.tab.info.item.armor.chest.dispenserUpgrade": (
        "§0발사기 업그레이드를 하나 이상 설치하면 발사 키(기본값: Ctrl + C)를 눌렀다 "
        "놓아 보조 손 슬롯의 아이템과 블록을 발사할 수 있습니다.\n\n"
        "• 일부 아이템과 블록은 발사기처럼 개체 형태로 특별히 배치됩니다.\n"
        "• 특별한 동작이 없는 아이템은 아이템 개체로 발사됩니다.\n"
        "• 특별한 동작이 없는 블록은 ‘회전 블록’ 개체로 발사되며, 다른 블록에 부딪히면 "
        "다시 블록으로 설치되려고 합니다.\n\n발사 거리를 늘리려면 발사기 업그레이드를 "
        "최대 4개까지 설치할 수 있습니다."
    ),
    "pneumaticcraft.gui.tab.info.item.armor.head.dispenserUpgrade": (
        "§0개체 추적기 업그레이드와 함께 사용하면 발사기 업그레이드로 작동 중인 드론을 "
        "디버그하고 감시할 수 있습니다. 드론을 조준한 뒤 드론 디버그 단축키(기본값: Y)를 "
        "누르고 헬멧 옵션 GUI(기본값: U)를 여세요.\n\n근처 드론이 관심을 보이는 "
        "블록(32블록 이내)에는 레드스톤 입자 효과도 표시됩니다."
    ),
    "pneumaticcraft.gui.tab.info.item.drone.creativeUpgrade": (
        "§0크리에이티브 공급 업그레이드는 모든 공기 소모를 없애며, 미니건 업그레이드가 "
        "설치된 경우 탄약도 소모하지 않게 합니다. 단, 드론은 여전히 탄약 상자를 "
        "소지해야 합니다."
    ),
    "pneumaticcraft.gui.tab.info.item.minigun.creativeUpgrade": (
        "§0크리에이티브 공급 업그레이드는 미니건에 무한 탄약을 제공하고 공기 소모를 "
        "없앱니다."
    ),
    "pneumaticcraft.gui.tab.info.security_station.hacking": (
        "§0보안 스테이션 해킹 콘솔입니다. 해커는 IO 포트에서 시작하며, 인접한 네트워크 "
        "노드를 좌클릭해 해킹할 수 있습니다. 노드 크기에 따라 해킹 시간이 달라집니다.\n"
        "노드를 점령할 때마다 진단 서브루틴에 탐지될 수 있으며, 탐지되면 IO 포트에 있는 "
        "해커를 역추적하기 시작합니다.\n서브루틴이 IO 포트까지 추적하면 패배합니다. 실제 "
        "해킹 중 진단 서브루틴이 작동 중이라면 큰 피해도 입습니다.\n진단 서브루틴이나 "
        "네트워크 레지스트리를 해킹하면 승리하며, 소유자가 재부팅할 때까지 보안 "
        "스테이션은 주변 영역을 보호하지 못합니다."
    ),
    "pneumaticcraft.gui.tab.info.security_station.stopWorm": (
        "§0STOP! 웜은 작동 중인 진단 서브루틴의 추적을 약 5초 동안 멈춥니다. 탐지된 "
        "뒤 STOP! 웜 버튼을 누르면 이 소프트웨어가 소모됩니다."
    ),
    "pneumaticcraft.message.seismicSensor.foundOilDetails": (
        "§a[지진 센서] %s %s§am 아래에서 발견: 최소 %s§a양동이"
    ),
}

INLINE_TERM_REPLACEMENTS = (
    ("Creative Supply Upgrade", "크리에이티브 공급 업그레이드"),
    ("Camouflage Applicator", "위장 도포기"),
    ("Logistics Active Provider Frame", "능동 공급자 물류 프레임"),
    ("Logistics Configurator", "물류 설정기"),
    ("Programmable Controller", "프로그래밍 가능 제어기"),
    ("Assembly Controller", "조립 제어기"),
    ("Refinery Controller", "정유기 제어기"),
    ("Refinery Outputs", "정유기 출력부"),
    ("Refinery Output", "정유기 출력부"),
    ("Security Station", "보안 스테이션"),
    ("Entity Tracker", "개체 추적기"),
    ("Block Tracker", "블록 추적기"),
    ("Spawner Agitator", "생성기 교반기"),
    ("Spawner Core", "생성기 코어"),
    ("Storage Frames", "저장 물류 프레임"),
    ("Storage Frame", "저장 물류 프레임"),
    ("Requester Frame", "요청자 물류 프레임"),
    ("Logistics Drones", "물류 드론"),
    ("Liquid Hopper", "유체 호퍼"),
    ("Heat Frame", "열 프레임"),
    ("Vortex Tube", "볼텍스 튜브"),
    ("Vortex Cannon", "볼텍스 캐논"),
    ("UV Light Box", "UV 라이트 박스"),
    ("Etching Acid", "에칭 산"),
    ("Compressed Iron", "압축 철"),
    ("Iron Boots", "철 부츠"),
    ("Iron Helmet", "철 헬멧"),
    ("Iron Leggings", "철 각반"),
    ("Armor Upgrades", "방어구 업그레이드"),
    ("Armor Upgrade", "방어구 업그레이드"),
    ("Pneumatic Armor GUI", "공압 방어구 GUI"),
    ("Remote", "리모컨"),
    ("Middle-Click", "가운데 클릭"),
    ("Right-Click", "우클릭"),
    ("Nuke Node", "노드 파괴"),
    ("Fortify Node", "노드 강화"),
    ("Lava", "용암"),
    ("Torches", "횃불"),
)

WORD_TERM_REPLACEMENTS = (
    ("Advanced Air Compressor", "고급 공기 압축기"),
    ("Advanced Liquid Compressor", "고급 액체 압축기"),
    ("Thermopneumatic Processing Plant", "열공압 처리 공장"),
    ("Pressure Chamber Interface", "압력 챔버 인터페이스"),
    ("Pressure Chamber", "압력 챔버"),
    ("Network Data Storage", "네트워크 데이터 저장소"),
    ("Network Storage", "네트워크 데이터 저장소"),
    ("Network API", "네트워크 API"),
    ("Entity Filter", "개체 필터"),
    ("Item Filter", "아이템 필터"),
    ("Assembly System", "조립 시스템"),
    ("Assembly Program", "조립 프로그램"),
    ("Thermal Compressor", "열 압축기"),
    ("Liquid Compressor", "액체 압축기"),
    ("Air Compressor", "공기 압축기"),
    ("Electrostatic Compressor", "정전기 압축기"),
    ("Security Station", "보안 스테이션"),
    ("Universal Sensor", "범용 센서"),
    ("Charging Station", "충전소"),
    ("Drone Interface", "드론 인터페이스"),
    ("Elevator Caller", "엘리베이터 호출기"),
    ("Elevator Base", "엘리베이터 기반"),
    ("Transfer Gadget", "전송 가젯"),
    ("Crop Support", "작물 지지대"),
    ("GPS Area Tool", "GPS 영역 도구"),
    ("GPS Tool", "GPS 도구"),
    ("Fluid Mixer", "유체 혼합기"),
    ("Enchanting Table", "마법 부여대"),
    ("Silk Touch", "섬세한 손길"),
    ("Tripwire Hooks", "철사 덫 갈고리"),
    ("End Portal", "엔드 차원문"),
    ("Aphorism Tiles", "격언 타일"),
    ("Signs", "표지판"),
    ("Heat Sink", "방열판"),
    ("Vortex Tube", "볼텍스 튜브"),
    ("Air Cannon", "에어 캐논"),
    ("Smart Chest", "스마트 상자"),
    ("Vacuum Trap", "진공 덫"),
    ("Memory Essence", "기억의 정수"),
    ("Tag Filter", "태그 필터"),
    ("Iron Bars", "철창"),
    ("Mob Spawner", "몹 생성기"),
    ("Silverfish", "좀벌레"),
    ("Redstone", "레드스톤"),
    ("redstone", "레드스톤"),
    ("Programmer", "프로그래머"),
    ("Conditions", "조건"),
    ("Condition", "조건"),
    ("Coordinates", "좌표"),
    ("Coordinate", "좌표"),
    ("Drones", "드론"),
    ("Drone", "드론"),
    ("Elevator", "엘리베이터"),
    ("Dispenser", "발사기"),
    ("Minigun", "미니건"),
    ("Ethanol", "에탄올"),
    ("Diesel", "디젤"),
    ("Fortune", "행운"),
    ("Sneak", "몸을 숙인 채"),
    ("Surface", "지상"),
    ("Tier", "등급"),
    ("tier", "등급"),
    ("Mob", "몹"),
    ("wrench", "렌치"),
    ("Refinery", "정유기"),
    ("Furnace", "화로"),
    ("Plastic", "플라스틱"),
    ("Lubricant", "윤활유"),
    ("Upgrades", "업그레이드"),
    ("Upgrade", "업그레이드"),
    ("Area", "영역"),
    ("Text", "텍스트"),
)

TERM_REPLACEMENTS = (
    ("열압식 가공 공장", "열공압 처리 공장"),
    ("열압식 처리 공장", "열공압 처리 공장"),
    ("열압 처리 공장", "열공압 처리 공장"),
    ("기본 저장소 프레임", "기본 저장 물류 프레임"),
    ("Default 스토리지 프레임", "기본 저장 물류 프레임"),
    ("패시브 공급자 프레임", "수동 공급자 물류 프레임"),
    ("활성 공급자 프레임", "능동 공급자 물류 프레임"),
    ("스토리지 프레임", "저장 물류 프레임"),
    ("저장소 프레임", "저장 물류 프레임"),
    ("에어리얼 인터페이스", "공중 인터페이스"),
    ("센트리 터렛", "감시 포탑"),
    ("센트리 건", "감시 포탑"),
    ("공압식 도어 베이스", "공압 문 기반"),
    ("공압식 도어", "공압 문"),
    ("액체 플라스틱", "용융 플라스틱"),
    ("공기 사용량", "공기 소모량"),
    ("공기 비용", "공기 소모량"),
    ("공기료", "공기 소모량"),
    ("공기 소모과", "공기 소모가"),
    ("리소스", "자원"),
    ("품목", "아이템"),
    ("갑옷", "방어구"),
    ("레깅스", "각반"),
    ("과정가", "과정이"),
    ("에칭 산를", "에칭 산을"),
    ("리모컨를", "리모컨을"),
    ("이 작품", "이 조각"),
    ("작품의", "조각의"),
    ("작품이", "조각이"),
    ("배치하십시오", "배치하세요"),
    ("삽입하십시오", "넣으세요"),
    ("참조하십시오", "참조하세요"),
    ("읽으십시오", "읽으세요"),
    ("고성능 에어컨 프레서", "고급 공기 압축기"),
    ("에어컨 프레서", "공기 압축기"),
    ("고성능 에어 컴프레서", "고급 공기 압축기"),
    ("열 공기 처리 플랜트", "열공압 처리 공장"),
    ("열 공압 처리 플랜트", "열공압 처리 공장"),
    ("공중 공용영역", "공중 인터페이스"),
    ("프로그래머블 컨트롤러", "프로그래밍 가능 제어기"),
    ("프로그램 가능한 컨트롤러", "프로그래밍 가능 제어기"),
    ("리퀘스터 프레임", "요청자 물류 프레임"),
    ("디스펜서 업그레이드", "발사기 업그레이드"),
    ("볼륨 업그레이드", "용량 업그레이드"),
    ("개체 트래커", "개체 추적기"),
    ("블록 트래커", "블록 추적기"),
    ("점핑 업그레이드", "도약 업그레이드"),
    ("점프 업그레이드", "도약 업그레이드"),
    ("에어컨 업그레이드", "공기 조절 업그레이드"),
    ("청크로더 업그레이드", "청크 로더 업그레이드"),
    ("무인 항공기", "드론"),
    ("물류 구성자", "물류 설정기"),
    ("공중 비용", "공기 소모"),
    ("실행 속도", "이동 속도"),
    ("가슴판", "흉갑"),
    ("히트 파이프", "열 파이프"),
    ("카마도", "화로"),
    ("정유소", "정유기"),
    ("디스플레이 선반", "진열 선반"),
    ("디스플레이 테이블", "진열대"),
    ("서모 스탯", "온도 조절기"),
    ("압력 게이지", "압력계"),
    ("공기포", "에어 캐논"),
    ("에어 캐니스터", "공기 용기"),
    ("레귤레이터 - 모듈", "조절기 모듈"),
    ("마이크로 미사일", "마이크로미사일"),
    ("레드 스톤", "레드스톤"),
    ("스피드 업그레이드", "속도 업그레이드"),
    ("바이오 디젤", "바이오디젤"),
    ("E엘리베이터", "엘리베이터"),
    ("E 엘리베이터", "엘리베이터"),
    ("E외부", "외부"),
    ("pne umaticcraft", "pneumaticcraft"),
    ("화타석과 타격", "부싯돌과 부시"),
    ("드론가", "드론이"),
    ("드론를", "드론을"),
    ("드론는", "드론은"),
    ("선택사항", "선택 사항"),
    ("스니크 + 우클릭", "몸을 숙인 채 우클릭"),
    ("트로코", "광산 수레"),
    ("감김 피해", "범위 피해"),
    ("1 하나", "하나"),
    ("2 이상의", "둘 이상의"),
    ("1 틱 당", "틱당"),
    ("할 수있는", "할 수 있는"),
    ("신뢰할 수있는", "신뢰할 수 있는"),
    ("해야합니다", "해야 합니다"),
    ("도움이됩니다", "도움이 됩니다"),
    ("참조하십시오", "참조하세요"),
    ("사용하십시오", "사용하세요"),
    ("확인하십시오", "확인하세요"),
    ("드릴링", "굴착"),
    ("크래프트", "제작"),
    ("공예", "제작"),
    ("MOD", "모드"),
    ("항목", "아이템"),
    ("기능 업그레이드", "업그레이드"),
    ("업그레이드 기능", "업그레이드"),
    ("개선 사항", "업그레이드"),
    ("개량", "업그레이드"),
    ("압축공기", "압축 공기"),
    ("공기통", "공기 용기"),
    ("공기 캐니스터", "공기 용기"),
    ("압력관", "압력 튜브"),
    ("압력실", "압력 챔버"),
    ("뉴매틱", "공압"),
    ("공압식 갑옷", "공압 방어구"),
    ("드론 무인 비행기", "드론"),
    ("엔티티", "개체"),
    ("엔터티", "개체"),
    ("스포너", "생성기"),
    ("버킷", "양동이"),
    ("구성요소", "구성 요소"),
    ("나이트 비전", "야간 투시"),
    ("Aerial 인터페이스", "공중 인터페이스"),
    ("몰입형 엔지니어링", "Immersive Engineering"),
    ("항공 비용", "공기 소모"),
    ("항공료", "공기 소모"),
    ("액세스", "접근"),
    ("프로세스", "과정"),
    ("액체 호퍼", "유체 호퍼"),
    ("유체 믹서", "유체 혼합기"),
    ("원유 오일", "원유"),
    ("식물성 오일", "식물성 기름"),
    ("윤활제", "윤활유"),
    ("가솔린", "휘발유"),
    ("케로신", "등유"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("웅크리고", "몸을 숙인 채"),
    ("몰래", "몸을 숙인 채"),
)

COLORS = {
    "black": "검은색",
    "blue": "파란색",
    "brown": "갈색",
    "cyan": "청록색",
    "gray": "회색",
    "green": "초록색",
    "light_blue": "하늘색",
    "light_gray": "회백색",
    "lime": "연두색",
    "magenta": "자홍색",
    "orange": "주황색",
    "pink": "분홍색",
    "purple": "보라색",
    "red": "빨간색",
    "white": "흰색",
    "yellow": "노란색",
}

SHAPED_BLOCKS = {
    "reinforced_brick_pillar": "강화 벽돌 기둥",
    "reinforced_brick_slab": "강화 벽돌 반 블록",
    "reinforced_bricks": "강화 벽돌",
    "reinforced_brick_stairs": "강화 벽돌 계단",
    "reinforced_brick_tile": "강화 벽돌 타일",
    "reinforced_brick_wall": "강화 벽돌 담장",
    "compressed_brick_pillar": "압축 벽돌 기둥",
    "compressed_brick_slab": "압축 벽돌 반 블록",
    "compressed_bricks": "압축 벽돌",
    "compressed_brick_stairs": "압축 벽돌 계단",
    "compressed_brick_tile": "압축 벽돌 타일",
    "compressed_brick_wall": "압축 벽돌 담장",
}


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def candidate() -> dict[str, object]:
    """모든 신규 문구의 보호 처리된 자동 번역 후보를 만든다."""
    english = load_json(ENGLISH_FILE)
    sources = load_json(SOURCE_FILE)
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests = {
        value
        for key, value in english.items()
        if sources[key] == "new_translation_required"
        and isinstance(value, str)
        and value not in VALUE_OVERRIDES
        and not family_goal.is_allowed_original(value)
        and not isinstance(cache.get(value), str)
    }
    failures: list[str] = []
    if requests:
        completed = 0
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(ars_family.request_translation, source): source
                for source in sorted(requests)
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                    completed += 1
                    if completed % 25 == 0:
                        write_json(CACHE_FILE, cache)
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("자동 번역 후보 생성 실패:\n" + "\n".join(failures))

    candidates: dict[str, object] = {}
    provenance: Counter[str] = Counter()
    invalid_candidates: list[str] = []
    for key, value in english.items():
        if sources[key] == "project_output_review":
            continue
        if not isinstance(value, str):
            raise TypeError(f"문자열이 아닌 언어 값: {key}")
        if value in VALUE_OVERRIDES:
            translated = VALUE_OVERRIDES[value]
            provenance["manual_term_candidate"] += 1
        elif family_goal.is_allowed_original(value):
            translated = value
            provenance["reviewed_original_candidate"] += 1
        else:
            translated = cache[value]
            provenance["automatic_translation_candidate"] += 1
        errors = family_goal.validate_value(key, value, translated)
        if errors:
            invalid_candidates.append(f"{key}: {'; '.join(errors)}")
        candidates[key] = translated
    write_json(CANDIDATE_FILE, candidates)
    report = {
        "keys": len(english),
        "candidate_keys": len(candidates),
        "candidate_sources": dict(sorted(provenance.items())),
        "invalid_candidates": invalid_candidates,
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "auto_candidate_report.json", report)
    if invalid_candidates:
        raise ValueError("자동 후보 구조 오류:\n" + "\n".join(invalid_candidates))
    return report


def reviewed_value(key: str, source: str, candidate_value: str) -> str:
    """확정 용어와 반복 패턴을 적용한 검수값을 반환한다."""
    if key in KEY_OVERRIDES:
        return KEY_OVERRIDES[key]
    if source in VALUE_OVERRIDES:
        return VALUE_OVERRIDES[source]
    if key.startswith("block.pneumaticcraft.plastic_brick_"):
        color = key.removeprefix("block.pneumaticcraft.plastic_brick_")
        return f"{COLORS[color]} 플라스틱 건축 벽돌™"
    if key.startswith("block.pneumaticcraft.smooth_plastic_brick_"):
        color = key.removeprefix("block.pneumaticcraft.smooth_plastic_brick_")
        return f"매끈한 {COLORS[color]} 플라스틱 건축 벽돌™"
    if key.startswith("block.pneumaticcraft.wall_lamp_inverted_"):
        color = key.removeprefix("block.pneumaticcraft.wall_lamp_inverted_")
        return f"{COLORS[color]} 벽 램프(반전)"
    if key.startswith("block.pneumaticcraft.wall_lamp_"):
        color = key.removeprefix("block.pneumaticcraft.wall_lamp_")
        return f"{COLORS[color]} 벽 램프"
    if key.startswith("block.pneumaticcraft."):
        stem = key.removeprefix("block.pneumaticcraft.")
        if stem in SHAPED_BLOCKS:
            return SHAPED_BLOCKS[stem]
    value = candidate_value
    value = value.replace("\u200b", "")
    for old, new in INLINE_TERM_REPLACEMENTS:
        value = value.replace(old, new)
    for old, new in WORD_TERM_REPLACEMENTS:
        value = re.sub(
            rf"(?<![A-Za-z0-9_]){re.escape(old)}(?![A-Za-z0-9_])", new, value
        )
    for old, new in TERM_REPLACEMENTS:
        value = value.replace(old, new)
    for old, new in (
        ("$(item)E", "$(item)"),
        ("$(thing)E", "$(thing)"),
        ("§0E", "§0"),
        ("§fE", "§f"),
        (" PC B", " PCB"),
        ("방법 그 1", "방법 1"),
        ("방법 그 2", "방법 2"),
        ("하면이를", "하면 이를"),
        ("과정가", "과정이"),
        ("공기 소모으로", "공기 소모가 큰 대신"),
        ("제작가 아니며", "제작할 수 없으며"),
        ("방어구을", "방어구를"),
        ("공기 소모을", "공기 소모를"),
        ("만큼 시원하거나", "만큼 체온을 낮추거나"),
        ("모든 작은 도움이 됩니다", "일부만 설치해도 효과가 있습니다"),
    ):
        value = value.replace(old, new)
    value = re.sub(r"[ \t]+([,.!?%])", r"\1", value)
    value = value.replace("~", "~")
    if key.endswith(".upgrade") and source.endswith(" Upgrade"):
        value = value.removesuffix(" 기능")
        if not value.endswith("업그레이드"):
            value += " 업그레이드"
    return value


def normalize() -> dict[str, object]:
    """후보를 작업본에 반영하고 모든 기존 산출물을 다시 검수한다."""
    english = load_json(ENGLISH_FILE)
    korean = load_json(KOREAN_FILE)
    candidates = load_json(CANDIDATE_FILE)
    changed = 0
    unresolved: list[str] = []
    for key, source_value in english.items():
        if not isinstance(source_value, str):
            raise TypeError(f"문자열이 아닌 언어 값: {key}")
        candidate_value = candidates.get(key, korean[key])
        if not isinstance(candidate_value, str):
            raise TypeError(f"문자열이 아닌 번역 후보: {key}")
        translated = reviewed_value(key, source_value, candidate_value)
        errors = family_goal.validate_value(key, source_value, translated)
        if errors:
            raise ValueError("; ".join(errors))
        if korean[key] != translated:
            korean[key] = translated
            changed += 1
        if source_value == translated and not (
            key in ALLOWED_EXACT_KEYS or family_goal.is_allowed_original(source_value)
        ):
            unresolved.append(key)
    write_json(KOREAN_FILE, korean)
    report = {
        "keys_normalized": len(english),
        "changed": changed,
        "unresolved": len(unresolved),
        "unresolved_examples": unresolved[:30],
        "review_status": "full_existing_korean_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    """전문 검증과 공통 검증을 함께 수행한다."""
    english = load_json(ENGLISH_FILE)
    korean = load_json(KOREAN_FILE)
    errors: list[str] = []
    if list(english) != list(korean):
        errors.append("언어 키 또는 순서 불일치")
    untranslated = []
    for key, source in english.items():
        target = korean.get(key)
        errors.extend(family_goal.validate_value(key, source, target))
        if (
            isinstance(source, str)
            and source == target
            and key not in ALLOWED_EXACT_KEYS
            and not family_goal.is_allowed_original(source)
        ):
            untranslated.append(key)
    if untranslated:
        errors.append(f"미번역 키: {untranslated[:30]}")
    report = {
        "keys": len(english),
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", report)
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("candidate", "normalize", "verify"))
    args = parser.parse_args()
    resolve_source_root()
    if args.command == "candidate":
        result = candidate()
        status = 0
    elif args.command == "normalize":
        result = normalize()
        status = 0
    else:
        result, status = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
