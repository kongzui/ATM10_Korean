#!/usr/bin/env python3
"""The Twilight Forest 모드군의 신규 번역 후보와 직접 연동을 처리한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from zipfile import ZipFile

import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/twilight_forest"
BASE_ROOT = WORK_ROOT / "twilightforest"
CACHE_PATH = PROJECT_ROOT / "temp/twilight_forest_auto_candidates.json"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
GOOGLE_TRANSLATE = "https://translate.googleapis.com/translate_a/single"
PROTECTED = re.compile(
    r"https?://\S+"
    r"|%(?:\d+\$)?[a-zA-Z%]"
    r"|\{[A-Za-z0-9_]+\}"
    r"|\$\{[^}]+\}"
    r"|\$\([^)]*\)"
    r"|[&§][0-9A-FK-ORa-fk-or]"
    r"|<[^>]+>"
    r"|\\n"
    r"|\n"
    r"|\d+(?:[.,]\d+)*(?:[xX×]\d+)?"
)

FORMAT_FIXES = {
    "advancement.twilightforest.naga_armors.desc": "%s와 %s을(를) 제작하세요",
    "config.twilightforest.casket_uuid_locking.tooltip": (
        "참이면 플레이어가 사망할 때 생성된 유품 상자를 다른 플레이어가 열 수 "
        "없습니다. 다른 사람의 유품 상자에서 아이템을 가져가지 못하게 하려면 "
        "사용하세요.\n참고: 서버 운영자는 잠긴 상자를 열 수 있습니다."
    ),
    "config.twilightforest.origin_dimension.tooltip": (
        "항상 황혼의 숲으로 이동할 수 있고 되돌아오게 될 차원입니다. 기본값은 "
        "오버월드입니다. (domain:regname)."
    ),
    "config.twilightforest.disable_uncrafting.tooltip": (
        "역제작대의 역제작 기능을 비활성화합니다. 동작을 바꿔야 할 사항이 너무 많은 "
        "경우(또는 그냥 귀찮은 경우에도 괜찮아요) 마지막 수단으로 사용하는 것을 "
        "권장합니다.\n특수 역제작 제작법은 모드의 다른 기능에 필요하므로 비활성화되지 "
        "않습니다."
    ),
    "config.twilightforest.portal_permission.tooltip": (
        "지정된 권한 이상을 가진 플레이어가 차원문을 만들 수 있게 합니다. 바닐라 권한 "
        "시스템을 따릅니다.\n자세한 내용: https://minecraft.wiki/w/Permission_level"
    ),
    "config.twilightforest.ram_indicator.tooltip": (
        "양털을 든 채 퀘스팅 램을 바라보면, 그 색의 양털을 이미 먹였는지에 따라 조준점 "
        "위에 확인 표시 또는 X를 표시합니다."
    ),
    "enchantment.twilightforest.renewal.desc": (
        "소지자의 인벤토리에 재충전 아이템이 있으면 충전량을 모두 쓴 홀을 자동으로 "
        "재충전합니다."
    ),
    "magic_painting.twilightforest.music_in_the_mire.title": "늪의 음악",
    "twilightforest.book.lichtower.1": (
        "§8[괴물에게 갉아 먹힌 탐험가의 수첩]§0\n\n이 탑을 둘러싼 이상한 기운을 "
        "조사하기 시작했다. 탑의 벽돌은 지금까지 본 어떤 것보다 강한 저주로 "
        "보호받고 있다. 저주의 마법은 끓어오르며"
    ),
    "twilightforest.book.lichtower.3": (
        "§8[[많은 장을 넘긴 후에]]§0\n\n돌파구를 찾았어요! 여행 중 장식된 안뜰에서 "
        "뱀처럼 생긴 거대한 괴물을 목격했어요. 근처에서는 닳고 버려진 녹색 비늘을 "
        "주웠어요.\n\n비늘에 깃든 마법에는 제가 필요한 저주 해제"
    ),
    "twilightforest.book.lichtower.4": (
        "속성이 있지만, 마법이 너무 희미해요. 그 생물에게서 직접 더 신선한 표본을 "
        "얻어야 할지도 모르겠어요."
    ),
    "twilightforest.book.yeticave.1": (
        "§8[[서리로 뒤덮인 탐험가의 수첩]]§0\n\n이 눈 덮인 땅을 둘러싼 눈보라가 "
        "그치지 않고 있어요. 평범한 눈이 아니라 마법 현상이에요. 무엇이 이런 효과를"
    ),
    "twilightforest.book.yeticave.2": (
        "일으키는지 알아내려면 실험해야겠어요.\n\n§8[[다음 장]]§0\n\n이 저주는 한 "
        "존재가 혼자 만들기에는 너무 강력한 듯해요. 여러 마법사가 힘을 합쳐야 할 "
        "거예요. 그중 한 명이라도"
    ),
    "twilightforest.book.yeticave.3": (
        "힘을 보태지 않으면 눈보라가 잠잠해질 거예요. 이상하게도 점괘에는 근처에 살아 "
        "있는 마법사의 흔적이 나타나지 않아요. 하지만 근처의 뾰족한 지붕 탑 하나에서 "
        "흥미로운 것을 봤어요..."
    ),
    "twilightforest.tips.mushglooms": (
        "머시그룸은 뼛가루로 거대 버섯으로 키울 수 없습니다. 하지만 양질의 흙에 놓으면 "
        "자랍니다."
    ),
}

NEW_EXACT = {
    "advancement.twilightforest.chicken_jerky": "치킨 저키!",
    "advancement.twilightforest.craft_travellers_gear": "80일간의 숲 일주",
    "advancement.twilightforest.craft_travellers_gear.desc": "여행자 장비를 제작하세요",
    "advancement.twilightforest.modify_travellers_gear": "옷이 사람을 말해 준다",
    "advancement.twilightforest.modify_travellers_gear.desc": (
        "여행자 장비에 특성을 추가하세요"
    ),
    "block.twilightforest.blackberry_bush": "블랙베리 덤불",
    "block.twilightforest.blightberry_bush": "블라이트베리 덤불",
    "block.twilightforest.blueberry_bush": "블루베리 덤불",
    "block.twilightforest.copper_oreberry": "구리 오어베리 덤불",
    "block.twilightforest.dark_tower_miniature_structure": "소형 어둠의 탑",
    "block.twilightforest.duskberry_bush": "더스크베리 덤불",
    "block.twilightforest.essence_oreberry": "에센스 베리 덤불",
    "block.twilightforest.gold_oreberry": "금 오어베리 덤불",
    "block.twilightforest.iron_oreberry": "철 오어베리 덤불",
    "block.twilightforest.maloberry_bush": "말로베리 덤불",
    "block.twilightforest.minotaur_labyrinth_miniature_structure": (
        "소형 미노타우로스 미궁"
    ),
    "block.twilightforest.raspberry_bush": "라즈베리 덤불",
    "block.twilightforest.skyberry_bush": "스카이베리 덤불",
    "block.twilightforest.stingberry_bush": "스팅베리 덤불",
    "commands.tffeature.ability_modifier": (
        "여행자 장비에서는 능력을 추가하거나 제거할 수 없습니다"
    ),
    "commands.tffeature.added_modifier": "%s을(를) %s에 추가했습니다!",
    "commands.tffeature.biomepng.counts_header": (
        "%sx%s 영역 안의 대략적인 생물 군계 블록 수"
    ),
    "commands.tffeature.biomepng.progress": "%s%% 매핑 완료",
    "commands.tffeature.biomepng.save_failed": (
        "이미지를 저장하지 못했습니다! 이 문제를 신고해 주세요!"
    ),
    "commands.tffeature.biomepng.save_success": "이미지를 저장했습니다!",
    "commands.tffeature.display_pieces.missing_key": "누락된 키",
    "commands.tffeature.generator_radius.center_chunk": "구조물 시작점의 중앙 청크",
    "commands.tffeature.generator_radius.radius": "중앙 청크로부터 반경: %s",
    "commands.tffeature.has_modifier": "이 여행자 장비에는 이미 %s 특성이 있습니다",
    "commands.tffeature.info.wip": (
        "이 명령어는 아직 개발 중이므로 일부 기능이 올바르게 작동하지 않을 수 있습니다."
    ),
    "commands.tffeature.invalid_modifier": "%s은(는) 유효한 여행자 장비 특성이 아닙니다",
    "commands.tffeature.no_modifier": "이 여행자 장비에는 %s 특성이 적용되지 않았습니다",
    "commands.tffeature.not_travellers_gear": "여행자 장비를 들고 있지 않습니다",
    "commands.tffeature.removed_modifier": "%s을(를) %s에서 제거했습니다!",
    "commands.tffeature.teleport.dimension_missing": (
        "The Twilight Forest 차원을 사용할 수 없습니다."
    ),
    "commands.tffeature.teleport.player_only": "플레이어만 이 명령어를 실행할 수 있습니다.",
    "commands.tffeature.teleport.success": (
        "The Twilight Forest의 %s %s %s 위치로 순간이동했습니다"
    ),
    "commands.tffeature.too_many_modifiers": (
        "이 여행자 장비에는 이미 특성이 최대치로 적용되어 있습니다"
    ),
    "commands.tffeature.wrong_modifier_slot": (
        "이 여행자 장비에는 %s 특성을 적용할 수 없습니다"
    ),
    "config.jade.plugin_twilightforest.drying_rack": "건조대 시간",
    "config.twilightforest.aurora_biomes.button": "생물 군계 편집",
    "config.twilightforest.first_person_glove_overlay": "1인칭 장갑 표시",
    "config.twilightforest.first_person_glove_overlay.tooltip": (
        "1인칭 시점에서 여행자 장갑이 손에 표시되게 합니다."
    ),
    "config.twilightforest.giant_skin_uuid_list.button": "스킨 편집",
    "config.twilightforest.item_display": "아이템 표시 특성 설정",
    "config.twilightforest.item_display.tooltip": (
        "여행자 장비의 아이템 표시 특성을 사용할 때 각 요소가 표시되는 위치를 "
        "제어합니다."
    ),
    "config.twilightforest.manual_travellers_wings_gradual_glide": "수동 점진 활공",
    "config.twilightforest.manual_travellers_wings_gradual_glide.tooltip": (
        "이 옵션이 꺼져 있으면 느린 낙하가 기본이며, 웅크리기 키를 누르면 정상 "
        "속도로 떨어집니다. 옵션이 켜져 있으면 정상 낙하가 기본이며, 웅크리기 키를 "
        "누르면 느린 낙하가 활성화됩니다."
    ),
    "config.twilightforest.screen_offset_x": "표시 X 오프셋",
    "config.twilightforest.screen_offset_x.tooltip": (
        "화면의 모든 표시 특성에 적용할 시작 Y 오프셋을 정합니다."
    ),
    "config.twilightforest.screen_offset_y": "표시 Y 오프셋",
    "config.twilightforest.screen_offset_y.tooltip": (
        "화면의 모든 표시 특성에 적용할 시작 Y 오프셋을 정합니다."
    ),
    "config.twilightforest.screen_scale": "표시 배율",
    "config.twilightforest.screen_scale.tooltip": (
        "화면의 모든 표시 특성에 적용할 배율을 정합니다."
    ),
    "config.twilightforest.twenty_four_hour_format": "24시간 형식",
    "config.twilightforest.twenty_four_hour_format.tooltip": (
        "켜면 시계 업그레이드가 12시간 형식 대신 24시간 형식으로 시간을 표시합니다."
    ),
    "death.attack.twilightforest.oreberry": "%1$s이(가) 오어베리 덤불에 찔려 죽었습니다",
    "death.attack.twilightforest.oreberry.player": (
        "%1$s이(가) %2$s에게서 도망치다 오어베리 덤불에 찔려 죽었습니다"
    ),
    "death.attack.twilightforest.stale_sandwich": (
        "%1$s이(가) %2$s 때문에 묵은 샌드위치가 되었습니다"
    ),
    "gamerule.playersTfPortalCreativeDelay": (
        "크리에이티브 모드 플레이어의 The Twilight Forest 포털 대기 시간"
    ),
    "gamerule.playersTfPortalCreativeDelay.description": (
        "크리에이티브 모드 플레이어가 차원을 이동하기 전에 The Twilight Forest "
        "포털 안에 서 있어야 하는 시간(틱)입니다."
    ),
    "gamerule.playersTfPortalDefaultDelay": (
        "일반 모드 플레이어의 The Twilight Forest 포털 대기 시간"
    ),
    "gamerule.playersTfPortalDefaultDelay.description": (
        "크리에이티브 모드가 아닌 플레이어가 차원을 이동하기 전에 The Twilight "
        "Forest 포털 안에 서 있어야 하는 시간(틱)입니다."
    ),
    "gui.twilightforest.drying_jei": "건조대",
    "gui.twilightforest.drying_minute": "%s분",
    "gui.twilightforest.drying_minutes": "%s분",
    "gui.twilightforest.drying_second": "%s초",
    "gui.twilightforest.drying_seconds": "%s초",
    "gui.twilightforest.drying_ticks": "%s틱",
    "item.twilightforest.beef_jerky": "소고기 육포",
    "item.twilightforest.berry_medley": "모둠 베리",
    "item.twilightforest.blackberry": "블랙베리",
    "item.twilightforest.blightberry": "블라이트베리",
    "item.twilightforest.blueberry": "블루베리",
    "item.twilightforest.chicken_jerky": "닭고기 육포",
    "item.twilightforest.cod_jerky": "대구 육포",
    "item.twilightforest.copper_berry": "구리 오어베리",
    "item.twilightforest.copper_nugget": "구리 조각",
    "item.twilightforest.duskberry": "더스크베리",
    "item.twilightforest.essence_berry": "농축 에센스 베리",
    "item.twilightforest.fugu_jerky": "복어 육포",
    "item.twilightforest.gelatinous_maze_slime_drop": "젤라틴 미로 슬라임 방울",
    "item.twilightforest.gelatinous_slime_drop": "젤라틴 슬라임 방울",
    "item.twilightforest.gold_berry": "금 오어베리",
    "item.twilightforest.iron_berry": "철 오어베리",
    "item.twilightforest.maloberry": "말로베리",
    "item.twilightforest.maze_slime_ball": "미로 슬라임볼",
    "item.twilightforest.meef_jerky": "미프 육포",
    "item.twilightforest.monster_jerky": "몬스터 육포",
    "item.twilightforest.moss_soup": "이끼 수프",
    "item.twilightforest.mutton_jerky": "양고기 육포",
    "item.twilightforest.pork_jerky": "돼지고기 육포",
    "item.twilightforest.rabbit_jerky": "토끼고기 육포",
    "item.twilightforest.raspberry": "라즈베리",
    "item.twilightforest.salmon_jerky": "연어 육포",
    "item.twilightforest.shika_senbei": "사슴 센베이",
    "item.twilightforest.skyberry": "스카이베리",
    "item.twilightforest.stale_bread": "묵은 빵",
    "item.twilightforest.stingberry": "스팅베리",
    "item.twilightforest.tanned_leather": "무두질한 가죽",
    "item.twilightforest.tannin": "타닌",
    "item.twilightforest.travellers_belt": "여행자 허리띠",
    "item.twilightforest.travellers_boots": "여행자 장화",
    "item.twilightforest.travellers_gloves": "여행자 장갑",
    "item.twilightforest.travellers_gloves.desc": "장식용",
    "item.twilightforest.travellers_goggles": "여행자 고글",
    "item.twilightforest.travellers_vest": "여행자 조끼",
    "item.twilightforest.travellers_wings": "여행자 날개",
    "item.twilightforest.treated_leather": "처리된 가죽",
    "item.twilightforest.tropical_fish_jerky": "열대어 육포",
    "item.twilightforest.venison_jerky": "사슴고기 육포",
    "itemGroup.twilightforest.food": "The Twilight Forest: 음식",
    "jade.drying_rack.remaining": "%s 남음",
    "key.twilightforest.categories.travellers_gear": (
        "The Twilight Forest (여행자 장비)"
    ),
    "key.twilightforest.item_display_map_cycle": "아이템 표시에 저장된 지도 전환",
    "key.twilightforest.red_thread_vision": "고글로 붉은 실 보기",
    "key.twilightforest.swap_hotbar": "단축바 교체",
    "key.twilightforest.zoom": "고글로 확대/축소",
    "subtitles.twilightforest.block.drying_rack.add_item": "건조대에 아이템을 올림",
    "subtitles.twilightforest.block.drying_rack.remove_item": "건조대에서 아이템을 꺼냄",
    "subtitles.twilightforest.entity.deer.eat": "사슴이 먹음",
    "subtitles.twilightforest.item.travellers_gear.cycle_maps": "지도를 전환함",
    "subtitles.twilightforest.item.travellers_gear.cycle_maps_empty": "지도를 전환함",
    "subtitles.twilightforest.item.travellers_gear.double_jump": "이단 점프를 함",
    "subtitles.twilightforest.item.travellers_gear.perfect_dodge": "공격을 회피함",
    "subtitles.twilightforest.item.travellers_gear.side_step": "옆걸음을 함",
    "subtitles.twilightforest.item.travellers_gear.side_step_ready": "옆걸음이 재충전됨",
    "subtitles.twilightforest.item.travellers_gear.swap_hotbar": "허리띠가 바스락거림",
    "subtitles.twilightforest.item.travellers_goggles.zoom_in": "여행자 고글을 확대함",
    "subtitles.twilightforest.item.travellers_goggles.zoom_out": "여행자 고글을 축소함",
    "tag.item.c.ingots.wrought_iron": "연철 주괴",
    "tag.item.twilightforest.immune_to_thorns": "가시 피해 면역",
    "tag.item.twilightforest.scepters": "홀",
}

DRYING_RACKS = {
    "acacia": "아카시아나무",
    "bamboo": "대나무",
    "birch": "자작나무",
    "canopy": "캐노피나무",
    "cherry": "벚나무",
    "crimson": "진홍빛",
    "dark": "어둠나무",
    "dark_oak": "짙은 참나무",
    "jungle": "정글나무",
    "mangrove": "맹그로브나무",
    "mining": "광부나무",
    "oak": "참나무",
    "sorting": "분류나무",
    "spruce": "가문비나무",
    "time": "시간나무",
    "transformation": "변화나무",
    "twilight_oak": "황혼 참나무",
    "vangrove": "맹그로브나무",
    "warped": "뒤틀린",
}

TRAVELLER_EXACT = {
    "travellers_gear.info_indent": "  ⤷ ",
    "travellers_gear.modifier.empty": "비어 있음",
    "travellers_gear.ability": "능력: %s",
    "travellers_gear.broken": " (파손됨)",
    "travellers_gear.modifier.twilightforest.agile_ranger": "민첩한 궁수",
    "travellers_gear.modifier.twilightforest.agile_ranger.description": (
        "활 계열 아이템을 사용할 때도 정상 속도로 움직일 수 있습니다"
    ),
    "travellers_gear.modifier.twilightforest.all_night_goggles": "밤샘 고글",
    "travellers_gear.modifier.twilightforest.all_night_goggles.description": (
        "불면증과 엔더맨의 적대화를 막습니다"
    ),
    "travellers_gear.modifier.twilightforest.aquatic_agility": "수중 민첩성",
    "travellers_gear.modifier.twilightforest.aquatic_agility.description": (
        "호흡과 친수성 효과를 함께 제공합니다"
    ),
    "travellers_gear.modifier.twilightforest.arrow_magnetism": "화살 자력",
    "travellers_gear.modifier.twilightforest.arrow_magnetism.description": (
        "빗나간 화살을 회수합니다"
    ),
    "travellers_gear.modifier.twilightforest.auto_repair": "자동 수리",
    "travellers_gear.modifier.twilightforest.auto_repair.description": (
        "시간이 지나면 내구도를 수리합니다"
    ),
    "travellers_gear.modifier.twilightforest.double_jump": "이단 점프",
    "travellers_gear.modifier.twilightforest.double_jump.description": (
        "공중에서 한 번 더 점프할 수 있습니다"
    ),
    "travellers_gear.modifier.twilightforest.efficient_eater": "효율적인 식사",
    "travellers_gear.modifier.twilightforest.efficient_eater.description": (
        "이동으로 소모되는 허기를 줄입니다"
    ),
    "travellers_gear.modifier.twilightforest.gradual_glide": (
        "점진 활공 (웅크리기로 활성화)"
    ),
    "travellers_gear.modifier.twilightforest.gradual_glide.description": (
        "공중을 활공할 수 있습니다"
    ),
    "travellers_gear.modifier.twilightforest.haste": "성급함",
    "travellers_gear.modifier.twilightforest.haste.description": "성급함 II를 부여합니다",
    "travellers_gear.modifier.twilightforest.high_jump": "높이뛰기",
    "travellers_gear.modifier.twilightforest.item_display": (
        "아이템 표시 (단축키: ${tfkeybinds/key.twilightforest.item_display_map_cycle})"
    ),
    "travellers_gear.modifier.twilightforest.item_display.clock.unknown": (
        "시간 알 수 없음"
    ),
    "travellers_gear.modifier.twilightforest.item_display.compass.lodestone": (
        "%s (%s블록 거리)"
    ),
    "travellers_gear.modifier.twilightforest.item_display.description": (
        "고글에 아이템을 들고 우클릭해 표시 항목을 추가합니다"
    ),
    "travellers_gear.modifier.twilightforest.perfect_dodge": "완벽한 회피",
    "travellers_gear.modifier.twilightforest.perfect_dodge.description": (
        "30% 확률로 투사체를 회피합니다"
    ),
    "travellers_gear.modifier.twilightforest.red_thread_vision": (
        "붉은 실 시야 (단축키: ${tfkeybinds/key.twilightforest.red_thread_vision})"
    ),
    "travellers_gear.modifier.twilightforest.red_thread_vision.description": (
        "설치된 붉은 실을 볼 수 있습니다"
    ),
    "travellers_gear.modifier.twilightforest.side_step": "옆걸음",
    "travellers_gear.modifier.twilightforest.side_step.description": (
        "%s 또는 %s을(를) 두 번 눌러 돌진합니다"
    ),
    "travellers_gear.modifier.twilightforest.slimy_soles": "끈적한 밑창",
    "travellers_gear.modifier.twilightforest.slimy_soles.description": (
        "몸을 튕겨 낙하 피해를 막습니다"
    ),
    "travellers_gear.modifier.twilightforest.stealth": "은신 (웅크리기로 활성화)",
    "travellers_gear.modifier.twilightforest.stealth.description": (
        "웅크리면 투명해집니다"
    ),
    "travellers_gear.modifier.twilightforest.step_up": "자동 오르기",
    "travellers_gear.modifier.twilightforest.straight_ahead": "정면 돌파",
    "travellers_gear.modifier.twilightforest.straight_ahead.description": (
        "앞으로 이동하는 속도를 높입니다"
    ),
    "travellers_gear.modifier.twilightforest.swap_hotbar": (
        "단축바 교체 (단축키: ${tfkeybinds/key.twilightforest.swap_hotbar})"
    ),
    "travellers_gear.modifier.twilightforest.swap_hotbar.description": (
        "단축바를 보관하고 꺼낼 수 있습니다"
    ),
    "travellers_gear.modifier.twilightforest.swap_hotbar_ability": (
        "단축바 교체 (단축키: ${tfkeybinds/key.twilightforest.swap_hotbar})"
    ),
    "travellers_gear.modifier.twilightforest.swift_swim": "빠른 수영",
    "travellers_gear.modifier.twilightforest.unrestrained": "구속 해제",
    "travellers_gear.modifier.twilightforest.unrestrained.description": (
        "블록 때문에 이동 속도가 느려지는 것을 막습니다"
    ),
    "travellers_gear.modifier.twilightforest.water_walk": "수상 보행",
    "travellers_gear.modifier.twilightforest.water_walk.description": (
        "물 위를 걸을 수 있습니다"
    ),
    "travellers_gear.modifier.twilightforest.zoom": (
        "확대/축소 (단축키: ${tfkeybinds/key.twilightforest.zoom})"
    ),
    "travellers_gear.shift_info": "정보를 보려면 %s을(를) 누르세요",
}

TIP_EXACT = {
    "twilightforest.tips.alpha_yeti": (
        "알파 설인이 날뛰면 천장의 블록이 떨어져 나옵니다. 떨어지는 고드름을 "
        "조심하세요!"
    ),
    "twilightforest.tips.baby_jockey": (
        "아기 스켈레톤 드루이드가 떼거미를 타고 나타나기도 합니다."
    ),
    "twilightforest.tips.berry_bushes": (
        "The Twilight Forest 곳곳에서 베리 덤불을 발견할 수 있습니다."
    ),
    "twilightforest.tips.candelabra": (
        "촛대에 레드스톤 가루를 사용하면 불꽃이 붉게 변하고 레드스톤 신호를 냅니다."
    ),
    "twilightforest.tips.casket_logging": (
        "유품 상자는 유체와 상호작용하면 물이나 용암에 잠기거나 블록으로 둘러싸일 수 "
        "있습니다."
    ),
    "twilightforest.tips.casket_usage": (
        "유품 상자는 사용 횟수가 제한된 묘비 역할을 합니다. 사망할 때 인벤토리에 "
        "있으면 스스로 설치되어 모든 아이템을 보관합니다."
    ),
    "twilightforest.tips.clouds": (
        "비구름과 눈구름으로 날씨 효과를 흉내 낼 수 있습니다!"
    ),
    "twilightforest.tips.craft_travellers_gear": (
        "처리된 가죽을 건조해 무두질한 가죽으로 만들면 여행자 장비를 제작할 수 "
        "있습니다."
    ),
    "twilightforest.tips.emperors_cloth": (
        "황제의 옷감을 방어구와 조합하면 그 방어구가 보이지 않게 됩니다."
    ),
    "twilightforest.tips.essence_charge": (
        "무생물의 에센스를 홀과 조합하면 홀을 완전히 충전합니다."
    ),
    "twilightforest.tips.feather_fan": (
        "공작 깃털 부채로 몹을 밀어낼 수 있고, 점프하면서 사용하면 자신을 공중으로 "
        "띄울 수 있습니다. 겉날개와 철퇴에도 잘 어울립니다!"
    ),
    "twilightforest.tips.giant_block": (
        "거인의 곡괭이로 같은 블록의 4x4x4 영역을 채굴하면 거대 블록 1개가 "
        "드롭됩니다."
    ),
    "twilightforest.tips.jerky": "건조대에서 고기를 말리면 육포가 됩니다.",
    "twilightforest.tips.key_biome_locations": (
        "진행 생물 군계 무리는 서로 약 600블록 떨어져 생성되므로 다음 보스가 지나치게 "
        "멀리 있지는 않습니다."
    ),
    "twilightforest.tips.key_biomes": (
        "진행 생물 군계는 일반 보스 하나를 미니보스 넷이 둘러싼 무리로 생성됩니다."
    ),
    "twilightforest.tips.lich_deflection": (
        "황혼의 리치는 보호막이 사라진 뒤 황혼의 홀 투사체를 튕겨 냅니다."
    ),
    "twilightforest.tips.maze_map_focus": (
        "미노타우로스가 가끔 미로 지도 초점을 드롭하며, 이것으로 미로 지도를 만들 수 "
        "있습니다."
    ),
    "twilightforest.tips.minion_buff": (
        "황혼의 리치가 투사체로 자신의 부하를 맞히면 그 부하가 더 강하고 빨라집니다. "
    ),
    "twilightforest.tips.minoshroom": (
        "미노버섯 가까이에 오래 머물면 내려찍기 공격을 합니다."
    ),
    "twilightforest.tips.modify_travellers_gear": (
        "여행자 장비는 부위마다 기본 능력 1개가 있고, 부위당 최대 3개를 더 추가할 수 "
        "있습니다."
    ),
    "twilightforest.tips.mystic_crown": (
        "신비한 왕관을 착용하면 홀의 성능이 조금 향상됩니다."
    ),
    "twilightforest.tips.nether_bushes": (
        "낯선 물건과 재료뿐 아니라 기묘한 식물도 어둠의 탑에 뿌리를 내렸습니다."
    ),
    "twilightforest.tips.ominous_fire": "불길한 불은 생물을 언데드로 바꿀 수 있습니다.",
    "twilightforest.tips.ore_meter": (
        "광석 측정기를 켜면 주변의 모든 광석을 표시합니다. 특정 블록에 웅크린 채 "
        "우클릭하면 그 블록만 대상으로 지정해 주변 개수만 표시할 수도 있습니다. "
    ),
    "twilightforest.tips.oreberries": (
        "금속 오어베리 덤불은 지하에서 드물게 생성됩니다."
    ),
    "twilightforest.tips.parrying": (
        "타이밍에 맞춰 방패로 막으면 투사체를 몹에게 튕겨 낼 수 있습니다."
    ),
    "twilightforest.tips.phantoms": (
        "기사 유령은 보이지 않을 때 받는 피해가 크게 줄어듭니다. 전투할 때는 보이는 "
        "유령을 노리세요!"
    ),
    "twilightforest.tips.pocket_watch": (
        "토끼의 회중시계는 단축바에 있으면 이동 속도를 높이고, 손에 들면 채굴 속도를 "
        "높입니다."
    ),
    "twilightforest.tips.potion_flask": (
        "물약 플라스크에는 같은 물약을 최대 3회분까지 담을 수 있습니다."
    ),
    "twilightforest.tips.renewal": (
        "재생 마법이 부여된 홀은 플레이어 인벤토리의 필수 아이템을 사용해 스스로 "
        "재충전합니다."
    ),
    "twilightforest.tips.the_lore": (
        "이야기는 모두 여기에 있습니다. 직접 실마리를 풀어 보세요!"
    ),
    "twilightforest.tips.the_walls": (
        "죽음의 책이 벽 속에 있습니다. 바로 당신의 벽 속에요."
    ),
    "twilightforest.tips.trophy_pedestal": (
        "트로피 받침대는 활성화한 뒤에만 채굴할 수 있습니다."
    ),
    "twilightforest.tips.uncrafting_table": (
        "분해 작업대는 아이템을 분해하는 데만 쓰이지 않습니다. 아이템을 다른 것으로 "
        "재조합하고, 도구와 방어구를 수리하며, 장비 사이에 마법 부여를 옮길 수도 "
        "있습니다!"
    ),
    "twilightforest.tips.wrought_iron": (
        "연철 창살은 일반적인 방법으로 얻을 수 없으며, 연철로 만든 블록을 분해해야만 "
        "얻을 수 있습니다."
    ),
}

QUEST_OVERRIDES: dict[str, object] = {
    "quest.4193303999597249.quest_desc": [
        "&9The Twilight Forest&r는 황혼의 숲 차원을 게임에 추가하는 모드입니다. "
        "이 차원에는 완전히 새로운 아이템, 생물 군계, 몹과 보스가 가득합니다!\\n\\n"
        "&9황혼의 숲&r으로 가는 포털을 만들려면 땅에 2x2 구덩이를 파고 물을 "
        "채우세요. 구덩이 가장자리를 꽃으로 둘러싼 뒤 물에 다이아몬드를 던지세요."
        "\\n\\n제대로 만들었다면 토르가 신호를 보내고 포털이 활성화됩니다.\\n",
        "{image:atm:textures/questpics/gettingstarted/twilight_portal.png width:100 "
        "height:100 align:center fit:true}",
    ],
    "quest.30A61E1A1EFA81E6.quest_desc": [
        "&2강철잎&r은 엄밀히 말하면 주괴이며, &9&lThe Twilight Forest&r의 "
        "상자에서 발견할 수 있습니다. \\n방어구 부위마다 서로 다른 마법 부여가 "
        "적용됩니다!"
    ],
    "quest.52A29269A23F85B3.quest_desc": [
        "&9설인 방어구&r에는 알파 설인 털이 필요합니다. 예상하셨겠지만 알파 "
        "설인에게서만 나옵니다. \\n\\n그래도 이 방어구는 적을 얼어붙게 해 느리게 "
        "만듭니다!"
    ],
}

WOOD_NAMES = {
    "Canopy": "캐노피나무",
    "Dark": "어둠나무",
    "Mangrove": "맹그로브나무",
    "Mining": "광부나무",
    "Sorting": "분류나무",
    "Time": "시간나무",
    "Transformation": "변화나무",
    "Twilight Oak": "황혼 참나무",
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
    "White": "흰색",
    "Yellow": "노란색",
}

FURNITURE = {
    "Display Case": "진열장",
    "Fancy Seat Back": "고급 의자 등받이",
    "Flat Seat Back": "평평한 의자 등받이",
    "Raised Seat Back": "돌출형 의자 등받이",
    "Small Seat Back": "소형 의자 등받이",
    "Tall Seat Back": "높은 의자 등받이",
    "Seat Back": "의자 등받이",
    "Seat": "의자",
    "Bookcase": "책장",
    "Fancy Armor Stand": "고급 갑옷 거치대",
    "Fancy Clock": "고급 시계",
    "Fancy Crafter": "고급 제작대",
    "Fancy Sign": "고급 표지판",
    "Grandfather Clock": "괘종시계",
    "Label": "라벨",
    "Potion Shelf": "물약 선반",
    "Shelf": "선반",
    "Table": "탁자",
    "Tool Rack": "도구 걸이",
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """JSON을 UTF-8 무BOM 형식으로 기록한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def translation_memory() -> tuple[dict[str, str], set[str]]:
    """신규 키와 현재 산출물을 제외한 기존 번역 기억을 만든다."""
    english = load_json(BASE_ROOT / "en_us.json")
    korean = load_json(BASE_ROOT / "ko_kr.json")
    sources = load_json(BASE_ROOT / "candidate_sources.json")
    values: dict[str, set[str]] = defaultdict(set)
    for key, source in english.items():
        target = korean[key]
        if (
            isinstance(source, str)
            and isinstance(target, str)
            and source != target
            and sources[key]
            not in {"new_translation_required", "project_output_review"}
        ):
            values[source].add(target)
    conflicts = {source for source, candidates in values.items() if len(candidates) > 1}
    memory = {
        source: next(iter(candidates))
        for source, candidates in values.items()
        if len(candidates) == 1
    }
    return memory, conflicts


def mask_text(text: str) -> tuple[str, list[str]]:
    """자동 번역에서 보존할 토큰을 본문과 분리한다."""
    protected: list[str] = []

    def replace(match: re.Match[str]) -> str:
        index = len(protected)
        protected.append(match.group(0))
        return f"ZXQPROTECTED{index}QXZ"

    return PROTECTED.sub(replace, text), protected


def restore_text(text: str, protected: list[str]) -> str:
    """보호 토큰을 원래 값으로 복원한다."""
    for index, value in enumerate(protected):
        token = f"ZXQPROTECTED{index}QXZ"
        if text.count(token) != 1:
            raise ValueError(f"자동 번역 보호 토큰이 바뀌었습니다: {token}:{text}")
        text = text.replace(token, value)
    if re.search(r"ZXQPROTECTED\d+QXZ", text):
        raise ValueError(f"복원되지 않은 보호 토큰이 있습니다: {text}")
    return text


def request_translation(source: str) -> str:
    """보호 처리한 영어 문장의 한국어 자동 번역 후보를 요청한다."""
    masked, protected = mask_text(source)
    query = urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": "ko", "dt": "t", "q": masked}
    )
    request = urllib.request.Request(
        f"{GOOGLE_TRANSLATE}?{query}",
        headers={"User-Agent": "ATM10-Korean-translation-candidate/1.0"},
    )
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            translated = "".join(row[0] for row in payload[0] if row and row[0])
            return restore_text(translated, protected)
        except Exception as exc:  # pragma: no cover - 외부 후보 서비스 오류 보고용
            last_error = exc
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"자동 번역 후보 요청 실패: {source}") from last_error


def build_candidates() -> dict[str, object]:
    """신규 키 248개의 보호된 자동 번역 후보를 만든다."""
    english = load_json(BASE_ROOT / "en_us.json")
    sources = load_json(BASE_ROOT / "candidate_sources.json")
    memory, conflicts = translation_memory()
    cache = load_json(CACHE_PATH) if CACHE_PATH.is_file() else {}
    candidates: dict[str, object] = {}
    candidate_sources: dict[str, str] = {}
    requests: set[str] = set()
    for key, value in english.items():
        if sources[key] != "new_translation_required":
            continue
        if not isinstance(value, str):
            raise TypeError(f"지원하지 않는 신규 값 자료형: {key}")
        if (
            family_goal.is_allowed_original(value)
            or key.startswith("jukebox_song.")
            or key.endswith(".author")
        ):
            candidates[key] = value
            candidate_sources[key] = "reviewed_original_candidate"
        elif value in memory and value not in conflicts:
            candidates[key] = memory[value]
            candidate_sources[key] = "family_memory_candidate"
        elif isinstance(cache.get(value), str):
            candidates[key] = cache[value]
            candidate_sources[key] = "automatic_cache_candidate"
        else:
            requests.add(value)
    failures: list[str] = []
    if requests:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(request_translation, source): source
                for source in sorted(requests)
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                except Exception as exc:  # pragma: no cover - 외부 오류 목록 보존
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_PATH, cache)
    if failures:
        raise RuntimeError("자동 번역 후보 생성 실패:\n" + "\n".join(failures))
    for key, value in english.items():
        if sources[key] != "new_translation_required" or key in candidates:
            continue
        translated = cache[value]
        assert isinstance(value, str) and isinstance(translated, str)
        errors = family_goal.validate_value(key, value, translated)
        if errors:
            raise ValueError("; ".join(errors))
        candidates[key] = translated
        candidate_sources[key] = "automatic_translation_candidate"
    write_json(BASE_ROOT / "auto_candidates.json", candidates)
    write_json(BASE_ROOT / "auto_candidate_sources.json", candidate_sources)
    report = {
        "scope": "The Twilight Forest 신규 언어 키 번역 후보",
        "candidate_counts": dict(sorted(Counter(candidate_sources.values()).items())),
        "protected_patterns": [
            "numbers",
            "placeholders",
            "URLs",
            "format codes",
            "keybind references",
            "line breaks",
        ],
        "current_output_self_reuse_excluded": True,
        "translation_memory_conflicts_excluded": len(conflicts),
        "review_status": "pending_manual_review",
    }
    write_json(WORK_ROOT / "auto_candidate_report.json", report)
    return report


def reviewed_new_value(key: str, source: str, candidate: str) -> str:
    """신규 후보를 키 문맥과 확정 용어에 맞게 최종 검수한다."""
    if key in NEW_EXACT:
        return NEW_EXACT[key]
    if key in TRAVELLER_EXACT:
        return TRAVELLER_EXACT[key]
    if key in TIP_EXACT:
        return TIP_EXACT[key]
    match = re.fullmatch(r"block\.twilightforest\.(.+)_drying_rack", key)
    if match and match.group(1) in DRYING_RACKS:
        return f"{DRYING_RACKS[match.group(1)]} 건조대"
    if key.startswith("jukebox_song.") or key.endswith(".author"):
        return source
    return candidate


def review_base_language() -> dict[str, object]:
    """현재 JAR·기존 프로젝트·신규 후보를 영어 원문과 대조한다."""
    english = load_json(BASE_ROOT / "en_us.json")
    korean = load_json(BASE_ROOT / "ko_kr.json")
    sources = load_json(BASE_ROOT / "candidate_sources.json")
    candidates = load_json(BASE_ROOT / "auto_candidates.json")
    before = dict(korean)
    for key, source in english.items():
        if key in FORMAT_FIXES:
            korean[key] = FORMAT_FIXES[key]
            sources[key] = "manual_review"
        elif sources[key] == "new_translation_required":
            candidate = candidates[key]
            if not isinstance(source, str) or not isinstance(candidate, str):
                raise TypeError(f"문자열이 아닌 신규 번역 후보: {key}")
            korean[key] = reviewed_new_value(key, source, candidate)
            sources[key] = "manual_review"
        errors = family_goal.validate_value(key, source, korean[key])
        if errors:
            raise ValueError("; ".join(errors))
    changed_keys = [key for key in korean if korean[key] != before[key]]
    write_json(BASE_ROOT / "ko_kr.json", korean)
    write_json(BASE_ROOT / "candidate_sources.json", sources)
    return {
        "keys_reviewed": len(english),
        "keys_changed": sum(value == "manual_review" for value in sources.values()),
        "changes_this_run": len(changed_keys),
        "source_counts": dict(sorted(Counter(sources.values()).items())),
    }


def review_quests() -> dict[str, object]:
    """전용 및 관련 FTB Quests의 표시 문구와 fallback 경로를 검수한다."""
    reviewed = 0
    changed = 0
    changes_this_run = 0
    for root in sorted((WORK_ROOT / "quests").glob("*")):
        korean_path = root / "ko_kr.json"
        source_path = root / "candidate_sources.json"
        if not korean_path.is_file():
            continue
        korean = load_json(korean_path)
        sources = load_json(source_path)
        before = dict(korean)
        for key, value in QUEST_OVERRIDES.items():
            if key in korean:
                korean[key] = value
                sources[key] = "manual_review"
        reviewed += len(korean)
        changed += sum(value == "manual_review" for value in sources.values())
        changes_this_run += sum(korean[key] != before[key] for key in korean)
        write_json(korean_path, korean)
        write_json(source_path, sources)
    return {
        "keys_reviewed": reviewed,
        "keys_changed": changed,
        "changes_this_run": changes_this_run,
    }


def review() -> dict[str, object]:
    """언어와 퀘스트 검수 결과를 한 보고서로 기록한다."""
    report = {
        "family": "The Twilight Forest",
        "language": review_base_language(),
        "ftbquests": review_quests(),
    }
    write_json(WORK_ROOT / "manual_review_report.json", report)
    return report


def translate_bibliowoods_value(source: str) -> str:
    """Twilight Forest 목재 가구 이름을 확정 사전으로 조합한다."""
    color = ""
    remainder = source
    for english, korean in sorted(COLORS.items(), key=lambda row: -len(row[0])):
        if remainder.startswith(f"{english} "):
            color = korean
            remainder = remainder[len(english) + 1 :]
            break
    wood = ""
    for english, korean in sorted(WOOD_NAMES.items(), key=lambda row: -len(row[0])):
        if remainder.startswith(f"{english} "):
            wood = korean
            remainder = remainder[len(english) + 1 :]
            break
    if not wood or remainder not in FURNITURE:
        raise ValueError(f"Bibliowoods 이름 규칙을 해석할 수 없습니다: {source}")
    return " ".join(part for part in (color, wood, FURNITURE[remainder]) if part)


def build_bibliowoods() -> dict[str, object]:
    """Bibliowoods 중 Twilight Forest 목재 전용 1,256개 키만 생성한다."""
    instance = resolve_source_root()
    matches = sorted((instance / "mods").glob("bibliowoods-*.jar"))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Bibliowoods JAR 검색 결과가 하나가 아닙니다: {matches}"
        )
    with ZipFile(matches[0]) as archive:
        all_english = json.loads(
            archive.read("assets/bibliowoods/lang/en_us.json").decode("utf-8-sig")
        )
    english = {
        key: value for key, value in all_english.items() if "twilightforest" in key
    }
    korean = {key: translate_bibliowoods_value(value) for key, value in english.items()}
    sources = {key: "generated_reviewed_translation" for key in english}
    root = WORK_ROOT / "bibliowoods"
    write_json(root / "en_us.json", english)
    write_json(root / "ko_kr.json", korean)
    write_json(root / "candidate_sources.json", sources)
    output = OUTPUT_ASSETS / "bibliowoods/lang/ko_kr.json"
    write_json(output, korean)
    report = {
        "label": "Bibliowoods Legacy - Twilight Forest integration",
        "jar": matches[0].name,
        "all_english_keys": len(all_english),
        "twilight_forest_keys": len(english),
        "other_mod_keys_excluded": len(all_english) - len(english),
        "generated_reviewed_translations": len(korean),
        "output": output.relative_to(PROJECT_ROOT).as_posix(),
    }
    write_json(WORK_ROOT / "bibliowoods_scope.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("candidates", "review", "bibliowoods"))
    args = parser.parse_args()
    if args.command == "candidates":
        report = build_candidates()
    elif args.command == "review":
        report = review()
    else:
        report = build_bibliowoods()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
