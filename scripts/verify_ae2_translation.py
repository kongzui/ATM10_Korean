#!/usr/bin/env python3
"""AE2 리소스팩, FTB Quests와 KubeJS 번역 산출물을 읽기 전용으로 검증한다."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

import build_ae2_quests as quests
import build_ftbquests_titles as titles
from local_paths import resolve_source_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCEPACK_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean"
OUTPUT_LANG = RESOURCEPACK_ROOT / "assets/ae2/lang/ko_kr.json"
PROGRESS_FILE = PROJECT_ROOT / "working/ae2/progress.json"
PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{\d+\}")
ALLOWED_IDENTICAL_TRANSLATIONS = {
    "block.ae2.debug_cube_gen",
    "block.ae2.debug_energy_gen",
    "block.ae2.debug_item_gen",
    "block.ae2.debug_phantom_node",
    "gui.ae2.CPUs",
    "gui.ae2.CompatibleUpgrade",
    "gui.ae2.CreativeTab",
    "gui.ae2.ETAFormat",
    "gui.ae2.ToastCraftingJobFinishedText",
    "gui.ae2.units.appliedenergistics",
    "gui.ae2.units.fe",
    "key.ae2.category",
    "theoneprobe.ae2.stored_energy",
}
CORE_TERM_TRANSLATIONS = {
    "ae2.emi_integration.category_inscriber": "각인기",
    "block.ae2.inscriber": "각인기",
    "gui.ae2.Inscriber": "각인기",
    "item.ae2.calculation_processor_press": "계산 회로 프레스",
    "item.ae2.engineering_processor_press": "공학 회로 프레스",
    "item.ae2.logic_processor_press": "논리 회로 프레스",
}
ALLTHECOMPRESSED_TRANSLATIONS = {
    **{
        f"block.allthecompressed.certus_quartz_block_{level}x": f"서투스 석영 블록 {level}x"
        for level in range(1, 10)
    },
    **{
        f"block.allthecompressed.fluix_block_{level}x": f"플루익스 블록 {level}x"
        for level in range(1, 10)
    },
    **{
        f"block.allthecompressed.sky_stone_block_{level}x": f"천령석 {level}x"
        for level in range(1, 10)
    },
}
COMPAT_TRANSLATIONS = (
    (
        "allthecompressed-*.jar",
        "assets/allthecompressed/lang/en_us.json",
        PROJECT_ROOT / "working/ae2/compat/allthecompressed/ko_kr.json",
        RESOURCEPACK_ROOT / "assets/allthecompressed/lang/ko_kr.json",
        ALLTHECOMPRESSED_TRANSLATIONS,
    ),
    (
        "create-1.21.1-*.jar",
        "assets/create/lang/en_us.json",
        PROJECT_ROOT / "working/ae2/compat/create/ko_kr.json",
        RESOURCEPACK_ROOT / "assets/create/lang/ko_kr.json",
        {"tag.item.c.gems.certus_quartz": "서투스 석영"},
    ),
    (
        "theurgy-*.jar",
        "assets/theurgy/lang/en_us.json",
        PROJECT_ROOT / "working/ae2/compat/theurgy/ko_kr.json",
        RESOURCEPACK_ROOT / "assets/theurgy/lang/ko_kr.json",
        {
            "item.theurgy.alchemical_sulfur_certus_quartz.source": "서투스 석영",
            "item.theurgy.alchemical_sulfur_fluix.source": "플루익스",
        },
    ),
)
COMMON_QUEST_OVERRIDES = (
    PROJECT_ROOT / "working/ftbquests/common_chapter_overrides.json"
)
ADDON_QUEST_OVERRIDE_FILES = (
    PROJECT_ROOT / "working/ae2_addons/extendedae/quest_overrides.json",
    PROJECT_ROOT / "working/ae2_addons/advanced_ae/quest_overrides.json",
    PROJECT_ROOT / "working/ae2_addons/megacells/quest_overrides.json",
    PROJECT_ROOT / "working/ae2_addons/appflux/quest_overrides.json",
    PROJECT_ROOT / "working/ae2_addons/expandedae/quest_overrides.json",
    PROJECT_ROOT / "working/ae2_addons/ae2importexportcard/quest_overrides.json",
    PROJECT_ROOT / "working/ae2_addons/ae2netanalyser/quest_overrides.json",
    PROJECT_ROOT / "working/ae2_addons/merequester/quest_overrides.json",
    PROJECT_ROOT / "working/ae2_addons/arseng/quest_overrides.json",
)
LATER_REVIEWED_QUEST_FILES = (
    PROJECT_ROOT / "working/atmgear/quest_overrides.json",
    PROJECT_ROOT / "working/mekanism/quests/related/ko_kr.json",
    PROJECT_ROOT / "working/mekanism/quests/mekanism_reactors/ko_kr.json",
    PROJECT_ROOT / "working/productivebees/quest_overrides.json",
    PROJECT_ROOT / "working/integrated_dynamics/quest_overrides.json",
    PROJECT_ROOT / "working/ars_nouveau/quests/related/ko_kr.json",
    PROJECT_ROOT / "working/powah_flux/quests/related/ko_kr.json",
)


def load_zip_json(path: Path, entry: str) -> dict[str, str]:
    """현재 설치 JAR의 문자열 언어 JSON을 읽는다."""
    with zipfile.ZipFile(path) as archive:
        value = json.loads(archive.read(entry).decode("utf-8-sig"))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise ValueError(f"문자열 JSON 객체가 아닙니다: {path}!{entry}")
    return value


def load_json_unique(path: Path) -> dict[str, str]:
    """중복 키를 거부하며 문자열 언어 JSON을 읽는다."""
    duplicates: list[str] = []

    def pairs_hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs_hook)
    if duplicates:
        raise ValueError(f"중복 JSON 키가 있습니다: {path}: {sorted(set(duplicates))}")
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise ValueError(f"문자열 JSON 객체가 아닙니다: {path}")
    return value


def find_single_jar(instance: Path, pattern: str) -> Path:
    """현재 설치 인스턴스에서 패턴과 일치하는 JAR 하나를 찾는다."""
    jars = sorted((instance / "mods").glob(pattern))
    if len(jars) != 1:
        raise ValueError(f"JAR을 하나로 확정할 수 없습니다: {pattern}: {jars}")
    return jars[0]


def validate_compat_translations(instance: Path) -> tuple[int, list[Path]]:
    """AE2 재료를 직접 표시하는 연동 모드의 부분 언어 파일을 검증한다."""
    checked_paths: list[Path] = []
    translated_keys = 0
    for pattern, entry, working_path, output_path, expected in COMPAT_TRANSLATIONS:
        jar = find_single_jar(instance, pattern)
        english = load_zip_json(jar, entry)
        if pattern.startswith("allthecompressed"):
            source_keys = {
                key
                for key in english
                if re.fullmatch(
                    r"block\.allthecompressed\."
                    r"(?:certus_quartz_block|fluix_block|sky_stone_block)_[1-9]x",
                    key,
                )
            }
            if source_keys != set(expected):
                raise ValueError("AllTheCompressed의 AE2 재료 키 집합이 바뀌었습니다.")
        elif not set(expected) <= set(english):
            raise ValueError(f"현재 JAR에 AE2 연동 키가 없습니다: {pattern}")

        working = load_json_unique(working_path)
        output = load_json_unique(output_path)
        if list(working) != list(expected) or working != expected:
            raise ValueError(f"AE2 연동 작업본이 확정 번역과 다릅니다: {working_path}")
        if output != working:
            raise ValueError(f"AE2 연동 출력이 작업본과 다릅니다: {output_path}")
        for key, translated in working.items():
            errors = validate_pair(key, english[key], translated)
            if errors:
                raise ValueError("\n".join(errors))
        checked_paths.extend((working_path, output_path))
        translated_keys += len(working)
    return translated_keys, checked_paths


def validate_pair(key: str, source: str, translated: str) -> list[str]:
    """현재 영어 원문과 프로젝트 번역의 구조 보존 여부를 검사한다."""
    errors = []
    if Counter(PLACEHOLDER_RE.findall(source)) != Counter(
        PLACEHOLDER_RE.findall(translated)
    ):
        errors.append(f"{key}: 자리표시자 불일치")
    if source.count("\n") != translated.count("\n"):
        errors.append(f"{key}: 줄바꿈 개수 불일치")
    return errors


def ensure_no_bom(path: Path) -> None:
    if path.read_bytes().startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"UTF-8 BOM이 있습니다: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)

    jar = instance / "mods/appliedenergistics2-19.2.17.jar"
    english = load_zip_json(jar, "assets/ae2/lang/en_us.json")
    output_lang = OUTPUT_LANG
    translated = load_json_unique(output_lang)
    if list(translated) != list(english):
        raise ValueError("AE2 리소스팩 키 또는 키 순서가 영어 원문과 다릅니다.")
    resource_errors = []
    for key in english:
        resource_errors.extend(validate_pair(key, english[key], translated[key]))
    if resource_errors:
        raise ValueError("\n".join(resource_errors))
    unexpected_identical = sorted(
        key
        for key in english
        if translated[key] == english[key] and key not in ALLOWED_IDENTICAL_TRANSLATIONS
    )
    if unexpected_identical:
        raise ValueError(f"AE2 영어 원문이 남았습니다: {unexpected_identical}")
    for key, expected_value in CORE_TERM_TRANSLATIONS.items():
        if translated.get(key) != expected_value:
            raise ValueError(f"AE2 핵심 용어가 일치하지 않습니다: {key}")

    compat_keys, compat_paths = validate_compat_translations(instance)

    lang_root = instance / "config/ftbquests/quests/lang"
    quest_english = quests.parse_language_snbt(
        lang_root / "en_us/chapters/applied_energistics_2.snbt_merged"
    )
    quest_current = quests.parse_language_snbt(
        lang_root / "ko_kr/chapters/applied_energistics_2.snbt_merged"
    )
    full_current = quests.parse_language_snbt(lang_root / "ko_kr.snbt")
    full_output = quests.parse_language_snbt(quests.OUTPUT_FILE)
    overrides = json.loads(quests.OVERRIDES_FILE.read_text(encoding="utf-8"))
    common_overrides = json.loads(COMMON_QUEST_OVERRIDES.read_text(encoding="utf-8"))
    addon_overrides = {}
    for path in ADDON_QUEST_OVERRIDE_FILES:
        addon_overrides |= json.loads(path.read_text(encoding="utf-8"))
    later_reviewed_overrides = {}
    for path in LATER_REVIEWED_QUEST_FILES:
        later_reviewed_overrides |= json.loads(path.read_text(encoding="utf-8"))
    additional_overrides = common_overrides | addon_overrides | later_reviewed_overrides
    expected = {
        key: quests.normalize(overrides[key])
        if key in overrides
        else quests.normalize(quest_current[key])
        for key in quest_english
    }
    for key, value in expected.items():
        if full_output.get(key) != value and not titles.TITLE_KEY_RE.fullmatch(key):
            raise ValueError(f"FTB Quests 출력이 작업본과 다릅니다: {key}")
        errors = quests.validate_value(key, quest_english[key], value)
        if errors:
            raise ValueError("\n".join(errors))
    for key, value in full_current.items():
        if (
            key not in expected
            and full_output.get(key) != value
            and not titles.TITLE_KEY_RE.fullmatch(key)
            and key not in additional_overrides
        ):
            raise ValueError(f"AE2 범위 밖의 FTB Quests 키가 변경됐습니다: {key}")
    mismatched_additional = sorted(
        key
        for key, value in additional_overrides.items()
        if full_output.get(key) != value
    )
    if mismatched_additional:
        raise ValueError(
            f"추가 FTB Quests 작업본과 출력이 다릅니다: {mismatched_additional}"
        )
    current_title_keys = {
        key for key in full_current if titles.TITLE_KEY_RE.fullmatch(key)
    }
    output_title_keys = {
        key for key in full_output if titles.TITLE_KEY_RE.fullmatch(key)
    }
    expected_full_keys = (
        (set(full_current) - current_title_keys)
        | (set(quest_english) - set(quest_current))
        | set(additional_overrides)
        | output_title_keys
    )
    if set(full_output) != expected_full_keys:
        raise ValueError("FTB Quests 전체 키 집합이 예상과 다릅니다.")

    quest_text = json.dumps(full_output, ensure_ascii=False)
    forbidden_quest_terms = (
        "회로 인쇄기",
        "세르투스 석영",
        "세투스 석영",
        "하늘 돌",
        "하늘석",
        "스카이 스톤",
        "플럭스 벌",
        "Fluix 연구원",
    )
    remaining_quest_terms = [
        term for term in forbidden_quest_terms if term in quest_text
    ]
    if remaining_quest_terms:
        raise ValueError(
            f"FTB Quests에 AE2 비표준 용어가 남았습니다: {remaining_quest_terms}"
        )
    expected_quest_terms = {
        "quest.26B3AE1E77A84BCB.quest_desc": ("충전된 서투스 석영", "천령석"),
        "quest.33422FBDAE11AE82.quest_subtitle": ("공간 벌", "플루익스 진주"),
        "quest.33422FBDAE11AE82.title": ("플루익스 벌",),
        "quest.6E17595887A051C2.quest_desc": ("플루익스 연구원",),
    }
    for key, terms in expected_quest_terms.items():
        value_text = json.dumps(full_output.get(key), ensure_ascii=False)
        if not all(term in value_text for term in terms):
            raise ValueError(f"FTB Quests의 AE2 확정 용어가 누락됐습니다: {key}")

    kube_path = (
        PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/kubejs/lang/ko_kr.json"
    )
    kube = load_json_unique(kube_path)
    if kube.get("item.kubejs.universal_press") != "각인기 범용 프레스":
        raise ValueError("KubeJS 범용 프레스 번역이 없습니다.")
    if kube.get("item.kubejs.sky_stone_cell") != "ME 무한 천령석 셀":
        raise ValueError("KubeJS 천령석 무한 셀 번역이 일치하지 않습니다.")
    infinity_script = instance / "kubejs/startup_scripts/ExtendedAE/InfinityCells.js"
    infinity_ids = set(
        re.findall(
            r"allthemods\.create\('([^']+)',\s*'custom_infinity_cell'\)",
            infinity_script.read_text(encoding="utf-8-sig"),
        )
    )
    infinity_keys = {f"item.kubejs.{item_id}" for item_id in infinity_ids}
    missing_infinity_keys = sorted(infinity_keys - set(kube))
    unexpected_kube_keys = sorted(
        set(kube) - infinity_keys - {"item.kubejs.universal_press"}
    )
    if missing_infinity_keys or unexpected_kube_keys:
        raise ValueError(
            "ExtendedAE 무한 셀 KubeJS 키 검증 실패: "
            f"누락={missing_infinity_keys}, 범위 밖={unexpected_kube_keys}"
        )

    related_lang_terms = (
        (
            PROJECT_ROOT / "working/mystical/mysticalagriculture/ko_kr.json",
            RESOURCEPACK_ROOT / "assets/mysticalagriculture/lang/ko_kr.json",
            {
                "crop.mysticalagriculture.sky_stone": "천령석",
                "crop.mysticalagriculture.certus_quartz": "서투스 석영",
                "crop.mysticalagriculture.fluix": "플루익스",
            },
        ),
        (
            PROJECT_ROOT / "working/productivebees/productivebees/ko_kr.json",
            RESOURCEPACK_ROOT / "assets/productivebees/lang/ko_kr.json",
            {
                "entity.productivebees.fluix_bee": "플루익스 벌",
                "productivebees.ingredient.description.spacial_bee": (
                    "이 벌의 벌집을 원심분리하여 추가 처리가 필요한 "
                    "서투스 석영 씨앗을 얻을 수 있습니다."
                ),
            },
        ),
    )
    related_lang_paths: list[Path] = []
    for working_path, related_output_path, expected_values in related_lang_terms:
        working_lang = load_json_unique(working_path)
        output_related_lang = load_json_unique(related_output_path)
        for key, expected_value in expected_values.items():
            if working_lang.get(key) != expected_value:
                raise ValueError(
                    f"AE2 연동 용어 작업본이 다릅니다: {working_path}: {key}"
                )
            if output_related_lang.get(key) != expected_value:
                raise ValueError(
                    f"AE2 연동 용어 출력이 다릅니다: {related_output_path}: {key}"
                )
        related_lang_paths.extend((working_path, related_output_path))

    terminology_roots = (
        PROJECT_ROOT / "working/ae2/ae2guide/_ko_kr",
        RESOURCEPACK_ROOT / "assets/ae2/ae2guide/_ko_kr",
        PROJECT_ROOT / "working/ae2_addons/extendedae/ae2guide/_ko_kr",
        RESOURCEPACK_ROOT / "assets/extendedae/ae2guide/_ko_kr",
        PROJECT_ROOT / "working/ae2_addons/megacells/ae2guide/_ko_kr",
        RESOURCEPACK_ROOT / "assets/megacells/ae2guide/_ko_kr",
    )
    forbidden_guide_terms = (
        "회로 인쇄기",
        "압형",
        "연산 패턴",
        "엔지니어링 패턴",
        "연산 회로",
        "엔지니어링 회로",
        "하늘석",
        "스카이 스톤",
    )
    terminology_errors = []
    for root in terminology_roots:
        for path in root.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            remaining = [term for term in forbidden_guide_terms if term in text]
            if remaining:
                terminology_errors.append(f"{path}: {remaining}")
    if terminology_errors:
        raise ValueError(
            "AE2 가이드 비표준 용어가 남았습니다:\n" + "\n".join(terminology_errors)
        )

    pack_meta_path = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/pack.mcmeta"
    pack_meta = json.loads(pack_meta_path.read_text(encoding="utf-8"))
    if pack_meta.get("pack", {}).get("pack_format") != 34:
        raise ValueError("Minecraft 1.21.1용 pack_format이 아닙니다.")

    checked_files = (
        output_lang,
        quests.OUTPUT_FILE,
        kube_path,
        pack_meta_path,
        PROGRESS_FILE,
        quests.PROGRESS_FILE,
        quests.OVERRIDES_FILE,
        *compat_paths,
        *related_lang_paths,
        *ADDON_QUEST_OVERRIDE_FILES,
        *LATER_REVIEWED_QUEST_FILES,
    )
    for path in checked_files:
        ensure_no_bom(path)

    result = {
        "ae2_resourcepack_keys": len(translated),
        "ftbquest_keys": len(expected),
        "kubejs_keys": len(kube),
        "ae2_compat_keys": compat_keys,
        "intentional_english_values": sum(
            translated[key] == english[key] for key in ALLOWED_IDENTICAL_TRANSLATIONS
        ),
        "extendedae_infinity_cell_keys": len(infinity_keys),
        "unrelated_ftbquest_keys_changed": 0,
        "ftbquest_title_keys_changed": sum(
            full_current.get(key) != full_output.get(key)
            for key in set(full_current) | set(full_output)
            if titles.TITLE_KEY_RE.fullmatch(key)
        ),
        "validation_errors": 0,
        "terminology_errors": 0,
        "utf8_bom_files": 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
