#!/usr/bin/env python3
"""Aquaculture 2와 Sushi Go Crafting의 표시 문자열을 번역하고 검증해요."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "aquaculture_sushi"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
RESOURCEPACK_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean"
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
BOOK_OUTPUT = (
    PROJECT_ROOT
    / "output/overrides/kubejs/data/sushigocrafting/patchouli_books"
    / "sushigocrafting/book.json"
)
GUIDE_SOURCE_ROOT = "assets/sushigocrafting/patchouli_books/sushigocrafting/en_us"
GUIDE_OUTPUT_ROOT = (
    RESOURCEPACK_ROOT / "assets/sushigocrafting/patchouli_books/sushigocrafting/ko_kr"
)
BOOK_SOURCE = "data/sushigocrafting/patchouli_books/sushigocrafting/book.json"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[.]\d+)?")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
VISIBLE_FIELDS = {"name", "description", "text", "title", "landing_text"}

NAMESPACES = {
    "aquaculture": "Aquaculture-*.jar",
    "sushigocrafting": "sushigocrafting-*.jar",
}

AQUA_OVERRIDES = {
    "tabs.aquaculture.tab": "Aquaculture 2",
    "_comment": "EMI 지원",
    "block.aquaculture.neptunium_block": "넵투늄 블록",
    "block.aquaculture.neptunes_bounty": "넵튠의 보물",
    "block.aquaculture.tackle_box": "낚시 도구 상자",
    "block.aquaculture.worm_farm": "지렁이 농장",
    "item.aquaculture.fish_fillet_raw": "생생선 필레",
    "item.aquaculture.fish_fillet_cooked": "익힌 생선 필레",
    "item.aquaculture.turtle_soup": "거북이 수프",
    "item.aquaculture.tin_can": "깡통",
    "item.aquaculture.fish_bones": "생선 뼈",
    "item.aquaculture.message_in_a_bottle": "병 속의 편지",
    "item.aquaculture.box": "나무 상자",
    "item.aquaculture.lockbox": "잠금 상자",
    "item.aquaculture.treasure_chest": "보물 상자",
    "item.aquaculture.neptunium_leggings": "넵투늄 각반",
    "entity.aquaculture.bobber": "Aquaculture 찌",
    "entity.aquaculture.water_arrow": "화살",
    "aquaculture.fishWeight.weight": "무게: %s",
    "aquaculture.fishWeight.juvenile": "어린 개체",
    "aquaculture.fishWeight.small": "소형",
    "aquaculture.fishWeight.large": "대형",
    "aquaculture.fishWeight.massive": "초대형",
    "aquaculture.fishing_rod.broken": "부서짐",
    "aquaculture.shift": "[SHIFT]",
    "aquaculture.unbreakable": "파괴 불가",
    "aquaculture.universal": "범용",
    "aquaculture.loot.open": "획득",
}

FILLET_KNIVES = {
    "wooden": "나무 생선 손질칼",
    "stone": "돌 생선 손질칼",
    "iron": "철 생선 손질칼",
    "gold": "금 생선 손질칼",
    "diamond": "다이아몬드 생선 손질칼",
    "neptunium": "넵투늄 생선 손질칼",
}

HOOK_NAMES = {
    "iron": "철 낚싯바늘",
    "gold": "금 낚싯바늘",
    "diamond": "다이아몬드 낚싯바늘",
    "light": "가벼운 낚싯바늘",
    "heavy": "무거운 낚싯바늘",
    "double": "이중 낚싯바늘",
    "redstone": "레드스톤 낚싯바늘",
    "note": "소리 낚싯바늘",
    "double_obsidian": "이중 흑요석 낚싯바늘",
    "obsidian": "흑요석 낚싯바늘",
    "obsidian_note": "흑요석 소리 낚싯바늘",
    "glowstone": "발광석 낚싯바늘",
    "nether_star": "네더의 별 낚싯바늘",
    "quartz": "석영 낚싯바늘",
    "soul_sand": "영혼 모래 낚싯바늘",
}

FISH_NAMES = {
    "atlantic_cod": "대서양 대구",
    "blackfish": "블랙피시",
    "pacific_halibut": "태평양 넙치",
    "atlantic_halibut": "대서양 넙치",
    "atlantic_herring": "대서양 청어",
    "pink_salmon": "곱사연어",
    "pollock": "명태",
    "rainbow_trout": "무지개송어",
    "bayad": "바야드",
    "boulti": "볼티",
    "capitaine": "카피테인",
    "synodontis": "시노돈티스",
    "smallmouth_bass": "작은입배스",
    "bluegill": "블루길",
    "brown_trout": "갈색송어",
    "carp": "잉어",
    "catfish": "메기",
    "gar": "가아",
    "minnow": "피라미",
    "muskellunge": "머스켈런지",
    "perch": "퍼치",
    "arapaima": "아라파이마",
    "piranha": "피라냐",
    "tambaqui": "탐바키",
    "brown_shrooma": "갈색 슈루마",
    "red_shrooma": "붉은 슈루마",
    "jellyfish": "해파리",
    "red_grouper": "붉바리",
    "tuna": "참치",
}

TURTLE_NAMES = {
    "box_turtle": "상자거북",
    "arrau_turtle": "아라우거북",
    "starshell_turtle": "별껍질거북",
}

WOOD_NAMES = {
    "oak": "참나무",
    "spruce": "가문비나무",
    "birch": "자작나무",
    "jungle": "정글나무",
    "acacia": "아카시아나무",
    "dark_oak": "짙은 참나무",
}

AQUA_MESSAGES = {
    1: "물고기는 어떻게 캐는 거지?",
    2: "의사가 감정을 병에 담아 두라고 했어.",
    3: "도와주세요! 병 속의 편지 공장에 갇혔어요!",
    4: "누가 우리 집을 망가뜨렸어요. 보급품을 보내 주세요!",
    5: "이봐요! 여기예요! 당신이 보여요!",
    6: "하하, 이제 쓰레기를 버린 건 바로 너야!",
    7: "크리퍼-콜라 소유.",
    8: "경고: 질식 위험. 어린이의 손이 닿지 않는 곳에 두세요.",
    9: "이걸 받았다면 미래의 네가 보내는 거야. 돼지고기는 절대 먹지 마.",
    10: "데이비 존스의 궤짝 입장권 한 장.",
    11: "9.17 N 19.89 E",
    12: "넵투나이트는 진짜야! 지어낸 이야기가 아니라니까!",
    13: "단돈 금 19.95개로 낚싯대를 키워 드립니다! 보장합니다!",
    14: "Fishallurgy가 대체 뭐지? 물고기에 생기는 반응 같은 건가?",
    15: "고래 버거! 빵 2개 + 고래 스테이크! 기억나죠!?",
    16: (
        "뭍에 오른 뒤로 모든 게 예전 같지 않아. 해변에 발을 딛는 순간 게임에서 "
        "완전히 져 버렸거든.."
    ),
    17: "Alt-F4를 누르면 다이아몬드를 공짜로 드립니다!",
    18: "오, 내겐 사랑스러운 코코넛 한 무더기가 있지..",
    19: "새로운 사람을 고기로 만나려고 식인종 부족에 가입했어.",
    20: "활동할 공간이 정말 많아!",
    21: (
        "Shadowclaimer 님, 즉시 채굴 도구와 무적 방어구로 쓸 수 있는 Unobtainium "
        "Hyper Diamonds를 추가해 주세요. 모두가 드림."
    ),
    22: "Shadowclaimer 님, 그래서 1.X는 언제 나오나요? 모두가 드림.",
    23: "팬 여러분, 안녕하세요! Shadowclaimer가 드림.",
    24: "참치 우주는 정말 놀라운 곳이야.",
    25: "Null Pointer Exception: Aquaculture.MessageInABottle (String) cannot be null.",
    26: "나는 매일 아침 다이아몬드 갑옷을 갈아 먹는다. - mDiyo",
    27: "-편지가 손안에서 마법처럼 사라집니다.-",
    28: (
        "나를 보세요. 이제 인벤토리를 보고, 다시 나를 보세요. 이 편지는 이제 "
        "다이아몬드입니다! 농담이에요. 아직 종이예요."
    ),
    29: "황동 5개로 재활용하세요.",
}

AQUA_TOOLTIPS = {
    "aquaculture.neptunium_fishing_rod.tooltip.title": "넵튠의 노래",
    "aquaculture.neptunium_fishing_rod.tooltip.desc": "물고기가 더 잘 미끼를 뭅니다",
    "aquaculture.neptunium_helmet.tooltip.title": "넵튠의 시야",
    "aquaculture.neptunium_helmet.tooltip.desc": "수중 시야가 개선됩니다",
    "aquaculture.neptunium_chestplate.tooltip.title": "넵튠의 허파",
    "aquaculture.neptunium_chestplate.tooltip.desc": "물속에서 숨을 쉴 수 있습니다",
    "aquaculture.neptunium_leggings.tooltip.title": "넵튠의 부력",
    "aquaculture.neptunium_leggings.tooltip.desc": "물속에서 무중력 상태가 됩니다",
    "aquaculture.neptunium_boots.tooltip.title": "넵튠의 신속",
    "aquaculture.neptunium_boots.tooltip.desc": "수영 속도가 증가합니다",
    "aquaculture.neptunium_pickaxe.tooltip.title": "넵튠의 은총",
    "aquaculture.neptunium_pickaxe.tooltip.desc": "물속에서도 채굴 속도가 느려지지 않습니다",
    "aquaculture.neptunium_axe.tooltip.title": "넵튠의 힘",
    "aquaculture.neptunium_axe.tooltip.desc": "물속의 적에게 주는 피해가 증가합니다",
    "aquaculture.neptunium_hoe.tooltip.title": "넵튠의 선물",
    "aquaculture.neptunium_hoe.tooltip.desc": "간 농지가 계속 촉촉하게 유지됩니다",
    "aquaculture.neptunium_shovel.tooltip.title": "넵튠의 은총",
    "aquaculture.neptunium_shovel.tooltip.desc": "물속에서도 채굴 속도가 느려지지 않습니다",
    "aquaculture.neptunium_sword.tooltip.title": "넵튠의 힘",
    "aquaculture.neptunium_sword.tooltip.desc": "물속의 적에게 주는 피해가 증가합니다",
    "aquaculture.neptunium_bow.tooltip.title": "넵튠의 일격",
    "aquaculture.neptunium_bow.tooltip.desc": "화살이 물속에서도 매끄럽게 날아갑니다",
    "aquaculture.neptunium_fillet_knife.tooltip.title": "넵튠의 만찬",
    "aquaculture.neptunium_fillet_knife.tooltip.desc": "얻는 생선 필레의 양이 늘어납니다",
    "aquaculture.iron_hook.tooltip.title": "튼튼함",
    "aquaculture.iron_hook.tooltip.desc": "20% 확률로 내구도를 소모하지 않습니다",
    "aquaculture.gold_hook.tooltip.title": "행운",
    "aquaculture.gold_hook.tooltip.desc": "행운이 증가합니다",
    "aquaculture.diamond_hook.tooltip.title": "매우 튼튼함",
    "aquaculture.diamond_hook.tooltip.desc": "50% 확률로 내구도를 소모하지 않습니다",
    "aquaculture.light_hook.tooltip.title": "가벼움",
    "aquaculture.light_hook.tooltip.desc": "낚싯줄을 더 멀리 던집니다",
    "aquaculture.heavy_hook.tooltip.title": "무거움",
    "aquaculture.heavy_hook.tooltip.desc": "낚싯줄을 더 가까이 던집니다",
    "aquaculture.double_hook.tooltip.title": "이중 미늘",
    "aquaculture.double_hook.tooltip.desc": "한 번에 두 가지를 낚을 수 있습니다",
    "aquaculture.redstone_hook.tooltip.title": "유인",
    "aquaculture.redstone_hook.tooltip.desc": "물고기를 낚아챌 수 있는 시간이 늘어납니다",
    "aquaculture.note_hook.tooltip.title": "알림",
    "aquaculture.note_hook.tooltip.desc": "물고기가 다가오면 알림음을 재생합니다",
    "aquaculture.nether_star_hook.tooltip.title": "초월적",
    "aquaculture.nether_star_hook.tooltip.desc": (
        "50% 확률로 내구도를 소모하지 않으며 행운이 증가합니다"
    ),
    "aquaculture.double_obsidian_hook.tooltip.title": "이중 미늘",
    "aquaculture.double_obsidian_hook.tooltip.desc": "한 번에 두 가지를 낚을 수 있습니다",
    "aquaculture.glowstone_hook.tooltip.title": "행운",
    "aquaculture.glowstone_hook.tooltip.desc": "행운이 증가합니다",
    "aquaculture.quartz_hook.tooltip.title": "튼튼함",
    "aquaculture.quartz_hook.tooltip.desc": "30% 확률로 내구도를 소모하지 않습니다",
    "aquaculture.soul_sand_hook.tooltip.title": "유인",
    "aquaculture.soul_sand_hook.tooltip.desc": "물고기를 낚아챌 수 있는 시간이 늘어납니다",
    "aquaculture.obsidian_note_hook.tooltip.title": "알림",
    "aquaculture.obsidian_note_hook.tooltip.desc": "물고기가 다가오면 알림음을 재생합니다",
}

AQUA_SUBTITLES = {
    "aquaculture.subtitles.tackle_box_open": "낚시 도구 상자가 열림",
    "aquaculture.subtitles.tackle_box_close": "낚시 도구 상자가 닫힘",
    "aquaculture.subtitles.worm_farm_empty": "지렁이 농장이 비워짐",
    "aquaculture.subtitles.fish_mount_removed": "물고기 장식대에서 물고기가 빠짐",
    "aquaculture.subtitles.fish_mount_broken": "물고기 장식대가 부서짐",
    "aquaculture.subtitles.fish_mount_placed": "물고기 장식대가 설치됨",
    "aquaculture.subtitles.fish_mount_add_item": "물고기가 장식대에 걸림",
    "aquaculture.subtitles.bobber_bait": "미끼가 다 떨어짐",
    "aquaculture.subtitles.bobber_note_catch": "물고기가 낚싯바늘에 다가옴",
    "aquaculture.subtitles.bobber_land_lava": "낚싯바늘이 용암에 떨어짐",
    "aquaculture.subtitles.jellyfish_flop": "해파리가 퍼덕임",
    "aquaculture.subtitles.fish_ambient": "물고기가 헤엄침",
    "aquaculture.subtitles.fish_death": "물고기가 죽음",
    "aquaculture.subtitles.fish_flop": "물고기가 퍼덕임",
    "aquaculture.subtitles.fish_hurt": "물고기가 다침",
    "aquaculture.subtitles.fish_collide": "물고기가 부딪힘",
    "aquaculture.subtitles.bottle_open": "병이 깨짐",
}

AQUA_TAGS = {
    "tag.item.aquaculture.bobber": "찌",
    "tag.item.aquaculture.fish_mount": "물고기 장식대",
    "tag.item.aquaculture.fishing_line": "낚싯줄",
    "tag.item.aquaculture.hook": "낚싯바늘",
    "tag.item.aquaculture.tackle_box": "낚시 도구 상자",
    "tag.item.aquaculture.tackle_box_green": "초록색 낚시 도구 상자 염료",
    "tag.item.aquaculture.turtle": "거북",
    "tag.item.aquaculture.turtle_edible": "식용 거북",
    "tag.item.c.ingots.neptunium": "넵투늄 주괴",
    "tag.item.c.nuggets.neptunium": "넵투늄 조각",
    "tag.item.c.storage_blocks.neptunium": "넵투늄 저장 블록",
    "tag.item.c.tools.knife": "칼",
}

SUSHI_STATIC = {
    "block.sushigocrafting.avocado_leaves": "아보카도 잎",
    "block.sushigocrafting.avocado_leaves_logged": "아보카도 잎 달린 원목",
    "block.sushigocrafting.avocado_log": "아보카도 원목",
    "block.sushigocrafting.avocado_sapling": "아보카도 묘목",
    "block.sushigocrafting.cooler_box": "냉장 상자",
    "block.sushigocrafting.cucumber_crop": "오이 씨앗",
    "block.sushigocrafting.cutting_board": "도마",
    "block.sushigocrafting.fermentation_barrel": "발효 통",
    "block.sushigocrafting.rice_cooker": "밥솥",
    "block.sushigocrafting.rice_crop": "쌀 씨앗",
    "block.sushigocrafting.roller": "김발",
    "block.sushigocrafting.sesame_crop": "참깨 씨앗",
    "block.sushigocrafting.soy_crop": "대두 씨앗",
    "block.sushigocrafting.wasabi_crop": "와사비 씨앗",
    "effect.sushigocrafting.acquired_taste": "익숙해진 맛",
    "effect.sushigocrafting.acquired_taste.description": (
        "음식을 먹을 때 영양과 포만도가 추가로 증가합니다"
    ),
    "effect.sushigocrafting.small_bites": "한입 크기",
    "effect.sushigocrafting.small_bites.description": (
        "먹던 음식을 돌려받을 수 있는 확률이 생깁니다"
    ),
    "effect.sushigocrafting.steady_hands": "정교한 손놀림",
    "effect.sushigocrafting.steady_hands.description": (
        "도마에서 재료를 손질할 때 얻는 양이 증가합니다"
    ),
    "entity.sushigocrafting.shrimp": "새우",
    "entity.sushigocrafting.tuna": "참치",
    "item.sushigocrafting.avocado": "아보카도",
    "item.sushigocrafting.avocado_maki": "아보카도 마키",
    "item.sushigocrafting.avocado_slices": "아보카도 조각",
    "item.sushigocrafting.cheese": "치즈",
    "item.sushigocrafting.chicken_temaki": "닭고기 테마키",
    "item.sushigocrafting.cleaver_knife": "중식도",
    "item.sushigocrafting.cooked_rice": "익힌 쌀",
    "item.sushigocrafting.crab_maki": "게맛살 마키",
    "item.sushigocrafting.cucumber": "오이",
    "item.sushigocrafting.cucumber_maki": "오이 마키",
    "item.sushigocrafting.cucumber_slices": "오이 조각",
    "item.sushigocrafting.imitation_crab": "게맛살",
    "item.sushigocrafting.nori_sheets": "김",
    "item.sushigocrafting.onigiri": "오니기리",
    "item.sushigocrafting.raw_tuna": "생참치",
    "item.sushigocrafting.rice": "쌀",
    "item.sushigocrafting.salmon_fillet": "연어 필레",
    "item.sushigocrafting.salmon_gunkan": "연어 군함말이",
    "item.sushigocrafting.salmon_maki": "연어 마키",
    "item.sushigocrafting.salmon_nigiri": "연어 니기리",
    "item.sushigocrafting.salmon_temaki": "연어 테마키",
    "item.sushigocrafting.seaweed_on_a_stick": "막대기에 꽂은 해초",
    "item.sushigocrafting.sesame_seed": "참깨",
    "item.sushigocrafting.shrimp": "새우",
    "item.sushigocrafting.shrimp_bucket": "새우가 든 양동이",
    "item.sushigocrafting.shrimp_nigiri": "새우 니기리",
    "item.sushigocrafting.shrimp_temaki": "새우 테마키",
    "item.sushigocrafting.soy_bean": "대두",
    "item.sushigocrafting.soy_sauce": "간장",
    "item.sushigocrafting.tobiko": "날치알",
    "item.sushigocrafting.tuna_bucket": "참치가 든 양동이",
    "item.sushigocrafting.tuna_fillet": "참치 필레",
    "item.sushigocrafting.tuna_gunkan": "참치 군함말이",
    "item.sushigocrafting.tuna_maki": "참치 마키",
    "item.sushigocrafting.tuna_nigiri": "참치 니기리",
    "item.sushigocrafting.tuna_temaki": "참치 테마키",
    "item.sushigocrafting.wakame_gunkan": "미역 군함말이",
    "item.sushigocrafting.wasabi_paste": "와사비 페이스트",
    "item.sushigocrafting.wasabi_root": "와사비 뿌리",
    "itemGroup.sushigocrafting": "Sushi Go Crafting",
    "text.sushigocrafting.add_food_effect": "음식 효과 추가",
    "text.sushigocrafting.almost_hollow": "거의 속이 빔",
    "text.sushigocrafting.amount": "양",
    "text.sushigocrafting.book.title": "이타마에 되기(Sushi Go Crafting 안내서)",
    "text.sushigocrafting.button": "버튼",
    "text.sushigocrafting.consumes": "소비함",
    "text.sushigocrafting.discovered_a": "발견:",
    "text.sushigocrafting.effects": "효과",
    "text.sushigocrafting.food_ingredients": "음식 재료",
    "text.sushigocrafting.hold": "누르기",
    "text.sushigocrafting.hunger": "허기",
    "text.sushigocrafting.increase_level_by": "효과 단계 증가량",
    "text.sushigocrafting.left_click_increase": "좌클릭하여 증가",
    "text.sushigocrafting.list_ingredients": "Sushi Go Crafting 음식 재료를 모두 표시",
    "text.sushigocrafting.list_oof_ingredients": "알려진 음식 재료 목록",
    "text.sushigocrafting.make_64": "우클릭하여 64개 만들기",
    "text.sushigocrafting.make_one": "좌클릭하여 1개 만들기",
    "text.sushigocrafting.modify_food_effect": "음식 효과 변경",
    "text.sushigocrafting.multiply_time_by": "지속 시간 배율",
    "text.sushigocrafting.overflowing": "넘침",
    "text.sushigocrafting.perfect": "완벽함",
    "text.sushigocrafting.perfect_weight": "새로운 완벽한 무게!",
    "text.sushigocrafting.right_click_decrease": "우클릭하여 감소",
    "text.sushigocrafting.roll": "말기",
    "text.sushigocrafting.saturation": "포만도",
    "text.sushigocrafting.sushi_effect": " 초밥 효과에 적용",
    "text.sushigocrafting.weight": "무게",
    "text.sushigocrafting.weirdly_balanced": "묘하게 균형 잡힘",
}

CALIFORNIA_NAMES = {
    "crab": "게맛살",
    "salmon": "연어",
    "tuna": "참치",
}

GUIDE_TEXT = {
    "Using your tools": "도구 사용법",
    "Your hands are your best tool": "손은 가장 좋은 도구입니다",
    "Getting Started": "시작하기",
    "How to get basic stuff": "기본 재료를 구하는 방법",
    "World": "월드",
    "What is out there?": "월드에는 무엇이 있을까요?",
    "Avocado": "아보카도",
    (
        "You can find Avocado trees in the world, mostly in plains. $(br2)You can "
        "harvest the avocado from the leaves by Right Click them when it's fully grown."
    ): (
        "월드의 평원에서 주로 아보카도나무를 찾을 수 있습니다. $(br2)열매가 완전히 "
        "자란 잎을 우클릭하면 아보카도를 수확할 수 있습니다."
    ),
    "Tobiko": "날치알",
    "You can get Tobiko from killing fishes.": "물고기를 처치하면 날치알을 얻을 수 있습니다.",
    "Seaweed": "해초",
    "You can find Seaweed in Oceans.": "바다에서 해초를 찾을 수 있습니다.",
    "Tuna and Shrimp": "참치와 새우",
    (
        "You can find those adorable creatures in the Ocean. $(br2)Bring a saddle, who "
        "knows what you can do with it."
    ): (
        "바다에서 이 귀여운 생물들을 찾을 수 있습니다. $(br2)안장을 가져가 보세요. "
        "어디에 쓸 수 있을지는 직접 확인해 보세요."
    ),
    "Crops": "작물",
    (
        "You can get seeds by breaking grass. $(br2)Most of the crops are grown like "
        "normal crops except Rice that needs to be grown underwater on dirt."
    ): (
        "풀을 부수면 씨앗을 얻을 수 있습니다. $(br2)대부분은 일반 작물처럼 자라지만, "
        "쌀은 물속의 흙에서 재배해야 합니다."
    ),
    "Cooler Box": "냉장 상자",
    (
        "A handy box used to combine automatically ingredients that have weight, just "
        "place them inside and they will be combined."
    ): (
        "무게가 있는 재료를 자동으로 합치는 편리한 상자입니다. 재료를 안에 넣으면 "
        "알아서 합쳐집니다."
    ),
    "Cutting Board": "도마",
    (
        "Chopping your ingredients is an important step for cooking, you can place your "
        "ingredients by right clicking the Cutting Board and right clicking with a "
        "$(6)Cleaver Knife$() those ingredients will get chopped up. $(br)To remove "
        "ingredients Sneak + Right Click the cutting board. $(br2)$(l:getting_started/"
        "effects)Steady Hands$() will be your friends when using the cutting boards."
    ): (
        "재료 손질은 요리의 중요한 단계입니다. 도마를 우클릭해 재료를 올린 뒤 "
        "$(6)중식도$()로 다시 우클릭하면 재료를 썰 수 있습니다. $(br)재료를 빼려면 "
        "웅크린 채 도마를 우클릭하세요. $(br2)도마를 사용할 때는 "
        "$(l:getting_started/effects)정교한 손놀림$() 효과가 도움이 됩니다."
    ),
    "Rice Cooker": "밥솥",
    (
        "A machine used to cook rice perfectly to $(6)Uncle Roger$() standards. To cook "
        "it you will need Rice, Water and some fuel to cook it up. $(br2)You won't have "
        "to worry about the weights in the output slot, Cooked Rice will be combined "
        "automatically."
    ): (
        "$(6)Uncle Roger$()의 기준에 맞게 밥을 완벽히 짓는 기계입니다. 쌀과 물, "
        "연료를 넣어 밥을 지으세요. $(br2)출력 칸의 무게는 걱정하지 않아도 됩니다. "
        "익힌 쌀은 자동으로 합쳐집니다."
    ),
    "Roller": "김발",
    (
        "A Roller is the most important tool when making sushi. To use a Roller properly "
        "and get the best food you will need to experiment with it first. $(br2)Making a "
        "roll will indicate you in the tooltip how far the perfect weight is and making "
        "a perfect roll will provide you with better food values and effects."
    ): (
        "김발은 초밥을 만들 때 가장 중요한 도구입니다. 김발을 제대로 사용해 최고의 "
        "음식을 만들려면 먼저 여러 조합을 시험해 보세요. $(br2)말이를 만들면 완벽한 "
        "무게와 얼마나 차이 나는지 툴팁에 표시되며, 완벽하게 말면 음식 수치와 효과가 "
        "더 좋아집니다."
    ),
    (
        "To use a Roller select what type of Sushi you want, then place in ingredients "
        "in the correct slot, select how much of those ingredients you want to use and "
        "then left click the Roller a bunch of times to get your Sushi. $(br2)You don't "
        "have to remember the perfect weight the Roller will show you already discovered "
        "perfect weights."
    ): (
        "김발에서 만들 초밥 종류를 고르고 알맞은 칸에 재료를 넣으세요. 사용할 재료의 "
        "양을 정한 뒤 김발을 여러 번 좌클릭하면 초밥이 완성됩니다. $(br2)완벽한 무게를 "
        "외울 필요는 없습니다. 이미 알아낸 무게는 김발이 표시해 줍니다."
    ),
    "Eating Effects": "음식 효과",
    (
        "Using different types of ingredients to make a type of sushi will get you "
        "different effects to make your food better"
    ): "같은 초밥도 재료 종류를 바꾸면 음식의 성능을 높이는 서로 다른 효과를 얻습니다.",
    "Small Bites": "한입 크기",
    (
        "Eating when having this potion effect will give you a small chance of not "
        "consuming the item."
    ): "이 효과가 있을 때 음식을 먹으면 낮은 확률로 아이템이 소모되지 않습니다.",
    "Acquired Taste": "익숙해진 맛",
    "Eating when having this potion effect will give extra food.": (
        "이 효과가 있을 때 음식을 먹으면 허기와 포만도를 추가로 회복합니다."
    ),
    "Steady Hands": "정교한 손놀림",
    (
        "Using a cutting board when having this potion effect will give extra weights in "
        "your ingredients."
    ): "이 효과가 있을 때 도마를 사용하면 재료의 무게가 더 늘어납니다.",
    "Ingredients": "재료",
    (
        "Ingredients are 'usually' processed food ready to used when making food, most "
        "of them will have a weight to them and their weights can be combined in the "
        "crafting table or in a $(l:using_tools/cooler_box)Cooler Box$() to do it in "
        "automated way. $(br2)If ingredients don't combine it might be because it goes "
        "over the max amount."
    ): (
        "재료는 보통 요리에 바로 쓸 수 있게 가공한 음식입니다. 대부분 무게가 있으며, "
        "제작대에서 합치거나 $(l:using_tools/cooler_box)냉장 상자$()로 자동 합칠 수 "
        "있습니다. $(br2)재료가 합쳐지지 않는다면 최대치보다 무거워졌기 때문일 수 "
        "있습니다."
    ),
    (
        "Most ingredients have an affect attached to them or an effect modifier that "
        "will modify/amplify effects from other ingredients."
    ): (
        "대부분의 재료에는 고유 효과나 효과 조정값이 있어 다른 재료의 효과를 변경하거나 "
        "강화합니다."
    ),
    "Nori": "김",
    (
        "To get Nori Sheets you will need to find some Kelp in the oceans and make a "
        "Dried Kelp Block with it. $(br2)Squishing a Dried Kelp Block (dropped as an "
        "item) between an Iron Block with a piston will get you some Nori Sheets."
    ): (
        "김을 만들려면 바다에서 다시마를 구해 말린 다시마 블록으로 만드세요. "
        "$(br2)아이템 상태의 말린 다시마 블록을 피스톤으로 철 블록에 눌러 붙이면 김을 "
        "얻을 수 있습니다."
    ),
    "Nori Piston Crafting": "피스톤으로 김 만들기",
}

BOOK_LANDING = (
    "초밥을 깊이 있게 다루는 음식 모드 Sushi Go Crafting에 오신 것을 환영합니다! "
    "$(br2)개발자를 후원하려면 $(l:https://www.patreon.com/buuz135)여기$()를 누르세요."
)

QUEST_CORRECTIONS = {
    "quest.0C82CE3AFBD48C1E.quest_desc": [
        "&l&aSushi Go Crafting&r은 블록을 많이 추가하지는 않지만, 추가되는 블록은 "
        "주방에서 꼭 사용해 볼 만합니다! \\n\\n특히 밥솥이 있으면 이제 쌀을 전자레인지로 "
        "익힐 필요가 없습니다."
    ],
    "quest.0C82CE3AFBD48C1E.title": "&l&aSushi Go Crafting&r",
    "task.53A6720343E57302.title": "Sushi Go Crafting",
    "quest.3416DB9F58D8AA2C.quest_desc": [
        "&3넵투늄&r은 낚시로 얻는 넵튠의 보물에서 나옵니다! \\n넵투늄 장비는 "
        "물속에서 유용한 강화 효과도 제공합니다."
    ],
}

RELATED_QUEST_IDS = {
    "01046CFBD7411AA6",
    "0A64D0937A5F7513",
    "0C82CE3AFBD48C1E",
    "12449D23295CF9ED",
    "16D0F1E3CEB60ABF",
    "3416DB9F58D8AA2C",
    "511562EA5811306B",
    "53A6720343E57302",
    "5A1DCD6C7F712A78",
    "7BCE96070C36D547",
}

INTENTIONAL_SAME = {
    "aquaculture": {
        "aquaculture.message11",
        "aquaculture.message25",
        "aquaculture.shift",
    },
    "sushigocrafting": {"itemGroup.sushigocrafting"},
}

ALLOWED_LATIN = {
    "Alt",
    "Aquaculture",
    "Crafting",
    "Diamonds",
    "EMI",
    "Fishallurgy",
    "Hyper",
    "MessageInABottle",
    "Null",
    "Pointer",
    "SHIFT",
    "Shadowclaimer",
    "String",
    "Sushi",
    "Uncle",
    "Unobtainium",
    "mDiyo",
    "null",
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽어요."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 객체가 아니에요: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 안정된 형식으로 써요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    """파일 SHA-256을 계산해요."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_jar(instance: Path, pattern: str) -> Path:
    """현재 인스턴스의 유일한 대상 JAR을 찾아요."""
    matches = sorted((instance / "mods").glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"JAR 수가 1개가 아니에요: {pattern} -> {matches}")
    return matches[0]


def read_jar_json(jar: Path, internal: str) -> dict[str, object]:
    """JAR을 ZIP으로 읽고 JSON 객체를 반환해요."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read(internal))
    if not isinstance(value, dict):
        raise TypeError(f"JAR JSON 객체가 아니에요: {jar.name}!/{internal}")
    return value


def read_jar_language(jar: Path, namespace: str, locale: str) -> dict[str, object]:
    """JAR 언어 파일을 읽어요."""
    return read_jar_json(jar, f"assets/{namespace}/lang/{locale}.json")


def korean_particle(name: str) -> str:
    """이름 끝 음절에 맞춰 '이/가'를 골라요."""
    last = name[-1]
    if "가" <= last <= "힣" and (ord(last) - ord("가")) % 28:
        return "이"
    return "가"


def aquaculture_translations(
    english: dict[str, object], candidate: dict[str, object]
) -> dict[str, object]:
    """현재 후보 전체를 원문과 대조한 Aquaculture 2 번역을 만들어요."""
    translated = dict(candidate)
    translated.update(AQUA_OVERRIDES)
    for material, value in FILLET_KNIVES.items():
        translated[f"item.aquaculture.{material}_fillet_knife"] = value
    for material, value in HOOK_NAMES.items():
        translated[f"item.aquaculture.{material}_hook"] = value
    for identifier, name in FISH_NAMES.items():
        translated[f"item.aquaculture.{identifier}"] = name
        translated[f"entity.aquaculture.{identifier}"] = name
        bucket_key = f"item.aquaculture.{identifier}_bucket"
        if bucket_key in english:
            translated[bucket_key] = f"{name}{korean_particle(name)} 든 양동이"
    for identifier, name in TURTLE_NAMES.items():
        translated[f"item.aquaculture.{identifier}"] = name
        translated[f"item.aquaculture.{identifier}_spawn_egg"] = f"{name} 생성 알"
        translated[f"entity.aquaculture.{identifier}"] = name
    for wood, name in WOOD_NAMES.items():
        value = f"{name} 물고기 장식대"
        translated[f"item.aquaculture.{wood}_fish_mount"] = value
        translated[f"entity.aquaculture.{wood}_fish_mount"] = value
    for number, value in AQUA_MESSAGES.items():
        translated[f"aquaculture.message{number}"] = value
    translated.update(AQUA_TOOLTIPS)
    translated.update(AQUA_SUBTITLES)
    translated.update(AQUA_TAGS)
    missing = sorted(set(english) - set(translated))
    extra = sorted(set(translated) - set(english))
    if missing or extra:
        raise ValueError(f"Aquaculture 2 번역 키 불일치: 누락={missing}, 초과={extra}")
    return {key: translated[key] for key in english}


def sushi_translations(english: dict[str, object]) -> dict[str, object]:
    """Sushi Go Crafting 전체 언어 번역을 만들어요."""
    translated = dict(SUSHI_STATIC)
    for protein, name in CALIFORNIA_NAMES.items():
        translated[f"item.sushigocrafting.{protein}_california"] = (
            f"{name} 캘리포니아 롤"
        )
        translated[f"item.sushigocrafting.{protein}_cheese_california"] = (
            f"{name} 치즈 캘리포니아 롤"
        )
        translated[f"item.sushigocrafting.{protein}_cucumber_california"] = (
            f"{name} 오이 캘리포니아 롤"
        )
        translated[f"item.sushigocrafting.tobiko_{protein}_california"] = (
            f"날치알 {name} 캘리포니아 롤"
        )
        translated[f"item.sushigocrafting.tobiko_{protein}_cheese_california"] = (
            f"날치알 {name} 치즈 캘리포니아 롤"
        )
        translated[f"item.sushigocrafting.tobiko_{protein}_cucumber_california"] = (
            f"날치알 {name} 오이 캘리포니아 롤"
        )
    missing = sorted(set(english) - set(translated))
    extra = sorted(set(translated) - set(english))
    if missing or extra:
        raise ValueError(
            f"Sushi Go Crafting 번역 키 불일치: 누락={missing}, 초과={extra}"
        )
    return {key: translated[key] for key in english}


def translated_guide_value(
    value: object, path: str, seen: list[dict[str, str]]
) -> object:
    """가이드의 사용자 표시 필드만 번역해요."""
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in VISIBLE_FIELDS and isinstance(child, str) and child:
                if child not in GUIDE_TEXT:
                    raise KeyError(f"가이드 번역이 없어요: {child_path} -> {child}")
                result[key] = GUIDE_TEXT[child]
                seen.append(
                    {"path": child_path, "source": child, "target": result[key]}
                )
            else:
                result[key] = translated_guide_value(child, child_path, seen)
        return result
    if isinstance(value, list):
        return [
            translated_guide_value(child, f"{path}[{index}]", seen)
            for index, child in enumerate(value)
        ]
    return value


def prepare() -> dict[str, object]:
    """현재 JAR 원문과 후보를 작업 폴더에 기록해요."""
    instance = resolve_source_root()
    rows = []
    total = 0
    for namespace, pattern in NAMESPACES.items():
        jar = source_jar(instance, pattern)
        english = read_jar_language(jar, namespace, "en_us")
        target = WORK_ROOT / namespace
        write_json(target / "en_us.json", english)
        candidate_path = f"assets/{namespace}/lang/ko_kr.json"
        with ZipFile(jar) as archive:
            has_candidate = candidate_path in archive.namelist()
            candidate = (
                json.loads(archive.read(candidate_path)) if has_candidate else {}
            )
        if has_candidate:
            write_json(target / "bundled_ko_kr.json", candidate)
        rows.append(
            {
                "namespace": namespace,
                "jar": jar.name,
                "jar_size": jar.stat().st_size,
                "jar_mtime_ns": jar.stat().st_mtime_ns,
                "english_keys": len(english),
                "bundled_korean_keys": len(candidate),
            }
        )
        total += len(english)
    report = {
        "family": FAMILY,
        "namespaces": rows,
        "english_keys": total,
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", report)
    return report


def build() -> dict[str, object]:
    """언어, 가이드와 책 첫 화면 산출물을 만들어요."""
    instance = resolve_source_root()
    aqua_en = load_json(WORK_ROOT / "aquaculture/en_us.json")
    aqua_candidate = load_json(WORK_ROOT / "aquaculture/bundled_ko_kr.json")
    aqua_ko = aquaculture_translations(aqua_en, aqua_candidate)
    sushi_en = load_json(WORK_ROOT / "sushigocrafting/en_us.json")
    sushi_ko = sushi_translations(sushi_en)
    for namespace, value in (("aquaculture", aqua_ko), ("sushigocrafting", sushi_ko)):
        write_json(WORK_ROOT / namespace / "ko_kr.json", value)
        write_json(RESOURCEPACK_ROOT / f"assets/{namespace}/lang/ko_kr.json", value)

    sushi_jar = source_jar(instance, NAMESPACES["sushigocrafting"])
    guide_rows = []
    guide_strings = []
    with ZipFile(sushi_jar) as archive:
        guide_names = sorted(
            name
            for name in archive.namelist()
            if name.startswith(f"{GUIDE_SOURCE_ROOT}/") and name.endswith(".json")
        )
        for internal in guide_names:
            source = json.loads(archive.read(internal))
            relative = Path(internal).relative_to(GUIDE_SOURCE_ROOT)
            translated = translated_guide_value(
                source, relative.as_posix(), guide_strings
            )
            write_json(WORK_ROOT / "guide/en_us" / relative, source)
            write_json(WORK_ROOT / "guide/ko_kr" / relative, translated)
            write_json(GUIDE_OUTPUT_ROOT / relative, translated)
            guide_rows.append(relative.as_posix())
        book = json.loads(archive.read(BOOK_SOURCE))
    translated_book = deepcopy(book)
    translated_book["landing_text"] = BOOK_LANDING
    write_json(WORK_ROOT / "guide/book_en_us.json", book)
    write_json(WORK_ROOT / "guide/book_ko_kr.json", translated_book)
    write_json(BOOK_OUTPUT, translated_book)
    write_json(WORK_ROOT / "guide/translated_strings.json", guide_strings)

    reused = sum(aqua_ko.get(key) == aqua_candidate.get(key) for key in aqua_en)
    report = {
        "reviewed_language_keys": len(aqua_en) + len(sushi_en),
        "aquaculture_existing_korean_reused": reused,
        "aquaculture_corrected_or_added": len(aqua_en) - reused,
        "sushi_new_language_translations": len(sushi_en),
        "guide_files": len(guide_rows),
        "guide_direct_strings": len(guide_strings),
        "book_landing_strings": 1,
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def direct_visible_values(value: object, path: str = "$") -> list[dict[str, str]]:
    """JSON의 직접 사용자 표시 필드를 찾아요."""
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in VISIBLE_FIELDS and isinstance(child, str) and child:
                found.append({"path": child_path, "value": child})
            else:
                found.extend(direct_visible_values(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(direct_visible_values(child, f"{path}[{index}]"))
    return found


def collect_references(instance: Path) -> dict[str, object]:
    """FTB Quests와 KubeJS의 실제 계열 참조를 모아요."""
    needles = ("aquaculture:", "sushigocrafting:")
    results = {
        "quest_references": [],
        "kubejs_references": [],
        "custom_name_candidates": [],
        "read_errors": [],
    }
    text_suffixes = {
        ".cfg",
        ".js",
        ".json",
        ".kjs",
        ".properties",
        ".snbt",
        ".toml",
        ".txt",
        ".zs",
    }
    for label, root in (
        ("quest_references", instance / "config/ftbquests/quests/chapters"),
        ("kubejs_references", instance / "kubejs"),
    ):
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in text_suffixes:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                results["read_errors"].append(f"{path}: {exc}")
                continue
            relative = path.relative_to(instance).as_posix()
            for number, line in enumerate(text.splitlines(), start=1):
                if any(needle in line for needle in needles):
                    row = f"{relative}:{number}:{line.strip()}"
                    results[label].append(row)
                    if "custom_name" in line.lower():
                        results["custom_name_candidates"].append(row)
    return results


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR 직접 문구와 관련 퀘스트·KubeJS 표시 경로를 감사해요."""
    instance = resolve_source_root()
    errors = []
    jars = []
    for namespace, pattern in NAMESPACES.items():
        jar = source_jar(instance, pattern)
        advancement_files = []
        direct_advancement_text = []
        with ZipFile(jar) as archive:
            for internal in sorted(archive.namelist()):
                if "/advancement/" not in internal or not internal.endswith(".json"):
                    continue
                advancement_files.append(internal)
                value = json.loads(archive.read(internal))
                for row in direct_visible_values(value):
                    direct_advancement_text.append({"file": internal, **row})
        if direct_advancement_text:
            errors.append(f"{namespace} 발전 과제에 직접 표시 문구가 있어요")
        jars.append(
            {
                "namespace": namespace,
                "jar": jar.name,
                "advancement_recipe_files": advancement_files,
                "direct_advancement_text": direct_advancement_text,
            }
        )
    references = collect_references(instance)
    errors.extend(references["read_errors"])
    if references["custom_name_candidates"]:
        errors.append("관련 퀘스트에 custom_name 표시 후보가 있어요")

    english_quests = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean_quests = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    related_keys = sorted(
        key
        for key in english_quests
        if any(identifier in key for identifier in RELATED_QUEST_IDS)
    )
    for key, expected in QUEST_CORRECTIONS.items():
        if korean_quests.get(key) != expected:
            errors.append(f"관련 퀘스트 교정값이 달라요: {key}")
    for key in related_keys:
        if key not in korean_quests:
            errors.append(f"관련 퀘스트 한국어가 없어요: {key}")
            continue
        source_text = json.dumps(english_quests[key], ensure_ascii=False)
        target_text = json.dumps(korean_quests[key], ensure_ascii=False)
        for label, pattern in (("자리표시자", PLACEHOLDER), ("서식 코드", FORMAT_CODE)):
            if Counter(pattern.findall(source_text)) != Counter(
                pattern.findall(target_text)
            ):
                errors.append(f"퀘스트 {label} 보존이 달라요: {key}")
        if Counter(NUMBER.findall(source_text)) != Counter(NUMBER.findall(target_text)):
            errors.append(f"퀘스트 숫자 보존이 달라요: {key}")

    report = {
        "family": FAMILY,
        "jars": jars,
        "references": references,
        "related_quest_keys": related_keys,
        "related_quest_keys_corrected": len(QUEST_CORRECTIONS),
        "related_quest_keys_reviewed_reused": len(related_keys)
        - len(QUEST_CORRECTIONS),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def normalized_format_tokens(value: str) -> Counter[str]:
    """Patchouli 링크 대상은 유지하고 표시 문구 차이는 허용해요."""
    tokens = re.findall(r"\$\([^)]*\)", value)
    normalized = []
    for token in tokens:
        if token.startswith("$(l:"):
            normalized.append(token)
        else:
            normalized.append(token)
    return Counter(normalized)


def verify_guide(instance: Path) -> tuple[dict[str, object], list[str]]:
    """가이드 구조와 Patchouli 서식 보존을 검증해요."""
    jar = source_jar(instance, NAMESPACES["sushigocrafting"])
    errors = []
    files = 0
    strings = 0
    with ZipFile(jar) as archive:
        names = sorted(
            name
            for name in archive.namelist()
            if name.startswith(f"{GUIDE_SOURCE_ROOT}/") and name.endswith(".json")
        )
        for internal in names:
            source = json.loads(archive.read(internal))
            relative = Path(internal).relative_to(GUIDE_SOURCE_ROOT)
            expected_rows = []
            expected = translated_guide_value(
                source, relative.as_posix(), expected_rows
            )
            output = load_json(GUIDE_OUTPUT_ROOT / relative)
            if output != expected:
                errors.append(f"가이드 산출물이 예상과 달라요: {relative.as_posix()}")
            source_values = direct_visible_values(source)
            target_values = direct_visible_values(output)
            if len(source_values) != len(target_values):
                errors.append(f"가이드 표시 문구 수가 달라요: {relative.as_posix()}")
            for source_row, target_row in zip(
                source_values, target_values, strict=True
            ):
                if normalized_format_tokens(
                    source_row["value"]
                ) != normalized_format_tokens(target_row["value"]):
                    errors.append(
                        f"가이드 Patchouli 서식이 달라요: {relative.as_posix()}"
                    )
            files += 1
            strings += len(expected_rows)
        source_book = json.loads(archive.read(BOOK_SOURCE))
    expected_book = deepcopy(source_book)
    expected_book["landing_text"] = BOOK_LANDING
    output_book = load_json(BOOK_OUTPUT)
    if output_book != expected_book:
        errors.append("책 첫 화면 산출물이 예상과 달라요")
    if normalized_format_tokens(
        str(source_book["landing_text"])
    ) != normalized_format_tokens(str(output_book["landing_text"])):
        errors.append("책 첫 화면 Patchouli 서식이 달라요")
    return {
        "files": files,
        "direct_strings": strings,
        "book_landing_strings": 1,
    }, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """현재 JAR과 산출물의 언어·구조·보존 규칙을 검증해요."""
    instance = resolve_source_root()
    audit_report = load_json(WORK_ROOT / "surface_audit.json")
    errors = []
    namespace_reports = []
    total_keys = 0
    reused = 0
    for namespace, pattern in NAMESPACES.items():
        jar = source_jar(instance, pattern)
        jar_english = read_jar_language(jar, namespace, "en_us")
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        output = load_json(RESOURCEPACK_ROOT / f"assets/{namespace}/lang/ko_kr.json")
        current_errors = []
        untranslated = []
        latin_residue = {}
        if jar_english != english:
            current_errors.append("작업 영어가 현재 설치 JAR 영어와 달라요")
        if list(english) != list(korean):
            current_errors.append("한국어 키 또는 순서가 영어 원문과 달라요")
        if korean != output:
            current_errors.append("작업 한국어와 산출물이 달라요")
        for key in english.keys() & korean.keys():
            source = english[key]
            target = korean[key]
            if type(source) is not type(target):
                current_errors.append(f"자료형 불일치: {key}")
                continue
            if not isinstance(source, str) or not isinstance(target, str):
                continue
            for label, pattern in (
                ("자리표시자", PLACEHOLDER),
                ("서식 코드", FORMAT_CODE),
            ):
                if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
                    current_errors.append(f"{label} 불일치: {key}")
            number_exceptions = {"tabs.aquaculture.tab"}
            if (
                Counter(NUMBER.findall(source)) != Counter(NUMBER.findall(target))
                and key not in number_exceptions
            ):
                current_errors.append(f"숫자 불일치: {key}")
            if source.count("\n") != target.count("\n"):
                current_errors.append(f"줄바꿈 불일치: {key}")
            if source == target and key not in INTENTIONAL_SAME[namespace]:
                untranslated.append(key)
            residue = sorted(set(LATIN_WORD.findall(target)) - ALLOWED_LATIN)
            if key == "aquaculture.message25":
                residue = []
            if residue:
                latin_residue[key] = residue
        if untranslated:
            current_errors.append(f"영어와 같은 미번역 후보: {untranslated}")
        if latin_residue:
            current_errors.append(f"허용하지 않은 영문 잔여: {latin_residue}")
        collisions = defaultdict(list)
        for key, target in korean.items():
            if isinstance(target, str) and key.startswith(
                ("item.", "block.", "entity.")
            ):
                collisions[target].append(key)
        unexpected_collisions = {
            target: keys
            for target, keys in collisions.items()
            if len(keys) > 1 and len({english[key] for key in keys}) > 1
        }
        if unexpected_collisions:
            current_errors.append(
                f"서로 다른 이름의 한국어 충돌: {unexpected_collisions}"
            )
        current_reused = 0
        if namespace == "aquaculture":
            candidate = load_json(WORK_ROOT / namespace / "bundled_ko_kr.json")
            current_reused = sum(
                korean.get(key) == candidate.get(key) for key in korean
            )
            reused += current_reused
        namespace_reports.append(
            {
                "namespace": namespace,
                "keys": len(english),
                "existing_korean_reused": current_reused,
                "new_or_corrected": len(english) - current_reused,
                "untranslated_candidates": untranslated,
                "latin_residue": latin_residue,
                "unexpected_name_collisions": unexpected_collisions,
                "errors": current_errors,
            }
        )
        total_keys += len(english)
        errors.extend(f"{namespace}: {message}" for message in current_errors)
    guide_report, guide_errors = verify_guide(instance)
    errors.extend(guide_errors)
    if audit_report.get("status") != "complete":
        errors.append("표시 표면 감사가 완료되지 않았어요")
    report = {
        "family": FAMILY,
        "namespaces": namespace_reports,
        "guide": guide_report,
        "keys": total_keys,
        "existing_korean_reused": reused,
        "new_or_corrected_language_keys": total_keys - reused,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "language_validation.json", report)
    related_keys = audit_report.get("related_quest_keys", [])
    guide_files = sorted(
        "resourcepacks/" + path.relative_to(RESOURCEPACK_ROOT.parent).as_posix()
        for path in GUIDE_OUTPUT_ROOT.rglob("*.json")
    )
    completion = {
        "family": FAMILY,
        "language_keys": total_keys,
        "existing_korean_reused": reused
        + int(audit_report.get("related_quest_keys_reviewed_reused", 0)),
        "new_or_corrected_translations": total_keys
        - reused
        + guide_report["direct_strings"]
        + 1
        + len(QUEST_CORRECTIONS),
        "guide_files": guide_report["files"],
        "guide_direct_strings": guide_report["direct_strings"] + 1,
        "ftbquests": {
            "reviewed_keys": len(related_keys),
            "corrected_keys": len(QUEST_CORRECTIONS),
            "reviewed_reused_keys": audit_report.get(
                "related_quest_keys_reviewed_reused", 0
            ),
        },
        "kubejs_references": len(
            audit_report.get("references", {}).get("kubejs_references", [])
        ),
        "output_files": [
            "resourcepacks/ATM10_Korean/assets/aquaculture/lang/ko_kr.json",
            "resourcepacks/ATM10_Korean/assets/sushigocrafting/lang/ko_kr.json",
            *guide_files,
            "kubejs/data/sushigocrafting/patchouli_books/sushigocrafting/book.json",
            "config/ftbquests/quests/lang/ko_kr.snbt",
        ],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    completion_path = WORK_ROOT / "family_completion.json"
    if completion_path.is_file():
        previous = load_json(completion_path)
        if "deployment" in previous:
            completion["deployment"] = previous["deployment"]
    write_json(completion_path, completion)
    return report, errors


def output_source(relative: str) -> Path:
    """적용 상대 경로를 저장소 산출물 경로로 바꿔요."""
    prefix = "resourcepacks/"
    if relative.startswith(prefix):
        return PROJECT_ROOT / "output/resourcepack" / relative.removeprefix(prefix)
    return PROJECT_ROOT / "output/overrides" / relative


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 스크립트의 백업·해시 결과를 완료 기록에 반영해요."""
    resolved = manifest_path.resolve()
    try:
        relative_manifest = resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError as exc:
        raise ValueError(f"프로젝트 밖의 적용 기록이에요: {resolved}") from exc
    manifest = load_json(resolved)
    completion_path = WORK_ROOT / "family_completion.json"
    completion = load_json(completion_path)
    expected = set(completion["output_files"])
    errors = []
    matched = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 기록 상태가 applied_and_verified가 아니에요")
    targets = manifest.get("targets")
    if not isinstance(targets, list):
        targets = []
        errors.append("적용 기록의 targets가 목록이 아니에요")
    for target in targets:
        if not isinstance(target, dict) or not isinstance(target.get("files"), list):
            continue
        files = {
            str(row.get("relative_path")): row
            for row in target["files"]
            if isinstance(row, dict) and row.get("relative_path") in expected
        }
        if set(files) != expected:
            continue
        for relative, row in files.items():
            source = output_source(relative)
            target_file = Path(str(row.get("target")))
            if not target_file.is_file() or sha256(target_file) != sha256(source):
                errors.append(f"적용 대상과 산출물 해시가 달라요: {relative}")
            if row.get("source_sha256") != row.get("after_sha256"):
                errors.append(f"적용 기록의 전후 해시가 달라요: {relative}")
        matched.append(target)
    if len(matched) != 1:
        errors.append(f"일치하는 적용 대상 기록 수가 1개가 아니에요: {len(matched)}")
    target = matched[0] if matched else {}
    deployment = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "target": target.get("target_root"),
        "changed_paths": target.get("changed_paths", []),
        "backup_manifest": relative_manifest,
        "errors": errors,
    }
    completion["deployment"] = deployment
    if errors:
        completion["status"] = "incomplete"
    write_json(completion_path, completion)
    return deployment, errors


def run_all() -> tuple[dict[str, object], list[str]]:
    """준비, 생성, 감사와 검증을 차례로 실행해요."""
    prepare_report = prepare()
    build_report = build()
    audit_report, audit_errors = audit()
    verify_report, verify_errors = verify()
    report = {
        "prepare": prepare_report,
        "build": build_report,
        "audit": audit_report,
        "verify": verify_report,
        "status": "complete"
        if not audit_errors and not verify_errors
        else "incomplete",
    }
    return report, audit_errors + verify_errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "build", "audit", "verify", "record-deployment", "all"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    errors = []
    if args.command == "prepare":
        report = prepare()
    elif args.command == "build":
        report = build()
    elif args.command == "audit":
        report, errors = audit()
    elif args.command == "verify":
        report, errors = verify()
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        report, errors = record_deployment(args.manifest)
    else:
        report, errors = run_all()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
