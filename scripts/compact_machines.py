#!/usr/bin/env python3
"""Compact Machines 언어와 ATM10 연동 표시 문구를 생성하고 검증한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

from five_family_goal import PROJECT_ROOT, load_json, validate_value
from local_paths import resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/compact_machines"
LANG_ROOT = WORK_ROOT / "compactmachines"
LANG_OUTPUT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/compactmachines/lang/ko_kr.json"
)

TRANSLATIONS = {
    "advancement.compactmachines.foundations": "기초",
    "advancement.compactmachines.foundations.desc": "부술 수 있는 벽 블록을 얻으세요.",
    "advancement.compactmachines.got_shrinking_device": "개인 축소 장치",
    "advancement.compactmachines.got_shrinking_device.desc": "개인 축소 장치를 얻으세요",
    "advancement.compactmachines.how_did_you_get_here": "어떻게 여기까지 왔나요?!",
    "advancement.compactmachines.how_did_you_get_here.desc": "플레이어가 어느 머신 안에 있는 걸까요?!",
    "advancement.compactmachines.recursion": "재귀적인 방",
    "advancement.compactmachines.recursion.desc": "재귀를 이해하려면 먼저 재귀를 이해해야 합니다.",
    "advancement.compactmachines.root": "Compact Machines",
    "advancement.compactmachines.root.desc": "",
    "biome.compactmachines.machine": "컴팩트 머신",
    "block.compactmachines.bound_machine_fallback": "컴팩트 머신",
    "block.compactmachines.solid_wall": "견고한 컴팩트 머신 벽",
    "block.compactmachines.wall": "컴팩트 머신 벽",
    "commands.machines.compactmachines.cannot_give_machine_item": "플레이어에게 새 머신 아이템을 지급하지 못했습니다.",
    "commands.machines.compactmachines.machine_given_successfully": "새 머신 아이템을 만들어 %s에게 지급했습니다.",
    "commands.rooms.compactmachines.room_reg_count": "등록된 방 수: %s",
    "commands.rooms.compactmachines.spawn_changed_successfully": "방 [%s]의 생성 지점을 변경했습니다.",
    "compactmachines.connected_block": "연결됨: %s",
    "compactmachines.direction.side": "면: %s",
    "compactmachines.rooms.templates.room_dimensions": "내부 크기: %s",
    "compactmachines.rooms.templates.structure_tooltip": "방을 만들 때 구조물 %s개를 생성합니다.",
    "config.jade.plugin_compactmachines.bound_machine": "연결된 컴팩트 머신",
    "config.jade.plugin_compactmachines.show_owner": "머신 소유자 표시",
    "curios.identifier.psd": "개인 축소 장치",
    "entity.minecraft.villager.compactmachines.tinkerer": "공간 기술자",
    "gamerule.compactmachines.allow_creative_oob": "창작 모드 플레이어의 경계 이탈 허용",
    "gamerule.compactmachines.allow_creative_oob.description": "창작 모드 플레이어가 경계 밖으로 나갈 수 있게 합니다",
    "gamerule.compactmachines.allow_spectator_oob": "관전자 모드 플레이어의 경계 이탈 허용",
    "gamerule.compactmachines.allow_spectator_oob.description": "관전자 모드 플레이어가 경계 밖으로 나갈 수 있게 합니다",
    "gamerule.compactmachines.allow_survival_oob": "생존 모드 플레이어의 경계 이탈 허용",
    "gamerule.compactmachines.allow_survival_oob.description": "생존 모드 플레이어가 경계 밖으로 나갈 수 있게 합니다",
    "gamerule.compactmachines.damage_oob": "경계 밖 플레이어에게 피해",
    "gamerule.compactmachines.damage_oob.description": "경계 밖으로 나간 플레이어에게 피해를 줍니다",
    "gamerule.compactmachines.damage_psd_on_exit": "방을 나갈 때 개인 축소 장치 내구도 감소",
    "gamerule.compactmachines.damage_psd_on_exit.description": "방을 나가면 개인 축소 장치의 내구도가 감소합니다",
    "item.compactmachines.enlarging_module": "원자 확대 모듈",
    "item.compactmachines.personal_shrinking_device": "개인 축소 장치",
    "item.compactmachines.shrinking_module": "원자 축소 모듈",
    "itemGroup.compactmachines.main": "Compact Machines",
    "jei.compactmachines.machines": "머신은 포켓 차원을 만드는 데 사용합니다. 머신을 제작해 월드에 설치한 다음 개인 축소 장치를 사용하면 안으로 들어갈 수 있습니다.",
    "jei.compactmachines.shrinking_device": "컴팩트 공간에 들어가려면 머신에 개인 축소 장치(PSD)를 사용하세요.",
    "key.category.compactmachines.general": "Compact Machines",
    "key.mapping.compactmachines.exit_room": "컴팩트 머신에서 빠르게 나가기",
    "key.mapping.compactmachines.open_upgrade_screen": "방 업그레이드 화면 열기",
    "machine.compactmachines.machine.bound_to": "연결 대상: %1$s",
    "machine.compactmachines.machine.owner": "소유자: %s",
    "machine.compactmachines.machine.size": "내부 크기: %1$s",
    "machine.compactmachines.machine_room_info": "%1$s의 머신이 %3$s에 있는 %2$s 크기의 방과 연결되어 있습니다",
    "machine.compactmachines.new_machine": "새 머신",
    "messages.compactmachines.hint.hold_shift": "자세히 보려면 Shift를 누르세요.",
    "messages.compactmachines.how_did_you_get_here": "어떻게 여기까지 왔나요?!",
    "messages.compactmachines.solid_wall": "경고! 창작 모드가 아니면 부술 수 없습니다!",
    "messages.compactmachines.teleport_oob": "다른 세계의 힘이 순간이동을 막습니다.",
    "rooms.compactmachines.player_room_info": "플레이어 '%1$s'은(는) 방 %2$s 안에 있습니다.",
    "rooms.compactmachines.spawnpoint_set": "새 생성 지점을 설정했습니다.",
    "rooms.errors.compactmachines.cannot_enter": "축소 장치를 만져 보았지만 아무 일도 일어나지 않습니다. 작동을 거부하는 것 같습니다.",
    "rooms.errors.compactmachines.room_not_found": "방 [%s]을(를) 찾을 수 없습니다.",
}

KUBEJS_EXTRA = {
    "machine.compactmachines.colossal": "컴팩트 머신 (초거대형)",
    "machine.compactmachines.giant": "컴팩트 머신 (거대형)",
    "machine.compactmachines.large": "컴팩트 머신 (대형)",
    "machine.compactmachines.normal": "컴팩트 머신 (일반형)",
    "machine.compactmachines.small": "컴팩트 머신 (소형)",
    "machine.compactmachines.tiny": "컴팩트 머신 (초소형)",
    "machine.compactmachines.soaryn": "컴팩트 머신 (Soaryn)",
    "machine.compactmachines.farming": "컴팩트 머신 (농업용)",
}

KUBEJS_OUTPUTS = {
    "startup_scripts/hyperbox/hyperbox.js": (
        "Hyperbox는 6.0 이상 버전에서 제거됩니다. Compact Machines로 옮겨 주세요.",
        'Hyperbox").append(Text.red("가 제거될 예정입니다!',
        "새 모드로 물건을 옮겨 주세요:",
    ),
    "server_scripts/mods/Hyperbox/hyperbox.js": (
        "Hyperbox는 6.0 이상 버전에서 제거됩니다. Compact Machines로 옮겨 주세요.",
    ),
}


def dump_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 안정된 형식으로 기록한다."""
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def normalize() -> dict[str, int]:
    """본체 58키와 ATM10 추가 8키, 퀘스트 제목을 반영한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    if set(english) != set(TRANSLATIONS):
        missing = sorted(set(english) - set(TRANSLATIONS))
        extra = sorted(set(TRANSLATIONS) - set(english))
        raise KeyError(f"번역 표 범위 불일치: missing={missing}, extra={extra}")
    changed = 0
    for key, source in english.items():
        translated = TRANSLATIONS[key]
        errors = validate_value(key, source, translated)
        if errors:
            raise ValueError("; ".join(errors))
        if korean[key] != translated:
            korean[key] = translated
            changed += 1
    dump_json(LANG_ROOT / "ko_kr.json", korean)
    dump_json(WORK_ROOT / "kubejs_extra_ko_kr.json", KUBEJS_EXTRA)

    quest_file = WORK_ROOT / "quests/related/ko_kr.json"
    quests = load_json(quest_file)
    quest_key = "quest.0539AF15A10B2859.title"
    quest_changed = int(quests[quest_key] != "&lCompact Machines")
    quests[quest_key] = "&lCompact Machines"
    dump_json(quest_file, quests)
    return {
        "language_keys": len(english),
        "language_changed": changed,
        "kubejs_extra_keys": len(KUBEJS_EXTRA),
        "quest_keys": len(quests),
        "quest_changed": quest_changed,
    }


def build_extra() -> dict[str, int]:
    """ATM10이 추가한 머신 등급 이름을 본체 언어 출력에 병합한다."""
    output = load_json(LANG_OUTPUT)
    output.update(KUBEJS_EXTRA)
    dump_json(LANG_OUTPUT, output)
    return {
        "base_keys": len(output) - len(KUBEJS_EXTRA),
        "extra_keys": len(KUBEJS_EXTRA),
    }


def named_strings(value: object, names: set[str]) -> list[str]:
    """중첩 JSON에서 지정한 표시 필드의 문자열을 모은다."""
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in names and isinstance(child, str):
                found.append(child)
            found.extend(named_strings(child, names))
    elif isinstance(value, list):
        for child in value:
            found.extend(named_strings(child, names))
    return found


def audit_data() -> tuple[dict[str, object], list[str]]:
    """JAR과 ATM10 KubeJS의 사용자 표시 경로를 검사한다."""
    instance = resolve_source_root()
    jar = next((instance / "mods").glob("compactmachines-neoforge-*.jar"))
    advancements = 0
    advancement_displays = []
    recipes = 0
    recipe_visible = []
    room_templates = 0
    room_template_visible = []
    with ZipFile(jar) as archive:
        for name in archive.namelist():
            if not name.endswith(".json"):
                continue
            if "/advancement/" in name:
                advancements += 1
                data = json.loads(archive.read(name).decode("utf-8"))
                if isinstance(data, dict) and "display" in data:
                    advancement_displays.append(name)
            elif "/recipe/" in name:
                recipes += 1
                data = json.loads(archive.read(name).decode("utf-8"))
                if named_strings(data, {"name", "title", "description", "text"}):
                    recipe_visible.append(name)
            elif "/room_templates/" in name:
                room_templates += 1
                data = json.loads(archive.read(name).decode("utf-8"))
                if named_strings(data, {"name", "title", "description", "text"}):
                    room_template_visible.append(name)

    kubejs_root = instance / "kubejs"
    reference_files = []
    for path in kubejs_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json", ".snbt"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if re.search(r"compact\s*machines|compactmachines", text, re.I):
            reference_files.append(path.relative_to(kubejs_root).as_posix())

    errors = []
    if advancement_displays:
        errors.append("표시 정보가 있는 발전 과제가 남음")
    if recipe_visible:
        errors.append("표시 문구가 있는 조합법이 남음")
    if room_template_visible:
        errors.append("표시 문구가 있는 방 템플릿이 남음")
    for relative, snippets in KUBEJS_OUTPUTS.items():
        output = PROJECT_ROOT / "output/overrides/kubejs" / relative
        if not output.is_file():
            errors.append(f"KubeJS 번역 출력 누락: {relative}")
            continue
        text = output.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"KubeJS 번역 문구 누락: {relative}:{snippet}")
    report = {
        "jar": jar.name,
        "advancements_checked": advancements,
        "advancement_display_entries": len(advancement_displays),
        "recipes_checked": recipes,
        "recipe_visible_field_entries": len(recipe_visible),
        "room_templates_checked": room_templates,
        "room_template_visible_entries": len(room_template_visible),
        "kubejs_reference_files_checked": len(reference_files),
        "kubejs_visible_scripts_translated": len(KUBEJS_OUTPUTS),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    dump_json(WORK_ROOT / "data_audit.json", report)
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """언어·추가 키·퀘스트·데이터 표시 경로를 검사한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    errors = []
    if list(english) != list(korean):
        errors.append("언어 키 또는 순서 불일치")
    allowed = {"Compact Machines", ""}
    for key, source in english.items():
        target = korean[key]
        errors.extend(validate_value(key, source, target))
        if source == target and source not in allowed:
            errors.append(f"미번역: {key}")
    output = load_json(LANG_OUTPUT) if LANG_OUTPUT.is_file() else {}
    for key, target in KUBEJS_EXTRA.items():
        if output.get(key) != target:
            errors.append(f"KubeJS 추가 언어 출력 불일치: {key}")

    quest_root = WORK_ROOT / "quests/related"
    quest_english = load_json(quest_root / "en_us.json")
    quest_korean = load_json(quest_root / "ko_kr.json")
    if list(quest_english) != list(quest_korean):
        errors.append("퀘스트 키 또는 순서 불일치")
    for key, source in quest_english.items():
        target = quest_korean[key]
        errors.extend(validate_value(key, source, target))
        if source == target and source != "&lCompact Machines":
            errors.append(f"미번역 퀘스트: {key}")
    data_report, data_errors = audit_data()
    errors.extend(data_errors)
    report = {
        "language_keys": len(english),
        "kubejs_extra_keys": len(KUBEJS_EXTRA),
        "quest_keys": len(quest_english),
        "data_audit": data_report,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    dump_json(WORK_ROOT / "specialized_validation.json", report)
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("normalize", "build-extra", "verify"))
    args = parser.parse_args()
    if args.command == "normalize":
        report = normalize()
        errors = []
    elif args.command == "build-extra":
        report = build_extra()
        errors = []
    else:
        report, errors = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
