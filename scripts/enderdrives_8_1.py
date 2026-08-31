#!/usr/bin/env python3
"""EnderDrives 8.1 언어와 AE2 가이드 연동을 재기준화하고 검증해요."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile

import build_ae2_addon_guides as guide_builder
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

FAMILY = "enderdrives"
JAR_PATTERN = "enderdrives-*.jar"
LANGUAGE_PATH = "assets/enderdrives/lang/en_us.json"
BUNDLED_KOREAN_PATH = "assets/enderdrives/lang/ko_kr.json"
GUIDE_PREFIX = "assets/enderdrives/ae2guide/enderdrives_intro/"
EXPECTED_KEYS = 140
EXPECTED_REUSED = 41
EXPECTED_GUIDES = 3
WORK_ROOT = PROJECT_ROOT / "working/ae2_addons/enderdrives"
BASELINE_PATH = (
    PROJECT_ROOT
    / "output/7.1/resourcepack/ATM10_Korean/assets/enderdrives/lang/ko_kr.json"
)
LANG_WORKING_PATH = WORK_ROOT / "lang/ko_kr.json"
OUTPUT_PATH = (
    active_output_root()
    / "resourcepack/ATM10_Korean/assets/enderdrives/lang/ko_kr.json"
)
TEXT_SUFFIXES = {".cfg", ".ini", ".js", ".json", ".properties", ".snbt", ".toml"}
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")

UPGRADE_TRANSLATIONS = {
    "commands.enderdrives.autobench.best": "안전한 최대 시험 규모: %s종.",
    "commands.enderdrives.autobench.cancel.no_ae2_terminal": (
        "15초 안에 AE2 터미널을 열지 않아 벤치마크를 취소했습니다."
    ),
    "commands.enderdrives.autobench.cancel.offline": (
        "플레이어가 오프라인이 되어 벤치마크를 취소했습니다."
    ),
    "commands.enderdrives.autobench.freq_mismatch": (
        "주파수가 대기 중인 벤치마크 요청과 다릅니다. 확인하려면 다시 시작하세요."
    ),
    "commands.enderdrives.autobench.loop_summary": (
        "%1$s종: 삽입 %2$s ms, 조회 %3$s ms, 저장 %4$s종, 메모리 %5$s MiB, "
        "TPS %6$s, 평균 틱 %7$s ms."
    ),
    "commands.enderdrives.autobench.pending": (
        "시험 중 비공개 주파수 %1$s의 데이터가 삭제됩니다. 확인하려면 "
        "/enderdrives autobenchmark %2$s 명령어를 다시 실행하세요."
    ),
    "commands.enderdrives.autobench.starting": "%s개의 고유 아이템 종류로 벤치마크를 시작합니다.",
    "commands.enderdrives.autobench.tps_drop": (
        "TPS가 %s 아래로 떨어져 벤치마크를 중단했습니다."
    ),
    "commands.enderdrives.autobench.waiting_ae2_terminal": (
        "벤치마크를 계속하려면 AE2 터미널을 여세요."
    ),
    "commands.enderdrives.clear.confirm": (
        "주파수 %1$s의 %2$s 공유 범위 데이터를 삭제하려면 명령어를 다시 실행하세요."
    ),
    "commands.enderdrives.clear.no_permission": ("전역 저장소를 비울 권한이 없습니다."),
    "commands.enderdrives.clear.success": (
        "주파수 %1$s의 %2$s 공유 범위에 저장된 아이템과 유체 데이터를 삭제했습니다."
    ),
    "commands.enderdrives.common.no": "아니요",
    "commands.enderdrives.common.yes": "예",
    "commands.enderdrives.dumpcell.cell_access_failed": (
        "생성한 AE2 저장 셀에 접근할 수 없습니다."
    ),
    "commands.enderdrives.dumpcell.no_items": ("주파수 %s에 저장된 아이템이 없습니다."),
    "commands.enderdrives.dumpcell.no_permission": (
        "전역 저장소를 저장 셀로 내보낼 권한이 없습니다."
    ),
    "commands.enderdrives.dumpcell.success": (
        "아이템 %1$s개를 AE2 저장 셀 %2$s개로 내보냈습니다."
    ),
    "commands.enderdrives.dumpcell.success_clear_hint": (
        "EnderDrive 데이터는 삭제하지 않았습니다. 내보낸 내용을 확인한 뒤 "
        "/enderdrives clear 명령어를 사용하세요."
    ),
    "commands.enderdrives.freq.invalid": ("주파수는 %1$s 이상 %2$s 이하여야 합니다."),
    "commands.enderdrives.scope.invalid": (
        "올바르지 않은 공유 범위입니다. private, team 또는 global을 사용하세요."
    ),
    "commands.enderdrives.setfreq.hold_disk": ("주 손에 EnderDrive 디스크를 드세요."),
    "commands.enderdrives.setfreq.success": (
        "들고 있는 디스크의 주파수를 %s(으)로 설정했습니다."
    ),
    "commands.enderdrives.stats.fluids": (
        "유체 데이터베이스: 레코드 %1$s개, 쓰기 %2$s회, 커밋 %3$s회, "
        "디스크 사용량 %4$s바이트."
    ),
    "commands.enderdrives.stats.items": (
        "아이템 데이터베이스: 레코드 %1$s개, 쓰기 %2$s회, 커밋 %3$s회, "
        "디스크 사용량 %4$s바이트."
    ),
    "commands.enderdrives.stress.complete": "부하 시험을 완료했습니다.",
    "commands.enderdrives.stress.duplicate": (
        "아이템 %s에서 직렬화 데이터 해시 충돌이 발생했습니다."
    ),
    "commands.enderdrives.stress.duplicates": "해시 충돌: %s건.",
    "commands.enderdrives.stress.inserted": (
        "아이템 %1$s종을 %2$s ms 만에 삽입했습니다."
    ),
    "commands.enderdrives.stress.unique_types": "저장된 고유 종류: %s종.",
    "commands.enderdrives.tape.cleanup.error": (
        "테이프 %1$s을(를) 검사할 수 없습니다: %2$s"
    ),
    "commands.enderdrives.tape.cleanup.success": (
        "빈 테이프 파일 %s개를 제거했습니다."
    ),
    "commands.enderdrives.tape.delete.fail": "테이프 %s을(를) 삭제할 수 없습니다.",
    "commands.enderdrives.tape.delete.released": (
        "삭제하기 전에 테이프 %s을(를) 메모리에서 해제했습니다."
    ),
    "commands.enderdrives.tape.delete.success": "테이프 %s을(를) 삭제했습니다.",
    "commands.enderdrives.tape.diagnose.header": "테이프 %s 진단:",
    "commands.enderdrives.tape.diagnose.malformed": "형식이 잘못된 항목: %s개.",
    "commands.enderdrives.tape.diagnose.no_file": (
        "테이프 %s의 파일이 존재하지 않습니다."
    ),
    "commands.enderdrives.tape.diagnose.scan_error": (
        "테이프 파일을 검사할 수 없습니다: %s"
    ),
    "commands.enderdrives.tape.diagnose.size": "파일 크기: %s바이트.",
    "commands.enderdrives.tape.diagnose.suggest": (
        "복구 가능한 JSON 백업을 만들려면 /enderdrives tape export %s 명령어를 실행하세요."
    ),
    "commands.enderdrives.tape.diagnose.total": "읽은 항목: %s개.",
    "commands.enderdrives.tape.diagnose_all.empty": "테이프 파일을 찾지 못했습니다.",
    "commands.enderdrives.tape.diagnose_all.error": (
        "테이프 %1$s을(를) 검사할 수 없습니다: %2$s"
    ),
    "commands.enderdrives.tape.diagnose_all.fail_entry": (
        "테이프 %1$s에서 형식이 잘못된 항목 %2$s개를 찾았습니다(전체 %3$s개)."
    ),
    "commands.enderdrives.tape.diagnose_all.ok_entry": (
        "테이프 %1$s을(를) 읽을 수 있으며 잘못된 형식의 항목은 %2$s개입니다."
    ),
    "commands.enderdrives.tape.diagnose_all.summary": (
        "테이프 파일 %1$s개를 검사했으며 %2$s개는 확인이 필요합니다."
    ),
    "commands.enderdrives.tape.export.fail": "테이프를 JSON으로 내보내지 못했습니다.",
    "commands.enderdrives.tape.export.success": "테이프 %s을(를) JSON으로 내보냈습니다.",
    "commands.enderdrives.tape.import.fail": "JSON에서 테이프를 가져오지 못했습니다.",
    "commands.enderdrives.tape.import.success": "JSON에서 테이프 %s을(를) 가져왔습니다.",
    "commands.enderdrives.tape.info.bytes": "직렬화된 바이트: %s.",
    "commands.enderdrives.tape.info.header": "테이프 %s 정보:",
    "commands.enderdrives.tape.info.in_ram": "메모리에 로드됨: %s.",
    "commands.enderdrives.tape.info.last_accessed": "마지막 접근: %s.",
    "commands.enderdrives.tape.info.not_in_ram": "메모리에 로드되지 않음",
    "commands.enderdrives.tape.info.pinned": "고정됨: %s.",
    "commands.enderdrives.tape.info.types": "저장된 종류: %s종.",
    "commands.enderdrives.tape.invalid_uuid": "올바르지 않은 테이프 UUID: %s",
    "commands.enderdrives.tape.list.empty": ("현재 메모리에 로드된 테이프가 없습니다."),
    "commands.enderdrives.tape.list.entry": "%1$s: 저장된 종류 %2$s종.",
    "commands.enderdrives.tape.list.header": "로드된 테이프:",
    "commands.enderdrives.tape.oldest.empty": "테이프 파일을 찾지 못했습니다.",
    "commands.enderdrives.tape.oldest.entry": ("%1$s, 수정 시각 %2$s, %3$s바이트."),
    "commands.enderdrives.tape.oldest.header": ("오래된 순서로 정렬한 테이프 파일:"),
    "commands.enderdrives.tape.pin.success": ("테이프 %s을(를) 메모리에 고정했습니다."),
    "commands.enderdrives.tape.release.fail": (
        "테이프 %s을(를) 영구 저장하지 못해 메모리에 계속 로드해 둡니다."
    ),
    "commands.enderdrives.tape.release.not_cached": (
        "테이프 %s은(는) 메모리에 로드되어 있지 않습니다."
    ),
    "commands.enderdrives.tape.release.success": (
        "테이프 %s을(를) 메모리에서 해제했습니다."
    ),
    "commands.enderdrives.tape.stats.cached": "메모리에 로드된 테이프: %s개.",
    "commands.enderdrives.tape.stats.disk_usage": (
        "디스크의 테이프 저장소 사용량: %s바이트."
    ),
    "commands.enderdrives.tape.stats.file_count": "디스크의 테이프 파일: %s개.",
    "commands.enderdrives.tape.stats.header": "테이프 데이터베이스 통계:",
    "commands.enderdrives.tape.stats.ram_usage": ("메모리에서 직렬화된 바이트: %s."),
    "commands.enderdrives.tape.stats.total_types": ("메모리에 저장된 종류: %s종."),
    "commands.enderdrives.tape.unpin.success": (
        "테이프 %s의 메모리 고정을 해제했습니다."
    ),
    "commands.enderdrives.team.none": "FTB 팀에 가입되어 있지 않습니다.",
    "commands.enderdrives.team.unavailable": (
        "FTB Teams를 사용할 수 없어 팀 저장소에 접근할 수 없습니다."
    ),
    "item.enderdrives.ender_fluid_disk_16k": "16k 엔더 유체 저장 셀",
    "item.enderdrives.ender_fluid_disk_1k": "1k 엔더 유체 저장 셀",
    "item.enderdrives.ender_fluid_disk_256k": "256k 엔더 유체 저장 셀",
    "item.enderdrives.ender_fluid_disk_4k": "4k 엔더 유체 저장 셀",
    "item.enderdrives.ender_fluid_disk_64k": "64k 엔더 유체 저장 셀",
    "item.enderdrives.ender_fluid_disk_creative": "크리에이티브 엔더 유체 저장 셀",
    "item.enderdrives.ender_fluid_housing": "엔더 유체 하우징",
    "item.enderdrives.ender_fluid_storage_component_16k": "16k 엔더 유체 저장 부품",
    "item.enderdrives.ender_fluid_storage_component_1k": "1k 엔더 유체 저장 부품",
    "item.enderdrives.ender_fluid_storage_component_256k": "256k 엔더 유체 저장 부품",
    "item.enderdrives.ender_fluid_storage_component_4k": "4k 엔더 유체 저장 부품",
    "item.enderdrives.ender_fluid_storage_component_64k": "64k 엔더 유체 저장 부품",
    "item.enderdrives.ender_item_housing": "엔더 아이템 하우징",
    "tooltip.enderdrives.disabled": "§c이 아이템은 서버에서 비활성화되었습니다.",
    "tooltip.enderdrives.disk.duplicate_sleep": (
        "비활성: 이 ME 네트워크에서 주파수와 공유 범위가 같은 다른 엔더 디스크가 "
        "활성화되어 있습니다."
    ),
    "tooltip.enderdrives.enderdisk.disabled": (
        "§c이 엔더 디스크는 서버에서 비활성화되었습니다."
    ),
    "tooltip.enderdrives.fluid_types": "%s§7 / §9%s§7 유체 종류",
    "tooltip.enderdrives.fluidenderdisk.disabled": (
        "§c이 엔더 유체 디스크는 서버에서 비활성화되었습니다."
    ),
    "tooltip.enderdrives.partitioned_fluid": "§7파티션 유체: §f%s단위%s",
    "tooltip.enderdrives.partitioned_item": "§7파티션 항목: §f%s개%s",
    "tooltip.enderdrives.tape.duplicate_sleep": (
        "비활성: 이 ME 네트워크에서 같은 테이프 디스크의 다른 복사본이 활성화되어 있습니다."
    ),
}


def load_json(path: Path) -> dict[str, str]:
    """UTF-8 문자열 JSON 객체를 읽어요."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise TypeError(f"문자열 JSON 객체가 아니에요: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 기록해요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def source_jar() -> Path:
    """현재 인스턴스의 EnderDrives JAR 하나를 찾아요."""
    matches = sorted((resolve_source_root() / "mods").glob(JAR_PATTERN))
    if len(matches) != 1:
        raise FileNotFoundError(f"EnderDrives JAR 수가 1개가 아니에요: {matches}")
    return matches[0]


def read_jar_language(jar: Path, member: str) -> dict[str, str]:
    """JAR 언어 파일 하나를 읽어요."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read(member))
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise TypeError(f"문자열 언어 파일이 아니에요: {jar.name}:{member}")
    return value


def read_optional_jar_language(jar: Path, member: str) -> dict[str, str]:
    """JAR에 한국어 후보가 없으면 빈 사전을 반환해요."""
    with ZipFile(jar) as archive:
        if member not in archive.namelist():
            return {}
    return read_jar_language(jar, member)


def prepare() -> dict[str, object]:
    """현재 언어와 가이드 원문 범위를 기록해요."""
    jar = source_jar()
    english = read_jar_language(jar, LANGUAGE_PATH)
    bundled = read_optional_jar_language(jar, BUNDLED_KOREAN_PATH)
    with ZipFile(jar) as archive:
        guides = sorted(
            name
            for name in archive.namelist()
            if name.startswith(GUIDE_PREFIX) and name.endswith(".md")
        )
    write_json(WORK_ROOT / "lang/en_us.json", english)
    write_json(WORK_ROOT / "lang/bundled_ko_kr.json", bundled)
    report = {
        "family": FAMILY,
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_mtime_ns": jar.stat().st_mtime_ns,
        "english_keys": len(english),
        "bundled_korean_keys": len(bundled),
        "baseline_korean_keys": len(load_json(BASELINE_PATH)),
        "upgrade_review_keys": len(UPGRADE_TRANSLATIONS),
        "guide_files": guides,
        "status": "prepared",
    }
    write_json(WORK_ROOT / "upgrade_inventory.json", report)
    return report


def build() -> dict[str, object]:
    """7.1 검수본과 8.1 변경분을 현재 영어 키 구조로 합쳐요."""
    english = load_json(WORK_ROOT / "lang/en_us.json")
    baseline = load_json(BASELINE_PATH)
    if len(english) != EXPECTED_KEYS:
        raise ValueError(f"현재 영어 키 수가 달라요: {len(english)} != {EXPECTED_KEYS}")
    if len(UPGRADE_TRANSLATIONS) != 99:
        raise ValueError(f"8.1 검토 키 수가 달라요: {len(UPGRADE_TRANSLATIONS)} != 99")
    missing_review = sorted(set(UPGRADE_TRANSLATIONS) - set(english))
    if missing_review:
        raise ValueError(f"현재 원문에 없는 검토 키가 있어요: {missing_review}")
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
    write_json(LANG_WORKING_PATH, korean)
    report = {
        "reviewed_language_keys": len(korean),
        "existing_korean_reused": reused,
        "new_language_translations": len(UPGRADE_TRANSLATIONS),
        "removed_language_keys": 1,
        "guide_pages_rebased": 1,
        "status": "complete",
    }
    write_json(WORK_ROOT / "upgrade_translation_report.json", report)
    return report


def scan_references() -> tuple[dict[str, object], list[str]]:
    """실제 인스턴스의 FTB Quests와 KubeJS 참조를 검사해요."""
    instance = resolve_source_root()
    errors = []
    result = {}
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
        display_lines = []
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeDecodeError) as exc:
                errors.append(f"{path.relative_to(instance).as_posix()}: {exc}")
                continue
            if "enderdrives" not in text.lower():
                continue
            relative = path.relative_to(instance).as_posix()
            files.append(relative)
            for number, line in enumerate(text.splitlines(), 1):
                lowered = line.lower()
                if "enderdrives" in lowered and any(
                    token in lowered for token in display_tokens
                ):
                    display_lines.append(f"{relative}:{number}:{line.strip()}")
        result[label] = {
            "reference_files": files,
            "direct_display_lines": display_lines,
        }
    return result, errors


def audit() -> tuple[dict[str, object], list[str]]:
    """가이드·클래스·KubeJS 우회 문구와 외부 참조를 함께 감사해요."""
    instance = resolve_source_root()
    guide_report = guide_builder.validate_enderdrives(instance, compare_output=False)
    guide_errors = list(guide_report["errors"])
    references, reference_errors = scan_references()
    errors = guide_errors + reference_errors
    report = {
        "family": FAMILY,
        "guide_pages": guide_report["guide_pages"],
        "guide_source_words": guide_report["source_words"],
        "language_keys": len(guide_report["translated_lang"]),
        "kubejs_translation_files": guide_report["kubejs_files"],
        "instance_references": references,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "upgrade_surface_audit.json", report)
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """현재 원문·작업본·출력과 전체 EnderDrives 표시 경로를 검증해요."""
    english = load_json(WORK_ROOT / "lang/en_us.json")
    korean = load_json(LANG_WORKING_PATH)
    output = load_json(OUTPUT_PATH)
    errors = []
    if list(english) != list(korean):
        errors.append("영어와 한국어의 키 또는 순서가 달라요")
    if output != korean:
        errors.append("언어 작업본과 리소스팩 출력이 달라요")
    for key in english.keys() & korean.keys():
        errors.extend(family_goal.validate_value(key, english[key], korean[key]))
        if key in UPGRADE_TRANSLATIONS and korean[key] != UPGRADE_TRANSLATIONS[key]:
            errors.append(f"8.1 확정 번역값 불일치: {key}")
        if (
            key in UPGRADE_TRANSLATIONS
            and english[key] == korean[key]
            and LATIN_WORD.search(english[key])
        ):
            errors.append(f"8.1 검토 키가 영어와 같아요: {key}")
    integrated = guide_builder.validate_enderdrives(
        resolve_source_root(), compare_output=True
    )
    errors.extend(integrated["errors"])
    report = {
        "family": FAMILY,
        "language_keys": len(korean),
        "existing_korean_reused": EXPECTED_REUSED,
        "new_language_translations": len(UPGRADE_TRANSLATIONS),
        "guide_pages": integrated["guide_pages"],
        "kubejs_translation_files": integrated["kubejs_files"],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "upgrade_validation.json", report)
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
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
