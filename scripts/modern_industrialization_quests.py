#!/usr/bin/env python3
"""Modern Industrialization 전용·연관 FTB Quests를 번역하고 검증한다."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import sys
from pathlib import Path

from build_ae2_quests import validate_value
from five_family_goal import PROJECT_ROOT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/modern_industrialization/quests"
GROUPS = ("mi_steam", "mi_electric", "mi_digital", "mi_endgame", "related")

AUTOMATIC_FORGE_DESC = [
    "가장 중요한 &l멀티블록&r 중 하나입니다. 다른 &l멀티블록&r을 만드는 데 필요하기 때문입니다. \n\n&b유체 입력&r 해치(각 &b입력&r에는 &b유체&r 1종류만 들어가므로 여러 개가 필요함), &c에너지 입력&r 해치, &e아이템 입력&r 및 출력 해치가 필요합니다. \n\n이 해치로 &e아이템&r, &b유체&r와 &c에너지&r를 공급하면 다른 &5멀티블록 제어기&r처럼 아이템을 제작합니다! \n\n&6별 부품&r에 필요한 아이템도 제작합니다. &4피&f, &bAureal&f, 영혼과 &c에너지&r가 많이 필요합니다!",
    "{@pagebreak}",
    "{image:atm:textures/questpics/chap3/creative_forge1.png width:150 height:100 align:center}",
    "첫 번째 층은 간단합니다. &9광택 다크스톤 블록&f과 &9계단&r, &7룬 블록&r, &6비전 광택 다크스톤&r을 놓으세요. 가장 중요한 &5대장간 블록&r도 잊지 마세요!",
    "{image:atm:textures/questpics/chap3/creative_forge2.png width:150 height:100 align:center}",
    "다음 층에는 &9다크스톤&r &9블록&f, &9계단&f과 &9반 블록&r, &6금박 비전 광택 다크스톤&r 및 &6조각된 광택 비전 다크스톤&r을 놓습니다. &b비전 수정 오벨리스크&r 4개도 필요합니다!",
    "{image:atm:textures/questpics/chap3/creative_forge3.png width:150 height:100 align:center}",
    "이번 층은 쉽습니다. 중앙에 &9&l5등급 &6대장간&r을 정사각형으로 만들고, 2블록 떨어진 곳에 &6다크스톤 받침대&r 8개를 놓으세요.",
    "{image:atm:textures/questpics/chap3/creative_forge4.png width:150 height:100 align:center}",
    "추가할 블록이 없는 층은 건너뜁니다. 한 블록의 공간을 두고 &9&l5등급 &6대장간&r 위에 &7양자 주입기&r를 놓으세요. ",
    "{image:atm:textures/questpics/chap3/creative_forge5.png width:200 height:100 align:center}",
    "{image:atm:textures/questpics/chap3/creative_forge6.png width:200 height:100 align:center}",
    "마지막으로 해치를 몇 개 더 배치하세요. 반드시 필요합니다!",
]


TRANSLATIONS: dict[str, dict[str, object]] = {
    "mi_steam": {
        "quest.088CA7B6D4899846.quest_desc": [
            "&#65C2A6포장기&r는 &#53E67B이중 주괴&r, &#53E67B칼날&r과 &#53E67B케이블&r을 만드는 데 사용합니다. 이 밖에도 용도가 많지만, 당장은 이 세 가지가 가장 중요합니다."
        ],
        "quest.0DAF5D42694EA8C9.quest_desc": [
            "&#6E6D6D&n단조 망치&r에서 여정이 시작됩니다. 광석의 &#B53A3A생산량을 늘리고&r 이후 제작에 필요한 &#DBD25A부품&r을 만드는 등 용도가 많습니다.",
            "",
            "제작한 &7망치&r가 제작법에 꼭 필요하지는 않지만, &#DBD25A부품&r을 더 많이 생산할 수 있습니다.",
        ],
        "quest.0DAF5D42694EA8C9.title": "&#949494단조 망치",
        "quest.1036837C9AD3F301.quest_desc": [
            "&#6E6D6D단조 망치&r를 사용하면 &#FFAC3B구리&r 주괴나 광석을 쉽게 가루로 만들 수 있습니다."
        ],
        "quest.12F9705ACB8FB300.quest_desc": [
            "&#EDD653&n절단기&r로 다양한 아이템을 제작할 수 있습니다. 그중 중요한 것은 볼트입니다. ",
            "",
            "&#EDD653&n절단기&r는 &#E3993D윤활유&r를 사용하며, 윤활유는 &#EDD653&n혼합기&r로 만듭니다.",
        ],
        "quest.12FB3990CA1653A4.quest_desc": [
            "&#DBA15A증기 채굴 드릴&r은 게임 초반 채굴에 큰 도움이 됩니다. &53x3&r 범위를 채굴하고 &#EEF768섬세한 손길을 전환&r할 수 있습니다.",
            "",
            "기본값이 &7'Y'&r인 \"3x3 채굴 전환\" 키를 눌러 &53x3&r 채굴을 전환할 수 있습니다.",
            "",
            "증기 채굴 드릴을 들고 &7웅크린 채 우클릭&r하면 &#EEF768섬세한 손길&r을 전환합니다.",
            "",
            "&#DBA15A증기 채굴 드릴&r을 채우려면 인벤토리의 &6연료&r 위에 드릴을 놓고 &7우클릭&r하세요. &9물&r은 월드에서 &7우클릭&r하여 채우거나 물 양동이를 들고 다니면 됩니다.",
        ],
        "quest.1C9D3FC67D58AC02.quest_desc": [
            "&#EDD653&n혼합기&r를 사용하면 아이템과 유체를 혼합할 수 있습니다. 아이템을 염색하거나 복제하는 데도 사용합니다."
        ],
        "quest.1E4E462928F2A71C.quest_desc": [
            "&7&n코크스로&r는 &#787777석탄&r을 &#696464코크스&r로 바꿉니다. &#696464코크스&r는 &#787777석탄&r보다 연료 효율이 4배 높습니다. ",
            "",
            "주 손이나 보조 손에 &#D1D15E렌치&r를 들면 멀티블록 미리보기가 표시됩니다. &#B4D95D해치&r를 들면 해치를 놓을 수 있는 위치가 표시됩니다.",
            "",
            "&7&n코크스로&r는 대부분 벽돌로 이루어진 속이 빈 멀티블록입니다.",
        ],
        "quest.21A4FE1741E4E78C.quest_desc": [
            "&#65C2A6채석기&r는 자원을 생성하는 멀티블록입니다. 작동하려면 &a드릴&r과 &7증기&r가 필요합니다.",
            "",
            "작업할 때마다 &a드릴&r이 소모될 수 있습니다. 더 좋은 &a드릴&r일수록 더 좋은 자원을 얻습니다.",
            "",
            "증기 채석기는 &#DEA14B구리&r 및 &#DE9531청동 드릴&r만 사용할 수 있습니다. &#8A5C1E흙&r을 사용하여 돌을 만들 수도 있습니다.",
        ],
        "quest.21A4FE1741E4E78C.quest_subtitle": "무한 자원",
        "quest.23708582B1064C9D.quest_desc": [
            "&#46DBBB회로&r가 작동하려면 이 기본 부품들이 필요합니다. 나중을 위해 일부 부품을 자동화해 두면 좋습니다."
        ],
        "quest.23708582B1064C9D.title": "정전 용량과 저항",
        "quest.24285F25F9563B02.quest_desc": [
            "&#467FDB&n아날로그 회로&r를 드디어 만들었군요! 보통은 절반쯤 걸리지만, 늦었다고 뭐라고 하지는 않을게요..."
        ],
        "quest.24285F25F9563B02.quest_subtitle": "전자 공학의 기초",
        "quest.253822C64BBBB1EB.quest_desc": [
            "&#6E6D6D단조 망치&r를 사용하면 &#9AD5ED주석&r 주괴나 광석을 쉽게 가루로 만들 수 있습니다."
        ],
        "quest.357DDE894EB512F7.quest_desc": [
            "&#65C2A6선재 압연기&r는 정확한 힘을 가해 &#53E67B전선&r을 만듭니다. 짜릿하죠!!"
        ],
        "quest.3AA4D1B60E4E71A5.quest_desc": [
            "모든 &c멀티블록&r의 등급은 내부의 &e해치&r로 정해집니다. &c멀티블록&r의 &e해치&r를 업그레이드하면 기계 전체가 업그레이드됩니다."
        ],
        "quest.41877F44CD3D1EDB.quest_desc": [
            "&#E3BC19청동 화로&r는 일반 화로처럼 작동하지만 증기를 사용하며 속도가 두 배 빠릅니다."
        ],
        "quest.458BFDB636F8B495.quest_desc": [
            "코크스 가루와 철을 혼합하면 생강철 가루가 됩니다. 증기 용광로에서 구우면 이후 진행에 필요한 강철 주괴를 얻을 수 있습니다."
        ],
        "quest.478C1AF86610A8B7.quest_desc": [
            "&#EDD653&n압축기&r는 &#53EDAA판&r, &#53EDAA곡면 판&r과 &#53EDAA고리&r를 만드는 데 사용합니다."
        ],
        "quest.48F77A0BE1F33B29.quest_desc": [
            "새로 만든 &#65C2A6선재 압연기&r로 &#53E67B전선&r과 &#53E67B가는 전선&r을 만들면 전기 시대로 나아갈 수 있습니다."
        ],
        "quest.48F77A0BE1F33B29.title": "전선이 절실해",
        "quest.4E69C6ABFE467C25.quest_desc": [
            "&#65C2A6합금 제련기&r는 &#3187C4Extended Industrialization&r에서 추가됩니다. &#4C4BDE혼합기&r와 &#954BDE화로&r의 작업을 하나로 합쳐 번거로움을 줄여 줍니다."
        ],
        "quest.55C6BBC996B51838.quest_desc": [
            "&#ED9553청동 보일러&r는 &9물&r을 증기로 바꿉니다. 증기는 &7&n증기 시대&r 기계를 작동시키는 연료입니다.",
            "",
            "기계에 &9물&r과 &#ED5353화로 연료&r를 공급하면 온도가 올라갑니다. 최대 온도에서는 기계 4대를 동시에 작동시킬 수 있습니다.",
        ],
        "quest.55C6BBC996B51838.quest_subtitle": "물 끓이기",
        "quest.589DFDB8FB7211AA.quest_desc": [
            "&#C1DB46&n전기 시대&r로 나아가는 데 필요한 &7고무&r는 쉽게 생산할 수 있습니다. 일찍 자동화할수록 훨씬 수월하게 진행할 수 있습니다."
        ],
        "quest.589DFDB8FB7211AA.title": "고무와 회로 기판",
        "quest.5CCF92238B23EDC9.quest_desc": [
            "&#A0DE45&nModern Industrialization&r은 성격상 &#D93D3DIC2&r 및 &#D93D3DGregTech&r와 비슷하지만, 진행 방식은 이 2개 모드와 다릅니다.",
            "",
            "이 퀘스트에서는 &#E8C843AllTheMods Star&r와 이후의 &#43E898Infinity Armor&r에 필요한 부품을 만드는 과정을 안내합니다.",
        ],
        "quest.5CCF92238B23EDC9.quest_subtitle": "읽으면 도움이 됩니다",
        "quest.5CCF92238B23EDC9.title": "&#A0DE45Modern Industrialization에 오신 것을 환영합니다",
        "quest.5E191081662C2F1A.quest_desc": [
            "&#6E6D6D단조 망치&r는 &#A0DE45Modern Industrialization&r 주민의 작업소 블록입니다. 이 주민은 여러 유용한 거래를 제공합니다."
        ],
        "quest.68EAB0248989FC97.quest_desc": [
            "&#EDD653&n증기 용광로&r를 만들면 새로운 진행 단계가 열립니다. 앞으로도 중요한 멀티블록입니다.",
            "",
            "이 멀티블록은 &7강철 주괴&r를 만들 뿐 아니라 &#696E60원료 합성유&r를 &#494D43합성유&r로 처리합니다. 합성유는 나중에 &#36472A고무&r 등을 만드는 데 사용합니다.",
        ],
        "quest.7282DCB1547CEB63.quest_desc": [
            "&#ED9553청동&r은 &7&n증기 시대&r의 기반 재료입니다. 이 가루를 구우면 이후에 사용할 &#ED9553청동 주괴&r가 됩니다."
        ],
        "quest.7282DCB1547CEB63.title": "&#EDD653청동",
        "quest.7A873E48E38B5C0E.quest_desc": [
            "강철 기계는 청동 기계보다 증기를 두 배 사용하지만, 작동 속도도 두 배 빠릅니다."
        ],
        "quest.7D220876E8FF7AED.quest_desc": [
            "&#65C2A6포장 해제기&r는 &#53E67B블록을 주괴로 풀거나&r 기계의 &#53E67B부품을 재활용&r하는 등 용도가 많습니다.",
            "",
            "&o실리콘 주괴도 더 쉽게 얻을 수 있습니다.&r",
        ],
        "task.198A217D6A4C951C.title": "주민 거래",
        "task.31BE41B971794377.title": "강철 시대",
        "task.45C5CAC94406DF41.title": "멀티블록 등급",
    },
    "mi_electric": {
        "quest.068128395837AF4F.quest_subtitle": "증기 기계와 동일",
        "quest.08C870DC50CA49FC.quest_desc": [
            "&#5C5C5C원유&r 자체는 쓸모가 많지 않지만 증류소에서 처리하면 여러 용도로 사용할 수 있는 물질을 얻습니다.",
            "",
            "원유에서 &#C4C241황산 중유&r, &#CECC5F황산 경유&r와 &#D9D782황산 나프타&r를 생산할 수 있습니다.",
        ],
        "quest.08C870DC50CA49FC.title": "&#5C5C5C원유 처리",
        "quest.0903F0D8642449B7.quest_desc": [
            "&6아날로그 회로&r에서 발전하여 이제 2비트보다 많은 정보를 처리할 수 있습니다. 새로운 기계들을 만들 수 있게 됩니다."
        ],
        "quest.0A9ADDE68342B987.quest_desc": [
            "&#43DEC2폴리에틸렌&r은 다음 화학 물질 처리 과정을 거쳐 만듭니다:",
            "",
            "&8원유&r -> &#D2CD2D황산 경유&r -> &#DBD658경유&r -> &#E2DF78증기 분해된 경유&r -> &#44D1DB에틸렌&r -> &#43DEC2폴리에틸렌&r.",
        ],
        "quest.0C94D76B87E49FFD.title": "철 처리",
        "quest.103728F2BAD5AE84.title": "고급 부품",
        "quest.1351D0594F1E6551.quest_desc": [
            "이 &#55EDA4기본 부품&r을 만들면 다음 처리 기술의 돌파구가 열립니다."
        ],
        "quest.1351D0594F1E6551.title": "회로 부품",
        "quest.162807D14C173CB4.quest_desc": [
            "&#5599ED원심분리기&r는 충분히 빠르게 돌리면 새로운 물질이 튀어나온다는 이론을 증명합니다. 용도가 많지만 주로 &#F2AAE5크롬&r과 &#AD3497모자나이트&r 처리에 필요합니다. "
        ],
        "quest.162807D14C173CB4.quest_subtitle": "빙글빙글 머리가 돌아가요...",
        "quest.1745124F83D033B9.title": "기본 부품",
        "quest.18C0EF38430C3E67.quest_subtitle": "디지털 시대",
        "quest.1A84DF4478D55C41.quest_subtitle": "증기 기계와 동일",
        "quest.1B4CD5AC8F6C3307.quest_desc": [
            "&#4497DB오버드라이브 모듈&r은 현재 제작법이 작동하지 않을 때도 기계의 효율을 유지합니다. 대신 기계를 해당 제작법에 고정합니다."
        ],
        "quest.1E0EF28175A7424F.quest_desc": [
            "이미 증기를 만들고 있으니 전기 생산에도 사용해 보세요. &#6363DB터빈&r을 설치하고 &7증기&r를 넣으면 &#DBDB63전기&r가 나옵니다."
        ],
        "quest.1E0EF28175A7424F.quest_subtitle": "증기 -> 전기",
        "quest.1F21B578FAF4CCAC.quest_subtitle": "증기 기계와 동일",
        "quest.1F3E18129B871C49.quest_subtitle": "증기 기계와 동일",
        "quest.22AD9DF2BCC04575.quest_subtitle": "에너지 만들기",
        "quest.22AD9DF2BCC04575.title": "전기 생산",
        "quest.256C3DBA392B4236.quest_desc": [
            "망간 및 크롬의 산성 용액을 전기분해하면 이후 제작법에 사용할 가루를 얻습니다."
        ],
        "quest.256C3DBA392B4236.quest_subtitle": "작은 가루 9개로 가루 1개",
        "quest.2EF0C033C540A7B1.title": "루비 처리",
        "quest.32D585D9F73CD9FD.quest_desc": [
            "&#EDDF55전기 용광로&r는 여러 자원을 제련할 수 있습니다. 제작법에 따라 구조물에 &#B8ED55특정 코일&r을 사용해야 합니다."
        ],
        "quest.374C06B3999BB0D3.quest_desc": [
            "&#C2C78B철&r, &#EDB2EA크롬&r, &#BEC9A3니켈&r과 &7망간&r을 혼합하면 &#ADF0EE스테인리스강 가루&r가 됩니다."
        ],
        "quest.3A03852E282DAA4D.quest_desc": [
            "&#ED8055전해조&r는 물질에 순간적으로 충분한 에너지를 가해 더 기본적인 자원으로 분해합니다."
        ],
        "quest.3B9D9CB589DB2003.quest_desc": [
            "&#71EBB4&nModern Industrialization&r 기계는 다른 모드와 다르게 작동합니다. 모든 기계에는 &#E5EB71효율 배수&r가 있으며, 같은 제작법을 계속 실행하면 증가합니다. &#E5EB71효율&r이 오르면 기계의 &#E5EB71속도&r도 증가하지만 &#E5EB71효율&r은 제작법이 바뀌면 초기화됩니다.",
            "",
            "부품을 계속 생산할 때는 기계 1대에 제작법 1개를 맡기는 것이 좋습니다. 이것이 이 모드가 의도한 플레이 방식이며, 나중에 업그레이드로 개선할 수 있습니다.",
            "",
            "{image:atm:textures/questpics/modernindustrialization/prod_line.png width:100 height:100 align:center}",
            "",
            "{@pagebreak}",
            "이 모드의 모든 기계는 FE를 전력으로 받을 수 있습니다. &c16 FE&r는 &#E1EB591 EU&r로 변환됩니다.",
        ],
        "quest.3B9D9CB589DB2003.quest_subtitle": "알아 두면 유용합니다",
        "quest.3CE72DAF431269CD.quest_desc": [
            "&#D6AC2F자화기&r는 넣은 재료를 자화합니다."
        ],
        "quest.401A3FD6A3511870.quest_subtitle": "열려라 참깨",
        "quest.401A3FD6A3511870.title": "논리 게이트",
        "quest.401B559649C54C5C.quest_desc": [
            "&#92CCF0수소&r와 &#519BC9염소&r를 혼합하면 &#4FB373염산&r이 됩니다. 염산은 &#F2A0E1크롬 가루&r를 처리할 때 사용합니다."
        ],
        "quest.408EBED932656006.quest_desc": [
            "&7실리콘&r을 도핑하면 일반 &7실리콘&r보다 생산량이 크게 늘어납니다."
        ],
        "quest.408EBED932656006.title": "도핑된 실리콘",
        "quest.413F338DB07BA88C.quest_subtitle": "증기 기계와 동일",
        "quest.4A5A143A79809BB6.quest_desc": [
            "드디어 만들었군요. 전기 시대에 오신 것을 환영합니다. 이제 진짜 모험이 시작됩니다.",
            "",
            "먼저 배터리를 만들기 위한 배터리 합금이 필요합니다. 정말 짜릿하죠.",
        ],
        "quest.4A5A143A79809BB6.quest_subtitle": "배터리 합금",
        "quest.4A5A143A79809BB6.title": "전기 시대",
        "quest.4E7B1B16C7CDA84C.quest_subtitle": "증기 기계와 동일",
        "quest.532BCAB3FBF91B1D.quest_desc": [
            "&#44DB9C업그레이드&r는 기계가 더 높은 &#4467DB오버클럭&r 상태에 도달하도록 하여 최대 속도를 높입니다.",
            "",
            "기계에는 모든 등급의 업그레이드를 최대 한 스택까지 넣을 수 있습니다. &#CEDB44기본 업그레이드&r는 개당 최대 처리량을 &#F7F448+2EU/t&r만큼 늘립니다.",
        ],
        "quest.548274CC00E67EC4.quest_desc": [
            "전기 전송은 간단합니다. &#F5B027발전기&r와 &#3CC1FA기계&r 사이를 케이블로 연결하세요. LV 케이블은 최대 &#EEFA3C256 EU/t&r를 전송합니다."
        ],
        "quest.548274CC00E67EC4.quest_subtitle": "케이블 전송 한계",
        "quest.548274CC00E67EC4.title": "LV 케이블",
        "quest.54CE9493B63620C4.quest_desc": [
            "&#AC59EB디젤 발전기&r는 여러 액체 연료를 전기로 바꿉니다. 초반에 구하기 쉬운 연료는 &7크레오소트유&r와 &8합성유&r입니다."
        ],
        "quest.54CE9493B63620C4.quest_subtitle": "액체 연료 -> 전기",
        "quest.55BB4005BB4CA316.title": "모자나이트 처리",
        "quest.5A62260FB3850092.quest_desc": [
            "&e황&r, &#6ACDE6산소&r와 &9물&r을 혼합하면 &#D3D955황산&r이 됩니다. 황산은 &7망간 가루&r를 처리할 때 사용합니다."
        ],
        "quest.5AA8D2A1F3618615.quest_subtitle": "전기 옮기기",
        "quest.5B50AC47957F0CD7.quest_desc": [
            "&7석유 시추기&r는 &#7A7A7A셰일유&r와 &#918686원유&r를 시추합니다."
        ],
        "quest.5B50AC47957F0CD7.quest_subtitle": "독수리 울음소리",
        "quest.5D404ED40C6C2690.quest_subtitle": "더 많은 전력 입력",
        "quest.604C003EE6B1CC6B.quest_subtitle": "증기 기계와 동일",
        "quest.6256612D46C88C0C.quest_desc": [
            "&#723CFA변압기&r는 전력을 한 전압 범위에서 다른 범위로 변환합니다. ",
            "",
            "&#EBC471LV&r-&#DDE548MV&r &#723CFA변압기&r: &#EBC471LV&r 전력을 &#DDE548MV&r 전력으로 변환하며 입력 5개와 출력 1개가 있습니다.",
            "",
            "&#DDE548MV&r-&#EBC471LV&r &#723CFA변압기&r: &#DDE548MV&r 전력을 &#EBC471LV&r 전력으로 변환하며 입력 1개와 출력 5개가 있습니다.",
        ],
        "quest.6256612D46C88C0C.quest_subtitle": '"자유는 모든 지각 있는 존재의 권리다"',
        "quest.6256612D46C88C0C.title": "LV-MV 변압기",
        "quest.6647A9652EFDDCDF.quest_desc": [
            "&#ADF0EE뜨거운 스테인리스강 주괴&r를 &#56E3DF진공 냉각기&r에 넣어 식히면 사용할 수 있는 &#ADF0EE스테인리스강 주괴&r가 됩니다."
        ],
        "quest.66D4256F79D5B30B.quest_subtitle": "증기 기계와 동일",
        "quest.6A25ED4059E224D2.quest_desc": [
            "&#ED5585증류소&r는 특정 유체를 증류하여 용도에 더 알맞은 산출물을 만듭니다. ",
            "",
            "하나의 입력에서 여러 산출물이 나올 때 원하는 것을 얻으려면 제작법을 고정해야 합니다. GUI에서 자물쇠 아이콘과 화살표를 차례로 누른 뒤 원하는 제작법의 &7'+'&r 아이콘을 누르세요. ",
        ],
        "quest.6A25ED4059E224D2.quest_subtitle": "제작법 고정",
        "quest.6E7DF4AF86A036EC.title": "셰일유 처리",
        "quest.72FFD9E471242D68.quest_desc": [
            "스테인리스강은 일반 화로보다 높은 제련 온도가 필요합니다. 앞서 만든 전기 용광로를 사용해야 합니다."
        ],
        "quest.744E620B7DEBB483.quest_desc": [
            "&#27CFF5진공 냉각기&r는 &#E6AD1E뜨거운 주괴&r나 특정 유체를 냉각하여 이미 생산하던 아이템의 수율을 높입니다."
        ],
        "quest.744E620B7DEBB483.quest_subtitle": "차갑게 식히기",
        "quest.76660075F254597E.quest_desc": [
            "&#F5B758고급 업그레이드&r는 개당 최대 사용량을 &#EDE02F16 EU/t&r만큼 늘립니다."
        ],
        "quest.7E3B19796870C2B1.quest_desc": [
            "&#9955ED화학 반응로&r는 앞으로 가장 유용하게 사용할 기계 중 하나로, 여러 화학 물질을 만듭니다."
        ],
        "quest.7EDBE88A2CFAB353.quest_desc": [
            "&#562FD6조립기&r는 다양한 부품과 기계를 자동으로 제작합니다.",
            "이미 사용한 일부 제작법을 &a훨씬 저렴하게&r 처리하기도 합니다.",
        ],
        "quest.7EDBE88A2CFAB353.quest_subtitle": "여러 대가 필요합니다",
        "quest.7FE5864E59D7B827.quest_desc": [
            "&#6784EB외피&r는 기계가 받을 수 있는 전력량을 제한합니다. 업그레이드를 넣을수록 더 많은 전력을 받도록 높은 등급의 &#6784EB외피&r가 필요합니다. &#6784EB외피&r 등급은 연결할 수 있는 케이블에도 영향을 줍니다."
        ],
        "quest.7FE5864E59D7B827.quest_subtitle": "기본 구성 요소",
        "task.12433760FD40CB3A.title": "주의 깊게 읽으세요",
        "task.1489DD401D237541.title": "전기",
        "task.1FE598387B609AE5.title": "전기 전송",
    },
    "mi_digital": {
        "quest.00C95A190BE2CBF9.quest_desc": [
            "&#994ABA스티렌&r을 얻으려면 &#C2C969철 가루&r를 &#69C9B6에틸벤젠&r 및 증기와 반응시켜야 합니다. &#69C9B6에틸벤젠&r은 &#CDCF95증기 분해된 나프타&r를 증류하여 만듭니다."
        ],
        "quest.00C95A190BE2CBF9.title": "고급 증류",
        "quest.011B8BD02D80DDD4.quest_desc": [
            "월드 곳곳에서 &#6E2D6E텅스텐 광석&r을 쉽게 찾을 수 있습니다. 캐면 &#A140A1텅스텐 원석&r을 얻습니다."
        ],
        "quest.024BD22824C7F53A.quest_desc": [
            "&#F0C87D증기 분해된 나프타&r를 증류하면 &#8FD5E3톨루엔&r을 얻습니다."
        ],
        "quest.09BE81548CD81068.quest_desc": [
            "드디어 &#FFEB6EAllthemods Star&r에 필요한 부품을 만들 단계에 도달했습니다!!"
        ],
        "quest.0B60DA8F65E5DF06.quest_desc": [
            "&#A140A1텅스텐 원석&r을 여러 방법으로 분쇄하여 &#C452C4텅스텐 가루&r를 얻을 수 있습니다."
        ],
        "quest.0C229BE9B57269EF.quest_desc": [
            "&#EBA844칸탈 가루&r는 &#816DF7전기 용광로&r에서 제련해야 합니다."
        ],
        "quest.0CD36928116E868E.quest_desc": [
            "&#F783F3염화 비닐&r에 &#9683F7작은 납 가루&r 또는 &#FEA8FF작은 크롬 가루&r를 혼합하면 &#F36EF5폴리염화비닐&r이 됩니다."
        ],
        "quest.0EA327E405EDFF02.quest_desc": [
            "&#9C6C35아세틸렌&r과 &#DEAB6D염산&r을 혼합하면 &#F783F3염화 비닐&r이 됩니다."
        ],
        "quest.1A83615B7E1D3540.quest_desc": [
            "연료가 든 &#45BF56원자로&r에 &9물&r을 넣으면 &#8F49C4중수소&r를 얻습니다. 다른 방법도 있지만 &#45BF56원자로&r가 가장 빠릅니다."
        ],
        "quest.226187AA3F1B6DB1.quest_desc": [
            "&#D4C35D모래&r, &8부싯돌&r, &#8DF0EE질소&r와 &#69C9C7톨루엔&r을 혼합하면 &#D66D40산업용 TNT&r가 됩니다."
        ],
        "quest.22B8D57337944D9C.quest_desc": [
            "이제 &#DF9DE0뜨거운 티타늄 주괴&r를 &#5CD1CF진공 냉각기&r에서 식혀 사용할 수 있는 &#F069F0티타늄 주괴&r로 만들 수 있습니다."
        ],
        "quest.22B8D57337944D9C.title": "&#F069F0티타늄 주괴",
        "quest.23DB52ECA259F36D.quest_desc": [
            "&#45BF56원자로&r에서 중수를 처리하면 &#EB5266삼중수소&r와 &#C09EDE중수 증기&r가 생성됩니다.",
            "",
            "&#EB5266삼중수소&r는 고급 부품에 사용합니다. &#C09EDE중수 증기&r는 &#DEAB47열교환기&r에서 &#8C47C9중수&r로 재활용할 수 있습니다.",
        ],
        "quest.267A357B28228694.quest_desc": [
            "&#4DB85E랜덤 액세스 메모리&r는 &#5EC7E6화학 반응로&r에서 &#A1A1A1스티렌-부타디엔 고무&r, &#D15EE6아르곤&r, &7안티모니 가루&r, &#5ED2E6알루미늄 가루&r와 &#5D76C2실리콘 웨이퍼&r로 만듭니다."
        ],
        "quest.282A23C3E7561796.quest_desc": [
            "&#94C0E3처리 배열&r은 여러 기계를 병렬로 작동하는 것처럼 처리하는 대형 멀티블록입니다. 최대 병렬 작업 수는 &#94E3A264&r입니다.",
            "",
            "멀티블록을 만들려면 먼저 제어기 GUI에서 병렬로 모사할 기계 수를 선택하세요.",
            "",
            "{image:atm:textures/questpics/modernindustrialization/proc_array_gui.png width:175 height:100 align:center}",
            "",
            "{@pagebreak}",
            "사용하려는 기계를 GUI 오른쪽 슬롯에 넣으세요. 실행할 병렬 작업 수와 같은 수의 기계가 필요합니다.",
            "",
            "&#94C0E3처리 배열&r에는 일반적인 업그레이드도 모두 넣을 수 있습니다.",
        ],
        "quest.2A95F4F998835B43.quest_subtitle": "조각 9개 -> 주괴 1개",
        "quest.3003598CE8B1FAAA.quest_subtitle": "더 나은 기술",
        "quest.3003598CE8B1FAAA.title": "더욱 고급인 부품",
        "quest.31CB278B4BA7B25E.quest_desc": [
            "&#B5E7F7액화 공기&r를 원심분리하면 &#A5CAD9산소&r, &#78ADC2질소&r와 &#DD91ED아르곤&r, 총 3가지 산출물이 나옵니다. 이 &#DD91ED아르곤&r은 곧 사용합니다."
        ],
        "quest.31CB278B4BA7B25E.quest_subtitle": "그럴듯하네요",
        "quest.31CB278B4BA7B25E.title": "공기 원심분리",
        "quest.352A226915809E1B.quest_desc": [
            "이제 &#A57DE3포장기&r에서 &#7DD2E3스테인리스강&r, &#B37DE3텅스텐&r과 &#E37DDB티타늄 주괴&r를 합쳐 새로운 &#3946E3혼합 방폭 주괴&r를 만들 수 있습니다. "
        ],
        "quest.35FDC436DE07635F.quest_desc": [
            "&#DB62DE폭발 압축기&r는 폭발물의 힘으로 자원을 결합합니다. &#8762DE혼합 방폭 합금 주괴&r를 더 효율적으로 만드는 등 여러 유용한 자원을 생산합니다."
        ],
        "quest.3601DD545E1D11B4.quest_desc": [
            "&#DD91ED아르곤&r을 &#83729E실리콘 가루&r 및 &#AAA0BA작은 이리듐 가루&r와 반응시키면 &#919191단결정 실리콘&r이 됩니다.",
            "",
            "&#AAA0BA이리듐&r 광석은 오버월드에서 찾을 수 있습니다.",
        ],
        "quest.36D35C35BBC0A555.quest_subtitle": "가장 효율적인 방법",
        "quest.386ABEB4249D157D.quest_desc": [
            "&#919191단결정 실리콘&r 하나를 잘라 &#8FA4B5실리콘 웨이퍼&r 32개를 만들 수 있습니다."
        ],
        "quest.3891F8D4201E6BFD.quest_desc": [
            "&#EBA844칸탈 주괴&r를 가는 전선으로 가공하고 케이블 형태로 성형하여 &#EBA844칸탈 코일&r을 만듭니다. ",
            "",
            "&#EBA844칸탈 코일&r을 사용하면 &#816DF7전기 용광로&r가 훨씬 높은 &#F76D6D온도&r에서 작동하여 더 많은 제작법을 처리합니다.",
            "",
            "&#816DF7전기 용광로&r GUI에서 코일을 바꿔야 합니다.",
            "",
            "{image:atm:textures/questpics/modernindustrialization/switch_to_kanthal.png width:150 height:75 align:center}",
        ],
        "quest.39A0BA6E2A72A681.quest_desc": [
            "&#99F0F0스테인리스강&r, &#ADDBDB알루미늄&r과 &#E9A8F7크롬 가루&r를 혼합하면 &#EBA844칸탈 가루&r가 됩니다."
        ],
        "quest.3A0C8BCE197A448B.quest_desc": [
            "&#827AFF스티렌-부타디엔&r에 &#9683F7작은 납 가루&r 또는 &#FEA8FF작은 크롬 가루&r를 혼합하면 &#A1A1A1스티렌-부타디엔 고무&r가 됩니다."
        ],
        "quest.3ACC27B786CDCF22.quest_desc": [
            "&#3ABEC7전기 압축기를 사용하면 &#CE5ADB작은 텅스텐 가루&r를 &#AF22BF텅스텐 조각&r으로 만들 수 있습니다."
        ],
        "quest.3B1CDC2DD05CAE80.quest_desc": [
            "&#F36EF5폴리염화비닐&r, &#6EBAF5백금 판, &#C4C362카드뮴 배터리&r, &#F7BB57어닐링 구리 케이블&r과 &#57BFF7디지털 회로 기판&r을 조합하면 &#EBE56E처리 유닛 기판&r이 됩니다."
        ],
        "quest.3CB05026BC4C5577.quest_desc": [
            "현재는 &#3946E3혼합 방폭 주괴&r를 &#6F93C7전기 압축기&r에서 처리하여 &#986FC7방폭 합금판&r을 매우 비효율적으로 만들 수 있습니다."
        ],
        "quest.3FE2A649F07DF28D.quest_subtitle": "Extreme Reactors 블루토늄을 분쇄해 플루토늄 가루를 얻을 수 있습니다",
        "quest.3FE489E6B1FAC24B.quest_subtitle": "소모된 연료봉 재활용",
        "quest.3FE489E6B1FAC24B.title": "플루토늄 얻기",
        "quest.40F2EDB9384CE782.quest_desc": [
            "&#DBE37F증기 분해된 경유&r를 증류하면 &#9C6C35아세틸렌&r을 얻습니다."
        ],
        "quest.4A06CCE1FE0F333C.quest_desc": [
            "&#74C3DB공기 흡입구&r를 &#46CAF2진공 냉각기&r에 넣으면 &#B5E7F7액화 공기&r를 얻습니다."
        ],
        "quest.4A618CA66AD6223D.quest_subtitle": "더욱 많은 전력 입력",
        "quest.4F870252E9FB1A41.quest_desc": [
            "원자로에는 연료봉을 넣어 연료를 공급합니다. 이 연료봉은 제작할 수 있는 가장 기본적인 종류입니다."
        ],
        "quest.50F97171D25CD2EE.quest_desc": [
            "&#6EDDFF터보 업그레이드&r는 개당 용량을 &#FFEB6E512EU/t&r만큼 늘립니다."
        ],
        "quest.56A4F5D301BC1E93.quest_desc": [
            "&#6EDDFF터보 업그레이드&r는 개당 용량을 &#FFEB6E64EU/t&r만큼 늘립니다."
        ],
        "quest.58F7C11C241DD7A4.quest_desc": [
            "&#6AADD9증류탑&r은 &#A3D2F0증류소&r를 업그레이드한 형태입니다. 같은 입력에서 여러 산출물을 얻는 것이 가장 큰 장점입니다.",
            "",
            "구조물을 만들려면 &#6AADD9증류탑&r 제어기 GUI에서 높이를 선택하세요. 필요한 산출물 수에 따라 높이가 달라집니다. &#76759E원유&r를 처리하려면 높이가 3블록이어야 합니다.",
        ],
        "quest.58F7C11C241DD7A4.quest_subtitle": "효율이 중요합니다",
        "quest.5A4406F89DB802F0.quest_desc": [
            "&#BB95CF스티렌&r과 &#D46C85부타디엔&r을 반응시키면 &#827AFF스티렌-부타디엔&r이 됩니다."
        ],
        "quest.5B45AB96953FA61C.title": "디지털 시대",
        "quest.633D6361DA680C75.quest_desc": [
            "&#E6ED98경유&r와 증기를 혼합하면 &#DBE37F증기 분해된 경유&r를 얻습니다."
        ],
        "quest.66E78F599CD50579.quest_desc": [
            "&#49C472원자로&r에서는 고급 자원을 처리할 수 있습니다. 여기서는 &#8F49C4중수소&r와 &#EB5266삼중수소&r를 생산합니다.",
            "",
            '이 자원 목록은 "대형" 원자로를 만드는 데 도움이 됩니다. 더 작은 원자로는 속도와 효율이 낮아 권장하지 않습니다.',
            "{@pagebreak}",
            "효율적인 원자로를 만드는 방법은 여기서 모두 설명하기에는 너무 복잡합니다. 대신 사용하기 좋은 설계를 소개합니다.",
            "",
            "다음은 &#49C472대형 원자로&r에서 &#8F49C4중수소&r를 생산하는 설계입니다.",
            "{image:atm:textures/questpics/modernindustrialization/large_reactor.png width:100 height:100 align:center}",
            "",
            "다음은 &#EB5266삼중수소&r를 생산하는 &#49C472극대형 원자로&r 설계입니다.",
            "",
            "{image:atm:textures/questpics/modernindustrialization/largest_reactor.png width:100 height:100 align:center}",
        ],
        "quest.66E78F599CD50579.quest_subtitle": "폭발하지 않습니다",
        "quest.672B69448F1D458B.quest_desc": [
            "&#FAAD28열교환기&r는 &#4D7DFFExtreme Reactors&r 터빈을 좋아하는 플레이어에게 안성맞춤입니다. 엄청난 양의 증기를 생산할 수 있습니다."
        ],
        "quest.672B69448F1D458B.quest_subtitle": "증기가 콸콸콸",
        "quest.6A9AE3514B5151C9.quest_desc": [
            "&#CFB951칸탈 코일&r을 사용하면 &#C356C4티타늄 원석&r을 &#DF9DE0뜨거운 티타늄 주괴&r로 처리할 수 있습니다. 이 과정에는 &#D49B70망간 황산 용액&r이 필요합니다."
        ],
        "quest.6F183B06683D1213.quest_desc": [
            "&#EBA844뜨거운 칸탈 주괴&r는 &#6DC0F7진공 냉각기&r로 식힐 수 있습니다."
        ],
        "quest.6F3974CAAA555FD0.quest_subtitle": "RAM 관리하기",
        "quest.75619C7174C6703C.quest_desc": [
            "우라늄 가루를 원심분리하면 우라늄 동위원소를 얻으며, 이를 더 좋은 연료봉으로 가공할 수 있습니다."
        ],
        "quest.75619C7174C6703C.title": "우라늄 가루 원심분리",
        "quest.78EC7D19BE24FE06.quest_subtitle": "폭발하지 않습니다",
        "quest.7AF6C95816E82861.quest_desc": [
            "&#8F49C4중수소&r와 &#AABBFA산소&r를 &#5B75D4화학 반응&r시키면 &#9C51DB중수&r가 됩니다. 중수는 &#45BF56원자로&r에 다시 넣을 수 있습니다."
        ],
        "quest.7C73740F1B515F2C.quest_desc": [
            "&#C452C4텅스텐 가루&r는 가공할 수 있도록 훨씬 작은 형태로 분쇄해야 합니다."
        ],
        "task.08F68CC089765088.title": "우회 요령",
    },
    "mi_endgame": {
        "quest.0AE83A6CC21F96D4.quest_desc": [
            "&#3127F5특이점&r을 전기분해하면 &#DA27F5UU 물질&r이 됩니다. 이 과정에서 &#3127F5특이점&r은 &n&a소모되지 않습니다&r."
        ],
        "quest.1E22A0D5F4B2EB0D.quest_subtitle": "헬륨으로 아르곤 냉각",
        "quest.27826D74ADC73556.quest_desc": [
            "&#ED8C61구리 가루&r와 &#90F0E7산소&r를 &#E3CE54칸탈 전기 용광로&r에서 가열하면 &#E87848뜨거운 어닐링 구리 주괴&r가 됩니다. 이를 &#4CBBD9진공 냉각기&r에서 식히면 &#E87848어닐링 구리 주괴&r를 얻습니다. 이 주괴를 분쇄하면 &#E87848어닐링 구리 가루&r가 됩니다."
        ],
        "quest.3AB0822F02350DA3.quest_subtitle": "무한 피해",
        "quest.3B99290BE63F2968.quest_subtitle": "탄소 가루 압축",
        "quest.4F780343E3FFA43E.quest_subtitle": "여기가 끝입니다",
        "quest.53C167AF34694F8F.quest_desc": [
            "&#40B36A이트륨&r, &#DBA146어닐링 구리&r, &#33CC3A네오디뮴&r과 &#D6D290이리듐&r 가루를 혼합하면 &#5EDEE0초전도체 가루&r가 됩니다. 이를 &#E3CE54칸탈 전기 용광로&r에서 가열한 뒤 &#4CBBD9진공 냉각기&r에서 식히세요."
        ],
        "quest.53C167AF34694F8F.quest_subtitle": "초전도하기",
        "quest.54C852CA6E056589.quest_subtitle": "핵 배터리",
        "quest.732DA855AFF62907.quest_desc": [
            "&8석탄&r을 원심분리하면 &7탄소 가루&r가 됩니다."
        ],
        "task.121A74E938A0320C.title": "UU 물질",
    },
    "related": {
        "quest.00F00B0B66059996.quest_desc": [
            "또 하나의 &l멀티블록&r입니다! 해군 기지보다도 더 많은 포트가 필요하겠네요!\n\n&3유체 입력 &f및 &3출력&r 해치와 &6아이템 입력 &f및 &6출력&r 해치가 필요합니다.\n\n처리 과정이 조금 길므로 잘 따라오세요!\n\n먼저 소울 트리에 유체 추출기(&lIF&r)를 사용하여 &7정제되지 않은 액체 영혼&r을 얻습니다.\n\n다음은 &9소스 응축기&r로 만드는 &d액화 소스&r입니다. &9소스 응축기&r는 주변 소스 병의 소스를 끌어와 &d액화 소스&r로 바꿉니다!\n\n이제 &b&l룬 도가니&r에서 영혼, &7정제되지 않은 액체 영혼&r과 &d액화 소스&r를 합쳐 액체 영혼을 만드세요!\n\n마지막으로 액체 영혼, &d액화 소스&r와 &l&5Mekanism&r 아이템을 사용하여 &5Obsidiansteel&r을 제작합니다.",
            "{@pagebreak}",
            "{image:atm:textures/questpics/chap3/creative_crucible1.png width:125 height:100 align:center}",
            "&l&b룬 도가니&r의 첫 번째 층 중앙에는 &6금박 조각 광택 다크스톤&r을, 그 둘레에는 &9광택 다크스톤&r을 놓습니다. 옆면에는 거꾸로 된 &9광택 다크스톤 계단&r을, 모서리에는 &7룬 블록&r을 놓으세요.",
            "{image:atm:textures/questpics/chap3/creative_crucible2.png width:125 height:100 align:center}",
            "정중앙에는 &b비전 수정&r을 놓고 &9광택 다크스톤 계단&r으로 둘러쌉니다. 옆면에는 &6비전 광택 다크스톤 기둥&r, 해치로 교체할 &9광택 다크스톤&r과 &6비전 광택 다크스톤&r을 놓습니다.",
            "{image:atm:textures/questpics/chap3/creative_crucible3.png width:125 height:100 align:center}",
            "각 모서리에 &b비전 수정 블록&r을 놓으면 이 층은 끝입니다!",
            "{image:atm:textures/questpics/chap3/creative_crucible4.png width:125 height:100 align:center}",
            "마지막으로 한 블록의 공간을 두고 중앙의 &b비전 수정 블록&r 위에 &7양자 주입기&r를 놓으세요.",
            "{image:atm:textures/questpics/chap3/creative_crucible5.png width:150 height:100 align:center}",
            "{image:atm:textures/questpics/chap3/creative_crucible6.png width:150 height:100 align:center}",
            "중간층의 &9광택 다크스톤 블록&r을 해치로 교체하세요!",
        ],
        "quest.00F00B0B66059996.title": "&b&l룬 도가니",
        "quest.050CCE5D1DD6B21E.quest_desc": AUTOMATIC_FORGE_DESC,
        "quest.050CCE5D1DD6B21E.title": "&c&l자동 헤파이스토스 대장간",
        "quest.1FC1588A131B6A4A.quest_desc": [
            "일반적인 &6&lATM Star&r 제작과 마찬가지로 자동화도 &6&l룬 별 제단&r 안에서 진행해야 합니다! \n\n건설 및 사용법은 챕터 3의 퀘스트를 확인하세요."
        ],
        "quest.1FC1588A131B6A4A.title": "&6&l룬 별 제단",
        "quest.360B150190A5C894.quest_desc": [
            "많은 모드 플레이어는 &5마법 부여&r를 완전히 자동화할 수 없고 원하는 &5마법&r을 선택할 수도 없다는 점에 불편을 느낍니다. 운에 맡겨야 했죠! \n\n이제 &5&l룬 인챈터&r가 두 문제를 모두 해결합니다. \n\n&5마법 부여대&r를 직접 건드릴 필요 없이 알맞은 아이템, &d소스&r와 &aXP 유체&r를 파이프로 공급하세요. \n\n&aXP 유체&r는 &8&lImmersive Engineering&r의 병입 기계로 &a액체 경험치&r를 병에 담은 뒤 &7&lExtended Industrialization&r의 통조림 기계에서 처리하여 얻습니다. \n\n&6&lATM Star&r를 다시 만들려면 &d주입된 드래곤의 숨결&r과 &5수선 책&r을 만들어야 합니다!",
            "{@pagebreak}",
            "(&b하늘색 양탄자&r는 &b영혼에 물든 깊은 책장&r",
            "&5보라색 양탄자&r는 &5메아리치는 스컬크 책장&r",
            "&9파란색 양탄자&r는 &9영혼에 물든 스컬크 책장&r)",
            "{image:atm:textures/questpics/chap3/creative_enchanter1.png width:125 height:100 align:center}",
            "&5&l룬 인챈터&r의 바닥에는 거의 모든 재료가 들어갑니다! 수많은 &9다크스톤&r, 책장, &7룬 블록&r과 &b비전 수정 블록&r이 필요합니다!",
            "{image:atm:textures/questpics/chap3/creative_enchanter2.png width:125 height:100 align:center}",
            "비슷하게 이어서 &7룬 블록&r과 &b비전 수정 블록&r을 &6금박 조각 광택 다크스톤&r과 &6다크스톤 기둥&r으로 바꾸세요. 새로 보이는 사각형은 &6다크스톤 기둥&r의 윗면입니다!",
            "{image:atm:textures/questpics/chap3/creative_enchanter3.png width:125 height:100 align:center}",
            "이제 더 쉬워집니다! 책장을 조금 더 놓고 &6다크스톤 받침대&r와 &5마법 부여대&r를 추가하세요.",
            "{image:atm:textures/questpics/chap3/creative_enchanter4.png width:125 height:100 align:center}",
            "이번 층은 더욱 쉽습니다! 마지막 책장 위에 &b영혼 랜턴&r 4개만 놓으세요.",
            "{image:atm:textures/questpics/chap3/creative_enchanter5.png width:125 height:100 align:center}",
            "이번 층은 너무 쉽네요! &5마법 부여대&r 한 블록 위에 &7양자 주입기&r를 놓으세요.",
            "{image:atm:textures/questpics/chap3/creative_enchanter6.png width:150 height:150 align:center}",
            "{image:atm:textures/questpics/chap3/creative_enchanter7.png width:150 height:150 align:center}",
            "미리 말했어야 했는데, 해치는 &5&l룬 인챈터&r 바닥에 놓습니다... 미안해요!",
        ],
        "quest.360B150190A5C894.title": "&5&l룬 인챈터",
        "quest.3403D7502F7BC897.quest_desc": [
            "말 그대로 무적입니다. 어떤 공격도 피해를 줄 수 없습니다.\n\n현재는 &c네더라이트 방어구&r에 &e양자 &b업그레이드&r를 적용해야 하지만, &6&lATM 팀&r이 이 제작법을 더 어렵게 만들고 있습니다!\n\n그리고 여러분은 막을 수 없습니다! &l으하하하하"
        ],
        "quest.3403D7502F7BC897.quest_subtitle": "무적",
        "quest.3403D7502F7BC897.title": "&e양자 &b방어구&r (&l&7MI&r)",
        "quest.34D14B807A2DAC0F.quest_desc": [
            "&5&lMekanism&r과 &l&7Modern Industrialization&r만 재미있는 장비를 가질 수 있다고 생각했나요? \n\n이 &5양자 방어구&r는 &c네더라이트 방어구&r와 비슷한 기본 능력치를 지니지만, &a메카슈트&r처럼 에너지를 방패로 사용할 수 있습니다. \n비행, 야간 투시와 재충전 등 더욱 강력해지는 업그레이드도 설치할 수 있습니다! \n\n가장 좋은 점은 저장소 시스템에 연결할 수 있다는 것입니다. 어디에 있든 자동으로 에너지를 받고 아이템을 꺼낼 수 있습니다. "
        ],
        "quest.2A6753C806D2AF8D.quest_desc": [
            "필요한 것보다 훨씬 큰 피해를 줍니다! 다만 몇 가지 단점도 있습니다."
        ],
        "quest.2A6753C806D2AF8D.quest_subtitle": "&f∞ &c공격 피해",
        "quest.17598C171E610752.quest_desc": [
            "이 제작법은 너무 복잡해 설명하기도 어렵네요. 차라리 &l&2Productive Trees&r의 가계도를 모두 나열하는 편이 낫겠어요. \n\n&6고급 모터&r를 &d티타늄 막대&r 및 &9처리 유닛&r과 조합하여 &6대형 고급 모터&r를 만드세요. \n또는 &6기계식 팔&r을 사용할 수도 있지만, 그쪽이 더 만들기 쉽다고 장담할 수는 없습니다!"
        ],
        "quest.17598C171E610752.title": "&6대형 고급 모터",
        "quest.24F3E90C14BFD1B4.quest_desc": [
            "&7&lModern Industrialization&r은 이름만큼이나 방대한 모드입니다! \n\n여러 등급의 기계가 있지만 다행히 &6&lStar&r를 위해 마지막 등급까지 진행할 필요는 없습니다. \n\n이제 전부 선택 사항입니다! 원한다면 &6&lCreate&r로 &6&lATM Star&r를 만들어도 됩니다."
        ],
        "quest.24F3E90C14BFD1B4.title": "&7&lModern Industrialization",
        "quest.2B0C3AAAA6D0B0D2.quest_desc": [
            "&a우라늄 사중 연료봉&r은 여러 방폭·방사선 차폐 합금과 방사성 물질로 만듭니다. \n\n모든 재료를 합치면 원자로에 훌륭한 연료가 됩니다! 또는 &c&l현자의 연료&r로 사용할 수도 있습니다!  \n\n그냥 &c블레이즈 버너&r를 써도 되지만... 그러면 재미없잖아요!"
        ],
        "quest.2B0C3AAAA6D0B0D2.title": "&a우라늄 사중 연료봉",
        "quest.42AF4EBDA5D6CC36.quest_desc": [
            "가장 강한 금속 세 가지인 &5텅스텐&r, &d티타늄&r과 &7스테인리스강&r을 조합하면 &2폭발내성 합금&r을 만들 수 있습니다. 얼룩도 중요했나 보네요. \n\n이 재료를 조합하여 &2케이싱&r을 만드세요. \n\n&3&l불가능한 확률 장치&r에는 &2폭발내성 케이싱&r 2개 또는 256M 휴대용 아이템 셀 2개가 필요하며, 두 재료를 섞어 써도 됩니다!"
        ],
        "quest.42AF4EBDA5D6CC36.title": "&2폭발내성 케이싱",
        "quest.4B7D387CEFF9667E.quest_desc": [
            "드디어 &6&lCreate&r가 업데이트됐고 기다린 보람이 있습니다! \n\n&6&lCreate&r는 제작, 분쇄, 혼합과 양조를 비롯한 거의 모든 작업에 회전력을 사용합니다. \n\n오랜만이라 &6&lCreate&r 사용법이 기억나지 않는다면 &7&lModern Industrialization&r으로 &6&lATM Star&r를 제작해도 됩니다."
        ],
        "quest.70CCE558E03227AB.quest_desc": [
            "&6&l룬 별 제단&r은 &3Drack.ion&r이 &7&lModern Industrialization&r으로 만든 멀티블록입니다! \n\n&5룬 별 제단 블록&r에서 시작하는 15x8x15 구조물입니다. 블록을 놓고 &7&lModern Industrialization&r의 &e렌치&r를 사용하면 멀티블록 건설 위치가 표시됩니다. \n\n퀘스트 2쪽이나 &e렌치&r를 참고해 건설한 뒤 &6&l제단&r 각 면에서 &6비전 광택 다크스톤&r 옆 &9광택 다크스톤&r을 해치로 교체하세요. 실제 &6&lStar&r 제작에 필요합니다. \n\n&l&7Modern Industrialization&r의 아이템 입력 해치에는 제작법 재료를 넣고, 아이템 출력 해치에서는 &6&lStar&r가 나옵니다. 에너지 입력 해치는 &6&l제단&r에 전력을 공급합니다! \n에너지 얘기가 나왔으니 말인데, &6&l별 제단&r이 충분한 FE/t를 받으려면 강화해야 합니다. &7&lModern Industrialization&r의 업그레이드를 여러 개 &5제단 블록&r에 넣으세요. 아이템을 볼 때 Shift를 누르면 &6&l제단&r의 처리량 증가치를 확인할 수 있습니다! \n\n&5제단 블록&r에서 &6&l제단&r 제작법을 시작할 수 있으며, 구조가 잘못되었으면 상태도 알려 줍니다. \n\n(참고로 제작법의 전리품 가방은 &5&lLunar Monstrosity&r에게서 얻습니다. &6제단&r의 &9계단&r이나 &6기둥&r 방향은 관계없습니다.)",
            "{@pagebreak}",
            "{image:atm:textures/questpics/chap2/atmstar_layer1.png width:125 height:75 align:center}",
            "1층에는 &5제단 블록&r과 함께 &9광택 다크스톤&r, &9광택 다크스톤 계단&r과 &6비전 광택 다크스톤&r을 놓습니다.",
            "{image:atm:textures/questpics/chap2/atmstar_layer2.png width:125 height:75 align:center}",
            "2층에는 &9광택 다크스톤&r, &9계단&r과 &6금박 조각 광택 다크스톤&r을 놓습니다.",
            "{image:atm:textures/questpics/chap2/atmstar_layer3.png width:125 height:100 align:center}",
            "3층에는 &b비전 수정 오벨리스크&r, &7룬 블록&r, &6비전 조각 광택 다크스톤&r과 &9광택 다크스톤 반 블록&r을 추가합니다!",
            "{image:atm:textures/questpics/chap2/atmstar_layer4.png width:125 height:100 align:center}",
            "4층에는 &6다크스톤 받침대&r, 중앙의 &7자화된 다크스톤 받침대&r와 &6비전 광택 다크스톤 기둥&r을 놓습니다.",
            "{image:atm:textures/questpics/chap2/atmstar_layer5.png width:125 height:100 align:center}",
            "5층은 간단합니다. &6기둥&r을 더 놓으세요.",
            "{image:atm:textures/questpics/chap2/atmstar_layer6.png width:125 height:100 align:center}",
            "6층에는 &6기둥&r과 함께 &7자화된 다크스톤 받침대&r 위에 &7양자 주입기&r를 놓습니다.",
            "{image:atm:textures/questpics/chap2/atmstar_layer7.png width:100 height:100 align:center}",
            "7층도 간단합니다. &6기둥&r을 더 놓으세요!",
            "{image:atm:textures/questpics/chap2/atmstar_layer8.png width:100 height:100 align:center}",
            "마지막 층에는 &6기둥&r, &7룬 블록&r과 &b비전 수정 블록&r을 더 놓습니다.",
            "{image:atm:textures/questpics/chap2/atmstar_layer9.png width:125 height:100 align:center}",
            "이제 우트렘 병을 추가하세요! 병이 가득 차지 않으면 &5제단 블록&r이 불평하는 것 같네요...",
            "{image:atm:textures/questpics/chap2/atmstar_layer10.png width:200 height:100 align:center}",
            "{image:atm:textures/questpics/chap2/atmstar_layer11.png width:200 height:100 align:center}",
            "&6&l제단&r을 시작하기 위한 마지막 단계는 해치 설치입니다. 그림처럼 &6비전 광택 다크스톤&r 바깥쪽에 아이템 입력·출력 해치와 에너지 입력 해치를 놓으세요.",
        ],
        "quest.70CCE558E03227AB.quest_subtitle": "&l&6ATM Star 제작",
        "quest.70CCE558E03227AB.title": "&l&6룬 별 제단",
        "quest.78215D704E6095B0.quest_desc": [
            "&5&lMekanism&r과 &l&7Modern Industrialization&r만 최종 단계 방어구를 가질 수 있다고 생각했나요? \n\n이 &5양자 방어구&r는 &c네더라이트 방어구&r와 비슷한 기본 능력치를 지니지만, &a메카슈트&r처럼 에너지를 방패로 사용할 수 있습니다. \n비행, 야간 투시와 재충전 등 더욱 강력해지는 업그레이드도 설치할 수 있습니다! \n\n가장 좋은 점은 저장소 시스템에 연결할 수 있다는 것입니다. 어디에 있든 시스템에서 자동으로 에너지를 받고 아이템을 꺼낼 수 있습니다. \n\n전 부위를 착용하면 &a방사선&r으로 인한 죽음도 막습니다."
        ],
        "quest.0D61473D7A09CD48.quest_desc": [
            *AUTOMATIC_FORGE_DESC[:-1],
            "마지막으로 해치를 몇 개 더 배치하세요! 반드시 필요합니다! 직접 건설하기 싫다면 &b&l자동 헤파이스토스 대장간&r 제어기를 웅크린 채 우클릭하여 멀티블록을 자동으로 건설할 수 있습니다.",
        ],
        "quest.3B5DEB942752B3BF.quest_desc": [
            "모든 제작법에는 &#DE552C최소&r 에너지 요구량이 있습니다. 제작법 화면에서 업그레이드에 마우스를 올리면 확인할 수 있습니다. ",
            "",
            "기계에 알맞은 업그레이드를 넣어 에너지 요구량을 충족하세요.",
            "",
            "{@pagebreak}",
            "1. &#39EDA5Forbidden and Arcanus&r의 &n&#A839ED룬 조율 수정&r. 용량을 &#EDE02F512 EU/t&r만큼 늘리며 &#EDA439Modern Industrialization&r 진행을 건너뜁니다.",
            "",
            "2. &#EDA439Modern Industrialization&r의 &n&#2278F2모든 업그레이드&r. 업그레이드 종류마다 에너지 용량 증가량이 다릅니다. ",
            "",
            "기본 업그레이드는 &#EDE02F2 EU/t&r, 고급은 &#EDE02F16 EU/t&r, 터보는 &#EDE02F64 EU/t&r, 초고급은 &#EDE02F512 EU/t&r, 양자는 &#EDE02F1,000,000,000 EU/t&r를 추가합니다.  ",
        ],
        "quest.798B592E956AD28C.quest_desc": [
            "&b&l룬 도가니&r는 자동 정수의 절반인 액체 영혼과 &b액체 Aureal&r을 얻는 멀티블록입니다! \n\n건설 방법은 퀘스트 설명의 다음 쪽을 확인하세요! \n\n작동하려면 &d액화 소스&r를 포함한 아이템과 액체를 포트로 공급해야 합니다. 액체 영혼과 &b액체 Aureal&r 모두 아이템과 액체가 필요합니다. \n\n&b&l룬 도가니&r에서는 &9타락한 영혼&r, &d마법 부여된 영혼&r과 &5Obsidiansteel&r도 제작할 수 있습니다!",
            "{@pagebreak}",
            "{image:atm:textures/questpics/chap3/creative_crucible1.png width:100 height:100 align:center}",
            "&l&b룬 도가니&r의 첫 번째 층 중앙에는 &6금박 조각 광택 다크스톤&r을, 그 둘레에는 &9광택 다크스톤&r을 놓습니다. 옆면에는 거꾸로 된 &9광택 다크스톤 계단&r을, 모서리에는 룬 블록을 놓으세요.",
            "{image:atm:textures/questpics/chap3/creative_crucible2.png width:100 height:100 align:center}",
            "정중앙에는 &b비전 수정&r을 놓고 &9광택 다크스톤 계단&r으로 둘러쌉니다. 옆면에는 &6비전 광택 다크스톤 기둥&r, 해치로 교체할 &9광택 다크스톤&r과 &6비전 광택 다크스톤&r을 놓습니다.",
            "{image:atm:textures/questpics/chap3/creative_crucible3.png width:100 height:100 align:center}",
            "각 모서리에 &b비전 수정 블록&r을 놓으면 이 층은 끝입니다!",
            "{image:atm:textures/questpics/chap3/creative_crucible4.png width:100 height:100 align:center}",
            "마지막으로 한 블록의 공간을 두고 중앙의 &b비전 수정 블록&r 위에 &7양자 주입기&r를 놓으세요.",
            "{image:atm:textures/questpics/chap3/creative_crucible5.png width:150 height:100 align:center}",
            "중간층의 &9광택 다크스톤 블록&r을 해치로 교체하세요! 직접 건설하기 싫다면 &b&l룬 도가니&r 제어기를 웅크린 채 우클릭하여 멀티블록을 자동으로 건설할 수 있습니다.",
        ],
        "quest.798B592E956AD28C.title": "&b&l룬 도가니&r",
        "quest.30EA16BB8C169F86.quest_desc": [
            "&6구리&r와 &7주석&r을 혼합한 합금입니다! \n\n&7&lModern Industrialization&r에서는 아주 많이 사용하지만 &8&lIE&r에서는... 그다지 많이 쓰지 않습니다."
        ],
        "quest.69F7A0DE8D70AC44.quest_desc": [
            "&#A0DE45Modern Industrialization&r의 &#DBA15A증기 채굴 드릴&r은 게임 초반 채굴에 큰 도움이 되며 &#6E6D6D단조 망치&r만 있으면 제작할 수 있습니다. &53x3&r 범위를 채굴하고 &#EEF768섬세한 손길을 전환&r할 수 있습니다.\n\n기본값이 &7'Y'&r인 \"3x3 채굴 전환\" 키를 눌러 &53x3&r 채굴을 전환할 수 있습니다.\n\n증기 채굴 드릴을 들고 &7웅크린 채 우클릭&r하면 &#EEF768섬세한 손길&r을 전환합니다.\n\n&#DBA15A증기 채굴 드릴&r을 채우려면 인벤토리의 &6연료&r 위에 드릴을 놓고 &7우클릭&r하세요. &9물&r은 월드에서 &7우클릭&r하여 채우거나 물 양동이를 들고 다니면 됩니다."
        ],
        "quest.69F7A0DE8D70AC44.quest_subtitle": "초반 채굴",
    },
}


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def restore_format_codes(source: object, translated: object) -> object:
    """원문의 색상 코드 개수와 배열 구조를 그대로 보존한다."""
    if isinstance(source, str) and isinstance(translated, str):
        if "\\n" in source and "\n" in translated:
            translated = translated.replace("\n", "\\n")
        pattern = re.compile(
            r"(?:§[0-9A-FK-ORa-fk-or]|&#[0-9A-Fa-f]{6}|&[0-9A-FK-ORa-fk-or])"
        )
        if Counter(pattern.findall(source)) != Counter(pattern.findall(translated)):
            raise ValueError(f"색상 코드 불일치: {source!r} / {translated!r}")
        return translated
    if isinstance(source, list) and isinstance(translated, list):
        if len(source) != len(translated):
            raise ValueError("퀘스트 설명 배열 길이가 다릅니다.")
        return [
            restore_format_codes(left, right) for left, right in zip(source, translated)
        ]
    raise TypeError("퀘스트 번역 자료형이 원문과 다릅니다.")


def normalize() -> dict[str, object]:
    rows = []
    for group in GROUPS:
        root = WORK_ROOT / group
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        overrides = TRANSLATIONS[group]
        unknown = sorted(set(overrides) - set(english))
        if unknown:
            raise KeyError(f"{group} 원문에 없는 키: {unknown}")
        for key, translated in overrides.items():
            translated = restore_format_codes(english[key], translated)
            errors = validate_value(key, english[key], translated)
            if errors:
                raise ValueError("; ".join(errors))
            korean[key] = translated
        write_json(root / "ko_kr.json", korean)
        rows.append(
            {
                "group": group,
                "keys": len(english),
                "reviewed": len(overrides),
                "remaining": len(set(english) - set(overrides)),
            }
        )
    return {"groups": rows}


def verify() -> tuple[dict[str, object], list[str]]:
    errors = []
    rows = []
    allowed_originals = {
        "Modern Industrialization",
        "Extended Industrialization",
        "&7&lModern Industrialization",
    }
    for group in GROUPS:
        root = WORK_ROOT / group
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        if list(english) != list(korean):
            errors.append(f"키 또는 순서 불일치: {group}")
            continue
        untranslated = []
        for key, source in english.items():
            target = korean[key]
            errors.extend(validate_value(key, source, target))
            if source == target and source not in allowed_originals:
                untranslated.append(key)
        if untranslated:
            errors.append(f"미번역: {group}:{untranslated[:30]}")
        rows.append(
            {"group": group, "keys": len(english), "untranslated": len(untranslated)}
        )
    report = {
        "groups": rows,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT.parent / "quest_validation.json", report)
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("normalize", "verify"))
    args = parser.parse_args()
    if args.command == "normalize":
        report = normalize()
        errors = []
    else:
        report, errors = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
