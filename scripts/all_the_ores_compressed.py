#!/usr/bin/env python3
"""All The Ores와 All The Compressed 언어 작업본을 생성하고 검증한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

from five_family_goal import PROJECT_ROOT, load_json, validate_value
from local_paths import resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/all_the_ores_compressed"

MATERIALS = {
    "aluminum": "알루미늄",
    "brass": "황동",
    "bronze": "청동",
    "cinnabar": "진사",
    "constantan": "콘스탄탄",
    "copper": "구리",
    "diamond": "다이아몬드",
    "electrum": "일렉트럼",
    "enderium": "엔더리움",
    "fluorite": "형석",
    "gold": "금",
    "invar": "인바",
    "iridium": "이리듐",
    "iron": "철",
    "lead": "납",
    "lumium": "루미움",
    "netherite": "네더라이트",
    "nickel": "니켈",
    "osmium": "오스뮴",
    "peridot": "페리도트",
    "platinum": "백금",
    "ruby": "루비",
    "salt": "소금",
    "sapphire": "사파이어",
    "signalum": "시그널륨",
    "silver": "은",
    "steel": "강철",
    "sulfur": "황",
    "tin": "주석",
    "uranium": "우라늄",
    "zinc": "아연",
}

ITEM_FORMS = {
    "ore_hammer": "광석 망치",
    "clump": "덩어리",
    "crystal": "결정",
    "dust": "가루",
    "gear": "기어",
    "ingot": "주괴",
    "nugget": "조각",
    "plate": "판",
    "rod": "막대기",
    "shard": "파편",
}

COMPRESSED_OVERRIDES = {
    "ancient_log_0": "고대 원목",
    "ancient_rock": "고대 바위",
    "antimatter_block": "반물질 블록",
    "allthemodium_block": "Allthemodium 블록",
    "baobab_log": "바오밥나무 원목",
    "baobab_planks": "바오밥나무 판자",
    "black_concrete": "검은색 콘크리트",
    "blaze_rod_block": "블레이즈 막대 블록",
    "blue_concrete": "파란색 콘크리트",
    "blue_ice": "푸른얼음",
    "brass_block": "황동 블록",
    "bricks": "벽돌",
    "brown_concrete": "갈색 콘크리트",
    "charged_redstone_block": "충전된 레드스톤 수정 블록",
    "cherry_log": "벚나무 원목",
    "cherry_planks": "벚나무 판자",
    "cinnabar_block": "진사 블록",
    "compressed_iron_block": "압축 철 블록",
    "crushed_blackstone": "부서진 흑암",
    "crushed_deepslate": "부서진 심층암",
    "crushed_end_stone": "부서진 엔드 돌",
    "crushed_netherrack": "부서진 네더랙",
    "cyan_concrete": "청록색 콘크리트",
    "dark_steel_block": "다크 스틸 블록",
    "darkstone": "다크스톤",
    "dried_kelp_block": "말린 켈프 블록",
    "dust": "가루",
    "emberstone_block": "엠버스톤 블록",
    "ender_pearl_block": "엔더 진주 블록",
    "end_steel_block": "엔드 스틸 블록",
    "energetic_alloy_block": "에너지 합금 블록",
    "entro_block": "엔트로 결정 블록",
    "fluorite_block": "형석 블록",
    "gray_concrete": "회색 콘크리트",
    "green_concrete": "초록색 콘크리트",
    "greg_star_block": "GregStar 블록",
    "honeycomb_block": "벌집 블록",
    "jade_block": "비취 블록",
    "kivi": "Kivi",
    "light_blue_concrete": "하늘색 콘크리트",
    "light_gray_concrete": "회백색 콘크리트",
    "lime_concrete": "연두색 콘크리트",
    "limonite_block": "갈철석 블록",
    "magenta_concrete": "자홍색 콘크리트",
    "magma_block": "마그마 블록",
    "mud": "진흙",
    "mycelium": "균사체",
    "nether_wart_block": "네더 사마귀 블록",
    "orange_concrete": "주황색 콘크리트",
    "packed_mud": "다진 진흙",
    "piglich_heart_block": "피글리치 심장 블록",
    "pink_concrete": "분홍색 콘크리트",
    "precasian_cobblestone": "Precasian 조약돌",
    "precasian_soil": "Precasian 토양",
    "precasian_stone": "Precasian 돌",
    "pulsating_alloy_block": "맥동 합금 블록",
    "purple_concrete": "보라색 콘크리트",
    "raw_allthemodium_block": "Allthemodium 원석 블록",
    "raw_aluminum_block": "알루미늄 원석 블록",
    "raw_copper_block": "구리 원석 블록",
    "raw_emberstone_block": "엠버스톤 원석 블록",
    "raw_gold_block": "금 원석 블록",
    "raw_iridium_block": "이리듐 원석 블록",
    "raw_iron_block": "철 원석 블록",
    "raw_lead_block": "납 원석 블록",
    "raw_limonite_block": "갈철석 원석 블록",
    "raw_nickel_block": "니켈 원석 블록",
    "raw_osmium_block": "오스뮴 원석 블록",
    "raw_platinum_block": "백금 원석 블록",
    "raw_silver_block": "은 원석 블록",
    "raw_tin_block": "주석 원석 블록",
    "raw_unobtainium_block": "Unobtainium 원석 블록",
    "raw_uranium_block": "우라늄 원석 블록",
    "raw_vibranium_block": "Vibranium 원석 블록",
    "raw_zinc_block": "아연 원석 블록",
    "red_concrete": "빨간색 콘크리트",
    "salt_block": "소금 블록",
    "silicon_block": "실리콘 블록",
    "skeletal_ingot_block": "Skeletal 주괴 블록",
    "sky_bronze_block": "하늘 청동 블록",
    "sky_osmium_block": "하늘 오스뮴 블록",
    "sky_steel_block": "하늘 강철 블록",
    "smooth_stone": "매끄러운 돌",
    "snow": "눈 블록",
    "sponge": "스펀지",
    "stranglewood_log": "Stranglewood 원목",
    "stranglewood_planks": "Stranglewood 판자",
    "sulfur_block": "황 블록",
    "unobtainium_allthemodium_alloy_block": "Unobtainium-Allthemodium 합금 블록",
    "unobtainium_block": "Unobtainium 블록",
    "unobtainium_vibranium_alloy_block": "Unobtainium-Vibranium 합금 블록",
    "vibranium_allthemodium_alloy_block": "Vibranium-Allthemodium 합금 블록",
    "vibranium_block": "Vibranium 블록",
    "vibrant_alloy_block": "활기찬 합금 블록",
    "warped_wart_block": "뒤틀린 사마귀 블록",
    "white_concrete": "하얀색 콘크리트",
    "xychorium_storage_blue": "파란색 Xychorium 보석 저장고",
    "xychorium_storage_dark": "어두운 Xychorium 보석 저장고",
    "xychorium_storage_green": "초록색 Xychorium 보석 저장고",
    "xychorium_storage_light": "밝은 Xychorium 보석 저장고",
    "xychorium_storage_red": "빨간색 Xychorium 보석 저장고",
    "yellow_concrete": "노란색 콘크리트",
}

QUEST_OVERRIDES = {
    "quest.6D6E07564D8FDD8D.quest_desc": [
        "&aExtreme Reactors&r는 크기와 효율 등을 자유롭게 조정할 수 있는 멀티블록 원자로를 제공합니다.\\n\\nExtreme Reactors를 시작하는 방법은 해당 모드의 퀘스트 챕터에서 자세히 알아보세요!"
    ],
    "quest.6D6E07564D8FDD8D.title": "&9Extreme Reactors: &a원자로",
    "quest.3331EBE1BB4BF64D.quest_desc": [
        "원자로의 위험한 영향 때문에 무섭다고 느끼는 분도 있을 거예요! \\n\\n다행히 &a&lExtreme Reactors&r에서 무서운 것은 복잡한 조합법을 따라가는 일뿐입니다! \\n\\n폭발하지는 않으니 안심하세요."
    ],
    "quest.3331EBE1BB4BF64D.title": "&a&lExtreme Reactors",
    "quest.14E5349DD740D026.quest_desc": [
        "원자로에 연료를 넣으려면 &9원자로 고체 액세스 포트&r가 있는 면을 골라 인벤토리에서 &e우라늄&r을 공급해야 합니다.\\n\\n가장 쉬운 방법은 아래 그림처럼 &a저장 서랍&r이나 &a상자&r를 놓고 위쪽에 &9아이템 파이프&r를 연결하는 것입니다.\\n",
        "{image:atm:textures/questpics/extremereactors/importexample.png width:150 height:150 align:1}",
    ],
    "quest.7C4E4793DA887DE4.quest_subtitle": "먹을 수 있는 게 아니에요... 정말이에요",
    "quest.7C4E4793DA887DE4.title": "&9Extreme Reactors&r에 오신 것을 환영합니다!",
    "quest.1A8F2408970BFCCF.quest_desc": [
        "&e일렉트럼&r은 &e금&r과 &7은&r으로 만든 합금입니다. \\n\\n이름에서 짐작할 수 있듯이 전선, 연결기, 변압기 등 전기와 관련된 곳에 아주 많이 사용됩니다!"
    ],
    "quest.2262AB9F934165D0.quest_desc": [
        "어떻게 구했는지는 상관없어요. 일단 가져오기만 하세요! \\n\\n&8&lImmersive Engineering&r에서는 단순한 건축물 외에도 &8강철&r을 아주 많이 사용합니다. 거의 모든 것을 만드는 데 &8강철&r이 필요할 거예요! \\n\\n주로 도구, 기계 부품, 건축 블록에 쓰이며, 그중 많은 것이 &8강철 판&r이나 &8비계&r로 만들어집니다. \\n\\n많은 양이 필요하지만 &l&c조잡한 용광로&r와 &l&6합금 가마&r는 자동화할 수 없으니 다른 방법이 필요할지도 모릅니다..."
    ],
    "quest.30EA16BB8C169F86.quest_desc": [
        "&6구리&r와 &7주석&r을 섞어 만든 합금입니다! \\n\\n&7&lModern Industrialization&r에서는 아주 많이 사용되지만 &8&lIE&r에서는... 그다지 많이 쓰이지 않습니다."
    ],
    "quest.4BA2F4AC2A08C294.quest_desc": [
        "이게 뭐냐고요? &8&lImmersive Engineering&r에서 가장 어렵고 비싼 멀티블록인 &c&l굴착기&r입니다! \\n\\n이 거대한 기계는 땅에서 광석과 블록을 자동으로 채굴합니다. \\n\\n채굴한 아이템은 뒤쪽 포트로 &6출력&r됩니다. 인접한 인벤토리가 없으면 아이템을 바닥에 내보냅니다. \\n\\n또한 &c에너지&r를 엄청나게 소비하므로 왼쪽의 에너지 포트로 전력을 공급해야 합니다!",
        "{@pagebreak}",
        "&8강철 블록&r을 하나 놓습니다.",
        "{image:atm:textures/questpics/immersive/immersive_excavator1.png width:100 height:100 align:center}",
        "&8강철 블록&r 위에 &8강철 비계&r 3개를 놓고 양 끝에 &8강철 블록&r 2개를 나누어 놓습니다.",
        "{image:atm:textures/questpics/immersive/immersive_excavator2.png width:175 height:100 align:center}",
        "앞서 놓은 &8비계&r 위에 &8강철 비계&r를 3x3으로 놓고, 양쪽 &8강철 블록&r 위에도 하나씩 추가합니다. 그런 다음 &8강철 판금&r으로 &8비계&r에서 이어지는 고리를 만들고, 그 안에 &e경공업 블록&r과 &8방열기 블록&r을 넣습니다. ",
        "{image:atm:textures/questpics/immersive/immersive_excavator3.png width:150 height:100 align:center}",
        "&8강철 비계&r 위에 비계를 더 놓고 가운데에 &8강철 블록&r을 놓습니다. 그 양 끝에도 &8강철 블록&r을 더 붙입니다. 한쪽에는 &e경공업 블록&r 3개를, 다른 쪽에는 &7중공업 블록&r 3개를 놓습니다. 이전 층의 &e경공업 블록&r 위에 하나를 더 놓고, &8방열기 블록&r 위에는 &4레드스톤 공학 블록&r을 놓습니다. 그 옆에는 &7중공업 블록&r을 하나 더 놓고 나머지는 &8강철 판금&r으로 채웁니다.",
        "{image:atm:textures/questpics/immersive/immersive_excavator4.png width:150 height:100 align:center}",
        "가운데 부분은 아래쪽 절반과 같은 구조를 반복하므로 우선 &8강철 비계&r를 놓습니다. &e경공업 블록&r이 있는 면에는 3개를 더 놓고, 반대편의 따로 놓인 &e경공업 블록&r에도 같은 방식으로 놓습니다. &e경공업 블록&r 3개 옆에는 &8방열기 블록&r 2개를 놓고 나머지는 &8판금&r으로 채웁니다.",
        "{image:atm:textures/questpics/immersive/immersive_excavator5.png width:150 height:100 align:center}",
        "&8강철 비계&r 위에 &8강철 블록&r 1개, &8비계&r 3개, 그리고 또 다른 &8블록&r을 차례로 놓습니다.",
        "{image:atm:textures/questpics/immersive/immersive_excavator6.png width:150 height:100 align:center}",
        "마지막으로 꼭대기에 &8강철 블록&r을 놓습니다!",
        "{image:atm:textures/questpics/immersive/immersive_excavator7.png width:150 height:100 align:center}",
        "이제 뒤쪽의 &7중공업 블록&r을 &6망치&r로 우클릭하면 강력한 &c&l굴착기&r가 완성됩니다!",
        "{image:atm:textures/questpics/immersive/immersive_excavator.png width:125 height:100 align:center}",
    ],
    "quest.4F56BFE6E4716F6D.quest_desc": [
        "&8&l아크 화로&r는 거대하고 유용한 기계로, 대부분의 다른 기계를 쓸모없게 만들 정도입니다! \\n\\n먼저 &8&l아크 화로&r 뒤쪽의 단자에 &c에너지&r를 공급해야 합니다. 연료로는 &0흑연 전극&r이 필요합니다. 흑연 전극은 GUI에서만 넣을 수 있으며 자동화할 수 없습니다. \\n\\n그런 다음 &0흑연 전극&r 근처의 위쪽 포트로 &e아이템&r을 &6입력&r합니다. 연료와 전력이 공급되면 &7철 막대기&r를 &7철 주괴&r로, &b서리강철 투구&r를 &b서리강철&r로, &e금 곡괭이&r를 &e금&r으로 만드는 등 거의 모든 것을 녹일 수 있습니다! \\n\\n녹인 &e아이템&r은 전력 단자 아래의 뒤쪽 포트로 &6출력&r됩니다. \\n\\n금속으로 합금을 만들 수도 있습니다!",
        "{@pagebreak}",
        "1번째 층은 &8강철 판금&r으로 U자를 만들고, 가운데에는 &7중공업 블록&r을, 양 끝에는 &8강철 블록&r을 놓습니다. 나머지는 &8강철 판금 반 블록&r으로 채우되 &8강철 비계&r 하나와 가마솥을 놓습니다.",
        "{image:atm:textures/questpics/immersive/immersive_arc1.png width:100 height:100 align:center}",
        "2번째 층은 &7중공업 블록&r과 그 양옆 블록 2개 위에 &e경공업 블록&r을 놓습니다. U자의 양쪽에는 &7중공업 블록&r을 놓고, 이전의 &8강철 블록&r 위에도 강철 블록을 더 놓습니다. &8반 블록&r 위에는 &4강화 용광로 벽돌&r을 2x3으로 쌓습니다. &8비계&r 위의 &4레드스톤 공학 블록&r도 잊지 마세요!",
        "{image:atm:textures/questpics/immersive/immersive_arc2.png width:100 height:100 align:center}",
        "3번째 층에는 &8강철 블록&r과 &e경공업 블록&r을 더 놓고 &4강화 용광로 벽돌&r 구조를 위로 연장합니다. 양쪽에 &8강철 판금&r도 1개씩 필요합니다.",
        "{image:atm:textures/questpics/immersive/immersive_arc3.png width:100 height:100 align:center}",
        "4번째 층에는 앞서 놓은 블록 위 가운데에 &e경공업 블록&r을 놓고 그 옆에 &8강철 비계&r 2개를 놓습니다. &4강화 용광로 벽돌&r도 더 쌓되 이번에는 길이를 한 블록 줄입니다!",
        "{image:atm:textures/questpics/immersive/immersive_arc4.png width:100 height:100 align:center}",
        "5번째이자 마지막 층은 앞서 놓은 비계 위에 &8강철 비계&r 2개를 더 놓습니다. 이전 &e경공업 블록&r 위와 그 앞쪽 일렬에도 경공업 블록을 놓습니다.",
        "{image:atm:textures/questpics/immersive/immersive_arc5.png width:100 height:100 align:center}",
        "마지막으로 가마솥을 &6망치&r로 우클릭하면 완성됩니다!",
        "{image:atm:textures/questpics/immersive/immersive_arc.png width:100 height:100 align:center}",
    ],
    "quest.73110103EF23BFDF.quest_desc": [
        "&6구리&r와 &7아연&r을 섞어 만든 합금입니다. \\n\\n&8&lIE&r에서는 그다지 많이 쓰이지 않지만... 이것으로 표지판을 만들 수는 있습니다."
    ],
    "quest.4B35C01F5D0AAC58.quest_desc": [
        "이제 &9&l야금 주입기&r와 약간의 &c에너지&r가 준비되었으니 &8강철&r을 만들어 봅시다! \\n\\n&e화학 물질 막대&r에 &0탄소&r가 필요합니다. &0석탄&f, &0숯&r 또는 그 변형을 &e화학 물질 슬롯&f에 넣어 &0탄소&r를 채울 수 있습니다. \\n\\n그런 다음 &7철 주괴&f/&7가루&r를 &4아이템 슬롯&r에 넣으면 탄소 10mB를 주입해 농축 철을 만듭니다. \\n\\n같은 단계를 반복해 &7농축 철&r에 &0탄소&r 10mB를 주입하면 &8강철 가루&r가 됩니다! &8가루&r를 제련하면 &8강철 주괴&r를 얻습니다. \\n\\n&8강철&r은 기계, 도구, 업그레이드, 원자로, 에너지 셀 등 거의 모든 곳에 사용되므로 많이 필요합니다."
    ],
    "quest.4B35C01F5D0AAC58.title": "&8강철 ",
    "quest.6F62B5510FA881CD.quest_desc": [
        "&7오스뮴&r은 Y 56 아래에서 생성되는 광석입니다. 광석의 모양은 &a에메랄드&r와 비슷하며 색은 &b푸른빛이 도는&7 회색&r입니다! \\n\\n&5&lMekanism&r의 여러 &5기계&r에 사용되므로 많이 필요할 거예요! \\n\\n&7방어구 &f및 &7도구&r도 만들 수 있습니다! &7방어구 &f및 &7검&r의 성능 수치는 &c네더라이트&r와 같고, &7곡괭이&r는 &7철 곡괭이&r와 같습니다."
    ],
    "quest.7276892E129A739B.quest_desc": [
        "이게 &5&lMekanism&r의 전부라고 생각하셨나요? 아직 갈 길이 멉니다! \\n\\n그 전에 &5기계 &f와 &a황&r부터 준비해 봅시다! \\n\\n앞으로 긴 여정이 기다리고 있습니다."
    ],
    "quest.078B69E9362A5496.quest_desc": [
        "네, &5&lMekanism&r은 정말 방대한 모드입니다! \\n\\n&2&l원자로&r와 무적에 가까운 방어구를 원한다면 제대로 찾아오셨습니다! \\n\\n먼저 &2&l핵분열로&r가 필요하며, 여기에는 &2핵분열성 연료&r가 필요합니다. &2핵분열성 연료&r를 만들려면 &c삼산화황&r부터 준비해야 합니다. \\n\\n&e황&r을 &c&l화학적 &e산화 장치&r에 넣어 &e이산화황&r을 만드는 것부터 시작하세요. \\n\\n그런 다음 &9&l전해 분리기&r로 &9물&r을 처리해 &b산소&r를 만드세요. \\n\\n이제 &b산소&r와 &e이산화황&r을 &c튜브&r로 &c&l화학 주입기&r에 공급해 &c삼산화황&r을 만들 수 있습니다."
    ],
    "quest.1036837C9AD3F301.quest_desc": [
        "&#6E6D6D단조 망치&r를 사용하면 &#FFAC3B구리&r 주괴나 광석을 쉽게 분쇄해 가루로 만들 수 있습니다."
    ],
    "quest.253822C64BBBB1EB.quest_desc": [
        "&#6E6D6D단조 망치&r를 사용하면 &#9AD5ED주석&r 주괴나 광석을 쉽게 분쇄해 가루로 만들 수 있습니다."
    ],
    "quest.7282DCB1547CEB63.quest_desc": [
        "&#ED9553청동&r은 &7&n증기 시대&r의 기반 재료입니다. 이 가루를 구우면 앞으로 사용할 &#ED9553청동 주괴&r를 얻을 수 있습니다."
    ],
    "quest.7282DCB1547CEB63.title": "&#EDD653청동",
    "quest.4F35D04721DFC9FF.quest_desc": [
        "처음 진행할 의식은 &9소환 의식&r입니다. 이 의식은 유용한 여러 악마를 소환하며, 의식 단계가 높아질수록 분쇄와 제련 등 다양한 작업을 도와줍니다.",
        "",
        "첫 의식에서는 &a폴리오트 분쇄기&r 악마를 소환합니다. 이 악마는 아이템을 분쇄하며, 상위 단계의 초크를 만드는 데 필요합니다!",
        "",
        "먼저 제작대에서 속박되지 않은 책과 &a영혼 사전&r을 조합하세요. 그러면 악마가 책에 속박되며, 이 책을 의식에 사용합니다.",
        "",
        '이제 영혼 사전을 열어 보세요! 왼쪽의 &d펜타클&r 탭에서 &b아비아르의 원&r을 선택합니다. 내용을 조금 읽어야 다음 단계가 열릴 수도 있습니다. \\"모두 읽은 것으로 표시\\"를 눌러 책의 모든 내용을 여는 방법도 있습니다.',
        "",
        "이 원을 사용해 새 친구를 소환할 것입니다. 오른쪽 그림의 왼쪽 아래에 있는 눈을 누르면 월드에 의식 구조의 윤곽을 표시할 수 있어 매우 편리합니다!",
        "",
        "멀티블록 의식 구조를 완성했다면 중앙 제물 그릇에서 수평으로 8블록 이내에 제물 그릇을 4개 놓고(이후 의식에는 더 필요할 수 있습니다) 필요한 아이템을 각각 사용하세요. 황금 제물 그릇에 속박된 책을 놓으면 의식이 시작됩니다!",
        "",
        "완성된 의식은 다음과 같은 모습입니다.",
        "",
        "{image:atm:textures/questpics/occultism/aviarcirclenew.png width:200 height:200 align:1}",
    ],
    "quest.5FE507DAEE770507.quest_desc": [
        "&b하늘색 초크&r를 얻으려고 &9마리드 분쇄기&r까지 만들고 싶지 않나요? 그렇다면 대신 &a지니 분쇄기&r를 선택할 수 있습니다. &a오픽스의 부름&r은 &a지니&r를 소환하는 데 사용하며, 악마 배우자도 이에 포함됩니다. &a지니&r는 폴리오트보다 효율적으로 광석을 분쇄하지만 &c아프리트&r나 &9마리드&r만큼 효율적이지는 않습니다. 얼음을 녹이지 않고 분쇄할 수도 있습니다."
    ],
    "quest.5FE507DAEE770507.quest_subtitle": "하늘색 초크를 얻는 다른 길",
    "quest.5FE507DAEE770507.title": "&a오픽스의 부름",
    "quest.0C9F9196CA49FF8D.quest_subtitle": "니켈 광석을 찾아 여정을 시작하세요",
    "quest.0C9F9196CA49FF8D.title": "Oritech의 시작",
}


def dump_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 안정된 형식으로 기록한다."""
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def translate_alltheores(key: str, source: str) -> str:
    """All The Ores 키 구조를 검수한 용어로 변환한다."""
    if key == "itemGroup.alltheores":
        return "All The Ores"
    if key.endswith(".tooltip"):
        match = re.fullmatch(r"§6Found between Y (-?\d+) and Y (-?\d+)", source)
        if not match:
            raise ValueError(f"알 수 없는 광석 높이 툴팁: {key}={source}")
        return f"§6Y {match.group(1)}~Y {match.group(2)} 사이에서 발견"

    prefix, namespace, stem = key.split(".", 2)
    if namespace != "alltheores":
        raise ValueError(f"알 수 없는 네임스페이스: {key}")
    if prefix == "block":
        if stem.startswith("molten_"):
            material = stem.removeprefix("molten_")
            return f"용융 {MATERIALS[material]}"
        ore = re.fullmatch(r"(?:(deepslate|end|nether|other)_)?(.+)_ore", stem)
        if ore:
            location, material = ore.groups()
            location_name = {
                None: "",
                "deepslate": "심층암 ",
                "end": "엔드 ",
                "nether": "네더 ",
                "other": "기타 ",
            }[location]
            return f"{location_name}{MATERIALS[material]} 광석"
        if stem.startswith("raw_") and stem.endswith("_block"):
            material = stem.removeprefix("raw_").removesuffix("_block")
            return f"{MATERIALS[material]} 원석 블록"
        if stem.endswith("_block"):
            return f"{MATERIALS[stem.removesuffix('_block')]} 블록"
    elif prefix == "chemical":
        match = re.fullmatch(r"(clean|dirty)_(.+)", stem)
        if match:
            state, material = match.groups()
            adjective = "순수한" if state == "clean" else "불순물이 섞인"
            return f"{adjective} {MATERIALS[material]} 슬러리"
    elif prefix == "fluid_type":
        match = re.fullmatch(r"molten_(.+)_type", stem)
        if match:
            return f"용융 {MATERIALS[match.group(1)]}"
    elif prefix == "item":
        match = re.fullmatch(r"molten_(.+)_bucket", stem)
        if match:
            return f"용융 {MATERIALS[match.group(1)]} 양동이"
        match = re.fullmatch(r"dirty_(.+)_dust", stem)
        if match:
            return f"불순물이 섞인 {MATERIALS[match.group(1)]} 가루"
        if stem.startswith("raw_"):
            return f"{MATERIALS[stem.removeprefix('raw_')]} 원석"
        if stem in MATERIALS:
            return MATERIALS[stem]
        for form, form_name in ITEM_FORMS.items():
            suffix = f"_{form}"
            if stem.endswith(suffix):
                material = stem.removesuffix(suffix)
                return f"{MATERIALS[material]} {form_name}"
    raise ValueError(f"검수되지 않은 All The Ores 키: {key}={source}")


def normalize_alltheores() -> dict[str, int]:
    """All The Ores 516개 키를 전체 재생성한다."""
    root = WORK_ROOT / "alltheores"
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    changed = 0
    for key, source in english.items():
        if not isinstance(source, str):
            raise TypeError(f"문자열이 아닌 언어 값: {key}")
        translated = translate_alltheores(key, source)
        if korean[key] != translated:
            korean[key] = translated
            changed += 1
    dump_json(root / "ko_kr.json", korean)
    return {"keys": len(english), "changed": changed}


def normalize_allthecompressed() -> dict[str, int]:
    """압축 블록 이름을 199개 기본 재료 단위로 검수해 전 단계에 반영한다."""
    root = WORK_ROOT / "allthecompressed"
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    base_names: dict[str, str] = {}
    for key, source in english.items():
        match = re.fullmatch(r"block\.allthecompressed\.(.+)_1x", key)
        if not match:
            continue
        if not isinstance(source, str) or not source.endswith(" 1x"):
            raise ValueError(f"압축 1단계 원문 형식 불일치: {key}")
        stem = match.group(1)
        candidate = korean[key]
        if not isinstance(candidate, str) or not candidate.endswith(" 1x"):
            raise ValueError(f"압축 1단계 후보 형식 불일치: {key}")
        base_names[stem] = COMPRESSED_OVERRIDES.get(stem, candidate.removesuffix(" 1x"))

    changed = 0
    compressed_keys = 0
    for key, source in english.items():
        match = re.fullmatch(r"block\.allthecompressed\.(.+)_([1-9])x", key)
        if match:
            stem, level = match.groups()
            if stem not in base_names:
                raise ValueError(f"압축 기본 이름 누락: {key}")
            if not isinstance(source, str) or not source.endswith(f" {level}x"):
                raise ValueError(f"압축 원문 단계 형식 불일치: {key}")
            translated = f"{base_names[stem]} {level}x"
            compressed_keys += 1
        elif key.startswith("block.allthecompressed."):
            stem = key.removeprefix("block.allthecompressed.")
            if stem not in base_names:
                raise ValueError(f"압축 기본 이름 누락: {key}")
            translated = base_names[stem]
        elif key == "itemGroup.allthecompressed":
            translated = "AllTheCompressed"
        elif key == "tooltip.allthecompressed.quantity":
            translated = "총 블록 수: %s"
        else:
            raise ValueError(f"검수되지 않은 All The Compressed 키: {key}")
        if korean[key] != translated:
            korean[key] = translated
            changed += 1
    dump_json(root / "ko_kr.json", korean)
    return {
        "keys": len(english),
        "base_materials": len(base_names),
        "compressed_keys": compressed_keys,
        "manual_or_corrected_bases": len(COMPRESSED_OVERRIDES),
        "changed": changed,
    }


def normalize_quests() -> dict[str, int]:
    """관련 퀘스트 66개 표시 키 중 검수 교정 대상을 반영한다."""
    root = WORK_ROOT / "quests/related"
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    unknown = sorted(set(QUEST_OVERRIDES) - set(english))
    if unknown:
        raise KeyError(f"원문에 없는 퀘스트 키: {unknown}")
    changed = 0
    for key, translated in QUEST_OVERRIDES.items():
        errors = validate_value(key, english[key], translated)
        if errors:
            raise ValueError("; ".join(errors))
        if korean[key] != translated:
            korean[key] = translated
            changed += 1
    dump_json(root / "ko_kr.json", korean)
    return {
        "keys": len(english),
        "reviewed_overrides": len(QUEST_OVERRIDES),
        "changed": changed,
    }


def verify_namespace(namespace: str) -> list[str]:
    """작업본의 키·자료형·자리표시자와 미번역을 검사한다."""
    root = WORK_ROOT / namespace
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    errors = []
    if list(english) != list(korean):
        return [f"키 또는 순서 불일치: {namespace}"]
    for key, source in english.items():
        target = korean[key]
        errors.extend(validate_value(key, source, target))
        if (
            isinstance(source, str)
            and isinstance(target, str)
            and source == target
            and key not in {"itemGroup.alltheores", "itemGroup.allthecompressed"}
            and not key.startswith("block.allthecompressed.kivi_")
        ):
            errors.append(f"미번역: {key}")
    return errors


def verify_quests() -> list[str]:
    """관련 퀘스트의 구조와 미번역 여부를 검사한다."""
    root = WORK_ROOT / "quests/related"
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    if list(english) != list(korean):
        return ["퀘스트 키 또는 순서 불일치"]
    errors = []
    for key, source in english.items():
        target = korean[key]
        errors.extend(validate_value(key, source, target))
        source_values = source if isinstance(source, list) else [source]
        target_values = target if isinstance(target, list) else [target]
        for index, (source_value, target_value) in enumerate(
            zip(source_values, target_values)
        ):
            if (
                isinstance(source_value, str)
                and source_value == target_value
                and re.search(r"[A-Za-z]{2,}", source_value)
                and not source_value.startswith(("{image:", "{@pagebreak}"))
                and re.sub(r"[§&][0-9A-FK-ORa-fk-or]", "", source_value).strip()
                not in {"Extreme Reactors", "Mekanism"}
            ):
                errors.append(f"미번역 퀘스트: {key}[{index}]")
    return errors


def iter_named_values(value: object, names: set[str]) -> list[str]:
    """중첩 JSON에서 지정한 표시 필드의 문자열 값을 모은다."""
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in names and isinstance(child, str):
                found.append(child)
            found.extend(iter_named_values(child, names))
    elif isinstance(value, list):
        for child in value:
            found.extend(iter_named_values(child, names))
    return found


def audit_data() -> tuple[dict[str, object], list[str]]:
    """JAR 데이터와 KubeJS의 사용자 표시 문구 경로를 검사한다."""
    instance = resolve_source_root()
    inventory = load_json(WORK_ROOT / "inventory.json")
    jar_rows = []
    errors = []
    for installed in inventory["installed"]:
        jar_name = installed["jar"]
        namespace = installed["namespace"]
        jar_path = instance / "mods" / jar_name
        advancements = 0
        advancement_displays = []
        recipes = 0
        recipe_visible_fields = []
        with ZipFile(jar_path) as archive:
            for name in archive.namelist():
                if not name.endswith(".json"):
                    continue
                if f"data/{namespace}/advancement/" in name:
                    advancements += 1
                    data = json.loads(archive.read(name).decode("utf-8"))
                    if isinstance(data, dict) and "display" in data:
                        advancement_displays.append(name)
                elif f"data/{namespace}/recipe/" in name:
                    recipes += 1
                    data = json.loads(archive.read(name).decode("utf-8"))
                    visible = iter_named_values(
                        data, {"name", "title", "description", "text"}
                    )
                    if visible:
                        recipe_visible_fields.append(
                            {"path": name, "values": visible[:5]}
                        )
        if advancement_displays:
            errors.append(f"표시 정보가 있는 발전 과제 발견: {namespace}")
        if recipe_visible_fields:
            errors.append(f"표시 문구가 있는 조합법 발견: {namespace}")
        jar_rows.append(
            {
                "namespace": namespace,
                "jar": jar_name,
                "advancements_checked": advancements,
                "advancement_display_entries": len(advancement_displays),
                "recipes_checked": recipes,
                "recipe_visible_field_entries": len(recipe_visible_fields),
            }
        )

    kubejs_root = instance / "kubejs"
    reference_files = []
    direct_visible_lines = []
    for path in kubejs_root.rglob("*.js"):
        text = path.read_text(encoding="utf-8")
        if not re.search(r"allthe(?:ores|compressed)", text, re.IGNORECASE):
            continue
        relative = path.relative_to(kubejs_root).as_posix()
        reference_files.append(relative)
        for line_number, line in enumerate(text.splitlines(), 1):
            if re.search(
                r"allthe(?:ores|compressed)", line, re.IGNORECASE
            ) and re.search(
                r"displayName|tooltip|custom_name|Text\.(?:of|literal)|\.title\(|\.description\(",
                line,
                re.IGNORECASE,
            ):
                direct_visible_lines.append(f"{relative}:{line_number}")
    if direct_visible_lines:
        errors.append("KubeJS 직접 참조 줄에 사용자 표시 문구가 발견됨")
    report = {
        "jars": jar_rows,
        "kubejs_reference_files_checked": len(reference_files),
        "kubejs_direct_visible_lines": direct_visible_lines,
        "manually_reviewed_output_reference_files": [
            "startup_scripts/CustomAdditions.js",
            "server_scripts/modpack/runic_multis/recipes/star_altar.js",
        ],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    dump_json(WORK_ROOT / "data_audit.json", report)
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("normalize", "verify"))
    args = parser.parse_args()
    if args.command == "normalize":
        report = {
            "alltheores": normalize_alltheores(),
            "allthecompressed": normalize_allthecompressed(),
            "quests": normalize_quests(),
        }
    else:
        data_report, data_errors = audit_data()
        errors = (
            verify_namespace("alltheores")
            + verify_namespace("allthecompressed")
            + verify_quests()
            + data_errors
        )
        report = {
            "alltheores_keys": len(load_json(WORK_ROOT / "alltheores/en_us.json")),
            "allthecompressed_keys": len(
                load_json(WORK_ROOT / "allthecompressed/en_us.json")
            ),
            "quest_keys": len(load_json(WORK_ROOT / "quests/related/en_us.json")),
            "data_audit": data_report,
            "errors": errors,
            "status": "complete" if not errors else "incomplete",
        }
        dump_json(WORK_ROOT / "specialized_validation.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
