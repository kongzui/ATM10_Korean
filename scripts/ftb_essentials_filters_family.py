#!/usr/bin/env python3
"""FTB Essentials와 FTB Filter System의 현재 JAR 영어 전체를 번역·검증한다."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "ftb_essentials_filters"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
RESOURCEPACK_ROOT = active_output_root() / "resourcepack/ATM10_Korean/assets"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[./xX×]\d+)*")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
ALLOWED_LATIN = {
    "ATM",
    "CustomFilterEvent",
    "dat",
    "data",
    "Filter",
    "FTB",
    "Minecraft",
    "SNBT",
    "smhdw",
    "Shift",
    "System",
    "TPA",
    "UUID",
    "rtp",
}

FTB_ESSENTIALS = {
    "sidebar_button.ftbessentials.trash_can": "휴지통",
    "ftbessentials.chat.status.start_record": "님이 녹화를 시작했습니다!",
    "ftbessentials.chat.status.stop_record": "님이 녹화를 중지했습니다!",
    "ftbessentials.chat.status.start_stream": "님이 방송을 시작했습니다!",
    "ftbessentials.chat.status.stop_stream": "님이 방송을 중지했습니다!",
    "ftbessentials.messages.kick_self": "자기 자신을 내보냈습니다!",
    "ftbessentials.feedback.limit_radius": "반경을 %s(으)로 제한합니다",
    "ftbessentials.near.players_within": "%s명(반경 %sm 이내)",
    "ftbessentials.teleport_prevented": "순간이동이 차단되었습니다!",
    "ftbessentials.tpa.expired": "TPA 요청이 만료되었습니다!",
    "ftbessentials.muted": "관리자에 의해 음소거되어 채팅을 사용할 수 없습니다!",
    "ftbessentials.mute_expiry": "음소거 해제까지: %s",
    "ftbessentials.enderchest.unable": "엔더 상자 인벤토리를 열 수 없습니다!",
    "ftbessentials.flight.disabled": "비행 비활성화",
    "ftbessentials.flight.enabled": "비행 활성화",
    "ftbessentials.god_mode.disabled": "무적 모드 비활성화",
    "ftbessentials.god_mode.enabled": "무적 모드 활성화",
    "ftbessentials.teleport.history_empty": "순간이동 기록이 비어 있습니다!",
    "ftbessentials.teleport.max_less_than_min": (
        "최대 순간이동 거리는 최소 거리보다 작을 수 없습니다!"
    ),
    "ftbessentials.rtp.not_here": "이 차원에서는 /rtp를 사용할 수 없습니다!",
    "ftbessentials.rtp.looking": "무작위 위치를 찾는 중...",
    "ftbessentials.rtp.found": "%s번 시도 후 적합한 위치를 찾았습니다: %s",
    "ftbessentials.rtp.failed": "순간이동할 수 있는 위치를 찾지 못했습니다!",
    "ftbessentials.jump.failed": "도약할 수 없습니다: %s",
    "ftbessentials.kit.added_items": "키트 '%s'의 아이템을 대상 인벤토리에 추가했습니다",
    "ftbessentials.kit.no_items": "키트에 추가할 아이템이 없습니다!",
    "ftbessentials.kit.cant_store": "인벤토리에 키트를 저장할 수 없습니다: %s",
    "ftbessentials.kit.created": "키트 '%s'을(를) 만들었습니다",
    "ftbessentials.kit.deleted": "키트 '%s'을(를) 삭제했습니다",
    "ftbessentials.kit.autogrant_modified": (
        "키트 '%s'의 자동 지급 설정을 변경했습니다: %s"
    ),
    "ftbessentials.kit.cooldown_modified": (
        "키트 '%s'의 재사용 대기시간을 변경했습니다: %s"
    ),
    "ftbessentials.kit.gave_to_players": (
        "키트 '%s'을(를) 플레이어 %s명에게 지급했습니다"
    ),
    "ftbessentials.kit.no_permission": "키트 '%s'을(를) 지급할 권한이 없습니다",
    "ftbessentials.kit.not_looking_at_block": "바라보는 블록이 없습니다",
    "ftbessentials.kit.not_enough_space": "키트를 저장할 인벤토리 공간이 부족합니다",
    "ftbessentials.kit_name": "키트 이름: %s",
    "ftbessentials.kit.count": "키트 %s개",
    "ftbessentials.kit.cooldown": "재사용 대기시간: %s",
    "ftbessentials.kit.cooldown.none": "재사용 대기시간 없음",
    "ftbessentials.kit.one_time": "한 번만 사용",
    "ftbessentials.kit.one_time_only": (
        '키트 "%s"은(는) 한 번만 사용할 수 있습니다("%s"에게 이미 지급됨)'
    ),
    "ftbessentials.kit.on_cooldown": (
        '키트 "%s"은(는) 재사용 대기 중입니다. 남은 시간: %s'
    ),
    "ftbessentials.kit.autogranted": "플레이어 로그인 시 자동 지급",
    "ftbessentials.kit.items": "아이템:",
    "ftbessentials.kit.no_such_kit": "그런 키트가 없습니다: '%s'",
    "ftbessentials.kit.already_exists": "키트 '%s'이(가) 이미 있습니다",
    "ftbessentials.kit.cooldown_reset": (
        "%s의 재사용 대기시간을 UUID %s에서 초기화했습니다"
    ),
    "ftbessentials.kit.cooldown_reset_all": (
        "%s의 재사용 대기시간을 모든 플레이어에게서 초기화했습니다"
    ),
    "ftbessentials.muted.muted": (
        "플레이어 %s이(가) %s에 의해 음소거되었습니다. 기간: %s"
    ),
    "ftbessentials.muted.unmuted": ("플레이어 %s의 음소거가 %s에 의해 해제되었습니다"),
    "ftbessentials.nick.too_long": "별명이 너무 깁니다!",
    "ftbessentials.nick.reset": "별명을 초기화했습니다!",
    "ftbessentials.nick.changed": "별명을 '%s'(으)로 변경했습니다",
    "ftbessentials.duration.indefinite": "별도 공지가 있을 때까지",
    "ftbessentials.duration.expected_format": (
        "기간 형식이 올바르지 않습니다. 예상 형식: <숫자>[smhdw]"
    ),
    "ftbessentials.speed_boost": "%s의 속도 증가(%s): %s%%",
    "ftbessentials.speed_boost.none": "%s의 속도 증가 없음",
    "ftbessentials.leaderboard": "순위표 [ %s ]",
    "ftbessentials.leaderboard.no_data": "데이터 없음!",
    "ftbessentials.home.set": "홈을 설정했습니다!",
    "ftbessentials.home.too_many": "홈을 더 추가할 수 없습니다!",
    "ftbessentials.home.deleted": "홈을 삭제했습니다!",
    "ftbessentials.home.not_found": "홈을 찾을 수 없습니다!",
    "ftbessentials.home.show_home": "%s: %s 떨어짐",
    "ftbessentials.home.y_too_low": (
        "Y 좌표가 너무 낮습니다! 홈은 Y=%s보다 위에 설정해야 합니다"
    ),
    "ftbessentials.none": "없음",
    "ftbessentials.home.for_player": "%s의 홈",
    "ftbessentials.click_to_teleport": "클릭해 순간이동",
    "ftbessentials.unknown_player_id": "알 수 없는 플레이어 ID: %s",
    "ftbessentials.unknown_player": "알 수 없는 플레이어: %s",
    "ftbessentials.tp_offline.player_is_online": (
        "플레이어가 온라인 상태입니다! 일반 /tp 명령어를 사용하세요"
    ),
    "ftbessentials.tp_offline.moved": (
        "오프라인 플레이어 %s을(를) %s(으)로 이동했습니다(차원: %s)"
    ),
    "ftbessentials.tp_offline.cant_update": "dat 파일을 갱신할 수 없습니다: %s",
    "ftbessentials.tpa.already_sent": "이미 요청을 보냈습니다!",
    "ftbessentials.tpa.notify": "TPA 요청! [ %s ➡ %s ]",
    "ftbessentials.tpa.click_one": "다음 중 하나를 클릭하세요: ",
    "ftbessentials.tpa.accept": "수락 ✔",
    "ftbessentials.tpa.accept.tooltip": "클릭해 수락",
    "ftbessentials.tpa.deny": "거절 ❌",
    "ftbessentials.tpa.deny.tooltip": "클릭해 거절",
    "ftbessentials.tpa.request_sent": "요청을 보냈습니다!",
    "ftbessentials.tpa.invalid_request": "잘못된 요청입니다!",
    "ftbessentials.tpa.gone_offline": "플레이어가 오프라인 상태가 되었습니다!",
    "ftbessentials.tpa.denied": "요청이 거절되었습니다!",
    "ftbessentials.warp.set": "워프를 설정했습니다!",
    "ftbessentials.warp.deleted": "워프를 삭제했습니다!",
    "ftbessentials.warp.not_found": "워프를 찾을 수 없습니다!",
    "ftbessentials.dimension_not_found": "차원을 찾을 수 없습니다!",
    "ftbessentials.unknown_dest": "알 수 없는 목적지입니다!",
    "ftbessentials.teleport.not_from_here": (
        "현재 차원에서는 다른 곳으로 순간이동할 수 없습니다!"
    ),
    "ftbessentials.teleport.not_to_here": "이 차원으로 순간이동할 수 없습니다!",
    "ftbessentials.teleport.on_cooldown": (
        "아직 순간이동할 수 없습니다! 남은 대기시간: %s"
    ),
    "ftbessentials.teleport.interrupted": "순간이동이 중단되었습니다!",
    "ftbessentials.teleport.notify": "%s초 후 순간이동합니다",
}

FTB_FILTER_SYSTEM = {
    "ftbfiltersystem": "FTB Filter System",
    "item.ftbfiltersystem.smart_filter": "스마트 필터",
    "item.ftbfiltersystem.smart_filter.tooltip.1": "우클릭: 필터 설정",
    "item.ftbfiltersystem.smart_filter.tooltip.2": (
        "Shift + 우클릭: 보조 손의 아이템으로 필터 테스트"
    ),
    "ftbfiltersystem.message.parse_failed": "필터 분석 실패: %s",
    "ftbfiltersystem.message.not_a_filter": "주 손에 스마트 필터를 들고 있어야 합니다",
    "ftbfiltersystem.message.not_configured": "이 스마트 필터에는 필터가 설정되지 않았습니다",
    "ftbfiltersystem.message.no_offhand_item": (
        "테스트할 아이템을 보조 손에 들고 있어야 합니다"
    ),
    "ftbfiltersystem.message.matched": "필터 일치: %s",
    "ftbfiltersystem.message.not_matched": "필터 불일치: %s",
    "ftbfiltersystem.message.changes_saved": "필터를 갱신했습니다!",
    "ftbfiltersystem.message.cache_cleared": "컴파일된 필터 캐시를 비웠습니다",
    "ftbfiltersystem.message.components_header": "%s개의 데이터 구성 요소(%s):",
    "ftbfiltersystem.message.components_header_none": "데이터 구성 요소 없음",
    "ftbfiltersystem.message.non_default_components": (
        "기본값이 아닌 구성 요소만 표시합니다"
    ),
    "ftbfiltersystem.gui.add": "추가...",
    "ftbfiltersystem.gui.delete": "삭제",
    "ftbfiltersystem.gui.configure": "설정...",
    "ftbfiltersystem.gui.percentage": "백분율",
    "ftbfiltersystem.gui.item_source.creative": "크리에이티브",
    "ftbfiltersystem.gui.item_source.inventory": "인벤토리",
    "ftbfiltersystem.gui.item_source.mod": "모드",
    "ftbfiltersystem.gui.nbt_ok": "SNBT 분석 성공",
    "ftbfiltersystem.gui.nbt_bad": "SNBT 분석 실패!",
    "ftbfiltersystem.gui.filter_ok": "필터 분석 성공",
    "ftbfiltersystem.gui.filter_bad": "필터 분석 실패!",
    "ftbfiltersystem.gui.custom_id": "사용자 지정 이벤트 ID:",
    "ftbfiltersystem.gui.custom_data": "추가 사용자 지정 데이터:",
    "ftbfiltersystem.gui.changes_made": "이 필터를 변경했습니다",
    "ftbfiltersystem.gui.changes_made.question": "저장하지 않고 편집기를 닫으시겠습니까?",
    "ftbfiltersystem.gui.compound": "복합 필터",
    "ftbfiltersystem.gui.basic": "기본 필터",
    "ftbfiltersystem.gui.fuzzy_match": "구성 요소 유사 일치?",
    "ftbfiltersystem.gui.custom_name": "사용자 지정 이름",
    "filter.ftbfiltersystem.and.name": "모두 만족",
    "filter.ftbfiltersystem.and.tooltip": (
        "복합 필터: 모든 하위 필터가 일치할 때 이 필터가 일치합니다."
    ),
    "filter.ftbfiltersystem.or.name": "하나 이상 만족",
    "filter.ftbfiltersystem.or.tooltip": (
        "복합 필터: 하나 이상의 하위 필터가 일치할 때 이 필터가 일치합니다."
    ),
    "filter.ftbfiltersystem.not.name": "부정",
    "filter.ftbfiltersystem.not.tooltip": (
        "복합 필터: 하위 필터가 일치하지 않을 때 이 필터가 일치합니다. "
        "하위 필터는 하나만 추가할 수 있습니다."
    ),
    "filter.ftbfiltersystem.only_one.name": "하나만 만족",
    "filter.ftbfiltersystem.only_one.tooltip": (
        "복합 필터: 정확히 하나의 하위 필터만 일치할 때 이 필터가 일치합니다."
    ),
    "filter.ftbfiltersystem.block.name": "블록 여부",
    "filter.ftbfiltersystem.block.tooltip": "설치 가능한 블록인 아이템과 일치합니다.",
    "filter.ftbfiltersystem.component.name": "아이템 구성 요소",
    "filter.ftbfiltersystem.component.tooltip": (
        "아이템의 데이터 구성 요소를 비교합니다.\n"
        "정확히 일치(모든 구성 요소가 일치해야 함)와 유사 일치(필터의 구성 요소만 비교)를 지원합니다.\n"
        "관리자 권한이 있으면 인벤토리에서 기본값이 아닌 구성 요소 데이터가 있는 아이템을 "
        "클릭해 현재 데이터를 SNBT로 직렬화하여 텍스트 편집기에 복사할 수 있습니다."
    ),
    "filter.ftbfiltersystem.durability.name": "내구도",
    "filter.ftbfiltersystem.durability.tooltip": (
        "남은 내구도를 기준으로 아이템을 비교합니다.\n"
        "내구도가 없는 아이템의 내구도는 0으로 간주합니다."
    ),
    "filter.ftbfiltersystem.food_value.name": "허기 회복량",
    "filter.ftbfiltersystem.food_value.tooltip": (
        "영양가(회복되는 허기 반 칸 수)를 기준으로 아이템을 비교합니다.\n"
        "음식이 아닌 아이템의 영양가는 0입니다."
    ),
    "filter.ftbfiltersystem.item.name": "아이템",
    "filter.ftbfiltersystem.item.tooltip": (
        "특정 아이템과 일치하는지 비교합니다.\n"
        "아이템 구성 요소 데이터는 여기서 확인하지 않습니다(구성 요소 필터 참고).\n"
        "크리에이티브 또는 인벤토리 아이템 목록에서 아이템을 선택할 수 있습니다.\n"
        "표시할 아이템을 줄이려면 텍스트 입력란에서 아이템 ID를 검색하세요."
    ),
    "filter.ftbfiltersystem.item_tag.name": "아이템 태그",
    "filter.ftbfiltersystem.item_tag.tooltip": (
        "아이템 태그와 비교하며, 해당 태그에 속한 아이템이 일치합니다.\n"
        "텍스트 입력란에서 표시할 아이템 태그를 검색할 수 있습니다."
    ),
    "filter.ftbfiltersystem.stack_size.name": "묶음 수량",
    "filter.ftbfiltersystem.stack_size.tooltip": "현재 묶음 수량을 기준으로 아이템을 비교합니다.",
    "filter.ftbfiltersystem.max_stack_size.name": "최대 묶음 수량",
    "filter.ftbfiltersystem.max_stack_size.tooltip": (
        "최대 묶음 수량을 기준으로 아이템을 비교합니다.\n"
        "겹칠 수 없는 아이템의 최대 묶음 수량은 1입니다."
    ),
    "filter.ftbfiltersystem.mod.name": "모드",
    "filter.ftbfiltersystem.mod.tooltip": (
        "아이템을 추가한 모드를 기준으로 비교합니다.\n"
        "바닐라 아이템은 Minecraft '모드'에 속합니다."
    ),
    "filter.ftbfiltersystem.custom.name": "사용자 지정",
    "filter.ftbfiltersystem.custom.tooltip": (
        "모드 및 모드팩 제작자를 위한 고급 필터입니다.\n"
        "일치를 시도하면 CustomFilterEvent를 발생시키며, 이벤트 결과로 일치 성공 또는 실패를 정합니다.\n"
        "이벤트의 'data' 매개변수로 전달할 자유 형식 텍스트를 입력란에 지정하세요."
    ),
    "filter.ftbfiltersystem.expression.name": "표현식",
    "filter.ftbfiltersystem.expression.tooltip": (
        "필터 표현식을 직접 입력하거나 인벤토리의 필터 아이템에서 불러올 수 있습니다.\n"
        "알아보기 쉽도록 사용자 지정 이름을 지정하는 것이 좋습니다."
    ),
    "filter.ftbfiltersystem.root.name": "루트(모두 만족)",
}

NAMESPACES = {
    "ftbessentials": {
        "jar_pattern": "ftb-essentials-*.jar",
        "translations": FTB_ESSENTIALS,
    },
    "ftbfiltersystem": {
        "jar_pattern": "ftb-filter-system-*.jar",
        "translations": FTB_FILTER_SYSTEM,
    },
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
    """파일의 SHA-256 해시를 계산한다."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_jar(instance: Path, pattern: str) -> Path:
    """현재 설치본에서 패턴에 맞는 JAR 하나를 찾는다."""
    jars = sorted((instance / "mods").glob(pattern))
    if len(jars) != 1:
        raise RuntimeError(
            f"대상 JAR 수가 1개가 아닙니다: {[path.name for path in jars]}"
        )
    return jars[0]


def read_jar_language(jar: Path, namespace: str) -> dict[str, object]:
    """원본 JAR에서 영어 언어 파일을 읽는다."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read(f"assets/{namespace}/lang/en_us.json"))
    if not isinstance(value, dict):
        raise TypeError(f"JAR 영어 언어 파일이 객체가 아닙니다: {jar}")
    return value


def prepare() -> dict[str, object]:
    """두 현재 JAR의 영어를 작업본으로 추출한다."""
    instance = resolve_source_root()
    rows = []
    for namespace, config in NAMESPACES.items():
        jar = source_jar(instance, str(config["jar_pattern"]))
        english = read_jar_language(jar, namespace)
        with ZipFile(jar) as archive:
            bundled_korean = f"assets/{namespace}/lang/ko_kr.json" in archive.namelist()
        root = WORK_ROOT / namespace
        write_json(root / "en_us.json", english)
        write_json(
            root / "candidate_sources.json",
            {key: "manual_current_en_us" for key in english},
        )
        rows.append(
            {
                "namespace": namespace,
                "jar": jar.name,
                "jar_size": jar.stat().st_size,
                "jar_mtime_ns": jar.stat().st_mtime_ns,
                "english_keys": len(english),
                "bundled_korean": bundled_korean,
            }
        )
    report = {
        "family": FAMILY,
        "namespaces": rows,
        "english_keys": sum(int(row["english_keys"]) for row in rows),
        "existing_korean_reused": 0,
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", report)
    return report


def build() -> dict[str, object]:
    """검수된 키별 번역을 작업본과 리소스팩에 생성한다."""
    counts = {}
    for namespace, config in NAMESPACES.items():
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        translations = config["translations"]
        if not isinstance(translations, dict):
            raise TypeError(f"번역표가 객체가 아닙니다: {namespace}")
        missing = sorted(set(english) - set(translations))
        extra = sorted(set(translations) - set(english))
        if missing or extra:
            raise KeyError(f"{namespace} 번역표 불일치: 누락={missing}, 초과={extra}")
        korean = {key: translations[key] for key in english}
        write_json(WORK_ROOT / namespace / "ko_kr.json", korean)
        write_json(RESOURCEPACK_ROOT / namespace / "lang/ko_kr.json", korean)
        counts[namespace] = len(korean)
    report = {
        "reviewed_keys": sum(counts.values()),
        "namespace_keys": counts,
        "existing_korean_reused": 0,
        "new_translation_keys": sum(counts.values()),
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def quest_audit(instance: Path) -> tuple[dict[str, object], list[str]]:
    """스마트 필터 Task와 FTB Essentials 안내 퀘스트를 감사한다."""
    quest_root = instance / "config/ftbquests/quests"
    smart_filter_rows = []
    custom_names = []
    read_errors = []
    for path in sorted(quest_root.rglob("*.snbt")):
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except UnicodeDecodeError as exc:
            read_errors.append(f"{path.relative_to(instance).as_posix()}: {exc}")
            continue
        for number, line in enumerate(lines, 1):
            if 'id: "ftbfiltersystem:smart_filter"' not in line:
                continue
            smart_filter_rows.append(
                f"{path.relative_to(instance).as_posix()}:{number}"
            )
            match = re.search(r'"minecraft:custom_name":\s*"((?:\\.|[^"\\])*)"', line)
            if match:
                custom_names.append(match.group(1))
    english_lang = (quest_root / "lang/en_us.snbt").read_text(encoding="utf-8-sig")
    korean_lang = (quest_root / "lang/ko_kr.snbt").read_text(encoding="utf-8-sig")
    essentials_english = [
        line for line in english_lang.splitlines() if "ftbessentials.snbt" in line
    ]
    essentials_korean = [
        line for line in korean_lang.splitlines() if "ftbessentials.snbt" in line
    ]
    errors = list(read_errors)
    if len(essentials_english) != 1 or len(essentials_korean) != 1:
        errors.append(
            "FTB Essentials 명령어 안내 퀘스트의 영어·한국어 표시 키가 각각 1개가 아닙니다"
        )
    required_commands = ("/sethome", "/home", "/spawn", "/rtp", "ftbessentials.snbt")
    if essentials_korean and not all(
        command in essentials_korean[0] for command in required_commands
    ):
        errors.append(
            "FTB Essentials 안내 퀘스트에서 명령어 또는 설정 파일명이 누락됐습니다"
        )
    latin_custom_names = sorted(
        {
            word
            for value in custom_names
            for word in LATIN_WORD.findall(value)
            if word not in {"MOX"}
        }
    )
    if latin_custom_names:
        errors.append(
            f"스마트 필터 custom_name 영문 후보가 있습니다: {latin_custom_names}"
        )
    return (
        {
            "smart_filter_tasks": len(smart_filter_rows),
            "smart_filter_chapter_files": len(
                {row.rsplit(":", 1)[0] for row in smart_filter_rows}
            ),
            "custom_names_reviewed": len(custom_names),
            "custom_name_english_candidates": latin_custom_names,
            "ftbessentials_quest_display_keys": len(essentials_korean),
            "read_errors": read_errors,
        },
        errors,
    )


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR 및 관련 퀘스트·KubeJS·가이드 표시 표면을 감사한다."""
    instance = resolve_source_root()
    jar_rows = []
    for namespace, config in NAMESPACES.items():
        jar = source_jar(instance, str(config["jar_pattern"]))
        with ZipFile(jar) as archive:
            visible_data = sorted(
                name
                for name in archive.namelist()
                if name.startswith("data/")
                and name.endswith(".json")
                and any(
                    token in name for token in ("advancement", "guide", "patchouli")
                )
            )
        jar_rows.append(
            {
                "namespace": namespace,
                "jar": jar.name,
                "advancement_guide_entries": visible_data,
            }
        )
    quests, quest_errors = quest_audit(instance)
    guide = (
        instance
        / "resourcepacks/ATM10_Korean/assets/modularrouters/patchouli_books/book/ko_kr/entries/filters/ftb_filter_system.json"
    )
    errors = list(quest_errors)
    guide_status = "missing"
    if guide.is_file():
        guide_value = load_json(guide)
        guide_text = json.dumps(guide_value, ensure_ascii=False)
        guide_status = (
            "reviewed_korean" if "스마트 필터" in guide_text else "incomplete"
        )
    if guide_status != "reviewed_korean":
        errors.append(
            f"Modular Routers의 FTB Filter System 가이드 상태: {guide_status}"
        )
    kubejs_references = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json"}:
            continue
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, 1):
            if any(
                name in line.lower() for name in ("ftbessentials", "ftbfiltersystem")
            ):
                kubejs_references.append(
                    f"{path.relative_to(instance).as_posix()}:{number}:{line.strip()}"
                )
    report = {
        "family": FAMILY,
        "jars": jar_rows,
        "ftbquests": quests,
        "modular_routers_guide": guide_status,
        "kubejs_references": kubejs_references,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """현재 JAR·작업본·산출물과 문자열 보존 규칙을 검증한다."""
    instance = resolve_source_root()
    audit_report = load_json(WORK_ROOT / "surface_audit.json")
    errors = []
    namespace_reports = []
    total_keys = 0
    for namespace, config in NAMESPACES.items():
        jar = source_jar(instance, str(config["jar_pattern"]))
        jar_english = read_jar_language(jar, namespace)
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        output = load_json(RESOURCEPACK_ROOT / namespace / "lang/ko_kr.json")
        current_errors = []
        untranslated = []
        latin_residue = {}
        if jar_english != english:
            current_errors.append("작업 영어가 현재 설치 JAR 영어와 다릅니다")
        if list(english) != list(korean):
            current_errors.append("한국어 키 또는 키 순서가 영어 원문과 다릅니다")
        if korean != output:
            current_errors.append("작업 한국어와 리소스팩 산출물이 다릅니다")
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
                ("숫자", NUMBER),
            ):
                if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
                    current_errors.append(f"{label} 불일치: {key}")
            if source.count("\n") != target.count("\n"):
                current_errors.append(f"줄바꿈 불일치: {key}")
            if source == target and key != "ftbfiltersystem":
                untranslated.append(key)
            residue = sorted(set(LATIN_WORD.findall(target)) - ALLOWED_LATIN)
            if residue:
                latin_residue[key] = residue
        collisions = defaultdict(list)
        for key, target in korean.items():
            if isinstance(target, str):
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
                f"서로 다른 영어 이름의 한국어 충돌: {unexpected_collisions}"
            )
        namespace_reports.append(
            {
                "namespace": namespace,
                "keys": len(english),
                "untranslated_candidates": untranslated,
                "latin_residue": latin_residue,
                "unexpected_name_collisions": unexpected_collisions,
                "errors": current_errors,
            }
        )
        total_keys += len(english)
        errors.extend(f"{namespace}: {message}" for message in current_errors)
    if audit_report.get("status") != "complete":
        errors.append("표시 표면 감사가 완료되지 않았습니다")
    report = {
        "family": FAMILY,
        "namespaces": namespace_reports,
        "keys": total_keys,
        "existing_korean_reused": 0,
        "new_translation_keys": total_keys,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "language_validation.json", report)
    quest_report = audit_report.get("ftbquests", {})
    completion = {
        "family": FAMILY,
        "versions": {
            "ftbessentials": "2101.1.9",
            "ftbfiltersystem": "21.1.4",
        },
        "language_keys": total_keys,
        "existing_korean_reused": 0,
        "new_translation_keys": total_keys,
        "ftbquests": quest_report,
        "modular_routers_guide": audit_report.get("modular_routers_guide"),
        "kubejs_references": len(audit_report.get("kubejs_references", [])),
        "output_files": [
            (RESOURCEPACK_ROOT / namespace / "lang/ko_kr.json")
            .relative_to(PROJECT_ROOT)
            .as_posix()
            for namespace in NAMESPACES
        ],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_completion.json", completion)
    return report, errors


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 스크립트의 두 산출물 백업·해시 결과를 완료 기록에 반영한다."""
    resolved_manifest = manifest_path.resolve()
    try:
        relative_manifest = resolved_manifest.relative_to(PROJECT_ROOT).as_posix()
    except ValueError as exc:
        raise ValueError(f"프로젝트 밖의 적용 기록입니다: {resolved_manifest}") from exc
    manifest = load_json(resolved_manifest)
    completion_path = WORK_ROOT / "family_completion.json"
    completion = load_json(completion_path)
    selected = {
        f"resourcepacks/ATM10_Korean/assets/{namespace}/lang/ko_kr.json": (
            RESOURCEPACK_ROOT / namespace / "lang/ko_kr.json"
        )
        for namespace in NAMESPACES
    }
    errors = []
    matched_targets = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 기록 상태가 applied_and_verified가 아닙니다")
    targets = manifest.get("targets")
    if not isinstance(targets, list):
        errors.append("적용 기록의 targets가 목록이 아닙니다")
        targets = []
    for target in targets:
        if not isinstance(target, dict):
            continue
        files = target.get("files")
        if not isinstance(files, list):
            continue
        rows = {
            str(row.get("relative_path")): row
            for row in files
            if isinstance(row, dict) and row.get("relative_path") in selected
        }
        if set(rows) != set(selected):
            continue
        for relative, source in selected.items():
            row = rows[relative]
            target_file = Path(str(row.get("target")))
            if not target_file.is_file() or sha256(target_file) != sha256(source):
                errors.append(f"적용 대상과 산출물의 해시가 다릅니다: {target_file}")
            if row.get("source_sha256") != row.get("after_sha256"):
                errors.append(f"적용 기록의 전후 해시가 다릅니다: {target_file}")
        matched_targets.append(target)
    if len(matched_targets) != 1:
        errors.append(f"대상 적용 기록 수가 1개가 아닙니다: {len(matched_targets)}")
    target = matched_targets[0] if matched_targets else {}
    deployment = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "target": target.get("target_root"),
        "changed_paths": target.get("changed_paths", []),
        "backup_manifest": relative_manifest,
        "output_sha256": {
            namespace: sha256(RESOURCEPACK_ROOT / namespace / "lang/ko_kr.json")
            for namespace in NAMESPACES
        },
        "errors": errors,
    }
    completion["deployment"] = deployment
    if errors:
        completion["status"] = "incomplete"
    write_json(completion_path, completion)
    return deployment, errors


def run_all() -> tuple[dict[str, object], list[str]]:
    """준비부터 감사·빌드·검증까지 순서대로 실행한다."""
    prepare_report = prepare()
    audit_report, audit_errors = audit()
    build_report = build()
    verify_report, verify_errors = verify()
    result = {
        "prepare": prepare_report,
        "audit": audit_report,
        "build": build_report,
        "verify": verify_report,
        "status": "complete"
        if not audit_errors and not verify_errors
        else "incomplete",
    }
    return result, audit_errors + verify_errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "audit", "build", "verify", "record-deployment", "all"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        report, errors = prepare(), []
    elif args.command == "audit":
        report, errors = audit()
    elif args.command == "build":
        report, errors = build(), []
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
