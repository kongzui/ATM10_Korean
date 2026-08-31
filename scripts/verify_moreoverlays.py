#!/usr/bin/env python3
"""More Overlays Updated의 전체 번역과 실제 설정 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

WORKING = PROJECT_ROOT / "working/common_ui/curios_effects/moreoverlays/ko_kr.json"
OVERRIDES = (
    PROJECT_ROOT
    / "working/common_ui/curios_effects/moreoverlays/recheck_overrides.json"
)
OUTPUT = (
    active_output_root()
    / "resourcepack/ATM10_Korean/assets/moreoverlays/lang/ko_kr.json"
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
DIRECT_REFERENCE = re.compile(
    r"(?i)\bmoreoverlays\b|\bmore overlays(?: updated)?\b|"
    r"key\.moreoverlays|config\.moreoverlays"
)
EXPECTED_CORRECTIONS = 16
BENIGN_PROJECT_COLLISION_VALUES = {
    "렌더링 설정",
    "설정 초기화",
    "아이템 검색",
    "저장",
}
CONFIG_COMMENT_MARKERS = (
    b"Settings for the light / mobspawn overlay",
    b"Render light levels as numbers instead of crosses",
    b"Ignore if there in no 2 Block space to spawn.",
    b"Ignore if mobs can actually spawn according to other mods and biome spawn lists",
    b"Blocks can allow/disallow spawns for different entity types.",
    b"Minimum save light level where no mobs can spawn",
    b"Color for the middle chunk line",
    b'Color for the number that marks "No spawns possible"',
    b"Also searches for the custom name of an item in user inventory",
    b"Color of the filtered out slots",
    b"Transparancy for the filtered out slots",
)
GLOSSARY_ROWS = (
    "| More Overlays Updated | More Overlays Updated | 공식 모드명 |",
    "| Overlay | 오버레이 | 공통 UI 용어 |",
    "| Light Level | 밝기 레벨 | Minecraft 밝기 용어 |",
    "| Light Overlay | 몹 생성 밝기 오버레이 | 기능명 |",
    "| Search Box / Search Bar | 검색창 | 공통 UI 용어 |",
)
HARDCODED_DISPLAY_MARKERS = {
    "at/ridgo8/moreoverlays/chunkbounds/ChunkBoundsHandler.class": (
        b"displayClientMessage",
        b"Chunk Border Overlay: ",
    ),
    "at/ridgo8/moreoverlays/chunkbounds/ChunkBoundsHandler$RenderMode.class": (
        b"NONE",
        b"CORNERS",
        b"GRID",
        b"REGIONS",
    ),
    "at/ridgo8/moreoverlays/lightoverlay/LightOverlayHandler.class": (
        b"displayClientMessage",
        b"Light Overlay Enabled",
        b"Light Overlay Disabled",
    ),
    "at/ridgo8/moreoverlays/gui/config/OptionBoolean.class": (
        b"setMessage",
        b"TRUE",
        b"FALSE",
    ),
}


def load_json_bytes(raw: bytes, source: str) -> dict[str, object]:
    """중복 키가 없는 UTF-8 JSON 객체만 허용한다."""
    duplicate_keys: list[str] = []

    def object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result = {}
        for key, value in pairs:
            if key in result:
                duplicate_keys.append(key)
            result[key] = value
        return result

    try:
        value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=object_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"JSON 읽기 실패: {source}: {exc}") from exc
    if duplicate_keys:
        raise RuntimeError(f"JSON 중복 키: {source}: {sorted(set(duplicate_keys))}")
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


def parse_config_paths(path: Path) -> dict[str, set[str]]:
    """현재 TOML의 최상위 섹션과 설정 키를 읽는다."""
    sections: dict[str, set[str]] = {}
    current = None
    for number, raw_line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        section = re.fullmatch(r"\[([A-Za-z0-9_]+)\]", line)
        if section:
            current = section.group(1)
            if current in sections:
                raise RuntimeError(f"TOML 중복 섹션: {current}")
            sections[current] = set()
            continue
        setting = re.match(r"([A-Za-z0-9_]+)\s*=", line)
        if setting and current is not None:
            key = setting.group(1)
            if key in sections[current]:
                raise RuntimeError(f"TOML 중복 설정: {current}.{key}")
            sections[current].add(key)
            continue
        raise RuntimeError(f"TOML 구조를 읽을 수 없습니다: {path}:{number}: {line}")
    return sections


def related_files(root: Path) -> list[Path]:
    """FTB Quests와 KubeJS에서 검토할 표시 가능 파일을 찾는다."""
    allowed = {".js", ".json", ".snbt", ".txt", ".toml"}
    return [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.suffix.lower() in allowed
    ]


def verify(instance: Path) -> dict[str, object]:
    errors = []
    matches = sorted((instance / "mods").glob("moreoverlays-*.jar"))
    if len(matches) != 1:
        raise RuntimeError(f"More Overlays Updated JAR 수 불일치: {len(matches)}")
    source_jar = matches[0]
    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        english = load_json_bytes(
            archive.read("assets/moreoverlays/lang/en_us.json"),
            "moreoverlays:en_us",
        )
        bundled_korean_entries = [
            name for name in names if name.endswith("/lang/ko_kr.json")
        ]
        language_files = [
            name
            for name in names
            if re.fullmatch(r"assets/moreoverlays/lang/[a-z_]+\.json", name)
        ]
        class_files = [name for name in names if name.endswith(".class")]
        class_bytes = {name: archive.read(name) for name in class_files}
        direct_translation_classes = [
            name
            for name, raw in class_bytes.items()
            if any(
                marker in raw
                for marker in (
                    b"key.moreoverlays.",
                    b"gui.config.moreoverlays.",
                    b"config.moreoverlays.",
                )
            )
        ]
        config_class = class_bytes.get(
            "at/ridgo8/moreoverlays/config/Config.class", b""
        )
        missing_markers = [
            marker.decode("ascii")
            for marker in CONFIG_COMMENT_MARKERS
            if marker not in config_class
        ]
        if missing_markers:
            errors.append(f"설정 기능 근거 문자열 변경: {missing_markers}")
        expected_class_links = {
            "at/ridgo8/moreoverlays/KeyBindings.class": (
                b"key.moreoverlays.chunkbounds.desc",
                b"key.moreoverlays.lightoverlay.desc",
            ),
            "at/ridgo8/moreoverlays/lightoverlay/LightScannerVanilla.class": (
                b"light_IgnoreLayer",
                b"light_SaveLevel",
                b"light_SimpleEntityCheck",
            ),
            "at/ridgo8/moreoverlays/itemsearch/GuiRenderer.class": (
                b"search_filteredSlotColor",
                b"search_filteredSlotTransparancy",
                b"search_maxResults",
            ),
            "at/ridgo8/moreoverlays/itemsearch/JeiModule.class": (
                b"IIngredientListOverlay",
                b"getJEITextField",
            ),
            "at/ridgo8/moreoverlays/gui/config/OptionValueEntry.class": (
                b"getComment",
                b"nullToEmpty",
                b"renderComponentTooltip",
            ),
            "at/ridgo8/moreoverlays/gui/config/OptionCategory.class": (
                b"tooltip",
                b"nullToEmpty",
                b"renderTooltip",
            ),
            "at/ridgo8/moreoverlays/gui/config/ConfigOptionList.class": (
                b"getComment",
                b"OptionCategory",
                b"I18n",
            ),
        }
        for name, markers in expected_class_links.items():
            raw = class_bytes.get(name, b"")
            missing = [
                marker.decode("ascii") for marker in markers if marker not in raw
            ]
            if missing:
                errors.append(f"클래스 표시 경로 변경: {name}: {missing}")
        missing_hardcoded_markers = [
            f"{name}:{marker.decode('ascii')}"
            for name, markers in HARDCODED_DISPLAY_MARKERS.items()
            for marker in markers
            if marker not in class_bytes.get(name, b"")
        ]
        if missing_hardcoded_markers:
            errors.append(
                "클래스 직접 표시 문자열 범위 변경: " f"{missing_hardcoded_markers}"
            )
        advancement_files = [
            name for name in names if name.endswith(".json") and "/advancement" in name
        ]
        recipe_files = [
            name for name in names if name.endswith(".json") and "/recipe" in name
        ]
        guide_files = [
            name
            for name in names
            if any(
                marker in name.lower() for marker in ("patchouli", "guideme", "book")
            )
        ]

    working = load_json_path(WORKING)
    output = load_json_path(OUTPUT)
    overrides = load_json_path(OVERRIDES)
    errors.extend(validate_language(english, working))
    if output != working:
        errors.append("More Overlays Updated 작업본과 산출물이 다릅니다")
    if len(english) != 40 or len(overrides) != EXPECTED_CORRECTIONS:
        errors.append(
            f"원문·교정 키 수 변경: 원문={len(english)}, 교정={len(overrides)}"
        )
    if bundled_korean_entries:
        errors.append(f"예상하지 않은 번들 한국어 발견: {bundled_korean_entries}")
    override_mismatches = sorted(
        key for key, expected in overrides.items() if working.get(key) != expected
    )
    if override_mismatches:
        errors.append(f"확정 재검수 교정값 불일치: {override_mismatches}")
    untranslated = {key for key in english if working.get(key) == english.get(key)}
    if untranslated != {"key.moreoverlays.category"}:
        errors.append(f"영어 원문 유지 범위 변경: {sorted(untranslated)}")
    duplicate_values = {
        value for value, count in Counter(working.values()).items() if count > 1
    }
    if duplicate_values:
        errors.append(f"모드 내부 한국어 이름 충돌: {sorted(duplicate_values)}")
    glossary = (PROJECT_ROOT / "glossary/README.md").read_text(encoding="utf-8")
    missing_glossary_rows = [row for row in GLOSSARY_ROWS if row not in glossary]
    if missing_glossary_rows:
        errors.append(f"More Overlays Updated 확정 용어 누락: {missing_glossary_rows}")

    config_path = instance / "config/moreoverlays.toml"
    config_sections = parse_config_paths(config_path)
    config_option_keys = {
        f"config.moreoverlays.{section}.{key.lower()}"
        for section, keys in config_sections.items()
        for key in keys
    }
    language_option_keys = {
        key
        for key in english
        if key.startswith("config.moreoverlays.")
        and not key.startswith("config.moreoverlays.category.")
    }
    if config_option_keys != language_option_keys:
        errors.append(
            "실제 설정과 번역 키 불일치: "
            f"누락={sorted(config_option_keys - language_option_keys)}, "
            f"초과={sorted(language_option_keys - config_option_keys)}"
        )
    language_categories = {
        key.removeprefix("config.moreoverlays.category.")
        for key in english
        if key.startswith("config.moreoverlays.category.")
    }
    legacy_categories = language_categories - set(config_sections)
    if legacy_categories != {"itemsearch"}:
        errors.append(f"레거시 설정 범주 변경: {sorted(legacy_categories)}")
    if set(config_sections) - language_categories:
        errors.append(
            f"설정 범주 번역 누락: {sorted(set(config_sections) - language_categories)}"
        )
    hardcoded_comment_tooltips = len(config_sections) + len(config_option_keys)
    if hardcoded_comment_tooltips != 32:
        errors.append(f"직접 표시 설정 설명 수 변경: {hardcoded_comment_tooltips}")

    owner_key_files = []
    jar_scan_errors = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        if jar_path == source_jar:
            continue
        try:
            with ZipFile(jar_path) as archive:
                for name in archive.namelist():
                    if not re.fullmatch(
                        r"assets/[^/]+/lang/(?:en_us|ko_kr)\.json", name
                    ):
                        continue
                    raw = archive.read(name)
                    if b"moreoverlays" not in raw:
                        continue
                    try:
                        values = load_json_bytes(raw, f"{jar_path.name}:{name}")
                    except (RuntimeError, TypeError) as exc:
                        jar_scan_errors.append(str(exc))
                        continue
                    collisions = sorted(set(values) & set(english))
                    if collisions:
                        owner_key_files.append(
                            f"{jar_path.name}:{name}:{','.join(collisions)}"
                        )
        except BadZipFile as exc:
            jar_scan_errors.append(f"JAR 읽기 실패: {jar_path}: {exc}")
    if jar_scan_errors:
        errors.append(
            "다른 모드 언어 파일 읽기 오류: " + " | ".join(jar_scan_errors[:10])
        )
    if owner_key_files:
        errors.append(f"다른 모드 소유 키 충돌: {owner_key_files}")

    project_language_files = 0
    project_collision_rows = []
    project_key_conflicts = []
    assets_root = active_output_root() / "resourcepack/ATM10_Korean/assets"
    for path in sorted(assets_root.glob("*/lang/ko_kr.json")):
        project_language_files += 1
        if path == OUTPUT:
            continue
        try:
            values = load_json_path(path)
        except (RuntimeError, TypeError) as exc:
            errors.append(str(exc))
            continue
        for key in set(working) & set(values):
            project_key_conflicts.append(f"{path}:{key}")
        for key, value in values.items():
            if isinstance(value, str) and value in set(working.values()):
                project_collision_rows.append((str(value), path.as_posix(), key))
    if project_key_conflicts:
        errors.append(f"프로젝트 언어 키 소유 충돌: {project_key_conflicts}")
    project_collision_values = {value for value, _, _ in project_collision_rows}
    harmful_collision_values = (
        project_collision_values - BENIGN_PROJECT_COLLISION_VALUES
    )
    if harmful_collision_values:
        errors.append(
            f"다른 모드와 유해한 한국어 이름 충돌: {sorted(harmful_collision_values)}"
        )

    quest_files = sorted((instance / "config/ftbquests/quests").rglob("*.snbt"))
    quest_references = []
    for path in quest_files:
        text = path.read_text(encoding="utf-8-sig")
        if DIRECT_REFERENCE.search(text):
            quest_references.append(path.relative_to(instance).as_posix())
    if quest_references:
        errors.append(f"예상하지 않은 FTB Quests 직접 참조: {quest_references}")

    kubejs_files = related_files(instance / "kubejs")
    kubejs_references = []
    for path in kubejs_files:
        text = path.read_text(encoding="utf-8-sig")
        if DIRECT_REFERENCE.search(text):
            kubejs_references.append(path.relative_to(instance).as_posix())
    if kubejs_references:
        errors.append(f"예상하지 않은 KubeJS 직접 참조: {kubejs_references}")

    for path in (WORKING, OVERRIDES, OUTPUT):
        if path.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"UTF-8 BOM이 있습니다: {path}")
    if len(names) != 75 or len(class_files) != 42 or len(language_files) != 6:
        errors.append(
            "JAR 구성 변경: "
            f"항목={len(names)}, 클래스={len(class_files)}, 언어={len(language_files)}"
        )
    if len(direct_translation_classes) != 3:
        errors.append(f"직접 번역 키 클래스 수 변경: {len(direct_translation_classes)}")
    if errors:
        raise RuntimeError(
            "More Overlays Updated 검증 실패:\n" + "\n".join(errors[:40])
        )

    return {
        "scope": "More Overlays Updated 전체 번역 재검수",
        "source_jar": source_jar.name,
        "source_jar_sha256": hashlib.sha256(source_jar.read_bytes()).hexdigest(),
        "source_jar_bytes": source_jar.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(class_files),
        "direct_translation_classes_reviewed": len(direct_translation_classes),
        "source_keys_reviewed": len(english),
        "bundled_korean_candidates_reviewed": 0,
        "project_candidates_retained": len(english) - len(overrides),
        "project_candidates_corrected": len(overrides),
        "new_translations": 0,
        "glossary_terms_added": len(GLOSSARY_ROWS),
        "config_sections_reviewed": len(config_sections),
        "config_options_reviewed": len(config_option_keys),
        "legacy_language_categories_reviewed": len(legacy_categories),
        "class_hardcoded_comment_tooltips_deferred": hardcoded_comment_tooltips,
        "class_hardcoded_status_literals_deferred": 9,
        "class_hardcoded_user_visible_literals_deferred": (
            hardcoded_comment_tooltips + 9
        ),
        "project_language_files_reviewed": project_language_files,
        "cross_mod_collision_keys_reviewed": len(project_collision_rows),
        "cross_mod_collision_values_reviewed": len(project_collision_values),
        "harmful_translation_collisions": 0,
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_direct_references": 0,
        "kubejs_files_reviewed": len(kubejs_files),
        "kubejs_direct_references": 0,
        "advancement_files": len(advancement_files),
        "recipe_files": len(recipe_files),
        "guide_files": len(guide_files),
        "validation": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            verify(resolve_source_root(args.instance)), ensure_ascii=False, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
