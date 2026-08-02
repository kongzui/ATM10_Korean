#!/usr/bin/env python3
"""Pylons 언어와 관련 FTB Quests 표시 문구를 번역하고 검증한다."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
from pathlib import Path
from zipfile import ZipFile

import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root


FAMILY = "pylons"
WORK_ROOT = PROJECT_ROOT / "working/pylons"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[A-Za-z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[&§][0-9A-FK-ORa-fk-or]")

LANG_TRANSLATIONS = {
    "block.pylons.expulsion_pylon": "추방 파일런",
    "block.pylons.harvester_pylon": "수확 파일런",
    "block.pylons.infusion_pylon": "주입 파일런",
    "block.pylons.interdiction_pylon": "차단 파일런",
    "block.pylons.protection_pylon": "보호 파일런",
    "chat.pylons.expelled": "%s 님의 청크에서 추방되었습니다!",
    "gui.pylons.blockedMobs": "생성을 막을 몹 추가:",
    "gui.pylons.effects": "활성 물약 효과:",
    "gui.pylons.energyMissing": "동력이 부족합니다.",
    "gui.pylons.fluxBar": "레드스톤 플럭스:",
    "gui.pylons.fluxData": "%d/%d RF 저장됨",
    "gui.pylons.insideWorldSpawn": "월드 시작 지점과 너무 가깝습니다.",
    "gui.pylons.inventoryFull": "인벤토리가 가득 찼습니다.",
    "gui.pylons.inventoryMissing": "파일런 위에 인벤토리를 놓으세요.",
    "gui.pylons.noOwner": "소유자를 찾을 수 없어 파일런을 비활성화했습니다.",
    "gui.pylons.owner": "소유자: %s",
    "gui.pylons.protectedMobsAndBlocks": "보호할 몹 또는 블록 추가:",
    "gui.pylons.toggleWork": "작동 상태",
    "gui.pylons.toolMissing": "작동하려면 괭이가 필요합니다.",
    "gui.pylons.whitelist": "허용 목록에 플레이어 추가:",
    "gui.pylons.workArea": "작업 영역(청크)",
    "gui.pylons.workAreaBlocks": "작업 영역(블록)",
    "gui.pylons.working": "파일런이 작동 중입니다.",
    "gui.pylons.wrongDimension": "이 차원에서는 사용할 수 없습니다.",
    "item.pylons.block_filter": "블록 필터",
    "item.pylons.lifeless_filter": "무생명 필터",
    "item.pylons.mob_filter": "몹 필터",
    "item.pylons.player_filter": "플레이어 필터",
    "item.pylons.potion_filter": "물약 필터",
    "itemGroup.pylons": "Pylons",
    "pylons.configuration.expulsionAllowedDimensions": "허용 차원",
    "pylons.configuration.expulsionPylonCanExplode": "폭발 가능",
    "pylons.configuration.expulsionPylonMaxRadius": "최대 반경",
    "pylons.configuration.expulsionWorldSpawnRadius": "월드 시작 지점 반경",
    "pylons.configuration.expulsion_pylon": "추방 파일런",
    "pylons.configuration.general": "일반",
    "pylons.configuration.harvesterCanBeAutomated": "자동화 가능",
    "pylons.configuration.harvesterPowerBuffer": "동력 버퍼",
    "pylons.configuration.harvesterPowerCost": "동력 소모량",
    "pylons.configuration.harvesterRequiresPower": "동력 필요",
    "pylons.configuration.harvesterRequiresTool": "도구 필요",
    "pylons.configuration.harvesterWorkDelay": "작업 간격",
    "pylons.configuration.harvester_pylon": "수확 파일런",
    "pylons.configuration.infusionAllowedEffects": "허용 효과",
    "pylons.configuration.infusionAppliedDuration": "적용 효과 지속 시간",
    "pylons.configuration.infusionChunkloads": "청크 로더로 작동",
    "pylons.configuration.infusionDeniedEffects": "차단 효과",
    "pylons.configuration.infusionMaximumPotency": "최대 효과 단계",
    "pylons.configuration.infusionMinimumDuration": "최소 효과 지속 시간",
    "pylons.configuration.infusionRequiredDuration": "필요한 효과 지속 시간",
    "pylons.configuration.infusion_pylon": "주입 파일런",
    "pylons.configuration.teamSupportEnabled": "팀 지원 활성화",
    "pylons.int.jei.category.expulsion_pylon": (
        "선택한 청크 범위(1x1~5x5청크)에서 다른 플레이어를 추방합니다.\n"
        "플레이어 필터로 허용 목록에 플레이어를 추가할 수 있습니다.\n\n"
        "OP는 자동으로 허용됩니다.\n\n"
        "팀 지원을 켜면 팀원도 자동으로 허용됩니다.\n\n"
        "레드스톤으로 자동 전환할 수 있습니다.\n"
    ),
    "pylons.int.jei.category.harvester_pylon": (
        "파일런 주변 범위(3x3~9x9블록)의 작물을 수확해 위쪽 인벤토리로 보냅니다.\n"
        "농장의 물 블록 안이나 작물과 같은 높이에 놓으세요.\n\n"
        "기본 설정에서는 파일런에 괭이가 필요하며 수확마다 내구도 1을 사용합니다.\n"
        "파괴 불가 괭이는 내구도를 쓰지 않으며 내구성 마법 부여도 적용됩니다.\n\n"
        "설정에서 내구도 대신 동력을 사용하게 바꿀 수 있습니다.\n\n"
        "레드스톤으로 자동 전환할 수 있습니다.\n"
    ),
    "pylons.int.jei.category.infusion_pylon": (
        "활성화한 물약 필터의 효과를 거리와 관계없이 자신에게 적용합니다.\n"
        "기본 설정에서는 소유자가 접속해 있는 동안 설치된 청크를 불러옵니다.\n\n"
        "자신에게 물약 효과를 적용한 뒤\n필터를 들고 우클릭하면 효과를 추출해 필터를 "
        "활성화합니다.\n\n"
        "기본 설정에서 추출 가능한 최소 지속 시간은 60초이며,\n필터를 활성화하려면 "
        "지속 시간 1시간이 필요합니다.\n\n"
        "같은 물약 필터를 양손에 하나씩 들고 우클릭하면 합칠 수 있습니다.\n\n"
        "레드스톤으로 자동 전환할 수 있습니다.\n"
    ),
    "pylons.int.jei.category.interdiction_pylon": (
        "선택한 청크 범위(1x1~5x5청크)에서 지정한 몹의 자연 생성과 강제 생성을 "
        "막습니다.\n몹 필터로 막을 몹을 지정하세요.\n\n"
        "무생명 필터를 쓰면 훨씬 넓은 범위에서 모든 몹의 자연 생성만 막습니다.\n\n"
        "레드스톤으로 자동 전환할 수 있습니다.\n"
    ),
    "pylons.int.jei.category.protection_pylon": (
        "선택한 청크 범위(1x1~5x5청크)에서 파일런 소유자가 블록을 부수거나 몹을 죽이는 "
        "실수를 막습니다.\n몹 필터와 블록 필터로 보호할 대상을 지정하세요.\n\n"
        "레드스톤으로 자동 전환할 수 있습니다.\n"
    ),
    "tooltip.pylons.activated": "활성화됨",
    "tooltip.pylons.effect_banned": "태그로 비활성화된 효과입니다.",
    "tooltip.pylons.effect_denied": "설정에서 비활성화된 효과입니다.",
    "tooltip.pylons.expulsion": "추방 파일런에 사용합니다.",
    "tooltip.pylons.expulsion1": "파일런 주변의 설정 가능한",
    "tooltip.pylons.expulsion2": "청크 범위에서 다른 플레이어를",
    "tooltip.pylons.expulsion3": "추방합니다.",
    "tooltip.pylons.harvester1": "파일런 주변의 설정 가능한",
    "tooltip.pylons.harvester2": "블록 범위에서 작물을 수확합니다.",
    "tooltip.pylons.harvester3": "물 블록 안이나 위에 놓으세요.",
    "tooltip.pylons.increase1": "같은 효과가 활성화된 상태에서",
    "tooltip.pylons.increase2": "우클릭하면 진행도가 늘어납니다.",
    "tooltip.pylons.infusion": "주입 파일런에 사용합니다.",
    "tooltip.pylons.infusion1": "활성화한 물약 필터의 효과를",
    "tooltip.pylons.infusion2": "거리와 관계없이",
    "tooltip.pylons.infusion3": "적용합니다.",
    "tooltip.pylons.insert1": "사용하려면 이 필터를",
    "tooltip.pylons.insert2": "파일런에 넣으세요!",
    "tooltip.pylons.interdiction": "차단 파일런에 사용합니다.",
    "tooltip.pylons.interdiction1": "파일런 주변의 설정 가능한 청크에서",
    "tooltip.pylons.interdiction2": "몹 생성을 막습니다.",
    "tooltip.pylons.lifeless1": "범위 안의 자연 생성을 막습니다.",
    "tooltip.pylons.lifeless2": "범위를 25x25청크로 늘립니다.",
    "tooltip.pylons.lifeless3": "다른 몹 필터를 비활성화합니다.",
    "tooltip.pylons.minimum_duration": "최소 효과 지속 시간: %s초",
    "tooltip.pylons.no_block": "블록을 우클릭해 선택하세요.",
    "tooltip.pylons.no_effect1": "효과가 활성화된 상태에서 우클릭해",
    "tooltip.pylons.no_effect2": "필터에 적용하세요.",
    "tooltip.pylons.no_mob": "몹을 우클릭해 선택하세요.",
    "tooltip.pylons.no_player": "플레이어를 우클릭해 선택하세요.",
    "tooltip.pylons.player": "플레이어: %s",
    "tooltip.pylons.potency_capped": "최대 단계: %s",
    "tooltip.pylons.progress": "진행도: %d/%d초",
    "tooltip.pylons.protection": "보호 파일런에 사용합니다.",
    "tooltip.pylons.protection1": "설정한 필터에 따라 실수로",
    "tooltip.pylons.protection2": "블록을 부수거나 몹을 죽이지",
    "tooltip.pylons.protection3": "못하게 합니다.",
}

QUEST_TRANSLATIONS: dict[str, object] = {
    "quest.011F787E620DE9E8.quest_desc": [
        "몹 필터로 다시 보고 싶지 않은 몹을 클릭하면 해당 몹이 설정됩니다. \\n\\n필터 하나에는 몹 1종만 담을 수 있으므로 좀비, 스켈레톤, 거미, 크리퍼와 엔더맨의 생성을 모두 막으려면 몹 필터 5개가 필요합니다. \\n\\n다른 몹을 클릭하면 필터에 저장된 몹을 바꿀 수 있습니다."
    ],
    "quest.011F787E620DE9E8.quest_subtitle": "초대받지 않은 손님!",
    "quest.034A9FBCA6D79BB6.quest_desc": [
        "수확 파일런이 작동하려면 괭이가 필요합니다. \\n\\n(파괴되지 않는 괭이는 영원히 작동하지만, 파괴되는 괭이는 교체해야 합니다.)"
    ],
    "quest.09D18512037386C1.quest_desc": [
        "물약 효과를 넣으려면 먼저 물약 필터를 채워야 합니다. \\n\\n자신에게 물약 효과가 걸린 상태에서 물약 필터를 들고 우클릭하면 효과가 자신에게서 사라지고 필터에 저장됩니다. 필터가 가득 차 활성화될 때까지 반복하세요. \\n\\n성급함이나 저항처럼 일반 물약으로 얻기 어려운 효과와 다른 모드의 물약 효과도 사용할 수 있습니다."
    ],
    "quest.12ED1EE85E146A4B.quest_desc": [
        "수확 파일런은 간단한 자동 농장으로 작동합니다. 파일런을 물 원천 안이나 위에 놓으면 주변의 설정한 영역에서 다 자란 작물을 자동으로 수확하고 다시 심습니다. ",
        "",
        "영역은 파일런 주변 3x3, 5x5, 7x7 또는 9x9블록으로 설정할 수 있습니다. ",
        "",
        "작물에 사용할 괭이와 수확물을 넣을 상자 같은 인벤토리를 파일런 위에 두어야 합니다. 준비를 마치고 파일런을 켜면 농사를 시작합니다!",
    ],
    "quest.18246A48C20B29D8.quest_desc": [
        "주입 파일런은 신호기와 비슷하지만 훨씬 좋고 저렴합니다! \\n물약 필터로 효과를 넣으면 어디에 있든 해당 물약 효과를 계속 부여합니다! \\n\\n맞습니다. 이제 주입 파일런에는 정해진 반경이 없으며 어디에 있든 효과가 닿습니다."
    ],
    "quest.30B0240543253EFB.quest_desc": [
        "Pylons는 &aMutant Gumdrop&r이 만든 훌륭한 모드입니다!\\n\\n규모가 작다고 얕보지 마세요! Minecraft 플레이를 편리하게 해 주는 다양한 파일런을 제공합니다.\\n\\n파일런 제작을 시작하려면 윤나는 흑암이 필요합니다."
    ],
    "quest.30B0240543253EFB.title": "&lPylons",
    "quest.32E52AD6EF194A60.quest_desc": [
        "추방 파일런은 다른 사람이 자신의 땅에 들어오지 못하게 합니다. \\n\\n설치하면 허용 목록에 없는 플레이어를 주변의 설정한 청크 범위 밖으로 밀어냅니다. \\n\\n화면 왼쪽 위에서 범위를 1x1, 3x3 또는 5x5청크로 설정할 수 있습니다. \\n\\n월드 시작 지점과 너무 가까운 곳에는 설치할 수 없습니다. 악용하려는 생각은 알고 있지만 허용하지 않습니다! \\n\\n플레이어를 허용하려면 플레이어 필터 퀘스트를 확인하세요!"
    ],
    "quest.32E52AD6EF194A60.quest_subtitle": "내 땅에서 나가!",
    "quest.403F76908A8A5661.quest_desc": [
        "추방 파일런은 플레이어를 영역 밖으로 밀어내지만, &l일부&r 플레이어는 가까이 있게 하고 싶을 수 있습니다. 그럴 때는 플레이어 필터가 필요합니다. \\n\\n필터로 플레이어를 우클릭해 등록한 뒤 파일런에 넣어 허용 목록에 추가하세요! \\n\\n다른 사람은 모두 밀려나도 친구는 그대로 남습니다! \\n\\n기본적으로 파일런 소유자는 추방되지 않습니다."
    ],
    "quest.5B5FC539BD1F4A73.quest_desc": [
        "이 파일런은 몹 생성을 막습니다. ",
        "",
        "몹 필터로 특정 몹의 생성만 막거나 무생명 필터로 모든 몹 생성을 막을 수 있습니다! ",
        "",
        "몹 필터를 여러 개 넣으면 더 많은 몹을 막을 수 있습니다. 몹 생성을 막을 작업 영역도 바꿀 수 있습니다. ",
        "",
        "무생명 필터를 사용하면 다른 설정을 모두 무시합니다.",
    ],
    "quest.5C2C29ECA67F9B49.quest_desc": [
        "무생명 필터를 사용하면 25x25청크 영역 안의 몹 자연 생성을 걱정할 필요가 없습니다. ",
        "",
        "다만 생성 장치나 생성 알이 만드는 강제 생성은 막지 않습니다!",
        "",
        "25x25 범위는 플레이어 주변에서 적대적·우호적 몹이 생성되는 모든 거리를 포함합니다. ",
        "",
        "파일런 위아래의 모든 Y 높이도 포함하므로 동굴을 밝힐 필요가 없습니다! ",
        "",
        "이 필터에는 허용 목록이 없으며 모든 몹의 자연 생성을 막습니다.",
    ],
    "quest.5C2C29ECA67F9B49.quest_subtitle": "마침내 찾아온 평화와 고요함",
    "quest.5E02AE661945306C.quest_desc": [
        "이 퀘스트는 AllTheMods 모드팩에서 사용하기 위해 &6AllTheMods 직원&r 또는 &2커뮤니티 기여자&r가 작성했습니다. \\n\\n모든 &6AllTheMods&r 팩은 &e모든 권리 보유&r 라이선스를 사용하므로, 명시적 허가 없이 &6AllTheMods 팀&r이 출시하지 않은 공개 팩에서 이 퀘스트를 사용할 수 없습니다. \\n\\n이 퀘스트는 의도적으로 숨겨져 있습니다. 이 문구가 보인다면 편집 모드입니다."
    ],
    "task.35320BB07FB39D05.title": "모든 권리 보유",
    "task.59DD89698DBAA215.title": "모든 권리 보유",
    "task.616C07AFBAFA7AE4.title": "괭이",
    "quest.2747AEE1F7F97848.quest_desc": [
        "물약은 좋지만 시간제한은 싫지 않나요? \\n\\n아니요, 주입 파일런 이야기는 잠시 넣어 두세요! \\n\\n이 &7유닛&r을 사용하면 더 빠르게 달리고 더 높이 뛸 수 있습니다! (그래도 농구 실력이 좋아지지는 않습니다.) \\n\\n더 많이 장착할수록 더 빠르고 높아집니다!"
    ],
}


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def normalize() -> dict[str, object]:
    english = load_json(WORK_ROOT / "pylons/en_us.json")
    if set(english) != set(LANG_TRANSLATIONS):
        missing = sorted(set(english) - set(LANG_TRANSLATIONS))
        extra = sorted(set(LANG_TRANSLATIONS) - set(english))
        raise RuntimeError(
            f"언어 확정 번역 키 불일치: missing={missing}, extra={extra}"
        )
    write_json(
        WORK_ROOT / "pylons/ko_kr.json",
        {key: LANG_TRANSLATIONS[key] for key in english},
    )
    quest_count = 0
    for scope in ("pylons", "related"):
        root = WORK_ROOT / "quests" / scope
        english_quests = load_json(root / "en_us.json")
        missing = sorted(set(english_quests) - set(QUEST_TRANSLATIONS))
        if missing:
            raise RuntimeError(f"퀘스트 확정 번역 누락: {scope}:{missing}")
        write_json(
            root / "ko_kr.json",
            {key: QUEST_TRANSLATIONS[key] for key in english_quests},
        )
        quest_count += len(english_quests)
    report = {
        "language_keys_reviewed": len(english),
        "quest_display_keys_reviewed": quest_count,
        "bundled_korean_reused_without_review": 0,
        "status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    english = load_json(WORK_ROOT / "pylons/en_us.json")
    korean = load_json(WORK_ROOT / "pylons/ko_kr.json")
    if list(english) != list(korean):
        errors.append("언어 키 또는 순서 불일치")
    for key, source in english.items():
        target = korean.get(key)
        errors.extend(
            f"pylons:{key}: {error}"
            for error in family_goal.validate_family_value(FAMILY, key, source, target)
        )
    quest_count = 0
    for scope in ("pylons", "related"):
        root = WORK_ROOT / "quests" / scope
        source_rows = load_json(root / "en_us.json")
        target_rows = load_json(root / "ko_kr.json")
        quest_count += len(source_rows)
        if list(source_rows) != list(target_rows):
            errors.append(f"{scope}: 퀘스트 키 또는 순서 불일치")
        for key, source in source_rows.items():
            source_text = family_goal.quest_snbt.flatten(source)
            target_text = family_goal.quest_snbt.flatten(target_rows.get(key))
            if Counter(FORMAT_CODE.findall(source_text)) != Counter(
                FORMAT_CODE.findall(target_text)
            ):
                errors.append(f"{scope}:{key}: 서식 코드 불일치")
            if Counter(PLACEHOLDER.findall(source_text)) != Counter(
                PLACEHOLDER.findall(target_text)
            ):
                errors.append(f"{scope}:{key}: 자리표시자 불일치")
            if source_text.count("\\n") != target_text.count("\\n"):
                errors.append(f"{scope}:{key}: 줄바꿈 불일치")
    report = {
        "language_keys_reviewed": len(english),
        "quest_display_keys_reviewed": quest_count,
        "bundled_korean_reused_without_review": 0,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", report)
    return report, errors


def audit() -> dict[str, object]:
    instance = resolve_source_root()
    jar = next((instance / "mods").glob("pylons-*.jar"))
    advancements = display_nodes = 0
    with ZipFile(jar) as archive:
        for name in archive.namelist():
            if "/advancement/" not in name or not name.endswith(".json"):
                continue
            advancements += 1
            data = json.loads(archive.read(name))
            if isinstance(data, dict) and isinstance(data.get("display"), dict):
                display_nodes += 1
    references: list[str] = []
    direct_display: list[str] = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not re.search(r"pylons:", text, re.I):
            continue
        relative = path.relative_to(instance).as_posix()
        references.append(relative)
        if path.suffix.lower() == ".js":
            for number, line in enumerate(text.splitlines(), start=1):
                if re.search(
                    r"displayName|setHoverName|tooltip|Text\.(?:of|literal)", line, re.I
                ):
                    direct_display.append(f"{relative}:{number}")
    report = {
        "advancement_files": advancements,
        "advancement_display_nodes": display_nodes,
        "kubejs_reference_files": references,
        "kubejs_direct_display_lines": direct_display,
        "status": "complete" if not direct_display else "review_required",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("normalize", "verify", "audit"))
    args = parser.parse_args()
    if args.command == "normalize":
        report = normalize()
        code = 0
    elif args.command == "verify":
        report, errors = verify()
        code = 1 if errors else 0
    else:
        report = audit()
        code = 0 if report["status"] == "complete" else 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
