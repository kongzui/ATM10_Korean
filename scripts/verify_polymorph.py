#!/usr/bin/env python3
"""Polymorph 번역과 Ars Polymorphia·제작법 충돌 연동 경로를 검증한다."""

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

WORK_ROOT = PROJECT_ROOT / "working/common_ui/convenience/polymorph"
WORKING = WORK_ROOT / "ko_kr.json"
OVERRIDES = WORK_ROOT / "recheck_overrides.json"
REPORT = WORK_ROOT / "recheck_20260820.json"
OUTPUT = (
    active_output_root() / "resourcepack/ATM10_Korean/assets/polymorph/lang/ko_kr.json"
)
GLOSSARY = PROJECT_ROOT / "glossary/README.md"

EXPECTED_JAR = "polymorph-neoforge-1.1.0+1.21.1.jar"
EXPECTED_JAR_SHA256 = "bec8118978adeb052de9c4eaf9a595830621d82515a764f32f9c8a4dd52ab94b"
EXPECTED_ARS_JAR = "ars_polymorphia-1.0.3.jar"
EXPECTED_ARS_SHA256 = "2b7724eb346a71b6e395a4ac781c1ecbfe37e6e813811f4aba2df8ff5d7c894d"
EXPECTED_OVERRIDE_SHA256 = (
    "eef46256f8beb2f1c45302ca11b4649c2305f1a716d1d7be260ae996bea3439d"
)
EXPECTED_OUTPUT_SHA256 = (
    "c350e1130c8e2eab5126488d3b166078504c2635d98dda88183a890f07f29f7e"
)
JUST_DIRE_VALUES = {
    "justdirethings.ability.polymorph_random": "무작위 변이",
    "justdirethings.ability.polymorph_target": "대상 지정 변이",
    "justdirethings.polymorphset": "변이 대상: %s",
}
GLOSSARY_ROWS = (
    "| Polymorph | Polymorph | 공식 모드명 |",
    "| Recipe Conflict | 제작법 충돌 | 제작·명령 용어 |",
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
ENGLISH_LANGUAGE = re.compile(r"assets/[^/]+/lang/en_us\.json")
DIRECT_REFERENCE = re.compile(r"(?i)\bpolymorph\b|polymorph:")
RELATED_EXTENSIONS = {".js", ".json", ".snbt", ".toml", ".txt"}
FORBIDDEN_TRANSLATIONS = re.compile(
    r"충돌 가능한 제작법|충돌 가능성이 있는 제작법|네트워크 연결 실패|"
    r"logs/conflicts\.log 를|잠재적인 충돌 가능성"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_language(data: bytes, label: str) -> dict[str, str]:
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


def load_path(path: Path) -> dict[str, str]:
    return load_language(path.read_bytes(), str(path))


def find_related_files(root: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in RELATED_EXTENSIONS
        ),
        key=lambda path: path.as_posix(),
    )


def direct_references(root: Path, files: list[Path]) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in files
        if DIRECT_REFERENCE.search(
            path.read_text(encoding="utf-8-sig", errors="replace")
        )
    }


def verify_language_owners(instance: Path, english: dict[str, str]) -> tuple[int, int]:
    jar_count = 0
    language_count = 0
    conflicts: list[str] = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        jar_count += 1
        try:
            with ZipFile(jar_path) as archive:
                for name in archive.namelist():
                    if not ENGLISH_LANGUAGE.fullmatch(name):
                        continue
                    language_count += 1
                    if name == "assets/polymorph/lang/en_us.json":
                        continue
                    value = json.loads(archive.read(name).decode("utf-8-sig"))
                    if not isinstance(value, dict):
                        continue
                    for key in set(english) & set(value):
                        if isinstance(value[key], str) and english[key] != value[key]:
                            conflicts.append(f"{jar_path.name}:{name}:{key}")
        except BadZipFile as error:
            raise RuntimeError(f"손상된 모드 JAR: {jar_path}") from error
    if conflicts:
        raise RuntimeError(f"다른 언어 소유자 충돌: {conflicts[:20]}")
    return jar_count, language_count


def verify(pre_apply: bool) -> dict[str, object]:
    instance = resolve_source_root(None)
    errors: list[str] = []
    source_jar = instance / "mods" / EXPECTED_JAR
    ars_jar = instance / "mods" / EXPECTED_ARS_JAR
    if sha256(source_jar) != EXPECTED_JAR_SHA256:
        errors.append("Polymorph 원본 JAR 해시가 변경되었습니다")
    if sha256(ars_jar) != EXPECTED_ARS_SHA256:
        errors.append("Ars Polymorphia 원본 JAR 해시가 변경되었습니다")

    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        english = load_language(
            archive.read("assets/polymorph/lang/en_us.json"), "Polymorph en_us"
        )
        bundled = load_language(
            archive.read("assets/polymorph/lang/ko_kr.json"), "Polymorph ko_kr"
        )
        classes = [name for name in names if name.endswith(".class")]
        class_bytes = [archive.read(name) for name in classes]
        class_references = {
            key
            for key in english
            if any(key.encode("utf-8") in data for data in class_bytes)
        }
        language_files = [
            name
            for name in names
            if name.startswith("assets/polymorph/lang/") and name.endswith(".json")
        ]
        data_files = [
            name
            for name in names
            if name.startswith("data/polymorph/") and name.endswith(".json")
        ]
    with ZipFile(ars_jar) as archive:
        ars_names = archive.namelist()
        ars_classes = [name for name in ars_names if name.endswith(".class")]
        ars_display_assets = [
            name
            for name in ars_names
            if "/lang/" in name
            or "advancement" in name
            or "patchouli" in name.lower()
            or "guideme" in name.lower()
        ]

    working = load_path(WORKING)
    output = load_path(OUTPUT)
    overrides = load_path(OVERRIDES)
    if len(names) != 175 or len(classes) != 98 or len(language_files) != 16:
        errors.append("Polymorph JAR 엔트리·클래스·언어 파일 수가 다릅니다")
    if len(ars_names) != 34 or len(ars_classes) != 11 or ars_display_assets:
        errors.append("Ars Polymorphia JAR 표시 자산 집계가 다릅니다")
    if len(english) != 3 or len(bundled) != 2:
        errors.append("Polymorph 영어 또는 내장 한국어 키 수가 다릅니다")
    if set(working) != set(english) or working != output:
        errors.append("Polymorph 작업본·산출물·영어 키 집합이 다릅니다")
    if (
        len(overrides) != 3
        or sha256(OVERRIDES) != EXPECTED_OVERRIDE_SHA256
        or overrides != output
    ):
        errors.append("Polymorph 재검수 교정표가 산출물과 다릅니다")
    if sha256(OUTPUT) != EXPECTED_OUTPUT_SHA256:
        errors.append("Polymorph 산출물 해시가 다릅니다")
    if set(class_references) != set(english) or data_files:
        errors.append("Polymorph 클래스·데이터 표시 경로 집계가 다릅니다")
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
        errors.append(f"Polymorph 금지 번역 잔존: {sorted(set(forbidden))}")

    quest_files = find_related_files(instance / "config/ftbquests/quests")
    quest_refs = direct_references(instance, quest_files)
    kube_files = find_related_files(instance / "kubejs")
    kube_refs = direct_references(instance, kube_files)
    if len(quest_files) != 142 or quest_refs:
        errors.append(f"Polymorph FTB Quests 참조 집계 불일치: {quest_refs}")
    if len(kube_files) != 892 or kube_refs:
        errors.append(f"Polymorph KubeJS 참조 집계 불일치: {kube_refs}")

    for path in (
        PROJECT_ROOT / "working/just_dire_things/justdirethings/ko_kr.json",
        active_output_root()
        / "resourcepack/ATM10_Korean/assets/justdirethings/lang/ko_kr.json",
    ):
        related = load_path(path)
        for key, value in JUST_DIRE_VALUES.items():
            if related.get(key) != value:
                errors.append(f"Just Dire Things 변이 용어 불일치: {path}:{key}")

    jar_count, english_count = verify_language_owners(instance, english)
    project_languages = list(
        (active_output_root() / "resourcepack/ATM10_Korean/assets").glob(
            "*/lang/ko_kr.json"
        )
    )
    if jar_count != 480 or english_count != 388 or len(project_languages) != 285:
        errors.append(
            "설치·프로젝트 언어 집계 변경: "
            f"jars={jar_count}, english={english_count}, project={len(project_languages)}"
        )
    glossary = GLOSSARY.read_text(encoding="utf-8")
    for row in GLOSSARY_ROWS:
        if row not in glossary:
            errors.append(f"Polymorph 용어집 행 누락: {row}")

    if not pre_apply:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        if not isinstance(report, dict) or report.get("validation") != "passed":
            errors.append("Polymorph 재검수 보고서 상태 불일치")
        application = report.get("application") if isinstance(report, dict) else None
        if (
            not isinstance(application, dict)
            or application.get("status") != "applied_and_verified"
            or application.get("polymorph_sha256") != EXPECTED_OUTPUT_SHA256
            or application.get("unexpected_changes") != 0
        ):
            errors.append("Polymorph 재검수 보고서 적용 집계 불일치")
        target = (
            instance / "resourcepacks/ATM10_Korean/assets/polymorph/lang/ko_kr.json"
        )
        if not target.exists() or target.read_bytes() != OUTPUT.read_bytes():
            errors.append("실제 source_root의 Polymorph 산출물이 다릅니다")

    if errors:
        raise RuntimeError("Polymorph 재검수 검증 실패:\n" + "\n".join(errors[:80]))
    return {
        "scope": "Polymorph 전체 번역 재검수",
        "source_jar": source_jar.name,
        "source_jar_sha256": sha256(source_jar),
        "source_jar_bytes": source_jar.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(classes),
        "language_files_reviewed": len(language_files),
        "source_keys_reviewed": len(english),
        "bundled_korean_candidates_reviewed": len(bundled),
        "bundled_korean_candidates_reused": sum(
            output.get(key) == value for key, value in bundled.items()
        ),
        "bundled_korean_candidates_rejected": sum(
            output.get(key) != value for key, value in bundled.items()
        ),
        "project_candidates_retained": 0,
        "project_candidates_corrected": len(overrides),
        "newly_translated": 0,
        "effective_output_keys": len(output),
        "class_referenced_language_keys": len(class_references),
        "ars_polymorphia_entries_reviewed": len(ars_names),
        "ars_polymorphia_class_files_reviewed": len(ars_classes),
        "ars_polymorphia_display_assets": len(ars_display_assets),
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_reference_files": len(quest_refs),
        "kubejs_files_reviewed": len(kube_files),
        "kubejs_reference_files": len(kube_refs),
        "just_dire_things_related_values_verified": len(JUST_DIRE_VALUES),
        "installed_mod_jars_reviewed": jar_count,
        "installed_english_language_files_reviewed": english_count,
        "other_language_owner_conflicts": 0,
        "project_language_files_reviewed": len(project_languages),
        "glossary_terms_added": len(GLOSSARY_ROWS),
        "output_sha256": sha256(OUTPUT),
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
