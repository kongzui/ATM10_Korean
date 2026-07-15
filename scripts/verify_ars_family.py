#!/usr/bin/env python3
"""Ars Nouveau 모드군의 가이드, 발전 과제, KubeJS와 적용 상태를 검증한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/ars_nouveau"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
DISPLAY_KEYS = {"name", "title", "description", "text"}
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
TRANSLATION_KEY = re.compile(r"^[a-z0-9_.-]+(?:\.[a-z0-9_.-]+)+$")


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def find_jar(instance: Path, prefix: str) -> Path:
    """설치본에서 정확히 하나인 모드 JAR을 찾는다."""
    matches = sorted((instance / "mods").glob(f"{prefix}*.jar"))
    if len(matches) != 1:
        raise FileNotFoundError(f"JAR 검색 결과가 하나가 아닙니다: {prefix}:{matches}")
    return matches[0]


def nested_fields(value: object, keys: set[str]) -> list[object]:
    """중첩 JSON에서 지정한 표시 필드를 모두 수집한다."""
    found: list[object] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in keys:
                found.append(child)
            found.extend(nested_fields(child, keys))
    elif isinstance(value, list):
        for child in value:
            found.extend(nested_fields(child, keys))
    return found


def translation_catalog() -> dict[str, object]:
    """Ars 모드군의 확정 한국어 키를 한 객체로 합친다."""
    combined: dict[str, object] = {}
    for target in family_goal.targets_for("ars_nouveau"):
        path = OUTPUT_ASSETS / target.namespace / "lang/ko_kr.json"
        combined.update(load_json(path))
    return combined


def verify_patchouli(instance: Path) -> tuple[dict[str, object], list[str]]:
    """Patchouli 페이지의 표시 필드가 언어 키를 통해 한국어로 이어지는지 검사한다."""
    translations = translation_catalog()
    files = 0
    fields = 0
    translated_keys = 0
    localized_literals = 0
    literals: list[str] = []
    missing: list[str] = []
    for target in family_goal.targets_for("ars_nouveau"):
        jar = find_jar(instance, target.jar_prefix)
        with ZipFile(jar) as archive:
            names = [
                name
                for name in archive.namelist()
                if "/patchouli_books/" in name
                and "/en_us/" in name
                and name.endswith(".json")
            ]
            files += len(names)
            for name in names:
                data = json.loads(archive.read(name).decode("utf-8-sig"))
                values = nested_fields(data, DISPLAY_KEYS)
                localized_path = (
                    PROJECT_ROOT
                    / "output/resourcepack/ATM10_Korean"
                    / name.replace("/en_us/", "/ko_kr/")
                )
                localized_values = (
                    nested_fields(load_json(localized_path), DISPLAY_KEYS)
                    if localized_path.is_file()
                    else []
                )
                if localized_values and len(values) != len(localized_values):
                    literals.append(f"{jar.name}:{name}:표시 필드 구조 불일치")
                for index, value in enumerate(values):
                    if not isinstance(value, str):
                        continue
                    fields += 1
                    if TRANSLATION_KEY.fullmatch(value):
                        translated_keys += 1
                        if value not in translations and not value.startswith(
                            "enchantment.minecraft."
                        ):
                            missing.append(f"{jar.name}:{name}:{value}")
                    elif (
                        LATIN_WORD.search(value)
                        and not value.startswith(("http", "#"))
                        and not family_goal.is_allowed_original(value)
                    ):
                        localized = (
                            localized_values[index]
                            if index < len(localized_values)
                            else None
                        )
                        if isinstance(localized, str) and localized != value:
                            if re.findall(r"\$\([^)]*\)", value) != re.findall(
                                r"\$\([^)]*\)", localized
                            ):
                                literals.append(
                                    f"{jar.name}:{name}:Patchouli 태그 순서 불일치"
                                )
                            else:
                                localized_literals += 1
                        else:
                            literals.append(f"{jar.name}:{name}:{value}")
    errors = []
    if missing:
        errors.append("Patchouli 번역 키 누락: " + " | ".join(missing[:30]))
    if literals:
        errors.append("Patchouli 영어 literal 표시 문구: " + " | ".join(literals[:30]))
    return {
        "files_checked": files,
        "display_fields": fields,
        "translation_keys": translated_keys,
        "missing_translation_keys": len(missing),
        "literal_display_fields": len(literals),
        "localized_literal_fields": localized_literals,
    }, errors


def verify_guideme(instance: Path) -> tuple[dict[str, object], list[str]]:
    """Ars Énergistique GuideME 페이지의 한국어 파일과 구조를 검사한다."""
    jar = find_jar(instance, "arseng-")
    source_name = "assets/arseng/ae2guide/arseng-index.md"
    output = OUTPUT_ASSETS / "arseng/ae2guide/_ko_kr/arseng-index.md"
    errors: list[str] = []
    with ZipFile(jar) as archive:
        source = archive.read(source_name).decode("utf-8-sig")
    if not output.is_file():
        errors.append("Ars Énergistique GuideME 한국어 페이지가 없습니다.")
        target = ""
    else:
        target = output.read_text(encoding="utf-8")
        source_links = re.findall(r"\]\(([^)]*)\)", source)
        target_links = re.findall(r"\]\(([^)]*)\)", target)
        source_tags = re.findall(r"<[^>]+>", source)
        target_tags = re.findall(r"<[^>]+>", target)
        if source_links != target_links:
            errors.append("Ars Énergistique GuideME 링크 순서가 다릅니다.")
        if source_tags != target_tags:
            errors.append("Ars Énergistique GuideME 태그 순서가 다릅니다.")
        if source == target:
            errors.append("Ars Énergistique GuideME 페이지가 영어와 같습니다.")
    return {
        "jar": jar.name,
        "pages_checked": 1,
        "output_exists": output.is_file(),
        "link_and_tag_order_checked": True,
    }, errors


def verify_advancements(instance: Path) -> tuple[dict[str, object], list[str]]:
    """모드군 전체 발전 과제의 제목과 설명 표시 경로를 검사한다."""
    translations = translation_catalog()
    files = 0
    fields = 0
    literals: list[str] = []
    missing: list[str] = []
    for target in family_goal.targets_for("ars_nouveau"):
        jar = find_jar(instance, target.jar_prefix)
        with ZipFile(jar) as archive:
            names = [
                name
                for name in archive.namelist()
                if "/advancement/" in name and name.endswith(".json")
            ]
            files += len(names)
            for name in names:
                data = json.loads(archive.read(name).decode("utf-8-sig"))
                for value in nested_fields(data, {"display"}):
                    if not isinstance(value, dict):
                        continue
                    for field in ("title", "description"):
                        shown = value.get(field)
                        if shown is None:
                            continue
                        fields += 1
                        if isinstance(shown, str):
                            literals.append(f"{jar.name}:{name}:{shown}")
                        elif isinstance(shown, dict) and isinstance(
                            shown.get("translate"), str
                        ):
                            key = shown["translate"]
                            if key not in translations:
                                missing.append(f"{jar.name}:{name}:{key}")
    errors = []
    if literals:
        errors.append("발전 과제 영어 literal 표시 문구: " + " | ".join(literals[:30]))
    if missing:
        errors.append("발전 과제 번역 키 누락: " + " | ".join(missing[:30]))
    return {
        "files_checked": files,
        "display_fields": fields,
        "literal_display_fields": len(literals),
        "missing_translation_keys": len(missing),
    }, errors


def verify_kubejs(instance: Path) -> tuple[dict[str, object], list[str]]:
    """KubeJS의 Ars 참조와 직접 표시 문자열 후보를 전수 분류한다."""
    family = re.compile(
        r"ars[_ ]nouveau|ars_additions|ars_controle|ars_elemancy|ars_elemental|"
        r"ars_technica|starbuncle|not_enough_glyphs|arseng|allthearcanistgear",
        re.IGNORECASE,
    )
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
        errors.append("KubeJS 직접 표시 문자열 후보: " + " | ".join(candidates[:30]))
    return {
        "files_referencing_family": len(references),
        "referenced_paths": references,
        "direct_display_candidates": len(candidates),
    }, errors


def verify_extra_scope(instance: Path) -> tuple[dict[str, object], list[str]]:
    """Ars Polymorphia의 언어 리소스 부재와 기존 공통 UI 완료 근거를 확인한다."""
    jar = find_jar(instance, "ars_polymorphia-")
    with ZipFile(jar) as archive:
        language_files = [
            name
            for name in archive.namelist()
            if "/lang/" in name and name.endswith(".json")
        ]
    common = load_json(PROJECT_ROOT / "working/common_ui/convenience/completion.json")
    errors = []
    if language_files:
        errors.append(f"Ars Polymorphia의 예상 밖 언어 파일: {language_files}")
    if common.get("status") != "complete":
        errors.append("공통 편의 기능 단계의 Ars Polymorphia 완료 근거가 없습니다.")
    return {
        "jar": jar.name,
        "language_files": len(language_files),
        "common_ui_completion": common.get("status"),
    }, errors


def deployment_report() -> dict[str, object]:
    """가장 최근 적용 기록에서 Ars 모드군 파일의 해시 일치를 집계한다."""
    manifests = sorted(
        (PROJECT_ROOT / "temp/backups").glob("*/backup_manifest.json"),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )
    if not manifests:
        return {"status": "not_applied", "files_checked": 0, "hash_matches": 0}
    path = manifests[0]
    manifest = load_json(path)
    targets = manifest.get("targets", [])
    if not isinstance(targets, list) or not targets:
        return {"status": "not_applied", "files_checked": 0, "hash_matches": 0}
    target = targets[0]
    assert isinstance(target, dict)
    files = target.get("files", [])
    namespaces = tuple(
        f"resourcepacks/ATM10_Korean/assets/{target.namespace}/"
        for target in family_goal.targets_for("ars_nouveau")
    )
    relevant = [
        row
        for row in files
        if isinstance(files, list) and isinstance(row, dict)
        if str(row.get("relative_path", ""))
        == "config/ftbquests/quests/lang/ko_kr.snbt"
        or str(row.get("relative_path", "")).startswith(namespaces)
    ]
    matches = sum(
        row.get("source_sha256") == row.get("after_sha256") for row in relevant
    )
    return {
        "status": "applied_and_verified"
        if relevant and matches == len(relevant)
        else "incomplete",
        "target": target.get("target_root"),
        "backup_manifest": path.relative_to(PROJECT_ROOT).as_posix(),
        "files_checked": len(relevant),
        "hash_matches": matches,
        "unexpected_changes": target.get("unexpected_changes", []),
    }


def verify(instance: Path) -> tuple[dict[str, object], int]:
    """모든 관련 표시 경로를 검사해 단계 완료 보고서를 만든다."""
    errors: list[str] = []
    core = load_json(WORK_ROOT / "language_validation.json")
    if core.get("status") != "complete":
        errors.append("언어·FTB Quests 핵심 검증이 완료되지 않았습니다.")
    patchouli, found = verify_patchouli(instance)
    errors.extend(found)
    guideme, found = verify_guideme(instance)
    errors.extend(found)
    advancements, found = verify_advancements(instance)
    errors.extend(found)
    kubejs, found = verify_kubejs(instance)
    errors.extend(found)
    extra_scope, found = verify_extra_scope(instance)
    errors.extend(found)
    report = {
        "family": "Ars Nouveau",
        "language_provenance": core.get("language_provenance", {}),
        "ftbquests": core.get("ftbquests", {}),
        "patchouli": patchouli,
        "guideme": guideme,
        "advancements": advancements,
        "kubejs": kubejs,
        "extra_scope": extra_scope,
        "deployment": deployment_report(),
        "validation_errors": len(errors),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "family_completion.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    report, status = verify(resolve_source_root())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
