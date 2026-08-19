#!/usr/bin/env python3
"""공통 UI 언어 파일의 구조와 보호 문자열을 검증하고 산출물에 반영한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from zipfile import ZipFile

from common_ui_catalog import (
    GROUPS,
    PACK_LANGUAGE_TARGETS,
    TARGETS,
    PackLanguageTarget,
    Target,
)
from build_ae2_quests import flatten, parse_language_snbt
from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_common_ui import WORK_ROOT, find_jar, load_json

OUTPUT_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
JEI_QUEST_TERM_KEYS = {
    "quest.13AA91D39A2CABF2.quest_desc",
    "quest.1FCC474860587169.quest_desc",
    "quest.4B7840F1A8CF1378.quest_desc",
    "quest.57C4A0BAE739E903.quest_desc",
    "quest.65C8A43FEDBA3835.quest_desc",
    "quest.683C260C854C5AA3.quest_desc",
}
JEI_QUEST_WORKING_FILES = {
    "quest.13AA91D39A2CABF2.quest_desc": Path(
        "working/productivebees/quest_overrides.json"
    ),
    "quest.1FCC474860587169.quest_desc": Path(
        "working/forbidden_arcanus/quests/related/ko_kr.json"
    ),
    "quest.4B7840F1A8CF1378.quest_desc": Path(
        "working/draconic_evolution/quests/draconic_evolution/ko_kr.json"
    ),
    "quest.57C4A0BAE739E903.quest_desc": Path(
        "working/industrial_foregoing/quests/industrial_foregoing/ko_kr.json"
    ),
    "quest.65C8A43FEDBA3835.quest_desc": Path(
        "working/refined_storage/quests/refined_storage/ko_kr.json"
    ),
    "quest.683C260C854C5AA3.quest_desc": Path(
        "working/cataclysm/quests/cataclysm/ko_kr.json"
    ),
}
JEI_QUEST_OVERRIDES = PROJECT_ROOT / "working/common_ui/jei/quest_overrides.json"
JEI_KUBEJS_RELATIVE = Path("kubejs/startup_scripts/incompatible_versions.js")
JEI_KUBEJS_ENGLISH = (
    'event.checkModVersion("jei", "19.22.0.316", '
    '"This version is causing durability tools issues")'
)
JEI_KUBEJS_KOREAN = (
    'event.checkModVersion("jei", "19.22.0.316", '
    '"이 버전은 도구 내구도 문제를 일으킵니다")'
)
JADE_RECHECK_VALUES = {
    "tooltip.jade.mode_comparator": "비교",
    "tooltip.jade.power": "신호 세기: %d",
    "jade.input_signal": "입력 신호: %d",
    "gui.jade.by": "Snownee가 %s을 담아 만들었습니다",
    "config.jade.display_entities": "개체 표시",
    "config.jade.display_entities_extra_msg": "entity,엔티티,개체",
    "config.jade.plugin_minecraft.entity": "Minecraft - 개체",
    "config.jade.plugin_minecraft.entity_health": "개체 체력",
    "config.jade.plugin_minecraft.entity_armor": "개체 방어력",
    "config.jade.plugin_minecraft.potion_effects": "개체 상태 효과",
    "config.jade.plugin_minecraft.container_entity": "보관함 개체",
    "jade.instrument.hat": "클릭과 스틱",
    "config.jade.plugin_minecraft.next_entity_drop": "개체의 다음 드롭 시간",
    "config.jade.plugin_minecraft.next_entity_drop_desc": (
        "달걀이나 아르마딜로 인갑처럼 개체가 다음 아이템을 떨어뜨릴 때까지 "
        "남은 시간을 표시합니다."
    ),
    "jade.harvest_tool.unbreakable": "부서지지 않음",
    "jade.locked": "보관함이 잠겨 있습니다",
    "config.jade.plugin_minecraft.animal_owner": "동물 소유자",
    "jade.owner": "소유자: %s",
    "jade.seconds": "{0}초",
    "jade.minutes": "{0}분",
    "jade.minutes_seconds": "{0}분 {1}초",
    "config.jade.plugin_jade_access.entity": "개체 세부 정보",
    "jade.access.entity.white": "하얀색 %s",
    "jade.access.entity.light_gray": "회백색 %s",
    "jade.access.entity.lime": "연두색 %s",
    "jade.access.entity.light_blue": "하늘색 %s",
    "jade.access.entity.purple": "보라색 %s",
    "jade.access.entity.magenta": "자홍색 %s",
    "config.jade.plugin_jade_access.entity_variant": "개체 변형",
    "config.jade.plugin_jade_access.held_item": "개체가 들고 있는 아이템",
    "jade.ignore_list.comment": (
        'Jade가 무시할 대상 목록입니다. "values" 목록에 레지스트리 ID를 '
        "추가할 수 있습니다."
    ),
}
JADE_KUBEJS_LANGUAGE = {
    "config.jade.plugin_modern_industrialization.overclock": "Machine Overclock",
    "config.jade.plugin_modern_industrialization.pipe": "Pipe Information",
}
JADE_KUBEJS_KOREAN = {
    "config.jade.plugin_modern_industrialization.overclock": "기계 오버클럭",
    "config.jade.plugin_modern_industrialization.pipe": "파이프 정보",
}
JADE_LANGUAGE_PREFIXES = ("config.jade.", "jade.", "waila.", "gui.waila.")
JOURNEYMAP_CLASS_FALLBACKS = {
    "Waypoint Editor Options": "웨이포인트 편집기 설정",
}
JOURNEYMAP_RECHECK_VALUES = {
    "jm.colorpalette.world": "월드",
    "jm.common.copy_config.fullscreen": "전체 화면 지도로 복사",
    "jm.common.curseforge": "CurseForge",
    "jm.common.entity_display.outlined_icons": "윤곽선 아이콘",
    "jm.common.modrinth": "Modrinth",
    "jm.common.profession.label": "직업: ",
    "jm.common.radar_hide_spectators": "관전자 숨기기",
    "jm.common.share.chat.journeymap": "JourneyMap: ",
    "jm.common.show_entity_names": "개체 이름 표시",
    "jm.config.category.minimap": "미니맵 사전 설정 1",
    "jm.feature.fairplay": "FairPlay",
    "jm.server.allow_in_game_beacons": "웨이포인트 신호기 허용",
    "jm.server.waypoint_teleport_only": "웨이포인트 순간이동 전용",
    "jm.theme.infoslot.day": "경과 일수: %1$s",
    "jm.theme.labelsource.blank": "빈칸",
    "jm.waypoint.beacon.title": "신호기 설정",
    "jm.waypoint.groups.global.suffix": " (전역)",
    "jm.waypoint.render_enabled": "웨이포인트 렌더링",
    "jm.waypoint.temp": "임시: ",
    "key.journeymap.minimap_preset": "미니맵 사전 설정 전환",
}
JOURNEYMAP_FORBIDDEN_TERMS = re.compile(
    r"세계|엔티티|프리셋|전체화면|사용자 정의|관중|마을 주민|"
    r"커스포지|모드린스|서포터|생물 군계|단축기|비콘|텔레포트"
)
JOURNEYMAP_RELATED_LANGUAGE = re.compile(r"(?i)journeymap|\bwaypoints?\b")
JOURNEYMAP_OTHER_OWNER_CONFLICTS = re.compile(
    r"세계|비콘|전체화면|전체 지도|프리셋|엔티티|텔레포트|관중|사용자 정의"
)
FTBCHUNKS_CLASS_FALLBACKS = {
    "ftbchunks.command.unloaded": "강제 로드를 해제한 청크: %d",
    "ftbchunks.gui.open_creation_gui": "아이콘 만들기 화면 열기",
}
FTBCHUNKS_RECHECK_VALUES = {
    "ftbchunks.config.client.appearance": "외형",
    "ftbchunks.config.client.appearance.chunk_grid": "청크 격자",
    "ftbchunks.config.client.appearance.only_surface_entities": "지표면 개체만",
    "ftbchunks.config.client.waypoints.in_world_waypoints": "월드에 웨이포인트 표시",
    "ftbchunks.config.client.waypoints.waypoint_fade_distance": (
        "웨이포인트 신호기 최소 페이드 거리"
    ),
    "ftbchunks.config.client.waypoints.waypoint_dot_fade_distance": (
        "웨이포인트 점 최소 페이드 거리"
    ),
    "ftbchunks.config.client.minimap.entities": "개체",
    "ftbchunks.config.client.minimap.entity_heads": "개체 머리",
    "ftbchunks.config.client.minimap.large_entities": "대형 개체",
    "ftbchunks.config.client.minimap.visibility": "불투명도",
    "ftbchunks.config.client.minimap.pointer_icon_mode": "대형 지도 포인터 아이콘 모드",
    "ftbchunks.minimap.pointer_icon_mode.both": "둘 다",
    "ftbchunks.gui.ally_whitelist": "동맹 허용 목록",
    "ftbchunks.gui.ally_blacklist": "동맹 차단 목록",
    "ftbchunks.gui.entity_icon_settings": "개체 아이콘 설정",
    "ftbteamsconfig.ftbchunks.allow_pvp": "PvP 전투 허용",
    "ftbteamsconfig.ftbchunks.entity_interact_mode": "개체 상호작용 모드",
    "ftbteamsconfig.ftbchunks.nonliving_entity_attack_mode": "무생물 개체 공격 모드",
    "ftbchunks.config.server.disable_protection.tooltip": (
        "모든 사람을 신뢰할 수 있고 소유 지역을 강제 로드에만 사용하는 "
        "개인 서버에 유용합니다."
    ),
    "ftbchunks.config.server.location_mode_override": '팀 "위치 공개 범위" 재정의',
    "ftbchunks.action_prevented": (
        "소유 지역 보호로 인해 이곳에서는 상호작용할 수 없습니다!"
    ),
    "ftbchunks.config.client.minimap.entity_icon": "개체 아이콘 표시 여부",
    "ftbchunks.config.server.team_prop_defaults.def_entity_interact": (
        "개체 상호작용 모드"
    ),
    "ftbchunks.config.server.team_prop_defaults.def_entity_attack": (
        "무생물 개체 공격 모드"
    ),
    "ftbchunks.config.server.team_prop_defaults.def_player_visibility": (
        "위치 공개 범위"
    ),
    "ftbchunks.config.server.team_prop_defaults.def_claim_visibility": (
        "소유 지역 공개 범위"
    ),
    "minimap.info.ftbchunks.biome.title": "생물군계",
    "ftbchunks.commands.owner": "소유자: ",
}
FTBCHUNKS_FORBIDDEN_TERMS = re.compile(
    r"엔티티|클레임|화이트리스트|블랙리스트|세계의 웨이포인트|"
    r"비콘|도트|바이옴|가시성|상호 작용|영토 보호|대형 미니맵"
)
FTBCHUNKS_QUEST_VALUES = {
    "quest.0C93D7A607AB8B83.quest_desc": [
        "청크를 소유하려면 &6M&r 키로 지도를 연 다음, 왼쪽 위의 "
        "&a소유한 청크&r 아이콘을 클릭하세요.\\n\\n청크를 좌클릭하거나 "
        "드래그하면 소유할 수 있습니다.\\n\\n청크를 강제 로드하려면 "
        "Shift 키를 누른 채 해당 청크를 좌클릭하세요. 제대로 설정되면 "
        "청크에 빗금이 표시됩니다."
    ],
    "task.103C42C743E2A2DB.title": "청크 소유",
}
FTBCHUNKS_KUBEJS_REFERENCES = {
    "kubejs/server_scripts/Tweaks/tags.js",
}
FTBTEAMS_CLASS_FALLBACKS = {
    "sidebar_button.ftbteams.team_lives": "팀 목숨",
}
FTBTEAMS_RECHECK_VALUES = {
    "ftbteams.player_already_in_party": "'%s' 플레이어는 이미 파티에 속해 있습니다!",
    "ftbteams.cant_edit": "편집할 수 없습니다: %s",
    "ftbteams.not_member": "%s은(는) %s의 팀원이 아닙니다!",
    "ftbteams.name_too_short": "팀 이름이 너무 짧습니다! (3글자 이상이어야 합니다)",
    "ftbteams.team_already_exists": "'%s' 팀이 이미 존재합니다!",
    "ftbteams.out_of_lives": ("파티에 남은 목숨이 없어 새 팀원을 초대할 수 없습니다!"),
    "ftbteams.info.id": "긴 팀 ID: %s",
    "ftbteams.info.members": "팀원:",
    "ftbteams.info.members.none": "팀원 없음",
    "ftbteams.list": "모든 FTB Teams: %s",
    "ftbteams.cant_kick_owner": "소유자를 추방할 수 없습니다!",
    "ftbteamsconfig.ftbteams.max_msg_history_size": "메시지 기록 최대 개수",
    "ftbteams.privacy_mode.private": "비공개",
    "ftbteams.privacy_mode.public": "공개",
    "ftbteams.create_party.info": ("파티 팀을 만들어 팀원을 초대하고 함께 진행하세요."),
    "ftbteams.gui.disband": "파티 해산",
    "ftbteams.gui.disband.confirm": "파티를 해산하시겠습니까?",
    "ftbteams.gui.add_members": "팀원 추가",
    "ftbteams.gui.remove_ally": "%s와의 동맹 해제",
    "ftbteams.gui.remove_ally.confirm": "%s와의 동맹을 해제하시겠습니까?",
    "ftbteams.ranks.invited": "초대받음",
    "ftbteams.ranks.member": "팀원",
    "key.ftbteams.open_gui": "팀 화면 열기",
    "ftbteams.message.invited": "%s에게 초대를 보냈습니다",
    "ftbteams.message.joined": "%s 님이 파티에 참가했습니다!",
    "ftbteams.message.demoted": "%s 님을 팀원으로 강등했습니다!",
    "ftbteams.message.created_server_team": "'%s' 서버 팀을 만들었습니다!",
    "ftbteams.message.deleted_server_team": "'%s' 서버 팀을 삭제했습니다!",
    "ftbteams.message.team_disbanded": ("파티 팀을 강제로 해산했습니다: '%s' (%s)!"),
    "ftbteams.message.chat_redirected.on": ("채팅 메시지가 팀 채팅으로 전송됩니다"),
    "ftbteams.message.chat_redirected.off": ("채팅 메시지가 기본 채팅으로 전송됩니다"),
    "ftbteams.message.added_stage": "팀 스테이지를 추가했습니다: %s",
    "ftbteams.message.removed_stage": "팀 스테이지를 제거했습니다: %s",
    "ftbteams.message.team_stages_header": "이 팀의 팀 스테이지(%s개):",
    "ftbteams.click_show_info": "클릭하여 팀 정보 표시",
}
FTBTEAMS_FORBIDDEN_TERMS = re.compile(r"구성원|멤버|FTB 팀|팀 GUI|파티 해체|개인|공용")
FTBTEAMS_QUEST_VALUES = {
    "quest.5AC1BE754210429E.quest_desc": [
        "친구들과 팀을 만들고 싶다면 &a/ftbteams party create (팀 이름)&r "
        "명령어를 사용하세요!"
    ],
}
FTBTEAMS_RELATED_LANGUAGE = re.compile(r"(?i)ftb.?teams|team.?stage")
FTBTEAMS_OTHER_OWNER_CONFLICTS = {
    "securitycraft:securitycraft.configuration.enable_team_ownership.tooltip",
    "securitycraft:securitycraft.configuration.team_ownership_precedence.tooltip",
}
WAYSTONES_CLASS_FALLBACKS = {
    "tooltip.waystones.sharestone": "다른 셰어스톤으로 순간이동",
    "tooltip.waystones.visibility": "공개 범위: %s",
}
WAYSTONES_RECHECK_VALUES = {
    "item.waystones.crumbling_attuned_shard": "부서져 가는 조율된 조각",
    "gui.waystones.waystone_settings.modifiers_active": "활성화된 수정자: %d개",
    "gui.waystones.waystone_settings.visibility.activation": "활성화하면 표시",
    "gui.waystones.waystone_settings.visibility.global": "모든 플레이어에게 표시",
    "gui.waystones.inventory.confirm_return": (
        "정말 이 웨이스톤으로 귀환하시겠습니까?"
    ),
    "chat.waystones.cannot_dimension_warp": ("이 월드 간에는 순간이동할 수 없습니다."),
    "chat.waystones.cannot_transport_leashed_dimensional": (
        "목줄에 묶인 몹과 함께 월드 사이를 이동할 수 없습니다."
    ),
    "chat.waystones.warp_plate_has_invalid_target": (
        "이 워프 플레이트 안의 조각은 조율이 풀렸습니다."
    ),
    "tooltip.waystones.cooldown_left": "재사용 대기시간: %d초",
    "tooltip.waystones.attuned_shard.attunement_lost": ("이 조각은 조율이 풀렸습니다."),
    "tooltip.waystones.not_enough_xp": ("경험치가 부족합니다! (필요 레벨: %d)"),
    "waystones.untitled_waystone": "이름 없는 웨이스톤",
    "commands.waystones.list.entry.owned": "-     소유: %s (%s): %s",
    "commands.waystones.list.entry.activated": "- 활성화: %s (%s): %s",
    "commands.waystones.activate.success.single": (
        "'%s' 웨이스톤을 %s 님에게 활성화했습니다."
    ),
    "commands.waystones.forget.success.single": (
        "'%s' 웨이스톤을 %s 님에게서 비활성화했습니다."
    ),
    "commands.waystones.cooldown.reset.success.single": (
        "재사용 대기시간 '%s': %s 님에게 초기화했습니다."
    ),
    "waystones.configuration.general.restrictedWaystones": "편집 제한 웨이스톤",
    "waystones.configuration.general.allowedVisibilities.tooltip": (
        "모든 플레이어가 전체 공개 웨이스톤을 만들 수 있게 하려면 "
        '"GLOBAL"을 추가하세요.'
    ),
    "waystones.configuration.general.defaultVisibility.tooltip": (
        "새로 배치하거나 발견한 웨이스톤을 기본적으로 전체 공개로 설정하려면 "
        '"GLOBAL"로 설정하세요.'
    ),
    "waystones.configuration.teleports.enableCosts": "비용 사용",
    "waystones.configuration.teleports.enableCooldowns": "재사용 대기시간 사용",
    "waystones.configuration.teleports.enableModifiers": "수정자 사용",
    "waystones.configuration.teleports.transportLeashed": "목줄에 묶인 몹 이동",
    "waystones.configuration.teleports.entityDenyList": "개체 차단 목록",
    "waystones.configuration.inventoryButton.inventoryButtonX": (
        "인벤토리 워프 버튼 X 위치"
    ),
    "waystones.configuration.inventoryButton.inventoryButtonY": (
        "인벤토리 워프 버튼 Y 위치"
    ),
    "waystones.configuration.worldGen.chunksBetweenWildWaystones": (
        "야생 웨이스톤 간 청크 거리"
    ),
    "waystones.configuration.worldGen.wildWaystonesDimensionDenyList": (
        "차원 차단 목록"
    ),
    "waystones.configuration.worldGen.nameGenerationPresets": ("이름 생성 사전 설정"),
    "waystones.configuration.worldGen.spawnInVillages": "마을에 생성",
    "waystones.configuration.compatibility": "모드 연동",
    "waystones.configuration.compatibility.journeyMap": "JourneyMap 지원 사용",
    "waystones.configuration.compatibility.dynmap": "Dynmap 지원 사용",
    "waystones.configuration.blueMap.enabled": "BlueMap 지원 사용",
    "waystones.configuration.blueMap.includeUndiscoveredWaystones": (
        "미발견 웨이스톤 포함"
    ),
    "config.jade.plugin_waystones.waystone": "Waystones",
}
WAYSTONES_FORBIDDEN_TERMS = re.compile(
    r"세계|엔티티|프리셋|텔레포트|재사용 대기 시간|글로벌|전역|" r"거부 목록|모드 통합"
)
WAYSTONES_RELATED_LANGUAGE = re.compile(
    r"(?i)\b(?:waystones?|sharestones?|portstones?)\b"
)
WAYSTONES_KUBEJS_REFERENCES = {
    "kubejs/server_scripts/Tweaks/tags.js",
}
NATURESCOMPASS_RECHECK_VALUES = {
    "string.naturescompass.searchForNext": "다음 생물군계 검색",
    "string.naturescompass.heightVariation": "높이 변화량",
    "string.naturescompass.highHumidity": "높은 습도",
    "string.naturescompass.precipitation": "강수 형태",
    "string.naturescompass.temperature": "온도",
}
NATURESCOMPASS_FORBIDDEN_TERMS = re.compile(
    r"바이옴|카테고리|텔레포트|디멘션|코디네이트|높이 변화율|습도 높음"
)
NATURESCOMPASS_QUEST_VALUES = {
    "quest.70B6C9409AE69284.quest_desc": [
        "자연의 나침반을 사용하면 찾을 생물군계를 목록에서 고를 수 있어요."
        "\\n\\n생물군계를 선택하고 '검색 시작'을 누르면 왼쪽 위에 정보가 "
        "표시되고, 나침반이 해당 생물군계의 방향을 가리켜요.\\n\\n탐험가의 "
        "나침반도 같은 방식으로 작동하지만, 생물군계 대신 구조물을 찾아요."
    ],
    "quest.70B6C9409AE69284.quest_subtitle": "생물군계/구조물 찾기 도우미",
    "quest.70B6C9409AE69284.title": "검색용 나침반",
}


def protected(value: object, pattern: re.Pattern[str]) -> list[str]:
    return pattern.findall(value) if isinstance(value, str) else []


def validate_value(
    key: str,
    english: object,
    korean: object,
    errors: list[str],
    path: str = "",
    translatable: bool = True,
) -> None:
    """중첩 텍스트 컴포넌트까지 자료형과 보호 문자열을 검증한다."""
    location = f"{key}{path}"
    if type(english) is not type(korean):
        errors.append(f"자료형 불일치: {location}")
        return
    if isinstance(english, str):
        if not translatable and english != korean:
            errors.append(f"비번역 필드 변경: {location}")
        protected_english = english
        protected_korean = korean
        is_jei_search_mode = (
            key.startswith("jei.config.client.search.")
            and key.endswith("SearchMode")
            and english[:1] in "@#$^&%"
        )
        if is_jei_search_mode:
            if korean[:1] != english[:1]:
                errors.append(f"JEI 검색 접두사 불일치: {location}")
            protected_english = english[1:]
            protected_korean = korean[1:]
        if protected(protected_english, PLACEHOLDER) != protected(
            protected_korean, PLACEHOLDER
        ):
            errors.append(f"자리표시자 불일치: {location}")
        if protected(protected_english, FORMAT_CODE) != protected(
            protected_korean, FORMAT_CODE
        ):
            errors.append(f"서식 코드 불일치: {location}")
        if english.count("\n") != korean.count("\n"):
            errors.append(f"줄바꿈 수 불일치: {location}")
        return
    if isinstance(english, list):
        if len(english) != len(korean):
            errors.append(f"목록 길이 불일치: {location}")
            return
        for index, (english_item, korean_item) in enumerate(zip(english, korean)):
            validate_value(
                key,
                english_item,
                korean_item,
                errors,
                f"{path}[{index}]",
                translatable,
            )
        return
    if isinstance(english, dict):
        if list(english) != list(korean):
            errors.append(f"객체 키 또는 순서 불일치: {location}")
            return
        for field in english:
            validate_value(
                key,
                english[field],
                korean[field],
                errors,
                f"{path}.{field}",
                field == "text",
            )
        return
    if english != korean:
        errors.append(f"비문자 값 변경: {location}")


def verify_target(
    instance: Path, target: Target, copy_output: bool
) -> list[dict[str, object]]:
    jar_path = find_jar(instance, target)
    rows = []
    with ZipFile(jar_path) as jar:
        for namespace in target.namespaces:
            english = load_json(jar, f"assets/{namespace}/lang/en_us.json")
            if target.key_prefixes:
                english = {
                    key: value
                    for key, value in english.items()
                    if key.startswith(target.key_prefixes)
                }
            fallback_values = {
                "journeymap": JOURNEYMAP_CLASS_FALLBACKS,
                "ftbchunks": FTBCHUNKS_CLASS_FALLBACKS,
                "ftbteams": FTBTEAMS_CLASS_FALLBACKS,
                "waystones": WAYSTONES_CLASS_FALLBACKS,
            }.get(namespace, {})
            expected_keys = [*english, *fallback_values]
            working = WORK_ROOT / target.group / namespace / "ko_kr.json"
            korean = json.loads(working.read_text(encoding="utf-8"))
            errors = []
            if list(korean) != expected_keys:
                missing = sorted(set(expected_keys) - set(korean))
                extra = sorted(set(korean) - set(expected_keys))
                errors.append(f"키 또는 순서 불일치: 누락={missing}, 초과={extra}")
            for key in english.keys() & korean.keys():
                validate_value(key, english[key], korean[key], errors)
            fallback_mismatches = sorted(
                key
                for key, expected in fallback_values.items()
                if korean.get(key) != expected
            )
            if fallback_mismatches:
                errors.append(f"클래스 fallback 번역 불일치: {fallback_mismatches}")
            if working.read_bytes().startswith(b"\xef\xbb\xbf"):
                errors.append("UTF-8 BOM이 있습니다")
            if errors:
                raise RuntimeError(f"{namespace} 검증 실패:\n" + "\n".join(errors[:30]))
            output = OUTPUT_ROOT / namespace / "lang/ko_kr.json"
            if copy_output:
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(working, output)
            rows.append(
                {
                    "group": target.group,
                    "jar": jar_path.name,
                    "namespace": namespace,
                    "keys": len(english),
                    "class_fallback_keys": len(fallback_values),
                    "output": output.relative_to(PROJECT_ROOT).as_posix(),
                    "validation": "passed",
                }
            )
    return rows


def verify_pack_target(
    instance: Path, target: PackLanguageTarget, copy_output: bool
) -> dict[str, object]:
    """팩의 KubeJS 언어 파일도 JAR 언어 파일과 같은 기준으로 검증한다."""
    english_path = instance / target.relative_dir / "en_us.json"
    english = json.loads(english_path.read_text(encoding="utf-8-sig"))
    working = WORK_ROOT / target.group / target.namespace / "ko_kr.json"
    korean = json.loads(working.read_text(encoding="utf-8"))
    errors = []
    if list(korean) != list(english):
        missing = sorted(set(english) - set(korean))
        extra = sorted(set(korean) - set(english))
        errors.append(f"키 또는 순서 불일치: 누락={missing}, 초과={extra}")
    for key in english.keys() & korean.keys():
        validate_value(key, english[key], korean[key], errors)
    if working.read_bytes().startswith(b"\xef\xbb\xbf"):
        errors.append("UTF-8 BOM이 있습니다")
    if errors:
        raise RuntimeError(f"{target.namespace} 검증 실패:\n" + "\n".join(errors[:30]))
    output = OUTPUT_ROOT / target.namespace / "lang/ko_kr.json"
    if copy_output:
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(working, output)
    return {
        "group": target.group,
        "source": target.relative_dir,
        "namespace": target.namespace,
        "keys": len(english),
        "output": output.relative_to(PROJECT_ROOT).as_posix(),
        "validation": "passed",
    }


def verify_jei_related(instance: Path) -> dict[str, object]:
    """JEI가 직접 언급되는 퀘스트와 KubeJS 표시 경로를 검증한다."""
    source_lang = instance / "config/ftbquests/quests/lang/en_us.snbt"
    output_lang = (
        PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
    )
    english = parse_language_snbt(source_lang)
    korean = parse_language_snbt(output_lang)
    related_keys = {
        key for key, value in english.items() if "jei" in flatten(value).lower()
    }
    errors = []
    if len(related_keys) != 25:
        errors.append(f"JEI 관련 FTB Quests 키 수 불일치: {len(related_keys)}")
    missing = sorted(related_keys - set(korean))
    if missing:
        errors.append(f"JEI 관련 FTB Quests 한국어 누락: {missing}")
    lost_name = sorted(
        key
        for key in related_keys & set(korean)
        if "jei" not in flatten(korean[key]).lower()
    )
    if lost_name:
        errors.append(f"JEI 관련 퀘스트에서 모드명 누락: {lost_name}")
    inconsistent_terms = sorted(
        key
        for key in JEI_QUEST_TERM_KEYS
        if key not in korean
        or re.search(r"조합법|레시피", flatten(korean[key])) is not None
    )
    if inconsistent_terms:
        errors.append(f"JEI 관련 퀘스트 제작법 용어 불일치: {inconsistent_terms}")
    working_mismatches = []
    for key, relative in JEI_QUEST_WORKING_FILES.items():
        values = json.loads((PROJECT_ROOT / relative).read_text(encoding="utf-8"))
        if key not in values or flatten(values[key]) != flatten(korean[key]):
            working_mismatches.append(relative.as_posix())
    if working_mismatches:
        errors.append(f"JEI 관련 퀘스트 작업본 불일치: {working_mismatches}")
    jei_overrides = json.loads(JEI_QUEST_OVERRIDES.read_text(encoding="utf-8"))
    if set(jei_overrides) != JEI_QUEST_TERM_KEYS:
        errors.append("JEI 관련 퀘스트 전용 override 키 범위가 다릅니다")
    override_mismatches = sorted(
        key
        for key in set(jei_overrides) & set(korean)
        if flatten(jei_overrides[key]) != flatten(korean[key])
    )
    if override_mismatches:
        errors.append(f"JEI 관련 퀘스트 전용 override 불일치: {override_mismatches}")

    source_script = instance / JEI_KUBEJS_RELATIVE
    output_script = PROJECT_ROOT / "output/overrides" / JEI_KUBEJS_RELATIVE
    source_text = source_script.read_text(encoding="utf-8")
    output_text = output_script.read_text(encoding="utf-8")
    if source_text.count(JEI_KUBEJS_ENGLISH) == 1:
        expected_text = source_text.replace(JEI_KUBEJS_ENGLISH, JEI_KUBEJS_KOREAN)
    elif source_text.count(JEI_KUBEJS_KOREAN) == 1:
        expected_text = source_text
    else:
        expected_text = ""
        errors.append("JEI KubeJS 원문 표시 문자열을 하나로 확정하지 못했습니다")
    if output_text != expected_text:
        errors.append("JEI KubeJS override가 계획한 한 문자열 변경과 다릅니다")
    mi_output = json.loads(
        (OUTPUT_ROOT / "modern_industrialization/lang/ko_kr.json").read_text(
            encoding="utf-8"
        )
    )
    mi_related_keys = {
        "modern_industrialization.configuration.missingRecipeViewerMessage",
        "modern_industrialization.configuration.missingRecipeViewerMessage.tooltip",
        "text.modern_industrialization.NoEmi",
    }
    mi_missing = sorted(mi_related_keys - set(mi_output))
    if mi_missing:
        errors.append(f"KubeJS 제작법 뷰어 연동 언어 키 누락: {mi_missing}")
    mi_inconsistent = sorted(
        key
        for key in mi_related_keys & set(mi_output)
        if re.search(r"조합법|레시피", str(mi_output[key])) is not None
    )
    if mi_inconsistent:
        errors.append(f"KubeJS 제작법 뷰어 용어 불일치: {mi_inconsistent}")

    jei_target = next(
        target
        for target in TARGETS
        if target.group == "jei" and target.namespaces == ("jei",)
    )
    jar_path = find_jar(instance, jei_target)
    with ZipFile(jar_path) as archive:
        names = archive.namelist()
        class_files = sum(name.endswith(".class") for name in names)
        guide_files = sum(
            marker in name.lower()
            for name in names
            for marker in ("patchouli", "guideme", "modonomicon")
        )
        advancement_files = sum(
            name.endswith(".json") and "/advancement" in name for name in names
        )
    if errors:
        raise RuntimeError("JEI 연관 경로 검증 실패:\n" + "\n".join(errors))
    return {
        "group": "jei",
        "namespace": "jei_related_paths",
        "source_jar_sha256": hashlib.sha256(jar_path.read_bytes()).hexdigest(),
        "class_files_reviewed": class_files,
        "ftbquests_keys_reviewed": len(related_keys),
        "ftbquests_terms_corrected": len(JEI_QUEST_TERM_KEYS),
        "kubejs_files_reviewed": 4,
        "kubejs_display_values_reviewed": 4,
        "kubejs_display_values_retained": 3,
        "kubejs_display_literals_corrected": 1,
        "guide_files": guide_files,
        "advancement_files": advancement_files,
        "validation": "passed",
    }


def verify_jade_related(instance: Path) -> dict[str, object]:
    """Jade 본체 밖의 실제 표시 경로와 연동 키 소유 범위를 검증한다."""
    errors = []
    output_path = OUTPUT_ROOT / "jade/lang/ko_kr.json"
    korean = json.loads(output_path.read_text(encoding="utf-8"))
    mismatches = sorted(
        key
        for key, expected in JADE_RECHECK_VALUES.items()
        if korean.get(key) != expected
    )
    if mismatches:
        errors.append(f"Jade 확정 교정값 불일치: {mismatches}")

    source_lang = instance / "config/ftbquests/quests/lang/en_us.snbt"
    quests = parse_language_snbt(source_lang)
    quest_refs = sorted(
        key
        for key, value in quests.items()
        if re.search(r"(?i)\b(?:jade|waila|hwyla)\b", flatten(value))
    )
    if quest_refs:
        errors.append(f"예상하지 않은 Jade 관련 FTB Quests 키: {quest_refs}")

    kubejs_language: dict[str, str] = {}
    for path in sorted((instance / "kubejs").rglob("en_us.json")):
        values = json.loads(path.read_text(encoding="utf-8-sig"))
        for key, value in values.items():
            if key.startswith(JADE_LANGUAGE_PREFIXES):
                kubejs_language[key] = value
    if kubejs_language != JADE_KUBEJS_LANGUAGE:
        errors.append(f"KubeJS Jade 언어 키 범위 불일치: {kubejs_language}")

    mi_output = json.loads(
        (OUTPUT_ROOT / "modern_industrialization/lang/ko_kr.json").read_text(
            encoding="utf-8"
        )
    )
    mi_working = json.loads(
        (
            PROJECT_ROOT
            / "working/modern_industrialization/modern_industrialization/ko_kr.json"
        ).read_text(encoding="utf-8")
    )
    for key, expected in JADE_KUBEJS_KOREAN.items():
        if mi_output.get(key) != expected or mi_working.get(key) != expected:
            errors.append(f"KubeJS Jade 연동 번역 불일치: {key}")

    kubejs_script_refs = []
    for path in sorted((instance / "kubejs").rglob("*.js")):
        for number, line in enumerate(
            path.read_text(encoding="utf-8-sig").splitlines(), start=1
        ):
            if re.search(r"(?i)\b(?:jade|waila|hwyla)\b", line):
                kubejs_script_refs.append(
                    f"{path.relative_to(instance).as_posix()}:{number}"
                )
    expected_script_ref = ["kubejs/server_scripts/mods/Minecolonies/tags.js:228"]
    if kubejs_script_refs != expected_script_ref:
        errors.append(f"KubeJS Jade 스크립트 참조 불일치: {kubejs_script_refs}")

    related_language_files = 0
    related_owned_keys = 0
    missing_owned_keys = []
    mods_root = instance / "mods"
    jade_target = next(target for target in TARGETS if target.group == "jade")
    jade_jar = find_jar(instance, jade_target)
    for jar_path in sorted(mods_root.glob("*.jar")):
        if jar_path == jade_jar:
            continue
        with ZipFile(jar_path) as archive:
            for name in archive.namelist():
                if not re.fullmatch(r"assets/[^/]+/lang/en_us\.json", name):
                    continue
                values = load_json(archive, name)
                keys = sorted(
                    key for key in values if key.startswith(JADE_LANGUAGE_PREFIXES)
                )
                if not keys:
                    continue
                related_language_files += 1
                related_owned_keys += len(keys)
                namespace = name.split("/")[1]
                related_output = OUTPUT_ROOT / namespace / "lang/ko_kr.json"
                translated = (
                    json.loads(related_output.read_text(encoding="utf-8"))
                    if related_output.is_file()
                    else {}
                )
                missing_owned_keys.extend(
                    f"{namespace}:{key}" for key in keys if key not in translated
                )
    if (related_language_files, related_owned_keys) != (51, 199):
        errors.append(
            "다른 모드 소유 Jade 연동 범위 불일치: "
            f"파일={related_language_files}, 키={related_owned_keys}"
        )

    with ZipFile(jade_jar) as archive:
        names = archive.namelist()
        english = load_json(archive, "assets/jade/lang/en_us.json")
    collisions: dict[str, set[str]] = {}
    for key, value in korean.items():
        collisions.setdefault(str(value), set()).add(str(english[key]))
    collisions = {
        value: source_values
        for value, source_values in collisions.items()
        if len(source_values) > 1
    }
    expected_collisions = {"위": {"Top", "Up"}}
    if collisions != expected_collisions:
        errors.append(f"Jade 번역 유발 이름 충돌 불일치: {collisions}")

    class_files = sum(name.endswith(".class") for name in names)
    json_files = sum(name.endswith(".json") for name in names)
    advancement_files = sum(
        name.endswith(".json") and "/advancement" in name.lower() for name in names
    )
    recipe_files = sum(
        name.endswith(".json") and "/recipe" in name.lower() for name in names
    )
    guide_files = sum(
        any(
            marker in name.lower() for marker in ("patchouli", "guideme", "modonomicon")
        )
        for name in names
    )
    screen_json_files = sum(
        name.endswith(".json") and "screen" in name.lower() for name in names
    )
    if (class_files, json_files, advancement_files, recipe_files, guide_files) != (
        301,
        18,
        0,
        0,
        0,
    ):
        errors.append("Jade JAR 표시 경로 인벤토리가 달라졌습니다")
    if screen_json_files:
        errors.append(f"Jade 화면 JSON을 추가 검수해야 합니다: {screen_json_files}")
    if errors:
        raise RuntimeError("Jade 연관 경로 검증 실패:\n" + "\n".join(errors))
    return {
        "group": "jade",
        "namespace": "jade_related_paths",
        "source_jar_sha256": hashlib.sha256(jade_jar.read_bytes()).hexdigest(),
        "class_files_reviewed": class_files,
        "ftbquests_keys_reviewed": len(quest_refs),
        "kubejs_language_values_reviewed": len(kubejs_language),
        "kubejs_script_references_reviewed": len(kubejs_script_refs),
        "other_mod_language_files_traced": related_language_files,
        "other_mod_owned_keys_traced": related_owned_keys,
        "other_mod_owned_missing_keys_deferred": len(missing_owned_keys),
        "translation_induced_name_collisions": 0,
        "direction_label_collisions_retained": len(collisions),
        "advancement_files": advancement_files,
        "recipe_files": recipe_files,
        "guide_files": guide_files,
        "screen_json_files": screen_json_files,
        "validation": "passed",
    }


def verify_journeymap_related(instance: Path) -> dict[str, object]:
    """JourneyMap의 fallback, 연동 언어와 JAR 내부 표시 경로를 검증한다."""
    errors = []
    output_path = OUTPUT_ROOT / "journeymap/lang/ko_kr.json"
    korean = json.loads(output_path.read_text(encoding="utf-8"))
    mismatches = sorted(
        key
        for key, expected in JOURNEYMAP_RECHECK_VALUES.items()
        if korean.get(key) != expected
    )
    if mismatches:
        errors.append(f"JourneyMap 확정 교정값 불일치: {mismatches}")
    fallback_mismatches = sorted(
        key
        for key, expected in JOURNEYMAP_CLASS_FALLBACKS.items()
        if korean.get(key) != expected
    )
    if fallback_mismatches:
        errors.append(f"JourneyMap 클래스 fallback 불일치: {fallback_mismatches}")
    forbidden = sorted(
        key
        for key, value in korean.items()
        if JOURNEYMAP_FORBIDDEN_TERMS.search(str(value))
    )
    if forbidden:
        errors.append(f"JourneyMap 금지·충돌 용어 잔존: {forbidden}")

    source_lang = instance / "config/ftbquests/quests/lang/en_us.snbt"
    quests = parse_language_snbt(source_lang)
    quest_journeymap_refs = sorted(
        key
        for key, value in quests.items()
        if re.search(r"(?i)journeymap", flatten(value))
    )
    quest_waypoint_refs = sorted(
        key
        for key, value in quests.items()
        if re.search(r"(?i)\bwaypoints?\b", flatten(value))
    )
    if quest_journeymap_refs or quest_waypoint_refs:
        errors.append(
            "예상하지 않은 JourneyMap 관련 FTB Quests 키: "
            f"모드명={quest_journeymap_refs}, 웨이포인트={quest_waypoint_refs}"
        )

    kubejs_files_reviewed = 0
    kubejs_refs = []
    kubejs_root = instance / "kubejs"
    for path in sorted(kubejs_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".js",
            ".json",
            ".snbt",
            ".txt",
        }:
            continue
        kubejs_files_reviewed += 1
        text = path.read_text(encoding="utf-8-sig")
        if re.search(r"(?i)journeymap|\bwaypoints?\b", text):
            kubejs_refs.append(path.relative_to(instance).as_posix())
    if kubejs_refs:
        errors.append(f"예상하지 않은 JourneyMap KubeJS 참조: {kubejs_refs}")

    journey_target = next(
        target
        for target in TARGETS
        if target.group == "map_team" and target.namespaces == ("journeymap",)
    )
    journey_jar = find_jar(instance, journey_target)
    with ZipFile(journey_jar) as archive:
        names = archive.namelist()
        english = load_json(archive, "assets/journeymap/lang/en_us.json")
        editor_popup = archive.read(
            "journeymap/client/ui/waypointmanager/waypoint/EditorOptionsPopup.class"
        )
        waypoint_editor = archive.read(
            "journeymap/client/ui/waypointmanager/waypoint/WaypointEditor.class"
        )
        teleport = archive.read("journeymap/common/util/JourneyMapTeleport.class")
        packet_handler = archive.read(
            "journeymap/common/network/handler/PacketHandler.class"
        )
        class_files = [name for name in names if name.endswith(".class")]
        json_files = [name for name in names if name.endswith(".json")]
        language_files = [name for name in json_files if "/lang/" in name]
        advancement_files = [
            name for name in json_files if "/advancement" in name.lower()
        ]
        recipe_files = [name for name in json_files if "/recipe" in name.lower()]
        guide_files = [
            name
            for name in names
            if any(
                marker in name.lower()
                for marker in ("patchouli", "guideme", "modonomicon")
            )
        ]
        screen_json_files = [name for name in json_files if "screen" in name.lower()]
        translation_api_classes = sum(
            b"literal" in archive.read(name) or b"translatable" in archive.read(name)
            for name in class_files
        )

    if b"Waypoint Editor Options" not in editor_popup:
        errors.append("JourneyMap 편집기 제목 fallback 원문을 찾지 못했습니다")
    hardcoded_markers = {
        "waypoint_editor": (waypoint_editor, (b"On", b"Off")),
        "teleport": (
            teleport,
            (
                b"Cannot Find World",
                b"Cannot teleport when dead.",
                b"Could not get world for Dimension",
                b"Server has disabled JourneyMap teleport usage",
                b"Server disabled cross dimension teleport.",
            ),
        ),
        "permission": (
            packet_handler,
            (b"You do not have permission to modify Journeymap",),
        ),
    }
    missing_class_markers = sorted(
        f"{scope}:{marker.decode('utf-8')}"
        for scope, (class_data, markers) in hardcoded_markers.items()
        for marker in markers
        if marker not in class_data
    )
    if missing_class_markers:
        errors.append(
            f"JourneyMap 클래스 표시 문자열 범위 변경: {missing_class_markers}"
        )
    if (
        len(class_files),
        len(json_files),
        len(language_files),
        len(advancement_files),
        len(recipe_files),
        len(guide_files),
        len(screen_json_files),
        translation_api_classes,
    ) != (858, 43, 30, 0, 0, 0, 0, 90):
        errors.append("JourneyMap JAR 표시 경로 인벤토리가 달라졌습니다")

    collisions: dict[str, set[str]] = {}
    for key, value in korean.items():
        if key in english:
            collisions.setdefault(str(value), set()).add(str(english[key]))
    collisions = {
        value: source_values
        for value, source_values in collisions.items()
        if len(source_values) > 1
    }

    other_language_files = 0
    other_owned_keys = 0
    other_missing_keys = []
    other_term_conflicts = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        if jar_path == journey_jar:
            continue
        with ZipFile(jar_path) as archive:
            for name in archive.namelist():
                if not re.fullmatch(r"assets/[^/]+/lang/en_us\.json", name):
                    continue
                values = load_json(archive, name)
                related = {
                    key: value
                    for key, value in values.items()
                    if JOURNEYMAP_RELATED_LANGUAGE.search(key)
                    or JOURNEYMAP_RELATED_LANGUAGE.search(str(value))
                }
                if not related:
                    continue
                other_language_files += 1
                other_owned_keys += len(related)
                namespace = name.split("/")[1]
                related_output = OUTPUT_ROOT / namespace / "lang/ko_kr.json"
                translated = (
                    json.loads(related_output.read_text(encoding="utf-8"))
                    if related_output.is_file()
                    else {}
                )
                for key in related:
                    if key not in translated:
                        other_missing_keys.append(f"{namespace}:{key}")
                    elif JOURNEYMAP_OTHER_OWNER_CONFLICTS.search(str(translated[key])):
                        other_term_conflicts.append(f"{namespace}:{key}")
    if (other_language_files, other_owned_keys) != (4, 81):
        errors.append(
            "다른 모드 소유 JourneyMap·웨이포인트 연동 범위 불일치: "
            f"파일={other_language_files}, 키={other_owned_keys}"
        )
    if other_missing_keys:
        errors.append(f"다른 모드 소유 연동 번역 누락: {other_missing_keys}")

    if errors:
        raise RuntimeError("JourneyMap 연관 경로 검증 실패:\n" + "\n".join(errors))
    return {
        "group": "map_team",
        "namespace": "journeymap_related_paths",
        "source_jar_sha256": hashlib.sha256(journey_jar.read_bytes()).hexdigest(),
        "class_files_reviewed": len(class_files),
        "class_translation_api_classes_reviewed": translation_api_classes,
        "class_fallback_literals_translated": len(JOURNEYMAP_CLASS_FALLBACKS),
        "class_hardcoded_display_literals_deferred": sum(
            len(markers) for _, markers in hardcoded_markers.values()
        ),
        "ftbquests_journeymap_keys_reviewed": len(quest_journeymap_refs),
        "ftbquests_waypoint_keys_reviewed": len(quest_waypoint_refs),
        "kubejs_files_reviewed": kubejs_files_reviewed,
        "kubejs_references_reviewed": len(kubejs_refs),
        "other_mod_language_files_traced": other_language_files,
        "other_mod_owned_keys_traced": other_owned_keys,
        "other_mod_owned_term_conflicts_deferred": len(other_term_conflicts),
        "translation_induced_collisions_reviewed": len(collisions),
        "harmful_translation_induced_collisions": 0,
        "advancement_files": len(advancement_files),
        "recipe_files": len(recipe_files),
        "guide_files": len(guide_files),
        "screen_json_files": len(screen_json_files),
        "validation": "passed",
    }


def verify_ftbchunks_related(instance: Path) -> dict[str, object]:
    """FTB Chunks의 fallback, 연동 문구와 JAR 표시 경로를 검증한다."""
    errors = []
    output_path = OUTPUT_ROOT / "ftbchunks/lang/ko_kr.json"
    korean = json.loads(output_path.read_text(encoding="utf-8"))
    mismatches = sorted(
        key
        for key, expected in FTBCHUNKS_RECHECK_VALUES.items()
        if korean.get(key) != expected
    )
    if mismatches:
        errors.append(f"FTB Chunks 확정 교정값 불일치: {mismatches}")
    fallback_mismatches = sorted(
        key
        for key, expected in FTBCHUNKS_CLASS_FALLBACKS.items()
        if korean.get(key) != expected
    )
    if fallback_mismatches:
        errors.append(f"FTB Chunks 클래스 fallback 불일치: {fallback_mismatches}")
    forbidden = sorted(
        key
        for key, value in korean.items()
        if FTBCHUNKS_FORBIDDEN_TERMS.search(str(value))
    )
    if forbidden:
        errors.append(f"FTB Chunks 금지·충돌 용어 잔존: {forbidden}")

    source_lang = instance / "config/ftbquests/quests/lang/en_us.snbt"
    source_quests = parse_language_snbt(source_lang)
    related_quest_keys = sorted(
        key
        for key, value in source_quests.items()
        if re.search(
            r"(?i)\b(?:claim(?:ed|ing)?|force[- ]?load(?:ed|ing)?) chunks?\b",
            flatten(value),
        )
    )
    if related_quest_keys != sorted(FTBCHUNKS_QUEST_VALUES):
        errors.append(f"FTB Chunks 관련 퀘스트 범위 변경: {related_quest_keys}")
    quest_output = parse_language_snbt(
        PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
    )
    quest_mismatches = sorted(
        key
        for key, expected in FTBCHUNKS_QUEST_VALUES.items()
        if quest_output.get(key) != expected
    )
    if quest_mismatches:
        errors.append(f"FTB Chunks 관련 퀘스트 번역 불일치: {quest_mismatches}")
    quest_working = json.loads(
        (PROJECT_ROOT / "working/ftbquests/common_chapter_overrides.json").read_text(
            encoding="utf-8"
        )
    )
    working_quest_mismatches = sorted(
        key
        for key, expected in FTBCHUNKS_QUEST_VALUES.items()
        if quest_working.get(key) != expected
    )
    if working_quest_mismatches:
        errors.append(
            "FTB Chunks 관련 퀘스트 작업본 불일치: " f"{working_quest_mismatches}"
        )

    kubejs_files_reviewed = 0
    kubejs_refs = []
    kubejs_root = instance / "kubejs"
    for path in sorted(kubejs_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".js",
            ".json",
            ".snbt",
            ".txt",
        }:
            continue
        kubejs_files_reviewed += 1
        text = path.read_text(encoding="utf-8-sig")
        if re.search(
            r"(?i)ftb.?chunks|\b(?:claim(?:ed|ing)?|"
            r"force[- ]?load(?:ed|ing)?) chunks?\b",
            text,
        ):
            kubejs_refs.append(path.relative_to(instance).as_posix())
    if set(kubejs_refs) != FTBCHUNKS_KUBEJS_REFERENCES:
        errors.append(f"FTB Chunks KubeJS 참조 범위 변경: {kubejs_refs}")

    chunks_target = next(
        target
        for target in TARGETS
        if target.group == "map_team" and target.namespaces == ("ftbchunks",)
    )
    chunks_jar = find_jar(instance, chunks_target)
    other_language_files = 0
    other_owned_keys = 0
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        if jar_path == chunks_jar:
            continue
        with ZipFile(jar_path) as archive:
            for name in archive.namelist():
                if not re.fullmatch(r"assets/[^/]+/lang/en_us\.json", name):
                    continue
                values = load_json(archive, name)
                related = {
                    key: value
                    for key, value in values.items()
                    if re.search(r"(?i)ftb.?chunks", f"{key} {value}")
                }
                if related:
                    other_language_files += 1
                    other_owned_keys += len(related)
    if other_language_files or other_owned_keys:
        errors.append(
            "예상하지 않은 다른 모드 소유 FTB Chunks 연동 언어: "
            f"파일={other_language_files}, 키={other_owned_keys}"
        )

    teams_output = json.loads(
        (OUTPUT_ROOT / "ftbteams/lang/ko_kr.json").read_text(encoding="utf-8")
    )
    if "ftbteams.team_not_found" not in teams_output:
        errors.append("FTB Teams 의존 오류 메시지 번역이 없습니다")

    with ZipFile(chunks_jar) as archive:
        names = archive.namelist()
        english = load_json(archive, "assets/ftbchunks/lang/en_us.json")
        class_files = [name for name in names if name.endswith(".class")]
        json_files = [name for name in names if name.endswith(".json")]
        language_files = [name for name in json_files if "/lang/" in name]
        advancement_files = [
            name for name in json_files if "/advancement" in name.lower()
        ]
        recipe_files = [name for name in json_files if "/recipe" in name.lower()]
        guide_files = [
            name
            for name in names
            if any(
                marker in name.lower()
                for marker in ("patchouli", "guideme", "modonomicon")
            )
        ]
        sidebar_files = [name for name in json_files if "/sidebar_buttons/" in name]
        block_color_files = [
            name for name in json_files if name.endswith("ftbchunks_block_colors.json")
        ]
        tag_files = [name for name in json_files if "/tags/" in name]
        translation_api_classes = sum(
            b"literal" in archive.read(name) or b"translatable" in archive.read(name)
            for name in class_files
        )
        commands_class = archive.read("dev/ftb/mods/ftbchunks/FTBChunksCommands.class")
        entity_row_class = archive.read(
            "dev/ftb/mods/ftbchunks/client/gui/"
            "EntityIconSettingsScreen$RowPanel.class"
        )
        hardcoded_markers = {
            "commands": (commands_class, (b"Not on a dedicted server!",)),
            "client": (
                archive.read("dev/ftb/mods/ftbchunks/client/FTBChunksClient.class"),
                (b"Click to copy", b"Transient Dev-Mode Waypoint", b"Death #"),
            ),
            "relative_time": (
                archive.read(
                    "dev/ftb/mods/ftbchunks/client/gui/"
                    "ChunkScreenPanel$ChunkButton.class"
                ),
                (b" ago", b" from now"),
            ),
            "slice_editor": (
                archive.read(
                    "dev/ftb/mods/ftbchunks/client/gui/SliceCreationGUI.class"
                ),
                (
                    b"Add Slice",
                    b"Remove Slice",
                    b"Next Slice",
                    b"Previous Slice",
                    b"Export",
                    b"Saved File",
                ),
            ),
            "debug": (
                archive.read(
                    "dev/ftb/mods/ftbchunks/client/minimap/components/"
                    "DebugComponent.class"
                ),
                (b"TQ: ", b"Rgn: ", b"Mem: ~", b"Updates: ", b"Last: %,d ns"),
            ),
            "claim_result": (
                archive.read("dev/ftb/mods/ftbchunks/data/ClaimedChunkImpl.class"),
                (b"OK",),
            ),
        }

    fallback_class_markers = {
        "ftbchunks.command.unloaded": commands_class,
        "ftbchunks.gui.open_creation_gui": entity_row_class,
    }
    missing_fallback_markers = sorted(
        key
        for key, class_data in fallback_class_markers.items()
        if key.encode() not in class_data
    )
    if missing_fallback_markers:
        errors.append(
            f"FTB Chunks 클래스 fallback 호출 변경: {missing_fallback_markers}"
        )
    missing_hardcoded_markers = sorted(
        f"{scope}:{marker.decode('utf-8')}"
        for scope, (class_data, markers) in hardcoded_markers.items()
        for marker in markers
        if marker not in class_data
    )
    if missing_hardcoded_markers:
        errors.append(
            f"FTB Chunks 클래스 직접 표시 문자열 범위 변경: {missing_hardcoded_markers}"
        )
    inventory = (
        len(names),
        len(class_files),
        len(json_files),
        len(language_files),
        len(advancement_files),
        len(recipe_files),
        len(guide_files),
        len(sidebar_files),
        len(block_color_files),
        len(tag_files),
        translation_api_classes,
    )
    if inventory != (370, 238, 38, 9, 0, 0, 0, 2, 19, 6, 54):
        errors.append(f"FTB Chunks JAR 표시 경로 인벤토리 변경: {inventory}")

    spacing_mismatches = []
    for key, english_value in english.items():
        korean_value = korean.get(key)
        if not isinstance(english_value, str) or not isinstance(korean_value, str):
            continue
        english_edges = (
            english_value[: len(english_value) - len(english_value.lstrip())],
            english_value[len(english_value.rstrip()) :],
        )
        korean_edges = (
            korean_value[: len(korean_value) - len(korean_value.lstrip())],
            korean_value[len(korean_value.rstrip()) :],
        )
        if english_edges != korean_edges:
            spacing_mismatches.append(key)
    if spacing_mismatches:
        errors.append(f"FTB Chunks 앞뒤 공백 불일치: {spacing_mismatches}")

    collisions: dict[str, set[str]] = {}
    for key, english_value in english.items():
        collisions.setdefault(str(korean[key]), set()).add(str(english_value))
    collisions = {
        value: source_values
        for value, source_values in collisions.items()
        if len(source_values) > 1
    }
    if collisions:
        errors.append(f"FTB Chunks 번역 유발 명칭 충돌: {collisions}")

    if errors:
        raise RuntimeError("FTB Chunks 연관 경로 검증 실패:\n" + "\n".join(errors))
    return {
        "group": "map_team",
        "namespace": "ftbchunks_related_paths",
        "source_jar_sha256": hashlib.sha256(chunks_jar.read_bytes()).hexdigest(),
        "class_files_reviewed": len(class_files),
        "class_translation_api_classes_reviewed": translation_api_classes,
        "class_fallback_literals_translated": len(FTBCHUNKS_CLASS_FALLBACKS),
        "class_hardcoded_display_literals_deferred": sum(
            len(markers) for _, markers in hardcoded_markers.values()
        ),
        "ftbquests_keys_reviewed": len(related_quest_keys),
        "kubejs_files_reviewed": kubejs_files_reviewed,
        "kubejs_technical_references_reviewed": len(kubejs_refs),
        "other_mod_language_files_traced": other_language_files,
        "other_mod_owned_keys_traced": other_owned_keys,
        "ftbteams_dependency_keys_traced": 1,
        "translation_induced_collisions_reviewed": len(collisions),
        "harmful_translation_induced_collisions": 0,
        "advancement_files": len(advancement_files),
        "recipe_files": len(recipe_files),
        "guide_files": len(guide_files),
        "sidebar_json_files": len(sidebar_files),
        "block_color_json_files": len(block_color_files),
        "tag_json_files": len(tag_files),
        "validation": "passed",
    }


def verify_ftbteams_related(instance: Path) -> dict[str, object]:
    """FTB Teams의 fallback, 연동 문구와 JAR 표시 경로를 검증한다."""
    errors = []
    output_path = OUTPUT_ROOT / "ftbteams/lang/ko_kr.json"
    korean = json.loads(output_path.read_text(encoding="utf-8"))
    mismatches = sorted(
        key
        for key, expected in FTBTEAMS_RECHECK_VALUES.items()
        if korean.get(key) != expected
    )
    if mismatches:
        errors.append(f"FTB Teams 확정 교정값 불일치: {mismatches}")
    fallback_mismatches = sorted(
        key
        for key, expected in FTBTEAMS_CLASS_FALLBACKS.items()
        if korean.get(key) != expected
    )
    if fallback_mismatches:
        errors.append(f"FTB Teams 표시 fallback 불일치: {fallback_mismatches}")
    forbidden = sorted(
        key
        for key, value in korean.items()
        if FTBTEAMS_FORBIDDEN_TERMS.search(str(value))
    )
    if forbidden:
        errors.append(f"FTB Teams 금지·충돌 용어 잔존: {forbidden}")

    source_lang = instance / "config/ftbquests/quests/lang/en_us.snbt"
    source_quests = parse_language_snbt(source_lang)
    related_quest_keys = sorted(
        key
        for key, value in source_quests.items()
        if re.search(r"(?i)ftb.?teams", flatten(value))
    )
    if related_quest_keys != sorted(FTBTEAMS_QUEST_VALUES):
        errors.append(f"FTB Teams 관련 퀘스트 범위 변경: {related_quest_keys}")
    quest_output = parse_language_snbt(
        PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
    )
    quest_mismatches = sorted(
        key
        for key, expected in FTBTEAMS_QUEST_VALUES.items()
        if quest_output.get(key) != expected
    )
    if quest_mismatches:
        errors.append(f"FTB Teams 관련 퀘스트 번역 불일치: {quest_mismatches}")
    quest_working = json.loads(
        (PROJECT_ROOT / "working/ftbquests/common_chapter_overrides.json").read_text(
            encoding="utf-8"
        )
    )
    working_quest_mismatches = sorted(
        key
        for key, expected in FTBTEAMS_QUEST_VALUES.items()
        if quest_working.get(key) != expected
    )
    if working_quest_mismatches:
        errors.append(
            "FTB Teams 관련 퀘스트 작업본 불일치: " f"{working_quest_mismatches}"
        )

    kubejs_files_reviewed = 0
    kubejs_refs = []
    kubejs_root = instance / "kubejs"
    for path in sorted(kubejs_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".js",
            ".json",
            ".snbt",
            ".txt",
        }:
            continue
        kubejs_files_reviewed += 1
        text = path.read_text(encoding="utf-8-sig")
        if re.search(r"(?i)ftb.?teams", text):
            kubejs_refs.append(path.relative_to(instance).as_posix())
    if kubejs_refs:
        errors.append(f"예상하지 않은 FTB Teams KubeJS 참조: {kubejs_refs}")

    teams_target = next(
        target
        for target in TARGETS
        if target.group == "map_team" and target.namespaces == ("ftbteams",)
    )
    teams_jar = find_jar(instance, teams_target)
    other_language_files = 0
    other_owned_keys = 0
    other_missing_keys = []
    other_term_conflicts = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        if jar_path == teams_jar:
            continue
        with ZipFile(jar_path) as archive:
            for name in archive.namelist():
                if not re.fullmatch(r"assets/[^/]+/lang/en_us\.json", name):
                    continue
                values = load_json(archive, name)
                related = {
                    key: value
                    for key, value in values.items()
                    if FTBTEAMS_RELATED_LANGUAGE.search(f"{key} {value}")
                }
                if not related:
                    continue
                other_language_files += 1
                other_owned_keys += len(related)
                namespace = name.split("/")[1]
                related_output = OUTPUT_ROOT / namespace / "lang/ko_kr.json"
                translated = (
                    json.loads(related_output.read_text(encoding="utf-8"))
                    if related_output.is_file()
                    else {}
                )
                for key in related:
                    marker = f"{namespace}:{key}"
                    if key not in translated:
                        other_missing_keys.append(marker)
                    elif re.search(r"FTB 팀", str(translated[key])):
                        other_term_conflicts.append(marker)
    if (other_language_files, other_owned_keys) != (4, 36):
        errors.append(
            "다른 모드 소유 FTB Teams 연동 범위 불일치: "
            f"파일={other_language_files}, 키={other_owned_keys}"
        )
    if other_missing_keys:
        errors.append(f"다른 모드 소유 FTB Teams 연동 번역 누락: {other_missing_keys}")
    if set(other_term_conflicts) != FTBTEAMS_OTHER_OWNER_CONFLICTS:
        errors.append(
            "다른 모드 소유 FTB Teams 용어 충돌 범위 변경: " f"{other_term_conflicts}"
        )

    with ZipFile(teams_jar) as archive:
        names = archive.namelist()
        english = load_json(archive, "assets/ftbteams/lang/en_us.json")
        class_files = [name for name in names if name.endswith(".class")]
        json_files = [name for name in names if name.endswith(".json")]
        language_files = [name for name in json_files if "/lang/" in name]
        advancement_files = [
            name for name in json_files if "/advancement" in name.lower()
        ]
        recipe_files = [name for name in json_files if "/recipe" in name.lower()]
        guide_files = [
            name
            for name in names
            if any(
                marker in name.lower()
                for marker in ("patchouli", "guideme", "modonomicon")
            )
        ]
        sidebar_files = [name for name in json_files if "/sidebar_buttons/" in name]
        translation_api_classes = sum(
            b"literal" in archive.read(name) or b"translatable" in archive.read(name)
            for name in class_files
        )
        client_manager = archive.read(
            "dev/ftb/mods/ftbteams/data/ClientTeamManagerImpl.class"
        )
        commands = archive.read("dev/ftb/mods/ftbteams/data/FTBTeamsCommands.class")
        party_team = archive.read("dev/ftb/mods/ftbteams/data/PartyTeam.class")
        utils = archive.read("dev/ftb/mods/ftbteams/data/FTBTUtils.class")

    expected_sidebar_files = {
        "assets/ftbteams/sidebar_buttons/my_team.json",
        "assets/ftbteams/sidebar_buttons/team_lives.json",
    }
    if set(sidebar_files) != expected_sidebar_files:
        errors.append(f"FTB Teams 사이드바 표시 경로 변경: {sidebar_files}")
    hardcoded_markers = {
        "client_team_manager": (client_manager, (b"System", b"Unknown")),
        "commands": (
            commands,
            (b"<none>", b"Team Type", b"Owner", b"Members", b"Server ID:"),
        ),
        "party_team": (party_team, (b"Already owner!", b"None", b"Allies:")),
    }
    missing_hardcoded_markers = sorted(
        f"{scope}:{marker.decode('utf-8')}"
        for scope, (class_data, markers) in hardcoded_markers.items()
        for marker in markers
        if marker not in class_data
    )
    if missing_hardcoded_markers:
        errors.append(
            "FTB Teams 클래스 직접 표시 문자열 범위 변경: "
            f"{missing_hardcoded_markers}"
        )
    if b"chat.copy.click" not in utils:
        errors.append("FTB Teams의 Minecraft 복사 도움말 키 호출을 찾지 못했습니다")
    inventory = (
        len(names),
        len(class_files),
        len(json_files),
        len(language_files),
        len(advancement_files),
        len(recipe_files),
        len(guide_files),
        len(sidebar_files),
        translation_api_classes,
    )
    if inventory != (176, 131, 13, 11, 0, 0, 0, 2, 35):
        errors.append(f"FTB Teams JAR 표시 경로 인벤토리 변경: {inventory}")

    spacing_mismatches = []
    for key, english_value in english.items():
        korean_value = korean.get(key)
        if not isinstance(english_value, str) or not isinstance(korean_value, str):
            continue
        english_edges = (
            english_value[: len(english_value) - len(english_value.lstrip())],
            english_value[len(english_value.rstrip()) :],
        )
        korean_edges = (
            korean_value[: len(korean_value) - len(korean_value.lstrip())],
            korean_value[len(korean_value.rstrip()) :],
        )
        if english_edges != korean_edges:
            spacing_mismatches.append(key)
    if spacing_mismatches:
        errors.append(f"FTB Teams 앞뒤 공백 불일치: {spacing_mismatches}")

    collisions: dict[str, set[str]] = {}
    for key, english_value in english.items():
        collisions.setdefault(str(korean[key]), set()).add(str(english_value))
    collisions = {
        value: source_values
        for value, source_values in collisions.items()
        if len(source_values) > 1
    }
    expected_collisions = {"동맹": {"Ally", "Allies"}}
    if collisions != expected_collisions:
        errors.append(f"FTB Teams 번역 유발 명칭 충돌 범위 변경: {collisions}")

    if errors:
        raise RuntimeError("FTB Teams 연관 경로 검증 실패:\n" + "\n".join(errors))
    return {
        "group": "map_team",
        "namespace": "ftbteams_related_paths",
        "source_jar_sha256": hashlib.sha256(teams_jar.read_bytes()).hexdigest(),
        "class_files_reviewed": len(class_files),
        "class_translation_api_classes_reviewed": translation_api_classes,
        "class_hardcoded_display_literals_deferred": sum(
            len(markers) for _, markers in hardcoded_markers.values()
        ),
        "external_minecraft_translation_keys_traced": 1,
        "ftbquests_keys_reviewed": len(related_quest_keys),
        "kubejs_files_reviewed": kubejs_files_reviewed,
        "kubejs_references_reviewed": len(kubejs_refs),
        "other_mod_language_files_traced": other_language_files,
        "other_mod_owned_keys_traced": other_owned_keys,
        "other_mod_owned_term_conflicts_deferred": len(other_term_conflicts),
        "translation_induced_collisions_reviewed": len(collisions),
        "harmful_translation_induced_collisions": 0,
        "advancement_files": len(advancement_files),
        "recipe_files": len(recipe_files),
        "guide_files": len(guide_files),
        "sidebar_json_files": len(sidebar_files),
        "validation": "passed",
    }


def verify_waystones_related(instance: Path) -> dict[str, object]:
    """Waystones의 fallback, 연동 문구와 JAR 표시 경로를 검증한다."""
    errors = []
    output_path = OUTPUT_ROOT / "waystones/lang/ko_kr.json"
    korean = json.loads(output_path.read_text(encoding="utf-8"))
    mismatches = sorted(
        key
        for key, expected in WAYSTONES_RECHECK_VALUES.items()
        if korean.get(key) != expected
    )
    if mismatches:
        errors.append(f"Waystones 확정 교정값 불일치: {mismatches}")
    fallback_mismatches = sorted(
        key
        for key, expected in WAYSTONES_CLASS_FALLBACKS.items()
        if korean.get(key) != expected
    )
    if fallback_mismatches:
        errors.append(f"Waystones 클래스 fallback 불일치: {fallback_mismatches}")
    forbidden = sorted(
        key
        for key, value in korean.items()
        if WAYSTONES_FORBIDDEN_TERMS.search(str(value))
    )
    if forbidden:
        errors.append(f"Waystones 금지·충돌 용어 잔존: {forbidden}")

    source_lang = instance / "config/ftbquests/quests/lang/en_us.snbt"
    source_quests = parse_language_snbt(source_lang)
    related_quest_language_keys = sorted(
        key
        for key, value in source_quests.items()
        if WAYSTONES_RELATED_LANGUAGE.search(flatten(value))
    )
    if related_quest_language_keys:
        errors.append(
            "예상하지 않은 Waystones 관련 FTB Quests 언어 키: "
            f"{related_quest_language_keys}"
        )

    quest_files = sorted((instance / "config/ftbquests/quests").rglob("*.snbt"))
    quest_item_references = {}
    for path in quest_files:
        text = path.read_text(encoding="utf-8-sig")
        item_ids = re.findall(r'id:\s*"waystones:([^"]+)"', text)
        if item_ids:
            quest_item_references[path.relative_to(instance).as_posix()] = item_ids
    expected_quest_item_references = {
        "config/ftbquests/quests/reward_tables/common.snbt": [
            "waystone",
            "warp_plate",
        ]
    }
    if quest_item_references != expected_quest_item_references:
        errors.append(
            "Waystones 관련 FTB Quests 아이템 참조 범위 변경: "
            f"{quest_item_references}"
        )
    reward_item_names = {
        "block.waystones.waystone": "웨이스톤",
        "block.waystones.warp_plate": "워프 플레이트",
    }
    reward_name_mismatches = sorted(
        key
        for key, expected in reward_item_names.items()
        if korean.get(key) != expected
    )
    if reward_name_mismatches:
        errors.append(
            f"Waystones 퀘스트 보상 표시 이름 불일치: {reward_name_mismatches}"
        )

    kubejs_files_reviewed = 0
    kubejs_refs = []
    kubejs_root = instance / "kubejs"
    for path in sorted(kubejs_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".js",
            ".json",
            ".snbt",
            ".txt",
        }:
            continue
        kubejs_files_reviewed += 1
        text = path.read_text(encoding="utf-8-sig")
        if re.search(r"(?i)waystones?", text):
            kubejs_refs.append(path.relative_to(instance).as_posix())
    if set(kubejs_refs) != WAYSTONES_KUBEJS_REFERENCES:
        errors.append(f"Waystones KubeJS 참조 범위 변경: {kubejs_refs}")

    waystones_target = next(
        target
        for target in TARGETS
        if target.group == "compass" and target.namespaces == ("waystones",)
    )
    waystones_jar = find_jar(instance, waystones_target)
    other_language_files = 0
    other_owned_keys = 0
    other_missing_keys = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        if jar_path == waystones_jar:
            continue
        with ZipFile(jar_path) as archive:
            for name in archive.namelist():
                if not re.fullmatch(r"assets/[^/]+/lang/en_us\.json", name):
                    continue
                values = load_json(archive, name)
                related = {
                    key: value
                    for key, value in values.items()
                    if WAYSTONES_RELATED_LANGUAGE.search(f"{key} {value}")
                }
                if not related:
                    continue
                other_language_files += 1
                other_owned_keys += len(related)
                namespace = name.split("/")[1]
                related_output = OUTPUT_ROOT / namespace / "lang/ko_kr.json"
                translated = (
                    json.loads(related_output.read_text(encoding="utf-8"))
                    if related_output.is_file()
                    else {}
                )
                for key in related:
                    if key not in translated:
                        other_missing_keys.append(f"{namespace}:{key}")
    if (other_language_files, other_owned_keys) != (1, 1):
        errors.append(
            "다른 모드 소유 Waystones 연동 범위 불일치: "
            f"파일={other_language_files}, 키={other_owned_keys}"
        )
    if other_missing_keys:
        errors.append(f"다른 모드 소유 Waystones 연동 번역 누락: {other_missing_keys}")

    with ZipFile(waystones_jar) as archive:
        names = archive.namelist()
        english = load_json(archive, "assets/waystones/lang/en_us.json")
        class_files = [name for name in names if name.endswith(".class")]
        json_files = [name for name in names if name.endswith(".json")]
        language_files = [name for name in json_files if "/lang/" in name]
        advancement_files = [
            name
            for name in json_files
            if name.startswith("data/waystones/advancement/")
        ]
        recipe_files = [
            name for name in json_files if name.startswith("data/waystones/recipe/")
        ]
        guide_files = [
            name
            for name in names
            if any(
                marker in name.lower()
                for marker in ("patchouli", "guideme", "modonomicon")
            )
        ]
        display_advancements = [
            name for name in advancement_files if "display" in load_json(archive, name)
        ]
        translation_api_classes = sum(
            b"literal" in archive.read(name) or b"translatable" in archive.read(name)
            for name in class_files
        )
        sharestone_class = archive.read(
            "net/blay09/mods/waystones/block/SharestoneBlock.class"
        )
        visibility_class = archive.read(
            "net/blay09/mods/waystones/client/gui/widget/"
            "WaystoneVisbilityButton.class"
        )
        commands_class = archive.read(
            "net/blay09/mods/waystones/command/ModCommands.class"
        )
        debug_class = archive.read(
            "net/blay09/mods/waystones/handler/WaystoneDebugHandler.class"
        )
        biome_name_class = archive.read(
            "net/blay09/mods/waystones/worldgen/namegen/BiomeNameGenerator.class"
        )

    fallback_class_markers = {
        "tooltip.waystones.sharestone": sharestone_class,
        "tooltip.waystones.visibility": visibility_class,
    }
    missing_fallback_markers = sorted(
        key
        for key, class_data in fallback_class_markers.items()
        if key.encode() not in class_data
    )
    if missing_fallback_markers:
        errors.append(
            f"Waystones 클래스 fallback 호출 변경: {missing_fallback_markers}"
        )
    hardcoded_markers = {
        "commands": (commands_class, (b"Unknown waystone style: \x01",)),
        "debug": (
            debug_class,
            (
                b"Waystone was successfully reset - it will re-initialize once it is next loaded.",
                b"Client UUID: \x01",
                b"Server UUID: \x01",
            ),
        ),
        "biome_name": (biome_name_class, (b"Corrupted Lands",)),
    }
    missing_hardcoded_markers = sorted(
        f"{scope}:{marker.decode('utf-8')}"
        for scope, (class_data, markers) in hardcoded_markers.items()
        for marker in markers
        if marker not in class_data
    )
    if missing_hardcoded_markers:
        errors.append(
            "Waystones 클래스 직접 표시 문자열 범위 변경: "
            f"{missing_hardcoded_markers}"
        )
    inventory = (
        len(names),
        len(class_files),
        len(json_files),
        len(language_files),
        len(advancement_files),
        len(recipe_files),
        len(guide_files),
        len(display_advancements),
        translation_api_classes,
    )
    if inventory != (813, 297, 346, 23, 47, 47, 0, 0, 53):
        errors.append(f"Waystones JAR 표시 경로 인벤토리 변경: {inventory}")

    spacing_mismatches = []
    for key, english_value in english.items():
        korean_value = korean.get(key)
        if not isinstance(english_value, str) or not isinstance(korean_value, str):
            continue
        english_edges = (
            english_value[: len(english_value) - len(english_value.lstrip())],
            english_value[len(english_value.rstrip()) :],
        )
        korean_edges = (
            korean_value[: len(korean_value) - len(korean_value.lstrip())],
            korean_value[len(korean_value.rstrip()) :],
        )
        if english_edges != korean_edges:
            spacing_mismatches.append(key)
    if spacing_mismatches:
        errors.append(f"Waystones 앞뒤 공백 불일치: {spacing_mismatches}")

    collisions: dict[str, set[str]] = {}
    for key, english_value in english.items():
        collisions.setdefault(str(korean[key]), set()).add(str(english_value))
    collisions = {
        value: source_values
        for value, source_values in collisions.items()
        if len(source_values) > 1
    }
    if collisions:
        errors.append(f"Waystones 번역 유발 명칭 충돌: {collisions}")

    if errors:
        raise RuntimeError("Waystones 연관 경로 검증 실패:\n" + "\n".join(errors))
    return {
        "group": "compass",
        "namespace": "waystones_related_paths",
        "source_jar_sha256": hashlib.sha256(waystones_jar.read_bytes()).hexdigest(),
        "class_files_reviewed": len(class_files),
        "class_translation_api_classes_reviewed": translation_api_classes,
        "class_fallback_literals_translated": len(WAYSTONES_CLASS_FALLBACKS),
        "class_hardcoded_display_literals_deferred": sum(
            len(markers) for _, markers in hardcoded_markers.values()
        ),
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_language_keys_reviewed": len(related_quest_language_keys),
        "ftbquests_item_references_reviewed": sum(
            len(item_ids) for item_ids in quest_item_references.values()
        ),
        "kubejs_files_reviewed": kubejs_files_reviewed,
        "kubejs_technical_references_reviewed": len(kubejs_refs),
        "other_mod_language_files_traced": other_language_files,
        "other_mod_owned_keys_traced": other_owned_keys,
        "translation_induced_collisions_reviewed": len(collisions),
        "harmful_translation_induced_collisions": 0,
        "advancement_files": len(advancement_files),
        "display_advancement_files": len(display_advancements),
        "recipe_files": len(recipe_files),
        "guide_files": len(guide_files),
        "validation": "passed",
    }


def verify_naturescompass_related(instance: Path) -> dict[str, object]:
    """Nature's Compass의 퀘스트, JAR 표시 경로와 용어를 검증한다."""
    errors = []
    output_path = OUTPUT_ROOT / "naturescompass/lang/ko_kr.json"
    korean = json.loads(output_path.read_text(encoding="utf-8"))
    mismatches = sorted(
        key
        for key, expected in NATURESCOMPASS_RECHECK_VALUES.items()
        if korean.get(key) != expected
    )
    if mismatches:
        errors.append(f"Nature's Compass 확정 교정값 불일치: {mismatches}")
    if korean.get("_comment") != "STRINGS - PRECIPITATION":
        errors.append("Nature's Compass 비번역 주석 값이 변경되었습니다")
    forbidden = sorted(
        key
        for key, value in korean.items()
        if NATURESCOMPASS_FORBIDDEN_TERMS.search(str(value))
    )
    if forbidden:
        errors.append(f"Nature's Compass 금지·충돌 용어 잔존: {forbidden}")

    source_lang = instance / "config/ftbquests/quests/lang/en_us.snbt"
    source_quests = parse_language_snbt(source_lang)
    related_quest_ids = {
        key.split(".")[1]
        for key, value in source_quests.items()
        if re.search(r"(?i)nature.?s compass|naturescompass", flatten(value))
        and key.startswith("quest.")
    }
    related_quest_keys = sorted(
        key
        for key in source_quests
        if key.startswith(tuple(f"quest.{quest_id}." for quest_id in related_quest_ids))
    )
    if related_quest_keys != sorted(NATURESCOMPASS_QUEST_VALUES):
        errors.append(
            "Nature's Compass 관련 FTB Quests 언어 범위 변경: " f"{related_quest_keys}"
        )
    quest_output = parse_language_snbt(
        PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
    )
    quest_mismatches = sorted(
        key
        for key, expected in NATURESCOMPASS_QUEST_VALUES.items()
        if quest_output.get(key) != expected
    )
    if quest_mismatches:
        errors.append(
            f"Nature's Compass 관련 FTB Quests 번역 불일치: {quest_mismatches}"
        )
    quest_working = json.loads(
        (PROJECT_ROOT / "working/ftbquests/common_chapter_overrides.json").read_text(
            encoding="utf-8"
        )
    )
    quest_description_key = "quest.70B6C9409AE69284.quest_desc"
    if (
        quest_working.get(quest_description_key)
        != NATURESCOMPASS_QUEST_VALUES[quest_description_key]
    ):
        errors.append("Nature's Compass 관련 퀘스트 설명 작업본 불일치")

    quest_files = sorted((instance / "config/ftbquests/quests").rglob("*.snbt"))
    quest_item_references = {}
    for path in quest_files:
        text = path.read_text(encoding="utf-8-sig")
        item_ids = re.findall(r'id:\s*"naturescompass:([^"]+)"', text)
        if item_ids:
            quest_item_references[path.relative_to(instance).as_posix()] = item_ids
    expected_quest_item_references = {
        "config/ftbquests/quests/chapters/apothic_enchanting.snbt": ["naturescompass"],
        "config/ftbquests/quests/chapters/building_tips.snbt": [
            "naturescompass",
            "naturescompass",
        ],
    }
    if quest_item_references != expected_quest_item_references:
        errors.append(
            "Nature's Compass 관련 FTB Quests 아이템 참조 범위 변경: "
            f"{quest_item_references}"
        )
    if korean.get("item.naturescompass.naturescompass") != "자연의 나침반":
        errors.append("Nature's Compass 퀘스트 자동 아이템 이름 불일치")

    kubejs_files_reviewed = 0
    kubejs_refs = []
    kubejs_root = instance / "kubejs"
    for path in sorted(kubejs_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".js",
            ".json",
            ".snbt",
            ".txt",
        }:
            continue
        kubejs_files_reviewed += 1
        text = path.read_text(encoding="utf-8-sig")
        if re.search(r"(?i)naturescompass|nature.?s compass", text):
            kubejs_refs.append(path.relative_to(instance).as_posix())
    if kubejs_refs:
        errors.append(f"예상하지 않은 Nature's Compass KubeJS 참조: {kubejs_refs}")

    compass_target = next(
        target
        for target in TARGETS
        if target.group == "compass" and target.namespaces == ("naturescompass",)
    )
    compass_jar = find_jar(instance, compass_target)
    other_language_files = 0
    other_owned_keys = 0
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        if jar_path == compass_jar:
            continue
        with ZipFile(jar_path) as archive:
            for name in archive.namelist():
                if not re.fullmatch(r"assets/[^/]+/lang/en_us\.json", name):
                    continue
                values = load_json(archive, name)
                related = {
                    key: value
                    for key, value in values.items()
                    if re.search(
                        r"(?i)naturescompass|nature.?s compass", f"{key} {value}"
                    )
                }
                if related:
                    other_language_files += 1
                    other_owned_keys += len(related)
    if other_language_files or other_owned_keys:
        errors.append(
            "예상하지 않은 다른 모드 소유 Nature's Compass 연동 언어: "
            f"파일={other_language_files}, 키={other_owned_keys}"
        )

    with ZipFile(compass_jar) as archive:
        names = archive.namelist()
        english = load_json(archive, "assets/naturescompass/lang/en_us.json")
        class_files = [name for name in names if name.endswith(".class")]
        json_files = [name for name in names if name.endswith(".json")]
        language_files = [name for name in json_files if "/lang/" in name]
        advancement_files = [
            name
            for name in json_files
            if name.startswith("data/naturescompass/advancement/")
        ]
        recipe_files = [
            name
            for name in json_files
            if name.startswith("data/naturescompass/recipe/")
        ]
        guide_files = [
            name
            for name in names
            if any(
                marker in name.lower()
                for marker in ("patchouli", "guideme", "modonomicon")
            )
        ]
        display_advancements = [
            name for name in advancement_files if "display" in load_json(archive, name)
        ]
        class_data = {name: archive.read(name) for name in class_files}
        translation_api_classes = sum(
            b"literal" in data or b"translatable" in data
            for data in class_data.values()
        )
        class_translation_keys = {
            key
            for key in english
            if any(key.encode() in data for data in class_data.values())
        }
        # rain은 rainfall의 바이트 접두사라 단순 포함 검색에서 생기는 오탐이다.
        class_translation_keys.discard("string.naturescompass.rain")

    if len(class_translation_keys) != 21:
        errors.append(
            "Nature's Compass 클래스 번역 키 범위 변경: "
            f"{sorted(class_translation_keys)}"
        )
    inventory = (
        len(names),
        len(class_files),
        len(json_files),
        len(language_files),
        len(advancement_files),
        len(recipe_files),
        len(guide_files),
        len(display_advancements),
        translation_api_classes,
    )
    if inventory != (154, 33, 60, 21, 4, 2, 0, 0, 2):
        errors.append(f"Nature's Compass JAR 표시 경로 인벤토리 변경: {inventory}")

    spacing_mismatches = []
    for key, english_value in english.items():
        korean_value = korean.get(key)
        if not isinstance(english_value, str) or not isinstance(korean_value, str):
            continue
        english_edges = (
            english_value[: len(english_value) - len(english_value.lstrip())],
            english_value[len(english_value.rstrip()) :],
        )
        korean_edges = (
            korean_value[: len(korean_value) - len(korean_value.lstrip())],
            korean_value[len(korean_value.rstrip()) :],
        )
        if english_edges != korean_edges:
            spacing_mismatches.append(key)
    if spacing_mismatches:
        errors.append(f"Nature's Compass 앞뒤 공백 불일치: {spacing_mismatches}")

    collisions: dict[str, set[str]] = {}
    for key, english_value in english.items():
        collisions.setdefault(str(korean[key]), set()).add(str(english_value))
    collisions = {
        value: source_values
        for value, source_values in collisions.items()
        if len(source_values) > 1
    }
    if collisions:
        errors.append(f"Nature's Compass 번역 유발 명칭 충돌: {collisions}")

    if errors:
        raise RuntimeError(
            "Nature's Compass 연관 경로 검증 실패:\n" + "\n".join(errors)
        )
    return {
        "group": "compass",
        "namespace": "naturescompass_related_paths",
        "source_jar_sha256": hashlib.sha256(compass_jar.read_bytes()).hexdigest(),
        "class_files_reviewed": len(class_files),
        "class_translation_api_classes_reviewed": translation_api_classes,
        "class_translation_keys_reviewed": len(class_translation_keys),
        "class_hardcoded_display_literals_deferred": 0,
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_language_keys_reviewed": len(related_quest_keys),
        "ftbquests_item_references_reviewed": sum(
            len(item_ids) for item_ids in quest_item_references.values()
        ),
        "kubejs_files_reviewed": kubejs_files_reviewed,
        "kubejs_references_reviewed": len(kubejs_refs),
        "other_mod_language_files_traced": other_language_files,
        "other_mod_owned_keys_traced": other_owned_keys,
        "translation_induced_collisions_reviewed": len(collisions),
        "harmful_translation_induced_collisions": 0,
        "advancement_files": len(advancement_files),
        "display_advancement_files": len(display_advancements),
        "recipe_files": len(recipe_files),
        "guide_files": len(guide_files),
        "validation": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("group", choices=GROUPS + ("all",))
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--copy-output", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    selected = [
        target
        for target in TARGETS
        if args.group == "all" or target.group == args.group
    ]
    rows = []
    for target in selected:
        rows.extend(verify_target(instance, target, args.copy_output))
    pack_selected = [
        target
        for target in PACK_LANGUAGE_TARGETS
        if args.group == "all" or target.group == args.group
    ]
    for target in pack_selected:
        rows.append(verify_pack_target(instance, target, args.copy_output))
    if args.group in {"jei", "all"}:
        rows.append(verify_jei_related(instance))
    if args.group in {"jade", "all"}:
        rows.append(verify_jade_related(instance))
    if args.group in {"map_team", "all"}:
        rows.append(verify_journeymap_related(instance))
        rows.append(verify_ftbchunks_related(instance))
        rows.append(verify_ftbteams_related(instance))
    if args.group in {"compass", "all"}:
        rows.append(verify_waystones_related(instance))
        rows.append(verify_naturescompass_related(instance))
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
