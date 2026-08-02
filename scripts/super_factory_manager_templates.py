#!/usr/bin/env python3
"""Super Factory Manager의 게임 내 SFML 예제를 번역하고 검증한다."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from pathlib import Path

import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root


JAR_PREFIX = "Super Factory Manager (SFM)-MC1.21.1-"
SOURCE_PREFIX = "assets/sfm/template_programs/"
WORK_ROOT = PROJECT_ROOT / "working/super_factory_manager/templates"
ENGLISH_ROOT = WORK_ROOT / "en_us"
KOREAN_ROOT = WORK_ROOT / "ko_kr"
OUTPUT_ROOT = (
    PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/sfm/template_programs"
)
EXCLUDED_FILES = {"changelog.sfml"}
PRESERVED_COMMENT_FILES = {"thank_you.sfml"}
PRESERVED_COMMENT_BODIES = {
    '#the_bumblezone:essence/calming_arena/drowned_bonus_held_item"',
    '#the_bumblezone:essence/knowing/block_entity_forced_highlighting"',
    "#the_bumblezone:essence/life/grow_plants",
    'INPUT FROM "storage a"',
    'INPUT FROM "storage b"',
    "a              a                 a",
    "| 5 stone |    | 5 stone |    | 10 stone |",
}

NAME_TRANSLATIONS = {
    "A simple program": "간단한 프로그램",
    "AE2 Inscribers": "AE2 각인기",
    "Empty Slots": "빈 슬롯",
    "Filtering": "필터링",
    "Forget": "입력 초기화",
    "Furnace Manager": "화로 관리자",
    "IF statements": "IF 명령문",
    "Known issues": "알려진 문제",
    "Limits": "수량 제한",
    "Redstone item movement": "레드스톤 아이템 이동",
    "Redstone signals": "레드스톤 신호",
    "Fluids and other resource types": "유체 및 기타 자원 유형",
    "Round Robin": "라운드 로빈",
    "Slots and sides": "슬롯과 면",
    "Tag Matching": "태그 일치",
    "Thank you!": "감사합니다!",
    "Timer triggers": "타이머 트리거",
}

COMMENT_TRANSLATIONS = {
    "on their own, input statements do nothing": "입력 명령문만으로는 아무 작업도 하지 않습니다",
    "there is no item buffer": "별도의 아이템 버퍼는 없습니다",
    "all the magic happens here": "실제 이동은 여기에서 이루어집니다",
    "labels:": "라벨:",
    "logic, engineering, calculation, silicon, last => inscribers": (
        "logic, engineering, calculation, silicon, last => 각인기"
    ),
    "materials, results => chests": "materials, results => 상자",
    "There's a partially filled inscriber.": "일부 재료만 들어 있는 각인기가 있습니다.",
    "We want to shuffle ingredients to make sure there isn't a full craft": (
        "완성 가능한 재료 조합이 여러 각인기에 나뉘어 있지 않도록 재료를 다시 모읍니다"
    ),
    "that is improperly distributed.": "잘못 분산된 상태를 정리합니다.",
    "This trigger interval should be longer than the time it takes": (
        "이 트리거 간격은 한 번의 제작에 걸리는 시간보다 길어야 합니다"
    ),
    "to process a single craft so that SFM doesn't sabotage the crafting": (
        "그래야 SFM이 제작에 충분한 재료가 든 각인기에서 재료를 빼내"
    ),
    "process by pulling out ingredients from inscribers that have enough.": (
        "제작을 방해하지 않습니다."
    ),
    "You can add EMPTY SLOTS IN before the labels to have SFM only insert into empty slots": (
        "라벨 앞에 EMPTY SLOTS IN을 붙이면 SFM이 빈 슬롯에만 넣습니다"
    ),
    "This should be useful for minimizing lag when outputting to large full inventories": (
        "가득 찬 대형 인벤토리로 출력할 때 렉을 줄이는 데 유용합니다"
    ),
    "Optional: run an infrequent condensing pass to stack items": (
        "선택 사항: 가끔 아이템을 합치는 정리 작업을 실행합니다"
    ),
    "basic filtering with limits": "수량 제한을 사용한 기본 필터링",
    "trailing comma is fine": "마지막 쉼표를 써도 됩니다",
    "use an asterisk to fuzzy match": "별표를 사용하면 부분 일치로 검색합니다",
    "quoted patterns use full regex": "따옴표로 감싼 패턴은 전체 정규식을 사용합니다",
    'without quotes, "*" gets converted to ".*"': (
        '따옴표가 없으면 "*"가 ".*"로 변환됩니다'
    ),
    "this is shorter, I prefer it": "이쪽이 더 짧아서 편리합니다",
    "you can exclude items too": "아이템을 제외할 수도 있습니다",
    "note that EXCEPT is a statement-level modifier": (
        "EXCEPT는 명령문 전체에 적용되는 한정자입니다"
    ),
    "iron_block and copper_block will both be excluded": (
        "iron_block과 copper_block이 모두 제외됩니다"
    ),
    'the "a" input is still active!!!': '"a" 입력이 아직 활성 상태입니다!!!',
    "or just": "또는 간단히",
    'only the "c" input is active :D': '"c" 입력만 활성 상태입니다 :D',
    'three inventories, all labelled "a"': '인벤토리 세 개에 모두 "a" 라벨이 지정되어 있습니다',
    "every a has = 5 stone    - FALSE (not all of them do!)": (
        "every a has = 5 stone    - FALSE (모든 인벤토리가 그렇지는 않습니다!)"
    ),
    'each a has >= 5 stone    - TRUE (alias for "every")': (
        'each a has >= 5 stone    - TRUE ("every"의 별칭)'
    ),
    "some a has eq 5 stone    - TRUE": "some a has eq 5 stone    - TRUE",
    "one a has = 5 stone       - FALSE (more than one does!)": (
        "one a has = 5 stone       - FALSE (하나보다 많습니다!)"
    ),
    "lone a has = 5 stone      - FALSE (more than zero or one does!)": (
        "lone a has = 5 stone      - FALSE (조건을 만족하는 인벤토리가 하나보다 많습니다!)"
    ),
    "overall a has eq 5 stone - FALSE (there are 20 stone in total, not 5)": (
        "overall a has eq 5 stone - FALSE (전체 돌은 총 20개이며 5개가 아닙니다)"
    ),
    "a has eq 5 stone           - FALSE (default behaviour is 'overall')": (
        "a has eq 5 stone           - FALSE (기본 동작은 'overall'입니다)"
    ),
    "Official SFM Discord:": "SFM 공식 Discord:",
    "Official SFM issue tracker:": "SFM 공식 문제 추적기:",
    "JEI support is missing from some versions": "일부 버전에는 JEI 지원이 없습니다",
    "Sometimes managers stop working for 'no reason'": (
        "가끔 공장 관리자가 '이유 없이' 작동을 멈춥니다"
    ),
    '"Rebuild cable network" gui button to try fix single': (
        '하나만 고치려면 GUI의 "케이블 네트워크 재구축" 버튼을 눌러 보세요'
    ),
    '"/sfm bust_cable_network_cache" to try fix all': (
        '모두 고치려면 "/sfm bust_cable_network_cache" 명령어를 실행해 보세요'
    ),
    "If it happens once, it will probably come back :(": (
        "한 번 발생했다면 다시 발생할 가능성이 높습니다 :("
    ),
    "I have no idea why this happens": "이 문제가 발생하는 이유는 아직 밝혀지지 않았습니다",
    "If you can reproduce this, pls tell me how": (
        "재현할 수 있다면 재현 방법을 알려 주세요"
    ),
    "outputting to composters (1.20.3+) without specifying a side": (
        "면을 지정하지 않고 퇴비통(1.20.3 이상)으로 출력하면"
    ),
    "will skip the check for if the item is compostable": (
        "아이템을 퇴비로 만들 수 있는지 확인하지 않아"
    ),
    "turning the composter into a trash can": "퇴비통이 쓰레기통처럼 작동합니다",
    "Sorry for any inconveniences :(": "불편을 드려 죄송합니다 :(",
    "This is hard to explain since there's so many variations": (
        "경우의 수가 많아 한 번에 설명하기 어렵습니다"
    ),
    "This is more a collection of samples than a coherent program": (
        "완성된 프로그램이라기보다 여러 예문을 모은 것입니다"
    ),
    "Guess what you think each statement does, try them out on your own!": (
        "각 명령문이 어떻게 작동할지 생각한 뒤 직접 시험해 보세요!"
    ),
    "quantity and retention can both be expanded with the EACH keyword": (
        "수량과 유지 수량 모두 EACH 키워드로 자원마다 적용할 수 있습니다"
    ),
    "this only makes sense if your resource id is a pattern": (
        "자원 ID가 패턴일 때만 의미가 있습니다"
    ),
    "redstone is a keyword": "redstone은 키워드입니다",
    "I fixed it so that it can be used without quotes now :D": (
        "이제 따옴표 없이도 사용할 수 있습니다 :D"
    ),
    "this checks the redstone signal on the manager block": (
        "공장 관리자 블록에 들어오는 레드스톤 신호를 확인합니다"
    ),
    "the default resource type is sfm:item": "기본 자원 유형은 sfm:item입니다",
    "is the same as": "다음과 같습니다",
    "so if you want to move all fluids, you gotta do": (
        "모든 유체를 이동하려면 다음처럼 작성합니다"
    ),
    "this expands to INPUT sfm:fluid:*:* FROM a": (
        "이는 INPUT sfm:fluid:*:* FROM a로 확장됩니다"
    ),
    "these are equivalent": "다음 표현은 서로 같습니다",
    'older versions used to default to "minecraft" for items': (
        '이전 버전에서는 아이템 네임스페이스의 기본값이 "minecraft"였습니다'
    ),
    "this is no longer the case, since there isn't usually name conflicts": (
        "이름 충돌이 거의 없으므로 이제는 그렇지 않습니다"
    ),
    "if there are, you can just manually specify the mod id if you care": (
        "충돌한다면 필요한 경우 모드 ID를 직접 지정하면 됩니다"
    ),
    "the following resource types are supported": "다음 자원 유형을 지원합니다",
    "(this example is generated so it's always up to date)": (
        "(이 예제는 자동 생성되므로 항상 최신 상태입니다)"
    ),
    "you probably don't need round robin": "대부분은 라운드 로빈이 필요하지 않습니다",
    "instead, try retain!": "대신 retain을 사용해 보세요!",
    'don\'t put more than 1 bucket of water in each block labelled "thingy"': (
        '"thingy" 라벨이 붙은 각 블록에 물을 1양동이보다 많이 넣지 않습니다'
    ),
    "don't take the last 5 stone": "마지막 돌 5개는 가져오지 않습니다",
    "alternatively, there is some round robin support": (
        "다른 방법으로 라운드 로빈 기능을 사용할 수 있습니다"
    ),
    "it will rotate the each time the statement ticks, so it isn't the fastest": (
        "명령문이 실행될 때마다 대상을 순환하므로 가장 빠른 방식은 아닙니다"
    ),
    'instead of outputting to all blocks labelled "dest"': (
        '"dest" 라벨이 붙은 모든 블록에 출력하는 대신'
    ),
    "when this statement executes it will pick only one block": (
        "이 명령문이 실행될 때 블록 하나만 선택합니다"
    ),
    "the chosen block rotates each time this statement is executed": (
        "명령문을 실행할 때마다 선택하는 블록이 순서대로 바뀝니다"
    ),
    "instead of outputting to all the labels": "모든 라벨로 출력하는 대신",
    "one label will be chosen each time the statement executes": (
        "명령문을 실행할 때마다 라벨 하나를 선택합니다"
    ),
    "basically alternating between": "즉, 다음 두 입력을 번갈아 사용합니다",
    "and": "그리고",
    "you can omit the namespace to match all namespaces": (
        "모든 네임스페이스와 일치시키려면 네임스페이스를 생략할 수 있습니다"
    ),
    "some tags have multiple path elements": "일부 태그는 경로 요소가 여러 개입니다",
    "block tags work for items too": "블록 태그는 아이템에도 적용됩니다",
    "matching all remaining segments is possible": "남은 경로 전체와 일치시킬 수도 있습니다",
    "should match:": "다음 태그와 일치합니다:",
    "combine with other stuff too": "다른 조건과 함께 사용할 수도 있습니다",
    "you can exclude tags as well": "태그를 제외할 수도 있습니다",
    "there is an implicit sfm:item:*:* here": "여기에는 sfm:item:*:*가 암시되어 있습니다",
    "inputted items will have ores/* and will not have needs_stone_tool": (
        "입력 아이템은 ores/* 태그가 있고 needs_stone_tool 태그가 없습니다"
    ),
    "WITHOUT will negate the entire expression": "WITHOUT는 식 전체를 부정합니다",
    "this will input stuff that doesn't have both tags": (
        "두 태그를 모두 갖지 않은 아이템을 입력합니다"
    ),
    "which is not the same as": "다음 표현과는 다릅니다",
    'Note that EXCEPT (see "Filtering" example) is statement-wide.': (
        'EXCEPT는 명령문 전체에 적용됩니다("필터링" 예제 참조).'
    ),
    "EXCEPT does not support WITH clauses.": "EXCEPT는 WITH 절을 지원하지 않습니다.",
    "There is no statement-wide exclusion for WITH clauses.": (
        "WITH 절에는 명령문 전체에 적용되는 제외 기능이 없습니다."
    ),
    "The manager's internal clock starts at zero when placed": (
        "공장 관리자를 설치하면 내부 시계가 영에서 시작합니다"
    ),
    "It is also randomly initialized after being unloaded": (
        "청크가 언로드되었다가 다시 로드되면 임의 값으로 초기화됩니다"
    ),
    "Sometimes you may want more control": "때로는 실행 시점을 더 세밀하게 제어해야 합니다",
    "Instead of the manager's internal clock, you can use the world clock to choose when to tick": (
        "공장 관리자의 내부 시계 대신 월드 시계로 실행 시점을 정할 수 있습니다"
    ),
    "You can also add an offset": "오프셋을 더할 수도 있습니다",
    "manager clock": "관리자 시계",
    "global clock": "월드 시계",
    "There is also a shorthand notation": "축약 표기법도 있습니다",
    "Don't mistake this for math lol": "수학식과 혼동하지 마세요",
    "You can mix and match": "여러 표기법을 함께 사용할 수 있습니다",
}

NAME_RE = re.compile(r'^(?P<indent>\s*)(?P<keyword>name)\s+"(?P<name>[^"]+)"\s*$', re.I)
COMMENT_RE = re.compile(r"^(?P<prefix>.*?)(?P<marker>-{2,})(?P<body>.*)$")
PROTECTED_TOKEN_RE = re.compile(
    r"https?://\S+|#[A-Za-z0-9_:*./-]+|(?:[A-Za-z0-9_*]+:)+[A-Za-z0-9_*./-]+|"
    r"(?<![A-Za-z0-9_])(?:EMPTY|SLOTS|IN|EACH|EXCEPT|WITH|WITHOUT|AND|NOT|FORGET|"
    r"TRUE|FALSE|RETAIN|INPUT|OUTPUT|FROM|TO)(?![A-Za-z0-9_])|"
    r"(?:>=|<=|==|=|>|<)|\d+(?:[.+-]\d+)*"
)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def split_ending(line: str) -> tuple[str, str]:
    for ending in ("\r\n", "\n", "\r"):
        if line.endswith(ending):
            return line[: -len(ending)], ending
    return line, ""


def translate_line(filename: str, raw_line: str) -> str:
    line, ending = split_ending(raw_line)
    match = NAME_RE.fullmatch(line)
    if match:
        source_name = match.group("name")
        target_name = NAME_TRANSLATIONS[source_name]
        return (
            f'{match.group("indent")}{match.group("keyword")} "{target_name}"{ending}'
        )

    comment = COMMENT_RE.fullmatch(line)
    if not comment or filename in PRESERVED_COMMENT_FILES:
        return raw_line
    body = comment.group("body")
    stripped = body.strip()
    if (
        not stripped
        or stripped.startswith(("http://", "https://"))
        or stripped in PRESERVED_COMMENT_BODIES
    ):
        return raw_line
    translated = COMMENT_TRANSLATIONS[stripped]
    leading = body[: len(body) - len(body.lstrip())]
    trailing = body[len(body.rstrip()) :]
    return (
        f'{comment.group("prefix")}{comment.group("marker")}'
        f"{leading}{translated}{trailing}{ending}"
    )


def find_jar() -> Path:
    return family_goal.find_jar(resolve_source_root(), JAR_PREFIX)


def prepare(force: bool) -> dict[str, object]:
    jar = find_jar()
    if ENGLISH_ROOT.exists() and not force:
        raise FileExistsError(
            "영어 원본이 이미 있습니다. 다시 만들려면 --force를 사용하세요."
        )
    if ENGLISH_ROOT.exists():
        shutil.rmtree(ENGLISH_ROOT)
    ENGLISH_ROOT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(jar) as archive:
        names = sorted(
            name
            for name in archive.namelist()
            if name.startswith(SOURCE_PREFIX) and name.endswith(".sfml")
        )
        for name in names:
            (ENGLISH_ROOT / Path(name).name).write_bytes(archive.read(name))
    report = {
        "jar": jar.name,
        "source_files": len(names),
        "selected_files": len(names) - len(EXCLUDED_FILES),
        "excluded": {
            "changelog.sfml": "과거 버전 변경 기록이며 현재 기능 안내가 아니므로 제외",
        },
    }
    write_json(WORK_ROOT / "template_inventory.json", report)
    return report


def normalize() -> dict[str, object]:
    if KOREAN_ROOT.exists():
        shutil.rmtree(KOREAN_ROOT)
    KOREAN_ROOT.mkdir(parents=True, exist_ok=True)
    translated_names = 0
    translated_comments = 0
    for source in sorted(ENGLISH_ROOT.glob("*.sfml")):
        if source.name in EXCLUDED_FILES:
            continue
        raw_lines = source.read_bytes().decode("utf-8").splitlines(keepends=True)
        target_lines: list[str] = []
        for line in raw_lines:
            target = translate_line(source.name, line)
            target_lines.append(target)
            if NAME_RE.fullmatch(split_ending(line)[0]):
                translated_names += 1
            elif target != line:
                translated_comments += 1
        (KOREAN_ROOT / source.name).write_bytes("".join(target_lines).encode("utf-8"))
    report = {
        "files": len(list(KOREAN_ROOT.glob("*.sfml"))),
        "translated_names": translated_names,
        "translated_comments": translated_comments,
        "preserved_sponsor_comments": "thank_you.sfml",
        "bundled_korean_reused_without_review": 0,
    }
    write_json(WORK_ROOT / "template_normalization.json", report)
    return report


def protected_tokens(text: str) -> list[str]:
    return PROTECTED_TOKEN_RE.findall(text)


def verify() -> tuple[dict[str, object], int]:
    selected = sorted(
        path for path in ENGLISH_ROOT.glob("*.sfml") if path.name not in EXCLUDED_FILES
    )
    targets = sorted(KOREAN_ROOT.glob("*.sfml"))
    errors: list[str] = []
    if [path.name for path in selected] != [path.name for path in targets]:
        errors.append("영어 원본과 한국어 산출물의 파일 목록이 다릅니다.")

    code_lines = 0
    checked_lines = 0
    for source in selected:
        target = KOREAN_ROOT / source.name
        if not target.is_file():
            continue
        source_lines = source.read_bytes().decode("utf-8").splitlines(keepends=True)
        target_lines = target.read_bytes().decode("utf-8").splitlines(keepends=True)
        if len(source_lines) != len(target_lines):
            errors.append(f"줄 수 불일치: {source.name}")
            continue
        for number, (source_line, target_line) in enumerate(
            zip(source_lines, target_lines, strict=True), start=1
        ):
            checked_lines += 1
            expected = translate_line(source.name, source_line)
            if target_line != expected:
                errors.append(f"검수된 번역과 불일치: {source.name}:{number}")
            source_body = split_ending(source_line)[0]
            if not NAME_RE.fullmatch(source_body) and not COMMENT_RE.fullmatch(
                source_body
            ):
                code_lines += 1
                if source_line != target_line:
                    errors.append(f"SFML 코드 변경: {source.name}:{number}")
            if protected_tokens(source_line) != protected_tokens(target_line):
                errors.append(f"보호 토큰 불일치: {source.name}:{number}")

    report = {
        "files_checked": len(selected),
        "lines_checked": checked_lines,
        "code_lines_preserved": code_lines,
        "excluded_changelog": "changelog.sfml",
        "bundled_korean_reused_without_review": 0,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "template_validation.json", report)
    return report, 0 if not errors else 1


def build() -> dict[str, object]:
    report, code = verify()
    if code:
        raise RuntimeError("SFML 예제 검증이 통과하지 않았습니다.")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for stale in OUTPUT_ROOT.glob("*.sfml"):
        if stale.name not in {path.name for path in KOREAN_ROOT.glob("*.sfml")}:
            stale.unlink()
    for source in KOREAN_ROOT.glob("*.sfml"):
        shutil.copyfile(source, OUTPUT_ROOT / source.name)
    result = {"files_built": report["files_checked"], "output": str(OUTPUT_ROOT)}
    write_json(WORK_ROOT / "template_build.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "normalize", "verify", "build"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.action == "prepare":
        result = prepare(args.force)
        code = 0
    elif args.action == "normalize":
        result = normalize()
        code = 0
    elif args.action == "build":
        result = build()
        code = 0
    else:
        result, code = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
