#!/usr/bin/env python3
"""Allthemodium·ATM 장비 직접 관련 FTB Quests 표시 문구를 완성한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import audit_ftbquests_titles as audit
import build_ae2_quests as snbt
from local_paths import PROJECT_ROOT, resolve_source_root

WORK_ROOT = PROJECT_ROOT / "working/atmgear"
OUTPUT_FILE = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
ENGLISH_FILE = WORK_ROOT / "quest_english.json"
OVERRIDES_FILE = WORK_ROOT / "quest_overrides.json"
REPORT_FILE = WORK_ROOT / "quest_progress.json"
DEDICATED_CHAPTER = "allthemodium"
CHAPTER_TITLE_KEY = "chapter.4293754F9B2D05F0.title"
GROUP_TITLE_KEY = "chapter_group.2084F3F6FB861C5B.title"
RELATED_QUEST_IDS = {
    "03E05018D64DDEE1",
    "09733948CBCB3FB9",
    "2296CE4418AE62D4",
    "23AE395433AED3C0",
    "24FDA15A7ACDF021",
    "268F6E67AA79A7BD",
    "27CF1A2587321A2C",
    "3512F47DADC07EAE",
    "3DCD38634176BD92",
    "445C21949ADA1FE3",
    "47AED7219704EB3E",
    "4C8C56F960D92E9D",
    "4DD66E31859EA593",
    "501A0AEEC73C0790",
    "52AFABA08674B6A8",
    "5A9C646718EE92C2",
    "5BA84F6282D9CAF1",
    "5E7CCDE9229A646A",
    "62DDE5B1287BEB36",
    "66E88F916B638B3B",
    "6C5F9D0D447EFB9C",
    "6F76DA3BBAE8337B",
    "7154D73516548149",
    "7279700A93E8630B",
    "72DDA413D73E3235",
    "744AC6BD82FC2DEE",
}
INTERNAL_KEYS = {
    "task.5F45BABFD89DE0EC.title",
    "task.7A588081117FA54F.title",
}
TERM_REPLACEMENTS = (
    ("언옵테이니움", "Unobtainium"),
    ("언옵테이니움", "Unobtainium"),
    ("언옵테늄", "Unobtainium"),
    ("올더모듐", "Allthemodium"),
    ("비브라늄", "Vibranium"),
    ("바이브라늄", "Vibranium"),
    ("더 비욘드", "The Beyond"),
    ("아르스 누보", "Ars Nouveau"),
    ("철의 마법", "Iron's Spells"),
    ("인더스트리얼 포어고잉", "Industrial Foregoing"),
    ("포비든 앤 아케이너스", "Forbidden & Arcanus"),
    ("엔더IO", "Ender IO"),
)
LITERAL_REPLACEMENTS = {
    "INDUSTRIAL FOREGOING QUESTLINE": "Industrial Foregoing 퀘스트라인",
    "ARS NOUVEAU QUESTLINE": "Ars Nouveau 퀘스트",
    "POWAH QUESTLINE": "Powah 퀘스트라인",
}
RELATED_ITEM_LANGUAGES = {
    "powah": {"block.powah.energizing_orb": "에너지 주입 오브"},
    "forbidden_arcanus": {
        "item.forbidden_arcanus.eternal_stella": "이터널 스텔라",
        "block.forbidden_arcanus.hephaestus_forge": "헤파이스토스 대장간",
    },
}


def paragraph(text: str) -> list[str]:
    """FTB Quests 설명 문단을 만든다."""
    return [text]


FIRST_TEXT_OVERRIDES = {
    "quest.07FDA46D83F8360D.quest_desc": (
        "&6Allthemodium 조각&r 4개와 엔더 진주 하나로 텔레포트 패드를 만들 수 있습니다."
        "\n\nMinecraft 차원 중 한 곳에 설치하면 다른 차원으로 이동합니다. \n\n양손을 "
        "모두 비우고 웅크린 채 우클릭해야 합니다! 중요한 내용이니 "
        "꼭 읽어 주세요! \n\n양손이 모두 비어 있어야 합니다!"
    ),
    "quest.111E4ACF7D570EE8.quest_desc": (
        "&2&l바닐라 Minecraft&r에서 가장 어려운 구조물이니, 당연히 &6Allthemodium&r을 "
        "찾으려면 이곳으로 와야 합니다!\n\n고대 도시 주변 동굴 벽에서 광석을 찾을 수 "
        "있습니다. 빛나서 눈에 잘 띄지만 매우 희귀합니다!\n\n&5딥 다크 생물 군계&r라면 "
        "어디서든 찾을 수 있습니다."
    ),
    "quest.0CC0632E8276C787.quest_desc": (
        "&l&c네더&r에 텔레포트 패드를 설치하면 &b&l디 아더&r로 이동합니다."
    ),
    "quest.144BB025516E0994.quest_desc": (
        "&3Vibranium&r은 &6Allthemodium&r 다음 광물이므로 &6Allthemodium 곡괭이&r나 "
        "같은 채굴 등급의 도구가 있어야 캘 수 있습니다.\n\n&c&l네더&r에서는 희귀하게, "
        "&b&l디 아더&r에서는 풍부하게 발견됩니다.\n\n더 많이 얻으려면 광석 가공을 권합니다."
        "\n\n멋진 색상의 ATM 광석이지만 아쉽게도 아이템 활용처는 가장 적습니다."
    ),
    "quest.15DC6770B112EE69.quest_desc": (
        "용해 챔버는 &l&7Industrial Foregoing&r이 추가하는 기계로, &3Vibranium&r과 "
        "&5Unobtainium&r을 결합할 때도 사용합니다. \n\n같은 모드의 몹 도살 공장에서 "
        "얻는 &d분홍색 슬라임&r이 필요합니다. \n\n&b&l디 아더&r의 피글린 마을에서 "
        "흔히 발견되는 영혼 용암도 필요합니다. \n\n주괴와 피글리치 심장을 정확한 순서로 "
        "넣고 전력을 공급하면 완성됩니다!\n"
    ),
    "quest.15FEA03A2CDBA33B.quest_desc": (
        "&b&l디 아더&r는 여러 해 동안 수없이 바뀌었지만 언제나 모험을 위한 차원이었습니다! "
        "\n\n새로운 생물 군계와 블록, 구조물이 수십 개나 있습니다. \n\n피글린 마을, "
        "고대 피라미드, 던전뿐 아니라 When Dungeons Arise와 &b&lIce &fand &cFire&r의 "
        "구조물도 있습니다. 각 구조물만의 특별한 전리품을 포함해 훌륭한 보상이 가득합니다! "
        "\n\n&3Vibranium&r과 다른 광석을 캐거나 구조물에서 더 좋은 물건을 찾을 수도 있습니다! "
        "\n\n다만 &b&l디 아더&r에서는 채석장으로 캘 수 없는 블록이 많습니다. 여기서는 쉽게 "
        "넘어갈 수 없어요."
    ),
    "quest.162D2286A69D6E07.quest_desc": (
        "일반 &6Allthemodium 방어구&r와 능력치는 비슷하지만, Ars Nouveau 주문을 위한 "
        "마나 증가, 마나 재생, 주문 위력 효과가 붙습니다!"
    ),
    "quest.18FAD56CDE05646A.quest_desc": (
        "예전에는 &7&l채굴 차원&r의 채석기가 모든 것을 캐면서 &6Allthemodium 광석&r만 "
        "남겼습니다. \n\n이제는 &6Allthemodium&r도 캐지만 드롭은 소멸시킵니다... 채석기를 "
        "사용할 때 조심하세요! \n\n&6Allthemodium&r만 찾는다면 광석 감지 물약을 마시고 "
        "직접 채굴하는 것을 권합니다!"
    ),
    "quest.19E356E67EF17E4A.quest_desc": (
        "역사상 가장 훌륭한 도구입니다! 스위스 군용 칼과 비슷하지만 더 좋죠! \n\n최고 "
        "채굴 등급으로 블록을 캐고, 나무를 손쉽게 베고, 길을 만들며, 공격력도 강합니다!"
    ),
    "quest.201EE3566D4D3123.quest_desc": (
        "&6Allthemodium&r을 채굴하려면 &c네더라이트&r 등급 이상의 곡괭이가 필요합니다! "
        "\n\n광석을 얻었다면 먼저 행운, Occultism, Mekanism으로 가공해 수량을 늘리는 것을 "
        "권합니다. 그다음에는 몇 가지 선택지가 있습니다. \n\n&6조각&r으로 텔레포트 패드 "
        "2개를 만들어 보세요! &7&l채굴 차원&r에서 &6Allthemodium&r을 더 찾거나 "
        "&b&l디 아더&r로 가서 모험할 수 있습니다. \n\n그 뒤에는 &3Vibranium&r을 캘 수 "
        "있도록 곡괭이를 업그레이드하세요. 나머지는 여러분의 선택입니다!"
    ),
    "quest.226B8B60AF864FEF.quest_desc": (
        "&6Allthemodium&r 장비를 &3Vibranium&r 장비로 업그레이드하려면 또 다른 대장장이 "
        "형판이 필요합니다. \n수상한 영혼 모래를 솔질하면 찾을 수 있습니다. \n\n수상한 "
        "영혼 모래는 &l&c네더&r의 보루 잔해에 있습니다.\n"
    ),
    "quest.272CF280BAE6870E.quest_desc": (
        "일반 &6Allthemodium 방어구&r와 능력치는 비슷하지만 Iron's Spells 주문의 위력이 "
        "더 강해집니다. \n\n최대 마나와 마나 재생 능력치도 붙습니다!"
    ),
    "quest.2C4299D33D419AA0.quest_desc": (
        "&2&l오버월드&r에 텔레포트 패드를 설치하면 &7&l채굴 차원&r으로 이동합니다."
    ),
    "quest.2EDE91023F7924FB.quest_desc": (
        "&d&l엔드&r에 텔레포트 패드를 설치하면 &5&lThe Beyond&r로 이동합니다."
    ),
    "quest.3F8D515D7B81B0E3.quest_desc": (
        "대장장이 형판이 또 있다고요?!?!?!\n\n그래도 이번에는 고고학으로 찾을 필요가 "
        "없습니다!\n\n&b&l디 아더&r의 던전 구조물에 있는 시험 생성기를 물리쳐야 합니다. "
        "정확히는 도서관 방에서 찾을 수 있어요!\n"
    ),
    "quest.4A079D40C0AF6BC3.quest_desc": (
        "아니요, &5&lThe Beyond&r에서는 찾을 수 없습니다. \n\n&5Unobtainium 광석&r은 "
        "엔드 고지대 생물 군계에서 매우 드물게 발견됩니다. 보통 엔드 도시도 이곳에 "
        "생성됩니다! \n\n광석을 캐려면 &3Vibranium 곡괭이&r나 같은 등급의 도구가 "
        "필요합니다. \n\n이제 광석 가공을 권해야 한다는 건 아시죠?"
    ),
    "quest.4B2146C9527C54E7.quest_desc": (
        "챕터 2에 도달했으니 &2&l바닐라 Minecraft&r를 클리어했겠군요! \n\n지금쯤 "
        "&c네더라이트&r도 얻고 &2&lMinecraft&r의 모든 보스를 처치했을 겁니다. 이제 "
        "무엇을 할까요? \n\n다음은 &6&lAllthemodium&r입니다! &6Allthemodium&r을 얻기 "
        "시작하려면 &c네더라이트&r가 필요하니 거기서 출발해 봅시다!"
    ),
    "quest.4E737C490DCC5D6C.quest_desc": (
        "&6&lAllthemodium&r에서 얻을 수 있는 최고의 방어구는 &5Unobtainium 방어구&r입니다! "
        "진짜 최상급 방어구를 만들 때도 &5Unobtainium 방어구&r가 필요합니다. \n\n방어력 "
        "40, 방어 강도 60, 밀치기 저항 "
        "100%를 제공하니 꼼짝도 하지 않겠네요! \n\n이전 방어구의 효과에 더해 &d마법 피해 "
        "저항&r도 90%로 높아집니다."
    ),
    "quest.5BA986D7928BF09F.quest_desc": (
        "피글리치는 &6&lAllthemodium&r이 추가하는 보스입니다. \n\n생명력이 1000하트이며 "
        "현재는 공격하지 않지만, 공격이 추가되면 아주 강력할 겁니다! \n\n처치하면 합금과 "
        "ATM의 별에 필요한 피글리치 심장을 떨어뜨립니다! \n\n(HNN이나 Ender IO 등으로 "
        "자동화하는 방법을 찾아보세요!)"
    ),
    "quest.6D738730B371B152.quest_desc": (
        "&l&7채굴 차원&r은 지표에 아무것도 없는 완전한 평지 세계입니다. \n\n지표 아래에는 "
        "거의 모든 광석이 있습니다. \n\n&7&l채굴 차원&r에는 동굴도, 몹 생성도, 방해물도 "
        "없고 여러 종류의 돌과 "
        "광석뿐입니다! \n\n광석은 &7&l채굴 차원&r의 Y 높이와 지층에 따라 다르게 생성됩니다. "
        "\n\n채석기를 설치하는 것을 권합니다."
    ),
    "quest.6E0624750DF8CD18.quest_desc": (
        "이제는 직접 제작할 수 없고 항상 &c네더라이트&r 장비를 업그레이드해야 합니다. "
        "\n네, 마법 부여를 유지하고 내구도도 수리해 줍니다!"
    ),
    "quest.6ECDD26CCCBC07C3.quest_desc": (
        "&c네더라이트 방어구&r에서 바로 업그레이드하므로 &5마법 부여&r가 유지됩니다. "
        "\n\n&6Allthemodium&r 풀세트는 방어력 24, 방어 강도 20, 밀치기 저항 50%를 "
        "제공합니다. \n\n그게 전부가 아닙니다! \n\n&6투구&r: &9수중 호흡&r, &3&l워든&r의 "
        "&0어둠 효과&r 면역, &7겉날개&r 충돌 피해 무효. \n&6흉갑&r: &d마법 피해 저항&r "
        "50%와 &c화염 저항&r. \n&6레깅스&r: &9물갈퀴&r와 &0시듦&r 면역. \n&6부츠&r: "
        "낙하 피해 저항, &b가루눈&r과 &c용암&r 위 보행."
    ),
    "quest.762581CAE5F5DDC1.quest_desc": (
        "멋진 마법 모드네요! &d&lArs Nouveau&r의 마법 부여 장치로 &5Unobtainium&r과 "
        "&6Allthemodium&r을 결합합니다! \n\n마법 부여 장치는 여러 조합에 쓰이는 "
        "멀티블록입니다. 아케인 코어 위에 마법 부여 장치를 놓고, 같은 Y 높이의 주변에 "
        "받침대를 배치하세요. \n\n받침대에 재료를 순서와 관계없이 올리고 주변에 마나를 "
        "준비한 뒤 장치에 마나 보석을 넣으면 제작이 시작됩니다. 그러면 "
        "&5Unobtainium&r-&6Allthemodium&r 합금 주괴가 완성됩니다!\n"
    ),
    "quest.766EEB89C6DF3575.quest_desc": (
        "이터널 스텔라는 대장장이 작업대에서 아이템과 결합해 파괴 불가로 만들거나 합금 도구를 "
        "제작할 때 사용합니다! \n\n먼저 재료가 충분한 3티어 헤파에스토스 대장간이 "
        "필요합니다. \n\n그다음 블랙홀에 아이템을 먹여 얻는 엑스페트리파이드 구슬 3개가 "
        "필요합니다. \n\n채굴해서 얻는 스텔라라이트 조각과 &6Allthemodium 주괴&r도 "
        "준비하세요!"
    ),
    "quest.7B3613C01F0B1373.quest_desc": (
        "&3Vibranium&r과 &6Allthemodium&r을 결합하려면 &l&cPowah&r의 에너지 주입 오브가 "
        "필요합니다! \n\n에너지 주입 오브를 놓고 에너지 주입 막대가 오브를 향하게 배치하세요. "
        "막대는 전력원 위에 놓아야 하며, 등급에 따라 저장하고 전송하는 에너지양이 달라집니다. "
        "\n\n주괴, 피글리치 심장 2개, 압축 니트로 수정 블록 X1을 오브에 넣으세요. 순서는 "
        "상관없습니다. 막대를 통해 1 Billion FE를 공급하면 완성됩니다!\n"
    ),
    "quest.7CC96CE9901F25BB.quest_desc": (
        "&l&5Forbidden & Arcanus&r는 헤파이스토스 대장간이라는 멀티블록을 중심으로 하는 "
        "마법 모드입니다.\n\n대장간 툴팁의 설명에 따라 건설하세요! 완성하면 의식에 필요한 "
        "아우레알, 영혼, 피, 경험치의 4가지 자원을 공급할 수 있습니다.\n\n의식을 통해 대장간도 "
        "업그레이드해야 합니다. 필요한 정보는 JEI에서 확인할 수 있습니다."
    ),
    "quest.7DE2154159D273C3.quest_desc": (
        "&3Vibranium 방어구&r는 &6Allthemodium 방어구&r의 업그레이드입니다. \n\n모든 "
        "능력치가 높아져 방어력 32, 방어 강도 36, 밀치기 저항 80%를 제공합니다. "
        "\n\n새로운 효과나 능력은 없지만 &d마법 피해 저항&r이 75%로 높아집니다!"
    ),
    "quest.27CF1A2587321A2C.quest_desc": (
        "상상할 수 있는 최고의 &e주문서&r입니다! &3주문&r 슬롯이 15개나 있습니다! "
        "&3주문&r이 15개나 있냐고요?!?! 잠깐, 15개면 그렇게 많지도 않네요... \n\n이전처럼 "
        "직전 단계 주문서, 주괴, 형판을 결합하세요."
    ),
    "quest.2296CE4418AE62D4.quest_desc": (
        "&6Allthemodium 방어구&r에 &d&lArs Nouveau&r 주문 강화 효과를 더한 장비입니다!"
    ),
    "quest.24FDA15A7ACDF021.quest_desc": (
        "&5Unobtainium 방어구&r에 &e&lIron's Spells&r 주문 강화 효과를 더한 장비입니다!"
    ),
    "quest.3512F47DADC07EAE.quest_desc": (
        "&5Unobtainium 방어구&r에 &d&lArs Nouveau&r 주문 강화 효과를 더한 장비입니다!"
    ),
    "quest.3DCD38634176BD92.quest_desc": (
        "대장장이 작업대에서 &6Allthemodium&r &e주문서&r를 Vibranium 주괴 및 형판과 "
        "결합하세요.\n\n이 형판은 보루 잔해의 수상한 영혼 모래를 솔질해서 얻을 수 "
        "있습니다."
    ),
    "quest.445C21949ADA1FE3.quest_desc": (
        "대장장이 작업대에서 고대의 서를 &6Allthemodium 주괴&r 및 형판과 결합하세요."
        "\n\n&9고대 도시&r의 수상한 점토를 솔질하면 형판을 얻을 수 있습니다."
    ),
    "quest.4DD66E31859EA593.quest_desc": (
        "&3Vibranium 방어구&r에 &e&lIron's Spells&r 주문 강화 효과를 더한 장비입니다!"
    ),
    "quest.501A0AEEC73C0790.quest_desc": (
        "&6피글리치&r는 &6&lAllthemodium&r이 추가한 보스로, &l&b디 아더&r의 고대 "
        "피라미드에 삽니다. \n\n처치하면 심장 1개를 떨어뜨립니다! 심장 블록 하나를 만들려면 "
        "9마리를 처치해야 합니다... \n\n다행히 자동화할 방법이 있습니다!"
    ),
    "quest.52AFABA08674B6A8.quest_desc": (
        "&3Vibranium 방어구&r에 &d&lArs Nouveau&r 주문 강화 효과를 더한 장비입니다!"
    ),
    "quest.5BA84F6282D9CAF1.quest_desc": (
        "&6Allthemodium 방어구&r에 &e&lIron's Spells&r 주문 강화 효과를 더한 장비입니다!"
    ),
    "quest.62DDE5B1287BEB36.quest_desc": (
        "&6&lATM의 별&r 내부를 구성하는 또 다른 부품은 &6각성한 "
        "&5Unobtainium&f-&3Vibranium&r 합금 블록입니다. 여기서는 간단히 &6각성한 "
        "합금&r 블록이라고 부르겠습니다. \n이것을 만들려면 &6&l별 제단&r 멀티블록이 "
        "필요합니다. 자세한 내용은 별 제작 퀘스트를 확인하세요! \n\n"
        "&5Unobtainium&f-&3Vibranium&r 합금 블록, 내구성 I 책 4권, &6각성한 "
        "수프레뮴 보석&r 4개, &6각성한 수프레뮴 정수&r 4개를 넣으세요. \n\n그다음 "
        "85 Million FE를 공급하면 합금이 각성합니다!"
    ),
    "quest.66E88F916B638B3B.quest_desc": (
        "조금 헷갈릴 수 있습니다. &5크리에이티브 &e마도서&r가 여러 개 있거든요! 여기서 "
        "필요한 것은 &d&lAll The Arcanist Gear&r의 마도서입니다. \n\n이 마도서를 만들려면 "
        "먼저 &l&dArs Nouveau&r의 크리에이티브 &e마도서&r를 제작해야 합니다. 그 조합에는 "
        "&e대마법사의 마도서&r, &6&lATM의 별&r, 몇 가지 추가 아이템이 필요합니다. \n\n"
        "&eUnobtainium 마도서&r와 성능은 같지만 마나가 무한하고 모든 문양이 해금되어 "
        "있습니다! \n\n모든 주문 위력을 손에 넣는 겁니다. 으하하하!"
    ),
    "quest.6C5F9D0D447EFB9C.quest_desc": (
        "&l&2바닐라&r 방어구가 전부라고 생각하셨나요? \n\n&6Allthemodium 방어구&r는 "
        "방어력과 방어 강도가 더 높고, 마법 피해 저항과 여러 강화 효과도 제공합니다. 자세한 "
        "내용은 &6&lAllthemodium&r 퀘스트 페이지에서 확인하세요! \n\n제작하려면 "
        "&c네더라이트&r가 필요합니다."
    ),
    "quest.6F76DA3BBAE8337B.quest_desc": (
        "&6&lAllthemodium&r 계열에서 얻을 수 있는 최고의 방어구, &5Unobtainium&r입니다! "
        "\n\n모든 능력치가 더 높고 밀치기 저항은 100%입니다! \n\n제작하려면 "
        "&3Vibranium 방어구&r가 필요합니다."
    ),
    "quest.72DDA413D73E3235.quest_desc": (
        "&6&lAllthemodium&r 방어구의 다음 단계인 &3Vibranium&r 방어구는 모든 능력치가 "
        "훨씬 높습니다! \n\n제작하려면 &6Allthemodium 방어구&r가 필요합니다."
    ),
    "quest.24934231538B6492.quest_desc": (
        "고대 피라미드는 &b&l디 아더&r에 있는 여러 구조물 중 하나입니다. \n\n말 그대로 "
        "피라미드이며, 이번에는 지하실이 없습니다! \n\n대신 피글리치가 기다립니다.\n"
    ),
    "quest.71E4FD61787DE299.quest_desc": (
        "고대 도시에서만 찾을 수 있는 또 다른 아이템은 &6Allthemodium 대장장이 형판&r입니다."
        "\n\n수상한 점토를 솔질해서 얻을 수 있습니다.\n\n수상한 점토는 고대 도시의 바닥에서 "
        "찾을 수 있습니다.\n"
    ),
}

VALUE_OVERRIDES: dict[str, snbt.TranslationValue] = {
    CHAPTER_TITLE_KEY: "&a2장&r: &eAllthemodium",
    GROUP_TITLE_KEY: "주요 퀘스트라인",
    "quest.0484051446480B54.title": "&6Allthemodium &5합금 &3도끼",
    "quest.089B1B9837AF4938.title": "&5Unobtainium 도구",
    "quest.08AC2D81A1004984.title": "&6Allthemodium &5합금 &3삼지창",
    "quest.0A9D5C5D2F4CDCC3.title": "&5Unobtainium 철퇴",
    "quest.11E957CDEFA0CAAB.title": "&5&lThe Beyond",
    "quest.144BB025516E0994.title": "&3Vibranium 주괴&r",
    "quest.151D836C7B0E6FAF.title": "&3Vibranium 방패",
    "quest.162D2286A69D6E07.title": "&6Allthemodium 비전술사 방어구",
    "quest.19E356E67EF17E4A.title": "&6Allthemodium &5합금 &3팩셀",
    "quest.1A05C605A52A4218.title": "&5Unobtainium&r-&6Allthemodium&r 합금 주괴",
    "quest.1F6C8117F3CED939.title": "&6Allthemodium 활",
    "quest.1FE47F03B5DF492D.title": "&5Unobtainium 비전술사 방어구",
    "quest.201EE3566D4D3123.title": "&6Allthemodium 주괴",
    "quest.226B8B60AF864FEF.title": "&3Vibranium 대장장이 형판&r",
    "quest.272CF280BAE6870E.title": "&6Allthemodium 마법사 방어구",
    "quest.2CF6EA138B53CE1B.title": "&5Unobtainium&r-&3Vibranium&r 합금 주괴",
    "quest.2D8026E10FBA7A72.title": "&6Allthemodium &5합금 &3곡괭이",
    "quest.39B6D9FD21419776.title": "&3Vibranium 마법사 방어구",
    "quest.3F8D515D7B81B0E3.title": "&5Unobtainium 대장장이 형판",
    "quest.44D5EDB8711EC7A0.title": "&6Allthemodium 철퇴",
    "quest.47F734CDD5793F26.title": "&5Unobtainium 쇠뇌",
    "quest.4A079D40C0AF6BC3.title": "&5Unobtainium 주괴&r",
    "quest.4B2146C9527C54E7.title": "&6&lAllthemodium",
    "quest.4E28B67554CBDAB7.title": "&6Allthemodium &5합금 &3칼날",
    "quest.4E737C490DCC5D6C.title": "&5Unobtainium 방어구",
    "quest.558FF21A6BCFE6E8.title": "&5Unobtainium 마법사 방어구",
    "quest.5A26738AC904DC39.title": "&6Allthemodium 주문서",
    "quest.5AAF6CA41209B365.title": "&3Vibranium 도구",
    "quest.5B46B5BF4ADB2BE9.title": "&6Allthemodium &5합금 &3삽",
    "quest.5FA68047A3C05E80.title": "&5Unobtainium 주문서",
    "quest.66039B738CF0718A.title": "&3Vibranium&r-&6Allthemodium&r 합금 주괴",
    "quest.68E6AE1B9EBCEFFF.title": "&3Vibranium 철퇴",
    "quest.6E0624750DF8CD18.title": "&6Allthemodium 도구",
    "quest.6ECDD26CCCBC07C3.title": "&6Allthemodium 방어구",
    "quest.71E4FD61787DE299.title": "&6Allthemodium 대장장이 형판",
    "quest.77AD61FCA9BC9AFB.title": "&3Vibranium 주문서",
    "quest.795A860668072830.title": "&3Vibranium 비전술사 방어구",
    "quest.7DE2154159D273C3.title": "&3Vibranium 방어구",
    "task.03ACF4486D706DEE.title": "Vibranium 방어구",
    "task.05256FE880D981D5.title": "Vibranium 도구",
    "task.0BFAF56214875C90.title": "Allthemodium 마법사 방어구",
    "task.0E7E336483AFA69C.title": "Vibranium 마법사 방어구",
    "task.194C02E800F974D6.title": "Vibranium 비전술사 방어구",
    "task.2A7CD3F14D3DC7C5.title": "Unobtainium 방어구",
    "task.2E3BC536B8A9FD91.title": "Unobtainium 마법사 방어구",
    "task.40C43560F454AD82.title": "Allthemodium 도구",
    "task.4709938E0FDCE0FB.title": "Allthemodium 방어구",
    "task.614C3310C61487CB.title": "Unobtainium 비전술사 방어구",
    "task.61E3800DF5D25567.title": "Allthemodium 비전술사 방어구",
    "task.6304FF8A9E8957FE.title": "Unobtainium 도구",
    "task.6514595CBD4DE6C6.title": "The Beyond 방문하기",
    "task.6AE0DA6AB109A840.title": "채석기 사용",
    "quest.2296CE4418AE62D4.title": "&6Allthemodium 비전술사 장비",
    "quest.23AE395433AED3C0.title": "&6&l별의&r 외장",
    "quest.24FDA15A7ACDF021.title": "&5Unobtainium 마법사 장비",
    "quest.27CF1A2587321A2C.title": "&5Unobtainium&r 주문서",
    "quest.3512F47DADC07EAE.title": "&5Unobtainium 비전술사 장비",
    "quest.3DCD38634176BD92.title": "&3Vibranium&r 주문서",
    "quest.445C21949ADA1FE3.title": "&6Allthemodium&r 주문서",
    "quest.4DD66E31859EA593.title": "&3Vibranium 마법사 장비",
    "quest.52AFABA08674B6A8.title": "&3Vibranium 비전술사 장비",
    "quest.5A9C646718EE92C2.title": "&3Vibranium&r",
    "quest.5BA84F6282D9CAF1.title": "&6Allthemodium 마법사 장비",
    "quest.5E7CCDE9229A646A.title": "&6Allthemodium&r",
    "quest.62DDE5B1287BEB36.title": (
        "&6각성한 &5Unobtainium&f-&3Vibranium&r 합금 블록"
    ),
    "quest.66E88F916B638B3B.title": "&5&l크리에이티브 &e마도서",
    "quest.6C5F9D0D447EFB9C.title": "&6Allthemodium 방어구",
    "quest.6F76DA3BBAE8337B.title": "&5Unobtainium 방어구",
    "quest.7154D73516548149.title": "&l&6Allthemodium",
    "quest.7279700A93E8630B.title": "&5Unobtainium&r",
    "quest.72DDA413D73E3235.title": "&3Vibranium 방어구",
    "quest.0484051446480B54.quest_desc": paragraph(
        "엄청난 피해를 주고 나무를 통째로 베어 쓰러뜨립니다! 더 바랄 게 있나요?"
    ),
    "quest.03E05018D64DDEE1.quest_desc": paragraph(
        "&e채굴 등급 5&r는 사실상 Allthemodium 광석을 위한 단계이며, 그 밖의 용도는 "
        "많지 않습니다."
    ),
    "quest.03E05018D64DDEE1.title": "&e채굴 등급 5",
    "quest.09733948CBCB3FB9.quest_desc": paragraph(
        "&d채굴 등급 6&r은 가장 높은 단계입니다. Vibranium과 Unobtainium을 포함해 "
        "파괴할 수 있는 모든 블록을 채굴할 수 있습니다."
    ),
    "quest.09733948CBCB3FB9.title": "&d채굴 등급 6",
    "quest.552F0B9B00F4F914.quest_desc": paragraph(
        "이 퀘스트는 &6AllTheMods 스태프&r 또는 &2커뮤니티 기여자&r가 AllTheMods "
        "모드팩에 사용하기 위해 작성했습니다. \\n\\n모든 &6AllTheMods&r 팩은 "
        "&eAll Rights Reserved&r 라이선스로 보호되므로, &6AllTheMods 팀&r의 명시적인 "
        "허가 없이 다른 공개 모드팩에 이 퀘스트를 사용할 수 없습니다. \\n\\n이 퀘스트는 "
        "의도적으로 숨겨져 있습니다. 이 문구가 보인다면 편집 모드입니다."
    ),
    "quest.5A26738AC904DC39.quest_desc": paragraph("주문 슬롯 13개!"),
    "quest.5FA68047A3C05E80.quest_desc": paragraph("주문 슬롯 15개!"),
    "quest.77AD61FCA9BC9AFB.quest_desc": paragraph("주문 슬롯 14개!"),
}


def normalize(value: snbt.TranslationValue) -> snbt.TranslationValue:
    """확정한 고유명사와 클릭 문구를 선택된 기존 번역에 적용한다."""
    if isinstance(value, list):
        return [normalize(item) for item in value]
    result = value
    for source, target in TERM_REPLACEMENTS:
        result = result.replace(source, target)
    for source, target in LITERAL_REPLACEMENTS.items():
        result = result.replace(source, target)
    return result


def validate_value(
    key: str, source: snbt.TranslationValue, target: snbt.TranslationValue
) -> list[str]:
    """색상 코드, 숫자, 자리표시자와 줄바꿈을 보존했는지 확인한다."""
    errors = snbt.validate_value(key, source, target)
    source_text = snbt.flatten(source)
    target_text = snbt.flatten(target)
    code_error = f"{key}: 색상/서식 코드 불일치"
    number_error = f"{key}: 숫자 불일치"
    if code_error in errors and Counter(re.findall(r"&.", source_text)) == Counter(
        re.findall(r"&.", target_text)
    ):
        errors.remove(code_error)
    if number_error in errors:
        number_re = re.compile(r"(?<![A-Za-z])\d+(?:[,.]\d+)*%?")
        source_numbers = number_re.findall(re.sub(r"&.", "", source_text))
        target_numbers = number_re.findall(re.sub(r"&.", "", target_text))
        if Counter(source_numbers) == Counter(target_numbers):
            errors.remove(number_error)
    return errors


def sha256(path: Path) -> str:
    """파일 SHA-256을 반환한다."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_task_ids(instance: Path) -> tuple[set[str], dict[str, int]]:
    """선택 퀘스트의 모든 Task ID와 챕터별 퀘스트 수를 수집한다."""
    chapters, _ = audit.parse_chapters(instance / "config/ftbquests/quests")
    task_ids: set[str] = set()
    chapter_counts: dict[str, int] = {}
    for chapter in chapters:
        selected = [
            quest for quest in chapter["quests"] if quest["id"] in RELATED_QUEST_IDS
        ]
        if selected:
            chapter_counts[chapter["filename"]] = len(selected)
        for quest in selected:
            task_ids.update(task["id"] for task in quest["tasks"])
    return task_ids, chapter_counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    lang_root = instance / "config/ftbquests/quests/lang"
    dedicated_en = snbt.parse_language_snbt(
        lang_root / f"en_us/chapters/{DEDICATED_CHAPTER}.snbt_merged"
    )
    dedicated_ko = snbt.parse_language_snbt(
        lang_root / f"ko_kr/chapters/{DEDICATED_CHAPTER}.snbt_merged"
    )
    full_en = snbt.parse_language_snbt(lang_root / "en_us.snbt")
    full_ko = snbt.parse_language_snbt(lang_root / "ko_kr.snbt")
    task_ids, chapter_counts = collect_task_ids(instance)
    english = dict(dedicated_en)
    installed = dict(dedicated_ko)
    for key in (CHAPTER_TITLE_KEY, GROUP_TITLE_KEY):
        english[key] = full_en[key]
        installed[key] = full_ko[key]
    selected_ids = RELATED_QUEST_IDS | task_ids
    for key, value in full_en.items():
        parts = key.split(".")
        if (
            len(parts) >= 3
            and parts[0] in {"quest", "task"}
            and parts[1] in selected_ids
        ):
            english[key] = value
            if key in full_ko:
                installed[key] = full_ko[key]

    draft = {
        key: normalize(installed.get(key, source)) for key, source in english.items()
    }
    for key, text in FIRST_TEXT_OVERRIDES.items():
        if key not in english or not isinstance(english[key], list):
            raise KeyError(f"설명 원문 키가 없습니다: {key}")
        draft[key] = [text.replace("\n", "\\n"), *normalize(english[key][1:])]
    unknown = sorted(set(VALUE_OVERRIDES) - set(english))
    if unknown:
        raise KeyError(f"영어 원문에 없는 번역 키: {unknown}")
    draft.update(VALUE_OVERRIDES)

    errors: list[str] = []
    intentional_original = 0
    for key, source in english.items():
        errors.extend(validate_value(key, source, draft[key]))
        if draft[key] == source:
            flat = snbt.flatten(source)
            if key in INTERNAL_KEYS or not re.search(r"[A-Za-z]{3,}", flat):
                intentional_original += 1
            elif all(
                part.startswith("{image:")
                for part in source
                if isinstance(source, list)
            ):
                intentional_original += 1
            else:
                errors.append(f"분류되지 않은 영어 원문 유지: {key}")
    if errors:
        raise RuntimeError("FTB Quests 번역 검증 실패:\n" + "\n".join(errors[:100]))

    base = OUTPUT_FILE if OUTPUT_FILE.is_file() else lang_root / "ko_kr.snbt"
    base_hash = sha256(base)
    output = snbt.merge_into_full_snbt(base, draft)
    OUTPUT_FILE.write_text(output, encoding="utf-8")
    reparsed = snbt.parse_language_snbt(OUTPUT_FILE)
    for key, value in draft.items():
        if reparsed.get(key) != value:
            raise RuntimeError(f"누적 SNBT 병합값 불일치: {key}")

    related_language_files: list[str] = []
    for namespace, values in RELATED_ITEM_LANGUAGES.items():
        path = (
            PROJECT_ROOT
            / f"output/resourcepack/ATM10_Korean/assets/{namespace}/lang/ko_kr.json"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = (
            json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        )
        if not isinstance(existing, dict):
            raise TypeError(f"관련 언어 파일 최상위 값이 객체가 아닙니다: {path}")
        existing.update(values)
        path.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        related_language_files.append(path.relative_to(PROJECT_ROOT).as_posix())

    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    ENGLISH_FILE.write_text(
        json.dumps(english, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    OVERRIDES_FILE.write_text(
        json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    kept = sum(key in installed and installed[key] == draft[key] for key in english)
    corrected = sum(
        key in installed and installed[key] != draft[key] for key in english
    )
    new = sum(key not in installed for key in english)
    report = {
        "scope": "Allthemodium and ATM gear related FTB Quests",
        "dedicated_chapter": DEDICATED_CHAPTER,
        "dedicated_quests": 54,
        "related_chapters": chapter_counts,
        "source_display_keys": len(english),
        "existing_korean_kept": kept,
        "existing_korean_corrected": corrected,
        "newly_completed": new,
        "literal_components_translated": len(LITERAL_REPLACEMENTS),
        "custom_names": 0,
        "related_item_hover_keys_added": sum(
            len(values) for values in RELATED_ITEM_LANGUAGES.values()
        ),
        "related_item_language_files": related_language_files,
        "classification": {
            "translated_or_localized": len(english) - intentional_original,
            "intentional_original_or_internal": intentional_original,
            "out_of_scope": 0,
            "manual_review": 0,
        },
        "remaining": 0,
        "base_sha256": base_hash,
        "output_sha256": sha256(OUTPUT_FILE),
        "status": "passed",
    }
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
