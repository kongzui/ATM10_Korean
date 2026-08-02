#!/usr/bin/env python3
"""Oritech 전용·연관 FTB Quests 표시 키를 영어 원문 기준으로 전부 재검수한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path

import ars_family
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT


WORK_ROOT = PROJECT_ROOT / "working/oritech"
QUEST_ROOT = WORK_ROOT / "quests"
CHAPTERS = ("oritech", "related")
CACHE_FILE = PROJECT_ROOT / "temp/oritech_quest_candidate_cache.json"
CANDIDATE_FILE = WORK_ROOT / "quest_auto_candidates.json"

MANUAL_TRANSLATIONS = {
    (
        "To use drone ports, place down 2 of them and &asneak right-click&r your "
        "&5target designator&r on one of them to store its location. Open the UI of "
        "the second one and place your &5target designator&r in it."
    ): (
        "드론 포트를 사용하려면 2개를 설치하세요. 한 포트에 &5표적 지정기&r를 들고 "
        "&a웅크린 채 우클릭&r하여 위치를 저장한 다음, 다른 포트의 UI를 열고 그 안에 "
        "&5표적 지정기&r를 넣으세요."
    ),
}

KEY_OVERRIDES: dict[tuple[str, str], object] = {
    ("oritech", "quest.01C0DC225CB25A0C.title"): "몹 공격",
    ("oritech", "quest.0C9F9196CA49FF8D.quest_subtitle"): (
        "니켈 광석을 찾아 여정을 시작하세요"
    ),
    ("oritech", "quest.0EC0F93FA4B4BE49.quest_desc"): [
        "이 기계는 &5엔더릭 레이저&r로만 전력을 공급할 수 있으며, 고급 아이템 제작에 "
        "사용합니다."
    ],
    ("oritech", "quest.0EC0F93FA4B4BE49.quest_subtitle"): "최종 제작 기계",
    ("oritech", "quest.114EACA9B32B32FB.quest_subtitle"): "방법은 알고 있죠...",
    ("oritech", "quest.161EDD68FF1A7F1B.quest_subtitle"): "용암으로 작동합니다",
    ("oritech", "quest.1630CFBFB562C43B.quest_subtitle"): (
        "액체 연료를 사용해 전력을 생산합니다"
    ),
    ("oritech", "quest.175509632CBF8631.quest_desc"): [
        "모든 분쇄 조합법의 생산량을 늘립니다."
    ],
    ("oritech", "quest.1831B35A3239B583.quest_subtitle"): (
        "여러 조합법을 한 번에 처리합니다"
    ),
    ("oritech", "quest.1B2BD489D5173B40.quest_subtitle"): ("얻는 방법은 아주 많습니다"),
    ("oritech", "quest.1D9A00C81C2A97F0.quest_subtitle"): "별거 없네요",
    ("oritech", "quest.1DBF1D4061518B0B.quest_subtitle"): "하나를 여러 개로",
    ("oritech", "quest.1F139091C1B4E50B.quest_subtitle"): "평범한 회로",
    ("oritech", "quest.208F759905CF7744.quest_desc"): [
        "드론 포트는 상당히 빠르지만 작동하려면 두 포트 사이가 최소 &450블록&r "
        "떨어져 있어야 합니다.",
        "",
        "드론 포트를 사용하려면 2개를 설치하세요. 한 포트에 &5표적 지정기&r를 들고 "
        "&a웅크린 채 우클릭&r하여 위치를 저장한 다음, 다른 포트의 UI를 열고 그 안에 "
        "&5표적 지정기&r를 넣으세요.",
        "",
        "&5표적 지정기&r를 넣은 드론 포트에 아이템이 들어오면 드론을 출발시켜 "
        "아이템을 운반합니다. ",
    ],
    ("oritech", "quest.208F759905CF7744.quest_subtitle"): ("그래요, 드론도 있습니다"),
    ("oritech", "quest.24310BEACE75749D.quest_desc"): [
        "애드온은 &5Oritech&r 기계의 업그레이드이자 모듈로 작동합니다. ",
        "",
        "애드온은 플러그처럼 생긴 슬롯에 장착합니다. 장착할 수 있는 애드온 수는 "
        "사용 중인 기계 핵에 따라 달라집니다.",
        "",
        "",
        "{image:atm:textures/questpics/oritech/ori-addon-slot.png width:50 height:100 align:left}",
        "",
        "애드온은 기계에 추가 기능도 부여합니다. 일부 조합법을 작동시키려면 특정 "
        "애드온을 장착해야 합니다.",
    ],
    ("oritech", "quest.24310BEACE75749D.quest_subtitle"): "쓸모 있게 만들기",
    ("oritech", "quest.310FA9380CB3E0BB.quest_subtitle"): (
        "원심 분리기에 유체를 넣을 수 있습니다"
    ),
    ("oritech", "quest.334AB2ED426108C7.quest_subtitle"): (
        "뭐라고 부르든, 갈아 버립니다"
    ),
    ("oritech", "quest.35BC118040E7428F.quest_desc"): [
        "엔더릭 레이저는 여러 용도로 사용할 수 있습니다:",
        "",
        "1. 멋진 모습으로 에너지를 전송합니다.",
        "2. 재료를 변환합니다.",
        "3. 블록을 파괴합니다.",
        "4. 자수정 성장을 촉진합니다.",
    ],
    ("oritech", "quest.38F4448F9603FE68.quest_subtitle"): (
        "위대함까지 2단계 남았습니다"
    ),
    ("oritech", "quest.3DD27DED791C6A0B.quest_desc"): [
        "&5Oritech&r에서 광석을 처리하려면 &6유체 애드온&r을 장착한 "
        "&a원심 분리기&r와 &a분쇄기&r 또는 &6파편 단조기&r가 필요합니다."
    ],
    ("oritech", "quest.3EB34CC8A3B0DB3C.quest_subtitle"): (
        "햄스터 먹이로는 쓸 수 없습니다"
    ),
    ("oritech", "quest.418E0A23EC74F320.quest_desc"): [
        "앞으로의 작업에 꼭 필요한 기계입니다."
    ],
    ("oritech", "quest.418E0A23EC74F320.quest_subtitle"): "빙글빙글 돌려요...",
    ("oritech", "quest.46EFCAE81C09368A.quest_desc"): [
        "기계 핵은 &9Oritech&r 기계의 기반입니다. 기계에 기계 핵을 들고 우클릭하여 "
        "건설하세요.",
        "",
        "기계의 속도나 효율에는 직접 영향을 주지 않고, 장착 가능한 애드온 수만 "
        "결정합니다.",
    ],
    ("oritech", "quest.46EFCAE81C09368A.quest_subtitle"): (
        "모든 기계에 기계 핵을 사용합니다"
    ),
    ("oritech", "quest.46EFCAE81C09368A.title"): "기계 핵",
    ("oritech", "quest.49D03933633D6A45.quest_subtitle"): "AI입니다",
    ("oritech", "quest.4CFA7EE8174E3FD8.quest_subtitle"): "에너지 입력 속도 증가",
    ("oritech", "quest.4EAD06B0B3AD7D6E.quest_subtitle"): (
        "가공 전 광석을 파편으로 만듭니다"
    ),
    ("oritech", "quest.4ED29ACF4A699E1B.quest_subtitle"): "더더 좋습니다",
    ("oritech", "quest.4F89C04CEBF812F9.title"): "주괴",
    ("oritech", "quest.50243E5CF1B156ED.quest_desc"): [
        "&5플루토늄 가루&r를 얻으려면 파편 단조기에서 &a가공 전 우라늄&r을 "
        "분해해 &5작은 플루토늄 가루&r를 얻거나, &a우라나이트 수정&r에 "
        "&5엔더릭 레이저&r를 발사해야 합니다."
    ],
    ("oritech", "quest.5189D72ED3808DC6.quest_desc"): [
        "자수정 군집에 표적 지정기를 들고 &a웅크린 채 우클릭&r한 다음, 레이저를 "
        "&a웅크린 채 우클릭&r하여 표적을 설정하세요.",
        "",
        "이 작은 수정은 보기만 좋은 것이 아닙니다. 에너지를 저장하며 더 복잡한 "
        "기계를 만드는 데 사용됩니다.",
    ],
    ("oritech", "quest.53D5A6F210DF199C.quest_subtitle"): (
        "10k RF/t를 안정적으로 전송합니다"
    ),
    ("oritech", "quest.53D5A6F210DF199C.title"): "에너지 전송",
    ("oritech", "quest.58819CE09A648A43.quest_subtitle"): (
        "대부분의 기계를 만드는 데 사용합니다"
    ),
    ("oritech", "quest.58819CE09A648A43.title"): "기본 기계 부품",
    ("oritech", "quest.5932B5AD48F6AB74.quest_desc"): [
        "&5파이프 증폭기&r에 전력을 공급해 &2Oritech&r 파이프의 추출 속도를 "
        "높이세요."
    ],
    ("oritech", "quest.5E9AF8BB2C67DCCE.quest_subtitle"): (
        "유체를 운송하는 방법은 다양합니다"
    ),
    ("oritech", "quest.5E9AF8BB2C67DCCE.title"): "유체 운송",
    ("oritech", "quest.6134991F25B25B42.quest_desc"): [
        "&l조립기&r는 &a새로운 아이템&r을 제작할 뿐 아니라 일부 아이템의 "
        "생산량도 늘립니다."
    ],
    ("oritech", "quest.6134991F25B25B42.quest_subtitle"): "제작기 그 이상",
    ("oritech", "quest.6134991F25B25B42.title"): "조립하기",
    ("oritech", "quest.6539582429A70EE8.quest_subtitle"): (
        "Oritech는 이 팩의 대부분의 발전원에서 생산한 전력을 사용할 수 있습니다"
    ),
    ("oritech", "quest.6EBFA16D212A7B22.quest_subtitle"): "최고 중의 최고",
    ("oritech", "quest.7084E47579D62B52.quest_subtitle"): ("더 많은 일을 하는 회로"),
    ("oritech", "quest.72E7AE66F2A7C4C4.quest_subtitle"): "기계에서 유체 사용",
    ("oritech", "quest.7937DE650CABC1FF.quest_subtitle"): "화로 연료로 작동",
    ("oritech", "quest.7CBAD1047B087803.quest_desc"): [
        "이제 &e덩어리&r를 얻었습니다. 원심 분리기에 유체 애드온을 장착하면 "
        "&a황산&r을 넣을 수 있습니다. &e덩어리&r를 황산으로 처리하면 보석을 "
        "얻습니다.",
        "",
        "생산량이 줄어도 괜찮다면 &9물&r을 대신 사용할 수 있습니다.",
        "",
        "&l&o&n참고&r",
        "",
        "현재 일부 조합법은 문제가 있어 가루나 조각을 출력합니다.",
    ],
    ("oritech", "quest.7CBAD1047B087803.title"): "보석으로 회전",
    ("oritech", "quest.7D2F41DD9774DDA7.title"): "아이템 운송",
    ("oritech", "task.400E42F53FDE783C.title"): "주괴",
    ("related", "quest.28DB59B20109D0D4.quest_desc"): [
        "&6&lOritech&r는 수많은 &l멀티블록 기계&r, 위험한 블록과 화려한 이름의 "
        "블록으로 유명한 기술 모드입니다! \n\n여러 기계와 다양한 합금·재료, "
        "그리고 많은 시간이 필요합니다. \n\n시작하려면 &6자기 코일&r이 필요합니다. "
        "행운을 빕니다!"
    ],
    ("related", "quest.28DB59B20109D0D4.title"): "&6&lOritech",
    ("related", "quest.486B5A605D79EA10.quest_desc"): [
        "&c맨해튼 &a모듈&r은 복잡한 조합법입니다. &cTNT&r, &d플루토늄 펠릿&r과 "
        "&5하이젠베르크 보정기&r가 필요합니다. 그래도 2/3만 복잡하다고 할 수 "
        "있겠네요. \n\n&d플루토늄 펠릿&r을 만들려면 먼저 &5자수정 조각&r에 "
        "에너지를 주입하세요. 그러면 &5플럭사이트&r가 만들어지며, 이를 "
        "&l&5입자 가속기&r에서 &a우라늄 가루&r와 함께 사용해 &d플루토늄 가루&r를 "
        "만들 수 있습니다. \n\n&d플루토늄 가루&r를 플라스틱판과 주괴로 조합하면 "
        "&d펠릿&r이 됩니다. \n\n&5하이젠베르크 보정기&r에는 사용할 수 있는 조합법이 "
        "2가지 있습니다. 둘 다 &c&l원자 단조기&r에서 &b아다만트 주괴&r를 "
        "&c각인&r해야 합니다. \n\n1. &b불경한 지능체&r를 사용하는 방법입니다. "
        "&2두비오스 용기&r에 &5기묘한 물질&r을 채워 만듭니다. &5기묘한 물질&r은 "
        "추가 반응실 2개를 장착한 &d&l유체 정유기&r에서 &c용암&r과 "
        "&3엔더릭 화합물&r을 처리해 얻습니다. \n\n2. &e슈퍼 AI 칩&r을 사용하는 "
        "방법입니다. &2&lMinecraft&r에 AI라니요? 이를 제작하려면 &c&l원자 단조기&r의 "
        "&c각인&r 조합법 단계를 따라야 하며, &8실리콘&r이 아주 많이 필요합니다."
    ],
}

TEXT_REPLACEMENTS = (
    ("오리테크", "Oritech"),
    ("오리텍", "Oritech"),
    ("엔더릭 레이저", "엔더릭 레이저"),
    ("엔더릭 레이저", "엔더릭 레이저"),
    ("파쇄기", "분쇄기"),
    ("분쇄기", "분쇄기"),
    ("조각 대장간", "파편 단조기"),
    ("파편 단조", "파편 단조기"),
    ("원자 대장간", "원자 단조기"),
    ("기계 코어", "기계 핵"),
    ("머신 코어", "기계 핵"),
    ("유체 추가 기능", "유체 애드온"),
    ("추가 기능", "애드온"),
    ("애드온", "애드온"),
    ("플럭스사이트", "플럭사이트"),
    ("프로메테움", "프로메튬"),
    ("프로메티움", "프로메튬"),
    ("우라나이트 크리스탈", "우라나이트 수정"),
    ("플루토늄 먼지", "플루토늄 가루"),
    ("원시 우라늄", "가공 전 우라늄"),
    ("원시 니켈", "가공 전 니켈"),
    ("인벤토리", "인벤토리"),
    ("재고", "인벤토리"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("마우스 오른쪽 버튼 클릭", "우클릭"),
    ("마우스 오른쪽 클릭", "우클릭"),
    ("오른쪽 클릭", "우클릭"),
)


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


def scalar_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(scalar_strings(item))
        return result
    raise TypeError(f"지원하지 않는 퀘스트 값: {type(value).__name__}")


def translated_scalar(source: str, cache: dict[str, object]) -> str:
    if not source or family_goal.is_allowed_original(source):
        return source
    translated = MANUAL_TRANSLATIONS.get(source, cache.get(source))
    if not isinstance(translated, str):
        raise KeyError(f"자동 번역 후보가 없습니다: {source}")
    for old, new in TEXT_REPLACEMENTS:
        translated = translated.replace(old, new)
    translated = re.sub(r"[ \t]+([,.!?])", r"\1", translated)
    return translated


def translated_value(value: object, cache: dict[str, object]) -> object:
    if isinstance(value, str):
        return translated_scalar(value, cache)
    if isinstance(value, list):
        return [translated_value(item, cache) for item in value]
    raise TypeError(f"지원하지 않는 퀘스트 값: {type(value).__name__}")


def preserve_literal_breaks(value: object) -> object:
    """검수 문자열의 실제 줄바꿈을 FTB Quests의 문자 ``\\n``으로 바꾼다."""
    if isinstance(value, str):
        return value.replace("\n", "\\n")
    if isinstance(value, list):
        return [preserve_literal_breaks(item) for item in value]
    return value


def candidate() -> dict[str, object]:
    """전용·연관 퀘스트 모든 표시 문자열의 보호된 자동 후보를 만든다."""
    english_by_chapter = {
        chapter: load_json(QUEST_ROOT / chapter / "en_us.json") for chapter in CHAPTERS
    }
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests = {
        source
        for english in english_by_chapter.values()
        for value in english.values()
        for source in scalar_strings(value)
        if source
        and source not in MANUAL_TRANSLATIONS
        and not family_goal.is_allowed_original(source)
        and not isinstance(cache.get(source), str)
    }
    failures: list[str] = []
    if requests:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(ars_family.request_translation, source): source
                for source in sorted(requests)
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("자동 번역 후보 생성 실패:\n" + "\n".join(failures))

    candidates = {
        chapter: {key: translated_value(value, cache) for key, value in english.items()}
        for chapter, english in english_by_chapter.items()
    }
    write_json(CANDIDATE_FILE, candidates)
    report = {
        "keys": sum(len(value) for value in english_by_chapter.values()),
        "candidate_keys": sum(len(value) for value in candidates.values()),
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "quest_auto_candidate_report.json", report)
    return report


def normalize() -> dict[str, object]:
    """현재 영어 표시 키 전부를 검수 후보로 교체한다."""
    candidates = load_json(CANDIDATE_FILE)
    reviewed = 0
    changed = 0
    for chapter in CHAPTERS:
        root = QUEST_ROOT / chapter
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        chapter_candidates = candidates[chapter]
        if not isinstance(chapter_candidates, dict):
            raise TypeError(f"챕터 후보가 객체가 아닙니다: {chapter}")
        for key, source in english.items():
            translated = preserve_literal_breaks(
                KEY_OVERRIDES.get((chapter, key), chapter_candidates[key])
            )
            errors = family_goal.validate_value(key, source, translated)
            if errors:
                raise ValueError("; ".join(errors))
            if korean[key] != translated:
                korean[key] = translated
                changed += 1
            reviewed += 1
        write_json(root / "ko_kr.json", korean)
    report = {
        "keys_reviewed": reviewed,
        "changed": changed,
        "review_status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "quest_normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    """키·자료형·자리표시자·서식 코드와 미번역을 검사한다."""
    errors: list[str] = []
    untranslated: list[str] = []
    reviewed = 0
    for chapter in CHAPTERS:
        root = QUEST_ROOT / chapter
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        if english.keys() != korean.keys():
            errors.append(f"키 불일치: {chapter}")
        for key, source in english.items():
            target = korean.get(key)
            errors.extend(family_goal.validate_value(key, source, target))
            if (
                source == target
                and (chapter, key) not in KEY_OVERRIDES
                and not family_goal.is_allowed_original(str(source))
            ):
                untranslated.append(f"{chapter}:{key}")
            reviewed += 1
    if untranslated:
        errors.append(f"미번역 키: {untranslated[:30]}")
    report = {
        "keys_reviewed": reviewed,
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
        report = candidate()
        status = 0
    elif args.command == "normalize":
        report = normalize()
        status = 0
    else:
        report, status = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
