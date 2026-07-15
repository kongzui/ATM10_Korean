#!/usr/bin/env python3
"""EvilCraft 모드군의 언어와 FTB Quests 작업본을 검수한다."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from local_paths import PROJECT_ROOT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/evilcraft"

TERM_REPLACEMENTS = (
    ("복수심에 불타는 영혼", "복수령"),
    ("복수 정령", "복수령"),
    ("어둠의 힘 보석", "다크 파워 젬"),
    ("검은 힘 보석", "다크 파워 젬"),
    ("어둠의 보석", "다크 젬"),
    ("어둠 보석", "다크 젬"),
    ("검은 보석", "다크 젬"),
    ("분쇄된 다크 젬", "분쇄된 다크 젬"),
    ("어둠 광석", "다크 광석"),
    ("검은 광석", "다크 광석"),
    ("검은 블록", "다크 블록"),
    ("검은 피의 벽돌", "다크 블러드 벽돌"),
    ("검은 피 벽돌", "다크 블러드 벽돌"),
    ("검은 벽돌", "다크 벽돌"),
    ("어둠 막대기", "다크 막대기"),
    ("검은 막대기", "다크 막대기"),
    ("이블크래프트", "EvilCraft"),
    ("garmonbozia", "가몬보지아"),
    ("Garmonbozia", "가몬보지아"),
)

LANGUAGE_OVERRIDES: dict[str, dict[str, str]] = {
    "evilcraft": {
        "block.evilcraft.entangled_chalice": "얽힌 성배",
        "block.evilcraft.eternal_water.auto_output.enabled": "자동 출력 활성화",
        "block.evilcraft.eternal_water.auto_output.disabled": "자동 출력 비활성화",
        "item.evilcraft.garmonbozia": "가몬보지아",
        "key.categories.evilcraft": "EvilCraft",
        "broom.evilcraft.shiftinfo": "<Shift로 빗자루 정보 보기>",
        "broom.parts.evilcraft.shiftinfo": "<Shift로 빗자루 부품 정보 보기>",
        "broom.modifiers.evilcraft.shiftinfo": "<Shift로 빗자루 정보 보기>",
        "block.evilcraft.entangled_chalice.info": (
            "얽힌 성배의 내용물은 어디에서나 공유됩니다.\\n"
            "Shift + 우클릭으로 전방위 공급을 전환합니다."
        ),
        "item.evilcraft.kineticator.info": (
            "Shift + 우클릭으로 끌어당기기를 전환합니다.\\n"
            "우클릭으로 범위를 변경합니다."
        ),
        "item.evilcraft.kineticator_repelling.info": (
            "Shift + 우클릭으로 밀어내기를 전환합니다.\\n"
            "우클릭으로 범위를 변경합니다."
        ),
        "item.evilcraft.vengeance_ring.info": (
            "복수령을 끌어들이거나 소환할 수 있습니다.\\n"
            "Shift + 우클릭으로 강화를 전환합니다."
        ),
        "death.attack.evilcraft.broom.player": (
            "%1$s이(가) 빗자루를 탄 %s에게 치여 죽었습니다."
        ),
        "info_book.evilcraft.structure": "&o구조&r",
        "info_book.evilcraft.first_age.relics.enchantments.unusing.text": (
            "&l&n사용 방지&r&N아끼는 도구가 잠깐 한눈판 사이에 부서지는 일이 "
            "지겨워졌습니다. 그래서 내구도가 거의 다 된 도구를 사용할 수 없게 만드는 "
            "새로운 마법 부여를 고안했습니다. 덕분에 도구를 예전 모습으로 수리할 시간을 "
            "충분히 벌 수 있습니다."
        ),
        "info_book.evilcraft.second_age.evolved_blood_machinery."
        "sanguinary_pedestal.text1": (
            "몹을 절벽에서 밀어 떨어뜨리고 &4피&0를 추출하는 일이 지겨워져, 주변의 "
            "&1피 얼룩&0에서 &4피&0를 추출해 가까운 탱크에 넣는 장치를 만들었습니다. "
            "&1다크 파워 젬&0을 사용하면 이 &4피&0 추출의 &4피&0 효율을 높일 수 "
            "있습니다."
        ),
        "info_book.second_age.tools.rejuvenated_flesh.text": (
            "&1살점&0에 &1가몬보지아&0를 결합하면 무한한 식량 공급원으로 만들 수 "
            "있습니다. 다만 이것을 먹으려면 &4피&0를 공급해야 합니다."
        ),
        "info_book.evilcraft.first_age.new_world.dark_ore.text": (
            "이 세계에 온갖 자원이 있다는 사실은 오래전부터 알고 있었습니다... 하지만 "
            "오늘 새로운 광석을 발견했습니다. 어두운 빛을 띠어 귀중한 보석을 떠올리게 "
            "하지만, 그 안에서 아주 불길한 기운이 느껴집니다. 주로 &l레드스톤 광석&r과 "
            "비슷한 높이에서 발견되지만 때로는 훨씬 높은 곳에서도 나옵니다. 다크 젬을 "
            "얻으려면 최소한 철 곡괭이로 채굴해야 합니다. 행운이 부여된 도구로 채굴하면 "
            "기묘한 가루도 나오는 듯합니다. 곧 이 가루의 쓰임새를 찾을 수 있겠지요. "
            "행운 단계가 높을수록 가루를 얻을 확률도 올라갑니다."
        ),
        "info_book.evilcraft.first_age.new_world.darkened_apple.text": (
            "이 책을 읽는 동안 이미 이 아이템을 발견했을지도 모릅니다. &1사과&0와 "
            "&1다크 젬&0을 조합하면, 먹었을 때 일정 시간 큰 피해를 주는 특별한 "
            "&1사과&0가 만들어집니다. 이 효과로 대상이 죽으면 정체불명의 변칙이 "
            "남습니다. 아직 이 현상의 쓰임새는 알아내지 못했습니다..."
        ),
    },
    "evilcraftcompat": {
        "info_book.evilcraftcompat.mod_integrations.jei.text": (
            '어떤 사람에게는 "&oToo Many Items&r"가 있고, 다른 사람에게는 '
            '"&oNot Enough Items&r"가 있는 모양입니다. 마침내 사람들이 '
            '"&oJust Enough Items&r"를 갖춘 단계에 도달한 듯하며, 이제 그들도 '
            "이 책의 지식을 이해할 수 있습니다."
        ),
        "info_book.evilcraftcompat.mod_integrations.ic2.text": (
            "윙윙거리는 기계를 끊임없이 다루는 이상한 무리가 있습니다. 그 기계들이 "
            "무엇을 하는지는 &1분쇄기&0 말고는 잘 모르겠습니다. &1다크 광석&0을 "
            "넣으면 곧바로 &1다크 젬&0과 분쇄된 형태를 얻을 수 있습니다. 일반 "
            "&1다크 젬&0도 넣어 분쇄할 수 있습니다."
        ),
        "info_book.evilcraftcompat.mod_integrations.thermal_expansion.text": (
            "이 사람들은 꽤 기묘합니다. 늘 이상한 옷을 입고, 어째서인지 여러 종류의 "
            "렌치를 들고 다니는 듯합니다. 제가 아는 것은 하나뿐입니다. 이들에게는 "
            "액체를 옮기는 기계가 있어 아주 기본적인 피 주입을 할 수 있지만, 안타깝게도 "
            "업그레이드할 수 없습니다."
        ),
    },
}

QUEST_OVERRIDES: dict[str, object] = {
    "quest.0104C2E2E30B966B.quest_desc": [
        "&c피의 상자&r가 너무 느린가요? 수리할 아이템이 너무 많나요? "
        "&c거대한 피의 상자&r를 만들면 이 문제를 해결할 수 있습니다.\\n\\n"
        "먼저 &9강화된 언데드 판자&r 25개를 만드세요. 이 판자로 속이 빈 3x3x3 "
        "정육면체를 만든 뒤, &c거대한 피의 상자&r 블록을 놓아 멀티블록 구조를 "
        "완성하세요. 올바르게 지었다면 이제 거대한 &c피의 상자&r를 사용할 수 "
        "있습니다. 이름처럼 정말 거대하죠.\\n\\n이 상자는 &6약속&r으로 업그레이드할 "
        "수도 있습니다.\\n",
        "{image:atm:textures/questpics/evilcraft/bloodchest.png width:250 "
        "height:200 align:1}",
    ],
    "quest.1DA0A87C471A38AC.quest_desc": [
        "&cEvilCraft&r에는 자체 몹 농장도 있습니다!\\n\\n시작하려면 "
        "&c다크 블러드 벽돌&r을 최소 33개 제작하세요. 이 벽돌로 소환된 정령을 "
        "가둘 만큼 튼튼한 구조물을 만들 수 있습니다.\\n\\n또한 &9영원한 봉쇄 "
        "상자&r에 갇힌 정령이 필요합니다. 어떤 드롭 아이템을 얻을지는 이 정령이 "
        "결정합니다.\\n\\n몹이 생성될 공간이 충분한 직육면체 구조물을 만드세요. 최소 "
        "크기는 3x4x3이며 좀비 같은 몹이 생성되기에 충분합니다. 구조물의 한 면에는 "
        "상호작용할 수 있도록 &9영혼 화로&r를 놓으세요.\\n\\n더 큰 몹을 생성하려면 "
        "더 큰 구조물이 필요합니다.\\n",
        "{image:atm:textures/questpics/evilcraft/evilcraft_spiritfurnace.png "
        "width:125 height:150 align:1}",
    ],
    "quest.35FA55BE8DF49EE8.title": "&d가몬보지아",
    "quest.6B7C016407F7AE3C.quest_desc": [
        "일반 무기로는 &d복수령&r을 공격할 수 없습니다. 그러면 어떻게 처치해야 "
        "할까요?\\n\\n관통 복수 빔을 발사하면 됩니다. 관통 복수 집중기를 어느 "
        "손이든 든 채 우클릭을 누르고 있으면 빔을 발사합니다."
    ],
    "quest.6B7C016407F7AE3C.quest_subtitle": "복수령 처치하기",
    "quest.745E616E97838D2E.quest_desc": [
        "&l잠깐!&r 동물을 마구 학살하지 마세요. PETA가 타협안을 제시한 모양입니다. "
        "무고한 동물을 그만 죽이면 &5크리에이티브 &4피 드롭&r을 준다고 하네요! "
        "\\n\\n이 아이템을 사용하면 &4피&r가 필요한 모든 용기를 무한히 채울 수 "
        "있습니다! \\n\\n제작하려면 &b끈기의 약속&r 4개, &6&lATM Star&r, "
        "그리고 &4피&r로 가득 찬 다른 아이템 4개가 필요합니다. "
    ],
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def replace_terms(value: object) -> object:
    """문자열 또는 문자열 목록의 확정 용어를 통일한다."""
    if isinstance(value, str):
        for before, after in TERM_REPLACEMENTS:
            value = value.replace(before, after)
        value = value.replace("GUI", "화면").replace("Grid", "제작 격자")
        return value
    if isinstance(value, list):
        return [replace_terms(child) for child in value]
    return value


def review_language() -> dict[str, object]:
    """언어 작업본 전체에 용어 통일과 검수 수정을 반영한다."""
    report: dict[str, object] = {}
    for namespace in ("evilcraft", "evilcraftcompat"):
        root = WORK_ROOT / namespace
        korean_path = root / "ko_kr.json"
        source_path = root / "candidate_sources.json"
        korean = load_json(korean_path)
        sources = load_json(source_path)
        before = dict(korean)
        korean = {key: replace_terms(value) for key, value in korean.items()}
        for key, value in LANGUAGE_OVERRIDES[namespace].items():
            korean[key] = value
        changed_keys = [key for key in korean if korean[key] != before[key]]
        for key in changed_keys:
            sources[key] = "manual_review"
        korean_path.write_text(
            json.dumps(korean, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        source_path.write_text(
            json.dumps(sources, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        report[namespace] = {
            "keys_reviewed": len(korean),
            "keys_changed": sum(value == "manual_review" for value in sources.values()),
            "changes_this_run": len(changed_keys),
            "source_counts": dict(sorted(Counter(sources.values()).items())),
        }
    return report


def review_quests() -> dict[str, object]:
    """전용 및 관련 퀘스트의 기존 한국어와 신규 문구를 검수한다."""
    reviewed = 0
    changed = 0
    changes_this_run = 0
    source_counts: Counter[str] = Counter()
    for root in sorted((WORK_ROOT / "quests").glob("*")):
        korean_path = root / "ko_kr.json"
        source_path = root / "candidate_sources.json"
        if not korean_path.is_file():
            continue
        korean = load_json(korean_path)
        sources = load_json(source_path)
        before = dict(korean)
        korean = {key: replace_terms(value) for key, value in korean.items()}
        for key, value in QUEST_OVERRIDES.items():
            if key in korean:
                korean[key] = value
        changed_keys = [key for key in korean if korean[key] != before[key]]
        for key in changed_keys:
            sources[key] = "manual_review"
        korean_path.write_text(
            json.dumps(korean, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        source_path.write_text(
            json.dumps(sources, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        reviewed += len(korean)
        changed += sum(value == "manual_review" for value in sources.values())
        changes_this_run += len(changed_keys)
        source_counts.update(str(value) for value in sources.values())
    return {
        "keys_reviewed": reviewed,
        "keys_changed": changed,
        "changes_this_run": changes_this_run,
        "source_counts": dict(sorted(source_counts.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    report = {
        "family": "EvilCraft",
        "languages": review_language(),
        "ftbquests": review_quests(),
    }
    (WORK_ROOT / "manual_review_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
