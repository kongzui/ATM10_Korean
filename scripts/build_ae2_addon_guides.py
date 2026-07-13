#!/usr/bin/env python3
"""AE2 연동 모드 GuideME 가이드의 현재 배치를 검증해 리소스팩에 만든다."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import zipfile
from pathlib import Path, PurePosixPath

import build_ae2_guide as core
from local_paths import resolve_source_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCEPACK_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean"
ADDON_WORKING_ROOT = PROJECT_ROOT / "working/ae2_addons/ae2wtlib"
GUIDE_WORKING_ROOT = ADDON_WORKING_ROOT / "ae2guide/_ko_kr"
LANG_WORKING_FILE = ADDON_WORKING_ROOT / "lang/ko_kr.json"
CORE_COMPAT_WORKING_FILE = (
    PROJECT_ROOT
    / "working/ae2/ae2guide/_ko_kr/items-blocks-machines/wireless_terminals.md"
)
PROGRESS_FILE = PROJECT_ROOT / "working/ae2_addons/guide_progress.json"

ACTIVE_BATCH = 1
ADDON_GUIDE_FILES = (
    "ae2wtlib/ae2wtlib-index.md",
    "ae2wtlib/magnet_card.md",
    "ae2wtlib/quantum_bridge_card.md",
    "ae2wtlib/restock.md",
    "ae2wtlib/wireless_crafting_terminal.md",
    "ae2wtlib/wireless_terminals.md",
    "ae2wtlib/wireless_universal_terminal.md",
)
CORE_COMPAT_RELATIVE = "items-blocks-machines/wireless_terminals.md"
LANG_RELATIVE = "assets/ae2wtlib/lang/ko_kr.json"
GUIDE_OUTPUT_ROOT = RESOURCEPACK_ROOT / "assets/ae2wtlib/ae2guide/_ko_kr"
CORE_COMPAT_OUTPUT_FILE = (
    RESOURCEPACK_ROOT
    / "assets/ae2/ae2guide/_ko_kr/items-blocks-machines/wireless_terminals.md"
)
LANG_OUTPUT_FILE = RESOURCEPACK_ROOT / LANG_RELATIVE

GUIDE_SOURCE_ROOTS = {
    "ae2": PurePosixPath("assets/ae2/ae2guide"),
    "ae2wtlib": PurePosixPath("assets/ae2wtlib/ae2guide"),
}
GUIDE_ITEM_NAMES = {
    "item.ae2wtlib.magnet_card": "ae2wtlib/magnet_card.md",
    "item.ae2wtlib.quantum_bridge_card": "ae2wtlib/quantum_bridge_card.md",
    "item.ae2wtlib.wireless_pattern_encoding_terminal": (
        "ae2wtlib/wireless_terminals.md"
    ),
    "item.ae2wtlib.wireless_pattern_access_terminal": (
        "ae2wtlib/wireless_terminals.md"
    ),
    "item.ae2wtlib.wireless_universal_terminal": (
        "ae2wtlib/wireless_universal_terminal.md"
    ),
}
PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{\d+\}")
FORMAT_CODE_RE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
TAG_TOKEN_RE = re.compile(r"<(/?)([A-Za-z][\w:]*)\b[^>]*>")
ITEM_TAG_RE = re.compile(
    r'<(?:ItemLink|ItemImage|ItemIcon|BlockImage)\b[^>]*\bid="([^"]+)"'
)
RECIPE_FOR_RE = re.compile(r'<RecipeFor\b[^>]*\bid="([^"]+)"')
RECIPE_RE = re.compile(r'<Recipe\b[^>]*\bid="([^"]+)"')
VOID_TAGS = {"br", "hr", "img", "input", "meta", "link"}


def find_single_jar(instance: Path, pattern: str, label: str) -> Path:
    jars = sorted((instance / "mods").glob(pattern))
    if len(jars) != 1:
        raise ValueError(
            f"{label} JAR을 하나로 확정할 수 없습니다: {[p.name for p in jars]}"
        )
    return jars[0]


def find_jars(instance: Path) -> dict[str, Path]:
    return {
        "ae2": find_single_jar(instance, "appliedenergistics2-*.jar", "AE2"),
        "ae2wtlib": find_single_jar(instance, "ae2wtlib-*.jar", "AE2WTLib"),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json_unique(path: Path) -> dict[str, str]:
    duplicates: list[str] = []

    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        return result

    raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    if duplicates:
        raise ValueError(f"중복 언어 키가 있습니다: {sorted(set(duplicates))}")
    if not isinstance(raw, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in raw.items()
    ):
        raise ValueError(f"언어 파일은 문자열 키와 값만 가져야 합니다: {path}")
    return raw


def load_archive_json_unique(archive: zipfile.ZipFile, entry: str) -> dict[str, str]:
    duplicates: list[str] = []

    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        return result

    raw = json.loads(
        archive.read(entry).decode("utf-8-sig"), object_pairs_hook=unique_object
    )
    if duplicates:
        raise ValueError(f"{entry}: 중복 언어 키가 있습니다: {sorted(set(duplicates))}")
    if not isinstance(raw, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in raw.items()
    ):
        raise ValueError(f"{entry}: 문자열 키와 값만 가져야 합니다.")
    return raw


def validate_language(source: dict[str, str], translated: dict[str, str]) -> list[str]:
    errors = []
    source_keys = set(source)
    translated_keys = set(translated)
    if source_keys != translated_keys:
        errors.append(
            "AE2WTLib 언어 키가 다릅니다: "
            f"누락={sorted(source_keys - translated_keys)}, "
            f"불필요={sorted(translated_keys - source_keys)}"
        )
    for key in sorted(source_keys & translated_keys):
        expected = PLACEHOLDER_RE.findall(source[key])
        actual = PLACEHOLDER_RE.findall(translated[key])
        if expected != actual:
            errors.append(f"{key}: 자리표시자가 다릅니다: {expected} != {actual}")
        if source[key].count("\n") != translated[key].count("\n"):
            errors.append(f"{key}: 줄바꿈 수가 다릅니다.")
        if FORMAT_CODE_RE.findall(source[key]) != FORMAT_CODE_RE.findall(
            translated[key]
        ):
            errors.append(f"{key}: 서식 코드가 다릅니다.")
    return errors


def validate_tag_nesting(relative: str, text: str) -> list[str]:
    errors = []
    stack: list[str] = []
    protected_text = core.INLINE_CODE_RE.sub("", text)
    for match in TAG_TOKEN_RE.finditer(protected_text):
        closing, name = match.groups()
        if match.group(0).endswith("/>") or name.lower() in VOID_TAGS:
            continue
        if closing:
            if not stack or stack[-1] != name:
                errors.append(f"{relative}: 태그 닫힘 순서가 잘못됐습니다: {name}")
                continue
            stack.pop()
        else:
            stack.append(name)
    if stack:
        errors.append(f"{relative}: 닫히지 않은 태그가 있습니다: {stack}")
    return errors


def resolve_guide_reference(namespace: str, page: str, target: str) -> str | None:
    clean = target.split("#", 1)[0].split("?", 1)[0]
    if not clean or re.match(r"^(?:https?://|mailto:)", clean):
        return None
    namespace_match = re.match(r"^([a-z0-9_.-]+):(.*)$", clean)
    if namespace_match:
        target_namespace, target_path = namespace_match.groups()
        root = GUIDE_SOURCE_ROOTS.get(target_namespace)
        if root is None:
            return None
        return posixpath.normpath((root / target_path).as_posix())
    root = GUIDE_SOURCE_ROOTS[namespace]
    return posixpath.normpath((root / PurePosixPath(page).parent / clean).as_posix())


def split_resource_id(value: str, default_namespace: str) -> tuple[str, str]:
    if ":" in value:
        return tuple(value.split(":", 1))  # type: ignore[return-value]
    return default_namespace, value


def item_resource_exists(
    archive_names: dict[str, set[str]], default_namespace: str, value: str
) -> bool:
    namespace, path = split_resource_id(value, default_namespace)
    if namespace not in archive_names:
        return True
    names = archive_names.get(namespace, set())
    candidates = (
        f"assets/{namespace}/models/item/{path}.json",
        f"assets/{namespace}/items/{path}.json",
        f"assets/{namespace}/models/block/{path}.json",
    )
    return any(candidate in names for candidate in candidates)


def recipe_resource_exists(
    archive_names: dict[str, set[str]], default_namespace: str, value: str
) -> bool:
    namespace, path = split_resource_id(value, default_namespace)
    if namespace not in archive_names:
        return True
    names = archive_names.get(namespace, set())
    return (
        f"data/{namespace}/recipe/{path}.json" in names
        or f"data/{namespace}/recipes/{path}.json" in names
    )


def validate_resources(
    archive_names: dict[str, set[str]], namespace: str, relative: str, text: str
) -> list[str]:
    errors = []
    targets = [
        *(match.group(1) for match in core.LINK_TARGET_RE.finditer(text)),
        *(match.group(1) for match in core.IMAGE_TARGET_RE.finditer(text)),
        *(match.group(1) for match in core.IMPORT_RE.finditer(text)),
    ]
    all_names = set().union(*archive_names.values())
    for target in targets:
        resolved = resolve_guide_reference(namespace, relative, target)
        if resolved and resolved not in all_names:
            errors.append(f"{relative}: 참조 대상이 없습니다: {target} -> {resolved}")
    for item_id in ITEM_TAG_RE.findall(text):
        if not item_resource_exists(archive_names, namespace, item_id):
            errors.append(
                f"{relative}: 아이템 또는 블록 ID를 찾을 수 없습니다: {item_id}"
            )
    for item_id in RECIPE_FOR_RE.findall(text):
        if not item_resource_exists(archive_names, namespace, item_id):
            errors.append(
                f"{relative}: RecipeFor 아이템 ID를 찾을 수 없습니다: {item_id}"
            )
    for recipe_id in RECIPE_RE.findall(text):
        if not recipe_resource_exists(archive_names, namespace, recipe_id):
            errors.append(f"{relative}: 조합법 ID를 찾을 수 없습니다: {recipe_id}")
    return errors


def guide_source(
    archives: dict[str, zipfile.ZipFile], namespace: str, relative: str
) -> str:
    entry = (GUIDE_SOURCE_ROOTS[namespace] / relative).as_posix()
    source_archive = archives["ae2wtlib"]
    return source_archive.read(entry).decode("utf-8-sig")


def guide_working_path(namespace: str, relative: str) -> Path:
    if namespace == "ae2":
        return CORE_COMPAT_WORKING_FILE
    return GUIDE_WORKING_ROOT / relative


def guide_output_path(namespace: str, relative: str) -> Path:
    if namespace == "ae2":
        return CORE_COMPAT_OUTPUT_FILE
    return GUIDE_OUTPUT_ROOT / relative


def validate(instance: Path, compare_output: bool) -> dict[str, object]:
    jars = find_jars(instance)
    errors = []
    expected_working = set(ADDON_GUIDE_FILES)
    actual_working = {
        path.relative_to(GUIDE_WORKING_ROOT).as_posix()
        for path in GUIDE_WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if actual_working != expected_working:
        errors.append(
            "AE2WTLib 작업본 목록이 다릅니다: "
            f"누락={sorted(expected_working - actual_working)}, "
            f"불필요={sorted(actual_working - expected_working)}"
        )

    if not LANG_WORKING_FILE.is_file():
        errors.append(f"AE2WTLib 언어 작업본이 없습니다: {LANG_WORKING_FILE}")

    archive_handles = {
        namespace: zipfile.ZipFile(path) for namespace, path in jars.items()
    }
    try:
        archive_names = {
            namespace: set(archive.namelist())
            for namespace, archive in archive_handles.items()
        }
        source_lang = load_archive_json_unique(
            archive_handles["ae2wtlib"], "assets/ae2wtlib/lang/en_us.json"
        )
        candidate_lang = load_archive_json_unique(
            archive_handles["ae2wtlib"], "assets/ae2wtlib/lang/ko_kr.json"
        )
        translated_lang = load_json_unique(LANG_WORKING_FILE)
        errors.extend(validate_language(source_lang, translated_lang))

        guide_rows = [("ae2", CORE_COMPAT_RELATIVE)]
        guide_rows.extend(("ae2wtlib", relative) for relative in ADDON_GUIDE_FILES)
        source_words = 0
        for namespace, relative in guide_rows:
            source = guide_source(archive_handles, namespace, relative)
            working_path = guide_working_path(namespace, relative)
            if not working_path.is_file():
                errors.append(f"가이드 작업본이 없습니다: {working_path}")
                continue
            translated = working_path.read_text(encoding="utf-8")
            pair_errors = core.validate_pair(relative, source, translated)
            if relative == "ae2wtlib/ae2wtlib-index.md":
                pair_errors = [
                    error
                    for error in pair_errors
                    if "한국어 본문을 찾을 수 없습니다" not in error
                ]
            errors.extend(pair_errors)
            errors.extend(validate_tag_nesting(relative, translated))
            errors.extend(
                validate_resources(archive_names, namespace, relative, translated)
            )
            source_words += len(
                core.ENGLISH_WORD_RE.findall(core.extract_visible_text(source))
            )
            if working_path.read_bytes().startswith(b"\xef\xbb\xbf"):
                errors.append(f"{working_path}: UTF-8 BOM이 있습니다.")

            if compare_output:
                output_path = guide_output_path(namespace, relative)
                if not output_path.is_file():
                    errors.append(f"가이드 출력 파일이 없습니다: {output_path}")
                elif working_path.read_bytes() != output_path.read_bytes():
                    errors.append(f"{relative}: 작업본과 출력이 다릅니다.")

        for key, relative in GUIDE_ITEM_NAMES.items():
            if key not in translated_lang:
                continue
            text = (GUIDE_WORKING_ROOT / relative).read_text(encoding="utf-8")
            if translated_lang[key] not in core.extract_visible_text(text):
                errors.append(
                    f"{relative}: 언어 파일의 아이템명이 가이드에 없습니다: "
                    f"{translated_lang[key]}"
                )

        if compare_output:
            output_files = {
                path.relative_to(GUIDE_OUTPUT_ROOT).as_posix()
                for path in GUIDE_OUTPUT_ROOT.rglob("*.md")
                if path.is_file()
            }
            if output_files != expected_working:
                errors.append(
                    "AE2WTLib 출력 목록이 다릅니다: "
                    f"누락={sorted(expected_working - output_files)}, "
                    f"불필요={sorted(output_files - expected_working)}"
                )
            if not LANG_OUTPUT_FILE.is_file():
                errors.append(f"AE2WTLib 언어 출력 파일이 없습니다: {LANG_OUTPUT_FILE}")
            elif LANG_WORKING_FILE.read_bytes() != LANG_OUTPUT_FILE.read_bytes():
                errors.append("AE2WTLib 언어 작업본과 출력이 다릅니다.")

        reused = sum(
            1
            for key, value in translated_lang.items()
            if candidate_lang.get(key) == value
        )
        return {
            "jars": jars,
            "source_words": source_words,
            "source_lang": source_lang,
            "candidate_lang": candidate_lang,
            "translated_lang": translated_lang,
            "existing_korean_reused": reused,
            "new_or_revised_translations": len(translated_lang) - reused,
            "errors": errors,
        }
    finally:
        for archive in archive_handles.values():
            archive.close()


def build(instance: Path) -> dict[str, object]:
    validation = validate(instance, compare_output=False)
    errors = validation["errors"]
    assert isinstance(errors, list)
    if errors:
        raise ValueError("\n".join(errors))

    for relative in ADDON_GUIDE_FILES:
        source = GUIDE_WORKING_ROOT / relative
        target = GUIDE_OUTPUT_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    CORE_COMPAT_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CORE_COMPAT_OUTPUT_FILE.write_bytes(CORE_COMPAT_WORKING_FILE.read_bytes())
    LANG_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    LANG_OUTPUT_FILE.write_bytes(LANG_WORKING_FILE.read_bytes())

    post_validation = validate(instance, compare_output=True)
    post_errors = post_validation["errors"]
    assert isinstance(post_errors, list)
    if post_errors:
        raise ValueError("\n".join(post_errors))

    jars = validation["jars"]
    assert isinstance(jars, dict)
    output_files = {
        "assets/ae2/ae2guide/_ko_kr/" + CORE_COMPAT_RELATIVE: sha256(
            CORE_COMPAT_OUTPUT_FILE
        ),
        LANG_RELATIVE: sha256(LANG_OUTPUT_FILE),
    }
    output_files.update(
        {
            "assets/ae2wtlib/ae2guide/_ko_kr/" + relative: sha256(
                GUIDE_OUTPUT_ROOT / relative
            )
            for relative in ADDON_GUIDE_FILES
        }
    )
    result = {
        "status": "batch_01_completed",
        "scope": "AE2WTLib GuideME guide batch 01",
        "batch": ACTIVE_BATCH,
        "source_jars": {
            namespace: {"name": path.name, "sha256": sha256(path)}
            for namespace, path in jars.items()
        },
        "language": "ko_kr",
        "guide_pages": 8,
        "new_guide_pages": 7,
        "core_compatibility_updates": 1,
        "source_words": validation["source_words"],
        "language_keys": len(validation["translated_lang"]),
        "existing_korean_reused": validation["existing_korean_reused"],
        "new_or_revised_translations": validation["new_or_revised_translations"],
        "guide_files": list(ADDON_GUIDE_FILES),
        "core_compatibility_file": CORE_COMPAT_RELATIVE,
        "output_sha256": output_files,
        "ftbquests_review": {
            "related_chapter_found": True,
            "terminology_mismatch_found": True,
            "mismatch": "유니버설 무선 터미널 -> 무선 범용 터미널",
            "keys_updated": 3,
            "handled_separately": True,
        },
        "kubejs_user_visible_literals_found": 0,
        "validation_errors": 0,
    }
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    result = build(resolve_source_root(args.instance))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
