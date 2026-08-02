#!/usr/bin/env python3
"""Oritech Oracle Index 가이드·발전 과제·KubeJS 표시 경로를 처리한다."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

import ars_family
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root
import oritech_family


WORK_ROOT = PROJECT_ROOT / "working/oritech/guide"
ENGLISH_ROOT = WORK_ROOT / "en_us"
CANDIDATE_ROOT = WORK_ROOT / "candidate"
KOREAN_ROOT = WORK_ROOT / "ko_kr"
OUTPUT_ROOT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/oracle_index/books/oritech/translated/ko_kr"
)
CACHE_FILE = PROJECT_ROOT / "temp/oritech_guide_candidate_cache.json"
JAR_PREFIX = "oritech-neoforge-"
BOOK_PREFIX = "assets/oracle_index/books/oritech/"

CUSTOM_PROTECTED = re.compile(
    r"`[^`]*`"
    r"|\((?:@|\$|https?://)[^)]+\)"
    r"|\{[^{}]+\}"
    r"|<[^>]+>"
    r"|(?:[a-z0-9_.-]+):[a-z0-9_./-]+"
    r"|\*\*"
    r"|__"
)
LINK_TARGET = re.compile(r"\]\(([^)]+)\)")
COMPONENT = re.compile(r"<[^>]+>")
IDENTIFIER = re.compile(r"(?:[a-z0-9_.-]+):[a-z0-9_./-]+")
NUMBER = re.compile(r"\d+(?:[.,]\d+)*(?:[xX×]\d+)?")
VISIBLE_LINK_TARGET = re.compile(r"\]\((?:@|\$|https?://)[^)]+\)")
VISIBLE_LINK = re.compile(r"\[[^\[\]]+\]\((?:@|\$|https?://)[^)]+\)")
VISIBLE_WORD = re.compile(r"[A-Za-z][A-Za-z'-]{2,}")
ISOLATED_TRANSLATION_ARTIFACT = re.compile(
    r"(?<![A-Za-z0-9:/_])(?:A|I|Z|E|M|a|i|it)(?![A-Za-z0-9:/_])"
)
HANGUL_LATIN_SUFFIX = re.compile(r"(?<=[가-힣])[A-Za-z]{1,2}\b")
ALLOWED_VISIBLE_WORDS = frozenset(
    {
        "Oritech",
        "RF",
        "GUI",
        "UI",
        "JEI",
        "REI",
        "EMI",
        "TNT",
        "NBT",
        "AE2",
        "RS2",
        "AI",
        "HP",
        "Shift",
        "GitHub",
        "Java",
        "Inc",
        "JSON",
        "FTB",
        "XP",
        "TL",
        "DR",
        "mB",
        "blockCount",
        "typeCount",
        "min",
        "sqrt",
        "collisionEnergy",
        "temperatureDiff",
        "neighborHeat",
        "pulses",
    }
)
FORBIDDEN_KOREAN_ARTIFACTS = (
    "그것은",
    "그들은",
    "그들의",
    "이것은",
    "기계은",
    "기계 핵가",
    "기계 핵를",
    "블록를",
    "아이템를",
    "조합법는",
    "조합법를",
    "확인하십시오",
    "기억하십시오",
    "정유소",
    "품목",
    "엔터티",
    "리소스",
    "어셈블러",
    "체인톱",
    "마이닝",
)

GUIDE_REPLACEMENTS = (
    ("Oritech은", "Oritech는"),
    ("Oritech이", "Oritech가"),
    ("오리테크", "Oritech"),
    ("오리텍", "Oritech"),
    ("엔더릭 레이저", "엔더릭 레이저"),
    ("엔더릭 레이저", "엔더릭 레이저"),
    ("Fragment Forge", "파편 단조기"),
    ("Pulverizer", "분쇄기"),
    ("Centrifuge", "원심 분리기"),
    ("Atomic Forge", "원자 단조기"),
    ("Machine Core", "기계 핵"),
    ("Machine Cores", "기계 핵"),
    ("Fluid Addon", "유체 애드온"),
    ("Addon", "애드온"),
    ("add-on", "애드온"),
    ("추가 기능", "애드온"),
    ("플럭스사이트", "플럭사이트"),
    ("플럭사이트(플럭사이트)", "플럭사이트"),
    ("최종 최종 게임", "최종 단계"),
    ("전동 도구", "전동 공구"),
    ("반응기", "원자로"),
    ("리액터", "원자로"),
    ("조합법가", "조합법이"),
    ("기계을", "기계를"),
    ("블록를", "블록을"),
    ("시작하십시오", "시작하세요"),
    ("사용하십시오", "사용하세요"),
    ("프로메테움", "프로메튬"),
    ("프로메티움", "프로메튬"),
    ("단호한", "아다만트"),
    ("원시 니켈", "가공 전 니켈"),
    ("원시 우라늄", "가공 전 우라늄"),
    ("원시 백금", "가공 전 백금"),
    ("재고", "인벤토리"),
    ("항목 파이프", "아이템 파이프"),
    ("항목을", "아이템을"),
    ("항목이", "아이템이"),
    ("항목의", "아이템의"),
    ("항목은", "아이템은"),
    ("머신 코어", "기계 핵"),
    ("기계 코어", "기계 핵"),
    ("## Usage", "## 사용법"),
    ("**Usage**", "**사용법**"),
    ("**Crafting**", "**제작**"),
    ("## Variants", "## 변형"),
    ("**Standard**", "**표준형**"),
    ("**Framed**", "**프레임형**"),
    ("**Duct**", "**덕트형**"),
    ("**Combat**", "**전투**"),
    ("#### Combat", "#### 전투"),
    ("**Unbreakable**", "**파괴 불가**"),
    ("**Infinite**", "**무한**"),
    ("**Energy**", "**에너지**"),
    ("**Charging**", "**충전**"),
    ("**Decay**", "**감쇠**"),
    ("**Range**", "**범위**"),
    ("**Toggle**", "**전환**"),
    ("**Processing**", "**처리**"),
    ("**Hanging**", "**매달기**"),
    ("**Entity Capture**", "**엔티티 포획**"),
    ("**Night Vision**", "**야간 투시**"),
    ("**Extended Reach**", "**확장된 사거리**"),
    ("**Energy Saver**", "**에너지 절약**"),
    ("Night Vision", "야간 투시"),
    ("Ore Vision", "광석 투시"),
    ("Far Reach", "원거리 상호작용"),
    ("Hyper Speed", "초고속"),
    ("Silk Touch", "섬세한 손길"),
    ("Fortune", "행운"),
    ("Unbreaking", "내구성"),
    ("Redstone Control", "레드스톤 제어"),
    ("Spawn Range", "생성 범위"),
    ("Catalyst Count", "촉매 수"),
    ("Active Rod Count", "활성 연료봉 수"),
    ("Energy Saver", "에너지 절약"),
    ("Modifier Augments", "속성 증강"),
    ("Effect Augments", "효과 증강"),
    ("Custom Augments", "사용자 지정 증강"),
    ("Research Stations", "연구대"),
    ("Research Station", "연구대"),
    ("Boosted Exo Elytra", "강화 엑소 겉날개"),
    ("Boosted Elytra", "강화 겉날개"),
    ("Exo Jetpack", "엑소 제트팩"),
    ("Exo Helmet", "엑소 헬멧"),
    ("Exo Chestplate", "엑소 흉갑"),
    ("Exo Leggings", "엑소 레깅스"),
    ("Exo Boots", "엑소 부츠"),
    ("Enderic", "엔더릭"),
    ("Sculk", "스컬크"),
    ("Spawner", "생성기"),
    ("Uranium", "우라늄"),
    ("Platinum", "백금"),
    ("Nickel", "니켈"),
    ("Amethyst", "자수정"),
    ("Duratium", "듀라티움"),
    ("듀라튬", "듀라티움"),
    ("Dubios", "두비오스"),
    ("Allay", "알레이"),
    ("Vex", "벡스"),
    ("buckets per pulse", "양동이/펄스"),
    ("items per pulse", "아이템/펄스"),
    ("buckets each", "각각 양동이"),
    ("buckets", "양동이"),
    ("blocks", "블록"),
    ("ticks", "틱"),
    ("Infinite", "무한"),
    ("Yield Addon", "수확량 애드온"),
    ("Yield 애드온", "수확량 애드온"),
    ("Hunter 애드온", "사냥 애드온"),
    ("addon 슬롯", "애드온 슬롯"),
    ("addon 블록", "애드온 블록"),
    ("redstone", "레드스톤"),
    ("energy", "에너지"),
    ("fluid", "유체"),
    ("extra", "추가"),
    ("most", "대부분의"),
    ("each", "각각"),
    ("one", "하나"),
    ("recipes", "조합법"),
    ("recipe", "조합법"),
    ("레시피", "조합법"),
    ("액체", "유체"),
    ("버킷", "양동이"),
    ("진드기", "틱"),
    ("생물 군계", "생물군계"),
    ("원광석", "가공 전 광석"),
    ("실크 터치", "섬세한 손길"),
    ("플래티넘", "백금"),
    ("잉곳", "주괴"),
    ("더스트", "가루"),
    ("너겟", "조각"),
    ("펠렛", "펠릿"),
    ("크리스탈", "수정"),
    ("미네랄 슬러리", "광물 슬러리"),
    ("실리콘 워시", "실리콘 세척액"),
    ("## 용법", "## 사용법"),
    ("## 속보", "## 해체"),
    ("## 창조", "## 생성"),
    ("기계 핵가", "기계 핵이"),
    ("기계 핵는", "기계 핵은"),
    ("블록를", "블록을"),
    ("아이템를", "아이템을"),
    ("유체를를", "유체를"),
    ("머신", "기계"),
    ("항목", "아이템"),
    ("조합법를", "조합법을"),
    ("기계 핵를", "기계 핵을"),
    ("유체 입력가", "유체 입력이"),
    ("번역 아이템", "번역 항목"),
    ("closest", "가장 가까운"),
    ("networks", "네트워크"),
    ("Souls", "영혼"),
    ("souls", "영혼"),
    ("Soul Soil", "영혼 흙"),
    ("cage", "우리"),
    ("slab", "반 블록"),
    ("stair", "계단"),
    ("plate", "감압판"),
    ("Tech Lever", "기술 레버"),
    ("Tier", "등급"),
    ("Ender", "엔더"),
    ("Cloak", "은신"),
    ("Exo", "엑소"),
    ("exo", "엑소"),
    ("elytra", "겉날개"),
    ("Super", "슈퍼"),
    ("Obtaining", "획득"),
    ("cobwebs", "거미줄"),
    ("Efficiency", "효율"),
    ("Sharpness", "날카로움"),
    ("Harvesting", "수확"),
    ("EEnchanting", "마법 부여"),
    ("Tree Felling", "나무 벌목"),
    ("Sneaking", "웅크리기"),
    ("Battleaxe", "전투 도끼"),
    ("zipline", "집라인"),
    ("Transparent", "투명형"),
    ("version", "변형"),
    ("Synergy Matrix", "시너지 매트릭스"),
    ("Quarry", "채석"),
    ("Folding Mechanic", "접이식 구조"),
    ("Slave", "보조"),
    ("Yield Mechanics", "생산량 방식"),
    ("Automation", "자동화"),
    ("Temperature", "온도"),
    ("Plutonium", "플루토늄"),
    ("Electrum", "일렉트럼"),
    ("Ore Boulders", "광석 바위"),
    ("fluxite", "플럭사이트"),
    ("마법부여사", "안정화 마법 부여기"),
    ("마법부여", "마법 부여"),
    ("정유소", "정유기"),
    ("품목", "아이템"),
    ("엔터티", "엔티티"),
    ("리소스 노드", "자원 노드"),
    ("리소스", "자원"),
    ("어셈블러", "조립기"),
    ("체인톱", "전기톱"),
    ("마이닝", "채굴"),
    ("야간 투시경", "야간 투시"),
    ("광석 비전", "광석 투시"),
    ("하이퍼 채굴", "초고속 채굴"),
    ("기계은", "기계는"),
    ("조합법는", "조합법은"),
    ("입력**가", "입력**이"),
    ("내구성**를", "내구성**을"),
    ("섬세한 손길와", "섬세한 손길과"),
    ("원거리 상호작용와", "원거리 상호작용과"),
    ("구성요소", "구성 요소"),
    ("기본적으로 작동합니다", "별도 설정 없이 작동합니다"),
    ("E에너지", "에너지"),
    ("E설치", "설치"),
    ("E각", "각"),
    ("A [원자로", "[원자로"),
    ("A 직선", "직선"),
    ("A 입자는", "입자는"),
    ("A [", "["),
    ("**16 블록 **", "**16블록**"),
    ("** 플러시 마운트**", "**매립형**"),
)

FINAL_GUIDE_REPLACEMENTS = (
    ("조합법가", "조합법이"),
    ("조합법는", "조합법은"),
    ("조합법를", "조합법을"),
    ("기계은", "기계는"),
    ("기계을", "기계를"),
    ("기계 핵가", "기계 핵이"),
    ("기계 핵를", "기계 핵을"),
    ("블록를", "블록을"),
    ("아이템를", "아이템을"),
    ("원자로 히트파이프", "원자로 열 파이프"),
    ("반응기", "원자로"),
    ("리액터", "원자로"),
    ("품목", "아이템"),
    ("엔터티", "엔티티"),
    ("어셈블러", "조립기"),
    ("체인톱", "전기톱"),
)

MANUAL_CANDIDATES = {
    (
        "- **Level Requirement**: The book used must be at the **maximum vanilla level** for that \n"
        "enchantment.\n"
        "- **No Restrictions**: This method ignores standard enchantment rules, allowing you \n"
        "to apply any enchantment to any item.\n"
        "- **Hyper Levels**: If the item already has the enchantment at its maximum level, \n"
        'the catalyst can "hyper enchant" it to even higher levels.\n'
        "- **Consumption**: The enchanted book is consumed during the hyper enchanting process."
    ): (
        "- **레벨 요구 사항**: 사용하는 책의 마법은 해당 마법의 **바닐라 최대 레벨**이어야 \n"
        "합니다.\n"
        "- **제한 없음**: 일반적인 마법 부여 규칙을 무시하므로 어떤 아이템에도 원하는 \n"
        "마법을 적용할 수 있습니다.\n"
        "- **초월 레벨**: 아이템에 이미 최대 레벨의 마법이 있다면 촉매로 마법 레벨을 \n"
        "더욱 높일 수 있습니다.\n"
        "- **소모**: 초월 마법 부여 과정에서 마법이 부여된 책이 소모됩니다."
    ),
    (
        "Tachyon collectors can be used to catch those particles and turn them into energy. "
        "The tachyons always exit in random directions at the collision point. Surrounding\n"
        "the entire area in collectors ensures you will catch them all. If all tachyons are "
        "collected, you can get up to 4x the amount of energy that was used to accelerate\n"
        "the particles."
    ): (
        "타키온 수집기로 이 입자를 붙잡아 에너지로 바꿀 수 있습니다. 타키온은 충돌 지점에서 "
        "항상 무작위 방향으로 빠져나갑니다. 전체 영역을\n"
        "수집기로 둘러싸면 모든 타키온을 붙잡을 수 있습니다. 타키온을 전부 수집하면 입자를 "
        "가속하는 데 사용한 에너지의 최대 4배를\n"
        "얻을 수 있습니다."
    ),
    (
        "In addition to increased capacity, it also improves the machine's\n"
        "throughput by adding 2 000 RF/t of transfer rate.\n"
        "This ensures that high-speed machines with many addons can receive\n"
        "enough energy to operate without interruption."
    ): (
        "용량이 늘어날 뿐 아니라 기계의\n"
        "전송 속도에 2 000 RF/t를 더해 처리량도 높입니다.\n"
        "덕분에 애드온을 많이 장착한 고속 기계도 중단 없이 작동하는 데\n"
        "충분한 에너지를 받을 수 있습니다."
    ),
    (
        "### Ore Locations\n"
        "- **Nickel**: Generates between **Y -65 and Y 40**. It is also a very common component\n"
        "of surface ore boulders.\n"
        "- **Platinum**: Rare ore in the overworld, generating between **Y -60 and Y -20**.\n"
        "It is much more abundant in **The End**.\n"
        "- **Uranium**: Found in [Uranium Veins](@oritech:deepslate_uranium_ore) in deep caves.\n"
        "- **Vanilla Ores**: Iron, copper, and gold can also be found in ore boulders\n"
        "and as resource nodes."
    ): (
        "### 광석 위치\n"
        "- **니켈**: **Y -65에서 Y 40** 사이에 생성됩니다. 지표 광석 바위에도 매우 흔하게\n"
        "포함됩니다.\n"
        "- **백금**: 오버월드의 희귀 광석으로 **Y -60에서 Y -20** 사이에 생성됩니다.\n"
        "**엔드**에서는 훨씬 풍부합니다.\n"
        "- **우라늄**: 깊은 동굴의 [우라늄 광맥](@oritech:deepslate_uranium_ore)에서 발견됩니다.\n"
        "- **바닐라 광석**: 철, 구리와 금도 광석 바위나\n"
        "자원 노드에서 찾을 수 있습니다."
    ),
    (
        "*   **Standard Mining**: Breaking the crystals will drop raw uranium, which can be "
        "processed into fuel.\n"
        "*   **Enderic Laser**: Destroying a crystal with an "
        "[Enderic Laser](@oritech:laser_arm_block)\n"
        "will yield **plutonium dust** instead. Plutonium is a much stronger fuel source\n"
        "for [Nuclear Reactors]($reactor/introduction).\n"
        "*   **Non-Renewable**: Unlike amethyst, Uranium Crystals do not regrow.\n"
        "Once a vein is depleted, you must find another."
    ): (
        "*   **일반 채굴**: 수정을 부수면 연료로 가공할 수 있는 가공 전 우라늄이 떨어집니다.\n"
        "*   **엔더릭 레이저**: [엔더릭 레이저](@oritech:laser_arm_block)로 수정을 파괴하면\n"
        "대신 **플루토늄 가루**를 얻습니다. 플루토늄은 [원자로]($reactor/introduction)에\n"
        "사용하는 훨씬 강력한 연료입니다.\n"
        "*   **재생 불가**: 우라늄 수정은 자수정과 달리 다시 자라지 않습니다.\n"
        "광맥을 모두 채굴하면 다른 광맥을 찾아야 합니다."
    ),
    (
        "Each cycle, the machine will attempt to start a new recipe for every\n"
        "available chamber.\n"
        "If you have three chamber addons, the machine can process four items at\n"
        "the same time.\n"
        "This is much more effective than speed addons for recipes that have a\n"
        "very long duration."
    ): (
        "기계는 매 주기마다 사용 가능한 각 처리실에서 새 조합법을\n"
        "시작하려 합니다.\n"
        "처리실 애드온이 세 개라면 아이템 네 개를\n"
        "동시에 처리할 수 있습니다.\n"
        "처리 시간이 매우 긴 조합법에서는 속도 애드온보다\n"
        "훨씬 효과적입니다."
    ),
    (
        "The reactor allows some heat to build up. Ideally, a properly cooled reactor does not "
        "produce any leaking heat. However, some components,\n"
        "such as the heat vents, are more efficient in hotter environments. If too much heat is "
        "created that cannot be removed, the fuel rods may overheat,\n"
        "resulting in a nuclear meltdown. If a rod reaches a temperature above 2000 C for a "
        "sustained amount of time, it will trigger a meltdown.\n"
        "Warning sirens will engage before the reactor reaches those temperatures. Depending on "
        "the size of the reactor and the number of rods,\n"
        "the meltdown will result in a bigger or smaller explosion."
    ): (
        "원자로에는 어느 정도 열이 쌓일 수 있습니다. 제대로 냉각된 원자로라면 이상적으로는 "
        "외부로 새는 열이 없어야 합니다. 하지만 방열구 같은 일부 부품은\n"
        "온도가 높은 환경에서 더 효율적입니다. 제거할 수 없을 만큼 열이 많이 발생하면 "
        "연료봉이 과열되어\n"
        "노심 용융이 일어날 수 있습니다. 연료봉 온도가 2000 C를 넘은 채 일정 시간 유지되면 "
        "노심 용융이 시작됩니다.\n"
        "원자로가 해당 온도에 도달하기 전에 경고 사이렌이 울립니다. 원자로 크기와 연료봉 수에 "
        "따라\n"
        "노심 용융으로 발생하는 폭발 규모가 달라집니다."
    ),
    (
        "The wrench helps you tune your pipe networks:\n"
        "- **Toggle**: Click the end of a pipe where it connects \n"
        "  to something else to turn that connection on or off.\n"
        "- **Quick Pick-up**: Shift + Right-click a pipe to pick \n"
        "  it up instantly."
    ): (
        "렌치를 사용해 파이프 네트워크를 조정할 수 있습니다:\n"
        "- **연결 전환**: 파이프가 다른 대상과 연결되는 끝부분을 클릭하면 \n"
        "  해당 연결을 켜거나 끕니다.\n"
        "- **빠른 회수**: Shift + 우클릭하면 파이프를 \n"
        "  즉시 회수합니다."
    ),
    (
        "Uranium is a high-yield energy source found in the deepest reaches of the world.\n"
        "Unlike standard mineral deposits, uranium generates in distinct **uranium veins** that\n"
        "cling to the surfaces of underground caverns."
    ): (
        "우라늄은 세계 깊은 곳에서 발견되는 고효율 에너지원입니다.\n"
        "일반 광상과 달리 우라늄은 지하 동굴 표면에 붙은 뚜렷한 **우라늄 광맥**으로\n"
        "생성됩니다."
    ),
    (
        "There are unsettling rumors of reckless scientists attempting to bombard these "
        "incursion points with speeds that defy known measurement methods,\n"
        "aiming to create singularities of their own. However, none have returned to share their "
        "findings, leaving their fates shrouded in mystery. Ever since,\n"
        "sensors are recording a mysterious tachyon stream from the site of the experiment."
    ): (
        "무모한 과학자들이 알려진 측정법으로는 잴 수 없는 속도로 이 침입 지점을 충돌시켜\n"
        "직접 특이점을 만들려 했다는 불길한 소문이 있습니다. 하지만 결과를 알리러 돌아온 "
        "사람은 아무도 없어 그들의 운명은 수수께끼로 남았습니다. 그 뒤로\n"
        "감지기는 실험 현장에서 정체불명의 타키온 흐름을 기록하고 있습니다."
    ),
    (
        "You can design your reactors as you wish. In general, dual or quad rods are more "
        "fuel-usage efficient, as they generate more total RF per pellet, but are also\n"
        "much harder to cool."
    ): (
        "원자로는 원하는 대로 설계할 수 있습니다. 일반적으로 이중 또는 사중 연료봉은 펠릿당 "
        "총 RF 생산량이 많아 연료 효율이 더 좋지만,\n"
        "냉각하기도 훨씬 어렵습니다."
    ),
}

MANUAL_CANDIDATES.update(
    {
        (
            "- It only accepts energy while actively processing a recipe. When idle, its intake is zero.\n"
            "- It consumes **all stored energy each tick** and converts it into processing progress.\n"
            "- Higher energy input gives more progress per tick, but with **diminishing returns**. "
            "The relationship follows a power curve:"
        ): (
            "- 조합법을 처리하는 동안에만 에너지를 받으며, 대기 중에는 에너지를 받지 않습니다.\n"
            "- 매 틱 **저장된 에너지를 모두 소비**하여 처리 진행도로 바꿉니다.\n"
            "- 에너지 입력량이 많을수록 틱당 진행도가 커지지만 **수확 체감**이 적용됩니다. "
            "그 관계는 다음 거듭제곱 곡선을 따릅니다:"
        ),
        (
            "Use item filters to control which items go where. They are blocks you place next to "
            "the target inventory.\n"
            "They have five input sides and always output to the side they are facing."
        ): (
            "아이템 필터로 아이템의 이동 방향을 제어할 수 있습니다. 대상 인벤토리 옆에 "
            "설치하는 블록입니다.\n"
            "입력 면이 다섯 개이며, 바라보는 면으로 항상 출력합니다."
        ),
        (
            '<Callout variant="info">\n'
            "    Essential for transferring the huge energy output\n"
            "    of a [Nuclear Reactor](@oritech:reactor_controller).\n"
            "</Callout>"
        ): (
            '<Callout variant="info">\n'
            "    [원자로](@oritech:reactor_controller)의 막대한 에너지 출력을\n"
            "    전송하는 데 꼭 필요합니다.\n"
            "</Callout>"
        ),
        (
            "With default configs, the bonuses are additive, not multiplicative. This means that one\n"
            "efficiency addon reduces the energy usage by 20%, two by 40%, etc."
        ): (
            "기본 설정에서는 보너스가 곱연산이 아니라 합연산으로 적용됩니다. 따라서 효율 "
            "애드온 하나는\n"
            "에너지 사용량을 20%, 둘은 40% 줄이는 식입니다."
        ),
        (
            "Its effects depend on the machine it is attached to:\n"
            "- **[Fragment Forge](@oritech:fragment_forge_block)**: Doubles the amount\n"
            "of byproducts produced during ore processing. Only one yield addon can be used here.\n"
            "- **[Block Destroyer](@oritech:destroyer_block)** and\n"
            "**[Enderic Laser](@oritech:laser_arm_block)**: Increases the resource yield\n"
            "when breaking blocks (Fortune effect). Up to 3 yield addons can be installed."
        ): (
            "장착한 기계에 따라 효과가 달라집니다:\n"
            "- **[파편 단조기](@oritech:fragment_forge_block)**: 광석 처리 중 나오는 부산물의\n"
            "양을 두 배로 늘립니다. 여기에는 수확량 애드온을 하나만 장착할 수 있습니다.\n"
            "- **[블록 파괴기](@oritech:destroyer_block)**와\n"
            "**[엔더릭 레이저](@oritech:laser_arm_block)**: 블록을 파괴할 때 자원 생산량을\n"
            "늘립니다(행운 효과). 수확량 애드온을 최대 3개까지 장착할 수 있습니다."
        ),
        (
            "While multiple yield addons can be installed, using three modules\n"
            "reaches the effective maximum for the Fortune effect on mining machines.\n"
            "Adding more than three will not further increase the yield for block\n"
            "breaking."
        ): (
            "수확량 애드온을 여러 개 장착할 수 있지만, 모듈 셋을 사용하면\n"
            "채굴 기계의 행운 효과가 실질적인 최대치에 도달합니다.\n"
            "셋보다 많이 장착해도 블록을 파괴할 때의 생산량은 더\n"
            "늘어나지 않습니다."
        ),
        (
            "The center acts as a hub for **Research Stations**, constructed as multiblock "
            "add-ons. The main unit supports \n"
            "up to **three stations**, allowing for parallel processing.\n"
            "*   Each station requires **3 Machine Cores**.\n"
            "*   A station handles one active research task at a time."
        ): (
            "센터는 멀티블록 애드온으로 건설하는 **연구대**의 중심 장치입니다. 본체에는 \n"
            "**연구대 세 곳**까지 연결해 병렬로 처리할 수 있습니다.\n"
            "*   연구대 하나마다 **기계 핵 3개**가 필요합니다.\n"
            "*   각 연구대는 한 번에 활성 연구 하나를 처리합니다."
        ),
        (
            "It is a good machine for your first workshop because it is cheap, fuel-flexible, "
            "and does not require multiblock setup. \n"
            "One generator is enough for a starter line, but building a second or third is often "
            "the easiest way to support \n"
            "an [Assembler](@oritech:assembler_block), "
            "[Pulverizer](@oritech:pulverizer_block), \n"
            "and [Powered Furnace](@oritech:powered_furnace_block) at the same time."
        ): (
            "저렴하고 여러 연료를 쓸 수 있으며 멀티블록 설치도 필요 없어 첫 작업장에 "
            "적합합니다. \n"
            "초기 생산 라인에는 발전기 한 대면 충분하지만, [조립기](@oritech:assembler_block), "
            "[분쇄기](@oritech:pulverizer_block), \n"
            "[전기 화로](@oritech:powered_furnace_block)를 동시에 돌리려면 두 번째나 세 번째 "
            "발전기를 짓는 것이 가장 간단합니다."
        ),
        (
            "The Industrial Chiller removes heat from high-temperature\n"
            "industrial processes. It is often required for stabilized\n"
            "[nuclear reactor]($reactor/introduction) components or advanced material\n"
            "cooling."
        ): (
            "산업용 냉각기는 고온\n"
            "산업 공정에서 열을 제거합니다. 안정화된\n"
            "[원자로]($reactor/introduction) 부품이나 고급 재료를\n"
            "냉각할 때 자주 필요합니다."
        ),
        (
            "Refinery Chamber Modules are expansion components for the \n"
            "[Industrial Refinery](@oritech:refinery_block). \n"
            "Up to two modules can be stacked on top of a single refinery block \n"
            "to enable additional fluid output channels."
        ): (
            "정유기 반응실 모듈은 \n"
            "[산업용 정유기](@oritech:refinery_block)의 확장 부품입니다. \n"
            "정유기 블록 하나 위에 모듈을 둘까지 쌓아 \n"
            "추가 유체 출력 통로를 활성화할 수 있습니다."
        ),
        (
            "Each module acts as a dedicated tank for the secondary and tertiary \n"
            "fluid products of a refining process. \n"
            "Fluids must be extracted directly from the module blocks rather than \n"
            "the main refinery base. \n"
            "These modules also require their own \n"
            "[machine cores]($multiblocks) to be part of the multiblock\n"
            "assembly."
        ): (
            "각 모듈은 정제 공정의 두 번째와 세 번째 \n"
            "유체 생산물을 위한 전용 탱크입니다. \n"
            "유체는 정유기 본체가 아니라 모듈 블록에서 \n"
            "직접 추출해야 합니다. \n"
            "또한 멀티블록 구조에 포함하려면 각 모듈에 별도의 \n"
            "[기계 핵]($multiblocks)이\n"
            "필요합니다."
        ),
        (
            "Duratium can be made in two ways:\n"
            "- In the [foundry](@oritech:foundry_block) by alloying "
            "[platinum](@oritech:platinum_ingot) and Netherite.\n"
            "- In the [atomic forge](@oritech:atomic_forge_block) using "
            "[platinum](@oritech:platinum_ingot)\n"
            "and [reinforced carbon sheets](@oritech:reinforced_carbon_sheet)."
        ): (
            "듀라티움은 두 가지 방법으로 만들 수 있습니다:\n"
            "- [주조소](@oritech:foundry_block)에서 [백금](@oritech:platinum_ingot)과 "
            "네더라이트를 합금합니다.\n"
            "- [원자 단조기](@oritech:atomic_forge_block)에서 "
            "[백금](@oritech:platinum_ingot)과\n"
            "[강화 탄소판](@oritech:reinforced_carbon_sheet)을 사용합니다."
        ),
        (
            "One generator is fine for a starter workshop, but you will outgrow it quickly. "
            "Do not be afraid to build more than one while you work toward better generators "
            "and automation."
        ): (
            "초기 작업장에는 발전기 한 대면 괜찮지만 금방 전력이 부족해집니다. 더 좋은 "
            "발전기와 자동화를 준비하는 동안 여러 대를 지어도 좋습니다."
        ),
        (
            "Nine small clumps combine into one clump, and those clumps can then be processed "
            "in a [Centrifuge](@oritech:centrifuge_block) into dusts and small dusts for smelting."
        ): (
            "작은 덩어리 아홉 개를 덩어리 하나로 합칠 수 있으며, 그 덩어리는 "
            "[원심 분리기](@oritech:centrifuge_block)에서 제련용 가루와 작은 가루로 "
            "처리할 수 있습니다."
        ),
        (
            "Note that an efficiency bonus of +100% means that only half the energy is needed, "
            "and +200% efficiency only needs a quarter.\n"
            "An efficiency change of -100% would make the machine need twice as much energy."
        ): (
            "효율 보너스가 +100%라면 필요한 에너지가 절반으로 줄고, +200%라면 사분의 일로 "
            "줄어듭니다.\n"
            "효율이 -100%로 바뀌면 기계에 필요한 에너지가 두 배가 됩니다."
        ),
    }
)


MANUAL_CANDIDATES.update(
    {
        """The machine processes trees block by block, including all connected
logs and leaves.
Drops from the leaves, such as saplings or fruit, are
automatically collected into the machine's internal inventory.
It can handle massive trees up to 8,000 blocks in size.""": """기계는 서로 연결된 원목과 나뭇잎을 포함해 나무를 블록 단위로 처리합니다.
묘목이나 열매처럼 나뭇잎에서 떨어지는 아이템은 기계의 내부 인벤토리로 자동 수집됩니다.
최대 8,000블록 크기의 거대한 나무도 처리할 수 있습니다.""",
        (
            'There is a config setting called "Boring Nukes" which makes the device behave '
            "like a block of TNT."
        ): (
            '장치를 TNT 블록처럼 작동하게 하는 "단순 핵무기" 설정(`Boring Nukes`)이 '
            "있습니다."
        ),
        (
            'There is a config setting called "Boring Nukes" which makes the nuke behave like '
            "a block of TNT."
        ): (
            '핵무기를 TNT 블록처럼 작동하게 하는 "단순 핵무기" 설정(`Boring Nukes`)이 '
            "있습니다."
        ),
        """Fluxite can be obtained in two main ways:
- **Amethyst Processing**: Mining an **Amethyst Cluster** with an [Enderic Laser](@oritech:laser_arm_block).
The laser will not destroy the budding amethyst. Instead, it speeds up its growth.
- **Platinum Processing**: It is obtained as a byproduct during the
[platinum](@oritech:platinum_ingot) ore processing chain.""": """플럭사이트는 두 가지 주요 방법으로 얻습니다:
- **자수정 처리**: [엔더릭 레이저](@oritech:laser_arm_block)로 **자수정 군집**을 채굴합니다.
  레이저는 싹 틔우는 자수정을 파괴하지 않고 성장 속도를 높입니다.
- **백금 처리**: [백금](@oritech:platinum_ingot) 광석 처리 계통에서 부산물로 얻습니다.""",
        """This metal is used in several alloys, such as [adamant](@oritech:adamant_ingot)
and [energite](@oritech:energite_ingot), and is used in most machines and machine parts.""": """이 금속은 [아다만트](@oritech:adamant_ingot), [에너자이트](@oritech:energite_ingot) 같은
여러 합금과 대부분의 기계 및 기계 부품에 사용됩니다.""",
        """In the overworld, platinum ore generates deep underground between **Y -60 and Y -20**.
It is also found much more abundantly throughout **The End**.""": """오버월드의 백금 광석은 지하 깊은 **Y -60에서 Y -20** 사이에 생성됩니다.
**엔드** 전역에서는 훨씬 더 풍부하게 발견됩니다.""",
        """In addition to the standard ore blocks, these veins often feature glowing **Uranium Crystals** that
light up the area around them.""": """이 광맥에는 일반 광석 블록뿐 아니라 주변을 밝히는 빛나는 **우라늄 수정**도 자주 생성됩니다.""",
        """Resource nodes are infinite sources of raw materials that can be mined using the
[Bedrock Extractor](@oritech:deep_drill_block). These nodes are found embedded in bedrock
and are indestructible.""": """자원 노드는 [기반암 추출기](@oritech:deep_drill_block)로 채굴할 수 있는 무한한 원재료 공급원입니다.
기반암에 박혀 있으며 파괴할 수 없습니다.""",
        """When certain elements collide with excessive energy, they can rip a hole in space-time, leading to a small dimensional incursion.
The energy required to achieve this is immense, and little is known about these incursions and their triggers.
Researchers have noted that colliding fire charges with a collision energy over 5000 J seems to bring the Nether closer.
Ender pearls with more than 10000 J appear to do the same for the End dimension.""": """특정 원소를 지나치게 큰 에너지로 충돌시키면 시공간이 찢어져 작은 차원 침입이 일어날 수 있습니다.
여기에 필요한 에너지는 막대하며, 차원 침입과 발생 조건은 거의 알려져 있지 않습니다.
연구 결과 화염구를 5000 J가 넘는 충돌 에너지로 부딪치면 네더가 가까워지는 것으로 보입니다.
엔더 진주를 10000 J가 넘는 에너지로 충돌시키면 엔드 차원에도 같은 현상이 나타나는 듯합니다.""",
        """Each fuel rod will consume a fixed amount of fuel from the fuel ports above. Each fuel pellet has a different fuel capacity. Use JEI, REI, or EMI to view the pellet
usage for specific capacity data. Each single rod uses 1 capacity unit, a double rod uses 2, and a quad rod uses 4.""": """각 연료봉은 위쪽 연료 포트에서 일정량의 연료를 소비합니다. 연료 펠릿마다 용량이 다르므로
JEI, REI 또는 EMI에서 펠릿별 용량을 확인하세요. 단일 연료봉은 용량 1, 이중 연료봉은 2, 사중 연료봉은 4를 사용합니다.""",
    }
)


MANUAL_CANDIDATES.update(
    {
        "Energy outputs to the **North**, **South**, and **Down** sides.": (
            "에너지는 **북쪽**, **남쪽**, **아래쪽** 면으로 출력됩니다."
        ),
        (
            "Automation can also be done via AE2 / RS2. Pattern providers work out of the box "
            "with the forge."
        ): (
            "AE2 또는 RS2로도 자동화할 수 있습니다. 패턴 공급기를 단조기에 연결하면 "
            "별도 설정 없이 작동합니다."
        ),
        """The fragment forge is a major step in improving the yield of your ore processing chain.
Fragmenting ore blocks creates **raw ores**, and fragmenting raw ores
creates **ore clumps**.""": """파편 단조기는 광석 처리 계통의 생산량을 높이는 핵심 기계입니다.
광석 블록을 파쇄하면 **가공 전 광석**이 나오고, 가공 전 광석을 다시 파쇄하면
**광석 덩어리**가 만들어집니다.""",
        """The Powered Furnace is a modern replacement for the traditional
stone furnace. It uses RF energy to smelt items at a much higher
speed and efficiency. The powered furnace is twice as fast as a normal furnace.""": """전기 화로는 일반 돌 화로를 대체하는 기계입니다.
RF 에너지로 아이템을 훨씬 빠르고 효율적으로 제련하며,
일반 화로보다 두 배 빠릅니다.""",
        """Simply place your [hand drill](@oritech:hand_drill), [chainsaw](@oritech:chainsaw),
or [exo-suit](@oritech:exo_suit) pieces into the charger's slots.
The machine will draw from its internal RF buffer to restore the item's
charge at a high rate.
It is also the primary way to supply turbofuel to an
[exo-jetpack](@oritech:exo_jetpack).""": """[휴대용 드릴](@oritech:hand_drill), [전기톱](@oritech:chainsaw),
또는 [엑소 슈트](@oritech:exo_suit) 부위를 충전기 슬롯에 넣으세요.
기계가 내부 RF 저장량을 사용해 아이템을 빠르게 충전합니다.
[엑소 제트팩](@oritech:exo_jetpack)에 터보연료를 넣는 기본 방법이기도 합니다.""",
        """Because of its high power requirements, it cannot be powered via
standard cables and must be energized by
[enderic lasers](@oritech:laser_arm_block).""": """필요 전력이 매우 커서 일반 케이블로는 전력을 공급할 수 없습니다.
[엔더릭 레이저](@oritech:laser_arm_block)로 에너지를 보내야 합니다.""",
        """- **Energy Transfer**: When aimed at machines or power storage, the
laser will charge them, ignoring normal input limits. This is required
for the [Atomic Forge](@oritech:atomic_forge_block) and
[Bedrock Extractor](@oritech:deep_drill_block).
- **Fluxite Harvesting**: Directing the laser at amethyst clusters
will transform them into [fluxite](@oritech:fluxite) when mined.
- **Growth Acceleration**: Aiming at a **Budding Amethyst** will
massively accelerate its growth rate without destroying it.
- **Combat**: Equipped with a [hunter addon](@oritech:machine_hunter_addon),
the laser will actively track and attack entities.
Addons like speed apply to combat as well.
- **Exo-Armor Charging**: The laser can wirelessly charge a player's
[Exo Chestplate](@oritech:exo_chestplate) if the player is targeted (only with a hunter addon installed).""": """- **에너지 전송**: 기계나 전력 저장 장치를 겨냥하면 일반 입력 한도를 무시하고 충전합니다.
  [원자 단조기](@oritech:atomic_forge_block)와 [기반암 추출기](@oritech:deep_drill_block)에 반드시 필요합니다.
- **플럭사이트 수확**: 자수정 군집에 레이저를 조준하면 채굴할 때 [플럭사이트](@oritech:fluxite)로 바뀝니다.
- **성장 가속**: **싹 틔우는 자수정**을 조준하면 블록을 파괴하지 않고 성장 속도를 크게 높입니다.
- **전투**: [사냥 애드온](@oritech:machine_hunter_addon)을 장착하면 레이저가 엔티티를 추적해 공격합니다.
  속도 같은 애드온 효과도 전투에 적용됩니다.
- **엑소 방어구 충전**: 사냥 애드온을 장착한 상태에서 플레이어를 조준하면
  [엑소 흉갑](@oritech:exo_chestplate)을 무선으로 충전합니다.""",
        """- **Item Pipes**: Accelerates the extraction rate to one full stack
every tick.
- **Fluid Pipes**: Increases the throughput up to 50 buckets per tick.""": """- **아이템 파이프**: 추출 속도를 매 틱 한 묶음까지 높입니다.
- **유체 파이프**: 처리량을 틱당 최대 50양동이까지 높입니다.""",
        """<Callout variant="info">
    A pipe booster must directly target an **extracting** pipe block
    (the interface where the pipe meets the machine) to have any effect.
</Callout>""": """<Callout variant="info">
    파이프 부스터가 작동하려면 파이프와 기계가 만나는 **추출용** 파이프 블록을 직접 향해야 합니다.
</Callout>""",
        """To use the splicer, you must attach the addons you wish to combine
via extenders. The machine must be full of energy to operate.
Once activated via the interface or by powering the **center** with
redstone, the splicer will consume the physical blocks in the world
and output a single combined block in its inventory.""": """접합기를 사용하려면 결합할 애드온을 확장기에 연결하고 기계의 에너지를 가득 채우세요.
인터페이스에서 작동시키거나 레드스톤으로 **중앙부**에 전력을 공급하면,
월드에 설치된 애드온 블록을 소모하고 결합 블록 하나를 인벤토리로 출력합니다.""",
        """<Callout variant="warning">
    Compaction is irreversible. Only addons that affect machine
    statistics (like speed, efficiency, or yield) can be spliced.
    Addons requiring direct interaction (Steam Boiler, Redstone,
    Inventory Proxy, Hunter) cannot be compacted.
    Additionally, a "Heart of the Machine" cannot be combined with
    other addons—it must be the only installed addon.
</Callout>""": """<Callout variant="warning">
    압축은 되돌릴 수 없습니다. 속도, 효율, 생산량처럼 기계 능력치에 영향을 주는 애드온만 접합할 수 있습니다.
    증기 보일러, 레드스톤, 인벤토리 프록시, 사냥처럼 직접 상호작용이 필요한 애드온은 압축할 수 없습니다.
    또한 "기계의 심장"은 다른 애드온과 결합할 수 없으며 단독으로만 장착해야 합니다.
</Callout>""",
    }
)


MANUAL_CANDIDATES.update(
    {
        """The Power Bank Addon Extender combines the slot expansion of an
extender with a large internal energy reserve.""": """전력 저장고 애드온 확장기는 확장기의 슬롯 증가 기능과
대용량 내부 에너지 저장소를 결합한 장치입니다.""",
        """The Heart of the Machine is a late-game addon that
combines several machine bonuses into a single block.""": """기계의 심장은 여러 기계 보너스를 블록 하나에 결합한
게임 후반부 애드온입니다.""",
        """This addon is powerful, but it comes with one strict limitation:
it only functions if it is the **first and only** addon attached to the
machine.
If any other addons or extenders are present, the Heart of the Machine
will remain inactive. Its main purpose is letting machines with many addons be
more compact.""": """이 애드온은 강력하지만 엄격한 제한이 하나 있습니다.
기계에 **가장 먼저 장착한 유일한** 애드온일 때만 작동합니다.
다른 애드온이나 확장기가 하나라도 있으면 기계의 심장은 비활성 상태로 남습니다.
애드온을 많이 사용하는 기계를 더 작은 공간에 구성하는 것이 주된 용도입니다.""",
        """The Fluid Addon enables fluid processing capabilities for machines
that otherwise only handle items.""": """유체 애드온은 원래 아이템만 처리하는 기계에
유체 처리 기능을 추가합니다.""",
        (
            "Speed addons make the laser deal more damage. Efficiency addons reduce its RF/t "
            "use. Yield addons do **not** increase the loot dropped."
        ): (
            "속도 애드온은 레이저 피해량을 높이고 효율 애드온은 RF/t 소비량을 "
            "줄입니다. 생산량 애드온은 떨어지는 전리품의 양을 **늘리지 않습니다**."
        ),
        """The Inventory Proxy Addon provides a dedicated access point for external
logistics systems to interact with a machine's internal storage.""": """인벤토리 프록시 애드온은 외부 물류 시스템이 기계 내부 저장소와
상호작용할 수 있는 전용 접근 지점을 제공합니다.""",
        """Right-clicking the addon opens a configuration menu where you can set
the following:
- **Input Control**: Allows you to disable the machine by providing a
redstone signal to the addon.
- **Output Measure**: A comparator attached to the addon can output a
signal based on energy storage, inventory contents, or recipe progress.""": """애드온을 우클릭하면 다음 항목을 설정할 수 있는 메뉴가 열립니다:
- **입력 제어**: 애드온에 레드스톤 신호를 보내 기계를 비활성화합니다.
- **출력 측정**: 애드온에 연결한 비교기가 저장된 에너지, 인벤토리 내용물 또는
  조합법 진행도에 따른 신호를 출력합니다.""",
        """When multiple speed addons are used, their speed bonuses are added together.
For example, two speed addons give a total speed bonus of +100%, so the
machine runs at 200% speed and a 100-tick recipe finishes in 50 ticks.
This allows much faster processing at the cost of significantly
higher power requirements.""": """속도 애드온을 여러 개 사용하면 속도 보너스가 합산됩니다.
예를 들어 속도 애드온 두 개는 총 +100%의 속도 보너스를 제공하므로,
기계가 200% 속도로 작동하고 100틱 조합법은 50틱 만에 끝납니다.
처리 속도가 크게 빨라지는 대신 필요한 전력도 많이 늘어납니다.""",
        """The default speed is fairly slow when used as a quarry, so adding some
[speed](@oritech:machine_speed_addon) and [efficiency](@oritech:machine_efficiency_addon) addons is recommended.""": """채석 장비로 사용할 때는 기본 속도가 꽤 느리므로
[속도](@oritech:machine_speed_addon)와 [효율](@oritech:machine_efficiency_addon) 애드온을 장착하는 것이 좋습니다.""",
        """It is required for constructing the following machines:
- **[Block Destroyer](@oritech:destroyer_block)**
- **[Placer Block](@oritech:placer_block)**
- **[Fertilizer Block](@oritech:fertilizer_block)**""": """다음 기계를 구성할 때 필요합니다:
- **[블록 파괴기](@oritech:destroyer_block)**
- **[블록 설치기](@oritech:placer_block)**
- **[비료 살포기](@oritech:fertilizer_block)**""",
        """**Crafting**
- Machine cores are crafted in tiers, with each tier raising the quality ceiling.
- Tier 1 uses planks and a crafting table.
- Tier 2 uses copper or iron with lapis.
- Tier 3 uses [Carbon Fibre Strands](@oritech:carbon_fibre_strands) or [Nickel](@oritech:nickel_ingot) with Redstone.
- Tier 4 uses [Machine Plating Blocks](@oritech:machine_plating_block) and [Enderic Compound](@oritech:enderic_compound).
- Tier 5 uses [Adamant](@oritech:adamant_ingot) and [Advanced Computing Engines](@oritech:advanced_computing_engine).
- Tier 6 uses [Duratium](@oritech:duratium_ingot) and [Dubious Containers](@oritech:dubios_container).
- Tier 7 uses [Prometheum](@oritech:promethium_ingot) and [Superconductors](@oritech:superconductor).""": """**제작**
- 기계 핵은 등급별로 제작하며, 등급이 올라갈수록 품질 상한도 높아집니다.
- 등급 1은 판자와 제작대를 사용합니다.
- 등급 2는 구리 또는 철과 청금석을 사용합니다.
- 등급 3은 [탄소 섬유 가닥](@oritech:carbon_fibre_strands) 또는 [니켈](@oritech:nickel_ingot)과 레드스톤을 사용합니다.
- 등급 4는 [기계 장갑판 블록](@oritech:machine_plating_block)과 [엔더릭 화합물](@oritech:enderic_compound)을 사용합니다.
- 등급 5는 [아다만트](@oritech:adamant_ingot)와 [고급 연산 엔진](@oritech:advanced_computing_engine)을 사용합니다.
- 등급 6은 [듀라티움](@oritech:duratium_ingot)과 [두비오스 용기](@oritech:dubios_container)를 사용합니다.
- 등급 7은 [프로메튬](@oritech:promethium_ingot)과 [초전도체](@oritech:superconductor)를 사용합니다.""",
        """**Usage**
- Multiblock machines highlight their required core positions when right-clicked.
- You can also right-click a machine with a core in hand to place the next valid core automatically, as long as the target spot is unobstructed.
- The resulting machine quality controls extender depth and addon scaling rather than raw crafting speed.""": """**사용법**
- 멀티블록 기계를 우클릭하면 기계 핵이 필요한 위치가 강조 표시됩니다.
- 기계 핵을 손에 들고 기계를 우클릭하면, 대상 위치가 비어 있는 한 다음 기계 핵을 자동으로 배치합니다.
- 최종 기계 품질은 제작 속도가 아니라 확장기 깊이와 애드온 확장량을 결정합니다.""",
    }
)


MANUAL_CANDIDATES.update(
    {
        "All plating blocks come with **slab**, **stair** and **pressure plate** variants.": (
            "모든 장갑판 블록에는 **반 블록**, **계단**, **감압판** 변형이 있습니다."
        ),
        """**Usage**
- This is one of the main progression gates into smarter machines and control blocks.
- It is used in machines and utilities such as the [Centrifuge](@oritech:centrifuge_block),
[Item Filter](@oritech:item_filter_block), [Charger](@oritech:charger_block),
[Target Designator](@oritech:target_designator), and [Reactor Controller](@oritech:reactor_controller).
- It also appears in augmentation recipes and upgrade paths, so it is worth automating once your
assembler line is stable.""": """**사용법**
- 지능형 기계와 제어 블록으로 발전할 때 필요한 핵심 부품 중 하나입니다.
- [원심 분리기](@oritech:centrifuge_block), [아이템 필터](@oritech:item_filter_block),
  [충전기](@oritech:charger_block), [표적 지정기](@oritech:target_designator),
  [원자로 제어기](@oritech:reactor_controller) 같은 기계와 도구에 사용됩니다.
- 증강 조합법과 업그레이드 계통에도 쓰이므로 조립기 생산 라인이 안정되면 자동화하는 것이 좋습니다.""",
        """**Obtaining**
- **Entity Capture**: Give a [Dubios Container](@oritech:dubios_container) to an [Allay](https://minecraft.wiki/w/Allay)
or interact with a [Vex](https://minecraft.wiki/w/Vex) to capture their essence.
- **Centrifuge (Alternative)**: Can be synthesized by processing a [Dubios Container](@oritech:dubios_container)
with [Strange Matter](@oritech:fluid_strange_matter). This method costs much more than capturing entities.""": """**획득**
- **엔티티 포획**: [두비오스 용기](@oritech:dubios_container)를 [알레이](https://minecraft.wiki/w/Allay)에게 주거나
  [벡스](https://minecraft.wiki/w/Vex)와 상호작용해 정수를 포획합니다.
- **원심 분리기(대안)**: [두비오스 용기](@oritech:dubios_container)를
  [기묘한 물질](@oritech:fluid_strange_matter)과 함께 처리해 합성할 수 있습니다. 엔티티를 포획하는 방식보다 비용이 훨씬 큽니다.""",
        """#### Area Mode
In this mode, the pickaxe mines a **3x3 area** of blocks. This is
useful for clearing large tunnels or rooms quickly.""": """#### 영역 모드
곡괭이가 **3x3 영역**을 채굴하므로 큰 터널이나 방을 빠르게 뚫을 때 유용합니다.""",
        (
            "When placing them, make sure the one different output side points where you want "
            "the filtered items to go."
        ): (
            "필터를 설치할 때 모양이 다른 출력 면을 아이템을 보낼 방향으로 향하게 하세요."
        ),
        """Schrödinger's Safe is used to store very large amounts of RF. Right-click the item on an unstable block, such as TNT or a nuclear explosive
(see the in-game tooltip for the full list).
That block is then contained inside the Schrödinger's Safe. The more dangerous the original block is, the higher the safe's energy storage
capacity becomes.
No machine cores are required for this multiblock. It assembles itself.""": """슈뢰딩거의 금고는 매우 많은 RF를 저장합니다. 금고 아이템으로 TNT나 핵폭발물 같은 불안정한 블록을 우클릭하세요
(전체 목록은 게임 내 툴팁에서 확인할 수 있습니다).
해당 블록이 금고 안에 봉인되며, 원래 블록이 위험할수록 에너지 저장 용량이 커집니다.
이 멀티블록에는 기계 핵이 필요하지 않고 구조물이 자동으로 조립됩니다.""",
        """To enable farming use, install the [crop filter addon](@oritech:crop_filter_addon). This causes the block destroyer
to skip all non-finished crops, allowing for automated harvesting.""": """농사에 사용하려면 [작물 필터 애드온](@oritech:crop_filter_addon)을 설치하세요.
블록 파괴기가 아직 다 자라지 않은 작물을 건너뛰므로 수확을 자동화할 수 있습니다.""",
        (
            "This machine is meant for continuous farming rather than burst growth. Water is "
            "the cheap baseline fluid, while mineral slurry is the better option when you want "
            "much higher crop throughput."
        ): (
            "이 기계는 작물을 한꺼번에 키우기보다 농장을 계속 가동하는 데 알맞습니다. "
            "물은 저렴한 기본 유체이고, 작물 처리량을 크게 높이려면 광물 슬러리가 더 좋습니다."
        ),
        """Burns standard furnace fuels (coal, wood, charcoal, etc.) to generate power.
This is your starting generator for early-game power needs.""": """석탄, 목재, 숯 같은 일반 화로 연료를 태워 전력을 생산합니다.
게임 초반 전력을 마련하는 시작용 발전기입니다.""",
        """<Callout variant="info">
    Make sure the panel has a clear view of the sky for best results.
</Callout>""": """<Callout variant="info">
    최대 성능을 내려면 패널 위로 하늘이 가리지 않게 설치하세요.
</Callout>""",
    }
)


MANUAL_CANDIDATES.update(
    {
        """Feed it biomass-derived fuels and other biological materials accepted by your recipe viewer.
This is a multiblock machine that needs [machine cores]($multiblocks) to work.""": """조합법 뷰어에 표시되는 바이오매스 연료나 다른 생물성 재료를 공급하세요.
이 멀티블록 기계가 작동하려면 [기계 핵]($multiblocks)이 필요합니다.""",
        """<Callout variant="info">
    Steam engines will not work if their water storage is completely full. Always ensure that the water can go somewhere.
    With some tanks, comparators and redstone you can build a self-sustaining loop.
</Callout>""": """<Callout variant="info">
    물 저장소가 완전히 차면 증기 기관이 작동하지 않습니다. 물이 빠져나갈 곳을 항상 마련하세요.
    탱크, 비교기와 레드스톤을 조합하면 스스로 유지되는 순환 설비를 만들 수 있습니다.
</Callout>""",
        """This is one of the best first quality-of-life machines to build after your first generator because it removes the need
for manual smelting fuel entirely.""": """첫 발전기를 만든 뒤 초기에 지어 두기 좋은 편의 기계입니다.
수동 제련용 연료가 전혀 필요하지 않게 됩니다.""",
        """When particles collide at high speed, they emit energy-dense tachyons. The higher the collision energy, the more
energy is ejected with the tachyons. They also fly farther, and there are more of them at higher speeds.""": """입자가 고속으로 충돌하면 에너지 밀도가 높은 타키온을 방출합니다.
충돌 에너지가 높을수록 타키온과 함께 더 많은 에너지가 나오며, 타키온의 수와 이동 거리도 늘어납니다.""",
        "A purified semi-metal used in electronics and advanced computing. It is based on sand and quartz.": (
            "모래와 석영으로 만들며 전자 부품과 고급 연산 장치에 사용하는 정제 반금속입니다."
        ),
        """Ore boulders are large clusters of deepslate and ore blocks that generate on the surface.
They show what lies beneath: a [Resource Node](@oritech:resource_node_redstone)
of the same material can always be found directly below at the bedrock layer.""": """광석 바위는 지표에 생성되는 심층암과 광석 블록의 큰 덩어리입니다.
바로 아래 기반암 층에는 항상 같은 재료의 [자원 노드](@oritech:resource_node_redstone)가 있으므로 지하 자원을 알려 주는 표식입니다.""",
        """To find these nodes, look for [Ore Boulders](@oritech:world_ores) on the surface.
They mark a resource node directly below in the bedrock.""": """자원 노드를 찾으려면 지표의 [광석 바위](@oritech:world_ores)를 찾으세요.
광석 바위 바로 아래 기반암에 자원 노드가 있습니다.""",
        """There are unsettling rumors of reckless scientists attempting to bombard these incursion points with speeds that defy known measurement methods,
aiming to create singularities of their own. However, none have returned to share their findings, leaving their fates shrouded in mystery. Ever since,
sensors are recording a mysterious tachyon stream from the site of the experiment.""": """무모한 과학자들이 알려진 측정법으로는 잴 수 없는 속도로 침입 지점을 충돌시켜
직접 특이점을 만들려 했다는 불길한 소문이 있습니다. 실험 결과를 알리러 돌아온 사람이 없어 어떻게 되었는지는 알 수 없습니다. 그 뒤로
감지기는 실험 현장에서 정체불명의 타키온 흐름을 기록하고 있습니다.""",
        """A single heat vent can vent heat based on the hottest neighboring block. At 1000 C, it will vent 14 heat, and at 0 C just 4. Depending on your
goals you probably want to either spread the heat with heat spreaders to many vents, or surround a few absorbers with heat pipes.""": """방열구 하나는 인접한 블록 중 가장 뜨거운 블록을 기준으로 열을 방출합니다. 1000 C에서는 열 14를, 0 C에서는 열 4만 방출합니다.
설계 목적에 따라 열 분산기로 여러 방열구에 열을 퍼뜨리거나, 흡열기 몇 개를 열 파이프로 둘러싸세요.""",
    }
)


MANUAL_CANDIDATES.update(
    {
        """When a mob type is set in the controller, it will visually highlight the needed
cage dimensions. If the cage is incomplete or incorrect, the spawner will
not operate.""": """제어기에 몹 유형을 지정하면 필요한 우리의 크기가 표시됩니다.
우리가 완성되지 않았거나 형태가 잘못되면 생성기가 작동하지 않습니다.""",
        """The Spawner Controller controls the automated mob spawning system. When placed
above a [spawner cage](@oritech:spawner_cage_block), it can be used to spawn specific mob types.""": """생성기 제어기는 자동 몹 생성 시스템을 제어합니다.
[생성기 우리](@oritech:spawner_cage_block) 위에 설치하면 지정한 몹을 생성할 수 있습니다.""",
        """- **Soul Cost**: The number of souls required for one spawn is calculated based on
the mob's health (specifically the square root of its maximum HP).
- **Spawn Range**: The controller attempts to find a valid spawning surface within
a small radius (4 blocks) around itself.
- **Redstone Control**: Applying a redstone signal to the controller will disable
it, stopping all spawning operations.""": """- **영혼 비용**: 한 번 생성할 때 필요한 영혼 수는 몹의 체력, 정확히는 최대 HP의 제곱근을 기준으로 계산합니다.
- **생성 범위**: 제어기 주변의 작은 반경(4블록) 안에서 몹이 생성될 수 있는 표면을 찾습니다.
- **레드스톤 제어**: 제어기에 레드스톤 신호를 보내면 비활성화되어 몹 생성을 멈춥니다.""",
        """The Soul Flower is a plant used for soul
production. Instead of dropping food or materials, it releases
a soul upon harvest.""": """영혼꽃은 영혼을 생산하는 작물입니다.
수확할 때 음식이나 재료 대신 영혼 하나를 방출합니다.""",
        """When the crop reaches its final growth stage and is harvested, it triggers
a death event that releases a soul. This soul can then be collected by any nearby
soul-collecting blocks, such as the [Arcane Catalyst](@oritech:enchantment_catalyst_block)
 or the [Spawner Controller](@oritech:spawner_controller_block).""": """작물이 마지막 성장 단계에 도달한 뒤 수확하면 사망 이벤트가 발생해 영혼을 방출합니다.
방출된 영혼은 근처의 [비전 촉매](@oritech:enchantment_catalyst_block)나
[생성기 제어기](@oritech:spawner_controller_block) 같은 영혼 수집 블록이 모읍니다.""",
        """The hand drill is an unbreakable tool that works like both
a pickaxe and a shovel. It uses energy to mine blocks
quickly.""": """휴대용 드릴은 곡괭이와 삽 역할을 모두 하는 부서지지 않는 도구입니다.
에너지를 사용해 블록을 빠르게 채굴합니다.""",
        """You can use the wrench to **zipline** on the wires between
[power poles](@oritech:power_pole_block). Just right-click
a wire to travel quickly to the other side. """: """렌치로 [전력 전송 전봇대](@oritech:power_pole_block) 사이의 전선을 따라 **집라인**을 탈 수 있습니다.
전선을 우클릭하면 반대편으로 빠르게 이동합니다.""",
        """Default energy capacity is 1M RF. Accepts energy from all sides through a 🟢 *green port* and can only output
through the single 🔴 *red port*.""": """기본 에너지 용량은 1M RF입니다. 🟢 *녹색 포트*를 통해 모든 면에서 에너지를 받고,
🔴 *빨간색 포트* 하나로만 출력합니다.""",
        """The Speed Addon is used to accelerate the processing time of a machine.
With the default additive addon setting, it adds 50% speed, meaning the
machine runs at 150% of its normal speed. A recipe that would normally
take 100 ticks will therefore finish in about 67 ticks.""": """속도 애드온은 기계의 처리 시간을 줄입니다.
기본 합산 설정에서는 속도가 50% 늘어나 기계가 정상 속도의 150%로 작동합니다.
따라서 원래 100틱이 걸리는 조합법은 약 67틱 만에 끝납니다.""",
    }
)


MANUAL_CANDIDATES.update(
    {
        """It can also be used to plant seeds in farmland or place saplings. The machine checks whether the position
is valid for the item before placing it.""": """농지에 씨앗을 심거나 묘목을 놓는 데도 사용할 수 있습니다.
기계는 아이템을 놓기 전에 해당 위치가 알맞은지 확인합니다.""",
        """<Callout variant="warning">
    Energy pipes cannot connect directly to an atomic forge; it needs
    to be powered by an [enderic laser](@oritech:laser_arm_block).
</Callout>""": """<Callout variant="warning">
    에너지 파이프는 원자 단조기에 직접 연결할 수 없습니다.
    [엔더릭 레이저](@oritech:laser_arm_block)로 전력을 공급해야 합니다.
</Callout>""",
        """<Callout variant="danger">
    Even with its "low yield," the blast is significantly more powerful than standard TNT. Ensure you have properly
    secured the area and are at a safe distance before detonation.
</Callout>""": """<Callout variant="danger">
    "저위력"이라 해도 일반 TNT보다 훨씬 강력합니다.
    폭발시키기 전에 주변을 안전하게 막고 충분히 멀리 떨어지세요.
</Callout>""",
        """<Callout variant="danger">
    The resulting crater and blast radius are significant. Ensure you are at a safe distance and have
    properly secured the area before detonation.
</Callout>""": """<Callout variant="danger">
    매우 큰 분화구가 생기고 폭발 반경도 넓습니다.
    폭발시키기 전에 주변을 안전하게 막고 충분히 멀리 떨어지세요.
</Callout>""",
        """A straight [guide ring](@oritech:accelerator_ring) needs to be placed right behind the controller, facing to the side,
with visuals aligning correctly. Any item can be inserted into the controller to be used as a particle.""": """제어기 바로 뒤에 옆을 향한 직선 [유도 고리](@oritech:accelerator_ring)를 놓고 모양이 올바르게 이어지게 하세요.
제어기에 어떤 아이템이든 넣어 입자로 사용할 수 있습니다.""",
        """If you need a more sustainable uranium supply, look
for [Uranium Resource Nodes](@oritech:resource_nodes). These are found near the bedrock
layer and can be harvested indefinitely using a [Bedrock Extractor](@oritech:deep_drill_block).""": """우라늄을 지속해서 공급하려면 [우라늄 자원 노드](@oritech:resource_nodes)를 찾으세요.
기반암 층 근처에서 발견되며 [기반암 추출기](@oritech:deep_drill_block)로 무한히 채굴할 수 있습니다.""",
        """Oil can be collected with buckets or pumped directly using a [Pump](@oritech:pump_block).
Once extracted, it can be stored in tanks and sent to a refinery for processing.""": """석유는 양동이로 담거나 [펌프](@oritech:pump_block)로 직접 퍼 올릴 수 있습니다.
추출한 석유는 탱크에 저장한 뒤 정유기로 보내 처리합니다.""",
        """<Callout variant="info">
    TL;DR: Build a ring from guide rings and motors. Once an inserted particle is up to speed, measured via a particle speed sensor,
    insert a second particle into the same ring to create a collision, with one very fast particle and one basically still.
    If you need higher speeds, make the ring bigger on all sides.
</Callout>""": """<Callout variant="info">
    요약: 유도 고리와 모터로 고리를 만드세요. 입자 속도 감지기로 첫 입자가 충분히 빨라졌는지 확인한 뒤,
    같은 고리에 두 번째 입자를 넣어 매우 빠른 입자와 거의 정지한 입자를 충돌시킵니다.
    더 높은 속도가 필요하면 고리를 모든 방향으로 크게 만드세요.
</Callout>""",
        """When burning fuel, each rod generates neutron pulses. Each pulse creates a specific amount of energy, 64 by default. The more pulses a rod receives,
the more energy it also creates.
Each rod sends and receives one pulse by default. However, if a neighboring component is also a fuel rod,
it will also hit the neighboring component with a pulse. Neutron reflectors can be used to send a pulse back to its origin, acting similarly to a rod type as neighbor.""": """연료를 태우면 연료봉마다 중성자 펄스가 발생합니다. 펄스 하나는 기본적으로 에너지 64를 만들며,
연료봉이 받는 펄스가 많을수록 생산하는 에너지도 늘어납니다.
각 연료봉은 기본적으로 펄스 하나를 보내고 받습니다. 인접한 부품도 연료봉이면 그 부품에도 펄스를 보냅니다.
중성자 반사판은 펄스를 원래 연료봉으로 되돌리며, 인접한 연료봉과 비슷하게 작동합니다.""",
    }
)


MANUAL_CANDIDATES.update(
    {
        """The catalyst automatically collects any souls released within a **16-block radius**.
Souls are released when mobs die nearby or when [Soul Flowers](@oritech:wither_crop_block)
are harvested.""": """촉매는 **16블록 반경** 안에서 방출된 영혼을 자동으로 모읍니다.
근처에서 몹이 죽거나 [영혼꽃](@oritech:wither_crop_block)을 수확하면 영혼이 방출됩니다.""",
        """Hyper enchanting costs much more souls than standard enchanting, scaling
exponentially with the target level.""": """초월 마법 부여는 일반 마법 부여보다 훨씬 많은 영혼을 소비하며,
목표 레벨이 높아질수록 비용이 기하급수적으로 늘어납니다.""",
        """The mob type is determined by the first entity that walks over the controller. This
type can only be changed by breaking and replacing the controller. Once a mob type
is set, the controller will highlight the required size of the spawner cage needed
underneath it. """: """제어기 위를 처음 지나간 엔티티로 생성할 몹 종류가 정해집니다.
종류를 바꾸려면 제어기를 부쉈다가 다시 설치해야 합니다. 몹 종류를 정하면
제어기 아래에 필요한 생성기 우리의 크기가 표시됩니다.""",
        """- **Mining Mode**: Fires a beam that breaks blocks from far
  away. You can also use it to charge [machine cores](@oritech:machine_frame_block)
  or speed up some machines. Like a mini enderic laser in your hand.
- **Combat Mode**: Similar to mining mode, but will not destroy blocks, only damage entities.
  It deals high damage and can turn creepers into
  charged creepers.""": """- **채굴 모드**: 멀리 있는 블록을 부수는 광선을 발사합니다.
  [기계 프레임](@oritech:machine_frame_block)을 충전하거나 일부 기계의 속도를 높일 수도 있어 손에 드는 소형 엔더릭 레이저처럼 작동합니다.
- **전투 모드**: 채굴 모드와 비슷하지만 블록은 파괴하지 않고 엔티티에만 피해를 줍니다.
  피해량이 높으며 크리퍼를 충전된 크리퍼로 바꿀 수 있습니다.""",
        """To increase the amount of energy the safe can store even further, point enderic lasers at it. The lasers do not transfer
energy to the safe. Instead,
they increase its storage capacity. The more lasers are firing at the safe, and the faster they fire, the more energy it can store. This scales
exponentially, so storage can get very large.""": """금고의 에너지 저장 용량을 더 늘리려면 엔더릭 레이저를 조준하세요.
레이저가 금고에 에너지를 전송하는 대신 저장 용량을 높입니다.
조준한 레이저가 많고 발사 속도가 빠를수록 더 많은 에너지를 저장하며, 용량이 기하급수적으로 늘어 매우 커질 수 있습니다.""",
        """<Callout variant="info">
    Burst addons are best for intermittent processing tasks but are
    not recommended for machines that need to run continuously.
</Callout>""": """<Callout variant="info">
    폭발 처리 애드온은 간헐적으로 처리하는 작업에 알맞으며,
    계속 작동해야 하는 기계에는 권장하지 않습니다.
</Callout>""",
        """<Callout variant="info">
    When processing fluids, a [fluid addon](@oritech:machine_fluid_addon)
    must be attached to the centrifuge before it can accept liquids.
</Callout>""": """<Callout variant="info">
    유체를 처리하려면 [유체 애드온](@oritech:machine_fluid_addon)을
    원심 분리기에 장착해야 합니다.
</Callout>""",
        """<Callout variant="danger">
    Always monitor your reactor's heat levels. A sustained overheat will trigger a nuclear meltdown,
    leading to significant structural damage.
</Callout>""": """<Callout variant="danger">
    원자로의 열 수치를 항상 살피세요. 과열이 계속되면 노심 용융이 발생해
    구조물이 심하게 손상됩니다.
</Callout>""",
        """Raw ores must be processed through a [pulverizer](@oritech:pulverizer_block) and [centrifuge](@oritech:centrifuge_block)
to create enriched pellets. These pellets are consumed inside [nuclear reactors]($reactor/introduction) to generate very large amounts of energy.""": """가공 전 광석을 [분쇄기](@oritech:pulverizer_block)와 [원심 분리기](@oritech:centrifuge_block)에서
처리하면 농축 펠릿이 만들어집니다. 이 펠릿은 [원자로]($reactor/introduction)에서 소비되어 매우 많은 에너지를 생산합니다.""",
        """Platinum can also be obtained by processing [nickel](@oritech:nickel_ingot)
in a [fragment forge](@oritech:fragment_forge_block).""": """[니켈](@oritech:nickel_ingot)을 [파편 단조기](@oritech:fragment_forge_block)에서
처리해 백금을 얻을 수도 있습니다.""",
        """You can use active cooling with heat absorbers, or passive cooling with just heat vents. When surrounded by active components on all sides, a single absorber
may absorb up to 16 * 4 = 64 heat per tick, but it does require ice to work. You can create ice from water with the industrial chiller.""": """흡열기를 사용하는 능동 냉각이나 방열구만 사용하는 수동 냉각을 선택할 수 있습니다.
흡열기 하나를 모든 면에서 활성 부품으로 둘러싸면 틱당 최대 16 * 4 = 64의 열을 흡수하지만 작동하려면 얼음이 필요합니다.
산업용 냉각기로 물을 얼음으로 바꿀 수 있습니다.""",
    }
)


MANUAL_CANDIDATES.update(
    {
        """The target designator is a tool used to tell your machines
where to point. You can save a position and then give
it to a machine.""": """표적 지정기는 기계가 바라볼 위치를 지정하는 도구입니다.
위치를 저장한 뒤 기계에 전달할 수 있습니다.""",
        """<Callout variant="warning">
    If both a Silk Touch Addon and a
    [Yield Addon](@oritech:machine_yield_addon) are installed on the
    same machine, Silk Touch will take priority.
</Callout>""": """<Callout variant="warning">
    같은 기계에 섬세한 손길 애드온과 [생산량 애드온](@oritech:machine_yield_addon)을
    함께 장착하면 섬세한 손길 효과가 우선합니다.
</Callout>""",
        """The Pipe Booster is an upgrade for high-throughput logistics
networks.
When placed adjacent to a pipe extraction point and powered with RF,
it massively increases the speed at which items and fluids are
pulled from a connected inventory.""": """파이프 부스터는 처리량이 큰 물류 네트워크용 업그레이드입니다.
파이프 추출 지점 옆에 놓고 RF를 공급하면 연결된 인벤토리에서
아이템과 유체를 꺼내는 속도가 크게 높아집니다.""",
        """Large high-density reactors producing thousands of RF will require multiple energy ports linked to a
[superconductor](@oritech:superconductor) network to prevent power bottlenecks.""": """수천 RF를 생산하는 대형 고밀도 원자로는 전력 병목을 막기 위해
[초전도체](@oritech:superconductor) 네트워크에 연결된 에너지 포트가 여러 개 필요합니다.""",
    }
)


FULL_MDX_TRANSLATIONS = {
    "content/arcane/tainted_refinery.mdx": """---
title: 오염된 정제소
id: oritech:tainted_refinery_block
type: block
---

오염된 정제소는 불안정한 변환 과정을 통해 만들어지는 표준 [정유기](@oritech:refinery_block)의 변형입니다.
정유기와 같은 조합법을 처리하지만 전혀 다른 방식으로 에너지를 사용합니다.
사실상 제한 없이 에너지를 받을 수 있으나 투입량이 늘수록 효율 증가폭은 줄어듭니다. 주변에 알맞은 블록을 배치하면 출력량과 에너지 효율을 크게 높일 수 있습니다.

<center>
<ModAsset location="oritech:area/tainted_refinery_area" width={500} />
</center>

---

## 생성

오염된 정제소는 제작할 수 없습니다. 충전된 [마법 부여 촉매](@oritech:enchantment_catalyst_block)가 근처(6블록 이내)에 있을 때 **정유기를 폭발시키면** 월드에 생성됩니다.

촉매에는 영혼이 하나 이상 들어 있어야 합니다. 폭발이 정유기에 닿으면 촉매가 폭발하고 정유기가 소모되며, 그 자리에 오염된 정제소가 나타납니다.
정유기가 바라보던 방향은 유지됩니다. 멀티블록 구조가 자동으로 설치되므로 기계 핵을 직접 배치할 필요가 없습니다.

<Callout variant="warning">
    폭발 지점 주변을 비워 두세요. 오염된 정제소의 기계 핵 위치가 막혀 있으면 구조물이 일부만 만들어질 수 있습니다.
</Callout>

---

## 에너지 방식

일정한 RF/t를 소비하는 일반 기계와 달리 오염된 정제소는 **에너지 입력량이 계속 달라집니다**.

- 조합법을 처리하는 동안에만 에너지를 받으며, 대기 중에는 에너지를 받지 않습니다.
- 매 틱 **저장된 에너지를 모두 소비**하여 처리 진행도로 바꿉니다.
- 에너지 입력량이 많을수록 틱당 진행도가 커지지만 **한계 효용 체감**이 적용됩니다. 그 관계는 다음 거듭제곱 곡선을 따릅니다:

> 진행도 = 0.2 × 에너지^0.45

따라서 에너지 입력을 두 배로 늘려도 처리 속도가 두 배가 되지는 않습니다. 안정적으로 많은 전력을 공급하면 유리하지만, 입력량이 조금 흔들려도 손해가 크지는 않습니다.
최대 입력은 500M RF/t입니다. 전력 설비가 허용하는 만큼 공급할 수 있으며, 필요하면 휴대용 에너지 저장 장치로 입력량을 제한하세요.

---

## 출력 선택

오염된 정제소는 여러 유체를 만들 수 있는 일반 정유기 조합법을 처리하지만 **한 번에 유체 하나만 출력합니다**.

GUI 버튼으로 원하는 출력 슬롯(슬롯 1, 2 또는 3)을 선택할 수 있습니다. 선택한 슬롯과 다른 유체 출력은 버려집니다.
생산을 시작하기 전에 필요한 출력을 선택하세요.

---

## 환경 보너스

오염된 정제소는 주변(맨해튼 거리 16블록 이내)에서 특정 블록을 찾습니다. 이 블록과 정유기 사이에는 **시야가 확보**되어야 합니다.
중간에 단단한 블록이 있으면 보너스를 받을 수 없습니다.

보너스 블록은 두 범주로 나뉩니다:

### 스컬크 블록 -> 생산량 보너스

스컬크 계열 블록은 아이템과 유체 모두에 적용되는 **출력 배율**을 1x에서 3x까지 높입니다.

사용 가능한 블록은 스컬크, 스컬크 촉매, 스컬크 감지체, 보정된 스컬크 감지체, 스컬크 비명체, 스컬크 정맥, 생성기, 벌레 먹은 돌 변형,
생성기 우리와 생성기 제어기입니다.

### 비전 블록 -> 에너지 효율

비전 계열 블록은 **에너지 배율 계수**를 1x에서 9x까지 높입니다. 이 배율은 한계 효용 체감 곡선을 계산하기 전에 에너지에 적용되므로,
RF당 처리 효율이 크게 높아집니다.

사용 가능한 블록은 마법 부여대, 책장, 조각된 책장, 엔드 막대기, 자수정 블록, 싹 틔우는 자수정, 자수정 봉오리와 군집, 영혼 횃불,
영혼 랜턴, 영혼 모닥불, 우는 흑요석, 리스폰 정박기, 비전 증강 작업대, 마법 부여기와 마법 부여 촉매입니다.

<Callout variant="info">
    JEI, REI 또는 EMI 같은 조합법 뷰어에서 각 범주에 사용할 수 있는 블록을 게임 안에서 확인할 수 있습니다.
</Callout>

### 최적화

효과를 최대로 높이려면 각 범주마다 **블록 16개**를 사용하고, 그 안에 **서로 다른 블록 종류를 최소 4개** 포함하세요.
종류가 4개보다 적으면 불이익을 받지만 블록을 더 배치해 일부 보완할 수 있습니다.

> 계수 = min(1, blockCount / 16 × typeCount / 4)

환경은 멀티블록을 처음 조립할 때 스캔합니다. 정유기를 부쉈다가 다시 조립하면 환경을 다시 스캔합니다.

<Callout variant="info">
    두 보너스 범주의 현재 강도는 정유기 GUI에 막대형 계기로 표시됩니다.
    툴팁에서도 현재 출력 배율과 에너지 배율 값을 확인할 수 있습니다.
</Callout>

---

## 해체

오염된 정제소 멀티블록의 어느 부분이든 부수면 구조물 전체가 해체됩니다.
일반 [정유기](@oritech:refinery_block) 아이템이 떨어집니다. 서바이벌에서는 오염된 정제소 아이템을 얻을 수 없으며, 다시 얻으려면 폭발 의식을 반복해야 합니다.
""",
    "content/equipment/jetpack.mdx": """---
id: oritech:jetpack
title: 제트팩
type: item
related_items: ["oritech:exo_jetpack", "oritech:jetpack_elytra", "oritech:jetpack_exo_elytra"]
custom:
    기본 RF 용량: "100,000"
    엑소 RF 용량: "5,000,000"
---

제트팩은 가슴 슬롯에 장착하는 비행 장비로, 저장된 에너지나 터보연료를 사용합니다. 에너지는 일반 전력 설비로 쉽게 충전할 수 있지만,
내부 터보연료 탱크는 [장비 충전기](@oritech:charger_block)에서 채워야 합니다.

점프 키를 누르고 있으면 일반 제트팩이 작동합니다. 제트팩은 별도로 켜고 끌 수 없으므로 점프 키를 누르는 동안에만 추력을 냅니다.
모든 변형은 에너지만 사용할 때보다 터보연료를 사용할 때 훨씬 빠릅니다. 공중 정지 모드는 없습니다.

### 변형

- **제트팩**: 기본 비행 장비입니다. **100,000 RF**와 연료 **4양동이**를 저장하고, **128 RF/t** 또는 터보연료 **10 mB/t**를 소비합니다. 충전 속도는 **1,024 RF/t**, 기본 속도는 **0.4**입니다.
- **엑소 제트팩**: 고성능 업그레이드입니다. **5,000,000 RF**와 연료 **32양동이**를 저장하고, **256 RF/t** 또는 터보연료 **15 mB/t**를 소비합니다. 충전 속도는 **10,000 RF/t**, 기본 속도는 **1.5**입니다.
- **강화 겉날개**: 기본 제트팩의 활공형 변형입니다. 저장량과 연료 수치는 기본 제트팩과 같지만 이미 활공 중일 때만 추력을 내며, 속도는 **0.6**입니다.
- **강화 엑소 겉날개**: 엑소 제트팩의 고급 활공형 변형입니다. 엑소 제트팩과 저장량, 연료 및 충전 수치가 같고 활공 중일 때만 추력을 내며, 속도는 **1.4**입니다.

### 실제 차이점

엑소 변형은 연료를 더 많이 저장할 뿐 아니라 더 빠르게 상승하고 전진 추력도 강합니다. 착용 중에는 장착한 에너지 아이템도 충전합니다.
따라서 [엑소 제트팩](@oritech:exo_jetpack)과 [강화 엑소 겉날개](@oritech:jetpack_exo_elytra)는
[휴대용 드릴](@oritech:hand_drill), [전기톱](@oritech:chainsaw), [엔더릭 레일건](@oritech:portable_laser) 같은 도구와 함께 쓰기 좋습니다.

겉날개 변형은 일반 제트팩과 작동 방식이 다릅니다. 수직 비행 장비처럼 움직이는 대신 활공 성능을 높이고,
비행 중 위쪽 추력을 반복해서 내므로 폭죽 없이도 계속 날 수 있습니다.

<Callout variant="info">
    평소 이동에는 전기를 사용하고, 최고 속도나 긴 상승 또는 전투 중 빠른 기동이 필요할 때는 터보연료를 사용하세요.
</Callout>
""",
    "content/machines/augmentations/augment_application_block.mdx": """---
title: 사이버네틱 증강 센터
id: oritech:augment_application_block
type: block
custom:
    RF 용량: "500,000,000"
    최대 RF 입력: "50,000,000"
    필요한 코어: "10"
    연구대 슬롯: "3"
---

사이버네틱 증강 센터는 신체에 영구 업그레이드를 연구하고 설치하는 핵심 시설입니다.
증강은 지속 능력치 강화부터 완전히 새로운 능력까지 다양한 효과를 제공합니다.

<Callout variant="warning">
    축하합니다! **육체의 나약함을 깨달은 순간 혐오감을 느꼈다면** 당신은 바로 저희가 찾던 고객입니다.
    강철의 힘과 확실성을 갈망하는 당신을 *Oritech Inc*가 기꺼이 도와드리겠습니다.

    축복받은 기계의 순수성을 받아들이고 나면 되돌릴 수 없다는 점을 기억하세요.
    모든 증강은 영구적이며, 예전 동료들을 "미가공 생체물질"이라고 부르고 싶은 설명하기 어려운 충동이 생길 수도 있습니다.
</Callout>


---

# 연구 및 개발

먼저 조립된 **사이버네틱 증강 센터** 안으로 들어가세요.
연구 인터페이스가 열리며 여기서 프로젝트를 살펴보고 시작할 수 있습니다.
각 증강에는 정해진 에너지와 자원이 필요합니다. 자원은 개인 인벤토리나 인터페이스에서 접근할 수 있는 기계 내부 저장소에서 가져옵니다.

기술 계통도에 표시된 것처럼 상위 등급 업그레이드 중에는 선행 연구가 필요한 것이 많습니다.

센터는 멀티블록 애드온으로 건설하는 **연구대**의 중심 장치입니다. 본체에는
**연구대 세 곳**까지 연결해 병렬로 처리할 수 있습니다.
*   연구대 하나마다 **기계 핵 3개**가 필요합니다.
*   각 연구대는 한 번에 활성 연구 하나를 처리합니다.

<center>
<ModAsset location="oritech:area/cyborg_research_ui" width={700} />
</center>

<Callout variant="info">
    완료한 증강 연구는 해당 기계의 메모리에 저장됩니다. 센터를 부수면 아직 적용하지 않은 연구 진행도와 설계도가 모두 사라집니다.
</Callout>

---

# 적용 및 제어

연구를 마치면 증강을 설치할 수 있습니다. 기술을 플레이어의 신체와 영구 결합하려면 설치할 때 자원을 한 번 지불해야 합니다.

이미 증강을 설치했다면 왼쪽 아래 UI의 **불러오기** 버튼을 눌러 기계에 불러올 수 있습니다.

**증강 관리**:
설치한 증강은 유지 관리나 지속적인 에너지 소비 없이 영구적으로 작동합니다.
다만 **광석 투시**나 **초고속**처럼 방해가 될 수 있는 능력은 원할 때 켜고 끌 수 있습니다.

*   **전환 메뉴**: 증강 단축키(기본 **[G]**)를 길게 눌러 원형 메뉴를 엽니다. 원하는 증강 위에 커서를 놓고 키를 떼면 상태가 바뀝니다.
*   **제거**: 증강은 영구 사용을 전제로 하지만 필요하면 제거할 수 있습니다. 설치에 사용한 자원은 돌려받을 수 없습니다.

<center>
<ModAsset location="oritech:area/cyborg_ui" width={700} />
</center>

---

**모드팩 개발자용 정보**

Oritech 증강은 데이터 기반으로 동작하며 데이터팩에서 폭넓게 설정할 수 있습니다.

*   **속성 증강**: 속도, 도달 거리, 체력 같은 엔티티 속성을 바꿉니다.
*   **효과 증강**: 물약과 비슷한 상태 효과를 적용합니다.
*   **사용자 지정 증강**: 광석 투시 같은 고유 동작을 구현합니다. 데이터팩에서 참조할 수 있지만 실제 동작에는 Java 모드가 필요합니다.

기존 증강을 수정하거나 비활성화할 수 있으며 JSON으로 완전히 새로운 증강도 정의할 수 있습니다.
*   **정의 예시**: [공격 피해 증강(GitHub)](https://github.com/Rearth/Oritech/blob/1.21/fabric/src/main/generated/data/oritech/recipe/augment/attackdamage.json)
*   **텍스처 위치**: `oritech/textures/gui/augment`

사용자 지정 항목을 추가했다면 번역 항목도 함께 넣으세요.
""",
    "docs/addons.mdx": """---
title: 애드온
icon: oritech:item/machine_extender
---

Oritech 기계는 애드온으로 업그레이드합니다. 애드온은 기계 본체나 본체에 연결된 기계 애드온 확장기에 붙이는 블록입니다.
속도 증가, 에너지 효율 향상, 특정 인벤토리 슬롯 접근 등 여러 기능을 제공합니다.

기계마다 애드온을 연결할 수 있는 위치가 정해져 있습니다. "애드온" UI 페이지를 확인하거나 기계에 표시되는 다음 표식을 찾으세요:

<center>
<ModAsset location="oritech:area/addon_marker" width={300} />
</center>

기계를 우클릭하거나 애드온을 설치할 때 연결할 기계를 찾으면 애드온이 활성화됩니다. 활성화된 애드온의 분홍색 부분은 파란색으로 바뀝니다.

<Callout variant="warning">
    연결된 애드온은 파란색, 연결되지 않은 애드온은 분홍색입니다. 분홍색 애드온은 어떤 기계에도 연결되지 않은 상태입니다.
</Callout>

기계 애드온 확장기를 사용하면 애드온 슬롯을 늘릴 수 있습니다. 확장기 자체는 기계 성능에 직접 영향을 주지 않지만,
확장기에 설치한 애드온은 연결된 기계에 장착한 것으로 계산됩니다.

사용할 수 있는 기계 애드온 확장기 층수는 기계 품질에 따라 달라집니다. 기계 핵 품질이 1이면
애드온을 총 1개 사용할 수 있습니다. 기계에 사용할 수 있는 기계 애드온 확장기의 총 개수는 기계 품질과 같습니다.

<center>
<ModAsset location="oritech:area/extenders" width={700} />
</center>
""",
    "docs/multiblocks.mdx": """---
title: 멀티블록
icon: oritech:item/machine_core_6
---

일부 기계는 작동하려면 기계 핵을 추가로 설치해야 합니다. 기계 핵은 기계 본체를 기준으로 정해진 위치에 놓아야 합니다.
필요한 기계 핵 수는 기계 툴팁에 표시됩니다. 기계 핵 하나를 여러 기계가 공유할 수는 없습니다.

<Callout variant="info">
    더 좋은 기계 핵을 사용해도 기계가 빨라지지는 않습니다. 기계 핵은 연결할 수 있는 기계 애드온 확장기의 층수만 늘립니다.
</Callout>

멀티블록을 만들려면 먼저 기계 본체를 설치하세요.

기계를 우클릭하면 기계 핵이 필요한 모든 위치가 몇 초 동안 강조 표시됩니다.
강조된 위치에 기계 핵을 놓으세요. 기계 핵을 손에 든 채 기계를 우클릭하면 다음 위치에 기계 핵을 자동으로 놓을 수도 있습니다.
단, 대상 위치가 비어 있어야 합니다. 장애물이 있으면 막힌 위치만 강조 표시됩니다.

기계 핵마다 품질이 있으며, 더 좋은 기계 핵을 사용하면 기계의 전체 품질이 높아집니다.

기계 UI 왼쪽 위의 기계 아이콘에 커서를 올리면 최종 품질을 확인할 수 있습니다.
기계 품질은 기계 작동에 직접 영향을 주지 않고 장착 가능한 애드온 수를 결정합니다.
애드온을 사용할 계획이 없다면 가장 저렴한 기계 핵을 사용해도 됩니다.
""",
    "content/resources/plastic_sheet.mdx": """---
id: oritech:plastic_sheet
title: 플라스틱
type: item
related_items: ["oritech:plastic_block"]
---

플라스틱은 절연체, 외장재와 여러 중후반부 부품에 사용하는 유용한 고분자 재료입니다.

Oritech에서 플라스틱을 생산하는 주요 경로는 두 가지입니다:
1. **바이오 경로**: [압축 밀](@oritech:packed_wheat)을 물과 함께 [원심 분리기](@oritech:centrifuge_block)에서 처리해 가공 전 바이오폴리머를 얻습니다. 이를 물과 함께 다시 원심 분리하면 플라스틱판이 만들어집니다.
2. **석유 경로**: 원유를 [정유기](@oritech:refinery_block)에서 정제해 나프타를 얻습니다. 나프타와 모래를 원심 분리기에 넣으면 고분자 수지가 나오며, 이를 제련하면 플라스틱판이 됩니다. 설비가 더 많이 필요하지만 플라스틱 생산량도 많습니다.

플라스틱은 상위 등급 기계 부품과 고급 자동화 부품에 사용됩니다.
""",
}


MANUAL_CANDIDATES.update(
    {
        """**Usage**
- **Entity Capture**: Can be used to capture the essence of small magical flying creatures to
create [Unholy Intelligence](@oritech:unholy_intelligence).
- **Processing**: Can be filled with [Strange Matter](@oritech:fluid_strange_matter) in a Centrifuge.
- **Crafting**: Used in high-tier recipes such as the [Superconductor](@oritech:superconductor),
[Ultimate Machine Core progression](@oritech:machine_core_6), [Schrodinger's Safe](@oritech:unstable_container),
and other containment-heavy machines.""": """**사용법**
- **엔티티 포획**: 작은 마법 비행 생물의 정수를 담아
[불경한 지능](@oritech:unholy_intelligence)을 만들 수 있습니다.
- **처리**: 원심 분리기에서 [기묘한 물질](@oritech:fluid_strange_matter)을 채울 수 있습니다.
- **제작**: [초전도체](@oritech:superconductor), [최종 기계 핵 계열](@oritech:machine_core_6),
[슈뢰딩거의 금고](@oritech:unstable_container)처럼 상위 등급의 격리 설비 조합법에 사용됩니다.""",
        """**Usage**
- Used in several cybernetic augments such as Night Vision, Ore Vision, Cloak, and Far Reach.
- Also used in machine recipes that rely on targeting or sensing, including the [Laser Arm](@oritech:laser_arm_block),
[Fuel Generator](@oritech:fuel_generator_block), and yield-focused upgrades.""": """**사용법**
- 야간 투시, 광석 투시, 은신, 원거리 상호작용 같은 사이버네틱 증강에 사용됩니다.
- [레이저 암](@oritech:laser_arm_block), [연료 발전기](@oritech:fuel_generator_block),
생산량 중심 업그레이드처럼 대상 지정이나 감지가 필요한 기계 조합법에도 사용됩니다.""",
        """**Usage**
- Used in late mid-game and end-game blocks such as the [Particle Accelerator](@oritech:accelerator_controller),
[Atomic Forge](@oritech:atomic_forge_block), [Large Solar Panel](@oritech:big_solar_panel_block),
[Bio Generator](@oritech:bio_generator_block), [Superconductor](@oritech:superconductor),
and [Advanced Augmentation Station](@oritech:advanced_augment_station).
- It is also common in high-tier addons and containment recipes, so it often becomes one of the first advanced
components players mass-produce.""": """**사용법**
- [입자 가속기](@oritech:accelerator_controller), [원자 단조기](@oritech:atomic_forge_block),
[대형 태양광 패널](@oritech:big_solar_panel_block), [바이오 발전기](@oritech:bio_generator_block),
[초전도체](@oritech:superconductor), [고급 증강 연구대](@oritech:advanced_augment_station) 같은 중후반부 블록에 사용됩니다.
- 상위 등급 애드온과 격리 조합법에도 널리 쓰이므로 초기에 대량 생산하게 되는 고급 부품 중 하나입니다.""",
        """**Crafting**
- **Centrifuge**: Extracted from [Packed Wheat](@oritech:packed_wheat), [Solid Biofuel](@oritech:solid_biofuel),
or Biomass Blocks using Water.""": """**제작**
- **원심 분리기**: [압축 밀](@oritech:packed_wheat), [고체 바이오연료](@oritech:solid_biofuel),
또는 바이오매스 블록을 물과 함께 처리해 추출합니다.""",
        """<Callout variant="info">
    The old world will burn in the fires of industry. The forests will fall, and nature must make way
    for progress! *Oritech Inc* reminds you that any resemblance to the ramblings of corrupt wizards
    is purely coincidental, and we are definitely not planning to strip-mine Fangorn Forest.
</Callout>""": """<Callout variant="info">
    낡은 세계는 산업의 불길에 타고 숲은 쓰러질 것입니다. 진보를 위해 자연이 길을 내야 합니다!
    타락한 마법사의 망언과 비슷하게 들린다면 순전히 우연이며, *Oritech Inc*는 팡고른 숲을
    노천 채굴할 계획이 전혀 없음을 알려드립니다.
</Callout>""",
        """If you want to automate wood collection, use a
[treefeller](@oritech:treefeller_block) machine.""": """목재 수집을 자동화하려면
[벌목기](@oritech:treefeller_block)를 사용하세요.""",
        """- **Exo Helmet**: Gives you **Night Vision** while you wear it.
- **Exo Chestplate**: Charges energy-powered tools in your inventory
  automatically (like the [chainsaw](@oritech:chainsaw) or
  [hand drill](@oritech:hand_drill)). There is also an exo-jetpack variant.
- **Exo Leggings**: Makes you **run faster**.
- **Exo Boots**: No more **Fall Damage** and increases how far
  you can fall safely.""": """- **엑소 헬멧**: 착용 중 **야간 투시** 효과를 제공합니다.
- **엑소 흉갑**: 인벤토리의 [전기톱](@oritech:chainsaw)이나
  [휴대용 드릴](@oritech:hand_drill) 같은 에너지 도구를 자동으로 충전합니다. 엑소 제트팩 변형도 있습니다.
- **엑소 레깅스**: **달리기 속도**를 높입니다.
- **엑소 부츠**: **낙하 피해**를 없애고 안전하게 떨어질 수 있는 높이를 늘립니다.""",
        """- **Pickaxe & Shovel**: The drill automatically works on
  any block that normally needs a pickaxe or a shovel.
- **Harvesting**: It is also very good at harvesting
  **Amethyst Clusters** and other cluster-based blocks.
- **Enchanting**: It supports standard enchantments like
  Efficiency, Fortune, and Silk Touch. Unbreaking
  makes it use less energy.""": """- **곡괭이 및 삽**: 일반적으로 곡괭이나 삽이 필요한 블록을 자동으로 채굴합니다.
- **수확**: **자수정 군집**과 다른 군집형 블록을 수확하는 데도 매우 효과적입니다.
- **마법 부여**: 효율, 행운, 섬세한 손길 같은 일반 마법을 지원합니다.
  내구성 마법은 에너지 소비량을 줄입니다.""",
        """- [Laser Arm](@oritech:laser_arm_block): Tells the laser
  where to fire.
- [Drone Port](@oritech:drone_port_block): Sets the destination
  for drones.
- [Power Pole](@oritech:power_pole_block): Connects power
  poles to each other.""": """- [레이저 암](@oritech:laser_arm_block): 레이저가 발사할 위치를 지정합니다.
- [드론 포트](@oritech:drone_port_block): 드론의 목적지를 지정합니다.
- [전력 전송 전봇대](@oritech:power_pole_block): 전봇대를 서로 연결합니다.""",
        "Energy can be inserted anywhere, but is only output at the 🔴 **red output marker**.": (
            "에너지는 어느 면으로든 입력할 수 있지만 🔴 **빨간색 출력 표식**에서만 "
            "출력됩니다."
        ),
    }
)


FULL_MDX_TRANSLATIONS.update(
    {
        "content/machines/processing/refinery_block.mdx": """---
title: 정유기
id: oritech:refinery_block
type: block
custom:
    RF 용량: "50,000"
    RF/t: "64"
    유체 용량(본체): "64양동이"
    유체 용량(모듈): "각각 4양동이"
    필요한 기계 핵: "9"

---
정유기는 아이템과 유체를 함께 처리합니다. 아이템 입력 하나, 유체 입력 하나와 여러 출력 칸이 있습니다.

<Callout variant="info">
    아침에 맡는 분별 증류 냄새만큼 달콤한 것도 없죠! 원유 [석유](@oritech:still_oil_bucket)를
    유용한 산업 제품으로 바꾸는 것보다 "진보"를 잘 보여 주는 일이 또 있을까요?
    환경 문제는 미래 세대가 해결할 일입니다!
</Callout>

<center>
<ModAsset location="oritech:area/refinery" width={1000} />
</center>

---

**분별 증류**

정유기에는 **아이템 입력 1개**, **유체 입력 1개**, **아이템 출력 1개**와
**유체 출력 3개**가 있습니다.

처음에는 첫 번째 유체 출력만 활성화됩니다.
두 번째와 세 번째 유체 출력을 사용하려면 본체 위에
[정유기 반응실 모듈](@oritech:refinery_module_block)을 설치해야 합니다.
2번째와 3번째 슬롯의 유체는 해당 모듈에서 직접 추출하세요.

**생산량 방식**

조합법의 유체 출력 수가 사용 가능한 슬롯이나 모듈보다 많으면 남는 용량을 다음처럼 활용합니다:
- 모듈이 없으면 첫 번째 유체 출력량이 두 배가 됩니다.
- 모듈이 하나만 있어 유체 출력 2개가 활성화되면, 해당하는 경우 두 번째 유체 출력량이 두 배가 됩니다.

<Callout variant="info">
    정유기에는 애드온 슬롯이 없어 직접 업그레이드하거나 속도를 높일 수 없습니다. 더 빠르고 다양한 기능이 필요하다면
    [오염된 정제소](@oritech:tainted_refinery_block)를 확인하세요.
</Callout>
""",
        "content/machines/powergen/fuel_generator_block.mdx": """---
id: oritech:fuel_generator_block
type: block
title: 연료 발전기
custom:
    RF 용량: "250,000"
    RF/t: "256"

---
석유나 디젤 같은 액체 연료를 태워 많은 에너지를 생산합니다. 기본 발전량은 256 RF/t입니다.

<Callout variant="warning">
    에너지는 기계 앞면의 노란색 연결 지점 2곳으로만 출력됩니다.

</Callout>

파이프나 양동이로 액체 연료를 공급할 수 있습니다.
이 멀티블록에는 [기계 핵]($multiblocks)이 필요합니다. 유체가 든 아이템을 들고 기계를 클릭해 연료를 넣거나 뺄 수도 있습니다.

가공 전 석유로도 작동하지만 정제 연료를 사용해야 효율이 크게 높아집니다. 이미 정유기가 있다면 정제 연료를 처음 사용하기에 가장 알맞은 기계입니다.

<Callout variant="info">
    정제 연료는 가공 전 자원보다 에너지 밀도가 훨씬 높습니다.
</Callout>
""",
        "content/equipment/chainsaw.mdx": """---
id: oritech:chainsaw
title: 전기톱
type: item
custom:
    RF 용량: "10,000"
    사용당 RF: "10"
    충전 속도: "512 RF/t"
---

전기톱은 나무를 빠르게 수확하는 도구입니다. 부서지지 않는 도끼처럼 작동하지만 에너지가 필요하며,
검으로도 사용할 수 있습니다.

<Callout variant="info">
    낡은 세계는 산업의 불길에 타고 숲은 쓰러질 것입니다. 진보를 위해 자연이 길을 내야 합니다!
    타락한 마법사의 망언과 비슷하게 들린다면 순전히 우연이며, *Oritech Inc*는 팡고른 숲을
    노천 채굴할 계획이 전혀 없음을 알려드립니다.
</Callout>

### 사용법

[충전기](@oritech:charger_block)에서 충전하거나 [엑소 흉갑](@oritech:exo_chestplate)을 착용하세요.
에너지가 떨어지면 작동 속도가 매우 느려집니다.

#### 나무 벌목
원목을 채굴할 때 **Shift**를 누르고 있으면 나무 전체를 한 번에 벱니다.
제거한 블록마다 에너지를 추가로 소비합니다.

#### 전투
전기톱은 검으로 취급되어 몹과 싸울 때 사용할 수 있습니다.
**거미줄**도 매우 빠르게 제거합니다.

<Callout variant="warning">
    전기톱은 부서지지 않지만 에너지가 있어야 최대 속도로 작동합니다.
</Callout>

### 마법 부여

효율, 날카로움, 섬세한 손길, 행운 같은 일반 도끼 및 검 마법을 사용할 수 있습니다.
**내구성** 마법은 작업마다 소비하는 에너지를 줄입니다.

더 좋은 마법을 부여하려면 [안정화 마법 부여기](@oritech:enchanter_block)를 확인하세요.

목재 수집을 자동화하려면 [벌목기](@oritech:treefeller_block)를 사용하세요.
""",
    }
)

FULL_MDX_TRANSLATIONS.update(
    {
        "content/logistics/power_pole_block.mdx": """---
id: oritech:power_pole_block
type: block
title: 전력 전봇대
custom:
    RF 용량: "1,000,000"
    범위: "50-1,000블록"
---
전력 전봇대는 먼 거리까지 전력을 전송합니다.
보통 높은 곳에 설치하며 다른 전력 전봇대하고만 연결할 수 있습니다.
<center>
<ModAsset location="oritech:area/power_pole" width={512} />
</center>

두 전봇대를 연결하려면 [표적 지정기](@oritech:target_designator)를 들고 첫 번째 전봇대를 Shift + 우클릭한 다음,
두 번째 전봇대도 Shift + 우클릭하세요. 전봇대 하나를 여러 전봇대에 연결할 수 있습니다.
서로 연결된 전봇대는 에너지를 공유하므로 대규모 전력망을 만들 수 있습니다.

연결된 전력망의 어느 전봇대에서든 에너지를 넣거나 꺼낼 수 있습니다.
녹색 포트로 에너지를 입력하고 빨간색 포트에서 출력합니다.
전력망 전체의 최대 전송률은 1M RF/t입니다.

<Callout variant="info">
    전력 전봇대는 장거리 전송용이며 연결 거리는 50블록 이상, 1000블록 이하여야 합니다.
</Callout>

[파이프 렌치](@oritech:wrench)를 들고 케이블을 클릭하면 전봇대 케이블을 타고 이동할 수 있습니다.

<center>
<ModAsset location="oritech:area/cable_ziplining" width={800} />
</center>
""",
        "content/machines/utility/pump_block.mdx": """---
title: 펌프
id: oritech:pump_block
type: block
---

펌프는 월드에서 대량의 유체를 끌어올리는 기계입니다.
설치하면 아래쪽으로 흡입관을 내려 유체 원천을 찾고,
서로 이어진 유체 전체를 탐색해 배수하기 시작합니다.

<center>
<ModAsset location="oritech:area/pump" width={512} />
</center>

---

**대규모 유체 배수**

펌프는 최대 100,000블록 규모의 유체 저장소를 배수할 수 있습니다.
그보다 큰 저장소는 전부 배수하지 못할 수 있습니다.
유체를 초당 4양동이 속도로 내부 저장소에 옮기며,
제거한 유체 블록마다 512 RF를 소비합니다.
매우 큰 유체 저장소는 탐색을 시작하는 데 몇 초가 걸릴 수 있습니다.
""",
        "content/machines/processing/centrifuge_block.mdx": """---
title: 원심 분리기
id: oritech:centrifuge_block
type: block
custom:
    RF 용량: "10,000"
    RF/t: "64"
    유체 용량: "8양동이(유체 애드온)"
    필요한 코어: "1"
    애드온 슬롯: "1"
---
원심 분리기는 빠른 회전으로 아이템을 분리하거나 변환합니다.
[파편 단조기](@oritech:fragment_forge_block)에서 나온 광석 덩어리에서 광석 가루를 추출하고,
석탄 가루를 탄소 섬유 가닥으로 만들거나 여러 유체를 처리할 수 있습니다.

광석 정제와 부품 생산, 이후의 석유·플라스틱 공정을 이어 주는 Oritech의 핵심 진행 기계입니다.

<Callout variant="info">
    유체를 처리하려면 [유체 애드온](@oritech:machine_fluid_addon)을 원심 분리기에 부착해야 합니다.
</Callout>

---

**유체 분리**

유체는 애드온이 아니라 **원심 분리기 본체**에서 직접 넣고 꺼냅니다.
애드온은 유체 처리 기능을 활성화할 때만 필요합니다.
대표적으로 원유를 여러 연료로 정제하거나 밀을 플라스틱 시트로 가공할 수 있습니다.

유체 조합법이 시작되지 않으면 애드온을 설치한 뒤 기계 화면을 열어 상태를 갱신하세요.
""",
        "docs/getting_started/gather_resources.mdx": """---
title: 자원 수집
icon: minecraft:diamond_pickaxe
---

처음 만드는 Oritech 기계는 단순하지만 기본 광석이 꽤 필요합니다.

동굴에 드러난 광석이나 지상의 광석 바위를 찾고 채굴 경로를 확보하세요.
초반에 가장 중요한 재료는 **구리, 철, 석탄, 니켈**입니다.

니켈은 여러 초반 기계와 합금 조합법에 들어가므로 특히 중요합니다.
레드스톤과 금, 다이아몬드도 곧 필요하니 채굴할 때 함께 모아 두세요.

자수정 정동석도 찾아 두세요. 나중에 플럭사이트를 생산하려면 싹 틔우는 자수정이 필요합니다.

<center>
<ModAsset location="oritech:area/ore_boulder" width={512} />
</center>
""",
        "docs/getting_started/alloys.mdx": """---
title: 강철과 기타 합금 만들기
icon: oritech:item/steel_ingot
---

**강철, 일렉트럼, 아다만트** 같은 초반 합금은 손으로 만들 수 있지만 재료 효율이 낮습니다.

<CraftingRecipe
    slots={[
        'iron_ingot',
        'iron_ingot',
        '',
        'coal',
        'coal',
        '',
        '',
        '',
        ''
    ]}
    result="oritech:steel_ingot"
    count={1}
/>

첫 기계를 만들 때는 손으로 합금을 제작해도 됩니다.
가능한 한 빨리 [분쇄기](@oritech:pulverizer_block)와 [주조소](@oritech:foundry_block)를 이용하는 합금 생산 설비로 전환하세요.

이 전환은 Oritech 초반의 재료 효율을 크게 높이며,
이후 바이오스틸, 에너자이트, 듀라티움 같은 합금을 생산할 기반도 마련해 줍니다.
""",
        "docs/reactor/components.mdx": """---
title: 원자로 구성 요소
icon: oritech:area/reactor
---

원자로는 다음 구성 요소로 만듭니다.

- 원자로 제어기: 원자로의 중심 블록입니다. 벽에 하나만 설치하며, 상호 작용하면 원자로를 조립하거나 갱신합니다.
GUI에는 원자로의 현재 상태와 구성 요소 온도, 통계가 표시됩니다. 내부는 첫 번째 층만 표시됩니다.

- 원자로 벽: 매우 튼튼하고 폭발에 강한 외벽 블록입니다. 원자로 틀 전체를 감싸야 합니다.

- 원자로 연료봉: 우라늄 또는 플루토늄 펠릿을 공급하는 내부 구성 요소입니다. 연료를 넣으려면 연료봉 묶음마다 위쪽에 연료 포트가 필요합니다.
단일·이중·사중 연료봉이 있으며, 봉 수에 따라 열과 에너지 생성량이 달라집니다.

- 원자로 열 파이프: 인접한 연료봉에서 열을 흡수해 인접한 열 배출구로 분산합니다. 2개 구성 요소 사이의 최대 열 전달량은 온도 차이에 따라 정해집니다.
  > temperatureDiff / 4 + 10

- 원자로 중성자 반사판: 인접한 연료봉의 중성자를 반사해 효율을 높입니다.

- 원자로 열 배출구: 인접한 구성 요소 중 가장 뜨거운 곳에서 열을 제거합니다. 구성 요소가 뜨거울수록 더 많은 열을 제거합니다.
  > neighborHeat / 100 + 4

- 원자로 열 흡수기: 인접한 모든 구성 요소에서 일정량의 열을 제거합니다. 냉각할 구성 요소가 여러 면에 닿을수록 효율적입니다.
흡수기 묶음 위의 냉각재 포트에 얼음, 푸른얼음 또는 꽁꽁 언 얼음을 계속 공급해야 합니다.
냉각재 소비량은 고정되어 있어 냉각 면이 늘어나도 증가하지 않으며, 매 틱 각 인접 구성 요소에서 열 16을 제거합니다.

- 원자로 에너지 포트: 원자로에서 만든 에너지를 출력합니다. 포트 하나당 최대 25,000 RF/t를 출력할 수 있습니다.

- 원자로 연료 포트: 아래에 연료봉이 오도록 원자로 외부 천장에 설치합니다. 이곳으로 연료 펠릿을 넣습니다.

- 원자로 냉각재 흡수기 포트: 아래에 열 흡수기가 오도록 원자로 외부 천장에 설치합니다.
얼음, 푸른얼음 또는 꽁꽁 언 얼음을 냉각재로 넣습니다.

- 원자로 레드스톤 포트: 레드스톤 신호를 받으면 새 연료 공급을 중단합니다. 이미 연소 중인 펠릿은 모두 소모된 뒤에야 원자로가 완전히 멈춥니다.
비교기를 연결하면 에너지, 활성 연료봉 수, 온도의 3가지 모드 중 하나를 출력하며, 포트를 우클릭해 출력 모드를 바꿀 수 있습니다.

## 연료봉 작동 방식

각 연료봉은 위쪽 연료 포트에서 정해진 양의 연료를 소비합니다. 펠릿마다 연료 용량이 다르므로 JEI, REI 또는 EMI에서 확인하세요.
단일 연료봉은 용량 1, 이중 연료봉은 2, 사중 연료봉은 4를 사용합니다.

연료가 타는 동안 각 연료봉은 중성자 펄스를 만듭니다. 펄스 하나는 기본적으로 에너지 64를 생성하며,
연료봉이 받는 펄스가 많을수록 더 많은 에너지를 만듭니다.
각 연료봉은 기본적으로 펄스 하나를 보내고 받습니다. 인접한 구성 요소도 연료봉이면 그 연료봉에도 펄스를 보냅니다.
중성자 반사판은 펄스를 원래 연료봉으로 되돌려 인접한 연료봉과 비슷하게 작동합니다.

이중·사중 연료봉은 같은 블록 안의 다른 봉에도 펄스를 보내고, 인접한 구성 요소에는 각각 2개 또는 4개의 펄스를 보냅니다.

내부 펄스는 단일 연료봉이 1개, 이중 연료봉이 4개, 사중 연료봉이 12개 생성합니다.

생성되는 열은 연료봉이 받는 내부·외부 펄스의 합으로 계산합니다.
> pulses / 2 * pulses + 4
""",
    }
)


FULL_MDX_TRANSLATIONS.update(
    {
        "docs/getting_started/lasers.mdx": """---
title: 레이저와 플럭사이트
icon: oritech:item/laser_arm_block
---

Oritech의 강력한 기계로 발전하려면 **플럭사이트**가 필요합니다.

일반적으로 자수정 군집에 [표적 지정기](@oritech:target_designator)로 [엔더릭 레이저](@oritech:laser_arm_block)를 조준해 얻습니다.

레이저 설비는 플럭사이트를 얻는 데만 쓰이지 않습니다. 이후에는 [원자 단조기](@oritech:atomic_forge_block) 같은 기계에 전력을 공급하고,
무선으로 에너지를 전송하며, 모드의 최상위 처리 설비를 가동하는 데도 사용합니다.

레이저 설비가 작동하기 시작하면 Oritech 기계가 서로 떨어진 단일 블록이 아니라 하나의 시스템으로 연결되는 단계에 들어섭니다.

<center>
<ModAsset location="oritech:area/fluxite_mining" width={512} />
</center>
""",
        "content/machines/utility/laser_arm_block.mdx": """---
title: 엔더릭 레이저
id: oritech:laser_arm_block
type: block
custom:
    RF 용량: "20,000"
    RF/t: "128"
    범위: "128블록"
    필요한 기계 핵: "1"
    애드온 슬롯: "1"
---
엔더릭 레이저는 많은 에너지를 소비해 정해진 방향으로 강력한 광선을 발사합니다.
주로 장거리 고속 채굴이나 장거리 전력 전송에 사용합니다.

<center>
<ModAsset location="oritech:area/fluxite_mining" width={512} />
</center>

---

**제어 및 조준**

[표적 지정기](@oritech:target_designator)를 레이저 블록에 사용해 발사 방향을 정합니다.
최대 범위는 128블록이며 장애물에 막히거나 레드스톤 신호로 비활성화될 때까지 계속 발사합니다.
특정 블록이 아니라 방향만 지정하므로 해당 방향의 모든 블록을 파괴하려 합니다.

레이저로 채굴한 아이템은 내부 인벤토리로 자동 수집됩니다.

<Callout variant="warning">
    내부 인벤토리에 들어가지 못한 아이템은 파괴됩니다.
    [아이템 파이프](@oritech:item_pipe)로 자원을 계속 꺼내세요.
    레이저는 유리를 통과하지만 경로에 있는 거의 모든 것을 파괴하므로 주의하세요.
</Callout>

---

**고급 상호작용**

- **에너지 전송**: 기계나 전력 저장 장치를 겨냥하면 일반 입력 한도를 무시하고 충전합니다.
  [원자 단조기](@oritech:atomic_forge_block)와 [기반암 추출기](@oritech:deep_drill_block)에 반드시 필요합니다.
- **플럭사이트 수확**: 자수정 군집에 레이저를 조준하면 채굴할 때 [플럭사이트](@oritech:fluxite)로 바뀝니다.
- **성장 가속**: **싹 틔우는 자수정**을 조준하면 블록을 파괴하지 않고 성장 속도를 크게 높입니다.
- **전투**: [사냥 애드온](@oritech:machine_hunter_addon)을 장착하면 레이저가 엔티티를 추적해 공격합니다.
  속도 같은 애드온 효과도 전투에 적용됩니다.
- **엑소 방어구 충전**: 사냥 애드온을 장착한 상태에서 플레이어를 조준하면
  [엑소 흉갑](@oritech:exo_chestplate)을 무선으로 충전합니다.

**애드온 및 업그레이드**

레이저 아래쪽에는 애드온 슬롯 하나가 있으며, 대규모 작업에서 작동 방식을 크게 바꿀 수 있습니다.

- **채석 애드온**: 레이저를 대규모 굴착 장비로 바꿉니다. 광선 폭이 넓어져 한 줄이 아니라 큰 터널이나 구역을 효율적으로 제거합니다.
- **생산량 애드온**: 행운처럼 작동해 채굴한 블록의 자원 생산량을 높입니다.
- **속도 애드온**: 에너지 소비량이 늘어나는 대신 채굴 속도 또는 에너지 전송량을 높입니다.
- **효율 애드온**: 채굴하거나 블록 성장을 가속할 때 소비하는 에너지를 줄입니다.
- **사냥 애드온**: 레이저를 전투 모드로 바꿉니다. [표적 지정기](@oritech:target_designator)를 레이저에 사용해
  조준 대상(몬스터, 동물, 상인)을 순환할 수 있습니다.
""",
    }
)


FULL_MDX_TRANSLATIONS.update(
    {
        "content/equipment/electric_mace.mdx": """---
id: oritech:electric_mace
title: 전기 철퇴
type: item
custom:
    RF 용량: "500,000"
    사용당 RF: "2,048"
    충전 속도: "50,000 RF/t"
---
전기 철퇴는 에너지를 사용해 추가 피해를 주는 무거운 무기입니다.
일반 철퇴의 작동 방식에 번개 공격을 더했습니다.

### 전투

공격 속도는 느리지만 대상을 맞히기 전까지 떨어진 거리가 길수록 더 큰 피해를 줍니다.
공격에 성공하면 낙하 거리가 초기화됩니다.

#### 번개
적을 맞히면 다음 2초 동안 번개가 여러 번 떨어집니다.
대상에게 큰 추가 피해를 주지만 에너지를 소비하며 재사용 대기시간이 조금 있습니다.

#### 사거리
전기 철퇴는 일반 도구보다 사거리가 길어 낙하 중에도 몹을 맞히기 쉽습니다.

### 에너지

철퇴는 부서지지 않지만 번개 공격에는 에너지가 필요합니다.
[충전기](@oritech:charger_block)에서 충전하거나 [엑소 흉갑](@oritech:exo_chestplate)을 사용하세요.

장착하면 **안전 낙하 거리**가 10블록 늘어나는 지속 효과도 받습니다.

### 업그레이드

일반 철퇴 마법과 함께 에너지 소비량을 줄이는 **내구성** 마법도 부여할 수 있습니다.

[제트팩](@oritech:jetpack)이나 [엑소 부츠](@oritech:exo_chestplate)와 함께 사용하면
전투에서 훨씬 다루기 쉽습니다.
""",
        "content/components/advanced_battery.mdx": """---
title: 고급 배터리
id: oritech:advanced_battery
type: item
---

고급 기계와 장비에 사용하는 대용량 에너지 저장 부품입니다.

**제작**
<CraftingRecipe
    slots={[
        '', 'oritech:electrum_ingot', '',
        'oritech:steel_ingot', 'oritech:energite_ingot', 'oritech:steel_ingot',
        'oritech:steel_ingot', 'oritech:energite_ingot', 'oritech:steel_ingot'
    ]}
    result="oritech:advanced_battery"
    count={1}
/>

- **원심 분리기**: [두비오스 용기](@oritech:dubios_container)를 [황산](@oritech:fluid_sulfuric_acid)과 함께 처리하면 대량 생산할 수 있습니다.

**사용법**
- [전기 철퇴](@oritech:electric_mace), [엔더릭 레일건](@oritech:portable_laser), 제트 보조 방어구와 비행 장비에 사용합니다.
  [대형 저장고](@oritech:large_storage_block), [대형 태양광 패널](@oritech:big_solar_panel_block) 같은 저장 및 발전 블록에도 들어갑니다.
- 황산 생산을 자동화한 뒤에는 [두비오스 용기](@oritech:dubios_container)에 황산을 채워 원심 분리하는 방식이 생산량을 늘리기에 가장 실용적입니다.
""",
        "content/machines/processing/cooler_block.mdx": """---
title: 산업용 냉각기
id: oritech:cooler_block
type: block
custom:
    RF 용량: "50,000"
    RF/t: "32"
    유체 용량: "4양동이"
    필요한 기계 핵: "1"
    애드온 슬롯: "1"
---
산업용 냉각기는 고온 산업 공정에서 열을 제거합니다.
안정화된 [원자로]($reactor/introduction) 부품이나 고급 재료를 냉각할 때 자주 필요합니다.

물을 받아 얼음 블록으로 출력합니다.

가장 중요한 용도는 흡열기 기반 냉각을 사용하는 원자로용 냉각재 생산입니다.
원자력 발전 규모를 키우기 시작하면 활용도가 크게 높아집니다.

---
**환경 효율**

냉각기 성능은 주변 환경의 영향을 크게 받습니다.
추운 생물군계에 설치하면 두 배 빠르게 작동하고 에너지 효율도 크게 높아집니다.
고정된 짧은 목록이 아니라 일반적인 추운 생물군계 태그를 사용하므로 눈이 내리거나 얼어붙은 생물군계 대부분이 해당합니다.
""",
    }
)


FULL_MDX_TRANSLATIONS.update(
    {
        "docs/reactor/introduction.mdx": """---
title: 소개
icon: oritech:area/reactor
---

<Callout variant="warning">
    원자의 힘을 다루는 일이 위험한 만큼 짜릿한 원자로의 세계에 오신 것을 환영합니다.
    큰 힘에는 큰 책임과 폭발할 수 있는 결과가 따릅니다. 실험실이 빛나는 분화구가 되지 않도록
    모든 안전 절차를 지키세요.
</Callout>

## 개요

Oritech 원자로는 많은 전력을 생산하는 훌륭한 방법입니다.
우라늄 또는 플루토늄 펠릿을 소비하며, 원자로 연료봉 수와 연료봉 옆의 중성자 반사판 수에 따라 RF를 생산합니다.
다만 충분히 냉각하는 것이 매우 중요합니다.

<center>
<ModAsset location="oritech:area/reactor" width={1000} />
</center>

원자로에서 연료를 태우면 열이 발생합니다. 다음 부품으로 원자로의 열을 관리하세요:
- 열 파이프는 연료봉의 열을 받아 파이프를 따라 옮깁니다.
- 원자로 방열구는 연료봉이나 열 파이프처럼 인접한 부품 중 가장 뜨거운 곳에서 열을 일부 받아 원자로 밖으로 방출합니다.
- 흡열기는 인접한 모든 부품에서 일정량의 열을 흡수하지만 계속 작동하려면 냉각재 아이템을 꾸준히 공급해야 합니다.

원자로 내부에는 어느 정도 열이 쌓일 수 있습니다. 제대로 냉각된 원자로라면 이상적으로는 외부로 새는 열이 없어야 합니다.
하지만 방열구 같은 일부 부품은 온도가 높은 환경에서 더 효율적입니다. 제거할 수 없을 만큼 열이 많이 발생하면 연료봉이 과열되어
노심 용융이 일어날 수 있습니다. 연료봉 온도가 2000 C를 넘은 채 일정 시간 유지되면 노심 용융이 시작됩니다.
원자로가 해당 온도에 도달하기 전에 경고 사이렌이 울립니다. 원자로 크기와 연료봉 수에 따라 폭발 규모가 달라집니다.

<Callout variant="info">
    새로운 원자로 설계와 변형을 안전하게 시험하려는 *Oritech Inc*의 견습 과학자는 `Safe Reactors` 설정을 사용할 수 있습니다.
    이 설정을 켜면 원자로가 과열될 때 폭발하는 대신 냉각 상태로 들어갑니다.
</Callout>

<center>
<ModAsset location="oritech:area/reactor_interior_sample" width={500} />
</center>

원자로는 직사각형 벽으로 만들며 모서리에는 원자로 벽 블록을 사용해야 합니다. 한 방향의 최대 크기는 64블록입니다.
벽 어딘가에 원자로 제어기를 놓고, 옆 벽에는 에너지 포트를 설치할 수 있습니다.
포트가 아닌 다른 부품은 모두 원자로 내부에 배치해야 합니다. 높이는 자유롭게 정할 수 있지만 내부 구조는 세로축에서 같아야 합니다.
즉, 원자로를 2D 평면으로 설계한 뒤 원하는 높이까지 위로 늘릴 수 있습니다. 내부 높이 1에서 작동하는 원자로는 높이 10에서도 같은 방식으로 작동하지만,
에너지 생산량과 냉각재 및 연료 소비량도 그에 맞춰 늘어납니다.

다음은 부품을 쌓는 예시입니다:

<center>
<ModAsset location="oritech:area/port_show" width={500} />
</center>
""",
        "content/machines/processing/assembler_block.mdx": """---
title: 조립기
id: oritech:assembler_block
type: block
custom:
    RF 용량: "50,000"
    RF/t: "128"
    필요한 기계 핵: "3"
    애드온 슬롯: "3"
---

조립기에는 2x2 제작 격자가 있습니다. 에너지와 입력 슬롯의 아이템이 충분하고 출력 슬롯에 공간이 있으면
아이템을 자동으로 조립합니다.

일부 기계 부품은 조립기 없이도 만들 수 있지만 훨씬 많은 자원이 필요합니다.

입력 슬롯에 넣은 부품의 순서는 중요하지 않습니다. 같은 아이템 2개가 필요할 때는 한 슬롯에서 모두 가져올 수도 있습니다.

## 자동화

인벤토리 프록시 애드온으로 아이템마다 들어갈 위치를 세밀하게 제어할 수 있습니다.
또는 조립기의 "균등 분배"나 "면별 입력" 모드를 사용하면 일부 설비를 훨씬 쉽게 자동화할 수 있습니다.

AE2 또는 RS2로도 자동화할 수 있습니다. 패턴 공급기는 조립기에 연결하면 별도 설정 없이 작동합니다.


## 효율

[모터](@oritech:motor)나 [자기 코일](@oritech:magnetic_coil) 같은 복잡한 부품은 조립기로 만드는 것이 좋습니다.
직접 제작할 수도 있지만 조립기를 사용할 때보다 자원을 더 많이 소비합니다.
""",
    }
)


FULL_MDX_TRANSLATIONS.update(
    {
        "content/particle/particle_collector_block.mdx": """---
title: 타키온 수집기
id: oritech:particle_collector_block
type: block
custom:
    RF 용량: "1,000,000"
---

타키온 수집기는 고속 입자 충돌이나 다른 원천에서 방출된 타키온을 붙잡아 에너지로 바꿉니다.

입자가 고속으로 충돌하면 에너지 밀도가 높은 타키온을 방출합니다.
충돌 에너지가 높을수록 타키온과 함께 더 많은 에너지가 나오며, 타키온의 수와 이동 거리도 늘어납니다.

타키온은 항상 충돌 지점에서 무작위 방향으로 빠져나갑니다. 전체 영역을 수집기로 둘러싸면 모두 붙잡을 수 있습니다.
타키온을 전부 수집하면 입자를 가속하는 데 사용한 에너지의 최대 **4x**를 얻을 수 있습니다.

입자 가속과 타키온 작동 방식에 관한 자세한 내용은 [입자 가속기 안내서]($particle_accelerator)를 참고하세요.
""",
        "content/equipment/promethium_pickaxe.mdx": """---
id: oritech:promethium_pickaxe
title: 프로메튬 곡괭이
type: item
---

프로메튬 곡괭이는 부서지지 않는 상위 등급 채굴 도구입니다.
채굴 속도가 매우 빠르며 영역 채굴과 섬세한 손길 수확 모드를 전환할 수 있습니다.

### 기능

- **파괴 불가**: 내구도가 없어 절대로 부서지지 않습니다.
- **확장된 사거리**: 손에 들면 블록 및 엔티티 상호작용 거리가 늘어납니다.
- **이중 모드**: **Shift + 우클릭**으로 두 모드를 전환합니다.

#### 영역 모드
곡괭이가 **3x3 영역**을 채굴하므로 큰 터널이나 방을 빠르게 뚫을 때 유용합니다.

#### 섬세한 손길 모드
한 번에 블록 하나를 채굴하지만 모든 블록에 **섬세한 손길**을 자동으로 적용합니다.
광석, 유리, 자수정 군집 같은 블록을 그대로 얻을 수 있습니다.

### 마법 부여

효율이나 행운 같은 일반 곡괭이 마법을 부여할 수 있습니다.
섬세한 손길은 보조 모드에 기본으로 포함되어 있습니다.
""",
        "content/components/carbon_fibre_strands.mdx": """---
title: 탄소 섬유 가닥
id: oritech:carbon_fibre_strands
type: item
---

탄소가 풍부한 가루로 만드는 가볍고 튼튼한 재료입니다.

**제작**
- **원심 분리기**: [석탄 가루](https://minecraft.wiki/w/Coal)나 비슷한 탄소계 가루를 처리해 만듭니다.

**사용법**
강화판, 레버와 중간 등급 기계 핵을 만드는 데 사용합니다.
""",
        "content/components/flux_gate.mdx": """---
title: 플럭스 게이트
id: oritech:flux_gate
type: item
---

플럭스 게이트는 Oritech에서 많은 전력을 조절할 때 사용하는 상위 등급 제어 부품입니다.

**제작**
- **조립기**: [처리 장치](@oritech:processing_unit), [플럭사이트](@oritech:fluxite), [백금](@oritech:platinum_ingot)으로 만듭니다.

**사용법**
- [입자 가속기](@oritech:accelerator_controller), [원자 단조기](@oritech:atomic_forge_block),
  [대형 태양광 패널](@oritech:big_solar_panel_block), [바이오 발전기](@oritech:bio_generator_block),
  [초전도체](@oritech:superconductor), [고급 증강 연구대](@oritech:advanced_augment_station) 같은 중후반부 블록에 사용됩니다.
- 상위 등급 애드온과 격리 조합법에도 널리 쓰이므로 초기에 대량 생산하게 되는 고급 부품 중 하나입니다.
""",
        "content/components/ion_thruster.mdx": """---
title: 이온 추진기
id: oritech:ion_thruster
type: item
---

이온 추진기는 에너지로 추력을 만드는 추진 모듈입니다.

**제작**
- **조립기**: [강화 탄소판](@oritech:reinforced_carbon_sheet), [고급 배터리](@oritech:advanced_battery),
  [플럭스 게이트](@oritech:flux_gate)로 조립합니다.

**사용법**
- [가속기 모터](@oritech:accelerator_motor), 비행 증강과 엑소 비행 업그레이드 및 강화 겉날개 같은 고급 이동 장비에 사용합니다.
- 입자 가속기나 플레이어의 영구 비행 능력을 준비할 때 필요한 핵심 과도기 부품입니다.
""",
        "content/components/reinforced_carbon_sheet.mdx": """---
title: 강화 탄소판
id: oritech:reinforced_carbon_sheet
type: item
---

처리한 탄소 섬유로 만드는 튼튼한 판입니다.

**제작**
- **정유기**: [탄소 섬유 가닥](@oritech:carbon_fibre_strands)을 [나프타](@oritech:fluid_naphtha)로 처리합니다.

**사용법**
장갑판과 추진 장치 부품에 사용합니다.
""",
        "content/components/silicon_wafer.mdx": """---
title: 실리콘 웨이퍼
id: oritech:silicon_wafer
type: item
---

마이크로프로세서의 기판으로 사용하는 얇은 정제 실리콘 조각입니다.

**제작**
- **원자 단조기**: [탄소 섬유 가닥](@oritech:carbon_fibre_strands)과 [실리콘](@oritech:silicon)으로 만듭니다.
- **원심 분리기**: [탄소 섬유 가닥](@oritech:carbon_fibre_strands)과 [실리콘 세척액](@oritech:fluid_silicon_wash)을 처리합니다.

**사용법**
고급 연산 및 인공지능 회로에 사용합니다.
""",
        "content/components/super_ai_chip.mdx": """---
title: 슈퍼 AI 칩
id: oritech:super_ai_chip
type: item
---

슈퍼 AI 칩은 Oritech의 최종 연산 부품 중 하나입니다.

**제작**
- **[원자 단조기](@oritech:atomic_forge_block)**: [듀라티움 주괴](@oritech:duratium_ingot)와
  [고급 연산 엔진](@oritech:advanced_computing_engine)을 융합합니다.

**사용법**
- [두비오스 용기](@oritech:dubios_container), [보조 처리실 애드온](@oritech:machine_processing_addon),
  고급 드론 물류와 다른 최종 단계 기계 부품의 조합법에 사용합니다.
""",
    }
)


FULL_MDX_TRANSLATIONS.update(
    {
        "content/machines/powergen/bio_generator_block.mdx": """---
id: oritech:bio_generator_block
type: block
title: 바이오 발전기
custom:
    RF 용량: "100,000"
    RF/t: "64"
    필요한 기계 핵: "2"

---
[바이오매스](@oritech:biomass)와 다른 생물성 재료를 에너지로 바꿉니다.
농장에서 나오는 유기 폐기물을 재활용하기 좋은 방법입니다.

기본 발전량은 64 RF/t입니다.
## 사용법

조합법 뷰어에 표시되는 바이오매스 연료나 다른 생물성 재료를 공급하세요.
이 멀티블록 기계가 작동하려면 [기계 핵]($multiblocks)이 필요합니다.

나무 농장, 작물 농장처럼 유기 폐기물을 꾸준히 만드는 설비가 있다면 손쉽게 자동화할 수 있는 발전기입니다.
애드온을 지원하므로 기본 발전기를 사용하지 않게 된 뒤에도 계속 활용할 수 있습니다.

<Callout variant="warning">
    계속 작동시키려면 바이오매스를 끊이지 않게 공급하세요.
</Callout>
""",
    }
)


FULL_MDX_TRANSLATIONS.update(
    {
        "content/machines/utility/drone_port_block.mdx": """---
title: 드론 포트
id: oritech:drone_port_block
type: block
---

드론 포트는 자율 비행 드론으로 아이템과 유체를 운반해 장거리 물류를 구현합니다.
출발 지점과 도착 지점에 서로 짝이 맞는 드론 포트가 필요합니다.

---

**물류 및 대상 지정**

[표적 지정기](@oritech:target_designator)로 송신 포트와 목적지를 연결하세요.
대상 포트는 최소 50블록 떨어져 있어야 하며 청크가 계속 로드되는 구역에 있어야 합니다.
포트 하나가 보낼 수 있는 목적지는 한 곳뿐이지만, 여러 외부 포트에서 배송을 받을 수 있습니다.
단, 한 포트가 아이템을 계속 보내면 대상 포트가 "막혀" 다른 포트의 배송이 도착하지 못할 수 있습니다.

---

**에너지 및 업그레이드**

- **이동 비용**: 배송 시간은 일정하지만 에너지 소비량은 거리에 따라
  `sqrt(distance) * 50 + 1024` RF 공식으로 늘어납니다.
- **유체 운송**: 유체를 운반하려면 송신 포트와 수신 포트 모두에
  [유체 애드온](@oritech:machine_fluid_addon)을 장착해야 합니다.
- **자동화**: [레드스톤 애드온](@oritech:machine_redstone_addon)을 장착하면
  인벤토리 양과 작동 상태를 감시할 수 있습니다.

**레드스톤 제어 모드**

레드스톤 애드온은 다음 고급 비교기 출력을 제공합니다:
- **전력 측정**: 저장된 에너지에 따른 신호 강도입니다.
- **인벤토리 슬롯 측정**: 아이템 또는 유체 중 가장 많은 재료 양에 따른 신호 강도입니다.
- **진행도 측정**: 작업 진행도에 따른 신호입니다.
- **작동 측정**: 대기, 송신, 수신 상태에 따른 신호입니다.
- **입력 제어**: 애드온에 전력을 공급하면 포트의 송수신을 막습니다.
""",
    }
)


FULL_MDX_TRANSLATIONS.update(
    {
        "content/equipment/target_designator.mdx": """---
id: oritech:target_designator
title: 표적 지정기
type: item
---

표적 지정기는 기계가 바라볼 위치를 지정하는 도구입니다.
위치를 저장한 뒤 기계에 전달할 수 있습니다.

### 사용법

1. **위치 저장**: 블록을 우클릭해 좌표를 저장합니다.
2. **기계에 전달**: 표적 지정기를 든 채 기계를 Shift + 우클릭해 새 대상을 설정합니다.

### 적용 기계

다음 기계에 표적 지정기가 필요합니다:

- [엔더릭 레이저](@oritech:laser_arm_block): 레이저가 발사할 위치를 지정합니다.
- [드론 포트](@oritech:drone_port_block): 드론의 목적지를 지정합니다.
- [전력 전송 전봇대](@oritech:power_pole_block): 전봇대를 서로 연결합니다.

### 사냥 애드온

[엔더릭 레이저](@oritech:laser_arm_block)에 **사냥 애드온**을 장착한 상태에서
표적 지정기를 사용하면 몹이나 플레이어 같은 조준 대상을 바꿀 수 있습니다.

<Callout variant="info">
    저장한 좌표는 아이템 툴팁에서 확인할 수 있습니다.
</Callout>
""",
    }
)


FULL_MDX_TRANSLATIONS.update(
    {
        "content/equipment/portable_laser.mdx": """---
id: oritech:portable_laser
title: 휴대용 레이저
type: item
custom:
    RF 용량: "5,000,000"
    RF/t: "4,096"
    발사당 RF: "100,000"
    범위: "128블록"
    기본 피해: "4"
    폭발 위력: "6"
---

휴대용 레이저는 채굴과 전투에 사용하는 원거리 도구입니다.
두 가지 모드를 전환해 사용할 수 있습니다.

### 모드

**Shift + 우클릭**으로 모드를 전환합니다.

- **채굴 모드**: 멀리 있는 블록을 광선으로 파괴합니다.
  [기계 프레임](@oritech:machine_frame_block)을 충전하거나 일부 기계의 속도를 높일 수도 있어, 손에 든 소형 엔더릭 레이저처럼 작동합니다.
- **전투 모드**: 블록을 파괴하지 않고 엔티티에만 피해를 줍니다.
  피해량이 높고 크리퍼를 충전된 크리퍼로 바꿀 수 있습니다.

### 기능

- **범위**: 최대 128블록 떨어진 블록까지 닿습니다.
- **업그레이드**: 효율 마법을 부여하면 채굴 모드가 빨라집니다.
  곡괭이에 적용되는 마법과 날카로움도 휴대용 레이저에 적용됩니다.
- **에너지 절약**: **내구성** 마법을 부여하면 채굴 광선과 전투 발사의 에너지 소비량이 줄어듭니다.

### 에너지

휴대용 레이저는 에너지를 많이 소비합니다.
[장비 충전기](@oritech:charger_block)에서 충전하거나 [엑소 흉갑](@oritech:exo_suit)을 사용하세요.

<Callout variant="danger">
    전투 모드의 폭발은 블록을 파괴할 수 있으므로 기지 근처에서 사용할 때 주의하세요.
</Callout>
""",
        "content/logistics/item_pipe.mdx": """---
id: oritech:item_pipe
type: block
related_items: ["oritech:framed_item_pipe", "oritech:item_pipe_duct_block", "oritech:transparent_item_pipe"]
title: 아이템 파이프
custom:
    전송량: "펄스당 아이템 8개"
    전송 간격: "5틱"
---

Oritech의 아이템 운송에는 아이템 파이프와 아이템 필터 블록을 사용합니다.
아이템 파이프는 서로 연결되며 인접한 인벤토리에도 연결됩니다.

아이템 파이프 자체에는 인벤토리가 없어서 호퍼 같은 다른 블록이 파이프망에 직접 아이템을 넣을 수 없습니다.
대신 인접한 인벤토리에서 아이템을 추출하도록 파이프를 설정해야 합니다.

## 변형
*   **표준형**: 기본 파이프입니다.
*   **프레임형**: 한 블록을 가득 채우는 형태입니다.
*   **투명형**: 내부에서 이동하는 아이템을 보여 줍니다. 이동 경로 전체가 투명 파이프일 때만 작동합니다.
*   **덕트형**: 외형이 다른 파이프입니다. 기계에 직접 연결되지 않고 다른 파이프에만 연결됩니다.

추출 모드를 전환하려면 아이템을 꺼낼 블록에 연결된 파이프 부분을 우클릭하세요.
추출을 지원하는 블록에 연결되어 있을 때만 활성화되며, 연결 방향마다 따로 설정할 수 있습니다.
특정 방향의 연결을 끊으려면 파이프 렌치를 사용하세요.

추출된 아이템은 월드 거리 기준으로 파이프망 안에서 **가장 가까운** 빈 인벤토리에 들어갑니다.

<Callout variant="warning">
    파이프는 인벤토리에서 처음 발견한 비어 있지 않은 슬롯의 아이템부터 추출합니다.
    파이프망 안의 어느 인벤토리에도 그 아이템을 넣을 수 없으면 해당 인벤토리에서 더 이상 추출하지 못합니다.

    파이프를 우클릭해 모터를 설치하면 모든 슬롯에서 추출하도록 업그레이드할 수 있습니다.
    성능을 위해 기본 상태에서는 이 기능이 비활성화되어 있습니다.
</Callout>

<center>
<ModAsset location="oritech:area/item_pipes" width={512} />
</center>

기본 전송 속도는 5틱마다 아이템 8개입니다.
""",
    }
)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def clean_mdx(value: str) -> str:
    """MDX 구조는 유지하면서 각 줄 끝의 불필요한 공백을 제거한다."""
    return "\n".join(line.rstrip() for line in value.rstrip().splitlines()) + "\n"


def clean_unit(value: str) -> str:
    """번역 단위의 줄 끝 공백을 제거하되 마지막 줄바꿈은 추가하지 않는다."""
    return "\n".join(line.rstrip() for line in value.splitlines())


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def guide_paths(archive: ZipFile) -> list[str]:
    return sorted(
        name
        for name in archive.namelist()
        if name.startswith(BOOK_PREFIX)
        and "/translated/" not in name
        and (name.endswith(".mdx") or name.endswith("/_meta.json"))
    )


def prepare() -> dict[str, object]:
    """현재 JAR의 영어 MDX·목차 메타데이터를 작업 폴더에 준비한다."""
    source_root = resolve_source_root()
    jar = family_goal.find_jar(source_root, JAR_PREFIX)
    files: list[str] = []
    with ZipFile(jar) as archive:
        for name in guide_paths(archive):
            relative = PurePosixPath(name).relative_to(BOOK_PREFIX)
            target = ENGLISH_ROOT.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            raw = archive.read(name)
            if name.endswith(".mdx"):
                target.write_text(clean_mdx(raw.decode("utf-8")), encoding="utf-8")
            else:
                target.write_bytes(raw)
            files.append(relative.as_posix())
    report = {
        "jar": jar.name,
        "mdx_files": sum(path.endswith(".mdx") for path in files),
        "meta_files": sum(path.endswith("_meta.json") for path in files),
        "files": files,
    }
    write_json(WORK_ROOT / "scope.json", report)
    return report


def mask_custom(text: str) -> tuple[str, list[str]]:
    protected: list[str] = []

    def replace(match: re.Match[str]) -> str:
        token = f"ZXQGUIDE{len(protected)}QXZ"
        protected.append(match.group(0))
        return token

    return CUSTOM_PROTECTED.sub(replace, text), protected


def restore_custom(text: str, protected: list[str]) -> str:
    for index, value in enumerate(protected):
        token = f"ZXQGUIDE{index}QXZ"
        if text.count(token) != 1:
            raise ValueError(f"가이드 보호 토큰이 바뀌었습니다: {token}")
        text = text.replace(token, value)
    return text


def mask_normalization(text: str) -> tuple[str, list[str]]:
    """단어 경계를 유지하면서 링크·식별자를 후처리에서 보호한다."""
    protected: list[str] = []

    def replace(match: re.Match[str]) -> str:
        token = f"\ue000{len(protected)}\ue001"
        protected.append(match.group(0))
        return token

    return CUSTOM_PROTECTED.sub(replace, text), protected


def restore_normalization(text: str, protected: list[str]) -> str:
    for index, value in enumerate(protected):
        token = f"\ue000{index}\ue001"
        if text.count(token) != 1:
            raise ValueError(f"가이드 정규화 보호 토큰이 바뀌었습니다: {index}")
        text = text.replace(token, value)
    return text


def request_candidate(source: str) -> str:
    masked, protected = mask_custom(source)
    translated = ars_family.request_translation(masked)
    return restore_custom(translated, protected)


def frontmatter_parts(text: str) -> tuple[list[str], list[str]]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError("MDX frontmatter 시작 구분자가 없습니다.")
    try:
        end = next(
            index for index in range(1, len(lines)) if lines[index].strip() == "---"
        )
    except StopIteration as exc:
        raise ValueError("MDX frontmatter 종료 구분자가 없습니다.") from exc
    return lines[: end + 1], lines[end + 1 :]


def translatable_units(text: str) -> list[str]:
    frontmatter, body = frontmatter_parts(text)
    units: list[str] = []
    custom = False
    for line in frontmatter[1:-1]:
        stripped = line.strip()
        if stripped == "custom:":
            custom = True
            continue
        if not stripped:
            continue
        if line.startswith((" ", "\t")) and custom and ":" in stripped:
            label = stripped.split(":", 1)[0]
            if not family_goal.is_allowed_original(label):
                units.append(label)
            continue
        custom = False
        if stripped.startswith("title:"):
            value = stripped.split(":", 1)[1].strip().strip('"')
            if value and not family_goal.is_allowed_original(value):
                units.append(value)
    paragraph: list[str] = []
    fenced = False
    for line in body + [""]:
        if line.lstrip().startswith("```"):
            fenced = not fenced
            paragraph.append(line)
            continue
        if not line.strip() and not fenced:
            if paragraph:
                value = "\n".join(paragraph)
                if re.search(r"[A-Za-z]{3,}", value) and not (
                    value.lstrip().startswith("```") and value.rstrip().endswith("```")
                ):
                    units.append(value)
                paragraph = []
            continue
        paragraph.append(line)
    return units


def json_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: list[str] = []
        for item in value.values():
            result.extend(json_strings(item))
        return result
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(json_strings(item))
        return result
    return []


def candidate() -> dict[str, object]:
    """가이드 본문과 목차의 모든 영어 표시 문자열에 번역 후보를 만든다."""
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    if not isinstance(cache, dict):
        raise TypeError("가이드 후보 캐시가 객체가 아닙니다.")
    units: set[str] = set()
    for path in sorted(ENGLISH_ROOT.rglob("*")):
        if path.suffix == ".mdx":
            units.update(translatable_units(path.read_text(encoding="utf-8")))
        elif path.name == "_meta.json":
            units.update(
                value
                for value in json_strings(load_json(path))
                if re.search(r"[A-Za-z]{3,}", value)
                and not family_goal.is_allowed_original(value)
            )
    requests = {
        value
        for value in units
        if value not in MANUAL_CANDIDATES and not isinstance(cache.get(value), str)
    }
    failures: list[str] = []
    if requests:
        completed = 0
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(request_candidate, source): source
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
        raise RuntimeError("가이드 자동 후보 생성 실패:\n" + "\n".join(failures))
    report = {
        "translatable_units": len(units),
        "candidate_units": sum(isinstance(cache.get(value), str) for value in units),
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


def language_name_map() -> dict[str, str]:
    english = load_json(PROJECT_ROOT / "working/oritech/oritech/en_us.json")
    korean = load_json(PROJECT_ROOT / "working/oritech/oritech/ko_kr.json")
    assert isinstance(english, dict) and isinstance(korean, dict)
    rows: dict[str, set[str]] = {}
    for key, source in english.items():
        target = korean[key]
        if isinstance(source, str) and isinstance(target, str):
            rows.setdefault(source, set()).add(target)
    return {
        source: next(iter(targets))
        for source, targets in rows.items()
        if len(targets) == 1
    }


def normalize_text(value: str, names: dict[str, str]) -> str:
    translated = names.get(value, value)
    translated = translated.replace("\u200b", "").replace("\ufeff", "")
    for old, new in GUIDE_REPLACEMENTS:
        if old.startswith(("#", "*")):
            translated = translated.replace(old, new)
    translated, protected = mask_normalization(translated)
    for source, target in sorted(
        oritech_family.SOURCE_OVERRIDES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        translated = translated.replace(source, target)
    for old, new in GUIDE_REPLACEMENTS:
        if re.fullmatch(r"[A-Za-z][A-Za-z -]*", old):
            translated = re.sub(
                rf"(?<![A-Za-z]){re.escape(old)}(?![A-Za-z])", new, translated
            )
        else:
            translated = translated.replace(old, new)
    translated = re.sub(r"(?<![A-Za-z])Z(?=\d)", "", translated)
    translated = re.sub(r"[ \t]+([,.!?])", r"\1", translated)
    for old, new in FINAL_GUIDE_REPLACEMENTS:
        translated = translated.replace(old, new)
    translated = restore_normalization(translated, protected)
    return re.sub(
        r"\*\*(.*?)\*\*", lambda match: f"**{match.group(1).strip()}**", translated
    )


def internal_link_names() -> dict[str, str]:
    korean = load_json(PROJECT_ROOT / "working/oritech/oritech/ko_kr.json")
    assert isinstance(korean, dict)
    result: dict[str, str] = {}
    for prefix in ("block.oritech.", "item.oritech.", "fluid.oritech."):
        for key, value in korean.items():
            if key.startswith(prefix) and isinstance(value, str):
                identifier = "@oritech:" + key[len(prefix) :]
                result.setdefault(identifier, value)
    return result


def rewrite_internal_links(text: str, link_names: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        target = match.group(1)
        label = link_names.get(target)
        return f"[{label}]({target})" if label else match.group(0)

    return re.sub(r"\[[^\]]+\]\((@oritech:[^)]+)\)", replace, text)


def cached_translation(
    source: str, cache: dict[str, object], names: dict[str, str]
) -> str:
    source = clean_unit(source)
    if family_goal.is_allowed_original(source):
        return source
    candidate_value = MANUAL_CANDIDATES.get(source)
    if candidate_value is None:
        candidate_value = next(
            (
                value
                for key, value in MANUAL_CANDIDATES.items()
                if clean_unit(key) == source
            ),
            cache.get(source),
        )
    if not isinstance(candidate_value, str):
        raise KeyError(f"가이드 번역 후보가 없습니다: {source}")
    return normalize_text(candidate_value, names)


def translate_mdx(
    text: str,
    cache: dict[str, object],
    names: dict[str, str],
    link_names: dict[str, str],
) -> str:
    frontmatter, body = frontmatter_parts(text)
    translated_front = [frontmatter[0]]
    custom = False
    for line in frontmatter[1:-1]:
        stripped = line.strip()
        if stripped == "custom:":
            custom = True
            translated_front.append(line)
            continue
        if line.startswith((" ", "\t")) and custom and ":" in stripped:
            indent = line[: len(line) - len(line.lstrip())]
            label, rest = stripped.split(":", 1)
            translated_label = cached_translation(label, cache, names)
            translated_front.append(f"{indent}{translated_label}:{rest}")
            continue
        custom = False
        if stripped.startswith("title:"):
            prefix, value = line.split(":", 1)
            title = value.strip().strip('"')
            translated_title = names.get(title) or cached_translation(
                title, cache, names
            )
            translated_front.append(f"{prefix}: {translated_title}")
        else:
            translated_front.append(line)
    translated_front.append(frontmatter[-1])

    translated_body: list[str] = []
    paragraph: list[str] = []
    fenced = False

    def flush() -> None:
        if not paragraph:
            return
        value = "\n".join(paragraph)
        if re.search(r"[A-Za-z]{3,}", value) and not (
            value.lstrip().startswith("```") and value.rstrip().endswith("```")
        ):
            value = cached_translation(value, cache, names)
        translated_body.extend(value.split("\n"))
        paragraph.clear()

    for line in body:
        if line.lstrip().startswith("```"):
            fenced = not fenced
            paragraph.append(line)
            continue
        if not line.strip() and not fenced:
            flush()
            translated_body.append("")
        else:
            paragraph.append(line)
    flush()
    return rewrite_internal_links(
        "\n".join(translated_front + translated_body), link_names
    )


def translate_json(
    value: object, cache: dict[str, object], names: dict[str, str]
) -> object:
    if isinstance(value, str):
        if not re.search(r"[A-Za-z]{3,}", value) or family_goal.is_allowed_original(
            value
        ):
            return value
        return cached_translation(value, cache, names)
    if isinstance(value, dict):
        return {key: translate_json(item, cache, names) for key, item in value.items()}
    if isinstance(value, list):
        return [translate_json(item, cache, names) for item in value]
    return value


def normalize() -> dict[str, object]:
    """후보 전부를 Oritech 확정 용어로 재검수하여 작업본과 출력에 반영한다."""
    cache = load_json(CACHE_FILE)
    if not isinstance(cache, dict):
        raise TypeError("가이드 후보 캐시가 객체가 아닙니다.")
    cache = {clean_unit(key): value for key, value in cache.items()}
    names = language_name_map()
    link_names = internal_link_names()
    files = 0
    for source in sorted(ENGLISH_ROOT.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(ENGLISH_ROOT)
        candidate_target = CANDIDATE_ROOT / relative
        korean_target = KOREAN_ROOT / relative
        output_target = OUTPUT_ROOT / relative
        if source.suffix == ".mdx":
            reviewed = FULL_MDX_TRANSLATIONS.get(relative.as_posix())
            if reviewed is None:
                translated = translate_mdx(
                    source.read_text(encoding="utf-8"), cache, names, link_names
                )
            else:
                translated = rewrite_internal_links(
                    normalize_text(reviewed, names), link_names
                )
            for target in (candidate_target, korean_target, output_target):
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(clean_mdx(translated), encoding="utf-8")
        elif source.name == "_meta.json":
            translated_json = translate_json(load_json(source), cache, names)
            for target in (candidate_target, korean_target, output_target):
                write_json(target, translated_json)
        else:
            continue
        files += 1
    report = {
        "files_reviewed": files,
        "mdx_files": len(list(KOREAN_ROOT.rglob("*.mdx"))),
        "meta_files": len(list(KOREAN_ROOT.rglob("_meta.json"))),
        "review_status": "all_current_english_guide_files_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def token_counter(pattern: re.Pattern[str], text: str) -> Counter[str]:
    return Counter(pattern.findall(text))


def audit_advancements(
    archive: ZipFile, english: dict[str, object], korean: dict[str, object]
) -> dict[str, object]:
    displayed = 0
    literal: list[str] = []
    missing: list[str] = []
    for name in archive.namelist():
        if "/advancement/" not in name or not name.endswith(".json"):
            continue
        value = json.loads(archive.read(name))
        display = value.get("display") if isinstance(value, dict) else None
        if not isinstance(display, dict):
            continue
        displayed += 1
        keys: list[str] = []
        for field in ("title", "description"):
            component = display.get(field)
            if isinstance(component, dict) and isinstance(
                component.get("translate"), str
            ):
                keys.append(component["translate"])
            elif component is not None:
                literal.append(f"{name}:{field}")
        for key in keys:
            if key not in english or key not in korean:
                missing.append(key)
    return {
        "displayed": displayed,
        "literal_display": literal,
        "missing_translation_keys": sorted(set(missing)),
    }


def audit_kubejs(source_root: Path) -> dict[str, object]:
    references: list[str] = []
    visible: list[str] = []
    kubejs = source_root / "kubejs"
    for path in sorted(kubejs.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "oritech" not in text.lower():
            continue
        relative = path.relative_to(kubejs).as_posix()
        references.append(relative)
        if re.search(r"(?:custom_name|displayName|setName)\s*\(", text):
            visible.append(relative)
    return {"reference_files": references, "direct_visible_literal_files": visible}


def audit_guide_quality(text: str) -> list[str]:
    """코드와 식별자를 제외한 실제 표시 문장의 기계번역 흔적을 검사한다."""
    _, body = frontmatter_parts(text)
    errors: list[str] = []
    fenced = False
    for line_number, line in enumerate(body, 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if re.fullmatch(r"#{1,6}\s*", line):
            errors.append(f"빈 제목:{line_number}")
        if len(VISIBLE_LINK_TARGET.findall(line)) != len(VISIBLE_LINK.findall(line)):
            errors.append(f"깨진 표시 링크:{line_number}")
        bold_values = re.findall(r"\*\*(.*?)\*\*", line)
        if any(not value or value != value.strip() for value in bold_values):
            errors.append(f"잘못된 굵게 표시:{line_number}")
        if any(value in line for value in FORBIDDEN_KOREAN_ARTIFACTS):
            errors.append(f"기계번역 어투:{line_number}")
        if (
            "<CraftingRecipe" in line
            or "slots={[" in line
            or "result=" in line
            or "count={" in line
            or re.search(r"'[a-z0-9_:.-]+'", line)
        ):
            continue
        visible = re.sub(r"`[^`]*`", "", line)
        visible = COMPONENT.sub("", visible)
        visible = re.sub(r"\]\([^)]*\)", "]()", visible)
        unexpected_words = [
            word
            for word in VISIBLE_WORD.findall(visible)
            if word not in ALLOWED_VISIBLE_WORDS
        ]
        if unexpected_words:
            errors.append(f"가시 영어 잔존:{line_number}:{','.join(unexpected_words)}")
        if ISOLATED_TRANSLATION_ARTIFACT.search(visible):
            errors.append(f"단독 영문 번역 흔적:{line_number}")
        if HANGUL_LATIN_SUFFIX.search(visible):
            errors.append(f"한글 뒤 영문 접미 흔적:{line_number}")
    return errors


def verify() -> tuple[dict[str, object], int]:
    """가이드 구조·보호 토큰·출력 일치와 관련 표시 경로를 검증한다."""
    errors: list[str] = []
    mdx_files = 0
    meta_files = 0
    for source in sorted(ENGLISH_ROOT.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(ENGLISH_ROOT)
        target = KOREAN_ROOT / relative
        output = OUTPUT_ROOT / relative
        if not target.is_file() or not output.is_file():
            errors.append(f"가이드 출력 누락: {relative.as_posix()}")
            continue
        if target.read_bytes() != output.read_bytes():
            errors.append(f"가이드 누적 출력 불일치: {relative.as_posix()}")
        if source.suffix == ".mdx":
            mdx_files += 1
            english_text = source.read_text(encoding="utf-8").replace("\r\n", "\n")
            korean_text = target.read_text(encoding="utf-8")
            try:
                english_front, _ = frontmatter_parts(english_text)
                korean_front, _ = frontmatter_parts(korean_text)
            except ValueError as exc:
                errors.append(f"MDX frontmatter 오류: {relative.as_posix()}:{exc}")
                continue
            for key in ("id:", "type:", "icon:"):
                old = [
                    line.strip()
                    for line in english_front
                    if line.strip().startswith(key)
                ]
                new = [
                    line.strip()
                    for line in korean_front
                    if line.strip().startswith(key)
                ]
                if old != new:
                    errors.append(f"MDX 식별자 불일치: {relative.as_posix()}:{key}")
            for label, pattern in (
                ("링크", LINK_TARGET),
                ("컴포넌트", COMPONENT),
                ("식별자", IDENTIFIER),
                ("숫자", NUMBER),
            ):
                if token_counter(pattern, english_text) != token_counter(
                    pattern, korean_text
                ):
                    errors.append(f"MDX {label} 불일치: {relative.as_posix()}")
            if english_text.count("```") != korean_text.count("```"):
                errors.append(f"MDX 코드 블록 불일치: {relative.as_posix()}")
            if english_text.count("**") != korean_text.count("**"):
                errors.append(f"MDX 굵게 표시 불일치: {relative.as_posix()}")
            english_headings = Counter(
                re.findall(r"^#{1,6}\s+", english_text, flags=re.MULTILINE)
            )
            korean_headings = Counter(
                re.findall(r"^#{1,6}\s+", korean_text, flags=re.MULTILINE)
            )
            if english_headings != korean_headings:
                errors.append(f"MDX 제목 계층 불일치: {relative.as_posix()}")
            for quality_error in audit_guide_quality(korean_text):
                errors.append(
                    f"MDX 표시 품질 오류: {relative.as_posix()}:{quality_error}"
                )
        elif source.name == "_meta.json":
            meta_files += 1
            english_json = load_json(source)
            korean_json = load_json(target)
            if isinstance(english_json, dict) and isinstance(korean_json, dict):
                if english_json.keys() != korean_json.keys():
                    errors.append(f"목차 키 불일치: {relative.as_posix()}")

    source_root = resolve_source_root()
    jar = family_goal.find_jar(source_root, JAR_PREFIX)
    english = load_json(PROJECT_ROOT / "working/oritech/oritech/en_us.json")
    korean = load_json(PROJECT_ROOT / "working/oritech/oritech/ko_kr.json")
    assert isinstance(english, dict) and isinstance(korean, dict)
    with ZipFile(jar) as archive:
        advancements = audit_advancements(archive, english, korean)
    kubejs = audit_kubejs(source_root)
    if advancements["literal_display"]:
        errors.append(f"발전 과제 literal 표시: {advancements['literal_display']}")
    if advancements["missing_translation_keys"]:
        errors.append(
            f"발전 과제 번역 키 누락: {advancements['missing_translation_keys']}"
        )
    if kubejs["direct_visible_literal_files"]:
        errors.append(
            f"KubeJS 직접 표시 문자열 확인 필요: {kubejs['direct_visible_literal_files']}"
        )
    report = {
        "mdx_files": mdx_files,
        "meta_files": meta_files,
        "advancements": advancements,
        "kubejs": kubejs,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "validation.json", report)
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("prepare", "candidate", "normalize", "verify")
    )
    args = parser.parse_args()
    if args.command == "prepare":
        report = prepare()
        status = 0
    elif args.command == "candidate":
        report = candidate()
        status = 0
    elif args.command == "normalize":
        report = normalize()
        status = 0
    else:
        report, status = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
