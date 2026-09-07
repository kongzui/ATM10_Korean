#!/usr/bin/env python3
"""8.1 호환판의 파일 문법·기존 번역 유지·현재 원본과의 구조 호환성을 검사해요."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from audit_mod_language_rebase import load_languages, validation_errors
from build_ae2_quests import parse_language_snbt, validate_value
from ftbquests_layout import split_locale_files
from local_paths import PROJECT_ROOT, resolve_source_root
from rebase_ftbquests import VALIDATION_ERROR_EXCEPTIONS
from version_context import active_output_root, active_report_dir, read_instance_version

CUSTOM_NAME = re.compile(r'("minecraft:custom_name"\s*:\s*)("(?:\\.|[^"\\])*")')


def strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"중복 키: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)


class SnbtReader:
    """FTB의 줄바꿈 구분 SNBT를 끝까지 읽고 중복 키와 구조를 검사해요."""

    token = re.compile(
        r'\s+|//[^\n]*|\#[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
        r"|[{}\[\]:,;]|[A-Za-z0-9_.+\-]+"
    )

    def __init__(self, text: str):
        self.tokens = []
        position = 0
        for match in self.token.finditer(text):
            if match.start() != position:
                raise ValueError(
                    f"SNBT 알 수 없는 문자: {text[position:position + 30]!r}"
                )
            value = match[0]
            if not value.isspace() and not value.startswith(("//", "#")):
                self.tokens.append(value)
            position = match.end()
        if position != len(text):
            raise ValueError("SNBT 끝에 해석할 수 없는 문자가 있어요")
        self.index = 0

    def take(self, expected: str | None = None) -> str:
        if self.index == len(self.tokens):
            raise ValueError("SNBT가 닫히기 전에 끝났어요")
        token = self.tokens[self.index]
        if expected is not None and token != expected:
            raise ValueError(f"SNBT 예상 {expected}, 실제 {token}")
        self.index += 1
        return token

    def peek(self) -> str:
        return self.tokens[self.index] if self.index < len(self.tokens) else ""

    def value(self) -> object:
        token = self.take()
        if token == "{":
            pairs = []
            while self.peek() != "}":
                key = self.take()
                if key in "{}[]:,;":
                    raise ValueError(f"SNBT 키가 잘못됐어요: {key}")
                self.take(":")
                pairs.append(
                    (json.loads(key) if key.startswith('"') else key, self.value())
                )
                if self.peek() == ",":
                    self.take()
            self.take("}")
            return strict_object(pairs)
        if token == "[":
            result = []
            if self.peek() in {"B", "I", "L"}:
                self.take()
                self.take(";")
            while self.peek() != "]":
                result.append(self.value())
                if self.peek() == ",":
                    self.take()
            self.take("]")
            return result
        if token in "{}]:,;":
            raise ValueError(f"SNBT 값이 잘못됐어요: {token}")
        if token.startswith('"'):
            return json.loads(token)
        return token

    def parse(self) -> object:
        result = self.value()
        if self.index != len(self.tokens):
            raise ValueError("SNBT 최상위 객체 뒤에 내용이 남았어요")
        return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def component_structure(value: object) -> object:
    """Tempad의 정적 텍스트 컴포넌트에서 표시 본문만 제외해요."""
    if isinstance(value, dict):
        return {
            k: "__TEXT__" if k == "text" else component_structure(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [component_structure(v) for v in value]
    return value


def mask_custom_names(raw: str) -> str:
    return CUSTOM_NAME.sub(lambda match: match[1] + '"__NAME__"', raw)


def verify(base_instance: Path) -> dict[str, object]:
    output = active_output_root()
    instance = resolve_source_root()
    if (
        read_instance_version(instance) != "8.1"
        or read_instance_version(base_instance) != "7.1"
    ):
        raise ValueError("이 검증은 ATM10 7.1 → 8.1 호환판용이에요")
    errors = []
    counts: Counter[str] = Counter()
    inventory = {}
    node = shutil.which("node")
    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        relative = path.relative_to(output).as_posix()
        inventory[relative] = sha256(path)
        try:
            if path.suffix in {".json", ".mcmeta"}:
                read_json(path)
                counts["json"] += 1
            elif path.suffix in {".snbt", ".snbt_merged"}:
                SnbtReader(path.read_text(encoding="utf-8")).parse()
                counts["snbt"] += 1
            elif path.suffix == ".js":
                if node is None:
                    raise ValueError("JavaScript 문법 검사용 Node.js를 찾을 수 없어요")
                result = subprocess.run(
                    [node, "--check", str(path)], capture_output=True
                )
                if result.returncode:
                    raise ValueError(result.stderr.decode("utf-8", errors="replace"))
                counts["javascript"] += 1
        except (ValueError, UnicodeError) as exc:
            errors.append(f"{relative}: {exc}")

    pack = output / "resourcepack/ATM10_Korean"
    metadata = read_json(pack / "pack.mcmeta")
    if (
        metadata["pack"]["pack_format"] != 34
        or "8.1" not in metadata["pack"]["description"]
    ):
        errors.append("리소스팩 형식 또는 8.1 설명이 잘못됐어요")
    modern_font = pack / "assets/modernui/font/gyeonggi_title_medium.ttf"
    if modern_font.exists():
        errors.append("배포에서 제외할 Modern UI 전용 글꼴이 남아 있어요")
    for path in (pack / "assets").glob("*/font/*.json"):
        for provider in read_json(path).get("providers", []):
            if provider.get("type") == "ttf":
                namespace, name = provider["file"].split(":", 1)
                font = pack / "assets" / namespace / "font" / name
                if not font.is_file() or font.read_bytes()[:4] not in {
                    b"\x00\x01\x00\x00",
                    b"OTTO",
                }:
                    errors.append(
                        f"TTF 참조 파일이 없거나 잘못됐어요: {provider['file']}"
                    )
                counts["font_references"] += 1

    current, _, language_sources, conflicts, source_errors, _ = load_languages(instance)
    baseline, _, _, base_conflicts, base_errors, _ = load_languages(base_instance)
    errors.extend(conflicts + base_conflicts)
    # 현재 JAR에 이미 있던 한국어 JSON 오류는 프로젝트에서 보정했는지 별도 확인한다.
    for error in source_errors + base_errors:
        if "assets/mcwtrpdoors/lang/ko_kr.json:" not in error:
            errors.append(error)
    assets = pack / "assets"
    missing_delta = []
    inherited_missing = []
    for path in assets.glob("*/lang/ko_kr.json"):
        namespace = path.parent.parent.name
        korean = read_json(path)
        if not isinstance(korean, dict):
            errors.append(f"언어 파일 자료형 오류: {namespace}")
            continue
        non_strings = {k: v for k, v in korean.items() if not isinstance(v, str)}
        if non_strings:
            if namespace != "tempad_static":
                errors.append(f"언어 값 자료형 오류: {namespace}")
                continue
            entry = next(
                s for s in language_sources[namespace] if s.endswith("/en_us.json")
            )
            jar, member = entry.split(":", 1)
            with ZipFile(instance / "mods" / jar) as archive:
                original = json.loads(archive.read(member).decode("utf-8-sig"))
            for key, value in non_strings.items():
                if component_structure(original.get(key)) != component_structure(value):
                    errors.append(f"Tempad 텍스트 컴포넌트 구조 오류: {key}")
                counts["static_text_components"] += 1
        english = current.get(namespace, {})
        old_english = baseline.get(namespace, {})
        string_values = {k: v for k, v in korean.items() if isinstance(v, str)}
        errors.extend(validation_errors(namespace, english, string_values))
        counts["language_files"] += 1
        counts["language_keys"] += len(korean)
        missing_delta.extend(
            f"{namespace}:{key}"
            for key in english
            if old_english.get(key) != english[key] and key not in korean
        )
        old_path = (
            PROJECT_ROOT
            / "output/7.1/resourcepack/ATM10_Korean/assets"
            / namespace
            / "lang/ko_kr.json"
        )
        old_korean = read_json(old_path) if old_path.is_file() else {}
        lost = set(old_korean) & set(english) - set(korean)
        errors.extend(f"7.1 번역 범위 손실: {namespace}:{key}" for key in sorted(lost))
        counts["baseline_values_reused"] += sum(
            korean.get(k) == v for k, v in old_korean.items()
        )
        inherited_missing.extend(
            f"{namespace}:{key}" for key in english if key not in korean
        )
    errors.extend(f"기존 모드 신규·변경 키 누락: {key}" for key in missing_delta)
    for row in read_json(PROJECT_ROOT / "working/compat_8_1/translation_review.json"):
        if current[row["namespace"]][row["key"]] != row["english"]:
            errors.append(f"검토 후 원문 변경: {row['namespace']}:{row['key']}")
        target = read_json(assets / row["namespace"] / "lang/ko_kr.json")
        if target[row["key"]] != row["translation"]:
            errors.append(f"검토한 번역과 산출물이 달라요: {row['key']}")

    source_reviews = read_json(
        PROJECT_ROOT / "versions/8.1/manifests/compat_source_review.json"
    )
    jar_members: dict[str, dict[str, str]] = {}
    for row in source_reviews:
        provider = row["provider"]
        if provider and provider != "instance":
            jar_members.setdefault(provider, {})[row["source"]] = ""
    for jar, members in jar_members.items():
        with ZipFile(instance / "mods" / jar) as archive:
            for member in members:
                members[member] = hashlib.sha256(archive.read(member)).hexdigest()
    for row in source_reviews:
        if sha256(output / row["output"]) != row["output_sha256"]:
            errors.append(f"검토 후 리소스 변경: {row['output']}")
        provider = row["provider"]
        expected = row["current_sha256"]
        if provider == "instance" and expected:
            # 적용 후에는 번역본 자체가 실제 경로에 있으므로 두 해시를 인정한다.
            actual = sha256(instance / row["source"])
            if actual not in {expected, row["output_sha256"]}:
                errors.append(f"검토 후 인스턴스 원본 변경: {row['source']}")
        elif provider and provider != "instance":
            if jar_members[provider][row["source"]] != expected:
                errors.append(f"검토 후 JAR 리소스 변경: {row['source']}")
        counts["resource_source_reviews"] += 1

    chapters = read_json(PROJECT_ROOT / "working/compat_8_1/chapter_review.json")
    for row in chapters:
        relative = row["path"]
        source = (instance / relative).read_text(encoding="utf-8-sig")
        target = (output / "overrides" / relative).read_text(encoding="utf-8")
        if mask_custom_names(source) != mask_custom_names(target):
            errors.append(f"퀘스트 표시 문구 밖의 구조 변경: {relative}")
        counts["chapter_structure_checks"] += 1
    for path in (output / "overrides/config/mysticalcustomization").rglob("*.json"):
        relative = path.relative_to(output / "overrides")
        source = read_json(instance / relative)
        target = read_json(path)
        source.pop("name", None)
        target.pop("name", None)
        if source != target:
            errors.append(f"작물·등급 설정의 표시 문구 밖 구조 변경: {relative}")
        counts["crop_structure_checks"] += 1

    omitted = read_json(PROJECT_ROOT / "working/ftbquests/8.1_omitted_keys.json")
    for relative, path in split_locale_files(instance, "en_us").items():
        target = output / "overrides/config/ftbquests/quests/lang/ko_kr" / relative
        if not target.is_file():
            errors.append(f"퀘스트 분할 파일 누락: {relative}")
            continue
        english = parse_language_snbt(path)
        korean = parse_language_snbt(target)
        errors.extend(
            f"퀘스트 번역 누락: {key}"
            for key in set(english) - set(korean) - set(omitted)
        )
        for key in set(english) & set(korean):
            value_errors = validate_value(key, english[key], korean[key])
            ignored = VALIDATION_ERROR_EXCEPTIONS.get(key, set())
            errors.extend(
                e
                for e in value_errors
                if not any(e.endswith(reason) for reason in ignored)
            )
        counts["quest_keys"] += len(korean)
    legacy = output / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
    if legacy.exists():
        errors.append("8.1에 적용하면 안 되는 7.1 병합 언어 파일이 남아 있어요")
    report = {
        "release": "8.1-compat.1",
        "status": "passed" if not errors else "failed",
        "counts": dict(counts),
        "missing_changed_language_keys": missing_delta,
        "inherited_missing_language_keys": len(inherited_missing),
        "source_known_korean_json_errors": source_errors,
        "game_screen_validation": "not_run",
        "errors": errors,
        "output_sha256": inventory,
    }
    active_report_dir().mkdir(parents=True, exist_ok=True)
    (active_report_dir() / "compat_validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-instance", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.base_instance)
    print(
        json.dumps(
            {k: v for k, v in report.items() if k != "output_sha256"},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
