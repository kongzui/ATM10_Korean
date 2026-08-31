#!/usr/bin/env python3
"""Productive Bees와 Modular Bees 번역을 빌드하고 전체 범위를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

import audit_ftbquests_titles as quest_audit
import build_ae2_quests as snbt
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

WORK_ROOT = PROJECT_ROOT / "working/productivebees"
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"
QUEST_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
QUEST_CHAPTER = "productive_bees"
DYNAMIC_REPORT = WORK_ROOT / "dynamic_name_validation.json"
TARGETS = (
    ("productivebees-", "productivebees", "guide"),
    ("ModularBees-", "modularbees", "modular_guide"),
)
DISPLAY_FIELDS = {"name", "title", "text", "description", "subtitle"}
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
PATCHOULI = re.compile(r"\$\([^)]*\)")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
TRANSLATION_KEY = re.compile(r"^[a-z0-9_.-]+(?:\.[a-z0-9_.-]+)+$")
BEE_NAME = re.compile(r"^(.+) Bee$")

INTENTIONAL_ORIGINAL_KEYS = {
    "entity.productivebees.basalz_bee",
    "entity.productivebees.beebee_bee",
    "entity.productivebees.blazing_bee",
    "entity.productivebees.blitz_bee",
    "entity.productivebees.blizz_bee",
    "entity.productivebees.breeze_bee",
    "entity.productivebees.brown_shroom_bee",
    "entity.productivebees.cheese_bee",
    "entity.productivebees.creeper_bee",
    "entity.productivebees.crimson_bee",
    "entity.productivebees.cupid_bee",
    "entity.productivebees.depth_ingot_bee",
    "entity.productivebees.fbi_bee",
    "entity.productivebees.infinity_bee",
    "entity.productivebees.kamikaz_bee",
    "entity.productivebees.pepto_bismol_bee",
    "entity.productivebees.phil_bee",
    "entity.productivebees.prosperity_bee",
    "entity.productivebees.red_shroom_bee",
    "entity.productivebees.ribbeet_bee",
    "entity.productivebees.royal_bee",
    "entity.productivebees.ruby_bee",
    "entity.productivebees.sky_ingot_bee",
    "entity.productivebees.villager_bee",
    "entity.productivebees.wanna_bee",
    "entity.productivebees.warped_bee",
    "entity.productivebees.zombie_bee",
}
INTENTIONAL_ORIGINAL_VALUES = {
    "Productive Bees",
    "Productive Bees!",
    "Modular Bees",
    "%s",
    "AllRightsReserved",
    "CreeBee",
    "ZomBee",
    "CuBee",
}
BILINGUAL_NAME_EXCEPTIONS = INTENTIONAL_ORIGINAL_KEYS | {
    "entity.productivebees.grave_bee",
    "entity.productivebees.patrick_bee",
}
DYNAMIC_LOCALIZED_NAME_EXCEPTIONS = {
    "entity.productivebees.allthemodium_bee": "Allthemodium 벌",
    "entity.productivebees.cloggrum_bee": "클로그룸 벌",
    "entity.productivebees.fluix_bee": "플루익스 벌",
    "entity.productivebees.forgotten_bee": "잊힌 벌",
    "entity.productivebees.froststeel_bee": "서리철 벌",
    "entity.productivebees.regalium_bee": "레갈륨 벌",
    "entity.productivebees.unobtainium_bee": "Unobtainium 벌",
    "entity.productivebees.utheric_bee": "우테릭 벌",
    "entity.productivebees.vibranium_bee": "Vibranium 벌",
}
DYNAMIC_NAME_TEMPLATES = {
    "item.productivebees.honeycomb_configurable": "%s의 벌집 조각",
    "block.productivebees.comb_configurable": "%s의 벌집 블록",
}
QUALITY_REVIEW_COUNTS = {
    "productivebees": {"reused": 1040, "corrected": 78, "new": 0},
    "modularbees": {"reused": 48, "corrected": 6, "new": 0},
    "guides": {"reused": 302, "corrected": 29, "new": 0},
    "ftbquests": {"reused": 411, "corrected": 155, "new": 0},
    "productivetrees": {"reused": 4, "corrected": 1, "new": 0},
    "overall": {"reused": 1805, "corrected": 269, "new": 0},
}
RELATED_BILINGUAL_BEE = {
    "key": "entity.productivebees.uru_metal_bee",
    "source": "Uru Metal Bee",
    "target": "우루 금속 벌",
    "jar_prefix": "sgearmetalworks-",
    "definition": "data/productivebees/productivebees/uru_metal.json",
    "work": PROJECT_ROOT / "working/silentgear/sgearmetalworks/ko_kr.json",
    "output": OUTPUT_ASSETS / "sgearmetalworks/lang/ko_kr.json",
}
PRODUCTIVE_TREES_INTEGRATION = {
    "jar_prefix": "productivetrees-",
    "work": PROJECT_ROOT / "working/productivetrees/ko_kr.json",
    "output": OUTPUT_ASSETS / "productivetrees/lang/ko_kr.json",
    "values": {
        "entity.productivebees.allergy_bee": ("Allergy Bee", "알레르기 벌"),
        "productivebees.ingredient.description.allergy_bee": (
            "Puts in an extra effort to collect pollen so your allergies don't act up "
            "while working with trees.",
            "나무 작업 중 알레르기가 생기지 않도록 꽃가루를 더 열심히 모읍니다.",
        ),
        "productivebees.devices.advanced_beehive": (
            "Advanced Beehive",
            "고급 벌통",
        ),
        "productivetrees.devices.advanced_beehive": (
            "Advanced Beehive",
            "고급 벌통",
        ),
        "productivetrees.information.upgrade.upgrade_pollen_sieve.advanced_hive": (
            "With this upgrade installed in the hive some pollen collected by bees will "
            "be sifted and deposited in the hive.",
            "이 업그레이드를 벌통에 설치하면 벌이 수집한 꽃가루 일부를 걸러 벌통에 "
            "보관합니다.",
        ),
    },
}
DYNAMIC_NAME_CLASS_CONSTANTS = {
    "cy/jdkdigital/productivebees/common/item/Honeycomb.class": (
        b"entity.productivebees.",
        b"item.productivebees.honeycomb_configurable",
    ),
    "cy/jdkdigital/productivebees/common/item/CombBlockItem.class": (
        b"entity.productivebees.",
        b"block.productivebees.comb_configurable",
    ),
    "cy/jdkdigital/productivebees/common/item/SpawnEgg.class": (
        b"entity.productivebees.",
        b"item.productivebees.spawn_egg_configurable",
    ),
    "cy/jdkdigital/productivebees/compat/jei/ingredients/BeeIngredientHelper.class": (
        b"entity.productivebees.",
        b"getDisplayName",
    ),
    "cy/jdkdigital/productivebees/compat/jei/ingredients/BeeIngredientRenderer.class": (
        b"entity.productivebees.",
        b"getTooltip",
    ),
}


def find_jar(instance: Path, prefix: str) -> Path:
    found = sorted((instance / "mods").glob(prefix + "*.jar"))
    if len(found) != 1:
        raise RuntimeError(f"JAR을 하나로 확정하지 못했습니다: {prefix} -> {found}")
    return found[0]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(archive: ZipFile, name: str) -> dict[str, object]:
    return json.loads(archive.read(name).decode("utf-8-sig"))


def find_bilingual_comb_bees(
    archive: ZipFile, english: dict[str, object]
) -> dict[str, str]:
    """가변 벌집을 만드는 일반 자원 벌과 영어 자원명을 반환한다."""
    create_comb: dict[str, bool] = {}
    marker = "data/productivebees/productivebees/"
    for name in archive.namelist():
        if not name.startswith(marker) or not name.endswith(".json"):
            continue
        data = load_json(archive, name)
        stem = Path(name).stem
        enabled = data.get("createComb", True) is not False
        create_comb[stem] = create_comb.get(stem, False) or enabled

    found: dict[str, str] = {}
    for stem, enabled in create_comb.items():
        key = f"entity.productivebees.{stem}_bee"
        source = english.get(key)
        match = BEE_NAME.fullmatch(source) if isinstance(source, str) else None
        if enabled and match and key not in BILINGUAL_NAME_EXCEPTIONS:
            found[key] = match.group(1)
    return found


def verify_dynamic_name_classes(jar: Path) -> tuple[list[str], list[str]]:
    """벌집·생성 알·JEI가 같은 벌 번역 키를 읽는지 확인한다."""
    checked: list[str] = []
    errors: list[str] = []
    with ZipFile(jar) as archive:
        for name, constants in DYNAMIC_NAME_CLASS_CONSTANTS.items():
            try:
                bytecode = archive.read(name)
            except KeyError:
                errors.append(f"동적 이름 표시 클래스를 찾지 못했습니다: {name}")
                continue
            missing = [
                value.decode("ascii") for value in constants if value not in bytecode
            ]
            if missing:
                errors.append(f"동적 이름 표시 상수 누락: {name} -> {missing}")
            else:
                checked.append(name)
    return checked, errors


def verify_related_bilingual_bee(instance: Path) -> tuple[dict[str, object], list[str]]:
    """다른 모드가 추가한 Productive Bees 재료 벌도 같은 규칙으로 확인한다."""
    errors: list[str] = []
    jar = find_jar(instance, str(RELATED_BILINGUAL_BEE["jar_prefix"]))
    with ZipFile(jar) as archive:
        english = load_json(archive, "assets/sgearmetalworks/lang/en_us.json")
        definition = str(RELATED_BILINGUAL_BEE["definition"])
        if definition not in archive.namelist():
            errors.append(f"연동 재료 벌 정의 누락: {definition}")
        else:
            data = load_json(archive, definition)
            if data.get("createComb", True) is False:
                errors.append(f"연동 재료 벌이 벌집을 만들지 않습니다: {definition}")
    key = str(RELATED_BILINGUAL_BEE["key"])
    source = str(RELATED_BILINGUAL_BEE["source"])
    target = str(RELATED_BILINGUAL_BEE["target"])
    if english.get(key) != source:
        errors.append(f"연동 재료 벌 영어 원명 불일치: {key}={english.get(key)}")
    for label in ("work", "output"):
        path = RELATED_BILINGUAL_BEE[label]
        assert isinstance(path, Path)
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get(key) != target:
            errors.append(f"연동 재료 벌 이중 표기 불일치: {path} -> {data.get(key)}")
    return {
        "key": key,
        "source": source,
        "target": target,
        "jar": jar.name,
        "exact_target_verified": target == "우루 금속 벌",
    }, errors


def verify_productive_trees_integration(
    instance: Path,
) -> tuple[dict[str, object], list[str]]:
    """Productive Trees가 소유한 Productive Bees 직접 연동 문구를 확인한다."""
    errors: list[str] = []
    jar = find_jar(instance, str(PRODUCTIVE_TREES_INTEGRATION["jar_prefix"]))
    with ZipFile(jar) as archive:
        english = load_json(archive, "assets/productivetrees/lang/en_us.json")

    work = PRODUCTIVE_TREES_INTEGRATION["work"]
    output = PRODUCTIVE_TREES_INTEGRATION["output"]
    assert isinstance(work, Path)
    assert isinstance(output, Path)
    work_values = json.loads(work.read_text(encoding="utf-8"))
    output_values = json.loads(output.read_text(encoding="utf-8"))
    values = PRODUCTIVE_TREES_INTEGRATION["values"]
    assert isinstance(values, dict)
    for key, pair in values.items():
        source, target = pair
        if english.get(key) != source:
            errors.append(f"Productive Trees 연동 영어 원문 불일치: {key}")
        if work_values.get(key) != target:
            errors.append(f"Productive Trees 연동 작업본 불일치: {key}")
        if output_values.get(key) != target:
            errors.append(f"Productive Trees 연동 산출물 불일치: {key}")
        errors.extend(validate_value(key, source, target))
    if sha256(work) != sha256(output):
        errors.append("Productive Trees 연동 작업본과 산출물 해시 불일치")
    return {
        "provider": "Productive Trees",
        "jar": jar.name,
        "display_keys_checked": len(values),
        "keys": sorted(values),
        "exact_targets_verified": not errors,
    }, errors


def validate_text(key: str, source: str, target: str) -> list[str]:
    errors: list[str] = []
    if PLACEHOLDER.findall(source) != PLACEHOLDER.findall(target):
        errors.append(f"자리표시자 불일치: {key}")
    if Counter(FORMAT_CODE.findall(source)) != Counter(FORMAT_CODE.findall(target)):
        errors.append(f"서식 코드 불일치: {key}")
    if Counter(PATCHOULI.findall(source)) != Counter(PATCHOULI.findall(target)):
        errors.append(f"Patchouli 태그 불일치: {key}")
    if source.count("\n") != target.count("\n"):
        errors.append(f"줄바꿈 수 불일치: {key}")
    return errors


def validate_value(key: str, source: object, target: object) -> list[str]:
    if type(source) is not type(target):
        return [f"자료형 불일치: {key}"]
    if isinstance(source, str):
        assert isinstance(target, str)
        return validate_text(key, source, target)
    if source != target:
        return [f"비문자 값 변경: {key}"]
    return []


def iter_display_values(
    source: object,
    target: object,
    path: str = "",
    parent: str | None = None,
) -> tuple[list[tuple[str, str, str]], list[str]]:
    rows: list[tuple[str, str, str]] = []
    errors: list[str] = []
    if type(source) is not type(target):
        return rows, [f"가이드 자료형 불일치: {path}"]
    if isinstance(source, dict):
        if list(source) != list(target):
            errors.append(f"가이드 키 또는 순서 불일치: {path}")
            return rows, errors
        for key in source:
            child_rows, child_errors = iter_display_values(
                source[key], target[key], f"{path}/{key}", key
            )
            rows.extend(child_rows)
            errors.extend(child_errors)
    elif isinstance(source, list):
        if len(source) != len(target):
            errors.append(f"가이드 배열 길이 불일치: {path}")
            return rows, errors
        for index, (left, right) in enumerate(zip(source, target, strict=True)):
            child_rows, child_errors = iter_display_values(
                left, right, f"{path}/{index}", parent
            )
            rows.extend(child_rows)
            errors.extend(child_errors)
    elif isinstance(source, str):
        assert isinstance(target, str)
        if parent in DISPLAY_FIELDS:
            rows.append((path, source, target))
            errors.extend(validate_text(path, source, target))
        elif source != target:
            errors.append(f"가이드 비표시 값 변경: {path}")
    elif source != target:
        errors.append(f"가이드 비문자 값 변경: {path}")
    return rows, errors


def copy_tree(source: Path, target: Path) -> list[str]:
    copied: list[str] = []
    for path in sorted(source.rglob("*.json")):
        relative = path.relative_to(source)
        output = target / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, output)
        copied.append(output.relative_to(PROJECT_ROOT).as_posix())
    return copied


def build(instance: Path) -> dict[str, object]:
    language_rows: list[dict[str, object]] = []
    guide_rows: list[dict[str, object]] = []
    outputs: list[str] = []
    for prefix, namespace, book in TARGETS:
        jar = find_jar(instance, prefix)
        with ZipFile(jar) as archive:
            english = load_json(archive, f"assets/{namespace}/lang/en_us.json")
        work_language = WORK_ROOT / namespace / "ko_kr.json"
        korean = json.loads(work_language.read_text(encoding="utf-8"))
        if list(english) != list(korean):
            raise ValueError(f"작업본의 키 또는 순서가 원문과 다릅니다: {namespace}")
        output_language = OUTPUT_ASSETS / namespace / "lang/ko_kr.json"
        output_language.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(work_language, output_language)
        outputs.append(output_language.relative_to(PROJECT_ROOT).as_posix())
        language_rows.append(
            {
                "namespace": namespace,
                "jar": jar.name,
                "english_keys": len(english),
                "existing_korean_reused": QUALITY_REVIEW_COUNTS[namespace]["reused"],
                "existing_korean_corrected": QUALITY_REVIEW_COUNTS[namespace][
                    "corrected"
                ],
                "newly_translated": QUALITY_REVIEW_COUNTS[namespace]["new"],
            }
        )
        guide_source = WORK_ROOT / namespace / "guide/ko_kr"
        guide_output = OUTPUT_ASSETS / namespace / f"patchouli_books/{book}/ko_kr"
        guide_files = copy_tree(guide_source, guide_output)
        outputs.extend(guide_files)
        guide_rows.append(
            {"namespace": namespace, "book": book, "files": len(guide_files)}
        )

    english_quests = json.loads(
        (WORK_ROOT / "quest_english.json").read_text(encoding="utf-8")
    )
    quest_overrides = json.loads(
        (WORK_ROOT / "quest_overrides.json").read_text(encoding="utf-8")
    )
    base = (
        QUEST_OUTPUT
        if QUEST_OUTPUT.is_file()
        else instance / "config/ftbquests/quests/lang/ko_kr.snbt"
    )
    merged = snbt.merge_into_full_snbt(base, quest_overrides)
    QUEST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    reparsed = snbt.parse_language_snbt(QUEST_OUTPUT)
    if any(reparsed.get(key) != value for key, value in quest_overrides.items()):
        raise ValueError("Productive Bees 퀘스트 누적 병합 결과가 다릅니다.")
    outputs.append(QUEST_OUTPUT.relative_to(PROJECT_ROOT).as_posix())
    quest_row = {
        "chapter": QUEST_CHAPTER,
        "display_keys": len(english_quests),
        "existing_korean_reused": QUALITY_REVIEW_COUNTS["ftbquests"]["reused"],
        "existing_korean_corrected": QUALITY_REVIEW_COUNTS["ftbquests"]["corrected"],
        "newly_translated": QUALITY_REVIEW_COUNTS["ftbquests"]["new"],
    }
    report = {
        "scope": "Productive Bees family",
        "languages": language_rows,
        "guides": guide_rows,
        "ftbquests": quest_row,
        "outputs": sorted(outputs),
    }
    (WORK_ROOT / "build_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def verify_languages(instance: Path) -> tuple[list[dict[str, object]], list[str]]:
    rows: list[dict[str, object]] = []
    errors: list[str] = []
    display_names: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for prefix, namespace, _ in TARGETS:
        jar = find_jar(instance, prefix)
        with ZipFile(jar) as archive:
            english = load_json(archive, f"assets/{namespace}/lang/en_us.json")
            bilingual_bees = (
                find_bilingual_comb_bees(archive, english)
                if namespace == "productivebees"
                else {}
            )
        work = WORK_ROOT / namespace / "ko_kr.json"
        output = OUTPUT_ASSETS / namespace / "lang/ko_kr.json"
        if work.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"UTF-8 BOM이 있습니다: {work}")
        korean = json.loads(work.read_text(encoding="utf-8"))
        if list(english) != list(korean):
            errors.append(f"키 또는 순서 불일치: {namespace}")
            continue
        translated = 0
        intentional = 0
        for key, source in english.items():
            target = korean[key]
            errors.extend(validate_value(key, source, target))
            if isinstance(source, str):
                if target == source and LATIN_WORD.search(source):
                    if (
                        key in INTENTIONAL_ORIGINAL_KEYS
                        or source in INTENTIONAL_ORIGINAL_VALUES
                    ):
                        intentional += 1
                    else:
                        errors.append(f"분류되지 않은 영어 유지 키: {key}={source}")
                else:
                    translated += 1
                if key.startswith(("entity.", "block.", "item.")):
                    display_names[target].append((key, source))
        for key, english_name in bilingual_bees.items():
            target = korean[key]
            localized_target = DYNAMIC_LOCALIZED_NAME_EXCEPTIONS.get(key)
            if localized_target is not None:
                if target != localized_target:
                    errors.append(
                        f"자원 벌 확정 번역 불일치: {key} -> {target} "
                        f"(필요한 값: {localized_target})"
                    )
                continue
            expected_suffix = f"({english_name}) 벌"
            if not isinstance(target, str) or not target.endswith(expected_suffix):
                errors.append(
                    f"자원 벌 이중 표기 불일치: {key} -> {target} "
                    f"(필요한 끝부분: {expected_suffix})"
                )
        if namespace == "productivebees":
            for key, expected in DYNAMIC_NAME_TEMPLATES.items():
                if korean.get(key) != expected:
                    errors.append(f"가변 벌집 이름 틀 불일치: {key}={korean.get(key)}")
            for key in INTENTIONAL_ORIGINAL_KEYS:
                target = korean.get(key)
                if isinstance(target, str) and "(" in target:
                    errors.append(
                        f"말장난 벌 이름에 불필요한 이중 표기: {key}={target}"
                    )
        if not output.is_file() or sha256(work) != sha256(output):
            errors.append(f"작업본과 산출물 해시가 다릅니다: {namespace}")
        rows.append(
            {
                "namespace": namespace,
                "keys": len(english),
                "translated": translated,
                "intentional_original": intentional,
                "bilingual_comb_bees": len(bilingual_bees),
            }
        )
    collisions = {
        name: entries
        for name, entries in display_names.items()
        if len({source for _, source in entries}) > 1
    }
    if collisions:
        errors.append(f"서로 다른 아이템·블록·벌 이름 충돌: {collisions}")
    productivebees_jar = find_jar(instance, TARGETS[0][0])
    dynamic_paths, dynamic_errors = verify_dynamic_name_classes(productivebees_jar)
    errors.extend(dynamic_errors)
    rows[0]["dynamic_name_paths_checked"] = dynamic_paths
    related_bee, related_errors = verify_related_bilingual_bee(instance)
    errors.extend(related_errors)
    rows[0]["related_bilingual_comb_bee"] = related_bee
    productive_trees, productive_trees_errors = verify_productive_trees_integration(
        instance
    )
    errors.extend(productive_trees_errors)
    rows[0]["productive_trees_integration"] = productive_trees
    return rows, errors


def verify_guides(instance: Path) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    rows: list[dict[str, object]] = []
    allowed_same = {"CreeBee", "ZomBee", "CuBee"}
    for prefix, namespace, book in TARGETS:
        jar = find_jar(instance, prefix)
        marker = f"assets/{namespace}/patchouli_books/{book}/en_us/"
        source_files: dict[str, object] = {}
        with ZipFile(jar) as archive:
            for name in archive.namelist():
                if name.startswith(marker) and name.endswith(".json"):
                    source_files[name[len(marker) :]] = load_json(archive, name)
        work_root = WORK_ROOT / namespace / "guide/ko_kr"
        work_files = {
            path.relative_to(work_root).as_posix(): path
            for path in work_root.rglob("*.json")
        }
        if set(source_files) != set(work_files):
            errors.append(f"가이드 파일 목록 불일치: {namespace}")
            continue
        display_count = 0
        translated_count = 0
        intentional_count = 0
        for relative, source in source_files.items():
            target = json.loads(work_files[relative].read_text(encoding="utf-8"))
            values, value_errors = iter_display_values(source, target, relative)
            errors.extend(value_errors)
            display_count += len(values)
            for path, left, right in values:
                if left == right and LATIN_WORD.search(left):
                    if left in allowed_same:
                        intentional_count += 1
                    else:
                        errors.append(f"분류되지 않은 가이드 영어 유지: {path}={left}")
                elif left != right:
                    translated_count += 1
            output = (
                OUTPUT_ASSETS / namespace / f"patchouli_books/{book}/ko_kr" / relative
            )
            if not output.is_file() or sha256(work_files[relative]) != sha256(output):
                errors.append(
                    f"가이드 작업본과 산출물 해시 불일치: {namespace}/{relative}"
                )
        rows.append(
            {
                "namespace": namespace,
                "files": len(source_files),
                "display_fields": display_count,
                "translated": translated_count,
                "intentional_original": intentional_count,
            }
        )
    return {"books": rows}, errors


def nested_values(value: object, key_name: str) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == key_name and isinstance(child, str):
                found.append(child)
            found.extend(nested_values(child, key_name))
    elif isinstance(value, list):
        for child in value:
            found.extend(nested_values(child, key_name))
    return found


def verify_jar_data(
    instance: Path, translations: dict[str, object]
) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    advancement_files = 0
    advancement_keys: set[str] = set()
    advancement_literals: list[str] = []
    definition_files = 0
    definition_description_keys: set[str] = set()
    integrations: set[str] = set()
    installed: list[str] = []
    for prefix, namespace, _ in TARGETS:
        jar = find_jar(instance, prefix)
        installed.append(jar.name)
        with ZipFile(jar) as archive:
            for name in archive.namelist():
                if not name.endswith(".json"):
                    continue
                if "/advancement" in name:
                    advancement_files += 1
                    data = load_json(archive, name)
                    advancement_keys.update(nested_values(data, "translate"))
                    display = data.get("display", {})
                    if isinstance(display, dict):
                        for field in ("title", "description"):
                            component = display.get(field)
                            if isinstance(component, dict) and isinstance(
                                component.get("text"), str
                            ):
                                advancement_literals.append(f"{name}:{field}")
                marker = f"data/{namespace}/productivebees/"
                if name.startswith(marker):
                    definition_files += 1
                    relative = name[len(marker) :]
                    integrations.add(relative.partition("/")[0])
                    data = load_json(archive, name)
                    for value in nested_values(data, "description"):
                        if TRANSLATION_KEY.fullmatch(value):
                            definition_description_keys.add(value)
                        elif LATIN_WORD.search(value):
                            errors.append(f"데이터 표시 literal 미분류: {name}={value}")
    missing_advancements = sorted(advancement_keys - set(translations))
    missing_descriptions = sorted(definition_description_keys - set(translations))
    if missing_advancements:
        errors.append(f"발전 과제 번역 키 누락: {missing_advancements}")
    if advancement_literals:
        errors.append(f"발전 과제 literal 표시 문구가 있습니다: {advancement_literals}")
    if missing_descriptions:
        errors.append(f"자동 생성 설명 키 누락: {missing_descriptions}")
    return {
        "installed": installed,
        "advancements": {
            "files_checked": advancement_files,
            "translation_keys_checked": len(advancement_keys),
            "literal_display_fields": len(advancement_literals),
            "missing": len(missing_advancements),
        },
        "generated_definitions": {
            "files_checked": definition_files,
            "description_keys_checked": len(definition_description_keys),
            "integration_groups": sorted(integrations),
            "missing": len(missing_descriptions),
        },
    }, errors


def verify_kubejs(instance: Path) -> tuple[dict[str, object], list[str]]:
    root = instance / "kubejs"
    referenced: list[str] = []
    display_literals: list[str] = []
    display_call = re.compile(r"(?:displayName|Text\.of|addTooltip|addText)\s*\(")
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json", ".snbt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        if not re.search(
            r"productivebees|modularbees|Productive Bees|ModularBees", text
        ):
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
                        display_literals.append(f"{relative}:{field}={value}")
        elif display_call.search(text):
            for line_no, line in enumerate(text.splitlines(), 1):
                if display_call.search(line) and re.search(
                    r"productivebees|modularbees", line
                ):
                    display_literals.append(f"{relative}:{line_no}={line.strip()}")
    historical = [
        item
        for item in display_literals
        if item.startswith("server_scripts/announcements/announcements.js:")
    ]
    actionable = [item for item in display_literals if item not in historical]
    errors = [f"KubeJS 직접 표시 문구가 남았습니다: {actionable}"] if actionable else []
    return {
        "files_referencing_family": len(referenced),
        "referenced_files": sorted(referenced),
        "translated_literals": 0,
        "historical_announcement_out_of_scope": len(historical),
        "unresolved_display_literals": len(actionable),
    }, errors


def verify_quests(
    instance: Path, translations: dict[str, object]
) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    english = json.loads((WORK_ROOT / "quest_english.json").read_text(encoding="utf-8"))
    korean = json.loads(
        (WORK_ROOT / "quest_overrides.json").read_text(encoding="utf-8")
    )
    output = snbt.parse_language_snbt(QUEST_OUTPUT)
    allowed_same = INTENTIONAL_ORIGINAL_VALUES | {
        "BlazBee",
        "Brown Shroombee",
        "Crimson Shroombee",
        "RuBee",
        "BreezBee",
        "ProsperiBee",
        "Red Shroombee",
        "Warped Shroombee",
    }
    chapters, _ = quest_audit.parse_chapters(instance / "config/ftbquests/quests")
    chapter = next(
        (row for row in chapters if row["filename"] == QUEST_CHAPTER + ".snbt"),
        None,
    )
    if chapter is None:
        return {}, ["Productive Bees 전용 챕터를 찾지 못했습니다."]
    tasks_by_key = {
        f"task.{task['id']}.title": task
        for quest in chapter["quests"]
        for task in quest["tasks"]
    }
    omitted_single_item_titles = 0
    for key, source in english.items():
        if key not in korean:
            task = tasks_by_key.get(key)
            if (
                task
                and task["type"] == "item"
                and "ftbfiltersystem:smart_filter" not in task["item_id"]
            ):
                namespace, _, item_path = task["item_id"].partition(":")
                item_name = translations.get(
                    f"item.{namespace}.{item_path}",
                    translations.get(f"block.{namespace}.{item_path}", ""),
                )
                if item_name:
                    omitted_single_item_titles += 1
                    continue
            errors.append(f"퀘스트 번역 키 누락: {key}")
            continue
        target = korean[key]
        if output.get(key) != target:
            errors.append(f"퀘스트 누적 출력 불일치: {key}")
        errors.extend(snbt.validate_value(key, source, target))
        source_flat = snbt.flatten(source)
        target_flat = snbt.flatten(target)
        if source_flat == target_flat and LATIN_WORD.search(source_flat):
            if source_flat not in allowed_same:
                errors.append(f"분류되지 않은 퀘스트 영어 유지: {key}={source_flat}")

    custom_names = [
        task
        for quest in chapter["quests"]
        for task in quest["tasks"]
        if task["custom_name"]
    ]
    if custom_names:
        errors.append(f"전용 챕터 custom_name 미처리: {custom_names}")
    explicit = 0
    redundant: list[str] = []
    for quest in chapter["quests"]:
        for task in quest["tasks"]:
            key = f"task.{task['id']}.title"
            if key not in english or key not in korean:
                continue
            explicit += 1
            if (
                task["type"] != "item"
                or "ftbfiltersystem:smart_filter" in task["item_id"]
            ):
                continue
            item_id = task["item_id"]
            namespace, _, item_path = item_id.partition(":")
            item_name = translations.get(
                f"item.{namespace}.{item_path}",
                translations.get(f"block.{namespace}.{item_path}", ""),
            )
            if (
                item_name
                and quest_audit.strip_formatting(snbt.flatten(korean[key])) == item_name
            ):
                redundant.append(task["id"])
    if redundant:
        errors.append(f"단순 ItemTask 중복 제목: {redundant}")
    target_namespaces = {"productivebees", "modularbees", "productivelib"}
    related = [
        task
        for other in chapters
        if other is not chapter
        for quest in other["quests"]
        for task in quest["tasks"]
        if task["item_id"].partition(":")[0] in target_namespaces
    ]
    related_custom = [task for task in related if task["custom_name"]]
    if related_custom:
        errors.append(f"전용 챕터 밖 관련 custom_name 미처리: {related_custom}")
    return {
        "chapter": chapter["filename"],
        "quests_checked": len(chapter["quests"]),
        "tasks_checked": sum(len(row["tasks"]) for row in chapter["quests"]),
        "display_keys_checked": len(english),
        "explicit_task_titles_checked": explicit,
        "omitted_single_item_task_titles": omitted_single_item_titles,
        "custom_names": len(custom_names),
        "redundant_single_item_task_titles": len(redundant),
        "related_tasks_outside_chapter_checked": len(related),
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
        "resourcepacks/ATM10_Korean/assets/productivebees/lang/ko_kr.json": (
            OUTPUT_ASSETS / "productivebees/lang/ko_kr.json"
        ),
        "resourcepacks/ATM10_Korean/assets/modularbees/lang/ko_kr.json": (
            OUTPUT_ASSETS / "modularbees/lang/ko_kr.json"
        ),
        "resourcepacks/ATM10_Korean/assets/productivetrees/lang/ko_kr.json": (
            OUTPUT_ASSETS / "productivetrees/lang/ko_kr.json"
        ),
    }
    for _, namespace, book in TARGETS:
        root = OUTPUT_ASSETS / namespace / f"patchouli_books/{book}/ko_kr"
        for path in root.rglob("*.json"):
            relative = path.relative_to(OUTPUT_ASSETS)
            expected[
                (Path("resourcepacks/ATM10_Korean/assets") / relative).as_posix()
            ] = path
    return expected


def dynamic_name_deployment_sources() -> dict[str, Path]:
    related_output = RELATED_BILINGUAL_BEE["output"]
    assert isinstance(related_output, Path)
    return {
        "resourcepacks/ATM10_Korean/assets/productivebees/lang/ko_kr.json": (
            OUTPUT_ASSETS / "productivebees/lang/ko_kr.json"
        ),
        "resourcepacks/ATM10_Korean/assets/sgearmetalworks/lang/ko_kr.json": (
            related_output
        ),
    }


def verify_deployment(
    instance: Path, manifest_path: Path | None, deployment_scope: str
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
    changed = set(target["changed_paths"])
    errors: list[str] = []
    if deployment_scope == "dynamic-names":
        expected = dynamic_name_deployment_sources()
    elif deployment_scope == "changed":
        all_expected = expected_deployment_sources()
        invalid = changed - set(all_expected)
        if invalid:
            errors.append(
                f"Productive Bees 범위 밖 적용 경로가 있습니다: {sorted(invalid)}"
            )
        expected = {
            relative: all_expected[relative]
            for relative in changed
            if relative in all_expected
        }
    else:
        expected = expected_deployment_sources()
    if changed != set(expected):
        errors.append(f"Productive Bees 적용 경로가 계획과 다릅니다: {sorted(changed)}")
    if target["unexpected_changes"]:
        errors.append("적용 매니페스트에 계획 밖 변경이 기록되었습니다.")
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
        "scope": deployment_scope,
        "backup_manifest": str(manifest_path),
        "changed_paths": sorted(changed),
        "hash_matches": matches,
        "unexpected_changes": target["unexpected_changes"],
    }, errors


def verify(
    instance: Path, manifest_path: Path | None, deployment_scope: str
) -> tuple[dict[str, object], int]:
    build_report = json.loads(
        (WORK_ROOT / "build_report.json").read_text(encoding="utf-8")
    )
    languages, errors = verify_languages(instance)
    translations: dict[str, object] = {}
    for _, namespace, _ in TARGETS:
        translations.update(
            json.loads(
                (WORK_ROOT / namespace / "ko_kr.json").read_text(encoding="utf-8")
            )
        )
    guides, guide_errors = verify_guides(instance)
    jar_data, jar_errors = verify_jar_data(instance, translations)
    kubejs, kubejs_errors = verify_kubejs(instance)
    quests, quest_errors = verify_quests(instance, translations)
    deployment, deployment_errors = verify_deployment(
        instance, manifest_path, deployment_scope
    )
    errors.extend(guide_errors)
    errors.extend(jar_errors)
    errors.extend(kubejs_errors)
    errors.extend(quest_errors)
    errors.extend(deployment_errors)
    productive_language = json.loads(
        (WORK_ROOT / "productivebees/ko_kr.json").read_text(encoding="utf-8")
    )
    related_bee = languages[0]["related_bilingual_comb_bee"]
    assert isinstance(related_bee, dict)
    productive_trees = languages[0]["productive_trees_integration"]
    assert isinstance(productive_trees, dict)
    dynamic_names = {
        "bilingual_resource_bees": languages[0]["bilingual_comb_bees"] + 1,
        "productivebees_language_bees": languages[0]["bilingual_comb_bees"],
        "related_resource_bees": 1,
        "templates": DYNAMIC_NAME_TEMPLATES,
        "examples": {
            "entity.productivebees.kyanite_bee": productive_language[
                "entity.productivebees.kyanite_bee"
            ],
            "entity.productivebees.obsidian_bee": productive_language[
                "entity.productivebees.obsidian_bee"
            ],
            str(related_bee["key"]): related_bee["target"],
        },
        "wordplay_names_preserved": {
            key: productive_language[key]
            for key in (
                "entity.productivebees.creeper_bee",
                "entity.productivebees.blazing_bee",
                "entity.productivebees.zombie_bee",
            )
        },
        "display_paths_checked": languages[0]["dynamic_name_paths_checked"],
        "direct_integrations": [productive_trees],
        "remaining": (
            len(DYNAMIC_NAME_CLASS_CONSTANTS)
            - len(languages[0]["dynamic_name_paths_checked"])
            + (0 if related_bee["exact_target_verified"] else 1)
            + (0 if productive_trees["exact_targets_verified"] else 1)
        ),
        "status": (
            "passed"
            if len(languages[0]["dynamic_name_paths_checked"])
            == len(DYNAMIC_NAME_CLASS_CONSTANTS)
            and related_bee["exact_target_verified"]
            and productive_trees["exact_targets_verified"]
            else "failed"
        ),
    }
    DYNAMIC_REPORT.write_text(
        json.dumps(dynamic_names, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    validation = {
        "scope": "Productive Bees family completion",
        "languages": languages,
        "dynamic_names": dynamic_names,
        "guides": guides,
        "related_content": jar_data,
        "kubejs": kubejs,
        "ftbquests": quests,
        "deployment": deployment,
        "remaining": len(errors),
        "errors": errors,
        "status": "complete"
        if not errors and manifest_path
        else "ready_for_apply"
        if not errors
        else "incomplete",
    }
    (WORK_ROOT / "family_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    completion = {
        "scope": "Productive Bees family",
        "installed": jar_data["installed"],
        "counts": {
            "language_english_keys": sum(
                row["english_keys"] for row in build_report["languages"]
            ),
            "language_existing_korean_reused": sum(
                row["existing_korean_reused"] for row in build_report["languages"]
            ),
            "language_existing_korean_corrected": sum(
                row["existing_korean_corrected"] for row in build_report["languages"]
            ),
            "language_newly_translated": sum(
                row["newly_translated"] for row in build_report["languages"]
            ),
            "guide_files": sum(row["files"] for row in guides["books"]),
            "guide_display_fields": sum(
                row["display_fields"] for row in guides["books"]
            ),
            "guide_existing_korean_reused": QUALITY_REVIEW_COUNTS["guides"]["reused"],
            "guide_existing_korean_corrected": QUALITY_REVIEW_COUNTS["guides"][
                "corrected"
            ],
            "guide_newly_translated": QUALITY_REVIEW_COUNTS["guides"]["new"],
            "quest_display_keys": build_report["ftbquests"]["display_keys"],
            "quest_existing_korean_reused": build_report["ftbquests"][
                "existing_korean_reused"
            ],
            "quest_existing_korean_corrected": build_report["ftbquests"][
                "existing_korean_corrected"
            ],
            "quest_newly_translated": build_report["ftbquests"]["newly_translated"],
            "productive_trees_integration_keys": productive_trees[
                "display_keys_checked"
            ],
            "productive_trees_existing_korean_reused": QUALITY_REVIEW_COUNTS[
                "productivetrees"
            ]["reused"],
            "productive_trees_existing_korean_corrected": QUALITY_REVIEW_COUNTS[
                "productivetrees"
            ]["corrected"],
            "productive_trees_newly_translated": QUALITY_REVIEW_COUNTS[
                "productivetrees"
            ]["new"],
            "visible_values": sum(QUALITY_REVIEW_COUNTS["overall"].values()),
            "existing_korean_reused": QUALITY_REVIEW_COUNTS["overall"]["reused"],
            "existing_korean_corrected": QUALITY_REVIEW_COUNTS["overall"]["corrected"],
            "newly_translated": QUALITY_REVIEW_COUNTS["overall"]["new"],
            "remaining": len(errors),
        },
        "related_content": {
            "dynamic_names": dynamic_names,
            "guides": guides,
            "advancements": jar_data["advancements"],
            "generated_definitions": jar_data["generated_definitions"],
            "kubejs": kubejs,
            "ftbquests": quests,
        },
        "deployment": deployment,
        "review_items": errors,
        "status": validation["status"],
    }
    (WORK_ROOT / "family_completion.json").write_text(
        json.dumps(completion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return validation, 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("--deployment-manifest", type=Path)
    parser.add_argument(
        "--deployment-scope",
        choices=("full", "dynamic-names", "changed"),
        default="full",
    )
    args = parser.parse_args()
    instance = resolve_source_root()
    if args.command == "build":
        print(json.dumps(build(instance), ensure_ascii=False, indent=2))
        return 0
    report, status = verify(instance, args.deployment_manifest, args.deployment_scope)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
