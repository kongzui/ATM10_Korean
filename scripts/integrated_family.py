#!/usr/bin/env python3
"""Integrated Dynamics 계열의 원문·후보·표시 경로를 준비한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/integrated_dynamics"
CACHE_PATH = PROJECT_ROOT / "temp/integrated_family_auto_candidates.json"
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"
QUEST_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
GOOGLE_TRANSLATE = "https://translate.googleapis.com/translate_a/single"

FAMILY_ARCHIVES = {
    "integratedcrafting": "integratedcrafting-*.jar",
    "integrateddynamics": "integrateddynamics-*.jar",
    "integratedscripting": "integratedscripting-*.jar",
    "integratedterminals": "integratedterminals-*.jar",
    "integratedtunnels": "integratedtunnels-*.jar",
}
ARCHIVE_NAMESPACES = {
    "integratedcrafting": ("integratedcrafting",),
    "integrateddynamics": ("integrateddynamics", "integrateddynamicscompat"),
    "integratedscripting": ("integratedscripting",),
    "integratedterminals": ("integratedterminals", "integratedterminalscompat"),
    "integratedtunnels": ("integratedtunnels",),
}
TARGET_NAMESPACES = {
    namespace for namespaces in ARCHIVE_NAMESPACES.values() for namespace in namespaces
}
PROTECTED = re.compile(
    r"%(?:\d+\$)?[a-zA-Z%]"
    r"|\{[A-Za-z0-9_]+\}"
    r"|[&§][0-9A-FK-ORa-fk-or]"
    r"|https?://\S+"
    r"|\b(?:FE|RF|EU|NBT|GUI|ID|TPS|IDE|JEI|ECMAScript|JavaScript|Node\.js)\b"
)
CACHE_RULES_VERSION = 2
CACHE_REFRESH = re.compile(r"\b(?:let|const|function|require|fs)\b", re.IGNORECASE)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[&§][0-9A-FK-ORa-fk-or]")

SOURCE_OVERRIDES = {
    "Integrated Crafting": "Integrated Crafting",
    "Integrated Dynamics": "Integrated Dynamics",
    "Integrated Scripting": "Integrated Scripting",
    "Integrated Terminals": "Integrated Terminals",
    "Integrated Tunnels": "Integrated Tunnels",
    "Any": "모든 유형",
    "Number": "숫자",
    "Named": "이름 있음",
    "Uniquely Named": "고유 이름 있음",
    "Boolean": "불리언",
    "Integer": "정수",
    "Double": "실수",
    "Long": "긴 정수",
    "String": "문자열",
    "Operator": "연산자",
    "NBT": "NBT",
    "List": "목록",
    "Block": "블록",
    "Item": "아이템",
    "Entity": "엔티티",
    "Fluid": "유체",
    "Ingredients": "재료",
    "Recipe": "제작법",
    "And": "AND",
    "Or": "OR",
    "Not": "NOT",
    "Nand": "NAND",
    "Nor": "NOR",
    "Xor": "XOR",
    "Square Root": "제곱근",
    "Power": "거듭제곱",
    "Intersection": "교집합",
    "Data Keys": "데이터 키",
    "Data Value": "데이터 값",
    "With Data": "데이터 포함",
    "Light level": "밝기",
    "Temperature": "온도",
    "Tooltip": "툴팁",
    "Bucket": "양동이",
    "Clear": "지우기",
    "Actions": "작업",
    "Logging": "로깅",
    "Functions": "함수",
    "Global functions": "전역 함수",
    "Object methods": "객체 메서드",
    "Graal Function": "Graal 함수",
    "Keep": "유지",
    "Member: §r§o%s": "멤버: §r§o%s",
    "Sneak": "웅크리기",
    "Part": "부품",
    "Parts": "부품",
    "Reader": "판독기",
    "Readers": "판독기",
    "Writer": "작성기",
    "Writers": "작성기",
    "Aspects": "애스펙트",
    "Value Type": "자료형",
    "Value Types": "자료형",
    "Logic Cable": "논리 케이블",
    "Ticks/Operation": "틱/작업",
    "Proxy": "프록시",
    "Fluid vaporize sound": "유체 기화 소리",
    "Bucket empty sound": "양동이 비우기 소리",
    "Bucket fill sound": "양동이 채우기 소리",
    "Fluid By Name": "이름으로 유체 찾기",
    "Network Count Of Item": "네트워크의 아이템 수",
    "Network Count Of Fluid": "네트워크의 유체량",
}

KEY_OVERRIDES = {
    "general.integratedcrafting.description": (
        "Integrated Dynamics 네트워크에서 자동 제작을 합니다."
    ),
    "advancement.integratedcrafting.craft_crafting_interface_attuned.desc": (
        "동조된 제작 인터페이스를 제작하세요"
    ),
    "parttype.integratedcrafting.interface_crafting.info": (
        "대상 기계에서 제작할 제작법 변수를 보관합니다."
    ),
    "parttype.integratedcrafting.interface_crafting_attuned.info": (
        "대상 기계가 제공하는 모든 제작법을 처리합니다."
    ),
    "aspect.integratedcrafting.read.list.network.recipes.info": (
        "사용 가능한 모든 제작법의 목록입니다."
    ),
    "aspect.integratedcrafting.read.list.network.craftingjobs.info": (
        "실행 중인 모든 제작 작업을 제작법 목록으로 표시합니다."
    ),
    "aspect.integratedcrafting.read.list.network.craftingingredients.info": (
        "현재 제작 중인 모든 재료의 목록입니다."
    ),
    "aspect.integratedcrafting.write.recipe.craft": "제작법 실행",
    "aspect.integratedcrafting.write.integer.craft": "에너지 제작",
    "info_book.integratedcrafting.introduction.text4": (
        "다음 절에서는 이 자동 제작 과정이 어떻게 작동하는지 설명합니다."
    ),
    "info_book.integratedcrafting.crafting_interface.basics.text2": (
        "&l제작 인터페이스&r가 기계 &o(제작대나 화로 등)&r를 바라보게 놓으면, "
        "해당 기계에 연결되어 제작법을 처리합니다."
    ),
    "info_book.integratedcrafting.crafting_interface.basics.text3": (
        "&l제작 인터페이스&r GUI에 &8제작법&0이 담긴 &l변수 카드&r를 넣으면, 연결된 "
        "기계에서 그 제작법을 처리할 수 있다고 네트워크에 알립니다."
    ),
    "info_book.integratedcrafting.crafting_interface.crafting.text1": (
        "이 절에서는 &l제작 인터페이스&r가 제작 과정을 처리하는 방식을 설명합니다. 모드를 "
        "제대로 활용하고 발생한 문제를 진단하는 데 꼭 필요한 내용입니다."
    ),
    "info_book.integratedcrafting.crafting_interface.crafting.text4": (
        "다음 그림은 제작대와 화로로 자동 제작할 때 필요한 최소 구성의 예입니다."
    ),
    "info_book.integratedcrafting.crafting_interface.configuration.text1": (
        "대부분의 &lIntegrated Dynamics&r 부품처럼 &l제작 인터페이스&r에서도 채널, "
        "우선순위, 작동 간격 등의 설정을 바꿀 수 있습니다."
    ),
    "info_book.integratedcrafting.crafting_interface.recipe_feedback.text1": (
        "&l제작 인터페이스&r에 &l변수 카드&r를 넣으면 제작법이 연결된 기계에서 유효한지 "
        "&2초록색 확인 표시&0 또는 &4빨간 X 표시&0로 알려 줍니다. 표시 위에 마우스를 "
        "올리면 자세한 내용을 볼 수 있습니다."
    ),
    "info_book.integratedcrafting.crafting_interface.recipe_feedback.text2": (
        "예를 들어 상자 제작법을 화로에 연결된 &l제작 인터페이스&r에 잘못 넣었을 때 즉시 "
        "알려 주는 사전 확인 기능입니다."
    ),
    "info_book.integratedcrafting.crafting_interface.debugging_jobs.text2": (
        "&l네트워크 판독기&r의 제작 관련 애스펙트로 네트워크에서 사용 가능한 제작법, "
        "실행 중인 제작 작업, 부족한 제작 재료의 목록을 읽어 문제를 진단할 수 있습니다. "
        "이 목록을 &l디스플레이 패널&r에 표시하면 원인을 찾는 데 도움이 됩니다."
    ),
    "info_book.integratedcrafting.crafting_writer.text2": (
        "다음 애스펙트로 지정한 제작법, 출력 아이템, 출력 유체 또는 출력 에너지의 제작 "
        "작업을 시작할 수 있습니다. 애스펙트 설정에서는 제작 채널, 실행 중인 작업이 새 "
        "작업을 막을지, 부족한 입력 재료도 제작할지, 저장소에 재료가 있으면 새 작업을 "
        "막을지를 정할 수 있습니다."
    ),
    "info_book.integratedcrafting.crafting_writer.text3": (
        "&l변수 카드&r로 &o아무것도&r 제작하지 않게 하려면 빈 값을 넣으세요. 예를 들어 "
        "실제 아이템을 지정하지 않은 &8아이템&0 자료형의 &l변수 카드&r를 넣으면 됩니다."
    ),
    "info_book.integratedcrafting.crafting_writer.text4": (
        "&lIntegrated Terminals&r이 설치되어 있으면 &l저장 터미널&r에서 제작 작업을 "
        "화면으로 직접 시작할 수 있습니다."
    ),
    "info_book.integratedcrafting.tutorials.autocrafting_trigger.text5": (
        "올바르게 구성했다면 참나무 원목 하나가 참나무 판자 4개로 바뀝니다. 판자를 "
        "꺼냈을 때 다른 원목이 남아 있으면 판자 4개를 다시 제작합니다. &l제작 작성기&r의 "
        "애스펙트 설정을 조정해 저장소 내용물을 무시하고 가능한 만큼 계속 제작하게 할 "
        "수도 있습니다."
    ),
    "info_book.integratedcrafting.tutorials.autocrafting_trigger.text6": (
        "이 절 마지막의 그림은 튜토리얼 완료에 필요한 구성 요소의 예입니다."
    ),
    "general.integratedterminals.description": (
        "Integrated Dynamics 네트워크를 살펴보고 관리하는 터미널입니다."
    ),
    "gui.integratedterminals.amount": "수량",
    "gui.integratedterminals.terminal_storage.to_craft": "제작 예정: %s",
    "gui.integratedterminals.terminal_storage.missing": "부족: %s",
    "gui.integratedterminals.terminal_storage.craftinggrid.autorefill": (
        "제작 격자 자동 채우기"
    ),
    "gui.integratedterminals.terminal_storage.craftinggrid.autorefill.type.storage": (
        "§a공급원: 네트워크"
    ),
    "gui.integratedterminals.terminal_storage.craftinggrid.autorefill.type.player": (
        "§a공급원: 플레이어"
    ),
    "gui.integratedterminals.terminal_storage.craftinggrid.autorefill.type.storage_player": (
        "§a공급원: 네트워크, 플레이어"
    ),
    "gui.integratedterminals.terminal_storage.craftinggrid.autorefill.type.player_storage": (
        "§a공급원: 플레이어, 네트워크"
    ),
    "gui.integratedterminals.terminal_storage.scale.info": (
        "저장소 격자의 크기를 설정합니다."
    ),
    "gui.integratedterminals.terminal_storage.scale.scalexy": ("§a높이/너비 자동 조절"),
    "gui.integratedterminals.terminal_storage.scale.scaley": "§a높이 자동 조절",
    "gui.integratedterminals.terminal_storage.scale.scalex": "§a너비 자동 조절",
    "gui.integratedterminals.terminal_storage.scale.medium": "§a중형",
    "gui.integratedterminals.terminal_crafting_job.craftingplan.empty": (
        "비어 있는 제작 작업"
    ),
    "gui.integratedterminals.craftingplan.status.invalid.desc": "저장소 재료 부족",
    "gui.integratedterminals.craftingplan.status.pending_inputs.desc": "입력 재료 부족",
    "gui.integratedterminals.craftingplan.status.finished": "완료",
    "key.integratedterminals.terminal.portable.open": (
        "첫 번째 휴대용 저장 터미널 열기"
    ),
    "advancement.integratedterminals.menril_glass": "빛을 밝히는 유리",
    "parttype.integratedterminals.terminal_crafting_job.tooltip.nohandlers": (
        "주의: 사용할 수 있는 제작 처리기가 없습니다. Integrated Crafting 같은 다른 "
        "모드를 설치하면 사용할 수 있습니다."
    ),
    "info_book.integratedterminals.introduction.text2": (
        "예를 들어 &l저장 터미널&r에서는 연결된 &o에너지 배터리&r 같은 &o저장 "
        "네트워크&r를 살펴보고 조작할 수 있습니다. &lIntegrated Tunnels&r의 &o아이템&r·"
        "&o유체&r 저장 기능처럼 다른 모드가 추가한 저장 기능도 함께 사용할 수 있습니다."
    ),
    "info_book.integratedterminals.storage_terminal.introduction.text1": (
        "&l저장 터미널&r은 &l케이블&r에 설치하여 연결된 네트워크의 저장소를 GUI로 "
        "관리하는 부품입니다."
    ),
    "info_book.integratedterminals.storage_terminal.usage.text1": (
        "&l저장 터미널&r에는 현재 네트워크에 연결된 모든 &o저장 네트워크&r가 탭으로 "
        "표시되며, 필요하면 채널별로 나뉩니다. 예를 들어 &o에너지 배터리&r가 여러 개면 "
        "에너지 탭에 전체 에너지 합계가 표시됩니다. &lIntegrated Tunnels&r의 &o아이템&r·"
        "&o유체&r 저장 기능처럼 다른 모드가 추가한 저장 기능도 조작할 수 있습니다. 각 탭 "
        "아래에는 현재 수량과 최대 수량이 표시됩니다. 이 가이드에서는 아이템, 유체, "
        "에너지처럼 저장할 수 있는 &o대상&r을 모두 &l재료&r라고 부릅니다."
    ),
    "info_book.integratedterminals.storage_terminal.usage.text2": (
        "재료는 보기만 하는 것이 아니라 직접 옮길 수도 있습니다. 일반 인벤토리처럼 "
        "클릭하여 집고 다시 클릭하여 놓으세요. 에너지와 유체는 인벤토리에서 배터리나 "
        "탱크 같은 용기 아이템을 클릭해야 합니다. Shift+클릭하면 한꺼번에 옮깁니다."
    ),
    "info_book.integratedterminals.storage_terminal.usage.text3": (
        "저장소 재료를 든 상태에서 해당 슬롯을 다시 클릭하면 수량이 조금 늘고, "
        "Shift+클릭하면 많이 늘어납니다. 우클릭하면 같은 방식으로 수량을 줄입니다. "
        "저장소 재료 위에서 마우스 휠을 굴려도 같은 조작을 할 수 있습니다."
    ),
    "info_book.integratedterminals.storage_terminal.usage.text4": (
        "저장소 재료를 든 상태에서 우클릭하면 적은 수량을, 좌클릭하면 든 수량 전부를, "
        "가운데 클릭하면 절반을 옮깁니다."
    ),
    "info_book.integratedterminals.storage_terminal.usage.text6": (
        "검색 상자에서 이름으로 표시할 재료를 걸러낼 수 있습니다. 공백으로 구분한 조건을 "
        "더 입력하면 결과를 세부적으로 검색할 수 있고, &oor&r 조건은 '|'로 구분합니다."
    ),
    "info_book.integratedterminals.storage_terminal.usage.text7": (
        "접두사로 검색 대상을 바꿀 수 있습니다. 기본값은 재료 이름이며, 문자열 앞에 "
        "&o'@'&r를 붙이면 모드, &o'#'&r을 붙이면 툴팁, &o'$'&r을 붙이면 아이템 "
        "태그를 검색합니다. 예를 들어 &o'$plank @minecraft'&r는 Minecraft가 추가한 모든 "
        "판자를 표시합니다."
    ),
    "info_book.integratedterminals.storage_terminal.usage.text8": (
        "아이템 저장 네트워크가 있으면 제작 탭도 추가됩니다. 아이템 탭에 제작 격자가 "
        "통합된 형태이며, 격자 내용물을 인벤토리나 네트워크로 보내기, 재료 균등 분배, "
        "제작 후 자동 채우기 설정 같은 편의 기능을 제공합니다."
    ),
    "info_book.integratedterminals.storage_terminal.autocrafting.text3": (
        "사용 가능한 모든 제작법은 해당 탭과 채널에 표시됩니다. 제작법을 클릭해 실행 "
        "횟수를 정하면 필요한 재료와 부족한 재료가 담긴 제작 계획이 표시되고, 확인하면 "
        "작업이 시작됩니다. 실행 중인 모든 작업은 &l제작 작업 터미널&r에서 볼 수 있습니다."
    ),
    "info_book.integratedterminals.storage_terminal.power_usage.text1": (
        "숙련된 사용자는 반복 클릭을 줄여 시간을 아낄 수 있습니다. &l저장 터미널&r에는 "
        "검색창 선택, 탭 이동, 제작 격자 비우기, 제작 격자 재료 균등 분배 같은 작업을 "
        "빠르게 하는 &o단축키&r가 있습니다. 단축키 목록은 이 절 마지막에 나옵니다."
    ),
    "info_book.integratedterminals.storage_terminal.power_usage.text2": (
        "JEI가 설치되어 있으면 제작법 Shift+클릭으로 제작 격자를 빠르게 채울 수 있습니다. "
        "자동 채우기 모드에서 선택한 공급원이 아이템을 가져올 위치를 결정합니다. JEI와 "
        "&l저장 터미널&r의 검색창을 서로 동기화할 수도 있습니다."
    ),
    "info_book.integratedterminals.storage_terminal.portable.text2": (
        "&l휴대용 저장 터미널&r을 특정 네트워크에 연결하려면 그 네트워크에 &l전방향 "
        "커넥터&r가 있어야 합니다. &l휴대용 저장 터미널&r을 들고 &l전방향 커넥터&r를 "
        "우클릭하면 연결됩니다."
    ),
    "info_book.integratedterminals.tutorials.introduction.text1": (
        "이 절에는 &lIntegrated Dynamics&r 네트워크를 살펴보고 관리하는 "
        "&lIntegrated Dynamics&r 애드온인 &lIntegrated Terminals&r의 사용법을 배우는 "
        "튜토리얼이 있습니다."
    ),
    "info_book.integratedterminals.tutorials.storage_terminal.text1": (
        "&l저장 터미널&r은 연결된 네트워크의 저장 내용물을 보여 주고 직접 조작하게 "
        "합니다. 재료 유형은 탭별로 나뉘며, 각 탭은 채널·검색어·&l변수 카드&r로 "
        "필터링하고 여러 기준으로 정렬할 수 있습니다. 자세한 내용은 가이드를 참고하세요."
    ),
    "info_book.integratedterminals.tutorials.storage_terminal_filtering.text1": (
        "&l저장 터미널&r의 유용한 기능 중 하나는 재료 &o필터링&r입니다. 이 튜토리얼에서는 "
        "텍스트 기반과 변수 기반의 두 가지 방식을 다룹니다. 발전 과제는 두 번째 방식으로만 "
        "달성합니다. 저장소는 Integrated Tunnels의 아이템 인터페이스로 연결합니다."
    ),
    "info_book.integratedterminals.tutorials.storage_terminal_filtering.text3": (
        "두 번째 단계에서는 &l저장 터미널&r GUI 오른쪽 아래의 &l변수&r 슬롯으로 "
        "필터링합니다. &lIntegrated Dynamics 논리 프로그래머&r에서 재료 유형을 입력받고 "
        "표시 여부를 &9불리언&0으로 출력하는 &l술어&r를 만든 뒤 &l변수&r에 저장하세요. 이 "
        "튜토리얼에서는 &o마법 부여 가능&r한 아이템을 모두 걸러냅니다. &l논리 "
        '프로그래머&r에서 &l술어&r 자료형의 &o"Item Enchantable"&r을 찾아 &l변수&r에 '
        "작성하고, &l저장 터미널&r의 아이템 탭에서 &l변수&r를 &l변수&r 슬롯에 넣으세요."
    ),
    "advancement.integratedscripting.terminal_open.desc": (
        "스크립팅 터미널 GUI를 여세요."
    ),
    "advancement.integratedscripting.terminal_display.desc": (
        "디스플레이 패널에 스크립트 값을 표시하세요"
    ),
    "operator.integratedscripting.integratedscript.basename": "통합 스크립트 %s",
    "item.integratedscripting.scripting_disk.id": "ID: %s",
    "item.integratedscripting.scripting_disk.bytes": "바이트: %s",
    "info_book.integratedscripting.introduction.text1": (
        "&lIntegrated Scripting&r은 &lIntegrated Dynamics&r 네트워크에서 복잡한 작업을 "
        "스크립트로 처리하게 하는 &lIntegrated Dynamics&r 애드온입니다. 기본적으로 "
        "JavaScript 스크립트 언어를 지원합니다."
    ),
    "info_book.integratedscripting.introduction.text2": (
        "복잡한 연산을 여러 변수 카드로 시각적으로 잇는 대신 편리한 스크립트 문법으로 "
        "&lIntegrated Dynamics&r 논리 연산을 정의할 수 있습니다."
    ),
    "info_book.integratedscripting.introduction.text3": (
        '예를 들어 &o"내구도가 있고 X 모드가 추가했으며 다이아몬드 곡괭이로만 캘 수 있는 '
        '블록에 해당하는 아이템"&r 같은 복잡한 목록 필터나, &o"이 목록에서 스택 크기가 '
        '두 번째로 큰 아이템 가져오기"&r를 쉽게 정의할 수 있습니다.'
    ),
    "info_book.integratedscripting.introduction.text4": (
        "이 모드를 사용하려면 기본 프로그래밍 지식을 익히는 것이 좋지만, 뒤쪽의 "
        "튜토리얼을 따라가며 배울 수도 있습니다."
    ),
    "info_book.integratedscripting.materials.text1": (
        "스크립팅을 시작하려면 &l멘데사이트&r 블록이 필요합니다. 가공하기 쉬워 스크립트를 "
        "저장하고 처리하는 재료로 알맞습니다. &l건조대&r에서 &l멘릴 수지&r와 &l안산암&r을 "
        "결합하면 &l멘데사이트&r를 만들 수 있습니다."
    ),
    "info_book.integratedscripting.concepts.text1": (
        "네트워크에서 스크립트를 편집·저장·제공하려면 &l스크립팅 터미널&r, &l스크립팅 "
        "디스크&r, &l스크립팅 드라이브&r의 세 요소가 필요합니다."
    ),
    "info_book.integratedscripting.concepts.text2": (
        "&l스크립팅 디스크&r는 스크립트 원문을 저장하지만 혼자서는 아무 작업도 하지 "
        "못합니다."
    ),
    "info_book.integratedscripting.concepts.text3": (
        "&l스크립팅 드라이브&r에는 &l스크립팅 디스크&r 하나를 넣을 수 있으며, 디스크의 "
        "내용을 네트워크에 제공합니다."
    ),
    "info_book.integratedscripting.concepts.text4": (
        "&l스크립팅 터미널&r에서는 현재 네트워크의 &l스크립팅 드라이브&r가 제공하는 모든 "
        "스크립트를 보고 관리하고 편집할 수 있습니다."
    ),
    "info_book.integratedscripting.concepts.text5": (
        "이제 각 요소를 차례로 자세히 알아봅니다."
    ),
    "info_book.integratedscripting.disk.text1": (
        "&l스크립팅 디스크&r는 스크립트를 저장하며 &l스크립팅 드라이브&r에 넣어 "
        "사용합니다. &l변수 카드&r와 &l멘데사이트&r를 조합해 만들 수 있습니다."
    ),
    "info_book.integratedscripting.disk.text2": (
        "&l스크립팅 디스크&r를 &l스크립팅 드라이브&r에 넣으면 고유 숫자 ID가 부여됩니다. "
        "&l스크립팅 터미널&r은 이 ID로 디스크의 스크립트를 수정하고, 스크립트 요소를 "
        "&l변수 카드&r에 연결할 때도 같은 ID를 사용합니다."
    ),
    "info_book.integratedscripting.disk.text3": (
        "&l스크립팅 디스크&r는 다른 네트워크의 &l스크립팅 드라이브&r로 옮겨도 스크립트 "
        "데이터가 사라지지 않습니다. 다만 해당 ID를 참조하는 &l변수 카드&r가 디스크와 같은 "
        "네트워크에 없으면 오류를 냅니다."
    ),
    "info_book.integratedscripting.disk.text4": (
        "&l스크립팅 디스크&r의 저장 용량에는 제한이 없지만, 관리하기 쉽도록 스크립트를 "
        "여러 디스크에 나누는 것을 권장합니다."
    ),
    "info_book.integratedscripting.drive.text1": (
        "&l스크립팅 드라이브&r는 &lIntegrated Dynamics&r 네트워크에 연결하는 블록입니다. "
        "&l스크립팅 디스크&r 하나를 넣어 그 안의 스크립트를 네트워크에 제공합니다."
    ),
    "info_book.integratedscripting.drive.text2": (
        "&l변수 저장소&r와 &l주크박스&r에 &l스크립팅 디스크&r를 조합하여 제작합니다."
    ),
    "info_book.integratedscripting.terminal.text1": (
        "&l스크립팅 터미널&r은 네트워크의 &l스크립팅 디스크&r에 저장된 스크립트를 "
        "관리하도록 &lIntegrated Dynamics&r 네트워크에 연결하는 부품입니다."
    ),
    "info_book.integratedscripting.terminal.text2": (
        "설치한 터미널을 우클릭하면 스크립트를 편집하는 간단한 &o통합 개발 환경&r(IDE)이 "
        "열립니다."
    ),
    "info_book.integratedscripting.terminal.text3": (
        "화면 왼쪽 위에서 네트워크에 연결된 &l스크립팅 디스크&r의 ID를 선택하면, 그 "
        "디스크에 저장된 모든 스크립트 파일이 아래 목록에 표시됩니다."
    ),
    "info_book.integratedscripting.terminal.text7": (
        "편집기는 간단한 구문 강조만 제공하고 현재는 구문 오류를 찾아내지 못합니다. 오류는 "
        "&l변수 카드&r로 스크립트를 실행할 때 표시됩니다."
    ),
    "info_book.integratedscripting.terminal.text8": (
        "스크립트 멤버를 &lIntegrated Dynamics&r 논리로 사용하려면 &l변수 카드&r에 "
        "바인딩하세요."
    ),
    "info_book.integratedscripting.terminal.text9": (
        "먼저 텍스트 편집기에서 변수 이름이나 함수 이름 같은 스크립트 멤버를 커서로 "
        "선택하세요."
    ),
    "info_book.integratedscripting.terminal.text10": (
        "그런 다음 화면 오른쪽 슬롯에 &l변수 카드&r를 넣으면 선택한 스크립트 멤버에 "
        "바인딩됩니다."
    ),
    "info_book.integratedscripting.terminal.text11": (
        "이제 &l변수 카드&r를 네트워크의 다른 곳에서 사용할 수 있습니다. 변수 멤버는 "
        "&l디스플레이 패널&r에 표시하고, 함수 멤버는 아이템 목록 필터의 연산자로 사용할 "
        "수 있습니다."
    ),
    "info_book.integratedscripting.writing.js.text1": (
        "이 모드에서는 JavaScript 문법으로 스크립트를 작성하며, ECMAScript(ECMA-262)의 "
        "모든 기능을 사용할 수 있습니다."
    ),
    "info_book.integratedscripting.writing.variables.text1": (
        "Integrated Dynamics의 모든 자료형(예: &6정수&0, &9불리언&0, &8아이템&0 등)은 "
        "JavaScript와 서로 변환해 사용할 수 있습니다."
    ),
    "info_book.integratedscripting.writing.variables.text2": (
        "JavaScript에서 만든 값을 정적 &l변수 카드&r로 사용하려면 &olet&r 또는 &oconst&r로 "
        "변수 멤버를 정의하는 방법이 가장 간단합니다."
    ),
    "info_book.integratedscripting.writing.variables.text4": (
        "이 값을 &l변수 카드&r에서 사용하려면 스크립팅 터미널 편집기에서 변수 멤버 이름을 "
        "선택하고 오른쪽 슬롯에 빈 &l변수 카드&r를 넣으세요. 이제 이 &l변수 카드&r를 "
        "&l디스플레이 패널&r에 표시하는 등 평소처럼 사용할 수 있습니다."
    ),
    "info_book.integratedscripting.writing.variables.text5": (
        "JavaScript 변수는 특정 값을 가진 긴 &4문자열&0처럼 &l논리 프로그래머&r에서 만들기 "
        "어려운 복잡한 값을 정의할 때 특히 유용합니다. 아래에서 이런 값을 만드는 예를 볼 "
        "수 있습니다."
    ),
    "info_book.integratedscripting.writing.functions.text1": (
        "&2연산자&0는 Integrated Dynamics 논리에서 값처럼 다룰 수 있으므로 JavaScript "
        "함수로도 만들 수 있습니다."
    ),
    "info_book.integratedscripting.writing.functions.text3": (
        "함수는 여러 인수를 받습니다. Integrated Dynamics 논리에서 함수를 실행하면 일반 "
        "Integrated Dynamics 값이 JavaScript 값으로 변환되어 인수로 전달됩니다."
    ),
    "info_book.integratedscripting.writing.functions.text4": (
        "JavaScript 함수를 &2연산자&0로 &l변수 카드&r에 바인딩하는 방법은 상수나 변수와 "
        "같습니다. 스크립팅 터미널 편집기에서 함수 멤버 이름을 선택하고 &l변수 카드&r에 "
        "바인딩하세요. 이제 이 값은 &2연산자&0를 받는 모든 곳에서 사용할 수 있습니다."
    ),
    "info_book.integratedscripting.writing.functions.text5": (
        "예를 들어 &8아이템&0 인수 하나를 받아 &9불리언&0을 반환하는 함수를 만들면, "
        "상자에서 읽은 아이템 목록을 거르는 필터 &2연산자&0로 사용할 수 있습니다."
    ),
    "info_book.integratedscripting.writing.functions.text6": (
        "아래에서 만들 수 있는 여러 함수 유형의 예를 볼 수 있습니다."
    ),
    "info_book.integratedscripting.writing.globals.text1": (
        "JavaScript 코드에서는 전역 &oidContext&r 변수의 &oops&r 필드를 통해 Integrated "
        "Dynamics의 모든 연산자를 함수로 호출할 수 있습니다. 새 연산자를 만들 때 기존 "
        "연산자를 활용할 수 있는 방법입니다."
    ),
    "info_book.integratedscripting.writing.globals.text2": (
        "예를 들어 아래처럼 아이템이 쌓이는지, 스택 크기가 16 이상인지 확인하는 &8아이템&0 "
        "필터를 작성할 수 있습니다."
    ),
    "info_book.integratedscripting.writing.globals.text3": (
        "실행할 연산자의 이름은 &l논리 프로그래머&r의 연산자 툴팁이나 이 가이드의 논리 "
        "프로그래밍 절에 있는 연산자 목록에서 전역 이름을 확인하세요."
    ),
    "info_book.integratedscripting.writing.globals.text4": (
        "&oidContext&r로 연산자를 호출하는 코드가 너무 길어지면 두 번째 예처럼 연산자를 "
        "사용자 정의 상수 변수에 저장할 수 있습니다. 다음 절에서 설명하는 &o객체 "
        "메서드&r를 사용할 수도 있습니다."
    ),
    "info_book.integratedscripting.writing.methods.text1": (
        "전역 함수를 길게 호출하지 않고 &l객체 메서드&r로 더 간결한 코드를 작성할 수 "
        "있습니다."
    ),
    "info_book.integratedscripting.writing.methods.text2": (
        "&8블록&0, &8아이템&0, &8유체&0 같은 객체 자료형은 JavaScript에서 사용할 때 "
        "&l메서드&r를 제공합니다."
    ),
    "info_book.integratedscripting.advanced.transient_storage.text1": (
        "Integrated Dynamics는 함수형 프로그래밍 원칙을 따르므로 &l지연기&r 같은 외부 "
        "수단을 제외하면 상태를 저장하지 않습니다."
    ),
    "info_book.integratedscripting.advanced.transient_storage.text2": (
        "JavaScript는 함수형 프로그래밍과 명령형 프로그래밍을 모두 지원하므로 상태를 "
        "일부 저장할 수 있습니다."
    ),
    "info_book.integratedscripting.advanced.transient_storage.text3": (
        "구체적으로 함수 밖에 변경 가능한 변수(예: &olet&r)를 선언하면 함수 호출로 값을 "
        "수정할 수 있습니다."
    ),
    "info_book.integratedscripting.advanced.transient_storage.text4": (
        "이 방식으로 함수 호출 횟수를 세거나 특정 값의 이동 평균을 계산하는 등 상태를 "
        "추적할 수 있습니다."
    ),
    "info_book.integratedscripting.advanced.transient_storage.text6": (
        "따라서 이 값이 항상 남아 있다고 가정하면 안 됩니다. 영구 데이터 저장이 필요하면 "
        "&l지연기&r를 사용하는 편이 좋습니다."
    ),
    "info_book.integratedscripting.advanced.external_editing.text1": (
        "싱글플레이 또는 멀티플레이 게임이 실행되는 파일 시스템에 접근할 수 있다면 외부 "
        "편집기에서도 스크립트 파일을 열 수 있습니다. 선호하는 IDE(Vi 등, 물론 Emacs는 "
        "아니고요)로 스크립트를 작성할 수 있습니다."
    ),
    "info_book.integratedscripting.advanced.external_editing.text2": (
        "스크립트 파일은 &oworld/integratedscripting/&r 디렉터리에 있습니다(싱글플레이 "
        "월드는 &osaves/&r 아래를 확인하세요). 안에는 ID별 &l스크립팅 디스크&r 디렉터리가 "
        "있고, 각 &l스크립팅 디스크&r 디렉터리에 해당 디스크의 모든 스크립트 파일이 "
        "저장됩니다."
    ),
    "info_book.integratedscripting.advanced.external_editing.text4": (
        "외부 편집기가 파일 변경 감지를 지원한다면(현대적인 IDE는 대부분 지원합니다), "
        "&l스크립팅 터미널&r에서 스크립트를 바꿨을 때 외부 편집기의 파일도 갱신됩니다."
    ),
    "info_book.integratedscripting.advanced.logging.text2": (
        "JavaScript에서 &oconsole.log()&r와 &oconsole.error()&r 같은 함수를 호출하면 각각 "
        "&o표준 출력&r과 &o표준 오류&r 스트림에 메시지를 기록합니다."
    ),
    "info_book.integratedscripting.advanced.logging.text3": (
        "이 함수를 호출한 로그 메시지는 스크립트별 &o.stdout&r 또는 &o.stderr&r 파일에 "
        "기록됩니다."
    ),
    "info_book.integratedscripting.advanced.logging.text4": (
        "예를 들어 스크립트가 &omyfile.js&r라면 로그 메시지는 &omyfile.js.stdout&r에 "
        "기록됩니다."
    ),
    "info_book.integratedscripting.advanced.logging.text5": (
        "&o.stdout&r와 &o.stderr&r 파일은 &l스크립팅 터미널&r이나 외부 편집으로 열 수 "
        "있습니다."
    ),
    "info_book.integratedscripting.advanced.typescript.text1": (
        "TypeScript는 JavaScript에 자료형 지원을 더한 널리 쓰이는 상위 집합 언어입니다. "
        "변수와 함수의 자료형을 정의하여 자료형에 안전한 JavaScript 코드를 작성할 수 "
        "있습니다."
    ),
    "info_book.integratedscripting.advanced.typescript.text2": (
        "Integrated Scripting은 순수 JavaScript만 실행하지만, 모든 전역 함수와 자료형, "
        "메서드의 TypeScript &o타입 정의 파일&r을 제공합니다."
    ),
    "info_book.integratedscripting.advanced.typescript.text3": (
        "외부 IDE에서 스크립트를 편집할 때 타입 정의 파일을 불러오면 자료형에 안전한 "
        "스크립트를 작성할 수 있습니다. TypeScript와 사용법을 알고 있을 때만 권장합니다."
    ),
    "info_book.integratedscripting.advanced.typescript.text4": (
        "타입 정의 파일은 &oworld/integratedscripting/integratedscripting.d.ts&r에 "
        "있습니다(싱글플레이 월드는 &osaves/&r 아래를 확인하세요). 월드를 다시 시작할 "
        "때마다 자동으로 생성되므로 직접 수정하지 마세요."
    ),
    "info_book.integratedscripting.tutorials.introduction.text1": (
        "이 절에는 복잡한 작업을 스크립트로 처리하는 &lIntegrated Dynamics&r 애드온인 "
        "&lIntegrated Scripting&r의 사용법을 배우는 튜토리얼이 있습니다."
    ),
    "info_book.integratedscripting.tutorials.basics.text1": (
        "&l멘데사이트&r 블록은 스크립팅 관련 아이템의 기본 제작 재료입니다. &l건조대&r로 "
        "만들어 보세요!"
    ),
    "info_book.integratedscripting.tutorials.basics.text2": (
        "다음으로 &l멘데사이트&r 블록을 사용해 &l스크립팅 디스크&r와 &l스크립팅 "
        "드라이브&r를 만듭니다. &l스크립팅 디스크&r는 스크립트 데이터를 저장하고, "
        "&l스크립팅 드라이브&r는 그 디스크를 네트워크에 연결합니다."
    ),
    "info_book.integratedscripting.tutorials.basics.text3": (
        "마지막으로 &l스크립팅 드라이브&r를 놓고 &l스크립팅 디스크&r를 넣으세요. 다음 "
        "튜토리얼부터 스크립트를 저장할 수 있습니다."
    ),
    "info_book.integratedscripting.tutorials.terminal.text2": (
        "먼저 &l스크립팅 터미널&r을 제작해 &l스크립팅 드라이브&r와 연결된 케이블에 놓고, "
        "&l스크립팅 터미널&r을 우클릭해 여세요."
    ),
    "info_book.integratedscripting.tutorials.terminal.text3": (
        "편집기에는 네트워크에서 접근 가능한 여러 &l스크립팅 디스크&r의 모든 스크립트 "
        "파일이 표시됩니다. 화면 왼쪽 위의 화살표로 &l스크립팅 디스크&r를 전환할 수 "
        "있습니다."
    ),
    "info_book.integratedscripting.tutorials.terminal.text4": (
        '아직 네트워크에 스크립트 파일이 없으므로 화면 왼쪽 아래의 "+" 버튼을 눌러 새 '
        "파일을 만드세요. 새 파일을 열고 화면 오른쪽 텍스트 영역을 클릭하여 "
        "&oJavaScript&r 코드를 작성합니다."
    ),
    "info_book.integratedscripting.tutorials.terminal.text6": (
        "마지막으로 상수를 &l변수 카드&r에 바인딩합니다. 화면 오른쪽 슬롯에 빈 &l변수 "
        "카드&r를 넣고 커서로 변수를 두 번 클릭하세요. 완성된 &l변수 카드&r는 상수 값에 "
        "바인딩되며, 이제 이 &l변수 카드&r를 네트워크 어디서든 사용할 수 있습니다. "
        "&l디스플레이 패널&r에 표시해 보세요!"
    ),
    "info_book.integratedscripting.tutorials.functions.text1": (
        "JavaScript로 상수를 만드는 것도 재미있지만, 스크립트의 진짜 힘은 &o함수&r를 "
        "만들 때 드러납니다."
    ),
    "info_book.integratedscripting.tutorials.functions.text2": (
        "JavaScript 함수는 &2연산자&0로 &l변수 카드&r에 바인딩해 일반 Integrated "
        "Dynamics 논리에서 사용할 수 있습니다. Integrated Tunnels 출력기의 필터를 "
        "정의하거나, 목록에 있는 아이템 스택 크기의 중간값처럼 복잡한 값을 계산할 수 "
        "있습니다."
    ),
    "info_book.integratedscripting.tutorials.functions.text3": (
        "이 튜토리얼에서는 &8아이템&0 인수 하나를 받아 &9불리언&0을 출력하는 함수를 "
        "만듭니다. 이 함수는 아이템 목록을 거르는 필터 연산자로 사용할 수 있습니다."
    ),
    "info_book.integratedscripting.tutorials.functions.text6": (
        "필터링된 목록의 결과를 &l디스플레이 패널&r에 표시하면 튜토리얼이 완료됩니다."
    ),
    "info_book.integratedscripting.tutorials.functions.text7": (
        "예제 스크립트에서는 아이템의 &oisStackable()&r 및 &ostacksize()&r 같은 내장 "
        "메서드를 호출할 수 있습니다. 사용 가능한 메서드의 자세한 목록은 가이드 뒤쪽에서 "
        "확인하세요."
    ),
    "general.integratedtunnels.description": (
        "Integrated Dynamics 네트워크로 아이템·유체·에너지 등을 전송합니다."
    ),
    "advancement.integratedtunnels.interface_item": "아이템 인터페이스",
    "advancement.integratedtunnels.interface_fluid": "유체 인터페이스",
    "advancement.integratedtunnels.interface_energy": "에너지 인터페이스",
    "advancement.integratedtunnels.import_items_list": "목록 기반 아이템 입력",
    "advancement.integratedtunnels.import_items_list.desc": (
        "아이템 입력기로 목록에 있는 모든 아이템을 인벤토리에 입력하세요"
    ),
    "advancement.integratedtunnels.pickup_items_limit.desc": (
        "월드 아이템 입력기로 한 번에 아이템 5개를 주우세요"
    ),
    "advancement.integratedtunnels.place_logwood.desc": (
        "월드 블록 출력기에서 'logs' 태그 목록을 사용해 아무 통나무나 배치하세요"
    ),
    "advancement.integratedtunnels.player_simulator": "플레이어 시뮬레이션",
    "parttype.integratedtunnels.interface_filter_energy.info": (
        "에너지 저장 장치를 네트워크에 연결하고 통과 여부를 필터링합니다."
    ),
    "parttype.integratedtunnels.importer_world_energy.info": (
        "월드의 에너지를 주워 네트워크로 가져옵니다."
    ),
    "parttype.integratedtunnels.exporter_world_energy.info": (
        "네트워크의 에너지를 월드로 내보냅니다."
    ),
    "parttype.integratedtunnels.importer_world_item.info": (
        "월드의 아이템을 주워 네트워크로 가져옵니다."
    ),
    "parttype.integratedtunnels.exporter_world_item.info": (
        "네트워크의 아이템을 월드에 놓습니다."
    ),
    "parttype.integratedtunnels.importer_world_fluid.info": (
        "월드의 유체를 주워 네트워크로 가져옵니다."
    ),
    "parttype.integratedtunnels.exporter_world_fluid.info": (
        "네트워크의 유체를 월드에 놓습니다."
    ),
    "parttype.integratedtunnels.player_simulator.info": (
        "플레이어의 행동을 시뮬레이션합니다."
    ),
    "info_book.integratedtunnels.player": "플레이어 시뮬레이션",
    "info_book.integratedtunnels.tutorials.introduction.text1": (
        "이 절에는 아이템·유체·에너지를 전송하는 &lIntegrated Dynamics&r 애드온인 "
        "&lIntegrated Tunnels&r의 사용법을 배우는 튜토리얼이 있습니다."
    ),
    "info_book.integratedtunnels.tutorials.export_items_limit.text1": (
        "&l인벤토리 판독기&r로 대상 인벤토리의 아이템 수를 읽고, 전체 수량이 &610&0보다 "
        "커질 때까지만 아이템을 옮기세요."
    ),
    "info_book.integratedtunnels.tutorials.import_items_list": "아이템 목록 입력",
    "info_book.integratedtunnels.tutorials.world_item_importer_exporter.text1": (
        "&o아이템 입력기&r와 &o아이템 출력기&r처럼 &l월드 아이템 입력기&r는 월드의 "
        "아이템을 네트워크로 줍고, &l월드 아이템 출력기&r는 네트워크의 아이템을 월드에 "
        "놓습니다. &o셜커 상자&r처럼 인벤토리가 있는 드롭된 아이템과도 상호작용합니다."
    ),
    "info_book.integratedtunnels.tutorials.drop_all_items.text1": (
        "&l월드 아이템 출력기&r에 빈 &l변수 카드&r를 넣어 네트워크의 모든 아이템을 "
        "바닥에 떨어뜨리세요."
    ),
    "info_book.integratedtunnels.tutorials.pickup_items_limit": ("제한된 아이템 줍기"),
    "info_book.integratedtunnels.tutorials.pickup_items_limit.text1": (
        "&l변수 카드&r에 상수 &65&0를 작성하고 &l월드 아이템 입력기&r에 넣어 대상 "
        "공간에서 한 번에 아이템 5개를 주우세요."
    ),
    "info_book.integratedtunnels.tutorials.break_stone.text1": (
        "&8돌&0 아이템 값을 참조하는 &l변수 카드&r를 만들어 &l월드 블록 입력기&r에 "
        "넣으면 돌 블록만 부숩니다. 애스펙트 설정에서 섬세한 손길을 켜 조약돌 대신 돌을 "
        "얻을 수 있는지도 확인해 보세요."
    ),
    "info_book.integratedtunnels.tutorials.place_logwood.text1": (
        "통나무만 놓는 &l월드 블록 출력기&r 시스템을 만들어 보세요. &l태그 값&r 연산자로 "
        "&ologs&r 태그에 속한 모든 아이템 목록을 가져오면 됩니다."
    ),
    "info_book.integratedtunnels.tutorials.click_sword.text1": (
        "반복 클릭은 지루하니 &l플레이어 시뮬레이터&r에 맡겨 보세요. 먼저 장치를 제작하고 "
        "&o다이아몬드 검&r이 든 &l변수 카드&r를 넣으면 아이템 네트워크의 &o다이아몬드 "
        "검&r을 사용해 자동으로 공격합니다."
    ),
    "gui.integrateddynamics.button.add": "추가",
    "gui.integrateddynamics.partoffset.offsets.max": "최대 오프셋: %s",
    "parttype.integrateddynamics.tooltip.maxoffset": "최대 오프셋: %s",
    "operator.integrateddynamics.list.append": "끝에 추가",
    "proxy.integrateddynamics.error.proxy_invalid_type": (
        "ID가 %s인 프록시는 %s 자료형 변수를 노출해야 하지만 %s이(가) 발견되었습니다."
    ),
    "delay.integrateddynamics.error.delay_invalid_type": (
        "ID가 %s인 지연기는 %s 자료형 변수를 노출해야 하지만 %s이(가) 발견되었습니다."
    ),
    "operator.integrateddynamics.error.operator_recursion_limit": (
        "연산자 재귀 한계 %s에 도달해 %s을(를) 호출할 수 없습니다. 게임을 멈추게 하려던 "
        "것은 아니죠?"
    ),
    "gui.integratedscripting.removal_dialog.message": ('"%s" 항목을 삭제하시겠습니까?'),
    "aspect.integrateddynamics.write.double.effect.particle.minecraft_dripping_lava.info": (
        "지정한 속도로 뚝뚝 떨어지는 용암 입자를 방출합니다."
    ),
    "aspect.integrateddynamics.write.double.effect.particle.minecraft_falling_lava.info": (
        "지정한 속도로 낙하하는 용암 입자를 방출합니다."
    ),
    "aspect.integrateddynamics.write.double.effect.particle.minecraft_dripping_water.info": (
        "지정한 속도로 뚝뚝 떨어지는 물 입자를 방출합니다."
    ),
    "aspect.integrateddynamics.write.double.effect.particle.minecraft_falling_water.info": (
        "지정한 속도로 낙하하는 물 입자를 방출합니다."
    ),
    "aspect.integrateddynamics.read.boolean.world.mob": "몹 존재 여부",
    "aspect.integrateddynamics.read.boolean.world.animal": "동물 존재 여부",
    "aspect.integrateddynamics.read.boolean.world.player": "플레이어 존재 여부",
    "aspect.integrateddynamics.read.boolean.world.item": "아이템 존재 여부",
    "operator.integrateddynamics.entity.ismob": "몹인지 여부",
    "operator.integrateddynamics.entity.isanimal": "동물인지 여부",
    "operator.integrateddynamics.entity.isplayer": "플레이어인지 여부",
    "operator.integrateddynamics.entity.isitem": "아이템인지 여부",
    "operator.integrateddynamics.operator.reduce": "축약",
    "operator.integrateddynamics.string.split_on": "기준 문자열로 나누기",
    "operator.integrateddynamics.list.slice": "일부 잘라내기",
    "info_book.integrateddynamics.introduction.text1": (
        "오랫동안 자동화 방법은 지나치게 제한적이었습니다. &1Integrated Dynamics&0는 논리 "
        "시스템 자동화의 대표 모드를 목표로 합니다. &lMinecraft&r와 여러 모드의 요소를 "
        "폭넓게 연결하여, 표현력이 높고 몰입감 있는 논리 프로그래밍 환경을 제공합니다."
    ),
    "info_book.integrateddynamics.introduction.text2": (
        "레드스톤 회로는 단순하면서도 쓸 만하고 이해하기 쉬운 자동화 방법입니다. 하지만 그 "
        "단순함이 불편할 때도 있습니다. 복잡한 자동화 네트워크에서는 회로가 매우 커져 "
        "관리하기 어려워지고, 작은 누수 하나만으로도 큰 문제가 생길 수 있습니다."
    ),
    "info_book.integrateddynamics.introduction.text3": (
        "이 가이드의 목적은 두 가지입니다. 먼저 모드의 핵심 개념을 배우는 &l튜토리얼&r을 "
        "제공합니다. 다음으로 튜토리얼을 원하지 않는 플레이어를 위해 모든 요소와 작동 "
        "방식을 설명하는 자세한 &l설명서&r를 제공합니다."
    ),
    "info_book.integrateddynamics.introduction.text4": (
        "아래쪽 화살표를 클릭하면 페이지를 넘기고, Shift+클릭하면 페이지 대신 절 단위로 "
        "이동합니다. 큰 절의 첫 페이지에는 하위 절로 바로 이동하는 목차가 있습니다. 제작법에 "
        "나오는 설명 대상 아이템을 클릭하면 해당 절로 이동합니다. 왼쪽 위 버튼은 상위 절로, "
        "오른쪽 위 버튼은 직전에 보았던 페이지로 이동합니다."
    ),
    "info_book.integrateddynamics.tutorials.menrilBasics.text2": (
        "그다음 &l멘릴 원목&r을 처리할 &l압착기&r와 &l건조대&r를 만드세요. &l압착기&r에 "
        "원목 블록을 놓고 평평해질 때까지 위에서 뛰면 됩니다. 그러면 &l멘릴 수지&r가 "
        "&l압착기&r의 양옆으로 흘러나옵니다. &l건조대&r를 &l압착기&r 옆에 놓아 방금 짠 "
        "&l멘릴 수지&r를 받으세요."
    ),
    "info_book.integrateddynamics.tutorials.networkFoundations.text1": (
        "이 모드의 핵심은 자동화 제어 네트워크를 만드는 것입니다. &l논리 케이블&r 10개로 "
        "네트워크를 만들어 보세요."
    ),
    "info_book.integrateddynamics.tutorials.basicNetworkComponents.text1": (
        "&l변수 카드&r를 값에 바인딩하는 방법 중 하나는 &l판독기&r로 값을 읽는 것입니다. "
        "먼저 기본 판독기를 몇 개 만드세요. 그런 다음 &l변수 카드&r의 값을 보여 주는 "
        "&l디스플레이 패널&r도 만드세요."
    ),
    "info_book.integrateddynamics.tutorials.aspects.text5": (
        "다음으로 &l레드스톤 작성기&r를 만들고, 레드스톤 판독기가 읽은 최대 정수 "
        "레드스톤 값을 출력하게 하세요."
    ),
    "info_book.integrateddynamics.tutorials.logicOperations.text1": (
        "판독기에서 읽은 값을 표시하는 것도 유용하지만, &2연산자&0로 여러 값을 결합하면 "
        "훨씬 흥미로운 일을 할 수 있습니다. 모든 &2연산자&0는 &l논리 프로그래머&r에서 "
        "찾을 수 있습니다."
    ),
    "info_book.integrateddynamics.tutorials.logicOperations.text2": (
        "아이템과 블록 형태가 모두 있는 &l논리 프로그래머&r를 만드세요. GUI를 열면 모든 "
        "&l연산자&r 목록이 표시됩니다."
    ),
    "info_book.integrateddynamics.tutorials.logicOperations.text5": (
        "&l변수 카드&r에 값을 쓴 뒤에도 카드를 &l논리 프로그래머&r에 다시 넣어 언제든지 "
        "수정할 수 있습니다."
    ),
    "info_book.integrateddynamics.tutorials.logicOperations.text6": (
        "&1Integrated Dynamics&0는 변수를 &o지연 평가&r합니다. 따라서 이 &l덧셈&r "
        "&l변수 카드&r에 두 &6정수&0의 합이 직접 저장되는 것이 아니라, 네트워크에서 값이 "
        "필요할 때 변수 참조를 따라 덧셈을 수행합니다. 네트워크가 참조한 &l변수 카드&r를 "
        "찾을 수 있도록 &l변수 저장소&r를 제작해 놓으세요. 두 &6정수&0 &l변수 카드&r를 "
        "저장소에 넣으면 네트워크에서 사용할 수 있습니다."
    ),
    "info_book.integrateddynamics.tutorials.logicOperations.text7": (
        "마지막으로 케이블을 &l변수 저장소&r에 연결하고 &l디스플레이 패널&r을 부착한 뒤, "
        "&l덧셈&r &l변수 카드&r를 넣어 합계를 표시하세요."
    ),
    "info_book.integrateddynamics.tutorials.logicOperations.text8": (
        "복잡한 자동화를 만들 때 &l논리 프로그래머&r와 &l변수 저장소&r를 자주 사용하게 "
        "됩니다."
    ),
    "info_book.integrateddynamics.manual.logic.value_types.recipe.text1": (
        "&8재료&0를 입력받아 다른 &8재료&0 값을 출력하는 추상 제작법입니다."
    ),
    "info_book.integrateddynamics.manual.logic.value_types.recipe.text2": (
        "제작법은 &l논리 프로그래머&r에서 직접 만들거나, &l기계 판독기&r로 지원되는 "
        "기계에서 읽을 수 있습니다."
    ),
    "info_book.integrateddynamics.manual.logic.value_types.recipe.text4": (
        "GUI에서 기존 &l변수 카드&r의 제작법을 찾을 때 Shift를 누르면 각 제작법의 출력 "
        "아이템을 잠시 표시할 수 있습니다."
    ),
    "info_book.integrateddynamics.manual.logic.value_types.recipe.text5": (
        "&l논리 프로그래머&r의 입력 슬롯을 Shift+클릭하면 세부 속성을 설정할 수 있습니다. "
        "NBT를 비교할지, 제작 후 완전히 소모되지 않는 아이템을 여러 제작법에서 재사용할지, "
        "태그가 같은 대체 아이템을 허용할지 등을 정합니다."
    ),
    "info_book.integrateddynamics.manual.parts.offsets.text1": (
        "부품은 기본적으로 바로 앞의 위치를 대상으로 합니다. &l부품 향상&r을 적용하면 부품의 "
        "&l오프셋&r 화면에서 대상 위치를 바꿀 수 있습니다."
    ),
    "info_book.integrateddynamics.manual.parts.offsets.text3": (
        "오프셋은 직접 입력하거나 &l렌치&r로 눈앞에서 지정할 수 있습니다. &l렌치&r를 오프셋 "
        "모드로 바꾸고 Shift+우클릭하면 위치가 저장됩니다. 그 &l렌치&r로 부품을 우클릭하면 "
        "저장한 위치를 부품에 적용합니다."
    ),
    "info_book.integrateddynamics.manual.parts.offsets.text4": (
        "오프셋은 고정값뿐 아니라 &l변수 카드&r를 이용한 &o동적&r 값으로도 정의할 수 "
        "있습니다."
    ),
    "info_book.integrateddynamics.manual.machines.energy_battery.text2": (
        "이 배터리는 &lRF&r 기반 전력과 &lTesla&r 전력을 모두 받습니다."
    ),
    "info_book.integrateddynamics.manual.machines.energy_battery.text4": (
        "배터리를 인벤토리에 둔 상태에서 Shift+우클릭하면 &l자동 공급&r 모드를 켤 수 "
        "있습니다. 이 모드에서는 양손에 든 아이템에 에너지를 자동으로 채웁니다."
    ),
    "info_book.integrateddynamics.manual.diagnostics.text1": (
        "관리자 권한이 있는 플레이어는 서버의 모든 네트워크 틱 소요 시간을 살펴보는 "
        "&l네트워크 진단&r 도구를 사용할 수 있습니다."
    ),
    "info_book.integrateddynamics.manual.diagnostics.text2": (
        "&o\\integrateddynamics networkdiagnostics&r 명령을 실행하면 이 도구에 사용할 임시 "
        "로컬 웹 서버가 시작됩니다."
    ),
    "info_book.integrateddynamics.manual.diagnostics.text3": (
        "명령 실행 뒤 표시된 링크를 클릭하면 웹 브라우저에서 모든 네트워크와 구성 요소의 "
        "표가 열립니다. 행을 클릭하면 월드에서 해당 요소를 강조하고, &l순간이동&r 버튼을 "
        "클릭하면 플레이어가 해당 위치로 이동합니다."
    ),
    "info_book.integrateddynamics.tutorials.nbt.text4": (
        "마지막으로 이 &3책&0 하위 태그의 &3id&0 필드를 읽습니다. 이번에는 직전에 읽은 "
        "하위 태그가 아니라 루트에서 시작해 &lNBT 경로&r 표현식을 적용합니다. 이 표현식은 "
        "깊이 중첩된 &4NBT&0 값을 읽을 때 유용합니다. 예를 들어 &3NBT&0 태그 &3{ root: { "
        "child1: { child2: ”some value” }}}&0에 &4”.root.child1.child2”&0를 적용하면 "
        "&3”some value”&0가 출력됩니다. &lNBT 경로&r의 고급 기능은 설명서의 고급 절에서 "
        "다룹니다."
    ),
    "info_book.integrateddynamics.manual.prerequisites.squeezer.text1": (
        "&l압착기&r는 게임 초반에 블록과 아이템을 밟아 부수거나 압착하는 기계입니다. "
        "플레이어뿐 아니라 어떤 엔티티든 위로 뛰거나 떨어져 작동시킬 수 있습니다. 결과 "
        "아이템은 인접한 인벤토리나 바닥으로 나오고, 결과 유체는 기계 안에 남았다가 옆에 "
        "대상 탱크가 있으면 양쪽 중 한 곳으로 흐릅니다. 레드스톤 신호로 내부 발판을 "
        "초기화할 수 있습니다. 특히 &l멘릴 원목&r에서 수지를 짜는 데 사용합니다."
    ),
    "info_book.integrateddynamics.manual.logic.advanced.nbt_path.text1": (
        "복잡한 &3NBT&0 태그에서 깊이 중첩된 값을 읽으려면 연산자를 길게 연결해야 할 수 "
        "있습니다. 이 작업을 단순하게 하도록 &4문자열&0 기반 &lNBT 경로 표현식&r으로 "
        "&3NBT&0 태그 안의 경로를 지정할 수 있습니다."
    ),
    "info_book.integrateddynamics.manual.logic.advanced.nbt_path.text2": (
        "가장 간단한 NBT 경로 표현식은 &4.fieldName&0 또는 &4[”fieldName”]&0 같은 &l필드 "
        "선택기&r를 연속해서 사용합니다."
    ),
    "info_book.integrateddynamics.manual.logic.advanced.nbt_path.text3": (
        "예를 들어 &3NBT&0 태그 &3{ root: { child1: { child2: ”some value” }}}&0에 "
        "&4”.root.child1.child2”&0를 적용하면 &3”some value”&0가 출력됩니다."
    ),
    "info_book.integrateddynamics.manual.logic.advanced.nbt_path.text4": (
        "필드 이름 배열이나 와일드카드로 여러 필드를 선택할 수 있습니다. 예: "
        "&4[fieldA,fieldB]&0 또는 &4*&0"
    ),
    "info_book.integrateddynamics.manual.logic.advanced.nbt_path.text5": (
        "예를 들어 &3NBT&0 태그 &3{ a: { b1: { c: ”some value” }}}&0에 "
        "&4”.a[b1,b2]*”&0를 적용하면 &3”some value”&0가 출력됩니다."
    ),
    "info_book.integrateddynamics.manual.logic.advanced.nbt_path.text6": (
        "NBT 목록에서는 &4[1]&0처럼 인덱스를 지정해 특정 원소를 선택할 수 있습니다."
    ),
    "info_book.integrateddynamics.manual.logic.advanced.nbt_path.text7": (
        "예를 들어 &3NBT&0 태그 &3{ a: [10,20] }&0에 &4”.a[1]”&0을 적용하면 "
        "&3”20”&0이 출력됩니다."
    ),
    "info_book.integrateddynamics.manual.logic.advanced.nbt_path.text8": (
        "슬라이스 연산자 &4[start:end:step]&0로 여러 목록 인덱스를 선택할 수 있습니다. "
        "시작값만 필수이고 나머지는 생략할 수 있습니다."
    ),
    "info_book.integrateddynamics.manual.logic.advanced.nbt_path.text9": (
        "예를 들어 &3NBT&0 태그 &3{ a: [0,1,2,3,4,5] }&0에 &4”.a[1:4:2]”&0를 "
        "적용하면 &3[1,3]&0이 출력됩니다."
    ),
    "info_book.integrateddynamics.manual.parts.writer.effect.text1": (
        "지정한 값과 설정에 따라 입자를 방출합니다."
    ),
    "info_book.integrateddynamics.manual.machines.materializer.text1": (
        "동적 &l변수 카드&r의 현재 값을 고정하려면 &l구체화 장치&r를 사용합니다. 동적 "
        "&l변수 카드&r와 새 빈 &l변수 카드&r를 넣으면, 동적 &l변수 카드&r의 현재 값이 "
        "정적 값으로 새 카드에 저장됩니다."
    ),
    "info_book.integrateddynamics.manual.machines.materializer.text3": (
        "&l변수 카드&r는 파이프로 &l구체화 장치&r에 넣거나 꺼낼 수 있습니다."
    ),
    "info_book.integrateddynamics.tutorials.advancedOperations.text1": (
        "앞 튜토리얼에서 보았듯 &l논리 프로그래머&r는 숫자 덧셈보다 훨씬 많은 일을 할 "
        "수 있습니다. 이번에는 고급 데이터 구조와 연산자 연결을 알아봅니다."
    ),
    "info_book.integrateddynamics.tutorials.advancedOperations.text2": (
        "먼저 &6정수&0 &61&0, &610&0, &6100&0이 담긴 정적 &7목록&0을 만들고 "
        "&l디스플레이 패널&r에 표시하세요."
    ),
    "info_book.integrateddynamics.tutorials.advancedOperations.text3": (
        "&7아이템&0은 이 모드의 자료형 중 하나입니다. 정적 &7아이템&0 &l변수 카드&r를 "
        "만들고 아이템의 모드 이름을 동적으로 가져와 &l디스플레이 패널&r에 표시하세요."
    ),
    "info_book.integrateddynamics.tutorials.advancedOperations.text4": (
        "참조된 변수를 찾을 수 있도록 &l변수 저장소&r에 넣어야 합니다."
    ),
    "info_book.integrateddynamics.tutorials.theValueOfOperators.text1": (
        "&1Integrated Dynamics&0에서 &2연산자&0는 값처럼 다룰 수 있습니다. 지금까지는 "
        "&l논리 프로그래머&r에서 직접 사용했지만, 이번에는 &2연산자&0를 &l변수 카드&r에 "
        "저장하고 동적으로 호출하는 방법을 알아봅니다."
    ),
    "info_book.integrateddynamics.tutorials.theValueOfOperators.text4": (
        "&2연산자&0에는 &o술어&r 결합, &2연산자&0 인수 순서 뒤집기, &7목록&0 처리 등 "
        "여러 고급 연산이 있습니다."
    ),
    "block.integrateddynamics.materializer": "구체화 장치",
    "block.integrateddynamics.menril_sapling": "멘릴 묘목",
    "block.integrateddynamics.invisible_light": "보이지 않는 빛",
    "block.integrateddynamics.block_liquid_chorus": "액상 후렴과",
    "item.integrateddynamics.bucket_liquid_chorus": "액상 후렴과 양동이",
    "fluid_type.integrateddynamics.liquid_chorus": "액상 후렴과",
    "item.integrateddynamics.on_the_dynamics_of_integration": "통합의 역학",
    "item.integrateddynamics.enhancement_offset": "부품 향상: 오프셋",
    "gui.integrateddynamics.logicprogrammer.info.create": "§l새 값에 바인딩§r할 변수 카드",
    "gui.integrateddynamics.logicprogrammer.info.modify": "§l수정§r할 변수 카드",
    "gui.integrateddynamics.logicprogrammer.tooltip.writeslot.modify": (
        "값을 §l불러올§r 변수 카드를 넣으세요"
    ),
    "gui.integrateddynamics.operator.globalname": "전역 이름: %s",
    "gui.integrateddynamics.operator.localname": "메서드 이름: %s",
    "aspect.integrateddynamics.tooltip.part_id": "§e§o부품 ID: §r§o%s",
    "operator.integrateddynamics.applied.type": "§A적용 대상: §r%s",
    "operator.integrateddynamics.general": "일반",
    "operator.integrateddynamics.tooltip.input_type_name": "§e입력 자료형 %s: §r",
    "valuetype.integrateddynamics.value_type": "자료형",
    "parttype.integrateddynamics.tooltip.writer.active_aspect": "애스펙트: %s (%s)",
    "parttype.integrateddynamics.tooltip.noaspects": (
        "주의: 사용 가능한 애스펙트가 없습니다. 다른 모드를 설치하면 사용할 수 있습니다."
    ),
    "parttype.integratedtunnels.exporter_item": "아이템 출력기",
    "parttype.integratedcrafting.interface_crafting_attuned": "동조된 제작 인터페이스",
    "parttype.integratedcrafting.interface_crafting_attuned.unsupported": (
        "대상 기계가 제작법 처리를 지원하지 않습니다."
    ),
    "gui.integratedcrafting.partsettings.blockingmode": "차단 모드",
    "info_book.integratedcrafting.crafting_interface.configuration.text2": (
        "또한 &o재료 유형마다&r 대상 면을 따로 바꿀 수 있습니다. 대상 기계가 서로 다른 면에서 "
        "서로 다른 재료 유형을 받는 경우 유용합니다. 예를 들어 아이템은 측면에서, 유체는 "
        "위쪽에서 받을 수 있습니다."
    ),
    "info_book.integratedcrafting.tutorials.autocrafting_setup.text3": (
        "다음으로 &l제작 인터페이스&r에 참나무 판자를 만드는 방법을 알려 줍니다. "
        "&l논리 프로그래머&r를 열고 참나무 원목을 입력으로, 참나무 판자 4개를 출력으로 하는 "
        "&l제작법&r이 담긴 &l변수 카드&r를 작성하세요 &o(기본 아이템 일치 설정은 바꾸지 "
        "마세요)&r. &l이 제작법은 반드시 직접 만들어야 하며, JEI 같은 모드로 자동 입력하면 "
        "안 됩니다.&r"
    ),
    "info_book.integratedterminals.storage_terminal.usage.text9": (
        "기본적으로 터미널은 가능한 공간을 모두 사용합니다. &l격자 크기&r 버튼으로 높이만, "
        "너비만 조절하거나 행과 열 수를 고정(소형, 중형, 대형)하도록 바꿀 수 있습니다. 더 많은 "
        "슬롯을 표시하려면 Minecraft 설정에서 &lGUI 크기&r를 조절해 보세요. 각 격자 크기의 "
        "동작은 클라이언트 설정 파일에서 구성할 수 있습니다."
    ),
    "advancement.integratedscripting.mendesite": "멘데사이트 잔뜩",
    "advancement.integratedscripting.scripting_drive": "드라이브가 보이네",
    "advancement.integratedscripting.terminal_bind.desc": (
        "스크립트를 만들고 변수 카드에 바인딩하세요."
    ),
    "advancement.integratedscripting.filter_chest.desc": (
        "스크립트 기반 함수로 상자에서 읽은 아이템 목록을 필터링하세요."
    ),
    "gui.integratedscripting.removal_dialog.keep": "유지",
    "gui.integratedscripting.error.invalid_member": (
        "바인딩할 올바른 함수 이름이나 변수 이름을 스크립트 편집기에서 선택하세요."
    ),
    "valuetype.integratedscripting.error.translation.unknown_to_graal": (
        "%s 값을 Graal 값으로 바꾸는 변환기를 찾을 수 없습니다."
    ),
    "valuetype.integratedscripting.error.translation.unknown_to_graal_nbt": (
        "NBT 변환 중 %s 값을 Graal 값으로 바꾸는 변환기를 찾을 수 없습니다."
    ),
    "valuetype.integratedscripting.error.translation.unknown_from_graal": (
        "%s Graal 값을 바꾸는 변환기를 찾을 수 없습니다."
    ),
    "valuetype.integratedscripting.error.translation.nbt_unknown": (
        "%s 자료형인 NBT 멤버를 변환할 수 없습니다."
    ),
    "valuetype.integratedscripting.error.translation.nbt_unmatched": (
        "%s 필드를 NBT로 해석할 수 없습니다."
    ),
    "valuetype.integratedscripting.error.translation.unsupported_translateToNbt": (
        '%s "%s"을(를) NBT로 변환할 수 없습니다.'
    ),
    "valuetype.integratedscripting.error.translation.proxyobject_putMember": (
        '읽기 전용 %s에 키 "%s"을(를) 추가할 수 없습니다.'
    ),
    "script.integratedscripting.tooltip.disk": "§e§o디스크 ID: §r§o%s",
    "script.integratedscripting.tooltip.path": "§e§o스크립트 경로: §r§o%s",
    "script.integratedscripting.tooltip.member": "§e§o멤버: §r§o%s",
    "script.integratedscripting.error.disk_not_in_network": (
        "ID가 %s인 디스크를 현재 네트워크에서 찾을 수 없습니다."
    ),
    "script.integratedscripting.error.path_not_in_network": (
        'ID가 %s인 디스크에 "%s" 스크립트가 없습니다.'
    ),
    "script.integratedscripting.error.member_not_in_network": (
        'ID가 %s인 디스크의 "%s" 스크립트에 "%s" 멤버가 없습니다.'
    ),
    "script.integratedscripting.error.script_read": (
        '디스크 %s에서 "%s" 스크립트를 읽는 중 오류가 발생했습니다: %s'
    ),
    "script.integratedscripting.error.script_exec": (
        '디스크 %s의 "%s" 스크립트에서 "%s" 멤버를 실행하는 중 오류가 발생했습니다: %s'
    ),
    "script.integratedscripting.error.invalid_type": (
        '디스크 %s의 "%s" 스크립트에 있는 "%s" 멤버는 %s 자료형 변수를 노출해야 하지만 '
        "%s이(가) 발견되었습니다."
    ),
    "info_book.integratedscripting.writing.js.text2": (
        "&orequire&r와 &ofs&r 같은 Node.js 전용 기능은 사용할 수 없습니다. Node.js 애플리케이션 "
        "개발에 익숙하다면 Webpack 같은 외부 도구를 사용해 호환되게 만들 수 있습니다."
    ),
    "info_book.integratedscripting.writing.variables.text3": (
        "&olet&r은 카운터처럼 스크립트에서 나중에 다시 할당할 수 있는 변수를 정의합니다. "
        "&oconst&r는 다시 할당할 수 없는 변수를 정의합니다."
    ),
    "info_book.integratedscripting.writing.functions.text2": (
        "&ofunction&r 키워드나 사용자 정의 람다처럼 어떤 JavaScript 함수 작성 방식으로도 "
        "&2연산자&0를 만들 수 있습니다."
    ),
    "info_book.integratedscripting.writing.methods.text4": (
        "예를 들어 전역 함수 &oitemstackStackable&r은 &8아이템&0 인수 하나를 받아 &9불리언&0을 "
        "출력합니다. 이 함수는 &8아이템&0 값에서 인수가 없는 &ostackable&r 메서드로도 사용할 "
        "수 있습니다."
    ),
    "info_book.integratedscripting.writing.methods.text5": (
        "인수를 둘 이상 받는 전역 함수는 첫 인수를 뺀 나머지 인수로 객체 값의 메서드로도 "
        "사용할 수 있습니다. 예를 들어 전역 함수 &oitemstackStrength&r는 &8아이템&0과 "
        "&8블록&0 인수를 받지만, &8아이템&0에서는 &8블록&0 인수 하나를 받는 메서드로도 "
        "사용할 수 있습니다."
    ),
    "info_book.integratedscripting.advanced.logging": "로깅",
    "info_book.integratedscripting.advanced.logging.text6": (
        "로그 파일이 너무 커지지 않도록 크기가 제한됩니다. 기본 제한은 2096줄입니다. 더 많은 "
        "줄이 필요하면 서버 관리자에게 문의하세요."
    ),
    "info_book.integratedscripting.tutorials.terminal.text1": (
        "이전 단계에서 &l스크립팅 디스크&r와 &l스크립팅 드라이브&r를 만들고 배치했습니다. 이번 "
        "튜토리얼에서는 실제로 스크립트를 &o작성&r하고 &l변수 카드&r에 바인딩하는 방법을 "
        "살펴봅니다."
    ),
    "info_book.integratedscripting.tutorials.terminal.text5": (
        "지금은 간단한 상수 값을 만들겠습니다. &oconst myVar = 123;&r처럼 작성하세요."
    ),
    "info_book.integratedscripting.tutorials.functions.text4": (
        "구체적으로 &l인벤토리 판독기&r로 아이템 목록을 읽고 새로 만든 함수로 &l필터링&r합니다. "
        "편집기에서 함수를 선택하고 빈 &l변수 카드&r를 넣으면 함수를 &l변수 카드&r에 "
        "&2연산자&0로 저장할 수 있습니다."
    ),
    "info_book.integratedscripting.tutorials.functions.text5": (
        "이번 튜토리얼에서는 필터 함수를 어떤 방식으로 구현해도 됩니다. 아래에 자유롭게 "
        "복사할 수 있는 올바른 예제 스크립트가 있습니다."
    ),
    "info_book.integratedcrafting.introduction.text3": (
        "그런 다음 &l제작 작성기&r를 사용해 네트워크의 모든 &l제작 인터페이스&r가 노출한 "
        "제작법을 바탕으로 제작 작업을 자동 시작할 수 있습니다."
    ),
    "info_book.integratedcrafting.crafting_interface.basics.text4": (
        "게임 후반에는 &l동조된 제작 인터페이스&r를 만들 수 있습니다. 대상 기계에서 사용할 "
        "수 있는 모든 제작법을 읽어 노출하므로 제작법을 직접 추가할 필요가 없습니다. 이는 "
        "&l기계 판독기&r에 나오는 제작법과 같습니다. 일부 모드 기계는 지원하지 않을 수 있으며, "
        "그런 기계에 &l동조된 제작 인터페이스&r를 놓으면 빨간 테두리가 표시됩니다."
    ),
    "info_book.integratedcrafting.crafting_interface.crafting.text2": (
        "제작 작업이 시작되면(예: &l제작 작성기&r 사용) 해당 작업의 제작법을 가진 하나 이상의 "
        "&l제작 인터페이스&r가 사용됩니다. 작업이 끝나기 전에 재료가 다른 곳에서 쓰이지 않도록 "
        "필요한 모든 재료를 네트워크에서 가져와 &l제작 인터페이스&r의 제작 작업에 보관합니다. "
        "&l제작 인터페이스&r는 제작법의 모든 입력을 연결된 기계에 넣으며, &lIntegrated Tunnels "
        "인터페이스&r가 제공하는 저장소 네트워크 내용을 기준으로 작동합니다."
    ),
    "info_book.integratedcrafting.crafting_interface.crafting.text3": (
        "하지만 &l제작 인터페이스&r는 연결된 기계의 제작 결과를 &l가져오지 않습니다&r. 제작 "
        "결과가 네트워크로 돌아오도록 구성하는 일은 플레이어의 몫입니다. 제작대는 예외라서 "
        "&l제작 인터페이스&r만 있으면 됩니다. &l제작 인터페이스&r는 저장소 네트워크의 변화를 "
        "추적하다가 예상 출력이 네트워크에 들어오면 작업을 완료로 표시합니다. 기계에 활성화된 "
        "&lIntegrated Tunnels 입력기&r를 달거나 기계가 &l제작 인터페이스&r로 자동 출력하게 "
        "구성하면 됩니다. &l제작 인터페이스&r에 들어온 모든 것(아이템, 유체, 에너지)은 설정된 "
        "채널의 저장소 네트워크로 들어갑니다."
    ),
    "info_book.integratedcrafting.crafting_interface.recipe_feedback.text3": (
        "&4빨간 X 표시&0는 &l변수 카드&r가 올바른 제작법을 노출하지 않거나 연결된 기계에서 "
        "그 제작법을 처리할 수 없다는 뜻입니다."
    ),
    "info_book.integratedcrafting.crafting_interface.recipe_feedback.text4": (
        "&2초록색 확인 표시&0는 &l변수 카드&r에 올바른 제작법이 &o있고&r 기계가 그 제작법을 "
        "처리할 수 있을 가능성이 높다는 뜻입니다."
    ),
    "info_book.integratedcrafting.crafting_interface.distribution.text2": (
        "분산할 모든 기계의 &l제작 인터페이스&r가 분산하려는 제작법과 정확히 같은 제작법을 "
        "하나 이상 노출하도록 구성하기만 하면 됩니다. 앞의 예라면 용광로 10대 모두의 "
        "&l제작 인터페이스&r에 철 주괴 제련 제작법이 정확히 같게 들어 있어야 합니다."
    ),
    "info_book.integratedcrafting.crafting_interface.blocking.text1": (
        "기본적으로 &l제작 인터페이스&r의 &o차단 모드&r는 켜져 있습니다. 기계는 한 번에 "
        "제작법 하나만 받고, 이전 제작법이 끝나야 다음 제작법을 시작합니다."
    ),
    "info_book.integratedcrafting.crafting_interface.blocking.text2": (
        "여러 입력을 병렬로 처리하는 기계라면 &l제작 인터페이스&r 설정 GUI에서 &o차단 "
        "모드&r를 끌 수 있습니다. 여러 개를 만드는 작업에서 &o차단 모드&r를 끄면 기계가 가능한 "
        "만큼 많은 입력을 함께 처리합니다."
    ),
    "info_book.integratedcrafting.crafting_interface.reusable.text1": (
        "입력 아이템을 완전히 소모하지 않고 내구도 일부만 쓰는 제작법이라면 해당 재료를 "
        "&o재사용 가능&r으로 설정할 수 있습니다. &l논리 프로그래머&r에서 제작법 &l변수 카드&r를 "
        "만들 때 입력 슬롯을 Shift+클릭하고 &o재사용 가능&r 확인란을 켜세요."
    ),
    "info_book.integratedcrafting.tutorials.autocrafting_setup.text2": (
        "자동 제작에는 먼저 &l제작 인터페이스&r가 필요합니다. 제작대나 화로 같은 기계를 "
        "바라보도록 설치하는 네트워크 부품입니다. &l제작 인터페이스&r를 만들고 &l제작대&r를 "
        "바라보게 놓으세요."
    ),
    "info_book.integratedtunnels.concepts.text1": (
        "&lIntegrated Tunnels&r에는 운송 방식마다 &o입력기&r, &o출력기&r, 두 종류의 "
        "&o인터페이스&r까지 네 가지 부품 유형이 있습니다."
    ),
    "info_book.integratedtunnels.concepts.text6": (
        "상대 우선순위를 다르게 지정한 입력기와 출력기를 여러 개 추가할 수도 있습니다."
    ),
    "info_book.integratedtunnels.concepts.text8": (
        "&lIntegrated Crafting&r 같은 자동 제작 모드가 설치되어 있으면 출력기의 &o제작&r "
        "설정을 사용할 수 있습니다. 내보낼 재료가 없을 때 먼저 자동 제작하게 됩니다."
    ),
    "info_book.integratedtunnels.item.text1": (
        "아이템을 네트워크로 옮깁니다. &l아이템 입력기&r는 &l아이템 인터페이스&r가 연결한 "
        "인벤토리의 아이템을 네트워크로 가져오고, &l아이템 출력기&r는 네트워크의 아이템을 "
        "&l아이템 인터페이스&r 쪽으로 내보냅니다. &l필터링 아이템 인터페이스&r를 사용하면 "
        "인터페이스를 통과할 아이템을 동적으로 필터링할 수 있습니다."
    ),
    "info_book.integratedtunnels.fluid.text1": (
        "유체를 네트워크로 옮깁니다. &l유체 입력기&r는 &l유체 인터페이스&r가 연결한 탱크의 "
        "유체를 네트워크로 가져오고, &l유체 출력기&r는 네트워크의 유체를 &l유체 인터페이스&r "
        "쪽으로 내보냅니다. &l필터링 유체 인터페이스&r를 사용하면 인터페이스를 통과할 유체를 "
        "동적으로 필터링할 수 있습니다."
    ),
    "info_book.integratedtunnels.energy.text1": (
        "에너지를 네트워크로 옮깁니다. &l에너지 입력기&r는 &l에너지 인터페이스&r가 연결한 "
        "장치의 에너지를 네트워크로 가져오고, &l에너지 출력기&r는 네트워크의 에너지를 "
        "&l에너지 인터페이스&r 쪽으로 내보냅니다. &l필터링 에너지 인터페이스&r를 사용하면 "
        "에너지가 인터페이스를 통과할지 동적으로 정할 수 있습니다."
    ),
    "info_book.integratedtunnels.world.item.text1": (
        "&l월드 아이템 입력기&r와 &l월드 아이템 출력기&r는 월드에 아이템을 놓거나 줍고, "
        "떨어진 셜커 상자나 당나귀처럼 인벤토리가 있는 엔티티와 상호작용합니다. 애스펙트 "
        "설정으로 발사 여부, 던지는 속도, 줍기 지연, 피치와 요 등을 바꿀 수 있습니다."
    ),
    "info_book.integratedtunnels.world.fluid.text1": (
        "&l월드 유체 입력기&r와 &l월드 유체 출력기&r는 유체 원천 블록을 놓거나 가져오고, "
        "떨어진 탱크 아이템처럼 탱크 역할을 하는 엔티티와 상호작용합니다. 애스펙트 설정으로 "
        "블록 업데이트 발생 여부 등을 바꿀 수 있습니다."
    ),
    "info_book.integratedtunnels.world.energy.text1": (
        "&l월드 에너지 입력기&r와 &l월드 에너지 출력기&r는 떨어진 배터리처럼 에너지 버퍼가 "
        "있는 엔티티와 상호작용할 수 있게 해 줍니다."
    ),
    "info_book.integratedtunnels.world.block.text1": (
        "&l월드 블록 입력기&r와 &l월드 블록 출력기&r로 블록을 부수고 놓을 수 있습니다. "
        "섬세한 손길 적용 여부 같은 여러 애스펙트 설정도 사용할 수 있습니다."
    ),
    "info_book.integratedtunnels.tutorials.interfaces.text1": (
        "&o인터페이스&r는 &l케이블&r에 부착하는 부품입니다. 아이템, 유체, 에너지용이 각각 "
        "인벤토리, 탱크, 에너지 장치에 연결됩니다. 인터페이스는 연결 대상을 네트워크에서 "
        "사용할 수 있게 합니다. 이때 &o인터페이스&r를 통해 접근합니다."
    ),
    "info_book.integratedtunnels.tutorials.importer_exporter.text1": (
        "&o아이템 입력기&r는 대상의 아이템을 &o아이템 인터페이스&r 중 하나로 옮깁니다. "
        "&o아이템 출력기&r는 반대로 &o아이템 인터페이스&r의 아이템을 대상으로 옮깁니다."
    ),
    "info_book.integratedtunnels.tutorials.place_logwood": "태그로 아이템 배치",
    "aspect.integrateddynamics.read.itemstack.charsetpipe.content": "파이프 아이템",
    "aspect.integrateddynamics.read.list.charsetpipe.contents": "파이프 아이템 목록",
    "aspect.integrateddynamics.read.itemstack.charsetpipe.content.info": (
        "현재 이 파이프를 통과하는 아이템입니다."
    ),
    "aspect.integrateddynamics.read.list.charsetpipe.contents.info": (
        "현재 이 파이프를 통과하는 아이템 목록입니다."
    ),
    "aspect.integrateddynamics.write.itemstack.charsetpipe.shifter.info": (
        "주어진 아이템의 파이프 이동을 활성화합니다."
    ),
    "aspect.integrateddynamics.write.list.charsetpipe.shifter.info": (
        "주어진 아이템 목록의 파이프 이동을 활성화합니다."
    ),
    "aspect.integrateddynamics.read.list.thaumcraft.aspectcontainer": (
        "위상 컨테이너 위상 목록"
    ),
    "aspect.integrateddynamics.read.thaumcraftaspect.thaumcraft.aspectcontainer": (
        "위상 컨테이너 위상"
    ),
    "aspect.integrateddynamics.read.list.refinedstorage.inventory.craftingitems": (
        "RS 제작 아이템 목록"
    ),
    "aspect.integrateddynamics.write.itemstack.refinedstorage.craft": "RS 아이템 제작",
    "aspect.integrateddynamics.write.list.refinedstorage.craft": "RS 아이템 목록 제작",
    "aspect.integrateddynamics.write.itemstack.refinedstorage.cancelcraft.info": (
        "RS 네트워크에서 해당 아이템의 실행 중인 모든 제작 작업을 취소합니다."
    ),
    "aspect.integrateddynamics.write.list.refinedstorage.cancelcraft.info": (
        "RS 네트워크에서 해당 아이템 목록의 실행 중인 모든 제작 작업을 취소합니다."
    ),
    "info_book.integratedtunnels.tutorials.import_all_items.text1": (
        "&l아이템 입력기&r에 빈 &l변수 카드&r를 넣어 대상 인벤토리의 모든 아이템을 "
        "네트워크로 가져오세요."
    ),
    "info_book.integratedtunnels.tutorials.import_items_list.text1": (
        "특정 목록의 모든 아이템을 대상 인벤토리로 가져오세요. &l인벤토리 판독기&r에서 "
        "목록을 읽어 아이템 목록을 만들 수 있습니다."
    ),
    "info_book.integratedtunnels.tutorials.filter_storage_day.text1": (
        "&l필터링 아이템 인터페이스&r로 &l상자&r를 네트워크에 연결하고, 낮일 때만 상자 "
        "내용을 네트워크에서 사용할 수 있게 만드세요."
    ),
    "info_book.integratedtunnels.tutorials.filter_storage_mod.text1": (
        "&l필터링 아이템 인터페이스&r로 &l상자&r를 네트워크에 연결하고 &lIntegrated "
        "Dynamics&r 모드의 아이템만 통과시키는 술어 기반 필터를 구성하세요. 이를 위해 "
        "&8아이템&0을 입력받아 &9불리언&0을 출력하는 새 연산자를 만듭니다."
    ),
    "info_book.integratedtunnels.tutorials.filter_storage_mod.text2": (
        "먼저 &l관계형 같음&r 연산자가 든 &2연산자&0 값을 만드세요. 다음으로 공백 없는 "
        "&lIntegratedDynamics&r 값이 든 &4문자열&0을 만듭니다. &l적용&r 연산자로 "
        "&l관계형 같음&r 연산자에 이 &4문자열&0 값을 부분 적용하세요."
    ),
    "info_book.integratedtunnels.tutorials.filter_storage_mod.text3": (
        "이제 &l아이템 모드&r 연산자가 든 또 다른 &2연산자&0 값을 만드세요. &l파이프&r "
        "연산자를 사용해 &l아이템 모드&r 연산자의 출력을 이전 단계에서 부분 적용한 연산자로 "
        "보낼 수 있습니다."
    ),
    "info_book.integratedtunnels.tutorials.filter_storage_mod.text4": (
        "&l파이프&r 연산자의 결과를 &l필터링 아이템 인터페이스&r의 술어 기반 애스펙트에 "
        "넣고, 의존하는 모든 변수는 &l변수 저장소&r에 넣으세요. 올바르게 구성했다면 필터는 "
        "&lIntegrated Dynamics&r 모드의 아이템만 통과시키며, &4문자열&0 상수를 바꾸어 대상 "
        "모드를 변경할 수 있습니다."
    ),
    "info_book.integratedtunnels.tutorials.world_block_importer_exporter.text1": (
        "월드에 아이템을 떨어뜨리거나 줍는 대신 &l월드 블록 입력기&r와 &l월드 블록 출력기&r로 "
        "블록을 부수고 놓을 수도 있습니다. 블록을 부술 때 섬세한 손길을 적용할지 같은 여러 "
        "애스펙트 설정을 사용할 수 있습니다."
    ),
    "info_book.integrateddynamics.manual.logic.advanced.nbt_path.text10": (
        "필터 구문으로 &4[?(@.childName < 10)]&0 같은 고급 필터 표현식도 사용할 수 있습니다. "
        "(@는 현재 태그, ..는 상위 태그, $는 루트 태그를 뜻합니다.)"
    ),
    "info_book.integrateddynamics.manual.logic.advanced.nbt_path.text11": (
        "예를 들어 &3NBT&0 태그 &3{ a: [0,1,2,3,4,5] }&0에 "
        "&4”$.a[?(@ == 3)]”&0 표현식을 적용하면 &3[3]&0이 출력됩니다."
    ),
    "info_book.integrateddynamics.manual.logic.advanced.nbt_path.text12": (
        "표현식은 ”&&”(AND), ”||”(OR), ”!”(NOT)로 조합할 수 있습니다."
    ),
    "info_book.integrateddynamics.manual.logic.advanced.nbt_path.text13": (
        "예를 들어 &3NBT&0 태그 &3{ a: [0,1,2,3,4,5] }&0에 "
        "&4”$.a[?(@ == 3 || (@ == 5))]”&0 표현식을 적용하면 &3[3,5]&0가 출력됩니다."
    ),
    "info_book.integrateddynamics.manual.logic_programming.text4": (
        "&l변수 카드&r에 새 값을 쓰는 것뿐 아니라 &l논리 프로그래머&r로 기존 "
        "&l변수 카드&r를 수정할 수도 있습니다. 기존 &l변수 카드&r를 오른쪽 슬롯에 넣으면 "
        "그 값을 &l논리 프로그래머&r로 불러옵니다. 이때 왼쪽의 &l연산자&r와 &l자료형&r은 "
        "선택하지 않아야 합니다. 처음 &l논리 프로그래머&r를 열었을 때가 이 상태이며, "
        "현재 선택을 지워 이 상태로 돌아갈 수도 있습니다."
    ),
    "operator.integrateddynamics.error.operator_nbt_path_expression": (
        "잘못된 NBT 경로 표현식입니다. '%s': %s"
    ),
    "info_book.integrateddynamics.tutorials.aspects.text2": (
        "월드의 &l논리 케이블&r에 &l레드스톤 판독기&r를 부착하세요. 판독기가 "
        "&l레드스톤 횃불&r처럼 레드스톤 값을 가진 대상을 향하는지 확인하세요."
    ),
    "info_book.integrateddynamics.tutorials.aspects.text4": (
        "이제 &l레드스톤 판독기&r와 같은 네트워크에 &l디스플레이 패널&r을 놓고, "
        "연결한 &l변수 카드&r를 넣어 값을 표시하세요."
    ),
    "info_book.integrateddynamics.tutorials.advancedOperations.text5": (
        "이 튜토리얼의 마지막 단계에서는 동적 변수와 연산자를 조합합니다. 네트워크에 "
        "&l엔티티 판독기&r를 부착해 대상 &7엔티티&0를 읽고, 그 &7엔티티&0가 바라보는 "
        "&7블록&0을 가져와 그 &7블록&0을 &l디스플레이 패널&r에 표시하세요."
    ),
    "info_book.integrateddynamics.manual.logic.value_types.list.text1": (
        "특정 &l자료형&r의 값을 담는 목록입니다. 한 목록의 모든 원소는 같은 자료형이어야 "
        '합니다. 예: &8(0, 1, 2, 3)&0, &8("a", "b", "c")&0, '
        "&8(3.33, 1.14, 5, 6)&0"
    ),
    "info_book.integrateddynamics.manual.logic.variables.variable_card.text2": (
        "변수는 정적이거나 동적일 수 있습니다. 정적 변수는 한 번 정의되면 바뀌지 않습니다. "
        "동적 변수는 &l논리 평가&r의 결과이며, 이 평가는 &l연산자&r 또는 "
        "&l판독기 애스펙트&r가 수행합니다. 계속 변하는 &lMinecraft&r 월드의 시간은 동적 "
        "변수의 한 예입니다."
    ),
    "info_book.integrateddynamics.manual.logic_programming.text1": (
        "동적 &l변수 카드&r를 만드는 또 다른 방법은 하나 이상의 &l변수 카드&r에 "
        "&l연산자&r를 적용해 새 &l변수 카드&r를 만드는 것입니다. 예를 들어 두 "
        "&l숫자&r를 더해 새로운 &l숫자&r를 만들 수 있습니다."
    ),
    "info_book.integrateddynamics.manual.logic_programming.text2": (
        "&l연산자&r는 하나 이상의 입력값과 하나의 출력값을 가집니다. 보통 입출력마다 "
        "정해진 &l자료형&r이 있으며, 제한이 없으면 &l모든 유형&r을 받습니다. 입력 하나와 "
        "&l불리언&r 출력 하나를 갖는 &l연산자&r를 &l술어&r라고 합니다."
    ),
    "info_book.integrateddynamics.manual.logic_programming.text5": (
        "&l논리 프로그래머&r 상단의 검색창에서 이름으로 &l연산자&r를 찾을 수 있습니다. "
        "왼쪽 아래 슬롯에 원하는 자료형의 &l변수 카드&r를 넣으면 입출력 자료형으로도 "
        "목록을 걸러낼 수 있습니다."
    ),
    "info_book.integrateddynamics.manual.parts.introduction.text1": (
        "&l논리 케이블&r의 각 면에는 부품을 놓을 수 있습니다. 이 장에서는 &l값&r을 읽어 "
        "&l변수 카드&r에 저장하는 부품과, &l변수 카드&r 안의 &l값&r을 바탕으로 작업을 "
        "수행하는 부품을 설명합니다."
    ),
    "info_book.integrateddynamics.manual.parts.introduction.text2": (
        "대부분의 부품은 GUI 왼쪽 위 버튼에서 설정할 수 있습니다. &l틱/작업&r은 부품이 "
        "몇 틱마다 작업할지를 정합니다. &l우선순위&r는 같은 네트워크의 부품들이 같은 틱에 "
        "작동할 순서를 정합니다. 예를 들어 부품 A의 우선순위가 -1이고 부품 B가 1이면 "
        "B가 항상 A보다 먼저 작동합니다. 우선순위가 같으면 순서는 무작위입니다."
    ),
    "info_book.integrateddynamics.manual.parts.reader.introduction.text1": (
        "동적 변수를 만드는 가장 간단한 방법은 &l판독기&r를 사용하는 것입니다. 여러 종류의 "
        "판독기가 월드의 정보를 읽어 &l변수 카드&r에 저장합니다. 각 &l판독기&r에는 서로 "
        "다른 &l자료형&r의 값을 읽는 하나 이상의 &l애스펙트&r가 있습니다."
    ),
    "info_book.integrateddynamics.manual.parts.settings.text3": (
        "틱/작업에서는 이 부품이 몇 틱마다 작동할지를 설정합니다. 값이 클수록 작동 속도가 "
        "느려집니다."
    ),
    "info_book.integrateddynamics.manual.machines.mechanical_squeezer.text1": (
        "&l압착기&r를 쓰려고 여러 번 뛰다 보면 자동화가 그리워질 때가 옵니다. 아직 "
        "&l압착기&r를 자동화하지 않았다면 &l기계식 압착기&r를 만들어 보세요. 직접 밟을 "
        "필요는 없지만 작동에는 에너지가 필요합니다. 일반 &l압착기&r보다 훨씬 빠르고 "
        "수율도 높습니다."
    ),
    "info_book.integratedcrafting.crafting_interface.dynamic_recipes.text3": (
        "제작법이 자주 바뀔수록 지연이 더 많이 발생할 수 있으니 이 기능은 주의해서 "
        "사용하세요."
    ),
    "info_book.integratedcrafting.tutorials.autocrafting_trigger.text2": (
        "먼저 &l제작 작성기&r를 제작하세요. 이 부품은 지정한 제작법, 아이템, 유체 또는 "
        "에너지의 제작 작업을 자동으로 시작합니다. 제작한 뒤 이전 튜토리얼의 "
        "&l제작 인터페이스&r가 있는 네트워크 아무 곳에나 설치하세요."
    ),
    "info_book.integratedcrafting.tutorials.autocrafting_trigger.text3": (
        "&l제작 작성기&r로 참나무 판자를 제작하기 전에 네트워크에 참나무 원목을 넣어야 "
        "합니다. &lIntegrated Tunnels&r의 &l아이템 인터페이스&r로 상자 같은 저장소를 "
        "네트워크에 연결하고, 상자에 참나무 원목이 하나 이상 있는지 확인하세요."
    ),
    "advancement.integrateddynamics.recipe_creation.desc": (
        "논리 프로그래머로 §8제작법§7을 직접 만드세요."
    ),
    "advancement.integrateddynamics.recipe_reading.desc": (
        "기계 판독기로 제작대 같은 기계의 제작법 목록을 읽으세요."
    ),
    "advancement.integrateddynamics.logical_list_building.desc": (
        "§6정수§7 1, 10, 100을 담은 정적 목록을 만드세요."
    ),
    "advancement.integrateddynamics.recursive_recursion.desc": (
        "무한 목록을 만들고 디스플레이 패널에 표시하세요."
    ),
    "advancement.integrateddynamics.redstone_transmission.desc": (
        "레드스톤 작성기가 레드스톤 판독기로 읽은 최대 정수 레드스톤 신호 세기를 "
        "출력하게 하세요."
    ),
    "advancement.integrateddynamics.what_would_i_be_looking_at.desc": (
        "바라보고 있는 블록을 가져오세요."
    ),
    "aspect.integrateddynamics.read.boolean.fluid.empty": "빈 탱크",
    "aspect.integrateddynamics.read.boolean.fluid.empty.info": (
        "대상 유체 탱크가 비어 있는지 여부"
    ),
    "aspect.integrateddynamics.read.boolean.fluid.nonempty": "비어 있지 않은 탱크",
    "aspect.integrateddynamics.read.boolean.fluid.nonempty.info": (
        "대상 유체 탱크에 유체가 있는지 여부"
    ),
    "aspect.integrateddynamics.read.boolean.inventory.full.info": (
        "모든 슬롯에 아이템이 하나 이상 있는지 여부"
    ),
    "aspect.integrateddynamics.read.boolean.inventory.empty": "빈 인벤토리",
    "aspect.integrateddynamics.read.boolean.inventory.empty.info": (
        "모든 슬롯이 비어 있는지 여부"
    ),
    "aspect.integrateddynamics.read.boolean.inventory.nonempty": (
        "비어 있지 않은 인벤토리"
    ),
    "aspect.integrateddynamics.read.double.inventory.fillratio.info": (
        "비어 있지 않은 슬롯 수를 전체 슬롯 수로 나눈 값"
    ),
    "aspect.integrateddynamics.read.boolean.fe.isempty": "빈 FE 버퍼",
    "aspect.integrateddynamics.read.boolean.fe.isempty.info": (
        "대상의 FE 버퍼가 완전히 비어 있는지 여부"
    ),
    "aspect.integrateddynamics.read.boolean.fe.isnonempty": "비어 있지 않은 FE 버퍼",
    "aspect.integrateddynamics.read.boolean.fe.isnonempty.info": (
        "대상의 FE 버퍼가 비어 있지 않은지 여부"
    ),
    "aspect.integrateddynamics.read.operator.recipehandler.recipesbyinput.info": (
        "주어진 입력으로 만들 수 있는 모든 제작법을 반환하는 연산자."
    ),
    "aspect.integrateddynamics.read.operator.recipehandler.recipesbyoutput.info": (
        "주어진 출력이 나오는 모든 제작법을 반환하는 연산자."
    ),
    "operator.integrateddynamics.string.regex_groups.info": (
        "주어진 문자열에서 정규식을 검색하고 일치한 모든 그룹의 목록을 반환합니다."
    ),
    "operator.integrateddynamics.string.join.info": (
        "주어진 문자열 목록을 지정한 구분자로 이어 새 문자열을 만듭니다."
    ),
    "operator.integrateddynamics.string.name.info": (
        "이름 있는 객체의 문자열이나 이름을 가져오거나 객체를 문자열로 변환합니다."
    ),
    "operator.integrateddynamics.string.unique_name.info": "객체의 고유 이름을 가져옵니다.",
    "operator.integrateddynamics.list.empty": "비어 있음",
    "operator.integrateddynamics.list.empty.info": "목록이 비어 있는지 여부",
    "operator.integrateddynamics.list.notempty": "비어 있지 않음",
    "operator.integrateddynamics.list.notempty.info": "목록이 비어 있지 않은지 여부",
    "operator.integrateddynamics.list.contains.info": (
        "목록에 주어진 요소가 들어 있는지 여부."
    ),
    "operator.integrateddynamics.list.lazybuilt.info": (
        "시작값과 이전 요소에 적용해 다음 요소를 만드는 연산자로 목록을 지연 생성합니다."
    ),
    "operator.integrateddynamics.list.slice.info": (
        "주어진 목록에서 시작 인덱스는 포함하고 끝 인덱스는 제외한 부분 목록을 가져옵니다."
    ),
    "operator.integrateddynamics.number.cast_double": "숫자를 실수로 변환",
    "operator.integrateddynamics.number.cast_double.info": "임의의 숫자를 실수로 변환",
    "operator.integrateddynamics.number.cast_long": "숫자를 긴 정수로 변환",
    "operator.integrateddynamics.number.cast_long.info": "임의의 숫자를 긴 정수로 변환",
    "operator.integrateddynamics.number.cast_integer.info": "임의의 숫자를 정수로 변환",
    "operator.integrateddynamics.nbt.compound_value_list_byte": (
        "NBT 복합 태그의 Byte 배열 값"
    ),
    "operator.integrateddynamics.nbt.compound_value_list_byte.info": (
        "주어진 NBT 복합 태그에서 지정한 키의 Byte 배열을 정수 목록으로 가져옵니다."
    ),
    "operator.integrateddynamics.nbt.compound_value_list_int.info": (
        "주어진 NBT 복합 태그에서 지정한 키의 정수 배열을 정수 목록으로 가져옵니다."
    ),
    "operator.integrateddynamics.nbt.compound_value_list_long": (
        "NBT 복합 태그의 Long 배열 값"
    ),
    "operator.integrateddynamics.nbt.compound_value_list_long.info": (
        "주어진 NBT 복합 태그에서 지정한 키의 Long 배열을 Long 목록으로 가져옵니다."
    ),
    "operator.integrateddynamics.nbt.compound_with_long.info": (
        "주어진 NBT 복합 태그에 지정한 Long 항목을 넣은 사본을 가져옵니다."
    ),
    "operator.integrateddynamics.nbt.compound_with_double.info": (
        "주어진 NBT 복합 태그에 지정한 Double 항목을 넣은 사본을 가져옵니다."
    ),
    "operator.integrateddynamics.nbt.compound_with_float.info": (
        "주어진 NBT 복합 태그에 지정한 Double 값을 Float 항목으로 넣은 사본을 "
        "가져옵니다."
    ),
    "operator.integrateddynamics.nbt.compound_with_list_byte": (
        "정수 목록을 포함한 NBT 복합 태그"
    ),
    "operator.integrateddynamics.nbt.compound_with_list_byte.info": (
        "주어진 정수 목록을 NBT Byte 배열 항목으로 넣은 NBT 복합 태그의 사본을 "
        "가져옵니다."
    ),
    "operator.integrateddynamics.nbt.compound_with_list_long": (
        "Long 목록을 포함한 NBT 복합 태그"
    ),
    "operator.integrateddynamics.nbt.compound_with_list_long.info": (
        "주어진 NBT Long 배열 항목을 넣은 NBT 복합 태그의 사본을 가져옵니다."
    ),
    "operator.integrateddynamics.nbt.as_string": "NBT 문자열을 문자열로 변환",
    "operator.integrateddynamics.nbt.as_tag_list": "NBT 목록을 NBT 목록으로 변환",
    "operator.integrateddynamics.nbt.as_byte_list": (
        "NBT Byte 배열을 Byte 목록으로 변환"
    ),
    "operator.integrateddynamics.nbt.as_int_list": (
        "NBT 정수 배열을 정수 목록으로 변환"
    ),
    "operator.integrateddynamics.nbt.as_long_list": (
        "NBT Long 배열을 Long 목록으로 변환"
    ),
    "operator.integrateddynamics.nbt.from_boolean": "불리언에서 NBT Byte 만들기",
    "operator.integrateddynamics.nbt.from_byte": "정수에서 NBT Byte 만들기",
    "operator.integrateddynamics.nbt.from_long": "Long에서 NBT Long 만들기",
    "operator.integrateddynamics.nbt.from_double": "Double에서 NBT Double 만들기",
    "operator.integrateddynamics.nbt.from_float": "Double에서 NBT Float 만들기",
    "operator.integrateddynamics.nbt.from_float.info": (
        "주어진 Double 값에서 NBT Float 태그를 만듭니다."
    ),
    "operator.integrateddynamics.nbt.from_tag_list": "태그 목록에서 NBT 목록 만들기",
    "operator.integrateddynamics.nbt.from_byte_list": (
        "Byte 목록에서 NBT Byte 배열 만들기"
    ),
    "operator.integrateddynamics.nbt.from_long_list": (
        "Long 목록에서 NBT Long 배열 만들기"
    ),
    "operator.integrateddynamics.nbt.path_match_all.info": (
        "주어진 NBT 값에 NBT 경로 표현식을 적용하고 일치하는 모든 값을 목록으로 "
        "반환합니다."
    ),
    "operator.integrateddynamics.ingredients.with_items": "아이템을 포함한 재료",
    "operator.integrateddynamics.ingredients.with_items.info": (
        "주어진 재료의 지정한 위치에 아이템 목록을 넣은 사본을 가져옵니다."
    ),
    "operator.integrateddynamics.ingredients.with_fluids": "유체를 포함한 재료",
    "operator.integrateddynamics.ingredients.with_fluids.info": (
        "주어진 재료의 지정한 위치에 유체 목록을 넣은 사본을 가져옵니다."
    ),
    "operator.integrateddynamics.ingredients.with_energies.info": (
        "주어진 재료의 지정한 위치에 에너지 요소 목록을 넣은 사본을 가져옵니다."
    ),
    "operator.integrateddynamics.general.choice.info": (
        "첫 번째 값이 참이면 두 번째 값을, 그렇지 않으면 세 번째 값을 가져옵니다.\\n"
        "두 번째와 세 번째 값의 자료형은 같아야 합니다."
    ),
    "info_book.integrateddynamics.manual.logic.variables.variable_card.text3": (
        "동적 변수는 &l디스플레이 패널&r에 값을 표시하거나 다른 동적 변수 평가에 "
        "필요해지는 등, 값이 요청될 때만 평가됩니다."
    ),
    "info_book.integrateddynamics.manual.networks.text2": (
        "&l논리 케이블&r을 숨기고 싶다면 어떤 재료의 모양도 흉내 낼 수 있는 "
        "&l덮개&r를 사용하세요. 케이블은 &lMC MultiPart&r와도 호환되므로 더 복잡한 "
        "덮개 구조 안에 숨길 수 있습니다."
    ),
    "info_book.integrateddynamics.manual.parts.settings.text1": (
        "대부분의 부품에는 기본 동작을 바꾸는 &l설정&r 화면이 있습니다."
    ),
    "info_book.integrateddynamics.manual.machines.delay.text2": (
        "&l지연기&r를 사용하면 지정한 변수 값의 이력을 유지할 수 있습니다. 이력을 남길 "
        "&l변수 카드&r를 위쪽 슬롯에 넣으세요. 그러면 이력에 해당하는 값 목록을 참조하는 "
        "&l변수 카드&r를 만들 수 있습니다. 지연기가 작동하려면 참조된 카드나 다른 "
        "&l변수 카드&r가 위쪽 슬롯에 계속 있어야 합니다."
    ),
    "info_book.integrateddynamics.manual.logic_programming.text6": (
        "플레이어의 인벤토리에 &l라벨러&r가 있으면 출력 슬롯 옆의 'E' 버튼을 눌러 결과 "
        "&l변수 카드&r에 즉시 라벨을 붙일 수 있습니다."
    ),
    "info_book.integrateddynamics.tutorials.logicOperations.text3": (
        "다음으로 &6정수&0 연산자를 찾아 클릭하고 열린 창에 숫자를 입력하세요. 빈 "
        "&l변수 카드&r를 넣어 이 &6정수&0를 &l변수 카드&r에 저장한 뒤, 다른 "
        "&6정수&0도 같은 방법으로 하나 더 만드세요."
    ),
    "info_book.integrateddynamics.tutorials.logicOperations.text4": (
        "마지막으로 &l덧셈&r 연산자를 찾아 여세요. 이 연산자는 &e숫자&0 두 개를 더합니다. "
        "&6정수&0 &l변수 카드&r 두 장을 입력 슬롯에 넣고 결과를 새 "
        "&l변수 카드&r에 저장하세요."
    ),
    "info_book.integrateddynamics.tutorials.recipe_handling.text2": (
        "&8제작법&0을 얻는 가장 쉬운 방법은 제작법을 처리하는 기계에서 직접 읽는 "
        "것입니다. &l기계 판독기&r를 &l제작대&r에 붙이고 제작법 목록을 읽어 모든 조합 "
        "제작법을 가져오세요."
    ),
    "info_book.integrateddynamics.tutorials.recipe_handling.text3": (
        "제작법을 더 세밀하게 제어하거나 &l기계 판독기&r로 제작법을 공개하지 않는 "
        "기계를 사용한다면, &l논리 프로그래머&r에서 &8제작법&0을 직접 만들 수 있습니다. "
        "예시로 간단한 &l상자&r 제작법을 만들어 보세요."
    ),
    "info_book.integrateddynamics.tutorials.recipe_handling.text4": (
        "마지막으로 제작법 읽기를 한 단계 확장합니다. &l출력으로 제작법 찾기&r "
        "애스펙트는 &8재료&0 값에 적용했을 때 그 &8재료&0가 출력되는 첫 번째 "
        "&8제작법&0을 반환하는 연산자를 제공합니다. 이 연산자로 &l상자&r 제작법을 "
        "찾아보세요."
    ),
    "info_book.integrateddynamics.tutorials.recipe_handling.text5": (
        "먼저 &l논리 프로그래머&r에서 &8상자&0 하나가 든 &8재료&0 값을 만드세요. "
        "&l제작대&r를 바라보는 &l기계 판독기&r에서 &l출력으로 제작법 찾기&r 애스펙트를 "
        "읽고, &o적용&r 연산자로 &l상자&r &8재료&0를 &l기계 판독기&r에서 얻은 연산자에 "
        "적용하세요. 결과 변수를 &l디스플레이 패널&r에 넣으면 &l상자&r 제작법이 "
        "표시됩니다. 사용한 모든 변수는 &l변수 저장소&r에 넣어 두세요."
    ),
    "info_book.integrateddynamics.tutorials.recipe_handling.text6": (
        "&8제작법&0과 &8재료&0로 할 수 있는 일은 훨씬 많습니다. 다른 고급 기능은 "
        "&l기계 판독기&r와 &l논리 프로그래머&r에서 살펴보세요."
    ),
    "info_book.integrateddynamics.tutorials.theValueOfOperators.text2": (
        "먼저 &l논리 프로그래머&r에서 새 정적 &2연산자&0를 만들려면 자동 완성 목록에서 "
        "&o산술 덧셈&r &2연산자&0를 찾아 &l변수 카드&r에 저장하고, &6정수&0 변수 두 "
        "개를 만드세요. &o적용&r 연산자로 첫 번째 &6정수&0를 &2연산자&0에 적용하면 "
        "&2덧셈 연산자&0의 첫 입력이 그 &6정수&0에 &o바인딩&r되고 입력 하나가 남은 새 "
        "&2연산자&0가 나옵니다. 새 &2연산자&0의 마지막 입력도 &o적용&r 연산자로 "
        "&o바인딩&r한 뒤, 결과를 &l디스플레이 패널&r에 표시하세요."
    ),
    "info_book.integrateddynamics.tutorials.theValueOfOperators.text3": (
        "&2연산자&0를 적용하는 것 외에도 여러 고급 &2연산자&0 작업이 있습니다. 여기서는 "
        "&2연산자&0를 &7목록&0에 사용하는 방법, 구체적으로 &7목록&0과 &o술어&r, 즉 입력 "
        "하나를 받아 &9불리언&0을 출력하는 &2연산자&0를 사용하는 &o필터&r "
        "&2연산자&0를 살펴봅니다. 먼저 &6정수&0 &61&0, &610&0, &6100&0이 든 "
        "&7목록&0을 만드세요. &o관계형 같음&r &2연산자&0를 변수에 저장하고 &6정수&0 "
        "&610&0을 적용한 다음, 이 적용한 &2연산자&0와 &7목록&0을 &o필터&r "
        "&2연산자&0에 넣으세요. &7목록&0의 각 요소에 연산자를 적용했을 때 &9거짓&0이 "
        "나오는 항목, 즉 &610&0과 다른 모든 요소가 목록에서 제거됩니다. 결과를 "
        "&l디스플레이 패널&r에 표시하세요."
    ),
    "info_book.integrateddynamics.manual.logic.value_types.operator.text2": (
        "예를 들어 덧셈 &2연산자&0를 변수 카드에 저장할 수 있습니다. 자동 완성 목록에서 "
        "연산자를 찾아 선택한 뒤 카드에 쓰세요. &6정수&0 &l변수 카드&r 하나를 부분 "
        "적용하면, 적용한 &6정수&0를 내부에서 참조하며 입력 하나와 출력 하나가 남은 새 "
        "가상 연산자가 만들어집니다. 여기에 다른 &6정수&0를 적용하면 &6정수&0 결과가 "
        "나옵니다."
    ),
    "info_book.integrateddynamics.manual.logic.value_types.operator.text3": (
        "&l논리 프로그래머&r에는 목록을 하나의 값으로 축소하거나 &l술어&r로 목록을 "
        "필터링하는 등 고급 평가에 쓰는 &2연산자&0도 있습니다."
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.item.checkstacksize.info": (
        "한 틱에 지정한 스택 크기만 정확히 옮길지 여부(더 적은 수량은 옮기지 않음)."
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.item.nbtrecursive.info": (
        "중첩된 NBT 태그와 목록을 재귀적으로 확인할지 여부."
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.fluid.checkamount.info": (
        "한 틱에 지정한 유체량만 정확히 옮길지 여부(더 적은 양은 옮기지 않음)."
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.fluid.nbtrecursive.info": (
        "중첩된 NBT 태그와 목록을 재귀적으로 확인할지 여부."
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.energy.checkamount.info": (
        "한 틱에 지정한 에너지양만 정확히 옮길지 여부(더 적은 양은 옮기지 않음)."
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.world.ignorereplacable": (
        "교체 가능한 블록 무시"
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.player.continuousclick.info": (
        "클릭을 계속 누르는 동작을 재현할지 여부. 끄면 클릭할 때마다 1틱이 걸립니다."
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.blacklist": "차단 목록",
    "aspect.aspecttypes.integratedtunnels.boolean.blacklist.info": (
        "주어진 목록의 아이템을 제외한 나머지만 처리할지 여부."
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.player.sneak.info": (
        "플레이어가 Shift를 눌러 웅크리는 동작을 재현할지 여부."
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.emptyisany.info": (
        "빈 값이 모든 대상과 일치할지 여부. 끄면 아무 대상과도 일치하지 않습니다."
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.craft.info": (
        "대상이 네트워크에 없을 때 제작할지 여부."
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.filter.applytoinsert.info": (
        "네트워크에 삽입할 때 필터를 적용할지 여부."
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.filter.applytoextract.info": (
        "네트워크에서 추출하거나 표시할 때 필터를 적용할지 여부."
    ),
    "aspect.aspecttypes.integratedtunnels.boolean.filter.allowallifnotapplied.info": (
        "삽입이나 추출에 필터를 적용하지 않을 때 모든 재료를 통과시킬지 여부."
    ),
    "aspect.integratedtunnels.read.list.itemnetwork.itemstacks.info": (
        "네트워크에 있는 모든 아이템의 목록을 가져옵니다."
    ),
    "aspect.integratedtunnels.read.list.fluidnetwork.fluidstacks.info": (
        "네트워크에 있는 모든 유체의 목록을 가져옵니다."
    ),
    "info_book.integratedtunnels.introduction.text2": (
        "&lIntegrated Dynamics&r 논리로 원하는 만큼 복잡한 필터를 구성할 수 있습니다. "
        '&o"매 틱마다 내구도 손상이 10 미만인 마법 부여 가능 곡괭이 3개를 이 상자로 '
        '보내기"&r나 &o"기계가 작동 중이고 이 상자에 철 주괴가 10개 미만일 때만 '
        '탱크에 기름이 1000mB 찰 때까지 채우기"&r도 문제없습니다. &lIntegrated '
        "Tunnels&r가 효율적으로 처리합니다!"
    ),
    "info_book.integratedtunnels.player.text1": (
        "경험 많은 Minecraft 플레이어라면 클릭이 적을수록 좋다는 것을 압니다. "
        "&l플레이어 시뮬레이터&r는 어느 손과 아이템으로 클릭할지 정해 반복 클릭을 "
        "자동화합니다. 고급 속성에서는 클릭 위치 같은 세부 설정도 바꿀 수 있습니다."
    ),
}

QUEST_KEY_OVERRIDES = {
    "quest.232A06C9FF0EE7B2.quest_desc": (
        "멘릴 씨앗으로 멘릴 열매, 멘릴 원목, 멘릴 묘목 생산을 자동화할 수 있습니다."
    ),
    "quest.1B5C86AE05678420.quest_desc": (
        "인터페이스를 우클릭하면 여러 옵션이 나타납니다. 각 기능은 다음과 같습니다.\n\n"
        "&l면 설정&r: 화면 위쪽에서 인터페이스가 어느 면에 있는 것처럼 작동할지 정합니다. "
        "입력·출력 면이 정해진 기계에 유용합니다.\n\n&l틱/작업&r: 10틱/작업으로 "
        "설정하면 10틱(0.5초)마다 한 번 입력하거나 출력합니다.\n\n&l우선순위&r: "
        "우선순위가 더 높은 인터페이스의 인벤토리로 아이템을 먼저 보냅니다.\n\n"
        "&l아이템/에너지 채널&r: 시스템을 여러 채널로 나누어 네트워크의 서로 다른 "
        "위치에서 입력하고 출력할 수 있습니다."
    ),
    "quest.4D62C62B523C69EC.quest_desc": (
        "발전기는 석탄처럼 연소 가능한 연료로 FE를 생성합니다."
    ),
    "quest.03C40D6A5D722543.quest_desc": (
        "변수 카드는 아이템 입력 같은 상호작용을 시작하는 데 필요합니다. 입력기의 슬롯에 "
        "변수 카드를 넣으세요.\n\n카드 옆의 '+' 버튼에서 입력량, 대상 아이템 슬롯, 채널 "
        "등 거의 모든 설정을 바꿀 수 있습니다.\n\n아이템을 단순히 옮기기만 한다면 카드를 "
        "넣고 필요할 때 전송량 제한만 조절하면 됩니다."
    ),
    "quest.499CF9F39CED8899.title": "&bIntegrated Dynamics",
    "quest.499CF9F39CED8899.quest_desc": (
        "&bIntegrated Dynamics&r(ID)는 저장과 아이템·에너지·유체 운송 등에 쓰는 물류 "
        "모드입니다!\n\n멘릴 나무는 메네글린 생물군계에서 찾을 수 있습니다.\n\n이 퀘스트에서는 "
        "모드의 기본 개념을 다룹니다. 더 자세히 알고 싶다면 이 퀘스트 보상으로 받은 가이드를 "
        "읽어 보세요."
    ),
    "quest.33F4A7613764A016.quest_desc": (
        "입력기와 같은 방식으로 작동하지만, 반대로 네트워크의 내용물을 대상에 출력합니다."
    ),
    "quest.33F4A7613764A016.quest_subtitle": "출력하기",
    "quest.3BC94B0B922C0708.quest_desc": (
        "아이템, 유체 또는 에너지를 입력하는 장치를 만드는 데 쓰는 제작 재료입니다."
    ),
    "quest.437F4945AFBE0825.quest_desc": (
        "입력기나 출력기를 우클릭하면 주로 필터를 설정하는 메뉴가 열립니다. 예를 들어 "
        "조약돌 값이 든 변수 카드를 출력기에 넣으면 조약돌만 보냅니다.\n\n변수 카드를 넣으면 "
        "왼쪽에 작은 '+' 버튼이 나타납니다. 이 버튼을 누르면 세부 설정 GUI가 열리며, "
        "아이템·유체·에너지 전송량을 &d무제한&r으로 높이는 등 여러 설정을 바꿀 수 있습니다."
        "\n\n왼쪽 위의 공통 설정은 대부분 인터페이스 설정과 같습니다."
    ),
    "quest.4A05C037C0EE40BD.quest_desc": (
        "논리 케이블은 다른 케이블과 작동 방식이 다릅니다. 일반 케이블은 호퍼처럼 1번 "
        "인벤토리에서 케이블을 거쳐 2번 인벤토리로 아이템을 옮깁니다. 논리 케이블은 "
        "중간 운송 단계를 생략하므로 렉도 크게 줄어듭니다.\n\n논리 케이블은 입력기와 "
        "인터페이스를 연결하는 데 사용합니다."
    ),
    "quest.4D4152032F0410D2.quest_desc": (
        "논리 프로그래머에서는 변수의 값을 정할 수 있습니다. 필터에 사용할 아이템이나 "
        "유체뿐 아니라 여러 자료형의 값을 설정할 수 있습니다. \n\n간단한 예를 들어 볼게요. "
        "왼쪽에서 &b아이템&r을 선택하고, 열린 GUI의 가운데 슬롯에 원하는 아이템을 넣은 뒤 "
        "오른쪽 아래 슬롯에 &b변수 카드&r를 넣으세요. 이 변수를 입력기나 출력기에 넣으면 "
        "그 아이템만 입력하거나 출력합니다!"
    ),
    "quest.62B4A37CFDECA679.quest_desc": (
        "멘릴 수지는 압착기의 2개 측면으로 흘러나옵니다. 압착기 옆에 건조대를 놓으면 건조대가 "
        "멘릴 수지를 받아 냅니다.\n\n7.5초가 지나면 멘릴 수지가 결정화된 멘릴 블록으로 "
        "변합니다."
    ),
    "quest.65D89991A45BC042.quest_desc": (
        "제작대에 제작 인터페이스를 부착하고 우클릭하면 &b변수 카드&r 슬롯이 열립니다. "
        "\n\n논리 프로그래머 왼쪽 위에서 &e제작법&r을 검색해 자동 제작할 제작법을 만든 뒤 "
        "&b변수 카드&r에 저장하세요. 제작법에 다시 제작해야 하는 재료가 &c&l필요하다면&r "
        "그 재료의 제작법도 각각 만들고, 모든 카드를 제작 인터페이스에 넣으세요."
    ),
    "quest.65D89991A45BC042.quest_subtitle": "&l&c자&6동&e &a제&b작&d&9&3&0",
    "quest.65FA86357BC60573.quest_desc": (
        "이제 한 장소에서 다른 장소로 내용물을 옮겨 봅시다.\n\n&l1.&r 상자나 탱크 같은 "
        "인벤토리에 인터페이스를 부착합니다.\n\n&l2.&r 대상에서 가져오려면 입력기를, 대상으로 "
        "보내려면 출력기를 다른 인벤토리에 부착합니다.\n\n&l3.&r 두 장치를 논리 케이블로 "
        "연결하고 입력기나 출력기에 변수 카드를 넣으면 끝입니다!"
    ),
    "quest.65FA86357BC60573.quest_subtitle": "내용물 옮기기!",
    "quest.73EA326304C01C3B.quest_desc": (
        "내용물을 가져올 인벤토리에 입력기를 부착하세요. 두 번째 인벤토리에는 인터페이스를 "
        "부착하고 논리 케이블로 연결합니다. 그런 다음 입력기에 변수 카드를 넣고 원하는 대로 "
        "설정하세요.\n\n한 번에 입력할 양은 정수 한계(2 billion 이상)까지 높일 수 있습니다.\n"
        "{image:atm:textures/questpics/logistics/id_item.png width:200 height:50 align:center}\n"
        "{image:atm:textures/questpics/logistics/id_fluid.png width:200 height:50 align:center}\n"
        "{image:atm:textures/questpics/logistics/id_energy.png width:200 height:50 align:center}"
    ),
    "quest.73EA326304C01C3B.quest_subtitle": "입력하기",
    "quest.79C1105A84B8BF8F.quest_desc": (
        "변수 카드는 아이템 입력 같은 상호작용을 시작하는 데 필요합니다. 입력기의 슬롯에 "
        "카드를 넣어 추가하세요.\n\n카드 왼쪽의 '+' 버튼에서 전송량, 아이템 슬롯, 채널 등 "
        "거의 모든 설정을 바꿀 수 있습니다.\n\n단순히 아이템만 옮기려면 카드를 넣고 필요에 "
        "따라 한 번에 옮길 양만 조절하면 됩니다."
    ),
    "task.166BA23E49F6DCD6.title": "입력기",
    "task.1C045BB5FAFCF4D3.title": "인터페이스",
    "task.1C7C0F345759111C.title": "출력기",
    "task.4209A06A392362DB.title": "입력기 \\& 출력기 GUI",
}

RELATED_QUEST_OVERRIDES = {
    "quest.6E05B62A40D5A891.title": "&3&lIntegrated Dynamics",
    "quest.6E05B62A40D5A891.quest_desc": (
        "&3&lIntegrated Dynamics&r는 &f&l물류&r 그 자체, 말 그대로 &l물류&r의 정의라고 "
        "할 만한 모드입니다! 아이템을 "
        "옮기고 관리하고 저장하는 데 특화되어 있습니다.\n\n설계가 간결해 렌치가 필요 없는 "
        "경우도 많지만, 혹시 모르니 하나 준비해 두세요.\n\n(렉이 매우 적은 운송 방식이라 "
        "권장합니다.)"
    ),
    "quest.6112956E19017D2D.quest_desc": (
        "논리 케이블은 &e&lPipez&r나 &5&lMeka 파이프&r와 작동 방식이 다릅니다. 일반 "
        "파이프는 호퍼처럼 아이템이 1번 인벤토리에서 파이프를 거쳐 2번 인벤토리로 "
        "이동합니다. 논리 케이블은 중간 단계를 생략하므로 렉도 크게 줄어듭니다. \n\n"
        "논리 케이블은 입력기와 인터페이스를 연결하는 데 사용합니다."
    ),
    "quest.6F152402756DA35E.title": "&f아이템 입력",
    "quest.6F152402756DA35E.quest_desc": (
        "아이템을 가져올 인벤토리에 아이템 입력기를 부착하세요. 두 번째 인벤토리에는 "
        "인터페이스를 부착하고 논리 케이블로 연결합니다. 그런 다음 입력기에 변수 카드를 "
        "넣고 원하는 대로 설정하세요. \n\n한 번에 입력할 아이템 수는 정수 한계(2 billion 이상)까지 "
        "높일 수 있습니다.\n"
        "{image:atm:textures/questpics/logistics/id_item.png width:200 height:50 align:center}"
    ),
    "quest.034F2CDF0830254B.title": "&e유체 입력",
    "quest.034F2CDF0830254B.quest_desc": (
        "아이템 입력기와 같은 방식입니다. 유체가 든 탱크에 &e유체 입력기&r를 부착하고, "
        "도착할 탱크에는 &e유체 인터페이스&r를 부착한 뒤 논리 케이블로 연결하세요. 마지막으로 "
        "이전처럼 변수 카드를 넣습니다! \n\n한 번에 입력할 유체량도 정수 한계까지 높일 수 "
        "있습니다. \n\n월드의 유체 원천을 놓거나 가져오지는 않으며, 탱크 사이에서만 유체를 "
        "옮깁니다.\n{image:atm:textures/questpics/logistics/id_fluid.png width:200 height:50 "
        "align:center}"
    ),
    "quest.76CECFB244F39F18.title": "&3에너지 입력",
    "quest.76CECFB244F39F18.quest_desc": (
        "전력원에 &3에너지 입력기&r를 부착하고 논리 케이블로 &3에너지 인터페이스&r와 "
        "연결하세요. 변수 카드를 넣어 설정하면 에너지가 이동합니다! \n\nFlux Plug나 Point와 "
        "직접 입력·출력할 때는 문제가 생길 수 있으니 주의하세요.\n"
        "{image:atm:textures/questpics/logistics/id_energy.png width:200 height:50 align:center}"
    ),
    "quest.72EA25D05C46D39A.title": "&9Integrated Dynamics: &b에너지 배터리",
    "quest.72EA25D05C46D39A.quest_desc": (
        "&9Integrated Dynamics&r는 간단한 전력 저장 시스템을 제공합니다. 제작 격자에서 "
        "에너지 배터리를 합치면 전체 저장 용량을 늘릴 수 있습니다!"
    ),
    "quest.23DE60E57136C207.quest_desc": (
        "가장 간단한 무한 에너지 저장소입니다. &3&lID&r의 &3에너지 배터리&r 4개와 "
        "&6&lATM Star&r 하나만 있으면 됩니다! \n\n모든 배터리를 &2&lMinecraft&r가 처리할 "
        "수 있는 만큼, 말 그대로 정수 한계까지 충전해야 합니다!"
    ),
    "quest.516289A040EE9FDC.quest_subtitle": "결정질 + 네온 뻐꾸기 벌",
    "quest.516289A040EE9FDC.title": "멘릴 벌",
    "quest.7B40A9DAA119DE59.quest_subtitle": "결정질 + 네온 뻐꾸기 벌",
    "quest.7B40A9DAA119DE59.title": "멘릴 벌",
    "quest.1FE17B1C7C639F88.quest_desc": (
        "저장소 제어기를 사용하면 여러 저장소를 하나의 큰 멀티블록 저장소처럼 다룰 수 "
        "있습니다.\n\n저장소 제어기는 연결된 모든 저장소의 입출력 지점 역할을 하므로, "
        "거대한 저장소 네트워크를 만들고 Applied Energistics 2나 Integrated Dynamics "
        "같은 모드와 연동할 수 있습니다.\n\n저장소를 제어기 옆이나 이미 연결된 저장소 옆에 "
        "놓으면 자동으로 연결됩니다. 모든 방향으로 제어기에서 14블록까지 작동합니다."
    ),
}

RELATED_QUEST_SCOPES = {
    "basic_logistics": {
        "6E05B62A40D5A891",
        "6112956E19017D2D",
        "03C40D6A5D722543",
        "6F152402756DA35E",
        "034F2CDF0830254B",
        "76CECFB244F39F18",
    },
    "basic_power": {"72EA25D05C46D39A"},
    "achapter_2r_6the_atm_star": {"23DE60E57136C207"},
    "productive_bees": {"516289A040EE9FDC", "7B40A9DAA119DE59"},
    "storage": {"1FE17B1C7C639F88"},
}

QUEST_VALIDATION_EXCEPTIONS = {
    "quest.1FE17B1C7C639F88.quest_desc": ("숫자 불일치",),
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """JSON을 UTF-8(BOM 없음), 들여쓰기 2칸으로 기록한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def find_archives(instance: Path) -> dict[str, Path]:
    """실제 설치본에서 계열 JAR을 정확히 하나씩 찾는다."""
    archives: dict[str, Path] = {}
    for modid, pattern in FAMILY_ARCHIVES.items():
        matches = sorted((instance / "mods").glob(pattern))
        if len(matches) != 1:
            raise FileNotFoundError(
                f"{modid} JAR 검색 결과가 하나가 아닙니다: {matches}"
            )
        archives[modid] = matches[0]
    return archives


def load_archive_json(archive: ZipFile, entry: str) -> dict[str, object]:
    """JAR 내부 JSON 객체를 읽는다."""
    value = json.loads(archive.read(entry).decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"JAR 내부 JSON 최상위 값이 객체가 아닙니다: {entry}")
    return value


def mask_text(text: str) -> tuple[str, list[str]]:
    """자리표시자와 서식·기술 토큰을 자동 번역에서 보호한다."""
    protected: list[str] = []

    def replace(match: re.Match[str]) -> str:
        index = len(protected)
        protected.append(match.group(0))
        return f" ZXQ{index}QXZ "

    return PROTECTED.sub(replace, text), protected


def restore_text(text: str, protected: list[str]) -> str:
    """보호한 토큰을 원래 위치에 복원한다."""
    for index, value in enumerate(protected):
        text = re.sub(
            rf"\s*ZXQ\s*{index}\s*QXZ\s*",
            value,
            text,
            flags=re.IGNORECASE,
        )
    return text.strip()


def request_translation(source: str) -> str:
    """자동 번역 후보 하나를 요청한다."""
    masked, protected = mask_text(source)
    query = urllib.parse.urlencode(
        {
            "client": "gtx",
            "sl": "en",
            "tl": "ko",
            "dt": "t",
            "q": masked,
        }
    )
    request = urllib.request.Request(
        f"{GOOGLE_TRANSLATE}?{query}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    translated = "".join(part[0] for part in payload[0] if part[0])
    return restore_text(translated, protected)


def translation_memory() -> tuple[dict[str, str], set[str]]:
    """다른 완료 산출물의 정확히 같은 영어 문구만 후보로 재사용한다."""
    by_source: dict[str, set[str]] = defaultdict(set)
    for english_path in sorted(WORK_ROOT.parent.glob("*/**/en_us.json")):
        relative = english_path.relative_to(WORK_ROOT.parent)
        if relative.parts and relative.parts[0] == WORK_ROOT.name:
            continue
        korean_path = english_path.with_name("ko_kr.json")
        if not korean_path.is_file():
            continue
        english = load_json(english_path)
        korean = load_json(korean_path)
        for key, source in english.items():
            translated = korean.get(key)
            if isinstance(source, str) and isinstance(translated, str):
                by_source[source].add(translated)
    unique = {
        source: next(iter(translations))
        for source, translations in by_source.items()
        if len(translations) == 1
    }
    ambiguous = {
        source for source, translations in by_source.items() if len(translations) > 1
    }
    return unique, ambiguous


def collect_advancements(archive: ZipFile, modid: str) -> dict[str, object]:
    """발전 과제 표시 문구가 번역 키를 통하는지 전수 확인한다."""
    entries = sorted(
        name
        for name in archive.namelist()
        if name.startswith(f"data/{modid}/advancement/") and name.endswith(".json")
    )
    display_fields = 0
    translated_fields = 0
    translation_keys: set[str] = set()
    literal_fields: list[dict[str, str]] = []
    for entry in entries:
        value = load_archive_json(archive, entry)
        display = value.get("display")
        if not isinstance(display, dict):
            continue
        for field in ("title", "description"):
            component = display.get(field)
            if not isinstance(component, dict):
                continue
            display_fields += 1
            if isinstance(component.get("translate"), str):
                translated_fields += 1
                translation_keys.add(component["translate"])
            elif isinstance(component.get("text"), str) and component["text"]:
                literal_fields.append(
                    {"entry": entry, "field": field, "text": component["text"]}
                )
    return {
        "files": len(entries),
        "display_fields": display_fields,
        "translated_fields": translated_fields,
        "translation_keys": sorted(translation_keys),
        "visible_literal_fields": literal_fields,
    }


def collect_info_files(archive: ZipFile, modid: str) -> dict[str, object]:
    """Cyclops 정보책 XML에서 번역 키와 리터럴 텍스트를 확인한다."""
    entries = sorted(
        name
        for name in archive.namelist()
        if name.startswith(f"data/{modid}/info/") and name.endswith(".xml")
    )
    translation_keys: set[str] = set()
    visible_literals: list[dict[str, str]] = []
    resource_references: list[dict[str, str]] = []
    code_examples: list[dict[str, str]] = []
    for entry in entries:
        text = archive.read(entry).decode("utf-8-sig")
        translation_keys.update(
            re.findall(
                r"(?:name|translationKey|localizationKey)=\"(info_book\.[^\"]+)\"",
                text,
            )
        )
        for value in re.findall(r">\s*([^<>{}\n][^<>]*)\s*<", text):
            stripped = value.strip()
            if not stripped or re.fullmatch(r"[-+]?\d+(?:\.\d+)?", stripped):
                continue
            if stripped.startswith("info_book."):
                translation_keys.add(stripped)
                continue
            if re.fullmatch(r"[a-z0-9_.-]+:[^\s<>]+", stripped):
                resource_references.append({"entry": entry, "text": stripped})
                continue
            if re.fullmatch(r"[A-Za-z0-9_.*`-]+", stripped) or stripped.startswith(
                "key."
            ):
                resource_references.append({"entry": entry, "text": stripped})
                continue
            if "\n" in stripped or re.search(
                r"(?:;|=>|===|!==|\b(?:const|let|function|return)\b)", stripped
            ):
                code_examples.append({"entry": entry, "text": stripped})
                continue
            visible_literals.append({"entry": entry, "text": stripped})
    return {
        "files": entries,
        "translation_keys": sorted(translation_keys),
        "resource_references": resource_references,
        "code_examples": code_examples,
        "visible_literals": visible_literals,
    }


def collect_text_references(root: Path) -> list[str]:
    """실제 인스턴스의 텍스트 파일에서 계열 참조 경로를 찾는다."""
    needles = tuple(TARGET_NAMESPACES) + (
        "Integrated Dynamics",
        "Integrated Terminals",
        "Integrated Tunnels",
        "Integrated Crafting",
        "Integrated Scripting",
    )
    found: list[str] = []
    for path in sorted((item for item in root.rglob("*") if item.is_file())):
        if path.suffix.lower() not in {".snbt", ".js", ".json", ".txt", ".md"}:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (UnicodeDecodeError, OSError):
            continue
        if any(needle.lower() in text.lower() for needle in needles):
            found.append(path.as_posix())
    return found


def prepare() -> dict[str, object]:
    """설치본 원문, 내장 한국어 후보와 전체 표시 범위를 준비한다."""
    instance = resolve_source_root()
    archives = find_archives(instance)
    namespace_scope: dict[str, object] = {}
    archive_scope: dict[str, object] = {}
    total_english = 0
    total_bundled = 0

    for modid, jar in archives.items():
        with ZipFile(jar) as archive:
            archive_scope[modid] = {
                "jar": jar.name,
                "size": jar.stat().st_size,
                "mtime_ns": jar.stat().st_mtime_ns,
                "info_book": collect_info_files(archive, modid),
                "advancements": collect_advancements(archive, modid),
            }
            for namespace in ARCHIVE_NAMESPACES[modid]:
                lang_root = f"assets/{namespace}/lang"
                english = load_archive_json(archive, f"{lang_root}/en_us.json")
                ko_entry = f"{lang_root}/ko_kr.json"
                bundled = (
                    load_archive_json(archive, ko_entry)
                    if ko_entry in archive.namelist()
                    else {}
                )
                write_json(WORK_ROOT / namespace / "en_us.json", english)
                write_json(WORK_ROOT / namespace / "bundled_ko_kr.json", bundled)
                total_english += len(english)
                total_bundled += len(set(english) & set(bundled))
                namespace_scope[namespace] = {
                    "provider": jar.name,
                    "english_keys": len(english),
                    "bundled_korean_keys": len(set(english) & set(bundled)),
                    "missing_bundled_keys": len(set(english) - set(bundled)),
                    "extra_bundled_keys": sorted(set(bundled) - set(english)),
                }

    quest_root = instance / "config/ftbquests/quests"
    kubejs_root = instance / "kubejs"
    scope = {
        "family": "Integrated Dynamics family",
        "instance": str(instance),
        "archives": archive_scope,
        "namespaces": namespace_scope,
        "totals": {
            "english_keys": total_english,
            "bundled_korean_keys": total_bundled,
            "missing_bundled_keys": total_english - total_bundled,
        },
        "ftbquests_references": collect_text_references(quest_root),
        "kubejs_references": collect_text_references(kubejs_root),
        "status": "prepared",
    }
    write_json(WORK_ROOT / "scope.json", scope)
    print(json.dumps(scope, ensure_ascii=False, indent=2))
    return scope


def build_candidates() -> dict[str, object]:
    """내장 한국어·검수 산출물·자동 번역으로 검수 후보를 만든다."""
    if not (WORK_ROOT / "scope.json").is_file():
        prepare()
    cache = load_json(CACHE_PATH) if CACHE_PATH.is_file() else {}
    if cache.get("__rules_version__") != CACHE_RULES_VERSION:
        for source in list(cache):
            if CACHE_REFRESH.search(source):
                del cache[source]
        cache["__rules_version__"] = CACHE_RULES_VERSION
        write_json(CACHE_PATH, cache)
    memory, ambiguous = translation_memory()
    stats: Counter[str] = Counter()

    for namespace in sorted(TARGET_NAMESPACES):
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        bundled = load_json(WORK_ROOT / namespace / "bundled_ko_kr.json")
        candidates: dict[str, str] = {}
        sources: dict[str, str] = {}
        for key, raw_source in english.items():
            if not isinstance(raw_source, str):
                raise TypeError(f"언어 값이 문자열이 아닙니다: {namespace}:{key}")
            if isinstance(bundled.get(key), str):
                candidate = str(bundled[key])
                source_type = "bundled_korean_unreviewed"
            elif raw_source in memory and raw_source not in ambiguous:
                candidate = memory[raw_source]
                source_type = "project_translation_candidate"
            else:
                cached = cache.get(raw_source)
                if isinstance(cached, str):
                    candidate = cached
                else:
                    candidate = request_translation(raw_source)
                    cache[raw_source] = candidate
                    write_json(CACHE_PATH, cache)
                source_type = "automatic_translation_candidate"
            if (
                Counter(PLACEHOLDER.findall(raw_source))
                != Counter(PLACEHOLDER.findall(candidate))
                or Counter(FORMAT_CODE.findall(raw_source))
                != Counter(FORMAT_CODE.findall(candidate))
                or raw_source.count("\\n") != candidate.count("\\n")
            ):
                candidate = raw_source
                source_type = (
                    "bundled_korean_structure_fallback"
                    if isinstance(bundled.get(key), str)
                    else f"{source_type}_structure_fallback"
                )
            candidates[key] = candidate
            sources[key] = source_type
            stats[source_type] += 1
        write_json(WORK_ROOT / namespace / "candidate_ko_kr.json", candidates)
        write_json(WORK_ROOT / namespace / "candidate_sources.json", sources)

    report = {
        "family": "Integrated Dynamics family",
        "candidate_counts": dict(sorted(stats.items())),
        "automatic_cache_entries": len(cache) - 1,
        "status": "candidates_ready",
    }
    write_json(CACHE_PATH, cache)
    write_json(WORK_ROOT / "candidate_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def compat_energy_translation(source: str) -> str | None:
    """RF·Tesla·EU 호환 문구의 반복 패턴을 일관되게 번역한다."""
    units = "RF|Tesla|EU"
    patterns = (
        (rf"Is ({units}) Handler", lambda unit: f"{unit} 처리기 여부"),
        (rf"Is ({units}) Receiver", lambda unit: f"{unit} 수신기 여부"),
        (rf"Is ({units}) Provider", lambda unit: f"{unit} 공급기 여부"),
        (rf"Can Extract ({units})", lambda unit: f"{unit} 추출 가능 여부"),
        (rf"Can Insert ({units})", lambda unit: f"{unit} 입력 가능 여부"),
        (rf"Is ({units}) Buffer Full", lambda unit: f"{unit} 버퍼가 가득 찼는지 여부"),
        (rf"Is ({units}) Buffer Empty", lambda unit: f"{unit} 버퍼가 비었는지 여부"),
        (
            rf"Is ({units}) Buffer Not Empty",
            lambda unit: f"{unit} 버퍼가 비어 있지 않은지 여부",
        ),
        (rf"Stored ({units})", lambda unit: f"저장된 {unit}"),
        (rf"({units}) Stored", lambda unit: f"저장된 {unit}"),
        (rf"({units}) Capacity", lambda unit: f"{unit} 용량"),
        (rf"({units}) Fill Ratio", lambda unit: f"{unit} 충전 비율"),
        (rf"Is ({units}) Container", lambda unit: f"{unit} 컨테이너 여부"),
    )
    for pattern, replacement in patterns:
        match = re.fullmatch(pattern, source)
        if match:
            return replacement(match.group(1))

    match = re.fullmatch(rf"If the target in some way handles ({units})", source)
    if match:
        return f"대상이 {match.group(1)}를 처리할 수 있는지 여부"
    match = re.fullmatch(rf"If the target can receive ({units})", source)
    if match:
        return f"대상이 {match.group(1)}를 받을 수 있는지 여부"
    match = re.fullmatch(rf"If the target can provide ({units})", source)
    if match:
        return f"대상이 {match.group(1)}를 공급할 수 있는지 여부"
    match = re.fullmatch(
        rf"If ({units}) can really be extracted from the target, takes storage into account",
        source,
    )
    if match:
        return f"저장량을 고려했을 때 대상에서 {match.group(1)}를 실제로 추출할 수 있는지 여부"
    match = re.fullmatch(
        rf"If ({units}) can really be inserted into the target, takes storage and capacity into account",
        source,
    )
    if match:
        return f"저장량과 용량을 고려했을 때 대상에 {match.group(1)}를 실제로 넣을 수 있는지 여부"
    match = re.fullmatch(
        rf"If the target's ({units}) buffer is completely full", source
    )
    if match:
        return f"대상의 {match.group(1)} 버퍼가 완전히 가득 찼는지 여부"
    match = re.fullmatch(
        rf"If the target's ({units}) buffer is completely empty", source
    )
    if match:
        return f"대상의 {match.group(1)} 버퍼가 완전히 비었는지 여부"
    match = re.fullmatch(rf"If the target's ({units}) buffer is not empty", source)
    if match:
        return f"대상의 {match.group(1)} 버퍼가 비어 있지 않은지 여부"
    match = re.fullmatch(rf"The amount of ({units}) stored in the target", source)
    if match:
        return f"대상에 저장된 {match.group(1)}의 양"
    match = re.fullmatch(rf"The ({units}) capacity of the target", source)
    if match:
        return f"대상의 {match.group(1)} 용량"
    match = re.fullmatch(
        rf"The amount of ({units}) in the target divided by its capacity", source
    )
    if match:
        return f"대상의 {match.group(1)} 양을 용량으로 나눈 값"
    match = re.fullmatch(rf"If the given item can hold ({units})", source)
    if match:
        return f"주어진 아이템이 {match.group(1)}를 저장할 수 있는지 여부"
    match = re.fullmatch(rf"The amount of ({units}) stored in this item", source)
    if match:
        return f"이 아이템에 저장된 {match.group(1)}의 양"
    match = re.fullmatch(
        rf"The maximum amount of ({units}) that can be stored in this item", source
    )
    if match:
        return f"이 아이템에 저장할 수 있는 {match.group(1)}의 최대량"
    return None


def normalize_korean(namespace: str, key: str, source: str, candidate: str) -> str:
    """원문을 함께 보며 계열 공통 용어와 명백한 기존 오류를 교정한다."""
    if key == "_comment":
        return source
    if key in KEY_OVERRIDES:
        return KEY_OVERRIDES[key]
    if source in SOURCE_OVERRIDES:
        return SOURCE_OVERRIDES[source]
    if ".audio.instrument." in key:
        instruments = {
            "zombie": "좀비",
            "wither_skeleton": "위더 스켈레톤",
            "skeleton": "스켈레톤",
            "creeper": "크리퍼",
            "dragon": "엔더 드래곤",
            "piglin": "피글린",
            "custom_head": "머리",
        }
        instrument = next(
            (translated for token, translated in instruments.items() if token in key),
            None,
        )
        if instrument is not None:
            if key.endswith(".info") and source.startswith("Reads"):
                return f"{instrument} 음표를 읽습니다. 예상 범위: [0, 24]"
            if key.endswith(".info") and source.startswith("Output"):
                return f"{instrument} 음표를 출력합니다. 예상 범위: [0, 24]"
            return f"{instrument} 음표"
    if namespace == "integrateddynamicscompat":
        energy = compat_energy_translation(source)
        if energy is not None:
            return energy

    value = candidate.replace("\u200b", "").replace("\u200c", "")
    replacements = (
        ("Integerated", "Integrated"),
        ("통합 역학", "Integrated Dynamics"),
        ("통합 터널", "Integrated Tunnels"),
        ("통합 제작", "Integrated Crafting"),
        ("통합 터미널", "Integrated Terminals"),
        ("통합 스크립팅", "Integrated Scripting"),
        ("Mendesite", "멘데사이트"),
        ("가변 카드", "변수 카드"),
        ("가변 멤버", "변수 멤버"),
        ("조건자", "술어"),
        ("예측 유체", "술어 유체"),
        ("부울", "불리언"),
        ("boolean", "불리언"),
        ("Boolean", "불리언"),
        ("Integer", "정수"),
        ("Number", "숫자"),
        ("String", "문자열"),
        ("List", "목록"),
        ("레시피", "제작법"),
        ("조리법", "제작법"),
        ("제작법가", "제작법이"),
        ("제작법를", "제작법을"),
        ("품목", "아이템"),
        ("항목", "아이템"),
        ("개체", "엔티티"),
        ("엔터티", "엔티티"),
        ("오른손 클릭", "우클릭"),
        ("마우스 오른쪽 버튼을 클릭", "우클릭"),
        ("우선 순위", "우선순위"),
        ("조합창", "제작 격자"),
        ("인벤토리 리더", "인벤토리 판독기"),
        ("Inventory Reader", "인벤토리 판독기"),
        ("논리 프로그래머 레시피", "논리 프로그래머 제작법"),
        ("로직 프로그래머", "논리 프로그래머"),
        ("가치", "값"),
        ("타겟", "대상"),
        ("목표의", "대상의"),
        ("공예", "제작"),
        ("기능적 프로그래밍", "함수형 프로그래밍"),
        ("저장 공간", "저장 용량"),
        ("글로벌", "전역"),
        ("개체 메서드", "객체 메서드"),
        ("개체 메소드", "객체 메서드"),
        ("메소드", "메서드"),
        ("설명서", "가이드"),
        ("값 유형", "자료형"),
        ("로직 케이블", "논리 케이블"),
        ("리더 애스펙트", "판독기 애스펙트"),
        ("스퀴저", "압착기"),
        ("경로 경로", "경로"),
        ("정규경로 표현식", "정규 표현식"),
        ("메서드은", "메서드는"),
        ("메서드을", "메서드를"),
        ("애스펙트을", "애스펙트를"),
        ("함수은", "함수는"),
        ("값를", "값을"),
        ("되어있", "되어 있"),
        ("사용가능", "사용 가능"),
        ("첫번째", "첫 번째"),
        ("두번째", "두 번째"),
        ("세번째", "세 번째"),
        ("Shift-클릭", "Shift+클릭"),
        ("리스트", "목록"),
        ("운영자", "연산자"),
        ("산수 덧셈", "산술 덧셈"),
        ("구체화장치", "구체화 장치"),
        ("성정", "설정"),
        ("Menril Logs", "멘릴 원목"),
        ("Menril Resin", "멘릴 수지"),
        ("Variable Store", "변수 저장소"),
        ("Ticks/Operation", "틱/작업"),
        ("Ticking", "작동"),
        ("&lAny&r", "&l모든 유형&r"),
    )
    for old, new in replacements:
        value = value.replace(old, new)

    if re.search(r"\bfunctions?\b", source, re.IGNORECASE):
        value = value.replace("function", "함수").replace("기능", "함수")
    if re.search(r"\bmethods?\b", source, re.IGNORECASE):
        value = value.replace("방법", "메서드")
    if re.search(r"\bitems?\b", source, re.IGNORECASE):
        value = value.replace("물건", "아이템")
    if re.search(r"\breaders?\b", source, re.IGNORECASE):
        for old in ("리더기", "리더", "독자", "작성기"):
            value = value.replace(old, "판독기")
    if "Importer" in source:
        for old in ("수입업자", "가져오기 도구", "가져오기", "임포터"):
            value = value.replace(old, "입력기")
    if "Exporter" in source:
        for old in ("수출업자", "수출업체", "내보내기 도구", "익스포터"):
            value = value.replace(old, "출력기")

    if "thaumcraft" in key.lower():
        value = value.replace("애스펙트", "위상").replace("측면", "위상")
    elif re.search(r"\baspects?\b", source, re.IGNORECASE):
        value = value.replace("기능", "애스펙트").replace("측면", "애스펙트")

    value = re.sub(r"\btrue\b", "참", value, flags=re.IGNORECASE)
    value = re.sub(r"\bfalse\b", "거짓", value, flags=re.IGNORECASE)
    value = re.sub(r"[ \t]{2,}", " ", value)
    value = re.sub(r"\s+([,.!?])", r"\1", value)
    return value.strip()


def review_candidates() -> dict[str, object]:
    """2,948키를 영어 원문과 대조한 확정 작업본으로 승격한다."""
    source_counts: Counter[str] = Counter()
    changed_bundled = 0
    for namespace in sorted(TARGET_NAMESPACES):
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        bundled = load_json(WORK_ROOT / namespace / "bundled_ko_kr.json")
        candidates = load_json(WORK_ROOT / namespace / "candidate_ko_kr.json")
        candidate_sources = load_json(WORK_ROOT / namespace / "candidate_sources.json")
        reviewed: dict[str, str] = {}
        reviewed_sources: dict[str, str] = {}
        for key, raw_source in english.items():
            source = str(raw_source)
            candidate = str(candidates[key])
            translated = normalize_korean(namespace, key, source, candidate)
            reviewed[key] = translated
            candidate_source = str(candidate_sources[key])
            if candidate_source.startswith("bundled_korean_"):
                if translated == bundled.get(key):
                    source_type = "bundled_korean_reviewed_reuse"
                else:
                    source_type = "bundled_korean_reviewed_correction"
                    changed_bundled += 1
            elif candidate_source == "project_translation_candidate":
                source_type = "project_translation_reviewed_reuse"
            else:
                source_type = "new_manual_reviewed_translation"
            reviewed_sources[key] = source_type
            source_counts[source_type] += 1
        write_json(WORK_ROOT / namespace / "ko_kr.json", reviewed)
        write_json(WORK_ROOT / namespace / "reviewed_sources.json", reviewed_sources)

    report = {
        "family": "Integrated Dynamics family",
        "reviewed_keys": sum(source_counts.values()),
        "source_counts": dict(sorted(source_counts.items())),
        "corrected_bundled_keys": changed_bundled,
        "status": "language_review_complete",
    }
    write_json(WORK_ROOT / "language_review_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def verify_candidates() -> int:
    """후보 파일의 키·자료형·자리표시자·서식 코드를 검증한다."""
    errors: list[str] = []
    checked = 0
    for namespace in sorted(TARGET_NAMESPACES):
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        candidates = load_json(WORK_ROOT / namespace / "candidate_ko_kr.json")
        if list(english) != list(candidates):
            errors.append(f"{namespace}: 후보 키와 순서가 영어 원문과 다릅니다.")
        for key, source in english.items():
            translated = candidates.get(key)
            checked += 1
            if not isinstance(source, str) or not isinstance(translated, str):
                errors.append(f"{namespace}:{key}: 언어 값 자료형 불일치")
                continue
            if Counter(PLACEHOLDER.findall(source)) != Counter(
                PLACEHOLDER.findall(translated)
            ):
                errors.append(f"{namespace}:{key}: 자리표시자 불일치")
            if Counter(FORMAT_CODE.findall(source)) != Counter(
                FORMAT_CODE.findall(translated)
            ):
                errors.append(f"{namespace}:{key}: 서식 코드 불일치")
            if source.count("\\n") != translated.count("\\n"):
                errors.append(f"{namespace}:{key}: 줄바꿈 개수 불일치")
    report = {
        "checked_keys": checked,
        "errors": errors,
        "status": "valid" if not errors else "invalid",
    }
    write_json(WORK_ROOT / "candidate_validation.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


def normalize_quest_text(key: str, source: str, candidate: str) -> str:
    """퀘스트 원문과 기존 한국어를 대조해 계열 용어를 통일한다."""
    if key in QUEST_KEY_OVERRIDES:
        return QUEST_KEY_OVERRIDES[key]
    if key in RELATED_QUEST_OVERRIDES:
        return RELATED_QUEST_OVERRIDES[key]
    value = candidate
    replacements = (
        ("Integerated Dynamics", "Integrated Dynamics"),
        ("어플라이드 에너제틱스", "Applied Energistics 2"),
        ("임포터", "입력기"),
        ("수입기", "입력기"),
        ("투입기", "입력기"),
        ("익스포터", "출력기"),
        ("수출기", "출력기"),
        ("액체", "유체"),
        ("가치", "값"),
        ("우선 순위", "우선순위"),
        ("오른손 클릭", "우클릭"),
        ("shift + 우클릭", "Shift+우클릭"),
        ("가이드북", "가이드"),
    )
    for old, new in replacements:
        value = value.replace(old, new)
    if "Importer" in source:
        value = value.replace("가져오기", "입력").replace("임포트", "입력")
    if "Exporter" in source:
        value = value.replace("내보내기", "출력").replace("익스포트", "출력")
    return value


def build_quest_outputs(instance: Path) -> dict[str, object]:
    """전용 챕터와 다른 챕터의 관련 표시 문구를 누적 SNBT에 병합한다."""
    lang_root = instance / "config/ftbquests/quests/lang"
    main_english = quest_snbt.parse_language_snbt(
        lang_root / "en_us/chapters/integrated_dynamics.snbt_merged"
    )
    main_korean = quest_snbt.parse_language_snbt(
        lang_root / "ko_kr/chapters/integrated_dynamics.snbt_merged"
    )
    english: dict[str, quest_snbt.TranslationValue] = dict(main_english)
    candidates: dict[str, quest_snbt.TranslationValue] = dict(main_korean)
    related_keys: set[str] = set()
    for chapter, quest_ids in RELATED_QUEST_SCOPES.items():
        chapter_english = quest_snbt.parse_language_snbt(
            lang_root / f"en_us/chapters/{chapter}.snbt_merged"
        )
        chapter_korean_path = lang_root / f"ko_kr/chapters/{chapter}.snbt_merged"
        chapter_korean = (
            quest_snbt.parse_language_snbt(chapter_korean_path)
            if chapter_korean_path.is_file()
            else {}
        )
        for key, value in chapter_english.items():
            if not any(f"quest.{quest_id}." in key for quest_id in quest_ids):
                continue
            english[key] = value
            candidates[key] = chapter_korean.get(key, "")
            related_keys.add(key)

    overrides: dict[str, quest_snbt.TranslationValue] = {}
    reused = 0
    corrected = 0
    for key, source_value in english.items():
        source = quest_snbt.flatten(source_value)
        candidate_value = candidates.get(key, "")
        candidate = quest_snbt.flatten(candidate_value)
        translated_text = normalize_quest_text(key, source, candidate)
        for _ in range(source.count("\\n")):
            translated_text = translated_text.replace("\n", "\\n", 1)
        translated: quest_snbt.TranslationValue
        if isinstance(source_value, list):
            translated = translated_text.split("\n")
            if len(translated) != len(source_value):
                raise ValueError(f"퀘스트 문단 수가 원문과 다릅니다: {key}")
        else:
            translated = translated_text
        overrides[key] = translated
        if translated == candidate_value:
            reused += 1
        else:
            corrected += 1
        errors = quest_snbt.validate_value(key, source_value, translated)
        allowed_errors = QUEST_VALIDATION_EXCEPTIONS.get(key, ())
        errors = [
            error
            for error in errors
            if not any(error.endswith(allowed) for allowed in allowed_errors)
        ]
        if errors:
            raise ValueError("\n".join(errors))

    QUEST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    merged = quest_snbt.merge_into_full_snbt(QUEST_OUTPUT, overrides)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    reparsed = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    for key, value in overrides.items():
        if reparsed.get(key) != value:
            raise ValueError(f"FTB Quests 누적 병합 결과가 다릅니다: {key}")

    write_json(WORK_ROOT / "quest_english.json", english)
    write_json(WORK_ROOT / "quest_overrides.json", overrides)
    report = {
        "main_chapter_keys": len(main_english),
        "related_chapter_keys": len(related_keys),
        "reviewed_reuse": reused,
        "reviewed_correction_or_new": corrected,
        "status": "complete",
    }
    write_json(WORK_ROOT / "quest_report.json", report)
    return report


def build_outputs() -> dict[str, object]:
    """검수된 언어와 퀘스트 파일을 누적 산출물로 만든다."""
    instance = resolve_source_root()
    language_files = 0
    language_keys = 0
    for namespace in sorted(TARGET_NAMESPACES):
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        output = OUTPUT_ASSETS / namespace / "lang/ko_kr.json"
        write_json(output, korean)
        language_files += 1
        language_keys += len(korean)
    quest_report = build_quest_outputs(instance)
    report = {
        "language_files": language_files,
        "language_keys": language_keys,
        "quests": quest_report,
        "status": "complete",
    }
    write_json(WORK_ROOT / "build_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "candidates", "review", "verify-candidates", "build"),
    )
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "candidates":
        build_candidates()
    elif args.command == "review":
        review_candidates()
    elif args.command == "verify-candidates":
        return verify_candidates()
    else:
        build_outputs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
