#!/usr/bin/env python3
"""EvilCraft 가이드북, 발전 과제, KubeJS와 적용 상태를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/evilcraft"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
INFO_KEY = re.compile(r"info_book\.[a-z0-9_.]+")


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def find_jar(instance: Path) -> Path:
    """설치본에서 EvilCraft JAR 하나를 찾는다."""
    matches = sorted((instance / "mods").glob("evilcraft-*.jar"))
    if len(matches) != 1:
        raise FileNotFoundError(f"EvilCraft JAR 검색 결과가 하나가 아닙니다: {matches}")
    return matches[0]


def translations() -> dict[str, object]:
    """본체와 호환 네임스페이스의 확정 번역을 합친다."""
    combined: dict[str, object] = {}
    for namespace in ("evilcraft", "evilcraftcompat"):
        combined.update(load_json(OUTPUT_ASSETS / namespace / "lang/ko_kr.json"))
    return combined


def verify_info_book(instance: Path) -> tuple[dict[str, object], list[str]]:
    """Origins of Darkness XML과 모든 통합 가이드 언어 키를 검사한다."""
    jar = find_jar(instance)
    catalog = translations()
    with ZipFile(jar) as archive:
        raw = archive.read("data/evilcraft/info/book.xml")
    text = raw.decode("utf-8-sig")
    ET.fromstring(text)
    referenced = sorted(set(INFO_KEY.findall(text)))
    missing = [key for key in referenced if key not in catalog]
    guide_keys = sorted(key for key in catalog if key.startswith("info_book."))
    untranslated = [
        key
        for key in guide_keys
        if isinstance(catalog[key], str)
        and re.search(r"[A-Za-z]{3,}", catalog[key])
        and catalog[key]
        not in {
            "Baubles",
            "Blood Magic",
            "Equivalent Exchange 3",
            "Forestry",
            "Ender IO",
            "Industrial Craft 2",
            "Just Enough Items",
            "Immersive Engineering",
            "Thermal Expansion",
            "Thaumcraft",
            "Tinkers' Construct",
            "Jade",
        }
        and catalog[key]
        == load_json(WORK_ROOT / key.split(".")[1] / "en_us.json").get(key)
    ]
    errors = []
    if missing:
        errors.append("Origins of Darkness 번역 키 누락: " + " | ".join(missing[:30]))
    if untranslated:
        errors.append("통합 가이드 영어 유지: " + " | ".join(untranslated[:30]))
    return {
        "jar": jar.name,
        "xml_files_checked": 1,
        "xml_translation_keys": len(referenced),
        "all_guide_language_keys": len(guide_keys),
        "missing_translation_keys": len(missing),
        "untranslated_guide_keys": len(untranslated),
    }, errors


def verify_advancements(instance: Path) -> tuple[dict[str, object], list[str]]:
    """발전 과제 표시 필드가 확정 번역 키를 사용하는지 검사한다."""
    jar = find_jar(instance)
    catalog = translations()
    files = 0
    fields = 0
    literals: list[str] = []
    missing: list[str] = []
    with ZipFile(jar) as archive:
        names = [
            name
            for name in archive.namelist()
            if "/advancement/" in name and name.endswith(".json")
        ]
        files = len(names)
        for name in names:
            data = json.loads(archive.read(name).decode("utf-8-sig"))
            display = data.get("display", {})
            if not isinstance(display, dict):
                continue
            for field in ("title", "description"):
                shown = display.get(field)
                if shown is None:
                    continue
                fields += 1
                if isinstance(shown, str):
                    literals.append(f"{name}:{shown}")
                elif isinstance(shown, dict) and isinstance(
                    shown.get("translate"), str
                ):
                    key = shown["translate"]
                    if key not in catalog:
                        missing.append(f"{name}:{key}")
    errors = []
    if literals:
        errors.append("발전 과제 literal 표시 문구: " + " | ".join(literals[:30]))
    if missing:
        errors.append("발전 과제 번역 키 누락: " + " | ".join(missing[:30]))
    return {
        "files_checked": files,
        "display_fields": fields,
        "literal_display_fields": len(literals),
        "missing_translation_keys": len(missing),
    }, errors


def verify_kubejs(instance: Path) -> tuple[dict[str, object], list[str]]:
    """KubeJS의 EvilCraft 참조와 직접 표시 문자열 후보를 전수 분류한다."""
    family = re.compile(r"evilcraft(?:compat)?", re.IGNORECASE)
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


def sha256(path: Path) -> str:
    """파일 SHA-256을 계산한다."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def deployment_report(instance: Path) -> dict[str, object]:
    """가장 최근 적용 기록에서 EvilCraft 관련 파일의 해시 일치를 집계한다."""
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
    expected = (
        (
            PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt",
            instance / "config/ftbquests/quests/lang/ko_kr.snbt",
        ),
        (
            OUTPUT_ASSETS / "evilcraft/lang/ko_kr.json",
            instance / "resourcepacks/ATM10_Korean/assets/evilcraft/lang/ko_kr.json",
        ),
        (
            OUTPUT_ASSETS / "evilcraftcompat/lang/ko_kr.json",
            instance
            / "resourcepacks/ATM10_Korean/assets/evilcraftcompat/lang/ko_kr.json",
        ),
    )
    matches = sum(
        source.is_file() and target.is_file() and sha256(source) == sha256(target)
        for source, target in expected
    )
    target_manifest = targets[0] if isinstance(targets[0], dict) else {}
    return {
        "status": "applied_and_verified" if matches == len(expected) else "incomplete",
        "target": str(instance),
        "backup_manifest": path.relative_to(PROJECT_ROOT).as_posix(),
        "files_checked": len(expected),
        "hash_matches": matches,
        "unexpected_changes": target_manifest.get("unexpected_changes", []),
    }


def verify(instance: Path) -> tuple[dict[str, object], int]:
    """모든 관련 표시 경로를 검사해 단계 완료 보고서를 만든다."""
    errors: list[str] = []
    core = load_json(WORK_ROOT / "language_validation.json")
    if core.get("status") != "complete":
        errors.append("언어·FTB Quests 핵심 검증이 완료되지 않았습니다.")
    info_book, found = verify_info_book(instance)
    errors.extend(found)
    advancements, found = verify_advancements(instance)
    errors.extend(found)
    kubejs, found = verify_kubejs(instance)
    errors.extend(found)
    deployment = deployment_report(instance)
    if deployment.get("status") != "applied_and_verified":
        errors.append("EvilCraft 산출물이 실제 설치본에 아직 적용되지 않았습니다.")
    report = {
        "family": "EvilCraft",
        "language_provenance": core.get("language_provenance", {}),
        "ftbquests": core.get("ftbquests", {}),
        "info_book": info_book,
        "advancements": advancements,
        "kubejs": kubejs,
        "dependency_scope": {
            "Cyclops Core": "필수 기반 라이브러리이며 EvilCraft 표시 언어 대상이 아님"
        },
        "deployment": deployment,
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
