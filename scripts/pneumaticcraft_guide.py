#!/usr/bin/env python3
"""PneumaticCraft Patchouli 가이드를 번역하고 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import functools
import json
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from zipfile import ZipFile

import ars_family
import pneumaticcraft_family as language
from local_paths import PROJECT_ROOT, resolve_source_root


WORK_ROOT = PROJECT_ROOT / "working/pneumaticcraft/guide"
ENGLISH_ROOT = WORK_ROOT / "en_us"
JAPANESE_ROOT = WORK_ROOT / "ja_jp"
KOREAN_ROOT = WORK_ROOT / "ko_kr"
OUTPUT_ROOT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/pneumaticcraft/patchouli_books/book/ko_kr"
)
CACHE_FILE = PROJECT_ROOT / "temp/pneumaticcraft_guide_candidate_cache_ja_v2.json"
LEGACY_CACHE_FILE = PROJECT_ROOT / "temp/pneumaticcraft_guide_candidate_cache.json"
BOOK_PREFIX = "assets/pneumaticcraft/patchouli_books/book/en_us/"
JAPANESE_BOOK_PREFIX = "assets/pneumaticcraft/patchouli_books/book/ja_jp/"
ADVANCEMENT_PREFIX = "data/pneumaticcraft/advancement/"
VISIBLE_FIELDS = {
    "caption",
    "description",
    "header",
    "name",
    "subtitle",
    "text",
    "title",
}
TRANSLATABLE_PATH_PREFIXES = ("categories/", "entries/")
PATCHOULI_TAG = re.compile(r"(?<!/)\$\([^)]+\)")
ALLOWED_UNCHANGED = {
    "Thaumcraft",
    "Immersive Engineering",
    "ComputerCraft",
    "Open Computers",
    "CraftTweaker",
    "Apotheosis",
    "Curios",
    "$(italic)Godot/$",
}
FORBIDDEN_GUIDE_FRAGMENTS = (
    "무인 항공기",
    "1 하나",
    "E엘리베이터",
    "E외부",
    "pne umaticcraft",
    "에어컨 프레서",
    "공중 비용",
    "화타석과 타격",
    "드론가",
    "드론를",
    "드론는",
    "해야합니다",
    "할 수있는",
)

LOCATION_OVERRIDES = {
    ("entries/compressors/advanced_liquid_compressor.json", 1): (
        "$(item)고급 액체 압축기/$는 $(l:compressors/liquid_compressor)액체 압축기/$의 "
        "$(l:base_concepts/pressure_tiers)2등급/$ 버전이며 최대 안전 압력은 20bar입니다. "
        "기본적으로 틱당 50mL의 공기를 생산하고 "
        "$(l:base_concepts/upgrades#speed)속도 업그레이드/$를 설치할 수 있습니다.$(p)"
        "다만 이 발전기는 $(l:base_concepts/heat)냉각/$해야 합니다. 온도가 높아질수록 "
        "효율이 떨어지며, 지나치게 뜨거우면 공기를 전혀 생산하지 않습니다."
    ),
    ("entries/compressors/electric_compressor.json", 1): (
        "$(item)전기 압축기/$는 $(thing)IndustrialCraft 2의 EU/$로 압축 공기를 "
        "생산합니다. 기본 효율은 40%이며, $(ttcolor)$(t:'I:electricCompressorEfficiency' "
        "참조)설정에서 변경/$할 수 있습니다.$(p)IC2 1등급 기계처럼 작동하므로 32EU/t를 "
        "초과해 입력하면 폭발합니다. 일반 IC2 기계처럼 IC2 $(item)변압기 업그레이드/$를 "
        "추가하면 더 높은 전압을 받을 수 있습니다."
    ),
    ("entries/compressors/electric_compressor.json", 2): (
        "틱당 공기 생산량(mL)은 다음과 같습니다:$(p)$(formula)입력 속도 / E × 400/$"
        "$(p)여기서 $(formula)E/$는 효율(%)입니다.$(p)예를 들어 기본 효율 40%에서 "
        "32EU/틱을 입력하면 압축 공기 생산량은 "
        "$(formula)32 / 40 × 400 = 320mL/틱/$입니다."
    ),
    ("entries/compressors/electric_compressor.json", 3): (
        "효율에는 기계의 $(l:base_concepts/heat)온도/$도 영향을 줍니다. 기계를 냉각해야 "
        "하며, 온도가 높아질수록 효율이 낮아져 결국 공기를 전혀 생산하지 않게 됩니다."
    ),
    ("entries/base_concepts/heat.json", 1): (
        "$(pncr)에는 $(thing)열/$ 시스템이 있습니다. 열은 현실과 비슷하게 블록에서 "
        "블록으로 퍼지며 $(l:base_concepts/pressure)압력이 분산되는 방식/$과도 비슷합니다:"
        "$(li)열은 더 뜨거운 물체에서 더 차가운 물체로 이동합니다.$(li)블록은 열 시스템을 "
        "지원하는 인접 블록에만 열을 전달합니다("
        "$(l:base_concepts/heat_sources)열원/$ 참조)."
    ),
    ("entries/base_concepts/heat.json", 2): (
        "$(li)온도 차이가 클수록 열이 더 빨리 이동합니다.$(li)물체마다 "
        "$(thing)열저항/$이 다릅니다. $(item)횃불/$과 $(item)공기/$는 열저항이 높고, "
        "$(l:base_concepts/basic_materials#compressed_iron_block)압축 철 블록/$은 매우 "
        "낮습니다. $(thing)열저항/$은 물체 사이에서 열이 이동하는 속도를 결정합니다."
    ),
    ("entries/base_concepts/heat.json", 3): (
        "$(li)물체마다 $(thing)열용량/$도 다릅니다. 열용량이 높을수록 같은 양의 열을 "
        "받아도 온도가 천천히 오르고, 같은 양의 열을 잃어도 천천히 내려갑니다. 즉, "
        "열용량이 큰 블록은 $(thing)온도/$를 높이는 데 더 많은 $(thing)열/$이 필요하지만 "
        "열을 잃을 때도 온도가 더 천천히 떨어집니다."
    ),
    ("entries/base_concepts/heat.json", 4): "단열",
    ("entries/base_concepts/heat.json", 5): (
        "기계의 면이 공기에 노출되면 열을 잃습니다. 노출 면이 많은 "
        "$(l:manufacturing/refinery)정유기/$에서 특히 두드러지지만, "
        "$(l:base_concepts/basic_materials#compressed_iron_block)압축 철 블록/$을 포함한 "
        "모든 열전도 블록에 적용됩니다.$(p)열 손실을 막으려면 어느 면도 공기 블록에 "
        "노출되지 않게 하세요. 열이 통하지 않는 블록이면 충분하며 완전한 블록일 필요도 "
        "없습니다. $(item)다락문/$이나 $(item)반 블록/$도 효과가 있습니다."
    ),
    ("entries/base_concepts/heat.json", 6): "열원",
    ("entries/base_concepts/heat.json", 7): (
        "$(pncr)의 일부 기계는 방출해야 할 열을 만들고, 일부 기계는 작동하는 데 열이 "
        "필요합니다.$(p)따라서 기계의 온도를 조절할 "
        "$(l:base_concepts/heat_sources)방법/$을 마련해야 합니다."
    ),
    ("entries/tubes/pressure_tubes.json", 1): (
        "압력 튜브는 $(pncr)에서 압축기와 기계 사이로 압축 공기를 운반하는 기본 "
        "장치입니다.$(p)연결되지 않은 튜브에서는 공기가 샙니다! 다만 "
        "$(l:tools/pneumatic_wrench)공압 렌치/$로 우클릭하면 튜브의 각 면을 열거나 닫을 "
        "수 있습니다. 다른 모드의 렌치도 작동할 수 있습니다."
    ),
    ("entries/tubes/pressure_tubes.json", 2): "튜브!",
    ("entries/tubes/pressure_tubes.json", 3): (
        "$(italic)압력 튜브 두 개와 $(l:tubes/pressure_gauge_module)압력계/$ "
        "$(italic)로 $(l:compressors/air_compressor)공기 압축기/$ "
        "$(italic)및 $(l:machines/air_cannon)에어 캐논/$을 연결한 모습"
    ),
    ("entries/tubes/pressure_tubes.json", 4): (
        "압력 튜브에는 여러 기능을 추가하는 부착물인 "
        "$(l:tubes/tube_modules)튜브 모듈/$을 설치할 수 있습니다. 자세한 내용은 각 "
        "모듈 페이지를 확인하세요.$(p)압력 튜브는 "
        "$(l:tools/camo_applicator)위장 도포기/$로 숨길 수 있습니다."
    ),
    ("entries/tubes/pressure_tubes.json", 5): (
        "튜브에는 세 $(l:base_concepts/pressure_tiers)등급/$이 있습니다:$(br)"
        "$(li)1등급 튜브: 최대 5bar, 공기 용량 1000mL$(li)1.5등급(강화) 튜브: 최대 "
        "10bar, 공기 용량 1000mL$(li)2등급(고급) 튜브: 최대 20bar, 공기 용량 4000mL"
    ),
    ("entries/base_concepts/heat_sources.json", 1): (
        "$(thing)정적 열원/$은 인접한 기계에 열을 공급하거나 기계에서 열을 빼앗는 블록과 "
        "유체입니다. 열이 너무 많이 드나들면 다른 블록이나 유체로 변할 수 있습니다. "
        "열의 출입량은 해당 블록 외부에 별도로 기록되므로 블록을 부쉈다가 다시 놓아 "
        "누적된 열을 초기화할 수는 없습니다."
    ),
    ("entries/base_concepts/heat_sources.json", 2): "바닐라 열원",
    ("entries/base_concepts/heat_sources.json", 3): (
        "다음 바닐라 블록과 유체가 정적 열원으로 작동합니다:$(li)공기$(li)얼음/꽁꽁 언 "
        "얼음/푸른얼음$(li)눈$(li)횃불$(li)불(꺼질 수 있음)$(li)마그마(네더랙으로 "
        "식음)$(li)물(얼거나 증발할 수 있음)$(li)용암(흑요석으로 식음)$(li)모닥불(꺼질 "
        "수 있음)"
    ),
    ("entries/base_concepts/heat_sources.json", 4): "모드 열원",
    ("entries/base_concepts/heat_sources.json", 5): (
        "다른 모드의 여러 블록도 서로 다른 특성의 정적 열원으로 작동합니다:$(li)IC2 "
        "증기와 과열 증기$(li)IC2 냉각수와 고온 냉각수$(li)IC2 및 Immersive Engineering "
        "우라늄 블록$(li)Quark 블레이즈 랜턴$(li)Quark 유황과 영구동토$(li)Natura 열 "
        "모래$(li)모드가 추가한 모든 유체에는 해당 모드가 정한 온도 특성이 있습니다."
    ),
    ("entries/base_concepts/heat_sources.json", 6): "사용자 지정 열원 추가",
    ("entries/base_concepts/heat_sources.json", 7): (
        "(모드팩 제작자용) 모든 블록의 열 특성은 데이터 팩에 정의됩니다. "
        "$(thing)data/<mod-id>/pneumaticcraft/block_heat_properties/$에 JSON 파일을 "
        "추가하여 새 정의를 만들거나 기본 정의를 덮어쓰거나 제거할 수 있습니다."
    ),
    ("entries/base_concepts/heat_sources.json", 8): (
        "$(l:machines/vortex_tube)볼텍스 튜브/$는 "
        "$(l:base_concepts/pressure)압력/$을 열과 냉기로 직접 바꾸는 $(thing)동적 "
        "열원/$입니다. 효율을 높이려면 사용하지 않는 면에 "
        "$(l:machines/heat_sink)방열판/$을 설치하는 것이 좋습니다."
    ),
    ("entries/base_concepts/heat_sources.json", 9): (
        "$(l:semiblocks/heat_frame)열 프레임/$은 인벤토리의 아이템을 가열하거나 얼리는 "
        "가젯입니다. 열 프레임은 $(thing)정적 열원/$에서 열을 직접 흡수하지 않으므로, "
        "옆에 $(l:machines/heat_pipe)열 파이프/$를 놓아 열을 전달할 수 있습니다."
    ),
    ("entries/base_concepts/heat_sources.json", 10): (
        "$(l:machines/heat_sink)방열판/$은 부착한 블록의 열이나 냉기를 대기로 효율적으로 "
        "방출하는 블록입니다."
    ),
    ("entries/base_concepts/heat_sources.json", 11): (
        "$(l:machines/heat_pipe)열 파이프/$는 압축 철로 만든 단열 코어로, 인접한 공기나 "
        "유체 블록과 열을 주고받지 않고 블록 사이로 열을 전달합니다. "
        "$(item)압축 철 블록/$으로 열을 전달하는 것보다 작고 저렴합니다. 열 파이프에 "
        "$(item)방열판/$을 직접 부착할 수도 있습니다."
    ),
    ("entries/base_concepts/heat_sources.json", 12): (
        "바닐라 $(item)화로/$를 $(l:machines/vortex_tube)볼텍스 튜브/$나 열을 만드는 "
        "$(l:compressors/advanced_air_compressor)고급 공기 압축기/$ 같은 동적 열원에 "
        "연결하면 화로가 열을 연료처럼 소비합니다. 고체 연료 없이 열만으로 화로를 "
        "작동할 수 있어 편리하고 효율적입니다."
    ),
    ("entries/base_concepts/heat_sources.json", 13): "화로(계속)",
    ("entries/base_concepts/heat_sources.json", 14): (
        "화로는 100°C부터 열로 작동하며 온도가 높을수록 빨라집니다. 화로 주변에 열원을 "
        "여러 개 놓으면 가열 효과가 커집니다.$(p)이 효과는 바닐라 $(item)용광로/$와 "
        "$(item)훈연기/$에도 적용됩니다."
    ),
    ("entries/programming/area.json", 0): "영역 위젯",
    ("entries/programming/area.json", 1): (
        "$(thing)영역/$ 위젯은 다른 위젯의 매개변수로만 사용하며, 해당 위젯이 작동할 "
        "영역(블록 하나일 수도 있음)을 지정합니다. 이 위젯을 사용하려면 "
        "$(l:tools/gps_tool)GPS 도구/$나 $(l:tools/gps_area_tool)GPS 영역 도구/$가 "
        "필요합니다.$(p)영역 위젯은 주로 다음 세 가지 방법으로 설정합니다:"
    ),
    ("entries/programming/area.json", 2): (
        "1. $(l:programming/programmer)프로그래머/$ GUI에서 영역 위젯을 "
        "$(thing)우클릭/$해 설정 GUI를 여세요. 두 $(thing)GPS/$ 버튼을 눌러 인벤토리의 "
        "$(l:tools/gps_tool)GPS 도구/$를 선택하고 영역의 두 끝점을 지정한 뒤, 아래의 "
        "선택 버튼으로 $(thing)영역 형태/$와 관련 매개변수를 정합니다."
    ),
    ("entries/programming/area.json", 3): (
        "2. 월드에서 $(l:tools/gps_tool)GPS 도구/$나 $(l:tools/gps_area_tool)GPS 영역 "
        "도구/$를 설정하세요. $(l:programming/programmer)프로그래머/$ GUI에서는 다음과 "
        "같이 사용할 수 있습니다:$(li)기존 $(thing)영역/$ 위젯에 $(item)GPS (영역) "
        "도구/$를 들고 $(thing)좌클릭/$하여 도구 설정을 위젯에 복사$(li)빈 프로그래밍 "
        "영역에 $(item)GPS 도구/$를 들고 $(thing)좌클릭/$하여 새 "
        "$(l:programming/coordinate)좌표/$ 위젯 생성$(li)빈 프로그래밍 영역에 "
        "$(item)GPS 도구/$를 들고 $(thing)Shift+좌클릭/$하여 새 $(thing)영역/$ 위젯 "
        "생성$(li)빈 프로그래밍 영역에 $(item)GPS 영역 도구/$를 들고 "
        "$(thing)Shift+좌클릭/$하여 새 $(thing)영역/$ 위젯 생성"
    ),
    ("entries/programming/area.json", 4): (
        "3. 고급 방법으로 $(l:programming/coordinate_operator)좌표 연산자/$ 위젯이 만든 "
        "$(thing)변수/$를 사용할 수 있습니다. 변수를 쓰려면 "
        "$(l:programming/programmer)프로그래머/$가 $(thing)고급/$ 모드여야 합니다. GPS "
        "버튼 옆의 드롭다운에서 알려진 변수 이름을 고르면 그 변수의 위치를 해당 영역 "
        "모서리로 사용합니다."
    ),
    ("entries/programming/area.json", 5): "$(italic)영역 위젯/$",
    ("entries/programming/conditions.json", 0): "조건",
    ("entries/programming/conditions.json", 1): (
        "$(thing)조건/$ 위젯은 어떤 상태를 검사하고, 검사에 성공하면 프로그램의 다른 "
        "부분으로 이동하게 합니다.$(p)모든 $(thing)조건/$ 위젯은 가장 아래쪽 매개변수로 "
        "$(thing)레이블 이름/$을 지정한 $(l:programming/text)텍스트/$ 위젯을 받습니다."
    ),
    ("entries/programming/conditions.json", 2): (
        "조건이 $(thing)참/$이면 $(l:programming/flow_control)프로그램 실행/$이 "
        "$(italic)오른쪽/$의 "
        "$(thing)텍스트/$ 매개변수와 같은 이름인 $(l:programming/label)레이블/$ 위젯으로 "
        "이동합니다. 조건이 $(thing)거짓/$이면 $(italic)왼쪽/$의 $(thing)텍스트/$ "
        "매개변수와 같은 이름인 $(thing)레이블/$로 이동합니다.$(p)$(thing)조건/$ 위젯이 "
        "유효한 $(thing)텍스트/$ 매개변수를 찾지 못하면 "
        "$(italic)아래쪽/$의 다음 위젯으로 계속 진행합니다."
    ),
    ("entries/programming/conditions.json", 3): (
        "$(italic)레드스톤 신호가 10 이상이면 드론을 자폭시키는 레드스톤 조건 위젯/$"
    ),
    ("entries/programming/conditions.json", 4): (
        "대부분의 $(thing)조건/$ 위젯은 $(thing)우클릭/$해 설정 GUI를 열 수 있습니다. "
        "GUI에는 보통 '='와 '>=' 선택 항목과 숫자 입력란이 있습니다.$(p)이 설정으로 상자 "
        "속 아이템 수 같은 값을 정확히 10개('=' 및 10), 20개 초과('>=' 및 21), 12개 "
        "미만('>=' 및 12로 검사하되 조건이 $(thing)거짓/$인 분기)인지 검사할 수 있습니다."
    ),
    ("entries/programming/conditions.json", 5): "측정",
    ("entries/programming/conditions.json", 6): (
        "$(l:programming/condition_item)조건: 아이템 필터/$를 제외한 모든 $(thing)조건/$ "
        "위젯 GUI에는 $(thing)측정/$ 입력란이 있습니다. 여기에 "
        "$(l:programming/variables)변수/$ 이름을 입력하면 드론이 측정한 값을 변수의 X에 "
        "저장합니다.$(p)이 값은 다른 변수처럼 사용할 수 있습니다. 예를 들어 유체 탱크의 "
        "양을 측정해 표지판에 표시할 수 있습니다."
    ),
    ("entries/programming/conditions.json", 7): "측정(계속)",
    ("entries/programming/conditions.json", 8): (
        "측정 변수 이름을 입력하면 조건 위젯에 분기용 텍스트 위젯이 없어도 오류가 "
        "아닙니다(보통은 분기가 하나 이상 필요함). 따라서 조건 위젯을 수량 측정에만 "
        "사용하고 실행은 평소처럼 아래로 계속 진행할 수 있습니다.$(p)참고: 압력 측정 "
        "조건은 값을 밀리바 단위로 저장합니다(예: 5.5bar는 5500)."
    ),
    ("entries/programming/conditions.json", 9): "조건 유형",
    ("entries/programming/conditions.json", 10): (
        "조건은 $(thing)월드 조건/$과 $(thing)드론 조건/$으로 나뉩니다.$(p)월드 조건은 "
        "$(item)상자/$에 특정 수량의 아이템이 있는지, 어느 위치에 블록이 있는지처럼 "
        "월드의 상태를 "
        "검사합니다.$(p)$(thing)드론 조건/$은 드론이 특정 아이템이나 압력을 가지고 "
        "있는지처럼 $(l:tools/drone)드론/$ 자체를 검사합니다."
    ),
    ("entries/programming/conditions.json", 12): "월드 조건",
    ("entries/programming/conditions.json", 13): "드론 조건",
    ("entries/programming/edit_sign.json", 0): "표지판 편집 위젯",
    ("entries/programming/edit_sign.json", 1): (
        "연결된 $(l:programming/area)영역/$ 안의 모든 $(item)표지판/$과 "
        "$(l:machines/aphorism_tile)격언 타일/$을 연결된 "
        "$(l:programming/text)텍스트/$ 위젯의 내용으로 바꿉니다.$(p)연결된 "
        "$(thing)텍스트/$ 위젯 하나가 한 줄을 나타내며, 여러 "
        "$(thing)텍스트/$ 위젯을 연결하면 여러 줄의 "
        "문구를 설정할 수 있습니다."
    ),
    ("entries/programming/edit_sign.json", 2): "변수",
    ("entries/programming/edit_sign.json", 3): (
        "텍스트에 $(thing)${<var_name>}/$을 넣어 $(l:programming/variables)변수/$의 값을 "
        "표시할 수도 있습니다. 예를 들어$(p)$(formula)Counter: ${counter}/$$(p)는 "
        "$(thing)counter/$ 변수가 $(thing)x=1,y=2,z=3/$일 때 "
        "$(thing)Counter: 1, 2, 3/$으로 표시됩니다. "
        "$(l:programming/variables#special)특수/$ 변수와 "
        "$(l:programming/variables#global)전역 변수/$도 사용할 수 있습니다."
    ),
    ("entries/programming/edit_sign.json", 4): "$(italic)표지판 편집 위젯/$",
    ("entries/programming/drop_item.json", 0): "아이템 버리기 위젯",
    ("entries/programming/drop_item.json", 1): (
        "$(l:tools/drone)드론/$이 인벤토리의 아이템을 연결된 "
        "$(l:programming/area)영역/$에 버립니다. $(thing)아이템 버리기/$ 위젯을 "
        "$(thing)우클릭/$하면 영역의 각 위치에 버릴 아이템 수를 정할 수 있습니다. "
        "$(thing)무작위/$ 모드는 바닐라 $(item)드로퍼/$처럼 작은 무작위 편차를 두고 "
        "아이템을 버리며, $(thing)직선/$ 모드는 아이템을 곧바로 아래에 버립니다."
    ),
    ("entries/programming/drop_item.json", 2): (
        "$(l:programming/item_filter)아이템 필터/$를 연결하면 필터가 허용한 아이템만 "
        "버립니다.$(p)해당하는 아이템이 $(item)드론/$ 인벤토리에 하나도 남지 않거나 "
        "$(item)드론/$이 영역의 모든 위치를 방문하면 위젯 실행이 끝납니다."
    ),
    ("entries/programming/drop_item.json", 3): "$(italic)아이템 버리기 위젯/$",
    ("entries/tools/pneumatic_wrench.json", 0): "공압 렌치",
    ("entries/tools/pneumatic_wrench.json", 1): (
        "공압 렌치는 $(pncr)의 $(thing)렌치/$입니다. 다음 작업에 사용할 수 있습니다:"
        "$(p)$(li)바닐라 및 모드 블록을 $(thing)우클릭/$해 회전$(li)$(pncr) 기계를 "
        "$(thing)몸을 숙인 채 우클릭/$해 저장된 업그레이드와 공기를 보존한 아이템으로 "
        "회수"
    ),
    ("entries/tools/pneumatic_wrench.json", 2): (
        "$(li)$(l:base_concepts/drones)드론/$을 $(thing)우클릭/$해 아이템으로 회수"
        "$(li)$(l:tubes/pressure_tubes)압력 튜브/$를 $(thing)우클릭/$해 각 면을 닫거나 "
        "다시 열어 서로 분리$(p)$(item)공압 렌치/$를 사용하려면 먼저 "
        "$(l:machines/charging_station)충전소/$에서 가압해야 합니다."
    ),
    ("entries/tools/minigun_ammo.json", 0): "미니건 탄약",
    ("entries/tools/minigun_ammo.json", 1): (
        "총기 탄약은 $(l:tools/minigun)미니건/$에서 사용합니다.$(p)탄약 종류에 따라 탄창 "
        "하나에 최대 2000발이 들어갑니다. $(item)미니건/$을 발사하는 동안 탄약이 "
        "계속 소모되며, "
        "남은 탄약은 아이템 툴팁과 내구도 막대, 미니건을 장착했을 때 화면 중앙 조준경 "
        "옆의 HUD에서 확인할 수 있습니다."
    ),
    ("entries/tools/minigun_ammo.json", 2): (
        "탄약은 $(item)미니건/$의 탄창에 넣어야 하며 플레이어 인벤토리에서는 자동으로 "
        "소모되지 않습니다. $(item)미니건/$을 $(thing)몸을 숙인 채 우클릭/$해 탄약을 "
        "장전하세요.$(p)탄약은 1~4번 슬롯 순서로 소모됩니다. 슬롯을 $(thing)가운데 "
        "클릭/$해 잠그면 $(item)미니건/$이 그 슬롯의 탄약만 사용하므로 여러 탄약을 "
        "장전했을 때 유용합니다. 잠긴 슬롯을 다시 $(thing)가운데 클릭/$하면 잠금이 "
        "풀립니다."
    ),
    ("entries/tools/minigun_ammo.json", 3): (
        "일반 $(item)총기 탄약/$은 별도 효과가 없지만 2000발이 들어가는 큰 탄창을 "
        "사용합니다.$(p)또한 $(l:tools/minigun_ammo#potions)물약/$과 조합해 효과를 "
        "부여할 수 있는 유일한 탄약입니다."
    ),
    ("entries/tools/minigun_ammo.json", 4): (
        "$(item)소이 미니건 탄약/$은 1000발이 들어가며 맞은 개체에 불을 붙입니다.$(p)"
        "블록에도 불이 붙을 수 있으니 주의하세요!"
    ),
    ("entries/tools/minigun_ammo.json", 5): (
        "$(item)중량 미니건 탄약/$은 500발이 들어가고 피해량이 매우 높지만, 무거워서 "
        "사거리가 일반 탄약의 20%뿐입니다."
    ),
    ("entries/tools/minigun_ammo.json", 6): (
        "$(item)방어구 관통 미니건 탄약/$은 500발이 들어갑니다. 제작 비용이 비싸지만 "
        "일반 탄약보다 피해량이 조금 높고 대상의 방어구를 관통할 수 있습니다."
    ),
    ("entries/tools/minigun_ammo.json", 8): (
        "$(item)빙결 미니건 탄약/$은 1000발이 들어갑니다. 맞은 대상을 느리게 만들고 "
        "피해를 주는 빙결 구름으로 감쌀 수 있지만, 이 구름은 자신에게도 피해를 줄 수 "
        "있습니다.$(p)불에 내성이 있는 대상에게 추가 피해를 주므로 $(#800)네더/$에서 "
        "싸울 때 매우 효과적입니다."
    ),
    ("entries/tools/minigun_ammo.json", 9): "물약이 묻은 탄약",
    ("entries/tools/minigun_ammo.json", 10): (
        "일반 미니건 탄약을 아무 $(item)물약/$과 조합할 수 있습니다. 이렇게 만든 탄약은 "
        "물리 피해를 주지 않는 대신 대상에게 물약 효과를 적용할 수 있습니다.$(p)"
        "$(thing)투척용/$ 및 $(thing)잔류형/$ 물약도 사용할 수 있으며 예상대로 범위 효과가 "
        "발생합니다. 다만 투척용 물약 탄약은 3배, 잔류형 물약 탄약은 6배 빠르게 "
        "소모됩니다!"
    ),
    ("entries/base_concepts/pressure_tiers.json", 0): "압력 등급",
    ("entries/base_concepts/pressure_tiers.json", 1): (
        "$(pncr)의 공압 기계에는 현재 세 가지 $(thing)등급/$이 있습니다:$(li)"
        "$(thing)1등급/$ 기계는 기본적으로 5bar의 압력을 견딜 수 있습니다.$(li)"
        "$(thing)1.5등급/$ 기계는 최대 10bar를 견딜 수 있습니다.$(li)"
        "$(thing)2등급/$ 기계는 최대 20bar를 견딜 수 있습니다."
    ),
    ("entries/base_concepts/pressure_tiers.json", 2): (
        "1.5등급은 $(pncr)의 Minecraft 1.18 버전에 추가된 선택적 등급입니다. 이전에는 "
        "2등급에서만 쓸 수 있던 일부 기능을 중간 단계에서 사용할 수 있습니다:$(li)"
        "도구를 10bar까지 충전$(li)$(item)다이아몬드 드릴 비트/$ 획득(3x3 영역을 "
        "굴착할 수 있으며, 이전에는 $(item)네더라이트 드릴 비트/$가 필요했습니다)"
    ),
    ("entries/base_concepts/pressure_tiers.json", 3): "게이지 압력",
    ("entries/base_concepts/pressure_tiers.json", 4): (
        "$(pncr)에서 사용하는 $(thing)bar/$는 정상 대기압보다 $(bold)높은/$ 압력을 "
        "나타냅니다. 따라서 0bar는 가압되지 않은 공기이고 -1bar는 진공입니다. 이를 "
        "$(thing)게이지 압력/$이라고도 합니다."
    ),
    ("entries/base_concepts/getting_started.json", 0): "시작하기",
    ("entries/base_concepts/getting_started.json", 1): (
        "PneumaticCraft에 오신 것을 환영합니다!$(li)$(thing)철/$과 $(thing)돌/$을 "
        "준비하세요. 처음에는 각각 한 스택 정도면 충분하며, 철은 조금 적어도 됩니다."
        "$(li)철을 땅에 던지고 폭발시키세요. 네, 정말입니다.$(li)폭발 뒤에 남은 "
        "$(thing)압축 철/$을 모으세요(폭발 과정에서 일부가 손실됩니다).$(li)"
        "$(l:tubes/pressure_tubes)압력 튜브/$를 만드세요.$(li)"
        "$(l:base_concepts/building_materials)강화석/$을 만드세요.$(li)"
        "$(l:manufacturing/pressure_chamber)압력 챔버/$를 건설하세요."
    ),
    ("entries/base_concepts/getting_started.json", 2): (
        "이제부터 $(pncr)를 진행하며 달성한 $(thing)발전 과제/$에 따라 설명서의 다른 "
        "항목이 잠금 해제됩니다. 다음에 무엇을 만들어야 할지 모르겠다면 이 모드의 발전 "
        "과제 페이지를 확인하세요. 일부 발전 과제를 달성하면 $(thing)경험치/$도 받습니다."
    ),
    ("entries/base_concepts/entity_filter.json", 0): "개체 필터",
    ("entries/base_concepts/entity_filter.json", 1): (
        "$(thing)개체 필터/$는 $(pncr)의 여러 기계와 도구가 영향을 줄 $(thing)개체/$를 "
        "지정할 때 사용합니다.$(p)필터를 입력하는 대부분의 화면에서는 $(thing)F1/$ 키를 "
        "누르고 있으면 팝업 도움말을 볼 수 있습니다."
    ),
    ("entries/base_concepts/entity_filter.json", 2): (
        "개체 유형으로 찾으려면 유형 이름을 입력하세요. 예를 들어 $(#800)creeper/$는 "
        "$(thing)minecraft:creeper/$와 일치합니다. 사용자 지정 이름을 가진 개체(플레이어 "
        "포함)를 찾으려면 $(#800)'Minemaarten'/$ 또는 $(#800)'desht'/$처럼 이름을 "
        "따옴표로 감싸세요.$(p)동물, 적대적 몹, 모든 플레이어처럼 특정 개체 "
        "$(italic)유형/$을 지정하려면 앞에 '@'를 붙입니다. 사용할 수 있는 "
        "$(thing)@ 지정자/$의 예는 다음과 같습니다."
    ),
    ("entries/base_concepts/entity_filter.json", 3): "예",
    ("entries/base_concepts/entity_filter.json", 4): (
        "$(li)$(#800)@player/$: 모든 플레이어$(li)$(#800)@mob/$: 모든 적대적 생물"
        "$(li)$(#800)@animal/$: 모든 비적대적 생물(동물)"
        "$(li)$(#800)@animal(age=adult)/$: 모든 성체 동물"
        "$(li)$(#800)@animal(age=baby)/$: 모든 새끼 동물"
        "$(li)$(#800)@animal(breedable=yes)/$: 현재 번식할 수 있는 모든 동물"
        "$(li)$(#800)sheep(shearable=yes)/$: 털을 깎을 수 있는 모든 양"
    ),
    ("entries/base_concepts/entity_filter.json", 5): "예(계속)",
    ("entries/base_concepts/entity_filter.json", 6): (
        "$(li)$(#800)sheep(shearable=yes,color=black)/$: 털을 깎을 수 있는 검은 양"
        "$(li)$(#800)wolf(color=blue)/$: 파란 목줄을 한 늑대와 개"
        "$(li)$(#800)cat(color=white)/$: 흰 목줄을 한 고양이"
        "$(li)$(#800)@minecart/$: 모든 광산 수레$(li)$(#800)@boat/$: 모든 보트"
        "$(li)$(#800)@living/$: 모든 살아 있는 개체"
        "$(li)$(#800)@item/$: 모든 아이템 개체"
        "$(li)$(#800)@orb/$: 모든 경험치 구슬"
    ),
    ("entries/base_concepts/entity_filter.json", 7): "예(계속)",
    ("entries/base_concepts/entity_filter.json", 8): (
        "$(li)$(#800)@drone/$: 모든 $(l:tools/drone)드론/$"
        "$(li)$(#800)@mob(mod=minecraft)/$: $(thing)minecraft/$ 네임스페이스의 몹만"
        "$(li)$(#800)Creeper/$: 크리퍼$(li)$(#800)'MineMaarten'/$ 또는 "
        "$(#800)\"Minemaarten\"/$: 이름이 'MineMaarten'인 개체"
        "$(li)$(#800)c*/$: 이름이 'c'로 시작하는 개체(예: Creeper, Cow)"
        "$(li)$(#800)*pig*/$: 이름에 'pig'가 들어가는 개체(예: Pig, Zombified Piglin)"
    ),
    ("entries/base_concepts/entity_filter.json", 9): (
        "$(li)$(#800)@player(team=team1)/$: 바닐라 점수판의 team1 팀에 속한 플레이어"
        "$(li)$(#800)@player(holding=stick)/$: 현재 막대기를 들고 있는 플레이어"
        "$(li)$(#800)@player(holding=#minecraft:planks)/$: "
        "$(thing)minecraft:planks/$ 아이템 태그에 속한 아이템을 들고 있는 플레이어"
    ),
    ("entries/base_concepts/entity_filter.json", 10): (
        "$(li)$(#800)@player(ftbteam=<uuid>|<shortname>)/$: 지정한 UUID 또는 짧은 "
        "이름의 $(l:https://www.curseforge.com/minecraft/mc-mods/ftb-teams-forge)FTB "
        "Teams/$ 팀에 속한 플레이어$(p)$(#800)ftbteam_officer/$, "
        "$(#800)ftbteam_owner/$, $(#800)ftbteam_ally/$ 지정자로 팀의 간부, 소유자, "
        "동맹을 찾을 수 있습니다. $(#800)ftbteam_enemy/$는 팀에서 적으로 표시한 "
        "플레이어와 일치합니다."
    ),
    ("entries/base_concepts/entity_filter.json", 11): (
        "일치는 대소문자를 구분하지 않으므로 $(#800)zombie/$와 $(#800)Zombie/$는 "
        "모두 좀비와 일치합니다.$(p)필터를 ';'(세미콜론)으로 구분해 $(thing)여러 조건/$을 "
        "지정할 수 있습니다. 이 방식은 하나라도 맞으면 통과하는 $(italic)OR 조건/$입니다:"
        "$(li)$(#800)creeper;zombie/$는 크리퍼$(italic)와/$ 좀비 모두와 일치합니다."
    ),
    ("entries/base_concepts/entity_filter.json", 12): (
        "필터 앞에 '!'를 붙이면 조건을 반대로 만들 수 있습니다:$(li)$(#800)!@player/$는 "
        "플레이어가 $(italic)아닌/$ 모든 개체와 일치합니다$(li)"
        "$(#800)!Creeper;Zombie/$는 크리퍼$(italic)도/$ 좀비도 아닌 개체와 일치합니다"
        "$(li)$(#800)Creeper;!Zombie/$는 $(#f00)잘못된 필터/$입니다. '!'는 필터의 맨 "
        "앞에만 쓸 수 있습니다./$$(p)$(bold)참고:/$ $(l:programming/text)텍스트/$ 프로그래밍 "
        "위젯을 사용하는 $(l:tools/drone)드론/$ 개체 필터에서는 '!'를 지원하지 않습니다. "
        "평소처럼 텍스트 위젯을 왼쪽에 연결하세요."
    ),
    ("entries/base_concepts/entity_filter.json", 13): (
        "$(italic)개체 필터를 사용하는 기계와 도구/$"
    ),
    ("entries/programming/tutorial_1.json", 0): "기본 드론 튜토리얼 #1",
    ("entries/programming/tutorial_1.json", 1): (
        "이 튜토리얼에서는 $(l:tools/drone)드론/$이 지정한 영역을 굴착하도록 간단한 "
        "프로그램을 만듭니다. 시작하기 전에 다음 항목을 준비하세요:"
    ),
    ("entries/programming/tutorial_1.json", 2): (
        "$(li)$(l:programming/programmer)프로그래머/$(물론 필요합니다)"
        "$(li)(크리에이티브 모드가 아니라면) 프로그래머 옆에 놓고 "
        "$(l:programming/puzzle_pieces)퍼즐 조각/$을 6개 이상 넣은 $(item)상자/$"
        "$(li)아무 종류의 $(item)삽/$을 넣은 $(item)상자/$ 또는 다른 인벤토리"
        "$(li)기본 $(l:tools/gps_tool)GPS 도구/$"
        "$(li)$(l:tools/gps_area_tool)GPS 영역 도구/$"
    ),
    ("entries/programming/tutorial_1.json", 3): (
        "$(l:programming/programmer)프로그래머/$ GUI를 여세요. 오른쪽에는 "
        "$(ttcolor)$(t:GUI에서 퍼즐 조각을 가상으로 나타낸 것을 프로그래밍 위젯이라고 "
        "합니다)프로그래밍 위젯/$이 놓인 $(thing)목록/$이 "
        "있습니다. 여러 페이지가 있으며, 아래쪽 화살표 버튼으로 넘기거나 "
        "$(thing)Space/$ 또는 $(thing)Tab/$ 키를 눌러 목록을 펼칠 수 있습니다.$(p)"
        "목록을 펼치면 위쪽에 검색어를 입력하는 $(thing)필터/$가 나타납니다. 'start'를 "
        "입력하면 $(7)회색으로 비활성화되지 않은/$ 위젯 하나만 남습니다."
    ),
    ("entries/programming/tutorial_1.json", 4): (
        "이제 $(l:programming/start)시작/$ 위젯을 주 프로그래밍 영역으로 끌어오세요. "
        "문제가 있음을 나타내는 $(4)빨간 테두리/$가 표시됩니다. 마우스를 올리면 원인을 "
        "볼 수 있습니다.$(p)아래에 연결된 위젯이 없기 때문입니다. 이제 프로그램을 만들어 "
        "해결하겠습니다.$(p)$(l:programming/inventory_import)인벤토리에서 가져오기/$ "
        "위젯을 찾아 $(thing)시작/$ 위젯 바로 아래로 끌어오세요."
    ),
    ("entries/programming/tutorial_1.json", 5): (
        "충분히 가까이 놓으면 $(thing)시작/$ 위젯 아래에 맞물립니다. 직소 퍼즐처럼 "
        "연결부가 맞는 모습을 보면 왜 $(thing)퍼즐 조각/$이라고 부르는지 알 수 있습니다."
        "$(p)다음으로 $(l:programming/area)영역/$ 위젯을 $(thing)불러오기/$ 위젯의 "
        "오른쪽($(ttcolor)$(t:다른 위젯 오른쪽에 놓은 위젯은 화이트리스트, 왼쪽에 놓은 "
        "위젯은 블랙리스트로 작동합니다)왼쪽이 아님/$)에 연결하세요. "
        "$(l:programming/item_filter)아이템 필터/$ 위젯도 $(thing)불러오기/$ 위젯의 "
        "오른쪽에 연결하고, 모두 정확히 맞물렸는지 확인하세요."
    ),
    ("entries/programming/tutorial_1.json", 6): (
        "$(thing)영역/$ 위젯에도 아직 영역을 지정하지 않아 $(4)빨간 테두리/$가 "
        "표시됩니다. $(item)GPS 도구/$를 들고 $(thing)몸을 숙인 채 우클릭/$해 앞서 "
        "놓은 $(item)상자/$ 중 $(item)삽/$이 들어 있는 상자를 선택하세요. 위치가 "
        "강조됩니다.$(p)프로그래머 GUI에서 $(thing)좌클릭/$으로 $(thing)영역/$ 위젯을 "
        "선택하되 커서에는 $(item)GPS 도구/$를 들어야 합니다. 위치가 $(thing)영역/$ "
        "위젯에 복사됩니다."
    ),
    ("entries/programming/tutorial_1.json", 7): (
        "이제 $(thing)아이템 필터/$를 $(thing)우클릭/$해 옵션 GUI를 여세요. "
        "$(bold)아이템 검색.../$ 버튼을 누르고 검색창에 'shovel'을 입력합니다. 앞서 상자에 "
        "넣은 삽 종류를 고른 뒤 $(thing)Escape/$를 눌러 검색창을 닫으세요.$(p)"
        "$(thing)아이템 필터/$ 창에서 '아이템 내구도'가 $(italic)선택 해제/$되어 있는지 "
        "확인해야 사용 중인 삽도 조건에 맞습니다. $(thing)Escape/$를 다시 눌러 주 GUI로 "
        "돌아가세요."
    ),
    ("entries/programming/tutorial_1.json", 8): (
        "이제 드론에게 상자에서 삽을 가져오도록 지시했습니다. 다음은 굴착입니다!$(p)"
        "$(l:programming/dig)굴착/$ 위젯을 $(thing)불러오기/$ 위젯 아래에 연결하세요.$(p)"
        "다른 $(thing)영역/$ 위젯을 $(thing)굴착/$ 위젯 오른쪽에 연결하세요."
    ),
    ("entries/programming/tutorial_1.json", 9): (
        "굴착할 영역을 지정하겠습니다. $(thing)GPS 영역 도구/$를 들고 한쪽 모서리 블록을 "
        "$(thing)우클릭/$한 다음 반대쪽 모서리 블록을 $(thing)좌클릭/$하세요. 드론이 삽을 "
        "사용하므로 흙이나 모래 영역을 선택하는 것이 좋습니다.$(p)강조 표시된 영역이 "
        "$(thing)채워진 직육면체/$인지 확인하세요. 기본값은 이 형태지만, 허공에서 도구를 "
        "$(thing)좌클릭 또는 우클릭/$하면 형태 설정 GUI를 열 수 있습니다."
    ),
    ("entries/programming/tutorial_1.json", 10): (
        "프로그래머 GUI로 돌아와 $(thing)GPS 영역 도구/$를 든 채 $(thing)굴착/$ 위젯에 "
        "연결된 $(thing)영역/$ 위젯을 $(thing)좌클릭/$하세요. 앞과 마찬가지로 설정이 영역 "
        "위젯에 복사됩니다.$(p)이제 오류를 나타내는 빨간 표시가 없어야 합니다. 축하합니다. "
        "올바른 프로그램을 만들었습니다!"
    ),
    ("entries/programming/tutorial_1.json", 11): (
        "마지막으로 $(l:tools/drone)드론/$을 $(l:machines/charging_station)충전소/$에서 "
        "가압하세요. 프로그래머 GUI 오른쪽 위 슬롯에 드론을 넣고 $(thing)⟶(내보내기)/$ "
        "버튼을 누르세요. 원한다면 왼쪽 입력란에서 드론 이름도 지정할 수 있습니다.$(p)"
        "소리가 들리면 드론 프로그래밍이 완료된 것입니다!"
    ),
    ("entries/programming/tutorial_1.json", 12): (
        "이제 드론을 배치하면 됩니다. 상자 근처의 월드를 $(thing)우클릭/$하고 드론이 "
        "작업하는 모습을 지켜보세요!"
    ),
    ("entries/armor/overview.json", 17): (
        "$(l:base_concepts/upgrades#thaumcraft)Thaumcraft 업그레이드/$는 해당 "
        "$(thing)마도사의 방어구/$와 같은 비스 할인을 제공합니다. 또한 "
        "$(l:armor/helmet)헬멧/$에 설치하면 $(item)Goggles of Revealing/$처럼 "
        "$(thing)오라 노드/$를 보여 주고 보관함에 든 $(thing)위상/$의 양을 표시합니다."
    ),
    ("entries/armor/pneumatic_chestplate.json", 17): (
        "$(l:base_concepts/upgrades#air_conditioning)공기 조절 업그레이드/$를 최대 4개 "
        "설치하면 $(l:https://minecraft.curseforge.com/projects/tough-as-nails)Tough As "
        "Nails/$ 모드가 추가하는 극한 환경 온도로부터 어느 정도 보호받습니다. 공기 조절 "
        "기능은 체온이 정상보다 높거나 낮으면 자동으로 작동하고, 정상으로 돌아오면 "
        "꺼집니다."
    ),
    ("entries/base_concepts/pressure.json", 1): (
        "압축 공기는 실제 압력 역학을 바탕으로 한 $(pncr)의 $(thing)동력 시스템/$입니다."
        "$(li)압축 공기는 여러 종류의 $(thing)압축기/$에서 $(italic)생산/$합니다."
        "$(li)가압할 수 있는 모든 기계와 도구에는 표준 대기압에서 저장할 수 있는 공기의 "
        "양을 뜻하는 $(thing)용량/$이 있습니다. 단위는 mL이며, 표준 대기압은 "
        "$(ttcolor)$(t:이 모드는 표준 대기압인 게이지 압력을 0bar로 표시합니다)0bar/$입니다."
    ),
    ("entries/base_concepts/pressure.json", 2): (
        "$(li)기계나 도구의 $(thing)압력 P/$는 다음과 같이 계산합니다:$(p)"
        "$(formula)P = (A / V) - 1/$$(p)여기서 $(formula)V/$는 $(thing)용량/$, "
        "$(formula)A/$는 기계에 현재 저장된 $(thing)공기/$입니다. 예를 들어 "
        "5000mL $(thing)용량/$의 기계에 20000mL $(thing)공기/$가 저장되어 있으면 "
        "압력은 $(thing)3bar/$입니다."
        "$(li)대부분의 기계는 $(l:base_concepts/upgrades#volume)용량 업그레이드/$로 용량을 "
        "늘릴 수 있으며, 용량이 커지면 공기를 사용할 때 압력이 덜 떨어집니다."
    ),
    ("entries/components/network_components.json", 7): (
        "$(item)네트워크 데이터 저장소/$에는 $(l:tools/drone)드론/$ 프로그램을 저장할 수 "
        "있습니다. 프로그래밍할 때 $(l:programming/puzzle_pieces)퍼즐 조각/$이 필요하지 "
        "않지만 프로그램을 $(italic)직접 실행할 수는 없습니다/$. 프로그램 모음을 보관하거나 다른 "
        "플레이어와 프로그램을 교환할 때 유용합니다."
    ),
    ("entries/compressors/advanced_air_compressor.json", 1): (
        "$(item)고급 공기 압축기/$는 $(l:compressors/air_compressor)공기 압축기/$의 "
        "$(l:base_concepts/pressure_tiers)2등급/$ 버전으로, 최대 안전 압력은 20bar입니다. "
        "기본적으로 $(ttcolor)$(t:속도 업그레이드를 설치하면 늘릴 수 있습니다)틱당 "
        "50mL/$의 공기를 생산하며 $(l:base_concepts/upgrades#speed)속도 업그레이드/$를 "
        "설치할 수 있습니다.$(p)다만 이 발전기는 $(l:base_concepts/heat)냉각/$해야 합니다. "
        "온도가 오를수록 효율이 떨어지고, 지나치게 뜨거우면 공기를 전혀 생산하지 않습니다."
    ),
    ("entries/compressors/air_compressor.json", 1): (
        "$(item)공기 압축기/$는 $(l:base_concepts/pressure)압축 공기/$를 생산하는 간단한 "
        "발전기입니다. 바닐라 $(item)화로/$에 넣을 수 있는 고체 연료를 태워 기본적으로 "
        "$(ttcolor)$(t:속도 업그레이드를 설치하면 늘릴 수 있습니다)틱당 10mL/$의 공기를 "
        "생산합니다.$(p)$(item)용암 양동이/$를 비롯해 액체 연료가 든 양동이는 "
        "$(italic)사용할 수 없습니다/$. 액체 연료에는 "
        "$(l:compressors/liquid_compressor)액체 압축기/$를 "
        "사용하세요."
    ),
    ("entries/compressors/electrostatic_compressor.json", 2): (
        "번개가 칠 확률을 높이려면 $(item)철창/$이나 $(item)피뢰침/$으로 만든 "
        "$(ttcolor)$(t:'pneumaticraft:electrostatic_grid' 블록 태그로 격자 블록을 바꿀 수 "
        "있습니다)격자/$를 압축기와 이 기계에 연결하세요. 격자가 번개의 도체 역할을 "
        "합니다.$(p)격자가 클수록 좋습니다. 격자 블록은 수평 반경 5블록, 위아래 5블록 "
        "이내에 둘 수 있지만, 모두 서로 이어져 $(item)정전기 압축기/$에 연결되어야 합니다."
    ),
    ("entries/compressors/electrostatic_compressor.json", 6): (
        "번개가 칠 확률을 더 높이려면 압축기 $(italic)바로 위/$에 격자 블록을 최대 "
        "10개까지 쌓아 $(thing)피뢰침/$을 만들 수 있습니다. 블록 하나마다 번개가 칠 "
        "확률이 조금씩 높아집니다."
    ),
    ("entries/logistics/logistics_configurator.json", 1): (
        "$(item)물류 설정기/$는 $(l:logistics/overview)물류 시스템/$을 구성하는 데 "
        "사용합니다.$(p)$(l:logistics/frames)물류 프레임/$을 $(thing)우클릭/$하면 여러 "
        "필터를 설정할 수 있습니다.$(p)$(thing)몸을 숙인 채 우클릭/$하면 인벤토리에 "
        "부착된 프레임을 떼어 냅니다."
    ),
    ("entries/logistics/logistics_drone.json", 1): (
        "$(item)물류 드론/$은 $(l:tools/drone)드론/$의 특수한 하위 등급입니다. "
        "프로그래밍할 수 없는 $(thing)하위 등급 드론/$이며 $(italic)물류 작업만/$ 수행합니다."
    ),
    ("entries/logistics/logistics_drone.json", 3): (
        "다른 드론과 마찬가지로 작동하려면 $(l:base_concepts/pressure)압력/$이 필요합니다. "
        "공기가 부족해지면 $(l:tools/drone#charging)발사기 업그레이드가 설치된 충전소/$를 "
        "자동으로 찾아갑니다."
    ),
    ("entries/machines/air_cannon.json", 1): (
        "$(item)에어 캐논/$은 $(l:base_concepts/pressure)압축 공기/$를 추진제로 사용해 "
        "아이템을 공중으로 멀리 운반하는 장치입니다.$(p)$(item)에어 캐논/$을 조준하려면 "
        "$(l:tools/gps_tool)GPS 도구/$가 "
        "필요합니다. 조준을 마친 뒤에는 GPS 도구를 빼서 다시 사용할 수 있습니다.$(p)"
        "$(#f00)레드스톤 펄스/$를 보내면 대포가 발사됩니다."
    ),
    ("entries/machines/aphorism_tile.json", 1): (
        "$(thing)격언 타일/$은 $(item)표지판/$과 비슷하지만 원하는 만큼의 텍스트를 "
        "표시할 수 있습니다. 전체 문구가 타일 안에 들어가도록 글자 크기가 자동으로 "
        "조정됩니다.$(p)격언 타일을 설치하면 기본적으로 "
        "$(ttcolor)$(t:클라이언트 설정의 'B:dramaSplash'에서 끌 수 있습니다)"
        "$(l:http://mc-drama.herokuapp.com/)Drama Generator/$의 무작위 문구/$가 표시됩니다."
    ),
    ("entries/machines/aphorism_tile.json", 2): (
        "$(li)빈손으로 $(item)격언 타일/$을 $(thing)우클릭/$하면 설치된 자리에서 편집할 "
        "수 있습니다.$(li)$(thing)Alt + 0-9/a-f/l/m/n/o/r/$을 사용해 "
        "$(l:https://minecraft.gamepedia.com/Formatting_codes)표준 Minecraft 서식 코드/$를 "
        "추가할 수 있습니다.$(li)$(thing)F1/$을 누르고 있으면 편집기 단축키 도움말이 "
        "나타납니다.$(li)염료를 들고 $(item)격언 타일/$을 $(thing)우클릭/$하면 색을 바꿀 수 "
        "있습니다. 타일의 해당 영역을 클릭해 테두리와 배경을 따로 칠할 수 있습니다."
    ),
    ("entries/machines/drone_interface.json", 1): (
        "드론 인터페이스는 $(l:tools/drone)드론/$과 통신하는 "
        "$(thing)ComputerCraft/OpenComputers 주변 장치/$입니다. $(item)드론/$에 "
        "$(l:programming/computer_control)컴퓨터 제어 퍼즐 조각/$을 사용해 프로그램을 "
        "작성하세요.$(p)드론이 컴퓨터 제어 조각을 실행하면 조각의 영역 안에 있는 "
        "$(ttcolor)$(t:드론 인터페이스 하나에는 한 번에 드론 하나만 연결할 수 있습니다)"
        "사용 가능한/$ $(item)드론 인터페이스/$에 연결을 시도합니다."
    ),
    ("entries/machines/drone_interface.json", 4): (
        'Lua 프로그램 예시:$(br)$(#008)m = peripheral.wrap("right")$(br)'
        'm.addArea(100, 64, 100, 120, 4, 120, "Filled")$(br)m.setAction("dig")'
        "$(br)while not m.isActionDone()$(br)do$(br)  sleep(1)$(br)end$(br)m.clearArea()"
        '$(br)m.addArea(80, 65, 80)$(br)m.setAction("goto")$(br)-- wait till done, '
        'as above$(br)m.setAction("standby")$(p)/$드론이 (100,64,100)부터 '
        "(120,4,120)까지의 넓은 영역에 있는 모든 블록을 굴착한 뒤 (80,65,80)으로 "
        "돌아가 대기하게 합니다."
    ),
    ("entries/machines/elevators.json", 2): (
        "$(thing)엘리베이터/$의 최대 높이는 $(item)엘리베이터 기반/$과 "
        "$(item)엘리베이터 프레임/$ 수로 결정됩니다. 다음 두 값 중 더 작은 값이 최대 "
        "높이입니다:$(li)수직으로 쌓은 $(item)엘리베이터 프레임/$ 수 × 1$(li)"
        "$(ttcolor)$(t:모드 설정의 'I:elevatorBaseBlocksPerBase'에서 배수를 바꿀 수 "
        "있습니다)수직으로 쌓은 $(item)엘리베이터 기반/$ 수 × 6인 값/$입니다. 이 값보다 "
        "높게 $(thing)엘리베이터/$를 만들 수 없습니다."
    ),
    ("entries/machines/kerosene_lamp.json", 2): (
        "$(item)등유 램프/$의 기본 범위는 10블록이며 GUI에서 최대 30블록까지 조정할 수 "
        "있습니다. 범위가 커질수록 연료 소비량은 제곱으로 늘어나므로 범위를 두 배로 "
        "늘리면 연료를 네 배 사용합니다.$(p)그래도 연료 소모량은 적습니다. 등유 "
        "1000mB와 기본 범위 10블록 기준으로 약 "
        "$(ttcolor)$(t:모드 설정의 'D:keroseneLampFuelEfficiency'에서 효율을 바꿀 수 "
        "있습니다)현실 시간 40분/$ 동안 작동합니다."
    ),
    ("entries/machines/pneumatic_door.json", 5): (
        "$(thing)공압 문/$은 문 기반 GUI에서 다음 세 모드 중 하나로 설정할 수 있습니다:"
        "$(li)$(thing)플레이어 접근/$: 플레이어가 범위 안에 들어오면 열립니다."
        "$(li)$(thing)접근 및 바라보기/$: 플레이어가 가까이에서 문을 $(italic)바라보면/$ "
        "열립니다."
        "$(li)$(thing)나무 문/$: 바닐라 $(item)나무 문/$처럼 작동합니다."
    ),
    ("entries/machines/tanks.json", 3): (
        "네 종류의 탱크는 서로 수직으로 $(thing)연결/$해 멀티블록처럼 만들 수 있습니다. "
        "$(l:tools/pneumatic_wrench)렌치/$로 탱크를 우클릭하세요. 위쪽 절반을 클릭하면 위 "
        "탱크에, 아래쪽 절반을 클릭하면 아래 탱크에 연결을 시도합니다.$(p)연결된 탱크의 "
        "경우 공간이 있다면 $(ttcolor)$(t:밀도가 0보다 작은 유체는 아래가 아니라 위로 "
        "이동합니다)위쪽 탱크/$의 유체가 아래쪽 탱크로 자동으로 흐릅니다."
    ),
    ("entries/machines/tanks.json", 5): (
        "다음 제한이 있습니다:$(li)두 탱크에는 같은 유체가 들어 있거나 둘 중 하나가 "
        "비어 있어야 연결할 수 있습니다.$(li)유체는 $(italic)위로 이동하지 않으므로/$, 가장 좋은 "
        "결과를 내려면 맨 위 탱크에 주입하고 맨 아래 탱크에서 빼내세요.$(li)탱크 GUI에는 "
        "우클릭한 탱크에 든 유체의 양만 표시됩니다."
    ),
    ("entries/machines/universal_sensor.json", 1): (
        "$(thing)범용 센서/$는 이름처럼 다양한 용도로 쓸 수 있습니다. 월드의 상태를 "
        "측정하고 결과에 따라 $(#f00)레드스톤 신호/$를 출력합니다.$(p)범용 기능에는 "
        "비용이 듭니다. $(ttcolor)$(t:상시 레드스톤 방출기는 무료로 사용할 수 있습니다)"
        "거의 모든/$ 경우 작동에 틱당 1mL의 $(l:base_concepts/pressure)공기/$가 필요하며, "
        "센서가 작동하려면 알맞은 $(l:base_concepts/upgrades)업그레이드/$도 필요합니다."
    ),
    ("entries/manufacturing/pressure_chamber.json", 2): (
        "$(li)$(thing)모서리/$와 $(thing)꼭짓점/$에는 $(item)압력 챔버 벽/$ 또는 "
        "$(item)압력 챔버 유리/$를 사용해야 합니다.$(li)$(thing)면/$에는 "
        "$(item)압력 챔버 벽/$, $(item)압력 챔버 유리/$, $(item)압력 챔버 밸브/$ 또는 "
        "$(l:manufacturing/pressure_chamber#interface)압력 챔버 인터페이스/$를 사용할 수 "
        "있습니다.$(li)$(item)압력 챔버 밸브/$가 하나 이상 필요합니다.$(li)"
        "$(item)압력 챔버 인터페이스/$는 "
        "두 개 이상을 권장하며, 하나는 안쪽을 향하고 하나는 바깥쪽을 향해야 합니다."
    ),
    ("entries/manufacturing/pressure_chamber.json", 17): (
        "$(item)강화 압력 챔버 밸브/$는 압력 챔버의 최대 압력을 기본 5bar에서 20bar로 "
        "높이는 고급 블록입니다. 챔버에 공기를 네 배 저장할 수 있고 "
        "$(ttcolor)$(t:기본 압력 챔버 제조법에는 최대 5bar만 필요하지만 모드팩에서 바꿀 "
        "수 있습니다)새 제조법/$이 해금될 수도 있습니다."
    ),
    ("entries/programming/block_right_click.json", 3): (
        "이 위젯으로 일반 블록을 설치할 수도 있지만 $(italic)권장하지 않습니다/$. 이미 블록이 있는 "
        "위치를 드론이 우클릭하면 그 블록과 상호작용하여 원래 위치가 아닌 $(italic)옆/$에 "
        "블록을 설치하기 때문입니다.$(p)따라서 보통은 $(l:programming/place)설치/$ 위젯을 "
        "사용하세요. 다만 $(item)씨앗/$을 심는 것처럼 $(thing)블록 우클릭/$ 위젯이 필요한 "
        "상황도 있습니다."
    ),
    ("entries/programming/condition_item.json", 3): (
        "검사할 아이템을 여러 개 추가할 수 있습니다. 오른쪽 두 번째 줄에 "
        "$(l:programming/item_filter)아이템 필터/$를 여러 개 연결하면 $(italic)모든/$ "
        "아이템이 필터와 일치할 때만 조건이 $(thing)참/$이 됩니다. 왼쪽에 놓은 "
        "$(l:programming/item_filter)아이템 필터/$는 조건이 $(thing)참/$이 되려면 해당 "
        "필터와 $(italic)일치하지 않아야/$ 합니다."
    ),
    ("entries/programming/conditions.json", 11): (
        "블록을 검사하는 모든 $(thing)월드 조건/$에는 여러 블록을 검사할 때 쓰는 "
        "$(thing)하나라도/모두/$ 옵션이 있습니다.$(li)$(thing)하나라도/$ 모드에서는 선택한 "
        "$(l:programming/area)영역/$의 블록 중 $(italic)하나/$만 일치해도 $(thing)참/$입니다."
        "$(li)$(thing)모두/$ 모드에서는 $(italic)모든/$ 블록이 일치해야 $(thing)참/$입니다."
    ),
    ("entries/programming/crafting.json", 2): (
        "제작 위젯은 기본적으로 가능한 한 많은 아이템을 제작합니다. 위젯 GUI의 "
        "$(thing)수량 사용/$ 설정으로 한도를 정할 수 있습니다.$(p)$(item)드론/$의 인벤토리를 "
        "늘리려면 $(l:base_concepts/upgrades#dispenser)인벤토리 업그레이드/$를 설치하세요."
    ),
    ("entries/programming/flow_control.json", 4): (
        "$(li)$(l:programming/label)레이블/$ 위젯은 프로그램에서 이동할 지점을 "
        "표시합니다.$(li)$(l:programming/jump)점프/$ 위젯은 조건 없이 즉시 이름이 같은 "
        "$(thing)레이블/$ 위젯으로 이동합니다.$(li)$(l:programming/conditions)조건/$ "
        "위젯은 검사 결과에 따라 점프를 실행할 수 있습니다.$(li)고급 "
        "$(l:programming/for_each_item)각 아이템 반복/$ 및 "
        "$(l:programming/for_each_coordinate)각 좌표 반복/$ 위젯은 입력 목록을 처리하며 "
        "$(thing)레이블/$로 반복해서 이동합니다."
    ),
    ("entries/programming/for_each_coordinate.json", 1): (
        "이 고급 위젯은 지정한 $(l:programming/area)영역/$의 모든 좌표를 차례로 "
        "처리합니다. 각 좌표를 $(ttcolor)$(t:위젯을 우클릭해 변수를 설정하세요)지정한 "
        "변수/$에 저장하고, 연결된 $(l:programming/text)텍스트/$ 위젯과 이름이 같은 "
        "$(l:programming/label)레이블/$로 이동합니다. 해당 루틴이 끝나면 이 위젯으로 "
        "돌아와 다음 좌표를 처리합니다. 일반적으로 루틴은 프로그램 끝에서 "
        "$(l:programming/start)시작/$으로 돌아갑니다."
    ),
    ("entries/programming/goto.json", 1): (
        "$(thing)위치로 이동/$은 간단합니다. $(l:tools/drone)드론/$이 지정한 "
        "$(l:programming/area)영역/$ 안에서 도달할 수 있는 가장 가까운 위치로 이동합니다."
        "$(p)드론이 $(ttcolor)$(t:설정 GUI에서 위젯이 즉시 완료되도록 바꿀 수 있습니다)"
        "영역에 도착/$하거나 해당 영역에 도달할 수 없으면 위젯이 완료됩니다."
    ),
    ("entries/programming/harvest.json", 3): (
        "$(item)드론/$이 $(l:programming/inventory_import)인벤토리에서 가져오기/$로 "
        "$(item)괭이/$를 가져오게 할 수 있습니다. 괭이를 장착하면 작물을 수확한 뒤 "
        "자동으로 다시 심으며, 이때 괭이의 내구도를 사용합니다.$(p)위젯 설정 GUI에서 "
        "$(item)괭이 필요/$를 선택하면 $(item)드론/$이 괭이를 들었을 때$(italic)만/$ "
        "수확합니다. 괭이가 "
        "부러지면 다른 괭이를 가져온 뒤 수확을 계속할 수 있습니다."
    ),
    ("entries/programming/liquid_export.json", 2): (
        "위젯 GUI에서 드론이 유체를 내보낼 탱크 면과 한 작업에서 내보낼 최대 유체량을 "
        "mB 단위로 지정할 수 있습니다.$(p)$(ttcolor)$(t:오른쪽에 연결하면 화이트리스트, "
        "왼쪽에 연결하면 블랙리스트로 작동합니다)$(l:programming/liquid_filter)유체 "
        "필터/$를 연결/$해 드론이 내보낼 수 있는 유체를 제한할 수 있습니다.$(p)"
        "$(item)드론/$의 "
        "탱크에 해당 유체가 없거나, 영역 안에 유체를 받을 탱크가 없으면 완료됩니다."
    ),
    ("entries/programming/liquid_import.json", 2): (
        "위젯을 $(thing)우클릭/$해 설정 GUI를 열면 드론이 유체를 가져올 탱크 면과 한 "
        "작업에서 가져올 최대 유체량을 mB 단위로 지정할 수 있습니다.$(p)"
        "$(ttcolor)$(t:오른쪽에 연결하면 화이트리스트, 왼쪽에 연결하면 블랙리스트로 "
        "작동합니다)$(l:programming/liquid_filter)유체 필터/$를 연결/$해 드론이 가져올 수 "
        "있는 유체를 제한할 수 있습니다.$(p)$(item)드론/$의 탱크가 가득 차거나 탱크에서 "
        "더 이상 "
        "해당 유체를 찾지 못하면 완료됩니다."
    ),
    ("entries/programming/start.json", 1): (
        "$(thing)시작/$ 위젯은 프로그램의 첫 위젯이며 "
        "$(l:programming/flow_control)프로그램 실행/$이 시작되는 곳입니다.$(p)$(italic)반드시/$ "
        "하나만 있어야 합니다."
    ),
    ("entries/programming/variables.json", 9): (
        "일반 변수는 $(l:tools/drone)드론/$마다 따로 있어 공유할 수 없습니다. 그러나 "
        "$(thing)전역 변수/$는 $(italic)공유할 수 있어/$ 드론끼리 통신할 수 있습니다.$(p)또한 "
        "$(l:tools/gps_tool)GPS 도구/$로 전역 변수를 연결하고 수정할 수 있고, "
        "$(l:machines/universal_sensor)범용 센서/$는 변수에 따라 $(#f00)레드스톤 신호/$를 "
        "출력하며, $(l:tools/remote)리모컨/$은 변수를 표시하고 수정할 수 있습니다."
    ),
    ("entries/programming/variables.json", 11): (
        "$(ttcolor)$(t:플레이어 전역 변수는 PNC:R 3.0.0, MC 1.18.1에서 추가되었습니다)"
        "전역 변수는 두 종류/$입니다: $(thing)플레이어 전역/$과 $(thing)서버 전역/$입니다."
        "$(li)플레이어 전역 변수는 '#'으로 시작하며 한 플레이어의 드론끼리 공유되고 다른 "
        "플레이어에게는 공개되지 않습니다.$(li)서버 전역 변수는 '%'로 시작하며 서버의 "
        "$(italic)모든/$ 플레이어가 공유합니다.$(p)참고: 이전 버전에는 '#'으로 시작하는 "
        "서버 전역 변수만 있었습니다."
    ),
    ("entries/renewables/overview.json", 2): (
        "1a단계: $(thing)효모 배양액/$을 만드세요. 버섯과 물을 "
        "$(l:manufacturing/thermopneumatic_processing_plant)열공압 처리 공장/$에서 "
        "혼합합니다. 공장의 온도는 30~60°C여야 하며, 생물군계와 고도에 따라 이 온도를 "
        "맞추기 쉬울 수도, 어려울 수도 있습니다."
    ),
    ("entries/renewables/overview.json", 4): (
        "2단계: $(thing)효모 배양액/$과 $(thing)설탕/$을 "
        "$(l:manufacturing/thermopneumatic_processing_plant)열공압 처리 공장/$에 넣어 "
        "$(thing)에탄올/$을 만드세요. 1a단계와 마찬가지로 온도 조건을 맞춰야 합니다."
    ),
    ("entries/semiblocks/transfer_gadget.json", 2): (
        "전송 도구는 두 색 중 하나로 표시됩니다:$(li)$(6)주황색/$ - 출력 모드"
        "$(li)$(9)파란색/$ - 입력 모드$(p)$(6)출력 모드/$에서는 부착된 인벤토리나 "
        "탱크에서 꺼내 이웃 블록에 넣고, $(9)입력 모드/$에서는 반대로 옮깁니다. 2초마다 "
        "아이템 1개 또는 유체 100mB를 전송합니다."
    ),
    ("entries/tools/amadron_tablet.json", 2): (
        "태블릿 GUI는 연결된 인벤토리나 탱크를 확인해 구매 가능한 항목을 판단합니다. "
        "$(ttcolor)$(t:자원은 아이템이나 유체일 수 있습니다)자원/$을 주문하면 "
        "$(thing)드론/$이 "
        "나타나 지불할 자원을 수거하고, 수거를 마치면 두 번째 $(thing)드론/$이 구매한 물품을 "
        "배달합니다.$(p)이 방법으로 $(l:components/pcb_blueprint)PCB 청사진/$이나 "
        "$(l:manufacturing/assembly_programs)조립 프로그램/$처럼 다른 방법으로 구할 수 "
        "없는 아이템을 얻을 수 있습니다. 매일 무작위로 갱신되는 $(thing)주민 거래/$도 "
        "추가됩니다."
    ),
    ("entries/tools/collector_drone.json", 3): (
        "다른 드론과 마찬가지로 작동하려면 $(l:base_concepts/pressure)압력/$이 필요합니다. "
        "공기가 부족해지면 $(l:tools/drone#charging)발사기 업그레이드가 설치된 충전소/$를 "
        "자동으로 찾아갑니다."
    ),
    ("entries/tools/drone.json", 3): (
        "드론은 공기가 부족해지면 주 프로그램을 멈추고, 압력이 1bar 이상이며 "
        "$(l:base_concepts/upgrades#dispenser)발사기 업그레이드/$가 설치된 "
        "$(l:machines/charging_station)충전소/$를 "
        "$(ttcolor)$(t:모드 설정의 'max_drone_charging_station_search_range'에서 바꿀 수 "
        "있습니다)80블록/$ 안에서 찾습니다.$(p)충전소를 찾으면 더 이상 공기를 공급받을 "
        "수 없을 때까지 충전합니다. 충전을 마친 $(item)드론/$은 $(item)충전소/$에서 "
        "떠나 $(item)드론/$의 주 프로그램을 다시 실행합니다."
    ),
    ("entries/tools/gps_tool.json", 3): (
        "$(l:programming/variables#global)전역 변수/$는 "
        "$(l:programming/coordinate_operator)좌표 연산자/$로 사용하는 고급 "
        "$(l:base_concepts/drone)드론/$ "
        "기능입니다.$(p)공중에서 $(item)GPS 도구/$를 $(thing)우클릭/$하면 변수 이름을 "
        "입력할 수 있습니다.$(p)이후 해당 $(thing)전역 변수/$는 $(item)GPS 도구/$에서 "
        "선택한 좌표 값을 따라갑니다. 이를 이용해 동적으로 바뀌는 영역을 사용하는 "
        "$(thing)드론 프로그램/$을 만들 수 "
        "있습니다."
    ),
    ("entries/tools/guard_drone.json", 3): (
        "다른 드론과 마찬가지로 작동하려면 $(l:base_concepts/pressure)압력/$이 필요합니다. "
        "공기가 부족해지면 $(l:tools/drone#charging)발사기 업그레이드가 설치된 충전소/$를 "
        "자동으로 찾아갑니다."
    ),
    ("entries/tools/harvesting_drone.json", 3): (
        "다른 드론과 마찬가지로 작동하려면 $(l:base_concepts/pressure)압력/$이 필요합니다. "
        "공기가 부족해지면 $(l:tools/drone#charging)발사기 업그레이드가 설치된 충전소/$를 "
        "자동으로 찾아갑니다."
    ),
    ("entries/tools/manometer.json", 4): (
        "$(thing)The One Probe/$나 $(thing)WAILA/HWYLA/$ 같은 모드가 설치되어 있으면 "
        "$(item)압력계/$를 사용할 일이 적을 수 있습니다."
    ),
    ("entries/tools/micromissiles.json", 4): (
        "$(item)마이크로미사일/$은 개체나 블록에 부딪히면 즉시 폭발합니다. 기본적으로 "
        "$(ttcolor)$(t:모드 설정의 'B:damageTerrain'에서 바꿀 수 있습니다)지형에는 피해를 "
        "주지 않습니다/$.$(p)수명은 기본적으로 "
        "$(ttcolor)$(t:모드 설정의 'I:missileLifetime'에서 바꿀 수 있습니다)"
        "$(item)마이크로미사일/$의 수명은 300틱(15초)/$"
        "입니다. 시간이 지나면 연료가 떨어져 추락하지만 땅에 닿으면 여전히 폭발합니다."
    ),
    ("entries/tools/minigun_ammo.json", 7): (
        "$(item)폭발성 미니건 탄약/$의 탄창 용량은 250발입니다. 명중하면 작지만 매우 "
        "강력한 폭발을 일으킬 수 있으며, 플레이어도 폭발 피해를 받을 수 있으니 "
        "주의하세요. 기본적으로 $(ttcolor)$(t:설정의 'B:explosiveAmmoTerrainDamage'에서 "
        "바꿀 수 있습니다)지형에는 피해를 주지 않습니다/$."
    ),
    ("entries/tubes/redstone_module.json", 2): (
        "모듈에 $(l:tubes/module_expansion_card)모듈 확장 카드/$를 적용하면 추가 신호 "
        "처리를 사용할 수 있습니다. 모듈이 $(thing)출력 모드/$일 때 우클릭해 GUI를 열면 "
        "신호 반전이나 다른 채널과의 AND/OR/XOR 연산처럼 출력 신호에 적용할 모드를 "
        "고를 수 있습니다.$(p)각 모드의 효과는 모듈 GUI에 자세히 설명되어 있습니다."
    ),
    ("entries/tubes/regulator_module.json", 3): (
        "$(thing)조절기 모듈/$은 레드스톤 신호와 관계없이 반대 방향, 즉 좁은 쪽에서 "
        "넓은 쪽으로 공기를 제한 없이 흘려보냅니다. 따라서 레드스톤 신호를 최대로 받은 "
        "조절기를 단방향 밸브로 사용할 수 있습니다.$(p)$(thing)조절기/$는 좁은 쪽의 "
        "압력을 $(italic)직접 낮추지 않습니다/$. 압력이 임계값보다 높아질 때 공기 흐름만 "
        "막습니다."
    ),
    ("entries/tubes/safety_module.json", 2): (
        "$(item)안전 모듈/$의 기본 임계값은 튜브 위험 압력보다 0.1bar 낮습니다:"
        "$(li)기본 $(item)압력 튜브/$: 4.9bar$(li)$(item)고급 압력 튜브/$: 19.9bar"
        "$(p)1.12.2 버전에서는 임계값을 정할 때 레드스톤 신호가 필요했지만 현재는 "
        "작동 방식이 바뀌었습니다."
    ),
    ("entries/tubes/tube_modules.json", 3): (
        "$(thing)인라인 모듈/$에는 다음과 같은 특별한 제한이 있습니다:$(li)압력 튜브 "
        "하나에는 인라인 모듈을 하나만 설치할 수 있습니다.$(li)인라인 모듈이 설치된 압력 "
        "튜브에는 다른 모듈을 설치할 수 없습니다.$(li)인라인 모듈의 양 끝에 해당하는 두 "
        "면으로만 연결할 수 있습니다.$(li)인라인 모듈은 $(italic)압력 튜브의 열린 "
        "끝/$에만 설치할 수 있습니다."
    ),
    ("entries/machines/elevators.json", 7): (
        "$(item)엘리베이터 기반/$에는 $(l:base_concepts/upgrades#charging)충전 업그레이드/$를 "
        "최대 4개까지 설치할 수 있습니다. 엘리베이터가 내려갈 때 사용한 공기의 일부를 "
        "회수합니다. 원래 하강에는 공기가 들지 않지만 공기를 회수하지도 않습니다.$(p)"
        "대신 하강 속도가 느려집니다. 업그레이드 4개를 설치하면 같은 거리를 올라갈 때 "
        "사용하는 공기의 60%를 회수하고 하강 속도는 40% 느려집니다."
    ),
    ("entries/machines/elevators.json", 9): (
        "$(item)엘리베이터 프레임/$ 옆에 설치한 $(item)엘리베이터 호출기/$로 "
        "$(thing)엘리베이터/$의 높이를 조절합니다. $(item)엘리베이터 프레임/$을 설치하면 "
        "다른 $(item)엘리베이터 호출기/$가 지정한 $(thing)층/$의 수를 계산합니다.$(p)"
        "$(thing)층/$ 이름은 $(item)엘리베이터 기반/$ GUI에서 지정할 수 있습니다. 각 "
        "$(item)엘리베이터 호출기/$에 층 이름이 버튼으로 표시되며, 버튼을 누르면 "
        "$(thing)엘리베이터/$를 해당 층으로 호출합니다."
    ),
    ("entries/manufacturing/thermopneumatic_processing_plant.json", 1): (
        "$(thing)열공압 처리 공장/$은 $(l:base_concepts/pressure)압력/$이나 "
        "$(l:base_concepts/heat)열/$로 재료를 처리하며 다음 용도로 사용합니다:$(li)"
        "$(thing)LPG/$ 100mB와 $(item)석탄/$ 1개로 $(l:components/plastic)플라스틱/$ "
        "1000mB를 만듭니다. 열은 필요하지만 압력은 필요하지 않습니다.$(li)$(thing)디젤/$ "
        "1000mB와 $(item)레드스톤 가루/$ 1개로 $(l:components/lubricant)윤활유/$ 1000mB를 "
        "만듭니다. 이 과정도 열은 필요하지만 압력은 필요하지 않습니다."
    ),
    ("entries/spawning/spawner_extractor.json", 1): (
        "$(item)생성기 추출기/$는 $(l:spawning/spawner_core)생성기 코어/$를 얻는 두 방법 "
        "중 하나입니다. 생성기 코어는 $(l:spawning/pressurized_spawner)가압 생성기/$를 "
        "사용할 때 필요합니다.$(p)월드에서 바닐라 $(item)생성기/$를 찾아 그 위에 생성기 "
        "추출기를 설치하세요."
    ),
    ("entries/programming/entity_export.json", 1): (
        "$(l:tools/drone)드론/$이 지정한 $(l:programming/area)영역/$으로 이동해 운반 중인 "
        "개체를 내려놓습니다. 연결된 $(l:programming/text)텍스트/$ 위젯에 선택적으로 지정한 "
        "$(l:base_concepts/entity_filter)개체 필터/$가 허용하는 개체만 내려놓습니다.$(p)"
        "$(l:programming/entity_import)개체 가져오기/$ 위젯도 참조하세요."
    ),
    ("entries/programming/entity_import.json", 1): (
        "$(l:tools/drone)드론/$이 지정한 $(l:programming/area)영역/$에서 연결된 "
        "$(l:programming/text)텍스트/$ 위젯의 선택적 "
        "$(l:base_concepts/entity_filter)개체 필터/$와 일치하는 가장 가까운 개체를 찾아 "
        "운반합니다.$(p)플레이어도 운반할 수 있지만 $(thing)몸을 숙이면/$ "
        "$(item)드론/$에서 쉽게 내릴 수 있습니다. 조종할 수 있는 비행 개체에 실려 "
        "이동하는 것도 나름의 장점이 있습니다."
    ),
    ("entries/programming/external_program.json", 2): (
        "$(l:programming/programmer)프로그래머/$도 인벤토리로 취급되므로 이 위젯으로 "
        "$(item)드론/$ 프로그램을 디버그할 수 있습니다. $(thing)외부 프로그램/$ 위젯에 "
        "$(item)프로그래머/$만 포함하는 영역을 지정해 $(item)드론/$을 프로그래밍한 뒤 "
        "배치하세요.$(p)프로그래머에 $(item)드론/$ 또는 $(item)네트워크 API/$를 넣고 "
        "프로그램을 작성하세요. $(item)프로그래머/$에서 $(thing)⟶(내보내기)/$ 버튼을 "
        "누르면 배치된 $(item)드론/$이 즉시 프로그램을 실행합니다."
    ),
    ("entries/programming/label.json", 2): (
        "$(thing)레이블/$ 위젯은 $(l:programming/conditions)조건/$을 사용할 때 프로그램 "
        "흐름에 $(italic)분기/$를 만들거나, 프로그램 구역을 나란히 정리할 때 사용합니다. "
        "$(l:programming/programmer)프로그래머/$ GUI 왼쪽 아래에서 $(bold)흐름 표시/$를 "
        "선택하면 이름이 같은 $(thing)점프/조건/레이블/$ 위젯을 잇는 선이 표시됩니다."
    ),
    ("entries/programming/teleport.json", 1): (
        "$(thing)순간이동/$은 $(l:programming/goto)위치로 이동/$보다 "
        "$(l:base_concepts/pressure)공기/$를 많이 쓰지만 작동 방식은 간단합니다. "
        "$(l:tools/drone)드론/$이 지정한 $(l:programming/area)영역/$ 안에서 도달할 수 있는 "
        "가장 가까운 위치로 순간이동합니다.$(p)$(item)드론/$은 한 번에 공기 10000mL를 "
        "사용합니다. 업그레이드하지 않은 $(item)드론/$ 용량의 대부분이므로 "
        "$(l:base_concepts/upgrades#volume)용량 업그레이드/$를 권장합니다."
    ),
    ("entries/programming/variables.json", 3): (
        "$(thing)변수/$에는 X/Y/Z 좌표만 저장되지만, 한 축만 사용하면 "
        "$(thing)정수/$도 표현할 수 있고 0을 거짓, 그 밖의 값을 참으로 정하면 "
        "$(thing)불리언/$도 표현할 수 있습니다. 자유롭게 활용해 보세요!"
    ),
    ("entries/renewables/overview.json", 5): (
        "3단계: 약간의 압력을 공급한 "
        "$(l:manufacturing/thermopneumatic_processing_plant)열공압 처리 공장/$에서 "
        "$(thing)씨앗/$이나 $(thing)작물/$을 압착해 $(thing)식물성 기름/$을 만드세요."
    ),
    ("entries/renewables/vegetable_oil.json", 1): (
        "$(thing)식물성 기름/$은 $(l:manufacturing/thermopneumatic_processing_plant)열공압 "
        "처리 공장/$에서 여러 $(thing)씨앗/$과 $(thing)작물/$로 만들 수 있습니다. 보통 "
        "다 자란 작물보다 씨앗에서 기름을 더 많이 얻습니다. 식물성 기름은 "
        "$(l:renewables/biodiesel)바이오디젤/$ 생산에 필요합니다."
    ),
    ("entries/semiblocks/transfer_gadget.json", 1): (
        "$(item)전송 도구/$는 간단한 아이템·유체 운반 장치입니다. 두 인벤토리나 탱크 "
        "$(italic)사이/$에 설치해 자원을 옮깁니다. 먼저 한쪽 인벤토리를 설치하고 그 블록의 "
        "옆면을 $(item)전송 도구/$로 우클릭한 뒤 두 번째 인벤토리를 설치하는 것이 가장 "
        "쉽습니다."
    ),
    ("entries/tools/drone.json", 1): (
        "드론은 다양한 자동화에 사용하는 강력한 프로그래밍 가능 비행 로봇입니다. 작동하려면 "
        "먼저 프로그램을 작성해야 하며, $(l:programming/programmer)프로그래머/$와 "
        "$(l:programming/puzzle_pieces)퍼즐 조각/$이 필요합니다.$(p)프로그램을 작성하고 "
        "$(l:base_concepts/pressure)가압한/$ 드론을 배치하면 지정한 작업을 수행합니다."
    ),
    ("entries/tools/drone.json", 10): (
        "알아 두면 좋은 기능이 몇 가지 더 있습니다:$(li)$(l:tools/gps_tool)GPS 도구/$로 "
        "드론을 우클릭하면 GPS 도구에 저장된 블록 위치로 이동합니다. 드론의 경로 탐색을 "
        "시험할 때 유용합니다.$(li)공압 헬멧의 "
        "$(l:base_concepts/upgrades#security)보안 업그레이드/$로 드론을 해킹하면 프로그램을 "
        "멈추고 플레이어에게 돌아옵니다. 접근하기 어려운 곳에 드론이 남았을 때 유용하며, "
        "다시 해킹하면 프로그램을 계속 실행합니다."
    ),
    ("entries/machines/drone_interface.json", 6): (
        "$(l:programming/programmer)프로그래머/$에서 드론 프로그램을 작성할 때와 달리, "
        "앞의 Lua 프로그램은 굴착과 이동 작업이 끝날 때까지 명시적으로 기다린 뒤 다음 "
        "작업을 실행해야 합니다. Lua 프로그램은 별도 스레드에서 실행되어 월드와 직접 "
        "상호작용하지 못하므로 드론에 다음 작업을 지시하고 완료 여부를 확인해야 합니다."
    ),
    ("entries/programming/void_item.json", 1): (
        "드론 인벤토리의 아이템을 즉시 영구적으로 파괴하므로 주의하세요! "
        "$(l:programming/item_filter)아이템 필터/$와 함께 사용하는 것을 강력히 권장합니다. "
        "필터를 사용하면 필터에서 허용한 아이템만 제거합니다.$(p)"
        "$(item)드론/$ 인벤토리에 대상 아이템이 하나도 남지 않으면 위젯 실행이 끝납니다."
    ),
    ("entries/programming/void_liquid.json", 1): (
        "$(l:programming/void_item)아이템 제거 위젯/$과 마찬가지로 드론 탱크의 유체를 "
        "즉시 영구적으로 제거하므로 주의하세요! "
        "$(l:programming/liquid_filter)유체 필터/$와 함께 사용하는 것을 강력히 권장합니다. "
        "필터를 사용하면 필터에서 허용한 유체만 제거합니다."
    ),
    ("entries/tubes/tube_junction.json", 1): (
        "$(thing)튜브 접합부/$는 두 $(l:tubes/pressure_tubes)압력 튜브/$를 서로 연결하지 "
        "않고 교차시키는 간단한 장치입니다. 튜브의 "
        "$(l:base_concepts/pressure_tiers)압력 등급/$은 달라도 됩니다."
    ),
    ("entries/machines/pneumatic_dynamo.json", 1): (
        "$(item)공압 다이너모/$는 $(l:base_concepts/pressure)압축 공기/$를 "
        "$(thing)Forge Energy/$로 변환하며, $(thing)Redstone Flux/$와 다른 모드의 에너지 "
        "시스템과 호환됩니다. 기본 생산량은 40FE/틱이며 "
        "$(l:base_concepts/upgrades#speed)속도 업그레이드/$로 늘릴 수 있습니다. "
        "$(item)자속 압축기/$의 FE 출력 한도는 현재 FE 생산량의 두 배이므로, 기본값은 "
        "80FE/틱이며 속도 업그레이드로 증가합니다."
    ),
    ("entries/machines/pneumatic_generator.json", 1): (
        "공압 발전기는 $(l:base_concepts/pressure)압축 공기/$로 "
        "$(thing)IndustrialCraft 2 EU/$를 생산합니다. 최소 작동 압력이 15bar인 "
        "2등급 기계입니다. 기본 효율은 40%이며 "
        "$(ttcolor)$(t:'I:pneumaticGeneratorEfficiency' 참조)설정에서 변경/$할 수 있습니다."
        "$(p)$(l:base_concepts/upgrades#speed)속도 업그레이드/$가 없으면 32EU/틱, 하나를 "
        "설치하면 128EU/틱, 두 개를 설치하면 512EU/틱을 출력합니다."
    ),
    ("entries/machines/pneumatic_generator.json", 2): (
        "공기 소모량(mL/틱)은 다음과 같습니다:$(p)$(formula)출력 속도 / E × 400/$"
        "$(p)여기서 $(formula)E/$는 효율(%)입니다. 예를 들어 기본 효율 40%, 출력 속도 "
        "32EU/틱이면 공기 소모량은 $(formula)32 / 40 × 400 = 320mL/틱/$입니다."
    ),
    ("entries/machines/liquid_hopper.json", 2): (
        "$(item)유체 호퍼/$는 $(9)입력/$ 면 앞의 바닥에 떨어진 아이템에서 유체를 "
        "빼내고, $(6)출력/$ 면 앞의 아이템에는 유체를 넣으려고 합니다. 물 양동이, "
        "용암 양동이, 다른 모드의 유체 용기 등이 대상입니다."
    ),
    ("entries/machines/liquid_hopper.json", 4): (
        "$(l:base_concepts/upgrades#dispenser)발사기 업그레이드/$를 $(item)유체 호퍼/$에 "
        "설치하면 $(9)입력/$ 면의 유체 블록 1000mB를 빨아들이고, 저장한 유체 1000mB를 "
        "$(6)출력/$ 면에 배치합니다. 예를 들어 물 펌프로 사용할 수 있습니다."
    ),
    ("entries/machines/heat_sink.json", 1): (
        "$(item)방열판/$은 $(l:base_concepts/heat)열/$을 방출하는 블록입니다.$(p)"
        "60°C보다 뜨겁거나 -60°C보다 차가운 $(item)방열판/$에 닿으면 피해를 받으니 "
        "주의하세요!$(p)$(item)방열판/$은 직접 연결된 블록의 열만 방출합니다. 여러 "
        "$(item)방열판/$을 연결하려면 $(l:machines/heat_pipe)열 파이프/$로 부착할 면을 "
        "늘리세요."
    ),
    ("entries/machines/heat_sink.json", 3): "능동 냉각",
    ("entries/machines/heat_sink.json", 4): (
        "$(item)방열판/$을 $(l:tubes/air_grate_module#active_cooling)에어 그레이트 모듈/$ "
        "범위 안에 두면 방열 효과가 커집니다. 모듈을 "
        "$(l:tubes/pressure_tubes)압력 튜브/$에 부착하면 범위가 표시됩니다. 여러 에어 "
        "그레이트 모듈의 냉각 효과는 중첩됩니다."
    ),
    ("entries/compressors/electrostatic_compressor.json", 1): (
        "$(item)정전기 압축기/$는 $(thing)번개/$ 에너지로 압축 공기를 생산하는 "
        "$(l:base_concepts/pressure_tiers)2등급/$ 공기 "
        "$(l:base_concepts/pressure)압축기/$입니다.$(p)번개가 치면 즉시 공기 200,000mL를 "
        "생산합니다. 많은 양이지만 대전된 크리퍼가 알아서 자주 찾아오지는 않으니, "
        "압축기에 번개가 치도록 해야 합니다."
    ),
    ("entries/compressors/electrostatic_compressor.json", 3): (
        "왼쪽 그림에서 최대 효율을 낼 만큼 큰 격자에 둘러싸인 것은 중앙 압축기뿐입니다. "
        "다른 압축기는 번개를 일으킬 확률이 더 낮습니다. 그래도 격자 중앙에 압축기 하나만 "
        "두는 것보다는 효과적입니다."
    ),
    ("entries/compressors/electrostatic_compressor.json", 4): (
        "하나의 $(thing)격자/$에 $(item)정전기 압축기/$를 여러 대 연결하면 번개로 생산한 "
        "공기가 압축기마다 똑같이 나뉩니다.$(p)번개가 친 뒤 압력이 너무 높아져 압축기가 "
        "폭발하지 않도록 압축기 아래쪽에 $(item)철창/$을 연결할 수 있습니다. 그러면 "
        "에너지가 기계로 들어가지 않고 땅으로 방출됩니다."
    ),
    ("entries/compressors/electrostatic_compressor.json", 5): (
        "이 방출은 압축기가 위험 압력에 도달했을 때만 일어납니다. 압축기 $(italic)바로/$ "
        "아래의 같은 Y축에 있는 $(item)철창/$ 하나마다 초과 공기를 최대 10,000mL까지 "
        "방출합니다.$(p)따라서 압축기 10대를 하나의 $(thing)격자/$에 연결했다면 "
        "$(ttcolor)$(t:압축기당 생산 공기 200000 / 10 = 20000, 철창 2개의 방출량 "
        "10000 × 2 = 20000)압축기마다 아래에 격자 블록 2개/$만 있으면 됩니다. "
        "($(l:base_concepts/upgrades#security)보안 업그레이드/$를 설치할 수도 있지만 더 "
        "비싸고 효과는 낮습니다.)"
    ),
    ("entries/compressors/electrostatic_compressor.json", 7): (
        "$(bold)참고:/$ 이전 버전의 $(pncr)와 달리 자연 번개는 압축기에 공기를 "
        "$(italic)추가하지 않습니다/$. 다른 모드로 번개를 만들어 악용할 수 있었기 "
        "때문입니다. 대신 압축기가 일정 확률로 ‘가짜’ 번개를 만듭니다. 맑은 날에는 이 "
        "확률이 $(italic)매우/$ 낮지만 $(thing)비/$가 오면 높아지고, "
        "$(thing)뇌우/$가 치면 크게 높아집니다."
    ),
    ("entries/base_concepts/memory_essence.json", 1): (
        "$(item)기억의 정수/$는 플레이어의 기억과 경험을 액체로 나타낸 유체입니다. "
        "추출해 저장했다가 바닐라 마법 부여나 일부 $(pncr) 제작 과정에 사용할 수 있습니다."
        "$(p)$(item)기억의 정수/$를 얻는 방법은 두 가지입니다:$(li)1. "
        "$(l:tools/memory_stick)메모리 스틱/$ 사용$(li)2. "
        "$(l:machines/aerial_interface)공중 인터페이스/$ 사용"
    ),
    ("entries/semiblocks/transfer_gadget.json", 3): (
        "빈손이나 $(l:tools/logistics_configurator)물류 설정기/$로 $(item)전송 도구/$를 "
        "$(thing)우클릭/$하면 입력/출력 모드를 전환합니다. $(thing)Shift+우클릭/$하거나 "
        "좌클릭해서 때리면 $(item)전송 도구/$를 제거합니다.$(p)속도가 느리고 제작법이 "
        "저렴하므로 공간이 부족한 게임 초반의 아이템·유체 운반에 적합합니다."
    ),
    ("entries/semiblocks/heat_frame.json", 1): (
        "이 아이템은 모든 $(thing)인벤토리/$에 설치할 수 있습니다. 인접한 "
        "$(l:base_concepts/heat)열원/$으로 가열하면 인벤토리의 아이템을 제련하고, 냉각하면 "
        "얼리려고 합니다. 결과 아이템을 넣을 공간이 있어야 작동합니다. 더 많이 가열할수록 "
        "제련 속도가 빨라져 최대 초당 아이템 1개를 처리하며, 더 많이 냉각할수록 아이템을 "
        "얼리는 속도가 빨라집니다."
    ),
    ("entries/semiblocks/heat_frame.json", 3): (
        "$(thing)열 프레임/$은 냉각 제작법에 "
        "$(l:https://minecraft.curseforge.com/projects/crafttweaker)CraftTweaker/$를 지원합니다. "
        "제련에는 일반 $(item)화로/$ 제작법을 사용합니다. 냉각 제작법은 추가하거나 제거할 "
        "수 있으며, 자세한 내용은 아래 링크를 확인하세요."
    ),
    ("entries/programming/block_right_click.json", 2): (
        "이 위젯은 프로그래머의 위젯 GUI에서 다음 두 모드 중 하나를 선택해 작동합니다:"
        "$(li)아이템 모드 - $(thing)든 아이템/$의 우클릭 동작을 사용합니다. 예: 블록에 "
        "$(item)부싯돌과 부시/$ 사용$(li)블록 모드 - $(thing)블록/$의 우클릭 동작을 "
        "활성화합니다. 예: $(item)레버/$ 전환$(p)$(thing)아이템 모드/$에서는 연결된 "
        "필터가 사용하는 $(italic)아이템/$에 적용되고, $(thing)블록 모드/$에서는 활성화할 "
        "$(italic)블록/$에 적용됩니다."
    ),
    ("entries/programming/programmable_controller.json", 1): (
        "프로그래밍 가능 제어기는 $(l:tools/drone)드론/$과 매우 비슷한 작업을 수행할 수 "
        "있습니다. $(l:programming/programmer)프로그래머/$에서 프로그램을 작성해 "
        "$(item)드론/$이나 $(l:components/network_components#network_api)네트워크 API/$에 "
        "저장한 뒤 $(item)프로그래밍 가능 제어기/$에 넣으세요. "
        "$(l:base_concepts/pressure)압력/$이 충분하면 $(item)프로그래밍 가능 제어기/$는 "
        "$(item)드론/$에 프로그램했을 때와 똑같이 프로그램을 실행합니다. "
    ),
    ("entries/programming/programmable_controller.json", 3): (
        "$(li)$(item)프로그래밍 가능 제어기/$는 다음 위젯을 실행할 수 없습니다: 컴퓨터 "
        "조각, 개체 공격, 드론 조건: 개체, 개체 내보내기, 개체 가져오기, 순간이동, 대기, "
        "자폭.$(p)$(item)프로그래밍 가능 제어기/$는 넓은 영역 굴착이나 대형 구조물 건설 "
        "같은 대규모 작업에 특히 적합합니다."
    ),
    ("entries/programming/programmable_controller.json", 4): "아이템·유체 연결",
    ("entries/programming/programmable_controller.json", 5): (
        "$(thing)미니드론/$이 수집한 아이템과 유체는 $(item)프로그래밍 가능 제어기/$ "
        "블록의 측면을 통해 넣거나 뺄 수 있습니다.$(p)기본 ‘드론’에는 인벤토리 슬롯 1개와 "
        "16000mB 탱크가 있습니다. $(l:base_concepts/upgrades#inventory)인벤토리 "
        "업그레이드/$를 최대 35개까지 추가해 인벤토리를 늘릴 수 있으며, 업그레이드마다 "
        "탱크 용량도 1000mB씩 늘어납니다."
    ),
    ("entries/programming/programmable_controller.json", 8): "아이템 충전",
    ("entries/programming/programmable_controller.json", 9): (
        "프로그래밍 가능 제어기는 미니드론이 든 아이템, 즉 드론 인벤토리 0번 슬롯의 "
        "아이템을 $(thing)충전/$할 수 있습니다. $(l:tools/jackhammer)착암기/$처럼 압축 "
        "공기로 충전하는 아이템과 $(thing)Forge Energy/$ 아이템을 모두 지원하며, 제어기 "
        "자체 버퍼의 공기 및 FE를 사용합니다. 충전은 기본적으로 꺼져 있으므로 제어기 GUI의 "
        "$(thing)든 아이템 충전/$ 측면 탭에서 켜세요."
    ),
    ("entries/machines/smart_chest.json", 1): (
        "$(item)스마트 상자/$는 슬롯이 72개인 상자입니다. 동생 격인 "
        "$(l:machines/reinforced_chest)강화 상자/$처럼 흑요석 수준의 폭발 저항을 지니고, "
        "부숴도 내용물을 보존합니다. 그 밖에도 매우 강력한 기능이 있습니다."
    ),
    ("entries/machines/smart_chest.json", 4): "아이템 밀어내기",
    ("entries/machines/smart_chest.json", 5): (
        "스마트 상자의 각 면은 아이템을 밀어내거나 끌어오거나 아무 작업도 하지 않도록 "
        "따로 설정할 수 있습니다. 기본값은 아무 작업도 하지 않는 것입니다. GUI의 "
        "$(thing)측면 설정/$ 탭에서 설정하세요.$(p)밀어내기로 설정한 면은 스마트 상자의 "
        "아이템을 그 면에 인접한 인벤토리로 보냅니다. $(item)발사기 업그레이드/$를 "
        "설치했다면 인접한 인벤토리가 없을 때 아이템을 월드에 배출합니다."
    ),
    ("entries/machines/smart_chest.json", 6): "아이템 끌어오기",
    ("entries/machines/smart_chest.json", 7): (
        "끌어오기로 설정한 면은 그 면에 인접한 인벤토리에서 아이템을 가져옵니다.$(p)"
        "$(l:base_concepts/upgrades#magnet)자석 업그레이드/$를 설치하면 주변 바닥의 아이템도 "
        "흡수합니다. 끌어오기로 설정한 면에서만 작동하며, 기본 수집 범위는 해당 면에 "
        "인접한 3x3x3 정육면체입니다. $(l:base_concepts/upgrades#range)범위 업그레이드/$로 "
        "범위를 늘릴 수 있습니다."
    ),
    ("entries/programming/void_item.json", 0): "아이템 폐기 위젯",
    ("entries/programming/void_liquid.json", 0): "유체 폐기 위젯",
    ("entries/manufacturing/assembly_system.json", 1): (
        "상위 등급 재료를 제작하려면 여러 $(thing)조립 기계/$로 이루어진 "
        "$(thing)조립 시스템/$이 필요합니다. 기계들은 수평으로 인접하면 서로 통신합니다. "
        "$(item)조립 IO 유닛/$을 제외한 각 종류의 기계는 하나씩만 둘 수 있습니다. 조립 "
        "라인은 $(l:base_concepts/pressure)압축 공기/$로 작동하지만, 전체 시스템에 동력을 "
        "공급할 때는 조립 제어기에만 공기를 공급하면 됩니다."
    ),
    ("entries/manufacturing/assembly_system.json", 2): (
        "$(thing)조립 시스템/$의 두뇌입니다. "
        "$(l:manufacturing/assembly_programs)프로그램/$을 받아 $(item)제어기/$가 다른 "
        "$(thing)조립 기계/$를 제어하는 방법을 정합니다.$(p)제어기 화면에는 현재 상태의 "
        "진단 정보가 표시됩니다. GUI를 열어 작동 상태를 확인하세요."
    ),
    ("entries/manufacturing/assembly_system.json", 3): (
        "$(item)IO 유닛/$은 인벤토리와 $(item)조립 플랫폼/$을 연결합니다. 이 로봇 팔은 "
        "대각선 방향에도 닿습니다.$(p)IO 유닛은 완성품을 내보내거나 제작 재료를 가져올 수 "
        "있습니다. 바닐라 $(item)상자/$나 모드가 추가한 인벤토리 블록을 포함해 모든 "
        "인벤토리를 사용할 수 있습니다."
    ),
    ("entries/manufacturing/assembly_system.json", 5): (
        "$(thing)조립 시스템/$에는 $(italic)두 개/$의 $(item)IO 유닛/$, 즉 입력 유닛과 "
        "출력 유닛이 하나씩 필요합니다. $(6)주황색/$은 출력, $(9)파란색/$은 입력을 "
        "뜻합니다. $(item)IO 유닛/$이 작동하려면 $(item)조립 플랫폼/$과, 모드에 따라 "
        "아이템을 꺼내거나 보관할 인벤토리에 모두 닿아야 합니다."
    ),
    ("entries/manufacturing/assembly_system.json", 8): (
        "$(item)조립 레이저/$는 재료를 자르거나 아이템을 나누고 모서리를 잘라 냅니다."
        "$(p)$(item)조립 드릴/$과 마찬가지로 대각선에는 $(italic)닿지 않습니다/$."
    ),
    ("entries/manufacturing/assembly_system.json", 9): "사용법",
    ("entries/manufacturing/assembly_system.json", 10): (
        "$(thing)조립 시스템/$으로 제작하려면 $(item)조립 제어기/$에 "
        "$(l:manufacturing/assembly_programs)조립 프로그램/$을 넣고 입력 인벤토리에 필요한 "
        "아이템을 넣으세요.$(p)제어기와 설치한 프로그램이 아는 제작법에 맞는 아이템은 "
        "자동으로 처리됩니다."
    ),
    ("entries/manufacturing/etching_tank.json", 1): (
        "먼저 $(thing)에칭 탱크/$를 $(l:manufacturing/etching_acid)에칭 산/$으로 채우세요. "
        "그런 다음 $(l:manufacturing/uv_light_box)UV 라이트 박스/$에서 일부 또는 전부 "
        "노광한 $(thing)빈 PCB/$를 최대 25개 넣으세요.$(p)에칭 산을 월드에 붓고 PCB를 "
        "그 안에 던져도 되지만, 에칭 탱크를 사용하면 훨씬 안전하고 빠릅니다."
    ),
    ("entries/manufacturing/etching_tank.json", 3): (
        "$(thing)빈 PCB/$는 어느 면으로든 투입할 수 있습니다. 에칭에 성공한 "
        "$(thing)미조립 PCB/$는 오른쪽 위 출력 슬롯으로, $(thing)불량 PCB/$는 오른쪽 "
        "아래 슬롯으로 이동합니다. 자동으로 꺼낼 때는 미조립 PCB를 기계 옆면에서, 불량 "
        "PCB를 위나 아래에서 꺼내세요. 불량 PCB를 $(thing)용광로/$로 보내 노광하지 않은 "
        "빈 PCB로 되돌린 뒤 과정을 다시 시작하도록 자동화할 수도 있습니다."
    ),
    ("entries/manufacturing/etching_tank.json", 4): "가열",
    ("entries/manufacturing/etching_tank.json", 5): (
        "$(l:base_concepts/heat)열/$이 없으면 PCB 하나를 완전히 에칭하는 데 150초가 "
        "걸립니다. 최대 25개를 동시에 에칭할 수 있습니다. 탱크를 가열하면 온도가 높을수록 "
        "처리 시간이 짧아져 최소 30초까지 줄어듭니다. 다만 가열한 상태로 PCB를 에칭하면 "
        "에칭 산이 조금씩 소모됩니다."
    ),
    ("entries/manufacturing/fluid_mixer.json", 1): (
        "$(thing)유체 혼합기/$는 $(l:base_concepts/pressure)압력/$으로 두 유체를 혼합해 "
        "유체 및 아이템 결과물을 만듭니다. 주로 $(l:renewables/biodiesel)바이오디젤/$을 "
        "생산할 때 사용합니다.$(p)압력이 높을수록 더 빨리 작동하지만 공기도 더 빨리 "
        "소모합니다."
    ),
    ("entries/manufacturing/refinery.json", 1): (
        "$(item)정유기/$는 $(l:base_concepts/heat)열/$로 "
        "$(l:base_concepts/oil)원유/$를 여러 연료로 정제하는 다중 블록 기계입니다. "
        "100°C부터 작동하며 온도가 높을수록 빠르게 정제합니다. 생산 연료를 가벼운 "
        "순서대로 나열하면 다음과 같습니다:$(li)$(thing)LPG(액화 석유 가스)/$"
        "$(li)$(thing)휘발유/$$(li)$(thing)등유/$$(li)$(thing)디젤/$"
    ),
    ("entries/manufacturing/refinery.json", 2): (
        "$(thing)정유기/$는 다중 블록 구조입니다. $(item)정유기 제어기/$를 놓고, 그 위나 "
        "옆에 $(item)정유기 출력부/$를 2~4개 쌓으세요.$(p)구조의 크기에 따라 수율이 "
        "달라집니다. 원유 10mB를 넣을 때:$(p)$(bold)출력부 2개/$"
        "$(li)$(thing)LPG/$ 2mB$(li)$(thing)디젤/$ 4mB$(br)$(bold)출력부 3개/$"
        "$(li)$(thing)LPG/$ 2mB$(li)$(thing)등유/$ 3mB$(li)$(thing)디젤/$ 2mB"
    ),
    ("entries/manufacturing/refinery.json", 3): (
        "$(bold)출력부 4개/$$(li)$(thing)LPG/$ 2mB$(li)$(thing)휘발유/$ 3mB"
        "$(li)$(thing)등유/$ 3mB$(li)$(thing)디젤/$ 2mB$(p)가장 가벼운 연료는 항상 "
        "맨 위 $(item)정유기 출력부/$에, 가장 무거운 연료는 맨 아래에 들어갑니다. 기존 "
        "구조에 $(item)정유기 출력부/$를 추가하면 작동을 계속할 수 있도록 이미 생산한 "
        "유체를 알맞은 출력부로 자동 재배치합니다."
    ),
    ("entries/manufacturing/refinery.json", 6): (
        "$(item)정유기/$에 $(item)비교기/$를 연결하면 $(item)정유기/$에 처리할 작업이 "
        "있을 때 신호 세기 15, 없을 때 0을 출력합니다. 정제할 $(thing)원유/$가 "
        "$(italic)있고/$ 정제 결과물을 "
        "넣을 출력 탱크 공간도 있어야 작업이 있는 것으로 판단합니다.$(p)예를 들어 공기를 "
        "절약하도록 $(l:machines/vortex_tube)볼텍스 튜브/$의 공기 공급을 자동으로 끌 때 "
        "사용할 수 있습니다."
    ),
    ("entries/manufacturing/refinery.json", 8): (
        "$(item)정유기/$는 여러 면이 공기에 노출된 다중 블록이라 단열하지 않으면 "
        "$(l:base_concepts/heat)열/$을 빠르게 잃습니다. 효율을 높이려면 사용하지 않는 면을 "
        "모두 덮는 것이 좋습니다. $(item)반 블록/$이나 $(item)다락문/$ 같은 블록을 포함해 "
        "열이 통하지 않는 블록이면 무엇이든 사용할 수 있지만, 특히 "
        "$(l:machines/thermal_lagging)단열재/$를 권장합니다."
    ),
    ("entries/manufacturing/refinery.json", 9): (
        "$(l:machines/vortex_tube)볼텍스 튜브/$로 $(item)정유기/$를 가열하거나, "
        "$(item)정유기/$ 블록 옆에 뜨거운 유체(용암 등)나 블록(마그마 블록 등)을 둘 수 "
        "있습니다. 이런 유체와 블록은 열을 빼앗겨 소모되므로 해당 자원의 생산과 배치를 "
        "자동화하는 편이 좋습니다."
    ),
    ("entries/manufacturing/refinery.json", 12): "정유기 제작",
    ("entries/logistics/overview.json", 1): (
        "$(pncr)의 $(thing)물류 시스템/$은 아이템과 유체를 운반하고 인벤토리와 탱크의 "
        "재고를 유지하는 방법을 제공합니다.$(p)인벤토리와 탱크에 "
        "$(l:logistics/frames)물류 프레임/$을 부착하면 해당 블록으로 아이템과 유체를 "
        "넣고 빼는 방식을 제어할 수 있습니다."
    ),
    ("entries/logistics/overview.json", 2): (
        "그 인벤토리는 $(l:logistics/logistics_drone)물류 드론/$이나, "
        "$(l:tubes/logistics_module)물류 모듈/$을 부착한 "
        "$(l:tubes/pressure_tubes)압력 튜브/$로 연결합니다.$(p)$(thing)물류 시스템/$은 "
        "$(l:https://wiki.factorio.com/Logistic_network)Factorio/$에서 큰 영향을 받았습니다. "
        "주된 차이는 별도의 물류 상자 대신 기존 인벤토리나 탱크에 부착할 "
        "$(l:logistics/frames)프레임/$을 제공한다는 점입니다."
    ),
    ("entries/logistics/logistics_drone.json", 4): (
        "$(item)물류 드론/$을 배치하면 배치 지점을 중심으로 한 33x33x33 범위 안에서 "
        "$(l:logistics/frames)물류 프레임/$이 붙은 모든 인벤토리와 탱크를 대상으로 "
        "작동합니다.$(p)아이템을 자주 옮기므로 이동 속도와 운반 용량을 높일 "
        "$(l:base_concepts/upgrades#speed)속도/$ 및 "
        "$(l:base_concepts/upgrades#inventory)인벤토리/$ 업그레이드를 권장합니다."
    ),
    ("entries/armor/overview.json", 1): (
        "$(pncr)에 $(thing)아이언맨/$의 HUD를 더하면 무엇이 될까요? 바로 "
        "$(thing)공압 방어구/$입니다!$(p)토니 스타크의 장비에서 영감을 받았다고 해서 "
        "무적은 아닙니다. 기본 상태에서는 같은 부위의 $(thing)철 방어구/$보다 방어력과 "
        "내구도가 조금 높을 뿐입니다. "
    ),
    ("entries/armor/overview.json", 3): (
        "하지만 이 방어구는 다양하게 업그레이드할 수 있습니다. 업그레이드를 설치하고 "
        "방어구를 가압하려면 $(l:machines/charging_station)충전소/$에 넣으세요.$(p)모든 "
        "부위에 공통으로 적용되는 업그레이드는 다음 페이지에서, 특정 부위 전용 업그레이드는 "
        "각 방어구 부위의 페이지에서 설명합니다."
    ),
    ("entries/armor/overview.json", 6): (
        "소중한 방어구를 수리하는 방법은 여러 가지입니다:$(li)압축 철 주괴로 "
        "$(thing)모루/$에서 수리$(li)각 부위에 $(thing)아이템 수명 업그레이드/$를 설치해 "
        "자동 수리$(li)각 부위에 $(thing)수선/$ 마법 부여 적용"
    ),
    ("entries/armor/overview.json", 8): (
        "모든 방어구 부위는 기본 회색 텍스처의 색을 자유롭게 바꿀 수 있습니다. 부위마다 "
        "$(thing)주 색상/$과 $(thing)보조 색상/$을 따로 조절할 수 있고, 헬멧의 "
        "$(thing)접안부/$에도 별도 색상을 지정할 수 있습니다.$(p)방어구 기본 GUI의 "
        "$(bold)색상.../$ 화면에서 조절하세요. 기본 기능이므로 별도 업그레이드는 필요하지 "
        "않습니다."
    ),
    ("entries/armor/overview.json", 9): (
        "$(l:base_concepts/upgrades#speed)속도 업그레이드/$는 각 방어구 부위의 기동 시간을 "
        "줄입니다. 또한 $(l:armor/pneumatic_helmet)헬멧/$의 "
        "$(l:base_concepts/upgrades#entity_tracker)개체 추적기/$와 "
        "$(l:base_concepts/upgrades#block_tracker)블록 추적기/$가 대상을 포착하는 시간을 "
        "줄이고, $(l:armor/pneumatic_leggings)레깅스/$의 달리기 속도를 높이지만 "
        "$(l:base_concepts/pressure)공기/$를 소모합니다."
    ),
    ("entries/armor/overview.json", 11): (
        "$(l:base_concepts/upgrades#armor)방어구 업그레이드/$는 각 방어구 부위의 방어력과 "
        "강인함을 높입니다. 두 개를 설치하면 각 부위가 해당 $(thing)다이아몬드 방어구/$와 "
        "같은 성능을 내며, 최대 네 개를 설치하면 $(thing)다이아몬드 방어구/$보다 높은 "
        "방어력을 냅니다."
    ),
    ("entries/armor/overview.json", 12): (
        "$(l:base_concepts/upgrades#item_life)아이템 수명 업그레이드/$는 "
        "$(l:base_concepts/pressure)공기/$를 소모해 방어구 부위를 천천히 수리합니다. 부위마다 "
        "최대 5개를 설치할 수 있으며, 추가할수록 수리 속도는 빨라지지만 공기 효율은 "
        "낮아집니다."
    ),
    ("entries/armor/overview.json", 13): (
        "$(l:base_concepts/upgrades#gilded)도금 업그레이드/$를 어느 방어구 부위에든 설치하면 "
        "$(thing)피글린/$이 플레이어가 실제로 $(thing)금 방어구/$를 입었다고 착각합니다. "
        "어리석은 피글린이네요."
    ),
    ("entries/armor/overview.json", 15): (
        "$(l:base_concepts/upgrades#radiation_shielding)방사선 차폐 업그레이드/$는 Mekanism의 "
        "$(l:https://wiki.aidancbrady.com/wiki/Radiation_Shielding_Unit)방사선 차폐 장치/$와 "
        "마찬가지로 Mekanism 방사선의 해로운 효과를 막아 줍니다. 완전히 보호받으려면 모든 "
        "방어구 부위에 차폐 업그레이드를 설치해야 합니다."
    ),
    ("entries/armor/pneumatic_chestplate.json", 1): (
        "$(item)공압 흉갑/$은 네 $(thing)공압 방어구/$ 부위 중 하나입니다.$(p)다른 세 "
        "부위보다 $(l:base_concepts/pressure)공기 용량/$이 큽니다."
    ),
    ("entries/armor/pneumatic_chestplate.json", 3): (
        "$(l:base_concepts/upgrades#security)보안 업그레이드/$를 설치하면 많은 공기를 "
        "소모하는 대신 불과 용암으로부터 보호받습니다. 흉갑이 공기를 빠르게 방출해 주변 "
        "불을 끄고 체온을 낮추며, 가까운 용암도 천천히 굳힙니다."
    ),
    ("entries/armor/pneumatic_chestplate.json", 5): (
        "참고: 이 보호 기능은 화염 피해를 받기 직전에 작동합니다. 물약 등으로 이미 "
        "보호받고 있다면 이 업그레이드는 작동하지 않습니다."
    ),
    ("entries/armor/pneumatic_chestplate.json", 7): (
        "$(item)보안 업그레이드/$는 절연되지 않은 "
        "$(l:https://minecraft.curseforge.com/projects/immersive-engineering)Immersive Engineering/$ "
        "전선의 감전 피해도 막습니다. 막은 피해에 비례해 흉갑의 공기를 소모하며, 밀쳐내기 "
        "효과는 막지 못합니다."
    ),
    ("entries/armor/pneumatic_chestplate.json", 10): (
        "자석 업그레이드는 Botania의 $(item)솔레놀리아/$ 효과를 존중하며, Immersive "
        "Engineering의 $(item)컨베이어 벨트/$에서 아이템을 끌어오지 않습니다."
    ),
    ("entries/armor/pneumatic_chestplate.json", 12): (
        "$(l:base_concepts/upgrades#dispenser)발사기 업그레이드/$를 설치하면 "
        "$(l:machines/air_cannon)에어 캐논/$처럼 $(thing)$(k:pneumaticcraft.chestplate.launcher)/$"
        " 키를 눌렀다 놓아 보조 손의 아이템이나 블록을 발사할 수 있습니다. 완전히 충전하는 "
        "데 15틱(0.75초)이 걸리며, 더 일찍 키를 놓으면 낮은 속도로 발사합니다."
    ),
    ("entries/armor/pneumatic_chestplate.json", 14): (
        "$(li)$(item)TNT/$나 $(item)화살/$처럼 일부 블록과 아이템은 "
        "$(item)발사기/$와 비슷한 특수 동작을 합니다.$(li)$(item)횃불/$ 같은 블록은 "
        "회전하며 날아가다가 무언가에 부딪히면 블록으로 돌아옵니다.$(li)그 밖의 아이템은 "
        "아이템 개체로 발사됩니다."
    ),
    ("entries/armor/pneumatic_chestplate.json", 15): (
        "흉갑에 $(l:base_concepts/upgrades#range)범위 업그레이드/$를 설치하고 활성화하면 "
        "블록 상호작용 거리가 3.5블록 늘어납니다. 근접 공격 거리는 늘어나지 않으며, "
        "작동하는 동안 소량의 공기를 계속 소모합니다."
    ),
    ("entries/compressors/thermal_compressor.json", 1): (
        "$(item)열 압축기/$는 수평으로 마주 보는 면의 "
        "$(l:base_concepts/heat)온도/$ 차이로 $(l:base_concepts/pressure)압축 공기/$를 "
        "생산합니다. 온도 차이가 클수록 더 많은 공기를 생산합니다.$(p)참고: "
        "$(l:machines/vortex_tube)볼텍스 튜브/$만으로 이 압축기를 작동하면 생산량보다 "
        "소모량이 많아져 압력이 줄어듭니다."
    ),
    ("entries/compressors/thermal_compressor.json", 3): (
        "$(item)열 압축기/$의 남북 면끼리, 동서 면끼리는 열이 통하지만 남북과 동서 "
        "사이에는 열이 통하지 않습니다. 따라서 압축기 하나에 서로 독립된 온도 차이를 두 "
        "개 만들 수 있습니다.$(p)연결된 면의 열은 서로 평형을 이루므로 유효한 온도 차이를 "
        "유지할 방법이 필요합니다."
    ),
    ("entries/compressors/thermal_compressor.json", 4): "활용법",
    ("entries/compressors/thermal_compressor.json", 5): (
        "$(item)열 압축기/$의 주요 활용법은 세 가지입니다:$(li)$(item)볼텍스 튜브/$의 "
        "$(italic)한쪽/$에서 버리는 열이나 냉기를 활용할 수 있습니다. 보통 볼텍스 튜브의 "
        "뜨거운 쪽이나 차가운 쪽만 사용하고 반대쪽은 "
        "$(l:machines/heat_sink)방열판/$으로 방출하지만, $(item)열 압축기/$를 사용하면 "
        "그 에너지의 일부를 압력으로 회수할 수 있습니다."
    ),
    ("entries/compressors/thermal_compressor.json", 6): "활용법(계속)",
    ("entries/compressors/thermal_compressor.json", 7): (
        "$(li)$(l:compressors/advanced_air_compressor)고급 공기 압축기/$ 같은 상위 압축기의 "
        "폐열을 활용할 수 있습니다. 보통은 하나 이상의 "
        "$(l:tools/heat_sink)방열판/$으로 열을 대기에 방출하지만, 열 압축기를 사용하면 "
        "폐열의 일부를 압력으로 회수할 수 있습니다."
    ),
    ("entries/compressors/thermal_compressor.json", 8): "활용법(계속)",
    ("entries/compressors/thermal_compressor.json", 9): (
        "$(li)$(l:base_concepts/heat_sources)용암이나 다른 모드의 블록/$처럼 자연적으로 "
        "뜨겁거나 차가운 물질을 대량으로 얻을 수 있다면 압력 생산에 사용할 수 있습니다. "
        "열원과 열을 다 쓴 자원을 놓고 치우는 작업도 자동화해야 할 수 있으며, "
        "$(l:tools/drone)드론/$이나 다른 모드의 장치로 처리할 수 있습니다."
    ),
    ("entries/compressors/thermal_compressor.json", 11): (
        "이 압축기는 $(#f00)레드스톤 신호/$로 제어할 수 있습니다. 비활성화하면 압력 "
        "생산이 멈추고 남북 면과 동서 면 사이의 열저항이 크게 높아집니다. 열이 조금 새기는 "
        "하지만 작동 중일 때보다 훨씬 적습니다. 튜브 네트워크가 완전히 가압된 경우처럼 "
        "압력이 필요하지 않을 때 온도 차이의 형태로 에너지를 저장하는 데 유용합니다."
    ),
    ("entries/compressors/maunal_compressor.json", 1): (
        "$(item)수동 압축기/$는 플레이어의 노동과 허기를 사용해 게임 초반에 "
        "$(l:base_concepts/pressure)압축 공기/$를 생산합니다. 압축기를 우클릭한 채로 유지해 "
        "공기를 펌프질하세요. 압력이 높아질수록 한 번 펌프질하는 시간이 길어지며, 결국 더 "
        "이상 공기를 넣을 수 없게 됩니다."
    ),
    ("entries/tubes/logistics_module.json", 1): (
        "이 강력한 모듈은 인벤토리를 $(l:logistics/overview)물류 시스템/$에 연결해 압력 "
        "튜브를 통한 아이템과 유체 운반을 제어합니다.$(p)모듈이 가리키는 인벤토리나 유체 "
        "탱크에는 $(l:logistics/frames)물류 프레임/$이 부착되어 있어야 합니다.$(p)물류 "
        "모듈에는 $(l:tubes/module_expansion_card)모듈 확장 카드/$를 설치할 수 없습니다."
    ),
    ("entries/tubes/logistics_module.json", 2): (
        "$(l:logistics/frames#passive_provider)수동 공급자/$ 프레임과 "
        "$(l:logistics/frames#requester)요청자/$ 프레임이 붙은 상자를 연결하는 물류 모듈 두 개"
    ),
    ("entries/tubes/logistics_module.json", 3): (
        "물류 모듈 네트워크는 $(l:tubes/pressure_tubes)압력 튜브/$로 서로 연결된 모든 "
        "모듈로 이루어집니다. 공기를 사용하는 기계는 네트워크에 "
        "$(italic)포함되지 않습니다/$.$(p)모듈 GUI에서 채널을 고르거나 $(item)염료/$로 "
        "우클릭해 채널을 선택할 수 있습니다. 같은 색의 물류 모듈끼리만 통신하므로 네트워크 "
        "하나에 $(thing)채널/$ 16개를 사용할 수 있습니다."
    ),
    ("entries/tubes/logistics_module.json", 4): (
        "물류 모듈이 작동하려면 $(l:base_concepts/pressure)압력/$이 3bar 이상이어야 합니다. "
        "소모하는 공기량은 거리, 운반량, 상수를 곱한 값입니다. 따라서 한 스택 전체를 "
        "옮기거나 먼 거리로 옮길수록 공기가 더 많이 필요합니다. 공기는 "
        "$(italic)수신/$ 물류 모듈 쪽으로 흐르므로 그 모듈에서 소모됩니다."
    ),
    ("entries/tubes/logistics_module.json", 5): (
        "표시등은 다음 상태를 나타냅니다:$(p)$(li)$(#f00)빨간색/$: 압력 부족. 최소 "
        "3bar를 공급하세요.$(li)$(#f80)주황색/$: 3bar보다 높지만 현재 거리만큼 아이템이나 "
        "유체를 옮기기에는 부족합니다.$(li)$(#0f0)초록색/$: 압력 충분, 대기 중."
        "$(li)$(#00f)파란색(점멸)/$: 아이템이나 유체를 운반 중입니다."
    ),
    ("entries/tubes/flow_detector_module.json", 1): (
        "흐름 감지 모듈은 튜브 속 $(thing)공기 흐름/$을 측정하는 "
        "$(l:tubes/tube_modules#inline)인라인/$ 모듈입니다. 다음 공식에 따라 "
        "$(#f00)레드스톤 신호/$를 출력합니다:$(p)  "
        "$(formula)0.2 × 흐름(mL/틱)/$$(p)예를 들어 공기가 20mL/틱으로 흐르면 신호 "
        "세기는 20 × 0.2 = 4입니다."
    ),
    ("entries/tubes/flow_detector_module.json", 2): (
        "$(thing)흐름/$은 $(l:base_concepts/pressure)압력/$과 다른 물리량입니다. 흐름은 "
        "틱마다 튜브를 통과하는 공기의 양입니다. 예를 들어 "
        "$(l:machines/elevators)엘리베이터/$가 멈춰 있으면 흐름은 0이지만, 작동해 공기를 "
        "소모하면 0보다 커집니다. 따라서 이 모듈로 기계의 공기 사용 여부를 감지할 수 "
        "있습니다.$(p)흐름 감지 모듈에는 "
        "$(l:tubes/module_expansion_card)모듈 확장 카드/$를 설치할 수 없습니다."
    ),
    ("entries/machines/sentry_turret.json", 1): (
        "$(thing)감시 포탑/$은 자동 방어 무기입니다. 내장된 "
        "$(l:tools/minigun)미니건/$과 직접 공급해야 하는 "
        "$(l:tools/minigun_ammo)총기 탄약/$으로 범위 안의 개체를 공격합니다. 기본 사거리는 "
        "16블록이며 $(l:base_concepts/upgrades#range)범위 업그레이드/$로 최대 32블록까지 "
        "늘릴 수 있습니다.$(p)감시 포탑은 $(l:base_concepts/pressure)압력/$ 없이 작동하지만 "
        "$(l:tools/minigun_ammo)탄약/$은 반드시 공급해야 합니다."
    ),
    ("entries/machines/sentry_turret.json", 3): (
        "$(thing)감시 포탑/$이 하나 이상의 $(l:machines/security_station)보안 스테이션/$ "
        "범위 안에 있으면, 개체 필터 설정과 관계없이 $(italic)모든/$ 보안 스테이션의 신뢰 "
        "목록에 등록된 플레이어는 절대 공격하지 않습니다."
    ),
    ("entries/machines/thermal_lagging.json", 1): (
        "$(l:base_concepts/heat)열/$을 사용하는 $(pncr) 기계는 공기에 노출되면 열을 "
        "잃습니다. 공기가 아니며 열을 전달하지 않는 블록이면 거의 무엇으로든 덮을 수 "
        "있지만, $(thing)단열재/$는 기계를 단열하는 데 특히 적합합니다."
    ),
    ("entries/machines/thermal_lagging.json", 2): (
        "$(thing)단열재/$는 없는 것처럼 $(italic)통과해서 클릭/$하여 뒤쪽 블록과 "
        "상호작용할 수 있습니다.$(p)다만 $(item)곡괭이/$나 $(item)렌치/$를 들고 있거나 "
        "$(thing)웅크린/$ 상태라면 단열재 자체를 대상으로 삼아 제거하거나 상호작용할 수 "
        "있습니다."
    ),
    ("entries/tools/jackhammer.json", 1): (
        "$(item)공압식 착암기/$는 $(l:base_concepts/pressure)압력/$으로 모든 종류의 "
        "블록을 같은 효율로 부수는 다용도 채굴 도구입니다. "
        "$(l:machines/charging_station)충전소/$에서 "
        "$(l:base_concepts/upgrades#speed)속도 업그레이드/$로 채굴 속도를, "
        "$(l:base_concepts/upgrades#volume)용량 업그레이드/$로 공기 용량을 늘릴 수 있습니다."
    ),
    ("entries/tools/jackhammer.json", 3): (
        "새 착암기에는 $(thing)드릴 비트/$가 없어 그대로는 쓸모가 없습니다. 착암기를 "
        "우클릭해 설정 GUI를 열고 오른쪽 위 슬롯에 비트를 넣으세요.$(p)드릴 비트는 성능과 "
        "비용이 낮은 순서대로 네 종류입니다:$(li)철/$$(li)압축 철/$$(li)다이아몬드/$"
        "$(li)네더라이트/$"
    ),
    ("entries/tools/jackhammer.json", 5): (
        "착암기는 일부 $(thing)광맥 채굴/$ 기능을 포함한 여러 굴착 모드를 지원해 넓은 "
        "영역을 빠르게 파낼 수 있습니다. 사용할 수 있는 모드는 $(thing)드릴 비트/$에 "
        "따라 달라지며, 상위 비트일수록 채굴 속도가 빠르고 더 많은 굴착 모드를 지원합니다."
        "$(p)착암기를 우클릭해 GUI를 열고 오른쪽 아래 버튼으로 굴착 모드를 선택하세요."
    ),
    ("entries/tools/jackhammer.json", 6): (
        "$(italic)네더라이트 드릴 비트를 설치하고 3x3 굴착 모드를 선택한 착암기 GUI/$"
    ),
    ("entries/tools/jackhammer.json", 8): (
        "착암기는 $(thing)마법 부여대/$에서 일반적인 방법으로 마법을 부여할 수 없지만, "
        "GUI에서 $(thing)섬세한 손길/$이나 $(thing)행운/$ 마법이 붙은 책을 넣을 수 "
        "있습니다. 위쪽 가운데 책 슬롯에 넣은 책의 마법이 착암기에 적용됩니다."
    ),
    ("entries/tools/jackhammer.json", 10): (
        "필요에 따라 섬세한 손길 책과 행운 책을 쉽게 바꿔 쓸 수 있습니다.$(p)원하는 책을 "
        "얻기 어렵다면 $(l:manufacturing/pressure_chamber)압력 챔버/$로 도구의 마법을 "
        "추출해 책에 옮길 수 있다는 점을 기억하세요."
    ),
    ("entries/tools/camo_applicator.json", 1): (
        "$(item)위장 도포기/$로 다음 $(pncr) 블록을 위장할 수 있습니다:$(li)"
        "$(l:tubes/pressure_tubes)압력 튜브/$$(li)"
        "$(l:machines/pneumatic_door)공압 문 받침/$$(li)"
        "$(l:machines/elevators)엘리베이터 받침 및 호출기/$$(li)"
        "$(l:machines/charging_station)충전소/$$(li)$(l:machines/heat_pipe)열 파이프/$"
        "$(p)단단한 블록을 $(thing)우클릭/$하면 그 외형을 도포기에 복사하고, "
        "$(thing)Shift+우클릭/$하면 복사한 블록을 지웁니다. "
    ),
    ("entries/tools/camo_applicator.json", 2): (
        "그런 다음 위장할 수 있는 블록을 $(thing)우클릭/$하여 위장을 적용하거나 "
        "제거하세요.$(p)위장을 적용하려면 인벤토리에 해당 블록이 실제로 있어야 하며, 적용할 "
        "때 블록을 하나 소모합니다. 위장을 제거하면 그 블록을 돌려받습니다.$(p)위장한 "
        "블록을 곡괭이나 알맞은 도구로 부수면 블록 대신 위장만 벗길 수도 있습니다."
    ),
    ("entries/tools/reinforced_chest_kit.json", 1): (
        "$(item)강화 상자 업그레이드 키트/$는 내용물을 유지한 채 모든 나무 상자를 "
        "$(l:machines/reinforced_chest)강화 상자/$로 즉시 업그레이드합니다. 나무 상자에 "
        "키트를 들고 $(thing)Shift+우클릭/$하세요.$(p)참고: 업그레이드에 사용한 "
        "$(item)나무 상자/$는 아이템으로 떨어집니다."
    ),
    ("entries/tools/reinforced_chest_kit.json", 2): (
        "강화 상자 업그레이드 키트 제작$(p)강화 상자는 완전히 비어 있어야 합니다."
    ),
    ("entries/tools/smart_chest_kit.json", 1): (
        "$(item)스마트 상자 업그레이드 키트/$는 내용물을 유지한 채 나무 상자나 "
        "$(l:machines/reinforced_chest)강화 상자/$를 "
        "$(l:machines/smart_chest)스마트 상자/$로 즉시 업그레이드합니다. 대상 상자에 키트를 "
        "들고 $(thing)Shift+우클릭/$하세요."
    ),
    ("entries/tools/smart_chest_kit.json", 2): (
        "$(p)참고: $(item)강화 상자/$에 사용하면 강화 상자가 아이템으로 떨어지고, "
        "$(item)나무 상자/$에 사용하면 해당 상자가 아이템으로 떨어집니다."
    ),
    ("entries/tools/smart_chest_kit.json", 3): (
        "스마트 상자 업그레이드 키트 제작$(p)스마트 상자는 완전히 비어 있고 설정되지 않은 "
        "상태여야 합니다."
    ),
    ("entries/tools/memory_stick.json", 1): (
        "$(item)메모리 스틱/$은 플레이어의 경험치 레벨을 추출하고 저장했다가 되돌리는 "
        "휴대용 장치입니다:$(li)$(thing)우클릭/$: 플레이어의 경험치 1레벨을 스틱으로 이동"
        "$(li)$(thing)Shift+우클릭/$: 스틱의 경험치 1레벨을 플레이어에게 이동"
        "$(li)$(thing)좌클릭/$: 경험치 자동 흡수 전환. 플레이어가 얻는 경험치 구슬을 "
        "스틱이 자동으로 흡수합니다."
    ),
    ("entries/tools/memory_stick.json", 2): (
        "메모리 스틱에 저장한 경험치는 $(l:base_concepts/memory_essence)기억의 정수/$ "
        "유체로도 꺼낼 수 있습니다. $(l:machines/tanks)유체 탱크/$를 "
        "$(thing)우클릭/$하면 경험치를 탱크와 스틱 사이에서 옮깁니다. 다른 모드의 유체 "
        "탱크도 사용할 수 있습니다. 빈 탱크를 우클릭하면 스틱에서 탱크로, 기억의 정수가 "
        "든 탱크를 우클릭하면 탱크에서 스틱으로 옮기려고 합니다."
    ),
    ("entries/tools/memory_stick.json", 4): (
        "$(thing)Curios/$ 모드가 설치되어 있으면 메모리 스틱을 Curios 슬롯에 넣어 인벤토리 "
        "공간을 아낄 수 있습니다. 경험치 자동 흡수를 켰을 때 특히 유용합니다."
    ),
    ("entries/programming/item_assign.json", 2): (
        "지정한 $(thing)변수/$에 아이템을 저장하려면 원하는 아이템을 설정한 "
        "$(l:programming/item_filter)아이템 필터/$ 위젯을 $(thing)아이템 할당/$ 위젯의 "
        "$(italic)오른쪽/$에 놓으세요. $(thing)아이템 할당/$ 위젯을 "
        "$(thing)우클릭/$해 변수를 지정하면 그 아이템을 변수에 할당합니다. 필터에서는 "
        "실제 아이템만 전달되며 필터 설정은 전달되지 않습니다.$(p)$(thing)아이템 필터/$ "
        "위젯을 생략하면 드론이 든 아이템을 변수에 할당합니다."
    ),
    ("entries/spawning/vacuum_trap.json", 1): (
        "$(item)진공 덫/$은 몹을 가두고 정수를 "
        "$(l:spawning/spawner_core)생성기 코어/$에 흡수해 나중에 "
        "$(l:spawning/pressurized_spawner)가압 생성기/$에서 사용하게 하는 기계입니다."
        "$(p)$(thing)진공 덫/$은 다음 순서로 사용하세요:"
    ),
    ("entries/spawning/vacuum_trap.json", 2): (
        "$(li)1. 진공 덫의 압력이 -0.5bar 이하인지 확인하세요. "
        "$(l:base_concepts/upgrades#volume)용량 업그레이드/$를 권장합니다. 저장한 진공을 "
        "보존하려면 진공 덫을 곡괭이로 부수지 말고 렌치로 회수하세요.$(li)2. 포획한 몹을 "
        "받을, 가득 차지 않은 $(l:spawning/spawner_core)생성기 코어/$를 넣으세요.$(li)3. "
        "진공 덫을 $(thing)Shift+우클릭/$하거나 레드스톤 신호를 공급해 문을 여세요."
    ),
    ("entries/spawning/vacuum_trap.json", 4): (
        "진공 덫은 다음 대상을 절대 포획하지 않습니다:$(li)플레이어$(li)드론$(li)보스 몹"
        "(위더, 엔더 드래곤 등)$(li)길들인 동물$(li)바닐라 생성기가 생성한 몹$(p)그 밖에 "
        "개체 ID(예: $(thing)minecraft:zombie/$)를 "
        "$(thing)pneumaticcraft:vacuum_trap_blacklisted/$ 개체 유형 태그에 추가해 포획 "
        "대상에서 제외할 수 있습니다."
    ),
    ("entries/spawning/vacuum_trap.json", 5): "기억의 정수",
    ("entries/spawning/vacuum_trap.json", 6): (
        "진공 덫 탱크에 $(l:base_concepts/memory_essence)기억의 정수/$가 100mB 이상 있으면 "
        "몹 흡수 효율이 크게 높아집니다. 포획한 몹 하나가 설치한 "
        "$(thing)생성기 코어/$의 정수를 1% 대신 2~4% 채우므로, 코어 하나를 채우는 데 "
        "몹 100마리 대신 25~50마리만 필요합니다. 몹을 포획할 때마다 기억의 정수 100mB를 "
        "사용합니다."
    ),
    ("entries/programming/jump.json", 1): (
        "이 위젯은 $(l:programming/flow_control)프로그램 흐름/$만 제어합니다. 프로그램이 "
        "$(thing)점프/$ 위젯에 도달하면 연결된 $(l:programming/text)텍스트/$ 위젯을 읽고, "
        "이름이 같은 $(l:programming/label)레이블/$ 위젯으로 이동하려고 합니다. 어떤 이유로든 "
        "실패하면 $(l:programming/start)시작/$ 위젯으로 돌아갑니다. 일반적으로 이 대체 "
        "동작이 일어날 일은 없습니다."
    ),
    ("entries/programming/jump.json", 2): (
        "$(thing)점프/$ 위젯은 같은 $(l:programming/label)레이블/$로 이동하는 점프를 둘 "
        "이상 사용해 프로그램 흐름의 여러 $(italic)분기/$를 합치거나, 구역을 각각의 "
        "‘서브루틴’으로 나눠 프로그램을 정리할 때 사용할 수 있습니다. "
        "$(l:programming/programmer)프로그래머/$ GUI 왼쪽 아래의 $(bold)흐름 표시/$를 "
        "선택하면 같은 이름을 가진 $(thing)점프/조건/레이블/$ 위젯을 잇는 선이 표시됩니다."
    ),
    ("entries/programming/puzzle_pieces.json", 1): (
        "$(thing)프로그래밍 퍼즐/$ 또는 $(thing)퍼즐 조각/$은 "
        "$(l:programming/programmer)프로그래머/$로 $(l:tools/drone)드론/$을 프로그래밍할 때 "
        "사용하는 실제 아이템입니다. 드론을 프로그래밍하면 소모되지만, 더 작거나 빈 "
        "프로그램으로 $(item)드론/$을 덮어쓰면 남는 조각을 돌려받습니다.$(p)"
        "$(item)프로그래머/$ GUI에 표시되는 $(thing)퍼즐 조각/$의 가상 형태를 "
        "$(thing)프로그래밍 위젯/$이라고 합니다."
    ),
    ("entries/programming/puzzle_pieces.json", 2): (
        "$(l:tools/drone)드론/$에 프로그램을 기록하려면 $(thing)퍼즐 조각/$을 인벤토리에 "
        "가지고 있거나 $(item)프로그래머/$의 어느 면에든 인접한 인벤토리에 넣어야 합니다."
        "$(p)크리에이티브 모드에서는 퍼즐 조각 없이 무료로 프로그래밍할 수 있습니다."
    ),
    ("entries/programming/condition_coordinate.json", 1): (
        "이것은 $(l:programming/conditions)조건/$ 위젯입니다.$(p)"
        "$(thing)조건: 좌표/$ 위젯은 두 $(l:programming/coordinate)좌표/$를 비교합니다. "
        "좌표의 각 축(X/Y/Z)에 여러 검사를 적용할 수 있으며, 두 좌표에서 축 하나나 둘 또는 "
        "세 축 모두가 일치하는지 확인할 수 있습니다."
    ),
    ("entries/base_concepts/oil.json", 1): (
        "$(pncr)의 월드에 자연 생성되는 것은 $(thing)원유/$뿐입니다. 물 호수와 비슷하게 "
        "생성되지만 지표보다 깊은 지하에서 발견될 가능성이 훨씬 큽니다. 따라서 "
        "$(l:tools/seismic_sensor)지진 센서/$ 같은 탐사 도구를 사용하기를 권장합니다."
    ),
    ("entries/base_concepts/oil.json", 2): (
        "원유는 두 가지 용도로 사용합니다. $(l:compressors/liquid_compressor)액체 압축기/$의 "
        "고품질 연료로 쓰도록 $(l:manufacturing/refinery)정제/$하거나, "
        "$(l:components/plastic)플라스틱/$과 $(l:components/lubricant)윤활유/$를 만듭니다."
        "$(p)$(item)플라스틱/$은 $(pncr)의 여러 제작법에 쓰이고, $(item)윤활유/$는 "
        "$(l:base_concepts/upgrades#speed)속도 업그레이드/$를 만드는 데 필요합니다."
    ),
    ("entries/base_concepts/oil.json", 3): (
        "원유를 찾았다면 추출하고 운반해야 합니다. $(pncr)에서는 "
        "$(l:machines/gas_lift)가스 리프트/$를 권장하지만 다른 모드의 유체 펌프도 사용할 "
        "수 있습니다. 기지에서 먼 곳의 원유를 게임 초반에 운반할 때는 "
        "$(l:machines/tanks)소형 탱크/$가 유용합니다. 유체를 32,000mB까지 담고 부숴도 "
        "내용물을 보존합니다. 가스 리프트도 유체를 보존하므로 같은 용도로 쓸 수 있습니다."
    ),
    ("entries/tubes/tube_modules.json", 1): (
        "$(thing)튜브 모듈/$은 $(l:tubes/pressure_tubes)압력 튜브/$의 옆면에 부착하거나 "
        "튜브와 $(thing)인라인/$으로 연결하는 부품입니다.$(p)부착한 모듈은 "
        "$(l:tools/pneumatic_wrench)공압 렌치/$로 $(thing)Shift+우클릭/$해 제거할 수 "
        "있습니다."
    ),
    ("entries/machines/security_station.json", 4): (
        "$(thing)보안 스테이션/$을 설정하려면 네트워크 격자에 "
        "$(l:components/network_components)네트워크 부품/$을 놓아 $(thing)네트워크/$를 "
        "만드세요. 네트워크마다 $(l:components/network_components#diagnostic)진단 서브루틴/$, "
        "$(l:components/network_components#io_port)네트워크 IO 포트/$, "
        "$(l:components/network_components#registry)네트워크 레지스트리/$가 하나씩 필요합니다."
        "$(p)이 세 특수 노드는 모두 $(l:components/network_components#node)네트워크 노드/$로 "
        "서로 연결해야 합니다."
    ),
    ("entries/machines/security_station.json", 13): (
        "$(thing)보안 스테이션/$에는 다음 업그레이드를 사용할 수 있습니다:$(li)"
        "$(l:base_concepts/upgrades#entity_tracker)개체 추적기/$는 "
        "$(l:machines/security_station#hacking)해커/$가 감지될 확률을 높입니다. 추가할수록 "
        "효과가 줄며 노드 해킹 시도 한 번당 최대 보호 확률은 99%입니다.$(li)"
        "$(l:base_concepts/upgrades#range)범위 업그레이드/$는 개당 보호 범위를 1블록씩 늘려 "
        "모든 방향으로 최대 16블록, 즉 최대 33x33x33 영역을 보호합니다."
    ),
    ("entries/machines/security_station.json", 19): (
        "누군가 $(thing)보안 스테이션/$을 해킹하면 $(bold)문제/$와 $(bold)상태/$ 탭에서 "
        "확인할 수 있고, 시스템을 해킹한 사람이 $(italic)누구인지/$도 표시됩니다. 이제 그 "
        "플레이어만 영역 안의 블록과 상호작용할 수 있습니다. 보안을 복구하려면 GUI의 "
        "$(bold)재부팅/$ 버튼으로 $(thing)보안 스테이션/$을 $(italic)재부팅/$하세요. "
        "재부팅에는 60초가 걸리며, 그동안 영역은 전혀 보호되지 않습니다."
    ),
    ("entries/machines/security_station.json", 21): (
        "다른 플레이어의 $(thing)보안 스테이션/$을 해킹하려면 하나 이상, 보통은 여러 "
        "$(l:base_concepts/upgrades#security)보안 업그레이드/$를 설치한 "
        "$(l:armor/pneumatic_helmet)공압 헬멧/$이 필요합니다. 그러면 맞은편 그림과 비슷한 "
        "GUI가 나타납니다. 해킹 방법은 $(l:https://www.youtube.com/watch?v=Lgmpslbrrwo)이 "
        "오래됐지만 여전히 유효한 영상/$을 참고하세요.$(p)노드를 $(thing)좌클릭/$하면 "
        "점령하고, 점령한 노드를 $(thing)우클릭/$하면 요새화합니다. 요새화한 노드는 진단 "
        "서브루틴이 점령하는 데 조금 더 오래 걸립니다."
    ),
    ("entries/machines/security_station.json", 23): (
        "$(li)$(thing)보안 스테이션/$을 잘 숨기고 보호하세요.$(li)여러 "
        "$(thing)보안 스테이션/$으로 한 영역을 보호하면 공격자는 모두 해킹해야 합니다."
        "$(li)전투 프로그램을 설치한 $(l:tools/drone)드론/$이나 "
        "$(l:machines/sentry_turret)감시 포탑/$ 같은 능동 방어 수단을 고려하세요.$(li)해킹된 "
        "$(thing)보안 스테이션/$이 $(#f00)레드스톤 신호/$를 내보내도록 설정해 추가 방어 "
        "수단을 작동시킬 수도 있습니다. 예를 들면 스테이션 아래의 TNT가 있겠죠."
    ),
    ("entries/tubes/regulator_module.json", 1): (
        "조절기 모듈은 튜브를 통과할 수 있는 $(l:base_concepts/pressure)압력/$을 제한하는 "
        "$(l:tubes/tube_modules#inline)인라인/$ 모듈입니다. 기본 상태에서는 튜브 등급과 "
        "관계없이 레드스톤 신호 0에서 4.9bar로 제한하며, 신호가 15에 가까워질수록 제한값은 "
        "0에 가까워집니다. 따라서 바로 옆의 레버를 켜면 조절기가 닫혀 공기 흐름을 막습니다."
    ),
    ("entries/tubes/regulator_module.json", 2): (
        "조절기의 좁은 쪽이 설정 압력에 도달하면 공기가 더 이상 통과하지 않습니다. 이 "
        "원리를 $(thing)변압기/$처럼 사용할 수 있습니다. 넓은 입력 쪽에는 고압 공기가 "
        "들어오지만 조절기 튜브가 출력 압력을 임계값으로 제한합니다.$(p)따라서 상위 등급 "
        "네트워크에서 하위 등급 튜브 네트워크로 공기를 안전하게 공급할 수 있습니다."
    ),
    ("entries/tubes/air_grate_module.json", 1): (
        "이 모듈은 개체를 끌어당기거나 밀어냅니다. $(l:base_concepts/pressure)양압/$에서는 "
        "개체를 밀어내고 $(thing)음압/$에서는 끌어당깁니다. 음압은 "
        "$(l:machines/vacuum_pump)진공 펌프/$로 만듭니다. 아이템 개체가 충분히 가까워지면 "
        "화로처럼 면별 입출력이 있는 인벤토리 규칙을 지키면서 인접한 인벤토리에 자동으로 "
        "들어갑니다."
    ),
    ("entries/tubes/air_grate_module.json", 2): (
        "모듈 범위는 다음 공식으로 계산합니다:$(p)양압:$(p)  "
        "$(#272)범위 = 4 × 압력(bar)/$$(p)음압:$(p)  "
        "$(#272)범위 = -16 × 압력(bar)/$$(p)예를 들어 2bar에서는 4 × 2 = 8블록까지 "
        "밀어내고, -0.5bar에서는 -16 × -0.5 = 8블록까지 끌어당깁니다."
    ),
    ("entries/tubes/air_grate_module.json", 3): (
        "에어 그레이트는 향하는 방향의 정육면체 영역에 있는 개체에만 영향을 주며, 개체를 "
        "직접 볼 수 있어야 합니다.$(p)모듈을 우클릭하면 영향 범위가 몇 초 동안 표시됩니다."
    ),
    ("entries/tubes/air_grate_module.json", 5): (
        "에어 그레이트 모듈은 $(l:machines/heat_sink)방열판/$을 능동 냉각할 수도 있습니다. "
        "모듈 앞 3x3x3 범위의 방열판을 냉각하며, 모듈을 설치하면 이 범위가 표시됩니다."
        "$(p)범위가 3블록 이상, 즉 압력이 0.75bar 이상일 때만 방열판을 냉각합니다."
    ),
    ("entries/renewables/glycerol.json", 5): (
        "$(thing)글리세롤/$은 $(thing)판자/$ 4개나 $(thing)석탄/$ 반 개와 같은 열량을 "
        "내는 쓸 만한 연료입니다."
    ),
    ("entries/tools/gps_tool.json", 1): (
        "$(item)GPS 도구/$로 블록을 $(thing)우클릭/$하면 그 블록의 좌표를 저장합니다. 이 "
        "정보는 $(pncr)의 여러 기능에서 사용합니다. 다음 페이지를 참고하세요.$(p)공중에서 "
        "$(item)GPS 도구/$를 $(thing)우클릭/$하면 좌표를 직접 조정하는 GUI가 열립니다."
        "$(p)웅크린 채 마우스 휠을 돌리면 플레이어가 바라보는 축을 따라 좌표를 빠르게 "
        "조정합니다."
    ),
    ("entries/tools/remote.json", 1): (
        "리모컨으로 $(l:programming/variables#global)전역 변수/$를 조작하는 전용 GUI를 "
        "만들어 $(l:tools/drone)드론/$이나 $(l:machines/universal_sensor)범용 센서/$를 "
        "원격 제어할 수 있습니다. $(item)범용 센서/$와 $(item)리모컨/$을 함께 사용하면 "
        "무선 레드스톤도 만들 수 있습니다!$(p)$(item)리모컨/$을 "
        "$(thing)Shift+우클릭/$하면 GUI 편집기가 열립니다."
    ),
    ("entries/components/reinforced_air_canister.json", 1): (
        "$(l:components/air_canister)공기 용기/$처럼 $(thing)강화 공기 용기/$도 공기를 "
        "저장하며 $(l:machines/charging_station)충전소/$에서 충전하거나 방출할 수 있습니다. "
        "다만 용량이 6000mL로 더 크고 20bar까지 안전하게 충전할 수 있습니다."
    ),
    ("entries/components/reinforced_air_canister.json", 2): (
        "$(thing)강화 공기 용기/$는 상자 같은 인벤토리와, "
        "$(l:tubes/charging_module)충전 모듈/$을 부착한 "
        "$(l:tubes/pressure_tubes)압력 튜브/$를 조합해 대량 공기 저장 장치로 사용할 수 "
        "있습니다. $(l:machines/aerial_interface)공중 인터페이스/$와 바닐라 "
        "$(thing)엔더 상자/$를 함께 사용하면 활용 범위가 더 넓어집니다."
    ),
    ("entries/machines/kerosene_lamp.json", 3): (
        "$(item)등유 램프/$는 대부분의 $(pncr) 블록처럼 $(thing)레드스톤/$으로 제어할 수 "
        "있습니다. 일반적인 켜기/끄기 모드 외에 $(bold)신호 보간/$ 모드가 있으며, 신호 "
        "세기에 따라 램프 범위를 비례 조절합니다.$(p)예를 들어 기본 최대 범위가 10블록일 "
        "때 $(#f00)레드스톤 신호/$ 8(최대 15)을 주면 범위는 5블록입니다."
    ),
    ("entries/logistics/frames.json", 1): (
        "$(thing)물류 프레임/$은 인벤토리나 탱크에 부착해 "
        "$(thing)물류 시스템/$의 일부로 지정하는 장치입니다.$(p)설치한 프레임은 "
        "$(l:tools/logistics_configurator)물류 설정기/$로 $(thing)우클릭/$해 설정하고, "
        "설정기로 $(thing)Shift+우클릭/$해 제거합니다. 아이템 상태의 프레임을 우클릭해 "
        "미리 설정할 수도 있습니다."
    ),
    ("entries/tools/harvesting_drone.json", 5): (
        "$(item)괭이/$ 하나만 든 인벤토리에 $(item)수확 드론/$을 "
        "$(thing)Shift+우클릭/$해 배치하면 그 괭이로 작물을 자동으로 다시 심습니다. 이 "
        "방식으로 배치한 드론은 괭이를 장착하지 않으면 작업하지 않습니다. 다시 심을 필요가 "
        "없다면 다른 블록에 드론을 배치하세요."
    ),
    ("entries/tools/remote.json", 14): (
        "편집기 GUI 왼쪽의 $(thing)Pastebin/$ 버튼으로 "
        "$(l:https://pastebin.com/4yxKG5Jc)이 레이아웃/$을 가져오세요.$(p)전역 변수 "
        "$(thing)signal1, signal2, signal3/$을 설정하는 확인란 세 개가 추가됩니다.$(p)"
        "$(l:machines/universal_sensor)범용 센서/$ 세 개를 놓고 압력을 공급하세요. 각 "
        "$(item)센서/$에 $(l:base_concepts/upgrades#dispenser)발사기 업그레이드/$를 넣고, 각 "
        "$(item)센서/$에서 레드스톤 선을 연결하세요. 선이 섞이지 않도록 센서를 한 블록씩 "
        "떨어뜨려 놓으세요."
    ),
    ("entries/tools/remote.json", 16): (
        "각 $(item)센서/$ GUI에서 다음과 같이 설정하세요:$(li)$(thing)발사기/$ 버튼 선택"
        "$(li)$(thing)월드/$ 선택$(li)$(thing)전역 변수/$ 선택$(li)$(thing)변수 이름/$ "
        "입력란에 각각 'signal1', 'signal2', 'signal3' 입력$(p)이제 $(item)리모컨/$을 "
        "$(thing)우클릭/$하고 각 확인란을 켜고 꺼 보세요. 해당 $(item)센서/$가 알맞게 "
        "레드스톤 신호를 출력합니다. 무선 레드스톤 완성입니다!"
    ),
    ("entries/base_concepts/cc_oc_integration.json", 1): (
        "$(thing)ComputerCraft/$나 $(thing)Open Computers/$가 설치되어 있으면 거의 모든 "
        "$(pncr) 기계와 $(l:machines/drone_interface)드론/$을 제어할 수 있습니다.$(p)이 "
        "페이지에 나오는 기계는 모두 CC/OC 주변 장치로 연결할 수 있습니다."
    ),
    ("entries/base_concepts/cc_oc_integration.json", 5): (
        "컴퓨터와 $(pnc) 기계는 $(item)어댑터/$로 연결해야 합니다. 그러면 OC 부품으로 "
        "인식되며 OC Lua 환경에서 $(thing)=components.list()/$를 실행해 확인할 수 "
        "있습니다. 이후 다음 함수를 사용할 수 있습니다. 예를 들어 "
        "$(thing)p = components.air_compressor.getPressure()/$는 연결된 "
        "$(item)공기 압축기/$의 현재 압력을 가져옵니다."
    ),
    ("entries/base_concepts/cc_oc_integration.json", 7): (
        "다음 메서드는 $(italic)모든/$ $(pncr) 기계에 공통입니다:$(li)"
        "$(#800)getPressure(), getPressure(<side>)/$: 기계의 압력을 가져옵니다. <side>는 "
        "선택 사항이며, 면마다 압력이 다른 $(l:machines/vacuum_pump)진공 펌프/$에서만 "
        "필요합니다.$(li)$(#800)getDangerPressure()/$: 기계가 폭발할 위험이 생기는 압력을 "
        "가져옵니다.$(li)$(#800)getCriticalPressure()/$: 기계가 반드시 폭발하는 절대 최대 "
        "압력을 가져옵니다."
    ),
    ("entries/base_concepts/cc_oc_integration.json", 9): (
        "다음 메서드는 $(l:base_concepts/heat)열/$을 지원하는 $(italic)모든/$ $(pncr) "
        "기계에 공통입니다:$(li)$(#800)getTemperature(), getTemperature(<side>)/$: 기계의 "
        "온도를 가져옵니다. <side>는 선택 사항이며 면마다 온도가 다른 "
        "$(l:machines/vortex_tube)볼텍스 튜브/$에서만 필요합니다."
    ),
    ("entries/base_concepts/cc_oc_integration.json", 10): (
        "$(li)$(#800)setExternalControl(<true/false>)/$: true이면 GPS 도구 삽입이나 범위 "
        "업그레이드 변경 같은 일반적인 방법으로 대포가 회전하지 못하게 합니다.$(li)"
        "$(#800)setTargetLocation(<x>,<y>,<z>)/$: GPS 도구에 저장한 위치 대신 지정한 "
        "좌표를 향하도록 대포를 조준합니다."
    ),
    ("entries/base_concepts/cc_oc_integration.json", 23): (
        "$(li)$(#800)setSensor(<sensorName>), setSensor(<index>), setSensor()/$: 현재 센서를 "
        "선택합니다. <sensorName>은 $(#800)getSensorNames()/$가 반환한 이름 중 하나이고, "
        "<index>는 $(#800)getSensorNames()/$가 반환한 테이블의 인덱스입니다. 인수 없이 "
        "$(#800)setSensor()/$를 "
        "호출하면 센서를 선택하지 않아 기계가 대기 상태로 들어가고 공기를 사용하지 "
        "않습니다. 현재 설치된 업그레이드로 해당 센서를 사용할 수 있으면 true를 반환합니다. "
    ),
    ("entries/components/plastic.json", 1): (
        "$(item)플라스틱/$은 $(pncr)의 중요한 제작 재료입니다.$(p)"
        "$(item)용융 플라스틱/$은 $(l:manufacturing/thermopneumatic_processing_plant)열공압 "
        "처리 공장/$에서 $(l:manufacturing/refinery)LPG/$와 $(item)석탄/$, 또는 "
        "$(l:renewables/biodiesel)바이오디젤/$과 $(item)숯/$으로 만듭니다."
    ),
    ("entries/armor/pneumatic_boots.json", 3): (
        "남은 압력 말고는 아무 걱정 없이 하늘을 날고 싶다면 "
        "$(l:base_concepts/upgrades#jet_boots_1)제트 부츠 업그레이드/$를 사용하세요. 총 "
        "5등급이 있으며 등급이 높을수록 비행 속도와 공기 소모량이 함께 늘어납니다."
    ),
    ("entries/armor/pneumatic_boots.json", 7): (
        "$(l:base_concepts/upgrades#jet_boots_3)제트 부츠 업그레이드 III등급/$ 이상이면 "
        "$(thing)건축가 모드/$를 사용할 수 있습니다. 크리에이티브 모드와 비슷하지만 더 "
        "느린 비행 조작과 향상된 공중 채굴 속도를 제공합니다.$(p)방어구 GUI에서 켜고 끌 수 "
        "있으며 전환 키도 지정할 수 있습니다."
    ),
    ("entries/machines/aerial_interface.json", 1): (
        "$(item)공중 인터페이스/$는 플레이어 인벤토리에 직접 연결하는 강력한 장치입니다. "
        "충분히 $(l:base_concepts/pressure)가압/$되면 다른 인벤토리처럼 상호작용할 수 "
        "있습니다. 아이템은 인터페이스에 머물지 않고 소유한 플레이어에게 "
        "$(italic)직접/$ 전달됩니다. 예를 들어 "
        "$(l:logistics/frames#requester)물류 요청자 프레임/$을 부착해 횃불 64개를 항상 "
        "보충할 수 있습니다."
    ),
    ("entries/machines/drone_interface.json", 43): (
        "$(#800)getAction()/$$(p)$(#800)setAction()/$으로 마지막에 설정한 작업을 문자열로 "
        "반환합니다. 설정한 작업이 없으면 $(thing)nil/$을 반환합니다. 이 메서드가 nil을 "
        "반환하지 않을 때만 $(#800)isActionDone()/$을 호출하도록 확인할 때 사용할 수 "
        "있습니다."
    ),
    ("entries/machines/drone_interface.json", 46): (
        "$(#800)getAllActions()/$$(p)현재 선택할 수 있는 모든 작업의 테이블을 반환합니다. "
        "예: $(thing)pneumaticcraft:dig/$ 또는 $(thing)pneumaticcraft:place'/$. 각 작업은 "
        "$(l:programming/programmer#ids)프로그래머/$ GUI의 프로그래밍 위젯과 직접 "
        "대응합니다.$(p)기본 작업처럼 $(thing)pneumaticcraft:/$로 시작하는 작업은 "
        "$(thing)pneumaticcraft:/$ 접두사를 생략할 수 있습니다."
    ),
    ("entries/machines/drone_interface.json", 60): (
        "$(#800)isActionDone()/$$(p)현재 작업이 끝났으면 true를 반환합니다. 예를 들어 "
        "'goto'가 목적지에 도착했거나, 'inventory import'가 더 가져올 수 없거나, 'dig'가 "
        "가능한 모든 블록을 팠을 때입니다."
    ),
    ("entries/machines/drone_interface.json", 62): (
        "$(#800)isConnectedToDrone()/$$(p)드론 프로그램이 ComputerCraft 조각에 도달해 "
        "연결을 맺는 등, 드론이 이 드론 인터페이스에 연결되어 있으면 true를 반환합니다."
    ),
    ("entries/machines/security_station.json", 6): (
        "이 서버에서는 설정으로 보안 스테이션 해킹이 비활성화되어 있습니다. 설치한 보안 "
        "스테이션을 다른 플레이어가 해킹할 수는 없지만, 이전 페이지의 올바른 부품으로 "
        "설정해야 합니다. 이후 페이지 중 $(thing)친구 허용/$을 제외한 대부분의 해킹 "
        "설명은 적용되지 않습니다."
    ),
    ("entries/machines/security_station.json", 11): (
        "해커에게 유용하지만 제작할 수 없어 주민 거래나 던전 전리품으로 찾아야 하는 "
        "아이템이 두 가지 있습니다:$(li)$(l:components/nuke_virus)핵 바이러스/$: 노드 하나를 "
        "즉시 점령합니다.$(li)$(l:components/stop_worm)STOP! 웜/$: 진단 서브루틴의 추적 "
        "진행을 잠시 멈춥니다."
    ),
    ("entries/logistics/frames.json", 2): (
        "다음 프레임 속성을 설정할 수 있습니다:$(li)모든 프레임은 $(thing)필터링/$으로 "
        "제공하거나 받을 아이템과 유체를 제한합니다. "
        "$(l:tools/tag_filter)태그 필터/$도 참고하세요.$(li)$(thing)필터/$ 측면 탭에서 "
        "$(thing)아이템 NBT/$ 또는 $(thing)모드 ID/$ 일치 여부와 화이트리스트(기본값) 또는 "
        "블랙리스트 적용 여부를 정할 수 있습니다."
    ),
    ("entries/base_concepts/pressure.json", 5): (
        "$(li)많은 기계에 $(thing)최소 압력/$이 필요하지만 실제 작업은 $(thing)압력/$이 "
        "아니라 $(thing)공기/$를 소모합니다. 압력은 저장한 공기량과 부피에 따라 결정되는 "
        "값이라는 점을 기억하세요."
    ),
    ("entries/machines/tanks.json", 1): (
        "유체 저장 탱크는 $(item)소형 탱크/$, $(item)중형 탱크/$, $(item)대형 탱크/$, "
        "$(item)거대 탱크/$의 네 종류입니다. $(l:machines/liquid_hopper)유체 호퍼/$도 유체를 "
        "저장하지만, 탱크는 더 조밀한 저장 공간과 유용한 쌓기 기능을 제공하며 유체를 "
        "자동으로 옮기지 않습니다. 다만 $(l:base_concepts/upgrades#dispenser)발사기 "
        "업그레이드/$를 설치하면 유체를 밀어낼 수 있습니다."
    ),
    ("entries/programming/programmer.json", 9): (
        "$(bold)7. 기타 버튼/$$(p)GUI 왼쪽 가장자리의 버튼은 순서대로 다음 기능을 "
        "제공합니다:$(li)$(thing)실행 취소/$: 최근 작업 최대 20개 취소$(li)$(thing)다시 "
        "실행/$: 마지막 실행 취소 복원$(li)$(thing)가져오기/내보내기/$: 프로그램을 JSON "
        "파일로 $(l:https://pastebin.com)pastebin.com/$과 주고받기(Pastebin 로그인은 선택)"
        "$(li)$(thing)삭제/$: 전체 프로그램 삭제(실행 취소 가능)$(li)$(thing)변환/$: "
        "프로그램을 $(thing)상대/$ 좌표로 변환(자세한 내용은 "
        "$(l:programming/programmer#convert_relative)이 페이지/$ 참고)"
    ),
}

GUIDE_OVERRIDES = {
    "This is a crafting component for other devices. It has no use on its own.": (
        "다른 장치를 제작하는 데 쓰는 부품이며, 단독으로는 기능이 없습니다."
    ),
    (
        "$(#800)addBlacklistLiquidFilter(<liquid name>)/$$(p)Like the "
        "addWhitelistLiquidFilter(...), but to blacklist liquids."
    ): (
        "$(#800)addBlacklistLiquidFilter(<liquid name>)/$$(p)"
        "addWhitelistLiquidFilter(...)와 비슷하지만 유체를 블랙리스트에 등록합니다."
    ),
    (
        "$(thing)Bandages/$ can be used to quickly heal 3 hearts of health. Quickly is "
        "not instantaneous, though; you will need to right-click and hold for 2 seconds "
        "to apply a bandage, and there is an 8-second cooldown between uses."
    ): (
        "$(thing)반창고/$를 사용하면 하트 3칸의 체력을 빠르게 회복할 수 있습니다. "
        "즉시 회복되는 것은 아니며, 우클릭을 2초 동안 눌러 반창고를 사용해야 합니다. "
        "사용 후에는 8초의 재사용 대기시간이 적용됩니다."
    ),
    (
        "A Seismic Sensor can have two results:$(p)$(#008)  No Oil found./$$(p)"
        "No Oil is found right under this block. Keep looking.$(p)$(#008)  Found Oil "
        "<distance>m below. It contains about <amount> buckets of Oil./$$(p)Oil is found! "
        "The clicked block would be a suitable place to put a "
        "$(l:machines/gas_lift)Gas Lift/$ to pump the Oil out."
    ): (
        "지진 센서의 결과는 두 가지입니다:$(p)$(#008)원유를 찾지 못했습니다./$$(p)"
        "이 블록 바로 아래에는 원유가 없습니다. 다른 곳을 찾아보세요.$(p)$(#008)"
        "아래 <distance>m에서 원유를 찾았습니다. 약 <amount>양동이의 원유가 있습니다./$"
        "$(p)원유를 찾았습니다! 클릭한 블록은 원유를 퍼 올릴 "
        "$(l:machines/gas_lift)가스 리프트/$를 설치하기에 적합한 장소입니다."
    ),
    (
        "Output mode $(item)Interfaces/$ will auto-eject into an adjacent inventory; "
        "this may or may not include other mods' pipes, depending on whether or not they "
        "look like an inventory to the interface.$(p)It costs 1000mL of "
        "$(l:base_concepts/pressure)air/$ per item transferred. This means, to transfer "
        "a full stack, the $(item)Interface/$ needs 64000mL (4 bar for a basic 3x3x3 "
        "chamber). If the Interface seems to get 'stuck', it's just waiting for more "
        "pressure to build up."
    ): (
        "출력 모드 $(item)인터페이스/$는 인접한 인벤토리로 아이템을 자동 배출합니다. "
        "다른 모드의 파이프가 인터페이스에 인벤토리로 인식되는지에 따라 해당 파이프로도 "
        "배출될 수 있습니다.$(p)아이템 하나를 옮길 때마다 1000mL의 "
        "$(l:base_concepts/pressure)공기/$를 사용합니다. 한 스택 전체를 옮기려면 "
        "$(item)인터페이스/$에 64000mL가 필요합니다(기본 3x3x3 챔버 기준 4bar). "
        "인터페이스가 멈춘 것처럼 보이면 압력이 더 쌓이기를 기다리는 중입니다."
    ),
    (
        "$(italic)A Redstone Condition widget which kills the drone if the signal >= "
        "10/$"
    ): "$(italic)신호가 10 이상이면 드론을 파괴하는 레드스톤 조건 위젯/$",
    (
        "$(italic)<10 bar = 0 redstone, >20 bar = 15 redstone, 10-20 bar = "
        "interpolate (e.g. 12 bar = 3 redstone)/$"
    ): (
        "$(italic)10bar 미만 = 레드스톤 0, 20bar 초과 = 레드스톤 15, "
        "10~20bar = 보간(예: 12bar = 레드스톤 3)/$"
    ),
    (
        "$(italic)<0°C = 0 redstone, >1000°C = 15 redstone, 0-1000°C = "
        "interpolate (e.g. 200°C = 3 redstone)/$"
    ): (
        "$(italic)0°C 미만 = 레드스톤 0, 1000°C 초과 = 레드스톤 15, "
        "0~1000°C = 보간(예: 200°C = 레드스톤 3)/$"
    ),
    (
        "$(#800)addArea(<x1>,<y1>,<z1>)/$$(p)$(#800)addArea(<x1>,<y1>,<z1>,"
        "<x2>,<y2>,<z2>,<areaType>)/$$(p)Adds an area to the current stored area of "
        "the Drone. When using the latter method, x1/y1/z1 represent the first point "
        "(which would be P1 of an $(l:tools/gps_area_tool)GPS Area Tool/$), and "
        "x2/y2/z2 represent the second point, or P2 of the GPS Area Tool.$(p)"
        "getAreaTypes() can be used to list the valid area types."
    ): (
        "$(#800)addArea(<x1>,<y1>,<z1>)/$$(p)$(#800)addArea(<x1>,<y1>,<z1>,"
        "<x2>,<y2>,<z2>,<areaType>)/$$(p)드론에 현재 저장된 영역에 새 영역을 "
        "추가합니다. 두 번째 형식에서 x1/y1/z1은 첫 번째 지점($(l:tools/gps_area_tool)"
        "GPS 영역 도구/$의 P1)을, x2/y2/z2는 두 번째 지점인 P2를 나타냅니다.$(p)"
        "getAreaTypes()를 사용하면 유효한 영역 유형을 확인할 수 있습니다."
    ),
    (
        "All produced liquids can be used as fuel in a "
        "$(l:compressors/liquid_compressor)Liquid Compressor/$ (with lighter fuels "
        "being of better quality).$(p)However, there are two other very important uses:"
        "$(li)$(thing)LPG/$ is used to make liquid $(l:components/plastic)Plastic/$"
        "$(li)$(thing)Diesel/$ is used to make $(l:components/lubricant)Lubricant/$ "
        "for $(l:base_concepts/upgrades#speed)Speed Upgrades/$.$(p)A "
        "$(l:manufacturing/thermopneumatic_processing_plant)Thermopneumatic Processing "
        "Plant/$ is used for both of these processes."
    ): (
        "생산된 모든 액체는 $(l:compressors/liquid_compressor)액체 압축기/$의 연료로 "
        "사용할 수 있으며, 가벼운 연료일수록 품질이 좋습니다.$(p)그 밖에도 중요한 용도가 "
        "두 가지 있습니다:$(li)$(thing)LPG/$는 액체 $(l:components/plastic)플라스틱/$을 "
        "만드는 데 사용합니다$(li)$(thing)디젤/$은 $(l:base_concepts/upgrades#speed)속도 "
        "업그레이드/$용 $(l:components/lubricant)윤활유/$를 만드는 데 사용합니다.$(p)"
        "두 과정 모두 $(l:manufacturing/thermopneumatic_processing_plant)열공압 처리 공장/$을 "
        "사용합니다."
    ),
    (
        "Now drag that $(l:programming/start)Start/$ widget onto the main programming "
        "area. It will appear with a $(4)red border/$, indicating a problem: mouse over "
        "to see what.$(p)Right, there's no widget connected underneath - we will remedy "
        "that now by creating our program.$(p)Find an "
        "$(l:programming/inventory_import)Import From Inventory/$ widget and drag it to "
        "right below the $(thing)Start/$ widget."
    ): (
        "이제 $(l:programming/start)시작/$ 위젯을 주 프로그래밍 영역으로 끌어오세요. "
        "문제가 있음을 나타내는 $(4)빨간 테두리/$가 표시됩니다. 마우스를 올리면 원인을 "
        "볼 수 있습니다.$(p)아래에 연결된 위젯이 없기 때문입니다. 이제 프로그램을 만들어 "
        "해결하겠습니다.$(p)$(l:programming/inventory_import)인벤토리에서 가져오기/$ "
        "위젯을 찾아 $(thing)시작/$ 위젯 바로 아래로 끌어오세요."
    ),
    (
        "The $(item)Assembly Drill/$ is one of the $(thing)Assembly Machines/$ which do "
        "the actual work. Its diamond drillhead is able to drill through the toughest "
        "materials.$(p)The $(item)Assembly Drill/$ can $(italic)not/$ reach diagonally, "
        "so it must be located directly adjacent to an $(thing)Assembly Platform/$."
    ): (
        "$(item)조립 드릴/$은 실제 작업을 수행하는 $(thing)조립 기계/$ 중 하나입니다. "
        "다이아몬드 드릴 헤드로 매우 단단한 재료도 뚫을 수 있습니다.$(p)$(item)조립 "
        "드릴/$은 대각선에 $(italic)닿을 수 없으므로/$ $(thing)조립 플랫폼/$ 바로 옆에 "
        "배치해야 합니다."
    ),
    (
        "The $(item)Pneumatic Boots/$ is one of the four $(thing)Pneumatic Armor/$ "
        "pieces.$(p)The boots provide inbuilt fall protection at a modest air cost "
        "(proportional to the fall damage negated).$(p)You also get 1-block step assist "
        "for free (no air cost).  Note that this is step assist, not auto-jump, and it's "
        "a toggleable feature."
    ): (
        "$(item)공압 부츠/$는 네 부위로 구성된 $(thing)공압 방어구/$ 중 하나입니다.$(p)"
        "부츠에는 막아 준 낙하 피해에 비례해 소량의 공기를 사용하는 낙하 보호 기능이 "
        "내장되어 있습니다.$(p)공기 소모 없이 1블록 높이의 단차를 자동으로 오르는 기능도 "
        "제공합니다. 자동 점프가 아닌 단차 오르기 기능이며 켜고 끌 수 있습니다."
    ),
    (
        "There are a few differences, though:$(li)A $(item)Programmable Controller/$ "
        "uses a miniature version of a $(item)Drone/$ - a $(thing)minidrone/$. It's not "
        "a real entity, so no pathfinding is involved, and the $(thing)minidrone/$ can "
        "move through walls. This has the benefit of being more friendly to the server "
        "and more reliable in general.$(li)When executing a program, the "
        "$(item)Programmable Controller/$ will use air at a rate of 10mL/tick (whereas "
        "Drones only use 1mL/tick)."
    ): (
        "다만 몇 가지 차이가 있습니다:$(li)$(item)프로그래밍 가능 제어기/$는 "
        "$(item)드론/$의 소형 버전인 $(thing)미니드론/$을 사용합니다. 실제 개체가 아니어서 "
        "길 찾기를 하지 않고 $(thing)미니드론/$은 벽도 통과할 수 있으므로 서버 부담이 "
        "적고 더 안정적입니다."
        "$(li)프로그램을 실행할 때 $(item)프로그래밍 가능 제어기/$는 10mL/틱의 공기를 "
        "사용합니다(드론은 1mL/틱만 사용합니다)."
    ),
    (
        "When the upgrade is active, simply hold the "
        "$(k:pneumaticcraft.boots.jet_boots) key to thrust in the direction you're "
        "looking.$(p)$(thing)Jet Boots/$ are a $(bold)heavy/$ user of air; it's strongly "
        "recommended to add multiple $(l:base_concepts/upgrades#volume)Volume Upgrades/$ "
        "to your boots (and $(l:armor/pneumatic_chestplate)chestplate/$, with "
        "$(l:base_concepts/upgrades#charging)Charging Upgrades/$).$(p)Use of an "
        "$(l:machines/aerial_interface)Aerial Interface/$ is also advised when possible, "
        "along with a good charging infrastructure at your base."
    ): (
        "업그레이드가 활성화된 상태에서 $(k:pneumaticcraft.boots.jet_boots) 키를 누르면 "
        "바라보는 방향으로 추진합니다.$(p)$(thing)제트 부츠/$는 공기를 $(bold)매우 많이/$ "
        "사용하므로 부츠에 $(l:base_concepts/upgrades#volume)용량 업그레이드/$를 여러 개 "
        "설치하는 것이 좋습니다. $(l:base_concepts/upgrades#charging)충전 업그레이드/$를 "
        "설치한 $(l:armor/pneumatic_chestplate)흉갑/$에도 용량 업그레이드를 설치하세요.$(p)"
        "가능하면 기지에 충분한 충전 설비를 갖추고 $(l:machines/aerial_interface)공중 "
        "인터페이스/$를 사용하는 것도 좋습니다."
    ),
}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def installed_jar() -> Path:
    matches = sorted(
        (resolve_source_root() / "mods").glob("pneumaticcraft-repressurized-*.jar")
    )
    if len(matches) != 1:
        raise FileNotFoundError(f"PneumaticCraft JAR 개수 불일치: {matches}")
    return matches[0]


def visible_strings(value: object, path: tuple[str, ...] = ()) -> list[str]:
    """번역할 사용자 표시 문자열을 재귀적으로 수집한다."""
    rows: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (*path, key)
            if key in VISIBLE_FIELDS and isinstance(child, str):
                rows.append(child)
            else:
                rows.extend(visible_strings(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(visible_strings(child, (*path, str(index))))
    return rows


def advancement_display_report(data: object) -> tuple[int, int, list[str]]:
    """발전 과제 표시 컴포넌트의 번역 키와 literal 수를 센다."""
    if not isinstance(data, dict) or not isinstance(data.get("display"), dict):
        return 0, 0, []
    translated = 0
    literals: list[str] = []
    display = data["display"]
    for field in ("title", "description"):
        component = display.get(field)
        if isinstance(component, dict) and isinstance(component.get("translate"), str):
            translated += 1
        elif isinstance(component, str):
            literals.append(component)
        elif isinstance(component, dict) and isinstance(component.get("text"), str):
            literals.append(component["text"])
    return translated, len(literals), literals


def is_allowed_unchanged(value: str) -> bool:
    """공식 모드명, 작품명과 API 메서드 표기는 원문 유지를 허용한다."""
    return value in ALLOWED_UNCHANGED or bool(
        re.fullmatch(r"[a-z][A-Za-z]+\(\)", value)
    )


def patchouli_tag_signature(value: str) -> list[str]:
    """번역 가능한 툴팁 본문을 제외한 Patchouli 태그 서명을 반환한다."""
    return [
        "$(t:<translated>)" if tag.startswith("$(t:") else tag
        for tag in PATCHOULI_TAG.findall(value)
    ]


def extract() -> dict[str, object]:
    """현재 JAR의 영어 책 235개와 발전 과제 표시 경로를 추출한다."""
    jar = installed_jar()
    book_files = 0
    japanese_book_files = 0
    visible_values = 0
    advancement_files = 0
    translated_components = 0
    literal_components: list[str] = []
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            if name.startswith(BOOK_PREFIX) and name.endswith(".json"):
                relative = name.removeprefix(BOOK_PREFIX)
                data = json.loads(archive.read(name).decode("utf-8"))
                write_json(ENGLISH_ROOT / relative, data)
                write_json(KOREAN_ROOT / relative, data)
                book_files += 1
                if relative.startswith(TRANSLATABLE_PATH_PREFIXES):
                    visible_values += len(visible_strings(data))
            elif name.startswith(JAPANESE_BOOK_PREFIX) and name.endswith(".json"):
                relative = name.removeprefix(JAPANESE_BOOK_PREFIX)
                data = json.loads(archive.read(name).decode("utf-8"))
                write_json(JAPANESE_ROOT / relative, data)
                japanese_book_files += 1
            elif name.startswith(ADVANCEMENT_PREFIX) and name.endswith(".json"):
                data = json.loads(archive.read(name).decode("utf-8"))
                translated, literal_count, literals = advancement_display_report(data)
                advancement_files += 1
                translated_components += translated
                if literal_count:
                    literal_components.extend(f"{name}:{value}" for value in literals)
    if book_files != 235:
        raise ValueError(f"영어 Patchouli JSON 수 불일치: {book_files}")
    if japanese_book_files != 235:
        raise ValueError(f"일본어 Patchouli JSON 수 불일치: {japanese_book_files}")
    report = {
        "jar": jar.name,
        "book_json_files": book_files,
        "japanese_book_json_files": japanese_book_files,
        "translatable_visible_values": visible_values,
        "advancement_files": advancement_files,
        "advancement_translated_components": translated_components,
        "advancement_literal_components": literal_components,
    }
    write_json(WORK_ROOT / "scope.json", report)
    return report


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_unique_visible() -> set[str]:
    values: set[str] = set()
    for path in sorted(ENGLISH_ROOT.rglob("*.json")):
        relative = path.relative_to(ENGLISH_ROOT).as_posix()
        if relative.startswith(TRANSLATABLE_PATH_PREFIXES):
            values.update(visible_strings(load_json(path)))
    return values


def collect_visible_pairs(english: object, japanese: object) -> list[tuple[str, str]]:
    """동일한 JSON 위치의 영어·일본어 표시 문자열을 짝짓는다."""
    pairs: list[tuple[str, str]] = []
    if isinstance(english, dict) and isinstance(japanese, dict):
        if list(english) != list(japanese):
            raise ValueError("영어·일본어 가이드 객체 키 불일치")
        for key, english_child in english.items():
            japanese_child = japanese[key]
            if key in VISIBLE_FIELDS and isinstance(english_child, str):
                if not isinstance(japanese_child, str):
                    raise TypeError(f"일본어 표시 문자열 자료형 불일치: {key}")
                pairs.append((english_child, japanese_child))
            else:
                pairs.extend(collect_visible_pairs(english_child, japanese_child))
    elif isinstance(english, list) and isinstance(japanese, list):
        if len(english) != len(japanese):
            raise ValueError("영어·일본어 가이드 배열 길이 불일치")
        for english_child, japanese_child in zip(english, japanese, strict=True):
            pairs.extend(collect_visible_pairs(english_child, japanese_child))
    return pairs


def japanese_source_map() -> tuple[dict[str, str], set[str], list[str], int]:
    """영어 원문별 일본어 보조 원문과 충돌 목록을 만든다."""
    sources: dict[str, set[str]] = {}
    mismatched_files: list[str] = []
    tag_mismatches = 0
    english_files = sorted(ENGLISH_ROOT.rglob("*.json"))
    for english_path in english_files:
        relative = english_path.relative_to(ENGLISH_ROOT)
        if not relative.as_posix().startswith(TRANSLATABLE_PATH_PREFIXES):
            continue
        japanese_path = JAPANESE_ROOT / relative
        if not japanese_path.is_file():
            raise FileNotFoundError(f"일본어 가이드 파일 누락: {relative.as_posix()}")
        english_data = load_json(english_path)
        japanese_data = load_json(japanese_path)
        if structure_signature(english_data) != structure_signature(japanese_data):
            mismatched_files.append(relative.as_posix())
            continue
        for english, japanese in collect_visible_pairs(english_data, japanese_data):
            if patchouli_tag_signature(english) != patchouli_tag_signature(
                japanese
            ) or english.count("/$") != japanese.count("/$"):
                tag_mismatches += 1
                continue
            sources.setdefault(english, set()).add(japanese)
    conflicts = {source for source, values in sources.items() if len(values) != 1}
    mapping = {
        source: next(iter(values))
        for source, values in sources.items()
        if len(values) == 1
    }
    return mapping, conflicts, mismatched_files, tag_mismatches


def candidate() -> dict[str, object]:
    """영어를 기준으로 일본어 구조를 활용한 한국어 후보를 만든다."""
    if not ENGLISH_ROOT.is_dir() or not JAPANESE_ROOT.is_dir():
        extract()
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    if not isinstance(cache, dict):
        raise TypeError("가이드 후보 캐시가 객체가 아닙니다.")
    legacy_cache = load_json(LEGACY_CACHE_FILE) if LEGACY_CACHE_FILE.is_file() else {}
    if not isinstance(legacy_cache, dict):
        raise TypeError("이전 가이드 후보 캐시가 객체가 아닙니다.")
    values = collect_unique_visible()
    japanese_map, conflicts, mismatched_files, tag_mismatches = japanese_source_map()
    requests = {
        value: japanese_map.get(value, value)
        for value in values
        if value not in language.VALUE_OVERRIDES
        and value not in GUIDE_OVERRIDES
        and not isinstance(cache.get(value), str)
    }
    failures: list[str] = []
    if requests:
        completed = 0
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(
                    ars_family.request_translation,
                    translation_source,
                    "ja" if source in japanese_map else "en",
                ): source
                for source, translation_source in sorted(requests.items())
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                    completed += 1
                    if completed % 25 == 0:
                        write_json(CACHE_FILE, cache)
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    fallback = legacy_cache.get(source)
                    if isinstance(fallback, str):
                        cache[source] = fallback
                    else:
                        failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("가이드 후보 생성 실패:\n" + "\n".join(failures))
    report = {
        "unique_visible_values": len(values),
        "manual_term_candidates": sum(
            value in language.VALUE_OVERRIDES or value in GUIDE_OVERRIDES
            for value in values
        ),
        "automatic_candidates": sum(
            value not in language.VALUE_OVERRIDES and value not in GUIDE_OVERRIDES
            for value in values
        ),
        "japanese_assisted_candidates": sum(
            value in japanese_map
            and value not in language.VALUE_OVERRIDES
            and value not in GUIDE_OVERRIDES
            for value in values
        ),
        "japanese_source_conflicts": len(conflicts),
        "japanese_structure_mismatches": mismatched_files,
        "japanese_tag_mismatches": tag_mismatches,
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


@functools.cache
def language_value_lookup() -> dict[str, str]:
    """현재 검수된 언어 파일의 영어 값과 한국어 값을 연결한다."""
    english = language.load_json(language.ENGLISH_FILE)
    korean = language.load_json(language.KOREAN_FILE)
    return {
        source: korean[key]
        for key, source in english.items()
        if isinstance(source, str) and isinstance(korean.get(key), str)
    }


def crafting_title(source: str) -> str | None:
    """단순 제작 문구를 확정된 아이템 이름으로 통일한다."""
    match = re.fullmatch(
        r"Crafting (?:a|an) (?P<open>\$\([^)]+\))?"
        r"(?P<name>[^$]+?)(?P<close>/\$)?\.?",
        source,
    )
    if not match:
        return None
    name = match.group("name")
    translated = language.VALUE_OVERRIDES.get(name, language_value_lookup().get(name))
    if translated is None:
        return None
    return f"{match.group('open') or ''}{translated}{match.group('close') or ''} 제작"


def translate_visible(
    value: object,
    cache: dict[str, object],
    relative: str,
    visible_index: list[int],
) -> object:
    """JSON 구조를 보존하며 표시 필드만 검수 후보로 교체한다."""
    if isinstance(value, dict):
        translated: dict[str, object] = {}
        for key, child in value.items():
            if key in VISIBLE_FIELDS and isinstance(child, str):
                index = visible_index[0]
                visible_index[0] += 1
                candidate_value = LOCATION_OVERRIDES.get(
                    (relative, index),
                    GUIDE_OVERRIDES.get(
                        child,
                        crafting_title(child)
                        or language.VALUE_OVERRIDES.get(child, cache.get(child)),
                    ),
                )
                if not isinstance(candidate_value, str):
                    raise KeyError(f"가이드 번역 후보 누락: {child}")
                reviewed = language.reviewed_value(
                    f"patchouli.{key}", child, candidate_value
                )
                reviewed = reviewed.replace("\u200b", "")
                reviewed = reviewed.replace("/ $", "/$")
                reviewed = re.sub(r"(\$\([^)]+\)) +", r"\1", reviewed)
                reviewed = re.sub(r" +/\$", "/$", reviewed)
                reviewed = re.sub(
                    r"/\$ +(?=[은는이가을를와과로에도만부터까지께])", "/$", reviewed
                )
                translated[key] = reviewed
            else:
                translated[key] = translate_visible(
                    child, cache, relative, visible_index
                )
        return translated
    if isinstance(value, list):
        return [
            translate_visible(child, cache, relative, visible_index) for child in value
        ]
    return value


def normalize() -> dict[str, object]:
    """영어 책 전체를 기준으로 한국어 작업본 235개를 재생성한다."""
    cache = load_json(CACHE_FILE)
    if not isinstance(cache, dict):
        raise TypeError("가이드 후보 캐시가 객체가 아닙니다.")
    translated_files = 0
    copied_templates = 0
    for source in sorted(ENGLISH_ROOT.rglob("*.json")):
        relative = source.relative_to(ENGLISH_ROOT)
        data = load_json(source)
        if relative.as_posix().startswith(TRANSLATABLE_PATH_PREFIXES):
            translated = translate_visible(data, cache, relative.as_posix(), [0])
            translated_files += 1
        else:
            translated = data
            copied_templates += 1
        write_json(KOREAN_ROOT / relative, translated)
    report = {
        "files_normalized": translated_files,
        "unchanged_template_files": copied_templates,
        "review_status": "full_existing_korean_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def structure_signature(value: object) -> object:
    """표시 문자열 값만 제외한 JSON 구조 서명을 만든다."""
    if isinstance(value, dict):
        return {
            key: (
                "<VISIBLE>"
                if key in VISIBLE_FIELDS and isinstance(child, str)
                else structure_signature(child)
            )
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [structure_signature(child) for child in value]
    return value


def verify() -> tuple[dict[str, object], int]:
    """파일 수, JSON 구조, Patchouli 태그와 미번역을 검증한다."""
    errors: list[str] = []
    english_files = sorted(ENGLISH_ROOT.rglob("*.json"))
    korean_files = sorted(KOREAN_ROOT.rglob("*.json"))
    english_rel = {path.relative_to(ENGLISH_ROOT) for path in english_files}
    korean_rel = {path.relative_to(KOREAN_ROOT) for path in korean_files}
    if english_rel != korean_rel:
        errors.append("가이드 파일 집합 불일치")
    untranslated: list[str] = []
    machine_fragments: list[str] = []
    for relative in sorted(english_rel & korean_rel):
        source = load_json(ENGLISH_ROOT / relative)
        target = load_json(KOREAN_ROOT / relative)
        if structure_signature(source) != structure_signature(target):
            errors.append(f"JSON 구조 불일치: {relative.as_posix()}")
            continue
        source_values = visible_strings(source)
        target_values = visible_strings(target)
        if len(source_values) != len(target_values):
            errors.append(f"표시 문자열 수 불일치: {relative.as_posix()}")
            continue
        for index, (source_value, target_value) in enumerate(
            zip(source_values, target_values, strict=True)
        ):
            if Counter(patchouli_tag_signature(source_value)) != Counter(
                patchouli_tag_signature(target_value)
            ):
                errors.append(f"Patchouli 태그 불일치: {relative.as_posix()}:{index}")
            if source_value.count("/$") != target_value.count("/$"):
                errors.append(
                    f"Patchouli 닫기 태그 불일치: {relative.as_posix()}:{index}"
                )
            if (
                relative.as_posix().startswith(TRANSLATABLE_PATH_PREFIXES)
                and source_value == target_value
                and re.search(r"[A-Za-z]{3,}", source_value)
                and not is_allowed_unchanged(source_value)
            ):
                untranslated.append(f"{relative.as_posix()}:{index}:{source_value}")
            if re.search(r"[ぁ-んァ-ン一-龯]", target_value) or any(
                fragment in target_value for fragment in FORBIDDEN_GUIDE_FRAGMENTS
            ):
                machine_fragments.append(
                    f"{relative.as_posix()}:{index}:{target_value}"
                )
    if untranslated:
        errors.append(f"가이드 미번역: {untranslated[:30]}")
    if machine_fragments:
        errors.append(f"가이드 기계번역 잔여: {machine_fragments[:30]}")
    report = {
        "files": len(english_rel),
        "untranslated": len(untranslated),
        "machine_translation_fragments": len(machine_fragments),
        "review_status": "full_existing_korean_reviewed",
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "validation.json", report)
    return report, 1 if errors else 0


def build() -> dict[str, object]:
    """검증된 한국어 가이드를 누적 리소스팩에 복사한다."""
    report, status = verify()
    if status:
        raise RuntimeError(f"가이드 검증 실패: {report['errors']}")
    copied = []
    for source in sorted(KOREAN_ROOT.rglob("*.json")):
        relative = source.relative_to(KOREAN_ROOT)
        destination = OUTPUT_ROOT / relative
        write_json(destination, load_json(source))
        copied.append(relative.as_posix())
    return {"files": len(copied), "copied": copied}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("extract", "candidate", "normalize", "verify", "build")
    )
    args = parser.parse_args()
    if args.command == "extract":
        result = extract()
        status = 0
    elif args.command == "candidate":
        result = candidate()
        status = 0
    elif args.command == "normalize":
        result = normalize()
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
