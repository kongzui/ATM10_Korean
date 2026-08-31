#!/usr/bin/env python3
"""The Twilight Forest 모드군의 신규 번역 후보와 직접 연동을 처리한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from zipfile import ZipFile

import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/twilight_forest"
BASE_ROOT = WORK_ROOT / "twilightforest"
CACHE_PATH = PROJECT_ROOT / "temp/twilight_forest_auto_candidates.json"
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"
GOOGLE_TRANSLATE = "https://translate.googleapis.com/translate_a/single"
PROTECTED = re.compile(
    r"https?://\S+"
    r"|%(?:\d+\$)?[a-zA-Z%]"
    r"|\{[A-Za-z0-9_]+\}"
    r"|\$\{[^}]+\}"
    r"|\$\([^)]*\)"
    r"|[&§][0-9A-FK-ORa-fk-or]"
    r"|<[^>]+>"
    r"|\\n"
    r"|\n"
    r"|\d+(?:[.,]\d+)*(?:[xX×]\d+)?"
)

FORMAT_FIXES = {
    "advancement.twilightforest.naga_armors.desc": "%s와 %s을(를) 제작하세요",
    "config.twilightforest.casket_uuid_locking.tooltip": (
        "참이면 플레이어가 사망할 때 생성된 유품 상자를 다른 플레이어가 열 수 "
        "없습니다. 다른 사람의 유품 상자에서 아이템을 가져가지 못하게 하려면 "
        "사용하세요.\n참고: 서버 운영자는 잠긴 상자를 열 수 있습니다."
    ),
    "config.twilightforest.origin_dimension.tooltip": (
        "항상 황혼의 숲으로 이동할 수 있고 되돌아오게 될 차원입니다. 기본값은 "
        "오버월드입니다. (domain:regname)."
    ),
    "config.twilightforest.disable_uncrafting.tooltip": (
        "역제작대의 역제작 기능을 비활성화합니다. 동작을 바꿔야 할 사항이 너무 많은 "
        "경우(또는 그냥 귀찮은 경우에도 괜찮아요) 마지막 수단으로 사용하는 것을 "
        "권장합니다.\n특수 역제작 제작법은 모드의 다른 기능에 필요하므로 비활성화되지 "
        "않습니다."
    ),
    "config.twilightforest.portal_permission.tooltip": (
        "지정된 권한 이상을 가진 플레이어가 차원문을 만들 수 있게 합니다. 바닐라 권한 "
        "시스템을 따릅니다.\n자세한 내용: https://minecraft.wiki/w/Permission_level"
    ),
    "config.twilightforest.ram_indicator.tooltip": (
        "양털을 든 채 퀘스팅 램을 바라보면, 그 색의 양털을 이미 먹였는지에 따라 조준점 "
        "위에 확인 표시 또는 X를 표시합니다."
    ),
    "enchantment.twilightforest.renewal.desc": (
        "소지자의 인벤토리에 재충전 아이템이 있으면 충전량을 모두 쓴 홀을 자동으로 "
        "재충전합니다."
    ),
    "magic_painting.twilightforest.music_in_the_mire.title": "늪의 음악",
    "twilightforest.book.lichtower.1": (
        "§8[괴물에게 갉아 먹힌 탐험가의 수첩]§0\n\n이 탑을 둘러싼 이상한 기운을 "
        "조사하기 시작했다. 탑의 벽돌은 지금까지 본 어떤 것보다 강한 저주로 "
        "보호받고 있다. 저주의 마법은 끓어오르며"
    ),
    "twilightforest.book.lichtower.3": (
        "§8[[많은 장을 넘긴 후에]]§0\n\n돌파구를 찾았어요! 여행 중 장식된 안뜰에서 "
        "뱀처럼 생긴 거대한 괴물을 목격했어요. 근처에서는 닳고 버려진 녹색 비늘을 "
        "주웠어요.\n\n비늘에 깃든 마법에는 제가 필요한 저주 해제"
    ),
    "twilightforest.book.lichtower.4": (
        "속성이 있지만, 마법이 너무 희미해요. 그 생물에게서 직접 더 신선한 표본을 "
        "얻어야 할지도 모르겠어요."
    ),
    "twilightforest.book.yeticave.1": (
        "§8[[서리로 뒤덮인 탐험가의 수첩]]§0\n\n이 눈 덮인 땅을 둘러싼 눈보라가 "
        "그치지 않고 있어요. 평범한 눈이 아니라 마법 현상이에요. 무엇이 이런 효과를"
    ),
    "twilightforest.book.yeticave.2": (
        "일으키는지 알아내려면 실험해야겠어요.\n\n§8[[다음 장]]§0\n\n이 저주는 한 "
        "존재가 혼자 만들기에는 너무 강력한 듯해요. 여러 마법사가 힘을 합쳐야 할 "
        "거예요. 그중 한 명이라도"
    ),
    "twilightforest.book.yeticave.3": (
        "힘을 보태지 않으면 눈보라가 잠잠해질 거예요. 이상하게도 점괘에는 근처에 살아 "
        "있는 마법사의 흔적이 나타나지 않아요. 하지만 근처의 뾰족한 지붕 탑 하나에서 "
        "흥미로운 것을 봤어요..."
    ),
    "twilightforest.tips.mushglooms": (
        "머시그룸은 뼛가루로 거대 버섯으로 키울 수 없습니다. 하지만 양질의 흙에 놓으면 "
        "자랍니다."
    ),
}

QUALITY_TEXT_REPLACEMENTS = (
    ("극지동물의 털", "극지 털"),
    ("카미나이트 가스트유체", "카미나이트 가스트링"),
    ("팬텀 기사", "기사 유령"),
    ("기사 팬텀", "기사 유령"),
    ("로얄 좀비", "충성스러운 좀비"),
    ("생명의 지배 지팡이", "생명력 흡수의 홀"),
    ("생명의 지배", "생명력 흡수의 홀"),
    ("황혼의 지배", "황혼의 홀"),
    ("무장의 지배", "요새화의 홀"),
    ("불사의 지배", "좀비의 홀"),
    ("우르-가스트", "유어 가스트"),
    ("리버뿌리", "생뿌리"),
    ("횃불딸기", "토치베리"),
    ("미로 지도 집중체", "미로 지도 초점"),
    ("마법의 지도 집중체", "마법 지도 초점"),
    ("마법의 지도 깃털", "마법 지도 초점"),
    ("마법의 지도", "마법 지도"),
    ("미노타우르스 스트로가노프", "미프 스트로가노프"),
    ("미노타우르스의 도끼", "미노타우로스 도끼"),
    ("할로우 힐", "속 빈 언덕"),
    ("퀘스트 양", "퀘스팅 램"),
    ("광석 미터", "광석 측정기"),
    ("구현 블록", "재등장 블록"),
    ("은폐 블록", "소멸 블록"),
    ("매야플", "메이애플"),
    ("미네우드", "광부나무"),
    ("돌 트위스트", "뒤틀린 돌"),
    ("생기없는 진액", "무생물의 정수"),
    ("생기 없는 진액", "무생물의 정수"),
    ("전환 가루", "변환 가루"),
    ("투구 게", "투구게"),
    ("매다는 표지판", "매달린 표지판"),
    ("벽 매달린 표지판", "벽걸이 표지판"),
    ("가스트링가", "가스트링이"),
    ("기사 유령가", "기사 유령이"),
    ("홀가", "홀이"),
    ("홀를", "홀을"),
)

QUALITY_LANGUAGE_OVERRIDES = {
    "twilightforest.book.author": "잊힌 탐험가",
    "twilightforest.book.darktower": "나무 탑에 관한 기록",
    "twilightforest.book.darktower.1": (
        "§8[[폭발 속에서도 남아 있는 듯한 탐험가의 수첩]]§0\n\n이 탑에는 분명 "
        "내게 반응하지 않는 장치가 있다. 장치의 마법은 내 손길을 알아보려는 듯하지만 "
        "그럴 수 없다. 마치 탑의 장치가"
    ),
    "twilightforest.book.darktower.2": (
        "근처의 강력한 존재들에 의해 억눌린 듯하다.\n\n§8[[다음 기록]]§0\n\n마법은 "
        "근처 요새 깊은 곳에서 흘러나오는 것 같다. 고블린의 마법은 부적에 가깝고 "
        "집중되어 있지 않으니, 그들에게서 나오는 힘은 아닐 것이다. 요새에는"
    ),
    "twilightforest.book.darktower.3": (
        "아직도 어떤 힘이 작동하고 있음이 틀림없다.\n\n§8[[다음 기록]]§0\n\n분석해 "
        "보니 여러 근원이 무리를 이루어 힘을 내고 있다. 보급을 마치는 대로 요새로 "
        "돌아가야겠다..."
    ),
    "twilightforest.book.hydralair": "불타는 늪에 관한 기록",
    "twilightforest.book.hydralair.1": (
        "§8[[내화 종이에 쓴 탐험가의 수첩]]§0\n\n나 같은 노련한 탐험가에게 불은 "
        "하찮은 장애물이다. 불바다를 건너고 용암의 바다를 헤엄친 적도 있다. 이곳의 "
        "타는 듯한 공기는 흥미로운 변화이지만"
    ),
    "twilightforest.book.hydralair.2": (
        "결국 아무런 방해도 되지 않는다.\n\n하지만 이번에는 이 불타는 늪의 왕이 분명한 "
        "강력한 생물을 둘러싼 또 다른 보호 주문이 나를 막는다. 보호 주문과 마주친 "
        "것은 처음이 아니며, 이제 나는"
    ),
    "twilightforest.book.hydralair.3": (
        "그 작동 원리를 조금씩 풀어내고 있다.\n\n이 주문도 다른 것들과 같다면 근처의 "
        "강력한 생물이 힘을 공급할 것이다. 불타는 늪 주변에는 습지가 여럿 있고, 그 "
        "아래에는 미노타우로스가 가득한 미궁이 있다."
    ),
    "twilightforest.book.hydralair.4": (
        "그런 주문을 묶어 둘 대상으로는 주변의 다른 미노타우로스와 어딘가 다른, "
        "강력한 미노타우로스가 가장 그럴듯하다..."
    ),
    "twilightforest.book.icetower": "오로라 요새에 관한 기록",
    "twilightforest.book.icetower.1": (
        "§8[[얼음으로 뒤덮인 탐험가의 수첩]]§0\n\n눈보라 하나를 이겨 냈더니 이번에는 "
        "빙하 꼭대기의 끔찍한 얼음 폭풍과 마주쳤다. 탐험 중에 극지방의 오로라처럼 "
        "여러 색으로 빛나는 얼음 궁전의 장관을 보았지만"
    ),
    "twilightforest.book.icetower.2": (
        "그 모든 것이 어떤 저주로 보호받는 듯하다.\n\n§8[[다음 기록]]§0\n\n나는 "
        "초보자가 아니다. 이 저주는 근처 생물의 힘을 공급받고 있다. 불타는 늪을 "
        "둘러싼 저주도 근처"
    ),
    "twilightforest.book.icetower.3": (
        "미노타우로스 우두머리의 힘으로 만들어졌다.\n\n이 빙하 주변에는 수많은 예티가 "
        "모여 있다. 어쩌면 예티에게도 우두머리가 있는 게 아닐까..."
    ),
    "twilightforest.book.labyrinth": "늪지 미궁에 관한 기록",
    "twilightforest.book.labyrinth.1": (
        "§8[[방수 종이에 쓴 탐험가의 수첩]]§0\n\n이 늪의 모기는 성가시면서도 이상하다. "
        "대부분 자연적으로 생겨난 흔적이 없고 이곳 생태계에서 맡은 역할도 보이지 "
        "않는다. 나는 모기들이"
    ),
    "twilightforest.book.labyrinth.2": (
        "일종의 마법 저주라고 의심하기 시작했다.\n\n§8[[다음 기록]]§0\n\n이곳의 "
        "폐허가 된 미궁에서 보호 주문까지 발견했으니 의심은 확신으로 바뀌었다. 보호 "
        "주문과 모기는 모두 하나의"
    ),
    "twilightforest.book.labyrinth.3": (
        "저주다. 이 저주는 지금까지 만난 것들과 근원이 다른 듯하다. 더 조사해야겠다..."
        "\n\n§8[[다음 기록]]§0\n\n이 저주는 한 존재가 혼자 만들기에는 너무 강력한 "
        "종류인 듯하다."
    ),
    "twilightforest.book.labyrinth.4": (
        "여러 마법사가 힘을 합쳐야 만들 수 있을 것이다.\n\n그중 한 명이라도 힘을 보태지 "
        "않으면 늪 전체를 뒤덮은 저주가 무너질 것이다. 이상하게도 점괘에는 근처에 "
        "살아 있는 마법사의 흔적이 나타나지 않는다."
    ),
    "twilightforest.book.labyrinth.5": (
        "다만 근처의 뾰족한 지붕을 가진 탑 하나에서 흥미로운 것을 보았다..."
    ),
    "twilightforest.book.lichtower": "뾰족한 탑에 관한 기록",
    "twilightforest.book.lichtower.1": (
        "§8[괴물에게 갉아 먹힌 탐험가의 수첩]§0\n\n이 탑을 둘러싼 이상한 기운을 "
        "조사하기 시작했다. 탑의 벽돌은 지금까지 본 어떤 것보다 강한 저주로 "
        "보호받고 있다. 저주의 마법이 끓어오르며"
    ),
    "twilightforest.book.lichtower.2": (
        "주변으로 퍼지고 있다.\n\n고향에 있었다면 이 마법을 처리할 방법이 많겠지만, "
        "이곳에서는 물자가 부족하다. 더 조사해야겠다..."
    ),
    "twilightforest.book.lichtower.3": (
        "§8[[수많은 기록이 지난 뒤]]§0\n\n돌파구를 찾았다! 여행 중 장식된 안뜰에서 "
        "뱀처럼 생긴 거대한 괴물을 목격했다. 근처에서는 닳아 버려진 녹색 비늘을 "
        "주웠다.\n\n비늘에 깃든 마법에는 내가 필요한 저주 해제"
    ),
    "twilightforest.book.lichtower.4": (
        "성질이 있지만 마력이 너무 희미하다. 그 생물에게서 직접 더 싱싱한 표본을 "
        "얻어야 할지도 모르겠다."
    ),
    "twilightforest.book.tfstronghold": "요새에 관한 기록",
    "twilightforest.book.tfstronghold.1": (
        "§8[[희미하게 빛나는 종이에 쓴 탐험가의 수첩]]§0\n\n이 지역을 둘러싼 어둠의 "
        "덩굴은 어두운 숲 전체에 걸린 보호 주문이 드러난 것일 뿐이다. 주문은 앞을 "
        "보지 못하게 만들어 몹시 성가시다. 이곳에서 몇 가지"
    ),
    "twilightforest.book.tfstronghold.2": (
        "흥미로운 것을 보았으니 계속 탐험하고 싶다.\n\n§8[[다음 기록]]§0\n\n어두운 "
        "숲에서 폐허를 발견했다. 보통 기사들이 지키는 형태의 요새다. 하지만 기사 대신 "
        "이 요새를 가득 채운 것은"
    ),
    "twilightforest.book.tfstronghold.3": (
        "고블린이다. 기사 같은 갑옷을 입었지만 행동은 기사답지 않다.\n\n§8[[다음 "
        "기록]]§0\n\n폐허 깊은 곳에서 받침대를 발견했다. 기사들이 힘을 증명하기 위해 "
        "트로피를 올려 두는 종류인 듯하다."
    ),
    "twilightforest.book.tfstronghold.4": (
        "강력한 홀을 얻으면 어두운 숲의 저주가 약해질 듯하다. 또 강력한 생물과 관련된 "
        "트로피를 받침대에 올리면 요새의 중심부로 들어갈 수 있을 것이다."
    ),
    "twilightforest.book.trollcave": "고원에 관한 기록",
    "twilightforest.book.trollcave.1": (
        "§8[[산에 부식된 탐험가의 수첩]]§0\n\n이 지역을 둘러싼 유독성 폭풍우로부터 "
        "몸을 지킬 방법은 없는 듯하다. 잠깐씩 나가 살펴보던 중, 지금까지 본 것들과 "
        "비슷한 또 다른 보호 주문도 발견했다."
    ),
    "twilightforest.book.trollcave.2": (
        "그 주문은 어떤 식으로든 유독성 폭풍우와 연결되어 있을 것이다. 더 조사해야겠다..."
        "\n\n§8[[다음 기록]]§0\n\n이토록 강력한 날씨 마법은 이 세계에서 아직 쓰러지지 "
        "않은 여러 거대한 악의 결과임이 틀림없다. 내 연구에는"
    ),
    "twilightforest.book.trollcave.3": (
        "타오르는 늪, 짙은 어둠으로 뒤덮인 숲, 눈에 덮인 왕국을 가리키는 단서가 "
        "여럿 있다."
    ),
    "twilightforest.book.unknown": "설명할 수 없는 것에 관한 기록",
    "twilightforest.book.unknown.1": (
        "§8[[여러 번 베껴 쓴 흔적이 있는 책]]§0\n\n이 구조물을 둘러싼 장막은 설명할 "
        "수 없지만, 마법의 힘은 강력하다. 이 저주가 다른 것들과 같다면 잠금을 풀 "
        "해답은 다른 곳에 있을 것이다. 어쩌면 내가 아직 끝내지"
    ),
    "twilightforest.book.unknown.2": (
        "못한 일이 있거나 처치하지 못한 괴물이 있을지도 모른다. 일단 돌아가야겠다. "
        "나중에 다시 와서 무언가 달라졌는지 확인해야겠다."
    ),
    "twilightforest.book.yeticave": "얼어붙은 동굴에 관한 기록",
    "twilightforest.book.yeticave.1": (
        "§8[[서리로 뒤덮인 탐험가의 수첩]]§0\n\n이 눈 덮인 땅을 둘러싼 눈보라가 "
        "그치지 않는다. 평범한 눈이 아니라 마법 현상이다. 무엇이 이런 효과를"
    ),
    "twilightforest.book.yeticave.2": (
        "일으키는지 알아내려면 실험해야겠다.\n\n§8[[다음 기록]]§0\n\n이 저주는 한 "
        "존재가 혼자 만들기에는 너무 강력한 듯하다. 여러 마법사가 힘을 합쳐야 할 "
        "것이다. 그중 한 명이라도"
    ),
    "twilightforest.book.yeticave.3": (
        "힘을 보태지 않으면 눈보라가 잠잠해질 것이다. 이상하게도 점괘에는 근처에 살아 "
        "있는 마법사의 흔적이 나타나지 않는다. 하지만 근처의 뾰족한 지붕을 가진 탑 "
        "하나에서 흥미로운 것을 보았다..."
    ),
    "twilightforest.tips.banister_shape": (
        "도끼를 든 채 난간을 우클릭하면 높이를 바꿀 수 있습니다."
    ),
    "twilightforest.tips.block_and_chain": (
        "블록과 사슬은 마법 부여대로 마법을 부여할 수 있습니다."
    ),
    "twilightforest.tips.bugs_on_head": "벌레는 기꺼이 머리 위에 앉습니다.",
    "twilightforest.tips.charm_of_keeping": (
        "보존의 부적은 사망해도 인벤토리의 일부를 지켜 줍니다."
    ),
    "twilightforest.tips.druid_hut": (
        "해골 드루이드 오두막에는 숨겨진 지하실이 있을 수 있습니다."
    ),
    "twilightforest.tips.e115_pickup": (
        "설치된 실험체 115번을 웅크린 채 우클릭하면 회수할 수 있습니다."
    ),
    "twilightforest.tips.fiery_pickaxe": (
        "파이어리 곡괭이는 부순 블록을 자동으로 제련합니다."
    ),
    "twilightforest.tips.hollow_log": "속이 빈 통나무 안을 잘 살펴보세요!",
    "twilightforest.tips.magic_saplings": (
        "마법나무 묘목은 지하 전리품 상자에서 찾을 수 있습니다."
    ),
    "twilightforest.tips.mazebreaker": (
        "미로 파괴자는 미로석을 16배 빠르게 부수며, 내구도가 추가로 소모되지 않습니다."
    ),
    "twilightforest.tips.twilight_portal": (
        "꽃으로 둘러싼 물웅덩이에 다이아몬드를 던지면 황혼의 숲 포털을 만들 수 "
        "있습니다."
    ),
    "twilightforest.tips.zombie_healing": (
        "좀비의 홀로 소환한 좀비는 썩은 살점으로 회복시킬 수 있습니다."
    ),
    "config.twilightforest.animate_trophies": "트로피 움직임",
    "config.twilightforest.animate_trophies.tooltip": (
        "인벤토리에서 트로피 아이템이 움직이고 회전하게 합니다."
    ),
    "config.twilightforest.boss_drop_chests.tooltip": (
        "참이면 The Twilight Forest 보스가 전리품을 바로 떨어뜨리는 대신 원래 생성된 "
        "위치에 상자를 만들고 그 안에 넣습니다.\n기사 유령의 전리품은 다른 방식으로 "
        "처리되므로 이 설정의 영향을 받지 않습니다."
    ),
    "config.twilightforest.casket_uuid_locking": "유품 상자 UUID 잠금",
    "config.twilightforest.check_portal_placement.tooltip": (
        "새 포털을 만들기 전에 목적지가 안전한지 확인할지 정합니다. 거짓이면 안전한 "
        "대체 목적지로 옮기는 대신 포털 생성에 실패합니다.\n이 기능을 끄면 포털 생성 "
        "검사 빈도도 줄어듭니다."
    ),
    "config.twilightforest.disable_portal.tooltip": (
        "황혼의 숲 포털 생성을 완전히 비활성화합니다. 차원 접근을 제한하려는 서버 "
        "운영자를 위한 설정입니다."
    ),
    "config.twilightforest.cloud_precipitation.tooltip": (
        "날씨 처리를 위해 구름 블록 아래로 몇 블록까지 검사할지 정합니다.\n틱 속도가 "
        "느려지면 값을 낮추세요. 0으로 설정하면 구름의 강수 처리를 모두 끕니다."
    ),
    "config.twilightforest.default_item_enchantments.tooltip": (
        "거짓이면 제작할 때 기본 마법이 부여되는 아이템(아이언우드 또는 강철잎 장비 "
        "등)이 크리에이티브 인벤토리에서 마법 부여된 상태로 표시되지 않습니다.\n제작법 "
        "자체에는 영향을 주지 않으며, 제작법을 바꾸려면 데이터팩이 필요합니다."
    ),
    "config.twilightforest.dim_settings.tooltip": (
        "부작용 없이 되돌릴 수 없는 설정입니다."
    ),
    "config.twilightforest.ingredient_switching.tooltip": (
        "참이면 제작법이 제작 태그를 사용할 때 역제작대에서 재료를 다른 항목으로 바꿀 "
        "수 없습니다.\n모든 제작법에서 재료 전환 기능이 사라집니다!\n처음부터 특정 "
        '재료가 표시되지 않게 하려면 "twilightforest:banned_uncrafting_ingredients" '
        "태그를 사용하세요."
    ),
    "config.twilightforest.disable_skull_candles.tooltip": (
        "바닐라 해골에 초를 사용해 해골 초를 만드는 기능을 비활성화합니다."
    ),
    "config.twilightforest.parry_window": "패링 판정 시간",
    "config.twilightforest.parry_window.tooltip": (
        "방패를 든 뒤 투사체를 패링할 수 있는 시간(틱)입니다. (1틱 = 1/20초)"
    ),
    "config.twilightforest.screen_offset_x.tooltip": (
        "화면의 모든 표시 특성에 적용할 시작 X 오프셋을 정합니다."
    ),
    "config.twilightforest.magic_trees": "마법나무",
    "config.twilightforest.magic_trees.tooltip": "마법나무와 관련된 모든 설정입니다.",
    "config.twilightforest.max_portal_size.tooltip": (
        "포털을 만들 때 확인할 물 블록의 최대 개수입니다. 값이 너무 크면 성능 문제가 "
        "생길 수 있습니다."
    ),
    "config.twilightforest.multiplayer_fight_adjuster": "멀티플레이 보스전 조정",
    "config.twilightforest.multiplayer_fight_adjuster.more_loot_and_health": (
        "전리품 및 체력 증가"
    ),
    "config.twilightforest.origin_dimension": "기준 차원",
    "config.twilightforest.portal_for_new_player.tooltip": (
        "참이고 `newPlayersSpawnInTF`도 참이면 황혼의 숲으로 보내진 새 플레이어를 위한 "
        "귀환 포털을 생성합니다."
    ),
    "config.twilightforest.portals_in_other_dimensions.tooltip": (
        "'기준' 차원이 아닌 곳에서도 황혼의 숲 포털을 만들 수 있게 합니다. 악용될 "
        "가능성이 있습니다."
    ),
    "config.twilightforest.prettify_ore_meter_gui": "광석 측정기 GUI 정렬",
    "config.twilightforest.prettify_ore_meter_gui.tooltip": (
        "광석 측정기 GUI의 대시와 백분율을 가지런히 맞춥니다."
    ),
    "config.twilightforest.screen_shake.tooltip": (
        "마법의 콩이 자라는 동안 화면을 흔들지 정합니다."
    ),
    "config.twilightforest.spawn_in_tf.tooltip": (
        "참이면 처음 접속한 플레이어가 황혼의 숲에서 생성됩니다."
    ),
    "config.twilightforest.shapeless_uncrafting": "무정형 제작법 역제작",
    "config.twilightforest.shapeless_uncrafting.tooltip": (
        "참이면 역제작대에서 무정형 제작법도 역제작할 수 있습니다.\n역제작대는 원래 "
        "정형 제작법만 처리하도록 설계되었지만, 기존 기능을 유지하려는 사용자를 위해 "
        "이 옵션이 남아 있습니다."
    ),
    "config.twilightforest.shield_indicator": "요새화 방패 표시기",
    "config.twilightforest.shield_indicator.tooltip": (
        "현재 활성화된 요새화 방패의 수를 방어구 막대 위에 표시합니다.\n다른 모드의 "
        "표시와 겹치면 이 기능을 끄세요."
    ),
    "config.twilightforest.shield_indicator_creative": (
        "요새화 방패 표시기(크리에이티브)"
    ),
    "config.twilightforest.shield_indicator_creative.tooltip": (
        "디버깅을 위해 크리에이티브 모드에서도 요새화 방패 표시기를 활성화합니다."
    ),
    "config.twilightforest.totem_charm_animation": "불사의 토템식 부적 애니메이션",
    "config.twilightforest.uncrafting_xp_cost": "역제작 비용 배수",
    "config.twilightforest.repairing_xp_cost": "수리 비용 배수",
    "advancement.twilightforest.fiery_set.desc": (
        "파이어리 방어구를 하나 이상 착용하고 파이어리 도구나 무기를 드세요"
    ),
    "advancement.twilightforest.hill1.desc": (
        "작은 속 빈 언덕에 있는 %s을(를) 처치하세요"
    ),
    "advancement.twilightforest.hill2.desc": (
        "중형 속 빈 언덕에 있는 %s을(를) 처치하세요"
    ),
    "advancement.twilightforest.hill3.desc": (
        "거대한 속 빈 언덕에 있는 %s을(를) 처치하세요"
    ),
    "advancement.twilightforest.lich_scepters.desc": (
        "강력한 홀 네 종류를 모두 획득하세요"
    ),
    "advancement.twilightforest.quest_ram": "램의 소원은 모두 이루어졌다",
    "advancement.twilightforest.quest_ram.desc": "%s에게 필요한 것을 건네주세요",
    "enchantment.twilightforest.chill_aura.desc": (
        "착용자를 공격한 적에게 서리 효과가 적용될 확률을 추가합니다."
    ),
    "enchantment.twilightforest.destruction.desc": (
        "블록과 사슬이 더 높은 채굴 등급의 블록도 부술 수 있게 합니다."
    ),
    "enchantment.twilightforest.fire_react.desc": (
        "착용자를 공격한 적에게 불이 붙을 확률을 추가합니다."
    ),
    "item.twilightforest.arctic_fur": "극지 털",
    "item.twilightforest.arctic_helmet": "극지 후드",
    "item.twilightforest.arctic_chestplate": "극지 재킷",
    "item.twilightforest.boarkchop": "생 보어크찹",
    "item.twilightforest.raw_meef": "생 미프",
    "item.twilightforest.cooked_meef": "미프 스테이크",
    "item.twilightforest.meef_stroganoff": "미프 스트로가노프",
    "item.twilightforest.exanimate_essence": "무생물의 정수",
    "item.twilightforest.magic_map_focus": "마법 지도 초점",
    "item.twilightforest.maze_map_focus": "미로 지도 초점",
    "item.twilightforest.maze_wafer": "미로 웨이퍼",
    "item.twilightforest.ore_meter": "광석 측정기",
    "item.twilightforest.quest_ram_spawn_egg": "퀘스팅 램 생성 알",
    "item.twilightforest.fortification_scepter": "요새화의 홀",
    "item.twilightforest.lifedrain_scepter": "생명력 흡수의 홀",
    "item.twilightforest.twilight_scepter": "황혼의 홀",
    "item.twilightforest.zombie_scepter": "좀비의 홀",
    "item.twilightforest.transformation_powder": "변환 가루",
    "item.twilightforest.yeti_chestplate": "예티 재킷",
    "item.twilightforest.magic_map": "빈 마법 지도",
    "item.twilightforest.emperors_cloth.desc": "가려짐",
    "item.twilightforest.harbinger_cube_spawn_egg": "전조의 큐브 생성 알",
    "item.twilightforest.moon_dial.phase_1": "기울어가는 볼록달",
    "item.twilightforest.moon_dial.phase_4": "삭",
    "item.twilightforest.moon_dial.phase_7": "차오르는 볼록달",
    "biome.twilightforest.clearing": "황혼의 공터",
    "biome.twilightforest.snowy_forest": "눈 덮인 숲",
    "biome.twilightforest.thornlands": "가시 지대",
    "commands.tffeature.center": "랜드마크 중심: %s",
    "commands.tffeature.chunk": "랜드마크 청크: %s",
    "commands.tffeature.nearest": "가장 가까운 랜드마크: %s",
    "commands.tffeature.none_nearby": "주변에서 랜드마크를 찾지 못했습니다!",
    "commands.tffeature.structure.conquer.status": "구조물 정복 상태 플래그: %s",
    "commands.tffeature.structure.conquer.update": (
        "구조물 정복 상태 플래그를 %s에서 %s(으)로 변경했습니다."
    ),
    "commands.tffeature.structure.inside": "랜드마크 구조물 안에 있습니다",
    "commands.tffeature.structure.outside": "랜드마크 구조물 밖에 있습니다",
    "commands.tffeature.structure.spawn_info": "%s, 가중치 %s",
    "commands.tffeature.usage": "/%s <info | reactivate | conquer | center>",
    "entity.twilightforest.carminite_ghastling": "카미나이트 가스트링",
    "entity.twilightforest.harbinger_cube": "전조의 큐브",
    "entity.twilightforest.knight_phantom": "기사 유령",
    "entity.twilightforest.loyal_zombie": "충성스러운 좀비",
    "entity.twilightforest.quest_ram": "퀘스팅 램",
    "entity.twilightforest.lich": "황혼의 리치",
    "misc.twilightforest.ore_meter_loading": "불러오는 중",
    "death.attack.twilightforest.slider": "%1$s이(가) 슬라이더에게 잘렸습니다",
    "death.attack.twilightforest.slider.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 슬라이더에게 잘렸습니다"
    ),
    "death.attack.twilightforest.chillingBreath.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 눈의 여왕에게 얼어 죽었습니다."
    ),
    "death.attack.twilightforest.failedChallenge": (
        "%1$s이(가) 패기를 증명하지 못하고 마시다 죽었습니다"
    ),
    "death.attack.twilightforest.fiery.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 파이어리 블록을 밟았습니다."
    ),
    "death.attack.twilightforest.fireJet.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 실수로 화염 분출기에 들어갔습니다."
    ),
    "death.attack.twilightforest.ghastTear.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 불타는 눈물에 데었습니다."
    ),
    "death.attack.twilightforest.haunt": "%1$s이(가) %2$s의 유령 무리에 합류했습니다.",
    "death.attack.twilightforest.haunt.item": (
        "%1$s이(가) %3$s을(를) 든 %2$s에게 죽어 유령 무리에 합류했습니다."
    ),
    "death.attack.twilightforest.hydraBite.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 히드라에게 살가죽을 뜯겼습니다."
    ),
    "death.attack.twilightforest.hydraFire.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 히드라에게 산 채로 구워졌습니다."
    ),
    "death.attack.twilightforest.knightmetal.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 기사금속 블록에 찔렸습니다."
    ),
    "death.attack.twilightforest.lichBomb.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 리치의 폭발 마법에 쓰러졌습니다."
    ),
    "death.attack.twilightforest.lifedrain": (
        "%1$s이(가) %2$s에게 생명력을 빼앗겼습니다."
    ),
    "death.attack.twilightforest.lifedrain.item": (
        "%1$s이(가) %3$s을(를) 사용한 %2$s에게 생명력을 빼앗겼습니다."
    ),
    "death.attack.twilightforest.lostWords": (
        "%1$s이(가) %2$s에게 죽은 뒤 할 말을 잃었습니다."
    ),
    "death.attack.twilightforest.lostWords.item": (
        "%1$s이(가) %3$s을(를) 사용한 %2$s에게 죽은 뒤 할 말을 잃었습니다."
    ),
    "death.attack.twilightforest.moonworm": "%1$s이(가) 월충에게 맞았습니다.",
    "death.attack.twilightforest.reactor.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 카미나이트 반응기에 너무 가까이 갔습니다."
    ),
    "death.attack.twilightforest.schooled": "%1$s이(가) %2$s에게 혼쭐이 났습니다.",
    "death.attack.twilightforest.schooled.item": (
        "%1$s이(가) %3$s을(를) 사용한 %2$s에게 혼쭐이 났습니다."
    ),
    "death.attack.twilightforest.snowballFight": (
        "%1$s이(가) %2$s와의 눈싸움에서 졌습니다."
    ),
    "death.attack.twilightforest.snowballFight.item": (
        "%1$s이(가) %3$s을(를) 사용한 %2$s와의 눈싸움에서 졌습니다."
    ),
    "death.attack.twilightforest.squish.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 눈의 여왕에게 짓눌렸습니다."
    ),
    "death.attack.twilightforest.thorns.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 가시덤불에 들어갔습니다."
    ),
    "death.attack.twilightforest.thrownAxe.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 날아온 도끼에 참수되었습니다."
    ),
    "death.attack.twilightforest.thrownBlock.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 날아온 블록에 짓눌렸습니다."
    ),
    "death.attack.twilightforest.thrownPickaxe.player": (
        "%1$s이(가) %2$s에게서 도망치던 중 날아온 곡괭이에 참수되었습니다."
    ),
    "subtitles.twilightforest.block.candelabra.ominous": "촛대에서 불꽃이 튐",
    "subtitles.twilightforest.block.casket.locked": "유품 상자가 딸깍거림",
    "subtitles.twilightforest.entity.tiny_bird.takeoff": "작은 새가 날아오름",
    "subtitles.twilightforest.item.charm.life": "생명의 부적이 생명을 되돌림",
    "subtitles.twilightforest.item.life_scepter.drain": "생명력 흡수의 홀이 생명력을 흡수함",
    "subtitles.twilightforest.item.ore_meter.clear": "광석 측정기가 정보를 지움",
    "subtitles.twilightforest.item.ore_meter.crackle": "광석 측정기가 탁탁거림",
    "subtitles.twilightforest.item.ore_meter.target_block": (
        "광석 측정기가 블록을 대상으로 지정함"
    ),
    "itemGroup.twilightforest.blocks": "The Twilight Forest: 블록",
    "itemGroup.twilightforest.equipment": "The Twilight Forest: 장비",
    "itemGroup.twilightforest.food": "The Twilight Forest: 음식",
    "itemGroup.twilightforest.items": "The Twilight Forest: 아이템",
    "block.twilightforest.casket.locked": "이 유품 상자는 %s만 열 수 있습니다!",
    "block.twilightforest.chipped_keepsake_casket": "금이 간 유품 상자",
    "block.twilightforest.damaged_keepsake_casket": "손상된 유품 상자",
    "block.twilightforest.cinder_furnace": "잿불 화로",
    "block.twilightforest.cinder_log": "잿불 원목",
    "block.twilightforest.cinder_wood": "잿불 나무",
    "block.twilightforest.cut_mazestone": "절단된 미로석",
    "block.twilightforest.knightmetal_block.desc": "접촉한 대상에게 큰 피해를 줍니다",
    "block.twilightforest.lich_tower_miniature_structure": "소형 리치 탑",
    "block.twilightforest.mason_jar": "메이슨병",
    "block.twilightforest.naga_courtyard_miniature_structure": "소형 나가 안뜰",
    "block.twilightforest.torchberry_plant": "토치베리 식물",
    "block.twilightforest.transformation_leaves": "변화나무 잎",
    "block.twilightforest.twilight_portal_miniature_structure": ("소형 황혼의 숲 포털"),
    "block.twilightforest.twisted_stone_pillar": "뒤틀린 돌기둥",
    "block.twilightforest.wrought_iron_fence": "연철 울타리",
    "item.twilightforest.wrought_iron_bar": "연철 창살",
    "structure.twilightforest.large_hollow_hill": "큰 속 빈 언덕",
    "structure.twilightforest.medium_hollow_hill": "중형 속 빈 언덕",
    "structure.twilightforest.small_hollow_hill": "작은 속 빈 언덕",
    "museumcurator.equipment.twilightforest.scepters": "강력한 홀",
    "museumcurator.machinery.twilightforest.carminitemachines": "카미나이트 장치",
    "gui.twilightforest.transformation_jei": "변환 가루",
    "misc.twilightforest.ore_meter_no_blocks": "주변에서 블록을 찾지 못했습니다",
    "misc.twilightforest.ore_meter_range": "반경: %s, 중심: [%s, %s]",
    "misc.twilightforest.ore_meter_total": "검사한 총 블록 수: %s",
    "misc.twilightforest.wip": (
        "이 기능은 개발 중이며, 버그나 의도하지 않은 효과로 월드가 손상될 수 있습니다"
    ),
    "twilightforest.tips.ghast_trap": (
        "가스트 함정 근처에서 카미나이트 가스트링을 처치하면 함정이 충전됩니다."
    ),
    "twilightforest.tips.hydra_heads": (
        "히드라는 머리 하나를 처치할 때마다 그 자리에서 머리 두 개를 재생합니다!"
    ),
    "twilightforest.tips.lich_scepters": ("리치는 다양한 마법의 홀을 떨어뜨립니다."),
    "twilightforest.tips.quest_ram": (
        "퀘스팅 램은 자신에게 필요한 것을 건넨 플레이어에게 보상을 줍니다."
    ),
    "twilightforest.tips.ur_ghast": (
        "가스트 함정을 사용하면 유어 가스트를 하늘에서 끌어내릴 수 있습니다."
    ),
    "twilightforest.tips.worldgen_features": (
        "숲 곳곳에는 많은 폐허가 있으며, 일부에는 특별한 아이템이 들어 있습니다."
    ),
}

NEW_EXACT = {
    "advancement.twilightforest.chicken_jerky": "치킨 저키!",
    "advancement.twilightforest.craft_travellers_gear": "80일간의 숲 일주",
    "advancement.twilightforest.craft_travellers_gear.desc": "여행자 장비를 제작하세요",
    "advancement.twilightforest.modify_travellers_gear": "옷이 사람을 말해 준다",
    "advancement.twilightforest.modify_travellers_gear.desc": (
        "여행자 장비에 특성을 추가하세요"
    ),
    "block.twilightforest.blackberry_bush": "블랙베리 덤불",
    "block.twilightforest.blightberry_bush": "블라이트베리 덤불",
    "block.twilightforest.blueberry_bush": "블루베리 덤불",
    "block.twilightforest.copper_oreberry": "구리 오어베리 덤불",
    "block.twilightforest.dark_tower_miniature_structure": "소형 어둠의 탑",
    "block.twilightforest.duskberry_bush": "더스크베리 덤불",
    "block.twilightforest.essence_oreberry": "에센스 베리 덤불",
    "block.twilightforest.gold_oreberry": "금 오어베리 덤불",
    "block.twilightforest.iron_oreberry": "철 오어베리 덤불",
    "block.twilightforest.maloberry_bush": "말로베리 덤불",
    "block.twilightforest.minotaur_labyrinth_miniature_structure": (
        "소형 미노타우로스 미궁"
    ),
    "block.twilightforest.raspberry_bush": "라즈베리 덤불",
    "block.twilightforest.skyberry_bush": "스카이베리 덤불",
    "block.twilightforest.stingberry_bush": "스팅베리 덤불",
    "commands.tffeature.ability_modifier": (
        "여행자 장비에서는 능력을 추가하거나 제거할 수 없습니다"
    ),
    "commands.tffeature.added_modifier": "%s을(를) %s에 추가했습니다!",
    "commands.tffeature.biomepng.counts_header": (
        "%sx%s 영역 안의 대략적인 생물 군계 블록 수"
    ),
    "commands.tffeature.biomepng.progress": "%s%% 매핑 완료",
    "commands.tffeature.biomepng.save_failed": (
        "이미지를 저장하지 못했습니다! 이 문제를 신고해 주세요!"
    ),
    "commands.tffeature.biomepng.save_success": "이미지를 저장했습니다!",
    "commands.tffeature.display_pieces.missing_key": "누락된 키",
    "commands.tffeature.generator_radius.center_chunk": "구조물 시작점의 중앙 청크",
    "commands.tffeature.generator_radius.radius": "중앙 청크로부터 반경: %s",
    "commands.tffeature.has_modifier": "이 여행자 장비에는 이미 %s 특성이 있습니다",
    "commands.tffeature.info.wip": (
        "이 명령어는 아직 개발 중이므로 일부 기능이 올바르게 작동하지 않을 수 있습니다."
    ),
    "commands.tffeature.invalid_modifier": "%s은(는) 유효한 여행자 장비 특성이 아닙니다",
    "commands.tffeature.no_modifier": "이 여행자 장비에는 %s 특성이 적용되지 않았습니다",
    "commands.tffeature.not_travellers_gear": "여행자 장비를 들고 있지 않습니다",
    "commands.tffeature.removed_modifier": "%s을(를) %s에서 제거했습니다!",
    "commands.tffeature.teleport.dimension_missing": (
        "The Twilight Forest 차원을 사용할 수 없습니다."
    ),
    "commands.tffeature.teleport.player_only": "플레이어만 이 명령어를 실행할 수 있습니다.",
    "commands.tffeature.teleport.success": (
        "The Twilight Forest의 %s %s %s 위치로 순간이동했습니다"
    ),
    "commands.tffeature.too_many_modifiers": (
        "이 여행자 장비에는 이미 특성이 최대치로 적용되어 있습니다"
    ),
    "commands.tffeature.wrong_modifier_slot": (
        "이 여행자 장비에는 %s 특성을 적용할 수 없습니다"
    ),
    "config.jade.plugin_twilightforest.drying_rack": "건조대 시간",
    "config.twilightforest.aurora_biomes.button": "생물 군계 편집",
    "config.twilightforest.first_person_glove_overlay": "1인칭 장갑 표시",
    "config.twilightforest.first_person_glove_overlay.tooltip": (
        "1인칭 시점에서 여행자 장갑이 손에 표시되게 합니다."
    ),
    "config.twilightforest.giant_skin_uuid_list.button": "스킨 편집",
    "config.twilightforest.item_display": "아이템 표시 특성 설정",
    "config.twilightforest.item_display.tooltip": (
        "여행자 장비의 아이템 표시 특성을 사용할 때 각 요소가 표시되는 위치를 "
        "제어합니다."
    ),
    "config.twilightforest.manual_travellers_wings_gradual_glide": "수동 점진 활공",
    "config.twilightforest.manual_travellers_wings_gradual_glide.tooltip": (
        "이 옵션이 꺼져 있으면 느린 낙하가 기본이며, 웅크리기 키를 누르면 정상 "
        "속도로 떨어집니다. 옵션이 켜져 있으면 정상 낙하가 기본이며, 웅크리기 키를 "
        "누르면 느린 낙하가 활성화됩니다."
    ),
    "config.twilightforest.screen_offset_x": "표시 X 오프셋",
    "config.twilightforest.screen_offset_x.tooltip": (
        "화면의 모든 표시 특성에 적용할 시작 Y 오프셋을 정합니다."
    ),
    "config.twilightforest.screen_offset_y": "표시 Y 오프셋",
    "config.twilightforest.screen_offset_y.tooltip": (
        "화면의 모든 표시 특성에 적용할 시작 Y 오프셋을 정합니다."
    ),
    "config.twilightforest.screen_scale": "표시 배율",
    "config.twilightforest.screen_scale.tooltip": (
        "화면의 모든 표시 특성에 적용할 배율을 정합니다."
    ),
    "config.twilightforest.twenty_four_hour_format": "24시간 형식",
    "config.twilightforest.twenty_four_hour_format.tooltip": (
        "켜면 시계 업그레이드가 12시간 형식 대신 24시간 형식으로 시간을 표시합니다."
    ),
    "death.attack.twilightforest.oreberry": "%1$s이(가) 오어베리 덤불에 찔려 죽었습니다",
    "death.attack.twilightforest.oreberry.player": (
        "%1$s이(가) %2$s에게서 도망치다 오어베리 덤불에 찔려 죽었습니다"
    ),
    "death.attack.twilightforest.stale_sandwich": (
        "%1$s이(가) %2$s 때문에 묵은 샌드위치가 되었습니다"
    ),
    "gamerule.playersTfPortalCreativeDelay": (
        "크리에이티브 모드 플레이어의 The Twilight Forest 포털 대기 시간"
    ),
    "gamerule.playersTfPortalCreativeDelay.description": (
        "크리에이티브 모드 플레이어가 차원을 이동하기 전에 The Twilight Forest "
        "포털 안에 서 있어야 하는 시간(틱)입니다."
    ),
    "gamerule.playersTfPortalDefaultDelay": (
        "일반 모드 플레이어의 The Twilight Forest 포털 대기 시간"
    ),
    "gamerule.playersTfPortalDefaultDelay.description": (
        "크리에이티브 모드가 아닌 플레이어가 차원을 이동하기 전에 The Twilight "
        "Forest 포털 안에 서 있어야 하는 시간(틱)입니다."
    ),
    "gui.twilightforest.drying_jei": "건조대",
    "gui.twilightforest.drying_minute": "%s분",
    "gui.twilightforest.drying_minutes": "%s분",
    "gui.twilightforest.drying_second": "%s초",
    "gui.twilightforest.drying_seconds": "%s초",
    "gui.twilightforest.drying_ticks": "%s틱",
    "item.twilightforest.beef_jerky": "소고기 육포",
    "item.twilightforest.berry_medley": "모둠 베리",
    "item.twilightforest.blackberry": "블랙베리",
    "item.twilightforest.blightberry": "블라이트베리",
    "item.twilightforest.blueberry": "블루베리",
    "item.twilightforest.chicken_jerky": "닭고기 육포",
    "item.twilightforest.cod_jerky": "대구 육포",
    "item.twilightforest.copper_berry": "구리 오어베리",
    "item.twilightforest.copper_nugget": "구리 조각",
    "item.twilightforest.duskberry": "더스크베리",
    "item.twilightforest.essence_berry": "농축 에센스 베리",
    "item.twilightforest.fugu_jerky": "복어 육포",
    "item.twilightforest.gelatinous_maze_slime_drop": "젤라틴 미로 슬라임 방울",
    "item.twilightforest.gelatinous_slime_drop": "젤라틴 슬라임 방울",
    "item.twilightforest.gold_berry": "금 오어베리",
    "item.twilightforest.iron_berry": "철 오어베리",
    "item.twilightforest.maloberry": "말로베리",
    "item.twilightforest.maze_slime_ball": "미로 슬라임볼",
    "item.twilightforest.meef_jerky": "미프 육포",
    "item.twilightforest.monster_jerky": "몬스터 육포",
    "item.twilightforest.moss_soup": "이끼 수프",
    "item.twilightforest.mutton_jerky": "양고기 육포",
    "item.twilightforest.pork_jerky": "돼지고기 육포",
    "item.twilightforest.rabbit_jerky": "토끼고기 육포",
    "item.twilightforest.raspberry": "라즈베리",
    "item.twilightforest.salmon_jerky": "연어 육포",
    "item.twilightforest.shika_senbei": "사슴 센베이",
    "item.twilightforest.skyberry": "스카이베리",
    "item.twilightforest.stale_bread": "묵은 빵",
    "item.twilightforest.stingberry": "스팅베리",
    "item.twilightforest.tanned_leather": "무두질한 가죽",
    "item.twilightforest.tannin": "타닌",
    "item.twilightforest.travellers_belt": "여행자 허리띠",
    "item.twilightforest.travellers_boots": "여행자 장화",
    "item.twilightforest.travellers_gloves": "여행자 장갑",
    "item.twilightforest.travellers_gloves.desc": "장식용",
    "item.twilightforest.travellers_goggles": "여행자 고글",
    "item.twilightforest.travellers_vest": "여행자 조끼",
    "item.twilightforest.travellers_wings": "여행자 날개",
    "item.twilightforest.treated_leather": "처리된 가죽",
    "item.twilightforest.tropical_fish_jerky": "열대어 육포",
    "item.twilightforest.venison_jerky": "사슴고기 육포",
    "itemGroup.twilightforest.food": "The Twilight Forest: 음식",
    "jade.drying_rack.remaining": "%s 남음",
    "key.twilightforest.categories.travellers_gear": (
        "The Twilight Forest (여행자 장비)"
    ),
    "key.twilightforest.item_display_map_cycle": "아이템 표시에 저장된 지도 전환",
    "key.twilightforest.red_thread_vision": "고글로 붉은 실 보기",
    "key.twilightforest.swap_hotbar": "단축바 교체",
    "key.twilightforest.zoom": "고글로 확대/축소",
    "subtitles.twilightforest.block.drying_rack.add_item": "건조대에 아이템을 올림",
    "subtitles.twilightforest.block.drying_rack.remove_item": "건조대에서 아이템을 꺼냄",
    "subtitles.twilightforest.entity.deer.eat": "사슴이 먹음",
    "subtitles.twilightforest.item.travellers_gear.cycle_maps": "지도를 전환함",
    "subtitles.twilightforest.item.travellers_gear.cycle_maps_empty": "지도를 전환함",
    "subtitles.twilightforest.item.travellers_gear.double_jump": "이단 점프를 함",
    "subtitles.twilightforest.item.travellers_gear.perfect_dodge": "공격을 회피함",
    "subtitles.twilightforest.item.travellers_gear.side_step": "옆걸음을 함",
    "subtitles.twilightforest.item.travellers_gear.side_step_ready": "옆걸음이 재충전됨",
    "subtitles.twilightforest.item.travellers_gear.swap_hotbar": "허리띠가 바스락거림",
    "subtitles.twilightforest.item.travellers_goggles.zoom_in": "여행자 고글을 확대함",
    "subtitles.twilightforest.item.travellers_goggles.zoom_out": "여행자 고글을 축소함",
    "tag.item.c.ingots.wrought_iron": "연철 주괴",
    "tag.item.twilightforest.immune_to_thorns": "가시 피해 면역",
    "tag.item.twilightforest.scepters": "홀",
}

DRYING_RACKS = {
    "acacia": "아카시아나무",
    "bamboo": "대나무",
    "birch": "자작나무",
    "canopy": "캐노피나무",
    "cherry": "벚나무",
    "crimson": "진홍빛",
    "dark": "어둠나무",
    "dark_oak": "짙은 참나무",
    "jungle": "정글나무",
    "mangrove": "맹그로브나무",
    "mining": "광부나무",
    "oak": "참나무",
    "sorting": "분류나무",
    "spruce": "가문비나무",
    "time": "시간나무",
    "transformation": "변화나무",
    "twilight_oak": "황혼 참나무",
    "vangrove": "맹그로브나무",
    "warped": "뒤틀린",
}

TRAVELLER_EXACT = {
    "travellers_gear.info_indent": "  ⤷ ",
    "travellers_gear.modifier.empty": "비어 있음",
    "travellers_gear.ability": "능력: %s",
    "travellers_gear.broken": " (파손됨)",
    "travellers_gear.modifier.twilightforest.agile_ranger": "민첩한 궁수",
    "travellers_gear.modifier.twilightforest.agile_ranger.description": (
        "활 계열 아이템을 사용할 때도 정상 속도로 움직일 수 있습니다"
    ),
    "travellers_gear.modifier.twilightforest.all_night_goggles": "밤샘 고글",
    "travellers_gear.modifier.twilightforest.all_night_goggles.description": (
        "불면증과 엔더맨의 적대화를 막습니다"
    ),
    "travellers_gear.modifier.twilightforest.aquatic_agility": "수중 민첩성",
    "travellers_gear.modifier.twilightforest.aquatic_agility.description": (
        "호흡과 친수성 효과를 함께 제공합니다"
    ),
    "travellers_gear.modifier.twilightforest.arrow_magnetism": "화살 자력",
    "travellers_gear.modifier.twilightforest.arrow_magnetism.description": (
        "빗나간 화살을 회수합니다"
    ),
    "travellers_gear.modifier.twilightforest.auto_repair": "자동 수리",
    "travellers_gear.modifier.twilightforest.auto_repair.description": (
        "시간이 지나면 내구도를 수리합니다"
    ),
    "travellers_gear.modifier.twilightforest.double_jump": "이단 점프",
    "travellers_gear.modifier.twilightforest.double_jump.description": (
        "공중에서 한 번 더 점프할 수 있습니다"
    ),
    "travellers_gear.modifier.twilightforest.efficient_eater": "효율적인 식사",
    "travellers_gear.modifier.twilightforest.efficient_eater.description": (
        "이동으로 소모되는 허기를 줄입니다"
    ),
    "travellers_gear.modifier.twilightforest.gradual_glide": (
        "점진 활공 (웅크리기로 활성화)"
    ),
    "travellers_gear.modifier.twilightforest.gradual_glide.description": (
        "공중을 활공할 수 있습니다"
    ),
    "travellers_gear.modifier.twilightforest.haste": "성급함",
    "travellers_gear.modifier.twilightforest.haste.description": "성급함 II를 부여합니다",
    "travellers_gear.modifier.twilightforest.high_jump": "높이뛰기",
    "travellers_gear.modifier.twilightforest.item_display": (
        "아이템 표시 (단축키: ${tfkeybinds/key.twilightforest.item_display_map_cycle})"
    ),
    "travellers_gear.modifier.twilightforest.item_display.clock.unknown": (
        "시간 알 수 없음"
    ),
    "travellers_gear.modifier.twilightforest.item_display.compass.lodestone": (
        "%s (%s블록 거리)"
    ),
    "travellers_gear.modifier.twilightforest.item_display.description": (
        "고글에 아이템을 들고 우클릭해 표시 항목을 추가합니다"
    ),
    "travellers_gear.modifier.twilightforest.perfect_dodge": "완벽한 회피",
    "travellers_gear.modifier.twilightforest.perfect_dodge.description": (
        "30% 확률로 투사체를 회피합니다"
    ),
    "travellers_gear.modifier.twilightforest.red_thread_vision": (
        "붉은 실 시야 (단축키: ${tfkeybinds/key.twilightforest.red_thread_vision})"
    ),
    "travellers_gear.modifier.twilightforest.red_thread_vision.description": (
        "설치된 붉은 실을 볼 수 있습니다"
    ),
    "travellers_gear.modifier.twilightforest.side_step": "옆걸음",
    "travellers_gear.modifier.twilightforest.side_step.description": (
        "%s 또는 %s을(를) 두 번 눌러 돌진합니다"
    ),
    "travellers_gear.modifier.twilightforest.slimy_soles": "끈적한 밑창",
    "travellers_gear.modifier.twilightforest.slimy_soles.description": (
        "몸을 튕겨 낙하 피해를 막습니다"
    ),
    "travellers_gear.modifier.twilightforest.stealth": "은신 (웅크리기로 활성화)",
    "travellers_gear.modifier.twilightforest.stealth.description": (
        "웅크리면 투명해집니다"
    ),
    "travellers_gear.modifier.twilightforest.step_up": "자동 오르기",
    "travellers_gear.modifier.twilightforest.straight_ahead": "정면 돌파",
    "travellers_gear.modifier.twilightforest.straight_ahead.description": (
        "앞으로 이동하는 속도를 높입니다"
    ),
    "travellers_gear.modifier.twilightforest.swap_hotbar": (
        "단축바 교체 (단축키: ${tfkeybinds/key.twilightforest.swap_hotbar})"
    ),
    "travellers_gear.modifier.twilightforest.swap_hotbar.description": (
        "단축바를 보관하고 꺼낼 수 있습니다"
    ),
    "travellers_gear.modifier.twilightforest.swap_hotbar_ability": (
        "단축바 교체 (단축키: ${tfkeybinds/key.twilightforest.swap_hotbar})"
    ),
    "travellers_gear.modifier.twilightforest.swift_swim": "빠른 수영",
    "travellers_gear.modifier.twilightforest.unrestrained": "구속 해제",
    "travellers_gear.modifier.twilightforest.unrestrained.description": (
        "블록 때문에 이동 속도가 느려지는 것을 막습니다"
    ),
    "travellers_gear.modifier.twilightforest.water_walk": "수상 보행",
    "travellers_gear.modifier.twilightforest.water_walk.description": (
        "물 위를 걸을 수 있습니다"
    ),
    "travellers_gear.modifier.twilightforest.zoom": (
        "확대/축소 (단축키: ${tfkeybinds/key.twilightforest.zoom})"
    ),
    "travellers_gear.shift_info": "정보를 보려면 %s을(를) 누르세요",
}

TIP_EXACT = {
    "twilightforest.tips.alpha_yeti": (
        "알파 설인이 날뛰면 천장의 블록이 떨어져 나옵니다. 떨어지는 고드름을 "
        "조심하세요!"
    ),
    "twilightforest.tips.baby_jockey": (
        "아기 스켈레톤 드루이드가 떼거미를 타고 나타나기도 합니다."
    ),
    "twilightforest.tips.berry_bushes": (
        "The Twilight Forest 곳곳에서 베리 덤불을 발견할 수 있습니다."
    ),
    "twilightforest.tips.candelabra": (
        "촛대에 레드스톤 가루를 사용하면 불꽃이 붉게 변하고 레드스톤 신호를 냅니다."
    ),
    "twilightforest.tips.casket_logging": (
        "유품 상자는 유체와 상호작용하면 물이나 용암에 잠기거나 블록으로 둘러싸일 수 "
        "있습니다."
    ),
    "twilightforest.tips.casket_usage": (
        "유품 상자는 사용 횟수가 제한된 묘비 역할을 합니다. 사망할 때 인벤토리에 "
        "있으면 스스로 설치되어 모든 아이템을 보관합니다."
    ),
    "twilightforest.tips.clouds": (
        "비구름과 눈구름으로 날씨 효과를 흉내 낼 수 있습니다!"
    ),
    "twilightforest.tips.craft_travellers_gear": (
        "처리된 가죽을 건조해 무두질한 가죽으로 만들면 여행자 장비를 제작할 수 "
        "있습니다."
    ),
    "twilightforest.tips.emperors_cloth": (
        "황제의 옷감을 방어구와 조합하면 그 방어구가 보이지 않게 됩니다."
    ),
    "twilightforest.tips.essence_charge": (
        "무생물의 에센스를 홀과 조합하면 홀을 완전히 충전합니다."
    ),
    "twilightforest.tips.feather_fan": (
        "공작 깃털 부채로 몹을 밀어낼 수 있고, 점프하면서 사용하면 자신을 공중으로 "
        "띄울 수 있습니다. 겉날개와 철퇴에도 잘 어울립니다!"
    ),
    "twilightforest.tips.giant_block": (
        "거인의 곡괭이로 같은 블록의 4x4x4 영역을 채굴하면 거대 블록 1개가 "
        "드롭됩니다."
    ),
    "twilightforest.tips.jerky": "건조대에서 고기를 말리면 육포가 됩니다.",
    "twilightforest.tips.key_biome_locations": (
        "진행 생물 군계 무리는 서로 약 600블록 떨어져 생성되므로 다음 보스가 지나치게 "
        "멀리 있지는 않습니다."
    ),
    "twilightforest.tips.key_biomes": (
        "진행 생물 군계는 일반 보스 하나를 미니보스 넷이 둘러싼 무리로 생성됩니다."
    ),
    "twilightforest.tips.lich_deflection": (
        "황혼의 리치는 보호막이 사라진 뒤 황혼의 홀 투사체를 튕겨 냅니다."
    ),
    "twilightforest.tips.maze_map_focus": (
        "미노타우로스가 가끔 미로 지도 초점을 드롭하며, 이것으로 미로 지도를 만들 수 "
        "있습니다."
    ),
    "twilightforest.tips.minion_buff": (
        "황혼의 리치가 투사체로 자신의 부하를 맞히면 그 부하가 더 강하고 빨라집니다. "
    ),
    "twilightforest.tips.minoshroom": (
        "미노버섯 가까이에 오래 머물면 내려찍기 공격을 합니다."
    ),
    "twilightforest.tips.modify_travellers_gear": (
        "여행자 장비는 부위마다 기본 능력 1개가 있고, 부위당 최대 3개를 더 추가할 수 "
        "있습니다."
    ),
    "twilightforest.tips.mystic_crown": (
        "신비한 왕관을 착용하면 홀의 성능이 조금 향상됩니다."
    ),
    "twilightforest.tips.nether_bushes": (
        "낯선 물건과 재료뿐 아니라 기묘한 식물도 어둠의 탑에 뿌리를 내렸습니다."
    ),
    "twilightforest.tips.ominous_fire": "불길한 불은 생물을 언데드로 바꿀 수 있습니다.",
    "twilightforest.tips.ore_meter": (
        "광석 측정기를 켜면 주변의 모든 광석을 표시합니다. 특정 블록에 웅크린 채 "
        "우클릭하면 그 블록만 대상으로 지정해 주변 개수만 표시할 수도 있습니다. "
    ),
    "twilightforest.tips.oreberries": (
        "금속 오어베리 덤불은 지하에서 드물게 생성됩니다."
    ),
    "twilightforest.tips.parrying": (
        "타이밍에 맞춰 방패로 막으면 투사체를 몹에게 튕겨 낼 수 있습니다."
    ),
    "twilightforest.tips.phantoms": (
        "기사 유령은 보이지 않을 때 받는 피해가 크게 줄어듭니다. 전투할 때는 보이는 "
        "유령을 노리세요!"
    ),
    "twilightforest.tips.pocket_watch": (
        "토끼의 회중시계는 단축바에 있으면 이동 속도를 높이고, 손에 들면 채굴 속도를 "
        "높입니다."
    ),
    "twilightforest.tips.potion_flask": (
        "물약 플라스크에는 같은 물약을 최대 3회분까지 담을 수 있습니다."
    ),
    "twilightforest.tips.renewal": (
        "재생 마법이 부여된 홀은 플레이어 인벤토리의 필수 아이템을 사용해 스스로 "
        "재충전합니다."
    ),
    "twilightforest.tips.the_lore": (
        "이야기는 모두 여기에 있습니다. 직접 실마리를 풀어 보세요!"
    ),
    "twilightforest.tips.the_walls": (
        "죽음의 책이 벽 속에 있습니다. 바로 당신의 벽 속에요."
    ),
    "twilightforest.tips.trophy_pedestal": (
        "트로피 받침대는 활성화한 뒤에만 채굴할 수 있습니다."
    ),
    "twilightforest.tips.uncrafting_table": (
        "분해 작업대는 아이템을 분해하는 데만 쓰이지 않습니다. 아이템을 다른 것으로 "
        "재조합하고, 도구와 방어구를 수리하며, 장비 사이에 마법 부여를 옮길 수도 "
        "있습니다!"
    ),
    "twilightforest.tips.wrought_iron": (
        "연철 창살은 일반적인 방법으로 얻을 수 없으며, 연철로 만든 블록을 분해해야만 "
        "얻을 수 있습니다."
    ),
}

QUEST_OVERRIDES: dict[str, object] = {
    "quest.4193303999597249.quest_desc": [
        "&9The Twilight Forest&r는 황혼의 숲 차원을 게임에 추가하는 모드입니다. "
        "이 차원에는 완전히 새로운 아이템, 생물 군계, 몹과 보스가 가득합니다!\\n\\n"
        "&9황혼의 숲&r으로 가는 포털을 만들려면 땅에 2x2 구덩이를 파고 물을 "
        "채우세요. 구덩이 가장자리를 꽃으로 둘러싼 뒤 물에 다이아몬드를 던지세요."
        "\\n\\n제대로 만들었다면 토르가 신호를 보내고 포털이 활성화됩니다.\\n",
        "{image:atm:textures/questpics/gettingstarted/twilight_portal.png width:100 "
        "height:100 align:center fit:true}",
    ],
    "quest.30A61E1A1EFA81E6.quest_desc": [
        "&2강철잎&r은 엄밀히 말하면 주괴이며, &9&lThe Twilight Forest&r의 "
        "상자에서 발견할 수 있습니다. \\n방어구 부위마다 서로 다른 마법 부여가 "
        "적용됩니다!"
    ],
    "quest.52A29269A23F85B3.quest_desc": [
        "&9설인 방어구&r에는 알파 설인 털이 필요합니다. 예상하셨겠지만 알파 "
        "설인에게서만 나옵니다. \\n\\n그래도 이 방어구는 적을 얼어붙게 해 느리게 "
        "만듭니다!"
    ],
}

QUALITY_QUEST_OVERRIDES: dict[str, object] = {
    "quest.1452D9CF827782B5.quest_desc": [
        "극지 장비는 극지 털로 만들며, 극지 털은 겨울 늑대와 예티에게서 얻을 수 "
        "있습니다! \\n\\n아니요, 둘 다 털을 깎을 수는 없습니다. \\n\\n이 장비는 &7가죽 "
        "갑옷&r처럼 염색할 수 있습니다!"
    ],
    "quest.3061B67330367CE2.quest_desc": [
        "히드라나 유어 가스트를 처치했다면 &4파이어리 눈물/피&r를 얻을 수 있습니다. "
        "둘 중 어느 것이든 쓸 수 있습니다! \\n\\n&4파이어리 병&r 중 하나로 철 갑옷을 "
        "업그레이드하면 &4파이어리 갑옷&r을 만들 수 있습니다. \\n\\n이 갑옷은 "
        "&c네더라이트&r보다 강하고, 착용자를 공격한 적에게 불을 붙입니다!"
    ],
    "quest.3215A3D706CECCEF.quest_desc": [
        "생뿌리, 철 주괴, &e금 조각&r을 조합하면 &7아이언우드&r를 만들 수 있습니다! "
        "\\n\\n재료를 얻으려면 도끼와 곡괭이가 필요할 거예요. \\n\\n모든 &7아이언우드 "
        "갑옷&r에는 보호 마법이 기본으로 부여됩니다!"
    ],
    "quest.52A29269A23F85B3.quest_desc": [
        "&9예티 방어구&r에는 알파 예티 털이 필요합니다. 예상하셨겠지만 알파 "
        "예티에게서만 나옵니다. \\n\\n그래도 이 방어구는 적을 얼어붙게 해 느리게 "
        "만듭니다!"
    ],
    "quest.7D1A27CBF1508712.quest_desc": [
        "&3눈의 여왕&r은 빙하 생물 군계의 &b오로라 궁전&r에 살고 있습니다.\\n\\n"
        "빙하 생물 군계에 들어가려면 알파 예티를 처치해야 합니다.\\n\\n왕좌에서 "
        "끌어내리면 트로피를 비롯한 수많은 전리품을 떨어뜨립니다!"
    ],
    "quest.0107D516E038E0DB.quest_desc": [
        "&e리치 탑&r은 &e리치&r의 거처입니다! 전투는 3단계로 진행됩니다.\\n\\n"
        "1단계: &e리치&r는 방패로 몸을 감싸고 가스트의 화염구처럼 날아오는 "
        "&5엔더 진주&r로 공격합니다. 진주를 &e리치&r에게 되받아쳐 방패를 부수세요! "
        "방패가 깨질수록 분신을 보내 시선을 돌립니다.\\n\\n2단계: &e리치&r는 홀을 "
        "바꾸어 전투를 도울 좀비를 소환합니다. 방어가 사라졌으니 근접 공격을 할 수 "
        "있습니다!\\n\\n3단계: 홀의 충전량을 모두 쓰면 &e금 검&r으로 바꾸고 광분합니다. "
        "서둘러 처치하세요!"
    ],
    "quest.01748C2CD9C97523.quest_desc": [
        "&c재등장 블록&r은 아주 멋진 문처럼 작동합니다. 우클릭하면 잠시 사라졌다가 "
        "다시 나타납니다.\\n\\n&c소멸 블록&r은 우클릭하면 사라지며, 다시 나타나지 "
        "않습니다."
    ],
    "quest.01748C2CD9C97523.title": "&c재등장 \\\\\\& 소멸 블록",
    "quest.04440BB2EFFD6DD9.quest_desc": [
        "늪지 미궁 깊은 곳에는 거대한 &c미노시룸&r이 있습니다.\\n\\n처치하면 "
        "&e미프 스트로가노프&r를 떨어뜨립니다. 다음 지역을 열려면 이것을 먹어야 "
        "합니다."
    ],
    "quest.04440BB2EFFD6DD9.title": "&c강력한 미프 스트로가노프!",
    "quest.0A207A437AF153AA.quest_desc": [
        "&2팬텀 갑옷&r은 &2기사 유령&r의 전리품 상자에서 발견할 수 있습니다."
    ],
    "quest.1FF5906DF721D091.quest_desc": [
        "&2히드라&r는 &c파이어리 갑옷&r 제작에 쓰이는 &c파이어리 피&r를 "
        "떨어뜨립니다.\\n\\n방어구 한 벌을 모두 착용하면 공격한 적에게 10초 동안 불이 "
        "붙습니다."
    ],
    "quest.20436AFCC7E6855D.quest_desc": [
        "마법의 콩과 양질의 흙을 준비한 뒤 고원 생물 군계에서 커다란 구름을 "
        "찾으세요.\\n\\n양질의 흙에 마법의 콩을 심으면 구름까지 닿는 콩나무가 "
        "자랍니다. 그곳에서 거인들을 만날 수 있습니다.\\n\\n계속 진행하려면 광부 "
        "거인을 처치하고 거인의 곡괭이를 얻어야 합니다."
    ],
    "quest.212EC1F41227184D.quest_desc": [
        "&e리치&r처럼 엔더 폭발을 쏘고 싶다면 &9황혼의 홀&r을 사용하세요!\\n\\n"
        "재충전하려면 제작 격자에서 &5엔더 진주&r와 조합하세요."
    ],
    "quest.212EC1F41227184D.title": "&9황혼의 홀",
    "quest.25906B43A198B72F.quest_desc": [
        "기사금속 갑옷&r은 기사금속 주괴로 만들 수 있으며, &2기사 유령&r의 전리품 "
        "상자에서도 발견할 수 있습니다."
    ],
    "quest.2A0B3C91D72E8B75.quest_desc": [
        "작은 예티와 겨울 늑대는 &6극지 방어구&r 제작에 쓰이는 극지 털을 "
        "떨어뜨립니다."
    ],
    "quest.3371570F189DF994.quest_desc": [
        "&6요새화의 홀&r은 몸 주위에 보호 방패를 소환합니다.\\n\\n재충전하려면 제작 "
        "격자에서 &6황금 사과&r와 조합하세요."
    ],
    "quest.3371570F189DF994.quest_subtitle": "방패를 소환합니다",
    "quest.3371570F189DF994.title": "&6요새화의 홀",
    "quest.3531B28F14CF72A2.quest_desc": [
        "&9황혼의 숲&r 모험에서 처음 처치할 보스는 안뜰에 있습니다.\\n\\n&2나가&r는 "
        "여러 마디로 이루어진 초록색 뱀이며, 피해를 줄수록 마디가 사라집니다.\\n\\n"
        "&2나가&r를 처치하면 좋은 아이템과 함께 다음 보스인 리치의 거처에 들어갈 "
        "자격을 얻습니다."
    ],
    "quest.3908F7C80154D9CA.quest_desc": [
        "자신만의 &2좀비&r를 소환하고 싶지 않은 사람이 있을까요? 그래서 &2좀비의 "
        "홀&r이 있습니다!\\n\\n재충전하려면 제작 격자에서 &c썩은 살점&r과 "
        "조합하세요."
    ],
    "quest.3908F7C80154D9CA.title": "&2좀비의 홀",
    "quest.3C8724C3A9459507.quest_desc": [
        "예티 갑옷은 알파 예티 털로 제작할 수 있습니다."
    ],
    "quest.3DCF26B53AE1EBF6.quest_desc": [
        "&2어두운 숲&r에는 지하로 이어지는 구조물이 있습니다.\\n\\n들어가려면 근처 "
        "받침대에 지금까지 얻은 보스 트로피 중 하나를 올려놓으세요. 어떤 트로피든 "
        "괜찮으며 다시 회수할 수 있습니다.\\n\\n3층에서 기사 유령들을 찾을 수 있습니다. "
        "모두 처치하면 다음 보스가 열립니다."
    ],
    "quest.4B95D48D7525FFAD.quest_desc": [
        "&2늪&r으로 갈 시간입니다! &2늪&r에는 꼭대기에 입구가 난 기묘한 언덕이 있습니다. "
        "바로 &c미노시룸 미궁&r입니다!\\n\\n안에서는 &e미로 지도 초점&r을 떨어뜨리는 "
        "새로운 적들을 만납니다. 초점은 &e미로 지도&r를 만드는 데 필요합니다.\\n\\n"
        "미로 지도는 &c미노시룸 미궁&r 안의 길을 기록하는 특별한 지도입니다. 여기서는 "
        "미니맵도 힘을 쓰지 못합니다.\\n\\n미궁 전용 전리품이 든 방도 여럿 있습니다!"
    ],
    "quest.4DA0725E089D7C91.quest_desc": [
        "&c퀘&6스&e팅&2 &3램&9을 &5찾&c아 &6보&e세&2요&r. &c무&6지&e개&2색 "
        "&3양&9털&5을 &6모&e두 &2먹&3이&r면 풍성한 보상을 줍니다(16색).\\n\\n힌트: 퀘스팅 램이 "
        "있는 폐허에서 머리 위를 살펴보세요. 발사기가 도움이 될 수 있습니다."
    ],
    "quest.4DA0725E089D7C91.title": (
        "&c퀘&6스&e팅 &2램&3의 &9화&5려&c한 &6변&e신&2!&3!"
    ),
    "quest.4F66DF6B494BEFF3.quest_desc": [
        "&8까마귀 깃털&r, &e토치베리&r, &6발광석&r을 조합하면 &e마법 지도 "
        "초점&r을 얻을 수 있습니다."
    ],
    "quest.4F66DF6B494BEFF3.title": "&e마법 지도 초점",
    "quest.51BC981AB4CFAD95.quest_desc": [
        "미로 파괴자는 미궁에서 드물게 발견되는 특별한 곡괭이입니다.\\n\\n다른 곡괭이는 "
        "미로 벽을 부술 때 내구도가 16만큼 닳지만, 이 곡괭이는 1만 닳습니다!"
    ],
    "quest.575E405B270BBCBC.quest_desc": [
        "&9황혼의 숲&r에는 발견할 새로운 생물이 아주 많습니다.\\n\\n그중에서도 특히 "
        "성가신 매미를 처치해 보세요. 다른 황혼의 숲 몹을 처치해도 과제는 완료됩니다."
    ],
    "quest.58BD1063A19777DC.quest_desc": [
        "&2고원&r 생물 군계를 열었다면 트롤을 찾아 처치하세요.\\n\\n트롤은 &9마법의 "
        "콩&r을 떨어뜨릴 수 있습니다. 상자에서는 마법의 콩을 키우는 데 필요한 양질의 "
        "흙도 찾을 수 있습니다."
    ],
    "quest.5FE4DAE8F41B1437.quest_desc": [
        "&c광석 자석&r은 석탄을 제외하고 이름에 광석이 들어간 블록을 땅속에서 끌어올릴 "
        "수 있습니다.\\n\\n&2속 빈 언덕&r의 상자에서 찾을 수 있습니다."
    ],
    "quest.60FC2DAEA954A849.quest_desc": [
        "&6월충 여왕&r은 횃불 발사기처럼 작동합니다. 대상 블록에 &e월충&r을 쏘아 "
        "횃불처럼 빛나게 합니다.\\n\\n일부 &2속 빈 언덕&r과 &e리치 탑&r의 전리품 "
        "상자에서 찾을 수 있습니다."
    ],
    "quest.610F9E9D0B5131C7.quest_desc": [
        "&6보존의 부적 I&r은 사망할 때 주로 쓰는 손과 보조 손에 든 아이템, 착용 중인 "
        "갑옷을 잃지 않게 해 줍니다."
    ],
    "quest.688C911ECFB2F134.quest_desc": [
        "&2어두운 숲&r 안에는 &8어둠의 탑&r이 있습니다.\\n\\n입구 바닥의 재등장 "
        "블록을 찾아 들어간 뒤, 미로를 통과해 꼭대기 층의 &c유어 가스트&r와 "
        "싸우세요.\\n\\n&c유어 가스트&r는 원거리 무기로 상대하는 것이 좋습니다. 보스 "
        "층의 가스트 함정 4개를 이용하면 &c유어 가스트&r에게 큰 피해를 줄 수 있습니다.\\n\\n함정은 "
        "&c가스트링&r을 처치해 충전한 뒤 레드스톤 신호로 작동시킵니다. 반드시 사용할 "
        "필요는 없지만 큰 도움이 됩니다."
    ],
    "quest.688C911ECFB2F134.quest_subtitle": "어두운 카미나이트 탑",
    "quest.6CB1BFBA10DF24E4.quest_desc": [
        "&c생명력 흡수의 홀&r로 적의 생명력을 흡수할 수 있습니다!\\n\\n재충전하려면 "
        "제작 격자에서 &c발효된 거미 눈&r과 조합하세요."
    ],
    "quest.6CB1BFBA10DF24E4.title": "&c생명력 흡수의 홀",
    "quest.6FD41DF7704466A4.quest_desc": [
        "알파 예티를 처치하면 &9빙하&r 생물 군계가 열립니다. 이곳에는 귀여운 펭귄과 "
        "&3눈의 여왕&r이 있습니다.\\n\\n&b오로라 궁전&r 꼭대기에서 &3눈의 "
        "여왕&r은 자신을 보호할 얼음 수정을 소환합니다.\\n\\n바닥을 부수고 큰 피해를 주는 "
        "&3얼음&r 공격도 사용합니다.\\n\\n몸의 아래쪽은 &3얼음&r으로 보호되므로 위쪽만 "
        "공격할 수 있습니다.\\n\\n&3눈의 여왕&r을 처치하면 &2고원&r으로 갈 수 "
        "있습니다."
    ],
    "quest.730AF9210F00018E.quest_desc": [
        "&b다이아몬드 미노타우로스 도끼&r는 &c미노시룸&r이 떨어뜨립니다. 달리면서 "
        "공격하면 더 큰 피해를 줍니다."
    ],
    "quest.730AF9210F00018E.title": "&b미노타우로스 도끼",
    "quest.7B4A687EB505C2FF.quest_desc": [
        "&c카미나이트 구축기&r는 레드스톤 신호를 받으면 신호가 들어온 방향으로 임시 "
        "블록을 생성합니다.\\n\\n&c카미나이트 반응기&r는 주변의 흑요석과 네더랙을 "
        "&e가짜 금&r과 &3가짜 다이아몬드&r로 바꿉니다. 잠시 뒤 주변 블록을 빨아들인 "
        "후 폭발하며, &c카미나이트 가스트링&r을 생성합니다."
    ],
    "quest.7B4A687EB505C2FF.title": "&c카미나이트 구축기 \\\\\\& 반응기",
}

WOOD_NAMES = {
    "Canopy": "캐노피나무",
    "Dark": "어둠나무",
    "Mangrove": "맹그로브나무",
    "Mining": "광부나무",
    "Sorting": "분류나무",
    "Time": "시간나무",
    "Transformation": "변화나무",
    "Twilight Oak": "황혼 참나무",
}

COLORS = {
    "Black": "검은색",
    "Blue": "파란색",
    "Brown": "갈색",
    "Cyan": "청록색",
    "Gray": "회색",
    "Green": "초록색",
    "Light Blue": "하늘색",
    "Light Gray": "회백색",
    "Lime": "연두색",
    "Magenta": "자홍색",
    "Orange": "주황색",
    "Pink": "분홍색",
    "Purple": "보라색",
    "Red": "빨간색",
    "White": "흰색",
    "Yellow": "노란색",
}

FURNITURE = {
    "Display Case": "진열장",
    "Fancy Seat Back": "고급 의자 등받이",
    "Flat Seat Back": "평평한 의자 등받이",
    "Raised Seat Back": "돌출형 의자 등받이",
    "Small Seat Back": "소형 의자 등받이",
    "Tall Seat Back": "높은 의자 등받이",
    "Seat Back": "의자 등받이",
    "Seat": "의자",
    "Bookcase": "책장",
    "Fancy Armor Stand": "고급 갑옷 거치대",
    "Fancy Clock": "고급 시계",
    "Fancy Crafter": "고급 제작대",
    "Fancy Sign": "고급 표지판",
    "Grandfather Clock": "괘종시계",
    "Label": "라벨",
    "Potion Shelf": "물약 선반",
    "Shelf": "선반",
    "Table": "탁자",
    "Tool Rack": "도구 걸이",
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """JSON을 UTF-8 무BOM 형식으로 기록한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize_quality_value(value: object) -> object:
    """검수에서 확정한 공통 용어를 문자열과 SNBT 배열에 일관되게 적용한다."""
    if isinstance(value, str):
        for old, new in QUALITY_TEXT_REPLACEMENTS:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [normalize_quality_value(item) for item in value]
    return value


def translation_memory() -> tuple[dict[str, str], set[str]]:
    """신규 키와 현재 산출물을 제외한 기존 번역 기억을 만든다."""
    english = load_json(BASE_ROOT / "en_us.json")
    korean = load_json(BASE_ROOT / "ko_kr.json")
    sources = load_json(BASE_ROOT / "candidate_sources.json")
    values: dict[str, set[str]] = defaultdict(set)
    for key, source in english.items():
        target = korean[key]
        if (
            isinstance(source, str)
            and isinstance(target, str)
            and source != target
            and sources[key]
            not in {"new_translation_required", "project_output_review"}
        ):
            values[source].add(target)
    conflicts = {source for source, candidates in values.items() if len(candidates) > 1}
    memory = {
        source: next(iter(candidates))
        for source, candidates in values.items()
        if len(candidates) == 1
    }
    return memory, conflicts


def mask_text(text: str) -> tuple[str, list[str]]:
    """자동 번역에서 보존할 토큰을 본문과 분리한다."""
    protected: list[str] = []

    def replace(match: re.Match[str]) -> str:
        index = len(protected)
        protected.append(match.group(0))
        return f"ZXQPROTECTED{index}QXZ"

    return PROTECTED.sub(replace, text), protected


def restore_text(text: str, protected: list[str]) -> str:
    """보호 토큰을 원래 값으로 복원한다."""
    for index, value in enumerate(protected):
        token = f"ZXQPROTECTED{index}QXZ"
        if text.count(token) != 1:
            raise ValueError(f"자동 번역 보호 토큰이 바뀌었습니다: {token}:{text}")
        text = text.replace(token, value)
    if re.search(r"ZXQPROTECTED\d+QXZ", text):
        raise ValueError(f"복원되지 않은 보호 토큰이 있습니다: {text}")
    return text


def request_translation(source: str) -> str:
    """보호 처리한 영어 문장의 한국어 자동 번역 후보를 요청한다."""
    masked, protected = mask_text(source)
    query = urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": "ko", "dt": "t", "q": masked}
    )
    request = urllib.request.Request(
        f"{GOOGLE_TRANSLATE}?{query}",
        headers={"User-Agent": "ATM10-Korean-translation-candidate/1.0"},
    )
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            translated = "".join(row[0] for row in payload[0] if row and row[0])
            return restore_text(translated, protected)
        except Exception as exc:  # pragma: no cover - 외부 후보 서비스 오류 보고용
            last_error = exc
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"자동 번역 후보 요청 실패: {source}") from last_error


def build_candidates() -> dict[str, object]:
    """신규 키 248개의 보호된 자동 번역 후보를 만든다."""
    english = load_json(BASE_ROOT / "en_us.json")
    sources = load_json(BASE_ROOT / "candidate_sources.json")
    memory, conflicts = translation_memory()
    cache = load_json(CACHE_PATH) if CACHE_PATH.is_file() else {}
    candidates: dict[str, object] = {}
    candidate_sources: dict[str, str] = {}
    requests: set[str] = set()
    for key, value in english.items():
        if sources[key] != "new_translation_required":
            continue
        if not isinstance(value, str):
            raise TypeError(f"지원하지 않는 신규 값 자료형: {key}")
        if (
            family_goal.is_allowed_original(value)
            or key.startswith("jukebox_song.")
            or key.endswith(".author")
        ):
            candidates[key] = value
            candidate_sources[key] = "reviewed_original_candidate"
        elif value in memory and value not in conflicts:
            candidates[key] = memory[value]
            candidate_sources[key] = "family_memory_candidate"
        elif isinstance(cache.get(value), str):
            candidates[key] = cache[value]
            candidate_sources[key] = "automatic_cache_candidate"
        else:
            requests.add(value)
    failures: list[str] = []
    if requests:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(request_translation, source): source
                for source in sorted(requests)
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                except Exception as exc:  # pragma: no cover - 외부 오류 목록 보존
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_PATH, cache)
    if failures:
        raise RuntimeError("자동 번역 후보 생성 실패:\n" + "\n".join(failures))
    for key, value in english.items():
        if sources[key] != "new_translation_required" or key in candidates:
            continue
        translated = cache[value]
        assert isinstance(value, str) and isinstance(translated, str)
        errors = family_goal.validate_value(key, value, translated)
        if errors:
            raise ValueError("; ".join(errors))
        candidates[key] = translated
        candidate_sources[key] = "automatic_translation_candidate"
    write_json(BASE_ROOT / "auto_candidates.json", candidates)
    write_json(BASE_ROOT / "auto_candidate_sources.json", candidate_sources)
    report = {
        "scope": "The Twilight Forest 신규 언어 키 번역 후보",
        "candidate_counts": dict(sorted(Counter(candidate_sources.values()).items())),
        "protected_patterns": [
            "numbers",
            "placeholders",
            "URLs",
            "format codes",
            "keybind references",
            "line breaks",
        ],
        "current_output_self_reuse_excluded": True,
        "translation_memory_conflicts_excluded": len(conflicts),
        "review_status": "pending_manual_review",
    }
    write_json(WORK_ROOT / "auto_candidate_report.json", report)
    return report


def reviewed_new_value(key: str, source: str, candidate: str) -> str:
    """신규 후보를 키 문맥과 확정 용어에 맞게 최종 검수한다."""
    if key in NEW_EXACT:
        return NEW_EXACT[key]
    if key in TRAVELLER_EXACT:
        return TRAVELLER_EXACT[key]
    if key in TIP_EXACT:
        return TIP_EXACT[key]
    match = re.fullmatch(r"block\.twilightforest\.(.+)_drying_rack", key)
    if match and match.group(1) in DRYING_RACKS:
        return f"{DRYING_RACKS[match.group(1)]} 건조대"
    if key.startswith("jukebox_song.") or key.endswith(".author"):
        return source
    return candidate


def review_base_language() -> dict[str, object]:
    """현재 JAR·기존 프로젝트·신규 후보를 영어 원문과 대조한다."""
    english = load_json(BASE_ROOT / "en_us.json")
    korean = load_json(BASE_ROOT / "ko_kr.json")
    sources = load_json(BASE_ROOT / "candidate_sources.json")
    candidates = load_json(BASE_ROOT / "auto_candidates.json")
    before = dict(korean)
    for key, source in english.items():
        original = korean[key]
        if key.startswith("magic_painting.") and key.endswith(".author"):
            korean[key] = source
        elif key in QUALITY_LANGUAGE_OVERRIDES:
            korean[key] = QUALITY_LANGUAGE_OVERRIDES[key]
        elif key in FORMAT_FIXES:
            korean[key] = FORMAT_FIXES[key]
            sources[key] = "manual_review"
        elif sources[key] == "new_translation_required":
            candidate = candidates[key]
            if not isinstance(source, str) or not isinstance(candidate, str):
                raise TypeError(f"문자열이 아닌 신규 번역 후보: {key}")
            korean[key] = reviewed_new_value(key, source, candidate)
            sources[key] = "manual_review"
        korean[key] = normalize_quality_value(korean[key])
        if korean[key] != original and sources[key] != "manual_review":
            sources[key] = "manual_quality_review"
        errors = family_goal.validate_value(key, source, korean[key])
        if errors:
            raise ValueError("; ".join(errors))
    changed_keys = [key for key in korean if korean[key] != before[key]]
    write_json(BASE_ROOT / "ko_kr.json", korean)
    write_json(BASE_ROOT / "candidate_sources.json", sources)
    return {
        "keys_reviewed": len(english),
        "keys_changed": sum(
            value in {"manual_review", "manual_quality_review"}
            for value in sources.values()
        ),
        "quality_keys": sum(
            value == "manual_quality_review" for value in sources.values()
        ),
        "changes_this_run": len(changed_keys),
        "source_counts": dict(sorted(Counter(sources.values()).items())),
    }


def review_quests() -> dict[str, object]:
    """전용 및 관련 FTB Quests의 표시 문구와 fallback 경로를 검수한다."""
    reviewed = 0
    changed = 0
    changes_this_run = 0
    for root in sorted((WORK_ROOT / "quests").glob("*")):
        korean_path = root / "ko_kr.json"
        source_path = root / "candidate_sources.json"
        if not korean_path.is_file():
            continue
        korean = load_json(korean_path)
        sources = load_json(source_path)
        before = dict(korean)
        for key, value in QUEST_OVERRIDES.items():
            if key in korean:
                korean[key] = value
                sources[key] = "manual_review"
        for key, value in korean.items():
            normalized = normalize_quality_value(value)
            if normalized != value:
                korean[key] = normalized
                sources[key] = "manual_quality_review"
        for key, value in QUALITY_QUEST_OVERRIDES.items():
            if key in korean and korean[key] != value:
                korean[key] = value
                sources[key] = "manual_quality_review"
        reviewed += len(korean)
        changed += sum(
            value in {"manual_review", "manual_quality_review"}
            for value in sources.values()
        )
        changes_this_run += sum(korean[key] != before[key] for key in korean)
        write_json(korean_path, korean)
        write_json(source_path, sources)
    return {
        "keys_reviewed": reviewed,
        "keys_changed": changed,
        "changes_this_run": changes_this_run,
    }


def review() -> dict[str, object]:
    """언어와 퀘스트 검수 결과를 한 보고서로 기록한다."""
    report = {
        "family": "The Twilight Forest",
        "language": review_base_language(),
        "ftbquests": review_quests(),
    }
    write_json(WORK_ROOT / "manual_review_report.json", report)
    return report


def translate_bibliowoods_value(source: str) -> str:
    """Twilight Forest 목재 가구 이름을 확정 사전으로 조합한다."""
    color = ""
    remainder = source
    for english, korean in sorted(COLORS.items(), key=lambda row: -len(row[0])):
        if remainder.startswith(f"{english} "):
            color = korean
            remainder = remainder[len(english) + 1 :]
            break
    wood = ""
    for english, korean in sorted(WOOD_NAMES.items(), key=lambda row: -len(row[0])):
        if remainder.startswith(f"{english} "):
            wood = korean
            remainder = remainder[len(english) + 1 :]
            break
    if not wood or remainder not in FURNITURE:
        raise ValueError(f"Bibliowoods 이름 규칙을 해석할 수 없습니다: {source}")
    return " ".join(part for part in (color, wood, FURNITURE[remainder]) if part)


def build_bibliowoods() -> dict[str, object]:
    """Bibliowoods 중 Twilight Forest 목재 전용 1,256개 키만 생성한다."""
    instance = resolve_source_root()
    matches = sorted((instance / "mods").glob("bibliowoods-*.jar"))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Bibliowoods JAR 검색 결과가 하나가 아닙니다: {matches}"
        )
    with ZipFile(matches[0]) as archive:
        all_english = json.loads(
            archive.read("assets/bibliowoods/lang/en_us.json").decode("utf-8-sig")
        )
    english = {
        key: value for key, value in all_english.items() if "twilightforest" in key
    }
    korean = {key: translate_bibliowoods_value(value) for key, value in english.items()}
    sources = {key: "generated_reviewed_translation" for key in english}
    root = WORK_ROOT / "bibliowoods"
    write_json(root / "en_us.json", english)
    write_json(root / "ko_kr.json", korean)
    write_json(root / "candidate_sources.json", sources)
    output = OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json"
    write_json(output, korean)
    report = {
        "label": "Bibliowoods Legacy - Twilight Forest integration",
        "jar": matches[0].name,
        "all_english_keys": len(all_english),
        "twilight_forest_keys": len(english),
        "other_mod_keys_excluded": len(all_english) - len(english),
        "generated_reviewed_translations": len(korean),
        "output": output.relative_to(PROJECT_ROOT).as_posix(),
    }
    write_json(WORK_ROOT / "bibliowoods_scope.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("candidates", "review", "bibliowoods"))
    args = parser.parse_args()
    if args.command == "candidates":
        report = build_candidates()
    elif args.command == "review":
        report = review()
    else:
        report = build_bibliowoods()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
