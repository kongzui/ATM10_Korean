#!/usr/bin/env python3
"""FTB Ultimine의 전체 번역과 설정·퀘스트·KubeJS 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from build_ae2_quests import flatten, parse_language_snbt
from local_paths import PROJECT_ROOT, resolve_source_root

WORK_ROOT = PROJECT_ROOT / "working/common_ui/convenience/ftbultimine"
WORKING = WORK_ROOT / "ko_kr.json"
OVERRIDES = WORK_ROOT / "recheck_overrides.json"
REPORT = WORK_ROOT / "recheck_20260820.json"
OUTPUT = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/ftbultimine/lang/ko_kr.json"
)
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
QUEST_COMMON = PROJECT_ROOT / "working/ftbquests/common_chapter_overrides.json"
QUEST_OWNER = PROJECT_ROOT / "working/mekanism/quests/mekanism_reactors/ko_kr.json"
ANNOUNCEMENT_OUTPUT = (
    PROJECT_ROOT
    / "output/overrides/kubejs/server_scripts/announcements/announcements.js"
)
GLOSSARY = PROJECT_ROOT / "glossary/README.md"

EXPECTED_JAR = "ftb-ultimine-neoforge-2101.1.15.jar"
EXPECTED_JAR_SHA256 = "1393a85ceb6e4794450d5f06043e3a033278e31b86de8e03950d8b87604b2213"
EXPECTED_CLIENT_CONFIG_SHA256 = (
    "67dadd3f0812bc01a0b0ca6fb204961512ce1332e97fe42dba2cb57813a496ef"
)
EXPECTED_SERVER_CONFIG_SHA256 = (
    "4a68193e0599b77987a94b6f31a6fe11ac227eb07e6daba898d446381598498b"
)
EXPECTED_CLIENT_FIELDS = {
    "general": {
        "require_ultimine_key_for_cycling",
        "shape_feedback_hotbar_message",
    },
    "overlay": {
        "overlay_inset_x",
        "overlay_inset_y",
        "overlay_pos",
        "overlay_scale",
        "require_sneak_for_menu",
        "shape_menu_context_lines",
    },
    "rendering": {"preview_line_alpha", "render_outline"},
}
EXPECTED_SERVER_FIELDS = {
    "costs_limits": {
        "exhaustion_per_block",
        "experience_per_block",
        "max_blocks",
        "require_tool",
        "require_valid_tool_for_block",
        "ultimine_cooldown",
    },
    "features": {
        "right_click_axe",
        "right_click_crystals",
        "right_click_harvesting",
        "right_click_hoe",
        "right_click_shovel",
        "single_crop_harvesting",
    },
    "misc": {
        "cancel_on_block_break_fail",
        "merge_tags",
        "merge_tags_shaped",
        "prevent_tool_break",
    },
}
EXPECTED_CLASS_REFERENCE_KEYS = {
    "key.ftbultimine",
    "key.categories.ftbultimine",
    "ftbultimine.info.base",
    "ftbultimine.info.active",
    "ftbultimine.info.not_active",
    "ftbultimine.info.no_valid_block",
    "ftbultimine.info.no_block_targeted",
    "ftbultimine.info.no_food",
    "ftbultimine.info.no_tool",
    "ftbultimine.info.no_permission",
    "ftbultimine.info.denied_tool",
    "ftbultimine.info.other_restriction",
    "ftbultimine.info.cooldown",
    "ftbultimine.info.blocks",
    "ftbultimine.info.partial_render",
    "ftbultimine.change_shape.next",
    "ftbultimine.change_shape.prev",
    "ftbultimine.change_shape",
    "ftbultimine.change_shape.short",
    "ftbultimine.change_shape.no_shift",
    "ftbultimine.client_settings",
    "ftbultimine.server_settings",
    "ftbultimine.modifier.max_blocks",
    "ftbultimine.modifier.cooldown",
    "ftbultimine.modifier.exhaustion",
    "ftbultimine.modifier.experience",
}
EXPECTED_OVERRIDES = {
    "ftbultimine.info.base": "FTB Ultimine: %s",
    "ftbultimine.info.no_valid_block": "Ultimine 대상 블록이 아닙니다",
    "ftbultimine.info.no_experience": "경험치가 부족합니다",
    "ftbultimine.info.blocks": "블록 %d개 채굴",
    "ftbultimine.info.partial_render": "블록 %d개 표시됨",
    "ftbultimine.change_shape.next": "다음 모양으로 전환",
    "ftbultimine.change_shape.prev": "이전 모양으로 전환",
    "ftbultimine.client_settings.general.require_ultimine_key_for_cycling.tooltip": (
        "켜면 키보드(기본값: 위/아래 방향키)로 모양을 바꿀 때 Ultimine 키"
        "(기본값: `)를 누르고 있어야 합니다.\n끄면 언제든 모양을 바꿀 수 있습니다."
    ),
    "ftbultimine.client_settings.general.shape_feedback_hotbar_message.tooltip": (
        "켜면 Ultimine 채굴 모양이 바뀔 때 핫바에 새 모양을 안내하는 메시지를 "
        "표시합니다."
    ),
    "ftbultimine.client_settings.rendering.preview_line_alpha": "윤곽선 불투명도",
    "ftbultimine.client_settings.rendering.preview_line_alpha.tooltip": (
        "블록 '안쪽'에 그리는 미리보기 선의 불투명도입니다."
    ),
    "ftbultimine.client_settings.overlay.shape_menu_context_lines": (
        "모양 메뉴 주변 항목 수"
    ),
    "ftbultimine.client_settings.overlay.overlay_inset_x": (
        "오버레이 패널 X축 안쪽 여백"
    ),
    "ftbultimine.client_settings.overlay.overlay_inset_x.tooltip": (
        "안쪽 여백은 화면 중앙 방향으로 적용됩니다.\nX축 위치가 가운데면 무시됩니다."
    ),
    "ftbultimine.client_settings.overlay.overlay_inset_y": (
        "오버레이 패널 Y축 안쪽 여백"
    ),
    "ftbultimine.client_settings.overlay.overlay_inset_y.tooltip": (
        "안쪽 여백은 화면 중앙 방향으로 적용됩니다.\nY축 위치가 가운데면 무시됩니다."
    ),
    "ftbultimine.client_settings.overlay.overlay_scale": "오버레이 배율",
    "ftbultimine.client_settings.overlay.overlay_scale.tooltip": (
        "글꼴이 가장 깔끔하게 보이도록 0.25 단위의 배율을 권장합니다."
    ),
    "ftbultimine.server_settings.features.right_click_axe": (
        "도끼 우클릭을 여러 블록에 적용"
    ),
    "ftbultimine.server_settings.features.right_click_hoe": (
        "괭이 우클릭을 여러 블록에 적용"
    ),
    "ftbultimine.server_settings.features.right_click_shovel": (
        "삽 우클릭을 여러 블록에 적용"
    ),
    "ftbultimine.server_settings.features.single_crop_harvesting.tooltip": (
        "켜면 Ultimine 키를 누르지 않은 상태에서도 작물 블록을 우클릭해 수확할 수 "
        "있습니다."
    ),
    "ftbultimine.server_settings.costs_limits.max_blocks.tooltip": (
        "한 번에 파괴하거나 변경할 수 있는 최대 블록 수입니다.\nFTB Ranks가 설치되어 "
        "있고 'ftbultimine.max_blocks' 노드가 있으면 그 값이 우선합니다."
    ),
    "ftbultimine.server_settings.costs_limits.exhaustion_per_block": (
        "채굴 블록당 허기 소모 배수"
    ),
    "ftbultimine.server_settings.costs_limits.exhaustion_per_block.tooltip": (
        "소수 값을 사용할 수 있습니다.\nFTB Ranks가 설치되어 있고 "
        "'ftbultimine.exhaustion_per_block' 노드가 있으면 그 값이 우선합니다."
    ),
    "ftbultimine.server_settings.costs_limits.require_tool": (
        "Ultimine 사용 시 도구 필요"
    ),
    "ftbultimine.server_settings.costs_limits.require_tool.tooltip": (
        "켜면 플레이어가 내구도가 있는 도구나 'ftbultimine:tools' 아이템 태그에 속한 "
        "아이템을 들어야 합니다.\n'Ultimine 사용 시 유효한 도구 필요'도 참고하세요."
    ),
    "ftbultimine.server_settings.costs_limits.require_valid_tool_for_block": (
        "Ultimine 사용 시 유효한 도구 필요"
    ),
    "ftbultimine.server_settings.costs_limits.require_valid_tool_for_block.tooltip": (
        "켜면 손에 든 도구가 Ultimine 대상 블록을 정상적으로 캘 수 있어야 합니다.\n"
        "즉, 해당 블록의 드롭 아이템을 얻을 수 있는 도구여야 합니다.\n"
        "'Ultimine 사용 시 도구 필요'도 참고하세요."
    ),
    "ftbultimine.server_settings.misc.merge_tags": "태그 병합(모양 없음)",
    "ftbultimine.server_settings.misc.merge_tags.tooltip": (
        "모양 없는 채굴 모드에서는 이 목록의 태그에 속하면서 처음 캔 블록과 블록 "
        "태그를 공유하는 블록도 Ultimine 대상으로 봅니다."
    ),
    "ftbultimine.server_settings.misc.merge_tags_shaped": "태그 병합(모양 있음)",
    "ftbultimine.server_settings.misc.merge_tags_shaped.tooltip": (
        "모양 있는 채굴 모드에서는 이 목록의 태그에 속하면서 처음 캔 블록과 블록 "
        "태그를 공유하는 블록도 Ultimine 대상으로 봅니다.\n기본값 '*'는 모든 블록을 "
        "후보로 인정합니다."
    ),
    "ftbultimine.server_settings.misc.cancel_on_block_break_fail.tooltip": (
        "고급 설정: 파괴 불가능한 블록이 발견되면 해당 블록을 건너뛰는 대신 채굴을 "
        "중단합니다."
    ),
    "ftbultimine.modifier.cooldown": "FTB Ultimine 재사용 대기시간(틱)",
}
EXPECTED_UNTRANSLATED = {
    "item.ftbultimine.ultiminer",
    "key.categories.ftbultimine",
    "key.ftbultimine",
}
QUEST_KEY = "quest.77B6A7151B3E5980.quest_desc"
EXPECTED_QUEST_VALUE = [
    r"&a광맥 채굴&r은 기능이 제한된 FTB Ultimine입니다.\n\n광석이나 원목을 캐면 "
    r"서로 붙어 있는 같은 종류의 블록도 함께 부서집니다.\n\n시간을 많이 아낄 수 "
    r"있지만... 이미 FTB Ultimine이 있긴 하죠."
]
ANNOUNCEMENT_ENGLISH = (
    'addAnnouncement("4.6", "Removed mods: Harvest with ease, FTB Ultimine does '
    'that now")'
)
ANNOUNCEMENT_KOREAN = (
    'addAnnouncement("4.6", "제거된 모드: Harvest with ease, 이제 FTB Ultimine이 '
    '같은 기능을 제공합니다")'
)
EXPECTED_CONFIG_REFERENCES = {
    "config/crash_assistant/modlist.json",
    "config/ftblibrary-client.snbt",
    "config/ftbultimine-client.snbt",
    "config/ftbultimine-server.snbt",
}
GLOSSARY_ROW = "| FTB Ultimine | FTB Ultimine | 공식 모드명 |"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"(?<![A-Za-z_])\d+(?:\.\d+)?")
OTHER_ENGLISH_LANGUAGE = re.compile(r"assets/[^/]+/lang/en_us\.json")
DIRECT_REFERENCE = re.compile(r"(?i)ftb.?ultimine|ultimine")
RELATED_EXTENSIONS = {".ini", ".js", ".json", ".snbt", ".toml", ".txt"}
FORBIDDEN_TRANSLATIONS = re.compile(
    r"컨텍스트 선|윤곽선 투명도|우클릭으로 여러 블록 파괴|"
    r"태그 병합\(형태|형태 없는 채굴|블록당 허기 소모량|재사용 대기 시간"
)


def load_json_bytes(raw: bytes, source: str) -> dict[str, object]:
    """중복 키가 없는 UTF-8 JSON 객체만 허용한다."""
    duplicates: list[str] = []

    def object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result = {}
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        return result

    try:
        value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=object_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"JSON 읽기 실패: {source}: {exc}") from exc
    if duplicates:
        raise RuntimeError(f"JSON 중복 키: {source}: {sorted(set(duplicates))}")
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {source}")
    return value


def load_json_path(path: Path) -> dict[str, object]:
    return load_json_bytes(path.read_bytes(), str(path))


def validate_language(
    english: dict[str, object], korean: dict[str, object]
) -> list[str]:
    """키, 순서, 자료형과 보호 문자열을 검증한다."""
    errors = []
    if list(english) != list(korean):
        errors.append(
            "키 또는 순서 불일치: "
            f"누락={sorted(set(english) - set(korean))}, "
            f"초과={sorted(set(korean) - set(english))}"
        )
    for key in english.keys() & korean.keys():
        source = english[key]
        translated = korean[key]
        if not isinstance(source, str) or not isinstance(translated, str):
            errors.append(f"문자열 자료형이 아닌 언어 값: {key}")
            continue
        if PLACEHOLDER.findall(source) != PLACEHOLDER.findall(translated):
            errors.append(f"자리표시자 불일치: {key}")
        if Counter(FORMAT_CODE.findall(source)) != Counter(
            FORMAT_CODE.findall(translated)
        ):
            errors.append(f"서식 코드 불일치: {key}")
        if source.count("\n") != translated.count("\n"):
            errors.append(f"줄바꿈 수 불일치: {key}")
    return errors


def parse_config_fields(path: Path) -> dict[str, set[str]]:
    """FTB 설정 SNBT에서 섹션별 옵션 키를 읽는다."""
    sections: dict[str, set[str]] = {}
    current = None
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line in {"{", "}", "]"}:
            continue
        section = re.fullmatch(r"([a-z_]+): \{", line)
        if section:
            current = section.group(1)
            sections[current] = set()
            continue
        option = re.match(r"([a-z_]+):", line)
        if option and current is not None:
            sections[current].add(option.group(1))
    return sections


def related_files(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.suffix.lower() in RELATED_EXTENSIONS
    ]


def verify_other_language_owners(
    instance: Path, source_jar: Path, english: dict[str, object], errors: list[str]
) -> tuple[int, int]:
    """다른 JAR의 영어 언어 파일에 같은 소유 키가 있는지 확인한다."""
    language_files = 0
    conflicts = []
    unreadable = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        try:
            with ZipFile(jar_path) as archive:
                for name in archive.namelist():
                    if not OTHER_ENGLISH_LANGUAGE.fullmatch(name):
                        continue
                    language_files += 1
                    try:
                        values = json.loads(archive.read(name).decode("utf-8-sig"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                        unreadable.append(f"{jar_path.name}:{name}:{exc}")
                        continue
                    if not isinstance(values, dict) or jar_path == source_jar:
                        continue
                    shared = sorted(set(values) & set(english))
                    if shared:
                        conflicts.append(f"{jar_path.name}:{name}:{shared}")
        except (BadZipFile, KeyError, OSError) as exc:
            unreadable.append(f"{jar_path.name}:{exc}")
    if unreadable:
        errors.append("설치 JAR 언어 파일 읽기 오류: " + " | ".join(unreadable[:10]))
    if conflicts:
        errors.append("다른 모드의 FTB Ultimine 키 소유 충돌: " + " | ".join(conflicts))
    if language_files != 388:
        errors.append(f"설치 영어 언어 파일 수 변경: {language_files}")
    return language_files, len(conflicts)


def verify(instance: Path, pre_apply: bool = False) -> dict[str, object]:
    """현재 설치 영어 원문과 프로젝트 산출물을 전수 검증한다."""
    errors: list[str] = []
    matches = sorted((instance / "mods").glob("ftb-ultimine-neoforge-*.jar"))
    if [path.name for path in matches] != [EXPECTED_JAR]:
        raise RuntimeError(
            f"FTB Ultimine JAR 범위 변경: {[path.name for path in matches]}"
        )
    source_jar = matches[0]
    source_sha256 = hashlib.sha256(source_jar.read_bytes()).hexdigest()
    if source_sha256 != EXPECTED_JAR_SHA256:
        errors.append(f"FTB Ultimine JAR SHA-256 변경: {source_sha256}")

    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        english = load_json_bytes(
            archive.read("assets/ftbultimine/lang/en_us.json"),
            "FTB Ultimine en_us",
        )
        bundled = load_json_bytes(
            archive.read("assets/ftbultimine/lang/ko_kr.json"),
            "FTB Ultimine ko_kr",
        )
        class_files = {
            name: archive.read(name) for name in names if name.endswith(".class")
        }
        language_files = [
            name
            for name in names
            if re.fullmatch(r"assets/ftbultimine/lang/[a-z_]+\.json", name)
        ]
        json_files = [name for name in names if name.endswith(".json")]
        advancement_files = [name for name in json_files if "/advancement" in name]
        recipe_files = [name for name in json_files if "/recipe/" in name]
        guide_files = [
            name
            for name in names
            if any(
                marker in name.lower()
                for marker in ("patchouli", "guideme", "modonomicon")
            )
        ]

    if (len(names), len(class_files), len(language_files)) != (173, 96, 10):
        errors.append(
            "FTB Ultimine JAR 구성 변경: "
            f"항목={len(names)}, 클래스={len(class_files)}, 언어={len(language_files)}"
        )
    if len(english) != 89 or len(bundled) != 17:
        errors.append(
            f"FTB Ultimine 언어 키 수 변경: 영어={len(english)}, 내장 한국어={len(bundled)}"
        )
    if advancement_files or recipe_files or guide_files:
        errors.append(
            "FTB Ultimine 추가 표시 데이터 발견: "
            f"발전={advancement_files}, 제작법={recipe_files}, 가이드={guide_files}"
        )
    class_referenced = {
        key
        for key in english
        if any(key.encode() in raw for raw in class_files.values())
    }
    if class_referenced != EXPECTED_CLASS_REFERENCE_KEYS:
        errors.append(
            "FTB Ultimine 클래스 언어 키 참조 범위 변경: "
            f"누락={sorted(EXPECTED_CLASS_REFERENCE_KEYS - class_referenced)}, "
            f"초과={sorted(class_referenced - EXPECTED_CLASS_REFERENCE_KEYS)}"
        )
    semantic_markers = {
        "dev/ftb/mods/ftbultimine/config/FTBUltimineClientConfig.class": (
            b"Alpha value (0-255)",
            b"number of shape names to display",
        ),
        "dev/ftb/mods/ftbultimine/config/FTBUltimineServerConfig.class": (
            b"Hunger multiplier for each block ultimined",
            b"strip multiple logs and scrape/unwax copper blocks",
            b"till multiple grass/dirt blocks into farmland",
            b"flatten multiple grass/dirt blocks into dirt paths",
        ),
    }
    for class_name, markers in semantic_markers.items():
        raw = class_files.get(class_name, b"")
        for marker in markers:
            if marker not in raw:
                errors.append(
                    f"설정 의미 근거 바이트코드 변경: {class_name}:{marker!r}"
                )

    working = load_json_path(WORKING)
    output = load_json_path(OUTPUT)
    overrides = load_json_path(OVERRIDES)
    errors.extend(validate_language(english, working))
    errors.extend(validate_language(english, output))
    if working != output:
        errors.append("FTB Ultimine working과 output 언어 파일이 다릅니다")
    if overrides != EXPECTED_OVERRIDES:
        errors.append("FTB Ultimine 재검수 교정 목록이 확정값과 다릅니다")
    mismatches = sorted(
        key for key, value in EXPECTED_OVERRIDES.items() if output.get(key) != value
    )
    if mismatches:
        errors.append(f"FTB Ultimine 확정 교정값 불일치: {mismatches}")
    untranslated = {key for key in english if output.get(key) == english.get(key)}
    if untranslated != EXPECTED_UNTRANSLATED:
        errors.append(f"FTB Ultimine 영어 원문 유지 범위 변경: {sorted(untranslated)}")
    forbidden = sorted(
        key
        for key, value in output.items()
        if isinstance(value, str) and FORBIDDEN_TRANSLATIONS.search(value)
    )
    if forbidden:
        errors.append(f"FTB Ultimine 의미 오류·금지 용어 잔존: {forbidden}")
    if OUTPUT.read_bytes().startswith(b"\xef\xbb\xbf"):
        errors.append("FTB Ultimine 산출물에 UTF-8 BOM이 있습니다")

    client_path = instance / "config/ftbultimine-client.snbt"
    server_path = instance / "config/ftbultimine-server.snbt"
    if (
        hashlib.sha256(client_path.read_bytes()).hexdigest()
        != EXPECTED_CLIENT_CONFIG_SHA256
    ):
        errors.append("FTB Ultimine 클라이언트 설정 파일이 바뀌었습니다")
    if (
        hashlib.sha256(server_path.read_bytes()).hexdigest()
        != EXPECTED_SERVER_CONFIG_SHA256
    ):
        errors.append("FTB Ultimine 서버 설정 파일이 바뀌었습니다")
    client_fields = parse_config_fields(client_path)
    server_fields = parse_config_fields(server_path)
    if client_fields != EXPECTED_CLIENT_FIELDS:
        errors.append(f"FTB Ultimine 클라이언트 설정 범위 변경: {client_fields}")
    if server_fields != EXPECTED_SERVER_FIELDS:
        errors.append(f"FTB Ultimine 서버 설정 범위 변경: {server_fields}")
    required_config_keys = {
        "ftbultimine.client_settings",
        "ftbultimine.server_settings",
        *(
            f"ftbultimine.client_settings.{section}"
            for section in EXPECTED_CLIENT_FIELDS
        ),
        *(
            f"ftbultimine.client_settings.{section}.{option}"
            for section, options in EXPECTED_CLIENT_FIELDS.items()
            for option in options
        ),
        *(
            f"ftbultimine.server_settings.{section}"
            for section in EXPECTED_SERVER_FIELDS
        ),
        *(
            f"ftbultimine.server_settings.{section}.{option}"
            for section, options in EXPECTED_SERVER_FIELDS.items()
            for option in options
        ),
    }
    if not required_config_keys <= set(english):
        errors.append(
            f"FTB Ultimine 설정 표시 키 누락: {sorted(required_config_keys - set(english))}"
        )

    source_quests = parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    related_quest_keys = sorted(
        key for key, value in source_quests.items() if "FTB Ultimine" in flatten(value)
    )
    if related_quest_keys != [QUEST_KEY]:
        errors.append(f"FTB Ultimine 관련 퀘스트 범위 변경: {related_quest_keys}")
    quest_output = parse_language_snbt(QUEST_OUTPUT)
    quest_common = load_json_path(QUEST_COMMON)
    quest_owner = load_json_path(QUEST_OWNER)
    for label, values in (
        ("output", quest_output),
        ("공통 작업본", quest_common),
        ("Mekanism 작업본", quest_owner),
    ):
        if values.get(QUEST_KEY) != EXPECTED_QUEST_VALUE:
            errors.append(f"FTB Ultimine 관련 퀘스트 {label} 값 불일치")
    source_quest = flatten(source_quests[QUEST_KEY])
    translated_quest = flatten(EXPECTED_QUEST_VALUE)
    if Counter(FORMAT_CODE.findall(source_quest)) != Counter(
        FORMAT_CODE.findall(translated_quest)
    ):
        errors.append("FTB Ultimine 관련 퀘스트 서식 코드 불일치")
    if NUMBER.findall(source_quest) != NUMBER.findall(translated_quest):
        errors.append("FTB Ultimine 관련 퀘스트 숫자 불일치")

    kube_files = related_files(instance / "kubejs")
    kube_references = [
        path.relative_to(instance).as_posix()
        for path in kube_files
        if DIRECT_REFERENCE.search(path.read_text(encoding="utf-8-sig"))
    ]
    expected_kube = ["kubejs/server_scripts/announcements/announcements.js"]
    if kube_references != expected_kube:
        errors.append(f"FTB Ultimine KubeJS 참조 범위 변경: {kube_references}")
    announcement_source = instance / expected_kube[0]
    source_text = announcement_source.read_text(encoding="utf-8-sig")
    output_text = ANNOUNCEMENT_OUTPUT.read_text(encoding="utf-8")
    if ANNOUNCEMENT_KOREAN not in output_text or ANNOUNCEMENT_ENGLISH in output_text:
        errors.append("FTB Ultimine KubeJS 공지 산출물 불일치")
    if (
        ANNOUNCEMENT_ENGLISH not in source_text
        and ANNOUNCEMENT_KOREAN not in source_text
    ):
        errors.append("FTB Ultimine 실제 KubeJS 공지 상태를 식별할 수 없습니다")

    config_files = [
        path
        for path in related_files(instance / "config")
        if "config/ftbquests/" not in path.relative_to(instance).as_posix()
    ]
    config_references = {
        path.relative_to(instance).as_posix()
        for path in config_files
        if DIRECT_REFERENCE.search(path.read_text(encoding="utf-8-sig"))
    }
    if config_references != EXPECTED_CONFIG_REFERENCES:
        errors.append(
            f"FTB Ultimine 설정·메타데이터 참조 범위 변경: {config_references}"
        )
    attribute_configs = sorted(
        (instance / "config/attributefix/ftbultimine").glob("*.json")
    )
    if len(attribute_configs) != 4:
        errors.append(f"FTB Ultimine 속성 설정 범위 변경: {attribute_configs}")
    for path in attribute_configs:
        load_json_path(path)

    installed_languages, owner_conflicts = verify_other_language_owners(
        instance, source_jar, english, errors
    )
    project_language_files = sorted(
        (PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets").glob(
            "*/lang/ko_kr.json"
        )
    )
    ultiminer_rows = []
    for path in project_language_files:
        values = load_json_path(path)
        for key, value in values.items():
            if key.startswith(("item.", "block.")) and value == "Ultiminer":
                ultiminer_rows.append(f"{path.parent.parent.name}:{key}")
    if len(project_language_files) != 285:
        errors.append(f"프로젝트 언어 파일 수 변경: {len(project_language_files)}")
    if ultiminer_rows != ["ftbultimine:item.ftbultimine.ultiminer"]:
        errors.append(f"Ultiminer 아이템 이름 충돌: {ultiminer_rows}")
    if GLOSSARY_ROW not in GLOSSARY.read_text(encoding="utf-8"):
        errors.append("FTB Ultimine 용어집 행 누락")

    output_sha256 = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    quest_sha256 = hashlib.sha256(QUEST_OUTPUT.read_bytes()).hexdigest()
    announcement_sha256 = hashlib.sha256(ANNOUNCEMENT_OUTPUT.read_bytes()).hexdigest()
    if not pre_apply:
        report = load_json_path(REPORT)
        language_review = report.get("language_review")
        if report.get("validation") != "passed":
            errors.append("FTB Ultimine 재검수 보고서 상태가 passed가 아닙니다")
        if (
            not isinstance(language_review, dict)
            or language_review.get("project_candidates_retained") != 54
            or language_review.get("project_candidates_corrected") != 35
        ):
            errors.append("FTB Ultimine 재검수 보고서 번역 집계 불일치")
        application = report.get("application")
        if (
            not isinstance(application, dict)
            or application.get("status") != "applied_and_verified"
        ):
            errors.append("FTB Ultimine 재검수 보고서 적용 상태 불일치")
        target_pairs = {
            OUTPUT: instance
            / "resourcepacks/ATM10_Korean/assets/ftbultimine/lang/ko_kr.json",
            ANNOUNCEMENT_OUTPUT: announcement_source,
        }
        for source, target in target_pairs.items():
            if (
                hashlib.sha256(source.read_bytes()).digest()
                != hashlib.sha256(target.read_bytes()).digest()
            ):
                errors.append(f"FTB Ultimine 적용 파일 해시 불일치: {target}")
        if (
            not isinstance(application, dict)
            or application.get("language_sha256") != output_sha256
            or application.get("quest_sha256") != quest_sha256
            or application.get("announcement_sha256") != announcement_sha256
            or application.get("quest_target_status") != "deferred_aggregate_scope"
            or application.get("unexpected_changes") != 0
        ):
            errors.append("FTB Ultimine 재검수 보고서 적용 해시 불일치")

    if errors:
        raise RuntimeError("FTB Ultimine 재검수 검증 실패:\n" + "\n".join(errors[:50]))
    bundled_reused = sum(output.get(key) == value for key, value in bundled.items())
    return {
        "scope": "FTB Ultimine 전체 번역 재검수",
        "source_jar": source_jar.name,
        "source_jar_sha256": source_sha256,
        "source_jar_bytes": source_jar.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(class_files),
        "source_keys_reviewed": len(english),
        "bundled_korean_candidates_reviewed": len(bundled),
        "bundled_korean_candidates_reused": bundled_reused,
        "project_candidates_retained": len(english) - len(EXPECTED_OVERRIDES),
        "project_candidates_corrected": len(EXPECTED_OVERRIDES),
        "effective_output_keys": len(output),
        "class_referenced_language_keys": len(class_referenced),
        "client_config_options_reviewed": sum(map(len, client_fields.values())),
        "server_config_options_reviewed": sum(map(len, server_fields.values())),
        "ftbquests_files_reviewed": len(
            list((instance / "config/ftbquests/quests").rglob("*.snbt"))
        ),
        "ftbquests_related_keys": len(related_quest_keys),
        "kubejs_files_reviewed": len(kube_files),
        "kubejs_reference_files": len(kube_references),
        "configuration_reference_files": len(config_references),
        "attribute_config_files_reviewed": len(attribute_configs),
        "installed_english_language_files_reviewed": installed_languages,
        "other_language_owner_conflicts": owner_conflicts,
        "project_language_files_reviewed": len(project_language_files),
        "harmful_item_name_collisions": 0,
        "output_sha256": output_sha256,
        "quest_output_sha256": quest_sha256,
        "announcement_output_sha256": announcement_sha256,
        "validation": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--pre-apply", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    print(
        json.dumps(
            verify(instance, pre_apply=args.pre_apply),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
