#!/usr/bin/env python3
"""Create 계열 JAR 데이터와 KubeJS의 직접 표시 문구를 검사한다."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

from five_family_goal import PROJECT_ROOT, load_json
from local_paths import resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/create"
NAMESPACES = {
    "create",
    "create_dragons_plus",
    "createaddition",
    "create_enchantment_industry",
    "create_aquatic_ambitions",
    "create_hypertube",
    "bellsandwhistles",
}
VISIBLE_FIELDS = {"name", "title", "description", "text"}
ENGLISH_WORD = re.compile(r"[A-Za-z]{2,}")


def dump_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 안정된 형식으로 기록한다."""
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def component_literals(value: object) -> list[str]:
    """텍스트 컴포넌트의 번역 키를 쓰지 않은 직접 문자열을 모은다."""
    found = []
    if isinstance(value, dict):
        text = value.get("text")
        if isinstance(text, str) and ENGLISH_WORD.search(text):
            found.append(text)
        for child in value.values():
            found.extend(component_literals(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(component_literals(child))
    return found


def visible_literals(value: object) -> list[str]:
    """표시용 이름 필드에 직접 쓰인 자연어 문자열을 모은다."""
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if (
                key in VISIBLE_FIELDS
                and isinstance(child, str)
                and ENGLISH_WORD.search(child)
                and ":" not in child
                and "/" not in child
            ):
                found.append(child)
            found.extend(visible_literals(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(visible_literals(child))
    return found


def audit() -> tuple[dict[str, object], list[str]]:
    """설치된 JAR과 KubeJS에서 언어 파일을 우회하는 문구를 검사한다."""
    instance = resolve_source_root()
    inventory = load_json(WORK_ROOT / "inventory.json")
    errors = []
    jar_rows = []
    for installed in inventory["installed"]:
        namespace = installed["namespace"]
        jar_name = installed["jar"]
        jar_path = instance / "mods" / jar_name
        advancement_count = 0
        advancement_displays = 0
        advancement_literals = []
        recipe_count = 0
        recipe_literals = []
        ponder_assets = 0
        ponder_literals = []
        with ZipFile(jar_path) as archive:
            for name in archive.namelist():
                if not name.endswith(".json"):
                    continue
                if name.startswith("data/") and "/advancement/" in name:
                    advancement_count += 1
                    data = json.loads(archive.read(name).decode("utf-8"))
                    display = data.get("display") if isinstance(data, dict) else None
                    if display is not None:
                        advancement_displays += 1
                        literals = component_literals(display)
                        if literals:
                            advancement_literals.append(
                                {"path": name, "values": literals[:5]}
                            )
                elif name.startswith("data/") and "/recipe/" in name:
                    recipe_count += 1
                    data = json.loads(archive.read(name).decode("utf-8"))
                    literals = visible_literals(data)
                    if literals:
                        recipe_literals.append({"path": name, "values": literals[:5]})
                elif "/ponder/" in name:
                    ponder_assets += 1
                    data = json.loads(archive.read(name).decode("utf-8"))
                    literals = component_literals(data)
                    if literals:
                        ponder_literals.append({"path": name, "values": literals[:5]})

        language = load_json(WORK_ROOT / namespace / "en_us.json")
        ponder_language_keys = sum(".ponder." in key for key in language)
        if advancement_literals:
            errors.append(f"발전 과제 직접 영문 발견: {namespace}")
        if recipe_literals:
            errors.append(f"조합법 직접 영문 발견: {namespace}")
        if ponder_literals:
            errors.append(f"Ponder 직접 영문 발견: {namespace}")
        jar_rows.append(
            {
                "namespace": namespace,
                "jar": jar_name,
                "advancements_checked": advancement_count,
                "advancement_display_entries": advancement_displays,
                "advancement_direct_literals": advancement_literals,
                "recipes_checked": recipe_count,
                "recipe_direct_literals": recipe_literals,
                "ponder_json_assets_checked": ponder_assets,
                "ponder_direct_literals": ponder_literals,
                "ponder_language_keys": ponder_language_keys,
            }
        )

    namespace_pattern = re.compile(
        r"(?:create|create_dragons_plus|createaddition|"
        r"create_enchantment_industry|create_aquatic_ambitions|"
        r"create_hypertube|bellsandwhistles):",
        re.IGNORECASE,
    )
    visible_pattern = re.compile(
        r"displayName|tooltip|custom_name|Text\.(?:of|literal)|"
        r"\.title\(|\.description\(",
        re.IGNORECASE,
    )
    kubejs_root = instance / "kubejs"
    reference_files = []
    direct_visible_lines = []
    for path in kubejs_root.rglob("*.js"):
        text = path.read_text(encoding="utf-8")
        if not namespace_pattern.search(text):
            continue
        relative = path.relative_to(kubejs_root).as_posix()
        reference_files.append(relative)
        for line_number, line in enumerate(text.splitlines(), 1):
            if namespace_pattern.search(line) and visible_pattern.search(line):
                direct_visible_lines.append(f"{relative}:{line_number}")
    if direct_visible_lines:
        errors.append("KubeJS Create 직접 참조 줄에 사용자 표시 문구가 발견됨")

    report = {
        "jars": jar_rows,
        "kubejs_reference_files_checked": len(reference_files),
        "kubejs_reference_files": sorted(reference_files),
        "kubejs_direct_visible_lines": direct_visible_lines,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    dump_json(WORK_ROOT / "data_audit.json", report)
    return report, errors


def main() -> int:
    report, errors = audit()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
