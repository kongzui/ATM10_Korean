#!/usr/bin/env python3
"""Controlling 번역과 단축키 필터·정렬 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root

WORK_ROOT = PROJECT_ROOT / "working/common_ui/inventory_controls/controlling"
WORKING = WORK_ROOT / "ko_kr.json"
OVERRIDES = WORK_ROOT / "recheck_overrides.json"
REPORT = WORK_ROOT / "recheck_20260820.json"
OUTPUT = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/controlling/lang/ko_kr.json"
)
GLOSSARY = PROJECT_ROOT / "glossary/README.md"

EXPECTED_JAR = "Controlling-neoforge-1.21.1-19.0.5.jar"
EXPECTED_JAR_SHA256 = "cc525fb6b030d9e4d33176983f278919e17b33935e2ca568929bdfa98f2b44a0"
EXPECTED_OVERRIDE_SHA256 = (
    "8febf3dc36658a32a3c7a611ae31bd14ab3eceeb849da10fa70960da08b1f8b2"
)
EXPECTED_OUTPUT_SHA256 = (
    "c901c83420140a792dca200fef1669f807d78a281d3f14aba84490197fe3d988"
)
GLOSSARY_ROWS = (
    "| Controlling | Controlling | 공식 모드명 |",
    "| Unbound Key Mapping | 미할당 단축키 | 키 설정 UI 용어 |",
    "| Available Key | 미사용 키 | 키 설정 UI 용어 |",
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
ENGLISH_LANGUAGE = re.compile(r"assets/[^/]+/lang/en_us\.json")
DIRECT_REFERENCE = re.compile(
    r"(?i)controlling:|assets/controlling|mods[./\\]controlling"
)
RELATED_EXTENSIONS = {".js", ".json", ".snbt", ".toml", ".txt"}
FORBIDDEN_TRANSLATIONS = re.compile(
    r"미할당 키 표시|사용 가능한 키|키 A->Z|키 Z->A|미할당 키 전환|"
    r"충돌 표시|모두 표시"
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


def verify_language_owners(
    instance: Path, english: dict[str, str]
) -> tuple[int, int, int]:
    jar_count = 0
    language_count = 0
    overlaps: list[str] = []
    for jar_path in sorted((instance / "mods").glob("*.jar")):
        jar_count += 1
        try:
            with ZipFile(jar_path) as archive:
                for name in archive.namelist():
                    if not ENGLISH_LANGUAGE.fullmatch(name):
                        continue
                    language_count += 1
                    if name == "assets/controlling/lang/en_us.json":
                        continue
                    value = json.loads(archive.read(name).decode("utf-8-sig"))
                    if isinstance(value, dict):
                        for key in set(english) & set(value):
                            overlaps.append(f"{jar_path.name}:{name}:{key}")
        except BadZipFile as error:
            raise RuntimeError(f"손상된 모드 JAR: {jar_path}") from error
    if overlaps:
        raise RuntimeError(f"Controlling 공통 키 소유자 중복: {overlaps[:20]}")
    return jar_count, language_count, len(overlaps)


def verify(pre_apply: bool) -> dict[str, object]:
    instance = resolve_source_root(None)
    errors: list[str] = []
    source_jar = instance / "mods" / EXPECTED_JAR
    if sha256(source_jar) != EXPECTED_JAR_SHA256:
        errors.append("Controlling 원본 JAR 해시가 변경되었습니다")
    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        english = load_language(
            archive.read("assets/controlling/lang/en_us.json"), "Controlling en_us"
        )
        bundled = load_language(
            archive.read("assets/controlling/lang/ko_kr.json"), "Controlling ko_kr"
        )
        classes = [name for name in names if name.endswith(".class")]
        class_bytes = [archive.read(name) for name in classes]
        class_keys = {
            key
            for key in english
            if any(key.encode("utf-8") in data for data in class_bytes)
        }
        language_files = [
            name
            for name in names
            if name.startswith("assets/controlling/lang/") and name.endswith(".json")
        ]
        data_files = [
            name
            for name in names
            if name.startswith("data/controlling/") and name.endswith(".json")
        ]
        free_list = archive.read(
            "com/blamejared/controlling/client/FreeKeysList$HeaderEntry.class"
        )
        constants = archive.read(
            "com/blamejared/controlling/ControllingConstants.class"
        )

    working = load_path(WORKING)
    output = load_path(OUTPUT)
    overrides = load_path(OVERRIDES)
    if len(names) != 92 or len(classes) != 42 or len(language_files) != 24:
        errors.append("Controlling JAR 엔트리·클래스·언어 파일 수 불일치")
    if len(english) != 12 or len(bundled) != 10:
        errors.append("Controlling 영어 또는 내장 한국어 키 수 불일치")
    if set(working) != set(english) or working != output:
        errors.append("Controlling 작업본·산출물·영어 키 집합 불일치")
    if (
        len(overrides) != 12
        or overrides != output
        or sha256(OVERRIDES) != EXPECTED_OVERRIDE_SHA256
        or sha256(OUTPUT) != EXPECTED_OUTPUT_SHA256
    ):
        errors.append("Controlling 교정표 또는 산출물 수·값·해시 불일치")
    if class_keys != set(english) or data_files:
        errors.append("Controlling 클래스 언어 키 또는 데이터 표시 경로 불일치")
    if (
        b"COMPONENT_OPTIONS_AVAILABLE_KEYS" not in free_list
        or b"options.availableKeys" not in constants
    ):
        errors.append("Controlling 미사용 키 제목 번역 호출 경로 누락")
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
        errors.append(f"Controlling 금지 번역 잔존: {sorted(set(forbidden))}")
    if not all(
        "→" in output[key]
        for key in (
            "options.sortAZ",
            "options.sortZA",
            "options.sortKeyAZ",
            "options.sortKeyZA",
        )
    ):
        errors.append("Controlling 정렬 방향 기호 누락")

    quest_files = find_related_files(instance / "config/ftbquests/quests")
    quest_refs = direct_references(instance, quest_files)
    kube_files = find_related_files(instance / "kubejs")
    kube_refs = direct_references(instance, kube_files)
    if len(quest_files) != 142 or quest_refs:
        errors.append(f"Controlling FTB Quests 직접 참조 불일치: {quest_refs}")
    if len(kube_files) != 892 or kube_refs:
        errors.append(f"Controlling KubeJS 직접 참조 불일치: {kube_refs}")

    jar_count, english_count, owner_overlaps = verify_language_owners(instance, english)
    project_languages = list(
        (PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets").glob(
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
            errors.append(f"Controlling 용어집 행 누락: {row}")

    if not pre_apply:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        if not isinstance(report, dict) or report.get("validation") != "passed":
            errors.append("Controlling 재검수 보고서 상태 불일치")
        application = report.get("application") if isinstance(report, dict) else None
        if (
            not isinstance(application, dict)
            or application.get("status") != "applied_and_verified"
            or application.get("controlling_sha256") != EXPECTED_OUTPUT_SHA256
            or application.get("unexpected_changes") != 0
        ):
            errors.append("Controlling 재검수 보고서 적용 집계 불일치")
        target = (
            instance / "resourcepacks/ATM10_Korean/assets/controlling/lang/ko_kr.json"
        )
        if not target.exists() or target.read_bytes() != OUTPUT.read_bytes():
            errors.append("실제 source_root의 Controlling 산출물이 다릅니다")

    if errors:
        raise RuntimeError("Controlling 재검수 검증 실패:\n" + "\n".join(errors[:80]))
    return {
        "scope": "Controlling 전체 번역 재검수",
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
        "class_referenced_language_keys": len(class_keys),
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_reference_files": len(quest_refs),
        "kubejs_files_reviewed": len(kube_files),
        "kubejs_reference_files": len(kube_refs),
        "installed_mod_jars_reviewed": jar_count,
        "installed_english_language_files_reviewed": english_count,
        "other_language_owner_overlaps": owner_overlaps,
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
