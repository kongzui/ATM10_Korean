#!/usr/bin/env python3
"""Occultism 언어 파일과 FTB Quests를 현재 영어 원문으로 전면 재검수한다."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import re
import sys
import time
from pathlib import Path
from zipfile import ZipFile

import theurgy_family as helper
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "occultism"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
LANG_ROOT = WORK_ROOT / "occultism"
QUEST_ROOTS = (WORK_ROOT / "quests/occultism", WORK_ROOT / "quests/related")
CACHE_PATH = PROJECT_ROOT / "temp/occultism_line_candidate_cache_v1.json"
WHOLE_CACHE_PATH = PROJECT_ROOT / "temp/occultism_whole_candidate_cache_v4.json"
LABEL_CACHE_PATH = PROJECT_ROOT / "temp/occultism_link_label_cache_v1.json"
BUNDLED_PATH = LANG_ROOT / "bundled_ko_kr.json"
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[.,/]\d+)*")
LINK_TARGET = re.compile(r"\]\(([^)]*)\)")
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")
FORMATTED_SPAN = re.compile(r"\[#\]\(([^)]*)\)(.*?)\[#\]\(\)")
EXTRA_KEYS = {
    "book.occultism.dictionary_of_spirits.crafting_rituals.craft_eldritch_chalice.ritual2.text": (
        "천상의 성배를 만드는 의식입니다."
    ),
}
SURFACE_BLOCKED = (
    "\u200b",
    "\ufeff",
    "이이에스늄",
    "분필s",
    "악마들s",
    "아프리트s",
    "마리드s",
    "E빈",
    "정령는",
    "Occultism는",
    "정령불가",
    "정령불를",
    "분필를",
    "반죽를",
    "사역마 사람들",
    "비밀주의",
    "너비:",
    "높이:",
    "정렬:",
    "펜타클",
    "이세계",
    "반죽는",
    "분필는",
    "폴리엇라고",
    "뼈대 두개골",
    "영혼이 조화된 보석",
)
ALLOWED_ORIGINALS = {
    "Susjes Simple Circle",
    "&9Xeovrenth Adjure",
    "&aIhagan's Enthrallment",
    "&aStrigeor's Higher Binding",
    "&b&lOccultism",
    "&cSevira's Permanent Confinement",
    "&dOsorin's Unbound Calling",
    "&dRonaza's Contact",
    "&4Tibira's Attraction",
    "&aOphyx' Calling",
    "&6Kandar's Opened Conjure",
    "&6Odus' Open Convocation",
    "&9Fatma's Incentivized Attraction",
    "&9Uphyxes' Inverted Tower",
    "&eEziveus' Spectral Compulsion",
    "Abras Conjure",
    "Fatma's Incentivized Attraction",
    "{image:atm:textures/questpics/occultism/aviarcirclenew.png width:200 height:200 align:1}",
    "{image:atm:textures/questpics/occultism/iesniumexample.png width:200 height:175 align:1}",
    "{image:atm:textures/questpics/occultism/storageupgradeexample.png width:200 height:150 align:1}",
    "{image:atm:textures/questpics/allthemodium/all_1.png width:100 height:100 align:center}",
}

EXACT_SOURCE = {
    "Occultism": "Occultism",
    "Dictionary of Spirits": "영혼 사전",
    "Dictionary of Spirits: Instructions for Summoning and Rituals": "영혼 사전: 소환과 의식 안내서",
    "Spirit Dictionary": "영혼 사전",
    "Otherworld": "이계",
    "Iesnium": "이에스늄",
    "Foliot": "폴리엇",
    "Djinni": "지니",
    "Afrit": "아프리트",
    "Marid": "마리드",
    "Familiar": "사역마",
    "Familiars": "사역마",
    "Pentacle": "마법진",
    "Pentacles": "마법진",
    "Ritual": "의식",
    "Rituals": "의식",
    "Possession": "빙의",
    "Summoning": "소환",
    "Dimensional Storage": "차원 저장소",
    "Dimensional Mineshaft": "차원 광산 갱도",
    "Storage Accessor": "저장소 접근기",
    "Storage Controller": "저장소 제어기",
    "Spirit Attuned Gem": "정령 조율 보석",
    "Book of Binding": "속박의 책",
    "Book of Calling": "부름의 책",
    "Sacrificial Bowl": "희생의 그릇",
    "Golden Sacrificial Bowl": "황금 희생의 그릇",
    "Chalk": "분필",
    "Purified Ink": "정제된 잉크",
}

EXACT_KEYS = {
    "itemGroup.occultism": "Occultism",
    "advancements.occultism.root.title": "Occultism",
    "item.occultism.book_of_calling_djinni.tooltip.deposit": "입금 대상: % s",
    "book.occultism.dictionary_of_spirits.getting_started.intro.help.text": (
        "Occultism을 플레이하다 문제가 생기면 Discord 서버에 참여해 도움을 요청하세요."
        "\n\\\n\\\n[Discord 서버 참여: https://discord.gg/trE4SHRXvb]"
        "(https://discord.gg/trE4SHRXvb)\n"
    ),
    "book.occultism.dictionary_of_spirits.getting_started.first_ritual.bowl_text.text": (
        "다음으로 마법진 가까이에 *최소* 4개의 "
        "[희생의 그릇](item://occultism:sacrificial_bowl)을 놓으세요."
        "\n\\\n\\\n중앙 [](item://occultism:golden_sacrificial_bowl)에서 8블록 이내의 "
        "**어디든지**에 놓으면 됩니다. **정확한 위치는 중요하지 않습니다.**\n"
    ),
    "book.occultism.dictionary_of_spirits.getting_started.iesnium_pickaxe.spotlight.text": (
        "[주입된 곡괭이](entry://getting_started/infused_pickaxe)처럼 이 곡괭이로는 "
        "[](item://occultism:iesnium_ore) 같은 2등급 이계 재료를 채굴할 수 있습니다. "
        "부서지기 쉬운 [](item://occultism:spirit_attuned_gem) 대신 금속으로 만들었으므로 "
        "내구성이 매우 높아 오랫동안 사용할 수 있습니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.pentacle_overview.intro4.text": (
        "재료는 [희생의 그릇](item://occultism:sacrificial_bowl)에 놓습니다.\n"
        "마법진 근처, 정확히는 중앙 [](item://occultism:golden_sacrificial_bowl)에서 가로로\n"
        "8블록 이내의 **어디든지**에 놓아야 합니다.\n"
        "정확한 위치는 중요하지 않습니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.familiar_rituals.overview.trading.text": (
        '"[사역마 반지](entry://crafting_rituals/craft_familiar_ring)에 담으면 사역마를 '
        "쉽게 거래할 수 있습니다.\n\\\n\\\n사역마를 풀어 주면 그 정령은 자신을 풀어 준 "
        "사람을 새 주인으로 인정합니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.possess_djinni.uses.text": (
        "- [빙의된 엔더맨](entry://possession_rituals/possess_enderman)\n"
        "- [빙의된 가스트](entry://possession_rituals/possess_ghast)\n"
        "- [빙의된 약한 셜커](entry://possession_rituals/possess_weak_shulker)\n"
        "- [빙의된 벌](entry://possession_rituals/possess_bee)\n"
        "- [빙의된 블레이즈](entry://possession_rituals/possess_blaze)\n"
        "- [무작위 동물(탑승 가능, 특수, 주민)]"
        "(entry://possession_rituals/possess_random_animal)\n"
        "- [속박되지 않은 드릭윙]"
        "(entry://possession_rituals/possess_unbound_otherworld_bird)\n"
        "- [드릭윙 사역마](entry://familiar_rituals/familiar_otherworld_bird)\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.possess_foliot.uses.text": (
        "- [빙의된 엔더마이트](entry://possession_rituals/possess_endermite)\n"
        "- [빙의된 스켈레톤](entry://possession_rituals/possess_skeleton)\n"
        "- [빙의된 마녀](entry://possession_rituals/possess_witch)\n"
        "- [빙의된 팬텀](entry://possession_rituals/possess_phantom)\n"
        "- [속박되지 않은 앵무새](entry://possession_rituals/possess_unbound_parrot)\n"
        "- [무작위 동물(일반, 수생, 소형)]"
        "(entry://possession_rituals/possess_random_animal)\n"
        "- [앵무새 사역마](entry://familiar_rituals/familiar_parrot)\n"
        "- [탐욕스러운 사역마](entry://familiar_rituals/familiar_greedy)\n"
        "- [사슴 사역마](entry://familiar_rituals/familiar_deer)\n"
        "- [대장장이 사역마](entry://familiar_rituals/familiar_blacksmith)\n"
        "- [비버 사역마](entry://familiar_rituals/familiar_beaver)\n"
    ),
    "book.occultism.dictionary_of_spirits.familiar_rituals.familiar_beaver.description.text": (
        "비버 사역마는 근처의 묘목이 작은 나무로 자라면 베어 냅니다. "
        "큰 나무는 처리할 수 없습니다.\n\\\n\\\n**업그레이드 동작**\\\n"
        "빈손으로 우클릭하면 간식을 줍니다.\n"
    ),
    "item.occultism.ritual_dummy.wild_hunt.tooltip": (
        "야생 사냥대는 위더 스켈레톤 해골을 높은 확률로 떨어뜨리는 위더 스켈레톤과 "
        "그 부하들로 이루어집니다."
    ),
    "book.occultism.dictionary_of_spirits.getting_started.divination_rod.how_to_use3.text": (
        "탐색에 성공한 뒤 아무것도 들지 않고 [#](ad03fc)우클릭[#]()하면 마지막으로 "
        "찾은 대상 블록을 다시 표시합니다.\n\\\n\\\n"
        '*"Theurgy"* 모드가 설치되어 있으면 막대가 대상 블록을 강조하지 않고 '
        "대상 방향으로 입자 효과를 보냅니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.getting_started.third_eye.about.text": (
        "물질세계 너머를 보는 능력을 [#](ad03fc)제3의 눈[#]()이라고 합니다.\n"
        "인간은 본래 [#](ad03fc)장막 너머[#]()를 볼 수 없지만,\n"
        "지식이 풍부한 소환사는 특정 물질과 장치를 이용해 이 한계를 우회할 수 있습니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.getting_started.possession_rituals.intro.text": (
        "빙의된 몹은 정령이 조종하므로 소환사가 일부 특성을 결정할 수 있습니다. "
        "보통 희귀 전리품의 **드롭률이 높지만** 처치하기도 더 어렵습니다.\n\\\n\\\n"
        "먼저 [빙의된 엔더마이트](entry://possession_rituals/possess_endermite)를 "
        "소환해 [](item://minecraft:end_stone)을 얻고, "
        "[고급 분필](entry://getting_started/chalks)을 만드는 것이 좋습니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.getting_started.iesnium.how.text": (
        "이에스늄은 [주입된 곡괭이](entry://getting_started/infused_pickaxe) 또는 "
        "나중에 배우게 될 [](item://occultism:iesnium_pickaxe)로만 채굴할 수 있습니다."
        "\n\\\n\\\n이에스늄이 든 블록을 확인했다면 앞 단계에서 만든 곡괭이로 "
        "채굴하세요.\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.craft_foliot.uses.text": (
        "- [연구 파편 가루](entry://pentacles/lime_chalk)\n"
        "- [자연의 반죽](entry://pentacles/green_chalk)\n"
        "- [주입된 렌즈](entry://crafting_rituals/craft_otherworld_goggles)\n"
        "- [취약한 영혼 보석](entry://crafting_rituals/fragile_soul_gem)\n"
        "- [생명력 나침반](entry://crafting_rituals/vitality_compass)\n"
        "- [지식의 서판](entry://crafting_rituals/knowledge_tablet)\n"
        "- [폴리엇 광부](entry://crafting_rituals/craft_foliot_miner)\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.craft_foliot.uses2.text": (
        "- [놀랍도록 넉넉한 가방](entry://crafting_rituals/craft_satchel)\n"
        "- [견습생 의식 가방](entry://crafting_rituals/apprentice_ritual_satchel)\n"
        "- [저장소 작동기 기반](entry://crafting_rituals/craft_storage_controller_base)\n"
        "- [안정된 웜홀](entry://crafting_rituals/craft_stable_wormhole)\n"
        "- [1등급 저장소 안정기](entry://crafting_rituals/craft_stabilizer_tier1)\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.craft_djinni.uses.text": (
        "- [주입된 곡괭이](entry://crafting_rituals/craft_infused_pickaxe)\n"
        "- [영혼 보석](entry://crafting_rituals/craft_soul_gem)\n"
        "- [사역마 반지](entry://crafting_rituals/craft_familiar_ring)\n"
        "- [개체 웜홀](entry://crafting_rituals/entity_wormhole)\n"
        "- [차원 추출기](entry://crafting_rituals/dimensional_extractor)\n"
        "- [차원 광산 갱도](entry://crafting_rituals/craft_dimensional_mineshaft)\n"
        "- [지니 광석 광부](entry://crafting_rituals/craft_djinni_miner)\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.craft_djinni.uses2.text": (
        "- [엔더 가방](entry://crafting_rituals/ender_satchel)\n"
        "- [차원 행렬](entry://crafting_rituals/craft_dimensional_matrix)\n"
        "- [저장소 접근기](entry://crafting_rituals/craft_storage_remote)\n"
        "- [2등급 저장소 안정기](entry://crafting_rituals/craft_stabilizer_tier2)\n"
        "- [정령 숫돌](entry://crafting_rituals/spirit_grindstone)\n"
        "- [분필 수리](entry://crafting_rituals/repair)\n"
        "- [회색 반죽](entry://pentacles/gray_chalk)\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.craft_marid.uses.text": (
        "- [4등급 저장소 안정기](entry://crafting_rituals/craft_stabilizer_tier4)\n"
        "- [마리드 최고급 광부](entry://crafting_rituals/craft_marid_miner)\n"
        "- [이에스늄 모루](entry://crafting_rituals/craft_iesnium_anvil)\n"
        "- [진실의 시야 지팡이](entry://crafting_rituals/true_sight_staff)\n"
        "- [드래고니스트 가루](entry://pentacles/magenta_chalk)\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.summon_djinni.uses.text": (
        "- [지니 분쇄기](entry://summoning_rituals/summon_crusher_t2)\n"
        "- [지니 제련공](entry://summoning_rituals/summon_smelter_t2)\n"
        "- [지니 결정화기](entry://summoning_rituals/summon_crystallizer_t2)\n"
        "- [지니 기계 조작자](entry://summoning_rituals/summon_manage_machine)\n"
        "- [보석 도박꾼](entry://summoning_rituals/summon_gambler)\n"
        "- [떠돌이 상인](entry://summoning_rituals/summon_wondering)\n"
        "- [맑은 날씨](entry://summoning_rituals/weather_magic@clear)\n"
        "- [시간 마법](entry://summoning_rituals/time_magic)\n"
        "- [악마 동반자](entry://familiar_rituals/demonic_partner)\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.summon_foliot.uses.text": (
        "- [폴리엇 분쇄기](entry://summoning_rituals/summon_crusher_t1)\n"
        "- [폴리엇 제련공](entry://summoning_rituals/summon_smelter_t1)\n"
        "- [폴리엇 결정화기](entry://summoning_rituals/summon_crystallizer_t1)\n"
        "- [폴리엇 벌목꾼](entry://summoning_rituals/summon_lumberjack)\n"
        "- [폴리엇 농부](entry://summoning_rituals/summon_farmer)\n"
        "- [폴리엇 운반자](entry://summoning_rituals/summon_transport_items)\n"
        "- [폴리엇 관리인](entry://summoning_rituals/summon_cleaner)\n"
        "- [이계석 상인](entry://summoning_rituals/summon_otherstone_trader)\n"
        "- [이계암 상인](entry://summoning_rituals/summon_otherrock_trader)\n"
        "- [이계 묘목 상인]"
        "(entry://summoning_rituals/summon_otherworld_sapling_trader)\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.contact_wild_spirit.uses.text": (
        "- [위더 스켈레톤 해골](entry://possession_rituals/wither_skull)\n"
        "- [허스크 무리](entry://possession_rituals/horde_husk)\n"
        "- [드라운드 무리](entry://possession_rituals/horde_drowned)\n"
        "- [크리퍼 무리](entry://possession_rituals/horde_creeper)\n"
        "- [좀벌레 무리](entry://possession_rituals/horde_silverfish)\n"
        "- [시험 열쇠](entry://possession_rituals/possess_weak_breeze)\n"
        "- [불길한 시험 열쇠](entry://possession_rituals/possess_breeze)\n"
        "- [육중한 코어](entry://possession_rituals/possess_strong_breeze)\n"
        "- [야생 약탈자 침공](entry://possession_rituals/horde_illager)\n"
        "- [무작위 동물 무리](entry://possession_rituals/wild_random_animal)\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.craft_afrit.intro.text": (
        "**목적:** [#](AA00AA)아프리트[#]() 속박\\\n\\\n"
        "잿불숲의 대마녀 세비라가 처음 발견한 **Seviras Permanent Confinement**는\n"
        " [#](AA00AA)아프리트[#]()를 물체에 속박하는 데 사용합니다. 관련 정령의 힘이 "
        "강하므로 숙련된 소환사만 수행해야 합니다.\n\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.possess_unbound_afrit.intro.text": (
        "**목적:** [#](AA00AA)속박되지 않은 아프리트[#]() 빙의\\\n\\\n"
        "**Odus Open Convocation**은 [#](AA00AA)Posuc' Convocation[#]()을 단순화한 "
        "형태로, 빨간색 분필 없이 [#](AA00AA)아프리트[#]()가 근처 생명체에 빙의하게 "
        "합니다.\n 마법진의 힘이 크게 약해져 용도가 제한됩니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.summon_unbound_afrit.intro.text": (
        "**목적:** [#](AA00AA)속박되지 않은 아프리트[#]() 소환\\\n\\\n"
        "**Kandars Open Conjure**는 [#](FF55FF)Abras Conjure[#]()를 단순화한 "
        "형태로, 빨간색 분필 없이 [#](AA00AA)아프리트[#]()를 소환합니다.\n"
        " 마법진의 힘이 크게 약해 [#](AA00AA)아프리트[#]()를 통제할 수 없으므로,\n"
        " 오직 [#](AA00AA)아프리트[#]()와 싸워 처치하는 데만 쓸 수 있습니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.possession_rituals.possess_hoglin.description.text": (
        "이 의식에서는 [#](ad03fc)돼지[#]()의 생명력으로 [#](ad03fc)호글린[#]()을 "
        "생성하고, 소환한 [#](ad03fc)아프리트[#]()가 즉시 빙의합니다. "
        "[#](ad03fc)빙의된 호글린[#]()은 "
        "[](item://minecraft:netherite_upgrade_smithing_template), "
        "[](item://minecraft:snout_armor_trim_smithing_template), "
        "[](item://minecraft:music_disc_pigstep), "
        "[](item://minecraft:piglin_banner_pattern), [](item://minecraft:nether_brick)을 "
        "떨어뜨리거나 [](item://minecraft:netherite_scrap)을 돌려줄 수 있습니다. 네더에서 "
        "의식을 치르지 않았다면 조글린으로 변하기 전에 처치해야 합니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.possession_rituals.possess_zombie_piglin.description.text": (
        "이 의식에서는 [#](ad03fc)아프리트[#]()가 [#](ad03fc)늙은 좀비화 피글린[#]()에 "
        "빙의해,\n [#](ad03fc)네더[#]()의 에너지와 [#](ad03fc)아프리트[#]()의 힘,\n"
        "  [#](ad03fc)돼지고기[#]()라는 물질과 [#](ad03fc)분홍색[#]()의 개념을 "
        "결합합니다.\n 이것이 [](item://occultism:demonic_meat)을 얻는 유일하게 알려진 "
        "방법입니다. 이 고기는\n  조리할 수 없지만 먹으면 화염 저항을 부여합니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.storage.storage_system_automation_theurgy.intro.text": (
        "운반 정령과 마찬가지로 Theurgy의 수은 물류 시스템은\n"
        " 저장소 작동기 및 안정된 웜홀과 함께 사용하도록 최적화되어 있습니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.summoning_rituals.summon_cleaner.tip.text": (
        "관리인은 [분쇄기](entry://summoning_rituals/summon_crusher_t1), "
        "[제련공](entry://summoning_rituals/summon_smelter_t1), "
        "[결정화기](entry://summoning_rituals/summon_crystallizer_t1)\n"
        "정령이 가공한 아이템을 주워 상자에 넣습니다.\n\\\n\\\n"
        "[운반 정령](entry://summoning_rituals/summon_transport_items)과 조합하면 "
        "전 과정을 자동화할 수 있습니다.\n"
    ),
    "jei.occultism.ingredient.spawn_egg.familiar_shub_niggurath.description": (
        "숲 생물군계로 염소 사역마를 데려간 뒤 검은색 염료, 부싯돌, 엔더의 눈 "
        "순서로 염소를 클릭하면 슈브 니구라스 사역마를 얻을 수 있습니다. 자세한 내용은 "
        "§6영혼§r §6사전§r §6항목§r을 참고하세요."
    ),
    "book.occultism.dictionary_of_spirits.crafting_rituals.apprentice_ritual_satchel.usage.text": (
        "1. [#](55FF55)Shift-우클릭[#]()해 가방을 열고 의식에 필요한 분필, 양초, "
        "수정, 해골 등의 아이템을 넣으세요.\n"
        "2. 이 책의 '눈' 아이콘으로 월드에 설치할 마법진을 미리 보세요.\n"
        "3. 책을 들고 원하는 위치를 [#](55FF55)우클릭[#]()해 마법진 미리 보기를 "
        "고정하세요.\n"
        "4. 가방으로 미리 표시된 분필 자국이나 블록을 [#](55FF55)우클릭[#]()하면 "
        "자동으로 설치합니다.\n"
        "5. 마법진이 완성될 때까지 반복하세요.\n"
    ),
    "book.occultism.dictionary_of_spirits.crafting_rituals.artisanal_ritual_satchel.usage_drawing.text": (
        "1. [#](55FF55)Shift-우클릭[#]()해 가방을 열고 의식에 필요한 분필, 양초, "
        "수정, 해골 등의 아이템을 넣으세요.\n"
        "2. 이 책의 '눈' 아이콘으로 월드에 설치할 마법진을 미리 보세요.\n"
        "3. 책을 들고 원하는 위치를 [#](55FF55)우클릭[#]()해 마법진 미리 보기를 "
        "고정하세요.\n"
        "4. 필요한 재료를 넣은 가방으로 미리 표시된 분필 자국이나 블록을 "
        "[#](55FF55)우클릭[#]()하면 표시된 블록을 모두 자동으로 설치합니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.crafting_rituals.craft_familiar_ring.usage.text": (
        "[](item://occultism:familiar_ring)를 사용하려면 소환해 길들인 사역마를 "
        "[#](AA00AA)우클릭[#]()해 반지에 담은 뒤,\n"
        " 반지를 [#](AA00AA)Curios[#]() 슬롯에 착용하여 사역마가 주는 효과를 "
        "이용하세요.\n\\\n\\\n"
        "사역마 반지에서 풀려난 정령은 자신을 풀어 준 사람을 새 주인으로 인정합니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.crafting_rituals.craft_soul_gem.usage.text": (
        "개체를 포획하려면 영혼 보석으로 [#](AA00AA)우클릭[#]()하세요. \\\n"
        "[#](AA00AA)우클릭[#]()하면 다시 풀어 줍니다.\n\\\n\\\n"
        "보스는 포획할 수 없습니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.crafting_rituals.fragile_soul_gem.use.text": (
        "개체를 포획하려면 영혼 보석으로 [#](55FF55)우클릭[#]()하세요. \\\n"
        "[#](55FF55)우클릭[#]()하면 다시 풀어 줍니다.\n\\\n\\\n"
        "보스는 포획할 수 없습니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.crafting_rituals.dimensional_battlefield.enchantment.text": (
        "  무기에는 마법을 부여할 수 있습니다. 약탈은 전리품 수량을 늘립니다.\n"
        "  \\\n"
        "  날카로움은 처리 속도를 높이지만, 대상 몹이 해당 마법에 취약하다면 강타,\n"
        "  살충 또는 찌르기만큼 효과적이지는 않습니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.getting_started.bookshelf_binding.automation.text": (
        "[](item://minecraft:chiseled_bookshelf) 위에 [#](00AA00)영혼 사전[#]()을 넣은 "
        "희생의 그릇을 놓으면 이 과정을 자동화할 수 있습니다.\n"
        "그릇이 레드스톤 신호를 받으면 안에 든 책들이 속박됩니다.\\\n\\\n"
        "참고: 구리와 은 희생의 그릇도 사용할 수 있습니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.getting_started.bookshelf_binding.info.text": (
        "속박의 책을 하나씩 만드는 일이 지루한가요? \\\n"
        "책장 속박을 사용해 보세요!\n"
        "월드 내 상호작용으로 한 번에 **6개**까지 속박할 수 있어 더는 일반적인 "
        "형태 없는 조합법을 반복하지 않아도 됩니다. \\\n\\\n"
        "[](item://minecraft:chiseled_bookshelf)에 책을 넣고 "
        "[#](AA00AA)Shift-우클릭[#]()한 채 [#](00AA00)영혼 사전[#]()을 사용하세요.\n"
    ),
    "book.occultism.dictionary_of_spirits.getting_started.divination_rod.troubleshooting.text": (
        "막대가 블록을 강조하지 않으면 다음 방법을 시도하세요.\n"
        "- Theurgy 모드가 설치되어 있으면 입자 효과를 대신 사용하므로 비디오 설정에서 "
        "입자를 '모두' 또는 '감소'로 설정하세요.\n"
        "- 인스턴스의 /config 폴더에서 occultism-client.toml을 열고 "
        "useAlternativeDivinationRodRenderer = true로 설정하세요.\n"
    ),
    "book.occultism.dictionary_of_spirits.getting_started.divination_rod.config.text": (
        "점술 막대에는 모든 광석을 찾는 추가 기능이 있지만,\n"
        " 기본 기능이 아니므로 따로 활성화해야 합니다.\n"
        " 이런 점술에는 탐욕스러운 사역마나 Theurgy 모드를 사용하는 것을 권장합니다.\n"
        " Occultism 점술 막대에서 직접 활성화하려면\n"
        " '서버 설정 > 아이템'에서 'Divination c:ores'를 'on'으로 설정하세요.\n"
    ),
    "book.occultism.dictionary_of_spirits.getting_started.books_of_calling.usage.text": (
        "- 허공을 [#](ad03fc)우클릭[#]()해 설정 화면 열기\n"
        "- 블록을 [#](ad03fc)Shift-우클릭[#]()해 설정 화면에서 선택한 동작 적용\n"
        "- 정령을 [#](ad03fc)Shift-우클릭[#]()해 포획(같은 유형이어야 함)\n"
        "- 포획한 정령이 든 책으로 [#](ad03fc)우클릭[#]()해 정령 풀어 주기\n"
    ),
    "book.occultism.dictionary_of_spirits.getting_started.first_ritual.start_ritual.text": (
        "마지막으로 앞에서 만든 **속박된** 속박의 책을 들고 "
        "[](item://occultism:golden_sacrificial_bowl)을 [#](ad03fc)우클릭[#]()한 뒤 "
        "분쇄기가 소환될 때까지 기다리세요.\n\\\n\\\n"
        "이제 분쇄기 근처에 알맞은 광석을 떨어뜨리고 가루로 만들 때까지 기다리면 "
        "됩니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.getting_started.demons_dream.harvest_effect.text": (
        "악마의 꿈에는 **[#](ad03fc)이계[#]() 재료와 상호작용하는 능력**이라는 "
        "부가 효과도 있습니다.\n"
        "이 능력은 악마의 꿈에만 있으며, 다른 방법으로 [#](ad03fc)제3의 눈[#]()을 "
        "얻어도 사용할 수 없습니다.\n"
        "악마의 꿈 효과를 받는 동안 이계석과 이계 나무를 **채취**할 수 있습니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.possess_djinni.uses2.text": (
        "- [박쥐 사역마](entry://familiar_rituals/familiar_bat)\n"
        "- [크툴루 사역마](entry://familiar_rituals/familiar_cthulhu)\n"
        "- [악마 사역마](entry://familiar_rituals/familiar_devil)\n"
        "- [드래곤 사역마](entry://familiar_rituals/familiar_dragon)\n"
        "- [머리 없는 래트맨 사역마](entry://familiar_rituals/familiar_headless)\n"
        "- [비홀더 사역마](entry://familiar_rituals/familiar_beholder)\n"
        "- [요정 사역마](entry://familiar_rituals/familiar_fairy)\n"
        "- [키메라 사역마](entry://familiar_rituals/familiar_chimera)\n"
        "- [미라 사역마](entry://familiar_rituals/familiar_mummy)\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.paraphernalia.crystal.text": (
        "수정은 양초만으로 닿을 수 없는 수준까지 마법진의 안정성을 높여, 더 불안정한 "
        "의식을 수행할 수 있게 합니다.\\\n\\\n"
        "다음 페이지에서 조합법을 확인하세요.\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.summon_afrit.uses.text": (
        "- [아프리트 분쇄기](entry://summoning_rituals/summon_crusher_t3)\n"
        "- [아프리트 제련공](entry://summoning_rituals/summon_smelter_t3)\n"
        "- [아프리트 결정화기](entry://summoning_rituals/summon_crystallizer_t3)\n"
        "- [뇌우](entry://summoning_rituals/weather_magic@thunder)\n"
        "- [비 오는 날씨](entry://summoning_rituals/weather_magic@rain)\n"
    ),
    "book.occultism.dictionary_of_spirits.possession_rituals.possess_strong_breeze.description.text": (
        "강한 야생 브리즈는 '흐름으로 벼린' 일반 브리즈의 강화형입니다. "
        "[](item://minecraft:heavy_core)을 얻기 위한 최종 대상이며, 보너스로 "
        "[](item://minecraft:flow_armor_trim_smithing_template), "
        "[](item://minecraft:flow_banner_pattern), "
        "[](item://minecraft:flow_pottery_sherd), "
        "[](item://minecraft:music_disc_creator)을 얻을 수 있습니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.storage.storage_system_automation.extraction.text": (
        "아이템을 추출하면, 특히 아이템 필터가 달린 파이프를 사용할 때 성능 문제가 "
        "생길 수 있습니다.\n 이는 거대한 저장소 전체에서 해당 아이템을 하나씩 "
        "검색하기 때문입니다.\n \\\n \\\n 성능을 *크게* 높이려면 운반 정령을 사용해\n"
        " 저장소 작동기나 안정된 웜홀에서 아이템을 꺼내세요. 정령이\n"
        " 저장 시스템 바로 옆 상자에 아이템을 넣고 파이프가 그 상자에서\n"
        " 꺼내더라도, 파이프가 직접 추출할 때보다 성능이 **훨씬** 좋습니다.\n"
    ),
    "book.occultism.dictionary_of_spirits.storage.storage_controller.usage.text": (
        "[](item://occultism:storage_controller)를 제작한 뒤(다음 페이지 참고) 월드에 "
        "놓고 빈손으로 [#](55FF55)우클릭[#]()하세요.\n"
        " 저장소 제어기 GUI가 열리며, 이후에는 아주 큰 "
        "[](item://minecraft:shulker_box)처럼 사용할 수 있습니다.\n"
    ),
    "gui.occultism.spirit.transporter.tag_filter": (
        "필터링할 태그를 세미콜론(;)으로 구분해 입력하세요.\n"
        '예: "c:ores;*logs*"\n'
        '별표(*)는 모든 문자와 일치합니다. 예를 들어 "*ore*"는 모든 모드의 광석 '
        '태그와 일치합니다. 아이템을 필터링하려면 아이템 ID 앞에 "item:"을 붙이세요. '
        '예: "item:minecraft:chest"'
    ),
    "item.occultism.ritual_dummy.craft_dark_iesnium_sacrificial_bowl.tooltip": (
        "어둠의 이에스늄 의식 그릇은 모든 의식을 평소 시간의 4분의 1만에 수행합니다. "
        "그 밖의 기능은 어둠의 황금 의식 그릇과 같습니다."
    ),
    "jei.occultism.ingredient.tallow.description": (
        "정육점 칼로 §2돼지§r, §2소§r, §2양§r, §2말§r, §2라마§r 같은 동물을 "
        "처치하면 수지를 얻습니다."
    ),
    "jei.occultism.ingredient.iesnium_ore.description": (
        "네더에서 발견됩니다. §6제3의§r §6눈§r 상태가 활성화되어 있을 때만 보입니다. "
        "자세한 내용은 §6영혼§r §6사전§r §6항목§r을 참고하세요."
    ),
    "jei.occultism.ingredient.spirit_fire.description": (
        "§6악마의 꿈 열매§r를 땅에 던지고 불을 붙이세요. 자세한 내용은 "
        "§6영혼 사전§r을 참고하세요."
    ),
    "jei.occultism.ingredient.spawn_egg.familiar_goat.description": (
        "키메라 사역마에게 황금 사과를 먹이면 염소 사역마를 얻을 수 있습니다. "
        "자세한 내용은 §6영혼§r §6사전§r §6항목§r을 참고하세요."
    ),
    "tag.item.curios.hands": "손",
    "quest.0B3EA604C5172D98.quest_desc": [
        "어떤 &c&m악마&r &9친구&r를 소환할지 지정하려면 특정한 "
        "&b속박의 책&r을 만들어야 합니다.\\n\\n"
        "이 책을 만들려면 검은색 염료를 &d정령불&r로 정화해 정제된 잉크를 "
        "얻으세요. 이것으로 &a폴리엇&r 악마를 소환하는 첫 속박의 책을 만듭니다.",
        "",
        "또는 빈 속박의 책을 만든 뒤 필요한 의식 등급에 맞게 염색할 수도 있습니다.",
    ],
    "quest.5316DF321B45D2CA.quest_desc": [
        "&dOccultism&r에 오신 것을 환영합니다!\\n\\n"
        "이 모드는 &c&m악마들&r, 즉 &b정령&r의 도움을 받아 여러 방식으로 플레이어를 "
        "돕습니다. 걱정하지 마세요. 대부분은 친절해요. &o대부분은요&r.\\n\\n"
        "시작하려면 &a악마의 꿈 열매 씨앗&r을 구하세요."
    ],
    "quest.6581D4AF1A6DE230.quest_desc": [
        "악마는 양초를 좋아합니다. 아마도요.\\n\\n"
        "친구를 소환하는 거의 모든 의식에는 양초가 필요합니다. &a정육점 칼&r로 "
        "돼지, 소, 양, 말 또는 상인 라마를 처치해 &a수지&r를 얻으세요. 특히 상인 "
        "라마를 찾아보세요. 좋은 양초가 된다고 들었거든요. &m방금 지어낸 말은 "
        "절대 아닙니다&r.\\n\\n"
        "바닐라 양초도 사용할 수 있습니다!\\n\\n"
        "&9정령 조율 수정&r도 여러 의식에 쓰이므로 지금 만들어 두는 것이 좋습니다!"
    ],
    "quest.690B89D23134B624.quest_desc": [
        "분필을 챙겨 &dRonaza's Contact&r 의식을 그리고 궁극의 분필*을 만들 준비를 "
        "하세요!",
        "",
        "16가지 분필을 모두 들고 다니는 대신 무지개 분필로 색이 변하며 어느 색으로도 "
        "인정되는 문양을 그릴 수 있습니다!",
        "",
        "&8*기초 분필은 포함하지 않습니다. 기초 분필까지 대신하려면 공허 분필을 "
        "만드세요&r",
    ],
    "quest.5ACE97EE75813006.quest_desc": [
        "&d의식&r에 관한 핵심 정보입니다. 기본부터 알아보죠.",
        "",
        "&l의식 등급&r:",
        "",
        "의식은 불러내는 악마의 힘에 따라 기본적으로 네 등급으로 나뉩니다. 첫 등급은 "
        "&e폴리엇&r, 그다음은 &a지니&r, &c아프리트&r, &9마리드&r입니다. 일부 의식은 "
        "&6속박되지 않은 아프리트&r처럼 등급 사이에 속합니다.",
        "",
        "&l의식 유형&r:",
        "",
        "의식은 다섯 유형이지만 진행에는 네 유형만 필요합니다. 주요 세 유형은 "
        "&9소환 의식&r, &5빙의 의식&r, &6주입 의식&r이며 퀘스트에서 처음 등장할 때 "
        "설명합니다. 네 번째는 세 유형의 요소를 조합해 악마를 직접 쓰지 않고 특별한 "
        "효과를 내는 &d악마 없는&r &d의식&r입니다.",
        "",
        "다섯 번째인 &e사역마 의식&r은 진행에 필요하지 않지만 유용한 친구를 소환해 "
        "도움을 받을 수 있습니다!",
        "",
        "&l분필&r:",
        "",
        "분필은 기초 분필과 유색 분필로 나뉩니다.",
        "",
        "기초 분필은 모든 의식에 쓰이며, 흰색 분필에서 시작해 검은색 분필까지 등급이 "
        "높을수록 색이 어두워집니다.",
        "",
        "유색 분필을 가장 자주 사용하지만, 기초 분필과 달리 색 자체가 힘의 세기를 "
        "뜻하지는 않습니다.",
    ],
    "quest.145C8235BCCB9BA8.quest_subtitle": "편히 잠들기를, 벳시",
    "quest.0A25276925EB0CBA.quest_subtitle": "이 신성한 보물로 소환하노라...",
    "quest.1DE0F289821F55D1.title": "&a분필 재료 마련",
    "task.2C5C6F411E2F0CAF.title": "#c:dusts/netherite 중 아무거나",
    "task.523951BF097BA61F.title": "#c:dusts/emerald 중 아무거나",
    "task.3621D48E2CFAF2C2.title": "#c:wools 중 아무거나",
}

QUEST_EXACT_KEYS = {
    "quest.00A6020BC979947F.quest_desc": [
        "새로 소환한 &9마리드 분쇄기&r로 메아리 조각과 이에스늄 주괴를 분쇄하세요. "
        "두 재료를 발광 먹물 주머니와 조합하면 청록색 분필을 만들 수 있습니다."
    ],
    "quest.00A6020BC979947F.title": "&3청록색 분필",
    "quest.03250A0202C25E80.quest_desc": [
        "&4Tibira's Attraction&r으로 소환한 &9속박되지 않은 마리드&r를 처치하면 "
        "&9마리드 정수&r를 얻습니다. 이 정수로 가장 높은 등급의 유색 분필인 파란색 "
        "분필을 만들 수 있습니다."
    ],
    "quest.03250A0202C25E80.title": "&9파란색 분필",
    "quest.06B9D8973E9C6A2C.quest_desc": [
        "Occultism 챕터에 Ars Nouveau 아이템이 있는 이유는 두 모드를 잇는 Ars "
        "Ocultas 때문입니다. 폴리엇 분쇄기 같은 정령은 격리 항아리 안에서도 일할 수 "
        "있습니다. 파이프로 항아리에 아이템을 넣으면 정령이 처리한 뒤 인접한 보관함으로 "
        "내보냅니다. 항아리 아래쪽이 가장 안정적인 출력 면이며, 내보낼 보관함이 없으면 "
        "아이템을 월드에 떨어뜨립니다."
    ],
    "quest.06B9D8973E9C6A2C.quest_subtitle": "정령도 격리 항아리에서 일할 수 있습니다",
    "quest.08697EB269B011FD.quest_desc": [
        "&dRonaza's Contact&r으로 &b이에스늄 의식 그릇&r을 엘드리치 성배로 "
        "업그레이드할 수 있습니다. 의식에 사용하면 완료 시간을... 완전히 없애 줍니다.",
        "",
        "맞습니다. 엘드리치 성배를 사용하면 모든 의식이 즉시 완료됩니다!",
    ],
    "quest.0D18BBB04693885A.quest_desc": [
        "Strigeor's Higher Binding은 &6주입 의식&r의 두 번째 등급입니다. 여러 용도가 "
        "있지만, 진행에 꼭 필요한 것은 주입된 곡괭이와 회색 반죽입니다."
    ],
    "quest.0F412542271B6254.quest_desc": [
        "&dOccultism&r을 계속 진행하기 전에 마법진 업그레이드 방식을 알아보겠습니다. "
        "같은 유형의 마법진은 이전 등급의 마법진을 바탕으로 확장됩니다.\n\n따라서 "
        "&a지니&r 소환용과 &a폴리엇&r 소환용 마법진을 따로 만들 필요 없이, 하나의 "
        "마법진으로 여러 등급의 의식을 수행할 수 있습니다. 예를 들어 &9Fatma's "
        "Incentivized Attraction&r은 이전의 모든 소환 마법진을 포함합니다.\n\n이 구조를 "
        "고려해 19x19 크기의 공간을 4곳 마련하는 것을 권장합니다. 소환, 주입, 빙의, "
        "기타 의식(야생 및 엘드리치)용으로 하나씩 사용하세요."
    ],
    "quest.0F412542271B6254.title": "마법진 안내",
    "quest.0BD6365534BF04D5.quest_desc": [
        "연두색 분필을 얻었으니 &5빙의 의식&r을 알아볼 차례입니다. 이 의식은 닭, 벌, "
        "박쥐 같은 살아 있는 몹을 제물로 요구한다는 점이 다릅니다. 의식이 복잡할수록 더 "
        "큰 제물이 필요합니다.",
        "",
        "필요한 아이템과 속박의 책을 황금 희생의 그릇에 모두 넣어도, 문양 위의 제물을 "
        "처치하기 전에는 의식이 시작되지 않습니다.",
        "",
        "빈 영혼 보석, 항아리, 몹 감금 도구, 양자 포획기 같은 몹 포획 아이템을 미리 "
        "준비하는 것이 좋습니다!",
        "",
        "&5빙의 의식&r의 첫 등급인 &eHeidryn's Lure&r는 스켈레톤 해골과 엔드 돌 "
        "같은 평범한 아이템을 얻는 데만 쓰입니다. 따라서 두 번째 등급인 &aIhagan's "
        "Enthrallment&r으로 바로 넘어가도 됩니다.",
    ],
    "quest.11A0593C0E2E6A35.quest_desc": [
        "&eEziveus' Spectral Compulsion&r으로 여러 자연 블록에 힘을 주입해 &2자연의 "
        "반죽&r을 만드세요. 이 반죽을 불순한 흰색 분필과 조합하면 녹색 분필이 됩니다."
    ],
    "quest.145C8235BCCB9BA8.quest_desc": [
        "모든 분필을 모으려면 적대적인 &c아프리트&r를 소환해 처치해야 합니다.",
        "",
        "&5빙의 의식&r은 아니지만 살아 있는 제물이 필요합니다. 이번에는 소를 희생해야 "
        "합니다. 미안해요, 벳시!",
    ],
    "quest.172D2A634E849562.quest_desc": [
        "&c이에스늄&r을 채굴할 수 있게 되었으니 악마에게 광산 일을 시킬 수 있습니다... "
        "아니, 광석 수집을 도와달라고 하는 겁니다. 악마를 부려 먹는 건 절대 아니에요."
        "\n\n먼저 악마 채굴 차원에 연결되는 &d차원 광산 갱도&r를 만드세요. 광부 악마가 "
        "담긴 램프를 광산 갱도 안에 놓아야 작동합니다. 어느 등급이든 퀘스트는 완료되지만, "
        "등급이 높을수록 작업 속도와 이에스늄 채굴 확률이 높아집니다.\n\n광산 갱도는 "
        "아이템을 자동으로 내보내지 않습니다. 호퍼, 운반 정령, 아이템 파이프 등으로 "
        "꺼내야 하며, 저장 한도를 넘은 아이템은 사라집니다."
    ],
    "quest.172D2A634E849562.title": "&c악마 채굴",
    "quest.1848F431D0380DA9.quest_desc": [
        "&aStrigeor's Higher Binding&r으로 분필을 수리하듯, &cSevira's Permanent "
        "Confinement&r으로 아프리트의 힘을 이용해 아이템을 수리할 수 있습니다.",
        "",
        "이 의식은 거의 모든 아이템을 수리하므로 &e악마 광부&r, 도구, 방어구의 내구도를 "
        "완전히 복구할 수 있습니다!",
        "",
        "수리한 아이템은 접두·접미 속성과 마법 부여 등 기존 속성을 모두 유지합니다.",
    ],
    "quest.1B5177A774FCEF64.quest_desc": [
        "악마 친구들의 도움을 받기 전에 의식의 핵심 도구인 &a분필&r을 만들어야 합니다."
        "\n\n의식 등급이 높아질수록 여러 색의 분필이 필요합니다. 먼저 가장 만들기 쉬운 "
        "&b흰색 분필&r부터 준비하세요.\n\n이계석은 화로에 굽고 이계 나무 원목은 "
        "&d정령불&r에 던지세요. 얻은 재료로 불순한 흰색 분필을 만들 수 있습니다."
        "\n\n분필을 정화하려면 &d정령불&r에 던지면 됩니다. 정화된 분필로 땅을 "
        "우클릭하면 &m악마의&r 멋진 문양이 그려집니다. 지우기 번거로우니 &a분필 "
        "솔&r도 꼭 만들어 두세요."
    ],
    "quest.1BDB369FD243D4C6.quest_desc": [
        "Occultism에서 가장 유용한 아이템 중 하나인 &b이에스늄 모루&r는 바닐라 모루의 "
        "강력한 상위 버전입니다.",
        "",
        "&9Uphyxes' Inverted Tower&r으로 만들며 다음 기능이 있습니다.",
        "",
        "- 부서지지 않습니다.",
        "- 합친 아이템에 적용되는 모든 마법 부여의 최대 레벨이 1 증가합니다.",
        "- 표시된 예상 경험치의 절반만 소모합니다(내림 처리하므로 25라면 12를 소모합니다).",
        "- 같은 아이템을 반복해서 편집할 때 경험치 증가 폭이 작습니다.",
        '- 아이템을 편집할 수 있는 최대 경험치 레벨, 즉 "너무 비쌉니다!"가 표시되는 '
        "기준이 높아집니다.",
    ],
    "quest.1DE0F289821F55D1.quest_desc": [
        "폴리엇 분쇄기를 얻었으니 &m부려 먹어서&r 정중히 부탁해서 &e엔드 돌&r, "
        "&9흑요석&r, &7방해석&r을 분쇄하세요. 이 재료로 새 분필을 만들 수 있습니다!"
    ],
    "quest.1EB887F8072439A3.quest_desc": [
        "&9Fatma's Incentivized Attraction&r으로 &9마리드 분쇄기&r를 소환하거나 "
        "&aOphyx' Calling&r으로 &a지니 분쇄기&r를 소환하세요. 얼음, 꽁꽁 언 얼음, "
        "푸른얼음을 각각 분쇄한 뒤 조합하면 연한 파란색 분필을 만들 수 있습니다."
    ],
    "quest.1EB887F8072439A3.title": "&b연한 파란색 분필",
    "quest.2960FFE0C53DFEB1.quest_desc": [
        "&cSevira's Permanent Confinement&r은 &6주입 의식&r의 세 번째 등급이며, 주로 "
        "다음 등급의 기초 분필인 검은색 분필을 만드는 데 사용합니다.",
        "",
        "의식의 준비 시간과 수행 시간을 크게 줄여 주는 아이템도 만들 수 있습니다.",
    ],
    "quest.2A3683BF7E50EF83.quest_desc": [
        "지금까지 필요한 &3이계&r 재료 대부분은 정령불로 얻었지만, &3이계&r의 광석을 "
        "찾으려면 &3제3의 눈&r이 필요합니다.",
        "",
        "이 광석은 전용 곡괭이로만 캘 수 있습니다. &d정령 조율 곡괭이 머리&r에 "
        "악마를 주입해 새로운 광석을 채굴할 곡괭이를 만드세요.",
    ],
    "quest.2A5004EB99AE4F96.quest_desc": [
        "앞으로도 이계 재료가 더 필요하지만, &7제3의 눈&r 효과가 필요할 때마다 "
        "&c악마의 꿈 열매&r를 먹는 일은 번거롭습니다.",
        "",
        "이럴 때 &d이계 고글&r을 사용하세요! Curios 슬롯에 장착해도 제3의 눈 효과를 "
        "얻을 수 있습니다.",
    ],
    "quest.2A5004EB99AE4F96.title": "거래 도구: 이계 고글",
    "quest.2AD68066C1948C90.quest_desc": [
        "첫 &e폴리엇 분쇄기&r도 훌륭하지만, 원광석 하나를 가루 6개로 만들어 주는 악마도 "
        "소환할 수 있습니다.",
        "",
        "바로 &9마리드 분쇄기&r입니다. 소환하려면 &9Fatma's Incentivized "
        "Attraction&r을 사용하세요.",
    ],
    "quest.2CF96A264EB5522C.quest_desc": [
        "&9Uphyxes' Inverted Tower&r는 &6주입 의식&r의 최고 등급입니다. 다른 세 "
        "등급보다 용도는 적지만 Occultism의 최종 단계에 필요합니다.",
        "",
        "주요 용도는 마젠타색 분필의 핵심 재료인 드래고니스트 가루 제작입니다.",
    ],
    "quest.2E68E1D96B25336D.quest_desc": [
        "&6Odus' Open Convocation&r으로 소환한 아프리트 빙의 좀비화 피글린을 처치해 "
        "악마 고기를 얻으세요. 이 고기로 분홍색 분필을 만들 수 있습니다."
    ],
    "quest.2E68E1D96B25336D.title": "&d분홍색 분필",
    "quest.2AD68066C1948C90.title": "&9Fatma's Incentivized Attraction",
    "quest.2CF96A264EB5522C.title": "&9Uphyxes' Inverted Tower",
    "quest.30C5B597610F4AFB.quest_desc": [
        "Eziveus' Spectral Compulsion으로 가장 먼저 만들 핵심 아이템은 연구 파편 "
        "가루입니다. 분쇄한 에메랄드와 조합하면 연두색 분필을 만들 수 있습니다!"
    ],
    "quest.30C5B597610F4AFB.title": "&a연두색 분필",
    "quest.33106E24A3B5DDD8.quest_desc": [
        "다음 목표는 네더에서 &e이에스늄 광석&r을 찾는 것입니다.",
        "",
        "&3제3의 눈&r 효과가 없으면 네더랙처럼 보입니다. &d이계 고글&r을 꼭 "
        "착용하세요!",
        "",
        "&a점술 막대&r를 네더랙에 조율한 뒤 우클릭을 길게 누르세요. 잠시 후 가장 "
        "가까운 이에스늄 광석 방향으로 입자가 날아갑니다. 광석은 &d주입된 곡괭이&r로만 "
        "캘 수 있습니다!",
        "",
        "일반적인 방법으로는 광석을 가루 두 배로 만들 수 없습니다. 폴리엇 분쇄기를 "
        "사용해 원광석 하나당 주괴 두 개를 얻으세요!",
        "",
        "참고: 입자가 보이지 않으면 비디오 설정에서 입자 표시가 켜져 있는지 확인하세요!",
        "",
        "{image:atm:textures/questpics/occultism/iesniumexample.png width:200 height:175 align:1}",
    ],
    "quest.33106E24A3B5DDD8.title": "&c이에스늄: 이계의 광석",
    "quest.367E891A50991436.quest_desc": [
        "&cSevira's Permanent Confinement&r으로 여러 위더 재료와 네더라이트를 조합하면 "
        "위더라이트 가루 3개를 만들 수 있습니다. 이 가루로 최고 등급의 기초 분필인 "
        "검은색 분필을 만드세요."
    ],
    "quest.38A1295878B68F83.quest_desc": [
        "아니요, 그런 뜻은 아닙니다.",
        "",
        "&c아프리트 악마&r는 &c불&r의 악마입니다. 더 강력한 악마라서 아군이 될 수도, "
        "적이 될 수도 있으며 의식이 &c아프리트&r를 얼마나 강하게 통제하는지에 따라 "
        "달라집니다.",
        "",
        "아직 빨간색 분필이 없으므로 &9속박되지 않은&r 악마만 소환할 수 있습니다. "
        "통제할 수 없는 사나운 적이니 전투를 준비하세요.",
    ],
    "quest.38A1295878B68F83.title": "&6Kandar's Opened Conjure",
    "quest.39647A2473F6F7D7.title": "&eEziveus' Spectral Compulsion",
    "quest.3D41D0092D94636B.quest_desc": [
        "악마의 꿈 열매에 불이 붙는다는 사실을 알고 계셨나요?",
        "",
        "&c악마의 꿈 열매&r를 땅에 던지고 불을 붙이면 &d정령불&r이 생깁니다. 이 "
        "불로 오버월드 아이템을 &9이계&r 재료로 바꿀 수 있습니다.",
        "",
        "보기에도 멋집니다.",
    ],
    "quest.3D41D0092D94636B.title": "&9이계의 불꽃",
    "quest.429B5A81DF6C43FE.quest_desc": [
        "&6Odus' Open Convocation&r은 돼지에 &c아프리트&r를 빙의시키는 의식입니다. "
        "빨간색 분필 없이 수행하므로 &9속박되지 않은&r 악마만 소환할 수 있습니다.",
        "",
        "소환된 &c아프리트&r 빙의 좀비화 피글린을 처치하면 분홍색 분필 재료인 악마 고기를 "
        "떨어뜨립니다.",
        "",
        "&4경고: 악마 고기를 충분히 모으려면 이 의식을 여러 번 수행해야 할 수 있습니다.",
    ],
    "quest.429B5A81DF6C43FE.title": "&6Odus' Open Convocation",
    "quest.42F50CE7FE715583.quest_desc": [
        "마법 저장소의 적재량을 늘리려면 &d저장소 안정기&r를 만드세요.",
        "",
        "안정기는 저장소 작동기의 기반이 아니라 차원 행렬 부분을 정확히 향해야 합니다. "
        "최대 5블록 떨어진 곳에 놓을 수 있지만, 행렬 사이를 다른 블록이 가리면 안 됩니다.",
        "",
        "더 높은 등급으로 바꾸려고 안정기를 부숴도 보관 중인 아이템은 사라지지 않습니다. "
        "다만 안정기를 다시 놓거나 업그레이드하기 전까지 새 아이템을 넣을 수 없습니다.",
        "",
        "아래에서 간단한 설치 예시를 확인하세요!",
        "",
        "{image:atm:textures/questpics/occultism/storageupgradeexample.png width:200 height:150 align:1}",
    ],
    "quest.42F50CE7FE715583.title": "&a마법 저장소 업그레이드",
    "quest.47358ADC1470C82A.quest_desc": [
        "&c악마의 꿈 열매&r는 몸에 아주 좋습니다. 알아 두어야 할 부작용이 조금 있을 "
        "뿐이죠.",
        "",
        "먹으면 일정 확률로 &3제3의 눈&r 효과를 얻어 &9이계&r를 볼 수 있습니다. "
        "겉보기와 실제 모습이 다른 블록이 있으며, 진행에 필요한 재료를 찾으려면 이 "
        "'시야'가 필요합니다.",
        "",
        "열매에 불을 붙여 재료 탐색 대부분을 건너뛰는 방법도 있습니다. 선택은 여러분의 "
        "몫입니다.",
    ],
    "quest.4C873491F6F0FFAF.quest_desc": [
        "&d정령불&r로 여러 오버월드 재료를 이계 변종으로 바꿀 수 있습니다. &b제3의 "
        "눈&r 효과를 받은 채 탐험하면 월드에서도 이계 재료를 찾을 수 있습니다. 기본 "
        "재료는 &d정령불&r에 던져 직접 변환할 수도 있습니다.",
        "",
        "&b안산암&r은 영구적인 &d정령불&r을 피울 수 있는 &3이계석&r으로 바뀝니다.",
        "",
        "&a참나무 묘목&r은 겉보기에는 같은 &9이계 참나무 묘목&r으로 바뀝니다. 자란 "
        "나무도 평범해 보이지만, &b제3의 눈&r 효과를 받으면 이계 변종으로 채취할 수 "
        "있습니다.",
        "",
        "&b제3의 눈&r 효과 중에도 일반 참나무 원목으로 바뀐다면 나무 위쪽부터 "
        "채취해 보세요.",
        "",
        "&e다이아몬드&r는 이후 여러 조합법에 쓰이는 &d정령 조율 보석&r으로 바뀝니다.",
    ],
    "quest.4C873491F6F0FFAF.title": "&d정령불&r 변환",
    "quest.4ABACE222E647E2C.quest_desc": [
        "희생 제단은 Ars Ocultas가 제공하는 또 다른 도구로, 제물 처리를 자동화합니다."
        "\n\n중앙 그릇 아래에 제단을 놓으세요. 제물로 쓸 생물이 든 격리 항아리와 원천 "
        "항아리가 가까이 있으면, 살아 있는 제물 대신 원천을 소모할 수 있습니다."
    ],
    "quest.4ABACE222E647E2C.quest_subtitle": "원천으로 제물 대체",
    "quest.4CE571F942461909.quest_desc": [
        "의식 가방은 편리하지만 블록을 하나씩 놓는 데 시간이 오래 걸립니다. 이제 "
        "&cSevira's Permanent Confinement&r 의식을 수행할 수 있으니 장인 의식 가방을 "
        "만드세요!",
        "",
        "장인 의식 가방은 일반 의식 가방과 비슷하지만 필요한 아이템을 즉시 모두 "
        "배치합니다. 황금 희생의 그릇을 우클릭하면 분필 문양을 지우고 해골, 양초, 수정 "
        "등을 회수해 가방에 넣을 수도 있습니다.",
        "",
        "단, 분필 내구도는 복구하지 않습니다.",
    ],
    "quest.4F35D04721DFC9FF.quest_desc": [
        "처음 배울 의식은 &9소환 의식&r입니다. 여러 악마를 소환해 분쇄, 제련 등 "
        "다양한 작업을 맡길 수 있습니다.",
        "",
        "첫 의식으로 &a폴리엇 분쇄기&r를 소환하세요. 이 악마가 고급 분필에 필요한 "
        "재료를 분쇄해 줍니다!",
        "",
        "먼저 속박되지 않은 책과 &a영혼 사전&r을 조합대에서 합치세요. 악마가 책에 "
        "속박되며, 이 책을 의식에 사용합니다.",
        "",
        "이제 영혼 사전을 열고 왼쪽의 &d마법진&r 탭에서 &bAviar's Circle&r을 "
        '선택하세요. 앞 내용을 조금 읽어야 열릴 수 있으며, "모두 읽음으로 표시"를 눌러 '
        "책 전체를 잠금 해제할 수도 있습니다.",
        "",
        "오른쪽 이미지의 왼쪽 아래에 있는 눈 아이콘을 누르면 월드에 의식 구조의 윤곽을 "
        "표시할 수 있습니다.",
        "",
        "구조를 완성한 뒤 중앙 그릇에서 수평 8블록 안에 희생의 그릇 4개 이상을 놓고 "
        "재료를 올리세요. 속박된 책을 황금 희생의 그릇에 넣으면 의식이 시작됩니다!",
        "",
        "완성된 의식은 아래와 같습니다.",
        "",
        "{image:atm:textures/questpics/occultism/aviarcirclenew.png width:200 height:200 align:1}",
    ],
    "quest.53DEA3DFEDC4809E.quest_desc": [
        "걱정하지 마세요. Abras 계열의 마지막 의식입니다. &9마리드&r를 소환하지만, "
        "빨간색 분필을 사용해도 악마를 &9속박&r할 만큼 강하지 않아 직접 싸워야 합니다.",
        "",
        "대부분의 제물과 달리 이 의식에는 삼지창을 사용합니다. 완성된 의식 원 위에서 "
        "몹을 죽이는 대신 중앙 그릇에 삼지창을 던지면 의식이 시작됩니다.",
    ],
    "quest.53DEA3DFEDC4809E.title": "&4Tibira's Attraction",
    "quest.56EC79AF11B0869E.quest_desc": [
        "&9Xeovrenth Adjure&r는 &5빙의 의식&r의 최고 등급입니다. 용도는 두 가지로, "
        "갈색 분필의 주재료인 잔혹 정수를 만들거나 사실상 불사이며 더 강한 철 골렘인 "
        "이에스늄 골렘을 소환하는 것입니다."
    ],
    "quest.57282D7E31EE61EE.quest_desc": [
        "&a원시 이에스늄 광석&r을 몇 개 모았다면 첫 주괴로 &d이에스늄 곡괭이&r를 "
        "만드세요. 주입된 곡괭이처럼 이에스늄을 채굴할 수 있고 내구도도 훨씬 높습니다.",
        "",
        "앞으로 편해지려면 꼭 하나 만들어 두세요!",
    ],
    "quest.57282D7E31EE61EE.title": "&a이계의 곡괭이&r",
    "quest.5FE507DAEE770507.quest_desc": [
        "&b연한 파란색 분필&r을 만들려고 &9마리드 분쇄기&r까지 얻고 싶지 않다면 "
        "&a지니 분쇄기&r를 사용해도 됩니다. &aOphyx' Calling&r은 &a지니&r를 소환하는 "
        "의식이며 악마 아내와 악마 남편도 소환할 수 있습니다. &a지니&r는 폴리엇보다 광석을 "
        "효율적으로 분쇄하지만 &c아프리트&r나 &9마리드&r보다는 느립니다. 얼음을 녹이지 "
        "않고 분쇄할 수도 있습니다."
    ],
    "quest.5FE507DAEE770507.title": "&aOphyx' Calling",
    "quest.61999669BDE127F9.quest_desc": [
        "의식을 반복해서 만들면 분필의 내구도가 빠르게 줄어듭니다.",
        "",
        "분필이 부서지기 직전이지만 새 분필을 만드는 의식을 처음부터 다시 하기 싫다면 "
        "이 수리 의식을 사용하세요!",
        "",
        "&a지니&r의 힘으로 어떤 색의 분필이든 내구도를 최대로 복구할 수 있습니다!",
        "",
        "Forbidden and Arcanus의 &aEternal Stella&r처럼 분필을 영구히 보존하는 "
        "아이템을 사용하는 방법도 있습니다!",
    ],
    "quest.61999669BDE127F9.quest_subtitle": "부수면 &m우리가&r 악마가 고쳐 드립니다!",
    "quest.666EA8B8F13EB292.title": "&d빈 영혼 보석",
    "quest.6CC5FE34778F0DFA.quest_desc": [
        "모드팩을 하다 보면 아이템이 넘쳐납니다. 아직 저장소를 정하지 못했다면 "
        "&d차원 저장소&r가 좋은 선택입니다!",
        "",
        "먼저 &d차원 저장소 작동기&r를 제작해 월드에 놓으세요. 셜커 상자처럼 블록을 "
        "부숴도 안에 든 아이템은 사라지지 않습니다.",
        "",
        "기본적으로 슬롯은 128개이며 슬롯마다 같은 아이템을 16스택까지 보관합니다. "
        "단, &5NBT&r 데이터가 있는 아이템은 겹쳐지지 않고 슬롯 하나를 전부 차지하니 "
        "따로 보관하는 편이 좋습니다.",
        "",
        'NBT 데이터가 있는 아이템을 구분하기 어렵다면 저장소 퀘스트라인의 "NBT와 '
        '당신" 퀘스트를 확인하세요!',
    ],
    "quest.6CC5FE34778F0DFA.title": "&c&m악마의&r &d마법 저장소&r!",
    "quest.6CCDEEDA2C99DA66.quest_desc": [
        "이 퀘스트는 AllTheMods 모드팩에 사용하기 위해 &6AllTheMods 스태프&r 또는 "
        "&2커뮤니티 기여자&r가 작성했습니다.\n\n모든 &6AllTheMods&r 팩은 &eAll "
        "Rights Reserved&r로 배포되므로, 명시적인 허가 없이 &6AllTheMods 팀&r이 "
        "출시하지 않은 공개 팩에서 이 퀘스트를 사용할 수 없습니다.\n\n이 퀘스트는 "
        "의도적으로 숨겨져 있습니다. 보인다면 편집 모드에 있는 것입니다."
    ],
    "quest.6FEED25FFAC4101F.quest_desc": [
        "&aStrigeor's Higher Binding&r으로 회색 반죽을 만들 수 있습니다. 불순한 흰색 "
        "분필에 바르면 회색 분필이 됩니다."
    ],
    "quest.74130EB1E4B8586D.quest_desc": [
        "&aIhagan's Enthrallment&r으로 알레이, 박쥐, 벌 또는 앵무새를 희생해 "
        "&6빙의된 벌&r을 소환하세요. 처치하면 주황색 분필의 주재료인 저주받은 꿀을 "
        "떨어뜨립니다!"
    ],
    "quest.74130EB1E4B8586D.title": "&6주황색 분필",
    "quest.78ECC28DD4BA9696.quest_desc": [
        "&d이계&r 재료 대부분은 정령불로 얻을 수 있지만, &9점술 막대&r로 월드에서 직접 "
        "찾을 수도 있습니다.",
        "",
        "먼저 막대를 찾을 재료에 조율하세요. 예를 들어 &8이계석&r을 찾으려면 막대로 "
        "&a안산암&r을 우클릭해 조율합니다.",
        "",
        "조율한 막대를 들고 우클릭을 길게 누르면 가장 가까운 대상 재료 방향으로 입자가 "
        "날아갑니다.",
        "",
        "이계 블록을 채취하려면 여전히 &3제3의 눈&r 효과가 필요합니다.",
    ],
    "quest.78ECC28DD4BA9696.title": "거래 도구: 점술 막대",
    "quest.7BCD4A425CF6199B.quest_desc": [
        "&9Xeovrenth Adjure&r으로 소환한 자비의 염소를 처치해 잔혹 정수를 얻으세요. "
        "코코아 콩과 조합하면 갈색 분필을 만들 수 있습니다."
    ],
    "quest.7BCD4A425CF6199B.title": "&#4E2C00갈색 분필",
    "quest.7F09F8F98C13F11B.quest_desc": [
        "&c희생&r 없는 악마 의식이 어디 있겠어요! :D\n\n대부분의 악마는 아이템만 "
        "원하니 아직 겁먹지 마세요. 하지만 아끼는 소가 있다면 조심해야 합니다. 미안해요, "
        "벳시.\n\n&a희생의 그릇&r에는 의식에 필요한 아이템을 올려놓습니다. 필요한 분필 "
        "문양을 가리지 않는다면 의식 구조 안 어디에 놓아도 됩니다.",
        "",
        "지금은 네 개면 충분하지만, 나중에는 의식 하나에 그릇이 열 개 넘게 필요할 수 "
        "있습니다!\n\n&6황금 희생의 그릇&r은 의식 중앙에서 활성화에 사용하며, 보통 "
        "의식에 맞는 속박의 책을 넣어야 합니다.",
    ],
    "quest.7F59941D62E672B0.quest_desc": [
        "Occultism에는 광석을 분쇄하는 악마만 있는 것이 아닙니다!",
        "",
        "아이템을 옮기거나 나무를 베는 등 여러 작업을 해 주는 악마도 있습니다!",
        "",
        "특별한 강화 효과를 주고 전투까지 돕는 &d사역마&r도 소환할 수 있습니다. "
        "영혼 사전에서 &d사역마 의식&r을 확인하세요!",
    ],
}

RELATED_EXACT_KEYS = {
    "quest.201EE3566D4D3123.quest_desc": [
        "&6Allthemodium&r을 채굴하려면 &c네더라이트&r 등급 이상의 곡괭이가 필요합니다!"
        "\n\n광석을 얻었다면 행운, Occultism 또는 Mekanism으로 처리해 생산량부터 "
        "늘리는 것을 권장합니다. 그다음에는 여러 활용법을 선택할 수 있습니다."
        "\n\n먼저 &6조각&r으로 텔레포트 패드 2개를 만드세요! &7&l채굴 차원&r에서 "
        "&6Allthemodium&r을 더 찾거나 &b&lThe Other&r로 이동해 새로운 모험을 할 수 "
        "있습니다.\n\n그다음에는 &3Vibranium&r을 채굴할 수 있도록 곡괭이를 "
        "업그레이드하는 것을 권장합니다. 이후 선택은 여러분의 몫입니다!",
        "{image:atm:textures/questpics/allthemodium/all_1.png width:100 height:100 align:center}",
    ],
    "quest.61217D80BFF8A858.quest_subtitle": "정말 Occultism과는 아무 관련이 없습니다",
    "quest.216DA9782EBDFF34.quest_desc": [
        "아무리 좋은 책과 아이템이 있어도 악마가 모든 명령에 따르며 노예처럼 일한다는 "
        "설정은 비현실적인 것 같습니다.\n\n그래도 퀘스트를 따라가면 실제로 그렇게 "
        "부릴 수 있습니다."
    ],
    "quest.4195800B4D7631E2.quest_desc": [
        "&6Eziveus' Spectral Compulsion&r 의식으로 &7웜홀 프레임&r, 석영 2개, "
        "&3엔더 진주&r를 조합해 안정된 웜홀을 만들 수 있습니다!"
    ],
    "quest.67C76EDD4BCCFF3F.quest_desc": [
        "&bStrigeor's Higher Binding&r으로 &b빈 영혼 보석&r을 만들 수 있습니다."
        "\n\n몹을 안전하게 운반하거나 &d&l드래곤 영혼&r을 만드는 데 사용합니다."
        "\n\n둘 다 해 보는 것을 권장합니다!"
    ],
    "quest.4E5238F00CEED8B2.quest_desc": [
        "초반에는 원광석을 바로 제련해야 하지만, 그러면 추가 자원을 놓치게 됩니다!"
        "\n\n원광석당 생산량을 두 배로 늘리는 방법은 여럿이며, 가장 쉬운 방법 중 하나는 "
        "&e광석 망치&r를 만들어 사용하는 것입니다.\n\n광석 망치는 원광석 1개를 광석 "
        "가루 2개로 만들며, 가루를 제련하면 주괴 생산량이 두 배가 됩니다!\n\n원광석 "
        "하나에서 더 많이 얻고 싶다면 &5Occultism&r을 확인하세요!"
    ],
    "quest.41FD145B911BD625.title": "이에스늄 벌",
    "quest.6FFFAE334DFAAAAB.title": "이에스늄 의식 그릇",
    "task.10037D5225C2D20E.title": "이에스늄 의식 그릇",
}

LANGUAGE_EXACT_KEYS = {
    "block.occultism.othercobblerock": "이계 조약암",
    "block.occultism.othercobblerock_slab": "이계 조약암 반 블록",
    "block.occultism.othercobblerock_stairs": "이계 조약암 계단",
    "block.occultism.othercobblerock_wall": "이계 조약암 담장",
    "block.occultism.othercobblestone": "이계 조약돌",
    "block.occultism.othercobblestone_slab": "이계 조약돌 반 블록",
    "block.occultism.othercobblestone_stairs": "이계 조약돌 계단",
    "block.occultism.othercobblestone_wall": "이계 조약돌 담장",
    "item.occultism.crushed_ice": "분쇄된 얼음",
    "item.occultism.crushed_packed_ice": "분쇄된 꽁꽁 언 얼음",
    "book.occultism.dictionary_of_spirits.pentacles.craft_afrit.uses.text": (
        "- [차원 전장](entry://crafting_rituals/dimensional_battlefield)\n"
        "- [이에스늄 의식 그릇]"
        "(entry://crafting_rituals/craft_iesnium_sacrificial_bowl)\n"
        "- [이에스늄 정육점 칼](entry://crafting_rituals/iesnium_butcher_knife)\n"
        "- [3등급 저장소 안정기](entry://crafting_rituals/craft_stabilizer_tier3)\n"
        "- [아프리트 심층 광석 광부](entry://crafting_rituals/craft_afrit_miner)\n"
        "- [장인 의식 가방](entry://crafting_rituals/artisanal_ritual_satchel)\n"
        "- [아이템 수리](entry://crafting_rituals/repair)\n"
        "- [위더라이트 가루](entry://pentacles/black_chalk)\n"
    ),
    "book.occultism.dictionary_of_spirits.rituals.overview.steps.text": (
        "의식은 항상 같은 순서로 진행합니다.\n"
        "- 마법진을 그립니다.\n"
        "- 황금 희생의 그릇을 놓습니다.\n"
        "- 희생의 그릇을 놓습니다.\n"
        "- 그릇에 재료를 넣습니다.\n"
        "- 활성화 아이템을 들고 황금 그릇을 [#](ad03fc)우클릭[#]()합니다.\n"
        "- *선택 사항: 마법진 중앙 가까이에서 제물을 바칩니다.*\n"
    ),
    "book.occultism.dictionary_of_spirits.pentacles.pentacle_overview.name": (
        "마법진 안내"
    ),
    "tag.block.occultism.saplings.otherworld_natural": "자연 이계 묘목",
    "book.occultism.dictionary_of_spirits.crafting_rituals."
    "artisanal_ritual_satchel.usage_cleaning.text": (
        "1. 제거하려는 마법진을 찾으세요. 마법진은 의식을 시작할 수 있는 온전한 "
        "상태여야 합니다.\n"
        "2. 가방을 들고 중앙 [](item://occultism:golden_sacrificial_bowl)을 "
        "[#](55FF55)우클릭[#]()하세요.\n"
        "2. 가방이 모든 분필 자국을 지우고 마법진에 사용된 양초, 해골 등의 보조 "
        "블록을 회수합니다.\n"
    ),
}

EXACT_KEYS.update(QUEST_EXACT_KEYS)
EXACT_KEYS.update(RELATED_EXACT_KEYS)
EXACT_KEYS.update(LANGUAGE_EXACT_KEYS)

FTB_LITERAL_BREAK_KEYS = {
    "quest.0F412542271B6254.quest_desc",
    "quest.172D2A634E849562.quest_desc",
    "quest.1B5177A774FCEF64.quest_desc",
    "quest.6CCDEEDA2C99DA66.quest_desc",
    "quest.7F09F8F98C13F11B.quest_desc",
    "quest.201EE3566D4D3123.quest_desc",
    "quest.216DA9782EBDFF34.quest_desc",
    "quest.4ABACE222E647E2C.quest_desc",
    "quest.4E5238F00CEED8B2.quest_desc",
    "quest.67C76EDD4BCCFF3F.quest_desc",
}
for key in FTB_LITERAL_BREAK_KEYS:
    EXACT_KEYS[key] = [text.replace("\n", chr(92) + "n") for text in EXACT_KEYS[key]]

mark_all_key = "quest.4F35D04721DFC9FF.quest_desc"
EXACT_KEYS[mark_all_key][6] = EXACT_KEYS[mark_all_key][6].replace(
    '"모두 읽음으로 표시"',
    chr(92) + '"모두 읽음으로 표시' + chr(92) + '"',
)

REPLACEMENTS = (
    ("펜타클", "마법진"),
    ("이세계", "이계"),
    ("영혼이 조화된 보석", "정령 조율 보석"),
    ("영혼 조율 보석", "정령 조율 보석"),
    ("뼈대 두개골", "스켈레톤 해골"),
    ("해골 두개골", "스켈레톤 해골"),
    ("마우스 오른쪽 버튼 클릭", "우클릭"),
    ("제사 그릇", "희생의 그릇"),
    ("황금 의식 그릇", "황금 희생의 그릇"),
    ("희생 그릇", "희생의 그릇"),
    ("반죽는", "반죽은"),
    ("분필는", "분필은"),
    ("폴리엇라고", "폴리엇이라고"),
    ("폴리엇[#]()가", "폴리엇[#]()이"),
    ("해골[#]()가", "스켈레톤[#]()이"),
    ("소유합니다", "빙의합니다"),
    ("개체를\n소유하여", "생명체에\n빙의시켜"),
    ("야생 영혼", "야생 정령"),
    ("영혼을\n영구적으로 주입", "정령을\n영구적으로 주입"),
    ("낮은 영혼", "하급 정령"),
    ("고출력 정령", "강력한 정령"),
    ("호출 잠재력", "소환력"),
    ("투옥에 매우 다재다능하여", "빙의에 폭넓게 활용되어"),
    ("전력이 낮은 영혼", "힘이 약한 정령"),
    ("Evoker", "소환사"),
    ("Abras 소환", "Abras Conjure"),
    ("아브라스 소환", "Abras Conjure"),
    ("Fatma의 인센티브 매력", "Fatma's Incentivized Attraction"),
    ("드릭윙스", "드릭윙"),
    ("품목", "아이템"),
    ("리소스", "자원"),
    ("이에스늄 픽", "이에스늄 곡괭이"),
    ("이이에스늄", "이에스늄"),
    ("악마들s", "악마들"),
    ("아프리트s", "아프리트"),
    ("마리드s", "마리드"),
    ("정령는", "정령은"),
    ("Occultism는", "Occultism은"),
    ("정령불가", "정령불이"),
    ("정령불를", "정령불을"),
    ("악마을", "악마를"),
    ("Transporting 악마들", "운반 정령"),
    ("E빈", "빈"),
    ("Ronaza의 연락처", "Ronaza's Contact"),
    ("Ronaza의 Contact", "Ronaza's Contact"),
    ("Strigeor의 상위 결속", "Strigeor's Higher Binding"),
    ("Strigeor의 Higher Binding", "Strigeor's Higher Binding"),
    ("Eziveus의 Spectral Compulsion", "Eziveus' Spectral Compulsion"),
    ("에지베우스의 Spectral Compulsion", "Eziveus' Spectral Compulsion"),
    ("Uphyxes의 Inverted Tower", "Uphyxes' Inverted Tower"),
    ("Uphyxes의 역 타워", "Uphyxes' Inverted Tower"),
    ("Fatma의 Incentivized Attraction", "Fatma's Incentivized Attraction"),
    ("Ihagan의 Enthrallment", "Ihagan's Enthrallment"),
    ("Ihagan의 매혹", "Ihagan's Enthrallment"),
    ("Heidryn의 Lure", "Heidryn's Lure"),
    ("Sevira의 영구 감금", "Sevira's Permanent Confinement"),
    ("Osorin의 속박되지 않은 부름", "Osorin's Unbound Calling"),
    ("Osorin의 언바운드 호출", "Osorin's Unbound Calling"),
    ("Tibira의 어트랙션", "Tibira's Attraction"),
    ("Shub Niggurath", "슈브 니구라스"),
    ("Demon's Dream", "악마의 꿈"),
    ("Wild Strong Breeze", "강한 야생 브리즈"),
    ("Wild Weak Breeze", "약한 야생 브리즈"),
    ("Wild Breeze", "야생 브리즈"),
    ("Wild Spirits", "야생 정령"),
    ("Eldritch Spirits", "엘드리치 정령"),
    ("Eldritch Spirit", "엘드리치 정령"),
    ("Magic Storage", "마법 저장소"),
    ("Storage Stabilizer", "저장소 안정기"),
    ("Storage Actuator", "저장소 작동기"),
    ("Stable Wormhole", "안정된 웜홀"),
    ("Dimensional Matrix", "차원 행렬"),
    ("True Sight Staff", "진실의 시야 지팡이"),
    ("Infused Pickaxe", "주입된 곡괭이"),
    ("Vitality Compass", "생명력 나침반"),
    ("Spirit Grindstone", "정령 숫돌"),
    ("Spirit Fire", "정령불"),
    ("Soul Gem", "영혼 보석"),
    ("Third Eye", "제3의 눈"),
    ("Books of Calling", "부름의 책"),
    ("Summoned Spirits", "소환된 정령"),
    ("Possessed Mobs", "빙의된 몹"),
    ("Wondering Trader", "떠돌이 상인"),
    ("Storage Accessor", "저장소 접근기"),
    ("Bee Nest", "벌집"),
    ("Smithing Template", "대장장이 형판"),
    ("Otherworld Sapling", "이계 묘목"),
    ("Bane of Arthropods", "살충"),
    ("Reinforced Deepslate", "강화된 심층암"),
    ("Budding Amethyst", "싹트는 자수정"),
    ("Diamond Horse", "다이아몬드 말"),
    ("Deep Ore", "심층 광석"),
    ("Magic Lamp", "마법 램프"),
    ("Crafting Automation", "제작 자동화"),
    ("Demon Mining World", "악마 채굴 차원"),
    ("Transporting Demons", "운반 정령"),
    ("Item Pipes", "아이템 파이프"),
    ("Demon Miners", "악마 광부"),
    ("Spirit Attuned Crystals", "정령 조율 수정"),
    ("Unbound Afrit", "속박되지 않은 아프리트"),
    ("Unbound 마리드", "속박되지 않은 마리드"),
    ("Demon-less", "악마 없는"),
    ("Empty 영혼 보석", "빈 영혼 보석"),
    ("Dragon Soul", "드래곤 영혼"),
    ("Ore Hammer", "광석 망치"),
    ("Divination Rod", "점술 막대"),
    ("The Hermetica", "헤르메티카"),
    ("Loves Sticks", "막대기를 좋아함"),
    ("trinity gem", "삼위일체 보석"),
    ("Otherrock", "이계암"),
    ("Otherstone", "이계석"),
    ("Otherglass", "이계 유리"),
    ("Otherword", "이계"),
    ("Dragonyst", "드래고니스트"),
    ("Crystallizer", "결정화기"),
    ("Transporter", "운반자"),
    ("Lumberjack", "벌목꾼"),
    ("Crusher", "분쇄기"),
    ("Smelter", "제련공"),
    ("Stabilizer", "안정기"),
    ("Actuator", "작동기"),
    ("Wormhole", "웜홀"),
    ("Pickaxe", "곡괭이"),
    ("Guardian Familia", "가디언 사역마"),
    ("Beholder", "비홀더"),
    ("Cthulhu", "크툴루"),
    ("Drikwings", "드릭윙"),
    ("Drikwing", "드릭윙"),
    ("Guardian", "가디언"),
    ("Blacksmith", "대장장이"),
    ("Blaze", "블레이즈"),
    ("Warden", "워든"),
    ("Creeper", "크리퍼"),
    ("Drowned", "드라운드"),
    ("Possessed", "빙의된"),
    ("Shulker", "셜커"),
    ("Allay", "알레이"),
    ("Farmer", "농부"),
    ("Janitor", "관리인"),
    ("Trader", "상인"),
    ("Miner", "광부"),
    ("Anvil", "모루"),
    ("Satchel", "가방"),
    ("Chalk", "분필"),
    ("Bowl", "그릇"),
    ("Armor", "방어구"),
    ("Dust", "가루"),
    ("Paste", "반죽"),
    ("Golden", "황금"),
    ("Stabilized", "안정화된"),
    ("Dimensional", "차원"),
    ("Smithing", "대장장이"),
    ("Trim", "장식"),
    ("Horse", "말"),
    ("Base", "기반"),
    ("Deep", "심층"),
    ("Ore", "광석"),
    ("Groves", "숲"),
    ("Bell", "종"),
    ("Rainbow", "무지개"),
    ("Nature", "자연"),
    ("Entity", "개체"),
    ("Horde", "무리"),
    ("Golem", "골렘"),
    ("Iron", "철"),
    ("Elder", "엘더"),
    ("Grey", "회색"),
    ("Infuse", "주입"),
    ("Witherite", "위더라이트"),
    ("Void", "공허"),
    ("Eldritch Chalice", "엘드리치 성배"),
    ("Trinity Gem", "삼위일체 보석"),
    ("Gambler", "도박꾼"),
    ("Worldgen", "월드 생성"),
    ("DJinni", "지니"),
    ("Dijinni", "지니"),
    ("Dijini", "지니"),
    ("Hoppers", "호퍼"),
    ("Mineshaft", "광산 갱도"),
    ("Tallow", "수지"),
    ("Llamas", "라마"),
    ("Vexes", "벡스"),
    ("Hammer", "망치"),
    ("Brush", "솔"),
    ("Essence", "정수"),
    ("Possesion", "빙의"),
    ("Infusion", "주입"),
    ("Friends", "친구들"),
    ("Friend", "친구"),
    ("Lime", "연두색"),
    ("Netherrack", "네더랙"),
    ("Nether", "네더"),
    ("Unbreaking", "내구성"),
    ("Mending", "수선"),
    ("Smite", "강타"),
    ("Impaling", "찌르기"),
    ("Greedy", "탐욕스러운"),
    ("Dark", "어둠의"),
    ("Forge", "제작"),
    ("Drop from", "드롭 출처:"),
    ("Breeze", "브리즈"),
    ("Wild", "야생"),
    ("Spirits", "정령"),
    ("Spirit", "정령"),
    ("Occultism자", "Occultism 수행자"),
    ("오컬티스트", "Occultism 수행자"),
    ("신비술사", "Occultism 수행자"),
    ("바인딩의 책", "속박의 책"),
    ("바인딩북", "속박의 책"),
    ("바인딩된", "속박된"),
    ("바인딩", "속박"),
    ("소명서", "부름의 책"),
    ("소울 젬", "영혼 보석"),
    ("소울젬", "영혼 보석"),
    ("소유 의식", "빙의 의식"),
    ("소유된 소장", "빙의된 워든"),
    ("소유한 감시관", "빙의된 워든"),
    ("소유된", "빙의된"),
    ("소유하게", "빙의하게"),
    ("소유하도록", "빙의하도록"),
    ("소유하는", "빙의하는"),
    ("소유하고", "빙의하고"),
    ("소유할", "빙의할"),
    ("소유의 분필", "빙의의 분필"),
    ("펜타클 소유", "빙의 마법진"),
    ("영혼 소환 및 소유", "정령 소환 및 빙의"),
    ("아프리트가 소유한", "아프리트가 빙의한"),
    ("소환과 소유가", "소환과 빙의가"),
    ("소유물에 종사하는", "빙의를 행하는"),
    ("개체를 소유하여", "생명체에 빙의시켜"),
    ("폴리엇[#]()가 소유합니다", "폴리엇[#]()가 빙의합니다"),
    ("드리크윙을 소유", "드릭윙에 빙의"),
    ("앵무새를 소유", "앵무새에 빙의"),
    ("앵무새 소유", "앵무새 빙의"),
    ("약한 셜커 생성 알을 소유함", "빙의된 약한 셜커 생성 알"),
    ("드리크윙", "드릭윙"),
    ("폴리트(Folit)", "폴리엇"),
    ("폴리엇가", "폴리엇이"),
    ("폴리엇를", "폴리엇을"),
    ("드릭윙는", "드릭윙은"),
    ("저세계", "이계"),
    ("아프리카", "아프리트"),
    ("정신과 함께 제작된 책을 할당합니다.", "정령에게 제작한 책을 지정하세요."),
    ("정신", "정령"),
    ("사역마s", "사역마"),
    ("지니s", "지니"),
    ("폴리엇s", "폴리엇"),
    ("알레이s", "알레이"),
    ("악마 광부s", "악마 광부"),
    ("분필를", "분필을"),
    ("반죽를", "반죽을"),
    ("타석", "이계석"),
    ("초크", "분필"),
    ("페이스트", "반죽"),
    ("영령사전", "영혼 사전"),
    ("사역마 사람들", "사역마"),
    ("비밀주의", "Occultism"),
    ("안정적인 웜홀", "안정된 웜홀"),
    ("정령 Attuned Crystals", "정령 조율 수정"),
    ("익숙한 사람", "사역마"),
    ("정령fire", "정령불"),
    ("Demon 가루", "악마 가루"),
    ("Demons", "악마들"),
    ("Demonic", "악마의"),
    ("Demon", "악마"),
    ("afrit", "아프리트"),
    ("otherstone", "이계석"),
    ("Folit", "폴리엇"),
    ("Endstone", "엔드 돌"),
    ("Theurgy Logistics", "Theurgy 물류"),
    ("iesnium", "이에스늄"),
    ("otherrock", "이계암"),
    ("djinni", "지니"),
    ("오컬티즘", "Occultism"),
    ("신비주의", "Occultism"),
    ("영혼의 사전", "영혼 사전"),
    ("정령의 사전", "영혼 사전"),
    ("영혼 사전", "영혼 사전"),
    ("다른 세계", "이계"),
    ("저세상", "이계"),
    ("이에스니움", "이에스늄"),
    ("이에스니엄", "이에스늄"),
    ("폴리오트", "폴리엇"),
    ("진니", "지니"),
    ("아프리트", "아프리트"),
    ("마리드", "마리드"),
    ("친숙한", "사역마"),
    ("패밀리어", "사역마"),
    ("Familiar", "사역마"),
    ("Familiars", "사역마"),
    ("Dictionary of Spirits", "영혼 사전"),
    ("Spirit Dictionary", "영혼 사전"),
    ("Otherworld", "이계"),
    ("Iesnium", "이에스늄"),
    ("Foliot", "폴리엇"),
    ("Djinni", "지니"),
    ("Afrit", "아프리트"),
    ("Marid", "마리드"),
    ("Pentacles", "마법진"),
    ("Pentacle", "마법진"),
    ("Rituals", "의식"),
    ("Ritual", "의식"),
    ("Possession", "빙의"),
    ("Summoning", "소환"),
    ("Dimensional Storage", "차원 저장소"),
    ("Dimensional Mineshaft", "차원 광산 갱도"),
    ("Spirit Attuned Gem", "정령 조율 보석"),
    ("Book of Binding", "속박의 책"),
    ("Book of Calling", "부름의 책"),
    ("Sacrificial Bowl", "희생의 그릇"),
    ("Right-Click", "우클릭"),
    ("right-click", "우클릭"),
    ("Shift+우클릭", "Shift+우클릭"),
    ("Crouch", "웅크리기"),
    ("Warning", "경고"),
    ("Success", "성공"),
    ("아이템 항목", "아이템"),
    ("항목", "아이템"),
    ("\n]", "\n"),
)


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for attempt in range(10):
        try:
            os.replace(temporary, path)
            break
        except PermissionError:
            if attempt == 9:
                raise
            time.sleep(0.1 * (attempt + 1))


def string_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value for text in string_values(item)]
    return []


def normalize_text(value: str) -> str:
    value = EXACT_SOURCE.get(value, value)
    value = value.replace("\u200b", "").replace("\ufeff", "")
    link_targets = []

    def protect_target(match: re.Match[str]) -> str:
        link_targets.append(match.group(0))
        return f"\ue000{len(link_targets) - 1}\ue001"

    value = LINK_TARGET.sub(protect_target, value)
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    value = re.sub(r"(?<!이)에스늄", "이에스늄", value)
    value = re.sub(r"\bCraft\b", "제작", value)
    value = re.sub(r"\bTier\s+(\d+)", r"\1등급", value)
    value = value.replace("Tier", "등급")
    value = re.sub(r"Demon's[ \t]+Dream", "악마의 꿈", value)
    value = re.sub(r"(?<![가-힣])소유(?![가-힣])", "빙의", value)
    escaped_newline = "\ue100"
    value = value.replace("\\n", escaped_newline)
    lines = value.split("\n")
    for line_index, line in enumerate(lines):
        if "\\" in line and not line.endswith("\\"):
            backslashes = line.count("\\")
            lines[line_index] = line.replace("\\", "").rstrip() + "\\" * backslashes
    value = "\n".join(lines).replace(escaped_newline, "\\n")
    for index, target in enumerate(link_targets):
        value = value.replace(f"\ue000{index}\ue001", target)
    value = (
        value.replace("분필를", "분필을")
        .replace("반죽를", "반죽을")
        .replace("분필는", "분필은")
        .replace("반죽는", "반죽은")
    )
    return value


def translate_text(
    value: str, cache: dict[str, str], whole_cache: dict[str, str] | None = None
) -> str:
    if whole_cache is not None and whole_cache.get(value, value) != value:
        candidate = whole_cache[value]
        if structurally_usable(value, candidate):
            return normalize_text(candidate)
    output = []
    for segment in value.splitlines(keepends=True):
        body = segment.removesuffix("\n")
        ending = "\n" if segment.endswith("\n") else ""
        output.append(EXACT_SOURCE.get(body, cache.get(body, body)) + ending)
    return normalize_text("".join(output))


def map_value(
    value: object,
    cache: dict[str, str],
    whole_cache: dict[str, str] | None = None,
) -> object:
    if isinstance(value, str):
        return translate_text(value, cache, whole_cache)
    if isinstance(value, list):
        return [map_value(item, cache, whole_cache) for item in value]
    return value


def whole_candidate(source: str, label_cache: dict[str, str]) -> str:
    """임의 줄바꿈을 합쳐 번역한 뒤 링크를 끊지 않도록 다시 나눈다."""
    ends_with_newline = source.endswith("\n")
    body = source[:-1] if ends_with_newline else source
    source_lines = body.split("\n")
    output = []
    index = 0
    while index < len(source_lines):
        if source_lines[index].strip() in {"", "\\"}:
            output.append(source_lines[index])
            index += 1
            continue
        group = []
        while index < len(source_lines) and source_lines[index].strip() not in {
            "",
            "\\",
        }:
            group.append(source_lines[index].strip())
            index += 1
        joined = " ".join(group)
        protected = []

        def protect_escaped_newline(match: re.Match[str]) -> str:
            protected.append(match.group(0))
            return f"%{8000 + len(protected)}$s"

        masked = re.sub(r"\\n", protect_escaped_newline, joined)

        def protect_formatted(match: re.Match[str]) -> str:
            label = label_cache.get(match.group(2), match.group(2))
            protected.append(f"[#]({match.group(1)}){label}[#]()")
            return f"%{8000 + len(protected)}$s"

        masked = FORMATTED_SPAN.sub(protect_formatted, masked)

        def protect_link(match: re.Match[str]) -> str:
            separator = match.group(0).index("](")
            label = match.group(0)[1:separator]
            target = match.group(0)[separator + 2 : -1]
            protected.append(f"[{label_cache.get(label, label)}]({target})")
            return f"%{8000 + len(protected)}$s"

        masked = MARKDOWN_LINK.sub(protect_link, masked)
        translated = helper.request_candidate(masked)

        def restore(text: str) -> str:
            for protected_index, protected_value in enumerate(protected, 1):
                text = text.replace(f"%{8000 + protected_index}$s", protected_value)
            return text

        if not structurally_usable(joined, restore(translated), check_newlines=False):
            raise ValueError(f"문단 구조 불일치: {joined[:120]}")
        tokens = re.findall(r"\[[^\]]*\]\([^)]*\)|\S+", translated)
        if len(group) == 1:
            output.append(restore(" ".join(tokens)))
            continue
        weights = [max(len(line), 1) for line in group]
        total_weight = sum(weights)
        total_length = sum(len(token) + 1 for token in tokens)
        token_index = 0
        consumed = 0
        for line_index, weight in enumerate(weights):
            remaining_lines = len(weights) - line_index - 1
            if remaining_lines == 0:
                output.append(restore(" ".join(tokens[token_index:])))
                break
            target = total_length * (consumed + weight) / total_weight
            end = token_index
            current_length = sum(len(token) + 1 for token in tokens[:token_index])
            while end < len(tokens) - remaining_lines and current_length < target:
                current_length += len(tokens[end]) + 1
                end += 1
            output.append(restore(" ".join(tokens[token_index:end])))
            token_index = end
            consumed += weight
    result = "\n".join(output)
    return result + ("\n" if ends_with_newline else "")


def structurally_usable(
    source: str, target: str, *, check_newlines: bool = True
) -> bool:
    """자동 후보가 원문의 게임 표시 토큰을 훼손하지 않았는지 확인한다."""
    for pattern in (PLACEHOLDER, FORMAT_CODE, LINK_TARGET):
        if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
            return False
    if len(MARKDOWN_LINK.findall(source)) != len(MARKDOWN_LINK.findall(target)):
        return False
    if check_newlines and source.count("\n") != target.count("\n"):
        return False
    if source.count("\\") != target.count("\\"):
        return False
    source_without_links = FORMAT_CODE.sub("", LINK_TARGET.sub("]()", source))
    target_without_links = FORMAT_CODE.sub("", LINK_TARGET.sub("]()", target))
    source_numbers = Counter(NUMBER.findall(source_without_links))
    target_numbers = Counter(NUMBER.findall(target_without_links))
    return not (source_numbers - target_numbers)


def candidates() -> dict[str, object]:
    if not BUNDLED_PATH.is_file():
        write_json(BUNDLED_PATH, load_json(LANG_ROOT / "ko_kr.json"))
    cache = load_json(CACHE_PATH) if CACHE_PATH.is_file() else {}
    whole_cache = load_json(WHOLE_CACHE_PATH) if WHOLE_CACHE_PATH.is_file() else {}
    label_cache = load_json(LABEL_CACHE_PATH) if LABEL_CACHE_PATH.is_file() else {}
    roots = (LANG_ROOT, *QUEST_ROOTS)
    sources = {
        text
        for root in roots
        for value in load_json(root / "en_us.json").values()
        for text in string_values(value)
        if text and LATIN_WORD.search(text)
    }
    segments = {
        segment.removesuffix("\n")
        for source in sources
        for segment in source.splitlines(keepends=True)
        if segment.removesuffix("\n") and LATIN_WORD.search(segment)
    }
    requests = sorted(segments - cache.keys())
    failures = []
    if requests:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(helper.request_candidate, source): source
                for source in requests
            }
            for number, future in enumerate(as_completed(futures), 1):
                source = futures[future]
                try:
                    cache[source] = future.result()
                except Exception as exc:  # pragma: no cover - 외부 서비스 오류 보고용
                    cache[source] = source
                    failures.append(f"{source}: {exc}")
                if number % 25 == 0:
                    write_json(CACHE_PATH, cache)
        write_json(CACHE_PATH, cache)
    labels = set()
    for source in sources:
        labels.update(match.group(2) for match in FORMATTED_SPAN.finditer(source))
        without_formatted = FORMATTED_SPAN.sub("", source)
        labels.update(
            match.group(0)[1 : match.group(0).index("](")]
            for match in MARKDOWN_LINK.finditer(without_formatted)
        )
    label_requests = sorted(
        label
        for label in labels - label_cache.keys()
        if label and LATIN_WORD.search(label)
    )
    label_failures = []
    if label_requests:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(helper.request_candidate, label): label
                for label in label_requests
            }
            for number, future in enumerate(as_completed(futures), 1):
                label = futures[future]
                try:
                    label_cache[label] = future.result()
                except Exception as exc:  # pragma: no cover - 외부 서비스 오류 보고용
                    label_cache[label] = label
                    label_failures.append(f"{label}: {exc}")
                if number % 25 == 0:
                    write_json(LABEL_CACHE_PATH, label_cache)
        write_json(LABEL_CACHE_PATH, label_cache)
    whole_requests = sorted(
        source
        for source in sources - whole_cache.keys()
        if ("\n" in source or "\\n" in source or len(source) >= 160)
        and len(source) <= 1200
    )
    whole_failures = []
    if whole_requests:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(whole_candidate, source, label_cache): source
                for source in whole_requests
            }
            for number, future in enumerate(as_completed(futures), 1):
                source = futures[future]
                try:
                    translated = future.result()
                    whole_cache[source] = (
                        translated
                        if structurally_usable(source, translated)
                        else source
                    )
                    if whole_cache[source] == source:
                        whole_failures.append(f"구조 불일치: {source[:120]}")
                except Exception as exc:  # pragma: no cover - 외부 서비스 오류 보고용
                    whole_cache[source] = source
                    whole_failures.append(f"{source[:120]}: {exc}")
                if number % 25 == 0:
                    write_json(WHOLE_CACHE_PATH, whole_cache)
        write_json(WHOLE_CACHE_PATH, whole_cache)
    bundled = load_json(BUNDLED_PATH)
    provenance = load_json(LANG_ROOT / "candidate_sources.json")
    english = load_json(LANG_ROOT / "en_us.json")
    language = {}
    for key, source in english.items():
        if provenance[key] == "bundled_ko_kr" and bundled[key] != source:
            language[key] = normalize_text(str(bundled[key]))
        else:
            language[key] = map_value(source, cache, whole_cache)
    write_json(LANG_ROOT / "auto_candidates_direct.json", language)
    for root in QUEST_ROOTS:
        source = load_json(root / "en_us.json")
        write_json(
            root / "auto_candidates_direct.json",
            {
                key: map_value(value, cache, whole_cache)
                for key, value in source.items()
            },
        )
    report = {
        "unique_strings": len(sources),
        "candidate_requests": len(requests),
        "candidate_failures": failures,
        "whole_candidate_requests": len(whole_requests),
        "whole_candidate_failures": whole_failures,
        "link_label_requests": len(label_requests),
        "link_label_failures": label_failures,
        "bundled_candidates_reviewed": sum(
            value == "bundled_ko_kr" for value in provenance.values()
        ),
        "status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "direct_candidate_report.json", report)
    return report


def normalize() -> dict[str, object]:
    roots = (LANG_ROOT, *QUEST_ROOTS)
    counts = {}
    for root in roots:
        english = load_json(root / "en_us.json")
        auto = load_json(root / "auto_candidates_direct.json")
        reviewed = {
            key: EXACT_KEYS.get(key, map_value(auto[key], {})) for key in english
        }
        if root == LANG_ROOT:
            reviewed.update(EXTRA_KEYS)
        write_json(root / "ko_kr.json", reviewed)
        counts[root.relative_to(WORK_ROOT).as_posix()] = len(reviewed)
    report = {"reviewed_keys": counts, "status": "complete"}
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def pairs(source: object, target: object, path: str) -> list[tuple[str, str, str]]:
    if isinstance(source, str) and isinstance(target, str):
        return [(path, source, target)]
    if (
        isinstance(source, list)
        and isinstance(target, list)
        and len(source) == len(target)
    ):
        return [
            row
            for index, (left, right) in enumerate(zip(source, target, strict=True))
            for row in pairs(left, right, f"{path}[{index}]")
        ]
    return []


def verify_root(root: Path) -> tuple[dict[str, object], list[str]]:
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    errors = []
    untranslated = []
    expected_keys = list(english)
    if root == LANG_ROOT:
        expected_keys.extend(EXTRA_KEYS)
    if expected_keys != list(korean):
        errors.append("키 또는 키 순서가 영어 원문과 다릅니다")
    for key in english.keys() & korean.keys():
        for path, source, target in pairs(english[key], korean[key], key):
            for label, pattern in (
                ("자리표시자", PLACEHOLDER),
                ("서식 코드", FORMAT_CODE),
            ):
                if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
                    errors.append(f"{label} 불일치: {path}")
            source_without_links = FORMAT_CODE.sub("", LINK_TARGET.sub("]()", source))
            target_without_links = FORMAT_CODE.sub("", LINK_TARGET.sub("]()", target))
            source_numbers = Counter(
                value.replace(",", "") for value in NUMBER.findall(source_without_links)
            )
            target_numbers = Counter(
                value.replace(",", "") for value in NUMBER.findall(target_without_links)
            )
            if source_numbers - target_numbers:
                errors.append(f"숫자 불일치: {path}")
            if source.count("\n") != target.count("\n"):
                errors.append(f"줄바꿈 불일치: {path}")
            if source.count("\\") != target.count("\\"):
                errors.append(f"강제 줄바꿈 기호 불일치: {path}")
            if Counter(LINK_TARGET.findall(source)) != Counter(
                LINK_TARGET.findall(target)
            ):
                errors.append(f"링크 대상 불일치: {path}")
            if len(MARKDOWN_LINK.findall(source)) != len(MARKDOWN_LINK.findall(target)):
                errors.append(f"링크 구문 불일치: {path}")
            if (
                source == target
                and LATIN_WORD.search(source)
                and source not in ALLOWED_ORIGINALS | {"Occultism"}
            ):
                untranslated.append(path)
            blocked = [token for token in SURFACE_BLOCKED if token in target]
            if blocked:
                errors.append(f"표시 품질 금지 문자열 {blocked}: {path}")
    if untranslated:
        errors.append(f"미번역 후보: {untranslated[:30]}")
    report = {
        "keys": len(english),
        "untranslated_candidates": untranslated,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    reports = []
    errors = []
    for root in (LANG_ROOT, *QUEST_ROOTS):
        report, current = verify_root(root)
        report["scope"] = root.relative_to(WORK_ROOT).as_posix()
        reports.append(report)
        errors.extend(current)
    result = {
        "scopes": reports,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", result)
    return result, errors


def audit() -> tuple[dict[str, object], list[str]]:
    jar = next((resolve_source_root() / "mods").glob("occultism-*.jar"))
    references = []
    literals = []
    advancement_display = 0
    with ZipFile(jar) as archive:
        names = archive.namelist()
        display_files = [
            name
            for name in names
            if (
                "/modonomicon/books/" in name
                or "/advancement/occultism/" in name
                or "/advancement/chalks/" in name
            )
            and name.endswith(".json")
        ]
        for name in display_files:
            value = json.loads(archive.read(name))
            if (
                "/advancement/" in name
                and isinstance(value, dict)
                and "display" in value
            ):
                advancement_display += 1

            def walk(item: object, path: str = "") -> None:
                if isinstance(item, dict):
                    for key, child in item.items():
                        current = f"{path}/{key}"
                        if key in {
                            "name",
                            "description",
                            "title",
                            "text",
                        } and isinstance(child, str):
                            if re.fullmatch(r"[a-z0-9_.-]+", child):
                                references.append((name, current, child))
                            elif child:
                                literals.append((name, current, child))
                        walk(child, current)
                elif isinstance(item, list):
                    for index, child in enumerate(item):
                        walk(child, f"{path}/{index}")

            walk(value)
    language = load_json(LANG_ROOT / "en_us.json")
    missing = sorted(
        {row[2] for row in references} - (language.keys() | EXTRA_KEYS.keys())
    )
    errors = []
    if missing:
        errors.append(f"표시 참조 키 누락: {missing[:20]}")
    if literals:
        errors.append(f"직접 영문 표시값: {literals[:10]}")
    report = {
        "jar": jar.name,
        "display_files": len(display_files),
        "advancement_display_files": advancement_display,
        "translated_display_references": len(references),
        "literal_display_values": len(literals),
        "missing_language_references": missing,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("candidates", "normalize", "verify", "audit")
    )
    args = parser.parse_args()
    if args.command == "candidates":
        report, errors = candidates(), []
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
