#!/usr/bin/env python3
"""The Bumblezone 본체와 직접 연동 표시 경로를 전수 재검수한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import bumblezone_advancements
import bumblezone_bundled_review
import bumblezone_descriptions
import bumblezone_prose
import bumblezone_quests
import bumblezone_tags
import bumblezone_ui
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/bumblezone"
LANG_ROOT = WORK_ROOT / "the_bumblezone"
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"

DYENAMICS_COLORS = {
    "Amber": "호박색",
    "Aquamarine": "아쿠아마린",
    "Bubblegum": "풍선껌색",
    "Cherenkov": "체렌코프",
    "Conifer": "침엽수색",
    "Fluorescent": "형광색",
    "Honey": "꿀색",
    "Icy Blue": "얼음빛 파란색",
    "Lavender": "라벤더색",
    "Maroon": "적갈색",
    "Mint": "민트색",
    "Navy": "남색",
    "Peach": "복숭아색",
    "Persimmon": "감색",
    "Rose": "장미색",
    "Spring Green": "봄 초록색",
    "Ultramarine": "울트라마린",
    "Wine": "와인색",
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
    "White": "하얀색",
    "Yellow": "노란색",
}

NAME_PHRASES = {
    "The Bumblezone": "The Bumblezone",
    "Bumblezone": "The Bumblezone",
    "Beehemoth": "비히모스",
    "Queen Beehemoth": "여왕 비히모스",
    "Rootmin": "루트민",
    "Sentry Watcher": "센트리 감시자",
    "Bee Queen": "여왕벌",
    "Variant Bee": "변종 벌",
    "Bee Variant": "변종 벌",
    "Honey Slime": "꿀 슬라임",
    "Cosmic Crystal": "코스믹 수정",
    "Essence of the Bees": "벌의 정수",
    "Essence of Raging": "격노의 정수",
    "Essence of Knowing": "통찰의 정수",
    "Essence of Calming": "평온의 정수",
    "Essence of Life": "생명의 정수",
    "Essence of Radiance": "광휘의 정수",
    "Essence of Continuity": "지속의 정수",
    "Wrath of the Hive": "벌집의 분노",
    "Protection of the Hive": "벌집의 보호",
    "Sempiternal Sanctum": "영원 성소",
    "Red Sempiternal Sanctum": "붉은 영원 성소",
    "Purple Sempiternal Sanctum": "보라색 영원 성소",
    "Blue Sempiternal Sanctum": "푸른 영원 성소",
    "Green Sempiternal Sanctum": "초록색 영원 성소",
    "Yellow Sempiternal Sanctum": "노란색 영원 성소",
    "White Sempiternal Sanctum": "하얀 영원 성소",
    "Cell Maze": "벌집 미로",
    "Throne Pillar": "왕좌 기둥",
    "Stingless Bee Helmet": "무침벌 투구",
    "Bumble Bee Chestplate": "호박벌 흉갑",
    "Trans Bumble Bee Chestplate": "트랜스 호박벌 흉갑",
    "Honey Bee Leggings": "꿀벌 레깅스",
    "Carpenter Bee Boots": "어리호박벌 부츠",
    "Buzzing Briefcase": "윙윙거리는 서류 가방",
    "Honey Crystal Shield": "꿀 수정 방패",
    "Honey Crystal Shards": "꿀 수정 조각",
    "Honey Crystal Shard": "꿀 수정 조각",
    "Glistering Honey Crystal": "반짝이는 꿀 수정",
    "Honey Crystal": "꿀 수정",
    "Crystalline Flower": "결정꽃",
    "Flower Headwear": "꽃 머리 장식",
    "Stinger Spear": "벌침 창",
    "Bee Stinger": "벌침",
    "Bee Cannon": "벌 대포",
    "Crystal Cannon": "수정 대포",
    "Honey Compass": "꿀 나침반",
    "Bee Bread": "벌빵",
    "Bee Soup": "벌 수프",
    "Pollen Puff": "꽃가루 뭉치",
    "Pile of Pollen": "꽃가루 더미",
    "Suspicious Pile of Pollen": "수상한 꽃가루 더미",
    "Dirt Pellet": "흙 알갱이",
    "Honey Cocoon": "꿀 고치",
    "Honeycomb Brood Block": "벌집 유충 블록",
    "Empty Honeycomb Brood Block": "빈 벌집 유충 블록",
    "Filled Porous Honeycomb Block": "꿀이 찬 다공성 벌집 조각 블록",
    "Porous Honeycomb Block": "다공성 벌집 조각 블록",
    "Beehive Beeswax": "벌집 밀랍",
    "Sticky Honey Residue": "끈적이는 꿀 찌꺼기",
    "Sticky Honey Redstone": "끈적이는 꿀 레드스톤",
    "Redstone Honey Web": "레드스톤 꿀 그물",
    "Honey Web": "꿀 그물",
    "Royal Jelly Fluid": "로열 젤리 액체",
    "Royal Jelly Block": "로열 젤리 블록",
    "Royal Jelly Bottle": "로열 젤리 병",
    "Royal Jelly Bucket": "로열 젤리 양동이",
    "Sugar Water Bubble Column": "설탕물 거품 기둥",
    "Sugar Water Bottle": "설탕물 병",
    "Sugar Water Bucket": "설탕물 양동이",
    "Sugar Water": "설탕물",
    "Honey Fluid": "액체 꿀",
    "Honey Bucket": "꿀 양동이",
    "Super Candle Soul Wick": "대형 양초 영혼 심지",
    "Super Candle Wick": "대형 양초 심지",
    "Super Candle Base": "대형 양초 받침",
    "Super Candle": "대형 양초",
    "Potion Candle Base": "물약 양초 받침",
    "Potion Candle": "물약 양초",
    "String Curtain": "실 커튼",
    "Carvable Wax": "조각용 밀랍",
    "Ancient Wax Compound Eyes": "고대 밀랍 겹눈",
    "Ancient Wax Diamond": "고대 밀랍 마름모",
    "Ancient Wax Bricks": "고대 밀랍 벽돌",
    "Ancient Wax": "고대 밀랍",
    "Luminescent Wax Channel": "발광 밀랍 통로",
    "Luminescent Wax Corner": "발광 밀랍 모서리",
    "Luminescent Wax Node": "발광 밀랍 마디",
    "Luminescent Wax": "발광 밀랍",
    "Comb Cutter": "벌집 절단",
    "Potent Poison": "강력한 독",
    "Neurotoxins": "신경독",
    "Neurotoxin": "신경독",
    "Hive Lifeline": "벌집 생명선",
    "Beenergized": "벌에너지",
    "Paralyzed": "마비",
    "Hidden": "은신",
    "Honey Slime Ranch": "꿀 슬라임 목장",
    "Bumbling Beepartments": "윙윙 벌 아파트",
    "Gazebuzz Cluster": "가제버즈 군락",
    "Honitel": "허니텔",
    "Phantasm Aviary": "환영 새장",
    "Howling Constructs": "울부짖는 구조물",
    "Pollinated Fields": "꽃가루받이 들판",
    "Pollinated Pillar": "꽃가루받이 기둥",
    "Pollinated Stream": "꽃가루받이 개울",
    "Floral Meadows": "꽃 목초지",
    "Crystal Canyon": "수정 협곡",
    "Sugar Water Floor": "설탕물 바닥",
    "Hive Wall": "벌집 벽",
    "Hive Pillar": "벌집 기둥",
    "Ancient Hoops": "고대 고리",
    "Ancient Shrine": "고대 성소",
    "Battle Cubes": "전투 큐브",
    "Bee House": "벌집 집",
    "Candle Parkour": "양초 파쿠르",
    "Cannon Range": "대포 사격장",
    "Cherry Veteran Tree": "벚나무 고목",
    "Dance Floor": "무도장",
    "Goliath Honey Fountain": "거대 꿀 분수",
    "Hanging Garden": "매달린 정원",
    "Hive Temple": "벌집 신전",
    "Honey Cave Room": "꿀 동굴 방",
    "Honey Fountain": "꿀 분수",
    "Ice Monolith": "얼음 거석",
    "Mite Fortress": "진드기 요새",
    "Overgrown Flower": "무성한 꽃",
    "Pirate Ship": "해적선",
    "Stinger Spear Shrine": "벌침 창 성소",
    "Subway": "지하철",
    "Heavy Air": "무거운 공기",
    "Windy Air": "바람 부는 공기",
    "Infinity Barrier": "무한 장벽",
    "Dense Bubble Block": "고밀도 거품 블록",
    "Banner Pattern": "현수막 무늬",
    "Music Disc": "음반",
    "Spawn Egg": "생성 알",
    "Potion of Neurotoxin": "신경독 물약",
    "Splash Potion of Neurotoxin": "투척용 신경독 물약",
    "Lingering Potion of Neurotoxin": "잔류형 신경독 물약",
    "Arrow of Neurotoxin": "신경독 화살",
}

WORD_TRANSLATIONS = {
    **COLORS,
    "Bee Nests": "벌집",
    "Bee Nest": "벌집",
    "Beehives": "벌통",
    "Beehive": "벌통",
    "Honeycombs": "벌집 조각",
    "Honeycomb": "벌집 조각",
    "Bumblezone": "The Bumblezone",
    "Beehemoths": "비히모스",
    "Bees": "벌",
    "Bee": "벌",
    "Royal Jelly": "로열 젤리",
    "Honey": "꿀",
    "Pollen": "꽃가루",
    "Wax": "밀랍",
    "Essence": "정수",
    "Ancient": "고대",
    "Luminescent": "발광",
    "Glistering": "반짝이는",
    "Sticky": "끈적이는",
    "Porous": "다공성",
    "Filled": "가득 찬",
    "Empty": "빈",
    "Suspicious": "수상한",
    "Sugar Infused": "설탕이 스며든",
    "Sugar": "설탕",
    "Water": "물",
    "Fluid": "액체",
    "Bottle": "병",
    "Bucket": "양동이",
    "Block": "블록",
    "Bricks": "벽돌",
    "Stairs": "계단",
    "Slabs": "반 블록",
    "Slab": "반 블록",
    "Wall": "벽",
    "Channel": "통로",
    "Corner": "모서리",
    "Node": "마디",
    "Diamond": "마름모",
    "Compound Eyes": "겹눈",
    "String Curtains": "실 커튼",
    "Curtains": "커튼",
    "Curtain": "커튼",
    "Base": "받침",
    "Wick": "심지",
    "Soul": "영혼",
    "Crystal": "수정",
    "Shards": "조각",
    "Shard": "조각",
    "Shield": "방패",
    "Spear": "창",
    "Cannon": "대포",
    "Compass": "나침반",
    "Helmet": "투구",
    "Chestplates": "흉갑",
    "Chestplate": "흉갑",
    "Leggings": "레깅스",
    "Boots": "부츠",
    "Armors": "갑옷",
    "Armor": "갑옷",
    "Flower": "꽃",
    "Flowers": "꽃",
    "Headwear": "머리 장식",
    "Cocoon": "고치",
    "Brood": "유충",
    "Residue": "찌꺼기",
    "Redstone": "레드스톤",
    "Web": "그물",
    "Egg": "알",
    "Variant": "변종",
    "Slime": "슬라임",
    "Queen": "여왕",
    "Watcher": "감시자",
    "Sentry": "센트리",
    "Candle": "양초",
    "Carvable": "조각용",
    "Waxes": "밀랍",
    "Dyes": "염료",
    "White": "하얀색",
    "Arrows": "화살",
    "Eyes": "눈",
    "Peace": "평화",
    "Pluses": "십자",
    "Sun": "태양",
    "Swords": "검",
    "Disc": "음반",
    "Discs": "음반",
    "Structures": "구조물",
    "Structure": "구조물",
    "Items": "아이템",
    "Item": "아이템",
    "Blocks": "블록",
    "Fluids": "액체",
    "Tools": "도구",
    "Repair": "수리",
    "Enchantables": "마법 부여 가능 아이템",
    "Enchanting": "마법 부여",
    "Potions": "물약",
    "Potion": "물약",
    "Lanterns": "랜턴",
    "Lantern": "랜턴",
    "Glass Panes": "유리판",
    "Glasses": "유리",
    "Glass": "유리",
    "Panes": "판",
    "Terracotta": "테라코타",
    "Glazed Terracotta": "유광 테라코타",
    "Concrete": "콘크리트",
    "Hopper Pots": "호퍼 화분",
    "Botany Pots": "식물 화분",
    "Creative": "크리에이티브",
    "Elite": "엘리트",
    "Ultra": "울트라",
    "Mod Compatibility": "모드 호환성",
    "Worldgen": "세계 생성",
    "Dimension": "차원",
    "Bee Aggression": "벌 공격성",
    "Client": "클라이언트",
    "General": "일반",
    "Configs": "설정",
    "Config": "설정",
    "Compatibility": "호환성",
    "Compat": "호환",
    "Options": "설정",
    "Option": "설정",
    "Fog Brightness Percentage": "안개 밝기 비율",
    "Fog Thickness": "안개 농도",
    "Fog": "안개",
    "Brightness": "밝기",
    "Percentage": "비율",
    "Thickness": "농도",
    "Essence HUD Rendering": "정수 HUD 표시",
    "Visual Effect Layers": "시각 효과 레이어",
    "Visual Effect Speed": "시각 효과 속도",
    "Knowing Essence Highlighting": "통찰의 정수 강조 표시",
    "Knowing Essence": "통찰의 정수",
    "Raging Essence": "격노의 정수",
    "Calming Essence": "평온의 정수",
    "Life Essence": "생명의 정수",
    "Radiance Essence": "광휘의 정수",
    "Continuity Essence": "지속의 정수",
    "Highlight Living Entities": "생명체 강조 표시",
    "Highlight Common Items": "일반 아이템 강조 표시",
    "Highlight Uncommon Items": "고급 아이템 강조 표시",
    "Highlight Rare Items": "희귀 아이템 강조 표시",
    "Highlight Epic Items": "특급 아이템 강조 표시",
    "Highlight Bosses": "보스 강조 표시",
    "Highlight Monsters": "몬스터 강조 표시",
    "Highlight Tamed": "길들인 몹 강조 표시",
    "Structure Name Clientside": "클라이언트 구조물 이름 표시",
    "Structure Name Serverside": "서버 구조물 이름 표시",
    "Structure Name X Coord": "구조물 이름 X 좌표",
    "Structure Name Y Coord": "구조물 이름 Y 좌표",
    "Show Armor Durability": "갑옷 내구도 표시",
    "Armor Durability X Coord": "갑옷 내구도 X 좌표",
    "Armor Durability Y Coord": "갑옷 내구도 Y 좌표",
    "Armor Durability": "갑옷 내구도",
    "Entity Model/Renderer": "엔티티 모델 및 렌더러",
    "Variant Bee Backup Model": "변종 벌 예비 모델",
    "Bee Queen Bonus Trade Item": "여왕벌 보너스 거래 아이템",
    "Game Music": "게임 음악",
    "Play Wrath Music": "분노 음악 재생",
    "Play Sanctum Music": "성소 음악 재생",
    "Display Bee Queen's Speech Bubble": "여왕벌 말풍선 표시",
    "Essence Blocks": "정수 블록",
    "Disable Essence Block Shader": "정수 블록 셰이더 끄기",
    "Silly Stuff": "장난스러운 설정",
    "Gui Bees All Year Round": "GUI 벌 연중 표시",
    "Gui Bees On April Fools": "만우절에 GUI 벌 표시",
    "Restrict Gui Bees to Bz Dimension": "GUI 벌을 The Bumblezone에서만 표시",
    "Maximum Number of Gui Bees": "GUI 벌 최대 수",
    "Bees Aggression": "벌 공격성",
    "Beehemoth Triggers Wrath": "비히모스 공격 시 분노 발동",
    "Wrath Outside Bumblezone": "The Bumblezone 밖에서 분노 허용",
    "Wrath Particles": "분노 입자",
    "Allow Wrath": "분노 허용",
    "Aggression Trigger Range": "공격성 발동 범위",
    "Wrath Timer": "분노 지속 시간",
    "Bee Buffs From Wrath": "분노로 얻는 벌 강화 효과",
    "Speed Boost Level": "속도 증가 단계",
    "Absorption Level": "흡수 단계",
    "Strength Level": "힘 단계",
    "Protection Timer": "보호 지속 시간",
    "Welcome Message": "환영 메시지",
    "Enable Message": "메시지 사용",
    "Teleportation": "순간이동",
    "Enable Entering Teleport": "입장 순간이동 사용",
    "Enable Exiting Teleport": "퇴장 순간이동 사용",
    "Send Mobs To Overworld": "몹을 오버월드로 보내기",
    "Force Overworld As Exit": "출구를 오버월드로 고정",
    "Only Overworld Hive Teleport": "오버월드 벌집에서만 순간이동",
    "Wrong Under Hive Block Warning": "벌집 아래 블록 오류 경고",
    "Allow Modded Hive Teleport": "모드 벌집 순간이동 허용",
    "Default Dimension": "기본 차원",
    "Misc Compat": "기타 호환",
    "Replacement Honey Fluid": "대체할 액체 꿀",
    "Pokecube Compat": "Pokecube 호환",
    "Spawn Bee-like Pokemon": "벌 계열 포켓몬 생성",
    "Bee Pokemon gets Protection": "벌 포켓몬에게 보호 부여",
    "Pokemon From Block Spawnrates": "블록에서 나오는 포켓몬 생성률",
    "Tropicraft Compat": "Tropicraft 호환",
    "Allow Tropibee Spawning": "트로피비 생성 허용",
    "Tropibee Spawnrate": "트로피비 생성률",
    "Tropibee By Dispensers": "발사기로 트로피비 생성",
    "Resourceful Bees Compat": "Resourceful Bees 호환",
    "Spawn Resourceful Bees": "Resourceful Bees 벌 생성",
    "Resourceful Bees From Block Spawnrates": "블록에서 나오는 Resourceful Bees 생성률",
    "Resourceful Bees Spawnrates": "Resourceful Bees 생성률",
    "Bee Dungeon Ore Comb Rates": "벌 던전 광물 벌집 조각 비율",
    "Spider Infested Dungeon Ore Comb Rates": "거미 감염 던전 광물 벌집 조각 비율",
    "Ore Comb Vein Rates": "광물 벌집 조각 광맥 비율",
    "Bee Jar Revives Brood Block": "벌 단지로 유충 블록 되살리기",
    "Resourceful Bees From Dispenser Block": "발사기 유충 블록에서 Resourceful Bees 생성",
    "Productive Bees Compat": "Productive Bees 호환",
    "Spawn Productive Bees": "Productive Bees 벌 생성",
    "Productive Bees Spawnrate": "Productive Bees 생성률",
    "Allowed Productive Bees": "허용할 Productive Bees 벌",
    "Ore Comb Veins": "광물 벌집 조각 광맥",
    "Bee Dungeon Ore Combs": "벌 던전 광물 벌집 조각",
    "Bee Cage Revives Brood Blocks": "벌 우리로 유충 블록 되살리기",
    "Productive Bees From Dispenser Block": "발사기 유충 블록에서 Productive Bees 생성",
    "Spider Infested Ore Comb Rates": "거미 감염 던전 광물 벌집 조각 비율",
    "Friends and Foes Compat": "Friends and Foes 호환",
    "Beekeeper Trades": "양봉가 거래",
    "Quark Compat": "Quark 호환",
    "Bz Items in Enchantment Tooltips": "마법 툴팁에 The Bumblezone 아이템 표시",
    "Buzzier Bees Compat": "Buzzier Bees 호환",
    "Bee Bottle Revives Brood Blocks": "벌 병으로 유충 블록 되살리기",
    "Forbidden Arcanus Compat": "Forbidden and Arcanus 호환",
    "Bee Bucket Revives Brood Blocks": "벌 양동이로 유충 블록 되살리기",
    "Potion of Bees Compat": "Potion of Bees 호환",
    "Bee Potion Revives Brood Blocks": "벌 물약으로 유충 블록 되살리기",
    "Goodall Compat": "Goodall 호환",
    "Bottled Bee Revives Brood Blocks": "병에 든 벌로 유충 블록 되살리기",
    "Beekeeper Compat": "Beekeeper 호환",
    "Lootr Compat": "Lootr 호환",
    "Lootr Cocoons": "Lootr 꿀 고치",
    "Create Compat": "Create 호환",
    "Limestone From Honey": "꿀로 석회암 생성",
    "Honey Bottle Extraction": "꿀이 든 병에서 액체 추출",
    "Variant Bees": "변종 벌",
    "Variant Types": "변종 종류",
    "Base Speed": "기본 속도",
    "Enable Friendly Fire": "아군 공격 허용",
    "Special Bee Spawning Options": "특수 벌 생성 설정",
    "Enable Special Spawning System": "특수 생성 시스템 사용",
    "Bees Amount Per Player": "플레이어당 벌 수",
    "Bee Loot Injection": "벌 전리품 추가",
    "Inject Into Vanilla Bee Loot": "바닐라 벌 전리품에 추가",
    "Inject Into Modded Bee Loot": "모드 벌 전리품에 추가",
    "Brewing Recipes": "양조법",
    "Glistering Honey Brewing Ingredient": "행운 물약용 반짝이는 꿀 재료",
    "Bee Stinger Brewing Ingredient": "긴 독 물약용 벌침 재료",
    "Bee Soup Brewing Ingredient": "신경독 물약용 벌 수프 재료",
    "Enchantments": "마법 부여",
    "Neurotoxin Enchant Max Level": "신경독 마법 최대 단계",
    "Paralysis Effect Max Duration": "마비 효과 최대 지속 시간",
    "Bee Queens": "여왕벌",
    "Bonus Trade Multiplier": "보너스 거래 배수",
    "Bonus Trade Timer": "보너스 거래 지속 시간",
    "Bonus Trade Stock": "보너스 거래 재고",
    "Holiday Trades": "기념일 거래",
    "Queen Respawning": "여왕 재생성",
    "Queen Ground Item Pickup": "여왕의 바닥 아이템 줍기",
    "Consume Item Entities": "아이템 엔티티 흡수",
    "Consume Experience Orbs": "경험치 구슬 흡수",
    "Consume Items In GUI": "GUI에서 아이템 흡수",
    "Consume Experience In GUI": "GUI에서 경험치 흡수",
    "Enchanting Power Per Tier": "티어당 마법 부여 능력",
    "Extra Required XP For Tiers": "티어에 필요한 추가 경험치",
    "Extra Tier Cost For Enchants": "마법 추가 티어 비용",
    "General Mechanics": "일반 기능",
    "Dispenser Drops Glass Bottle": "발사기가 유리병 떨어뜨리기",
    "Brood Block Bee Area Capacity": "유충 블록 주변 벌 수 제한",
    "Pile of Pollen Hyper Flammability": "꽃가루 더미 초고속 연소",
    "Super Candle Burns Living Entities": "대형 양초가 생명체 태우기",
    "Music Discs": "음반",
    "Wandering Trader Trades": "떠돌이 상인 거래",
    "Essence Item And Events": "정수 아이템 및 이벤트",
    "Repeatable Essence Events": "정수 이벤트 반복 허용",
    "Blue Arena Bubbles Mechanic": "푸른 경기장 거품 기능",
    "Blue Arena Time Frame In Ticks": "푸른 경기장 제한 시간(틱)",
    "Green Arena Time Frame In Ticks": "초록색 경기장 제한 시간(틱)",
    "Purple Arena Time Frame In Ticks": "보라색 경기장 제한 시간(틱)",
    "Red Arena Time Frame In Ticks": "붉은 경기장 제한 시간(틱)",
    "Yellow Arena Time Frame In Ticks": "노란색 경기장 제한 시간(틱)",
    "White Arena Time Frame In Ticks": "하얀 경기장 제한 시간(틱)",
    "Cosmic Crystal Health": "코스믹 수정 체력",
    "Raging Essence Ability Use": "격노의 정수 능력 사용량",
    "Raging Essence Cooldown": "격노의 정수 재사용 대기시간",
    "Raging Essence Strength Levels": "격노의 정수 힘 단계",
    "Knowing Essence Ability Use": "통찰의 정수 능력 사용량",
    "Knowing Essence Cooldown": "통찰의 정수 재사용 대기시간",
    "Calming Essence Ability Use": "평온의 정수 능력 사용량",
    "Calming Essence Cooldown": "평온의 정수 재사용 대기시간",
    "Life Essence Ability Use": "생명의 정수 능력 사용량",
    "Life Essence Cooldown": "생명의 정수 재사용 대기시간",
    "Radiance Essence Ability Use": "광휘의 정수 능력 사용량",
    "Radiance Essence Cooldown": "광휘의 정수 재사용 대기시간",
    "Continuity Essence Cooldown": "지속의 정수 재사용 대기시간",
    "Dungeons": "던전",
    "Bee Dungeon Rarity": "벌 던전 희귀도",
    "Tree Dungeon Rarity": "나무 던전 희귀도",
    "Spider Infested Dungeon Rarity": "거미 감염 던전 희귀도",
    "Spider Infested Dungeon Spawner Rates": "거미 감염 던전 생성기 비율",
}

QUALITY_REPLACEMENTS = (
    ("범블존", "The Bumblezone"),
    ("부봉침 벌", "무침벌"),
    ("벌 떡", "벌빵"),
    ("꿀 수정 파편", "꿀 수정 조각"),
    ("꿀 자루", "꿀 고치"),
    ("벌의 분노", "벌집의 분노"),
    ("벌의 보호", "벌집의 보호"),
    ("벌의 라텍스", "벌의 정수"),
)

ALLOWED_ORIGINALS = {
    "The Bumblezone",
    "www.github.com/TelepathicGrunt/Bumblezone/wiki",
}


def load_json(path: Path) -> dict[str, str]:
    """문자열 값으로 이루어진 UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(text, str) for key, text in value.items()
    ):
        raise TypeError(f"문자열 JSON 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 저장한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_object_json(path: Path) -> dict[str, object]:
    """FTB Quests 후보처럼 문자열과 목록을 포함하는 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError(f"JSON 객체가 아닙니다: {path}")
    return value


def normalize_bundled(value: str) -> str:
    """현재 JAR의 한국어 후보에서 확정 용어 충돌만 바로잡는다."""
    for old, new in QUALITY_REPLACEMENTS:
        value = value.replace(old, new)
    return value


def translate_name(source: str) -> str | None:
    """짧은 이름과 반복되는 태그 이름을 확정 어휘로 조합한다."""
    if source in NAME_PHRASES:
        return NAME_PHRASES[source]
    translated = source
    replacements = {**WORD_TRANSLATIONS, **NAME_PHRASES}
    for english in sorted(replacements, key=len, reverse=True):
        korean = replacements[english]
        translated = re.sub(
            rf"(?<![A-Za-z]){re.escape(english)}(?![A-Za-z])", korean, translated
        )
    translated = re.sub(r"\s+", " ", translated).strip()
    if re.search(r"[A-Za-z]", translated):
        return None
    return translated


def translate_banner(key: str, source: str) -> str | None:
    """색상별 현수막 무늬 이름을 일관되게 번역한다."""
    if not key.startswith("block.minecraft.banner.the_bumblezone."):
        return None
    for english, korean in sorted(
        COLORS.items(), key=lambda row: len(row[0]), reverse=True
    ):
        if source.startswith(f"{english} "):
            motif = source[len(english) + 1 :]
            translated = translate_name(motif)
            if translated:
                return f"{korean} {translated}"
    return None


def reviewed_value(
    key: str, source: str, candidate: str
) -> tuple[str | None, str | None]:
    """키 유형별 검수 규칙을 적용하고 출처를 함께 반환한다."""
    if key in bumblezone_advancements.TRANSLATIONS:
        return bumblezone_advancements.TRANSLATIONS[key], "manual_review"
    if key in bumblezone_bundled_review.TRANSLATIONS:
        return bumblezone_bundled_review.TRANSLATIONS[key], "manual_review"
    if key in bumblezone_prose.TRANSLATIONS:
        return bumblezone_prose.TRANSLATIONS[key], "manual_review"
    if key in bumblezone_ui.TRANSLATIONS:
        return bumblezone_ui.TRANSLATIONS[key], "manual_review"
    description = bumblezone_descriptions.translate(key, source)
    if description:
        return description, "manual_review"
    if key.startswith("tag."):
        translated = bumblezone_tags.translate(source)
        if translated:
            return translated, "manual_review"
    if (
        key.startswith("jukebox_song.the_bumblezone.")
        or source in ALLOWED_ORIGINALS
        or source.startswith(("http://", "https://"))
    ):
        return source, "keep_original"
    if key.startswith("the_bumblezone.configuration.") and not key.endswith(".tooltip"):
        translated = translate_name(source)
        if translated:
            return translated, "manual_pattern_review"
    if key.startswith("the_bumblezone.midnightconfig."):
        translated = translate_name(source)
        if translated:
            return translated, "manual_pattern_review"
    banner = translate_banner(key, source)
    if banner:
        return banner, "manual_pattern_review"
    name_prefixes = (
        "block.",
        "item.",
        "entity.the_bumblezone.",
        "biome.the_bumblezone.",
        "structure.the_bumblezone.",
        "fluid.",
        "fluid_type.",
        "effect.the_bumblezone.",
        "enchantment.the_bumblezone.",
        "tag.",
        "the_bumblezone.",
    )
    if key.startswith(name_prefixes) and "\n" not in source and len(source) <= 80:
        translated = translate_name(source)
        if translated:
            return translated, "manual_pattern_review"
    normalized = normalize_bundled(candidate)
    if source != normalized and not re.search(r"[A-Za-z]", normalized):
        return normalized, "bundled_quality_review"
    return None, None


def review_language() -> dict[str, object]:
    """영어 1,788키 전체에 검수 번역을 적용하고 미결 항목을 기록한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    candidates = load_json(LANG_ROOT / "ko_kr.json")
    reviewed: dict[str, str] = {}
    provenance: dict[str, str] = {}
    unresolved: list[dict[str, str]] = []
    for key, source in english.items():
        translated, origin = reviewed_value(key, source, candidates[key])
        if translated is None or origin is None:
            unresolved.append(
                {"key": key, "source": source, "candidate": candidates[key]}
            )
            reviewed[key] = candidates[key]
            provenance[key] = "unresolved"
        else:
            reviewed[key] = translated
            provenance[key] = origin
    write_json(LANG_ROOT / "ko_kr.json", reviewed)
    write_json(LANG_ROOT / "candidate_sources.json", provenance)
    write_json(WORK_ROOT / "unresolved_language.json", unresolved)
    report = {
        "family": "The Bumblezone",
        "keys_reviewed": len(english),
        "resolved": len(english) - len(unresolved),
        "unresolved": len(unresolved),
        "source_counts": dict(Counter(provenance.values())),
    }
    write_json(WORK_ROOT / "manual_review_report.json", report)
    return report


def build_integrations() -> dict[str, object]:
    """현재 Dyenamics and Friends의 The Bumblezone 연동 표시 키를 생성한다."""
    mods = resolve_source_root() / "mods"
    jars = sorted(mods.glob("dyenamicsandfriends-*.jar"))
    if len(jars) != 1:
        raise RuntimeError(f"Dyenamics and Friends JAR 수가 1이 아닙니다: {jars}")
    jar = jars[0]
    with ZipFile(jar) as archive:
        english = json.loads(
            archive.read("assets/dyenamicsandfriends/lang/en_us.json").decode("utf-8")
        )
    scoped = {
        key: value
        for key, value in english.items()
        if key.startswith("block.dyenamicsandfriends.bumblezone_")
        or key == "resourcePack.dyenamicsandfriends.the_bumblezone"
    }
    if len(scoped) != 37:
        raise RuntimeError(
            f"Dyenamics and Friends 연동 키가 37개가 아닙니다: {len(scoped)}"
        )
    translated: dict[str, str] = {}
    for key, source in scoped.items():
        if key == "resourcePack.dyenamicsandfriends.the_bumblezone":
            translated[key] = "Dyenamics And Friends - The Bumblezone"
            continue
        match = re.fullmatch(r"(.+) (String Curtain|Super Candle Base)", source)
        if not match or match.group(1) not in DYENAMICS_COLORS:
            raise RuntimeError(f"알 수 없는 Dyenamics 연동 이름: {key}={source}")
        color, item = match.groups()
        suffix = {"String Curtain": "실 커튼", "Super Candle Base": "대형 양초 받침"}[
            item
        ]
        translated[key] = f"{DYENAMICS_COLORS[color]} {suffix}"
    integration_root = WORK_ROOT / "integrations/dyenamicsandfriends"
    write_json(integration_root / "en_us.json", scoped)
    write_json(integration_root / "ko_kr.json", translated)
    output = OUTPUT_ASSETS / "dyenamicsandfriends/lang/ko_kr.json"
    write_json(output, translated)
    report = {
        "jar": jar.name,
        "keys": len(scoped),
        "output": str(output.relative_to(PROJECT_ROOT)),
    }
    write_json(WORK_ROOT / "integration_report.json", report)
    return report


def review_quests() -> dict[str, object]:
    """The Bumblezone 챕터와 관련 기본 갑옷 퀘스트 195개 표시 키를 검수한다."""
    reviewed = 0
    scope_counts: dict[str, int] = {}
    for scope in ("bumblezone", "related"):
        root = WORK_ROOT / f"quests/{scope}"
        english = load_object_json(root / "en_us.json")
        korean = load_object_json(root / "ko_kr.json")
        sources = load_object_json(root / "candidate_sources.json")
        for key, source in english.items():
            translated = bumblezone_quests.translate(scope, key, source)
            translated = translated.replace("\n", "\\n")
            current = korean[key]
            if isinstance(current, str):
                replacement: object = translated
            elif isinstance(current, list) and current and isinstance(current[0], str):
                replacement = [translated, *current[1:]]
            else:
                raise TypeError(f"지원하지 않는 퀘스트 표시 값: {key}={current!r}")
            errors = family_goal.quest_snbt.validate_value(key, source, replacement)
            if errors:
                raise ValueError("; ".join(errors))
            korean[key] = replacement
            sources[key] = "manual_review"
            reviewed += 1
        write_json(root / "ko_kr.json", korean)
        write_json(root / "candidate_sources.json", sources)
        scope_counts[scope] = len(english)
    fallback_root = WORK_ROOT / "quests/fallback"
    write_json(fallback_root / "ko_kr.json", bumblezone_quests.EXTRA_FALLBACK_TITLES)
    write_json(
        fallback_root / "candidate_sources.json",
        {
            key: "manual_fallback_review"
            for key in bumblezone_quests.EXTRA_FALLBACK_TITLES
        },
    )
    report = {
        "keys_reviewed": reviewed,
        "scope_counts": scope_counts,
        "new_translation": reviewed,
        "explicit_fallback_titles": len(bumblezone_quests.EXTRA_FALLBACK_TITLES),
    }
    write_json(WORK_ROOT / "quest_review_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("review", "build-integrations", "review-quests")
    )
    args = parser.parse_args()
    if args.command == "review":
        report = review_language()
    elif args.command == "build-integrations":
        report = build_integrations()
    else:
        report = review_quests()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
