#!/usr/bin/env python3
"""AE2 리소스팩, FTB Quests와 KubeJS 번역 산출물을 읽기 전용으로 검증한다."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import build_ae2_quests as quests
import build_ae2_translation as resourcepack
import build_ftbquests_titles as titles
from local_paths import resolve_source_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
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
)


def ensure_no_bom(path: Path) -> None:
    if path.read_bytes().startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"UTF-8 BOM이 있습니다: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)

    jar = instance / "mods/appliedenergistics2-19.2.17.jar"
    english = resourcepack.load_zip_json(jar, "assets/ae2/lang/en_us.json")
    output_lang = resourcepack.OUTPUT_LANG
    translated = json.loads(output_lang.read_text(encoding="utf-8"))
    if list(translated) != list(english):
        raise ValueError("AE2 리소스팩 키 또는 키 순서가 영어 원문과 다릅니다.")
    resource_errors = []
    for key in english:
        resource_errors.extend(
            resourcepack.validate_pair(key, english[key], translated[key])
        )
    if resource_errors:
        raise ValueError("\n".join(resource_errors))

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
    additional_overrides = common_overrides | addon_overrides
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

    kube_path = (
        PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/kubejs/lang/ko_kr.json"
    )
    kube = json.loads(kube_path.read_text(encoding="utf-8"))
    if kube.get("item.kubejs.universal_press") != "각인기 범용 프레스":
        raise ValueError("KubeJS 범용 프레스 번역이 없습니다.")
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

    pack_meta_path = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/pack.mcmeta"
    pack_meta = json.loads(pack_meta_path.read_text(encoding="utf-8"))
    if pack_meta.get("pack", {}).get("pack_format") != 34:
        raise ValueError("Minecraft 1.21.1용 pack_format이 아닙니다.")

    checked_files = (
        output_lang,
        quests.OUTPUT_FILE,
        kube_path,
        pack_meta_path,
        resourcepack.PROGRESS_FILE,
        quests.PROGRESS_FILE,
        quests.OVERRIDES_FILE,
        *ADDON_QUEST_OVERRIDE_FILES,
    )
    for path in checked_files:
        ensure_no_bom(path)

    result = {
        "ae2_resourcepack_keys": len(translated),
        "ftbquest_keys": len(expected),
        "kubejs_keys": len(kube),
        "extendedae_infinity_cell_keys": len(infinity_keys),
        "unrelated_ftbquest_keys_changed": 0,
        "ftbquest_title_keys_changed": sum(
            full_current.get(key) != full_output.get(key)
            for key in set(full_current) | set(full_output)
            if titles.TITLE_KEY_RE.fullmatch(key)
        ),
        "validation_errors": 0,
        "utf8_bom_files": 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
