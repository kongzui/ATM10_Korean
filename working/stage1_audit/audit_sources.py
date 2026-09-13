"""단계 0 원문 기준과 단계 1 정적 표시 경로를 읽기 전용으로 조사해요."""

import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
DEST = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_ae2_quests import parse_language_snbt  # noqa: E402
from ftbquests_layout import split_locale_files  # noqa: E402
from local_paths import resolve_source_root  # noqa: E402
from rebase_ftbquests import load_split, value_hash  # noqa: E402
from snapshot_instance import collect  # noqa: E402
from verify_compat_release import SnbtReader  # noqa: E402


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, data):
    (DEST / name).write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strings(value, pointer=""):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from strings(child, f"{pointer}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from strings(child, f"{pointer}/{index}")
    elif isinstance(value, str):
        yield pointer, value


def changes(old, new, pointer=""):
    if isinstance(old, dict) and isinstance(new, dict):
        for key in sorted(old.keys() | new.keys()):
            yield from changes(old.get(key), new.get(key), f"{pointer}/{key}")
    elif isinstance(old, list) and isinstance(new, list):
        # ID가 있는 목록은 순서 변경과 실제 내용 변경을 구분해요.
        if old and new and all(isinstance(x, dict) and "id" in x for x in old + new):
            a, b = {x["id"]: x for x in old}, {x["id"]: x for x in new}
            if a.keys() == b.keys():
                if list(a) != list(b):
                    yield {
                        "path": pointer,
                        "kind": "순서",
                        "old": list(a),
                        "new": list(b),
                    }
                yield from changes(a, b, pointer)
                return
        for index in range(max(len(old), len(new))):
            yield from changes(
                old[index] if index < len(old) else None,
                new[index] if index < len(new) else None,
                f"{pointer}/{index}",
            )
    elif old != new:
        kind = "기타"
        if "/images/" in pointer and pointer.endswith("/id"):
            kind = "이미지ID"
        elif pointer.endswith("/count"):
            kind = "수량"
        elif pointer.endswith(("/order", "/order_index")):
            kind = "순서"
        elif "custom_name" in pointer:
            kind = "표시문구"
        yield {"path": pointer, "kind": kind, "old": old, "new": new}


def main():
    instance = resolve_source_root(None)
    errors = []
    before = read(ROOT / "temp/stage1_before.json")
    manifest = read(instance / "manifest.json")
    metadata = read(instance / "minecraftinstance.json")
    expected = {x["projectID"]: x["fileID"] for x in manifest["files"]}
    embedded = {x["projectID"]: x["fileID"] for x in metadata["manifest"]["files"]}
    addons = {x["fileNameOnDisk"]: x for x in metadata["installedAddons"]}
    pack_paths = metadata["installedModpack"].get("filePaths", [])
    with (ROOT / "versions/8.1/manifests/jar_inventory.csv").open(
        encoding="utf-8-sig", newline=""
    ) as stream:
        baseline = {row["jar"]: row for row in csv.DictReader(stream)}
    jars = {path.name: path for path in (instance / "mods").glob("*.jar")}
    inventory = []
    for name, path in sorted(jars.items()):
        addon = addons.get(name, {})
        project = addon.get("addonID")
        file_id = addon.get("installedFile", {}).get("id")
        category = "메타데이터 없음: 개인 추가 여부 미확정"
        if project in expected:
            category = (
                "팩 지정 파일" if expected[project] == file_id else "팩 모드 버전 변경"
            )
        elif project:
            category = "팩 manifest 밖 추가 모드"
        if project not in expected and any(
            p.replace("\\", "/").endswith("/overrides/mods/" + name) for p in pack_paths
        ):
            category = "팩 overrides 제공 JAR"
        inventory.append(
            {
                "jar": name,
                "bytes": path.stat().st_size,
                "baseline_present": name in baseline,
                "baseline_bytes_equal": str(path.stat().st_size)
                == baseline.get(name, {}).get("bytes"),
                "project_id": project,
                "installed_file_id": file_id,
                "manifest_file_id": expected.get(project),
                "classification": category,
            }
        )
    pack_file = metadata["installedModpack"]["installedFile"]
    save(
        "jar_classification.json",
        {
            "instance": str(instance),
            "pack_version": manifest["version"],
            "pack_file": {k: pack_file.get(k) for k in ("id", "fileName", "hashes")},
            "manifest_matches_embedded": expected == embedded,
            "manifest_sha256": digest((instance / "manifest.json").read_bytes()),
            "baseline_count": len(baseline),
            "installed_count": len(jars),
            "added_vs_baseline": sorted(jars.keys() - baseline.keys()),
            "removed_vs_baseline": sorted(baseline.keys() - jars.keys()),
            "counts": dict(Counter(x["classification"] for x in inventory)),
            "rows": inventory,
            "limitation": "목록·크기 비교이며 전체 JAR의 과거 SHA 동일성 증명은 아니에요.",
        },
    )

    quest_root = instance / "config/ftbquests/quests"
    english, key_files = load_split(instance, "en_us")
    old_hashes = read(ROOT / "versions/8.1/manifests/ftbquests_english_hashes.json")[
        "keys"
    ]
    merged = parse_language_snbt(quest_root / "lang/en_us.snbt")
    korean = {}
    korean_files = {}
    output_lang = ROOT / "output/8.1/overrides/config/ftbquests/quests/lang/ko_kr"
    for path in sorted(output_lang.rglob("*.snbt")):
        for key, value in parse_language_snbt(path).items():
            if key in korean:
                errors.append(f"배포 한국어 중복: {key}")
            korean[key] = value
            korean_files[key] = path.relative_to(ROOT).as_posix()
    language_files = []
    for relative, path in split_locale_files(instance, "en_us").items():
        values = parse_language_snbt(path)
        normalized = relative.replace(".snbt_merged", ".snbt")
        language_files.append(
            {
                "source": path.relative_to(instance).as_posix(),
                "source_sha256": digest(path.read_bytes()),
                "canonical_relative": normalized,
                "output_exists": (output_lang / normalized).is_file(),
                "keys": len(values),
                "unchanged_baseline_keys": sum(
                    value_hash(v) == old_hashes.get(k, {}).get("sha256")
                    for k, v in values.items()
                ),
            }
        )
    prior_audit = read(ROOT / "versions/8.1/reports/current_instance_compat_audit.json")
    structure = []
    for row in read(ROOT / "working/compat_8_1/chapter_review.json"):
        path = instance / row["path"]
        target = ROOT / "output/8.1/overrides" / row["path"]
        source_data = SnbtReader(path.read_text(encoding="utf-8-sig")).parse()
        target_data = SnbtReader(target.read_text(encoding="utf-8-sig")).parse()
        delta = list(changes(target_data, source_data))
        structure.append(
            {
                "path": row["path"],
                "current_sha256": digest(path.read_bytes()),
                "reviewed_source_sha256": row["source_sha256"],
                "comparison": "기존 배포 구조 -> 실행후 현재 구조; 변경 원인을 추정하지 않아요.",
                "counts": dict(Counter(x["kind"] for x in delta)),
                "changes": delta,
            }
        )
    save(
        "english_baseline_and_compat.json",
        {
            "source_choice": "분할 영어는 이전 키별 해시와 비교하고 병합 파일은 별도 비교해요.",
            "english_keys": len(english),
            "baseline_keys": len(old_hashes),
            "changed": [
                k
                for k, v in english.items()
                if k in old_hashes and value_hash(v) != old_hashes[k]["sha256"]
            ],
            "new": sorted(english.keys() - old_hashes.keys()),
            "missing": sorted(old_hashes.keys() - english.keys()),
            "merged_keys": len(merged),
            "merged_only": {k: merged[k] for k in merged.keys() - english.keys()},
            "split_only": {k: english[k] for k in english.keys() - merged.keys()},
            "merged_changed": {
                k: {"split": english[k], "merged": merged[k]}
                for k in english.keys() & merged.keys()
                if english[k] != merged[k]
            },
            "files": language_files,
            "prior_errors_by_prefix": dict(
                Counter(e.split(":")[0] for e in prior_audit["errors"])
            ),
            "chapter_structure": structure,
            "game_screen_validation": "not_run; 정적 표시 경로 조사",
        },
    )

    chapters = []
    for path in sorted((quest_root / "chapters").glob("*.snbt")):
        try:
            chapters.append(
                (path, SnbtReader(path.read_text(encoding="utf-8-sig")).parse())
            )
        except Exception as exc:
            errors.append(f"{path}: {exc}")
    for mod, chapter_name in (("auroral", "auroral"), ("neovitae", "neo_vitae")):
        search_pattern = rf"{mod}|{chapter_name}"
        if mod == "neovitae":
            search_pattern += r"|Neo Vitae"
        jar = next(path for name, path in jars.items() if name.startswith(mod + "-"))
        with ZipFile(jar) as archive:
            lang_member = f"assets/{mod}/lang/en_us.json"
            lang = json.loads(archive.read(lang_member))
            guide = []
            for member in archive.namelist():
                if member.endswith((".md", ".mdx")) or (
                    "/modonomicon/books/" in member and member.endswith(".json")
                ):
                    data = archive.read(member)
                    text = data.decode("utf-8-sig")
                    references = []
                    literals = []
                    if member.endswith(".json"):
                        for pointer, value in strings(json.loads(text)):
                            if value in lang or value.startswith(f"book.{mod}."):
                                references.append(
                                    {
                                        "pointer": pointer,
                                        "key": value,
                                        "english": lang.get(value),
                                    }
                                )
                            elif (
                                pointer.split("/")[-1]
                                in {"text", "title", "name", "description", "tooltip"}
                                and value
                            ):
                                literals.append({"pointer": pointer, "value": value})
                    guide.append(
                        {
                            "member": member,
                            "sha256": digest(data),
                            "language_references": references,
                            "visible_non_language_candidates": literals,
                            "english_markdown": text
                            if member.endswith((".md", ".mdx"))
                            else None,
                        }
                    )
            save(
                f"{mod}_guide_sources.json",
                {
                    "jar": jar.name,
                    "jar_sha256": digest(jar.read_bytes()),
                    "language_member": lang_member,
                    "language_sha256": digest(archive.read(lang_member)),
                    "language_keys": len(lang),
                    "guide_files": len(guide),
                    "unique_guide_language_keys": len(
                        {x["key"] for row in guide for x in row["language_references"]}
                    ),
                    "files": guide,
                },
            )
        scope = []
        for path, chapter in chapters:
            for quest in chapter.get("quests", []):
                qid = quest["id"]
                text = json.dumps(quest, ensure_ascii=False)
                quest_keys = [k for k in english if k.startswith(f"quest.{qid}.")]
                searchable = text + " " + json.dumps([english[k] for k in quest_keys])
                dedicated = path.stem == chapter_name
                if not dedicated and not re.search(search_pattern, searchable, re.I):
                    continue
                tasks = []
                for task in quest.get("tasks", []):
                    tid = task["id"]
                    item = task.get("item", {})
                    item_id = (
                        item.get("id", "") if isinstance(item, dict) else str(item)
                    )
                    item_keys = [
                        f"{prefix}.{item_id.replace(':', '.')}"
                        for prefix in ("item", "block")
                        if f"{prefix}.{item_id.replace(':', '.')}" in lang
                    ]
                    tasks.append(
                        {
                            "id": tid,
                            "type": task.get("type"),
                            "source": task,
                            "title_key": f"task.{tid}.title",
                            "english_title": english.get(f"task.{tid}.title"),
                            "korean_title": korean.get(f"task.{tid}.title"),
                            "item_id": item_id,
                            "item_language_keys": item_keys,
                            "item_english_names": {k: lang[k] for k in item_keys},
                            "custom_components": item.get("components", {})
                            if isinstance(item, dict)
                            else {},
                        }
                    )
                ids = [qid] + [t["id"] for t in tasks]
                related_keys = [
                    k
                    for k in english.keys() | korean.keys()
                    if any(
                        k.startswith(f"{kind}.{identifier}.")
                        for identifier in ids
                        for kind in ("quest", "task")
                    )
                ]
                scope.append(
                    {
                        "chapter": path.name,
                        "chapter_id": chapter["id"],
                        "group_id": chapter.get("group"),
                        "dedicated_chapter": dedicated,
                        "quest_id": qid,
                        "quest_source": quest,
                        "tasks": tasks,
                        "title_path": "명시적 한국어 quest.title"
                        if f"quest.{qid}.title" in korean
                        else "첫 Task fallback; Task 제목 -> custom_name/아이템 이름 확인",
                        "language": {
                            k: {
                                "english": english.get(k),
                                "korean": korean.get(k),
                                "english_file": key_files.get(k),
                                "korean_file": korean_files.get(k),
                                "baseline_hash_matches": k in english
                                and value_hash(english[k])
                                == old_hashes.get(k, {}).get("sha256"),
                            }
                            for k in sorted(related_keys)
                        },
                    }
                )
        search_hits = []
        for folder in ("kubejs", "patchouli_books", "datapacks", "config/ftbquests"):
            for path in sorted((instance / folder).rglob("*")):
                if not path.is_file() or path.suffix not in {
                    ".js",
                    ".json",
                    ".md",
                    ".snbt",
                }:
                    continue
                # 다른 locale의 중복 검색은 표시 경로 수에 포함하지 않아요.
                if folder == "config/ftbquests" and "/lang/" in path.as_posix():
                    continue
                try:
                    content = path.read_text(encoding="utf-8-sig")
                    hits = [
                        {"line": number, "text": line.strip()}
                        for number, line in enumerate(content.splitlines(), 1)
                        if re.search(search_pattern, line, re.I)
                    ]
                    if hits:
                        search_hits.append(
                            {
                                "file": path.relative_to(instance).as_posix(),
                                "sha256": digest(path.read_bytes()),
                                "matches": hits,
                            }
                        )
                except Exception as exc:
                    errors.append(f"{path}: {exc}")
        save(
            f"{mod}_quest_and_kubejs_paths.json",
            {
                "jar": jar.name,
                "quest_count": len(scope),
                "task_count": sum(len(q["tasks"]) for q in scope),
                "chapters": dict(Counter(q["chapter"] for q in scope)),
                "navigation": {
                    k: {"english": english.get(k), "korean": korean.get(k)}
                    for q in scope
                    for k in (
                        f"chapter.{q['chapter_id']}.title",
                        f"chapter_group.{q['group_id']}.title",
                    )
                },
                "quests": scope,
                "text_search_hits": search_hits,
                "game_screen_validation": "not_run; 정적 표시 경로 조사",
                "limitation": "fallback은 언어·Task 구조에서 추적한 경로이며 화면 검증이 아니에요.",
            },
        )
    after = collect(instance)
    save(
        "safety_and_errors.json",
        {
            "snapshot_equal": before == after,
            "tracked_files": sum(len(rows) for rows in after["files"].values()),
            "errors": errors,
            "writes": "working/stage1_audit/*.json 및 조사 스크립트만",
            "game_screen_validation": "not_run",
        },
    )
    print(
        json.dumps(
            {"snapshot_equal": before == after, "errors": errors}, ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
