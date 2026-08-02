#!/usr/bin/env python3
"""Extreme Reactors 전용·연관 FTB Quests 한국어를 전수 재검수한다."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import five_family_goal as family_goal
from local_paths import PROJECT_ROOT


WORK_ROOT = PROJECT_ROOT / "working/extreme_reactors"
QUEST_ROOT = WORK_ROOT / "quests"
CHAPTERS = ("extreme_reactors", "related")

ALLOWED_EXACT_KEYS = {
    ("extreme_reactors", "task.27D8027E1B88F02A.title"),
    ("extreme_reactors", "task.4851C74261B5FA25.title"),
    ("related", "quest.3331EBE1BB4BF64D.title"),
}

KEY_OVERRIDES: dict[tuple[str, str], object] = {
    (
        "extreme_reactors",
        "quest.14E5349DD740D026.title",
    ): "수동 냉각 원자로에 연료 공급하기",
    ("extreme_reactors", "quest.186731580B14F9D2.quest_desc"): [
        "터빈을 사용하려면 여러 &6포트&r가 필요합니다.\\n\\n&9유체 포트&r는 "
        "&b증기&r를 받아들이거나 사용 후 응축된 &9물&r을 내보냅니다. 따라서 터빈에는 "
        "입력용과 출력용으로 두 개가 필요합니다.\\n\\n&c전력 탭&r은 생성된 전력을 "
        "꺼내며, 멀티블록을 완성하는 데 꼭 필요합니다."
    ],
    ("extreme_reactors", "quest.25D4406CB86C8CBB.quest_desc"): [
        "이제 원자로에서 &9폐기물&r을 모으고 있으니, 진행에 필요한 일부 주괴를 "
        '"유체화"해야 합니다. 무슨 뜻일까요?\\n\\n&a유체화기&r를 만들어야 합니다! '
        "핵심 부품은 &a유체화기 제어기&r입니다. 완성한 뒤 제어기를 우클릭하면 화면이 "
        "열립니다. 여기에서 작동을 켜거나 끄고, 내부 내용물과 현재 에너지 수준을 확인할 수 있습니다."
    ],
    ("extreme_reactors", "quest.2A20000FAEC2E16A.quest_desc"): [
        "원자로에서 전력이나 아이템을 꺼내고 연료를 넣으려면 이 &c필수&r 블록들이 "
        "필요합니다.\\n\\n&c전력 탭&r은 &9수동 냉각&r 원자로가 만든 전력을 꺼내는 "
        "통로입니다. 파이프나 케이블을 연결해 전력을 전달할 수 있습니다.\\n\\n"
        "&a반입출 포트&r는 모든 원자로에 필요하며 연료를 넣거나 폐기물을 꺼내는 데 "
        "사용합니다. 보통 입력용과 출력용으로 원자로마다 2개를 두는 것이 좋습니다."
    ],
    ("extreme_reactors", "quest.3C3FE45CEF5E242B.quest_desc"): [
        "다른 &a재처리기 부품&r은 정해진 위치가 있지만, 이 세 부품은 틀이 아닌 수직 면이라면 "
        "어디에나 놓을 수 있습니다!\\n\\n&c전력 포트&r는 폐기물을 처리하는 멀티블록에 "
        "전력을 공급합니다.\\n\\n&9유체 주입기 포트&r는 투입한 폐기물 종류에 맞는 유체를 "
        "공급합니다. 시아나이트를 처리할 때는 물이 필요합니다!\\n\\n&a출력 포트&r는 "
        "재처리된 재료를 내보냅니다. 우클릭해 손으로 꺼내거나 파이프를 연결해 자동화할 수 있습니다."
    ],
    ("extreme_reactors", "quest.3F9D553C9FA64F2A.quest_desc"): [
        "원자로는 원하는 크기로 만들 수 있는 멀티블록 구조입니다!\\n\\n&a기본 원자로 부품&r으로 "
        "만들 수 있는 최대 크기는 5x5x5입니다.\\n\\n&e강화 원자로 부품&r으로는 최대 "
        "32x32x48 크기까지 만들 수 있습니다. 원자로의 전체 출력에는 많은 변수가 영향을 "
        "주므로 직접 실험해 보세요!\\n\\n&l전체적인 팁&r:\\n\\n원자로가 높을수록 "
        "연료봉이 많아져 더 많은 연료를 저장하고 태울 수 있으며, 총 전력도 늘어납니다. 대신 "
        "&c연소율&r도 높아집니다.\\n\\n원자로를 넓히되 연료봉 수를 늘리지 않으면 효율이 "
        "높아져 전체 연료 소비량이 줄어듭니다."
    ],
    ("extreme_reactors", "quest.4415C9F8DA2D7E68.quest_desc"): [
        "시아나이트로 터빈의 핵심인 &9터빈 제어기&r를 만들 수 있습니다.\\n\\n터빈도 "
        "원자로처럼 멀티블록 구조입니다! &d능동 냉각&r 원자로에서 만든 &7증기&r를 받아 "
        "엄청난 양의 전력을 생성합니다. 첫 터빈을 만들려면 몇 가지 부품이 더 필요합니다."
        "\\n\\n참고: 기본 터빈 부품으로 만들 수 있는 최대 크기는 5x5x10입니다. 더 큰 "
        "터빈을 만들려면 &a강화 터빈 부품&r을 사용해야 합니다."
    ],
    ("extreme_reactors", "quest.4745152F6FF242B3.quest_subtitle"): (
        "아끼면 부족하지 않다... 뭐, 그런 말이죠"
    ),
    ("extreme_reactors", "quest.476755275B948A5F.title"): "능동 냉각 원자로 건설하기",
    ("extreme_reactors", "quest.476755275B948A5F.quest_desc"): [
        "원자로로 물 같은 &b냉각재&r를 가열해 &b증기&r 같은 &b기체&r를 만들 수도 "
        "있습니다.\\n\\n이렇게 하려면 강화 원자로를 건설해야 합니다. 3x3x3 원자로와 같은 "
        "방식으로 짓되, 모든 부품을 &a강화 원자로 부품&r으로 사용하세요. 3x3x3보다 크게 "
        "짓는 것도 권장합니다.\\n\\n냉각재를 넣으려면 &9Forge 유체 포트&r가 필요합니다. "
        "물 같은 유체를 원자로에 넣고 생성된 증기를 내보내는 데에도 이 포트를 사용합니다."
        "\\n\\n원한다면 &aMekanism 유체 포트&r를 사용해 유체 증기를 Mekanism의 화학 증기로 "
        "바꿔 내보낼 수 있습니다."
    ],
    ("extreme_reactors", "quest.4FA6BEA4E646B742.quest_subtitle"): "단단한 탄소",
    ("extreme_reactors", "quest.5A615BB74A5CD332.title"): (
        "루디크라이트 \\& 리디큘라이트"
    ),
    ("extreme_reactors", "quest.5914D015D8543875.quest_desc"): [
        "&a유체화기&r는 3가지 방식으로 작동합니다. 고체 하나를 유체로 만들거나, 고체 "
        "2개를 결합해 유체로 만들거나, 유체 2개를 결합해 새 유체를 만들 수 있습니다. "
        "사용하는 &a주입기&r 종류에 따라 작동 방식이 달라집니다.\\n\\n예를 들어 "
        "&d블루토늄&r 하나를 유체로 바꾸려면 &a고체 주입기&r 1개를 사용합니다."
        "\\n\\n고체 두 개를 결합하려면 &a고체 주입기&r 2개로 멀티블록을 만드세요."
        "\\n\\n유체 두 개를 결합하려면 &9유체 주입기&r 2개를 사용하세요.\\n\\n처음에는 "
        "복잡해 보이지만 진행에 꼭 필요합니다. 예를 들어 마젠타이트를 유체화기에서 먼저 "
        "유체로 바꾼 뒤, 루디크라이트와 함께 &a재처리기&r로 보내 리디큘라이트를 만듭니다."
    ],
    ("extreme_reactors", "quest.5AD80D3242DD3F60.quest_desc"): [
        "모드에서 얻기 가장 어려운 재료 중 하나입니다!\\n\\n"
        "&6ATM의 별&r을 만드는 데에도 사용합니다!"
    ],
    ("extreme_reactors", "quest.67AFCBCE7AAC3089.title"): "터빈 축 만들기",
    ("extreme_reactors", "quest.4AD8363D7359A072.quest_desc"): [
        "가장 작은 수동 냉각 원자로인 &93x3x3&r 원자로를 만들어 보겠습니다. "
        "퀘스트 요구 사항에 표시된 수량이 이 원자로 하나를 만드는 데 정확히 필요한 양입니다."
        "\\n\\n먼저 원자로 외장으로 3x3x3 틀을 만드세요. 아래쪽 면 중앙에는 원자로 외장 "
        "하나를 더 놓으면 됩니다. 각 바깥쪽 벽에는 능동 전력 탭이나 고체 반입출 포트 같은 "
        "&9원자로 부품&r이 하나씩 있어야 합니다.",
        "{@pagebreak}",
        "모든 원자로에는 &6원자로 제어기&r가 정확히 1개 필요하며, 보통 앞쪽 벽 중앙에 "
        "놓습니다. 그다음 멀티블록 중앙에 &a연료봉&r 1개를 놓고, 그 위의 윗면에 "
        "&e제어봉&r 1개를 놓으세요.\\n\\n폐기물을 넣고 꺼내려면 &9원자로 고체 반입출 "
        "포트&r가 필요합니다. 이번 구조에서는 왼쪽과 오른쪽에 하나씩 놓으세요."
        "\\n\\n전력을 꺼내려면 뒤쪽 벽 중앙에 &c능동 전력 탭&r을 놓습니다. 이 부품까지 "
        "놓으면 원자로가 완성됩니다! 이제 제어기를 우클릭해 화면을 열고 원자로를 켤 수 "
        "있습니다!\\n\\n참고: &a기본 원자로 부품&r으로 만들 수 있는 가장 큰 원자로는 "
        "5x5x5입니다. 더 큰 원자로를 만들려면 &e강화 원자로 부품&r이 필요합니다.",
        "{@pagebreak}",
        "3x3x3 원자로는 다음과 같은 모습입니다:\\n",
        "{image:atm:textures/questpics/extremereactors/3x3sample.png width:150 height:150 align:1}",
    ],
    ("extreme_reactors", "quest.67AFCBCE7AAC3089.quest_desc"): [
        "터빈을 회전시키려면 다음 &c필수&r 부품이 필요합니다:\\n\\n"
        "- &9회전자 베어링&r은 터빈 축 한쪽 끝에 놓습니다. 어느 면에든 놓을 수 있지만, "
        "축이 뻗어 나갈 방향을 결정합니다. 보통 아래쪽 면 중앙에 놓습니다.\\n\\n"
        "- &e회전자 축&r은 회전자 베어링에서 반대쪽 면의 터빈 외장 블록 하나까지 이어져 "
        "터빈의 축을 이룹니다.\\n\\n"
        "- &9회전자 날개&r는 회전자를 돌립니다. 회전자 축에 붙이며 여러 블록 길이로 만들 "
        "수 있습니다. 날개마다 처리할 수 있는 증기량이 정해져 있으므로 원자로의 증기 생산량에 "
        "맞춰 필요한 수를 결정하세요.\\n\\n"
        "아래는 위쪽에 납 터빈 코일을 놓은 수직 축 터빈의 예시입니다.\\n",
        "{image:atm:textures/questpics/extremereactors/maxbasicturbine.png width:100 height:150 align:1}",
    ],
    ("extreme_reactors", "quest.69642A3618E86DED.quest_desc"): [
        "&a재처리기&r의 틀을 만들려면 외장이 많이 필요합니다. 즉, 시아나이트도 많이 "
        "필요합니다.\\n\\n가로 3블록, 세로 3블록, 높이 7블록인 속이 빈 구조를 만드세요. "
        "이것이 틀입니다.\\n\\n제대로 만들었다면 아래쪽 면과 위쪽 면 중앙에 각각 빈자리가 "
        "하나 생깁니다. 수직 면에는 &a재처리기 유리&r나 전력 포트, 제어기 같은 필수 "
        "&a재처리기&r 부품을 놓을 수 있습니다.\\n\\n틀의 모습은 다음 페이지에서 확인하세요!",
        "{@pagebreak}",
        "재처리기 멀티블록의 틀입니다.\\n",
        "{image:atm:textures/questpics/extremereactors/reprocessorframe.png width:100 height:175 align:1}",
        "{@pagebreak}",
        "완성된 재처리기입니다:\\n",
        "{image:atm:textures/questpics/extremereactors/reprocessorfull.png width:100 height:150 align:1}",
    ],
    ("extreme_reactors", "quest.7C4D8AA107780795.quest_desc"): [
        "&a유체화기&r에서 &d블루토늄&r과 &e옐로륨&r을 결합하면 &2베르데륨을 "
        "만들 수 있습니다.\\n\\n&2베르데륨&r을 원자로 연료로 쓰면 반응물인 "
        "&c로시나이트&r가 생성됩니다. 꼭 필요한 재료입니다!\\n\\n&2베르데륨&r을 "
        "연료로 쓰려면 원자로에 &c연료 주입 포트&r를 설치해야 합니다.\\n\\n참고: "
        "원자로에 들어 있는 기존 연료를 비우거나, 이 용도의 새 원자로를 만들어야 할 수 있습니다."
    ],
    ("extreme_reactors", "quest.7E07C5A6FA6B6B1F.quest_desc"): [
        "완성된 &a재처리기&r에 전력, 물, &9시아나이트&r를 공급하면 "
        "&d블루토늄&r을 만들 수 있습니다.",
        "",
        "블루토늄은 원자로 연료로 사용할 수 있으며, 연소 후에는 &9마젠타이트&r라는 "
        "폐기물을 생성합니다.",
    ],
    ("extreme_reactors", "quest.7C4E4793DA887DE4.quest_desc"): [
        "원조 모드인 &eBig Reactors&r를 바탕으로 만든 &aExtreme Reactors&r에서는 원하는 "
        "크기의 멀티블록 원자로를 만들 수 있습니다!\\n\\n핵심 재료는 우라늄입니다. "
        "시작하려면 우라늄과 많은 양의 석탄·철을 준비하세요.\\n\\n진행 방법을 모르겠다면 "
        "&aExtreme 가이드&r를 참고하세요!"
    ],
    ("extreme_reactors", "quest.75AD0CEBC1335915.quest_desc"): [
        "&d원자로 제어기&r는 원자로의 핵심입니다. 원자로가 완성되면 제어기를 우클릭해 "
        "화면을 열 수 있습니다.\\n\\n&9수동 냉각&r 원자로와 &e능동 냉각&r 원자로는 "
        "서로 다른 화면을 사용합니다. 수동 냉각 원자로는 연료를 태워 전력을 직접 생성합니다. "
        "능동 냉각 원자로는 발생한 열로 냉각재를 증기로 바꾸고, 그 증기를 터빈으로 보내 "
        "전력을 생성합니다.\\n\\n수동 냉각 원자로 화면에서는 작동 상태와 폐기물 배출 모드를 "
        "확인하고 전환할 수 있습니다. 온도, FE/t 생산량, 틱당 연료 소비량도 표시됩니다."
    ],
    ("extreme_reactors", "quest.775D176081DD75F5.quest_desc"): [
        "완성된 터빈 제어기를 우클릭하면 터빈 화면이 열립니다.\\n\\n이 화면에는 터빈의 "
        "모든 상태가 표시되며, 각 항목에 마우스를 올리면 자세한 설명을 볼 수 있습니다."
        "\\n\\n왼쪽 아래의 화살표 2개로 &9유량&r을 조절합니다. 이 값은 터빈으로 "
        "들어가는 가열된 증기의 양을 정합니다. 처음에는 원자로의 &d증기 생산량&r에 맞춰 "
        "설정해 보세요.",
        "{image:atm:textures/questpics/extremereactors/turbineui.png width:200 height:150 align:1}",
    ],
    ("extreme_reactors", "quest.7B4AAC741F0A6073.quest_desc"): [
        "모든 원자로에는 &9원자로 제어봉&r과 &9연료봉&r이 필요합니다. 이 부품들은 "
        "원자로의 연료 소모량을 조절합니다.\\n\\n제어봉은 원자로 윗면에 놓으며 최소 1개가 "
        "필요합니다. 제어봉과 연료봉을 늘리면 대체로 더 많은 연료를 태워 총 전력을 높일 수 "
        "있지만, 구조에 따라 연소율도 높아집니다.\\n\\n각 제어봉 아래에는 원자로 바닥까지 "
        "이어지는 연료봉이 필요합니다. 원자로 높이가 5블록이라면 제어봉마다 연료봉 3개를 "
        "아래로 이어 놓으세요.\\n\\n제어봉을 우클릭하면 삽입 비율을 조절할 수 있습니다. "
        "제어봉을 연료봉 안으로 더 깊게 삽입할수록 연료 소모량이 줄어듭니다."
    ],
}

TEXT_REPLACEMENTS = (
    ("패시브 리액터", "수동 냉각 원자로"),
    ("패시브 원자로", "수동 냉각 원자로"),
    ("패시브 냉각", "수동 냉각"),
    ("패시브", "수동 냉각"),
    ("활성 냉각", "능동 냉각"),
    ("냉각되는 원자로", "능동 냉각 원자로"),
    ("리액터", "원자로"),
    ("재처리 장치", "재처리기"),
    ("유동화 장치", "유체화기"),
    ("액체화 장치", "유체화기"),
    ("액체화기", "유체화기"),
    ("Fluidizer", "유체화기"),
    ("컨트롤러", "제어기"),
    ("전력 추출기", "전력 탭"),
    ("전원 포트", "전력 포트"),
    ("액세스 포트", "반입출 포트"),
    ("단단한 반입출", "고체 반입출"),
    ("단단한 주입기", "고체 주입기"),
    ("액체 주입기", "유체 주입기"),
    ("액체 포트", "유체 포트"),
    ("액체", "유체"),
    ("케이싱", "외장"),
    ("연료 막대", "연료봉"),
    ("제어 막대", "제어봉"),
    ("사이아나이트", "시아나이트"),
    ("청록색 시아나이트", "시아나이트"),
    ("마그네타이트", "마젠타이트"),
    ("냉각수", "냉각재"),
    ("흐름 속도", "유량"),
    ("시작 포인트", "기준값"),
    ("오른손으로 클릭", "우클릭"),
    ("오른손 클릭", "우클릭"),
    ("오른클릭", "우클릭"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("칼날", "날개"),
    ("블레이드", "날개"),
    ("홀드하고", "저장하고"),
    ("현재 힘 수준", "현재 에너지 수준"),
    ("엄청난 양의 힘", "엄청난 양의 전력"),
    ("전체적인 힘", "총 전력"),
    ("최대한의 힘", "최대 전력"),
    ("힘을 출력", "전력을 출력"),
    ("힘을 생산", "전력을 생산"),
    ("힘을 생성", "전력을 생성"),
    ("힘이 필요", "전력이 필요"),
    ("증기 생산율", "증기 생산량"),
    ("작업 화면", "Task Screen"),
)

FORBIDDEN_ARTIFACTS = (
    "패시브",
    "활성 냉각",
    "재처리 장치",
    "유동화",
    "액체화",
    "Fluidizer",
    "컨트롤러",
    "전력 추출기",
    "전원 포트",
    "액세스 포트",
    "단단한 주입기",
    "사이아나이트",
    "마그네타이트",
    "냉각수",
    "오른손",
    "오른클릭",
    "연료 막대",
    "제어 막대",
    "홀드",
    "something",
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


def normalize_scalar(value: str) -> str:
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    return value


def normalize_value(value: object) -> object:
    if isinstance(value, str):
        return normalize_scalar(value)
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    raise TypeError(f"지원하지 않는 퀘스트 값: {type(value).__name__}")


def scalar_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value for text in scalar_strings(item)]
    return []


def normalize() -> dict[str, object]:
    reviewed = 0
    changed = 0
    for chapter in CHAPTERS:
        root = QUEST_ROOT / chapter
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        for key, source in english.items():
            translated = normalize_value(KEY_OVERRIDES.get((chapter, key), korean[key]))
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
    errors: list[str] = []
    untranslated: list[str] = []
    reviewed = 0
    for chapter in CHAPTERS:
        root = QUEST_ROOT / chapter
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        if list(english) != list(korean):
            errors.append(f"키 또는 순서 불일치: {chapter}")
        for key, source in english.items():
            target = korean.get(key)
            errors.extend(family_goal.validate_value(key, source, target))
            if source == target and (chapter, key) not in ALLOWED_EXACT_KEYS:
                untranslated.append(f"{chapter}:{key}")
            for text in scalar_strings(target):
                artifacts = [word for word in FORBIDDEN_ARTIFACTS if word in text]
                if artifacts:
                    errors.append(
                        f"기계번역 잔재: {chapter}:{key}: {', '.join(artifacts)}"
                    )
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
    parser.add_argument("command", choices=("normalize", "verify"))
    args = parser.parse_args()
    if args.command == "normalize":
        result = normalize()
        status = 0
    else:
        result, status = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
