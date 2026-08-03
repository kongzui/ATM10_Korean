#!/usr/bin/env python3
"""SecurityCraft 언어 파일과 관련 FTB Quests를 현재 영어 원문으로 전면 재검수한다."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import ars_family
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "securitycraft"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
LANG_ROOT = WORK_ROOT / "securitycraft"
QUEST_ROOT = WORK_ROOT / "quests/related"
BUNDLED_PATH = LANG_ROOT / "bundled_ko_kr.json"
CACHE_PATH = PROJECT_ROOT / "temp/securitycraft_candidate_cache_v1.json"
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[.,/xX×]\d+)*")
URL = re.compile(r"https?://\S+")

ALLOWED_ORIGINALS = {
    "SecurityCraft",
    "SecurityCraft Manual",
    "Discord",
    "Patreon",
    "Reddit",
    "GitHub",
    "Smart Module",
    "Storage Module",
    "Disguise Module",
    "Whitelist Module",
    "Blacklist Module",
    "Redstone Module",
    "Harming Module",
}

EXACT_SOURCE = {
    "SecurityCraft": "SecurityCraft",
    "SecurityCraft Manual": "SecurityCraft 설명서",
    "Reinforced Stone": "강화된 돌",
    "Universal Block Reinforcer": "범용 블록 강화기",
    "Universal Block Remover": "범용 블록 강화 해제기",
    "Universal Owner Changer": "범용 소유자 변경기",
    "Universal Key Changer": "범용 열쇠 변경기",
    "Universal Block Modifier": "범용 블록 설정기",
    "Security Camera": "보안 카메라",
    "Username Logger": "사용자 이름 기록기",
    "Inventory Scanner": "인벤토리 스캐너",
    "Retinal Scanner": "망막 스캐너",
    "Keypad": "키패드",
    "Keycard Reader": "키 카드 판독기",
    "Keycard Lock": "키 카드 잠금장치",
    "Panic Button": "비상 버튼",
    "Laser Block": "레이저 블록",
    "Portable Radar": "휴대용 레이더",
    "Codebreaker": "암호 해독기",
    "Wire Cutters": "전선 절단기",
    "Taser": "전기 충격기",
    "Mine Remote Access Tool": "지뢰 원격 제어기",
    "Sentry Remote Access Tool": "센트리 원격 제어기",
    "Passcode": "암호",
    "Owner": "소유자",
    "Allowlist": "허용 목록",
    "Denylist": "차단 목록",
    "Module": "모듈",
    "Modules": "모듈",
}

EXACT_KEYS = {
    "itemGroup.securitycraft": "SecurityCraft",
    "itemGroup.securitycraft.decoration": "SecurityCraft: 장식",
    "itemGroup.securitycraft.explosives": "SecurityCraft: 폭발물",
    "itemGroup.securitycraft.technical": "SecurityCraft: 기술",
    "key.categories.securitycraft": "SecurityCraft",
    "block.securitycraft.reinforced_light_gray_terracotta": "강화된 회백색 테라코타",
    "block.securitycraft.reinforced_polished_granite_slab": (
        "강화된 윤이 나는 화강암 반 블록"
    ),
    "help.securitycraft.sc_manual.info": (
        "SecurityCraft 설명서에서는 SecurityCraft가 추가하는 모든 블록과 아이템의 기본 정보를 "
        "확인할 수 있습니다. 더 자세한 설명은 GitHub 위키에서 확인하세요: "
        "https://github.com/Geforce132/SecurityCraft/wiki."
    ),
    "help.securitycraft.block_mines.info": (
        "위장 지뢰는 다른 블록처럼 보이도록 위장한 지뢰입니다. 가까이 다가가거나 채굴하면 "
        "폭발하지만, 위장 지뢰의 소유자에게는 반응하지 않습니다."
    ),
    "help.securitycraft.block_pocket_manager.info": (
        "블록 포켓 관리자는 소유자와 허용 목록의 플레이어만 들어갈 수 있는 블록 포켓을 "
        "관리합니다. GUI에서 크기를 고른 뒤 관리자를 맨 아래층 바깥쪽에 두고 그 주위에 선택한 "
        "크기의 정육면체를 만드세요. 모서리는 강화된 조각된 수정 석영, 모서리 사이는 방향을 "
        "맞춘 강화된 수정 석영 기둥, 바닥과 벽과 천장은 블록 포켓 벽으로 만듭니다. 완성 예시는 "
        'https://i.imgur.com/opc7dqO.png 에서 확인할 수 있습니다. 구조를 완성하고 "활성화"를 '
        "누르면 설치한 모듈이 작동합니다. 자세한 내용은 범용 블록 설정기로 여는 설정 GUI를 "
        "확인하세요."
    ),
    "help.securitycraft.block_reinforcers.info": (
        "범용 블록 강화기는 여러 바닐라 블록을 SecurityCraft의 강화 블록으로 바꿉니다. 강화기를 "
        "우클릭해 바닐라 블록을 위쪽 슬롯에 넣고 GUI를 닫거나, 크리에이티브 모드가 아닐 때 "
        "강화할 블록을 강화기로 부수세요. 강화 블록을 바닐라 블록으로 되돌리려면 아래쪽 슬롯을 "
        "사용합니다. 이 기능은 2단계 강화기에서만 쓸 수 있습니다. 제작기에 변환할 블록과 강화기를 "
        "함께 넣어 자동화할 수도 있습니다. GUI에서 강화 또는 강화 해제를 선택하면 제작할 때에도 "
        "같은 작업을 수행합니다. 1단계 강화기는 300회, 2단계 강화기는 2700회 사용할 수 있고, "
        "3단계 강화기는 사용 횟수가 무제한입니다."
    ),
    "help.securitycraft.briefcase.info": (
        "서류 가방은 암호로 잠기는 12칸짜리 휴대용 저장 장치입니다. 제작한 뒤 우클릭해 앞으로 "
        "사용할 4자리 암호를 설정하세요. 다시 우클릭해 암호를 입력하면 내용물을 사용할 수 "
        "있습니다. 암호를 없애거나 소유자를 바꾸려면 서류 가방을 보조 손에 들고, 주 손에 범용 "
        "열쇠 변경기 또는 범용 소유자 변경기를 든 채 우클릭하세요."
    ),
    "help.securitycraft.crystal_quartz_item.info": (
        "수정 석영은 수정 석영 블록을 만드는 데 사용합니다."
    ),
    "help.securitycraft.display_cases.info": (
        "진열장은 바닐라 아이템 액자처럼 아이템 하나를 표시하지만 아이템을 회전할 수는 없습니다. "
        "키패드처럼 암호를 입력해야 열립니다. 열린 진열장에 아이템을 들고 우클릭하면 넣을 수 "
        "있고, Shift를 누른 채 우클릭하면 꺼낼 수 있습니다. 빈손으로 우클릭하면 닫힙니다. 열린 "
        "동안에는 누구나 사용할 수 있습니다. 발광 진열장은 발광 아이템 액자처럼 어둠 속에서도 "
        "밝게 보입니다."
    ),
    "help.securitycraft.key_panel.info": (
        "키 패널은 작고 물에 잠길 수 있는 키패드입니다. 키패드와 암호로 보호된 상자, 통, 화로를 "
        "만드는 재료로도 사용합니다."
    ),
    "help.securitycraft.keypad_smoker.info": (
        "암호로 보호된 훈연기는 처음 설치할 때 암호를 설정해야 합니다. 이후 GUI에 올바른 암호를 "
        "입력하면 훈연기의 인벤토리를 열 수 있습니다."
    ),
    "help.securitycraft.lens.info": (
        "렌즈는 여러 SecurityCraft 블록의 표시 색상을 바꿉니다. 가죽 방어구처럼 렌즈와 염료를 "
        "함께 조합해 색을 입히세요. 레이저 블록의 레이저, 인벤토리 스캐너의 감지 영역, 트로피 "
        "시스템의 조준 레이저, 클레이모어의 레이저 색상을 바꿀 수 있습니다. 블록을 우클릭해 해당 "
        "슬롯에 렌즈를 넣으면 적용됩니다."
    ),
    "help.securitycraft.mine.info": (
        "지뢰는 크리퍼, 고양이, 오실롯을 제외한 개체가 밟으면 폭발합니다. 전선 절단기를 들고 "
        "지뢰를 우클릭하면 해체되어 안전하게 부술 수 있습니다. 부싯돌과 부시를 들고 우클릭하면 "
        "다시 활성화됩니다."
    ),
    "help.securitycraft.reinforced_crystal_quartz.info": (
        "강화된 수정 석영 블록은 블록 포켓을 만드는 데 사용합니다. 자세한 내용은 블록 포켓 "
        "관리자 페이지를 확인하세요."
    ),
    "help.securitycraft.reinforced_fence_gate.info": (
        "전기가 흐르는 철 울타리 문은 바닐라 울타리 문처럼 작동하지만 부술 수 없고 키패드나 "
        "인벤토리 스캐너 등으로만 열 수 있습니다. 소유자가 아닌 개체가 닿으면 피해를 받습니다."
    ),
    "help.securitycraft.sonic_security_system.info": (
        '소닉 보안 시스템은 게임 "메트로이드 프라임 2: 에코스"의 같은 이름을 가진 장치에서 '
        "영감을 받았습니다. 특정 SecurityCraft 블록을 잠가 사용하거나 상호 작용하지 못하게 "
        "합니다. 지원되는 블록을 우클릭해 시스템에 연결하고, 설치한 시스템을 우클릭해 활성화, "
        "비활성화 또는 초기화할 수 있습니다. 휴대용 음정 재생기나 소리 블록으로 근처에서 등록된 "
        "음정을 연주하면 잠긴 블록이 잠시 열립니다. 음정을 등록하려면 시스템 GUI에서 녹음을 켠 "
        "뒤 소리 블록으로 원하는 음정을 연주하고 녹음을 끄세요."
    ),
    "help.securitycraft.taser.info": (
        "전기 충격기는 스스로 충전됩니다. 우클릭해 발사하며, 맞은 개체는 10초 동안 멀미 II, "
        "구속 II, 나약함 II를 받습니다. 인벤토리에 레드스톤이 있을 때 Shift를 누른 채 우클릭하면 "
        "다음 발사의 위력이 2배가 됩니다."
    ),
    "help.securitycraft.universal_owner_changer.info": (
        "범용 소유자 변경기는 블록의 소유자를 바꿉니다. 모루에서 변경기의 이름을 새 소유자의 "
        "이름으로 바꾼 뒤 자신의 블록을 우클릭하세요. 설정에서 허용된 경우 이름을 바꾸지 않은 "
        "변경기로 소유자가 없는 블록을 우클릭해 소유권을 등록할 수도 있습니다."
    ),
}

REPLACEMENTS = (
    ("블럭", "블록"),
    ("유저", "사용자"),
    ("인벤 ", "인벤토리 "),
    ("패스코드", "암호"),
    ("화이트리스트", "허용 목록"),
    ("블랙리스트", "차단 목록"),
    ("허용리스트", "허용 목록"),
    ("차단리스트", "차단 목록"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("왼쪽 클릭", "좌클릭"),
    ("웅크린 상태에서", "Shift를 누른 채"),
    ("강화 된", "강화된"),
    ("업그레이드 모듈", "업그레이드 모듈"),
    ("데미지", "피해"),
    ("쿨다운", "재사용 대기시간"),
    ("아이템들", "아이템"),
    ("엔티티", "개체"),
    ("엔터티", "개체"),
    ("시큐리티크래프트", "SecurityCraft"),
    ("만능 블록", "범용 블록"),
    ("만능 열쇠", "범용 열쇠"),
    ("만능 소유자", "범용 소유자"),
    ("허용목록", "허용 목록"),
    ("거부목록", "차단 목록"),
    ("거부 목록", "차단 목록"),
    ("비밀번호", "암호"),
    ("재고 스캐너", "인벤토리 스캐너"),
    ("우버튼으로 클릭", "우클릭"),
    ("마우스 오른쪽을 클릭", "우클릭"),
    ("센트리 건를", "센트리 건을"),
    ("소유자과", "소유자와"),
    ("소유자을", "소유자를"),
    ("허공를", "허공을"),
    ("허용 목록를", "허용 목록을"),
    ('"모듈"를', '"모듈"을'),
    ("흡연자", "훈연기"),
    ("액세스", "접근"),
    ("광산", "지뢰"),
    ("눈금 단위: 눈금 단위:", "눈금 단위:"),
)

SURFACE_BLOCKED = (
    "\u200b",
    "\ufeff",
    "블럭",
    "유저",
    "패스코드",
    "마우스 오른쪽 버튼을 클릭",
    "마우스 오른쪽 버튼으로 클릭",
    "강화 된",
    "데미지",
)


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def structurally_usable(source: str, target: str) -> bool:
    for pattern in (PLACEHOLDER, FORMAT_CODE, URL):
        if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
            return False
    if source.count("\n") != target.count("\n"):
        return False
    source_plain = FORMAT_CODE.sub("", URL.sub("", source))
    target_plain = FORMAT_CODE.sub("", URL.sub("", target))
    return not (
        Counter(NUMBER.findall(source_plain)) - Counter(NUMBER.findall(target_plain))
    )


def normalize_text(value: str) -> str:
    value = EXACT_SOURCE.get(value, value)
    value = value.replace("\u200b", "").replace("\ufeff", "")
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    value = re.sub(r"\bAllowlist\b", "허용 목록", value)
    value = re.sub(r"\bWhitelist\b", "허용 목록", value)
    value = re.sub(r"\bDenylist\b", "차단 목록", value)
    value = re.sub(r"\bBlacklist\b", "차단 목록", value)
    value = re.sub(r"\bPasscode\b", "암호", value)
    value = re.sub(r"\bCooldown\b", "재사용 대기시간", value)
    return value


def extract_bundled() -> dict[str, object]:
    mods = resolve_source_root() / "mods"
    jars = sorted(mods.glob("[[]1.21.1] SecurityCraft*.jar"))
    if len(jars) != 1:
        raise RuntimeError(f"SecurityCraft JAR을 하나로 확정하지 못했습니다: {jars}")
    with ZipFile(jars[0]) as archive:
        bundled = json.loads(archive.read("assets/securitycraft/lang/ko_kr.json"))
    write_json(BUNDLED_PATH, bundled)
    return {"jar": jars[0].name, "bundled_keys": len(bundled)}


def candidates() -> dict[str, object]:
    if not BUNDLED_PATH.is_file():
        extract_bundled()
    bundled = load_json(BUNDLED_PATH)
    english = load_json(LANG_ROOT / "en_us.json")
    cache = load_json(CACHE_PATH) if CACHE_PATH.is_file() else {}
    sources = {
        source
        for key, source in english.items()
        if isinstance(source, str)
        and LATIN_WORD.search(source)
        and (
            key.startswith("help.securitycraft.")
            or not (
                key in bundled
                and isinstance(bundled[key], str)
                and bundled[key] != source
                and structurally_usable(source, bundled[key])
            )
        )
    }
    requests = sorted(
        source for source in sources if source not in cache or cache[source] == source
    )
    failures = []
    if requests:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(ars_family.request_translation, source): source
                for source in requests
            }
            for number, future in enumerate(as_completed(futures), 1):
                source = futures[future]
                try:
                    candidate = future.result()
                    cache[source] = (
                        candidate if structurally_usable(source, candidate) else source
                    )
                    if cache[source] == source:
                        failures.append(f"구조 불일치: {source[:120]}")
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스 보고용
                    cache[source] = source
                    failures.append(f"{source[:120]}: {exc}")
                if number % 25 == 0:
                    write_json(CACHE_PATH, cache)
        write_json(CACHE_PATH, cache)
    write_json(
        LANG_ROOT / "auto_candidates_direct.json",
        {
            key: normalize_text(cache.get(source, source))
            for key, source in english.items()
        },
    )
    report = {
        "unique_strings": len(sources),
        "candidate_requests": len(requests),
        "candidate_failures": failures,
        "status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "direct_candidate_report.json", report)
    return report


def normalize() -> dict[str, object]:
    if not BUNDLED_PATH.is_file():
        extract_bundled()
    bundled = load_json(BUNDLED_PATH)
    english = load_json(LANG_ROOT / "en_us.json")
    auto = load_json(LANG_ROOT / "auto_candidates_direct.json")
    reviewed = {}
    for key, source in english.items():
        if key in EXACT_KEYS:
            reviewed[key] = EXACT_KEYS[key]
            continue
        candidate = bundled.get(key)
        if key.startswith("help.securitycraft."):
            reviewed[key] = normalize_text(str(auto[key]))
        elif (
            isinstance(source, str)
            and isinstance(candidate, str)
            and candidate != source
            and structurally_usable(source, candidate)
        ):
            reviewed[key] = normalize_text(candidate)
        else:
            reviewed[key] = normalize_text(str(auto[key]))
    write_json(LANG_ROOT / "ko_kr.json", reviewed)
    report = {"reviewed_keys": len(reviewed), "status": "complete"}
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], list[str]]:
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    errors = []
    untranslated = []
    if list(english) != list(korean):
        errors.append("키 또는 키 순서가 영어 원문과 다릅니다")
    for key in english.keys() & korean.keys():
        source = english[key]
        target = korean[key]
        if not isinstance(source, str) or not isinstance(target, str):
            errors.append(f"문자열 자료형이 아닙니다: {key}")
            continue
        if not structurally_usable(source, target):
            errors.append(f"표시 토큰 불일치: {key}")
        if (
            source == target
            and LATIN_WORD.search(source)
            and FORMAT_CODE.sub("", source) not in ALLOWED_ORIGINALS
            and not re.fullmatch(r"[A-Z0-9_+./:%() -]+", source.strip())
        ):
            untranslated.append(key)
        blocked = [token for token in SURFACE_BLOCKED if token in target]
        if blocked:
            errors.append(f"표시 품질 금지 문자열 {blocked}: {key}")
    if untranslated:
        errors.append(f"미번역 후보: {untranslated[:30]}")
    result = {
        "keys": len(english),
        "untranslated_candidates": untranslated,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", result)
    return result, errors


def audit() -> tuple[dict[str, object], list[str]]:
    mods = resolve_source_root() / "mods"
    jar = next(mods.glob("[[]1.21.1] SecurityCraft*.jar"))
    language = load_json(LANG_ROOT / "en_us.json")
    manual_keys = [key for key in language if "manual" in key.lower()]
    recipe_advancements = []
    display_literals = []
    with ZipFile(jar) as archive:
        for name in archive.namelist():
            if not name.startswith(
                "data/securitycraft/advancement/"
            ) or not name.endswith(".json"):
                continue
            recipe_advancements.append(name)
            value = json.loads(archive.read(name))
            if "display" in value:
                display_literals.append(name)
    errors = []
    if display_literals:
        errors.append(f"직접 표시 발전 과제 발견: {display_literals[:20]}")
    result = {
        "jar": jar.name,
        "manual_language_keys": len(manual_keys),
        "recipe_advancement_files": len(recipe_advancements),
        "literal_display_advancements": display_literals,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", result)
    return result, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("extract", "candidates", "normalize", "verify", "audit"),
    )
    args = parser.parse_args()
    if args.command == "extract":
        result = extract_bundled()
        errors = []
    elif args.command == "candidates":
        result = candidates()
        errors = list(result["candidate_failures"])
    elif args.command == "normalize":
        result = normalize()
        errors = []
    elif args.command == "verify":
        result, errors = verify()
    else:
        result, errors = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
