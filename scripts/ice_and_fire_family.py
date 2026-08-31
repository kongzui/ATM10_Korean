#!/usr/bin/env python3
"""Ice and Fire 언어와 전용 FTB Quests를 현재 영어 원문으로 전면 재검수해요."""

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

import five_family_goal as family_goal
import ars_family
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "ice_and_fire"
ROOT = PROJECT_ROOT / "working" / FAMILY
LANG = ROOT / "iceandfire"
BUNDLED = LANG / "bundled_candidates.json"
QUEST = ROOT / "quests/ice__fire"
RELATED = ROOT / "quests/related"
QUEST_REVIEW_CACHE = PROJECT_ROOT / "temp/ice_and_fire_quest_review_cache.json"
QUEST_REVIEWED = QUEST / "reviewed_auto_candidates.json"
GUIDES = ROOT / "guides"
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets/iceandfire"
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
IMAGE = re.compile(r"\{image:[^}]+\}")
QUEST_PROTECTED = re.compile(
    r"(?:\\n)+"
    r"|\n+"
    r"|https?://\S+"
    r"|%(?:\d+\$)?[a-zA-Z%]"
    r"|\{[A-Za-z0-9_]+\}"
    r"|\$\([^)]*\)"
    r"|/\$"
    r"|[&§][0-9A-FK-ORa-fk-or]"
    r"|<[^>]+>"
)

REPLACEMENTS = (
    ("Ice and Fire", "Ice and Fire"),
    ("아이스 앤 파이어", "Ice and Fire"),
    ("아이스 드래곤스틸", "얼음 드래곤스틸"),
    ("파이어 드래곤스틸", "화염 드래곤스틸"),
    ("라이트닝 드래곤스틸", "번개 드래곤스틸"),
    ("아이스 드래곤", "얼음 드래곤"),
    ("파이어 드래곤", "화염 드래곤"),
    ("라이트닝 드래곤", "번개 드래곤"),
    ("Ice Dragon", "얼음 드래곤"),
    ("Fire Dragon", "화염 드래곤"),
    ("Lightning Dragon", "번개 드래곤"),
    ("Dragonsteel", "드래곤스틸"),
    ("Dragon Steel", "드래곤스틸"),
    ("DragonForge", "드래곤 대장간"),
    ("Dragon Forge", "드래곤 대장간"),
    ("Dragonforge", "드래곤 대장간"),
    ("Dragon Blood", "드래곤 피"),
    ("Dragon Bone", "드래곤 뼈"),
    ("Dragon Scale", "드래곤 비늘"),
    ("Dragon Egg", "드래곤 알"),
    ("Dragon Roost", "드래곤 둥지"),
    ("Dragon Cave", "드래곤 동굴"),
    ("Dragons", "드래곤"),
    ("Dragon", "드래곤"),
    ("Bestiary Lectern", "괴물 도감 독서대"),
    ("Bestiary", "괴물 도감"),
    ("Manuscripts", "필사본"),
    ("Manuscript", "필사본"),
    ("Death Worm", "데스 웜"),
    ("죽음의 벌레", "데스 웜"),
    ("죽음 벌레", "데스 웜"),
    ("죽음벌레", "데스 웜"),
    ("죽음 벌래", "데스 웜"),
    ("Hippogryph", "히포그리프"),
    ("Hippogryth", "히포그리프"),
    ("Hippocampus", "히포캄푸스"),
    ("해마", "히포캄푸스"),
    ("Cockatrice", "코카트리스"),
    ("Stymphalian", "스팀팔리안"),
    ("스팀팔리언", "스팀팔리안"),
    ("스팀팔리아", "스팀팔리안"),
    ("스팀팔로스 청동새", "스팀팔리안 새"),
    ("스팀팔로스의 새", "스팀팔리안 새"),
    ("스팀팔로스 새", "스팀팔리안 새"),
    ("Myrmex", "미르멕스"),
    ("Sea Serpent", "바다뱀"),
    ("씨 서펀트", "바다뱀"),
    ("Amphithere", "암피테레"),
    ("엠피데어", "암피테레"),
    ("Gorgon", "고르곤"),
    ("Cyclops", "키클롭스"),
    ("사이클롭스", "키클롭스"),
    ("Hydra", "히드라"),
    ("Siren", "세이렌"),
    ("사이렌", "세이렌"),
    ("Troll", "트롤"),
    ("Pixie", "픽시"),
    ("Ghost", "유령"),
    ("Dread", "드레드"),
    ("Wither", "위더"),
    ("Armor Points", "방어력"),
    ("Hearts", "체력"),
    ("Cooldown", "재사용 대기시간"),
    ("Right Click", "우클릭"),
    ("Right-click", "우클릭"),
    ("Shift Right Click", "Shift+우클릭"),
    ("Spawn Egg", "생성 알"),
    ("산란 알", "생성 알"),
    ("썩은 계란", "썩은 알"),
    ("드래곤 식사", "드래곤 먹이"),
    ("고르곤 헤드", "고르곤의 머리"),
    ("히포그리스", "히포그리프"),
    ("히포그리드", "히포그리프"),
    ("드래곤강철", "드래곤스틸"),
    ("드래곤 강철", "드래곤스틸"),
    ("드래곤포지", "드래곤 대장간"),
    ("드래곤 블러드", "드래곤 피"),
    ("드래곤 Blood", "드래곤 피"),
    ("휴식처", "둥지"),
    ("장갑 포인트", "방어력"),
    ("방어 포인트", "방어력"),
    ("방어구 포인트", "방어력"),
    ("하트", "체력"),
    ("폭도", "몹"),
    ("건강", "체력"),
    ("요금을 부과", "돌진"),
    ("무효화됩니다", "사라집니다"),
    ("어떤 방울도 주지 않을 것입니다", "아무 아이템도 드롭하지 않습니다"),
    ("네사체", "나일륨"),
    ("마귀나무", "악마 나무"),
    ("레시피", "제작법"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("왼쪽 클릭", "좌클릭"),
    ("엔터티", "개체"),
    ("엔티티", "개체"),
    ("쿨다운", "재사용 대기시간"),
    ("드랍", "드롭"),
    ("아머", "방어구"),
    ("헤드", "머리"),
    ("죽이십시오", "처치하세요"),
    ("길들이십시오", "길들이세요"),
    ("스테이지", "단계"),
    ("Stage", "단계"),
    ("얼음과 불", "Ice and Fire"),
    ("아이스 앤 파이어", "Ice and Fire"),
    ("길들인 데스 웜", "길들여진 데스 웜"),
    ("길들인 용", "길들여진 드래곤"),
    ("닭고기 달걀", "닭의 알"),
    (" 하트", " 체력"),
    ("&b&l얼음&f과 &c불&r", "&b&lIce &fand &cFire&r"),
    ("&b&l다른 쪽&r", "&b&lThe Other&r"),
    ("allthemods", "AllTheMods"),
    ("atm10", "ATM10"),
    ("Jar", "병"),
    ("pixie", "픽시"),
    ("(x)", "(X)"),
    ("(g)", "(G)"),
    ("&4t&0n&4t", "&4T&0N&4T"),
    ("토끼 발 하나만", "토끼 발 1개만"),
    ("눈이 하나 뿐", "눈이 1개뿐"),
    ("한 번만 사용할 수", "1회만 사용할 수"),
    ("두 가지 다른 방법", "2가지 방법"),
    ("폭이 겨우 1/4 블록부터", "폭이 블록의 사분의 일 정도부터"),
    ("라이트 블루", "하늘색"),
    ("라이트 그레이", "밝은 회색"),
    ("블랙", "검은"),
    ("블루", "파란"),
    ("브라운", "갈색"),
    ("그레이", "회색"),
    ("오렌지", "주황색"),
    ("핑크", "분홍색"),
    ("레드", "빨간"),
    ("화이트", "하얀"),
    ("옐로우", "노란"),
)

QUEST_REPLACEMENTS = (
    ("계란", "알"),
    ("썩은 달걀", "썩은 알"),
    ("보금자리", "둥지"),
    ("&b&l얼음 &f및 &c불&r", "&b&lIce &fand &cFire&r"),
    ("&b&l다른&r", "&b&lThe Other&r"),
    ("&b&l다른 몬스터&r", "&b&lThe Other&r"),
    ("&l1단계&r에서 &l3개", "&l1단계&r부터 &l3단계"),
    ("&l4단계&r 및 &l5개", "&l4단계&r와 &l5단계"),
    ("&l4단계&r 또는 &l5마리의", "&l4단계&r 또는 &l5단계"),
    ("초과 근무를 하면서", "시간이 지나면서"),
    ("공격도 받습니다", "공격도 사용할 수 있습니다"),
    ("자이언트 데스 웜", "거대 데스 웜"),
    ("막대한 피해", "큰 피해"),
    ("&c불을&r 설정합니다", "&c불&r을 붙입니다"),
    (
        "담배를 피우며 날아다니는 것을 볼 수 있습니다",
        "날아다니며 둥지 근처의 몹을 불태웁니다",
    ),
    ("그들이 무엇을 하기를 기대해야 합니까?", "어떤 공격을 하는지 알아볼까요?"),
    ("물린 후 입에 물릴 수도", "입으로 물어뜯을 수도"),
    (
        "초기 &l단계&r &c속성 공격&r은 가장 큰 걱정거리가 아니라, "
        "오히려 비행하고 당신을 따라오는 능력이 최악입니다.",
        "낮은 &l단계&r에서는 &c속성 공격&r보다 날아다니며 끝까지 "
        "쫓아오는 능력이 더 위험합니다.",
    ),
    ("게다가 꼬리 같은 팬.", "꼬리에는 부채 모양 지느러미도 있습니다."),
    (
        "그들의 &b얼음 숨&r이 &b얼어붙고&r 길을 가로막는 플레이어와 "
        "블록이 될 것입니다.",
        "그들의 &b얼음 숨결&r은 앞을 가로막는 플레이어와 블록을 " "&b얼립니다&r.",
    ),
    (
        "그들의 &b냉혹한 공격&r은 당신을 &b얼어붙게&r 손상시킬 수 있으므로",
        "그들의 &b얼음 공격&r은 당신을 &b얼리고&r 피해를 줄 수 있으므로",
    ),
    ("그들에게서 뒤로 던질", "뒤로 밀쳐낼"),
    ("머리에만 6개의 뿔", "머리에 6개의 뿔"),
    ("그들은 혼란스러울 수 있는 서서 잠을 잔다.", "헷갈릴 수 있지만 서서 잠을 잡니다."),
    ("더 많은 피해를 보상합니다", "대신 더 큰 피해를 줍니다"),
    ("갈가리 찢어지고", "물어뜯고"),
    ("한 명을 죽였나요?", "한 마리를 쓰러뜨렸나요?"),
    ("킬에서", "시체에서"),
    ("&5체력&r를 얻을 수 없지만", "&5심장&r을 얻을 수 없지만"),
    ("번개 용의 피", "번개 드래곤 피"),
    (
        "&e데스 웜&r는 &e사막&r의 모래를 파고드는 괴물처럼 침출됩니다.",
        "&e데스 웜&r은 &e사막&r의 모래 속에 굴을 파고 다니는 거머리 모양의 괴물입니다.",
    ),
    ("크기로 제공됩니다", "크기로 나타납니다"),
    ("&7방어력&r가 4개", "&7방어력&r은 4"),
    ("당신에게 무너질", "당신을 덮칠"),
    ("근처에 &4T&0N&4T&r 불을 켜면", "근처의 &4T&0N&4T&r에 불을 붙이면"),
    ("드래곤&r의 요소", "드래곤&r의 속성"),
    ("손상, 낙하 및 생성을 결정합니다", "공격력, 드롭, 생성 위치를 결정합니다"),
    ("가장 위험하고 중요한 괴물일 뿐입니다", "가장 위험하고 중요한 몬스터입니다"),
    ("희귀한 방울", "희귀 드롭"),
    ("손상을 입히", "피해를 입히"),
    ("손상시킬", "피해를 줄"),
    ("&c플루트&r", "&c피리&r"),
    (
        "이 퀘스트는 다음에 의해 출시되지 않은 공개 팩에서 사용할 수 없습니다. "
        "&6AllTheMods 팀&r 명시적인 허가 없이.",
        "이 퀘스트는 &6AllTheMods 팀&r의 명시적인 허가 없이 다른 공개 팩에서 "
        "사용할 수 없습니다.",
    ),
    ("Shift 막대로 마우스 오른쪽 버튼으로 클릭", "막대기를 들고 Shift+우클릭"),
    ("얼어붙기&f또는", "빙결&f 또는"),
    ("&5비늘&f또는", "&5비늘&f 또는"),
    ("&b비늘&f또는", "&b비늘&f 또는"),
)

EXACT = {
    "advancements.iceandfire.deathworm_egg.title": "폴 아트레이디스",
    "advancements.iceandfire.kill_ghost.title": "누구에게 전화할까요?",
    "advancements.iceandfire.root.title": "Ice and Fire",
    "advancements.iceandfire.tame_hippocampus.title": "프리 윌리",
    "itemGroup.iceandfire": "Ice and Fire",
    "item.iceandfire.bestiary": "괴물 도감",
    "block.iceandfire.lectern": "괴물 도감 독서대",
    "entity.iceandfire.cockatrice": "코카트리스",
    "entity.iceandfire.hippogryph": "히포그리프",
    "entity.iceandfire.hippocampus": "히포캄푸스",
    "item.iceandfire.stymphalian_feather_bundle.desc_0": (
        "사용자 주위 8방향으로 날카로운 깃털을 발사합니다"
    ),
    "block.iceandfire.dragonforge_lightning_core": "번개 드래곤 대장간 코어",
    "block.iceandfire.dragonforge_lightning_core_disabled": "번개 드래곤 대장간 코어",
    "block.iceandfire.dragonforge_lightning_input": "번개 드래곤 대장간 투입구",
    "item.iceandfire.banner_pattern_eye.desc": "키클롭스 눈 문양",
    "item.iceandfire.cyclops_eye": "키클롭스의 눈",
    "item.iceandfire.banner_pattern_hippogryph_head.desc": "히포그리프 머리 문양",
    "item.iceandfire.hippogryph_skull": "히포그리프 두개골",
    "item.iceandfire.banner_pattern_troll.desc": "트롤 머리 문양",
    "item.iceandfire.troll_skull": "트롤 두개골",
    "item.iceandfire.deathworm_gauntlet.desc_1": "대상을 플레이어 쪽으로 끌어옵니다",
    "item.iceandfire.pixie_wand.desc_1": "픽시 가루를 탄약으로 사용합니다",
    "dragon.name": "이름:",
    "entity.minecraft.villager.scribe": "서기관",
    "item.iceandfire.hippogryph_sword.desc_1": "사용할 때마다 휩쓸기 공격을 합니다",
    "item.iceandfire.tide_trident_inventory": "파도 삼지창",
    "item.iceandfire.dragon_skull_fire": "화염 드래곤 두개골",
    "item.iceandfire.dragon_skull_ice": "얼음 드래곤 두개골",
    "item.iceandfire.dragon_skull_lightning": "번개 드래곤 두개골",
    "config.iceandfire.cockatrice.eggChance": "알을 던졌을 때 생성될 확률",
    "config.iceandfire.dragon.eggBornTime": "알 부화 시간",
    "block.iceandfire.graveyard_soil.desc": "밤에 유령이 생성됩니다",
    "death.attack.dragon.0": "%s은(는) 드래곤에게 두 동강 났습니다",
    "death.attack.dragon.1": "%s은(는) 드래곤에게 갈기갈기 찢겼습니다",
    "death.attack.dragon.2": "%s은(는) 드래곤에게 잡아먹혔습니다",
    "death.attack.dragon.attacker_0": "%s은(는) %s에게 두 동강 났습니다",
    "death.attack.dragon.attacker_1": "%s은(는) %s에게 갈기갈기 찢겼습니다",
    "death.attack.dragon.attacker_2": "%s은(는) %s에게 잡아먹혔습니다",
    "death.attack.dragon_fire.0": "%s은(는) 드래곤에게 KFC가 되었습니다",
    "death.attack.dragon_fire.1": "%s은(는) 드래곤에게 불태워졌습니다",
    "death.attack.dragon_fire.2": "%s은(는) 드래곤에게 잿더미가 되었습니다",
    "death.attack.dragon_fire.attacker_0": "%s은(는) %s에게 KFC가 되었습니다",
    "death.attack.dragon_fire.attacker_1": "%s은(는) %s에게 불태워졌습니다",
    "death.attack.dragon_fire.attacker_2": "%s은(는) %s에게 잿더미가 되었습니다",
    "death.attack.dragon_ice.0": "%s은(는) 드래곤에게 얼어붙었습니다",
    "death.attack.dragon_ice.1": "%s은(는) 드래곤에게 얼음이 되었습니다",
    "death.attack.dragon_ice.2": "%s은(는) 드래곤에게 냉동 수면에 빠졌습니다",
    "death.attack.dragon_ice.attacker_0": "%s은(는) %s에게 얼어붙었습니다",
    "death.attack.dragon_ice.attacker_1": "%s은(는) %s에게 얼음이 되었습니다",
    "death.attack.dragon_ice.attacker_2": "%s은(는) %s에게 냉동 수면에 빠졌습니다",
    "death.attack.dragon_lightning.0": "%s은(는) 드래곤이 내리친 번개에 맞았습니다",
    "death.attack.dragon_lightning.1": "%s은(는) 드래곤에게 과충전되었습니다",
    "death.attack.dragon_lightning.2": "%s은(는) 드래곤에게 감전되었습니다",
    "death.attack.dragon_lightning.attacker_0": "%s은(는) %s에게 과충전되었습니다",
    "death.attack.dragon_lightning.attacker_1": "%s은(는) %s이(가) 내리친 번개에 맞았습니다",
    "death.attack.dragon_lightning.attacker_2": "%s은(는) %s에게 감전되었습니다",
    "death.attack.gorgon.0": "%s은(는) 고르곤에게 돌이 되었습니다",
    "death.attack.gorgon.1": "%s은(는) 고르곤에게 고르곤졸라가 되었습니다",
    "death.attack.gorgon.2": "%s은(는) 고르곤에게 석화되었습니다",
    "death.attack.gorgon.attacker_0": "%s은(는) %s에게 돌이 되었습니다",
    "death.attack.gorgon.attacker_1": "%s은(는) %s에게 고르곤졸라가 되었습니다",
    "death.attack.gorgon.attacker_2": "%s은(는) %s에게 석화되었습니다",
}

GUIDE_TRANSLATIONS = {
    "patchouli_books/iceandfire/ko_kr/categories/introduction.json": {
        "name": "소개",
        "description": "기본 소개 페이지",
        "icon": "minecraft:writable_book",
        "sortnum": 1,
    },
    "patchouli_books/iceandfire/ko_kr/entries/introduction.json": {
        "name": "소개",
        "icon": "minecraft:writable_book",
        "category": "iceandfire:introduction",
        "pages": [
            {
                "type": "patchouli:spotlight",
                "item": {"item": "iceandfire:manuscript"},
                "title": "소개",
                "text": (
                    "괴물 도감 표지 뒤에 낡고 해진 쪽지가 붙어 있습니다. 쪽지에는 "
                    "이렇게 적혀 있습니다:$(br)“초자연적인 도구 설계와 신비로운 "
                    "생물을 찾는 방법을 기록한 이 필사본을 미지의 경이를 탐험하려는 "
                    "이에게 바칩니다. 이 책이 모험에 도움이 되기를 바랍니다.”"
                ),
            }
        ],
    },
    "tinkers/book/ko_kr/modifiers/flame.json": {
        "modifier": "flame",
        "text": [
            {
                "text": "화염 드래곤의 피로 도구를 코팅하면 적에게 불을 붙이는 힘이 깃듭니다."
            },
            {"text": "\n"},
            {
                "text": (
                    "드래곤스틸 도구에는 적용할 수 없습니다. Blizzard와 함께 사용할 "
                    "수 없습니다."
                )
            },
            {"text": "\n"},
        ],
        "effects": [
            "적에게 10초 동안 불을 붙입니다",
            "드래곤 화염 추가 피해",
            "단일 단계만 존재",
        ],
        "demoTool": [
            "tconstruct:broadsword",
            "tconstruct:cleaver",
            "tconstruct:hammer",
            "tconstruct:arrow",
            "tconstruct:longsword",
            "tconstruct:shortbow",
            "tconstruct:frypan",
            "tconstruct:crossbow",
            "tconstruct:scythe",
            "tconstruct:shuriken",
        ],
    },
    "tinkers/book/ko_kr/modifiers/frost.json": {
        "modifier": "frost",
        "text": [
            {
                "text": "얼음 드래곤의 피로 도구를 코팅하면 적을 얼음에 가두는 힘이 깃듭니다."
            },
            {"text": "\n"},
            {
                "text": (
                    "드래곤스틸 도구에는 적용할 수 없습니다. Inferno와 함께 사용할 "
                    "수 없습니다."
                )
            },
            {"text": "\n"},
        ],
        "effects": [
            "적을 10초 동안 얼음에 가둡니다",
            "드래곤 냉기 추가 피해",
            "둔화 효과 부여",
            "단일 단계만 존재",
        ],
        "demoTool": [
            "tconstruct:broadsword",
            "tconstruct:cleaver",
            "tconstruct:hammer",
            "tconstruct:arrow",
            "tconstruct:longsword",
            "tconstruct:shortbow",
            "tconstruct:frypan",
            "tconstruct:crossbow",
            "tconstruct:scythe",
            "tconstruct:shuriken",
        ],
    },
}

GUIDE_SOURCES = {
    "patchouli_books/iceandfire/ko_kr/categories/introduction.json": (
        "assets/iceandfire/patchouli_books/iceandfire/en_us/categories/introduction.json"
    ),
    "patchouli_books/iceandfire/ko_kr/entries/introduction.json": (
        "assets/iceandfire/patchouli_books/iceandfire/en_us/entries/introduction.json"
    ),
    "tinkers/book/ko_kr/modifiers/flame.json": (
        "assets/iceandfire/tinkers/book/en_us/modifiers/flame.json"
    ),
    "tinkers/book/ko_kr/modifiers/frost.json": (
        "assets/iceandfire/tinkers/book/en_us/modifiers/frost.json"
    ),
}


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def bundled_candidates() -> dict[str, object]:
    """현재 설치 JAR의 한국어를 검수 후보로만 읽어 와요."""
    instance = resolve_source_root()
    jar = family_goal.find_jar(instance, "iceandfire-")
    with ZipFile(jar) as archive:
        value = json.loads(
            archive.read("assets/iceandfire/lang/ko_kr.json").decode("utf-8")
        )
    if not isinstance(value, dict):
        raise TypeError(jar)
    write(BUNDLED, value)
    return value


def normalize_guides() -> list[dict[str, object]]:
    """JAR의 별도 안내서 표시 문구를 한국어 로케일 파일로 만들어요."""
    instance = resolve_source_root()
    jar = family_goal.find_jar(instance, "iceandfire-")
    rows = []
    with ZipFile(jar) as archive:
        for destination, source_name in GUIDE_SOURCES.items():
            source = json.loads(archive.read(source_name).decode("utf-8"))
            translated = GUIDE_TRANSLATIONS[destination]
            source_path = GUIDES / "source" / destination
            target_path = GUIDES / "ko_kr" / destination
            output_path = OUTPUT_ASSETS / destination
            write(source_path, source)
            write(target_path, translated)
            write(output_path, translated)
            rows.append(
                {
                    "source": source_name,
                    "output": output_path.relative_to(PROJECT_ROOT).as_posix(),
                }
            )
    return rows


def review(source: object, candidate: object) -> object:
    if isinstance(source, list) and isinstance(candidate, list):
        return [
            review(left, right) for left, right in zip(source, candidate, strict=True)
        ]
    if not isinstance(source, str) or not isinstance(candidate, str):
        return candidate
    if IMAGE.fullmatch(source):
        return source
    value = candidate
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    value = value.replace("화염용", "화염 드래곤")
    value = value.replace("얼음용", "얼음 드래곤")
    value = value.replace("번개용", "번개 드래곤")
    value = re.sub(
        r"(?<![가-힣])용(?=(?:&[0-9a-fk-or])|[은이가을를의과도만, .!?])",
        "드래곤",
        value,
    )
    return value


def review_quest(source: object, candidate: object) -> object:
    """퀘스트에서만 나타나는 기계번역 어순과 게임 용어를 다듬어요."""
    value = review(source, candidate)
    if not isinstance(value, str):
        if isinstance(value, list):
            return [
                review_quest(left, right)
                for left, right in zip(source, value, strict=True)
            ]
        return value
    for old, new in QUEST_REPLACEMENTS:
        value = value.replace(old, new)
    return value


def review_language(key: str, source: object, candidate: object) -> object:
    """생성 알·설정·배너처럼 키 역할이 분명한 이름을 일관되게 정리해요."""
    value = review(source, candidate)
    if not isinstance(value, str):
        return value
    if key.startswith("item.iceandfire.spawn_egg_"):
        match = re.fullmatch(r"스폰 (.+)", value)
        if match:
            value = f"{match.group(1)} 생성 알"
    if key.startswith("config.iceandfire."):
        if key.endswith(".spawn"):
            value = "생성 허용"
        elif key.endswith(".spawnWeight"):
            value = "생성 가중치"
        elif key.endswith(".spawnChance"):
            value = "생성 확률"
        elif key.endswith(".canDespawn"):
            value = "자연 소멸 허용"
    if "banner_pattern_" in key and "_head.desc" in key:
        if key.endswith("_head.desc"):
            value = value.replace("두개골", "머리 문양")
        else:
            value = value.replace("두개골", "머리")
    return value


def lower_source(source: str) -> str:
    """퀘스트의 과도한 영문 대문자를 낮춰 자연스러운 번역 후보를 만들어요."""
    if IMAGE.fullmatch(source) or source.startswith("{@"):
        return source
    return source.lower()


def request_review_translation(source: str) -> str:
    """HTML 태그형 표식으로 서식 위치와 한국어 어순을 함께 보존해요."""
    protected: list[str] = []

    def mask(match: re.Match[str]) -> str:
        index = len(protected)
        protected.append(match.group(0))
        return f"<x{index}/>"

    masked = QUEST_PROTECTED.sub(mask, source)
    query = urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": "ko", "dt": "t", "q": masked}
    )
    request = urllib.request.Request(
        f"{ars_family.GOOGLE_TRANSLATE}?{query}",
        headers={"User-Agent": "ATM10-Korean-quest-review/1.0"},
    )
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            translated = "".join(row[0] for row in payload[0] if row and row[0])
            for index, value in enumerate(protected):
                marker = f"<x{index}/>"
                translated = translated.replace(marker, value)
            if re.search(r"<x\d+/>", translated):
                raise ValueError(f"복원되지 않은 보호 표식이 있습니다: {translated}")
            if Counter(protected) != Counter(QUEST_PROTECTED.findall(translated)):
                raise ValueError(f"보호 토큰 수가 바뀌었습니다: {translated}")
            return translated
        except Exception as exc:  # pragma: no cover - 외부 후보 서비스 오류 보고용
            last_error = exc
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"퀘스트 번역 후보 요청 실패: {source}") from last_error


def iter_strings(value: object) -> list[str]:
    """문자열 또는 문자열 배열을 순서대로 펼쳐요."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    raise TypeError(f"지원하지 않는 퀘스트 값: {value!r}")


def refresh_quests() -> dict[str, object]:
    """전용 퀘스트를 소문자 정규화 원문으로 다시 번역해 후보 품질을 높여요."""
    english = load(QUEST / "en_us.json")
    cache = load(QUEST_REVIEW_CACHE) if QUEST_REVIEW_CACHE.is_file() else {}
    requests = {
        lower_source(text)
        for value in english.values()
        for text in iter_strings(value)
        if not IMAGE.fullmatch(text) and not text.startswith("{@")
    }
    pending = sorted(
        source for source in requests if not isinstance(cache.get(source), str)
    )
    if pending:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(request_review_translation, source): source
                for source in pending
            }
            for future in as_completed(futures):
                source = futures[future]
                cache[source] = future.result()
        write(QUEST_REVIEW_CACHE, cache)

    reviewed: dict[str, object] = {}
    for key, value in english.items():
        translated = []
        for text in iter_strings(value):
            normalized = lower_source(text)
            translated.append(text if normalized not in requests else cache[normalized])
        reviewed[key] = translated[0] if isinstance(value, str) else translated
    write(QUEST_REVIEWED, reviewed)
    result = {
        "scope": "ice__fire",
        "keys": len(reviewed),
        "unique_strings": len(requests),
        "new_requests": len(pending),
        "status": "complete",
    }
    write(ROOT / "quest_candidate_review.json", result)
    return result


def normalize() -> dict[str, object]:
    english = load(LANG / "en_us.json")
    auto = load(LANG / "auto_candidates.json")
    bundled = bundled_candidates()
    write(
        LANG / "candidate_sources.json",
        {
            key: "bundled_ko_kr" if key in bundled else "new_translation_required"
            for key in english
        },
    )
    reviewed = {}
    bundled_reviewed = 0
    for key, source in english.items():
        candidate = EXACT.get(key)
        if candidate is None:
            candidate = bundled.get(key)
            if (
                candidate is None
                or candidate == source
                or family_goal.validate_value(key, source, candidate)
            ):
                candidate = auto[key]
            else:
                bundled_reviewed += 1
        reviewed[key] = review_language(key, source, candidate)
    write(LANG / "ko_kr.json", reviewed)
    language_keys = len(reviewed)
    guides = normalize_guides()
    quest_rows = []
    for root in (QUEST, RELATED):
        english = load(root / "en_us.json")
        reviewed_path = root / "reviewed_auto_candidates.json"
        auto = load(
            reviewed_path if reviewed_path.is_file() else root / "auto_candidates.json"
        )
        reviewed = {
            key: review_quest(source, auto[key]) for key, source in english.items()
        }
        write(root / "ko_kr.json", reviewed)
        quest_rows.append({"scope": root.name, "keys": len(reviewed)})
    result = {
        "language_keys": language_keys,
        "bundled_candidates_reviewed": bundled_reviewed,
        "new_translations_reviewed": language_keys - bundled_reviewed,
        "quests": quest_rows,
        "guides": guides,
        "status": "complete",
    }
    write(ROOT / "normalization.json", result)
    return result


def verify_pair(root: Path) -> tuple[dict[str, object], list[str]]:
    english, korean = load(root / "en_us.json"), load(root / "ko_kr.json")
    errors = []
    if list(english) != list(korean):
        errors.append(f"키 또는 순서 불일치: {root.name}")
    for key in english.keys() & korean.keys():
        source, target = english[key], korean[key]
        errors.extend(family_goal.validate_value(key, source, target))
        source_values = source if isinstance(source, list) else [source]
        target_values = target if isinstance(target, list) else [target]
        for index, (left, right) in enumerate(
            zip(source_values, target_values, strict=True)
        ):
            if not isinstance(left, str) or not isinstance(right, str):
                continue
            source_numbers = Counter(NUMBER.findall(left))
            if source_numbers and source_numbers != Counter(NUMBER.findall(right)):
                errors.append(f"숫자 불일치: {root.name}:{key}[{index}]")
            if Counter(IMAGE.findall(left)) != Counter(IMAGE.findall(right)):
                errors.append(f"이미지 구문 불일치: {root.name}:{key}[{index}]")
    return {"scope": root.name, "keys": len(english)}, errors


def validate_guide(source: object, target: object, path: str) -> list[str]:
    """안내서의 자료형·식별자·숫자·줄바꿈을 재귀적으로 검사해요."""
    errors = family_goal.validate_value(path, source, target)
    if errors or type(source) is not type(target):
        return errors
    if isinstance(source, dict):
        assert isinstance(target, dict)
        for key in source:
            if key in {"modifier", "type", "item", "icon", "category", "demoTool"}:
                if source[key] != target[key]:
                    errors.append(f"안내서 식별자 불일치: {path}.{key}")
            errors.extend(validate_guide(source[key], target[key], f"{path}.{key}"))
    elif isinstance(source, list):
        assert isinstance(target, list)
        for index, (left, right) in enumerate(zip(source, target, strict=True)):
            errors.extend(validate_guide(left, right, f"{path}[{index}]"))
    elif isinstance(source, str):
        assert isinstance(target, str)
        if Counter(NUMBER.findall(source)) != Counter(NUMBER.findall(target)):
            errors.append(f"안내서 숫자 불일치: {path}")
        if re.fullmatch(r"[a-z0-9_]+:[a-z0-9_./-]+", source) and source != target:
            errors.append(f"안내서 네임스페이스 불일치: {path}")
    return errors


def verify() -> tuple[dict[str, object], list[str]]:
    rows, errors = [], []
    for root in (LANG, QUEST, RELATED):
        row, current = verify_pair(root)
        rows.append(row)
        errors.extend(current)
    guide_rows = []
    for destination in GUIDE_SOURCES:
        source_path = GUIDES / "source" / destination
        target_path = GUIDES / "ko_kr" / destination
        output_path = OUTPUT_ASSETS / destination
        if not source_path.is_file() or not target_path.is_file():
            errors.append(f"안내서 작업본 누락: {destination}")
            continue
        source, target = load(source_path), load(target_path)
        errors.extend(validate_guide(source, target, destination))
        if not output_path.is_file() or load(output_path) != target:
            errors.append(f"안내서 누적 출력 불일치: {destination}")
        guide_rows.append(destination)
    result = {
        "scopes": rows,
        "guides": guide_rows,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write(ROOT / "specialized_validation.json", result)
    return result, errors


def audit() -> tuple[dict[str, object], list[str]]:
    instance = resolve_source_root()
    jar = family_goal.find_jar(instance, "iceandfire-")
    with ZipFile(jar) as archive:
        names = archive.namelist()
        advancements = sum(n.endswith(".json") and "/advancement" in n for n in names)
        recipes = sum(n.endswith(".json") and "/recipe" in n for n in names)
    visible_lines = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json", ".snbt"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            lowered = line.lower()
            if (
                "iceandfire:" in lowered
                and any(
                    token in lowered
                    for token in ("name", "display", "tooltip", "lore", "text")
                )
                and not re.search(r'"name"\s*:\s*"iceandfire:[^"]+"', lowered)
            ):
                visible_lines.append(
                    f"{path.relative_to(instance).as_posix()}:{number}:{line.strip()}"
                )
    result = {
        "jar": jar.name,
        "advancements": advancements,
        "recipes": recipes,
        "guide_files_translated": len(GUIDE_TRANSLATIONS),
        "kubejs_direct_display_lines": visible_lines,
        "status": "complete",
    }
    write(ROOT / "surface_audit.json", result)
    return result, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("refresh-quests", "normalize", "verify", "audit")
    )
    args = parser.parse_args()
    if args.command == "refresh-quests":
        report, errors = refresh_quests(), []
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
