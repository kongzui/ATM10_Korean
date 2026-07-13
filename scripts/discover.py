#!/usr/bin/env python3
"""ATM10 인스턴스를 읽기 전용으로 조사하고 번역 매니페스트를 만든다."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from local_paths import resolve_source_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "manifests"
LANG_ENTRY_RE = re.compile(r"^assets/([^/]+)/lang/(en_us|ko_kr)\.json$", re.IGNORECASE)
SNBT_KEY_RE = re.compile(r'^\s*(?P<key>[A-Za-z0-9_.-]+|"(?:[^"\\]|\\.)*")\s*:')
VISIBLE_TEXT_MARKERS = (
    ("display_name", re.compile(r"\.displayName\s*\(")),
    ("text_component", re.compile(r"Text\.(?:of|red|green|yellow|blue|white|gold|translatable)\s*\(")),
    ("ui_message", re.compile(r"(?:setStatusMessage|statusMessage|\.tell|\.respond|setTitle|setSubtitle)\s*(?:=|\()")),
    ("tooltip", re.compile(r"tooltip|modifyTooltips", re.IGNORECASE)),
    ("ponder", re.compile(r"(?:Ponder|\.text\s*\()", re.IGNORECASE)),
)
STRING_WITH_LETTERS_RE = re.compile(r"(['\"])(?:(?!\1).)*[A-Za-z]{2}(?:(?!\1).)*\1")


def project_output(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError(f"출력 경로는 프로젝트 안이어야 합니다: {resolved}") from exc
    return resolved


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def decode_json(raw: bytes) -> tuple[dict[str, Any] | None, str]:
    try:
        value = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(value, dict):
            return None, "JSON 최상위 값이 객체가 아님"
        return value, ""
    except Exception as exc:  # 오류 JAR/파일도 반드시 매니페스트에 기록한다.
        return None, f"{type(exc).__name__}: {exc}"


def scan_jars(mods: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, set[str]]]:
    jars = sorted(mods.glob("*.jar"), key=lambda p: p.name.lower())
    inventory: list[dict[str, Any]] = []
    language_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    en_keys_by_namespace: dict[str, set[str]] = defaultdict(set)

    for jar in jars:
        groups: dict[str, dict[str, list[str]]] = defaultdict(lambda: {"en_us": [], "ko_kr": []})
        jar_status = "ok"
        jar_error = ""
        try:
            with zipfile.ZipFile(jar) as archive:
                for entry in archive.namelist():
                    match = LANG_ENTRY_RE.match(entry)
                    if match:
                        groups[match.group(1).lower()][match.group(2).lower()].append(entry)

                for namespace in sorted(groups):
                    locale_data: dict[str, tuple[int | str, set[str]]] = {}
                    for locale in ("en_us", "ko_kr"):
                        paths = sorted(groups[namespace][locale])
                        keys: set[str] = set()
                        state = "missing"
                        error_text = ""
                        if paths:
                            state = "ok"
                            for entry in paths:
                                parsed, error = decode_json(archive.read(entry))
                                if error:
                                    state = "error"
                                    error_text = (error_text + " | " + f"{entry}: {error}").strip(" |")
                                    errors.append({"source_type": "jar_json", "source": jar.name, "entry": entry, "error": error})
                                elif parsed is not None:
                                    keys.update(parsed.keys())
                        locale_data[locale] = (state, keys)
                        locale_data[f"{locale}_paths"] = (";".join(paths), set())
                        locale_data[f"{locale}_error"] = (error_text, set())

                    en_state, en_keys = locale_data["en_us"]
                    ko_state, ko_keys = locale_data["ko_kr"]
                    en_keys_by_namespace[namespace].update(en_keys)
                    language_rows.append(
                        {
                            "jar": jar.name,
                            "namespace": namespace,
                            "en_path": locale_data["en_us_paths"][0],
                            "ko_path": locale_data["ko_kr_paths"][0],
                            "en_status": en_state,
                            "ko_status": ko_state,
                            "en_keys": len(en_keys),
                            "ko_keys": len(ko_keys),
                            "shared_keys": len(en_keys & ko_keys),
                            "missing_in_ko": len(en_keys - ko_keys),
                            "ko_only_keys": len(ko_keys - en_keys),
                            "error": " | ".join(filter(None, (locale_data["en_us_error"][0], locale_data["ko_kr_error"][0]))),
                        }
                    )
        except Exception as exc:
            jar_status = "error"
            jar_error = f"{type(exc).__name__}: {exc}"
            errors.append({"source_type": "jar", "source": jar.name, "entry": "", "error": jar_error})

        has_en = any(group["en_us"] for group in groups.values())
        has_ko = any(group["ko_kr"] for group in groups.values())
        inventory.append(
            {
                "jar": jar.name,
                "bytes": jar.stat().st_size,
                "status": jar_status,
                "namespaces": ";".join(sorted(groups)),
                "namespace_count": len(groups),
                "has_en_us": has_en,
                "has_ko_kr": has_ko,
                "classification": "en_and_ko" if has_en and has_ko else "en_only" if has_en else "ko_only" if has_ko else "no_target_language_file",
                "error": jar_error,
            }
        )

    summary = {
        "jar_files": len(jars),
        "jar_scan_errors": sum(row["status"] == "error" for row in inventory),
        "language_json_errors": sum(error["source_type"] == "jar_json" for error in errors),
        "jars_with_en_us": sum(bool(row["has_en_us"]) for row in inventory),
        "jars_with_ko_kr": sum(bool(row["has_ko_kr"]) for row in inventory),
        "jars_with_en_and_ko": sum(bool(row["has_en_us"] and row["has_ko_kr"]) for row in inventory),
        "jars_with_en_without_ko": sum(bool(row["has_en_us"] and not row["has_ko_kr"]) for row in inventory),
        "namespaces_with_en_us": sum(row["en_status"] != "missing" for row in language_rows),
        "namespaces_with_ko_kr": sum(row["ko_status"] != "missing" for row in language_rows),
        "namespace_en_keys": sum(int(row["en_keys"]) for row in language_rows),
        "namespace_ko_keys": sum(int(row["ko_keys"]) for row in language_rows),
    }
    return inventory, language_rows, errors, summary, dict(en_keys_by_namespace)


def snbt_keys(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    keys = set()
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        match = SNBT_KEY_RE.match(line)
        if match:
            keys.add(match.group("key"))
    return keys


def scan_ftbquests(instance: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    root = instance / "config" / "ftbquests"
    quest_root = root / "quests"
    lang_root = quest_root / "lang"
    en_path = lang_root / "en_us.snbt"
    ko_path = lang_root / "ko_kr.snbt"
    en_keys = snbt_keys(en_path)
    ko_keys = snbt_keys(ko_path)
    merged = list(lang_root.rglob("*.snbt_merged")) if lang_root.is_dir() else []
    chapter_rows: list[dict[str, Any]] = []
    en_chapter_root = lang_root / "en_us" / "chapters"
    ko_chapter_root = lang_root / "ko_kr" / "chapters"
    if en_chapter_root.is_dir():
        for en_chapter in sorted(en_chapter_root.glob("*.snbt_merged"), key=lambda path: path.name.lower()):
            ko_chapter = ko_chapter_root / en_chapter.name
            chapter_en_keys = snbt_keys(en_chapter)
            chapter_ko_keys = snbt_keys(ko_chapter)
            chapter_rows.append(
                {
                    "chapter": en_chapter.name.removesuffix(".snbt_merged"),
                    "en_path": en_chapter.relative_to(instance).as_posix(),
                    "ko_path": ko_chapter.relative_to(instance).as_posix(),
                    "ko_exists": ko_chapter.is_file(),
                    "en_estimated_keys": len(chapter_en_keys),
                    "ko_estimated_keys": len(chapter_ko_keys),
                    "shared_estimated_keys": len(chapter_en_keys & chapter_ko_keys),
                    "missing_in_ko_estimated": len(chapter_en_keys - chapter_ko_keys),
                    "ko_only_estimated": len(chapter_ko_keys - chapter_en_keys),
                }
            )
    summary = {
        "root": str(root.relative_to(instance).as_posix()),
        "all_files": sum(1 for path in root.rglob("*") if path.is_file()) if root.is_dir() else 0,
        "snbt_files": sum(1 for path in root.rglob("*.snbt") if path.is_file()) if root.is_dir() else 0,
        "chapter_files": sum(1 for path in (quest_root / "chapters").glob("*.snbt")) if (quest_root / "chapters").is_dir() else 0,
        "en_us_path": str(en_path.relative_to(instance).as_posix()),
        "ko_kr_path": str(ko_path.relative_to(instance).as_posix()),
        "en_us_exists": en_path.is_file(),
        "ko_kr_exists": ko_path.is_file(),
        "en_us_estimated_keys": len(en_keys),
        "ko_kr_estimated_keys": len(ko_keys),
        "shared_estimated_keys": len(en_keys & ko_keys),
        "missing_in_ko_estimated": len(en_keys - ko_keys),
        "ko_only_estimated": len(ko_keys - en_keys),
        "key_count_method": "최상위 '키: 값' 행 정규식 집계; 정식 SNBT 파서 결과가 아니므로 추정치",
        "merged_localization_files": len(merged),
        "chapter_manifest_rows": len(chapter_rows),
    }
    return summary, chapter_rows


def scan_kubejs(instance: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    root = instance / "kubejs"
    language_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for path in sorted(root.glob("assets/*/lang/*.json"), key=lambda p: p.as_posix().lower()):
        parsed, error = decode_json(path.read_bytes())
        relative = path.relative_to(instance).as_posix()
        if error:
            errors.append({"source_type": "kubejs_json", "source": relative, "entry": "", "error": error})
        language_rows.append(
            {
                "path": relative,
                "namespace": path.parents[1].name,
                "locale": path.stem.lower(),
                "keys": len(parsed) if parsed is not None else 0,
                "status": "error" if error else "ok",
                "error": error,
            }
        )

    candidate_rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.js"), key=lambda p: p.as_posix().lower()):
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except Exception as exc:
            errors.append({"source_type": "kubejs_js", "source": path.relative_to(instance).as_posix(), "entry": "", "error": f"{type(exc).__name__}: {exc}"})
            continue
        for number, line in enumerate(lines, 1):
            if not STRING_WITH_LETTERS_RE.search(line):
                continue
            categories = [name for name, pattern in VISIBLE_TEXT_MARKERS if pattern.search(line)]
            if categories:
                candidate_rows.append(
                    {
                        "path": path.relative_to(instance).as_posix(),
                        "line": number,
                        "category": ";".join(categories),
                        "comment_like": line.lstrip().startswith(("//", "/*", "*")),
                        "excerpt": line.strip()[:300],
                    }
                )

    en_rows = [row for row in language_rows if row["locale"] == "en_us"]
    ko_rows = [row for row in language_rows if row["locale"] == "ko_kr"]
    summary = {
        "all_files": sum(1 for path in root.rglob("*") if path.is_file()) if root.is_dir() else 0,
        "js_files": sum(1 for path in root.rglob("*.js") if path.is_file()) if root.is_dir() else 0,
        "language_json_files": len(language_rows),
        "en_us_files": len(en_rows),
        "ko_kr_files": len(ko_rows),
        "en_us_keys": sum(int(row["keys"]) for row in en_rows if row["status"] == "ok"),
        "ko_kr_keys": sum(int(row["keys"]) for row in ko_rows if row["status"] == "ok"),
        "user_visible_candidate_lines": len(candidate_rows),
        "candidate_note": "문자열 패턴 기반 후보이며 실제 표시 여부는 수동 확인 필요",
    }
    return language_rows, candidate_rows, errors, summary


def pack_meta(archive: zipfile.ZipFile) -> tuple[str, str]:
    names = {name.lower(): name for name in archive.namelist()}
    entry = names.get("pack.mcmeta")
    if not entry:
        return "", ""
    parsed, error = decode_json(archive.read(entry))
    if error or parsed is None:
        raise ValueError(f"pack.mcmeta: {error}")
    pack = parsed.get("pack", {})
    return str(pack.get("pack_format", "")), json.dumps(pack.get("description", ""), ensure_ascii=False)


def scan_resourcepacks(instance: Path, current_en: dict[str, set[str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    root = instance / "resourcepacks"
    rows: list[dict[str, Any]] = []
    overlap_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for path in sorted(root.iterdir(), key=lambda p: p.name.lower()) if root.is_dir() else []:
        row = {"candidate": path.name, "kind": "directory" if path.is_dir() else "file", "bytes": path.stat().st_size, "pack_format": "", "description": "", "language_files": 0, "ko_kr_files": 0, "ko_kr_keys": 0, "overlap_namespaces": 0, "shared_key_candidates": 0, "status": "ok", "error": ""}
        try:
            if path.is_file() and zipfile.is_zipfile(path):
                row["kind"] = "zip"
                with zipfile.ZipFile(path) as archive:
                    row["pack_format"], row["description"] = pack_meta(archive)
                    for entry in archive.namelist():
                        normalized = PurePosixPath(entry.lower())
                        if len(normalized.parts) >= 4 and normalized.parts[-2] == "lang" and normalized.suffix == ".json":
                            row["language_files"] += 1
                            if normalized.name == "ko_kr.json":
                                row["ko_kr_files"] += 1
                                parsed, error = decode_json(archive.read(entry))
                                if error:
                                    raise ValueError(f"{entry}: {error}")
                                row["ko_kr_keys"] += len(parsed or {})
                                namespace = normalized.parts[-3]
                                legacy_keys = set((parsed or {}).keys())
                                current_keys = current_en.get(namespace, set())
                                shared = current_keys & legacy_keys
                                if current_keys:
                                    row["overlap_namespaces"] += 1
                                    row["shared_key_candidates"] += len(shared)
                                overlap_rows.append(
                                    {
                                        "candidate": path.name,
                                        "namespace": namespace,
                                        "current_en_keys": len(current_keys),
                                        "legacy_ko_keys": len(legacy_keys),
                                        "shared_key_candidates": len(shared),
                                        "missing_in_legacy": len(current_keys - legacy_keys),
                                        "legacy_only_keys": len(legacy_keys - current_keys),
                                        "current_key_coverage_percent": f"{(len(shared) / len(current_keys) * 100):.2f}" if current_keys else "",
                                        "note": "키 교집합만 계산; 번역 품질과 원문 동일성은 검증하지 않음",
                                    }
                                )
            elif path.is_dir():
                language_files = list(path.glob("assets/*/lang/*.json"))
                row["language_files"] = len(language_files)
                for language_file in language_files:
                    if language_file.name.lower() == "ko_kr.json":
                        row["ko_kr_files"] += 1
                        parsed, error = decode_json(language_file.read_bytes())
                        if error:
                            raise ValueError(f"{language_file}: {error}")
                        row["ko_kr_keys"] += len(parsed or {})
            else:
                row["status"] = "not_zip_or_directory"
        except Exception as exc:
            row["status"] = "error"
            row["error"] = f"{type(exc).__name__}: {exc}"
            errors.append({"source_type": "resourcepack", "source": path.name, "entry": "", "error": row["error"]})
        rows.append(row)
    overlapping = [row for row in overlap_rows if int(row["current_en_keys"]) > 0]
    summary = {
        "candidates": len(rows),
        "candidate_names": [row["candidate"] for row in rows],
        "overlap_namespaces": len(overlapping),
        "shared_key_candidates": sum(int(row["shared_key_candidates"]) for row in overlapping),
        "current_en_keys_in_overlap_namespaces": sum(int(row["current_en_keys"]) for row in overlapping),
        "legacy_ko_keys_in_overlap_namespaces": sum(int(row["legacy_ko_keys"]) for row in overlapping),
        "missing_in_legacy": sum(int(row["missing_in_legacy"]) for row in overlapping),
        "legacy_only_keys": sum(int(row["legacy_only_keys"]) for row in overlapping),
        "reuse_warning": "공유 키는 재사용 검토 후보일 뿐이며 5.4 번역 품질과 7.1 원문 동일성은 아직 검증하지 않음",
    }
    return rows, overlap_rows, errors, summary


def scan_other_candidates(instance: Path) -> list[dict[str, Any]]:
    roots = ("config", "defaultconfigs", "patchouli_books", "datapacks", "blueprints", "fancymenu_data")
    rows = []
    for name in roots:
        root = instance / name
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or "ftbquests" in {part.lower() for part in path.parts}:
                continue
            relative = path.relative_to(instance).as_posix()
            lowered = relative.lower()
            if re.search(r"(?:^|/)(?:en_us|ko_kr)(?:\.|/)", lowered) or "/lang/" in lowered or re.search(r"(?:language|localization|translation)", path.name, re.IGNORECASE):
                rows.append({"path": relative, "bytes": path.stat().st_size, "reason": "이름 또는 경로가 언어/현지화 패턴과 일치"})
    return sorted(rows, key=lambda row: row["path"].lower())


def read_pack_version(instance: Path) -> dict[str, Any]:
    path = instance / "manifest.json"
    if not path.is_file():
        return {"name": "", "version": "", "minecraft": "", "manifest_file_entries": 0, "error": "manifest.json 없음"}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        minecraft = data.get("minecraft", {})
        return {"name": data.get("name", ""), "version": data.get("version", ""), "minecraft": minecraft.get("version", ""), "manifest_file_entries": len(data.get("files", [])), "error": ""}
    except Exception as exc:
        return {"name": "", "version": "", "minecraft": "", "manifest_file_entries": 0, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    instance = resolve_source_root(args.instance)
    if not instance.is_dir():
        parser.error(f"인스턴스 경로에 접근할 수 없습니다: {instance}")
    for required in ("mods", "config/ftbquests", "kubejs", "resourcepacks"):
        if not (instance / required).is_dir():
            parser.error(f"필수 조사 경로가 없습니다: {instance / required}")
    output = project_output(args.output)
    output.mkdir(parents=True, exist_ok=True)

    inventory, jar_langs, errors, jar_summary, current_en = scan_jars(instance / "mods")
    ftb_summary, ftb_chapters = scan_ftbquests(instance)
    kube_langs, kube_candidates, kube_errors, kube_summary = scan_kubejs(instance)
    resourcepacks, legacy_overlap, pack_errors, pack_summary = scan_resourcepacks(instance, current_en)
    other_candidates = scan_other_candidates(instance)
    errors.extend(kube_errors)
    errors.extend(pack_errors)

    write_csv(output / "jar_inventory.csv", ["jar", "bytes", "status", "namespaces", "namespace_count", "has_en_us", "has_ko_kr", "classification", "error"], inventory)
    write_csv(output / "jar_language_files.csv", ["jar", "namespace", "en_path", "ko_path", "en_status", "ko_status", "en_keys", "ko_keys", "shared_keys", "missing_in_ko", "ko_only_keys", "error"], jar_langs)
    write_csv(output / "ftbquest_chapters.csv", ["chapter", "en_path", "ko_path", "ko_exists", "en_estimated_keys", "ko_estimated_keys", "shared_estimated_keys", "missing_in_ko_estimated", "ko_only_estimated"], ftb_chapters)
    write_csv(output / "kubejs_languages.csv", ["path", "namespace", "locale", "keys", "status", "error"], kube_langs)
    write_csv(output / "kubejs_text_candidates.csv", ["path", "line", "category", "comment_like", "excerpt"], kube_candidates)
    write_csv(output / "resourcepack_candidates.csv", ["candidate", "kind", "bytes", "pack_format", "description", "language_files", "ko_kr_files", "ko_kr_keys", "overlap_namespaces", "shared_key_candidates", "status", "error"], resourcepacks)
    write_csv(output / "legacy_resourcepack_overlap.csv", ["candidate", "namespace", "current_en_keys", "legacy_ko_keys", "shared_key_candidates", "missing_in_legacy", "legacy_only_keys", "current_key_coverage_percent", "note"], legacy_overlap)
    write_csv(output / "other_translation_candidates.csv", ["path", "bytes", "reason"], other_candidates)
    write_csv(output / "errors.csv", ["source_type", "source", "entry", "error"], errors)

    summary = {
        "instance": str(instance),
        "pack": read_pack_version(instance),
        "jars": jar_summary,
        "ftbquests": ftb_summary,
        "kubejs": kube_summary,
        "resourcepacks": pack_summary,
        "other_translation_candidates": len(other_candidates),
        "recorded_errors": len(errors),
        "notes": [
            "원본 파일은 읽기만 했으며 JAR과 리소스팩을 추출하거나 수정하지 않음",
            "FTB Quests 키 수는 정규식 기반 추정치",
            "KubeJS 표시 문구는 패턴 기반 후보이므로 수동 확인 필요",
        ],
    }
    (output / "discovery_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not any(error["source_type"] == "jar" for error in errors) else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        raise SystemExit(1)
