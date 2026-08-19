#!/usr/bin/env python3
"""Modonomicon 전체 번역과 실제 가이드 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root

WORK_ROOT = PROJECT_ROOT / "working/common_ui/guide_ui/modonomicon"
WORKING = WORK_ROOT / "ko_kr.json"
FALLBACKS = WORK_ROOT / "display_fallbacks.json"
OVERRIDES = WORK_ROOT / "recheck_overrides.json"
REPORT = WORK_ROOT / "recheck_20260820.json"
OUTPUT = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/modonomicon/lang/ko_kr.json"
)
GLOSSARY = PROJECT_ROOT / "glossary/README.md"

EXPECTED_JAR = "modonomicon-1.21.1-neoforge-1.120.1.jar"
EXPECTED_JAR_SHA256 = "f5753e656ea6f200f3862d95a3ffab660470f09cdd222566b562aa3e465dd703"
EXPECTED_CONFIG_SHA256 = (
    "f7301ac5c174fd4958b6a7bbca7d6211da2f4ac83f85ef87e55461a2110f9044"
)
DISPLAY_PREFIXES = (
    "item.modonomicon.",
    "itemGroup.modonomicon",
    "modonomicon.command.",
    "modonomicon.configuration.",
    "modonomicon.gui.",
    "modonomicon.multiblock.",
    "modonomicon.subtitle.",
    "tooltip.modonomicon.",
)
EXPECTED_NON_DEMO_EXCLUDED = {
    "advancement.minecraft.husbandry.ride_a_boat_with_a_goat.title",
    "advancement.minecraft.story.mine_stone.title",
    "test.test.test",
}
EXPECTED_CLASS_UNREFERENCED = {
    "item.modonomicon.modonomicon",
    "modonomicon.configuration.enableSmoothZoom",
    "modonomicon.configuration.fontFallbackLocales",
    "modonomicon.configuration.qol",
    "modonomicon.configuration.storeLastOpenPageWhenClosingEntry",
}
EXPECTED_CONFIG_OPTIONS = {
    "enableSmoothZoom",
    "fontFallbackLocales",
    "storeLastOpenPageWhenClosingEntry",
}
EXPECTED_FALLBACKS = {
    "modonomicon.configuration.enableSmoothZoom.tooltip": (
        "책의 범주 화면을 확대하거나 축소할 때 부드럽게 전환합니다."
    ),
    "modonomicon.configuration.storeLastOpenPageWhenClosingEntry.tooltip": (
        "항목을 닫을 때 마지막으로 열었던 페이지를 저장합니다. "
        "이 설정과 관계없이 Esc 키로 책 전체를 닫으면 마지막 페이지가 저장됩니다."
    ),
    "modonomicon.configuration.fontFallbackLocales.tooltip": (
        "현재 언어를 기본 Modonomicon 글꼴이 지원하지 않아 글자가 네모로 표시되면, "
        "이 목록에 로케일 코드를 추가하여 Minecraft 기본 글꼴을 사용하세요."
    ),
}
EXPECTED_OVERRIDES = {
    "modonomicon.command.failure": (
        "Modonomicon이 사용자를 대신해 명령어를 실행하려 했습니다"
        "(예: 항목을 처음 읽었거나 명령어 버튼·링크를 클릭했을 때). "
        "하지만 이 명령어의 최대 사용 횟수에 이미 도달했습니다."
    ),
    "modonomicon.command.reload_requested": (
        "리소스 팩과 데이터 팩을 다시 불러오도록 요청했습니다."
    ),
    "modonomicon.gui.bookmarks.no_results": "아직 책갈피가 없습니다.",
    "modonomicon.gui.button.read_all": "모든 항목을 읽은 것으로 표시",
    "modonomicon.gui.button.read_all.tooltip.read_all": (
        "§c모든§r 항목(잠긴 항목 포함)을 읽은 것으로 표시합니다."
    ),
    "modonomicon.gui.button.read_all.tooltip.read_unlocked": (
        "모든 §a잠금 해제된§r 항목을 읽은 것으로 표시합니다."
    ),
    "modonomicon.gui.button.read_all.tooltip.shift": (
        "Shift-클릭하여 §c모든§r 항목(잠긴 항목 포함)을 읽은 것으로 표시합니다."
    ),
    "modonomicon.gui.button.read_all.tooltip.shift_warning": (
        "§l§c경고:§r 이렇게 하면 진행도에 따라 잠금이 해제되는 책을 "
        "정상적으로 읽기 어려워질 수 있습니다."
    ),
    "modonomicon.gui.hover.book_entry_link_locked_info.hint": (
        "힌트: 이 항목이 속한 범주는 %s입니다."
    ),
    "modonomicon.gui.hover.book_link.error": (
        "잘못된 링크: %s. 책의 저자나 번역가에게 수정을 요청하세요. "
        '자세한 내용은 로그의 "Failed to parse book link." 문맥에서 확인할 수 있습니다.'
    ),
    "modonomicon.gui.hover.book_page_link_locked_info.hint": (
        "힌트: 이 페이지는 항목 %s에 있으며, 해당 항목은 범주 %s에 있습니다."
    ),
    "modonomicon.gui.hover.command_link.unavailable": (
        "이 명령어를 너무 많이 사용하여 다시 사용할 수 없습니다."
    ),
    "modonomicon.gui.hover.item_link_info": (
        "클릭하여 JEI에서 제작법을 보고, Shift-클릭하여 사용법을 보세요."
    ),
    "modonomicon.gui.hover.item_link_info.no_jei": (
        "클릭으로 제작법과 사용법을 보려면 JEI를 설치하세요."
    ),
    "modonomicon.gui.hover.item_link_info_line2": (
        "제작법이나 사용법이 없으면 아무 작업도 하지 않습니다."
    ),
    "modonomicon.gui.page.entity.loading_error": "개체 불러오기 실패",
    "modonomicon.gui.recipe_page.recipe_missing": (
        "다음 제작법을 찾을 수 없습니다: %s. 모드에 문제가 있거나 "
        "모드팩에서 해당 제작법을 비활성화했을 수 있습니다."
    ),
    "modonomicon.gui.search.info": "항목을 검색하려면 찾을 내용을 바로 입력하세요.\n",
    "modonomicon.multiblock.remove_blocks": " (빨간색으로 표시된 블록 제거)",
    "modonomicon.subtitle.turn_page": "페이지가 넘어감",
    "tooltip.modonomicon.condition.advancement.loading": "불러오는 중...",
    "tooltip.modonomicon.condition.entry_read": (
        '다음 항목을 읽어야 함: %s\n힌트: 오른쪽 위의 "눈" 버튼으로 '
        "모든 항목을 읽은 것으로 표시할 수 있습니다."
    ),
    "tooltip.modonomicon.condition.mod_loaded": ("다음 모드가 설치되어 있어야 함: %s"),
    "tooltip.modonomicon.fluid.amount": "%s mB",
    "tooltip.modonomicon.fluid.amount_and_capacity": "%s / %s mB",
    "tooltip.modonomicon.recipe.crafting_shapeless": "모양 없음",
}
EXPECTED_PROVIDERS = {
    "occultism-1.21.1-neoforge-1.223.0.jar": {
        "book_files": 240,
        "book_roots": 1,
        "categories": 9,
        "entries": 230,
        "multiblocks": 20,
        "translation_keys": 1220,
        "bundled_korean": 1220,
        "project_korean": 1220,
    },
    "theurgy-1.21.1-neoforge-1.73.1.jar": {
        "book_files": 93,
        "book_roots": 1,
        "categories": 3,
        "entries": 89,
        "multiblocks": 7,
        "translation_keys": 746,
        "bundled_korean": 0,
        "project_korean": 746,
    },
}
GLOSSARY_ROWS = (
    "| Modonomicon | Modonomicon | 공식 모드명 |",
    "| Mark as Read | 읽은 것으로 표시 | 가이드 UI 용어 |",
    "| Millibucket | mB | 유체 부피 단위 |",
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
URL = re.compile(r"https?://[^)\s]+")
BOOK_FILE = re.compile(r"^data/([^/]+)/modonomicon/books/(.+\.json)$")
MULTIBLOCK_FILE = re.compile(r"^data/([^/]+)/modonomicon/multiblocks/.+\.json$")
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
        if URL.findall(source) != URL.findall(translated):
            errors.append(f"URL 불일치: {key}")
        if source.count("\n") != translated.count("\n"):
            errors.append(f"줄바꿈 수 불일치: {key}")
        if source.count("\\") != translated.count("\\"):
            errors.append(f"Modonomicon 줄 연결 문자 불일치: {key}")
    return errors


def collect_strings(value: object, strings: list[str]) -> None:
    """중첩 JSON의 문자열 값을 모두 모은다."""
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, list):
        for child in value:
            collect_strings(child, strings)
    elif isinstance(value, dict):
        for child in value.values():
            collect_strings(child, strings)


def scan_provider_guides(
    instance: Path, errors: list[str]
) -> dict[str, dict[str, int]]:
    """Modonomicon 책 제공 모드와 해당 번역 키 범위를 센다."""
    found: dict[str, dict[str, int]] = {}
    output_root = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        try:
            with ZipFile(jar_path) as archive:
                names = archive.namelist()
                book_matches = [
                    (name, match) for name in names if (match := BOOK_FILE.match(name))
                ]
                if not book_matches:
                    continue
                namespaces = {match.group(1) for _, match in book_matches}
                strings: list[str] = []
                book_roots = categories = entries = 0
                for name, match in book_matches:
                    relative = match.group(2)
                    if relative.endswith("/book.json"):
                        book_roots += 1
                    elif "/categories/" in relative:
                        categories += 1
                    elif "/entries/" in relative:
                        entries += 1
                    data = load_json_bytes(
                        archive.read(name), f"{jar_path.name}:{name}"
                    )
                    collect_strings(data, strings)
                english: dict[str, object] = {}
                bundled: set[str] = set()
                project: set[str] = set()
                for namespace in namespaces:
                    english_path = f"assets/{namespace}/lang/en_us.json"
                    if english_path in names:
                        english.update(
                            load_json_bytes(
                                archive.read(english_path),
                                f"{jar_path.name}:{english_path}",
                            )
                        )
                    bundled_path = f"assets/{namespace}/lang/ko_kr.json"
                    if bundled_path in names:
                        bundled.update(
                            load_json_bytes(
                                archive.read(bundled_path),
                                f"{jar_path.name}:{bundled_path}",
                            )
                        )
                    project_path = output_root / namespace / "lang/ko_kr.json"
                    if project_path.is_file():
                        project.update(load_json_path(project_path))
                referenced = {value for value in strings if value in english}
                found[jar_path.name] = {
                    "book_files": len(book_matches),
                    "book_roots": book_roots,
                    "categories": categories,
                    "entries": entries,
                    "multiblocks": sum(
                        bool(MULTIBLOCK_FILE.match(name)) for name in names
                    ),
                    "translation_keys": len(referenced),
                    "bundled_korean": len(referenced & bundled),
                    "project_korean": len(referenced & project),
                }
        except BadZipFile as exc:
            errors.append(f"Modonomicon 제공 JAR 읽기 오류: {jar_path.name}: {exc}")
    if found != EXPECTED_PROVIDERS:
        errors.append(f"Modonomicon 제공 가이드 범위 변경: {found}")
    return found


def scan_shapeless_terms(instance: Path, errors: list[str]) -> tuple[int, int]:
    """설치 모드의 Shapeless 표시 용어 충돌을 센다."""
    output_root = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
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
    if source_rows != 15 or len(conflicts) != 8:
        errors.append(
            f"Shapeless 교차 검수 범위 변경: 원문={source_rows}, 충돌={conflicts}"
        )
    if "modonomicon:tooltip.modonomicon.recipe.crafting_shapeless" in conflicts:
        errors.append("Modonomicon Shapeless 용어 충돌이 남아 있습니다")
    return source_rows, len(conflicts)


def verify(instance: Path, pre_apply: bool = False) -> dict[str, object]:
    """현재 설치본과 프로젝트 산출물을 전수 검증한다."""
    errors: list[str] = []
    jar_matches = sorted((instance / "mods").glob("modonomicon-*.jar"))
    if [path.name for path in jar_matches] != [EXPECTED_JAR]:
        raise RuntimeError(
            f"Modonomicon JAR 범위 변경: {[path.name for path in jar_matches]}"
        )
    jar_path = jar_matches[0]
    jar_sha256 = hashlib.sha256(jar_path.read_bytes()).hexdigest()
    if jar_sha256 != EXPECTED_JAR_SHA256:
        errors.append(f"Modonomicon JAR SHA-256 변경: {jar_sha256}")

    with ZipFile(jar_path) as archive:
        names = archive.namelist()
        english = load_json_bytes(
            archive.read("assets/modonomicon/lang/en_us.json"), "Modonomicon en_us"
        )
        language_files = [
            name
            for name in names
            if re.fullmatch(r"assets/modonomicon/lang/[^/]+\.json", name)
        ]
        class_files = {
            name: archive.read(name) for name in names if name.endswith(".class")
        }
        class_referenced = {
            key
            for key in english
            if any(key.encode() in raw for raw in class_files.values())
        }
        sounds = load_json_bytes(
            archive.read("assets/modonomicon/sounds.json"), "Modonomicon sounds"
        )
        core_book_files = [
            name
            for name in names
            if "/modonomicon/books/" in name and name.endswith(".json")
        ]
        advancement_files = [
            name for name in names if "/advancement" in name and name.endswith(".json")
        ]
        recipe_files = [
            name for name in names if "/recipe" in name and name.endswith(".json")
        ]

    if len(names) != 572 or len(class_files) != 411:
        errors.append(
            f"Modonomicon JAR 구성 변경: 항목={len(names)}, 클래스={len(class_files)}"
        )
    if len(english) != 215 or any(
        not isinstance(value, str) for value in english.values()
    ):
        errors.append(f"Modonomicon 영어 언어 범위 변경: {len(english)}")
    if (
        len(language_files) != 4
        or "assets/modonomicon/lang/ko_kr.json" in language_files
    ):
        errors.append(f"Modonomicon 내장 언어 파일 범위 변경: {language_files}")

    display_english = {
        key: value for key, value in english.items() if key.startswith(DISPLAY_PREFIXES)
    }
    excluded = set(english) - set(display_english)
    demo_excluded = {key for key in excluded if key.startswith("book.modonomicon.demo")}
    if (
        len(display_english) != 78
        or len(demo_excluded) != 134
        or excluded - demo_excluded != EXPECTED_NON_DEMO_EXCLUDED
    ):
        errors.append(
            "Modonomicon 공통 표시·데모 키 범위 변경: "
            f"표시={len(display_english)}, 데모={len(demo_excluded)}, "
            f"기타={sorted(excluded - demo_excluded)}"
        )
    if len(class_referenced) != 74:
        errors.append(f"Modonomicon 클래스 참조 언어 키 변경: {len(class_referenced)}")
    if set(display_english) - class_referenced != EXPECTED_CLASS_UNREFERENCED:
        errors.append("Modonomicon 동적·설정 언어 키 범위가 바뀌었습니다")
    if class_referenced & excluded != {"test.test.test"}:
        errors.append(
            f"Modonomicon 제외 키 클래스 참조 변경: {class_referenced & excluded}"
        )

    client_class = class_files.get(
        "com/klikli_dev/modonomicon/ModonomiconNeo$Client.class"
    )
    config_class = class_files.get(
        "com/klikli_dev/modonomicon/config/ClientConfig$QoLCategory.class"
    )
    item_class = class_files.get(
        "com/klikli_dev/modonomicon/item/ModonomiconItem.class"
    )
    if not client_class or not all(
        marker in client_class
        for marker in (b"IConfigScreenFactory", b"ConfigurationScreen")
    ):
        errors.append("Modonomicon NeoForge 설정 화면 등록 경로가 바뀌었습니다")
    config_comments = (
        b"Quality of Life Settings",
        b"Enable smooth zoom in book categories",
        b"Enable keeping the last open page stored when closing an entry.",
        b"If your locale is not supported by the default Modonomicon font",
    )
    if not config_class or not all(
        marker in config_class for marker in config_comments
    ):
        errors.append("Modonomicon 설정 주석 표시 경로가 바뀌었습니다")
    if not item_class or b"Book ID: " not in item_class:
        errors.append("Modonomicon 고급 툴팁의 하드코딩 Book ID 경로가 바뀌었습니다")
    expected_sounds = {
        "turn_page": {
            "category": "player",
            "sounds": ["modonomicon:turn_page"],
            "subtitle": "modonomicon.subtitle.turn_page",
        }
    }
    if sounds != expected_sounds:
        errors.append("Modonomicon 소리 자막 경로가 바뀌었습니다")
    if core_book_files or advancement_files or recipe_files:
        errors.append(
            "Modonomicon 본체 데이터 범위 변경: "
            f"책={core_book_files}, 발전={advancement_files}, 제작법={recipe_files}"
        )

    fallbacks = load_json_path(FALLBACKS)
    overrides = load_json_path(OVERRIDES)
    working = load_json_path(WORKING)
    output = load_json_path(OUTPUT)
    expected_output = {**display_english, **EXPECTED_FALLBACKS}
    if fallbacks != EXPECTED_FALLBACKS:
        errors.append(f"Modonomicon 설정 화면 보완값 변경: {fallbacks}")
    if overrides != EXPECTED_OVERRIDES:
        errors.append(f"Modonomicon 재검수 교정 목록 변경: {overrides}")
    errors.extend(validate_language(display_english, dict(list(working.items())[:78])))
    errors.extend(validate_language(display_english, dict(list(output.items())[:78])))
    if list(working) != list(expected_output) or list(output) != list(expected_output):
        errors.append("Modonomicon 최종 키 또는 순서가 원문·설정 보완 범위와 다릅니다")
    if working != output:
        errors.append("Modonomicon working과 output 언어 파일이 다릅니다")
    for key, value in {**EXPECTED_OVERRIDES, **EXPECTED_FALLBACKS}.items():
        if output.get(key) != value:
            errors.append(f"Modonomicon 교정·보완값 불일치: {key}")
    if OUTPUT.read_bytes().startswith(b"\xef\xbb\xbf"):
        errors.append("Modonomicon 산출물에 UTF-8 BOM이 있습니다")
    output_text = OUTPUT.read_text(encoding="utf-8")
    for forbidden in ("읽음으로 표시", "사용처", "엔티티", "%s mb"):
        if forbidden in output_text:
            errors.append(f"Modonomicon 보류된 충돌 용어가 남아 있습니다: {forbidden}")

    config_path = instance / "config/modonomicon-client.toml"
    config_bytes = config_path.read_bytes()
    config_text = config_bytes.decode("utf-8-sig")
    config_options = {
        match.group(1)
        for line in config_text.splitlines()
        if (match := re.match(r"\s*([A-Za-z0-9_]+)\s*=", line))
    }
    config_sections = {
        match.group(1)
        for line in config_text.splitlines()
        if (match := re.fullmatch(r"\s*\[([^]]+)]\s*", line))
    }
    config_comment_lines = sum(
        line.lstrip().startswith("#") for line in config_text.splitlines()
    )
    if hashlib.sha256(config_bytes).hexdigest() != EXPECTED_CONFIG_SHA256:
        errors.append("Modonomicon 실제 클라이언트 설정 파일이 바뀌었습니다")
    if (
        config_options != EXPECTED_CONFIG_OPTIONS
        or config_sections != {"qol"}
        or config_comment_lines != 4
    ):
        errors.append(
            "Modonomicon 설정 범위 변경: "
            f"옵션={config_options}, 구역={config_sections}, 주석={config_comment_lines}"
        )

    providers = scan_provider_guides(instance, errors)
    quest_files = sorted((instance / "config/ftbquests/quests").rglob("*.snbt"))
    quest_references = []
    for path in quest_files:
        if re.search(r"(?i)modonomicon", path.read_text(encoding="utf-8-sig")):
            quest_references.append(path.relative_to(instance).as_posix())
    if len(quest_files) != 142 or quest_references:
        errors.append(f"Modonomicon FTB Quests 참조 범위 변경: {quest_references}")

    kube_files = []
    kube_references = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in KUBE_EXTENSIONS:
            continue
        kube_files.append(path)
        if re.search(r"(?i)modonomicon", path.read_text(encoding="utf-8-sig")):
            kube_references.append(path.relative_to(instance).as_posix())
    if len(kube_files) != 1020 or kube_references:
        errors.append(f"Modonomicon KubeJS 참조 범위 변경: {kube_references}")

    language_paths = sorted(
        (PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets").glob(
            "*/lang/ko_kr.json"
        )
    )
    official_name_rows = []
    for path in language_paths:
        for key, value in load_json_path(path).items():
            if key.startswith(("item.", "block.")) and value == "Modonomicon":
                official_name_rows.append(f"{path.parent.parent.name}:{key}")
    if len(language_paths) != 285:
        errors.append(f"프로젝트 언어 파일 수 변경: {len(language_paths)}")
    if official_name_rows != ["modonomicon:item.modonomicon.modonomicon"]:
        errors.append(f"Modonomicon 아이템명 충돌 발견: {official_name_rows}")
    shapeless_rows, shapeless_conflicts = scan_shapeless_terms(instance, errors)

    glossary_text = GLOSSARY.read_text(encoding="utf-8")
    for row in GLOSSARY_ROWS:
        if row not in glossary_text:
            errors.append(f"Modonomicon 용어집 행 누락: {row}")

    output_sha256 = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    if not pre_apply:
        report = load_json_path(REPORT)
        if report.get("validation") != "passed":
            errors.append("Modonomicon 재검수 보고서 상태가 passed가 아닙니다")
        language_review = report.get("language_review")
        if (
            not isinstance(language_review, dict)
            or language_review.get("project_candidates_corrected")
            != len(EXPECTED_OVERRIDES)
            or language_review.get("new_display_fallbacks") != len(EXPECTED_FALLBACKS)
        ):
            errors.append("Modonomicon 재검수 보고서 번역 집계 불일치")
        application = report.get("application")
        if (
            not isinstance(application, dict)
            or application.get("status") != "applied_and_verified"
            or application.get("sha256") != output_sha256
            or application.get("unexpected_changes") != 0
        ):
            errors.append("Modonomicon 재검수 보고서 게임 적용 집계 불일치")

    if errors:
        raise RuntimeError("Modonomicon 재검수 검증 실패:\n" + "\n".join(errors[:50]))
    return {
        "scope": "Modonomicon 전체 번역 재검수",
        "source_jar": jar_path.name,
        "source_jar_sha256": jar_sha256,
        "source_jar_bytes": jar_path.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(class_files),
        "source_keys_reviewed": len(english),
        "common_display_keys_reviewed": len(display_english),
        "excluded_demo_keys_reviewed": len(demo_excluded),
        "excluded_other_source_keys_reviewed": len(excluded - demo_excluded),
        "bundled_korean_candidates_reviewed": 0,
        "project_candidates_retained": len(display_english) - len(EXPECTED_OVERRIDES),
        "project_candidates_corrected": len(EXPECTED_OVERRIDES),
        "new_display_fallbacks": len(EXPECTED_FALLBACKS),
        "effective_output_keys": len(output),
        "class_referenced_language_keys": len(class_referenced),
        "sound_subtitle_keys_reviewed": 1,
        "client_config_options_reviewed": len(config_options),
        "client_config_comment_lines_reviewed": config_comment_lines,
        "hardcoded_advanced_tooltips_deferred": 1,
        "provider_jars_reviewed": len(providers),
        "provider_book_files_inventoried": sum(
            values["book_files"] for values in providers.values()
        ),
        "provider_translation_keys_inventoried": sum(
            values["translation_keys"] for values in providers.values()
        ),
        "provider_project_korean_present": sum(
            values["project_korean"] for values in providers.values()
        ),
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_reference_files": len(quest_references),
        "kubejs_files_reviewed": len(kube_files),
        "kubejs_reference_files": len(kube_references),
        "project_language_files_reviewed": len(language_paths),
        "harmful_modonomicon_name_collisions": 0,
        "cross_mod_shapeless_rows_reviewed": shapeless_rows,
        "remaining_shapeless_conflicts_deferred": shapeless_conflicts,
        "core_advancement_files": len(advancement_files),
        "core_recipe_files": len(recipe_files),
        "core_modonomicon_book_files": len(core_book_files),
        "glossary_terms_added": len(GLOSSARY_ROWS),
        "output_sha256": output_sha256,
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
