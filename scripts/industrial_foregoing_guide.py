#!/usr/bin/env python3
"""Industrial Foregoing Patchouli 가이드와 발전 과제 표시 경로를 번역·검증한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path
from zipfile import ZipFile

import ars_family
import industrial_foregoing_family as language
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root


WORK_ROOT = PROJECT_ROOT / "working/industrial_foregoing/guide"
ENGLISH_ROOT = WORK_ROOT / "en_us"
JAPANESE_ROOT = WORK_ROOT / "ja_jp"
KOREAN_ROOT = WORK_ROOT / "ko_kr"
OUTPUT_ROOT = (
    active_output_root()
    / "resourcepack/ATM10_Korean/assets/industrialforegoing"
    / "patchouli_books/industrial_foregoing/ko_kr"
)
BOOK_OUTPUT = (
    active_output_root()
    / "overrides/kubejs/data/industrialforegoing"
    / "patchouli_books/industrial_foregoing/book.json"
)
CACHE_FILE = PROJECT_ROOT / "temp/industrial_foregoing_guide_candidate_cache.json"
BOOK_PREFIX = "assets/industrialforegoing/patchouli_books/industrial_foregoing/en_us/"
JAPANESE_PREFIX = (
    "assets/industrialforegoing/patchouli_books/industrial_foregoing/ja_jp/"
)
BOOK_SOURCE = "data/industrialforegoing/patchouli_books/industrial_foregoing/book.json"
ADVANCEMENT_PREFIXES = (
    "data/industrialforegoing/advancement/",
    "data/industrialforegoingsouls/advancement/",
)
VISIBLE_FIELDS = {
    "caption",
    "description",
    "header",
    "name",
    "subtitle",
    "text",
    "title",
}
PATCHOULI_TAG = re.compile(r"\$\([^)]+\)")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")

ALLOWED_LATIN = {
    "AE2",
    "Biofuel",
    "FE",
    "GUI",
    "Industrial Foregoing",
    "MIB",
    "JEI",
    "Mek",
    "Minecraft",
    "Pam's HarvestCraft",
    "RF",
    "Tesla",
    "Tinkers' Construct",
}

CATEGORY_OVERRIDES = {
    "Agriculture and Husbandry": "농업 및 축산",
    "Basics": "기초",
    "Generators": "발전기",
    "Misc": "기타",
    "Resource Production": "자원 생산",
    "Tools": "도구",
    "Transport": "운송",
}

LOCATION_OVERRIDES = {
    ("categories/basics.json", "description"): (
        "Industrial Foregoing에서 플라스틱을 확보하는 일은 가장 중요한 시작 단계 중 "
        "하나입니다. 생산 과정을 꼭 익혀 두세요."
    ),
    ("categories/agriculture_husbandry.json", "description"): (
        "작물과 동물을 자동으로 관리하는 기계를 설명합니다."
    ),
    ("categories/generators.json", "description"): (
        "여러 자원으로 FE를 생산하는 발전기를 설명합니다."
    ),
    (
        "categories/misc.json",
        "description",
    ): "다른 분류에 속하지 않는 기계와 장치입니다.",
    ("categories/resource_production.json", "description"): (
        "광석, 유체와 여러 자원을 자동으로 생산하고 가공하는 기계를 설명합니다."
    ),
    (
        "categories/tools.json",
        "description",
    ): "플레이어가 직접 사용하는 도구와 장비입니다.",
    ("categories/transport.json", "description"): (
        "아이템, 유체와 개체를 옮기는 장치입니다."
    ),
    ("entries/basics/latex_processing_unit.json", "text"): (
        "라텍스 처리 장치는 $(6)750$()mb의 $(l:basics/latex)라텍스$()와 물 "
        "$(6)500$()mb를 사용해 $(l:basics/plastic)건조 고무$() 1개를 생산합니다."
    ),
    ("entries/resource_production/sludge_refiner.json", "text"): (
        "$(6)슬러지$()를 유용한 자원으로 바꾸는 기계입니다.$(br2)"
        "$(6)슬러지$()는 $(l:agriculture_n_husbandry/plant_gatherer)식물 수확기$()"
        "에서 얻습니다. 공급하면 $(6)여러 자원$()을 무작위로 생산합니다.$(br)"
        "이 과정에는 $(6)1000$()RF/t가 필요하므로 충분한 전력을 저장해 두세요."
    ),
    ("entries/agr_hus/animal_rancher.json", "text"): (
        "양의 털을 $(6)깎고$() 소의 젖을 $(6)짭니다$()."
    ),
    ("entries/agr_hus/essence.json", "text"): (
        "$(l:agr_hus/mob_crusher)몹 분쇄기$()가 생산하는 유체 형태의 경험치입니다."
    ),
    ("entries/agr_hus/hydroponic_bed.json", "text"): (
        "전력과 $(6)물$()(네더 작물은 $(6)용암$())을 공급하면 작물의 성장 속도를 "
        "높입니다.$(br2)$(l:resource_production/ether_gas)에테르 가스$()를 아주 "
        "조금 공급하면 훨씬 빠르게 자라며 수확 후 자동으로 다시 심습니다."
    ),
    ("entries/agr_hus/mob_crusher.json", "text"): (
        "플레이어가 처치한 것처럼 몹을 $(6)처치$()해 전리품과 정수를 생산합니다. "
        "전리품은 몹의 전리품 목록에서 직접 생성됩니다.$(br2)정수 대신 무작위 "
        "레벨의 $(6)행운$()을 적용한 전리품을 생산하는 모드도 있습니다."
    ),
    ("entries/agr_hus/mob_duplicator.json", "text"): (
        "몹을 생성하는 기계입니다. 전력과 $(l:agr_hus/essence)정수$(), 개체가 든 "
        "$(l:tools/mib)몹 포획기$()를 공급하면 주변에 해당 개체를 생성합니다.$(br2)"
        "주변 개체 수가 너무 많으면 생성을 멈춥니다."
    ),
    ("entries/agr_hus/plant_gatherer.json", "text"): (
        "나무를 $(6)벌목$()하고 작물을 $(6)수확$()합니다. 작업할 때마다 "
        "$(l:agr_hus/sludge)슬러지$()가 조금 생성됩니다.$(br2)작업 영역에서 나무를 "
        "수확하기 시작하면 기준 원목에 이어진 통나무와 나뭇잎을 모두 수확합니다."
    ),
    ("entries/agr_hus/plant_sower.json", "text"): (
        "작물과 묘목을 $(6)심습니다$().$(br2)내부 인벤토리의 9개 슬롯은 "
        "$(6)색상$()으로 구분되며 기계 윗면의 색상과 대응합니다. 위쪽 작업 영역도 "
        "9구역으로 나뉘어 각 슬롯의 씨앗을 해당 구역에만 심습니다."
    ),
    ("entries/agr_hus/sewer.json", "text"): (
        "동물에게서 $(l:agr_hus/sewage)오물$()을 수집하는 기계입니다. 자세한 과정은 "
        "굳이 알지 않는 편이 좋습니다."
    ),
    ("entries/agr_hus/wither_builder.json", "text"): (
        "위더를 소환하는 구조물을 만드는 기계입니다. 전력, $(6)위더 해골 3개$(), "
        "$(6)영혼 모래 4개$()를 공급하면 작업 영역에 구조물을 완성합니다."
    ),
    ("entries/basics/fluid_extractor.json", "text"): (
        "유체 추출기는 앞에 놓인 원목에서 $(l:basics/latex)라텍스$()를 추출합니다. "
        "여러 대가 같은 원목에서 동시에 추출할 수 있습니다.$(br2)기계가 원목을 "
        "소모하면 먼저 껍질 벗긴 원목으로 바꾸고, 완전히 소모하면 사라지게 합니다."
    ),
    ("entries/generators/bioreactor.json", "text"): (
        "물과 $(6)씨앗$(), $(6)묘목$(), $(6)염료$(), 심지어 $(6)머리$()까지 "
        "사용해 $(l:generators/biofuel)바이오연료$()를 만듭니다.$(br2)서로 다른 "
        "종류의 재료를 많이 넣을수록 재료 하나당 생산량이 증가합니다. 한 종류만 "
        "사용하면 재료당 $(6)80$()mb를 만들지만, 네 종류를 사용하면 각각 "
        "$(6)110$()mb씩 총 $(6)440$()mb를 만듭니다."
    ),
    ("entries/generators/biofuel.json", "text"): (
        "$(l:generators/bioreactor)생물 반응기$()가 식물, 염료, 머리 같은 여러 "
        "재료로 만드는 보라색 유체입니다.$(br2)"
        "$(l:generators/biofuel_generator)바이오연료 발전기$()와 "
        "$(l:tools/infinity_tools)인피니티 도구$()의 연료로 사용합니다."
    ),
    ("entries/generators/mycelial_reactor.json", "text"): (
        "$(6)균사 네트워크$()(균사체가 존재하는 하위 공간)를 통해 다른 $(6)균사 "
        "발전기$()를 감지하고 막대한 FE를 생산합니다.$(br2)작동하려면 각 종류의 "
        "균사 발전기가 동시에 하나씩 가동 중이어야 합니다."
    ),
    ("entries/misc/enchantment_applicator.json", "text"): (
        "모루와 같은 방식으로 작동하지만 경험치 대신 "
        "$(l:agr_husb/essence)정수$()를 사용합니다. 비용이 너무 높게 표시되어도 "
        "탱크에 정수가 충분하면 작업할 수 있습니다."
    ),
    ("entries/misc/enchantment_extractor.json", "text"): (
        "책과 마법이 부여된 아이템을 넣으면 마법을 추출합니다.$(br2)마법을 책으로 "
        "옮기거나, 추출한 마법을 $(l:agr_husb/essence)정수$()로 바꾸는 두 가지 "
        "방식으로 작동합니다."
    ),
    ("entries/misc/infinity_charger.json", "text"): (
        "전력을 저장할 수 있는 아이템을 충전합니다. 특히 $(6)인피니티$() 아이템을 "
        "매우 빠르게 충전합니다."
    ),
    ("entries/misc/stasis_chamber.json", "text"): (
        "전력을 공급하면 작업 영역 안의 모든 개체를 $(6)정지$()시키고 "
        "$(6)회복$()시킵니다."
    ),
    ("entries/resource_production/dye_mixer.json", "text"): (
        "기본 염료를 섞어 여러 색의 염료를 만듭니다.$(br2)예를 들어 흰색 "
        "$(6)염료$() 하나를 만들 때 $(4)빨간색$(0), $(2)초록색$(0), "
        "$(1)파란색$(0) 버퍼를 각각 1만큼 사용합니다.$(br)$(6)30$()RF/t를 "
        "소비합니다."
    ),
    ("entries/resource_production/laser_drill.json", "text"): (
        "전력을 공급하면 작업 영역에서 가장 먼저 찾은 "
        "$(l:resource_production/ore_laser_base)광석 레이저 베이스$() 또는 "
        "$(l:resource_production/fluid_laser_base)유체 레이저 베이스$()를 충전합니다."
    ),
    ("entries/resource_production/marine_fisher.json", "text"): (
        "고양이의 가장 좋은 친구입니다 <3$(br2)최소 $(6)3x3$(), 깊이 "
        "$(6)1$()블록의 물 $(6)웅덩이$() 위에 놓으면 $(6)낚시$()를 시작합니다. "
        "작업당 $(6)5000$()RF를 사용해 물고기와 다른 낚시 보상을 내부 인벤토리에 "
        "넣습니다."
    ),
    ("entries/resource_production/potion_brewer.json", "text"): (
        "바닐라 양조기를 자동화한 기계입니다.$(br2)$(6)전력$()을 공급하면 넣어 둔 "
        "재료로 물약을 만듭니다.$(br)내부 $(6)물$() 탱크가 차 있으면 빈 병에 물을 "
        "채우며 병은 소모하지 않습니다.$(br2)완성한 물약을 모두 꺼내려면 녹색 "
        "필터에 물약을 지정해야 합니다."
    ),
    ("entries/resource_production/spores_recreator.json", "text"): (
        "$(6)균류$()를 복제합니다.$(br2)$(6)40$()RF/t와 작업당 $(6)물$() "
        "$(6)100$()mb가 필요합니다.$(br2)네더 균류는 $(6)용암$()이 필요합니다."
    ),
    ("entries/resource_production/stonework_factory.json", "text"): (
        "차세대 $(6)조약돌$() 생성기입니다.$(br2)$(6)60$()RF/t와 $(6)물$(), "
        "$(6)용암$()을 공급하면 지정한 재료를 생산합니다.$(br)생산한 재료에는 "
        "다음 작업을 이어서 적용할 수 있습니다:$(br)$(li)제련$(br)$(li)분쇄$(br)"
        "$(li)조합"
    ),
    ("entries/tools/infinity_launcher.json", "text"): (
        "인피니티 런처는 일정 범위 안의 개체를 몹 포획기에 넣거나 풀어주는 "
        "도구입니다. GUI에서 모드를 고르고 발사하면 인벤토리의 몹 포획기를 "
        "사용해 대상을 포획하거나 풀어줍니다."
    ),
    ("entries/tools/infinity_nuke.json", "text"): (
        "인피니티 핵은 등급과 바이오연료 양에 따라 폭발 반경이 커지는 대량 파괴 "
        "도구입니다. 불러온 청크의 아이템 개체는 파괴하지 않습니다.$(br2)땅에 놓고 "
        "우클릭해 무장한 다음, 부싯돌과 부시로 우클릭하면 폭발합니다."
    ),
    ("entries/tools/infinity_trident.json", "text"): (
        "인피니티 삼지창은 삼지창의 능력을 극대화하는 도구입니다. 등급을 높이면 "
        "$(6)충성$(), $(6)급류$(), $(6)집전$() 효과의 레벨이 올라갑니다.$(br2)"
        "집전 효과와 적중 피해는 광역으로 적용됩니다."
    ),
}

LOCATION_OVERRIDES.update(
    {
        ("entries/agr_hus/animal_feeder.json", "text"): (
            "동물의 먹이를 공급하면 동물에게 $(6)먹이를 주어$() 번식시킵니다."
        ),
        ("entries/agr_hus/essence.json", "name"): "정수(양동이)",
        ("entries/agr_hus/meat.json", "name"): "액상 고기(양동이)",
        ("entries/agr_hus/meat.json", "text"): (
            "$(l:agr_hus/mob_slaughter_factory)몹 도살 공장$()에서 생산하는 유체입니다."
        ),
        ("entries/agr_hus/pink_slime.json", "name"): "분홍색 슬라임(양동이)",
        ("entries/agr_hus/pink_slime.json", "text"): (
            "$(l:agr_hus/mob_slaughter_factory)몹 도살 공장$()에서 생산하는 유체입니다."
        ),
        ("entries/agr_hus/plant_fertilizer.json", "text"): (
            "식물에 $(6)뼛가루를 사용$()하는 기계입니다.$(br2)다음 식물로 넘어가기 "
            "전에 현재 작물이 더 이상 뼛가루를 받지 않을 때까지 계속 비료를 "
            "줍니다. 따라서 $(6)해바라기$()처럼 뼛가루를 계속 받는 식물이나 최종 "
            "성장 단계에 도달하지 않는 식물에서는 작업이 멈출 수 있습니다."
        ),
        ("entries/agr_hus/plant_fertilizer.json", "pages.1.text"): (
            "식물 비료 공급기는 다음 아이템을 받습니다: " "$(br)$(li)뼛가루 $(li)비료"
        ),
        ("entries/agr_hus/plant_gatherer.json", "pages.1.text"): (
            "식물 수확기는 우클릭으로 수확할 수 있는 작물도 직접 부숴 수확합니다. "
            "하지만 에테르 가스를 조금 공급하면 작물을 자동으로 다시 심습니다."
        ),
        ("entries/agr_hus/sewage.json", "name"): "오물(양동이)",
        ("entries/agr_hus/sewage.json", "text"): (
            "$(l:agr_hus/sewer)오물통$()에서 생산하는 유체입니다. 자세한 내용은 "
            "굳이 알지 않는 편이 좋습니다."
        ),
        ("entries/agr_hus/sewage_composter.json", "text"): (
            "$(l:agr_hus/sewage)오물$()을 공급하면 "
            "$(l:agr_hus/fertilizer)비료$()를 생산합니다."
        ),
        ("entries/agr_hus/sewer.json", "text"): (
            "동물에게서 $(l:agr_hus/sewage)오물$()을 모으고 경험치를 흡수해 "
            "정수로 바꾸는 기계입니다."
        ),
        ("entries/agr_hus/simulated_hydroponic_bed.json", "text"): (
            "전력을 공급하면 수경 재배 모의 처리기의 작물 데이터를 바탕으로 "
            "생산물을 생성합니다."
        ),
        ("entries/agr_hus/sludge.json", "name"): "슬러지(양동이)",
        ("entries/basics/addons.json", "text"): (
            "작업 영역이 있는 기계의 범위를 늘립니다. 모든 기계가 범위 업그레이드를 "
            "받는 것은 아닙니다. 등급이 오를 때마다 범위가 1씩 증가합니다."
        ),
        ("entries/basics/addons.json", "pages.1.text"): (
            "매 틱 진행 막대가 차는 양을 늘립니다. " "$(br2)1등급 -> +1$(br)2등급 -> +2"
        ),
        ("entries/basics/addons.json", "pages.2.title"): "효율",
        ("entries/basics/addons.json", "pages.2.text"): (
            "작업 한 번을 완료하는 데 필요한 틱 수를 줄입니다. "
            "$(br2)1등급 -> -10%$(br)2등급 -> -20%"
        ),
        ("entries/basics/addons.json", "pages.3.text"): (
            "기계가 처리를 마칠 때 완료하는 작업 횟수를 늘립니다. "
            "$(br2)1등급 -> 작업 +1회 $(br)2등급 -> 작업 +2회"
        ),
        ("entries/basics/dissolution_chamber.json", "text"): (
            "아이템 최대 $(6)8$()개와 유체 최대 $(6)1$()종류를 사용해 재료를 "
            "제작하는 강력한 기계입니다. 아이템이나 유체를 생산할 수 있습니다."
            "$(br2)모든 조합법은 무형이므로 재료를 어느 슬롯에 넣어도 됩니다."
            "$(br2)조합법이 완성되면 추가 아이템이 들어오지 않도록 모든 슬롯을 "
            "잠급니다."
        ),
        ("entries/basics/fluid_extractor.json", "pages.1.text"): (
            "$(br2)$(6)원목마다 라텍스 생산량이 다릅니다. 생산량은 JEI에서 "
            "확인하세요. $(6)전력 공급은 선택 사항이며, 공급하면 더 빨리 작동합니다."
        ),
        ("entries/generators/biofuel_generator.json", "text"): (
            "$(l:generators/biofuel)바이오연료$()로 $(6)160$()RF/t를 생산하는 "
            "발전기입니다.$(br2)내부 전력 버퍼가 가득 차면 연료 소비를 멈춥니다."
        ),
        ("entries/generators/pity.json", "name"): "조악한 발전기",
        ("entries/generators/pity.json", "text"): (
            "석탄 같은 가연성 연료를 사용하는 매우 비효율적인 발전기입니다."
            "$(br2)내부 전력 버퍼가 가득 차도 연료를 계속 소비할 정도로 "
            "비효율적입니다."
        ),
        ("entries/misc/enchantment_factory.json", "text"): (
            "대량의 $(l:agr_hus/essence)정수$()와 아이템을 공급하면 해당 아이템에 "
            "무작위 $(6)30$()레벨 마법을 부여합니다."
        ),
        ("entries/misc/enchantment_sorter.json", "text"): (
            "마법이 부여된 아이템과 그렇지 않은 아이템을 분류합니다."
        ),
        ("entries/misc/mob_detector.json", "text"): (
            "앞쪽의 개체 수를 감지해, 감지한 수와 같은 세기의 레드스톤 신호를 "
            "뒤쪽으로 출력합니다."
        ),
        ("entries/resource_production/block_breaker.json", "text"): (
            "앞의 블록을 부숴 내부 인벤토리에 넣습니다. 작업할 때마다 "
            "$(6)1000$()RF를 사용합니다."
        ),
        ("entries/resource_production/block_placer.json", "text"): (
            "블록을 배치합니다.$(br2)내부 인벤토리의 블록을 앞에 배치하며, "
            "작업할 때마다 $(6)1000$()RF를 사용합니다."
        ),
        ("entries/resource_production/ether_gas.json", "name"): ("에테르 가스(양동이)"),
        ("entries/resource_production/ether_gas.json", "text"): (
            "$(l:resource_production/fluid_laser_base)유체 레이저 베이스$()를 위더 "
            "바로 위에 놓았을 때 생산하는 유체입니다."
        ),
        ("entries/resource_production/fermentation_station.json", "text"): (
            "생광석 고기가 설정한 양에 도달하면 내용물을 밀봉하고, 선택한 생산 "
            "방식으로 고기를 발효합니다."
        ),
        ("entries/resource_production/fluid_collector.json", "text"): (
            "앞의 유체 원천 블록을 빨아들입니다.$(br2)내부 탱크의 유체를 배치하며 "
            "$(6)1000$()RF를 사용합니다."
        ),
        ("entries/resource_production/fluid_laser_base.json", "text"): (
            "$(l:resource_production/laser_drill)레이저 드릴$()로 완전히 충전하면 "
            "유체를 생산합니다. 소모되지 않는 특정 촉매가 필요하며, 기계를 특정 "
            "생물군계에 설치하고 특정 깊이로 설정해야 합니다.$(br2)일부 유체는 "
            "기계 아래에 특정 개체가 있어야 생산됩니다.$(br2)정확한 조건은 "
            "JEI에서 확인하세요."
        ),
        ("entries/resource_production/fluid_placer.json", "text"): (
            "유체를 배치합니다.$(br2)내부 탱크의 유체를 앞에 배치하며 "
            "$(6)1000$()RF를 사용합니다."
        ),
        ("entries/resource_production/fluid_sieving_machine.json", "text"): (
            "발효 광석 고기와 모래를 사용해, 고기를 처음 만들 때 사용한 광석의 "
            "가루로 바꿉니다."
        ),
        ("entries/resource_production/mechanical_dirt.json", "pages.1.text"): (
            "연결된 블록 하나에 $(6)전력$()이나 $(6)액상 고기$()를 공급하면 모든 "
            "연결 블록에 똑같이 나누어집니다."
        ),
        ("entries/resource_production/ore_laser_base.json", "text"): (
            "$(l:resource_production/laser_drill)레이저 드릴$()로 완전히 충전하면 "
            "광석을 생산합니다. 각 광석의 가중치는 기계가 있는 생물군계와 설정한 "
            "채굴 깊이에 따라 달라집니다.$(br2)레이저 렌즈는 해당 색상 광석의 "
            "가중치를 높입니다.$(br2)정확한 값은 JEI에서 확인하세요."
        ),
        ("entries/resource_production/resourceful_furnace.json", "text"): (
            "화로 3대를 하나로 합친 기계입니다.$(br2)아이템 하나를 제련할 때마다 "
            "정수 $(6)2$()mb를 생산하며, $(6)40$()RF/t를 사용합니다."
        ),
        ("entries/resource_production/washing_factory.json", "text"): (
            "액상 고기와 광석을 사용해 해당 광석의 생광석 고기를 만듭니다."
        ),
        ("entries/resource_production/water_condensator.json", "text"): (
            "주변 원천 블록에서 $(6)물$()을 생산하는 기계입니다.$(br2)물 원천 "
            "블록과 맞닿은 면이 $(6)2개 이상$()이면 작동합니다.$(br)맞닿은 원천 "
            "블록을 늘리고 작업당 $(6)1000()RF를 공급하면 훨씬 빨라집니다."
        ),
        ("entries/tools/infinity_backpack.json", "text"): (
            "인피니티 백팩은 많은 아이템을 휴대해 보관하는 도구입니다.$(br2)세 "
            "가지 전용 유체를 담을 수 있습니다. $(6)바이오연료$()는 자동 기능을 "
            "작동시키고, $(6)정수$()는 자동 줍기로 얻은 경험치를 저장하며, "
            "$(6)액상 고기$()는 플레이어에게 자동으로 먹이를 줍니다."
        ),
        ("entries/tools/infinity_backpack.json", "pages.1.text"): (
            "$(6)자석 모드$()를 켜면 주울 수 있는 주변 아이템이 플레이어에게 "
            "순간이동합니다.$(br2)$(6)자동 줍기 모드$()를 켜면 플레이어가 주운 "
            "아이템 중 백팩에 넣을 수 있는 것을 자동으로 백팩에 넣습니다.$(br2)"
            "각 슬롯은 남는 아이템을 $(6)무효화$()하거나, 인벤토리의 덜 찬 스택을 "
            "$(6)자동 보충$()하도록 설정할 수 있습니다."
        ),
        ("entries/tools/infinity_drill.json", "text"): (
            "인피니티 드릴은 넓은 영역을 채굴하는 도구입니다. 등급이 높을수록 한 "
            "번에 채굴하는 영역이 넓어집니다."
        ),
        ("entries/tools/infinity_hammer.json", "text"): (
            "인피니티 해머는 범위 안의 적에게 피해를 주는 도구입니다. 등급이 "
            "높아지면 더 높은 레벨의 $(6)참수$() 효과가 열려 몹 머리를 쉽게 "
            "얻을 수 있습니다."
        ),
        ("entries/tools/infinity_hammer.json", "pages.1.text"): (
            "지면을 우클릭하면 플레이어 앞의 원뿔형 영역에 $(6)분쇄$() 효과를 "
            "일으킵니다."
        ),
        ("entries/tools/infinity_nuke.json", "text"): (
            "인피니티 핵은 등급과 저장된 바이오연료 양에 따라 폭발 반경이 커지는 "
            "대량 파괴 도구입니다. 클레임된 청크의 블록은 파괴하지 않습니다."
            "$(br2)땅에 놓고 우클릭해 무장한 뒤, 부싯돌과 부시로 우클릭하면 "
            "폭발합니다."
        ),
        ("entries/tools/infinity_saw.json", "text"): (
            "인피니티 톱은 나무를 효율적으로 베는 도구입니다. 등급이 높을수록 한 "
            "번에 더 많은 블록을 벱니다. 큰 나무는 같은 블록을 계속 파괴하세요."
        ),
        ("entries/tools/infinity_tools.json", "name"): "인피니티 도구",
        ("entries/tools/infinity_tools.json", "text"): (
            "인피니티 도구는 전력이 많을수록 강해지며, 등급을 높이면 특별한 기능이 "
            "열릴 수 있습니다. $(l:biofuel)바이오연료$()를 채우면 사용할 때 전력 "
            "대신 연료를 소비해 더 효율적으로 작동합니다.$(br2)$(6)웅크리고 "
            "우클릭$()하면 도구 GUI를 엽니다."
        ),
        ("entries/tools/infinity_tools.json", "pages.1.text"): (
            "도구 GUI에서 충전 기능을 꺼 $(6)충전$()을 막을 수 있습니다.$(br2)"
            "등급은 7가지입니다: $(li)조악$(li)일반$(li)고급$(li)희귀$(li)영웅"
            "$(li)전설$(li)유물 $(br2)모든 도구는 전리품을 플레이어에게 "
            "순간이동시킵니다."
        ),
        ("entries/tools/infinity_tools.json", "pages.2.text"): (
            "후원자가 되면 특별한 $(6)빛나는$() 외형의 도구를 얻을 수 있습니다!"
        ),
        ("entries/tools/mib.json", "text"): (
            "MIB를 들고 개체를 $(6)우클릭$()하면 해당 개체를 MIB 안에 "
            "보관합니다.$(br2)MIB를 들고 땅을 $(6)우클릭$()하면 개체를 꺼냅니다."
        ),
        ("entries/transport/conveyor.json", "text"): (
            "컨베이어는 아이템, 개체와 유체를 운송합니다. "
            "$(l:conveyor_upgrades)업그레이드$()를 장착하면 월드와 상호작용할 수 "
            "있습니다. 아이템과 개체는 위아래로도 이동하지만 유체는 수평으로만 "
            "이동합니다.$(br2)염료로 우클릭하면 컨베이어의 색을 바꿀 수 있습니다."
        ),
        ("entries/transport/conveyor.json", "pages.2.text"): (
            "발광석을 사용하면 컨베이어가 아이템과 개체를 매우 빠르게 옮깁니다."
        ),
        ("entries/transport/conveyor.json", "pages.3.text"): (
            "플라스틱을 사용하면 컨베이어 위의 아이템을 주울 수 없게 합니다."
        ),
        ("entries/transport/conveyor_upgrades.json", "pages.0.text"): (
            "인벤토리에서 아이템과 유체를 추출하며, 플레이어 인벤토리에서도 "
            "아이템을 꺼낼 수 있습니다.$(br2)추출할 아이템과 유체는 GUI에서 "
            "필터링할 수 있습니다."
        ),
        ("entries/transport/conveyor_upgrades.json", "pages.1.text"): (
            "인벤토리에 아이템과 유체를 넣습니다. 컨베이어에 닿은 아이템을 넣는 "
            "모드와 업그레이드에 직접 닿은 아이템만 넣는 모드가 있습니다.$(br2)"
            "삽입할 아이템과 유체는 GUI에서 필터링할 수 있습니다."
        ),
        ("entries/transport/conveyor_upgrades.json", "pages.2.title"): "감지",
        ("entries/transport/conveyor_upgrades.json", "pages.2.text"): (
            "컨베이어 위의 아이템과 개체를 감지합니다.$(br2)감지할 아이템과 개체는 "
            "GUI에서 필터링할 수 있습니다. 개체가 든 MIB로 대상 개체를 "
            "지정할 수도 있습니다."
        ),
        ("entries/transport/conveyor_upgrades.json", "pages.3.title"): "튕김",
        ("entries/transport/conveyor_upgrades.json", "pages.3.text"): (
            "컨베이어 위의 아이템과 개체를 공중으로 발사합니다. GUI에서 수직·수평 "
            "세기를 바꿀 수 있습니다.$(br2)발사할 아이템과 개체는 GUI에서 "
            "필터링할 수 있습니다. 개체가 든 MIB로 대상 개체를 지정할 수도 있습니다."
        ),
        ("entries/transport/conveyor_upgrades.json", "pages.4.title"): "낙하",
        ("entries/transport/conveyor_upgrades.json", "pages.4.text"): (
            "컨베이어 위의 아이템과 개체를 바로 아래로 떨어뜨립니다.$(br2)떨어뜨릴 "
            "아이템과 개체는 GUI에서 필터링할 수 있습니다. 개체가 든 MIB로 대상 "
            "개체를 지정할 수도 있습니다."
        ),
        ("entries/transport/conveyor_upgrades.json", "pages.5.title"): "순간이동",
        ("entries/transport/conveyor_upgrades.json", "pages.5.text"): (
            "컨베이어 위의 아이템과 개체를 순간이동시킵니다. GUI에서 수직·수평 "
            "거리를 바꿀 수 있습니다.$(br2)순간이동시킬 아이템과 개체는 GUI에서 "
            "필터링할 수 있습니다. 개체가 든 MIB로 대상 개체를 지정할 수도 있습니다."
        ),
        ("entries/transport/conveyor_upgrades.json", "pages.6.title"): "분배",
        ("entries/transport/conveyor_upgrades.json", "pages.6.text"): (
            "컨베이어 위의 아이템과 개체를 GUI에서 설정한 비율로 나눕니다. 분배할 "
            "모든 면에 업그레이드를 장착해야 합니다."
        ),
        ("entries/transport/fluid_transporter.json", "text"): (
            "유체 수송기는 1블록 떨어진 인벤토리 사이에서 유체를 옮깁니다. 추출 "
            "쪽과 삽입 쪽에 각각 수송기가 필요합니다.$(br2)한 블록에 여러 종류의 "
            "수송기를 함께 둘 수 있습니다. 삽입·추출 모드는 가운데 부분을 우클릭해 "
            "바꿉니다."
        ),
        ("entries/transport/fluid_transporter.json", "pages.1.text"): (
            "GUI에서 허용 목록과 차단 목록으로 전송 대상을 필터링할 수 있습니다."
            "$(br2)업그레이드나 수송기를 제거하려면 수송기를 웅크리고 우클릭하세요."
            "$(br2)삽입 모드에서 조절기 모드를 사용하면 인벤토리에 남겨 둘 아이템 "
            "또는 유체의 양을 지정할 수 있습니다."
        ),
        ("entries/transport/fluid_transporter.json", "pages.2.text"): (
            "수송기 바깥쪽 고리에 속도 업그레이드를 우클릭하면 작동 속도가 "
            "빨라지고, 효율 업그레이드를 우클릭하면 전송량이 늘어납니다."
        ),
        ("entries/transport/item_transporter.json", "text"): (
            "아이템 수송기는 1블록 떨어진 인벤토리 사이에서 아이템을 옮깁니다. "
            "추출 쪽과 삽입 쪽에 각각 수송기가 필요합니다.$(br2)한 블록에 여러 "
            "종류의 수송기를 함께 둘 수 있습니다. 삽입·추출 모드는 가운데 부분을 "
            "우클릭해 바꿉니다."
        ),
        ("entries/transport/item_transporter.json", "pages.1.text"): (
            "GUI에서 허용 목록과 차단 목록으로 전송 대상을 필터링할 수 있습니다."
            "$(br2)업그레이드나 수송기를 제거하려면 수송기를 웅크리고 우클릭하세요."
            "$(br2)삽입 모드에서 조절기 모드를 사용하면 인벤토리에 남겨 둘 아이템 "
            "또는 유체의 양을 지정할 수 있습니다."
        ),
        ("entries/transport/item_transporter.json", "pages.2.text"): (
            "수송기 바깥쪽 고리에 속도 업그레이드를 우클릭하면 작동 속도가 "
            "빨라지고, 효율 업그레이드를 우클릭하면 전송량이 늘어납니다."
        ),
        ("entries/transport/world_transporter.json", "text"): (
            "월드 수송기는 월드의 아이템을 인벤토리로 줍거나 인벤토리의 아이템을 "
            "월드에 떨어뜨립니다.$(br2)한 블록에 여러 종류의 수송기를 함께 둘 수 "
            "있습니다. 삽입·추출 모드는 가운데 부분을 우클릭해 바꿉니다."
        ),
        ("entries/transport/world_transporter.json", "pages.1.text"): (
            "GUI에서 허용 목록과 차단 목록으로 전송 대상을 필터링할 수 있습니다."
            "$(br2)업그레이드나 수송기를 제거하려면 수송기를 웅크리고 우클릭하세요."
            "$(br2)삽입 모드에서 조절기 모드를 사용하면 인벤토리에 남겨 둘 아이템 "
            "또는 유체의 양을 지정할 수 있습니다."
        ),
        ("entries/transport/world_transporter.json", "pages.2.text"): (
            "수송기 바깥쪽 고리에 속도 업그레이드를 우클릭하면 작동 속도가 "
            "빨라지고, 효율 업그레이드를 우클릭하면 전송량이 늘어납니다."
        ),
    }
)

GUIDE_REPLACEMENTS = (
    ("Mob Slaughter Factory", "몹 도살 공장"),
    ("Mob Imprisonment Tool", "몹 포획기"),
    ("Mob 투옥 도구", "몹 포획기"),
    ("Mob Crusher", "몹 분쇄기"),
    ("Sewage Composter", "오물 처리기"),
    ("Plant Gatherer", "식물 수확기"),
    ("Sludge Refiner", "슬러지 정제기"),
    ("Fluid Laser Base", "유체 레이저 베이스"),
    ("Ore 레이저 베이스", "광석 레이저 베이스"),
    ("Ore Laser Base", "광석 레이저 베이스"),
    ("Latex Processing Unit", "라텍스 처리 장치"),
    ("Infinity Tools", "인피니티 도구"),
    ("Infinity Backpack", "인피니티 백팩"),
    ("Infinity Hammer", "인피니티 해머"),
    ("Infinity Launcher", "인피니티 런처"),
    ("Infinity Nuke", "인피니티 핵"),
    ("Infinity", "인피니티"),
    ("마피아 투옥 도구", "몹 포획기"),
    ("MIT", "MIB"),
    ("Nuke", "인피니티 핵"),
    ("Patreon", "후원자"),
    ("AOE", "광역"),
    ("채널링", "집전"),
    ("Biofuel", "바이오연료"),
    ("Essence", "정수"),
    ("Sewage", "오물"),
    ("Sludge", "슬러지"),
    ("Fertilizer", "비료"),
    ("Latex", "라텍스"),
    ("Wither Skulls", "위더 해골"),
    ("soulsand", "영혼 모래"),
    ("Speed ​​Addons", "속도 업그레이드"),
    ("Speed Addons", "속도 업그레이드"),
    ("Efficiency Addons", "효율 업그레이드"),
    ("Tier 1", "1단계"),
    ("Tier 2", "2단계"),
    ("baby", "새끼"),
    ("milk", "착유"),
    ("water", "물"),
    ("lava", "용암"),
    ("fortune", "행운"),
    ("chop", "벌목"),
    ("harvest", "수확"),
    ("plant", "심기"),
    ("color", "색상"),
    ("latex", "라텍스"),
    ("sapplings", "묘목"),
    ("dyes", "염료"),
    ("skulls", "머리"),
    ("Mycelial", "균사"),
    ("mycelial", "균사"),
    ("heal", "회복"),
    ("dye", "염료"),
    ("Red", "빨간색"),
    ("Green", "초록색"),
    ("Blue", "파란색"),
    ("fishing", "낚시"),
    ("Power", "전력"),
    ("fungi", "균류"),
    ("cobblestone", "조약돌"),
    ("Smelting", "제련"),
    ("biofuel", "바이오연료"),
    ("essence", "정수"),
    ("void", "초과분 폐기"),
    ("refill", "자동 보충"),
    ("Beheading", "참수"),
    ("shatter", "분쇄"),
    ("Sneak+우클릭 누르기", "웅크리고 우클릭"),
    ("charge", "충전"),
    ("Poor", "조악"),
    ("Common", "일반"),
    ("Uncommon", "고급"),
    ("Rare", "희귀"),
    ("Epic", "영웅"),
    ("Legendary", "전설"),
    ("Artifact", "유물"),
    ("Shiny", "빛나는"),
    ("Loyalty", "충성"),
    ("Riptide", "급류"),
    ("Channeling", "집전"),
    ("upgrades", "업그레이드"),
)

SOURCE_OVERRIDES = {
    (
        "Imbued with unknown technology, this block will spawn $(6)mobs$() at a "
        "fast rate when certain conditions are met.$(br2)Firstly, it requires "
        "$(6)1000$()RF and $(6)20mb$() of $(6)Liquid Meat$() per operation, "
        "secondly, normal mob spawn conditions have to be met (this means the light "
        "level has to be $(6)7$() or lower and the block has to be loaded)$(br2)"
    ): (
        "알 수 없는 기술이 깃든 이 블록은 조건을 충족하면 $(6)몹$()을 빠르게 "
        "생성합니다.$(br2)작업할 때마다 $(6)1000$()RF와 $(6)액상 고기$() "
        "$(6)20mb$()가 필요합니다. 또한 일반적인 몹 생성 조건을 충족해야 하므로 "
        "조명 밝기가 $(6)7$() 이하이고 블록이 로드되어 있어야 합니다.$(br2)"
    ),
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


def find_jars(instance: Path) -> tuple[Path, Path, Path, Path]:
    main = sorted((instance / "mods").glob("industrialforegoing-*.jar"))
    souls = sorted((instance / "mods").glob("industrial-foregoing-souls-*.jar"))
    mifa = sorted((instance / "mods").glob("mifa-neoforge-*.jar"))
    soulplied = sorted((instance / "mods").glob("soulplied_energistics-*.jar"))
    if any(len(matches) != 1 for matches in (main, souls, mifa, soulplied)):
        raise RuntimeError(
            "JAR을 확정하지 못했습니다: "
            f"main={main}, souls={souls}, mifa={mifa}, soulplied={soulplied}"
        )
    return main[0], souls[0], mifa[0], soulplied[0]


def prepare() -> dict[str, object]:
    """현재 JAR에서 영어·일본어 가이드와 발전 과제 범위를 준비한다."""
    instance = resolve_source_root()
    main_jar, souls_jar, mifa_jar, soulplied_jar = find_jars(instance)
    files = 0
    japanese_files = 0
    advancement_rows: list[dict[str, object]] = []
    for jar in (main_jar, souls_jar, mifa_jar, soulplied_jar):
        with ZipFile(jar) as archive:
            for name in sorted(archive.namelist()):
                if name.startswith(BOOK_PREFIX) and name.endswith(".json"):
                    relative = name.removeprefix(BOOK_PREFIX)
                    write_json(ENGLISH_ROOT / relative, json.loads(archive.read(name)))
                    files += 1
                elif name.startswith(JAPANESE_PREFIX) and name.endswith(".json"):
                    relative = name.removeprefix(JAPANESE_PREFIX)
                    write_json(JAPANESE_ROOT / relative, json.loads(archive.read(name)))
                    japanese_files += 1
                elif name.endswith(".json") and (
                    name.startswith(ADVANCEMENT_PREFIXES) or "/advancement/" in name
                ):
                    data = json.loads(archive.read(name))
                    display = data.get("display") if isinstance(data, dict) else None
                    advancement_rows.append(
                        {
                            "jar": jar.name,
                            "path": name,
                            "has_display": isinstance(display, dict),
                            "display": display if isinstance(display, dict) else None,
                        }
                    )
            if jar == main_jar:
                book = json.loads(archive.read(BOOK_SOURCE))
                write_json(WORK_ROOT / "book_en_us.json", book)
    write_json(WORK_ROOT / "advancements.json", advancement_rows)
    kubejs_files: list[str] = []
    visible_kubejs_literals: list[str] = []
    reference = re.compile(
        r"industrialforegoing|industrial_foregoing|industrialforegoingsouls|"
        r"industrial_foregoing_souls",
        re.I,
    )
    visible_api = re.compile(
        r"displayName|tooltip|custom_name|Text\.(?:of|translatable)|"
        r'["\'](?:text|title|description)["\']\s*:',
        re.I,
    )
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json", ".snbt"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if not reference.search(text):
            continue
        relative = path.relative_to(instance).as_posix()
        kubejs_files.append(relative)
        for number, line in enumerate(text.splitlines(), 1):
            if reference.search(line) and visible_api.search(line):
                visible_kubejs_literals.append(f"{relative}:{number}:{line.strip()}")
    report = {
        "jar": main_jar.name,
        "souls_jar": souls_jar.name,
        "mifa_jar": mifa_jar.name,
        "soulplied_jar": soulplied_jar.name,
        "english_files": files,
        "japanese_files": japanese_files,
        "advancements": len(advancement_rows),
        "advancements_with_display": sum(
            bool(row["has_display"]) for row in advancement_rows
        ),
        "kubejs_reference_files": kubejs_files,
        "kubejs_visible_literals": visible_kubejs_literals,
    }
    write_json(WORK_ROOT / "scope.json", report)
    return report


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


def set_path(value: object, path: tuple[object, ...], translated: str) -> None:
    current = value
    for part in path[:-1]:
        current = current[part]  # type: ignore[index]
    current[path[-1]] = translated  # type: ignore[index]


def item_name_map() -> dict[str, str]:
    english = language.load_json(
        PROJECT_ROOT / "working/industrial_foregoing/industrialforegoing/en_us.json"
    )
    korean = language.load_json(
        PROJECT_ROOT / "working/industrial_foregoing/industrialforegoing/ko_kr.json"
    )
    return {
        source: korean[key]
        for key, source in english.items()
        if key.startswith(("block.", "item.", "fluid_type.", "entity."))
        and isinstance(source, str)
        and isinstance(korean[key], str)
    }


def translate_value(
    source: str, cache: dict[str, object], names: dict[str, str]
) -> str:
    if source in SOURCE_OVERRIDES:
        return SOURCE_OVERRIDES[source]
    if source in CATEGORY_OVERRIDES:
        return CATEGORY_OVERRIDES[source]
    if source in names:
        return names[source]
    candidate = cache[source]
    if not isinstance(candidate, str):
        raise TypeError(f"번역 후보가 문자열이 아닙니다: {source}")
    tags: list[str] = []

    def mask_tag(match: re.Match[str]) -> str:
        tags.append(match.group(0))
        return f"ZXQPATCHOULITAG{len(tags) - 1}QXZ"

    value = PATCHOULI_TAG.sub(mask_tag, candidate)
    for old, new in language.TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    value = value.replace("에센스", "정수")
    value = value.replace("핑크 슬라임", "분홍색 슬라임")
    value = value.replace("머신", "기계")
    value = value.replace("드라이 러버", "건조 고무")
    value = value.replace("액체 고기", "액상 고기")
    value = value.replace("업그레이드을", "업그레이드를")
    for old, new in GUIDE_REPLACEMENTS:
        value = value.replace(old, new)
    for old, new in sorted(names.items(), key=lambda row: len(row[0]), reverse=True):
        value = value.replace(old, new)
    for index, tag in enumerate(tags):
        value = value.replace(f"ZXQPATCHOULITAG{index}QXZ", tag)
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    return value


def candidate() -> dict[str, object]:
    """영어 가이드 전체의 보호 처리된 번역 후보를 만든다."""
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    names = item_name_map()
    requests: set[str] = set()
    locations = 0
    for path in sorted(ENGLISH_ROOT.rglob("*.json")):
        for _, source in visible_locations(load_json(path)):
            locations += 1
            if (
                source not in CATEGORY_OVERRIDES
                and source not in SOURCE_OVERRIDES
                and source not in names
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
        raise RuntimeError("가이드 후보 생성 실패:\n" + "\n".join(failures))
    report = {
        "visible_locations": locations,
        "unique_requests": len(requests),
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


def build() -> dict[str, object]:
    """검수 규칙을 적용해 한국어 가이드와 책 표지를 만든다."""
    cache = load_json(CACHE_FILE)
    names = item_name_map()
    files = 0
    locations = 0
    changed = 0
    for source_path in sorted(ENGLISH_ROOT.rglob("*.json")):
        relative = source_path.relative_to(ENGLISH_ROOT)
        data = load_json(source_path)
        for field_path, source in visible_locations(data):
            short_override = None
            if not relative.as_posix().startswith("entries/") or field_path == (
                "pages",
                0,
                "text",
            ):
                short_override = LOCATION_OVERRIDES.get(
                    (relative.as_posix(), str(field_path[-1]))
                )
            translated = LOCATION_OVERRIDES.get(
                (relative.as_posix(), ".".join(map(str, field_path))),
                short_override or translate_value(source, cache, names),
            )
            set_path(data, field_path, translated)
            locations += 1
            changed += int(source != translated)
        write_json(KOREAN_ROOT / relative, data)
        write_json(OUTPUT_ROOT / relative, data)
        files += 1

    book = load_json(WORK_ROOT / "book_en_us.json")
    book["landing_text"] = (
        "모든 것을 자동화해야 한다면 Industrial Foregoing을 사용해 보세요! $(br2)"
        "개발자를 후원하려면 $(l:https://www.patreon.com/buuz135)여기$()를 누르세요."
    )
    write_json(BOOK_OUTPUT, book)
    report = {
        "files": files,
        "visible_locations": locations,
        "changed": changed,
        "book_override": BOOK_OUTPUT.relative_to(PROJECT_ROOT).as_posix(),
        "review_status": "full_existing_korean_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def normalize_tags(value: str) -> list[str]:
    return PATCHOULI_TAG.findall(value)


def verify() -> tuple[dict[str, object], int]:
    """가이드 구조·태그·미번역과 발전 과제 literal을 검사한다."""
    errors: list[str] = []
    untranslated: list[str] = []
    latin_residuals: list[str] = []
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
        if source.keys() != target.keys():
            errors.append(f"최상위 구조 불일치: {relative.as_posix()}")
        if target != load_json(output_path):
            errors.append(f"가이드 누적 출력 불일치: {relative.as_posix()}")
        source_locations = visible_locations(source)
        target_locations = dict(visible_locations(target))
        for field_path, source_value in source_locations:
            locations += 1
            target_value = target_locations.get(field_path)
            label = f"{relative.as_posix()}:{'.'.join(map(str, field_path))}"
            if not isinstance(target_value, str):
                errors.append(f"가이드 표시 값 누락: {label}")
                continue
            if normalize_tags(source_value) != normalize_tags(target_value):
                errors.append(f"Patchouli 태그 불일치: {label}")
            if source_value == target_value and LATIN_WORD.search(source_value):
                untranslated.append(label)
            residue = target_value
            for allowed in ALLOWED_LATIN:
                residue = residue.replace(allowed, "")
            residue = PATCHOULI_TAG.sub("", residue)
            residue = re.sub(r"https?://\S+", "", residue)
            if LATIN_WORD.search(residue):
                latin_residuals.append(f"{label}:{target_value}")
        files += 1

    advancements = json.loads(
        (WORK_ROOT / "advancements.json").read_text(encoding="utf-8")
    )
    if not isinstance(advancements, list):
        errors.append("발전 과제 감사 보고서 자료형 불일치")
        advancements = []
    displayed = [row for row in advancements if row.get("has_display")]
    if displayed:
        errors.append(f"literal 발전 과제 표시 발견: {len(displayed)}")
    scope = load_json(WORK_ROOT / "scope.json")
    kubejs_visible_literals = scope.get("kubejs_visible_literals", [])
    if kubejs_visible_literals:
        errors.append(f"KubeJS literal 표시 문구 발견: {len(kubejs_visible_literals)}")
    if untranslated:
        errors.append(f"미번역 가이드 문구: {untranslated[:20]}")
    if latin_residuals:
        errors.append(f"가이드 영어 잔존: {latin_residuals[:20]}")
    if not BOOK_OUTPUT.is_file():
        errors.append("책 표지 덮어쓰기 누락")
    report = {
        "files": files,
        "visible_locations": locations,
        "untranslated": len(untranslated),
        "latin_residuals": len(latin_residuals),
        "advancements": len(advancements),
        "advancements_with_display": len(displayed),
        "kubejs_reference_files": len(scope.get("kubejs_reference_files", [])),
        "kubejs_visible_literals": len(kubejs_visible_literals),
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
