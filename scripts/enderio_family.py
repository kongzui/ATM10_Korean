#!/usr/bin/env python3
"""Ender IO 번역 원본을 준비하고 배치별 진행 상태를 검증한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
from audit_ftbquests_titles import parse_chapters
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/enderio"
OUTPUT_FILE = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/enderio/lang/ko_kr.json"
)
QUEST_OUTPUT_FILE = (
    PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
JAR_PATTERN = "enderio-*.jar"
LANG_ROOT = "assets/enderio/lang"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[&§][0-9A-FK-ORa-fk-or]")
BATCH_ONE_SIZE = 181
BATCH_TWO_END = 361
BATCH_THREE_END = 541
KEEP_ORIGINALS = {
    "block.enderio.enderface": "블록 자체가 공식 모드명 Ender IO를 표시함",
    "block.enderio.niard": "뜻이 확정되지 않은 Ender IO 고유 기계명",
    "energy.enderio.micro_infinity": "숫자 자리표시자와 Ender IO 전력 단위 기호",
    "item.enderio.enderios": "따옴표를 포함한 Ender IO 고유 아이템명",
    "itemGroup.enderio.enderio": "공식 모드명",
    "pack.enderio.machine.experiment.niard": "공식 모드명과 고유 기계명 조합",
}
COLORS = {
    "black": "검은색",
    "blue": "파란색",
    "brown": "갈색",
    "cyan": "청록색",
    "gray": "회색",
    "green": "초록색",
    "light_blue": "하늘색",
    "light_gray": "연한 회색",
    "lime": "연두색",
    "magenta": "자홍색",
    "orange": "주황색",
    "pink": "분홍색",
    "purple": "보라색",
    "red": "빨간색",
    "white": "하얀색",
    "yellow": "노란색",
}
PRESSURE_PLATE_MATERIALS = {
    "acacia": "아카시아나무",
    "birch": "자작나무",
    "crimson": "진홍빛",
    "dark_oak": "짙은 참나무",
    "dark_steel": "다크 스틸",
    "heavy_weighted": "무거운 무게",
    "jungle": "정글나무",
    "light_weighted": "가벼운 무게",
    "oak": "참나무",
    "polished_blackstone": "윤나는 흑암",
    "soularium": "솔라리움",
    "spruce": "가문비나무",
    "stone": "돌",
    "warped": "뒤틀린",
}
COLLISION_EXCEPTIONS = {
    "Ender IO": {
        "block.enderio.enderface",
        "itemGroup.enderio.enderio",
        "keys.categories.enderio",
    },
    "글라이더": {
        "item.enderio.glider",
        "tag.item.enderio.tools.glider",
    },
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    duplicates: list[str] = []

    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        return result

    value = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=unique_object
    )
    if duplicates:
        raise ValueError(f"JSON 중복 키가 있습니다: {path}: {sorted(set(duplicates))}")
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """JSON을 UTF-8(BOM 없음), 들여쓰기 2칸으로 기록한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def find_jar(instance: Path) -> Path:
    """실제 설치본에서 Ender IO JAR 하나를 찾는다."""
    matches = sorted((instance / "mods").glob(JAR_PATTERN))
    if len(matches) != 1:
        raise FileNotFoundError(f"Ender IO JAR 검색 결과가 하나가 아닙니다: {matches}")
    return matches[0]


def load_archive_json(archive: ZipFile, entry: str) -> dict[str, object]:
    """JAR 내부 JSON 객체를 읽는다."""
    value = json.loads(archive.read(entry).decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"JAR 내부 JSON 최상위 값이 객체가 아닙니다: {entry}")
    return value


def prepare() -> None:
    """설치본 원문과 내장 한국어 후보를 작업 디렉터리에 준비한다."""
    instance = resolve_source_root()
    jar = find_jar(instance)
    with ZipFile(jar) as archive:
        english = load_archive_json(archive, f"{LANG_ROOT}/en_us.json")
        bundled = load_archive_json(archive, f"{LANG_ROOT}/ko_kr.json")
        advancement_files = [
            name
            for name in archive.namelist()
            if name.startswith("data/enderio/advancement/") and name.endswith(".json")
        ]
        patchouli_files = [
            name
            for name in archive.namelist()
            if name.startswith("assets/enderio/patchouli_books/")
            and not name.endswith("/")
        ]

    write_json(WORK_ROOT / "en_us.json", english)
    write_json(WORK_ROOT / "bundled_ko_kr.json", bundled)
    if not (WORK_ROOT / "ko_kr.json").exists():
        write_json(WORK_ROOT / "ko_kr.json", bundled)

    identical = [key for key in english if english[key] == bundled.get(key)]
    candidate_sources = {
        key: "bundled_same_as_english_unusable"
        if key in identical
        else "bundled_korean_unreviewed"
        for key in english
    }
    write_json(WORK_ROOT / "candidate_sources.json", candidate_sources)
    write_json(
        WORK_ROOT / "scope.json",
        {
            "family": "Ender IO",
            "jar": jar.name,
            "namespace": "enderio",
            "english_keys": len(english),
            "bundled_korean_keys": len(bundled),
            "bundled_values_identical_to_english": len(identical),
            "bundled_korean_usable_without_review": 0,
            "advancement_files": len(advancement_files),
            "patchouli_files": patchouli_files,
            "patchouli_runtime_book_metadata_found": False,
        },
    )
    progress_path = WORK_ROOT / "progress.json"
    if not progress_path.exists():
        write_json(
            progress_path,
            {
                "family": "Ender IO",
                "batch_size": 180,
                "reviewed_keys": 0,
                "total_keys": len(english),
                "status": "prepared",
            },
        )
    print(f"준비 완료: {jar.name}, 영어 {len(english)}키")
    print(f"내장 한국어 중 영어와 동일한 값: {len(identical)}키")


def glass_translation(key: str) -> str | None:
    """투명 유리와 융합 석영 변형 이름을 일관된 규칙으로 번역한다."""
    variants = {
        "block.enderio.clear_glass": "투명 유리",
        "block.enderio.fused_quartz": "융합 석영",
    }
    for prefix, base in variants.items():
        if key == prefix:
            return base
        if not key.startswith(prefix + "_"):
            continue
        suffix = key.removeprefix(prefix + "_")
        kind = ""
        if suffix == "d":
            return f"어두운 {base}"
        if suffix == "e":
            return f"발광 {base}"
        if suffix.startswith("d_"):
            kind = "어두운 "
            suffix = suffix.removeprefix("d_")
        elif suffix.startswith("e_"):
            kind = "발광 "
            suffix = suffix.removeprefix("e_")
        color = COLORS.get(suffix)
        if color is not None:
            return f"{color} {kind}{base}"
    return None


def translate_batch_one() -> None:
    """발전 과제와 블록 이름 181키를 첫 검토 배치로 반영한다."""
    english = load_json(WORK_ROOT / "en_us.json")
    korean = load_json(WORK_ROOT / "ko_kr.json")
    translations = {
        "advancements.enderio.place_capacitor_bank.description": "축전기 뱅크를 제작하세요",
        "advancements.enderio.place_capacitor_bank.title": "모듈식 전력 저장고",
        "advancements.enderio.rich.description": "다른 사람들에게 부자로 보이세요",
        "advancements.enderio.rich.title": "다른 사람들에게는 비밀이에요",
        "advancements.enderio.richer.description": "다른 사람들에게 더 부자로 보이세요",
        "advancements.enderio.richer.title": "이거 진짜 맞나요?",
        "advancements.enderio.use_glider.description": "가죽 몇 장을 정말 믿으시나요?",
        "advancements.enderio.use_glider.title": "장엄한 비행",
        "block.enderio.advanced_capacitor_bank": "고급 축전기 뱅크",
        "block.enderio.alloy_smelter": "합금 제련기",
        "block.enderio.attractor_obelisk": "유인 오벨리스크",
        "block.enderio.aversion_obelisk": "회피 오벨리스크",
        "block.enderio.basic_capacitor_bank": "기본 축전기 뱅크",
        "block.enderio.block_detector": "블록 감지기",
        "block.enderio.cloud_seed": "구름 씨앗",
        "block.enderio.cloud_seed_concentrated": "농축 구름 씨앗",
        "block.enderio.cold_fire": "차가운 불",
        "block.enderio.conductive_alloy_block": "전도성 합금 블록",
        "block.enderio.conduit": "도관 묶음",
        "block.enderio.crafter": "자동 제작기",
        "block.enderio.creative_power": "크리에이티브 전원",
        "block.enderio.dark_steel_bars": "다크 스틸 창살",
        "block.enderio.dark_steel_block": "다크 스틸 블록",
        "block.enderio.dark_steel_door": "다크 스틸 문",
        "block.enderio.dark_steel_ladder": "다크 스틸 사다리",
        "block.enderio.dark_steel_pressure_plate": "다크 스틸 감압판",
        "block.enderio.dark_steel_trapdoor": "다크 스틸 다락문",
        "block.enderio.dew_of_the_void": "공허의 이슬",
        "block.enderio.drain": "배수구",
        "block.enderio.enchanter": "마법 부여기",
        "block.enderio.end_steel_bars": "엔드 스틸 창살",
        "block.enderio.end_steel_block": "엔드 스틸 블록",
        "block.enderio.enderface": "Ender IO",
        "block.enderio.enderman_head": "엔더맨 머리",
        "block.enderio.energetic_alloy_block": "에너지 합금 블록",
        "block.enderio.energetic_photovoltaic_module": "에너지 태양광 모듈",
        "block.enderio.ensouled_chassis": "영혼이 깃든 섀시",
        "block.enderio.farming_station": "농장 작업대",
        "block.enderio.fire_water": "화염수",
        "block.enderio.fluid_tank": "유체 탱크",
        "block.enderio.hootch": "밀주",
        "block.enderio.impulse_hopper": "임펄스 호퍼",
        "block.enderio.industrial_insulation": "산업용 절연재",
        "block.enderio.inhibitor_obelisk": "억제 오벨리스크",
        "block.enderio.liquid_darkness": "액체 어둠",
        "block.enderio.liquid_sunshine": "액체 햇빛",
        "block.enderio.mind_killer": "정신 파괴기",
        "block.enderio.niard": "Niard",
        "block.enderio.nutrient_distillation": "영양 증류액",
        "block.enderio.painted_crafting_table": "도색된 작업대",
        "block.enderio.painted_fence": "도색된 울타리",
        "block.enderio.painted_fence_gate": "도색된 울타리 문",
        "block.enderio.painted_glowstone": "도색된 발광석",
        "block.enderio.painted_redstone_block": "도색된 레드스톤 블록",
        "block.enderio.painted_sand": "도색된 모래",
        "block.enderio.painted_slab": "도색된 반 블록",
        "block.enderio.painted_stairs": "도색된 계단",
        "block.enderio.painted_trapdoor": "도색된 다락문",
        "block.enderio.painted_travel_anchor": "도색된 이동 앵커",
        "block.enderio.painted_wall": "도색된 담장",
        "block.enderio.painted_wooden_pressure_plate": "도색된 나무 감압판",
        "block.enderio.painting_machine": "도색기",
        "block.enderio.powered_spawner": "동력 스포너",
        "block.enderio.pressurized_fluid_tank": "가압 유체 탱크",
        "block.enderio.pulsating_alloy_block": "맥동 합금 블록",
        "block.enderio.pulsating_photovoltaic_module": "맥동 태양광 모듈",
        "block.enderio.redstone_alloy_block": "레드스톤 합금 블록",
        "block.enderio.reinforced_obsidian_block": "강화 흑요석",
        "block.enderio.relocator_obelisk": "재배치 오벨리스크",
        "block.enderio.resetting_lever_five": "복귀 레버 (5초)",
        "block.enderio.resetting_lever_five_inv": "반전 복귀 레버 (5초)",
        "block.enderio.resetting_lever_sixty": "복귀 레버 (1분)",
        "block.enderio.resetting_lever_sixty_inv": "반전 복귀 레버 (1분)",
        "block.enderio.resetting_lever_ten": "복귀 레버 (10초)",
        "block.enderio.resetting_lever_ten_inv": "반전 복귀 레버 (10초)",
        "block.enderio.resetting_lever_thirty": "복귀 레버 (30초)",
        "block.enderio.resetting_lever_thirty_inv": "반전 복귀 레버 (30초)",
        "block.enderio.resetting_lever_three_hundred": "복귀 레버 (5분)",
        "block.enderio.resetting_lever_three_hundred_inv": "반전 복귀 레버 (5분)",
    }
    ordered_keys = list(english)
    batch_keys = ordered_keys[:BATCH_ONE_SIZE]
    for key in batch_keys:
        translated = translations.get(key) or glass_translation(key)
        if translated is None:
            raise KeyError(f"첫 배치 번역이 없습니다: {key}")
        korean[key] = translated
    write_json(WORK_ROOT / "ko_kr.json", korean)
    write_json(WORK_ROOT / "keep_originals.json", KEEP_ORIGINALS)

    sources = load_json(WORK_ROOT / "candidate_sources.json")
    for key in batch_keys:
        sources[key] = "manual_translation"
    sources["block.enderio.powered_spawner"] = "existing_project_translation_reuse"
    for key in KEEP_ORIGINALS:
        sources[key] = "reviewed_original"
    write_json(WORK_ROOT / "candidate_sources.json", sources)
    write_json(
        WORK_ROOT / "progress.json",
        {
            "family": "Ender IO",
            "batch_size": BATCH_ONE_SIZE,
            "reviewed_keys": BATCH_ONE_SIZE,
            "total_keys": len(english),
            "completed_batches": [
                {
                    "batch": 1,
                    "range": [1, BATCH_ONE_SIZE],
                    "scope": "발전 과제 전체와 블록 이름 앞부분",
                }
            ],
            "status": "in_progress",
        },
    )
    print(f"첫 번역 배치 반영 완료: {BATCH_ONE_SIZE}키")


def silent_pressure_plate_translation(key: str) -> str | None:
    """무소음 감압판 계열을 마인크래프트 재료명에 맞춰 번역한다."""
    prefix = "block.enderio.silent_"
    suffix = "_pressure_plate"
    if not key.startswith(prefix) or not key.endswith(suffix):
        return None
    material = key.removeprefix(prefix).removesuffix(suffix)
    translated = PRESSURE_PLATE_MATERIALS.get(material)
    return f"무소음 {translated} 감압판" if translated else None


def translate_batch_two() -> None:
    """남은 블록, 도관, 필터와 기계 UI 180키를 두 번째 배치로 반영한다."""
    english = load_json(WORK_ROOT / "en_us.json")
    korean = load_json(WORK_ROOT / "ko_kr.json")
    translations = {
        "block.enderio.rocket_fuel": "로켓 연료",
        "block.enderio.sag_mill": "SAG 분쇄기",
        "block.enderio.slice_and_splice": "절단 접합기",
        "block.enderio.soul_binder": "영혼 결속기",
        "block.enderio.soul_chain": "영혼 사슬",
        "block.enderio.soul_engine": "영혼 엔진",
        "block.enderio.soularium_block": "솔라리움 블록",
        "block.enderio.soularium_pressure_plate": "솔라리움 감압판",
        "block.enderio.stirling_generator": "스털링 발전기",
        "block.enderio.travel_anchor": "이동 앵커",
        "block.enderio.vacuum_chest": "진공 상자",
        "block.enderio.vapor_of_levity": "부양의 증기",
        "block.enderio.vat": "발효조",
        "block.enderio.vibrant_alloy_block": "활기찬 합금 블록",
        "block.enderio.vibrant_capacitor_bank": "활기찬 축전기 뱅크",
        "block.enderio.vibrant_photovoltaic_module": "활기찬 태양광 모듈",
        "block.enderio.void_chassis": "공허 섀시",
        "block.enderio.weather_obelisk": "날씨 오벨리스크",
        "block.enderio.wired_charger": "유선 충전기",
        "block.enderio.wireless_charger": "무선 충전기",
        "block.enderio.wireless_charger_antenna": "맥동 무선 안테나",
        "block.enderio.wireless_charger_antenna_advanced": "활기찬 무선 안테나",
        "block.enderio.xp_juice": "경험치 주스",
        "block.enderio.xp_obelisk": "경험치 오벨리스크",
        "block.enderio.xp_vacuum": "경험치 흡입기",
        "conduit.enderio.ender_energy": "활기찬 에너지 도관",
        "conduit.enderio.ender_fluid": "활기찬 유체 도관",
        "conduit.enderio.ender_item": "활기찬 아이템 도관",
        "conduit.enderio.energy": "에너지 도관",
        "conduit.enderio.enhanced_energy": "에너지 합금 에너지 도관",
        "conduit.enderio.enhanced_item": "에너지 합금 아이템 도관",
        "conduit.enderio.fluid": "유체 도관",
        "conduit.enderio.item": "아이템 도관",
        "conduit.enderio.pressurized_fluid": "에너지 합금 유체 도관",
        "conduit.enderio.redstone": "레드스톤 도관",
        "config.jade.plugin_enderio.soul_bound": "영혼 귀속",
        "enderio.alloy_smelter_mode.all": "합금 및 제련",
        "enderio.alloy_smelter_mode.alloys": "합금만",
        "enderio.alloy_smelter_mode.furnace": "제련만",
        "enderio.capacitor.loot.base.dud": "불량 축전기",
        "enderio.capacitor.loot.base.enhanced": "강화 축전기",
        "enderio.capacitor.loot.base.impossible": "불가능한 축전기",
        "enderio.capacitor.loot.base.normal": "축전기",
        "enderio.capacitor.loot.base.wonder": "경이로운 축전기",
        "enderio.capacitor.loot.modifier.enhanced": "강화된",
        "enderio.capacitor.loot.modifier.failed": "실패한",
        "enderio.capacitor.loot.modifier.good": "좋은",
        "enderio.capacitor.loot.modifier.incredibly": "엄청나게",
        "enderio.capacitor.loot.modifier.nice": "괜찮은",
        "enderio.capacitor.loot.modifier.premium": "고급",
        "enderio.capacitor.loot.modifier.simple": "단순한",
        "enderio.capacitor.loot.modifier.unstable": "불안정한",
        "enderio.capacitor.loot.type.burning_energy_generation": "뜨거운",
        "enderio.capacitor.loot.type.energy_capacity": "만족을 모르는",
        "enderio.capacitor.loot.type.energy_use": "굶주린",
        "enderio.capacitor.loot.type.fuel_efficiency": "효율적인",
        "enderio.capacitor.loot.type.unknown.Mystery": "수수께끼",
        "enderio.capacitor.modifier.base.tooltip": "기본 배율: %s",
        "enderio.capacitor.modifier.burning_energy_generation.tooltip": "연소 발전 배율: %s",
        "enderio.capacitor.modifier.energy_capacity.tooltip": "에너지 용량 배율: %s",
        "enderio.capacitor.modifier.energy_use.tooltip": "에너지 사용량 배율: %s",
        "enderio.capacitor.modifier.fuel_efficiency.tooltip": "연료 효율 배율: %s",
        "enderio.damage_filter_mode.ignore": "내구도 무시",
        "enderio.damage_filter_mode.is_damageable": "내구도가 있음",
        "enderio.damage_filter_mode.more_than_25": "내구도 25%% 초과 손상",
        "enderio.damage_filter_mode.more_than_50": "내구도 50%% 초과 손상",
        "enderio.damage_filter_mode.more_than_75": "내구도 75%% 초과 손상",
        "enderio.damage_filter_mode.not_damageable": "내구도가 없음",
        "enderio.damage_filter_mode.not_damaged": "손상되지 않음",
        "enderio.damage_filter_mode.only_damaged": "손상된 것만",
        "enderio.damage_filter_mode.up_to_25": "내구도 25%% 이하 손상",
        "enderio.damage_filter_mode.up_to_50": "내구도 50%% 이하 손상",
        "enderio.damage_filter_mode.up_to_75": "내구도 75%% 이하 손상",
        "enderio.glass_collision.animals_block": "동물만 통과 불가",
        "enderio.glass_collision.animals_pass": "동물은 통과 가능",
        "enderio.glass_collision.mobs_block": "몬스터만 통과 불가",
        "enderio.glass_collision.mobs_pass": "몬스터는 통과 가능",
        "enderio.glass_collision.players_block": "플레이어만 통과 불가",
        "enderio.glass_collision.players_pass": "플레이어는 통과 가능",
        "enderio.powered_spawner_mode.capture": "몹 포획",
        "enderio.powered_spawner_mode.spawn": "몹 생성",
        "enderio.redstone_control.active_with_signal": "신호가 있을 때 작동",
        "enderio.redstone_control.active_without_signal": "신호가 없을 때 작동",
        "enderio.redstone_control.always_active": "항상 작동",
        "enderio.redstone_control.never_active": "작동하지 않음",
        "energy.enderio.micro_infinity": "%s µI",
        "entity.enderio.painted_sand": "떨어지는 도색된 모래",
        "fluid_type.enderio.cloud_seed": "구름 씨앗",
        "fluid_type.enderio.cloud_seed_concentrated": "농축 구름 씨앗",
        "fluid_type.enderio.dew_of_the_void": "공허의 이슬",
        "fluid_type.enderio.fire_water": "화염수",
        "fluid_type.enderio.hootch": "밀주",
        "fluid_type.enderio.liquid_darkness": "액체 어둠",
        "fluid_type.enderio.liquid_sunshine": "액체 햇빛",
        "fluid_type.enderio.nutrient_distillation": "영양 증류액",
        "fluid_type.enderio.rocket_fuel": "로켓 연료",
        "fluid_type.enderio.vapor_of_levity": "부양의 증기",
        "fluid_type.enderio.xp_juice": "경험치 주스",
        "gui.enderio.conduit.channel": "채널",
        "gui.enderio.conduit.error.no_screen_type": "오류: 화면 유형이 정의되지 않음",
        "gui.enderio.conduit.extract": "추출",
        "gui.enderio.conduit.fluid.change_fluid1": "고정된 유체: ",
        "gui.enderio.conduit.fluid.change_fluid2": "클릭하여 초기화하세요!",
        "gui.enderio.conduit.fluid.change_fluid3": "유체: %s",
        "gui.enderio.conduit.input": "입력",
        "gui.enderio.conduit.insert": "삽입",
        "gui.enderio.conduit.output": "출력",
        "gui.enderio.conduit.priority": "우선순위",
        "gui.enderio.conduit.redstone.signal_color": "신호 색상",
        "gui.enderio.conduit.redstone.strong_signal": "강한 신호",
        "gui.enderio.conduit.redstone_channel": "신호 색상",
        "gui.enderio.conduit.round_robin.disabled": "순환 분배 꺼짐",
        "gui.enderio.conduit.round_robin.enabled": "순환 분배 켜짐",
        "gui.enderio.conduit.self_feed.disabled": "자체 공급 꺼짐",
        "gui.enderio.conduit.self_feed.enabled": "자체 공급 켜짐",
        "gui.enderio.electromagnet_off": "전자석 꺼짐",
        "gui.enderio.electromagnet_on": "전자석 켜짐",
        "gui.enderio.error_cannot_teleport": "오류: 순간이동할 수 없음",
        "gui.enderio.error_invalid_destination": "오류: 목적지가 올바른 대상이 아님",
        "gui.enderio.error_too_far": "오류: 너무 멂",
        "gui.enderio.filter.allow_list": "허용 목록",
        "gui.enderio.filter.confirm": "확인",
        "gui.enderio.filter.damage_filter": "내구도 필터",
        "gui.enderio.filter.deny_list": "거부 목록",
        "gui.enderio.filter.filter": "필터",
        "gui.enderio.filter.ignore_components": "구성 요소 무시",
        "gui.enderio.filter.ignore_tags": "NBT 무시",
        "gui.enderio.filter.match_components": "구성 요소 일치",
        "gui.enderio.filter.match_tags": "NBT 일치",
        "gui.enderio.ioconfig": "입출력 설정",
        "gui.enderio.ioconfig.both": "내보내기 / 가져오기",
        "gui.enderio.ioconfig.disabled": "비활성화",
        "gui.enderio.ioconfig.none": "없음",
        "gui.enderio.ioconfig.pull": "가져오기",
        "gui.enderio.ioconfig.push": "내보내기",
        "gui.enderio.ioconfig.toggle_neighbours": "이웃 표시/숨기기",
        "gui.enderio.machine.alloy_smelter.mode": "제련 모드",
        "gui.enderio.machine.generator.efficiency": "효율 %s%%",
        "gui.enderio.machine.generator.generating": "%sµI/t 생산 중",
        "gui.enderio.machine.no_fluid": "유체 없음",
        "gui.enderio.machine.nocap.desc": "이 기계를 작동하려면\n 축전기를 넣으세요!",
        "gui.enderio.machine.nocap.title": "축전기 없음",
        "gui.enderio.machine.obelisk.no_soul_filter": "영혼 필터가 설치되지 않음",
        "gui.enderio.machine.obelisk.upkeep_cost": "유지 비용 %sµI/t",
        "gui.enderio.machine.powered_spawner.mode": "스포너 모드",
        "gui.enderio.machine.powered_spawner.status.disabled": "설정에서 비활성화됨",
        "gui.enderio.machine.powered_spawner.status.other_mod": "다른 모드가 차단함",
        "gui.enderio.machine.powered_spawner.status.overcrowded.mobs": "몹이 너무 많음",
        "gui.enderio.machine.powered_spawner.status.overcrowded.spawners": "스포너가 너무 많음",
        "gui.enderio.machine.powered_spawner.status.unknown_mob": "알 수 없는 몹",
        "gui.enderio.machine.range": "범위",
        "gui.enderio.machine.range.hide": "범위 숨기기",
        "gui.enderio.machine.range.max": "최대 범위",
        "gui.enderio.machine.range.show": "범위 표시",
        "gui.enderio.machine.vat.dump_tank": "탱크 내용물 폐기",
        "gui.enderio.machine.vat.transfer_tank": "탱크 내용물 옮기기",
        "gui.enderio.machine.xp_obelisk.button.retrieve.10_levels": "경험치 10레벨 꺼내기",
        "gui.enderio.machine.xp_obelisk.button.retrieve.1_level": "경험치 1레벨 꺼내기",
        "gui.enderio.machine.xp_obelisk.button.retrieve.all_levels": "모든 경험치 레벨 꺼내기",
        "gui.enderio.machine.xp_obelisk.button.rstore.1_level": "경험치 1레벨 저장",
        "gui.enderio.machine.xp_obelisk.button.store.10_levels": "경험치 10레벨 저장",
        "gui.enderio.machine.xp_obelisk.button.store.all_levels": "모든 경험치 레벨 저장",
        "gui.enderio.not_visible": "숨김",
        "gui.enderio.redstone_mode": "레드스톤 모드",
        "gui.enderio.visible": "표시",
        "hint.enderio.connected_textures.text": "축전기 뱅크의 연결 텍스처를 사용하려면 클라이언트에 Athena를 설치하세요.",
    }
    ordered_keys = list(english)
    batch_keys = ordered_keys[BATCH_ONE_SIZE:BATCH_TWO_END]
    for key in batch_keys:
        translated = translations.get(key) or silent_pressure_plate_translation(key)
        if translated is None:
            raise KeyError(f"두 번째 배치 번역이 없습니다: {key}")
        korean[key] = translated
    write_json(WORK_ROOT / "ko_kr.json", korean)
    write_json(WORK_ROOT / "keep_originals.json", KEEP_ORIGINALS)

    sources = load_json(WORK_ROOT / "candidate_sources.json")
    for key in batch_keys:
        sources[key] = "manual_translation"
    for key in KEEP_ORIGINALS:
        sources[key] = "reviewed_original"
    write_json(WORK_ROOT / "candidate_sources.json", sources)
    write_json(
        WORK_ROOT / "progress.json",
        {
            "family": "Ender IO",
            "batch_size": 180,
            "reviewed_keys": BATCH_TWO_END,
            "total_keys": len(english),
            "completed_batches": [
                {
                    "batch": 1,
                    "range": [1, BATCH_ONE_SIZE],
                    "scope": "발전 과제 전체와 블록 이름 앞부분",
                },
                {
                    "batch": 2,
                    "range": [BATCH_ONE_SIZE + 1, BATCH_TWO_END],
                    "scope": "남은 블록, 도관, 필터와 기계 UI",
                },
            ],
            "status": "in_progress",
        },
    )
    print(f"두 번째 번역 배치 반영 완료: {len(batch_keys)}키")


def translate_batch_three() -> None:
    """아이템, JEI, 메시지와 태그 앞부분 180키를 세 번째 배치로 반영한다."""
    english = load_json(WORK_ROOT / "en_us.json")
    korean = load_json(WORK_ROOT / "ko_kr.json")
    translations = {
        "item.enderio.advanced_item_filter": "고급 아이템 필터",
        "item.enderio.animal_token": "동물 토큰",
        "item.enderio.basic_capacitor": "기본 축전기",
        "item.enderio.basic_fluid_filter": "기본 유체 필터",
        "item.enderio.basic_item_filter": "기본 아이템 필터",
        "item.enderio.basic_soul_filter": "기본 영혼 필터",
        "item.enderio.big_advanced_item_filter": "대형 고급 아이템 필터",
        "item.enderio.big_item_filter": "대형 아이템 필터",
        "item.enderio.broken_spawner": "부서진 스포너",
        "item.enderio.cloud_seed_bucket": "구름 씨앗 양동이",
        "item.enderio.cloud_seed_concentrated_bucket": "농축 구름 씨앗 양동이",
        "item.enderio.cold_fire_igniter": "차가운 불 점화기",
        "item.enderio.conductive_alloy_grinding_ball": "전도성 합금 분쇄구",
        "item.enderio.conductive_alloy_ingot": "전도성 합금 주괴",
        "item.enderio.conductive_alloy_nugget": "전도성 합금 조각",
        "item.enderio.conduit": "<누락> 도관",
        "item.enderio.conduit_binder": "도관 결합재",
        "item.enderio.conduit_binder_composite": "도관 결합재 복합물",
        "item.enderio.conduit_facade": "도관 위장판",
        "item.enderio.conduit_probe": "도관 탐침",
        "item.enderio.confusing_powder": "혼란 가루",
        "item.enderio.coordinate_selector": "좌표 선택기",
        "item.enderio.creative_tab_icon": "내부 아이템 - 획득 불가",
        "item.enderio.dark_bimetal_gear": "다크 바이메탈 기어",
        "item.enderio.dark_steel_grinding_ball": "다크 스틸 분쇄구",
        "item.enderio.dark_steel_ingot": "다크 스틸 주괴",
        "item.enderio.dark_steel_nugget": "다크 스틸 조각",
        "item.enderio.dark_steel_sword": "디 엔더",
        "item.enderio.dew_of_the_void_bucket": "공허의 이슬 양동이",
        "item.enderio.double_layer_capacitor": "이중 축전기",
        "item.enderio.electromagnet": "전자석",
        "item.enderio.end_steel_grinding_ball": "엔드 스틸 분쇄구",
        "item.enderio.end_steel_ingot": "엔드 스틸 주괴",
        "item.enderio.end_steel_nugget": "엔드 스틸 조각",
        "item.enderio.ender_crystal": "엔더 수정",
        "item.enderio.ender_crystal_powder": "엔드의 알갱이",
        "item.enderio.ender_resonator": "엔더 공명기",
        "item.enderio.enderios": '"Enderios"',
        "item.enderio.energetic_alloy_grinding_ball": "에너지 합금 분쇄구",
        "item.enderio.energetic_alloy_ingot": "에너지 합금 주괴",
        "item.enderio.energetic_alloy_nugget": "에너지 합금 조각",
        "item.enderio.energized_gear": "에너지 바이메탈 기어",
        "item.enderio.enticing_crystal": "유혹의 수정",
        "item.enderio.experience_rod": "경험치 막대",
        "item.enderio.fire_water_bucket": "화염수 양동이",
        "item.enderio.frank_n_zombie": "프랭크 앤 좀비",
        "item.enderio.glider": "글라이더",
        "item.enderio.glider_wing": "글라이더 날개",
        "item.enderio.grains_of_infinity": "무한의 알갱이",
        "item.enderio.guardian_diode": "수호자 다이오드",
        "item.enderio.hardened_conduit_facade": "강화 도관 위장판",
        "item.enderio.hootch_bucket": "밀주 양동이",
        "item.enderio.infinity_rod": "무한 막대",
        "item.enderio.iron_gear": "무한 바이메탈 기어",
        "item.enderio.limited_item_filter": "제한 아이템 필터",
        "item.enderio.liquid_darkness_bucket": "액체 어둠 양동이",
        "item.enderio.liquid_sunshine_bucket": "액체 햇빛 양동이",
        "item.enderio.location_printout": "위치 출력물",
        "item.enderio.loot_capacitor": "전리품 축전기",
        "item.enderio.monster_token": "몬스터 토큰",
        "item.enderio.nutrient_distillation_bucket": "영양 증류액 양동이",
        "item.enderio.nutritious_stick": "영양 만점 막대",
        "item.enderio.octadic_capacitor": "8중 축전기",
        "item.enderio.photovoltaic_composite": "태양광 복합재",
        "item.enderio.photovoltaic_plate": "태양광 판",
        "item.enderio.plant_matter_brown": "잔가지와 잘라낸 가지",
        "item.enderio.plant_matter_green": "잎 조각과 다듬은 가지",
        "item.enderio.player_token": "플레이어 토큰",
        "item.enderio.powdered_coal": "석탄 가루",
        "item.enderio.powdered_copper": "구리 가루",
        "item.enderio.powdered_ender_pearl": "엔더 진주 가루",
        "item.enderio.powdered_gold": "금 가루",
        "item.enderio.powdered_iron": "철 가루",
        "item.enderio.powdered_lapis_lazuli": "청금석 가루",
        "item.enderio.powdered_obsidian": "흑요석 가루",
        "item.enderio.powdered_quartz": "석영 가루",
        "item.enderio.powdered_tin": "주석 가루",
        "item.enderio.prescient_crystal": "예지 수정",
        "item.enderio.prescient_powder": "예지의 알갱이",
        "item.enderio.pulsating_alloy_grinding_ball": "맥동 합금 분쇄구",
        "item.enderio.pulsating_alloy_ingot": "맥동 합금 주괴",
        "item.enderio.pulsating_alloy_nugget": "맥동 합금 조각",
        "item.enderio.pulsating_crystal": "맥동 수정",
        "item.enderio.pulsating_powder": "압전성의 알갱이",
        "item.enderio.redstone_alloy_grinding_ball": "레드스톤 합금 분쇄구",
        "item.enderio.redstone_alloy_ingot": "레드스톤 합금 주괴",
        "item.enderio.redstone_alloy_nugget": "레드스톤 합금 조각",
        "item.enderio.redstone_and_filter": "레드스톤 AND 필터",
        "item.enderio.redstone_counting_filter": "레드스톤 계수 필터",
        "item.enderio.redstone_filter_base": "레드스톤 필터 기반",
        "item.enderio.redstone_nand_filter": "레드스톤 NAND 필터",
        "item.enderio.redstone_nor_filter": "레드스톤 NOR 필터",
        "item.enderio.redstone_not_filter": "레드스톤 NOT 필터",
        "item.enderio.redstone_or_filter": "레드스톤 OR 필터",
        "item.enderio.redstone_sensor_filter": "레드스톤 감지 필터",
        "item.enderio.redstone_timer_filter": "레드스톤 타이머 필터",
        "item.enderio.redstone_toggle_filter": "레드스톤 전환 필터",
        "item.enderio.redstone_xnor_filter": "레드스톤 XNOR 필터",
        "item.enderio.redstone_xor_filter": "레드스톤 XOR 필터",
        "item.enderio.rocket_fuel_bucket": "로켓 연료 양동이",
        "item.enderio.sentient_ender": "자아를 지닌 엔더",
        "item.enderio.silicon": "실리콘",
        "item.enderio.skeletal_contractor": "해골 계약자",
        "item.enderio.soul_powder": "영혼 가루",
        "item.enderio.soul_vial": "영혼 약병",
        "item.enderio.soularium_grinding_ball": "솔라리움 분쇄구",
        "item.enderio.soularium_ingot": "솔라리움 주괴",
        "item.enderio.soularium_nugget": "솔라리움 조각",
        "item.enderio.staff_of_levity": "부양의 지팡이",
        "item.enderio.staff_of_travelling": "이동의 지팡이",
        "item.enderio.suspicious_seed": "수상한 씨앗",
        "item.enderio.transparent_conduit_facade": "투명 도관 위장판",
        "item.enderio.transparent_hardened_conduit_facade": "투명 강화 도관 위장판",
        "item.enderio.vapor_of_levity_bucket": "부양의 증기 양동이",
        "item.enderio.vibrant_alloy_grinding_ball": "활기찬 합금 분쇄구",
        "item.enderio.vibrant_alloy_ingot": "활기찬 합금 주괴",
        "item.enderio.vibrant_alloy_nugget": "활기찬 합금 조각",
        "item.enderio.vibrant_crystal": "활기찬 수정",
        "item.enderio.vibrant_gear": "활기찬 바이메탈 기어",
        "item.enderio.vibrant_powder": "활력의 알갱이",
        "item.enderio.void_vial": "공허의 약병",
        "item.enderio.weather_crystal": "날씨 수정",
        "item.enderio.withering_powder": "시듦 가루",
        "item.enderio.xp_juice_bucket": "경험치 주스 양동이",
        "item.enderio.yeta_wrench": "예타 렌치",
        "item.enderio.z_logic_controller": "Z-로직 제어기",
        "item.enderio.zombie_electrode": "좀비 전극",
        "itemGroup.enderio.enderio": "Ender IO",
        "jei.enderio.alloy_smelting.title": "합금 제련",
        "jei.enderio.enchanter.title": "마법 부여",
        "jei.enderio.fire_crafting.chance": "확률 %s%%",
        "jei.enderio.fire_crafting.drops": "결과물 %s",
        "jei.enderio.fire_crafting.title": "불 제작",
        "jei.enderio.fire_crafting.valid_blocks": "사용 가능한 블록:",
        "jei.enderio.fire_crafting.valid_dimensions": "사용 가능한 차원:",
        "jei.enderio.sag_mill.title": "SAG 분쇄",
        "jei.enderio.slicing.title": "절단",
        "jei.enderio.soul_binding.title": "영혼 결속",
        "jei.enderio.soul_engine.title": "영혼 엔진",
        "jei.enderio.tank.title": "유체 탱크",
        "jei.enderio.vat.title": "발효조 발효",
        "jei.enderio.weather_change.title": "날씨 오벨리스크",
        "key.enderio.toggle_magnet": "전자석 켜기/끄기",
        "key.enderio.travel_staff": "이동의 지팡이",
        "keys.categories.enderio": "Ender IO",
        "message.enderio.conduit.probe.copied": "데이터 복사됨: %s",
        "message.enderio.conduit.probe.pasted": "데이터 붙여넣음: %s",
        "message.enderio.conduit.probe.switched_mode": "도관 탐침 모드를 %s(으)로 변경함",
        "message.enderio.too_many_levels": "레벨이 21862를 넘었습니다. 경험치가 너무 많습니다.",
        "message.enderio.tool.coordinate_selector.no_block": "범위 안에 블록이 없습니다",
        "message.enderio.tool.coordinate_selector.no_paper": "인벤토리에 종이가 없습니다",
        "message.enderio.tool.glider.disable": "글라이더 비활성화: ",
        "message.enderio.tool.glider.disable.fall_flying": "겉날개 비행",
        "message.enderio.tool.soul_vial.error.blacklisted": "이 엔티티는 차단 목록에 있습니다.",
        "message.enderio.tool.soul_vial.error.boss": "좋은 시도였지만, 보스는 병을 싫어합니다.",
        "message.enderio.tool.soul_vial.error.dead": "죽은 몹은 포획할 수 없습니다!",
        "message.enderio.tool.soul_vial.error.failed": "이 엔티티는 포획할 수 없습니다.",
        "message.enderio.tool.soul_vial.error.player": "플레이어를 병에 넣을 수 없습니다!",
        "pack.enderio.machine.experiment.ender_io": "Ender IO: Ender IO",
        "pack.enderio.machine.experiment.farming_station": "Ender IO: 농장 작업대",
        "pack.enderio.machine.experiment.niard": "Ender IO: Niard",
        "tag.block.enderio.blocks_travel_when_stood_on": "순간이동 방지",
        "tag.block.enderio.mind_killer": "정신 파괴기",
        "tag.block.enderio.range_extender": "범위 확장기",
        "tag.block.enderio.redstone_connectable": "레드스톤 연결 가능",
        "tag.entity_type.enderio.soul_vial_blacklist": "영혼 약병 차단 목록",
        "tag.entity_type.enderio.soul_vial_whitelist": "영혼 약병 허용 목록",
        "tag.entity_type.enderio.spawner_blacklist": "스포너 차단 목록",
        "tag.entity_type.enderio.spawner_whitelist": "스포너 허용 목록",
        "tag.fluid.enderio.fluid_fuel.cold_fire_igniter": "차가운 불 점화기 연료",
        "tag.fluid.enderio.fluid_fuel.staff_of_levity": "부양의 지팡이 연료",
        "tag.fluid.enderio.solar_panel_dark": "어두운 태양광 패널",
        "tag.fluid.enderio.solar_panel_light": "밝은 태양광 패널",
        "tag.item.enderio.amethyst": "자수정",
        "tag.item.enderio.blacklists.broken_spawner": "부서진 스포너 차단 목록",
        "tag.item.enderio.blacklists.electromagnet": "전자석 차단 목록",
        "tag.item.enderio.blaze_powder": "블레이즈 가루",
        "tag.item.enderio.cloud_cold": "차가운 구름",
        "tag.item.enderio.crops": "작물",
        "tag.item.enderio.enderio.hide_facades": "위장판 숨기기",
    }
    ordered_keys = list(english)
    batch_keys = ordered_keys[BATCH_TWO_END:BATCH_THREE_END]
    for key in batch_keys:
        translated = translations.get(key)
        if translated is None:
            raise KeyError(f"세 번째 배치 번역이 없습니다: {key}")
        korean[key] = translated
    write_json(WORK_ROOT / "ko_kr.json", korean)
    write_json(WORK_ROOT / "keep_originals.json", KEEP_ORIGINALS)

    sources = load_json(WORK_ROOT / "candidate_sources.json")
    for key in batch_keys:
        sources[key] = "manual_translation"
    for key in KEEP_ORIGINALS:
        sources[key] = "reviewed_original"
    write_json(WORK_ROOT / "candidate_sources.json", sources)
    progress = load_json(WORK_ROOT / "progress.json")
    completed_batches = list(progress["completed_batches"])
    completed_batches.append(
        {
            "batch": 3,
            "range": [BATCH_TWO_END + 1, BATCH_THREE_END],
            "scope": "아이템, JEI, 메시지와 태그 앞부분",
        }
    )
    write_json(
        WORK_ROOT / "progress.json",
        {
            "family": "Ender IO",
            "batch_size": 180,
            "reviewed_keys": BATCH_THREE_END,
            "total_keys": len(english),
            "completed_batches": completed_batches,
            "status": "in_progress",
        },
    )
    print(f"세 번째 번역 배치 반영 완료: {len(batch_keys)}키")


def translate_batch_four() -> None:
    """태그와 툴팁 64키를 마지막 배치로 반영한다."""
    english = load_json(WORK_ROOT / "en_us.json")
    korean = load_json(WORK_ROOT / "ko_kr.json")
    translations = {
        "tag.item.enderio.explosives": "폭발물",
        "tag.item.enderio.insulation_metals": "절연용 금속",
        "tag.item.enderio.lightning_rod": "피뢰침",
        "tag.item.enderio.meat": "고기",
        "tag.item.enderio.natural_lights": "자연광",
        "tag.item.enderio.prismarine": "프리즈머린",
        "tag.item.enderio.seeds": "씨앗",
        "tag.item.enderio.sunflower": "해바라기",
        "tag.item.enderio.tools.glider": "글라이더",
        "tag.item.enderio.wind_charges": "돌풍구",
        "tooltip.enderio.armory.durability.amount": "내구도 %s",
        "tooltip.enderio.armory.ender_head_chance": "몹 머리를 떨어뜨릴 확률 %s%%",
        "tooltip.enderio.block.blast_resistant": "폭발 저항",
        "tooltip.enderio.conduit.energy.rate": "최대 출력 %s µI/t",
        "tooltip.enderio.conduit.facade.blast_resist": "강화: 파괴와 폭발에 견딤",
        "tooltip.enderio.conduit.facade.transparent": "투명: 반투명 블록으로 도색하면 도관을 숨김",
        "tooltip.enderio.conduit.fluid.effective_rate": "실제 전송률: %s mB/t",
        "tooltip.enderio.conduit.fluid.raw_rate": "전송률: 네트워크 틱당 %s mB",
        "tooltip.enderio.conduit.graph_tick_rate": "네트워크 틱: 초당 %s회",
        "tooltip.enderio.conduit.item.effective_rate": "실제 전송률: 초당 %s개",
        "tooltip.enderio.conduit.item.raw_rate": "전송률: 네트워크 틱당 %s개",
        "tooltip.enderio.conduit.probe.copy_paste": "탐침",
        "tooltip.enderio.conduit.probe.mode": "모드 %s",
        "tooltip.enderio.conduit.probe.mode.contains_copied": "복사/붙여넣기",
        "tooltip.enderio.conduit.probe.probe": "복사한 도관 데이터 포함:",
        "tooltip.enderio.dark_steel_ladder.faster": "일반 사다리보다 빠름",
        "tooltip.enderio.energy_equivalence": "FE와 같은 Ender IO 에너지 단위입니다.",
        "tooltip.enderio.filter.configured": "설정됨",
        "tooltip.enderio.filter.not_allowed_component_match": "이 필터는 현재 이 아이템에서 사용할 수 없는 구성 요소 일치를 사용합니다. 제작 칸에서 필터를 초기화하여 이 경고를 없애세요.",
        "tooltip.enderio.filter.unconfigured_hint": "웅크린 상태에서 사용하여 설정",
        "tooltip.enderio.fluid_tank.contents_tooltip": "%d/%d mB / %s",
        "tooltip.enderio.fluid_tank.empty_tooltip": "빈 탱크",
        "tooltip.enderio.glass.blocks_light": "빛을 차단함",
        "tooltip.enderio.glass.emits_light": "빛을 방출함",
        "tooltip.enderio.grinding_ball_bonus_output": "추가 생산량 %s%%",
        "tooltip.enderio.grinding_ball_main_output": "주 생산량 %s%%",
        "tooltip.enderio.grinding_ball_power_use": "전력 사용량 %s%%",
        "tooltip.enderio.lore.suspicious_seed": "이 씨앗은 주변의 경험치 구슬과 상호작용하는 것 같습니다...",
        "tooltip.enderio.machine.photovoltaic_cell.advanced": "낮 동안 전력을 생산함",
        "tooltip.enderio.machine.photovoltaic_cell.advanced2": "하늘이 가리지 않고 보여야 함",
        "tooltip.enderio.machine.photovoltaic_cell.advanced3": "최대 출력: ",
        "tooltip.enderio.machine.photovoltaic_cell.main": "태양광 발전!",
        "tooltip.enderio.machine.progress": "진행률 %s%%",
        "tooltip.enderio.machine.sag_mill.chance": "확률: %s%%",
        "tooltip.enderio.machine.sag_mill.chance.grinding_ball": "확률: %s%% (분쇄구 적용)",
        "tooltip.enderio.machine.sag_mill.grinding_ball.remaining": "남은 내구도: %s%%",
        "tooltip.enderio.machine.sag_mill.grinding_ball.title": "SAG 분쇄기 분쇄구",
        "tooltip.enderio.machine.status.active": "기계 작동 중",
        "tooltip.enderio.machine.status.blocked_by_redstone": "레드스톤 신호로 기계가 차단됨",
        "tooltip.enderio.machine.status.drain.no_source": "배수구 아래에 원천 블록이 있어야 작동함",
        "tooltip.enderio.machine.status.empty_tank": "탱크가 비어 있음",
        "tooltip.enderio.machine.status.energy_full": "에너지 저장소가 가득 참",
        "tooltip.enderio.machine.status.full_tank": "탱크가 가득 참",
        "tooltip.enderio.machine.status.idle": "기계 대기 중",
        "tooltip.enderio.machine.status.input_empty": "입력 칸에 아이템이 없음",
        "tooltip.enderio.machine.status.no_capacitor": "이 기계를 사용하려면 축전기를 설치하세요",
        "tooltip.enderio.machine.status.no_energy": "기계를 사용할 전력이 부족함",
        "tooltip.enderio.machine.status.output_full": "출력 공간이 부족함",
        "tooltip.enderio.no_soul_bound": "이 아이템에는 영혼을 귀속할 수 있습니다.",
        "tooltip.enderio.show_advanced_tooltip": "<Shift 누르기>",
        "tooltip.enderio.soul_bound": "귀속된 영혼: %s",
        "tooltip.enderio.tool.soul_vial.health": "생명력: %s/%s",
        "tooltip.enderio.tool.void_vial.hint": "플레이어 대신 경험치 구슬을 모읍니다. 탱크에 경험치를 넣거나 플레이어가 마실 수 있습니다.",
        "tooltip.enderio.tool.void_vial.stored_experience": "저장량: %s레벨 + 경험치 %s",
    }
    ordered_keys = list(english)
    batch_keys = ordered_keys[BATCH_THREE_END:]
    for key in batch_keys:
        translated = translations.get(key)
        if translated is None:
            raise KeyError(f"마지막 배치 번역이 없습니다: {key}")
        korean[key] = translated
    write_json(WORK_ROOT / "ko_kr.json", korean)

    sources = load_json(WORK_ROOT / "candidate_sources.json")
    for key in batch_keys:
        sources[key] = "manual_translation"
    write_json(WORK_ROOT / "candidate_sources.json", sources)
    progress = load_json(WORK_ROOT / "progress.json")
    completed_batches = list(progress["completed_batches"])
    completed_batches.append(
        {
            "batch": 4,
            "range": [BATCH_THREE_END + 1, len(english)],
            "scope": "태그와 툴팁",
        }
    )
    write_json(
        WORK_ROOT / "progress.json",
        {
            "family": "Ender IO",
            "batch_size": 180,
            "reviewed_keys": len(english),
            "total_keys": len(english),
            "completed_batches": completed_batches,
            "status": "language_complete",
        },
    )
    print(f"마지막 번역 배치 반영 완료: {len(batch_keys)}키")


def build_outputs() -> None:
    """완성된 언어 파일과 관련 FTB Quests 교정을 산출물에 반영한다."""
    if verify(require_complete=True):
        raise ValueError("전체 언어 검증이 실패하여 산출물을 만들 수 없습니다.")
    korean = load_json(WORK_ROOT / "ko_kr.json")
    write_json(OUTPUT_FILE, korean)

    instance = resolve_source_root()
    english_quests = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    current_quests = quest_snbt.parse_language_snbt(QUEST_OUTPUT_FILE)
    long_key = "quest.4A6B585C2394A89A.quest_desc"
    long_value = current_quests[long_key]
    if not isinstance(long_value, list):
        raise TypeError(f"퀘스트 값 자료형이 배열이 아닙니다: {long_key}")
    corrected_long = [
        value.replace("소울라리움", "솔라리움").replace(
            "&a&lEnderIO&r", "&a&lEnder IO&r"
        )
        for value in long_value
    ]
    quest_overrides: dict[str, quest_snbt.TranslationValue] = {
        "quest.4869C413646CC4CC.quest_desc": [
            "발전기에서 전력을 내보내는 것이 좋겠죠. 그런데 어떻게 옮길까요?",
            "",
            "처음에는 &aPipez&r 모드의 &c에너지 파이프&r를 사용하거나, 이미 해당 모드를 시작했다면 &9Powah&r의 &c에너지 케이블&r을 사용할 수 있습니다.",
            "",
            "옛날 방식이 그립다면 이 팩의 &6Ender IO&r가 제공하는 &6에너지 도관&r을 사용할 수도 있습니다.",
        ],
        long_key: corrected_long,
        "quest.5F1218CF8EFC607B.quest_desc": [
            "&c&lLaserIO&r는 DireWolf가 &a&lEnder IO&r의 &l물류&r 시스템을 이어 만든 모드입니다.",
            "",
            "아이템을 &c레이저&r로 옮기는 것이 핵심입니다! &c레이저&r를 싫어할 사람이 있을까요?!",
            "",
            "모든 것은 로직 칩에서 시작합니다.",
        ],
        "quest.010A970FC91BD617.quest_subtitle": "합금 제련기에서 제작",
        "quest.035495984F84FB44.quest_subtitle": "합금 제련기에서 제작",
        "quest.035495984F84FB44.title": "맥동 합금 벌",
        "quest.0691BDE968724213.quest_subtitle": "합금 제련기에서 제작",
        "quest.16987C41D4F5BA47.quest_subtitle": "합금 제련기에서 제작",
        "quest.205DE46ABA1CCC8F.quest_subtitle": "합금 제련기에서 제작",
        "quest.2FE088899C1AF39B.quest_subtitle": "합금 제련기에서 제작",
        "quest.692BC8AADCBF76C3.quest_subtitle": "합금 제련기에서 제작",
        "quest.728189EE56E5CAF7.quest_subtitle": "합금 제련기에서 제작",
        "quest.7A2B26CF0EDAA724.quest_subtitle": "합금 제련기에서 제작",
    }
    errors = []
    for key, translated in quest_overrides.items():
        source = english_quests.get(key)
        if source is None:
            errors.append(f"영어 퀘스트 원문에 키가 없습니다: {key}")
            continue
        errors.extend(quest_snbt.validate_value(key, source, translated))
    if errors:
        raise ValueError("\n".join(errors))

    merged = quest_snbt.merge_into_full_snbt(QUEST_OUTPUT_FILE, quest_overrides)
    QUEST_OUTPUT_FILE.write_text(merged, encoding="utf-8")
    reparsed = quest_snbt.parse_language_snbt(QUEST_OUTPUT_FILE)
    for key, value in quest_overrides.items():
        if reparsed.get(key) != value:
            raise ValueError(f"FTB Quests 병합 결과가 다릅니다: {key}")
    write_json(
        WORK_ROOT / "quest_english.json",
        {key: english_quests[key] for key in quest_overrides},
    )
    write_json(WORK_ROOT / "quest_overrides.json", quest_overrides)
    write_json(
        WORK_ROOT / "quest_validation.json",
        {
            "family": "Ender IO",
            "corrected_keys": len(quest_overrides),
            "type_errors": 0,
            "format_code_errors": 0,
            "placeholder_errors": 0,
            "number_errors": 0,
            "newline_errors": 0,
            "status": "complete",
        },
    )
    if verify_family_outputs():
        raise ValueError("Ender IO 계열 전체 검증이 실패했습니다.")
    print(f"산출물 빌드 완료: 언어 {len(korean)}키, 퀘스트 {len(quest_overrides)}키")


def verify_family_outputs(deployment_manifest: Path | None = None) -> int:
    """Ender IO 본체와 직접 연동되는 표시 경로의 누적 산출물을 검증한다."""
    errors: list[str] = []
    if verify(require_complete=True):
        errors.append("Ender IO 언어 파일 검증 실패")

    korean = load_json(WORK_ROOT / "ko_kr.json")
    if load_json(OUTPUT_FILE) != korean:
        errors.append("Ender IO 작업본과 리소스팩 산출물이 다릅니다.")

    quest_english = load_json(WORK_ROOT / "quest_english.json")
    quest_overrides = load_json(WORK_ROOT / "quest_overrides.json")
    quest_output = quest_snbt.parse_language_snbt(QUEST_OUTPUT_FILE)
    for key, value in quest_overrides.items():
        if quest_output.get(key) != value:
            errors.append(f"Ender IO 퀘스트 누적 출력 불일치: {key}")
        errors.extend(quest_snbt.validate_value(key, quest_english[key], value))

    related_language = {
        "crop.mysticalagriculture.soularium": "솔라리움",
        "crop.mysticalagriculture.dark_steel": "다크 스틸",
        "crop.mysticalagriculture.pulsating_alloy": "맥동 합금",
        "crop.mysticalagriculture.end_steel": "엔드 스틸",
    }
    for relative in (
        "working/mystical/mysticalagriculture/ko_kr.json",
        "output/resourcepack/ATM10_Korean/assets/mysticalagriculture/lang/ko_kr.json",
    ):
        values = load_json(PROJECT_ROOT / relative)
        for key, expected in related_language.items():
            if values.get(key) != expected:
                errors.append(f"Ender IO 연동 용어 불일치: {relative}:{key}")

    bee_key = "entity.productivebees.pulsating_alloy_bee"
    bee_value = "맥동 합금(Pulsating Alloy) 벌"
    for relative in (
        "working/productivebees/productivebees/ko_kr.json",
        "output/resourcepack/ATM10_Korean/assets/productivebees/lang/ko_kr.json",
    ):
        if load_json(PROJECT_ROOT / relative).get(bee_key) != bee_value:
            errors.append(f"Ender IO 연동 용어 불일치: {relative}:{bee_key}")

    bee_quests = {
        "quest.010A970FC91BD617.quest_subtitle": "합금 제련기에서 제작",
        "quest.035495984F84FB44.quest_subtitle": "합금 제련기에서 제작",
        "quest.035495984F84FB44.title": "맥동 합금 벌",
        "quest.0691BDE968724213.quest_subtitle": "합금 제련기에서 제작",
        "quest.16987C41D4F5BA47.quest_subtitle": "합금 제련기에서 제작",
        "quest.205DE46ABA1CCC8F.quest_subtitle": "합금 제련기에서 제작",
        "quest.2FE088899C1AF39B.quest_subtitle": "합금 제련기에서 제작",
        "quest.692BC8AADCBF76C3.quest_subtitle": "합금 제련기에서 제작",
        "quest.728189EE56E5CAF7.quest_subtitle": "합금 제련기에서 제작",
        "quest.7A2B26CF0EDAA724.quest_subtitle": "합금 제련기에서 제작",
    }
    bee_work = load_json(PROJECT_ROOT / "working/productivebees/quest_overrides.json")
    for key, expected in bee_quests.items():
        if bee_work.get(key) != expected or quest_output.get(key) != expected:
            errors.append(f"Productive Bees 연동 퀘스트 불일치: {key}")

    evil_work = load_json(PROJECT_ROOT / "working/evilcraft/evilcraftcompat/ko_kr.json")
    evil_output = load_json(
        PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/evilcraftcompat/lang/ko_kr.json"
    )
    for key in (
        "info_book.evilcraftcompat.mod_integrations.enderio",
        "info_book.evilcraftcompat.mod_integrations.enderio.text",
    ):
        if evil_output.get(key) != evil_work.get(key):
            errors.append(f"EvilCraft Ender IO 연동 출력 불일치: {key}")

    instance = resolve_source_root()
    chapters, _ = parse_chapters(instance / "config/ftbquests/quests")
    fallback_tasks = [
        task
        for chapter in chapters
        if chapter["filename"] == "apotheosis_2.snbt"
        for quest in chapter["quests"]
        if quest["id"] == "263860CADB3D76C6"
        for task in quest["tasks"]
        if task["id"] == "6AA7603047B9C2C3"
    ]
    if (
        len(fallback_tasks) != 1
        or fallback_tasks[0]["item_id"] != "enderio:powered_spawner"
    ):
        errors.append("동력 스포너 퀘스트 fallback Task를 확인하지 못했습니다.")
    if quest_output.get("quest.263860CADB3D76C6.title") is not None:
        errors.append("동력 스포너 퀘스트에 불필요한 명시적 제목이 있습니다.")
    if quest_output.get("task.6AA7603047B9C2C3.title") is not None:
        errors.append("동력 스포너 Task에 불필요한 명시적 제목이 있습니다.")
    if korean.get("block.enderio.powered_spawner") != "동력 스포너":
        errors.append("동력 스포너 아이템 fallback 이름이 일치하지 않습니다.")

    integration_scope = load_json(WORK_ROOT / "integration_scope.json")
    quest_scope = load_json(WORK_ROOT / "quest_scope.json")
    if integration_scope.get("status") != "complete":
        errors.append("Ender IO 연동 범위 조사가 완료 상태가 아닙니다.")
    if quest_scope.get("status") != "complete":
        errors.append("Ender IO 퀘스트 범위 조사가 완료 상태가 아닙니다.")

    deployment: dict[str, object] = {"status": "not_checked"}
    if deployment_manifest is not None:
        manifest = load_json(deployment_manifest)
        expected_changes = {
            "config/ftbquests/quests/lang/ko_kr.snbt",
            "resourcepacks/ATM10_Korean/assets/enderio/lang/ko_kr.json",
            "resourcepacks/ATM10_Korean/assets/mysticalagriculture/lang/ko_kr.json",
            "resourcepacks/ATM10_Korean/assets/productivebees/lang/ko_kr.json",
        }
        targets = manifest.get("targets", [])
        if manifest.get("status") != "applied_and_verified" or len(targets) != 1:
            errors.append("Ender IO 적용 매니페스트가 완료 상태가 아닙니다.")
        else:
            target = targets[0]
            changed_paths = set(target.get("changed_paths", []))
            if changed_paths != expected_changes:
                errors.append("Ender IO 적용 경로가 계획과 다릅니다.")
            if target.get("unexpected_changes"):
                errors.append("Ender IO 적용 중 계획하지 않은 파일이 변경되었습니다.")
            file_records = {
                record["relative_path"]: record for record in target.get("files", [])
            }
            hash_matches = 0
            for relative in expected_changes:
                record = file_records.get(relative)
                if record is None:
                    errors.append(f"Ender IO 적용 기록 누락: {relative}")
                    continue
                target_path = Path(record["target"])
                current_hash = hashlib.sha256(target_path.read_bytes()).hexdigest()
                if record.get("source_sha256") != record.get(
                    "after_sha256"
                ) or current_hash != record.get("after_sha256"):
                    errors.append(f"Ender IO 적용 파일 해시 불일치: {relative}")
                    continue
                hash_matches += 1
            deployment = {
                "status": "applied_and_verified" if not errors else "invalid",
                "target": target.get("target_root"),
                "backup_manifest": str(deployment_manifest),
                "changed_paths": sorted(changed_paths),
                "hash_matches": hash_matches,
                "unexpected_changes": target.get("unexpected_changes", []),
            }

    source_counts = Counter(load_json(WORK_ROOT / "candidate_sources.json").values())
    report = {
        "family": "Ender IO",
        "jar": "enderio-8.2.11-beta.jar",
        "language_keys": len(korean),
        "existing_project_reuse": source_counts["existing_project_translation_reuse"],
        "manual_translations": source_counts["manual_translation"],
        "reviewed_originals": source_counts["reviewed_original"],
        "bundled_korean_reuse": 0,
        "quest_corrections": len(quest_overrides),
        "related_language_corrections": 5,
        "related_quest_corrections": len(bee_quests),
        "advancement_display_fields": integration_scope["advancements"][
            "display_fields"
        ],
        "kubejs_display_strings": integration_scope["kubejs"][
            "direct_display_string_candidates"
        ],
        "patchouli_runtime_translation_required": integration_scope["patchouli"][
            "runtime_translation_required"
        ],
        "fallback_paths_checked": 1,
        "deployment": deployment,
        "remaining": len(errors),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    write_json(WORK_ROOT / "family_completion.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


def verify(reviewed_keys: int | None = None, require_complete: bool = False) -> int:
    """현재 번역과 지정한 검토 완료 범위를 검증한다."""
    instance = resolve_source_root()
    jar = find_jar(instance)
    with ZipFile(jar) as archive:
        installed_english = load_archive_json(archive, f"{LANG_ROOT}/en_us.json")

    english = load_json(WORK_ROOT / "en_us.json")
    korean = load_json(WORK_ROOT / "ko_kr.json")
    progress = load_json(WORK_ROOT / "progress.json")
    keep_originals = load_json(WORK_ROOT / "keep_originals.json")
    if reviewed_keys is None:
        reviewed_keys = int(progress.get("reviewed_keys", 0))
    ordered_keys = list(english)
    reviewed = ordered_keys[:reviewed_keys]

    errors: list[str] = []
    if english != installed_english:
        errors.append("작업 영어 원문이 현재 설치된 JAR과 다릅니다.")
    if set(english) != set(korean):
        errors.append("영어와 한국어 키 집합이 다릅니다.")

    type_errors: list[str] = []
    placeholder_errors: list[str] = []
    format_errors: list[str] = []
    newline_errors: list[str] = []
    for key, source in english.items():
        target = korean.get(key)
        if not isinstance(source, str) or not isinstance(target, str):
            type_errors.append(key)
            continue
        if Counter(PLACEHOLDER.findall(source)) != Counter(PLACEHOLDER.findall(target)):
            placeholder_errors.append(key)
        if Counter(FORMAT_CODE.findall(source)) != Counter(FORMAT_CODE.findall(target)):
            format_errors.append(key)
        if source.count("\n") != target.count("\n"):
            newline_errors.append(key)

    reviewed_untranslated = [
        key
        for key in reviewed
        if english[key] == korean.get(key) and key not in keep_originals
    ]
    remaining = [
        key for key in ordered_keys[reviewed_keys:] if english[key] == korean.get(key)
    ]
    translated_names: dict[str, list[str]] = defaultdict(list)
    for key in reviewed:
        value = korean.get(key)
        if isinstance(value, str):
            translated_names[value].append(key)
    collisions = [
        {"translation": value, "keys": keys}
        for value, keys in translated_names.items()
        if len(keys) > 1
        and len({english[key] for key in keys}) > 1
        and not set(keys) <= COLLISION_EXCEPTIONS.get(value, set())
    ]
    if type_errors:
        errors.append("문자열 자료형 오류: " + " | ".join(type_errors[:30]))
    if placeholder_errors:
        errors.append("자리표시자 불일치: " + " | ".join(placeholder_errors[:30]))
    if format_errors:
        errors.append("서식 코드 불일치: " + " | ".join(format_errors[:30]))
    if newline_errors:
        errors.append("줄바꿈 개수 불일치: " + " | ".join(newline_errors[:30]))
    if reviewed_untranslated:
        errors.append(
            "검토 완료 범위의 영어 잔존: " + " | ".join(reviewed_untranslated[:30])
        )
    if collisions:
        errors.append(
            "번역으로 생긴 이름 충돌: "
            + " | ".join(row["translation"] for row in collisions[:30])
        )
    if require_complete and remaining:
        errors.append("전체 완료 전 영어 잔존: " + " | ".join(remaining[:30]))

    report = {
        "family": "Ender IO",
        "jar": jar.name,
        "english_keys": len(english),
        "korean_keys": len(korean),
        "reviewed_keys": reviewed_keys,
        "remaining_keys": len(english) - reviewed_keys,
        "reviewed_untranslated": len(reviewed_untranslated),
        "remaining_values_equal_to_english": len(remaining),
        "type_errors": len(type_errors),
        "placeholder_errors": len(placeholder_errors),
        "format_code_errors": len(format_errors),
        "newline_errors": len(newline_errors),
        "duplicate_keys": 0,
        "translation_induced_name_collisions": len(collisions),
        "intentional_collision_exceptions": len(COLLISION_EXCEPTIONS),
        "output_untouched_until_complete": not require_complete,
        "validation_errors": len(errors),
        "errors": errors,
        "status": "complete"
        if require_complete and not errors
        else "batch_complete"
        if not errors
        else "error",
    }
    write_json(WORK_ROOT / "language_validation.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


def main() -> int:
    """명령행 진입점이다."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("prepare", help="설치본 언어 파일과 범위 정보를 준비합니다.")
    subparsers.add_parser("batch-one", help="첫 181키 번역 배치를 반영합니다.")
    subparsers.add_parser("batch-two", help="다음 180키 번역 배치를 반영합니다.")
    subparsers.add_parser("batch-three", help="세 번째 180키 번역 배치를 반영합니다.")
    subparsers.add_parser("batch-four", help="마지막 64키 번역 배치를 반영합니다.")
    subparsers.add_parser("build", help="완성된 언어와 퀘스트 산출물을 만듭니다.")
    family_parser = subparsers.add_parser(
        "verify-family", help="Ender IO 본체와 직접 연동 표시 경로를 함께 검증합니다."
    )
    family_parser.add_argument("--deployment-manifest", type=Path)
    verify_parser = subparsers.add_parser("verify", help="현재 번역 배치를 검증합니다.")
    verify_parser.add_argument("--reviewed-keys", type=int)
    verify_parser.add_argument(
        "--all", action="store_true", help="전체 605키 완료를 요구합니다."
    )
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
        return 0
    if args.command == "batch-one":
        translate_batch_one()
        return 0
    if args.command == "batch-two":
        translate_batch_two()
        return 0
    if args.command == "batch-three":
        translate_batch_three()
        return 0
    if args.command == "batch-four":
        translate_batch_four()
        return 0
    if args.command == "build":
        build_outputs()
        return 0
    if args.command == "verify-family":
        return verify_family_outputs(args.deployment_manifest)
    return verify(args.reviewed_keys, args.all)


if __name__ == "__main__":
    raise SystemExit(main())
