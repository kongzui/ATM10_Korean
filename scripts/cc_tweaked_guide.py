#!/usr/bin/env python3
"""Advanced Peripherals Patchouli 가이드를 현재 JAR 기준으로 번역하고 검증한다."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root


WORK_ROOT = PROJECT_ROOT / "working/cc_tweaked/guide"
ENGLISH_ROOT = WORK_ROOT / "en_us"
KOREAN_ROOT = WORK_ROOT / "ko_kr"
OUTPUT_ROOT = (
    active_output_root()
    / "resourcepack/ATM10_Korean/assets/advancedperipherals/patchouli_books/manual/ko_kr"
)
BOOK_OUTPUT = (
    active_output_root()
    / "overrides/kubejs/data/advancedperipherals/patchouli_books/manual/book.json"
)
JAR_PREFIX = "AdvancedPeripherals-"
SOURCE_PREFIX = "assets/advancedperipherals/patchouli_books/manual/en_us/"
BOOK_PATH = "data/advancedperipherals/patchouli_books/manual/book.json"
VISIBLE_KEYS = {"name", "description", "text", "title", "link_text", "landing_text"}
PATCHOULI_TOKEN = re.compile(r"\$\([^)]*\)")

NAME_TRANSLATIONS = {
    "Advanced Peripherals": "Advanced Peripherals",
    "Metaphysics": "형이상학",
    "Items": "아이템",
    "Peripherals": "주변 장치",
    "Colony integrator": "식민지 연동기",
    "Geo Scanner": "지질 스캐너",
    "Chat Box": "채팅 상자",
    "NBT Storage": "NBT 저장소",
    "Block reader": "블록 리더",
    "Energy Detector": "에너지 감지기",
    "Environment Detector": "환경 감지기",
    "Inventory Manager": "인벤토리 관리자",
    "Player Detector": "플레이어 감지기",
    "RS Bridge": "RS 브리지",
    "ME Bridge": "ME 브리지",
    "Weak automata core": "약한 오토마타 코어",
    "End automata core": "엔드 오토마타 코어",
    "Overpowered automata core": "초강력 오토마타 코어",
    "Overpowered weak automata core": "초강력 약한 오토마타 코어",
    "Intro": "소개",
    "Cooldowns and fuel": "재사용 대기시간과 연료",
    "Husbandry automata core": "축산 오토마타 코어",
    "Chunk Controller": "청크 제어기",
    "Pocket Computer Addons": "포켓 컴퓨터 애드온",
    "Memory Card": "메모리 카드",
    "Computer Tool": "컴퓨터 조정 도구",
    "API documentation": "API 문서",
}

TEXT_PREFIXES = {
    "The colony integrator can interact with a colony from MineColonies..": (
        "식민지 연동기는 MineColonies의 식민지와 상호 작용합니다."
    ),
    "The Geo Scanner provides information about blocks around and chunk where scanner located. "
    "Geo scanner has delay between scans, so you should be ready for this.": (
        "지질 스캐너는 주변 블록과 자신이 놓인 청크의 정보를 제공합니다. 스캔 사이에는 "
        "재사용 대기시간이 있으니 코드에서 고려해야 합니다."
    ),
    "The Chat Box peripheral allows you to interact with the game chat by sending and receiving "
    "messages.$(p)You can even send messages that are only visible for the Chat Box if you start "
    "your message with a `$`.": (
        "채팅 상자는 메시지를 보내고 받아 게임 채팅과 상호 작용합니다.$(p)메시지를 `$`로 "
        "시작하면 채팅 상자에만 보이는 메시지도 보낼 수 있습니다."
    ),
    "NBT Storage is custom block that allow input/output custom data to block. Mostly provided "
    "for ID support.": (
        "NBT 저장소는 사용자 지정 데이터를 블록에 넣고 꺼낼 수 있는 블록입니다. 주로 ID "
        "지원을 위해 제공됩니다."
    ),
    "This block is able to read data of blocks and tile entities in front of it.": (
        "앞에 있는 블록과 블록 엔티티의 데이터를 읽습니다."
    ),
    "The Energy Detector can detect energy flow and acts as a resistor. You can define the max "
    "flow rate to use it as a resistor.": (
        "에너지 감지기는 에너지 흐름을 측정하고 저항기 역할도 합니다. 최대 흐름량을 지정해 "
        "저항기로 사용할 수 있습니다."
    ),
    "The Environment Detector is able to receive information from the environment like the "
    "current time, the current moon phase, the light level of the block and many more.": (
        "환경 감지기는 현재 시간, 달의 위상, 블록의 밝기 등 여러 환경 정보를 가져옵니다."
    ),
    "The Inventory Manager can communicate with the player's inventory. You need to right click "
    "a Memory Card and put the card into the manager to use it.": (
        "인벤토리 관리자는 플레이어 인벤토리와 통신합니다. 메모리 카드를 든 채 우클릭한 뒤 "
        "관리자에 넣어야 사용할 수 있습니다."
    ),
    "The Player Detector is able to recognize players within a certain range. In addition, it "
    "recognizes the player who clicks on him.": (
        "플레이어 감지기는 일정 범위 안의 플레이어를 감지하며, 자신을 클릭한 플레이어도 "
        "알아냅니다."
    ),
    "The RS Bridge is able to interact with Refined Storage. You can retrieve items, craft items, "
    "get all items as a list and more.": (
        "RS 브리지는 Refined Storage와 상호 작용합니다. 아이템을 가져오거나 제작하고, 전체 "
        "아이템 목록을 읽는 등의 작업을 할 수 있습니다."
    ),
    "The ME Bridge is able to interact with Applied Energistics 2. You can retrieve items, craft "
    "items, get all items as a list and more. The Me Bridge uses one channel.": (
        "ME 브리지는 Applied Energistics 2와 상호 작용합니다. 아이템을 가져오거나 제작하고, "
        "전체 아이템 목록을 읽는 등의 작업을 할 수 있습니다. ME 브리지는 채널 하나를 사용합니다."
    ),
    "The Chunk Controller is a crafting ingredient for the Chunky Turtle.$(p)Combine with a turtle "
    "or advanced turtle to make it chunk-loading!": (
        "청크 제어기는 청크 터틀의 제작 재료입니다.$(p)터틀이나 고급 터틀과 조합하면 청크를 "
        "계속 불러오는 터틀이 됩니다!"
    ),
    "We provide Pocket Computer upgrades for the following peripherals:$(li)$(9)$(l:peripherals/"
    "environment_detector)Environment Detector$(/l)$()$(li)$(9)$(l:peripherals/player_detector)"
    "Player Detector$(/l)$()$(li)$(9)$(l:peripherals/chat_box)Chat Box$(/l)$()": (
        "다음 주변 장치를 포켓 컴퓨터 업그레이드로 제공합니다:$(li)$(9)$(l:peripherals/"
        "environment_detector)환경 감지기$(/l)$()$(li)$(9)$(l:peripherals/player_detector)"
        "플레이어 감지기$(/l)$()$(li)$(9)$(l:peripherals/chat_box)채팅 상자$(/l)$()"
    ),
    "The $(9)$(l:items/ar_goggles)AR Goggles$(/l)$() can be used in combination with the "
    "$(9)$(l:peripherals/inventory_manager)Inventory Manager$(/l)$() to communicate with the "
    "player's inventory.$(p)Right click with the Memory Card in hand to assign it to yourself.": (
        "$(9)$(l:items/ar_goggles)AR 고글$(/l)$()은 $(9)$(l:peripherals/inventory_manager)"
        "인벤토리 관리자$(/l)$()와 함께 사용해 플레이어 인벤토리와 통신합니다.$(p)메모리 "
        "카드를 든 채 우클릭해 자신의 카드로 등록하세요."
    ),
    "The Computer Tool is a tool to open GUI's from our blocks. Currently, the Computer Tool is "
    "useless, it's just a wonderful item.": (
        "컴퓨터 조정 도구는 이 모드의 블록 GUI를 여는 도구입니다. 현재는 기능이 없고 그저 "
        "멋진 아이템일 뿐입니다."
    ),
}

TEXT_TRANSLATIONS = {
    "This manual provides basic information about all the peripherals added by this mod.$(p)For "
    "more information please see $(9)$(l:https://docs.advanced-peripherals.de/)the official "
    "documentation$(/l)$().": (
        "이 설명서는 Advanced Peripherals가 추가하는 모든 주변 장치의 기본 정보를 제공합니다."
        "$(p)자세한 내용은 $(9)$(l:https://docs.advanced-peripherals.de/)공식 문서$(/l)$()를 "
        "참고하세요."
    ),
    "What is the origin of the Universe? What is its first cause? Is its existence necessary? Is "
    "I am real?": "우주의 기원은 무엇일까요? 최초의 원인은 무엇일까요? 존재는 필연일까요? 나는 실재할까요?",
    "Advanced Peripherals adds some items that are used in combination with the peripherals, or "
    "as crafting ingredients to enhance turtles.": (
        "Advanced Peripherals는 주변 장치와 함께 사용하거나 터틀을 강화하는 제작 재료로 쓰는 "
        "아이템을 추가합니다."
    ),
    "All the peripherals added by this mod.$(p)Use them to interact with other mods, players, the "
    "world and the game chat.": (
        "이 모드가 추가하는 모든 주변 장치입니다.$(p)다른 모드, 플레이어, 월드, 게임 채팅과 "
        "상호 작용하는 데 사용하세요."
    ),
    "Connect your Colony integrator to a computer in area of village to make use of it!": (
        "식민지 영역 안에서 식민지 연동기를 컴퓨터에 연결해 사용하세요!"
    ),
    "Connect your Geo Scanner to a computer to make use of it!": "지질 스캐너를 컴퓨터에 연결해 사용하세요!",
    "Connect your Chat Box to a computer to make use of it!": "채팅 상자를 컴퓨터에 연결해 사용하세요!",
    "Connect your NBT Storage to a computer to make use of it!": "NBT 저장소를 컴퓨터에 연결해 사용하세요!",
    "Connect your Block reader to a computer and target block to make use of it!": (
        "블록 리더를 컴퓨터와 조사할 블록에 맞닿게 연결해 사용하세요!"
    ),
    "Connect your Energy Detector to a computer to make use of it!": (
        "에너지 감지기를 컴퓨터에 연결해 사용하세요!"
    ),
    "Connect your Environment Detector to a computer to make use of it!": (
        "환경 감지기를 컴퓨터에 연결해 사용하세요!"
    ),
    "Connect your Inventory Manager to a computer to make use of it!": (
        "인벤토리 관리자를 컴퓨터에 연결해 사용하세요!"
    ),
    "Connect your Player Detector to a computer to make use of it!": (
        "플레이어 감지기를 컴퓨터에 연결해 사용하세요!"
    ),
    "Connect your RS Bridge to a computer to make use of it!": "RS 브리지를 컴퓨터에 연결해 사용하세요!",
    "Connect your ME Bridge to a computer to make use of it!": "ME 브리지를 컴퓨터에 연결해 사용하세요!",
    "The Weak Automata core is turtle upgrade, that allow to transform turtle into powerful "
    "automata!": "약한 오토마타 코어는 터틀을 강력한 오토마타로 바꾸는 업그레이드입니다!",
    "It provides several ability for turtles.$(li)Digging block with tool;$(li)Click on block with "
    "item or empty hand;$(li)Suck item around, all or specific;$(li)Detect items around;$(li)Detect "
    "block or turtle in line of view;$(li)Charge turtle with RF item inside inventory": (
        "터틀에 여러 능력을 제공합니다.$(li)도구로 블록 캐기$(li)아이템이나 빈손으로 블록 "
        "클릭$(li)주변의 모든 아이템 또는 지정 아이템 흡수$(li)주변 아이템 감지$(li)시야 "
        "안의 블록이나 터틀 감지$(li)인벤토리의 RF 아이템으로 터틀 충전"
    ),
    "But weak core is only a start of metaphysics research! Empty construct ready to accept soul "
    "fragments of mobs. Seems, you need to try to feed different mobs to soul to receive advanced "
    "variants.$(li)$(l:metaphysics/end_automata_core)End Automata core$(li)$(l:metaphysics/"
    "husbandry_automata_core)Husbandry Automata core": (
        "약한 코어는 형이상학 연구의 시작일 뿐입니다! 이 빈 그릇은 몹의 영혼 조각을 받아들일 "
        "준비가 되어 있습니다. 여러 몹을 영혼에 먹이면 고급 형태를 얻을 수 있을 듯합니다."
        "$(li)$(l:metaphysics/end_automata_core)엔드 오토마타 코어$(li)$(l:metaphysics/"
        "husbandry_automata_core)축산 오토마타 코어"
    ),
    "After consuming 10 endermans, weak automata core will be transformed to end automata core!"
    "$(p)In addition to be more powerful weak automata core variant, seems, this soul also provide "
    "some limited teleportation abilities for turtle itself.": (
        "엔더맨 10마리를 흡수하면 약한 오토마타 코어가 엔드 오토마타 코어로 변합니다!"
        "$(p)약한 코어보다 강할 뿐 아니라 터틀 자체에 제한적인 순간이동 능력도 제공하는 듯합니다."
    ),
    "In additions to weak automata core abilities, this soul also allow limited world-bound "
    "teleportation. Seems, you need to store points and then teleport to them!$(p)But be aware, "
    "any stored points will be lost after turtle is broken.": (
        "약한 오토마타 코어의 능력에 더해 같은 차원 안에서 제한적으로 순간이동할 수 있습니다. "
        "지점을 저장한 뒤 그곳으로 이동하세요!$(p)터틀이 부서지면 저장한 지점이 모두 사라집니다."
    ),
    "This is you first attempt to bypass rules of metaphysics. Well, not so successful as you hope "
    "it would be.$(p)Naive combination of any automata core and nether star lead to some result ...": (
        "형이상학의 법칙을 벗어나려는 첫 시도입니다. 기대만큼 성공적이지는 않았습니다."
        "$(p)아무 오토마타 코어나 네더의 별과 단순히 조합했더니 무언가가 만들어졌습니다..."
    ),
    "Overpowered versions of automata cores doesn't consumes item durability when use it.$(p)But "
    "everything come for price. If you try to perform any operation with this core without enough "
    "fuel - upgrade will broke immediately.": (
        "초강력 오토마타 코어는 아이템을 사용할 때 내구도를 소비하지 않습니다.$(p)하지만 "
        "대가가 따릅니다. 연료가 부족한 상태로 작업하면 업그레이드가 즉시 부서집니다."
    ),
    "This world hold many secrets from you. You feel, that even simple turtle can become a powerful "
    "tool to control reality, you just need to put something real inside it. Something more like "
    "... soul?": (
        "이 세계에는 아직 모르는 비밀이 많습니다. 평범한 터틀도 현실을 다루는 강력한 도구가 "
        "될 수 있을 것 같습니다. 그 안에 진짜 무언가를 넣기만 하면 됩니다. 예를 들면... 영혼?"
    ),
    "All world changing operations will consume turtle fuel (of course, if you not disable fuel "
    "usage in CC:Tweaked configuration).$(p)Also, most of this operations have cooldowns, so you "
    "should consider this in your code. Hopefully, every active cooldown can be recived via "
    "peripheral methods.": (
        "월드를 바꾸는 모든 작업은 터틀 연료를 소비합니다(CC: Tweaked 설정에서 연료 사용을 "
        "끄지 않은 경우).$(p)대부분의 작업에는 재사용 대기시간도 있으므로 코드에서 고려해야 "
        "합니다. 활성 재사용 대기시간은 주변 장치 메서드로 확인할 수 있습니다."
    ),
    "You think, that cooldowns are too big? This is when fuel consuming rate come to help!$(p)"
    "Bigger fuel consuming rate will reduce cooldown, but obviously increate fuel consumption. For "
    "example, if click operation required 1 fuel point for perform and will have 5 seconds cooldown, "
    "with fuel consumption 2 you can perform click operation one in 2.5 seconds, but in cost of 2 "
    "fuel point.": (
        "재사용 대기시간이 너무 길다면 연료 소비율을 높여 보세요!$(p)연료 소비율을 높이면 "
        "대기시간이 줄지만 연료를 더 씁니다. 예를 들어 클릭 작업이 연료 1과 5초의 대기시간을 "
        "요구할 때 소비율을 2로 설정하면 연료 2를 써서 2.5초마다 작업할 수 있습니다."
    ),
    "However, fuel consumption rate is not so simple! Every automata core has max fuel consumption "
    "limitation, that can be retrieved via $(l)getConfiguration$() method.$(p)Also, fuel point will "
    "grow faster, than cooldown drops. Fuel consumption 3 will required 4 fuel points, fuel "
    "consumption 4 will required fuel points, etc.": (
        "연료 소비율은 단순하지 않습니다! 오토마타 코어마다 최대 소비율이 있으며 "
        "$(l)getConfiguration$() 메서드로 확인할 수 있습니다.$(p)대기시간이 줄어드는 것보다 "
        "연료 소모가 더 빠르게 늘어납니다. 소비율 3에는 연료 4가 필요하고 이후에도 계속 증가합니다."
    ),
    "After consuming 3 chickens, 3 cows, 3 sheeps, weak automata core will be transformed to "
    "husbandry automata core!$(p)In addition to be more powerful weak automata core variant, seems, "
    "this soul also provide abilities to interact with animals!": (
        "닭 3마리, 소 3마리, 양 3마리를 흡수하면 약한 오토마타 코어가 축산 오토마타 코어로 "
        "변합니다!$(p)약한 코어보다 강할 뿐 아니라 동물과 상호 작용하는 능력도 제공하는 듯합니다!"
    ),
    "In additions to weak automata core abilities, this core also allow to interact with animals "
    "and even transfer them inside!$(p)But be aware, any stored animal will be lost after turtle "
    "is broken.": (
        "약한 오토마타 코어의 능력에 더해 동물과 상호 작용하고 내부에 보관할 수도 있습니다!"
        "$(p)터틀이 부서지면 보관한 동물이 모두 사라집니다."
    ),
    "Simply combine these with a pocket computer to add the peripheral to it. Note that you can't "
    "use the associated events.": (
        "포켓 컴퓨터와 조합하면 해당 주변 장치를 추가할 수 있습니다. 단, 관련 이벤트는 사용할 "
        "수 없습니다."
    ),
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


def find_jar() -> Path:
    root = resolve_source_root()
    matches = sorted(
        path
        for path in (root / "mods").glob("*.jar")
        if path.name.lower().startswith(JAR_PREFIX.lower())
    )
    if len(matches) != 1:
        raise RuntimeError(f"Advanced Peripherals JAR을 확정하지 못했습니다: {matches}")
    return matches[0]


def prepare(force: bool) -> dict[str, object]:
    jar = find_jar()
    files = 0
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            if not name.startswith(SOURCE_PREFIX) or not name.endswith(".json"):
                continue
            target = ENGLISH_ROOT / name.removeprefix(SOURCE_PREFIX)
            if target.exists() and not force:
                raise FileExistsError(f"기존 작업본을 덮어쓰지 않습니다: {target}")
            write_json(target, json.loads(archive.read(name).decode("utf-8-sig")))
            files += 1
        write_json(
            WORK_ROOT / "book_en_us.json",
            json.loads(archive.read(BOOK_PATH).decode("utf-8-sig")),
        )
    report = {"jar": jar.name, "localized_files": files, "book_metadata": 1}
    write_json(WORK_ROOT / "scope.json", report)
    return report


def translate_value(source: str) -> str:
    if source in NAME_TRANSLATIONS:
        return NAME_TRANSLATIONS[source]
    if source in TEXT_TRANSLATIONS:
        return TEXT_TRANSLATIONS[source]
    marker = "$(p)For the full documentation please see the "
    if marker in source:
        prefix, suffix = source.split(marker, 1)
        translated_prefix = TEXT_PREFIXES.get(prefix)
        if translated_prefix is None:
            raise KeyError(f"가이드 본문 번역이 없습니다: {prefix}")
        match = re.fullmatch(
            r"\$\(9\)\$\(l:([^)]*)\)official wiki page\$\(/l\)\$\(\)!", suffix
        )
        if match is None:
            raise ValueError(f"공식 문서 링크 형식이 다릅니다: {source}")
        return (
            f"{translated_prefix}$(p)자세한 내용은 $(9)$(l:{match.group(1)})"
            "공식 위키 문서$(/l)$()를 참고하세요!"
        )
    raise KeyError(f"가이드 표시 문구 번역이 없습니다: {source}")


def transform(value: object, translate: bool, visible: bool = False) -> object:
    if isinstance(value, dict):
        return {
            key: transform(child, translate, key in VISIBLE_KEYS)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [transform(child, translate, visible) for child in value]
    if isinstance(value, str) and visible:
        return translate_value(value) if translate else "<visible>"
    return value


def visible_pairs(
    source: object, target: object, path: str = "$"
) -> list[tuple[str, str, str]]:
    pairs: list[tuple[str, str, str]] = []
    if isinstance(source, dict) and isinstance(target, dict):
        for key, child in source.items():
            if key not in target:
                continue
            if (
                key in VISIBLE_KEYS
                and isinstance(child, str)
                and isinstance(target[key], str)
            ):
                pairs.append((f"{path}.{key}", child, target[key]))
            else:
                pairs.extend(visible_pairs(child, target[key], f"{path}.{key}"))
    elif isinstance(source, list) and isinstance(target, list):
        for index, (left, right) in enumerate(zip(source, target, strict=False)):
            pairs.extend(visible_pairs(left, right, f"{path}[{index}]"))
    return pairs


def normalize() -> dict[str, object]:
    changed = 0
    reviewed = 0
    for source_path in sorted(ENGLISH_ROOT.rglob("*.json")):
        source = load_json(source_path)
        translated = transform(source, True)
        target = KOREAN_ROOT / source_path.relative_to(ENGLISH_ROOT)
        previous = load_json(target) if target.is_file() else None
        if previous != translated:
            changed += 1
        write_json(target, translated)
        reviewed += len(visible_pairs(source, translated))
    book_source = load_json(WORK_ROOT / "book_en_us.json")
    book_translated = transform(book_source, True)
    write_json(WORK_ROOT / "book_ko_kr.json", book_translated)
    reviewed += len(visible_pairs(book_source, book_translated))
    report = {
        "visible_strings_reviewed": reviewed,
        "changed_files": changed,
        "existing_korean_reused_without_review": 0,
        "status": "all_current_english_strings_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    reviewed = 0
    files = 0
    for source_path in sorted(ENGLISH_ROOT.rglob("*.json")):
        target_path = KOREAN_ROOT / source_path.relative_to(ENGLISH_ROOT)
        if not target_path.is_file():
            errors.append(f"한국어 가이드 파일 누락: {target_path}")
            continue
        source = load_json(source_path)
        target = load_json(target_path)
        if transform(source, False) != transform(target, False):
            errors.append(f"가이드 비표시 구조 변경: {target_path}")
        for pointer, english, korean in visible_pairs(source, target):
            reviewed += 1
            if english == korean and english not in {"Advanced Peripherals"}:
                errors.append(f"미번역 가이드 문구: {target_path}:{pointer}")
            if PATCHOULI_TOKEN.findall(english) != PATCHOULI_TOKEN.findall(korean):
                errors.append(f"Patchouli 토큰 불일치: {target_path}:{pointer}")
        files += 1
    book_source = load_json(WORK_ROOT / "book_en_us.json")
    book_target = load_json(WORK_ROOT / "book_ko_kr.json")
    if transform(book_source, False) != transform(book_target, False):
        errors.append("책 메타데이터 비표시 구조가 변경되었습니다.")
    for pointer, english, korean in visible_pairs(book_source, book_target):
        reviewed += 1
        if english == korean and english not in {"Advanced Peripherals"}:
            errors.append(f"미번역 책 문구: {pointer}")
        if PATCHOULI_TOKEN.findall(english) != PATCHOULI_TOKEN.findall(korean):
            errors.append(f"책 Patchouli 토큰 불일치: {pointer}")
    report = {
        "files": files + 1,
        "visible_strings_reviewed": reviewed,
        "untranslated": sum("미번역" in error for error in errors),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "validation.json", report)
    return report, 1 if errors else 0


def build() -> dict[str, object]:
    copied = 0
    for source in sorted(KOREAN_ROOT.rglob("*.json")):
        write_json(OUTPUT_ROOT / source.relative_to(KOREAN_ROOT), load_json(source))
        copied += 1
    write_json(BOOK_OUTPUT, load_json(WORK_ROOT / "book_ko_kr.json"))
    return {
        "localized_files": copied,
        "book_file": str(BOOK_OUTPUT.relative_to(PROJECT_ROOT)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "normalize", "verify", "build"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.force)
        status = 0
    elif args.command == "normalize":
        result = normalize()
        status = 0
    elif args.command == "verify":
        result, status = verify()
    else:
        result = build()
        status = 0
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
