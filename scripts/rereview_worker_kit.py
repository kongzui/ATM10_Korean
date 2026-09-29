#!/usr/bin/env python3
"""품질 재검수 워커에게 줄 자료를 만든다(실제 인스턴스와 JAR은 읽기만 한다).

- pairs <계열>: 계열 범위의 영어·한국어 대조 파일을 temp/rereview/<계열>/에 만든다.
- index: 영어 이름 → 프로젝트 한국어 이름 색인을 temp/rereview/name_index.json에 만든다.
- lookup <이름>...: 색인에서 영어 이름으로 확정 한국어 이름을 찾는다.
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

from build_ae2_quests import parse_language_snbt
from ftbquests_layout import split_locale_files
from local_paths import resolve_source_root
from rebase_ftbquests import OUTPUT_SPLIT_ROOT
from verify_quality_rereview import PACK_ASSETS
from version_context import active_output_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REREVIEW_ROOT = PROJECT_ROOT / "working/quality_rereview"
KIT_ROOT = PROJECT_ROOT / "temp/rereview"
INDEX_PATH = KIT_ROOT / "name_index.json"
LANG_RE = re.compile(r"assets/([^/]+)/lang/(en_us|ko_kr)\.json$")
NAME_PREFIXES = (
    "item.",
    "block.",
    "entity.",
    "fluid",
    "effect.",
    "biome.",
    "dimension.",
)


def jar_languages(
    instance: Path,
) -> tuple[dict[str, dict[str, str]], dict[str, str], list[str]]:
    """모든 JAR의 네임스페이스별 영어와 JAR 내장 한국어를 읽는다."""
    english: dict[str, dict[str, str]] = {}
    jar_korean: dict[str, str] = {}
    errors: list[str] = []
    for jar in sorted((instance / "mods").glob("*.jar")):
        try:
            with zipfile.ZipFile(jar) as archive:
                for name in archive.namelist():
                    match = LANG_RE.search(name)
                    if not match:
                        continue
                    try:
                        data = json.loads(archive.read(name).decode("utf-8-sig"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as error:
                        errors.append(f"{jar.name}:{name}: {error}")
                        continue
                    strings = {k: v for k, v in data.items() if isinstance(v, str)}
                    if match.group(2) == "en_us":
                        english.setdefault(match.group(1), {}).update(strings)
                    else:
                        for key, value in strings.items():
                            jar_korean.setdefault(key, value)
        except zipfile.BadZipFile as error:
            errors.append(f"{jar.name}: {error}")
    return english, jar_korean, errors


def pair_lines(
    korean: dict, english: dict, fallback: dict[str, tuple[str, str]]
) -> list[str]:
    """키마다 영어 출처·영어·현재 한국어를 JSON 문자열 표기로 적는다."""
    lines = []
    for key, value in korean.items():
        if key in english:
            source, text = "JAR", english[key]
        elif key in fallback:
            source, text = f"다른 JAR({fallback[key][0]})", fallback[key][1]
        else:
            source, text = "영어 원문 없음", None
        lines.append(
            f"{key}\n  EN[{source}]: {json.dumps(text, ensure_ascii=False)}\n"
            f"  KO: {json.dumps(value, ensure_ascii=False)}"
        )
    return lines


def build_pairs(family: str, instance: Path) -> list[str]:
    """계열 범위의 언어·퀘스트 대조 파일을 만들고 오류 목록을 돌려준다."""
    scope = json.loads(
        (REREVIEW_ROOT / family / "scope.json").read_text(encoding="utf-8")
    )
    target = KIT_ROOT / family
    target.mkdir(parents=True, exist_ok=True)
    english, _, errors = jar_languages(instance)
    fallback: dict[str, tuple[str, str]] = {}
    for namespace, strings in english.items():
        for key, value in strings.items():
            fallback.setdefault(key, (namespace, value))
    assets = active_output_root() / PACK_ASSETS
    for namespace in scope.get("language_namespaces", []):
        path = assets / namespace / "lang/ko_kr.json"
        korean = json.loads(path.read_text(encoding="utf-8"))
        lines = pair_lines(korean, english.get(namespace, {}), fallback)
        (target / f"{namespace}.txt").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
        print(f"{namespace}: {len(korean)}키")
    english_files = {
        relative.removesuffix("_merged"): path
        for relative, path in split_locale_files(instance, "en_us").items()
    }
    for relative in scope.get("quest_files", []):
        if relative not in english_files:
            errors.append(f"영어 퀘스트 파일 없음: {relative}")
            continue
        korean = parse_language_snbt(OUTPUT_SPLIT_ROOT / relative)
        quest_english = parse_language_snbt(english_files[relative])
        lines = pair_lines(korean, quest_english, {})
        name = relative.replace("/", "__").removesuffix(".snbt") + ".txt"
        (target / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{relative}: {len(korean)}키")
    return errors


def build_index(instance: Path) -> list[str]:
    """아이템·블록·엔티티 등의 영어 이름으로 확정 한국어 이름을 찾는 색인을 만든다."""
    english, jar_korean, errors = jar_languages(instance)
    flat: dict[str, str] = {}
    for strings in english.values():
        for key, value in strings.items():
            flat.setdefault(key, value)
    for path in (instance / "kubejs/assets").glob("*/lang/en_us.json"):
        for key, value in json.loads(path.read_text(encoding="utf-8-sig")).items():
            if isinstance(value, str):
                flat.setdefault(key, value)
    project: dict[str, str] = {}
    for path in (active_output_root() / PACK_ASSETS).glob("*/lang/ko_kr.json"):
        project.update(json.loads(path.read_text(encoding="utf-8")))
    index: dict[str, list[list[str | None]]] = {}
    for key, value in flat.items():
        if key.startswith(NAME_PREFIXES):
            korean = project.get(key) or jar_korean.get(key)
            index.setdefault(value.lower(), []).append([key, korean])
    KIT_ROOT.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    print(f"이름 {len(index)}개")
    return errors


def lookup(names: list[str]) -> None:
    """정확히 같은 영어 이름을 먼저 찾고, 없으면 부분 일치를 최대 6개 보여 준다."""
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    for name in names:
        query = name.lower()
        hits = index.get(query)
        if hits is None:
            hits = [
                hit for text, found in index.items() if query in text for hit in found
            ]
        shown = "; ".join(f"{key}={korean}" for key, korean in (hits or [])[:6])
        print(f"{name} => {shown}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("pairs").add_argument("family")
    commands.add_parser("index")
    commands.add_parser("lookup").add_argument("names", nargs="+")
    args = parser.parse_args()

    if args.command == "lookup":
        lookup(args.names)
        return 0
    instance = resolve_source_root(args.instance)
    if args.command == "pairs":
        errors = build_pairs(args.family, instance)
    else:
        errors = build_index(instance)
    for error in errors:
        print(f"처리하지 못함: {error}")
    return 1 if any(error.startswith("영어 퀘스트") for error in errors) else 0


if __name__ == "__main__":
    raise SystemExit(main())
