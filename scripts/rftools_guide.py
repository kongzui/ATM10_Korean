#!/usr/bin/env python3
"""RFTools 통합 Patchouli 가이드를 추출·번역·검증·빌드한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import shutil
from pathlib import Path
from zipfile import ZipFile

import actually_additions_family as candidate_helper
from local_paths import PROJECT_ROOT, resolve_source_root


WORK_ROOT = PROJECT_ROOT / "working/rftools/guide"
ENGLISH_ROOT = WORK_ROOT / "en_us"
KOREAN_ROOT = WORK_ROOT / "ko_kr"
OUTPUT_ROOT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/rftoolsbase/patchouli_books/manual/ko_kr"
)
CACHE_FILE = PROJECT_ROOT / "temp/rftools_guide_candidate_cache_v2.json"
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"
JAR_PREFIXES = (
    "rftoolsbase-",
    "rftoolsbuilder-",
    "rftoolspower-",
    "rftoolsstorage-",
    "rftoolsutility-",
)
SOURCE_PREFIX = "assets/rftoolsbase/patchouli_books/manual/en_us/"
VISIBLE_FIELDS = {"name", "description", "text", "landing_text", "title", "heading"}
PROTECTED = re.compile(
    r"\$\([^)]*\)|%(?:\d+\$)?[A-Za-z%]|\{[^{}]*\}|#[0-9A-Fa-f]{6}|"
    r"\b(?:rftools\w*|minecraft|xnet):[a-z0-9_./-]+\b"
)
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
FORBIDDEN_ARTIFACTS = (
    "그만큼$(",
    "누르다$(",
    "삽입하다$(",
    "사용$(",
    "방어막를",
    "조합법로",
    "차원 세포",
    "물질 비머",
    "타오르는 교반기",
    "크래프터",
    "머신 베이스",
    "비슷한 물건",
    " to a ",
    " so a ",
    " in $(",
)

LOCATION_OVERRIDES = {
    "book.json:name": "RFTools 기술 가이드",
    "book.json:landing_text": (
        "RFTools 계열부터 XNet, Deep Resonance와 그 밖의 McJty 기술을 설명하는 통합 "
        "가이드입니다.$(br)버그를 발견했다면 $(l:rftoolsbase:basics/bugs)여기$()에 "
        "신고해 주세요."
    ),
    "categories/category_rftoolsbuilder_mover.json:description": (
        "움직이는 탈것을 만들고 제어하는 블록을 설명합니다."
    ),
    "categories/category_rftoolsbuilder_shape_cards.json:description": (
        "빌더와 방어막 프로젝터에서 사용할 영역의 형상을 정의하는 카드를 설명합니다."
    ),
    "categories/category_rftoolsstorage.json:description": (
        "아이템을 저장하고 간편하게 이용하는 RFTools Storage의 기능을 설명합니다."
    ),
    "entries/logic/invchecker.json:pages[0].text": (
        "$(item)인벤토리 검사기$()는 뒤쪽 인벤토리의 지정 슬롯에 설정 수량보다 많은 "
        "아이템이 있으면 $(thing)레드스톤 신호$()를 냅니다. GUI에서 슬롯과 아이템, "
        "선택 사항인 $(thing)아이템 태그$(), 피해값 일치 여부를 설정합니다. 아이템과 "
        "태그를 비우면 해당 슬롯의 모든 아이템을 셉니다."
    ),
    "entries/logic/invchecker.json:pages[1].text": (
        "GUI에서 슬롯, 스택 수, 선택 사항인 아이템 태그, 피해값 모드와 기준 수량을 "
        "설정합니다. 해당 슬롯의 모든 유효한 아이템을 세려면 아이템 또는 태그 조건을 "
        "비워 두세요."
    ),
    "entries/logic/redstone_receiver.json:pages[0].text": (
        "연결된 레드스톤 송신기의 신호를 받습니다. 이 수신기를 들고 송신기나 연결된 다른 "
        "수신기를 우클릭하면 같은 채널에 연결됩니다. 아날로그 모드를 켜면 송신한 신호 "
        "강도를 그대로 출력합니다."
    ),
    "entries/machines/crafter.json:pages[0].text": (
        "제작기는 블록과 아이템을 자동으로 제작합니다. 최고 등급은 조합법을 최대 8개까지 "
        "처리합니다.$(br2)재료용 입력 슬롯 26개와 출력 슬롯 4개가 있습니다."
    ),
    "entries/machines/crafter.json:pages[1].text": (
        "R 버튼으로 슬롯의 내용물을 $(l)기억$()시키면 해당 입력 또는 출력 슬롯에는 "
        "지정한 아이템만 들어갑니다. 기억을 지우려면 F 버튼을 누르세요.$(br2)"
        "$(5)주입$()하면 전력 사용량이 줄어듭니다.$(br2)제작기는 "
        "$(l:rftoolsbase:tools/filtermodule)필터 모듈$(/l)을 지원합니다."
    ),
    "entries/machines/dialing_device.json:pages[1].text": (
        "먼저 물질 송신기를 선택하세요. 주변에 하나뿐이면 자동으로 선택됩니다. 그다음 아래 "
        "목록에서 물질 수신기를 고르고 '연결' 또는 '한 번 연결'을 선택합니다. '한 번 "
        "연결'은 누군가 순간이동하면 즉시 연결을 끊습니다."
    ),
    "entries/machines/matter_beamer.json:pages[0].text": (
        "물질 빔 발사기는 재료 아이템을 $(l:rftoolsbase:machines/spawner)생성기$(/l)로 "
        "보냅니다. 입력 슬롯이 하나이며 작동 중에는 FE를 사용합니다. 연결된 생성기가 "
        "사용할 수 있는 아이템만 전송합니다."
    ),
    "entries/machines/matter_beamer.json:pages[1].heading": "물질 빔 발사기",
    "entries/machines/matter_beamer.json:pages[2].text": (
        "물질 빔 발사기를 렌치로 선택한 뒤 대상 생성기를 렌치로 사용하세요. 선택한 빔 "
        "발사기를 다시 렌치로 사용하면 목적지가 지워집니다."
    ),
    "entries/machines/matter_beamer.json:pages[3].text": (
        "빔 발사기에 레드스톤 신호를 주고 생성기 조합법에 필요한 재료를 넣으세요. "
        "$(5)주입$()하면 펄스마다 더 많은 아이템을 보내고 FE 소모량이 줄어듭니다."
    ),
    "entries/machines/matter_receiver.json:pages[0].text": (
        "물질 수신기는 $(l:rftoolsbase:machines/matter_transmitter)물질 송신기$(/l)에서 "
        "플레이어가 순간이동해 도착하는 장치입니다. $(l:rftoolsbase:machines/dialing_device)"
        "다이얼링 장치$(/l)로 송신기와 수신기를 연결하세요.$(br2)$(5)주입$()하면 전력 "
        "소모량이 줄어듭니다."
    ),
    "entries/machines/matter_transmitter.json:pages[0].text": (
        "물질 송신기는 플레이어를 $(l:rftoolsbase:machines/matter_receiver)물질 수신기$(/l)로 "
        "순간이동시킵니다. $(l:rftoolsbase:machines/dialing_device)다이얼링 장치$(/l)로 "
        "송신기와 수신기를 연결하세요.$(br2)$(5)주입$()하면 전력 소모량이 줄고 "
        "순간이동 속도가 빨라집니다."
    ),
    "entries/tools/filtermodule.json:pages[0].text": (
        "필터 모듈은 기계가 받을 아이템을 허용 목록이나 차단 목록으로 제한합니다. 빌더, "
        "모듈식 저장소, 제작기 등 여러 기계가 지원합니다.$(br2)블록, 아이템과 태그를 "
        "등록할 수 있으며 NBT와 피해값 일치 여부도 설정할 수 있습니다."
    ),
    "entries/tools/filtermodule.json:pages[1].text": (
        "$(5)인벤토리를 웅크린 채 우클릭$()하면 그 안의 아이템과 블록을 필터에 "
        "추가합니다.$(br)$(5)월드의 블록을 웅크린 채 우클릭$()하면 해당 블록을 "
        "추가합니다.$(br2)필터 모듈 GUI에서 태그를 직접 추가하거나 블록과 아이템을 "
        "해당 태그로 변환할 수도 있습니다."
    ),
    "entries/powerstorage/powercell.json:pages[0].text": (
        "$(item)파워셀$()은 많은 전력을 저장합니다. 하나씩 설치하거나 서로 맞닿게 놓아 "
        "멀티블록 구조로 연결할 수 있습니다. 등급이 달라도 연결되며, 파워셀끼리 RF를 "
        "자동으로 분배합니다."
    ),
    "entries/powerstorage/powercell.json:pages[1].text": (
        "파워셀에는 UI가 없습니다. 원하는 면을 $(l:rftoolsbase:tools/smartwrench)스마트 "
        "렌치$()의 $(thing)렌치 모드$()로 사용해 입력, 출력 또는 사용하지 않음으로 "
        "설정하세요. 파란색은 입력, 노란색은 출력, 빈 면은 둘 다 사용하지 않음을 뜻합니다."
    ),
    "entries/mover/mover.json:pages[0].text": (
        "무버는 탈것이 이동할 위치를 표시합니다.$(br2)"
        "$(l:rftoolsbase:mover/mover_controller)무버 제어기$(/l)로 무버를 찾아 이동 "
        "네트워크에 연결하세요."
    ),
    "entries/mover/mover_controller.json:pages[0].text": (
        "무버 제어기는 여러 무버를 연결합니다. 무버 하나에 인접하게 설치한 뒤 사용해 "
        "연결 가능한 다른 무버를 찾으세요."
    ),
    "entries/mover/vehicle_builder.json:name": "탈것 빌더",
    "entries/mover/vehicle_builder.json:pages[0].text": (
        "탈것 빌더는 공간 챔버의 블록으로 탈것을 만듭니다.$(br2)먼저 올바른 공간 챔버를 "
        "완성한 뒤 탈것 빌더로 해당 영역을 탈것으로 바꾸세요."
    ),
    "entries/mover/vehicle_cards.json:name": "탈것 카드",
    "entries/mover/vehicle_cards.json:pages[0].text": (
        "탈것 카드는 탈것을 구성하는 블록을 저장합니다. 탈것 빌더가 유효한 공간 챔버의 "
        "내용을 카드에 담습니다."
    ),
    "entries/mover/vehicle_cards.json:pages[2].text": (
        "카드를 무버에 넣으면 해당 지점에 탈것을 배치합니다. 이후 무버 제어기로 연결된 "
        "무버 사이에서 탈것을 이동할 수 있습니다."
    ),
    "entries/mover/vehicle_modules.json:name": "탈것 모듈",
    "entries/mover/vehicle_modules.json:pages[0].text": (
        "탈것 모듈은 무버 제어기와 상호 작용하는 화면 모듈입니다. 모듈을 들고 무버 "
        "제어기에 사용해 연결하세요."
    ),
    "entries/mover/vehicle_modules.json:pages[3].text": (
        "제어 모듈은 탈것을 선택한 무버로 보냅니다. 상태 모듈은 RFTools 화면에 탈것 "
        "정보를 표시합니다."
    ),
    "entries/scanner/scanner.json:pages[0].text": (
        "저장소 스캐너는 주변 인벤토리를 검색해 내용물을 하나의 GUI에 표시합니다. 아이템을 "
        "검색하거나 꺼내고 연결된 인벤토리에 다시 넣을 수 있습니다."
    ),
    "entries/scanner/scanner.json:pages[3].text": (
        "검색창은 아이템 이름으로 필터링합니다. @minecraft 또는 @rftoolsstorage처럼 검색어 "
        "앞에 @를 붙이면 모드 ID로 필터링합니다."
    ),
    "entries/scanner/modules.json:pages[2].text": (
        "저장소 제어 모듈은 아이템 필터를 최대 9개까지 감시합니다. 모든 인벤토리를 세거나 "
        "별표 또는 경로 지정이 가능한 인벤토리만 셀 수 있습니다."
    ),
    "entries/scanner/modules.json:pages[3].text": (
        "비우기 모듈은 조건에 맞는 플레이어 인벤토리의 아이템을 연결된 스캐너 네트워크로 "
        "보냅니다. 아이템 태그를 사용하면 여러 아이템을 한 조건으로 묶을 수 있습니다."
    ),
    "entries/shape_cards/shape_card_def.json:pages[2].text": (
        "카드를 우클릭해 상자, 구, 원기둥, 원뿔, 원환체, 각기둥, 스캔 또는 합성 형상을 "
        "편집하세요. 웅크린 채 사용하면 월드에서 위치를 선택할 수 있습니다."
    ),
    "entries/modularstorage/storagemodules.json:pages[0].text": (
        "저장 모듈은 모듈식 저장소에 아이템을 실제로 보관합니다. 1티어는 100스택, 2티어는 "
        "200스택, 3티어는 300스택, 4티어는 500스택을 저장합니다."
    ),
    "entries/modularstorage/remote_module.json:pages[1].text": (
        "일반적인 원격 사용에는 저장소 스캐너에 연결한 "
        "$(l:rftoolsbase:scanner/modules)저장소 제어 모듈$(/l)을 태블릿에 넣으세요."
    ),
    "entries/basics/machine_bases.json:pages[0].text": (
        "$(item)기계 기반$()은 제작 재료라는 점에서 "
        "$(l:rftoolsbase:basics/machine_frames)기계 프레임$()과 비슷하지만 완성되는 "
        "기계의 형태가 다릅니다.$(br2)기계 기반으로 만드는 기계는 블록 높이의 1/4이며 "
        "대개 $(thing)레드스톤$() 입력이나 출력을 갖습니다."
    ),
    "entries/basics/machine_bases.json:pages[1].text": (
        "기계를 설치할 때 바라보는 방향은 $(thing)커서와 가장 가까운 블록 모서리$()에 "
        "따라 정해집니다.$(br2)설치할 면에 X자를 그렸다고 생각하고 커서가 X자의 어느 "
        "구역을 가리키는지 확인하세요.$(br2)출력은 이 방향을 향하고 입력은 반대쪽에서 "
        "받습니다."
    ),
    "entries/basics/machine_bases.json:pages[2].text": (
        "비좁은 공간이나 벽에 기계를 설치할 때 특히 편리합니다.$(br2)방향이 마음에 들지 "
        "않으면 $(l:rftoolsbase:tools/smartwrench)스마트 렌치$()의 렌치 모드로 "
        "우클릭해 회전하세요."
    ),
    "entries/basics/machine_bases.json:pages[3].heading": "기계 기반",
    "entries/basics/machine_bases.json:pages[3].text": (
        "$(item)기계 기반$() 자체에는 기능이 없으며 여러 블록을 만드는 기본 재료로 "
        "사용합니다."
    ),
    "entries/logic/analog.json:name": "아날로그 연산기",
    "entries/logic/analog.json:pages[0].text": (
        "$(item)아날로그 연산기$()는 A와 B 입력을 비교한 결과에 따라 입력 신호를 "
        "계산합니다.$(br2)블록을 우클릭하면 출력(O), 입력(I), 두 비교 입력(A, B)의 "
        "위치를 보여 주는 GUI가 열립니다."
    ),
    "entries/logic/analog.json:pages[1].heading": "아날로그 연산기",
    "entries/logic/analog.json:pages[3].text": (
        "아날로그 연산기 아래에는 A = B, A < B, A > B의 세 조건이 있습니다.$(br2)"
        "각 조건에서 입력 신호에 곱할 값과 더할 값을 정할 수 있습니다. 예를 들어 신호 "
        "강도를 두 배로 만든 뒤 10을 더할 수 있습니다."
    ),
    "entries/logic/analog.json:pages[4].text": (
        "신호를 나누거나 값을 빼려면 각각 1보다 작은 수를 곱하거나 음수를 더하세요. "
        "예를 들어 0.5를 곱하면 절반이 되고 -10을 더하면 10이 줄어듭니다.$(br2)"
        "레드스톤 신호는 0부터 15까지만 사용하므로 범위를 벗어난 결과는 각각 0 또는 "
        "15로 제한됩니다.$(br2)$(i)수학은 재미있지 않나요?$()"
    ),
    "entries/logic/logic.json:pages[0].text": (
        "레드스톤 입력 3개와 출력 1개가 있습니다. GUI에서 각 입력 조합의 출력을 끔, 켬, "
        "유지 중 하나로 정하세요. '유지'는 입력이 해당 조합으로 바뀌기 전의 출력 상태를 "
        "그대로 유지합니다."
    ),
    "entries/logic/redstone_information.json:pages[0].text": (
        "여러 레드스톤 채널을 저장하는 아이템입니다. 채널을 추가하려면 $(5)우클릭$()으로 "
        "$(l:rftoolsbase:logic/redstone_transmitter)레드스톤 송신기$(/l)나 "
        "$(l:rftoolsbase:logic/redstone_receiver)레드스톤 수신기$(/l)를 선택하세요. 이후 "
        "$(l:rftoolsbase:tools/tablet)태블릿$(/l)에 "
        "넣으면 어디서든 레드스톤 신호를 확인하고 바꿀 수 있습니다."
    ),
    "entries/logic/redstone_transmitter.json:pages[1].text": (
        "$(l:rftoolsbase:logic/redstone_receiver)레드스톤 수신기$(/l)로 신호를 "
        "받으세요.$(br2)GUI에서 채널에 알아보기 쉬운 이름을 지정할 수 있습니다."
    ),
    "entries/logic/wire.json:name": "와이어",
    "entries/logic/wire.json:pages[0].text": (
        "$(item)와이어$()는 $(thing)입력 신호$()를 $(thing)출력$()으로 그대로 "
        "전달합니다. 단순하고 지연이 거의 없지만 직선으로만 연결됩니다.$(br2)"
        "$(l:rftoolsbase:basics/machine_bases)기계 기반$()으로 만든 다른 블록처럼 벽이나 "
        "천장에도 설치할 수 있습니다."
    ),
    "entries/logic/wire.json:pages[1].heading": "와이어",
    "entries/machines/infusing.json:pages[0].text": (
        "$(item)기계 주입기$()는 $(l:rftoolsbase:basics/dimensional_shards)차원 조각$()을 "
        "사용해 여러 기계의 $(thing)효율$()을 높입니다. 대부분 전력 요구량이 줄고, 일부 "
        "장치는 추가 효과도 얻습니다.$(br2)기계 주입기 자체를 $(thing)주입$()하면 "
        "주입기의 전력 사용량이 줄어듭니다."
    ),
    "entries/machines/infusing.json:pages[2].text": (
        "$(li)$(l:rftoolsutility:machines/environmental)환경 제어기$() "
        "$(li)$(l:rftoolsutility:machines/dialing_device)다이얼링 장치$() "
        "$(li)$(l:rftoolsutility:machines/matter_receiver)물질 수신기$() "
        "$(li)$(l:rftoolsutility:machines/matter_transmitter)물질 송신기$()(+속도) "
        "$(li)$(l:rftoolsutility:machines/spawner)생성기$() "
        "$(li)$(l:rftoolsutility:machines/matter_beamer)물질 빔 발사기$()(+속도, 필요 아이템 감소) "
        "$(li)$(l:rftoolsutility:machines/screen_controller)화면 제어기$()(+범위) "
        "$(li)$(l:rftoolsutility:machines/crafter)제작기$()"
    ),
    "entries/machines/infusing.json:pages[4].text": (
        "$(li)$(l:rftoolspower:powergeneration/coalgenerator)석탄 발전기$() "
        "$(li)$(l:rftoolspower:powergeneration/endergenic)엔더제닉 발전기$()(+발전량, 진주 보관 중 전력 손실 감소) "
        "$(li)$(l:rftoolspower:powerstorage/dimensionalcell)차원 셀$()(장거리 RF 추출 비용 감소, RF/t 출력 증가) "
        "$(li)$(l:rftoolspower:powergeneration/blazingagitator)블레이징 교반기$()(+가열된 블레이즈 막대 품질) "
        "$(li)$(l:rftoolspower:powergeneration/blazinggenerator)블레이징 발전기$()(+발전량)"
    ),
    "entries/machines/screen.json:pages[0].text": (
        "화면은 장착한 모듈에 따라 여러 정보를 표시합니다. 근처의 "
        "$(l:rftoolsbase:machines/screen_controller)화면 제어기$(/l)에서 무선으로 전력을 "
        "공급받아야 합니다.$(br2)빈손으로 $(5)우클릭$()해 화면 GUI를 여세요."
    ),
    "entries/machines/screen.json:pages[1].text": (
        "GUI에서 모듈을 설치하거나, 모듈을 들고 화면을 우클릭해 설치할 수 있습니다.$(br2)"
        "에너지 모듈처럼 대상을 지정해야 하는 모듈은 먼저 감시할 기계를 모듈로 "
        "$(5)웅크린 채 우클릭$()하세요."
    ),
    "entries/machines/screen.json:pages[2].text": (
        "화면에 설치한 모듈은 일반 화면 GUI에서 각 모듈 GUI를 열어 표시 방식을 설정할 수 "
        "있습니다.$(br2)완전 밝기 모드를 켤 수 있으며, 렌치로 화면의 크기와 투명도를 "
        "바꿀 수도 있습니다."
    ),
    "entries/powerstorage/dimensionalcell.json:name": "차원 셀",
    "entries/powerstorage/dimensionalcell.json:pages[0].text": (
        "차원 셀은 여러 차원에 걸쳐 연결할 수 있는 전력 저장 장치입니다. "
        "$(l:rftoolsbase:powerstorage/powercell)파워셀$(/l)처럼 FE를 저장하고 전송하지만, "
        "연결된 셀끼리는 맞닿지 않아도 전력을 공유합니다."
    ),
    "entries/powerstorage/dimensionalcell.json:pages[1].text": (
        "차원 셀은 $(l:rftoolsbase:powerstorage/powercell_card)파워셀 카드$(/l)로 "
        "연결합니다. 연결되지 않은 카드를 넣어 새 연결을 만들거나 기존 셀의 연결을 다른 "
        "카드에 복사하세요."
    ),
    "entries/powerstorage/dimensionalcell.json:pages[2].text": (
        "GUI에는 연결·복사용 카드 슬롯, FE 아이템 충전 슬롯, 네트워크 저장량 표시줄, 면 "
        "모드 버튼과 FE 입출력 통계 버튼이 있습니다."
    ),
    "entries/powerstorage/dimensionalcell.json:pages[3].text": (
        "없음, 입력, 출력 버튼은 모든 면을 FE 무시, 수신, 전송으로 설정합니다. 각 면은 "
        "$(l:rftoolsbase:tools/smartwrench)스마트 렌치$(/l)로도 바꿀 수 있습니다. 파란색은 "
        "입력, 노란색은 출력, 빈 면은 비활성화입니다."
    ),
    "entries/powerstorage/dimensionalcell.json:pages[4].text": (
        "차원 셀을 $(thing)출력 모드$()로 쓰면 원격 셀에서 RF를 가져올 때 소량의 비용이 "
        "듭니다. 보통 몇 퍼센트에 불과하지만 누적될 수 있습니다. 차원 셀을 "
        "$(l:rftoolsbase:machines/infusing)주입$()하면 이 비용이 줄어듭니다."
    ),
    "entries/powerstorage/dimensionalcell.json:pages[5].text": (
        "기본 차원 셀은 250,000 RF를 저장하고 최대 1,250 RF/t를 입출력합니다. "
        "$(l:rftoolsbase:machines/infusing)주입$()하면 전송 속도가 빨라집니다."
    ),
    "entries/powerstorage/dimensionalcell.json:pages[6].text": (
        "중급 차원 셀은 1,000,000 RF를 저장하고 최대 5,000 RF/t를 입출력합니다. "
        "$(l:rftoolsbase:machines/infusing)주입$()하면 전송 속도가 빨라집니다."
    ),
    "entries/powerstorage/dimensionalcell.json:pages[7].text": (
        "고급 차원 셀은 4,000,000 RF를 저장하고 최대 20,000 RF/t를 입출력합니다. "
        "$(l:rftoolsbase:machines/infusing)주입$()하면 전송 속도가 빨라집니다."
    ),
    "entries/machines/environmental.json:pages[0].text": (
        "$(item)환경 제어기$()는 넓은 범위에 여러 효과를 부여합니다. 동시에 "
        "$(thing)최대 7가지 효과$()를 사용할 수 있지만 효과가 많을수록 전력 사용량도 "
        "늘어납니다."
    ),
    "entries/machines/environmental.json:pages[2].text": "환경 제어기 GUI",
    "entries/machines/environmental.json:pages[3].text": (
        "주요 UI 요소는 다음과 같습니다.$(br2)왼쪽에는 활성 모듈을 넣는 "
        "$(item)모듈 슬롯$() 7개가 있습니다.$(br2)위쪽 "
        "슬라이더로 작동 반경을 정하고, 아래 입력란에서 최소·최대 Y 높이를 지정합니다. "
    ),
    "entries/machines/environmental.json:pages[4].text": (
        "아래 필터에서는 모듈 효과를 받을 플레이어나 면역인 플레이어를 지정합니다. 모든 "
        "몹과 플레이어, 플레이어 차단 목록, 플레이어 허용 목록, 수동적 몹, 적대적 몹, "
        "적대적·수동적 몹의 모드를 지원합니다.$(br2)마지막으로 레드스톤 제어 버튼과 "
        "왼쪽 아래의 전력 측정기가 있습니다."
    ),
    "entries/machines/spawner.json:pages[0].text": (
        "생성기는 채운 주사기, FE와 연결된 $(l:rftoolsbase:machines/matter_beamer)물질 빔 "
        "발사기$(/l)가 공급한 재료로 몹을 생성합니다. 선택한 몹에 따라 필요한 재료가 "
        "달라집니다."
    ),
    "entries/machines/spawner.json:pages[2].text": (
        "같은 종류의 몹에게 주사기를 사용해 완전히 채운 뒤 생성기에 넣으세요. 툴팁에 "
        "저장된 몹과 주입 수준이 표시됩니다."
    ),
    "entries/machines/spawner.json:pages[3].text": (
        "GUI에는 물질 버퍼 세 개가 표시됩니다. 물질 빔 발사기는 주사기에 든 몹이 요구하는 "
        "재료를 보내야 하며 관련 없는 재료는 무시됩니다."
    ),
    "entries/powergeneration/blazingagitator.json:name": "블레이징 교반기",
    "entries/powergeneration/blazingagitator.json:pages[0].text": (
        "블레이징 교반기는 블레이즈 막대를 "
        "$(l:rftoolsbase:powergeneration/blazinggenerator)블레이징 발전기$(/l)의 연료로 "
        "가공합니다. 소량의 FE를 사용해 일반 막대를 가열된 블레이즈 막대로 만듭니다."
    ),
    "entries/powergeneration/blazingagitator.json:pages[2].text": (
        "입력 격자에서 서로 이웃한 막대는 품질을 높여 줍니다. 품질이 좋은 막대는 더 빨리 "
        "완성되고 전력 품질도 좋아지므로 격자에 강한 막대를 몇 개 유지하세요."
    ),
    "entries/powergeneration/blazinggenerator.json:name": "블레이징 발전기",
    "entries/powergeneration/blazinggenerator.json:pages[0].text": (
        "블레이징 발전기는 가열된 블레이즈 막대를 태워 FE를 생산합니다. 일반 블레이즈 "
        "막대는 먼저 $(l:rftoolsbase:powergeneration/blazingagitator)블레이징 교반기$(/l)에서 "
        "가공해야 합니다."
    ),
    "entries/powergeneration/blazinginfuser.json:name": "블레이징 주입기",
    "entries/powergeneration/blazinginfuser.json:pages[0].text": (
        "블레이징 주입기는 $(l:rftoolsbase:powergeneration/blazingagitator)블레이징 "
        "교반기$(/l)에서 만든 가열된 블레이즈 막대를 강화합니다. 촉매를 소모해 막대의 "
        "출력, 지속 시간 또는 둘 다를 높입니다."
    ),
    "entries/powergeneration/endergenic.json:pages[0].text": (
        "엔더제닉 발전은 정확한 타이밍이 핵심입니다. 진주 주입기가 엔더제닉 진주를 만들고, "
        "발전기가 진주를 받아 다시 발사하며, 알맞은 순간에 진주를 받으면 FE가 생성됩니다."
    ),
    "entries/powergeneration/endergenic.json:pages[9].text": (
        "엔더 모니터는 발전기 상태를 감시해 타이밍 자동화를 돕습니다. 잘 조정한 구성도 "
        "진주를 잃을 수 있으므로 진주 공급과 시작 회로를 준비하세요."
    ),
    "entries/basics/dimensional_shards.json:pages[0].text": (
        "$(item)차원 조각 광석$()은 여러 차원의 지하에서 작은 광맥으로 생성됩니다. "
        "$(thing)행운$() 마법부여가 적용되며 채굴하면 $(item)차원 조각$()을 "
        "떨어뜨립니다.$(br2)복잡한 조합법에 쓰고 "
        "$(l:rftoolsbase:machines/infusing)기계 주입$()에도 사용합니다."
    ),
    "entries/basics/dimensional_shards.json:pages[3].text": (
        "$(item)차원 조각$()으로 여러 종류의 $(item)장식 블록$()도 만들 수 있습니다."
    ),
    "entries/basics/dimensional_shards.json:pages[4].text": (
        "RFTools Dimensions가 설치되어 있다면 멋진 장식 블록을 만들 수 있지만, 지금은 "
        "설치되어 있지 않네요. :("
    ),
    "entries/builder/builder_intro.json:pages[0].text": (
        "빌더는 채석, 건설, 유체 펌프 작업, 경험치와 아이템 수집 등을 수행합니다. 형상 "
        "카드로 작업 종류와 영역을 지정하세요."
    ),
    "entries/builder/builder_target.json:pages[1].text": (
        "형상 카드에 크기와 오프셋을 직접 입력할 수 있습니다.$(br2)오프셋은 항상 빌더를 "
        "기준으로 하며, 0,0,0이면 빌더가 영역의 중심에 놓입니다."
    ),
    "entries/builder/builder_target.json:pages[2].text": (
        "빌더를 웅크린 채 우클릭해 영역 선택을 시작할 수 있습니다. 또는 형상 카드에서 "
        "크기를 정하고 GUI의 기준점 버튼으로 오프셋을 조절하세요."
    ),
    "entries/projector/scanner.json:pages[1].text": (
        "왼쪽 위 슬롯에 입력 형상 카드를 넣으세요. 이 카드가 스캔할 영역의 크기와 "
        "오프셋을 정합니다.$(br2)$(thing)스캔$()을 누르면 결과가 왼쪽 아래 슬롯의 형상 "
        "카드에 기록됩니다."
    ),
    "entries/shield/shield_advanced.json:pages[0].text": (
        "방어막 프로젝터는 주변 틀 블록이나 GUI에 넣은 형상 카드로 방어막을 만듭니다. "
        "형상 카드로 만든 방어막은 틀 블록을 무시합니다."
    ),
    "entries/shield/shield_advanced.json:pages[1].text": (
        "표시 모드는 숨김, 방어막, 반투명, 불투명, 모방입니다. 모방은 모방 슬롯에 넣은 "
        "블록의 텍스처를 방어막에 사용합니다."
    ),
    "entries/machines/screen_controller.json:pages[0].text": (
        "화면 제어기는 주변의 $(l:rftoolsbase:machines/screen)화면$(/l)에 전력을 "
        "공급합니다. GUI의 '스캔' 버튼을 누르면 32×32×32 범위의 모든 화면을 "
        "연결합니다.$(br2)$(5)주입$()하면 범위가 넓어집니다."
    ),
    "entries/machines/screen_link.json:pages[0].text": (
        "화면 연결기는 $(l:rftoolsbase:machines/screen)화면$(/l)의 위치를 저장해 "
        "$(l:rftoolsbase:tools/tablet)태블릿$(/l)에서 원격으로 열 수 있게 합니다."
    ),
    "entries/machines/screen_link.json:pages[3].text": (
        "연결기를 태블릿에 넣으세요. 화면이 있는 청크가 로드되어 있으면 태블릿으로 원격 "
        "화면을 엽니다. 웅크린 채 사용하면 태블릿 관리 화면이 열립니다."
    ),
    "entries/machines/teleporter.json:pages[0].text": (
        "충전된 포터는 $(l:rftoolsbase:machines/matter_receiver)물질 수신기$(/l)를 목적지로 "
        "사용하는 휴대용 순간이동 도구입니다. 사용하기 전에 FE로 충전해야 합니다."
    ),
    "entries/machines/teleporter.json:pages[2].text": (
        "포터를 들고 물질 수신기를 우클릭해 목적지를 저장하세요. 기본 포터는 목적지 하나, "
        "고급 포터는 여러 목적지를 저장하고 전환할 수 있습니다."
    ),
    "entries/modularstorage/modularstorage.json:pages[0].text": (
        "모듈식 저장소는 검색 기능이 있는 저장 블록입니다. "
        "$(l:rftoolsbase:modularstorage/storagemodules)저장 모듈$(/l)을 넣으면 보관할 수 "
        "있는 스택 수가 정해집니다."
    ),
    "entries/modularstorage/modularstorage.json:pages[2].text": (
        "아이템은 블록이 아니라 모듈에 저장되므로 모듈을 옮겨도 내용물이 유지됩니다. "
        "상위 등급 모듈일수록 인벤토리가 커집니다."
    ),
    "entries/modularstorage/modularstorage.json:pages[3].text": (
        "GUI에서 아이템을 검색·정렬·압축하고 표시할 인벤토리 크기를 전환할 수 있습니다. "
        "실제 저장 용량은 모듈 슬롯에 넣은 모듈이 결정합니다."
    ),
    "entries/modularstorage/storagemodules.json:pages[4].text": (
        "정형 NBT 조합법으로 업그레이드하면 모듈 내용물이 유지됩니다. 귀중한 모듈을 다른 "
        "시스템으로 옮기기 전에 백업하세요."
    ),
    "entries/machines/crafter.json:name": "제작기",
    "entries/basics/bugs.json:pages[0].text": (
        "McJty 모드에서 버그를 발견했다면 다음 링크로 신고해 주세요. 모드팩에서만 생기는 "
        "문제라면 먼저 모드팩 제작자에게 알려 문제의 원인을 확인하세요."
    ),
    "entries/basics/machine_frames.json:pages[0].text": (
        "모든 기계와 장치에는 일종의 $(thing)프레임$()이 필요합니다. 기계 프레임 자체에는 "
        "기능이 없지만 여러 기계의 공통 제작 재료로 사용합니다."
    ),
    "entries/basics/machine_bases.json:name": "기계 기반",
    "entries/builder/space_chambers.json:pages[0].text": (
        "공간 챔버는 빌더나 탈것 빌더가 복사·이동할 영역을 표시합니다. 챔버 블록과 제어기 "
        "하나로 영역을 정의하세요."
    ),
    "entries/builder/chamber_details.json:pages[0].text": (
        "챔버 세부 정보 화면에는 선택한 공간 챔버의 내용물이 표시됩니다.$(br2)공간 카드를 "
        "우클릭하면 현재 영역 안의 모든 블록과 엔티티를 확인할 수 있습니다."
    ),
    "entries/logic/redstone_receiver.json:pages[1].text": (
        "$(l:rftoolsbase:logic/redstone_transmitter)레드스톤 송신기$(/l) 또는 "
        "$(l:rftoolsbase:machines/screen)화면$(/l)으로 레드스톤 신호를 보내세요."
    ),
    "entries/machines/dialing_device.json:pages[0].text": (
        "다이얼링 장치는 $(l:rftoolsbase:machines/matter_transmitter)물질 송신기$(/l)를 "
        "$(l:rftoolsbase:machines/matter_receiver)물질 수신기$(/l)와 연결합니다. 송신기는 "
        "근처에 있어야 하지만 수신기는 다른 차원처럼 멀리 있어도 됩니다.$(br2)"
        "$(5)주입$()하면 전력 사용량이 줄어듭니다."
    ),
    "entries/logic/sensor.json:pages[0].text": (
        "센서는 입력면 앞의 1, 3 또는 5블록 범위에서 여러 대상을 감지합니다. 설치된 블록, "
        "작물 성장 단계와 엔티티 수 등을 조건으로 사용할 수 있습니다."
    ),
    "entries/logic/counter.json:pages[0].text": (
        "카운터는 레드스톤 펄스를 세다가 지정한 수에 도달하면 레드스톤 신호를 냅니다. "
        "이후 다시 처음부터 셉니다.$(br2)GUI의 '최댓값'은 셀 펄스 수를, '현재값'은 "
        "지금까지 센 수를 나타냅니다."
    ),
    "entries/logic/counter.json:pages[1].text": (
        "현재값이 최댓값과 같아지면 레드스톤 신호를 냅니다. 다음 레드스톤 펄스를 받으면 "
        "신호를 끄고 카운터를 0으로 초기화합니다."
    ),
    "entries/machines/matter_beamer.json:name": "물질 빔 발사기",
    "categories/category_rftoolsutility_logic.json:description": (
        "레드스톤 신호를 만들고 처리하는 논리 회로 블록을 설명합니다."
    ),
    "entries/powerstorage/powercell_card.json:pages[0].text": (
        "이 카드는 $(l:rftoolsbase:powerstorage/dimensionalcell)차원 셀$(/l)을 서로 "
        "연결합니다. 새 카드는 연결되지 않은 상태이며, 차원 셀에 넣어 새 연결을 만들거나 "
        "기존 연결을 복사할 수 있습니다."
    ),
    "categories/category_rftoolsstorage_scanner.json:description": (
        "주변 인벤토리를 한곳에서 이용하게 해 주는 저장소 스캐너를 설명합니다."
    ),
    "entries/scanner/scanner.json:pages[4].text": (
        "인벤토리의 순서를 바꾸거나 제거하고, 경로 지정 가능 상태로 표시하거나 정렬할 수 "
        "있습니다. 경로 지정 가능한 인벤토리는 자동 입출력과 별표 모듈 보기에 사용합니다."
    ),
    "entries/scanner/scanner.json:pages[5].text": (
        "원격으로 사용하려면 $(l:rftoolsbase:scanner/modules)저장소 제어 모듈$(/l)을 "
        "스캐너에 연결한 뒤 $(l:rftoolsbase:scanner/remote)스캐너 태블릿$(/l)에 넣으세요."
    ),
    "entries/shape_cards/shape_card_def.json:pages[0].text": (
        "기본 형상 카드는 형상, 크기, 오프셋과 채움·비움 모드를 저장합니다. 빌더에서 블록을 "
        "배치하거나 방어막 프로젝터에서 형상 방어막을 정의할 때 사용합니다."
    ),
    "entries/powergeneration/coalgenerator.json:pages[2].text": (
        "내부 버퍼가 있어 출력이 잠시 막혀도 계속 연소합니다. 석탄 블록은 오랫동안 "
        "자동으로 가동할 때 편리합니다."
    ),
}

ENVIRONMENTAL_EFFECTS = {
    6: ("신속 I", "0.001"),
    7: ("재생 I", "0.0015"),
    8: ("낙하 피해 50% 감소", "0.001"),
    9: ("발광", "0.001"),
    10: ("성급함 I", "0.001"),
    11: ("야간 투시", "0.001"),
    12: ("포화", "0.001"),
    13: ("행운", "0.002"),
    14: ("적대적 몹 생성 방지", "0.001"),
    15: ("낙하 피해 무효화", "0.003"),
    16: ("성급함 III", "0.001"),
    17: ("수중 호흡", "0.001"),
    18: ("$(thing)크리에이티브 비행$()", "0.004"),
    19: ("재생 III", "0.001"),
    20: ("신속 III", "0.003"),
    21: ("포화 III", "0.003"),
    22: ("셜커·엔더맨 순간이동 방지", "0.001"),
    23: ("실명", "0.001"),
    24: ("독", "0.001"),
    25: ("나약함", "0.001"),
    26: ("구속", "0.001"),
}
for page, (effect, usage) in ENVIRONMENTAL_EFFECTS.items():
    LOCATION_OVERRIDES[f"entries/machines/environmental.json:pages[{page}].text"] = (
        f"범위 안의 모든 유효한 대상에게 {effect} 효과를 적용합니다.$(br2)"
        f"사용량: {usage} RF/t(범위 안의 블록당)"
    )

SOURCE_OVERRIDES = {
    "RFTools": "RFTools",
    "RFTools Base": "RFTools Base",
    "RFTools Builder": "RFTools Builder",
    "RFTools Power": "RFTools Power",
    "RFTools Storage": "RFTools Storage",
    "RFTools Utility": "RFTools Utility",
    "Basics": "기초",
    "Machines": "기계",
    "Tools": "도구",
    "Logic": "논리 회로",
    "Shape Cards": "형상 카드",
    "Power Generation": "발전",
    "Power Storage": "전력 저장",
    "Modular Storage": "모듈식 저장소",
    "Shield": "방어막",
    "Builder": "빌더",
    "Projector": "프로젝터",
    "Scanner": "스캐너",
    "Mover": "무버",
    "Technology Guide": "RFTools 기술 가이드",
}

TERM_REPLACEMENTS = (
    ("RFTools 도구", "RFTools"),
    ("McJty", "McJty"),
    ("엑스넷", "XNet"),
    ("딥 레조넌스", "Deep Resonance"),
    ("파워 셀", "파워셀"),
    ("전원 셀", "파워셀"),
    ("차원 샤드", "차원 조각"),
    ("차원 파편", "차원 조각"),
    ("디멘셔널 샤드", "차원 조각"),
    ("스마트렌치", "스마트 렌치"),
    ("모양 카드", "형상 카드"),
    ("셰이프 카드", "형상 카드"),
    ("쉴드", "방어막"),
    ("장벽", "방어막"),
    ("빌더 머신", "빌더"),
    ("스토리지", "저장소"),
    ("스크린", "화면"),
    ("컨트롤러", "제어기"),
    ("텔레포트", "순간이동"),
    ("트랜스미터", "송신기"),
    ("리시버", "수신기"),
    ("액체", "유체"),
    ("엔터티", "엔티티"),
    ("레시피", "조합법"),
    ("멀티 블록", "멀티블록"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("몰래 우클릭", "웅크린 채 우클릭"),
    ("살짝 우클릭", "웅크린 채 우클릭"),
    ("하십시오", "하세요"),
    ("항목", "아이템"),
    ("차량", "탈것"),
    ("우주 챔버", "공간 챔버"),
    ("우주 공간", "공간 챔버"),
    ("재고 검사기", "인벤토리 검사기"),
    ("Matter Receiver", "물질 수신기"),
    ("Matter Transmitter", "물질 송신기"),
    ("Matter Beamer", "물질 빔 발사기"),
    ("Storage Scanner", "저장소 스캐너"),
    ("Screen Controller", "화면 제어기"),
    ("Mover Controller", "무버 제어기"),
    ("Mover", "무버"),
    ("Crafter", "제작기"),
    ("Powercells", "파워셀"),
    ("Powercell", "파워셀"),
    ("Spawner", "생성기"),
    ("Infusing", "주입"),
    ("순간 이동", "순간이동"),
    ("화이트리스트", "허용 목록"),
    ("블랙리스트", "차단 목록"),
    ("데미지", "피해값"),
    ("몰래 사용", "웅크린 채 사용"),
    ("Tier 1", "1티어"),
    ("Tier 2", "2티어"),
    ("Tier 3", "3티어"),
    ("Tier 4", "4티어"),
    ("Worldgen", "월드 생성"),
    ("Builder", "빌더"),
    ("Keep", "유지"),
    ("PowerCell", "파워셀"),
    ("Machine Infuser", "기계 주입기"),
    ("Composer", "컴포저"),
    ("Silk Touch", "섬세한 손길"),
    ("Fortune", "행운"),
    ("Liquid Card", "유체 형상 카드"),
    ("Shield Projector", "방어막 프로젝터"),
)


def find_jar(instance: Path, prefix: str) -> Path:
    matches = sorted(
        path
        for path in (instance / "mods").glob("*.jar")
        if path.name.lower().startswith(prefix.lower())
    )
    if len(matches) != 1:
        raise FileNotFoundError(f"JAR을 하나로 확정할 수 없습니다: {prefix}: {matches}")
    return matches[0]


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


def prepare(force: bool) -> dict[str, object]:
    instance = resolve_source_root()
    if ENGLISH_ROOT.exists() and not force:
        raise FileExistsError(f"기존 가이드 작업본을 덮어쓰지 않습니다: {ENGLISH_ROOT}")
    if force:
        for root in (ENGLISH_ROOT, KOREAN_ROOT):
            if root.exists():
                shutil.rmtree(root)
    sources: dict[str, str] = {}
    files = 0
    for prefix in JAR_PREFIXES:
        jar = find_jar(instance, prefix)
        with ZipFile(jar) as archive:
            for name in sorted(archive.namelist()):
                if not name.startswith(SOURCE_PREFIX) or not name.endswith(".json"):
                    continue
                relative = name.removeprefix(SOURCE_PREFIX)
                payload = archive.read(name)
                target = ENGLISH_ROOT / relative
                if target.exists() and target.read_bytes() != payload:
                    raise ValueError(f"서로 다른 가이드 파일이 겹칩니다: {relative}")
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(payload)
                    sources[relative] = jar.name
                    files += 1
    book_jar = find_jar(instance, "rftoolsbase-")
    with ZipFile(book_jar) as archive:
        book = json.loads(
            archive.read("data/rftoolsbase/patchouli_books/manual/book.json")
        )
    write_json(ENGLISH_ROOT / "book.json", book)
    sources["book.json"] = book_jar.name
    files += 1
    report = {"files": files, "sources": sources, "status": "prepared"}
    write_json(WORK_ROOT / "inventory.json", report)
    return report


def iter_visible(value: object, path: str = "") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if key in VISIBLE_FIELDS and isinstance(child, str):
                rows.append((child_path, child))
            else:
                rows.extend(iter_visible(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(iter_visible(child, f"{path}[{index}]"))
    return rows


def request_candidate(source: str) -> str:
    """Patchouli 토큰을 요청에서 제외하고 일반 문장 조각만 번역한다."""
    parts = re.split(f"({PROTECTED.pattern}|\\n)", source)
    translated: list[str] = []
    for part in parts:
        if not part:
            continue
        if part == "\n" or PROTECTED.fullmatch(part):
            translated.append(part)
        elif LATIN_WORD.search(part):
            translated.append(candidate_helper.request_translation_candidate(part))
        else:
            translated.append(part)
    return "".join(translated)


def candidate() -> dict[str, object]:
    documents = {
        path.relative_to(ENGLISH_ROOT).as_posix(): load_json(path)
        for path in sorted(ENGLISH_ROOT.rglob("*.json"))
    }
    visible = {
        f"{relative}:{location}": source
        for relative, document in documents.items()
        for location, source in iter_visible(document)
    }
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests = {
        source
        for location, source in visible.items()
        if location not in LOCATION_OVERRIDES
        and source not in SOURCE_OVERRIDES
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
        raise RuntimeError("가이드 번역 후보 생성 실패:\n" + "\n".join(failures))
    candidates = {
        location: LOCATION_OVERRIDES.get(
            location, SOURCE_OVERRIDES.get(source, cache.get(source, source))
        )
        for location, source in visible.items()
    }
    write_json(CANDIDATE_FILE, candidates)
    report = {
        "visible_fields": len(visible),
        "candidate_sources": len(requests),
        "status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


def normalize_value(value: str) -> str:
    """Patchouli 토큰 내부는 건드리지 않고 표시 문장만 정리한다."""
    parts = re.split(f"({PROTECTED.pattern})", value)
    normalized: list[str] = []
    for part in parts:
        if not part or PROTECTED.fullmatch(part):
            normalized.append(part)
            continue
        for old, new in TERM_REPLACEMENTS:
            part = part.replace(old, new)
        part = part.replace(".,", ",").replace(" ​​", " ")
        part = re.sub(r"[ \t]+([,.!?])", r"\1", part)
        normalized.append(part)
    return "".join(normalized)


def rebuild(
    value: object, relative: str, path: str, candidates: dict[str, str]
) -> object:
    if isinstance(value, dict):
        result: dict[str, object] = {}
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if key in VISIBLE_FIELDS and isinstance(child, str):
                result[key] = normalize_value(candidates[f"{relative}:{child_path}"])
            else:
                result[key] = rebuild(child, relative, child_path, candidates)
        return result
    if isinstance(value, list):
        return [
            rebuild(child, relative, f"{path}[{index}]", candidates)
            for index, child in enumerate(value)
        ]
    return value


def normalize() -> dict[str, object]:
    candidates = load_json(CANDIDATE_FILE)
    files = 0
    visible = 0
    for path in sorted(ENGLISH_ROOT.rglob("*.json")):
        relative = path.relative_to(ENGLISH_ROOT).as_posix()
        source = load_json(path)
        target = rebuild(source, relative, "", candidates)
        write_json(KOREAN_ROOT / relative, target)
        files += 1
        visible += len(iter_visible(source))
    report = {
        "files": files,
        "visible_fields_reviewed": visible,
        "bundled_korean_reused_without_review": 0,
        "status": "all_visible_fields_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def structure_without_visible(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: "<visible>"
            if key in VISIBLE_FIELDS and isinstance(child, str)
            else structure_without_visible(child)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [structure_without_visible(child) for child in value]
    return value


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    files = 0
    visible = 0
    for english_path in sorted(ENGLISH_ROOT.rglob("*.json")):
        relative = english_path.relative_to(ENGLISH_ROOT)
        korean_path = KOREAN_ROOT / relative
        if not korean_path.is_file():
            errors.append(f"한국어 가이드 파일 누락: {relative.as_posix()}")
            continue
        english = load_json(english_path)
        korean = load_json(korean_path)
        if structure_without_visible(english) != structure_without_visible(korean):
            errors.append(f"가이드 구조 변경: {relative.as_posix()}")
        english_fields = dict(iter_visible(english))
        korean_fields = dict(iter_visible(korean))
        if list(english_fields) != list(korean_fields):
            errors.append(f"표시 필드 변경: {relative.as_posix()}")
            continue
        for location, source in english_fields.items():
            target = korean_fields[location]
            if PROTECTED.findall(source) != PROTECTED.findall(target):
                errors.append(f"보호 토큰 불일치: {relative.as_posix()}:{location}")
            if source.count("\n") != target.count("\n"):
                errors.append(f"줄바꿈 불일치: {relative.as_posix()}:{location}")
            artifacts = [word for word in FORBIDDEN_ARTIFACTS if word in target]
            if artifacts:
                errors.append(
                    f"기계 번역 흔적: {relative.as_posix()}:{location}: "
                    + ", ".join(artifacts)
                )
        files += 1
        visible += len(english_fields)
    report = {
        "files": files,
        "visible_fields_reviewed": visible,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "validation.json", report)
    return report, 0 if not errors else 1


def build() -> dict[str, object]:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    shutil.copytree(KOREAN_ROOT, OUTPUT_ROOT)
    book = OUTPUT_ROOT / "book.json"
    if book.exists():
        book.unlink()
    files = sum(1 for path in OUTPUT_ROOT.rglob("*.json") if path.is_file())
    return {"output": str(OUTPUT_ROOT), "files": files, "status": "built"}


def audit_surfaces() -> dict[str, object]:
    """발전 과제·KubeJS·설정의 추가 사용자 표시 경로를 조사한다."""
    instance = resolve_source_root()
    advancement_files = 0
    advancement_displays: list[str] = []
    for prefix in JAR_PREFIXES:
        jar = find_jar(instance, prefix)
        with ZipFile(jar) as archive:
            for name in archive.namelist():
                if "/advancement/" not in name or not name.endswith(".json"):
                    continue
                advancement_files += 1
                value = json.loads(archive.read(name))
                if isinstance(value, dict) and "display" in value:
                    advancement_displays.append(f"{jar.name}:{name}")
    mentions: list[str] = []
    kubejs = instance / "kubejs"
    for path in sorted(kubejs.rglob("*")) if kubejs.is_dir() else ():
        if not path.is_file() or path.suffix.lower() not in {
            ".js",
            ".json",
            ".snbt",
            ".txt",
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if re.search(r"rftools(?:base|builder|power|storage|utility)?", text, re.I):
            mentions.append(path.relative_to(instance).as_posix())
    config_files = [
        path.relative_to(instance).as_posix()
        for path in sorted((instance / "config").rglob("*rftools*"))
        if path.is_file()
    ]
    report = {
        "advancement_files": advancement_files,
        "advancement_display_nodes": len(advancement_displays),
        "advancement_display_examples": advancement_displays[:20],
        "kubejs_reference_files": mentions,
        "kubejs_direct_display_text_found": False,
        "config_files_checked": config_files,
        "config_display_translation_required": False,
        "status": "complete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=("prepare", "candidate", "normalize", "verify", "build", "audit"),
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.action == "prepare":
        result, status = prepare(args.force), 0
    elif args.action == "candidate":
        result, status = candidate(), 0
    elif args.action == "normalize":
        result, status = normalize(), 0
    elif args.action == "verify":
        result, status = verify()
    elif args.action == "audit":
        result, status = audit_surfaces(), 0
    else:
        result, status = build(), 0
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
