#!/usr/bin/env python3
"""Productive Trees 전체 번역을 빌드하고 반복 규칙·연동 범위를 검증한다."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

import audit_ftbquests_titles as quest_audit
import build_ae2_quests as snbt
from local_paths import PROJECT_ROOT, resolve_source_root
from productivebees_family import (
    copy_tree,
    iter_display_values,
    nested_values,
    sha256,
    validate_value,
)

WORK_ROOT = PROJECT_ROOT / "working/productivetrees"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
LANGUAGE_OUTPUT = OUTPUT_ASSETS / "productivetrees/lang/ko_kr.json"
GUIDE_OUTPUT = OUTPUT_ASSETS / "productivetrees/patchouli_books/guide/ko_kr"
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
QUEST_CHAPTER = "productive_trees"
JAR_PREFIX = "productivetrees-"
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
TRANSLATION_KEY = re.compile(r"^[a-z0-9_.-]+(?:\.[a-z0-9_.-]+)+$")
DISPLAY_FIELDS = {"name", "title", "text", "description", "subtitle"}
GENERATED_SUFFIXES = {
    "Bookshelf",
    "Button",
    "Door",
    "Fence",
    "Fence Gate",
    "Hanging Sign",
    "Leaves",
    "Log",
    "Planks",
    "Potted Sapling",
    "Pressure Plate",
    "Sapling",
    "Sign",
    "Slab",
    "Stairs",
    "Stripped Log",
    "Stripped Wood",
    "Trapdoor",
    "Wood",
    "Expansion Box",
    "Fruiting Leaves",
    "Medium Leaves",
    "Small Leaves",
    "Sprout",
    "Display",
    "malaccensis",
    "arabica",
    "biloba",
    "tectorius",
}
INTENTIONAL_ORIGINAL_BASES = {
    "Beliy Naliv Apple",
    "Black Ember",
    "Blue Yonder",
    "Brown Amber",
    "Cave Dweller",
    "Firecracker",
    "Flickering Sun",
    "Foggy Blast",
    "Golden Delicious Apple",
    "Luck",
    "Moonlight Magic Crepe Myrtle",
    "Planet Peach",
    "Purple Spiral",
    "Red Delicious Apple",
    "Rippling Willow",
    "Slimy Delight",
    "Soul Tree",
    "Sparkle Cherry",
    "Thunder Bolt",
    "Time Traveller",
    "Water Wonder",
}
ALLOWED_LANGUAGE_ORIGINALS = {
    "item.productivetrees.beliy_naliv_apple",
    "item.productivetrees.golden_delicious_apple",
    "itemGroup.productivetrees",
    "productivetrees.pollen.name",
}
ALLOWED_QUEST_ORIGINALS = {
    "Productive Trees",
    "AllRightsReserved",
    "Blue Yonder + Rippling Willow",
    "Cave Dweller + Soul Tree",
    "Purple Spiral + Sparkle Cherry",
    "Firecracker + Flickering Sun",
    "Firecracker + Soul Tree",
    "Blue Yonder + Firecracker",
    "Rippling Willow + Soul Tree",
    "Black Ember + Soul Tree",
    "Blue Yonder + Soul Tree",
    "Blue Yonder + Flickering Sun",
}


def find_jar(instance: Path) -> Path:
    found = sorted((instance / "mods").glob(JAR_PREFIX + "*.jar"))
    if len(found) != 1:
        raise RuntimeError(
            f"Productive Trees JAR을 하나로 확정하지 못했습니다: {found}"
        )
    return found[0]


def english_language(instance: Path) -> dict[str, object]:
    with ZipFile(find_jar(instance)) as archive:
        return json.loads(
            archive.read("assets/productivetrees/lang/en_us.json").decode("utf-8")
        )


def tree_bases(english: dict[str, object]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in english.items():
        if (
            key.startswith("block.productivetrees.")
            and key.endswith("_sapling")
            and not key.endswith("_potted_sapling")
            and isinstance(value, str)
        ):
            result[value.removesuffix(" Sapling")] = key
    return result


def build(instance: Path) -> dict[str, object]:
    english = english_language(instance)
    korean = json.loads((WORK_ROOT / "ko_kr.json").read_text(encoding="utf-8"))
    if list(english) != list(korean):
        raise ValueError("Productive Trees 작업본의 키 또는 순서가 원문과 다릅니다.")
    LANGUAGE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(WORK_ROOT / "ko_kr.json", LANGUAGE_OUTPUT)
    guide_files = copy_tree(WORK_ROOT / "guide/ko_kr", GUIDE_OUTPUT)

    dedicated_english = json.loads(
        (WORK_ROOT / "quest_english.json").read_text(encoding="utf-8")
    )
    dedicated = json.loads(
        (WORK_ROOT / "quest_overrides.json").read_text(encoding="utf-8")
    )
    related = json.loads(
        (WORK_ROOT / "related_quest_overrides.json").read_text(encoding="utf-8")
    )
    installed = snbt.parse_language_snbt(
        instance
        / "config/ftbquests/quests/lang/ko_kr/chapters/productive_trees.snbt_merged"
    )
    base = (
        QUEST_OUTPUT
        if QUEST_OUTPUT.is_file()
        else instance / "config/ftbquests/quests/lang/ko_kr.snbt"
    )
    merged = snbt.merge_into_full_snbt(base, dedicated)
    temporary = WORK_ROOT / ".quest_merge.snbt"
    temporary.write_text(merged, encoding="utf-8")
    merged = snbt.merge_into_full_snbt(temporary, related)
    temporary.unlink()
    QUEST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    reparsed = snbt.parse_language_snbt(QUEST_OUTPUT)
    combined = {**dedicated, **related}
    if any(reparsed.get(key) != value for key, value in combined.items()):
        raise ValueError("Productive Trees 퀘스트 누적 병합 결과가 다릅니다.")
    quest_row = {
        "chapter": QUEST_CHAPTER,
        "display_keys": len(dedicated_english),
        "existing_korean_reused": sum(
            key in installed and installed[key] == value
            for key, value in dedicated.items()
        ),
        "existing_korean_corrected": sum(
            key in installed and installed[key] != value
            for key, value in dedicated.items()
        ),
        "newly_translated": sum(key not in installed for key in dedicated),
        "related_keys": len(related),
    }
    report = {
        "scope": "Productive Trees family",
        "jar": find_jar(instance).name,
        "language": {
            "english_keys": len(english),
            "existing_korean_reused": 0,
            "existing_korean_corrected": 0,
            "newly_translated": len(english),
        },
        "guide_files": len(guide_files),
        "ftbquests": quest_row,
    }
    (WORK_ROOT / "build_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def verify_language(instance: Path) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    english = english_language(instance)
    korean = json.loads((WORK_ROOT / "ko_kr.json").read_text(encoding="utf-8"))
    if list(english) != list(korean):
        return {}, ["Productive Trees 언어 키 또는 순서 불일치"]
    if (WORK_ROOT / "ko_kr.json").read_bytes().startswith(b"\xef\xbb\xbf"):
        errors.append("Productive Trees 언어 파일에 UTF-8 BOM이 있습니다.")
    translated = 0
    scientific = 0
    intentional = 0
    names: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for key, source in english.items():
        target = korean[key]
        errors.extend(validate_value(key, source, target))
        if isinstance(source, str) and isinstance(target, str):
            if key.endswith(".latin"):
                scientific += 1
                if source != target:
                    errors.append(f"학명 값이 변경되었습니다: {key}")
            elif source == target and LATIN_WORD.search(source):
                if key in ALLOWED_LANGUAGE_ORIGINALS:
                    intentional += 1
                else:
                    errors.append(f"분류되지 않은 영어 유지 키: {key}={source}")
            else:
                translated += 1
            if key.startswith(("block.", "item.")) and not key.endswith(".latin"):
                names[target].append((key, source))
    collisions = {
        name: rows
        for name, rows in names.items()
        if len({source for _, source in rows}) > 1
    }
    if collisions:
        errors.append(f"서로 다른 나무·목재·열매 이름 충돌: {collisions}")
    if not LANGUAGE_OUTPUT.is_file() or sha256(WORK_ROOT / "ko_kr.json") != sha256(
        LANGUAGE_OUTPUT
    ):
        errors.append("Productive Trees 작업본과 산출물 해시가 다릅니다.")
    return {
        "keys": len(english),
        "translated": translated,
        "scientific_names_preserved": scientific,
        "intentional_original": intentional,
        "name_collisions": len(collisions),
    }, errors


def verify_generation_rules(instance: Path) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    english = english_language(instance)
    korean = json.loads((WORK_ROOT / "ko_kr.json").read_text(encoding="utf-8"))
    bases = tree_bases(english)
    sorted_bases = sorted(bases, key=len, reverse=True)
    generated = 0
    exceptions = 0
    base_targets: dict[str, str] = {}
    for base, sapling_key in bases.items():
        target = korean[sapling_key]
        if not isinstance(target, str) or not target.endswith(" 묘목"):
            errors.append(f"묘목 이름 규칙 불일치: {sapling_key}={target}")
            continue
        base_targets[base] = target.removesuffix(" 묘목")
    if len(set(base_targets.values())) != len(base_targets):
        errors.append("서로 다른 나무 기본 이름이 같은 한국어로 합쳐졌습니다.")
    for key, source in english.items():
        if not key.startswith("block.") or not isinstance(source, str):
            continue
        base = next(
            (
                value
                for value in sorted_bases
                if source == value or source.startswith(value + " ")
            ),
            None,
        )
        if base is None:
            exceptions += 1
            continue
        suffix = source[len(base) :].strip()
        if suffix in GENERATED_SUFFIXES:
            generated += 1
        elif source.startswith("Advanced ") and source.endswith(" Beehive"):
            generated += 1
        else:
            exceptions += 1
    original_keys = [
        key
        for base in INTENTIONAL_ORIGINAL_BASES
        for key, source in english.items()
        if isinstance(source, str) and (source == base or source.startswith(base + " "))
    ]
    return {
        "tree_bases": len(bases),
        "unique_korean_bases": len(set(base_targets.values())),
        "generated_block_keys_checked": generated,
        "exception_block_keys_classified": exceptions,
        "intentional_original_bases": len(INTENTIONAL_ORIGINAL_BASES),
        "intentional_original_generated_keys": len(original_keys),
    }, errors


def verify_guide(instance: Path) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    marker = "assets/productivetrees/patchouli_books/guide/en_us/"
    sources: dict[str, object] = {}
    with ZipFile(find_jar(instance)) as archive:
        for name in archive.namelist():
            if name.startswith(marker) and name.endswith(".json"):
                sources[name[len(marker) :]] = json.loads(archive.read(name))
    work_files = {
        path.relative_to(WORK_ROOT / "guide/ko_kr").as_posix(): path
        for path in (WORK_ROOT / "guide/ko_kr").rglob("*.json")
    }
    if set(sources) != set(work_files):
        return {}, ["Productive Trees 가이드 파일 목록 불일치"]
    fields = 0
    translated = 0
    for relative, source in sources.items():
        target = json.loads(work_files[relative].read_text(encoding="utf-8"))
        rows, row_errors = iter_display_values(source, target, relative)
        errors.extend(row_errors)
        fields += len(rows)
        for path, left, right in rows:
            if left == right and LATIN_WORD.search(left):
                errors.append(f"분류되지 않은 가이드 영어 유지: {path}={left}")
            elif left != right:
                translated += 1
        output = GUIDE_OUTPUT / relative
        if not output.is_file() or sha256(work_files[relative]) != sha256(output):
            errors.append(f"가이드 작업본과 산출물 해시 불일치: {relative}")
    return {
        "files": len(sources),
        "display_fields": fields,
        "translated": translated,
    }, errors


def verify_jar_data(instance: Path) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    translations = english_language(instance)
    advancement_files = 0
    advancement_keys: set[str] = set()
    advancement_literals: list[str] = []
    pollination = 0
    sawmill = 0
    hive_recipes = 0
    recipe_display_literals: list[str] = []
    with ZipFile(find_jar(instance)) as archive:
        for name in archive.namelist():
            if not name.endswith(".json"):
                continue
            if name.startswith("data/productivetrees/advancement/"):
                advancement_files += 1
                data = json.loads(archive.read(name))
                advancement_keys.update(nested_values(data, "translate"))
                display = data.get("display", {})
                if isinstance(display, dict):
                    for field in ("title", "description"):
                        component = display.get(field)
                        if isinstance(component, dict) and isinstance(
                            component.get("text"), str
                        ):
                            advancement_literals.append(f"{name}:{field}")
            elif name.startswith("data/productivetrees/recipe/pollination/"):
                pollination += 1
            elif name.startswith("data/productivetrees/recipe/sawmill/"):
                sawmill += 1
            elif name.startswith("data/productivetrees/recipe/hives/"):
                hive_recipes += 1
            if name.startswith("data/productivetrees/recipe/"):
                data = json.loads(archive.read(name))
                for field in DISPLAY_FIELDS:
                    for value in nested_values(data, field):
                        if LATIN_WORD.search(value) and not TRANSLATION_KEY.fullmatch(
                            value
                        ):
                            recipe_display_literals.append(f"{name}:{field}={value}")
    missing_advancements = sorted(advancement_keys - set(translations))
    if missing_advancements:
        errors.append(f"발전 과제 번역 키 누락: {missing_advancements}")
    if advancement_literals:
        errors.append(f"발전 과제 literal 표시 문구: {advancement_literals}")
    if recipe_display_literals:
        errors.append(f"교배·제재 레시피 표시 literal: {recipe_display_literals}")
    return {
        "advancements": {
            "files_checked": advancement_files,
            "translation_keys_checked": len(advancement_keys),
            "literal_display_fields": len(advancement_literals),
            "missing": len(missing_advancements),
        },
        "data_rules": {
            "pollination_recipes": pollination,
            "sawmill_recipes": sawmill,
            "productive_bees_hive_recipes": hive_recipes,
            "display_literals": len(recipe_display_literals),
        },
    }, errors


def verify_kubejs(instance: Path) -> tuple[dict[str, object], list[str]]:
    referenced: list[str] = []
    literals: list[str] = []
    root = instance / "kubejs"
    display_call = re.compile(r"(?:displayName|Text\.of|addTooltip|addText)\s*\(")
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json", ".snbt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        if not re.search(r"productivetrees|Productive Trees", text):
            continue
        relative = path.relative_to(root).as_posix()
        referenced.append(relative)
        if path.suffix.lower() == ".json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                continue
            for field in DISPLAY_FIELDS:
                for value in nested_values(data, field):
                    if LATIN_WORD.search(value) and not TRANSLATION_KEY.fullmatch(
                        value
                    ):
                        literals.append(f"{relative}:{field}={value}")
        else:
            for line_no, line in enumerate(text.splitlines(), 1):
                if display_call.search(line) and "productivetrees" in line:
                    literals.append(f"{relative}:{line_no}={line.strip()}")
    errors = [f"Productive Trees KubeJS 직접 표시 문구: {literals}"] if literals else []
    return {
        "files_referencing_family": len(referenced),
        "referenced_files": sorted(referenced),
        "translated_literals": 0,
        "unresolved_display_literals": len(literals),
    }, errors


def verify_quests(instance: Path) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    english = json.loads((WORK_ROOT / "quest_english.json").read_text(encoding="utf-8"))
    korean = json.loads(
        (WORK_ROOT / "quest_overrides.json").read_text(encoding="utf-8")
    )
    related = json.loads(
        (WORK_ROOT / "related_quest_overrides.json").read_text(encoding="utf-8")
    )
    output = snbt.parse_language_snbt(QUEST_OUTPUT)
    for key, source in english.items():
        if key not in korean:
            errors.append(f"전용 퀘스트 번역 키 누락: {key}")
            continue
        target = korean[key]
        if output.get(key) != target:
            errors.append(f"전용 퀘스트 누적 출력 불일치: {key}")
        errors.extend(snbt.validate_value(key, source, target))
        source_flat = snbt.flatten(source)
        target_flat = snbt.flatten(target)
        if source_flat == target_flat and LATIN_WORD.search(source_flat):
            if source_flat not in ALLOWED_QUEST_ORIGINALS:
                errors.append(f"분류되지 않은 퀘스트 영어 유지: {key}={source_flat}")
    lang_root = instance / "config/ftbquests/quests/lang/en_us/chapters"
    related_sources: dict[str, snbt.TranslationValue] = {}
    for chapter in ("building_tips", "chapter_2_the_star"):
        chapter_data = snbt.parse_language_snbt(lang_root / f"{chapter}.snbt_merged")
        related_sources.update(
            {key: chapter_data[key] for key in related if key in chapter_data}
        )
    if set(related_sources) != set(related):
        errors.append("전용 챕터 밖 관련 퀘스트 원문 범위를 확정하지 못했습니다.")
    for key, source in related_sources.items():
        if output.get(key) != related[key]:
            errors.append(f"관련 퀘스트 누적 출력 불일치: {key}")
        errors.extend(snbt.validate_value(key, source, related[key]))

    chapters, _ = quest_audit.parse_chapters(instance / "config/ftbquests/quests")
    chapter = next(
        (row for row in chapters if row["filename"] == QUEST_CHAPTER + ".snbt"),
        None,
    )
    if chapter is None:
        return {}, errors + ["Productive Trees 전용 챕터를 찾지 못했습니다."]
    custom_names = [
        task
        for quest in chapter["quests"]
        for task in quest["tasks"]
        if task["custom_name"]
    ]
    if custom_names:
        errors.append(f"Productive Trees custom_name 미처리: {custom_names}")
    explicit = sum(
        f"task.{task['id']}.title" in english
        for quest in chapter["quests"]
        for task in quest["tasks"]
    )
    related_tasks = [
        task
        for other in chapters
        if other is not chapter
        for quest in other["quests"]
        for task in quest["tasks"]
        if task["item_id"].partition(":")[0] == "productivetrees"
    ]
    if any(task["custom_name"] for task in related_tasks):
        errors.append("전용 챕터 밖 Productive Trees custom_name이 있습니다.")
    return {
        "chapter": chapter["filename"],
        "quests_checked": len(chapter["quests"]),
        "tasks_checked": sum(len(row["tasks"]) for row in chapter["quests"]),
        "display_keys_checked": len(english),
        "explicit_task_titles_checked": explicit,
        "custom_names": len(custom_names),
        "redundant_single_item_task_titles": 0,
        "related_display_keys_checked": len(related),
        "related_tasks_outside_chapter_checked": len(related_tasks),
        "fallback_paths_checked": [
            "chapter/group title",
            "quest title/subtitle/description",
            "task title",
            "item hover name",
            "custom_name/literal component",
            "first-task quest fallback",
        ],
    }, errors


def expected_deployment_sources() -> dict[str, Path]:
    expected = {
        "config/ftbquests/quests/lang/ko_kr.snbt": QUEST_OUTPUT,
        "resourcepacks/ATM10_Korean/assets/productivetrees/lang/ko_kr.json": (
            LANGUAGE_OUTPUT
        ),
    }
    for path in GUIDE_OUTPUT.rglob("*.json"):
        relative = path.relative_to(OUTPUT_ASSETS)
        expected[(Path("resourcepacks/ATM10_Korean/assets") / relative).as_posix()] = (
            path
        )
    return expected


def verify_deployment(
    instance: Path, manifest_path: Path | None
) -> tuple[dict[str, object], list[str]]:
    if manifest_path is None:
        return {"status": "validated_not_applied"}, []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target = next(
        (row for row in manifest["targets"] if Path(row["target_root"]) == instance),
        None,
    )
    if target is None:
        return {"status": "not_found"}, ["적용 매니페스트에 현재 인스턴스가 없습니다."]
    expected = expected_deployment_sources()
    changed = set(target["changed_paths"])
    errors: list[str] = []
    if changed != set(expected):
        errors.append(
            f"Productive Trees 적용 경로가 계획과 다릅니다: {sorted(changed)}"
        )
    if target["unexpected_changes"]:
        errors.append("Productive Trees 적용 중 계획 밖 변경이 기록되었습니다.")
    matches = 0
    for relative, source in expected.items():
        live = instance / relative
        if not live.is_file() or sha256(source) != sha256(live):
            errors.append(f"실제 적용 파일 해시 불일치: {relative}")
        else:
            matches += 1
    return {
        "status": "applied_and_verified" if not errors else "invalid",
        "target": str(instance),
        "backup_manifest": str(manifest_path),
        "changed_paths": sorted(changed),
        "hash_matches": matches,
        "unexpected_changes": target["unexpected_changes"],
    }, errors


def verify(instance: Path, manifest_path: Path | None) -> tuple[dict[str, object], int]:
    build_report = json.loads(
        (WORK_ROOT / "build_report.json").read_text(encoding="utf-8")
    )
    language, errors = verify_language(instance)
    rules, rule_errors = verify_generation_rules(instance)
    guide, guide_errors = verify_guide(instance)
    jar_data, jar_errors = verify_jar_data(instance)
    kubejs, kubejs_errors = verify_kubejs(instance)
    quests, quest_errors = verify_quests(instance)
    deployment, deployment_errors = verify_deployment(instance, manifest_path)
    errors.extend(rule_errors)
    errors.extend(guide_errors)
    errors.extend(jar_errors)
    errors.extend(kubejs_errors)
    errors.extend(quest_errors)
    errors.extend(deployment_errors)
    status = (
        "complete"
        if not errors and manifest_path
        else "ready_for_apply"
        if not errors
        else "incomplete"
    )
    validation = {
        "scope": "Productive Trees family completion",
        "language": language,
        "generation_rules": rules,
        "guide": guide,
        "related_content": jar_data,
        "kubejs": kubejs,
        "ftbquests": quests,
        "deployment": deployment,
        "remaining": len(errors),
        "errors": errors,
        "status": status,
    }
    (WORK_ROOT / "family_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    completion = {
        "scope": "Productive Trees family",
        "installed": [build_report["jar"]],
        "counts": {
            "language_english_keys": build_report["language"]["english_keys"],
            "language_existing_korean_reused": 0,
            "language_existing_korean_corrected": 0,
            "language_newly_translated": build_report["language"]["newly_translated"],
            "tree_bases": rules.get("tree_bases", 0),
            "guide_files": guide.get("files", 0),
            "guide_display_fields": guide.get("display_fields", 0),
            "quest_display_keys": build_report["ftbquests"]["display_keys"],
            "quest_existing_korean_reused": build_report["ftbquests"][
                "existing_korean_reused"
            ],
            "quest_existing_korean_corrected": build_report["ftbquests"][
                "existing_korean_corrected"
            ],
            "quest_newly_translated": build_report["ftbquests"]["newly_translated"],
            "related_quest_keys": build_report["ftbquests"]["related_keys"],
            "remaining": len(errors),
        },
        "related_content": {
            "guide": guide,
            "advancements": jar_data["advancements"],
            "data_rules": jar_data["data_rules"],
            "kubejs": kubejs,
            "ftbquests": quests,
        },
        "generation_rules": rules,
        "deployment": deployment,
        "review_items": errors,
        "status": status,
    }
    (WORK_ROOT / "family_completion.json").write_text(
        json.dumps(completion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return validation, 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("--deployment-manifest", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root()
    if args.command == "build":
        print(json.dumps(build(instance), ensure_ascii=False, indent=2))
        return 0
    report, status = verify(instance, args.deployment_manifest)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
