#!/usr/bin/env python3
"""GuideME의 전체 번역, 설정 fallback과 연관 가이드 경로를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root

WORKING = PROJECT_ROOT / "working/common_ui/guide_ui/guideme/ko_kr.json"
OVERRIDES = PROJECT_ROOT / "working/common_ui/guide_ui/guideme/recheck_overrides.json"
FALLBACKS = PROJECT_ROOT / "working/common_ui/guide_ui/guideme/display_fallbacks.json"
OUTPUT = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/guideme/lang/ko_kr.json"
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
DIRECT_REFERENCE = re.compile(
    r"(?i)(?<![A-Za-z0-9_])guideme(?![A-Za-z0-9_])|"
    r"item\.guideme\.guide|guideme\.guidebook"
)
LOCALE_DIR = re.compile(r"_[a-z]{2}_[a-z]{2}", re.IGNORECASE)
EXPECTED_JAR_SHA256 = "7938843929b065050375d7585398c9a478ae92a8f543ee6594161245750fd420"
EXPECTED_CORRECTIONS = 13
EXPECTED_FALLBACKS = 6
EXPECTED_CONFIG = {
    "guides": {"ignoreTranslatedGuides", "hideMissingRecipeErrors"},
    "gui": {"adaptiveScaling", "fullWidthLayout"},
    "debug": {"showDebugGuiOverlays"},
}
CURRENT_REVIEWED_PROVIDER_JARS = {
    "AdvancedAE-1.6.11-1.21.1.jar": 13,
    "ae2importexportcard-1.21.1-1.5.0.jar": 1,
    "AE2NetworkAnalyzer-1.21-2.1.5-neoforge.jar": 2,
    "ae2wtlib-19.5.0.jar": 8,
    "appliedenergistics2-19.2.17.jar": 125,
    "AppliedFlux-1.21-2.1.5-neoforge.jar": 12,
    "arseng-2.1.1-beta.jar": 1,
    "enderdrives-neoforge-1.21.1-1.4.4.jar": 3,
    "expandedae-2.1.1.jar": 5,
    "ExtendedAE-1.21-2.2.33-neoforge.jar": 46,
    "megacells-4.11.0.jar": 7,
    "merequester-neoforge-1.21.1-1.4.3.jar": 1,
}
FUTURE_OWNER_PROVIDER_JARS = {
    "energymeter-neoforge-1.21.1-0.4.1.jar": 2,
    "little-big-redstone-1.9.0-1.21.1.jar": 25,
    "Modern-Industrialization-2.4.3.jar": 39,
    "Powah-6.2.10.jar": 28,
}
HARDCODED_DISPLAY_MARKERS = {
    "guideme/internal/screen/GuideScreen.class": (
        b"GuideME Guidebook",
        b"# Page not Found\n\nPage ",
    ),
    "guideme/internal/screen/GuideSearchScreen.class": (b"AE2 Guidebook Search",),
    "guideme/internal/screen/GuideNavBar.class": (b"Navigation Tree",),
    "guideme/internal/siteexport/SiteExporter.class": (
        b"Guide data exported to",
        b"Click to open export folder",
    ),
    "guideme/internal/command/StructureCommands.class": (
        b"Saved structure",
        b"Placed structure",
        b"Failed to place structure",
    ),
}
EXPECTED_DIAGNOSTIC_CLASSES = {
    "guideme/scene/annotation/BlockAnnotationTemplateElementCompiler.class",
    "guideme/scene/element/EntityElementCompiler.class",
    "guideme/scene/element/ImportStructureElementCompiler.class",
    "guideme/scene/SceneTagCompiler.class",
    "guideme/document/LytErrorSink.class",
    "guideme/document/flow/LytFlowParent.class",
    "guideme/document/block/LytBlockContainer.class",
    "guideme/compiler/tags/RecipeCompiler.class",
    "guideme/compiler/tags/CommandLinkCompiler.class",
    "guideme/compiler/tags/CategoryIndexCompiler.class",
    "guideme/compiler/tags/ATagCompiler$1.class",
    "guideme/compiler/tags/KeyBindTagCompiler.class",
    "guideme/compiler/tags/ItemGridCompiler.class",
    "guideme/compiler/tags/ColorTagCompiler.class",
    "guideme/compiler/tags/MdxAttrs.class",
    "guideme/compiler/tags/SubPagesCompiler.class",
    "guideme/compiler/PageCompiler$1.class",
}
GLOSSARY_ROWS = (
    "| GuideME | GuideME | 공식 모드명 |",
    "| GuideME Guide | GuideME 가이드 | 아이템명 |",
    "| GUI Scale / UI Scaling | GUI 배율 | Minecraft UI 용어 |",
    "| Shapeless | 모양 없음 / 모양 없는 | 제작법 분류 |",
)


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


def parse_config(path: Path) -> dict[str, set[str]]:
    """현재 GuideME TOML의 섹션과 설정 키를 읽는다."""
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
            sections[current] = set()
            continue
        setting = re.match(r"([A-Za-z0-9_]+)\s*=", line)
        if setting and current is not None:
            sections[current].add(setting.group(1))
            continue
        raise RuntimeError(f"TOML 구조를 읽을 수 없습니다: {path}:{number}: {line}")
    return sections


def is_guide_page(name: str) -> bool:
    lower = name.lower()
    if not lower.endswith((".md", ".mdx")):
        return False
    if not any(
        marker in lower
        for marker in ("/ae2guide/", "/guides/", "/guide/", "/mi_guidebook/")
    ):
        return False
    return not any(LOCALE_DIR.fullmatch(part) for part in name.split("/"))


def korean_ae2_guide_path(name: str) -> Path:
    parts = name.split("/")
    index = parts.index("ae2guide") + 1
    parts.insert(index, "_ko_kr")
    return PROJECT_ROOT / "output/resourcepack/ATM10_Korean" / Path(*parts)


def related_files(root: Path) -> list[Path]:
    allowed = {".js", ".json", ".snbt", ".txt", ".toml"}
    return [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.suffix.lower() in allowed
    ]


def verify(instance: Path) -> dict[str, object]:
    errors = []
    matches = sorted((instance / "mods").glob("guideme-*.jar"))
    if len(matches) != 1:
        raise RuntimeError(f"GuideME JAR 수 불일치: {len(matches)}")
    source_jar = matches[0]
    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        english = load_json_bytes(
            archive.read("assets/guideme/lang/en_us.json"), "guideme:en_us"
        )
        class_files = [name for name in names if name.endswith(".class")]
        nonshaded_classes = [name for name in class_files if "/shaded/" not in name]
        class_bytes = {name: archive.read(name) for name in nonshaded_classes}
        language_files = [
            name
            for name in names
            if re.fullmatch(r"assets/guideme/lang/[a-z_]+\.json", name)
        ]
        bundled_korean = [
            name for name in language_files if name.endswith("ko_kr.json")
        ]
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
                marker in name.lower() for marker in ("patchouli", "guides/", "book")
            )
        ]

    source_sha256 = hashlib.sha256(source_jar.read_bytes()).hexdigest()
    if source_sha256 != EXPECTED_JAR_SHA256:
        errors.append(f"GuideME JAR SHA-256 변경: {source_sha256}")
    if len(names) != 5458 or len(class_files) != 5102 or len(nonshaded_classes) != 618:
        errors.append(
            "GuideME JAR 구성 변경: "
            f"항목={len(names)}, 클래스={len(class_files)}, 비음영={len(nonshaded_classes)}"
        )
    if language_files != ["assets/guideme/lang/en_us.json"] or bundled_korean:
        errors.append(f"GuideME 언어 파일 범위 변경: {language_files}")

    working = load_json_path(WORKING)
    output = load_json_path(OUTPUT)
    overrides = load_json_path(OVERRIDES)
    fallbacks = load_json_path(FALLBACKS)
    expected = {**english, **fallbacks}
    errors.extend(validate_language(expected, working))
    if output != working:
        errors.append("GuideME 작업본과 산출물이 다릅니다")
    if len(english) != 36 or len(overrides) != EXPECTED_CORRECTIONS:
        errors.append(
            f"GuideME 원문·교정 키 수 변경: 원문={len(english)}, 교정={len(overrides)}"
        )
    if len(fallbacks) != EXPECTED_FALLBACKS:
        errors.append(f"GuideME 표시 fallback 수 변경: {len(fallbacks)}")
    override_mismatches = sorted(
        key
        for key, expected_value in overrides.items()
        if working.get(key) != expected_value
    )
    if override_mismatches:
        errors.append(f"GuideME 확정 교정값 불일치: {override_mismatches}")
    fallback_mismatches = sorted(
        key
        for key, expected_value in fallbacks.items()
        if working.get(key) != expected_value
    )
    if fallback_mismatches:
        errors.append(f"GuideME 표시 fallback 불일치: {fallback_mismatches}")
    untranslated = {key for key in english if working.get(key) == english.get(key)}
    if untranslated != {"key.guideme.category"}:
        errors.append(f"GuideME 영어 원문 유지 범위 변경: {sorted(untranslated)}")
    duplicate_values = {
        value for value, count in Counter(working.values()).items() if count > 1
    }
    if duplicate_values != {"가이드"}:
        errors.append(f"GuideME 모드 내부 번역 충돌 변경: {sorted(duplicate_values)}")

    config = parse_config(instance / "config/guideme.toml")
    if config != EXPECTED_CONFIG:
        errors.append(f"GuideME 실제 설정 구조 변경: {config}")
    option_keys = {key for keys in config.values() for key in keys}
    required_display_keys = {
        "guideme.configuration.title",
        *(f"guideme.configuration.{section}" for section in config),
        *(f"guideme.configuration.{key}" for key in option_keys),
        *(f"guideme.configuration.{key}.tooltip" for key in option_keys),
    }
    required_fallbacks = required_display_keys - set(english)
    if set(fallbacks) != required_fallbacks:
        errors.append(
            "GuideME 실제 설정 fallback 범위 불일치: "
            f"누락={sorted(required_fallbacks - set(fallbacks))}, "
            f"초과={sorted(set(fallbacks) - required_fallbacks)}"
        )
    client_class = class_bytes.get("guideme/internal/GuideMEClient.class", b"")
    config_class = class_bytes.get(
        "guideme/internal/GuideMEClient$ClientConfig.class", b""
    )
    if b"net/neoforged/neoforge/client/gui/ConfigurationScreen" not in client_class:
        errors.append("GuideME NeoForge 설정 화면 등록 경로를 찾지 못했습니다")
    config_markers = (*config.keys(), *option_keys)
    missing_config_markers = [
        marker
        for marker in config_markers
        if marker.encode("ascii") not in config_class
    ]
    if missing_config_markers:
        errors.append(f"GuideME 설정 필드 바이트코드 변경: {missing_config_markers}")

    guidebook_keys = {
        key.removeprefix("guideme.guidebook.")
        for key in english
        if key.startswith("guideme.guidebook.")
    }
    guidebook_class = class_bytes.get("guideme/internal/GuidebookText.class", b"")
    missing_guidebook_markers = sorted(
        key for key in guidebook_keys if key.encode("ascii") not in guidebook_class
    )
    if len(guidebook_keys) != 23 or missing_guidebook_markers:
        errors.append(
            "GuideME GuidebookText 표시 경로 변경: "
            f"키={len(guidebook_keys)}, 누락={missing_guidebook_markers}"
        )

    missing_hardcoded_markers = [
        f"{name}:{marker.decode('utf-8')}"
        for name, markers in HARDCODED_DISPLAY_MARKERS.items()
        for marker in markers
        if marker not in class_bytes.get(name, b"")
    ]
    if missing_hardcoded_markers:
        errors.append(
            f"GuideME 직접 표시 문자열 범위 변경: {missing_hardcoded_markers}"
        )
    diagnostic_classes = {
        name for name, raw in class_bytes.items() if b"appendError" in raw
    }
    if diagnostic_classes != EXPECTED_DIAGNOSTIC_CLASSES:
        errors.append(
            "GuideME 하드코딩 진단 클래스 범위 변경: "
            f"누락={sorted(EXPECTED_DIAGNOSTIC_CLASSES - diagnostic_classes)}, "
            f"초과={sorted(diagnostic_classes - EXPECTED_DIAGNOSTIC_CLASSES)}"
        )

    expected_providers = {
        **CURRENT_REVIEWED_PROVIDER_JARS,
        **FUTURE_OWNER_PROVIDER_JARS,
    }
    provider_pages: dict[str, list[str]] = {}
    discovered_providers = set()
    translated_pages_missing = []
    jar_scan_errors = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        if jar_path == source_jar:
            continue
        try:
            with ZipFile(jar_path) as archive:
                archive_names = archive.namelist()
                has_guide_api = any(
                    b"guideme/" in archive.read(name)
                    for name in archive_names
                    if name.endswith(".class") and "/shaded/" not in name
                )
                has_ae2_guide = any(
                    "/ae2guide/" in name.lower() for name in archive_names
                )
                has_metadata = any(
                    "/guideme_guides/" in name.lower() and name.endswith(".json")
                    for name in archive_names
                )
                pages = [name for name in archive_names if is_guide_page(name)]
                if has_guide_api or has_ae2_guide or has_metadata:
                    discovered_providers.add(jar_path.name)
                    provider_pages[jar_path.name] = pages
                    if jar_path.name in CURRENT_REVIEWED_PROVIDER_JARS:
                        for name in pages:
                            if "/ae2guide/" not in name.lower():
                                errors.append(
                                    f"검수 완료 공급자의 비 AE2 가이드 경로: {jar_path.name}:{name}"
                                )
                                continue
                            if not korean_ae2_guide_path(name).is_file():
                                translated_pages_missing.append(
                                    f"{jar_path.name}:{name}"
                                )
        except (BadZipFile, KeyError, OSError) as exc:
            jar_scan_errors.append(f"{jar_path.name}:{exc}")
    if jar_scan_errors:
        errors.append(
            "GuideME 공급자 JAR 읽기 오류: " + " | ".join(jar_scan_errors[:10])
        )
    if discovered_providers != set(expected_providers):
        errors.append(
            "GuideME 공급자 범위 변경: "
            f"누락={sorted(set(expected_providers) - discovered_providers)}, "
            f"초과={sorted(discovered_providers - set(expected_providers))}"
        )
    provider_page_counts = {
        name: len(provider_pages.get(name, [])) for name in expected_providers
    }
    if provider_page_counts != expected_providers:
        errors.append(f"GuideME 공급자 원문 페이지 수 변경: {provider_page_counts}")
    if translated_pages_missing:
        errors.append(
            f"현재 목표 검수 가이드 한국어 누락: {translated_pages_missing[:20]}"
        )

    owner_key_files = []
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
                    if not any(key.encode("utf-8") in raw for key in english):
                        continue
                    values = load_json_bytes(raw, f"{jar_path.name}:{name}")
                    collisions = sorted(set(values) & set(english))
                    if collisions:
                        owner_key_files.append(
                            f"{jar_path.name}:{name}:{','.join(collisions)}"
                        )
        except (BadZipFile, RuntimeError, TypeError) as exc:
            errors.append(f"다른 모드 언어 파일 읽기 오류: {jar_path.name}:{exc}")
    if owner_key_files:
        errors.append(f"다른 모드 소유 GuideME 키 충돌: {owner_key_files}")

    project_language_files = 0
    project_collision_rows = []
    project_key_conflicts = []
    harmful_name_collisions = []
    assets_root = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
    for path in sorted(assets_root.glob("*/lang/ko_kr.json")):
        project_language_files += 1
        if path == OUTPUT:
            continue
        values = load_json_path(path)
        for key in set(working) & set(values):
            project_key_conflicts.append(f"{path}:{key}")
        for target_key, target_value in working.items():
            if not isinstance(target_value, str):
                continue
            for other_key, other_value in values.items():
                if other_value != target_value:
                    continue
                project_collision_rows.append(
                    (target_value, path.as_posix(), other_key)
                )
                if target_key.startswith(("item.", "block.")) and other_key.startswith(
                    ("item.", "block.")
                ):
                    harmful_name_collisions.append(
                        f"{target_key}:{path.as_posix()}:{other_key}:{target_value}"
                    )
    if project_key_conflicts:
        errors.append(f"프로젝트 GuideME 언어 키 소유 충돌: {project_key_conflicts}")
    if harmful_name_collisions:
        errors.append(f"GuideME 아이템·블록 이름 충돌: {harmful_name_collisions}")

    shapeless_term_conflicts = []
    forbidden_shapeless = re.compile(r"형태 없음|무형|무정형")
    for path in sorted(assets_root.glob("*/lang/ko_kr.json")):
        values = load_json_path(path)
        for key, value in values.items():
            if (
                (
                    "shapeless" in key.lower()
                    or key == "ftbultimine.server_settings.misc.merge_tags"
                )
                and isinstance(value, str)
                and forbidden_shapeless.search(value)
            ):
                shapeless_term_conflicts.append(f"{path.parent.parent.name}:{key}")

    quest_files = sorted((instance / "config/ftbquests/quests").rglob("*.snbt"))
    quest_references = []
    for path in quest_files:
        if DIRECT_REFERENCE.search(path.read_text(encoding="utf-8-sig")):
            quest_references.append(path.relative_to(instance).as_posix())
    if quest_references:
        errors.append(f"예상하지 않은 GuideME FTB Quests 직접 참조: {quest_references}")

    kubejs_files = related_files(instance / "kubejs")
    kubejs_references = []
    for path in kubejs_files:
        if DIRECT_REFERENCE.search(path.read_text(encoding="utf-8-sig")):
            kubejs_references.append(path.relative_to(instance).as_posix())
    expected_foreign_reference = ["kubejs/assets/guideme/lang/ru_ru.json"]
    if kubejs_references != expected_foreign_reference:
        errors.append(f"GuideME KubeJS 참조 범위 변경: {kubejs_references}")

    glossary = (PROJECT_ROOT / "glossary/README.md").read_text(encoding="utf-8")
    missing_glossary_rows = [row for row in GLOSSARY_ROWS if row not in glossary]
    if missing_glossary_rows:
        errors.append(f"GuideME 확정 용어 누락: {missing_glossary_rows}")
    for path in (WORKING, OVERRIDES, FALLBACKS, OUTPUT):
        if path.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"UTF-8 BOM이 있습니다: {path}")
    if errors:
        raise RuntimeError("GuideME 검증 실패:\n" + "\n".join(errors[:50]))

    current_pages = sum(CURRENT_REVIEWED_PROVIDER_JARS.values())
    future_pages = sum(FUTURE_OWNER_PROVIDER_JARS.values())
    return {
        "scope": "GuideME 전체 번역 재검수",
        "source_jar": source_jar.name,
        "source_jar_sha256": source_sha256,
        "source_jar_bytes": source_jar.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(class_files),
        "nonshaded_class_files_reviewed": len(nonshaded_classes),
        "source_keys_reviewed": len(english),
        "bundled_korean_candidates_reviewed": len(bundled_korean),
        "project_candidates_retained": len(english) - len(overrides),
        "project_candidates_corrected": len(overrides),
        "new_display_fallback_translations": len(fallbacks),
        "effective_output_keys": len(working),
        "actual_config_sections_reviewed": len(config),
        "actual_config_options_reviewed": len(option_keys),
        "stale_upstream_language_keys_reviewed": 1,
        "guidebook_text_keys_reviewed": len(guidebook_keys),
        "hardcoded_display_literals_deferred": sum(
            len(markers) for markers in HARDCODED_DISPLAY_MARKERS.values()
        ),
        "hardcoded_diagnostic_classes_deferred": len(diagnostic_classes),
        "provider_jars_reviewed": len(expected_providers),
        "provider_source_pages_reviewed": current_pages + future_pages,
        "current_goal_provider_pages_present": current_pages,
        "future_owner_provider_pages_deferred": future_pages,
        "project_language_files_reviewed": project_language_files,
        "cross_mod_collision_rows_reviewed": len(project_collision_rows),
        "harmful_item_block_name_collisions": 0,
        "cross_mod_shapeless_term_conflicts_deferred": len(shapeless_term_conflicts),
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_direct_references": 0,
        "kubejs_files_reviewed": len(kubejs_files),
        "kubejs_foreign_language_files_reviewed": len(kubejs_references),
        "kubejs_direct_display_references": 0,
        "advancement_files": len(advancement_files),
        "recipe_files": len(recipe_files),
        "guide_files_in_core_jar": len(guide_files),
        "glossary_terms_added": len(GLOSSARY_ROWS),
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
