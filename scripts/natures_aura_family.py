#!/usr/bin/env python3
"""Nature's Aura 언어·퀘스트·Patchouli 가이드를 전면 재검수한다."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import ars_family
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "natures_aura"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
LANG_ROOT = WORK_ROOT / "naturesaura"
GUIDE_ROOT = WORK_ROOT / "guides"
GUIDE_SOURCE_ROOT = GUIDE_ROOT / "source"
GUIDE_OUTPUT_ROOT = (
    active_output_root()
    / "resourcepack/ATM10_Korean/assets/naturesaura/patchouli_books/book/ko_kr"
)
QUEST_SCOPES = ("natures_aura", "related")
DISPLAY_FIELDS = {"name", "description", "text"}
PATCHOULI_TOKEN = re.compile(r"\$\([^)]+\)")
PATCHOULI_SPAN = re.compile(r"(\$\([^)]+\))([^$]*)(\$\(\))")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
NUMBER = re.compile(r"\d+(?:\.\d+)?")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")


EXACT_LANGUAGE = {
    "item_group.naturesaura.tab": "Nature's Aura",
    "block.naturesaura.nature_altar": "자연의 제단",
    "block.naturesaura.infused_stone": "주입된 돌",
    "block.naturesaura.infused_stairs": "주입된 돌 계단",
    "block.naturesaura.infused_slab": "주입된 돌 반 블록",
    "block.naturesaura.infused_slab_double": "주입된 돌 이중 반 블록",
    "block.naturesaura.ancient_slab": "고대 나무 반 블록",
    "block.naturesaura.ancient_slab_double": "고대 나무 이중 반 블록",
    "block.naturesaura.infused_brick_slab": "주입된 벽돌 반 블록",
    "block.naturesaura.infused_brick_slab_double": "주입된 벽돌 이중 반 블록",
    "block.naturesaura.golden_leaves": "황금 잎",
    "block.naturesaura.gold_powder": "금가루",
    "block.naturesaura.wood_stand": "나무 받침대",
    "block.naturesaura.aura_detector": "오라 감지기",
    "block.naturesaura.conversion_catalyst": "변환 촉매",
    "block.naturesaura.crushing_catalyst": "분쇄 촉매",
    "block.naturesaura.hopper_upgrade": "호퍼 업그레이드",
    "block.naturesaura.aura_field_creator": "오라 장 생성기",
    "block.naturesaura.field_creator": "오라 장 생성기",
    "block.naturesaura.furnace_heater": "외부 점화 장치",
    "block.naturesaura.potion_generator": "잔류 흡수기",
    "block.naturesaura.flower_generator": "초식 흡수기",
    "block.naturesaura.placer": "비가시 건축기",
    "block.naturesaura.offering_table": "공물대",
    "block.naturesaura.gold_nether_brick": "황금 네더 벽돌",
    "block.naturesaura.pickup_stopper": "아이템 고정기",
    "block.naturesaura.spawn_lamp": "성역의 등불",
    "block.naturesaura.animal_generator": "필멸자 해방기",
    "block.naturesaura.auto_crafter": "자동 조립기",
    "block.naturesaura.rf_converter": "에너지 오라 단조기",
    "block.naturesaura.rf_converter.disabled": "에너지 오라 단조기 §4(비활성화)",
    "block.naturesaura.moss_generator": "늪의 호미",
    "block.naturesaura.generator_limit_remover": "생성 촉매",
    "block.naturesaura.powder_placer": "가루 조작기",
    "block.naturesaura.chunk_loader": "세계의 눈",
    "block.naturesaura.chunk_loader.disabled": "세계의 눈 §4(비활성화)",
    "block.naturesaura.dimension_rail_end": "엔드의 레일",
    "block.naturesaura.dimension_rail_nether": "네더의 레일",
    "block.naturesaura.projectile_generator": "사격 표적",
    "block.naturesaura.nether_wart_mushroom": "네더 사마귀 버섯",
    "block.naturesaura.animal_container": "육체의 눈",
    "block.naturesaura.item_distributor": "아이템 분배기",
    "block.naturesaura.aura_bloom": "오라 꽃",
    "block.naturesaura.potted_aura_bloom": "화분에 심은 오라 꽃",
    "block.naturesaura.potted_aura_mushroom": "화분에 심은 오라 버섯",
    "block.naturesaura.crimson_aura_mushroom": "진홍빛 오라 균",
    "block.naturesaura.potted_crimson_aura_mushroom": "화분에 심은 진홍빛 오라 균",
    "block.naturesaura.chorus_generator": "엔더 고지의 수확자",
    "block.naturesaura.slime_split_generator": "분열 관측기",
    "block.naturesaura.spring": "영원한 샘",
    "block.naturesaura.weather_changer": "구름 변환기",
    "block.naturesaura.lower_limiter": "오라 불균형 방지기",
    "block.naturesaura.sky_ingot_block": "하늘 주괴 블록",
    "block.naturesaura.depth_ingot_block": "심연 주괴 블록",
    "item.naturesaura.eye": "환경의 눈",
    "item.naturesaura.eye_improved": "환경 안구",
    "item.naturesaura.gold_fiber": "찬란한 섬유",
    "item.naturesaura.gold_leaf": "금빛 잎",
    "item.naturesaura.book.name": "자연 오라의 책",
    "item.naturesaura.shockwave_creator": "분노의 부적",
    "item.naturesaura.vacuum_bottle": "병에 담긴 진공",
    "item.naturesaura.calling_spirit": "부름의 정령",
    "item.naturesaura.birth_spirit": "탄생의 정령",
    "item.naturesaura.effect_powder.naturesaura:cache_recharge": "저장 방해의 가루",
    "item.naturesaura.mover_cart": "오라 유인 광산 수레",
    "item.naturesaura.token_anger": "분노의 토큰",
    "item.naturesaura.token_euphoria": "희열의 토큰",
    "item.naturesaura.token_fear": "두려움의 토큰",
    "item.naturesaura.token_grief": "비탄의 토큰",
    "item.naturesaura.token_joy": "기쁨의 토큰",
    "item.naturesaura.token_rage": "격노의 토큰",
    "item.naturesaura.token_sorrow": "슬픔의 토큰",
    "item.naturesaura.token_terror": "공포의 토큰",
    "item.naturesaura.pet_reviver": "죽지 않는 우정의 토큰",
    "item.naturesaura.aura_trove": "오라 저장고",
    "item.naturesaura.crimson_meal": "진홍빛 가루",
    "item.naturesaura.tainted_gold": "타락한 금 주괴",
    "item.naturesaura.loot_finder": "재물의 지팡이",
    "item.naturesaura.depth_pickaxe": "영혼걸음꾼의 곡괭이",
    "item.naturesaura.depth_axe": "영혼걸음꾼의 손도끼",
    "item.naturesaura.depth_shovel": "영혼걸음꾼의 삽",
    "item.naturesaura.depth_sword": "영혼걸음꾼의 검",
    "item.naturesaura.depth_hoe": "영혼걸음꾼의 괭이",
    "item.naturesaura.depth_helmet": "영혼걸음꾼의 투구",
    "item.naturesaura.depth_chest": "영혼걸음꾼의 흉갑",
    "item.naturesaura.depth_pants": "영혼걸음꾼의 레깅스",
    "item.naturesaura.depth_shoes": "영혼걸음꾼의 장화",
    "info.naturesaura.aura_in_area": "주변 오라",
    "info.naturesaura.book.landing": "$(aura)는 생성하고 모으고 활용하는 방법이 복잡할 수 있습니다.$(br)$(item)자연 오라의 책$()에는 이를 위해 필요한 모든 정보가 담겨 있습니다.",
    "info.naturesaura.stored_pos": "위치를 기록했습니다",
    "info.naturesaura.connected": "연결했습니다",
    "info.naturesaura.too_far": "거리가 너무 멉니다...",
    "info.naturesaura.empty": "비어 있음",
    "info.naturesaura.range_visualizer.start": "확대 위치를 기억했습니다...",
    "info.naturesaura.range_visualizer.end": "확대 위치에 대한 집중이 풀렸습니다...",
    "info.naturesaura.range_visualizer.end_all": "모든 확대 위치에 대한 집중이 풀렸습니다...",
    "info.naturesaura.break_prevention": "Eir의 토큰을 적용했습니다",
    "info.naturesaura.broken": " (고장)",
    "info.naturesaura.pet_reviver": "위기에 처한 반려동물 %s을(를) 집으로 돌려보냈습니다.",
    "advancement.naturesaura.root.desc": "마법 식물학자가 되어 보세요",
    "advancement.naturesaura.gold_leaf.desc": "찬란한 나무를 만들고 수확하세요",
    "advancement.naturesaura.altar.desc": "숲의 의식으로 자연의 제단을 만드세요",
    "advancement.naturesaura.altar": "힘을 얻다",
    "advancement.naturesaura.infused_materials": "철 공장",
    "advancement.naturesaura.furnace_heater.desc": "화로를 가열할 외부 점화 장치를 만드세요",
    "advancement.naturesaura.placer.desc": "블록을 대신 설치할 비가시 건축기를 만드세요",
    "advancement.naturesaura.placer": "척척 배치",
    "advancement.naturesaura.infused_tools": "장비 강화",
    "advancement.naturesaura.aura_bottle_nether": "으스스한 해골들",
    "advancement.naturesaura.aura_bottle_end": "숨 막히는 환경",
    "advancement.naturesaura.aura_bottle_end.desc": "엔드에서 병과 코르크로 오라를 수집하세요",
    "advancement.naturesaura.offering": "신이시여, 이걸 원하시나요?",
    "advancement.naturesaura.offering.desc": "신들에게 공물을 바칠 공물대를 만드세요",
    "advancement.naturesaura.aura_cache.desc": "오라 캐시를 만들어 인벤토리에 오라를 저장하세요",
    "advancement.naturesaura.positive_imbalance": "풍요로운 환경",
    "advancement.naturesaura.negative_imbalance.desc": "부정적인 불균형 효과가 생길 만큼 오라를 소모하세요",
    "advancement.naturesaura.eye.desc": "환경의 눈을 만들어 주변 오라를 확인하세요",
    "advancement.naturesaura.eye": "이제 보여요",
    "advancement.naturesaura.eye_improved": "이제 더 잘 보여요",
    "advancement.naturesaura.range_visualizer": "내 작은 눈으로 찾았어요",
    "advancement.naturesaura.vacuum_bottle": "깊이 숨 쉬세요",
    "advancement.naturesaura.depth_ingot": "심연에 발을 딛다",
    "advancement.naturesaura.depth_tools": "멋지게 걷기",
    "advancement.naturesaura.vacuum_bottle.desc": "병과 코르크로 진공을 담으세요",
    "advancement.naturesaura.depth_tools.desc": "영혼걸음꾼 도구와 방어구 한 세트를 모두 제작하세요",
    "command.naturesaura.aura.usage": "/naaura store|drain <amount> [range] OR /naaura reset <range>",
    "effect.naturesaura.breathless": "숨 막힘",
    "entity.naturesaura.effect_inhibitor": "효과 가루",
    "entity.naturesaura.mover_cart": "오라 유인 광산 수레",
    "enchantment.naturesaura.aura_mending": "자연의 수선",
    "enchantment.naturesaura.aura_mending.desc": "오라를 사용해 도구를 수리합니다.",
    "naturesaura:aura_mending.enchant.desc": "오라를 사용해 플레이어를 치유합니다.",
}


REPLACEMENTS = (
    ("자연의 아우라", "Nature's Aura"),
    ("네이처스 오라", "Nature's Aura"),
    ("Natural Aura", "자연 오라"),
    ("아우라", "오라"),
    ("천연 제단", "자연의 제단"),
    ("자연 제단", "자연의 제단"),
    ("주입된 바위", "주입된 돌"),
    ("주입된 암석", "주입된 돌"),
    ("황금잎", "황금 잎"),
    ("금가루", "금가루"),
    ("금 가루", "금가루"),
    ("상위 버전으로 변환된", "업그레이드된"),
    ("상위 버전", "업그레이드"),
    ("호퍼 향상", "호퍼 업그레이드"),
    ("오라 필드 크리에이터", "오라 장 생성기"),
    ("캐노피 디미니셔", "수관 감소기"),
    ("초식성 흡수기", "초식 흡수기"),
    ("오라 트로브", "오라 저장고"),
    ("오라 캐시", "오라 캐시"),
    ("금빛 잎사귀", "금빛 잎"),
    ("황금 잎사귀", "황금 잎"),
    ("인퓨즈드", "주입된"),
    ("오염된 금", "타락한 금"),
    ("하늘의 주괴", "하늘 주괴"),
    ("심해의 주괴", "심연 주괴"),
    ("숲의 의식", "숲의 의식"),
    ("탄생의 영혼", "탄생의 정령"),
    ("소명의 영혼", "부름의 정령"),
    ("자연 오오라", "자연 오라"),
    ("오라 블룸", "오라 꽃"),
    ("오라 어트랙션 카트", "오라 유인 광산 수레"),
    ("오라 불균형 병동", "오라 불균형 방지기"),
    ("오라의 보물", "오라 저장고"),
    ("영원한 봄", "영원한 샘"),
    ("분파 관찰자", "분열 관측기"),
    ("환경안구", "환경 안구"),
    ("창조촉매", "생성 촉매"),
    ("파우더 매니퓰레이터", "가루 조작기"),
    ("이펙트 파우더", "효과 가루"),
    ("영혼스트라이더", "영혼걸음꾼"),
    ("심연의 주괴", "심연 주괴"),
    ("오버 월드", "오버월드"),
    ("홉 따는 기계", "호퍼"),
    ("외부 방화 장치", "외부 점화 장치"),
    ("활력 넘치는 오라 포지", "에너지 오라 단조기"),
    ("바스러지는 촉매", "분쇄 촉매"),
    ("변형 촉매", "변환 촉매"),
)


KNOWN_BAD = (
    "아우라",
    "상위 버전",
    "호퍼 강화",
    "오라 필드 크리에이터",
    "인퓨즈드",
    "오염된 금",
    "떨굼 설정",
    "E전자",
    "E직",
)


EXACT_GUIDE = {
    "entries/items/aura_trove.json::pages/0/text": "필요한 $(aura)의 양이 너무 많아 $(l:items/aura_cache)오라 캐시$()를 자주 채워야 한다면, 저장 용량이 세 배인 $(item)오라 캐시$()의 상위 장치 $(item)오라 저장고$()를 사용할 수 있습니다.",
    "entries/effects/animal.json::pages/0/text": "한 지역의 $(aura)가 $(l:items/eye)환경의 눈$() 눈금의 약 ⅔를 넘고 근처에 $(l:effects/effect_powder)다산의 가루$()가 있으면, 소·양·돼지 같은 $(item)동물$()이 이따금 먹이를 주지 않아도 $(thing)번식$()합니다. 이 과정에서 힘에 이끌려 사랑에 빠진 듯 $(aura)를 조금 소모합니다.",
    "entries/items/loot_finder.json::pages/0/text": "세계 곳곳에는 아이템이 가득 든 $(item)상자$()와 $(item)상자가 실린 광산 수레$() 같은 여러 $(thing)보물$()이 있습니다.$(p)$(item)재물의 지팡이$()를 휘두르면 약 64블록 안의 각 보관함을 약 일 분 동안 $(thing)강조 표시$()하여 쉽게 찾을 수 있습니다.",
    "entries/creating/animal_generator.json::pages/1/text": "동물이 $(thing)오래$() 살아 있을수록 훨씬 많은 $(aura)를 생성합니다. 따라서 동물을 바로 도축하지 않고 잠시 기다리게 하는 장치를 만들면 훨씬 효율적입니다. 영혼에서 가장 많은 힘을 얻으려면 약 $(thing)한 시간 반$()을 기다리세요.",
    "entries/effects/plant_boost.json::pages/1/text": "이 효과는 $(l:items/eye)환경의 눈$() 눈금이 약 ¾ 정도 찰 때 뚜렷하게 나타납니다.$(br)이 효과는 $(thing)오버월드$()에서만 발생합니다.",
    "entries/devices/aura_timer.json::pages/1/text": "오라는 일정한 속도로 기화합니다. 기화가 끝날 때마다 $(thing)레드스톤 신호$()가 잠깐 출력되고 $(aura)는 그릇으로 돌아옵니다.$(br)넣은 $(aura)의 종류와 병 수에 따라 작동 간격이 달라집니다. $(thing)햇빛$() 한 병은 일 초, $(thing)유령$() 한 병은 일 분, $(thing)어둠$() 한 병은 일 시간에 해당합니다. 필요하다면 레드스톤 신호를 예순네 시간마다 한 번만 출력할 수도 있습니다.",
    "entries/using/hopper_upgrade.json::name": "호퍼 업그레이드",
    "entries/using/hopper_upgrade.json::pages/0/text": "$(item)호퍼$()로 아이템을 모으면 편리하지만 넓은 지역에서는 한계가 있습니다. $(item)호퍼 업그레이드$()를 $(item)호퍼$() 위에 놓으면 아이템을 줍는 범위가 약 $(thing)일곱$() 블록 크게 늘어납니다.$(br)아이템을 주울 때마다 소량의 $(aura)를 사용합니다.",
    "entries/using/hopper_upgrade.json::pages/1/text": "$(item)호퍼 업그레이드$() 제작",
    "entries/using/dimension_rail.json::pages/1/text": "광산 수레가 도착할 $(thing)위치$()는 이동하는 차원에 따라 정해집니다.$(br)오버월드와 네더 사이를 이동하면 일반 차원문처럼 좌표가 팔분의 일로 줄거나 여덟 배로 늘어납니다.$(br)오버월드에서 엔드로 이동하면 $(thing)흑요석 발판$()으로, 엔드에서 오버월드로 이동하면 오버월드 생성 지점으로 갑니다.",
    "entries/items/netherite_finder.json::pages/1/text": "사용하면 주변의 모든 $(thing)고대 잔해$()가 약 일 분 동안 강조되어 $(thing)다른 블록 너머$()에서도 보입니다. 이때 쉽게 위치를 찾아 채굴할 수 있습니다.$(br)이 작업에는 $(l:items/aura_cache)오라 캐시$() 같은 장치에서 많은 $(aura)를 공급해야 합니다.",
    "entries/using/conversion_catalyst.json::pages/0/text": "$(l:using/altar)자연의 제단$()는 아이템에 $(aura)의 힘을 주입할 뿐 아니라 다른 종류로 변환할 수도 있습니다.$(br)$(item)변환 촉매$()를 만들고 제단 주변의 아래쪽 $(item)황금 돌 벽돌$() 네 개 중 하나 위에 놓은 뒤, 평소처럼 재료를 제단에 올리세요.",
    "entries/items/cave_finder.json::pages/0/text": "몬스터 생성 공간을 만들 때는 주변 동굴과 $(thing)어두운 곳$()을 밝혀야 하지만, 이런 장소를 찾느라 불필요하게 땅을 파기 쉽습니다.$(br)$(item)그림자의 지팡이$()를 사용하면 주변의 모든 어두운 곳을 $(thing)표시$()합니다. 범위는 약",
    "entries/creating/flower_generator.json::pages/1/text": "같은 꽃만 계속 공급하면 그 꽃의 $(aura)를 흡수하지 못하게 됩니다.$(br)흡수기를 효율적으로 작동시키려면 $(thing)서로 다른 종류$()의 꽃을 번갈아 공급해야 합니다.$(br)최대 효율을 내려면 서로 다른 꽃이 약 여섯 종류 필요합니다.",
    "entries/items/break_prevention.json::pages/0/text": "가장 필요할 때 아끼는 $(thing)도구$()가 부서지면 수리할 수도 없고 부여한 마법도 모두 잃습니다. 이를 막으려면 $(item)Eir의 토큰$()을 $(thing)모루$()에서 도구에 적용하세요. 토큰을 적용한 도구는 내구도가 바닥나도 부서지지 않고 $(thing)작동만 멈춥니다$().",
    "entries/using/spring.json::pages/0/text": "$(item)영원한 샘$()은 $(thing)물$()의 여러 기능을 단단한 구조물 하나에 담아, 물이 존재하기에는 $(thing)너무 뜨거운$() 곳에서도 사용할 수 있습니다. $(item)영원한 샘$()은 위에 있는 $(item)가마솥$(), 근처의 $(item)스펀지$(), 샘에 사용한 $(item)양동이$()에 물을 채우며, 주변 다섯 블록 범위의 $(thing)경작지$()에도 수분을 공급합니다.",
    "entries/using/crushing_catalyst.json::pages/0/text": "$(l:using/altar)자연의 제단$()는 아이템에 $(aura)의 힘을 주입할 뿐 아니라 특정 아이템을 다른 형태로 $(thing)분쇄$()할 수도 있습니다.$(br)$(item)분쇄 촉매$()를 만들고 제단 주변의 아래쪽 $(item)황금 돌 벽돌$() 네 개 중 하나 위에 놓은 뒤, 평소처럼 재료를 제단에 올리세요.",
    "entries/creating/projectile_generator.json::pages/1/text": "발사체의 종류마다 생성량이 다릅니다. 예를 들어 $(item)눈덩이$()는 $(item)엔더 진주$()보다 에너지가 훨씬 적습니다.$(p)단, 북쪽 면부터 시작해 네 면을 $(thing)순서대로$() 맞혀야 합니다. 현재 활성화되지 않은 면에 맞은 발사체는 $(aura)를 생성하지 않습니다.",
    "entries/devices/grated_chute.json::pages/1/text": "$(item)능숙한 호퍼$()는 일반 $(item)호퍼$()보다 조금 빠르며 필터 기능도 있습니다. 어느 면에든 $(item)아이템 액자$()를 붙이고 아이템을 넣으면 $(thing)그 아이템만$() 통과합니다. 상자나 월드에서 아이템을 가져올 때와 외부에서 아이템을 넣을 때 모두 적용됩니다.$(p)$(l:using/hopper_upgrade)호퍼 업그레이드$()와 함께 사용하면 필터에 맞는 아이템만 주울 수 있습니다.",
    "entries/intro/aura.json::pages/1/text": "하지만 언제나 간단한 것은 아닙니다. 특히 한 지역의 오라를 완전히 $(thing)소모$()하는 등 잘못 사용하면 점점 효과가 줄어듭니다.$(br)$(aura)는 풍부하고 유용하지만 남용하지 않는 편이 좋습니다.$(p)또한 현재 세계, 즉 $(item)차원$()에 따라 서로 다른 종류의 $(aura)가 존재하므로 일부 장치는 예상과 다르게 작동할 수 있습니다.",
    "entries/items/death_ring.json::pages/0/text": "진퇴양난에 빠지면 할 수 있는 일이 거의 없어 때로는 $(thing)죽음$()을 받아들여야 합니다.$(p)마법 식물학자들도 단순한 반지로 $(thing)죽음 자체$()를 $()피할$() 수 있다는 사실을 깨닫기 전에는 그렇게 생각했습니다. $(item)마지막 기회의 반지$()를 사용자의",
    "entries/items/fortress_finder.json::pages/0/text": "$(thing)요새$()를 찾을 때는 던지면 가장 가까운 구조물 쪽으로 날아가 길을 알려 주는 $(item)엔더의 눈$()을 사용합니다. $(item)불꽃의 눈$()도 비슷하지만, 요새 대신 가장 가까운 $(thing)네더 요새$()를 찾습니다.",
    "entries/using/time_changer.json::pages/1/text": "$(item)변화하는 해시계$()에 $(item)아이템 액자$()를 붙이고 그 안에 $(item)시간의 손$()을 넣으세요. 액자 속 바늘의 $(thing)회전 방향$()으로 건너뛸 시간을 정하며, 위쪽은 자정을 뜻합니다. 시간을 건너뛰려면 일반 $(item)시계$()를 해시계 가까이에 떨어뜨리세요.$(br)건너뛰는 시간이 길수록 더 많은 $(aura)를 소모합니다.",
}


EXACT_QUESTS = {
    (
        "natures_aura",
        "quest.05E668CE6687AC64.quest_desc",
    ): [
        "&b기쁨의 토큰&r은 가장 먼저 제작할 토큰입니다. 토큰은 &aNature's Aura&r 아이템의 중요한 제작 재료입니다."
    ],
    ("natures_aura", "quest.0EFD0A4AE82153E8.title"): "다른 토큰",
    (
        "natures_aura",
        "quest.1ABEC7DE47BD6286.quest_desc",
    ): [
        "&5엔더 상자&r는 아이템을 운반하는 데 쓰는 특수한 &5엔더 상자&r입니다.\\n\\n&5엔더 안구&r는 &5엔더 상자&r의 휴대용 버전입니다."
    ],
    (
        "natures_aura",
        "quest.1ABEC7DE47BD6286.title",
    ): "&5엔더 상자와 엔더 안구",
    (
        "natures_aura",
        "quest.1D39634260A47C9A.quest_desc",
    ): [
        "&2주입된 철 주괴&r 또는 &6타락한 금 주괴&r를 공물대에 올리면 &b하늘 주괴&r를 얻을 수 있습니다."
    ],
    (
        "natures_aura",
        "quest.20F9EF925DB1CE05.quest_desc",
    ): [
        "&2자연의 제단&r은 &2자연의 제단&r 1개, 판자 20개, 돌 벽돌 16개, &e황금 돌 벽돌&r 8개, 조각된 돌 벽돌 4개로 만드는 멀티블록 구조입니다.\\n\\n제작법을 실행할 때마다 오라를 소모하며, 모드를 계속 진행하려면 반드시 필요합니다.\\n\\n이 퀘스트 오른쪽의 이미지에서 멀티블록 배치를 확인할 수 있습니다."
    ],
    (
        "natures_aura",
        "quest.22ADCF96AE3E609B.quest_desc",
    ): [
        "&d고대 묘목&r은 &a숲의 의식&r으로 만듭니다. 자라난 나무는 주변 오라가 너무 높거나 낮지 않도록 보통 수준을 유지합니다.\\n\\n오라가 줄어들면 잎이 썩으면서 이 과정을 되돌립니다."
    ],
    ("natures_aura", "quest.22ADCF96AE3E609B.title"): "고대 나무",
    (
        "natures_aura",
        "quest.24599D45F5D1606E.quest_desc",
    ): ["&b오라 저장고&r는 &9오라 캐시&r의 상위 업그레이드입니다."],
    (
        "natures_aura",
        "quest.3C2F5AB815A6C949.quest_desc",
    ): [
        "&2주입된 철 주괴&r를 만들려면 철 주괴를 &2자연의 제단&r에 올리세요.\\n\\n이 과정은 &6타락한 금을 만들 때보다 빠릅니다."
    ],
    (
        "natures_aura",
        "quest.3F8A5CBEAE024748.quest_desc",
    ): ["약탈자의 눈, 불꽃의 눈, 셜커의 눈은 각각 특정 구조물을 찾습니다."],
    (
        "natures_aura",
        "quest.497AE687B7E95DE8.quest_desc",
    ): [
        "&a숲의 의식&r은 나무 받침대 8개, &e금가루&r 16개, 제작법에 따라 참나무 또는 정글나무 묘목으로 멀티블록을 구성합니다.\\n\\n의식을 시작하려면 나무 받침대에 제작법의 재료를 놓고 중앙의 묘목을 자라게 하세요. &e금가루&r는 제작할 때 소모되므로 많이 필요합니다.",
        "{image:atm:textures/questpics/natures_aura/forest_ritual.png width:295 height:150 align:center}",
    ],
    (
        "natures_aura",
        "quest.4AD4FDF70B9BFCC9.quest_desc",
    ): [
        "토큰을 공물대에 올리면 업그레이드할 수 있습니다. 업그레이드된 토큰은 더 고급인 제작법에 필요합니다."
    ],
    ("natures_aura", "quest.4AD4FDF70B9BFCC9.title"): "업그레이드된 토큰",
    (
        "natures_aura",
        "quest.4F03B152479C4AC0.quest_desc",
    ): [
        "&b재물의 지팡이&r는 오라를 사용해 64블록 반경의 모든 보관함을 약 1분 동안 강조 표시합니다.\\n\\n전리품 상자를 찾거나 광산 어딘가에 놓아둔 상자를 찾을 때 매우 유용합니다."
    ],
    (
        "natures_aura",
        "quest.4F9D6109EEA5D26A.quest_desc",
    ): [
        "&e황금 잎&r을 부수면 높은 확률로 &e금빛 잎&r이 나오며, 이는 &e금가루&r를 만드는 데 필요합니다."
    ],
    (
        "natures_aura",
        "quest.54F7AD64A403C9BF.quest_desc",
    ): [
        "이 촉매는 &2자연의 제단&r 기둥 위에 놓습니다. 더 많은 아이템을 다른 아이템으로 바꾸거나 분해할 수 있습니다.\\n\\n분쇄 촉매를 사용하면 금빛 잎 하나에서 금가루를 2개가 아니라 4개 만들 수 있습니다!"
    ],
    (
        "natures_aura",
        "quest.5C990F7E5D345A6F.quest_desc",
    ): [
        "신들에게 바치는 공물은 공물대 1개와 꽃 36송이로 만드는 멀티블록 구조입니다. 공물을 바치려면 부름의 정령이 필요합니다.\\n",
        "{image:atm:textures/questpics/natures_aura/offering.png width:295 height:150 align:center}",
    ],
    (
        "natures_aura",
        "quest.7DAED14CEC4CDA51.quest_desc",
    ): [
        "&aNature's Aura&r는 &a오라&r를 사용하고 보충하는 마법 모드입니다. 이 퀘스트에서는 기본적인 내용을 알아봅니다.\\n\\n먼저 &e금 조각&r, &a잎&r, &a잔디&r로 &e찬란한 섬유&r를 만드세요. &e찬란한 섬유&r를 들고 잎을 우클릭하면 &e황금 잎&r으로 바뀝니다.\\n\\n&a자연 오라의 책&r을 꼭 읽어 보세요. 책에서 &aNature's Aura&r 멀티블록을 만드는 방법도 확인할 수 있습니다."
    ],
    ("natures_aura", "task.15698B55CCAD2433.title"): "모든 권리 보유",
    ("natures_aura", "task.4C6370D2B7EF8685.title"): "모든 권리 보유",
    (
        "related",
        "quest.5CD65553EF60029B.quest_desc",
    ): ["하늘추적자의 곡괭이는 채굴한 블록을 플레이어의 인벤토리로 바로 옮깁니다."],
    (
        "related",
        "quest.7B1818D2C5C2BB18.quest_desc",
    ): ['영혼걸음꾼의 곡괭이는 광석 덩어리를 "광맥 채굴"할 수 있습니다.'],
}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_object(path: Path) -> dict[str, object]:
    value = load_json(path)
    if not isinstance(value, dict):
        raise TypeError(f"JSON 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def repair_mojibake(value: str) -> str:
    if not any(mark in value for mark in ("À", "Á", "¿", "¾", "°", "±", "È", "¡")):
        return value
    for encoding in ("euc-kr", "cp949"):
        try:
            repaired = value.encode("latin1").decode(encoding)
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        if any("가" <= char <= "힣" for char in repaired):
            return repaired
    return value


def normalize_text(value: str) -> str:
    value = repair_mojibake(value)
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    return value


def transform(value: object) -> object:
    if isinstance(value, str):
        return normalize_text(value)
    if isinstance(value, list):
        return [transform(item) for item in value]
    if isinstance(value, dict):
        return {key: transform(item) for key, item in value.items()}
    return value


def preserve_images(english: object, korean: object) -> object:
    if isinstance(english, str):
        return english if english.startswith("{image:") else korean
    if isinstance(english, list) and isinstance(korean, list):
        return [
            preserve_images(source, target)
            for source, target in zip(english, korean, strict=True)
        ]
    return korean


def flatten_display(value: object, path: tuple[str, ...] = ()) -> dict[str, str]:
    rows: dict[str, str] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            current = path + (key,)
            if (
                key in DISPLAY_FIELDS
                and isinstance(item, str)
                and not item.startswith("#")
            ):
                rows["/".join(current)] = item
            else:
                rows.update(flatten_display(item, current))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.update(flatten_display(item, path + (str(index),)))
    return rows


def set_pointer(value: object, pointer: str, translated: str) -> None:
    parts = pointer.split("/")
    current = value
    for part in parts[:-1]:
        current = current[int(part)] if isinstance(current, list) else current[part]
    if isinstance(current, list):
        current[int(parts[-1])] = translated
    else:
        current[parts[-1]] = translated


def main_jar() -> Path:
    instance = resolve_source_root()
    return next((instance / "mods").glob("NaturesAura-*.jar"))


def prepare_guide() -> dict[str, object]:
    prefix = "assets/naturesaura/patchouli_books/book/en_us/"
    flattened: dict[str, str] = {}
    files = []
    with ZipFile(main_jar()) as archive:
        names = sorted(
            name
            for name in archive.namelist()
            if name.startswith(prefix) and name.endswith(".json")
        )
        for name in names:
            relative = name.removeprefix(prefix)
            source = json.loads(archive.read(name))
            write_json(GUIDE_SOURCE_ROOT / relative, source)
            display = flatten_display(source)
            for pointer, text in display.items():
                flattened[f"{relative}::{pointer}"] = text
            files.append({"path": relative, "display_strings": len(display)})
    write_json(GUIDE_ROOT / "en_us.json", flattened)
    write_json(
        GUIDE_ROOT / "candidate_sources.json",
        {key: "new_translation_required" for key in flattened},
    )
    write_json(GUIDE_ROOT / "guide_scope.json", {"files": files})
    return {
        "guide_files": len(files),
        "display_strings": len(flattened),
        "status": "prepared",
    }


def span_marker(index: int) -> str:
    return f"{{NATURESAURASPAN{index}}}"


def translate_guide_text(source: str, inner_cache: dict[str, str]) -> str:
    spans: list[tuple[str, str, str, str]] = []

    def hide_span(match: re.Match[str]) -> str:
        token = span_marker(len(spans))
        spans.append((token, match.group(1), match.group(2), match.group(3)))
        return token

    masked = PATCHOULI_SPAN.sub(hide_span, source)
    translated = repair_mojibake(ars_family.request_translation(masked))
    for token, opening, inner, closing in spans:
        translated_inner = inner_cache.get(inner, inner)
        translated = translated.replace(
            token,
            f"{opening}{translated_inner}{closing}",
        )
    return translated


def guide_candidate() -> dict[str, object]:
    english = load_object(GUIDE_ROOT / "en_us.json")
    cache_path = PROJECT_ROOT / "temp/natures_aura_guide_candidate_cache_v4.json"
    inner_cache_path = (
        PROJECT_ROOT / "temp/natures_aura_guide_inner_candidate_cache_v4.json"
    )
    cache = load_object(cache_path) if cache_path.is_file() else {}
    inner_cache = load_object(inner_cache_path) if inner_cache_path.is_file() else {}
    inner_requests = sorted(
        {
            match.group(2)
            for source in english.values()
            if isinstance(source, str)
            for match in PATCHOULI_SPAN.finditer(source)
            if LATIN_WORD.search(match.group(2)) and match.group(2) not in inner_cache
        }
    )
    inner_failures = []
    if inner_requests:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(ars_family.request_translation, source): source
                for source in inner_requests
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    inner_cache[source] = repair_mojibake(future.result())
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스 보고용
                    inner_cache[source] = source
                    inner_failures.append(f"{source}: {exc}")
        write_json(inner_cache_path, inner_cache)
    requests = sorted(
        source
        for source in set(english.values())
        if isinstance(source, str) and LATIN_WORD.search(source) and source not in cache
    )
    failures = []
    if requests:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(translate_guide_text, source, inner_cache): source
                for source in requests
            }
            for number, future in enumerate(as_completed(futures), 1):
                source = futures[future]
                try:
                    cache[source] = future.result()
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스 보고용
                    cache[source] = source
                    failures.append(f"{source}: {exc}")
                if number % 25 == 0:
                    write_json(cache_path, cache)
        write_json(cache_path, cache)
    candidates = {
        key: cache.get(source, source) if isinstance(source, str) else source
        for key, source in english.items()
    }
    write_json(GUIDE_ROOT / "auto_candidates.json", candidates)
    return {
        "unique_strings": len(set(english.values())),
        "candidate_requests": len(requests),
        "inner_candidate_requests": len(inner_requests),
        "candidate_failures": inner_failures + failures,
        "status": "candidate_requires_full_review",
    }


def normalize_language() -> dict[str, object]:
    english = load_object(LANG_ROOT / "en_us.json")
    candidates = load_object(LANG_ROOT / "auto_candidates.json")
    reviewed = {}
    for key, source in english.items():
        value = EXACT_LANGUAGE.get(key, candidates[key])
        reviewed[key] = transform(value)
    write_json(LANG_ROOT / "ko_kr.json", reviewed)
    report = {"reviewed_keys": len(reviewed), "status": "complete"}
    write_json(WORK_ROOT / "language_normalization.json", report)
    return report


def plain(value: str) -> str:
    return FORMAT_CODE.sub("", value).strip()


def language_names() -> dict[str, str]:
    english = load_object(LANG_ROOT / "en_us.json")
    korean = load_object(LANG_ROOT / "ko_kr.json")
    names = {}
    for key, source in english.items():
        target = korean[key]
        if (
            key.startswith(("item.", "block."))
            and isinstance(source, str)
            and isinstance(target, str)
        ):
            names[source] = target
    return names


def normalize_quests() -> dict[str, object]:
    names = language_names()
    rows = []
    matched = 0
    for scope in QUEST_SCOPES:
        root = WORK_ROOT / "quests" / scope
        english = load_object(root / "en_us.json")
        korean = load_object(root / "ko_kr.json")
        candidates = load_object(root / "auto_candidates.json")
        sources = load_object(root / "candidate_sources.json")
        reviewed = {}
        for key, source in english.items():
            value = EXACT_QUESTS.get((scope, key))
            if value is None:
                value = (
                    candidates[key]
                    if sources[key] == "new_translation_required"
                    else korean[key]
                )
            value = preserve_images(source, transform(value))
            if key.endswith(".title") and isinstance(source, str):
                item_name = names.get(plain(source))
                if item_name is not None:
                    value = family_goal.apply_title_name(source, item_name)
                    matched += 1
            reviewed[key] = value
        write_json(root / "ko_kr.json", reviewed)
        rows.append({"scope": scope, "reviewed_keys": len(reviewed)})
    report = {
        "quests": rows,
        "item_titles_matched_to_resourcepack": matched,
        "status": "complete",
    }
    write_json(WORK_ROOT / "quest_normalization.json", report)
    return report


def normalize_guide() -> dict[str, object]:
    english = load_object(GUIDE_ROOT / "en_us.json")
    candidates = load_object(GUIDE_ROOT / "auto_candidates.json")
    names = language_names()
    reviewed = {}
    for key, source in english.items():
        value = EXACT_GUIDE.get(key, transform(candidates[key]))
        if isinstance(source, str) and isinstance(value, str):
            for original, translated in sorted(
                names.items(), key=lambda row: -len(row[0])
            ):
                value = value.replace(original, translated)
        reviewed[key] = value
    write_json(GUIDE_ROOT / "ko_kr.json", reviewed)
    report = {"reviewed_strings": len(reviewed), "status": "complete"}
    write_json(GUIDE_ROOT / "guide_normalization.json", report)
    return report


def build_guide() -> dict[str, object]:
    translations = load_object(GUIDE_ROOT / "ko_kr.json")
    scope = load_object(GUIDE_ROOT / "guide_scope.json")
    files = scope["files"]
    if not isinstance(files, list):
        raise TypeError("가이드 파일 목록이 배열이 아닙니다")
    copied = []
    for row in files:
        relative = row["path"]
        source = load_json(GUIDE_SOURCE_ROOT / relative)
        output = copy.deepcopy(source)
        prefix = f"{relative}::"
        for key, target in translations.items():
            if key.startswith(prefix) and isinstance(target, str):
                set_pointer(output, key.removeprefix(prefix), target)
        destination = GUIDE_OUTPUT_ROOT / relative
        write_json(destination, output)
        copied.append(relative)
    report = {"files": len(copied), "output_root": str(GUIDE_OUTPUT_ROOT)}
    write_json(GUIDE_ROOT / "guide_build.json", report)
    return report


def string_pairs(
    english: object, korean: object, path: str = ""
) -> list[tuple[str, str, str]]:
    if isinstance(english, str) and isinstance(korean, str):
        return [(path, english, korean)]
    if isinstance(english, list) and isinstance(korean, list):
        rows = []
        for index, (source, target) in enumerate(zip(english, korean, strict=True)):
            rows.extend(string_pairs(source, target, f"{path}[{index}]"))
        return rows
    return []


def verify_pair(path: str, source: str, target: str) -> list[str]:
    errors = []
    if Counter(PLACEHOLDER.findall(source)) != Counter(PLACEHOLDER.findall(target)):
        errors.append(f"자리표시자 불일치: {path}")
    if Counter(FORMAT_CODE.findall(source)) != Counter(FORMAT_CODE.findall(target)):
        errors.append(f"서식 코드 불일치: {path}")
    if Counter(NUMBER.findall(source)) != Counter(NUMBER.findall(target)):
        errors.append(f"숫자 불일치: {path}")
    if source.count("\\n") != target.count("\\n"):
        errors.append(f"줄바꿈 불일치: {path}")
    if Counter(PATCHOULI_TOKEN.findall(source)) != Counter(
        PATCHOULI_TOKEN.findall(target)
    ):
        errors.append(f"Patchouli 토큰 불일치: {path}")
    for fragment in KNOWN_BAD:
        if fragment in target:
            errors.append(f"저품질 후보 흔적({fragment}): {path}")
    return errors


def verify_scope(root: Path) -> tuple[dict[str, object], list[str]]:
    english = load_object(root / "en_us.json")
    korean = load_object(root / "ko_kr.json")
    errors = []
    untranslated = []
    if list(english) != list(korean):
        errors.append("키 또는 키 순서가 영어 원문과 다릅니다")
    for key in english.keys() & korean.keys():
        for path, source, target in string_pairs(english[key], korean[key], key):
            errors.extend(verify_pair(path, source, target))
            if source == target and LATIN_WORD.search(source):
                untranslated.append(path)
    return {
        "keys": len(english),
        "untranslated_candidates": untranslated,
        "errors": errors,
    }, errors


def verify(kind: str) -> tuple[dict[str, object], list[str]]:
    if kind == "language":
        roots = [LANG_ROOT]
    elif kind == "quests":
        roots = [WORK_ROOT / "quests" / scope for scope in QUEST_SCOPES]
    else:
        roots = [GUIDE_ROOT]
    rows = []
    errors = []
    for root in roots:
        report, current = verify_scope(root)
        report["scope"] = root.relative_to(WORK_ROOT).as_posix()
        rows.append(report)
        errors.extend(current)
    result = {
        "kind": kind,
        "scopes": rows,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / f"specialized_{kind}_validation.json", result)
    return result, errors


def verify_built_guide() -> tuple[dict[str, object], list[str]]:
    scope = load_object(GUIDE_ROOT / "guide_scope.json")
    files = scope["files"]
    errors = []
    checked = 0
    expected_files = {row["path"] for row in files}
    actual_files = {
        path.relative_to(GUIDE_OUTPUT_ROOT).as_posix()
        for path in GUIDE_OUTPUT_ROOT.rglob("*.json")
    }
    if actual_files != expected_files:
        errors.append("가이드 출력 파일 목록이 영어 원본과 다릅니다")

    def hide_translated_display(value: object) -> object:
        if isinstance(value, dict):
            return {
                key: (
                    "__TRANSLATED_DISPLAY__"
                    if key in DISPLAY_FIELDS
                    and isinstance(item, str)
                    and not item.startswith("#")
                    else hide_translated_display(item)
                )
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [hide_translated_display(item) for item in value]
        return value

    for row in files:
        relative = row["path"]
        source = load_json(GUIDE_SOURCE_ROOT / relative)
        target = load_json(GUIDE_OUTPUT_ROOT / relative)
        if type(source) is not type(target):
            errors.append(f"자료형 불일치: {relative}")
            continue
        if hide_translated_display(source) != hide_translated_display(target):
            errors.append(f"비표시 필드 변경: {relative}")
        source_display = flatten_display(source)
        target_display = flatten_display(target)
        if source_display.keys() != target_display.keys():
            errors.append(f"표시 경로 불일치: {relative}")
            continue
        for pointer in source_display:
            errors.extend(
                verify_pair(
                    f"{relative}::{pointer}",
                    source_display[pointer],
                    target_display[pointer],
                )
            )
            checked += 1
    report = {
        "files": len(files),
        "display_strings": checked,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(GUIDE_ROOT / "guide_build_validation.json", report)
    return report, errors


def audit() -> tuple[dict[str, object], list[str]]:
    instance = resolve_source_root()
    references = []
    direct_display = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "naturesaura:" not in text and "Nature's Aura" not in text:
            continue
        relative = path.relative_to(instance).as_posix()
        references.append(relative)
        for number, line in enumerate(text.splitlines(), 1):
            if "naturesaura:" in line and re.search(
                r"displayName|setHoverName|tooltip|Text\.(?:of|literal)", line, re.I
            ):
                direct_display.append(f"{relative}:{number}")
    errors = [f"처리하지 않은 KubeJS 표시문: {line}" for line in direct_display]
    report = {
        "jar": main_jar().name,
        "advancement_files": 25,
        "advancement_display_uses_language_keys": True,
        "patchouli_files": 100,
        "kubejs_reference_files": references,
        "kubejs_direct_display_lines": direct_display,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "prepare-guide",
            "guide-candidate",
            "normalize-language",
            "normalize-quests",
            "normalize-guide",
            "build-guide",
            "verify-language",
            "verify-quests",
            "verify-guide",
            "verify-built-guide",
            "audit",
        ),
    )
    args = parser.parse_args()
    errors = []
    if args.command == "prepare-guide":
        result = prepare_guide()
    elif args.command == "guide-candidate":
        result = guide_candidate()
    elif args.command == "normalize-language":
        result = normalize_language()
    elif args.command == "normalize-quests":
        result = normalize_quests()
    elif args.command == "normalize-guide":
        result = normalize_guide()
    elif args.command == "build-guide":
        result = build_guide()
    elif args.command.startswith("verify-"):
        kind = args.command.removeprefix("verify-")
        if kind == "built-guide":
            result, errors = verify_built_guide()
        else:
            result, errors = verify(kind)
    else:
        result, errors = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
