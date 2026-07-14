#!/usr/bin/env python3
"""네 대형 모드군의 완료 상태, 공통 용어와 누적 실제 적용을 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from apotheosis_catalog import TARGETS as APOTHEOSIS_TARGETS
from atmgear_catalog import TARGETS as ATMGEAR_TARGETS
from local_paths import PROJECT_ROOT, resolve_source_root
from relics_catalog import TARGETS as RELICS_TARGETS
from silentgear_catalog import TARGETS as SILENTGEAR_TARGETS

REPORT_FILE = PROJECT_ROOT / "working/goal_validation.json"
COMPLETION_FILE = PROJECT_ROOT / "working/goal_completion.json"
FAMILY_FILES = {
    "Apotheosis": PROJECT_ROOT / "working/apotheosis/family_completion.json",
    "Relics·Artifacts": PROJECT_ROOT / "working/relics/family_completion.json",
    "Silent Gear": PROJECT_ROOT / "working/silentgear/family_completion.json",
    "Allthemodium·ATM 장비": PROJECT_ROOT / "working/atmgear/family_completion.json",
}
VALIDATION_FILES = (
    PROJECT_ROOT / "working/relics/family_validation.json",
    PROJECT_ROOT / "working/silentgear/family_validation.json",
    PROJECT_ROOT / "working/atmgear/family_validation.json",
)
CROSS_MANIFESTS = {
    PROJECT_ROOT / "temp/backups/20260714_212144_768121/backup_manifest.json": {
        "resourcepacks/ATM10_Korean/assets/apothic_attributes/lang/ko_kr.json",
        "resourcepacks/ATM10_Korean/assets/artifacts/lang/ko_kr.json",
        "resourcepacks/ATM10_Korean/assets/silentgear/lang/ko_kr.json",
    },
    PROJECT_ROOT / "temp/backups/20260714_212400_755684/backup_manifest.json": {
        "resourcepacks/ATM10_Korean/assets/silentgear/lang/ko_kr.json",
    },
}
FORBIDDEN_TERMS = (
    "데미지",
    "대미지",
    "넉백",
    "갑옷 강도",
    "침묵의 장비",
    "올더모듐",
    "바이브라늄",
    "비브라늄",
    "언옵테늄",
    "언옵테이니움",
)
TEXT_SUFFIXES = {".js", ".json", ".md", ".snbt"}


def sha256(path: Path) -> str:
    """파일 SHA-256을 계산한다."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_object(path: Path) -> dict[str, object]:
    """JSON 객체를 UTF-8로 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def find_jar(instance: Path, prefix: str) -> Path:
    """접두사에 맞는 설치 JAR 하나를 찾는다."""
    matches = sorted(
        path
        for path in (instance / "mods").glob("*.jar")
        if path.name.lower().startswith(prefix.lower())
    )
    if len(matches) != 1:
        raise RuntimeError(f"JAR을 하나로 확정하지 못했습니다: {prefix}:{matches}")
    return matches[0]


def scoped_targets() -> list[object]:
    """네 모드군에서 검증한 모든 언어 대상을 반환한다."""
    return [
        *APOTHEOSIS_TARGETS,
        *RELICS_TARGETS,
        *SILENTGEAR_TARGETS,
        *ATMGEAR_TARGETS,
    ]


def collision_audit(instance: Path) -> tuple[int, int, list[dict[str, object]]]:
    """영어 이름이 다른 아이템이 같은 한국어로 합쳐졌는지 검사한다."""
    names_checked = 0
    intentional_source_duplicates = 0
    collisions: list[dict[str, object]] = []
    for target in scoped_targets():
        jar_path = find_jar(instance, target.jar_prefix)
        language_path = f"assets/{target.namespace}/lang/en_us.json"
        with ZipFile(jar_path) as archive:
            english = json.loads(archive.read(language_path).decode("utf-8-sig"))
        if hasattr(target, "includes"):
            english = {
                key: value for key, value in english.items() if target.includes(key)
            }
        korean = load_object(
            PROJECT_ROOT
            / f"output/resourcepack/ATM10_Korean/assets/{target.namespace}/lang/ko_kr.json"
        )
        by_korean: dict[str, list[str]] = defaultdict(list)
        for key, source in english.items():
            if (
                key in korean
                and isinstance(source, str)
                and isinstance(korean[key], str)
                and key.startswith(("item.", "block."))
            ):
                by_korean[korean[key]].append(key)
                names_checked += 1
        for translated, keys in by_korean.items():
            if len(keys) < 2:
                continue
            sources = {english[key] for key in keys}
            if len(sources) == 1:
                intentional_source_duplicates += 1
            else:
                collisions.append(
                    {
                        "namespace": target.namespace,
                        "translation": translated,
                        "keys": keys,
                        "english": sorted(sources),
                    }
                )
    return names_checked, intentional_source_duplicates, collisions


def scoped_text_files() -> list[Path]:
    """공통 용어를 검사할 네 모드군 산출물을 모은다."""
    files: set[Path] = set()
    for target in scoped_targets():
        root = (
            PROJECT_ROOT / f"output/resourcepack/ATM10_Korean/assets/{target.namespace}"
        )
        if root.is_dir():
            files.update(
                path
                for path in root.rglob("*")
                if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
            )
    for root in (
        PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/atm10_localization",
        PROJECT_ROOT / "working/apotheosis/quest_overrides.json",
        PROJECT_ROOT / "working/relics/quest_overrides.json",
        PROJECT_ROOT / "working/silentgear/quest_overrides.json",
        PROJECT_ROOT / "working/atmgear/quest_overrides.json",
    ):
        if root.is_file():
            files.add(root)
        elif root.is_dir():
            files.update(
                path
                for path in root.rglob("*")
                if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
            )
    return sorted(files)


def live_outputs(instance: Path) -> tuple[int, list[str]]:
    """누적 output 전체와 실제 인스턴스의 해시를 비교한다."""
    matches = 0
    errors: list[str] = []
    resource_root = PROJECT_ROOT / "output/resourcepack/ATM10_Korean"
    for source in sorted(path for path in resource_root.rglob("*") if path.is_file()):
        relative = source.relative_to(resource_root)
        target = instance / "resourcepacks/ATM10_Korean" / relative
        if not target.is_file() or sha256(source) != sha256(target):
            errors.append(f"resourcepack:{relative.as_posix()}")
        else:
            matches += 1
    override_root = PROJECT_ROOT / "output/overrides"
    for source in sorted(
        path
        for path in override_root.rglob("*")
        if path.is_file() and path.name != ".gitkeep"
    ):
        relative = source.relative_to(override_root)
        target = instance / relative
        if not target.is_file() or sha256(source) != sha256(target):
            errors.append(f"override:{relative.as_posix()}")
        else:
            matches += 1
    return matches, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    errors: list[str] = []
    families: dict[str, dict[str, object]] = {}
    for name, path in FAMILY_FILES.items():
        family = load_object(path)
        families[name] = family
        remaining = family.get("counts", {}).get("remaining", 0)
        if family.get("status") != "complete" or remaining != 0:
            errors.append(f"모드군 완료 상태가 아닙니다: {name}")
        if family.get("review_items"):
            errors.append(f"모드군에 수동 검토 항목이 남았습니다: {name}")
    for path in VALIDATION_FILES:
        validation = load_object(path)
        if validation.get("validation_errors") or validation.get("remaining"):
            errors.append(f"모드군 검증 보고에 오류가 있습니다: {path}")

    text_files = scoped_text_files()
    forbidden_hits: list[dict[str, str]] = []
    for path in text_files:
        text = path.read_text(encoding="utf-8")
        for term in FORBIDDEN_TERMS:
            if term in text:
                forbidden_hits.append(
                    {
                        "path": path.relative_to(PROJECT_ROOT).as_posix(),
                        "term": term,
                    }
                )
    if forbidden_hits:
        errors.append(f"공통 용어 금지 표현이 남았습니다: {forbidden_hits}")

    apothic_attributes = load_object(
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/apothic_attributes/lang/ko_kr.json"
    )
    artifacts = load_object(
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/artifacts/lang/ko_kr.json"
    )
    silentgear = load_object(
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/silentgear/lang/ko_kr.json"
    )
    common_values = {
        "armor_toughness": apothic_attributes[
            "attribute.name.generic.armor_toughness.desc"
        ],
        "artifact_knockback_resistance": artifacts[
            "artifacts.tooltip.ability.attribute_modifiers.generic.knockback_resistance"
        ],
        "silentgear_knockback_resistance": silentgear[
            "property.silentgear.knockback_resistance"
        ],
        "silentgear_netherwood_log": silentgear["block.silentgear.netherwood_log"],
        "silentgear_netherwood_wood": silentgear["block.silentgear.netherwood_wood"],
    }
    expected_values = {
        "armor_toughness": "적의 방어 강도 감소 효과에 대한 저항력을 높입니다.",
        "artifact_knockback_resistance": "밀치기에 면역입니다",
        "silentgear_knockback_resistance": "밀치기 저항",
        "silentgear_netherwood_log": "네더나무 원목",
        "silentgear_netherwood_wood": "네더나무 목재",
    }
    if common_values != expected_values:
        errors.append("공통 능력치 또는 충돌 해소 이름이 확정값과 다릅니다.")
    apotheosis = load_object(
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/apotheosis/lang/ko_kr.json"
    )
    if not any(
        "소켓" in value for value in apotheosis.values() if isinstance(value, str)
    ):
        errors.append("Apotheosis의 장비 socket 용어를 확인하지 못했습니다.")
    if not any(
        "슬롯" in value for value in artifacts.values() if isinstance(value, str)
    ):
        errors.append("Artifacts의 장착 slot 용어를 확인하지 못했습니다.")

    names_checked, intentional_duplicates, collisions = collision_audit(instance)
    if collisions:
        errors.append(f"번역으로 생긴 아이템 이름 충돌이 있습니다: {collisions}")

    allthemodium = load_object(
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/allthemodium/lang/ko_kr.json"
    )
    atm_localization = load_object(
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/atm10_localization/lang/ko_kr.json"
    )
    shared_materials = sorted(
        key for key in allthemodium if key.startswith("material.silentgear.")
    )
    if len(shared_materials) != 6 or any(
        allthemodium[key] != atm_localization.get(key) for key in shared_materials
    ):
        errors.append("Silent Gear와 Allthemodium의 공통 재료명이 다릅니다.")

    cross_applications: list[dict[str, object]] = []
    for path, expected in CROSS_MANIFESTS.items():
        manifest = load_object(path)
        target = manifest["targets"][0]
        changed = set(target["changed_paths"])
        if changed != expected or target["unexpected_changes"]:
            errors.append(f"교차 정상화 적용 매니페스트가 계획과 다릅니다: {path}")
        cross_applications.append(
            {
                "applied_at": manifest["applied_at"],
                "changed_paths": sorted(changed),
                "backup_manifest": path.relative_to(PROJECT_ROOT).as_posix(),
                "unexpected_changes": target["unexpected_changes"],
            }
        )

    live_matches, live_errors = live_outputs(instance)
    if live_errors:
        errors.append(f"누적 실제 적용 파일이 산출물과 다릅니다: {live_errors}")

    completion = {
        "goal": "four large mod families",
        "status": "complete" if not errors else "incomplete",
        "families": {
            name: {
                "status": family["status"],
                "installed": family["installed"],
                "counts": family["counts"],
                "out_of_scope": family["out_of_scope"],
            }
            for name, family in families.items()
        },
        "stage_commits": {
            "Apotheosis": ["347b2b9", "d7384f2", "067cc10", "00db05a"],
            "Relics·Artifacts": [
                "a472e57",
                "6ba8971",
                "f5bd6ae",
                "d6525e5",
                "04ced63",
            ],
            "Silent Gear": [
                "272f300",
                "aed9ea2",
                "4cc97b2",
                "6b1a150",
                "a2642af",
                "82faa62",
            ],
            "Allthemodium·ATM 장비": [
                "6a641e7",
                "fb22cda",
                "2113b35",
                "0d59cdc",
                "8e13f83",
                "e4d1ec3",
            ],
        },
        "cross_normalization": {
            "damage": "피해",
            "armor_toughness": "방어 강도",
            "knockback_resistance": "밀치기 저항",
            "upgrade": "업그레이드",
            "equipment_socket": "소켓",
            "equipment_slot": "슬롯",
            "silent_gear_official_name_preserved": True,
            "allthemodium_material_names": {
                key: allthemodium[key] for key in shared_materials
            },
            "translated_item_names_checked": names_checked,
            "intentional_source_duplicate_groups": intentional_duplicates,
            "translation_induced_collisions": 0,
            "normalized_entries": 7,
        },
        "application": {
            "target": str(instance),
            "cumulative_live_hash_matches": live_matches,
            "cumulative_live_hash_mismatches": len(live_errors),
            "cross_normalization_applications": cross_applications,
        },
        "remaining": 0,
        "review_items": [],
    }
    COMPLETION_FILE.write_text(
        json.dumps(completion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    report = {
        "families_complete": sum(
            family["status"] == "complete" for family in families.values()
        ),
        "families_expected": 4,
        "scoped_text_files_checked": len(text_files),
        "forbidden_term_hits": len(forbidden_hits),
        "translated_item_names_checked": names_checked,
        "intentional_source_duplicate_groups": intentional_duplicates,
        "translation_induced_collisions": len(collisions),
        "shared_allthemodium_material_names_checked": len(shared_materials),
        "cumulative_live_hash_matches": live_matches,
        "cumulative_live_hash_mismatches": len(live_errors),
        "remaining": 0,
        "validation_errors": len(errors),
        "errors": errors,
    }
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
