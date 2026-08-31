#!/usr/bin/env python3
"""Just Enough Archaeology의 현재 JAR 영어 전체를 번역하고 검증한다."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "jearchaeology"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
LANG_ROOT = WORK_ROOT / FAMILY
OUTPUT_LANG = (
    active_output_root()
    / "resourcepack/ATM10_Korean/assets/jearchaeology/lang/ko_kr.json"
)
JAR_PATTERN = "jearchaeology-*.jar"
JAR_ENGLISH = "assets/jearchaeology/lang/en_us.json"
JAR_KOREAN = "assets/jearchaeology/lang/ko_kr.json"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[./xX×]\d+)*")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
BRACKET_TOKEN = re.compile(r"\[(?:ATM|BA|C|UC|R)\]")

FIXED_BY_KEY = {
    "emi.category.jearchaeology.brushing": "솔질",
    "emi.category.jearchaeology.sniffing": "스니퍼의 냄새 맡기",
    "jearchaeology.recipe.brush": "솔질",
    "jearchaeology.recipe.sniff": "스니퍼의 냄새 맡기",
    "jearchaeology.brush.structure.desert_well": "사막 우물",
    "jearchaeology.brush.structure.desert_pyramid": "사막 피라미드",
    "jearchaeology.brush.structure.trail_ruins_common": "흔적 폐허",
    "jearchaeology.brush.structure.trail_ruins_rare": "흔적 폐허",
    "jearchaeology.brush.structure.ocean_ruin_warm": "따뜻한 바다 폐허",
    "jearchaeology.brush.structure.ocean_ruin_cold": "차가운 바다 폐허",
    "jearchaeology.brush.structure.bastion": "보루 잔해 [ATM]",
    "jearchaeology.brush.structure.ancient_city": "고대 도시 [ATM]",
    "jearchaeology.brush.structure.buried_ruins_or_obelist": (
        "매몰된 폐허 및 사막 오벨리스크 [BA]"
    ),
    "jearchaeology.brush.structure.archeologist_camp_sand": "고고학자 야영지 [BA]",
    "jearchaeology.brush.structure.archeologist_camp_redsand": "고고학자 야영지 [BA]",
    "jearchaeology.brush.structure.archeologist_camp_grassy": "고고학자 야영지 [BA]",
    "jearchaeology.brush.structure.underwater": "수중 수상한 모래 [BA]",
    "jearchaeology.brush.structure.plains_gravel": "스톤헨지 [BA]",
    "jearchaeology.brush.structure.fossil_chicken": "닭 화석 [BA]",
    "jearchaeology.brush.structure.fossil_creeper": "크리퍼 화석 [BA]",
    "jearchaeology.brush.structure.fossil_jungle": "오셀롯 화석 [BA]",
    "jearchaeology.brush.structure.fossil_sheep": "양 화석 [BA]",
    "jearchaeology.brush.structure.fossil_villager": "주민 화석 [BA]",
    "jearchaeology.brush.structure.archaeological_site_rare": "고고학 유적지 [R]",
    "jearchaeology.brush.structure.archaeological_site": "고고학 유적지",
    "jearchaeology.brush.structure.wishing_weald": "소원의 숲",
    "jearchaeology.brush.structure.observatory": "천문대",
}

PREHISTORIC_NAMES = {
    "lush_den": "선사 시대의 무성한 굴",
    "sandy_den": "선사 시대의 모래 굴",
    "sunscorched_den": "선사 시대의 햇볕에 그을린 굴",
    "enhydro_agate": "선사 시대의 엔하이드로 마노",
    "eroded_pillar": "선사 시대의 침식된 기둥",
    "frozen_spike": "선사 시대의 얼어붙은 첨탑",
    "powdered_deposit": "선사 시대의 가루 퇴적층",
    "preserved_skeleton": "선사 시대의 보존된 골격",
    "submerged_impact": "선사 시대의 물에 잠긴 충돌구",
    "submerged_spike": "선사 시대의 물에 잠긴 첨탑",
    "sunscorched_remains": "선사 시대의 햇볕에 그을린 유적",
    "suspicious_mound": "선사 시대의 수상한 둔덕",
    "underwater_fissure": "선사 시대의 수중 균열",
    "mud_pit": "선사 시대의 진흙 구덩이",
    "rooted_pit": "선사 시대의 뿌리내린 구덩이",
    "dripstone_oasis": "선사 시대의 점적석 오아시스",
    "frozen_pond": "선사 시대의 얼어붙은 연못",
    "mossy_pond": "선사 시대의 이끼 낀 연못",
    "birch_tree": "선사 시대의 자작나무",
    "oak_tree": "선사 시대의 참나무",
    "spruce_tree": "선사 시대의 가문비나무",
    "hydrothermal_vents": "선사 시대의 열수 분출공",
    "vibrant_hydrothermal_vents": "선사 시대의 생기 넘치는 열수 분출공",
}

RUIN_NAMES = {
    "deserted_tower_ruins": "버려진 탑 폐허",
    "deserted_gimmi_tower": "버려진 Gimmi 탑",
    "frozen_gimmi_tower": "얼어붙은 Gimmi 탑",
    "lush_gimmi_tower": "무성한 Gimmi 탑",
    "rooted_gimmi_tower": "뿌리내린 Gimmi 탑",
    "sunscorched_gimmi_tower": "햇볕에 그을린 Gimmi 탑",
    "temperate_gimmi_tower": "온대 Gimmi 탑",
    "stonjourner_henge_ruins": "Stonjourner 환상열석 폐허",
    "sol_henge_ruins": "Sol 환상열석 폐허",
    "luna_henge_ruins": "Luna 환상열석 폐허",
    "crumbling_arch_ruins": "무너져 가는 아치 폐허",
    "rooted_arch_ruins": "뿌리내린 아치 폐허",
    "decaying_crypt_ruins": "쇠락한 지하 묘지 폐허",
    "deserted_house_ruins": "버려진 집 폐허",
    "deserted_town_center_ruins": "버려진 마을 중심부 폐허",
    "fallen_statue_ruins": "쓰러진 조각상 폐허",
    "hidden_bunker_ruins": "숨겨진 벙커 폐허",
    "mossy_oubliette_ruins": "이끼 낀 밀실 감옥 폐허",
    "toppled_pillars_ruins": "쓰러진 기둥 폐허",
    "unstable_cave_ruins": "불안정한 동굴 폐허",
}

RARITY_SUFFIXES = (
    ("_rare_automaton", " [R]"),
    ("_rare_bottom", " [R]"),
    ("_rare_top", " [R]"),
    ("_uncommon", " [UC]"),
    ("_common", " [C]"),
    ("_rare", " [R]"),
)

OPTIONAL_COMPAT_JARS = {
    "better_archeology": ("*BetterArcheology*.jar", "*betterarcheology*.jar"),
    "cobblemon": ("*Cobblemon*.jar", "*cobblemon-*.jar"),
    "mega_showdown": ("*MegaShowdown*.jar", "*mega_showdown*.jar"),
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없이 JSON을 기록한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    """파일의 SHA-256 해시를 계산한다."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_jar(instance: Path) -> Path:
    """현재 설치본의 Just Enough Archaeology JAR 하나를 찾는다."""
    jars = sorted((instance / "mods").glob(JAR_PATTERN))
    if len(jars) != 1:
        raise RuntimeError(
            f"대상 JAR 수가 1개가 아닙니다: {[path.name for path in jars]}"
        )
    return jars[0]


def read_jar_english(jar: Path) -> dict[str, object]:
    """원본 JAR에서 영어 언어 파일을 읽는다."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read(JAR_ENGLISH))
    if not isinstance(value, dict):
        raise TypeError(f"JAR 영어 언어 파일이 객체가 아닙니다: {jar}")
    return value


def prepare() -> dict[str, object]:
    """현재 JAR 영어를 작업본으로 추출한다."""
    instance = resolve_source_root()
    jar = source_jar(instance)
    english = read_jar_english(jar)
    with ZipFile(jar) as archive:
        bundled_korean = JAR_KOREAN in archive.namelist()
    write_json(LANG_ROOT / "en_us.json", english)
    write_json(
        LANG_ROOT / "candidate_sources.json",
        {key: "manual_current_en_us" for key in english},
    )
    report = {
        "family": FAMILY,
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_mtime_ns": jar.stat().st_mtime_ns,
        "language_namespace": FAMILY,
        "english_keys": len(english),
        "bundled_korean": bundled_korean,
        "existing_korean_reused": 0,
        "new_translation_keys": len(english),
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", report)
    return report


def split_rarity(identifier: str) -> tuple[str, str]:
    """키 식별자에서 희귀도 접미사를 분리한다."""
    for suffix, label in RARITY_SUFFIXES:
        if identifier.endswith(suffix):
            return identifier[: -len(suffix)], label
    raise KeyError(f"희귀도 접미사를 해석할 수 없습니다: {identifier}")


def translate_key(key: str) -> str:
    """검수된 키별 규칙으로 한국어 값을 만든다."""
    if key in FIXED_BY_KEY:
        return FIXED_BY_KEY[key]
    prefix = "jearchaeology.brush.structure."
    if not key.startswith(prefix):
        raise KeyError(f"번역 규칙이 없는 키입니다: {key}")
    identifier, rarity = split_rarity(key.removeprefix(prefix))
    if identifier.startswith("prehistoric_"):
        base = identifier.removeprefix("prehistoric_")
        if base not in PREHISTORIC_NAMES:
            raise KeyError(f"선사시대 구조물 번역이 없습니다: {base}")
        return PREHISTORIC_NAMES[base] + rarity
    if identifier not in RUIN_NAMES:
        raise KeyError(f"폐허 구조물 번역이 없습니다: {identifier}")
    return RUIN_NAMES[identifier] + rarity


def build() -> dict[str, object]:
    """전체 영어 키의 검수된 한국어를 생성한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    korean = {key: translate_key(key) for key in english}
    write_json(LANG_ROOT / "ko_kr.json", korean)
    write_json(OUTPUT_LANG, korean)
    report = {
        "reviewed_keys": len(korean),
        "existing_korean_reused": 0,
        "new_translation_keys": len(korean),
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def scan_text_surfaces(instance: Path) -> tuple[list[str], list[str]]:
    """퀘스트·KubeJS·기존 리소스팩의 직접 표시 문자열을 찾는다."""
    matches: list[str] = []
    errors: list[str] = []
    extensions = {".json", ".snbt", ".js", ".txt", ".toml", ".mcmeta"}
    for relative in ("config/ftbquests", "kubejs", "resourcepacks"):
        root = instance / relative
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            if path.suffix.lower() not in extensions:
                continue
            relative_path = path.relative_to(instance).as_posix()
            if (
                relative_path
                == "resourcepacks/ATM10_Korean/assets/jearchaeology/lang/ko_kr.json"
            ):
                continue
            try:
                lines = path.read_text(encoding="utf-8-sig").splitlines()
            except UnicodeDecodeError as exc:
                errors.append(f"{relative_path}: {exc}")
                continue
            for number, line in enumerate(lines, 1):
                if "jearchaeology" in line.lower():
                    matches.append(f"{relative_path}:{number}:{line.strip()}")
    return matches, errors


def audit() -> tuple[dict[str, object], list[str]]:
    """언어 외 표시 표면과 선택적 호환 모드 설치 여부를 감사한다."""
    instance = resolve_source_root()
    jar = source_jar(instance)
    with ZipFile(jar) as archive:
        names = archive.namelist()
        json_entries = sorted(
            name for name in names if name.endswith((".json", ".mcmeta", ".toml"))
        )
        visible_data = sorted(
            name
            for name in names
            if name.startswith("data/")
            and name.endswith(".json")
            and any(token in name for token in ("advancement", "guide", "patchouli"))
        )
    matches, errors = scan_text_surfaces(instance)
    installed_compatibility = {}
    for label, patterns in OPTIONAL_COMPAT_JARS.items():
        installed_compatibility[label] = sorted(
            {
                path.name
                for pattern in patterns
                for path in (instance / "mods").glob(pattern)
            }
        )
    report = {
        "family": FAMILY,
        "jar": jar.name,
        "jar_visible_entries": json_entries,
        "jar_advancement_guide_entries": visible_data,
        "related_ftbquests_kubejs_resourcepack_matches": matches,
        "optional_compatibility_jars": installed_compatibility,
        "metadata_note": (
            "mods.toml의 영문 설명은 언어 키를 사용하지 않는 모드 목록 메타데이터이므로 "
            "리소스팩 번역 대상이 아닙니다."
        ),
        "scan_errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """현재 JAR·작업본·산출물의 구조와 번역 보존 규칙을 검증한다."""
    instance = resolve_source_root()
    jar = source_jar(instance)
    jar_english = read_jar_english(jar)
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    output = load_json(OUTPUT_LANG)
    audit_report = load_json(WORK_ROOT / "surface_audit.json")
    errors: list[str] = []
    untranslated: list[str] = []
    latin_residue: dict[str, list[str]] = {}
    if jar_english != english:
        errors.append("작업 영어가 현재 설치 JAR 영어와 다릅니다")
    if list(english) != list(korean):
        errors.append("한국어 키 또는 키 순서가 영어 원문과 다릅니다")
    if korean != output:
        errors.append("작업 한국어와 리소스팩 산출물이 다릅니다")
    for key in english.keys() & korean.keys():
        source = english[key]
        target = korean[key]
        if type(source) is not type(target):
            errors.append(f"자료형 불일치: {key}")
            continue
        if not isinstance(source, str) or not isinstance(target, str):
            continue
        for label, pattern in (
            ("자리표시자", PLACEHOLDER),
            ("서식 코드", FORMAT_CODE),
            ("숫자", NUMBER),
            ("보호 약어", BRACKET_TOKEN),
        ):
            if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
                errors.append(f"{label} 불일치: {key}")
        if source.count("\\n") != target.count("\\n"):
            errors.append(f"줄바꿈 불일치: {key}")
        if source == target and LATIN_WORD.search(source):
            untranslated.append(key)
        residue = sorted(
            set(LATIN_WORD.findall(target))
            - {"ATM", "Gimmi", "Luna", "Sol", "Stonjourner"}
        )
        if residue:
            latin_residue[key] = residue
    collisions: dict[str, list[str]] = defaultdict(list)
    for key, target in korean.items():
        if isinstance(target, str):
            collisions[target].append(key)
    unexpected_collisions = {
        target: keys
        for target, keys in collisions.items()
        if len(keys) > 1 and len({english[key] for key in keys}) > 1
    }
    if untranslated:
        errors.append(f"영어와 같은 미번역 후보가 있습니다: {untranslated}")
    if latin_residue:
        errors.append(f"허용하지 않은 영문 잔여가 있습니다: {latin_residue}")
    if unexpected_collisions:
        errors.append(
            f"서로 다른 영어 이름의 한국어 충돌이 있습니다: {unexpected_collisions}"
        )
    if audit_report.get("status") != "complete":
        errors.append("표시 표면 감사가 완료되지 않았습니다")
    report = {
        "family": FAMILY,
        "jar": jar.name,
        "keys": len(english),
        "existing_korean_reused": 0,
        "new_translation_keys": len(korean),
        "untranslated_candidates": untranslated,
        "latin_residue": latin_residue,
        "unexpected_name_collisions": unexpected_collisions,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "language_validation.json", report)
    completion = {
        "family": FAMILY,
        "version": "1.21.1-1.2.0",
        "language_keys": len(korean),
        "existing_korean_reused": 0,
        "new_translation_keys": len(korean),
        "related_ftbquests": 0,
        "related_kubejs": 0,
        "guides_advancements": 0,
        "output_files": [OUTPUT_LANG.relative_to(PROJECT_ROOT).as_posix()],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_completion.json", completion)
    return report, errors


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 스크립트의 백업·해시 검증 결과를 완료 기록에 반영한다."""
    resolved_manifest = manifest_path.resolve()
    try:
        relative_manifest = resolved_manifest.relative_to(PROJECT_ROOT).as_posix()
    except ValueError as exc:
        raise ValueError(f"프로젝트 밖의 적용 기록입니다: {resolved_manifest}") from exc
    manifest = load_json(resolved_manifest)
    completion_path = WORK_ROOT / "family_completion.json"
    completion = load_json(completion_path)
    selected_path = "resourcepacks/ATM10_Korean/assets/jearchaeology/lang/ko_kr.json"
    errors: list[str] = []
    matched_targets: list[dict[str, object]] = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 기록 상태가 applied_and_verified가 아닙니다")
    targets = manifest.get("targets")
    if not isinstance(targets, list):
        errors.append("적용 기록의 targets가 목록이 아닙니다")
        targets = []
    for target in targets:
        if not isinstance(target, dict):
            continue
        files = target.get("files")
        if not isinstance(files, list):
            continue
        matching = [
            row
            for row in files
            if isinstance(row, dict) and row.get("relative_path") == selected_path
        ]
        if len(matching) != 1:
            continue
        row = matching[0]
        target_file = Path(str(row.get("target")))
        if not target_file.is_file():
            errors.append(f"적용 대상 파일이 없습니다: {target_file}")
        elif sha256(target_file) != sha256(OUTPUT_LANG):
            errors.append(f"적용 대상과 산출물의 해시가 다릅니다: {target_file}")
        if row.get("source_sha256") != row.get("after_sha256"):
            errors.append(f"적용 기록의 전후 해시가 다릅니다: {target_file}")
        matched_targets.append(target)
    if len(matched_targets) != 1:
        errors.append(f"대상 적용 기록 수가 1개가 아닙니다: {len(matched_targets)}")
    target = matched_targets[0] if matched_targets else {}
    deployment = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "target": target.get("target_root"),
        "changed_paths": target.get("changed_paths", []),
        "backup_manifest": relative_manifest,
        "output_sha256": sha256(OUTPUT_LANG),
        "errors": errors,
    }
    completion["deployment"] = deployment
    if errors:
        completion["status"] = "incomplete"
    write_json(completion_path, completion)
    return deployment, errors


def run_all() -> tuple[dict[str, object], list[str]]:
    """준비부터 감사·빌드·검증까지 순서대로 실행한다."""
    prepare_report = prepare()
    audit_report, audit_errors = audit()
    build_report = build()
    verify_report, verify_errors = verify()
    result = {
        "prepare": prepare_report,
        "audit": audit_report,
        "build": build_report,
        "verify": verify_report,
        "status": "complete"
        if not audit_errors and not verify_errors
        else "incomplete",
    }
    return result, audit_errors + verify_errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "audit", "build", "verify", "record-deployment", "all"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        report, errors = prepare(), []
    elif args.command == "audit":
        report, errors = audit()
    elif args.command == "build":
        report, errors = build(), []
    elif args.command == "verify":
        report, errors = verify()
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요합니다")
        report, errors = record_deployment(args.manifest)
    else:
        report, errors = run_all()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
