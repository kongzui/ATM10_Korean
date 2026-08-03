#!/usr/bin/env python3
"""Theurgy 언어 파일과 전용 FTB Quests를 전면 재검수한다."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from zipfile import ZipFile

import ars_family
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "theurgy"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
LANG_ROOT = WORK_ROOT / "theurgy"
QUEST_ROOT = WORK_ROOT / "quests" / "theurgy"
CACHE_PATH = PROJECT_ROOT / "temp/theurgy_line_candidate_cache_v4.json"
PREVIOUS_CACHE_PATH = PROJECT_ROOT / "temp/theurgy_direct_candidate_cache_v3.json"
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[.,/]\d+)*")
LINK = re.compile(r"(?:\[.*?\]\([^)]*\)|\b(?:item|category|entry)://[^\s)]+)")
LINK_TARGET = re.compile(r"\]\(([^)]*)\)")
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")
TRANSLATION_TOKEN = re.compile(
    r"%(?:\d+\$)?[a-zA-Z%]|[§&][0-9A-FK-ORa-fk-or]|\]\([^)]*\)"
)

EXACT_SOURCE = {
    "Theurgy": "Theurgy",
    "The Hermetica": "헤르메티카",
    "Alchemical Salt": "연금술 소금",
    "Alchemical Sulfur": "연금술 유황",
    "Alchemical Mercury": "연금술 수은",
    "Alchemical Niter": "연금술 초석",
    "Sal Ammoniac": "염화 암모늄",
    "Mercury Flux": "수은 플럭스",
    "Caloric Flux": "열 플럭스",
    "Sulfuric Flux": "유황 플럭스",
    "Calcination Oven": "하소 오븐",
    "Mercury Distiller": "수은 증류기",
    "Distiller": "증류기",
    "Liquefaction Cauldron": "액화 가마솥",
    "Pyromantic Brazier": "화염 화로",
    "Incubator": "배양기",
    "Digestion Vat": "소화조",
    "Fermentation Vat": "발효조",
    "Mercury Catalyst": "수은 촉매",
    "Caloric Flux Emitter": "열 플럭스 방출기",
    "Sulfuric Flux Emitter": "유황 플럭스 방출기",
    "Reformation Source Pedestal": "재구성 근원 받침대",
    "Reformation Target Pedestal": "재구성 대상 받침대",
    "Reformation Result Pedestal": "재구성 결과 받침대",
    "Sal Ammoniac Accumulator": "염화 암모늄 농축기",
    "Sal Ammoniac Tank": "염화 암모늄 탱크",
    "Sal Ammoniac Ore": "염화 암모늄 광석",
    "Deepslate Sal Ammoniac Ore": "심층암 염화 암모늄 광석",
    "Mercurial Connection Node": "수은 연결 노드",
    "Mercurial Fluid Extractor": "수은 유체 추출기",
    "Mercurial Fluid Inserter": "수은 유체 삽입기",
    "Mercurial Item Extractor": "수은 아이템 추출기",
    "Mercurial Item Inserter": "수은 아이템 삽입기",
    "Mercurial Wand": "머큐리얼 지팡이",
    "Mercurial Wire": "수은 전선",
    "Divination Rod": "점봉",
    "Glass Divination Rod": "유리 점봉",
    "Iron Divination Rod": "철 점봉",
    "Diamond Divination Rod": "다이아몬드 점봉",
    "Netherite Divination Rod": "네더라이트 점봉",
    "Amethyst Divination Rod": "자수정 점봉",
    "Purified Gold": "정제된 금",
    "Fermentation Starter": "발효 종균",
    "List Filter": "목록 필터",
    "Attribute Filter": "속성 필터",
    "Accumulation": "농축",
    "Calcination": "하소",
    "Digestion": "소화",
    "Distillation": "증류",
    "Alchemical Distillation": "연금술 증류",
    "Fermentation": "발효",
    "Alchemical Fermentation": "연금술 발효",
    "Incubation": "배양",
    "Liquefaction": "액화",
    "Reformation": "재구성",
    "Transmutation": "변환",
    "Exaltation": "승급",
    "Replication": "복제",
    "Spagyrics": "스파기리아",
    "Usage": "사용법",
    "Uses": "용도",
    "Process": "과정",
    "Working Correctly": "정상 작동",
    "Redstone": "레드스톤",
    "Logistics": "물류",
    "Disabled": "비활성화",
    "Enabled": "활성화",
    "Unknown Source": "알 수 없는 원료",
    "Niter": "초석",
    "Salt": "소금",
    "Sulfur": "유황",
    "Mercury": "수은",
    "Abundant": "풍부",
    "Common": "일반",
    "Rare": "희귀",
    "Precious": "귀중",
    "Animal Parts": "동물 재료",
    "Crops": "작물",
    "Earthen Matters": "토질 재료",
    "Gems": "보석",
    "Logs": "통나무",
    "Metals": "금속",
    "Mob Drops": "몬스터 전리품",
    "Other Minerals": "기타 광물",
    (
        " Liquefaction allows the extraction of [#](ad03fc)Alchemical Sulfur[#]() "
        "from matter. In the this cauldron a [#](ad03fc)Solvent[#](), usually a type "
        "of acid, is used to dissolve the target object, then the resulting solution "
        "is heated to evaporate the solvent and leave behind the Sulfur."
    ): (
        " 액화는 물질에서 [#](ad03fc)연금술 유황[#]()을 추출하는 과정입니다. "
        "이 가마솥에서는 보통 산성 물질인 [#](ad03fc)용매[#]()로 대상 아이템을 "
        "녹인 뒤, 용액을 가열해 용매를 증발시키고 유황만 남깁니다."
    ),
    (
        "After a while some salt will have been created, you can [#](008080)right-click"
        "[#]() the [](item://theurgy:calcination_oven) with an empty hand to obtain "
        "[Mineral Salt](item://theurgy:alchemical_salt_mineral)."
    ): (
        "잠시 뒤 소금이 만들어지면, 빈손으로 [](item://theurgy:calcination_oven)을 "
        "[#](008080)우클릭[#]()해 [광물 소금](item://theurgy:alchemical_salt_mineral)"
        "을 꺼내세요."
    ),
    (
        "After a while some sulfur will have been extracted, you can [#](008080)right-"
        "click[#]() the [](item://theurgy:liquefaction_cauldron) with an empty hand to "
        "obtain [Alchemical Sulfur](item://theurgy:alchemical_sulfur_iron)."
    ): (
        "잠시 뒤 유황이 추출되면, 빈손으로 [](item://theurgy:liquefaction_cauldron)"
        "을 [#](008080)우클릭[#]()해 [연금술 유황]"
        "(item://theurgy:alchemical_sulfur_iron)을 꺼내세요."
    ),
    (
        "After, [#](008080)right-click[#]() the [](item://theurgy:sulfuric_flux_emitter) "
        "with an empty hand to see if it is linked to all the pedestals."
    ): (
        "그런 다음 빈손으로 [](item://theurgy:sulfuric_flux_emitter)를 "
        "[#](008080)우클릭[#]()해 모든 받침대에 연결됐는지 확인하세요."
    ),
    (
        "For more information on how to use these contraptions, see also "
        "[](entry://getting_started/spagyrics) in [Getting Started]"
        "(category://getting_started)."
    ): (
        "이 장치들의 자세한 사용법은 [시작하기](category://getting_started)의 "
        "[](entry://getting_started/spagyrics) 항목도 참고하세요."
    ),
    (
        "Now [#](008080)right-click[#]() the [](item://theurgy:liquefaction_cauldron) "
        "with the item you want to extract sulfur from, such as "
        "[](item://minecraft:raw_iron). The item will be placed inside."
    ): (
        "이제 [](item://minecraft:raw_iron)처럼 유황을 추출할 아이템을 든 채 "
        "[](item://theurgy:liquefaction_cauldron)을 [#](008080)우클릭[#]()해 "
        "안에 넣으세요."
    ),
    (
        "Optionally you can now [#](008080)right-click[#]() the "
        "[](item://theurgy:sal_ammoniac_accumulator) with a "
        "[](item://theurgy:sal_ammoniac_crystal) (obtained by mining). You will get "
        "Sal Ammoniac regardless, but the crystal will speed up the process significantly."
    ): (
        "선택 사항으로, 채굴해 얻은 [](item://theurgy:sal_ammoniac_crystal)을 든 채 "
        "[](item://theurgy:sal_ammoniac_accumulator)를 [#](008080)우클릭[#]()할 수 "
        "있습니다. 수정이 없어도 염화 암모늄은 만들어지지만, 넣으면 처리 속도가 "
        "크게 빨라집니다."
    ),
    (
        "You can [#](008080)right-click[#]() the [](item://theurgy:incubator) with an "
        "empty hand to obtain 3x [](item://minecraft:iron_ingot)."
    ): (
        "빈손으로 [](item://theurgy:incubator)를 [#](008080)우클릭[#]()해 "
        "[](item://minecraft:iron_ingot) 3개를 꺼내세요."
    ),
    (
        "[#](008080)Right-click[#]() the [](item://theurgy:calcination_oven) with any "
        "Mineral such as Ores, Raw Metals or Ingots to calcinate it."
    ): (
        "광석, 원석, 주괴 같은 광물을 든 채 [](item://theurgy:calcination_oven)을 "
        "[#](008080)우클릭[#]()해 하소하세요."
    ),
    (
        "[#](008080)Right-click[#]() with an empty hand to retrieve the "
        "[Alchemical Niter: Common Gems](item://theurgy:alchemical_niter_gems_common)."
    ): (
        "빈손으로 [#](008080)우클릭[#]()해 [연금술 초석: 일반 보석]"
        "(item://theurgy:alchemical_niter_gems_common)을 꺼내세요."
    ),
    (
        "[#](008080)Right-click[#]() with an empty hand to retrieve the "
        "[Alchemical Niter: Rare Metals](item://theurgy:alchemical_niter_metals_rare)."
    ): (
        "빈손으로 [#](008080)우클릭[#]()해 [연금술 초석: 희귀 금속]"
        "(item://theurgy:alchemical_niter_metals_rare)을 꺼내세요."
    ),
    (
        "[#](008080)Shift-right-click[#]() the [](item://theurgy:digestion_vat) with "
        "an [#](008080)empty hand[#]() to close the vat and start the digestion."
    ): (
        "[#](008080)빈손[#]()으로 [](item://theurgy:digestion_vat)를 "
        "[#](008080)Shift+우클릭[#]()해 통을 닫고 소화를 시작하세요."
    ),
    (
        "§aShift-right-Click§r§7 with an empty hand to close or open the vat to start "
        "or stop processing."
    ): "빈손으로 §aShift+우클릭§r§7해 통을 여닫고 가공을 시작하거나 멈추세요.",
    (
        "§aCrouch-Click§r§7 a block to attune the rod to it.\n"
        "§aRight-Click and hold§r§7 to let the rod search for blocks.\n"
        "§aRight-Click without holding§r§7 after a successful search to let the rod "
        "show the last found block without consuming durability.\n"
    ): (
        "블록을 §aShift+클릭§r§7해 점봉을 조율하세요.\n"
        "§a우클릭한 채§r§7 있으면 점봉이 블록을 찾습니다.\n"
        "검색에 성공한 뒤 §a짧게 우클릭§r§7하면 내구도를 소모하지 않고 마지막으로 "
        "찾은 블록을 표시합니다.\n"
    ),
    (
        "§aCraft§r§7 the rod with a type of Alchemical Sulfur to attune the rod to it.\n"
        "§aRight-Click and hold§r§7 to let the rod search for blocks.\n"
        "§aRight-Click without holding§r§7 after a successful search to let the rod "
        "show the last found block without consuming durability.\n"
    ): (
        "점봉을 연금술 유황과 §a제작§r§7해 해당 재료에 조율하세요.\n"
        "§a우클릭한 채§r§7 있으면 점봉이 블록을 찾습니다.\n"
        "검색에 성공한 뒤 §a짧게 우클릭§r§7하면 내구도를 소모하지 않고 마지막으로 "
        "찾은 블록을 표시합니다.\n"
    ),
    (
        "§aCraft§r§7 the rod, it is automatically attuned to Amethyst.\n"
        "§aRight-Click and hold§r§7 to let the rod search for blocks.\n"
        "§aRight-Click without holding§r§7 after a successful search to let the rod "
        "show the last found block without consuming durability.\n"
    ): (
        "점봉을 §a제작§r§7하면 자수정에 자동으로 조율됩니다.\n"
        "§a우클릭한 채§r§7 있으면 점봉이 블록을 찾습니다.\n"
        "검색에 성공한 뒤 §a짧게 우클릭§r§7하면 내구도를 소모하지 않고 마지막으로 "
        "찾은 블록을 표시합니다.\n"
    ),
    (
        "§aRight-Click§r§7 the air to open the filter GUI and add items.\n"
        "§aRight-Click§r§7 a logistics inserter or extractor to apply the filter.\n"
        "§aRight-Click§r§7 a filtered block with an empty hand to remove the filter.\n"
    ): (
        "허공을 §a우클릭§r§7해 필터 화면을 열고 아이템을 추가하세요.\n"
        "물류 삽입기나 추출기를 §a우클릭§r§7해 필터를 적용하세요.\n"
        "빈손으로 필터가 적용된 블록을 §a우클릭§r§7해 필터를 제거하세요.\n"
    ),
    (
        "Place this on top of a heating device such as a Pyromantic Brazier.\n"
        "§aRight-Click§r§7 with ingredients to add them to the distiller for processing.\n"
    ): (
        "화염 화로 같은 가열 장치 위에 놓으세요.\n"
        "재료를 든 채 §a우클릭§r§7해 증류기에 넣고 가공하세요.\n"
    ),
    (
        "Place this on top of a heating device such as a Pyromantic Brazier.\n"
        "§aRight-Click§r§7 with ingredients to add them to the cauldron for processing.\n"
    ): (
        "화염 화로 같은 가열 장치 위에 놓으세요.\n"
        "재료를 든 채 §a우클릭§r§7해 가마솥에 넣고 가공하세요.\n"
    ),
}

EXACT_KEYS = {
    "itemGroup.theurgy": "Theurgy",
    "book.theurgy.the_hermetica.name": "헤르메티카",
    "block.theurgy.calcination_oven.tooltip.usage": (
        "화염 화로 같은 가열 장치 위에 놓으세요.\n"
        "§a우클릭§r§7으로 재료를 넣으면 오븐이 가공을 시작합니다.\n"
    ),
    "block.theurgy.digestion_vat.tooltip.usage": (
        "§a우클릭§r§7으로 재료를 통에 넣으세요.\n"
        "빈손으로 §aShift+우클릭§r§7하면 통을 여닫아 가공을 시작하거나 멈춥니다.\n"
    ),
    "block.theurgy.fermentation_vat.tooltip.usage": (
        "§a우클릭§r§7으로 재료를 통에 넣으세요.\n"
        "빈손으로 §aShift+우클릭§r§7하면 통을 여닫아 가공을 시작하거나 멈춥니다.\n"
    ),
    "book.theurgy.the_hermetica.getting_started.required_items_transmutation.target.text": (
        "이제 대상 유형의 유황이 *두 개* 필요합니다.\n\\\n\\\n"
        "하나는 중간 재구성을 위해 초석으로 바꾸고, 다른 하나는 모든 초석을 대상 "
        "유황으로 최종 재구성하는 데 사용합니다.\n"
    ),
    "book.theurgy.the_hermetica.getting_started.incubation.step3.text": (
        "잠시 뒤 입력 아이템이 소모되고 결과물로 배양됩니다.\n\\\n\\\n"
        "빈손으로 [](item://theurgy:incubator)를 [#](008080)우클릭[#]()해 "
        "[](item://minecraft:iron_ingot) 3개를 꺼내세요.\n\\\n\\\n"
        "*축하합니다. 철 원석 1개로 철 주괴 3개를 만들었어요!*\n"
    ),
    "book.theurgy.the_hermetica.getting_started.required_items_exaltation.target2.text": (
        "이 설명에서는 금 유황을 사용합니다.\n\\\n\\\n"
        "*참고: 등급과 유형을 모두 바꾸려면 이전 실험처럼 대상 유형의 유황이 "
        "두 개 필요합니다.*\n"
    ),
    "book.theurgy.the_hermetica.getting_started.incubation_after_reformation.intro.text": (
        "마지막으로 석영 유황을 석영으로 배양할 수 있습니다.\n\\\n\\\n"
        "[배양](entry://getting_started/incubation)에서 배운 순서를 그대로 따르세요.\n"
    ),
    "book.theurgy.the_hermetica.getting_started.ore_refining.intro2.text": (
        "스파기리아의 첫 활용법으로 원석을 여러 주괴로 효율적으로 정제해 보겠습니다.\n"
        "다음 페이지에서는 스파기리아 공정으로 [철 원석](item://minecraft:raw_iron) "
        "*한 개*를 [철 주괴](item://minecraft:iron_ingot) *세 개*로 만들어 봅니다.\n"
    ),
    "book.theurgy.the_hermetica.getting_started.strata_recycling.refining.text": (
        "두 단계로 진행합니다:\n"
        "1. 먼저 지층 재료를 하소해 [연금술 소금 - 지층]"
        "(item://theurgy:alchemical_salt_strata)을 얻습니다.\n"
        "2. 이 소금 5개를 다시 하소해 소량의 [연금술 소금 - 광물]"
        "(item://theurgy:alchemical_salt_mineral)을 얻습니다.\n"
    ),
    "book.theurgy.the_hermetica.getting_started.result_pedestal.result2.text": (
        "대상 받침대도 [#](008080)우클릭[#]()해 원래의 [연금술 유황: 석영]"
        "(item://theurgy:alchemical_sulfur_quartz)을 회수하세요.\n\\\n\\\n"
        "[연금술 유황: 청금석](item://theurgy:alchemical_sulfur_lapis) 하나를 소모해 "
        "[연금술 유황: 석영](item://theurgy:alchemical_sulfur_quartz)을 하나 더 "
        "만들었으므로, 원하는 유황이 두 배가 됐습니다.\n"
    ),
    "book.theurgy.the_hermetica.getting_started.plant_recycling.refining.text": (
        "두 단계로 진행합니다:\n"
        "1. 먼저 작물이나 나무 같은 식물을 하소해 [연금술 소금 - 식물]"
        "(item://theurgy:alchemical_salt_plant)을 얻습니다.\n"
        "2. 이 소금 2개를 다시 하소해 소량의 [연금술 소금 - 생물]"
        "(item://theurgy:alchemical_salt_creature)을 얻습니다.\n"
    ),
    "book.theurgy.the_hermetica.getting_started.convert_to_other_tier.instructions.text": (
        "다음 항목에서는 [연금술 유황: 철](item://theurgy:alchemical_sulfur_iron)을 "
        "[연금술 유황: 금](item://theurgy:alchemical_sulfur_gold)으로 바꿉니다. "
        "*철 유황을 최소 4개, 금 유황을 하나 얻었다고 가정합니다.*\n\\\n\\\n"
        "다른 등급 사이의 모든 변환에도 같은 방법을 사용할 수 있습니다.\n"
    ),
    "book.theurgy.the_hermetica.getting_started.incubation_after_transmutation.intro.text": (
        "마지막으로 철 유황을 철 주괴로 배양할 수 있습니다.\n\\\n\\\n"
        "[배양](entry://getting_started/incubation)에서 배운 순서를 그대로 따르세요.\n"
    ),
    "book.theurgy.the_hermetica.getting_started.incubation_after_exaltation.intro.text": (
        "마지막으로 금 유황을 금 주괴로 배양할 수 있습니다.\n\\\n\\\n"
        "[배양](entry://getting_started/incubation)에서 배운 순서를 그대로 따르세요.\n"
    ),
    "book.theurgy.the_hermetica.getting_started.ore_refining.description": (
        "광석 생산량을 세 배로 늘리세요"
    ),
    "book.theurgy.the_hermetica.getting_started.credits.open_source.text": (
        "생태계와 이 모드에 직접 기여한 것 외에도, Theurgy는 여러 오픈 소스 "
        "라이브러리와 도구 및 다른 오픈 소스 모드의 코드를 사용합니다.\n\\\n\\\n"
        "누구나 [GitHub에서 Theurgy 소스 코드를 확인할 수 있습니다]"
        "(https://github.com/klikli-dev/theurgy). 자유롭게 기여하거나 프로젝트에 도움이 "
        "될 부분을 살펴보세요.\n"
    ),
    "book.theurgy.the_hermetica.getting_started.purified_gold.purifying.text": (
        "정제는 다소 의외로 소화 공정으로 진행하지만, 다행히 촉매인 "
        "[](item://theurgy:purified_gold)은 필요하지 않습니다.\n\\\n\\\n"
        "대신 [아무 연금술 소금](item://theurgy:alchemical_salt_mineral)이나 사용할 수 "
        "있습니다. 소금이 금의 불순물과 결합해 이를 끌어냅니다.\n"
    ),
}

REPLACEMENTS = (
    ("신성 마법", "Theurgy"),
    ("신비술", "Theurgy"),
    ("연금술 나이터", "연금술 초석"),
    ("연금술 니터", "연금술 초석"),
    ("Alchemical Niter", "연금술 초석"),
    ("Alchemical Niters", "연금술 초석"),
    ("Alchemical Salt", "연금술 소금"),
    ("Alchemical Sulfur", "연금술 유황"),
    ("ALchemical Sulfur", "연금술 유황"),
    ("Alchemical Mercury", "연금술 수은"),
    ("Sal Ammoniac", "염화 암모늄"),
    ("Sal 암모니아", "염화 암모늄"),
    ("살 암모니아", "염화 암모늄"),
    ("샐 암모니아", "염화 암모늄"),
    ("염화암모늄", "염화 암모늄"),
    ("Mercury Flux", "수은 플럭스"),
    ("수성 플럭스", "수은 플럭스"),
    ("칼로리 플럭스", "열 플럭스"),
    ("Caloric Flux", "열 플럭스"),
    ("황산 플럭스", "유황 플럭스"),
    ("Sulfuric Flux", "유황 플럭스"),
    ("The Hermetica", "헤르메티카"),
    ("Spagyrics", "스파기리아"),
    ("Reformation Array", "재구성 배열"),
    ("Mercurial Logistics Network", "수은 물류망"),
    ("Mercurial Logistics System", "수은 물류망"),
    ("Mercurial Logistics", "수은 물류"),
    ("Mercurial Wand", "머큐리얼 지팡이"),
    ("Mercurial Wires", "수은 전선"),
    ("Exaltation", "승급"),
    ("Transmutation", "변환"),
    ("Reformation", "재구성"),
    ("Apparatus", "장치"),
    ("Accumulator", "농축기"),
    ("Distiller", "증류기"),
    ("Incubator", "배양기"),
    ("Emitter", "방출기"),
    ("Pedestal", "받침대"),
    ("Mineral Salt", "광물 소금"),
    ("Purified Gold", "정제된 금"),
    ("Common Metals", "일반 금속"),
    ("Common Gems", "일반 보석"),
    ("Rare Metals", "희귀 금속"),
    ("Sagyrics", "스파기리아"),
    ("Mercury Shards", "수은 조각"),
    ("Pyromantic Braziers", "화염 화로"),
    ("Fermentation", "발효"),
    ("Mercurial", "수은"),
    ("Target", "대상"),
    ("Entry", "항목"),
    ("Flux", "플럭스"),
    ("Niter", "초석"),
    ("Sulfur", "유황"),
    ("Quartz", "석영"),
    ("Lapis", "청금석"),
    ("Raw Iron", "철 원석"),
    ("Iron Ingots", "철 주괴"),
    ("Iron", "철"),
    ("Gold", "금"),
    ("Theurgy's", "Theurgy의"),
    ("Alchemical Sulpurs", "연금술 유황"),
    ("Alchemical", "연금술"),
    ("Mercury", "수은"),
    ("Salts", "소금"),
    ("Salt", "소금"),
    ("Water", "물"),
    ("Crystals", "수정"),
    ("Shards", "조각"),
    ("Strata", "지층"),
    ("Common Materials", "일반 재료"),
    ("Abundant", "풍부"),
    ("Vanilla", "바닐라"),
    ("Netherite", "네더라이트"),
    ("Overworld", "오버월드"),
    ("Wires", "전선"),
    ("Modded", "모드 환경"),
    ("Unobtainium", "언옵테이니움"),
    ("Rare", "희귀"),
    ("Result", "결과"),
    ("[iron]", "[철]"),
    ("[gold]", "[금]"),
    ("[coal]", "[석탄]"),
    ("[lapis]", "[청금석]"),
    ("[diamond]", "[다이아몬드]"),
    ("[diamonds]", "[다이아몬드]"),
    ("Sneak-Right-Click", "Shift+우클릭"),
    ("Shift-right-Click", "Shift+우클릭"),
    ("Right-Click", "우클릭"),
    ("Crouch-Click", "Shift+클릭"),
    ("shift-우클릭", "Shift+우클릭"),
    ("Shift-", "Shift+"),
    ("Warning", "경고"),
    ("Success", "성공"),
    ("Vats", "통"),
    ("Vat", "통"),
    ("연금술 장치들", "연금술 장치"),
    ("품목", "아이템"),
    ("항목", "아이템"),
    ("오른쪽 클릭", "우클릭"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("Shift 키를 누른 채 우클릭", "Shift+우클릭"),
    ("Shift-우클릭", "Shift+우클릭"),
    ("용법", "사용법"),
    ("부란기", "배양기"),
    ("인큐베이터", "배양기"),
    ("수성", "수은"),
    ("개혁", "재구성"),
    ("개량", "재구성"),
    ("승영", "승급"),
    ("초석를", "초석을"),
    ("유황를", "유황을"),
    ("로드", "점봉"),
    (")]", ")"),
)


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value for text in strings(item)]
    return []


def translated_text(value: str, cache: dict[str, str]) -> str:
    """원문의 실제 줄바꿈 위치를 보존하며 줄 단위 후보를 조립한다."""
    output = []
    for segment in value.splitlines(keepends=True):
        body = segment.removesuffix("\n")
        ending = "\n" if segment.endswith("\n") else ""
        output.append(EXACT_SOURCE.get(body, cache.get(body, body)) + ending)
    return "".join(output)


def transform(value: object, cache: dict[str, str]) -> object:
    if isinstance(value, list):
        return [transform(item, cache) for item in value]
    if not isinstance(value, str):
        return value
    translated = EXACT_SOURCE.get(value, translated_text(value, cache))
    for old, new in REPLACEMENTS:
        translated = translated.replace(old, new)
    return translated


def request_candidate(source: str) -> str:
    """문장 구조는 유지하고 링크 대상·자리표시자·서식 코드만 보호해 번역한다."""
    protected = []

    def mask(match: re.Match[str]) -> str:
        index = len(protected)
        protected.append(match.group(0))
        return f"ZXQPROTECTED{index}QXZ"

    masked = TRANSLATION_TOKEN.sub(mask, source)
    query = urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": "ko", "dt": "t", "q": masked}
    )
    request = urllib.request.Request(
        f"{ars_family.GOOGLE_TRANSLATE}?{query}",
        headers={"User-Agent": "ATM10-Korean-translation-candidate/1.0"},
    )
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            translated = "".join(row[0] for row in payload[0] if row and row[0])
            for index, value in enumerate(protected):
                token = f"ZXQPROTECTED{index}QXZ"
                if translated.count(token) != 1:
                    raise ValueError(f"보호 토큰이 바뀌었습니다: {token}")
                translated = translated.replace(token, value)
            return translated
        except Exception as exc:  # pragma: no cover - 외부 서비스 오류 보고용
            last_error = exc
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"자동 번역 후보 요청 실패: {source}") from last_error


def candidates() -> dict[str, object]:
    roots = (LANG_ROOT, QUEST_ROOT)
    if CACHE_PATH.is_file():
        cache = load_json(CACHE_PATH)
    elif PREVIOUS_CACHE_PATH.is_file():
        cache = load_json(PREVIOUS_CACHE_PATH)
    else:
        cache = {}
    sources = {
        text
        for root in roots
        for value in load_json(root / "en_us.json").values()
        for text in strings(value)
        if text and LATIN_WORD.search(text)
    }
    segments = {
        segment.removesuffix("\n")
        for source in sources
        for segment in source.splitlines(keepends=True)
        if segment.removesuffix("\n") and LATIN_WORD.search(segment)
    }
    requests = sorted(segments - cache.keys())
    failures = []
    if requests:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(request_candidate, source): source
                for source in requests
            }
            for number, future in enumerate(as_completed(futures), 1):
                source = futures[future]
                try:
                    cache[source] = future.result()
                except Exception as exc:  # pragma: no cover - 외부 서비스 오류 보고용
                    cache[source] = source
                    failures.append(f"{source}: {exc}")
                if number % 25 == 0:
                    write_json(CACHE_PATH, cache)
        write_json(CACHE_PATH, cache)
    for root in roots:
        english = load_json(root / "en_us.json")
        auto = {key: transform(value, cache) for key, value in english.items()}
        write_json(root / "auto_candidates_direct.json", auto)
    report = {
        "unique_strings": len(sources),
        "candidate_requests": len(requests),
        "candidate_failures": failures,
        "status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "direct_candidate_report.json", report)
    return report


def normalize_root(root: Path) -> int:
    english = load_json(root / "en_us.json")
    auto = load_json(root / "auto_candidates_direct.json")
    reviewed = {}
    for key, source in english.items():
        value = EXACT_KEYS.get(key, auto[key])
        if key.startswith("chapter.") and source == "Theurgy":
            value = "Theurgy"
        reviewed[key] = value
    write_json(root / "ko_kr.json", reviewed)
    return len(reviewed)


def normalize() -> dict[str, object]:
    report = {
        "language_keys": normalize_root(LANG_ROOT),
        "quest_keys": normalize_root(QUEST_ROOT),
        "status": "complete",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def pairs(source: object, target: object, path: str) -> list[tuple[str, str, str]]:
    if isinstance(source, str) and isinstance(target, str):
        return [(path, source, target)]
    if (
        isinstance(source, list)
        and isinstance(target, list)
        and len(source) == len(target)
    ):
        return [
            row
            for index, (left, right) in enumerate(zip(source, target, strict=True))
            for row in pairs(left, right, f"{path}[{index}]")
        ]
    return []


def verify_root(root: Path) -> tuple[dict[str, object], list[str]]:
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    errors = []
    untranslated = []
    if list(english) != list(korean):
        errors.append("키 또는 키 순서가 영어 원문과 다릅니다")
    for key in english.keys() & korean.keys():
        for path, source, target in pairs(english[key], korean[key], key):
            for label, pattern in (
                ("자리표시자", PLACEHOLDER),
                ("서식 코드", FORMAT_CODE),
                ("숫자", NUMBER),
            ):
                if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
                    errors.append(f"{label} 불일치: {path}")
            if Counter(LINK_TARGET.findall(source)) != Counter(
                LINK_TARGET.findall(target)
            ):
                errors.append(f"링크 대상 불일치: {path}")
            if len(MARKDOWN_LINK.findall(source)) != len(MARKDOWN_LINK.findall(target)):
                errors.append(f"링크 구문 불일치: {path}")
            if source.count("\n") != target.count("\n"):
                errors.append(f"줄바꿈 불일치: {path}")
            if (
                source == target
                and LATIN_WORD.search(source)
                and source not in {"Theurgy", "§6[§7more§6]", "%smB"}
            ):
                untranslated.append(path)
    report = {
        "keys": len(english),
        "untranslated_candidates": untranslated,
        "errors": errors,
        "status": "complete" if not errors and not untranslated else "incomplete",
    }
    if untranslated:
        errors.append(f"미번역 후보: {untranslated[:30]}")
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    reports = []
    errors = []
    for label, root in (("language", LANG_ROOT), ("quests", QUEST_ROOT)):
        report, current = verify_root(root)
        report["scope"] = label
        reports.append(report)
        errors.extend(current)
    result = {
        "scopes": reports,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", result)
    return result, errors


def audit() -> tuple[dict[str, object], list[str]]:
    instance = resolve_source_root()
    jar = next((instance / "mods").glob("theurgy-*.jar"))
    with ZipFile(jar) as archive:
        names = archive.namelist()
        book_files = [
            name
            for name in names
            if "/modonomicon/books/" in name and name.endswith(".json")
        ]
        references = []
        literals = []
        for name in book_files:
            value = json.loads(archive.read(name))

            def walk(item: object, path: str = "") -> None:
                if isinstance(item, dict):
                    for key, child in item.items():
                        current = f"{path}/{key}"
                        if key in {
                            "name",
                            "description",
                            "title",
                            "text",
                        } and isinstance(child, str):
                            if re.fullmatch(r"[a-z0-9_.-]+", child):
                                references.append((name, current, child))
                            elif child:
                                literals.append((name, current, child))
                        walk(child, current)
                elif isinstance(item, list):
                    for index, child in enumerate(item):
                        walk(child, f"{path}/{index}")

            walk(value)
    errors = []
    language = load_json(LANG_ROOT / "en_us.json")
    missing_references = sorted({row[2] for row in references} - language.keys())
    if missing_references:
        errors.append(f"설명서 참조 키 누락: {missing_references[:20]}")
    if literals:
        errors.append(f"설명서 직접 영문 표시값: {literals[:10]}")
    report = {
        "jar": jar.name,
        "modonomicon_files": len(book_files),
        "translated_display_references": len(references),
        "literal_display_values": len(literals),
        "missing_language_references": missing_references,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("candidates", "normalize", "verify", "audit")
    )
    args = parser.parse_args()
    if args.command == "candidates":
        report, errors = candidates(), []
    elif args.command == "normalize":
        report, errors = normalize(), []
    elif args.command == "verify":
        report, errors = verify()
    else:
        report, errors = audit()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
