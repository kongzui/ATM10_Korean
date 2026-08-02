#!/usr/bin/env python3
"""Industrial Foregoing 관련 FTB Quests 기존 한국어를 전체 재검수한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path

import ars_family
import build_ae2_quests as quest_snbt
import industrial_foregoing_family as language
from local_paths import PROJECT_ROOT


QUEST_ROOT = PROJECT_ROOT / "working/industrial_foregoing/quests"
CACHE_FILE = PROJECT_ROOT / "temp/industrial_foregoing_quest_candidate_cache.json"
CANDIDATE_FILE = (
    PROJECT_ROOT / "working/industrial_foregoing/quest_auto_candidates.json"
)

KEY_OVERRIDES: dict[str, object] = {
    "chapter.193F91842D2ED7D9.title": "Industrial Foregoing",
    "quest.06094615950AC062.title": "기타 컨베이어 업그레이드",
    "quest.0BCCDE24D378F260.title": "&d고급 기계 프레임",
    "quest.0BCCDE24D378F260.quest_subtitle": "등급: &d3",
    "quest.3514E9C1A8C7400C.title": "&b기본 기계 프레임",
    "quest.3514E9C1A8C7400C.quest_subtitle": "등급: &b2",
    "quest.55820773BDD5319D.title": "Industrial Foregoing",
    "quest.55820773BDD5319D.quest_subtitle": "등급: &a1",
    "quest.79D48F8F31B152C3.title": "&bIndustrial Foregoing &#27AEB9Souls",
    "quest.7B4AF35313D7D779.title": "&6최고급 기계 프레임",
    "quest.7B4AF35313D7D779.quest_subtitle": "등급: &64",
    "quest.0BB42C5861B22D32.title": "&9Industrial Foregoing: &b균사 반응기",
    "quest.11374A3B5BD644F5.title": "&lIndustrial Foregoing",
    "quest.21C2458FED19363C.quest_subtitle": "Industrial Foregoing 생성기",
    "quest.2580135392DEF522.title": "모의 수경 재배대",
    "quest.3924975B48F5A482.title": "Soulplied Energistics",
    "quest.6C001E18093FC037.title": "식물",
    "quest.0FAAE744E156D8EF.quest_subtitle": "균사 반응기라, 흐음?",
    "quest.0BB42C5861B22D32.quest_subtitle": "당신의 균사 반응기는 아니에요",
    "quest.06F84E2C484FAC5B.quest_desc": [
        "조약돌 생성기를 아시나요? 자재 석재 가공 공장은 그 기능을 한 단계 더 "
        "발전시킨 기계입니다. 돌을 자갈, 모래, 규소로 분쇄하거나 돌로 제련하고, "
        "흑요석을 만드는 등 JEI에 표시된 여러 가공을 수행할 수 있습니다."
    ],
    "quest.0B35172E47705205.quest_desc": [
        "맞습니다. &bIndustrial Foregoing&r에도 광석 가공이 있습니다. 광석과 "
        "&6액상 고기&r를 사용해 생광석 고기를 만듭니다. 저는 광석 의사가 아니라서 "
        "이 생광석 고기를 더 처리할 수는 없네요. 발효 스테이션에 넣어 볼까요?"
    ],
    "quest.0E8647B8EB4AAC41.quest_desc": [
        "비적대적 몹 -> &#FF69B4분홍색 슬라임&r을 더 많이 생산\\n"
        "적대적 몹 -> &6액상 고기&r를 더 많이 생산"
    ],
    "quest.0FAAE744E156D8EF.quest_desc": [
        "&b균사 반응기&r는 주변의 모든 균사 발전기가 동시에 작동할 때 총 "
        "&a25MFE/t&r를 생산합니다.\\n\\n작동시키려면 각 균사 발전기가 소비하는 "
        "자원을 확인해 모두 자동화해야 합니다. 대부분은 간단하지만, 일부는 그렇지 "
        "않습니다... &o특히 마법 추출 균사 발전기 말이죠&r.\\n\\n모든 공급을 "
        "자동화했다면 반응기를 하나만 둘 필요도 없습니다. 더 만들어도 됩니다."
    ],
    "quest.15551AC6C68E12E0.quest_desc": [
        "&bIndustrial Foregoing&r의 생성기라고 보면 됩니다. &a정수&r와 개체가 든 "
        "몹 포획기를 사용해 해당 몹의 복제본을 생성합니다.\\n\\n생성기에 넣을 수 "
        "없는 보스와 일부 몹은 몹 복제기에서도 차단됩니다.\\n\\n*&8예외가 조금 "
        "있습니다. 고급 툴팁(F3 + H)을 켜고 생성 알에서 SHIFT를 눌러 몹 복제기 "
        "차단 태그가 있는지 확인하세요."
    ],
    "quest.1684D52FDAAC894B.quest_desc": [
        "앞에서 말한 광석 의사 이야기를 기억하나요? 발효 스테이션은 생광석 고기를 "
        "발효 광석 고기로 바꿉니다. 4가지 모드가 있습니다.\\n\\n"
        "1. 광석 2배 가공, 5초.\\n2. 광석 3배 가공, 45초.\\n"
        "3. 광석 4배 가공, 120초. &#FF69B4분홍색 슬라임&r을 촉매로 사용합니다.\\n"
        "4. 광석 5배 가공, 300초. &b에테르 가스&r를 촉매로 사용합니다."
    ],
    "quest.1823CC81D613892B.quest_desc": [
        "몹 도살 공장은 작업 영역의 몹을 &l제거&r하고 &#FF69B4분홍색 슬라임&r과 "
        "&6액상 고기&r로 바꿉니다.\\n\\n비적대적 몹 -> &#FF69B4분홍색 슬라임&r을 "
        "더 많이 생산\\n적대적 몹 -> &6액상 고기&r를 더 많이 생산\\n\\n이 기계는 "
        "범위 업그레이드를 지원합니다."
    ],
    "quest.1BA3D15FFE7DBE59.quest_desc": [
        "&bIndustrial Foregoing&r의 주요 자원 중 하나는 &f라텍스&r입니다. 라텍스는 "
        "기계와 업그레이드에 필요한 기계 프레임을 만드는 데 사용합니다.\\n\\n"
        "&a유체 추출기&r는 &6원목&r에서 라텍스를 추출합니다. 아카시아와 맹그로브 "
        "원목이 가장 많은 라텍스를 줍니다.\\n\\n------------------------\\n\\n"
        "플라스틱은 건조 고무를 제련해 만듭니다. &a라텍스 처리 장치&r는 라텍스를 "
        "건조 고무로 바꿉니다.\\n\\n&b정리하면 라텍스 -> 건조 고무 -> 플라스틱입니다."
    ],
    "quest.224C07AC71C5F40E.quest_desc": [
        "작업 영역의 식물에 &l뼛가루&r 또는 &#8B4513비료&r를 사용합니다. 한 작물이 "
        "더 이상 &l뼛가루&r를 받지 않을 때까지 계속 &#8B4513비료&r를 사용한 뒤 다음 식물로 "
        "넘어갑니다. 따라서 &e해바라기&r처럼 계속 &l뼛가루&r를 받거나 최종 성장 단계가 "
        "없는 식물에서는 작업이 멈출 수 있습니다.\\n\\n이 기계는 범위 업그레이드를 "
        "지원합니다."
    ],
    "quest.22702838FC507A2E.quest_desc": [
        "수경 재배대는 에너지와 &9물&r로 위에 심은 작물과 묘목을 키웁니다. 대부분의 "
        "작물을 지원합니다. &b에테르 가스&r를 공급하면 작물을 자동으로 수확해 내부 "
        "버퍼에 넣습니다. 수경 재배 모의 처리기에 사용할 작물 데이터도 수집할 수 "
        "있습니다.\\n\\n묘목이 자랄 공간은 따로 확보해야 합니다."
    ],
    "quest.2580135392DEF522.quest_desc": [
        "일반 수경 재배대가 너무 느리거나 영혼 가속기를 충분히 붙일 공간이 없나요? "
        "모의 수경 재배대를 사용해 보세요. 수경 재배 모의 처리기와 씨앗 또는 묘목으로 "
        "원하는 작물을 가상으로 재배합니다. &9물&r이나 &b에테르 가스&r도 필요하지 "
        "않습니다. 수경 재배 모의 처리기는 작물을 많이 키울수록 성능이 좋아지지만, "
        "모의 수경 재배대에서는 성장 속도가 더 느립니다.\\n\\n처리기의 성능을 끝까지 "
        "올리려 하지는 마세요. 상상하기 어려울 만큼 오래 걸립니다. Ender IO 퀘스트를 "
        "전부 만드는 시간보다도 훨씬 길 겁니다."
    ],
    "quest.2782EA80C1C74EBD.quest_desc": [
        "몹 분쇄기는 작업 영역의 몹을 &l제거&r하고 전리품을 수집하며, 몹이 주는 "
        "&a경험치&r를 &a정수&r로 바꿉니다. 정수를 만드는 대신 경험치를 사용해 몹 "
        "분쇄기에 약탈 효과를 적용할 수도 있습니다.\\n\\n생성기에 넣을 수 없는 "
        "보스와 일부 몹은 몹 분쇄기에서도 차단됩니다. 이런 몹은 &l제거&r되지 않고 "
        "작업당 75의 피해를 받습니다.\\n\\n이 기계는 범위 업그레이드를 지원합니다."
    ],
    "quest.28B3591BFC0FA08B.quest_desc": [
        "위더 건설기는 이름 그대로 위더를 소환하는 구조물을 만듭니다. ATM Star에 "
        "필요한 위더의 나침반 재료이기도 합니다.\\n\\n&8생성된 위더가 기계를 "
        "폭파하지 못하도록 위더 공격을 견디는 유리로 주변을 둘러싸는 편이 좋습니다."
    ],
    "quest.339DF320DDCAD98B.quest_desc": [
        "수송기는 1블록 떨어진 인벤토리 사이에서 아이템이나 유체를 옮깁니다. 추출 "
        "쪽과 삽입 쪽에 각각 수송기가 하나씩 필요합니다. 가운데 영역을 우클릭하면 "
        "모드를 바꿀 수 있습니다.\\n\\n한 블록에 여러 종류의 수송기를 함께 둘 수 "
        "있습니다. 속도 업그레이드는 전송 속도를, 효율 업그레이드는 전송량을 "
        "늘립니다."
    ],
    "quest.34AA079FFAFC64BD.quest_desc": [
        "유체 체질기는 &bIndustrial Foregoing&r 광석 가공의 마지막 단계입니다. "
        "모래로 발효 광석 고기의 유용한 성분을 걸러 광물 가루를 만듭니다. 가루는 "
        "제련하거나 합금 재료로 사용하세요."
    ],
    "quest.3AFDE3396861A944.quest_desc": [
        "마법 부여 적용기는 자동 모루입니다. 마법이 부여된 책의 마법을 장비에 자동으로 "
        "적용하며, &a경험치&r 대신 &a정수&r를 사용합니다. 기계 바로 위의 탱크에서도 "
        "유체를 받아 장비 마법 부여의 최대 비용을 높일 수 있습니다."
    ],
    "quest.3E6706BC4C318A40.quest_desc": [
        "오물통은 작업 영역의 동물에게서 &#8B4513오물&r을 모으고, 플레이어의 "
        "&a경험치&r를 흡수해 &a정수&r로 바꿉니다.\\n\\n오물 처리기는 "
        "&#8B4513오물&r을 &#8B4513비료&r로 바꿉니다.\\n\\n오물통은 범위 "
        "업그레이드를 지원합니다."
    ],
    "quest.41E8550FC36ABCA5.quest_desc": [
        "거의 무한히 충전할 수 있어 인피니티 도구라고 부릅니다. 도구의 등급을 "
        "높이면 특별한 능력이 추가됩니다. &5바이오연료&r를 채워 두면 사용할 때 "
        "전력 대신 연료를 소비해 더 효율적으로 작동합니다.\\n\\n등급은 7가지입니다:\\n"
        "조악\\n일반\\n고급\\n희귀\\n영웅\\n전설\\n유물\\n\\n각 도구의 자세한 기능은 "
        "Industrial Foregoing 설명서에서 확인하세요. 한 퀘스트에 모든 도구를 "
        "설명하지 않아도 되니 다행이네요!"
    ],
    "quest.485AFAE5BBEF2FC7.quest_desc": [
        "동물 목장기는 &z양&r의 털을 깎고 &8소&r에게서 &8우유&r를 짭니다.\\n\\n"
        "동물 먹이 공급기는 동물에게 먹이를 주어 번식시킵니다.\\n\\n동물 새끼 "
        "분리기는 새끼를 기계 뒤쪽으로 순간이동시킵니다.\\n\\n이 기계들은 모두 "
        "범위 업그레이드를 지원합니다."
    ],
    "quest.605A5AC65BC7E864.quest_desc": [
        "해양 어획기는 자동으로 낚시해 물고기, 보물, 마법이 부여된 책 등을 잡습니다. "
        "다만 벌은 잡지 못하므로 벌 낚시는 직접 해야 합니다.\\n\\n3x3 이상의 &9물&r "
        "웅덩이 위에 설치해야 합니다."
    ],
    "quest.616CFD4078D67B51.quest_desc": [
        "컨베이어는 아이템, 개체, 유체를 옮기는 또 다른 방법입니다. 컨베이어 "
        "업그레이드를 장착하면 월드와도 상호작용할 수 있습니다.\\n\\n발광석으로 "
        "업그레이드하면 더 빨라지고, 플라스틱으로 업그레이드하면 위의 아이템을 "
        "주울 수 없게 합니다."
    ],
    "quest.65C147F5282E8FCD.quest_desc": [
        "인피니티 충전기는 인피니티 도구를 충전하기에 가장 좋습니다. &l매우 많은&r "
        "FE를 저장하므로 인피니티 도구에 적합합니다.\\n\\n다른 아이템도 충전할 수 "
        "있습니다."
    ],
    "quest.6C001E18093FC037.quest_desc": [
        "식물 수확기는 작업 영역의 식물을 수확합니다. 수확하면 슬러지 정제기에 넣을 "
        "수 있는 &#5919B6슬러지&r가 생길 수 있습니다. &b에테르 가스&r를 공급하면 "
        "작물을 자동으로 다시 심습니다.\\n\\n식물 파종기는 작물과 묘목을 자동으로 "
        "심습니다. 색상으로 구분된 9개 인벤토리 슬롯은 기계 윗면의 표시와 대응하며, "
        "작업 영역의 9개 구역에 각각 해당 슬롯의 씨앗을 심습니다.\\n\\n두 기계 모두 "
        "범위 업그레이드를 지원합니다."
    ],
    "quest.6FF04DD735346BED.quest_desc": [
        "라텍스를 건조 고무로 바꿉니다. 건조 고무 1개를 만드는 데 라텍스 750mB와 "
        "&9물&r 500mB를 사용합니다."
    ],
    "quest.418E57E34FFC19E1.quest_desc": [
        "광석 레이저 베이스는 &bIndustrial Foregoing&r의 공허 채굴기로, 허공에서 "
        "광석을 생성합니다. 렌즈를 사용하면 청금석의 파란색처럼 특정 색상의 광석이 "
        "나올 확률을 높일 수 있습니다.\\n\\n유체 레이저 베이스는 허공이나 특정 "
        "몹에게서 유체를 생산합니다. 각 유체에 맞는 렌즈가 필요하며, 유체를 추출당하는 "
        "몹은 피해를 받으므로 정지장을 함께 사용하는 편이 좋습니다.\\n\\n레이저 "
        "드릴은 작업 영역 안의 레이저 베이스에 진행도를 공급합니다."
    ],
    "quest.4DB5DD6E20619B4D.quest_desc": [
        "기계의 성능을 높이는 데 사용합니다. 일반 업그레이드는 4개 등급이며, 범위 "
        "업그레이드는 별도로 8개 등급이 있습니다."
    ],
    "quest.4F3EF1574F31A7E2.quest_desc": [
        "정지장은 작업 영역의 몹을 제자리에 고정하고 회복시킵니다. 회복량이 더 "
        "필요하다면 업그레이드를 장착하세요!"
    ],
    "quest.79D48F8F31B152C3.quest_desc": [
        "&bIndustrial Foregoing &#27AEB9Souls&r는 다른 기계를 가속하는 장치를 "
        "추가합니다.\\n\\n&#27AEB9영혼 레이저 베이스&r는 이 시스템의 핵심이며, 위더에서 "
        "에테르 가스를 추출하는 유체 레이저 베이스와 비슷하게 작동합니다. &9파란색 "
        "레이저 렌즈&r로 &#27AEB9워든&r에게서 &#27AEB9영혼&r을 추출합니다. 영혼은 "
        "&#27AEB9영혼 파이프&r나 AE2·RS 저장망으로 꺼내고, &#27AEB9영혼&r은 "
        "&#27AEB9영혼 가속기&r에 공급해 블록을 가속합니다.\\n\\n&#27AEB9워든&r에게서 "
        "&#27AEB9영혼&r을 추출하는 과정은 "
        "대상에게 &4&l고통스럽고&r 피해를 주며, 죽을 수도 있습니다. 정지장을 사용하고 "
        "회복 속도 업그레이드도 충분히 장착하는 것을 권장합니다.",
        "{@pagebreak}",
        "다음과 같이 바닥과 &#27AEB9영혼 레이저 베이스&r 사이를 3블록 비우세요:",
        "{image:atm:textures/questpics/industrialforegoing/soul_laser_gap.png width:100 height:100 align:center}",
        "또한 &#27AEB9워든&r이 완전히 땅 위로 나온 뒤 정지장에 넣으세요.",
    ],
    "quest.7CB4D47ABC295B92.quest_desc": [
        "물약을 양조합니다. 일반 양조기처럼 블레이즈 가루를 연료로 쓰고 병이 필요하지만, "
        "병에 물을 자동으로 채울 수 있습니다.\\n\\n이 기계는 일부 동작이 직관적이지 "
        "않으므로 다른 퀘스트에서 자동화 구성을 자세히 안내합니다."
    ],
    "quest.0BB42C5861B22D32.quest_desc": [
        "&b균사 반응기&r는 주변의 모든 균사 발전기가 동시에 작동할 때 총 "
        "&a25MFE/t&r를 생산합니다.\\n\\n작동시키려면 각 균사 발전기가 소비하는 "
        "자원을 확인해 모두 자동화해야 합니다. 대부분은 간단하지만 일부는 그렇지 "
        "않습니다... &o특히 마법 추출 균사 발전기 말이죠&r.\\n\\n모든 공급을 "
        "자동화했다면 반응기를 하나만 둘 필요도 없습니다. 더 만들어도 됩니다."
    ],
    "quest.23254CE8487D2E68.quest_desc": [
        "&8위더 건설기&r는 &lIndustrial Foregoing&r에서 얻을 수 있는 최고의 기계 "
        "중 하나이며, 그만큼 비쌉니다. \\n\\n먼저 &8위더&r를 만드는 재료와 "
        "&8위더&r의 전리품이 필요합니다.\\n\\n그다음에는 &b에테르 가스&r로 "
        "만드는 &6최고급 기계 프레임&r이 필요합니다. &b에테르 가스&r도 "
        "&8위더&r에게 레이저 드릴을 작동시켜 얻습니다. &8위더&r가 필요하다는 "
        "뜻이죠!\\n\\n&8위더&r가 날아가 다른 대상을 "
        "공격하지 못하도록 정지장을 사용하면 훨씬 쉽게 에테르 가스를 추출할 수 "
        "있습니다!"
    ],
}

TEXT_REPLACEMENTS = (
    ("인더스트리얼 포어고잉", "Industrial Foregoing"),
    ("인더스트리얼 포고잉", "Industrial Foregoing"),
    ("인더스트리얼 포어 고잉", "Industrial Foregoing"),
    ("산업 전술", "Industrial Foregoing"),
    ("머신 프레임", "기계 프레임"),
    ("기계 틀", "기계 프레임"),
    ("미천한 기계 프레임", "조악한 기계 프레임"),
    ("간단한 기계 프레임", "기본 기계 프레임"),
    ("발전된 기계 프레임", "고급 기계 프레임"),
    ("핑크 슬라임", "분홍색 슬라임"),
    ("분홍 슬라임", "분홍색 슬라임"),
    ("드라이 러버", "건조 고무"),
    ("액체 고기", "액상 고기"),
    ("에센스", "정수"),
    ("인첸트", "마법 부여"),
    ("인챈트", "마법 부여"),
    ("디스인챈트", "마법 추출"),
    ("상위 버전으로 변환", "업그레이드"),
    ("애드온", "업그레이드"),
    ("스포너", "생성기"),
    ("몹 감금 도구", "몹 포획기"),
    ("몹 투옥 도구", "몹 포획기"),
    ("업그레이드을", "업그레이드를"),
    ("정지장를", "정지장을"),
    ("레이저 기반", "레이저 베이스"),
    ("건식 고무", "건조 고무"),
    ("미천한 발전기", "조악한 발전기"),
    ("정지 챔버", "정지장"),
    ("소울 파이프", "영혼 파이프"),
    ("소울 서지", "영혼 가속기"),
    ("소울", "영혼"),
    ("액세스", "이용"),
    ("항목", "아이템"),
    ("우측 누르기", "우클릭"),
    ("오른쪽 누르기", "우클릭"),
)

ALLOWED_EXACT_KEYS = {
    "chapter.193F91842D2ED7D9.title",
    "quest.11374A3B5BD644F5.title",
    "quest.55820773BDD5319D.title",
    "quest.79D48F8F31B152C3.title",
    "quest.3924975B48F5A482.title",
    "task.6B17A0D9906E8C90.title",
    "task.7058D3373DA87B34.title",
}

SOURCE_OVERRIDES = {
    (
        "The Bioreactor produces &5Biofuel&r with &9Water&r and a bunch of "
        "different materials (check JEI for all valid Bioreactor Inputs). The more "
        "types of materials you provide, the more efficient the Bioreactor is at "
        "producing &5Biofuel&r.\\n\\nThe Biofuel Generator uses &5Biofuel&r made "
        "from the &5Bioreactor&r to generate FE."
    ): (
        "생물 반응기는 &9물&r과 여러 종류의 재료로 &5바이오연료&r를 생산합니다. "
        "사용 가능한 재료는 JEI에서 확인하세요. 서로 다른 종류의 재료를 많이 넣을수록 "
        "생물 반응기의 &5바이오연료&r 생산 효율이 높아집니다.\\n\\n바이오연료 "
        "발전기는 &5생물 반응기&r가 만든 &5바이오연료&r로 FE를 생산합니다."
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


def iter_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for child in value for text in iter_strings(child)]
    return []


def map_strings(value: object, translations: dict[str, str]) -> object:
    if isinstance(value, str):
        return translations[value]
    if isinstance(value, list):
        return [map_strings(child, translations) for child in value]
    return value


def candidate() -> dict[str, object]:
    """미번역 퀘스트 문구의 보호 처리된 후보를 만든다."""
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests: set[str] = set()
    english_by_scope: dict[str, dict[str, object]] = {}
    sources_by_scope: dict[str, dict[str, object]] = {}
    for root in sorted(QUEST_ROOT.glob("*")):
        if not (root / "en_us.json").is_file():
            continue
        english = load_json(root / "en_us.json")
        sources = load_json(root / "candidate_sources.json")
        english_by_scope[root.name] = english
        sources_by_scope[root.name] = sources
        for key, value in english.items():
            if sources[key] != "new_translation_required":
                continue
            for source in iter_strings(value):
                if (
                    not re.fullmatch(r"\{image:[^}]+\}", source)
                    and source not in SOURCE_OVERRIDES
                    and not isinstance(cache.get(source), str)
                ):
                    requests.add(source)
    failures: list[str] = []
    if requests:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(ars_family.request_translation, source): source
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
        raise RuntimeError("퀘스트 후보 생성 실패:\n" + "\n".join(failures))

    candidates: dict[str, dict[str, object]] = {}
    for scope, english in english_by_scope.items():
        rows: dict[str, object] = {}
        for key, value in english.items():
            if sources_by_scope[scope][key] != "new_translation_required":
                continue
            translations = {
                source: (
                    source
                    if re.fullmatch(r"\{image:[^}]+\}", source)
                    else SOURCE_OVERRIDES.get(source, cache.get(source))
                )
                for source in iter_strings(value)
            }
            rows[key] = map_strings(value, translations)
        candidates[scope] = rows
    write_json(CANDIDATE_FILE, candidates)
    report = {
        "candidate_keys": sum(len(rows) for rows in candidates.values()),
        "unique_requests": len(requests),
        "review_status": "candidate_requires_full_review",
    }
    write_json(QUEST_ROOT.parent / "quest_auto_candidate_report.json", report)
    return report


def item_name_pairs() -> tuple[tuple[str, str], ...]:
    english = language.load_json(
        PROJECT_ROOT / "working/industrial_foregoing/industrialforegoing/en_us.json"
    )
    korean = language.load_json(
        PROJECT_ROOT / "working/industrial_foregoing/industrialforegoing/ko_kr.json"
    )
    pairs = [
        (source, korean[key])
        for key, source in english.items()
        if key.startswith(("block.", "item.", "fluid_type.", "entity."))
        and isinstance(source, str)
        and isinstance(korean[key], str)
    ]
    return tuple(sorted(pairs, key=lambda row: len(row[0]), reverse=True))


def review_text(value: object, pairs: tuple[tuple[str, str], ...]) -> object:
    if isinstance(value, list):
        return [review_text(child, pairs) for child in value]
    if not isinstance(value, str):
        return value
    if re.fullmatch(r"\{image:[^}]+\}", value):
        return value
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    for old, new in pairs:
        value = value.replace(old, new)
    value = value.replace("모드 팩", "모드팩")
    value = value.replace("해야합니다", "해야 합니다")
    value = value.replace("할 수있는", "할 수 있는")
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    return value


def normalize() -> dict[str, object]:
    """신규 후보를 반영하고 기존 한국어 전부를 다시 검수한다."""
    candidates = load_json(CANDIDATE_FILE)
    pairs = item_name_pairs()
    reviewed = 0
    changed = 0
    unresolved: list[str] = []
    for root in sorted(QUEST_ROOT.glob("*")):
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        if not english_file.is_file() or not korean_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        scope_candidates = candidates.get(root.name, {})
        for key, source in english.items():
            base = scope_candidates.get(key, korean[key])
            translated = KEY_OVERRIDES.get(key, review_text(base, pairs))
            errors = quest_snbt.validate_value(key, source, translated)
            if errors:
                raise ValueError("; ".join(errors))
            reviewed += 1
            if korean[key] != translated:
                korean[key] = translated
                changed += 1
            if source == translated and key not in ALLOWED_EXACT_KEYS:
                if any(
                    re.search(r"[A-Za-z]{3,}", text) for text in iter_strings(source)
                ):
                    unresolved.append(key)
        write_json(korean_file, korean)
    report = {
        "keys_reviewed": reviewed,
        "changed": changed,
        "unresolved": len(unresolved),
        "unresolved_examples": unresolved[:30],
        "review_status": "full_existing_korean_reviewed",
    }
    write_json(QUEST_ROOT.parent / "quest_normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    untranslated: list[str] = []
    reviewed = 0
    for root in sorted(QUEST_ROOT.glob("*")):
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        if not english_file.is_file() or not korean_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        if list(english) != list(korean):
            errors.append(f"키 또는 순서 불일치: {root.name}")
            continue
        for key, source in english.items():
            target = korean[key]
            errors.extend(quest_snbt.validate_value(key, source, target))
            reviewed += 1
            if source == target and key not in ALLOWED_EXACT_KEYS:
                if any(
                    re.search(r"[A-Za-z]{3,}", text) for text in iter_strings(source)
                ):
                    untranslated.append(key)
    if untranslated:
        errors.append(f"미번역 퀘스트 키: {untranslated[:30]}")
    report = {
        "keys_reviewed": reviewed,
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(QUEST_ROOT.parent / "specialized_quest_validation.json", report)
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("candidate", "normalize", "verify"))
    args = parser.parse_args()
    if args.command == "candidate":
        result = candidate()
        status = 0
    elif args.command == "normalize":
        result = normalize()
        status = 0
    else:
        result, status = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
