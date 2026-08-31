#!/usr/bin/env python3
"""생물·몹 확장 네 모드의 전체 표시 문자열과 안내서를 번역하고 검증해요."""

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
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "mob_expansion"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
RESOURCEPACK_ROOT = active_output_root() / "resourcepack/ATM10_Korean"
QUEST_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
BOOK_OUTPUT = (
    active_output_root()
    / "overrides/kubejs/data/livingthings/patchouli_books/lexicon/book.json"
)
GUIDE_SOURCE_ROOT = "assets/livingthings/patchouli_books/lexicon/en_us"
GUIDE_OUTPUT_ROOT = (
    RESOURCEPACK_ROOT / "assets/livingthings/patchouli_books/lexicon/ko_kr"
)
BOOK_SOURCE = "data/livingthings/patchouli_books/lexicon/book.json"
VISIBLE_FIELDS = {"name", "description", "text", "title", "landing_text"}
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
PATCHOULI_CODE = re.compile(r"\$\([^)]+\)")
NUMBER = re.compile(r"\d+(?:[.]\d+)?")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")

NAMESPACES = {
    "endermanoverhaul": "endermanoverhaul-neoforge-*.jar",
    "creeperoverhaul": "CreeperOverhaul-neoforge-*.jar",
    "livingthings": "livingthings-neoforge-*.jar",
    "variantsandventures": "variantsandventures-neoforge-*.jar",
}

ENDERMAN_BIOMES = {
    "badlands": "악지",
    "cave": "동굴",
    "coral": "산호",
    "crimson_forest": "진홍빛 숲",
    "dark_oak": "짙은 참나무",
    "desert": "사막",
    "end": "엔드",
    "end_islands": "엔드 섬",
    "flower_fields": "꽃밭",
    "ice_spikes": "역고드름",
    "mushroom_fields": "버섯 들판",
    "nether_wastes": "네더 황무지",
    "savanna": "사바나",
    "snowy": "눈 덮인",
    "soulsand_valley": "영혼 모래 골짜기",
    "swamp": "늪",
    "warped_forest": "뒤틀린 숲",
    "windswept_hills": "바람이 세찬 언덕",
}

ENDERMAN_FIXED = {
    "block.endermanoverhaul.tiny_skull": "작은 해골",
    "config.endermanoverhaul.allowPickingUpBlocks": "블록 줍기 허용",
    "config.endermanoverhaul.allowSpawning": "생성 허용",
    "config.endermanoverhaul.client.title": "Enderman Overhaul 클라이언트",
    "config.endermanoverhaul.clientConfig": "클라이언트 설정",
    "config.endermanoverhaul.description": (
        "Enderman Overhaul은 생물군계별 엔더맨을 추가합니다!"
    ),
    "config.endermanoverhaul.endEndermanTeleportChance": "엔드 엔더맨 순간이동 확률",
    "config.endermanoverhaul.flashScreen": "화면 번쩍임",
    "config.endermanoverhaul.friendlyEndermanDespawn": "우호적 엔더맨 소멸",
    "config.endermanoverhaul.friendlyEndermanTeleport": "우호적 엔더맨 순간이동",
    "config.endermanoverhaul.replaceDefaultEnderman": "기본 엔더맨 대체",
    "config.endermanoverhaul.replaceMekanismBabyEnderman": (
        "Mekanism 아기 엔더맨 대체"
    ),
    "config.endermanoverhaul.title": "Enderman Overhaul",
    "entity.endermanoverhaul.ancient_pearl": "고대의 진주",
    "entity.endermanoverhaul.axolotl_pet_enderman": "아홀로틀 반려 엔더맨",
    "entity.endermanoverhaul.bubble_pearl": "거품 진주",
    "entity.endermanoverhaul.corrupted_pearl": "타락한 진주",
    "entity.endermanoverhaul.crimson_pearl": "진홍빛 진주",
    "entity.endermanoverhaul.ender_bullet": "엔더 탄환",
    "entity.endermanoverhaul.hammerhead_pet_enderman": "귀상어 반려 엔더맨",
    "entity.endermanoverhaul.icy_pearl": "얼어붙은 진주",
    "entity.endermanoverhaul.pet_enderman": "반려 엔더맨",
    "entity.endermanoverhaul.scarab": "스카라베",
    "entity.endermanoverhaul.soul_pearl": "영혼 진주",
    "entity.endermanoverhaul.spirit": "영혼",
    "entity.endermanoverhaul.summoner_pearl": "소환사의 진주",
    "entity.endermanoverhaul.warped_pearl": "뒤틀린 진주",
    "item.endermanoverhaul.ancient_pearl": "고대의 진주",
    "item.endermanoverhaul.badlands_hood": "악지 후드",
    "item.endermanoverhaul.bubble_pearl": "거품 진주",
    "item.endermanoverhaul.corrupted_blade": "타락한 검",
    "item.endermanoverhaul.corrupted_pearl": "타락한 진주",
    "item.endermanoverhaul.corrupted_shield": "타락한 방패",
    "item.endermanoverhaul.crimson_pearl": "진홍빛 진주",
    "item.endermanoverhaul.enderman_tooth": "엔더맨 이빨",
    "item.endermanoverhaul.icy_pearl": "얼어붙은 진주",
    "item.endermanoverhaul.savanna_hood": "사바나 후드",
    "item.endermanoverhaul.scarab_spawn_egg": "스카라베 생성 알",
    "item.endermanoverhaul.snowy_hood": "눈 덮인 후드",
    "item.endermanoverhaul.soul_pearl": "영혼 진주",
    "item.endermanoverhaul.spirit_spawn_egg": "영혼 생성 알",
    "item.endermanoverhaul.summoner_pearl": "소환사의 진주",
    "item.endermanoverhaul.warped_pearl": "뒤틀린 진주",
    "itemGroup.endermanoverhaul.main": "Enderman Overhaul",
    "subtitles.endermanoverhaul.entity.ancient_pearl.hit": "고대의 진주가 맞음",
    "subtitles.endermanoverhaul.entity.bubble_pearl.hit": "거품 진주가 터짐",
    "subtitles.endermanoverhaul.entity.bubble_pearl.thrown": "거품 진주가 던져짐",
    "subtitles.endermanoverhaul.entity.cave_enderman.ambient": "동굴 엔더맨이 울음",
    "subtitles.endermanoverhaul.entity.cave_enderman.hurt": "동굴 엔더맨이 다침",
    "subtitles.endermanoverhaul.entity.corrupted_pearl.hit": "타락한 진주가 맞음",
    "subtitles.endermanoverhaul.entity.dark_oak_enderman.ambient": (
        "짙은 참나무 엔더맨이 울음"
    ),
    "subtitles.endermanoverhaul.entity.dark_oak_enderman.darkness": (
        "짙은 참나무 엔더맨이 어둠을 드리움"
    ),
    "subtitles.endermanoverhaul.entity.dark_oak_enderman.stare": (
        "짙은 참나무 엔더맨이 소리침"
    ),
    "subtitles.endermanoverhaul.entity.flower_fields_enderman.ambient": (
        "꽃밭 엔더맨이 울음"
    ),
    "subtitles.endermanoverhaul.entity.flower_fields_enderman.death": (
        "꽃밭 엔더맨이 죽음"
    ),
    "subtitles.endermanoverhaul.entity.flower_fields_enderman.hurt": (
        "꽃밭 엔더맨이 다침"
    ),
    "subtitles.endermanoverhaul.entity.icy_pearl.hit": "얼어붙은 진주가 맞음",
    "subtitles.endermanoverhaul.entity.plant_enderman.ambient": "식물 엔더맨이 울음",
    "subtitles.endermanoverhaul.entity.plant_enderman.hurt": "식물 엔더맨이 다침",
    "subtitles.endermanoverhaul.entity.soul_pearl.hit": "영혼 진주가 맞음",
    "subtitles.endermanoverhaul.entity.summoner_pearl.hit": "소환사의 진주가 맞음",
    "subtitles.endermanoverhaul.entity.tall_enderman.ambient": "키 큰 엔더맨이 울음",
    "subtitles.endermanoverhaul.entity.tall_enderman.death": "키 큰 엔더맨이 죽음",
    "subtitles.endermanoverhaul.entity.tall_enderman.stare": "키 큰 엔더맨이 소리침",
    "tag.item.endermanoverhaul.ender_pearls": "엔더 진주",
    "tooltip.endermanoverhaul.ancient_pearl_1": (
        "함께 싸워 줄 우호적 엔더맨을 소환합니다"
    ),
    "tooltip.endermanoverhaul.ancient_pearl_2": (
        "소환한 엔더맨을 웅크린 채 우클릭하면 진주를 회수합니다"
    ),
    "tooltip.endermanoverhaul.ancient_pet": "반려 생물 체력: %.1f",
    "tooltip.endermanoverhaul.bound_to": "연결된 대상: %s",
    "tooltip.endermanoverhaul.bubble_pearl": "중력의 영향을 받지 않는 정밀한 엔더 진주",
    "tooltip.endermanoverhaul.corrupted_blade": "대상을 무작위 위치로 순간이동시킵니다",
    "tooltip.endermanoverhaul.corrupted_pearl": "대상을 무작위 위치로 순간이동시킵니다",
    "tooltip.endermanoverhaul.corrupted_shield": "공격자를 무작위 위치로 순간이동시킵니다",
    "tooltip.endermanoverhaul.crimson_pearl": "순간이동할 때 힘 II를 부여합니다",
    "tooltip.endermanoverhaul.hood": "엔더맨을 화나게 하지 않고 바라볼 수 있습니다",
    "tooltip.endermanoverhaul.icy_pearl": "적중하면 주변 대상을 얼립니다",
    "tooltip.endermanoverhaul.not_bound": "연결되지 않음",
    "tooltip.endermanoverhaul.soul_pearl_1": "웅크린 채 우클릭하여 엔티티와 연결합니다",
    "tooltip.endermanoverhaul.soul_pearl_2": "연결된 엔티티를 대상 위치로 순간이동시킵니다",
    "tooltip.endermanoverhaul.summoner_pearl": "적중하면 주변 대상을 순간이동시킵니다",
    "tooltip.endermanoverhaul.warped_pearl": "순간이동할 때 저항 II를 부여합니다",
}

CREEPER_OVERRIDES = {
    "item.creeperoverhaul.jungle_creeper_spawn_egg": "정글 크리퍼 생성 알",
    "subtitles.creeperoverhaul.entity.ocean.creeper.deflate": (
        "바다 크리퍼의 바람이 빠짐"
    ),
    "gui.creeperoverhaul.cosmetics": "꾸미기",
    "gui.creeperoverhaul.cosmetics.login": "Creeper Overhaul에 로그인",
    "gui.creeperoverhaul.cosmetics.preview_in_game": (
        "꾸미기 요소를 미리 보려면 게임 안에 있어야 합니다."
    ),
}

LIVING_ENTITIES = {
    "elephant": "코끼리",
    "giraffe": "기린",
    "lion": "사자",
    "shark": "상어",
    "penguin": "펭귄",
    "ostrich": "타조",
    "flamingo": "홍학",
    "crab": "게",
    "mantaray": "쥐가오리",
    "raccoon": "라쿤",
    "owl": "올빼미",
    "ancient_blaze": "고대 블레이즈",
    "koala": "코알라",
    "snail": "달팽이",
    "monkey": "원숭이",
    "nether_knight": "네더 기사",
    "shroomie": "슈루미",
    "seahorse": "해마",
    "baby_ender_dragon": "아기 엔더 드래곤",
    "peacock": "공작",
}

LIVING_FIXED = {
    "itemGroup.livingthings.general": "Living Things",
    "item.livingthings.shark_tooth": "상어 이빨",
    "item.livingthings.crab": "생게살",
    "item.livingthings.cooked_crab": "익힌 게살",
    "item.livingthings.crab_shell": "게 껍데기",
    "item.livingthings.ostrich": "생타조고기",
    "item.livingthings.cooked_ostrich": "익힌 타조고기",
    "item.livingthings.banana": "바나나",
    "item.livingthings.elephant": "생코끼리고기",
    "item.livingthings.cooked_elephant": "익힌 코끼리고기",
    "item.livingthings.lion": "생사자고기",
    "item.livingthings.cooked_lion": "익힌 사자고기",
    "item.livingthings.giraffe": "생기린고기",
    "item.livingthings.cooked_giraffe": "익힌 기린고기",
    "item.livingthings.ostrich_egg": "타조 알",
    "item.livingthings.ancient_helmet": "고대 투구",
    "item.livingthings.seahorse_bucket": "해마가 든 양동이",
    "item.livingthings.lexicon": "Living Things 안내서",
    "block.livingthings.ostrich_nest": "타조 둥지",
    "entity.livingthings.thrown_ostrich_egg": "던져진 타조 알",
    "messages.livingthings.nopatchouli.title": "사용할 수 없습니다!",
    "messages.livingthings.nopatchouli.subtitle": "Patchouli 모드가 설치되어 있지 않습니다.",
    "messages.livingthings.nopatchouli.wiki": "모드에 관한 자세한 정보: %s",
}

LIVING_SUBTITLES = {
    "subtitles.livingthings.lion.ambient": "사자가 포효함",
    "subtitles.livingthings.lion.hurt": "사자가 다침",
    "subtitles.livingthings.lion.death": "사자가 죽음",
    "subtitles.livingthings.penguin.ambient": "펭귄이 지저귐",
    "subtitles.livingthings.penguin.hurt": "펭귄이 다침",
    "subtitles.livingthings.penguin.death": "펭귄이 죽음",
    "subtitles.livingthings.elephant.ambient": "코끼리가 나팔 소리를 냄",
    "subtitles.livingthings.elephant.hurt": "코끼리가 다침",
    "subtitles.livingthings.elephant.death": "코끼리가 죽음",
    "subtitles.livingthings.elephant.chest": "코끼리에게 상자가 장착됨",
    "subtitles.livingthings.elephant.saddle": "코끼리에게 안장이 장착됨",
    "subtitles.livingthings.ostrich.egg.cracks": "타조 알이 깨짐",
    "subtitles.livingthings.ostrich.egg.laying": "타조가 알을 낳음",
    "subtitles.livingthings.ostrich.ambient": "타조가 울음",
    "subtitles.livingthings.raccoon.ambient": "라쿤이 울음",
    "subtitles.livingthings.raccoon.hurt": "라쿤이 다침",
    "subtitles.livingthings.raccoon.death": "라쿤이 죽음",
    "subtitles.livingthings.owl.ambient": "올빼미가 울음",
    "subtitles.livingthings.owl.hurt": "올빼미가 다침",
    "subtitles.livingthings.owl.death": "올빼미가 죽음",
    "subtitles.livingthings.owl.fly": "올빼미가 날갯짓함",
    "subtitles.livingthings.ancient_blaze.ambient": "고대 블레이즈가 숨을 쉼",
    "subtitles.livingthings.ancient_blaze.burn": "고대 블레이즈가 타닥거림",
    "subtitles.livingthings.ancient_blaze.death": "고대 블레이즈가 죽음",
    "subtitles.livingthings.ancient_blaze.hurt": "고대 블레이즈가 다침",
    "subtitles.livingthings.ancient_blaze.shoot": "고대 블레이즈가 발사함",
    "subtitles.livingthings.ancient_blaze.spawn": "고대 블레이즈가 풀려남",
    "subtitles.livingthings.ancient_blaze.charge_up": "고대 블레이즈가 힘을 모음",
    "subtitles.livingthings.nether_knight.ambient": "네더 기사가 소리를 냄",
    "subtitles.livingthings.nether_knight.hurt": "네더 기사가 다침",
    "subtitles.livingthings.nether_knight.death": "네더 기사가 죽음",
    "subtitles.livingthings.seahorse.flop": "해마가 퍼덕임",
    "subtitles.livingthings.mantaray.flop": "쥐가오리가 퍼덕임",
    "subtitles.livingthings.baby_ender_dragon.ambient": "아기 엔더 드래곤이 포효함",
    "subtitles.livingthings.baby_ender_dragon.hurt": "아기 엔더 드래곤이 다침",
    "subtitles.livingthings.baby_ender_dragon.death": "아기 엔더 드래곤이 죽음",
    "subtitles.livingthings.baby_ender_dragon.flaps": "아기 엔더 드래곤이 날갯짓함",
    "subtitles.livingthings.baby_ender_dragon.shoot": "아기 엔더 드래곤이 발사함",
    "subtitles.livingthings.ostrich_nest.remove_egg": "둥지에서 타조 알을 꺼냄",
    "subtitles.livingthings.ancient_armor.equip": "고대 방어구가 장착됨",
    "subtitles.livingthings.peacock.ambient": "공작이 울음",
    "subtitles.livingthings.peacock.hurt": "공작이 다침",
    "subtitles.livingthings.peacock.death": "공작이 죽음",
}

VARIANT_NAMES = {
    "gelid": "젤리드",
    "murk": "머크",
    "thicket": "시킷",
    "verdant": "버던트",
}

VARIANT_FIXED = {
    "entity.variantsandventures.gelid": "젤리드",
    "entity.variantsandventures.murk": "머크",
    "entity.variantsandventures.thicket": "시킷",
    "entity.variantsandventures.verdant": "버던트",
    "item_group.variantsandventures.main_tab": "Variants&Ventures",
    "item.variantsandventures.gelid_spawn_egg": "젤리드 생성 알",
    "item.variantsandventures.murk_spawn_egg": "머크 생성 알",
    "item.variantsandventures.thicket_spawn_egg": "시킷 생성 알",
    "item.variantsandventures.verdant_spawn_egg": "버던트 생성 알",
    "subtitles.entity.variantsandventures.gelid.ambient": "젤리드가 신음함",
    "subtitles.entity.variantsandventures.gelid.attack": "젤리드가 공격함",
    "subtitles.entity.variantsandventures.gelid.death": "젤리드가 죽음",
    "subtitles.entity.variantsandventures.gelid.hurt": "젤리드가 다침",
    "subtitles.entity.variantsandventures.murk.ambient": "머크가 뼈 소리를 냄",
    "subtitles.entity.variantsandventures.murk.attack": "머크가 발사함",
    "subtitles.entity.variantsandventures.murk.death": "머크가 죽음",
    "subtitles.entity.variantsandventures.murk.hurt": "머크가 다침",
    "subtitles.entity.variantsandventures.murk.shear": "가위가 딸깍거림",
    "subtitles.entity.variantsandventures.snowball.impact": "눈덩이가 부딪힘",
    "subtitles.entity.variantsandventures.thicket.ambient": "시킷이 신음함",
    "subtitles.entity.variantsandventures.thicket.attack": "시킷이 공격함",
    "subtitles.entity.variantsandventures.thicket.death": "시킷이 죽음",
    "subtitles.entity.variantsandventures.thicket.hurt": "시킷이 다침",
    "subtitles.entity.variantsandventures.verdant.ambient": "버던트가 뼈 소리를 냄",
    "subtitles.entity.variantsandventures.verdant.attack": "버던트가 발사함",
    "subtitles.entity.variantsandventures.verdant.death": "버던트가 죽음",
    "subtitles.entity.variantsandventures.verdant.hurt": "버던트가 다침",
}

VARIANT_CONFIG_STATIC = {
    "variantsandventures": "Variants&Ventures",
    "category.mod_mobs": "모드 몹",
    "category.vanilla_mobs": "바닐라 몹",
    "category.mod_mobs.group.gelid": "젤리드(빙결 좀비)",
    "category.mod_mobs.group.murk": "머크(침몰한 스켈레톤)",
    "category.mod_mobs.group.thicket": "시킷(정글 좀비)",
    "category.mod_mobs.group.verdant": "버던트(정글 스켈레톤)",
    "category.vanilla_mobs.group.stray": "스트레이",
    "category.vanilla_mobs.group.husk": "허스크",
    "category.vanilla_mobs.group.bogged": "보그드",
    "category.vanilla_mobs.group.parched": "파치드",
}

QUEST_CORRECTIONS = {
    "quest.1F31EBF49079F9D3.quest_desc": [
        "Creeper Overhaul은 생물군계마다 서로 다른 크리퍼를 추가합니다. "
        "\\n\\n종류마다 전리품이 다르고, 몇몇은 우호적이기까지 합니다! "
        "\\n\\n그래도 모두 고양이를 무서워합니다..."
    ],
    "quest.1F31EBF49079F9D3.title": "Creeper Overhaul",
    "quest.2BD077EFE77B8EBB.quest_desc": [
        "좀비는 생물군계에 따라 여러 변종으로 생성됩니다. "
        "\\n\\n허스크 - 사막에서 생성됩니다. "
        "\\n드라운드 - 물속에서 생성됩니다. "
        "\\n젤리드 - 추운 생물군계에서 생성됩니다. "
        "\\n시킷 - 정글에서 생성됩니다."
    ],
    "quest.2BD077EFE77B8EBB.title": "좀비 변종",
    "quest.570223A03231DF8C.quest_desc": [
        "Enderman Overhaul은 Creeper Overhaul과 비슷하지만, 이번에는 엔더맨을 "
        "다룹니다! \\n\\n다양한 생물군계에서 저마다 독특한 엔더맨을 만날 수 있습니다. "
        "공격 방식이 다르거나 특별한 진주를 떨어뜨리며, 생김새도 모두 다릅니다!"
    ],
    "quest.570223A03231DF8C.title": "Enderman Overhaul",
    "quest.6827836C8E675A94.quest_desc": [
        "스켈레톤도 좀비처럼 여러 변종이 있습니다! "
        "\\n\\n스트레이 - 추운 생물군계에서 생성됩니다. "
        "\\n보그드 - 늪과 시련의 회당에서 생성됩니다. "
        "\\n머크 - 산호초의 물속에서 생성됩니다. "
        "\\n버던트 - 정글에서 생성됩니다."
    ],
    "quest.6827836C8E675A94.title": "스켈레톤 변종",
    "quest.77FC692AC94D2EEF.title": "&l&9오버월드 현상금:&r&e 크리퍼",
}

RELATED_QUEST_IDS = {
    "1F31EBF49079F9D3",
    "2BD077EFE77B8EBB",
    "570223A03231DF8C",
    "6827836C8E675A94",
    "77FC692AC94D2EEF",
}

ALLOWED_LATIN = {
    "Creeper",
    "Enderman",
    "Living",
    "Mekanism",
    "Overhaul",
    "Patchouli",
    "Things",
    "Variants",
    "Ventures",
}

INTENTIONAL_SAME = {
    "endermanoverhaul": {
        "config.endermanoverhaul.title",
        "itemGroup.endermanoverhaul.main",
    },
    "creeperoverhaul": {"itemGroup.creeperoverhaul.item_group"},
    "livingthings": {"itemGroup.livingthings.general"},
    "variantsandventures": {
        "item_group.variantsandventures.main_tab",
        "yacl3.config.variantsandventures:variantsandventures",
    },
}

GUIDE_INTENTIONAL_SAME = {"", "item.livingthings.lexicon"}

GUIDE_TEXT = {
    "Hostile Mobs": "적대적 몹",
    "Be aware of these mobs, because they might attack you!": (
        "공격할 수 있으니 이 몹들을 조심하세요!"
    ),
    "Items": "아이템",
    "All the items": "모든 아이템을 소개합니다.",
    "Neutral Mobs": "중립적 몹",
    "These mobs will only defend themselves, if you attack them first!": (
        "먼저 공격할 때만 자신을 방어하는 몹입니다!"
    ),
    "Passive Mobs": "비공격적 몹",
    "These mobs will never hurt anyone!": "누구도 공격하지 않는 몹입니다!",
    "Ancient Blaze": "고대 블레이즈",
    "Baby Enderdragon": "아기 엔더 드래곤",
    "Lion": "사자",
    "Nether Knight": "네더 기사",
    "Shark": "상어",
    "Ancient Helmet": "고대 투구",
    "Banana": "바나나",
    "Cooked Crab Meat": "익힌 게살",
    "Cooked Elephant Meat": "익힌 코끼리고기",
    "Cooked Giraffe Meat": "익힌 기린고기",
    "Cooked Lion Meat": "익힌 사자고기",
    "Cooked Ostrich Meat": "익힌 타조고기",
    "Raw Crab Meat": "생게살",
    "Crab Shell": "게 껍데기",
    "Raw Elephant Meat": "생코끼리고기",
    "Raw Giraffe Meat": "생기린고기",
    "Raw Lion Meat": "생사자고기",
    "Raw Ostrich Meat": "생타조고기",
    "Ostrich Egg": "타조 알",
    "Ostrich Nest": "타조 둥지",
    "Bucket of Seahorse": "해마가 든 양동이",
    "Shark Tooth": "상어 이빨",
    "Crab": "게",
    "Elephant": "코끼리",
    "Giraffe": "기린",
    "Monkey": "원숭이",
    "Raccoon": "라쿤",
    "Flamingo": "홍학",
    "Koala": "코알라",
    "Mantaray": "쥐가오리",
    "Ostrich": "타조",
    "Owl": "올빼미",
    "Peacock": "공작",
    "Penguin": "펭귄",
    "Seahorse": "해마",
    "Shroomie": "슈루미",
    "Snail": "달팽이",
    (
        "Another boss from the Nether!$(br2)$(bold)Health: $()125 Hearts$(br)"
        "$(bold)Attack-Damage: $()3 Hearts$(br2)$(bold)Attacks: $()$(li)6 "
        "Large Fireballs$(li)∞ Small Fireballs"
    ): (
        "네더의 또 다른 보스입니다!$(br2)$(bold)체력: $()125하트$(br)"
        "$(bold)공격 피해: $()3하트$(br2)$(bold)공격: $()$(li)대형 화염구 "
        "6개$(li)∞개의 소형 화염구"
    ),
    "can be created with a ritual (next page)": "의식을 통해 만들 수 있습니다(다음 쪽).",
    (
        "$(bold)Summoning$()$(br2)To summon the ancient blaze you need to "
        "place a$(br)Jack o'Lantern on top of two glowstone blocks.$(br2)Once "
        "the ancient blaze is summoned it will be invulnerable until it charged "
        "up it's 6 large fireballs.$(br2)The amount of large fireballs can be "
        "seen by the amount of sticks flying around."
    ): (
        "$(bold)소환$()$(br2)고대 블레이즈를 소환하려면 발광석 블록 두 개 "
        "위에$(br)잭오랜턴을 놓으세요.$(br2)소환된 고대 블레이즈는 대형 화염구 "
        "6개를 모두 충전할 때까지 무적입니다.$(br2)주변을 날아다니는 막대 수로 "
        "충전된 대형 화염구 수를 알 수 있습니다."
    ),
    (
        "$(bold)Death$()$(br2)When dying, it will drop it's helmet.$(br2)"
        "The ancient blaze will spawn 4 normal blazes to revenge it's death."
    ): (
        "$(bold)죽음$()$(br2)죽을 때 투구를 떨어뜨립니다.$(br2)고대 "
        "블레이즈가 죽으면 복수하려는 일반 블레이즈 4마리가 생성됩니다."
    ),
    (
        "A semi dangerous animal that has a weakness for chorus fruits!$(br)"
        "Tamed baby enderdragons will follow you around.$(br2)$(bold)Health: "
        "$()5 Hearts$(br2)$(bold)Taming Items: $()$(li)Chorus Fruit"
    ): (
        "후렴과를 무척 좋아하는 제법 위험한 동물입니다!$(br)길들인 아기 엔더 "
        "드래곤은 플레이어를 따라다닙니다.$(br2)$(bold)체력: $()5하트$(br2)"
        "$(bold)길들이기 아이템: $()$(li)후렴과"
    ),
    "Can be hatched by placing a dragon egg on top of a purpur pillar. ": (
        "퍼퍼 기둥 위에 드래곤 알을 놓으면 부화시킬 수 있습니다. "
    ),
    (
        "A dangerous animal!$(br2)$(bold)Health: $()10 Hearts$(br)$(bold)"
        "Attack-Damage: $()2.5 Hearts$(br2)$(bold)Breeding Items: $()$(li)"
        "Raw Beef$(li)Raw Chicken$(li)Raw Rabbit"
    ): (
        "위험한 동물입니다!$(br2)$(bold)체력: $()10하트$(br)$(bold)공격 "
        "피해: $()2.5하트$(br2)$(bold)번식 아이템: $()$(li)익히지 않은 "
        "소고기$(li)익히지 않은 닭고기$(li)익히지 않은 토끼고기"
    ),
    "Can be found in all $(bold)Savanna$() biomes.": (
        "모든 $(bold)사바나$() 생물군계에서 찾을 수 있습니다."
    ),
    "Deadly fighter that is guarding the nether fortress.": (
        "네더 요새를 지키는 치명적인 전사입니다."
    ),
    (
        "A fast water creature, that will hunt down players!$(br2)$(bold)Health: "
        "$()11 Hearts$(br)$(bold)Attack-Damage: $()3 Hearts$(br2)$(bold)"
        "Drops:$()$(li)0-3 Shark Tooth$(li)1-2 Raw Cod"
    ): (
        "플레이어를 추격하는 빠른 수중 생물입니다!$(br2)$(bold)체력: $()"
        "11하트$(br)$(bold)공격 피해: $()3하트$(br2)$(bold)전리품:$()"
        "$(li)상어 이빨 0-3개$(li)생대구 1-2개"
    ),
    "Can be found in all $(bold)Ocean$() biomes.": (
        "모든 $(bold)바다$() 생물군계에서 찾을 수 있습니다."
    ),
    "$(br)$(bold)Obtaining:$()$(br)Can be dropped by an Ancient Blaze.": (
        "$(br)$(bold)획득:$()$(br)고대 블레이즈가 떨어뜨릴 수 있습니다."
    ),
    "$(br)$(bold)Usage:$()$(li)adds Fire Resistance Effect when worn": (
        "$(br)$(bold)용도:$()$(li)착용하면 화염 저항 효과를 부여합니다"
    ),
    "$(br)$(bold)Obtaining:$()$(br)can be obtained by breaking jungle leaves": (
        "$(br)$(bold)획득:$()$(br)정글 나뭇잎을 부수면 얻을 수 있습니다"
    ),
    "$(br)$(bold)Usage:$()$(li)can be eaten": (
        "$(br)$(bold)용도:$()$(li)먹을 수 있습니다"
    ),
    "$(br)$(bold)Obtaining:$()$(br)can be obtained by smelting Raw Crab": (
        "$(br)$(bold)획득:$()$(br)생게살을 제련하면 얻을 수 있습니다"
    ),
    (
        "$(br)$(bold)Obtaining:$()$(br)can be obtained by smelting Raw " "Elephant Meat"
    ): "$(br)$(bold)획득:$()$(br)생코끼리고기를 제련하면 얻을 수 있습니다",
    (
        "$(br)$(bold)Obtaining:$()$(br)can be obtained by smelting Raw " "Giraffe Meat"
    ): "$(br)$(bold)획득:$()$(br)생기린고기를 제련하면 얻을 수 있습니다",
    (
        "$(br)$(bold)Obtaining:$()$(br)can be obtained by smelting Raw Lion Meat"
    ): "$(br)$(bold)획득:$()$(br)생사자고기를 제련하면 얻을 수 있습니다",
    (
        "$(br)$(bold)Obtaining:$()$(br)can be obtained by smelting Raw " "Ostrich Meat"
    ): "$(br)$(bold)획득:$()$(br)생타조고기를 제련하면 얻을 수 있습니다",
    "$(br)$(bold)Obtaining:$()$(br)can be dropped by Crabs": (
        "$(br)$(bold)획득:$()$(br)게가 떨어뜨릴 수 있습니다"
    ),
    (
        "$(br)$(bold)Usage:$()$(li)can be eaten$(li)can be smelted to Cooked "
        "Crab Meat"
    ): (
        "$(br)$(bold)용도:$()$(li)먹을 수 있습니다$(li)제련하여 익힌 게살을 "
        "만들 수 있습니다"
    ),
    "$(br)$(bold)Usage:$()$(li)no known usages": (
        "$(br)$(bold)용도:$()$(li)알려진 용도가 없습니다"
    ),
    "$(br)$(bold)Obtaining:$()$(br)can be dropped by Elephants": (
        "$(br)$(bold)획득:$()$(br)코끼리가 떨어뜨릴 수 있습니다"
    ),
    (
        "$(br)$(bold)Usage:$()$(li)can be eaten$(li)can be smelted to Cooked "
        "Elephant Meat"
    ): (
        "$(br)$(bold)용도:$()$(li)먹을 수 있습니다$(li)제련하여 익힌 "
        "코끼리고기를 만들 수 있습니다"
    ),
    "$(br)$(bold)Obtaining:$()$(br)can be dropped by Giraffes": (
        "$(br)$(bold)획득:$()$(br)기린이 떨어뜨릴 수 있습니다"
    ),
    (
        "$(br)$(bold)Usage:$()$(li)can be eaten$(li)can be smelted to Cooked "
        "Giraffe Meat"
    ): (
        "$(br)$(bold)용도:$()$(li)먹을 수 있습니다$(li)제련하여 익힌 기린고기를 "
        "만들 수 있습니다"
    ),
    "$(br)$(bold)Obtaining:$()$(br)can be dropped by Lions": (
        "$(br)$(bold)획득:$()$(br)사자가 떨어뜨릴 수 있습니다"
    ),
    (
        "$(br)$(bold)Usage:$()$(li)can be eaten$(li)can be smelted to Cooked "
        "Lion Meat"
    ): (
        "$(br)$(bold)용도:$()$(li)먹을 수 있습니다$(li)제련하여 익힌 사자고기를 "
        "만들 수 있습니다"
    ),
    "$(br)$(bold)Obtaining:$()$(br)can be dropped by Ostrichs": (
        "$(br)$(bold)획득:$()$(br)타조가 떨어뜨릴 수 있습니다"
    ),
    (
        "$(br)$(bold)Usage:$()$(li)can be eaten$(li)can be smelted to Cooked "
        "Ostrich Meat"
    ): (
        "$(br)$(bold)용도:$()$(li)먹을 수 있습니다$(li)제련하여 익힌 타조고기를 "
        "만들 수 있습니다"
    ),
    (
        "$(br)$(bold)Obtaining:$()$(br)If an ostrich nest contains an egg and "
        "a player right-clicks it, the egg can be dropped$(br2)Can be dropped by "
        "an ostrich that was about do build its nest"
    ): (
        "$(br)$(bold)획득:$()$(br)알이 든 타조 둥지를 우클릭하면 알을 꺼낼 "
        "수 있습니다$(br2)둥지를 만들려던 타조가 떨어뜨릴 수도 있습니다"
    ),
    (
        "$(br)$(bold)Usage:$()$(br)can be placed in an ostrich nest, to hatch "
        "a baby ostrich"
    ): (
        "$(br)$(bold)용도:$()$(br)타조 둥지에 놓아 아기 타조를 부화시킬 수 " "있습니다"
    ),
    (
        "$(br)$(bold)Obtaining:$()$(br)If mined without a silk-touch tool the "
        "nest will fall apart and you get a few sticks."
    ): (
        "$(br)$(bold)획득:$()$(br)섬세한 손길 도구 없이 캐면 둥지가 부서지고 "
        "막대기 몇 개를 얻습니다."
    ),
    (
        "$(br)$(bold)Usage:$()$(br)can be placed$(br)an ostrichs might lay an "
        "egg into it"
    ): (
        "$(br)$(bold)용도:$()$(br)설치할 수 있습니다$(br)타조가 안에 알을 낳을 "
        "수 있습니다"
    ),
    (
        "$(br)$(bold)Obtaining:$()$(br)right-click a seahorse with a water "
        "bucket to capture it in a bucket"
    ): (
        "$(br)$(bold)획득:$()$(br)물 양동이로 해마를 우클릭하면 양동이에 담을 "
        "수 있습니다"
    ),
    "$(br)$(bold)Obtaining:$()$(br)can be dropped by Sharks": (
        "$(br)$(bold)획득:$()$(br)상어가 떨어뜨릴 수 있습니다"
    ),
    (
        "$(br)$(bold)Usage:$()$(li)can be used for arrows$(li)can be crafted "
        "to bone meal"
    ): (
        "$(br)$(bold)용도:$()$(li)화살 재료로 사용할 수 있습니다$(li)뼛가루로 "
        "제작할 수 있습니다"
    ),
    (
        "$(br2)$(bold)Health: $()4 Hearts$(br)$(bold)Attack-Damage: $()0.5 "
        "Heart$(br2)$(bold)Breeding Items: $()$(li)Raw Cod$(br2)$(bold)Drops:"
        "$()$(li)1-2 Raw Crab$(li)0-1 Crab Shell"
    ): (
        "$(br2)$(bold)체력: $()4하트$(br)$(bold)공격 피해: $()0.5하트"
        "$(br2)$(bold)번식 아이템: $()$(li)생대구$(br2)$(bold)전리품:$()"
        "$(li)생게살 1-2개$(li)게 껍데기 0-1개"
    ),
    "Can be found in $(bold)Swamp$() and $(bold)Beach$() biomes.": (
        "$(bold)늪$()과 $(bold)해변$() 생물군계에서 찾을 수 있습니다."
    ),
    (
        "Huge animals that will be angry when you attack them!$(br2)$(bold)"
        "Health: $()30 Hearts$(br)$(bold)Attack-Damage: $()3.5 Hearts$(br2)"
        "$(bold)Breeding Items: $()$(li)Wheat (only tamed ones)$(br2)Can be "
        "tamed with apples. Tamed Elephants can be equipped with a saddle, and "
        "then with a chest."
    ): (
        "공격하면 화를 내는 거대한 동물입니다!$(br2)$(bold)체력: $()30하트"
        "$(br)$(bold)공격 피해: $()3.5하트$(br2)$(bold)번식 아이템: $()"
        "$(li)밀(길들인 개체만)$(br2)사과로 길들일 수 있습니다. 길들인 코끼리에는 "
        "안장을 장착한 뒤 상자도 장착할 수 있습니다."
    ),
    (
        "Huge animals that will be angry when you attack them!$(br2)$(bold)"
        "Health: $()15 Hearts$(br)$(bold)Attack-Damage: $()2 Hearts$(br2)"
        "$(bold)Breeding Items: $()$(li)Wheat"
    ): (
        "공격하면 화를 내는 거대한 동물입니다!$(br2)$(bold)체력: $()15하트"
        "$(br)$(bold)공격 피해: $()2하트$(br2)$(bold)번식 아이템: $()"
        "$(li)밀"
    ),
    (
        "$(br2)$(bold)Health: $()3 Hearts$(br)$(bold)Attack-Damage: $()1.5 "
        "Heart$(br2)$(bold)Breeding Items: $()$(li)Apples$(li)Bananas$(br2)"
        "$(bold)Drops:$()$(li)1-2 Leather$(li)0-1 Banana"
    ): (
        "$(br2)$(bold)체력: $()3하트$(br)$(bold)공격 피해: $()1.5하트"
        "$(br2)$(bold)번식 아이템: $()$(li)사과$(li)바나나$(br2)$(bold)"
        "전리품:$()$(li)가죽 1-2개$(li)바나나 0-1개"
    ),
    "Can be found in all $(bold)Jungle$() biomes.": (
        "모든 $(bold)정글$() 생물군계에서 찾을 수 있습니다."
    ),
    (
        "Medium-sized mammals that clean their food thoroughly before eating "
        "it.$(br2)$(bold)Health: $()5 Hearts$(br)$(bold)Attack-Damage: $()1 "
        "Hearts$(br2)$(bold)Breeding Items: $()$(li)Wheat$(li)Apple$(li)Carrot"
        "$(li)Potato$(li)Beetroot"
    ): (
        "먹기 전에 먹이를 깨끗이 씻는 중형 포유류입니다.$(br2)$(bold)체력: "
        "$()5하트$(br)$(bold)공격 피해: $()1하트$(br2)$(bold)번식 아이템: "
        "$()$(li)밀$(li)사과$(li)당근$(li)감자$(li)비트"
    ),
    "Can be found in $(bold)Forest$() and $(bold)Plain$() biomes.": (
        "$(bold)숲$()과 $(bold)평원$() 생물군계에서 찾을 수 있습니다."
    ),
    (
        "Pink bird that stands most of the time on one leg.$(br2)$(bold)Health: "
        "$()5 Hearts$(br2)$(bold)Breeding Items: $()$(li)Raw Salmon$(li)Raw Cod"
    ): (
        "대부분 한쪽 다리로 서 있는 분홍색 새입니다.$(br2)$(bold)체력: $()"
        "5하트$(br2)$(bold)번식 아이템: $()$(li)생연어$(li)생대구"
    ),
    "Can be found in $(bold)Swamps$() and at $(bold)Rivers$().": (
        "$(bold)늪$()과 $(bold)강$()에서 찾을 수 있습니다."
    ),
    (
        "Very slow animal, that will sleep most of the day.$(br2)$(bold)Health: "
        "$()5 Hearts$(br2)$(bold)Breeding Items: $()$(li)Wheat$(br2)$(bold)"
        "Drops:$()$(li)1-2 Leather"
    ): (
        "하루 대부분을 자며 보내는 매우 느린 동물입니다.$(br2)$(bold)체력: "
        "$()5하트$(br2)$(bold)번식 아이템: $()$(li)밀$(br2)$(bold)전리품:"
        "$()$(li)가죽 1-2개"
    ),
    (
        "Aquatic animal that looks like it's flying through the sea.$(br2)"
        "$(bold)Health: $()5 Hearts$(br2)$(bold)Drops:$()$(li)1-2 Raw Cod"
    ): (
        "바닷속을 날아다니는 것처럼 보이는 수생 동물입니다.$(br2)$(bold)체력: "
        "$()5하트$(br2)$(bold)전리품:$()$(li)생대구 1-2개"
    ),
    (
        "Fast running bird that can be ridden without a saddle.$(br2)$(bold)"
        "Health: $()10 Hearts$(br2)$(bold)Breeding Items: $()$(li)Wheat"
        "$(br2)$(bold)Breeding Behavior:$()$(br)    Next Page ..."
    ): (
        "안장 없이 탈 수 있는 빠른 새입니다.$(br2)$(bold)체력: $()10하트"
        "$(br2)$(bold)번식 아이템: $()$(li)밀$(br2)$(bold)번식 행동:$()"
        "$(br)    다음 쪽..."
    ),
    (
        "$(bold)Breeding Behavior:$()$(br2)After two ostrichs fell in love, "
        "one of them will search the nearest sand-block to build a nest on it."
        "$(br)If there is already an empty nest nearby, the ostrich will choose "
        "this to lay the egg.$(br)The egg will need some time, before an ostrich "
        "baby will hatch."
    ): (
        "$(bold)번식 행동:$()$(br2)타조 두 마리가 사랑에 빠지면 한 마리가 "
        "가장 가까운 모래 블록을 찾아 그 위에 둥지를 만듭니다.$(br)주변에 빈 "
        "둥지가 있으면 그곳에 알을 낳습니다.$(br)시간이 지나면 알에서 아기 타조가 "
        "부화합니다."
    ),
    "An ostrich laying an egg into its nest.": "타조가 둥지에 알을 낳는 모습입니다.",
    (
        "Nocturnal bird that can spawn in different color variations.$(br2)"
        "$(bold)Health: $()5 Hearts$(br2)$(bold)Breeding Items: $()$(li)Melon "
        "Seeds$(li)Pumpkin Seeds$(li)Beetroot Seeds$(br2)$(bold)Taming Item: "
        "$()$(li)Wheat Seeds"
    ): (
        "여러 색상으로 생성되는 야행성 새입니다.$(br2)$(bold)체력: $()5하트"
        "$(br2)$(bold)번식 아이템: $()$(li)수박씨$(li)호박씨$(li)비트 씨앗"
        "$(br2)$(bold)길들이기 아이템: $()$(li)밀 씨앗"
    ),
    "Can be found in $(bold)Forest$() biomes.": (
        "$(bold)숲$() 생물군계에서 찾을 수 있습니다."
    ),
    (
        "Peacocks are a type of large pheasant known for their beautiful colored "
        "feathers.$(br2)$(bold)Health: $()4 Hearts$(br2)$(bold)Breeding Items: "
        "$()$(li)Wheat"
    ): (
        "공작은 아름다운 색의 깃털로 유명한 대형 꿩의 한 종류입니다.$(br2)"
        "$(bold)체력: $()4하트$(br2)$(bold)번식 아이템: $()$(li)밀"
    ),
    "Can be found in $(bold)Savannas$() and in $(bold)Jungles$().": (
        "$(bold)사바나$()와 $(bold)정글$()에서 찾을 수 있습니다."
    ),
    (
        "A cute animal that is very talkative.$(br2)$(bold)Health: $()5 Hearts"
        "$(br2)$(bold)Breeding Items: $()$(li)Raw Salmon$(li)Raw Cod$(li)"
        "Pufferfish"
    ): (
        "수다스러운 귀여운 동물입니다.$(br2)$(bold)체력: $()5하트$(br2)"
        "$(bold)번식 아이템: $()$(li)생연어$(li)생대구$(li)복어"
    ),
    "Can be found in $(bold)Snowy$() biomes.": (
        "$(bold)눈 덮인$() 생물군계에서 찾을 수 있습니다."
    ),
    "Colorful animal that wanders through the ocean in groups.$(br2)$(bold)Health: $()2 Hearts": (
        "무리를 지어 바다를 돌아다니는 화려한 동물입니다.$(br2)$(bold)체력: $()2하트"
    ),
    "Can be found in $(bold)Warm$() and $(bold)Luke Warm Oceans$().": (
        "$(bold)따뜻한 바다$()와 $(bold)미지근한 바다$()에서 찾을 수 있습니다."
    ),
    (
        "Helpful animal that will plant at least one mushroom when you give them "
        "one.$(br2)$(bold)Health: $()5 Hearts$(br2)$(bold)Breeding Items: $()"
        "$(li)Wheat$(br2)$(bold)Drops:$()$(li)1-2 Red Mushroom$(br)    --- or "
        "---$(li)1-2 Brown Mushroom"
    ): (
        "버섯을 주면 적어도 하나를 심어 주는 유용한 동물입니다.$(br2)$(bold)"
        "체력: $()5하트$(br2)$(bold)번식 아이템: $()$(li)밀$(br2)$(bold)"
        "전리품:$()$(li)빨간색 버섯 1-2개$(br)    --- 또는 ---$(li)갈색 버섯 "
        "1-2개"
    ),
    "Can be found in all $(bold)Mushroom Fields$().": (
        "모든 $(bold)버섯 들판$()에서 찾을 수 있습니다."
    ),
    (
        "$(br2)$(bold)Health: $()2 Hearts$(br2)$(bold)Breeding Items: $()"
        "$(li)Carrots$(li)Apples$(br2)can be recolored by (sneak-)rightclicking "
        "the snail with any dye$(br2)$(bold)Drops:$()$(li)1-2 Slime Balls"
    ): (
        "$(br2)$(bold)체력: $()2하트$(br2)$(bold)번식 아이템: $()$(li)"
        "당근$(li)사과$(br2)염료로 달팽이를 (웅크린 채) 우클릭하면 색을 바꿀 수 "
        "있습니다$(br2)$(bold)전리품:$()$(li)슬라임볼 1-2개"
    ),
    (
        "Can be found in nearly all various biomes like $(bold)Forests$(), "
        "$(bold)Swamps$() or $(bold)Plains$()."
    ): (
        "$(bold)숲$(), $(bold)늪$(), $(bold)평원$()을 비롯한 거의 모든 "
        "생물군계에서 찾을 수 있습니다."
    ),
    "This book holds the knowledge about the added mobs and items": (
        "이 책에는 추가된 몹과 아이템에 관한 지식이 담겨 있습니다."
    ),
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


def read_jar_language(
    jar: Path, namespace: str, locale: str = "en_us"
) -> dict[str, object]:
    """JAR의 언어 파일을 읽어요."""
    internal = f"assets/{namespace}/lang/{locale}.json"
    with ZipFile(jar) as archive:
        if internal not in archive.namelist():
            return {}
        value = json.loads(archive.read(internal))
    if not isinstance(value, dict):
        raise TypeError(f"JAR 언어 파일이 객체가 아니에요: {jar.name}:{internal}")
    return value


def ordered_translation(
    namespace: str,
    english: dict[str, object],
    translated: dict[str, str],
) -> dict[str, object]:
    """번역 키가 영어 원문과 정확히 같은지 확인하고 원문 순서로 정렬해요."""
    missing = sorted(set(english) - set(translated))
    extra = sorted(set(translated) - set(english))
    if missing or extra:
        raise ValueError(f"{namespace} 번역 키 불일치: 누락={missing}, 초과={extra}")
    return {key: translated[key] for key in english}


def enderman_translations(english: dict[str, object]) -> dict[str, object]:
    """Enderman Overhaul 전체 번역을 만들어요."""
    translated = dict(ENDERMAN_FIXED)
    for identifier, biome in ENDERMAN_BIOMES.items():
        camel = "".join(part.capitalize() for part in identifier.split("_"))
        translated[f"config.endermanoverhaul.spawn{camel}Enderman"] = (
            f"{biome} 엔더맨 생성"
        )
        translated[f"entity.endermanoverhaul.{identifier}_enderman"] = f"{biome} 엔더맨"
        translated[f"item.endermanoverhaul.{identifier}_enderman_spawn_egg"] = (
            f"{biome} 엔더맨 생성 알"
        )
    return ordered_translation("endermanoverhaul", english, translated)


def creeper_translations(
    english: dict[str, object], candidate: dict[str, object]
) -> dict[str, object]:
    """Creeper Overhaul 기존 후보 전체를 검수한 뒤 교정값을 반영해요."""
    translated = {
        key: value for key, value in candidate.items() if isinstance(value, str)
    }
    translated.update(CREEPER_OVERRIDES)
    return ordered_translation("creeperoverhaul", english, translated)


def living_translations(english: dict[str, object]) -> dict[str, object]:
    """Living Things 전체 번역을 만들어요."""
    translated = dict(LIVING_FIXED)
    translated.update(LIVING_SUBTITLES)
    for identifier, name in LIVING_ENTITIES.items():
        translated[f"entity.livingthings.{identifier}"] = name
        translated[f"item.livingthings.{identifier}_spawn_egg"] = f"{name} 생성 알"
    return ordered_translation("livingthings", english, translated)


def korean_instrumental(value: str) -> str:
    """한국어 이름에 자연스러운 '로/으로' 조사를 붙여요."""
    codepoint = ord(value[-1]) - 0xAC00
    if 0 <= codepoint <= 0xD7A3 - 0xAC00:
        final = codepoint % 28
        return value + ("으로" if final not in {0, 8} else "로")
    return value + "로"


def add_full_variant_config(
    translated: dict[str, str],
    stem: str,
    name: str,
    subject: str,
    topic: str,
    base: str,
    biome: str,
) -> None:
    """모드 몹 하나의 자연 생성·던전·시련의 회당 설정을 추가해요."""
    lower = stem[0].lower() + stem[1:]
    translated[f"enable{stem}"] = f"{name} 활성화"
    translated[f"enable{stem}Spawns"] = f"{name} 자연 생성 활성화"
    translated[f"enable{stem}Spawns.desc"] = (
        f"활성화하면 {biome}에서 {base} 대신 {subject} 생성될 수 있습니다."
    )
    translated[f"{lower}SpawnChance"] = f"{name} 생성 확률"
    translated[f"{lower}SpawnChance.desc"] = (
        f"{name} 생성 확률입니다. 예를 들어 80%라면 {biome}에서 생성되는 모든 "
        f"{base}의 80%가 {korean_instrumental(name)} 바뀝니다."
    )
    translated[f"{lower}MinimumYLevel"] = f"{name} 생성 최소 Y 좌표"
    translated[f"{lower}MinimumYLevel.desc"] = (
        f"{name} 생성 최소 Y 좌표입니다. 예를 들어 62라면 바다 높이보다 위에서만 "
        f"{subject} 생성됩니다."
    )
    translated[f"enable{stem}Spawners"] = f"던전의 {name} 생성기 활성화"
    translated[f"enable{stem}Spawners.desc"] = (
        f"활성화하면 {biome}의 던전에서 {base} 생성기 대신 {name} 생성기가 나타날 "
        "수 있습니다."
    )
    translated[f"{lower}SpawnerChance"] = f"던전의 {name} 생성기 확률"
    translated[f"{lower}SpawnerChance.desc"] = (
        f"던전의 {name} 생성기 확률입니다. 예를 들어 80%라면 {biome}의 모든 "
        f"{base} 생성기 중 80%가 {name} 생성기로 바뀝니다."
    )
    translated[f"enable{stem}SpawnersInTrialChambers"] = (
        f"시련의 회당의 {name} 생성기 활성화"
    )
    translated[f"enable{stem}SpawnersInTrialChambers.desc"] = (
        f"활성화하면 시련의 회당 생성기에 {topic} 추가될 수 있습니다."
    )


def add_better_vanilla_config(
    translated: dict[str, str],
    stem: str,
    name: str,
    subject: str,
    base: str,
    biome: str,
) -> None:
    """바닐라 계열 몹 하나의 개선된 자연 생성·던전 설정을 추가해요."""
    lower = stem[0].lower() + stem[1:]
    translated[f"enableBetter{stem}Spawns"] = f"개선된 {name} 자연 생성 활성화"
    translated[f"enableBetter{stem}Spawns.desc"] = (
        f"활성화하면 {biome}에서 {base} 대신 {subject} 생성될 수 있습니다."
    )
    translated[f"{lower}SpawnChance"] = f"{name} 생성 확률"
    translated[f"{lower}SpawnChance.desc"] = (
        f"{name} 생성 확률입니다. 예를 들어 80%라면 {biome}에서 생성되는 모든 "
        f"{base}의 80%가 {korean_instrumental(name)} 바뀝니다."
    )
    translated[f"{lower}MinimumYLevel"] = f"{name} 생성 최소 Y 좌표"
    translated[f"{lower}MinimumYLevel.desc"] = (
        f"{name} 생성 최소 Y 좌표입니다. 예를 들어 62라면 바다 높이보다 위에서만 "
        f"{subject} 생성됩니다."
    )
    translated[f"enable{stem}Spawners"] = f"던전의 {name} 생성기 활성화"
    translated[f"enable{stem}Spawners.desc"] = (
        f"활성화하면 {biome}의 던전에서 {base} 생성기 대신 {name} 생성기가 나타날 "
        "수 있습니다."
    )
    translated[f"{lower}SpawnerChance"] = f"던전의 {name} 생성기 확률"
    translated[f"{lower}SpawnerChance.desc"] = (
        f"던전의 {name} 생성기 확률입니다. 예를 들어 80%라면 {biome}의 모든 "
        f"{base} 생성기 중 80%가 {name} 생성기로 바뀝니다."
    )


def variants_translations(english: dict[str, object]) -> dict[str, object]:
    """Variants & Ventures 전체 번역을 만들어요."""
    translated = dict(VARIANT_FIXED)
    prefix = "yacl3.config.variantsandventures:"
    translated.update(
        {
            prefix
            + (
                key if key == "variantsandventures" else "variantsandventures." + key
            ): value
            for key, value in VARIANT_CONFIG_STATIC.items()
        }
    )
    config: dict[str, str] = {}
    add_full_variant_config(
        config, "Gelid", "젤리드", "젤리드가", "젤리드가", "좀비", "추운 생물군계"
    )
    config["enableMurk"] = "머크 활성화"
    config["enableMurkSpawns"] = "머크 자연 생성 활성화"
    config["enableMurkSpawns.desc"] = (
        "활성화하면 따뜻한 바다 생물군계에서 머크가 생성될 수 있습니다."
    )
    config["enableMurkSpawnersInTrialChambers"] = "시련의 회당의 머크 생성기 활성화"
    config["enableMurkSpawnersInTrialChambers.desc"] = (
        "활성화하면 시련의 회당 생성기에 머크가 추가될 수 있습니다."
    )
    add_full_variant_config(
        config, "Thicket", "시킷", "시킷이", "시킷이", "좀비", "정글 생물군계"
    )
    add_full_variant_config(
        config,
        "Verdant",
        "버던트",
        "버던트가",
        "버던트가",
        "스켈레톤",
        "정글 생물군계",
    )
    add_better_vanilla_config(
        config, "Stray", "스트레이", "스트레이가", "스켈레톤", "추운 생물군계"
    )
    add_better_vanilla_config(
        config, "Husk", "허스크", "허스크가", "좀비", "사막 생물군계"
    )
    add_better_vanilla_config(
        config, "Bogged", "보그드", "보그드가", "스켈레톤", "늪 생물군계"
    )
    add_better_vanilla_config(
        config, "Parched", "파치드", "파치드가", "스켈레톤", "사막 생물군계"
    )
    translated.update(
        {prefix + f"variantsandventures.{key}": value for key, value in config.items()}
    )
    return ordered_translation("variantsandventures", english, translated)


def translated_guide_value(
    value: object,
    path: str,
    seen: list[dict[str, str]],
    field: str | None = None,
) -> object:
    """Patchouli JSON의 사용자 표시 필드만 재귀적으로 번역해요."""
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            result[key] = translated_guide_value(child, child_path, seen, key)
        return result
    if isinstance(value, list):
        return [
            translated_guide_value(child, f"{path}[{index}]", seen, field)
            for index, child in enumerate(value)
        ]
    if isinstance(value, str) and field in VISIBLE_FIELDS:
        if value in GUIDE_INTENTIONAL_SAME:
            target = value
            status = "intentional_same"
        elif value in GUIDE_TEXT:
            target = GUIDE_TEXT[value]
            status = "translated"
        else:
            raise ValueError(f"안내서 번역이 없어요: {path} -> {value!r}")
        seen.append({"path": path, "source": value, "target": target, "status": status})
        return target
    return deepcopy(value)


def prepare() -> dict[str, object]:
    """현재 JAR 영어 원문과 기존 한국어 후보를 작업 폴더에 기록해요."""
    instance = resolve_source_root()
    rows = []
    total = 0
    living_jar = None
    for namespace, pattern in NAMESPACES.items():
        jar = source_jar(instance, pattern)
        english = read_jar_language(jar, namespace)
        bundled_korean = read_jar_language(jar, namespace, "ko_kr")
        write_json(WORK_ROOT / namespace / "en_us.json", english)
        if bundled_korean:
            write_json(WORK_ROOT / namespace / "bundled_ko_kr.json", bundled_korean)
        rows.append(
            {
                "namespace": namespace,
                "jar": jar.name,
                "jar_size": jar.stat().st_size,
                "jar_mtime_ns": jar.stat().st_mtime_ns,
                "english_keys": len(english),
                "bundled_korean_keys": len(bundled_korean),
            }
        )
        total += len(english)
        if namespace == "livingthings":
            living_jar = jar
    if living_jar is None:
        raise FileNotFoundError("Living Things JAR을 찾지 못했어요")
    guide_files = []
    with ZipFile(living_jar) as archive:
        internal_files = sorted(
            name
            for name in archive.namelist()
            if name.startswith(GUIDE_SOURCE_ROOT + "/") and name.endswith(".json")
        )
        for internal in internal_files:
            relative = Path(internal).relative_to(GUIDE_SOURCE_ROOT)
            source = json.loads(archive.read(internal))
            write_json(WORK_ROOT / "guide/en_us" / relative, source)
            guide_files.append(relative.as_posix())
        book = json.loads(archive.read(BOOK_SOURCE))
    write_json(WORK_ROOT / "guide/book_en_us.json", book)
    report = {
        "family": FAMILY,
        "namespaces": rows,
        "english_keys": total,
        "guide_files": guide_files,
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", report)
    return report


def build() -> dict[str, object]:
    """언어·안내서·FTB Quests 산출물을 만들어요."""
    english_by_namespace = {
        namespace: load_json(WORK_ROOT / namespace / "en_us.json")
        for namespace in NAMESPACES
    }
    creeper_candidate = load_json(WORK_ROOT / "creeperoverhaul/bundled_ko_kr.json")
    translated_by_namespace = {
        "endermanoverhaul": enderman_translations(
            english_by_namespace["endermanoverhaul"]
        ),
        "creeperoverhaul": creeper_translations(
            english_by_namespace["creeperoverhaul"], creeper_candidate
        ),
        "livingthings": living_translations(english_by_namespace["livingthings"]),
        "variantsandventures": variants_translations(
            english_by_namespace["variantsandventures"]
        ),
    }
    source_rows = {}
    reused = 0
    corrected = 0
    new = 0
    for namespace, translated in translated_by_namespace.items():
        candidate = creeper_candidate if namespace == "creeperoverhaul" else {}
        candidate_sources = {}
        for key, value in translated.items():
            if key not in candidate:
                status = "new_translation"
                new += 1
            elif candidate[key] == value:
                status = "bundled_korean_reused_after_review"
                reused += 1
            else:
                status = "bundled_korean_corrected"
                corrected += 1
            candidate_sources[key] = status
        source_rows[namespace] = Counter(candidate_sources.values())
        write_json(WORK_ROOT / namespace / "ko_kr.json", translated)
        write_json(
            RESOURCEPACK_ROOT / f"assets/{namespace}/lang/ko_kr.json", translated
        )
        write_json(WORK_ROOT / namespace / "candidate_sources.json", candidate_sources)

    guide_rows: list[dict[str, str]] = []
    guide_files = []
    for source_path in sorted((WORK_ROOT / "guide/en_us").rglob("*.json")):
        relative = source_path.relative_to(WORK_ROOT / "guide/en_us")
        source = load_json(source_path)
        translated = translated_guide_value(source, relative.as_posix(), guide_rows)
        write_json(WORK_ROOT / "guide/ko_kr" / relative, translated)
        write_json(GUIDE_OUTPUT_ROOT / relative, translated)
        guide_files.append(relative.as_posix())
    source_book = load_json(WORK_ROOT / "guide/book_en_us.json")
    translated_book = translated_guide_value(source_book, "book.json", guide_rows)
    write_json(WORK_ROOT / "guide/book_ko_kr.json", translated_book)
    write_json(BOOK_OUTPUT, translated_book)
    write_json(WORK_ROOT / "guide/translated_strings.json", guide_rows)

    instance = resolve_source_root()
    quest_candidate = instance / "config/ftbquests/quests/lang/ko_kr.snbt"
    quest_before = quest_snbt.parse_language_snbt(quest_candidate)
    quest_merge_source = QUEST_OUTPUT if QUEST_OUTPUT.is_file() else quest_candidate
    merged = quest_snbt.merge_into_full_snbt(quest_merge_source, QUEST_CORRECTIONS)
    QUEST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    quest_after = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    for key, expected in QUEST_CORRECTIONS.items():
        if quest_after.get(key) != expected:
            raise ValueError(f"퀘스트 병합 결과가 달라요: {key}")
    quest_reused = sum(
        quest_before.get(key) == value for key, value in QUEST_CORRECTIONS.items()
    )
    quest_corrected = len(QUEST_CORRECTIONS) - quest_reused
    guide_translated = sum(row["status"] == "translated" for row in guide_rows)
    guide_same = len(guide_rows) - guide_translated
    report = {
        "reviewed_language_keys": sum(
            len(value) for value in english_by_namespace.values()
        ),
        "existing_korean_reused": reused,
        "existing_korean_corrected": corrected,
        "new_language_translations": new,
        "candidate_sources": {
            namespace: dict(counter) for namespace, counter in source_rows.items()
        },
        "guide_files": len(guide_files),
        "guide_direct_strings_translated": guide_translated,
        "guide_intentional_same_strings": guide_same,
        "quest_existing_korean_reused": quest_reused,
        "quest_existing_korean_corrected": quest_corrected,
        "quest_keys": len(QUEST_CORRECTIONS),
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def collect_references(instance: Path) -> dict[str, object]:
    """FTB Quests와 KubeJS에서 네 모드의 실제 참조를 모아요."""
    needles = tuple(f"{namespace}:" for namespace in NAMESPACES)
    suffixes = {
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
    results: dict[str, object] = {
        "quest_references": [],
        "kubejs_references": [],
        "custom_name_candidates": [],
        "read_errors": [],
    }
    for label, root in (
        ("quest_references", instance / "config/ftbquests/quests/chapters"),
        ("kubejs_references", instance / "kubejs"),
    ):
        rows = results[label]
        custom_names = results["custom_name_candidates"]
        read_errors = results["read_errors"]
        if not isinstance(rows, list) or not isinstance(custom_names, list):
            raise TypeError("참조 보고서 목록 초기화에 실패했어요")
        if not isinstance(read_errors, list):
            raise TypeError("읽기 오류 보고서 목록 초기화에 실패했어요")
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                read_errors.append(f"{path}: {exc}")
                continue
            lines = text.splitlines()
            relative = path.relative_to(instance).as_posix()
            for index, line in enumerate(lines):
                if not any(needle in line for needle in needles):
                    continue
                rows.append(f"{relative}:{index + 1}:{line.strip()}")
                window = "\n".join(lines[max(0, index - 8) : index + 9]).lower()
                if "custom_name" in window:
                    custom_names.append(f"{relative}:{index + 1}:{line.strip()}")
    return results


def audit_advancements(instance: Path) -> tuple[list[dict[str, object]], list[str]]:
    """발전 과제의 번역 키와 직접 영어 문구를 확인해요."""
    rows = []
    errors = []
    for namespace, pattern in NAMESPACES.items():
        jar = source_jar(instance, pattern)
        advancement_files = []
        translated_keys = []
        direct_literals = []
        with ZipFile(jar) as archive:
            for internal in sorted(archive.namelist()):
                if "/advancement/" not in internal or not internal.endswith(".json"):
                    continue
                advancement_files.append(internal)
                value = json.loads(archive.read(internal))
                display = value.get("display", {})
                if not isinstance(display, dict):
                    continue
                for field in ("title", "description"):
                    shown = display.get(field)
                    if isinstance(shown, dict) and isinstance(
                        shown.get("translate"), str
                    ):
                        translated_keys.append(shown["translate"])
                    elif isinstance(shown, str):
                        direct_literals.append(
                            {"file": internal, "field": field, "value": shown}
                        )
        language = load_json(WORK_ROOT / namespace / "ko_kr.json")
        missing = sorted(set(translated_keys) - set(language))
        if missing:
            errors.append(f"{namespace} 발전 과제 번역 키가 누락됐어요: {missing}")
        if direct_literals:
            errors.append(f"{namespace} 발전 과제에 직접 영어 문구가 있어요")
        rows.append(
            {
                "namespace": namespace,
                "jar": jar.name,
                "advancement_files": advancement_files,
                "advancement_translation_keys": sorted(set(translated_keys)),
                "missing_advancement_keys": missing,
                "direct_advancement_text": direct_literals,
            }
        )
    return rows, errors


def audit() -> tuple[dict[str, object], list[str]]:
    """안내서, 발전 과제, FTB Quests와 KubeJS 표시 경로를 감사해요."""
    instance = resolve_source_root()
    errors = []
    advancements, advancement_errors = audit_advancements(instance)
    errors.extend(advancement_errors)
    references = collect_references(instance)
    read_errors = references.get("read_errors", [])
    custom_names = references.get("custom_name_candidates", [])
    if isinstance(read_errors, list):
        errors.extend(str(value) for value in read_errors)
    if custom_names:
        errors.append(f"관련 참조 주변에 custom_name 후보가 있어요: {custom_names}")

    english_quests = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean_quests = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    related_quest_keys = sorted(
        key
        for key in english_quests
        if any(identifier in key for identifier in RELATED_QUEST_IDS)
    )
    if set(related_quest_keys) != set(QUEST_CORRECTIONS):
        errors.append(
            "관련 FTB Quests 키 범위가 예상과 달라요: "
            f"{sorted(set(related_quest_keys) ^ set(QUEST_CORRECTIONS))}"
        )
    for key, expected in QUEST_CORRECTIONS.items():
        if korean_quests.get(key) != expected:
            errors.append(f"관련 퀘스트 교정값이 달라요: {key}")

    chapter = instance / "config/ftbquests/quests/chapters/bounty_board.snbt"
    chapter_text = chapter.read_text(encoding="utf-8")
    namespace_pattern = "|".join(re.escape(value) for value in NAMESPACES)
    task_pattern = re.compile(
        rf'\{{\s*entity:\s*"((?:{namespace_pattern}):[^"]+)"'
        rf'\s*id:\s*"([A-F0-9]+)"\s*type:\s*"kill"',
        re.MULTILINE,
    )
    entity_tasks = [
        {"entity": match.group(1), "task_id": match.group(2)}
        for match in task_pattern.finditer(chapter_text)
    ]
    explicit_task_titles = {
        row["task_id"]: english_quests.get(f"task.{row['task_id']}.title")
        for row in entity_tasks
        if f"task.{row['task_id']}.title" in english_quests
    }
    fallback_missing = []
    language_by_namespace = {
        namespace: load_json(WORK_ROOT / namespace / "ko_kr.json")
        for namespace in NAMESPACES
    }
    for row in entity_tasks:
        namespace, identifier = row["entity"].split(":", 1)
        key = f"entity.{namespace}.{identifier}"
        if key not in language_by_namespace[namespace]:
            fallback_missing.append({"entity": row["entity"], "language_key": key})
    if explicit_task_titles:
        errors.append(
            f"관련 처치 과제에 명시적 영어 제목이 있어요: {explicit_task_titles}"
        )
    if fallback_missing:
        errors.append(f"자동 엔티티 제목 번역이 누락됐어요: {fallback_missing}")

    inventory = load_json(WORK_ROOT / "inventory.json")
    guide_files = inventory.get("guide_files", [])
    if not isinstance(guide_files, list) or not guide_files:
        errors.append("Living Things 안내서 파일 목록이 비어 있어요")
    report = {
        "family": FAMILY,
        "advancements": advancements,
        "guide_files": len(guide_files) if isinstance(guide_files, list) else 0,
        "references": references,
        "related_quest_keys": related_quest_keys,
        "related_quest_keys_corrected": len(QUEST_CORRECTIONS),
        "entity_fallback_tasks": entity_tasks,
        "explicit_entity_task_titles": explicit_task_titles,
        "fallback_missing_entity_keys": fallback_missing,
        "ftbquests_display_work": "complete",
        "kubejs_display_work": "ids_only",
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def validate_preserved(
    key: str,
    source: str,
    target: str,
    include_patchouli: bool = False,
) -> list[str]:
    """자리표시자·서식·숫자·줄바꿈 보존을 확인해요."""
    errors = []
    patterns = [("자리표시자", PLACEHOLDER), ("서식 코드", FORMAT_CODE)]
    if include_patchouli:
        patterns.append(("Patchouli 코드", PATCHOULI_CODE))
    for label, pattern in patterns:
        if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
            errors.append(f"{label} 불일치: {key}")
    if Counter(NUMBER.findall(source)) != Counter(NUMBER.findall(target)):
        errors.append(f"숫자 불일치: {key}")
    if source.count("\n") != target.count("\n"):
        errors.append(f"줄바꿈 불일치: {key}")
    return errors


def verify_languages(instance: Path) -> tuple[list[dict[str, object]], list[str]]:
    """네 모드 언어 산출물을 현재 JAR과 대조해요."""
    rows = []
    errors = []
    for namespace, pattern in NAMESPACES.items():
        jar = source_jar(instance, pattern)
        jar_english = read_jar_language(jar, namespace)
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
            current_errors.extend(validate_preserved(key, source, target))
            if source == target and key not in INTENTIONAL_SAME[namespace]:
                untranslated.append(key)
            residue = sorted(set(LATIN_WORD.findall(target)) - ALLOWED_LATIN)
            if residue:
                latin_residue[key] = residue
        collisions = defaultdict(list)
        for key, target in korean.items():
            if isinstance(target, str) and key.startswith(("item.", "block.")):
                collisions[target].append(key)
        unexpected_collisions = {
            target: keys
            for target, keys in collisions.items()
            if len(keys) > 1 and len({english[key] for key in keys}) > 1
        }
        if untranslated:
            current_errors.append(f"영어와 같은 미번역 후보: {untranslated}")
        if latin_residue:
            current_errors.append(f"허용하지 않은 영문 잔여: {latin_residue}")
        if unexpected_collisions:
            current_errors.append(
                f"서로 다른 이름의 한국어 충돌: {unexpected_collisions}"
            )
        rows.append(
            {
                "namespace": namespace,
                "keys": len(english),
                "untranslated_candidates": untranslated,
                "latin_residue": latin_residue,
                "unexpected_name_collisions": unexpected_collisions,
                "errors": current_errors,
            }
        )
        errors.extend(f"{namespace}: {message}" for message in current_errors)
    return rows, errors


def verify_guide(instance: Path) -> tuple[dict[str, object], list[str]]:
    """Living Things 안내서의 파일·문구·Patchouli 코드를 검증해요."""
    errors = []
    jar = source_jar(instance, NAMESPACES["livingthings"])
    files = []
    direct_rows: list[dict[str, str]] = []
    with ZipFile(jar) as archive:
        internals = sorted(
            name
            for name in archive.namelist()
            if name.startswith(GUIDE_SOURCE_ROOT + "/") and name.endswith(".json")
        )
        for internal in internals:
            relative = Path(internal).relative_to(GUIDE_SOURCE_ROOT)
            source = json.loads(archive.read(internal))
            expected_rows: list[dict[str, str]] = []
            expected = translated_guide_value(
                source, relative.as_posix(), expected_rows
            )
            working_source = load_json(WORK_ROOT / "guide/en_us" / relative)
            working_target = load_json(WORK_ROOT / "guide/ko_kr" / relative)
            output = load_json(GUIDE_OUTPUT_ROOT / relative)
            if working_source != source:
                errors.append(f"안내서 작업 영어가 JAR과 달라요: {relative}")
            if working_target != expected or output != expected:
                errors.append(f"안내서 한국어 산출물이 달라요: {relative}")
            direct_rows.extend(expected_rows)
            files.append(relative.as_posix())
        source_book = json.loads(archive.read(BOOK_SOURCE))
    book_rows: list[dict[str, str]] = []
    expected_book = translated_guide_value(source_book, "book.json", book_rows)
    if load_json(WORK_ROOT / "guide/book_en_us.json") != source_book:
        errors.append("안내서 책 원본이 현재 JAR과 달라요")
    if load_json(WORK_ROOT / "guide/book_ko_kr.json") != expected_book:
        errors.append("안내서 책 작업 한국어가 예상과 달라요")
    if load_json(BOOK_OUTPUT) != expected_book:
        errors.append("안내서 책 덮어쓰기 산출물이 예상과 달라요")
    direct_rows.extend(book_rows)
    untranslated = []
    latin_residue = {}
    for row in direct_rows:
        source = row["source"]
        target = row["target"]
        errors.extend(
            validate_preserved(row["path"], source, target, include_patchouli=True)
        )
        if source == target and row["status"] != "intentional_same":
            untranslated.append(row["path"])
        if row["status"] == "intentional_same":
            continue
        cleaned = PATCHOULI_CODE.sub("", target)
        residue = sorted(set(LATIN_WORD.findall(cleaned)) - ALLOWED_LATIN)
        if residue:
            latin_residue[row["path"]] = residue
    if untranslated:
        errors.append(f"안내서 미번역 문구가 있어요: {untranslated}")
    if latin_residue:
        errors.append(f"안내서에 허용하지 않은 영문 잔여가 있어요: {latin_residue}")
    report = {
        "files": len(files),
        "direct_strings": len(direct_rows),
        "translated_strings": sum(row["status"] == "translated" for row in direct_rows),
        "intentional_same_strings": sum(
            row["status"] == "intentional_same" for row in direct_rows
        ),
        "untranslated": untranslated,
        "latin_residue": latin_residue,
        "errors": errors,
    }
    return report, errors


def verify_quests(instance: Path) -> tuple[dict[str, object], list[str]]:
    """관련 FTB Quests 키와 보존 요소를 영어 원문과 대조해요."""
    errors = []
    english = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    latin_residue = {}
    for key, expected in QUEST_CORRECTIONS.items():
        if korean.get(key) != expected:
            errors.append(f"퀘스트 번역값이 달라요: {key}")
            continue
        errors.extend(quest_snbt.validate_value(key, english[key], expected))
        target_text = "\n".join(expected) if isinstance(expected, list) else expected
        residue = sorted(set(LATIN_WORD.findall(target_text)) - ALLOWED_LATIN)
        if residue:
            latin_residue[key] = residue
    if latin_residue:
        errors.append(f"퀘스트에 허용하지 않은 영문 잔여가 있어요: {latin_residue}")
    return {
        "keys": len(QUEST_CORRECTIONS),
        "latin_residue": latin_residue,
        "errors": errors,
    }, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """현재 JAR과 모든 산출물의 완결성과 보존 규칙을 검증해요."""
    instance = resolve_source_root()
    audit_report = load_json(WORK_ROOT / "surface_audit.json")
    translation_report = load_json(WORK_ROOT / "translation_report.json")
    languages, language_errors = verify_languages(instance)
    guide, guide_errors = verify_guide(instance)
    quests, quest_errors = verify_quests(instance)
    errors = language_errors + guide_errors + quest_errors
    if audit_report.get("status") != "complete":
        errors.append("표시 표면 감사가 완료되지 않았어요")
    language_keys = sum(int(row["keys"]) for row in languages)
    report = {
        "family": FAMILY,
        "languages": languages,
        "language_keys": language_keys,
        "guide": guide,
        "quests": quests,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "language_validation.json", report)

    guide_files = [
        (
            "resourcepacks/ATM10_Korean/assets/livingthings/patchouli_books/"
            f"lexicon/ko_kr/{relative}"
        )
        for relative in load_json(WORK_ROOT / "inventory.json")["guide_files"]
    ]
    completion = {
        "family": FAMILY,
        "language_keys": language_keys,
        "existing_korean_reused": translation_report["existing_korean_reused"],
        "new_or_corrected_language_translations": (
            translation_report["existing_korean_corrected"]
            + translation_report["new_language_translations"]
        ),
        "guide": {
            "files": guide["files"],
            "direct_strings": guide["direct_strings"],
            "translated_strings": guide["translated_strings"],
        },
        "ftbquests": {
            "reviewed_keys": quests["keys"],
            "existing_korean_reused": translation_report[
                "quest_existing_korean_reused"
            ],
            "corrected_keys": translation_report["quest_existing_korean_corrected"],
            "entity_fallback_tasks": len(audit_report["entity_fallback_tasks"]),
            "display_work": audit_report["ftbquests_display_work"],
        },
        "kubejs_references": len(
            audit_report.get("references", {}).get("kubejs_references", [])
        ),
        "output_files": [
            *[
                ("resourcepacks/ATM10_Korean/assets/" f"{namespace}/lang/ko_kr.json")
                for namespace in NAMESPACES
            ],
            *guide_files,
            "kubejs/data/livingthings/patchouli_books/lexicon/book.json",
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
    if relative.startswith("resourcepacks/"):
        return (
            active_output_root()
            / "resourcepack"
            / relative.removeprefix("resourcepacks/")
        )
    return active_output_root() / "overrides" / relative


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
