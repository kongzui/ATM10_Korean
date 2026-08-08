#!/usr/bin/env python3
"""BiblioCraft·BiblioWoods·BiblioBiomes의 전체 표시 문자열을 번역·검증해요."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

from chipped_family import load_json, write_json
from dungeons_arise_family import (
    VISIBLE_DATA_KEYS,
    component_literal_text,
    scan_visible_nbt,
    walk_json,
)
from local_paths import PROJECT_ROOT, resolve_source_root

FAMILY = "bibliocraft_family"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
JARS = {
    "bibliocraft": "bibliocraft-1.21.1-*.jar",
    "bibliowoods": "bibliowoods-1.21.1-*.jar",
    "bibliobiomes": "bibliobiomes-1.21.1-*.jar",
}
OUTPUTS = {
    label: (
        PROJECT_ROOT
        / f"output/resourcepack/ATM10_Korean/assets/{label}/lang/ko_kr.json"
    )
    for label in JARS
}
DEPLOYMENT_PATHS = [
    f"resourcepacks/ATM10_Korean/assets/{label}/lang/ko_kr.json" for label in JARS
]

PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[.]\d+)?")
HANGUL = re.compile(r"[가-힣]")

COLORS = {
    "Black": "검은색",
    "Blue": "파란색",
    "Brown": "갈색",
    "Cyan": "청록색",
    "Gray": "회색",
    "Green": "초록색",
    "Light Blue": "하늘색",
    "Light Gray": "회백색",
    "Lime": "연두색",
    "Magenta": "자홍색",
    "Orange": "주황색",
    "Pink": "분홍색",
    "Purple": "보라색",
    "Red": "빨간색",
    "White": "하얀색",
    "Yellow": "노란색",
}

# 현재 설치본의 영어 목재 이름을 현재 모드 원문과 검수된 프로젝트 용어에 맞춰 고정해요.
MATERIALS = {
    "Acacia": "아카시아나무",
    "Alder": "오리나무",
    "Alpha": "알파 나무",
    "Ancient": "고대",
    "Apricorn": "규토리나무",
    "Archwood": "아크우드",
    "Aspen": "아스펜",
    "Aurum": "아우룸",
    "Bamboo": "대나무",
    "Banyin": "바닌나무",
    "Baobab": "바오밥",
    "Barn Wood": "헛간 목재",
    "Birch": "자작나무",
    "Blackwood": "블랙우드",
    "Bloom": "개화목",
    "Blue Bioshroom": "파란색 바이오버섯",
    "Blue Enchanted": "파란 마법 나무",
    "Brimwood": "브림우드",
    "Canopy": "캐노피나무",
    "Cherry": "벚나무",
    "Cika": "치카",
    "Cinnamon": "계피나무",
    "Clinkera": "클린케라",
    "Cobalt": "코발트 나무",
    "Conberry": "콘베리",
    "Cradlewood": "요람나무",
    "Crimson": "진홍빛",
    "Cruderoot": "크루드루트",
    "Cursed Spruce": "저주받은 가문비나무",
    "Cypress": "사이프러스",
    "Dark": "어둠나무",
    "Dark Oak": "짙은 참나무",
    "Dark Spruce": "어두운 가문비나무",
    "Dead": "고사목",
    "Decidrheum": "데시드리움",
    "Demonic": "악마",
    "Denia": "데니아",
    "Ebony": "흑단",
    "Echo": "메아리나무",
    "Edelwood": "에델우드",
    "Empyreal": "엠피리얼",
    "Eucalyptus": "유칼립투스",
    "Fir": "전나무",
    "Florus": "플로러스",
    "Fruit": "과일나무",
    "Fungyss": "펀지스",
    "Greatwood": "그레이트우드",
    "Green Bioshroom": "초록색 바이오버섯",
    "Green Enchanted": "초록 마법 나무",
    "Grongle": "그롱글",
    "Hawthorn": "산사나무",
    "Hellbark": "헬바크",
    "Holly": "호랑가시나무",
    "Ironwood": "아이언우드",
    "Jacaranda": "자카란다",
    "Jinglestem": "방울줄기",
    "Joshua": "여호수아나무",
    "Jungle": "정글나무",
    "Kapok": "카폭",
    "Larch": "낙엽송",
    "Lunar": "달빛나무",
    "Magic": "마법 나무",
    "Magnolia": "목련",
    "Mahogany": "마호가니",
    "Mangrove": "맹그로브나무",
    "Maple": "단풍나무",
    "Mauve": "모브 나무",
    "Menril": "멘릴 나무",
    "Mining": "광부나무",
    "Mycha": "미카",
    "Netherwood": "네더나무",
    "Northland": "북방나무",
    "Nut": "견과나무",
    "Oak": "참나무",
    "Otherplanks": "기타 판자",
    "Palm": "야자나무",
    "Pine": "소나무",
    "Pink Bioshroom": "분홍색 바이오버섯",
    "Polished Mahogany": "광택 낸 마호가니",
    "Polished Willow": "광택 낸 버드나무",
    "Polished Witch Hazel": "광택 낸 풍년화",
    "Powdery": "가루나무",
    "Rainbow Eucalyptus": "무지개 유칼립투스",
    "Redwood": "레드우드",
    "Roseroot": "로즈루트",
    "Rowan": "마가목",
    "Rubber": "고무나무",
    "Sakura": "벚나무",
    "Scarlet": "진홍나무",
    "Sepia": "세피아",
    "Silverwood": "실버우드",
    "Skyris": "스카이리스",
    "Skyroot": "스카이루트",
    "Smogstem": "안개줄기",
    "Socotra": "소코트라",
    "Sorting": "분류나무",
    "Soul": "영혼",
    "Spirit": "영혼 나무",
    "Spruce": "가문비나무",
    "Sunroot": "선루트",
    "Time": "시간나무",
    "Torreya": "개비자나무",
    "Transformation": "변화나무",
    "Treated Wood": "방부목",
    "Twilight Oak": "황혼 참나무",
    "Umbran": "엄브란",
    "Warped": "뒤틀린",
    "White Mangrove": "흰 맹그로브나무",
    "Wigglewood": "흔들나무",
    "Wildwood": "야생나무",
    "Willow": "버드나무",
    "Witch Hazel": "풍년화",
    "Yagroot": "야그루트",
    "Yellow Bioshroom": "노란색 바이오버섯",
    "Zelkova": "느티나무",
}

FURNITURE = {
    "Bookcase": "책장",
    "Fancy Armor Stand": "화려한 갑옷 거치대",
    "Fancy Clock": "화려한 시계",
    "Fancy Crafter": "화려한 제작대",
    "Fancy Sign": "화려한 표지판",
    "Grandfather Clock": "괘종시계",
    "Label": "라벨",
    "Potion Shelf": "물약 선반",
    "Shelf": "선반",
    "Table": "탁자",
    "Tool Rack": "도구 걸이",
}

COLORED_FURNITURE = {
    "Display Case": "진열장",
    "Seat": "의자",
    "Seat Back": "의자 등받이",
    "Fancy Seat Back": "화려한 의자 등받이",
    "Flat Seat Back": "평평한 의자 등받이",
    "Raised Seat Back": "돌출형 의자 등받이",
    "Small Seat Back": "소형 의자 등받이",
    "Tall Seat Back": "높은 의자 등받이",
}

CORE_NAMES = {
    "Big Book": "큰 책",
    "Clipboard": "클립보드",
    "Cookie Jar": "쿠키 항아리",
    "Desk Bell": "탁상 종",
    "Dinner Plate": "식사 접시",
    "Disc Rack": "음반 거치대",
    "Fancy Gold Lamp": "화려한 금 램프",
    "Fancy Gold Lantern": "화려한 금 랜턴",
    "Fancy Iron Lamp": "화려한 철 램프",
    "Fancy Iron Lantern": "화려한 철 랜턴",
    "Gold Chain": "금 사슬",
    "Gold Lantern": "금 랜턴",
    "Gold Soul Lantern": "금 영혼 랜턴",
    "Iron Fancy Armor Stand": "화려한 철 갑옷 거치대",
    "Iron Printing Table": "철 인쇄대",
    "Lock and Key": "자물쇠와 열쇠",
    "Plumb Line": "다림줄",
    "Printing Table": "인쇄대",
    "Redstone Book": "레드스톤 책",
    "Slotted Book": "비밀 수납 책",
    "Soul Fancy Gold Lantern": "화려한 금 영혼 랜턴",
    "Soul Fancy Iron Lantern": "화려한 철 영혼 랜턴",
    "Stockroom Catalog": "창고 목록",
    "Sword Pedestal": "검 받침대",
    "Tape Measure": "줄자",
    "Tape Reel": "줄자 릴",
    "Typewriter": "타자기",
    "Typewriter Page": "타자기 용지",
}

CORE_KEY_TRANSLATIONS = {
    "block.bibliocraft.typewriter.no_paper": "입력을 시작하기 전에 종이를 넣어야 합니다!",
    "item.bibliocraft.lock_and_key.locked": "%s 잠금에 성공했습니다!",
    "item.bibliocraft.lock_and_key.no_custom_name": (
        "블록에 사용하기 전에 이 자물쇠와 열쇠의 이름을 바꿔야 합니다!"
    ),
    "item.bibliocraft.lock_and_key.unlocked": "%s 잠금 해제에 성공했습니다!",
    "item.bibliocraft.plumb_line.distance": "깊이: %s",
    "item.bibliocraft.redstone_book.text": (
        "이 책을 책장에 넣으면 책장이 레드스톤 신호를 냅니다. 신호 세기는 책을 넣은 "
        "칸에 따라 달라집니다. 1번 칸(왼쪽 위)은 신호를 내지 않습니다. 2번 칸의 "
        "신호 세기는 1입니다. 이후 칸마다 신호 세기가 하나씩 증가하여, 16번 칸(오른쪽 "
        "아래)의 신호 세기는 15가 됩니다."
    ),
    "item.bibliocraft.redstone_book.title": "레드스톤: 제1권",
    "item.bibliocraft.slotted_book.text": (
        "여러 책 사이에 귀중품을 숨길 수 있는 책입니다."
    ),
    "item.bibliocraft.stockroom_catalog.add_container": (
        "%s의 내용물을 창고 목록에 기록하기 시작했습니다!"
    ),
    "item.bibliocraft.stockroom_catalog.remove_container": (
        "%s의 내용물을 창고 목록에 기록하지 않습니다!"
    ),
    "item.bibliocraft.tape_measure.distance": ("거리: %s블록 (x: %s, y: %s, z: %s)"),
}

UI_TRANSLATIONS = {
    "color.aqua": "청록색",
    "color.black": "검은색",
    "color.blue": "파란색",
    "color.dark_aqua": "짙은 청록색",
    "color.dark_blue": "짙은 파란색",
    "color.dark_gray": "짙은 회색",
    "color.dark_green": "짙은 초록색",
    "color.dark_purple": "짙은 보라색",
    "color.dark_red": "짙은 빨간색",
    "color.gold": "금색",
    "color.gray": "회색",
    "color.green": "초록색",
    "color.light_purple": "밝은 보라색",
    "color.red": "빨간색",
    "color.white": "하얀색",
    "color.yellow": "노란색",
    "config.bibliocraft.compatibility": "호환성",
    "config.bibliocraft.compatibility.jei": "JEI",
    "config.bibliocraft.compatibility.jei.show_color_types": "색상 종류 표시",
    "config.bibliocraft.compatibility.jei.show_color_types.tooltip": (
        "JEI에 모든 색상 블록을 표시할지, 기본 하얀색만 표시할지 정합니다."
    ),
    "config.bibliocraft.compatibility.jei.show_wood_types": "목재 종류 표시",
    "config.bibliocraft.compatibility.jei.show_wood_types.tooltip": (
        "JEI에 모든 목재 종류 블록을 표시할지, 기본 참나무만 표시할지 정합니다."
    ),
    "config.bibliocraft.compatibility.jei.tooltip": "JEI 모드 호환 옵션입니다.",
    "config.bibliocraft.compatibility.tooltip": "호환성 옵션입니다.",
    "config.bibliocraft.cosmetic": "꾸미기",
    "config.bibliocraft.cosmetic.enable_pride": "프라이드 꾸미기 활성화",
    "config.bibliocraft.cosmetic.enable_pride.tooltip": (
        "프라이드의 달 동안 프라이드 테마 꾸미기를 활성화할지 정합니다."
    ),
    "config.bibliocraft.cosmetic.enable_pride_always": "프라이드 꾸미기 항상 활성화",
    "config.bibliocraft.cosmetic.enable_pride_always.tooltip": (
        "프라이드 테마 꾸미기를 일 년 내내 활성화할지, 프라이드의 달에만 "
        "활성화할지 정합니다. 프라이드 꾸미기가 꺼져 있으면 적용되지 않습니다."
    ),
    "config.bibliocraft.cosmetic.tooltip": "꾸미기 옵션입니다.",
    "container.bibliocraft.bookcase": "책장",
    "container.bibliocraft.cookie_jar": "쿠키 항아리",
    "container.bibliocraft.disc_rack": "음반 거치대",
    "container.bibliocraft.fancy_armor_stand": "갑옷 거치대",
    "container.bibliocraft.fancy_crafter": "제작",
    "container.bibliocraft.label": "라벨",
    "container.bibliocraft.potion_shelf": "물약 선반",
    "container.bibliocraft.printing_table": "인쇄대",
    "container.bibliocraft.shelf": "선반",
    "container.bibliocraft.tool_rack": "도구 걸이",
    "gui.bibliocraft.clock.add_trigger": "작동 조건 추가",
    "gui.bibliocraft.clock.delete_trigger": "작동 조건 삭제",
    "gui.bibliocraft.clock.edit_trigger": "작동 조건 편집",
    "gui.bibliocraft.clock.emit_redstone": "레드스톤 신호 출력",
    "gui.bibliocraft.clock.emit_sound": "소리 재생",
    "gui.bibliocraft.clock.hours": "시간",
    "gui.bibliocraft.clock.hours_hint": "hh",
    "gui.bibliocraft.clock.minutes": "분",
    "gui.bibliocraft.clock.minutes_hint": "mm",
    "gui.bibliocraft.clock.tick": "초침 소리 활성화",
    "gui.bibliocraft.clock.time": "시간:",
    "gui.bibliocraft.clock.time_separator": ":",
    "gui.bibliocraft.clock.title": "시계",
    "gui.bibliocraft.clock.triggers": "작동 조건",
    "gui.bibliocraft.fancy_sign.title": "화려한 표지판",
    "gui.bibliocraft.fancy_text_area.alignment": "정렬 전환",
    "gui.bibliocraft.fancy_text_area.bold": "굵게",
    "gui.bibliocraft.fancy_text_area.bold.short": "B",
    "gui.bibliocraft.fancy_text_area.color_hint": "#RRGGBB",
    "gui.bibliocraft.fancy_text_area.italic": "기울임꼴",
    "gui.bibliocraft.fancy_text_area.italic.short": "I",
    "gui.bibliocraft.fancy_text_area.mode": "그림자·발광 전환",
    "gui.bibliocraft.fancy_text_area.narration": "텍스트 영역",
    "gui.bibliocraft.fancy_text_area.obfuscated": "난독화",
    "gui.bibliocraft.fancy_text_area.obfuscated.short": "O",
    "gui.bibliocraft.fancy_text_area.scale_down": "-",
    "gui.bibliocraft.fancy_text_area.scale_down.tooltip": "축소",
    "gui.bibliocraft.fancy_text_area.scale_up": "+",
    "gui.bibliocraft.fancy_text_area.scale_up.tooltip": "확대",
    "gui.bibliocraft.fancy_text_area.strikethrough": "취소선",
    "gui.bibliocraft.fancy_text_area.strikethrough.short": "S",
    "gui.bibliocraft.fancy_text_area.underlined": "밑줄",
    "gui.bibliocraft.fancy_text_area.underlined.short": "U",
    "gui.bibliocraft.formatted_line.alignment.center": "가운데",
    "gui.bibliocraft.formatted_line.alignment.left": "왼쪽",
    "gui.bibliocraft.formatted_line.alignment.right": "오른쪽",
    "gui.bibliocraft.formatted_line.mode.glowing": "발광",
    "gui.bibliocraft.formatted_line.mode.normal": "보통",
    "gui.bibliocraft.formatted_line.mode.shadow": "그림자",
    "gui.bibliocraft.printing_table.add_experience": "경험치 추가",
    "gui.bibliocraft.printing_table.mode": "모드: %s",
    "gui.bibliocraft.printing_table.mode.bind": "제본",
    "gui.bibliocraft.printing_table.mode.clone": "복제",
    "gui.bibliocraft.printing_table.mode.merge": "합치기",
    "gui.bibliocraft.stockroom_catalog.count": "x%s",
    "gui.bibliocraft.stockroom_catalog.distance": "%s블록 거리",
    "gui.bibliocraft.stockroom_catalog.locate": "찾기",
    "gui.bibliocraft.stockroom_catalog.remove": "제거",
    "gui.bibliocraft.stockroom_catalog.search": "검색",
    "gui.bibliocraft.stockroom_catalog.show_containers": "보관함 표시",
    "gui.bibliocraft.stockroom_catalog.show_items": "아이템 표시",
    "gui.bibliocraft.stockroom_catalog.sort": "정렬: %s",
    "gui.bibliocraft.stockroom_catalog.sorting.container.alphabetical_asc": "A-Z",
    "gui.bibliocraft.stockroom_catalog.sorting.container.alphabetical_desc": "Z-A",
    "gui.bibliocraft.stockroom_catalog.sorting.container.distance_asc": "<-->",
    "gui.bibliocraft.stockroom_catalog.sorting.container.distance_desc": "-><-",
    "gui.bibliocraft.stockroom_catalog.sorting.item.alphabetical_asc": "A-Z",
    "gui.bibliocraft.stockroom_catalog.sorting.item.alphabetical_desc": "Z-A",
    "gui.bibliocraft.stockroom_catalog.sorting.item.count_asc": "1-99",
    "gui.bibliocraft.stockroom_catalog.sorting.item.count_desc": "99-1",
    "gui.bibliocraft.typewriter.title": "타자기",
    "itemGroup.bibliocraft": "BiblioCraft",
    "jei.bibliocraft.all_colors": "이 블록은 모든 색상으로 제작할 수 있습니다.",
    "jei.bibliocraft.all_colors_and_wood_types": (
        "이 블록은 모든 색상과 목재 종류로 제작할 수 있습니다."
    ),
    "jei.bibliocraft.all_wood_types": "이 블록은 모든 목재 종류로 제작할 수 있습니다.",
    "jei.bibliocraft.category.printing_table": "인쇄대",
    "jei.bibliocraft.requires_experience": "이 조합법에는 경험치도 필요합니다!",
    "subtitles.bibliocraft.clock.chime": "시계가 종을 울림",
    "subtitles.bibliocraft.clock.tick": "시계가 째깍거림",
    "subtitles.bibliocraft.clock.tock": "시계가 똑딱거림",
    "subtitles.bibliocraft.desk_bell": "탁상 종이 울림",
    "subtitles.bibliocraft.display_case.close": "진열장이 닫힘",
    "subtitles.bibliocraft.display_case.open": "진열장이 열림",
    "subtitles.bibliocraft.tape_measure.close": "줄자가 감김",
    "subtitles.bibliocraft.tape_measure.open": "줄자가 늘어남",
    "subtitles.bibliocraft.typewriter.add_paper": "타자기에 종이를 넣음",
    "subtitles.bibliocraft.typewriter.chime": "타자기가 종을 울림",
    "subtitles.bibliocraft.typewriter.take_page": "타자기에서 종이를 꺼냄",
    "subtitles.bibliocraft.typewriter.type": "타자기로 입력함",
    "subtitles.bibliocraft.typewriter.typing": "타자기로 입력함",
}

TAG_VALUES = {
    "Bookcases": "책장",
    "Books for Bookcases": "책장에 넣을 책",
    "Cookies for Cookie Jars": "쿠키 항아리에 넣을 쿠키",
    "Discs for Disc Racks": "음반 거치대에 넣을 음반",
    "Display Cases": "진열장",
    "Fancy Armor Stands": "화려한 갑옷 거치대",
    "Fancy Clocks": "화려한 시계",
    "Fancy Lamps": "화려한 램프",
    "Fancy Lanterns": "화려한 랜턴",
    "Fancy Signs": "화려한 표지판",
    "Gold Fancy Lamps": "화려한 금 램프",
    "Gold Fancy Lanterns": "화려한 금 랜턴",
    "Grandfather Clocks": "괘종시계",
    "Iron Fancy Lamps": "화려한 철 램프",
    "Iron Fancy Lanterns": "화려한 철 랜턴",
    "Labels": "라벨",
    "Paper for Typewriters": "타자기용 종이",
    "Potion Shelves": "물약 선반",
    "Potions for Potion Shelves": "물약 선반에 넣을 물약",
    "Printing Table Cloning Blacklist": "인쇄대 복제 제외 목록",
    "Printing Tables": "인쇄대",
    "Seat Backs": "의자 등받이",
    "Seats": "의자",
    "Shelves": "선반",
    "Swords for Sword Pedestals": "검 받침대에 놓을 검",
    "Tables": "탁자",
    "Tool Racks": "도구 걸이",
    "Tools for Tool Racks": "도구 걸이에 놓을 도구",
    "Typewriters": "타자기",
    "Wax for Fancy Signs": "화려한 표지판용 밀랍",
    "Wooden Fancy Armor Stands": "목재 화려한 갑옷 거치대",
}

INTENTIONAL_NO_HANGUL_KEYS = {
    "config.bibliocraft.compatibility.jei",
    "gui.bibliocraft.clock.hours_hint",
    "gui.bibliocraft.clock.minutes_hint",
    "gui.bibliocraft.clock.time_separator",
    "gui.bibliocraft.fancy_text_area.bold.short",
    "gui.bibliocraft.fancy_text_area.color_hint",
    "gui.bibliocraft.fancy_text_area.italic.short",
    "gui.bibliocraft.fancy_text_area.obfuscated.short",
    "gui.bibliocraft.fancy_text_area.scale_down",
    "gui.bibliocraft.fancy_text_area.scale_up",
    "gui.bibliocraft.fancy_text_area.strikethrough.short",
    "gui.bibliocraft.fancy_text_area.underlined.short",
    "gui.bibliocraft.stockroom_catalog.count",
    "gui.bibliocraft.stockroom_catalog.sorting.container.alphabetical_asc",
    "gui.bibliocraft.stockroom_catalog.sorting.container.alphabetical_desc",
    "gui.bibliocraft.stockroom_catalog.sorting.container.distance_asc",
    "gui.bibliocraft.stockroom_catalog.sorting.container.distance_desc",
    "gui.bibliocraft.stockroom_catalog.sorting.item.alphabetical_asc",
    "gui.bibliocraft.stockroom_catalog.sorting.item.alphabetical_desc",
    "gui.bibliocraft.stockroom_catalog.sorting.item.count_asc",
    "gui.bibliocraft.stockroom_catalog.sorting.item.count_desc",
    "itemGroup.bibliocraft",
}


def find_jar(label: str) -> Path:
    """현재 설치본에서 지정한 JAR 하나를 찾아요."""
    matches = sorted((resolve_source_root() / "mods").glob(JARS[label]))
    if len(matches) != 1:
        raise FileNotFoundError(f"{label} JAR이 정확히 한 개가 아니에요: {matches}")
    return matches[0]


def read_language(label: str, locale: str) -> dict[str, str]:
    """현재 JAR에서 언어 파일을 읽어요."""
    with ZipFile(find_jar(label)) as archive:
        try:
            value = json.loads(archive.read(f"assets/{label}/lang/{locale}.json"))
        except KeyError:
            return {}
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise TypeError(f"{label} {locale} 언어 파일 형식이 올바르지 않아요")
    return value


def read_project_candidate(label: str) -> dict[str, str]:
    """작업 시작 전 Git 산출물을 낮은 품질의 한국어 후보로 읽어요."""
    candidate_path = WORK_ROOT / f"{label}_project_candidate_ko_kr.json"
    if candidate_path.is_file():
        candidate = load_json(candidate_path)
    else:
        relative = OUTPUTS[label].relative_to(PROJECT_ROOT).as_posix()
        completed = subprocess.run(
            ["git", "show", f"HEAD:{relative}"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            check=False,
        )
        if completed.returncode:
            candidate = {}
        else:
            candidate = json.loads(completed.stdout.decode("utf-8"))
        write_json(candidate_path, candidate)
    if not isinstance(candidate, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in candidate.items()
    ):
        raise TypeError(f"{label} 기존 프로젝트 한국어 후보 형식이 올바르지 않아요")
    return candidate


def collect_surface(label: str) -> dict[str, object]:
    """JAR의 언어·데이터·NBT·가이드 표시 표면을 전수 확인해요."""
    jar = find_jar(label)
    language_files = []
    data_files = []
    direct_fields = []
    localized_fields = []
    invalid_json = []
    nbt_files = []
    nbt_rows = []
    guide_candidates = []
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            lower = name.lower()
            if "/lang/" in lower and lower.endswith(".json"):
                language_files.append(name)
            if lower.endswith((".md", ".txt", ".json")) and any(
                token in lower
                for token in ("/book/", "/guide/", "/manual/", "patchouli")
            ):
                guide_candidates.append(name)
            if lower.startswith("data/") and lower.endswith(".json"):
                data_files.append(name)
                try:
                    value = json.loads(archive.read(name))
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    invalid_json.append(f"{name}: {exc}")
                    continue
                for key, path, child in walk_json(value):
                    if key not in VISIBLE_DATA_KEYS:
                        continue
                    row = {"file": name, "path": path, "value": child}
                    if isinstance(child, dict) and isinstance(
                        child.get("translate"), str
                    ):
                        localized_fields.append(row)
                    else:
                        literal = component_literal_text(child)
                        if literal and literal.strip():
                            direct_fields.append({**row, "literal": literal})
            if not lower.endswith(".nbt"):
                continue
            nbt_files.append(name)
            raw = archive.read(name)
            try:
                raw = gzip.decompress(raw)
            except gzip.BadGzipFile:
                pass
            for row in scan_visible_nbt(raw):
                nbt_rows.append({"file": name, **row})
    return {
        "label": label,
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_mtime_ns": jar.stat().st_mtime_ns,
        "jar_sha256": hashlib.sha256(jar.read_bytes()).hexdigest(),
        "language_files": language_files,
        "data_json_files": len(data_files),
        "data_direct_fields": direct_fields,
        "data_localized_fields": localized_fields,
        "invalid_json": invalid_json,
        "nbt_files": len(nbt_files),
        "nbt_visible_fields": nbt_rows,
        "guide_candidates": guide_candidates,
    }


def audit_references() -> tuple[dict[str, object], list[str]]:
    """FTB Quests와 KubeJS의 정확한 네임스페이스 참조를 분류해요."""
    instance = resolve_source_root()
    pattern = re.compile(
        r"(?<![a-z0-9_])(?:bibliocraft|bibliowoods|bibliobiomes):[a-z0-9_./-]+",
        re.IGNORECASE,
    )
    report: dict[str, object] = {"ftbquests": [], "kubejs": [], "read_errors": []}
    errors = []
    for label, base in (
        ("ftbquests", instance / "config/ftbquests/quests"),
        ("kubejs", instance / "kubejs"),
    ):
        rows = report[label]
        if not isinstance(rows, list) or not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {
                ".cfg",
                ".js",
                ".json",
                ".snbt",
                ".toml",
                ".txt",
            }:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                report["read_errors"].append(f"{path}: {exc}")
                continue
            matches = pattern.findall(text)
            if not matches:
                continue
            visible_lines = [
                number
                for number, line in enumerate(text.splitlines(), 1)
                if pattern.search(line)
                and re.search(
                    r"(?i)(?:custom_name|displayname|display_name|lore|subtitle|title|tooltip)"
                    r"\s*[:=(]",
                    line,
                )
            ]
            relative = path.relative_to(instance).as_posix()
            if relative.endswith("disable_loot_table_ids.json"):
                classification = "loot_table_identifiers_only"
            elif relative.endswith("mods/Bibliocraft/Recipes.js"):
                classification = "recipe_identifier_only"
            else:
                classification = "item_ids_use_resourcepack_names"
            row = {
                "path": relative,
                "occurrences": len(matches),
                "unique_identifiers": len(set(matches)),
                "classification": classification,
                "visible_namespace_candidate_lines": visible_lines,
            }
            rows.append(row)
            if visible_lines:
                errors.append(f"{label}에 직접 표시 문구 후보가 있어요: {row}")
    errors.extend(str(value) for value in report["read_errors"])
    return report, errors


def prepare() -> dict[str, object]:
    """현재 JAR 영어 원문과 기존 한국어 후보, 표시 표면을 기록해요."""
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    counts = {}
    candidates = {}
    project_candidates = {}
    for label in JARS:
        english = read_language(label, "en_us")
        korean = read_language(label, "ko_kr")
        project_korean = read_project_candidate(label)
        write_json(WORK_ROOT / f"{label}_en_us.json", english)
        write_json(WORK_ROOT / f"{label}_candidate_ko_kr.json", korean)
        rows.append(collect_surface(label))
        counts[label] = len(english)
        candidates[label] = len(korean)
        project_candidates[label] = len(project_korean)
    references, reference_errors = audit_references()
    catalog = {
        "family": FAMILY,
        "jars": rows,
        "language_keys": counts,
        "bundled_korean_candidate_keys": candidates,
        "project_korean_candidate_keys": project_candidates,
        "references": references,
        "reference_errors": reference_errors,
        "status": "prepared" if not reference_errors else "incomplete",
    }
    write_json(WORK_ROOT / "source_surface_catalog.json", catalog)
    return catalog


def generated_name_map() -> dict[str, str]:
    """목재·가구·색상 조합의 검수된 이름 대응표를 만들어요."""
    values = dict(CORE_NAMES)
    for material, material_ko in MATERIALS.items():
        for suffix, suffix_ko in FURNITURE.items():
            values[f"{material} {suffix}"] = f"{material_ko} {suffix_ko}"
        for color, color_ko in COLORS.items():
            for suffix, suffix_ko in COLORED_FURNITURE.items():
                values[f"{color} {material} {suffix}"] = (
                    f"{color_ko} {material_ko} {suffix_ko}"
                )
    for color, color_ko in COLORS.items():
        values[f"{color} Typewriter"] = f"{color_ko} 타자기"
        for material in ("Gold", "Iron"):
            material_ko = "금" if material == "Gold" else "철"
            for fixture, fixture_ko in (("Lamp", "램프"), ("Lantern", "랜턴")):
                values[f"{color} Fancy {material} {fixture}"] = (
                    f"{color_ko} 화려한 {material_ko} {fixture_ko}"
                )
    return values


def translate_key(key: str, source: str, names: dict[str, str]) -> tuple[str, str]:
    """키와 원문 종류에 따라 한 값을 번역해요."""
    if key in CORE_KEY_TRANSLATIONS:
        return CORE_KEY_TRANSLATIONS[key], "reviewed_message"
    if key in UI_TRANSLATIONS:
        return UI_TRANSLATIONS[key], "reviewed_ui"
    if key.startswith("tag.") and source in TAG_VALUES:
        return TAG_VALUES[source], "reviewed_tag"
    if key.startswith(("block.", "item.")) and source in names:
        return names[source], "generated_reviewed_name"
    raise KeyError(f"번역 규칙이 없는 현재 영어 원문이에요: {key}={source!r}")


def build() -> dict[str, object]:
    """세 JAR의 현재 영어 키 전체를 번역해 작업본과 산출물을 만들어요."""
    names = generated_name_map()
    counts = {}
    methods = Counter()
    reused = 0
    revised = 0
    new = 0
    for label in JARS:
        english = read_language(label, "en_us")
        candidate = read_project_candidate(label)
        translated = {}
        for key, source in english.items():
            target, method = translate_key(key, source, names)
            translated[key] = target
            methods[method] += 1
        write_json(WORK_ROOT / f"{label}_ko_kr.json", translated)
        write_json(OUTPUTS[label], translated)
        counts[label] = len(translated)
        reused += sum(candidate.get(key) == value for key, value in translated.items())
        revised += sum(
            key in candidate and candidate[key] != value
            for key, value in translated.items()
        )
        new += sum(key not in candidate for key in translated)
    report = {
        "family": FAMILY,
        "reviewed_language_keys": sum(counts.values()),
        "output_keys": counts,
        "material_source_names": len(MATERIALS),
        "existing_project_values_reused": reused,
        "existing_project_values_revised": revised,
        "new_language_values": new,
        "translation_methods": dict(sorted(methods.items())),
        "errors": [],
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def preserved_errors(key: str, source: str, target: str) -> list[str]:
    """자리표시자·서식·숫자·줄바꿈이 보존됐는지 확인해요."""
    errors = []
    for label, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식 코드", FORMAT_CODE),
        ("숫자", NUMBER),
    ):
        if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
            errors.append(f"{key} {label}이 달라요")
    if source.count("\n") != target.count("\n"):
        errors.append(f"{key} 실제 줄바꿈 수가 달라요")
    if source.count("\\n") != target.count("\\n"):
        errors.append(f"{key} 이스케이프 줄바꿈 수가 달라요")
    return errors


def source_is_current(catalog: dict[str, object]) -> list[str]:
    """준비 이후 원본 JAR이 바뀌지 않았는지 확인해요."""
    errors = []
    for row in catalog["jars"]:
        jar = find_jar(row["label"])
        if (
            row["jar"] != jar.name
            or row["jar_size"] != jar.stat().st_size
            or row["jar_mtime_ns"] != jar.stat().st_mtime_ns
            or row["jar_sha256"] != hashlib.sha256(jar.read_bytes()).hexdigest()
        ):
            errors.append(f"{row['label']} JAR이 원문 추출 당시와 달라요")
    return errors


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR 데이터와 FTB Quests·KubeJS 표시 경로를 감사해요."""
    catalog = load_json(WORK_ROOT / "source_surface_catalog.json")
    errors = source_is_current(catalog)
    surfaces = {}
    for row in catalog["jars"]:
        label = row["label"]
        if row["invalid_json"]:
            errors.append(f"{label}에 읽지 못한 데이터 JSON이 있어요")
        if row["guide_candidates"]:
            errors.append(f"{label}에 별도 가이드 후보가 있어요")
        direct_fields = row["data_direct_fields"]
        merge_strategy_fields = [
            value
            for value in direct_fields
            if value["value"] == "first"
            and ".component_mergers." in value["path"]
            and value["path"].endswith(".title")
        ]
        if len(merge_strategy_fields) != len(direct_fields):
            errors.append(f"{label} 데이터에 직접 표시 문구가 있어요")
        if row["nbt_visible_fields"]:
            errors.append(f"{label} NBT에 직접 표시 문구가 있어요")
        surfaces[label] = {
            "data_json_files": row["data_json_files"],
            "data_localized_fields": len(row["data_localized_fields"]),
            "data_direct_fields": len(direct_fields),
            "direct_field_classification": (
                "recipe_component_merge_strategy"
                if direct_fields and len(merge_strategy_fields) == len(direct_fields)
                else "none"
            ),
            "nbt_files": row["nbt_files"],
            "nbt_visible_fields": len(row["nbt_visible_fields"]),
            "guide_candidates": len(row["guide_candidates"]),
        }
    references, reference_errors = audit_references()
    errors.extend(reference_errors)
    report = {
        "family": FAMILY,
        "jar_surfaces": surfaces,
        "references": references,
        "ftbquests_display_work": (
            "no_related_references"
            if not references["ftbquests"]
            else "item_ids_use_resourcepack_names"
        ),
        "kubejs_display_work": (
            "no_visible_text_work"
            if references["kubejs"] and not reference_errors
            else "no_related_references"
        ),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def canonical_source(source: str) -> str:
    """프로젝트에서 같은 나무 이름을 쓰는 Cherry와 Sakura만 동등하게 봐요."""
    return re.sub(r"(?<![A-Za-z])Sakura(?![A-Za-z])", "Cherry", source)


def verify_language() -> tuple[dict[str, object], list[str]]:
    """영어 전체 키·출력·보존 요소·이름 구분을 검증해요."""
    errors = []
    by_mod = {}
    no_hangul = []
    same = []
    unexpected_collisions = {}
    total = 0
    for label in JARS:
        english = read_language(label, "en_us")
        work = load_json(WORK_ROOT / f"{label}_ko_kr.json")
        output = load_json(OUTPUTS[label])
        candidate = read_project_candidate(label)
        total += len(english)
        if list(work) != list(english) or list(output) != list(english):
            errors.append(f"{label} 한국어 키 또는 순서가 현재 영어 원문과 달라요")
        if work != output:
            errors.append(f"{label} 작업본과 산출물이 달라요")
        collisions = defaultdict(lambda: defaultdict(list))
        for key, source in english.items():
            target = output.get(key)
            if not isinstance(target, str):
                errors.append(f"문자열 번역이 없어요: {key}")
                continue
            errors.extend(preserved_errors(key, source, target))
            if source == target:
                same.append(key)
            if not HANGUL.search(target):
                no_hangul.append(key)
            if key.startswith(("block.", "item.")):
                collisions[target][source].append(key)
        invalid = {}
        for target, sources in collisions.items():
            canonical = {canonical_source(source) for source in sources}
            if len(canonical) > 1:
                invalid[target] = dict(sources)
        if invalid:
            unexpected_collisions[label] = invalid
            errors.append(f"{label}에서 서로 다른 영어 이름이 합쳐졌어요")
        by_mod[label] = {
            "english_keys": len(english),
            "output_keys": len(output),
            "bundled_korean_candidate_keys": len(read_language(label, "ko_kr")),
            "project_korean_candidate_keys": len(candidate),
            "existing_project_values_reused": sum(
                candidate.get(key) == value for key, value in output.items()
            ),
            "existing_project_values_revised": sum(
                key in candidate and candidate[key] != value
                for key, value in output.items()
            ),
            "new_values": sum(key not in candidate for key in output),
            "unexpected_collapsed_name_count": len(invalid),
        }
    if set(no_hangul) != INTENTIONAL_NO_HANGUL_KEYS:
        errors.append(
            "영문·기호 유지 키가 검수 목록과 달라요: "
            f"actual={sorted(no_hangul)}, expected={sorted(INTENTIONAL_NO_HANGUL_KEYS)}"
        )
    if any(key not in INTENTIONAL_NO_HANGUL_KEYS for key in same):
        errors.append(f"검수하지 않은 영어 원문 유지값이 있어요: {same}")
    report = {
        "reviewed_english_keys": total,
        "mods": by_mod,
        "existing_project_values_reused": sum(
            row["existing_project_values_reused"] for row in by_mod.values()
        ),
        "existing_project_values_revised": sum(
            row["existing_project_values_revised"] for row in by_mod.values()
        ),
        "new_language_values": sum(row["new_values"] for row in by_mod.values()),
        "intentional_no_hangul_keys": sorted(no_hangul),
        "intentional_same_keys": same,
        "unexpected_collapsed_names": unexpected_collisions,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """언어와 표시 표면, 적용 기록을 함께 검증해요."""
    catalog = load_json(WORK_ROOT / "source_surface_catalog.json")
    source_errors = source_is_current(catalog)
    language, language_errors = verify_language()
    surface, surface_errors = audit()
    errors = source_errors + language_errors + surface_errors
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = load_json(deployment_path) if deployment_path.is_file() else None
    report = {
        "family": FAMILY,
        "language": language,
        "surface_audit": surface["status"],
        "ftbquests": surface["ftbquests_display_work"],
        "kubejs": surface["kubejs_display_work"],
        "output_files": DEPLOYMENT_PATHS,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    completion = {
        "family": FAMILY,
        "reviewed_language_keys": language["reviewed_english_keys"],
        "bundled_korean_candidate_keys": sum(
            row["bundled_korean_candidate_keys"] for row in language["mods"].values()
        ),
        "existing_project_values_reused": language["existing_project_values_reused"],
        "existing_project_values_revised": language["existing_project_values_revised"],
        "new_language_values": language["new_language_values"],
        "ftbquests_work": surface["ftbquests_display_work"],
        "kubejs_work": surface["kubejs_display_work"],
        "deployment": deployment,
        "errors": errors,
        "status": (
            "complete"
            if not errors
            and (
                deployment is None or deployment.get("status") == "applied_and_verified"
            )
            else "incomplete"
        ),
    }
    write_json(WORK_ROOT / "family_completion.json", completion)
    return report, errors


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 매니페스트의 백업·해시 검증을 완료 기록에 연결해요."""
    manifest_path = manifest_path.resolve()
    manifest = load_json(manifest_path)
    errors = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 매니페스트 상태가 완료가 아니에요")
    if manifest.get("java_processes"):
        errors.append(
            f"적용 당시 Java 프로세스가 있었어요: {manifest['java_processes']}"
        )
    targets = manifest.get("targets", [])
    if not isinstance(targets, list) or not targets:
        errors.append("적용 대상 기록이 없어요")
        targets = []
    summaries = []
    expected = set(DEPLOYMENT_PATHS)
    for target in targets:
        records = {
            row.get("relative_path"): row
            for row in target.get("files", [])
            if isinstance(row, dict)
        }
        missing = sorted(expected - set(records))
        extra = sorted(set(records) - expected)
        if missing or extra:
            errors.append(f"적용 경로가 달라요: missing={missing}, extra={extra}")
        hash_verified = all(
            records.get(path, {}).get("source_sha256")
            == records.get(path, {}).get("after_sha256")
            for path in expected
        )
        if not hash_verified:
            errors.append("적용 후 세 산출물 중 해시가 다른 파일이 있어요")
        if target.get("unexpected_changes"):
            errors.append(f"예상 밖 적용 변경이 있어요: {target['unexpected_changes']}")
        summaries.append(
            {
                "target_type": target.get("target_type"),
                "target_root": target.get("target_root"),
                "changed_paths": target.get("changed_paths", []),
                "unexpected_changes": target.get("unexpected_changes", []),
                "hash_verified": hash_verified,
            }
        )
    try:
        relative_manifest = manifest_path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        relative_manifest = str(manifest_path)
    report = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "backup_manifest": relative_manifest,
        "expected_paths": DEPLOYMENT_PATHS,
        "targets": summaries,
        "errors": errors,
    }
    write_json(WORK_ROOT / "deployment_report.json", report)
    verify_report, verify_errors = verify()
    return {
        "deployment": report,
        "verification": verify_report["status"],
        "status": "applied_and_verified"
        if not errors and not verify_errors
        else "incomplete",
    }, errors + verify_errors


def run_all() -> tuple[dict[str, object], list[str]]:
    """준비·생성·감사·검증을 순서대로 실행해요."""
    prepared = prepare()
    built = build()
    audit_report, audit_errors = audit()
    verify_report, verify_errors = verify()
    errors = audit_errors + verify_errors
    return {
        "prepare": prepared["status"],
        "build": built["status"],
        "audit": audit_report["status"],
        "verify": verify_report["status"],
        "status": "complete" if not errors else "incomplete",
    }, errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "build", "audit", "verify", "record-deployment", "all"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    if args.command == "prepare":
        result = prepare()
    elif args.command == "build":
        result = build()
    elif args.command == "audit":
        result, errors = audit()
    elif args.command == "verify":
        result, errors = verify()
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        result, errors = record_deployment(args.manifest)
    else:
        result, errors = run_all()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
