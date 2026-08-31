#!/usr/bin/env python3
"""Everything is Copper·Dyenamics와 직접 연동 표시를 번역하고 검증해요."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

FAMILY = "copper_dyenamics"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"
COPPER_OUTPUT = OUTPUT_ASSETS / "everythingcopper/lang/ko_kr.json"
DYENAMICS_OUTPUT = OUTPUT_ASSETS / "dyenamics/lang/ko_kr.json"
FRIENDS_OUTPUT = OUTPUT_ASSETS / "dyenamicsandfriends/lang/ko_kr.json"
QUEST_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
CATACLYSM_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/chapters/cataclysm.snbt"
)
CATACLYSM_SOURCE_COPY = WORK_ROOT / "ftbquests/cataclysm_source.snbt"
DEPLOYMENT_PATHS = {
    "resourcepacks/ATM10_Korean/assets/everythingcopper/lang/ko_kr.json",
    "resourcepacks/ATM10_Korean/assets/dyenamics/lang/ko_kr.json",
    "resourcepacks/ATM10_Korean/assets/dyenamicsandfriends/lang/ko_kr.json",
    "config/ftbquests/quests/lang/ko_kr.snbt",
    "config/ftbquests/quests/chapters/cataclysm.snbt",
}
JARS = {
    "everythingcopper": "everythingcopper-*.jar",
    "dyenamics": "dyenamics-*.jar",
    "dyenamicsandfriends": "dyenamicsandfriends-*.jar",
}
LANGUAGE_PATHS = {mod_id: f"assets/{mod_id}/lang/en_us.json" for mod_id in JARS}
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[.]\d+)?")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")

DYENAMICS_COLORS = {
    "Amber": "호박색",
    "Aquamarine": "아쿠아마린색",
    "Bubblegum": "풍선껌색",
    "Cherenkov": "체렌코프색",
    "Conifer": "침엽수색",
    "Fluorescent": "형광색",
    "Honey": "꿀색",
    "Icy Blue": "얼음빛 파란색",
    "Lavender": "라벤더색",
    "Maroon": "적갈색",
    "Mint": "민트색",
    "Navy": "남색",
    "Peach": "복숭아색",
    "Persimmon": "감색",
    "Rose": "장미색",
    "Spring Green": "봄 초록색",
    "Ultramarine": "울트라마린색",
    "Wine": "와인색",
}

DYENAMICS_OBJECTS = {
    "Banner": "현수막",
    "Bed": "침대",
    "Candle": "양초",
    "Carpet": "양탄자",
    "Concrete": "콘크리트",
    "Concrete Powder": "콘크리트 가루",
    "Dye": "염료",
    "Glazed Terracotta": "유광 테라코타",
    "Rockwool": "암면",
    "Shulker Box": "셜커 상자",
    "Stained Glass": "색유리",
    "Stained Glass Pane": "색유리 판",
    "Terracotta": "테라코타",
    "Wool": "양털",
}

COPPER_OBJECTS = {
    "Anvil": "모루",
    "Axe": "도끼",
    "Bars": "창살",
    "Boots": "부츠",
    "Bucket": "양동이",
    "Bulb": "전구",
    "Button": "버튼",
    "Cauldron": "가마솥",
    "Chain": "사슬",
    "Chestplate": "흉갑",
    "Door": "문",
    "Golem": "골렘",
    "Grate": "격자",
    "Helmet": "투구",
    "Hoe": "괭이",
    "Hopper": "호퍼",
    "Horse Armor": "말 갑옷",
    "Ladder": "사다리",
    "Lantern": "랜턴",
    "Leggings": "레깅스",
    "Minecart": "광산 수레",
    "Nugget": "조각",
    "Pickaxe": "곡괭이",
    "Pressure Plate": "감압판",
    "Rail": "레일",
    "Shears": "가위",
    "Shield": "방패",
    "Shovel": "삽",
    "Soul Lantern": "영혼 랜턴",
    "Sword": "검",
    "Trapdoor": "다락문",
}

COPPER_STATIC = {
    "everythingcopper.recipe.weathering": "풍화 처리",
    "everythingcopper.screen.empty": "비어 있음",
    "everythingcopper.screen.fluid_level": "%s: %s",
    "everythingcopper.screen.fuel_time": "남은 시간: %s",
    "everythingcopper.bulb.tip1": ("레드스톤 신호를 받으면 상태가 전환됩니다."),
    "everythingcopper.bulb.tip2": (
        "발광석 가루를 사용하면 최대 밝기가 되고, 레드스톤 횃불을 사용하면 "
        "손으로 켜고 끌 수 있습니다."
    ),
    "death.attack.everythingcopper.copper_poisoning": (
        "%1$s이(가) 구리 중독으로 사망했습니다"
    ),
    "death.attack.everythingcopper.copper_poisoning.player": (
        "%1$s이(가) %2$s와(과) 놀다가 구리 중독으로 사망했습니다"
    ),
    "death.attack.everythingcopper.copper_poisoning1": (
        "%1$s은(는) 구리를 먹다 마지막 이가 깨졌습니다..."
    ),
    "death.attack.everythingcopper.copper_poisoning1.player": (
        "%1$s은(는) %2$s을(를) 간질이며 구리를 먹다 마지막 이가 깨졌습니다"
    ),
    "death.attack.everythingcopper.copper_poisoning2": (
        "구리 중독이 %1$s을(를) 쓰러뜨렸습니다"
    ),
    "death.attack.everythingcopper.copper_poisoning2.player": (
        "구리 중독이 %1$s을(를) 쓰러뜨렸습니다. 모두 %2$s 탓입니다"
    ),
    "death.attack.everythingcopper.copper_poisoning3": (
        "%1$s은(는) 구리 조각이 목에 걸렸습니다. 얘들아, 금속은 먹지 마세요!"
    ),
    "death.attack.everythingcopper.copper_poisoning3.player": (
        "%1$s은(는) %2$s에게서 달아나며 구리 조각을 먹다 목에 걸렸습니다. "
        "달리면서 먹지 마세요."
    ),
    "advancements.adventure.consume_copper_nugget.title": "이가 깨지는 맛",
    "advancements.adventure.consume_copper_nugget.description": (
        "구리 조각을 먹으세요. 건강에 아주 좋답니다."
    ),
    "advancements.adventure.summon_copper_golem.title": "골렘 팔레트",
    "advancements.adventure.summon_copper_golem.description": (
        "구리 골렘을 소환하세요. 구리가 너무 많이 남았다는 것 외에는 "
        "특별한 이유가 없습니다."
    ),
}

QUEST_CORRECTIONS = {
    "quest.50B127137AA9E660.quest_desc": ["드디어 &6구리&r가 제대로 쓰이게 되었어요!"],
    "quest.50B127137AA9E660.quest_subtitle": "13",
    "quest.50B127137AA9E660.title": "&6구리 갑옷",
    "quest.4745488579AAF603.quest_subtitle": "&f5.8 &c공격 피해",
    "quest.64EED65F80A91D9E.quest_subtitle": "티어: &b3",
    "task.18DA9065596F9097.title": "모드 추가 금속 곡괭이",
    "task.4732C2BE50DB2A80.title": "Dyenamics 염료",
}
RELATED_QUEST_IDS = {
    "50B127137AA9E660",
    "4745488579AAF603",
    "64EED65F80A91D9E",
    "18DA9065596F9097",
    "4732C2BE50DB2A80",
}
CUSTOM_NAME_SOURCE = '"minecraft:custom_name": "\\"ATM Star Block\\""'
CUSTOM_NAME_TARGET = '"minecraft:custom_name": "\\"ATM 스타 블록\\""'
INTENTIONAL_SAME = {"everythingcopper.screen.fluid_level"}

FRIENDS_SUFFIXES = {
    "String Curtain": "실 커튼",
    "Super Candle Base": "대형 양초 받침",
    "Fire Bricks": "내화 벽돌",
    "Foundry Capacitor": "주조소 축전기",
    "Foundry Controller": "주조소 제어기",
    "Foundry Drain": "주조소 배출구",
    "Foundry Tank": "주조소 탱크",
    "Foundry Window": "주조소 창",
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽어요."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아니에요: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 읽기 쉬운 형태로 기록해요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def read_tracked_json(relative: str) -> dict[str, object]:
    """현재 작업 전 커밋에 있던 JSON 후보를 읽어요."""
    result = subprocess.run(
        ["git", "show", f"HEAD:{relative}"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    value = json.loads(result.stdout)
    if not isinstance(value, dict):
        raise TypeError(f"Git의 JSON 후보가 객체가 아니에요: {relative}")
    return value


def sha256(path: Path) -> str:
    """파일 SHA-256을 계산해요."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_jars(instance: Path) -> dict[str, Path]:
    """세 모드의 현재 JAR을 하나씩 찾아요."""
    found = {}
    for mod_id, pattern in JARS.items():
        matches = sorted((instance / "mods").glob(pattern))
        if len(matches) != 1:
            raise FileNotFoundError(f"{mod_id} JAR 수가 1개가 아니에요: {matches}")
        found[mod_id] = matches[0]
    return found


def read_jar_language(jar: Path, mod_id: str) -> dict[str, object]:
    """현재 JAR의 영어 언어 파일을 읽어요."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read(LANGUAGE_PATHS[mod_id]))
    if not isinstance(value, dict):
        raise TypeError(f"JAR 언어 파일이 객체가 아니에요: {jar.name}")
    return value


def material_prefix(waxed: str | None, damage: str | None, state: str | None) -> str:
    """구리의 밀랍·손상·산화 상태를 이름 순서에 맞게 번역해요."""
    parts = []
    if waxed:
        parts.append("밀랍칠한")
    if damage == "Chipped ":
        parts.append("금이 간")
    elif damage == "Damaged ":
        parts.append("손상된")
    state_names = {
        "Exposed ": "노출된",
        "Weathered ": "풍화된",
        "Oxidized ": "산화된",
    }
    if state:
        parts.append(state_names[state])
    parts.append("구리")
    return " ".join(parts)


def translate_copper_name(source: str) -> str:
    """Everything is Copper의 구조화된 엔티티·블록·아이템 이름을 번역해요."""
    if source == "Weathering Station":
        return "풍화 처리대"
    wip = source.endswith(" [WIP]")
    core = source.removesuffix(" [WIP]")
    chiseled = re.fullmatch(
        r"(Waxed )?(Exposed |Weathered |Oxidized )?Chiseled Copper",
        core,
    )
    if chiseled:
        material = material_prefix(chiseled.group(1), None, chiseled.group(2))
        target = f"{material} 조각 블록"
        return f"{target} [개발 중]" if wip else target
    match = re.fullmatch(
        r"(Waxed )?(Chipped |Damaged )?" r"(Exposed |Weathered |Oxidized )?Copper (.+)",
        core,
    )
    if not match:
        raise ValueError(f"처리하지 않은 Everything is Copper 이름이에요: {source}")
    material = material_prefix(match.group(1), match.group(2), match.group(3))
    object_name = match.group(4)
    attachment = re.fullmatch(r"Minecart with (.+)", object_name)
    if attachment:
        carried = {
            "Chest": "상자",
            "Command Block": "명령 블록",
            "Furnace": "화로",
            "Hopper": "호퍼",
            "Spawner": "생성기",
            "TNT": "TNT",
        }.get(attachment.group(1))
        if carried is None:
            raise ValueError(f"처리하지 않은 구리 광산 수레 부착물이에요: {source}")
        target = f"{carried}가 실린 {material} 광산 수레"
    else:
        translated_object = COPPER_OBJECTS.get(object_name)
        if translated_object is None:
            raise ValueError(f"처리하지 않은 구리 물체 이름이에요: {source}")
        target = f"{material} {translated_object}"
    return f"{target} [개발 중]" if wip else target


def translate_copper(english: dict[str, object]) -> dict[str, str]:
    """Everything is Copper 영어 356키 전체를 번역해요."""
    translated = {}
    for key, source in english.items():
        if not isinstance(source, str):
            raise TypeError(f"문자열이 아닌 영어 값이 있어요: {key}")
        if key.startswith(("entity.", "block.", "item.")):
            translated[key] = translate_copper_name(source)
        elif key in COPPER_STATIC:
            translated[key] = COPPER_STATIC[key]
        else:
            raise KeyError(f"검수되지 않은 Everything is Copper 키예요: {key}")
    if len(translated) != 356:
        raise ValueError(
            f"Everything is Copper 키가 356개가 아니에요: {len(translated)}"
        )
    return translated


def split_color_name(source: str) -> tuple[str, str]:
    """Dyenamics 색상 이름과 뒤쪽 물체 이름을 분리해요."""
    for color in sorted(DYENAMICS_COLORS, key=len, reverse=True):
        if source.startswith(f"{color} "):
            return color, source[len(color) + 1 :]
    raise ValueError(f"검수되지 않은 Dyenamics 색상 이름이에요: {source}")


def translate_dyenamics(english: dict[str, object]) -> dict[str, str]:
    """Dyenamics의 18색 블록·염료 253키 전체를 번역해요."""
    translated = {}
    for key, source in english.items():
        if not isinstance(source, str):
            raise TypeError(f"문자열이 아닌 영어 값이 있어요: {key}")
        if key == "entity.dyenamics.sheep":
            translated[key] = "양"
            continue
        color, object_name = split_color_name(source)
        translated_object = DYENAMICS_OBJECTS.get(object_name)
        if translated_object is None:
            raise ValueError(f"검수되지 않은 Dyenamics 물체 이름이에요: {source}")
        translated[key] = f"{DYENAMICS_COLORS[color]} {translated_object}"
    if len(translated) != 253:
        raise ValueError(f"Dyenamics 키가 253개가 아니에요: {len(translated)}")
    return translated


def scoped_friends_english(english: dict[str, object]) -> dict[str, str]:
    """기존 완료 모드와 직접 연결된 Dyenamics and Friends 146키를 골라요."""
    scoped = {
        key: value
        for key, value in english.items()
        if key.startswith(
            (
                "block.dyenamicsandfriends.bumblezone_",
                "block.dyenamicsandfriends.productivemetalworks_",
            )
        )
        or key
        in {
            "resourcePack.dyenamicsandfriends.the_bumblezone",
            "resourcePack.dyenamicsandfriends.productivemetalworks",
        }
    }
    if len(scoped) != 146:
        raise ValueError(
            f"Dyenamics and Friends 직접 연동 키가 146개가 아니에요: {len(scoped)}"
        )
    if not all(isinstance(value, str) for value in scoped.values()):
        raise TypeError("Dyenamics and Friends 연동 값에 문자열 아닌 항목이 있어요")
    return scoped  # type: ignore[return-value]


def translate_friends(english: dict[str, str]) -> dict[str, str]:
    """기존 146개 연동 이름의 색상 용어를 현재 기준과 일치시켜요."""
    translated = {}
    resource_names = {
        "resourcePack.dyenamicsandfriends.the_bumblezone": (
            "Dyenamics And Friends - The Bumblezone"
        ),
        "resourcePack.dyenamicsandfriends.productivemetalworks": (
            "Dyenamics And Friends - Productive Metalworks"
        ),
    }
    for key, source in english.items():
        if key in resource_names:
            translated[key] = resource_names[key]
            continue
        color, object_name = split_color_name(source)
        translated_object = FRIENDS_SUFFIXES.get(object_name)
        if translated_object is None:
            raise ValueError(f"검수되지 않은 연동 물체 이름이에요: {source}")
        translated[key] = f"{DYENAMICS_COLORS[color]} {translated_object}"
    return translated


def prepare() -> dict[str, object]:
    """현재 세 JAR과 기존 한국어 후보를 작업 폴더에 기록해요."""
    instance = resolve_source_root()
    jars = find_jars(instance)
    languages = {}
    inventory_rows = []
    for mod_id, jar in jars.items():
        english = read_jar_language(jar, mod_id)
        languages[mod_id] = english
        write_json(WORK_ROOT / mod_id / "en_us.json", english)
        with ZipFile(jar) as archive:
            bundled_languages = sorted(
                name
                for name in archive.namelist()
                if name.startswith(f"assets/{mod_id}/lang/") and name.endswith(".json")
            )
        inventory_rows.append(
            {
                "mod_id": mod_id,
                "jar": jar.name,
                "jar_size": jar.stat().st_size,
                "jar_mtime_ns": jar.stat().st_mtime_ns,
                "english_keys": len(english),
                "bundled_languages": bundled_languages,
                "bundled_korean_keys": 0,
            }
        )
    existing_friends = read_tracked_json(
        "output/7.1/resourcepack/ATM10_Korean/assets/dyenamicsandfriends/lang/ko_kr.json"
    )
    write_json(
        WORK_ROOT / "dyenamicsandfriends/candidate_ko_kr.json",
        existing_friends,
    )
    friends_scoped = scoped_friends_english(languages["dyenamicsandfriends"])
    candidates = {
        "everythingcopper_existing_korean_keys": 0,
        "dyenamics_existing_korean_keys": 0,
        "dyenamicsandfriends_project_candidate_keys": len(existing_friends),
        "dyenamicsandfriends_scoped_candidate_keys": len(
            set(existing_friends) & set(friends_scoped)
        ),
        "foreign_bundled_languages_used": False,
    }
    inventory = {
        "family": FAMILY,
        "jars": inventory_rows,
        "main_language_keys": (
            len(languages["everythingcopper"]) + len(languages["dyenamics"])
        ),
        "dyenamicsandfriends_total_keys": len(languages["dyenamicsandfriends"]),
        "dyenamicsandfriends_scoped_integration_keys": len(friends_scoped),
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", inventory)
    write_json(WORK_ROOT / "candidate_sources.json", candidates)
    return inventory


def build_cataclysm_override(instance: Path) -> dict[str, object]:
    """Dyenamics 블록 보상의 사용자 지정 영어 이름 한 곳을 번역해요."""
    source_path = instance / "config/ftbquests/quests/chapters/cataclysm.snbt"
    if CATACLYSM_SOURCE_COPY.is_file():
        source = CATACLYSM_SOURCE_COPY.read_text(encoding="utf-8")
    else:
        source = source_path.read_text(encoding="utf-8")
        CATACLYSM_SOURCE_COPY.parent.mkdir(parents=True, exist_ok=True)
        CATACLYSM_SOURCE_COPY.write_text(source, encoding="utf-8")
    if source.count(CUSTOM_NAME_SOURCE) != 1:
        raise ValueError(
            "Cataclysm의 ATM Star Block 사용자 지정 이름이 한 곳이 아니에요"
        )
    target = source.replace(CUSTOM_NAME_SOURCE, CUSTOM_NAME_TARGET)
    CATACLYSM_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    CATACLYSM_OUTPUT.write_text(target, encoding="utf-8")
    return {
        "source": source_path.relative_to(instance).as_posix(),
        "output": CATACLYSM_OUTPUT.relative_to(PROJECT_ROOT).as_posix(),
        "custom_name_translations": 1,
    }


def build_quests(instance: Path) -> dict[str, object]:
    """관련 퀘스트 7키를 전체 언어 파일에 안전하게 병합해요."""
    candidate_path = instance / "config/ftbquests/quests/lang/ko_kr.snbt"
    candidate = quest_snbt.parse_language_snbt(candidate_path)
    merge_source = QUEST_OUTPUT if QUEST_OUTPUT.is_file() else candidate_path
    merged = quest_snbt.merge_into_full_snbt(merge_source, QUEST_CORRECTIONS)
    QUEST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    merged_values = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    for key, expected in QUEST_CORRECTIONS.items():
        if merged_values.get(key) != expected:
            raise ValueError(f"퀘스트 병합 결과가 달라요: {key}")
    reused = sum(
        candidate.get(key) == value for key, value in QUEST_CORRECTIONS.items()
    )
    return {
        "reviewed_keys": len(QUEST_CORRECTIONS),
        "existing_korean_reused": reused,
        "new_or_corrected": len(QUEST_CORRECTIONS) - reused,
    }


def build() -> dict[str, object]:
    """두 본체 609키와 직접 연동·퀘스트 산출물을 만들어요."""
    instance = resolve_source_root()
    copper_english = load_json(WORK_ROOT / "everythingcopper/en_us.json")
    dyenamics_english = load_json(WORK_ROOT / "dyenamics/en_us.json")
    friends_english = scoped_friends_english(
        load_json(WORK_ROOT / "dyenamicsandfriends/en_us.json")
    )
    copper_korean = translate_copper(copper_english)
    dyenamics_korean = translate_dyenamics(dyenamics_english)
    friends_korean = translate_friends(friends_english)
    existing_friends = load_json(WORK_ROOT / "dyenamicsandfriends/candidate_ko_kr.json")
    friends_reused = sum(
        existing_friends.get(key) == value for key, value in friends_korean.items()
    )
    merged_friends = load_json(FRIENDS_OUTPUT)
    merged_friends.update(friends_korean)
    write_json(WORK_ROOT / "everythingcopper/ko_kr.json", copper_korean)
    write_json(WORK_ROOT / "dyenamics/ko_kr.json", dyenamics_korean)
    write_json(WORK_ROOT / "dyenamicsandfriends/ko_kr.json", friends_korean)
    write_json(COPPER_OUTPUT, copper_korean)
    write_json(DYENAMICS_OUTPUT, dyenamics_korean)
    write_json(FRIENDS_OUTPUT, merged_friends)
    quests = build_quests(instance)
    cataclysm = build_cataclysm_override(instance)
    report = {
        "reviewed_main_language_keys": len(copper_korean) + len(dyenamics_korean),
        "existing_main_korean_reused": 0,
        "new_main_translations": len(copper_korean) + len(dyenamics_korean),
        "everythingcopper_keys": len(copper_korean),
        "dyenamics_keys": len(dyenamics_korean),
        "dyenamicsandfriends_reviewed_integration_keys": len(friends_korean),
        "dyenamicsandfriends_existing_reused": friends_reused,
        "dyenamicsandfriends_existing_corrected": (
            len(friends_korean) - friends_reused
        ),
        "quests": quests,
        "cataclysm_override": cataclysm,
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def advancement_surfaces(
    jar: Path, english: dict[str, object]
) -> tuple[dict[str, object], list[str]]:
    """발전 과제 표시가 언어 키를 통하는지 확인해요."""
    errors = []
    translated_keys = []
    direct_text = []
    files = []
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            if "/advancement" not in name or not name.endswith(".json"):
                continue
            files.append(name)
            value = json.loads(archive.read(name))
            display = value.get("display") if isinstance(value, dict) else None
            if not isinstance(display, dict):
                continue
            for field in ("title", "description"):
                component = display.get(field)
                if isinstance(component, dict) and isinstance(
                    component.get("translate"), str
                ):
                    key = component["translate"]
                    translated_keys.append(key)
                    if key not in english:
                        errors.append(
                            f"발전 과제 언어 키가 영어 파일에 없어요: {name}:{key}"
                        )
                elif isinstance(component, str):
                    direct_text.append(f"{name}:{field}={component}")
    if direct_text:
        errors.append(f"발전 과제에 직접 영어 문구가 있어요: {direct_text}")
    return {
        "files": len(files),
        "translated_display_keys": translated_keys,
        "direct_display_text": direct_text,
    }, errors


def audit_references(instance: Path) -> dict[str, object]:
    """관련 FTB Quests와 KubeJS 참조를 파일 단위로 모아요."""
    references = {"ftbquests": [], "kubejs": [], "read_errors": []}
    for label, base in (
        ("ftbquests", instance / "config/ftbquests/quests/chapters"),
        ("kubejs", instance / "kubejs"),
    ):
        for path in sorted(base.rglob("*"), key=lambda item: item.as_posix().lower()):
            if not path.is_file() or path.suffix.lower() not in {
                ".js",
                ".json",
                ".snbt",
            }:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                references["read_errors"].append(
                    f"{path.relative_to(instance).as_posix()}: {exc}"
                )
                continue
            hits = [
                term
                for term in ("everythingcopper", "dyenamics", "dyenamicsandfriends")
                if term in text.lower()
            ]
            if hits:
                references[label].append(
                    {
                        "path": path.relative_to(instance).as_posix(),
                        "namespaces": hits,
                        "custom_name_literals": text.count('"minecraft:custom_name"'),
                    }
                )
    return references


def audit() -> tuple[dict[str, object], list[str]]:
    """발전 과제·퀘스트·KubeJS와 연동 용어 범위를 감사해요."""
    instance = resolve_source_root()
    jars = find_jars(instance)
    errors = []
    advancement_reports = {}
    for mod_id, jar in jars.items():
        english = read_jar_language(jar, mod_id)
        report, report_errors = advancement_surfaces(jar, english)
        advancement_reports[mod_id] = report
        errors.extend(report_errors)
    references = audit_references(instance)
    errors.extend(str(value) for value in references["read_errors"])
    english_quests = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean_quests = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    related_keys = sorted(
        key
        for key in english_quests
        if any(identifier in key for identifier in RELATED_QUEST_IDS)
    )
    if set(related_keys) != set(QUEST_CORRECTIONS):
        errors.append(
            "관련 퀘스트 키 범위가 예상과 달라요: "
            f"{sorted(set(related_keys) ^ set(QUEST_CORRECTIONS))}"
        )
    for key, expected in QUEST_CORRECTIONS.items():
        if korean_quests.get(key) != expected:
            errors.append(f"관련 퀘스트 번역값이 달라요: {key}")
    basic_tools = (
        instance / "config/ftbquests/quests/chapters/basic_tools.snbt"
    ).read_text(encoding="utf-8")
    building_tips = (
        instance / "config/ftbquests/quests/chapters/building_tips.snbt"
    ).read_text(encoding="utf-8")
    smart_filters = {
        "everythingcopper_pickaxes": (
            'id: "18DA9065596F9097"' in basic_tools
            and "item(everythingcopper:copper_pickaxe)" in basic_tools
        ),
        "dyenamics_dyes": (
            'id: "4732C2BE50DB2A80"' in building_tips
            and "and(mod(dyenamics)item_tag(c:dyes))" in building_tips
        ),
    }
    if not all(smart_filters.values()):
        errors.append(f"관련 스마트 필터 구조를 확인하지 못했어요: {smart_filters}")
    source_cataclysm = CATACLYSM_SOURCE_COPY.read_text(encoding="utf-8")
    output_cataclysm = CATACLYSM_OUTPUT.read_text(encoding="utf-8")
    if source_cataclysm.count(CUSTOM_NAME_SOURCE) != 1:
        errors.append("원본 Cataclysm 사용자 지정 이름 수가 달라요")
    if output_cataclysm.count(CUSTOM_NAME_TARGET) != 1:
        errors.append("번역 Cataclysm 사용자 지정 이름 수가 달라요")
    if (
        output_cataclysm.replace(CUSTOM_NAME_TARGET, CUSTOM_NAME_SOURCE)
        != source_cataclysm
    ):
        errors.append("Cataclysm 챕터에서 지정한 이름 외의 내용이 달라요")
    friends_english = scoped_friends_english(
        read_jar_language(jars["dyenamicsandfriends"], "dyenamicsandfriends")
    )
    friends_expected = translate_friends(friends_english)
    friends_output = load_json(FRIENDS_OUTPUT)
    for key, expected in friends_expected.items():
        if friends_output.get(key) != expected:
            errors.append(f"Dyenamics and Friends 색상 용어가 달라요: {key}")
    report = {
        "family": FAMILY,
        "advancements": advancement_reports,
        "references": references,
        "related_quest_keys": related_keys,
        "smart_filters": smart_filters,
        "cataclysm_custom_name_translated": True,
        "dyenamicsandfriends_total_keys": len(
            read_jar_language(jars["dyenamicsandfriends"], "dyenamicsandfriends")
        ),
        "dyenamicsandfriends_scoped_integration_keys": len(friends_expected),
        "dyenamicsandfriends_full_addon_translation": "out_of_plan_scope",
        "ftbquests_display_work": "complete",
        "kubejs_display_work": "id_only_references_no_literal_changes",
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def validate_preserved(key: str, source: str, target: str) -> list[str]:
    """자리표시자·숫자·서식·줄바꿈 보존을 확인해요."""
    errors = []
    for label, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("숫자", NUMBER),
        ("서식 코드", FORMAT_CODE),
    ):
        if pattern.findall(source) != pattern.findall(target):
            errors.append(f"{label} 불일치: {key}")
    if source.count("\\n") != target.count("\\n"):
        errors.append(f"이스케이프 줄바꿈 불일치: {key}")
    if source.count("\n") != target.count("\n"):
        errors.append(f"실제 줄바꿈 불일치: {key}")
    return errors


def verify_language(
    mod_id: str,
    jar: Path,
    output: Path,
    translator: object,
    expected_count: int,
) -> tuple[dict[str, object], list[str]]:
    """한 본체의 현재 영어와 한국어 산출물을 완전 대조해요."""
    errors = []
    jar_english = read_jar_language(jar, mod_id)
    working_english = load_json(WORK_ROOT / mod_id / "en_us.json")
    working_korean = load_json(WORK_ROOT / mod_id / "ko_kr.json")
    output_korean = load_json(output)
    expected = translator(jar_english)  # type: ignore[operator]
    if jar_english != working_english:
        errors.append(f"{mod_id} 작업 영어가 현재 JAR과 달라요")
    if list(jar_english) != list(working_korean):
        errors.append(f"{mod_id} 한국어 키 또는 순서가 영어와 달라요")
    if working_korean != output_korean or working_korean != expected:
        errors.append(f"{mod_id} 작업본·산출물·확정 번역이 서로 달라요")
    untranslated = []
    latin_residue = {}
    collisions = defaultdict(list)
    for key in jar_english.keys() & working_korean.keys():
        source = jar_english[key]
        target = working_korean[key]
        if not isinstance(source, str) or not isinstance(target, str):
            errors.append(f"{mod_id} 문자열이 아닌 값이 있어요: {key}")
            continue
        errors.extend(validate_preserved(key, source, target))
        if source == target and key not in INTENTIONAL_SAME:
            untranslated.append(key)
        stripped = PLACEHOLDER.sub("", FORMAT_CODE.sub("", target))
        residue = sorted(set(LATIN_WORD.findall(stripped)) - {"TNT"})
        if residue:
            latin_residue[key] = residue
        if key.startswith(("entity.", "block.", "item.")):
            collisions[target].append(key)
    unexpected_collisions = {
        target: keys
        for target, keys in collisions.items()
        if len(keys) > 1 and len({jar_english[key] for key in keys}) > 1
    }
    if untranslated:
        errors.append(f"{mod_id} 영어 동일값이 남았어요: {untranslated}")
    if latin_residue:
        errors.append(f"{mod_id} 허용하지 않은 영문 잔여가 있어요: {latin_residue}")
    if unexpected_collisions:
        errors.append(f"{mod_id} 검색명이 충돌해요: {unexpected_collisions}")
    if len(working_korean) != expected_count:
        errors.append(
            f"{mod_id} 키 수가 {expected_count}개가 아니에요: {len(working_korean)}"
        )
    return {
        "keys": len(working_korean),
        "untranslated_candidates": untranslated,
        "latin_residue": latin_residue,
        "unexpected_name_collisions": unexpected_collisions,
        "errors": errors,
    }, errors


def verify_quests(instance: Path) -> tuple[dict[str, object], list[str]]:
    """관련 퀘스트 키와 Cataclysm 사용자 지정 이름을 검증해요."""
    errors = []
    english = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    latin_residue = {}
    for key, expected in QUEST_CORRECTIONS.items():
        if korean.get(key) != expected:
            errors.append(f"퀘스트 번역값이 달라요: {key}")
            continue
        errors.extend(quest_snbt.validate_value(key, english[key], expected))
        text = "\n".join(expected) if isinstance(expected, list) else expected
        stripped = PLACEHOLDER.sub("", FORMAT_CODE.sub("", text.replace("\\n", " ")))
        residue = sorted(set(LATIN_WORD.findall(stripped)) - {"Dyenamics"})
        if residue:
            latin_residue[key] = residue
    if latin_residue:
        errors.append(f"퀘스트에 허용하지 않은 영문 잔여가 있어요: {latin_residue}")
    source = CATACLYSM_SOURCE_COPY.read_text(encoding="utf-8")
    target = CATACLYSM_OUTPUT.read_text(encoding="utf-8")
    chapter_exact = target.replace(CUSTOM_NAME_TARGET, CUSTOM_NAME_SOURCE) == source
    if not chapter_exact:
        errors.append("Cataclysm 챕터의 지정 범위 밖 내용이 달라요")
    return {
        "keys": len(QUEST_CORRECTIONS),
        "latin_residue": latin_residue,
        "cataclysm_custom_name_changes": target.count(CUSTOM_NAME_TARGET),
        "cataclysm_only_expected_change": chapter_exact,
        "errors": errors,
    }, errors


def verify_friends(jar: Path) -> tuple[dict[str, object], list[str]]:
    """Dyenamics and Friends 146개 기존 연동 키의 용어 일치를 검증해요."""
    errors = []
    english = scoped_friends_english(read_jar_language(jar, "dyenamicsandfriends"))
    working = load_json(WORK_ROOT / "dyenamicsandfriends/ko_kr.json")
    output = load_json(FRIENDS_OUTPUT)
    expected = translate_friends(english)
    if working != expected:
        errors.append("Dyenamics and Friends 작업본이 확정 번역과 달라요")
    for key, target in expected.items():
        if output.get(key) != target:
            errors.append(f"Dyenamics and Friends 누적 산출물이 달라요: {key}")
        errors.extend(validate_preserved(key, english[key], target))
    color_mismatches = []
    for key, source in english.items():
        if key.startswith("resourcePack."):
            continue
        color, _ = split_color_name(source)
        if not expected[key].startswith(f"{DYENAMICS_COLORS[color]} "):
            color_mismatches.append(key)
    if color_mismatches:
        errors.append(f"Dyenamics 색상 용어가 일치하지 않아요: {color_mismatches}")
    return {
        "current_jar_total_keys": len(read_jar_language(jar, "dyenamicsandfriends")),
        "scoped_integration_keys": len(expected),
        "color_term_mismatches": color_mismatches,
        "errors": errors,
    }, errors


def verify_create_color_links() -> tuple[dict[str, object], list[str]]:
    """기존 Create 연동 Dyenamics 색상 명칭도 같은 기준인지 확인해요."""
    path = OUTPUT_ASSETS / "create_dragons_plus/lang/ko_kr.json"
    values = load_json(path)
    relevant = {
        key: value
        for key, value in values.items()
        if "dyenamics_" in key and isinstance(value, str)
    }
    errors = []
    mismatches = []
    slug_colors = {
        color.lower().replace(" ", "_"): target
        for color, target in DYENAMICS_COLORS.items()
    }
    for key, value in relevant.items():
        slug = next((slug for slug in slug_colors if f"dyenamics_{slug}" in key), None)
        if slug is None or slug_colors[slug] not in value:
            mismatches.append(key)
    if mismatches:
        errors.append(f"Create 연동 색상 용어가 일치하지 않아요: {mismatches}")
    return {
        "linked_keys": len(relevant),
        "mismatches": mismatches,
        "errors": errors,
    }, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """현재 설치 영어와 전체 산출물·연동·퀘스트를 검증해요."""
    instance = resolve_source_root()
    jars = find_jars(instance)
    audit_report = load_json(WORK_ROOT / "surface_audit.json")
    copper, copper_errors = verify_language(
        "everythingcopper",
        jars["everythingcopper"],
        COPPER_OUTPUT,
        translate_copper,
        356,
    )
    dyenamics, dyenamics_errors = verify_language(
        "dyenamics",
        jars["dyenamics"],
        DYENAMICS_OUTPUT,
        translate_dyenamics,
        253,
    )
    friends, friends_errors = verify_friends(jars["dyenamicsandfriends"])
    quests, quest_errors = verify_quests(instance)
    create_links, create_errors = verify_create_color_links()
    audit_errors = audit_report.get("errors", [])
    errors = (
        copper_errors + dyenamics_errors + friends_errors + quest_errors + create_errors
    )
    if isinstance(audit_errors, list):
        errors.extend(str(value) for value in audit_errors)
    report = {
        "family": FAMILY,
        "everythingcopper": copper,
        "dyenamics": dyenamics,
        "dyenamicsandfriends": friends,
        "quests": quests,
        "create_color_links": create_links,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = load_json(deployment_path) if deployment_path.is_file() else None
    completion = {
        "family": FAMILY,
        "main_language_keys": 609,
        "integration_keys": friends["scoped_integration_keys"],
        "quest_keys": quests["keys"],
        "cataclysm_custom_name_changes": quests["cataclysm_custom_name_changes"],
        "surface_audit": audit_report.get("status"),
        "family_validation": report["status"],
        "deployment": deployment,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_completion.json", completion)
    return report, errors


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 스크립트의 백업·해시 결과를 완료 기록에 반영해요."""
    resolved = manifest_path.resolve()
    try:
        relative_manifest = resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        relative_manifest = str(resolved)
    manifest = load_json(resolved)
    errors = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 매니페스트가 완료 상태가 아니에요")
    if manifest.get("java_processes"):
        errors.append(f"적용 당시 Java 프로세스가 있어요: {manifest['java_processes']}")
    targets = manifest.get("targets")
    if not isinstance(targets, list) or not targets:
        errors.append("적용 대상 기록이 없어요")
        targets = []
    summarized = []
    for target in targets:
        if not isinstance(target, dict):
            errors.append("적용 대상 기록 형식이 잘못됐어요")
            continue
        records = {
            value.get("relative_path"): value
            for value in target.get("files", [])
            if isinstance(value, dict)
        }
        missing = sorted(DEPLOYMENT_PATHS - set(records))
        if missing:
            errors.append(f"적용 기록에 산출물이 없어요: {missing}")
        hash_errors = sorted(
            path
            for path in DEPLOYMENT_PATHS & set(records)
            if records[path].get("source_sha256") != records[path].get("after_sha256")
        )
        if hash_errors:
            errors.append(f"적용 후 해시가 달라요: {hash_errors}")
        cataclysm_record = records.get(
            "config/ftbquests/quests/chapters/cataclysm.snbt"
        )
        backup_value = (
            cataclysm_record.get("backup")
            if isinstance(cataclysm_record, dict)
            else None
        )
        if backup_value and Path(backup_value).is_file():
            original = Path(backup_value).read_text(encoding="utf-8")
            CATACLYSM_SOURCE_COPY.parent.mkdir(parents=True, exist_ok=True)
            CATACLYSM_SOURCE_COPY.write_text(original, encoding="utf-8")
        elif not CATACLYSM_SOURCE_COPY.is_file():
            errors.append("Cataclysm 적용 전 원본 백업을 찾지 못했어요")
        if target.get("status") != "applied_and_verified":
            errors.append(
                f"적용 대상 상태가 완료가 아니에요: {target.get('target_root')}"
            )
        if target.get("unexpected_changes"):
            errors.append(
                f"예상 밖 적용 변경이 있어요: {target.get('unexpected_changes')}"
            )
        summarized.append(
            {
                "target_type": target.get("target_type"),
                "target_root": target.get("target_root"),
                "changed_paths": target.get("changed_paths", []),
                "unexpected_changes": target.get("unexpected_changes", []),
                "hash_verified_paths": sorted(
                    path
                    for path in DEPLOYMENT_PATHS & set(records)
                    if records[path].get("source_sha256")
                    == records[path].get("after_sha256")
                ),
            }
        )
    report = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "backup_manifest": relative_manifest,
        "targets": summarized,
        "errors": errors,
    }
    write_json(WORK_ROOT / "deployment_report.json", report)
    verify_report, verify_errors = verify()
    return {
        "deployment": report,
        "verification": verify_report["status"],
    }, errors + verify_errors


def run_all() -> tuple[dict[str, object], list[str]]:
    """준비·생성·표면 감사·검증을 순서대로 실행해요."""
    prepared = prepare()
    built = build()
    audit_report, audit_errors = audit()
    verify_report, verify_errors = verify()
    errors = audit_errors + verify_errors
    return {
        "prepare": prepared,
        "build": built,
        "audit": audit_report,
        "verify": verify_report,
        "status": "complete" if not errors else "incomplete",
    }, errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "build", "audit", "verify", "record-deployment", "all"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    if args.command == "prepare":
        result = prepare()
    elif args.command == "build":
        result = build()
    elif args.command == "audit":
        result, errors = audit()
    elif args.command == "verify":
        result, errors = verify()
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        result, errors = record_deployment(args.manifest)
    else:
        result, errors = run_all()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
