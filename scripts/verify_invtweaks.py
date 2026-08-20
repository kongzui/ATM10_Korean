#!/usr/bin/env python3
"""Inventory Tweaks 번역과 키 설정·정렬·설정 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root

WORK_ROOT = PROJECT_ROOT / "working/common_ui/inventory_controls/invtweaks"
SOURCES = WORK_ROOT / "display_sources.json"
WORKING = WORK_ROOT / "ko_kr.json"
OVERRIDES = WORK_ROOT / "recheck_overrides.json"
REPORT = WORK_ROOT / "recheck_20260820.json"
OUTPUT = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/invtweaks/lang/ko_kr.json"
)
GLOSSARY = PROJECT_ROOT / "glossary/README.md"

EXPECTED_JAR = "invtweaks-1.21.1-1.3.2.jar"
EXPECTED_JAR_SHA256 = "ceb5b20a43ca1c5bd707f60bb5d5fa61099c7a7ba50b19f6bddfe93f1ca0073c"
EXPECTED_CONFIG_SHA256 = (
    "7db2a9a1c7e8f7cb78bfec7202a03fe350d11054b74821051ab5d6e2dde3e914"
)
EXPECTED_BACKUP_SHA256 = (
    "bfd7a47f2a57b89a097dff2472c77c8332b61dc961b995c59bb2766dca480e20"
)
EXPECTED_SOURCE_SHA256 = (
    "03f6d5e8d718966a25ba5ec9cef56ef7cac9913b2775960667add55199e8f7d2"
)
EXPECTED_OVERRIDE_SHA256 = (
    "ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356"
)
EXPECTED_OUTPUT_SHA256 = (
    "798f3e1faede376a7e91ea96ed66c8b3c11d73fa3b5665d818a04c4b9e692cf4"
)
EXPECTED_ENGLISH = {
    "key.categories.invtweaks": "Inventory Tweaks ReFoxed",
    "key.invtweaks_sort_player.desc": "Sort Player Inventory",
    "key.invtweaks_sort_inventory.desc": "Sort External Inventory",
    "key.invtweaks_sort_either.desc": "Sort Inventory Under Cursor",
}
EXPECTED_KOREAN = {
    "key.categories.invtweaks": "Inventory Tweaks ReFoxed",
    "key.invtweaks_sort_player.desc": "플레이어 인벤토리 정렬",
    "key.invtweaks_sort_inventory.desc": "외부 인벤토리 정렬",
    "key.invtweaks_sort_either.desc": "커서 아래의 인벤토리 정렬",
    "fml.menu.mods.info.description.invtweaks": (
        "현대 버전의 Minecraft용 Inventory Tweaks입니다."
    ),
}
EXPECTED_CONFIG_OPTIONS = {
    "autoRefill",
    "category",
    "containerOverrides",
    "enableButtons",
    "enableDebug",
    "enableSort",
    "quickView",
    "rules",
}
GLOSSARY_ROW = "| Inventory Tweaks ReFoxed | Inventory Tweaks ReFoxed | 공식 모드명 |"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
NUMBER = re.compile(r"(?<![A-Za-z0-9_])\d+(?:\.\d+)?")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
ENGLISH_LANGUAGE = re.compile(r"assets/[^/]+/lang/en_us\.json")
DIRECT_REFERENCE = re.compile(r"(?i)invtweaks(?:[.:/\\]|\b)|inventory tweaks")
RELATED_EXTENSIONS = {".js", ".json", ".snbt", ".toml", ".txt"}
FORBIDDEN_TRANSLATIONS = re.compile(r"인벤토리 트윅|인벤토리 조정|Refoxed")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_strings(data: bytes, label: str) -> dict[str, str]:
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
        raise TypeError(f"문자열 JSON 객체가 아닙니다: {label}")
    return value


def load_path(path: Path) -> dict[str, str]:
    return load_strings(path.read_bytes(), str(path))


def find_related_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in RELATED_EXTENSIONS
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
    result: set[str] = set()
    section = ""
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        table = re.fullmatch(
            r"\[\[(sorting)\.(category|containerOverrides)\]\]", stripped
        )
        if table:
            section = f"{table.group(1)}.{table.group(2)}"
            result.add(table.group(2))
            continue
        simple = re.fullmatch(r"\[(sorting|tweaks)\]", stripped)
        if simple:
            section = simple.group(1)
            continue
        if (
            section in {"sorting", "tweaks"}
            and stripped
            and not stripped.startswith("#")
        ):
            if "=" in stripped:
                result.add(stripped.split("=", 1)[0].strip())
    return result


def verify_language_owners(
    instance: Path, expected_keys: set[str]
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
                    if jar_path.name == EXPECTED_JAR and name == (
                        "assets/invtweaks/lang/en_us.json"
                    ):
                        continue
                    value = json.loads(archive.read(name).decode("utf-8-sig"))
                    if isinstance(value, dict):
                        for key in expected_keys & set(value):
                            overlaps.append(f"{jar_path.name}:{name}:{key}")
        except BadZipFile as error:
            raise RuntimeError(f"손상된 모드 JAR: {jar_path}") from error
    if overlaps:
        raise RuntimeError(f"Inventory Tweaks 언어 키 소유자 중복: {overlaps[:20]}")
    return jar_count, language_count, len(overlaps)


def verify(pre_apply: bool) -> dict[str, object]:
    instance = resolve_source_root(None)
    errors: list[str] = []
    source_jar = instance / "mods" / EXPECTED_JAR
    config = instance / "config/invtweaks-client.toml"
    backup = instance / "config/invtweaks-client-1.toml.bak"
    if sha256(source_jar) != EXPECTED_JAR_SHA256:
        errors.append("Inventory Tweaks 원본 JAR 해시가 변경되었습니다")
    if sha256(config) != EXPECTED_CONFIG_SHA256:
        errors.append("Inventory Tweaks 클라이언트 설정 해시가 변경되었습니다")
    if sha256(backup) != EXPECTED_BACKUP_SHA256:
        errors.append("Inventory Tweaks 설정 백업 해시가 변경되었습니다")

    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        classes = [name for name in names if name.endswith(".class")]
        language_files = [
            name
            for name in names
            if re.fullmatch(r"assets/invtweaks/lang/[^/]+\.json", name)
        ]
        english = load_strings(
            archive.read("assets/invtweaks/lang/en_us.json"),
            "Inventory Tweaks en_us",
        )
        key_mappings = archive.read("invtweaks/events/KeyMappings.class")
        sort_button = archive.read("invtweaks/gui/InvTweaksButtonSort.class")
        packet_sort = archive.read("invtweaks/network/PacketSortInv.class")
        config_class = archive.read("invtweaks/config/InvTweaksConfig.class")
        all_classes = b"".join(archive.read(name) for name in classes)
        metadata = archive.read("META-INF/neoforge.mods.toml").decode("utf-8")
        data_files = [name for name in names if name.startswith("data/")]
        guide_files = [
            name
            for name in names
            if any(
                token in name.lower()
                for token in ("patchouli", "guideme", "modonomicon")
            )
        ]

    sources = load_path(SOURCES)
    working = load_path(WORKING)
    output = load_path(OUTPUT)
    overrides = load_path(OVERRIDES)
    if len(names) != 46 or len(classes) != 22 or len(language_files) != 5:
        errors.append("Inventory Tweaks JAR 엔트리·클래스·언어 파일 수 불일치")
    if "assets/invtweaks/lang/ko_kr.json" in language_files:
        errors.append("예상 밖의 Inventory Tweaks 내장 한국어가 있습니다")
    if english != EXPECTED_ENGLISH:
        errors.append("Inventory Tweaks 설치 영어 원문이 변경되었습니다")
    if working != EXPECTED_KOREAN or output != EXPECTED_KOREAN or working != output:
        errors.append("Inventory Tweaks 작업본·산출물·확정 번역 불일치")
    if (
        sources
        != {
            "fml.menu.mods.info.description.invtweaks": (
                "Inventory Tweaks, but for modern versions of Minecraft."
            )
        }
        or overrides
        or sha256(SOURCES) != EXPECTED_SOURCE_SHA256
        or sha256(OVERRIDES) != EXPECTED_OVERRIDE_SHA256
        or sha256(OUTPUT) != EXPECTED_OUTPUT_SHA256
    ):
        errors.append("Inventory Tweaks 표시 원문·교정표·산출물 해시 불일치")

    if not all(key.encode("utf-8") in key_mappings for key in english):
        errors.append("Inventory Tweaks 단축키 등록 경로 누락")
    if b"net/minecraft/network/chat/Component" in sort_button:
        errors.append("Inventory Tweaks 정렬 버튼의 예상 밖 텍스트 표시 경로")
    if (
        b"Failed to sort inventory" not in packet_sort
        or b"org/apache/logging/log4j/Logger" not in packet_sort
        or b"net/minecraft/network/chat/Component" in packet_sort
    ):
        errors.append("Inventory Tweaks 정렬 실패 로그 표시 경로가 변경되었습니다")
    if b"IConfigScreenFactory" in all_classes:
        errors.append("Inventory Tweaks 예상 밖의 게임 내 설정 화면 경로")
    if config_options(config) != EXPECTED_CONFIG_OPTIONS or not all(
        option.encode("utf-8") in config_class for option in EXPECTED_CONFIG_OPTIONS
    ):
        errors.append("Inventory Tweaks 설정 옵션·클래스 대응 불일치")
    if data_files or guide_files:
        errors.append("Inventory Tweaks 예상 밖의 데이터·발전 과제·가이드 자산")
    if (
        'displayName="Inventory Tweaks Refoxed"' not in metadata
        or "description='''Inventory Tweaks, but for modern versions of Minecraft.'''"
        not in metadata
    ):
        errors.append("Inventory Tweaks 모드 메타데이터 표시 경로 불일치")

    for key in english:
        if PLACEHOLDER.findall(english[key]) != PLACEHOLDER.findall(output[key]):
            errors.append(f"자리표시자 불일치: {key}")
        if NUMBER.findall(english[key]) != NUMBER.findall(output[key]):
            errors.append(f"숫자 불일치: {key}")
        if english[key].count("\n") != output[key].count("\n"):
            errors.append(f"줄바꿈 불일치: {key}")
        if Counter(FORMAT_CODE.findall(english[key])) != Counter(
            FORMAT_CODE.findall(output[key])
        ):
            errors.append(f"서식 코드 불일치: {key}")
    forbidden = FORBIDDEN_TRANSLATIONS.findall("\n".join(output.values()))
    if forbidden:
        errors.append(f"Inventory Tweaks 금지 표기 잔존: {sorted(set(forbidden))}")
    related_guide = (
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/advanced_ae/ae2guide/_ko_kr/"
        "aae_intro/advanced_io_bus.md"
    )
    if "외부 인벤토리" not in related_guide.read_text(encoding="utf-8"):
        errors.append("Inventory Tweaks 관련 모드 외부 인벤토리 용어 불일치")

    quest_files = find_related_files(instance / "config/ftbquests/quests")
    quest_refs = direct_references(instance, quest_files)
    kube_files = find_related_files(instance / "kubejs")
    kube_refs = direct_references(instance, kube_files)
    if len(quest_files) != 142 or quest_refs:
        errors.append(f"Inventory Tweaks FTB Quests 직접 참조 불일치: {quest_refs}")
    if len(kube_files) != 894 or kube_refs:
        errors.append(f"Inventory Tweaks KubeJS 직접 참조 불일치: {kube_refs}")

    jar_count, english_count, owner_overlaps = verify_language_owners(
        instance, set(output)
    )
    project_languages = list(
        (PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets").glob(
            "*/lang/ko_kr.json"
        )
    )
    if jar_count != 480 or english_count != 388 or len(project_languages) != 286:
        errors.append(
            "설치·프로젝트 언어 집계 변경: "
            f"jars={jar_count}, english={english_count}, "
            f"project={len(project_languages)}"
        )
    if GLOSSARY_ROW not in GLOSSARY.read_text(encoding="utf-8"):
        errors.append("Inventory Tweaks 용어집 행 누락")

    if not pre_apply:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        application = report.get("application") if isinstance(report, dict) else None
        if report.get("validation") != "passed":
            errors.append("Inventory Tweaks 재검수 보고서 상태 불일치")
        if (
            not isinstance(application, dict)
            or application.get("status") != "applied_and_verified"
            or application.get("invtweaks_sha256") != EXPECTED_OUTPUT_SHA256
            or application.get("unexpected_changes") != 0
        ):
            errors.append("Inventory Tweaks 재검수 보고서 적용 집계 불일치")
        target = (
            instance / "resourcepacks/ATM10_Korean/assets/invtweaks/lang/ko_kr.json"
        )
        if not target.exists() or target.read_bytes() != OUTPUT.read_bytes():
            errors.append("실제 source_root의 Inventory Tweaks 산출물이 다릅니다")

    if errors:
        raise RuntimeError(
            "Inventory Tweaks 재검수 검증 실패:\n" + "\n".join(errors[:80])
        )
    return {
        "scope": "Inventory Tweaks 전체 표시 문구 재검수",
        "source_jar": source_jar.name,
        "source_jar_sha256": sha256(source_jar),
        "source_jar_bytes": source_jar.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(classes),
        "language_files_reviewed": len(language_files),
        "source_keys_reviewed": len(english),
        "bundled_korean_candidates_reviewed": 0,
        "project_candidates_retained": len(english),
        "project_candidates_corrected": len(overrides),
        "newly_translated": len(sources),
        "effective_output_keys": len(output),
        "metadata_display_strings_reviewed": len(sources),
        "key_mapping_display_paths_reviewed": len(english),
        "icon_only_sort_button_paths_reviewed": 1,
        "log_only_literals_excluded": 1,
        "configuration_options_reviewed": len(EXPECTED_CONFIG_OPTIONS),
        "configuration_files_read_only_reviewed": 2,
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_reference_files": len(quest_refs),
        "kubejs_files_reviewed": len(kube_files),
        "kubejs_reference_files": len(kube_refs),
        "installed_mod_jars_reviewed": jar_count,
        "installed_english_language_files_reviewed": english_count,
        "other_language_owner_overlaps": owner_overlaps,
        "project_language_files_reviewed": len(project_languages),
        "related_mod_term_paths_reviewed": 1,
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
