#!/usr/bin/env python3
"""순차 모드 번역 작업의 자동 번역 검수 후보를 생성한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import sys
from pathlib import Path

import actually_additions_family as candidate_helper
from local_paths import PROJECT_ROOT


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LATIN_WORD = re.compile(r"[A-Za-z]{3,}")


def load_json(path: Path) -> object:
    """UTF-8 JSON을 읽는다."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없이 JSON을 기록한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def string_values(value: object) -> list[str]:
    """중첩된 표시 값에서 문자열을 모두 모은다."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value for text in string_values(item)]
    if isinstance(value, dict):
        return [text for item in value.values() for text in string_values(item)]
    return []


def translated_value(value: object, candidates: dict[str, str]) -> object:
    """원본 구조를 유지한 채 문자열만 후보로 바꾼다."""
    if isinstance(value, str):
        return candidates.get(value, value)
    if isinstance(value, list):
        return [translated_value(item, candidates) for item in value]
    if isinstance(value, dict):
        return {key: translated_value(item, candidates) for key, item in value.items()}
    return value


def english_files(work_root: Path) -> list[Path]:
    """대상 모드군의 영어 작업본만 찾는다."""
    return sorted(work_root.rglob("en_us.json"))


def candidate(family: str) -> dict[str, object]:
    """모든 영어 표시 문자열의 검수용 후보를 생성한다."""
    work_root = PROJECT_ROOT / "working" / family
    files = english_files(work_root)
    if not files:
        raise FileNotFoundError(f"영어 작업본이 없습니다: {work_root}")
    cache_file = PROJECT_ROOT / f"temp/{family}_candidate_cache_v1.json"
    cache_value = load_json(cache_file) if cache_file.is_file() else {}
    if not isinstance(cache_value, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in cache_value.items()
    ):
        raise TypeError(f"후보 캐시가 문자열 JSON 객체가 아닙니다: {cache_file}")
    cache: dict[str, str] = cache_value
    sources: set[str] = set()
    for path in files:
        sources.update(string_values(load_json(path)))
    requests = sorted(
        source
        for source in sources
        if LATIN_WORD.search(source) and source not in cache
    )
    failures: list[str] = []
    if requests:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(
                    candidate_helper.request_translation_candidate, source
                ): source
                for source in requests
            }
            for number, future in enumerate(as_completed(futures), start=1):
                source = futures[future]
                try:
                    cache[source] = future.result()
                    if number % 25 == 0:
                        write_json(cache_file, cache)
                except (
                    Exception
                ) as exc:  # pragma: no cover - 외부 후보 서비스 오류 보고용
                    failures.append(f"{source}: {exc}")
        write_json(cache_file, cache)
    if failures:
        raise RuntimeError("번역 후보 생성 실패:\n" + "\n".join(failures))
    outputs: list[dict[str, object]] = []
    for path in files:
        english = load_json(path)
        output = path.with_name("auto_candidates.json")
        write_json(output, translated_value(english, cache))
        outputs.append(
            {
                "source": path.relative_to(PROJECT_ROOT).as_posix(),
                "output": output.relative_to(PROJECT_ROOT).as_posix(),
                "strings": len(string_values(english)),
            }
        )
    report = {
        "family": family,
        "english_files": len(files),
        "unique_strings": len(sources),
        "candidate_requests": len(requests),
        "outputs": outputs,
        "status": "candidate_requires_full_review",
    }
    write_json(work_root / "auto_candidate_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family")
    args = parser.parse_args()
    print(json.dumps(candidate(args.family), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
