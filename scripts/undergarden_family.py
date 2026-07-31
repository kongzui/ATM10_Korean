#!/usr/bin/env python3
"""The Undergarden 본체와 직접 연동 표시 경로를 수동 재검수한다."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import five_family_goal as family_goal
import twilight_family
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/undergarden"
LANG_ROOT = WORK_ROOT / "undergarden"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"

TERM_REPLACEMENTS = (
    ("지하 정원", "The Undergarden"),
    ("지하정원", "The Undergarden"),
    ("언더가든", "The Undergarden"),
    ("크로그룸", "클로그룸"),
    ("크로그럼", "클로그룸"),
    ("클로그럼", "클로그룸"),
    ("프로스트강철", "서리철"),
    ("서리강철", "서리철"),
    ("유테리움", "우테리움"),
    ("유서릭", "우테릭"),
    ("리가리움", "레갈륨"),
    ("레갈리움", "레갈륨"),
    ("잊혀진", "잊힌"),
    ("가디언", "수호자"),
    ("포탈", "차원문"),
    ("물집딸기", "발포 베리"),
    ("돌맹이", "조약돌"),
    ("잊힌 미니언", "잊힌 하수인"),
    ("스폰 알", "생성 알"),
    ("취성", "취약"),
)

ADVANCEMENT_OVERRIDES = {
    "advancement.undergarden.all_ore_blocks.desc": (
        "The Undergarden의 모든 광석 블록을 하나씩 모으세요."
    ),
    "advancement.undergarden.all_ore_blocks.title": "수집가 한정판",
    "advancement.undergarden.all_undergarden_biomes.desc": (
        "The Undergarden의 모든 생물 군계를 발견하세요."
    ),
    "advancement.undergarden.all_undergarden_biomes.title": "지하 지도 제작자",
    "advancement.undergarden.break_denizen_campfire.desc": (
        "거주민의 모닥불을 부숴 주변의 모든 거주민을 화나게 하세요."
    ),
    "advancement.undergarden.break_denizen_campfire.title": "흥을 깨는 사람",
    "advancement.undergarden.catacombs.desc": "지하 묘지에 들어가세요.",
    "advancement.undergarden.catacombs.title": "잊힌 회랑",
    "advancement.undergarden.catalyst.desc": "카탈리스트를 제작하세요.",
    "advancement.undergarden.catalyst.title": "표 한 장 주세요",
    "advancement.undergarden.catch_gwibling.desc": (
        "작은 정원메기를 양동이로 잡으세요."
    ),
    "advancement.undergarden.catch_gwibling.title": "이상한 물고기",
    "advancement.undergarden.cloggrum_armor.desc": (
        "클로그룸 갑옷 한 벌을 모두 갖추세요."
    ),
    "advancement.undergarden.cloggrum_armor.title": "분석으로 나를 감싸 줘",
    "advancement.undergarden.cloggrum_battleaxe.desc": (
        "클로그룸 전투도끼를 든 잊힌 자에게서 그 도끼를 얻으세요."
    ),
    "advancement.undergarden.cloggrum_battleaxe.title": "차갑게 식은 손",
    "advancement.undergarden.contract_utheric_infection.desc": (
        "우테릭 감염에 걸리세요. 감염이 걷잡을 수 없이 번지지 않게 조심하세요!"
    ),
    "advancement.undergarden.contract_utheric_infection.title": "대지를 덮친 역병",
    "advancement.undergarden.craft_infuser.desc": "주입기를 제작하세요.",
    "advancement.undergarden.craft_infuser.title": "주입 사랑해 <3",
    "advancement.undergarden.cure_utheric_infection.desc": (
        "우테릭 감염을 억제할 방법을 찾으세요."
    ),
    "advancement.undergarden.cure_utheric_infection.title": "간절했던 해독제",
    "advancement.undergarden.enter_denizen_camp.desc": "거주민 야영지를 찾으세요.",
    "advancement.undergarden.enter_denizen_camp.title": "현지인과의 만남",
    "advancement.undergarden.enter_depths.desc": (
        "The Undergarden 밑바닥의 공포석 장벽을 뚫고 심층부로 들어가세요..."
    ),
    "advancement.undergarden.enter_depths.title": "심층부로",
    "advancement.undergarden.enter_undergarden.desc": "잊힌 땅이 기다립니다...",
    "advancement.undergarden.enter_undergarden.title": "The Undergarden 입장",
    "advancement.undergarden.forgotten_battleaxe.desc": (
        "클로그룸 전투도끼를 잊힌 주괴로 업그레이드하세요."
    ),
    "advancement.undergarden.forgotten_battleaxe.title": "전설의 도끼",
    "advancement.undergarden.forgotten_ingot.desc": (
        "잊힌 수호자의 조각으로 잊힌 주괴를 제련하세요."
    ),
    "advancement.undergarden.forgotten_ingot.title": "지금 남은 것",
    "advancement.undergarden.forgotten_tools.desc": (
        "잊힌 주괴로 클로그룸 도구를 업그레이드해 잊힌 도구 6종을 모두 만드세요."
    ),
    "advancement.undergarden.forgotten_tools.title": "잊힌 무기고",
    "advancement.undergarden.gloomper_secret_disc.desc": "비밀 음반을 얻으세요.",
    "advancement.undergarden.gloomper_secret_disc.title": "우울한 죽음",
    "advancement.undergarden.kill_all_rotspawn.desc": "모든 종류의 부패종을 처치하세요.",
    "advancement.undergarden.kill_all_rotspawn.title": "부패종의 천적",
    "advancement.undergarden.kill_forgotten_guardian.desc": "잊힌 수호자를 처치하세요.",
    "advancement.undergarden.kill_forgotten_guardian.title": "퇴역 처리",
    "advancement.undergarden.kill_rotling.desc": (
        "가장 약한 부패종인 부패귀를 처치하세요."
    ),
    "advancement.undergarden.kill_rotling.title": "개체 수 조절",
    "advancement.undergarden.kill_scintling.desc": (
        "죄 없는 정원 민달팽이를 죽였습니다. 이 괴물..."
    ),
    "advancement.undergarden.kill_scintling.title": "끔찍한 사람",
    "advancement.undergarden.mine_ore.desc": "The Undergarden 광석을 하나 얻으세요.",
    "advancement.undergarden.mine_ore.title": "심층 채굴",
    "advancement.undergarden.obtain_denizen_mask.desc": (
        "거주민에게서 신비한 가면을 얻으세요."
    ),
    "advancement.undergarden.obtain_denizen_mask.title": "우리 중 하나",
    "advancement.undergarden.plant_gloomgourd.desc": "우울호박 씨앗을 심으세요.",
    "advancement.undergarden.plant_gloomgourd.title": "보라색 호박",
    "advancement.undergarden.root.title": "The Undergarden",
    "advancement.undergarden.shard_torch.desc": (
        "주변 부패종에게 피해를 주는 파편 횃불을 제작하세요."
    ),
    "advancement.undergarden.shard_torch.title": "방호 장치",
    "advancement.undergarden.shoot_slingshot.desc": "무언가에 조약돌을 쏘세요.",
    "advancement.undergarden.shoot_slingshot.title": "돌팔매질",
    "advancement.undergarden.shoot_slingshot_goo.desc": (
        "무언가를 성가시게 하도록 정원 민달팽이 점액 공을 쏘세요."
    ),
    "advancement.undergarden.shoot_slingshot_goo.title": "날아드는 골칫거리",
    "advancement.undergarden.shoot_slingshot_gronglet.desc": (
        "그롱이를 쏘세요! 이래도 괜찮은 걸까요..?"
    ),
    "advancement.undergarden.shoot_slingshot_gronglet.title": "윤리적으로 의심스러움",
    "advancement.undergarden.shoot_slingshot_rotten_blisterberry.desc": (
        "무언가에 썩은 발포 베리를 쏘고, 팔다리가 멀쩡하기를 바라세요."
    ),
    "advancement.undergarden.shoot_slingshot_rotten_blisterberry.title": (
        "안전하지 않아"
    ),
    "advancement.undergarden.slingshot.desc": "새총을 제작하세요.",
    "advancement.undergarden.slingshot.title": "새로운 단짝",
    "advancement.undergarden.slingshot_20_damage.desc": (
        "조약돌 하나로 무언가에 20 이상의 피해를 주세요...!?"
    ),
    "advancement.undergarden.slingshot_20_damage.title": "저격은 좋은 일이야",
    "advancement.undergarden.stack_of_gloomgourds.desc": (
        "우울호박 한 스택을 모으세요."
    ),
    "advancement.undergarden.stack_of_gloomgourds.title": "호박 군주",
    "advancement.undergarden.stoneborn_trade.desc": "돌인간과 거래하세요.",
    "advancement.undergarden.stoneborn_trade.title": "차원 간 거래",
    "advancement.undergarden.summon_minion.desc": (
        "잊힌 금속 블록과 조각된 우울호박으로 잊힌 하수인을 만드세요."
    ),
    "advancement.undergarden.summon_minion.title": "보초 만들기",
    "advancement.undergarden.underbeans.desc": "지하콩 덤불을 찾아 수확하세요.",
    "advancement.undergarden.underbeans.title": "영광스러운 콩!",
}

QUALITY_OVERRIDES = {
    **ADVANCEMENT_OVERRIDES,
    "itemGroup.undergarden_group": "The Undergarden",
    "config.undergarden.return_portal_frame_block_id": "귀환 차원문 틀 블록 ID",
    "effect.undergarden.brittleness": "취약",
    "effect.undergarden.brittleness.description": (
        "대상의 방어력이 높을수록 받는 피해가 증가합니다. 증가량은 효과 단계에 따라 커집니다."
    ),
    "effect.undergarden.featherweight.description": (
        "피해를 받으면 더 멀리 밀려납니다. 밀려나는 거리는 효과 단계에 따라 증가합니다."
    ),
    "effect.undergarden.gooey.description": (
        "대상의 발밑에 정원 민달팽이 점액이 계속 생깁니다."
    ),
    "enchantment.undergarden.self_sling.desc": (
        "탄약 대신 자신을 발사합니다. 땅에 서 있을 때만 사용할 수 있습니다."
    ),
    "block.undergarden.blood_mushroom_cap": "핏빛 버섯 갓",
    "block.undergarden.amorous_bristle": "연정의 강모",
    "block.undergarden.engorged_blood_mushroom_cap": "부풀어 오른 핏빛 버섯 갓",
    "block.undergarden.indigo_mushroom_cap": "쪽빛 버섯 갓",
    "block.undergarden.ink_mushroom_cap": "먹물 버섯 갓",
    "block.undergarden.veil_mushroom_cap": "장막 버섯 갓",
    "block.undergarden.polished_depthrock": "윤이 나는 깊은돌",
    "block.undergarden.polished_depthrock_slab": "윤이 나는 깊은돌 반 블록",
    "block.undergarden.polished_depthrock_stairs": "윤이 나는 깊은돌 계단",
    "block.undergarden.polished_depthrock_wall": "윤이 나는 깊은돌 담장",
    "block.undergarden.depthrock_pebbles": "깊은돌 조약돌 더미",
    "block.undergarden.gloom_o_lantern": "우울호박 랜턴",
    "block.undergarden.shard_o_lantern": "파편 랜턴",
    "block.undergarden.undergarden_portal": "The Undergarden 차원문",
    "block.undergarden.wigglewood_wood": "흔들나무 목재",
    "item.undergarden.depthrock_pebble": "깊은돌 조약돌",
    "item.undergarden.blood_globule": "핏방울",
    "item.undergarden.cooked_gwibling": "구운 작은 정원메기",
    "item.undergarden.grongle_chest_boat": "상자가 실린 그롱글 보트",
    "item.undergarden.smogstem_chest_boat": "상자가 실린 안개줄기 보트",
    "item.undergarden.wigglewood_chest_boat": "상자가 실린 흔들나무 보트",
    "item.undergarden.goo_ball": "정원 민달팽이 점액 공",
    "item.undergarden.raw_dweller_meat": "생 토착종 고기",
    "item.undergarden.raw_gloomper_leg": "생 우울두꺼비 다리",
    "item.undergarden.raw_gwibling": "생 작은 정원메기",
    "item.undergarden.underbean_on_a_stick": "막대기에 꽂은 지하콩",
    "entity.undergarden.minion": "잊힌 하수인",
    "death.attack.blisterberry_bush": "%1$s이(가) 발포 베리 덤불에 찔렸습니다",
    "death.attack.blisterberry_bush.player": (
        "%1$s이(가) %2$s에게서 도망치려다 발포 베리 덤불에 찔렸습니다"
    ),
    "death.attack.shard_torch": "%1$s이(가) 파편 횃불의 마법에 쓰러졌습니다",
    "death.attack.shard_torch.player": (
        "%1$s이(가) %2$s에게서 도망치려다 파편 횃불의 마법에 쓰러졌습니다"
    ),
    "subtitles.entity.forgotten_guardian.deflect": "잊힌 수호자가 공격을 튕겨 냄",
    "subtitles.item.blisterbomb": "발포 폭탄을 던짐",
}

NEW_TRANSLATIONS = {
    "biome.undergarden.depths": "심층부",
    "biome.undergarden.frosty_smogstem_forest": "서리 낀 안개줄기 숲",
    "biome.undergarden.infected_depths": "감염된 심층부",
    "biome.undergarden.puff_mushroom_forest": "부푼 버섯 숲",
    "commands.undergarden.infection.cannot_infect": "%s은(는) 감염에 면역입니다",
    "commands.undergarden.infection.cannot_infect_multiple": (
        "모든 대상이 감염에 면역입니다"
    ),
    "commands.undergarden.infection.skipped": (
        "%s개의 대상은 감염에 면역이어서 영향을 받지 않았습니다"
    ),
    "commands.undergarden.infection.success.multiple": (
        "감염 수치를 %s(으)로 설정한 대상: %s개"
    ),
    "commands.undergarden.infection.success.single": (
        "감염 수치를 %s(으)로 설정했습니다: %s"
    ),
    "config.undergarden.toggle_undergarden_fog": "The Undergarden 안개 표시 전환",
    "config.undergarden.toggle_utheric_infection_number_display": (
        "우테릭 감염 수치 표시 전환"
    ),
    "config.undergarden.toggle_utheric_infection_overlay": "우테릭 감염 오버레이 전환",
    "container.undergarden.infuser": "주입기",
    "death.attack.utheric_infection": "%1$s이(가) 우테릭 감염을 이기지 못했습니다",
    "death.attack.utheric_infection.player": (
        "%1$s이(가) %2$s에게서 도망치려다 우테릭 감염을 이기지 못했습니다"
    ),
    "effect.undergarden.chilly": "냉기",
    "effect.undergarden.chilly.description": "대상을 느려지게 하고 몸을 떨게 합니다.",
    "effect.undergarden.purity": "정화",
    "effect.undergarden.purity.description": (
        "대상의 우테릭 감염 수치를 매초 낮춥니다. 감소량은 효과 단계에 따라 증가합니다."
    ),
    "emi.category.undergarden.infusing": "주입",
    "gui.undergarden.jei.category.infuser": "주입",
    "gui.undergarden.jei.category.infusing.experience": "%s 경험치",
    "gui.undergarden.jei.category.infusing.time.seconds": "%s초",
    "tooltip.undergarden.cloggrum_boots": (
        "착용하면 정원 민달팽이 점액 위에서도 느려지지 않습니다."
    ),
    "tooltip.undergarden.forgotten_tool": (
        "The Undergarden 블록을 1.5배 빠르게 캡니다."
    ),
    "tooltip.undergarden.forgotten_weapon": (
        "보스가 아닌 The Undergarden 몹에게 1.5배의 피해를 줍니다."
    ),
    "tooltip.undergarden.froststeel_weapon": "대상을 느려지게 합니다.",
    "tooltip.undergarden.rogdorium_infusion": "로그도리움 주입",
    "tooltip.undergarden.slingshot_ammo": "새총 탄약으로 사용할 수 있습니다.",
    "tooltip.undergarden.utherium_weapon": "부패종에게 1.5배의 피해를 줍니다.",
    "trim_material.undergarden.cloggrum": "클로그룸 소재",
    "trim_material.undergarden.forgotten": "잊힌 금속 소재",
    "trim_material.undergarden.froststeel": "서리철 소재",
    "trim_material.undergarden.regalium": "레갈륨 소재",
    "trim_material.undergarden.utherium": "우테리움 소재",
    "upgrade.undergarden.forgotten_upgrade": "잊힌 도구 업그레이드",
    "jukebox_song.undergarden.gloomper_anthem": "Screem - Gloomper Anthem",
    "jukebox_song.undergarden.gloomper_secret": (
        "AI가 우울두꺼비 그림을 보고 만든 노래"
    ),
    "jukebox_song.undergarden.limax_maximus": "Screem - Limax Maximus",
    "jukebox_song.undergarden.mammoth": "Screem - Mammoth",
    "jukebox_song.undergarden.relict": "Screem - Relict",
}

SIMPLE_NEW_NAMES = {
    "item.undergarden.ancient_chestplate": "고대 갑옷",
    "item.undergarden.ancient_helmet": "고대 헬멧",
    "item.undergarden.ancient_leggings": "고대 레깅스",
    "item.undergarden.ancient_root_boat": "고대 뿌리 보트",
    "item.undergarden.ancient_root_chest_boat": "상자가 실린 고대 뿌리 보트",
    "item.undergarden.blue_mogmoss": "파란 모구이끼",
    "item.undergarden.cloggrum_bucket": "클로그룸 양동이",
    "item.undergarden.cloggrum_bucket.block": "클로그룸 %s 양동이",
    "item.undergarden.cloggrum_bucket.entity": "%s이(가) 든 클로그룸 양동이",
    "item.undergarden.crumbling_catalyst": "부서져 가는 카탈리스트",
    "item.undergarden.denizen_mask": "신비한 가면",
    "item.undergarden.denizen_spawn_egg": "거주민 생성 알",
    "item.undergarden.forgotten_spawn_egg": "잊힌 자 생성 알",
    "item.undergarden.forgotten_upgrade_smithing_template": "대장장이 형판",
    "item.undergarden.greater_dweller_spawn_egg": "거대 토착종 생성 알",
    "item.undergarden.minion_spawn_egg": "잊힌 하수인 생성 알",
    "item.undergarden.mysterious_pot_spawn_egg": "신비한 항아리 생성 알",
    "item.undergarden.rogdorium": "로그도리움",
    "item.undergarden.rogdorium_nugget": "로그도리움 조각",
    "item.undergarden.rotbelcher_spawn_egg": "부패분출자 생성 알",
    "item.undergarden.slop_bowl": "오물 그릇",
    "item.undergarden.smithing_template.forgotten_upgrade.additions_slot_description": (
        "잊힌 주괴 추가"
    ),
    "item.undergarden.smithing_template.forgotten_upgrade.applies_to": "클로그룸 도구",
    "item.undergarden.smithing_template.forgotten_upgrade.base_slot_description": (
        "클로그룸 무기 또는 도구 추가"
    ),
    "item.undergarden.smithing_template.forgotten_upgrade.ingredients": "잊힌 주괴",
    "item.undergarden.smog_mog_spawn_egg": "S'모그 생성 알",
    "item.undergarden.spear": "창",
    "item.undergarden.utheric_cluster": "우테릭 군집",
    "entity.undergarden.blisterbomb": "발포 폭탄",
    "entity.undergarden.boomgourd": "폭탄호박",
    "entity.undergarden.denizen": "거주민",
    "entity.undergarden.depthrock_pebble": "깊은돌 조약돌",
    "entity.undergarden.forgotten": "잊힌 자",
    "entity.undergarden.goo_ball": "점액 공",
    "entity.undergarden.greater_dweller": "거대 토착종",
    "entity.undergarden.gronglet": "그롱이",
    "entity.undergarden.minion_projectile": "하수인 발사체",
    "entity.undergarden.mysterious_pot": "신비한 항아리",
    "entity.undergarden.rogdoric_gronglet": "로그도릭 그롱이",
    "entity.undergarden.rotbelcher": "부패분출자",
    "entity.undergarden.rotbelcher_projectile": "부패분출자 발사체",
    "entity.undergarden.rotten_blisterberry": "썩은 발포 베리",
    "entity.undergarden.smog_mog": "S'모그",
    "entity.undergarden.spear": "창",
    "entity.undergarden.utheric_gronglet": "우테릭 그롱이",
}

BLOCK_PREFIXES = {
    "ancient_root": "고대 뿌리",
    "dreadrock": "공포석",
}
BLOCK_SUFFIXES = {
    "": "",
    "button": "버튼",
    "door": "문",
    "fence": "울타리",
    "fence_gate": "울타리 문",
    "hanging_sign": "매달린 표지판",
    "planks": "판자",
    "pressure_plate": "감압판",
    "sign": "표지판",
    "slab": "반 블록",
    "stairs": "계단",
    "trapdoor": "다락문",
    "bricks": "벽돌",
    "brick_slab": "벽돌 반 블록",
    "brick_stairs": "벽돌 계단",
    "brick_wall": "벽돌 담장",
    "wall": "담장",
    "rogdorium_ore": "로그도리움 광석",
    "utherium_ore": "우테리움 광석",
}

OTHER_BLOCKS = {
    "block.undergarden.blue_mogmoss_rug": "파란 모구이끼 깔개",
    "block.undergarden.denizen_totem": "신비한 토템",
    "block.undergarden.depthrock_pot": "깊은돌 항아리",
    "block.undergarden.grongle_hanging_sign": "매달린 그롱글 표지판",
    "block.undergarden.infuser": "주입기",
    "block.undergarden.potted_puff_mushroom": "화분에 심은 부푼 버섯",
    "block.undergarden.puff_mushroom": "부푼 버섯",
    "block.undergarden.puff_mushroom_cap": "부푼 버섯 갓",
    "block.undergarden.puff_mushroom_stem": "부푼 버섯 줄기",
    "block.undergarden.rogdoric_ancient_root": "로그도릭 고대 뿌리",
    "block.undergarden.rogdoric_gronglet": "로그도릭 그롱이",
    "block.undergarden.rogdorium_block": "로그도리움 블록",
    "block.undergarden.smogstem_hanging_sign": "매달린 안개줄기 표지판",
    "block.undergarden.utheric_gronglet": "우테릭 그롱이",
    "block.undergarden.utherium_growth": "우테리움 성장체",
    "block.undergarden.wigglewood_hanging_sign": "매달린 흔들나무 표지판",
}

TAG_MATERIALS = {
    "Regalium": "레갈륨",
    "Utherium": "우테리움",
    "Cloggrum": "클로그룸",
    "Forgotten": "잊힌 금속",
    "Froststeel": "서리철",
    "Rogdorium": "로그도리움",
    "Raw Cloggrum": "클로그룸 원석",
    "Raw Froststeel": "서리철 원석",
}
TAG_TYPES = {
    "Gems": "보석",
    "Ingots": "주괴",
    "Nuggets": "조각",
    "Ores": "광석",
    "Raw Materials": "원석",
    "Storage Blocks": "저장 블록",
    "Items": "아이템",
}

SUBTITLE_ENTITIES = {
    "Dweller": "토착종",
    "Forgotten": "잊힌 자",
    "Greater Dweller": "거대 토착종",
    "Rotbelcher": "부패분출자",
    "S'Mog": "S'모그",
}
SUBTITLE_ACTIONS = {
    "jumps": "점프함",
    "mutters": "중얼거림",
    "dies": "죽음",
    "hurts": "다침",
    "grumbles": "투덜거림",
    "groans": "신음함",
    "belches": "내뿜음",
    "squeaks": "찍찍거림",
}

QUEST_OVERRIDES = {
    "quest.17C2C8F64B4AE6EE.quest_desc": (
        "&2토착종&r은 &2&lThe Undergarden&r의 소와 같은 동물입니다. \n"
        "온순하며 죽으면 가죽과 토착종 고기를 떨어뜨립니다. \n\n"
        "다행히 젖을 짤 수는 없습니다. &2토착종&r의 우유는 사양할게요."
    ),
    "quest.1E81B903137BB62A.quest_desc": (
        "&2&lThe Undergarden&r의 위험한 몹을 상대하려면 평범한 도구만으로는 부족합니다. "
        "\n\n일반 방패처럼 쓸 수 있는 &7클로그룸 방패&r를 제작할 수 있습니다. "
        "\n\n&7전투도끼&r는 &7잊힌 자&r에게서 희귀 전리품으로 얻어야 합니다."
    ),
    "quest.1FCF946B7BE3C0BD.quest_desc": (
        "&c우테리움&r 도구는 다이아몬드 도구와 비슷하지만, 무기는 &c부패종&r에게 "
        "더 큰 피해를 줍니다! \n\n적이 만들어 낸 물질로 그 적을 더 강하게 공격하는 셈이죠. "
        "대중문화에서 비슷한 장면이 잔뜩 떠오를 법한데, 지금은 하나도 생각나지 않네요..."
    ),
    "quest.2C5A7E4CD8B57E08.quest_desc": (
        "그롱글 나무는 그롱글생장지 생물 군계에서만 자라는, 정글 나무처럼 키가 큰 나무입니다! "
        "\n\n&e그롱이&r도 이 나무에서 나타납니다."
    ),
    "quest.4E3D548E5D8D7D26.quest_desc": (
        "잊힌 들판은 &2&lThe Undergarden&r의 평원입니다. \n\n나무는 없지만 바위와 꽃, "
        "몹이 가득합니다! \n\n다만 &7잊힌 자&r는 나타나지 않습니다. 기대를 꺾어서 미안해요."
    ),
    "quest.76CDC18D7A208512.quest_desc": (
        "&2&lThe Undergarden&r에서는 &c부패종&r이 플레이어를 &c우테리움&r에 감염시킬 수 "
        "있습니다. 감염 수치가 낮으면 시간이 지나며 줄어들지만, 높아지면 저절로 줄지 않습니다. "
        "이때는 공포석 지대 깊은 곳에서만 발견되는 &3로그도리움&r으로 치료해야 합니다. "
        "로그도리움을 먹거나 갑옷에 주입하면 감염을 막을 수 있습니다. 이번에는 제가 "
        "&3로그도리움&r을 조금 드릴게요!"
    ),
    "quest.76CDC18D7A208512.title": "경고",
    "task.2116DA966E4C7711.title": "우테릭 감염 이해하기",
}

QUEST_QUALITY_OVERRIDES = {
    "quest.00CB8D60E7831A57.quest_desc": (
        "지하 묘지는 깊은돌 벽돌로 이루어진 거대한 지하 구조물입니다. 지상으로 튀어나온 "
        "일부를 발견할 수도 있습니다.\n\n거대한 미로 안에는 &7잊힌 자&r와 숨겨진 상자, "
        "보스인 &a잊힌 수호자&r가 있습니다.\n\n단단히 준비하세요!"
    ),
    "quest.01B13BBB41BBB460.quest_desc": (
        "&c우테리움 갑옷&r은 네더라이트 갑옷과 능력치가 같습니다!\n\n대장장이 형판도 "
        "필요하지 않습니다!"
    ),
    "quest.06D13E319C26C949.quest_desc": (
        "핏빛 버섯 습지에는 거대한 핏빛 버섯이 자랍니다.\n\n피를 보면 불안해지니 설명은 "
        "짧게 끝낼게요."
    ),
    "quest.073BA8470EA37A00.quest_desc": "또 다른 바다지만, 이곳은 훨씬 춥습니다.",
    "quest.0A0A991BAC99092C.quest_desc": (
        "쪽빛 버섯 습지는 핏빛 버섯 습지보다 물이 훨씬 많습니다. \n\n쪽빛 버섯은 물론, "
        "작은 안개줄기 나무와 유독성 혼합물 연못도 있습니다. 저 액체에는 어떤 효과가 있을까요..."
    ),
    "quest.0D91A6B36BD2F526.quest_desc": (
        "&7클로그룸 전투도끼&r를 업그레이드해 &2&lThe Undergarden&r 최고의 무기를 만드세요!"
    ),
    "quest.0FA77C28A57E06F1.quest_desc": (
        "장막 버섯은 장막 버섯 습지에서만 발견됩니다.\n\n갈색 갓 아래가 비어 있으면 "
        "버섯 장막이 자랍니다. 이름이 붙은 이유도 바로 이것입니다!"
    ),
    "quest.1054168AFD8520D4.quest_desc": (
        "&a잊힌 수호자&r는 &a잊힌 주괴&r로 만들어진 거대한 골렘입니다.\n\n플레이어를 "
        "표적으로 삼아 수단과 방법을 가리지 않고 공격합니다.\n\n체력은 하트 80개이며, 처치하면 "
        "&a잊힌 조각&r을 떨어뜨립니다."
    ),
    "quest.1190BB433EFA3945.quest_desc": (
        "새총은 &2&lThe Undergarden&r에서 추가되는 재미있는 무기입니다. 탄약은 4종입니다."
        "\n\n정원 민달팽이 점액 공은 맞은 몹에게 끈적임 효과를 줍니다.\n\n깊은돌 "
        "조약돌은 평범한 발사체입니다.\n\n썩은 발포 베리는 충돌하면 폭발합니다.\n\n"
        "&e그롱이&r는 피해를 주지 않고, 날아가며 소리만 냅니다!"
    ),
    "quest.130577AD1A1A8222.quest_desc": (
        "&7클로그룸&r 갑옷은 철 갑옷보다 능력치가 조금 낮지만, 재료가 나무에서 자라다시피 "
        "하니 공평한 셈입니다.\n\n클로그룸 부츠를 신으면 정원 민달팽이 점액도 쉽게 지나갈 수 있습니다!"
    ),
    "quest.141681FE9E524FB0.quest_desc": (
        "&7잊힌 자&r는 지하 묘지에서 나타나는 전사입니다.\n\n고대 갑옷을 입고 클로그룸 "
        "도구를 들며, 이 장비는 처치했을 때 떨어질 수 있습니다.\n\n&c부패종&r도 적으로 여겨 "
        "공격합니다."
    ),
    "quest.15A8F04BC10E619E.quest_desc": (
        "여러 종류의 묘목을 모으려고 수많은 생물 군계를 돌아다니기 싫은 사람도 있습니다. "
        "\n\n&2&lThe Undergarden&r 개발자도 그랬는지, 대부분의 묘목을 울창한 숲에 넣어 "
        "두었습니다!"
    ),
    "quest.16A04B2FC3F0D902.quest_desc": (
        "&7클로그룸&r 도구는 철 도구와 비슷하지만, 철보다는 진흙처럼 보입니다!\n\n다만 "
        "클로그룸 검은 철 검보다 더 강합니다."
    ),
    "quest.1BAE1519E44E40CE.quest_desc": (
        "고대 바다를 떠올려 보세요. 이제 켈프와 &b정원메기&r, &b작은 정원메기&r를 모두 "
        "없애면 됩니다.\n\n그곳이 바로 죽은 바다입니다!"
    ),
    "quest.1C232674CD04024D.quest_desc": (
        "&2&lThe Undergarden&r 차원에는 다채롭고 기괴한 생물 군계, 풍부한 식생, 온순하거나 "
        "적대적인 몹, 그리고 여러 광석과 아이템이 가득합니다.\n\n싸울 준비를 하세요!"
    ),
    "quest.1C232674CD04024D.title": "&2&lThe Undergarden&r에 오신 것을 환영합니다!",
    "quest.1E13D7CE5A9EFF74.quest_desc": (
        "서리 들판은 &2&lThe Undergarden&r의 추운 생물 군계입니다. 거대한 고드름과 가루눈, "
        "얼어붙은 심층 잔디를 보면 얼마나 추운지 알 수 있습니다! \n\n지하에는 평범한 깊은돌 "
        "대신 전율석이 있습니다.\n\n전율석은 돌보다 얼음에 가까워, 그 위에 서면 미끄럽습니다!"
    ),
    "quest.1E13D7CE5A9EFF74.title": "서리 들판",
    "quest.22739522F0D33D7B.quest_desc": (
        "우울호박은 호박처럼 자연적으로 자라며 재배할 수 있습니다.\n\n호박처럼 파이나 랜턴으로 "
        "만들 수 있습니다!\n\n하지만 호박과 달리 폭발물로도 만들 수 있습니다..."
    ),
    "quest.24D38DA8E86DD897.quest_desc": (
        "가장 작고 약한 &c부패종&r입니다. \n\n체력은 하트 5개입니다. \n\n다른 &c부패종&r처럼 "
        "&2돌인간&r과 &7잊힌 자&r를 공격하며 &c우테릭 파편&r을 떨어뜨립니다."
    ),
    "quest.30582B5FBED35FD1.title": "&c우테릭&r",
    "quest.36389696767EFB4E.quest_desc": (
        "메마른 심연은 이름 그대로 황량합니다... 적대적인 몹과 조약돌 외에는 아무것도 "
        "없습니다. \n\n조약돌이라면 차라리 다른 곳에서 찾고 싶네요..."
    ),
    "quest.380D3212D1CBA593.quest_desc": (
        "중간 크기의 &c부패종&r인 &c부패자&r입니다.\n\n체력은 하트 20개입니다.\n\n"
        "다른 &c부패종&r처럼 &2돌인간&r과 &7잊힌 자&r를 공격하며 &c우테릭 파편&r을 떨어뜨립니다."
    ),
    "quest.3AF7446592D19FA6.quest_desc": (
        "&e레갈륨&r은 &2&lThe Undergarden&r에서 에메랄드와 같은 역할을 합니다.\n\n갑옷이나 "
        "도구로 만들 수는 없지만, &2돌인간&r과 다른 아이템을 거래할 때 사용합니다."
    ),
    "quest.3AF7446592D19FA6.title": "&e레갈륨&r",
    "quest.4141EF8B8C316118.quest_desc": (
        "&7클로그룸&r은 &2&lThe Undergarden&r의 철과 같은 광물입니다.\n\n어디서나 발견되며 "
        "수많은 제작법에 사용됩니다.\n\n심지어 몇몇 몹도 떨어뜨립니다!"
    ),
    "quest.4141EF8B8C316118.title": "&7클로그룸&r",
    "quest.43FD4AEBB9548E57.quest_desc": (
        "안개줄기 숲은 쪽빛 버섯 습지와 이웃한 생물 군계입니다.\n\n이곳도 푸른빛을 띠고 "
        "쪽빛 버섯이 자라지만, 안개줄기 나무가 훨씬 큽니다!"
    ),
    "quest.4568C2F465EDB960.quest_desc": (
        "늘어진열매는 거의 모든 생물 군계의 천장에서 자랍니다. 위를 보세요!\n\n빛나는 열매와 "
        "비슷하게 덩굴을 따라 자랍니다."
    ),
    "quest.4C5CFA45D9B4F6D3.quest_desc": (
        "쪽빛 버섯은 안개줄기 나무와 아주 잘 어울리는지 주로 함께 자랍니다!"
    ),
    "quest.4C7E006502E30C20.quest_desc": (
        "이 퀘스트는 AllTheMods 모드팩에서 사용하도록 &6AllTheMods Staff&r 또는 "
        "&2커뮤니티 기여자&r가 작성했습니다.\n\n모든 &6AllTheMods&r 팩에는 "
        "&eAll Rights Reserved&r 라이선스가 적용됩니다. &6AllTheMods Team&r이 배포하지 "
        "않은 공개 모드팩에서는 명시적인 허가 없이 이 퀘스트를 사용할 수 없습니다.\n\n"
        "이 퀘스트는 의도적으로 숨겨져 있습니다. 지금 보인다면 편집 모드입니다."
    ),
    "quest.4D836B9D9E3B898F.quest_desc": (
        "&2돌인간&r은 주민과 철 골렘을 합친 듯한 존재입니다.\n\n오른쪽 클릭해 거래할 수 "
        "있습니다.\n\n적대적인 몹이나 자신을 공격한 플레이어와도 싸웁니다."
    ),
    "quest.4D836B9D9E3B898F.title": "&2돌인간&r",
    "quest.4F3B4990BE6C2A4A.quest_desc": (
        "&7정원 민달팽이&r는 &2&lThe Undergarden&r 곳곳에서 발견되는 작고 무해한 생물입니다. "
        "\n\n눈 골렘처럼 이동한 자리에 흔적을 남기지만, 그 흔적은 훨씬 끈적합니다...\n\n"
        "죽이면 점액을 떨어뜨리지만 흔적에서도 모을 수 있는데, 굳이 죽일 필요가 있을까요!"
    ),
    "quest.4F5A2E2A5C7F4837.quest_desc": (
        "&a잊힌 주괴&r는 지하 묘지의 상자에서 찾거나 &a잊힌 수호자&r를 처치해 얻을 수 "
        "있습니다. \n\n업그레이드에는 지하 묘지 상자에서 발견되는 대장장이 형판도 필요합니다."
    ),
    "quest.511144EF336BFAF5.quest_desc": (
        "안개 첨탑은... 맞아요, 짐작하신 대로 안개가 솟아나는 곳입니다! 물론 &2모구&r와 "
        "&3S'모그&r의 몫도 빼놓을 수 없죠. \n\n이곳에는 발포 베리와 거친 깊은 흙, 안개 "
        "배출구가 있습니다. 배출구에는 가까이 가지 않는 편이 좋습니다..."
    ),
    "quest.51E2728C5E35A152.quest_desc": (
        "서리철은 서리 들판, 서리 낀 안개줄기 숲, 빙해 같은 추운 생물 군계에서 생성됩니다."
        "\n\n이 지역에서 깊은돌을 대신하는 전율석에 광석이 박혀 있습니다. 전율석은 얼음처럼 "
        "미끄러우며 이동 속도를 조금 늦춥니다.\n\n작귀의 배 속에서 서리철 조각을 찾을 수도 있습니다!"
    ),
    "quest.51E2728C5E35A152.title": "&b서리철&r",
    "quest.5B4B5C148D63ACA1.quest_desc": (
        "&a잊힌 하수인&r은 자연적으로 나타나지 않으며 직접 만들어야 합니다. &a잊힌 금속 "
        "블록&r 위에 조각된 우울호박을 놓으세요.\n\n눈 골렘과 비슷하게 플레이어는 공격하지 않고 "
        "적대적인 몹을 향해 발사체를 쏩니다.\n\n체력은 하트 10개이고 죽어도 아무것도 떨어뜨리지 "
        "않습니다... 그런데 왜 죽이려는 건가요?"
    ),
    "quest.5B4B5C148D63ACA1.title": "&a잊힌 하수인&r",
    "quest.5D229FA3A5F92954.quest_desc": (
        "&4작귀&r는 &2&lThe Undergarden&r의 다른 적대적인 몹과 비슷하지만, 전리품은 훨씬 "
        "쓸모 있습니다! \n\n처치하면 &7클로그룸 조각&r이나 &b서리철 조각&r을 떨어뜨릴 수 있습니다."
    ),
    "quest.5E63C78CDC44FF95.quest_desc": (
        "썩은 발포 베리는 그대로 던질 수 없지만 발포 폭탄으로 만들면 던질 수 있습니다! "
        "\n\n한 단계 더 나아가면, 발포 베리를 사방으로 뿌리는 TNT 같은 폭탄호박도 만들 수 있습니다."
    ),
    "quest.6124C0E9E419694B.quest_desc": (
        "&7클로그룸&r 도구를 &a잊힌 주괴&r와 대장장이 형판으로 업그레이드하세요. \n\n"
        "이 도구는 최상급이며, &2&lThe Undergarden&r 블록을 더 빠르게 캡니다. \n\n"
        "검과 도끼는 &c부패수&r와 &a잊힌 수호자&r를 제외한 &2&lThe Undergarden&r 몹에게 더 큰 "
        "피해를 줍니다!"
    ),
    "quest.6124C0E9E419694B.title": "&a잊힌&r 도구",
    "quest.647A87E800C703C3.quest_desc": (
        "제가 가장 좋아하는 생물 군계입니다! \n\n거대한 그롱글 나무가 가득한 초록빛 정글입니다. "
        "\n\n나무 위에서는 &e그롱이&r를 찾을 수 있습니다!"
    ),
    "quest.6751F2651063B3A5.quest_desc": (
        "핏빛 버섯은 핏빛 버섯 습지에서 발견됩니다.\n\n짙은 참나무처럼 생겼으며 대부분 "
        "흰색이지만 일부 블록에는 핏자국이 있습니다!"
    ),
    "quest.6C4B93FE64BD418D.title": "The Undergarden",
    "quest.6D4FB6291CA8D1A6.quest_desc": (
        "안개줄기 나무는 실제 바오밥나무처럼 아래쪽이 훨씬 굵습니다!\n\n회색 원목과 파란 "
        "잎을 지녔습니다.\n안개줄기 숲, 울창한 숲, 쪽빛 버섯 습지 등 여러 생물 군계에서 "
        "찾을 수 있습니다!"
    ),
    "quest.6F416275B6F6D8F0.quest_desc": (
        "발포 베리는 안개 첨탑에서 자랍니다.\n\n환경이 워낙 험해서 일부 열매는 썩은 채로 "
        "자랍니다.\n\n그 열매는 먹지 않는 편이 좋겠지만, 다른 용도가 있을지도 모릅니다!"
    ),
    "quest.70FD8856BFCD9AEE.quest_desc": (
        "가장 크고 위험한 &c부패종&r입니다. \n\n체력은 하트 80개로, 미니 보스라고 해도 될 "
        "정도입니다. \n\n다른 &c부패종&r처럼 &2돌인간&r과 &7잊힌 자&r를 공격하며 &c우테릭 "
        "파편&r을 떨어뜨립니다."
    ),
    "quest.71E1454990DEC451.quest_desc": (
        "&b정원메기&r는 &b작은 정원메기&r보다 크고 사나운 물고기입니다.\n\n전리품도 없고 "
        "양동이에 담을 수도 없습니다. 주는 것이라고는 고통뿐입니다!"
    ),
    "quest.744DBE831C120B2F.quest_desc": (
        "바위가 움직이는 건가요? 잠깐, 바위가 아니라 &2모구&r입니다! \n\n&2모구&r는 깊은돌 "
        "조약돌로 번식시킬 수 있으며, 죽으면 조약돌이나 모구이끼를 떨어뜨릴 수 있습니다!"
        "\n\n모구이끼는 여러 제작법에 사용됩니다!"
    ),
    "quest.744DBE831C120B2F.title": "&2모구&r",
    "quest.7617737FC179EA1A.quest_desc": (
        "&b서리철&r 갑옷은 다이아몬드 갑옷보다 조금 약하지만 밀치기 저항을 크게 높여 줍니다."
        "\n\n대신 이동 속도가 느려집니다. 이 갑옷을 입으면 빠르게 움직이기는 어렵겠네요!"
    ),
    "quest.79C652E3FCB88550.quest_desc": (
        "&5우울두꺼비&r는 기본적으로 온순하지만 방어 수단이 있어 중립적인 몹에 가깝습니다! "
        "\n\n공격받으면 잔류형 물약과 비슷한 효과 구름을 만듭니다. \n\n죽으면 맛있는 다리와 "
        "가죽을 떨어뜨릴 수 있습니다. \n\n우울호박으로 번식시킬 수도 있습니다!"
    ),
    "quest.7E3DA4168D352B42.quest_desc": (
        "이번이 정말 마지막 버섯 습지입니다! \n이 버섯은 평범해 보이지만, 아래에서 자라는 "
        "것이 특별합니다!\n\n바로 버섯 장막입니다. 장식에 아주 유용합니다."
    ),
    "quest.041ED280691BB05D.quest_desc": (
        "&9서리철&r은 &2&lThe Undergarden&r의 추운 생물 군계에서 흔히 발견되는 광석입니다."
    ),
    "quest.16359196D49A6223.title": "&b서리철&r",
    "quest.2C387BFA6EE6FDB7.quest_desc": (
        "&c우테리움 수정&r은 &2&lThe Undergarden&r의 &c부패수&r가 떨어뜨립니다!"
    ),
    "quest.2FA0F5B348322095.quest_desc": (
        "&7클로그룸&r은 &2&lThe Undergarden&r에서 철과 같은 광석이며 곳곳에 생성됩니다."
    ),
    "quest.498483750C18FCD6.title": "&e레갈륨&r",
    "quest.5E6D7C1D7957DD4D.title": "&a잊힌 금속&r",
    "quest.788A7A2F1F438B64.title": "&7클로그룸&r",
}

PRODUCTIVE_BEES = {
    "entity.productivebees.cloggrum_bee": "클로그룸 벌",
    "entity.productivebees.forgotten_bee": "잊힌 벌",
    "entity.productivebees.froststeel_bee": "서리철 벌",
    "entity.productivebees.regalium_bee": "레갈륨 벌",
    "entity.productivebees.utheric_bee": "우테릭 벌",
    "productivebees.ingredient.description.utheric_bee": (
        "조심하세요! 이 벌 떼는 The Undergarden에서 자라는 우울호박 속에 숨어 있습니다."
    ),
    "productivebees.ingredient.description.forgotten_bee": (
        "이 벌은 시간 속에 잊힌 듯합니다. 소문에 따르면 The Undergarden의 지하 묘지에서 "
        "드물게 발견되는 알에서 태어난다고 합니다."
    ),
    "productivebees.ingredient.description.regalium_bee": (
        "The Undergarden의 돌인간과 거래해 특별한 음반을 얻은 황금 벌은 아주 위엄 있는 "
        "모습으로 변합니다."
    ),
}

PRODUCTIVE_QUESTS = {
    "quest.26B9909717528D5E.quest_subtitle": "The Undergarden에서 발견",
    "quest.26B9909717528D5E.title": "우테릭 벌",
    "quest.4F4C1A349F953013.quest_subtitle": "The Undergarden에서 발견",
    "quest.4F4C1A349F953013.title": "잊힌 벌",
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없이 JSON을 기록한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize_terms(value: object) -> object:
    """검수에서 확정한 공통 용어를 문자열 또는 목록에 적용한다."""
    if isinstance(value, str):
        for old, new in TERM_REPLACEMENTS:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [normalize_terms(item) for item in value]
    return value


def translate_block(key: str) -> str | None:
    """규칙적인 신규 블록 이름을 조합한다."""
    if key in OTHER_BLOCKS:
        return OTHER_BLOCKS[key]
    stem = key.removeprefix("block.undergarden.")
    for prefix, translated in BLOCK_PREFIXES.items():
        if stem == prefix:
            return translated
        marker = f"{prefix}_"
        if stem.startswith(marker):
            suffix = stem[len(marker) :]
            if suffix in BLOCK_SUFFIXES:
                return f"{translated} {BLOCK_SUFFIXES[suffix]}"
    return None


def translate_tag(source: str) -> str | None:
    """재료 태그의 규칙적인 이름을 번역한다."""
    specials = {
        "Virulent Mix": "유독성 혼합물",
        "Raw Cloggrum Materials": "클로그룸 원석",
        "Raw Froststeel Materials": "서리철 원석",
        "Slingshot Enchantables": "새총에 부여 가능한 마법",
        "Grongle Logs": "그롱글 원목",
        "Infuser Rogdorium Fuels": "주입기용 로그도리움 연료",
        "Infuser Utherium Fuels": "주입기용 우테리움 연료",
        "Undergarden Mushrooms": "The Undergarden 버섯",
        "Smogstem Logs": "안개줄기 원목",
        "Wigglewood Logs": "흔들나무 원목",
    }
    if source in specials:
        return specials[source]
    for material, translated in sorted(
        TAG_MATERIALS.items(), key=lambda row: -len(row[0])
    ):
        if source == material:
            return translated
        if source.startswith(f"{material} "):
            kind = source[len(material) + 1 :]
            if kind in TAG_TYPES:
                return f"{translated} {TAG_TYPES[kind]}"
    return None


def translate_subtitle(source: str) -> str | None:
    """신규 자막의 개체명과 동작을 조합한다."""
    if source == "Saddle removed":
        return "안장을 벗김"
    for entity, translated in sorted(
        SUBTITLE_ENTITIES.items(), key=lambda row: -len(row[0])
    ):
        if source.startswith(f"{entity} "):
            action = source[len(entity) + 1 :]
            if action in SUBTITLE_ACTIONS:
                return f"{translated} {SUBTITLE_ACTIONS[action]}"
    return None


def translate_new(key: str, source: object) -> object:
    """내장 한국어에 없던 키를 검수된 규칙과 사전으로 번역한다."""
    if not isinstance(source, str):
        raise TypeError(f"문자열이 아닌 신규 언어 값: {key}")
    if key in QUALITY_OVERRIDES:
        return QUALITY_OVERRIDES[key]
    if key in NEW_TRANSLATIONS:
        return NEW_TRANSLATIONS[key]
    if key in SIMPLE_NEW_NAMES:
        return SIMPLE_NEW_NAMES[key]
    if key.startswith("block."):
        translated = translate_block(key)
    elif key.startswith("tag."):
        translated = translate_tag(source)
    elif key.startswith("subtitles."):
        translated = translate_subtitle(source)
    else:
        translated = None
    if translated is None:
        raise KeyError(f"수동 번역 규칙이 없는 신규 키: {key} = {source!r}")
    return translated


def review_language() -> dict[str, object]:
    """현재 설치 JAR의 679개 언어 키를 전수 재검수한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    sources = load_json(LANG_ROOT / "candidate_sources.json")
    for key, source in english.items():
        old = korean[key]
        if sources[key] == "new_translation_required":
            korean[key] = translate_new(key, source)
            sources[key] = "manual_review"
        else:
            korean[key] = normalize_terms(korean[key])
            if key in QUALITY_OVERRIDES:
                korean[key] = QUALITY_OVERRIDES[key]
            if korean[key] != old:
                sources[key] = "manual_quality_review"
        errors = family_goal.validate_value(key, source, korean[key])
        if errors:
            raise ValueError("; ".join(errors))
    write_json(LANG_ROOT / "ko_kr.json", korean)
    write_json(LANG_ROOT / "candidate_sources.json", sources)
    source_counts = Counter(sources.values())
    return {
        "keys_reviewed": len(english),
        "changes_from_initial_candidates": (
            source_counts["manual_quality_review"] + source_counts["manual_review"]
        ),
        "bundled_exact_reuse": source_counts["bundled_ko_kr"],
        "quality_edited": source_counts["manual_quality_review"],
        "new_translation": source_counts["manual_review"],
        "reviewed_or_edited": (
            source_counts["manual_quality_review"] + source_counts["manual_review"]
        ),
        "source_counts": dict(sorted(source_counts.items())),
    }


def replace_quest_text(value: object, replacement: str) -> object:
    """퀘스트 목록에서는 첫 표시 문구만 바꾸고 이미지 요소를 보존한다."""
    replacement = replacement.replace("\n", "\\n")
    if isinstance(value, str):
        return replacement
    if isinstance(value, list) and value and isinstance(value[0], str):
        return [replacement, *value[1:]]
    raise TypeError(f"지원하지 않는 퀘스트 표시 값: {value!r}")


def add_productive_quest_scope() -> None:
    """namespace 검사로 잡히지 않는 Productive Bees 연동 표시 키를 범위에 더한다."""
    root = WORK_ROOT / "quests/related"
    english = load_json(root / "en_us.json")
    korean = load_json(root / "ko_kr.json")
    sources = load_json(root / "candidate_sources.json")
    productive_english = load_json(
        WORK_ROOT.parent / "productivebees/quest_english.json"
    )
    for key, target in PRODUCTIVE_QUESTS.items():
        english[key] = productive_english[key]
        korean[key] = target
        sources[key] = "manual_quality_review"
    write_json(root / "en_us.json", english)
    write_json(root / "ko_kr.json", korean)
    write_json(root / "candidate_sources.json", sources)


def review_quests() -> dict[str, object]:
    """전용·관련 퀘스트와 Productive Bees 연동 키를 전수 검수한다."""
    add_productive_quest_scope()
    reviewed = 0
    source_counts: Counter[str] = Counter()
    seen: set[str] = set()
    overrides = QUEST_OVERRIDES | QUEST_QUALITY_OVERRIDES
    for root in sorted((WORK_ROOT / "quests").glob("*")):
        english_path = root / "en_us.json"
        if not english_path.is_file():
            continue
        english = load_json(english_path)
        korean = load_json(root / "ko_kr.json")
        sources = load_json(root / "candidate_sources.json")
        before = dict(korean)
        for key, source in english.items():
            korean[key] = normalize_terms(korean[key])
            if key in overrides:
                korean[key] = replace_quest_text(korean[key], overrides[key])
                sources[key] = (
                    "manual_review"
                    if key in QUEST_OVERRIDES
                    else "manual_quality_review"
                )
                seen.add(key)
            elif sources[key] == "new_translation_required":
                raise ValueError(f"수동 번역이 빠진 퀘스트 키: {key}")
            elif korean[key] != before[key]:
                sources[key] = "manual_quality_review"
            errors = family_goal.quest_snbt.validate_value(key, source, korean[key])
            if errors:
                raise ValueError("; ".join(errors))
        reviewed += len(english)
        source_counts.update(str(value) for value in sources.values())
        write_json(root / "ko_kr.json", korean)
        write_json(root / "candidate_sources.json", sources)
    unknown = sorted(set(overrides) - seen)
    if unknown:
        raise KeyError(f"현재 퀘스트 원문에 없는 교정 키: {unknown}")
    return {
        "keys_reviewed": reviewed,
        "changes_from_initial_candidates": (
            source_counts["manual_quality_review"] + source_counts["manual_review"]
        ),
        "quality_edited": source_counts["manual_quality_review"],
        "new_translation": source_counts["manual_review"],
        "reviewed_or_edited": (
            source_counts["manual_quality_review"] + source_counts["manual_review"]
        ),
        "source_counts": dict(sorted(source_counts.items())),
    }


def build_bibliowoods() -> dict[str, object]:
    """BiblioWoods의 The Undergarden 목재 직접 연동 키 471개를 생성한다."""
    instance = resolve_source_root()
    matches = sorted((instance / "mods").glob("bibliowoods-*.jar"))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"BiblioWoods JAR 검색 결과가 하나가 아닙니다: {matches}"
        )
    with ZipFile(matches[0]) as archive:
        all_english = json.loads(
            archive.read("assets/bibliowoods/lang/en_us.json").decode("utf-8-sig")
        )
    english = {key: value for key, value in all_english.items() if "undergarden" in key}
    woods = {
        "Grongle": "그롱글",
        "Smogstem": "안개줄기",
        "Wigglewood": "흔들나무",
    }
    old_woods = twilight_family.WOOD_NAMES
    try:
        twilight_family.WOOD_NAMES = woods
        korean = {
            key: twilight_family.translate_bibliowoods_value(value)
            for key, value in english.items()
        }
    finally:
        twilight_family.WOOD_NAMES = old_woods
    root = WORK_ROOT / "bibliowoods"
    write_json(root / "en_us.json", english)
    write_json(root / "ko_kr.json", korean)
    write_json(
        root / "candidate_sources.json",
        {key: "generated_reviewed_translation" for key in english},
    )
    output = OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json"
    merged = load_json(output) if output.is_file() else {}
    preserved = sum(key not in english for key in merged)
    merged.update(korean)
    write_json(output, merged)
    report = {
        "jar": matches[0].name,
        "all_english_keys": len(all_english),
        "undergarden_keys": len(english),
        "existing_keys_preserved": preserved,
        "merged_output_keys": len(merged),
    }
    write_json(WORK_ROOT / "bibliowoods_scope.json", report)
    return report


def review_productive_bees() -> dict[str, object]:
    """Productive Bees의 The Undergarden 직접 연동 표시 키 8개만 교정한다."""
    working = PROJECT_ROOT / "working/productivebees/productivebees/ko_kr.json"
    output = OUTPUT_ASSETS / "productivebees/lang/ko_kr.json"
    working_data = load_json(working)
    output_data = load_json(output)
    missing = sorted(set(PRODUCTIVE_BEES) - set(working_data))
    if missing:
        raise KeyError(f"Productive Bees 연동 키가 없습니다: {missing}")
    working_data.update(PRODUCTIVE_BEES)
    output_data.update(PRODUCTIVE_BEES)
    write_json(working, working_data)
    write_json(output, output_data)
    report = {
        "keys_reviewed": len(PRODUCTIVE_BEES),
        "changes_from_previous_output": len(PRODUCTIVE_BEES),
        "quality_edited": len(PRODUCTIVE_BEES),
        "working_keys_preserved": len(working_data) - len(PRODUCTIVE_BEES),
        "output_keys": len(output_data),
    }
    write_json(WORK_ROOT / "productivebees_scope.json", report)
    return report


def review() -> dict[str, object]:
    """본체와 모든 직접 표시 연동 경로의 검수 결과를 기록한다."""
    report = {
        "family": "The Undergarden",
        "language": review_language(),
        "ftbquests": review_quests(),
        "bibliowoods": build_bibliowoods(),
        "productive_bees": review_productive_bees(),
    }
    write_json(WORK_ROOT / "manual_review_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("review", "bibliowoods", "productivebees"))
    args = parser.parse_args()
    if args.command == "review":
        report = review()
    elif args.command == "bibliowoods":
        report = build_bibliowoods()
    else:
        report = review_productive_bees()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
