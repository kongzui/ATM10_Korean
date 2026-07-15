#!/usr/bin/env python3
"""다섯 모드군의 설치 범위와 언어 작업본을 준비하고 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

import audit_ftbquests_titles as quest_audit
import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LEGACY_PACK = "resourcepacks/all-the-mods-10_5.4_resourcepack.zip"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
TRANSLATION_KEY = re.compile(r"^[a-z0-9_.-]+(?:\.[a-z0-9_.-]+)+$")


@dataclass(frozen=True)
class Target:
    family: str
    jar_prefix: str
    namespace: str
    label: str
    direct_integration: bool = False


TARGETS = (
    Target("mekanism", "Mekanism-", "mekanism", "Mekanism"),
    Target(
        "mekanism",
        "MekanismGenerators-",
        "mekanismgenerators",
        "Mekanism Generators",
    ),
    Target("mekanism", "MekanismTools-", "mekanismtools", "Mekanism Tools"),
    Target("mekanism", "mekanismcovers-", "mekanismcovers", "Mekanism Covers"),
    Target(
        "mekanism",
        "mekanisticrouters-",
        "mekanisticrouters",
        "Mekanistic Routers",
    ),
    Target(
        "mekanism",
        "JustEnoughMekanismMultiblocks-",
        "jei_mekanism_multiblocks",
        "Just Enough Mekanism Multiblocks",
    ),
    Target("mekanism", "mekmm-", "mekmm", "MEKMM"),
    Target(
        "mekanism",
        "GravitationalModulatingAdditionalUnit-",
        "gmut",
        "Gravitational Modulating Additional Unit",
        True,
    ),
    Target(
        "mekanism",
        "Applied-Mekanistics-",
        "appmek",
        "Applied Mekanistics",
        True,
    ),
    Target(
        "mekanism",
        "refinedstorage-mekanism-integration-",
        "refinedstorage_mekanism_integration",
        "Refined Storage - Mekanism Integration",
        True,
    ),
    Target("powah_flux", "Powah-", "powah", "Powah!"),
    Target("powah_flux", "Powah-", "lollipop", "Lollipop"),
    Target("powah_flux", "FluxNetworks-", "fluxnetworks", "Flux Networks"),
    Target("ars_nouveau", "ars_nouveau-", "ars_nouveau", "Ars Nouveau"),
    Target("ars_nouveau", "ars_additions-", "ars_additions", "Ars Additions"),
    Target("ars_nouveau", "ars_controle-", "ars_controle", "Ars Controle"),
    Target("ars_nouveau", "ars_creo-", "ars_creo", "Ars Creo"),
    Target("ars_nouveau", "ars_elemancy-", "ars_elemancy", "Ars Elemancy"),
    Target("ars_nouveau", "ars_elemental-", "ars_elemental", "Ars Elemental"),
    Target("ars_nouveau", "ars_ocultas-", "ars_ocultas", "Ars Ocultas"),
    Target("ars_nouveau", "ars_technica-", "ars_technica", "Ars Technica"),
    Target("ars_nouveau", "ars_unification-", "ars_unification", "Ars Unification"),
    Target(
        "ars_nouveau",
        "not_enough_glyphs-",
        "not_enough_glyphs",
        "Not Enough Glyphs",
    ),
    Target(
        "ars_nouveau",
        "starbunclemania-",
        "starbunclemania",
        "Starbuncle Mania",
    ),
    Target("ars_nouveau", "arseng-", "arseng", "Ars Énergistique", True),
    Target(
        "ars_nouveau",
        "allthearcanistgear-",
        "allthearcanistgear",
        "All the Arcanist Gear",
        True,
    ),
    Target("evilcraft", "evilcraft-", "evilcraft", "EvilCraft"),
    Target("evilcraft", "evilcraft-", "evilcraftcompat", "EvilCraft Compat"),
    Target(
        "twilight_forest",
        "twilightforest-",
        "twilightforest",
        "The Twilight Forest",
    ),
)

FAMILY_LABELS = {
    "mekanism": "Mekanism",
    "powah_flux": "Powah!·Flux Networks",
    "ars_nouveau": "Ars Nouveau",
    "evilcraft": "EvilCraft",
    "twilight_forest": "The Twilight Forest",
}

QUEST_CHAPTERS = {
    "mekanism": ("mekanism", "mekanism_reactors"),
    "powah_flux": ("powah",),
    "ars_nouveau": ("ars_nouveau",),
    "evilcraft": ("evilcraft",),
    "twilight_forest": ("twilight_forest",),
}

QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
QUEST_CHAPTER_OUTPUT = (
    PROJECT_ROOT / "output/overrides/config/ftbquests/quests/chapters"
)

EXTRA_SCOPE = {
    "ars_nouveau": (
        {
            "label": "Ars Polymorphia",
            "jar_prefix": "ars_polymorphia-",
            "expected": True,
        },
    ),
}

ALLOWED_ORIGINALS = {
    "Mekanism",
    "Mekanism: Generators",
    "Mekanism: Tools",
    "Powah",
    "Powah!",
    "Flux Networks",
    "Ars Nouveau",
    "Ars Additions",
    "Ars Controle",
    "Ars Creo",
    "Ars Elemancy",
    "Ars Elemental",
    "Ars Ocultas",
    "Ars Technica",
    "Ars Unification",
    "Not Enough Glyphs",
    "Starbuncle Mania",
    "StarbuncleMania",
    "Ars Énergistique",
    "EvilCraft",
    "The Twilight Forest",
    "Baubles",
    "Blood Magic",
    "Equivalent Exchange 3",
    "Forestry",
    "Ender IO",
    "Industrial Craft 2",
    "Just Enough Items",
    "Immersive Engineering",
    "Thermal Expansion",
    "Thaumcraft",
    "Tinkers' Construct",
    "Jade",
    "MrCompost - Findings",
    "MrCompost - Home",
    "MrCompost - Maker",
    "MrCompost - Motion",
    "Rotch Gwylt - Radiance",
    "Rotch Gwylt - Steps",
    "Rotch Gwylt - Superstitious",
    "MrCompost - Thread",
    "MrCompost - Wayfarer",
    "HexaBlu",
    "Thistle - The Sound of Glass",
    "AllRightsReserved",
    "Ctrl+C, Ctrl+V",
    "LostMyself",
    "TedXenon",
    "Applied Mekanistics",
    "Mekanism CC2C",
    "Mekanism C2C",
    "Mekanism IC2I",
    "Mekanism I2C",
    "Mekanism PRC",
    "SPS",
    "Gravitational Modulating Additional Unit",
    "Mekanism - Gravitational Modulating Additional Unit",
}

ALLOWED_NAME_COLLISIONS = {
    frozenset({"Energised Steel", "Energized Steel"}),
    frozenset({"Amethyst Golem", "The Amethyst Golem"}),
    frozenset({"Drygmy", "The Drygmy"}),
    frozenset({"Starbuncle", "The Starbuncle"}),
    frozenset({"Whirlisprig", "The Whirlisprig"}),
    frozenset({"Wixie", "The Wixie"}),
    frozenset({"Liveroot", "Liveroots"}),
    frozenset({"Naga Scale", "Naga Scales"}),
    frozenset({"Has: %s %s Candle", "Has: %s %s Candles"}),
}

MEKANISM_QUEST_WORDS = {
    "Ultimate": "궁극",
    "Tier": "단계",
    "Steam": "증기",
    "Reactors": "반응기",
    "Reactor": "반응기",
    "Modpack": "모드팩",
    "Modded": "모드가 추가된",
    "Mod": "모드",
    "Slurry": "슬러리",
    "Ore": "광석",
    "Metallurgic": "금속공학",
    "Infuser": "주입기",
    "Atomic": "원자",
    "Fusion": "핵융합",
    "Redstone": "레드스톤",
    "Basic": "기본",
    "Quantum": "양자",
    "Creative": "크리에이티브",
    "Bins": "단일 아이템 창고",
    "Bin": "단일 아이템 창고",
    "Configurator": "설정 장치",
    "Portal": "포털",
    "Itemstack": "아이템 스택",
    "Item": "아이템",
    "Robit": "로빗",
    "Multiblock": "멀티블록",
    "Mutliblock": "멀티블록",
    "Dissambler": "분해기",
    "Paxel": "팍셀",
    "Induction": "유도",
    "Cell": "셀",
    "Hohlraum": "홀로륨",
    "Casing": "케이싱",
    "Heat": "열",
    "Shears": "가위",
    "Drive": "드라이브",
    "Type": "유형",
    "Bodyarmor": "흉갑",
    "Teleport": "순간이동",
    "Home": "귀환",
    "Chargepad": "충전 패드",
    "Rename": "이름 변경",
    "Mob": "몹",
    "Appearance": "외형",
    "Crafting": "제작",
    "Windows": "창",
    "Craft": "제작",
    "Pants": "바지",
    "Neutral": "중립",
    "Glowing": "발광",
    "Sword": "검",
    "Unit": "유닛",
    "Side": "측면",
    "Configs": "설정",
    "Machine": "기계",
    "Empty": "빈",
    "Bar": "막대",
    "Set": "설정",
    "Network": "네트워크",
    "Name": "이름",
    "Entangloporters": "양자 전송기",
    "Entangloporter": "양자 전송기",
    "Glass": "유리",
    "Part": "부품",
    "DUMP": "버리기",
    "Bedrock": "기반암",
    "X-Ray": "투시",
    "ETC": "기타",
    "Paxels": "팍셀",
    "Armor": "방어구",
    "Offhand": "보조 손",
    "Walls": "벽",
    "Idle": "대기",
    "Damage": "피해",
    "Chemical": "화학 물질",
    "Netherite": "네더라이트",
    "Types": "유형",
    "Tag": "태그",
    "Activate": "가동",
    "Time-Dilating": "시간 확장",
    "Flight": "비행",
    "Wind": "풍력",
}

MEKANISM_QUEST_TEXT_REPLACEMENTS = {
    "quest.1796E08BBDC09B84.quest_desc": (
        ("1톤", "아주 많은 양"),
        (
            "밀거나 당기는 것에 따라 걸리거나 장소가 결정됩니다.",
            "유체나 화학 물질의 입출력 방향은 연결된 파이프가 밀어 넣는지 "
            "끌어내는지에 따라 결정됩니다.",
        ),
    ),
    "quest.0306D25C7407FE88.quest_desc": (("1년", "오랫동안"),),
    "quest.4869D9DBDD1A15CD.quest_desc": (("16진수", "헥스"),),
    "quest.7B500E0577BDFF8F.quest_desc": (("12가지", "열두 가지"),),
    "task.09788D3638E59F3B.title": (("계층 설치 프로그램", "등급 설치기"),),
    "task.11EF7663818B6CC6.title": (("쓰레기통", "단일 아이템 창고"),),
    "task.36B9FB74D9BF26E4.title": (("열역학적 도체", "열역학 전도체"),),
    "task.4558919345C3BE5D.title": (("강화제", "농축기"),),
    "task.4632192573FD8501.title": (("기계 파이프", "기계식 파이프"),),
    "task.4B60ACBCC3B46D1D.title": (("강화된 아이템", "농축 물질"),),
    "task.4B6C5B2099B18AB7.title": (("제련소", "제련기"),),
    "task.564D0E533237E951.title": (("정수기", "정화기"),),
    "task.729C1974AE346ECA.title": (("정수기", "정화기"),),
    "task.151AF2F49AAEBBDA.title": (("유도세포", "유도 셀"),),
    "task.496C4FDD2515EB24.title": (("유도 공급자", "유도 공급기"),),
    "quest.477B411F84342EEA.quest_desc": (
        ("mekanism은", "Mekanism은"),
        ("[best] 적합한", "가장 적합한"),
        ("[기본 Energy Cube]", "기본 에너지 큐브"),
        ("[Configure]하기", "설정하기"),
        ("[craft]하기", "제작하기"),
        ("[Power]", "에너지"),
        ("[upgrading]", "업그레이드"),
        ("[interface]", "GUI"),
        ("[아이템]", "아이템"),
        ("[Charge]", "충전"),
        ("[Energy Cube]", "에너지 큐브"),
        ("[chapter]", "챕터"),
    ),
    "quest.493D04D954E4FBA0.quest_desc": (("기술 모드od...인데", "기술 모드인데"),),
    "quest.6718043D0F2D1830.quest_desc": (
        (
            "DireWolf는 그의 카드 &5&lMekanism&r 및 its... 다른 물질 상태와 함께 "
            "작동하도록 요청받았습니다.",
            "DireWolf는 자신의 카드를 &5&lMekanism&r의 여러 물질 상태와 함께 "
            "사용할 수 있게 해 달라는 요청을 받았습니다.",
        ),
        (
            "모든 가압 튜브가 움직일 수 있는 것은 이 카드도 할 수 있습니다.",
            "이 카드는 가압 튜브가 운반하는 모든 물질을 옮길 수 있습니다.",
        ),
        ("가스, 주입 유형 및 안료.", "화학 물질, 주입 유형, 안료가 대상입니다."),
    ),
    "quest.3E32450DBB7529AA.quest_desc": (
        ("&eBatcher&r", "&e아이템 배처&r"),
        ("필터와 금액", "필터와 수량"),
    ),
    "quest.4A1C8125896F7F1A.quest_desc": (
        ("AllTheMods Staff", "AllTheMods 운영진"),
        ("All Rights Reserved", "모든 권리 보유"),
        ("AllTheMods Team", "AllTheMods 팀"),
        ("AllTheMods Modpack", "AllTheMods 모드팩"),
    ),
    "quest.4F7F0A5162D70082.quest_desc": (("만들어야 though...하며", "만들어야 하며"),),
    "quest.49F08DE190AAD0D8.quest_desc": (("mekanism의", "Mekanism의"),),
    "quest.14385D3D359224BC.quest_desc": (("Craft에", "제작할 때"),),
    "quest.16DDAE318535D0F9.quest_desc": (("스위핑 엣지(Sweeping Edge)", "휩쓸기"),),
    "quest.1FC88A3BFCE6C9D7.quest_desc": (
        ("Swift Sneaking Enchantment", "신속한 잠행 마법"),
    ),
    "quest.359934E888495E5E.quest_desc": (
        ("Dirty 광석 슬러리", "오염된 광석 슬러리"),
        ("Clean 광석 슬러리", "정제된 광석 슬러리"),
    ),
    "quest.3B936CA3F0F7B26B.quest_desc": (
        ("보이드 마이너(Void Miners)", "공허 채굴기"),
    ),
    "quest.459AEC4C2A611824.quest_desc": (("Night Vision", "야간 투시"),),
    "quest.5B9F3F32AB28A83A.title": (("Thermo 부분", "열 전달부"),),
    "quest.6D7D0A5313284B53.quest_desc": (("Fall 피해", "낙하 피해"),),
    "quest.795B80BF12D23897.quest_desc": (
        ("프로스트 워커", "차가운 걸음"),
        ("Frost Walker", "차가운 걸음"),
    ),
    "quest.795B80BF12D23897.title": (("프로스트 워커", "차가운 걸음"),),
    "quest.69B5D716568AA9EB.quest_desc": (
        ("Mekanism Cables", "Mekanism 케이블"),
        ("ATM Stars", "ATM Star"),
    ),
    "quest.65A529C8238E89F1.quest_desc": (("좀 별로네요 though...", "좀 별로네요..."),),
    "quest.2DE7CC686B56881F.quest_desc": (("mekanism", "Mekanism"),),
}

MEKANISM_CUSTOM_NAMES = {
    "Crushers": ("분쇄기", 3),
    "Enrichers": ("농축기", 3),
    "Smelters": ("제련기", 3),
    "Purifiers": ("정화기", 1),
    "Purificaters": ("정화기", 1),
}

MEKANISM_QUEST_ITEM_TITLES = {
    "quest.162CE44400A63575.title": "금속공학 주입기",
    "quest.08DDE018A804BFE7.title": "농축기",
    "quest.7AE502EDB73BD57A.title": "분쇄기",
    "quest.166971866A9234C7.title": "주입 합금",
    "quest.488DBE69595F38F8.title": "전동 제련기",
    "quest.001DE8028CAF0A08.title": "방음 업그레이드",
    "quest.09830BB2A23E94B4.title": "화학 물질 업그레이드",
    "quest.515A60B89ED5440D.title": "돌 생성 업그레이드",
    "quest.74200A48498DD7F8.title": "태양광 발전기",
    "quest.0650996C7818ADB5.title": "열 발전기",
    "quest.6CD1720B76F47806.title": "바이오연료 발전기",
    "quest.4EDD96EB60EF5814.title": "고급 태양광 발전기",
    "quest.7778937DF377C1B4.title": "풍력 발전기",
    "quest.7ECA0633AF1AEC19.title": "정밀 제재기",
    "quest.33415CB421F7620A.title": "정화기",
    "quest.27512B0434531195.title": "화학 주입실",
    "quest.566C1DBA9829E328.title": "결합기",
    "quest.60B52705049D1BA5.title": "화학적 세척 장치",
    "quest.6B8040401B512E50.title": "화학적 용해 장치",
    "quest.602A6CF9D5B66AD3.title": "화학적 결정화 장치",
    "quest.18783C62009934DB.title": "전해 분리기",
    "quest.2A793B35FE25003C.title": "화학적 산화 장치",
    "quest.376532CD98D39781.title": "화학적 반응 장치",
    "quest.71869B1D81D6A7EF.title": "가압 반응 장치",
    "quest.603BEDD49070ECAD.title": "회전 콘덴서",
    "quest.2D1CBCEC82F1B37D.title": "장작 가열기",
    "quest.21F3379C904BFD50.title": "전기 저항 가열기",
    "quest.4274E777FB60BA28.title": "충전 패드",
    "quest.041365A540BF5A03.title": "광석 사전",
    "quest.424B3E3B299D3999.title": "스포이트",
    "quest.109310AF19AAC482.title": "화염 방사기",
    "quest.4E7823C2FCEBE4DC.title": "전동 활",
    "quest.3D2B4D9FD2086B9B.title": "핵분열로 로직 어댑터",
    "quest.5A088F8402230BA5.title": "핵분열로 포트",
    "quest.6A1174845810C7A1.title": "모듈 제어기",
    "quest.7864C8F2CBC910CB.title": "메카슈트 투구",
    "quest.6C1F7A0B330B3F42.title": "메카슈트 흉갑",
    "quest.56DB53F255100136.title": "메카슈트 각반",
    "quest.6D7D0A5313284B53.title": "메카슈트 부츠",
    "quest.0306D25C7407FE88.title": "레이저 초점 매트릭스",
}

MEKANISM_QUEST_ELEMENT_OVERRIDES = {
    "quest.0095422BC87AA135.quest_desc": {
        0: (
            "다시요? 필요한 건 &7주괴&f이지, &7덩어리&f나 &7조각&r이 아니에요! "
            "&7주괴&r 말입니다! \\n\\n"
            "&7광석 조각&r을 &b산소&r와 함께 &b&l정화기&r에 넣으면 "
            "&7광석 덩어리&r가 됩니다. 산소는 앞서 만든 &9&l전해 분리기&r에서 "
            "가져오면 됩니다. \\n\\n"
            "이제 이전 단계와 같은 과정을 반복하세요. &7덩어리&f를 &4분쇄&f해 "
            "&7오염된 가루&r를 얻습니다. \\n\\n"
            "&7오염된 가루&r를 &d농축&f해 깨끗하게 만드세요. \\n\\n"
            "마지막으로 &7가루&f를 &6제련&f하면 &7주괴&r가 완성됩니다!"
        ),
    },
    "quest.18783C62009934DB.quest_desc": {
        0: (
            "&9&l전해 분리기&r는 1종의 &b유체&r를 2종의 &c화학 물질&r로 "
            "분리합니다! \\n\\n"
            "&b유체&r는 &4빨간색 막대&r로 들어가고, 생성된 &c화학 물질&r은 "
            "&9파란색&f과 &3청록색 막대&r에 표시됩니다. \\n\\n"
            "GUI 아래쪽의 버튼으로 두 출력 막대의 동작을 각각 바꿀 수 있습니다. "
            "\\n\\n대기는 저장 한도에 도달하면 생산을 멈춥니다. 예를 들어 수소가 가득 "
            "차면 더 이상 &9물&r을 소비하지 않습니다. \\n\\n"
            "초과분 버리기는 막대가 가득 차도 넘치는 양만 버려 각 &c화학 물질&r "
            "생산을 계속합니다. "
            "수소보다 &b산소&r가 많이 필요할 때 유용합니다. \\n\\n"
            "모두 버리기는 생성되는 &c화학 물질&r을 전부 삭제합니다."
        ),
    },
    "quest.03840E4C74731E0C.quest_desc": {
        0: (
            "지금까지 대부분의 &5&lMekanism&r 퀘스트에서 &9전기 펌프&r를 "
            "사용하라고 했습니다. \\n\\n하지만 이제 졸업할 때예요. &2&l반응기&r에는 "
            "훨씬 많은 &9물&r이 필요하니 &9싱크대&r를 사용하세요! \\n\\n"
            "&9싱크대&r는 &9물&r을 무한히 공급하며 거의 모든 모드의 파이프로 "
            "&b추출&r할 수 있습니다. 사용할 수 있다면 틱마다 &9물&r을 2빌리언 mB "
            "넘게 끌어오는 &9&lID&r를 권장합니다! \\n\\n"
            "앞에서 &9전기 펌프&r를 사용한 이유는 여러분에게 &9싱크대&r를 맡길 "
            "수 없어서가 아니라 두 가지입니다. 1. &9싱크대&r가 "
            "없는 모드팩에서도 설명이 유효하고, 2. 전기 펌프가 &5&lMekanism&r의 "
            "기계이기 때문입니다. "
        ),
    },
    "quest.438F734D16DA9638.quest_desc": {
        0: (
            "&a폴로늄&r을 얻었으니 나머지 재료는 이미 갖추었을 거예요! \\n\\n"
            "&2&lP.R.C.&r, &9물&r, &d형석 가루&r가 필요합니다. \\n\\n"
            "1,000mB의 &9물&r, 1,000mB의 &a폴로늄&r, 1개의 &d형석 가루&r를 "
            "조합하면 1개의 &a폴로늄 펠릿&r과 1,000mB의 &8사용후핵폐기물&r을 "
            "얻습니다. \\n\\n"
            "&d형석 가루&r는 다른 금속 가루처럼 &4&l분쇄기&r, "
            "&d&l농축기&r 또는 광석 망치로 만들 수 있습니다!"
        ),
    },
    "quest.7B0DFA55B4D8B16D.quest_desc": {
        0: (
            "&a&l텔레포터&r는 &5기계&r를 완성하고 &a전원을 공급&r하면 어느 "
            "차원이든 원하는 곳으로 순간이동할 수 있게 해 줍니다! \\n\\n"
            "그럼 어떻게 만들고 전원을 공급하는지 알아봅시다. \\n\\n"
            "&a&l텔레포터&r 하나에는 1개의 &a텔레포터 블록&f과 9개의 "
            "&a텔레포터 프레임&r이 필요합니다. \\n\\n"
            "&a텔레포터 블록&r은 &a&l텔레포터&r의 주 &a제어기&r이며 "
            "&a에너지&r를 받는 블록입니다. &a전원이 공급&r되면 GUI를 열어 "
            "&5양자 전송기&r처럼 네트워크 이름을 입력하고 체크 표시를 눌러 "
            "네트워크를 만들 수 있습니다. \\n\\n"
            "다른 &a&l텔레포터 구조물&r이나 &a텔레포터 블록&r도 GUI에서 같은 "
            "네트워크를 선택하면, &a&l텔레포터&r를 통해 같은 네트워크의 다른 "
            "&a&l텔레포터&r로 이동할 수 있습니다. \\n\\n"
            "&a&l텔레포터 구조물&r을 만들려면 &a텔레포터 블록&r 양옆에 "
            "&a텔레포터 프레임&r을 하나씩 놓고, 그 위로 3개씩 더 쌓아 전체 높이를 "
            "4블록으로 만드세요. &a텔레포터 블록&r 위에 2블록 높이의 빈 공간을 "
            "남기고 마지막 &a텔레포터 프레임&r으로 위쪽을 연결합니다. \\n\\n"
            "전원을 공급하고 네트워크를 설정하면 &a&l텔레포터&r에 색깔 있는 "
            "포털이 나타납니다! \\n\\n포털 색상은 &a&l텔레포터&r GUI에서 바꿀 수 있습니다."
        ),
    },
}

TIER_KO = {
    "Basic": "기본",
    "Advanced": "고급",
    "Elite": "엘리트",
    "Ultimate": "궁극",
    "Overclocked": "오버클럭",
    "Quantum": "양자",
    "Dense": "고밀도",
    "Multiversal": "다중우주",
    "Creative": "크리에이티브",
}

MEKANISM_EXACT = {
    "Damage": "피해",
    "Efficiency": "효율",
    "Enchantability": "마법 부여 적합성",
    "Applied Mekanistics": "Applied Mekanistics",
    "Chemical": "화학 물질",
    "Large Antiprotonic Nucleosynthesizer": "대형 반양성자 핵합성기",
    "Large Pigment Mixer": "대형 안료 혼합기",
    "Large Wind Generator": "대형 풍력 발전기",
    "Pigment Extracting": "안료 추출",
    "Painting": "염색",
    "Max Chemical Tanks": "최대 화학 물질 탱크",
    "Edit Max Chemical Tanks": "최대 화학 물질 탱크 편집",
    "Settings for configuring Max Chemical Tanks": "최대 화학 물질 탱크 설정",
    "Mid Chemical Tanks": "중간 화학 물질 탱크",
    "Edit Mid Chemical Tanks": "중간 화학 물질 탱크 편집",
    "Settings for configuring Mid Chemical Tanks": "중간 화학 물질 탱크 설정",
    "Tier Config": "등급 설정",
    "Mekanism: MoreMachine - Tier Config": "Mekanism: MoreMachine - 등급 설정",
    "Mekanism Config": "Mekanism 설정",
    "Mekanism - Client Config": "Mekanism - 클라이언트 설정",
    "Mekanism - Common Config": "Mekanism - 공통 설정",
    "Mekanism - General Config": "Mekanism - 일반 설정",
    "Client Config": "클라이언트 설정",
    "Common Config": "공통 설정",
    "General Config": "일반 설정",
    "LostMyself": "LostMyself",
    "TedXenon": "TedXenon",
    "Supercharging Elements: %s": "초충전 소자: %s",
    "Processing Speed": "처리 속도",
}

MEKANISM_KEY_OVERRIDES = {
    "block.mekanism.chemical_injection_chamber": "화학 주입실",
    "block.mekanismgenerators.control_rod_assembly": "제어봉 집합체",
    "block.mekanismgenerators.fission_fuel_assembly": "핵분열 연료 집합체",
    "block.mekanismgenerators.fission_reactor_casing": "핵분열로 케이싱",
    "block.mekanismgenerators.fission_reactor_logic_adapter": "핵분열로 로직 어댑터",
    "block.mekanismgenerators.fission_reactor_port": "핵분열로 포트",
    "block.mekanismgenerators.advanced_solar_generator": "고급 태양광 발전기",
    "block.mekanismgenerators.heat_generator": "열 발전기",
    "gui.mekanism.digital_miner.max": "최대 Y 높이: %1$s",
    "gui.mekanism.digital_miner.min": "최소 Y 높이: %1$s",
    "miner.mekanism.radius": "블록 반경: %1$s",
    "multiblock.mekanism.invalid_inner": (
        "내부 구조의 %1$s 위치에 잘못된 블록(%2$s)이 있습니다."
    ),
    "mekanisticrouters.itemText.usage.item.chemical_module_mk1": (
        "모듈 방향에 있는 인접 블록과 라우터 사이에서 화학 물질을 전송합니다.\n"
        "• 라우터 버퍼에 화학 물질 용기 아이템이 있어야 합니다."
    ),
    "mekanisticrouters.itemText.usage.item.chemical_module_mk2": (
        "주변 블록과 라우터 사이에서 화학 물질을 전송합니다.\n"
        "• 라우터 버퍼에 화학 물질 용기 아이템이 있어야 합니다.\n"
        "• 탱크와도 주고받을 수 있습니다."
    ),
    "mekanisticrouters.guiText.popup.chemical_refill.control": (
        "§a§C화학 물질 재충전 모듈§r\n\n여기에서 다음 항목을 정할 수 있습니다: "
        "\n- 플레이어 인벤토리에서 상호작용할 구역\n\n필터는 이 모듈에서 "
        "화학 물질을 받을 수 있는 아이템을 제어합니다."
    ),
    "item.refinedstorage_mekanism_integration.chemical_storage_disk.help": (
        "%s버킷을 저장합니다. 비어 있을 때 손에 들고 사용하면 화학 물질 저장 부품을 "
        "돌려받습니다. 화학 물질 저장 부품과 조합해 더 높은 등급으로 업그레이드할 수 "
        "있습니다."
    ),
    "item.refinedstorage_mekanism_integration.creative_chemical_storage_disk.help": (
        "버킷을 무한히 저장합니다."
    ),
    "item.refinedstorage_mekanism_integration.chemical_storage_block.help": (
        "%s버킷을 저장합니다. 비어 있을 때 손에 들고 사용하면 화학 물질 저장 부품과 "
        "기계 케이싱을 돌려받습니다. 화학 물질 저장 부품과 조합해 더 높은 등급으로 "
        "업그레이드할 수 있습니다."
    ),
    "item.refinedstorage_mekanism_integration.creative_chemical_storage_block.help": (
        "버킷을 무한히 저장합니다."
    ),
    "advancements.refinedstorage_mekanism_integration.storing_chemicals": (
        "화학 물질 저장"
    ),
    "advancements.refinedstorage_mekanism_integration.storing_chemicals.description": (
        "화학 물질 저장 디스크를 제작해 디스크 드라이브에 넣으세요."
    ),
    "refinedstorage_mekanism_integration.configuration.title": (
        "Refined Storage - Mekanism Integration 설정"
    ),
    "refinedstorage_mekanism_integration.configuration.section.refinedstorage_mekanism_integration.common.toml": (
        "Refined Storage - Mekanism Integration 설정"
    ),
    "refinedstorage_mekanism_integration.configuration.section.refinedstorage_mekanism_integration.common.toml.title": (
        "Refined Storage - Mekanism Integration 설정"
    ),
    "config.refinedstorage_mekanism_integration.option.chemicalStorageBlock.tooltip": (
        "화학 물질 저장 블록 설정입니다."
    ),
}


def sha256(path: Path) -> str:
    """파일 SHA-256을 계산한다."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def duplicate_keys(raw: str) -> list[str]:
    """JSON 객체의 중복 키를 찾는다."""
    duplicates: list[str] = []

    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        counts = Counter(key for key, _ in pairs)
        duplicates.extend(key for key, count in counts.items() if count > 1)
        return dict(pairs)

    json.loads(raw, object_pairs_hook=hook)
    return sorted(set(duplicates))


def load_json_bytes(raw: bytes) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError("언어 JSON 최상위 값이 객체가 아닙니다.")
    return value


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 파일에서 읽는다."""
    return load_json_bytes(path.read_bytes())


def find_jar(instance: Path, prefix: str) -> Path:
    """접두사로 설치 JAR 하나를 확정한다."""
    matches = sorted(
        path
        for path in (instance / "mods").glob("*.jar")
        if path.name.lower().startswith(prefix.lower())
    )
    if len(matches) != 1:
        raise RuntimeError(f"JAR을 하나로 확정하지 못했습니다: {prefix}:{matches}")
    return matches[0]


def targets_for(family: str) -> tuple[Target, ...]:
    """모드군의 언어 대상을 반환한다."""
    return tuple(target for target in TARGETS if target.family == family)


def language_paths(namespace: str) -> tuple[str, str]:
    """영어와 한국어 언어 파일 경로를 반환한다."""
    return (
        f"assets/{namespace}/lang/en_us.json",
        f"assets/{namespace}/lang/ko_kr.json",
    )


def read_mod_metadata(archive: ZipFile) -> str:
    """모드 메타데이터 원문을 가능한 위치에서 읽는다."""
    candidates = (
        "META-INF/neoforge.mods.toml",
        "META-INF/mods.toml",
        "fabric.mod.json",
    )
    for name in candidates:
        if name in archive.namelist():
            return archive.read(name).decode("utf-8-sig", errors="replace")
    return ""


def asset_inventory(archive: ZipFile, namespace: str) -> dict[str, object]:
    """가이드·발전 과제·사용자 표시 JSON 후보를 센다."""
    names = archive.namelist()
    guide_tokens = ("patchouli", "guide", "book", "manual")
    guides = sorted(
        name
        for name in names
        if name.lower().endswith((".json", ".md"))
        and any(token in name.lower() for token in guide_tokens)
        and (f"/{namespace}/" in name or name.startswith(f"assets/{namespace}/"))
    )
    advancements = sorted(
        name
        for name in names
        if name.lower().endswith(".json")
        and ("/advancement/" in name or "/advancements/" in name)
        and f"data/{namespace}/" in name
    )
    recipes = sum(
        name.lower().endswith(".json")
        and ("/recipe/" in name or "/recipes/" in name)
        and f"data/{namespace}/" in name
        for name in names
    )
    return {
        "guide_candidates": len(guides),
        "guide_examples": guides[:20],
        "advancements": len(advancements),
        "advancement_examples": advancements[:20],
        "recipes": recipes,
    }


def dependency_scan(instance: Path, modids: set[str]) -> list[dict[str, object]]:
    """모든 설치 JAR 메타데이터에서 대상 모드 의존성을 찾는다."""
    rows: list[dict[str, object]] = []
    target_prefixes = {target.jar_prefix.lower() for target in TARGETS}
    for jar in sorted((instance / "mods").glob("*.jar")):
        if any(jar.name.lower().startswith(prefix) for prefix in target_prefixes):
            continue
        try:
            with ZipFile(jar) as archive:
                metadata = read_mod_metadata(archive)
        except Exception as exc:  # pragma: no cover - 실제 손상 JAR 보고용
            rows.append({"jar": jar.name, "error": str(exc)})
            continue
        lowered = metadata.lower()
        hits = sorted(modid for modid in modids if modid.lower() in lowered)
        if hits:
            rows.append({"jar": jar.name, "dependency_mentions": hits})
    return rows


def inventory(instance: Path, family: str) -> dict[str, object]:
    """실제 설치본의 버전·네임스페이스·부가 자산을 조사한다."""
    rows: list[dict[str, object]] = []
    modids: set[str] = set()
    for target in targets_for(family):
        jar = find_jar(instance, target.jar_prefix)
        english_path, korean_path = language_paths(target.namespace)
        with ZipFile(jar) as archive:
            names = set(archive.namelist())
            english = (
                load_json_bytes(archive.read(english_path))
                if english_path in names
                else {}
            )
            korean = (
                load_json_bytes(archive.read(korean_path))
                if korean_path in names
                else {}
            )
            metadata = read_mod_metadata(archive)
            assets = asset_inventory(archive, target.namespace)
        modids.add(target.namespace)
        rows.append(
            {
                "label": target.label,
                "jar": jar.name,
                "namespace": target.namespace,
                "direct_integration": target.direct_integration,
                "english_keys": len(english),
                "bundled_korean_keys": len(korean),
                "metadata_mentions_family": sorted(
                    modid for modid in modids if modid.lower() in metadata.lower()
                ),
                **assets,
            }
        )
    extra_scope: list[dict[str, object]] = []
    installed_jars = sorted((instance / "mods").glob("*.jar"))
    for extra in EXTRA_SCOPE.get(family, ()):
        matches = [
            path
            for path in installed_jars
            if path.name.lower().startswith(str(extra["jar_prefix"]).lower())
        ]
        extra_scope.append(
            {
                "label": extra["label"],
                "installed": bool(matches),
                "jars": [path.name for path in matches],
                "language_target": False,
            }
        )
    return {
        "family": FAMILY_LABELS[family],
        "installed": rows,
        "extra_scope": extra_scope,
        "other_dependency_mentions": dependency_scan(instance, modids),
    }


def prepare(instance: Path, family: str, force: bool) -> dict[str, object]:
    """내장·5.4 한국어 후보를 출처별로 합쳐 작업본을 만든다."""
    work_root = PROJECT_ROOT / "working" / family
    legacy_path = instance / LEGACY_PACK
    legacy = ZipFile(legacy_path) if legacy_path.is_file() else None
    rows: list[dict[str, object]] = []
    try:
        for target in targets_for(family):
            jar = find_jar(instance, target.jar_prefix)
            english_path, korean_path = language_paths(target.namespace)
            with ZipFile(jar) as archive:
                english = load_json_bytes(archive.read(english_path))
                bundled = (
                    load_json_bytes(archive.read(korean_path))
                    if korean_path in archive.namelist()
                    else {}
                )
            legacy_korean = {}
            if legacy is not None and korean_path in legacy.namelist():
                legacy_korean = load_json_bytes(legacy.read(korean_path))
            project_output = OUTPUT_ASSETS / target.namespace / "lang/ko_kr.json"
            project_korean = (
                load_json(project_output) if project_output.is_file() else {}
            )
            target_root = work_root / target.namespace
            english_file = target_root / "en_us.json"
            korean_file = target_root / "ko_kr.json"
            source_file = target_root / "candidate_sources.json"
            if korean_file.exists() and not force:
                raise FileExistsError(
                    f"기존 작업본을 덮어쓰지 않습니다. --force 필요: {korean_file}"
                )
            korean: dict[str, object] = {}
            sources: dict[str, str] = {}
            for key, value in english.items():
                candidates = (
                    ("project_output_review", project_korean),
                    ("bundled_ko_kr", bundled),
                    ("legacy_5.4_candidate", legacy_korean),
                )
                for source_name, candidate in candidates:
                    if key not in candidate:
                        continue
                    candidate_value = candidate[key]
                    if (
                        isinstance(value, str)
                        and candidate_value == value
                        and not is_allowed_original(value)
                    ):
                        continue
                    korean[key] = candidate_value
                    sources[key] = source_name
                    break
                else:
                    korean[key] = value
                    sources[key] = "new_translation_required"
            target_root.mkdir(parents=True, exist_ok=True)
            english_file.write_text(
                json.dumps(english, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            korean_file.write_text(
                json.dumps(korean, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            source_file.write_text(
                json.dumps(sources, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            counts = Counter(sources.values())
            rows.append(
                {
                    "label": target.label,
                    "jar": jar.name,
                    "namespace": target.namespace,
                    "english_keys": len(english),
                    **dict(sorted(counts.items())),
                }
            )
    finally:
        if legacy is not None:
            legacy.close()
    report = {**inventory(instance, family), "language_candidates": rows}
    work_root.mkdir(parents=True, exist_ok=True)
    (work_root / "scope.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def quest_candidate_is_translation(source: object, candidate: object) -> bool:
    """퀘스트 후보가 영어 원문을 그대로 둔 값이 아닌지 판정한다."""
    if type(source) is not type(candidate):
        return False
    if isinstance(source, list) and len(source) != len(candidate):
        return False
    if quest_snbt.validate_value("candidate", source, candidate):
        return False
    source_text = quest_snbt.flatten(source)
    candidate_text = quest_snbt.flatten(candidate)
    return source_text != candidate_text or is_allowed_original(source_text)


def write_quest_candidates(
    root: Path,
    english: dict[str, object],
    bundled: dict[str, object],
    project: dict[str, object],
    force: bool,
) -> dict[str, object]:
    """퀘스트 영어·한국어 후보·출처 파일을 쓴다."""
    korean_file = root / "ko_kr.json"
    if korean_file.exists() and not force:
        raise FileExistsError(f"기존 퀘스트 작업본을 덮어쓰지 않습니다: {korean_file}")
    korean: dict[str, object] = {}
    sources: dict[str, str] = {}
    for key, value in english.items():
        for source_name, candidate in (
            ("project_output_review", project),
            ("installed_ko_kr_candidate", bundled),
        ):
            if key in candidate and quest_candidate_is_translation(
                value, candidate[key]
            ):
                korean[key] = candidate[key]
                sources[key] = source_name
                break
        else:
            korean[key] = value
            sources[key] = "new_translation_required"
    root.mkdir(parents=True, exist_ok=True)
    for name, value in (
        ("en_us.json", english),
        ("ko_kr.json", korean),
        ("candidate_sources.json", sources),
    ):
        (root / name).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return {
        "display_keys": len(english),
        **dict(sorted(Counter(sources.values()).items())),
    }


def related_quest_keys(instance: Path, family: str) -> dict[str, object]:
    """전용 챕터 밖에서 대상 네임스페이스를 쓰는 퀘스트 표시 키를 모은다."""
    namespaces = {target.namespace for target in targets_for(family)}
    dedicated = set(QUEST_CHAPTERS[family])
    chapters, _ = quest_audit.parse_chapters(instance / "config/ftbquests/quests")
    lang_root = instance / "config/ftbquests/quests/lang/en_us/chapters"
    related: dict[str, object] = {}
    for chapter in chapters:
        chapter_name = Path(chapter["filename"]).stem
        if chapter_name in dedicated:
            continue
        task_ids: set[str] = set()
        quest_ids: set[str] = set()
        for quest in chapter["quests"]:
            matched_tasks = {
                task["id"]
                for task in quest["tasks"]
                if task["item_id"].partition(":")[0] in namespaces
            }
            if matched_tasks:
                task_ids.update(matched_tasks)
                quest_ids.add(quest["id"])
        language_file = lang_root / f"{chapter_name}.snbt_merged"
        if not language_file.is_file():
            continue
        language = quest_snbt.parse_language_snbt(language_file)
        for key, value in language.items():
            if any(
                key.startswith(f"quest.{object_id}.") for object_id in quest_ids
            ) or any(key.startswith(f"task.{object_id}.") for object_id in task_ids):
                related[key] = value
            elif (
                family == "mekanism" and "mekanism" in quest_snbt.flatten(value).lower()
            ):
                related[key] = value
    return related


def prepare_quests(instance: Path, family: str, force: bool) -> dict[str, object]:
    """전용·관련 FTB Quests 표시 문구 작업본을 준비한다."""
    lang_root = instance / "config/ftbquests/quests/lang"
    project = (
        quest_snbt.parse_language_snbt(QUEST_OUTPUT) if QUEST_OUTPUT.is_file() else {}
    )
    rows: dict[str, object] = {}
    for chapter in QUEST_CHAPTERS[family]:
        english = quest_snbt.parse_language_snbt(
            lang_root / f"en_us/chapters/{chapter}.snbt_merged"
        )
        bundled_path = lang_root / f"ko_kr/chapters/{chapter}.snbt_merged"
        bundled = (
            quest_snbt.parse_language_snbt(bundled_path)
            if bundled_path.is_file()
            else {}
        )
        rows[chapter] = write_quest_candidates(
            PROJECT_ROOT / "working" / family / "quests" / chapter,
            english,
            bundled,
            project,
            force,
        )
    related = related_quest_keys(instance, family)
    installed_full = quest_snbt.parse_language_snbt(lang_root / "ko_kr.snbt")
    rows["related"] = write_quest_candidates(
        PROJECT_ROOT / "working" / family / "quests/related",
        related,
        installed_full,
        project,
        force,
    )
    report = {"family": FAMILY_LABELS[family], "chapters": rows}
    path = PROJECT_ROOT / "working" / family / "quest_scope.json"
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def redundant_item_task_title_keys(instance: Path, family: str) -> set[str]:
    """전용 챕터의 단일 ItemTask 중 중복 제목 키를 반환한다."""
    english_keys: set[str] = set()
    lang_root = instance / "config/ftbquests/quests/lang/en_us/chapters"
    for chapter in QUEST_CHAPTERS[family]:
        english_keys.update(
            quest_snbt.parse_language_snbt(lang_root / f"{chapter}.snbt_merged")
        )
    chapters, _ = quest_audit.parse_chapters(instance / "config/ftbquests/quests")
    dedicated = {
        chapter["filename"]: chapter
        for chapter in chapters
        if Path(chapter["filename"]).stem in QUEST_CHAPTERS[family]
    }
    keys: set[str] = set()
    for chapter in dedicated.values():
        for quest in chapter["quests"]:
            for task in quest["tasks"]:
                if (
                    task["type"] == "item"
                    and task["item_id"] != "ftbfiltersystem:smart_filter"
                    and f'task.{task["id"]}.title' in english_keys
                ):
                    keys.add(f'task.{task["id"]}.title')
    return keys


def remove_language_keys(text: str, keys: set[str]) -> str:
    """SNBT 언어 객체에서 지정한 최상위 키를 제거한다."""
    matches = list(quest_snbt.ENTRY_RE.finditer(text))
    replacements: list[tuple[int, int]] = []
    for index, match in enumerate(matches):
        if match.group(1) not in keys:
            continue
        end = (
            matches[index + 1].start() if index + 1 < len(matches) else text.rfind("}")
        )
        replacements.append((match.start(), end))
    for start, end in reversed(replacements):
        text = text[:start] + text[end:]
    return text


def build_quests(instance: Path, family: str) -> dict[str, object]:
    """검수한 퀘스트 번역을 누적 ko_kr.snbt에 병합한다."""
    redundant_keys = redundant_item_task_title_keys(instance, family)
    combined: dict[str, object] = {}
    for root in sorted((PROJECT_ROOT / "working" / family / "quests").glob("*")):
        korean_file = root / "ko_kr.json"
        if korean_file.is_file():
            combined.update(
                {
                    key: value
                    for key, value in load_json(korean_file).items()
                    if key not in redundant_keys
                }
            )
    installed_base = instance / "config/ftbquests/quests/lang/ko_kr.snbt"
    base = QUEST_OUTPUT if QUEST_OUTPUT.is_file() else installed_base
    restored: dict[str, object] = {}
    if QUEST_OUTPUT.is_file():
        installed = quest_snbt.parse_language_snbt(installed_base)
        current = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
        restored = {
            key: value for key, value in installed.items() if key not in current
        }
    merged = quest_snbt.merge_into_full_snbt(base, {**restored, **combined})
    merged = remove_language_keys(merged, redundant_keys)
    QUEST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    reparsed = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    if any(reparsed.get(key) != value for key, value in combined.items()):
        raise ValueError("퀘스트 누적 병합 결과가 작업본과 다릅니다.")
    remaining_redundant = sorted(redundant_keys & set(reparsed))
    if remaining_redundant:
        raise ValueError(f"중복 단일 ItemTask 제목 제거 실패: {remaining_redundant}")
    structure_overrides: list[str] = []
    if family == "mekanism":
        source = instance / "config/ftbquests/quests/chapters/mekanism.snbt"
        text = source.read_text(encoding="utf-8-sig")
        for english_name, (korean_name, expected) in MEKANISM_CUSTOM_NAMES.items():
            needle = f'\\"{english_name}\\"'
            if text.count(needle) != expected:
                raise ValueError(
                    f"Smart Filter 이름 개수 불일치: {english_name}="
                    f"{text.count(needle)} (예상 {expected})"
                )
            text = text.replace(needle, f'\\"{korean_name}\\"')
        destination = QUEST_CHAPTER_OUTPUT / "mekanism.snbt"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        structure_overrides.append(str(destination.relative_to(PROJECT_ROOT)))
    return {
        "family": FAMILY_LABELS[family],
        "merged_keys": len(combined),
        "removed_redundant_item_task_titles": len(redundant_keys),
        "structure_overrides": structure_overrides,
    }


def verify_quests(instance: Path, family: str) -> tuple[dict[str, object], list[str]]:
    """전용·관련 퀘스트와 fallback 표시 경로를 검증한다."""
    errors: list[str] = []
    output = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    redundant_keys = redundant_item_task_title_keys(instance, family)
    display_keys = 0
    english_display: dict[str, object] = {}
    for root in sorted((PROJECT_ROOT / "working" / family / "quests").glob("*")):
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        if not english_file.is_file() or not korean_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        english_display.update(english)
        display_keys += len(english)
        if list(english) != list(korean):
            errors.append(f"퀘스트 키 또는 순서 불일치: {root.name}")
            continue
        for key, source in english.items():
            target = korean[key]
            errors.extend(quest_snbt.validate_value(key, source, target))
            if key in redundant_keys:
                if key in output:
                    errors.append(f"중복 단일 ItemTask 제목이 출력에 남음: {key}")
                continue
            if output.get(key) != target:
                errors.append(f"퀘스트 누적 출력 불일치: {key}")
            source_text = quest_snbt.flatten(source)
            target_text = quest_snbt.flatten(target)
            if source_text == target_text and not is_allowed_original(
                quest_audit.strip_formatting(source_text)
            ):
                errors.append(f"분류되지 않은 퀘스트 영어 유지: {key}")
            expected_title = MEKANISM_QUEST_ITEM_TITLES.get(key)
            if (
                expected_title
                and quest_audit.strip_formatting(target_text) != expected_title
            ):
                errors.append(
                    f"퀘스트 제목과 아이템명 불일치: {key}="
                    f"{quest_audit.strip_formatting(target_text)!r}, 예상={expected_title!r}"
                )
    chapters, _ = quest_audit.parse_chapters(instance / "config/ftbquests/quests")
    dedicated = [
        chapter
        for chapter in chapters
        if Path(chapter["filename"]).stem in QUEST_CHAPTERS[family]
    ]
    custom_names = [
        task
        for chapter in dedicated
        for quest in chapter["quests"]
        for task in quest["tasks"]
        if task["custom_name"] and LATIN_WORD.search(task["custom_name"])
    ]
    tasks = [
        task
        for chapter in dedicated
        for quest in chapter["quests"]
        for task in quest["tasks"]
    ]
    explicit_task_titles = [
        task for task in tasks if f'task.{task["id"]}.title' in english_display
    ]
    redundant_single_item_titles = [
        task
        for task in explicit_task_titles
        if task["type"] == "item" and task["item_id"] != "ftbfiltersystem:smart_filter"
    ]
    unremoved_titles = [
        task
        for task in redundant_single_item_titles
        if f'task.{task["id"]}.title' in output
    ]
    if unremoved_titles:
        errors.append(
            "중복 단일 ItemTask 제목이 남아 있습니다: "
            + ", ".join(task["id"] for task in unremoved_titles)
        )
    first_task_fallbacks = [
        quest
        for chapter in dedicated
        for quest in chapter["quests"]
        if f'quest.{quest["id"]}.title' not in english_display
    ]
    for quest in first_task_fallbacks:
        if not quest["tasks"]:
            errors.append(f"제목과 Task가 모두 없는 퀘스트: {quest['id']}")
            continue
        first_task = quest["tasks"][0]
        task_title_key = f'task.{first_task["id"]}.title'
        if task_title_key in english_display:
            continue
        item_id = first_task["item_id"]
        if first_task["type"] != "item" or ":" not in item_id:
            errors.append(f"번역 경로를 확인할 수 없는 퀘스트 fallback: {quest['id']}")
            continue
        namespace, item_path = item_id.split(":", 1)
        language_path = OUTPUT_ASSETS / namespace / "lang" / "ko_kr.json"
        language = load_json(language_path) if language_path.is_file() else {}
        item_keys = (
            f"item.{namespace}.{item_path}",
            f"block.{namespace}.{item_path}",
            f"{namespace}.glyph_name.{item_path}",
        )
        if not any(key in language for key in item_keys):
            errors.append(
                f"아이템 이름이 없는 퀘스트 fallback: {quest['id']}={item_id}"
            )
    unresolved_custom_names = custom_names
    if family == "mekanism" and custom_names:
        structure_path = QUEST_CHAPTER_OUTPUT / "mekanism.snbt"
        if not structure_path.is_file():
            errors.append("Mekanism Smart Filter 구조 오버라이드 누락")
        else:
            structure_text = structure_path.read_text(encoding="utf-8")
            remaining = [
                name
                for name in MEKANISM_CUSTOM_NAMES
                if f'\\"{name}\\"' in structure_text
            ]
            expected_korean = sum(
                expected for _, expected in MEKANISM_CUSTOM_NAMES.values()
            )
            actual_korean = sum(
                structure_text.count(f'\\"{name}\\"')
                for name in {value[0] for value in MEKANISM_CUSTOM_NAMES.values()}
            )
            if remaining or actual_korean != expected_korean:
                errors.append(
                    "Smart Filter 구조 오버라이드 검증 실패: "
                    f"영어={remaining}, 한국어={actual_korean}/{expected_korean}"
                )
            else:
                unresolved_custom_names = []
    report = {
        "chapters": [chapter["filename"] for chapter in dedicated],
        "quests_checked": sum(len(chapter["quests"]) for chapter in dedicated),
        "tasks_checked": sum(
            len(quest["tasks"]) for chapter in dedicated for quest in chapter["quests"]
        ),
        "display_keys_checked": display_keys,
        "source_english_custom_names": len(custom_names),
        "unresolved_english_custom_names": len(unresolved_custom_names),
        "explicit_task_titles": len(explicit_task_titles),
        "source_redundant_single_item_task_titles": len(redundant_single_item_titles),
        "remaining_redundant_single_item_task_titles": len(unremoved_titles),
        "first_task_quest_fallbacks": len(first_task_fallbacks),
        "fallback_paths_checked": [
            "chapter/group title",
            "quest title/subtitle/description",
            "task title",
            "item hover name",
            "custom_name/literal component",
            "first-task quest fallback",
        ],
    }
    return report, errors


def normalize_mekanism_value(key: str, english: str, korean: str) -> str:
    """Mekanism 계열의 확정 용어와 반복 패턴을 적용한다."""
    if key in MEKANISM_KEY_OVERRIDES:
        return MEKANISM_KEY_OVERRIDES[key]
    if english in MEKANISM_EXACT:
        return MEKANISM_EXACT[english]
    factory = re.fullmatch(
        r"(Basic|Advanced|Elite|Ultimate|Overclocked|Quantum|Dense|Multiversal|Creative) "
        r"(Pigment Extracting|Painting) Factory",
        english,
    )
    if factory:
        process = "안료 추출" if factory.group(2) == "Pigment Extracting" else "염색"
        return f"{TIER_KO[factory.group(1)]} {process} 시스템"
    storage = re.fullmatch(r"(Basic|Advanced|Elite|Ultimate) Storage", english)
    if storage:
        return f"{TIER_KO[storage.group(1)]} 저장소"
    rate = re.fullmatch(r"(Basic|Advanced|Elite|Ultimate) Output Rate", english)
    if rate:
        return f"{TIER_KO[rate.group(1)]} 출력 속도"
    tank_tooltip = re.fullmatch(
        r"(Storage size|Output rate) of (Basic|Advanced|Elite|Ultimate) "
        r"(max|mid) chemical tanks in mb\.",
        english,
    )
    if tank_tooltip:
        label = "저장 용량" if tank_tooltip.group(1) == "Storage size" else "출력 속도"
        size = "최대" if tank_tooltip.group(3) == "max" else "중간"
        return f"{TIER_KO[tank_tooltip.group(2)]} {size} 화학 물질 탱크의 {label}(mB)입니다."
    rs_item = re.fullmatch(
        r"(64B|256B|1024B|8192B) Chemical Storage (Part|Disk|Block)", english
    )
    if rs_item:
        kind = {"Part": "부품", "Disk": "디스크", "Block": "블록"}[rs_item.group(2)]
        return f"{rs_item.group(1)} 화학 물질 저장 {kind}"
    rs_creative = re.fullmatch(r"Creative Chemical Storage (Disk|Block)", english)
    if rs_creative:
        kind = "디스크" if rs_creative.group(1) == "Disk" else "블록"
        return f"크리에이티브 화학 물질 저장 {kind}"
    rs_energy = re.fullmatch(r"(64B|256B|1024B|8192B|Creative) energy usage", english)
    if rs_energy:
        tier = (
            "크리에이티브" if rs_energy.group(1) == "Creative" else rs_energy.group(1)
        )
        return f"{tier} 에너지 사용량"
    rs_energy_tooltip = re.fullmatch(
        r"The energy used by the (64B|256B|1024B|8192B|Creative) "
        r"Chemical Storage Block\.",
        english,
    )
    if rs_energy_tooltip:
        tier = (
            "크리에이티브"
            if rs_energy_tooltip.group(1) == "Creative"
            else rs_energy_tooltip.group(1)
        )
        return f"{tier} 화학 물질 저장 블록이 사용하는 에너지입니다."
    replacements = (
        ("정제된 저장소", "Refined Storage"),
        ("메카니즘", "Mekanism"),
        ("화학물질", "화학 물질"),
        ("약품", "화학 물질"),
        ("케미컬", "화학 물질"),
        ("데미지", "피해"),
        ("대미지", "피해"),
        ("멀티블럭", "멀티블록"),
        ("반양자성", "반양성자"),
        ("페인팅", "염색"),
        ("회화", "염색"),
        ("팩토리", "시스템"),
        ("스토리지", "저장소"),
        ("창의적인", "크리에이티브"),
        ("창조적", "크리에이티브"),
        ("창의", "크리에이티브"),
        ("첨단", "고급"),
        ("기초", "기본"),
        ("궁극적인", "궁극"),
        ("궁극적", "궁극"),
        ("항목", "아이템"),
        ("물류 운송업자", "물류 수송기"),
        ("동적 탱크", "다이나믹 탱크"),
        ("기계장치", "기계"),
        ("머신", "기계"),
        ("강괴", "강철 주괴"),
        ("케이싱 글래스", "케이싱 유리"),
        ("업그레이드 제거", "업그레이드 회수"),
        ("절삭유", "냉각재"),
        ("AllTheMods Staff", "AllTheMods 운영진"),
        ("All Rights Reserved", "모든 권리 보유"),
        ("AllTheMods Team", "AllTheMods 팀"),
        ("(MB)", "(mB)"),
        ("(mb)", "(mB)"),
    )
    for old, new in replacements:
        korean = korean.replace(old, new)
    for old, new in MEKANISM_QUEST_WORDS.items():
        pattern = (
            rf"(^|\\n|[^A-Za-z]|[&§][0-9A-FK-ORa-fk-or])"
            rf"{re.escape(old)}(?![A-Za-z])"
        )
        korean = re.sub(pattern, lambda match: match.group(1) + new, korean)
    korean = korean.replace("Tier ", "단계 ")
    return korean


def apply_title_name(value: str, name: str) -> str:
    """제목의 서식 코드 개수를 보존하면서 표시 이름을 확정명으로 맞춘다."""
    codes = FORMAT_CODE.findall(value)
    prefix = "".join(code for code in codes if code.lower() not in {"&r", "§r"})
    suffix = "".join(code for code in codes if code.lower() in {"&r", "§r"})
    return prefix + name + suffix


def normalize(family: str) -> dict[str, object]:
    """모드군별 검수에서 확정한 반복 용어와 패턴을 작업본에 적용한다."""
    if family != "mekanism":
        return {"family": FAMILY_LABELS[family], "changed": 0}
    changed = 0
    for target in targets_for(family):
        root = PROJECT_ROOT / "working" / family / target.namespace
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        for key, source in english.items():
            if not isinstance(source, str) or not isinstance(korean[key], str):
                continue
            normalized = normalize_mekanism_value(key, source, korean[key])
            if normalized != korean[key]:
                korean[key] = normalized
                changed += 1
        (root / "ko_kr.json").write_text(
            json.dumps(korean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    quest_root = PROJECT_ROOT / "working" / family / "quests"
    for root in sorted(quest_root.glob("*")):
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        if not english_file.is_file() or not korean_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        for key, source in english.items():
            source_values = source if isinstance(source, list) else [source]
            target_values = (
                korean[key] if isinstance(korean[key], list) else [korean[key]]
            )
            if len(source_values) != len(target_values):
                continue
            normalized_values = [
                normalize_mekanism_value(key, source_text, target_text)
                if isinstance(source_text, str) and isinstance(target_text, str)
                else target_text
                for source_text, target_text in zip(
                    source_values, target_values, strict=True
                )
            ]
            for old, new in MEKANISM_QUEST_TEXT_REPLACEMENTS.get(key, ()):
                normalized_values = [
                    value.replace(old, new) for value in normalized_values
                ]
            if key in MEKANISM_QUEST_ITEM_TITLES:
                normalized_values = [
                    apply_title_name(value, MEKANISM_QUEST_ITEM_TITLES[key])
                    for value in normalized_values
                ]
            for index, value in MEKANISM_QUEST_ELEMENT_OVERRIDES.get(key, {}).items():
                normalized_values[index] = value
            normalized: object = (
                normalized_values
                if isinstance(korean[key], list)
                else normalized_values[0]
            )
            if normalized != korean[key]:
                korean[key] = normalized
                changed += 1
        korean_file.write_text(
            json.dumps(korean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return {"family": FAMILY_LABELS[family], "changed": changed}


def validate_value(key: str, source: object, target: object) -> list[str]:
    """자료형·자리표시자·줄바꿈·서식 코드를 검사한다."""
    errors: list[str] = []
    if type(source) is not type(target):
        return [f"자료형 불일치: {key}"]
    if not isinstance(source, str):
        return errors
    assert isinstance(target, str)
    if Counter(PLACEHOLDER.findall(source)) != Counter(PLACEHOLDER.findall(target)):
        errors.append(f"자리표시자 불일치: {key}")
    if source.count("\n") != target.count("\n"):
        errors.append(f"줄바꿈 불일치: {key}")
    if Counter(FORMAT_CODE.findall(source)) != Counter(FORMAT_CODE.findall(target)):
        errors.append(f"서식 코드 불일치: {key}")
    return errors


def is_allowed_original(source: str) -> bool:
    """고유명사·키·식별자처럼 의도적으로 유지 가능한 값을 판정한다."""
    stripped = source.strip()
    return (
        stripped in ALLOWED_ORIGINALS
        or TRANSLATION_KEY.fullmatch(stripped) is not None
        or re.fullmatch(r"\{image:[^}]+\}", stripped) is not None
        or not LATIN_WORD.search(stripped)
        or bool(re.fullmatch(r"[A-Z0-9_+./:%×() -]+", stripped))
    )


def verify_language(
    instance: Path, family: str
) -> tuple[list[dict[str, object]], list[str]]:
    """모드군 언어 파일과 누적 출력의 완전성을 검사한다."""
    rows: list[dict[str, object]] = []
    errors: list[str] = []
    for target in targets_for(family):
        root = PROJECT_ROOT / "working" / family / target.namespace
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        if not english_file.is_file() or not korean_file.is_file():
            errors.append(f"작업본 누락: {target.namespace}")
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        if list(english) != list(korean):
            errors.append(f"키 또는 순서 불일치: {target.namespace}")
            continue
        raw = korean_file.read_text(encoding="utf-8")
        duplicates = duplicate_keys(raw)
        if duplicates:
            errors.append(f"중복 키: {target.namespace}:{duplicates}")
        if korean_file.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"UTF-8 BOM: {target.namespace}")
        untranslated: list[str] = []
        names_by_korean: dict[str, list[str]] = defaultdict(list)
        for key, source in english.items():
            target_value = korean[key]
            errors.extend(validate_value(key, source, target_value))
            if (
                key.startswith(("item.", "block."))
                and isinstance(source, str)
                and isinstance(target_value, str)
            ):
                names_by_korean[target_value].append(key)
            if (
                isinstance(source, str)
                and isinstance(target_value, str)
                and source == target_value
                and not is_allowed_original(source)
            ):
                untranslated.append(key)
        collisions = []
        for translated, keys in names_by_korean.items():
            source_names = {english[key] for key in keys}
            if (
                len(source_names) > 1
                and frozenset(source_names) not in ALLOWED_NAME_COLLISIONS
            ):
                collisions.append(
                    {
                        "translation": translated,
                        "keys": keys,
                        "english": sorted(source_names),
                    }
                )
        if collisions:
            errors.append(f"번역으로 생긴 이름 충돌: {target.namespace}:{collisions}")
        output = OUTPUT_ASSETS / target.namespace / "lang/ko_kr.json"
        expected_output = dict(korean)
        guide_extra_path = PROJECT_ROOT / "working/ars_nouveau/guide_extra_ko_kr.json"
        guide_extra_keys = 0
        if family == "ars_nouveau" and guide_extra_path.is_file():
            guide_extra = {
                key: value
                for key, value in load_json(guide_extra_path).items()
                if key.startswith(f"{target.namespace}.")
            }
            expected_output.update(guide_extra)
            guide_extra_keys = len(guide_extra)
        output_matches = output.is_file() and load_json(output) == expected_output
        if not output_matches:
            errors.append(f"누적 출력 불일치: {target.namespace}")
        jar = find_jar(instance, target.jar_prefix)
        _, korean_path = language_paths(target.namespace)
        with ZipFile(jar) as archive:
            bundled = (
                load_json_bytes(archive.read(korean_path))
                if korean_path in archive.namelist()
                else {}
            )
        legacy_path = instance / LEGACY_PACK
        with ZipFile(legacy_path) as legacy:
            legacy_korean = (
                load_json_bytes(legacy.read(korean_path))
                if korean_path in legacy.namelist()
                else {}
            )
        provenance = Counter()
        for key, target_value in korean.items():
            source_value = english[key]
            reusable = target_value != source_value or is_allowed_original(
                str(target_value)
            )
            if key in bundled and target_value == bundled[key] and reusable:
                provenance["bundled_exact_reuse"] += 1
            elif (
                key in legacy_korean and target_value == legacy_korean[key] and reusable
            ):
                provenance["legacy_exact_reuse"] += 1
            else:
                provenance["new_or_edited"] += 1
        rows.append(
            {
                "label": target.label,
                "jar": jar.name,
                "namespace": target.namespace,
                "english_keys": len(english),
                "korean_keys": len(korean),
                "untranslated": len(untranslated),
                "untranslated_examples": untranslated[:30],
                "duplicate_keys": len(duplicates),
                "translation_induced_name_collisions": len(collisions),
                "output_matches": output_matches,
                "guide_extra_keys": guide_extra_keys,
                **dict(provenance),
            }
        )
        if untranslated:
            errors.append(
                f"분류되지 않은 영어 유지: {target.namespace}:{untranslated[:30]}"
            )
    return rows, errors


def build(family: str) -> dict[str, object]:
    """검수한 작업본을 누적 리소스팩에 반영한다."""
    copied: list[str] = []
    for target in targets_for(family):
        source = PROJECT_ROOT / "working" / family / target.namespace / "ko_kr.json"
        if not source.is_file():
            raise FileNotFoundError(source)
        destination = OUTPUT_ASSETS / target.namespace / "lang/ko_kr.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        guide_extra_path = PROJECT_ROOT / "working/ars_nouveau/guide_extra_ko_kr.json"
        if family == "ars_nouveau" and guide_extra_path.is_file():
            merged = load_json(destination)
            merged.update(
                {
                    key: value
                    for key, value in load_json(guide_extra_path).items()
                    if key.startswith(f"{target.namespace}.")
                }
            )
            destination.write_text(
                json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        copied.append(destination.relative_to(PROJECT_ROOT).as_posix())
    return {"family": FAMILY_LABELS[family], "copied": copied}


def verify(instance: Path, family: str) -> tuple[dict[str, object], int]:
    """모드군 언어 산출물을 검증하고 보고서를 기록한다."""
    languages, errors = verify_language(instance, family)
    quests, quest_errors = verify_quests(instance, family)
    errors.extend(quest_errors)
    provenance = {
        key: sum(int(row.get(key, 0)) for row in languages)
        for key in (
            "bundled_exact_reuse",
            "legacy_exact_reuse",
            "new_or_edited",
        )
    }
    report = {
        "family": FAMILY_LABELS[family],
        "languages": languages,
        "language_provenance": provenance,
        "ftbquests": quests,
        "validation_errors": len(errors),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    path = PROJECT_ROOT / "working" / family / "language_validation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "inventory",
            "prepare",
            "prepare-quests",
            "normalize",
            "build",
            "build-quests",
            "verify",
        ),
    )
    parser.add_argument("family", choices=tuple(FAMILY_LABELS))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root()
    if args.command == "inventory":
        result = inventory(instance, args.family)
        report_path = PROJECT_ROOT / "working" / args.family / "inventory.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        status = 0
    elif args.command == "prepare":
        result = prepare(instance, args.family, args.force)
        status = 0
    elif args.command == "prepare-quests":
        result = prepare_quests(instance, args.family, args.force)
        status = 0
    elif args.command == "normalize":
        result = normalize(args.family)
        status = 0
    elif args.command == "build-quests":
        result = build_quests(instance, args.family)
        status = 0
    elif args.command == "build":
        result = build(args.family)
        status = 0
    else:
        result, status = verify(instance, args.family)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
