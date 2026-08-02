#!/usr/bin/env python3
"""Steve's Carts 언어와 관련 표시 문구를 번역하고 검증한다."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path
from zipfile import ZipFile

import actually_additions_family as candidate_helper
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root


FAMILY = "steves_carts"
WORK_ROOT = PROJECT_ROOT / "working/steves_carts"
CACHE_FILE = PROJECT_ROOT / "temp/steves_carts_language_candidate_cache_v1.json"
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"
PLACEHOLDER = re.compile(
    r"%(?:\d+\$)?(?:\.\d+)?[A-Za-z%]|\{[^{}]*\}|"
    r"§[0-9A-FK-ORa-fk-or]|&[0-9A-FK-ORa-fk-or]"
)
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")

SOURCE_OVERRIDES = {
    "Steve's Carts": "Steve's Carts",
    "Steve's Carts - Blocks": "Steve's Carts - 블록",
    "Steve's Carts - Components": "Steve's Carts - 부품",
    "Steve's Carts - Modules": "Steve's Carts - 모듈",
    "Cart": "카트",
    "Minecart": "광산 수레",
    "Cart Assembler": "카트 조립기",
    "Cart Modifier": "카트 개조기",
    "Module Toggler": "모듈 전환기",
    "Cargo Manager": "화물 관리자",
    "Liquid Manager": "유체 관리자",
    "External Distributor": "외부 분배기",
    "Detector Unit": "감지 장치",
    "Advanced Detector Rail": "고급 감지 레일",
    "Junction Rail": "분기 레일",
    "Cart Disassembler": "카트 분해기",
    "Module": "모듈",
    "Hull": "차체",
    "Standard Hull": "표준 차체",
    "Wooden Hull": "나무 차체",
    "Reinforced Hull": "강화 차체",
    "Galgadorian Hull": "갈가도리안 차체",
    "Creative Hull": "크리에이티브 차체",
    "Engine": "엔진",
    "Coal Engine": "석탄 엔진",
    "Thermal Engine": "열 엔진",
    "Solar Engine": "태양광 엔진",
    "Creative Engine": "크리에이티브 엔진",
    "Drill": "드릴",
    "Hardened Drill": "경화 드릴",
    "Galgadorian Drill": "갈가도리안 드릴",
    "Wood Cutter": "벌목기",
    "Hardened Wood Cutter": "경화 벌목기",
    "Galgadorian Wood Cutter": "갈가도리안 벌목기",
    "Farmer": "농사 모듈",
    "Shooter": "발사기",
    "Advanced Shooter": "고급 발사기",
    "Chunk Loader": "청크 로더",
    "Track Remover": "레일 제거기",
    "Entity Detector": "엔티티 감지기",
    "Player Detector": "플레이어 감지기",
    "Animal Detector": "동물 감지기",
    "Hostile Detector": "적대적 몹 감지기",
    "Tank": "탱크",
    "Side Tanks": "측면 탱크",
    "Top Tank": "상단 탱크",
    "Front Tank": "전면 탱크",
    "Reinforced Metal": "강화 금속",
    "Stabilized Metal": "안정화 금속",
    "Galgadorian Metal": "갈가도리안 금속",
    "Reinforced Metal Block": "강화 금속 블록",
    "Galgadorian Metal Block": "갈가도리안 금속 블록",
    "Simple PCB": "간단한 PCB",
    "Production Line": "생산 라인",
    "Assembly": "조립",
    "Cost": "비용",
    "Capacity": "용량",
    "Storage": "저장소",
    "Fuel": "연료",
    "Efficiency": "효율",
    "Durability": "내구도",
    "Current tool": "현재 도구",
    "Disabled": "비활성화",
    "Enabled": "활성화",
    "On": "켜기",
    "Off": "끄기",
    "Yes": "예",
    "No": "아니요",
    "None": "없음",
    "Owner": "소유자",
    "Mode": "모드",
    "Direction": "방향",
    "Input": "입력",
    "Output": "출력",
    "Left": "왼쪽",
    "Right": "오른쪽",
    "All": "모두",
    "Redstone": "레드스톤",
    "Inventory": "인벤토리",
    "Experience": "경험치",
    "Height": "높이",
    "Width": "너비",
    "Delay": "지연 시간",
    "Range": "범위",
    "Speed": "속도",
}

TERM_REPLACEMENTS = (
    ("[%2:item|items]", "[%2:아이템|아이템]"),
    ("[%2:unit|units]", "[%2:단위|단위]"),
    ("[%2:side|sides]", "[%2:면|면]"),
    ("[%1:second|seconds]", "[%1:초|초]"),
    ("Steve's 카트", "Steve's Carts"),
    ("스티브의 카트", "Steve's Carts"),
    ("스티브 카트", "Steve's Carts"),
    ("Galgadorian", "갈가도리안"),
    ("Galadorian", "갈가도리안"),
    ("갈가도리안인", "갈가도리안"),
    ("강화된 금속", "강화 금속"),
    ("안정된 금속", "안정화 금속"),
    ("안정화된 금속", "안정화 금속"),
    ("선체", "차체"),
    ("홀", "차체"),
    ("모듈식", "모듈"),
    ("액체", "유체"),
    ("재고", "인벤토리"),
    ("GUI", "화면"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("마우스 왼쪽 버튼을 클릭", "좌클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("왼쪽 클릭", "좌클릭"),
    ("업그레이드", "업그레이드"),
    ("레드 스톤", "레드스톤"),
    ("엔터티", "엔티티"),
    ("장바구니", "카트"),
    ("헐", "차체"),
    ("어셈블러", "조립기"),
    ("크래프터", "제작기"),
    ("가슴", "상자"),
    ("탐지기", "감지기"),
    ("탐지 레일", "감지 레일"),
    ("검출기", "감지기"),
    ("마을 사람들", "주민"),
    ("다이아 패 한 벌", "다이아몬드"),
    ("철괴", "철 주괴"),
    ("토치", "횃불"),
    ("비녀장", "전환"),
    ("이체", "전송"),
    ("쉴드", "방패"),
    ("구하다", "저장"),
)

QUEST_OVERRIDES: dict[str, object] = {
    "quest.309B0B2898893B4E.quest_desc": [
        "&b&lSteve's Carts&r는 카트를 업그레이드하는 모드입니다! \\n\\n어떤 업그레이드가 있냐고요? 싱크대만 빼면 거의 다 있습니다! \\n\\n드릴부터 총과 아케이드 기계까지! 카트에 무엇을 더 바라겠어요?"
    ],
    "quest.309B0B2898893B4E.title": "&l&bSteve's Carts",
    "quest.55BF254B1831359B.quest_desc": [
        "&5갈가도리안 드릴&r은 카트에 장착할 수 있는 최고의 드릴입니다. \\n\\n그만큼 제작하기도 더 어렵습니다... \\n&3안정화 금속&r이 아주 많이 필요하다고만 해 두죠! 조합법을 따라가세요!"
    ],
    "quest.55BF254B1831359B.title": "&5갈가도리안 드릴",
}

KEY_OVERRIDES = {
    "arcade.stevescarts.buttonSave": "저장",
    "arcade.stevescarts.buttonStartLevel": "레벨 시작",
    "arcade.stevescarts.buttonStop": "중지",
    "arcade.stevescarts.creeperHighScores": "최고 기록",
    "arcade.stevescarts.creeperMapName1": "소형",
    "arcade.stevescarts.creeperMapName2": "중형",
    "arcade.stevescarts.creeperMapName3": "대형",
    "arcade.stevescarts.ghastLives": "추가 목숨",
    "arcade.stevescarts.instructionDrop": "떨어뜨리기",
    "arcade.stevescarts.leftMouseButton": "왼쪽 버튼",
    "arcade.stevescarts.operatorHelp": (
        "플레이 방법은 스토리 모드에서 '시작' 스토리를 실행해 확인할 수 있습니다. 직접 "
        "맵을 만들려면 맵 편집기에서 새 맵을 생성하세요. 자세한 설명도 편집기 안에 "
        "있습니다. 감지 레일과 분기점을 연결하려면 감지 레일을 클릭한 뒤 분기점을 "
        "클릭하세요. 더 자세한 내용은 위키를 참고하세요."
    ),
    "arcade.stevescarts.operatorSave": "저장",
    "arcade.stevescarts.rightMouseButton": "오른쪽 버튼",
    "arcade.stevescarts.stackerRemovedLinesCombo": ("[%1->한|두|세|네] 줄 제거: [%2]"),
    "block.stevescarts.enhanced_galgadorian_metal": "고급 갈가도리안 블록",
    "block.stevescarts.upgrade_cart_deployer": "업그레이드: 카트 배치기",
    "block.stevescarts.upgrade_cart_modifier": "업그레이드: 카트 개조기",
    "block.stevescarts.upgrade_experienced_assembler": "업그레이드: 숙련 조립기",
    "block.stevescarts.upgrade_manager_bridge": "업그레이드: 관리자 연결",
    "block.stevescarts.upgrade_quick_demolisher": "업그레이드: 고속 분해기",
    "gui.stevescarts.assembleProgress": "진행도",
    "gui.stevescarts.basicAssembleInstruction": (
        "카트 제작을 시작하려면 원하는 카트 차체를 차체 슬롯에 넣으세요."
    ),
    "gui.stevescarts.busyAssemblerError": "조립기가 작업 중입니다!",
    "gui.stevescarts.cargoManager": "화물",
    "gui.stevescarts.cartAreaBridge": "다리 재료",
    "gui.stevescarts.cartAreaBuckets": "양동이(착유기용)",
    "gui.stevescarts.currentSide": "현재 면",
    "gui.stevescarts.departureBayError": "출발 구역에 카트가 있습니다.",
    "gui.stevescarts.directionFromCart": "카트에서 꺼내기",
    "gui.stevescarts.directionToCart": "카트에 넣기",
    "gui.stevescarts.distributorFromCart": "카트에서 꺼내기",
    "gui.stevescarts.distributorToCart": "카트에 넣기",
    "gui.stevescarts.managerBot": "하단 관리자",
    "gui.stevescarts.managerTop": "상단 관리자",
    "gui.stevescarts.modifyCart": "카트 개조",
    "gui.stevescarts.noHullError": "차체가 없습니다.",
    "gui.stevescarts.operatorAnd": "AND",
    "gui.stevescarts.operatorEastUnit": "동쪽 장치",
    "gui.stevescarts.operatorNorthUnit": "북쪽 장치",
    "gui.stevescarts.operatorNot": "NOT",
    "gui.stevescarts.operatorOutput": "출력",
    "gui.stevescarts.operatorSouthUnit": "남쪽 장치",
    "gui.stevescarts.operatorTopUnit": "상단 장치",
    "gui.stevescarts.operatorWestUnit": "서쪽 장치",
    "gui.stevescarts.optionCage": "우리 생물 태우기",
    "gui.stevescarts.optionCageAuto": "우리 자동 태우기",
    "gui.stevescarts.sateSeeds": "씨앗 보유",
    "gui.stevescarts.stateBat": "박쥐 승객 있음",
    "gui.stevescarts.stateBridge": "다리 재료 보유",
    "gui.stevescarts.stateCake": "케이크 보유",
    "gui.stevescarts.stateChicken": "닭 승객 있음",
    "gui.stevescarts.stateFertilizing": "비료 보유",
    "gui.stevescarts.stateHostile": "적대적 몹 승객 있음",
    "gui.stevescarts.stateProjectiles": "발사체 보유",
    "gui.stevescarts.stateRails": "레일 보유",
    "gui.stevescarts.stateSaplings": "묘목 보유",
    "gui.stevescarts.stateShield": "방패 활성화 여부",
    "gui.stevescarts.stateSpider": "거미 승객 있음",
    "gui.stevescarts.stateToggle": "전환",
    "gui.stevescarts.stateTorches": "횃불 보유",
    "gui.stevescarts.transferAll": "가능한 만큼 전송",
    "gui.stevescarts.transferAllLiquid": "가능한 만큼 전송",
    "gui.stevescarts.turnBack": "전송 후 돌아가기",
    "info.stevescarts.alphaExtraMessage": "알파 버전 1주년",
    "info.stevescarts.cartSideBottom": "아래",
    "info.stevescarts.cartSideCenter": "가운데",
    "info.stevescarts.cartSideTop": "위",
    "info.stevescarts.effectBlueprint": "설계도 카트를 사용할 수 있습니다.",
    "info.stevescarts.effectInputChest": "슬롯이 [%1]개인 입력 상자입니다.",
    "info.stevescarts.moduleCategoryAttachment": "부착물",
    "info.stevescarts.moduleConflictAlso": "다음 항목과도 충돌:",
    "info.stevescarts.moduleConflictHowever": "단, 다음 항목과 충돌:",
    "info.stevescarts.moduleCount3": "셋",
    "info.stevescarts.moduleGroupFarmer": "[%1:농사 모듈|농사 모듈]",
    "info.stevescarts.moduleGroupShooter": "[%1:발사기|발사기]",
    "info.stevescarts.moduleGroupToolShooter": (
        "[%1:도구|도구] 또는 [%1:발사기|발사기]"
    ),
    "info.stevescarts.moduleRequirement": "필요 항목",
    "item.stevescarts.BlockDetector0": "감지 관리자",
    "item.stevescarts.BlockDetector2": "감지 정거장",
    "item.stevescarts.BlockDetector3": "감지 분기점",
    "item.stevescarts.BlockDetector4": "레드스톤 감지 장치",
    "item.stevescarts.advanced_crafter": "고급 제작기",
    "item.stevescarts.advanced_smelter": "고급 제련기",
    "item.stevescarts.basic_farmer": "기본 농사 모듈",
    "item.stevescarts.basic_wood_cutter": "기본 벌목기",
    "item.stevescarts.blank_upgrade": "빈 업그레이드",
    "item.stevescarts.bridge_builder": "다리 건설기",
    "item.stevescarts.cage": "우리",
    "item.stevescarts.chest_lock": "상자 잠금장치",
    "item.stevescarts.chest_pane": "상자 판",
    "item.stevescarts.creative_incinerator": "크리에이티브 소각로",
    "item.stevescarts.creative_supplies": "크리에이티브 보급품",
    "item.stevescarts.crop_nether_wart": "작물: 네더 사마귀",
    "item.stevescarts.enchanter": "마법 부여기",
    "item.stevescarts.enhanced_galgadorian_metal": "고급 갈가도리안 금속",
    "item.stevescarts.entity_detector_animal": "엔티티 감지기: 동물",
    "item.stevescarts.entity_detector_bat": "엔티티 감지기: 박쥐",
    "item.stevescarts.entity_detector_monster": "엔티티 감지기: 몬스터",
    "item.stevescarts.entity_detector_villager": "엔티티 감지기: 주민",
    "item.stevescarts.experience_bank": "경험치 은행",
    "item.stevescarts.extracting_chests": "추출 상자",
    "item.stevescarts.front_chest": "전면 상자",
    "item.stevescarts.galgadorian_farmer": "갈가도리안 농사 모듈",
    "item.stevescarts.gift_storage": "선물 저장소",
    "item.stevescarts.hardened_mesh": "경화 망",
    "item.stevescarts.huge_chest_pane": "거대 상자 판",
    "item.stevescarts.huge_dynamic_pane": "거대 동적 판",
    "item.stevescarts.huge_iron_pane": "거대 철판",
    "item.stevescarts.huge_sctank_pane": "거대 탱크 판",
    "item.stevescarts.hydrator": "수분 공급기",
    "item.stevescarts.iron_blade": "철 칼날",
    "item.stevescarts.iron_drill": "철 드릴",
    "item.stevescarts.large_chest_pane": "대형 상자 판",
    "item.stevescarts.large_dynamic_pane": "대형 동적 판",
    "item.stevescarts.large_lump_of_galgador": "대형 갈가도르 덩어리",
    "item.stevescarts.large_railer": "대형 레일 설치기",
    "item.stevescarts.liquid_cleaner": "유체 청소기",
    "item.stevescarts.melter": "용해기",
    "item.stevescarts.modularcart": "모듈 카트",
    "item.stevescarts.netherite_wood_cutter": "네더라이트 벌목기",
    "item.stevescarts.oak_log": "참나무 원목",
    "item.stevescarts.oak_twig": "참나무 가지",
    "item.stevescarts.planter_range_extender": "심기 범위 확장기",
    "item.stevescarts.power_observer": "동력 감지기",
    "item.stevescarts.projectile_fire_charge": "발사체: 화염구",
    "item.stevescarts.railer": "레일 설치기",
    "item.stevescarts.raw_handle": "미가공 손잡이",
    "item.stevescarts.refined_handle": "정제 손잡이",
    "item.stevescarts.sctank_pane": "탱크 판",
    "item.stevescarts.shooting_station": "발사 정거장",
    "item.stevescarts.side_chests": "측면 상자",
    "item.stevescarts.smelter": "제련기",
    "item.stevescarts.sock": "양말",
    "item.stevescarts.speed_handle": "속도 손잡이",
    "item.stevescarts.stuffed_sock": "채운 양말",
    "item.stevescarts.top_chest": "상단 상자",
    "item.stevescarts.torch_placer": "횃불 설치기",
    "item.stevescarts.treetap": "수액 채취 모듈",
    "item.stevescarts.tri_torch": "삼중 횃불",
    "item.stevescarts.unknowncomponent": "알 수 없는 Steve's Carts 부품",
    "item.stevescarts.unknownmodule": "알 수 없는 Steve's Carts 모듈",
    "item.stevescarts.upgrade_cart_deployer": "업그레이드: 카트 배치기",
    "item.stevescarts.upgrade_cart_modifier": "업그레이드: 카트 개조기",
    "item.stevescarts.upgrade_experienced_assembler": "업그레이드: 숙련 조립기",
    "item.stevescarts.upgrade_manager_bridge": "업그레이드: 관리자 연결",
    "item.stevescarts.upgrade_quick_demolisher": "업그레이드: 고속 분해기",
    "modules.addons.stevescarts.informationProviderLabelStorage": "사용 중인 저장소",
    "modules.addons.stevescarts.informationProviderMessageUnbreakable": (
        "파괴되지 않는 도구"
    ),
    "modules.addons.stevescarts.intelligenceChange": "드릴 지능 설정 변경",
    "modules.addons.stevescarts.leverStartCart": "카트 출발",
    "modules.addons.stevescarts.leverStopCart": "카트 정지",
    "modules.addons.stevescarts.leverTurnAroundCart": "카트 방향 전환",
    "modules.addons.stevescarts.planterRangeExtenderTitle": "심기 범위",
    "modules.addons.stevescarts.recipeChangeLimit": (
        "유지할 아이템 수 [%1->증가|감소]"
    ),
    "modules.addons.stevescarts.recipeDisabled": "생산 안 함",
    "modules.addons.stevescarts.recipeLimit": "유지할 아이템 제한",
    "modules.attachments.stevescarts.controlSystemOdoMeter": "총거리",
    "modules.attachments.stevescarts.controlSystemTripMeter": "구간 거리",
    "modules.attachments.stevescarts.experienceExtract": "클릭해 경험치 50 추출",
    "modules.attachments.stevescarts.noteAdd": "연주 목록 #[%1]에 음 추가",
    "modules.attachments.stevescarts.noteCreateTrack": "새 연주 목록 만들기",
    "modules.attachments.stevescarts.noteDeactivateInstrument": "노트 블록 설정 제거",
    "modules.attachments.stevescarts.noteDelay": "지연 변경. 현재 지연: [%1]",
    "modules.attachments.stevescarts.noteRemove": ("연주 목록 #[%1]의 마지막 음 제거"),
    "modules.attachments.stevescarts.noteRemoveTrack": "맨 아래 연주 목록 제거",
    "modules.attachments.stevescarts.noteVolume": (
        "연주 음량: [%1->음소거|낮음|보통|높음]"
    ),
    "modules.attachments.stevescarts.railerTitle": "레일 설치기",
    "modules.attachments.stevescarts.seatStateMessage": (
        "[%1->이 카트는 사용 중입니다|카트 타기|카트 내리기]"
    ),
    "modules.engines.stevescarts.outOfLava": "용암 부족",
    "modules.engines.stevescarts.outOfPower": "동력 부족",
    "modules.engines.stevescarts.thermalPowered": "동력 공급됨",
    "modules.tanks.stevescarts.tankEmpty": "비어 있음",
    "modules.tanks.stevescarts.tankInvalidFluid": "알 수 없음",
    "modules.tanks.stevescarts.tankLocked": "고정 대상:",
    "modules.tools.stevescarts.cutterTitle": "벌목기",
    "modules.tools.stevescarts.repairDiamonds": "다이아몬드",
    "modules.tools.stevescarts.repairIron": "철 주괴",
    "modules.tools.stevescarts.toolBroken": "파손됨",
    "modules.tools.stevescarts.toolRepairing": "도구 수리 중",
    "stevescarts.creativetab.items": "Steve's Carts 2 - 부품",
    "stories.beginning.stevescarts.detector": (
        "감지 레일은 친구가 될 수도 적이 될 수도 있습니다. Steve가 감지 레일을 지나면 "
        "강철 분기점을 포함한 여러 분기점의 방향이 바뀔 수 있습니다. 영향을 받을 "
        "분기점은 감지 레일에 마우스를 올려 확인하세요."
    ),
    "stories.beginning.stevescarts.goodJob": "잘했습니다. 바로 그렇게 하는 겁니다.",
    "stories.beginning.stevescarts.map": (
        "Steve가 지도를 얻었습니다. 계속하려면 다음 레벨 버튼을 누르세요."
    ),
    "stories.beginning.stevescarts.steel": (
        "길에는 늘 장애물이 있습니다. 레일 운영자에게는 강철 레일이 그런 존재입니다. "
        "강철 분기점은 방향을 바꿀 수 없습니다. 행운을 빕니다."
    ),
    "stories.beginning.stevescarts.trackOperator": (
        "여러분은 레일 운영자입니다. 레일이 올바르게 이어지도록 만드는 것이 임무입니다. "
        "시작 버튼을 누르기 전에 분기점을 클릭해 방향을 바꾸세요."
    ),
}


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
        return f"QXSC{len(tokens) - 1}QX"

    protected = PLACEHOLDER.sub(hide, source).replace("\n", " QXSCNEWLINEQX ")
    translated = candidate_helper.request_translation_candidate(protected)
    translated = translated.replace(" QXSCNEWLINEQX ", "\n").replace(
        "QXSCNEWLINEQX", "\n"
    )
    for index, token in enumerate(tokens):
        marker = f"QXSC{index}QX"
        if marker not in translated:
            raise ValueError(f"보호 표식이 사라졌습니다: {source}: {marker}")
        translated = translated.replace(marker, token)
    return translated


def candidate() -> dict[str, object]:
    english = load_json(WORK_ROOT / "stevescarts/en_us.json")
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests = {
        source
        for source in english.values()
        if source not in SOURCE_OVERRIDES
        and LATIN_WORD.search(source)
        and not isinstance(cache.get(source), str)
    }
    failures: list[str] = []
    if requests:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(request_candidate, source): source
                for source in sorted(requests)
            }
            for number, future in enumerate(as_completed(futures), start=1):
                source = futures[future]
                try:
                    cache[source] = future.result()
                    if number % 25 == 0:
                        write_json(CACHE_FILE, cache)
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("번역 후보 생성 실패:\n" + "\n".join(failures))
    candidates = {
        key: SOURCE_OVERRIDES.get(source, cache.get(source, source))
        for key, source in english.items()
    }
    write_json(CANDIDATE_FILE, candidates)
    report = {
        "keys": len(english),
        "unique_sources": len(set(english.values())),
        "candidate_sources": len(requests),
        "status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


def reviewed_value(key: str, source: str, candidate_value: str) -> str:
    value = KEY_OVERRIDES.get(key, SOURCE_OVERRIDES.get(source, candidate_value))
    for old, new in TERM_REPLACEMENTS:
        value = value.replace(old, new)
    value = value.replace(".,", ".").replace(". ,", ".")
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    leading = source[: len(source) - len(source.lstrip())]
    trailing = source[len(source.rstrip()) :]
    return leading + value.strip() + trailing


def normalize() -> dict[str, object]:
    english = load_json(WORK_ROOT / "stevescarts/en_us.json")
    candidates = load_json(CANDIDATE_FILE)
    korean = {
        key: reviewed_value(key, source, candidates[key])
        for key, source in english.items()
    }
    write_json(WORK_ROOT / "stevescarts/ko_kr.json", korean)
    root = WORK_ROOT / "quests/related"
    quest_english = json.loads((root / "en_us.json").read_text(encoding="utf-8"))
    missing = sorted(set(quest_english) - set(QUEST_OVERRIDES))
    if missing:
        raise RuntimeError(f"퀘스트 확정 번역 누락: {missing}")
    write_json(
        root / "ko_kr.json",
        {key: QUEST_OVERRIDES[key] for key in quest_english},
    )
    report = {
        "language_keys_reviewed": len(english),
        "quest_display_keys_reviewed": len(quest_english),
        "bundled_korean_reused_without_review": 0,
        "status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    untranslated: list[str] = []
    english = load_json(WORK_ROOT / "stevescarts/en_us.json")
    korean = load_json(WORK_ROOT / "stevescarts/ko_kr.json")
    if list(english) != list(korean):
        errors.append("언어 키 또는 순서 불일치")
    for key, source in english.items():
        target = korean.get(key, "")
        errors.extend(
            f"stevescarts:{key}: {error}"
            for error in family_goal.validate_family_value(FAMILY, key, source, target)
        )
        if (
            source == target
            and LATIN_WORD.search(source)
            and source not in SOURCE_OVERRIDES
            and not family_goal.is_allowed_original(source)
        ):
            untranslated.append(key)
        forbidden = (
            "장바구니",
            "헐 슬롯",
            "너에겐 껍질",
            "구하다",
            "비녀장",
            "다이아 패 한 벌",
            "재고 품목",
            "마우스 오른쪽 버튼",
            "마우스 왼쪽 버튼",
            "스티브의 카트",
            "Steve's 카트",
            "[%2:item|items]",
            "[%2:unit|units]",
            "[%2:side|sides]",
            "NoteBlock",
        )
        if any(fragment in target for fragment in forbidden):
            errors.append(f"stevescarts:{key}: 기계번역 흔적")
    root = WORK_ROOT / "quests/related"
    source_rows = json.loads((root / "en_us.json").read_text(encoding="utf-8"))
    target_rows = json.loads((root / "ko_kr.json").read_text(encoding="utf-8"))
    for key, source in source_rows.items():
        source_text = family_goal.quest_snbt.flatten(source)
        target_text = family_goal.quest_snbt.flatten(target_rows.get(key))
        if Counter(PLACEHOLDER.findall(source_text)) != Counter(
            PLACEHOLDER.findall(target_text)
        ):
            errors.append(f"related:{key}: 서식 코드 또는 자리표시자 불일치")
        if source_text.count("\\n") != target_text.count("\\n"):
            errors.append(f"related:{key}: 줄바꿈 불일치")
    if untranslated:
        errors.append("미번역 키: " + ", ".join(untranslated[:30]))
    report = {
        "language_keys_reviewed": len(english),
        "quest_display_keys_reviewed": len(source_rows),
        "bundled_korean_reused_without_review": 0,
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", report)
    return report, errors


def audit() -> dict[str, object]:
    instance = resolve_source_root()
    jar = next((instance / "mods").glob("stevescarts-*.jar"))
    advancements = display_nodes = 0
    with ZipFile(jar) as archive:
        for name in archive.namelist():
            if "/advancement/" not in name or not name.endswith(".json"):
                continue
            advancements += 1
            data = json.loads(archive.read(name))
            if isinstance(data, dict) and isinstance(data.get("display"), dict):
                display_nodes += 1
    references: list[str] = []
    direct_display: list[str] = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "stevescarts:" not in text.lower():
            continue
        relative = path.relative_to(instance).as_posix()
        references.append(relative)
        if path.suffix.lower() == ".js":
            for number, line in enumerate(text.splitlines(), start=1):
                if re.search(
                    r"displayName|setHoverName|tooltip|Text\.(?:of|literal)", line, re.I
                ):
                    direct_display.append(f"{relative}:{number}")
    report = {
        "advancement_files": advancements,
        "advancement_display_nodes": display_nodes,
        "kubejs_reference_files": references,
        "kubejs_direct_display_lines": direct_display,
        "status": "complete" if not direct_display else "review_required",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("candidate", "normalize", "verify", "audit")
    )
    args = parser.parse_args()
    if args.command == "candidate":
        report = candidate()
        code = 0
    elif args.command == "normalize":
        report = normalize()
        code = 0
    elif args.command == "verify":
        report, errors = verify()
        code = 1 if errors else 0
    else:
        report = audit()
        code = 0 if report["status"] == "complete" else 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
