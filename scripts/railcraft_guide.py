#!/usr/bin/env python3
"""Railcraft Reborn Patchouli 가이드를 추출·번역·검증·빌드한다."""

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


WORK_ROOT = PROJECT_ROOT / "working/railcraft_reborn/guide"
ENGLISH_ROOT = WORK_ROOT / "en_us"
KOREAN_ROOT = WORK_ROOT / "ko_kr"
OUTPUT_ROOT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/railcraft/patchouli_books/guide_book/ko_kr"
)
BOOK_OUTPUT = (
    PROJECT_ROOT
    / "output/overrides/kubejs/data/railcraft/patchouli_books/guide_book/book.json"
)
CACHE_FILE = PROJECT_ROOT / "temp/railcraft_reborn_guide_candidate_cache.json"
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"
VISIBLE_FIELDS = {"name", "description", "text", "landing_text", "title"}

TERM_REPLACEMENTS = (
    ("RailCraft", "Railcraft"),
    ("레일크래프트", "Railcraft"),
    ("마인카트", "광산 수레"),
    ("카트", "광산 수레"),
    ("트랙", "선로"),
    ("철로", "선로"),
    ("레일", "레일"),
    ("크로우바", "쇠지렛대"),
    ("크로바", "쇠지렛대"),
    ("코크스 오븐", "코크스로"),
    ("코크 오븐", "코크스로"),
    ("롤링 머신", "압연기"),
    ("롤링 기계", "압연기"),
    ("스팀", "증기"),
    ("Steam", "증기"),
    ("파이어박스", "화실"),
    ("Firebox", "화실"),
    ("보일러 탱크", "보일러 탱크"),
    ("컨트롤러", "제어기"),
    ("수신기", "수신기"),
    ("액체", "유체"),
    ("아이템", "아이템"),
    ("엔터티", "엔티티"),
    ("레시피", "조합법"),
    ("선로을", "선로를"),
    ("선로으로", "선로로"),
    ("멀티 블록", "멀티블록"),
)

LOCATION_OVERRIDES: dict[str, str] = {
    "book.name": "Railcraft Reborn 가이드",
    "book.landing_text": (
        "Railcraft Reborn의 사용법을 설명하는 가이드입니다.$(br2)"
        "현재 베타 버전이며 새로운 분류가 추가될 예정입니다."
    ),
    "categories/multiblock.json:name": "멀티블록 구조",
    "categories/multiblock.json:description": "멀티블록 구조를 건설하고 사용하는 방법을 설명합니다.",
    "categories/signal_boxes.json:name": "신호 박스",
    "categories/signal_boxes.json:description": "신호 시스템을 제어하고 연동하는 여러 신호 박스를 설명합니다.",
    "categories/track_type.json:name": "선로 유형",
    "categories/track_type.json:description": (
        "선로는 레일과 노반의 종류에 따라 구분됩니다. 유형마다 속도, 전도성, 충돌, "
        "지지 블록 없이 놓을 수 있는지, 폭발 저항 같은 특성이 다릅니다."
    ),
    "categories/tracks.json:description": (
        "Railcraft는 Minecraft의 선로 종류를 크게 확장하고 제작 과정도 더 깊이 있게 "
        "바꿉니다. 침목으로 노반을 만든 뒤 레일과 결합해 여러 유형의 선로를 제작합니다."
    ),
    "entries/multiblock/blast_furnace.json:name": "용광로",
    "entries/multiblock/blast_furnace.json:pages[0].text": (
        "용광로는 가운데가 비어 있는 3x3x4 벽돌 구조로, 철 주괴를 강철 주괴로 "
        "바꿉니다.$(br2)네더 벽돌·영혼 모래·마그마 크림으로 만든 특수 벽돌 34개가 "
        "필요합니다. 재료로 환산하면 네더 벽돌 36개, 영혼 모래 36개, 마그마 크림 "
        "9개로 용광로 하나를 만들 수 있습니다. 용광로끼리는 붙여 지을 수 없으며 사이를 "
        "최소 한 블록 띄워야 합니다."
    ),
    "entries/multiblock/blast_furnace.json:pages[1].name": "용광로",
    "entries/multiblock/coke_oven.json:name": "코크스로",
    "entries/multiblock/coke_oven.json:pages[0].text": (
        "코크스로는 가운데가 비어 있는 3x3x3 벽돌 구조입니다. 석탄을 석탄 코크스로, "
        "목재를 숯으로 바꾸며 부산물로 크레오소트유를 만듭니다.$(br2)벽돌과 모래로 만든 "
        "특수 벽돌 26개가 필요합니다. 재료로 환산하면 점토 104개와 모래 130개로 "
        "코크스로 하나를 만들 수 있습니다. 코크스로끼리는 붙여 지을 수 없으며 사이를 "
        "최소 한 블록 띄워야 합니다."
    ),
    "entries/multiblock/coke_oven.json:pages[1].name": "코크스로",
    "entries/multiblock/coke_oven.json:pages[2].text": (
        "코크스로에는 크레오소트유 64,000단위를 저장할 수 있습니다. 양동이나 유리병으로 "
        "꺼낼 수 있으며, 각각 1,000단위를 담습니다. 채운 양동이는 겹칠 수 없지만 채운 "
        "유리병은 겹칠 수 있습니다.$(br2)석탄을 석탄 코크스로 바꾸는 데는 시간이 오래 "
        "걸립니다. 레일을 많이 만들 계획이라면 코크스로를 여러 개 건설하는 것이 좋습니다."
    ),
    "entries/multiblock/crusher.json:name": "암석 분쇄기",
    "entries/multiblock/crusher.json:pages[0].text": (
        "암석 분쇄기는 여러 재료를 가공하는 3x2x2 구조입니다. 강철 블록·피스톤·"
        "다이아몬드로 만든 특수 블록 12개로 건설합니다. 재료로 환산하면 강철 블록 3개, "
        "피스톤 12개, 다이아몬드 12개가 필요합니다. 암석 분쇄기끼리는 붙여 지을 수 "
        "없으며 사이를 최소 한 블록 띄워야 합니다."
    ),
    "entries/multiblock/crusher.json:pages[1].name": "암석 분쇄기",
    "entries/multiblock/iron_tank.json:pages[0].text": (
        "크레오소트유나 바이오 연료, 심지어 꿀까지 넘쳐나나요? 해결책이 있습니다!"
        "$(br2)산업 시설의 멋진 중심물이 될 철 탱크를 소개합니다!$(br2)"
        "크기는 3×3, 5×5, 7×7, 9×9의 네 종류이며 높이는 4블록부터 8블록까지 "
        "정할 수 있습니다. 원하는 크기에 맞춰 철 탱크 벽으로 틀을 만드세요."
    ),
    "entries/multiblock/iron_tank.json:pages[2].text": (
        "윗면·아랫면·옆면을 탱크 벽, 게이지, 밸브를 원하는 조합으로 채우세요."
        "$(br2)탱크를 쌓아 올릴 수도 있습니다. 두 탱크가 맞닿는 중앙에 밸브 블록을 "
        "각각 하나씩 놓으면 됩니다."
    ),
    "entries/multiblock/steam_boiler.json:pages[0].text": (
        "많은 산업 시설의 중심에는 촉수 달린 괴물 같은 증기 보일러가 있습니다. 복잡한 "
        "설비 전체의 에너지 수요를 감당할 만큼 증기를 생산합니다. 처음에는 어려워 보여도 "
        "직접 설치할 수 있도록 차근차근 설명하겠습니다!$(br2)증기 보일러를 지을 때 맨 "
        "아래층은 반드시 화실이어야 합니다. 화실은 두 종류입니다. 고체 연료 화실은 숯이나 "
        "석탄 코크스 같은 화로 연료를 태우고, 유체 연료 화실은 크레오소트유·바이오 연료·"
        "일반 연료 같은 유체를 사용합니다."
    ),
    "entries/multiblock/steam_boiler.json:pages[1].text": (
        "증기 보일러의 기본 바닥 크기는 소형 1×1, 주력 2×2, 대형 3×3의 세 가지입니다."
        "$(br2)화실을 놓은 뒤 그 위에 보일러 탱크를 쌓으세요. 탱크에는 저압과 고압 두 "
        "종류가 있습니다. 고압 보일러 탱크는 증기를 두 배로 생산하지만 저압 탱크가 보통 "
        "연료 효율은 더 좋습니다."
    ),
    "entries/multiblock/steam_boiler.json:pages[2].text": (
        "증기 보일러가 클수록 연료 효율이 좋아지므로 작은 보일러 여러 개보다 큰 보일러 "
        "하나가 대체로 낫습니다. 다만 보일러가 최고 온도에 도달하지 않는 짧은 운전에서는 "
        "최대 효율을 위해 고압보다 저압 보일러를 쓰는 편이 좋습니다. 계속 가동한다면 압력과 "
        "관계없이 연료 단위당 증기량은 같습니다.$(br2)만들 수 있는 탱크 크기는 화실 "
        "크기에 따라 달라집니다. 1×1 화실은 한 세제곱미터 탱크만, 2×2 화실은 8 또는 "
        "12세제곱미터 탱크를, 3×3 화실은 18, 27, 36세제곱미터 탱크를 사용할 수 있습니다."
    ),
    "entries/multiblock/steam_boiler.json:pages[3].text": (
        "증기 보일러를 완성하면 물과 연료를 공급해야 합니다. 주의: 탱크가 아니라 화실에 "
        "물이 끊기지 않도록 계속 공급하세요. 물이 마른 뜨거운 보일러에 다시 물을 넣으면 "
        "대형 폭발이 일어날 수 있습니다. 물 공급만 일정하면 보일러는 안전합니다."
    ),
    "entries/multiblock/steam_boiler.json:pages[4].text": (
        "보일러는 처음 가열할 때 매우 비효율적이며 최고 온도일 때보다 연료를 최대 8x 더 "
        "사용합니다. 쓰지 않을 때 끄기보다 계속 가동하는 편이 좋습니다. 특히 큰 보일러는 "
        "크기에 따라 가열 시간이 길어집니다."
    ),
    "entries/multiblock/steam_oven.json:pages[0].text": (
        "증기 오븐은 증기를 공급하면 아이템을 제련하는 2x2x2 구조입니다. 한 번에 최대 "
        "9개를 256틱, 즉 12.8초 만에 처리할 수 있습니다!"
    ),
    "entries/multiblock/steam_turbine.json:pages[0].text": (
        "증기는 넘치는데 쓸 곳이 없나요? 강력한 증기 터빈으로 증기를 전력으로 바꿀 수 "
        "있습니다.$(br2)암석 분쇄기와 같은 2x3x2 구조로 건설하며, 작동하려면 터빈 "
        "회전자를 설치해야 합니다. 회전자는 현실 시간으로 며칠 동안 계속 사용할 수 있고, "
        "두 회전자를 바닐라 수리 방식으로 합쳐 수리할 수 있습니다."
    ),
    "entries/multiblock/water_tank.json:name": "물 탱크",
    "entries/multiblock/water_tank.json:pages[0].text": (
        "물 탱크는 철도에 물을 공급하는 수동 설비로, 주변 환경에서 물을 모아 탱크를 "
        "채웁니다. 물 400양동이를 저장해 증기 기관차나 다른 물 소비 장치를 보충할 수 "
        "있습니다. 물이 차는 속도는 생물군계, 날씨, 하늘이 보이는 실외인지에 따라 "
        "달라집니다. 사막 횡단 철도에는 적합하지 않습니다.$(br2)코크스로와 비슷하게 물 "
        "탱크 측판으로 가운데가 빈 3x3x3 구조를 만드세요."
    ),
    "entries/signal_boxes/analog_signal_controller_box.json:pages[0].text": (
        "아날로그 신호 제어기 박스는 일반 제어기 박스와 달리 레드스톤 신호 세기에 따라 "
        "다른 신호 표시를 내보냅니다. 예를 들어 신호 세기 5에서는 녹색, 0에서는 "
        "빨간색을 내보내고 15에서는 꺼지도록 화면에서 설정할 수 있습니다."
    ),
    "entries/signal_boxes/signal_block_relay_box.json:pages[0].text": (
        "신호 블록 중계 박스는 다른 구간 신호기나 중계 박스 최대 두 개와 연결할 수 "
        "있습니다. 신호 구간의 끝을 막거나 구간을 연장하는 데 사용합니다. 연장기로 쓰면 "
        "신호 구간을 모퉁이 너머까지 이어 하나의 구간처럼 작동시킬 수 있습니다."
    ),
    "entries/signal_boxes/signal_block_relay_box.json:pages[1].text": (
        "중계 박스는 레드스톤 신호를 출력하도록 설정해 제어기 역할도 할 수 있습니다. 신호 "
        "수신기 박스와 마찬가지로 신호 제어기 박스나 신호 커패시터 박스 옆에 놓을 수도 있습니다."
    ),
    "entries/signal_boxes/signal_capacitor_box.json:pages[0].text": (
        "신호 커패시터 박스는 신호 수신기 박스나 신호 블록 중계 박스 옆에 놓습니다. 인접한 "
        "박스의 레드스톤 출력이 바뀌면 미리 정한 시간 동안 레드스톤 펄스를 냅니다. 개념은 "
        "RedPower의 State Cell과 비슷합니다."
    ),
    "entries/signal_boxes/signal_capacitor_box.json:pages[1].text": (
        "박스를 우클릭하면 화면이 열립니다. 현재 레드스톤 출력 지속 시간을 확인하고 조절할 "
        "수 있으며, 상승 에지와 하강 에지 모드를 바꾸는 버튼도 있습니다."
    ),
    "entries/signal_boxes/signal_capacitor_box.json:pages[2].text": (
        "상승 에지는 인접한 박스가 레드스톤 출력을 시작할 때 지정 시간 동안 펄스를 냅니다. "
        "하강 에지는 인접한 박스가 출력을 멈춘 뒤에도 지정 시간 동안 펄스를 유지해 지연 "
        "신호를 만듭니다."
    ),
    "entries/signal_boxes/signal_controller_box.json:pages[0].text": (
        "신호 제어기 박스는 신호 수신기 박스 옆에 놓아 수신기의 신호 표시를 연결된 장치로 "
        "보냅니다. 수신기 하나 옆에 제어기 여러 개를 놓으면 구간 신호기 하나로 여러 분기 "
        "모터나 원거리 신호기를 제어할 수 있습니다.$(br2)제어기 옆에 수신기 박스 두 개를 "
        "놓으면 둘 중 더 제한적인 신호 표시를 보냅니다. 레드스톤 신호를 공급해 화면에서 "
        "선택한 표시를 직접 내보낼 수도 있습니다."
    ),
    "entries/signal_boxes/signal_controller_box.json:pages[1].text": (
        "신호 수신기 박스가 직접 내보내는 레드스톤 전류로는 작동하지 않습니다. 대신 화면에서 "
        "선택한 표시와 수신기에서 받은 표시 중 항상 더 제한적인 것을 내보냅니다. 제어기 "
        "하나를 수신기 두 개에 연결할 수는 없습니다. 제어기 옆의 수신기는 정보를 제공할 "
        "뿐, 제어기끼리 직접 연결하지는 않습니다."
    ),
    "entries/signal_boxes/signal_receiver_box.json:pages[0].text": (
        "신호 수신기 박스는 어떤 제어기와도 연결할 수 있습니다. 연결한 뒤 화면에서 어떤 "
        "신호 표시일 때 레드스톤 전류를 출력할지 선택합니다. 신호 제어기 박스 옆에 놓으면 "
        "현재 신호 표시도 해당 박스로 전달합니다."
    ),
    "entries/tools/charge_meter.json:name": "전하 측정기",
    "entries/tools/charge_meter.json:pages[0].text": (
        "전하 측정기는 전기 기관차, 전력 공급 장치, 전기 선로처럼 전하를 사용하거나 "
        "전달하는 기계·전선·선로의 전하 흐름을 측정하는 Railcraft 도구입니다. 5초 "
        "동안 네트워크 사용량을 기록합니다."
    ),
    "entries/tools/crowbar.json:name": "쇠지렛대",
    "entries/tools/crowbar.json:pages[0].text": (
        "쇠지렛대는 모든 철도 기술자가 지녀야 할 다목적 도구입니다. 일반 레일을 빠르게 "
        "철거하고 감지기 블록이나 적재기에도 사용할 수 있습니다. 선로를 우클릭하면 보통 "
        "방향을 바꾸며, 일부 선로에서는 설정 화면을 엽니다. 감지기 블록·광산 수레 발사기·"
        "고급 적재기를 우클릭하면 클릭한 면을 향하도록 회전합니다."
    ),
    "entries/tools/crowbar.json:pages[1].text": (
        "쇠지렛대는 광산 수레와도 여러 방식으로 상호 작용합니다. 광산 수레를 우클릭하면 "
        "약간 밀어 주고, 기관차를 우클릭하면 진행 방향을 뒤집습니다. 웅크린 상태로 "
        "우클릭하면 광산 수레끼리 연결할 수 있습니다. 자세한 내용은 광산 수레 연결 항목을 "
        "참고하세요."
    ),
    "entries/tools/crowbar.json:pages[2].text": (
        "다이아몬드 쇠지렛대는 엔드 도시 상자에서 찾을 수 있습니다.$(br2)계절 쇠지렛대는 "
        "광산 수레를 연결하지 못하는 대신 광산 수레의 계절 장식을 바꿉니다. 작업장에서만 "
        "얻을 수 있습니다."
    ),
    "entries/tools/goggles.json:name": "선로 기술자의 고글",
    "entries/tools/goggles.json:pages[0].text": (
        "눈에 보이는 것이 세상의 전부는 아닙니다. 선로 기술자의 고글은 증강 현실로 평소 "
        "숨겨진 정보를 보여 줍니다. 월드를 유지하는 엔더 필드, 제어기와 수신기를 잇는 "
        "신호, 지난 30분 동안의 플레이어 이동 경로와 다른 플레이어까지 확인할 수 있습니다."
    ),
    "entries/tools/goggles.json:pages[1].text": (
        "고글은 한 번에 오라 하나만 표시하므로 보고 싶은 오라에 맞춰야 합니다. 손에 든 "
        "고글을 우클릭하거나, 고글을 착용한 상태에서 $(k:railcraft.change_aura) 키를 "
        "눌러 현재 오라를 바꿀 수 있습니다."
    ),
    "entries/tools/overalls.json:pages[0].text": (
        "작업복 없는 철도 기술자가 완성된 모습일까요? 그럴 리 없습니다!$(br2)최고의 "
        "방어구는 아니지만 선로 위에서 납작한 동전처럼 되는 사고를 어느 정도 막아 줍니다. "
        "정확한 원리는 몰라도 민첩성과 상황 인식을 높여 준다고 해 두죠."
    ),
    "entries/tools/overalls.json:pages[1].text": (
        "기관차에 부딪힐 때 받는 피해를 줄이고, 내구도를 소모해 전기 피해도 막아 줍니다."
    ),
    "entries/tools/signal_block_surveyor.json:name": "신호 구간 측량기",
    "entries/tools/signal_block_surveyor.json:pages[0].text": (
        "신호 구간 측량기는 구간 신호기 두 개를 연결해 하나의 신호 구간을 만듭니다. 첫 "
        "신호기를 우클릭해 측량을 시작한 뒤 반대쪽 신호기로 이동해 다시 우클릭하세요. "
        "유효한 구간이면 연결 성공 메시지가, 실패하면 이유를 알려 주는 메시지가 표시됩니다."
    ),
    "entries/tools/signal_tuner.json:name": "신호 조율기",
    "entries/tools/signal_tuner.json:pages[0].text": (
        "이 전자 주파수 스캐너는 제어기와 수신기를 연결합니다. 제어기를 우클릭한 뒤 연결할 "
        "수신기로 이동해 다시 우클릭하세요. 성공하면 화면에 메시지가 표시됩니다. 기존 "
        "연결을 지울 때도 제어기나 수신기를 우클릭해 사용할 수 있습니다."
    ),
    "entries/tools/whistle_tuner.json:name": "기적 조율기",
    "entries/tools/whistle_tuner.json:pages[0].text": (
        "기관차에 딱 맞는 기적 소리를 찾고 있나요? 이 도구를 들고 기관차를 한 번 치면 "
        "음높이를 바꿀 수 있습니다."
    ),
    "entries/track_type/abandoned.json:name": "버려진 선로",
    "entries/track_type/abandoned.json:pages[0].text": (
        "버려진 선로는 지지대 없이 매달아 놓을 수 있고 광산 수레가 탈선할 수 있으며, "
        "주변에 풀이 자라는 특징이 있습니다. 일반 레일과 목재 침목 하나로 만듭니다."
        "$(br2)철 선로보다 목재와 크레오소트유가 적게 들어서 자원이나 시간이 부족할 때 "
        "짧은 시간에 많은 선로를 놓기 좋습니다."
    ),
    "entries/track_type/abandoned.json:pages[1].text": (
        "버려진 선로에서는 광산 수레가 너무 빠르면 탈선할 수 있습니다. 속도가 틱당 "
        "0.35블록(7m/s, 일반 레일 제한 속도의 87.5%)을 넘으면 탈선 판정을 시작합니다. "
        "제한 속도를 넘긴 뒤 매 틱 .2% 확률로 탈선하며, 이 확률은 한 초에 4%, 거의 "
        "1/3까지 누적되는 데 10초가 걸립니다. 열차의 광산 수레 하나가 탈선하면 열차 "
        "전체가 탈선합니다."
    ),
    "entries/track_type/abandoned.json:pages[2].text": (
        "협곡을 건널 때 지지대 없이 이어 놓을 수 있어 유용합니다. 몹과 플레이어는 공중에 "
        "매달린 버려진 선로 위를 걸을 수 없습니다.$(br2)버려진 선로 주변에는 키 큰 풀이 "
        "자랍니다."
    ),
    "entries/track_type/high_speed.json:name": "고속 선로",
    "entries/track_type/high_speed.json:pages[0].text": (
        "고속 선로는 일반 선로와 조금 다릅니다. 광산 수레가 평소보다 2.5배 빠르게 달릴 "
        "수 있지만 직선 구간에서만 안전합니다. 이 속도는 설정에서 바꿀 수 있습니다. 속도를 "
        "먼저 줄이지 않고 선로를 벗어나거나 충돌하면 폭발합니다. 자세한 내용은 관련 항목을 "
        "확인하세요."
    ),
    "entries/track_type/iron.json:name": "철 선로",
    "entries/track_type/iron.json:pages[0].text": (
        "표준 철 선로는 바닐라 Minecraft 레일과 거의 같습니다. 표준 레일과 목재 노반으로 "
        "제작하며, 다른 Railcraft 유연 선로처럼 선로 키트를 설치할 수 있습니다."
    ),
    "entries/track_type/reinforced.json:name": "강화 선로",
    "entries/track_type/reinforced.json:pages[0].text": (
        "강화 선로는 철 선로보다 다음 장점이 있습니다.$(li)폭발 저항이 45로 높아 TNT "
        "폭발도 견딥니다.$(li)철 선로보다 25% 빠릅니다."
    ),
    "entries/track_type/reinforced.json:pages[1].text": (
        "고속 선로보다 훨씬 느리지만 훨씬 안전합니다.$(br2)다만 지지 블록이 사라지면 "
        "선로가 항상 떨어지므로 폭발 저항이 높은 블록 위에 설치하세요."
    ),
    "entries/track_type/strap_iron.json:name": "띠철 선로",
    "entries/track_type/strap_iron.json:pages[0].text": (
        "띠철 선로 또는 목재 선로는 제한 속도가 철 선로의 30%에 불과해 매우 느립니다. "
        "목재 레일과 목재 노반으로 제작합니다."
    ),
    "entries/track_type/strap_iron.json:pages[1].text": (
        "띠철 선로는 철 선로보다 철이 훨씬 적게 들지만 목재와 크레오소트유는 조금 더 "
        "필요합니다. 철이 부족할 때 좋고, 경치를 천천히 둘러보거나 정밀한 시간 조절이 "
        "필요한 구간에도 쓸 수 있습니다."
    ),
    "entries/tracks/buffer_stop_track.json:name": "완충 정지 선로",
    "entries/tracks/buffer_stop_track.json:pages[0].text": (
        "철도 노선 끝을 멋지게 마감하고 싶나요? 완충 정지 선로는 광산 수레가 선로 끝을 "
        "벗어나지 않게 확실히 멈춥니다. 광산 수레가 튕겨 나가거나 폭발하지도 않습니다."
    ),
    "entries/tracks/control_track.json:name": "제어 선로",
    "entries/tracks/control_track.json:pages[0].text": (
        "제어 선로는 한 방향으로만 광산 수레를 약하게 가속하고 반대 방향의 수레는 서서히 "
        "감속합니다. 전력을 공급하면 방향이 반대로 바뀝니다. 제작 비용이 낮고 양쪽으로 "
        "열여섯 블록까지 전력을 전달합니다. 기본 방향은 쇠지렛대로 바꿀 수 있습니다."
    ),
    "entries/tracks/coupler_track.json:name": "연결 선로",
    "entries/tracks/coupler_track.json:pages[0].text": (
        "연결 선로는 광산 수레를 열차로 연결하거나 분리합니다. 작동하려면 레드스톤 전력이 "
        "필요합니다. 선로를 우클릭하면 연결 모드와 연결 해제 모드를 전환합니다."
    ),
    "entries/tracks/coupler_track.json:pages[1].text": (
        "열차 감지기와 함께 사용하면 열차 전체를 한꺼번에 연결할 수 있습니다.$(br)"
        "쇠지렛대로 자동 연결 모드를 설정할 수도 있습니다. 이 모드에서는 다음에 충돌하는 "
        "광산 수레와 자동으로 연결되도록 광산 수레를 준비합니다."
    ),
    "entries/tracks/elevator_track.json:name": "승강 선로",
    "entries/tracks/elevator_track.json:pages[0].text": (
        "승강 선로는 벽에 수직으로 설치할 수 있습니다. 한 선로에 전력을 공급하면 아래쪽 "
        "선로에도 모두 전달됩니다. 전력이 있는 선로는 광산 수레를 위로 올리고, 전력이 없는 "
        "선로는 아래로 내립니다. 꼭대기에 도달하면 위 블록의 일반 선로로 밀어냅니다. "
        "사다리처럼 올라갈 수도 있습니다."
    ),
    "entries/tracks/gated_track.json:name": "차단문 선로",
    "entries/tracks/gated_track.json:pages[0].text": (
        "차단문 선로는 울타리 문 역할도 하며 손이나 레드스톤으로 열고 닫을 수 있습니다."
        "$(br)단방향 문은 광산 수레가 통과하면서 열리지만, 구역 안의 동물이 밀어 열고 "
        "나오지는 못하게 합니다."
    ),
    "entries/tracks/high_speed_booster_track.json:name": "고속 가속 선로",
    "entries/tracks/high_speed_booster_track.json:pages[0].text": (
        "전력이 있으면 광산 수레를 고속으로 가속하고, 전력이 없으면 일반 광산 수레 속도로 "
        "감속합니다.$(br2)고속 선로의 최대 속도에 도달하려면 이 선로나 고속 전환 선로가 "
        "필요합니다."
    ),
    "entries/tracks/high_speed_transition_track.json:name": "고속 전환 선로",
    "entries/tracks/high_speed_transition_track.json:pages[0].text": (
        "방향이 있는 고속 전환 선로입니다. 전력이 있으면 화살표 방향의 광산 수레를 "
        "가속합니다. 반대 방향으로 오는 수레는 전력이 있으면 일반 속도까지 감속하고, "
        "전력이 없으면 완전히 멈춥니다."
    ),
    "entries/tracks/launch_track.json:name": "발사 선로",
    "entries/tracks/launch_track.json:pages[0].text": (
        "발사 선로는 지나가는 광산 수레를 공중으로 날립니다. 쇠지렛대로 선로를 우클릭해 "
        "발사력을 조절할 수 있습니다.$(br2)광산 수레를 발사하려면 레드스톤 전력을 "
        "공급해야 합니다."
    ),
    "entries/tracks/launch_track.json:pages[1].text": (
        "현실적이지는 않지만 정말 재미있습니다! 발사 선로는 지나가는 광산 수레를 공중으로 "
        "날립니다. 쇠지렛대로 선로를 우클릭해 발사력을 조절할 수 있습니다.$(br2)"
        "광산 수레를 발사하려면 레드스톤 전력을 공급해야 합니다.$(br2)현실적이지는 "
        "않지만 정말 재미있습니다!"
    ),
    "entries/tracks/locking_track.json:name": "잠금 선로",
    "entries/tracks/locking_track.json:pages[0].text": (
        "전력이 없으면 지나가는 광산 수레를 붙잡아 둡니다. 동력 레일과 달리 수레를 밀어 "
        "낼 수 없습니다. 쇠지렛대로 선로를 때리면 모드를 바꿀 수 있으며 일부 모드는 선로에 "
        "화살표가 표시됩니다. 수레를 붙잡은 선로에 전력이 공급되면 화살표 방향으로 출발시킵니다."
    ),
    "entries/tracks/locking_track.json:pages[1].text": (
        "모드:$(li)잠금 모드 - 기본 모드입니다. 전력이 들어오면 광산 수레를 놓아 주지만 "
        "가속하지 않습니다.$(li)열차 잠금 모드 - 전력이 들어오면 열차 전체가 선로를 "
        "벗어나거나 다른 열차·광산 수레가 접근한 뒤 10초까지 전력을 유지합니다. 수레를 "
        "가속하지 않습니다.$(li)탑승 모드 - 전력이 들어오면 화살표 방향으로 수레를 가속합니다."
    ),
    "entries/tracks/locking_track.json:pages[2].text": (
        "모드:$(li)열차 탑승 모드 - 전력이 들어오면 열차 전체가 선로를 벗어나거나 다른 "
        "열차·광산 수레가 접근한 뒤 10초까지 전력을 유지하고 화살표 방향으로 가속합니다."
        "$(li)대기 모드 - 전력이 들어오면 잠기기 전에 달리던 방향으로 광산 수레를 "
        "가속합니다.$(li)열차 대기 모드 - 전력이 들어오면 열차 전체가 선로를 벗어나거나 "
        "다른 열차·광산 수레가 접근한 뒤 10초까지 전력을 유지하고 진행 방향으로 가속합니다."
    ),
    "entries/tracks/one_way_track.json:name": "단방향 선로",
    "entries/tracks/one_way_track.json:pages[0].text": (
        "전력이 없을 때는 일반 레일처럼 작동합니다. 전력이 들어오면 화살표 반대 방향으로 "
        "오는 광산 수레의 움직임을 되돌립니다. 방향을 바꾸는 과정에서 속도는 조금 줄어듭니다."
    ),
    "entries/tracks/turnout_track.json:name": "분기 선로",
    "entries/tracks/turnout_track.json:pages[0].text": (
        "분기 선로는 광산 수레를 한 선로에서 다른 선로로 보냅니다. 바닐라 Minecraft "
        "분기와 달리 좌우 중 하나를 고르는 대신 직진하거나 방향을 틀도록 선택합니다."
    ),
    "entries/tracks/turnout_track.json:pages[1].text": (
        "레드스톤으로 직접 조작할 수 없으므로 분기 모터를 분기 선로 반대편에 놓아야 합니다. "
        "수동으로만 바꾸려면 분기 레버를 쓸 수 있습니다.$(br2)광산 수레가 분기 쪽에서 "
        "접근하면 현재 설정과 관계없이 잠시 선로가 맞춰져 지나갈 수 있으며, 지나간 뒤 "
        "직접 원래대로 돌릴 필요가 없습니다."
    ),
    "entries/tracks/wye_track.json:name": "Y자 선로",
    "entries/tracks/wye_track.json:pages[0].text": (
        "Y자 선로는 광산 수레의 진행 방향을 바꾸는 좋은 방법입니다.$(br2)유연 선로를 "
        "스파이크 망치로 우클릭하면 가능한 형태를 순서대로 바꿀 수 있습니다. Y자 선로 "
        "키트는 기본적으로 분기 선로 키트 다음인 두 번째 형태입니다."
    ),
    "entries/tracks/wye_track.json:pages[1].text": (
        "분기 작동기로 제어할 수 있습니다. 레버는 수동, 모터는 신호·레드스톤, 라우팅 "
        "작동기는 라우팅 테이블을 사용합니다.$(br2)플레이어가 선로 키트를 부수면 아이템이 "
        "떨어지지 않고 유연 선로의 일부로 돌아갑니다."
    ),
}

FORBIDDEN = (
    "레시피",
    "컨트롤러",
    "파이어박스",
    "롤링 머신",
    "롤링 기계",
    "코크스 오븐",
    "터널 보어",
    "보어 헤드",
    "엔터티",
    "품목",
)


def read_json_bytes(raw: bytes, label: str) -> dict[str, object]:
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {label}")
    return value


def load_json(path: Path) -> dict[str, object]:
    return read_json_bytes(path.read_bytes(), str(path))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def jar_path() -> Path:
    mods = resolve_source_root() / "mods"
    matches = sorted(mods.glob("railcraft-reborn-*.jar"))
    if len(matches) != 1:
        raise RuntimeError(f"Railcraft JAR 수가 1개가 아닙니다: {matches}")
    return matches[0]


def walk_visible(value: object, location: str = "") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}" if location else key
            if key in VISIBLE_FIELDS and isinstance(child, str):
                rows.append((child_location, child))
            rows.extend(walk_visible(child, child_location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_location = f"{location}[{index}]"
            rows.extend(walk_visible(child, child_location))
    return rows


def replace_visible(
    value: object,
    translations: dict[str, str],
    location: str = "",
) -> object:
    if isinstance(value, dict):
        result: dict[str, object] = {}
        for key, child in value.items():
            child_location = f"{location}.{key}" if location else key
            if key in VISIBLE_FIELDS and isinstance(child, str):
                result[key] = translations[child_location]
            else:
                result[key] = replace_visible(child, translations, child_location)
        return result
    if isinstance(value, list):
        return [
            replace_visible(child, translations, f"{location}[{index}]")
            for index, child in enumerate(value)
        ]
    return value


def prepare(force: bool) -> dict[str, object]:
    if force:
        shutil.rmtree(ENGLISH_ROOT, ignore_errors=True)
        shutil.rmtree(KOREAN_ROOT, ignore_errors=True)
    files = 0
    visible = 0
    prefix = "assets/railcraft/patchouli_books/guide_book/en_us/"
    with ZipFile(jar_path()) as archive:
        names = sorted(
            name
            for name in archive.namelist()
            if name.startswith(prefix) and name.endswith(".json")
        )
        for name in names:
            relative = Path(name[len(prefix) :])
            value = read_json_bytes(archive.read(name), name)
            write_json(ENGLISH_ROOT / relative, value)
            if force or not (KOREAN_ROOT / relative).is_file():
                write_json(KOREAN_ROOT / relative, value)
            files += 1
            visible += len(walk_visible(value))
        book_name = "data/railcraft/patchouli_books/guide_book/book.json"
        book = read_json_bytes(archive.read(book_name), book_name)
        write_json(WORK_ROOT / "book_en_us.json", book)
        if force or not (WORK_ROOT / "book_ko_kr.json").is_file():
            write_json(WORK_ROOT / "book_ko_kr.json", book)
        visible += len(walk_visible(book, "book"))
    report = {"files": files, "visible_strings": visible, "bundled_korean": 0}
    write_json(WORK_ROOT / "scope.json", report)
    return report


def candidate() -> dict[str, object]:
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests: set[str] = set()
    documents: dict[str, dict[str, object]] = {}
    for path in sorted(ENGLISH_ROOT.rglob("*.json")):
        relative = path.relative_to(ENGLISH_ROOT).as_posix()
        value = load_json(path)
        documents[relative] = value
        for _, source in walk_visible(value):
            if not isinstance(cache.get(source), str):
                requests.add(source)
    book = load_json(WORK_ROOT / "book_en_us.json")
    documents["book.json"] = book
    for _, source in walk_visible(book, "book"):
        if not isinstance(cache.get(source), str):
            requests.add(source)

    failures: list[str] = []
    if requests:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(
                    candidate_helper.request_translation_candidate, source
                ): source
                for source in sorted(requests)
            }
            for completed, future in enumerate(as_completed(futures), start=1):
                source = futures[future]
                try:
                    cache[source] = future.result()
                    if completed % 20 == 0:
                        write_json(CACHE_FILE, cache)
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("가이드 후보 생성 실패:\n" + "\n".join(failures))

    rows: dict[str, dict[str, str]] = {}
    for relative, document in documents.items():
        base = "book" if relative == "book.json" else ""
        rows[relative] = {
            location: cache[source] for location, source in walk_visible(document, base)
        }
    write_json(CANDIDATE_FILE, rows)
    report = {
        "files": len(documents),
        "visible_strings": sum(len(row) for row in rows.values()),
        "status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


def normalize_text(location: str, value: str) -> str:
    value = LOCATION_OVERRIDES.get(location, value)
    for old, new in TERM_REPLACEMENTS:
        value = value.replace(old, new)
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    return value


def normalize_document(
    relative: str,
    english: dict[str, object],
    candidates: dict[str, str],
    base: str = "",
) -> dict[str, object]:
    translations: dict[str, str] = {}
    for location, source in walk_visible(english, base):
        override_location = location if base else f"{relative}:{location}"
        candidate_value = candidates[location]
        translations[location] = normalize_text(
            location if base else override_location, candidate_value
        )
    result = replace_visible(english, translations, base)
    if not isinstance(result, dict):
        raise TypeError(f"정규화 결과가 객체가 아닙니다: {relative}")
    return result


def normalize() -> dict[str, object]:
    candidates = load_json(CANDIDATE_FILE)
    changed = 0
    reviewed = 0
    for path in sorted(ENGLISH_ROOT.rglob("*.json")):
        relative = path.relative_to(ENGLISH_ROOT).as_posix()
        rows = candidates.get(relative)
        if not isinstance(rows, dict):
            raise TypeError(f"가이드 후보 파일이 없습니다: {relative}")
        english = load_json(path)
        target = normalize_document(relative, english, rows)
        korean_path = KOREAN_ROOT / relative
        previous = load_json(korean_path)
        if previous != target:
            changed += 1
        write_json(korean_path, target)
        reviewed += len(walk_visible(english))
    book_rows = candidates.get("book.json")
    if not isinstance(book_rows, dict):
        raise TypeError("book.json 후보가 없습니다.")
    book_english = load_json(WORK_ROOT / "book_en_us.json")
    book_target = normalize_document("book.json", book_english, book_rows, "book")
    if load_json(WORK_ROOT / "book_ko_kr.json") != book_target:
        changed += 1
    write_json(WORK_ROOT / "book_ko_kr.json", book_target)
    reviewed += len(walk_visible(book_english, "book"))
    report = {
        "visible_strings_reviewed": reviewed,
        "changed_files": changed,
        "existing_korean_reused_without_review": 0,
        "status": "all_current_english_strings_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def protected_tokens(value: str) -> list[str]:
    return re.findall(
        r"\$\([^)]*\)|%(?:\d+\$)?[A-Za-z%]|\\n|\d+(?:[.,]\d+)*(?:[xX×]\d+)?", value
    )


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    reviewed = 0
    untranslated: list[str] = []
    for english_path in sorted(ENGLISH_ROOT.rglob("*.json")):
        relative = english_path.relative_to(ENGLISH_ROOT)
        korean_path = KOREAN_ROOT / relative
        if not korean_path.is_file():
            errors.append(f"한국어 가이드 파일 누락: {relative.as_posix()}")
            continue
        english = load_json(english_path)
        korean = load_json(korean_path)
        english_rows = dict(walk_visible(english))
        korean_rows = dict(walk_visible(korean))
        if list(english_rows) != list(korean_rows):
            errors.append(f"표시 경로 불일치: {relative.as_posix()}")
            continue
        for location, source in english_rows.items():
            target = korean_rows[location]
            reviewed += 1
            if protected_tokens(source) != protected_tokens(target):
                errors.append(f"보호 토큰 불일치: {relative.as_posix()}:{location}")
            if source == target:
                untranslated.append(f"{relative.as_posix()}:{location}")
            artifacts = [word for word in FORBIDDEN if word in target]
            if artifacts:
                errors.append(
                    f"용어 미정리: {relative.as_posix()}:{location}: {', '.join(artifacts)}"
                )
    book_english = load_json(WORK_ROOT / "book_en_us.json")
    book_korean = load_json(WORK_ROOT / "book_ko_kr.json")
    for (location, source), (_, target) in zip(
        walk_visible(book_english, "book"),
        walk_visible(book_korean, "book"),
        strict=True,
    ):
        reviewed += 1
        if protected_tokens(source) != protected_tokens(target):
            errors.append(f"보호 토큰 불일치: {location}")
        if source == target:
            untranslated.append(location)
    if untranslated:
        errors.append(f"미번역 표시 문자열: {untranslated[:30]}")
    report = {
        "files": len(list(ENGLISH_ROOT.rglob("*.json"))) + 1,
        "visible_strings_reviewed": reviewed,
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "validation.json", report)
    return report, 1 if errors else 0


def build() -> dict[str, object]:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    shutil.copytree(KOREAN_ROOT, OUTPUT_ROOT)
    book = load_json(WORK_ROOT / "book_ko_kr.json")
    write_json(BOOK_OUTPUT, book)
    return {
        "localized_files": len(list(KOREAN_ROOT.rglob("*.json"))),
        "book_file": BOOK_OUTPUT.relative_to(PROJECT_ROOT).as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("prepare", "candidate", "normalize", "verify", "build")
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.force)
        status = 0
    elif args.command == "candidate":
        result = candidate()
        status = 0
    elif args.command == "normalize":
        result = normalize()
        status = 0
    elif args.command == "verify":
        result, status = verify()
    else:
        result = build()
        status = 0
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
