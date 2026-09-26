#!/usr/bin/env python3
"""Logistics Networks의 현재 원문과 검수한 번역·표시 경로를 대조해요."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
from zipfile import ZipFile

import build_ae2_guide as guide
from build_ae2_addon_guides import validate_tag_nesting
from local_paths import PROJECT_ROOT, resolve_source_root
from snapshot_instance import collect
from verify_ad_astra_translation import scan_instance_routes
from verify_compat_release import read_json, sha256, strict_object
from verify_stage1_translation import check_review, check_value

MOD = "logisticsnetworks"
PACK = "resourcepack/ATM10_Korean"
WORK = PROJECT_ROOT / "working" / MOD
GUIDE = f"assets/{MOD}/guides/{MOD}/guide"
REGISTRY = f"assets/{MOD}/guideme_guides/guide.json"
EXTRA_KEYS = ("guide.logisticsnetworks.name", "guide.logisticsnetworks.description")
ANCHORS = {
    "nodes/filters-upgrades.md": "filters",
    "wrench/copy-paste.md": "clipboard-editor",
}
FALLBACKS = {
    "Install Mekanism to unlock this recipe.": "이 제작법을 사용하려면 Mekanism을 설치하세요.",
    "Install Ars Nouveau to unlock this recipe.": "이 제작법을 사용하려면 Ars Nouveau를 설치하세요.",
}
ROUTE_PATTERN = re.compile(r"logistics[ _-]?networks?|물류 노드", re.IGNORECASE)


def allowed_paths():
    """언어 파일과 현재 영어 가이드에 대응하는 경로만 허용해요."""
    paths = {f"{PACK}/assets/{MOD}/lang/ko_kr.json"}
    paths.add(f"{PACK}/{REGISTRY}")
    paths.update(
        f"{PACK}/{GUIDE}/_ko_kr/{p.relative_to(WORK / 'guide/en_us').as_posix()}"
        for p in (WORK / "guide/en_us").rglob("*.md")
    )
    return paths


def check_registry(archive, output, korean, record):
    """직접 표시하던 두 컴포넌트만 번역 키로 연결하고 영어 fallback을 보존해요."""
    original = json.loads(archive.read(REGISTRY), object_pairs_hook=strict_object)
    if original != read_json(WORK / "guide/registry_en_us.json"):
        raise ValueError("가이드 등록 원문 변경")
    review = read_json(WORK / "guide/registry_review.json")
    if tuple(review) != EXTRA_KEYS:
        raise ValueError("가이드 추가 키 범위 불일치")
    components = [
        original["item_settings"]["display_name"],
        *original["item_settings"]["tooltip_lines"],
    ]
    if len(components) != 2:
        raise ValueError("가이드 표시 컴포넌트 수 변경")
    for component, key in zip(components, EXTRA_KEYS):
        text = component.pop("text")
        row = review[key]
        if (
            row["english"] != text
            or row["translation"] != korean[key]
            or row["reviewed"] is not True
        ):
            raise ValueError(f"가이드 등록 검수 불일치: {key}")
        check_value(key, text, korean[key])
        component.update(translate=key, fallback=text)
    if original != read_json(
        WORK / "guide/registry_ko_kr.json"
    ) or original != read_json(output / PACK / REGISTRY):
        raise ValueError("가이드 등록 산출물의 비표시 구조 또는 컴포넌트 변경")
    for name in ("registry_en_us.json", "registry_ko_kr.json", "registry_review.json"):
        record(WORK / "guide" / name, PROJECT_ROOT, "project")
    record(output / PACK / REGISTRY, output, "output")


def check_guides(archive, output, record):
    """전체 페이지와 태그·링크·영문 문단·검수 해시를 검사해요."""
    names = archive.namelist()
    pages = [
        n.removeprefix(f"{GUIDE}/")
        for n in names
        if n.startswith(f"{GUIDE}/")
        and n.endswith(".md")
        and not n.removeprefix(f"{GUIDE}/").startswith("_")
    ]
    review = read_json(WORK / "guide/review.json")
    rows = review["entries"]
    if (
        review["mod"] != MOD
        or review["schema_version"] != 1
        or len(pages) != 17
        or len(set(pages)) != 17
        or len(rows) != 17
        or {r["path"] for r in rows} != set(pages)
    ):
        raise ValueError("GuideME 전체 페이지 목록 또는 검수 범위 불일치")
    for row in rows:
        page = row["path"]
        raw = archive.read(f"{GUIDE}/{page}")
        target_path = output / PACK / GUIDE / "_ko_kr" / page
        target = target_path.read_bytes()
        if (
            row.get("reviewed") is not True
            or row["source_sha256"] != hashlib.sha256(raw).hexdigest()
            or row["target_sha256"] != hashlib.sha256(target).hexdigest()
            or (WORK / "guide/en_us" / page).read_bytes() != raw
            or (WORK / "guide/ko_kr" / page).read_bytes() != target
        ):
            raise ValueError(f"가이드 원문·검수·산출물 불일치: {page}")
        english = raw.decode("utf-8")
        korean = target.decode("utf-8")
        # 현재 NodeScreen.drawChannelTabs는 0 <= index < 9를 그대로 표시해요.
        # 첫 페이지의 오래된 번호 표기 한 곳만 코드에 맞춰 대조해요.
        if page == "index.md":
            if english.count("numbered 1 through 9") != 1:
                raise ValueError("교정 대상 원문이 바뀌었어요")
            english = english.replace("numbered 1 through 9", "numbered 0 through 8")
        comparable = korean
        if page in ANCHORS:
            anchor = f'<a name="{ANCHORS[page]}"></a>\n\n'
            if comparable.count(anchor) != 1:
                raise ValueError(f"번역 제목의 원문 앵커 누락 또는 중복: {page}")
            comparable = comparable.replace(anchor, "")
        if page == "nodes/upgrades-special.md":
            for source, translated in FALLBACKS.items():
                old = f'fallbackText="{source}"'
                new = f'fallbackText="{translated}"'
                if english.count(old) != 1 or comparable.count(new) != 1:
                    raise ValueError("제작법 대체 문구 검수 불일치")
                comparable = comparable.replace(new, old)
        errors = guide.validate_pair(page, english, comparable)
        errors.extend(validate_tag_nesting(page, korean))
        if errors:
            raise ValueError("; ".join(errors))
        check_value(page, english, comparable)
        metadata, _ = guide.split_front_matter(korean)
        title = guide.NAVIGATION_TITLE_RE.search(metadata)[0].split(":", 1)[1].strip()
        if not title or re.search(r"[:#\[\]{}&*!|>\"']", title):
            raise ValueError(f"안전한 단일 YAML 제목이 아니에요: {page}")
        for pattern in (guide.LINK_TARGET_RE, guide.IMAGE_TARGET_RE, guide.IMPORT_RE):
            for match in pattern.finditer(korean):
                reference = match.group(1)
                clean, _, fragment = reference.partition("#")
                if re.match(r"^(?:https?://|mailto:)", clean):
                    continue
                resolved = posixpath.normpath(
                    posixpath.join(posixpath.dirname(page), clean)
                )
                if f"{GUIDE}/{resolved}" not in names:
                    raise ValueError(f"가이드 참조 대상 누락: {page}: {reference}")
                if fragment and ANCHORS.get(resolved) != fragment:
                    raise ValueError(f"번역 가이드 앵커 대상 누락: {reference}")
        for path in (WORK / "guide/en_us" / page, WORK / "guide/ko_kr" / page):
            record(path, PROJECT_ROOT, "project")
        record(target_path, output, "output")
    record(WORK / "guide/review.json", PROJECT_ROOT, "project")
    return len(rows)


def check_routes(instance, archive, record):
    audit_path = WORK / "display_audit.json"
    audit = read_json(audit_path)
    current = scan_instance_routes(instance, ROUTE_PATTERN)
    if any(current[k] != audit[k] for k in current):
        raise ValueError("FTB Quests·KubeJS 표시 경로 조사 결과 변경")
    for relative in current["source_sha256"]:
        record(instance / relative, instance, "instance")
    loader = audit["guide_loader"]
    jar = instance / "mods" / loader["jar"]
    if sha256(jar) != loader["sha256"]:
        raise ValueError("GuideME 로더 버전 변경")
    with ZipFile(jar) as guide_archive:
        for member, digest in loader["classes"].items():
            if hashlib.sha256(guide_archive.read(member)).hexdigest() != digest:
                raise ValueError(f"GuideME 표시 경로 변경: {member}")
    for member, digest in audit["behavior_classes"].items():
        if hashlib.sha256(archive.read(member)).hexdigest() != digest:
            raise ValueError(f"가이드 동작 대조 코드 변경: {member}")
    record(jar, instance, "instance")
    record(audit_path, PROJECT_ROOT, "project")


def verify(*, language_only=False, evidence_hash=None):
    instance = resolve_source_root()
    before = collect(instance)
    output = PROJECT_ROOT / "output/8.1"
    evidence = {}

    def record(path, root, prefix):
        evidence[f"{prefix}/{path.relative_to(root).as_posix()}"] = sha256(path)
        if evidence_hash:
            evidence_hash(path, root, prefix)

    try:
        source = read_json(WORK / "source.json")
        jar = instance / "mods" / source["jar"]
        if sha256(jar) != source["jar_sha256"]:
            raise ValueError("Logistics Networks JAR이 검수 원본과 달라요")
        record(jar, instance, "instance")
        with ZipFile(jar) as archive:
            member = f"assets/{MOD}/lang/en_us.json"
            if archive.namelist().count(member) != 1:
                raise ValueError("영어 언어 멤버가 없거나 중복돼요")
            english = json.loads(archive.read(member), object_pairs_hook=strict_object)
        korean_path = output / PACK / f"assets/{MOD}/lang/ko_kr.json"
        korean = read_json(korean_path)
        expected = set(english)
        if not language_only or set(EXTRA_KEYS) <= set(korean):
            expected.update(EXTRA_KEYS)
        if read_json(WORK / "en_us.json") != english or expected != set(korean):
            raise ValueError("현재 원문 또는 번역 키가 달라요")
        if read_json(WORK / "ko_kr.json") != korean:
            raise ValueError("작업 번역과 배포 번역이 달라요")
        review = read_json(WORK / "review.json")
        keys = check_review(MOD, review, english, korean)
        for name in ("source.json", "en_us.json", "ko_kr.json", "review.json"):
            record(WORK / name, PROJECT_ROOT, "project")
        record(korean_path, output, "output")
        counts = {MOD: {"language_keys": keys}}
        if not language_only:
            with ZipFile(jar) as archive:
                check_registry(archive, output, korean, record)
                counts[MOD]["language_keys"] += len(EXTRA_KEYS)
                counts[MOD]["guide_files"] = check_guides(archive, output, record)
                counts[MOD]["registry_files"] = 1
                check_routes(instance, archive, record)
        return {
            "status": "passed",
            "scope": "language" if language_only else "language_guides_routes",
            "counts": counts,
            "source_sha256": evidence,
        }
    finally:
        if before != collect(instance):
            raise ValueError("검증 중 실제 인스턴스의 파일이 변경됐어요")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language-only", action="store_true")
    args = parser.parse_args()
    report = verify(language_only=args.language_only)
    suffix = "language_validation" if args.language_only else "validation"
    path = PROJECT_ROOT / f"versions/8.1/reports/{MOD}_{suffix}.json"
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
