#!/usr/bin/env python3
"""Corail Tombstone 전체 번역과 퀘스트·연동 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from build_ae2_quests import parse_language_snbt
from local_paths import PROJECT_ROOT, resolve_source_root

WORK_ROOT = PROJECT_ROOT / "working/common_ui/convenience/tombstone"
WORKING = WORK_ROOT / "ko_kr.json"
OVERRIDES = WORK_ROOT / "recheck_overrides.json"
REPORT = WORK_ROOT / "recheck_20260820.json"
OUTPUT = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/tombstone/lang/ko_kr.json"
)
PRODUCTIVE_WORKING = PROJECT_ROOT / "working/productivebees/productivebees/ko_kr.json"
PRODUCTIVE_OUTPUT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/productivebees/lang/ko_kr.json"
)
PRODUCTIVE_QUEST = PROJECT_ROOT / "working/productivebees/quest_overrides.json"
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
GLOSSARY = PROJECT_ROOT / "glossary/README.md"

EXPECTED_JAR = "tombstone-neoforge-1.21.1-9.5.1.jar"
EXPECTED_JAR_SHA256 = "b705f17075ebc3bc5d3f6649ba567a865bf8c3c469be402014c5d3deaae1f30e"
EXPECTED_OVERRIDE_SHA256 = (
    "8190c23916b45c7b6df59cd99214e7cb783c7141113e6c1fdd9d6b06fdb2352c"
)
EXPECTED_CONFIGS = {
    "tombstone-client.toml": (
        "fb33977a5fe7fcc2f4df4b6e31ff840b76c4c41e4b954d1c79d83772d8252e77",
        31,
    ),
    "tombstone-common.toml": (
        "090c98896ba716642faa18ff009860367803dec5eeb45ee5a000c09a08f672b9",
        70,
    ),
    "tombstone-server.toml": (
        "aeba26d153dbd0cf63dd41e7c11ac305b1144353628025de9a1c7a6d45bf6d29",
        71,
    ),
}
EXPECTED_UNTRANSLATED = {
    "tombstone.lang.last_update",
    "tombstone.message.rip",
}
EXPECTED_QUEST_REFERENCES = {
    "config/ftbquests/quests/chapters/productive_bees.snbt",
    "config/ftbquests/quests/chapters/tips_and_tricks.snbt",
    "config/ftbquests/quests/lang/en_us.snbt",
    "config/ftbquests/quests/lang/fr_fr.snbt",
    "config/ftbquests/quests/lang/id_id.snbt",
    "config/ftbquests/quests/lang/it_it.snbt",
    "config/ftbquests/quests/lang/ko_kr.snbt",
    "config/ftbquests/quests/lang/pt_br.snbt",
    "config/ftbquests/quests/lang/ru_ru.snbt",
}
EXPECTED_KUBE_REFERENCES = {
    "kubejs/assets/the_bumblezone/lang/ru_ru.json",
    "kubejs/assets/tombstone/lang/ru_ru.json",
    "kubejs/server_scripts/mods/Minecolonies/tags.js",
    "kubejs/server_scripts/Tweaks/tags.js",
}
RELATED_QUEST_COPIES = (
    PROJECT_ROOT / "working/ftbquests/common_chapter_overrides.json",
    PROJECT_ROOT / "working/actually_additions/quests/related/ko_kr.json",
    PROJECT_ROOT / "working/draconic_evolution/quests/related/ko_kr.json",
    PROJECT_ROOT / "working/industrial_foregoing/quests/related/ko_kr.json",
)
GLOSSARY_ROWS = (
    "| Corail Tombstone | Corail Tombstone | 공식 모드명 |",
    "| Decorative Grave | 장식 무덤 | 블록·기능명 |",
    "| Grave Soul | 무덤 영혼 | 개체·마법 자원명 |",
    "| Book of Disenchantment | 마법 해제의 책 | 아이템명 |",
    "| Magic Scroll | 마법 두루마리 | 아이템 분류명 |",
    "| Main Hand / Offhand | 주 손 / 보조 손 | 장비·조작 용어 |",
    "| Respawn / Respawn Point | 재생성 / 재생성 지점 |",
    "| Elytra | 겉날개 | Minecraft 아이템명 |",
    "| Grave's Bee | 무덤 벌 | 개체·퀘스트명 |",
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"(?<![A-Za-z_])\d+(?:\.\d+)?")
CONFIG_OPTION = re.compile(r"^\s*[A-Za-z0-9_]+\s*=", re.MULTILINE)
OTHER_ENGLISH_LANGUAGE = re.compile(r"assets/[^/]+/lang/en_us\.json")
DIRECT_REFERENCE = re.compile(
    r"(?i)corail[ _-]?tombstone|tombstone:|grave.?s bee|grave soul|decorative grave"
)
RELATED_EXTENSIONS = {".js", ".json", ".snbt", ".toml", ".txt"}
FORBIDDEN_TRANSLATIONS = re.compile(
    r"그레이브스 벌|장식용 무덤|장식된 무덤|장식 묘비|마법 스크롤|"
    r"마법 주문서|주손|마우스 오른쪽|오른쪽 클릭|우클릭을 유지|엔티티|"
    r"재사용 대기 시간|생물 군계|마법부여|스펙트럼 가디언|마을 디펜더|"
    r"룬 회로 인쇄기|불치병|닿기의 두루마리|수생의 두루마리|리스폰|엘리트라"
)
NUMBER_EXCEPTIONS = {
    "tombstone.item.christmas_gift.desc",
    "tombstone.message.gift.failed",
    "description.effect.tombstone.unstable_intangibility",
    "tombstone.advancement.chain_death.desc",
    "tombstone.advancement.strong_or_careful.desc",
    "tombstone.advancement.use_scribe.desc",
    "tombstone.compendium.halloween.desc",
    "tombstone.compendium.christmas.desc",
    "tombstone.compendium.spring_bloom.desc",
    "tombstone.compendium.christmas_gift.desc",
    "tombstone.compendium.scroll_of_unstable_intangibility.desc",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    number_exceptions_seen = set()
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
        if Counter(NUMBER.findall(source)) != Counter(NUMBER.findall(translated)):
            if key in NUMBER_EXCEPTIONS:
                number_exceptions_seen.add(key)
            else:
                errors.append(f"숫자 불일치: {key}")
    if number_exceptions_seen != NUMBER_EXCEPTIONS:
        errors.append(
            "숫자 표기 예외 범위 변경: "
            f"{sorted(number_exceptions_seen ^ NUMBER_EXCEPTIONS)}"
        )
    return errors


def find_related_files(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.suffix.lower() in RELATED_EXTENSIONS
    ]


def verify_other_language_owners(
    instance: Path,
    source_jar: Path,
    english: dict[str, object],
    errors: list[str],
) -> tuple[int, int, int]:
    """설치된 다른 모드가 같은 언어 키를 소유하는지 확인한다."""
    jar_count = 0
    language_files = 0
    conflicts = []
    unreadable = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        jar_count += 1
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
                    if jar_path == source_jar or not isinstance(values, dict):
                        continue
                    shared_keys = sorted(set(values) & set(english))
                    if shared_keys:
                        conflicts.append(f"{jar_path.name}:{name}:{shared_keys}")
        except (BadZipFile, KeyError, OSError, RuntimeError, TypeError) as exc:
            unreadable.append(f"{jar_path.name}:{exc}")
    if unreadable:
        errors.append("설치 JAR 언어 파일 읽기 오류: " + " | ".join(unreadable[:10]))
    if conflicts:
        errors.append("다른 모드의 언어 키 소유 충돌: " + " | ".join(conflicts))
    if jar_count != 480 or language_files != 388:
        errors.append(
            f"설치 JAR 범위 변경: JAR={jar_count}, 영어 언어={language_files}"
        )
    return jar_count, language_files, len(conflicts)


def verify(instance: Path, pre_apply: bool = False) -> dict[str, object]:
    """현재 설치 영어 원문과 프로젝트 산출물을 전수 검증한다."""
    errors: list[str] = []
    jar_matches = sorted((instance / "mods").glob("tombstone-neoforge-*.jar"))
    if [path.name for path in jar_matches] != [EXPECTED_JAR]:
        raise RuntimeError(
            f"Corail Tombstone JAR 범위 변경: {[path.name for path in jar_matches]}"
        )
    source_jar = jar_matches[0]
    source_sha256 = sha256(source_jar)
    if source_sha256 != EXPECTED_JAR_SHA256:
        errors.append(f"Corail Tombstone JAR SHA-256 변경: {source_sha256}")

    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        english = load_json_bytes(
            archive.read("assets/tombstone/lang/en_us.json"),
            "Corail Tombstone en_us",
        )
        bundled_korean = "assets/tombstone/lang/ko_kr.json" in names
        class_files = {
            name: archive.read(name) for name in names if name.endswith(".class")
        }
        language_files = [
            name
            for name in names
            if name.startswith("assets/tombstone/lang/") and name.endswith(".json")
        ]
        advancement_files = [
            name
            for name in names
            if name.startswith("data/tombstone/advancement") and name.endswith(".json")
        ]
        recipe_files = [
            name
            for name in names
            if name.startswith("data/tombstone/recipe") and name.endswith(".json")
        ]
        loot_files = [
            name for name in names if "loot_table" in name and name.endswith(".json")
        ]
        tag_files = [
            name for name in names if "/tags/" in name and name.endswith(".json")
        ]

    expected_jar_counts = (1644, 576, 7, 238, 103, 55, 71)
    actual_jar_counts = (
        len(names),
        len(class_files),
        len(language_files),
        len(advancement_files),
        len(recipe_files),
        len(loot_files),
        len(tag_files),
    )
    if actual_jar_counts != expected_jar_counts:
        errors.append(f"Corail Tombstone JAR 구성 변경: {actual_jar_counts}")
    if bundled_korean:
        errors.append("현재 JAR에 예상하지 않은 내장 한국어가 있습니다")
    if len(english) != 1233:
        errors.append(f"영어 언어 키 수 변경: {len(english)}")

    class_references = {
        key
        for key in english
        if any(key.encode() in raw for raw in class_files.values())
    }
    if len(class_references) != 116:
        errors.append(f"클래스 언어 키 참조 범위 변경: {len(class_references)}")

    working = load_json_path(WORKING)
    output = load_json_path(OUTPUT)
    overrides = load_json_path(OVERRIDES)
    errors.extend(validate_language(english, working))
    errors.extend(validate_language(english, output))
    if working != output:
        errors.append("Corail Tombstone working과 output 언어 파일이 다릅니다")
    if len(overrides) != 373 or sha256(OVERRIDES) != EXPECTED_OVERRIDE_SHA256:
        errors.append(
            "Corail Tombstone 재검수 교정 목록 변경: "
            f"키={len(overrides)}, SHA={sha256(OVERRIDES)}"
        )
    override_mismatches = sorted(
        key for key, value in overrides.items() if output.get(key) != value
    )
    if override_mismatches:
        errors.append(f"Corail Tombstone 교정값 불일치: {override_mismatches}")
    untranslated = {key for key in english if output.get(key) == english.get(key)}
    if untranslated != EXPECTED_UNTRANSLATED:
        errors.append(f"영어 원문 유지 범위 변경: {sorted(untranslated)}")
    forbidden = sorted(
        key
        for key, value in output.items()
        if isinstance(value, str) and FORBIDDEN_TRANSLATIONS.search(value)
    )
    if forbidden:
        errors.append(f"금지된 기존 기계 번역이 남았습니다: {forbidden}")
    if OUTPUT.read_bytes().startswith(b"\xef\xbb\xbf"):
        errors.append("Corail Tombstone 산출물에 UTF-8 BOM이 있습니다")

    name_groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
    name_prefixes = (
        "item.",
        "block.",
        "tombstone.item.",
        "tombstone.block.",
        "tombstone.grave.",
        "effect.",
        "enchantment.",
    )
    for key, value in output.items():
        if not key.startswith(name_prefixes) or any(
            marker in key for marker in (".desc", ".use", ".tooltip")
        ):
            continue
        if isinstance(value, str) and isinstance(english.get(key), str):
            name_groups[value].append((key, english[key]))
    collisions = {
        value: rows
        for value, rows in name_groups.items()
        if len(rows) > 1 and len({source for _, source in rows}) > 1
    }
    if collisions:
        errors.append(f"서로 다른 이름의 한국어 충돌: {collisions}")

    config_option_count = 0
    for name, (expected_hash, expected_count) in EXPECTED_CONFIGS.items():
        path = instance / "config" / name
        if sha256(path) != expected_hash:
            errors.append(f"실제 설정 파일 변경: {name}")
        text = path.read_text(encoding="utf-8-sig")
        count = len(CONFIG_OPTION.findall(text))
        config_option_count += count
        if count != expected_count:
            errors.append(f"설정 옵션 수 변경: {name}={count}")

    quest_files = sorted((instance / "config/ftbquests/quests").rglob("*.snbt"))
    quest_references = {
        path.relative_to(instance).as_posix()
        for path in quest_files
        if DIRECT_REFERENCE.search(path.read_text(encoding="utf-8-sig"))
    }
    if len(quest_files) != 142 or quest_references != EXPECTED_QUEST_REFERENCES:
        errors.append(f"Corail Tombstone FTB Quests 참조 범위 변경: {quest_references}")

    quest_output = parse_language_snbt(QUEST_OUTPUT)
    quest_desc = quest_output.get("quest.47043AF7D1FABC43.quest_desc")
    if not isinstance(quest_desc, list) or not any(
        "Corail Tombstone 마법 해제의 책" in value
        and "장식 무덤" in value
        and "무덤 영혼" in value
        and "주 손" in value
        for value in quest_desc
        if isinstance(value, str)
    ):
        errors.append("Corail Tombstone 마법 해제 퀘스트 교정값이 없습니다")
    if quest_output.get("quest.573BC5360C5CA675.title") != "무덤 벌":
        errors.append("Productive Bees 연동 퀘스트 제목이 '무덤 벌'이 아닙니다")
    for path in RELATED_QUEST_COPIES:
        text = path.read_text(encoding="utf-8")
        if "Corail Tombstone 마법 해제의 책" not in text or "주 손" not in text:
            errors.append(f"관련 퀘스트 복사본 교정 누락: {path}")

    productive_working = load_json_path(PRODUCTIVE_WORKING)
    productive_output = load_json_path(PRODUCTIVE_OUTPUT)
    productive_quest = load_json_path(PRODUCTIVE_QUEST)
    if (
        productive_working.get("entity.productivebees.grave_bee") != "무덤 벌"
        or productive_output.get("entity.productivebees.grave_bee") != "무덤 벌"
        or productive_quest.get("quest.573BC5360C5CA675.title") != "무덤 벌"
    ):
        errors.append("Productive Bees 'Grave's Bee' 연동 교정값이 다릅니다")

    kube_files = find_related_files(instance / "kubejs")
    kube_references = {
        path.relative_to(instance).as_posix()
        for path in kube_files
        if DIRECT_REFERENCE.search(path.read_text(encoding="utf-8-sig"))
    }
    if len(kube_files) != 892 or kube_references != EXPECTED_KUBE_REFERENCES:
        errors.append(f"Corail Tombstone KubeJS 참조 범위 변경: {kube_references}")

    jar_count, installed_language_files, owner_conflicts = verify_other_language_owners(
        instance, source_jar, english, errors
    )
    project_language_files = sorted(
        (PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets").glob(
            "*/lang/ko_kr.json"
        )
    )
    if len(project_language_files) != 285:
        errors.append(f"프로젝트 언어 파일 수 변경: {len(project_language_files)}")

    glossary_text = GLOSSARY.read_text(encoding="utf-8")
    for row in GLOSSARY_ROWS:
        if row not in glossary_text:
            errors.append(f"Corail Tombstone 용어집 행 누락: {row}")

    output_sha256 = sha256(OUTPUT)
    productive_sha256 = sha256(PRODUCTIVE_OUTPUT)
    if not pre_apply:
        report = load_json_path(REPORT)
        language_review = report.get("language_review")
        if report.get("validation") != "passed":
            errors.append("Corail Tombstone 재검수 보고서 상태가 passed가 아닙니다")
        if (
            not isinstance(language_review, dict)
            or language_review.get("project_candidates_retained") != 860
            or language_review.get("project_candidates_corrected") != 373
        ):
            errors.append("Corail Tombstone 재검수 보고서 번역 집계 불일치")
        application = report.get("application")
        if (
            not isinstance(application, dict)
            or application.get("status") != "applied_and_verified"
            or application.get("tombstone_sha256") != output_sha256
            or application.get("productivebees_sha256") != productive_sha256
            or application.get("unexpected_changes") != 0
        ):
            errors.append("Corail Tombstone 재검수 보고서 적용 집계 불일치")
        target_tombstone = (
            instance / "resourcepacks/ATM10_Korean/assets/tombstone/lang/ko_kr.json"
        )
        target_productive = (
            instance
            / "resourcepacks/ATM10_Korean/assets/productivebees/lang/ko_kr.json"
        )
        if (
            not target_tombstone.exists()
            or target_tombstone.read_bytes() != OUTPUT.read_bytes()
        ):
            errors.append("실제 source_root의 Corail Tombstone 산출물이 다릅니다")
        if (
            not target_productive.exists()
            or target_productive.read_bytes() != PRODUCTIVE_OUTPUT.read_bytes()
        ):
            errors.append("실제 source_root의 Productive Bees 연동 산출물이 다릅니다")

    if errors:
        raise RuntimeError(
            "Corail Tombstone 재검수 검증 실패:\n" + "\n".join(errors[:80])
        )
    return {
        "scope": "Corail Tombstone 전체 번역 재검수",
        "source_jar": source_jar.name,
        "source_jar_sha256": source_sha256,
        "source_jar_bytes": source_jar.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(class_files),
        "source_keys_reviewed": len(english),
        "bundled_korean_candidates_reviewed": 0,
        "project_candidates_retained": len(english) - len(overrides),
        "project_candidates_corrected": len(overrides),
        "newly_translated": 0,
        "effective_output_keys": len(output),
        "class_referenced_language_keys": len(class_references),
        "configuration_options_reviewed": config_option_count,
        "advancement_files_reviewed": len(advancement_files),
        "recipe_files_reviewed": len(recipe_files),
        "loot_table_files_reviewed": len(loot_files),
        "tag_files_reviewed": len(tag_files),
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_reference_files": len(quest_references),
        "ftbquests_keys_corrected": 2,
        "kubejs_files_reviewed": len(kube_files),
        "kubejs_reference_files": len(kube_references),
        "installed_mod_jars_reviewed": jar_count,
        "installed_english_language_files_reviewed": installed_language_files,
        "other_language_owner_conflicts": owner_conflicts,
        "project_language_files_reviewed": len(project_language_files),
        "harmful_name_collisions": len(collisions),
        "related_productivebees_values_corrected": 2,
        "glossary_terms_added": len(GLOSSARY_ROWS),
        "output_sha256": output_sha256,
        "productivebees_sha256": productive_sha256,
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
