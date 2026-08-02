#!/usr/bin/env python3
"""MI 계열 JAR 데이터와 KubeJS의 사용자 표시 경로를 검사한다."""

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

WORK_ROOT = PROJECT_ROOT / "working/modern_industrialization"
NAMESPACES = {
    "modern_industrialization",
    "extended_industrialization",
    "industrialization_overdrive",
}
ENGLISH_WORD = re.compile(r"[A-Za-z]{3,}")
KOREAN = re.compile(r"[가-힣]")


def dump_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def component_literals(value: object) -> list[str]:
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
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if (
                key in {"name", "title", "description", "text", "custom_name"}
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
    instance = resolve_source_root()
    inventory = load_json(WORK_ROOT / "inventory.json")
    errors = []
    jar_rows = []
    for installed in inventory["installed"]:
        namespace = installed["namespace"]
        if namespace not in NAMESPACES:
            continue
        jar_path = instance / "mods" / installed["jar"]
        advancement_count = 0
        recipe_count = 0
        advancement_literals = []
        recipe_literals = []
        with ZipFile(jar_path) as archive:
            for name in archive.namelist():
                if not name.endswith(".json"):
                    continue
                if name.startswith("data/") and "/advancement/" in name:
                    advancement_count += 1
                    data = json.loads(archive.read(name).decode("utf-8"))
                    display = data.get("display") if isinstance(data, dict) else None
                    literals = component_literals(display)
                    if literals:
                        advancement_literals.append({"path": name, "values": literals})
                elif name.startswith("data/") and "/recipe/" in name:
                    recipe_count += 1
                    data = json.loads(archive.read(name).decode("utf-8"))
                    literals = visible_literals(data)
                    if literals:
                        recipe_literals.append({"path": name, "values": literals})
        if advancement_literals:
            errors.append(f"발전 과제 직접 영문 발견: {namespace}")
        if recipe_literals:
            errors.append(f"제작법 직접 영문 발견: {namespace}")
        jar_rows.append(
            {
                "namespace": namespace,
                "jar": installed["jar"],
                "advancements_checked": advancement_count,
                "advancement_direct_literals": advancement_literals,
                "recipes_checked": recipe_count,
                "recipe_direct_literals": recipe_literals,
            }
        )

    kubejs_root = instance / "kubejs"
    namespace_pattern = re.compile(
        r"modern_industrialization:|extended_industrialization:|"
        r"industrialization_overdrive:",
        re.IGNORECASE,
    )
    reference_files = []
    for path in kubejs_root.rglob("*.js"):
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(kubejs_root).as_posix()
        if namespace_pattern.search(text) or "Modern Industrialization" in relative:
            reference_files.append(relative)

    visible_overrides = []
    override_root = PROJECT_ROOT / "output/overrides/kubejs"
    for relative in (
        "startup_scripts/CustomAdditions.js",
        "startup_scripts/Modern-Industrialization/atm_stuff.js",
    ):
        path = override_root / relative
        if not path.is_file():
            continue
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1
        ):
            if ".displayName(" not in line or line.lstrip().startswith("//"):
                continue
            match = re.search(r"\.displayName\(['\"](.+?)['\"]\)", line)
            if match:
                value = match.group(1)
                visible_overrides.append(
                    {"path": relative, "line": line_number, "value": value}
                )
                if relative.endswith("atm_stuff.js") and not KOREAN.search(value):
                    errors.append(f"MI KubeJS 표시명 미번역: {relative}:{line_number}")
                if relative.endswith("CustomAdditions.js") and value in {
                    "Liquid Souls",
                    "Unrefined Liquid Souls",
                    "Liquid Aureal",
                }:
                    errors.append(
                        f"MI 연관 KubeJS 표시명 미번역: {relative}:{line_number}"
                    )

    kube_lang_path = kubejs_root / "assets/modern_industrialization/lang/en_us.json"
    kube_extras = []
    if kube_lang_path.is_file():
        kube_lang = load_json(kube_lang_path)
        jar_lang = load_json(WORK_ROOT / "modern_industrialization/en_us.json")
        kube_extras = sorted(set(kube_lang) - set(jar_lang))
        translated_extra_path = WORK_ROOT / "kubejs_extra_ko_kr.json"
        translated_extras = (
            load_json(translated_extra_path) if translated_extra_path.is_file() else {}
        )
        if set(kube_extras) != set(translated_extras):
            errors.append(f"KubeJS MI 언어 추가 키 미처리: {kube_extras[:20]}")

    report = {
        "jars": jar_rows,
        "kubejs_reference_files_checked": len(reference_files),
        "kubejs_reference_files": sorted(reference_files),
        "kubejs_visible_overrides_checked": visible_overrides,
        "kubejs_language_extra_keys": kube_extras,
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
