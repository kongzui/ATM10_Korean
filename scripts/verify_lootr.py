#!/usr/bin/env python3
"""Lootr 전체 번역과 설정·발전 과제·연동 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

WORK_ROOT = PROJECT_ROOT / "working/common_ui/convenience/lootr"
WORKING = WORK_ROOT / "ko_kr.json"
OVERRIDES = WORK_ROOT / "recheck_overrides.json"
REPORT = WORK_ROOT / "recheck_20260820.json"
OUTPUT = active_output_root() / "resourcepack/ATM10_Korean/assets/lootr/lang/ko_kr.json"
BUMBLE_WORKING = PROJECT_ROOT / "working/bumblezone/the_bumblezone/ko_kr.json"
BUMBLE_OUTPUT = (
    active_output_root()
    / "resourcepack/ATM10_Korean/assets/the_bumblezone/lang/ko_kr.json"
)
GLOSSARY = PROJECT_ROOT / "glossary/README.md"

EXPECTED_JAR = "lootr-neoforge-1.21.1-1.11.37.120.jar"
EXPECTED_JAR_SHA256 = "f7b80bf86e02a1107fb1600aa6a02608ebcddb140b123a42d5ee199e5db65c8d"
EXPECTED_OVERRIDE_SHA256 = (
    "41e9b002346b8743f08bd97c92087ed030fc6f80eab013092dc8c81d7083feb0"
)
EXPECTED_CONFIGS = {
    "lootr-client.toml": (
        "4da5bc00c2cc7db774e16f6905929303bfca802367d49133ba9742a6330238ad",
        3,
    ),
    "lootr-common.toml": (
        "cb848383f0abff383a96a6cbf59bb91135cce38cb71711f3ffe5baca20fabf9a",
        48,
    ),
}
EXPECTED_UNTRANSLATED = {
    "itemGroup.lootr",
    "itemGroup.lootr.lootr",
    "lootr.advancements.root.title",
    "lootr.commands.blockpos",
    "lootr.commands.usage",
    "text.autoconfig.lootr.title",
}
EXPECTED_KUBE_REFERENCES = {
    "kubejs/assets/the_bumblezone/lang/ru_ru.json",
}
BUMBLE_VALUES = {
    "the_bumblezone.midnightconfig.allowLootrCompat": "전리품 꿀 고치의 Lootr 호환 허용",
    "the_bumblezone.configuration.lootrcompat": "Lootr 호환",
    "the_bumblezone.configuration.allowlootrcompat": "Lootr 꿀 고치",
    "the_bumblezone.configuration.allowlootrcompat.tooltip": (
        "전리품 꿀 고치가 Lootr와 호환되게 합니다."
    ),
}
GLOSSARY_ROWS = (
    "| Lootr | Lootr | 공식 모드명 |",
    "| Lootr Container | 전리품 보관함 | 블록·개체 분류명 |",
    "| Instanced Loot | 개인별 전리품 | 기능명 |",
    "| Decay (Lootr) | 붕괴 | 기능·설정 용어 |",
    "| Structure Piece | 구조물 조각 | 구조물 판정 용어 |",
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
CONFIG_OPTION = re.compile(r"^\s*[A-Za-z0-9_]+\s*=", re.MULTILINE)
OTHER_ENGLISH_LANGUAGE = re.compile(r"assets/[^/]+/lang/en_us\.json")
DIRECT_REFERENCE = re.compile(r"(?i)\blootr\b|lootr:")
RELATED_EXTENSIONS = {".js", ".json", ".snbt", ".toml", ".txt"}
FORBIDDEN_TRANSLATIONS = re.compile(
    r"전리품 컨테이너|Lootr 컨테이너|당신의 첫|블록과 엔티티|이 엔티티|"
    r"보관함과 엔티티|저장 용기|새로고침 되|장식된 전리품 단지|100상자|"
    r"틱 시간이 흐르는 동안 새로고침|각 구조물에서 확인 작업 수행|"
    r"비교기에 신호 공급|플레이어의 전리품이 나옴|겉날개 아이템이 있는 프레임|"
    r"부식|컨테이터|덫상자로써|텍스쳐|블랙리스트|화이트리스트"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json_bytes(data: bytes, label: str) -> dict[str, str]:
    duplicates: list[str] = []

    def reject_duplicate(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        return result

    value = json.loads(data.decode("utf-8-sig"), object_pairs_hook=reject_duplicate)
    if duplicates:
        raise ValueError(f"중복 JSON 키: {label}: {sorted(set(duplicates))}")
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise TypeError(f"문자열 언어 객체가 아닙니다: {label}")
    return value


def load_json_path(path: Path) -> dict[str, str]:
    return load_json_bytes(path.read_bytes(), str(path))


def load_external_language(data: bytes, label: str) -> dict[str, str]:
    """다른 모드의 메타 주석 중복은 허용하고 문자열 언어 값만 비교한다."""
    value = json.loads(data.decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"다른 모드 언어 파일이 객체가 아닙니다: {label}")
    return {
        key: item
        for key, item in value.items()
        if isinstance(key, str) and isinstance(item, str)
    }


def find_related_files(root: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in RELATED_EXTENSIONS
        ),
        key=lambda path: path.as_posix(),
    )


def direct_reference_files(root: Path, files: list[Path]) -> set[str]:
    references = set()
    for path in files:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if DIRECT_REFERENCE.search(text):
            references.add(path.relative_to(root).as_posix())
    return references


def verify_language_owners(instance: Path, english: dict[str, str]) -> tuple[int, int]:
    language_count = 0
    conflicts: list[str] = []
    jar_count = 0
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        jar_count += 1
        try:
            with ZipFile(jar_path) as archive:
                for name in archive.namelist():
                    if not OTHER_ENGLISH_LANGUAGE.fullmatch(name):
                        continue
                    language_count += 1
                    other = load_external_language(
                        archive.read(name), f"{jar_path.name}:{name}"
                    )
                    if name == "assets/lootr/lang/en_us.json":
                        continue
                    for key in set(english) & set(other):
                        if english[key] != other[key]:
                            conflicts.append(f"{jar_path.name}:{name}:{key}")
        except BadZipFile as error:
            raise RuntimeError(f"손상된 모드 JAR: {jar_path}") from error
    if conflicts:
        raise RuntimeError(f"다른 언어 소유자 충돌: {conflicts[:20]}")
    return jar_count, language_count


def harmful_name_collisions(
    english: dict[str, str], korean: dict[str, str]
) -> list[tuple[str, list[str]]]:
    prefixes = ("block.lootr.", "entity.lootr.")
    grouped: defaultdict[str, list[str]] = defaultdict(list)
    for key, value in korean.items():
        if key.startswith(prefixes):
            grouped[value].append(key)
    collisions = []
    for value, keys in grouped.items():
        if len(keys) > 1 and len({english[key] for key in keys}) > 1:
            collisions.append((value, sorted(keys)))
    return collisions


def verify(pre_apply: bool) -> dict[str, object]:
    instance = resolve_source_root(None)
    errors: list[str] = []
    source_jar = instance / "mods" / EXPECTED_JAR
    if not source_jar.is_file():
        raise FileNotFoundError(f"Lootr JAR이 없습니다: {source_jar}")
    if sha256(source_jar) != EXPECTED_JAR_SHA256:
        errors.append("Lootr 원본 JAR 해시가 변경되었습니다")

    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        english = load_json_bytes(
            archive.read("assets/lootr/lang/en_us.json"), "Lootr en_us"
        )
        bundled = load_json_bytes(
            archive.read("assets/lootr/lang/ko_kr.json"), "Lootr ko_kr"
        )
        class_files = [name for name in names if name.endswith(".class")]
        class_bytes = [archive.read(name) for name in class_files]
        class_references = {
            key
            for key in english
            if any(key.encode("utf-8") in data for data in class_bytes)
        }
        language_files = [
            name
            for name in names
            if name.startswith("assets/lootr/lang/") and name.endswith(".json")
        ]
        advancement_files = [
            name
            for name in names
            if name.startswith("data/lootr/advancement/") and name.endswith(".json")
        ]
        loot_files = [
            name
            for name in names
            if name.startswith("data/lootr/loot_table/") and name.endswith(".json")
        ]
        tag_files = [
            name for name in names if "/tags/" in name and name.endswith(".json")
        ]
        guide_files = [
            name
            for name in names
            if any(part in name.lower() for part in ("patchouli", "guideme", "manual"))
        ]

    working = load_json_path(WORKING)
    output = load_json_path(OUTPUT)
    overrides = load_json_path(OVERRIDES)
    if len(names) != 703 or len(class_files) != 308 or len(language_files) != 32:
        errors.append("Lootr JAR 엔트리·클래스·언어 파일 수가 변경되었습니다")
    if len(english) != 217 or len(bundled) != 217:
        errors.append("Lootr 영어 또는 내장 한국어 키 수가 변경되었습니다")
    if set(working) != set(english) or set(output) != set(english):
        errors.append("Lootr 작업본 또는 산출물 키 집합이 영어 원문과 다릅니다")
    if working != output:
        errors.append("Lootr 작업본과 산출물이 다릅니다")
    if len(overrides) != 52 or sha256(OVERRIDES) != EXPECTED_OVERRIDE_SHA256:
        errors.append("Lootr 재검수 교정표 수 또는 해시가 다릅니다")
    for key, value in overrides.items():
        if output.get(key) != value:
            errors.append(f"Lootr 교정표가 산출물에 반영되지 않음: {key}")
    untranslated = {key for key in english if english[key] == output[key]}
    if untranslated != EXPECTED_UNTRANSLATED:
        errors.append(f"Lootr 원문 유지 키가 다릅니다: {sorted(untranslated)}")
    for key in english:
        if PLACEHOLDER.findall(english[key]) != PLACEHOLDER.findall(output[key]):
            errors.append(f"자리표시자 불일치: {key}")
        if english[key].count("\n") != output[key].count("\n"):
            errors.append(f"줄바꿈 불일치: {key}")
        if Counter(FORMAT_CODE.findall(english[key])) != Counter(
            FORMAT_CODE.findall(output[key])
        ):
            errors.append(f"서식 코드 불일치: {key}")
    forbidden = FORBIDDEN_TRANSLATIONS.findall("\n".join(output.values()))
    if forbidden:
        errors.append(f"Lootr 금지 번역 잔존: {sorted(set(forbidden))}")
    collisions = harmful_name_collisions(english, output)
    if collisions:
        errors.append(f"Lootr 이름 충돌: {collisions}")
    if len(class_references) != 170:
        errors.append(f"Lootr 클래스 참조 언어 키 수 변경: {len(class_references)}")
    if (
        len(advancement_files) != 14
        or len(loot_files) != 9
        or len(tag_files) != 56
        or guide_files
    ):
        errors.append("Lootr 발전 과제·전리품 표·태그·가이드 경로 수가 다릅니다")

    config_option_count = 0
    for name, (expected_hash, expected_count) in EXPECTED_CONFIGS.items():
        path = instance / "config" / name
        text = path.read_text(encoding="utf-8-sig")
        count = len(CONFIG_OPTION.findall(text))
        config_option_count += count
        if sha256(path) != expected_hash or count != expected_count:
            errors.append(f"Lootr 설정 스냅샷 불일치: {name}")
    common_config = (instance / "config/lootr-common.toml").read_text(
        encoding="utf-8-sig"
    )
    for phrase in (
        "checks structure pieces as well as structure starts",
        "player-specific inventory",
        "already been marked as refreshing",
        "will be marked for refresh during level tick",
    ):
        if phrase not in common_config:
            errors.append(f"Lootr 설정 의미 근거 누락: {phrase}")

    quest_root = instance / "config/ftbquests/quests"
    quest_files = find_related_files(quest_root)
    quest_references = direct_reference_files(instance, quest_files)
    if len(quest_files) != 142 or quest_references:
        errors.append(
            "Lootr FTB Quests 참조 집계 불일치: "
            f"files={len(quest_files)}, refs={sorted(quest_references)}"
        )

    kube_files = find_related_files(instance / "kubejs")
    kube_references = direct_reference_files(instance, kube_files)
    if len(kube_files) != 892 or kube_references != EXPECTED_KUBE_REFERENCES:
        errors.append(
            "Lootr KubeJS 참조 집계 불일치: "
            f"files={len(kube_files)}, refs={sorted(kube_references)}"
        )
    for path in (BUMBLE_WORKING, BUMBLE_OUTPUT):
        related = load_json_path(path)
        for key, value in BUMBLE_VALUES.items():
            if related.get(key) != value:
                errors.append(f"The Bumblezone Lootr 연동값 불일치: {path}:{key}")

    jar_count, english_language_count = verify_language_owners(instance, english)
    if jar_count != 480 or english_language_count != 388:
        errors.append(
            "설치 모드 또는 영어 언어 파일 수 변경: "
            f"jars={jar_count}, languages={english_language_count}"
        )
    project_language_files = list(
        (active_output_root() / "resourcepack/ATM10_Korean/assets").glob(
            "*/lang/ko_kr.json"
        )
    )
    if len(project_language_files) != 285:
        errors.append(f"프로젝트 언어 파일 수 변경: {len(project_language_files)}")

    glossary_text = GLOSSARY.read_text(encoding="utf-8")
    for row in GLOSSARY_ROWS:
        if row not in glossary_text:
            errors.append(f"Lootr 용어집 행 누락: {row}")

    output_hash = sha256(OUTPUT)
    if not pre_apply:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        if not isinstance(report, dict):
            raise TypeError("Lootr 재검수 보고서가 JSON 객체가 아닙니다")
        language_review = report.get("language_review")
        if report.get("validation") != "passed":
            errors.append("Lootr 재검수 보고서 상태가 passed가 아닙니다")
        if (
            not isinstance(language_review, dict)
            or language_review.get("project_candidates_retained") != 165
            or language_review.get("project_candidates_corrected") != 52
        ):
            errors.append("Lootr 재검수 보고서 번역 집계 불일치")
        application = report.get("application")
        if (
            not isinstance(application, dict)
            or application.get("status") != "applied_and_verified"
            or application.get("lootr_sha256") != output_hash
            or application.get("unexpected_changes") != 0
        ):
            errors.append("Lootr 재검수 보고서 적용 집계 불일치")
        target = instance / "resourcepacks/ATM10_Korean/assets/lootr/lang/ko_kr.json"
        if not target.exists() or target.read_bytes() != OUTPUT.read_bytes():
            errors.append("실제 source_root의 Lootr 산출물이 다릅니다")

    if errors:
        raise RuntimeError("Lootr 재검수 검증 실패:\n" + "\n".join(errors[:80]))
    return {
        "scope": "Lootr 전체 번역 재검수",
        "source_jar": source_jar.name,
        "source_jar_sha256": sha256(source_jar),
        "source_jar_bytes": source_jar.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(class_files),
        "language_files_reviewed": len(language_files),
        "source_keys_reviewed": len(english),
        "bundled_korean_candidates_reviewed": len(bundled),
        "bundled_korean_candidates_reused": sum(
            output[key] == bundled[key] for key in english
        ),
        "bundled_korean_candidates_rejected": sum(
            output[key] != bundled[key] for key in english
        ),
        "project_candidates_retained": len(english) - len(overrides),
        "project_candidates_corrected": len(overrides),
        "newly_translated": 0,
        "effective_output_keys": len(output),
        "class_referenced_language_keys": len(class_references),
        "configuration_options_reviewed": config_option_count,
        "advancement_files_reviewed": len(advancement_files),
        "loot_table_files_reviewed": len(loot_files),
        "tag_files_reviewed": len(tag_files),
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_reference_files": len(quest_references),
        "kubejs_files_reviewed": len(kube_files),
        "kubejs_reference_files": len(kube_references),
        "related_bumblezone_values_verified": len(BUMBLE_VALUES),
        "installed_mod_jars_reviewed": jar_count,
        "installed_english_language_files_reviewed": english_language_count,
        "other_language_owner_conflicts": 0,
        "project_language_files_reviewed": len(project_language_files),
        "harmful_name_collisions": len(collisions),
        "glossary_terms_added": len(GLOSSARY_ROWS),
        "output_sha256": output_hash,
        "validation": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pre-apply", action="store_true")
    args = parser.parse_args()
    print(json.dumps(verify(args.pre_apply), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
