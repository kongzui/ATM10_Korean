#!/usr/bin/env python3
"""Mouse Tweaks의 하드코딩 설정 화면과 번역 덮어쓰기를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root

WORK_ROOT = PROJECT_ROOT / "working/common_ui/inventory_controls/mousetweaks"
SOURCES = WORK_ROOT / "display_sources.json"
WORKING = WORK_ROOT / "ko_kr.json"
OVERRIDES = WORK_ROOT / "recheck_overrides.json"
WORKING_SCRIPT = WORK_ROOT / "kubejs/startup_scripts/mousetweaks_config_labels.js"
REPORT = WORK_ROOT / "recheck_20260820.json"
OUTPUT = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/mousetweaks/lang/ko_kr.json"
)
OUTPUT_SCRIPT = (
    PROJECT_ROOT
    / "output/overrides/kubejs/startup_scripts/mousetweaks_config_labels.js"
)
GLOSSARY = PROJECT_ROOT / "glossary/README.md"

EXPECTED_JAR = "MouseTweaks-neoforge-mc1.21-2.26.1.jar"
EXPECTED_JAR_SHA256 = "68e6f4201c5de97b77929a7215c9552495696ca6a3bf3ae4eacc34e135f6cc8b"
EXPECTED_CONFIG_SHA256 = (
    "4069ce1a439d8c37453c1b1e9f2037e0942674c7e48723a39b37eab245792ad4"
)
EXPECTED_SOURCE_SHA256 = (
    "be6d8b4e3025ec7021360f157dc55e38328489a9179860624861192c7fa8ea4e"
)
EXPECTED_OVERRIDE_SHA256 = (
    "ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356"
)
EXPECTED_OUTPUT_SHA256 = (
    "5212e13522777feb24c25d8a01babc5b8e56c12933b914d1bd0e887b7188fdff"
)
EXPECTED_SCRIPT_SHA256 = (
    "7fcd1dee21582b2988886fc4ea4cc1cd27336db22a38d4ea363f2310d39d237b"
)
EXPECTED_KUBEJS_JAR = "kubejs-neoforge-2101.7.2-build.368.jar"
EXPECTED_KUBEJS_SHA256 = (
    "28867299e7a9f02cfd74e34745fdbbb073fe4887fddbc98fd6c1ed2e87b01482"
)
GLOSSARY_ROW = "| Mouse Tweaks | Mouse Tweaks | 공식 모드명 |"
EXPECTED_CONFIG = {
    "Debug": "0",
    "LMBTweakWithItem": "1",
    "LMBTweakWithoutItem": "1",
    "RMBTweak": "1",
    "ScrollItemScaling": "0",
    "WheelScrollDirection": "0",
    "WheelSearchOrder": "1",
    "WheelTweak": "1",
}
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
NUMBER = re.compile(r"(?<![A-Za-z0-9_])\d+(?:\.\d+)?")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
ENGLISH_LANGUAGE = re.compile(r"assets/[^/]+/lang/en_us\.json")
DIRECT_REFERENCE = re.compile(r"(?i)mousetweaks(?:[.:/\\]|\b)|mouse tweaks")
RELATED_EXTENSIONS = {".js", ".json", ".snbt", ".toml", ".txt"}
FORBIDDEN_TRANSLATIONS = re.compile(
    r"마우스 트윅|마우스 조정|오른쪽 마우스 버튼 트윅|왼쪽 마우스 버튼 트윅|"
    r"인벤토리 위치 인식|스크롤 스케일링"
)
NATIVE_PRIORITY_SIGNATURE = (
    b"(Ldev/latvian/mods/rhino/Context;Lnet/neoforged/bus/api/EventPriority;"
    b"Ljava/lang/Class;Ljava/util/function/Consumer;)V"
)


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


def load_config(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key, value = stripped.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def verify_language_owners(
    instance: Path, sources: dict[str, str]
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
                    value = json.loads(archive.read(name).decode("utf-8-sig"))
                    if isinstance(value, dict):
                        for key in set(sources) & set(value):
                            overlaps.append(f"{jar_path.name}:{name}:{key}")
        except BadZipFile as error:
            raise RuntimeError(f"손상된 모드 JAR: {jar_path}") from error
    if overlaps:
        raise RuntimeError(f"Mouse Tweaks 표시 키 기존 소유자 중복: {overlaps[:20]}")
    return jar_count, language_count, len(overlaps)


def verify(pre_apply: bool) -> dict[str, object]:
    instance = resolve_source_root(None)
    errors: list[str] = []
    source_jar = instance / "mods" / EXPECTED_JAR
    config = instance / "config/MouseTweaks.cfg"
    kubejs_jar = instance / "mods" / EXPECTED_KUBEJS_JAR
    if sha256(source_jar) != EXPECTED_JAR_SHA256:
        errors.append("Mouse Tweaks 원본 JAR 해시가 변경되었습니다")
    if sha256(config) != EXPECTED_CONFIG_SHA256:
        errors.append("Mouse Tweaks 설정 파일 해시가 변경되었습니다")
    if sha256(kubejs_jar) != EXPECTED_KUBEJS_SHA256:
        errors.append("KubeJS 원본 JAR 해시가 변경되었습니다")

    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        classes = [name for name in names if name.endswith(".class")]
        language_files = [
            name
            for name in names
            if re.fullmatch(r"assets/[^/]+/lang/[^/]+\.json", name)
        ]
        data_files = [name for name in names if name.startswith("data/mousetweaks/")]
        guide_files = [
            name
            for name in names
            if any(
                token in name.lower()
                for token in ("patchouli", "guideme", "modonomicon")
            )
        ]
        config_screen = archive.read("yalter/mousetweaks/ConfigScreen.class")
        config_class = archive.read("yalter/mousetweaks/Config.class")
        metadata = archive.read("META-INF/neoforge.mods.toml").decode("utf-8")

    with ZipFile(kubejs_jar) as archive:
        native_wrapper = archive.read(
            "dev/latvian/mods/kubejs/plugin/builtin/wrapper/NativeEventWrapper.class"
        )

    sources = load_path(SOURCES)
    working = load_path(WORKING)
    output = load_path(OUTPUT)
    overrides = load_path(OVERRIDES)
    if len(names) != 35 or len(classes) != 22 or language_files:
        errors.append("Mouse Tweaks JAR 엔트리·클래스·언어 파일 수 불일치")
    if data_files or guide_files:
        errors.append("Mouse Tweaks 예상 밖의 데이터·발전 과제·가이드 자산")
    if len(sources) != 18 or set(working) != set(sources) or working != output:
        errors.append("Mouse Tweaks 표시 원문·작업본·산출물 키 집합 불일치")
    if (
        overrides
        or sha256(SOURCES) != EXPECTED_SOURCE_SHA256
        or sha256(OVERRIDES) != EXPECTED_OVERRIDE_SHA256
        or sha256(OUTPUT) != EXPECTED_OUTPUT_SHA256
    ):
        errors.append("Mouse Tweaks 원문표·교정표·산출물 해시 불일치")

    description_key = "fml.menu.mods.info.description.mousetweaks"
    screen_sources = {
        key: value for key, value in sources.items() if key != description_key
    }
    if not all(
        value.encode("utf-8") in config_screen for value in screen_sources.values()
    ):
        errors.append("Mouse Tweaks 설정 화면 하드코딩 원문 경로 누락")
    if (
        'displayName="Mouse Tweaks"' not in metadata
        or f'description="{sources[description_key]}"' not in metadata
    ):
        errors.append("Mouse Tweaks 모드 메타데이터 원문 경로 불일치")
    if load_config(config) != EXPECTED_CONFIG:
        errors.append("Mouse Tweaks 설정 옵션·값 불일치")
    if not all(key.encode("utf-8") in config_class for key in EXPECTED_CONFIG):
        errors.append("Mouse Tweaks 설정 클래스 옵션 경로 누락")

    if NATIVE_PRIORITY_SIGNATURE not in native_wrapper:
        errors.append("KubeJS NativeEvents 우선순위 등록 경로가 변경되었습니다")
    if (
        WORKING_SCRIPT.read_bytes() != OUTPUT_SCRIPT.read_bytes()
        or sha256(OUTPUT_SCRIPT) != EXPECTED_SCRIPT_SHA256
    ):
        errors.append("Mouse Tweaks 설정 화면 덮어쓰기 산출물 불일치")
    script = OUTPUT_SCRIPT.read_text(encoding="utf-8")
    required_script_tokens = (
        'Platform.isLoaded("mousetweaks")',
        "Platform.isClientEnvironment()",
        "ScreenEvent$Init$Post",
        "ScreenEvent$Render$Pre",
        "$EventPriority.LOWEST",
        "String(screen.getClass().getName()) !== SCREEN_CLASS",
        '$I18n.exists("mousetweaks.configuration.title")',
        "widget instanceof $AbstractWidget",
        "widget.setMessage($Component.literal(translated))",
    )
    if not all(token in script for token in required_script_tokens):
        errors.append("Mouse Tweaks 설정 화면 덮어쓰기 안전 조건 누락")
    if not all(value in script for value in screen_sources.values()):
        errors.append("Mouse Tweaks 하드코딩 원문 매핑 누락")
    if not all(key in script for key in screen_sources):
        errors.append("Mouse Tweaks 한국어 키 매핑 누락")

    for key in sources:
        if PLACEHOLDER.findall(sources[key]) != PLACEHOLDER.findall(output[key]):
            errors.append(f"자리표시자 불일치: {key}")
        if NUMBER.findall(sources[key]) != NUMBER.findall(output[key]):
            errors.append(f"숫자 불일치: {key}")
        if sources[key].count("\n") != output[key].count("\n"):
            errors.append(f"줄바꿈 불일치: {key}")
        if Counter(FORMAT_CODE.findall(sources[key])) != Counter(
            FORMAT_CODE.findall(output[key])
        ):
            errors.append(f"서식 코드 불일치: {key}")
    forbidden = FORBIDDEN_TRANSLATIONS.findall("\n".join(output.values()))
    if forbidden:
        errors.append(f"Mouse Tweaks 금지 번역 잔존: {sorted(set(forbidden))}")
    if output.get("mousetweaks.configuration.title") != "Mouse Tweaks 설정":
        errors.append("Mouse Tweaks 공식 모드명 표기 불일치")
    if output.get("mousetweaks.configuration.value.always_one") != (
        "항상 아이템 하나만 이동(macOS 호환)"
    ):
        errors.append("Mouse Tweaks 수량·macOS 호환 의미 불일치")

    quest_files = find_related_files(instance / "config/ftbquests/quests")
    quest_refs = direct_references(instance, quest_files)
    kube_files = find_related_files(instance / "kubejs")
    kube_refs = direct_references(instance, kube_files)
    applied_script = "kubejs/startup_scripts/mousetweaks_config_labels.js"
    expected_kube_count = 893 if pre_apply else 894
    expected_kube_refs = set() if pre_apply else {applied_script}
    if len(quest_files) != 142 or quest_refs:
        errors.append(f"Mouse Tweaks FTB Quests 직접 참조 불일치: {quest_refs}")
    if len(kube_files) != expected_kube_count or kube_refs != expected_kube_refs:
        errors.append(f"Mouse Tweaks KubeJS 직접 참조 불일치: {kube_refs}")

    jar_count, english_count, owner_overlaps = verify_language_owners(instance, sources)
    project_languages = list(
        (PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets").glob(
            "*/lang/ko_kr.json"
        )
    )
    if jar_count != 480 or english_count != 388 or len(project_languages) != 286:
        errors.append(
            "설치·프로젝트 언어 집계 변경: "
            f"jars={jar_count}, english={english_count}, project={len(project_languages)}"
        )
    if GLOSSARY_ROW not in GLOSSARY.read_text(encoding="utf-8"):
        errors.append("Mouse Tweaks 용어집 행 누락")

    if not pre_apply:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        if not isinstance(report, dict) or report.get("validation") != "passed":
            errors.append("Mouse Tweaks 재검수 보고서 상태 불일치")
        application = report.get("application") if isinstance(report, dict) else None
        if (
            not isinstance(application, dict)
            or application.get("status") != "applied_and_verified"
            or application.get("mousetweaks_sha256") != EXPECTED_OUTPUT_SHA256
            or application.get("config_script_sha256") != EXPECTED_SCRIPT_SHA256
            or application.get("unexpected_changes") != 0
        ):
            errors.append("Mouse Tweaks 재검수 보고서 적용 집계 불일치")
        language_target = (
            instance / "resourcepacks/ATM10_Korean/assets/mousetweaks/lang/ko_kr.json"
        )
        script_target = instance / applied_script
        if (
            not language_target.exists()
            or language_target.read_bytes() != OUTPUT.read_bytes()
            or not script_target.exists()
            or script_target.read_bytes() != OUTPUT_SCRIPT.read_bytes()
        ):
            errors.append("실제 source_root의 Mouse Tweaks 산출물이 다릅니다")

    if errors:
        raise RuntimeError("Mouse Tweaks 재검수 검증 실패:\n" + "\n".join(errors[:80]))
    return {
        "scope": "Mouse Tweaks 전체 표시 문구 재검수",
        "source_jar": source_jar.name,
        "source_jar_sha256": sha256(source_jar),
        "source_jar_bytes": source_jar.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(classes),
        "bundled_language_files": len(language_files),
        "metadata_display_strings_reviewed": 1,
        "hardcoded_config_display_strings_reviewed": len(screen_sources),
        "existing_korean_candidates_reviewed": 0,
        "existing_korean_candidates_reused": 0,
        "existing_korean_candidates_corrected": 0,
        "newly_translated": len(output),
        "effective_output_keys": len(output),
        "configuration_options_reviewed": len(EXPECTED_CONFIG),
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_reference_files": len(quest_refs),
        "original_kubejs_files_reviewed": 893,
        "kubejs_display_overrides_added": 1,
        "installed_mod_jars_reviewed": jar_count,
        "installed_english_language_files_reviewed": english_count,
        "other_language_owner_overlaps": owner_overlaps,
        "project_language_files_reviewed": len(project_languages),
        "glossary_terms_added": 1,
        "output_sha256": sha256(OUTPUT),
        "config_script_sha256": sha256(OUTPUT_SCRIPT),
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
