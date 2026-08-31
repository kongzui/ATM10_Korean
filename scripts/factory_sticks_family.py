#!/usr/bin/env python3
"""Factory Blocks와 Construction Sticks의 표시 문자열을 번역하고 검증해요."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "factory_sticks"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
RESOURCEPACK_ROOT = active_output_root() / "resourcepack/ATM10_Korean/assets"
QUEST_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[.]\d+)?")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")

NAMESPACES = {
    "factory_blocks": "factory_blocks-*.jar",
    "constructionstick": "ConstructionSticks-*.jar",
}

FACTORY_FIXED = {
    "item.factory_blocks.debug": "디버그 아이템(제거 예정)",
    "subtitles.factory_block.metal_sound": "금속 소리가 남",
    "block.factory_blocks.test_block": "시험용 블록",
}

FACTORY_TOOLTIPS = {
    "factory": "점무늬 녹슨 판금",
    "rust": "녹슨 판금",
    "vrust": "매우 녹슨 판금",
    "srust": "살짝 녹슨 판금",
    "wireframe": "철망 구조",
    "pwireframe": "보라색 철망 구조",
    "hazard": "노랑·검정 주의 줄무늬",
    "hazardo": "주황·하양 주의 줄무늬",
    "circuit": "회로",
    "metalbox": "금속 상자",
    "gcircuit": "금도금 회로",
    "pgcircuit": "금색 테두리 보라색 회로",
    "grinder": "분쇄기",
    "old_vents": "낡은 환기구",
    "rust_plates": "분할된 녹슨 판금",
    "bcircuit": "파란색 테두리 회로",
    "ice": "얼음 얼음 얼음",
    "mosaic": "파란색 회로",
    "bwireframe": "파란색 철망 구조",
    "rusty_scaffold": "녹슨 비계",
    "large_pipes": "대형 파이프",
    "small_pipes": "소형 파이프",
    "vent": "환기구",
    "gvent": "빛나는 환기구",
    "insulation": "단열재",
    "gears": "톱니바퀴와 플라이휠",
    "caution": "녹슨 비계",
    "cables": "케이블",
    "rust_bplates": "볼트로 고정한 녹슨 판금",
    "grate": "격자판",
    "rgrate": "녹슨 격자판",
    "hex": "대형 육각 무늬",
    "wgpanel": "심하게 부식된 패널",
    "wopanel": "심하게 녹슨 패널",
    "sturdy": "튼튼한 판금",
    "megacell": "메가셀 배터리",
    "exhaust": "배기구 판금",
    "engineer": "엔지니어용 파이프",
    "scaffold": "대형 녹슨 비계",
    "piping": "배관",
    "large_plating": "엉성한 판금",
    "fan_side": "매끈한 금속",
    "fan": "환풍기(레드스톤 작동)",
    "fan_on": "환풍기(항상 작동)",
    "fan_four": "환풍기(레드스톤 작동, 네 면)",
    "fan_four_on": "환풍기(항상 작동, 네 면)",
    "fan_malfunction": "환풍기(레드스톤 작동, 고장)",
    "fan_malfunction_on": "환풍기(항상 작동, 고장)",
    "medium_fan": "중형 환풍기",
}

CONSTRUCTION = {
    "advancement.constructionstick.iron_stick.desc": "아무 건축 막대나 제작하세요",
    "advancement.constructionstick.iron_stick.title": "끈끈한 상황",
    "advancement.constructionstick.root.desc": "건축을 더 쉽게",
    "advancement.constructionstick.root.title": "Construction Sticks",
    "advancement.constructionstick.template_angel.desc": "공중에 블록을 놓아요, 오-예!",
    "advancement.constructionstick.template_angel.title": "천사 막대 형판",
    "advancement.constructionstick.template_battery.desc": "건축에 전력을 더하세요",
    "advancement.constructionstick.template_battery.title": "배터리 형판",
    "advancement.constructionstick.template_destruction.desc": "블록 파괴자",
    "advancement.constructionstick.template_destruction.title": "파괴 막대 형판",
    "advancement.constructionstick.template_replacement.desc": "낡은 건 빼고 새것으로",
    "advancement.constructionstick.template_replacement.title": "교체 막대 형판",
    "advancement.constructionstick.template_unbreakable.desc": "한계가 없습니다!",
    "advancement.constructionstick.template_unbreakable.title": "파괴 불가 형판",
    "constructionstick.alias.emi.construction": "건축",
    "constructionstick.alias.emi.construction_wand": "건축 완드",
    "constructionstick.alias.emi.wand": "완드",
    "constructionstick.configuration.AngelFalling": "천사 낙하",
    "constructionstick.configuration.AngelFalling.tooltip": (
        "천사 업그레이드가 있을 때 10블록 넘게 떨어지는 동안 발아래에 블록을 놓습니다"
        "(추락이나 공허 낙하에서 살아남는 데 사용할 수 있습니다)"
    ),
    "constructionstick.configuration.BEList": "블록 엔티티 목록",
    "constructionstick.configuration.BEList.tooltip": (
        "블록 엔티티 허용/차단 목록입니다. 막대가 블록 엔티티를 포함한 블록을 놓도록 "
        "허용하거나 막습니다. minecraft:chest 같은 블록 ID나 minecraft 같은 모드 ID를 "
        "추가할 수 있습니다"
    ),
    "constructionstick.configuration.BEWhitelist": "블록 엔티티 허용 목록",
    "constructionstick.configuration.BEWhitelist.tooltip": (
        "켜면 BEList를 허용 목록으로 처리하고, 끄면 차단 목록으로 처리합니다"
    ),
    "constructionstick.configuration.MaxRange": "최대 범위",
    "constructionstick.configuration.MaxRange.tooltip": (
        "최대 설치 범위(0: 무제한)입니다. 모든 막대에 적용되며 게임 밸런스가 아니라 "
        "지연 방지를 위한 설정입니다."
    ),
    "constructionstick.configuration.SimilarBlocks": "유사 블록",
    "constructionstick.configuration.SimilarBlocks.tooltip": (
        "유사 일치 모드에서 같은 것으로 처리할 블록입니다. 블록 ID를 ;로 구분해 입력하세요"
    ),
    "constructionstick.configuration.UndoHistory": "실행 취소 기록",
    "constructionstick.configuration.UndoHistory.tooltip": "실행 취소할 수 있는 작업 수",
    "constructionstick.configuration.angel": "천사 업그레이드",
    "constructionstick.configuration.angel.tooltip": (
        "막대의 파괴 블록 제한(0이면 파괴 업그레이드 비활성화)"
    ),
    "constructionstick.configuration.batteryStorage": "배터리 용량",
    "constructionstick.configuration.batteryStorage.tooltip": "배터리 에너지 저장 용량",
    "constructionstick.configuration.batteryUsage": "배터리 소모량",
    "constructionstick.configuration.batteryUsage.tooltip": "블록 하나당 배터리 에너지 소모량",
    "constructionstick.configuration.blockentity": "블록 엔티티",
    "constructionstick.configuration.blockentity.tooltip": "블록 엔티티 설정",
    "constructionstick.configuration.copper_stick": "구리 막대",
    "constructionstick.configuration.copper_stick.tooltip": "구리 막대 설정",
    "constructionstick.configuration.destruction": "파괴 업그레이드",
    "constructionstick.configuration.destruction.tooltip": (
        "막대의 파괴 블록 제한(0이면 파괴 업그레이드 비활성화)"
    ),
    "constructionstick.configuration.diamond_stick": "다이아몬드 막대",
    "constructionstick.configuration.diamond_stick.tooltip": "다이아몬드 막대 설정",
    "constructionstick.configuration.durability": "내구도",
    "constructionstick.configuration.durability.tooltip": "막대 내구도",
    "constructionstick.configuration.iron_stick": "철 막대",
    "constructionstick.configuration.iron_stick.tooltip": "철 막대 설정",
    "constructionstick.configuration.limit": "설치 제한",
    "constructionstick.configuration.limit.tooltip": (
        "천사 업그레이드의 최대 설치 거리(0이면 천사 업그레이드 비활성화)"
    ),
    "constructionstick.configuration.misc": "기타",
    "constructionstick.configuration.misc.tooltip": "기타 설정",
    "constructionstick.configuration.netherite_stick": "네더라이트 막대",
    "constructionstick.configuration.netherite_stick.tooltip": "네더라이트 막대 설정",
    "constructionstick.configuration.upgradeable": "업그레이드 가능",
    "constructionstick.configuration.upgradeable.tooltip": (
        "대장장이 작업대에서 막대와 막대 업그레이드를 합쳐 업그레이드할 수 있게 합니다."
    ),
    "constructionstick.configuration.wooden_stick": "최고로 끈끈한 막대",
    "constructionstick.configuration.wooden_stick.tooltip": "최고로 끈끈한 막대 설정",
    "constructionstick.description.durability.limited": "%d개 블록 동안",
    "constructionstick.description.key.sneak": "웅크리기",
    "constructionstick.description.key.sneak_opt": "웅크리기+%s",
    "constructionstick.description.stick": (
        "%s은(는) 건물에서 자신을 향한 면에 최대 %s개 블록을 놓을 수 있으며, 내구도는 "
        "%s입니다.\n\n지정된 %s 키를 눌러 설치 제한을 바꾸세요(가로, 세로, 남북, "
        "동서, 제한 없음).\n\n지정된 %s 키를 눌러 옵션 화면을 여세요.\n\n"
        "§5§n실행 취소§0§r\n바라보는 블록에서 지정된 %s 키를 누르고 있으면 마지막으로 "
        "놓은 블록이 초록색 테두리로 표시됩니다. 표시된 블록을 보면서 지정된 %s 키를 "
        "누르면 작업을 취소하고 모든 아이템을 돌려받습니다. 파괴 업그레이드를 사용했다면 "
        "블록을 복구합니다.\n\n§5§n보관함§0§r\n셜커 상자와 꾸러미, 다른 모드의 여러 "
        "보관함에서 막대에 건축 블록을 공급할 수 있습니다.\n\n§5§n보조 손 우선§0§r\n"
        "보조 손에 블록이 있으면 바라보는 블록 대신 그 블록을 놓습니다."
    ),
    "constructionstick.description.template_angel": (
        "천사 업그레이드는 바라보는 블록 또는 블록 줄의 반대편에 블록을 놓습니다. 최대 "
        "거리는 막대 등급에 따라 달라집니다. 빈 공간을 우클릭하면 공중에 블록을 놓습니다. "
        "이때 놓을 블록을 보조 손에 들고 있어야 합니다."
    ),
    "constructionstick.description.template_battery": (
        "배터리 업그레이드를 사용하면 내구도 대신 에너지를 쓸 수 있습니다. 막대가 에너지를 "
        "저장하고 블록을 놓을 때 사용합니다. 주의: 에너지를 충전하는 방법을 제공하는 모드가 "
        "있어야 막대를 충전할 수 있습니다."
    ),
    "constructionstick.description.template_destruction": (
        "파괴 업그레이드는 자신을 향한 면의 블록을 파괴합니다(블록 엔티티 제외). 최대 파괴 "
        "수는 막대 등급에 따라 달라집니다. 파괴한 블록은 공허로 사라지지만, 실수했다면 실행 "
        "취소 기능으로 복구할 수 있습니다."
    ),
    "constructionstick.description.template_replacement": (
        "교체 업그레이드를 사용하면 블록을 보조 손에 든 종류의 블록으로 바꿀 수 있습니다. "
        "이미 설치한 벽을 교체할 때 유용합니다."
    ),
    "constructionstick.description.template_unbreakable": (
        "파괴 불가 업그레이드를 사용하면 내구도를 소모하지 않고 블록을 놓을 수 있습니다. "
        "막대가 절대 부서지지 않습니다."
    ),
    "constructionstick.description.upgrade": (
        "§5§n설치§0§r\n새 업그레이드 형판, 막대와 필요한 아이템을 대장장이 작업대에서 "
        "합치면 적용됩니다(필요한 아이템은 대장장이 작업대 제작법에서 확인하세요). "
        "업그레이드를 바꾸려면 막대를 든 채 지정된 %s 키를 누르거나 옵션 화면을 사용하세요."
    ),
    "constructionstick.networking.query_undo.failed": "작업을 취소하지 못했습니다: %s",
    "constructionstick.networking.stick_option.undo": "막대 옵션을 바꾸지 못했습니다: %s",
    "constructionstick.networking.undo_blocks.failed": "블록을 되돌리지 못했습니다: %s",
    "constructionstick.option.direction": "방향: ",
    "constructionstick.option.direction.player": "§a플레이어",
    "constructionstick.option.direction.player.desc": "블록이 플레이어를 향하도록 놓습니다",
    "constructionstick.option.direction.target": "§6대상",
    "constructionstick.option.direction.target.desc": "대상 블록과 같은 방향으로 놓습니다",
    "constructionstick.option.lock": "제한: ",
    "constructionstick.option.lock.eastwest": "§6동/서",
    "constructionstick.option.lock.eastwest.desc": "원래 블록 위에서 동서 방향으로 줄을 만듭니다",
    "constructionstick.option.lock.horizontal": "§a좌/우",
    "constructionstick.option.lock.horizontal.desc": "원래 블록 앞에 가로 열을 만듭니다",
    "constructionstick.option.lock.nolock": "§c없음",
    "constructionstick.option.lock.nolock.desc": "원래 블록의 어느 면에서든 확장합니다",
    "constructionstick.option.lock.northsouth": "§6남/북",
    "constructionstick.option.lock.northsouth.desc": "원래 블록 위에서 남북 방향으로 줄을 만듭니다",
    "constructionstick.option.lock.vertical": "§a위/아래",
    "constructionstick.option.lock.vertical.desc": "원래 블록 앞에 세로 열을 만듭니다",
    "constructionstick.option.match": "일치 방식: ",
    "constructionstick.option.match.any": "§c모두",
    "constructionstick.option.match.any.desc": "어떤 블록이든 확장합니다",
    "constructionstick.option.match.exact": "§a정확히",
    "constructionstick.option.match.exact.desc": "완전히 같은 블록만 확장합니다",
    "constructionstick.option.match.similar": "§6유사",
    "constructionstick.option.match.similar.desc": "비슷한 블록(흙/잔디 종류)을 같게 처리합니다",
    "constructionstick.option.random": "무작위: ",
    "constructionstick.option.random.no": "§c아니요",
    "constructionstick.option.random.no.desc": "설치할 블록을 무작위로 고르지 않습니다",
    "constructionstick.option.random.yes": "§a예",
    "constructionstick.option.random.yes.desc": "단축바에 있는 블록을 무작위로 놓습니다",
    "constructionstick.option.replace": "교체: ",
    "constructionstick.option.replace.no": "§c아니요",
    "constructionstick.option.replace.no.desc": "블록을 교체하지 않습니다",
    "constructionstick.option.replace.yes": "§a예",
    "constructionstick.option.replace.yes.desc": "유체, 눈, 키 큰 잔디 같은 블록을 교체합니다",
    "constructionstick.option.upgrades": "",
    "constructionstick.option.upgrades.constructionstick:default": "건축",
    "constructionstick.option.upgrades.constructionstick:default.desc": (
        "건물에서 자신을 향한 면을 확장합니다"
    ),
    "constructionstick.option.upgrades.constructionstick:upgrade_angel": "§6천사",
    "constructionstick.option.upgrades.constructionstick:upgrade_angel.desc": (
        "블록 뒤편과 공중에 블록을 놓습니다"
    ),
    "constructionstick.option.upgrades.constructionstick:upgrade_battery": "§4배터리",
    "constructionstick.option.upgrades.constructionstick:upgrade_battery.desc": (
        "내구도 대신 에너지를 사용합니다"
    ),
    "constructionstick.option.upgrades.constructionstick:upgrade_destruction": "§c파괴",
    "constructionstick.option.upgrades.constructionstick:upgrade_destruction.desc": (
        "자신을 향한 면의 블록을 파괴합니다"
    ),
    "constructionstick.option.upgrades.constructionstick:upgrade_replacement": "§5교체",
    "constructionstick.option.upgrades.constructionstick:upgrade_replacement.desc": (
        "블록을 보조 손에 든 블록으로 교체합니다"
    ),
    "constructionstick.option.upgrades.constructionstick:upgrade_unbreakable": "§d파괴 불가",
    "constructionstick.option.upgrades.constructionstick:upgrade_unbreakable.desc": (
        "내구도를 소모하지 않고 설치할 수 있습니다"
    ),
    "constructionstick.placement.denied": "이 블록은 건축 막대로 놓을 수 없습니다!",
    "constructionstick.tooltip.blocks": "최대 %d개 블록",
    "constructionstick.tooltip.shift": "[SHIFT] 누르기",
    "constructionstick.tooltip.storage": "%s/%s RF 저장됨",
    "constructionstick.tooltip.upgrades": "막대 업그레이드:",
    "constructionstick.tooltip.upgrades_tip": "대장장이 작업대에서 형판을 막대에 적용하세요",
    "item.constructionstick.copper_stick": "구리 막대",
    "item.constructionstick.diamond_stick": "다이아몬드 막대",
    "item.constructionstick.iron_stick": "철 막대",
    "item.constructionstick.netherite_stick": "네더라이트 막대",
    "item.constructionstick.template_angel": "천사 막대 형판",
    "item.constructionstick.template_battery": "배터리 형판",
    "item.constructionstick.template_destruction": "파괴 막대 형판",
    "item.constructionstick.template_replacement": "교체 막대 형판",
    "item.constructionstick.template_unbreakable": "파괴 불가 형판",
    "item.constructionstick.wooden_stick": "최고로 끈끈한 막대",
    "itemGroup.constructionstick.tab": "Construction Sticks",
    "key.constructionstick.category": "Construction Sticks",
    "key.constructionstick.change_direction": "방향 전환",
    "key.constructionstick.change_restriction": "제한 전환",
    "key.constructionstick.change_upgrade": "업그레이드 전환",
    "key.constructionstick.open_gui": "막대 옵션 열기",
    "key.constructionstick.show_previous": "이전 작업 표시",
    "key.constructionstick.toggle_random": "무작위 전환",
    "key.constructionstick.undo": "작업 취소",
    "stat.constructionstick.use_stick": "막대로 놓은 블록 수",
}

INTENTIONAL_SAME = {
    "factory_blocks": set(),
    "constructionstick": {
        "advancement.constructionstick.root.title",
        "constructionstick.option.upgrades",
        "itemGroup.constructionstick.tab",
        "key.constructionstick.category",
    },
}

ALLOWED_LATIN = {
    "BEList",
    "Construction",
    "EMI",
    "SHIFT",
    "Sticks",
    "chest",
    "minecraft",
}

QUEST_CORRECTIONS = {
    "quest.318A2CC03D1D0B04.quest_desc": [
        "&l건축 완드&r가 그리우셨나요? \\n\\n저도 그랬고, &9Mrbysco&r 님도 "
        "그랬습니다! 그래서 &l&6Construction Sticks&r를 만들었죠! \\n\\n&6건축 막대&r에는 "
        "여러 등급이 있습니다. 비싼 막대일수록 내구도가 높고 더 많은 블록을 놓을 수 "
        "있습니다. \\n\\n처음에는 빈 공간을 채우도록 블록을 놓지만, GUI를 열어 옵션을 "
        "바꿀 수 있습니다. 먼저 직접 단축키를 지정해야 합니다. \\n\\n옵션 화면에서는 블록을 "
        "놓을 위치와 무늬, 사용할 블록 종류까지 모두 바꿀 수 있습니다! \\n\\n막대 전용 "
        "업그레이드도 제작할 수 있습니다. 사용하려면 대장장이 작업대에서 업그레이드와 "
        "&6건축 막대&r를 결합하세요. "
    ],
    "quest.318A2CC03D1D0B04.title": "&l&6Construction Sticks",
    "task.3BE936F7D054FDDA.title": "막대!",
}

RELATED_QUEST_IDS = {"318A2CC03D1D0B04", "3BE936F7D054FDDA"}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽어요."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 객체가 아니에요: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 안정된 형식으로 써요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    """파일 SHA-256을 계산해요."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_jar(instance: Path, pattern: str) -> Path:
    """현재 인스턴스의 유일한 대상 JAR을 찾아요."""
    matches = sorted((instance / "mods").glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"JAR 수가 1개가 아니에요: {pattern} -> {matches}")
    return matches[0]


def read_jar_language(jar: Path, namespace: str) -> dict[str, object]:
    """JAR의 영어 언어 파일을 읽어요."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read(f"assets/{namespace}/lang/en_us.json"))
    if not isinstance(value, dict):
        raise TypeError(f"JAR 언어 파일이 객체가 아니에요: {jar.name}")
    return value


def factory_translations(english: dict[str, object]) -> dict[str, object]:
    """Factory Blocks 전체 번역을 만들어요."""
    translated = dict(FACTORY_FIXED)
    for identifier, tooltip in FACTORY_TOOLTIPS.items():
        translated[f"block.factory_blocks.{identifier}"] = "공장 블록"
        translated[f"item.factory_blocks.{identifier}.tooltip"] = tooltip
    missing = sorted(set(english) - set(translated))
    extra = sorted(set(translated) - set(english))
    if missing or extra:
        raise ValueError(f"Factory Blocks 번역 키 불일치: 누락={missing}, 초과={extra}")
    return {key: translated[key] for key in english}


def prepare() -> dict[str, object]:
    """현재 JAR 원문을 작업 폴더에 기록해요."""
    instance = resolve_source_root()
    rows = []
    total = 0
    for namespace, pattern in NAMESPACES.items():
        jar = source_jar(instance, pattern)
        english = read_jar_language(jar, namespace)
        write_json(WORK_ROOT / namespace / "en_us.json", english)
        rows.append(
            {
                "namespace": namespace,
                "jar": jar.name,
                "jar_size": jar.stat().st_size,
                "jar_mtime_ns": jar.stat().st_mtime_ns,
                "english_keys": len(english),
                "bundled_korean": False,
            }
        )
        total += len(english)
    report = {
        "family": FAMILY,
        "namespaces": rows,
        "english_keys": total,
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", report)
    return report


def build() -> dict[str, object]:
    """두 모드의 언어 산출물을 만들어요."""
    factory_en = load_json(WORK_ROOT / "factory_blocks/en_us.json")
    construction_en = load_json(WORK_ROOT / "constructionstick/en_us.json")
    factory_ko = factory_translations(factory_en)
    missing = sorted(set(construction_en) - set(CONSTRUCTION))
    extra = sorted(set(CONSTRUCTION) - set(construction_en))
    if missing or extra:
        raise ValueError(
            f"Construction Sticks 번역 키 불일치: 누락={missing}, 초과={extra}"
        )
    construction_ko = {key: CONSTRUCTION[key] for key in construction_en}
    for namespace, translated in (
        ("factory_blocks", factory_ko),
        ("constructionstick", construction_ko),
    ):
        write_json(WORK_ROOT / namespace / "ko_kr.json", translated)
        write_json(RESOURCEPACK_ROOT / namespace / "lang/ko_kr.json", translated)
        write_json(
            WORK_ROOT / namespace / "candidate_sources.json",
            {key: "new_translation_required" for key in translated},
        )
    report = {
        "reviewed_language_keys": len(factory_en) + len(construction_en),
        "existing_korean_reused": 0,
        "new_language_translations": len(factory_en) + len(construction_en),
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def collect_references(instance: Path) -> dict[str, object]:
    """FTB Quests와 KubeJS의 실제 계열 참조를 모아요."""
    needles = ("factory_blocks:", "constructionstick:")
    suffixes = {
        ".cfg",
        ".js",
        ".json",
        ".kjs",
        ".properties",
        ".snbt",
        ".toml",
        ".txt",
        ".zs",
    }
    results = {
        "quest_references": [],
        "kubejs_references": [],
        "custom_name_candidates": [],
        "read_errors": [],
    }
    for label, root in (
        ("quest_references", instance / "config/ftbquests/quests/chapters"),
        ("kubejs_references", instance / "kubejs"),
    ):
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                results["read_errors"].append(f"{path}: {exc}")
                continue
            relative = path.relative_to(instance).as_posix()
            for number, line in enumerate(text.splitlines(), start=1):
                if any(needle in line for needle in needles):
                    row = f"{relative}:{number}:{line.strip()}"
                    results[label].append(row)
                    if "custom_name" in line.lower():
                        results["custom_name_candidates"].append(row)
    return results


def audit() -> tuple[dict[str, object], list[str]]:
    """발전 과제와 관련 FTB Quests·KubeJS 표시 경로를 감사해요."""
    instance = resolve_source_root()
    errors = []
    jars = []
    for namespace, pattern in NAMESPACES.items():
        jar = source_jar(instance, pattern)
        advancement_files = []
        translated_keys = []
        direct_literals = []
        with ZipFile(jar) as archive:
            for internal in sorted(archive.namelist()):
                if "/advancement/" not in internal or not internal.endswith(".json"):
                    continue
                advancement_files.append(internal)
                value = json.loads(archive.read(internal))
                display = value.get("display", {})
                if not isinstance(display, dict):
                    continue
                for field in ("title", "description"):
                    shown = display.get(field)
                    if isinstance(shown, dict) and isinstance(
                        shown.get("translate"), str
                    ):
                        translated_keys.append(shown["translate"])
                    elif isinstance(shown, str):
                        direct_literals.append(
                            {"file": internal, "field": field, "value": shown}
                        )
        language = load_json(WORK_ROOT / namespace / "ko_kr.json")
        missing_advancement_keys = sorted(set(translated_keys) - set(language))
        if missing_advancement_keys:
            errors.append(
                f"{namespace} 발전 과제 번역 키가 누락됐어요: {missing_advancement_keys}"
            )
        if direct_literals:
            errors.append(f"{namespace} 발전 과제에 직접 영어 문구가 있어요")
        jars.append(
            {
                "namespace": namespace,
                "jar": jar.name,
                "advancement_files": advancement_files,
                "advancement_translation_keys": sorted(set(translated_keys)),
                "missing_advancement_keys": missing_advancement_keys,
                "direct_advancement_text": direct_literals,
            }
        )
    references = collect_references(instance)
    errors.extend(references["read_errors"])
    if references["custom_name_candidates"]:
        errors.append("관련 퀘스트에 custom_name 표시 후보가 있어요")
    english_quests = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean_quests = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    related_quest_keys = sorted(
        key
        for key in english_quests
        if any(identifier in key for identifier in RELATED_QUEST_IDS)
    )
    for key, expected in QUEST_CORRECTIONS.items():
        if korean_quests.get(key) != expected:
            errors.append(f"Construction Sticks 관련 퀘스트 교정값이 달라요: {key}")
    for key in related_quest_keys:
        if key not in korean_quests:
            errors.append(f"Construction Sticks 관련 퀘스트 한국어가 없어요: {key}")
            continue
        source_text = json.dumps(english_quests[key], ensure_ascii=False)
        target_text = json.dumps(korean_quests[key], ensure_ascii=False)
        for label, pattern in (("자리표시자", PLACEHOLDER), ("서식 코드", FORMAT_CODE)):
            if Counter(pattern.findall(source_text)) != Counter(
                pattern.findall(target_text)
            ):
                errors.append(f"퀘스트 {label} 보존이 달라요: {key}")
        if Counter(NUMBER.findall(source_text)) != Counter(NUMBER.findall(target_text)):
            errors.append(f"퀘스트 숫자 보존이 달라요: {key}")
    report = {
        "family": FAMILY,
        "jars": jars,
        "references": references,
        "related_quest_keys": related_quest_keys,
        "related_quest_keys_corrected": len(QUEST_CORRECTIONS),
        "ftbquests_display_work": "complete",
        "kubejs_display_work": "ids_only",
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """현재 JAR과 산출물의 키·자료형·표시 보존 규칙을 검증해요."""
    instance = resolve_source_root()
    audit_report = load_json(WORK_ROOT / "surface_audit.json")
    errors = []
    rows = []
    total = 0
    for namespace, pattern in NAMESPACES.items():
        jar = source_jar(instance, pattern)
        jar_english = read_jar_language(jar, namespace)
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        output = load_json(RESOURCEPACK_ROOT / namespace / "lang/ko_kr.json")
        current_errors = []
        untranslated = []
        latin_residue = {}
        if jar_english != english:
            current_errors.append("작업 영어가 현재 설치 JAR 영어와 달라요")
        if list(english) != list(korean):
            current_errors.append("한국어 키 또는 순서가 영어 원문과 달라요")
        if korean != output:
            current_errors.append("작업 한국어와 산출물이 달라요")
        for key in english.keys() & korean.keys():
            source = english[key]
            target = korean[key]
            if type(source) is not type(target):
                current_errors.append(f"자료형 불일치: {key}")
                continue
            if not isinstance(source, str) or not isinstance(target, str):
                continue
            for label, pattern in (
                ("자리표시자", PLACEHOLDER),
                ("서식 코드", FORMAT_CODE),
            ):
                if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
                    current_errors.append(f"{label} 불일치: {key}")
            if Counter(NUMBER.findall(source)) != Counter(NUMBER.findall(target)):
                current_errors.append(f"숫자 불일치: {key}")
            if source.count("\n") != target.count("\n"):
                current_errors.append(f"줄바꿈 불일치: {key}")
            if source == target and key not in INTENTIONAL_SAME[namespace]:
                untranslated.append(key)
            residue = sorted(set(LATIN_WORD.findall(target)) - ALLOWED_LATIN)
            if residue:
                latin_residue[key] = residue
        collisions = defaultdict(list)
        for key, target in korean.items():
            if isinstance(target, str) and key.startswith(("item.", "block.")):
                collisions[target].append(key)
        unexpected_collisions = {
            target: keys
            for target, keys in collisions.items()
            if len(keys) > 1 and len({english[key] for key in keys}) > 1
        }
        if untranslated:
            current_errors.append(f"영어와 같은 미번역 후보: {untranslated}")
        if latin_residue:
            current_errors.append(f"허용하지 않은 영문 잔여: {latin_residue}")
        if unexpected_collisions:
            current_errors.append(
                f"서로 다른 이름의 한국어 충돌: {unexpected_collisions}"
            )
        rows.append(
            {
                "namespace": namespace,
                "keys": len(english),
                "existing_korean_reused": 0,
                "new_translations": len(english),
                "untranslated_candidates": untranslated,
                "latin_residue": latin_residue,
                "unexpected_name_collisions": unexpected_collisions,
                "errors": current_errors,
            }
        )
        errors.extend(f"{namespace}: {message}" for message in current_errors)
        total += len(english)
    if audit_report.get("status") != "complete":
        errors.append("표시 표면 감사가 완료되지 않았어요")
    report = {
        "family": FAMILY,
        "namespaces": rows,
        "keys": total,
        "existing_korean_reused": 0,
        "new_translations": total,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "language_validation.json", report)
    completion = {
        "family": FAMILY,
        "language_keys": total,
        "existing_korean_reused": 0,
        "new_or_corrected_translations": total + len(QUEST_CORRECTIONS),
        "ftbquests": {
            "reviewed_keys": len(audit_report.get("related_quest_keys", [])),
            "corrected_keys": len(QUEST_CORRECTIONS),
            "display_work": audit_report.get("ftbquests_display_work"),
        },
        "kubejs_references": len(
            audit_report.get("references", {}).get("kubejs_references", [])
        ),
        "output_files": [
            "resourcepacks/ATM10_Korean/assets/factory_blocks/lang/ko_kr.json",
            "resourcepacks/ATM10_Korean/assets/constructionstick/lang/ko_kr.json",
            "config/ftbquests/quests/lang/ko_kr.snbt",
        ],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    completion_path = WORK_ROOT / "family_completion.json"
    if completion_path.is_file():
        previous = load_json(completion_path)
        if "deployment" in previous:
            completion["deployment"] = previous["deployment"]
    write_json(completion_path, completion)
    return report, errors


def output_source(relative: str) -> Path:
    """적용 상대 경로를 저장소 산출물 경로로 바꿔요."""
    if relative.startswith("resourcepacks/"):
        return (
            active_output_root()
            / "resourcepack"
            / relative.removeprefix("resourcepacks/")
        )
    return active_output_root() / "overrides" / relative


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 스크립트의 백업·해시 결과를 완료 기록에 반영해요."""
    resolved = manifest_path.resolve()
    try:
        relative_manifest = resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError as exc:
        raise ValueError(f"프로젝트 밖의 적용 기록이에요: {resolved}") from exc
    manifest = load_json(resolved)
    completion_path = WORK_ROOT / "family_completion.json"
    completion = load_json(completion_path)
    expected = set(completion["output_files"])
    errors = []
    matched = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 기록 상태가 applied_and_verified가 아니에요")
    targets = manifest.get("targets")
    if not isinstance(targets, list):
        targets = []
        errors.append("적용 기록의 targets가 목록이 아니에요")
    for target in targets:
        if not isinstance(target, dict) or not isinstance(target.get("files"), list):
            continue
        files = {
            str(row.get("relative_path")): row
            for row in target["files"]
            if isinstance(row, dict) and row.get("relative_path") in expected
        }
        if set(files) != expected:
            continue
        for relative, row in files.items():
            source = output_source(relative)
            target_file = Path(str(row.get("target")))
            if not target_file.is_file() or sha256(target_file) != sha256(source):
                errors.append(f"적용 대상과 산출물 해시가 달라요: {relative}")
            if row.get("source_sha256") != row.get("after_sha256"):
                errors.append(f"적용 기록의 전후 해시가 달라요: {relative}")
        matched.append(target)
    if len(matched) != 1:
        errors.append(f"일치하는 적용 대상 기록 수가 1개가 아니에요: {len(matched)}")
    target = matched[0] if matched else {}
    deployment = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "target": target.get("target_root"),
        "changed_paths": target.get("changed_paths", []),
        "backup_manifest": relative_manifest,
        "errors": errors,
    }
    completion["deployment"] = deployment
    if errors:
        completion["status"] = "incomplete"
    write_json(completion_path, completion)
    return deployment, errors


def run_all() -> tuple[dict[str, object], list[str]]:
    """준비, 생성, 감사와 검증을 차례로 실행해요."""
    prepare_report = prepare()
    build_report = build()
    audit_report, audit_errors = audit()
    verify_report, verify_errors = verify()
    report = {
        "prepare": prepare_report,
        "build": build_report,
        "audit": audit_report,
        "verify": verify_report,
        "status": "complete"
        if not audit_errors and not verify_errors
        else "incomplete",
    }
    return report, audit_errors + verify_errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "build", "audit", "verify", "record-deployment", "all"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    errors = []
    if args.command == "prepare":
        report = prepare()
    elif args.command == "build":
        report = build()
    elif args.command == "audit":
        report, errors = audit()
    elif args.command == "verify":
        report, errors = verify()
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        report, errors = record_deployment(args.manifest)
    else:
        report, errors = run_all()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
