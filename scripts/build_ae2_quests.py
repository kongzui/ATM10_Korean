#!/usr/bin/env python3
"""AE2 챕터 번역을 검증하고 전체 ko_kr.snbt override에 병합한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import TypeAlias

from local_paths import resolve_source_root
from version_context import active_output_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OVERRIDES_FILE = PROJECT_ROOT / "working/ae2/quest_overrides.json"
OUTPUT_FILE = active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
PROGRESS_FILE = PROJECT_ROOT / "working/ae2/quest_progress.json"
ENTRY_RE = re.compile(r"^[ \t]*([A-Za-z0-9_.-]+):", re.MULTILINE)
STRING_RE = re.compile(r'"(?:\\.|[^"\\])*"')
FORMAT_RE = re.compile(r"&[0-9a-fklmnor]", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{\d+\}")
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
NUMBER_VALIDATION_EXCEPTIONS = {
    # 원문의 `4`는 수량이 아니라 `for`를 대신한 말장난이다.
    "quest.51236544BFEF487B.quest_subtitle",
}

TranslationValue: TypeAlias = str | list[str]


def parse_language_snbt(path: Path) -> dict[str, TranslationValue]:
    text = path.read_text(encoding="utf-8-sig")
    matches = list(ENTRY_RE.finditer(text))
    result: dict[str, TranslationValue] = {}
    for index, match in enumerate(matches):
        end = (
            matches[index + 1].start() if index + 1 < len(matches) else text.rfind("}")
        )
        raw = text[match.end() : end].strip()
        strings = [json.loads(token) for token in STRING_RE.findall(raw)]
        if not strings:
            raise ValueError(
                f"SNBT 문자열 값을 읽지 못했습니다: {path}:{match.group(1)}"
            )
        result[match.group(1)] = strings if raw.startswith("[") else strings[0]
    return result


def normalize_string(value: str) -> str:
    replacements = (
        ("어플라이드 에너제틱스 2", "Applied Energistics 2"),
        ("회로 인쇄기", "각인기"),
        ("세르투스", "서투스"),
        ("커투스", "서투스"),
        ("Fluix", "플루익스"),
        ("fluix", "플루익스"),
        ("시공", "공간"),
        ("액체", "유체"),
        ("저장고", "저장소"),
        ("패턴 공급자", "패턴 공급기"),
        ("상위 버전으로 변환", "업그레이드"),
        ("오른손 클릭", "우클릭"),
        ("우선 순위", "우선순위"),
        ("게임 내 가이드", "게임 내 AE2 가이드"),
    )
    for old, new in replacements:
        value = value.replace(old, new)
    value = re.sub(r"조합(?!법)", "제작", value)
    value = value.replace("보조처리", "보조 처리")
    return value


def normalize(value: TranslationValue) -> TranslationValue:
    if isinstance(value, str):
        return normalize_string(value)
    return [normalize_string(item) for item in value]


def flatten(value: TranslationValue) -> str:
    return "\n".join(value) if isinstance(value, list) else value


def validate_value(
    key: str, source: TranslationValue, translated: TranslationValue
) -> list[str]:
    errors = []
    if type(source) is not type(translated):
        return [f"{key}: 값 자료형 불일치"]
    if isinstance(source, list) and len(source) != len(translated):
        errors.append(f"{key}: 문단 수 불일치")
    source_text = flatten(source)
    translated_text = flatten(translated)
    if Counter(FORMAT_RE.findall(source_text)) != Counter(
        FORMAT_RE.findall(translated_text)
    ):
        errors.append(f"{key}: 색상/서식 코드 불일치")
    if Counter(PLACEHOLDER_RE.findall(source_text)) != Counter(
        PLACEHOLDER_RE.findall(translated_text)
    ):
        errors.append(f"{key}: 자리표시자 불일치")
    if key not in NUMBER_VALIDATION_EXCEPTIONS and Counter(
        NUMBER_RE.findall(source_text)
    ) != Counter(NUMBER_RE.findall(translated_text)):
        errors.append(f"{key}: 숫자 불일치")
    if source_text.count("\\n") != translated_text.count("\\n"):
        errors.append(f"{key}: 줄바꿈 개수 불일치")
    return errors


def serialize_snbt(value: TranslationValue) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if len(value) == 1:
        return f"[{json.dumps(value[0], ensure_ascii=False)}]"
    lines = ["["]
    lines.extend(f"\t\t{json.dumps(item, ensure_ascii=False)}" for item in value)
    lines.append("\t]")
    return "\n".join(lines)


def merge_into_full_snbt(
    source_path: Path, translations: dict[str, TranslationValue]
) -> str:
    text = source_path.read_text(encoding="utf-8-sig")
    matches = list(ENTRY_RE.finditer(text))
    existing = {match.group(1) for match in matches}
    replacements = []
    for index, match in enumerate(matches):
        key = match.group(1)
        if key not in translations:
            continue
        end = (
            matches[index + 1].start() if index + 1 < len(matches) else text.rfind("}")
        )
        replacements.append(
            (match.end(), end, " " + serialize_snbt(translations[key]) + "\n")
        )
    for start, end, replacement in reversed(replacements):
        text = text[:start] + replacement + text[end:]

    missing = [key for key in translations if key not in existing]
    if missing:
        closing = text.rfind("}")
        additions = "".join(
            f"\t{key}: {serialize_snbt(translations[key])}\n" for key in sorted(missing)
        )
        text = text[:closing] + additions + text[closing:]
    return text


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    lang_root = instance / "config/ftbquests/quests/lang"
    english_path = lang_root / "en_us/chapters/applied_energistics_2.snbt_merged"
    current_path = lang_root / "ko_kr/chapters/applied_energistics_2.snbt_merged"
    full_current_path = lang_root / "ko_kr.snbt"

    english = parse_language_snbt(english_path)
    current = parse_language_snbt(current_path)
    overrides = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
    if set(overrides) - set(english):
        raise ValueError(
            f"영어 원문에 없는 퀘스트 키: {sorted(set(overrides) - set(english))}"
        )

    final = {
        key: normalize(overrides[key])
        if key in overrides
        else normalize(current[key])
        if key in current
        else None
        for key in english
    }
    missing = [key for key, value in final.items() if value is None]
    if missing:
        raise ValueError(f"번역되지 않은 AE2 퀘스트 키: {missing}")
    typed_final = {key: value for key, value in final.items() if value is not None}

    errors = []
    for key in english:
        errors.extend(validate_value(key, english[key], typed_final[key]))
    if errors:
        raise ValueError("\n".join(errors))

    merged = merge_into_full_snbt(full_current_path, typed_final)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(merged, encoding="utf-8")
    reparsed = parse_language_snbt(OUTPUT_FILE)
    for key, value in typed_final.items():
        if reparsed.get(key) != value:
            raise ValueError(f"전체 SNBT 병합 결과가 다릅니다: {key}")

    kept = sum(key in current and typed_final[key] == current[key] for key in english)
    corrected = sum(
        key in current and typed_final[key] != current[key] for key in english
    )
    new = sum(key not in current for key in english)
    progress = {
        "scope": "FTB Quests applied_energistics_2 chapter",
        "total_keys": len(english),
        "existing_korean_kept": kept,
        "existing_korean_corrected": corrected,
        "newly_completed": new,
        "remaining": 0,
        "output": OUTPUT_FILE.relative_to(PROJECT_ROOT).as_posix(),
        "output_sha256": sha256(OUTPUT_FILE),
        "validation_errors": 0,
        "review_items": [],
    }
    PROGRESS_FILE.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(progress, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
