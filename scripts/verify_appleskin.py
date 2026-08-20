#!/usr/bin/env python3
"""AppleSkin 번역과 설정·HUD·F3 표시 경로를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root

WORK_ROOT = PROJECT_ROOT / "working/common_ui/inventory_controls/appleskin"
WORKING = WORK_ROOT / "ko_kr.json"
OVERRIDES = WORK_ROOT / "recheck_overrides.json"
WORKING_DEBUG_SCRIPT = WORK_ROOT / "kubejs/startup_scripts/appleskin_debug_labels.js"
REPORT = WORK_ROOT / "recheck_20260820.json"
OUTPUT = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/appleskin/lang/ko_kr.json"
)
OUTPUT_DEBUG_SCRIPT = (
    PROJECT_ROOT / "output/overrides/kubejs/startup_scripts/appleskin_debug_labels.js"
)
GLOSSARY = PROJECT_ROOT / "glossary/README.md"

EXPECTED_JAR = "appleskin-neoforge-mc1.21-3.0.9.jar"
EXPECTED_JAR_SHA256 = "38b48dd6231341c9f964ce6e42c57ec866c6cc8f72bec938390a59bafb3922df"
EXPECTED_CONFIG_SHA256 = (
    "7127a276c7305371397053cd8d0833e6825c828850626e4067b9fed1430ed217"
)
EXPECTED_BUNDLED_KO_SHA256 = (
    "79ff08357d72b07b17c0e6c51d24b8cc6e0102d444a555fa05214c5a9a2926b4"
)
EXPECTED_OVERRIDE_SHA256 = (
    "2a53748d0156ef416d3940c2591ffd8af18e0de6bd41d810edf9d8371e7e3605"
)
EXPECTED_OUTPUT_SHA256 = (
    "82a521ed0f3f235227e0b256c73f69fa193aa97d3ae78654eae2a64708520a76"
)
EXPECTED_DEBUG_SCRIPT_SHA256 = (
    "19e1faf838c5bbf60d947cde6cbbab50847b4da627f614dc49afabf3a93361a1"
)
EXPECTED_KUBEJS_JAR = "kubejs-neoforge-2101.7.2-build.368.jar"
EXPECTED_KUBEJS_SHA256 = (
    "28867299e7a9f02cfd74e34745fdbbb073fe4887fddbc98fd6c1ed2e87b01482"
)
GLOSSARY_ROWS = (
    "| AppleSkin | AppleSkin | 공식 모드명 |",
    "| Saturation (food) | 포만도 | 음식 시스템 수치 |",
    "| Food Exhaustion | 허기 소모도 | 음식 시스템 수치 |",
)
EXPECTED_CONFIG_OPTIONS = {
    "maxHudOverlayFlashAlpha",
    "showFoodExhaustionHudUnderlay",
    "showFoodHealthHudOverlay",
    "showFoodStatsInDebugOverlay",
    "showFoodValuesHudOverlay",
    "showFoodValuesHudOverlayWhenOffhand",
    "showFoodValuesInTooltip",
    "showFoodValuesInTooltipAlways",
    "showSaturationHudOverlay",
    "showVanillaAnimationsOverlay",
}
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
NUMBER = re.compile(r"(?<![A-Za-z0-9_])\d+(?:\.\d+)?")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
ENGLISH_LANGUAGE = re.compile(r"assets/[^/]+/lang/en_us\.json")
DIRECT_REFERENCE = re.compile(r"(?i)appleskin(?:[.:/\\]|\b)|apple skin")
RELATED_EXTENSIONS = {".js", ".json", ".snbt", ".toml", ".txt"}
FORBIDDEN_TRANSLATIONS = re.compile(
    r"포화도|참이면|진행 바로|음식이 회복할 허기|아이템 설명에 회복량|"
    r"다른 손에 든 아이템|발광 HUD"
)
DEBUG_LITERAL = b"hunger: \x01, sat: \x01, exh: \x01/\x01"
NATIVE_PRIORITY_SIGNATURE = (
    b"(Ldev/latvian/mods/rhino/Context;Lnet/neoforged/bus/api/EventPriority;"
    b"Ljava/lang/Class;Ljava/util/function/Consumer;)V"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_language(data: bytes, label: str) -> dict[str, str]:
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
        raise TypeError(f"문자열 언어 객체가 아닙니다: {label}")
    return value


def load_path(path: Path) -> dict[str, str]:
    return load_language(path.read_bytes(), str(path))


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


def config_options(path: Path) -> set[str]:
    options: set[str] = set()
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("#", "[")) and "=" in stripped:
            options.add(stripped.split("=", 1)[0].strip())
    return options


def verify_language_owners(
    instance: Path, english: dict[str, str]
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
                    if name == "assets/appleskin/lang/en_us.json":
                        continue
                    value = json.loads(archive.read(name).decode("utf-8-sig"))
                    if isinstance(value, dict):
                        for key in set(english) & set(value):
                            overlaps.append(f"{jar_path.name}:{name}:{key}")
        except BadZipFile as error:
            raise RuntimeError(f"손상된 모드 JAR: {jar_path}") from error
    if overlaps:
        raise RuntimeError(f"AppleSkin 언어 키 소유자 중복: {overlaps[:20]}")
    return jar_count, language_count, len(overlaps)


def verify_related_terms(errors: list[str]) -> None:
    sushi = load_path(
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/sushigocrafting/lang/ko_kr.json"
    )
    fancy = load_path(
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/fancymenu/lang/ko_kr.json"
    )
    ultimine = load_path(
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/ftbultimine/lang/ko_kr.json"
    )
    if sushi.get("text.sushigocrafting.saturation") != "포만도":
        errors.append("Sushi Go Crafting 음식 포만도 용어 불일치")
    if fancy.get("fancymenu.placeholders.world.current_player_hunger_saturation") != (
        "현재 플레이어 포만도"
    ):
        errors.append("FancyMenu 플레이어 포만도 용어 불일치")
    if ultimine.get("ftbultimine.modifier.exhaustion") != "FTB Ultimine 허기 소모량":
        errors.append("FTB Ultimine 허기 소모량 문맥 예외 불일치")


def verify(pre_apply: bool) -> dict[str, object]:
    instance = resolve_source_root(None)
    errors: list[str] = []
    source_jar = instance / "mods" / EXPECTED_JAR
    config = instance / "config/appleskin-client.toml"
    kubejs_jar = instance / "mods" / EXPECTED_KUBEJS_JAR
    if sha256(source_jar) != EXPECTED_JAR_SHA256:
        errors.append("AppleSkin 원본 JAR 해시가 변경되었습니다")
    if sha256(config) != EXPECTED_CONFIG_SHA256:
        errors.append("AppleSkin 클라이언트 설정 해시가 변경되었습니다")
    if sha256(kubejs_jar) != EXPECTED_KUBEJS_SHA256:
        errors.append("KubeJS 원본 JAR 해시가 변경되었습니다")

    with ZipFile(source_jar) as archive:
        names = archive.namelist()
        english = load_language(
            archive.read("assets/appleskin/lang/en_us.json"), "AppleSkin en_us"
        )
        bundled_bytes = archive.read("assets/appleskin/lang/ko_kr.json")
        bundled = load_language(bundled_bytes, "AppleSkin ko_kr")
        classes = [name for name in names if name.endswith(".class")]
        language_files = [
            name
            for name in names
            if name.startswith("assets/appleskin/lang/") and name.endswith(".json")
        ]
        data_files = [
            name
            for name in names
            if name.startswith("data/appleskin/") and name.endswith(".json")
        ]
        guide_files = [
            name
            for name in names
            if any(
                token in name.lower()
                for token in ("patchouli", "guideme", "modonomicon")
            )
        ]
        mod_config = archive.read("squeek/appleskin/ModConfig.class")
        debug_info = archive.read("squeek/appleskin/client/DebugInfoHandler.class")
        metadata = archive.read("META-INF/neoforge.mods.toml").decode("utf-8")

    with ZipFile(kubejs_jar) as archive:
        native_wrapper = archive.read(
            "dev/latvian/mods/kubejs/plugin/builtin/wrapper/NativeEventWrapper.class"
        )

    working = load_path(WORKING)
    output = load_path(OUTPUT)
    overrides = load_path(OVERRIDES)
    if len(names) != 78 or len(classes) != 36 or len(language_files) != 21:
        errors.append("AppleSkin JAR 엔트리·클래스·언어 파일 수 불일치")
    if len(english) != 22 or len(bundled) != 12:
        errors.append("AppleSkin 영어 또는 내장 한국어 키 수 불일치")
    if hashlib.sha256(bundled_bytes).hexdigest() != EXPECTED_BUNDLED_KO_SHA256:
        errors.append("AppleSkin 내장 한국어 후보 해시 불일치")
    if working != output or set(output) != set(english):
        errors.append("AppleSkin 작업본·산출물·영어 키 집합 불일치")
    if (
        len(overrides) != 16
        or any(output.get(key) != value for key, value in overrides.items())
        or sha256(OVERRIDES) != EXPECTED_OVERRIDE_SHA256
        or sha256(OUTPUT) != EXPECTED_OUTPUT_SHA256
    ):
        errors.append("AppleSkin 교정표 또는 산출물 수·값·해시 불일치")
    if bundled.get("appleskin.configuration.client") != output.get(
        "appleskin.configuration.client"
    ) or bundled.get("fml.menu.mods.info.description.appleskin") != output.get(
        "fml.menu.mods.info.description.appleskin"
    ):
        errors.append("AppleSkin 내장 한국어 재사용 항목 불일치")
    if sum(output.get(key) == value for key, value in bundled.items()) != 2:
        errors.append("AppleSkin 내장 한국어 재사용 수 불일치")

    option_keys = {
        key.removeprefix("appleskin.configuration.")
        for key in english
        if key.startswith("appleskin.configuration.")
        and key != "appleskin.configuration.client"
        and not key.endswith(".tooltip")
    }
    if option_keys != EXPECTED_CONFIG_OPTIONS or config_options(config) != option_keys:
        errors.append("AppleSkin 언어·설정 옵션 대응 불일치")
    if not all(option.encode("utf-8") in mod_config for option in option_keys):
        errors.append("AppleSkin ModConfig 옵션 표시 경로 누락")
    if data_files or guide_files:
        errors.append("AppleSkin 예상 밖의 데이터·발전 과제·가이드 자산")
    if (
        'displayName="AppleSkin"' not in metadata
        or 'description="Adds various food-related HUD improvements"' not in metadata
    ):
        errors.append("AppleSkin 모드 메타데이터 표시 경로 불일치")

    if DEBUG_LITERAL not in debug_info:
        errors.append("AppleSkin F3 하드코딩 원문 경로가 변경되었습니다")
    if NATIVE_PRIORITY_SIGNATURE not in native_wrapper:
        errors.append("KubeJS NativeEvents 우선순위 등록 경로가 변경되었습니다")
    if (
        WORKING_DEBUG_SCRIPT.read_bytes() != OUTPUT_DEBUG_SCRIPT.read_bytes()
        or sha256(OUTPUT_DEBUG_SCRIPT) != EXPECTED_DEBUG_SCRIPT_SHA256
    ):
        errors.append("AppleSkin F3 한국어 덮어쓰기 산출물 불일치")
    debug_script = OUTPUT_DEBUG_SCRIPT.read_text(encoding="utf-8")
    required_script_tokens = (
        'Platform.isLoaded("appleskin")',
        "Platform.isClientEnvironment()",
        "CustomizeGuiOverlayEvent$DebugText",
        "$EventPriority.LOWEST",
        "^hunger: ([^,]+), sat: ([^,]+), exh: (.+)$",
        "허기: ${match[1]}, 포만도: ${match[2]}, 허기 소모도: ${match[3]}",
    )
    if not all(token in debug_script for token in required_script_tokens):
        errors.append("AppleSkin F3 한국어 덮어쓰기 안전 조건 누락")

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
        errors.append(f"AppleSkin 금지 번역 잔존: {sorted(set(forbidden))}")
    boolean_tooltips = {
        key: value
        for key, value in output.items()
        if key.endswith(".tooltip") and "maxHudOverlayFlashAlpha" not in key
    }
    if len(boolean_tooltips) != 9 or not all(
        value.startswith("활성화하면 ") for value in boolean_tooltips.values()
    ):
        errors.append("AppleSkin 불리언 설정 툴팁 문체 불일치")
    if output.get("appleskin.configuration.showSaturationHudOverlay") != (
        "포만도 오버레이 표시"
    ):
        errors.append("AppleSkin 음식 포만도 용어 불일치")

    verify_related_terms(errors)
    quest_files = find_related_files(instance / "config/ftbquests/quests")
    quest_refs = direct_references(instance, quest_files)
    kube_files = find_related_files(instance / "kubejs")
    kube_refs = direct_references(instance, kube_files)
    applied_script = "kubejs/startup_scripts/appleskin_debug_labels.js"
    expected_kube_count = 892 if pre_apply else 893
    expected_kube_refs = set() if pre_apply else {applied_script}
    if len(quest_files) != 142 or quest_refs:
        errors.append(f"AppleSkin FTB Quests 직접 참조 불일치: {quest_refs}")
    if len(kube_files) != expected_kube_count or kube_refs != expected_kube_refs:
        errors.append(f"AppleSkin KubeJS 직접 참조 불일치: {kube_refs}")

    jar_count, english_count, owner_overlaps = verify_language_owners(instance, english)
    project_languages = list(
        (PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets").glob(
            "*/lang/ko_kr.json"
        )
    )
    if jar_count != 480 or english_count != 388 or len(project_languages) != 285:
        errors.append(
            "설치·프로젝트 언어 집계 변경: "
            f"jars={jar_count}, english={english_count}, project={len(project_languages)}"
        )
    glossary = GLOSSARY.read_text(encoding="utf-8")
    for row in GLOSSARY_ROWS:
        if row not in glossary:
            errors.append(f"AppleSkin 용어집 행 누락: {row}")

    if not pre_apply:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        if not isinstance(report, dict) or report.get("validation") != "passed":
            errors.append("AppleSkin 재검수 보고서 상태 불일치")
        application = report.get("application") if isinstance(report, dict) else None
        if (
            not isinstance(application, dict)
            or application.get("status") != "applied_and_verified"
            or application.get("appleskin_sha256") != EXPECTED_OUTPUT_SHA256
            or application.get("debug_script_sha256") != EXPECTED_DEBUG_SCRIPT_SHA256
            or application.get("unexpected_changes") != 0
        ):
            errors.append("AppleSkin 재검수 보고서 적용 집계 불일치")
        language_target = (
            instance / "resourcepacks/ATM10_Korean/assets/appleskin/lang/ko_kr.json"
        )
        script_target = instance / applied_script
        if (
            not language_target.exists()
            or language_target.read_bytes() != OUTPUT.read_bytes()
            or not script_target.exists()
            or script_target.read_bytes() != OUTPUT_DEBUG_SCRIPT.read_bytes()
        ):
            errors.append("실제 source_root의 AppleSkin 산출물이 다릅니다")

    if errors:
        raise RuntimeError("AppleSkin 재검수 검증 실패:\n" + "\n".join(errors[:80]))
    return {
        "scope": "AppleSkin 전체 번역 재검수",
        "source_jar": source_jar.name,
        "source_jar_sha256": sha256(source_jar),
        "source_jar_bytes": source_jar.stat().st_size,
        "jar_entries": len(names),
        "class_files_reviewed": len(classes),
        "language_files_reviewed": len(language_files),
        "source_keys_reviewed": len(english),
        "bundled_korean_candidates_reviewed": len(bundled),
        "bundled_korean_candidates_reused": sum(
            output.get(key) == value for key, value in bundled.items()
        ),
        "bundled_korean_candidates_rejected": sum(
            output.get(key) != value for key, value in bundled.items()
        ),
        "project_candidates_retained": 6,
        "project_candidates_corrected": len(overrides),
        "newly_translated": 0,
        "effective_output_keys": len(output),
        "configuration_options_reviewed": len(option_keys),
        "hardcoded_f3_display_paths_corrected": 1,
        "ftbquests_files_reviewed": len(quest_files),
        "ftbquests_reference_files": len(quest_refs),
        "original_kubejs_files_reviewed": 892,
        "kubejs_display_overrides_added": 1,
        "installed_mod_jars_reviewed": jar_count,
        "installed_english_language_files_reviewed": english_count,
        "other_language_owner_overlaps": owner_overlaps,
        "project_language_files_reviewed": len(project_languages),
        "related_mod_term_paths_reviewed": 3,
        "glossary_terms_added": len(GLOSSARY_ROWS),
        "output_sha256": sha256(OUTPUT),
        "debug_script_sha256": sha256(OUTPUT_DEBUG_SCRIPT),
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
