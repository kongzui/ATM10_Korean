#!/usr/bin/env python3
"""공통 UI 언어 파일의 구조와 보호 문자열을 검증하고 산출물에 반영한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from zipfile import ZipFile

from common_ui_catalog import (
    GROUPS,
    PACK_LANGUAGE_TARGETS,
    TARGETS,
    PackLanguageTarget,
    Target,
)
from build_ae2_quests import flatten, parse_language_snbt
from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_common_ui import WORK_ROOT, find_jar, load_json

OUTPUT_ROOT = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
JEI_QUEST_TERM_KEYS = {
    "quest.13AA91D39A2CABF2.quest_desc",
    "quest.1FCC474860587169.quest_desc",
    "quest.4B7840F1A8CF1378.quest_desc",
    "quest.57C4A0BAE739E903.quest_desc",
    "quest.65C8A43FEDBA3835.quest_desc",
    "quest.683C260C854C5AA3.quest_desc",
}
JEI_QUEST_WORKING_FILES = {
    "quest.13AA91D39A2CABF2.quest_desc": Path(
        "working/productivebees/quest_overrides.json"
    ),
    "quest.1FCC474860587169.quest_desc": Path(
        "working/forbidden_arcanus/quests/related/ko_kr.json"
    ),
    "quest.4B7840F1A8CF1378.quest_desc": Path(
        "working/draconic_evolution/quests/draconic_evolution/ko_kr.json"
    ),
    "quest.57C4A0BAE739E903.quest_desc": Path(
        "working/industrial_foregoing/quests/industrial_foregoing/ko_kr.json"
    ),
    "quest.65C8A43FEDBA3835.quest_desc": Path(
        "working/refined_storage/quests/refined_storage/ko_kr.json"
    ),
    "quest.683C260C854C5AA3.quest_desc": Path(
        "working/cataclysm/quests/cataclysm/ko_kr.json"
    ),
}
JEI_QUEST_OVERRIDES = PROJECT_ROOT / "working/common_ui/jei/quest_overrides.json"
JEI_KUBEJS_RELATIVE = Path("kubejs/startup_scripts/incompatible_versions.js")
JEI_KUBEJS_ENGLISH = (
    'event.checkModVersion("jei", "19.22.0.316", '
    '"This version is causing durability tools issues")'
)
JEI_KUBEJS_KOREAN = (
    'event.checkModVersion("jei", "19.22.0.316", '
    '"이 버전은 도구 내구도 문제를 일으킵니다")'
)
JADE_RECHECK_VALUES = {
    "tooltip.jade.mode_comparator": "비교",
    "tooltip.jade.power": "신호 세기: %d",
    "jade.input_signal": "입력 신호: %d",
    "gui.jade.by": "Snownee가 %s을 담아 만들었습니다",
    "config.jade.display_entities": "개체 표시",
    "config.jade.display_entities_extra_msg": "entity,엔티티,개체",
    "config.jade.plugin_minecraft.entity": "Minecraft - 개체",
    "config.jade.plugin_minecraft.entity_health": "개체 체력",
    "config.jade.plugin_minecraft.entity_armor": "개체 방어력",
    "config.jade.plugin_minecraft.potion_effects": "개체 상태 효과",
    "config.jade.plugin_minecraft.container_entity": "보관함 개체",
    "jade.instrument.hat": "클릭과 스틱",
    "config.jade.plugin_minecraft.next_entity_drop": "개체의 다음 드롭 시간",
    "config.jade.plugin_minecraft.next_entity_drop_desc": (
        "달걀이나 아르마딜로 인갑처럼 개체가 다음 아이템을 떨어뜨릴 때까지 "
        "남은 시간을 표시합니다."
    ),
    "jade.harvest_tool.unbreakable": "부서지지 않음",
    "jade.locked": "보관함이 잠겨 있습니다",
    "config.jade.plugin_minecraft.animal_owner": "동물 소유자",
    "jade.owner": "소유자: %s",
    "jade.seconds": "{0}초",
    "jade.minutes": "{0}분",
    "jade.minutes_seconds": "{0}분 {1}초",
    "config.jade.plugin_jade_access.entity": "개체 세부 정보",
    "jade.access.entity.white": "하얀색 %s",
    "jade.access.entity.light_gray": "회백색 %s",
    "jade.access.entity.lime": "연두색 %s",
    "jade.access.entity.light_blue": "하늘색 %s",
    "jade.access.entity.purple": "보라색 %s",
    "jade.access.entity.magenta": "자홍색 %s",
    "config.jade.plugin_jade_access.entity_variant": "개체 변형",
    "config.jade.plugin_jade_access.held_item": "개체가 들고 있는 아이템",
    "jade.ignore_list.comment": (
        'Jade가 무시할 대상 목록입니다. "values" 목록에 레지스트리 ID를 '
        "추가할 수 있습니다."
    ),
}
JADE_KUBEJS_LANGUAGE = {
    "config.jade.plugin_modern_industrialization.overclock": "Machine Overclock",
    "config.jade.plugin_modern_industrialization.pipe": "Pipe Information",
}
JADE_KUBEJS_KOREAN = {
    "config.jade.plugin_modern_industrialization.overclock": "기계 오버클럭",
    "config.jade.plugin_modern_industrialization.pipe": "파이프 정보",
}
JADE_LANGUAGE_PREFIXES = ("config.jade.", "jade.", "waila.", "gui.waila.")


def protected(value: object, pattern: re.Pattern[str]) -> list[str]:
    return pattern.findall(value) if isinstance(value, str) else []


def validate_value(
    key: str,
    english: object,
    korean: object,
    errors: list[str],
    path: str = "",
    translatable: bool = True,
) -> None:
    """중첩 텍스트 컴포넌트까지 자료형과 보호 문자열을 검증한다."""
    location = f"{key}{path}"
    if type(english) is not type(korean):
        errors.append(f"자료형 불일치: {location}")
        return
    if isinstance(english, str):
        if not translatable and english != korean:
            errors.append(f"비번역 필드 변경: {location}")
        protected_english = english
        protected_korean = korean
        is_jei_search_mode = (
            key.startswith("jei.config.client.search.")
            and key.endswith("SearchMode")
            and english[:1] in "@#$^&%"
        )
        if is_jei_search_mode:
            if korean[:1] != english[:1]:
                errors.append(f"JEI 검색 접두사 불일치: {location}")
            protected_english = english[1:]
            protected_korean = korean[1:]
        if protected(protected_english, PLACEHOLDER) != protected(
            protected_korean, PLACEHOLDER
        ):
            errors.append(f"자리표시자 불일치: {location}")
        if protected(protected_english, FORMAT_CODE) != protected(
            protected_korean, FORMAT_CODE
        ):
            errors.append(f"서식 코드 불일치: {location}")
        if english.count("\n") != korean.count("\n"):
            errors.append(f"줄바꿈 수 불일치: {location}")
        return
    if isinstance(english, list):
        if len(english) != len(korean):
            errors.append(f"목록 길이 불일치: {location}")
            return
        for index, (english_item, korean_item) in enumerate(zip(english, korean)):
            validate_value(
                key,
                english_item,
                korean_item,
                errors,
                f"{path}[{index}]",
                translatable,
            )
        return
    if isinstance(english, dict):
        if list(english) != list(korean):
            errors.append(f"객체 키 또는 순서 불일치: {location}")
            return
        for field in english:
            validate_value(
                key,
                english[field],
                korean[field],
                errors,
                f"{path}.{field}",
                field == "text",
            )
        return
    if english != korean:
        errors.append(f"비문자 값 변경: {location}")


def verify_target(
    instance: Path, target: Target, copy_output: bool
) -> list[dict[str, object]]:
    jar_path = find_jar(instance, target)
    rows = []
    with ZipFile(jar_path) as jar:
        for namespace in target.namespaces:
            english = load_json(jar, f"assets/{namespace}/lang/en_us.json")
            if target.key_prefixes:
                english = {
                    key: value
                    for key, value in english.items()
                    if key.startswith(target.key_prefixes)
                }
            working = WORK_ROOT / target.group / namespace / "ko_kr.json"
            korean = json.loads(working.read_text(encoding="utf-8"))
            errors = []
            if list(korean) != list(english):
                missing = sorted(set(english) - set(korean))
                extra = sorted(set(korean) - set(english))
                errors.append(f"키 또는 순서 불일치: 누락={missing}, 초과={extra}")
            for key in english.keys() & korean.keys():
                validate_value(key, english[key], korean[key], errors)
            if working.read_bytes().startswith(b"\xef\xbb\xbf"):
                errors.append("UTF-8 BOM이 있습니다")
            if errors:
                raise RuntimeError(f"{namespace} 검증 실패:\n" + "\n".join(errors[:30]))
            output = OUTPUT_ROOT / namespace / "lang/ko_kr.json"
            if copy_output:
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(working, output)
            rows.append(
                {
                    "group": target.group,
                    "jar": jar_path.name,
                    "namespace": namespace,
                    "keys": len(english),
                    "output": output.relative_to(PROJECT_ROOT).as_posix(),
                    "validation": "passed",
                }
            )
    return rows


def verify_pack_target(
    instance: Path, target: PackLanguageTarget, copy_output: bool
) -> dict[str, object]:
    """팩의 KubeJS 언어 파일도 JAR 언어 파일과 같은 기준으로 검증한다."""
    english_path = instance / target.relative_dir / "en_us.json"
    english = json.loads(english_path.read_text(encoding="utf-8-sig"))
    working = WORK_ROOT / target.group / target.namespace / "ko_kr.json"
    korean = json.loads(working.read_text(encoding="utf-8"))
    errors = []
    if list(korean) != list(english):
        missing = sorted(set(english) - set(korean))
        extra = sorted(set(korean) - set(english))
        errors.append(f"키 또는 순서 불일치: 누락={missing}, 초과={extra}")
    for key in english.keys() & korean.keys():
        validate_value(key, english[key], korean[key], errors)
    if working.read_bytes().startswith(b"\xef\xbb\xbf"):
        errors.append("UTF-8 BOM이 있습니다")
    if errors:
        raise RuntimeError(f"{target.namespace} 검증 실패:\n" + "\n".join(errors[:30]))
    output = OUTPUT_ROOT / target.namespace / "lang/ko_kr.json"
    if copy_output:
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(working, output)
    return {
        "group": target.group,
        "source": target.relative_dir,
        "namespace": target.namespace,
        "keys": len(english),
        "output": output.relative_to(PROJECT_ROOT).as_posix(),
        "validation": "passed",
    }


def verify_jei_related(instance: Path) -> dict[str, object]:
    """JEI가 직접 언급되는 퀘스트와 KubeJS 표시 경로를 검증한다."""
    source_lang = instance / "config/ftbquests/quests/lang/en_us.snbt"
    output_lang = (
        PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
    )
    english = parse_language_snbt(source_lang)
    korean = parse_language_snbt(output_lang)
    related_keys = {
        key for key, value in english.items() if "jei" in flatten(value).lower()
    }
    errors = []
    if len(related_keys) != 25:
        errors.append(f"JEI 관련 FTB Quests 키 수 불일치: {len(related_keys)}")
    missing = sorted(related_keys - set(korean))
    if missing:
        errors.append(f"JEI 관련 FTB Quests 한국어 누락: {missing}")
    lost_name = sorted(
        key
        for key in related_keys & set(korean)
        if "jei" not in flatten(korean[key]).lower()
    )
    if lost_name:
        errors.append(f"JEI 관련 퀘스트에서 모드명 누락: {lost_name}")
    inconsistent_terms = sorted(
        key
        for key in JEI_QUEST_TERM_KEYS
        if key not in korean
        or re.search(r"조합법|레시피", flatten(korean[key])) is not None
    )
    if inconsistent_terms:
        errors.append(f"JEI 관련 퀘스트 제작법 용어 불일치: {inconsistent_terms}")
    working_mismatches = []
    for key, relative in JEI_QUEST_WORKING_FILES.items():
        values = json.loads((PROJECT_ROOT / relative).read_text(encoding="utf-8"))
        if key not in values or flatten(values[key]) != flatten(korean[key]):
            working_mismatches.append(relative.as_posix())
    if working_mismatches:
        errors.append(f"JEI 관련 퀘스트 작업본 불일치: {working_mismatches}")
    jei_overrides = json.loads(JEI_QUEST_OVERRIDES.read_text(encoding="utf-8"))
    if set(jei_overrides) != JEI_QUEST_TERM_KEYS:
        errors.append("JEI 관련 퀘스트 전용 override 키 범위가 다릅니다")
    override_mismatches = sorted(
        key
        for key in set(jei_overrides) & set(korean)
        if flatten(jei_overrides[key]) != flatten(korean[key])
    )
    if override_mismatches:
        errors.append(f"JEI 관련 퀘스트 전용 override 불일치: {override_mismatches}")

    source_script = instance / JEI_KUBEJS_RELATIVE
    output_script = PROJECT_ROOT / "output/overrides" / JEI_KUBEJS_RELATIVE
    source_text = source_script.read_text(encoding="utf-8")
    output_text = output_script.read_text(encoding="utf-8")
    if source_text.count(JEI_KUBEJS_ENGLISH) == 1:
        expected_text = source_text.replace(JEI_KUBEJS_ENGLISH, JEI_KUBEJS_KOREAN)
    elif source_text.count(JEI_KUBEJS_KOREAN) == 1:
        expected_text = source_text
    else:
        expected_text = ""
        errors.append("JEI KubeJS 원문 표시 문자열을 하나로 확정하지 못했습니다")
    if output_text != expected_text:
        errors.append("JEI KubeJS override가 계획한 한 문자열 변경과 다릅니다")
    mi_output = json.loads(
        (OUTPUT_ROOT / "modern_industrialization/lang/ko_kr.json").read_text(
            encoding="utf-8"
        )
    )
    mi_related_keys = {
        "modern_industrialization.configuration.missingRecipeViewerMessage",
        "modern_industrialization.configuration.missingRecipeViewerMessage.tooltip",
        "text.modern_industrialization.NoEmi",
    }
    mi_missing = sorted(mi_related_keys - set(mi_output))
    if mi_missing:
        errors.append(f"KubeJS 제작법 뷰어 연동 언어 키 누락: {mi_missing}")
    mi_inconsistent = sorted(
        key
        for key in mi_related_keys & set(mi_output)
        if re.search(r"조합법|레시피", str(mi_output[key])) is not None
    )
    if mi_inconsistent:
        errors.append(f"KubeJS 제작법 뷰어 용어 불일치: {mi_inconsistent}")

    jei_target = next(
        target
        for target in TARGETS
        if target.group == "jei" and target.namespaces == ("jei",)
    )
    jar_path = find_jar(instance, jei_target)
    with ZipFile(jar_path) as archive:
        names = archive.namelist()
        class_files = sum(name.endswith(".class") for name in names)
        guide_files = sum(
            marker in name.lower()
            for name in names
            for marker in ("patchouli", "guideme", "modonomicon")
        )
        advancement_files = sum(
            name.endswith(".json") and "/advancement" in name for name in names
        )
    if errors:
        raise RuntimeError("JEI 연관 경로 검증 실패:\n" + "\n".join(errors))
    return {
        "group": "jei",
        "namespace": "jei_related_paths",
        "source_jar_sha256": hashlib.sha256(jar_path.read_bytes()).hexdigest(),
        "class_files_reviewed": class_files,
        "ftbquests_keys_reviewed": len(related_keys),
        "ftbquests_terms_corrected": len(JEI_QUEST_TERM_KEYS),
        "kubejs_files_reviewed": 4,
        "kubejs_display_values_reviewed": 4,
        "kubejs_display_values_retained": 3,
        "kubejs_display_literals_corrected": 1,
        "guide_files": guide_files,
        "advancement_files": advancement_files,
        "validation": "passed",
    }


def verify_jade_related(instance: Path) -> dict[str, object]:
    """Jade 본체 밖의 실제 표시 경로와 연동 키 소유 범위를 검증한다."""
    errors = []
    output_path = OUTPUT_ROOT / "jade/lang/ko_kr.json"
    korean = json.loads(output_path.read_text(encoding="utf-8"))
    mismatches = sorted(
        key
        for key, expected in JADE_RECHECK_VALUES.items()
        if korean.get(key) != expected
    )
    if mismatches:
        errors.append(f"Jade 확정 교정값 불일치: {mismatches}")

    source_lang = instance / "config/ftbquests/quests/lang/en_us.snbt"
    quests = parse_language_snbt(source_lang)
    quest_refs = sorted(
        key
        for key, value in quests.items()
        if re.search(r"(?i)\b(?:jade|waila|hwyla)\b", flatten(value))
    )
    if quest_refs:
        errors.append(f"예상하지 않은 Jade 관련 FTB Quests 키: {quest_refs}")

    kubejs_language: dict[str, str] = {}
    for path in sorted((instance / "kubejs").rglob("en_us.json")):
        values = json.loads(path.read_text(encoding="utf-8-sig"))
        for key, value in values.items():
            if key.startswith(JADE_LANGUAGE_PREFIXES):
                kubejs_language[key] = value
    if kubejs_language != JADE_KUBEJS_LANGUAGE:
        errors.append(f"KubeJS Jade 언어 키 범위 불일치: {kubejs_language}")

    mi_output = json.loads(
        (OUTPUT_ROOT / "modern_industrialization/lang/ko_kr.json").read_text(
            encoding="utf-8"
        )
    )
    mi_working = json.loads(
        (
            PROJECT_ROOT
            / "working/modern_industrialization/modern_industrialization/ko_kr.json"
        ).read_text(encoding="utf-8")
    )
    for key, expected in JADE_KUBEJS_KOREAN.items():
        if mi_output.get(key) != expected or mi_working.get(key) != expected:
            errors.append(f"KubeJS Jade 연동 번역 불일치: {key}")

    kubejs_script_refs = []
    for path in sorted((instance / "kubejs").rglob("*.js")):
        for number, line in enumerate(
            path.read_text(encoding="utf-8-sig").splitlines(), start=1
        ):
            if re.search(r"(?i)\b(?:jade|waila|hwyla)\b", line):
                kubejs_script_refs.append(
                    f"{path.relative_to(instance).as_posix()}:{number}"
                )
    expected_script_ref = ["kubejs/server_scripts/mods/Minecolonies/tags.js:228"]
    if kubejs_script_refs != expected_script_ref:
        errors.append(f"KubeJS Jade 스크립트 참조 불일치: {kubejs_script_refs}")

    related_language_files = 0
    related_owned_keys = 0
    missing_owned_keys = []
    mods_root = instance / "mods"
    jade_target = next(target for target in TARGETS if target.group == "jade")
    jade_jar = find_jar(instance, jade_target)
    for jar_path in sorted(mods_root.glob("*.jar")):
        if jar_path == jade_jar:
            continue
        with ZipFile(jar_path) as archive:
            for name in archive.namelist():
                if not re.fullmatch(r"assets/[^/]+/lang/en_us\.json", name):
                    continue
                values = load_json(archive, name)
                keys = sorted(
                    key for key in values if key.startswith(JADE_LANGUAGE_PREFIXES)
                )
                if not keys:
                    continue
                related_language_files += 1
                related_owned_keys += len(keys)
                namespace = name.split("/")[1]
                related_output = OUTPUT_ROOT / namespace / "lang/ko_kr.json"
                translated = (
                    json.loads(related_output.read_text(encoding="utf-8"))
                    if related_output.is_file()
                    else {}
                )
                missing_owned_keys.extend(
                    f"{namespace}:{key}" for key in keys if key not in translated
                )
    if (related_language_files, related_owned_keys) != (51, 199):
        errors.append(
            "다른 모드 소유 Jade 연동 범위 불일치: "
            f"파일={related_language_files}, 키={related_owned_keys}"
        )

    with ZipFile(jade_jar) as archive:
        names = archive.namelist()
        english = load_json(archive, "assets/jade/lang/en_us.json")
    collisions: dict[str, set[str]] = {}
    for key, value in korean.items():
        collisions.setdefault(str(value), set()).add(str(english[key]))
    collisions = {
        value: source_values
        for value, source_values in collisions.items()
        if len(source_values) > 1
    }
    expected_collisions = {"위": {"Top", "Up"}}
    if collisions != expected_collisions:
        errors.append(f"Jade 번역 유발 이름 충돌 불일치: {collisions}")

    class_files = sum(name.endswith(".class") for name in names)
    json_files = sum(name.endswith(".json") for name in names)
    advancement_files = sum(
        name.endswith(".json") and "/advancement" in name.lower() for name in names
    )
    recipe_files = sum(
        name.endswith(".json") and "/recipe" in name.lower() for name in names
    )
    guide_files = sum(
        any(
            marker in name.lower() for marker in ("patchouli", "guideme", "modonomicon")
        )
        for name in names
    )
    screen_json_files = sum(
        name.endswith(".json") and "screen" in name.lower() for name in names
    )
    if (class_files, json_files, advancement_files, recipe_files, guide_files) != (
        301,
        18,
        0,
        0,
        0,
    ):
        errors.append("Jade JAR 표시 경로 인벤토리가 달라졌습니다")
    if screen_json_files:
        errors.append(f"Jade 화면 JSON을 추가 검수해야 합니다: {screen_json_files}")
    if errors:
        raise RuntimeError("Jade 연관 경로 검증 실패:\n" + "\n".join(errors))
    return {
        "group": "jade",
        "namespace": "jade_related_paths",
        "source_jar_sha256": hashlib.sha256(jade_jar.read_bytes()).hexdigest(),
        "class_files_reviewed": class_files,
        "ftbquests_keys_reviewed": len(quest_refs),
        "kubejs_language_values_reviewed": len(kubejs_language),
        "kubejs_script_references_reviewed": len(kubejs_script_refs),
        "other_mod_language_files_traced": related_language_files,
        "other_mod_owned_keys_traced": related_owned_keys,
        "other_mod_owned_missing_keys_deferred": len(missing_owned_keys),
        "translation_induced_name_collisions": 0,
        "direction_label_collisions_retained": len(collisions),
        "advancement_files": advancement_files,
        "recipe_files": recipe_files,
        "guide_files": guide_files,
        "screen_json_files": screen_json_files,
        "validation": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("group", choices=GROUPS + ("all",))
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--copy-output", action="store_true")
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    selected = [
        target
        for target in TARGETS
        if args.group == "all" or target.group == args.group
    ]
    rows = []
    for target in selected:
        rows.extend(verify_target(instance, target, args.copy_output))
    pack_selected = [
        target
        for target in PACK_LANGUAGE_TARGETS
        if args.group == "all" or target.group == args.group
    ]
    for target in pack_selected:
        rows.append(verify_pack_target(instance, target, args.copy_output))
    if args.group in {"jei", "all"}:
        rows.append(verify_jei_related(instance))
    if args.group in {"jade", "all"}:
        rows.append(verify_jade_related(instance))
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
