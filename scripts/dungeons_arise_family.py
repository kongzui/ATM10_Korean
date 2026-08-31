#!/usr/bin/env python3
"""When Dungeons Arise의 현재 표시 문구를 추출·번역·검증해요."""

from __future__ import annotations

import argparse
import gzip
import io
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

from gateways_hellish_family import Tag
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import (
    active_output_root,
    output_deployment_path,
    resolve_active_output_path,
)

FAMILY = "dungeons_arise"
JAR_PATTERN = "DungeonsArise-*.jar"
NAMESPACE = "dungeons_arise"
EXPECTED_LANGUAGE_KEYS = 119
WORK_ROOT = PROJECT_ROOT / "working/dungeons_arise"
LANG_OUTPUT = (
    active_output_root()
    / "resourcepack/ATM10_Korean/assets/dungeons_arise/lang/ko_kr.json"
)
OVERRIDE_ROOT = active_output_root() / "overrides/kubejs"
VISIBLE_DATA_KEYS = {
    "custom_name",
    "description",
    "item_name",
    "literal_text",
    "minecraft:custom_name",
    "minecraft:item_name",
    "text",
    "title",
}
VISIBLE_NBT_STRING_NAMES = {
    "CustomName",
    "LastOutput",
    "Text1",
    "Text2",
    "Text3",
    "Text4",
    "author",
    "minecraft:custom_name",
    "minecraft:item_name",
    "raw",
    "title",
}
VISIBLE_NBT_LIST_NAMES = {"messages", "minecraft:lore"}
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-Za-z]")
NUMBER = re.compile(r"(?<![A-Za-z§&])\d+(?:\.\d+)?")
FOREIGN_SCRIPT = re.compile(r"[\u0600-\u06ff\u3040-\u30ff\u4e00-\u9fff]")

LANG_TEXT = {
    "Monastery Explorer Map": "수도원 탐험 지도",
    "Illager Campsite Explorer Map": "약탈자 야영지 탐험 지도",
    "Illager Castle Explorer Map": "약탈자 성 탐험 지도",
    "Illager Hall Explorer Map": "약탈자 회관 탐험 지도",
    "Illager Fort Explorer Map": "약탈자 요새 탐험 지도",
    "Abandoned Temple Explorer Map": "버려진 사원 탐험 지도",
    "Lighthouse Explorer Map": "등대 탐험 지도",
    "Mushroom Mines Explorer Map": "버섯 광산 탐험 지도",
    "Mushroom Village Explorer Map": "버섯 마을 탐험 지도",
    "Coliseum Explorer Map": "콜로세움 탐험 지도",
    "Fishing Hut Explorer Map": "낚시 오두막 탐험 지도",
    "Small Prairie House Explorer Map": "작은 초원 주택 탐험 지도",
    "Wishing Well Explorer Map": "소원의 우물 탐험 지도",
    "Merchant Campsite Explorer Map": "상인 야영지 탐험 지도",
    "Infested Temple Explorer Map": "감염된 사원 탐험 지도",
    "Heavenly Rider Explorer Map": "천상의 기수 탐험 지도",
    "Mining System Explorer Map": "채굴 시설 탐험 지도",
    "Heavenly Conqueror Explorer Map": "천상의 정복자 탐험 지도",
    "Scorched Mines Map": "불타버린 광산 지도",
    "Undead Pirate Ship Explorer Map": "언데드 해적선 탐험 지도",
    "Foundry Explorer Map": "주조소 탐험 지도",
    "Small Blimp Explorer Map": "소형 비행선 탐험 지도",
    "Bandit Village Explorer Map": "도적 마을 탐험 지도",
    "Typhon Explorer Map": "티폰 탐험 지도",
    "Ceryneian Hind Explorer Map": "케리네이아의 암사슴 탐험 지도",
    "Heavenly Challenger Explorer Map": "천상의 도전자 탐험 지도",
    "Illager Corsair Explorer Map": "약탈자 사략선 탐험 지도",
    "Illager Galley Explorer Map": "약탈자 갤리선 탐험 지도",
    "Mushroom House Explorer Map": "버섯 집 탐험 지도",
    "When Dungeons Arise": "When Dungeons Arise",
    "Dungeons arise on a brave new world": "용감한 신세계에 던전이 솟아오릅니다",
    "Lost for Words": "할 말을 잃다",
    "Find an Abandoned Temple": "버려진 사원을 찾으세요",
    "Three Little Birds": "작은 새 세 마리",
    "Find an Aviary": "새장을 찾으세요",
    "What Happens in Las Vegas...": "라스베이거스에서 일어난 일은...",
    "Find the Bandit Towers": "도적 탑을 찾으세요",
    "Rusted Root": "녹슨 뿌리",
    "Find a Bandit Village": "도적 마을을 찾으세요",
    "Who Killed This Thing?": "이걸 누가 죽였지?",
    "Find a Ceryneian Hind": "케리네이아의 암사슴을 찾으세요",
    "Remember Me For Centuries": "수백 년 동안 나를 기억하라",
    "Find a Coliseum": "콜로세움을 찾으세요",
    "Fishing In The Dark": "어둠 속 낚시",
    "Find a Fishing Hut": "낚시 오두막을 찾으세요",
    "Iron Maiden": "아이언 메이든",
    "Find a Foundry": "주조소를 찾으세요",
    "A Saucerful of Secrets": "비밀이 가득한 접시",
    "Find a Giant Mushroom": "거대 버섯을 찾으세요",
    "The Imperial March": "제국의 행진",
    "Find a Heavenly Challenger": "천상의 도전자를 찾으세요",
    "Ghost Riders In The Sky": "하늘의 유령 기수",
    "Find a Heavenly Conqueror": "천상의 정복자를 찾으세요",
    "Ride Of The Valkyries": "발키리의 기행",
    "Find a Heavenly Rider": "천상의 기수를 찾으세요",
    "People Are Strange": "사람들은 이상해",
    "Find an Illager Campsite": "약탈자 야영지를 찾으세요",
    "You Are A Pirate": "너는 해적",
    "Find an Illager Corsair or an Illager Galley": (
        "약탈자 사략선 또는 약탈자 갤리선을 찾으세요"
    ),
    "Wild Tales": "거친 이야기",
    "Find an Illager Fort": "약탈자 요새를 찾으세요",
    "All Along The Watchtower": "망루를 따라서",
    "Find an Illager Windmill": "약탈자 풍차를 찾으세요",
    "Scary Monsters And Super Creeps": "무서운 괴물과 지독한 악당",
    "Find an Infested Temple": "감염된 사원을 찾으세요",
    "On The Road": "길 위에서",
    "Discover an Infested Temple explorer map": "감염된 사원 탐험 지도를 발견하세요",
    "The Lighthouse": "등대",
    "Arrive at a Lighthouse": "등대에 도착하세요",
    "Let's Groove": "신나게 춤춰요",
    "Find a Merchant Campsite": "상인 야영지를 찾으세요",
    "Stone Free": "돌에서 해방",
    "Find a Mining System": "채굴 시설을 찾으세요",
    "A Quiet Place": "조용한 곳",
    "Find a Monastery": "수도원을 찾으세요",
    "Over The Garden Wall": "정원 담장 너머",
    "Find a Mushroom House": "버섯 집을 찾으세요",
    "We All Lift Together": "우리 모두 함께 든다",
    "Find a Mushroom Mine": "버섯 광산을 찾으세요",
    "Sweet Dreams": "달콤한 꿈",
    "Find a Mushroom Village": "버섯 마을을 찾으세요",
    "Renai Circulation": "연애 서큘레이션",
    "Find a Plague Asylum": "역병 수용소를 찾으세요",
    "Katabasis": "카타바시스",
    "Find the Scorched Mines": "불타버린 광산을 찾으세요",
    "Enter Sandman": "샌드맨 등장",
    "Find the Shiraz Palace": "시라즈 궁전을 찾으세요",
    "Sky High": "하늘 높이",
    "Find a Small Blimp": "소형 비행선을 찾으세요",
    "Guns and Roses": "총과 장미",
    "Visit the Thornborn Towers": "쏜본 탑을 방문하세요",
    "Jaws": "죠스",
    "Find a Typhon": "티폰을 찾으세요",
    "Smoke On The Water": "물 위의 연기",
    "Find an Undead Pirate Ship": "언데드 해적선을 찾으세요",
    "Jump": "점프",
    "Find a Wishing Well": "소원의 우물을 찾으세요",
    "Distant Dreamer": "먼 곳을 꿈꾸는 자",
    "Find Keep Kayra": "케이라 성채를 찾으세요",
    "Sgt. Peppers Lonely Hearts Club": "페퍼 상사의 외로운 마음 클럽",
    "Find a Greenwood Pub": "그린우드 선술집을 찾으세요",
    "Curses": "저주",
    "Find a Bathhouse": "목욕탕을 찾으세요",
    "Welcome To The Machine": "기계에 오신 것을 환영합니다",
    "Find a Mechanical Nest": "기계 둥지를 찾으세요",
    "Sympathy For The Devil": "악마를 위한 연민",
    "Find the Kisegi Sanctuary": "키세기 성소를 찾으세요",
    "Feed The Machine": "기계에게 먹이를",
    "Find the Mining Complex": "채굴 단지를 찾으세요",
    "Purification": "정화",
    "Confers a chance to negate all incoming poisonous and withering effects, releasing a burst of energy that damages nearby enemies.": (
        "받는 중독과 시듦 효과를 무효화하고, 주변 적에게 피해를 주는 에너지를 방출할 확률이 생깁니다."
    ),
    "Voltaic Shot": "전격 사격",
    "Charges arrows with electrical energy, which allows them to fly in a straight line and deliver an explosion.": (
        "화살에 전기 에너지를 충전하여 직선으로 날아가 폭발을 일으키게 합니다."
    ),
    "Discharge": "방전",
    "Attacking enemies builds up speed, however, high levels of speed are discharged in a violent explosion, damaging both victim and attacker.": (
        "적을 공격하면 속도가 쌓이지만, 속도가 너무 높아지면 거센 폭발로 방출되어 대상과 공격자 모두에게 피해를 줍니다."
    ),
    "Curse of Lolth": "롤스의 저주",
    "Bestows a chance to regenerate health when attacking enemies, however, spiders may sprout from their body. Damaging an arthropod will reflect damage to the wielder.": (
        "적을 공격할 때 체력을 회복할 확률이 생기지만 몸에서 거미가 솟아날 수 있습니다. 절지동물에게 피해를 주면 사용자에게 피해가 반사됩니다."
    ),
    "Ensnaring": "속박",
    "Confers a chance to inflict greater slowness when damaging enemies, and summons fangs that attack all monsters around them.": (
        "적에게 피해를 줄 때 더 강한 둔화를 부여할 확률이 생기고, 주변의 모든 몬스터를 공격하는 송곳니를 소환합니다."
    ),
}

DATA_TEXT = {
    "Tequila": "데킬라",
    "Absinthe": "압생트",
    "Vodka": "보드카",
    "Gin": "진",
    "Fernet": "페르네트",
    "Cider": "사과주",
    "A powerful brew distilled from withered flesh.": "시든 살점에서 증류한 강력한 술입니다.",
    "Distilled from tears of unborn children.": "태어나지 못한 아이들의 눈물로 증류했습니다.",
    "Best served cold.": "차갑게 마실 때 가장 좋습니다.",
    "Common beer with a touch of opioids.": "아편 성분을 살짝 넣은 흔한 맥주입니다.",
    "Keeps villagers at bay.": "주민이 가까이 오지 못하게 합니다.",
    "istilled from boiled frog legs and enhanced by the occult.": (
        "삶은 개구리 다리에서 증류하고 주술로 강화했습니다."
    ),
    "Nobody shall build a fortress higher than a man's step.": (
        "누구도 사람의 한 걸음보다 높은 요새를 지어서는 안 됩니다."
    ),
    "Particles of this brew seem to attract": "이 술의 입자는 주변 물체를 끌어당겨",
    "and asimilate nearby objects.": "흡수하는 듯합니다.",
    "Its name is purely metaphorical.": "이 이름은 순전히 비유적인 표현입니다.",
    "Some people describe its effects": "어떤 이들은 이 술의 효과가",
    "as incredibly light and liberating.": "놀랄 만큼 가볍고 자유롭다고 말합니다.",
    "But captives always spill out the": "하지만 포로는 취기가 충분히 오르면",
    "truth when they're high enough.": "언제나 진실을 털어놓습니다.",
    "True beer. Really, just beer.": "진짜 맥주입니다. 정말로 그냥 맥주예요.",
    "Beer beer beer beer.": "맥주 맥주 맥주 맥주.",
    "Distilled from magma cubes and freshly": "마그마 큐브와 갓 수확한",
    "harvested froglights.": "개구리불로 증류했습니다.",
    "Increases resistance during hot situations.": "뜨거운 상황에서 저항력을 높여 줍니다.",
    "Subjects can feel the thrill of business": "피실험자는 혈관을 타고 흐르는",
    "running through their veins.": "사업의 짜릿함을 느낄 수 있습니다.",
    "Proyective techniques reveal": "투영 기법으로 일시적인",
    "temporary psychopatic tendencies.": "사이코패스 성향이 드러납니다.",
    "Casts an aura of malice, and possibly bad breath.": (
        "악의의 기운과 아마도 입 냄새까지 내뿜습니다."
    ),
    "Microscopic sponge particles": "미세한 스펀지 입자가",
    "that breathe on their own.": "스스로 숨을 쉽니다.",
    "Despite all reports of whispers and": "속삭임과 침입적인 생각이",
    "intrusive thoughts, they should be": "보고되었지만, 해롭지 않은 것으로",
    "regarded as harmless.": "간주해야 합니다.",
    "In most cases.": "대부분은요.",
    "Infested Temple Treasure Key": "감염된 사원 보물 열쇠",
    "This key twists and turns, signaling its use for a higher vault.": (
        "이 열쇠는 비틀리고 휘어져 있으며, 상위 금고에 쓰인다는 것을 나타냅니다."
    ),
    "Kisegi Sanctuary Treasure Key": "키세기 성소 보물 열쇠",
    "Meant for a more complex mechanism, this key may open higher vaults.": (
        "더 복잡한 장치에 맞는 열쇠로, 상위 금고를 열 수 있습니다."
    ),
    "Two treasure keys are required to open a treasure vault.": (
        "보물 금고를 열려면 보물 열쇠 두 개가 필요합니다."
    ),
    "Kisegi Sanctuary Ominous Treasure Key": "키세기 성소 불길한 보물 열쇠",
    "A faint chant can be heard in the distance when holding this key. An arachnid chorus of familiar faces.": (
        "이 열쇠를 들면 멀리서 희미한 성가가 들립니다. 익숙한 얼굴을 한 거미류의 합창입니다."
    ),
    "Note: Redistribute to the Mushroom Mines": "참고: 버섯 광산으로 재분배할 것.",
    "Note: Supplier has since cut contact.": "참고: 공급자가 이후 연락을 끊었음.",
    "Note: Supplier has stated their lifelong disdain": "참고: 공급자는 평생에 걸쳐",
    'for the "frog-folks".': '"개구리 종족"을 혐오한다고 밝혔음.',
    "Abstain from delivering to the Keep.": "성채에는 납품하지 말 것.",
    "Note: Must be delivered to the lightning chambers.": (
        "참고: 번개실로 배송해야 함."
    ),
    "Mining Complex Treasure Key": "채굴 단지 보물 열쇠",
    "Rupee": "루피",
    "Infested Temple Key": "감염된 사원 열쇠",
    "Infested Temple Ominous Key": "감염된 사원 불길한 열쇠",
    "Unsettlingly weightless, this key urges you forward of its own accord.": (
        "불안할 만큼 무게가 없는 이 열쇠는 스스로 앞으로 나아가라고 재촉합니다."
    ),
    "Kisegi Sanctuary Key": "키세기 성소 열쇠",
    "Kisegi Sanctuary Ominous Key": "키세기 성소 불길한 열쇠",
    "Covered in silk, this key seems to resonate with the voices of a thousand spiders.": (
        "비단실에 덮인 이 열쇠에서는 수천 마리 거미의 목소리가 울리는 듯합니다."
    ),
}

NBT_TEXT = {
    '"17236151OWO"': '"17236151OWO"',
    "-": "-",
    "---------------": "---------------",
    ".": ".",
    "1ts f0r the": "더 큰",
    "===============": "===============",
    "A Golem's": "골렘의",
    "A Melony": "멜론",
    "A beacon of": "희망의",
    "A bow under a": "붉은 구름 아래",
    "A faint chant can be heard in the distance when holding this key. An arachnid chorus of familiar faces.": (
        "이 열쇠를 들면 멀리서 희미한 성가가 들립니다. 익숙한 얼굴을 한 거미류의 합창입니다."
    ),
    "A spoonful of": "파리",
    "All Star": "올스타",
    "Ancestor": "선조",
    "Bikini": "비키니",
    "Black Widow": "검은과부거미",
    "Blessed by": "폭풍의",
    "Blessing": "축복",
    "Bottom": "시티",
    "Breakdown": "붕괴",
    "Cabin": "오두막",
    "Capybara's": "카피바라의",
    "Cauldron of ": "마녀의",
    "Celeste": "셀레스트",
    "Cliffside Caves": "절벽 동굴",
    "Covered in silk, this key seems to resonate with the voices of a thousand spiders.": (
        "비단실에 덮인 이 열쇠에서는 수천 마리 거미의 목소리가 울리는 듯합니다."
    ),
    "Creation shard": "창조의 파편",
    "Cursed Pants": "저주받은 바지",
    "Debris Miner": "잔해 광부",
    "Depths of": "하스신의",
    "DiamondTown": "DiamondTown",
    "Dinnerbone": "Dinnerbone",
    "Drunken Villager": "술 취한 주민",
    "Elder": "말씀",
    "Elephant": "코끼리",
    "Emerald": "에메랄드",
    "Exist for ": "사랑을 위해",
    "Eye": "눈",
    "Eye of the": "우주의",
    "Eyes": "눈",
    "Faithful": "올로크",
    "Fireflies": "비행",
    "Forge Sentry": "대장간 파수꾼",
    "Forger of": "별의",
    "Foundry Guardian": "주조소 수호자",
    "Frash Bang!!": "섬광탄!!",
    "Free!": "무료!",
    "Frog before": "천국 앞의",
    "Frogal ": "프로갈",
    "Frogging Object": "개구리형 물체",
    "Frogging the": "개구리화한",
    "Froggus": "운명",
    "Froggy Mountain": "개구리 산",
    "Frogithiru": "프로기시루",
    "Fungus Turtle": "균류 거북",
    "Gate 3": "3번 관문",
    "Gearling": "기어링",
    "Gears": "Gears",
    "Gunflex": "건플렉스",
    "Harvest": "수확",
    "Hathsin": "심연",
    "Heaven": "개구리",
    "Hope": "봉화",
    "Hot place": "뜨거운 곳은",
    "Hut in the": "늪지의",
    "I am a Stick!": "나는 막대기다!",
    "If you walk with": "균류와 함께 걸으면",
    "Impostor": "임포스터",
    "Infested Temple Key": "감염된 사원 열쇠",
    "Infested Temple Ominous Key": "감염된 사원 불길한 열쇠",
    "Infested Temple Treasure Key": "감염된 사원 보물 열쇠",
    "Killer": "살인",
    "Kinda": "검 비슷한",
    "Kisegi Sanctuary Key": "키세기 성소 열쇠",
    "Kisegi Sanctuary Ominous Key": "키세기 성소 불길한 열쇠",
    "Kisegi Sanctuary Ominous Treasure Key": "키세기 성소 불길한 보물 열쇠",
    "Kisegi Sanctuary Treasure Key": "키세기 성소 보물 열쇠",
    "Knights": "기사단",
    "Knowledge is": "아는 것이",
    "Kocke Kola": "Kocke Kola",
    "Little": "작은",
    "Love": "존재한다",
    "Love Letter": "연애편지",
    "Lucy in the Sky": "다이아몬드와 함께",
    "Meal": "식사",
    "Meant for a more complex mechanism, this key may open higher vaults.": (
        "더 복잡한 장치에 맞는 열쇠로, 상위 금고를 열 수 있습니다."
    ),
    "Mechanical": "기계식",
    "Mining Complex Treasure Key": "채굴 단지 보물 열쇠",
    "Mountain": "산",
    "Mountains": "산속",
    "Next Home": "다음 보금자리",
    "Octopus": "문어",
    "Old Palace": "옛 궁전",
    "Olloch The": "충직한",
    "One ring to ": "모든 것을 지배할",
    "Only the worthy": "자격 있는 자만",
    "Our home": "우리의 집",
    "Outside": "나갈 시간",
    "Painting": "그림",
    "Pattern, help.": "무늬가 필요해.",
    "Pipse": "Pipse",
    "Plants": "식물",
    "Poor's man clothing": "가난뱅이의 옷",
    "Power": "힘이다",
    "Radiant ": "빛나는",
    "Red and Blue": "빨강과 파랑",
    "Reindordt The": "현자",
    "Richard, the Survivor": "생존자 리처드",
    "Ride of the": "반딧불이의",
    "Ship": "배",
    "Skeleton before": "업데이트 이전",
    "Standard Death Arrows": "표준 죽음의 화살",
    "Stars": "대장장이",
    "Stingy Situation!": "인색한 상황!",
    "Swamp": "오두막",
    "Sword": "무언가",
    "Termination": "종결",
    "The": "",
    "The All-seeing": "모든 것을 보는",
    "The Blind Eye": "눈먼 눈",
    "The Boss": "우두머리",
    "The End": "엔드의",
    "The Fate of": "프로거스의",
    "The Storm": "축복",
    "The dichotomy of Machine and Man": "기계와 인간의 이분법",
    "The good, the bad": "좋은 놈, 나쁜 놈",
    "The touch of our": "양서류 신의",
    "TheCatsKing": "TheCatsKing",
    "TheY lI3 t0": "그들은 우리에게",
    "They s4y": "그들은 말하지",
    "This is not": "이것은",
    "This key twists and turns, signaling its use for a higher vault.": (
        "이 열쇠는 비틀리고 휘어져 있으며, 상위 금고에 쓰인다는 것을 나타냅니다."
    ),
    "Throwing": "투척용",
    "Time to go": "밖으로",
    "To claim prize": "상품 수령용",
    "To narrow to ": "좁혀 보니",
    "To narrow to be": "좁혀 보니",
    "Traitor's web": "배신자의 거미줄",
    "Two treasure keys are required to open a treasure vault.": (
        "보물 금고를 열려면 보물 열쇠 두 개가 필요합니다."
    ),
    "Unidentified": "미확인",
    "Universe": "눈",
    "Unlicensed Alchemist": "무허가 연금술사",
    "Unsettlingly weightless, this key urges you forward of its own accord.": (
        "불안할 만큼 무게가 없는 이 열쇠는 스스로 앞으로 나아가라고 재촉합니다."
    ),
    "W3 weRe n0T ": "우리가 항상",
    "Watcher": "감시자",
    "Weakest": "가장 나약한",
    "What the h*ll": "대체 뭘",
    "Wise": "레인도르트",
    "Words of the": "원로의",
    "You are an": "당신은",
    "a painting": "그림",
    "a trap": "함정이 아니다",
    "alW4yS l1Ke th3m": "그들과 같진 않았어",
    "amphibian God": "손길",
    "and the frog": "그리고 개구리",
    "are you doing ": "하고 있는 거야",
    "be a painting 2": "그림 2",
    "d": "d",
    "flies": "한 숟갈",
    "go0d...": "위해서라고...",
    "great3r": "선을",
    "here?": "여기서?",
    "not for us": "우리 자리가 아니다",
    "out of spores.": "못할 거야.",
    "red cloud": "활",
    "rule them all": "절대 반지",
    "shall ring": "종을",
    "the Bell.": "울릴 수 있다.",
    "the Update": "스켈레톤",
    "the fungus,": "포자에서",
    "the witch": "가마솥",
    "uS": "거짓말했어",
    "with Diamonds": "하늘의 루시",
    "www.minecraft-heads.com": "www.minecraft-heads.com",
    "you'll never be": "영원히 벗어나지",
    "مدخل جنة الجحيم": "지옥 낙원의 입구",
}

RUNTIME_LANGUAGE_ALIASES = {
    "enchantment.dungeons_arise.lolth_curse": "롤스의 저주",
}

LEET_NBT_VALUES = {
    "1ts f0r the",
    "TheY lI3 t0",
    "They s4y",
    "W3 weRe n0T ",
    "alW4yS l1Ke th3m",
    "go0d...",
    "great3r",
}


def translated_nbt_literal(source: str) -> str:
    """기술 ID를 보존하면서 NBT 표시 원문의 확정 번역을 반환해요."""
    if source.startswith("Custom Head ID: "):
        return source.replace("Custom Head ID: ", "커스텀 머리 ID: ", 1)
    return NBT_TEXT[source]


def find_jar() -> Path:
    """현재 설치본의 When Dungeons Arise JAR 하나를 찾아요."""
    matches = sorted((resolve_source_root() / "mods").glob(JAR_PATTERN))
    if len(matches) != 1:
        raise FileNotFoundError(f"JAR이 정확히 한 개가 아니에요: {matches}")
    return matches[0]


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없는 JSON을 안정된 형식으로 기록해요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def read_language(locale: str) -> dict[str, str]:
    """현재 JAR의 언어 JSON 객체를 읽어요."""
    with ZipFile(find_jar()) as archive:
        internal = f"assets/{NAMESPACE}/lang/{locale}.json"
        if internal not in archive.namelist():
            return {}
        value = json.loads(archive.read(internal))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(text, str) for key, text in value.items()
    ):
        raise TypeError(f"{locale} 언어 파일이 문자열 객체가 아니에요")
    return value


def walk_json(value: object, path: str = "$") -> list[tuple[str, str, object]]:
    """JSON 안의 모든 키와 값을 경로와 함께 모아요."""
    rows = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            rows.append((key, child_path, child))
            rows.extend(walk_json(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(walk_json(child, f"{path}[{index}]"))
    return rows


def component_literal_text(value: object) -> str | None:
    """텍스트 컴포넌트에서 직접 표시되는 문자열만 합쳐요."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        rows = [component_literal_text(child) for child in value]
        text = "".join(child for child in rows if child)
        return text or None
    if not isinstance(value, dict) or "translate" in value:
        return None
    rows = []
    if isinstance(value.get("text"), str):
        rows.append(value["text"])
    if "extra" in value:
        extra = component_literal_text(value["extra"])
        if extra:
            rows.append(extra)
    text = "".join(rows)
    return text or None


def nbt_component_literal(value: str) -> str | None:
    """NBT 문자열이 JSON 컴포넌트면 실제 직접 표시 문자만 꺼내요."""
    try:
        component = json.loads(value)
    except json.JSONDecodeError:
        return value or None
    return component_literal_text(component)


def visible_nbt_strings(
    tag: Tag,
    path: tuple[str | int, ...] = (),
    parent_name: str | None = None,
) -> list[dict[str, str]]:
    """구조물 NBT에서 책·표지판·이름 문자열을 모아요."""
    rows = []
    if tag.kind == 10:
        for name, child in tag.value.items():
            child_path = path + (name,)
            if child.kind == 8 and name in VISIBLE_NBT_STRING_NAMES:
                literal = nbt_component_literal(str(child.value))
                if literal and literal.strip():
                    rows.append(
                        {
                            "path": "/" + "/".join(map(str, child_path)),
                            "source": str(child.value),
                            "literal": literal,
                        }
                    )
            rows.extend(visible_nbt_strings(child, child_path, name))
    elif tag.kind == 9:
        child_kind, children = tag.value
        if child_kind == 8 and parent_name in VISIBLE_NBT_LIST_NAMES:
            for index, child in enumerate(children):
                literal = nbt_component_literal(str(child.value))
                if literal and literal.strip():
                    rows.append(
                        {
                            "path": "/" + "/".join(map(str, path + (index,))),
                            "source": str(child.value),
                            "literal": literal,
                        }
                    )
        else:
            for index, child in enumerate(children):
                rows.extend(visible_nbt_strings(child, path + (index,), parent_name))
    return rows


def scan_visible_nbt(raw: bytes) -> list[dict[str, str]]:
    """대형 블록 배열을 만들지 않고 NBT의 표시 문자열만 스트리밍으로 읽어요."""
    stream = io.BytesIO(raw)
    rows = []

    def read_exact(length: int) -> bytes:
        value = stream.read(length)
        if len(value) != length:
            raise EOFError(f"NBT가 예정보다 일찍 끝났어요: {len(value)}/{length}")
        return value

    def read_string() -> str:
        length = struct.unpack(">H", read_exact(2))[0]
        return read_exact(length).decode("utf-8")

    def add(path: tuple[str | int, ...], source: str) -> None:
        literal = nbt_component_literal(source)
        if literal and literal.strip():
            rows.append(
                {
                    "path": "/" + "/".join(map(str, path)),
                    "source": source,
                    "literal": literal,
                }
            )

    def scan_payload(
        kind: int,
        path: tuple[str | int, ...],
        name: str | None = None,
    ) -> None:
        scalar_sizes = {1: 1, 2: 2, 3: 4, 4: 8, 5: 4, 6: 8}
        if kind in scalar_sizes:
            read_exact(scalar_sizes[kind])
        elif kind == 7:
            length = struct.unpack(">i", read_exact(4))[0]
            read_exact(length)
        elif kind == 8:
            value = read_string()
            if name in VISIBLE_NBT_STRING_NAMES:
                add(path, value)
        elif kind == 9:
            child_kind = struct.unpack(">B", read_exact(1))[0]
            length = struct.unpack(">i", read_exact(4))[0]
            for index in range(length):
                child_path = path + (index,)
                if child_kind == 8 and name in VISIBLE_NBT_LIST_NAMES:
                    add(child_path, read_string())
                else:
                    scan_payload(child_kind, child_path, name)
        elif kind == 10:
            while True:
                child_kind = struct.unpack(">B", read_exact(1))[0]
                if child_kind == 0:
                    break
                child_name = read_string()
                scan_payload(child_kind, path + (child_name,), child_name)
        elif kind in {11, 12}:
            length = struct.unpack(">i", read_exact(4))[0]
            read_exact(length * (4 if kind == 11 else 8))
        else:
            raise ValueError(f"지원하지 않는 NBT 태그 종류예요: {kind}")

    root_kind = struct.unpack(">B", read_exact(1))[0]
    if root_kind != 10:
        raise ValueError(f"NBT 루트가 compound가 아니에요: {root_kind}")
    read_string()
    scan_payload(root_kind, ())
    if stream.read(1):
        raise ValueError("NBT 루트 뒤에 해석하지 못한 데이터가 있어요")
    return rows


def prepare() -> dict[str, object]:
    """언어·데이터 JSON·구조물 NBT의 현재 표시 원문을 전부 추출해요."""
    jar = find_jar()
    english = read_language("en_us")
    korean = read_language("ko_kr")
    if len(english) != EXPECTED_LANGUAGE_KEYS:
        raise ValueError(
            f"영어 키 수가 달라요: {len(english)} != {EXPECTED_LANGUAGE_KEYS}"
        )
    write_json(WORK_ROOT / "en_us.json", english)
    if korean:
        write_json(WORK_ROOT / "bundled_ko_kr.json", korean)

    data_direct = []
    data_localized = []
    invalid_json = []
    data_json_files = []
    nbt_rows = []
    nbt_files = []
    guide_entries = []
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            lower = name.lower()
            if lower.endswith((".md", ".txt", ".json")) and any(
                segment in lower
                for segment in ("/book/", "/guide/", "/manual/", "patchouli")
            ):
                guide_entries.append(name)
            if lower.startswith("data/") and lower.endswith(".json"):
                data_json_files.append(name)
                try:
                    value = json.loads(archive.read(name))
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    invalid_json.append(f"{name}: {exc}")
                    continue
                for key, path, child in walk_json(value):
                    if key not in VISIBLE_DATA_KEYS:
                        continue
                    row = {"file": name, "path": path, "value": child}
                    if isinstance(child, dict) and isinstance(
                        child.get("translate"), str
                    ):
                        data_localized.append(row)
                    else:
                        literal = component_literal_text(child)
                        if literal and literal.strip():
                            data_direct.append({**row, "literal": literal})
            if not lower.endswith(".nbt"):
                continue
            nbt_files.append(name)
            compressed = archive.read(name)
            try:
                raw = gzip.decompress(compressed)
            except gzip.BadGzipFile:
                raw = compressed
            for row in scan_visible_nbt(raw):
                nbt_rows.append({"file": name, **row})

    def catalog(rows: list[dict[str, object]]) -> list[dict[str, object]]:
        occurrences: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in rows:
            literal = str(row["literal"])
            occurrences[literal].append(
                {key: value for key, value in row.items() if key != "literal"}
            )
        return [
            {
                "source": source,
                "occurrences": values,
                "count": len(values),
            }
            for source, values in sorted(occurrences.items())
        ]

    report = {
        "family": FAMILY,
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_mtime_ns": jar.stat().st_mtime_ns,
        "language_keys": len(english),
        "bundled_korean_candidate_keys": len(korean),
        "data_json_files": len(data_json_files),
        "data_localized_fields": data_localized,
        "data_direct_fields": data_direct,
        "data_direct_catalog": catalog(data_direct),
        "nbt_files": len(nbt_files),
        "nbt_visible_fields": nbt_rows,
        "nbt_direct_catalog": catalog(nbt_rows),
        "guide_candidates": guide_entries,
        "invalid_json": invalid_json,
        "errors": invalid_json,
        "status": "prepared"
        if not invalid_json and not guide_entries
        else "incomplete",
    }
    write_json(WORK_ROOT / "source_surface_catalog.json", report)
    summary = {
        "family": FAMILY,
        "jar": jar.name,
        "language_keys": len(english),
        "bundled_korean_candidate_keys": len(korean),
        "data_json_files": len(data_json_files),
        "data_localized_fields": len(data_localized),
        "data_direct_fields": len(data_direct),
        "data_direct_unique_values": len(report["data_direct_catalog"]),
        "nbt_files": len(nbt_files),
        "nbt_visible_fields": len(nbt_rows),
        "nbt_direct_unique_values": len(report["nbt_direct_catalog"]),
        "guide_candidates": len(guide_entries),
        "errors": invalid_json,
        "status": report["status"],
    }
    write_json(WORK_ROOT / "inventory.json", summary)
    return summary


def replace_component_literal(source: str, target: str) -> str:
    """JSON 컴포넌트의 스타일을 보존하고 직접 표시 문자만 바꿔요."""
    try:
        component = json.loads(source)
    except json.JSONDecodeError:
        return target
    if isinstance(component, str):
        component = target
    elif isinstance(component, dict) and isinstance(component.get("text"), str):
        if component_literal_text(component) != component["text"]:
            raise ValueError(f"복합 NBT 컴포넌트는 자동 치환할 수 없어요: {source}")
        component["text"] = target
    else:
        raise ValueError(f"알 수 없는 NBT 텍스트 컴포넌트예요: {source}")
    return json.dumps(component, ensure_ascii=False, separators=(",", ":"))


def transform_nbt(raw: bytes) -> tuple[bytes, list[tuple[str, str]]]:
    """NBT의 표시 문자열만 바꾸고 나머지 이진 태그를 그대로 복사해요."""
    source_stream = io.BytesIO(raw)
    target_stream = io.BytesIO()
    replacements = []

    def read_exact(length: int) -> bytes:
        value = source_stream.read(length)
        if len(value) != length:
            raise EOFError(f"NBT가 예정보다 일찍 끝났어요: {len(value)}/{length}")
        return value

    def copy_exact(length: int) -> None:
        target_stream.write(read_exact(length))

    def read_string() -> str:
        length = struct.unpack(">H", read_exact(2))[0]
        return read_exact(length).decode("utf-8")

    def write_string(value: str) -> None:
        encoded = value.encode("utf-8")
        target_stream.write(struct.pack(">H", len(encoded)))
        target_stream.write(encoded)

    def transform_string(value: str) -> str:
        literal = nbt_component_literal(value)
        if not literal or not literal.strip():
            return value
        target_literal = translated_nbt_literal(literal)
        if target_literal == literal:
            return value
        replacements.append((literal, target_literal))
        return replace_component_literal(value, target_literal)

    def transform_payload(kind: int, name: str | None = None) -> None:
        scalar_sizes = {1: 1, 2: 2, 3: 4, 4: 8, 5: 4, 6: 8}
        if kind in scalar_sizes:
            copy_exact(scalar_sizes[kind])
        elif kind == 7:
            length_raw = read_exact(4)
            target_stream.write(length_raw)
            length = struct.unpack(">i", length_raw)[0]
            copy_exact(length)
        elif kind == 8:
            value = read_string()
            if name in VISIBLE_NBT_STRING_NAMES:
                value = transform_string(value)
            write_string(value)
        elif kind == 9:
            child_kind_raw = read_exact(1)
            length_raw = read_exact(4)
            target_stream.write(child_kind_raw)
            target_stream.write(length_raw)
            child_kind = struct.unpack(">B", child_kind_raw)[0]
            length = struct.unpack(">i", length_raw)[0]
            for _index in range(length):
                if child_kind == 8 and name in VISIBLE_NBT_LIST_NAMES:
                    write_string(transform_string(read_string()))
                else:
                    transform_payload(child_kind, name)
        elif kind == 10:
            while True:
                child_kind_raw = read_exact(1)
                target_stream.write(child_kind_raw)
                child_kind = struct.unpack(">B", child_kind_raw)[0]
                if child_kind == 0:
                    break
                child_name = read_string()
                write_string(child_name)
                transform_payload(child_kind, child_name)
        elif kind in {11, 12}:
            length_raw = read_exact(4)
            target_stream.write(length_raw)
            length = struct.unpack(">i", length_raw)[0]
            copy_exact(length * (4 if kind == 11 else 8))
        else:
            raise ValueError(f"지원하지 않는 NBT 태그 종류예요: {kind}")

    root_kind_raw = read_exact(1)
    target_stream.write(root_kind_raw)
    root_kind = struct.unpack(">B", root_kind_raw)[0]
    if root_kind != 10:
        raise ValueError(f"NBT 루트가 compound가 아니에요: {root_kind}")
    write_string(read_string())
    transform_payload(root_kind)
    if source_stream.read(1):
        raise ValueError("NBT 루트 뒤에 해석하지 못한 데이터가 있어요")
    return target_stream.getvalue(), replacements


def transform_data_value(value: object) -> tuple[object, list[tuple[str, str]]]:
    """데이터 JSON에서 검수한 직접 표시 필드만 번역해요."""
    replacements = []

    def transform(child: object, parent_key: str | None = None) -> object:
        if isinstance(child, dict):
            return {key: transform(item, key) for key, item in child.items()}
        if isinstance(child, list):
            return [transform(item, parent_key) for item in child]
        if (
            isinstance(child, str)
            and parent_key in VISIBLE_DATA_KEYS
            and child in DATA_TEXT
        ):
            target = DATA_TEXT[child]
            replacements.append((child, target))
            return target
        return child

    return transform(value), replacements


def build() -> dict[str, object]:
    """언어와 직접 표시 데이터·NBT를 확정 번역으로 만들어요."""
    catalog_path = WORK_ROOT / "source_surface_catalog.json"
    if not catalog_path.is_file():
        raise FileNotFoundError("prepare로 만든 현재 원문 목록이 없어요")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    jar = find_jar()
    if (
        catalog.get("jar") != jar.name
        or catalog.get("jar_size") != jar.stat().st_size
        or catalog.get("jar_mtime_ns") != jar.stat().st_mtime_ns
    ):
        raise RuntimeError(
            "현재 JAR이 원문 추출 당시와 달라요. prepare를 다시 실행하세요"
        )

    english = read_language("en_us")
    missing_language = sorted(set(english.values()) - set(LANG_TEXT))
    extra_language = sorted(set(LANG_TEXT) - set(english.values()))
    if missing_language or extra_language:
        raise KeyError(
            f"언어 번역표가 현재 원문과 달라요: missing={missing_language}, "
            f"extra={extra_language}"
        )
    korean = {key: LANG_TEXT[source] for key, source in english.items()}
    korean.update(RUNTIME_LANGUAGE_ALIASES)
    write_json(WORK_ROOT / "ko_kr.json", korean)
    write_json(LANG_OUTPUT, korean)

    data_sources = {row["source"] for row in catalog["data_direct_catalog"]}
    if data_sources != set(DATA_TEXT):
        raise KeyError(
            "데이터 번역표가 현재 원문과 달라요: "
            f"missing={sorted(data_sources - set(DATA_TEXT))}, "
            f"extra={sorted(set(DATA_TEXT) - data_sources)}"
        )
    nbt_sources = {row["source"] for row in catalog["nbt_direct_catalog"]}
    missing_nbt = []
    for source in sorted(nbt_sources):
        try:
            translated_nbt_literal(source)
        except KeyError:
            missing_nbt.append(source)
    if missing_nbt or set(NBT_TEXT) - nbt_sources:
        raise KeyError(
            "NBT 번역표가 현재 원문과 달라요: "
            f"missing={missing_nbt}, extra={sorted(set(NBT_TEXT) - nbt_sources)}"
        )

    data_files = sorted({row["file"] for row in catalog["data_direct_fields"]})
    expected_data_replacements = len(catalog["data_direct_fields"])
    nbt_changed_rows = [
        row
        for row in catalog["nbt_visible_fields"]
        if translated_nbt_literal(row["literal"]) != row["literal"]
    ]
    nbt_files = sorted({row["file"] for row in nbt_changed_rows})
    data_reports = []
    nbt_reports = []
    with ZipFile(jar) as archive:
        for internal in data_files:
            source = json.loads(archive.read(internal))
            target, replacements = transform_data_value(source)
            output = OVERRIDE_ROOT / internal
            write_json(output, target)
            data_reports.append(
                {
                    "source": internal,
                    "output": output.relative_to(PROJECT_ROOT).as_posix(),
                    "replacements": [
                        {"source": source_text, "target": target_text}
                        for source_text, target_text in replacements
                    ],
                }
            )
        for internal in nbt_files:
            source_bytes = archive.read(internal)
            compressed = source_bytes.startswith(b"\x1f\x8b")
            raw = gzip.decompress(source_bytes) if compressed else source_bytes
            target_raw, replacements = transform_nbt(raw)
            output = OVERRIDE_ROOT / internal
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(
                gzip.compress(target_raw, mtime=0) if compressed else target_raw
            )
            nbt_reports.append(
                {
                    "source": internal,
                    "output": output.relative_to(PROJECT_ROOT).as_posix(),
                    "replacements": [
                        {"source": source_text, "target": target_text}
                        for source_text, target_text in replacements
                    ],
                }
            )
    data_replacements = sum(len(row["replacements"]) for row in data_reports)
    nbt_replacements = sum(len(row["replacements"]) for row in nbt_reports)
    errors = []
    if data_replacements != expected_data_replacements:
        errors.append(
            f"데이터 번역 수가 달라요: {data_replacements} != {expected_data_replacements}"
        )
    if nbt_replacements != len(nbt_changed_rows):
        errors.append(
            f"NBT 번역 수가 달라요: {nbt_replacements} != {len(nbt_changed_rows)}"
        )
    write_json(WORK_ROOT / "translated_data_files.json", data_reports)
    write_json(WORK_ROOT / "translated_nbt_files.json", nbt_reports)
    report = {
        "family": FAMILY,
        "reviewed_language_keys": len(english),
        "runtime_language_aliases": len(RUNTIME_LANGUAGE_ALIASES),
        "language_output_keys": len(korean),
        "data_files": len(data_reports),
        "data_replacements": data_replacements,
        "nbt_files": len(nbt_reports),
        "nbt_replacements": nbt_replacements,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def load_json_without_duplicates(path: Path) -> tuple[object, list[str]]:
    """중복 키를 놓치지 않고 JSON을 읽어요."""
    duplicates = []

    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        value = {}
        for key, child in pairs:
            if key in value:
                duplicates.append(key)
            value[key] = child
        return value

    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook)
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        return {}, [f"{path}: JSON을 읽지 못했어요: {exc}"]
    return value, [f"{path} 중복 키: {key}" for key in duplicates]


def preserved_errors(label: str, source: str, target: str) -> list[str]:
    """자리표시자·서식·숫자·줄바꿈을 보존했는지 확인해요."""
    errors = []
    for name, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식 코드", FORMAT_CODE),
        ("숫자", NUMBER),
    ):
        source_values = Counter(pattern.findall(source))
        target_values = Counter(pattern.findall(target))
        if source_values != target_values:
            errors.append(
                f"{label} {name} 불일치: {dict(source_values)} != {dict(target_values)}"
            )
    if source.count("\n") != target.count("\n"):
        errors.append(f"{label} 실제 줄바꿈 수가 달라요")
    if source.count("\\n") != target.count("\\n"):
        errors.append(f"{label} 이스케이프 줄바꿈 수가 달라요")
    return errors


def audit_references() -> tuple[dict[str, object], list[str]]:
    """FTB Quests와 KubeJS의 관련 참조와 직접 표시 후보를 확인해요."""
    instance = resolve_source_root()
    errors = []
    report: dict[str, object] = {"ftbquests": [], "kubejs": [], "read_errors": []}
    suffixes = {".cfg", ".js", ".json", ".snbt", ".toml", ".txt"}
    for label, base in (
        ("ftbquests", instance / "config/ftbquests/quests"),
        ("kubejs", instance / "kubejs"),
    ):
        rows = report[label]
        if not isinstance(rows, list) or not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                read_errors = report["read_errors"]
                if isinstance(read_errors, list):
                    read_errors.append(f"{path}: {exc}")
                continue
            count = text.lower().count(f"{NAMESPACE}:")
            if not count:
                continue
            visible_lines = []
            for number, line in enumerate(text.splitlines(), 1):
                if f"{NAMESPACE}:" not in line.lower():
                    continue
                if re.search(
                    r"(?i)(?:custom_name|displayname|display_name|lore|subtitle|title|tooltip)"
                    r"\s*[:=(]",
                    line,
                ):
                    visible_lines.append(number)
            row = {
                "path": path.relative_to(instance).as_posix(),
                "namespace_occurrences": count,
                "visible_namespace_candidate_lines": visible_lines,
            }
            rows.append(row)
            if visible_lines:
                errors.append(f"{label}에 직접 표시 문구 후보가 있어요: {row}")
    read_errors = report["read_errors"]
    if isinstance(read_errors, list):
        errors.extend(str(message) for message in read_errors)
    return report, errors


def audit() -> tuple[dict[str, object], list[str]]:
    """현재 원문 목록·런타임 번역 키·외부 표시 경로를 감사해요."""
    errors = []
    catalog_path = WORK_ROOT / "source_surface_catalog.json"
    if not catalog_path.is_file():
        return {"status": "incomplete"}, ["prepare 원문 목록이 없어요"]
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    jar = find_jar()
    if (
        catalog.get("jar") != jar.name
        or catalog.get("jar_size") != jar.stat().st_size
        or catalog.get("jar_mtime_ns") != jar.stat().st_mtime_ns
    ):
        errors.append("현재 JAR이 원문 추출 당시와 달라요")
    if catalog.get("invalid_json"):
        errors.append(f"읽지 못한 데이터 JSON이 있어요: {catalog['invalid_json']}")
    if catalog.get("guide_candidates"):
        errors.append(f"별도 가이드 후보가 있어요: {catalog['guide_candidates']}")
    english = read_language("en_us")
    runtime_keys = set(english) | set(RUNTIME_LANGUAGE_ALIASES)
    missing_localized = sorted(
        {
            row["value"]["translate"]
            for row in catalog["data_localized_fields"]
            if row["value"]["translate"].startswith(
                ("advancement.dungeons_arise", "enchantment.dungeons_arise")
            )
            and row["value"]["translate"] not in runtime_keys
        }
    )
    if missing_localized:
        errors.append(
            f"실제 데이터가 참조하지만 제공되지 않는 번역 키가 있어요: {missing_localized}"
        )
    references, reference_errors = audit_references()
    errors.extend(reference_errors)
    report = {
        "family": FAMILY,
        "source_catalog": {
            "language_keys": catalog["language_keys"],
            "data_localized_fields": len(catalog["data_localized_fields"]),
            "data_direct_fields": len(catalog["data_direct_fields"]),
            "nbt_visible_fields": len(catalog["nbt_visible_fields"]),
            "guides": len(catalog["guide_candidates"]),
        },
        "runtime_language_aliases": RUNTIME_LANGUAGE_ALIASES,
        "missing_localized_keys": missing_localized,
        "references": references,
        "ftbquests_display_work": (
            "no_related_references"
            if not references["ftbquests"]
            else "namespace_ids_only"
        ),
        "kubejs_display_work": (
            "no_related_references"
            if not references["kubejs"]
            else "namespace_ids_only"
        ),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def verify_language() -> tuple[dict[str, object], list[str]]:
    """현재 영어 119키와 런타임 별칭 1키의 확정 번역을 검증해요."""
    errors = []
    english = read_language("en_us")
    expected = {key: LANG_TEXT[source] for key, source in english.items()}
    expected.update(RUNTIME_LANGUAGE_ALIASES)
    work, work_errors = load_json_without_duplicates(WORK_ROOT / "ko_kr.json")
    output, output_errors = load_json_without_duplicates(LANG_OUTPUT)
    errors.extend(work_errors + output_errors)
    if not isinstance(work, dict) or not isinstance(output, dict):
        return {"status": "incomplete"}, errors
    expected_order = list(english) + list(RUNTIME_LANGUAGE_ALIASES)
    if list(work) != expected_order or list(output) != expected_order:
        errors.append("언어 키 또는 순서가 현재 영어 원문과 런타임 별칭 목록과 달라요")
    if work != output or output != expected:
        errors.append("작업본·산출물·확정 번역값이 서로 달라요")
    same_as_source = set()
    no_hangul = set()
    foreign_script = {}
    for key, target in output.items():
        source = english.get(key, "Curse of Lolth")
        errors.extend(preserved_errors(key, source, target))
        if source == target:
            same_as_source.add(key)
        if target and not re.search(r"[가-힣]", target):
            no_hangul.add(key)
        foreign = sorted(set(FOREIGN_SCRIPT.findall(target)))
        if foreign:
            foreign_script[key] = foreign
    expected_same = {
        key for key, source in english.items() if LANG_TEXT[source] == source
    }
    if same_as_source != expected_same:
        errors.append(
            "영어와 같은 값 검토 결과가 달라요: "
            f"missing={sorted(expected_same - same_as_source)}, "
            f"unexpected={sorted(same_as_source - expected_same)}"
        )
    if no_hangul - expected_same:
        errors.append(
            f"한국어가 없는 언어 값이 있어요: {sorted(no_hangul - expected_same)}"
        )
    if foreign_script:
        errors.append(f"한국어 외 문자권 문자가 남았어요: {foreign_script}")
    report = {
        "reviewed_english_keys": len(english),
        "runtime_alias_keys": len(RUNTIME_LANGUAGE_ALIASES),
        "output_keys": len(output),
        "bundled_korean_candidate_keys": len(read_language("ko_kr")),
        "existing_korean_values_reused": 0,
        "new_language_values": len(output),
        "intentional_same_keys": sorted(same_as_source),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify_data_outputs() -> tuple[dict[str, object], list[str]]:
    """16개 데이터 JSON에서 계획한 99개 표시 필드만 바뀌었는지 확인해요."""
    errors = []
    manifest_path = WORK_ROOT / "translated_data_files.json"
    if not manifest_path.is_file():
        return {"status": "incomplete"}, ["데이터 번역 기록이 없어요"]
    rows = json.loads(manifest_path.read_text(encoding="utf-8"))
    replacement_count = 0
    with ZipFile(find_jar()) as archive:
        for row in rows:
            source = json.loads(archive.read(row["source"]))
            expected, replacements = transform_data_value(source)
            output_path = resolve_active_output_path(row["output"])
            output, output_errors = load_json_without_duplicates(output_path)
            errors.extend(output_errors)
            if output != expected:
                errors.append(f"데이터 산출물이 확정 변환값과 달라요: {row['output']}")
            for source_text, target_text in replacements:
                errors.extend(
                    preserved_errors(
                        f"{row['source']} {source_text}", source_text, target_text
                    )
                )
            replacement_count += len(replacements)
    if replacement_count != 99:
        errors.append(f"데이터 표시 필드 번역 수가 달라요: {replacement_count} != 99")
    report = {
        "files": len(rows),
        "replacements": replacement_count,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify_nbt_outputs() -> tuple[dict[str, object], list[str]]:
    """33개 NBT 산출물을 다시 읽어 230개 번역과 모든 경로를 확인해요."""
    errors = []
    catalog = json.loads(
        (WORK_ROOT / "source_surface_catalog.json").read_text(encoding="utf-8")
    )
    manifest_path = WORK_ROOT / "translated_nbt_files.json"
    if not manifest_path.is_file():
        return {"status": "incomplete"}, ["NBT 번역 기록이 없어요"]
    rows = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_by_file: dict[str, list[tuple[str, str]]] = defaultdict(list)
    changed_count = 0
    for row in catalog["nbt_visible_fields"]:
        target = translated_nbt_literal(row["literal"])
        if row["literal"] not in LEET_NBT_VALUES:
            errors.extend(
                preserved_errors(f"{row['file']} {row['path']}", row["literal"], target)
            )
        if target != row["literal"]:
            changed_count += 1
        if target.strip():
            expected_by_file[row["file"]].append((row["path"], target))
    manifest_files = {row["source"] for row in rows}
    expected_files = {
        file
        for file, values in expected_by_file.items()
        if any(
            translated_nbt_literal(source_row["literal"]) != source_row["literal"]
            for source_row in catalog["nbt_visible_fields"]
            if source_row["file"] == file
        )
    }
    if manifest_files != expected_files:
        errors.append(
            "NBT 파일 목록이 달라요: "
            f"missing={sorted(expected_files - manifest_files)}, "
            f"extra={sorted(manifest_files - expected_files)}"
        )
    for row in rows:
        output_path = resolve_active_output_path(row["output"])
        try:
            value = output_path.read_bytes()
            raw = gzip.decompress(value) if value.startswith(b"\x1f\x8b") else value
            actual = [(item["path"], item["literal"]) for item in scan_visible_nbt(raw)]
        except (EOFError, OSError, UnicodeError, ValueError) as exc:
            errors.append(f"NBT 산출물을 읽지 못했어요: {row['output']}: {exc}")
            continue
        expected = expected_by_file[row["source"]]
        if actual != expected:
            errors.append(f"NBT 표시 경로나 번역값이 달라요: {row['output']}")
    if changed_count != 230:
        errors.append(f"NBT 표시 필드 번역 수가 달라요: {changed_count} != 230")
    report = {
        "files": len(rows),
        "translated_visible_fields": changed_count,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def deployment_paths() -> set[str]:
    """이 모드가 실제 인스턴스에 적용할 정확한 상대 경로를 반환해요."""
    paths = {"resourcepacks/ATM10_Korean/assets/dungeons_arise/lang/ko_kr.json"}
    for manifest_name in ("translated_data_files.json", "translated_nbt_files.json"):
        manifest_path = WORK_ROOT / manifest_name
        if not manifest_path.is_file():
            continue
        rows = json.loads(manifest_path.read_text(encoding="utf-8"))
        paths.update(output_deployment_path(row["output"]) for row in rows)
    return paths


def verify() -> tuple[dict[str, object], list[str]]:
    """언어·데이터·NBT·외부 표시 경로를 모두 검증해요."""
    language, language_errors = verify_language()
    data, data_errors = verify_data_outputs()
    nbt, nbt_errors = verify_nbt_outputs()
    surface, surface_errors = audit()
    errors = language_errors + data_errors + nbt_errors + surface_errors
    expected_override_files = {
        path.removeprefix("kubejs/")
        for path in deployment_paths()
        if path.startswith("kubejs/data/dungeons_arise/")
    }
    actual_override_files = {
        path.relative_to(OVERRIDE_ROOT).as_posix()
        for path in (OVERRIDE_ROOT / "data/dungeons_arise").rglob("*")
        if path.is_file()
    }
    if actual_override_files != expected_override_files:
        errors.append(
            "덮어쓰기 산출물 목록이 달라요: "
            f"missing={sorted(expected_override_files - actual_override_files)}, "
            f"extra={sorted(actual_override_files - expected_override_files)}"
        )
    report = {
        "family": FAMILY,
        "language": language,
        "data": data,
        "nbt": nbt,
        "surface_audit": surface["status"],
        "ftbquests": surface["ftbquests_display_work"],
        "kubejs": surface["kubejs_display_work"],
        "output_files": len(deployment_paths()),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = (
        json.loads(deployment_path.read_text(encoding="utf-8"))
        if deployment_path.is_file()
        else None
    )
    completion = {
        "family": FAMILY,
        "reviewed_language_keys": language["reviewed_english_keys"],
        "runtime_language_aliases": language["runtime_alias_keys"],
        "existing_korean_values_reused": language["existing_korean_values_reused"],
        "new_language_values": language["new_language_values"],
        "translated_data_fields": data["replacements"],
        "translated_nbt_fields": nbt["translated_visible_fields"],
        "ftbquests_work": surface["ftbquests_display_work"],
        "kubejs_work": surface["kubejs_display_work"],
        "output_files": sorted(deployment_paths()),
        "deployment": deployment,
        "errors": errors,
        "status": (
            "complete"
            if not errors
            and (
                deployment is None or deployment.get("status") == "applied_and_verified"
            )
            else "incomplete"
        ),
    }
    write_json(WORK_ROOT / "family_completion.json", completion)
    return report, errors


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 매니페스트의 대상·백업·해시 결과를 작업 기록에 연결해요."""
    errors = []
    manifest_path = manifest_path.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 매니페스트 상태가 완료가 아니에요")
    if manifest.get("java_processes"):
        errors.append(
            f"적용 당시 Java 프로세스가 있었어요: {manifest['java_processes']}"
        )
    expected = deployment_paths()
    targets = manifest.get("targets", [])
    if not isinstance(targets, list) or not targets:
        errors.append("적용 대상 기록이 없어요")
        targets = []
    summaries = []
    for target in targets:
        records = {
            row.get("relative_path"): row
            for row in target.get("files", [])
            if isinstance(row, dict)
        }
        missing = sorted(expected - set(records))
        extra = sorted(set(records) - expected)
        if missing or extra:
            errors.append(f"적용 경로가 달라요: missing={missing}, extra={extra}")
        hash_errors = sorted(
            path
            for path in expected & set(records)
            if records[path].get("source_sha256") != records[path].get("after_sha256")
        )
        if hash_errors:
            errors.append(f"적용 후 해시가 달라요: {hash_errors}")
        if target.get("status") != "applied_and_verified":
            errors.append(
                f"대상 적용 상태가 완료가 아니에요: {target.get('target_root')}"
            )
        if target.get("unexpected_changes"):
            errors.append(f"예상 밖 적용 변경이 있어요: {target['unexpected_changes']}")
        summaries.append(
            {
                "target_type": target.get("target_type"),
                "target_root": target.get("target_root"),
                "changed_paths": target.get("changed_paths", []),
                "unexpected_changes": target.get("unexpected_changes", []),
                "hash_verified_paths": sorted(expected - set(hash_errors)),
            }
        )
    try:
        manifest_name = manifest_path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        manifest_name = str(manifest_path)
    report = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "backup_manifest": manifest_name,
        "expected_paths": sorted(expected),
        "targets": summaries,
        "errors": errors,
    }
    write_json(WORK_ROOT / "deployment_report.json", report)
    return report, errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "build", "audit", "verify", "record-deployment"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare()
    elif args.command == "build":
        result = build()
    elif args.command == "audit":
        result, _ = audit()
    elif args.command == "verify":
        result, _ = verify()
    else:
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        result, _ = record_deployment(args.manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return (
        0 if result["status"] in {"prepared", "complete", "applied_and_verified"} else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
