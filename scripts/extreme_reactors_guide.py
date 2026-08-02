#!/usr/bin/env python3
"""Extreme Reactors Patchouli 가이드와 기타 표시 경로를 번역·검증한다."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path
from zipfile import ZipFile

import ars_family
from local_paths import PROJECT_ROOT, resolve_source_root


WORK_ROOT = PROJECT_ROOT / "working/extreme_reactors/guide"
ENGLISH_ROOT = WORK_ROOT / "en_us"
KOREAN_ROOT = WORK_ROOT / "ko_kr"
OUTPUT_ROOT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/bigreactors"
    / "patchouli_books/erguide/ko_kr"
)
BOOK_OUTPUT = (
    PROJECT_ROOT
    / "output/overrides/kubejs/data/bigreactors/patchouli_books/erguide/book.json"
)
CACHE_FILE = PROJECT_ROOT / "temp/extreme_reactors_guide_segment_cache.json"
BOOK_PREFIX = "assets/bigreactors/patchouli_books/erguide/en_us/"
BOOK_SOURCE = "data/bigreactors/patchouli_books/erguide/book.json"
ADVANCEMENT_PREFIX = "data/bigreactors/advancement/"
VISIBLE_FIELDS = {
    "caption",
    "description",
    "header",
    "link_text",
    "name",
    "subtitle",
    "text",
    "title",
}
PATCHOULI_TAG = re.compile(r"\$\([^)]*\)")
NUMBER = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?%?")
URL = re.compile(r"https?://[^\s)]+")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
TEMPLATE_VALUE = re.compile(r"^#[A-Za-z]+$")

ALLOWED_LATIN = {
    "CC",
    "FE",
    "Forge",
    "Forge Energy",
    "GUI",
    "JEI",
    "Mekanism",
    "Minecraft",
    "Redstone",
    "RF",
    "RPM",
    "Extreme Reactors",
    "X",
    "Y",
    "Z",
    "mB",
}

EXACT_VALUES = {
    "Active Cooling": "능동 냉각",
    "Active FE Power Port": "능동형 FE 전력 포트",
    "Basic": "기본",
    "Casing": "외장",
    "Computer Port": "컴퓨터 포트",
    "Controller": "제어기",
    "Creative Water Generator": "크리에이티브 물 생성기",
    "Creative Steam Generator": "크리에이티브 증기 생성기",
    "Energy Cell": "에너지 셀",
    "Energizer parts": "에너자이저 부품",
    "Extreme Reactors": "Extreme Reactors",
    "FE Charging Port": "FE 충전 포트",
    "Fluid Injector": "유체 주입기",
    "Fluidizer parts": "유체화기 부품",
    "Forge Charging Port": "Forge 충전 포트",
    "Forge Energy Power Tap": "Forge Energy 전력 탭",
    "Forge Fluid Port": "Forge 유체 포트",
    "Forge Power Tap": "Forge 전력 탭",
    "Fuel Injection Port": "연료 주입 포트",
    "Glass": "유리",
    "How to build": "건설 방법",
    "Housing": "터빈 외장",
    "Inductor Coils": "유도 코일",
    "Inner workings": "작동 원리",
    "Mekanism Fluid Port": "Mekanism 유체 포트",
    "Moderators": "방사선 감속재",
    "Operational mode": "작동 방식",
    "Ores": "광석",
    "Other stuff": "기타",
    "Output Port": "출력 포트",
    "Part usage": "부품 용도",
    "Passive and Active Parts": "수동형·능동형 부품",
    "Passive Cooling": "수동 냉각",
    "Passive FE Power Port": "수동형 FE 전력 포트",
    "Power Port": "전력 포트",
    "Power Systems": "전력 체계",
    "Reactor parts": "원자로 부품",
    "Reprocessor parts": "재처리기 부품",
    "Reinforced": "강화",
    "Redstone Port": "레드스톤 포트",
    "Rotor Bearing": "회전자 베어링",
    "Rotor Blade": "회전자 날개",
    "Rotor Shaft": "회전자 축",
    "Solid Injector": "고체 주입기",
    "Solid Access Port": "고체 반입출 포트",
    "Steam Generator": "증기 생성기",
    "The Beginning": "시작하기",
    "The Coolants System": "냉각재 순환 체계",
    "The Energizer": "에너자이저",
    "The Fluidizer": "유체화기",
    "The Reactor": "원자로",
    "The Reprocessor": "재처리기",
    "The Rotor": "회전자",
    "The Turbine": "터빈",
    "Turbine parts": "터빈 부품",
    "Variants": "종류",
    "Waste Injector": "폐기물 주입기",
    "Water Generator": "물 생성기",
    "Your First Reactor": "첫 원자로",
}

TEXT_REPLACEMENTS = (
    ("익스트림 리액터", "Extreme Reactors"),
    ("익스트림 원자로", "Extreme Reactors"),
    ("극한 원자로", "Extreme Reactors"),
    ("리액터", "원자로"),
    ("반응기", "원자로"),
    ("터빈", "터빈"),
    ("에너지 공급기", "에너자이저"),
    ("에너자이저", "에너자이저"),
    ("재처리 장치", "재처리기"),
    ("리프로세서", "재처리기"),
    ("유동화 장치", "유체화기"),
    ("유동화기", "유체화기"),
    ("액체화기", "유체화기"),
    ("컨트롤러", "제어기"),
    ("케이싱", "외장"),
    ("하우징", "외장"),
    ("연료 막대", "연료봉"),
    ("제어 막대", "제어봉"),
    ("로터 샤프트", "회전자 축"),
    ("로터 블레이드", "회전자 날개"),
    ("로터 베어링", "회전자 베어링"),
    ("로터", "회전자"),
    ("샤프트", "축"),
    ("블레이드", "날개"),
    ("인덕터 코일", "유도 코일"),
    ("유도자 코일", "유도 코일"),
    ("파워 탭", "전력 탭"),
    ("전력 추출기", "전력 탭"),
    ("액세스 포트", "반입출 포트"),
    ("고체 액세스 포트", "고체 반입출 포트"),
    ("충전 포트", "충전 포트"),
    ("냉각수", "냉각재"),
    ("활성 냉각", "능동 냉각"),
    ("수동 냉각", "수동 냉각"),
    ("패시브", "수동형"),
    ("액티브", "능동형"),
    ("오른쪽 클릭", "우클릭"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("그래픽 사용자 인터페이스", "화면"),
    ("그래픽 인터페이스", "화면"),
    ("사용자 인터페이스", "화면"),
    ("필수 사항", "필수 여부"),
    ("유효한 위치", "설치 가능 위치"),
    ("변형", "종류"),
    ("조리법", "조합법"),
    ("레시피", "조합법"),
    ("인젝터", "주입기"),
    ("전원 포트", "전력 포트"),
    ("화면를", "화면을"),
    ("얼굴", "면"),
    ("빌딩 블록", "구성 블록"),
    ("사용후", "사용 후"),
    ("다양한 종류으로", "다양한 종류로"),
    ("일부 부분", "일부 부품"),
    ("다른 부분", "다른 부품"),
    ("일부는 필수사항", "일부는 필수"),
    ("예", "예"),
    ("아니요", "아니요"),
)

ENGLISH_REPLACEMENTS = (
    ("Active Forge Energy Power Tap", "능동형 Forge Energy 전력 탭"),
    ("Passive FE Power Port", "수동형 FE 전력 포트"),
    ("Active FE Power Port", "능동형 FE 전력 포트"),
    ("Solid Access Port", "고체 반입출 포트"),
    ("Induction Coils", "유도 코일"),
    ("Inductor Coils", "유도 코일"),
    ("Rotor Bearing", "회전자 베어링"),
    ("Rotor Shaft", "회전자 축"),
    ("Rotor Blade", "회전자 날개"),
    ("Control Rods", "제어봉"),
    ("Control Rod", "제어봉"),
    ("Fuel Rods", "연료봉"),
    ("Fuel Rod", "연료봉"),
    ("Forge Power Tap", "Forge 전력 탭"),
    ("Power Tap", "전력 탭"),
    ("Fluid Port", "유체 포트"),
    ("Power system", "전력 체계"),
    ("power system", "전력 체계"),
    ("Yellorium Ingots", "옐로륨 주괴"),
    ("Yellorium", "옐로륨"),
    ("Blutonium", "블루토늄"),
    ("Cyanite", "시아나이트"),
    ("Magentite", "마젠타이트"),
    ("Energizer", "에너자이저"),
    ("Fluidizer", "유체화기"),
    ("Reprocessor", "재처리기"),
    ("Reinforced", "강화"),
    ("Controller", "제어기"),
    ("Reactor", "원자로"),
    ("Turbine", "터빈"),
    ("Housing", "터빈 외장"),
    ("Rotor", "회전자"),
    ("Casing", "외장"),
    ("Glass", "유리"),
    ("wrench", "렌치"),
    ("Vapors", "증기"),
    ("vapor", "증기"),
    ("coolant", "냉각재"),
    ("passive", "수동형"),
    ("active", "능동형"),
    ("inlet mode", "입력 모드"),
    ("outlet mode", "출력 모드"),
    ("Rotary", "회전식"),
    ("engaged", "연결된"),
)

FORBIDDEN_ARTIFACTS = (
    "익스트림 리액터",
    "극한 원자로",
    "재처리 장치",
    "유동화",
    "액체화기",
    "컨트롤러",
    "케이싱",
    "연료 막대",
    "제어 막대",
    "로터",
    "샤프트",
    "블레이드",
    "파워 탭",
    "액세스 포트",
    "냉각수",
    "활성 냉각",
    "마우스 오른쪽",
    "오른쪽 클릭",
    "그래픽 사용자 인터페이스",
    "레시피",
    "쓰레기",
    "맥박",
    "축차",
    "주택",
    "당신",
    "적극적으로",
    "수동적으로",
    "솔리드",
    "콘센트",
    "중재자",
    "조합법가",
    "연료봉를",
    "연료봉가",
    "종류은",
    "종류을",
    "다중 블록",
    "약혼한",
    "자신을 망치",
)

LOCATION_OVERRIDES = {
    ("categories/energizer.json", "description"): (
        "에너자이저는 생산량보다도 훨씬 많은 에너지를 저장할 수 있는 멀티블록 기계입니다."
    ),
    ("categories/intro.json", "description"): (
        "첫 원자로를 건설하고 에너지 생산을 시작하는 데 필요한 내용을 설명합니다."
    ),
    (
        "categories/misc.json",
        "description",
    ): "다른 분류에 속하지 않는 내용을 설명합니다.",
    ("categories/reactor-operational_mode.json", "description"): (
        "원자로는 수동 냉각과 능동 냉각의 두 방식으로 만들 수 있습니다.$(br2)작동 방식에 "
        "따라 원자로가 가동 중에 생산하는 것이 달라집니다."
    ),
    ("categories/reactor-parts.json", "description"): (
        "원자로는 다음 부품으로 만듭니다.$(br2)필수 부품과 선택 부품이 있으며, 원자로 "
        "종류에 따라 사용할 수 없는 부품도 있습니다. 각 부품 페이지에서 종류별 사용 가능 "
        "여부를 확인하세요."
    ),
    ("categories/reactor-variants.json", "description"): (
        "원자로 부품의 여러 종류를 설명합니다.$(br2)일부 부품은 특정 종류에서 기능을 "
        "지원하지 않아 사용할 수 없습니다."
    ),
    ("categories/reactor.json", "description"): (
        "원자로는 전력을 직접 생성하거나 냉각재를 기화하는 멀티블록 기계입니다. 생성된 "
        "증기는 터빈 회전자를 구동하는 데 사용할 수 있습니다."
    ),
    ("categories/reprocessor.json", "description"): (
        "재처리기는 원자로의 폐기물을 새 연료나 다른 자원으로 바꾸어 재사용하는 멀티블록 "
        "기계입니다."
    ),
    ("categories/turbine-parts.json", "description"): (
        "터빈은 다음 부품으로 만듭니다.$(br2)필수 부품과 선택 부품이 있으며, 터빈 종류에 "
        "따라 사용할 수 없는 부품도 있습니다. 각 부품 페이지에서 종류별 사용 가능 여부를 "
        "확인하세요."
    ),
    ("categories/turbine-variants.json", "description"): (
        "터빈 부품의 여러 종류를 설명합니다.$(br2)일부 부품은 특정 종류에서 기능을 "
        "지원하지 않아 사용할 수 없습니다."
    ),
    ("categories/turbine.json", "description"): (
        "터빈의 구조와 에너지를 생산하는 방법을 설명합니다."
    ),
    ("entries/energizer/part-computerport.json", "pages.0.text"): (
        "컴퓨터 포트로 에너자이저를 컴퓨터에 연결해 상태 정보를 읽을 수 있습니다.$(br2)"
        "연결된 컴퓨터에는 표준 메서드가 제공되며, 이를 호출해 에너자이저 상태를 조회할 수 "
        "있습니다."
    ),
    ("entries/energizer/part-controller.json", "pages.0.text"): (
        "제어기는 에너자이저의 주 화면입니다.$(br2)제어기를 우클릭해 에너자이저를 켜거나 "
        "끄고, 저장된 에너지 양과 에너지의 입출력 상태를 확인할 수 있습니다."
    ),
    ("entries/energizer/part-controller.json", "pages.1.text"): (
        "화면의 조작 요소에 마우스를 올리면 자세한 정보와 설명이 툴팁으로 표시됩니다.$(br2)"
    ),
    ("entries/energizer/part-controller.json", "pages.2.text"): (
        "$(l)필수 여부:$() 최소 하나$(br)$(l)설치 가능 위치:$() 틀이 아닌 수직 면"
        "$(br)$(l)화면:$() 있음"
    ),
    ("entries/energizer/part-fechargingport.json", "pages.0.text"): (
        "Forge 충전 포트는 에너자이저에 저장된 에너지로 Forge Energy "
        "$(l:bigreactors:misc/powersystem)전력 체계$(/l)를 사용하는 아이템을 충전합니다."
        "$(br2)포트 화면을 열고 충전할 아이템을 가운데 입력 슬롯에 넣으세요."
    ),
    ("entries/energizer/part-fechargingport.json", "pages.1.text"): (
        "아이템의 에너지 버퍼가 가득 차면 출력 슬롯으로 자동 이동합니다.$(br2)충전을 "
        "중단하려면 배출 버튼을 눌러 아이템을 즉시 출력 슬롯으로 옮기세요."
    ),
    ("entries/energizer/part-powerportfe.json", "pages.0.text"): (
        "수동형 FE 전력 포트로 에너자이저에 에너지를 넣거나 꺼낼 수 있습니다.$(br2)"
        "Forge Energy 호환 케이블이나 기계를 연결할 수 있지만, 연결된 블록이 스스로 "
        "에너지를 보내거나 가져가야 합니다."
    ),
    ("entries/energizer/part-powerportfe_active.json", "pages.0.text"): (
        "능동형 FE 전력 포트로 에너자이저에 에너지를 넣거나 꺼낼 수 있습니다.$(br2)"
        "Forge Energy 호환 케이블이나 기계를 연결하면, 연결된 블록이 지원하는 경우 포트가 "
        "에너지를 자동으로 전달합니다."
    ),
    ("categories/fluidizer-parts.json", "description"): (
        "유체화기는 다음 부품으로 만듭니다.$(br2)모든 부품이 필수이지만, 유리는 기계의 "
        "네 수직 면에서 외장을 대신할 수 있고 주입기는 작동 방식에 맞춰 선택합니다.$(br2)"
        "주입기의 종류와 수에 따라 $(l:bigreactors:fluidizer/operational_mode)작동 방식$(/l)이 "
        "결정됩니다."
    ),
    ("categories/reprocessor-parts.json", "description"): (
        "재처리기는 다음 부품으로 만듭니다.$(br2)모든 부품이 필수이지만, 유리는 기계의 "
        "네 수직 면에서 외장을 대신할 수 있습니다."
    ),
    ("entries/fluidizer/operational_mode.json", "pages.0.text"): (
        "유체화기는 주입기의 종류와 수에 따라 다음 세 방식으로 재료를 처리합니다:"
        "$(br2)$(li)$(o)고체 방식: $()주괴 같은 고체 연료를 유체 연료로 바꿉니다. "
        "이 방식을 사용하려면 고체 주입기가 정확히 하나 있어야 합니다."
    ),
    ("entries/fluidizer/howtobuild.json", "pages.0.text"): (
        "유체화기는 최소 3x3x3 크기이며, 외장과 다른 장치 부품으로 만듭니다.$(br)기계의 "
        "면에서는 외장 대신 유리를 사용할 수 있지만 틀에는 사용할 수 없습니다.$(br2)"
        "부품별 설치 위치 제한은 각 유체화기 부품 페이지에서 확인하세요."
    ),
    ("entries/fluidizer/part-casing.json", "pages.0.text"): (
        "외장은 유체화기의 기본 구성 블록입니다.$(br2)틀을 만들고 다른 부품을 제작하는 데 "
        "필요합니다. 유리를 쓰지 않으려면 유체화기의 면도 외장으로 채울 수 있습니다."
    ),
    ("entries/fluidizer/part-controller.json", "pages.0.text"): (
        "제어기는 유체화기의 주 화면입니다.$(br2)제어기를 우클릭해 유체화기를 켜거나 "
        "끄고, 저장된 유체와 에너지 양 및 현재 작업 상태를 확인할 수 있습니다."
    ),
    ("entries/fluidizer/part-controller.json", "pages.1.text"): (
        "화면의 조작 요소에 마우스를 올리면 자세한 정보와 설명이 툴팁으로 표시됩니다.$(br2)"
    ),
    ("entries/fluidizer/part-controller.json", "pages.2.text"): (
        "$(l)필수 여부:$() 정확히 하나$(br)$(l)설치 가능 위치:$() 틀이 아닌 수직 면"
        "$(br)$(l)화면:$() 있음"
    ),
    ("entries/fluidizer/part-fluidinjector.json", "pages.0.text"): (
        "유체 주입기로 기존 유체 연료를 유체화기에 넣어 섞고 새 연료를 만들 수 있습니다."
    ),
    ("entries/fluidizer/part-glass.json", "pages.0.text"): (
        "유리는 외장 대신 사용해 유체화기 내부를 보여 주는 장식 블록입니다."
    ),
    ("entries/fluidizer/part-outputport.json", "pages.0.text"): (
        "출력 포트로 유체화기의 유체 연료를 꺼낼 수 있습니다.$(br2)파이프를 연결하면 "
        "연료를 자동으로 내보냅니다."
    ),
    ("entries/fluidizer/part-powerport.json", "pages.0.text"): (
        "전력 포트로 유체화기에 필요한 에너지를 공급합니다.$(br2)Forge Energy 호환 "
        "케이블이나 발전기를 연결할 수 있습니다."
    ),
    ("entries/fluidizer/part-solidinjector.json", "pages.0.text"): (
        "고체 주입기로 주괴 같은 고체 연료를 유체화기에 넣어 유체로 바꾸거나, 다른 연료와 "
        "섞어 새 연료를 만들 수 있습니다."
    ),
    ("entries/intro/first.json", "pages.10.text"): (
        "원자로가 가열되면 에너지가 서서히 생성되어 내부 에너지 버퍼에 저장됩니다.$(br2)"
        "저장된 에너지를 사용하려면 능동형 Forge 전력 탭에 에너지 파이프나 기계를 "
        "연결하세요.$(br)연결된 블록이 에너지를 받을 수 있으면 전력 탭이 에너지를 보냅니다."
    ),
    ("entries/intro/er.json", "pages.0.text"): (
        "Minecraft용 $(bold)Extreme Reactors$() 모드에 오신 것을 환영합니다. 고급 원자로와 "
        "터빈으로 막대한 원자력 에너지를 다룰 수 있습니다. 여러 발전 구조를 조합해 필요한 "
        "용량과 효율에 맞는 전력 설비를 만드세요."
    ),
    ("entries/intro/er.json", "pages.1.text"): (
        "$(bold)개요$()$(br)$(bold)Extreme Reactors$()에서는 여러 부품과 구성을 사용해 "
        "원자로와 터빈을 만들고 관리합니다. 에너지 생산과 유체 흐름을 조절해 효율 높은 "
        "발전 체계를 구축할 수 있습니다."
    ),
    ("entries/intro/er.json", "pages.2.text"): (
        "$(bold)주요 장치$()$(li)$(o)$(bold)원자로:$() 발전 설비의 중심입니다. 수동 냉각과 "
        "능동 냉각 중 하나를 선택하고 연료 종류, 제어봉 삽입량, 폐기물 배출을 관리해 성능을 "
        "최적화하세요.$(li)$(o)$(bold)터빈:$() 원자로가 만든 증기로 복잡한 회전자를 돌려 "
        "에너지를 생성합니다. 기본형부터 강화형까지 다양한 설계로 유체 입출력과 발전량을 "
        "필요에 맞게 확장할 수 있습니다."
    ),
    ("entries/intro/er.json", "pages.3.text"): (
        "$(bold)자동화와 제어$()$(br)레드스톤 신호로 원자로와 터빈을 제어하면 다른 "
        "Minecraft 기계와 연동할 수 있습니다. 유체, 에너지, 폐기물을 다루는 여러 포트와 "
        "화면을 이용해 설비 전체를 자동화하세요."
    ),
    ("entries/intro/er.json", "pages.4.text"): (
        "$(bold)건설과 구성$()$(br)원자로와 터빈에는 외장, 회전자 축, 유도 코일과 여러 "
        "포트가 필요합니다. 이 가이드는 각 부품의 조립 방법과 효율적인 설정을 설명합니다."
    ),
    ("entries/intro/er.json", "pages.5.text"): (
        "$(bold)시작하기$()$(br)$(bold)Extreme Reactors$()를 익히면서 에너지 생산과 "
        "관리의 균형을 찾아보세요. 모드 플레이 경험과 관계없이 이 가이드에서 원자력 발전에 "
        "필요한 지식과 도구를 배울 수 있습니다."
    ),
    ("entries/intro/first.json", "pages.0.text"): (
        "원자로는 아주 많은 에너지를 생산하는 멀티블록 기계입니다.$(br2)멀티블록 기계는 "
        "월드에 여러 블록을 서로 맞닿게 배치해 만듭니다.$(br2)원자로 제작과 가동에는 "
        "옐로륨 주괴가 필요하므로 옐로라이트 광석을 채굴해 제련하세요."
    ),
    ("entries/intro/first.json", "pages.6.text"): (
        "필요한 블록을 모두 만들었다면 첫 원자로를 건설할 준비가 되었습니다.$(br2)아래 "
        "도면처럼 블록을 놓고, 중앙 연료봉 아래에는 외장을 놓으세요."
    ),
    ("entries/intro/first.json", "pages.8.text"): (
        "마지막 블록을 놓으면 원자로가 완성되고 제어기를 우클릭해 화면을 열 수 있습니다."
        "$(br2)완성되지 않으면 설치한 블록을 우클릭하세요. 문제를 설명하는 오류 메시지가 "
        "표시됩니다. 오류를 고친 뒤 원자로가 완성되었는지 다시 확인하세요."
    ),
    ("entries/intro/first.json", "pages.9.text"): (
        "원자로가 준비되었으니 연료를 넣을 차례입니다.$(br2)옐로륨 주괴를 더 준비하고 "
        "고체 반입출 포트를 우클릭하세요. 포트를 입력 모드로 바꾼 뒤 주괴를 입력 슬롯에 "
        "넣습니다.$(br2)주괴는 빠르게 소비되어 원자로 연료로 바뀝니다.$(br2)제어기 화면을 "
        "열고 원자로를 켜세요."
    ),
    ("entries/intro/first.json", "pages.11.text"): (
        "축하합니다. 첫 원자로를 완성했습니다!$(br2)게임 초반에 필요한 에너지를 생산하고, "
        "가이드의 나머지 내용을 읽은 뒤 더 큰 원자로와 터빈을 만들어 보세요."
    ),
    ("entries/misc/coolantsystem.json", "pages.1.text"): (
        "$(bold)증기$()는 원자로 안에서 냉각재를 기화해 만든 유체입니다. "
        "$(l:bigreactors/part-forgefluidport)유체 포트$(/l)를 사용해 원자로에서 터빈으로 "
        "보내 회전자를 돌린 뒤 원래 냉각재로 다시 응축할 수 있으므로 순환 과정이 이어집니다."
        "$(br2)원자로와 터빈에는 유효한 냉각재와 증기만 사용할 수 있습니다."
    ),
    ("entries/misc/coolantsystem.json", "pages.0.text"): (
        "$(l:bigreactors/active)능동 냉각$(/l) 원자로·터빈 설비는 원자로의 열로 냉각재를 "
        "기화합니다. 생성된 증기는 여러 터빈의 회전자를 돌려 에너지를 생산합니다.$(br2)"
        "$(bold)냉각재$()는 원자로가 인식하는 유체입니다. 입력 모드의 "
        "$(l:bigreactors/part-forgefluidport)유체 포트$(/l)로 냉각재 탱크에 공급하세요."
    ),
    ("entries/misc/coolantsystem.json", "pages.2.text"): (
        "Extreme Reactors는 기본적으로 물을 냉각재로, 그 결과인 증기를 기체로 등록합니다."
        "$(br2)다른 모드나 모드팩에서 유체를 추가하거나 기본 냉각재와 증기를 변경·제거할 "
        "수 있습니다."
    ),
    ("entries/misc/passiveactiveparts.json", "pages.0.text"): (
        "외부 블록과 상호 작용하는 일부 원자로·터빈 부품은 $(bold)수동형$() 또는 "
        "$(bold)능동형$()으로 제공되며, 두 형태가 모두 있는 부품도 있습니다.$(br2)"
        "$(bold)수동형$() 부품은 스스로 에너지, 유체, 아이템을 보내거나 가져오지 않습니다. "
        "연결된 블록이 전송을 시작해야 합니다."
    ),
    ("entries/misc/passiveactiveparts.json", "pages.1.text"): (
        "$(bold)능동형$() 부품은 연결된 블록으로 에너지, 유체, 아이템을 보내거나 외부에서 "
        "가져오려고 합니다. 대신 연결된 블록이 이 부품에 직접 넣거나 꺼내는 동작은 허용하지 "
        "않습니다.$(br2)수동형과 능동형 부품을 조합해 자원 분배와 회수 방식을 세밀하게 "
        "구성할 수 있습니다."
    ),
    ("entries/misc/powersystem.json", "pages.0.text"): (
        "Extreme Reactors의 에너지 생성기는 특정 전력 체계에 종속되지 않도록 설계되었습니다."
        "$(br2)생성된 에너지는 내부 버퍼에 저장되며, 전력 탭으로 꺼낼 때 연결된 전력 "
        "체계에 맞게 변환됩니다."
    ),
    ("entries/misc/powersystem.json", "pages.1.text"): (
        "원자로나 터빈에 설치한 전력 탭이 기계의 출력 전력 체계를 결정합니다.$(br2)현재는 "
        "$(l:bigreactors/part-forgepowertap)Forge Energy 전력 탭$(/l)이 있으며, "
        "$(bold)Forge Energy$() 장치로 에너지를 보냅니다.$(br2)새 전력 탭 종류를 "
        "추가하면 다른 전력 체계도 지원할 수 있습니다."
    ),
    ("entries/misc/wrench.json", "pages.0.text"): (
        "익스트림 렌치는 말 그대로 렌치입니다.$(br2)반입출 포트나 유체 포트 같은 부품의 "
        "입력·출력 모드를 바꿀 수 있습니다.$(br2)Forge 렌치 태그가 지정되어 있어 다른 "
        "모드에서도 사용할 수 있습니다."
    ),
    ("entries/fluidizer/operational_mode.json", "pages.1.text"): (
        "$(li)$(o)고체 혼합 방식: $()고체 연료 두 종류를 유체로 바꿔 섞고 새 연료를 "
        "만듭니다. 이 방식을 사용하려면 고체 주입기가 정확히 두 개 있어야 합니다."
        "$(li)$(o)유체 혼합 방식: $()유체 연료 두 종류를 섞어 새 연료를 만듭니다. "
        "이 방식을 사용하려면 유체 주입기가 정확히 두 개 있어야 합니다."
    ),
    ("entries/intro/first.json", "pages.2.text"): (
        "첫 원자로를 만들려면 다음 기본 원자로 블록을 준비하세요:$(br2)"
        "$(li)외장 22개$(li)제어기 1개$(li)제어봉 1개$(li)연료봉 1개"
        "$(li)고체 반입출 포트 1개$(li)능동형 Forge Energy 전력 탭 1개$(br2)"
        "유리는 선택 사항이며 외장 블록으로 대신할 수 있습니다."
    ),
    ("entries/reactor/moderators.json", "pages.0.text"): (
        "방사선 감속재는 원자로 내부에 놓아 연료가 방출한 방사선 일부를 흡수하고 "
        "$(l:bigreactors/innerworking)열을 이동$(/l)시키는 블록이나 유체입니다. 열을 "
        "$(l:bigreactors/part-fuelrod)연료봉$(/l)에서 멀리 옮깁니다.$(br2)감속재마다 "
        "방사선을 열로 바꾸는 효율, 방사선 흡수량, 열전도율이 서로 다릅니다."
    ),
    ("entries/reactor/active.json", "pages.1.text"): (
        "능동 냉각 원자로를 만들려면 멀티블록에 유체 포트를 최소 두 개 넣어야 합니다. "
        "하나는 냉각재를 원자로에 넣도록 설정하고, 다른 하나는 생성된 증기를 꺼내도록 "
        "설정하세요.$(br2)꺼낸 증기를 터빈으로 보내 에너지를 생성할 수 있습니다."
    ),
    ("entries/reactor/basic-variant.json", "pages.0.text"): (
        "기본형은 처음 만드는 원자로에 적합합니다.$(br2)외부 크기는 최대 5x5x5이며 "
        "대부분 철 주괴만으로 만들 수 있어 게임 초반에 저렴하게 에너지를 생산할 수 있습니다."
    ),
    ("entries/reactor/innerworking.json", "pages.0.text"): (
        "원자로는 어떻게 $(l:bigreactors/passive)에너지를 생성$(/l)하거나 "
        "$(l:bigreactors/active)냉각재를 기화$(/l)할까요?$(br2)답은 열입니다.$(br2)"
        "방사선을 받은 $(l:bigreactors/reactants)연료$(/l)가 뜨거워지고, "
        "$(l:bigreactors/moderators)감속재$(/l)가 방사선 일부를 흡수해 열을 "
        "$(l:bigreactors/part-fuelrod)연료봉$(/l)에서 "
        "$(l:bigreactors/part-casing)외장$(/l) 쪽으로 옮깁니다.$(br2)외장의 열이 "
        "에너지를 생성하거나 $(l:bigreactors/coolantsystem)냉각재$(/l)를 기화합니다."
    ),
    ("entries/reactor/innerworking.json", "pages.1.text"): (
        "열을 $(l:bigreactors/part-fuelrod)연료봉$(/l)에서 멀리 옮기는 것은 원자로 "
        "설계의 핵심이며, $(l:bigreactors/moderators)감속재$(/l)가 중요한 역할을 합니다. "
        "방사선은 $(l:bigreactors/part-fuelrod)연료봉$(/l) 기둥의 축과 직각인 모든 방향으로 "
        "퍼집니다.$(br2)$(italic)이 설명은 좋은 원자로를 설계하는 데 필요한 정도로 실제 "
        "내부 작동을 단순화한 내용입니다.$()"
    ),
    ("entries/reactor/moderators.json", "pages.1.text"): (
        "아주 싸지만 전체 효율이 매우 낮을 수도 있습니다. 공기가 그 예로, 작동은 하지만 "
        "효율이 거의 없습니다.$(br2)보통 희귀하거나 제작 비용이 높은 블록과 유체일수록 "
        "성능이 좋습니다.$(br2)Extreme Reactors는 기본적으로 여러 Minecraft 및 모드 "
        "블록·유체를 감속재로 등록합니다.$(br)다른 모드나 모드팩에서 감속재를 추가하거나 "
        "기본값을 변경·제거할 수 있습니다."
    ),
    ("entries/reactor/moderators.json", "pages.2.text"): (
        "유효한 감속재만 원자로 내부에 놓을 수 있습니다. 유효하지 않은 블록을 넣으면 "
        "멀티블록이 완성되지 않습니다.$(br2)감속재로 사용할 수 있는 블록과 유체 양동이는 "
        "Minecraft의 $(italic)고급 툴팁$() 기능(F3 + H)을 켰을 때 전용 툴팁으로 확인할 "
        "수 있습니다."
    ),
    ("entries/reactor/part-casing.json", "pages.0.text"): (
        "외장은 원자로의 기본 구성 블록입니다.$(br2)틀을 만들고 다른 부품을 제작하는 데 "
        "필요합니다. 유리를 쓰지 않으려면 원자로의 면도 외장으로 채울 수 있습니다.$(br2)"
        "아주 많이 만들게 될 겁니다."
    ),
    ("entries/reactor/part-casing.json", "pages.2.text"): (
        "$(l)필수 여부:$() 틀 전체$(br)$(l)설치 가능 위치:$() 아무 곳"
        "$(br)$(l)종류:$() 전체$(br)$(l)화면:$() 없음"
    ),
    ("entries/reactor/part-computerport.json", "pages.0.text"): (
        "컴퓨터 포트로 원자로를 컴퓨터에 연결해 복잡한 자동화를 구성할 수 있습니다.$(br2)"
        "연결된 컴퓨터에는 표준 메서드가 제공되며, 원자로 상태를 조회하고 동작을 제어할 수 "
        "있습니다."
    ),
    ("entries/reactor/part-controller.json", "pages.0.text"): (
        "제어기는 원자로의 주 화면입니다.$(br2)제어기를 우클릭해 원자로를 켜거나 끄고, "
        "연료봉의 반응물 양과 원자로 온도 등을 확인할 수 있습니다."
    ),
    ("entries/reactor/part-controller.json", "pages.1.text"): (
        "$(l:bigreactors/passive)수동 냉각$(/l) 원자로에서는 내부 에너지 버퍼와 생산량을, "
        "$(l:bigreactors/active)능동 냉각$(/l) 원자로에서는 냉각재와 증기 양을 확인할 수 "
        "있습니다.$(br2)화면의 조작 요소에 마우스를 올리면 자세한 정보와 설명이 툴팁으로 "
        "표시됩니다."
    ),
    ("entries/reactor/part-controlrod.json", "pages.0.text"): (
        "제어봉은 각 $(l:bigreactors/part-fuelrod)연료봉$(/l) 기둥 안으로 삽입할 수 "
        "있습니다. 제어봉의 재료가 중성자 방사선을 흡수해 "
        "$(l:bigreactors/part-fuelrod)연료봉$(/l) 속 반응물에 닿는 양을 줄이므로 연료 "
        "소비와 열·폐기물 생성을 늦추거나 멈출 수 있습니다."
    ),
    ("entries/reactor/part-controlrod.json", "pages.1.text"): (
        "제어봉을 우클릭해 화면을 여세요.$(br2)각 제어봉에 이름을 지정하면 "
        "$(l:bigreactors/part-computerport)컴퓨터 포트$(/l)로 원자로를 제어할 때 구분할 "
        "수 있습니다.$(br2)삽입 비율은 제어봉이 "
        "$(l:bigreactors/part-fuelrod)연료봉$(/l) 기둥에 들어가는 정도입니다. 이 제어봉 "
        "하나만 바꾸거나 모든 제어봉을 한꺼번에 바꿀 수 있습니다."
    ),
    ("entries/reactor/part-controlrod.json", "pages.3.text"): (
        "$(l)필수 여부:$() 있음$(br)$(l)설치 가능 위치:$() 연료봉 기둥 끝의 한쪽 면"
        "$(br)$(l)종류:$() 전체$(br)$(l)화면:$() 있음"
    ),
    ("entries/reactor/part-creativewatergen.json", "pages.0.text"): (
        "물 생성기는 $(l:bigreactors/active)능동 냉각$(/l) 원자로에 물을 계속 공급하는 "
        "크리에이티브 전용 부품입니다.$(br2)원자로가 켜져 있을 때만 냉각재 유체 탱크에 "
        "자동으로 물 한 양동이를 공급합니다."
    ),
    ("entries/reactor/part-creativewatergen.json", "pages.1.text"): (
        "$(l)필수 여부:$() 없음$(br)$(l)설치 가능 위치:$() 틀이 아닌 모든 면"
        "$(br)$(l)종류:$() 강화$(br)$(l)화면:$() 없음$(br)"
        "$(l)크리에이티브 모드:$() 크리에이티브 전용이며 조합법이 없습니다."
    ),
    ("entries/reactor/part-fluidaccessport.json", "pages.0.text"): (
        "연료 주입 포트는 원자로의 $(l:bigreactors:reactor/part-fuelrod)연료봉$(/l)에 "
        "유체 연료를 넣고 유체 폐기물을 꺼냅니다.$(br2)화면에서 포트를 "
        "$(bold)입력 모드$()로 설정하면 유체 연료를 받고, $(bold)출력 모드$()로 설정하면 "
        "유체 폐기물을 내보냅니다."
    ),
    ("entries/reactor/part-redstoneport.json", "pages.4.text"): (
        "$(li)$(o)증기 양: $()원자로의 증기 양이 설정값보다 높거나 낮거나 범위 안에 "
        "있을 때 신호를 출력합니다.$(br2)원자로를 완전히 자동화하려면 보통 레드스톤 포트가 "
        "두 개 이상 필요합니다.$(br2)더 복잡한 자동화는 "
        "$(l:bigreactors:reactor/part-computerport)컴퓨터 포트$(/l)를 확인하세요."
    ),
    ("entries/reactor/part-fluidaccessport.json", "pages.1.text"): (
        "$(l:bigreactors/wrench)렌치$(/l)로 포트의 입력·출력 모드를 바꿀 수 있습니다."
        "$(br2)고체 반입출 포트와 달리 연료 주입 포트를 사용하면 재료가 손실되지 않습니다."
    ),
    ("entries/reactor/part-fluidaccessport.json", "pages.2.text"): (
        "$(l)필수 여부:$() 없음$(br)$(l)설치 가능 위치:$() 틀이 아닌 모든 면"
        "$(br)$(l)종류:$() 강화$(br)$(l)화면:$() 있음$(br)$(l)렌치:$() "
        "$(l:bigreactors:misc/wrench)렌치$(/l)로 포트 모드를 전환할 수 있습니다."
    ),
    ("entries/reactor/part-forgechargingport.json", "pages.0.text"): (
        "Forge 충전 포트는 $(l:bigreactors/passive)수동 냉각$(/l) 원자로에 저장된 "
        "에너지로 Forge Energy $(l:bigreactors/powersystem)전력 체계$(/l)를 사용하는 "
        "아이템을 충전합니다.$(br2)포트 화면을 열고 충전할 아이템을 가운데 입력 슬롯에 "
        "넣으세요."
    ),
    ("entries/reactor/part-forgefluidport.json", "pages.0.text"): (
        "Forge 유체 포트는 $(l:bigreactors/active)능동 냉각$(/l) 원자로에 유체를 넣거나 "
        "꺼냅니다.$(br2)Minecraft 유체 중 유효한 "
        "$(l:bigreactors/coolantsystem)냉각재와 증기$(/l)만 받을 수 있습니다.$(br2)"
        "$(l:bigreactors/wrench)렌치$(/l)로 입력·출력 모드를 바꿀 수 있습니다."
    ),
    ("entries/reactor/part-forgepowertap.json", "pages.0.text"): (
        "Forge Energy 전력 탭은 $(l:bigreactors/passive)수동 냉각$(/l) 원자로에서 "
        "에너지를 꺼냅니다. Forge Energy $(l:bigreactors/powersystem)전력 체계$(/l)로 "
        "출력하므로 이 체계와 호환되는 파이프나 기계에만 연결할 수 있습니다."
    ),
    ("entries/reactor/part-forgepowertap.json", "pages.1.text"): (
        "원자로 하나에는 $(l:bigreactors/powersystem)전력 체계$(/l)를 하나만 사용할 수 "
        "있으므로 전력 탭도 한 종류만 설치할 수 있습니다. 전력 탭은 "
        "$(l:bigreactors/passiveactiveparts)수동형과 능동형$(/l)으로 제공됩니다."
    ),
    ("entries/reactor/part-fuelrod.json", "pages.0.text"): (
        "연료봉은 원자로 내부에 긴 수직 또는 수평 기둥으로 놓습니다. 연료와 폐기물 같은 "
        "반응물을 저장하며, 원자로가 작동하면 방사선을 받아 열을 생성합니다. 이 열은 에너지 "
        "생성이나 냉각재 기화에 사용됩니다."
    ),
    ("entries/reactor/part-fuelrod.json", "pages.1.text"): (
        "각 기둥의 첫 연료봉은 $(l:bigreactors/part-casing)외장$(/l)에 닿아야 하고, "
        "마지막 연료봉 뒤에는 $(l:bigreactors/part-controlrod)제어봉$(/l)이 있어야 합니다. "
        "모든 연료봉 기둥은 수직(Y축) 또는 수평(X축이나 Z축) 중 한 방향으로 통일해야 하며 "
        "방향을 섞을 수 없습니다. 따라서 모든 제어봉은 원자로의 같은 면에 놓이게 됩니다."
    ),
    ("entries/reactor/part-mekanismfluidport.json", "pages.0.text"): (
        "Mekanism 유체 포트는 $(l:bigreactors:reactor/active)능동 냉각$(/l) 원자로의 "
        "증기를 Mekanism 화학 기체로 꺼냅니다.$(br2)원자로 속 유체에 Mekanism 회전식 "
        "조합법이 있으면 증기를 자동으로 기체로 바꾸며, 조합법에 정의된 변환 비율을 따릅니다."
    ),
    ("entries/reactor/part-redstoneport.json", "pages.0.text"): (
        "레드스톤 포트로 레드스톤 신호를 사용해 원자로를 자동화할 수 있습니다.$(br2)"
        "포트 화면을 열어 설정하세요. 신호를 받는 입력 설정 세 가지와 신호를 내보내는 "
        "출력 설정 여섯 가지 중에서 선택할 수 있습니다."
    ),
    ("entries/reactor/part-redstoneport.json", "pages.1.text"): (
        "$(bold)입력 설정$()$(br2)레드스톤 신호를 받으면 다음 동작 중 하나를 수행합니다."
        "$(br2)$(li)$(o)켜기/끄기: $()받은 신호에 따라 원자로를 켜거나 끕니다."
        "$(li)$(o)폐기물 배출: $()폐기물을 출력 모드의 반입출 포트로 보냅니다."
        "$(li)$(o)제어봉 삽입: $()원자로의 모든 제어봉 삽입 비율을 설정합니다."
    ),
    ("entries/reactor/part-redstoneport.json", "pages.2.text"): (
        "$(bold)출력 설정$()$(br2)다음 조건 중 하나를 만족하면 레드스톤 신호를 내보냅니다."
        "$(br2)$(li)$(o)외장 온도: $()원자로 외장 온도가 설정값보다 높거나 낮거나 범위 "
        "안에 있을 때입니다.$(li)$(o)노심 온도: $()원자로 노심 온도가 설정값보다 높거나 "
        "낮거나 범위 안에 있을 때입니다.$(li)$(o)연료 반응성: $()연료 반응성 비율이 "
        "설정값보다 높거나 낮거나 범위 안에 있을 때입니다."
    ),
    ("entries/reactor/part-redstoneport.json", "pages.3.text"): (
        "$(li)$(o)연료 양: $()연료 양이 설정값보다 높거나 낮거나 범위 안에 있을 때입니다."
        "$(li)$(o)폐기물 양: $()폐기물 양이 설정값보다 높거나 낮거나 범위 안에 있을 때입니다."
        "$(li)$(o)저장된 에너지: $()내부 버퍼의 에너지 양이 설정값보다 높거나 낮거나 범위 "
        "안에 있을 때입니다.$(li)$(o)냉각재 양: $()냉각재 양이 설정값보다 높거나 낮거나 "
        "범위 안에 있을 때입니다."
    ),
    ("entries/reactor/part-solidaccessport.json", "pages.0.text"): (
        "고체 반입출 포트는 주괴 같은 고체 재료를 원자로의 "
        "$(l:bigreactors:reactor/part-fuelrod)연료봉$(/l)에 들어갈 연료 반응물로 바꾸고, "
        "고체 폐기물을 꺼냅니다.$(br2)화면에서 포트를 $(bold)입력 모드$()로 설정하면 "
        "연료 재료를 받고, $(bold)출력 모드$()로 설정하면 폐기물을 내보냅니다."
    ),
    ("entries/reactor/part-solidaccessport.json", "pages.1.text"): (
        "$(l:bigreactors:misc/wrench)렌치$(/l)로 포트 모드를 바꿀 수 있습니다.$(br2)"
        "화면에서 재료를 손으로 넣거나 꺼낼 수도 있습니다.$(br2)고체 반입출 포트는 연료를 "
        "빠르게 넣는 방법이지만 변환 과정에서 재료가 조금 손실됩니다."
    ),
    ("entries/reactor/part-solidaccessport.json", "pages.3.text"): (
        "$(l)필수 여부:$() 필수는 아니지만 사실상 필요$(br)$(l)설치 가능 위치:$() 틀이 "
        "아닌 모든 면$(br)$(l)종류:$() 전체$(br)$(l)화면:$() 있음$(br)$(l)렌치:$() "
        "$(l:bigreactors:misc/wrench)렌치$(/l)로 포트 모드를 전환할 수 있습니다."
    ),
    ("entries/reactor/passive.json", "pages.0.text"): (
        "수동 냉각 원자로는 외부 냉각재 없이 내부 열로 "
        "$(l:bigreactors:reactor/innerworking)에너지를 직접 생성$(/l)합니다.$(br2)이 책의 "
        "앞부분에서 설명한 $(l:bigreactors:intro/first)첫 원자로$(/l)가 수동 냉각 방식입니다."
    ),
    ("entries/reactor/reactants.json", "pages.0.text"): (
        "반응물은 원자로 안에서 핵반응을 유지하는 데 사용하는 화학 물질입니다.$(br2)"
        "반응물은 두 종류입니다:$(li)$(bold)연료:$() "
        "$(l:bigreactors:reactor/part-fuelrod)연료봉$(/l) 안에서 핵분열 연쇄 반응을 "
        "유지합니다.$(li)$(bold)폐기물:$() 연료가 소모된 뒤 생기는 부산물입니다."
    ),
    ("entries/reactor/reactants.json", "pages.1.text"): (
        "Extreme Reactors에는 기본적으로 네 가지 반응물이 있습니다. 연료인 옐로륨과 "
        "블루토늄, 그리고 각각의 폐기물인 시아나이트와 마젠타이트입니다.$(br2)각 반응물은 "
        "그 반응물을 만들 수 있는 아이템 목록을 가집니다. 예를 들어 아이템을 "
        "$(l:bigreactors:reactor/part-solidaccessport)고체 반입출 포트$(/l)에 넣어 반응물로 "
        "바꿀 수 있습니다.$(br2)옐로륨은 $(l:bigreactors:intro/ores)옐로륨 주괴$(/l)에서 "
        "얻습니다. 시아나이트는 원자로에서 배출되면 시아나이트 주괴가 됩니다."
    ),
    ("entries/reactor/reactants.json", "pages.2.text"): (
        "일부 반응물은 $(l:bigreactors:reprocessor/reprocessing)재처리기$(/l)에서 폐기물을 "
        "새 연료로 바꾸어 만들 수 있습니다.$(br2)연료 종류마다 고유한 속성이 있어 원자로 "
        "안에서 서로 다르게 작동합니다.$(br2)다른 모드나 모드팩에서 반응물, 연료 종류와 "
        "원료를 추가하거나 기본값을 변경·제거할 수 있습니다."
    ),
    ("entries/reactor/reactants.json", "pages.3.text"): (
        "연료 반응물을 만들 수 있는 아이템은 Minecraft의 $(italic)고급 툴팁$() 기능"
        "(F3 + H)을 켰을 때 전용 툴팁으로 확인할 수 있습니다."
    ),
    ("entries/reactor/reinforced-variant.json", "pages.0.text"): (
        "강화형은 필요한 만큼 큰 원자로를 만들어 막대한 에너지를 생성하고 저장할 수 있습니다."
        "$(br2)최대 크기는 Extreme Reactors 설정에서 플레이어, 모드팩 제작자나 서버 "
        "관리자가 최대 256블록까지 지정할 수 있습니다."
    ),
    ("entries/reactor/reinforced-variant.json", "pages.1.text"): (
        "강화 원자로는 구조가 튼튼하고 발전 용량이 매우 크지만, 제작 비용이 더 들고 다른 "
        "종류보다 효율이 낮습니다. 큰 발전 용량이 이런 단점을 충분히 보완합니다."
    ),
    ("entries/reprocessor/howtobuild.json", "pages.0.text"): (
        "재처리기는 가로 3블록, 세로 3블록, 높이 7블록이며 외장과 다른 장치 부품으로 "
        "만듭니다.$(br)기계의 수직 면에서는 외장 대신 유리를 사용할 수 있지만 틀에는 사용할 "
        "수 없습니다.$(br2)부품별 설치 위치 제한은 각 재처리기 부품 페이지에서 확인하세요."
    ),
    ("entries/reprocessor/part-casing.json", "pages.0.text"): (
        "외장은 재처리기의 기본 구성 블록입니다.$(br2)틀을 만들고 다른 부품을 제작하는 데 "
        "필요합니다. 유리를 쓰지 않으려면 재처리기의 면도 외장으로 채울 수 있습니다."
    ),
    ("entries/reprocessor/part-collector.json", "pages.0.text"): (
        "수집기는 재처리 작업이 끝나면 재처리기 내부의 완성된 재료를 회수합니다."
    ),
    ("entries/reprocessor/part-controller.json", "pages.0.text"): (
        "제어기는 재처리기의 주 화면입니다.$(br2)제어기를 우클릭해 재처리기를 켜거나 "
        "끄고, 저장된 유체와 에너지 양 및 현재 재처리 작업 상태를 확인할 수 있습니다."
    ),
    ("entries/reprocessor/part-controller.json", "pages.1.text"): (
        "화면의 조작 요소에 마우스를 올리면 자세한 정보와 설명이 툴팁으로 표시됩니다.$(br2)"
    ),
    ("entries/reprocessor/part-controller.json", "pages.2.text"): (
        "$(l)필수 여부:$() 최소 하나$(br)$(l)설치 가능 위치:$() 틀이 아닌 수직 면"
        "$(br)$(l)화면:$() 있음"
    ),
    ("entries/reprocessor/part-fluidinjector.json", "pages.0.text"): (
        "유체 주입기로 폐기물 재처리에 필요한 유체를 공급합니다.$(br2)폐기물 종류에 따라 "
        "필요한 유체가 다를 수 있습니다."
    ),
    ("entries/reprocessor/part-glass.json", "pages.0.text"): (
        "유리는 외장 대신 사용해 재처리기 내부를 보여 주는 장식 블록입니다."
    ),
    ("entries/reprocessor/part-outputport.json", "pages.0.text"): (
        "출력 포트로 재처리된 재료를 꺼낼 수 있습니다.$(br2)화면에서 손으로 꺼내거나 "
        "파이프를 연결해 자동으로 내보낼 수 있습니다."
    ),
    ("entries/reprocessor/part-powerport.json", "pages.0.text"): (
        "전력 포트로 재처리기에 필요한 에너지를 공급합니다.$(br2)Forge Energy 호환 "
        "케이블이나 발전기를 연결할 수 있습니다."
    ),
    ("entries/reprocessor/part-wasteinjector.json", "pages.0.text"): (
        "폐기물 주입기로 원자로의 폐기물을 재처리기에 넣습니다.$(br2)화면에서 손으로 넣거나 "
        "파이프를 연결해 자동으로 공급할 수 있습니다."
    ),
    ("entries/turbine/coils.json", "pages.0.text"): (
        "유도 코일은 보통 금속 블록이며, 회전자 축 둘레에 놓습니다. 코일을 연결하면 회전 "
        "속도를 낮추는 대신 에너지를 추출합니다.$(br2)코일 종류에 따라 회전 중인 회전자에서 "
        "에너지를 뽑는 효율과 속도가 다릅니다."
    ),
    ("entries/turbine/basic-variant.json", "pages.0.text"): (
        "기본형은 처음 만드는 터빈에 적합합니다.$(br2)최대 크기는 5x5x10이며 대부분 철 "
        "주괴만으로 만들 수 있어 게임 초중반에 저렴하게 에너지를 생산할 수 있습니다."
        "$(br2)기본 터빈은 회전자를 돌리는 데 최대 1000mB/t의 증기를 사용할 수 있습니다."
    ),
    ("entries/turbine/coils.json", "pages.1.text"): (
        "보통 희귀하거나 제작 비용이 높은 블록일수록 성능이 좋습니다.$(br2)Extreme "
        "Reactors는 기본적으로 여러 Minecraft 및 모드 블록을 유도 코일로 등록합니다."
        "$(br2)다른 모드나 모드팩에서 유도 코일을 추가하거나 기본값을 변경·제거할 수 있습니다."
    ),
    ("entries/turbine/coils.json", "pages.2.text"): (
        "유효한 코일만 터빈 내부의 회전자 축 둘레에 놓을 수 있습니다. 유효하지 않은 블록을 "
        "넣으면 멀티블록이 완성되지 않습니다.$(br2)유도 코일로 사용할 수 있는 블록은 "
        "Minecraft의 $(italic)고급 툴팁$() 기능(F3 + H)을 켰을 때 전용 툴팁으로 확인할 "
        "수 있습니다."
    ),
    ("entries/turbine/innerworking.json", "pages.0.text"): (
        "터빈은 어떻게 에너지를 생성할까요?$(br2)$(l:bigreactors/rotor)회전자$(/l)를 "
        "돌려서 생성합니다.$(br2)터빈의 증기 탱크에 있는 유체는 "
        "$(l:bigreactors/part-controller)제어기$(/l) 화면에서 설정한 유량에 따라 "
        "$(l:bigreactors/rotor)회전자$(/l) 공간으로 들어갑니다.$(br2)각 "
        "$(l:bigreactors/part-rotorblade)회전자 날개$(/l)가 증기를 조금씩 받아 "
        "$(l:bigreactors/rotor)회전자$(/l)를 돌립니다."
    ),
    ("entries/turbine/innerworking.json", "pages.1.text"): (
        "$(l:bigreactors/coils)유도 코일$(/l)을 "
        "$(l:bigreactors/part-controller)연결$(/l)하면 "
        "$(l:bigreactors/rotor)회전자$(/l) 속도와 모든 코일의 평균 효율·저항 값에 따라 "
        "에너지가 생성됩니다.$(br2)$(italic)이 설명은 좋은 터빈을 설계하는 데 필요한 정도로 "
        "실제 내부 작동을 단순화한 내용입니다.$()"
    ),
    ("entries/turbine/part-casing.json", "pages.0.text"): (
        "터빈 외장은 터빈의 기본 구성 블록입니다.$(br2)틀을 만들고 "
        "$(l:bigreactors/rotor)회전자$(/l)를 지지하며 다른 부품을 제작하는 데 필요합니다. "
        "유리를 쓰지 않으려면 터빈의 면도 외장으로 채울 수 있습니다.$(br2)아주 많이 만들게 "
        "될 겁니다."
    ),
    ("entries/turbine/part-casing.json", "pages.2.text"): (
        "$(l)필수 여부:$() 틀과 $(l:bigreactors:turbine/rotor)회전자$(/l) 끝"
        "$(br)$(l)설치 가능 위치:$() 아무 곳$(br)$(l)종류:$() 전체"
        "$(br)$(l)화면:$() 없음"
    ),
    ("entries/turbine/part-computerport.json", "pages.0.text"): (
        "컴퓨터 포트로 터빈을 컴퓨터에 연결해 복잡한 자동화를 구성할 수 있습니다.$(br2)"
        "연결된 컴퓨터에는 표준 메서드가 제공되며, 터빈 상태를 조회하고 동작을 제어할 수 "
        "있습니다."
    ),
    ("entries/turbine/part-controller.json", "pages.0.text"): (
        "제어기는 터빈의 주 화면입니다.$(br2)제어기를 우클릭해 터빈을 켜거나 끄고, 내부 "
        "탱크의 증기와 냉각재 양, $(l:bigreactors/rotor)회전자$(/l) 속도와 에너지 생산량을 "
        "확인할 수 있습니다."
    ),
    ("entries/turbine/part-controller.json", "pages.1.text"): (
        "$(l:bigreactors/rotor)회전자$(/l)로 들어가는 증기 유량을 조절하고, 응축된 냉각재의 "
        "처리 방식을 선택하며, $(l:bigreactors/coils)유도 코일$(/l)을 연결하거나 연결 해제할 "
        "수 있습니다.$(br2)화면의 조작 요소에 마우스를 올리면 자세한 정보와 설명이 툴팁으로 "
        "표시됩니다."
    ),
    ("entries/turbine/part-controller.json", "pages.3.text"): (
        "$(l)필수 여부:$() 최소 하나$(br)$(l)설치 가능 위치:$() 틀이 아닌 모든 면"
        "$(br)$(l)종류:$() 전체$(br)$(l)화면:$() 있음"
    ),
    ("entries/turbine/part-creativesteamgen.json", "pages.0.text"): (
        "증기 생성기는 터빈에 증기를 계속 공급하는 크리에이티브 전용 부품입니다.$(br2)"
        "터빈이 켜져 있을 때만 해당 부품 종류가 허용하는 최대량까지 증기 탱크에 자동으로 "
        "증기를 공급합니다."
    ),
    ("entries/turbine/part-creativesteamgen.json", "pages.1.text"): (
        "$(l)필수 여부:$() 없음$(br)$(l)설치 가능 위치:$() 틀이 아닌 모든 면"
        "$(br)$(l)종류:$() 전체$(br)$(l)화면:$() 없음$(br)"
        "$(l)크리에이티브 모드:$() 크리에이티브 전용이며 조합법이 없습니다."
    ),
    ("entries/turbine/part-forgechargingport.json", "pages.0.text"): (
        "Forge 충전 포트는 터빈에 저장된 에너지로 Forge Energy "
        "$(l:bigreactors:misc/powersystem)전력 체계$(/l)를 사용하는 아이템을 충전합니다."
        "$(br2)포트 화면을 열고 충전할 아이템을 가운데 입력 슬롯에 넣으세요."
    ),
    ("entries/turbine/part-forgechargingport.json", "pages.1.text"): (
        "아이템의 에너지 버퍼가 가득 차면 출력 슬롯으로 자동 이동합니다.$(br2)충전을 "
        "중단하려면 배출 버튼을 눌러 아이템을 즉시 출력 슬롯으로 옮기세요."
    ),
    ("entries/turbine/part-forgefluidport.json", "pages.0.text"): (
        "Forge 유체 포트로 터빈에 유체를 넣거나 꺼낼 수 있습니다.$(br2)Minecraft 유체 중 "
        "유효한 $(l:bigreactors:misc/coolantsystem)냉각재와 증기$(/l)만 받을 수 있습니다."
        "$(br2)$(l:bigreactors:misc/wrench)렌치$(/l)로 입력·출력 모드를 바꿀 수 있습니다."
    ),
    ("entries/turbine/part-forgefluidport.json", "pages.3.text"): (
        "$(l)필수 여부:$() 없음$(br)$(l)설치 가능 위치:$() 틀이 아닌 모든 면"
        "$(br)$(l)종류:$() 전체$(br)$(l)화면:$() 없음$(br)$(l)렌치:$() "
        "$(l:bigreactors:misc/wrench)렌치$(/l)로 포트 모드를 전환할 수 있습니다."
    ),
    ("entries/turbine/part-forgepowertap.json", "pages.0.text"): (
        "Forge Energy 전력 탭으로 터빈의 에너지를 꺼낼 수 있습니다.$(br2)Forge Energy "
        "$(l:bigreactors:misc/powersystem)전력 체계$(/l)로 출력하므로 이 체계와 호환되는 "
        "파이프나 기계에만 연결할 수 있습니다."
    ),
    ("entries/turbine/part-forgepowertap.json", "pages.1.text"): (
        "터빈 하나에는 $(l:bigreactors:misc/powersystem)전력 체계$(/l)를 하나만 사용할 수 "
        "있으므로 전력 탭도 한 종류만 설치할 수 있습니다.$(br2)전력 탭은 "
        "$(l:bigreactors:misc/passiveactiveparts)수동형과 능동형$(/l)으로 제공됩니다."
    ),
    ("entries/turbine/part-forgepowertap.json", "pages.4.text"): (
        "$(l)필수 여부:$() 없음$(br)$(l)설치 가능 위치:$() 틀이 아닌 모든 면"
        "$(br)$(l)종류:$() 전체$(br)$(l)화면:$() 없음$(br)"
        "$(l)전력 체계:$() Forge Energy"
    ),
    ("entries/turbine/part-glass.json", "pages.0.text"): (
        "유리는 $(l:bigreactors:turbine/part-casing)터빈 외장$(/l) 대신 사용해 터빈 내부를 "
        "보여 주는 장식 블록입니다."
    ),
    ("entries/turbine/part-glass.json", "pages.2.text"): (
        "$(l)필수 여부:$() 없음$(br)$(l)설치 가능 위치:$() 틀이 아닌 모든 면"
        "$(br)$(l)종류:$() 전체$(br)$(l)화면:$() 없음"
    ),
    ("entries/turbine/part-redstoneport.json", "pages.3.text"): (
        "$(li)$(o)저장된 에너지: $()내부 에너지 버퍼의 에너지 양이 설정값보다 높거나 "
        "낮거나 범위 안에 있을 때 신호를 출력합니다.$(br2)터빈을 완전히 자동화하려면 보통 "
        "레드스톤 포트가 두 개 이상 필요합니다.$(br2)더 복잡한 자동화는 "
        "$(l:bigreactors:turbine/part-computerport)컴퓨터 포트$(/l)를 확인하세요."
    ),
    ("entries/turbine/part-redstoneport.json", "pages.1.text"): (
        "$(bold)입력 설정$()$(br2)레드스톤 신호를 받으면 다음 동작 중 하나를 수행합니다."
        "$(br2)$(li)$(o)켜기/끄기: $()받은 신호에 따라 터빈을 켜거나 끕니다."
        "$(li)$(o)유도 코일: $()유도 코일을 연결하거나 연결 해제합니다."
        "$(li)$(o)유량: $()터빈 내부 증기의 최대 유량을 변경합니다."
    ),
    ("entries/turbine/part-redstoneport.json", "pages.0.text"): (
        "레드스톤 포트로 레드스톤 신호를 사용해 터빈을 자동화할 수 있습니다.$(br2)포트 "
        "화면을 열어 설정하세요. 신호를 받는 입력 설정 세 가지와 신호를 내보내는 출력 설정 "
        "네 가지 중에서 선택할 수 있습니다."
    ),
    ("entries/turbine/part-redstoneport.json", "pages.2.text"): (
        "$(bold)출력 설정$()$(br2)다음 조건 중 하나를 만족하면 레드스톤 신호를 내보냅니다."
        "$(br2)$(li)$(o)회전자 속도: $()회전자 속도가 설정값보다 높거나 낮거나 범위 안에 "
        "있을 때입니다.$(li)$(o)냉각재 양: $()냉각재 양이 설정값보다 높거나 낮거나 범위 "
        "안에 있을 때입니다.$(li)$(o)증기 양: $()증기 양이 설정값보다 높거나 낮거나 범위 "
        "안에 있을 때입니다."
    ),
    ("entries/turbine/part-rotorbearing.json", "pages.0.text"): (
        "회전자 베어링은 터빈 $(l:bigreactors:turbine/rotor)회전자$(/l)의 시작점입니다."
        "$(br2)보통 터빈 면 중앙에 하나를 놓고, 뒤쪽으로 "
        "$(l:bigreactors:turbine/part-rotorshaft)회전자 축$(/l)을 이어 놓습니다."
    ),
    ("entries/turbine/part-rotorbearing.json", "pages.2.text"): (
        "$(l)필수 여부:$() 정확히 하나$(br)$(l)설치 가능 위치:$() 틀이 아닌 모든 면"
        "$(br)$(l)종류:$() 전체$(br)$(l)화면:$() 없음"
    ),
    ("entries/turbine/part-rotorblade.json", "pages.0.text"): (
        "회전자 날개는 $(l:bigreactors:turbine/rotor)회전자$(/l)를 실제로 돌리는 마지막 "
        "부품입니다.$(br2)$(l:bigreactors:turbine/part-rotorshaft)회전자 축$(/l)에 직각으로 "
        "붙이거나, 이미 놓은 날개에서 축의 바깥쪽으로 이어 놓을 수 있습니다."
    ),
    ("entries/turbine/part-rotorblade.json", "pages.2.text"): (
        "$(l)필수 여부:$() 있음$(br)$(l)설치 가능 위치:$() 터빈 내부에서 다른 날개나 "
        "회전자 축에 연결$(br)$(l)종류:$() 전체$(br)$(l)화면:$() 없음"
    ),
    ("entries/turbine/part-rotorshaft.json", "pages.0.text"): (
        "회전자 축은 터빈 $(l:bigreactors:turbine/rotor)회전자$(/l)의 중심 부품입니다."
        "$(br2)축 블록은 터빈 안에서 "
        "$(l:bigreactors:turbine/part-rotorbearing)회전자 베어링$(/l)부터 반대편 "
        "$(l:bigreactors:turbine/part-casing)터빈 외장$(/l)까지 끊김 없이 이어져야 합니다."
        "$(br2)"
    ),
    ("entries/turbine/part-rotorshaft.json", "pages.2.text"): (
        "$(l)필수 여부:$() 있음$(br)$(l)설치 가능 위치:$() 터빈 내부"
        "$(br)$(l)종류:$() 전체$(br)$(l)화면:$() 없음"
    ),
    ("entries/turbine/reinforced-variant.json", "pages.0.text"): (
        "강화형은 필요한 만큼 큰 터빈을 만들어 막대한 에너지를 생성할 수 있습니다.$(br2)"
        "최대 크기는 Extreme Reactors 설정에서 플레이어, 모드팩 제작자나 서버 관리자가 "
        "최대 256블록까지 지정할 수 있습니다.$(br2)강화 터빈은 회전자를 돌리는 데 최대 "
        "2000mB/t의 증기를 사용할 수 있습니다."
    ),
    ("entries/turbine/reinforced-variant.json", "pages.1.text"): (
        "강화 터빈은 구조가 튼튼하고 발전 용량이 매우 크지만, 제작 비용이 더 들고 다른 "
        "종류보다 효율이 낮습니다. 큰 발전 용량이 이런 단점을 충분히 보완합니다."
    ),
    ("entries/turbine/rotor.json", "pages.0.text"): (
        "회전자 설계는 터빈의 $(l:bigreactors:turbine/innerworking)에너지 생산$(/l)에 직접 "
        "영향을 주므로 가장 중요한 요소입니다.$(br2)회전자는 네 종류의 블록으로 만듭니다:"
        "$(li)$(l:bigreactors:turbine/part-rotorbearing)회전자 베어링$(/l) 하나"
        "$(li)$(l:bigreactors:turbine/part-rotorshaft)회전자 축$(/l) 여러 개"
        "$(li)$(l:bigreactors:turbine/part-rotorblade)회전자 날개$(/l) 여러 개"
        "$(li)$(l:bigreactors:turbine/part-casing)터빈 외장$(/l) 하나"
    ),
    ("entries/turbine/rotor.json", "pages.2.text"): (
        "$(bold)회전자 만들기$()$(br2)회전자는 터빈의 X, Y, Z축 중 어느 방향으로든 만들 "
        "수 있습니다.$(br2)첫 블록은 보통 터빈 면 중앙에 놓는 "
        "$(l:bigreactors:turbine/part-rotorbearing)회전자 베어링$(/l)입니다.$(br2)베어링에서 "
        "시작해 반대편 면의 $(l:bigreactors:turbine/part-casing)터빈 외장$(/l)에 닿을 때까지 "
        "$(l:bigreactors:turbine/part-rotorshaft)회전자 축$(/l)을 이어 놓으세요."
    ),
    ("entries/turbine/rotor.json", "pages.3.text"): (
        "축을 완성했으면 $(l:bigreactors:turbine/part-rotorblade)회전자 날개$(/l)를 놓으세요. "
        "$(l:bigreactors:turbine/part-rotorshaft)회전자 축$(/l)에 직각으로 붙이거나 이미 놓은 "
        "날개 옆에 이어 놓을 수 있습니다.$(br2)원하는 조합으로 날개를 필요한 만큼 놓을 수 "
        "있습니다.$(br)날개 수와 각 날개의 증기 용량은 회전자 속도에 직접 영향을 줍니다."
    ),
    ("entries/turbine/rotor.json", "pages.4.text"): (
        "$(bold)날개는 몇 개가 필요할까요?$()$(br2)날개 종류마다 회전자를 돌리는 데 "
        "$(italic)사용$()할 수 있는 최대 증기량이 정해져 있습니다.$(br2)인벤토리에서 날개에 "
        "마우스를 올려 용량을 확인하세요.$(br2)이 값과 제어기 화면에서 설정한 증기 유량을 "
        "비교해 필요한 날개 수를 계산하세요."
    ),
    ("entries/turbine/rotor.json", "pages.5.text"): (
        "$(bold)유도 코일$()$(br2)에너지를 실제로 생성하려면 회전자 끝, 즉 닫는 "
        "$(l:bigreactors:turbine/part-casing)터빈 외장$(/l) 블록 가까이에 "
        "$(l:bigreactors:turbine/coils)유도 코일$(/l)을 놓아야 합니다.$(br2)"
        "$(italic)$(l:bigreactors:turbine/part-controller)제어기$(/l) 화면에서 코일을 "
        "연결하는 것도 잊지 마세요!$()$(br2)코일 고리는 최대 세 줄까지 놓을 수 있고, "
        "각 고리는 코일 블록을 최대 여덟 개까지 사용합니다."
    ),
    ("entries/turbine/rotor.json", "pages.6.text"): (
        "여러 코일 종류를 섞어 사용할 수 있으며, 이때 터빈은 모든 코일 속성의 평균값을 "
        "사용합니다.$(br2)처음에는 구하기 쉽고 값싼 코일을 사용한 뒤, 희귀하고 비싼 코일을 "
        "구할 때마다 조금씩 교체할 수 있습니다.$(br2)다음 페이지에는 앞에서 본 회전자에 "
        "$(l:bigreactors:turbine/coils)유도 코일$(/l)을 추가한 예시가 나옵니다."
    ),
}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def installed_jar() -> Path:
    matches = sorted((resolve_source_root() / "mods").glob("ExtremeReactors2-*.jar"))
    if len(matches) != 1:
        raise FileNotFoundError(f"Extreme Reactors JAR 개수가 1이 아닙니다: {matches}")
    return matches[0]


def visible_locations(
    value: object, path: tuple[object, ...] = ()
) -> list[tuple[tuple[object, ...], str]]:
    rows: list[tuple[tuple[object, ...], str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (*path, key)
            if key in VISIBLE_FIELDS and isinstance(child, str):
                rows.append((child_path, child))
            rows.extend(visible_locations(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(visible_locations(child, (*path, index)))
    return rows


def set_path(value: object, path: tuple[object, ...], replacement: str) -> None:
    current = value
    for part in path[:-1]:
        current = current[part]  # type: ignore[index]
    current[path[-1]] = replacement  # type: ignore[index]


def advancement_translate_keys(value: object) -> list[str]:
    rows: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "translate" and isinstance(child, str):
                rows.append(child)
            rows.extend(advancement_translate_keys(child))
    elif isinstance(value, list):
        for child in value:
            rows.extend(advancement_translate_keys(child))
    return rows


def prepare() -> dict[str, object]:
    jar = installed_jar()
    files = 0
    advancement_rows: list[dict[str, object]] = []
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            if name.startswith(BOOK_PREFIX) and name.endswith(".json"):
                relative = name.removeprefix(BOOK_PREFIX)
                write_json(ENGLISH_ROOT / relative, json.loads(archive.read(name)))
                files += 1
            elif name.startswith(ADVANCEMENT_PREFIX) and name.endswith(".json"):
                data = json.loads(archive.read(name))
                display = data.get("display") if isinstance(data, dict) else None
                keys = advancement_translate_keys(display)
                advancement_rows.append(
                    {
                        "path": name,
                        "has_display": isinstance(display, dict),
                        "translation_keys": keys,
                        "literal_display": isinstance(display, dict) and not keys,
                    }
                )
        write_json(WORK_ROOT / "book_en_us.json", json.loads(archive.read(BOOK_SOURCE)))
    write_json(WORK_ROOT / "advancements.json", advancement_rows)

    instance = resolve_source_root()
    reference = re.compile(r"bigreactors|extreme[ _-]?reactors|zerocore", re.I)
    visible_api = re.compile(
        r"displayName|tooltip|custom_name|Text\.(?:of|translatable)|"
        r'["\'](?:text|title|description)["\']\s*:',
        re.I,
    )
    kubejs_files: list[str] = []
    visible_literals: list[str] = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json", ".snbt"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if not reference.search(text):
            continue
        relative = path.relative_to(instance).as_posix()
        kubejs_files.append(relative)
        if "/lang/" in relative.casefold():
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if reference.search(line) and visible_api.search(line):
                visible_literals.append(f"{relative}:{number}:{line.strip()}")
    report = {
        "jar": jar.name,
        "localized_guide_files": files,
        "book_files": 1,
        "total_guide_files": files + 1,
        "advancements": len(advancement_rows),
        "advancements_with_display": sum(
            row["has_display"] for row in advancement_rows
        ),
        "advancements_with_literal_display": sum(
            row["literal_display"] for row in advancement_rows
        ),
        "kubejs_reference_files": kubejs_files,
        "kubejs_foreign_language_files_excluded": sum(
            "/lang/" in path.casefold() for path in kubejs_files
        ),
        "kubejs_visible_literals": visible_literals,
    }
    write_json(WORK_ROOT / "scope.json", report)
    return report


def mask_tags(source: str) -> tuple[str, list[str]]:
    tags: list[str] = []

    def replace(match: re.Match[str]) -> str:
        tags.append(match.group(0))
        return f"ZXQPATCHOULITAG{len(tags) - 1}QXZ"

    return PATCHOULI_TAG.sub(replace, source), tags


def restore_tags(candidate: str, tags: list[str]) -> str:
    value = candidate
    for index, tag in enumerate(tags):
        value = value.replace(f"ZXQPATCHOULITAG{index}QXZ", tag)
        value = value.replace(f"ZXQPATCHOULITAG {index} QXZ", tag)
    return value


def text_segments(source: str) -> list[str]:
    return [part for part in re.split(r"(\$\([^)]+\))", source) if part]


def location_override_sources() -> set[str]:
    sources: set[str] = set()
    for relative, field in LOCATION_OVERRIDES:
        path = tuple(int(part) if part.isdigit() else part for part in field.split("."))
        value = dict(visible_locations(load_json(ENGLISH_ROOT / relative))).get(path)
        if not isinstance(value, str):
            raise KeyError(f"가이드 위치 재검수 원문이 없습니다: {relative}:{field}")
        sources.add(value)
    return sources


def candidate() -> dict[str, object]:
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    if not isinstance(cache, dict):
        raise TypeError("가이드 후보 캐시가 객체가 아닙니다.")
    overridden_sources = location_override_sources()
    sources = {
        segment
        for path in ENGLISH_ROOT.rglob("*.json")
        for _, source in visible_locations(load_json(path))
        if source not in EXACT_VALUES
        and not TEMPLATE_VALUE.fullmatch(source)
        and source not in overridden_sources
        for segment in text_segments(source)
        if not PATCHOULI_TAG.fullmatch(segment)
        and re.search(r"[A-Za-z]", segment)
        and not isinstance(cache.get(segment), str)
    }
    failures: list[str] = []
    if sources:
        completed = 0
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {}
            for source in sorted(sources):
                futures[executor.submit(ars_family.request_translation, source)] = (
                    source
                )
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
        raise RuntimeError("가이드 후보 생성 실패:\n" + "\n".join(failures))
    locations = sum(
        len(visible_locations(load_json(path))) for path in ENGLISH_ROOT.rglob("*.json")
    )
    report = {
        "visible_locations": locations,
        "unique_sources": len(
            {
                source
                for path in ENGLISH_ROOT.rglob("*.json")
                for _, source in visible_locations(load_json(path))
            }
        ),
        "new_candidate_requests": len(sources),
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


def translated_value(source: str, cache: dict[str, object]) -> str:
    if source in EXACT_VALUES:
        return EXACT_VALUES[source]
    if TEMPLATE_VALUE.fullmatch(source):
        return source
    translated_segments: list[str] = []
    for segment in text_segments(source):
        if PATCHOULI_TAG.fullmatch(segment) or not re.search(r"[A-Za-z]", segment):
            translated_segments.append(segment)
            continue
        candidate_value = cache.get(segment)
        if not isinstance(candidate_value, str):
            raise KeyError(f"가이드 번역 후보가 없습니다: {segment}")
        value = candidate_value.replace(
            "Extreme Reactors", "\ue000EXTREME_REACTORS\ue001"
        )
        for old, new in TEXT_REPLACEMENTS:
            value = value.replace(old, new)
        for old, new in ENGLISH_REPLACEMENTS:
            value = value.replace(old, new)
        for old, new in {
            "yes": "예",
            "no": "아니요",
            "all": "전체",
            "any": "아무 곳",
            "block": "블록",
            "some": "일부",
            "energy": "에너지",
        }.items():
            value = re.sub(rf"(?<![A-Za-z]){old}(?![A-Za-z])", new, value)
        value = value.replace("\ue000EXTREME_REACTORS\ue001", "Extreme Reactors")
        translated_segments.append(value)
    value = "".join(translated_segments)
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    return value


def build() -> dict[str, object]:
    cache = load_json(CACHE_FILE)
    if not isinstance(cache, dict):
        raise TypeError("가이드 후보 캐시가 객체가 아닙니다.")
    files = 0
    locations = 0
    changed = 0
    for source_path in sorted(ENGLISH_ROOT.rglob("*.json")):
        relative = source_path.relative_to(ENGLISH_ROOT)
        data = load_json(source_path)
        for field_path, source in visible_locations(data):
            override = LOCATION_OVERRIDES.get(
                (relative.as_posix(), ".".join(map(str, field_path)))
            )
            translated = override or translated_value(source, cache)
            set_path(data, field_path, translated)
            locations += 1
            changed += int(source != translated)
        write_json(KOREAN_ROOT / relative, data)
        write_json(OUTPUT_ROOT / relative, data)
        files += 1
    book = load_json(WORK_ROOT / "book_en_us.json")
    if not isinstance(book, dict):
        raise TypeError("Patchouli book.json이 객체가 아닙니다.")
    book["name"] = "Extreme 가이드"
    book["landing_text"] = (
        "Extreme Reactors의 기초를 설명하는 안내서, 줄여서 Extreme 가이드입니다.$(br2)"
        "Extreme Reactors는 에너지를 효율적으로 대량 생산하는 모드이며, 이 책은 그 목표를 "
        "달성하는 방법을 안내합니다!"
    )
    write_json(BOOK_OUTPUT, book)
    report = {
        "localized_guide_files": files,
        "book_files": 1,
        "total_guide_files": files + 1,
        "visible_locations": locations,
        "changed": changed,
        "review_status": "all_current_english_guide_strings_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def tag_signature(value: str) -> list[str]:
    return PATCHOULI_TAG.findall(value)


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    untranslated: list[str] = []
    latin_residuals: list[str] = []
    artifacts: list[str] = []
    files = 0
    locations = 0
    for source_path in sorted(ENGLISH_ROOT.rglob("*.json")):
        relative = source_path.relative_to(ENGLISH_ROOT)
        target_path = KOREAN_ROOT / relative
        output_path = OUTPUT_ROOT / relative
        if not target_path.is_file() or not output_path.is_file():
            errors.append(f"가이드 출력 누락: {relative.as_posix()}")
            continue
        source = load_json(source_path)
        target = load_json(target_path)
        if target != load_json(output_path):
            errors.append(f"가이드 누적 출력 불일치: {relative.as_posix()}")
        source_rows = visible_locations(source)
        target_rows = dict(visible_locations(target))
        if [path for path, _ in source_rows] != [
            path for path, _ in visible_locations(target)
        ]:
            errors.append(f"가이드 표시 구조 불일치: {relative.as_posix()}")
        for field_path, source_value in source_rows:
            locations += 1
            label = f"{relative.as_posix()}:{'.'.join(map(str, field_path))}"
            target_value = target_rows.get(field_path)
            if not isinstance(target_value, str):
                errors.append(f"가이드 표시 값 누락: {label}")
                continue
            checks = (
                (
                    "Patchouli 태그",
                    tag_signature(source_value),
                    tag_signature(target_value),
                ),
                ("숫자", NUMBER.findall(source_value), NUMBER.findall(target_value)),
                ("URL", URL.findall(source_value), URL.findall(target_value)),
            )
            for kind, expected, actual in checks:
                if Counter(expected) != Counter(actual):
                    errors.append(f"{kind} 불일치: {label}")
            if (
                source_value == target_value
                and not TEMPLATE_VALUE.fullmatch(source_value)
                and source_value != "Extreme Reactors"
            ):
                untranslated.append(label)
            found = [word for word in FORBIDDEN_ARTIFACTS if word in target_value]
            if found:
                artifacts.append(f"{label}:{','.join(found)}")
            residue = target_value
            for allowed in sorted(ALLOWED_LATIN, key=len, reverse=True):
                residue = residue.replace(allowed, "")
            residue = PATCHOULI_TAG.sub("", residue)
            residue = URL.sub("", residue)
            residue = re.sub(r"#[A-Za-z]+", "", residue)
            if LATIN_WORD.search(residue):
                latin_residuals.append(f"{label}:{target_value}")
        files += 1
    scope = load_json(WORK_ROOT / "scope.json")
    if not isinstance(scope, dict):
        errors.append("가이드 범위 보고서 자료형 불일치")
        scope = {}
    advancements = load_json(WORK_ROOT / "advancements.json")
    if not isinstance(advancements, list):
        errors.append("발전 과제 감사 보고서 자료형 불일치")
        advancements = []
    literal_advancements = [row for row in advancements if row.get("literal_display")]
    if literal_advancements:
        errors.append(f"literal 발전 과제 표시 발견: {len(literal_advancements)}")
    visible_kubejs = scope.get("kubejs_visible_literals", [])
    if visible_kubejs:
        errors.append(f"KubeJS 직접 표시 리터럴 발견: {len(visible_kubejs)}")
    if untranslated:
        errors.append(f"미번역 가이드 문구: {untranslated[:20]}")
    if artifacts:
        errors.append(f"기계번역 잔재: {artifacts[:20]}")
    if latin_residuals:
        errors.append(f"가이드 영어 잔존: {latin_residuals[:20]}")
    book = load_json(BOOK_OUTPUT) if BOOK_OUTPUT.is_file() else {}
    if not isinstance(book, dict) or book.get("name") != "Extreme 가이드":
        errors.append("가이드 책 이름 번역 누락")
    report = {
        "localized_guide_files": files,
        "book_files": 1,
        "total_guide_files": files + 1,
        "visible_locations": locations,
        "untranslated": len(untranslated),
        "machine_translation_artifacts": len(artifacts),
        "latin_residuals": len(latin_residuals),
        "advancements": len(advancements),
        "advancements_with_display": sum(
            row.get("has_display", False) for row in advancements
        ),
        "advancements_with_literal_display": len(literal_advancements),
        "kubejs_reference_files": len(scope.get("kubejs_reference_files", [])),
        "kubejs_visible_literals": len(visible_kubejs),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "validation.json", report)
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "candidate", "build", "verify"))
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare()
        status = 0
    elif args.command == "candidate":
        result = candidate()
        status = 0
    elif args.command == "build":
        result = build()
        status = 0
    else:
        result, status = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
