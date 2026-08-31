#!/usr/bin/env python3
"""Waystones 8.1 언어와 관련 표시 경로를 재기준화하고 검증해요."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
import re
from pathlib import Path
from zipfile import ZipFile

import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

FAMILY = "waystones"
MOD_ID = "waystones"
JAR_PATTERN = "waystones-*.jar"
LANGUAGE_PATH = "assets/waystones/lang/en_us.json"
BUNDLED_KOREAN_PATH = "assets/waystones/lang/ko_kr.json"
EXPECTED_KEYS = 356
EXPECTED_REUSED = 257
WORK_ROOT = PROJECT_ROOT / "working/waystones"
BASELINE_PATH = (
    PROJECT_ROOT
    / "output/7.1/resourcepack/ATM10_Korean/assets/waystones/lang/ko_kr.json"
)
OUTPUT_PATH = (
    active_output_root() / "resourcepack/ATM10_Korean/assets/waystones/lang/ko_kr.json"
)
TEXT_SUFFIXES = {".cfg", ".ini", ".js", ".json", ".properties", ".snbt", ".toml"}
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")
RESOURCE_LOCATION = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
TRANSLATION_KEY = re.compile(r"^[a-z0-9_.:-]+$")
VISIBLE_FIELDS = {
    "custom_name",
    "description",
    "message",
    "name",
    "subtitle",
    "text",
    "title",
}

UPGRADE_TRANSLATIONS = {
    "block.waystones.fleeting_memorial": "덧없는 추모비",
    "block.waystones.mud_bricks_waystone": "진흙 웨이스톤",
    "block.waystones.prismarine_waystone": "프리즈머린 웨이스톤",
    "block.waystones.purpur_waystone": "퍼퍼 웨이스톤",
    "block.waystones.red_nether_bricks_waystone": "네더 웨이스톤",
    "block.waystones.warp_portal": "워프 포털",
    "chat.waystones.destination_chunk_load_failed": "목적지를 불러올 수 없습니다.",
    "chat.waystones.destination_out_of_bounds": "목적지가 월드 경계 밖에 있습니다.",
    "chat.waystones.requirements_not_met": "순간이동에 필요한 조건을 충족하지 못했습니다.",
    "chat.waystones.source_item_missing": "순간이동에 사용할 아이템을 더 이상 들고 있지 않습니다.",
    "chat.waystones.source_waystone_out_of_range": "웨이스톤에서 너무 멀리 이동했습니다.",
    "chat.waystones.teleport_failed": "순간이동에 실패했습니다.",
    "chat.waystones.teleport_no_longer_valid": "순간이동을 완료할 수 없습니다.",
    "chat.waystones.warp_portal_attunement_lost": (
        "연결된 대상이 파괴되어 이 포털이 닫혔습니다."
    ),
    "chat.waystones.warp_portal_no_space": "이곳에는 워프 포털을 열 공간이 없습니다.",
    "color.waystones.group.aqua": "청록색",
    "color.waystones.group.black": "검은색",
    "color.waystones.group.blue": "파란색",
    "color.waystones.group.dark_aqua": "짙은 청록색",
    "color.waystones.group.dark_blue": "짙은 파란색",
    "color.waystones.group.dark_gray": "짙은 회색",
    "color.waystones.group.dark_green": "짙은 초록색",
    "color.waystones.group.dark_purple": "짙은 보라색",
    "color.waystones.group.dark_red": "짙은 빨간색",
    "color.waystones.group.gold": "금색",
    "color.waystones.group.gray": "회색",
    "color.waystones.group.green": "초록색",
    "color.waystones.group.light_purple": "밝은 보라색",
    "color.waystones.group.red": "빨간색",
    "color.waystones.group.white": "흰색",
    "color.waystones.group.yellow": "노란색",
    "commands.waystones.twinbound.already_linked": (
        "%s님과 %s님은 이미 쌍둥이 결속 깃털로 연결되어 있습니다"
    ),
    "commands.waystones.twinbound.no_space": (
        "%s님의 인벤토리에 쌍둥이 결속 깃털을 넣을 빈칸이 필요합니다"
    ),
    "commands.waystones.twinbound.same_player": "서로 다른 플레이어 두 명을 선택하세요",
    "commands.waystones.twinbound.success": (
        "%s님과 %s님의 쌍둥이 결속 깃털을 연결했습니다"
    ),
    "container.waystones.edit_group": "그룹 편집",
    "container.waystones.fleeting_memorial": "덧없는 추모비",
    "container.waystones.manage_groups": "그룹 관리",
    "container.waystones.manage_waystones": "웨이스톤 관리",
    "container.waystones.personal_waystone_settings": "%s",
    "container.waystones.waystone_selection": "목적지를 선택하세요",
    "gui.waystones.group_settings.color": "라벨 색상: %s",
    "gui.waystones.group_settings.icon": "아이콘: %s",
    "gui.waystones.manage_groups.create": "그룹 만들기",
    "gui.waystones.manage_groups.hide_group": "기본 제공 그룹 숨기기",
    "gui.waystones.manage_groups.no_groups": "사용할 수 있는 그룹이 없습니다.",
    "gui.waystones.manage_groups.save": "저장",
    "gui.waystones.manage_groups.show_group": "기본 제공 그룹 다시 표시",
    "gui.waystones.manage_groups.unnamed_group": "이름 없는 그룹",
    "gui.waystones.manage_waystones.drag_to_reorder": (
        "끌어서 순서를 바꾸세요. 두 번 클릭하면 맨 위로 이동합니다. Shift를 누른 채 "
        "두 번 클릭하면 맨 아래로 이동합니다."
    ),
    "gui.waystones.personal_waystone_settings.configure_waystone": "웨이스톤 편집",
    "gui.waystones.personal_waystone_settings.favorite": "즐겨찾기",
    "gui.waystones.personal_waystone_settings.no_alias": "별칭 없음",
    "gui.waystones.personal_waystone_settings.no_group": "그룹 없음",
    "gui.waystones.personal_waystone_settings.no_groups_defined": "정의된 그룹 없음",
    "gui.waystones.personal_waystone_settings.save": "저장",
    "gui.waystones.waystone_selection.back": "뒤로",
    "gui.waystones.waystone_selection.edit_personal_settings": "개인 설정",
    "gui.waystones.waystone_selection.epitaph_requirement": "%s",
    "gui.waystones.waystone_selection.manage": "관리",
    "gui.waystones.waystone_selection.no_sharestones_available": (
        "순간이동할 수 있는 같은 종류의 셰어스톤이 없습니다."
    ),
    "gui.waystones.waystone_selection.return_to_portal": "포털로 돌아가기",
    "gui.waystones.waystone_selection.sort": "정렬: %s",
    "gui.waystones.waystone_selection.sort.distance": "거리순",
    "gui.waystones.waystone_selection.sort.manual": "수동",
    "gui.waystones.waystone_selection.sort.name": "이름순",
    "gui.waystones.waystone_selection.twinbound_feather": "%s",
    "gui.waystones.waystone_selection.twinbound_feather_requirement": "%s",
    "gui.waystones.waystone_settings.personal_settings": "개인 설정",
    "gui.waystones.waystone_settings.visibility.sharestones": (
        "같은 종류의 셰어스톤에 표시"
    ),
    "gui.waystones.waystone_settings.visibility.team": "팀에 표시",
    "item.waystones.epitaph": "묘비명",
    "item.waystones.portal_scroll": "포털 주문서",
    "item.waystones.twinbound_feather": "쌍둥이 결속 깃털",
    "waystones.configuration.compatibility.fixVanillaTeleportBug": (
        "바닐라 순간이동 오류 수정"
    ),
    "waystones.configuration.compatibility.fixVanillaTeleportBug.tooltip": (
        "true로 설정하면 바닐라와 다른 모드를 포함한 모든 엔티티 순간이동에 Waystones의 "
        "엔티티 순간이동 패킷 수정 사항을 적용합니다."
    ),
    "waystones.configuration.general.allowEveryoneToManageGlobalWaystones": (
        "모든 플레이어의 전역 웨이스톤 관리 허용"
    ),
    "waystones.configuration.general.allowEveryoneToManageGlobalWaystones.tooltip": (
        "true로 설정하면 모든 플레이어가 전역 웨이스톤을 관리할 수 있습니다."
    ),
    "waystones.configuration.general.allowedVisibilities": (
        "허용할 공개 범위(사용 중단)"
    ),
    "waystones.configuration.general.allowedVisibilities.tooltip": (
        "사용이 중단된 설정입니다. 대신 allowEveryoneToManageGlobalWaystones를 사용하세요."
    ),
    "waystones.configuration.general.defaultVisibility": "기본 공개 범위",
    "waystones.configuration.general.warpPlateCooldownTime": "워프 플레이트 재사용 대기시간",
    "waystones.configuration.general.warpPlateCooldownTime.tooltip": (
        "엔티티가 같은 워프 플레이트에서 다시 순간이동하려면 대상 워프 플레이트에서 "
        "벗어나 있어야 하는 틱 단위 시간입니다."
    ),
    "waystones.configuration.teleports.enableDurability": "내구도 사용",
    "waystones.configuration.teleports.enableDurability.tooltip": (
        "false로 설정하면 워프 스톤의 내구도가 감소하지 않습니다."
    ),
    "waystones.groups.community_hubs": "커뮤니티 중심지",
    "waystones.groups.dimension": "차원",
    "waystones.groups.dimension.minecraft.overworld": "오버월드",
    "waystones.groups.dimension.minecraft.the_end": "엔드",
    "waystones.groups.dimension.minecraft.the_nether": "네더",
    "waystones.groups.dungeons": "던전",
    "waystones.groups.favorites": "즐겨찾기",
    "waystones.groups.global": "전역 웨이스톤",
    "waystones.groups.overworld": "오버월드",
    "waystones.groups.player_homes": "플레이어 집",
    "waystones.groups.players": "플레이어",
    "waystones.groups.resource_sites": "자원 채집지",
    "waystones.groups.teams": "팀",
    "waystones.groups.villages": "마을",
}

PLACEHOLDER_ONLY_KEYS = {
    "container.waystones.personal_waystone_settings",
    "gui.waystones.waystone_selection.epitaph_requirement",
    "gui.waystones.waystone_selection.twinbound_feather",
    "gui.waystones.waystone_selection.twinbound_feather_requirement",
}


def load_json(path: Path) -> dict[str, str]:
    """UTF-8 JSON 객체를 문자열 사전으로 읽어요."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise TypeError(f"문자열 JSON 객체가 아니에요: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 JSON 보고서 또는 언어 파일을 기록해요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def source_jar() -> Path:
    """현재 인스턴스의 Waystones JAR 하나를 찾아요."""
    matches = sorted((resolve_source_root() / "mods").glob(JAR_PATTERN))
    if len(matches) != 1:
        raise FileNotFoundError(f"Waystones JAR 수가 1개가 아니에요: {matches}")
    return matches[0]


def read_jar_language(jar: Path, member: str) -> dict[str, str]:
    """JAR의 언어 파일 하나를 읽어요."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read(member))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise TypeError(f"문자열 언어 파일이 아니에요: {jar.name}:{member}")
    return value


def prepare() -> dict[str, object]:
    """현재 영어 원문과 후보, 7.1 재사용 원본을 기록해요."""
    jar = source_jar()
    english = read_jar_language(jar, LANGUAGE_PATH)
    bundled = read_jar_language(jar, BUNDLED_KOREAN_PATH)
    baseline = load_json(BASELINE_PATH)
    write_json(WORK_ROOT / "en_us.json", english)
    write_json(WORK_ROOT / "bundled_ko_kr.json", bundled)
    report = {
        "family": FAMILY,
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_mtime_ns": jar.stat().st_mtime_ns,
        "english_keys": len(english),
        "bundled_korean_keys": len(bundled),
        "baseline_korean_keys": len(baseline),
        "upgrade_review_keys": len(UPGRADE_TRANSLATIONS),
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", report)
    return report


def build() -> dict[str, object]:
    """검토된 7.1 번역과 8.1 변경분을 합쳐 현재 키 구조를 만들어요."""
    english = load_json(WORK_ROOT / "en_us.json")
    baseline = load_json(BASELINE_PATH)
    if len(english) != EXPECTED_KEYS:
        raise ValueError(f"현재 영어 키 수가 달라요: {len(english)} != {EXPECTED_KEYS}")
    if len(UPGRADE_TRANSLATIONS) != 99:
        raise ValueError(f"8.1 검토 키 수가 달라요: {len(UPGRADE_TRANSLATIONS)} != 99")
    missing_review = sorted(set(UPGRADE_TRANSLATIONS) - set(english))
    if missing_review:
        raise ValueError(f"현재 원문에 없는 8.1 검토 키가 있어요: {missing_review}")
    korean = {}
    reused = 0
    missing = []
    for key in english:
        if key in UPGRADE_TRANSLATIONS:
            korean[key] = UPGRADE_TRANSLATIONS[key]
        elif key in baseline:
            korean[key] = baseline[key]
            reused += 1
        else:
            missing.append(key)
    if missing or reused != EXPECTED_REUSED:
        raise ValueError(f"재사용 구조가 달라요: missing={missing}, reused={reused}")
    write_json(WORK_ROOT / "ko_kr.json", korean)
    write_json(OUTPUT_PATH, korean)
    report = {
        "reviewed_language_keys": len(korean),
        "existing_korean_reused": reused,
        "changed_source_translations": 4,
        "new_language_translations": 95,
        "removed_output_only_keys": 2,
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def visible_literals(value: object, path: str = "") -> list[str]:
    """데이터 JSON의 직접 표시 문자열 후보를 찾아요."""
    rows = []
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}/{key}"
            if key in VISIBLE_FIELDS and isinstance(item, str):
                if (
                    LATIN_WORD.search(item)
                    and not RESOURCE_LOCATION.fullmatch(item)
                    and not TRANSLATION_KEY.fullmatch(item)
                ):
                    rows.append(f"{child_path}={item}")
            rows.extend(visible_literals(item, child_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(visible_literals(item, f"{path}/{index}"))
    return rows


def scan_instance_references(instance: Path) -> tuple[dict[str, object], list[str]]:
    """FTB Quests와 KubeJS의 Waystones 직접 표시 후보를 검사해요."""
    result = {}
    errors = []
    display_tokens = (
        "custom_name",
        "description",
        "display",
        "lore",
        "name",
        "text",
        "title",
    )
    for label, root in (
        ("ftbquests", instance / "config/ftbquests"),
        ("kubejs", instance / "kubejs"),
    ):
        files = []
        direct_display_lines = []
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeDecodeError) as exc:
                errors.append(f"{path.relative_to(instance).as_posix()}: {exc}")
                continue
            lowered = text.lower()
            if "waystones:" not in lowered and "waystones" not in lowered:
                continue
            relative = path.relative_to(instance).as_posix()
            files.append(relative)
            for number, line in enumerate(text.splitlines(), 1):
                lowered_line = line.lower()
                if (
                    "waystones:" in lowered_line or "waystones" in lowered_line
                ) and any(token in lowered_line for token in display_tokens):
                    direct_display_lines.append(f"{relative}:{number}:{line.strip()}")
        result[label] = {
            "reference_files": files,
            "direct_display_lines": direct_display_lines,
        }
    return result, errors


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR 데이터와 인스턴스의 FTB Quests·KubeJS 노출 경로를 감사해요."""
    jar = source_jar()
    errors = []
    data_counts: dict[str, int] = defaultdict(int)
    literals = []
    parse_errors = []
    with ZipFile(jar) as archive:
        for name in archive.namelist():
            if not name.startswith("data/") or not name.endswith(".json"):
                continue
            category = "other"
            if "/advancement" in name:
                category = "advancement"
            elif "/recipe" in name:
                category = "recipe"
            data_counts[category] += 1
            try:
                payload = json.loads(archive.read(name))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                parse_errors.append(f"{name}: {exc}")
                continue
            for row in visible_literals(payload):
                literals.append(f"{name}:{row}")
    references, read_errors = scan_instance_references(resolve_source_root())
    errors.extend(parse_errors)
    errors.extend(read_errors)
    report = {
        "family": FAMILY,
        "jar": jar.name,
        "data_json_counts": dict(data_counts),
        "direct_visible_data_literals": literals,
        "instance_references": references,
        "parse_errors": parse_errors,
        "read_errors": read_errors,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """키·값·자리표시자·충돌·산출물 일치를 검증해요."""
    english = load_json(WORK_ROOT / "en_us.json")
    korean = load_json(WORK_ROOT / "ko_kr.json")
    output = load_json(OUTPUT_PATH)
    errors = []
    if list(english) != list(korean):
        errors.append("영어와 한국어의 키 또는 순서가 달라요")
    if output != korean:
        errors.append("작업본과 리소스팩 산출물이 달라요")
    if len(korean) != EXPECTED_KEYS:
        errors.append(f"한국어 키 수가 달라요: {len(korean)} != {EXPECTED_KEYS}")
    if set(UPGRADE_TRANSLATIONS) - set(korean):
        errors.append("8.1 확정 번역 키가 산출물에서 빠졌어요")
    validation_errors = []
    for key in english.keys() & korean.keys():
        validation_errors.extend(
            family_goal.validate_value(key, english[key], korean[key])
        )
        if key in UPGRADE_TRANSLATIONS and korean[key] != UPGRADE_TRANSLATIONS[key]:
            validation_errors.append(f"8.1 확정 번역값 불일치: {key}")
        if (
            key in UPGRADE_TRANSLATIONS
            and key not in PLACEHOLDER_ONLY_KEYS
            and english[key] == korean[key]
            and LATIN_WORD.search(english[key])
        ):
            validation_errors.append(f"8.1 검토 키가 영어와 같아요: {key}")
    errors.extend(validation_errors)
    name_groups: dict[str, list[str]] = defaultdict(list)
    for key, target in korean.items():
        if key.startswith(("block.", "item.")):
            name_groups[target].append(key)
    collisions = {
        target: keys
        for target, keys in name_groups.items()
        if len(keys) > 1 and len({english[key] for key in keys}) > 1
    }
    if collisions:
        errors.append(f"서로 다른 검색명이 충돌해요: {collisions}")
    audit_path = WORK_ROOT / "surface_audit.json"
    audit_status = None
    if audit_path.is_file():
        audit_status = json.loads(audit_path.read_text(encoding="utf-8")).get("status")
        if audit_status != "complete":
            errors.append("표시 경로 감사가 완료되지 않았어요")
    report = {
        "family": FAMILY,
        "language_keys": len(korean),
        "existing_korean_reused": EXPECTED_REUSED,
        "upgrade_review_keys": len(UPGRADE_TRANSLATIONS),
        "untranslated_upgrade_keys": 0,
        "translation_induced_name_collisions": len(collisions),
        "surface_audit": audit_status,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "build", "audit", "verify"))
    args = parser.parse_args()
    if args.command == "prepare":
        report, errors = prepare(), []
    elif args.command == "build":
        report, errors = build(), []
    elif args.command == "audit":
        report, errors = audit()
    else:
        report, errors = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
