#!/usr/bin/env python3
"""Pam's HarvestCraft 2 네 모드의 표시 문구를 현재 영어 원문으로 전면 재검수해요."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "pams_harvestcraft_2"
ROOT = PROJECT_ROOT / "working" / FAMILY
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
TARGETS = {
    "pamhc2crops": "Pam's HarvestCraft 2 - Crops",
    "pamhc2foodcore": "Pam's HarvestCraft 2 - Food Core",
    "pamhc2foodextended": "Pam's HarvestCraft 2 - Food Extended",
    "pamhc2trees": "Pam's HarvestCraft 2 - Trees",
}

SOURCE_EXACT = {
    "Bakeware": "제빵 도구",
    "Batter": "튀김 반죽",
    "Cutting Board": "도마",
    "Dough": "반죽",
    "Pot": "냄비",
    "Skillet": "프라이팬",
    "Fresh Water": "민물",
    "Ground Beef": "다진 소고기",
    "Ground Chicken": "다진 닭고기",
    "Ground Fish": "다진 생선",
    "Ground Mutton": "다진 양고기",
    "Ground Pork": "다진 돼지고기",
    "Ground Rabbit": "다진 토끼고기",
    "Cooked Ground Beef": "익힌 다진 소고기",
    "Cooked Ground Chicken": "익힌 다진 닭고기",
    "Cooked Ground Fish": "익힌 다진 생선",
    "Cooked Ground Mutton": "익힌 다진 양고기",
    "Cooked Ground Pork": "익힌 다진 돼지고기",
    "Cooked Ground Rabbit": "익힌 다진 토끼고기",
    "Battered Sausage": "튀김옷 소시지",
    "Baked Alaska": "베이크드 알래스카",
    "Bangers and Mash": "뱅어스 앤 매시",
    "Bean Corn Meal": "콩 옥수수 가루",
    "Beans on Toast": "토스트에 얹은 콩",
    "Bento Box": "도시락",
    "Bratwurst": "브라트부르스트",
    "Bibimpbap": "비빔밥",
    "Calabash Crop": "호리병박 작물",
    "Cantaloupe Crop": "칸탈루프 작물",
    "Cactusfruit Crop": "선인장 열매 작물",
    "Soybean Crop": "대두 작물",
    "Soybean": "대두",
    "Soybean Seed": "대두 씨앗",
    "Tomatillo Crop": "토마티요 작물",
    "Tomatillo Seed": "토마티요 씨앗",
    "Waterchestnut Crop": "물밤 작물",
    "Zucchini Crop": "주키니 작물",
    "Sunchoke Crop": "선초크 작물",
    "Brusselsprout Crop": "방울양배추 작물",
    "Bellpepper Crop": "피망 작물",
    "Chilipepper Crop": "칠리 고추 작물",
    "Coffeebean Crop": "커피콩 작물",
    "Spiceleaf Crop": "향신료 잎 작물",
    "Tealeaf Crop": "찻잎 작물",
    "Mustard Seeds Crop": "겨자씨 작물",
    "Sesame Seeds Crop": "참깨 작물",
    "Winter Squash Crop": "겨울호박 작물",
    "Green Grape Crop": "청포도 작물",
    "Candleberry Crop": "캔들베리 작물",
    "Mulberry Crop": "오디 작물",
    "Scallion Crop": "대파 작물",
    "Dragonfruit Fruit": "용과 열매",
    "Spiderweb Fruit": "거미줄 열매",
    "Paperbark Fruit": "페이퍼바크 열매",
    "Maple Fruit": "단풍나무 수액",
}

KEY_EXACT = {
    "item.pamhc2foodcore.bakedvegetablemedlyitem": "구운 채소 모둠",
    "item.pamhc2foodcore.fishsticksitem": "생선 스틱",
    "item.pamhc2foodcore.glazedcarrotsitem": "글레이즈드 당근",
    "item.pamhc2foodcore.grilledcheeseandhamitem": "햄 치즈 토스트",
    "item.pamhc2foodcore.grilledcheeseitem": "그릴드 치즈",
    "item.pamhc2foodextended.chickenparmasanitem": "치킨 파르메산",
    "item.pamhc2foodextended.chilidogitem": "칠리도그",
    "item.pamhc2foodextended.chocolatemilkshakeitem": "초콜릿 밀크셰이크",
    "item.pamhc2foodextended.cornishpastyitem": "코니시 페이스티",
    "item.pamhc2foodextended.cornonthecobitem": "통옥수수",
    "item.pamhc2foodextended.creamofchickenitem": "치킨 크림 수프",
    "item.pamhc2foodextended.creamofmushroomitem": "버섯 크림 수프",
    "item.pamhc2foodextended.crispyricepuffbarsitem": "쌀 튀밥 바",
    "item.pamhc2foodextended.crispyricepuffcerealitem": "쌀 튀밥 시리얼",
    "item.pamhc2foodextended.deviledeggitem": "데빌드 에그",
    "item.pamhc2foodextended.dhalitem": "달 커리",
    "item.pamhc2foodextended.eggplantparmitem": "가지 파르메산",
    "item.pamhc2foodextended.espressoitem": "에스프레소",
    "item.pamhc2foodextended.generaltsochickenitem": "제너럴 쏘 치킨",
    "item.pamhc2foodextended.gingeredrhubarbtartitem": "생강 루바브 타르트",
    "item.pamhc2foodextended.gravyitem": "그레이비",
    "item.pamhc2foodextended.greenbeancasseroleitem": "껍질콩 캐서롤",
    "item.pamhc2foodextended.gritsitem": "그리츠",
    "item.pamhc2foodextended.hamandpineapplepizzaitem": "햄 파인애플 피자",
    "item.pamhc2foodextended.hashitem": "해시",
    "item.pamhc2foodextended.hazelnutcoffeeitem": "헤이즐넛 커피",
    "item.pamhc2foodextended.hushpuppiesitem": "허시 퍼피",
    "item.pamhc2foodextended.leafychickensandwichitem": "채소 치킨 샌드위치",
    "item.pamhc2foodextended.leafyfishsandwichitem": "채소 생선 샌드위치",
    "item.pamhc2foodextended.loadedbakedpotatoitem": "토핑 구운 감자",
    "item.pamhc2foodextended.misosoupitem": "미소 된장국",
    "item.pamhc2foodextended.mochicakeitem": "모치 케이크",
    "item.pamhc2foodextended.mochidessertitem": "모치 디저트",
    "item.pamhc2foodextended.mochiitem": "모치",
    "item.pamhc2foodextended.museliitem": "뮤즐리",
    "item.pamhc2foodextended.nachoesitem": "나초",
    "item.pamhc2foodextended.neapolitanicecreamitem": "나폴리탄 아이스크림",
    "item.pamhc2foodextended.oatmealraisincookiesitem": "오트밀 건포도 쿠키",
    "item.pamhc2foodextended.pastagardeniaitem": "파스타 가르데니아",
    "item.pamhc2foodextended.rawtofabbititem": "생 토파빗",
    "item.pamhc2foodextended.rawtofaconitem": "생 토파콘",
    "item.pamhc2foodextended.rawtofeakitem": "생 토피크",
    "item.pamhc2foodextended.rawtofickenitem": "생 토피켄",
    "item.pamhc2foodextended.rawtofishitem": "생 토피시",
    "item.pamhc2foodextended.rawtofuttonitem": "생 토퍼튼",
    "item.pamhc2foodextended.cookedtofabbititem": "익힌 토파빗",
    "item.pamhc2foodextended.cookedtofaconitem": "익힌 토파콘",
    "item.pamhc2foodextended.cookedtofeakitem": "익힌 토피크",
    "item.pamhc2foodextended.cookedtofickenitem": "익힌 토피켄",
    "item.pamhc2foodextended.cookedtofishitem": "익힌 토피시",
    "item.pamhc2foodextended.cookedtofuttonitem": "익힌 토퍼튼",
}

REPLACEMENTS = (
    ("Pam's HarvestCraft 2 - 작물", "Pam's HarvestCraft 2 - Crops"),
    ("Pam's HarvestCraft 2 - 과일 나무", "Pam's HarvestCraft 2 - Trees"),
    ("Pam's HarvestCraft 2 - 푸드 코어", "Pam's HarvestCraft 2 - Food Core"),
    ("Pam's HarvestCraft 2 - 식품 확장", "Pam's HarvestCraft 2 - Food Extended"),
    ("라이트 그레이", "밝은 회색"),
    ("글로우 베리", "발광 열매"),
    ("글로우베리", "발광 열매"),
    ("요리된", "익힌"),
    ("조리된", "익힌"),
    ("쇠고기", "소고기"),
    ("야채", "채소"),
    ("계란후라이", "달걀 프라이"),
    ("계란", "달걀"),
    ("요거트", "요구르트"),
    ("카라멜", "캐러멜"),
    ("애플파이", "사과 파이"),
    ("애플 ", "사과 "),
    ("Passonfruit", "패션프루트"),
    ("패스슨푸르트", "패션프루트"),
    ("패슨푸르트", "패션프루트"),
    ("데이트 ", "대추야자 "),
    ("사과젤리", "사과 젤리"),
    ("바나나파이", "바나나 파이"),
    ("치즈 케이크", "치즈케이크"),
    ("닭 튀김", "프라이드치킨"),
    ("냄비 파이", "팟 파이"),
    ("가루 반죽", "반죽"),
    ("도시락 상자", "도시락"),
    ("메들리", "모둠"),
    ("디너", "저녁 식사"),
    ("시나몬", "계피"),
    ("파인사과", "파인애플"),
    ("식용뿌리", "식용 뿌리"),
    ("부리또", "부리토"),
    ("바베큐", "바비큐"),
    ("앤쵸비", "앤초비"),
    ("소세지", "소시지"),
    ("폭행 소시지", "튀김옷 소시지"),
    ("구운 알래스카", "베이크드 알래스카"),
    ("타자", "반죽"),
    ("빵집", "제빵 도구"),
    ("땅토끼", "토끼고기"),
    ("자르기", "작물"),
    ("크롭", "작물"),
    ("보리작물", "보리 작물"),
    ("선인장과일", "선인장 열매"),
    ("브뤼셀프라우트", "방울양배추"),
    ("칠리페퍼", "칠리 고추"),
    ("향신료잎", "향신료 잎"),
    ("밤나무 작물", "물밤 작물"),
    ("호박 작물", "주키니 작물"),
    (" 과일 로그", " 열매"),
    (" 과일 기록", " 열매"),
    (" 열매 통나무", " 열매"),
    (" 과일", " 열매"),
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


def review(namespace: str, key: str, source: object, candidate: object) -> object:
    if not isinstance(source, str) or not isinstance(candidate, str):
        return candidate
    value = (
        TARGETS[namespace] if key == f"itemGroup.{namespace}" else KEY_EXACT.get(key)
    )
    if value is None:
        value = SOURCE_EXACT.get(source, candidate)
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    if source.startswith("Cantaloupe ") and value.startswith("멜론 "):
        value = value.replace("멜론 ", "칸탈루프 ", 1)
    if source == "Miso Paste":
        value = "된장"
    elif source == "Miso":
        value = "미소"
    elif source == "Mochi":
        value = "모치"
    elif source == "Rice Cake":
        value = "떡"
    elif source == "Stuffed Chili Peppers":
        value = "속을 채운 칠리 고추"
    elif source == "Stuffed Pepper":
        value = "속을 채운 피망"
    elif key == "item.pamhc2trees.peppercornitem":
        value = "통후추"
    if source.endswith(" Crop") and not value.endswith("작물"):
        value = re.sub(r"(?:자르기|크롭)$", "작물", value)
    if namespace == "pamhc2trees" and source.endswith(" Fruit"):
        value = re.sub(r"(?:과일|열매)(?: 로그| 기록)?$", "열매", value)
    return value.strip()


def normalize() -> dict[str, object]:
    rows = []
    for namespace in TARGETS:
        root = ROOT / namespace
        english = load(root / "en_us.json")
        auto = load(root / "auto_candidates.json")
        korean = {
            key: review(namespace, key, source, auto[key])
            for key, source in english.items()
        }
        write(root / "ko_kr.json", korean)
        rows.append({"namespace": namespace, "keys": len(korean)})
    related = ROOT / "quests/related"
    if related.is_dir():
        english = load(related / "en_us.json")
        auto = load(related / "auto_candidates.json")
        write(
            related / "ko_kr.json",
            {
                key: review("pamhc2foodcore", key, source, auto[key])
                for key, source in english.items()
            },
        )
    result = {
        "languages": rows,
        "existing_korean_reused": 0,
        "new_translations_reviewed": sum(row["keys"] for row in rows),
        "related_quest_keys": 0,
        "status": "complete",
    }
    write(ROOT / "normalization.json", result)
    return result


def verify_pair(namespace: str) -> tuple[dict[str, object], list[str]]:
    root = ROOT / namespace
    english, korean = load(root / "en_us.json"), load(root / "ko_kr.json")
    errors = []
    if list(english) != list(korean):
        errors.append(f"키 또는 순서 불일치: {namespace}")
    for key in english.keys() & korean.keys():
        source, target = english[key], korean[key]
        errors.extend(family_goal.validate_value(key, source, target))
        if isinstance(source, str) and isinstance(target, str):
            if Counter(NUMBER.findall(source)) != Counter(NUMBER.findall(target)):
                errors.append(f"숫자 불일치: {namespace}:{key}")
    return {"namespace": namespace, "keys": len(english)}, errors


def verify() -> tuple[dict[str, object], list[str]]:
    rows, errors = [], []
    for namespace in TARGETS:
        row, current = verify_pair(namespace)
        rows.append(row)
        errors.extend(current)
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
                        name.endswith(".json") and "/advancement" in name
                        for name in names
                    ),
                    "recipes": sum(
                        name.endswith(".json") and "/recipe" in name for name in names
                    ),
                    "guide_files": sum("guide" in name.lower() for name in names),
                }
            )
    visible_lines = []
    namespaces = tuple(f"{namespace}:" for namespace in TARGETS)
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json", ".snbt"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            lowered = line.lower()
            if any(namespace in lowered for namespace in namespaces) and any(
                token in lowered
                for token in ("display", "tooltip", "lore", "text", ".name(")
            ):
                visible_lines.append(
                    f"{path.relative_to(instance).as_posix()}:{number}:{line.strip()}"
                )
    result = {
        "jars": rows,
        "kubejs_direct_display_lines": visible_lines,
        "status": "complete",
    }
    write(ROOT / "surface_audit.json", result)
    return result, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("normalize", "verify", "audit"))
    args = parser.parse_args()
    if args.command == "normalize":
        report, errors = normalize(), []
    elif args.command == "verify":
        report, errors = verify()
    else:
        report, errors = audit()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
