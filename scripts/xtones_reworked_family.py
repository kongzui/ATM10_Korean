#!/usr/bin/env python3
"""XTones Reworked의 전체 블록 이름과 표시 표면을 번역하고 검증해요."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root

FAMILY = "xtones_reworked"
MOD_ID = "xtonesreworked"
JAR_PATTERN = "xtonesreworked-*.jar"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
RESOURCE_OUTPUT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/xtonesreworked/lang/ko_kr.json"
)
DEPLOYMENT_PATH = "resourcepacks/ATM10_Korean/assets/xtonesreworked/lang/ko_kr.json"
LANGUAGE_PATH = "assets/xtonesreworked/lang/en_us.json"
KUBE_CANDIDATE = "kubejs/assets/xtonesreworked/lang/pt_br.json"
TEXT_SUFFIXES = {
    ".cfg",
    ".ini",
    ".js",
    ".json",
    ".properties",
    ".snbt",
    ".toml",
    ".txt",
}
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[.]\d+)?")
FAMILY_KEY = re.compile(r"block[.]xtonesreworked[.]([a-z0-9]+)_block_(\d+)")

EXPECTED_FAMILIES = {
    "agon": "Agon",
    "azur": "Azur",
    "bitt": "Bitt",
    "cray": "Cray",
    "fort": "Fort",
    "glaxx": "Glaxx",
    "iszm": "ISZM",
    "jelt": "Jelt",
    "korp": "Korp",
    "kryp": "Kryp",
    "lair": "Lair",
    "lave": "Lave",
    "mint": "Mint",
    "myst": "Myst",
    "reds": "Reds",
    "reed": "Reed",
    "roen": "Roen",
    "sols": "Sols",
    "sync": "Sync",
    "tank": "Tank",
    "vect": "Vect",
    "vena": "Vena",
    "zane": "Zane",
    "zech": "Zech",
    "zest": "Zest",
    "zeta": "Zeta",
    "zion": "Zion",
    "zkul": "Zkul",
    "zoea": "Zoea",
    "zome": "Zome",
    "zone": "Zone",
    "zorg": "Zorg",
    "ztyl": "Ztyl",
    "zyth": "Zyth",
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽어요."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아니에요: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 읽기 쉬운 형태로 기록해요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    """파일 SHA-256을 계산해요."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_jar(instance: Path) -> Path:
    """현재 인스턴스의 유일한 XTones Reworked JAR을 찾아요."""
    matches = sorted((instance / "mods").glob(JAR_PATTERN))
    if len(matches) != 1:
        raise FileNotFoundError(f"JAR 수가 1개가 아니에요: {matches}")
    return matches[0]


def read_jar_language(jar: Path) -> dict[str, object]:
    """현재 JAR의 영어 언어 파일을 읽어요."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read(LANGUAGE_PATH))
    if not isinstance(value, dict):
        raise TypeError(f"JAR 언어 파일이 객체가 아니에요: {jar.name}")
    return value


def expected_source() -> dict[str, str]:
    """확정한 547개 영어 키 구조를 만들어요."""
    expected = {
        "itemGroup.xtonesreworked": "Xtones Reworked",
        "block.xtonesreworked.xtone_tile": "Xtone Tile",
        "block.xtonesreworked.flat_lamp": "Flat Lamp",
    }
    for slug, display in EXPECTED_FAMILIES.items():
        for variant in range(16):
            key = f"block.xtonesreworked.{slug}_block_{variant}"
            expected[key] = display if variant == 0 else f"{display} Variant {variant}"
    return expected


def translations(english: dict[str, object]) -> dict[str, str]:
    """고유 계열명은 유지하고 무늬 구분어를 한국어로 번역해요."""
    expected = expected_source()
    if english != expected:
        missing = sorted(set(expected) - set(english))
        extra = sorted(set(english) - set(expected))
        changed = sorted(
            key
            for key in english.keys() & expected.keys()
            if english[key] != expected[key]
        )
        raise ValueError(
            f"현재 영어 키 구조가 확정 범위와 달라요: "
            f"누락={missing}, 초과={extra}, 값 변경={changed}"
        )
    translated = {
        "itemGroup.xtonesreworked": "Xtones Reworked",
        "block.xtonesreworked.xtone_tile": "Xtone 타일",
        "block.xtonesreworked.flat_lamp": "평면 램프",
    }
    for slug, display in EXPECTED_FAMILIES.items():
        for variant in range(16):
            key = f"block.xtonesreworked.{slug}_block_{variant}"
            translated[key] = display if variant == 0 else f"{display} 변형 {variant}"
    return {key: translated[key] for key in english}


def prepare() -> dict[str, object]:
    """현재 영어 원문과 한국어 후보 유무를 작업 폴더에 기록해요."""
    instance = resolve_source_root()
    jar = source_jar(instance)
    english = read_jar_language(jar)
    with ZipFile(jar) as archive:
        languages = sorted(
            name
            for name in archive.namelist()
            if name.startswith("assets/xtonesreworked/lang/") and name.endswith(".json")
        )
    candidate_path = instance / KUBE_CANDIDATE
    candidate = load_json(candidate_path) if candidate_path.is_file() else {}
    write_json(WORK_ROOT / "en_us.json", english)
    inventory = {
        "family": FAMILY,
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_mtime_ns": jar.stat().st_mtime_ns,
        "english_keys": len(english),
        "block_keys": sum(key.startswith("block.") for key in english),
        "item_group_keys": sum(key.startswith("itemGroup.") for key in english),
        "jar_languages": languages,
        "bundled_korean_keys": 0,
        "status": "prepared",
    }
    candidates = {
        "current_jar_korean": None,
        "project_korean_candidate_before_family": None,
        "instance_kubejs_non_korean_candidate": {
            "path": KUBE_CANDIDATE,
            "language": "pt_br",
            "keys": len(candidate),
            "same_keyset_as_current_english": set(candidate) == set(english),
            "used_for_korean_translation": False,
        },
        "existing_korean_candidate_keys": 0,
    }
    write_json(WORK_ROOT / "inventory.json", inventory)
    write_json(WORK_ROOT / "candidate_sources.json", candidates)
    return inventory


def build() -> dict[str, object]:
    """현재 영어 547키 전체의 검수된 한국어 산출물을 만들어요."""
    english = load_json(WORK_ROOT / "en_us.json")
    korean = translations(english)
    write_json(WORK_ROOT / "ko_kr.json", korean)
    write_json(RESOURCE_OUTPUT, korean)
    report = {
        "reviewed_language_keys": len(english),
        "existing_korean_reused": 0,
        "new_language_translations": len(korean),
        "intentional_proper_names_retained": len(EXPECTED_FAMILIES) + 1,
        "localized_block_names": len(korean) - len(EXPECTED_FAMILIES) - 1,
        "ftbquests_translation_keys": 0,
        "kubejs_files_modified": 0,
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def collect_visible_recipe_fields(value: object, path: str = "") -> list[str]:
    """조합법 JSON에 직접 노출될 수 있는 문자열 필드를 찾아요."""
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}/{key}"
            if key in {"description", "name", "text", "title", "translate"}:
                if isinstance(child, str):
                    found.append(f"{child_path}={child}")
            found.extend(collect_visible_recipe_fields(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(collect_visible_recipe_fields(child, f"{path}/{index}"))
    return found


def scan_instance_references(instance: Path) -> dict[str, object]:
    """포르투갈어 후보 외의 KubeJS·FTB Quests 직접 참조를 찾아요."""
    references = []
    read_errors = []
    excluded = (instance / KUBE_CANDIDATE).resolve()
    for base in (instance / "kubejs", instance / "config/ftbquests"):
        for path in sorted(base.rglob("*"), key=lambda item: item.as_posix().lower()):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if path.resolve() == excluded:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                read_errors.append(f"{path.relative_to(instance).as_posix()}: {exc}")
                continue
            if MOD_ID in text.lower():
                references.append(path.relative_to(instance).as_posix())
    return {
        "references_outside_non_korean_candidate": references,
        "read_errors": read_errors,
    }


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR 조합법과 KubeJS·FTB Quests 표시 경로를 감사해요."""
    instance = resolve_source_root()
    jar = source_jar(instance)
    errors = []
    with ZipFile(jar) as archive:
        names = archive.namelist()
        recipe_files = sorted(
            name
            for name in names
            if name.startswith("data/") and "/recipe" in name and name.endswith(".json")
        )
        advancement_files = sorted(
            name
            for name in names
            if name.startswith("data/")
            and "/advancement" in name
            and name.endswith(".json")
        )
        guide_files = sorted(
            name
            for name in names
            if any(word in name.lower() for word in ("guide", "patchouli", "book"))
        )
        visible_fields = []
        for name in recipe_files:
            value = json.loads(archive.read(name))
            visible_fields.extend(
                f"{name}:{field}" for field in collect_visible_recipe_fields(value)
            )
    if advancement_files:
        errors.append(f"예상하지 않은 발전 과제가 있어요: {advancement_files}")
    if guide_files:
        errors.append(f"예상하지 않은 가이드 파일이 있어요: {guide_files}")
    if visible_fields:
        errors.append(f"조합법에 직접 표시 문자열이 있어요: {visible_fields}")
    references = scan_instance_references(instance)
    errors.extend(str(value) for value in references["read_errors"])
    if references["references_outside_non_korean_candidate"]:
        errors.append(
            "KubeJS·FTB Quests에 추가 참조가 있어요: "
            f"{references['references_outside_non_korean_candidate']}"
        )
    candidate = instance / KUBE_CANDIDATE
    if not candidate.is_file():
        errors.append(f"계획에 기록된 KubeJS 언어 후보가 없어요: {KUBE_CANDIDATE}")
    else:
        candidate_values = load_json(candidate)
        if set(candidate_values) != set(read_jar_language(jar)):
            errors.append("KubeJS 포르투갈어 후보 키가 현재 영어 키와 달라요")
    report = {
        "family": FAMILY,
        "jar": jar.name,
        "recipe_files": len(recipe_files),
        "recipe_visible_fields": visible_fields,
        "advancement_files": advancement_files,
        "guide_files": guide_files,
        "kubejs_non_korean_candidate": KUBE_CANDIDATE,
        "kubejs_candidate_used": False,
        "references": references,
        "ftbquests_display_work": "no_related_references",
        "kubejs_display_work": "candidate_audited_no_korean_changes",
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def preserved_tokens(key: str, source: str, target: str) -> list[str]:
    """자리표시자·서식·숫자·줄바꿈 보존 여부를 확인해요."""
    errors = []
    for label, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식 코드", FORMAT_CODE),
        ("숫자", NUMBER),
    ):
        if pattern.findall(source) != pattern.findall(target):
            errors.append(f"{label} 불일치: {key}")
    if source.count("\\n") != target.count("\\n"):
        errors.append(f"이스케이프 줄바꿈 불일치: {key}")
    if source.count("\n") != target.count("\n"):
        errors.append(f"실제 줄바꿈 불일치: {key}")
    return errors


def verify() -> tuple[dict[str, object], list[str]]:
    """현재 JAR과 산출물의 키·값·표시 이름 완결성을 확인해요."""
    instance = resolve_source_root()
    jar_english = read_jar_language(source_jar(instance))
    english = load_json(WORK_ROOT / "en_us.json")
    korean = load_json(WORK_ROOT / "ko_kr.json")
    output = load_json(RESOURCE_OUTPUT)
    audit_report = load_json(WORK_ROOT / "surface_audit.json")
    errors = []
    untranslated = []
    allowed_same = {"itemGroup.xtonesreworked"} | {
        f"block.xtonesreworked.{slug}_block_0" for slug in EXPECTED_FAMILIES
    }
    if jar_english != english:
        errors.append("작업 영어가 현재 설치 JAR 영어와 달라요")
    if list(english) != list(korean):
        errors.append("한국어 키 또는 순서가 영어 원문과 달라요")
    if korean != output:
        errors.append("작업 한국어와 리소스팩 산출물이 달라요")
    for key in english.keys() & korean.keys():
        source = english[key]
        target = korean[key]
        if not isinstance(source, str) or not isinstance(target, str):
            errors.append(f"문자열이 아닌 값이 있어요: {key}")
            continue
        errors.extend(preserved_tokens(key, source, target))
        if source == target and key not in allowed_same:
            untranslated.append(key)
    expected_same = sorted(
        key for key in allowed_same if english.get(key) != korean.get(key)
    )
    if expected_same:
        errors.append(f"고유 계열명이 예상과 달라요: {expected_same}")
    if untranslated:
        errors.append(f"허용하지 않은 영어 동일값이 있어요: {untranslated}")
    collisions = defaultdict(list)
    for key, target in korean.items():
        if key.startswith("block.") and isinstance(target, str):
            collisions[target].append(key)
    unexpected_collisions = {
        target: keys for target, keys in collisions.items() if len(keys) > 1
    }
    if unexpected_collisions:
        errors.append(f"블록 검색명이 충돌해요: {unexpected_collisions}")
    family_variants = defaultdict(set)
    for key in korean:
        match = FAMILY_KEY.fullmatch(key)
        if match:
            family_variants[match.group(1)].add(int(match.group(2)))
    expected_variants = set(range(16))
    invalid_families = {
        family: sorted(variants)
        for family, variants in family_variants.items()
        if variants != expected_variants
    }
    if set(family_variants) != set(EXPECTED_FAMILIES):
        errors.append("34개 재질 계열 목록이 확정 범위와 달라요")
    if invalid_families:
        errors.append(f"계열별 변형 번호가 0~15가 아니에요: {invalid_families}")
    audit_errors = audit_report.get("errors", [])
    if isinstance(audit_errors, list):
        errors.extend(str(value) for value in audit_errors)
    report = {
        "family": FAMILY,
        "keys": len(korean),
        "families": len(family_variants),
        "variants_per_family": 16,
        "intentional_same_proper_names": len(allowed_same),
        "untranslated_candidates": untranslated,
        "unexpected_name_collisions": unexpected_collisions,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "language_validation.json", report)
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = load_json(deployment_path) if deployment_path.is_file() else None
    completion = {
        "family": FAMILY,
        "language_keys": len(korean),
        "surface_audit": audit_report.get("status"),
        "language_validation": report["status"],
        "deployment": deployment,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_completion.json", completion)
    return report, errors


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 스크립트의 백업·해시 결과를 완료 기록에 반영해요."""
    resolved = manifest_path.resolve()
    try:
        relative_manifest = resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        relative_manifest = str(resolved)
    manifest = load_json(resolved)
    errors = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 매니페스트가 완료 상태가 아니에요")
    if manifest.get("java_processes"):
        errors.append(f"적용 당시 Java 프로세스가 있어요: {manifest['java_processes']}")
    targets = manifest.get("targets")
    if not isinstance(targets, list) or not targets:
        errors.append("적용 대상 기록이 없어요")
        targets = []
    summarized_targets = []
    for target in targets:
        if not isinstance(target, dict):
            errors.append("적용 대상 기록 형식이 잘못됐어요")
            continue
        files = target.get("files", [])
        record = next(
            (
                value
                for value in files
                if isinstance(value, dict)
                and value.get("relative_path") == DEPLOYMENT_PATH
            ),
            None,
        )
        if target.get("status") != "applied_and_verified":
            errors.append(
                f"적용 대상 상태가 완료가 아니에요: {target.get('target_root')}"
            )
        if target.get("unexpected_changes"):
            errors.append(
                f"예상 밖 적용 변경이 있어요: {target.get('unexpected_changes')}"
            )
        if record is None:
            errors.append(
                f"XTones 산출물 적용 기록이 없어요: {target.get('target_root')}"
            )
        elif record.get("source_sha256") != record.get("after_sha256"):
            errors.append(f"적용 후 해시가 달라요: {target.get('target_root')}")
        summarized_targets.append(
            {
                "target_type": target.get("target_type"),
                "target_root": target.get("target_root"),
                "changed_paths": target.get("changed_paths", []),
                "unexpected_changes": target.get("unexpected_changes", []),
                "hash_verified": bool(
                    record and record.get("source_sha256") == record.get("after_sha256")
                ),
            }
        )
    report = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "backup_manifest": relative_manifest,
        "targets": summarized_targets,
        "errors": errors,
    }
    write_json(WORK_ROOT / "deployment_report.json", report)
    verify_report, verify_errors = verify()
    return {
        "deployment": report,
        "verification": verify_report["status"],
    }, errors + verify_errors


def run_all() -> tuple[dict[str, object], list[str]]:
    """준비·생성·표면 감사·검증을 순서대로 실행해요."""
    prepared = prepare()
    built = build()
    audit_report, audit_errors = audit()
    verify_report, verify_errors = verify()
    errors = audit_errors + verify_errors
    return {
        "prepare": prepared,
        "build": built,
        "audit": audit_report,
        "verify": verify_report,
        "status": "complete" if not errors else "incomplete",
    }, errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "build", "audit", "verify", "record-deployment", "all"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    if args.command == "prepare":
        result = prepare()
    elif args.command == "build":
        result = build()
    elif args.command == "audit":
        result, errors = audit()
    elif args.command == "verify":
        result, errors = verify()
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        result, errors = record_deployment(args.manifest)
    else:
        result, errors = run_all()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
