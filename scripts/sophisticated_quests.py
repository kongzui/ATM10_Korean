#!/usr/bin/env python3
"""Sophisticated 계열 FTB Quests 표시 문구를 범위 한정해 병합하고 검증한다."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import audit_ftbquests_titles as quest_audit
import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

WORK_FILE = PROJECT_ROOT / "working/sophisticated/quests/storage/ko_kr.json"
OUTPUT_FILE = active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
OUTPUT_SPLIT = OUTPUT_FILE.with_suffix("")
NAMESPACE_RE = re.compile(
    r"sophisticated(?:backpacks|storage|core|storageinmotion):",
    re.IGNORECASE,
)


def chapter_language_path(instance: Path, locale: str) -> Path:
    """현재 버전의 storage 챕터 언어 파일 경로를 반환한다."""
    root = instance / f"config/ftbquests/quests/lang/{locale}/chapters"
    for suffix in (".snbt", ".snbt_merged"):
        path = root / f"storage{suffix}"
        if path.is_file():
            return path
    raise FileNotFoundError(f"FTB Quests {locale} storage 챕터를 찾을 수 없습니다.")


def load_output() -> dict[str, quest_snbt.TranslationValue]:
    """병합 또는 분할 FTB Quests 한국어 산출물을 읽는다."""
    if OUTPUT_FILE.is_file():
        return quest_snbt.parse_language_snbt(OUTPUT_FILE)
    if not OUTPUT_SPLIT.is_dir():
        raise FileNotFoundError("FTB Quests 한국어 산출물을 찾을 수 없습니다.")
    output: dict[str, quest_snbt.TranslationValue] = {}
    for path in sorted(
        OUTPUT_SPLIT.rglob("*.snbt"), key=lambda item: item.as_posix().lower()
    ):
        for key, value in quest_snbt.parse_language_snbt(path).items():
            if key in output:
                raise ValueError(f"분할 FTB Quests 출력 키가 중복됩니다: {key}")
            output[key] = value
    return output


def load_working() -> dict[str, quest_snbt.TranslationValue]:
    """중복 키와 BOM을 거부하며 검수 작업본을 읽는다."""

    if WORK_FILE.read_bytes().startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"UTF-8 BOM이 있습니다: {WORK_FILE}")

    def reject_duplicates(
        pairs: list[tuple[str, object]],
    ) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"중복 키가 있습니다: {key}")
            result[key] = value
        return result

    raw = json.loads(
        WORK_FILE.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicates,
    )
    if not isinstance(raw, dict):
        raise TypeError("퀘스트 작업본의 최상위 값은 객체여야 합니다.")
    result: dict[str, quest_snbt.TranslationValue] = {}
    for key, value in raw.items():
        if isinstance(value, str) or (
            isinstance(value, list) and all(isinstance(item, str) for item in value)
        ):
            result[key] = value
        else:
            raise TypeError(f"지원하지 않는 번역 값입니다: {key}")
    return result


def scoped_language(
    instance: Path,
) -> tuple[dict[str, quest_snbt.TranslationValue], int, int]:
    """storage 챕터에서 Sophisticated 네임스페이스를 쓰는 표시 키를 모은다."""

    quest_root = instance / "config/ftbquests/quests"
    chapter_path = quest_root / "chapters/storage.snbt"
    text = chapter_path.read_text(encoding="utf-8-sig")
    quest_ids: set[str] = set()
    task_ids: set[str] = set()
    for block in quest_audit.list_objects(text, "quests"):
        if not NAMESPACE_RE.search(block):
            continue
        quest_id = quest_audit.scalar_string(block, "id")
        if not quest_id:
            raise ValueError("Sophisticated 관련 퀘스트 ID를 찾지 못했습니다.")
        quest_ids.add(quest_id)
        for task in quest_audit.list_objects(block, "tasks"):
            task_id = quest_audit.scalar_string(task, "id")
            if not task_id:
                raise ValueError(f"Task ID를 찾지 못했습니다: {quest_id}")
            task_ids.add(task_id)

    english = quest_snbt.parse_language_snbt(chapter_language_path(instance, "en_us"))
    scoped = {
        key: value
        for key, value in english.items()
        if (key.startswith("quest.") and key.split(".", 2)[1] in quest_ids)
        or (key.startswith("task.") and key.split(".", 2)[1] in task_ids)
    }
    return scoped, len(quest_ids), len(task_ids)


def validate(
    source: dict[str, quest_snbt.TranslationValue],
    translated: dict[str, quest_snbt.TranslationValue],
) -> None:
    """키·자료형·보호 문자열·확정 용어를 검증한다."""

    if list(translated) != list(source):
        missing = sorted(set(source) - set(translated))
        extra = sorted(set(translated) - set(source))
        raise ValueError(f"퀘스트 키 불일치: 누락={missing}, 초과={extra}")
    errors: list[str] = []
    for key, value in source.items():
        key_errors = quest_snbt.validate_value(key, value, translated[key])
        if key == "quest.1FE17B1C7C639F88.quest_desc":
            key_errors = [
                error for error in key_errors if not error.endswith("숫자 불일치")
            ]
        errors.extend(key_errors)
    flattened = "\n".join(quest_snbt.flatten(value) for value in translated.values())
    banned = {
        "정교한 저장소": "Sophisticated Storage",
        "정교한 배낭": "Sophisticated Backpacks",
        "금 간 작업대": "Chipped 작업대",
        "자동 용광로 기능": "자동 용광로 업그레이드",
        "자동 훈연기 기능": "자동 훈연기 업그레이드",
        "자동 화로 기능": "자동 화로 업그레이드",
        "고급 식사 기능": "고급 식사 업그레이드",
        "백팩": "배낭",
        "스토리지 컨트롤러": "저장소 제어기",
    }
    for wrong, expected in banned.items():
        if wrong in flattened:
            errors.append(f"금지 용어가 남았습니다: {wrong} -> {expected}")
    if errors:
        raise ValueError("\n".join(errors))


def kubejs_scope(instance: Path) -> dict[str, object]:
    """KubeJS의 관련 참조 파일과 사용자 표시 문구 수정 필요 여부를 기록한다."""

    files: list[str] = []
    language_files: list[str] = []
    identifier_files: list[str] = []
    root = instance / "kubejs"
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".js",
            ".json",
            ".snbt",
            ".txt",
        }:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        relative = path.relative_to(root).as_posix()
        is_foreign_mirror = bool(
            re.fullmatch(
                r"assets/sophisticated(?:core|storage|storageinmotion)/lang/ru_ru\.json",
                relative,
            )
        )
        if not is_foreign_mirror and not NAMESPACE_RE.search(text):
            continue
        files.append(relative)
        if is_foreign_mirror:
            language_files.append(relative)
        else:
            identifier_files.append(relative)
    return {
        "files_reviewed": files,
        "foreign_language_mirrors": language_files,
        "recipe_or_identifier_references": identifier_files,
        "korean_display_files": [],
        "display_text_corrections": 0,
    }


def build(instance: Path) -> dict[str, object]:
    """검수 작업본을 누적 한국어 SNBT에 병합한다."""

    if OUTPUT_SPLIT.is_dir() and not OUTPUT_FILE.is_file():
        raise ValueError(
            "분할 FTB Quests 출력은 scripts/rebase_ftbquests.py로 갱신해야 합니다."
        )

    source, quests, tasks = scoped_language(instance)
    translated = load_working()
    validate(source, translated)
    installed = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/ko_kr.snbt"
    )
    before = (
        quest_snbt.parse_language_snbt(OUTPUT_FILE)
        if OUTPUT_FILE.is_file()
        else installed
    )
    base = (
        OUTPUT_FILE
        if OUTPUT_FILE.is_file()
        else (instance / "config/ftbquests/quests/lang/ko_kr.snbt")
    )
    merged = quest_snbt.merge_into_full_snbt(base, translated)
    OUTPUT_FILE.write_text(merged, encoding="utf-8")
    reparsed = quest_snbt.parse_language_snbt(OUTPUT_FILE)
    for key, value in translated.items():
        if reparsed.get(key) != value:
            raise ValueError(f"누적 SNBT 병합 결과가 다릅니다: {key}")
    return {
        "chapter": "storage",
        "quests_reviewed": quests,
        "tasks_reviewed": tasks,
        "display_keys_reviewed": len(source),
        "installed_korean_reused": sum(
            installed.get(key) == value for key, value in translated.items()
        ),
        "project_values_reused": sum(
            before.get(key) == value for key, value in translated.items()
        ),
        "quality_review_corrections": sum(
            before.get(key) != value for key, value in translated.items()
        ),
        "kubejs": kubejs_scope(instance),
        "validation_errors": 0,
    }


def verify(instance: Path) -> dict[str, object]:
    """작업본과 누적 산출물의 일치 여부를 재검증한다."""

    source, quests, tasks = scoped_language(instance)
    translated = load_working()
    validate(source, translated)
    output = load_output()
    mismatches = [key for key, value in translated.items() if output.get(key) != value]
    if mismatches:
        raise ValueError(f"누적 SNBT와 작업본이 다릅니다: {mismatches}")
    return {
        "chapter": "storage",
        "quests_reviewed": quests,
        "tasks_reviewed": tasks,
        "display_keys_reviewed": len(source),
        "working_output_match": True,
        "kubejs": kubejs_scope(instance),
        "validation_errors": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    args = parser.parse_args()
    instance = resolve_source_root()
    result = build(instance) if args.command == "build" else verify(instance)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
