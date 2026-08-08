#!/usr/bin/env python3
"""Silent Gear 계열 FTB Quests 전체 표시 문구를 번역하고 누적 산출물로 만든다."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import build_ae2_quests as snbt
from local_paths import PROJECT_ROOT, resolve_source_root

WORK_ROOT = PROJECT_ROOT / "working/silentgear"
OUTPUT_FILE = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
ENGLISH_FILE = WORK_ROOT / "quest_english.json"
OVERRIDES_FILE = WORK_ROOT / "quest_overrides.json"
REPORT_FILE = WORK_ROOT / "quest_progress.json"
CHAPTER = "silent_gear"
CHAPTER_TITLE_KEY = "chapter.1D42B373285DEF81.title"
INTERNAL_KEYS = {
    "task.55E0635973A828B0.title",
    "task.6D9DBD885FE4C94C.title",
}
FALLBACK_TITLES = {
    "quest.11B0B93D725ABE43.title": "수리 키트",
    "quest.36A5229DB5D4C059.title": "주괴 주형",
    "quest.0251715AB65D8151.title": "보석 주형",
    "quest.4119E115505036E5.title": "조각 주형",
    "quest.7965E2CBF3FF9B65.title": "톱니바퀴 주형",
    "quest.00A1223DAAEB28BD.title": "막대 주형",
    "quest.75EE2123753062B8.title": "판 주형",
}


def paragraph(text: str) -> list[str]:
    """FTB Quests 설명 필드 형식으로 문단 하나를 만든다."""
    return [text]


TRANSLATIONS: dict[str, snbt.TranslationValue] = {
    "quest.002D65E4D7E8F62B.title": "2단계 등급기 촉매제",
    "quest.036D5767E07005BC.quest_desc": paragraph(
        "&b배출구&r는 &7액체 금속&r을 꺼낼 때 사용합니다. 손이나 양동이로 다루기에는 "
        "너무 뜨겁거든요. \\n\\n&c&l주조소&r의 &7꼭지&r를 &b배출구&r에 연결하세요. "
        "꼭지를 우클릭하면 &7액체 금속&r이 흘러나옵니다. \\n\\n&b배출구&r를 보면 "
        "&c&l주조소&r에 들어 있는 액체의 양도 확인할 수 있습니다!"
    ),
    "quest.036D5767E07005BC.title": "&c&l주조소&r &b배출구",
    "quest.047F3F99035CE623.quest_subtitle": "광산이 그리워요",
    "quest.061A51A0EC13CA0F.quest_desc": paragraph(
        "이제 &a제어기&r, &b배출구&r, &4탱크&r가 있으니 블록 몇 가지가 더 필요합니다. "
        "\\n\\n먼저 &6액체 가열 코일&r은 &c&l주조소&r의 바닥을 이루며 주조소를 "
        "가열하는 데 필요합니다. \\n\\n나머지 구조물은 &c&l주조소&r 창 또는 "
        "&c내화 벽돌&r로 채웁니다. 말 그대로 건축 블록이죠! \\n\\n&c&l주조소&r의 "
        "모서리 틀은 비워도 되지만, 완성하려면 벽 4면과 바닥이 있어야 합니다. 빠진 블록이 "
        "있다면 &a제어기&r가 위치를 알려 줍니다. \\n\\n&a제어기&r와 &6액체 가열 코일&r, "
        "벽만 제대로 갖추면 내부가 1x1인 작은 &c&l주조소&r도 만들 수 있습니다. "
        "\\n\\n하지만 &c&l주조소&r가 클수록 내부 공간도 넓어지므로 너무 작은 "
        "&c&l주조소&r를 만드는 것은 권하지 않습니다! \\n\\n&a제어기&r가 화로처럼 빛나고 "
        "&6액체 가열 코일&r이 &6주황색&r으로 "
        "변하면 &c&l주조소&r가 완성된 것입니다."
    ),
    "quest.061A51A0EC13CA0F.title": "&c&l주조소&r 건설",
    "quest.0EF9F10A2178451F.quest_desc": paragraph(
        "&c&l주조소&r의 모든 부품은 꼭지, 주조대, 주조 대야를 제외하고 원하는 "
        "&z색상&r으로 염색할 수 있습니다. 서로 다른 &z색상&r도 한 &c&l주조소&r에서 "
        "함께 사용할 수 있으니 원한다면 알록달록한 &c&l주조소&r를 만들어 보세요."
    ),
    "quest.0EF9F10A2178451F.title": "&z염색 가능한 &c&l주조소&r &z부품",
    "quest.0DF4B01CC5B49E4E.quest_desc": paragraph(
        "이 주형으로 기본 검을 만들 수 있습니다! 믿을 만한 피해량과 속도를 제공합니다."
    ),
    "quest.0FEAD3CA2CC4A8B1.title": "3단계 별빛 충전기 촉매제",
    "quest.158B24939A269D83.quest_desc": paragraph(
        "팁 업그레이드는 도구의 채굴 등급을 높이는 데 사용합니다.\\n\\n예를 들어 철 곡괭이와 "
        "다이아몬드 1개로 다이아몬드 팁 업그레이드를 만들어 곡괭이에 장착하면 흑요석을 "
        "캘 수 있고 능력치도 향상됩니다."
    ),
    "quest.158B24939A269D83.quest_subtitle": "다이아몬드 3개를 찾지 못했을 때",
    "quest.2156C00E30424844.quest_desc": paragraph(
        "&4탱크&r는 &c&l주조소&r에 액체를 넣는 데 사용합니다. \\n\\n주로 연료를 "
        "넣습니다. \\n\\n대부분 &c용암&r이죠! \\n\\n현재로서는 용암이 &c&l주조소&r에 "
        "연료를 공급하는 거의 유일한 방법입니다."
    ),
    "quest.2156C00E30424844.title": "&c&l주조소&r &4탱크",
    "quest.22A0A9C81A5C85A1.quest_subtitle": "모든 부품을 하나로 묶기",
    "quest.26F9DB31A835B69C.quest_desc": paragraph(
        "&n주조소&r: &a확인&r \\n&n주조소의 액체 금속&r: &a확인&r \\n\\n이제 어떻게 "
        "꺼낼까요? \\n\\n앞에서 만난 &c&l주조소&r &b배출구&r를 새 친구인 &c&l주조소&r "
        "&7꼭지&r와 연결할 차례입니다. \\n\\n&b배출구&r에 &c&l주조소&r &7꼭지&r를 설치하면 "
        "그 아래의 블록으로 &7액체 금속&r을 흘려보낼 수 있습니다. \\n\\n&8주조 대야&r는 "
        "약 900mB의 &7액체 금속&r을 완전한 &7금속 블록&r으로 만듭니다. \\n\\n또는 "
        "&8주조대&r를 사용하면 다음에 필요한 물건을 만들 수 있습니다..."
    ),
    "quest.26F9DB31A835B69C.title": "아이템 주조",
    "quest.29131C3532610ADF.quest_desc": paragraph(
        "별빛 충전기용 2단계 기둥 덮개입니다."
    ),
    "quest.29131C3532610ADF.title": "2단계 별빛 충전기 기둥 덮개",
    "quest.2BF119DD5D977409.title": "2단계 별빛 충전기 촉매제",
    "quest.2EB96FF06627FD9A.quest_subtitle": "(일부) 아이템 분해!",
    "quest.2EB96FF06627FD9A.title": "회수기",
    "quest.3B560B2ECE331CAF.quest_desc": paragraph(
        "별빛 충전기용 3단계 기둥 덮개입니다."
    ),
    "quest.3B560B2ECE331CAF.title": "3단계 별빛 충전기 기둥 덮개",
    "quest.405DCD3E36232EEA.quest_desc": paragraph(
        "검보다 피해는 낮지만, 도달 거리가 더 깁니다."
    ),
    "quest.45899579D9B92D91.quest_desc": paragraph(
        "&a제어기&r는 &c&l주조소&r의 핵심입니다. \\n\\n모든 &c&l주조소&r에는 "
        "제어기가 1개 이상 필요합니다. \\n\\n&c&l주조소&r를 사용하면 &c&l주조소&r의 "
        "GUI를 열어 &c&l주조소&r 내부 액체의 양을 확인할 수 있습니다. \\n\\n아이템을 "
        "&c&l주조소&r에 넣거나 꺼낼 때도 사용할 수 있습니다."
    ),
    "quest.45899579D9B92D91.title": "&c&l주조소&r &a제어기",
    "quest.48D358470A019E7A.title": "1단계 별빛 충전기 촉매제",
    "quest.6A393C7A24899E3E.quest_desc": paragraph(
        "재료 등급기 촉매와 함께 주괴를 재료 등급기에 넣으면 재료에 등급이 "
        "매겨집니다.\\n\\n등급이 좋을수록 재료의 능력치가 더 좋습니다.\\n\\n최고 등급은 "
        '"MAX"입니다.'
    ),
    "quest.6B78378BC8036227.title": "1단계 등급기 촉매제",
    "quest.6BBC440BD0AD0E93.quest_desc": paragraph(
        "&9&lSilent Gear&r를 좋아하는 사람도 있고 &7&lTinker's Construct&r를 좋아하는 "
        "사람도 있습니다. \\n\\n둘 중 하나만 고르는 대신 &9&lSilent Gear&r와 "
        "&c&lProductive Metalworks&r를 함께 사용해 두 방식의 장점을 살렸습니다! "
        "\\n\\n&c&lProductive Metalworks&r에서는 &9&lSilent Gear&r 아이템을 얻는 방식이 "
        "달라집니다. 이제 &9청사진&r 대신 &8주형&r과 &c&l주조소&r가 필요합니다. "
        "\\n\\n&c&l주조소&r 제작은 &c내화 점토&r부터 시작하세요."
    ),
    "quest.6BBC440BD0AD0E93.title": "&9&lSilent Gear&r와 &c&lProductive Metalworks",
    "quest.711826BBCA832EE2.quest_desc": paragraph(
        "모든 &8주형&r은 같은 방법으로 만듭니다. \\n\\n&8주조대&r에 아이템을 놓고 그 위에 "
        "&8강철&r을 부으면 됩니다! \\n\\n&8강철&r은 &8강철 아이템이나 주괴&r를 녹여 얻을 수 "
        "있습니다. 또는 &7철&r 9개와 &0석탄&r 10개를 합금으로 만들 수도 있습니다. "
        "\\n\\n&c&l주조소&r가 &6가열&r되어 있고 서로 다른 &7액체 금속&r이 정확한 양만큼 "
        "들어 있으면 합금이 만들어집니다. 두 &7액체 금속&r이 하나의 새로운 &7액체 금속&r으로 "
        "합쳐집니다!"
    ),
    "quest.711826BBCA832EE2.title": "&8주형",
    "quest.769D5DE66D13B256.quest_desc": paragraph(
        "이 퀘스트는 &6AllTheMods 스태프&r 또는 &2커뮤니티 기여자&r가 AllTheMods 모드팩에 "
        "사용하기 위해 작성했습니다.\\n\\n모든 &6AllTheMods&r 팩은 "
        "&eAll Rights Reserved&r 라이선스로 보호되므로, &6AllTheMods 팀&r의 명시적인 허가 "
        "없이 다른 공개 모드팩에 이 퀘스트를 사용할 수 없습니다.\\n\\n이 퀘스트는 의도적으로 "
        "숨겨져 있습니다. 이 문구가 보인다면 편집 모드입니다."
    ),
    "quest.7C3D763CF22D167A.quest_desc": paragraph(
        '별빛 충전기는 재료에 "별빛 충전" 특성을 부여할 수 있습니다.\\n\\n밤하늘이 보이는 '
        "곳에서 별빛 충전기를 중심으로 구조물을 지어야 하며 밤에만 별빛 에너지를 얻습니다."
        "\\n\\n충전기는 7x7 구조물의 중앙에 놓고 각 모서리에 기둥을 세워야 합니다. 각 "
        '기둥에는 "별빛 충전기 기둥 덮개"가 필요합니다.\\n\\n재료마다 충전기 촉매제도 '
        "하나씩 필요합니다."
    ),
    "quest.7C3D763CF22D167A.quest_subtitle": "재료에 특성 부여",
    "quest.7D690A7D0FF6E328.title": "3단계 등급기 촉매제",
    "quest.7E13007340A818C5.quest_desc": paragraph(
        "별빛 충전기용 1단계 기둥 덮개입니다."
    ),
    "quest.7E13007340A818C5.title": "1단계 별빛 충전기 기둥 덮개",
    "task.2AE89914A34BF3AD.title": "내화 벽돌 또는 주조소 창",
    "task.3B23E744D3B72AE8.title": "내화 벽돌 또는 주조소 창",
    "task.511ECEA2E9BD1F71.title": "#productivemetalworks:foundry_drains 태그의 아무 아이템",
    "task.51297F6E0D9BB58C.title": "#productivemetalworks:foundry_tanks 태그의 아무 아이템",
    "task.76E296A2AD3EFE92.title": "#productivemetalworks:foundry_controllers 태그의 아무 아이템",
}


def sha256(path: Path) -> str:
    """파일의 SHA-256을 계산한다."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_value(
    key: str, source: snbt.TranslationValue, target: snbt.TranslationValue
) -> list[str]:
    """어순 변경을 허용하며 색상 코드와 숫자의 전체 집합을 보존한다."""
    errors = snbt.validate_value(key, source, target)
    source_text = snbt.flatten(source)
    target_text = snbt.flatten(target)
    code_error = f"{key}: 색상/서식 코드 불일치"
    number_error = f"{key}: 숫자 불일치"
    if code_error in errors and Counter(re.findall(r"&.", source_text)) == Counter(
        re.findall(r"&.", target_text)
    ):
        errors.remove(code_error)
    if number_error in errors:
        number_re = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?")
        source_numbers = number_re.findall(re.sub(r"&.", "", source_text))
        target_numbers = number_re.findall(re.sub(r"&.", "", target_text))
        if Counter(source_numbers) == Counter(target_numbers):
            errors.remove(number_error)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    lang_root = instance / "config/ftbquests/quests/lang"
    english = snbt.parse_language_snbt(
        lang_root / f"en_us/chapters/{CHAPTER}.snbt_merged"
    )
    installed = snbt.parse_language_snbt(
        lang_root / f"ko_kr/chapters/{CHAPTER}.snbt_merged"
    )
    full_english = snbt.parse_language_snbt(lang_root / "en_us.snbt")
    full_korean = snbt.parse_language_snbt(lang_root / "ko_kr.snbt")
    english[CHAPTER_TITLE_KEY] = full_english[CHAPTER_TITLE_KEY]
    installed[CHAPTER_TITLE_KEY] = full_korean[CHAPTER_TITLE_KEY]
    draft = {key: installed.get(key, source) for key, source in english.items()}
    unknown = sorted(set(TRANSLATIONS) - set(english))
    if unknown:
        raise KeyError(f"영어 원문에 없는 번역 키: {unknown}")
    draft.update(TRANSLATIONS)
    errors: list[str] = []
    for key, source in english.items():
        errors.extend(validate_value(key, source, draft[key]))
        if (
            draft[key] == source
            and re.search(r"[A-Za-z]{3,}", snbt.flatten(source))
            and key not in INTERNAL_KEYS | {CHAPTER_TITLE_KEY}
        ):
            errors.append(f"분류되지 않은 영어 원문 유지: {key}")
    if errors:
        raise RuntimeError("\n".join(errors))

    base = OUTPUT_FILE if OUTPUT_FILE.is_file() else lang_root / "ko_kr.snbt"
    base_hash = sha256(base)
    merged_values = dict(draft)
    merged_values.update(FALLBACK_TITLES)
    output = snbt.merge_into_full_snbt(base, merged_values)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(output, encoding="utf-8")
    reparsed = snbt.parse_language_snbt(OUTPUT_FILE)
    for key, value in merged_values.items():
        if reparsed.get(key) != value:
            raise RuntimeError(f"누적 SNBT 병합값 불일치: {key}")

    ENGLISH_FILE.write_text(
        json.dumps(english, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    OVERRIDES_FILE.write_text(
        json.dumps(merged_values, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    kept = sum(key in installed and installed[key] == draft[key] for key in english)
    corrected = sum(
        key in installed and installed[key] != draft[key] for key in english
    )
    new = sum(key not in installed for key in english) + len(FALLBACK_TITLES)
    report = {
        "scope": "Silent Gear family FTB Quests",
        "chapter": CHAPTER,
        "source_display_keys": len(english),
        "fallback_titles_added": len(FALLBACK_TITLES),
        "existing_korean_kept": kept,
        "existing_korean_corrected": corrected,
        "newly_completed": new,
        "classification": {
            "translated_or_localized": len(english) - len(INTERNAL_KEYS),
            "intentional_original": 1,
            "internal_or_not_displayed": len(INTERNAL_KEYS),
            "out_of_scope": 0,
            "manual_review": 0,
        },
        "remaining": 0,
        "base_sha256": base_hash,
        "output_sha256": sha256(OUTPUT_FILE),
        "status": "passed",
    }
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
