#!/usr/bin/env python3
"""Silent Gear 관련 KubeJS 표시 문구를 검증된 덮어쓰기 산출물로 만든다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from local_paths import PROJECT_ROOT, resolve_source_root

TRAIT_ROOT = Path("kubejs/data/silentgear/silentgear_traits")
OUTPUT_ROOT = PROJECT_ROOT / "output/overrides"
REPORT = PROJECT_ROOT / "working/silentgear/kubejs_audit.json"
TRAITS = {
    "advanced_aquatic.json": {
        "name": ("Advanced Aquatic", "고급 수생"),
        "description": (
            "Advanced Aquatic gives waterbreathing without a full set",
            "고급 수생 특성은 방어구 풀세트가 아니어도 수중 호흡을 부여합니다",
        ),
    },
    "advanced_flame_ward.json": {
        "name": ("Advanced Flame Ward", "고급 화염 수호"),
        "description": (
            "Gives fire resistance without a full set",
            "방어구 풀세트가 아니어도 화염 저항을 부여합니다",
        ),
        "extra_wiki_lines": (
            "  - The item cannot be destroyed by fire or lava",
            "  - 아이템은 불이나 용암에 의해 파괴되지 않습니다",
        ),
    },
    "cure_levitation.json": {
        "name": ("Cure Levitation", "공중 부양 해제"),
        "description": (
            "Removes levitation effect when equipped",
            "착용하면 공중 부양 효과를 제거합니다",
        ),
    },
    "cure_nausea.json": {
        "name": ("Cure Nausea", "멀미 해제"),
        "description": (
            "Removes nausea effect when equipped",
            "착용하면 멀미 효과를 제거합니다",
        ),
    },
}
ATM_MATERIALS = {
    "material.silentgear.allthemodium": "Allthemodium",
    "material.silentgear.vibranium": "Vibranium",
    "material.silentgear.vibranium_allthemodium": "Vibranium-Allthemodium 합금",
    "material.silentgear.unobtainium_allthemodium": "Unobtainium-Allthemodium 합금",
    "material.silentgear.unobtainium_vibranium": "Unobtainium-Vibranium 합금",
    "material.silentgear.unobtainium": "Unobtainium",
}
ACTIVE_MATERIAL_KEYS = {
    "material.silentgear.allthemodium",
    "material.silentgear.vibranium",
    "material.silentgear.unobtainium",
}


def load_object(path: Path) -> dict[str, object]:
    """JSON 객체를 UTF-8로 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def build_trait(instance: Path, name: str, rules: dict[str, tuple[str, str]]) -> int:
    """원본 구조를 보존하고 사용자 표시 literal만 번역한다."""
    source = instance / TRAIT_ROOT / name
    value = load_object(source)
    changes = 0
    for field in ("name", "description"):
        expected, translated = rules[field]
        component = value.get(field)
        if not isinstance(component, dict) or component.get("text") != expected:
            raise RuntimeError(f"예상한 {field} 원문과 다릅니다: {source}")
        component["text"] = translated
        changes += 1
    if "extra_wiki_lines" in rules:
        expected, translated = rules["extra_wiki_lines"]
        lines = value.get("extra_wiki_lines")
        if lines != [expected]:
            raise RuntimeError(f"예상한 위키 추가 문구와 다릅니다: {source}")
        value["extra_wiki_lines"] = [translated]
        changes += 1
    output = OUTPUT_ROOT / TRAIT_ROOT / name
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return changes


def verify_material_sources(instance: Path) -> list[str]:
    """ATM 재료 데이터가 기대한 여섯 번역 키를 실제로 참조하는지 확인한다."""
    found: set[str] = set()
    data_root = instance / "kubejs/data/silentgear/silentgear_materials"
    for path in data_root.glob("*.json"):
        value = load_object(path)
        display = value.get("display")
        if not isinstance(display, dict):
            continue
        name = display.get("name")
        if isinstance(name, dict) and isinstance(name.get("translate"), str):
            key = name["translate"]
            if key in ATM_MATERIALS:
                found.add(key)
    missing = sorted(ACTIVE_MATERIAL_KEYS - found)
    if missing:
        raise RuntimeError(f"ATM Silent Gear 재료 데이터 키 누락: {missing}")
    return sorted(found)


def build_material_language() -> Path:
    """KubeJS가 추가한 ATM 재료명 한국어 파일을 만든다."""
    output = (
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/atm10_localization/lang/ko_kr.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(ATM_MATERIALS, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    material_keys = verify_material_sources(instance)
    literal_count = sum(
        build_trait(instance, name, rules) for name, rules in TRAITS.items()
    )
    material_output = build_material_language()
    report = {
        "trait_files": len(TRAITS),
        "translated_literals": literal_count,
        "material_translate_keys": material_keys,
        "material_language_file": str(material_output.relative_to(PROJECT_ROOT)),
        "status": "passed",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
