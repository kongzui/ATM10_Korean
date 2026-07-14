#!/usr/bin/env python3
"""Relics·Artifacts 계열 검수본에 확정 번역을 배치 단위로 반영한다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile

from local_paths import resolve_source_root
from prepare_relics import WORK_ROOT, find_jar, load_json
from relics_catalog import BATCHES, TARGETS


ARTIFACT_ITEM_NAMES = {
    "anglers_hat": "낚시꾼 모자",
    "antidote_vessel": "해독 용기",
    "aqua_dashers": "아쿠아 대셔",
    "bunny_hoppers": "토끼 점프화",
    "charm_of_shrinking": "축소의 부적",
    "charm_of_sinking": "침몰의 부적",
    "chorus_totem": "코러스 토템",
    "cloud_in_a_bottle": "병 속의 구름",
    "cowboy_hat": "카우보이 모자",
    "cross_necklace": "십자가 목걸이",
    "crystal_heart": "수정 심장",
    "digging_claws": "굴착 발톱",
    "eternal_steak": "영원의 스테이크",
    "everlasting_beef": "영원의 생고기",
    "feral_claws": "야성의 발톱",
    "fire_gauntlet": "화염 건틀릿",
    "flame_pendant": "불꽃 펜던트",
    "flippers": "오리발",
    "golden_hook": "황금 갈고리",
    "helium_flamingo": "헬륨 플라밍고",
    "kitty_slippers": "고양이 슬리퍼",
    "lucky_scarf": "행운의 스카프",
    "mimic_spawn_egg": "미믹 생성 알",
    "night_vision_goggles": "야간 투시경",
    "novelty_drinking_hat": "장난감 음료 모자",
    "obsidian_skull": "흑요석 두개골",
    "onion_ring": "양파 링",
    "panic_necklace": "공황 목걸이",
    "pickaxe_heater": "곡괭이 가열기",
    "plastic_drinking_hat": "플라스틱 음료 모자",
    "pocket_piston": "주머니 피스톤",
    "power_glove": "파워 글러브",
    "rooted_boots": "뿌리내린 장화",
    "running_shoes": "러닝화",
    "scarf_of_invisibility": "투명화 스카프",
    "shock_pendant": "충격 펜던트",
    "snorkel": "스노클",
    "snowshoes": "설피",
    "steadfast_spikes": "견고한 스파이크",
    "strider_shoes": "스트라이더 신발",
    "superstitious_hat": "미신의 모자",
    "thorn_pendant": "가시 펜던트",
    "umbrella": "우산",
    "universal_attractor": "만능 자석",
    "vampiric_glove": "흡혈 장갑",
    "villager_hat": "주민 모자",
    "warp_drive": "워프 드라이브",
    "whoopee_cushion": "방귀 방석",
    "withered_bracelet": "시든 팔찌",
}

ARTIFACT_TITLE_TRANSLATIONS = {
    "Add Face Slot": "얼굴 슬롯 추가",
    "Allow Light Sources": "광원 허용",
    "Allow Walking on Powdered Snow": "가루눈 보행 허용",
    "Archaeology Chance": "고고학 생성 확률",
    "Artifact Rarity": "유물 희귀도",
    "Attack Damage Bonus": "공격 피해 보너스",
    "Attack Knockback Bonus": "공격 밀치기 보너스",
    "Attack Speed Bonus": "공격 속도 보너스",
    "Block Break Speed Bonus": "블록 파괴 속도 보너스",
    "Bonus Invincibility Ticks": "추가 무적 틱",
    "Cancel Lightning Damage": "번개 피해 무효화",
    "Cancel Hot Floor Damage": "뜨거운 바닥 피해 무효화",
    "Campsite": "야영지",
    "Campsite Count": "야영지 생성 시도 횟수",
    "Cooldown": "재사용 대기시간",
    "Cooldown Overlay Offset": "재사용 대기시간 오버레이 위치",
    "Consume on Use": "사용 시 소모",
    "Drinking Speed Bonus": "마시는 속도 보너스",
    "Eating Speed Bonus": "먹는 속도 보너스",
    "Enable Accessories Compat": "Accessories 연동 활성화",
    "Enable Cooldown Overlay": "재사용 대기시간 오버레이 활성화",
    "Enable Curios Compat": "Curios 연동 활성화",
    "Enable Trinkets Compat": "Trinkets 연동 활성화",
    "Entity Equipment Chance": "엔티티 유물 장착 확률",
    "Entity Experience Bonus": "엔티티 경험치 보너스",
    "Fall Damage Multiplier": "낙하 피해 배율",
    "Fart Chance": "방귀 소리 확률",
    "Fire Duration": "불타는 시간",
    "Fire Resistance Duration": "화염 저항 지속 시간",
    "Flight Duration": "비행 지속 시간",
    "Fortune Level Bonus": "행운 레벨 보너스",
    "Grant Fire Resistance": "화염 저항 부여",
    "Health Bonus": "체력 보너스",
    "Health Restored": "회복 체력",
    "Hunger Cost": "허기 비용",
    "Hunger Replenishing Duration": "허기 회복 간격",
    "Grow Plants After Eating": "섭취 후 식물 성장",
    "Haste Duration per Food Point": "허기 회복량당 성급함 지속 시간",
    "Haste Level": "성급함 레벨",
    "Is Glider": "활공 기능",
    "Is Infinite": "무제한 지속",
    "Is Shield": "방패 기능",
    "Jump Strength Bonus": "점프 강도 보너스",
    "Knockback Resistance": "밀치기 저항",
    "Looting Level Bonus": "약탈 레벨 보너스",
    "Luck of the Sea Level Bonus": "바다의 행운 레벨 보너스",
    "Lure Level Bonus": "미끼 레벨 보너스",
    "Magnetism Level": "자력 레벨",
    "Max Damage": "최대 피해",
    "Max Effect Duration": "최대 효과 지속 시간",
    "Max Healing per Hit": "타격당 최대 회복량",
    "Max Y": "최대 Y 좌표",
    "Minimalist Campsites": "간소화된 야영지",
    "Min Y": "최소 Y 좌표",
    "Min Damage": "최소 피해",
    "Modify Hurt Sounds": "피격음 변경",
    "Mount Speed Bonus": "탈것 속도 보너스",
    "Movement Speed on Snow Bonus": "눈 위 이동 속도 보너스",
    "Nullify Ender Pearl Damage": "엔더 진주 피해 무효화",
    "Oxygen Bonus": "산소 보너스",
    "Absorption Ratio": "흡수 비율",
    "Recharge Duration": "재충전 시간",
    "Remove Slot Restrictions": "슬롯 제한 제거",
    "Repel Creepers": "크리퍼 퇴치",
    "Repel Phantoms": "팬텀 퇴치",
    "Reputation Bonus": "평판 보너스",
    "Safe Fall Distance Bonus": "안전 낙하 거리 보너스",
    "Scale Modifier": "크기 배율",
    "Show First Person Gloves": "일인칭 장갑 표시",
    "Show Tooltips": "유물 툴팁 표시",
    "Slipperiness Reduction": "미끄러움 감소",
    "Speed Duration": "신속 지속 시간",
    "Speed Level": "신속 레벨",
    "Sprint Jump Horizontal Velocity": "질주 이단 점프 수평 속도",
    "Sprint Jump Vertical Velocity": "질주 이단 점프 수직 속도",
    "Sprinting Speed Bonus": "질주 속도 보너스",
    "Sprinting Step Height Bonus": "질주 시 오르기 높이 보너스",
    "Strength": "효과 강도",
    "Strike Chance": "발동 확률",
    "Swim Speed Bonus": "수영 속도 보너스",
    "Teleportation Chance": "순간이동 확률",
    "Tool Tier": "도구 등급",
    "Underwater Fall Damage": "수중 낙하 피해",
    "Use Modded Chests": "다른 모드 상자 사용",
    "Use Modded Mimic Textures": "다른 모드 미믹 텍스처 사용",
    "Water Breathing Duration": "수중 호흡 지속 시간",
    "Wither Chance": "시듦 부여 확률",
    "Wither Duration": "시듦 지속 시간",
    "Wither Level": "시듦 레벨",
}

ARTIFACT_EXACT = {
    "artifacts.advancements.adventurous_eater.description": "유물을 먹으세요",
    "artifacts.advancements.adventurous_eater.title": "모험적인 미식가",
    "artifacts.advancements.amateur_archaeologist.description": "유물을 찾으세요",
    "artifacts.advancements.amateur_archaeologist.title": "아마추어 고고학자",
    "artifacts.advancements.chest_slayer.description": "미믹을 처치하세요",
    "artifacts.advancements.chest_slayer.title": "상자 사냥꾼",
    "artifacts.config.general.artifactRarity.description.1": (
        "1보다 큰 값은 유물을 더 희귀하게 하고, 0과 1 사이의 값은 더 흔하게 합니다"
    ),
    "artifacts.config.general.artifactRarity.description.2": (
        "이 값을 두 배로 늘리면 유물을 찾기가 약 두 배 어려워지며, 반대도 마찬가지입니다"
    ),
    "artifacts.config.general.campsite.campsiteCount.description.0": (
        "청크마다 야영지 생성을 시도하는 횟수"
    ),
    "artifacts.config.general.campsite.minimalistCampsites.description": (
        "야영지를 상자 또는 미믹 하나로 대체합니다"
    ),
    "artifacts.config.general.campsite.mimicChance.description": (
        "야영지의 상자 대신 미믹이 생성될 확률"
    ),
    "artifacts.config.general.campsite.useModdedChests.description": (
        "야영지를 생성할 때 다른 모드의 나무 상자를 사용할지 여부"
    ),
    "artifacts.config.items.thorn_pendant.maxDamage.description": (
        "가시 펜던트가 발동할 때 입히는 최소 피해량"
    ),
    "artifacts.config.items.thorn_pendant.minDamage.description": (
        "가시 펜던트가 발동할 때 입히는 최대 피해량"
    ),
    "artifacts.config.title": "Artifacts 설정",
    "artifacts.creative_tab": "Artifacts",
    "artifacts.key_category": "Artifacts",
    "artifacts.subtitles.entity.mimic.close": "미믹이 닫힘",
    "artifacts.subtitles.entity.mimic.death": "미믹이 죽음",
    "artifacts.subtitles.entity.mimic.hurt": "미믹이 다침",
    "artifacts.subtitles.entity.mimic.open": "미믹이 뛰어오름",
    "artifacts.tooltip.ability.attribute_modifiers.generic.attack_burning_duration": (
        "착용자의 근접 공격이 화염 피해를 줍니다"
    ),
    "artifacts.tooltip.ability.attribute_modifiers.generic.flatulence": (
        "착용자의 방귀가 더 잦아집니다"
    ),
    "artifacts.tooltip.ability.attribute_modifiers.generic.invincibility_ticks": (
        "피해를 입은 뒤의 무적 시간이 늘어납니다"
    ),
    "artifacts.tooltip.ability.attribute_modifiers.generic.sprinting_step_height": (
        "질주 중 착용자가 오를 수 있는 높이가 늘어납니다"
    ),
    "artifacts.tooltip.ability.attribute_modifiers.player.entity_experience": (
        "생물이 떨어뜨리는 경험치가 증가합니다"
    ),
    "artifacts.tooltip.ability.attribute_modifiers.player.villager_reputation": (
        "주민의 거래 가격이 낮아집니다"
    ),
    "artifacts.tooltip.ability.auto_smelt": "채굴한 광물을 자동으로 제련합니다",
    "artifacts.tooltip.ability.damage_absorption.chance": (
        "착용자의 근접 공격이 %s%% 확률로 체력을 흡수합니다"
    ),
    "artifacts.tooltip.ability.death_protection_teleport.chance": (
        "치명적인 피해를 받으면 %s%% 확률로 다른 곳으로 순간이동합니다"
    ),
    "artifacts.tooltip.ability.mob_effects.invisibility": "착용자를 투명하게 만듭니다",
    "artifacts.tooltip.ability.mob_effects.night_vision.partial": (
        "착용자가 어둠 속을 조금 더 잘 볼 수 있게 합니다"
    ),
    "artifacts.tooltip.ability.replenish_hunger_on_grass": (
        "잔디 위를 걸으면 허기가 서서히 회복됩니다"
    ),
    "artifacts.tooltip.ability.enchantment_level_modifiers.looting.single_level": (
        "처치한 엔티티에 약탈 레벨 1을 추가로 적용합니다"
    ),
    "artifacts.tooltip.ability.retaliation_effects.fire.chance": (
        "%s%% 확률로 공격자에게 불을 붙입니다"
    ),
    "artifacts.tooltip.ability.retaliation_effects.lightning.chance": (
        "%s%% 확률로 공격자에게 번개를 내리칩니다"
    ),
    "artifacts.tooltip.ability.retaliation_effects.thorns.chance": (
        "%s%% 확률로 공격자에게 피해를 줍니다"
    ),
    "artifacts.tooltip.ability.swim_in_air.keymapping": (
        "공중에서 %s 키를 눌러 헤엄치기 시작합니다"
    ),
    "artifacts.tooltip.ability.swim_in_air.swimming": (
        "제한된 시간 동안 공중에서 헤엄칠 수 있습니다"
    ),
    "artifacts.tooltip.ability.tool_tier_upgrade": (
        "착용자의 기본 채굴 등급을 %s 등급으로 높입니다"
    ),
    "artifacts.tooltip.cooldown": "+재사용 대기시간 (%s)",
    "artifacts.tooltip.cosmetic": "치장용",
    "artifacts.tooltip.cosmetics_disabled": "치장 효과 꺼짐(오른쪽 클릭으로 전환)",
    "artifacts.tooltip.cosmetics_enabled": "치장 효과 켜짐(오른쪽 클릭으로 전환)",
    "artifacts.tooltip.item.novelty_drinking_hat": (
        "'이봐! 난 1등이고, 중력으로 음료를 마시지!'"
    ),
    "artifacts.tooltip.toggle_keymapping": "%s 키를 눌러 전환",
    "tag.mob_effect.artifacts.antidote_vessel_cancellable": "해독 용기로 단축 가능한 효과",
}

RELIC_ITEM_NAMES = {
    "reflective_necklace": "반사 목걸이",
    "jellyfish_necklace": "해파리 목걸이",
    "kinetic_belt": "운동력 허리띠",
    "springy_boot": "용수철 장화",
    "leafy_mantle": "잎사귀 망토",
    "roller_skate": "롤러스케이트",
    "midnight_mantle": "한밤의 망토",
    "chorus_staff": "코러스 지팡이",
    "piglin_mask": "피글린 가면",
    "cut_glass_boot": "세공 유리 장화",
    "ring_of_the_seven_deadly_sins": "칠대 죄악의 반지",
    "sphere_of_self_sacrifice": "자기희생의 구체",
    "hunting_belt": "사냥 허리띠",
    "rider_flute": "기수의 피리",
    "clot_of_time": "시간의 응어리",
    "chef_hat": "요리사 모자",
    "raw_meatball": "생 미트볼",
    "cooked_meatball": "익힌 미트볼",
    "experience_disperser": "경험치 분산기",
    "glitchy_mantle": "오류의 망토",
    "ghostly_mantle": "유령 망토",
    "shield_of_retaliation": "보복의 방패",
    "relic_experience_bottle": "유물 경험치 병",
    "golden_tooth": "황금 이빨",
    "pet_bone": "반려동물 뼈",
}

RELIC_GLOBAL_REPLACEMENTS = {
    "장애가 있는": "비활성화",
    "경험 소스": "경험치 획득 조건",
    "경험 포인트": "경험치",
    "타겟팅": "적용 대상",
    "선적 서류 비치": "문서",
    "유물 체험": "유물 경험치",
    "능력 수준": "능력 레벨",
    "상대적 수준": "환산 레벨",
    "상대 레벨": "환산 레벨",
    "유물소유시간": "유물 보유 시간",
    "글라이딩": "활공",
    "데미지": "피해",
    "손상": "피해",
    "오브": "구체",
    "바운스": "튕기기",
    "유물 운반자": "유물 소지자",
    "유물 보유자": "유물 소지자",
    "건강": "체력",
    "애완동물": "반려동물",
    "마운트": "탈것",
    "플루트": "피리",
    "텔레포트": "순간이동",
    "목표물": "대상",
    "스펙트럼": "유령",
    "스턴": "기절",
    "비밀 열쇠": "웅크리기 키",
    "글리치": "오류",
    "결함이 있는 사본": "오류 사본",
    "결함 있는 사본": "오류 사본",
    "금니": "황금 이빨",
    "치아": "이빨",
    "다시 롤링": "재추첨",
    "다시 굴립니다": "재추첨합니다",
    "배고픔": "허기",
}

RELIC_EXACT = {
    "itemGroup.relics": "Relics",
    "relics.description.relic.intro.title": "Relics에 오신 것을 환영합니다!",
    "relics.description.relic.intro.top_scroll.title": "위쪽 두루마리",
    "relics.description.relic.intro.bottom_scroll.title": "아래쪽 두루마리",
    "relics.description.researching.bookmarks.ability_experience": (
        "능력 경험치 획득 조건"
    ),
    "relics.description.researching.bookmarks.ability_targeting": "능력 적용 대상",
    "relics.description.researching.bookmarks.synergy_targeting": "시너지 적용 대상",
    "relics.description.researching.ability.targeting.neutral_mobs": (
        "중립적 생물에게 적용됩니다"
    ),
    "relics.description.researching.ability.targeting.team_players": (
        "같은 팀의 플레이어에게 적용됩니다"
    ),
    "relics.description.researching.ability.targeting.other_team_players": (
        "다른 팀의 플레이어에게 적용됩니다"
    ),
    "relics.description.relic.intro.customization": (
        "여기에서 원하는 대로 유물을 설정할 수 있습니다! 화면이 복잡해 보일 수 있지만 "
        "구조는 어렵지 않습니다."
    ),
    "relics.description.relic.intro.buttons": (
        "각 탭에는 여러 버튼이 있습니다. 거의 모두 이름이 표시되므로 기능을 모르겠다면 "
        "버튼에 마우스를 올려 설명을 확인하세요."
    ),
    "relics.description.researching.general.player_experience.title_1": "경험치:",
    "relics.description.researching.general.relic_progress.title": "유물 성장 진행도:",
    "relics.description.researching.general.documentation.title": "문서",
    "relics.description.researching.relic.experience.title": "유물 경험치:",
    "relics.description.researching.ability.info.level": "능력 레벨:",
    "relics.description.ability.research.rule_1.title": "탐색",
    "relics.description.ability.research.rule_3.title": "세부 사항 확인",
    "relics.description.relic.rankup.title": "유물 등급 상승",
    "relics.description.ability.levelup.title": "능력 레벨 상승",
    "relics.description.ability.reroll.title": "능력 속성 재추첨",
    "relics.description.ability.reset.title": "능력 레벨 초기화",
    "relics.description.researching.general.player_experience.extra_info": (
        "바닐라 Minecraft의 플레이어 경험치입니다. 몹 처치, 광석 채굴, 아이템 제련 "
        "등으로 얻습니다."
    ),
    "relics.description.researching.general.relic_rank.extra_info": (
        "유물의 등급을 직접 올리면 모든 업그레이드 진행도가 초기화되지만 최대 레벨이 "
        "증가합니다."
    ),
    "relics.description.statistic.relic.retention_time": "유물 보유 시간",
    "relics.description.jellyfish_necklace.ability.shock.mode.enabled": "활성화",
    "relics.description.jellyfish_necklace.ability.shock.mode.disabled": "비활성화",
    "relics.description.jellyfish_necklace.ability.regeneration.statistic.health_regenerated": (
        "회복한 체력"
    ),
    "relics.description.kinetic_belt.ability.gliding.mode.enabled": "활성화",
    "relics.description.kinetic_belt.ability.gliding.mode.disabled": "비활성화",
    "relics.description.kinetic_belt.synergy.electricity.mode.enabled": "활성화",
    "relics.description.kinetic_belt.synergy.electricity.mode.disabled": "비활성화",
    "relics.description.reflective_necklace.description": (
        "이 유물은 공격을 막지는 않습니다. 대신 피해 일부를 떠맡아 착용자 곁의 "
        "창백한 구체에 보관합니다. 착용자가 반격하면 구체들이 차례로 날아가 적이나 "
        "벽에 부딪혀 산산이 부서집니다."
    ),
    "relics.description.reflective_necklace.ability.reflection.statistic.total_orbs": (
        "생성한 구체"
    ),
    "relics.description.jellyfish_necklace.description": (
        "이 유물은 물이 있는 곳에서 생기를 얻습니다. 비를 맞거나 액체 속에 있으면 "
        "착용자의 몸을 안정시키고 상처를 회복합니다. 촉수에 전기 에너지가 쌓였을 "
        "때 무언가가 스치면 전기 사슬 하나가 풀려나 경로의 모든 대상을 찌릅니다."
    ),
    "relics.description.jellyfish_necklace.ability.shock.rank_modifier.charge": (
        "능력이 발동하면 착용자는 %10$s초 동안 공격으로 대상을 %5$s초간 마비시킬 수 "
        "있습니다. 현재 발동 중 이 효과로 이미 마비된 대상에게는 다시 적용되지 않습니다."
    ),
    "relics.description.kinetic_belt.description": (
        "이 유물은 착용자를 날게 하지는 않지만 더 오래 공중에 머물게 합니다. 고도가 "
        "천천히 낮아지고 운동량을 더 잘 유지하며 부드럽게 착지합니다."
    ),
    "relics.description.springy_boot.description": (
        "이 유물을 신으면 땅에 처음 닿은 뒤에도 낙하가 끝나지 않습니다. 바닥이 "
        "착용자를 다시 공중으로 밀어 올리고, 힘이 다할 때까지 계속 튕겨 나갑니다."
    ),
    "relics.description.springy_boot.ability.bounce.statistic.secondary_bounces": (
        "튕긴 횟수"
    ),
    "relics.description.springy_boot.ability.bounce.statistic.shockwave_damage": (
        "충격파로 준 피해"
    ),
    "relics.description.leafy_mantle.description": (
        "이 유물을 두르면 나뭇잎이 착용자에게 길을 내줍니다. 가지 사이를 방해 없이 "
        "움직이며 서서히 체력을 회복합니다. 죽음이 가까워지면 숲이 대신 피해를 받습니다."
    ),
    "relics.description.roller_skate.description": (
        "이 유물을 신으면 평범한 달리기도 특별해집니다. 바닥을 미끄러지듯 빠르게 "
        "움직이고, 강하게 드리프트하면 바퀴에서 칼날처럼 날카로운 불꽃이 튑니다."
    ),
    "relics.description.roller_skate.ability.skating.statistic.damage_resisted": (
        "스케이트 중 감소한 피해"
    ),
    "relics.description.roller_skate.ability.skating.statistic.sparks_created": (
        "드리프트 중 생성한 불꽃"
    ),
    "relics.description.roller_skate.ability.skating.statistic.damage_dealt": (
        "불꽃으로 준 피해"
    ),
    "relics.description.midnight_mantle.description": (
        "이 유물은 달의 위상에 따라 변합니다. 만월에는 더 빠르고 강하게 공격하고, "
        "신월에는 더 튼튼해져 상처를 쉽게 회복합니다. 어둠은 착용자를 숨기고, 피해를 "
        "받으면 주변의 별들이 치명적인 별자리를 이룹니다."
    ),
    "relics.description.midnight_mantle.ability.phase.mode.new_moon": "신월",
    "relics.description.midnight_mantle.ability.phase.rank_modifier.switch": (
        "능력 모드를 전환하면 %5$s초 동안 효과가 %6$s%% 증가합니다."
    ),
    "relics.description.midnight_mantle.ability.phase.statistic.duration_new_moon": (
        "신월 모드 유지 시간"
    ),
    "relics.description.midnight_mantle.ability.phase.statistic.duration_full_moon": (
        "만월 모드 유지 시간"
    ),
    "relics.description.midnight_mantle.ability.phase.statistic.additional_damage": (
        "추가로 준 피해"
    ),
    "relics.description.midnight_mantle.ability.constellation.statistic.star_stun": (
        "별 폭발의 기절 시간"
    ),
    "relics.description.midnight_mantle.ability.starfall.statistic.shockwave_stun": (
        "별 충격파의 기절 시간"
    ),
    "relics.description.midnight_mantle.ability.starfall.statistic.star_bounces": (
        "별이 튕긴 횟수"
    ),
    "relics.description.chorus_staff.description": (
        "이 유물은 거리를 단순하게 뛰어넘습니다. 한 번 휘두르면 착용자가 그 자리에서 "
        "사라져 순식간에 앞쪽에 나타납니다."
    ),
    "relics.description.chorus_staff.ability.blink.rank_modifier.flicker": (
        "순간이동할 때 주변의 모든 대상이 잠시 플레이어를 인식하지 못합니다."
    ),
    "relics.description.chorus_staff.ability.blink.statistic.targets": (
        "순간이동 중 소지자를 놓친 대상"
    ),
    "relics.description.piglin_mask.description": (
        "이 유물은 네더에서 태어난 피글린의 모습을 본뜹니다. 가면을 쓴 낯선 이를 "
        "피글린이 곧바로 적대하지 않으며, 금을 거래하면 평소보다 많은 물품을 줍니다. "
        "싸움이 벌어지면 익숙한 얼굴을 지키려고 나섭니다."
    ),
    "relics.description.piglin_mask.ability.looting.rank_modifier.frenzy": (
        "떨어진 이빨을 주우면 %3$s초 동안, 모은 이빨 하나당 주는 피해가 %4$s%%, 공격 "
        "속도가 %5$s%% 증가합니다. 새 이빨을 주우면 지속 시간이 갱신됩니다. 모은 이빨이 "
        "32개에 도달하면 이후에는 지속 시간이 갱신되지 않지만 끝날 때까지 모든 보너스가 "
        "3배가 됩니다."
    ),
    "relics.description.piglin_mask.ability.looting.statistic.teeth_picked_up": (
        "주운 황금 이빨"
    ),
    "relics.description.piglin_mask.ability.neutrality.statistic.target": (
        "소지자를 지킨 피글린"
    ),
    "relics.description.cut_glass_boot.description": (
        "이 유물은 액체를 항상 장애물로 여기지 않습니다. 액체를 내부에 저장하고 발밑의 "
        "같은 액체를 알아보아 착용자가 그 표면을 걸을 수 있게 합니다."
    ),
    "relics.description.ring_of_the_seven_deadly_sins.description": (
        "이 유물은 착용자의 죄악에 반응하지만 어느 것도 순수한 선물은 아닙니다. 대상보다 "
        "높거나, 분노하거나, 굶주리거나, 부유하거나, 더 오래 참을 때 힘을 주지만 모든 "
        "이점에는 빈틈이 있습니다. 상황이 바뀌면 같은 죄악이 주인에게 불리하게 작용합니다."
    ),
    "relics.description.ring_of_the_seven_deadly_sins.ability.pride": "교만",
    "relics.description.ring_of_the_seven_deadly_sins.ability.envy": "질투",
    "relics.description.ring_of_the_seven_deadly_sins.ability.wrath": "분노",
    "relics.description.ring_of_the_seven_deadly_sins.ability.gluttony": "폭식",
    "relics.description.ring_of_the_seven_deadly_sins.ability.greed.description": (
        "행운이 %1$s, 전리품 획득량이 %2$s 증가하지만 %3$s%% 확률로 유물 소지자가 "
        "얻은 전리품이 파괴됩니다."
    ),
    "relics.description.ring_of_the_seven_deadly_sins.statistic.unequip_attempts": (
        "반지 해제 시도"
    ),
    "relics.description.ring_of_the_seven_deadly_sins.ability.pride.statistic.additional_damage": (
        "높이 차이로 준 추가 피해"
    ),
    "relics.description.ring_of_the_seven_deadly_sins.ability.pride.statistic.damage_received": (
        "높이 차이로 받은 추가 피해"
    ),
    "relics.description.ring_of_the_seven_deadly_sins.ability.envy.statistic.defensive_shift": (
        "체력 차이로 받은 추가 피해"
    ),
    "relics.description.ring_of_the_seven_deadly_sins.ability.wrath.statistic.bonus_damage": (
        "타이밍 구간에서 준 추가 피해"
    ),
    "relics.description.ring_of_the_seven_deadly_sins.ability.greed.statistic.nullified_tables": (
        "파괴된 전리품 획득"
    ),
    "relics.description.ring_of_the_seven_deadly_sins.ability.gluttony.statistic.positive_duration": (
        "긍정적 허기 효과 유지 시간"
    ),
    "relics.description.ring_of_the_seven_deadly_sins.ability.gluttony.statistic.negative_duration": (
        "부정적 허기 효과 유지 시간"
    ),
    "relics.description.sphere_of_self_sacrifice.description": (
        "이 유물은 체력을 빼앗았다가 더 많이 돌려줍니다. 착용자가 자신의 피를 바치면 "
        "잃은 체력이 이자까지 붙어 서서히 돌아옵니다."
    ),
    "relics.description.sphere_of_self_sacrifice.ability.sacrifice.statistic.salvation_triggers": (
        "능력 발동과 맞바꾼 피해 완화 횟수"
    ),
    "relics.description.sphere_of_self_sacrifice.ability.sacrifice.statistic.salvation_damage_blocked": (
        "능력 발동과 맞바꿔 완화한 피해"
    ),
    "relics.description.hunting_belt.description": (
        "이 유물은 착용자 대신 곁의 길들인 짐승에게 힘을 줍니다. 반려동물의 공격이 "
        "더 강해지며, 함께 싸우는 동료가 많을수록 선택한 대상은 더 불리해집니다."
    ),
    "relics.description.hunting_belt.ability.pack": "무리",
    "relics.description.rider_flute.description": (
        "이 유물은 탈것이 보이지 않을 때도 가까이 둘 수 있게 합니다. 길들인 탈것을 "
        "피리 안에 넣고 다시 꺼내거나 불러올 수 있어 마구간과 고삐가 없어도 언제든 "
        "곁에 둘 수 있습니다."
    ),
    "relics.description.rider_flute.ability.stable": "마구간",
    "relics.description.rider_flute.ability.stable.statistic.captured_mounts": (
        "피리에 넣은 탈것"
    ),
    "relics.description.rider_flute.ability.stable.statistic.released_mounts": (
        "피리에서 꺼낸 탈것"
    ),
    "relics.description.rider_flute.ability.stable.statistic.healed_health": (
        "피리 안에서 탈것이 회복한 체력"
    ),
    "relics.description.rider_flute.ability.stable.statistic.distance_traveled": (
        "피리에서 꺼낸 탈것을 타고 이동한 거리"
    ),
    "relics.message.rider_flute.deployed_suffix": " [꺼냄]",
    "relics.description.clot_of_time.description": (
        "이 유물은 착용자가 방금 지나온 길을 따라 시간을 되돌립니다. 몸이 이미 있었던 "
        "곳으로 돌아가며 최근의 순간을 한 단계씩 되감습니다."
    ),
    "relics.description.clot_of_time.ability.rewind": "시간 역행",
    "relics.description.clot_of_time.ability.rewind.statistic.health_restored": (
        "체력 되감기로 회복한 체력"
    ),
    "relics.description.chef_hat.description": (
        "이 유물은 처치한 대상의 전리품에 먹거리를 더합니다. 대상이 죽으면 생고기처럼 "
        "바로 먹거나 익혀서 더 든든하게 먹을 수 있는 미트볼이 남을 수 있습니다."
    ),
    "relics.description.chef_hat.ability.satiety.rank_modifier.quick_meal": (
        "미트볼을 3배 빠르게 먹습니다."
    ),
    "relics.description.chef_hat.ability.satiety.statistic.meatballs_dropped": (
        "대상이 떨어뜨린 미트볼"
    ),
    "relics.description.chef_hat.ability.satiety.statistic.health_restored": (
        "미트볼로 회복한 체력"
    ),
    "relics.description.experience_disperser.description": (
        "이 유물은 경험치가 한곳에만 쌓이게 두지 않습니다. 유물 하나가 경험치를 받으면 "
        "그 일부를 다른 유물에도 나누어 모든 장비를 함께 성장시킵니다."
    ),
    "relics.description.experience_disperser.ability.dispersion.statistic.distributions": (
        "경험치 분산 발동 횟수"
    ),
    "relics.description.experience_disperser.ability.dispersion.statistic.distributed_experience": (
        "분산된 경험치"
    ),
    "relics.description.experience_disperser.ability.dispersion.statistic.player_xp_conversions": (
        "경험치 구체 변환 횟수"
    ),
    "relics.description.experience_disperser.ability.dispersion.statistic.converted_player_experience": (
        "변환된 플레이어 경험치"
    ),
    "relics.description.glitchy_mantle.description": (
        "이 유물을 두르면 착용자의 모습과 실제 위치가 어긋납니다. 공격이 빗나가 적을 "
        "혼란스럽게 하고, 뒤에 남은 오류 사본과 부딪힌 적은 잠시 정신을 잃습니다. 발밑의 "
        "공허마저 굳어 단단한 바닥이 없어도 다음 걸음을 내디딜 수 있습니다."
    ),
    "relics.description.glitchy_mantle.ability.illusion.mode.enabled": "활성화",
    "relics.description.glitchy_mantle.ability.distortion.statistic.misses": (
        "유도한 빗나감"
    ),
    "relics.description.glitchy_mantle.ability.illusion.statistic.illusions": (
        "생성한 오류 사본"
    ),
    "relics.description.glitchy_mantle.ability.illusion.statistic.target_detonations": (
        "대상이 파괴한 사본"
    ),
    "relics.description.glitchy_mantle.ability.illusion.statistic.stun_duration": (
        "사본이 준 총 기절 시간"
    ),
    "relics.description.glitchy_mantle.ability.glitch.statistic.forced_falls": (
        "강제 추락 횟수"
    ),
    "relics.description.glitchy_mantle.ability.glitch.statistic.phase_rollbacks": (
        "안전 지점으로 돌아간 횟수"
    ),
    "relics.description.glitchy_mantle.ability.glitch.mode.enabled": "활성화",
    "relics.description.glitchy_mantle.synergy.electricity.mode.enabled": "활성화",
    "relics.description.glitchy_mantle.ability.glitch.rank_modifier.phase": (
        "유물 소지자가 단단한 블록을 최대 %3$s초 동안 통과할 수 있습니다. 제한 시간을 "
        "넘기면 마지막 안전 지점으로 돌아갑니다."
    ),
    "relics.description.glitchy_mantle.ability.glitch.enabled.description": (
        "유물 소지자가 단단한 바닥을 걷듯 공중을 이동할 수 있습니다. 공중에서 %1$s초 "
        "넘게 멈춰 있으면 발밑이 불안정해져 추락하며, 착지할 때까지 낙하 피해를 %2$s%% "
        "더 받습니다. 웅크리기 키를 누르면 낙하 피해 없이 직접 아래로 내려갈 수 있습니다."
    ),
    "relics.description.ghostly_mantle.description": (
        "이 유물의 소지자 뒤로 무덤 안개가 흐릅니다. 안개에 들어온 대상은 숨이 막히고, "
        "소지자와 눈을 마주치면 힘을 잃습니다. 죽음이 닥치면 망토가 잠시 몸을 유령으로 "
        "바꾸어 잔혹한 운명에서 벗어나게 합니다."
    ),
    "relics.description.ghostly_mantle.ability.fog.mode.enabled": "활성화",
    "relics.description.ghostly_mantle.ability.gaze.statistic.charges_applied": (
        "적용한 충전"
    ),
    "relics.description.ghostly_mantle.ability.fog.statistic.fog_clouds": (
        "생성한 안개 구름"
    ),
    "relics.description.ghostly_mantle.ability.spectral_escape": "유령 탈출",
    "relics.description.ghostly_mantle.ability.spectral_escape.statistic.reprisal_damage": (
        "유령 형태의 복수 모드에서 준 추가 피해"
    ),
    "relics.description.ghostly_mantle.ability.spectral_escape.statistic.spectral_form_duration": (
        "유령 형태 유지 시간"
    ),
    "relics.description.shield_of_retaliation.description": (
        "이 방패에는 힘보다 완벽한 타이밍이 필요합니다. 정확한 순간에 받아친 공격은 "
        "소지자에게 닿기 전에 힘을 잃고, 적에게는 아무것도 남지 않습니다."
    ),
    "relics.description.shield_of_retaliation.ability.retaliation": "받아치기",
    "relics.description.shield_of_retaliation.ability.retaliation.description": (
        "오른쪽 버튼을 누르면 %1$s초 동안 받아치기 판정이 열립니다. 피해 원인이 플레이어 "
        "앞에 있으면 피해를 막고, 위치가 없는 피해는 보는 방향과 관계없이 막습니다. 판정 "
        "동안 아무것도 막지 못하면 이후 %3$s초 안에 받는 다음 공격 피해가 %2$s% "
        "증가합니다. 버튼을 놓거나 받아치기에 성공하거나 판정이 끝나면 %4$s초 동안 "
        "재사용 대기시간이 적용됩니다."
    ),
    "relics.description.shield_of_retaliation.ability.retaliation.rank_modifier.projectile": (
        "방패가 활성화된 동안 날아오는 발사체를 플레이어 앞에 멈춰 시선을 따라 움직이게 "
        "합니다. 붙잡은 발사체 하나당 받아치기 판정이 %6$s초 늘어납니다. 버튼을 놓거나 "
        "판정이 끝나면 모든 발사체가 조준점의 대상을 향해 발사되어 %5$s% 더 큰 피해를 "
        "줍니다."
    ),
    "relics.description.shield_of_retaliation.ability.retaliation.statistic.blocks": (
        "피해 차단 횟수"
    ),
    "relics.description.shield_of_retaliation.ability.retaliation.statistic.targets_stunned": (
        "기절시킨 대상"
    ),
    "entity.relics.spore": "포자",
    "entity.relics.kinetic_electricity": "전기 사슬",
    "entity.relics.glitchy_illusion": "오류 환영",
    "effect.relics.anti_heal": "재생 방지",
    "effect.relics.tremor": "진동",
    "relics.description.reflective_necklace.ability.reflection.description": (
        "유물 착용자가 피해를 받으면 %1$s%% 확률로 받은 피해의 %2$s%%를 저장한 구체를 "
        "만듭니다. 착용자가 공격하면 16블록 안의 구체가 차례로 공격 대상으로 날아갑니다. "
        "구체는 경로의 대상에게 저장한 피해를 주고 사라지며, 단단한 블록에 부딪히거나 "
        "생성 후 %3$s초 안에 대상을 찾지 못해도 사라집니다."
    ),
    "relics.description.jellyfish_necklace.ability.shock.enabled.description": (
        "%1$s초마다 전기 아크를 1회 충전하며 최대 %2$s회까지 저장합니다. 착용자가 생명체와 "
        "접촉하면 충전 1회를 소모해 %3$s블록 안의 대상을 %4$s%%의 힘으로 밀치고 %5$s초 "
        "동안 마비시킵니다. 이어서 전기 사슬이 %6$s블록 안의 대상 사이를 최대 %7$s회 "
        "튕기며 경로의 모든 대상에게 %8$s 피해를 줍니다."
    ),
    "relics.description.kinetic_belt.ability.gliding.rank_modifier.strike": (
        "능력을 사용하는 동안 유물 착용자가 주는 발사체 피해가 %2$s%% 증가합니다."
    ),
    "relics.description.kinetic_belt.ability.gliding.rank_modifier.resistance": (
        "능력을 사용하는 동안 유물 착용자가 받는 피해가 %3$s%% 감소합니다."
    ),
    "relics.description.midnight_mantle.ability.phase.new_moon.description": (
        "유물 착용자의 최대 체력이 %3$s%%, 체력 회복량이 %4$s%% 증가합니다. 보너스는 "
        "현재 달의 위상이 신월에 가까울수록 강해집니다."
    ),
    "relics.description.midnight_mantle.ability.invisibility.description": (
        "밝기가 %1$s%%보다 낮으면 유물 착용자를 그림자로 감싸 투명하게 만듭니다. 그림자 "
        "밖으로 나오면 %2$s초 동안 다시 발동하지 않으며, 16블록 안의 모든 대상이 착용자를 "
        "인식하지 못해야 다시 발동할 수 있습니다."
    ),
    "relics.description.chorus_staff.ability.blink.description": (
        "사용하면 내부에 저장된 %2$s회 중 1회를 소모해 유물 소지자를 앞쪽으로 최대 "
        "%1$s블록 순간이동시킵니다. 저장 횟수는 %3$s초마다 1회씩 자동 회복됩니다."
    ),
    "relics.description.rider_flute.ability.stable.description": (
        "길들인 탈것을 오른쪽 클릭해 피리 안에 넣습니다. 다시 오른쪽 클릭하면 꺼내며, "
        "또 클릭하면 피리로 되돌릴 수 있습니다. 완전히 해제하려면 웅크린 채 오른쪽 "
        "클릭하세요. 피리는 탈것을 최대 %1$s마리 저장하며, 웅크린 채 마우스 휠을 돌려 "
        "선택할 탈것을 바꿉니다."
    ),
    "relics.description.rider_flute.ability.stable.rank_modifier.regeneration": (
        "피리 안의 모든 탈것이 초당 %2$s 체력을 회복합니다."
    ),
    "relics.description.rider_flute.ability.stable.rank_modifier.resistance": (
        "피리에서 소환한 탈것을 타는 동안 소지자와 탈것이 받는 피해가 %3$s%% 감소합니다."
    ),
    "relics.description.clot_of_time.ability.rewind.description": (
        "오른쪽 버튼을 누르는 동안 최근 이동 경로를 따라 최대 %1$s초 전까지 부드럽게 "
        "되돌아갑니다. 되감기가 끝나면 끊지 않고 사용한 시간만큼 재사용 대기시간이 적용됩니다."
    ),
    "effect.relics.glitch": "오류",
}

RELIQUIFIED_DESCRIPTIONS = {
    "umbrella": (
        "겉보기에는 낡은 천과 삐걱거리는 살대를 지닌 평범한 여행용 우산입니다. 하지만 "
        "바람이 차양을 채우는 순간 공기가 주인에게 복종하여, 보이지 않는 계단을 밟듯 "
        "천천히 낙하하며 기류를 따라 활공하게 합니다."
    ),
    "snorkel": (
        "소금기에 검게 바랜 호흡관입니다. 좁은 관이 믿기 어려울 만큼 깊은 곳까지 공기를 "
        "전해 주어, 마지막 숨을 걱정하지 않고 더 오래 물속에 머물게 합니다."
    ),
    "plastic_drinking_hat": (
        "굽은 관 두 개가 달린 엉뚱한 모자입니다. 원래는 시끌벅적한 파티를 위해 만들어졌지만, "
        "전투와 이동을 멈추지 않고도 물약과 음료를 재빨리 마실 수 있어 모험에서 더 유용합니다."
    ),
    "novelty_drinking_hat": (
        "굽은 관 두 개가 달린 엉뚱한 모자입니다. 원래는 시끌벅적한 파티를 위해 만들어졌지만, "
        "전투와 이동을 멈추지 않고도 물약과 음료를 재빨리 마실 수 있어 모험에서 더 유용합니다."
    ),
    "night_vision_goggles": (
        "정교하게 연마한 렌즈를 단 무거운 고글입니다. 희미한 빛까지 모아 어둠 속 세상을 "
        "선명하게 드러내며, 숙련된 착용자에게는 어둠 자체를 아군으로 만들어 줍니다."
    ),
    "cowboy_hat": (
        "끝없는 평원을 누비던 기수의 낡은 챙 넓은 모자입니다. 햇빛과 긴 여정에 가죽이 "
        "검게 바랬으며, 이 모자를 쓴 기수가 탄 탈것은 더 빠르고 자신 있게 움직입니다."
    ),
    "villager_hat": (
        "단정한 리본을 두른 소박한 밀짚모자로, 마을의 신뢰를 얻었다는 표식입니다. 주민과 "
        "쉽게 거래하고 철 골렘의 보호를 받게 해 줍니다."
    ),
    "anglers_hat": (
        "소금기와 바람에 닳은 낚시꾼의 모자입니다. 오래 기다릴 줄 아는 숙련된 낚시꾼이 "
        "쓰면 어획량이 풍성해지고, 때로는 평범한 물고기보다 귀한 보물도 낚아 올립니다."
    ),
    "lucky_scarf": (
        "돌가루와 긴 지하 생활에 빛이 바랜 탐광자의 스카프입니다. 실 한 올 한 올이 광석에서 "
        "행운을 끌어내어, 메마른 광맥에서도 더 풍성한 산물을 얻게 합니다."
    ),
    "charm_of_shrinking": (
        "세상이 일그러져 비치는 수정이 달린 작은 부적입니다. 주변 공간이 착용자의 몸을 "
        "다르게 받아들여 발소리와 낙하 충격을 줄이고 몸의 크기까지 바꾸게 합니다."
    ),
    "obsidian_skull": (
        "통흑요석을 깎아 만든 무거운 두개골입니다. 네더의 열기가 남아 있어 추위 속에서도 "
        "따뜻하며, 그 힘은 잠시나마 용암조차 치명적이지 않게 만듭니다."
    ),
    "superstitious_hat": (
        "레프러콘과 행운의 정령을 떠올리게 하는 밝고 낡은 모자입니다. 값진 전리품은 "
        "대담한 자를 따른다고 믿는 이들이 즐겨 씁니다."
    ),
    "scarf_of_invisibility": (
        "몸과 공기의 경계를 흐리는 특이한 천으로 짠 어두운 스카프입니다. 착용자가 가만히 "
        "서면 실이 떨리며 윤곽이 서서히 주변 풍경 속으로 사라집니다."
    ),
    "cross_necklace": (
        "순례자와 언데드 사냥꾼이 지니던 세월에 검게 바랜 십자가 부적입니다. 위기의 순간 "
        "피해 일부를 대신 받아, 마지막이 될 공격에서도 살아남을 짧은 틈을 줍니다."
    ),
    "panic_necklace": (
        "적의를 감지하듯 작은 수정이 떨리는 목걸이입니다. 주인을 노리는 시선이 많을수록 "
        "강하게 반응하여 심장을 뛰게 하고, 목숨을 구할 다급한 힘을 몸에 채웁니다."
    ),
    "shock_pendant": (
        "가는 전류가 끊임없이 번쩍이는 금 간 수정 펜던트입니다. 적의 공격을 받으면 에너지를 "
        "즉시 방출하여 대상 사이를 뛰어다니는 밝은 전기 사슬로 되갚습니다."
    ),
    "flame_pendant": (
        "꺼지지 않는 불꽃이 타오르는 수정 펜던트입니다. 대장간의 열기를 품고 있어 적의 "
        "공격을 받으면 불길을 터뜨려 뜨거운 반격으로 돌려줍니다."
    ),
    "thorn_pendant": (
        "진한 독이 흐르는 가느다란 에메랄드 가시가 감싼 펜던트입니다. 착용자가 공격받는 "
        "순간 가시가 반응하여 적에게 고통스러운 대가를 치르게 합니다."
    ),
    "charm_of_sinking": (
        "어두운 심해가 일렁이는 묵직한 푸른 돌의 부적입니다. 주인을 바닥으로 끌어당기지만, "
        "다른 이가 숨과 힘을 잃는 곳에서 오히려 물을 든든한 보호막으로 바꿉니다."
    ),
    "antidote_vessel": (
        "정화 입자가 맴도는 맑은 영약을 담은 작은 밀폐 용기입니다. 독과 저주가 완전히 "
        "퍼지기 전에 힘을 약화시켜 해로운 효과를 더 빨리 떨쳐 내게 합니다."
    ),
    "universal_attractor": (
        "주변에 조절 가능한 역장을 만드는 소형 장치입니다. 극성을 바꾸어 전리품과 여러 "
        "물체를 소지자에게 끌어오거나 반대로 밀어낼 수 있습니다."
    ),
    "crystal_heart": (
        "부드러운 진홍빛이 맥박치는 심장 모양의 수정입니다. 에너지가 주인의 생명력을 "
        "일시적으로 강화하여 몸이 견딜 수 있는 한계를 넓힙니다."
    ),
    "cloud_in_a_bottle": (
        "작은 구름이 느긋하게 맴도는 투명한 병입니다. 공중을 박차면 갇힌 기류가 몸을 "
        "들어 올려, 발밑에 땅이 없어도 보이지 않는 발판을 딛듯 계속 움직이게 합니다."
    ),
    "helium_flamingo": (
        "가벼운 기체와 발명가의 엉뚱한 발상으로 채운 밝은 풍선 플라밍고입니다. 소지자가 "
        "점프하면 몸을 띄워 하늘을 잔잔한 물처럼 헤엄치게 합니다."
    ),
    "running_shoes": (
        "속도에 의지하는 이를 위해 만든 가벼운 러닝화입니다. 움직임을 붙잡아 가속으로 "
        "바꾸므로 오래 달릴수록 발걸음이 빨라지고 관성까지 힘을 보탭니다."
    ),
    "snowshoes": (
        "체중을 넓게 퍼뜨려 눈밭을 단단한 길처럼 만드는 설피입니다. 평범한 신발이라면 "
        "푹 빠질 눈더미에서도 힘들이지 않고 일정한 속도로 움직이게 합니다."
    ),
    "steadfast_spikes": (
        "걸음마다 바닥을 단단히 무는 튼튼한 스파이크입니다. 보통 신발이 미끄러질 매끄러운 "
        "얼음 위에서도 접지력과 균형을 유지하게 합니다."
    ),
    "flippers": (
        "물속에서 빠르게 움직이도록 만든 유연한 오리발입니다. 헤엄칠 때마다 추진력을 "
        "높여 더 빠르고 민첩하게 물을 가르게 합니다."
    ),
    "rooted_boots": (
        "밑창에 살아 있는 뿌리망을 엮은 장화입니다. 잔디를 밟으면 뿌리가 잠시 땅속으로 "
        "뻗어 대지에서 영양분을 끌어옵니다."
    ),
    "aqua_dashers": (
        "밑창 아래에 탄력 있는 물 발판을 만드는 가벼운 러닝화입니다. 걸음마다 수면이 "
        "잠시 단단해져 길처럼 달릴 수 있고, 느린 첫걸음 뒤에는 금세 제 속도를 되찾습니다."
    ),
    "strider_shoes": (
        "녹은 돌의 열기도 견디는 신발입니다. 걸음마다 발밑의 용암이 잠시 굳어 수면처럼 "
        "달릴 수 있고, 느린 첫걸음 뒤에는 금세 평소 속도를 되찾습니다."
    ),
    "whoopee_cushion": (
        "작은 가스 장치를 숨긴 장난용 방석입니다. 주인이 어설프게 앉는 순간 큰 소리와 "
        "함께 강한 바람을 내뿜습니다. 우스운 장난처럼 보여도 생각보다 훨씬 강력합니다."
    ),
    "vampiric_glove": (
        "공격할 때마다 붉은 핏줄이 빛나는 어두운 장갑입니다. 상처 입은 적의 생명력을 "
        "빼앗아 주인에게 돌려주며, 전투가 치열할수록 훔친 에너지로 가득 찹니다."
    ),
    "golden_hook": (
        "전리품뿐 아니라 경험치 한 조각까지 챙기는 이를 위한 금빛 갈고리입니다. 쓰러진 "
        "적의 에너지를 끌어당겨 경험치 구체가 더 빨리 주인을 찾고 더 큰 힘을 주게 합니다."
    ),
    "onion_ring": (
        "매운 양파 냄새가 나는 팔찌로, 포만감과 곡괭이질의 힘을 기묘하게 이어 줍니다. "
        "배가 든든한 동안 몸이 더 빠르고 지치지 않아 돌과 광석을 쉬지 않고 캡니다."
    ),
    "digging_claws": (
        "돌과 흙을 빠르게 파헤치도록 강화한 발톱입니다. 날이 바위를 놀라울 만큼 쉽게 "
        "파고들어 블록을 거침없이 뚫고 나가게 합니다."
    ),
    "power_glove": (
        "공격 사이에 에너지를 모았다가 드물지만 파괴적인 힘으로 방출하는 무거운 전투 "
        "장갑입니다. 충전이 절정에 이르면 상상하기 어려운 위력으로 적을 내리칩니다."
    ),
    "withered_bracelet": (
        "시듦의 에너지를 머금은 어두운 팔찌입니다. 차가운 빛이 마른 열기를 남기며, "
        "착용자의 공격은 적에게 파괴적인 부패를 옮길 수 있습니다."
    ),
    "warp_drive": (
        "엔더 진주의 에너지와 동기화된 소형 워프 장치입니다. 순간이동이 일어나는 순간을 "
        "가로채 안정시켜 더 안전하고 효율적으로 이동하게 합니다."
    ),
    "kitty_slippers": (
        "고양이 얼굴이 달린 부드러운 슬리퍼로, 이상하지만 설득력 있는 포식자의 기운을 "
        "냅니다. 몬스터가 거리를 두게 하고 조용하고 가볍게 움직이게 하며, 고양이처럼 "
        "여러 번의 삶을 지닌 듯 주인에게 또 한 번의 기회를 주기도 합니다."
    ),
    "bunny_hoppers": (
        "탄력 있는 밑창을 단 토끼 모양 슬리퍼입니다. 한 번 뛰면 착용자를 높이 쏘아 올려 "
        "긴 수직 도약으로 바꾸므로 빠른 전투와 기습적인 공중 공격에 알맞습니다."
    ),
    "feral_claws": (
        "끊임없이 몰아붙이는 공격을 위한 포식자의 발톱입니다. 정확한 타격마다 사냥 본능을 "
        "깨워 움직임을 빠르게 하고 연속 공격을 점점 거센 전투 광란으로 바꿉니다."
    ),
    "pocket_piston": (
        "전투 장갑에 내장된 소형 피스톤 장치입니다. 움직일 때마다 숨은 충격을 뿜어 "
        "평소보다 멀리 손을 뻗고 주변 공간을 확실하게 제어하게 합니다."
    ),
    "fire_gauntlet": (
        "공격할 때마다 달아오르는 심지가 든 전투 건틀릿입니다. 닿은 적에게 불길을 남겨 "
        "긴 전투일수록 전장을 검게 그을린 황무지로 바꿉니다."
    ),
    "pickaxe_heater": (
        "곡괭이에 직접 장착한 소형 가열 장치입니다. 채굴한 광석을 즉시 가열하여 때로는 "
        "캐내는 순간 완성된 주괴로 바꿉니다."
    ),
    "chorus_totem": (
        "주인을 긴급 구조하도록 조율된 코러스 에너지 토템입니다. 치명적인 공격을 받는 순간 "
        "작동하여 소지자를 위험에서 떼어 내고 가장 가까운 안전한 곳으로 옮깁니다."
    ),
    "everlasting_beef": (
        "아무리 먹어도 시간이 지나면 다시 차오르는 신비한 생고기입니다. 베어 문 자국이 "
        "서서히 사라져 주인이 작은 식사를 거듭 즐기게 합니다."
    ),
    "eternal_steak": (
        "아무리 먹어도 시간이 지나면 다시 차오르는 신비한 스테이크입니다. 베어 문 자국이 "
        "서서히 사라져 주인이 작은 식사를 거듭 즐기게 합니다."
    ),
}

RELIQUIFIED_ABILITY_NAMES = {
    "Canopy Shield": "차양 방패",
    "Night Vision": "야간 투시",
    "Master's Saddle": "명인의 안장",
    "Golem Guard": "골렘 수호",
    "Lucky Catch": "행운의 어획",
    "Lucky Vein": "행운의 광맥",
    "Chest Mastery": "상자 숙련",
    "Lava Resilience": "용암 내성",
    "Superstitious Trophy": "미신의 전리품",
    "Vanishing": "은폐",
    "Electric Chain": "전기 사슬",
    "Poisoned Thorns": "독 가시",
    "Crystal Reserve": "수정 비축",
    "Air Jump": "공중 점프",
    "Aerial Swimming": "공중 유영",
    "Snowstride": "눈길 걸음",
    "Steadfastness": "굳건함",
    "Wall Slide": "벽 미끄러지기",
    "Swift Swim": "재빠른 수영",
    "Root Nourishment": "뿌리 영양",
    "Water Run": "수면 질주",
    "Lava Stride": "용암 걸음",
    "Gas Burst": "가스 분출",
    "Blooddrinker": "흡혈",
    "Hungry Drill": "굶주린 굴착",
    "Digger": "굴착자",
    "Power Strike": "강타",
    "Withering": "시듦",
    "Transgression": "공간 도약",
    "Nine Lives": "아홉 목숨",
    "Predatory Frenzy": "포식자의 광란",
    "Piston Impulse": "피스톤 충격",
    "Scorching Flame": "작열하는 불꽃",
    "Thermal Processing": "열 가공",
    "Chorus Bloom": "코러스 개화",
    "Endless Meal": "무한한 식사",
}

RELIQUIFIED_GLOBAL_REPLACEMENTS = {
    "유물 보관함": "유물 소지자",
    "유물 홀더": "유물 소지자",
    "유물 보유자": "유물 소지자",
    "홀더": "소지자",
    "RMB": "오른쪽 버튼",
    "LMB": "왼쪽 버튼",
    "배고픔": "허기",
    "건강": "체력",
    "데미지": "피해",
    "트리거": "발동",
    "음주": "음료 섭취",
    "술을 마시면": "음료를 마시면",
    "술로": "음료로",
    "술을 마시며": "음료를 마시며",
    "소멸 효과": "은폐 효과",
    "크리스탈": "수정",
    "스파크": "불꽃",
    "유물 소지자이": "유물 소지자가",
    "유물 소지자을": "유물 소지자를",
    "허기과": "허기와",
    "대상쪽": "대상 쪽",
    "위더": "시듦",
    "파워 스트라이크": "강타",
    "포화도": "포만도",
    "배니싱": "은폐",
    "소멸이": "은폐가",
}

RELIQUIFIED_EXACT = {
    "tooltip.reliquified_artifacts.modified": "Reliquified Artifacts에서 변경됨",
    "tooltip.reliquified_artifacts.mimi_dust": (
        "상자에 사용하면 미믹으로 바꾸며, 변환 전 상자에 있던 아이템 수만큼 무작위 "
        "유물을 떨어뜨립니다."
    ),
    "item.reliquified_artifacts.mimi_dust": "미미 가루",
    "relics.description.umbrella.ability.glider.description": (
        "우산을 손에 들고 있으면 소지자의 낙하 속도가 %4$s로 제한됩니다."
    ),
    "relics.description.umbrella.ability.glider.rank_modifier.bounce": (
        "우산을 들고 낙하할 때 왼쪽 버튼을 누르면 바라보는 반대 방향으로 %2$s의 힘으로 "
        "튀어 오르며, %1$s회 충전 중 1회를 소모합니다. 땅에 닿으면 충전이 모두 회복됩니다."
    ),
    "relics.description.umbrella.ability.glider.statistic.bounces_done": "튀어 오른 횟수",
    "relics.description.umbrella.ability.glider.statistic.flight_duration": (
        "감속 낙하 시간"
    ),
    "relics.description.umbrella.ability.shield.description": (
        "오른쪽 버튼을 누르면 우산을 온전한 방패로 사용합니다. 연속 공격을 최대 %1$s회 "
        "막은 뒤 %3$s초 동안 재사용 대기시간이 적용됩니다."
    ),
    "relics.description.umbrella.ability.shield.statistic.blocked_hits": "막은 공격",
    "relics.description.snorkel.ability.snorkeling.description": (
        "소지자와 공기 사이의 물이 %1$s블록 이하라면 수중에서 숨 쉴 수 있습니다."
    ),
    "relics.description.snorkel.ability.snorkeling.statistic.drowning_damage_reduced": (
        "감소시킨 익사 피해"
    ),
    "relics.description.plastic_drinking_hat.ability.drinking.statistic.air_restored": (
        "음료로 회복한 공기 방울"
    ),
    "relics.description.plastic_drinking_hat.ability.drinking.statistic.consumed_duration": (
        "음료를 마신 시간"
    ),
    "relics.description.plastic_drinking_hat.ability.drinking.statistic.health_restored": (
        "음료로 회복한 체력"
    ),
    "relics.description.plastic_drinking_hat.ability.drinking.statistic.hunger_restored": (
        "음료로 회복한 허기"
    ),
    "relics.description.novelty_drinking_hat.ability.drinking.statistic.air_restored": (
        "음료로 회복한 공기 방울"
    ),
    "relics.description.novelty_drinking_hat.ability.drinking.statistic.consumed_duration": (
        "음료를 마신 시간"
    ),
    "relics.description.novelty_drinking_hat.ability.drinking.statistic.health_restored": (
        "음료로 회복한 체력"
    ),
    "relics.description.novelty_drinking_hat.ability.drinking.statistic.hunger_restored": (
        "음료로 회복한 허기"
    ),
    "relics.description.night_vision_goggles.ability.vision.rank_modifier.evasion": (
        "어둠 속에서 공격자가 소지자를 빗맞힐 확률이 최대 %2$s%%가 됩니다. 주변이 "
        "어두울수록 확률이 높아져 완전한 어둠에서 최대치에 도달합니다."
    ),
    "relics.description.night_vision_goggles.ability.vision.statistic.evasion_damage_avoided": (
        "어둠 속 회피로 피한 피해"
    ),
    "relics.description.cowboy_hat.ability.riding.statistic.mounted_distance": (
        "탈것을 타고 이동한 거리"
    ),
    "relics.description.villager_hat.ability.golem_guard": "골렘 수호",
    "relics.description.villager_hat.ability.golem_guard.description": (
        "철 골렘이 유물 소지자를 공격하지 않고 소지자를 지킵니다."
    ),
    "relics.description.villager_hat.ability.trade_surge.statistic.multicast_bonus_results": (
        "추가로 받은 거래 결과"
    ),
    "relics.description.villager_hat.ability.trade_surge.statistic.trades_preserved": (
        "보존된 거래 재고"
    ),
    "relics.description.anglers_hat.ability.catch.description": (
        "낚시에 성공하면 %1$s%% 확률로 어획량이 최대 %4$s배가 됩니다."
    ),
    "relics.description.anglers_hat.ability.catch.rank_modifier.quick_bite": (
        "물고기를 2배 빠르게 먹습니다."
    ),
    "relics.description.lucky_scarf.ability.fortune.description": (
        "광석과 행운이 적용되는 블록을 캘 때 %1$s%% 확률로 추가 행운 레벨을 적용하며, "
        "한 블록에서 최대 %2$s회 발동합니다."
    ),
    "relics.description.lucky_scarf.ability.fortune.statistic.bonus_fortune_procs": (
        "추가 행운 발동 횟수"
    ),
    "relics.description.charm_of_shrinking.ability.size.mode.grow": "확대",
    "relics.description.charm_of_shrinking.ability.size.mode.shrink": "축소",
    "relics.description.charm_of_shrinking.ability.size.mode.stabilize": "고정",
    "relics.description.obsidian_skull.ability.lava.statistic.safe_falls": (
        "1등급부터 용암으로 안전하게 착지한 횟수"
    ),
    "relics.description.scarf_of_invisibility.ability.invisibility.rank_modifier.regeneration": (
        "은폐가 활성화된 동안 소지자가 초당 %5$s 체력을 회복합니다."
    ),
    "relics.description.scarf_of_invisibility.ability.invisibility.rank_modifier.strike": (
        "은폐가 끝난 뒤 첫 공격이 %3$s%% 더 큰 피해를 줍니다."
    ),
    "relics.description.scarf_of_invisibility.ability.invisibility.rank_modifier.stun": (
        "은폐가 끝난 뒤 첫 공격이 대상을 %4$s초 동안 기절시킵니다."
    ),
    "relics.description.cross_necklace.ability.protection.rank_modifier.holy_fire": (
        "소지자를 공격한 언데드에게 %2$s초 동안 불을 붙입니다."
    ),
    "relics.description.panic_necklace.ability.panic.statistic.healing_restored": (
        "시야 안의 대상이 죽을 때 회복한 체력"
    ),
    "relics.description.shock_pendant.ability.shock.description": (
        "피해를 입으면 %1$s%% 확률로 전기 불꽃을 방출합니다. 불꽃은 %2$s블록 안의 "
        "대상 사이를 최대 %3$s회 튕기며 각각 %4$s 피해를 줍니다."
    ),
    "relics.description.shock_pendant.ability.shock.rank_modifier.tremor": (
        "소지자가 피해를 입으면 %6$s%% 확률로 공격자에게 %7$s초 동안 진동 효과를 줍니다."
    ),
    "relics.description.thorn_pendant.ability.poison.description": (
        "소지자가 받은 피해의 %1$s%%를 공격자에게 되돌려 줍니다."
    ),
    "relics.description.flame_pendant.ability.fire.statistic.burning_bonus_damage": (
        "불타는 대상에게 준 추가 피해"
    ),
    "relics.description.thorn_pendant.ability.poison.statistic.poisoned_bonus_damage": (
        "중독된 대상에게 준 추가 피해"
    ),
    "relics.description.charm_of_sinking.ability.sinking.statistic.air_bubbles_restored": (
        "회복한 공기 방울"
    ),
    "relics.description.charm_of_sinking.ability.sinking.statistic.damage_reduced": (
        "머리 위 물 블록으로 감소시킨 피해"
    ),
    "relics.description.antidote_vessel.ability.antidote.rank_modifier.resilience": (
        "활성화된 부정적 효과 하나당 유물 소지자가 받는 피해가 %2$s%% 감소합니다."
    ),
    "relics.description.antidote_vessel.ability.antidote.statistic.damage_reduced": (
        "부정적 효과 수에 따라 감소시킨 피해"
    ),
    "relics.description.antidote_vessel.ability.antidote.statistic.reduced_effect_duration": (
        "줄어든 부정적 효과의 총 지속 시간"
    ),
    "relics.description.universal_attractor.ability.magnetism.mode.pull": "당기기",
    "relics.description.universal_attractor.ability.magnetism.mode.push": "밀어내기",
    "relics.description.universal_attractor.ability.magnetism.rank_modifier.experience": (
        "당기기 모드에서는 경험치 구체도 끌어옵니다."
    ),
    "relics.description.universal_attractor.ability.magnetism.rank_modifier.projectiles": (
        "밀어내기 모드에서는 적대적 발사체도 밀어냅니다."
    ),
    "relics.description.universal_attractor.ability.magnetism.rank_modifier.teleport": (
        "당기기 모드에서 아이템이 천천히 이동하지 않고 소지자에게 즉시 순간이동합니다."
    ),
    "relics.description.universal_attractor.ability.magnetism.statistic.repelled_projectiles": (
        "밀어낸 적대적 발사체"
    ),
    "relics.description.crystal_heart.ability.heart.statistic.immortality_triggers": (
        "받은 불멸 효과"
    ),
    "relics.description.cloud_in_a_bottle.ability.jump.statistic.slow_fall_duration": (
        "감속 낙하 시간"
    ),
    "relics.description.cloud_in_a_bottle.ability.jump.statistic.combat_recovery_bonus_damage": (
        "회복된 추가 점프로 준 추가 피해"
    ),
    "relics.description.helium_flamingo.ability.flying.rank_modifier.aerial_guard": (
        "공중에 떠 있는 동안 유물 소지자가 받는 피해가 %4$s%% 감소합니다."
    ),
    "relics.description.helium_flamingo.ability.flying.rank_modifier.efficient_hover": (
        "유물 소지자가 거의 움직이지 않으면 체공 시간이 소모되지 않습니다."
    ),
    "relics.description.helium_flamingo.ability.flying.statistic.aerial_archery_bonus_damage": (
        "체공 중 원거리 공격으로 준 추가 피해"
    ),
    "relics.description.steadfast_spikes.ability.resistance.description": (
        "밀치기와 미끄러운 표면에 대한 저항이 %1$s%% 증가합니다."
    ),
    "relics.description.steadfast_spikes.ability.resistance.rank_modifier.anchor": (
        "유물 소지자가 가만히 서 있으면 외부 힘으로 움직이지 않습니다."
    ),
    "relics.description.flippers.ability.swim.rank_modifier.breathing": (
        "유물 소지자가 물속에 있으면 공기 방울이 %2$s%% 더 느리게 소모됩니다."
    ),
    "relics.description.rooted_boots.ability.devouring.description": (
        "유물 소지자 아래의 잔디 블록을 흙으로 바꾸고 허기 %1$s와 포만도 %2$s를 "
        "회복합니다. 발동 후 %3$s초 동안 재사용 대기시간이 적용됩니다."
    ),
    "relics.description.rooted_boots.ability.devouring.statistic.healing_done": (
        "회복한 체력"
    ),
    "relics.description.aqua_dashers.ability.water_dash.statistic.projectiles_ignored": (
        "수면을 달리는 동안 통과한 발사체"
    ),
    "relics.description.strider_shoes.ability.lava_stride.rank_modifier.free_stride": (
        "웅크리지 않아도 용암 표면을 이동할 수 있습니다."
    ),
    "relics.description.whoopee_cushion.ability.push.rank_modifier.toxic_cloud": (
        "능력이 발동하면 %6$s%% 확률로 가스 구름이 남습니다. 구름은 대상을 중독시키고 "
        "메스꺼움을 주며, 안의 생물이 유물 소지자를 인식하지 못하게 합니다."
    ),
    "relics.description.vampiric_glove.ability.vampire.rank_modifier.overheal_absorption": (
        "최대 체력을 넘는 초과 회복량은 최대 %6$s까지 흡수 체력으로 바뀝니다."
    ),
    "relics.description.golden_hook.ability.hook.rank_modifier.crowd_pull": (
        "대상을 공격하면 %3$s블록 안의 주변 생물을 대상 쪽으로 조금 끌어당깁니다."
    ),
    "relics.description.onion_ring.ability.hunger_mining.rank_modifier.sustenance": (
        "블록을 파괴하면 %4$s%% 확률로 허기 1을 회복합니다."
    ),
    "relics.description.power_glove.ability.power.description": (
        "%1$s번째 공격마다 %2$s%% 더 큰 피해를 줍니다."
    ),
    "relics.description.power_glove.ability.power.statistic.shields_broken": (
        "파괴한 방패"
    ),
    "relics.description.warp_drive.ability.warp.rank_modifier.disorientation": (
        "순간이동 후 %2$s블록 안의 모든 대상을 %3$s초 동안 실명시키고, 유물 소지자를 "
        "인식하지 못하게 합니다."
    ),
    "relics.description.warp_drive.ability.warp.rank_modifier.protection": (
        "엔더 진주로 순간이동할 때 유물 소지자가 더 이상 피해를 받지 않습니다."
    ),
    "relics.description.kitty_slippers.ability.feline_aura.description": (
        "%1$s블록 안의 크리퍼와 팬텀이 고양이를 만난 것처럼 유물 소지자를 피합니다."
    ),
    "relics.description.bunny_hoppers.ability.jump.statistic.impact_bonus_damage": (
        "높이 뛴 뒤 낙하하며 준 추가 피해"
    ),
    "relics.description.pocket_piston.ability.piston.statistic.extended_damage_dealt": (
        "늘어난 사거리에서 준 피해"
    ),
    "relics.description.pickaxe_heater.ability.heating.statistic.molten_luck_levels": (
        "추가 행운 레벨 발동 횟수"
    ),
    "relics.description.chorus_totem.ability.chorus.rank_modifier.disorient": (
        "순간이동 전 발동 지점에서 %4$s블록 안의 모든 대상을 %5$s초 동안 실명시키고, "
        "유물 소지자를 인식하지 못하게 합니다."
    ),
    "relics.description.everlasting_beef.ability.meal.description": (
        "음식으로 먹을 때마다 내구도 1을 소모합니다. 내구도가 없으면 먹을 수 없고 "
        "%1$s초마다 1씩 회복합니다. 최대 내구도: %5$s."
    ),
    "relics.description.eternal_steak.ability.meal.description": (
        "음식으로 먹을 때마다 내구도 1을 소모합니다. 내구도가 없으면 먹을 수 없고 "
        "%1$s초마다 1씩 회복합니다. 최대 내구도: %5$s."
    ),
    "relics.description.everlasting_beef.ability.meal.statistic.healed": (
        "섭취로 회복한 체력"
    ),
    "relics.description.eternal_steak.ability.meal.statistic.healed": (
        "섭취로 회복한 체력"
    ),
    "relics.description.cowboy_hat.ability.riding.rank_modifier.mounted_absorption": (
        "탈것을 타는 동안 소지자가 %3$s의 흡수 체력을 얻습니다."
    ),
    "relics.description.flippers.ability.swim.experience_source.evasion_miss": (
        "물속에서 소지자를 빗맞힌 공격 하나당 경험치 +1"
    ),
    "relics.description.kitty_slippers.ability.nine_lives.experience_source.evasion_miss": (
        "소지자를 빗맞힌 공격 하나당 경험치 +1"
    ),
    "relics.description.kitty_slippers.ability.nine_lives.statistic.evasion_misses": (
        "소지자를 빗맞힌 공격"
    ),
    "relics.description.everlasting_beef.ability.meal.rank_modifier.preservation": (
        "%3$s%% 확률로 먹어도 내구도를 소모하지 않습니다."
    ),
    "relics.description.everlasting_beef.ability.meal.rank_modifier.quick_meal": (
        "%4$s%% 더 빠르게 먹습니다."
    ),
    "relics.description.everlasting_beef.ability.meal.rank_modifier.restoration": (
        "먹으면 체력을 %2$s 추가로 회복합니다."
    ),
    "relics.description.eternal_steak.ability.meal.rank_modifier.preservation": (
        "%3$s%% 확률로 먹어도 내구도를 소모하지 않습니다."
    ),
    "relics.description.eternal_steak.ability.meal.rank_modifier.quick_meal": (
        "%4$s%% 더 빠르게 먹습니다."
    ),
    "relics.description.eternal_steak.ability.meal.rank_modifier.restoration": (
        "먹으면 체력을 %2$s 추가로 회복합니다."
    ),
}


def translate_artifacts(english: dict[str, object], korean: dict[str, object]) -> None:
    """Artifacts JAR 후보를 전수 대조한 확정 용어로 교정한다."""
    old_names = {
        slug: korean.get(f"item.artifacts.{slug}") for slug in ARTIFACT_ITEM_NAMES
    }
    for slug, name in ARTIFACT_ITEM_NAMES.items():
        item_key = f"item.artifacts.{slug}"
        if item_key in korean:
            korean[item_key] = name
        prefix = f"artifacts.config.items.{slug}."
        old_name = old_names[slug]
        if not isinstance(old_name, str) or old_name == name:
            continue
        for key, value in korean.items():
            if key.startswith(prefix) and isinstance(value, str):
                korean[key] = value.replace(old_name, name)
    for key, value in english.items():
        if key.endswith(".title") and isinstance(value, str):
            translated = ARTIFACT_TITLE_TRANSLATIONS.get(value)
            if translated is not None:
                korean[key] = translated
    korean.update(
        {key: value for key, value in ARTIFACT_EXACT.items() if key in korean}
    )


def translate_relics(english: dict[str, object], korean: dict[str, object]) -> None:
    """Relics 초안의 공통 용어와 확정 아이템 이름을 교정한다."""
    for key, value in korean.items():
        if not isinstance(value, str):
            continue
        for before, after in RELIC_GLOBAL_REPLACEMENTS.items():
            value = value.replace(before, after)
        korean[key] = value
        if key.endswith(".mode.enabled"):
            korean[key] = "활성화"
        elif key.endswith(".mode.disabled"):
            korean[key] = "비활성화"
    for slug, name in RELIC_ITEM_NAMES.items():
        key = f"item.relics.{slug}"
        if key in korean:
            korean[key] = name
    korean.update({key: value for key, value in RELIC_EXACT.items() if key in korean})


def translate_reliquified_artifacts(
    english: dict[str, object], korean: dict[str, object]
) -> None:
    """Reliquified Artifacts 초안의 성장 문구와 확정 용어를 교정한다."""
    for key, value in korean.items():
        if not isinstance(value, str):
            continue
        for before, after in RELIC_GLOBAL_REPLACEMENTS.items():
            value = value.replace(before, after)
        for before, after in RELIQUIFIED_GLOBAL_REPLACEMENTS.items():
            value = value.replace(before, after)
        korean[key] = value
        if key.endswith(".mode.enabled"):
            korean[key] = "활성화"
        elif key.endswith(".mode.disabled"):
            korean[key] = "비활성화"
        parts = key.split(".")
        if len(parts) == 5 and parts[3] in {"ability", "synergy"}:
            source = english.get(key)
            if isinstance(source, str) and source in RELIQUIFIED_ABILITY_NAMES:
                korean[key] = RELIQUIFIED_ABILITY_NAMES[source]
    for slug, description in RELIQUIFIED_DESCRIPTIONS.items():
        key = f"relics.description.{slug}.description"
        if key in korean:
            korean[key] = description
    korean.update(
        {key: value for key, value in RELIQUIFIED_EXACT.items() if key in korean}
    )


TRANSLATORS = {
    "artifacts": translate_artifacts,
    "relics": translate_relics,
    "reliquified_artifacts": translate_reliquified_artifacts,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", choices=BATCHES)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    if args.batch not in TRANSLATORS:
        parser.error(f"아직 번역 규칙이 준비되지 않은 배치입니다: {args.batch}")

    target = next(target for target in TARGETS if target.batch == args.batch)
    instance = resolve_source_root(args.instance)
    jar_path = find_jar(instance, target)
    with ZipFile(jar_path) as jar:
        english = load_json(jar, f"assets/{target.namespace}/lang/en_us.json")
    working_path = WORK_ROOT / target.namespace / "ko_kr.json"
    korean = json.loads(working_path.read_text(encoding="utf-8"))
    TRANSLATORS[args.batch](english, korean)
    working_path.write_text(
        json.dumps(korean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{args.batch}: {len(korean)}개 키 반영 완료")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
