#!/usr/bin/env python3
"""Supplementaries와 Amendments의 표시 문구를 현재 영어 원문으로 전면 재검수해요."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import five_family_goal as family_goal
from ars_family import request_translation
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "supplementaries_amendments"
ROOT = PROJECT_ROOT / "working" / FAMILY
CACHE_PATH = PROJECT_ROOT / "temp/supplementaries_amendments_candidate_cache_v2.json"
MANUAL_REVIEW_PATH = ROOT / "manual_review_8_1.json"
LATIN = re.compile(r"[A-Za-z]{3,}")
NUMBER = re.compile(r"\d+(?:[.,/xX×]\d+)*")

SUPPLEMENTARIES_EXACT = {
    "tab.supplementaries.supplementaries": "Supplementaries",
    "trim_pattern.supplementaries.blast": "폭발 방어구 장식",
    "item.supplementaries.blast_armor_trim_smithing_template": "대장장이 형판",
    "block.supplementaries.gold_bars": "금 창살",
    "block.supplementaries.ash_bricks": "재 벽돌 블록",
    "item.supplementaries.bunting": "장식 깃발",
    "entity.supplementaries.plunderer": "노략꾼",
    "item.supplementaries.plunderer_spawn_egg": "노략꾼 생성 알",
    "commands.supplementaries.configs": "설정에 접근하려면 Configured를 설치하세요",
    "commands.supplementaries.configs_reloaded": "Supplementaries 설정을 다시 불러왔습니다!",
    "commands.supplementaries.record.start": "소리 블록 녹음을 시작했습니다",
    "commands.supplementaries.record.stop": "소리 블록 녹음을 중지하고 recorded_songs/%s에 노래를 저장했습니다",
    "painting.supplementaries.bombs.author": "Plantkillable",
    "painting.supplementaries.jar.author": "TestedBubble",
    "subtitles.supplementaries.aeugh": "복어가 괴상한 소리를 냄",
    "supplementaries.configuration.sack.sack_increment.description": (
        "과적 효과가 적용되기 시작하는 자루의 최대 개수입니다. 이 개수의 배수마다 "
        "효과 강도가 한 단계씩 증가합니다."
    ),
    "supplementaries.configuration.slingshot.block_outline_color.description": (
        "블록 외곽선에 사용할 RGBA 색상을 hex 형식으로 지정합니다. 예를 들어 바닐라 "
        "외곽선 색상은 0x00000066입니다."
    ),
    "tag.block.supplementaries.column_shape_4x4": "4x4 기둥 형태",
    "tag.block.supplementaries.column_shape_6x6": "6x6 기둥 형태",
    "tag.block.supplementaries.column_shape_8x8": "8x8 기둥 형태",
    "tag.block.supplementaries.column_shape_10x10": "10x10 기둥 형태",
    "supplementaries.configuration.wind_vane.power_scaling.description": (
        "풍향계 애니메이션은 다음 식에 따라 흔들립니다: \n"
        "pitch(time) = max_angle_1*sin(2pi*time*pow/period_1) + "
        "<max_angle_2>*sin(2pi*time*pow/<period_2>)\n"
        "각 항목:\n"
        " - pow = max(1,redstone_power*<power_scaling>)\n"
        " - time = 틱 단위 시간\n"
        " - redstone_power = 블록의 레드스톤 동력\n"
        "<power_scaling> = 동력에 따라 주파수가 변하는 정도입니다. 2이면 동력 "
        "레벨마다 두 배 빠르게 회전합니다(비가 오면 2배, 천둥번개가 치면 4배).\n"
        "날씨가 바뀔 때 차이를 더 뚜렷하게 표시하려면 값을 높이세요"
    ),
    "gui.supplementaries.optifine.message": (
        "계속하기 전에 OptiFine이 문제와 충돌을 일으키는 것으로 알려져 있다는 점을 확인하세요.\n\n"
        " OptiFine은 모드 환경에 적합하지 않으며 Forge 자체와도 심각한 호환성 문제가 여러 차례 있었습니다.\n\n"
        " 성능 면에서도 ModernFix, Embeddium, 셰이더용 Oculus처럼 훨씬 빠른 대안이 있습니다. \n\n"
        "모드 환경과 바닐라 환경 어느 쪽에서 플레이하든 아래에 나열된 모드를 대신 사용하는 것이 좋습니다."
    ),
}

COLORS = {
    "indigo": "남색",
    "turquoise": "터키석색",
    "teal": "암청록색",
    "royal_blue": "로열 블루",
    "navy": "네이비",
    "sky_blue": "하늘색",
    "azure": "하늘빛",
    "cerulean": "세룰리안",
    "cobalt": "코발트색",
    "sapphire": "사파이어색",
    "rose": "장미색",
    "crimson": "진홍색",
    "maroon": "고동색",
    "coral": "산호색",
    "salmon": "연어색",
    "peach": "복숭아색",
    "tan": "황갈색",
    "beige": "베이지색",
    "ginger": "생강색",
    "amber": "호박색",
    "olive": "올리브색",
    "forest": "숲색",
    "verdant": "선록색",
    "jade": "옥색",
    "emerald": "에메랄드색",
    "mint": "민트색",
    "aqua": "아쿠아색",
    "slate": "슬레이트색",
}

AMENDMENTS_EXACT = {
    "block.amendments.tool_hook": "도구 걸이",
    "item.amendments.dragon_charge": "드래곤 화염구",
    "block.amendments.candle_skull": "양초가 놓인 해골",
    "block.amendments.hanging_pot": "매달린 화분",
    "block.amendments.hanging_flower_pot": "매달린 꽃 화분",
    "block.amendments.double_cake": "겹 케이크",
    "block.amendments.ceiling_banner": "천장 현수막",
    "tag.item.amendments.goes_in_lectern": "독서대에 놓을 수 있음",
    "tag.item.amendments.goes_in_tripwire_hook": "철사덫 갈고리에 걸 수 있음",
    "tag.item.amendments.non_stackable_heads": "겹칠 수 없는 머리",
    "tag.item.amendments.sets_on_fire": "불을 붙임",
    "tag.moonlight.amendments.soft_fluid.can_glow": "빛날 수 있음",
    "tag.moonlight.amendments.soft_fluid.cant_boil": "끓일 수 없음",
    "tag.moonlight.amendments.soft_fluid.cant_extinguish": "불을 끌 수 없음",
    "tag.moonlight.amendments.soft_fluid.cant_go_in_liquid_cauldron": "액체 가마솥에 담을 수 없음",
    "tag.moonlight.amendments.soft_fluid.no_tint_in_cauldron": "가마솥에서 색조를 적용하지 않음",
}
for slug, value in COLORS.items():
    AMENDMENTS_EXACT[f"item.amendments.dye_bottle.{slug}"] = value

REPLACEMENTS = (
    ("레시피", "제작법"),
    ("블랙리스트", "차단 목록"),
    ("화이트리스트", "허용 목록"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("왼쪽 클릭", "좌클릭"),
    ("스미싱 템플릿", "대장장이 형판"),
    ("갑옷 트림", "방어구 장식"),
    ("배너", "현수막"),
    ("헤드", "머리"),
    ("글로우", "발광"),
    ("Noteblocks", "소리 블록"),
    ("글로브", "지구본"),
    ("엔터티", "개체"),
    ("로프", "밧줄"),
    ("풀리", "도르래"),
    ("승수", "배율"),
    ("퓨즈", "도화선"),
    ("쿨다운", "재사용 대기시간"),
    ("캐논볼", "대포알"),
    ("트랩도어", "다락문"),
    ("풍로", "풀무"),
    ("전차대", "회전대"),
    ("총알총", "새총"),
    ("Optifine", "OptiFine"),
    ("3d", "3D"),
    ("0로", "0으로"),
    ("1를", "1을"),
    ("내쏘는", "함정"),
    ("진드기", "틱"),
    ("광고 소재", "크리에이티브"),
    ("구이", "GUI"),
    ("씌우다", "오버레이"),
    ("참고 입자", "음표 입자"),
    ("고패", "도르래"),
    ("델타 미터", "고도계"),
    ("조명에 맞", "번개에 맞"),
    ("속보 허용", "파괴 허용"),
    ("잘못 짜인 흠", "다락문"),
    ("화재 혐의", "화염구"),
    ("부활절 달걀", "이스터 에그"),
    ("수스", "수상한"),
    ("브레이크 반경", "파괴 반경"),
    ("음악 디스크", "음반"),
    ("트레이더", "상인"),
    ("노트블록", "소리 블록"),
    ("메모 블록", "소리 블록"),
    ("도구 설명", "툴팁"),
)


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def transform(value: object) -> object:
    if isinstance(value, str):
        for old, new in REPLACEMENTS:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [transform(item) for item in value]
    return value


def translation_memory() -> tuple[dict[str, str], set[str]]:
    """현재 프로젝트 검수본에서 영어 원문별 재사용 가능한 번역을 모아요."""
    values: dict[str, set[str]] = {}
    for namespace in ("supplementaries", "amendments"):
        root = ROOT / namespace
        english = load(root / "en_us.json")
        korean = load(root / "ko_kr.json")
        sources = load(root / "candidate_sources.json")
        for key, source in english.items():
            target = korean[key]
            if (
                sources[key] == "new_translation_required"
                or not isinstance(source, str)
                or not isinstance(target, str)
                or source == target
            ):
                continue
            values.setdefault(source, set()).add(target)
    conflicts = {source for source, candidates in values.items() if len(candidates) > 1}
    memory = {
        source: next(iter(candidates))
        for source, candidates in values.items()
        if len(candidates) == 1
    }
    return memory, conflicts


def manual_review() -> tuple[dict[str, dict[str, str]], dict[str, int]]:
    """현재 버전 신규 후보의 수동 검수 결과와 검수 수를 읽어요."""
    data = load(MANUAL_REVIEW_PATH)
    if data.get("status") != "complete":
        raise ValueError("Supplementaries·Amendments 수동 검수가 완료되지 않았습니다")
    overrides = data.get("overrides")
    reviewed_counts = data.get("reviewed_candidate_counts")
    if not isinstance(overrides, dict) or not isinstance(reviewed_counts, dict):
        raise TypeError(MANUAL_REVIEW_PATH)
    result: dict[str, dict[str, str]] = {}
    counts: dict[str, int] = {}
    for namespace in ("supplementaries", "amendments"):
        values = overrides.get(namespace)
        count = reviewed_counts.get(namespace)
        if not isinstance(values, dict) or not isinstance(count, int):
            raise TypeError(f"수동 검수 자료형 오류: {namespace}")
        if not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in values.items()
        ):
            raise TypeError(f"수동 검수 번역 자료형 오류: {namespace}")
        result[namespace] = values
        counts[namespace] = count
    return result, counts


def candidates() -> dict[str, object]:
    """8.1 신규 키의 보호 처리된 검수용 번역 후보를 만들어요."""
    memory, conflicts = translation_memory()
    cache = load(CACHE_PATH) if CACHE_PATH.is_file() else {}
    pending: set[str] = set()
    rows: dict[str, dict[str, object]] = {}
    source_rows: dict[str, dict[str, str]] = {}
    for namespace, exact in (
        ("supplementaries", SUPPLEMENTARIES_EXACT),
        ("amendments", AMENDMENTS_EXACT),
    ):
        root = ROOT / namespace
        english = load(root / "en_us.json")
        sources = load(root / "candidate_sources.json")
        translated: dict[str, object] = {}
        provenance: dict[str, str] = {}
        for key, value in english.items():
            if sources[key] != "new_translation_required":
                continue
            if not isinstance(value, str):
                raise TypeError(f"자동 후보가 지원하지 않는 자료형: {namespace}:{key}")
            if key in exact:
                translated[key] = exact[key]
                provenance[key] = "exact_key_override"
            elif family_goal.is_allowed_original(value):
                translated[key] = value
                provenance[key] = "reviewed_original_candidate"
            elif value in memory and value not in conflicts:
                translated[key] = memory[value]
                provenance[key] = "family_memory_candidate"
            elif isinstance(cache.get(value), str):
                translated[key] = cache[value]
                provenance[key] = "automatic_cache_candidate"
            else:
                pending.add(value)
        rows[namespace] = translated
        source_rows[namespace] = provenance

    failures = []
    if pending:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(request_translation, source): source
                for source in sorted(pending)
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                except (
                    Exception
                ) as exc:  # pragma: no cover - 외부 후보 서비스 오류 보고용
                    failures.append(f"{source}: {exc}")
        write(CACHE_PATH, cache)
    if failures:
        raise RuntimeError("자동 번역 후보 생성 실패:\n" + "\n".join(failures))

    counts: Counter[str] = Counter()
    for namespace in ("supplementaries", "amendments"):
        root = ROOT / namespace
        english = load(root / "en_us.json")
        sources = load(root / "candidate_sources.json")
        translated = rows[namespace]
        provenance = source_rows[namespace]
        for key, value in english.items():
            if sources[key] != "new_translation_required" or key in translated:
                continue
            target = cache[value]
            errors = family_goal.validate_value(key, value, target)
            if errors:
                raise ValueError("; ".join(errors))
            translated[key] = target
            provenance[key] = "automatic_translation_candidate"
        write(root / "auto_candidates.json", translated)
        write(root / "auto_candidate_sources.json", provenance)
        counts.update(provenance.values())
    report = {
        "scope": "Supplementaries·Amendments 8.1 신규 언어 키 검수 후보",
        "protected_patterns": [
            "numbers",
            "placeholders",
            "URLs",
            "format codes",
            "line breaks",
        ],
        "current_output_self_reuse_excluded": True,
        "translation_memory_conflicts_excluded": len(conflicts),
        "candidate_counts": dict(sorted(counts.items())),
        "review_status": "pending_manual_review",
    }
    write(ROOT / "auto_candidate_report.json", report)
    return report


def normalize() -> dict[str, object]:
    manual, reviewed_counts = manual_review()
    rows = []
    for namespace, exact in (
        ("supplementaries", SUPPLEMENTARIES_EXACT),
        ("amendments", AMENDMENTS_EXACT),
    ):
        root = ROOT / namespace
        english, korean = load(root / "en_us.json"), load(root / "ko_kr.json")
        auto, sources = (
            load(root / "auto_candidates.json"),
            load(root / "candidate_sources.json"),
        )
        new_count = sum(v == "new_translation_required" for v in sources.values())
        if reviewed_counts[namespace] != new_count:
            raise ValueError(
                f"수동 검수 수 불일치: {namespace} "
                f"{reviewed_counts[namespace]} != {new_count}"
            )
        unknown = sorted(set(manual[namespace]) - set(english))
        if unknown:
            raise ValueError(
                f"현재 원문에 없는 수동 검수 키: {namespace}:{unknown[:20]}"
            )
        reviewed = {}
        for key in english:
            value = manual[namespace].get(key, exact.get(key))
            if value is None:
                value = (
                    auto[key]
                    if sources[key] == "new_translation_required"
                    else korean[key]
                )
            reviewed[key] = transform(value)
        if namespace == "supplementaries":
            for key in english:
                if key.startswith("block.supplementaries.bunting_"):
                    reviewed[key] = (
                        transform(reviewed[key])
                        .replace("멧새", "장식 깃발")
                        .replace("번팅", "장식 깃발")
                    )
                    if not str(reviewed[key]).endswith("장식 깃발"):
                        reviewed[key] = str(reviewed[key]).replace("깃발", "장식 깃발")
        write(root / "ko_kr.json", reviewed)
        rows.append(
            {
                "namespace": namespace,
                "keys": len(reviewed),
                "project_output_reused": sum(
                    v == "project_output_review" for v in sources.values()
                ),
                "bundled_korean_reused": sum(
                    v == "bundled_ko_kr" for v in sources.values()
                ),
                "new_translation_reviewed": new_count,
                "manual_corrections": len(manual[namespace]),
            }
        )
    candidate_report = load(ROOT / "auto_candidate_report.json")
    candidate_report.update(
        {
            "review_status": "manual_review_complete",
            "reviewed_candidate_counts": reviewed_counts,
            "manual_correction_counts": {
                namespace: len(values) for namespace, values in manual.items()
            },
        }
    )
    write(ROOT / "auto_candidate_report.json", candidate_report)
    result = {"languages": rows, "status": "complete"}
    write(ROOT / "normalization.json", result)
    return result


def verify() -> tuple[dict[str, object], list[str]]:
    rows, errors = [], []
    for namespace in ("supplementaries", "amendments"):
        root = ROOT / namespace
        english, korean = load(root / "en_us.json"), load(root / "ko_kr.json")
        untranslated = []
        if list(english) != list(korean):
            errors.append(f"키 또는 순서 불일치: {namespace}")
        for key in english.keys() & korean.keys():
            source, target = english[key], korean[key]
            errors.extend(family_goal.validate_value(key, source, target))
            if isinstance(source, str) and isinstance(target, str):
                if Counter(NUMBER.findall(source)) != Counter(NUMBER.findall(target)):
                    errors.append(f"숫자 불일치: {namespace}:{key}")
                if (
                    source == target
                    and LATIN.search(source)
                    and not (
                        source
                        in {
                            "Supplementaries",
                            "Amendments",
                            "Plantkillable",
                            "TestedBubble",
                        }
                        or family_goal.is_allowed_original(source)
                        or key.startswith("jukebox_song.")
                        or key == "message.supplementaries.fluid_tooltip"
                    )
                ):
                    untranslated.append(key)
        if untranslated:
            errors.append(f"분류되지 않은 영어 유지: {namespace}:{untranslated[:20]}")
        rows.append(
            {"namespace": namespace, "keys": len(english), "untranslated": untranslated}
        )
    result = {
        "languages": rows,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write(ROOT / "specialized_validation.json", result)
    return result, errors


def audit() -> tuple[dict[str, object], list[str]]:
    instance = resolve_source_root()
    rows = []
    for target in family_goal.targets_for(FAMILY):
        jar = family_goal.find_jar(instance, target.jar_prefix)
        with ZipFile(jar) as archive:
            names = archive.namelist()
            rows.append(
                {
                    "jar": jar.name,
                    "advancements": sum(
                        n.endswith(".json") and "/advancement" in n for n in names
                    ),
                    "recipes": sum(
                        n.endswith(".json") and "/recipe" in n for n in names
                    ),
                }
            )
    result = {"jars": rows, "kubejs_direct_display_lines": [], "status": "complete"}
    write(ROOT / "surface_audit.json", result)
    return result, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("candidates", "normalize", "verify", "audit")
    )
    args = parser.parse_args()
    report, errors = (
        (candidates(), [])
        if args.command == "candidates"
        else (normalize(), [])
        if args.command == "normalize"
        else verify()
        if args.command == "verify"
        else audit()
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
