#!/usr/bin/env python3
"""L_Ender's Cataclysm의 표시 경로와 완성 산출물을 검증한다."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
import cataclysm_family as quality_review
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/cataclysm"
LANG_ROOT = WORK_ROOT / "cataclysm"
LANG_OUTPUT = (
    active_output_root() / "resourcepack/ATM10_Korean/assets/cataclysm/lang/ko_kr.json"
)
QUEST_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
BAD_FRAGMENTS = (
    "네더라이트 괴물",
    "현세의 잔재",
    "바제트",
    "커슘",
    "이그니튬",
    "재성성기",
    "Yuri_0",
    "피해amage",
    "상위 버전으로 변환",
    " get...",
    " Home",
    " Wasteland",
    " much...",
    " though...",
    " propability",
    " boss...",
)


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def sha256(path: Path) -> str:
    """파일의 SHA-256 해시를 계산한다."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_jar(instance: Path) -> Path:
    """현재 설치된 Cataclysm JAR 하나를 찾는다."""
    return family_goal.find_jar(instance, "L_Ender's Cataclysm ")


def verify_language_source(instance: Path) -> tuple[dict[str, object], list[str]]:
    """작업 원문이 현재 설치 JAR의 영어 원문과 같은지 확인한다."""
    jar = find_jar(instance)
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    output = load_json(LANG_OUTPUT)
    with ZipFile(jar) as archive:
        current = json.loads(
            archive.read("assets/cataclysm/lang/en_us.json").decode("utf-8-sig")
        )
    errors = []
    if list(current.items()) != list(english.items()):
        errors.append("작업 영어 원문이 현재 설치 JAR과 다릅니다.")
    if list(korean.items()) != list(output.items()):
        errors.append("검수 작업본과 리소스팩 산출물이 다릅니다.")
    return {
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_sha256": sha256(jar),
        "english_keys": len(english),
        "korean_keys": len(korean),
        "source_matches_installed_jar": english == current,
        "output_matches_working_copy": korean == output,
    }, errors


def translated_catalog() -> dict[str, object]:
    """완성된 Cataclysm 번역 카탈로그를 읽는다."""
    return load_json(LANG_OUTPUT)


def verify_advancements(instance: Path) -> tuple[dict[str, object], list[str]]:
    """발전 과제 표시 요소가 언어 키를 통해 표시되는지 확인한다."""
    jar = find_jar(instance)
    catalog = translated_catalog()
    files = 0
    display_fields = 0
    literals: list[str] = []
    missing: list[str] = []
    with ZipFile(jar) as archive:
        names = [
            name
            for name in archive.namelist()
            if name.endswith(".json")
            and name.startswith(
                ("data/cataclysm/advancement/", "data/cataclysm/advancements/")
            )
        ]
        files = len(names)
        for name in names:
            data = json.loads(archive.read(name).decode("utf-8-sig"))
            display = data.get("display")
            if not isinstance(display, dict):
                continue
            for field in ("title", "description"):
                shown = display.get(field)
                if shown is None:
                    continue
                display_fields += 1
                if isinstance(shown, str):
                    if shown:
                        literals.append(f"{name}:{field}:{shown}")
                elif isinstance(shown, dict):
                    key = shown.get("translate")
                    if isinstance(key, str) and key not in catalog:
                        missing.append(f"{name}:{field}:{key}")
    errors = []
    if files != 21:
        errors.append(f"현재 JAR의 발전 과제 파일 수가 예상과 다릅니다: {files}/21")
    if literals:
        errors.append(
            "발전 과제에 번역 불가능한 직접 문구가 있습니다: "
            + " | ".join(literals[:20])
        )
    if missing:
        errors.append("발전 과제 번역 키가 빠졌습니다: " + " | ".join(missing[:20]))
    return {
        "files_checked": files,
        "display_fields_checked": display_fields,
        "visible_literal_fields": len(literals),
        "missing_translation_keys": len(missing),
    }, errors


def verify_guides(instance: Path) -> tuple[dict[str, object], list[str]]:
    """JAR 안의 별도 가이드나 Patchouli 표시 경로 존재 여부를 확인한다."""
    jar = find_jar(instance)
    candidates: list[str] = []
    with ZipFile(jar) as archive:
        for name in archive.namelist():
            lower = name.lower()
            if not lower.endswith((".json", ".snbt", ".txt", ".md")):
                continue
            if "patchouli_books/" in lower or re.search(r"(^|/)(book|guide)s?/", lower):
                candidates.append(name)
    errors = []
    if candidates:
        errors.append(
            "별도 가이드 표시 경로를 수동 검토해야 합니다: "
            + " | ".join(candidates[:20])
        )
    return {
        "separate_guide_candidates": len(candidates),
        "candidate_paths": candidates,
        "display_path": "모드 언어 파일 및 FTB Quests",
    }, errors


def verify_kubejs(instance: Path) -> tuple[dict[str, object], list[str]]:
    """KubeJS 참조와 직접 표시 문구 후보를 분리한다."""
    family = re.compile(r"cataclysm", re.IGNORECASE)
    display = re.compile(
        r"displayName|tooltip|Text\.(?:of|literal)|custom_name|\bname\s*:",
        re.IGNORECASE,
    )
    references: list[str] = []
    candidates: list[str] = []
    root = instance / "kubejs"
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".js",
            ".json",
            ".snbt",
            ".md",
            ".txt",
        }:
            continue
        relative = path.relative_to(instance).as_posix()
        if "/lang/" in relative:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        if not family.search(text):
            continue
        references.append(relative)
        for number, line in enumerate(text.splitlines(), 1):
            if family.search(line) and display.search(line):
                candidates.append(f"{relative}:{number}:{line.strip()}")
    errors = []
    if candidates:
        errors.append(
            "KubeJS 직접 표시 문구 후보가 있습니다: " + " | ".join(candidates[:20])
        )
    return {
        "files_referencing_family": len(references),
        "referenced_paths": references,
        "direct_display_candidates": len(candidates),
    }, errors


def verify_configs(instance: Path) -> tuple[dict[str, object], list[str]]:
    """Cataclysm 설정 파일을 읽기 전용 비번역 경로로 분류한다."""
    paths = sorted(
        path.relative_to(instance).as_posix()
        for path in (instance / "config").glob("cataclysm-*.toml")
        if path.is_file() and not path.name.endswith(".bak")
    )
    errors = []
    if paths != ["config/cataclysm-client.toml", "config/cataclysm-common.toml"]:
        errors.append(f"Cataclysm 설정 파일 범위가 예상과 다릅니다: {paths}")
    return {
        "runtime_config_files": paths,
        "localized_display_artifacts": 0,
        "classification": "런타임 설정값이며 번역 산출물 대상이 아님",
    }, errors


def flatten(value: object) -> str:
    """품질 금지 문구 검사를 위해 표시 값을 한 문자열로 합친다."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(flatten(item) for item in value)
    return ""


def verify_quality() -> tuple[dict[str, object], list[str]]:
    """수동 확정값과 누적 퀘스트 산출물, 금지 문구를 확인한다."""
    language = translated_catalog()
    quest_output = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    errors: list[str] = []
    mismatched_language = sorted(
        key
        for key, expected in quality_review.LANGUAGE_OVERRIDES.items()
        if language.get(key) != quality_review.normalize_language_value(key, expected)
    )
    if mismatched_language:
        errors.append(
            "수동 확정 언어 값이 다릅니다: " + " | ".join(mismatched_language[:20])
        )

    quest_values: dict[str, object] = {}
    for root in sorted((WORK_ROOT / "quests").glob("*")):
        path = root / "ko_kr.json"
        if path.is_file():
            quest_values.update(load_json(path))
    mismatched_quests = sorted(
        key for key, value in quest_values.items() if quest_output.get(key) != value
    )
    if mismatched_quests:
        errors.append(
            "FTB Quests 누적 산출물이 작업본과 다릅니다: "
            + " | ".join(mismatched_quests[:20])
        )

    bad_hits: list[str] = []
    for scope, values in (("language", language), ("quests", quest_values)):
        for key, value in values.items():
            text = flatten(value)
            for fragment in BAD_FRAGMENTS:
                if fragment.lower() in text.lower():
                    bad_hits.append(f"{scope}:{key}:{fragment}")
    if bad_hits:
        errors.append(
            "번역기식 또는 잔존 영어 문구가 있습니다: " + " | ".join(bad_hits[:20])
        )
    return {
        "language_overrides_checked": len(quality_review.LANGUAGE_OVERRIDES),
        "quest_keys_checked": len(quest_values),
        "mismatched_language_overrides": len(mismatched_language),
        "mismatched_quest_outputs": len(mismatched_quests),
        "forbidden_fragment_hits": len(bad_hits),
    }, errors


def main() -> int:
    instance = resolve_source_root()
    checks = {}
    errors: list[str] = []
    for name, verifier in (
        ("language_source", verify_language_source),
        ("advancements", verify_advancements),
        ("guides", verify_guides),
        ("kubejs", verify_kubejs),
        ("configs", verify_configs),
    ):
        report, check_errors = verifier(instance)
        checks[name] = report
        errors.extend(check_errors)
    quality, quality_errors = verify_quality()
    checks["quality"] = quality
    errors.extend(quality_errors)
    report = {
        "family": "L_Ender's Cataclysm",
        "instance": instance.as_posix(),
        **checks,
        "validation_errors": len(errors),
        "errors": errors,
        "status": "complete" if not errors else "failed",
    }
    path = WORK_ROOT / "family_completion.json"
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
