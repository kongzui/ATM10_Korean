"""Immersive Engineering 공학자의 설명서 114쪽을 번역하고 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from zipfile import ZipFile

from immersive_engineering_family import NAME_TRANSLATIONS, REVIEWED_VALUE_TRANSLATIONS
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root


WORK_ROOT = PROJECT_ROOT / "working/immersive_engineering/manual"
ENGLISH_ROOT = WORK_ROOT / "en_us"
KOREAN_ROOT = WORK_ROOT / "ko_kr"
OUTPUT_ROOT = (
    active_output_root()
    / "resourcepack/ATM10_Korean/assets/immersiveengineering/manual/ko_kr"
)
CACHE_FILE = PROJECT_ROOT / "temp/immersive_engineering_manual_machine_cache.json"
MANUAL_PREFIX = "assets/immersiveengineering/manual/en_us/"
TAG_RE = re.compile(r"<[^>]*>|∽.|https?://\S+")
FORMAT_CODE_RE = re.compile(r"§[0-9a-fk-or]", re.IGNORECASE)
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
LATIN_WORD_RE = re.compile(r"[A-Za-z]{3,}")
COMMON_ENGLISH_WORDS = {
    "and",
    "are",
    "can",
    "does",
    "for",
    "from",
    "have",
    "into",
    "not",
    "only",
    "the",
    "this",
    "will",
    "with",
    "your",
}

TERM_TRANSLATIONS = {
    "Immersive Engineering": "Immersive Engineering",
    "Engineer's Manual": "공학자의 설명서",
    "Engineer's Workbench": "공학자의 작업대",
    "Engineer's Hammer": "공학자의 망치",
    "Engineer's Screwdriver": "공학자의 드라이버",
    "Engineer's Wire Cutters": "공학자의 전선 절단기",
    "Accumulator Backpack": "축전기 배낭",
    "Accumulators": "축전기",
    "Accumulator": "축전기",
    "Chemical Thrower": "화학 분사기",
    "Heavy Plated Shield": "중장갑 방패",
    "Automated Engineer's Workbench": "자동 공학자의 작업대",
    "Light Engineering Block": "경공학 블록",
    "Heavy Engineering Block": "중공학 블록",
    "Redstone Engineering Block": "레드스톤 공학 블록",
    "Treated Wood": "방부목",
    "Metal Press": "금속 프레스",
    "Arc Furnace": "아크로",
    "Crude Blast Furnace": "조잡한 용광로",
    "Improved Blast Furnace": "개량 용광로",
    "Coke Oven": "코크스로",
    "Alloy Kiln": "합금 가마",
    "Garden Cloche": "원예용 온실",
    "Kinetic Dynamo": "운동 에너지 발전기",
    "Current Transformer": "전류 변성기",
    "Thermoelectric Generator": "열전 발전기",
    "Structural Arm": "구조 지지대",
    "Structural Connector": "구조 연결기",
    "Structural Cable": "구조 케이블",
    "Sheetmetal": "판금",
    "Steel Scaffolding": "강철 비계",
    "Aluminium Scaffolding": "알루미늄 비계",
    "Aluminum Scaffolding": "알루미늄 비계",
    "Wire Coil": "전선 코일",
    "Connector": "연결기",
    "Relay": "릴레이",
    "Conveyor Belt": "컨베이어 벨트",
    "Fluid Pipe": "유체 파이프",
    "Fluid Pump": "유체 펌프",
    "Mining Drill": "채굴 드릴",
    "Sawblade": "톱날",
    "Buzzsaw": "원형톱",
    "Railgun": "레일건",
    "Revolver": "리볼버",
    "Skyhook": "스카이훅",
    "Shader": "셰이더",
    "Blueprint": "설계도",
    "Creosote Oil": "크레오소트유",
    "Plant Oil": "식물성 기름",
    "Biodiesel": "바이오디젤",
    "Bio-Diesel": "바이오디젤",
    "Redstone Acid": "레드스톤 산",
    "HOP Graphite": "HOP 흑연",
    "Constantan": "콘스탄탄",
    "Electrum": "일렉트럼",
    "Aluminium": "알루미늄",
    "Aluminum": "알루미늄",
}

LINK_LABEL_OVERRIDES = {
    "Accumulator": "축전기",
    "Accumulators": "축전기",
    "HV Accumulators": "HV 축전기",
    "high-voltage architecture": "고전압 설비",
    "wire connectors and relays": "전선 연결기와 릴레이",
    "wires": "전선",
    "§o§nBottling §o§nMachine§r": "§o§n병입기§r",
    "eponymous tool": "같은 이름의 도구",
    "Crusher": "분쇄기",
    "crushing": "분쇄",
    "lanterns": "랜턴",
    "Vacuum Tubes": "진공관",
    "electron tube": "진공관",
    "backplanes": "회로 백플레인",
    "simpler sisters": "더 단순한 기계",
    "most advanced": "가장 고급인 기계",
    "Industrial Squeezer": "압착기",
    "preservative for wood": "목재 방부제",
    "duroplast items": "듀로플라스트 아이템",
    "minerals": "광물",
    "fluid barrels": "유체 저장 통",
    "barrels": "통",
    "Wooden Barrel": "나무 통",
    "minecarts": "광산 수레",
    "Sulfur": "황",
    "creating steel": "강철 생산",
    "steel production": "강철 생산",
    "Mineral Vein": "광맥",
    "molds": "주형",
    "other engineers": "다른 공학자들",
    "Posts": "기둥",
    "posts": "기둥",
    "storage shelf": "저장 선반",
    "Storage Crates": "저장 상자",
    "crates": "상자",
    "Storage Barrels": "저장 통",
    "Tough Fabric": "질긴 천",
    "check here": "여기에서 확인",
    "manual entry": "설명서 항목",
    "Redstone Wires": "레드스톤 전선",
    "redstone wires": "레드스톤 전선",
    "Redstone Interface Connector": "레드스톤 인터페이스 연결기",
    "Redstone Interface Connectors": "레드스톤 인터페이스 연결기",
    "redstone interface connector": "레드스톤 인터페이스 연결기",
    "scaffolding": "비계",
    "§2sawblades§r": "§2톱날§r",
    "sawblade": "톱날",
    "Revolver's cartridges": "리볼버 탄약통",
    "Revolver's": "리볼버",
    "Revolvers": "리볼버",
    "Drills": "드릴",
    "Chemical Throwers": "화학 분사기",
    "Heavy Plated Shields": "중장갑 방패",
    "Railguns": "레일건",
    "Accumulator Backpacks": "축전기 배낭",
    "Advanced Electronic Components": "고급 전자 부품",
    "Circuit Backplanes": "회로 백플레인",
    "Squeezer": "압착기",
    "Fluid Router": "유체 라우터",
    "Item Router": "아이템 라우터",
    "Machine Interface": "기계 인터페이스",
    "Mineral Deposits": "광물 매장지",
    "Thermoelectric Generators": "열전 발전기",
    "Thermoelectric Generator": "열전 발전기",
    "Plant Oil and Ethanol": "식물성 기름과 에탄올",
    "duroplast sheets": "듀로플라스트 판",
    "Fiberboard": "섬유판",
}

MANUAL_REPLACEMENTS = (
    ("어큐뮬레이터", "축전기"),
    ("커넥터", "연결기"),
    ("릴레이션", "릴레이"),
    ("엔지니어의", "공학자의"),
    ("엔지니어 작업대", "공학자의 작업대"),
    ("엔지니어링 블록", "공학 블록"),
    ("액체", "유체"),
    ("크레오소트 오일", "크레오소트유"),
    ("바이오 디젤", "바이오디젤"),
    ("쉐이더", "셰이더"),
    ("원형 톱", "원형톱"),
    ("화학 투척기", "화학 분사기"),
    ("금속 압착기", "금속 프레스"),
    ("버즈소", "원형톱"),
    ("전기톱", "원형톱"),
    ("블레이드", "톱날"),
    ("화학투척기", "화학 분사기"),
    ("석탄 콜라", "석탄 코크스"),
    ("Vertical 컨베이어 벨트", "수직 컨베이어 벨트"),
    ("표준 컨베이어 벨트와 같은 can.", "표준 컨베이어 벨트처럼 이동시킬 수 있습니다."),
    ("§2도끼§r 캔처럼", "§2도끼§r처럼"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("살짝 + 오른쪽 클릭", "Shift+우클릭"),
    ("제작법를", "제작법을"),
    ("질긴 천는", "질긴 천은"),
    ("Jump 쿠션", "점프 쿠션"),
    ("Ersatz 가죽", "대체 가죽"),
    ("원형톱는", "원형톱은"),
    ("스카이훅는", "스카이훅은"),
    ("스카이훅를", "스카이훅을"),
    ("크레오소트유은", "크레오소트유는"),
    ("에탄올는", "에탄올은"),
    ("식물성 기름는", "식물성 기름은"),
    ("섬유판는", "섬유판은"),
    ("포탄는", "포탄은"),
    ("물약는", "물약은"),
    ("콘스탄탄와", "콘스탄탄과"),
    ("사용하십시오", "사용하세요"),
    ("두십시오", "두세요"),
    ("마십시오", "마세요"),
    ("레시피", "제작법"),
    ("데미지", "피해"),
    ("항목", "아이템"),
    ("재고", "인벤토리"),
    ("퍼니스", "용광로"),
    ("몰래 + 우클릭", "Shift+우클릭"),
    ("몰래 우클릭", "Shift+우클릭"),
    ("몰래 누른 채 우클릭", "Shift+우클릭"),
    ("블록를", "블록을"),
    ("톱날를", "톱날을"),
    ("알루미늄로", "알루미늄으로"),
    ("방부목로", "방부목으로"),
    ("변압기s§r", "변압기§r"),
    ("띠 커튼는", "띠 커튼은"),
    ("작업 시 극 사이", "손에 든 채 두 전봇대 사이"),
    ("우클릭", "우클릭"),
)

TITLE_OVERRIDES = {
    "automated_engineers_workbench.txt": "자동 공학자의 작업대",
    "catwalks.txt": "캣워크",
    "coke_and_graphite.txt": "코크스와 흑연",
    "crafting_components.txt": "제작 부품",
    "crusher.txt": "분쇄기",
    "engineered_lighting.txt": "공학 조명",
    "engineers_circuit_workbench.txt": "공학자의 회로 작업대",
    "excavator.txt": "굴착기",
    "external_heater.txt": "외부 가열기",
    "kinetic_generators.txt": "운동 에너지 발전기",
    "mixer.txt": "혼합기",
    "other_engineers.txt": "다른 공학자들",
    "razor_wire.txt": "철조망",
    "revolver_cartridges.txt": "리볼버 탄약통",
    "sawmill.txt": "제재기",
    "signs.txt": "표지판",
    "storage_barrels.txt": "저장 통",
    "storage_crates.txt": "저장 상자",
    "storage_shelf.txt": "저장 선반",
}

FILE_REPLACEMENTS = {
    "alloy_kiln.txt": (
        ("Kiln을 형성", "합금 가마를 완성"),
        ("Kiln 벽돌", "가마 벽돌"),
    ),
    "accumulators.txt": (
        ("측면당 축전기 전압의 연결기 하나", "각 면에 연결된 해당 전압의 연결기 하나"),
        ("몰래 이동하면", "몸을 숙이면"),
    ),
    "assembler.txt": (
        ("제작법를", "제작법을"),
        ("제작법가", "제작법이"),
        ("제작대와 동일한 버킷으로 지정됩니다", "제작대에서처럼 양동이로 표시됩니다"),
    ),
    "automated_engineers_workbench.txt": (
        ("세부 아이템을 조립", "여러 아이템을 조립"),
        ("도면 테이블", "설계도 슬롯"),
        ("생성해야 할 아이템", "만들 아이템"),
    ),
    "basic_metal_products.txt": (
        ("모래 또는 합금 용광로", "합금 가마나 아크로"),
        ("구조 엔지니어링", "구조 공학"),
        ("주괴를 망치로 두드려 만들어집니다", "주괴를 두드려 만듭니다"),
        ("로 제작하거나 제작할 수 있습니다", "에서 만들거나 직접 제작할 수 있습니다"),
        ("플레이트", "판"),
        ("와이어는", "전선은"),
    ),
    "basic_tools.txt": (
        ("기계를 구성하고 형성", "기계의 설정을 바꾸고 멀티블록을 완성"),
        ("또 다른 일반적인 아이템", "또 하나의 기본 공구"),
        ("연결을 측정", "전력망을 측정"),
        ("에너지 저장소를 겨냥하거나 우클릭하면", "에너지 저장 장치를 우클릭하면"),
    ),
    "balloon.txt": (
        ("물에 떠있게 유지", "공중에 떠 있도록"),
        ("살짝 클릭하면", "몸을 숙인 채 설치하면"),
        ("몰래 풍선을 우클릭", "풍선을 Shift+우클릭"),
    ),
    "arc_furnace.txt": (
        (
            "이에 대한 예는 Steel.<br>를 만들기 위해 녹는 철에 코크스 가루를 추가하는 것입니다.",
            "예를 들어 강철을 만들 때는 용융 철에 코크스 가루를 추가합니다.<br>",
        ),
    ),
    "coke_and_graphite.txt": (
        ("Coal Coke는", "석탄 코크스는"),
        ("HOP 흑연 Dust", "HOP 흑연 가루"),
        ("그 먼지", "그 가루"),
    ),
    "coke_oven.txt": (("§oslow§r이지만", "§o느리지만§r"),),
    "crude_blast_furnace.txt": (
        (
            "철의 탄소 함량을 높여 TD LINK STEEL.<br>로 바꾸는",
            "철의 탄소 함량을 높여 강철로 바꾸는<br>",
        ),
        (
            "공학자의 망치가 있는 측면의 중앙 블록 중 하나를 우클릭합니다",
            "공학자의 망치로 측면 중앙 블록 중 하나를 우클릭합니다",
        ),
    ),
    "engineers_circuit_workbench.txt": (
        (
            "공학자의 회로 작업대연기를 흡입하지 마십시오\nCircuit Workbench",
            "공학자의 회로 작업대\n연기를 들이마시지 마세요\n회로 작업대",
        ),
        ("Redstone 와이어", "레드스톤 전선"),
        ("Circuit Workbench를", "회로 작업대를"),
    ),
    "engineers_skyhook.txt": (("§owill§r 사용자에게", "사용자에게 §o반드시§r"),),
    "engineers_toolbox.txt": (
        ("'Food' 및 'Anything'", "'음식'과 '기타'"),
        ("'Wiring' 슬롯", "'배선' 슬롯"),
    ),
    "engineers_workbench.txt": (("Workbench의 두 번째 기능", "작업대의 두 번째 기능"),),
    "catwalks.txt": (("Catwalk는", "캣워크는"),),
    "clinker_brick.txt": (
        ("§2Smoker§r", "§2훈연기§r"),
        ("§2클링커 벽돌 모서리s§r", "§2클링커 벽돌 모서리§r"),
        ("§2Sills§r", "§2클링커 벽돌 창턱§r"),
        ("외관의 외관", "건물 외관"),
    ),
    "concrete.txt": (("§2Stonecutter§r", "§2석재 절단기§r"),),
    "crafting_components.txt": (
        ("§2Iron§r 및 §2강철 기계 부품s§r", "§2철 기계 부품§r과 §2강철 기계 부품§r"),
        ("§2전자 부품s§r", "§2전자 부품§r"),
        ("§2백열전구s§r", "§2백열전구§r"),
    ),
    "engineered_lighting.txt": (
        ("Cage 램프", "케이지 램프"),
        ("Floodlights는", "투광 조명등은"),
        ("전원 랜턴", "전동 랜턴"),
        ("이를 실행하려면", "작동시키려면"),
        (
            "공학자의 망치를 사용하면 거꾸로 뒤집어집니다",
            "공학자의 망치로 우클릭하면 위아래 방향이 바뀝니다",
        ),
        ("투광등을 실행하려면", "투광 조명등을 작동시키려면"),
    ),
    "fermenter.txt": (("발효조(Fermenter)는", "산업용 발효기는"),),
    "fluid_router.txt": (
        ("Fluid Router는 yhr", "유체 라우터는"),
        ("유체 입력은", "입력된 유체는"),
    ),
    "improved_blast_furnace.txt": (
        ("Furnace의 구조", "용광로의 구조"),
        ("각 퍼니스에는", "각 용광로에는"),
    ),
    "industrial_hemp.txt": (
        ("Industrial Hemp는", "산업용 대마는"),
        (
            "LINK TO GO HERE(식물유) 생성에 사용될 수 있습니다",
            "식물성 기름을 만드는 데 사용할 수 있습니다",
        ),
        ("식물성 오일", "식물성 기름"),
    ),
    "shaders.txt": (
        ("항목의 디자인", "아이템의 외형"),
        ("(및 아직 발견해야 할 다른 것)", "(그리고 아직 발견하지 못한 다른 장비)"),
        ("여기에서 확인>를", "여기에서 확인>을"),
        ("가방 사용시", "꾸러미를 사용할 때"),
        ("셰이더의 가방", "셰이더 꾸러미"),
    ),
    "slag_products.txt": (
        (
            "다른 블록에서 자랄 때보다 더 빨리 자란다",
            "다른 블록에서보다 더 빨리 자랍니다",
        ),
        ("§2로§r에서", "§2용광로§r에서"),
        ("§2슬래그 유리§r.<br>가 됩니다", "§2슬래그 유리§r가 됩니다.<br>"),
    ),
    "silo.txt": (
        ("품목", "아이템"),
        ("사일로의 채우기에 비례하여", "사일로가 찬 정도에 비례하여"),
        ("상위 6개 레이어", "위쪽 6개 층"),
    ),
    "siren.txt": (
        ("중장비 소음을 통해", "중장비 소리를 뚫고 들릴 만큼"),
        ("레드스톤 전선>.<br>와", "레드스톤 전선>에<br>"),
    ),
    "squeezer.txt": (
        ("멀티블록 구조이다", "멀티블록 구조입니다"),
        ("위와 같이 제작되었으며", "그림처럼 조립하고"),
        ("형성되었습니다", "완성합니다"),
        ("프로세스", "공정"),
        ("품목", "아이템"),
    ),
    "storage_barrels.txt": (
        ("유체 버킷", "유체 양동이"),
        ("배럴", "통"),
    ),
    "storage_crates.txt": (
        ("Shulker 상자", "셜커 상자"),
        ("자재 스택", "아이템 묶음"),
        ("충전량", "저장량"),
        ("장기간 상자에", "상자에 일정 시간 동안"),
        ("파손될 수 없음을", "부서지지 않음을"),
    ),
    "storage_shelf.txt": (
        ("보관 선반", "저장 선반"),
        ("별도의 선반이 있습니다", "별도의 보관 공간입니다"),
        ("전체 상자 라인", "상자 한 줄 전체"),
    ),
    "strip_curtains.txt": (("강력한 신호를 활성화", "강한 신호를 출력하도록 설정"),),
    "tank.txt": (
        ("유체 버킷", "유체 양동이"),
        ("상위 4개 레이어", "위쪽 4개 층"),
    ),
    "transformers.txt": (
        ("HV.<br>로", "HV로<br>"),
        ("LV와 HV 사이를 직접 이동", "LV와 HV 사이를 직접 변환"),
    ),
    "treated_wood.txt": (
        (
            "크레오소트유;creosote_oil>.<br>가 함침된",
            "크레오소트유;creosote_oil>를<br>스며들게 한",
        ),
        ("단순함에도 불구하고", "간단한 재료지만"),
    ),
    "windows.txt": (
        ("위더(Wither) 수준", "위더 수준"),
        ("프레임 유리창", "틀이 있는 유리창"),
        ("판>로", "판>으로"),
    ),
    "jerrycan.txt": (("<&recipe>Jerrycan은", "<&recipe>제리캔은"),),
    "item_router.txt": (
        ("분류하고 분류하도록", "분류하도록"),
        ("§2Damage 필터§r", "§2피해 필터§r"),
    ),
    "other_engineers.txt": (
        ("§l구조 엔지니어§r", "§l구조 공학자§r"),
        ("Machinist의", "기계 기술자의"),
        ("Gunsmith의", "총기 제작자의"),
        ("§lOutfitter§r", "§l의상 제작자§r"),
        ("Outfitter의", "의상 제작자의"),
        ("§l기계공§r", "§l기계 기술자§r"),
        ("§l전기기사§r", "§l전기 기술자§r"),
        ("§l총제작자§r", "§l총기 제작자§r"),
    ),
    "pipe_valve.txt": (
        (
            "<&pump_recipe>Pipe 밸브는 <link;fluid_pipes;pipe>.<br>의 실행에 대한 유체 흐름을 제어하는 redsto- 기계식 장치입니다.",
            "<&pump_recipe>파이프 밸브는 <link;fluid_pipes;pipe>를 지나는 유체 흐름을 제어하는 레드스톤 기계 장치입니다.<br>",
        ),
    ),
    "razor_wire.txt": (
        ("Razorwire는", "철조망은"),
        ("Razorwire는 전선", "철조망은 전선"),
        ("면도날에 전기를 공급", "철조망에 전기를 공급"),
    ),
    "redstone_probe.txt": (
        ("§lCrusher: §r", "§l분쇄기: §r"),
        ("§lSqueezer: §r", "§l압착기: §r"),
    ),
    "redstone_state_cells.txt": (("§lSet: §r", "§l설정: §r"),),
    "revolver_cartridges.txt": (
        ("§lEmpty §lCasings§r 및 §lShells§r", "§l빈 탄피§r와 §l빈 포탄§r"),
        ("Bullet Casing 금형", "탄피 주형"),
        ("§lCasull §lCartridges§r", "§l카슐 탄약통§r"),
        ("§l벅샷 §l카트리지§r", "§l산탄 포탄§r"),
        ("§l실버 §l카트리지§r", "§l은탄 탄약통§r"),
        ("§l고폭성 §l카트리지§r", "§l고폭탄 탄약통§r"),
        ("§l드래곤의 §l호흡 카트리지§r", "§l드래곤의 숨결 포탄§r"),
        ("Buckshot과", "산탄과"),
        ("§lPhial §lCartridges§r", "§l약병탄 탄약통§r"),
        (
            "Lingering 물약은 일시적인 Linging 물약 구름",
            "잔류형 물약은 일시적인 잔류형 물약 구름",
        ),
        ("§l플레어 §l카트리지§r", "§l조명탄 포탄§r"),
        ("§l호밍 §l카트리지§r", "§l유도탄 탄약통§r"),
        ("§lWolfpack §lCartridges§r", "§l울프팩 탄약통§r"),
    ),
    "resin_and_duroplast.txt": (
        ("Duroplast는", "듀로플라스트는"),
        ("Duroplast 품목", "듀로플라스트 아이템"),
    ),
    "scaffolding_and_ladders.txt": (("Scaffolding은", "비계는"),),
}


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def installed_jar() -> Path:
    matches = sorted(
        (resolve_source_root() / "mods").glob("ImmersiveEngineering-*.jar")
    )
    if len(matches) != 1:
        raise FileNotFoundError(f"Immersive Engineering JAR 개수 불일치: {matches}")
    return matches[0]


def extract() -> dict[str, object]:
    jar = installed_jar()
    files = {}
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            if not name.startswith(MANUAL_PREFIX) or not name.endswith(".txt"):
                continue
            relative = name.removeprefix(MANUAL_PREFIX)
            content = (
                archive.read(name)
                .decode("utf-8")
                .replace("\r\n", "\n")
                .replace("\r", "\n")
            )
            files[relative] = content
    if len(files) != 114:
        raise ValueError(f"설명서 영어 원문 파일 수 불일치: {len(files)}")
    ENGLISH_ROOT.mkdir(parents=True, exist_ok=True)
    for relative, content in files.items():
        path = ENGLISH_ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    report = {
        "jar": jar.name,
        "pages": len(files),
        "source_sha256": sha256(jar.read_bytes()),
        "source_bytes": sum(len(value.encode("utf-8")) for value in files.values()),
    }
    write_json(WORK_ROOT / "scope.json", report)
    return report


def translation_terms() -> list[tuple[str, str]]:
    terms = dict(TERM_TRANSLATIONS)
    for source, target in {**NAME_TRANSLATIONS, **REVIEWED_VALUE_TRANSLATIONS}.items():
        if (
            isinstance(source, str)
            and isinstance(target, str)
            and 2 <= len(source) <= 60
            and "\n" not in source
            and not source.startswith("§")
        ):
            terms.setdefault(source, target)
    return sorted(terms.items(), key=lambda item: len(item[0]), reverse=True)


def protect_text(text: str) -> tuple[str, dict[str, str]]:
    protected: dict[str, str] = {}

    def reserve(value: str) -> str:
        token = f"ZXQ{len(protected):04d}QXZ"
        protected[token] = value
        return token

    text = TAG_RE.sub(lambda match: reserve(match.group()), text)
    for source, target in translation_terms():
        if source in text:
            text = text.replace(source, reserve(target))
    return text, protected


def restore_text(text: str, protected: dict[str, str]) -> str:
    for token, value in protected.items():
        if token not in text:
            raise ValueError(f"번역 후보에서 보호 토큰이 사라졌습니다: {token}")
        text = text.replace(token, value)
    if "ZXQ" in text:
        raise ValueError("번역 후보에 복원되지 않은 보호 토큰이 있습니다.")
    return text


def translate_link_label(label: str, cache: dict[str, str]) -> str:
    if label in LINK_LABEL_OVERRIDES:
        translated = LINK_LABEL_OVERRIDES[label]
    elif label in TERM_TRANSLATIONS:
        translated = TERM_TRANSLATIONS[label]
    elif not re.search(r"[A-Za-z]", label):
        translated = label
    else:
        protected_label, protected = protect_text(label)
        cache_key = "label:" + sha256(protected_label.encode("utf-8"))
        if cache_key not in cache:
            cache[cache_key] = request_translation(protected_label)
            time.sleep(0.12)
        translated = restore_text(cache[cache_key], protected)
    for old, new in MANUAL_REPLACEMENTS:
        translated = translated.replace(old, new)
    return translated


def localize_visible_tags(value: str, cache: dict[str, str]) -> str:
    def replace_link(match: re.Match[str]) -> str:
        parts = match.group()[1:-1].split(";")
        if len(parts) >= 3:
            parts[2] = translate_link_label(parts[2], cache)
        return "<" + ";".join(parts) + ">"

    value = re.sub(r"<link;[^>]+>", replace_link, value)
    value = value.replace(
        "<config;b;tools.chemthrower.scroll;"
        "sneaking and using the scrollwheel, or through use of;using>",
        "<config;b;tools.chemthrower.scroll;" "몸을 숙인 채 스크롤하거나;사용하여>",
    )
    return value


def request_translation(text: str) -> str:
    query = urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": "ko", "dt": "t", "q": text}
    )
    request = urllib.request.Request(
        "https://translate.googleapis.com/translate_a/single?" + query,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return "".join(row[0] for row in payload[0] if row[0])
        except Exception:
            if attempt == 4:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise AssertionError("도달할 수 없는 코드")


def translate_segment(segment: str, cache: dict[str, str]) -> str:
    if not re.search(r"[A-Za-z]", TAG_RE.sub("", segment)):
        return segment
    protected_text, protected = protect_text(segment)
    cache_key = sha256(protected_text.encode("utf-8"))
    if cache_key not in cache:
        cache[cache_key] = request_translation(protected_text)
        write_json(CACHE_FILE, cache)
        time.sleep(0.12)
    try:
        return restore_text(cache[cache_key], protected)
    except ValueError:
        cache[cache_key] = split_translation(protected_text, protected, cache)
        write_json(CACHE_FILE, cache)
        return restore_text(cache[cache_key], protected)


def split_translation(
    protected_text: str, protected: dict[str, str], cache: dict[str, str]
) -> str:
    token_pattern = re.compile(
        "(" + "|".join(re.escape(token) for token in protected) + ")"
    )
    translated_parts = []
    for part in token_pattern.split(protected_text):
        if not part:
            continue
        if part in protected:
            translated_parts.append(part)
            continue
        part_key = "split:" + sha256(part.encode("utf-8"))
        if part_key not in cache:
            cache[part_key] = request_translation(part)
            time.sleep(0.12)
        translated_parts.append(cache[part_key])
    return "".join(translated_parts)


def translate_segment_in_order(segment: str, cache: dict[str, str]) -> str:
    if not re.search(r"[A-Za-z]", TAG_RE.sub("", segment)):
        return segment
    protected_text, protected = protect_text(segment)
    translated = split_translation(protected_text, protected, cache)
    return restore_text(translated, protected)


def candidate() -> dict[str, object]:
    if not ENGLISH_ROOT.is_dir():
        extract()
    cache = (
        json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        if CACHE_FILE.is_file()
        else {}
    )
    translated_pages = 0
    segments = 0
    KOREAN_ROOT.mkdir(parents=True, exist_ok=True)
    for source in sorted(ENGLISH_ROOT.glob("*.txt")):
        content = source.read_text(encoding="utf-8")
        parts = re.split(r"(<np>|\n\n+)", content)
        translated = []
        for part in parts:
            if not part or part == "<np>" or part.startswith("\n\n"):
                translated.append(part)
                continue
            translated.append(translate_segment(part, cache))
            segments += 1
        localized = localize_visible_tags("".join(translated), cache)
        (KOREAN_ROOT / source.name).write_text(
            localized, encoding="utf-8", newline="\n"
        )
        translated_pages += 1
    report = {
        "pages": translated_pages,
        "translated_segments": segments,
        "candidate_cache_entries": len(cache),
        "status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


def review() -> dict[str, object]:
    changed_pages = 0
    english_remnants = []
    for path in sorted(KOREAN_ROOT.glob("*.txt")):
        value = path.read_text(encoding="utf-8")
        original = value
        for old, new in MANUAL_REPLACEMENTS:
            value = value.replace(old, new)
        for old, new in FILE_REPLACEMENTS.get(path.name, ()):
            value = value.replace(old, new)
        if path.name in TITLE_OVERRIDES and value:
            lines = value.split("\n")
            lines[0] = TITLE_OVERRIDES[path.name]
            value = "\n".join(lines)
        if value != original:
            path.write_text(value, encoding="utf-8", newline="\n")
            changed_pages += 1
        plain = TAG_RE.sub(" ", value)
        words = {word.lower() for word in LATIN_WORD_RE.findall(plain)}
        common = sorted(words & COMMON_ENGLISH_WORDS)
        if common:
            english_remnants.append({"file": path.name, "words": common})
    report = {
        "pages_fully_reviewed": len(list(KOREAN_ROOT.glob("*.txt"))),
        "pages_with_term_normalization": changed_pages,
        "english_remnant_candidates": english_remnants,
        "status": "reviewed" if not english_remnants else "review_required",
    }
    write_json(WORK_ROOT / "review_report.json", report)
    return report


def verify() -> tuple[dict[str, object], list[str]]:
    errors = []
    source_files = {path.name: path for path in ENGLISH_ROOT.glob("*.txt")}
    target_files = {path.name: path for path in KOREAN_ROOT.glob("*.txt")}
    if set(source_files) != set(target_files):
        errors.append("설명서 영어·한국어 파일 목록이 다릅니다.")
    source_equal = []
    for name in sorted(set(source_files) & set(target_files)):
        source = source_files[name].read_text(encoding="utf-8")
        target = target_files[name].read_text(encoding="utf-8")
        source_tags = [tag_signature(tag) for tag in TAG_RE.findall(source)]
        target_tags = [tag_signature(tag) for tag in TAG_RE.findall(target)]
        if source_tags != target_tags:
            errors.append(f"{name}: 링크 또는 서식 태그 순서 불일치")
        missing_numbers = source_numbers_missing(source, target)
        if missing_numbers:
            errors.append(f"{name}: 원문 숫자 누락 {missing_numbers}")
        if source == target and source:
            source_equal.append(name)
        if source and len(target.splitlines()) < 2:
            errors.append(f"{name}: 제목 또는 부제목 줄 누락")
    if source_equal:
        errors.append(f"영어 원문과 동일한 설명서 페이지: {source_equal}")
    review_report = WORK_ROOT / "review_report.json"
    if not review_report.is_file():
        errors.append("설명서 재검수 보고서가 없습니다.")
        review = {}
    else:
        review = json.loads(review_report.read_text(encoding="utf-8"))
        if review.get("status") != "reviewed":
            errors.append("설명서 영어 잔여 후보 검토가 끝나지 않았습니다.")
    report = {
        "pages": len(target_files),
        "tag_order_parity": not any("태그 순서 불일치" in error for error in errors),
        "number_parity": not any("원문 숫자 누락" in error for error in errors),
        "source_equal": len(source_equal),
        "review_status": review.get("status"),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "validation.json", report)
    return report, errors


def tag_signature(tag: str) -> tuple[str, ...]:
    if tag.startswith("<link;"):
        parts = tag[1:-1].split(";")
        return ("link", parts[1], parts[3] if len(parts) >= 4 else "")
    if tag.startswith("<config;b;"):
        parts = tag[1:-1].split(";")
        return tuple(parts[:3])
    return (tag,)


def visible_numbers(value: str) -> list[str]:
    """태그와 서식 코드 바깥에 실제로 표시되는 숫자를 정규화한다."""
    plain = FORMAT_CODE_RE.sub("", TAG_RE.sub(" ", value))
    return [
        str(float(number)) if "." in number else str(int(number))
        for number in NUMBER_RE.findall(plain)
    ]


def source_numbers_missing(source: str, target: str) -> list[str]:
    """한국어에서 사라진 영어 원문의 표시 숫자를 중복 개수까지 찾는다."""
    remaining = visible_numbers(target)
    missing = []
    for number in visible_numbers(source):
        if number in remaining:
            remaining.remove(number)
        else:
            missing.append(number)
    return missing


def build() -> dict[str, object]:
    report, errors = verify()
    if errors:
        raise ValueError("검증되지 않은 설명서는 빌드하지 않습니다.")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    copied = []
    for source in sorted(KOREAN_ROOT.glob("*.txt")):
        destination = OUTPUT_ROOT / source.name
        destination.write_bytes(source.read_bytes())
        copied.append(str(destination.relative_to(PROJECT_ROOT)))
    return {"pages": report["pages"], "copied": copied}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("extract", "candidate", "review", "verify", "build")
    )
    args = parser.parse_args()
    if args.command == "extract":
        report = extract()
        errors = []
    elif args.command == "candidate":
        report = candidate()
        errors = []
    elif args.command == "review":
        report = review()
        errors = []
    elif args.command == "verify":
        report, errors = verify()
    else:
        report = build()
        errors = []
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
