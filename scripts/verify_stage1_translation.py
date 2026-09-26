#!/usr/bin/env python3
"""8.1 단계1 누적 배포의 고정 범위와 현재 원문·검수 증거를 검사해요.

review.json은 {schema_version: 1, mod: ..., entries: [...]} 형태예요.
각 entry에는 key, english, translation, reviewed: true가 필요해요.
quest_audit.json은 같은 필드에 english_path, english_sha256, structure_path,
structure_sha256, output_path, output_sha256, source_layout: split_snbt_merged,
baseline_value_sha256: {key: 기존 manifest 해시}를 추가해요. 경로는 인스턴스 또는
output/8.1 기준이며 아래 고정 경로와 일치해야 해요. 퀘스트 entries는 현재
영어의 모든 키를 포함해요. 영어에 없는 기존 키는 기준 번역 그대로만 허용해요.
새 fallback 키나 영어 키 삭제는 별도 표시 경로 계약 확정 전 차단해요.
가이드는 working/auroral/guide/{en_us,ko_kr}/<상대경로>와 review.json을 사용해요.
가이드 review는 schema_version: 1, mod: auroral, entries 배열이며 각 행은
path, source_sha256, target_sha256, reviewed: true로 원시 파일 바이트에 결합해요.
"""

from __future__ import annotations

import hashlib
import json
import posixpath
import re
import subprocess
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import build_ae2_guide as guide
from build_ae2_addon_guides import validate_tag_nesting
from local_paths import PROJECT_ROOT, resolve_source_root
from rebase_ftbquests import value_hash
from verify_compat_release import SnbtReader, read_json, sha256, strict_object
from version_context import read_instance_version

BASELINE = "3aa66388e4cf3fcf9dc1f928d90dedc250769d5e"
RELEASE_MODS = {
    "8.1-stable.2": ("auroral",),
    "8.1-stable.3": ("auroral", "neovitae"),
    "8.1-stable.4": ("auroral", "neovitae"),
}
CHAPTERS = {"auroral": "auroral", "neovitae": "neo_vitae"}
PACK = "resourcepack/ATM10_Korean"
QUEST_ROOT = "config/ftbquests/quests"
METADATA = {"release.json", f"{PACK}/pack.mcmeta"}
GUIDE_ROOT = "assets/auroral/auroral"
GUIDE_PAGES = (
    "aurora/aurora_events.md",
    "aurora/creatures.md",
    "decorations/aurora_lantern.md",
    "decorations/hearthwood_log.md",
    "decorations/snow_angel.md",
    "flora/aurora_blooms.md",
    "flora/ender_bloom.md",
    "flora/glow_leeks.md",
    "flora/shimmering_ice.md",
    "food/frosted_cookies.md",
    "food/hot_cocoa.md",
    "food/index.md",
    "food/roasted_snowball.md",
    "food/snore.md",
    "food/sugared_roasted_snowball.md",
    "getting_started/first_steps.md",
    "getting_started/introduction.md",
    "index.md",
    "shimmersteel/armor_trims.md",
    "shimmersteel/bow.md",
    "shimmersteel/cold_brewing_stand.md",
    "shimmersteel/glacial_basin.md",
    "shimmersteel/ingots.md",
    "shimmersteel/tools.md",
    "shimmerweave/fabric.md",
    "shimmerweave/goggles.md",
    "shimmerweave/leggings.md",
    "shimmerweave/skates.md",
    "shimmerweave/tunic.md",
)
PLACEHOLDER = re.compile(
    r"(?<!\d)%(?:(?:\d+\$)?[-#+0,(<]*\d*(?:\.\d+)?(?:[tT][a-zA-Z]|[a-zA-Z%]))"
    r"|\{[A-Za-z0-9_]+(?:,[^{}]+)?\}"
)
FORMAT = re.compile(r"[§&][0-9a-fk-or]|\$\([^)]*\)", re.IGNORECASE)
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
BOOK_COLOR = re.compile(r"\[\#\]\([^)]*\)")
LINK_TARGET = re.compile(r"!?\[(?:\\.|[^\]\\])*\]\(((?:\\.|[^()\\]|\([^()]*\))*)\)")
URL = re.compile(r"(?:https?://|mailto:)[^\s<>\"'\[\]()]+")


def git_bytes(relative: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{BASELINE}:{relative}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=True,
    ).stdout


def baseline_inventory() -> dict[str, str]:
    report = json.loads(
        git_bytes("versions/8.1/reports/stable_validation.json"),
        object_pairs_hook=strict_object,
    )
    if report["status"] != "passed" or report["release"] != "8.1-stable.1":
        raise ValueError("고정 기준 커밋의 stable.1 검증이 유효하지 않아요")
    # 보고서의 해시뿐 아니라 고정 커밋에 저장된 실제 output도 대조해요.
    listed = (
        subprocess.run(
            ["git", "ls-tree", "-r", "-z", "--name-only", BASELINE, "output/8.1/"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            check=True,
        )
        .stdout.decode("utf-8")
        .rstrip("\0")
        .split("\0")
    )
    paths = [p for p in listed if not p.endswith("/.gitkeep")]
    expected = report["output_sha256"]
    if {p.removeprefix("output/8.1/") for p in paths} - set(expected):
        raise ValueError("기준 커밋의 파일 목록과 검증 보고서가 달라요")
    # 기준 보고서에만 있는 기존 10개 파일도 아래 산출물 비교에서 해시를 계승해요.
    # cat-file 일괄 조회로 파일마다 Git 프로세스를 만드는 비용을 줄여요.
    refs = "".join(f"{BASELINE}:{p}\n" for p in paths).encode("utf-8")
    data = subprocess.run(
        ["git", "cat-file", "--batch"],
        input=refs,
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=True,
    ).stdout
    offset = 0
    for path in paths:
        end = data.index(b"\n", offset)
        header = data[offset:end].split()
        if len(header) != 3 or header[1] != b"blob":
            raise ValueError(f"기준 원본을 읽을 수 없어요: {path}")
        size = int(header[2])
        blob = data[end + 1 : end + 1 + size]
        offset = end + size + 2
        digests = {hashlib.sha256(blob).hexdigest()}
        # Windows 보고서의 CRLF 체크아웃과 Git의 LF 텍스트 차이만 인정해요.
        # 실제 output은 아래에서 기준 보고서의 원시 바이트 해시 그대로 검사해요.
        try:
            blob.decode("utf-8")
        except UnicodeDecodeError:
            pass
        else:
            if b"\0" not in blob:
                crlf = blob.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
                digests.add(hashlib.sha256(crlf).hexdigest())
        if expected[path.removeprefix("output/8.1/")] not in digests:
            # 일부 기존 JS는 CRLF/LF가 섞여 있어 일괄 변환으로 재현되지 않아요.
            # 이때는 보고서의 원시 해시와 일치하는 현재 파일을 읽어 Git 원본과
            # 줄 끝만 정규화해서 대조해요. 내용 변경이나 해시 갱신은 허용하지 않아요.
            current = (PROJECT_ROOT / path).read_bytes()
            if hashlib.sha256(current).hexdigest() != expected[
                path.removeprefix("output/8.1/")
            ] or current.replace(b"\r\n", b"\n") != blob.replace(b"\r\n", b"\n"):
                raise ValueError(f"기준 output과 검증 해시가 달라요: {path}")
    return expected


def allowed_paths(release_id: str) -> set[str]:
    paths = set(METADATA)
    paths.update(f"{PACK}/{GUIDE_ROOT}/_ko_kr/{p}" for p in GUIDE_PAGES)
    for mod in RELEASE_MODS[release_id]:
        paths.add(f"{PACK}/assets/{mod}/lang/ko_kr.json")
        paths.add(f"overrides/{QUEST_ROOT}/lang/ko_kr/chapters/{CHAPTERS[mod]}.snbt")
    if release_id == "8.1-stable.4":
        import verify_ad_astra_translation as ad_astra

        paths.update(ad_astra.allowed_paths())
    return paths


def check_value(key: str, english: object, korean: object) -> None:
    """문단별 자료형과 보호 토큰을 예외 목록 없이 모두 검사해요."""
    if type(english) is not type(korean):
        raise ValueError(f"{key}: 자료형 불일치")
    if isinstance(english, list):
        if len(english) != len(korean):
            raise ValueError(f"{key}: 문단 수 불일치")
        for index, (source, target) in enumerate(zip(english, korean)):
            check_value(f"{key}[{index}]", source, target)
        return
    if not isinstance(english, str):
        raise ValueError(f"{key}: 문자열 이외의 언어 값")
    if english.strip() and not korean.strip():
        raise ValueError(f"{key}: 빈 번역")
    for label, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식", FORMAT),
        ("숫자", NUMBER),
        ("책 색상 표식", BOOK_COLOR),
        ("링크 대상", LINK_TARGET),
        ("URL", URL),
    ):
        if Counter(pattern.findall(english)) != Counter(pattern.findall(korean)):
            raise ValueError(f"{key}: {label} 불일치")
    for label, pattern in (
        ("태그", guide.TAG_RE),
        ("인라인 코드", guide.INLINE_CODE_RE),
    ):
        if pattern.findall(english) != pattern.findall(korean):
            raise ValueError(f"{key}: {label} 또는 순서 불일치")
    source_tokens = PLACEHOLDER.findall(english)
    if source_tokens != PLACEHOLDER.findall(korean) and any(
        p.startswith("%") and p != "%%" and not re.match(r"%\d+\$", p)
        for p in source_tokens
    ):
        raise ValueError(f"{key}: 비순번 자리표시자 순서 불일치")
    for token in ("\n", "\r", "\t", "\\n", "\\r", "\\t", "\\"):
        if english.count(token) != korean.count(token):
            raise ValueError(f"{key}: 개행·이스케이프 불일치 {token!r}")


def check_review(mod: str, review: dict, english: dict, korean: dict) -> int:
    if review.get("schema_version") != 1 or review.get("mod") != mod:
        raise ValueError(f"{mod}: 검수 자료 스키마 또는 모드 오류")
    rows = review["entries"]
    if not isinstance(rows, list):
        raise ValueError(f"{mod}: entries는 배열이어야 해요")
    keys = [r["key"] for r in rows]
    if len(keys) != len(set(keys)) or set(keys) != set(english):
        raise ValueError(f"{mod}: 전체 영어 키의 검수 증거가 없거나 중복돼요")
    for row in rows:
        key = row["key"]
        if (
            row.get("reviewed") is not True
            or row["english"] != english[key]
            or row["translation"] != korean[key]
        ):
            raise ValueError(f"{mod}:{key}: 현재 원문·번역과 검수 증거 불일치")
        check_value(key, english[key], korean[key])
    return len(rows)


def snapshot(root: Path) -> dict[str, tuple[int, int]]:
    result = {}
    for path in root.rglob("*"):
        if path.is_file():
            stat = path.stat()
            result[path.relative_to(root).as_posix()] = (stat.st_size, stat.st_mtime_ns)
    return result


def check_guides(jar: Path, output: Path, evidence_hash) -> int:
    """현재 Auroral JAR의 29페이지와 번역 검수·구조를 직접 대조해요."""
    working = PROJECT_ROOT / "working/auroral/guide"
    review_path = working / "review.json"
    review = read_json(review_path)
    if review.get("schema_version") != 1 or review.get("mod") != "auroral":
        raise ValueError("Auroral 가이드 검수 스키마 오류")
    rows = review["entries"]
    if not isinstance(rows, list):
        raise ValueError("가이드 entries는 배열이어야 해요")
    pages = [r["path"] for r in rows]
    if len(pages) != len(set(pages)) or set(pages) != set(GUIDE_PAGES):
        raise ValueError("가이드 전체 29페이지의 검수 증거가 없거나 중복돼요")
    with ZipFile(jar) as archive:
        names = archive.namelist()
        actual = [
            n.removeprefix(f"{GUIDE_ROOT}/")
            for n in names
            if n.startswith(f"{GUIDE_ROOT}/")
            and n.endswith(".md")
            and not n.removeprefix(f"{GUIDE_ROOT}/").startswith("_")
        ]
        if len(actual) != len(set(actual)) or set(actual) != set(GUIDE_PAGES):
            raise ValueError("현재 JAR의 영어 가이드 목록이 고정 범위와 달라요")
        for row in rows:
            page = row["path"]
            source = archive.read(f"{GUIDE_ROOT}/{page}")
            target_path = output / PACK / GUIDE_ROOT / "_ko_kr" / page
            target = target_path.read_bytes()
            if (
                row.get("reviewed") is not True
                or row.get("source_sha256") != hashlib.sha256(source).hexdigest()
                or row.get("target_sha256") != hashlib.sha256(target).hexdigest()
                or (working / "en_us" / page).read_bytes() != source
                or (working / "ko_kr" / page).read_bytes() != target
            ):
                raise ValueError(f"가이드 원문/검수/산출물 불일치: {page}")
            english = source.decode("utf-8")
            korean = target.decode("utf-8")
            # 기존 Markdown 검증기는 LF 기준이며 원시 개행은 별도로 보존 검사해요.
            normalized_source = english.replace("\r\n", "\n")
            normalized_target = korean.replace("\r\n", "\n")
            errors = guide.validate_pair(page, normalized_source, normalized_target)
            errors.extend(validate_tag_nesting(page, normalized_target))
            if errors:
                raise ValueError("; ".join(errors))
            check_value(page, english, korean)
            # title 외 YAML은 원문 문자열로 고정하고 title도 단일 문자열만 허용해요.
            metadata, _ = guide.split_front_matter(normalized_target)
            title = (
                guide.NAVIGATION_TITLE_RE.search(metadata)[0].split(":", 1)[1].strip()
            )
            if not title or title.startswith(("[", "{", "&", "*", "!", "|", ">")):
                raise ValueError(f"가이드 YAML 제목 자료형 오류: {page}")
            if title.startswith('"'):
                if not isinstance(json.loads(title), str):
                    raise ValueError(f"가이드 YAML 제목 자료형 오류: {page}")
            elif title.startswith("'"):
                if not re.fullmatch(r"'(?:[^']|'')*'", title):
                    raise ValueError(f"가이드 YAML 제목 따옴표 오류: {page}")
            elif ": " in title or " #" in title:
                raise ValueError(f"가이드 YAML 제목은 따옴표가 필요해요: {page}")
            targets = [
                *(m.group(1) for m in guide.LINK_TARGET_RE.finditer(normalized_target)),
                *(
                    m.group(1)
                    for m in guide.IMAGE_TARGET_RE.finditer(normalized_target)
                ),
                *(m.group(1) for m in guide.IMPORT_RE.finditer(normalized_target)),
            ]
            for reference in targets:
                clean = reference.split("#", 1)[0].split("?", 1)[0]
                if not clean or re.match(r"^(?:https?://|mailto:)", clean):
                    continue
                resolved = posixpath.normpath(
                    f"{GUIDE_ROOT}/{posixpath.dirname(page)}/{clean}"
                )
                if resolved not in names:
                    raise ValueError(f"가이드 참조 대상 없음: {page}: {reference}")
            for path in (working / "en_us" / page, working / "ko_kr" / page):
                evidence_hash(path, PROJECT_ROOT, "project")
    evidence_hash(review_path, PROJECT_ROOT, "project")
    return len(rows)


def check_neovitae_book(jar: Path, english: dict, korean: dict, evidence_hash) -> dict:
    """책 JSON의 참조와 직접 표시 문구를 현재 JAR에서 다시 수집해요."""
    working = PROJECT_ROOT / "working/neovitae"
    literals = {}
    references = set()

    def visit(value, member, pointer=""):
        if isinstance(value, dict):
            for key, child in value.items():
                location = f"{pointer}/{key}"
                if (
                    key in ("title", "text", "name", "description")
                    and isinstance(child, str)
                    and child.strip()
                    and not child.startswith("book.neovitae.")
                ):
                    literals.setdefault(child, []).append(
                        {"source": member, "pointer": location}
                    )
                visit(child, member, location)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, member, f"{pointer}/{index}")
        elif isinstance(value, str) and value.startswith("book.neovitae."):
            references.add(value)

    with ZipFile(jar) as archive:
        members = [
            name
            for name in archive.namelist()
            if name.startswith("data/neovitae/modonomicon/books/")
            and name.endswith(".json")
        ]
        if len(members) != 223 or len(set(members)) != len(members):
            raise ValueError("Neo Vitae 책 JSON 전체 223개 범위가 달라요")
        for member in members:
            visit(
                json.loads(archive.read(member), object_pairs_hook=strict_object),
                member,
            )
    if len(references) != 1529 or references - set(english):
        raise ValueError("Neo Vitae 책의 언어 참조가 변경되거나 누락됐어요")
    source_path = working / "guide_literal_sources.json"
    if len(literals) != 61 or literals != read_json(source_path):
        raise ValueError("Neo Vitae 직접 표시 문구의 현재 원문·위치가 달라요")
    if set(literals) & set(english) or set(korean) != set(english) | set(literals):
        raise ValueError("Neo Vitae 추가 언어 키가 현재 책의 직접 표시 문구와 달라요")
    review_path = working / "guide_literals.review.json"
    review = read_json(review_path)
    count = check_review("neovitae", review, {key: key for key in literals}, korean)
    for row in review["entries"]:
        if row.get("sources") != literals[row["key"]]:
            raise ValueError("Neo Vitae 직접 표시 문구의 검수 위치가 달라요")
    # 직접 문자열도 I18n.get으로 번역하는 현재 로더의 조사 증거를 결합해요.
    bytecode_path = PROJECT_ROOT / "working/stage1_audit/bytecode_display_evidence.json"
    records = [
        row
        for row in read_json(bytecode_path)["evidence"]
        if row["member"] == "com/klikli_dev/modonomicon/book/BookTextHolder.class"
    ]
    if len(records) != 1:
        raise ValueError("직접 표시 문자열의 로더 조사 증거가 없거나 중복돼요")
    record = records[0]
    loader = jar.parent / Path(record["jar"]).name
    with ZipFile(loader) as archive:
        digest = hashlib.sha256(archive.read(record["member"])).hexdigest()
    if digest != record["class_sha256"]:
        raise ValueError("직접 표시 문자열을 처리하는 현재 로더가 변경됐어요")
    evidence_hash(loader, jar.parent.parent, "instance")
    for path in (source_path, review_path, bytecode_path):
        evidence_hash(path, PROJECT_ROOT, "project")
    return {
        "book_json_files": len(members),
        "book_referenced_keys": len(references),
        "book_literal_keys": count,
    }


def verify(release_id: str, inventory: dict[str, str]) -> dict:
    """현재 JAR을 읽기 전용으로 확인하고 재현 가능한 증거 해시를 반환해요."""
    mods = RELEASE_MODS[release_id]
    baseline = baseline_inventory()
    allowed = allowed_paths(release_id)
    missing = set(baseline) - set(inventory)
    changed = {p for p in inventory if inventory[p] != baseline.get(p)}
    if missing or changed - allowed:
        raise ValueError(
            f"단계1 범위 밖 변경/삭제: {sorted(missing | (changed - allowed))}"
        )
    output = PROJECT_ROOT / "output/8.1"
    instance = resolve_source_root()
    before = snapshot(instance)
    evidence = {}
    counts = Counter()
    additional_family = None

    def evidence_hash(path: Path, root: Path, prefix: str) -> str:
        digest = sha256(path)
        evidence[f"{prefix}/{path.relative_to(root).as_posix()}"] = digest
        return digest

    try:
        if read_instance_version(instance) != "8.1":
            raise ValueError("단계1 검증에는 현재 ATM10 8.1 인스턴스가 필요해요")
        evidence_hash(instance / "manifest.json", instance, "instance")
        english_members = {f"assets/{m}/lang/en_us.json": m for m in mods}
        sources = {}
        source_jars = {}
        for jar in sorted((instance / "mods").glob("*.jar")):
            with ZipFile(jar) as archive:
                names = archive.namelist()
                for member, mod in english_members.items():
                    if member not in names:
                        continue
                    if names.count(member) != 1 or mod in sources:
                        raise ValueError(f"{mod}: 중복 영어 원본 JAR/멤버")
                    english = json.loads(
                        archive.read(member).decode("utf-8-sig"),
                        object_pairs_hook=strict_object,
                    )
                    if (
                        not isinstance(english, dict)
                        or not english
                        or any(not isinstance(v, str) for v in english.values())
                    ):
                        raise ValueError(f"{mod}: JAR 영어 키/자료형 오류")
                    sources[mod] = english
                    source_jars[mod] = jar
                    evidence_hash(jar, instance, "instance")
        if set(sources) != set(mods):
            raise ValueError("대상 모드의 현재 JAR 영어 원본이 없어요")
        counts["guide_files"] = check_guides(
            source_jars["auroral"], output, evidence_hash
        )
        quest_baseline = json.loads(
            git_bytes("versions/8.1/manifests/ftbquests_english_hashes.json"),
            object_pairs_hook=strict_object,
        )["keys"]
        for mod in mods:
            working = PROJECT_ROOT / "working" / mod
            english = sources[mod]
            work_english = working / "en_us.json"
            if read_json(work_english) != english:
                raise ValueError(f"{mod}: working 영어와 현재 JAR 전체 영어가 달라요")
            evidence_hash(work_english, PROJECT_ROOT, "project")
            relative = f"{PACK}/assets/{mod}/lang/ko_kr.json"
            korean = read_json(output / relative)
            if not isinstance(korean, dict):
                raise ValueError(f"{mod}: 한국어 최상위 자료형 오류")
            if mod == "neovitae":
                counts.update(
                    check_neovitae_book(
                        source_jars[mod], english, korean, evidence_hash
                    )
                )
            elif set(korean) != set(english):
                raise ValueError(f"{mod}: 한국어 전체 키가 현재 영어와 달라요")
            review_path = working / "review.json"
            counts["language_keys"] += check_review(
                mod, read_json(review_path), english, korean
            )
            evidence_hash(review_path, PROJECT_ROOT, "project")
            counts["language_files"] += 1

            chapter = CHAPTERS[mod]
            english_path = f"{QUEST_ROOT}/lang/en_us/chapters/{chapter}.snbt_merged"
            structure_path = f"{QUEST_ROOT}/chapters/{chapter}.snbt"
            target_path = f"overrides/{QUEST_ROOT}/lang/ko_kr/chapters/{chapter}.snbt"
            audit_path = working / "quest_audit.json"
            audit = read_json(audit_path)
            for field, relative, root, prefix in (
                ("english", english_path, instance, "instance"),
                ("structure", structure_path, instance, "instance"),
                ("output", target_path, output, "output"),
            ):
                if audit.get(f"{field}_path") != relative or audit.get(
                    f"{field}_sha256"
                ) != evidence_hash(root / relative, root, prefix):
                    raise ValueError(f"{mod}: 퀘스트 {field} 감사 근거 불일치")
            source = SnbtReader(
                (instance / english_path).read_text(encoding="utf-8-sig")
            ).parse()
            structure = SnbtReader(
                (instance / structure_path).read_text(encoding="utf-8-sig")
            ).parse()
            target = SnbtReader(
                (output / target_path).read_text(encoding="utf-8")
            ).parse()
            if not all(isinstance(v, dict) for v in (source, structure, target)):
                raise ValueError(f"{mod}: 퀘스트 최상위 자료형 오류")
            expected_hashes = {
                key: row["sha256"]
                for key, row in quest_baseline.items()
                if row["file"] == f"chapters/{chapter}.snbt"
            }
            if (
                audit.get("source_layout") != "split_snbt_merged"
                or audit.get("baseline_value_sha256") != expected_hashes
                or {key: value_hash(value) for key, value in source.items()}
                != expected_hashes
            ):
                raise ValueError(f"{mod}: 현재 분할 영어와 고정 기준 키별 해시 불일치")
            old = SnbtReader(
                git_bytes(f"output/8.1/{target_path}").decode("utf-8")
            ).parse()
            if set(source) - set(target) or set(old) - set(target):
                raise ValueError(
                    f"{mod}: 퀘스트 키 삭제는 별도 표시 경로 계약이 필요해요"
                )
            for key in set(target) - set(source):
                if key not in old or old[key] != target[key]:
                    raise ValueError(
                        f"{mod}:{key}: 새 fallback 키의 원문 근거가 필요해요"
                    )
            counts["quest_keys"] += check_review(mod, audit, source, target)
            evidence_hash(audit_path, PROJECT_ROOT, "project")
            counts["quest_files"] += 1
        if release_id == "8.1-stable.4":
            import verify_ad_astra_translation as ad_astra

            additional_family = ad_astra.verify(evidence_hash=evidence_hash)
            for family_counts in additional_family["counts"].values():
                counts["language_keys"] += family_counts["language_keys"]
                counts["language_files"] += 1
                counts["guide_files"] += family_counts.get("guide_files", 0)
                counts["guide_display_strings"] += family_counts.get("guide_strings", 0)
        for relative, expected in inventory.items():
            if sha256(output / relative) != expected:
                raise ValueError(f"검증 중 산출물 변경: {relative}")
    finally:
        if snapshot(instance) != before:
            raise ValueError(
                "검증 중 실제 인스턴스 파일 목록·크기·수정 시각이 바뀌었어요"
            )
    return {
        "schema_version": 1,
        "release": release_id,
        "baseline_commit": BASELINE,
        "mods": list(mods)
        + (list(additional_family["counts"]) if additional_family else []),
        "status": "passed",
        "counts": dict(counts),
        "changed_paths": sorted(changed),
        "unchanged_files": len(set(inventory) - changed),
        "current_jar_english_verified": True,
        "instance_unchanged": True,
        "evidence_sha256": evidence,
        **(
            {"additional_family_counts": additional_family["counts"]}
            if additional_family
            else {}
        ),
    }
