#!/usr/bin/env python3
"""Gateways to Eternity와 Hellish Trials의 표시 문자열 전체를 번역·검증한다."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass
import gzip
import hashlib
import io
import json
import re
import struct
import sys
from pathlib import Path
from typing import BinaryIO
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "gateways_hellish"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
LANG_WORK_ROOT = WORK_ROOT / "gateways"
LANG_OUTPUT = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/gateways/lang/ko_kr.json"
)
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
TOOLTIP_OUTPUT = PROJECT_ROOT / "output/overrides/kubejs/client_scripts/tooltips.js"
GATEWAY_DATA_PATH = "data/gateways/gateways/hellish_fortress.json"
GATEWAY_DATA_OUTPUT = PROJECT_ROOT / "output/overrides/kubejs" / GATEWAY_DATA_PATH
GATEWAYS_PATTERN = "GatewaysToEternity-*.jar"
HELLISH_PATTERN = "HellishTrials-*.jar"
GATEWAYS_ENGLISH = "assets/gateways/lang/en_us.json"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[./xX×]\d+)*")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
ALLOWED_LATIN = {"Alt", "Ctrl", "Gateways", "Shift", "Eternity"}
INTENTIONAL_SAME_KEYS = {
    "failure.gateways.mob_effect",
    "reward.gateways.stack",
    "tooltip.gateways.dot",
    "tooltip.gateways.dot_with_count",
    "tooltip.gateways.with_count",
}

TRANSLATIONS = {
    "entity.gateways.gateway": "영원의 게이트웨이",
    "item.gateways.gate_pearl": "게이트 진주",
    "gateways.gate_pearl": "게이트 진주 - %s",
    "itemGroup.gateways": "Gateways to Eternity",
    "info.gateways.gate_pearl": (
        "게이트 진주는 블록에 사용해 게이트웨이를 소환할 수 있습니다.\n\n"
        "현재 간격 설정에 따라 다른 게이트웨이와 너무 가까워지는 위치에서는 "
        "사용할 수 없습니다.\n"
    ),
    "info.gateways.gate_pearl.2": (
        "열린 게이트웨이는 몹을 생성하지 못하거나, 활성 몹이 너무 멀리 이동하거나, "
        "웨이브 타이머가 끝나면 번개와 함께 실패합니다.\n\n"
        "획득한 보상은 게이트웨이에서 생성됩니다."
    ),
    "tooltip.gateways.with_count": "%s %s",
    "tooltip.gateways.dot_with_count": "• %s %s",
    "tooltip.gateways.dot": "• %s",
    "tooltip.gateways.scroll": "[스크롤]",
    "tooltip.gateways.shift": "[Shift]",
    "tooltip.gateways.ctrl": "[Ctrl]",
    "tooltip.gateways.alt": "[Alt]",
    "tooltip.gateways.true": "활성화",
    "tooltip.gateways.false": "비활성화",
    "tooltip.gateways.num_wave": "%s개 웨이브",
    "tooltip.gateways.num_waves": "%s개 웨이브",
    "tooltip.gateways.wave": "웨이브 %s/%s",
    "tooltip.gateways.entities": "개체: ",
    "tooltip.gateways.modifiers": "변형자: ",
    "tooltip.gateways.rewards": "보상: ",
    "tooltip.gateways.num_failures": "%s개 불이익",
    "tooltip.gateways.num_failure": "%s개 불이익",
    "tooltip.gateways.failures": "실패 불이익",
    "tooltip.gateways.num_rule": "%s개 규칙 변경",
    "tooltip.gateways.num_rules": "%s개 규칙 변경",
    "tooltip.gateways.rules": "규칙 변경",
    "tooltip.gateways.key_rewards": "주요 보상",
    "tooltip.gateways.endless.base_wave": "기본 웨이브",
    "tooltip.gateways.endless.num_modif": "%s개 무한 변형자",
    "tooltip.gateways.endless.num_modifs": "%s개 무한 변형자",
    "tooltip.gateways.endless.modifier": "무한 변형자 %s/%s",
    "tooltip.gateways.endless.wave_time": "최대 웨이브 시간: %s",
    "tooltip.gateways.endless.setup_time": "준비 시간: %s",
    "boss.gateways.wave": "웨이브: %d/%d | 시간: %s | 적: %d",
    "boss.gateways.done": "게이트 완료!",
    "boss.gateways.starting": "웨이브 %d 시작까지 %s",
    "boss.gateways.endless.top": "웨이브: %d/%d | 남은 시간: %d",
    "boss.gateways.endless.bot": "적: %d/%d | 활성 변형자: %d",
    "boss.gateways.endless.incoming": "곧 등장할 적: %d",
    "reward.gateways.stack": "%s %s",
    "reward.gateways.entity": "%s %s 전리품 추첨",
    "reward.gateways.loot_table": "%s %s회 추첨",
    "reward.gateways.chance": "%s 확률로 %s",
    "reward.gateways.experience": "%s 경험치",
    "reward.gateways.summon": "%s 소환",
    "failure.gateways.explosion": "반경 %s의 폭발",
    "failure.gateways.mob_effect": "%s",
    "failure.gateways.summon": "%s 소환",
    "failure.gateways.chance": "%s 확률로 %s",
    "rule.gateways.default": "[이전 값: %s]",
    "rule.gateways.spawn_range": "생성 범위: %s",
    "rule.gateways.leash_range": "이탈 범위: %s",
    "rule.gateways.allow_discarding": "개체 제거 허용: %s",
    "rule.gateways.allow_dim_change": "차원 이동 허용: %s",
    "rule.gateways.player_damage_only": "플레이어 피해만 허용: %s",
    "rule.gateways.remove_mobs_on_failure": "실패 시 몹 제거: %s",
    "rule.gateways.fail_on_out_of_bounds": "범위 이탈 시 실패: %s",
    "rule.gateways.spacing": "간격: %s",
    "rule.gateways.requires_nearby_player": "근처 플레이어 필요: %s",
    "rule.gateways.lives": "목숨: %s",
    "error.gateways.no_space": "이 게이트웨이를 열 공간이 부족합니다",
    "error.gateways.wave_failed": (
        "다음 웨이브를 생성할 공간이 부족해 게이트웨이가 붕괴했습니다"
    ),
    "error.gateways.too_far": (
        "웨이브 개체가 너무 멀리 이동해 게이트웨이가 붕괴했습니다"
    ),
    "error.gateways.wave_elapsed": "웨이브 제한 시간이 끝났습니다",
    "error.gateways.entity_discarded": (
        "개체가 처치되지 않고 제거되어 게이트웨이가 붕괴했습니다"
    ),
    "error.gateways.no_nearby_player": (
        "근처에 플레이어가 없어 게이트웨이가 붕괴했습니다"
    ),
    "error.gateways.out_of_lives": ("남은 목숨이 없어 게이트웨이가 붕괴했습니다"),
    "appmode.gateways.after_wave": "%s번째 웨이브에 적용됩니다.",
    "appmode.gateways.after_every_n_waves": (
        "%s개 웨이브마다 적용됩니다. 최대 %s회 적용됩니다."
    ),
    "appmode.gateways.only_on_wave": "%s번째 웨이브에만 적용됩니다.",
    "appmode.gateways.only_on_every_n_waves": (
        "%s개 웨이브마다 해당 웨이브에만 적용됩니다."
    ),
    "stat.gateways.gates_defeated": "완료한 게이트웨이",
    "modifier.gateways.gear_set": "장비: %s",
    "gateways.basic/blaze": "블레이즈 게이트웨이",
    "gateways.basic/slime": "슬라임 게이트웨이",
    "gateways.basic/enderman": "엔더맨 게이트웨이",
    "gateways.emerald_grove": "에메랄드 숲의 게이트웨이",
    "gateways.overworldian_nights": "오버월드의 밤 게이트웨이",
    "gateways.hellish_fortress": "지옥불 요새의 게이트웨이",
    "gateways.endless/blaze": "무한 블레이즈 게이트웨이",
    "rewards.gateways.loot_table.simple_dungeon": "던전 전리품",
    "rewards.gateways.loot_table.nether_bridge": "네더 요새 전리품",
    "name.gateways.necrotic_farmer": "괴사한 농부",
    "name.gateways.undead_legionnaire": "언데드 군단병",
    "name.gateways.withered_ranger": "위더 레인저",
    "name.gateways.butcher": "도살자",
    "name.gateways.huge_slime": "거대 슬라임",
    "name.gateways.magicbane_slime": "마법 파멸 슬라임",
    "name.gateways.acidic_slime": "산성 슬라임",
    "name.gateways.flaming_enderman": "불타는 엔더맨",
    "subtitle.gateways.gate_warp": "게이트웨이가 물체를 생성함",
    "subtitle.gateways.gate_ambient": "게이트웨이에서 소리가 남",
    "subtitle.gateways.gate_start": "게이트웨이가 열림",
    "subtitle.gateways.gate_end": "게이트웨이가 닫힘",
    "text.gateways.errored_gate_pearl": "알 수 없는 게이트웨이: %s",
}

BOOK_PAGES = [
    (
        " 나는 아자리엘이다. 이리델 북부의 작은 마을에서 태어났다.\n"
        " 태어날 때부터 명예로운 사람은 아니었고, 스스로 명예를 이룬 적도 없었다.\n"
        " 사춘기를 몹시 거칠게 보내며 부모님께 화를 내고, 활 하나만 든 채 반항심에 "
        "고향을 떠났다."
    ),
    "그리고 한 번도 가져 본 적 없는 무언가를 간절히 원했다.\n ",
    (
        "1687년 T.A.        소마스.         \n처음 몇 달은 숲에서 살아남으려 애쓰는 데 "
        "썼다. 얼마 지나지 않아 이 작은 모험으로는 원하는 것을 얻을 수 없다는 걸 "
        "깨달았다. 적어도 원치 않던 삶에서는 벗어날 수 있었다."
    ),
    (
        "평생 대장장이로 사는 것은 견딜 수 없었다. 처음 몇 년간 일을 배우는 건 나쁘지 "
        "않았지만, 더 많은 것을 갈망하고 있다는 걸 깨닫는 데 오래 걸리지 않았다."
    ),
    (
        "1687년 T.A.      웨드마스.\n 짧은 일탈이 걷잡을 수 없이 커진 듯하다. 집으로 "
        "돌아갈까 생각 중이다. 기대했던 것은 얻지 못했다. \n 운명이 무엇을 준비했는지는 "
        "모른다. 다른 길이 있을지도 모른다. \n 하지만 아직 돌아갈 준비는 되지 않았다."
    ),
    (
        "이 일을 끝없이 끌지는 않겠다. 하지만 놓칠 수 없는 기회라는 생각이 든다. 여기서 "
        "무언가를 얻어야 한다. 숲을 떠도는 건 시간 낭비처럼 느껴졌다. 생존 기술이 늘어난 "
        "지금은 더 그렇다.\n 혼자서 살아남을 수는 있지만, 그게 무슨  \n"
    ),
    (
        "살아남기만 하는 데 무슨 의미가 있을까?\n\n 유망해 보이는 장소에 관한 소문과 "
        "전설을 들었다. 우리 마을에서는 잘 알려지지 않은 이야기지만, 내가 찾던 곳일지도 "
        "모른다는 생각이 든다. "
    ),
    (
        "1691년 T.A.     포어라이스.\n 여기는 지옥이다. 비유가 아니었고, 과장도 아니었다. "
        "나는 말 그대로 지옥에 있다. 상상도 못 한 생물들을 보았고, 어디서나 울음소리가 "
        "들린다. 벽이 비명을 지르고, 목소리들이 끔찍한 말을 속삭인다. 그 말을 내가 하는 "
        "것인지조차 알 수 없다. "
    ),
    (
        "내 입이 저절로 움직이는 느낌이다. 귀를 멀게 하는 소리가 들리고, 보지 말았어야 할 "
        "것들이 보인다. 이곳의 생물들은 나를 증오하고, 모든 것이 나를 증오하며, 나도 나를 "
        "증오한다.\n 숲과는 다르다. 내가 무슨 일에 뛰어들었는지 모르겠다. 몇몇 여행자를 "
        "만났고, 믿을 만해 보였다."
    ),
    (
        "함께 오기로 했다고, 적어도 그들은 그렇게 말했다. 내가 먼저 차원문에 들어왔고, "
        "그 뒤로 다시는 보지 못했다. 돌아가는 길도 찾지 못했다. 그저 엄마에게 돌아가고 싶다."
    ),
    (
        " 이 지하 묘지를 너무 오래 헤맸다. 몇 년이 지났는지도 모르겠다. 자원을 모으고 "
        "장비를 갖추며 저 돔 안에서 기다리는 것에 대비하고 있다.\n 이 모든 시간과 고통을 "
        "헛되게 할 수는 없다. 이곳의 모든 생명을 끝내기 전에는 돌아가지 않겠다. "
    ),
    (
        "그 안에서 무엇을 만나게 될지 수많은 전설이 전해진다.\n 어떤 이야기는 돔에서 "
        "승리한 자가 가장 깊은 소망, 빼앗긴 것, 영혼이 울부짖으며 원하는 것을 받는다고 "
        "한다. 그곳에서 소원이 진짜로 이루어진다고."
    ),
    (
        "하지만... 그런 헛소리는 믿을 수 없다. \n 나는 신앙심이 있는 사람이다. 하지만 "
        "악당이 아닌, 존중받는 누군가가 되어 고향에 돌아가고 싶을 뿐이다. \n 무엇이 너를 "
        "여기로 데려왔는지, 소문이 진실인지 나는 모르며,"
    ),
    (
        "앞으로도 영원히 모를 것이다.  \n 전설은 희망할 무언가를 갈망하는 인간 본성 그 "
        "자체일 뿐이라고 내 일부는 믿는다.\n 네 임무도, 갈망도, 목숨도 내 마음을 움직이지 "
        "않는다. 하지만 이 모든 것을 헛되게 할 수는 없다. "
    ),
    "부탁한다. 이 모든 것이 헛될 수는 없다.",
]

CORRIDOR = "data/hellish_trials/structure/nether_trial/nether_trial_corridor_3.nbt"
MAIN = "data/hellish_trials/structure/nether_trial/nether_trial_main_0.nbt"
NORMAL_VAULT = (
    "data/hellish_trials/structure/nether_trial/nether_trial_vault_0_normal.nbt"
)
OMINOUS_VAULT = (
    "data/hellish_trials/structure/nether_trial/nether_trial_vault_1_ominous.nbt"
)


@dataclass(eq=True)
class Tag:
    """NBT 태그의 종류와 값을 보존한다."""

    kind: int
    value: object


def read_exact(stream: BinaryIO, length: int) -> bytes:
    """요청한 바이트 수를 정확히 읽는다."""
    value = stream.read(length)
    if len(value) != length:
        raise EOFError(f"NBT가 예정보다 일찍 끝났습니다: {len(value)}/{length}")
    return value


def read_string(stream: BinaryIO) -> str:
    """NBT 문자열을 읽는다."""
    length = struct.unpack(">H", read_exact(stream, 2))[0]
    return read_exact(stream, length).decode("utf-8")


def read_payload(stream: BinaryIO, kind: int) -> object:
    """종류별 NBT 페이로드를 읽는다."""
    formats = {1: ">b", 2: ">h", 3: ">i", 4: ">q", 5: ">f", 6: ">d"}
    if kind in formats:
        size = struct.calcsize(formats[kind])
        return struct.unpack(formats[kind], read_exact(stream, size))[0]
    if kind == 7:
        length = struct.unpack(">i", read_exact(stream, 4))[0]
        return read_exact(stream, length)
    if kind == 8:
        return read_string(stream)
    if kind == 9:
        child_kind = struct.unpack(">B", read_exact(stream, 1))[0]
        length = struct.unpack(">i", read_exact(stream, 4))[0]
        return child_kind, [
            Tag(child_kind, read_payload(stream, child_kind)) for _ in range(length)
        ]
    if kind == 10:
        children = {}
        while True:
            child_kind = struct.unpack(">B", read_exact(stream, 1))[0]
            if child_kind == 0:
                break
            name = read_string(stream)
            children[name] = Tag(child_kind, read_payload(stream, child_kind))
        return children
    if kind == 11:
        length = struct.unpack(">i", read_exact(stream, 4))[0]
        return [struct.unpack(">i", read_exact(stream, 4))[0] for _ in range(length)]
    if kind == 12:
        length = struct.unpack(">i", read_exact(stream, 4))[0]
        return [struct.unpack(">q", read_exact(stream, 8))[0] for _ in range(length)]
    raise ValueError(f"지원하지 않는 NBT 태그 종류입니다: {kind}")


def read_nbt(raw: bytes) -> tuple[str, Tag]:
    """압축이 풀린 명명된 루트 NBT를 읽는다."""
    stream = io.BytesIO(raw)
    kind = struct.unpack(">B", read_exact(stream, 1))[0]
    if kind != 10:
        raise ValueError(f"NBT 루트가 compound가 아닙니다: {kind}")
    name = read_string(stream)
    root = Tag(kind, read_payload(stream, kind))
    if stream.read(1):
        raise ValueError("NBT 루트 뒤에 해석하지 못한 데이터가 있습니다")
    return name, root


def write_string(stream: BinaryIO, value: str) -> None:
    """NBT 문자열을 기록한다."""
    encoded = value.encode("utf-8")
    stream.write(struct.pack(">H", len(encoded)))
    stream.write(encoded)


def write_payload(stream: BinaryIO, tag: Tag) -> None:
    """종류별 NBT 페이로드를 기록한다."""
    formats = {1: ">b", 2: ">h", 3: ">i", 4: ">q", 5: ">f", 6: ">d"}
    if tag.kind in formats:
        stream.write(struct.pack(formats[tag.kind], tag.value))
    elif tag.kind == 7:
        value = bytes(tag.value)
        stream.write(struct.pack(">i", len(value)))
        stream.write(value)
    elif tag.kind == 8:
        write_string(stream, str(tag.value))
    elif tag.kind == 9:
        child_kind, children = tag.value
        stream.write(struct.pack(">Bi", child_kind, len(children)))
        for child in children:
            write_payload(stream, child)
    elif tag.kind == 10:
        for name, child in tag.value.items():
            stream.write(struct.pack(">B", child.kind))
            write_string(stream, name)
            write_payload(stream, child)
        stream.write(b"\x00")
    elif tag.kind == 11:
        stream.write(struct.pack(">i", len(tag.value)))
        for value in tag.value:
            stream.write(struct.pack(">i", value))
    elif tag.kind == 12:
        stream.write(struct.pack(">i", len(tag.value)))
        for value in tag.value:
            stream.write(struct.pack(">q", value))
    else:
        raise ValueError(f"지원하지 않는 NBT 태그 종류입니다: {tag.kind}")


def write_nbt(name: str, root: Tag) -> bytes:
    """명명된 루트 NBT를 압축 전 바이트로 기록한다."""
    stream = io.BytesIO()
    stream.write(struct.pack(">B", root.kind))
    write_string(stream, name)
    write_payload(stream, root)
    return stream.getvalue()


def get_tag(root: Tag, path: tuple[str | int, ...]) -> Tag:
    """compound 이름과 list 인덱스로 지정한 태그를 찾는다."""
    current = root
    for part in path:
        if isinstance(part, str):
            if current.kind != 10:
                raise TypeError(f"compound가 아닌 경로에서 이름을 찾았습니다: {path}")
            current = current.value[part]
        else:
            if current.kind != 9:
                raise TypeError(f"list가 아닌 경로에서 인덱스를 찾았습니다: {path}")
            current = current.value[1][part]
    return current


def component_with_text(source: str, target: str) -> str:
    """JSON 텍스트 컴포넌트의 다른 속성을 보존하고 표시 문자만 바꾼다."""
    value = json.loads(source)
    if isinstance(value, str):
        value = target
    elif isinstance(value, dict) and isinstance(value.get("text"), str):
        value["text"] = target
    else:
        raise ValueError(f"알 수 없는 텍스트 컴포넌트입니다: {source}")
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def nbt_replacements() -> dict[str, list[tuple[tuple[str | int, ...], str, bool]]]:
    """현재 구조물에서 번역할 표시 문자열 21개를 반환한다."""
    corridor = [
        (
            (
                "entities",
                0,
                "nbt",
                "HandItems",
                0,
                "components",
                "minecraft:custom_name",
            ),
            "아자리엘의 활",
            True,
        ),
        (
            (
                "entities",
                1,
                "nbt",
                "Item",
                "components",
                "minecraft:custom_name",
            ),
            "즉사의 화살",
            True,
        ),
        (
            (
                "entities",
                2,
                "nbt",
                "Item",
                "components",
                "minecraft:custom_name",
            ),
            "아자리엘의 여정",
            True,
        ),
    ]
    for index, page in enumerate(BOOK_PAGES):
        corridor.append(
            (
                (
                    "entities",
                    2,
                    "nbt",
                    "Item",
                    "components",
                    "minecraft:writable_book_content",
                    "pages",
                    index,
                    "raw",
                ),
                page,
                False,
            )
        )
    return {
        CORRIDOR: corridor,
        MAIN: [
            (
                ("entities", 0, "nbt", "CustomName"),
                "끝없이 애태우는 크리퍼",
                True,
            )
        ],
        NORMAL_VAULT: [
            (
                (
                    "blocks",
                    0,
                    "nbt",
                    "config",
                    "key_item",
                    "components",
                    "minecraft:custom_name",
                ),
                "네더 시련 열쇠",
                True,
            )
        ],
        OMINOUS_VAULT: [
            (
                (
                    "blocks",
                    0,
                    "nbt",
                    "config",
                    "key_item",
                    "components",
                    "minecraft:custom_name",
                ),
                "불길한 네더 시련 열쇠",
                True,
            )
        ],
    }


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없이 JSON을 기록한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    """파일의 SHA-256을 계산한다."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_jar(instance: Path, pattern: str) -> Path:
    """현재 설치본에서 패턴에 맞는 JAR 하나를 찾는다."""
    jars = sorted((instance / "mods").glob(pattern))
    if len(jars) != 1:
        raise RuntimeError(
            f"대상 JAR 수가 1개가 아닙니다: {[path.name for path in jars]}"
        )
    return jars[0]


def read_gateways_english(jar: Path) -> dict[str, object]:
    """현재 Gateways JAR의 영어 언어 파일을 읽는다."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read(GATEWAYS_ENGLISH))
    if not isinstance(value, dict):
        raise TypeError("Gateways 영어 언어 파일이 객체가 아닙니다")
    return value


def prepare() -> dict[str, object]:
    """현재 두 JAR의 버전과 Gateways 영어 전체를 작업본에 기록한다."""
    instance = resolve_source_root()
    gateways = source_jar(instance, GATEWAYS_PATTERN)
    hellish = source_jar(instance, HELLISH_PATTERN)
    english = read_gateways_english(gateways)
    with ZipFile(gateways) as archive:
        bundled_korean = "assets/gateways/lang/ko_kr.json" in archive.namelist()
    with ZipFile(hellish) as archive:
        hellish_languages = sorted(
            name
            for name in archive.namelist()
            if "/lang/" in name and name.endswith(".json")
        )
    write_json(LANG_WORK_ROOT / "en_us.json", english)
    write_json(
        LANG_WORK_ROOT / "candidate_sources.json",
        {key: "manual_current_en_us" for key in english},
    )
    report = {
        "family": FAMILY,
        "jars": [
            {
                "name": gateways.name,
                "size": gateways.stat().st_size,
                "mtime_ns": gateways.stat().st_mtime_ns,
            },
            {
                "name": hellish.name,
                "size": hellish.stat().st_size,
                "mtime_ns": hellish.stat().st_mtime_ns,
            },
        ],
        "gateways_english_keys": len(english),
        "gateways_bundled_korean": bundled_korean,
        "hellish_language_files": hellish_languages,
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", report)
    return report


def replace_direct_text(value: object) -> int:
    """게이트웨이 JSON의 직접 표시 이름 하나를 한국어로 바꾼다."""
    count = 0
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "Name" and child == '{"text":"Wither Skeleton Spawner"}':
                value[key] = '{"text":"위더 스켈레톤 생성기"}'
                count += 1
            else:
                count += replace_direct_text(child)
    elif isinstance(value, list):
        for child in value:
            count += replace_direct_text(child)
    return count


def build() -> dict[str, object]:
    """언어 파일, 게이트웨이 데이터와 Hellish Trials 구조물 번역을 만든다."""
    instance = resolve_source_root()
    gateways = source_jar(instance, GATEWAYS_PATTERN)
    hellish = source_jar(instance, HELLISH_PATTERN)
    english = read_gateways_english(gateways)
    missing = sorted(set(english) - set(TRANSLATIONS))
    extra = sorted(set(TRANSLATIONS) - set(english))
    if missing or extra:
        raise KeyError(f"Gateways 번역표 불일치: 누락={missing}, 초과={extra}")
    korean = {key: TRANSLATIONS[key] for key in english}
    write_json(LANG_WORK_ROOT / "ko_kr.json", korean)
    write_json(LANG_OUTPUT, korean)

    with ZipFile(gateways) as archive:
        gateway_data = json.loads(archive.read(GATEWAY_DATA_PATH))
    replaced_gateway_names = replace_direct_text(gateway_data)
    if replaced_gateway_names != 1:
        raise RuntimeError(
            f"생성기 직접 이름 교체 수가 1개가 아닙니다: {replaced_gateway_names}"
        )
    write_json(GATEWAY_DATA_OUTPUT, gateway_data)

    nbt_rows = []
    replacements = nbt_replacements()
    with ZipFile(hellish) as archive:
        for internal, rows in replacements.items():
            root_name, root = read_nbt(gzip.decompress(archive.read(internal)))
            source_rows = []
            for path, target, is_component in rows:
                tag = get_tag(root, path)
                if tag.kind != 8 or not isinstance(tag.value, str):
                    raise TypeError(
                        f"번역 대상이 문자열 태그가 아닙니다: {internal}:{path}"
                    )
                source = tag.value
                if source.count("\n") != target.count("\n"):
                    raise ValueError(f"줄바꿈 수가 다릅니다: {internal}:{path}")
                tag.value = (
                    component_with_text(source, target) if is_component else target
                )
                source_rows.append(
                    {
                        "path": "/" + "/".join(map(str, path)),
                        "source": source,
                        "target": tag.value,
                    }
                )
            output = PROJECT_ROOT / "output/overrides/kubejs" / internal
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(gzip.compress(write_nbt(root_name, root), mtime=0))
            nbt_rows.append(
                {
                    "source": internal,
                    "output": output.relative_to(PROJECT_ROOT).as_posix(),
                    "translations": source_rows,
                }
            )
    write_json(WORK_ROOT / "hellish_nbt_translations.json", nbt_rows)
    report = {
        "language_keys": len(korean),
        "gateway_data_strings": replaced_gateway_names,
        "hellish_nbt_strings": sum(len(rows) for rows in replacements.values()),
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def walk_visible_nbt(tag: Tag, path: tuple[str | int, ...] = ()) -> list[str]:
    """사용자에게 보일 수 있는 NBT 컴포넌트·책 문자열 경로를 찾는다."""
    rows = []
    if tag.kind == 10:
        for name, child in tag.value.items():
            child_path = path + (name,)
            if child.kind == 8 and name in {
                "minecraft:custom_name",
                "CustomName",
                "raw",
            }:
                rows.append("/" + "/".join(map(str, child_path)))
            rows.extend(walk_visible_nbt(child, child_path))
    elif tag.kind == 9:
        for index, child in enumerate(tag.value[1]):
            rows.extend(walk_visible_nbt(child, path + (index,)))
    return rows


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR, 퀘스트, KubeJS와 데이터팩의 표시 경로를 전체 감사한다."""
    instance = resolve_source_root()
    gateways = source_jar(instance, GATEWAYS_PATTERN)
    hellish = source_jar(instance, HELLISH_PATTERN)
    errors = []
    visible_nbt = {}
    expected = nbt_replacements()
    with ZipFile(hellish) as archive:
        language_files = sorted(
            name
            for name in archive.namelist()
            if "/lang/" in name and name.endswith(".json")
        )
        guide_or_advancement = sorted(
            name
            for name in archive.namelist()
            if any(
                token in name.lower()
                for token in ("advancement", "patchouli", "guideme")
            )
        )
        for internal in sorted(
            name for name in archive.namelist() if name.endswith(".nbt")
        ):
            _, root = read_nbt(gzip.decompress(archive.read(internal)))
            paths = walk_visible_nbt(root)
            if paths:
                visible_nbt[internal] = paths
    expected_paths = {
        internal: ["/" + "/".join(map(str, path)) for path, _, _ in rows]
        for internal, rows in expected.items()
    }
    if visible_nbt != expected_paths:
        errors.append("Hellish Trials의 표시 NBT 경로가 검수 목록과 다릅니다")
    if language_files:
        errors.append(
            f"Hellish Trials에 예상하지 않은 언어 파일이 있습니다: {language_files}"
        )
    if guide_or_advancement:
        errors.append(
            "Hellish Trials에 예상하지 않은 가이드·발전과제가 있습니다: "
            + " | ".join(guide_or_advancement)
        )

    english_quests = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean_quests = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    required_english = {
        "quest.01EC5DB1A4A25B0B.quest_desc",
        "quest.22E57BF23B9BA2C5.quest_desc",
        "quest.6B5B01C612951BAF.quest_desc",
    }
    if not required_english <= set(english_quests):
        errors.append("관련 FTB Quests 영어 설명 키가 현재 원본에서 누락됐습니다")
    expected_quest_values = {
        "quest.01EC5DB1A4A25B0B.title": "게이트 진주",
        "quest.22E57BF23B9BA2C5.title": "월드 티어 게이트웨이",
        "quest.6B5B01C612951BAF.title": "&z게이트 진주 - 아포틱 침략자의 무한 게이트웨이",
    }
    for key, value in expected_quest_values.items():
        if korean_quests.get(key) != value:
            errors.append(f"FTB Quests 제목이 검수값과 다릅니다: {key}")
    for key in required_english:
        source_value = english_quests[key]
        target_value = korean_quests.get(key)
        if not isinstance(source_value, list) or not isinstance(target_value, list):
            errors.append(f"FTB Quests 설명 자료형이 목록이 아닙니다: {key}")
            continue
        source_text = "\n".join(source_value)
        target_text = "\n".join(target_value)
        for label, pattern in (("서식 코드", FORMAT_CODE), ("숫자", NUMBER)):
            if Counter(pattern.findall(source_text)) != Counter(
                pattern.findall(target_text)
            ):
                errors.append(f"FTB Quests {label} 보존이 다릅니다: {key}")
        if source_text.count("\\n") != target_text.count("\\n"):
            errors.append(f"FTB Quests 줄바꿈 보존이 다릅니다: {key}")
    quest_text = json.dumps(korean_quests, ensure_ascii=False)
    for required_text in (
        "평화적 몹",
        "월드 티어",
        "영원한 크레이그",
        "100개의 웨이브",
    ):
        if required_text not in quest_text:
            errors.append(f"FTB Quests 번역 문구가 누락됐습니다: {required_text}")
    if "Craig the Eternal" in quest_text:
        errors.append("관련 FTB Quests에 영문 Craig 이름이 남았습니다")

    tooltip = TOOLTIP_OUTPUT.read_text(encoding="utf-8")
    tooltip_lines = (
        "§c경고: 다음 차원 밖에서는 3번째 웨이브에 붕괴합니다:",
        "§c오버월드, 네더, 엔드, 황혼의 숲",
    )
    if any(line not in tooltip for line in tooltip_lines):
        errors.append("Apotheosis 게이트 진주의 KubeJS 경고 번역이 누락됐습니다")

    apotheosis_language = load_json(
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/apotheosis/lang/ko_kr.json"
    )
    expected_apotheosis_keys = {
        "apotheosis.tiered/frontier",
        "apotheosis.tiered/ascent",
        "apotheosis.tiered/summit",
        "apotheosis.tiered/pinnacle",
        "apotheosis.endless_invader",
    }
    apotheosis_keys = sorted(expected_apotheosis_keys & set(apotheosis_language))
    if set(apotheosis_keys) != expected_apotheosis_keys:
        errors.append(f"Apotheosis 게이트웨이 연동 키가 다릅니다: {apotheosis_keys}")

    with ZipFile(gateways) as archive:
        source_gateway_data = json.loads(archive.read(GATEWAY_DATA_PATH))
    source_text = json.dumps(source_gateway_data, ensure_ascii=False)
    if source_text.count("Wither Skeleton Spawner") != 1:
        errors.append("Gateways 데이터의 직접 표시 생성기 이름 수가 1개가 아닙니다")

    report = {
        "family": FAMILY,
        "gateways_language_keys": len(read_gateways_english(gateways)),
        "gateways_direct_data_strings": 1,
        "hellish_language_files": language_files,
        "hellish_guide_or_advancement_files": guide_or_advancement,
        "hellish_visible_nbt_paths": visible_nbt,
        "hellish_visible_nbt_strings": sum(
            len(paths) for paths in visible_nbt.values()
        ),
        "ftbquests_reviewed": sorted(required_english),
        "apotheosis_integration_keys": apotheosis_keys,
        "kubejs_warning_lines": list(tooltip_lines),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def verify_language() -> tuple[dict[str, object], list[str]]:
    """Gateways 언어 키·자료형·자리표시자·서식을 검증한다."""
    instance = resolve_source_root()
    jar = source_jar(instance, GATEWAYS_PATTERN)
    source = read_gateways_english(jar)
    working = load_json(LANG_WORK_ROOT / "en_us.json")
    korean = load_json(LANG_WORK_ROOT / "ko_kr.json")
    output = load_json(LANG_OUTPUT)
    errors = []
    untranslated = []
    latin_residue = {}
    if source != working:
        errors.append("작업 영어가 현재 JAR 영어와 다릅니다")
    if list(source) != list(korean):
        errors.append("한국어 키 또는 키 순서가 영어 원문과 다릅니다")
    if korean != output:
        errors.append("작업 한국어와 리소스팩 산출물이 다릅니다")
    for key in source.keys() & korean.keys():
        original = source[key]
        target = korean[key]
        if type(original) is not type(target):
            errors.append(f"자료형 불일치: {key}")
            continue
        if not isinstance(original, str) or not isinstance(target, str):
            continue
        for label, pattern in (
            ("자리표시자", PLACEHOLDER),
            ("서식 코드", FORMAT_CODE),
            ("숫자", NUMBER),
        ):
            if Counter(pattern.findall(original)) != Counter(pattern.findall(target)):
                errors.append(f"{label} 불일치: {key}")
        if original.count("\n") != target.count("\n"):
            errors.append(f"줄바꿈 불일치: {key}")
        if original == target and key not in INTENTIONAL_SAME_KEYS | {
            "itemGroup.gateways"
        }:
            untranslated.append(key)
        residue = sorted(set(LATIN_WORD.findall(target)) - ALLOWED_LATIN)
        if residue:
            latin_residue[key] = residue
    allowed_collisions = {
        frozenset({"tooltip.gateways.num_wave", "tooltip.gateways.num_waves"}),
        frozenset({"tooltip.gateways.num_failures", "tooltip.gateways.num_failure"}),
        frozenset({"tooltip.gateways.num_rule", "tooltip.gateways.num_rules"}),
        frozenset(
            {
                "tooltip.gateways.endless.num_modif",
                "tooltip.gateways.endless.num_modifs",
            }
        ),
    }
    collisions = defaultdict(list)
    for key, value in korean.items():
        collisions[value].append(key)
    unexpected_collisions = {
        value: keys
        for value, keys in collisions.items()
        if len(keys) > 1
        and len({source[key] for key in keys}) > 1
        and frozenset(keys) not in allowed_collisions
    }
    if untranslated:
        errors.append(f"영어와 같은 미번역 후보: {untranslated}")
    if latin_residue:
        errors.append(f"허용하지 않은 영문 잔여: {latin_residue}")
    if unexpected_collisions:
        errors.append(f"서로 다른 영어의 한국어 충돌: {unexpected_collisions}")
    return {
        "keys": len(source),
        "untranslated_candidates": untranslated,
        "latin_residue": latin_residue,
        "unexpected_name_collisions": unexpected_collisions,
        "errors": errors,
    }, errors


def verify_data_outputs() -> tuple[dict[str, object], list[str]]:
    """데이터 JSON과 NBT가 지정한 표시 문자열만 바뀌었는지 검증한다."""
    instance = resolve_source_root()
    gateways = source_jar(instance, GATEWAYS_PATTERN)
    hellish = source_jar(instance, HELLISH_PATTERN)
    errors = []
    with ZipFile(gateways) as archive:
        source_gateway = json.loads(archive.read(GATEWAY_DATA_PATH))
    expected_gateway = deepcopy(source_gateway)
    replace_direct_text(expected_gateway)
    output_gateway = load_json(GATEWAY_DATA_OUTPUT)
    if expected_gateway != output_gateway:
        errors.append("Gateways 데이터 산출물이 지정한 한 문자열 외에도 다릅니다")

    nbt_verified = []
    with ZipFile(hellish) as archive:
        for internal, rows in nbt_replacements().items():
            source_name, expected_root = read_nbt(
                gzip.decompress(archive.read(internal))
            )
            source_root = deepcopy(expected_root)
            for path, target, is_component in rows:
                source_tag = get_tag(source_root, path)
                expected_tag = get_tag(expected_root, path)
                expected_tag.value = (
                    component_with_text(source_tag.value, target)
                    if is_component
                    else target
                )
                if source_tag.value.count("\n") != target.count("\n"):
                    errors.append(f"NBT 줄바꿈 수가 다릅니다: {internal}:{path}")
                if Counter(NUMBER.findall(source_tag.value)) != Counter(
                    NUMBER.findall(target)
                ):
                    errors.append(f"NBT 숫자 보존이 다릅니다: {internal}:{path}")
            output = PROJECT_ROOT / "output/overrides/kubejs" / internal
            output_name, output_root = read_nbt(gzip.decompress(output.read_bytes()))
            if output_name != source_name or output_root != expected_root:
                errors.append(f"NBT 산출물에 지정하지 않은 차이가 있습니다: {internal}")
            if read_nbt(write_nbt(output_name, output_root)) != (
                output_name,
                output_root,
            ):
                errors.append(f"NBT 재직렬화 검증에 실패했습니다: {internal}")
            nbt_verified.append(
                {
                    "path": internal,
                    "strings": len(rows),
                    "output_sha256": sha256(output),
                }
            )
    return {
        "gateway_json_verified": output_gateway == expected_gateway,
        "hellish_nbt_files": nbt_verified,
        "hellish_nbt_strings": sum(row["strings"] for row in nbt_verified),
        "errors": errors,
    }, errors


def output_paths() -> list[str]:
    """이번 모드 단위의 적용 대상 8개를 반환한다."""
    paths = [
        "resourcepacks/ATM10_Korean/assets/gateways/lang/ko_kr.json",
        "config/ftbquests/quests/lang/ko_kr.snbt",
        "kubejs/client_scripts/tooltips.js",
        f"kubejs/{GATEWAY_DATA_PATH}",
    ]
    paths.extend(f"kubejs/{path}" for path in nbt_replacements())
    return paths


def output_source(relative: str) -> Path:
    """적용 상대 경로를 저장소 산출물 경로로 바꾼다."""
    prefix = "resourcepacks/"
    if relative.startswith(prefix):
        return PROJECT_ROOT / "output/resourcepack" / relative.removeprefix(prefix)
    return PROJECT_ROOT / "output/overrides" / relative


def verify() -> tuple[dict[str, object], list[str]]:
    """모든 산출물과 완료 경계를 통합 검증한다."""
    language, language_errors = verify_language()
    data, data_errors = verify_data_outputs()
    audit_report = load_json(WORK_ROOT / "surface_audit.json")
    errors = language_errors + data_errors
    if audit_report.get("status") != "complete":
        errors.append("표시 표면 감사가 완료되지 않았습니다")
    parsed_quests = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    if len(parsed_quests) < 8000:
        errors.append("누적 FTB Quests 한국어 SNBT 키 수가 예상보다 적습니다")
    report = {
        "family": FAMILY,
        "language": language,
        "data": data,
        "quest_language_keys": len(parsed_quests),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "validation.json", report)
    completion = {
        "family": FAMILY,
        "versions": {"gateways": "5.1.0", "hellish_trials": "1.0.5"},
        "language_keys": 96,
        "gateway_data_strings": 1,
        "hellish_nbt_strings": 21,
        "ftbquests": {
            "new_keys": 3,
            "corrected_keys": 1,
            "reviewed_existing_keys": 2,
        },
        "kubejs_corrected_strings": 2,
        "existing_korean_reused": 2,
        "new_or_corrected_translations": 124,
        "output_files": output_paths(),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    completion_path = WORK_ROOT / "family_completion.json"
    if completion_path.is_file():
        previous_completion = load_json(completion_path)
        if "deployment" in previous_completion:
            completion["deployment"] = previous_completion["deployment"]
    write_json(completion_path, completion)
    return report, errors


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 스크립트의 백업·해시 결과를 완료 기록에 반영한다."""
    resolved = manifest_path.resolve()
    try:
        relative_manifest = resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError as exc:
        raise ValueError(f"프로젝트 밖의 적용 기록입니다: {resolved}") from exc
    manifest = load_json(resolved)
    expected = set(output_paths())
    errors = []
    matched = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 기록 상태가 applied_and_verified가 아닙니다")
    targets = manifest.get("targets")
    if not isinstance(targets, list):
        targets = []
        errors.append("적용 기록의 targets가 목록이 아닙니다")
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
            target_file = Path(str(row.get("target")))
            if not target_file.is_file():
                errors.append(f"적용 대상이 없습니다: {target_file}")
                continue
            source_file = output_source(relative)
            if not source_file.is_file() or sha256(target_file) != sha256(source_file):
                errors.append(
                    f"적용 대상과 저장소 산출물의 해시가 다릅니다: {relative}"
                )
            if row.get("source_sha256") != row.get("after_sha256"):
                errors.append(f"적용 전후 해시가 다릅니다: {relative}")
        matched.append(target)
    if len(matched) != 1:
        errors.append(f"일치하는 적용 대상 기록 수가 1개가 아닙니다: {len(matched)}")
    target = matched[0] if matched else {}
    deployment = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "target": target.get("target_root"),
        "changed_paths": target.get("changed_paths", []),
        "backup_manifest": relative_manifest,
        "errors": errors,
    }
    completion_path = WORK_ROOT / "family_completion.json"
    completion = load_json(completion_path)
    completion["deployment"] = deployment
    if errors:
        completion["status"] = "incomplete"
    write_json(completion_path, completion)
    return deployment, errors


def run_all() -> tuple[dict[str, object], list[str]]:
    """준비, 생성, 감사와 검증을 순서대로 실행한다."""
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "build", "audit", "verify", "record-deployment", "all"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        report, errors = prepare(), []
    elif args.command == "build":
        report, errors = build(), []
    elif args.command == "audit":
        report, errors = audit()
    elif args.command == "verify":
        report, errors = verify()
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요합니다")
        report, errors = record_deployment(args.manifest)
    else:
        report, errors = run_all()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
