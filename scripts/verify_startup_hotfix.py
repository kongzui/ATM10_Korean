#!/usr/bin/env python3
"""7.1·8.1 수정판의 변경 범위, 전체 문법과 실제 Rhino 콜백을 검증해요."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path

from local_paths import PROJECT_ROOT
from verify_compat_release import SnbtReader, read_json, sha256
from version_context import read_instance_version

BASELINE = "18eb59d"
SCRIPT_NAMES = (
    "appleskin_debug_labels.js",
    "mousetweaks_config_labels.js",
    "enderdrives_messages.js",
)
SCRIPT_DIR = "overrides/kubejs/startup_scripts"
PACK_DIR = "resourcepack/ATM10_Korean"
FONT = f"{PACK_DIR}/assets/modernui/font/gyeonggi_title_medium.ttf"


def fixed_script(raw: bytes) -> bytes:
    result = re.sub(rb"(?m)^(\s*)const ", rb"\1let ", raw)
    result = result.replace(b"for (const [source, key]", b"for (let [source, key]")
    return result.replace(
        b"function translateWidgets(screen, widgets) {",
        b"let translateWidgets = function (screen, widgets) {",
    )


def run(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, capture_output=True, cwd=PROJECT_ROOT)


def verify(version: str, instance: Path, java: Path, javac: Path) -> dict:
    if read_instance_version(instance) != version:
        raise ValueError("검증할 산출물과 실제 원본 버전이 달라요")
    output = PROJECT_ROOT / "output" / version
    temp = PROJECT_ROOT / "temp/startup_hotfix" / version
    temp.mkdir(parents=True, exist_ok=True)
    errors = []
    counts = Counter()
    inventory = {}
    node = shutil.which("node")
    if not node:
        raise ValueError("Node.js 문법 검사 도구가 없어요")
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
                checked = run([node, "--check", str(path)])
                if checked.returncode:
                    raise ValueError(checked.stderr.decode("utf-8", errors="replace"))
                counts["javascript"] += 1
        except (ValueError, UnicodeError) as exc:
            errors.append(f"{relative}: {exc}")

    # 이전 커밋의 모든 파일과 대조해 번역, 퀘스트 및 무관한 코드의 변경을 차단해요.
    prefix = f"output/{version}/"
    listing = run(["git", "ls-tree", "-r", "--name-only", BASELINE, "--", prefix])
    if listing.returncode:
        raise ValueError("수정 전 산출물 목록을 읽지 못했어요")
    names = listing.stdout.decode("utf-8").splitlines()
    batch = subprocess.run(
        ["git", "cat-file", "--batch"],
        input="".join(f"{BASELINE}:{name}\n" for name in names).encode("utf-8"),
        capture_output=True,
        cwd=PROJECT_ROOT,
        check=True,
    ).stdout
    offset = 0
    changed = []
    baseline_scripts = []
    for name in names:
        end = batch.index(b"\n", offset)
        size = int(batch[offset:end].split()[-1])
        old = batch[end + 1 : end + 1 + size]
        offset = end + size + 2
        relative = name.removeprefix(prefix)
        path = output / relative
        if path.name == ".gitkeep":
            continue
        if relative == FONT:
            if path.exists():
                errors.append("개인 Modern UI 글꼴이 남아 있어요")
            if not path.exists():
                changed.append(relative)
            continue
        new = path.read_bytes()
        old_lf, new_lf = old.replace(b"\r\n", b"\n"), new.replace(b"\r\n", b"\n")
        if relative in {f"{SCRIPT_DIR}/{n}" for n in SCRIPT_NAMES}:
            original = temp / path.name
            original.write_bytes(old)
            baseline_scripts.append(original)
            if fixed_script(old_lf) != new_lf:
                errors.append(f"선언 호환성 수정 이외 스크립트 변경: {relative}")
        elif version == "7.1" and relative in {
            f"{PACK_DIR}/assets/herbsandharvest/books/chapters/{n}.json"
            for n in ("herbs", "grapes")
        }:
            value, tail = json.JSONDecoder().raw_decode(old_lf.decode().lstrip())
            remainder = old_lf.decode().lstrip()[tail:]
            if re.sub(r"\s", "", remainder) != "]}" or value != read_json(path):
                errors.append(f"중복 닫기 제거 외 가이드 변경: {relative}")
        elif relative not in {"release.json", f"{PACK_DIR}/pack.mcmeta"}:
            if old_lf != new_lf:
                errors.append(f"허용하지 않은 산출물 변경: {relative}")
        if old_lf != new_lf:
            changed.append(relative)
        if "/lang/" in relative and path.suffix == ".json":
            counts["unchanged_language_values"] += len(read_json(path))
    added = set(inventory) - {name.removeprefix(prefix) for name in names}
    # 기존 world/ 제외 규칙에 걸린 가이드 10개는 이전 배포의 해시·원문 검토로 확인해요.
    previous = json.loads(
        run(
            ["git", "show", f"{BASELINE}:versions/8.1/reports/compat_validation.json"]
        ).stdout
    )
    reviewed = json.loads(
        run(
            [
                "git",
                "show",
                f"{BASELINE}:versions/8.1/manifests/compat_source_review.json",
            ]
        ).stdout
    )
    unchanged_sources = {
        r["output"]
        for r in reviewed
        if r["state"] == "unchanged" and r["baseline_sha256"] == r["current_sha256"]
    }
    for name in sorted(added):
        if name not in unchanged_sources or inventory[name] != previous[
            "output_sha256"
        ].get(name):
            errors.append(f"계획 밖 산출물 추가: {name}")
        else:
            counts["inherited_ignored_guides_verified"] += 1
    pack = output / PACK_DIR
    if read_json(pack / "pack.mcmeta")["pack"]["pack_format"] != 34:
        errors.append("리소스팩 형식 오류")
    if (output / FONT).exists():
        errors.append("Modern UI 개인 글꼴 포함")
    for path in (pack / "assets").glob("*/font/*.json"):
        for provider in read_json(path).get("providers", []):
            if provider.get("type") == "ttf":
                namespace, name = provider["file"].split(":", 1)
                font = pack / "assets" / namespace / "font" / name
                if not font.exists() or font.read_bytes()[:4] not in {
                    b"\x00\x01\x00\x00",
                    b"OTTO",
                }:
                    errors.append(f"글꼴 참조 오류: {provider['file']}")
                counts["font_references"] += 1

    (rhino,) = instance.glob("mods/rhino-*.jar")
    rhino_hash = sha256(rhino)
    scripts = PROJECT_ROOT / "scripts"
    compiled = run(
        [
            str(javac),
            "-encoding",
            "UTF-8",
            "-d",
            str(temp),
            str(scripts / "StartupRhinoCheck.java"),
        ]
    )
    if compiled.returncode:
        raise ValueError(compiled.stderr.decode("utf-8", errors="replace"))
    command = [
        str(java),
        "-Dfile.encoding=UTF-8",
        "-cp",
        f"{temp};{rhino}",
        "StartupRhinoCheck",
    ]
    translations = read_json(pack / "assets/mousetweaks/lang/ko_kr.json")
    modes = []
    for client, loaded in ((True, True), (False, True), (True, False)):
        settings = temp / "settings.js"
        settings.write_text(
            f"var testClient = {json.dumps(client)};\n"
            f"var testModsLoaded = {json.dumps(loaded)};\n"
            f"var testTranslations = {json.dumps(translations, ensure_ascii=False)};\n",
            encoding="utf-8",
        )
        setup = [str(settings), str(scripts / "startup_rhino_fixture.js")]
        if client and loaded:
            for original in baseline_scripts:
                result = run(command + setup + [str(original)])
                if (
                    result.returncode == 0
                    or b"redeclaration of var" not in result.stderr
                ):
                    errors.append(f"수정 전 오류 재현 실패: {original.name}")
                else:
                    counts["original_errors_reproduced"] += 1
        result = run(
            command
            + setup
            + [str(output / SCRIPT_DIR / n) for n in SCRIPT_NAMES]
            + [str(scripts / "startup_rhino_assertions.js")]
        )
        modes.append(
            {"client": client, "mods_loaded": loaded, "passed": result.returncode == 0}
        )
        if result.returncode:
            errors.append(result.stderr.decode("utf-8", errors="replace"))
    if rhino_hash != sha256(rhino):
        errors.append("Rhino 원본 JAR 변경")
    report = {
        "release": read_json(output / "release.json")["release_id"],
        "status": "passed" if not errors else "failed",
        "baseline_commit": BASELINE,
        "counts": dict(counts),
        "changed_paths": changed,
        "rhino": {"jar": rhino.name, "sha256": rhino_hash, "modes": modes},
        "scope": "실제 Rhino 엔진 + 게임 API 대역, 이벤트 반복·필터·서버 조건 검사",
        "game_screen_validation": "not_run",
        "deployment": "not_applied_user_will_install",
        "errors": errors,
        "output_sha256": inventory,
    }
    destination = (
        PROJECT_ROOT / "versions" / version / "reports/startup_hotfix_validation.json"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", choices=("7.1", "8.1"), required=True)
    parser.add_argument("--instance", type=Path, required=True)
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--javac", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.version, args.instance, args.java, args.javac)
    print(
        json.dumps(
            {k: v for k, v in result.items() if k != "output_sha256"},
            ensure_ascii=False,
            indent=2,
        )
    )
    raise SystemExit(0 if result["status"] == "passed" else 1)
