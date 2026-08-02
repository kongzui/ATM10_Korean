#!/usr/bin/env python3
"""Actually Additions 관련 FTB Quests 표시 문자열 6키를 전부 재검수한다."""

from __future__ import annotations

import argparse
import json

import ars_family
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT


QUEST_ROOT = PROJECT_ROOT / "working/actually_additions/quests/related"

REVIEWED: dict[str, object] = {
    "quest.3D755073C56274BE.quest_desc": [
        "원자 재구성기 앞에 렌즈 아이템을 떨어뜨리세요. 재구성기가 작동하면 "
        "&c색&e상&a의&b렌&3즈&r로 변환됩니다. \n\n그 앞에 "
        "&c색&e상&a의&b렌&3즈&r를 떨어뜨리고 작동시키면 &c폭발의 렌즈&r가 "
        "만들어집니다. \n\n&3필멸의 렌즈&r를 얻을 때까지 이 과정을 반복하세요."
    ],
    "quest.3D755073C56274BE.title": "&3필멸의 렌즈",
    "quest.635BA2C17458E9E6.quest_desc": [
        "이렇게 간단한 조합법으로도 꽤 유용한 기계를 얻을 수 있습니다! \n\n"
        "설치 방향에 따라 발사기처럼 조준 방향이 달라지니 알맞게 놓고, 에너지를 "
        "공급한 뒤 &4레드스톤 횃불&r로 작동 방식을 설정하세요. \n\n비활성화 "
        "모드에서는 &4레드스톤 신호&r를 받으면 작동을 멈추고, 펄스 모드에서는 "
        "&4레드스톤 신호&r를 받을 때마다 한 번 작동합니다. \n\n여기서는 "
        "&6&l별&r 자동화가 목적이므로 너무 깊게 다루지 않고 렌즈부터 시작하겠습니다!"
    ],
    "quest.71B72958B9F80355.quest_desc": [
        "걱정하지 마세요. 이제부터는 아이템을 더 떨어뜨리지 않아도 됩니다! \n\n"
        "이제 제작만 하면 됩니다. &3필멸의 렌즈&r를 &b다이아몬드 검&r 및 "
        "&5날카로움 V 마법이 부여된 책&r과 조합해 살해의 렌즈를 만드세요. \n\n"
        "&5마법이 부여된 책&r은 &5&l룬 문자 마법 부여기&r에서 얻을 수 있으며, "
        "다른 퀘스트에서 자세히 배울 수 있습니다!"
    ],
    "quest.71B72958B9F80355.title": "&4살해의 렌즈",
    "quest.47043AF7D1FABC43.quest_desc": [
        "아이템의 마법 부여를 책으로 옮기는 방법은 다양합니다. 이 퀘스트에서는 그중 "
        "여러 방법을 소개합니다.\n\n&cSuper Factory Manager&r: 제가 떠올릴 수 있는 "
        "가장 저렴한 방법 중 하나로 &a경험치&r가 전혀 들지 않습니다. &5흑요석&r "
        "블록 위에 마법이 부여된 아이템과 책 여러 권을 떨어뜨린 뒤, 떨어지는 "
        "&8모루&r가 그 위에 착지하게 하세요.\n\n&b마법 해제대&r: 마법이 부여된 "
        "아이템을 왼쪽 칸에, 책을 가운데 칸에 넣으면 마법 부여가 책 형태로 오른쪽 "
        "칸에 나옵니다! &a경험치&r가 필요합니다.\n아이템 대신 마법이 부여된 책을 "
        "넣어 여러 마법 부여를 나눌 수도 있습니다.\n\n&6Draconic Evolution 마법 "
        "해제기&r: 마법이 부여된 아이템에서 원하는 마법 하나를 골라 책으로 옮길 수 "
        "있습니다. &a경험치&r가 필요합니다.",
        "{@pagebreak}",
        "&cEvilCraft 정화기와 Blook&r: &c피&r를 사용해 마법이 부여된 아이템의 "
        "마법을 &cBlook&r으로 옮깁니다.\n\n&5&lApothic Enchanting 고서&r: 모루에서 "
        "사용하면 마법이 부여된 아이템의 마법을 추출합니다.\n&8Scrapping 고서&r는 "
        "마법 부여 절반만 추출하고 아이템을 파괴합니다.\n&8Superior Scrapping "
        "고서&r는 모든 마법 부여를 추출하고 아이템을 파괴합니다.\n&8Extraction "
        "고서&r는 모든 마법 부여를 추출하면서 아이템을 보존합니다.\n이 고서에 "
        "마법을 주입하는 방법은 &5&lApothic Enchanting&r 챕터에서 확인하세요."
        "\n\n&bIndustrial Foregoing 마법 부여 추출기&r: 자동 마법 해제에 추천합니다. "
        "기계에 마법이 부여된 아이템과 책을 넣으면 아이템의 마법을 추출합니다. "
        "원한다면 마법을 &a정수&r로 바꿀 수도 있습니다.\n\n&8Corail Tombstone 마법 "
        "해제의 책&r: 장식 무덤에는 때때로 무덤 영혼이 떠돕니다. 보조 손에 책을, "
        "주손에 마법이 부여된 아이템을 들고 무덤 영혼을 우클릭하면 마법을 제거해 "
        "책으로 돌려받을 수 있습니다. 무덤이 조금 부패하니 주의하세요."
        "\n\n&5Actually Additions 마법 해제 렌즈&r: 원자 재구성기에 장착하는 렌즈입니다. "
        "재구성기가 내보내는 레이저 앞에 마법이 부여된 아이템과 책 한 권을 던지면 "
        "마법 하나를 아이템에서 책으로 분리합니다.",
    ],
}


def preserve_literal_breaks(value: object) -> object:
    """Python 문자열의 줄바꿈을 FTB Quests의 문자 그대로인 ``\\n``으로 바꾼다."""
    if isinstance(value, str):
        return value.replace("\n", "\\n")
    if isinstance(value, list):
        return [preserve_literal_breaks(item) for item in value]
    return value


def apply() -> dict[str, object]:
    """현재 영어 원문과 대조한 검수본을 작업 파일에 반영한다."""
    english = ars_family.load_json(QUEST_ROOT / "en_us.json")
    if english.keys() != REVIEWED.keys():
        missing = sorted(english.keys() - REVIEWED.keys())
        extra = sorted(REVIEWED.keys() - english.keys())
        raise KeyError(f"검수 키 불일치: missing={missing}, extra={extra}")
    reviewed = {key: preserve_literal_breaks(value) for key, value in REVIEWED.items()}
    ars_family.write_json(QUEST_ROOT / "ko_kr.json", reviewed)
    report = {
        "keys_reviewed": len(english),
        "project_candidates_re_reviewed": 5,
        "new_translations": 1,
        "status": "all_current_english_keys_reviewed",
    }
    ars_family.write_json(
        PROJECT_ROOT / "working/actually_additions/quest_normalization.json", report
    )
    return report


def verify() -> tuple[dict[str, object], int]:
    """키·자료형·자리표시자·서식 코드와 미번역을 검사한다."""
    english = ars_family.load_json(QUEST_ROOT / "en_us.json")
    korean = ars_family.load_json(QUEST_ROOT / "ko_kr.json")
    errors: list[str] = []
    if english.keys() != korean.keys():
        errors.append("영어와 한국어의 키가 다릅니다.")
    for key, source in english.items():
        target = korean.get(key)
        errors.extend(family_goal.validate_value(key, source, target))
        if source == target and source != "{@pagebreak}":
            errors.append(f"미번역 키: {key}")
    report = {
        "keys_reviewed": len(english),
        "untranslated": sum(1 for key in english if english[key] == korean.get(key)),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    ars_family.write_json(
        PROJECT_ROOT / "working/actually_additions/quest_specialized_validation.json",
        report,
    )
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("apply", "verify"))
    args = parser.parse_args()
    if args.command == "apply":
        report = apply()
        status = 0
    else:
        report, status = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
