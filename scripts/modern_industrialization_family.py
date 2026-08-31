#!/usr/bin/env python3
"""Modern Industrialization 계열 언어 파일을 전체 재검수하고 검증한다."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from five_family_goal import (
    PROJECT_ROOT,
    is_allowed_original,
    load_json,
    validate_value,
)
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/modern_industrialization"
NAMESPACES = (
    "modern_industrialization",
    "extended_industrialization",
    "industrialization_overdrive",
)

ALLOWED_ORIGINALS = {
    "",
    " ",
    "∞",
    "Alt",
    "EV",
    "EU",
    "HV",
    "I/O",
    "IN",
    "LV",
    "ME Wire",
    "MV",
    "Modern Industrialization",
    "Extended Industrialization",
    "Industrialization Overdrive",
    "SV",
    "Vajra",
    "1x1",
    "3x3",
    "%s ❤",
    "%s%s EU",
    "%s%s EU/t",
    "%s / %s %sEU",
    "%s / %s (%s)",
    "[CurseForge]",
}

KUBEJS_EXTRA_TRANSLATIONS = {
    "block.modern_industrialization.auto_forge": "자동 헤파이스토스 대장간",
    "block.modern_industrialization.deepslate_iridium_ore": "심층암 이리듐 광석",
    "block.modern_industrialization.ev_runic_transformer": "EV→룬 변압기",
    "block.modern_industrialization.runic_crucible": "룬 도가니",
    "block.modern_industrialization.runic_enchanter": "룬 인챈터",
    "block.modern_industrialization.runic_energy_input_hatch": "룬 에너지 입력 해치",
    "block.modern_industrialization.runic_energy_output_hatch": "룬 에너지 출력 해치",
    "block.modern_industrialization.runic_ev_transformer": "룬→EV 변압기",
    "block.modern_industrialization.runic_fluid_input_hatch": "룬 유체 입력 해치",
    "block.modern_industrialization.runic_fluid_output_hatch": "룬 유체 출력 해치",
    "block.modern_industrialization.runic_item_input_hatch": "룬 아이템 입력 해치",
    "block.modern_industrialization.runic_item_output_hatch": "룬 아이템 출력 해치",
    "block.modern_industrialization.runic_storage_unit": "룬 저장 유닛",
    "block.modern_industrialization.runic_superconductor_transformer": "룬→SV 변압기",
    "block.modern_industrialization.star_altar": "룬 별 제단",
    "block.modern_industrialization.superconductor_runic_transformer": "SV→룬 변압기",
    "cable_tier_long.modern_industrialization.runic": "룬",
    "cable_tier_short.modern_industrialization.runic": "룬",
    "machine_casing.extended_industrialization.large_steel_crate": "대형 강철 상자",
    "machine_casing.modern_industrialization.runic": "룬",
    "rei_categories.modern_industrialization.auto_forge": "자동 헤파이스토스 대장간",
    "rei_categories.modern_industrialization.runic_crucible": "룬 도가니",
    "rei_categories.modern_industrialization.runic_enchanter": "룬 인챈터",
    "rei_categories.modern_industrialization.star_altar": "룬 별 제단",
}

BASE_REPLACEMENTS = (
    ("발전된", "고급"),
    ("고도로 고급", "초고급"),
    ("액체 반입", "유체 입력"),
    ("액체 반출", "유체 출력"),
    ("아이템 반입", "아이템 입력"),
    ("아이템 반출", "아이템 출력"),
    ("에너지 반입", "에너지 입력"),
    ("에너지 반출", "에너지 출력"),
    ("기계 껍데기", "기계 외피"),
    ("어셈블러", "조립기"),
    ("조합기", "조립기"),
    ("포지 해머", "단조 망치"),
    ("채광용 드릴", "채굴 드릴"),
    ("채광 드릴", "채굴 드릴"),
    ("융합 원자로", "핵융합로"),
    ("원자력 발전소", "원자로"),
    ("선재압연기", "선재 압연기"),
    ("액체 파이프", "유체 파이프"),
    ("레시피", "제작법"),
    ("퀀텀", "양자"),
    ("데미지", "피해"),
    ("우선 순위", "우선순위"),
    ("스테인리스 강철", "스테인리스강"),
    (" Mox ", " MOX "),
    ("연료 막대", "연료봉"),
    ("연료봉 이중", "이중 연료봉"),
    ("연료봉 사중", "사중 연료봉"),
    ("제작법가", "제작법이"),
    ("제작법를", "제작법을"),
    ("제작법와", "제작법과"),
    ("전기용광로", "전기 용광로"),
    ("개 당", "개당"),
    ("연료 당", "연료당"),
    ("Shift-클릭 으로", "Shift-클릭으로"),
    ("%s 으로", "%s로"),
)

VALUE_TRANSLATIONS = {
    "Extreme Voltage": "극한 전압",
    "High Voltage": "고전압",
    "Low Voltage": "저전압",
    "Medium Voltage": "중전압",
    "Superconductor": "초전도체",
    "Black ME Wire": "검은색 ME 전선",
    "Blue ME Wire": "파란색 ME 전선",
    "Brown ME Wire": "갈색 ME 전선",
    "Cyan ME Wire": "청록색 ME 전선",
    "Gray ME Wire": "회색 ME 전선",
    "Green ME Wire": "초록색 ME 전선",
    "Light Blue ME Wire": "하늘색 ME 전선",
    "Light Gray ME Wire": "회백색 ME 전선",
    "Lime ME Wire": "연두색 ME 전선",
    "Liquid Air Bucket": "액체 공기 양동이",
    "Lubricant Bucket": "윤활유 양동이",
    "Magenta ME Wire": "자홍색 ME 전선",
    "Orange ME Wire": "주황색 ME 전선",
    "Pink ME Wire": "분홍색 ME 전선",
    "Purple ME Wire": "보라색 ME 전선",
    "Red ME Wire": "빨간색 ME 전선",
    "White ME Wire": "흰색 ME 전선",
    "Yellow ME Wire": "노란색 ME 전선",
    "Bricked Bronze": "벽돌식 청동",
    "Bricked Steel": "벽돌식 강철",
    "Steel Crate": "강철 상자",
    "Electric Furnace": "전기 화로",
    "Electric Macerator": "전기 분쇄기",
    "Electric Packer": "전기 포장기",
    "Electric Unpacker": "전기 포장 해제기",
    "Electric Wiremill": "전기 선재 압연기",
    "Steel Compressor": "강철 압축기",
    "Steel Cutting Machine": "강철 절단기",
    "Steel Furnace": "강철 화로",
    "Steel Macerator": "강철 분쇄기",
    "Unpacker": "포장 해제기",
    "AE2 integration": "AE2 연동",
    "Enable the Applied Energistics 2 integration, if present.": "Applied Energistics 2가 설치되어 있으면 연동을 활성화합니다.",
    "Almost Unified integration": "Almost Unified 연동",
    "Enable the Almost Unified integration, if present.": "Almost Unified가 설치되어 있으면 연동을 활성화합니다.",
    "Armor HUD vertical position": "방어구 HUD 세로 위치",
    "Space between the top of the screen and the jetpack/GraviChestPlate overlay text.": "화면 위쪽과 제트팩·중력 흉갑 오버레이 문구 사이의 간격입니다.",
    "Barrel content rendering": "배럴 내용물 렌더링",
    "Enable rendering of barrel content: item icon, item amount, and item name.": "배럴 내용물의 아이템 아이콘, 수량과 이름을 표시합니다.",
    "Base item pipe transfer": "아이템 파이프 기본 전송량",
    "Base amount of items transferred by item pipes every 3 seconds.": "아이템 파이프가 3초마다 전송하는 기본 아이템 수입니다.",
    "Bidirectional energy compatibility": "양방향 에너지 호환",
    "Enable bidirectional energy compatibility with NeoForge's energy system. We recommend leaving this to false unless the other mods have been balanced accordingly.": "NeoForge 에너지 시스템과 양방향 에너지 호환을 활성화합니다. 다른 모드가 이에 맞게 균형 조정되지 않았다면 끄는 것을 권장합니다.",
    "Mod Compatibility": "모드 호환",
    "Runtime Datagen": "런타임 데이터 생성",
    "Datagen on startup": "시작 시 데이터 생성",
    "Run MI runtime datagen on startup.": "시작할 때 MI 런타임 데이터를 생성합니다.",
    "Debug commands": "디버그 명령어",
    "Enable UNSUPPORTED and DANGEROUS debug commands.": "지원되지 않으며 위험한 디버그 명령어를 활성화합니다.",
    "Default Industrialist trades": "산업가 기본 거래",
    "Enable the default trades from the Industrialist villager provided by MI. Disable this to provide your own set of trades.": "MI 산업가 주민의 기본 거래를 활성화합니다. 자체 거래 목록을 사용하려면 끄세요.",
    "FE per EU": "EU당 FE",
    "How many Forge Energy units a single EU from MI is worth.": "MI의 1 EU를 몇 FE로 환산할지 정합니다.",
    "FTB Quests integration": "FTB Quests 연동",
    "Enable the FTB Quests integration, if present.": "FTB Quests가 설치되어 있으면 연동을 활성화합니다.",
    "Hatch placement overlay": "해치 배치 오버레이",
    "Show valid positions in multiblocks when holding a hatch.": "해치를 들고 있을 때 멀티블록에서 배치 가능한 위치를 표시합니다.",
    "Inter-machine connected textures": "기계 사이 연결 텍스처",
    "Enable connected textures between machines that have the same casing. (Requires a suitable resource pack)": "같은 케이싱을 사용하는 기계 사이에 연결 텍스처를 적용합니다. 적절한 리소스팩이 필요합니다.",
    "Load generated resources": "생성된 리소스 불러오기",
    "Additionally load resources in modern_industrialization/generated_resources.": "modern_industrialization/generated_resources 폴더의 리소스도 불러옵니다.",
    "Max distillation tower height": "증류탑 최대 높이",
    "Maximum height of the distillation tower multiblock.": "증류탑 멀티블록의 최대 높이입니다.",
    "Messages": "메시지",
    "New version message": "새 버전 메시지",
    "Display when a new version is available": "새 버전이 있을 때 메시지를 표시합니다.",
    "Rendering": "렌더링",
    "Respawn with guidebook": "부활 시 가이드북 지급",
    "Grant guidebook when a player respawns after death.": "플레이어가 사망 후 부활하면 가이드북을 지급합니다.",
    "Spawn with guidebook": "첫 접속 시 가이드북 지급",
    "Grant guidebook the first time a player joins the server.": "플레이어가 서버에 처음 접속할 때 가이드북을 지급합니다.",
    "Accepts %s, %s, %s and %s": "%s, %s, %s 및 %s 사용 가능",
    "Only accepts %s and %s": "%s 및 %s만 사용 가능",
    "Consumes %s and produces %s per mb": "mb당 %s를 소모하고 %s를 생산합니다",
    "Consumes %s and produces %s per item": "아이템 하나당 %s를 소모하고 %s를 생산합니다",
    "Accepts hatches:": "사용 가능한 해치:",
    "Change machine hull to connect higher tier cables.": "더 높은 등급의 케이블을 연결하려면 기계 외피를 바꾸세요.",
    "Accepts an overdrive module.": "오버드라이브 모듈을 장착할 수 있습니다.",
    "Accepts a redstone control module.": "레드스톤 제어 모듈을 장착할 수 있습니다.",
    "Activated": "활성화됨",
    "Infinite Damage": "무한 피해",
    "Quantum Armor": "양자 방어구",
    "Can store up to %d stacks": "최대 %d스택을 저장할 수 있습니다",
    "Blacklist mode enabled": "블랙리스트 모드 활성화됨",
    "Technology For Newbies": "초보자를 위한 기술",
    "Both": "둘 다",
    "Click to switch to %s": "클릭하여 %s로 전환",
    "Click to open link": "클릭하여 링크 열기",
    "Applied pipe settings from Config Card": "설정 카드의 파이프 설정을 적용했습니다",
    "Cleared Config Card": "설정 카드를 비웠습니다",
    "Configured (%d items)": "설정됨(아이템 %d개)",
    "Configured (no items)": "설정됨(아이템 없음)",
    "Camouflage application:": "위장 적용:",
    "Item pipe configuration:": "아이템 파이프 설정:",
    "Copied pipe settings to Config Card": "파이프 설정을 설정 카드에 복사했습니다",
    "Consumes the following for: ": "다음 작업에 소모: ",
    "Maximum efficiency reached only under continuous operation": "연속으로 작동해야 최대 효율에 도달합니다",
    "Customizable Ore Generation (Need Restart)": "광석 생성 사용자 설정(재시작 필요)",
    "Deactivated": "비활성화됨",
    "- Press %s + %s to swap between Fortune and Silk Touch.": "- %s + %s를 눌러 행운과 섬세한 손길을 전환하세요.",
    "Direct Energy for one capture": "포획 1회당 직접 에너지",
    "Direct Heat for one capture": "포획 1회당 직접 열",
    "Disabled": "비활성화됨",
    "Durability Cost: %d": "내구도 소모: %d",
    "Efficiency": "효율",
    "Empty": "비어 있음",
    "⚠ Empty Filter": "⚠ 빈 필터",
    "Enabled": "활성화됨",
    "Energy: %s %%": "에너지: %s %%",
    "Energy Input Hatch": "에너지 입력 해치",
    "Energy Output Hatch": "에너지 출력 해치",
    "Energy Stored: %s": "저장 에너지: %s",
    "%s - Max network transfer: %s": "%s - 네트워크 최대 전송량: %s",
    "Fluid auto-eject disabled": "유체 자동 배출 비활성화됨",
    "Fluid auto-eject enabled": "유체 자동 배출 활성화됨",
    "Fluid auto-pull disabled": "유체 자동 입력 비활성화됨",
    "Fluid auto-pull enabled": "유체 자동 입력 활성화됨",
    "Fluid Input Hatch": "유체 입력 해치",
    "Fluid Output Hatch": "유체 출력 해치",
    "Fluid IO, Left Click to Insert or Extract": "유체 입출력, 좌클릭하여 넣거나 빼기",
    "Fluid Input, Left Click to Insert or Extract": "유체 입력, 좌클릭하여 넣거나 빼기",
    "Fluid Output, Left Click to Extract": "유체 출력, 좌클릭하여 빼기",
    "MI Generated Resources": "MI 생성 리소스",
    "Resources from the modern_industrialization/generated_resources folder.": "modern_industrialization/generated_resources 폴더의 리소스입니다.",
    "Production: %s": "생산량: %s",
    "Max Production: %s": "최대 생산량: %s",
    "Gravichestplate disabled!": "중력 흉갑 비활성화됨!",
    "Gravichestplate enabled!": "중력 흉갑 활성화됨!",
    "Overclock: %s": "오버클럭: %s",
    "Double MI Steam Machines speed for 2 minutes": "MI 증기 기계의 속도를 2분 동안 두 배로 높입니다",
    "Use Gunpowder to double this machine speed for 2 minutes": "화약을 사용하면 이 기계의 속도가 2분 동안 두 배로 증가합니다",
    "Has a capacity of %s.": "용량: %s.",
    "Has a capacity of %s slots.": "슬롯 용량: %s칸.",
    "Heat Conduction %s/°kCt": "열전도율 %s/°kCt",
    "Item auto-eject disabled": "아이템 자동 배출 비활성화됨",
    "Item auto-eject enabled": "아이템 자동 배출 활성화됨",
    "Item auto-pull disabled": "아이템 자동 입력 비활성화됨",
    "Item auto-pull enabled": "아이템 자동 입력 활성화됨",
    "Item Input Hatch": "아이템 입력 해치",
    "Item Output Hatch": "아이템 출력 해치",
    "Jetpack disabled!": "제트팩 비활성화됨!",
    "Jetpack enabled!": "제트팩 활성화됨!",
    "Mouse Scroll": "마우스 휠",
    "Locked": "잠김",
    "Lock editing disabled": "잠금 편집 비활성화됨",
    "Lock editing enabled": "잠금 편집 활성화됨",
    "%s on Electric Machine: consume %s mb for 1 efficiency tick": "전기 기계에서 %s 사용 시 효율 틱 1회당 %smb를 소모합니다",
    "Allows machines to accept %s power": "기계가 %s 전력을 받을 수 있게 합니다",
    "Electric Machine Upgrade: Max Overclock +%s": "전기 기계 업그레이드: 최대 오버클럭 +%s",
    "Total Stack Upgrade +%s": "전체 중첩 업그레이드 +%s",
    "Can produce up to %s": "최대 %s까지 생산할 수 있습니다",
    "Can produce up to %s worth of %s": "%s 상당의 %s을(를) 생산할 수 있습니다",
    "Multiblock Materials": "멀티블록 재료",
    "Status: Active": "상태: 작동 중",
    "Network Amount": "네트워크 수량",
    "Network Delay": "네트워크 지연",
    "Network Energy": "네트워크 에너지",
    "Network Fluid": "네트워크 유체",
    "Shift-click to clear the network of its fluid.": "Shift-클릭하여 네트워크의 유체를 비웁니다.",
    "Click with a container to set the fluid for the network.": "용기를 들고 클릭하여 네트워크 유체를 설정합니다.",
    "Network Moved Items": "네트워크 이동 아이템 수",
    "Network Tier": "네트워크 등급",
    "Network Transfer": "네트워크 전송량",
    "Not linked to a Large Tank": "대형 탱크에 연결되지 않음",
    "No Tool Required": "도구 필요 없음",
    "Not consumed": "소모되지 않음",
    "%d veins per chunk": "청크당 광맥 %d개",
    "%d ores per vein": "광맥당 광석 %d개",
    "Y level %d to %d": "Y 레벨 %d~%d",
    "Click/Shift-Click to change": "클릭/Shift-클릭하여 변경",
    "Transfer priority: %d": "전송 우선순위: %d",
    "Pipes will interact with higher priorities first.": "파이프는 우선순위가 높은 대상부터 상호작용합니다.",
    "Progress: %s": "진행도: %s",
    "Put any Motor here to improve Item Pipe Speed": "모터를 넣어 아이템 파이프 속도를 높이세요",
    "Insert in a machine to enable redstone control.": "기계에 넣어 레드스톤 제어를 활성화합니다.",
    "Machine requires: %s": "기계 작동 조건: %s",
    "Requires biome: %s": "필요한 생물군계: %s",
    "Requires block behind machine: %s": "기계 뒤에 필요한 블록: %s",
    "Requires block below machine: %s": "기계 아래에 필요한 블록: %s",
    "Requires dimension: %s": "필요한 차원: %s",
    "Click to open shape selection panel.": "클릭하여 형태 선택 패널을 엽니다.",
    "High Signal": "강한 신호",
    "Low Signal": "약한 신호",
    "Tool configuration:": "도구 설정:",
    "Disabled transparent camouflage rendering": "투명 위장 렌더링 비활성화됨",
    "Enabled transparent camouflage rendering": "투명 위장 렌더링 활성화됨",
    "Whitelist mode enabled": "화이트리스트 모드 활성화됨",
}

VALUE_TRANSLATIONS.update(
    {
        # Extended Industrialization: 블록, 아이템, 분류와 조작키
        "Aluminum Tesla Winding": "알루미늄 테슬라 권선",
        "Annealed Copper Tesla Winding": "어닐링 구리 테슬라 권선",
        "Blazing Essence": "타오르는 정수",
        "Bronze Bending Machine": "청동 굽힘 기계",
        "Bronze Composter": "청동 퇴비화기",
        "Bronze Solar Boiler": "청동 태양열 보일러",
        "Bronze Waste Collector": "청동 배설물 수집기",
        "Composted Manure": "퇴비화된 거름",
        "Copper Tesla Winding": "구리 테슬라 권선",
        "Distilled Water": "증류수",
        "Electric Alloy Smelter": "전기 합금 제련기",
        "Electric Bending Machine": "전기 굽힘 기계",
        "Electric Brewery": "전기 양조기",
        "Electric Canning Machine": "전기 통조림 기계",
        "Electric Composter": "전기 퇴비화기",
        "Electric Farmer": "전기 농사 기계",
        "Electric Honey Extractor": "전기 꿀 추출기",
        "Electric Waste Collector": "전기 배설물 수집기",
        "Electrum Tesla Winding": "일렉트럼 테슬라 권선",
        "EV Tesla Receiver Hatch": "EV 테슬라 수신 해치",
        "Honey": "꿀",
        "HV Solar Panel": "HV 태양 전지판",
        "HV Tesla Receiver Hatch": "HV 테슬라 수신 해치",
        "Large Configurable Chest": "대형 설정 가능 상자",
        "Large Electric Furnace": "대형 전기 화로",
        "Large Electric Macerator": "대형 전기 분쇄기",
        "Large Steam Furnace": "대형 증기 화로",
        "Large Steam Macerator": "대형 증기 분쇄기",
        "Lethal Tesla Coil": "살상용 테슬라 코일",
        "LV Solar Panel": "LV 태양 전지판",
        "LV Tesla Receiver Hatch": "LV 테슬라 수신 해치",
        "Machine Chainer": "기계 연결기",
        "Machine Chainer Relay": "기계 연결 중계기",
        "Manure": "거름",
        "MV Solar Panel": "MV 태양 전지판",
        "MV Tesla Receiver Hatch": "MV 테슬라 수신 해치",
        "NPK Fertilizer": "NPK 비료",
        "Phosphoric Acid": "인산",
        "Polished Silver Machine Casing": "광택 은 기계 케이싱",
        "Potassium Chloride": "염화 칼륨",
        "Potassium Hydroxide": "수산화 칼륨",
        "Processing Array": "처리 배열",
        "Steam Farmer": "증기 농사 기계",
        "Steel Alloy Smelter": "강철 합금 제련기",
        "Steel Bending Machine": "강철 굽힘 기계",
        "Steel Brewery": "강철 양조기",
        "Steel Canning Machine": "강철 통조림 기계",
        "Steel Composter": "강철 퇴비화기",
        "Steel Honey Extractor": "강철 꿀 추출기",
        "Steel Plated Bricks": "강철 도금 벽돌",
        "Steel Solar Boiler": "강철 태양열 보일러",
        "Steel Waste Collector": "강철 배설물 수집기",
        "SV Tesla Receiver Hatch": "SV 테슬라 수신 해치",
        "Superconductor Tesla Winding": "초전도체 테슬라 권선",
        "Tesla Coil": "테슬라 코일",
        "Tesla Particle Generator": "테슬라 입자 생성기",
        "Tesla Receiver": "테슬라 수신기",
        "Tesla Tower": "테슬라 타워",
        "Universal Transformer": "범용 변압기",
        "Shoulders": "어깨",
        "%1$s was vaporized": "%1$s이(가) 증발했습니다",
        "%1$s was vaporized by %2$s using %3$s": "%1$s이(가) %3$s을(를) 사용한 %2$s에게 증발했습니다",
        "%1$s was vaporized by %2$s": "%1$s이(가) %2$s에게 증발했습니다",
        "%1$s was electrocuted to death": "%1$s이(가) 감전사했습니다",
        "Nano Saber Sweep": "나노 세이버 휩쓸기",
        "Blazing Essence Bucket": "타오르는 정수 양동이",
        "Canned Food": "통조림 식품",
        "Composted Manure Bucket": "퇴비화된 거름 양동이",
        "Crystallized Honey": "결정화된 꿀",
        "Distilled Water Bucket": "증류수 양동이",
        "Electric Chainsaw": "전기 전기톱",
        "Electric Mining Drill": "전기 채굴 드릴",
        "Granite Dust": "화강암 가루",
        "Honey Bucket": "꿀 양동이",
        "HV Photovoltaic Cell": "HV 광전지",
        "Looting Module": "약탈 모듈",
        "LV Photovoltaic Cell": "LV 광전지",
        "Machine Config Card": "기계 설정 카드",
        "Manure Bucket": "거름 양동이",
        "Mulch": "멀치",
        "MV Photovoltaic Cell": "MV 광전지",
        "Nano Boots": "나노 부츠",
        "Nano Chestplate": "나노 흉갑",
        "Nano Gravichestplate": "나노 중력 흉갑",
        "Nano Helmet": "나노 헬멧",
        "Nano Leggings": "나노 레깅스",
        "Quantum Nano Boots": "양자 나노 부츠",
        "Quantum Nano Chestplate": "양자 나노 흉갑",
        "Quantum Nano Helmet": "양자 나노 헬멧",
        "Quantum Nano Leggings": "양자 나노 레깅스",
        "Quantum Nano Saber": "양자 나노 세이버",
        "Nano Saber": "나노 세이버",
        "Netherite Dust": "네더라이트 가루",
        "Netherite Rotary Blade": "네더라이트 회전날",
        "NPK Fertilizer Bucket": "NPK 비료 양동이",
        "Nyano Helmet": "냐노 헬멧",
        "Quantum Nyano Helmet": "양자 냐노 헬멧",
        "Phosphoric Acid Bucket": "인산 양동이",
        "Potassium Chloride Bucket": "염화 칼륨 양동이",
        "Potassium Hydroxide Bucket": "수산화 칼륨 양동이",
        "Robot Auto Feeder": "로봇 자동 급식기",
        "Silk Touch Module": "섬세한 손길 모듈",
        "Silver Curved Plate": "은 곡면 판",
        "Silver Tesla Top Load": "은 테슬라 상단 부하",
        "Steam Chainsaw": "증기 전기톱",
        "Steel Combine": "강철 콤바인",
        "Tesla Calibrator": "테슬라 교정기",
        "Tesla Handheld Receiver": "휴대용 테슬라 수신기",
        "Tesla Interdimensional Upgrade": "테슬라 차원 간 업그레이드",
        "Tin Can": "주석 캔",
        "Ultimate Laser Drill": "궁극의 레이저 드릴",
        "Toggle Boots Ability": "부츠 능력 전환",
        "Toggle Chestplate Ability": "흉갑 능력 전환",
        "Toggle Helmet Ability": "헬멧 능력 전환",
        "Toggle Leggings Ability": "레깅스 능력 전환",
        "Toggle Main Hand Ability": "주 손 능력 전환",
        "Cupronickel": "백동",
        "Kanthal": "칸탈",
        "Bending Machine": "굽힘 기계",
        "Composter": "퇴비화기",
        "Alloy Smelter": "합금 제련기",
        "Brewery": "양조기",
        "Canning Machine": "통조림 기계",
        "Farmer Enchantment Modules": "농사 기계 마법 부여 모듈",
        "Lethal Tesla Coil Enchantment Modules": "살상용 테슬라 코일 마법 부여 모듈",
        "Farmer Plantable": "농사 기계 재배 가능 항목",
        "Farmer Voidable": "농사 기계 폐기 가능 항목",
        "Photovoltaic Cells": "광전지",
        "Processing Array Blacklist": "처리 배열 블랙리스트",
        "Rainbow Dyeable": "무지개색 염색 가능 항목",
        "Aluminum": "알루미늄",
        "Annealed Copper": "어닐링 구리",
        "Copper": "구리",
        "Electrum": "일렉트럼",
        # Extended Industrialization: 사용자 표시 문구
        "Blazing Essence is used in the brewery to brew potions.": "타오르는 정수는 양조기에서 물약을 양조할 때 사용합니다.",
        "1mb of Blazing Essence is used every time the brewery brews a set of potions.": "양조기가 물약 한 묶음을 양조할 때마다 타오르는 정수 1mb를 사용합니다.",
        "Brews %s potions at a time.": "한 번에 물약 %s개를 양조합니다.",
        "Requires %s to brew potions.": "물약을 양조하려면 %s이(가) 필요합니다.",
        "Calcification: %s %%": "석회화: %s %%",
        "Runs LEF in batches of up to %s at %s the EU cost.": "대형 전기 화로에서 최대 %s개씩 일괄 처리하며 EU 비용은 %s배입니다.",
        "Blue: ": "파란색: ",
        "Green: ": "초록색: ",
        "Red: ": "빨간색: ",
        "The block at %s is not a network part.": "%s의 블록은 네트워크 구성 요소가 아닙니다.",
        "Chunk at %s is not loaded.": "%s의 청크가 불러와지지 않았습니다.",
        "No existing network could be found for %s.": "%s에 연결된 네트워크를 찾을 수 없습니다.",
        "Dumping data on network of %s:": "%s의 네트워크 데이터를 출력합니다:",
        "* Key: %s": "* 키: %s",
        "* Transmitter: %s": "* 송신기: %s",
        "* Receiver Count: %s / %s (linked / loaded)": "* 수신기 수: %s / %s (연결됨 / 불러옴)",
        "Not loaded": "불러오지 않음",
        "%s\n  * Ticking: %s\n  * Voltage: %s": "%s\n  * 틱 처리 중: %s\n  * 전압: %s",
        "Configure": "설정",
        "Click to open machine configuration panel.": "클릭하여 기계 설정 패널을 엽니다.",
        "Deactivated": "비활성화됨",
        "- Can be dyed and trimmed!": "- 염색과 장식이 가능합니다!",
        "- Can be dyed!": "- 염색할 수 있습니다!",
        "Disabled 3x3 Mining": "3x3 채굴 비활성화됨",
        "Enabled 3x3 Mining": "3x3 채굴 활성화됨",
        "- Press %s + %s to swap between Fortune/Looting and Silk Touch.": "- %s + %s를 눌러 행운/약탈과 섬세한 손길을 전환하세요.",
        "- Press %s + %s to swap between Looting and Beheading.": "- %s + %s를 눌러 약탈과 참수를 전환하세요.",
        "- Use %s + %s to change mining speed.": "- %s + %s를 사용하여 채굴 속도를 바꾸세요.",
        "- Press %s while held or %s while hovered to toggle 3x3 mining.": "- 들고 있을 때 %s, 마우스를 올렸을 때 %s를 눌러 3x3 채굴을 전환하세요.",
        "Insert an enchantment module to make the machine use the enchantment.": "마법 부여 모듈을 넣으면 기계가 해당 마법을 사용합니다.",
        "Can be used in the %s.": "%s에서 사용할 수 있습니다.",
        "Applies %s in the machine for %s.": "기계에 %s을(를) %s 수준으로 적용합니다.",
        "Voltage determines the level of %s applied in the machine.": "전압에 따라 기계에 적용되는 %s의 레벨이 정해집니다.",
        "Not Tilling": "경작 안 함",
        "Alternating Lines": "교차 줄",
        "As Needed": "필요한 만큼",
        "Quadrants": "사분면",
        "  - %s: %s": "  - %s: %s",
        "Fertilizing": "비료 주기",
        "When supplied with a valid fluid fertilizer, it will randomly bonemeal crops and saplings.": "유효한 액체 비료를 공급하면 작물과 묘목에 무작위로 뼛가루 효과를 적용합니다.",
        "Harvesting": "수확",
        "When there is enough output space provided, it will harvest fully grown crops and trees.": "출력 공간이 충분하면 다 자란 작물과 나무를 수확합니다.",
        "Hydrating": "수분 공급",
        "When supplied with water, tilled soil will be hydrated.": "물을 공급하면 경작지를 촉촉하게 유지합니다.",
        "Planting": "심기",
        "When supplied with crops or saplings, it will plant them on valid soil. Using different planting modes will plant them in different arrangements.": "작물이나 묘목을 공급하면 알맞은 땅에 심습니다. 심기 모드에 따라 서로 다른 배치로 심습니다.",
        "Tilling": "경작",
        "When enabled, dirt blocks will be turned into farmland. This will not work unless water is supplied.": "활성화하면 흙 블록을 경작지로 바꿉니다. 물을 공급하지 않으면 작동하지 않습니다.",
        "Can perform the following tasks using %s:": "%s을(를) 사용하여 다음 작업을 수행할 수 있습니다:",
        "Fluid Fertilizers": "액체 비료",
        "Consumes: %smb": "소모량: %smb",
        "Cycle Time: %ss": "주기: %s초",
        "Generating: %s EU/t": "발전량: %s EU/t",
        "When placed facing into a beehive, honey will be extracted in fluid form.": "벌통을 향하도록 배치하면 꿀을 유체 형태로 추출합니다.",
        "Batch size and cost is determined by coil used.": "사용한 코일에 따라 일괄 처리량과 비용이 정해집니다.",
        "Connected Machines: %s / %s": "연결된 기계: %s / %s",
        "Connects up to %s consecutive machines in a straight line in the direction it is facing.": "바라보는 방향의 직선상에 연속된 기계를 최대 %s대까지 연결합니다.",
        "Accepts items, fluids, and energy and distributes them to connected machines.": "아이템, 유체와 에너지를 받아 연결된 기계에 분배합니다.",
        "Can connect to other machine chainers, but it must not link back to itself.": "다른 기계 연결기에 연결할 수 있지만, 연결이 자기 자신에게 되돌아오면 안 됩니다.",
        "Problem at: %s": "문제 위치: %s",
        "Failed to apply machine configuration to machine.": "기계에 설정을 적용하지 못했습니다.",
        "Applied machine configuration to machine from card.": "카드의 설정을 기계에 적용했습니다.",
        "Cleared machine configuration from card.": "카드의 기계 설정을 비웠습니다.",
        "Configured (%s)": "설정됨(%s)",
        "- Press %s + %s on a machine to save its settings in the card.": "- 기계에서 %s + %s를 눌러 설정을 카드에 저장하세요.",
        "- Use %s on a machine to apply the settings from the card.": "- 기계에서 %s을(를) 사용하여 카드의 설정을 적용하세요.",
        "- (Optional) Hold in off-hand when placing machines to automatically apply settings.": "- (선택) 보조 손에 든 채 기계를 배치하면 설정을 자동으로 적용합니다.",
        "- Clear using %s + %s on air.": "- 허공에서 %s + %s를 사용하여 비우세요.",
        "Saved machine configuration to card.": "기계 설정을 카드에 저장했습니다.",
        "Manure can be collected by placing a Waste Collector underneath an animal.": "동물 아래에 배설물 수집기를 놓으면 거름을 모을 수 있습니다.",
        "Meow :3": "야옹 :3",
        "I love mulch!": "멀치가 정말 좋아!",
        "Mulch is my favorite food!": "내가 가장 좋아하는 음식은 멀치야!",
        "- Press %s to make a long ranged sweep attack.": "- %s를 눌러 긴 사거리의 휩쓸기 공격을 하세요.",
        "Creative Flight: %s": "자유 비행: %s",
        "Armor information:": "방어구 정보:",
        "- Press %s while equipped or %s while hovered to toggle Creative Flight.": "- 착용 중에는 %s, 마우스를 올렸을 때는 %s를 눌러 자유 비행을 전환하세요.",
        "- Press %s while equipped or %s while hovered to toggle Night Vision.": "- 착용 중에는 %s, 마우스를 올렸을 때는 %s를 눌러 야간 투시를 전환하세요.",
        "- Press %s while equipped or %s while hovered to toggle the Speed Boost.": "- 착용 중에는 %s, 마우스를 올렸을 때는 %s를 눌러 속도 증가를 전환하세요.",
        "- Press %s while equipped or %s while hovered to toggle the Step Boost.": "- 착용 중에는 %s, 마우스를 올렸을 때는 %s를 눌러 단차 보조를 전환하세요.",
        "Night Vision: %s": "야간 투시: %s",
        "Disabled Night Vision": "야간 투시 비활성화됨",
        "Enabled Night Vision": "야간 투시 활성화됨",
        "Speed: %s": "속도: %s",
        "Disabled Speed Boost": "속도 증가 비활성화됨",
        "Enabled Speed Boost": "속도 증가 활성화됨",
        "Step: %s": "단차 보조: %s",
        "Disabled Step Boost": "단차 보조 비활성화됨",
        "Enabled Step Boost": "단차 보조 활성화됨",
        "Will produce up to %s when placed in a Solar Panel.": "태양 전지판에 넣으면 최대 %s을(를) 생산합니다.",
        "Remaining Operation Time: %s": "남은 작동 시간: %s",
        "Remaining Operation Time: %s minute(s)": "남은 작동 시간: %s분",
        "Priority: %s": "우선순위: %s",
        "Batch size is determined by the amount of machines provided to it.": "넣은 기계 수에 따라 일괄 처리량이 정해집니다.",
        "Runs at %s the EU cost.": "EU 비용 %s배로 작동합니다.",
        "Insert electric crafting machines to run in parallel.": "전기 제작 기계를 넣으면 병렬로 작동합니다.",
        "Can run recipes of any single block electric crafting machine provided to it in batches.": "넣은 단일 블록 전기 제작 기계의 제작법을 일괄 처리할 수 있습니다.",
        "Machines: %s": "기계: %s",
        "Rainbow": "무지개",
        "Automatically grabs Canned Food from your inventory and feeds it to you.": "인벤토리에서 통조림 식품을 자동으로 꺼내 먹여 줍니다.",
        "Works with item containing items such as backpacks.": "배낭처럼 아이템을 담는 아이템 안에서도 작동합니다.",
        "Will calcify and lose efficiency over time to a minimum of %s efficiency when not using %s. Using an axe on the boiler will reset its calcification.": "%s을(를) 사용하지 않으면 시간이 지날수록 석회화되어 효율이 최소 %s까지 떨어집니다. 보일러에 도끼를 사용하면 석회화가 초기화됩니다.",
        "Solar Efficiency: %s %%": "태양열 효율: %s %%",
        "By supplying %s to the Solar Panel, the Photovoltaic Cell in its slot will last 2x as long and produce 1.5x as much energy!": "태양 전지판에 %s을(를) 공급하면 슬롯의 광전지가 두 배 오래가고 에너지를 1.5배 생산합니다!",
        "To produce energy, the Solar Panel needs a matching tier Photovoltaic Cell in its inventory.": "에너지를 생산하려면 태양 전지판에 같은 등급의 광전지가 들어 있어야 합니다.",
        "Energy generation rates are determined by how high the sun is in the sky and if the sky is visible.": "발전량은 태양의 고도와 하늘이 보이는지에 따라 정해집니다.",
        "- Press %s on still or flowing water to fill.": "- 고인 물이나 흐르는 물에서 %s을(를) 눌러 채우세요.",
        "- Place fuel inside the chainsaw using %s.": "- %s을(를) 사용하여 전기톱 안에 연료를 넣으세요.",
        "- Toggle Silk Touch with %s + %s.": "- %s + %s로 섬세한 손길을 전환하세요.",
        "Cleared selection from tesla calibrator.": "테슬라 교정기의 선택을 지웠습니다.",
        "- Press %s + %s on a transmitter to save its position in the calibrator.": "- 송신기에서 %s + %s를 눌러 위치를 교정기에 저장하세요.",
        "- Use %s on a Tesla Receiver to link it to the selected transmitter.": "- 테슬라 수신기에서 %s을(를) 사용하여 선택한 송신기에 연결하세요.",
        "- (Optional) Hold in off-hand when placing receivers to automatically link.": "- (선택) 보조 손에 든 채 수신기를 배치하면 자동으로 연결합니다.",
        "Failed to link receiver because no transmitter is selected.": "선택한 송신기가 없어 수신기를 연결하지 못했습니다.",
        "Linked receiver to selected transmitter.": "수신기를 선택한 송신기에 연결했습니다.",
        "Linked to %s": "%s에 연결됨",
        "Selected transmitter for calibration.": "교정할 송신기를 선택했습니다.",
        "Wirelessly transmits energy to linked receivers within %s blocks.": "%s블록 안의 연결된 수신기에 에너지를 무선으로 전송합니다.",
        "Voltage of energy transmitted is set by the hull provided. Higher voltages have an increased passive drain.": "전송 전압은 장착한 외피로 정합니다. 전압이 높을수록 대기 소모량이 늘어납니다.",
        "Cleared selected transmitter.": "선택한 송신기를 지웠습니다.",
        "Receives energy from a linked transmitter within range and charges items while in your inventory.": "범위 안의 연결된 송신기에서 에너지를 받아 인벤토리의 아이템을 충전합니다.",
        "Tesla Calibration:": "테슬라 교정:",
        "- Press %s on a transmitter to link the receiver to it.": "- 송신기에서 %s을(를) 눌러 수신기를 연결하세요.",
        "Selected transmitter for receiving.": "에너지를 받을 송신기를 선택했습니다.",
        "Removes the range limitation on a Tesla Tower and allows it to transmit energy across dimensions.": "테슬라 타워의 거리 제한을 없애고 차원을 넘어 에너지를 전송할 수 있게 합니다.",
        "Damages Players: No": "플레이어 피해: 아니요",
        "Damages Players: Yes": "플레이어 피해: 예",
        "Deals damage to entities within %s blocks while powered.": "전력이 공급되는 동안 %s블록 안의 개체에 피해를 줍니다.",
        "Voltage determines the amount of damage dealt and energy required:": "전압에 따라 피해량과 필요한 에너지가 정해집니다:",
        "Cannot receive %s power": "%s 전력을 받을 수 없음",
        "Not linked to any transmitter": "송신기에 연결되지 않음",
        "Transmitter is too far": "송신기가 너무 멂",
        "Transmitter is not loaded": "송신기가 불러와지지 않음",
        "Note: %s": "음표: %s",
        "Consuming: %s": "소모량: %s",
        "Drain: %s": "대기 소모량: %s",
        "Receivers: %s": "수신기: %s",
        "Transmitting: %s (%s)": "전송량: %s (%s)",
        "Generates arcs for aesthetic purposes only.": "장식용 전기 아크만 생성합니다.",
        "Extreme": "극대",
        "Immense": "거대",
        "Large": "대형",
        "Medium": "중형",
        "Small": "소형",
        "Can receive energy from a linked transmitter.": "연결된 송신기에서 에너지를 받을 수 있습니다.",
        "Must accept energy of the same voltage as the linked transmitter.": "연결된 송신기와 같은 전압의 에너지를 받을 수 있어야 합니다.",
        "Wirelessly transmits energy to linked receivers within range.": "범위 안의 연결된 수신기에 에너지를 무선으로 전송합니다.",
        "Energy transfer rate, range, and passive drain is determined by the windings used.": "사용한 권선에 따라 에너지 전송량, 범위와 대기 소모량이 정해집니다.",
        "Voltage of energy transmitted is set by the energy hatches. All hatches must be the same tier.": "전송 전압은 에너지 해치로 정합니다. 모든 해치는 같은 등급이어야 합니다.",
        "All energy hatches must be of the same voltage.": "모든 에너지 해치의 전압이 같아야 합니다.",
        "No energy hatches provided": "에너지 해치가 없음",
        "Add tesla upgrades to increase maximum range.": "테슬라 업그레이드를 추가하여 최대 범위를 늘리세요.",
        "Area: %s": "범위: %s",
        "Mode: %s": "모드: %s",
        "Beheading": "참수",
        "Fortune": "행운",
        "Fortune & Looting": "행운 및 약탈",
        "Looting": "약탈",
        "Silk Touch": "섬세한 손길",
        "Beheading mode enabled!": "참수 모드 활성화됨!",
        "Fortune mode enabled!": "행운 모드 활성화됨!",
        "Looting mode enabled!": "약탈 모드 활성화됨!",
        "Silk Touch mode enabled!": "섬세한 손길 모드 활성화됨!",
        "Hull for cable tier to convert from (LV by default).": "변환 전 케이블 등급의 외피입니다(기본값 LV).",
        "Hull for cable tier to convert to (LV by default).": "변환 후 케이블 등급의 외피입니다(기본값 LV).",
        "  - %s: %s for %s": "  - %s: %s, %s 기준",
        "When placed underneath animals, manure will be collected.": "동물 아래에 배치하면 거름을 수집합니다.",
        "Allows the Tesla Tower to transmit up to %s within %s blocks with a passive drain of %s.": "테슬라 타워가 %s까지의 에너지를 %s블록 안에 전송할 수 있게 하며 대기 소모량은 %s입니다.",
        # Industrialization Overdrive
        "Multi Processing Array": "다중 처리 배열",
        "Pyrolyse Oven": "열분해 오븐",
        "Multiblock Builder": "멀티블록 건축기",
        "Runs Pyrolyse Oven in batches of up to %d at %s the EU cost.": "열분해 오븐에서 최대 %d개씩 일괄 처리하며 EU 비용은 %s배입니다.",
        "Energy: %s / %s": "에너지: %s / %s",
        "Insert electric crafting multiblocks to run in parallel.": "전기 제작 멀티블록을 넣으면 병렬로 작동합니다.",
        "Can run recipes of any electric crafting multiblock provided to it in batches.": "넣은 전기 제작 멀티블록의 제작법을 일괄 처리할 수 있습니다.",
        "Machines: %d": "기계: %d",
        "- Press %s + %s on a MI multiblock to automatically build it.": "- MI 멀티블록에서 %s + %s를 눌러 자동으로 건설하세요.",
        "- Requires parts to be in your inventory.": "- 필요한 부품이 인벤토리에 있어야 합니다.",
        "- Requires parts to be in your inventory or a linked ME system.": "- 필요한 부품이 인벤토리나 연결된 ME 시스템에 있어야 합니다.",
        "Linked to an ME system at %s.": "%s의 ME 시스템에 연결됨.",
        "Not linked to an ME system.": "ME 시스템에 연결되지 않음.",
        "Silk Touch: %s": "섬세한 손길: %s",
        "Speed changed to %d.": "속도를 %d(으)로 변경했습니다.",
        "Fast": "빠름",
        "Speed: %d": "속도: %d",
        "Instant": "즉시",
        "Normal": "보통",
        "Slow": "느림",
    }
)

BASE_KEY_OVERRIDES = {
    "block.modern_industrialization.fire_clay_bricks": "내화 점토 벽돌 블록",
    # 발전 과제 141개를 영어 원문과 대조한 뒤 의미·수치·확정 아이템명을 교정한다.
    "advancements.modern_industrialization.advanced_upgrade": "기계 가속의 가속",
    "advancements.modern_industrialization.analog_circuit.description": "아날로그 회로를 제작하여 전기 시대에 진입하세요",
    "advancements.modern_industrialization.assembler.description": "조립기를 제작하세요",
    "advancements.modern_industrialization.basic_upgrade": "기계 가속",
    "advancements.modern_industrialization.basic_upgrade.description": "기본 업그레이드를 제작하여 전기 제작법의 최대 속도를 높이세요",
    "advancements.modern_industrialization.blastproof_alloy_plate.description": "압축기에서 방폭 합금판을 제작하세요",
    "advancements.modern_industrialization.bronze_furnace": "연료 효율 10배",
    "advancements.modern_industrialization.bronze_macerator": "광석 2배화",
    "advancements.modern_industrialization.bronze_mixer": "Mixin 없는 혼합",
    "advancements.modern_industrialization.diesel_jetpack": "겉날개... 아니, 제트팩!",
    "advancements.modern_industrialization.diesel_mining_drill.description": "디젤 채굴 드릴을 제작하세요",
    "advancements.modern_industrialization.distillation_tower.description": "증류탑을 제작하여 석유 처리의 잠재력을 모두 끌어내세요",
    "advancements.modern_industrialization.electric_blast_furnace.description": "알루미늄 생산을 시작하려면 전기 용광로를 제작하세요",
    "advancements.modern_industrialization.electric_quarry": "자원이 콸콸콸!!!",
    "advancements.modern_industrialization.electrolyzer": "식물이 갈망하는 바로 그것",
    "advancements.modern_industrialization.forge_hammer.description": "단조 망치를 제작하여 모드 탐험을 시작하세요",
    "advancements.modern_industrialization.fusion_reactor.description": "막대한 에너지를 생산하려면 핵융합로를 제작하세요",
    "advancements.modern_industrialization.gravichestplate.description": "중력 흉갑을 제작하여 자유 비행을 활성화하세요",
    "advancements.modern_industrialization.heat_exchanger.description": "고압 증기 손실을 막고 용암으로 손쉽게 발전하려면 열교환기를 제작하세요",
    "advancements.modern_industrialization.inductor.description": "인덕터를 제작하세요",
    "advancements.modern_industrialization.kanthal_coil": "더 나은 전기 용광로",
    "advancements.modern_industrialization.kanthal_coil.description": "칸탈 코일을 제작하여 새로운 전기 용광로 제작법을 해금하세요",
    "advancements.modern_industrialization.lv_steam_turbine": "태양 전지판보다 낫다",
    "advancements.modern_industrialization.mixed_ingot_iridium.description": "이리듐 판을 만들기 위한 혼합 이리듐 주괴를 제작하세요",
    "advancements.modern_industrialization.mv_lv_transformer.description": "MV-LV 변압기를 제작하세요",
    "advancements.modern_industrialization.nuclear_reactor.description": "원자로를 제작하여 정교하게 설계된 작동 원리를 알아보세요",
    "advancements.modern_industrialization.nuke": "나는 이제 죽음이요, 세상의 파괴자가 되었도다",
    "advancements.modern_industrialization.nuke.description": "핵폭탄을 제작하세요",
    "advancements.modern_industrialization.oil_drilling_rig": "당신의 나라에 자유를",
    "advancements.modern_industrialization.plasma_turbine.description": "플라즈마 터빈을 제작하여 헬륨 플라즈마를 에너지로 변환하세요",
    "advancements.modern_industrialization.polarizer": "모두를 지배할 하나(+2)의 제작법",
    "advancements.modern_industrialization.pressurizer.description": "효율적인 증기 처리를 해금하려면 가압기를 제작하세요",
    "advancements.modern_industrialization.quantum_chestplate.description": "양자 흉갑을 제작하세요. 양자 방어구 한 부위마다 피해를 받을 확률이 25%씩 줄어듭니다",
    "advancements.modern_industrialization.quantum_sword.description": "양자 검을 제작하여 적을 분해하세요(떠돌이 상인의 라마도 가능합니다)",
    "advancements.modern_industrialization.quantum_upgrade.description": "양자 업그레이드를 제작하여 제작법 속도 제한을 없애세요",
    "advancements.modern_industrialization.raw_iridium": "다이아몬드 2.0: 다시 돌아온 전기 춤",
    "advancements.modern_industrialization.replicator.description": "복제기를 제작하고 UU 물질로 원하는 아이템을 복제하세요",
    "advancements.modern_industrialization.steam_quarry.description": "증기 채석기를 제작하여 직접 채광과 작별하세요",
    "advancements.modern_industrialization.steel_machine_casing": "구운 생강철!",
    "advancements.modern_industrialization.steel_machine_casing.description": "증기 용광로로 강철을 생산하고 강철 기계 케이싱을 제작하세요",
    "advancements.modern_industrialization.steel_wiremill.description": "강철 선재 압연기를 제작하세요",
    "advancements.modern_industrialization.used_steel_upgrade.description": "청동 기계에 강철 업그레이드를 우클릭하세요",
    # 블록·아이템·설정·툴팁의 검색명과 사용자 표시 문구를 현재 원문에 맞춘다.
    "block.modern_industrialization.acrylic_acid": "아크릴산",
    "block.modern_industrialization.annealed_copper_block": "어닐링 구리 블록",
    "block.modern_industrialization.assembler": "조립기",
    "block.modern_industrialization.cryofluid": "극저온 유체",
    "block.modern_industrialization.electric_unpacker": "전기 포장 해제기",
    "block.modern_industrialization.forge_hammer": "단조 망치",
    "block.modern_industrialization.fusion_chamber": "핵융합 챔버",
    "block.modern_industrialization.fusion_reactor": "핵융합로",
    "block.modern_industrialization.heat_exchanger": "열교환기",
    "block.modern_industrialization.liquid_air": "액화 공기",
    "block.modern_industrialization.nuclear_alloy_machine_casing_pipe": "핵 합금 파이프 기계 케이싱",
    "block.modern_industrialization.nuclear_casing": "핵 합금 케이싱",
    "block.modern_industrialization.nuclear_fluid_hatch": "원자로 유체 해치",
    "block.modern_industrialization.nuclear_item_hatch": "원자로 아이템 해치",
    "block.modern_industrialization.nuclear_reactor": "원자로",
    "block.modern_industrialization.nuke": "핵폭탄",
    "block.modern_industrialization.pipe": "파이프",
    "block.modern_industrialization.steel_unpacker": "강철 포장 해제기",
    "item.modern_industrialization.cryofluid_bucket": "극저온 유체 양동이",
    "item.modern_industrialization.diesel_mining_drill": "디젤 채굴 드릴",
    "item.modern_industrialization.steam_mining_drill": "증기 채굴 드릴",
    "item.modern_industrialization.liquid_air_bucket": "액화 공기 양동이",
    "item.modern_industrialization.mixed_plate_nuclear": "핵 혼합 판",
    "item.modern_industrialization.nuclear_alloy_large_plate": "핵 합금 대형 판",
    "item.modern_industrialization.nuclear_alloy_plate": "핵 합금 판",
    "item_tooltip.modern_industrialization.forge_hammer.line_0": "게임 초반에 광석 블록의 생산량을 늘릴 때 사용하세요!",
    "item_tooltip.modern_industrialization.forge_hammer.line_1": "(증기 채굴 드릴을 사용하면 섬세한 손길을 쉽게 얻을 수 있습니다.)",
    "item_tooltip.modern_industrialization.stainless_steel_dust.line_0": "인바 가루 제작법과 구분하려면 REI의 슬롯 고정을 사용하세요",
    "item_tooltip.modern_industrialization.trash_can.line_0": "보낸 모든 아이템과 유체를 삭제합니다.",
    "modern_industrialization.configuration.compostableToPlantOil.tooltip": "퇴비화 가능한 모든 아이템의 식물성 오일 제작법을 원심분리기에 생성합니다.",
    "modern_industrialization.configuration.missingRecipeViewerMessage": "제작법 뷰어 누락 메시지",
    "modern_industrialization.configuration.stonecutterToCuttingMachine": "석재 절단기-절단기 제작법",
    "modern_industrialization.configuration.stonecutterToCuttingMachine.tooltip": "모든 석재 절단기 제작법에 대응하는 절단기 제작법을 생성합니다.",
    "rei_categories.modern_industrialization.assembler": "조립기",
    "rei_categories.modern_industrialization.fusion_reactor": "핵융합로",
    "rei_categories.modern_industrialization.steel_wiremill": "선재 압연기",
    "text.modern_industrialization.BatteryInStorageUnit": "휴대용 저장 유닛에 넣으면 용량이 %s만큼 늘어납니다",
    "text.modern_industrialization.ClickToDisable": "클릭하여 비활성화",
    "text.modern_industrialization.ClickToEnable": "클릭하여 활성화",
    "text.modern_industrialization.ClickToToggleBlacklist": "클릭하여 블랙리스트 모드 활성화",
    "text.modern_industrialization.ClickToToggleWhitelist": "클릭하여 화이트리스트 모드 활성화",
    "text.modern_industrialization.ConfigCardConfiguredCamouflage": "설정됨(%s 위장)",
    "text.modern_industrialization.ConfigCardHelpCamouflage2": "- 월드의 블록에서 %s + %s를 눌러 위장으로 선택하세요.",
    "text.modern_industrialization.ConfigCardHelpCamouflage3": "- 파이프에서 %s을(를) 사용하여 위장을 갱신하세요.",
    "text.modern_industrialization.ConfigCardHelpCamouflage4": "- 렌치를 들고 %s + %s를 눌러 위장을 제거하세요.",
    "text.modern_industrialization.ConfigCardHelpCamouflage5": "- %s + %s를 사용하여 위장의 투명 렌더링을 전환하세요.",
    "text.modern_industrialization.ConfigCardHelpClear": "허공에서 %s + %s를 사용하여 저장된 내용을 지우세요.",
    "text.modern_industrialization.ConfigCardSetCamouflage": "%s 위장을 설정 카드에 복사했습니다",
    "text.modern_industrialization.EbfMaxEu": "최대 %d EU/t의 전기 용광로 제작법을 사용할 수 있습니다",
    "text.modern_industrialization.EfficiencyDefaultMessage": "오버클럭할 활성 제작법이 없습니다",
    "text.modern_industrialization.EfficiencyMaxOverclock": "최대 오버클럭: %d EU/t",
    "text.modern_industrialization.HasBetterYieldAssemblerRecipe": "수율이 더 높은 조립기 제작법이 있습니다.",
    "text.modern_industrialization.NeutronProductionTemperatureEffect": "온도에 따라 방출되는 중성자",
    "text.modern_industrialization.NeutronTemperatureVariation": "온도가 올라가면 감소",
    "text.modern_industrialization.NeutronsMultiplication": "방출 중성자 최대 %s개",
    "text.modern_industrialization.NewVersion": "Modern Industrialization 새 버전(%s)을 %s에서 이용할 수 있습니다!",
    "text.modern_industrialization.NoEmi": "경고: Modern Industrialization을 플레이할 때 EMI(아이템 및 제작법 뷰어) 사용을 강력히 권장합니다. EMI가 없으면 게임에서 제작법을 확인하거나 충돌하는 기계 제작법을 처리할 수 없습니다. Just Enough Items와 Roughly Enough Items도 지원합니다. 이 메시지는 설정에서 끌 수 있습니다.",
    "text.modern_industrialization.OverclockMachine": "%s을(를) 사용하여 이 기계의 속도를 %f배로 높입니다(%d틱 지속)",
    "text.modern_industrialization.PipeConnectionTooltipExtractOnly": "출력만",
    "text.modern_industrialization.PipeConnectionTooltipInsertOnly": "입력만",
    "text.modern_industrialization.PipeConnectionTooltipInsertOrExtract": "입력 또는 출력",
    "text.modern_industrialization.PriorityExtract": "출력 우선순위: %d",
    "text.modern_industrialization.PriorityInsert": "입력 우선순위: %d",
    "text.modern_industrialization.PriorityItemHelp": "아이템은 낮은 출력 우선순위(%s)에서 같거나 높은 입력 우선순위(%s)로만 이동합니다. 차이가 클수록 먼저 처리됩니다.",
    "text.modern_industrialization.SteamDrillToggle": "- %s + %s로 섬세한 손길을 전환하세요.",
    "text.modern_industrialization.SteamDrillWaterHelp": "- 고인 물이나 흐르는 물에서 %s을(를) 눌러 채우세요.",
    "text.modern_industrialization.TooltipSpeedUpgrade": "아이템 파이프 속도 업그레이드: 3초당 아이템 +%d개.",
    "text.modern_industrialization.TooltipSpeedUpgradeStack": "전체 중첩 업그레이드: 3초당 아이템 +%d개.",
    "text.modern_industrialization.TooltipsShiftRequired": "[Shift] 키를 눌러 정보 보기",
}

TAG_ROOT_TRANSLATIONS = {
    "tag.c.dusts": "가루",
    "tag.c.gears": "톱니바퀴",
    "tag.c.ingots": "주괴",
    "tag.c.nuggets": "조각",
    "tag.c.ores": "광석",
    "tag.c.plates": "판",
    "tag.c.raw_materials": "원석",
    "tag.c.rods": "막대",
    "tag.c.storage_blocks": "저장 블록",
    "tag.c.tiny_dusts": "작은 가루",
    "tag.modern_industrialization.barrels": "배럴",
    "tag.modern_industrialization.fluid_pipes": "유체 파이프",
    "tag.modern_industrialization.forge_hammer_tools": "단조 망치 도구",
    "tag.modern_industrialization.item_pipes": "아이템 파이프",
    "tag.modern_industrialization.me_wires": "ME 전선",
    "tag.modern_industrialization.replicator_blacklist": "복제기 블랙리스트",
    "tag.modern_industrialization.tanks": "탱크",
}

TAG_ITEM_SUFFIXES = {
    "dusts": "_dust",
    "gears": "_gear",
    "gems": "",
    "ingots": "_ingot",
    "nuggets": "_nugget",
    "plates": "_plate",
    "raw_materials": "",
    "rods": "_rod",
    "tiny_dusts": "_tiny_dust",
}


def dump_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 안정된 형식으로 기록한다."""
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def reviewed_candidate(key: str, value: object) -> object:
    """기존 한국어 후보의 반복적인 기계번역식 용어를 교정한다."""
    if not isinstance(value, str):
        return value
    for before, after in BASE_REPLACEMENTS:
        value = value.replace(before, after)
    value = value.rstrip()
    if key.startswith("block.modern_industrialization.") and key.endswith("_barrel"):
        if value.endswith(" 통"):
            value = value[:-2] + " 배럴"
    if key.startswith("block.modern_industrialization.") and key.endswith(
        "_transformer"
    ):
        value = value.replace(" to ", "→")
    return value


def translate_tag(key: str, korean: dict[str, object]) -> str | None:
    """공통 태그 이름을 검수된 실제 아이템·블록 이름과 일치시킨다."""
    if key in TAG_ROOT_TRANSLATIONS:
        return TAG_ROOT_TRANSLATIONS[key]
    parts = key.split(".")
    if len(parts) != 4 or parts[:2] != ["tag", "c"]:
        return None
    category, material = parts[2:]
    if category in TAG_ITEM_SUFFIXES:
        if category == "raw_materials":
            reference = f"item.modern_industrialization.raw_{material}"
        else:
            reference = (
                f"item.modern_industrialization.{material}"
                f"{TAG_ITEM_SUFFIXES[category]}"
            )
    elif category == "ores":
        reference = f"block.modern_industrialization.{material}_ore"
    elif category == "storage_blocks":
        reference = f"block.modern_industrialization.{material}_block"
    else:
        return None
    value = korean.get(reference)
    return value if isinstance(value, str) else None


def translate_missing(
    key: str, source: object, korean: dict[str, object]
) -> object | None:
    """신규 키를 확정 번역 또는 검수된 이름 규칙으로 번역한다."""
    if isinstance(source, str) and source in ALLOWED_ORIGINALS:
        return source
    if isinstance(source, str) and source in VALUE_TRANSLATIONS:
        return VALUE_TRANSLATIONS[source]
    if key.startswith("tag."):
        return translate_tag(key, korean)
    return None


def normalize() -> dict[str, object]:
    """확정 번역과 검수 규칙을 작업본에 반영한다."""
    rows = []
    for namespace in NAMESPACES:
        root = WORK_ROOT / namespace
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        sources = load_json(root / "candidate_sources.json")
        source_counts = Counter(sources.values())
        unresolved = []
        changed = 0
        for key, source in english.items():
            candidate = korean[key]
            if key in BASE_KEY_OVERRIDES:
                translated = BASE_KEY_OVERRIDES[key]
            elif sources[key] == "bundled_ko_kr":
                translated = reviewed_candidate(key, candidate)
            else:
                translated = translate_missing(key, source, korean)
                if translated is None:
                    unresolved.append(key)
                    continue
            if translated != candidate:
                korean[key] = translated
                changed += 1
        dump_json(root / "ko_kr.json", korean)
        rows.append(
            {
                "namespace": namespace,
                "keys": len(english),
                "candidate_sources": dict(source_counts),
                "changed": changed,
                "unresolved": len(unresolved),
                "unresolved_examples": unresolved[:100],
            }
        )
    report = {"namespaces": rows}
    dump_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], list[str]]:
    """모든 키의 번역·형식·자료형을 검사한다."""
    rows = []
    errors = []
    for namespace in NAMESPACES:
        root = WORK_ROOT / namespace
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        if list(english) != list(korean):
            errors.append(f"키 또는 순서 불일치: {namespace}")
            continue
        untranslated = []
        for key, source in english.items():
            target = korean[key]
            errors.extend(validate_value(key, source, target))
            if (
                isinstance(source, str)
                and isinstance(target, str)
                and source == target
                and source not in ALLOWED_ORIGINALS
                and not is_allowed_original(source)
            ):
                untranslated.append(key)
        if untranslated:
            errors.append(f"미번역: {namespace}:{untranslated[:50]}")
        rows.append(
            {
                "namespace": namespace,
                "keys": len(english),
                "untranslated": len(untranslated),
            }
        )
    report = {
        "namespaces": rows,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    dump_json(WORK_ROOT / "specialized_language_validation.json", report)
    return report, errors


def build_extras() -> dict[str, object]:
    """KubeJS가 추가한 MI 언어 키를 작업 보고서와 리소스팩에 병합한다."""
    extra_path = WORK_ROOT / "kubejs_extra_ko_kr.json"
    dump_json(extra_path, KUBEJS_EXTRA_TRANSLATIONS)
    output_path = (
        active_output_root()
        / "resourcepack/ATM10_Korean/assets/modern_industrialization/lang/ko_kr.json"
    )
    output = load_json(output_path)
    output.update(KUBEJS_EXTRA_TRANSLATIONS)
    dump_json(output_path, output)
    return {
        "base_keys": len(output) - len(KUBEJS_EXTRA_TRANSLATIONS),
        "kubejs_extra_keys": len(KUBEJS_EXTRA_TRANSLATIONS),
        "output_keys": len(output),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("normalize", "verify", "build-extras"))
    args = parser.parse_args()
    if args.command == "normalize":
        report = normalize()
        errors = []
    elif args.command == "verify":
        report, errors = verify()
    else:
        report = build_extras()
        errors = []
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
