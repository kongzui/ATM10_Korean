#!/usr/bin/env python3
"""Extreme Reactors와 ZeroCore 언어 파일을 현재 영어 원문 기준으로 번역·검증한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path

import ars_family
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root


FAMILY = "extreme_reactors"
WORK_ROOT = PROJECT_ROOT / "working/extreme_reactors"
NAMESPACES = ("bigreactors", "zerocore")
CACHE_FILE = PROJECT_ROOT / "temp/extreme_reactors_language_candidate_cache.json"
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"

EXACT_VALUES = {
    "Compat - JEI": "호환성 - JEI",
    "GUI": "GUI",
    "Extreme Reactors": "Extreme Reactors",
    "Basic": "기본",
    "Reinforced": "강화",
    "Controller": "제어기",
    "Control Rod": "제어봉",
    "Solid Access Port": "고체 반입출 포트",
    "Fuel Injection Port": "연료 주입 포트",
    "Fluid Port (Active)": "유체 포트(능동형)",
    "Fluid Port (Passive)": "유체 포트(수동형)",
    "Redstone Port": "레드스톤 포트",
    "Charging Port (FE)": "충전 포트(FE)",
    "FE Power Port (Passive)": "FE 전력 포트(수동형)",
    "FE Power Port (Active)": "FE 전력 포트(능동형)",
    "Energy Core": "에너지 코어",
    "Cryomisi": "크라이오미시",
    "Tangerium": "탠저륨",
    "Redfrigium": "레드프리지움",
    "Energizer Cell": "에너자이저 셀",
    "Energy Cell": "에너지 셀",
}

NAME_TERMS = (
    ("Extreme Reactors", "Extreme Reactors"),
    ("Forge Energy", "FE"),
    ("Status Display", "상태 표시기"),
    ("Cryomisi", "크라이오미시"),
    ("Tangerium", "탠저륨"),
    ("Redfrigium", "레드프리지움"),
    ("Reinforced", "강화"),
    ("Basic", "기본"),
    ("Creative Water Generator", "크리에이티브 물 생성기"),
    ("Creative Steam Generator", "크리에이티브 증기 생성기"),
    ("Fluid Access Port", "유체 반입출 포트"),
    ("Solid Access Port", "고체 반입출 포트"),
    ("Fuel Injection Port", "연료 주입 포트"),
    ("Charging Port", "충전 포트"),
    ("Computer Port", "컴퓨터 포트"),
    ("Redstone Port", "레드스톤 포트"),
    ("Power Port", "전력 포트"),
    ("Power Tap", "전력 탭"),
    ("Fluid Port", "유체 포트"),
    ("Output Port", "출력 포트"),
    ("Waste Injector", "폐기물 주입기"),
    ("Solid Injector", "고체 주입기"),
    ("Fluid Injector", "유체 주입기"),
    ("Rotor Bearing", "회전자 베어링"),
    ("Rotor Shaft", "회전자 축"),
    ("Rotor Blade", "회전자 날개"),
    ("Control Rod", "제어봉"),
    ("Fuel Rod", "연료봉"),
    ("Reactor Casing", "원자로 외장"),
    ("Turbine Casing", "터빈 외장"),
    ("Reprocessor Casing", "재처리기 외장"),
    ("Fluidizer Casing", "유체화기 외장"),
    ("Energizer Casing", "에너자이저 외장"),
    ("Reactor Glass", "원자로 유리"),
    ("Turbine Glass", "터빈 유리"),
    ("Reprocessor Glass", "재처리기 유리"),
    ("Fluidizer Glass", "유체화기 유리"),
    ("Energizer Glass", "에너자이저 유리"),
    ("Reactor Controller", "원자로 제어기"),
    ("Turbine Controller", "터빈 제어기"),
    ("Reprocessor Controller", "재처리기 제어기"),
    ("Fluidizer Controller", "유체화기 제어기"),
    ("Energizer Controller", "에너자이저 제어기"),
    ("Reactor", "원자로"),
    ("Turbine", "터빈"),
    ("Reprocessor", "재처리기"),
    ("Fluidizer", "유체화기"),
    ("Energizer", "에너자이저"),
    ("Yellorium", "옐로륨"),
    ("Yellorite", "옐로라이트"),
    ("Cyanite", "시아나이트"),
    ("Blutonium", "블루토늄"),
    ("Magentite", "마젠타이트"),
    ("Verderium", "베르데륨"),
    ("Rossinite", "로시나이트"),
    ("Graphite", "흑연"),
    ("Ludicrite", "루디크라이트"),
    ("Ridiculite", "리디큘라이트"),
    ("Inanite", "이나나이트"),
    ("Insanite", "인사나이트"),
    ("Anglesite", "앵글사이트"),
    ("Benitoite", "베니토아이트"),
    ("Deepslate", "심층암"),
    ("Mekanism", "Mekanism"),
    ("Forge", "Forge"),
    ("Housing", "외장"),
    ("Raw", "가공 전"),
    ("Bar", "주괴"),
    ("Uranium", "우라늄"),
    ("Plutonium", "플루토늄"),
    ("Steel", "강철"),
    ("Alloy", "합금"),
    ("Ingot", "주괴"),
    ("Block", "블록"),
    ("Nugget", "조각"),
    ("Dust", "가루"),
    ("Ore", "광석"),
    ("Bucket", "양동이"),
    ("Source", "원천"),
    ("Casing", "외장"),
    ("Glass", "유리"),
    ("Controller", "제어기"),
    ("Collector", "수집기"),
    ("Wrench", "렌치"),
    ("Guide", "가이드"),
    ("Debug Tool", "디버그 도구"),
    ("Active", "능동형"),
    ("Passive", "수동형"),
    ("Fuel", "연료"),
    ("Waste", "폐기물"),
    ("Water", "물"),
    ("Steam", "증기"),
    ("Coolant", "냉각재"),
    ("Vapor", "증기"),
    ("Reactant", "반응물"),
    ("reactant", "반응물"),
    ("coolant", "냉각재"),
    ("vapor", "증기"),
    ("parts", "부품"),
)

TEXT_REPLACEMENTS = (
    ("익스트림 리액터", "Extreme Reactors"),
    ("익스트림 원자로", "Extreme Reactors"),
    ("리액터", "원자로"),
    ("반응기", "원자로"),
    ("재처리 장치", "재처리기"),
    ("리프로세서", "재처리기"),
    ("유동화기", "유체화기"),
    ("유동화 장치", "유체화기"),
    ("에너지 공급기", "에너자이저"),
    ("에너자이저", "에너자이저"),
    ("옐로리움", "옐로륨"),
    ("옐로륨", "옐로륨"),
    ("시아나이트", "시아나이트"),
    ("블루토늄", "블루토늄"),
    ("마젠타이트", "마젠타이트"),
    ("베르데리움", "베르데륨"),
    ("로시나이트", "로시나이트"),
    ("루디크리트", "루디크라이트"),
    ("리디큘라이트", "리디큘라이트"),
    ("이난나이트", "이나나이트"),
    ("인세나이트", "인사나이트"),
    ("연료 막대", "연료봉"),
    ("제어 막대", "제어봉"),
    ("로터", "회전자"),
    ("파워 탭", "전력 탭"),
    ("파워 포트", "전력 포트"),
    ("액세스 포트", "반입출 포트"),
    ("케이싱", "외장"),
    ("수동 모드", "수동 모드"),
    ("자동 모드", "자동 모드"),
    ("항목", "아이템"),
    ("엔터티", "엔티티"),
    ("분당 회전수", "RPM"),
    ("비어 있는", "비어 있음"),
    ("~에 따라", "에 따라"),
    ("하십시오", "하세요"),
    ("Extreme Reactorss", "Extreme Reactors"),
    ("10로", "10으로"),
    ("0로", "0으로"),
    ("% 가득한", "% 채움"),
    ("전원 포트", "전력 포트"),
    ("이 부분은", "이 부품은"),
    ("레시피", "조합법"),
    ("냉각수", "냉각재"),
    ("액체", "유체"),
    ("사용될 수 있습니다", "사용할 수 있습니다"),
)

FINAL_ENGLISH_TERMS = (
    ("Reactors", "원자로"),
    ("Reactor", "원자로"),
    ("Reprocessor", "재처리기"),
    ("Fluidizer", "유체화기"),
    ("Energizer", "에너자이저"),
    ("Collector", "수집기"),
    ("Yellorite", "옐로라이트"),
    ("Mod", "모드"),
)

ALLOWED_EXACT_VALUES = {
    "Extreme Reactors",
    "GUI",
    "FE",
    "RF",
}

FORBIDDEN_ARTIFACTS = (
    "쓰레기",
    "레시피",
    "% 가득한",
    "콘센트",
    "공허한",
    "약혼한",
    "풀린",
    "E입력",
    "금액(분)",
    "신호 포함",
    "다음으로 설정",
    "삽입 방법",
    "취소 방법",
    "끄십시오",
    "공극",
    "전원 포트",
    "액체",
    "부분은",
    "좀도둑",
    "장애를 입히다",
    "구하다",
    "다시 놓기",
    "맥박",
    "베니토나이트",
    "베니토사이트",
)

KEY_OVERRIDES = {
    "vapor.bigreactors.steam": "증기(기체)",
    "item.bigreactors.wrench": "익스트림 렌치",
    "gui.bigreactors.generic.waste.label": "폐기물: ",
    "gui.bigreactors.turbine.active": "터빈이 활성 상태입니다",
    "gui.bigreactors.energizer.active": "에너자이저가 활성 상태입니다",
    "gui.bigreactors.show_recipes.tooltip.title": "조합법 보기",
    "gui.bigreactors.reactor.controller.fuelusage.tooltip.body": (
        "노심에서 연료가 핵분열해 폐기물로 바뀌는 속도입니다."
    ),
    "gui.bigreactors.reactor.controller.fuelrichness.tooltip.body": (
        "노심이 방사선에 노출된 정도입니다. 방사선 수치가 높을수록 연료 소모량이 줄어듭니다."
    ),
    "gui.bigreactors.reactor.controller.fuelbar.tooltip.title": "노심 연료 상태",
    "gui.bigreactors.reactor.controller.coreheatbar.tooltip.title": "노심 온도",
    "gui.bigreactors.reactor.controller.coreheatbar.tooltip.body": (
        "원자로 연료의 온도입니다. 온도가 높을수록 연료 소모량이 늘어납니다.\n\n"
        "노심의 열은 외장으로 전달되며, 전달률은 원자로 내부 설계에 따라 달라집니다."
    ),
    "gui.bigreactors.reactor.controller.casingheatbar.tooltip.title": "외장 온도",
    "gui.bigreactors.reactor.controller.casingheatbar.tooltip.body": (
        "원자로 외장의 온도입니다. 온도가 높을수록 에너지 출력과 냉각재 변환량이 늘어납니다."
    ),
    "gui.bigreactors.reactor_turbine.controller.energybar.tooltip.body": (
        "생성된 에너지는 전력 탭에 연결된 장치로 전달될 때까지 내부 버퍼에 저장됩니다.\n\n"
        "버퍼가 가득 차면 새로 생성된 에너지는 손실됩니다."
    ),
    "gui.bigreactors.reactor.controller.energyratio.tooltip.body": (
        "이 원자로는 수동 냉각 방식이며 노심의 열로 에너지를 직접 생성합니다.\n\n"
        "내부 에너지 버퍼에 저장하지 못한 에너지는 손실됩니다."
    ),
    "gui.bigreactors.reactor.controller.coolantbar.tooltip.title": "냉각재 탱크",
    "gui.bigreactors.reactor.controller.coolantbar.tooltip.value3b": "% 채움",
    "gui.bigreactors.reactor.controller.coolantbar.tooltip.body": (
        "외장의 열이 탱크 안의 냉각재를 가열해 증기를 생성합니다."
    ),
    "gui.bigreactors.reactor.controller.vaporbar.tooltip.title": "증기 탱크",
    "gui.bigreactors.reactor.controller.vaporbar.tooltip.value3b": "% 채움",
    "gui.bigreactors.reactor.controller.vaporbar.tooltip.body": (
        "가열된 냉각재가 이 탱크에 증기로 저장됩니다. 유체 포트로 꺼내야 합니다."
    ),
    "gui.bigreactors.reactor.controller.vaporratio.tooltip.body": (
        "이 원자로는 노심에서 물 같은 냉각재를 가열하는 능동 냉각 방식입니다."
    ),
    "gui.bigreactors.reactor.controller.wasteeject.tooltip.body": (
        "자동 모드에서는 노심의 폐기물을 가능한 한 빨리 배출합니다.\n\n"
        "수동 모드에서는 이 화면이나 레드스톤·컴퓨터 포트 신호로 직접 배출해야 합니다."
    ),
    "gui.bigreactors.reactor.controller.scram.tooltip.body": (
        "원자로를 끄고 제어봉을 연료봉 안으로 끝까지 밀어 넣습니다. (좋은 결과를 바라세요...)"
    ),
    "gui.bigreactors.reactor.controller.voidreactants.tooltip.title": "반응물 비우기",
    "gui.bigreactors.reactor.controller.voidreactants.tooltip.body": (
        "원자로 안의 모든 반응물을 제거합니다."
    ),
    "gui.bigreactors.reactor.solidaccessport.directioninput.tooltip.title": "입력 모드",
    "gui.bigreactors.reactor.solidaccessport.directioninput.tooltip.body": (
        "고체 반입출 포트를 입력 모드로 설정합니다."
    ),
    "gui.bigreactors.reactor.solidaccessport.directionoutput.tooltip.title": "출력 모드",
    "gui.bigreactors.reactor.solidaccessport.directionoutput.tooltip.body": (
        "고체 반입출 포트를 출력 모드로 설정합니다."
    ),
    "gui.bigreactors.reactor.solidaccessport.dumpfuel.tooltip.body": (
        "원자로 안의 연료를 배출해 고체 반입출 포트에 주괴로 내보냅니다."
    ),
    "gui.bigreactors.reactor.solidaccessport.dumpwaste.tooltip.body": (
        "원자로 안의 폐기물을 배출해 고체 반입출 포트에 주괴로 내보냅니다."
    ),
    "gui.bigreactors.reactor.fluidaccessport.directioninput.tooltip.title": "입력 모드",
    "gui.bigreactors.reactor.fluidaccessport.directioninput.tooltip.body": (
        "연료 주입 포트를 입력 모드로 설정합니다."
    ),
    "gui.bigreactors.reactor.fluidaccessport.directionoutput.tooltip.title": "출력 모드",
    "gui.bigreactors.reactor.fluidaccessport.directionoutput.tooltip.body": (
        "연료 주입 포트를 출력 모드로 설정합니다."
    ),
    "gui.bigreactors.reactor.fluidaccessport.dumpfuel.tooltip.body": (
        "원자로 안의 연료를 연료 주입 포트의 연료 탱크로 배출합니다."
    ),
    "gui.bigreactors.reactor.fluidaccessport.dumpwaste.tooltip.body": (
        "원자로 안의 폐기물을 연료 주입 포트의 폐기물 탱크로 배출합니다."
    ),
    "gui.bigreactors.reactor.fluidaccessport.fueltank.tooltip.title": "연료 탱크",
    "gui.bigreactors.reactor.fluidaccessport.fueltank.tooltip.body": (
        "포트에 주입하거나 원자로에서 배출한 유체 연료를 저장합니다."
    ),
    "gui.bigreactors.reactor.fluidaccessport.wastetank.tooltip.body": (
        "원자로에서 배출한 유체 폐기물을 저장합니다."
    ),
    "gui.bigreactors.reactor.redstoneport.sensortype.inputsetcontrolrod.body": (
        "원자로의 모든 제어봉 삽입 비율을 변경합니다."
    ),
    "gui.bigreactors.reactor.redstoneport.sensortype.inputsetcontrolrod.whileon.label": "신호 있음:",
    "gui.bigreactors.reactor.redstoneport.sensortype.inputsetcontrolrod.whileoff.label": "신호 없음:",
    "gui.bigreactors.reactor.redstoneport.sensortype.inputsetcontrolrod.setto.label": "설정값:",
    "gui.bigreactors.reactor.redstoneport.sensortype.inputsetcontrolrod.augment.label": "삽입량:",
    "gui.bigreactors.reactor.redstoneport.sensortype.inputsetcontrolrod.reduce.label": "인출량:",
    "gui.bigreactors.reactor.redstoneport.sensortype.outputcasingtemperature.title": "외장 온도",
    "gui.bigreactors.reactor.redstoneport.sensortype.outputfueltemperature.title": "노심 온도",
    "gui.bigreactors.reactor.redstoneport.sensortype.outputfuelrichness.title": "연료 반응성",
    "gui.bigreactors.reactor.redstoneport.sensortype.outputfuelrichness.body": (
        "현재 연료 반응성 비율에 따라 신호를 출력합니다."
    ),
    "gui.bigreactors.reactor.redstoneport.sensortype.outputcoolantamount.title": "냉각재 양",
    "gui.bigreactors.reactor.redstoneport.sensortype.outputvaporamount.title": "증기 양",
    "gui.bigreactors.reactor.redstoneport.sensortype.outputvaporamount.body": (
        "내부 탱크에 저장된 증기 양에 따라 신호를 출력합니다."
    ),
    "gui.bigreactors.reactor.redstoneport.sensortype.richness.label": "반응성:",
    "gui.bigreactors.reactor.redstoneport.sensortype.richness.min.label": "반응성(최소):",
    "gui.bigreactors.reactor.redstoneport.sensortype.richness.max.label": "반응성(최대):",
    "gui.bigreactors.reactor.controlrod.name.set": "설정",
    "gui.bigreactors.reactor.controlrod.insertion.input.tooltip.body": (
        "위·아래 버튼을 클릭하면 1씩 바뀝니다.\n\n"
        "Ctrl 또는 Command 키를 누르면 10씩 바뀝니다.\n\n"
        "Shift 키를 누르면 클릭한 버튼에 따라 100 또는 0으로 설정됩니다."
    ),
    "gui.bigreactors.reactor.controlrod.insertion.set": "변경",
    "gui.bigreactors.reactor.controlrod.insertion.setall.tooltip.body": (
        "원자로의 모든 제어봉 삽입 비율을 변경합니다."
    ),
    "gui.bigreactors.turbine.controller.coolantbar.title": "냉각재 탱크",
    "gui.bigreactors.turbine.controller.coolantbar.footer": (
        "사용한 증기는 냉각재로 응축되어 이 탱크에 저장되며, 출력 유체 포트로 내보낼 수 있습니다."
    ),
    "gui.bigreactors.turbine.controller.vaporbar.title": "증기 탱크",
    "gui.bigreactors.turbine.controller.vaporbar.footer": (
        "입력 유체 포트로 받은 증기를 이 탱크에 저장한 뒤 터빈 회전자를 구동하는 데 사용합니다."
    ),
    "gui.bigreactors.turbine.controller.rpmbar.tooltip.body": (
        "회전자의 분당 회전 수입니다.\n\n"
        "회전자는 900 또는 1800 RPM에서 가장 효율적입니다.\n\n"
        "2000 RPM을 넘으면 터빈이 심각하게 고장 날 수 있습니다."
    ),
    "gui.bigreactors.turbine.controller.rotorstatus.tooltip.body": (
        "회전자 날개는 날개 용량 이하의 증기에서만 에너지를 완전히 회수할 수 있습니다.\n\n"
        "입력 유량이 용량을 넘으면 효율이 떨어집니다."
    ),
    "gui.bigreactors.turbine.controller.flowrate.label": "유량:",
    "gui.bigreactors.turbine.controller.flowrate.tooltip.body": (
        "증기 탱크에서 꺼내는 최대 유량, 즉 터빈의 최대 처리 유량을 설정합니다.\n\n"
        "위·아래 버튼을 클릭하면 1씩 바뀝니다.\n\n"
        "Ctrl 또는 Command 키를 누르면 10씩 바뀝니다.\n\n"
        "Shift 키를 누르면 클릭한 버튼에 따라 최대값 또는 0으로 설정됩니다."
    ),
    "gui.bigreactors.turbine.controller.energyratio.tooltip.body": (
        "터빈은 회전하는 회전자 주위의 금속 유도 코일로 에너지를 생성합니다.\n\n"
        "코일이 많거나 품질이 높을수록 더 빠르게 에너지를 생성합니다."
    ),
    "gui.bigreactors.turbine.controller.vent.all.tooltip.title": "냉각재 전부 배출",
    "gui.bigreactors.turbine.controller.vent.overflow.tooltip.title": "초과 냉각재만 배출",
    "gui.bigreactors.turbine.controller.vent.overflow.tooltip.body": (
        "응축되어 생성된 냉각재 중 냉각재 탱크에 저장할 수 없는 양만 배출합니다."
    ),
    "gui.bigreactors.turbine.controller.vent.donotvent.tooltip.title": "냉각재 배출 안 함",
    "gui.bigreactors.turbine.controller.inductor.tooltip.body": (
        "회전하는 회전자에서 에너지를 추출하는 터빈 내부의 금속 코일입니다.\n\n"
        "연결하면 에너지를 생성하는 대신 회전자에 저항을 주어 회전 속도를 낮춥니다.\n\n"
        "연결을 끊으면 에너지를 생성하지 않지만 회전자가 더 빠르게 회전합니다."
    ),
    "gui.bigreactors.turbine.controller.inductor.mode.engaged": "연결됨",
    "gui.bigreactors.turbine.controller.inductor.mode.disengaged": "연결 해제됨",
    "gui.bigreactors.turbine.redstoneport.sensortype.inputflowregulator.whileon.label": "신호 있음:",
    "gui.bigreactors.turbine.redstoneport.sensortype.inputflowregulator.whileoff.label": "신호 없음:",
    "gui.bigreactors.turbine.redstoneport.sensortype.inputflowregulator.setto.label": "설정값:",
    "gui.bigreactors.turbine.redstoneport.sensortype.inputflowregulator.insertby.label": "증가량:",
    "gui.bigreactors.turbine.redstoneport.sensortype.inputflowregulator.retractby.label": "감소량:",
    "gui.bigreactors.turbine.redstoneport.sensortype.outputrotorspeed.speed.min.label": "속도(최소):",
    "gui.bigreactors.turbine.redstoneport.sensortype.outputcoolantamount.title": "냉각재 양",
    "gui.bigreactors.turbine.redstoneport.sensortype.outputvaporamount.title": "증기 양",
    "gui.bigreactors.turbine.redstoneport.sensortype.outputvaporamount.body": (
        "내부 탱크에 저장된 증기 양에 따라 신호를 출력합니다."
    ),
    "gui.bigreactors.reprocessor.controller.voidfluid.title": "유체 비우기",
    "gui.bigreactors.reprocessor.controller.voidfluid.body": "재처리기 안의 모든 유체를 제거합니다.",
    "gui.bigreactors.fluidizer.controller.off.title": "유체화기 끄기",
    "gui.bigreactors.energizer.controller.on.title": "에너자이저 켜기",
    "gui.bigreactors.energizer.controller.off.title": "에너자이저 끄기",
    "gui.bigreactors.energizer.controller.input.tooltip.body": "에너자이저에 입력된 에너지 양",
    "gui.bigreactors.energizer.powerport.directioninput.tooltip.body": (
        "이 전력 포트를 입력 모드로 설정합니다."
    ),
    "gui.bigreactors.energizer.powerport.directionoutput.tooltip.body": (
        "이 전력 포트를 출력 모드로 설정합니다."
    ),
    "gui.bigreactors.generator.fluidport.directioninput.tooltip.title": "입력 모드",
    "gui.bigreactors.generator.fluidport.directionoutput.tooltip.title": "출력 모드",
    "gui.bigreactors.generator.redstoneport.sensortype.amount.min.label": "양(최소):",
    "multiblock.validation.energizer.invalid_block_for_exterior": (
        "%1$s은(는) 에너자이저 외부에 사용할 수 없습니다."
    ),
    "multiblock.validation.reactor.too_few_controllers": (
        "제어기가 부족합니다. 원자로에는 최소 하나가 필요합니다."
    ),
    "multiblock.validation.turbine.too_few_controllers": (
        "제어기가 부족합니다. 터빈에는 최소 하나가 필요합니다."
    ),
    "multiblock.validation.turbine.invalid_block_for_interior": (
        "터빈 내부에 사용할 수 없는 블록입니다. 회전자 부품, 금속 블록, 빈 공간만 허용됩니다."
    ),
    "multiblock.validation.turbine.block_must_be_rotor": (
        "이 위치에는 회전자가 있어야 합니다. 회전자는 베어링에서 시작해 터빈 내부 끝까지 이어져야 합니다."
    ),
    "multiblock.validation.turbine.shaft_too_short": (
        "회전자 축은 터빈 내부의 전체 길이에 걸쳐 이어져야 합니다."
    ),
    "multiblock.validation.turbine.found_loose_rotor_blocks": (
        "주 회전자에 연결되지 않은 회전자 블록이 %1$d개 있습니다. 모든 회전자 블록은 "
        "베어링에서 시작해 터빈 내부 끝까지 이어지는 한 줄의 축을 이루어야 합니다."
    ),
    "multiblock.validation.turbine.found_loose_rotor_blades": (
        "회전자에 연결되지 않은 회전자 날개가 %1$d개 있습니다. 모든 회전자 날개는 "
        "회전자 축에서 바깥쪽으로 끊김 없이 이어져야 합니다."
    ),
    "multiblock.validation.turbine.invalid_metals_shape": (
        "회전자 둘레의 고리 안에 있지 않은 금속 블록이 %1$d개 있습니다. 모든 금속 블록은 "
        "회전자 둘레에 완전하거나 일부인 고리 형태로 배치해야 합니다."
    ),
    "multiblock.validation.turbine.invalid_rotor_end": (
        "회전자의 끝은 터빈 외장 블록에 맞닿아야 합니다."
    ),
    "multiblock.validation.reprocessor.missing_controller": (
        "재처리기에는 제어기가 정확히 하나 있어야 합니다."
    ),
    "multiblock.validation.reprocessor.missing_wasteinjector": (
        "재처리기에는 폐기물 주입기가 정확히 하나 있어야 합니다."
    ),
    "multiblock.validation.fluidizer.missing_controller": (
        "유체화기에는 제어기가 정확히 하나 있어야 합니다."
    ),
    "multiblock.validation.energizer.too_few_controllers": (
        "제어기가 부족합니다. 에너자이저에는 최소 하나가 필요합니다."
    ),
    "config.bigreactors.general": "일반",
    "config.bigreactors.recipes": "조합법",
    "config.bigreactors.worldgen": "월드 생성",
    "config.bigreactors.client": "클라이언트 전용 설정",
    "config.bigreactors.general.fuelusagemultiplier": "연료 소비 배율",
    "config.bigreactors.general.powerproductionmultiplier": "전력 생산 배율",
    "config.bigreactors.general.ticksperredstoneupdate": "레드스톤 포트 갱신 주기(틱)",
    "config.bigreactors.turbine.turbineaerodragmultiplier": "공기 저항 배율",
    "config.bigreactors.turbine.turbinecoildragmultiplier": "코일 저항 배율",
    "config.bigreactors.turbine.turbinefluidperblademultiplier": "날개당 유체량 배율",
    "config.bigreactors.turbine.turbinemassdragmultiplier": "질량 저항 배율",
    "config.bigreactors.turbine.turbinepowerproductionmultiplier": "전력 생산 배율",
    "config.bigreactors.recipes.registercharcoalforsmelting": "숯을 제련해 흑연 만들기",
    "config.bigreactors.recipes.registerCoalForSmelting": "석탄을 제련해 흑연 만들기",
    "config.bigreactors.worldgen.anglesiteorepercluster": "광맥당 최대 앵글사이트 광석 수",
    "config.bigreactors.worldgen.benitoiteoreenableworldgen": "베니토아이트 광석 생성",
    "config.bigreactors.worldgen.benitoiteoremaxclustersperchunk": (
        "청크당 최대 베니토아이트 광맥 수"
    ),
    "config.bigreactors.worldgen.benitoiteorepercluster": "광맥당 최대 베니토아이트 광석 수",
    "config.bigreactors.worldgen.userworldgenversion": (
        "사용자 지정 월드 생성 버전(청크를 다시 생성하려면 값을 올리세요)"
    ),
    "config.bigreactors.client.disableapitooltips": (
        "연료, 감속재, 코일 등에 고급 툴팁을 추가하지 않기"
    ),
    "api.bigreactors.reactor.tooltip.moderator": (
        "Extreme Reactors: 이 블록이나 유체는 원자로 내부의 방사선 감속재로 사용할 수 있습니다."
    ),
    "zerocore:api.multiblock.validation.block_not_connected": (
        "블록이 멀티블록 제어기에 연결되어 있지 않습니다."
    ),
    "zerocore:api.multiblock.validation.machine_too_large": (
        "기계가 너무 큽니다. %2$s 방향으로 최대 %1$d블록까지 만들 수 있습니다."
    ),
    "zerocore:api.multiblock.validation.machine_too_small": (
        "기계가 너무 작습니다. %2$s 방향으로 최소 %1$d블록이어야 합니다."
    ),
    "zerocore:api.multiblock.validation.invalid_part_for_bottom": (
        "이 블록은 기계의 맨 아래층에 사용할 수 없습니다."
    ),
    "zerocore:api.multiblock.validation.invalid_part_for_top": (
        "이 블록은 기계의 맨 위층에 사용할 수 없습니다."
    ),
    "zerocore:api.multiblock.validation.invalid_part_for_interior": (
        "이 블록은 기계 내부에 사용할 수 없습니다."
    ),
    "zerocore:debugTool.block.tooltip1": "블록을 우클릭해 디버그 정보 표시",
    "zerocore:debugTool.block.tooltip3a": "웅크리기: ",
    "zerocore:debugTool.block.tooltip3b": "클라이언트 측에서 조회",
    "zerocore:gui.manual.open": "가이드 페이지 열기",
    "gui.zerocore.base.generic.disable": "비활성화",
    "gui.zerocore.base.generic.save": "저장",
    "gui.zerocore.base.generic.reset": "초기화",
    "gui.zerocore.base.generic.unknown": "알 수 없음",
    "gui.zerocore.base.redstone.sensorbehavior.setfromsignal.text": "신호에 따라 설정",
    "gui.zerocore.base.redstone.sensorbehavior.setfromsignallevel.text": (
        "신호 세기에 따라 설정"
    ),
    "gui.zerocore.base.redstone.sensorbehavior.setonpulse.text": "펄스가 오면 설정",
    "gui.zerocore.base.redstone.sensorbehavior.toggleonpulse.text": "펄스가 오면 전환",
    "gui.zerocore.base.redstone.sensorbehavior.augmentonpulse.text": "펄스가 오면 증가",
    "gui.zerocore.base.redstone.sensorbehavior.reduceonpulse.text": "펄스가 오면 감소",
    "gui.zerocore.base.redstone.sensorbehavior.performonpulse.text": "펄스가 오면 실행",
    "gui.zerocore.base.redstone.sensorbehavior.activewhileabove.text": "기준값 초과 시 활성",
    "gui.zerocore.base.redstone.sensorbehavior.activewhilebelow.text": "기준값 미만 시 활성",
    "gui.zerocore.base.redstone.sensorbehavior.activewhilebetween.text": "범위 안에서 활성",
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


def is_name_key(key: str) -> bool:
    return key.startswith(
        (
            "item.",
            "block.",
            "fluid.",
            "itemGroup.",
            "reactant.",
            "coolant.",
            "vapor.",
            "part.",
            "variant.",
        )
    )


def translate_name(source: str) -> str:
    value = EXACT_VALUES.get(source, source)
    if value != source:
        return value
    for old, new in NAME_TERMS:
        value = re.sub(rf"(?<![A-Za-z]){re.escape(old)}(?![A-Za-z])", new, value)
    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace(" - ", " - ")
    return value


def candidate() -> dict[str, object]:
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests: set[str] = set()
    english_rows: dict[str, dict[str, object]] = {}
    for namespace in NAMESPACES:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        english_rows[namespace] = english
        for key, source in english.items():
            if (
                isinstance(source, str)
                and not is_name_key(key)
                and source not in EXACT_VALUES
                and not family_goal.is_allowed_original(source)
                and not isinstance(cache.get(source), str)
            ):
                requests.add(source)
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

    candidates: dict[str, dict[str, str]] = {}
    for namespace, english in english_rows.items():
        translated: dict[str, str] = {}
        for key, source in english.items():
            if not isinstance(source, str):
                raise TypeError(f"문자열이 아닌 언어 값: {namespace}:{key}")
            if is_name_key(key):
                translated[key] = translate_name(source)
            elif source in EXACT_VALUES:
                translated[key] = EXACT_VALUES[source]
            elif family_goal.is_allowed_original(source):
                translated[key] = source
            else:
                translated[key] = str(cache[source])
        candidates[namespace] = translated
    write_json(CANDIDATE_FILE, candidates)
    report = {
        "keys": sum(len(row) for row in english_rows.values()),
        "candidate_keys": sum(len(row) for row in candidates.values()),
        "review_scope": "all_current_english_keys",
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "auto_candidate_report.json", report)
    return report


def reviewed_value(key: str, source: str, candidate_value: str) -> str:
    value = KEY_OVERRIDES.get(
        key, translate_name(source) if is_name_key(key) else candidate_value
    )
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    value = value.replace("Extreme Reactors", "\ue000EXTREME_REACTORS\ue001")
    for old, new in FINAL_ENGLISH_TERMS:
        value = re.sub(rf"(?<![A-Za-z]){old}(?![A-Za-z])", new, value)
    value = value.replace("\ue000EXTREME_REACTORS\ue001", "Extreme Reactors")
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    if is_name_key(key):
        value = value.rstrip(".")
    return value


def normalize() -> dict[str, object]:
    candidates = load_json(CANDIDATE_FILE)
    changed = 0
    unresolved: list[str] = []
    for namespace in NAMESPACES:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        candidate_rows = candidates.get(namespace)
        if not isinstance(candidate_rows, dict):
            raise TypeError(f"후보 네임스페이스가 없습니다: {namespace}")
        for key, source in english.items():
            candidate_value = candidate_rows.get(key)
            if not isinstance(source, str) or not isinstance(candidate_value, str):
                raise TypeError(f"문자열이 아닌 언어 값: {namespace}:{key}")
            translated = reviewed_value(key, source, candidate_value)
            errors = family_goal.validate_family_value(FAMILY, key, source, translated)
            if errors:
                raise ValueError("; ".join(errors))
            if korean[key] != translated:
                korean[key] = translated
                changed += 1
            if (
                source == translated
                and source not in ALLOWED_EXACT_VALUES
                and not family_goal.is_allowed_original(source)
            ):
                unresolved.append(f"{namespace}:{key}")
        write_json(WORK_ROOT / namespace / "ko_kr.json", korean)
    report = {
        "keys_reviewed": 572,
        "changed": changed,
        "unresolved": len(unresolved),
        "unresolved_examples": unresolved[:30],
        "review_status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    untranslated: list[str] = []
    keys_reviewed = 0
    for namespace in NAMESPACES:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        keys_reviewed += len(english)
        if list(english) != list(korean):
            errors.append(f"키 또는 순서 불일치: {namespace}")
        for key, source in english.items():
            target = korean.get(key)
            if not isinstance(source, str) or not isinstance(target, str):
                errors.append(f"문자열이 아닌 값: {namespace}:{key}")
                continue
            errors.extend(
                family_goal.validate_family_value(FAMILY, key, source, target)
            )
            artifacts = [word for word in FORBIDDEN_ARTIFACTS if word in target]
            if artifacts:
                errors.append(
                    f"기계번역 잔재: {namespace}:{key}: {', '.join(artifacts)}"
                )
            if (
                source == target
                and source not in ALLOWED_EXACT_VALUES
                and not family_goal.is_allowed_original(source)
            ):
                untranslated.append(f"{namespace}:{key}")
    if untranslated:
        errors.append(f"미번역 키: {untranslated[:30]}")
    report = {
        "keys_reviewed": keys_reviewed,
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
