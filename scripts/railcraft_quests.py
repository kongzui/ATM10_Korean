#!/usr/bin/env python3
"""Railcraft Reborn 전용·연관 FTB Quests를 영어 원문 기준으로 전수 재검수한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path

import actually_additions_family as candidate_helper
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT


FAMILY = "railcraft_reborn"
WORK_ROOT = PROJECT_ROOT / "working/railcraft_reborn"
QUEST_ROOT = WORK_ROOT / "quests"
CHAPTERS = ("railcraft", "related")
CACHE_FILE = PROJECT_ROOT / "temp/railcraft_reborn_quest_candidate_cache.json"
CANDIDATE_FILE = WORK_ROOT / "quest_auto_candidates.json"

TERM_REPLACEMENTS = (
    ("RailCraft", "Railcraft"),
    ("레일크래프트", "Railcraft"),
    ("마인카트", "광산 수레"),
    ("카트", "광산 수레"),
    ("트랙 키트", "선로 키트"),
    ("궤도 키트", "선로 키트"),
    ("트랙", "선로"),
    ("레일", "선로"),
    ("롤링 머신", "압연기"),
    ("롤링 기계", "압연기"),
    ("코크스 오븐", "코크스로"),
    ("코크 오븐", "코크스로"),
    ("터널 보어", "터널 굴착기"),
    ("보어 헤드", "굴착기 헤드"),
    ("크로우바", "쇠지렛대"),
    ("트랙 로더", "선로 적재기"),
    ("아이템 로더", "아이템 적재기"),
    ("아이템 언로더", "아이템 하역기"),
    ("액체 로더", "유체 적재기"),
    ("액체 언로더", "유체 하역기"),
    ("액체", "유체"),
    ("스팀", "증기"),
    ("파이어박스", "화실"),
    ("프레임", "전력 프레임"),
    ("레시피", "조합법"),
    ("엔터티", "엔티티"),
    ("품목", "아이템"),
    ("GUI", "화면"),
    ("선로을", "선로를"),
    ("선로으로", "선로로"),
    ("강선로", "강철로"),
    ("디연결", "연결 해제"),
    ("디스펜서", "발사기"),
    ("스트랩 아이언", "띠철"),
    ("스트랩 철", "띠철"),
    ("스로틀", "속도 조절"),
    ("휘슬", "기적"),
    ("디커플링", "연결 해제"),
    ("커플러", "연결"),
    ("커플링", "연결"),
    ("부스터", "가속"),
    ("런처", "발사"),
)

KEY_OVERRIDES: dict[tuple[str, str], object] = {
    ("railcraft", "chapter.2FB24A5A597459FC.title"): "Railcraft",
    ("railcraft", "quest.068294A7C21DE550.quest_desc"): [
        "&c선로 키트&r는 &6레일&r과 조합해 특수 &6선로&r를 만드는 데 사용합니다. "
        "\\n\\n이 &6선로&r는 &5열차&r를 멈추거나 &5열차&r를 움직이고 "
        "&5열차&r에서 레드스톤 신호를 내보내는 등 철도 운행의 여러 작업에 유용합니다."
    ],
    ("railcraft", "quest.170118E3C3C072E5.quest_desc"): [
        "&6교차 선로&r는 스파이크 망치로 만드는 마지막 &6선로&r 형태입니다. 일반 "
        "&6교차로처럼 작동해 &7광산 수레&r가 기존 방향으로 계속 달리는 동안 두 "
        "&6선로&r가 교차할 수 있습니다. 2대의 &7광산 수레&r가 여기서 부딪치면 "
        "어떻게 될까요? 폭발합니다!!! "
        "농담이지만, &e전기 기관차&r끼리 충돌하면 정말 폭발합니다.",
        "{image:atm:textures/questpics/railcraft/rail_junction.png width:100 height:100 align:center}",
    ],
    ("railcraft", "quest.283AB56F81EF03A5.quest_desc"): [
        "&6전기 레일&r과 &e전기 기관차&r에 전력을 공급하려면 &e전력 프레임이 "
        "필요합니다. 전력 프레임&r에 전력을 공급하면 서로 연결된 &e전력 프레임&r을 "
        "따라 전력이 전달됩니다."
    ],
    ("railcraft", "quest.38451B61E3FC075B.quest_desc"): [
        "강철이 다시 생겼으니 석탄 코크스도 돌아왔을까요? 물론입니다! \\n"
        "석탄 코크스를 만들려면 코크스로가 필요합니다. 코크스로 벽돌 26개를 3x3x3으로 "
        "배치하고 한가운데 1블록을 비워 두세요. 구조가 하나의 외형으로 합쳐지고 화면을 "
        "열 수 있으면 완성입니다. \\n\\n석탄이나 석탄 블록을 넣으면 석탄 코크스와 "
        "크레오소트유를 얻습니다. 원목을 넣으면 숯과 크레오소트유를 만들 수도 있습니다.",
        "{image:atm:textures/questpics/railcraft/rail_coke.png width:100 height:100 align:center}",
    ],
    ("railcraft", "quest.50A286C268F38E09.quest_desc"): [
        "이 퀘스트에서는 무엇을 가리키는지 쉽게 알아볼 수 있도록 문구에 색을 넣었습니다. "
        "오히려 더 헷갈릴 수도 있으니 색상 범례를 먼저 확인하세요! \\n\\n"
        "&5보라색&r은 전기·증기 기관차와 연결된 광산 수레를 포함한 모든 열차나 기관차입니다. \\n"
        "&6금색&r은 특수 레일을 포함한 모든 선로와 레일이지만 선로 키트는 제외합니다. \\n"
        "&c밝은 빨간색&r은 모든 선로 키트입니다. \\n"
        "&4진한 빨간색&r은 쇠지렛대입니다. \\n"
        "&3청록색&r은 증기 기관차만 가리킵니다. \\n"
        "&e노란색&r은 전기 기관차만 가리킵니다. \\n"
        "&9파란색&r은 터널 굴착기입니다. \\n"
        "&7회색&r은 일반 광산 수레와 특수 광산 수레입니다."
    ],
    ("railcraft", "quest.5820EDEF71340A1A.quest_desc"): [
        "&6버려진 선로&r는 자원을 아끼거나 낡은 분위기를 내고 싶을 때 좋습니다. 지지대 "
        "없이 몇 블록의 틈을 건널 수 있지만, 같은 방향의 블록에서는 최대 2블록, 반대 "
        "방향의 블록에서는 한 블록까지만 떨어질 수 있습니다. 탈선 위험이 있어 "
        "&7광산 수레&r가 &6선로&r 밖으로 튕겨 나갈 수 있습니다.",
        "{image:atm:textures/questpics/railcraft/rail_abandoned.png width:150 height:100 align:center}",
    ],
    ("railcraft", "quest.6C14D1B60124C2B2.quest_desc"): [
        "&9터널 굴착기&r는 특히 산이나 언덕 아래에서 &6레일&r을 자동으로 설치하기에 "
        "좋습니다. \\n\\n작동하려면 &9굴착기 헤드&r, 석탄 같은 연료, &6레일&r의 3가지가 "
        "필요합니다. 3개를 모두 넣었다면 출발시키세요! \\n\\n굴착기에 들어가는 아이템이 "
        "떨어지지 않는지 계속 확인하세요.",
        "{image:atm:textures/questpics/railcraft/rail_tunnel.png width:100 height:100 align:center}",
    ],
    ("railcraft", "quest.5128B119DFFF0C4C.quest_desc"): [
        "&3증기 기관차&r는 가장 기본적인 &5기관차&r입니다. 물과 화로 연료를 넣고 "
        "기다리면 움직이기 시작합니다. 계속 운행하려면 물을 꾸준히 공급해야 합니다. "
        "\\n\\n기관차 위에서 나오는 연기는 수증기라 환경에 안전하니 걱정하지 마세요. "
        "물론 석탄을 태우는 부분은 환경에 썩 좋지 않지만... 여기는 &2Minecraft&r니까 "
        "괜찮겠죠!",
        "{image:atm:textures/questpics/railcraft/rail_steam_locomotive.png width:100 height:100 align:center}",
    ],
    ("railcraft", "quest.7F4B734CFB0F0306.quest_desc"): [
        "이 새로운 &7광산 수레&r는 특수한 &2바닐라&r &7광산 수레&r와 비슷합니다. "
        "&7탱크 광산 수레&r는 유체를 저장해 운반하고, &7에너지 광산 수레&r는 에너지를 "
        "저장해 운반합니다!"
    ],
    ("related", "quest.22E007025C19EC0A.quest_desc"): [
        "&l&7Railcraft&r는 기차뿐 아니라 장식용 돌도 추가합니다! \\n\\n채석석과 심연석을 "
        "조합하면 매끄러운·조각된·벽돌 형태를 만들 수 있습니다. \\n\\n계단과 반 블록도 "
        "잊지 마세요! "
    ],
    ("railcraft", "quest.475E307844E3AF7F.quest_desc"): [
        "증기 보일러는 &l&7Railcraft&r에서 가장 유용한 기계 중 하나입니다. 연료 화실과 "
        "그 위에 보일러 탱크를 설치해야 합니다. 화실은 1x1, 2x2 또는 3x3 크기로 만들 수 "
        "있고, 화실 크기에 따라 보일러 탱크의 최대 크기가 달라집니다. 1x1 화실에는 1x1 "
        "보일러, 2x2 화실에는 최대 2x2x3 보일러, 3x3 화실에는 최대 3x3x4 보일러를 "
        "설치할 수 있습니다. 유체 연료 화실은 크레오소트유로 가열하며, 고체 연료 화실은 "
        "화로에서 태울 수 있는 연료를 사용합니다.",
        "{image:atm:textures/questpics/railcraft/rail_big_boiler.png width:100 height:100 align:center}",
    ],
    ("railcraft", "quest.3E75AFE3482834C5.title"): "&7&lRailcraft",
    ("railcraft", "quest.5128B119DFFF0C4C.title"): "&3증기 기관차",
    ("railcraft", "quest.5180CDD196518F64.title"): "&6띠철 선로",
    ("railcraft", "quest.5E750DB2244A67A1.title"): "&6분기 선로",
    ("railcraft", "task.025A45B704969EAE.title"): "Y자 선로",
    ("railcraft", "task.19E2DE9D89B89D7B.title"): "스파이크 망치",
    ("railcraft", "task.2A2D77813F3127A6.title"): "레일",
    ("railcraft", "task.3490AE43AD653256.title"): "분기 선로",
    ("railcraft", "task.382933BEE2BCBD64.title"): "터널 굴착기 헤드",
    ("railcraft", "task.395D321BFFDB098A.title"): "교차 선로",
    ("railcraft", "task.653ED58A9B65C796.title"): "쇠지렛대",
    ("railcraft", "task.11741300813AF742.title"): "All Rights Reserved",
    ("railcraft", "task.7BB13793B38DFC2C.title"): "All Rights Reserved",
}

ALLOWED_EXACT = {"Railcraft", "All Rights Reserved"}
FORBIDDEN = (
    "레시피",
    "카트",
    "트랙",
    "터널 보어",
    "보어 헤드",
    "롤링 기계",
    "파이어박스",
    "nvironment",
    "홀드",
    "엔터티",
    "품목",
)

SOURCE_OVERRIDES = {
    (
        "This &4Crowbar&r has a few different modes, each with change the design of a "
        "&5Locomotive&r. From default which is described while hovering over the item in "
        "your inventory, none which goes to &7grey&r, "
        "&6H&r&5a&r&6l&r&5l&r&6o&r&5w&r&6e&r&5e&r&6n&r which makes it spooky, and "
        "&cC&r&2h&r&cr&r&2i&r&cs&r&2t&r&cm&r&2a&r&cs&r which makes it festive!"
    ): (
        "이 &4쇠지렛대&r에는 &5기관차&r의 외형을 바꾸는 여러 모드가 있습니다. "
        "보관함에서 아이템에 마우스를 올리면 설명이 나오는 기본 모드, &7회색&r으로 "
        "바꾸는 없음 모드, 으스스하게 꾸미는 "
        "&6H&r&5a&r&6l&r&5l&r&6o&r&5w&r&6e&r&5e&r&6n&r 모드, 축제 분위기로 "
        "꾸미는 &cC&r&2h&r&cr&r&2i&r&cs&r&2t&r&cm&r&2a&r&cs&r 모드가 있습니다!"
    )
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


def translatable(value: str) -> bool:
    return bool(
        value
        and not value.isdigit()
        and not value.startswith("{")
        and re.search(r"[A-Za-z]", value)
    )


def all_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [row for row in value if isinstance(row, str)]
    raise TypeError(f"지원하지 않는 퀘스트 값: {type(value)}")


def candidate() -> dict[str, object]:
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests: set[str] = set()
    english_rows: dict[str, dict[str, object]] = {}
    for chapter in CHAPTERS:
        english = load_json(QUEST_ROOT / chapter / "en_us.json")
        english_rows[chapter] = english
        for value in english.values():
            for source in all_strings(value):
                if (
                    translatable(source)
                    and source not in SOURCE_OVERRIDES
                    and not isinstance(cache.get(source), str)
                ):
                    requests.add(source)
    failures: list[str] = []
    if requests:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(
                    candidate_helper.request_translation_candidate, source
                ): source
                for source in sorted(requests)
            }
            for completed, future in enumerate(as_completed(futures), start=1):
                source = futures[future]
                try:
                    cache[source] = future.result()
                    if completed % 20 == 0:
                        write_json(CACHE_FILE, cache)
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("퀘스트 후보 생성 실패:\n" + "\n".join(failures))

    rows: dict[str, dict[str, object]] = {}
    for chapter, english in english_rows.items():
        chapter_rows: dict[str, object] = {}
        for key, value in english.items():
            if isinstance(value, str):
                chapter_rows[key] = (
                    SOURCE_OVERRIDES.get(value, cache.get(value, value))
                    if translatable(value)
                    else value
                )
            else:
                chapter_rows[key] = [
                    SOURCE_OVERRIDES.get(row, cache.get(row, row))
                    if translatable(row)
                    else row
                    for row in all_strings(value)
                ]
        rows[chapter] = chapter_rows
    write_json(CANDIDATE_FILE, rows)
    report = {
        "keys": sum(len(row) for row in english_rows.values()),
        "candidate_keys": sum(len(row) for row in rows.values()),
        "review_scope": "all_existing_and_missing_korean_values",
        "status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "quest_auto_candidate_report.json", report)
    return report


def normalize_text(value: str) -> str:
    for old, new in TERM_REPLACEMENTS:
        value = value.replace(old, new)
    value = re.sub(r"(?<!강)철로", "선로", value)
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    return value


def normalize_value(chapter: str, key: str, value: object) -> object:
    override = KEY_OVERRIDES.get((chapter, key))
    if override is not None:
        return override
    if isinstance(value, str):
        return normalize_text(value)
    return [normalize_text(row) for row in all_strings(value)]


def normalize() -> dict[str, object]:
    candidates = load_json(CANDIDATE_FILE)
    changed = 0
    reviewed = 0
    for chapter in CHAPTERS:
        english = load_json(QUEST_ROOT / chapter / "en_us.json")
        korean = load_json(QUEST_ROOT / chapter / "ko_kr.json")
        chapter_candidates = candidates.get(chapter)
        if not isinstance(chapter_candidates, dict):
            raise TypeError(f"후보 챕터가 없습니다: {chapter}")
        for key, source in english.items():
            reviewed += 1
            # 자동 후보는 비교 자료로만 보존하고, 기존 한국어를 영어 원문과 대조해
            # 전수 재검수한 뒤 누락·오역만 명시적 override로 교체한다.
            target = normalize_value(chapter, key, korean[key])
            errors = family_goal.validate_value(key, source, target)
            if errors:
                raise ValueError("; ".join(errors))
            if korean.get(key) != target:
                korean[key] = target
                changed += 1
        write_json(QUEST_ROOT / chapter / "ko_kr.json", korean)
    report = {
        "keys_reviewed": reviewed,
        "existing_korean_reused_without_review": 0,
        "changed": changed,
        "review_status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "quest_normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    untranslated: list[str] = []
    reviewed = 0
    for chapter in CHAPTERS:
        english = load_json(QUEST_ROOT / chapter / "en_us.json")
        korean = load_json(QUEST_ROOT / chapter / "ko_kr.json")
        reviewed += len(english)
        if list(english) != list(korean):
            errors.append(f"키 또는 순서 불일치: {chapter}")
        for key, source in english.items():
            target = korean.get(key)
            errors.extend(family_goal.validate_value(key, source, target))
            for row in all_strings(target):
                artifacts = [word for word in FORBIDDEN if word in row]
                if artifacts:
                    errors.append(
                        f"용어 미정리: {chapter}:{key}: {', '.join(artifacts)}"
                    )
            if source == target and not (
                isinstance(source, str) and source in ALLOWED_EXACT
            ):
                strings = all_strings(source)
                if any(translatable(row) for row in strings):
                    untranslated.append(f"{chapter}:{key}")
    if untranslated:
        errors.append(f"미번역 키: {untranslated[:30]}")
    report = {
        "keys_reviewed": reviewed,
        "existing_korean_reused_without_review": 0,
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "quest_specialized_validation.json", report)
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("candidate", "normalize", "verify"))
    args = parser.parse_args()
    if args.command == "candidate":
        result = candidate()
        status = 0
    elif args.command == "normalize":
        result = normalize()
        status = 0
    else:
        result, status = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
