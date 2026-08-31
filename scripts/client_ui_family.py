#!/usr/bin/env python3
"""클라이언트 메뉴·설정 UI 계열의 현재 원문과 한국어 후보를 준비해요."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

FAMILY = "client_ui"
WORK_ROOT = PROJECT_ROOT / "working/client_ui"
OUTPUT_ROOT = active_output_root() / "resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-Za-z]")
NUMBER = re.compile(r"(?<![A-Za-z§&])\d+(?:\.\d+)?")
URL = re.compile(
    r"https?://(?:[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]*" r"[A-Za-z0-9_~/#\]=%-])?"
)
LINE_CODE = re.compile(r"^(?:[§&][0-9A-Za-z])+")
FOREIGN_SCRIPT = re.compile(r"[\u0600-\u06ff\u3040-\u30ff\u4e00-\u9fff]")
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
MODS = {
    "fancymenu": {
        "jar": "fancymenu_neoforge_*.jar",
        "keys": 3367,
        "bundled_korean": True,
    },
    "sodium-extra": {
        "jar": "sodium-extra-neoforge-*.jar",
        "keys": 380,
        "bundled_korean": True,
    },
    "iris": {
        "jar": "iris-neoforge-*.jar",
        "keys": 73,
        "bundled_korean": True,
    },
    "extremesoundmuffler": {
        "jar": "ExtremeSoundMuffler-*.jar",
        "keys": 77,
        "bundled_korean": False,
    },
    "fzzy_config": {
        "jar": "fzzy_config-*.jar",
        "keys": 287,
        "bundled_korean": False,
    },
    "iris_search": {
        "jar": "IrisSearch-*.jar",
        "keys": 5,
        "bundled_korean": False,
    },
}

FANCY_REPLACEMENTS = (
    (
        "현재 활성화된 효과가 하나라도 있으면 확인합니다.",
        "현재 활성화된 효과가 하나라도 있는지 확인합니다.",
    ),
    ("element identifier", "요소 식별자"),
    ("Java Virtual Machine", "Java 가상 머신"),
    ("처치한 대상", "처치자"),
    ("얼는", "어는"),
    ("الآن", "현재"),
    ("스케일링", "배율 조정"),
    ("커스터마이징", "사용자 지정"),
    ("커스터마이즈", "사용자 지정"),
    ("커스텀", "사용자 지정"),
    ("요구사항", "조건"),
    ("액션", "동작"),
    ("위치 지정자", "로케이터"),
    ("파우더 스노우", "가루눈"),
    ("백그라운드", "배경"),
    ("파라미터", "매개변수"),
    ("카테고리", "분류"),
    ("퍼센트", "백분율"),
    ("볼륨", "음량"),
    ("스케일", "배율"),
    ("랜덤", "무작위"),
    ("토글", "전환"),
    ("타입", "유형"),
    ("바이옴", "생물군계"),
    ("유저", "사용자"),
)

FANCY_OVERRIDES = {
    "fancymenu.actions.multiselect.warning.override": (
        "§x§l동작 스크립트를 덮어쓸까요?\n\n"
        "선택한 항목들의 동작 스크립트가 서로 달라요!\n"
        "모든 동작 스크립트가 §x덮어써집니다§r!\n\n계속할까요?"
    ),
    "fancymenu.layout.manage.rename.error.empty_name": (
        "레이아웃 이름 변경 실패!\n\n파일 이름은 최소 한 글자 이상이어야 합니다!"
    ),
    "fancymenu.listeners.on_damage_taken.desc": (
        "이 리스너는 플레이어가 피해를 받을 때 한 번 실행됩니다.\n\n"
        "동작과 조건에 사용할 수 있는 변수는 다음과 같습니다:\n\n"
        "- §z$$damage_amount §r= 공격으로 잃은 체력량\n"
        "- §z$$damage_type §r= 피해 유형의 리소스 위치\n"
        "- §z$$is_fatal_damage §r= 이 공격으로 플레이어 체력이 모두 소진되면 TRUE\n"
        "- §z$$damage_source §r= 피해를 준 엔티티의 리소스 위치, 없으면 NONE"
    ),
    "fancymenu.placeholders.math_sign.desc": (
        "다음을 반환합니다:\n 숫자가 양수면 1\n 숫자가 음수면 -1\n 숫자가 영이면 0"
    ),
    "fancymenu.placeholders.split_text.desc": (
        "텍스트를 특정 문자 또는 정규식 기준으로 나눕니다.\n\n"
        "input = 나눌 텍스트.\n"
        "regex = 텍스트를 나눌 문자 또는 정규식.\n"
        "max_parts = 텍스트를 나눌 최대 부분 수. -1로 설정하면 제한을 해제합니다.\n"
        "split_index = 나눈 뒤 반환할 부분. 0부터 시작합니다."
    ),
    "fancymenu.placeholders.unix_time.desc": (
        "1970년 1월 초하루 00:00:00 UTC 이후\n"
        "경과한 시간을 기준으로 한 현재 시간을 밀리초로 반환합니다."
    ),
    "fancymenu.placeholders.world.active_effect.desc": (
        "주어진 인덱스의 활성 효과 키를 반환합니다.\n"
        "가져올 효과의 인덱스는 영부터 시작합니다.\n"
        "첫 번째 효과의 인덱스는 0입니다.\n"
        "월드에 있지 않거나\n해당 인덱스에 활성 효과가 없으면 빈 값을 반환합니다."
    ),
    "fancymenu.placeholders.world.boss_name.desc": (
        "활성 보스의 이름을 반환합니다.\n"
        "가져올 보스의 인덱스는 영부터 시작합니다.\n"
        "첫 번째 보스의 인덱스는 0입니다.\n"
        "이름을 JSON으로 반환할지 정하는 불리언(true/false)도 받습니다.\n"
        "월드에 없거나 지정한 인덱스의 보스가 활성화되지 않았으면 빈 값을 반환합니다."
    ),
    "fancymenu.placeholders.world.current_boss_health.desc": (
        "활성 보스의 현재 체력을 백분율로 반환합니다.\n"
        "체력을 가져올 보스의 인덱스는 영부터 시작합니다.\n"
        "첫 번째 보스의 인덱스는 0입니다.\n"
        "월드에 없거나 지정한 인덱스의 보스가 활성화되지 않았으면 '0'을 반환합니다.\n"
        "가능한 값: 0-100"
    ),
    "fancymenu.requirements.is_camera_perspective.value.first_person": "일인칭",
    "fancymenu.requirements.is_camera_perspective.value.third_person_back": "삼인칭",
    "fancymenu.elements.glsl.compile_mode.direct": "직접 프래그먼트",
    "fancymenu.placeholders.jvm_name": "Java 가상 머신",
    "fancymenu.requirements.screens.manage_screen.group_mode.and": "그리고",
    "fancymenu.requirements.screens.manage_screen.group_mode.or": "또는",
    "fancymenu.requirements.screens.requirement.info.mode.normal": "일반",
    "fancymenu.requirements.screens.requirement.info.mode.opposite": "반대",
    "fancymenu.requirements.world.is_player_in_powder_snow": (
        "플레이어가 가루눈 안에 있는지 확인"
    ),
    "fancymenu.requirements.world.was_player_in_powder_snow": (
        "플레이어가 가루눈 안에 있었는지 확인"
    ),
    "fancymenu.helper.editor.layoutoptions.universal_layout.options.add_blacklist.desc": (
        "화면을 블랙리스트에 추가하려면\n§l화면 식별자§r를 사용하세요.\n\n"
        "§x블랙리스트에 있는 화면은\n§x레이아웃에서 무시되므로\n"
        "§x이 화면에는 사용자 지정이\n§x적용되지 않습니다.\n\n"
        "§x화면 식별자를 얻으려면\n§x해당 화면에서\n"
        "§x§l사용자 지정 -> 현재 화면 식별자 복사\n§r§x를 클릭하세요."
    ),
    "fancymenu.helper.editor.layoutoptions.universal_layout.options.add_whitelist.desc": (
        "화면을 화이트리스트에 추가하려면\n§l화면 식별자§r를 사용하세요.\n\n"
        "§x화이트리스트에 화면이 있으면\n§x그 화면들만 레이아웃으로\n"
        "§x사용자 지정됩니다. 다른 화면은\n§x모두 무시됩니다!\n\n"
        "§x화면 식별자를 얻으려면\n§x해당 화면에서\n"
        "§x§l사용자 지정 -> 현재 화면 식별자 복사\n§r§x를 클릭하세요."
    ),
    "fancymenu.helper.editor.properties.autoscale.forced_scale_needed": (
        "자동 배율 조정을 사용하려면 §l강제 GUI 배율을\n"
        "먼저 설정해야 합니다!\n\n강제 GUI 배율은 2로\n설정하는 것을 권장합니다.\n\n"
        "§x강제 GUI 배율을 설정하려면\n§x편집기 배경을 우클릭하고\n"
        "§x§lGUI 배율 강제§r§x를 클릭하세요."
    ),
}

FANCY_INTENTIONAL_SAME_KEYS = {
    "fancymenu.actions.blocks.delay",
    "fancymenu.actions.blocks.else",
    "fancymenu.actions.blocks.else_if",
    "fancymenu.actions.blocks.execute_later",
    "fancymenu.actions.blocks.if",
    "fancymenu.actions.blocks.while",
    "fancymenu.actions.openlink.desc.value",
    "fancymenu.actions.script_editor.shortcuts.a",
    "fancymenu.backgrounds.browser.url",
    "fancymenu.backgrounds.glsl.compile_mode.shadertoy",
    "fancymenu.buddy.achievement.locked",
    "fancymenu.buddy.achievement.reward",
    "fancymenu.decoration_overlays.browser.url",
    "fancymenu.decoration_overlays.glsl.compile_mode.shadertoy",
    "fancymenu.editor.shortcuts.a",
    "fancymenu.editor.shortcuts.copy",
    "fancymenu.editor.shortcuts.cut",
    "fancymenu.editor.shortcuts.delete",
    "fancymenu.editor.shortcuts.enter",
    "fancymenu.editor.shortcuts.g",
    "fancymenu.editor.shortcuts.grid",
    "fancymenu.editor.shortcuts.paste",
    "fancymenu.editor.shortcuts.redo",
    "fancymenu.editor.shortcuts.save",
    "fancymenu.editor.shortcuts.select_all",
    "fancymenu.editor.shortcuts.undo",
    "fancymenu.elements.browser.url",
    "fancymenu.elements.glsl.compile_mode.shadertoy",
    "fancymenu.overlay.debug.cpu",
    "fancymenu.overlay.debug.fps",
    "fancymenu.overlay.debug.gpu",
    "fancymenu.overlay.debug.toggle.shortcut",
    "fancymenu.overlay.menu_bar.customization.hide_overlay.shortcut",
    "fancymenu.overlay.menu_bar.customization.reload_fancymenu.shortcut",
    "fancymenu.overlay.menu_bar.user_interface.ui_blur_intensity.slider_label",
    "fancymenu.placeholders.pi",
    "fancymenu.requirements.categories.gui",
    "fancymenu.schedulers.manage.description.id",
    "fancymenu.ui.color_picker.hex",
    "fancymenu.ui.color_picker.hsv",
    "fancymenu.ui.color_picker.rgba",
}

INTENTIONAL_SAME_KEYS = {
    "fancymenu": FANCY_INTENTIONAL_SAME_KEYS,
    "sodium-extra": {
        "sodium-extra.overlay.coordinates",
        "sodium-extra.overlay.fps",
    },
    "iris": {"iris.keybinds", "iris.unsupported.iris"},
    "extremesoundmuffler": {
        "main_screen.side_screen.x",
        "main_screen.side_screen.y",
        "main_screen.side_screen.z",
    },
    "fzzy_config": {
        "fc.validated_field.color.r",
        "fc.validated_field.color.g",
        "fc.validated_field.color.b",
        "fc.validated_field.color.a",
        "fc.keybind.ctrl",
        "fc.keybind.ctrl.shift",
        "fc.keybind.ctrl.shift.alt",
        "fc.keybind.ctrl.alt",
        "fc.keybind.shift",
        "fc.keybind.shift.alt",
        "fc.keybind.alt",
        "fc.keybind.resetting",
        "fc.search.child",
        "fc.search.modifier.SHIFT",
        "fc.search.modifier.ALT",
        "fc.search.modifier.CTRL",
        "fc.button.info.page_up",
        "fc.button.info.page_down",
        "fc.button.info.home",
        "fc.button.info.end",
        "fzzy_config.text.or_3",
    },
    "iris_search": set(),
}

IRIS_OVERRIDES = {
    "iris.shaders.debug.failure": (
        "이 컴퓨터는 OpenGL 클라이언트 디버깅을 지원하지 않습니다. 셰이더 디버깅은 "
        "활성화되었습니다."
    ),
    "iris.shaders.debug.restart": (
        "디버그 컨텍스트가 없습니다. OpenGL 클라이언트 디버깅을 활성화하려면 게임을 "
        "다시 시작하세요."
    ),
    "iris.shaders.debug.restartNoDebug": (
        "셰이더 디버깅이 활성화되었습니다. NeoForge에서는 OpenGL 디버깅을 지원하지 "
        "않습니다."
    ),
    "iris.load.failure.shader": (
        "셰이더 팩을 불러오지 못했습니다! 이 오류를 셰이더 개발자에게 알려 주세요. "
    ),
    "iris.load.failure.generic": (
        "Iris가 셰이더를 불러오는 중 문제가 발생했습니다. Iris 개발자에게 알려 주세요. "
    ),
    "iris.keybind.wireframe": "와이어프레임(싱글플레이 전용)",
    "iris.nec.failure.title": "[%s] Not Enough Crashes 감지됨!",
    "iris.nec.failure.description": (
        "Not Enough Crashes는 충돌을 처리하는 동안 게임을 심각하게 망가뜨릴 수 있고, "
        "정확한 결과도 제공하지 않습니다.\nMixinTrace를 사용하면 충돌 원인을 더 안정적으로 "
        "찾을 수 있으며 게임을 잘못된 상태로 남겨 두지 않습니다."
    ),
    "iris.unsupported.pack.description": (
        "불러오려는 셰이더 팩에 %s에서 지원하지 않는 기능이 들어 있습니다. 다른 팩을 "
        "사용해 보세요. 목록: %s"
    ),
    "iris.unsupported.pack.macos": (
        "\nmacOS에서는 많은 셰이더 팩에 문제가 생길 수 있습니다."
    ),
    "options.iris.shaderPackSelection": "셰이더 팩...",
    "options.iris.shaderPackSelection.title": "셰이더 팩",
    "options.iris.shaderPackSelection.failedAdd": ("올바른 셰이더 팩 파일이 아닙니다."),
    "options.iris.shaderPackOptions.tooManyFiles": (
        "셰이더 설정 파일 여러 개를 한꺼번에 가져올 수 없습니다!"
    ),
    "options.iris.shadowDistance.enabled": (
        "그림자가 표시되는 최대 거리를 조정합니다. 이 거리보다 멀리 있는 지형과 엔티티는 "
        "그림자를 드리우지 않습니다. 그림자 거리를 줄이면 성능이 크게 향상될 수 있습니다."
    ),
    "options.iris.colorSpace": "색 공간",
    "options.iris.colorSpace.sodium_tooltip": (
        "화면을 변환할 색 공간입니다. 셰이더 팩 위에 적용됩니다. 잘 모르겠다면 SRGB를 "
        "사용하세요."
    ),
}

EXTREME_SOUND_TEXT = {
    "key.open_muffler_gui": "소리 차단기 화면 열기",
    "inventory.btn": "소리 차단기",
    "slider.btn.muffler.muffle": "소리 차단",
    "slider.btn.muffler.unmuffle": "소리 차단 해제",
    "slider.btn.play.play_sound": "소리 재생/정지",
    "slider.btn.volume": "음량: %s",
    "main_screen.btn.csl.recent": "최근",
    "main_screen.btn.csl.all": "전체",
    "main_screen.btn.csl.muffled": "차단됨",
    "main_screen.btn.csl.tooltip": "소리 %s개 표시 중",
    "main_screen.btn.tms.stop": "소리 차단 중지",
    "main_screen.btn.tms.start": "소리 차단 시작",
    "main_screen.btn.delete.sounds": "차단한 소리 삭제",
    "main_screen.btn.delete.list": "차단 목록 삭제",
    "main_screen.btn.delete.anchor": "앵커 삭제",
    "main_screen.btn.accept": "확인",
    "main_screen.btn.cancel": "취소",
    "main_screen.btn.next_sounds": "다음 소리",
    "main_screen.btn.previous_sounds": "이전 소리",
    "main_screen.btn.anchors.disabled": "앵커가 비활성화되어 있습니다!",
    "main_screen.btn.anchors.set_message": "먼저 앵커를 설정하세요",
    "main_screen.btn.anchors.set": "앵커 설정",
    "main_screen.btn.anchors.set_range": "범위: 1 - %s",
    "main_screen.btn.anchors.set_title": "앵커 이름 변경",
    "main_screen.btn.anchors.edit": "앵커 편집",
    "main_screen.main_title": "ESM - 기본 화면",
    "main_screen.empty": "아직 표시할 내용이 없습니다.",
    "main_screen.tip": "도움말: %s",
    "main_screen.side_screen.x": "X: %s",
    "main_screen.side_screen.y": "Y: %s",
    "main_screen.side_screen.z": "Z: %s",
    "main_screen.side_screen.radius": "반경: %s",
    "main_screen.side_screen.dimension": "차원: %s",
    "main_screen.side_screen.title": "이름: ",
    "main_screen.side_screen.radius_edit": "반경: ",
    "tip.disable": "설정에서 이 도움말을 끌 수 있습니다",
    "tip.change_volume": "슬라이더를 끌어 차단한 소리의 음량을 조절할 수 있습니다",
    "tip.inv_button": (
        "인벤토리 버튼을 우클릭한 채 끌어 원하는 위치로 옮길 수 있습니다"
    ),
    "tip.inv_button_disable": (
        "설정에서 인벤토리 화면의 소리 차단기 버튼을 켜거나 끌 수 있습니다"
    ),
    "tip.play_sound": "각 소리의 재생 버튼을 눌러 해당 소리를 들어 볼 수 있습니다",
    "tip.unmuffle": (
        "소리 차단 중지 버튼을 누르면 선택한 모든 소리의 차단을 멈추며, 다시 누르면 "
        "차단을 재개합니다"
    ),
    "tip.no_anchors": "설정에서 앵커를 비활성화할 수 있습니다",
    "tip.sound_blacklist": "설정에서 소리를 차단 목록에 넣을 수 있습니다",
    "tip.left_buttons": ("설정에서 차단 및 재생 버튼을 왼쪽으로 옮길 수 있습니다"),
    "tip.dark_theme": "설정에서 어두운 테마를 사용할 수 있습니다",
    "tip.use_anchors": (
        "앵커(위쪽 버튼 10개)는 선택한 영역 안의 소리를 차단할 때 사용합니다"
    ),
    "tip.set_anchors": (
        "번호가 붙은 앵커 버튼을 누른 다음 오른쪽의 위치 표식 버튼을 눌러 앵커 위치를 "
        "설정하세요"
    ),
    "tip.modify_anchors": (
        "앵커를 설정한 뒤에도 위치 표식 버튼을 눌러 언제든 위치를 옮길 수 있습니다."
    ),
    "tip.modify_anchors_2": "위치를 정한 앵커의 이름과 범위를 바꿀 수 있습니다",
    "tip.reset_recent_sounds": (
        '"최근" 소리 화면에서 Shift를 누른 채 휴지통 버튼을 누르면 최근 소리 목록을 '
        "비울 수 있습니다"
    ),
    "log.warn.loadAnchorList": "ESM: 앵커 목록이 없어 빈 목록을 만듭니다",
    "log.error.loadAnchorList": "ESM: 앵커 목록을 불러오는 중 오류 발생:\n %s",
    "log.error.saveAnchorList": "ESM: 앵커 목록을 저장하는 중 오류 발생\n %s",
    "log.warn.loadMuffledList": "ESM: 차단 목록이 없어 빈 목록을 만듭니다",
    "log.error.loadMuffledList": "ESM: 차단 목록을 불러오는 중 오류 발생:\n %s",
    "log.error.saveMuffledList": "ESM: 차단 목록을 저장하는 중 오류 발생:\n %s",
    "forbiddenSounds.button": "금지할 소리 설정",
    "general.button": "일반",
    "Anchors.button": "앵커",
    "inventory_button.button": "인벤토리 버튼",
    "extremesoundmuffler.configuration.inventory_button": "인벤토리 버튼",
    "extremesoundmuffler.configuration.Anchors": "앵커",
    "extremesoundmuffler.configuration.general": "일반",
    "extremesoundmuffler.configuration.forbiddenSounds": "금지된 소리",
    "extremesoundmuffler.configuration.modsMuffled": "차단된 모드",
    "extremesoundmuffler.configuration.useDarkTheme": "어두운 테마 사용",
    "extremesoundmuffler.configuration.leftButtons": "버튼을 왼쪽에 표시",
    "extremesoundmuffler.configuration.lawfulAllList": "전체 소리 목록 허용",
    "extremesoundmuffler.configuration.defaultMuteVolume": "기본 차단 음량",
    "extremesoundmuffler.configuration.showTip": "도움말 표시",
    "extremesoundmuffler.configuration.disableInventoryButton": (
        "인벤토리 버튼 비활성화"
    ),
    "extremesoundmuffler.configuration.invButtonX": "인벤토리 버튼 X 좌표",
    "extremesoundmuffler.configuration.invButtonY": "인벤토리 버튼 Y 좌표",
    "extremesoundmuffler.configuration.disableCreativeInventoryButton": (
        "크리에이티브 인벤토리 버튼 비활성화"
    ),
    "extremesoundmuffler.configuration.creativeInvButtonX": (
        "크리에이티브 버튼 X 좌표"
    ),
    "extremesoundmuffler.configuration.creativeInvButtonY": (
        "크리에이티브 버튼 Y 좌표"
    ),
    "extremesoundmuffler.configuration.disableAnchors": "앵커 비활성화",
}

IRIS_SEARCH_TEXT = {
    "iris_search.button.search": "검색",
    "iris_search.button.clear": "지우기",
    "iris_search.tooltip.search": "셰이더 설정 검색(Ctrl + F)",
    "iris_search.tooltip.clear": "셰이더 검색 종료(Esc)",
    "iris_search.search.hint": "옵션 검색...",
}

FZZY_TEXT = {
    "fc.validated_field.boolean.true": "참",
    "fc.validated_field.boolean.false": "거짓",
    "fc.validated_field.choice_set": "선택 항목 편집...",
    "fc.validated_field.choice_set.deselect": "모두 선택 해제",
    "fc.validated_field.choice_set.select": "모두 선택",
    "fc.validated_field.choice_set.selected": "%s: 선택됨",
    "fc.validated_field.choice_set.deselected": "%s: 선택 해제됨",
    "fc.validated_field.color.r": "R",
    "fc.validated_field.color.g": "G",
    "fc.validated_field.color.b": "B",
    "fc.validated_field.color.a": "A",
    "fc.validated_field.color.hl": "색조·명도 맵",
    "fc.validated_field.color.s": "채도 슬라이더",
    "fc.validated_field.color.r.desc": "0에서 255 사이의 정수를 입력하세요",
    "fc.validated_field.color.g.desc": "0에서 255 사이의 정수를 입력하세요",
    "fc.validated_field.color.b.desc": "0에서 255 사이의 정수를 입력하세요",
    "fc.validated_field.color.a.desc": "0에서 255 사이의 정수를 입력하세요",
    "fc.validated_field.color.a.desc_locked": "알파 값은 255로 고정되어 있습니다.",
    "fc.validated_field.color.s.desc": "색조·명도 맵에서 색조와 명도를 바꾸세요",
    "fc.validated_field.color.s.usage.keyboard": (
        "위쪽 또는 아래쪽 화살표 키를 눌러 색의 채도를 바꾸세요"
    ),
    "fc.validated_field.color.hl.desc": (
        "색조와 명도만 지정합니다. 채도는 채도 슬라이더로 바꾸세요."
    ),
    "fc.validated_field.color.hl.usage.keyboard": (
        "왼쪽 또는 오른쪽 화살표로 색조를, 위쪽 또는 아래쪽 화살표로 명도를 바꾸세요"
    ),
    "fc.validated_field.color.hl.usage.mouse": "맵을 클릭해 색조와 명도를 지정하세요",
    "fc.validated_field.color.int.desc": "16진수 색상 표현입니다.",
    "fc.validated_field.entity_attribute.error": "∽o∽4알 수 없는 속성∽r",
    "fc.validated_field.expression": "수식 편집",
    "fc.validated_field.expression.ln.tip": (
        "자연로그\n주어진 값의 밑이 'e'인 로그를 계산합니다"
    ),
    "fc.validated_field.expression.min.tip": (
        "최댓값\n주어진 두 값 중 큰 값을 계산합니다"
    ),
    "fc.validated_field.expression.max.tip": (
        "최솟값\n주어진 두 값 중 작은 값을 계산합니다"
    ),
    "fc.validated_field.expression.log.tip": (
        "로그\n첫 번째 값의 밑을 두 번째 값으로 한 로그를 계산합니다\nlog[right](left)"
    ),
    "fc.validated_field.expression.log10.tip": (
        "상용로그\n주어진 값의 밑이 10인 로그를 계산합니다"
    ),
    "fc.validated_field.expression.log2.tip": (
        "밑이 2인 로그\n주어진 값의 밑이 2인 로그를 계산합니다"
    ),
    "fc.validated_field.expression.sqrt.tip": (
        "제곱근\n주어진 값의 제곱근을 계산합니다"
    ),
    "fc.validated_field.expression.abs.tip": (
        "절댓값\n주어진 값의 절댓값을 계산합니다"
    ),
    "fc.validated_field.expression.sin.tip": (
        "사인\n주어진 라디안 값의 사인을 계산합니다"
    ),
    "fc.validated_field.expression.cos.tip": (
        "코사인\n주어진 라디안 값의 코사인을 계산합니다"
    ),
    "fc.validated_field.expression.pow.tip": (
        "거듭제곱\n^ 왼쪽 값을 오른쪽 값만큼 거듭제곱합니다"
    ),
    "fc.validated_field.expression.paren.tip": "괄호\n괄호 한 쌍을 추가합니다",
    "fc.validated_field.expression.incr.tip": (
        "증분 단위 내림\n주어진 값을 지정한 증분의 가장 가까운 아래쪽 배수로 내립니다.\n"
        "incr(1.16, 0.1)은 1.1로 내림합니다"
    ),
    "fc.validated_field.expression.ciel.tip": (
        "올림\n주어진 값을 양의 무한대 방향으로 올림합니다"
    ),
    "fc.validated_field.expression.flr.tip": (
        "내림\n주어진 값을 음의 무한대 방향으로 내림합니다"
    ),
    "fc.validated_field.expression.rnd.tip": (
        "반올림\n주어진 값을 가장 가까운 정수로 반올림합니다.\n정확히 중간이면 짝수로 "
        "반올림합니다."
    ),
    "fc.validated_field.expression.plus.tip": "더하기\n왼쪽 값과 오른쪽 값을 더합니다",
    "fc.validated_field.expression.minus.tip": ("빼기\n왼쪽 값에서 오른쪽 값을 뺍니다"),
    "fc.validated_field.expression.times.tip": "곱하기\n왼쪽 값과 오른쪽 값을 곱합니다",
    "fc.validated_field.expression.div.tip": "나누기\n왼쪽 값을 오른쪽 값으로 나눕니다",
    "fc.validated_field.expression.mod.tip": (
        "나머지\n왼쪽 값을 오른쪽 값으로 나눈 나머지를 계산합니다"
    ),
    "fc.validated_field.ingredient": "선택한 유형에 속한 값만 유지됩니다",
    "fc.validated_field.ingredient.edit": "재료 편집...",
    "fc.validated_field.ingredient.items": "아이템 ID",
    "fc.validated_field.ingredient.tags": "태그 ID",
    "fc.validated_field.ingredient.clear": "지우기",
    "fc.validated_field.list": "목록 편집...",
    "fc.validated_field.list.clear": "목록 비우기",
    "fc.validated_field.list.clear.desc": (
        "확인을 누르면 이 목록을 완전히 비웁니다. 계속할까요?"
    ),
    "fc.validated_field.map": "맵 편집...",
    "fc.validated_field.map.clear": "맵 비우기",
    "fc.validated_field.map.clear.desc": (
        "확인을 누르면 이 맵을 완전히 비웁니다. 계속할까요?"
    ),
    "fc.validated_field.number.desc.fallback": "%1$s에서 %2$s 사이의 숫자",
    "fc.validated_field.number.desc.fallback.min": "%s 이하의 숫자",
    "fc.validated_field.number.desc.fallback.max": "%s 이상의 숫자",
    "fc.validated_field.number.desc.fallback.any": "유효한 숫자",
    "fc.validated_field.number.editBox.usage": "새 숫자를 입력해 값을 바꾸세요.",
    "fc.validated_field.number.slider.usage": (
        "왼쪽 또는 오른쪽 키를 눌러 값을 증감하세요."
    ),
    "fc.validated_field.number.slider.usage2": "Enter를 눌러 확인하세요.",
    "fc.validated_field.number.slider.usage.unfocused": (
        "슬라이더를 끌어 값을 바꾸세요."
    ),
    "fc.validated_field.number.textbox.invalid": "잘못된 입력: 숫자를 입력해야 합니다.",
    "fc.validated_field.number.textbox.usage": "Enter를 눌러 입력을 확인하세요.",
    "fc.validated_field.number.textbox.usage.unfocused": (
        "체크 표시를 눌러 입력을 확인하세요."
    ),
    "fc.validated_field.object": "편집...",
    "fc.validated_field.set": "집합 편집...",
    "fc.validated_field.set.clear": "집합 비우기",
    "fc.validated_field.set.clear.desc": (
        "확인을 누르면 이 집합을 완전히 비웁니다. 계속할까요?"
    ),
    "fc.validated_field.condition": "조건을 충족하지 않음",
    "fc.validated_field.conditions": "조건을 충족하지 않음",
    "fc.validated_field.pair.left": "왼쪽",
    "fc.validated_field.pair.right": "오른쪽",
    "fc.validated_field.expand": "펼쳐짐",
    "fc.validated_field.expand.usage.focused": "Enter를 눌러 펼치기",
    "fc.validated_field.expand.usage.hovered": "좌클릭하여 펼치기",
    "fc.validated_field.collapse": "접힘",
    "fc.validated_field.collapse.usage.focused": "Enter를 눌러 접기",
    "fc.validated_field.collapse.usage.hovered": "좌클릭하여 접기",
    "fc.validated_field.current": "현재 값: %s",
    "fc.validated_field.default": "[%1$s]을(를) 기본값 [%2$s](으)로 복원",
    "fc.validated_field.update.error": (
        "[%1$s], [%2$s]을(를) [%3$s](으)로 바꾸는 중 오류: %4$s"
    ),
    "fc.validated_field.revert.error": "[%1$s] 복원 중 오류: %2$s",
    "fc.validated_field.update": "[%1$s], [%2$s]을(를) [%3$s](으)로 변경",
    "fc.validated_field.revert": "[%1$s], [%2$s]을(를) [%3$s](으)로 되돌리기",
    "fc.tristate.default": "기본값",
    "fc.tristate.default.desc": "기본값",
    "fc.tristate.true": "참",
    "fc.tristate.true.desc": "참",
    "fc.tristate.false": "거짓",
    "fc.tristate.false.desc": "거짓",
    "fc.keybind.ctrl": "Ctrl %s",
    "fc.keybind.ctrl.shift": "Ctrl Shift %s",
    "fc.keybind.ctrl.shift.alt": "Ctrl Shift Alt %s",
    "fc.keybind.ctrl.alt": "Ctrl Alt %s",
    "fc.keybind.shift": "Shift %s",
    "fc.keybind.shift.alt": "Shift Alt %s",
    "fc.keybind.alt": "Alt %s",
    "fc.keybind.or": "%1$s ∽o또는∽r %2$s",
    "fc.keybind.narrate": "%s 키 지정",
    "fc.keybind.resetting": "∽e>∽r %s ∽e<∽r",
    "fc.keybind.resetting.narrate": "새 키를 선택하세요. 현재: %s",
    "test.walkable.testChildDave.testChildBool": "Dave 자식 항목의 불리언 테스트",
    "test.walkable.testChildDave.testChildBool.desc": (
        "Dave가 가장 좋아하는 불리언입니다. 잘 다뤄 주세요."
    ),
    "fc.networking.permission.cheat": (
        "플레이어 [%1$s]이(가) 서버 설정을 바꾸며 치트를 시도했을 수 있습니다!"
    ),
    "fc.networking.restart": "설정을 적용하려면 다시 시작해야 합니다.",
    "fc.search.indirect": "일치하는 하위 항목이 있습니다:",
    "fc.search.indirect.group": "그룹에 일치하는 하위 항목이 있습니다:",
    "fc.search.title": "검색창 설정",
    "fc.search.clear": "검색 지우기",
    "fc.search.child": "(%1$s): %2$s",
    "fc.search.modifier": "보조 키",
    "fc.search.modifier.disabled": "관련 없음",
    "fc.search.modifier.disabled.desc": "검색 전달 방식에 보조 키가 필요하지 않습니다",
    "fc.search.modifier.desc": (
        "검색 전달 방식에 사용할 보조 키입니다. 방식이 항상 또는 안 함이면 사용되지 "
        "않습니다"
    ),
    "fc.search.modifier.SHIFT": "Shift",
    "fc.search.modifier.ALT": "Alt",
    "fc.search.modifier.CTRL": "Ctrl",
    "fc.search.modifier.fallback": "키",
    "fc.search.behavior": "검색 전달 방식",
    "fc.search.behavior.desc": (
        "현재 검색어를 하위 항목으로 전달하는 방법입니다. 조건을 충족하면 하위 항목이 "
        "열리고 검색창에 현재 검색어가 미리 입력됩니다."
    ),
    "fc.search.behavior.HOLD_MODIFIER": "%s 누르기",
    "fc.search.behavior.HOLD_MODIFIER.desc": "%s 키를 눌러 검색어 전달",
    "fc.search.behavior.DONT_HOLD_MODIFIER": "%s 누르지 않기",
    "fc.search.behavior.DONT_HOLD_MODIFIER.desc": (
        "%s 키를 누르면 검색어 전달을 막습니다"
    ),
    "fc.search.behavior.ALWAYS": "항상",
    "fc.search.behavior.ALWAYS.desc": "검색어를 전달합니다",
    "fc.search.behavior.NEVER": "안 함",
    "fc.search.behavior.NEVER.desc": "검색어를 전달하지 않습니다",
    "fc.search.clearSearch": "검색 지우기",
    "fc.search.clearSearch.desc": (
        "참 = GUI를 열 때 검색어를 지웁니다\n거짓 = GUI를 다시 열 때 검색어를 "
        "표시합니다."
    ),
    "fc.narrator.position.list": "목록 항목 %2$s개 중 %1$s번째",
    "fc.narrator.position.config": "설정 %2$s개 중 %1$s번째",
    "fc.narrator.position.entry": "요소 %2$s개 중 %1$s번째",
    "fc.narrator.position.child": "하위 요소 %2$s개 중 %1$s번째",
    "fc.command.config": "∽6∽l영향받는 설정:∽r",
    "fc.command.player": "∽6∽l담당 플레이어:∽r",
    "fc.command.history": "∽6∽l문제 발생 당시의 변경 기록:∽r",
    "fc.command.accept": "[업데이트 수락]",
    "fc.command.accepted": "업데이트 수락됨. 전송자 권한을 다시 동기화합니다: %s",
    "fc.command.reject": "[업데이트 거부]",
    "fc.command.rejected": "업데이트 거부됨: %s",
    "fc.command.inspect": "[업데이트 확인]",
    "fc.command.error.no_id": "격리된 업데이트 ID가 유효하지 않습니다",
    "fc.config.generic.section": "설정 구역",
    "fc.config.generic.section.desc": (
        "이 설정 구역에는 번역 키가 구현되어 있지 않아 화면에 표시할 이름을 알 수 "
        "없습니다!"
    ),
    "fc.config.generic.field": "설정",
    "fc.config.generic.field.desc": (
        "이 설정에는 번역 키가 구현되어 있지 않아 화면에 표시할 이름을 알 수 없습니다!"
    ),
    "fc.config.right_click": "동작",
    "fc.config.restore.confirm.desc": (
        "확인을 누르면 이 설정을 기본값으로 초기화합니다. 계속할까요?"
    ),
    "fc.config.back": "뒤로",
    "fc.config.back.desc": "%s(으)로 돌아가기\n(Shift를 누르면 모두 종료)",
    "fc.config.done.desc": "설정을 저장하고 화면 닫기",
    "fc.config.search": "검색",
    "fc.config.search.desc": (
        "이름으로 설정 필터링\n\n$ : 설명 검색\n- : 검색 반전\n-$ : 설명 검색 반전\n"
        '"" : 정확히 검색\n-"" : 정확히 검색 반전\n// : 정규식 검색\n-// : 정규식 '
        "검색 반전"
    ),
    "fc.config.forwarded": "전달받은 설정",
    "fc.config.forwarded_error.c2s": (
        "설정을 전달하지 못했습니다. 서버가 이 데이터 유형을 받지 않습니다. 관리자에게 "
        "문의하세요."
    ),
    "fc.config.forwarded_error.s2c": (
        "설정을 전달하지 못했습니다. 전달 대상 플레이어에게 호환되는 클라이언트가 "
        "없습니다."
    ),
    "fc.config.restart": "다시 시작 필요",
    "fc.config.restart.warning": "이 설정을 바꾸면 다시 시작해야 합니다!",
    "fc.config.restart.warning.section": (
        "이 구역의 일부 설정을 바꾸면 다시 시작해야 합니다!"
    ),
    "fc.config.restart.warning.config": (
        "이 구성의 일부 설정을 바꾸면 다시 시작해야 합니다!"
    ),
    "fc.config.restart.update": (
        "클라이언트를 다시 시작해야 할 수 있는 설정 업데이트를 받았습니다. 궁금한 점이 "
        "있다면 서버 운영자에게 문의하세요."
    ),
    "fc.config.restart.update.client": (
        "클라이언트를 다시 시작해야 하는 설정을 변경했습니다."
    ),
    "fc.config.restart.update.client.prompt": "[다시 시작]",
    "fc.config.restart.update.server": (
        "서버를 다시 시작해야 하는 설정을 변경했습니다. 접속한 클라이언트에는 변경 사항이 "
        "자동으로 적용되고 알림도 전송되었습니다. 플레이어 및 운영진과 다시 시작 일정을 "
        "정하세요."
    ),
    "fc.config.restart.sync": (
        "동기화 중 받은 설정을 적용하려면 클라이언트를 다시 시작해야 합니다. 계속할까요?"
    ),
    "fc.config.relog.warning": (
        "이 설정을 바꾸면 현재 서버나 월드에서 나갔다가 다시 들어와야 합니다!"
    ),
    "fc.config.relog.warning.section": (
        "이 구역의 일부 설정을 바꾸면 현재 서버나 월드에서 나갔다가 다시 들어와야 "
        "합니다!"
    ),
    "fc.config.relog.warning.config": (
        "이 구성의 일부 설정을 바꾸면 현재 서버나 월드에서 나갔다가 다시 들어와야 "
        "합니다!"
    ),
    "fc.config.relog.update": (
        "현재 서버에서 나갔다가 다시 들어와야 할 수 있는 설정 업데이트를 받았습니다. "
        "궁금한 점이 있다면 서버 운영자에게 문의하세요."
    ),
    "fc.config.relog.update.client": (
        "월드에서 나갔다가 다시 들어와야 하는 설정을 변경했습니다."
    ),
    "fc.config.relog.update.client.prompt": "[게임 나가기]",
    "fc.config.relog.update.server": (
        "현재 서버에서 나갔다가 다시 들어와야 하는 설정을 변경했습니다. 접속한 "
        "클라이언트에는 변경 사항이 자동으로 적용되고 알림도 전송되었습니다. 필요하면 "
        "플레이어에게 추가로 안내하세요."
    ),
    "fc.config.reload_both.warning": (
        "이 설정을 바꾸면 데이터 팩(/reload)과 리소스(F3 + T)를 다시 불러와야 합니다."
    ),
    "fc.config.reload_both.warning.section": (
        "이 구역의 일부 설정을 바꾸면 데이터 팩(/reload)과 리소스(F3 + T)를 다시 "
        "불러와야 합니다."
    ),
    "fc.config.reload_both.warning.config": (
        "이 구성의 일부 설정을 바꾸면 데이터 팩(/reload)과 리소스(F3 + T)를 다시 "
        "불러와야 합니다."
    ),
    "fc.config.reload_both.update": (
        "데이터 팩(/reload)과 리소스(F3 + T)를 다시 불러와야 할 수 있는 설정 업데이트를 "
        "받았습니다. 서버가 다시 불러와질 수 있으니 준비하고, 궁금한 점이 있다면 서버 "
        "운영자에게 문의하세요."
    ),
    "fc.config.reload_both.update.client": (
        "데이터 팩(/reload)과 리소스(F3 + T)를 다시 불러와야 하는 설정을 변경했습니다."
    ),
    "fc.config.reload_both.update.server": (
        "데이터 팩(/reload)과 리소스(F3 + T)를 다시 불러와야 하는 설정을 변경했습니다. "
        "접속한 클라이언트에는 변경 사항이 자동으로 적용되고 리소스를 다시 불러오라는 "
        "알림도 전송되었습니다. 플레이어 및 운영진과 다시 불러올 일정을 정하세요."
    ),
    "fc.config.reload_data.warning": (
        "이 설정을 바꾸면 데이터 팩을 다시 불러와야 합니다(/reload)."
    ),
    "fc.config.reload_data.warning.section": (
        "이 구역의 일부 설정을 바꾸면 데이터 팩을 다시 불러와야 합니다(/reload)."
    ),
    "fc.config.reload_data.warning.config": (
        "이 구성의 일부 설정을 바꾸면 데이터 팩을 다시 불러와야 합니다(/reload)."
    ),
    "fc.config.reload_data.update": (
        "데이터 팩을 다시 불러와야 할 수 있는 설정 업데이트를 받았습니다. 서버가 다시 "
        "불러와질 수 있으니 준비하세요."
    ),
    "fc.config.reload_data.update.client": (
        "데이터 팩을 다시 불러와야 하는 설정을 변경했습니다(/reload)."
    ),
    "fc.config.reload_data.update.prompt": "[데이터 팩 다시 불러오기]",
    "fc.config.reload_data.update.server": (
        "데이터 팩을 다시 불러와야 하는 설정을 변경했습니다(/reload). 접속한 "
        "클라이언트에는 변경 사항이 자동으로 적용되고 다시 불러올 수 있다는 알림도 "
        "전송되었습니다. 플레이어 및 운영진과 다시 불러올 일정을 정하세요."
    ),
    "fc.config.reload_resources.warning": (
        "이 설정을 바꾸면 리소스를 다시 불러와야 합니다(F3 + T)."
    ),
    "fc.config.reload_resources.warning.section": (
        "이 구역의 일부 설정을 바꾸면 리소스를 다시 불러와야 합니다(F3 + T)."
    ),
    "fc.config.reload_resources.warning.config": (
        "이 구성의 일부 설정을 바꾸면 리소스를 다시 불러와야 합니다(F3 + T)."
    ),
    "fc.config.reload_resources.update": (
        "리소스를 다시 불러와야 할 수 있는 설정 업데이트를 받았습니다(F3 + T). 궁금한 "
        "점이 있다면 서버 운영자에게 문의하세요."
    ),
    "fc.config.reload_resources.update.client": (
        "리소스를 다시 불러와야 하는 설정을 변경했습니다(F3 + T)."
    ),
    "fc.config.reload_resources.update.client.prompt": "[리소스 팩 다시 불러오기]",
    "fc.config.reload_resources.update.server": (
        "클라이언트가 리소스를 다시 불러와야 하는 설정을 변경했습니다(F3 + T). 접속한 "
        "클라이언트에는 변경 사항이 자동으로 적용되고 알림도 전송되었습니다. 궁금한 점이 "
        "있는 플레이어에게 추가로 안내하세요."
    ),
    "fc.config.prompt.hover": "클릭하여 명령어 실행",
    "fc.button.accept": "수락",
    "fc.button.deny": "거부",
    "fc.button.apply": "변경 사항 적용",
    "fc.button.apply.desc": "모든 변경 사항을 적용하고 설정을 저장합니다",
    "fc.button.revert": "변경 사항 되돌리기",
    "fc.button.revert.desc": "방금 바꾼 모든 설정을 되돌립니다",
    "fc.button.restore": "기본값 복원",
    "fc.button.restore.desc": "모든 구성의 설정을 기본값으로 복원합니다",
    "fc.button.restore.confirm": "확인",
    "fc.button.restore.confirm.desc": (
        "확인을 누르면 이 설정들을 기본값으로 초기화합니다. 계속할까요?"
    ),
    "fc.button.reset": "구성 초기화",
    "fc.button.changelog": "변경 기록",
    "fc.button.changelog.desc": "방금 바꾼 모든 설정을 나열합니다",
    "fc.button.forward": "설정 전달",
    "fc.button.forward.confirm": "전달",
    "fc.button.forward.active": "이 항목을 다른 플레이어에게 전달",
    "fc.button.forward.inactive": "설정을 전달할 플레이어가 없습니다",
    "fc.button.alert.active": "전달받은 설정",
    "fc.button.alert.inactive": "전달받은 설정 없음",
    "fc.button.noPerms": "편집 불가",
    "fc.button.noPerms.desc": "이 항목을 편집할 권한이 없습니다.",
    "fc.button.outOfGame": "게임 밖",
    "fc.button.outOfGame.desc": (
        "이 항목을 편집하려면 게임에 들어가거나 서버에 접속하세요"
    ),
    "fc.button.notLoaded": "불러오지 않음",
    "fc.button.notLoaded.desc": (
        "이 구성은 아직 불러오지 않았습니다. 게임에 들어가면 불러올 수 있습니다."
    ),
    "fc.button.navigate": "%s(으)로 이동",
    "fc.button.changes": "변경 사항...",
    "fc.button.changes.title": "변경 사항 관리",
    "fc.button.changes.message": "변경 사항 %s개 버튼",
    "fc.button.changes.message.noChanges": "변경 사항 없음 버튼",
    "fc.button.changes.desc": "변경 사항을 적용하거나 되돌리는 관리 메뉴입니다.",
    "fc.button.copy": "복사",
    "fc.button.paste": "붙여넣기",
    "fc.button.save": "구성 저장",
    "fc.button.delete": "항목 삭제",
    "fc.button.add": "새 항목 추가",
    "fc.button.config": "구성 열기",
    "fc.button.config_inactive": "∽c구성을 찾을 수 없음∽r",
    "fc.button.cancel": "취소",
    "fc.button.goto": "이동...",
    "fc.button.goto.narration": "이동: %s",
    "fc.button.up": "증가",
    "fc.button.down": "감소",
    "fc.button.clear": "키 지정 지우기",
    "fc.button.compound": "키 지정 옵션 추가",
    "fc.button.slider.usage.focused": "위쪽 또는 아래쪽 화살표를 눌러 값 바꾸기",
    "fc.button.restart.cancel": "타이틀 화면으로 돌아가기",
    "fc.button.click.open_url": "%s 링크 열기",
    "fc.button.click.open_file": "파일 열기: %s",
    "fc.button.click.run_command": '명령어 "%s" 실행',
    "fc.button.click.copy_to_clipboard": '"%s"을(를) 클립보드에 복사',
    "fc.button.info": "화면 사용법",
    "fc.button.info.fc": "∽o이 구성은 %s에서 제공합니다∽r",
    "fc.button.info.fc.tip": "위키 페이지 열기",
    "fc.button.info.alert": (
        "∽o[!]∽r - 아이콘이 표시된 설정은 변경 후 별도의 동작이 필요합니다."
    ),
    "fc.button.info.page_up": "Page Up",
    "fc.button.info.page_down": "Page Down",
    "fc.button.info.home": "Home",
    "fc.button.info.end": "End",
    "fc.button.info.copy": "복사",
    "fc.button.info.paste": "붙여넣기",
    "fc.button.info.find": "찾기",
    "fc.button.info.save": "저장",
    "fc.button.info.undo": "실행 취소",
    "fc.button.info.context_keyboard": "상황에 맞는 메뉴",
    "fc.button.info.context_mouse": "상황에 맞는 메뉴",
    "fc.button.info.back": "뒤로",
    "fc.button.info.search": "바로 가기",
    "fc.button.info.info": "정보",
    "fc.button.info.full_exit": "모두 종료",
    "fc.button.info.page_up.desc": "설정 한 페이지 위로 스크롤합니다",
    "fc.button.info.page_down.desc": "설정 한 페이지 아래로 스크롤합니다",
    "fc.button.info.home.desc": "구성 맨 위로 스크롤합니다",
    "fc.button.info.end.desc": "구성 맨 아래로 스크롤합니다",
    "fc.button.info.copy.desc": "마우스를 올렸거나 선택한 설정을 복사합니다",
    "fc.button.info.paste.desc": "복사한 값을 호환되는 설정에 붙여넣습니다",
    "fc.button.info.find.desc": "검색창에 포커스를 둡니다",
    "fc.button.info.save.desc": "변경 사항을 저장하고 서버에 업데이트를 보냅니다",
    "fc.button.info.undo.desc": "최신 변경 사항부터 차례로 실행 취소합니다",
    "fc.button.info.context_keyboard.desc": ("사용할 수 있다면 '우클릭' 메뉴를 엽니다"),
    "fc.button.info.context_mouse.desc": "사용할 수 있다면 '우클릭' 메뉴를 엽니다",
    "fc.button.info.back.desc": "이전 구성 화면으로 돌아갑니다",
    "fc.button.info.search.desc": "'바로 가기' 메뉴를 엽니다",
    "fc.button.info.info.desc": "이 팝업을 엽니다",
    "fc.button.info.full_exit.desc": (
        "열려 있는 모든 구성 GUI를 종료하고, 필요한 경우 저장합니다"
    ),
    "fzzy_config.text.or_2": "%1$s 또는 %2$s",
    "fzzy_config.text.or_3": "%1$s, %2$s",
    "fzzy_config.text.and_2": "%1$s 및 %2$s",
}

FZZY_OVERRIDES = {
    "fc.validated_field.color.int.desc": "십육진수 색상 표현입니다.",
    "fc.validated_field.expression.log10.tip": (
        "밑이 10인 로그\n주어진 값의 밑이 10인 로그를 계산합니다"
    ),
}

EXTREME_ESCAPED_LINE_KEYS = {
    "log.error.loadAnchorList",
    "log.error.saveAnchorList",
    "log.error.loadMuffledList",
    "log.error.saveMuffledList",
}

SODIUM_OVERRIDES = {
    "modmenu.summaryTranslation.sodium-extra": "Sodium에 들어가기 어려운 기능들.",
    "options.particles.minecraft.ambient_entity_effect": "주변 엔티티 효과",
    "options.particles.minecraft.block_marker": "블록 표식",
    "options.particles.minecraft.damage_indicator": "피해 표시기",
    "options.particles.minecraft.dripping_dripstone_lava": "점적석에 맺힌 용암",
    "options.particles.minecraft.dripping_dripstone_water": "점적석에 맺힌 물",
    "options.particles.minecraft.dripping_honey": "맺힌 꿀",
    "options.particles.minecraft.dripping_lava": "맺힌 용암",
    "options.particles.minecraft.dripping_obsidian_tear": "맺힌 흑요석 눈물",
    "options.particles.minecraft.dripping_water": "맺힌 물",
    "options.particles.minecraft.dust_pillar.tooltip": (
        "철퇴 내려치기 공격 때 생성됩니다."
    ),
    "options.particles.minecraft.dust_plume": "먼지 구름",
    "options.particles.minecraft.end_rod": "엔드 막대",
    "options.particles.minecraft.entity_effect": "엔티티 효과",
    "options.particles.minecraft.falling_nectar": "떨어지는 꽃꿀",
    "options.particles.minecraft.falling_spore_blossom": "떨어지는 포자",
    "options.particles.minecraft.infested": "감염",
    "options.particles.minecraft.scrape": "긁어내기",
    "options.particles.minecraft.sculk_charge": "스컬크 전하",
    "options.particles.minecraft.sculk_charge_pop": "스컬크 전하 터짐",
    "options.particles.minecraft.snowflake": "눈송이",
    "options.particles.minecraft.sonic_boom": "음파 폭발",
    "options.particles.minecraft.splash": "물 튀김",
    "options.particles.minecraft.trial_spawner_detection_ominous": (
        "불길한 시련 생성기 감지"
    ),
    "options.particles.minecraft.vault_connection.tooltip": (
        "플레이어가 금고 근처에 있을 때 생성됩니다."
    ),
    "sodium-extra.option.advanced_item_tooltips": "고급 아이템 툴팁",
    "sodium-extra.option.beacon_beam": "신호기 광선",
    "sodium-extra.option.biome_colors": "생물군계 색상",
    "sodium-extra.option.details": "세부 사항",
    "sodium-extra.option.fog_start": "안개 시작 배율",
    "sodium-extra.option.light_updates": "조명 업데이트",
    "sodium-extra.option.limit_beacon_beam_height": "신호기 광선 높이 제한",
    "sodium-extra.option.overlay_corner.top_left": "좌측 상단",
    "sodium-extra.option.render": "렌더링",
    "sodium-extra.option.sky_colors": "하늘 색상",
    "options.particles.minecraft.ambient_entity_effect.tooltip": (
        "신호기와 신호기가 부여하는 상태 효과에서 방출됩니다."
    ),
    "options.particles.minecraft.angry_villager.tooltip": (
        "주민의 번식이 실패하거나 접근할 수 없는 작업소의 주인이 사라질 때 생성됩니다."
    ),
    "options.particles.minecraft.ash.tooltip": "영혼 모래 골짜기 생물군계의 공중을 떠다닙니다.",
    "options.particles.minecraft.barrier.tooltip": "방벽 아이템을 들고 있을 때 표시됩니다.",
    "options.particles.minecraft.block.tooltip": (
        "블록을 부수거나 솔질할 때, 철 골렘이 걸을 때, 엔티티가 높은 곳에서 떨어질 때, "
        "플레이어나 고양이가 달릴 때, 갑옷 거치대가 부서질 때, 양이 풀을 먹을 때 "
        "생성됩니다."
    ),
    "options.particles.minecraft.block_crumble.tooltip": (
        "크리킹 하트와 연결된 크리킹이 함께 파괴될 때 생성됩니다."
    ),
    "options.particles.minecraft.block_marker.tooltip": (
        "방벽이나 빛 블록을 주로 들고 있을 때 그 위치를 표시합니다."
    ),
    "options.particles.minecraft.bubble.tooltip": (
        "물이 튀는 엔티티 주변과 수중에서 움직일 때 표시됩니다. 가디언의 광선, 낚시찌, "
        "물고기의 이동 흔적, 수중 발사체와 엔더의 눈에서도 방출됩니다."
    ),
    "options.particles.minecraft.bubble_column_up.tooltip": "위로 솟는 거품 기둥을 나타냅니다.",
    "options.particles.minecraft.bubble_pop.tooltip": "거품이 터질 때 생성됩니다.",
    "options.particles.minecraft.campfire_cosy_smoke.tooltip": (
        "모닥불과 영혼 모닥불에서 방출됩니다."
    ),
    "options.particles.minecraft.campfire_signal_smoke.tooltip": (
        "건초 더미 위에 놓은 모닥불과 영혼 모닥불에서 방출됩니다."
    ),
    "options.particles.minecraft.cherry_leaves.tooltip": "벚나무 잎에서 떨어집니다.",
    "options.particles.minecraft.cloud.tooltip": (
        "젖은 스펀지가 네더에서 마를 때와 흉조 효과를 지닌 채 마을에 들어갈 때 "
        "생성됩니다."
    ),
    "options.particles.minecraft.composter.tooltip": "퇴비통에 아이템을 넣을 때 생성됩니다.",
    "options.particles.minecraft.copper_fire_flame": "구리 불꽃",
    "options.particles.minecraft.copper_fire_flame.tooltip": "구리 횃불에서 방출됩니다.",
    "options.particles.minecraft.crimson_spore.tooltip": (
        "진홍빛 숲 생물군계의 공중을 떠다닙니다."
    ),
    "options.particles.minecraft.crit.tooltip": (
        "치명타와 특정 공격 때 생성됩니다. 석궁 발사체와 완전히 당긴 화살 뒤에도 "
        "나타납니다."
    ),
    "options.particles.minecraft.current_down.tooltip": "아래로 흐르는 거품 기둥을 나타냅니다.",
    "options.particles.minecraft.damage_indicator.tooltip": (
        "근접 공격으로 엔티티에게 피해를 줄 때 생성됩니다."
    ),
    "options.particles.minecraft.dolphin.tooltip": "돌고래가 이동한 뒤에 나타납니다.",
    "options.particles.minecraft.dragon_breath.tooltip": (
        "엔더 드래곤의 숨결 공격과 드래곤 화염구, 잔류형 드래곤의 숨결 구름에서 "
        "방출됩니다."
    ),
    "options.particles.minecraft.dripping_dripstone_lava.tooltip": (
        "뾰족한 점적석에 용암 방울이 맺혀 떨어지기 전 모습을 나타냅니다."
    ),
    "options.particles.minecraft.dripping_dripstone_water.tooltip": (
        "뾰족한 점적석에 물방울이 맺혀 떨어지기 전 모습을 나타냅니다."
    ),
    "options.particles.minecraft.dripping_honey.tooltip": (
        "꿀이 가득 찬 벌집과 벌통 아래에 꿀방울이 맺혀 떨어지기 전 모습을 나타냅니다."
    ),
    "options.particles.minecraft.dripping_lava.tooltip": (
        "위쪽에 용암이 있는 블록 아래에 용암 방울이 맺혀 떨어지기 전 모습을 나타냅니다."
    ),
    "options.particles.minecraft.dripping_obsidian_tear.tooltip": (
        "우는 흑요석에 눈물이 맺혀 떨어지기 전 모습을 나타냅니다."
    ),
    "options.particles.minecraft.dripping_water.tooltip": (
        "비가 올 때 나뭇잎, 위쪽에 물이 있는 블록, 젖은 스펀지에 물방울이 맺혀 "
        "떨어지기 전 모습을 나타냅니다."
    ),
    "options.particles.minecraft.dust.tooltip": (
        "가루, 횃불, 중계기, 레버, 레드스톤 광석처럼 전력이 공급된 레드스톤 부품에서 "
        "방출됩니다."
    ),
    "options.particles.minecraft.dust_color_transition.tooltip": (
        "활성화된 스컬크 감지체에서 방출됩니다."
    ),
    "options.particles.minecraft.dust_plume.tooltip": (
        "장식된 도자기에 아이템을 넣을 때 생성됩니다."
    ),
    "options.particles.minecraft.effect.tooltip": "투척용 물약에서 생성됩니다.",
    "options.particles.minecraft.egg_crack.tooltip": (
        "스니퍼 알을 이끼 블록 위에 놓을 때와 알에 금이 갈 때 생성됩니다."
    ),
    "options.particles.minecraft.elder_guardian.tooltip": (
        "엘더 가디언이 채굴 피로를 부여할 때 표시됩니다."
    ),
    "options.particles.minecraft.electric_spark.tooltip": (
        "뇌우 중 피뢰침에서 생성되며 번개가 구리에 떨어질 때도 생성됩니다."
    ),
    "options.particles.minecraft.enchant.tooltip": "책장에서 마법 부여대로 날아갑니다.",
    "options.particles.minecraft.enchanted_hit.tooltip": (
        "날카로움, 강타, 살충, 찌르기처럼 피해를 주는 특정 마법이 부여된 무기로 "
        "엔티티를 공격할 때 생성됩니다."
    ),
    "options.particles.minecraft.end_rod.tooltip": (
        "엔드 막대에서 방출되며 셜커 탄환 뒤에도 나타납니다."
    ),
    "options.particles.minecraft.entity_effect.tooltip": (
        "물약이 묻은 화살, 영역 효과 구름, 잔류형 물약, 주문 시전과 신호기·전달체를 "
        "제외한 여러 상태 효과 원천에서 방출됩니다."
    ),
    "options.particles.minecraft.explosion.tooltip": (
        "폭발과 폭발 방출기에서 생성됩니다. 큰 충격과 엔더 드래곤의 사망 효과에도 "
        "표시됩니다."
    ),
    "options.particles.minecraft.explosion_emitter.tooltip": "폭발 중에 방출됩니다.",
    "options.particles.minecraft.falling_dripstone_lava.tooltip": (
        "뾰족한 점적석에서 용암 방울이 떨어질 때 생성됩니다."
    ),
    "options.particles.minecraft.falling_dripstone_water.tooltip": (
        "뾰족한 점적석에서 물방울이 떨어질 때 생성됩니다."
    ),
    "options.particles.minecraft.falling_dust.tooltip": (
        "모래와 자갈처럼 중력의 영향을 받는 블록에서 떨어집니다."
    ),
    "options.particles.minecraft.falling_honey.tooltip": (
        "꿀이 가득 찬 벌집과 벌통에서 꿀방울이 떨어질 때 생성됩니다."
    ),
    "options.particles.minecraft.falling_lava.tooltip": (
        "위쪽에 용암이 있는 블록에서 용암 방울이 떨어질 때 생성됩니다."
    ),
    "options.particles.minecraft.falling_nectar.tooltip": "꽃가루를 운반하는 벌에서 떨어집니다.",
    "options.particles.minecraft.falling_obsidian_tear.tooltip": (
        "우는 흑요석의 눈물이 떨어질 때 생성됩니다."
    ),
    "options.particles.minecraft.falling_spore_blossom.tooltip": "포자 꽃에서 떨어집니다.",
    "options.particles.minecraft.falling_water.tooltip": (
        "위쪽에 물이 있는 블록, 비가 올 때의 나뭇잎, 젖은 스펀지에서 물방울이 떨어질 "
        "때 생성됩니다."
    ),
    "options.particles.minecraft.firefly": "반딧불이",
    "options.particles.minecraft.firefly.tooltip": (
        "내부 밝기가 13 이하일 때 반딧불이 덤불에서 생성됩니다."
    ),
    "options.particles.minecraft.firework.tooltip": (
        "폭죽 뒤에 나타나며 폭죽 별이 폭발할 때 생성됩니다."
    ),
    "options.particles.minecraft.fishing.tooltip": "낚시 중 물고기의 이동 흔적을 나타냅니다.",
    "options.particles.minecraft.flame.tooltip": (
        "횃불, 화로와 다른 불 원천에서 방출됩니다. 생성기와 마그마 큐브 주변에도 "
        "표시됩니다."
    ),
    "options.particles.minecraft.flash.tooltip": "폭죽 별이 든 폭죽이 폭발할 때 생성됩니다.",
    "options.particles.minecraft.glow.tooltip": "발광 오징어에서 방출됩니다.",
    "options.particles.minecraft.glow_squid_ink.tooltip": (
        "발광 오징어가 공격받을 때 생성됩니다."
    ),
    "options.particles.minecraft.gust.tooltip": (
        "돌풍구가 블록에 부딪힐 때 생성됩니다."
    ),
    "options.particles.minecraft.gust_emitter_large.tooltip": (
        "돌풍구가 블록에 부딪혀 여러 돌풍 입자를 방출할 때 생성됩니다."
    ),
    "options.particles.minecraft.gust_emitter_small.tooltip": (
        "돌풍구가 블록에 부딪혀 작은 돌풍 입자를 터뜨릴 때 생성됩니다."
    ),
    "options.particles.minecraft.happy_villager.tooltip": (
        "뼛가루로 식물 키우기, 거래, 동물 먹이 주기, 수분, 작업소나 침대 차지, 거북이 "
        "알 설치·부화처럼 긍정적인 상호작용 중에 생성됩니다."
    ),
    "options.particles.minecraft.heart.tooltip": (
        "길들이기, 번식, 먹이 주기와 알레이 복제 때 생성됩니다."
    ),
    "options.particles.minecraft.infested.tooltip": (
        "감염 효과를 지닌 엔티티에서 방출됩니다."
    ),
    "options.particles.minecraft.instant_effect.tooltip": (
        "즉시 치유나 즉시 피해 물약이 깨질 때 생성되며 분광 화살 뒤에도 나타납니다."
    ),
    "options.particles.minecraft.item.tooltip": (
        "도구가 부서질 때, 음식을 먹을 때, 물약이나 엔더의 눈처럼 던지거나 사용한 "
        "아이템이 깨질 때 생성됩니다."
    ),
    "options.particles.minecraft.item_cobweb.tooltip": (
        "방직 효과를 지닌 엔티티에서 생성됩니다."
    ),
    "options.particles.minecraft.item_slime.tooltip": (
        "슬라임과 점액질 효과를 지닌 엔티티에서 생성됩니다."
    ),
    "options.particles.minecraft.item_snowball.tooltip": "던진 눈덩이가 깨질 때 생성됩니다.",
    "options.particles.minecraft.landing_honey.tooltip": "떨어진 꿀방울이 닿을 때 생성됩니다.",
    "options.particles.minecraft.landing_lava.tooltip": "떨어진 용암 방울이 닿을 때 생성됩니다.",
    "options.particles.minecraft.landing_obsidian_tear.tooltip": (
        "떨어진 흑요석 눈물이 닿을 때 생성됩니다."
    ),
    "options.particles.minecraft.large_smoke.tooltip": (
        "블레이즈와 불처럼 큰 불 원천에서 방출됩니다. 네더에 물을 놓을 때와 용암과 "
        "물이 만나 여러 돌 블록을 만들 때도 표시됩니다."
    ),
    "options.particles.minecraft.lava.tooltip": "용암과 모닥불에서 방출됩니다.",
    "options.particles.minecraft.light_block.tooltip": (
        "밝기에 관계없이 빛 아이템을 들고 있을 때 표시됩니다."
    ),
    "options.particles.minecraft.mycelium.tooltip": (
        "균사체 위에 표시되며 팬텀의 날개 뒤에도 나타납니다."
    ),
    "options.particles.minecraft.nautilus.tooltip": (
        "전달체와 전달체가 대상으로 삼은 엔티티 쪽으로 날아갑니다."
    ),
    "options.particles.minecraft.note.tooltip": "소리 블록과 주크박스에서 생성됩니다.",
    "options.particles.minecraft.ominous_spawning.tooltip": (
        "불길한 사건 중 불길한 아이템 생성기가 아이템을 생성할 때 표시됩니다."
    ),
    "options.particles.minecraft.pale_oak_leaves": "창백한 참나무 잎",
    "options.particles.minecraft.pale_oak_leaves.tooltip": "창백한 참나무 잎에서 떨어집니다.",
    "options.particles.minecraft.poof.tooltip": (
        "몹이 죽거나 여러 소멸·분출 효과가 일어날 때 생성됩니다. 좀벌레가 돌에 들어갈 "
        "때, 생성기가 몹을 생성할 때, 특정 포효와 폭죽 별이 없는 폭죽이 사라질 때 등이 "
        "해당합니다."
    ),
    "options.particles.minecraft.portal.tooltip": (
        "차원문과 순간이동에서 생성됩니다. 엔더의 눈 뒤에 나타나며 엔더 진주, 엔더 상자, "
        "엔더맨과 엔더마이트 주변에도 표시됩니다."
    ),
    "options.particles.minecraft.raid_omen.tooltip": (
        "습격 징조 효과를 지닌 엔티티에서 방출됩니다."
    ),
    "options.particles.minecraft.rain.tooltip": "비가 올 때 땅에 표시됩니다.",
    "options.particles.minecraft.reverse_portal.tooltip": (
        "충전된 리스폰 정박기에서 방출됩니다."
    ),
    "options.particles.minecraft.scrape.tooltip": "구리의 산화를 긁어낼 때 생성됩니다.",
    "options.particles.minecraft.sculk_charge.tooltip": "스컬크 전하의 이동 경로를 표시합니다.",
    "options.particles.minecraft.sculk_charge_pop.tooltip": (
        "스컬크 전하가 사라질 때 생성됩니다."
    ),
    "options.particles.minecraft.sculk_soul.tooltip": (
        "스컬크 촉매가 활성화되면 그 위에 표시됩니다."
    ),
    "options.particles.minecraft.shriek.tooltip": "활성화된 스컬크 비명체에서 방출됩니다.",
    "options.particles.minecraft.small_flame.tooltip": "양초에서 방출됩니다.",
    "options.particles.minecraft.small_gust.tooltip": (
        "돌풍 충전 효과를 지닌 엔티티에서 방출됩니다."
    ),
    "options.particles.minecraft.smoke.tooltip": (
        "횃불, 모닥불, 화로, 양조기, 블레이즈, 가스트, 위더와 용암처럼 여러 열·마법 "
        "원천에서 방출됩니다. 점화된 TNT와 차원문 관련 효과 같은 특정 동작 중에도 "
        "표시됩니다."
    ),
    "options.particles.minecraft.sneeze.tooltip": "판다가 재채기할 때 생성됩니다.",
    "options.particles.minecraft.snowflake.tooltip": (
        "가루눈 안에 있는 엔티티에서 생성됩니다."
    ),
    "options.particles.minecraft.sonic_boom.tooltip": "워든이 음파 공격을 할 때 생성됩니다.",
    "options.particles.minecraft.soul.tooltip": (
        "영혼 모래나 영혼 흙 위를 영혼 가속 효과로 달릴 때 생성됩니다."
    ),
    "options.particles.minecraft.soul_fire_flame.tooltip": (
        "영혼 횃불과 다른 영혼 불 원천에서 방출됩니다."
    ),
    "options.particles.minecraft.spit.tooltip": "라마가 침을 뱉을 때 생성됩니다.",
    "options.particles.minecraft.splash.tooltip": (
        "물이 튈 때, 비가 튈 때, 낚시할 때와 특정 물 충돌 효과에서 생성됩니다. 늑대가 "
        "물을 털어낼 때도 생성됩니다."
    ),
    "options.particles.minecraft.spore_blossom_air.tooltip": "포자 꽃 주변의 공중을 떠다닙니다.",
    "options.particles.minecraft.squid_ink.tooltip": "오징어가 공격받을 때 생성됩니다.",
    "options.particles.minecraft.sweep_attack.tooltip": "휩쓸기 공격을 할 때 생성됩니다.",
    "options.particles.minecraft.tinted_leaves": "물든 나뭇잎",
    "options.particles.minecraft.tinted_leaves.tooltip": (
        "창백한 참나무와 벚나무를 제외한 대부분의 나뭇잎 블록에서 떨어지며, 원본 "
        "나뭇잎의 색을 따릅니다."
    ),
    "options.particles.minecraft.totem_of_undying.tooltip": (
        "불사의 토템이 발동할 때 생성됩니다."
    ),
    "options.particles.minecraft.trail.tooltip": (
        "크리킹과 크리킹 하트 사이 또는 아이블라섬이 열리고 닫힐 때처럼 두 지점 사이에 "
        "선을 그립니다."
    ),
    "options.particles.minecraft.trial_omen.tooltip": (
        "시련 징조 효과를 지닌 엔티티에서 방출됩니다."
    ),
    "options.particles.minecraft.trial_spawner_detection.tooltip": (
        "시련 생성기가 활성화될 때 생성됩니다."
    ),
    "options.particles.minecraft.trial_spawner_detection_ominous.tooltip": (
        "불길한 시련 생성기가 활성화될 때 생성됩니다."
    ),
    "options.particles.minecraft.underwater.tooltip": "물속의 공중을 떠다닙니다.",
    "options.particles.minecraft.vibration.tooltip": (
        "소리 원천에서 스컬크 감지체나 워든으로, 소리 블록에서 알레이로 이동합니다."
    ),
    "options.particles.minecraft.warped_spore.tooltip": (
        "뒤틀린 숲 생물군계의 공중을 떠다닙니다."
    ),
    "options.particles.minecraft.wax_off.tooltip": "구리에서 밀랍을 긁어낼 때 생성됩니다.",
    "options.particles.minecraft.wax_on.tooltip": "벌집 조각으로 구리에 밀랍을 칠할 때 생성됩니다.",
    "options.particles.minecraft.white_ash.tooltip": (
        "현무암 삼각주 생물군계의 공중을 떠다닙니다."
    ),
    "options.particles.minecraft.white_smoke.tooltip": (
        "제작기가 아이템을 내보낼 때 방출됩니다."
    ),
    "options.particles.minecraft.witch.tooltip": "마녀에게서 방출됩니다.",
    "sodium-extra.option.advanced_item_tooltips.tooltip": (
        "아이템 툴팁에 식별자와 내구도를 표시합니다."
    ),
    "sodium-extra.option.advancement_toast.tooltip": "발전 과제 팝업(토스트)을 표시합니다.",
    "sodium-extra.option.animate_fire.tooltip": "불 애니메이션을 처리합니다.",
    "sodium-extra.option.animate_lava.tooltip": "용암 애니메이션을 처리합니다.",
    "sodium-extra.option.animate_portal.tooltip": "차원문 애니메이션을 처리합니다.",
    "sodium-extra.option.animate_sculk_sensor.tooltip": (
        "스컬크 감지체 애니메이션을 처리합니다."
    ),
    "sodium-extra.option.animate_water.tooltip": "물 애니메이션을 처리합니다.",
    "sodium-extra.option.animations_all.tooltip": "모든 애니메이션을 처리합니다.",
    "sodium-extra.option.armor_stands.tooltip": "갑옷 거치대를 렌더링합니다.",
    "sodium-extra.option.beacon_beam.tooltip": "신호기 광선을 렌더링합니다.",
    "sodium-extra.option.biome_colors.tooltip": (
        "적용할 수 있는 곳에 생물군계 기반 색상을 사용합니다."
    ),
    "sodium-extra.option.block_animations.tooltip": "블록 애니메이션을 처리합니다.",
    "sodium-extra.option.block_break.tooltip": "블록 파괴 입자를 처리합니다.",
    "sodium-extra.option.block_breaking.tooltip": "블록을 부수는 중의 입자를 처리합니다.",
    "sodium-extra.option.cloud_distance.tooltip": (
        "플레이어로부터 구름을 렌더링할 거리를 설정합니다."
    ),
    "sodium-extra.option.cloud_height.tooltip": "구름을 렌더링할 높이를 설정합니다.",
    "sodium-extra.option.enchanting_table_book.tooltip": (
        "마법 부여대의 책을 렌더링합니다."
    ),
    "sodium-extra.option.fog.tooltip": (
        "차원별 지형 안개 거리를 조절합니다.\n다중 차원 안개를 끄면 단일 안개로 안개를 "
        "조절할 수 있습니다.\n0: 바닐라 안개 설정 사용\n1–32: 안개 거리를 청크 단위로 "
        "설정\n33: 최대 안개 거리(사실상 안개 비활성화)"
    ),
    "sodium-extra.option.fog_start.tooltip": (
        "플레이어와 얼마나 가까운 곳에서 지형 안개가 시작될지 조절합니다."
    ),
    "sodium-extra.option.fog_type.atmospheric.tooltip": (
        "대기와 날씨로 생기는 안개를 조절합니다."
    ),
    "sodium-extra.option.fog_type.cloud_end": "%s - 구름 끝",
    "sodium-extra.option.fog_type.cloud_end.tooltip": (
        "안개가 구름에 섞이는 끝 거리를 조절합니다(끝 배율)."
    ),
    "sodium-extra.option.fog_type.default.tooltip": "%s의 안개 표시와 거리를 전환합니다.",
    "sodium-extra.option.fog_type.dimension_or_boss": "차원 또는 보스 안개",
    "sodium-extra.option.fog_type.dimension_or_boss.tooltip": (
        "엔더 드래곤 전투처럼 차원 효과나 보스 구역에서 발생하는 안개를 조절합니다."
    ),
    "sodium-extra.option.fog_type.environment_end": "%s - 환경 끝",
    "sodium-extra.option.fog_type.environment_end.tooltip": (
        "환경 안개가 뻗는 끝 거리를 조절합니다(끝 배율)."
    ),
    "sodium-extra.option.fog_type.environment_start": "%s - 환경 시작",
    "sodium-extra.option.fog_type.environment_start.tooltip": (
        "환경 안개가 시작되는 지점을 조절합니다(시작 배율)."
    ),
    "sodium-extra.option.fog_type.lava": "용암 안개",
    "sodium-extra.option.fog_type.lava.tooltip": "용암에 잠겼을 때의 안개를 조절합니다.",
    "sodium-extra.option.fog_type.powder_snow": "가루눈 안개",
    "sodium-extra.option.fog_type.powder_snow.tooltip": (
        "가루눈 안에 있을 때의 안개를 조절합니다."
    ),
    "sodium-extra.option.fog_type.render_distance_end": "%s - 렌더링 끝",
    "sodium-extra.option.fog_type.render_distance_end.tooltip": (
        "렌더링 거리 경계의 페이드 끝을 조절합니다(끝 배율)."
    ),
    "sodium-extra.option.fog_type.render_distance_start": "%s - 렌더링 시작",
    "sodium-extra.option.fog_type.render_distance_start.tooltip": (
        "렌더링 거리 경계의 페이드 시작을 조절합니다(시작 배율)."
    ),
    "sodium-extra.option.fog_type.sky_end": "%s - 하늘 끝",
    "sodium-extra.option.fog_type.sky_end.tooltip": (
        "안개가 하늘에 섞이는 끝 거리를 조절합니다(끝 배율)."
    ),
    "sodium-extra.option.fog_type.water": "물 안개",
    "sodium-extra.option.fog_type.water.tooltip": "물속의 안개를 조절합니다.",
    "sodium-extra.option.global_fog": "전체 안개",
    "sodium-extra.option.global_fog.tooltip": "모든 안개 효과를 렌더링합니다.",
    "sodium-extra.option.instant_sneak.tooltip": (
        "웅크릴 때 카메라의 부드러운 움직임을 비활성화합니다."
    ),
    "sodium-extra.option.item_frame_name_tag.tooltip": (
        "아이템 액자의 이름표를 표시합니다."
    ),
    "sodium-extra.option.item_frames.tooltip": "아이템 액자를 렌더링합니다.",
    "sodium-extra.option.light_updates_warning": "조명 업데이트 경고",
    "sodium-extra.option.light_updates_warning.tooltip": (
        "디버그 HUD의 조명 업데이트 경고 메시지를 비활성화합니다. 조명 업데이트가 "
        "성능과 화면 정확도에 미치는 영향을 이해하는 경우에만 끄세요."
    ),
    "sodium-extra.option.light_updates.tooltip": (
        "조명 업데이트를 처리합니다. 끄면 청크 생성 시 조명이 잘못될 수 있습니다. 영향을 "
        "이해하는 경우에만 끄세요."
    ),
    "sodium-extra.option.limit_beacon_beam_height.tooltip": (
        "신호기 광선을 월드의 최대 높이까지만 표시합니다."
    ),
    "sodium-extra.option.linear_flat_color_blender.tooltip": (
        "블록 면에는 선형 혼합을 적용하지 않고 생물군계 색상만 선형으로 혼합합니다."
    ),
    "sodium-extra.option.moon.tooltip": "달을 렌더링합니다.",
    "sodium-extra.option.multi_dimension_fog.tooltip": (
        "차원별 안개 슬라이더를 활성화합니다. 끄면 단일 안개 슬라이더를 사용합니다.\n이 "
        "옵션을 바꾼 뒤에는 메뉴를 닫았다가 다시 열어 안개 슬라이더를 갱신하세요."
    ),
    "sodium-extra.option.overlay_corner.tooltip": (
        "오버레이(FPS와 좌표)를 표시할 모서리를 설정합니다."
    ),
    "sodium-extra.option.paintings.tooltip": "그림을 렌더링합니다.",
    "sodium-extra.option.particles.tooltips": "%s 입자를 처리합니다.",
    "sodium-extra.option.particles_all.tooltip": "모든 입자를 처리합니다.",
    "sodium-extra.option.piston.tooltip": "피스톤이 늘어나는 애니메이션을 렌더링합니다.",
    "sodium-extra.option.player_name_tag.tooltip": "플레이어 이름표를 표시합니다.",
    "sodium-extra.option.prevent_shaders.tooltip": (
        "바닐라 셰이더 효과가 불러와지는 것을 막습니다. 관전 중 거미의 시야 왜곡 등이 "
        "해당합니다."
    ),
    "sodium-extra.option.rain_snow.tooltip": "비와 눈을 렌더링합니다.",
    "sodium-extra.option.rain_splash.tooltip": "빗물이 튀는 입자를 렌더링합니다.",
    "sodium-extra.option.recipe_toast.tooltip": "제작법 팝업(토스트)을 표시합니다.",
    "sodium-extra.option.reduce_resolution_on_mac.tooltip": (
        "macOS의 Retina 디스플레이에서 해상도를 절반으로 낮춰 성능을 개선합니다.\n이 "
        "옵션을 바꾸면 다시 시작해야 합니다."
    ),
    "sodium-extra.option.resolution.tooltip": "게임의 전체 화면 해상도를 설정합니다.",
    "sodium-extra.option.show_coordinates.tooltip": "오버레이에 플레이어 좌표를 표시합니다.",
    "sodium-extra.option.show_fps.tooltip": "오버레이에 현재 FPS를 표시합니다.",
    "sodium-extra.option.show_fps_extended.tooltip": (
        "오버레이의 현재 FPS 옆에 최대, 평균, 최소 FPS 통계를 추가로 표시합니다."
    ),
    "sodium-extra.option.single_fog.tooltip": (
        "모든 차원의 지형 안개 거리를 조절합니다.\n다중 차원 안개를 켜면 차원별로 "
        "안개를 조절할 수 있습니다.\n0: 바닐라 안개 설정 사용\n1–32: 안개 거리를 청크 "
        "단위로 설정\n33: 최대 안개 거리(사실상 안개 비활성화)"
    ),
    "sodium-extra.option.sky.tooltip": "하늘을 렌더링합니다.",
    "sodium-extra.option.sky_colors.tooltip": "생물군계 기반 하늘 색상을 적용합니다.",
    "sodium-extra.option.stars.tooltip": "별을 렌더링합니다.",
    "sodium-extra.option.steady_debug_hud": "고정 주기 디버그 HUD",
    "sodium-extra.option.steady_debug_hud.tooltip": (
        "고정 주기 디버그 HUD 갱신 간격에 따라 디버그 HUD를 일정한 주기로 갱신합니다."
    ),
    "sodium-extra.option.steady_debug_hud_refresh_interval": (
        "고정 주기 디버그 HUD 갱신 간격"
    ),
    "sodium-extra.option.steady_debug_hud_refresh_interval.tooltip": (
        "디버그 HUD를 갱신할 주기를 틱 단위로 설정합니다."
    ),
    "sodium-extra.option.sun.tooltip": "태양을 렌더링합니다.",
    "sodium-extra.option.system_toast.tooltip": "시스템 팝업(토스트)을 표시합니다.",
    "sodium-extra.option.text_contrast.tooltip": (
        "FPS/좌표 오버레이의 가독성을 조절합니다.\n- 없음: 흰색 글자만 표시\n- 배경: "
        "디버그 화면과 같은 배경 추가\n- 그림자: 흰색 글자에 그림자 추가"
    ),
    "sodium-extra.option.toasts.tooltip": "발전 과제와 제작법 팝업(토스트)을 표시합니다.",
    "sodium-extra.option.tutorial_toast.tooltip": "튜토리얼 팝업(토스트)을 표시합니다.",
    "sodium-extra.option.use_adaptive_sync.tooltip": (
        "V-Sync가 프레임 도중에 전환되고 때때로 스스로 꺼지도록 하여 반응성을 개선할 수 "
        "있습니다. 일부 GPU 드라이버에서는 문제가 생길 수 있습니다."
    ),
    "sodium-extra.option.use_fast_random.tooltip": (
        "블록 렌더링에 더 빠른 난수 함수를 사용합니다. 무작위로 회전되는 일부 텍스처의 "
        "모양이 바닐라와 달라질 수 있습니다."
    ),
    "sodium-extra.overlay.coordinates": "X: %s, Y: %s, Z: %s",
    "sodium-extra.overlay.coordinates_unavailable": (
        "좌표를 표시할 수 없습니다(reducedDebugInfo가 활성화됨)."
    ),
    "sodium-extra.overlay.fps": "%s FPS",
    "sodium-extra.suggestRSO.header": "제안: Reese's Sodium Options 설치",
    "sodium-extra.suggestRSO.message": (
        "Sodium Extra와 함께 Reese's Sodium Options를 설치하는 것을 강력히 권장합니다. "
        "기능이 계속 늘어나 Sodium의 비디오 설정 화면은 이 모드 없이 탐색하기 어려울 수 "
        "있습니다."
    ),
}


def find_jar(namespace: str) -> Path:
    """현재 설치본에서 네임스페이스의 JAR 하나를 찾아요."""
    matches = sorted((resolve_source_root() / "mods").glob(str(MODS[namespace]["jar"])))
    if len(matches) != 1:
        raise FileNotFoundError(f"{namespace} JAR이 정확히 한 개가 아니에요: {matches}")
    return matches[0]


def read_language(namespace: str, locale: str) -> dict[str, str]:
    """JAR의 언어 JSON 객체를 읽어요."""
    with ZipFile(find_jar(namespace)) as archive:
        internal = f"assets/{namespace}/lang/{locale}.json"
        if internal not in archive.namelist():
            return {}
        value = json.loads(archive.read(internal))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(text, str) for key, text in value.items()
    ):
        raise TypeError(f"{namespace} {locale} 언어 파일이 문자열 객체가 아니에요")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 안정된 형식으로 기록해요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def split_balanced(text: str, source_lines: list[str]) -> list[str]:
    """문장의 단어를 원문 줄 길이 비율에 맞춰 같은 줄 수로 나눠요."""
    words = text.split()
    line_count = len(source_lines)
    if line_count == 1:
        return [" ".join(words)]
    if len(words) < line_count:
        raise ValueError(f"줄 수를 보존할 단어가 부족해요: {text!r}, {line_count}줄")
    weights = [max(1, len(LINE_CODE.sub("", line))) for line in source_lines]
    lines = []
    position = 0
    for index in range(line_count - 1):
        remaining_lines = line_count - index
        maximum = len(words) - (remaining_lines - 1)
        remaining_text = " ".join(words[position:])
        desired = len(remaining_text) * weights[index] / sum(weights[index:])
        choices = range(position + 1, maximum + 1)
        end = min(
            choices,
            key=lambda candidate: abs(
                len(" ".join(words[position:candidate])) - desired
            ),
        )
        lines.append(" ".join(words[position:end]))
        position = end
    lines.append(" ".join(words[position:]))
    return lines


def match_line_structure(source: str, target: str) -> str:
    """번역 후보의 뜻을 유지하며 원문의 실제 줄바꿈과 줄 시작 서식을 복원해요."""
    if source.count("\n") == target.count("\n"):
        return target
    source_paragraphs = source.split("\n\n")
    target_paragraphs = target.split("\n\n")
    if len(source_paragraphs) != len(target_paragraphs):
        raise ValueError(f"문단 구조가 달라요: {source!r} != {target!r}")
    rebuilt = []
    for source_paragraph, target_paragraph in zip(
        source_paragraphs, target_paragraphs, strict=True
    ):
        source_lines = source_paragraph.split("\n")
        prefixes = []
        for line in source_lines:
            matched = LINE_CODE.match(line)
            prefixes.append(matched.group(0) if matched else "")
        body_lines = []
        for line in target_paragraph.split("\n"):
            body_lines.append(LINE_CODE.sub("", line, count=1))
        balanced = split_balanced(" ".join(body_lines), source_lines)
        rebuilt.append(
            "\n".join(
                prefix + line for prefix, line in zip(prefixes, balanced, strict=True)
            )
        )
    return "\n\n".join(rebuilt)


def normalize_fancymenu(key: str, source: str, candidate: str) -> str:
    """FancyMenu 후보 전체를 용어집 수준으로 재검수하고 줄 구조를 맞춰요."""
    target = candidate
    for old, new in FANCY_REPLACEMENTS:
        target = target.replace(old, new)
    target = FANCY_OVERRIDES.get(key, target)
    return match_line_structure(source, target)


def translated_language(namespace: str) -> dict[str, str]:
    """현재 영어 원문 순서대로 네임스페이스의 확정 번역을 만들어요."""
    english = read_language(namespace, "en_us")
    candidate = read_language(namespace, "ko_kr")
    if namespace == "fancymenu":
        if set(candidate) != set(english):
            raise ValueError("FancyMenu 한국어 후보 키가 현재 영어 원문과 달라요")
        return {
            key: normalize_fancymenu(key, source, candidate[key])
            for key, source in english.items()
        }
    if namespace == "sodium-extra":
        if set(candidate) != set(english):
            raise ValueError("Sodium Extra 한국어 후보 키가 현재 영어 원문과 달라요")
        return {key: SODIUM_OVERRIDES.get(key, candidate[key]) for key in english}
    if namespace == "iris":
        missing = set(english) - set(candidate)
        if missing - set(IRIS_OVERRIDES):
            raise ValueError(
                f"Iris에 번역하지 않은 누락 키가 있어요: {sorted(missing)}"
            )
        return {key: IRIS_OVERRIDES.get(key, candidate.get(key, "")) for key in english}
    exact = {
        "extremesoundmuffler": EXTREME_SOUND_TEXT,
        "fzzy_config": FZZY_TEXT,
        "iris_search": IRIS_SEARCH_TEXT,
    }[namespace]
    if set(exact) != set(english):
        raise ValueError(
            f"{namespace} 확정 번역 키가 현재 영어와 달라요: "
            f"missing={sorted(set(english) - set(exact))}, "
            f"extra={sorted(set(exact) - set(english))}"
        )
    translated = {}
    for key in english:
        target = exact[key]
        if namespace == "fzzy_config":
            target = FZZY_OVERRIDES.get(key, target).replace("∽", "§")
        if namespace == "extremesoundmuffler" and key in EXTREME_ESCAPED_LINE_KEYS:
            target = target.replace("\n", "\\n")
        translated[key] = target
    return translated


def build() -> dict[str, object]:
    """6개 모드의 현재 영어 원문 4,189개를 모두 확정 산출물로 만들어요."""
    reports = []
    errors = []
    for namespace in MODS:
        english = read_language(namespace, "en_us")
        candidate = read_language(namespace, "ko_kr")
        try:
            korean = translated_language(namespace)
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{namespace}: {exc}")
            continue
        write_json(WORK_ROOT / namespace / "ko_kr.json", korean)
        write_json(OUTPUT_ROOT / namespace / "lang/ko_kr.json", korean)
        reused = sum(1 for key, value in korean.items() if candidate.get(key) == value)
        reports.append(
            {
                "namespace": namespace,
                "english_keys": len(english),
                "bundled_candidate_keys": len(candidate),
                "bundled_candidate_values_reused": reused,
                "new_or_corrected_values": len(korean) - reused,
                "status": "complete",
            }
        )
    report = {
        "family": FAMILY,
        "mods": reports,
        "english_keys": sum(int(value["keys"]) for value in MODS.values()),
        "errors": errors,
        "status": "complete"
        if not errors and len(reports) == len(MODS)
        else "incomplete",
    }
    write_json(WORK_ROOT / "language_build.json", report)
    return report


def prepare() -> dict[str, object]:
    """현재 JAR의 영어 원문과 한국어 후보를 작업 폴더에 기록해요."""
    reports = []
    total_keys = 0
    total_candidates = 0
    for namespace in MODS:
        jar = find_jar(namespace)
        english = read_language(namespace, "en_us")
        korean = read_language(namespace, "ko_kr")
        expected = int(MODS[namespace]["keys"])
        if len(english) != expected:
            raise ValueError(
                f"{namespace} 영어 키 수가 달라요: {len(english)} != {expected}"
            )
        write_json(WORK_ROOT / namespace / "en_us.json", english)
        if korean:
            write_json(WORK_ROOT / namespace / "bundled_ko_kr.json", korean)
        reports.append(
            {
                "namespace": namespace,
                "jar": jar.name,
                "jar_size": jar.stat().st_size,
                "jar_mtime_ns": jar.stat().st_mtime_ns,
                "english_keys": len(english),
                "bundled_korean_keys": len(korean),
                "missing_candidate_keys": len(set(english) - set(korean)),
                "extra_candidate_keys": len(set(korean) - set(english)),
            }
        )
        total_keys += len(english)
        total_candidates += len(korean)
    report = {
        "family": FAMILY,
        "mods": reports,
        "english_keys": total_keys,
        "bundled_korean_candidate_keys": total_candidates,
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", report)
    return report


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


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR 데이터와 FTB Quests·KubeJS의 별도 표시 문구를 감사해요."""
    instance = resolve_source_root()
    errors = []
    jar_reports = []
    for namespace in MODS:
        jar = find_jar(namespace)
        data_json_files = []
        invalid_json = []
        localized_fields = []
        direct_fields = []
        guide_entries = []
        with ZipFile(jar) as archive:
            for name in sorted(archive.namelist()):
                lower = name.lower()
                if lower.endswith((".md", ".txt", ".json")) and any(
                    segment in lower
                    for segment in ("/book/", "/guide/", "/manual/", "patchouli")
                ):
                    guide_entries.append(name)
                if not lower.startswith("data/") or not lower.endswith(".json"):
                    continue
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
                        localized_fields.append(row)
                    elif isinstance(child, str):
                        direct_fields.append(row)
        if invalid_json:
            errors.extend(f"{namespace}: {message}" for message in invalid_json)
        if direct_fields:
            errors.append(
                f"{namespace} 데이터에 직접 표시 문구가 있어요: {direct_fields}"
            )
        if guide_entries:
            errors.append(
                f"{namespace} JAR에 별도 가이드 후보가 있어요: {guide_entries}"
            )
        jar_reports.append(
            {
                "namespace": namespace,
                "jar": jar.name,
                "data_json_files": len(data_json_files),
                "localized_visible_fields": localized_fields,
                "direct_visible_fields": direct_fields,
                "guide_candidates": guide_entries,
                "invalid_json": invalid_json,
            }
        )

    references = {"ftbquests": [], "kubejs": [], "read_errors": []}
    suffixes = {".cfg", ".js", ".json", ".snbt", ".toml", ".txt"}
    for label, base in (
        ("ftbquests", instance / "config/ftbquests/quests"),
        ("kubejs", instance / "kubejs"),
    ):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                references["read_errors"].append(f"{path}: {exc}")
                continue
            counts = {
                namespace: text.lower().count(f"{namespace.lower()}:")
                for namespace in MODS
            }
            if not any(counts.values()):
                continue
            visible_lines = []
            for number, line in enumerate(text.splitlines(), 1):
                if not any(
                    f"{namespace.lower()}:" in line.lower() for namespace in MODS
                ):
                    continue
                if re.search(
                    r"(?i)(?:custom_name|displayname|display_name|lore|subtitle|title|tooltip)"
                    r"\s*[:=(]",
                    line,
                ):
                    visible_lines.append(number)
            row = {
                "path": path.relative_to(instance).as_posix(),
                "namespace_occurrences": counts,
                "visible_namespace_candidate_lines": visible_lines,
            }
            references[label].append(row)
            if visible_lines:
                errors.append(f"{label}에 직접 표시 문구 후보가 있어요: {row}")
    errors.extend(str(message) for message in references["read_errors"])
    report = {
        "family": FAMILY,
        "jars": jar_reports,
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


def preserved_errors(label: str, source: str, target: str) -> list[str]:
    """자리표시자·서식·숫자·줄바꿈·URL 보존을 확인해요."""
    errors = []
    for name, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식 코드", FORMAT_CODE),
        ("숫자", NUMBER),
        ("URL", URL),
    ):
        source_values = Counter(pattern.findall(source))
        target_values = Counter(pattern.findall(target))
        if source_values != target_values:
            errors.append(
                f"{label} {name} 불일치: {dict(source_values)} != {dict(target_values)}"
            )
    if source.count("\n") != target.count("\n"):
        errors.append(
            f"{label} 실제 줄바꿈 수 불일치: "
            f"{source.count(chr(10))} != {target.count(chr(10))}"
        )
    if source.count("\\n") != target.count("\\n"):
        source_escaped_lines = source.count("\\n")
        target_escaped_lines = target.count("\\n")
        errors.append(
            f"{label} 이스케이프 줄바꿈 수 불일치: "
            f"{source_escaped_lines} != {target_escaped_lines}"
        )
    return errors


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


def verify_language() -> tuple[dict[str, object], list[str]]:
    """6개 모드 4,189개 키의 구조와 확정 번역값을 전부 검증해요."""
    errors = []
    mod_reports = []
    forbidden_fancy = tuple(old for old, _new in FANCY_REPLACEMENTS)
    no_hangul_extra = {"fancymenu.overlay.menu_bar.user_interface"}
    for namespace in MODS:
        english = read_language(namespace, "en_us")
        candidate = read_language(namespace, "ko_kr")
        expected = translated_language(namespace)
        work, work_errors = load_json_without_duplicates(
            WORK_ROOT / namespace / "ko_kr.json"
        )
        output, output_errors = load_json_without_duplicates(
            OUTPUT_ROOT / namespace / "lang/ko_kr.json"
        )
        current_errors = work_errors + output_errors
        if not isinstance(work, dict) or not isinstance(output, dict):
            errors.extend(f"{namespace}: {message}" for message in current_errors)
            continue
        if list(english) != list(work) or list(english) != list(output):
            current_errors.append("언어 키 또는 순서가 현재 영어 원문과 달라요")
        if work != output or output != expected:
            current_errors.append("작업본·산출물·확정 번역값이 서로 달라요")
        same_as_source = set()
        no_hangul = set()
        foreign_script = {}
        empty_values = []
        for key, source in english.items():
            target = output.get(key)
            if not isinstance(target, str):
                current_errors.append(f"문자열이 아닌 번역값이 있어요: {key}")
                continue
            current_errors.extend(preserved_errors(key, source, target))
            if source and not target:
                empty_values.append(key)
            if source and source == target:
                same_as_source.add(key)
            if target and not re.search(r"[가-힣]", target):
                no_hangul.add(key)
            foreign = sorted(set(FOREIGN_SCRIPT.findall(target)))
            if foreign:
                foreign_script[key] = foreign
        if empty_values:
            current_errors.append(f"빈 번역값이 있어요: {empty_values}")
        expected_same = INTENTIONAL_SAME_KEYS[namespace]
        if same_as_source != expected_same:
            current_errors.append(
                "영어와 같은 값 검토 결과가 달라요: "
                f"missing={sorted(expected_same - same_as_source)}, "
                f"unexpected={sorted(same_as_source - expected_same)}"
            )
        allowed_no_hangul = expected_same | (
            no_hangul_extra if namespace == "fancymenu" else set()
        )
        unexpected_no_hangul = no_hangul - allowed_no_hangul
        if unexpected_no_hangul:
            current_errors.append(
                f"한국어가 없는 값이 있어요: {sorted(unexpected_no_hangul)}"
            )
        if foreign_script:
            current_errors.append(f"한국어 외 문자권 문자가 남았어요: {foreign_script}")
        forbidden_hits = {}
        if namespace == "fancymenu":
            for key, target in output.items():
                hits = sorted(term for term in forbidden_fancy if term in target)
                if hits:
                    forbidden_hits[key] = hits
        if namespace == "fzzy_config":
            for key, target in output.items():
                if "∽" in target:
                    forbidden_hits[key] = ["∽"]
        if forbidden_hits:
            current_errors.append(f"폐기한 후보 용어가 남았어요: {forbidden_hits}")
        reused = sum(
            1 for key, target in output.items() if candidate.get(key) == target
        )
        mod_reports.append(
            {
                "namespace": namespace,
                "keys": len(output),
                "expected_keys": MODS[namespace]["keys"],
                "bundled_candidate_keys": len(candidate),
                "bundled_candidate_values_reused": reused,
                "new_or_corrected_values": len(output) - reused,
                "intentional_technical_same_values": sorted(same_as_source),
                "no_hangul_values": sorted(no_hangul),
                "foreign_script_values": foreign_script,
                "forbidden_candidate_terms": forbidden_hits,
                "errors": current_errors,
                "status": "complete" if not current_errors else "incomplete",
            }
        )
        errors.extend(f"{namespace}: {message}" for message in current_errors)
    report = {
        "mods": mod_reports,
        "keys": sum(row["keys"] for row in mod_reports),
        "expected_keys": sum(int(value["keys"]) for value in MODS.values()),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def deployment_paths() -> set[str]:
    """이 모음이 실제 인스턴스에 적용할 정확한 상대 경로를 반환해요."""
    return {
        f"resourcepacks/ATM10_Korean/assets/{namespace}/lang/ko_kr.json"
        for namespace in MODS
    }


def verify() -> tuple[dict[str, object], list[str]]:
    """언어 구조와 전체 표시 표면 감사를 함께 검증해요."""
    language, language_errors = verify_language()
    surface, surface_errors = audit()
    errors = language_errors + surface_errors
    report = {
        "family": FAMILY,
        "language": language,
        "surface_audit": surface["status"],
        "ftbquests": surface["ftbquests_display_work"],
        "kubejs": surface["kubejs_display_work"],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    reused = sum(row["bundled_candidate_values_reused"] for row in language["mods"])
    changed = sum(row["new_or_corrected_values"] for row in language["mods"])
    translation_report = {
        "family": FAMILY,
        "reviewed_language_keys": language["keys"],
        "bundled_korean_candidate_keys": sum(
            row["bundled_candidate_keys"] for row in language["mods"]
        ),
        "existing_korean_values_reused": reused,
        "new_or_corrected_language_values": changed,
        "ftbquests_work": surface["ftbquests_display_work"],
        "kubejs_work": surface["kubejs_display_work"],
        "status": report["status"],
    }
    write_json(WORK_ROOT / "translation_report.json", translation_report)
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = (
        json.loads(deployment_path.read_text(encoding="utf-8"))
        if deployment_path.is_file()
        else None
    )
    completion = {
        "family": FAMILY,
        "language_keys": language["keys"],
        "existing_korean_values_reused": reused,
        "new_or_corrected_translations": changed,
        "ftbquests_work": surface["ftbquests_display_work"],
        "kubejs_work": surface["kubejs_display_work"],
        "output_files": sorted(deployment_paths()),
        "surface_audit": surface["status"],
        "family_validation": report["status"],
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
    verification, verification_errors = verify()
    result = {
        "deployment": report,
        "verification": verification["status"],
        "status": (
            "complete" if not errors and not verification_errors else "incomplete"
        ),
    }
    return result, errors + verification_errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "build", "audit", "verify", "record-deployment", "all"),
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
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        result, _ = record_deployment(args.manifest)
    else:
        prepared = prepare()
        built = build()
        verification, verification_errors = verify()
        result = {
            "prepare": prepared,
            "build": built,
            "verify": verification,
            "status": "complete" if not verification_errors else "incomplete",
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"prepared", "complete"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
