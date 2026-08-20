#!/usr/bin/env python3
"""Better Advancements 번역과 발전 과제 화면 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root

WORK_ROOT = PROJECT_ROOT / "working/common_ui/inventory_controls/betteradvancements"
WORKING = WORK_ROOT / "ko_kr.json"
OVERRIDES = WORK_ROOT / "recheck_overrides.json"
REPORT = WORK_ROOT / "recheck_20260820.json"
OUTPUT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/betteradvancements/lang/ko_kr.json"
)
GLOSSARY = PROJECT_ROOT / "glossary/README.md"

EXPECTED_JAR = "BetterAdvancements-NeoForge-1.21.1-0.4.3.21.jar"
EXPECTED_JAR_SHA256 = "60b548bef04a2f0e1da686ee9035c2e3d4ed0459a17d7a4836fc26af6de6b60e"
EXPECTED_CONFIG_SHA256 = (
    "38e88509078026a5a660e00947e5a6db74a3c374c8c7978ef64c360167f84db9"
)
EXPECTED_OVERRIDE_SHA256 = (
    "ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356"
)
EXPECTED_OUTPUT_SHA256 = (
    "ef8a38beb7df2a2fbd2785f7ed364bdc4dd88a6f1b96749a1070738035cbbefd"
)
GLOSSARY_ROW = "| Better Advancements | Better Advancements | 공식 모드명 |"
EXPECTED_CONFIG_OPTIONS = {
    "addInventoryButton",
    "criteriaDetail",
    "criteriaDetailRequiresShift",
    "defaultCompletedIconColor",
    "defaultCompletedLineColor",
    "defaultCompletedTitleColor",
    "defaultDrawDirectLines",
    "defaultHideLines",
    "defaultUncompletedIconColor",
    "defaultUncompletedLineColor",
    "defaultUncompletedTitleColor",
    "doAdvancementsBackgroundFade",
    "onlyUseAboveAdvancementTabs",
    "orderTabsAlphabetically",
    "showDebugCoordinates",
    "uiScaling",
}
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
ENGLISH_LANGUAGE = re.compile(r"assets/[^/]+/lang/en_us\.json")
DIRECT_REFERENCE = re.compile(
    r"(?i)betteradvancements(?:[.:/\\]|\b)|better advancements"
)
RELATED_EXTENSIONS = {".js", ".json", ".snbt", ".toml", ".txt"}


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
    result: set[str] = set()
    for path in files:
        relative = path.relative_to(root).as_posix()
        content = path.read_text(encoding="utf-8-sig", errors="replace")
        if DIRECT_REFERENCE.search(relative) or DIRECT_REFERENCE.search(content):
            result.add(relative)
    return result


def config_options(path: Path) -> set[str]:
    options: set[str] = set()
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            options.add(stripped.split("=", 1)[0].strip())
    return options


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
                    if name == "assets/betteradvancements/lang/en_us.json":
                        continue
                    value = json.loads(archive.read(name).decode("utf-8-sig"))
                    if isinstance(value, dict):
                        for key in set(english) & set(value):
                            overlaps.append(f"{jar_path.name}:{name}:{key}")
        except BadZipFile as error:
            raise RuntimeError(f"손상된 모드 JAR: {jar_path}") from error
    if overlaps:
        raise RuntimeError(f"Better Advancements 언어 키 소유자 중복: {overlaps[:20]}")
    return jar_count, language_count, len(overlaps)


def verify(pre_apply: bool) -> dict[str, object]:
    instance = resolve_source_root(None)
    errors: list[str] = []
    source_jar = instance / "mods" / EXPECTED_JAR
    config = instance / "config/betteradvancements-client.toml"
    if sha256(source_jar) != EXPECTED_JAR_SHA256:
        errors.append("Better Advancements 원본 JAR 해시가 변경되었습니다")
    if sha256(config) != EXPECTED_CONFIG_SHA256:
        errors.append("Better Advancements 클라이언트 설정 해시가 변경되었습니다")

    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        english = load_language(
            archive.read("assets/betteradvancements/lang/en_us.json"),
            "Better Advancements en_us",
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
            if name.startswith("assets/betteradvancements/lang/")
            and name.endswith(".json")
        ]
        korean_files = [name for name in language_files if name.endswith("/ko_kr.json")]
        data_files = [
            name
            for name in names
            if name.startswith("data/betteradvancements/") and name.endswith(".json")
        ]
        guide_files = [
            name
            for name in names
            if any(
                token in name.lower()
                for token in ("patchouli", "guideme", "modonomicon")
            )
        ]
        compatibility = json.loads(
            archive.read(
                "assets/betteradvancements/load_screens/pga_compat.json"
            ).decode("utf-8")
        )

    working = load_path(WORKING)
    output = load_path(OUTPUT)
    overrides = load_path(OVERRIDES)
    if len(names) != 72 or len(classes) != 36 or len(language_files) != 2:
        errors.append("Better Advancements JAR 엔트리·클래스·언어 파일 수 불일치")
    if english != {"betteradvancements.remaining": "%d remaining"}:
        errors.append("Better Advancements 영어 원문이 변경되었습니다")
    if korean_files:
        errors.append(f"예상하지 못한 내장 한국어 파일: {korean_files}")
    if working != output or set(output) != set(english):
        errors.append("Better Advancements 작업본·산출물·영어 키 집합 불일치")
    if output != {"betteradvancements.remaining": "완료까지 %d개 남음"}:
        errors.append("Better Advancements 확정 번역 불일치")
    if (
        overrides
        or sha256(OVERRIDES) != EXPECTED_OVERRIDE_SHA256
        or sha256(OUTPUT) != EXPECTED_OUTPUT_SHA256
    ):
        errors.append("Better Advancements 교정표 또는 산출물 해시 불일치")
    if class_keys != set(english) or data_files or guide_files:
        errors.append("Better Advancements 표시·데이터·가이드 경로 불일치")
    if compatibility != {
        "screens": [
            {
                "COMMENT": "BETTER ADVANCEMENTS SUPPORT",
                "class": "betteradvancements.gui.BetterAdvancementsScreen",
                "texture": "publicguiannouncement:textures/gui/advancements_menu.png",
                "fullSize": 255,
            }
        ]
    }:
        errors.append("Public GUI Announcement 호환 화면 정의 불일치")
    if config_options(config) != EXPECTED_CONFIG_OPTIONS:
        errors.append("Better Advancements 설정 옵션 집합 불일치")
    for key in english:
        if PLACEHOLDER.findall(english[key]) != PLACEHOLDER.findall(output[key]):
            errors.append(f"자리표시자 불일치: {key}")
        if english[key].count("\n") != output[key].count("\n"):
            errors.append(f"줄바꿈 불일치: {key}")
        if Counter(FORMAT_CODE.findall(english[key])) != Counter(
            FORMAT_CODE.findall(output[key])
        ):
            errors.append(f"서식 코드 불일치: {key}")

    quest_files = find_related_files(instance / "config/ftbquests/quests")
    quest_refs = direct_references(instance, quest_files)
    kube_files = find_related_files(instance / "kubejs")
    kube_refs = direct_references(instance, kube_files)
    expected_kube_refs = {"kubejs/assets/betteradvancements/lang/ru_ru.json"}
    if len(quest_files) != 142 or quest_refs:
        errors.append(f"Better Advancements FTB Quests 직접 참조 불일치: {quest_refs}")
    if len(kube_files) != 892 or kube_refs != expected_kube_refs:
        errors.append(f"Better Advancements KubeJS 직접 참조 불일치: {kube_refs}")

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
    if GLOSSARY_ROW not in GLOSSARY.read_text(encoding="utf-8"):
        errors.append("Better Advancements 용어집 행 누락")

    if not pre_apply:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        if not isinstance(report, dict) or report.get("validation") != "passed":
            errors.append("Better Advancements 재검수 보고서 상태 불일치")
        application = report.get("application") if isinstance(report, dict) else None
        if (
            not isinstance(application, dict)
            or application.get("status") != "applied_and_verified"
            or application.get("betteradvancements_sha256") != EXPECTED_OUTPUT_SHA256
            or application.get("unexpected_changes") != 0
        ):
            errors.append("Better Advancements 재검수 보고서 적용 집계 불일치")
        target = (
            instance
            / "resourcepacks/ATM10_Korean/assets/betteradvancements/lang/ko_kr.json"
        )
        if not target.exists() or target.read_bytes() != OUTPUT.read_bytes():
            errors.append("실제 source_root의 Better Advancements 산출물이 다릅니다")

    if errors:
        raise RuntimeError(
            "Better Advancements 재검수 검증 실패:\n" + "\n".join(errors[:80])
        )
    return {
        "scope": "Better Advancements 전체 번역 재검수",
        "source_jar": source_jar.name,
        "source_jar_sha256": sha256(source_jar),
        "source_jar_bytes": source_jar.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(classes),
        "language_files_reviewed": len(language_files),
        "source_keys_reviewed": len(english),
        "bundled_korean_candidates_reviewed": 0,
        "project_candidates_retained": 1,
        "project_candidates_corrected": 0,
        "newly_translated": 0,
        "effective_output_keys": len(output),
        "class_referenced_language_keys": len(class_keys),
        "configuration_options_reviewed": len(EXPECTED_CONFIG_OPTIONS),
        "compatibility_display_files_reviewed": 1,
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_reference_files": len(quest_refs),
        "kubejs_files_reviewed": len(kube_files),
        "kubejs_reference_files": len(kube_refs),
        "kubejs_korean_display_references": 0,
        "installed_mod_jars_reviewed": jar_count,
        "installed_english_language_files_reviewed": english_count,
        "other_language_owner_overlaps": owner_overlaps,
        "project_language_files_reviewed": len(project_languages),
        "glossary_terms_added": 1,
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
