#!/usr/bin/env python3
"""PneumaticCraft 관련 FTB Quests 기존 번역 전체를 재검수한다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT


QUEST_ROOT = PROJECT_ROOT / "working/pneumaticcraft/quests"

TEXT_REPLACEMENTS = (
    ("압축된 철 갑옷", "압축 철 방어구"),
    ("압축된 아이언 맨", "압축 아이언맨"),
    ("압축된 철", "압축 철"),
    ("공압 갑옷", "공압 방어구"),
    ("전송 도구", "전송 가젯"),
    ("로지스틱 모듈", "물류 모듈"),
    ("로지스틱 틀", "물류 프레임"),
    ("로지스틱 코어", "물류 코어"),
    ("로지스틱 설정 장치", "물류 설정기"),
    ("전송 장치", "전송 가젯"),
    ("액체 호퍼", "유체 호퍼"),
    ("열 틀", "열 프레임"),
    ("아이템/액체 운송", "아이템/유체 운송"),
    ("특정 액체가", "특정 유체가"),
    ("해당 액체가", "해당 유체가"),
    ("특정 액체를 사용", "특정 유체를 사용"),
    ("액체를 펌프로 주입", "유체를 파이프로 주입"),
    ("피글린을 패시브 상태로 만듭니다", "피글린이 적대하지 않게 합니다"),
    ("방어구을", "방어구를"),
    ("FE를 펌프로 공급", "FE를 공급"),
    ("액체 플라스틱", "용융 플라스틱"),
    ("Tier I", "I단계"),
    ("Tier II", "II단계"),
    ("티어 I", "I단계"),
    ("티어 II", "II단계"),
    ("Solution", "해결책"),
    ("오른손 클릭", "우클릭"),
    ("업그레이드을", "업그레이드를"),
    ("주의하십시오", "주의하세요"),
    ("갑옷", "방어구"),
    ("보안 상위 버전으로 변환", "보안 업그레이드"),
    ("상위 버전으로 변환", "업그레이드"),
    ("뉴매틱크래프트", "PneumaticCraft"),
    ("뉴매틱 다이나모", "공압 다이나모"),
    ("프로덕티브 비", "Productive Bees"),
    ("신비농업", "Mystical Agriculture"),
    ("스포너", "생성기"),
    ("뉴매틱", "공압"),
    ("무인 항공기", "드론"),
    ("에어 캐니스터", "공기 용기"),
    ("디스펜서 업그레이드", "발사기 업그레이드"),
    ("볼륨 업그레이드", "용량 업그레이드"),
    ("개체 트래커", "개체 추적기"),
    ("블록 트래커", "블록 추적기"),
    ("압력관", "압력 튜브"),
    ("정유소", "정유기"),
    ("케로신", "등유"),
    ("가솔린", "휘발유"),
    ("바이오 디젤", "바이오디젤"),
    ("가슴판", "흉갑"),
    ("MOD", "모드"),
    ("항목", "아이템"),
)

KEY_OVERRIDES: dict[str, object] = {
    "quest.002163B909070CF8.quest_desc": [
        "벽 너머에 있는 특정 블록과 유체의 상세 정보도 볼 수 있습니다.\\n",
        "{image:atm:textures/questpics/pneumaticcraft/block_tracker.png width:150 height:150 align:center}",
    ],
    "quest.0A912B2E2BE34920.quest_desc": [
        "지표에서도 원유를 찾을 수 있지만, 굴착하면 많은 양을 얻을 수 있습니다. 먼저 "
        "&3지진 센서&r로 아래에 원유가 있는 곳을 찾으세요. 그다음 드릴 파이프를 채운 "
        "&3가스 리프트&r로 원유를 퍼 올리세요. 작동하려면 압력이 필요합니다.\\n",
        "{image:pneumaticcraft:textures/patchouli/oil_pumping.png width:200 height:200 align:right fit:true}",
    ],
    "quest.0AEAEA976ED0C470.quest_subtitle": "전선은 어디 있죠?",
    "quest.23737103592776C2.quest_desc": [
        "&3등유 램프&r는 연료를 사용해 빛을 내는 훌륭한 광원이며, 등유가 가장 좋은 "
        "연료입니다."
    ],
    "quest.312331F6DB0CE5F4.quest_desc": ["Tier I보다 더 빠릅니다."],
    "quest.440B1E1D4951F808.quest_desc": [
        "&3스마트 상자&r는 폭발에 견디는 72칸 상자입니다. 완전히 설정 가능한 "
        "전방향 호퍼가 내장되어 있고 업그레이드 슬롯도 있습니다. 두 상자로 합칠 수는 "
        "없으며 셜커 상자처럼 내용물을 보존합니다.",
        "{image:atm:textures/questpics/pneumaticcraft/smart_chest_ui.png width:200 height:100 align:center}",
    ],
    "quest.461C8F1E88AA58D9.quest_desc": [
        "PneumaticCraft 유체가 든 양동이를 사용하는 제조법에 이 탱크를 활용할 수 "
        "있습니다.\\n\\n&3유체 탱크&r를 다른 &3유체 탱크&r 위에 놓고 렌치로 연결하면 "
        "하나의 큰 탱크처럼 작동합니다.\\n",
        "{image:pneumaticcraft:textures/patchouli/small_tanks.png width:250 height:250 align:center fit:true}",
    ],
    "quest.4A076530297F4A97.quest_desc": [
        "이 3개 부품으로 멋진 &3엘리베이터&r를 만들 수 있습니다.\\n",
        "{image:pneumaticcraft:textures/patchouli/elevator.png width:1 height:1 align:left fit:true}",
    ],
    "quest.521656D425E2FDBA.quest_desc": ["Tier II보다 훨씬 더 빠릅니다."],
    "quest.52D3697F1F5625C7.quest_desc": [
        "&3에칭 산&r은 압력 챔버에서 용융 플라스틱과 몇 가지 재료로 만들며, 에칭 "
        "탱크에서 사용합니다."
    ],
    "quest.53518D4ED99A242F.quest_subtitle": "장치를 멋지게 꾸미고 싶나요?",
    "quest.5D7B34761E8FD212.quest_desc": [
        "&3정전기 압축기&r는 번개를 맞아 많은 압력을 생성합니다.\\n\\n자세한 내용은 "
        'JEI의 "정보" 탭을 확인하세요.\\n',
        "{image:pneumaticcraft:textures/patchouli/electrostatic_compressor.png width:100 height:100 align:left fit:true}",
    ],
    "quest.5E71F8A046C60346.quest_desc": [
        "PneumaticCraft가 동력을 생산하는 모드가 아니라고 누가 그랬나요?\\n\\n"
        "&3공압 다이나모&r는 압력을 FE로 바꿉니다. 툴팁이나 PNC:R 설명서를 읽어 작동 "
        "방식을 확인하세요."
    ],
    "quest.68F92455A9483AD6.quest_subtitle": "겉날개가 어렵다고 생각했나요?",
    "quest.6CA01DCE1F4A0EC3.quest_desc": [
        "다음 단계로 진행하려면 &3원유&r가 필요합니다. 원유는 오버월드 지표에서 "
        "자연적으로 발견할 수 있습니다."
    ],
    "quest.6FD65139CD50A8C0.quest_desc": [
        "그게 가능하기나 할까요?\\n\\n이 과정을 자동화하려면 &eProductive Bees&r나 "
        "&aMystical Agriculture&r를 사용할 수 있습니다. 아니면... 폭발로 자동화할 수도 "
        "있겠네요."
    ],
    "quest.72C09FD89C28B1EC.quest_desc": [
        "이번에 만들 &3정유기&r는 아래쪽 &3정유기 제어기&r 1개와 그 위의 "
        "&3정유기 출력부&r 네 개로 구성된 1x1x5 멀티블록입니다. 원유와 열을 공급하면 "
        "디젤, 등유, 휘발유, LPG를 생산합니다. 옆면에 &3단열재&r를 붙이면 열을 "
        "유지하는 데 도움이 됩니다.",
        "",
        "{image:atm:textures/questpics/pneumaticcraft/oil_refinery.png width:300 height:150 align:center}",
    ],
    "quest.7386A8433698946C.quest_desc": [
        "아이템을 선택하면 이 업그레이드가 주변 상자나 바닥에서 해당 아이템을 찾습니다. "
        "상자 안을 검색하려면 블록 추적기 업그레이드가, 바닥의 아이템을 검색하려면 개체 "
        "추적기 업그레이드가 필요합니다.\\n",
        "{image:atm:textures/questpics/pneumaticcraft/item_search_upgrade.png width:200 height:200 align:center}",
    ],
}

ALLOWED_EXACT_KEYS = {
    "quest.2E252FA1B5D9E0D7.title",
    "quest.3AAB71E9BDFD4C1E.title",
    "quest.04BE9F63E6003475.title",
    "quest.43CDC28DC56BB3E2.quest_subtitle",
    "quest.461C8F1E88AA58D9.quest_subtitle",
    "quest.4E1E31EDD544EE10.quest_subtitle",
    "task.13266875BDB5077D.title",
    "task.2C268116DA162155.title",
    "quest.21B96130EA516B82.quest_subtitle",
    "quest.6ED2CDD01659FD10.quest_subtitle",
}


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def replace_text(value: object) -> object:
    if isinstance(value, list):
        return [replace_text(child) for child in value]
    if not isinstance(value, str):
        return value
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    return value


def normalize() -> dict[str, object]:
    reviewed = 0
    changed = 0
    unresolved: list[str] = []
    for root in sorted(QUEST_ROOT.glob("*")):
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        source_file = root / "candidate_sources.json"
        if not english_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        sources = load_json(source_file)
        for key, source in english.items():
            target = KEY_OVERRIDES.get(key, korean[key])
            if sources[key] == "new_translation_required" and key not in KEY_OVERRIDES:
                unresolved.append(key)
                continue
            target = replace_text(target)
            errors = quest_snbt.validate_value(key, source, target)
            if errors:
                raise ValueError("; ".join(errors))
            reviewed += 1
            if korean[key] != target:
                korean[key] = target
                changed += 1
        write_json(korean_file, korean)
    report = {
        "display_keys_reviewed": reviewed,
        "changed": changed,
        "manual_overrides": len(KEY_OVERRIDES),
        "unresolved": len(unresolved),
        "unresolved_examples": unresolved,
        "review_status": "full_existing_korean_reviewed",
    }
    write_json(QUEST_ROOT.parent / "quest_normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    untranslated: list[str] = []
    checked = 0
    for root in sorted(QUEST_ROOT.glob("*")):
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        if not english_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        if list(english) != list(korean):
            errors.append(f"{root.name}: 키 또는 순서가 영어 원문과 다릅니다.")
        for key, source in english.items():
            target = korean.get(key)
            errors.extend(quest_snbt.validate_value(key, source, target))
            if key not in ALLOWED_EXACT_KEYS and quest_snbt.flatten(
                source
            ) == quest_snbt.flatten(target):
                untranslated.append(key)
            checked += 1
    report = {
        "display_keys": checked,
        "untranslated": len(untranslated),
        "untranslated_examples": untranslated,
        "errors": errors,
        "status": "complete" if not errors and not untranslated else "incomplete",
    }
    write_json(QUEST_ROOT.parent / "specialized_quest_validation.json", report)
    if untranslated:
        errors.append(f"미번역 {len(untranslated)}개")
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("normalize", "verify"))
    args = parser.parse_args()
    if args.command == "normalize":
        report = normalize()
        errors = []
    else:
        report, errors = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
