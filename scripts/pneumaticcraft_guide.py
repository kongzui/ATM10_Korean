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
}

GUIDE_OVERRIDES = {
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
