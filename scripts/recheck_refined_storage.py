#!/usr/bin/env python3
"""Refined Storage 2 재검수 범위와 누적 산출물을 현재 설치 원문으로 검증한다."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import audit_ftbquests_titles as quest_audit
import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root

WORK_ROOT = PROJECT_ROOT / "working/refined_storage"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
REPORT_PATH = WORK_ROOT / "recheck_20260808.json"


@dataclass(frozen=True)
class LanguageTarget:
    namespace: str
    jar_prefix: str
    ownership: str


PRIMARY_TARGETS = (
    LanguageTarget("refinedstorage", "refinedstorage-neoforge-", "primary"),
    LanguageTarget("extradisks", "ExtraDisks-", "primary"),
    LanguageTarget("extrastorage", "ExtraStorage-", "primary"),
    LanguageTarget("refinedtypes", "refined-types-", "primary"),
    LanguageTarget("universalgrid", "universalgrid-neoforge-", "primary"),
    LanguageTarget(
        "refinedstorage_curios_integration",
        "refinedstorage-curios-integration-",
        "primary",
    ),
)
CONSISTENCY_TARGETS = (
    LanguageTarget(
        "refinedstorage_jei_integration",
        "refinedstorage-jei-integration-neoforge-",
        "consistency_only_family_5",
    ),
    LanguageTarget(
        "refinedstorage_mekanism_integration",
        "refinedstorage-mekanism-integration-",
        "consistency_only_family_2",
    ),
)
ALL_TARGETS = PRIMARY_TARGETS + CONSISTENCY_TARGETS
ALLOWED_NAMESPACES = {target.namespace for target in ALL_TARGETS}
DEDICATED_CHAPTER = "refined_storage"

PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_RE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER_RE = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?")
URL_RE = re.compile(r"https?://[^\s\"']+")
PROTECTED_RE = re.compile(
    r"(?<![A-Za-z])(?:ALT|CMD|CTRL|FE|FPS|GUIs?|JEI|RS2|RS|SHIFT|X|Y|Z|N|E|S|W)"
    r"(?![A-Za-z])"
)
UNIT_RE = re.compile(r"(?<=\d)(?:B|K|kB|k|m|x)\b")
NAME_PREFIXES = ("block.", "item.")
NUMBER_EXCEPTIONS = {
    "gui.refinedstorage.tenth_anniversary.enable_cape",
    "gui.refinedstorage.tenth_anniversary.disable_cape",
    "gui.refinedstorage.tenth_anniversary.cape_info",
    "text.autoconfig.refinedstorage.option.upgrade.fortune1UpgradeEnergyUsage",
    "text.autoconfig.refinedstorage.option.upgrade.fortune1UpgradeEnergyUsage.tooltip",
    "text.autoconfig.refinedstorage.option.upgrade.fortune2UpgradeEnergyUsage",
    "text.autoconfig.refinedstorage.option.upgrade.fortune2UpgradeEnergyUsage.tooltip",
    "text.autoconfig.refinedstorage.option.upgrade.fortune3UpgradeEnergyUsage",
    "text.autoconfig.refinedstorage.option.upgrade.fortune3UpgradeEnergyUsage.tooltip",
}
UPSTREAM_DUPLICATE_EXCEPTIONS = {"extradisks": {"_comment"}}
EXPECTED = {
    "primary_language_keys": 1142,
    "consistency_language_keys": 47,
    "quest_display_keys": 99,
    "quests": 52,
    "tasks": 59,
}
EXPECTED_DEPLOYMENTS = {
    "config/ftbquests/quests/lang/ko_kr.snbt",
    "resourcepacks/ATM10_Korean/assets/refinedstorage/lang/ko_kr.json",
    "resourcepacks/ATM10_Korean/assets/refinedtypes/lang/ko_kr.json",
    "resourcepacks/ATM10_Korean/assets/universalgrid/lang/ko_kr.json",
}
REVIEW_STATS = {
    "reviewed": 1288,
    "unchanged": 1161,
    "corrected": 127,
    "missing_added": 0,
}


def find_jar(instance: Path, prefix: str) -> Path:
    """접두사로 현재 설치 JAR 하나를 확정한다."""
    matches = sorted(
        path
        for path in (instance / "mods").glob("*.jar")
        if path.name.lower().startswith(prefix.lower())
    )
    if len(matches) != 1:
        raise RuntimeError(f"JAR을 하나로 확정하지 못했습니다: {prefix}:{matches}")
    return matches[0]


def parse_json(
    raw: str,
    label: str,
    errors: list[str],
    allowed_duplicates: set[str] | None = None,
) -> dict[str, object]:
    """중복 키를 기록하면서 JSON 객체를 읽는다."""
    duplicates: list[str] = []

    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        counts = Counter(key for key, _ in pairs)
        duplicates.extend(key for key, count in counts.items() if count > 1)
        return dict(pairs)

    value = json.loads(raw, object_pairs_hook=hook)
    if not isinstance(value, dict):
        errors.append(f"{label}: 최상위 값이 객체가 아닙니다")
        return {}
    unexpected_duplicates = set(duplicates) - (allowed_duplicates or set())
    if unexpected_duplicates:
        errors.append(f"{label}: 중복 키 {sorted(unexpected_duplicates)}")
    return value


def load_json(path: Path, errors: list[str]) -> dict[str, object]:
    return parse_json(path.read_text(encoding="utf-8-sig"), str(path), errors)


def flatten(value: object) -> str:
    if isinstance(value, list):
        return "\n".join(str(part) for part in value)
    return str(value)


def protected_tokens(value: str) -> Counter[str]:
    """한국어 조사와 이스케이프 줄바꿈 옆의 보호 토큰을 정규화한다."""
    tokens = PROTECTED_RE.findall(value.replace("\\n", " "))
    return Counter("GUI" if token == "GUIs" else token for token in tokens)


def validate_value(key: str, source: object, target: object) -> list[str]:
    """자료형과 번역 금지 토큰을 비교한다."""
    errors: list[str] = []
    if type(source) is not type(target):
        return [f"{key}: 자료형 불일치"]
    if isinstance(source, list) and len(source) != len(target):
        errors.append(f"{key}: 문단 수 불일치")
    source_text = flatten(source)
    target_text = flatten(target)
    checks = (
        ("자리표시자", PLACEHOLDER_RE),
        ("서식 코드", FORMAT_RE),
        ("URL", URL_RE),
        ("단위", UNIT_RE),
    )
    for label, pattern in checks:
        if Counter(pattern.findall(source_text)) != Counter(
            pattern.findall(target_text)
        ):
            errors.append(f"{key}: {label} 불일치")
    if protected_tokens(source_text) != protected_tokens(target_text):
        errors.append(f"{key}: 보호 토큰 불일치")
    if key not in NUMBER_EXCEPTIONS and Counter(
        NUMBER_RE.findall(source_text)
    ) != Counter(NUMBER_RE.findall(target_text)):
        errors.append(f"{key}: 숫자 불일치")
    if source_text.count("\\n") != target_text.count("\\n"):
        errors.append(f"{key}: 이스케이프 줄바꿈 불일치")
    if source_text.count("\n") != target_text.count("\n"):
        errors.append(f"{key}: 실제 줄바꿈 불일치")
    if len(source_text) - len(source_text.lstrip()) != len(target_text) - len(
        target_text.lstrip()
    ):
        errors.append(f"{key}: 앞쪽 공백 불일치")
    if len(source_text) - len(source_text.rstrip()) != len(target_text) - len(
        target_text.rstrip()
    ):
        errors.append(f"{key}: 뒤쪽 공백 불일치")
    return errors


def language_audit(instance: Path, errors: list[str]) -> tuple[list[dict], int, int]:
    """현재 JAR 영어, 작업본과 누적 리소스팩을 대조한다."""
    rows: list[dict] = []
    primary_count = 0
    consistency_count = 0
    for target in ALL_TARGETS:
        jar = find_jar(instance, target.jar_prefix)
        member = f"assets/{target.namespace}/lang/en_us.json"
        with zipfile.ZipFile(jar) as archive:
            source = parse_json(
                archive.read(member).decode("utf-8-sig"),
                f"{jar.name}:{member}",
                errors,
                UPSTREAM_DUPLICATE_EXCEPTIONS.get(target.namespace),
            )
        output_path = OUTPUT_ASSETS / target.namespace / "lang/ko_kr.json"
        translated = load_json(output_path, errors)
        if list(source) != list(translated):
            errors.append(f"{target.namespace}: 영어와 누적 한국어 키 또는 순서 불일치")
        if target.ownership == "primary":
            work_en = load_json(WORK_ROOT / target.namespace / "en_us.json", errors)
            work_ko = load_json(WORK_ROOT / target.namespace / "ko_kr.json", errors)
            if list(source.items()) != list(work_en.items()):
                errors.append(
                    f"{target.namespace}: 작업 영어가 현재 JAR 원문과 다릅니다"
                )
            if list(work_en) != list(work_ko):
                errors.append(f"{target.namespace}: 작업 한영 키 또는 순서 불일치")
            if translated != work_ko:
                errors.append(f"{target.namespace}: 누적 출력이 작업 한국어와 다릅니다")
            primary_count += len(source)
        else:
            consistency_count += len(source)
        for key, value in source.items():
            if key not in translated:
                continue
            errors.extend(
                f"{target.namespace}:{message}"
                for message in validate_value(key, value, translated[key])
            )
        collisions: dict[str, set[str]] = defaultdict(set)
        collision_keys: dict[str, list[str]] = defaultdict(list)
        for key, value in translated.items():
            if key.startswith(NAME_PREFIXES) and isinstance(value, str):
                collisions[value].add(str(source.get(key, "")))
                collision_keys[value].append(key)
        induced = {
            value: keys
            for value, keys in collision_keys.items()
            if len(collisions[value]) > 1
        }
        if induced:
            errors.append(f"{target.namespace}: 번역 후 이름 충돌 {induced}")
        rows.append(
            {
                "namespace": target.namespace,
                "jar": jar.name,
                "ownership": target.ownership,
                "keys": len(source),
                "name_collisions": len(induced),
                "upstream_duplicate_keys": sorted(
                    UPSTREAM_DUPLICATE_EXCEPTIONS.get(target.namespace, set())
                ),
                "output_matches": target.ownership != "primary"
                or translated == work_ko,
            }
        )
    return rows, primary_count, consistency_count


def quest_ids(instance: Path) -> tuple[list[dict], list[dict], set[str], set[str]]:
    """지정 네임스페이스를 실제 Task가 사용하는 전용·관련 퀘스트로 좁힌다."""
    chapters, _ = quest_audit.parse_chapters(instance / "config/ftbquests/quests")
    dedicated: list[dict] = []
    related: list[dict] = []
    quest_ids: set[str] = set()
    task_ids: set[str] = set()
    for chapter in chapters:
        chapter_name = Path(chapter["filename"]).stem
        for quest in chapter["quests"]:
            if not any(
                task["item_id"].partition(":")[0] in ALLOWED_NAMESPACES
                for task in quest["tasks"]
            ):
                continue
            row = {"chapter": chapter_name, **quest}
            if chapter_name == DEDICATED_CHAPTER:
                dedicated.append(row)
            else:
                related.append(row)
            quest_ids.add(quest["id"])
            task_ids.update(task["id"] for task in quest["tasks"])
    return dedicated, related, quest_ids, task_ids


def keys_for_objects(language: dict[str, object], quests: list[dict]) -> list[str]:
    qids = {quest["id"] for quest in quests}
    tids = {task["id"] for quest in quests for task in quest["tasks"]}
    return [
        key
        for key in language
        if any(key.startswith(f"quest.{value}.") for value in qids)
        or any(key.startswith(f"task.{value}.") for value in tids)
    ]


def quest_audit_exact(instance: Path, errors: list[str]) -> dict[str, object]:
    """전용·관련 퀘스트의 표시 키와 fallback 결과를 검증한다."""
    dedicated, related, qids, tids = quest_ids(instance)
    current = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    main_en = load_json(WORK_ROOT / "quests/refined_storage/en_us.json", errors)
    main_ko = load_json(WORK_ROOT / "quests/refined_storage/ko_kr.json", errors)
    main_keys = keys_for_objects(main_en, dedicated)
    installed_main = quest_snbt.parse_language_snbt(
        instance
        / "config/ftbquests/quests/lang/en_us/chapters/refined_storage.snbt_merged"
    )
    for key in main_keys:
        if installed_main.get(key) != main_en[key]:
            errors.append(f"FTB:{key}: 작업 영어가 현재 원문과 다릅니다")
        errors.extend(
            f"FTB:{message}"
            for message in validate_value(key, main_en[key], main_ko[key])
        )
        if flatten(main_ko[key]) or not key.startswith("task."):
            if current.get(key) != main_ko[key]:
                errors.append(f"FTB:{key}: 누적 출력 불일치")
        elif key in current:
            errors.append(f"FTB:{key}: 빈 Task 제목이 누적 출력에 남아 있습니다")

    related_en = load_json(WORK_ROOT / "quests/related/en_us.json", errors)
    related_ko = load_json(WORK_ROOT / "quests/related/ko_kr.json", errors)
    related_keys = keys_for_objects(related_en, related)
    for key in related_keys:
        errors.extend(
            f"FTB:{message}"
            for message in validate_value(key, related_en[key], related_ko[key])
        )
        if current.get(key) != related_ko[key]:
            errors.append(f"FTB:{key}: 관련 퀘스트 누적 출력 불일치")

    fallback_rows: list[dict[str, str]] = []
    output_languages: dict[str, str] = {}
    for path in OUTPUT_ASSETS.glob("*/lang/ko_kr.json"):
        values = load_json(path, errors)
        output_languages.update(
            {key: value for key, value in values.items() if isinstance(value, str)}
        )
    for quest in dedicated + related:
        quest_key = f"quest.{quest['id']}.title"
        if isinstance(current.get(quest_key), str) and current[quest_key]:
            resolved = current[quest_key]
            route = "quest.title"
        else:
            first = quest["tasks"][0]
            task_key = f"task.{first['id']}.title"
            if isinstance(current.get(task_key), str) and current[task_key]:
                resolved = current[task_key]
                route = "task.title"
            elif first["custom_name"]:
                resolved = first["custom_name"]
                route = "custom_name"
            else:
                namespace, item_path = first["item_id"].partition(":")[::2]
                candidates = (
                    f"item.{namespace}.{item_path}",
                    f"block.{namespace}.{item_path}",
                )
                resolved = next(
                    (
                        output_languages[key]
                        for key in candidates
                        if key in output_languages
                    ),
                    "",
                )
                route = "item_hover"
            if not resolved:
                errors.append(
                    f"FTB:{quest['id']}: 첫 Task fallback 제목을 해석하지 못했습니다"
                )
        fallback_rows.append(
            {"quest": quest["id"], "route": route, "resolved": str(resolved)}
        )
    return {
        "quests": len(qids),
        "tasks": len(tids),
        "main_display_keys": len(main_keys),
        "related_display_keys": len(related_keys),
        "display_keys": len(main_keys) + len(related_keys),
        "fallbacks_checked": len(fallback_rows),
        "fallback_routes": dict(Counter(row["route"] for row in fallback_rows)),
    }


def other_surfaces(instance: Path) -> dict[str, object]:
    """가이드·발전 과제·KubeJS의 실제 소유 경로를 센다."""
    guide_files = 0
    advancement_files = 0
    advancement_displays = 0
    for target in PRIMARY_TARGETS:
        jar = find_jar(instance, target.jar_prefix)
        with zipfile.ZipFile(jar) as archive:
            names = archive.namelist()
            guide_files += sum(
                any(
                    token in name.lower()
                    for token in ("/patchouli_books/", "/guideme/", "/modonomicon/")
                )
                for name in names
            )
            for name in names:
                if "/advancement/" not in name or not name.endswith(".json"):
                    continue
                advancement_files += 1
                try:
                    value = json.loads(archive.read(name).decode("utf-8-sig"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if isinstance(value, dict) and isinstance(value.get("display"), dict):
                    advancement_displays += 1
    kubejs = instance / "kubejs"
    announcement = kubejs / "server_scripts/announcements/announcements.js"
    visible_announcements = int(
        announcement.is_file()
        and "추가된 모드:" in announcement.read_text(encoding="utf-8-sig")
        and "RefinedTypes" in announcement.read_text(encoding="utf-8-sig")
    )
    return {
        "guides": guide_files,
        "advancement_files": advancement_files,
        "advancement_displays": advancement_displays,
        "kubejs_visible_strings": visible_announcements,
        "kubejs_note": "RefinedTypes 추가 공지는 이미 한국어이며, 나머지는 레시피·ID 참조입니다.",
    }


def deployment_audit(path: Path | None, errors: list[str]) -> dict[str, object]:
    """적용 스크립트의 백업·해시·예상 밖 변경 결과를 검증한다."""
    if path is None:
        return {"status": "not_checked"}
    manifest = json.loads(path.read_text(encoding="utf-8-sig"))
    targets = manifest.get("targets", [])
    if manifest.get("status") != "applied_and_verified" or len(targets) != 1:
        errors.append("적용 매니페스트 상태 또는 대상 수가 올바르지 않습니다")
        return {"status": "invalid", "backup_manifest": str(path)}
    target = targets[0]
    changed = set(target.get("changed_paths", []))
    if changed != EXPECTED_DEPLOYMENTS:
        errors.append(f"실제 적용 파일 불일치: {sorted(changed)}")
    unexpected = target.get("unexpected_changes", [])
    if unexpected:
        errors.append(f"계획하지 않은 실제 인스턴스 변경: {unexpected}")
    files = target.get("files", [])
    hash_matches = sum(
        row.get("source_sha256") == row.get("after_sha256") for row in files
    )
    if hash_matches != len(EXPECTED_DEPLOYMENTS):
        errors.append(
            f"적용 후 해시 불일치: {hash_matches}/{len(EXPECTED_DEPLOYMENTS)}"
        )
    return {
        "status": target.get("status"),
        "target": target.get("target_root"),
        "backup_manifest": str(path.resolve()),
        "changed_paths": sorted(changed),
        "hash_matches": hash_matches,
        "unexpected_changes": unexpected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--backup-manifest", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    errors: list[str] = []
    languages, primary_count, consistency_count = language_audit(instance, errors)
    quests = quest_audit_exact(instance, errors)
    surfaces = other_surfaces(instance)
    deployment = deployment_audit(args.backup_manifest, errors)
    actual = {
        "primary_language_keys": primary_count,
        "consistency_language_keys": consistency_count,
        "quest_display_keys": quests["display_keys"],
        "quests": quests["quests"],
        "tasks": quests["tasks"],
    }
    for key, expected in EXPECTED.items():
        if actual[key] != expected:
            errors.append(f"범위 수 불일치: {key}={actual[key]} (예상 {expected})")
    if REVIEW_STATS["reviewed"] != sum(
        (primary_count, consistency_count, quests["display_keys"])
    ):
        errors.append("완료 통계의 전체 검수 수가 실제 범위와 다릅니다")
    if (
        REVIEW_STATS["unchanged"]
        + REVIEW_STATS["corrected"]
        + REVIEW_STATS["missing_added"]
        != REVIEW_STATS["reviewed"]
    ):
        errors.append("완료 통계 합계가 맞지 않습니다")
    report = {
        "family": "Refined Storage 2",
        "scope": {
            "primary": [target.namespace for target in PRIMARY_TARGETS],
            "consistency_only": [target.namespace for target in CONSISTENCY_TARGETS],
            "excluded": [
                "cabletiers",
                "interdimensionalwirelesstransmitter",
                "refinedstorage_quartz_arsenal",
            ],
        },
        "review_stats": REVIEW_STATS,
        "languages": languages,
        "quests": quests,
        "surfaces": surfaces,
        "deployment": deployment,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    if args.write_report:
        REPORT_PATH.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
