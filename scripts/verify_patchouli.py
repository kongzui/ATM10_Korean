#!/usr/bin/env python3
"""Patchouli의 전체 번역과 연관 가이드 표시 경로를 검증한다."""

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

WORKING = PROJECT_ROOT / "working/common_ui/guide_ui/patchouli/ko_kr.json"
OVERRIDES = PROJECT_ROOT / "working/common_ui/guide_ui/patchouli/recheck_overrides.json"
REPORT = PROJECT_ROOT / "working/common_ui/guide_ui/patchouli/recheck_20260820.json"
OUTPUT = (
    active_output_root() / "resourcepack/ATM10_Korean/assets/patchouli/lang/ko_kr.json"
)
GLOSSARY = PROJECT_ROOT / "glossary/README.md"

EXPECTED_JAR = "Patchouli-1.21.1-93-NEOFORGE.jar"
EXPECTED_JAR_SHA256 = "959af52ed6640c316c3a8469203420be4aeea11ad6603890ba83bf48f5d9f993"
EXPECTED_CONFIG_SHA256 = (
    "d9a6d7cadb6d473cf087602d9866840d2bb7f2c16915267eb3f6fbf68d5d774d"
)
RUNTIME_PREFIXES = (
    "item.patchouli.guide_book",
    "patchouli.subtitle.",
    "patchouli.gui.",
    "patchouli.networking.",
)
EXPECTED_OVERRIDES = {
    "patchouli.gui.lexicon.progress_tooltip.info": (
        "발전 과제를 완료하여 더 많은 항목의 잠금을 해제하세요!"
    ),
    "patchouli.gui.lexicon.shapeless": "모양 없음",
    "patchouli.gui.lexicon.needs_air": "(빨간색으로 표시된 블록 제거)",
    "patchouli.gui.lexicon.button.resize": "GUI 배율 조정",
}
UNREACHABLE_TEST_KEYS = {
    "item.patchouli.comprehensive_test_book.name",
    "item.patchouli.comprehensive_test_book.landing",
    "item.patchouli:test_book_1.name",
    "item.patchouli:test_book_1.landing",
    "item.patchouli:test_book_2.name",
    "item.patchouli:test_book_2.landing",
    "item.patchouli:test_completion.name",
    "item.patchouli:test_completion.landing",
    "item.patchouli:intro_book.name",
    "item.patchouli:intro_book.subtitle",
    "item.patchouli:intro_book.landing",
    "item.patchouli:pamphlet.name",
    "item.patchouli:pamphlet.landing",
}
DYNAMIC_OR_RESOURCE_KEYS = {
    "patchouli.gui.lexicon.button.resize.size0",
    "patchouli.gui.lexicon.button.resize.size1",
    "patchouli.gui.lexicon.button.resize.size2",
    "patchouli.gui.lexicon.button.resize.size3",
    "patchouli.gui.lexicon.button.resize.size4",
    "patchouli.gui.lexicon.button.resize.size5",
    "patchouli.gui.lexicon.seconds",
    "patchouli.gui.lexicon.sneak",
    "patchouli.gui.lexicon.view",
    "patchouli.subtitle.book_flip",
    "patchouli.subtitle.book_open",
}
EXPECTED_BUNDLED_RUNTIME_MISSING = {
    "patchouli.gui.lexicon.button.toggle_mock_header",
    "patchouli.networking.open_book.failed",
    "patchouli.networking.reload_contents.failed",
}
EXPECTED_CONFIG_OPTIONS = {
    "disableAdvancementLocking",
    "noAdvancementBooks",
    "testingMode",
    "inventoryButtonBook",
    "useShiftForQuickLookup",
    "textOverflowMode",
    "quickLookupTime",
}
EXPECTED_PROVIDER_JARS = {
    "actuallyadditions-1.3.26+mc1.21.1.jar": 6,
    "AdvancedPeripherals-1.21.1-0.7.62b.jar": 24,
    "allthemodium-3.0.1_mc_1.21.1.jar": 19,
    "Apotheosis-1.21.1-8.5.4.jar": 126,
    "ars_elemancy-1.21.1-1.17.jar": 15,
    "ars_elemental-1.21.1-0.7.10.0.jar": 1,
    "ars_nouveau-1.21.1-5.12.0.jar": 288,
    "ars_ocultas-1.21.1-2.4.1.jar": 4,
    "buildinggadgets2-1.3.9.jar": 29,
    "enderio-8.2.11-beta.jar": 2,
    "ExtremeReactors2-1.21.1-2.4.28.jar": 93,
    "iceandfire-2.0-beta.17.jar": 2,
    "industrialforegoing-1.21-3.6.38.jar": 80,
    "irons_spellbooks-1.21.1-3.16.1.jar": 10,
    "justdirethings-1.5.7.jar": 165,
    "laserio-1.9.11.jar": 40,
    "livingthings-neoforge-1.21.1-2.3.0.jar": 41,
    "merrymaking-1.21.1-16.jar": 48,
    "mffs-5.4.27.jar": 49,
    "modular-routers-13.2.5+mc1.21.1.jar": 61,
    "ModularBees-1.21.1-3.2-neoforge.jar": 18,
    "MysticalAgradditions-1.21.1-8.0.13.jar": 6,
    "MysticalAgriculture-1.21.1-8.0.26.jar": 71,
    "NaturesAura-41.9.jar": 100,
    "pneumaticcraft-repressurized-8.2.20+mc1.21.1.jar": 235,
    "productivebees-1.21.1-13.13.5.jar": 81,
    "productivemetalworks-1.21.1-1.15.0.jar": 4,
    "productivetrees-1.21.1-1.0.0.jar": 13,
    "railcraft-reborn-1.21.1-1.2.10.jar": 42,
    "rftoolsbase-1.21-6.0.11.jar": 15,
    "rftoolsbuilder-1.21-7.0.5.jar": 25,
    "rftoolspower-1.21-7.0.6.jar": 15,
    "rftoolsstorage-1.21-6.0.5.jar": 9,
    "rftoolsutility-1.21-7.0.12.jar": 27,
    "silent-gear-1.21.1-neoforge-4.2.1.1.jar": 1,
    "starbunclemania-1.21.1-1.5.7.jar": 15,
    "sushigocrafting-1.21-0.6.5.jar": 15,
    "xnet-1.21-7.0.7.jar": 12,
}
EXPECTED_QUEST_REFERENCES = {
    "config/ftbquests/quests/chapters/allthemodium.snbt": 2,
    "config/ftbquests/quests/chapters/chapter_2_the_star.snbt": 1,
    "config/ftbquests/quests/chapters/elmystical_agriculturerr.snbt": 2,
    "config/ftbquests/quests/chapters/extreme_reactors.snbt": 1,
    "config/ftbquests/quests/chapters/industrial_foregoing.snbt": 2,
    "config/ftbquests/quests/chapters/justdirethings.snbt": 1,
    "config/ftbquests/quests/chapters/natures_aura.snbt": 1,
    "config/ftbquests/quests/chapters/pneumaticcraft.snbt": 1,
    "config/ftbquests/quests/chapters/productive_bees.snbt": 1,
    "config/ftbquests/quests/chapters/productive_trees.snbt": 1,
}
EXPECTED_KUBE_RELATED_FILES = {
    "kubejs/assets/extreme_reactors2/lang/pt_br.json",
    "kubejs/assets/livingthings/lang/ru_ru.json",
    "kubejs/assets/modular_routers/lang/pt_br.json",
    "kubejs/data/actuallyadditions/patchouli_books/booklet/book.json",
    "kubejs/data/advancedperipherals/patchouli_books/manual/book.json",
    "kubejs/data/allthemodium/patchouli_books/allthemodium_book/book.json",
    "kubejs/data/bigreactors/patchouli_books/erguide/book.json",
    "kubejs/data/industrialforegoing/patchouli_books/industrial_foregoing/book.json",
    "kubejs/data/justdirethings/patchouli_books/justdirethingsbook/book.json",
    "kubejs/data/livingthings/patchouli_books/lexicon/book.json",
    "kubejs/data/railcraft/patchouli_books/guide_book/book.json",
    "kubejs/data/sushigocrafting/patchouli_books/sushigocrafting/book.json",
    "kubejs/server_scripts/Tweaks/recipes_fix.js",
    "kubejs/server_scripts/Tweaks/tags.js",
}
HARDCODED_MARKERS = {
    "vazkii/patchouli/common/item/ItemModBook.class": (b"Book ID: \x01",),
    "vazkii/patchouli/client/book/text/BookTextParser.class": (
        b"[MISSING FUNCTION: \x01]",
        b"BAD LINK: Cannot specify anchor when linking to a category",
        b" (INVALID ANCHOR:\x01)",
        b"BAD LINK: \x01",
    ),
    "vazkii/patchouli/neoforge/common/NeoForgePatchouliConfig.class": (
        b"Set this to true to disable advancement locking for ALL books",
        b"Granular list of Book ID's to disable advancement locking",
        b"Enable testing mode.",
        b"Set this to the ID of a book to have it show up",
        b"Set this to true to use Shift instead of Ctrl",
        b"Set how text overflow should be coped with",
        b"How long in ticks the quick lookup key needs to be pressed",
    ),
}
GLOSSARY_ROWS = (
    "| Patchouli | Patchouli | 공식 모드명 |",
    "| Guide Book | 가이드북 | 아이템명 |",
    "| Entry / Chapter | 항목 | Patchouli 가이드 UI 용어 |",
    "| Bookmark (Guide Book) | 책갈피 | Patchouli 가이드 UI 용어 |",
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
PATCHOULI_CODE = re.compile(r"\$\([^)]*\)")
URL = re.compile(r"https?://[^)\s]+")
PROVIDER_PAGE = re.compile(
    r"^(?:assets|data)/([^/]+)/patchouli_books/([^/]+)/en_us/(.+\.json)$"
)
KUBE_EXTENSIONS = {".js", ".json", ".snbt", ".txt", ".toml"}
SHAPELESS_CONFLICT = re.compile(r"무형|무정형|형태 없")


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
        if Counter(PATCHOULI_CODE.findall(source)) != Counter(
            PATCHOULI_CODE.findall(translated)
        ):
            errors.append(f"Patchouli 서식 코드 불일치: {key}")
        if URL.findall(source) != URL.findall(translated):
            errors.append(f"URL 불일치: {key}")
        if source.count("\n") != translated.count("\n"):
            errors.append(f"줄바꿈 수 불일치: {key}")
    return errors


def scan_provider_guides(
    instance: Path, errors: list[str]
) -> tuple[dict[str, int], int, int, int]:
    """설치 JAR의 Patchouli 영어 페이지와 한국어 후보 범위를 센다."""
    provider_counts = {}
    bundled_korean = 0
    project_korean = 0
    scan_errors = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        try:
            with ZipFile(jar_path) as archive:
                names = set(archive.namelist())
                pages = []
                for name in names:
                    match = PROVIDER_PAGE.match(name)
                    if match:
                        pages.append(match.groups())
                if not pages:
                    continue
                provider_counts[jar_path.name] = len(pages)
                for namespace, book, relative in pages:
                    source = (
                        f"assets/{namespace}/patchouli_books/{book}/en_us/{relative}"
                    )
                    data_source = (
                        f"data/{namespace}/patchouli_books/{book}/en_us/{relative}"
                    )
                    actual_source = source if source in names else data_source
                    korean_source = actual_source.replace("/en_us/", "/ko_kr/", 1)
                    if korean_source in names:
                        bundled_korean += 1
                    project_path = (
                        active_output_root()
                        / "resourcepack/ATM10_Korean/assets"
                        / namespace
                        / "patchouli_books"
                        / book
                        / "ko_kr"
                        / relative
                    )
                    if project_path.is_file():
                        project_korean += 1
        except BadZipFile as exc:
            scan_errors.append(f"{jar_path.name}: {exc}")
    if scan_errors:
        errors.append("Patchouli 제공 JAR 읽기 오류: " + " | ".join(scan_errors))
    if provider_counts != EXPECTED_PROVIDER_JARS:
        errors.append(
            "Patchouli 제공 모드·페이지 범위 변경: "
            f"현재={provider_counts}, 예상={EXPECTED_PROVIDER_JARS}"
        )
    source_pages = sum(provider_counts.values())
    return provider_counts, source_pages, bundled_korean, project_korean


def scan_shapeless_terms(instance: Path, errors: list[str]) -> tuple[int, int]:
    """설치 모드의 Shapeless 표시 용어 충돌을 센다."""
    output_root = active_output_root() / "resourcepack/ATM10_Korean/assets"
    source_rows = 0
    conflicts = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        try:
            with ZipFile(jar_path) as archive:
                for name in archive.namelist():
                    match = re.fullmatch(r"assets/([^/]+)/lang/en_us\.json", name)
                    if not match:
                        continue
                    try:
                        english = json.loads(archive.read(name).decode("utf-8-sig"))
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue
                    output_path = output_root / match.group(1) / "lang/ko_kr.json"
                    korean = (
                        load_json_path(output_path) if output_path.is_file() else {}
                    )
                    for key, value in english.items():
                        if not isinstance(value, str) or not re.search(
                            r"(?i)\bshapeless\b", value
                        ):
                            continue
                        source_rows += 1
                        translated = korean.get(key)
                        if isinstance(translated, str) and SHAPELESS_CONFLICT.search(
                            translated
                        ):
                            conflicts.append(f"{match.group(1)}:{key}")
        except BadZipFile:
            continue
    if source_rows != 15:
        errors.append(f"Shapeless 교차 검수 행 수 변경: {source_rows}")
    if len(conflicts) != 9:
        errors.append(f"소유 모드 차례로 보류한 Shapeless 충돌 변경: {conflicts}")
    if "patchouli:patchouli.gui.lexicon.shapeless" in conflicts:
        errors.append("Patchouli Shapeless 용어 충돌이 남아 있습니다")
    return source_rows, len(conflicts)


def verify(instance: Path) -> dict[str, object]:
    """현재 설치본과 프로젝트 산출물을 전수 검증한다."""
    errors: list[str] = []
    jar_matches = sorted((instance / "mods").glob("Patchouli-*.jar"))
    if [path.name for path in jar_matches] != [EXPECTED_JAR]:
        raise RuntimeError(
            f"Patchouli JAR 범위 변경: {[path.name for path in jar_matches]}"
        )
    jar_path = jar_matches[0]
    jar_sha256 = hashlib.sha256(jar_path.read_bytes()).hexdigest()
    if jar_sha256 != EXPECTED_JAR_SHA256:
        errors.append(f"Patchouli JAR SHA-256 변경: {jar_sha256}")

    with ZipFile(jar_path) as archive:
        names = archive.namelist()
        english = load_json_bytes(
            archive.read("assets/patchouli/lang/en_us.json"), "Patchouli en_us"
        )
        bundled = load_json_bytes(
            archive.read("assets/patchouli/lang/ko_kr.json"), "Patchouli ko_kr"
        )
        class_files = {
            name: archive.read(name) for name in names if name.endswith(".class")
        }
        class_referenced = {
            key
            for key in english
            if any(key.encode() in raw for raw in class_files.values())
        }
        for class_name, markers in HARDCODED_MARKERS.items():
            raw = class_files.get(class_name)
            if raw is None:
                errors.append(f"하드코딩 검사 클래스 누락: {class_name}")
                continue
            for marker in markers:
                if marker not in raw:
                    errors.append(f"하드코딩 표시 경로 변경: {class_name}:{marker!r}")
        config_screen_classes = [
            name
            for name, raw in class_files.items()
            if b"ConfigurationScreen" in raw or b"IConfigScreenFactory" in raw
        ]
        sound_values = load_json_bytes(
            archive.read("assets/patchouli/sounds.json"), "Patchouli sounds"
        )
        core_book_files = [
            name
            for name in names
            if "/patchouli_books/" in name and name.endswith(".json")
        ]
        advancement_files = [
            name for name in names if "/advancement" in name and name.endswith(".json")
        ]
        recipe_files = [
            name for name in names if "/recipe" in name and name.endswith(".json")
        ]

    if len(english) != 92 or len(bundled) != 87:
        errors.append(
            f"언어 키 수 변경: 영어={len(english)}, 내장 한국어={len(bundled)}"
        )
    runtime_english = {
        key: value for key, value in english.items() if key.startswith(RUNTIME_PREFIXES)
    }
    unreachable = set(english) - set(runtime_english)
    if len(runtime_english) != 79 or unreachable != UNREACHABLE_TEST_KEYS:
        errors.append(
            f"런타임·시험 키 범위 변경: 런타임={len(runtime_english)}, "
            f"시험={sorted(unreachable)}"
        )
    bundled_runtime = set(runtime_english) & set(bundled)
    if set(runtime_english) - bundled_runtime != EXPECTED_BUNDLED_RUNTIME_MISSING:
        errors.append("내장 한국어의 런타임 누락 키 범위가 바뀌었습니다")

    expected_class_referenced = set(runtime_english) - DYNAMIC_OR_RESOURCE_KEYS
    if class_referenced & set(runtime_english) != expected_class_referenced:
        errors.append("Patchouli 클래스 언어 키 참조 범위가 바뀌었습니다")
    if class_referenced & UNREACHABLE_TEST_KEYS:
        errors.append("시험 책 키가 배포 클래스에 다시 연결되었습니다")
    if config_screen_classes:
        errors.append(f"새 설정 화면 등록 경로 발견: {config_screen_classes}")
    expected_sounds = {
        "book_flip": {
            "category": "player",
            "sounds": ["patchouli:book_flip"],
            "subtitle": "patchouli.subtitle.book_flip",
        },
        "book_open": {
            "category": "player",
            "sounds": ["patchouli:book_open"],
            "subtitle": "patchouli.subtitle.book_open",
        },
    }
    if sound_values != expected_sounds:
        errors.append("Patchouli 소리 자막 경로가 바뀌었습니다")
    if core_book_files or advancement_files or recipe_files:
        errors.append(
            "Patchouli 본체 데이터 범위 변경: "
            f"책={core_book_files}, 발전={advancement_files}, 제작법={recipe_files}"
        )

    working = load_json_path(WORKING)
    output = load_json_path(OUTPUT)
    overrides = load_json_path(OVERRIDES)
    report = load_json_path(REPORT)
    errors.extend(validate_language(runtime_english, working))
    errors.extend(validate_language(runtime_english, output))
    if working != output:
        errors.append("Patchouli working과 output 언어 파일이 다릅니다")
    if overrides != EXPECTED_OVERRIDES:
        errors.append(f"Patchouli 재검수 교정 목록 변경: {overrides}")
    for key, value in EXPECTED_OVERRIDES.items():
        if output.get(key) != value:
            errors.append(f"Patchouli 교정값 불일치: {key}")
    if OUTPUT.read_bytes().startswith(b"\xef\xbb\xbf"):
        errors.append("Patchouli 산출물에 UTF-8 BOM이 있습니다")

    config_path = instance / "config/patchouli-client.toml"
    config_bytes = config_path.read_bytes()
    config_text = config_bytes.decode("utf-8-sig")
    config_options = {
        match.group(1)
        for line in config_text.splitlines()
        if (match := re.match(r"([A-Za-z0-9_]+)\s*=", line))
    }
    config_comment_lines = sum(
        line.startswith("#") for line in config_text.splitlines()
    )
    if hashlib.sha256(config_bytes).hexdigest() != EXPECTED_CONFIG_SHA256:
        errors.append("Patchouli 실제 클라이언트 설정 파일이 바뀌었습니다")
    if config_options != EXPECTED_CONFIG_OPTIONS or config_comment_lines != 8:
        errors.append(
            f"Patchouli 설정 범위 변경: 옵션={config_options}, 주석={config_comment_lines}"
        )

    provider_counts, source_pages, bundled_pages, project_pages = scan_provider_guides(
        instance, errors
    )
    if (source_pages, bundled_pages, project_pages) != (1807, 69, 1382):
        errors.append(
            "Patchouli 제공 가이드 집계 변경: "
            f"영어={source_pages}, 내장 한국어={bundled_pages}, "
            f"프로젝트 후보={project_pages}"
        )

    quest_files = sorted((instance / "config/ftbquests/quests").rglob("*.snbt"))
    quest_references = {}
    quest_language_display_lines = []
    for path in quest_files:
        text = path.read_text(encoding="utf-8-sig")
        count = text.count('"patchouli:book"')
        relative = path.relative_to(instance).as_posix()
        if count:
            quest_references[relative] = count
        if "/lang/" in relative:
            for line in text.splitlines():
                if re.search(r"(?i)patchouli", line) and "{image:" not in line:
                    quest_language_display_lines.append(f"{relative}:{line.strip()}")
    if len(quest_files) != 142 or quest_references != EXPECTED_QUEST_REFERENCES:
        errors.append(f"Patchouli FTB Quests 참조 범위 변경: {quest_references}")
    if quest_language_display_lines:
        errors.append(
            "Patchouli FTB Quests 사용자 표시 문구 발견: "
            + " | ".join(quest_language_display_lines[:10])
        )

    kube_files = []
    kube_related = set()
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in KUBE_EXTENSIONS:
            continue
        kube_files.append(path)
        relative = path.relative_to(instance).as_posix()
        text = path.read_text(encoding="utf-8-sig")
        if re.search(r"(?i)patchouli", text) or "/patchouli_books/" in relative:
            kube_related.add(relative)
    if len(kube_files) != 1020 or kube_related != EXPECTED_KUBE_RELATED_FILES:
        errors.append(f"Patchouli KubeJS 참조 범위 변경: {sorted(kube_related)}")
    if (instance / "kubejs/assets/patchouli/lang/ko_kr.json").exists():
        errors.append("KubeJS에 Patchouli 소유 한국어 언어 파일이 새로 생겼습니다")

    language_paths = sorted(
        (active_output_root() / "resourcepack/ATM10_Korean/assets").glob(
            "*/lang/ko_kr.json"
        )
    )
    guide_book_rows = []
    for path in language_paths:
        values = load_json_path(path)
        for key, value in values.items():
            if value == "가이드북" and key.startswith(("item.", "block.")):
                guide_book_rows.append(f"{path.parent.parent.name}:{key}")
    if len(language_paths) != 285:
        errors.append(f"프로젝트 언어 파일 수 변경: {len(language_paths)}")
    if guide_book_rows != ["patchouli:item.patchouli.guide_book"]:
        errors.append(f"가이드북 아이템명 충돌 발견: {guide_book_rows}")
    shapeless_rows, shapeless_conflicts = scan_shapeless_terms(instance, errors)

    glossary_text = GLOSSARY.read_text(encoding="utf-8")
    for row in GLOSSARY_ROWS:
        if row not in glossary_text:
            errors.append(f"Patchouli 용어집 행 누락: {row}")
    if report.get("validation") != "passed":
        errors.append("Patchouli 재검수 보고서 상태가 passed가 아닙니다")
    language_review = report.get("language_review")
    if not isinstance(language_review, dict) or language_review.get(
        "project_candidates_corrected"
    ) != len(EXPECTED_OVERRIDES):
        errors.append("Patchouli 재검수 보고서 교정 집계 불일치")
    application = report.get("application")
    output_sha256 = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    if (
        not isinstance(application, dict)
        or application.get("status") != "applied_and_verified"
        or application.get("sha256") != output_sha256
        or application.get("unexpected_changes") != 0
    ):
        errors.append("Patchouli 재검수 보고서 게임 적용 집계 불일치")

    if errors:
        raise RuntimeError("Patchouli 재검수 검증 실패:\n" + "\n".join(errors[:50]))
    return {
        "scope": "Patchouli 전체 번역 재검수",
        "source_jar": jar_path.name,
        "source_jar_sha256": jar_sha256,
        "source_jar_bytes": jar_path.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(class_files),
        "source_keys_reviewed": len(english),
        "runtime_keys_reviewed": len(runtime_english),
        "unreachable_test_keys_reviewed": len(UNREACHABLE_TEST_KEYS),
        "bundled_korean_candidates_reviewed": len(bundled),
        "bundled_runtime_candidates_reviewed": len(bundled_runtime),
        "project_candidates_retained": len(runtime_english) - len(EXPECTED_OVERRIDES),
        "project_candidates_corrected": len(EXPECTED_OVERRIDES),
        "effective_output_keys": len(output),
        "class_referenced_language_keys": len(expected_class_referenced),
        "resource_or_dynamic_language_keys": len(DYNAMIC_OR_RESOURCE_KEYS),
        "sound_subtitle_keys_reviewed": 2,
        "client_config_options_reviewed": len(config_options),
        "client_config_comment_lines_reviewed": config_comment_lines,
        "hardcoded_advanced_tooltips_deferred": 1,
        "hardcoded_book_parser_diagnostics_deferred": 4,
        "hardcoded_config_comments_deferred": 7,
        "provider_jars_reviewed": len(provider_counts),
        "provider_source_pages_inventoried": source_pages,
        "provider_bundled_korean_candidates": bundled_pages,
        "project_provider_korean_candidates_present": project_pages,
        "project_provider_korean_candidates_missing": source_pages - project_pages,
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_reference_files": len(quest_references),
        "ftbquests_component_references": sum(quest_references.values()),
        "kubejs_files_reviewed": len(kube_files),
        "kubejs_related_files": len(kube_related),
        "project_language_files_reviewed": len(language_paths),
        "harmful_guide_book_name_collisions": 0,
        "cross_mod_shapeless_rows_reviewed": shapeless_rows,
        "remaining_shapeless_conflicts_deferred": shapeless_conflicts,
        "core_advancement_files": len(advancement_files),
        "core_recipe_files": len(recipe_files),
        "core_patchouli_book_files": len(core_book_files),
        "glossary_terms_added": len(GLOSSARY_ROWS),
        "validation": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    print(json.dumps(verify(instance), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
