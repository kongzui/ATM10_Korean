#!/usr/bin/env python3
"""8.1 품질 재검수 계열의 퀘스트·언어·KubeJS 산출물을 기준 커밋과 현재 원문으로 검증해요."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

from build_ae2_quests import parse_language_snbt
from build_ae2_quests import validate_value
from ftbquests_layout import split_locale_files
from local_paths import PROJECT_ROOT, resolve_source_root
from rebase_ftbquests import MANUAL_OVERRIDES
from rebase_ftbquests import VALIDATION_ERROR_EXCEPTIONS
from snapshot_instance import collect
from verify_compat_release import sha256

REREVIEW_ROOT = PROJECT_ROOT / "working/quality_rereview"
OUTPUT = PROJECT_ROOT / "output/8.1"
QUEST_LANG = "overrides/config/ftbquests/quests/lang/ko_kr"
PACK_ASSETS = "resourcepack/ATM10_Korean/assets"
PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{\d+\}")
FORMAT_RE = re.compile(r"[&§][0-9a-fk-or]", re.IGNORECASE)
PATCHOULI_TAG_RE = re.compile(r"\$\([^)]*\)")
JS_STRING_RE = re.compile(r"'(?:\\.|[^'\\\n])*'|\"(?:\\.|[^\"\\\n])*\"")


def families() -> list[tuple[str, dict]]:
    """검수를 마친 계열의 범위 파일을 순서대로 읽어요."""
    result = []
    for path in sorted(REREVIEW_ROOT.glob("*/scope.json")):
        scope = json.loads(path.read_text(encoding="utf-8"))
        if scope.get("status") == "completed":
            result.append((path.parent.name, scope))
    return result


def scope_paths(scope: dict) -> set[str]:
    paths = {f"{QUEST_LANG}/{relative}" for relative in scope.get("quest_files", [])}
    paths.update(
        f"{PACK_ASSETS}/{namespace}/lang/ko_kr.json"
        for namespace in scope.get("language_namespaces", [])
    )
    paths.update(
        f"overrides/kubejs/{relative}" for relative in scope.get("kubejs_files", [])
    )
    paths.update(scope.get("guide_files", []))
    return paths


def allowed_paths() -> set[str]:
    """완료된 재검수 계열이 바꿀 수 있는 output 경로만 허용해요."""
    paths: set[str] = set()
    for _, scope in families():
        paths.update(scope_paths(scope))
    return paths


def git_text(commit: str, relative: str) -> str:
    return subprocess.run(
        ["git", "show", f"{commit}:output/8.1/{relative}"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8")


def git_language_snbt(commit: str, relative: str) -> dict:
    """기준 커밋의 분할 언어 SNBT를 현재 산출물과 같은 파서로 읽어요."""
    with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "temp") as directory:
        path = Path(directory) / "baseline.snbt"
        path.write_text(git_text(commit, relative), encoding="utf-8")
        return parse_language_snbt(path)


def verify_quests(name: str, scope: dict, instance: Path, record) -> int:
    english_files = {
        relative.removesuffix("_merged"): path
        for relative, path in split_locale_files(instance, "en_us").items()
    }
    manual = json.loads(MANUAL_OVERRIDES.read_text(encoding="utf-8"))
    revision_root = REREVIEW_ROOT / name / "quests"
    keys = 0
    for relative in scope.get("quest_files", []):
        english = parse_language_snbt(english_files[relative])
        output_path = OUTPUT / QUEST_LANG / relative
        current = parse_language_snbt(output_path)
        baseline = git_language_snbt(
            scope["baseline_commit"], f"{QUEST_LANG}/{relative}"
        )
        if set(current) != set(baseline):
            raise ValueError(f"{relative}: 기준 대비 퀘스트 키가 추가·삭제됐어요")
        if set(current) - set(english):
            raise ValueError(f"{relative}: 현재 영어에 없는 키가 있어요")
        for key, value in current.items():
            items = value if isinstance(value, list) else [value]
            if any("\n" in item for item in items):
                raise ValueError(f"{relative}:{key}: 실제 줄바꿈 문자가 들어 있어요")
            ignored = VALIDATION_ERROR_EXCEPTIONS.get(key, set())
            errors = [
                error
                for error in validate_value(key, english[key], value)
                if not any(error.endswith(reason) for reason in ignored)
            ]
            if errors:
                raise ValueError("; ".join(errors))
            if value != baseline[key] and manual.get(key) != value:
                raise ValueError(f"{relative}:{key}: 8.1 수동 검수 목록과 불일치")
            keys += 1
        stem = Path(relative).stem
        revision_path = revision_root / f"{stem}.json"
        if revision_path.is_file():
            for key, value in json.loads(
                revision_path.read_text(encoding="utf-8")
            ).items():
                if current.get(key) != value:
                    raise ValueError(f"{relative}:{key}: 수정본과 산출물 불일치")
            record(revision_path, PROJECT_ROOT, "project")
        record(english_files[relative], instance, "instance")
        record(output_path, OUTPUT, "output")
    return keys


def verify_languages(scope: dict, record) -> int:
    keys = 0
    for namespace in scope.get("language_namespaces", []):
        relative = f"{PACK_ASSETS}/{namespace}/lang/ko_kr.json"
        current = json.loads((OUTPUT / relative).read_text(encoding="utf-8"))
        baseline = json.loads(git_text(scope["baseline_commit"], relative))
        if list(current) != list(baseline):
            raise ValueError(f"{namespace}: 기준 대비 키 목록·순서가 바뀌었어요")
        for key, value in current.items():
            old = baseline[key]
            if not isinstance(value, str):
                # 텍스트 컴포넌트 목록 같은 비문자열 값은 기준과 같을 때만 허용해요.
                if value != old:
                    raise ValueError(
                        f"{namespace}:{key}: 문자열이 아닌 값이 바뀌었어요"
                    )
                keys += 1
                continue
            if sorted(PLACEHOLDER_RE.findall(value)) != sorted(
                PLACEHOLDER_RE.findall(old)
            ):
                raise ValueError(f"{namespace}:{key}: 자리표시자 불일치")
            if sorted(FORMAT_RE.findall(value)) != sorted(FORMAT_RE.findall(old)):
                raise ValueError(f"{namespace}:{key}: 서식 코드 불일치")
            keys += 1
        record(OUTPUT / relative, OUTPUT, "output")
    return keys


def same_guide_shape(new: object, old: object, where: str) -> None:
    """가이드 JSON은 구조와 문자열 밖의 값이 같고, 문자열의 서식 태그가 같아야 해요."""
    if isinstance(old, dict):
        if not isinstance(new, dict) or list(new) != list(old):
            raise ValueError(f"{where}: 가이드 필드 구성이 바뀌었어요")
        for key in old:
            same_guide_shape(new[key], old[key], f"{where}.{key}")
    elif isinstance(old, list):
        if not isinstance(new, list) or len(new) != len(old):
            raise ValueError(f"{where}: 가이드 목록 길이가 바뀌었어요")
        for index, (child, base) in enumerate(zip(new, old)):
            same_guide_shape(child, base, f"{where}[{index}]")
    elif isinstance(old, str):
        if not isinstance(new, str):
            raise ValueError(f"{where}: 가이드 값 자료형이 바뀌었어요")
        for pattern in (PATCHOULI_TAG_RE, FORMAT_RE):
            if pattern.findall(new) != pattern.findall(old):
                raise ValueError(f"{where}: 가이드 서식 태그 불일치")
    elif new != old:
        raise ValueError(f"{where}: 문자열이 아닌 가이드 값이 바뀌었어요")


def verify_guides(scope: dict, record) -> int:
    files = 0
    for relative in scope.get("guide_files", []):
        path = OUTPUT / relative
        current = json.loads(path.read_text(encoding="utf-8"))
        baseline = json.loads(git_text(scope["baseline_commit"], relative))
        same_guide_shape(current, baseline, relative)
        record(path, OUTPUT, "output")
        files += 1
    return files


def verify_kubejs(scope: dict, record) -> int:
    files = 0
    for relative in scope.get("kubejs_files", []):
        path = OUTPUT / "overrides/kubejs" / relative
        text = path.read_text(encoding="utf-8")
        baseline = git_text(scope["baseline_commit"], f"overrides/kubejs/{relative}")
        if JS_STRING_RE.sub("''", text) != JS_STRING_RE.sub("''", baseline):
            raise ValueError(f"{relative}: 문자열 밖의 코드가 바뀌었어요")
        for new, old in zip(JS_STRING_RE.findall(text), JS_STRING_RE.findall(baseline)):
            if sorted(FORMAT_RE.findall(new)) != sorted(FORMAT_RE.findall(old)):
                raise ValueError(f"{relative}: 서식 코드 불일치 {new}")
        subprocess.run(["node", "--check", str(path)], check=True, capture_output=True)
        record(path, OUTPUT, "output")
        files += 1
    return files


def verify(*, evidence_hash=None):
    instance = resolve_source_root()
    before = collect(instance)
    evidence = {}

    def record(path, root, prefix):
        evidence[f"{prefix}/{path.relative_to(root).as_posix()}"] = sha256(path)
        if evidence_hash:
            evidence_hash(path, root, prefix)

    counts = {}
    try:
        for name, scope in families():
            quest_keys = verify_quests(name, scope, instance, record)
            language_keys = verify_languages(scope, record)
            kubejs_files = verify_kubejs(scope, record)
            guide_files = verify_guides(scope, record)
            record(REREVIEW_ROOT / name / "scope.json", PROJECT_ROOT, "project")
            counts[f"quality_rereview_{name}"] = {
                "language_keys": language_keys,
                "quest_keys": quest_keys,
                "kubejs_files": kubejs_files,
                "guide_files": guide_files,
            }
        record(MANUAL_OVERRIDES, PROJECT_ROOT, "project")
        return {
            "status": "passed",
            "counts": counts,
            "instance_unchanged": True,
            "evidence_sha256": evidence,
        }
    finally:
        if before != collect(instance):
            raise ValueError("검증 중 인스턴스 파일 목록·크기·수정 시각 변경")


if __name__ == "__main__":
    result = verify()
    report = PROJECT_ROOT / "versions/8.1/reports/quality_rereview_validation.json"
    report.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["counts"], ensure_ascii=False))
