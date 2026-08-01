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
QUALITY_REVIEW_COUNTS = {
    "language": {"reused": 521, "corrected": 136, "new": 0},
    "quests": {"reused": 54, "corrected": 43, "new": 0},
    "overall": {"reused": 575, "corrected": 179, "new": 0},
}


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


def expected_deployment_sources() -> dict[str, Path]:
    """EvilCraft 작업 단위에서 적용할 세 산출물만 반환한다."""
    return {
        "config/ftbquests/quests/lang/ko_kr.snbt": (
            PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
        ),
        "resourcepacks/ATM10_Korean/assets/evilcraft/lang/ko_kr.json": (
            OUTPUT_ASSETS / "evilcraft/lang/ko_kr.json"
        ),
        "resourcepacks/ATM10_Korean/assets/evilcraftcompat/lang/ko_kr.json": (
            OUTPUT_ASSETS / "evilcraftcompat/lang/ko_kr.json"
        ),
    }


def deployment_report(
    instance: Path, manifest_path: Path | None
) -> tuple[dict[str, object], list[str]]:
    """명시한 적용 기록의 경로와 실제 파일 해시를 검증한다."""
    if manifest_path is None:
        return {"status": "validated_not_applied"}, []
    manifest = load_json(manifest_path)
    targets = manifest.get("targets", [])
    if not isinstance(targets, list):
        return {"status": "invalid"}, ["적용 매니페스트의 대상 목록이 잘못되었습니다."]
    target = next(
        (
            row
            for row in targets
            if isinstance(row, dict) and Path(str(row.get("target_root"))) == instance
        ),
        None,
    )
    if target is None:
        return {"status": "not_found"}, ["적용 매니페스트에 현재 인스턴스가 없습니다."]
    expected = expected_deployment_sources()
    changed = set(target.get("changed_paths", []))
    errors: list[str] = []
    if changed != set(expected):
        errors.append(f"EvilCraft 적용 경로가 계획과 다릅니다: {sorted(changed)}")
    unexpected = target.get("unexpected_changes", [])
    if unexpected:
        errors.append("EvilCraft 적용 중 계획 밖 변경이 기록되었습니다.")
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
        "files_checked": len(expected),
        "hash_matches": matches,
        "unexpected_changes": unexpected,
    }, errors


def verify(instance: Path, manifest_path: Path | None) -> tuple[dict[str, object], int]:
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
    deployment, found = deployment_report(instance, manifest_path)
    errors.extend(found)
    status = (
        "complete"
        if not errors and manifest_path
        else "ready_for_apply"
        if not errors
        else "incomplete"
    )
    report = {
        "family": "EvilCraft",
        "counts": {
            "language_values": 657,
            "quest_display_values": 97,
            "visible_values": sum(QUALITY_REVIEW_COUNTS["overall"].values()),
            "existing_korean_reused": QUALITY_REVIEW_COUNTS["overall"]["reused"],
            "existing_korean_corrected": QUALITY_REVIEW_COUNTS["overall"]["corrected"],
            "newly_translated": QUALITY_REVIEW_COUNTS["overall"]["new"],
            "language_existing_korean_reused": QUALITY_REVIEW_COUNTS["language"][
                "reused"
            ],
            "language_existing_korean_corrected": QUALITY_REVIEW_COUNTS["language"][
                "corrected"
            ],
            "quest_existing_korean_reused": QUALITY_REVIEW_COUNTS["quests"]["reused"],
            "quest_existing_korean_corrected": QUALITY_REVIEW_COUNTS["quests"][
                "corrected"
            ],
            "remaining": len(errors),
        },
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
        "status": status,
    }
    (WORK_ROOT / "family_completion.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deployment-manifest", type=Path)
    args = parser.parse_args()
    report, status = verify(resolve_source_root(), args.deployment_manifest)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
