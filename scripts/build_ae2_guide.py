#!/usr/bin/env python3
"""AE2 내장 가이드 첫 번역 배치를 검증해 누적 리소스팩에 만든다."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import zipfile
from pathlib import Path, PurePosixPath

from local_paths import resolve_source_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKING_ROOT = PROJECT_ROOT / "working/ae2/ae2guide/_ko_kr"
OUTPUT_ROOT = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/ae2/ae2guide/_ko_kr"
)
PROGRESS_FILE = PROJECT_ROOT / "working/ae2/guide_progress.json"
SOURCE_ROOT = PurePosixPath("assets/ae2/ae2guide")

ACTIVE_BATCH = 12
BATCHES = {
    1: (
        "index.md",
        "getting-started.md",
        "tips-and-tricks.md",
        "ae2-mechanics/meteorites.md",
        "ae2-mechanics/certus-growth.md",
    ),
    2: (
        "ae2-mechanics/ae2-mechanics-index.md",
        "ae2-mechanics/bytes-and-types.md",
        "ae2-mechanics/devices.md",
        "ae2-mechanics/energy.md",
        "ae2-mechanics/import-export-storage.md",
        "ae2-mechanics/me-network-connections.md",
        "ae2-mechanics/cable-subparts.md",
    ),
    3: (
        "ae2-mechanics/channels.md",
        "ae2-mechanics/subnetworks.md",
        "ae2-mechanics/p2p-tunnels.md",
        "ae2-mechanics/quantum-bridge.md",
        "ae2-mechanics/spatial-io.md",
    ),
    4: ("ae2-mechanics/autocrafting.md",),
    5: (
        "example-setups/advanced-certus-farm.md",
        "example-setups/semiauto-certus-farm.md",
        "example-setups/simple-certus-farm.md",
        "example-setups/amethyst-farm.md",
    ),
    6: (
        "example-setups/bucket-emptier.md",
        "example-setups/bucket-filler.md",
        "example-setups/cell-dumper-filler.md",
        "example-setups/interface-autostocking.md",
        "example-setups/level-emitter-autostocking.md",
        "example-setups/pipe-subnet.md",
        "example-setups/specialized-local-storage.md",
        "example-setups/storage-types.md",
    ),
    7: (
        "example-setups/example-setups-index.md",
        "example-setups/charger-automation.md",
        "example-setups/furnace-automation.md",
        "example-setups/main-network.md",
        "example-setups/ore-fortuner.md",
        "example-setups/processor-automation.md",
        "example-setups/recursive-crafting-setup.md",
        "example-setups/regulated-cobble-gen.md",
        "example-setups/throw-in-water-automation.md",
    ),
    8: (
        "items-blocks-machines/items-blocks-machines-index.md",
        "items-blocks-machines/budding_certus.md",
        "items-blocks-machines/certus_quartz_crystal.md",
        "items-blocks-machines/certus_quartz_crystal_charged.md",
        "items-blocks-machines/certus_quartz_dust.md",
        "items-blocks-machines/crystal_resonance_generator.md",
        "items-blocks-machines/decorative_certus.md",
        "items-blocks-machines/decorative_fluix.md",
        "items-blocks-machines/decorative_sky_stone.md",
        "items-blocks-machines/ender_dust.md",
        "items-blocks-machines/fluix_block.md",
        "items-blocks-machines/fluix_crystal.md",
        "items-blocks-machines/fluix_dust.md",
        "items-blocks-machines/fluix_pearl.md",
        "items-blocks-machines/fluix_researcher.md",
        "items-blocks-machines/illuminated_panels.md",
        "items-blocks-machines/matter_ball.md",
        "items-blocks-machines/mysterious_cube.md",
        "items-blocks-machines/presses.md",
        "items-blocks-machines/processors.md",
        "items-blocks-machines/quartz_block.md",
        "items-blocks-machines/quartz_fixture.md",
        "items-blocks-machines/quartz_glass.md",
        "items-blocks-machines/singularities.md",
        "items-blocks-machines/sky_dust.md",
        "items-blocks-machines/sky_stone.md",
        "items-blocks-machines/tiny_tnt.md",
    ),
    9: (
        "items-blocks-machines/cutting_knives.md",
        "items-blocks-machines/matter_cannon.md",
        "items-blocks-machines/fluix_upgrade_smithing_template.md",
        "items-blocks-machines/meteorite_compass.md",
        "items-blocks-machines/spatial_cells.md",
        "items-blocks-machines/guide.md",
        "items-blocks-machines/patterns.md",
        "items-blocks-machines/color_applicator.md",
        "items-blocks-machines/wireless_receiver.md",
        "items-blocks-machines/network_tool.md",
        "items-blocks-machines/charged_staff.md",
        "items-blocks-machines/quartz_tools.md",
        "items-blocks-machines/wrench.md",
        "items-blocks-machines/fluix_tools.md",
        "items-blocks-machines/wireless_terminals.md",
        "items-blocks-machines/upgrade_cards.md",
        "items-blocks-machines/paintballs.md",
        "items-blocks-machines/view_cell.md",
        "items-blocks-machines/storage_cells.md",
        "items-blocks-machines/entropy_manipulator.md",
        "items-blocks-machines/memory_card.md",
    ),
    10: (
        "items-blocks-machines/cable_anchor.md",
        "items-blocks-machines/cables.md",
        "items-blocks-machines/p2p_tunnels.md",
        "items-blocks-machines/controller.md",
        "items-blocks-machines/energy_acceptor.md",
        "items-blocks-machines/energy_cells.md",
        "items-blocks-machines/facades.md",
        "items-blocks-machines/quantum_bridge.md",
        "items-blocks-machines/quartz_fiber.md",
        "items-blocks-machines/spatial_anchor.md",
        "items-blocks-machines/spatial_io_port.md",
        "items-blocks-machines/spatial_pylon.md",
        "items-blocks-machines/toggle_bus.md",
        "items-blocks-machines/vibration_chamber.md",
        "items-blocks-machines/wireless_access_point.md",
    ),
    11: (
        "items-blocks-machines/formation_annihilation_core.md",
        "items-blocks-machines/cell_workbench.md",
        "items-blocks-machines/charger.md",
        "items-blocks-machines/condenser.md",
        "items-blocks-machines/crank.md",
        "items-blocks-machines/growth_accelerator.md",
        "items-blocks-machines/inscriber.md",
        "items-blocks-machines/molecular_assembler.md",
        "items-blocks-machines/sky_stone_tank.md",
    ),
    12: (
        "items-blocks-machines/formation_plane.md",
        "items-blocks-machines/annihilation_plane.md",
        "items-blocks-machines/chest.md",
        "items-blocks-machines/drive.md",
        "items-blocks-machines/import_bus.md",
        "items-blocks-machines/export_bus.md",
        "items-blocks-machines/io_port.md",
        "items-blocks-machines/monitors.md",
        "items-blocks-machines/storage_bus.md",
    ),
}
BATCH_FILES = tuple(
    relative for batch in range(1, ACTIVE_BATCH + 1) for relative in BATCHES[batch]
)

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---(?=\n)", re.DOTALL)
NAVIGATION_TITLE_RE = re.compile(r"(?m)^  title:.*$")
TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_TARGET_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
IMAGE_TARGET_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
VISIBLE_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\([^)]+\)")
VISIBLE_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]+\)")
IMPORT_RE = re.compile(r'<ImportStructure\b[^>]*src="([^"]+)"')
HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+")
ENGLISH_WORD_RE = re.compile(r"\b[A-Za-z]+(?:['’][A-Za-z]+)?\b")


def find_ae2_jar(instance: Path) -> Path:
    jars = sorted((instance / "mods").glob("appliedenergistics2-*.jar"))
    if len(jars) != 1:
        raise ValueError(
            f"AE2 JAR을 하나로 확정할 수 없습니다: {[p.name for p in jars]}"
        )
    return jars[0]


def load_source(archive: zipfile.ZipFile, relative: str) -> str:
    entry = (SOURCE_ROOT / relative).as_posix()
    return archive.read(entry).decode("utf-8-sig")


def split_front_matter(text: str) -> tuple[str, str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError("YAML front matter를 찾을 수 없습니다.")
    return match.group(1), text[match.end() :]


def protected_front_matter(value: str) -> str:
    matches = NAVIGATION_TITLE_RE.findall(value)
    if len(matches) != 1:
        raise ValueError("navigation.title을 하나로 확정할 수 없습니다.")
    return NAVIGATION_TITLE_RE.sub("  title: __TRANSLATED_TITLE__", value)


def extract_visible_text(text: str) -> str:
    metadata, body = split_front_matter(text)
    title_match = NAVIGATION_TITLE_RE.search(metadata)
    title = title_match.group(0).split(":", 1)[1].strip() if title_match else ""
    body = INLINE_CODE_RE.sub(" ", body)
    body = VISIBLE_IMAGE_RE.sub(lambda match: f" {match.group(1)} ", body)
    body = VISIBLE_LINK_RE.sub(lambda match: f" {match.group(1)} ", body)
    body = TAG_RE.sub(" ", body)
    body = re.sub(r"[#>*_~|=]+", " ", body)
    return re.sub(r"\s+", " ", f"{title} {body}").strip()


def english_paragraph_candidates(text: str) -> list[str]:
    _, body = split_front_matter(text)
    candidates = []
    for paragraph in re.split(r"\n\s*\n", body):
        visible = INLINE_CODE_RE.sub(" ", paragraph)
        visible = VISIBLE_IMAGE_RE.sub(lambda match: f" {match.group(1)} ", visible)
        visible = VISIBLE_LINK_RE.sub(lambda match: f" {match.group(1)} ", visible)
        visible = TAG_RE.sub(" ", visible)
        visible = re.sub(r"[#>*_~|=]+", " ", visible)
        visible = re.sub(r"\s+", " ", visible).strip()
        if "가-힣" in visible:
            continue
        if re.search(r"[가-힣]", visible):
            continue
        if len(ENGLISH_WORD_RE.findall(visible)) >= 4:
            candidates.append(visible)
    return candidates


def resolve_reference(page: str, target: str) -> str | None:
    clean = target.split("#", 1)[0].split("?", 1)[0]
    if not clean or re.match(r"^(?:https?://|mailto:)", clean):
        return None
    combined = (SOURCE_ROOT / PurePosixPath(page).parent / clean).as_posix()
    return posixpath.normpath(combined)


def validate_references(
    archive_names: set[str], relative: str, translated: str
) -> list[str]:
    errors = []
    targets = [
        *(match.group(1) for match in LINK_TARGET_RE.finditer(translated)),
        *(match.group(1) for match in IMAGE_TARGET_RE.finditer(translated)),
        *(match.group(1) for match in IMPORT_RE.finditer(translated)),
    ]
    for target in targets:
        resolved = resolve_reference(relative, target)
        if resolved and resolved not in archive_names:
            errors.append(f"{relative}: 참조 대상이 없습니다: {target} -> {resolved}")
    return errors


def validate_pair(relative: str, source: str, translated: str) -> list[str]:
    errors = []
    try:
        source_meta, _ = split_front_matter(source)
        translated_meta, _ = split_front_matter(translated)
        if protected_front_matter(source_meta) != protected_front_matter(
            translated_meta
        ):
            errors.append(
                f"{relative}: navigation.title 외 front matter가 변경됐습니다."
            )
    except ValueError as exc:
        errors.append(f"{relative}: {exc}")

    checks = (
        ("GuideME/HTML 태그", TAG_RE.findall(source), TAG_RE.findall(translated)),
        (
            "인라인 코드",
            INLINE_CODE_RE.findall(source),
            INLINE_CODE_RE.findall(translated),
        ),
        (
            "Markdown 링크",
            LINK_TARGET_RE.findall(source),
            LINK_TARGET_RE.findall(translated),
        ),
        (
            "이미지 참조",
            IMAGE_TARGET_RE.findall(source),
            IMAGE_TARGET_RE.findall(translated),
        ),
        ("제목 단계", HEADING_RE.findall(source), HEADING_RE.findall(translated)),
    )
    for label, expected, actual in checks:
        if expected != actual:
            errors.append(f"{relative}: {label}의 순서 또는 값이 원문과 다릅니다.")

    if source.count("\n---\n") != translated.count("\n---\n"):
        errors.append(f"{relative}: 수평선 또는 front matter 경계 개수가 다릅니다.")
    if not re.search(r"[가-힣]", extract_visible_text(translated)):
        errors.append(f"{relative}: 한국어 본문을 찾을 수 없습니다.")
    candidates = english_paragraph_candidates(translated)
    if candidates:
        errors.append(f"{relative}: 영어 문단 후보가 남았습니다: {candidates[:3]}")
    return errors


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(instance: Path) -> dict[str, object]:
    jar = find_ae2_jar(instance)
    expected_files = set(BATCH_FILES)
    actual_files = {
        path.relative_to(WORKING_ROOT).as_posix()
        for path in WORKING_ROOT.rglob("*.md")
        if path.is_file()
    }
    if actual_files != expected_files:
        raise ValueError(
            f"작업본 파일 목록이 다릅니다: 누락={sorted(expected_files - actual_files)}, "
            f"불필요={sorted(actual_files - expected_files)}"
        )

    errors = []
    source_words = 0
    source_characters = 0
    batch_source_words = 0
    with zipfile.ZipFile(jar) as archive:
        archive_names = set(archive.namelist())
        for relative in BATCH_FILES:
            source = load_source(archive, relative)
            translated = (WORKING_ROOT / relative).read_text(encoding="utf-8")
            errors.extend(validate_pair(relative, source, translated))
            errors.extend(validate_references(archive_names, relative, translated))
            visible = extract_visible_text(source)
            words = len(ENGLISH_WORD_RE.findall(visible))
            source_words += words
            source_characters += len(visible)
            if relative in BATCHES[ACTIVE_BATCH]:
                batch_source_words += words
    if errors:
        raise ValueError("\n".join(errors))

    for relative in BATCH_FILES:
        source = WORKING_ROOT / relative
        target = OUTPUT_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())

    output_files = {
        path.relative_to(OUTPUT_ROOT).as_posix()
        for path in OUTPUT_ROOT.rglob("*.md")
        if path.is_file()
    }
    if output_files != expected_files:
        raise ValueError("출력 가이드 파일 목록이 첫 배치와 다릅니다.")

    result = {
        "scope": f"Applied Energistics 2 GuideME guide batches 01-{ACTIVE_BATCH:02d}",
        "source_jar": jar.name,
        "language": "ko_kr",
        "batch": ACTIVE_BATCH,
        "batch_files": list(BATCHES[ACTIVE_BATCH]),
        "batch_pages": len(BATCHES[ACTIVE_BATCH]),
        "batch_source_words": batch_source_words,
        "files": list(BATCH_FILES),
        "pages": len(BATCH_FILES),
        "source_words": source_words,
        "source_characters": source_characters,
        "existing_korean_reused": 0,
        "newly_translated": len(BATCH_FILES),
        "remaining_core_pages": 125 - len(BATCH_FILES),
        "working_root": WORKING_ROOT.relative_to(PROJECT_ROOT).as_posix(),
        "output_root": OUTPUT_ROOT.relative_to(PROJECT_ROOT).as_posix(),
        "output_sha256": {
            relative: sha256(OUTPUT_ROOT / relative) for relative in BATCH_FILES
        },
        "validation_errors": 0,
        "status": "completed",
    }
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    result = build(resolve_source_root(args.instance))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
