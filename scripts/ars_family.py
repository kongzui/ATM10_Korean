#!/usr/bin/env python3
"""Ars Nouveau 모드군의 번역 후보, 관련 콘텐츠와 완료 상태를 관리한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from zipfile import ZipFile

import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/ars_nouveau"
CACHE_PATH = PROJECT_ROOT / "temp/ars_nouveau_auto_candidates.json"
GOOGLE_TRANSLATE = "https://translate.googleapis.com/translate_a/single"
MANUAL_CANDIDATES = {
    "%2$s's poison spores blossomed inside %1$s": (
        "%1$s의 몸속에서 %2$s의 독 포자가 피어났습니다"
    ),
    (
        "All three Technomancer variants (Technomancer, Artificer, Machinaguard) "
        "share these perks when wearing a full set:\n\n"
        "$(li)$(bold)Damage reduction$() - Reduced damage from Create machinery "
        "(e.g. crushers, saws)\n"
        "$(li)$(bold)Schematicannon boost$() - Nearby Schematic Cannons operate "
        "faster\n"
        "$(li)$(bold)Manipulation school$() - Bonus manipulation spell power\n"
        "$(li)$(bold)Goggles$() - The helmet augments your HUD with Create "
        "component info"
    ): (
        "세 가지 테크노맨서 변형(테크노맨서, 아티피서, 마키나가드)은 완전한 "
        "세트를 착용하면 다음 효과를 공유합니다:\n\n"
        "$(li)$(bold)피해 감소$() - Create 기계(예: 분쇄기, 톱)로 받는 피해 감소\n"
        "$(li)$(bold)스키매틱 대포 가속$() - 주변 스키매틱 대포의 작동 속도 증가\n"
        "$(li)$(bold)조작 학파$() - 조작 주문력 증가\n"
        "$(li)$(bold)고글$() - 투구가 HUD에 Create 부품 정보를 표시"
    ),
}
PROPER_NAMES = {
    "Ashguard": "애시가드",
    "Phoenix": "피닉스",
    "Stormguard": "스톰가드",
    "Kirin": "기린",
    "Steamguard": "스팀가드",
    "Bannik": "반니크",
    "Swampguard": "스웜프가드",
    "Hydra": "히드라",
    "Magmaguard": "마그마가드",
    "Typhon": "티폰",
    "Desertguard": "데저트가드",
    "Sphinx": "스핑크스",
    "Omniguard": "옴니가드",
    "Tiamat": "티아마트",
    "Artificer": "아티피서",
    "Machinaguard": "마키나가드",
}
ARMOR_PARTS = {
    "Helmet": "투구",
    "Chestplate": "흉갑",
    "Leggings": "각반",
    "Boots": "장화",
    "Hood": "두건",
    "Tunic": "튜닉",
    "Pants": "바지",
    "Shoes": "신발",
    "Cap": "모자",
    "Set": "세트",
}
ELEMENTS = {
    "Air": "공기",
    "Earth": "대지",
    "Fire": "화염",
    "Water": "물",
    "Anima": "아니마",
    "Necromancy": "강령술",
}
SOURCE_OVERRIDES = {
    "Blue: %s": "파랑: %s",
    "Green: %s": "초록: %s",
    "Red: %s": "빨강: %s",
    "Pitch: %s": "음높이: %s",
    "Volume: %s": "음량: %s",
    "Inventory must be within %s blocks.": "보관함이 %s블록 안에 있어야 합니다.",
    "Lectern must be within %s blocks.": "독서대가 %s블록 안에 있어야 합니다.",
    "%1$s was crushed by %2$s magic blocks": (
        "%1$s은(는) %2$s의 마법 블록에 짓눌렸습니다"
    ),
    "%1$s was frozen to death by %2$s using %3$": (
        "%1$s은(는) %3$을(를) 사용한 %2$s에게 얼어 죽었습니다"
    ),
    "Clear": "비우기",
    "Lock": "잠그기",
    "Unlock": "잠금 해제",
    "Single": "단일",
    "Multiple": "다중",
    "Multi": "다중",
    "Remote": "리모컨",
    "Active:": "작동 중:",
    "Cauterize": "소작",
    "Charm": "현혹",
    "Discharge": "방전",
    "Oxidize": "산화",
    "Feed": "먹이 주기",
    "Ride": "탑승",
    "Stuffed": "과식",
    "Processing": "가공",
    "Create Processing": "Create 가공",
    "Set Perks": "세트 효과",
    "Arcane Wrench": "아케인 렌치",
    "Transmutation": "변환",
    "Spellcaster Bag": "주문 시전자 가방",
    "Trinkets Pouch": "장신구 주머니",
    "Flarecannon": "플레어캐논",
    "Flarecannon Familiar": "플레어캐논 사역마",
    "Siren": "사이렌",
    "Siren Familiar": "사이렌 사역마",
    "Siren Token": "사이렌 조각",
    "Water Jet Origin": "물줄기 발생점",
    "Rogue Air Mage": "떠돌이 공기 마법사",
    "Rogue Earth Mage": "떠돌이 대지 마법사",
    "Rogue Fire Mage": "떠돌이 화염 마법사",
    "Rogue Water Mage": "떠돌이 물 마법사",
    "Enderference": "엔더 방해",
    "Enthralled": "매료",
    "Life Linked": "생명 연결",
    "Mana Shield": "마나 보호막",
    "Static Charged": "정전기 충전",
    "Air Bangle": "공기 팔찌",
    "Earth Bangle": "대지 팔찌",
    "Fire Bangle": "화염 팔찌",
    "Water Bangle": "물 팔찌",
    "Air Focus": "공기 포커스",
    "Earth Focus": "대지 포커스",
    "Fire Focus": "화염 포커스",
    "Water Focus": "물 포커스",
    "Summoning Focus": "소환 포커스",
    "BlockShaping Focus": "블록 조형 포커스",
    "Cheap Damage": "저비용 공격",
    "Heavy Cover": "묵직한 표지",
    "Lucky Cover": "행운의 표지",
    "Keen Cover": "예리한 표지",
    "Sharp Pages": "날카로운 페이지",
    "Slow Power": "느린 위력",
    "Wheel of Fortune": "운명의 수레바퀴",
    "Book Covers": "책 표지",
    "Book Cover: Focus": "책 표지: 포커스",
    "StarbuncleMania": "StarbuncleMania",
    "Enhanced Spell Book Controls": "향상된 주문서 조작",
    "Clear on Auto-Focus": "자동 포커스 시 검색어 지우기",
    "Enable Auto-Focus": "자동 포커스 활성화",
    "Escape to Clear": "Esc 키로 검색어 지우기",
    "Warping Spell Prism": "워프 주문 프리즘",
    "Precise Delay": "정밀 지연",
    "Scryer's Linkage": "예지자의 연결 장치",
    "Temporal Stability Sensor": "시간 안정성 감지기",
    "Portable Brazier Relay": "휴대용 화로 전달체",
    "Warp Scroll Holder": "워프 두루마리 거치대",
    "Arcane Compactor": "아케인 압축기",
    "Arcane Packer": "아케인 포장기",
    "Random Filter": "무작위 필터",
    "Carian Phalanx": "카리아의 검진",
    "Create Geyser": "간헐천 생성",
    "Life Link": "생명 연결",
    "Mist Cloud": "안개 구름",
    "Phantom Grasp": "환영의 손아귀",
    "Water Jet": "물줄기",
    "Advanced Spell Prism": "고급 주문 프리즘",
    "Wind Warper Relay": "바람 워프 전달체",
    "Air Infused Turret": "공기 주입 포탑",
    "Deep Depositor Relay": "심층 공급 전달체",
    "Earth Infused Turret": "대지 주입 포탑",
    "Fiery Collector Relay": "화염 수집 전달체",
    "Fire Infused Turret": "화염 주입 포탑",
    "Manipulation Infused Turret": "조작 주입 포탑",
    "Flow Splitter Relay": "흐름 분배 전달체",
    "Water Infused Turret": "물 주입 포탑",
    "Siren Shrine": "사이렌 제단",
    "Urn of Endless Waters": "무한한 물의 항아리",
    "Mark of Mastery": "숙련의 표식",
    "Focus of Necromancy": "강령술 포커스",
    "Detection": "탐지",
    "Pollination": "수분 촉진",
    "Repulsion": "밀어내기",
    "Enchanter's Horn": "마법 부여사의 뿔피리",
    "Protection of the 4 elements": "네 원소의 보호",
    "Air Essence": "공기 정수",
    "Earth Essence": "대지 정수",
    "Fire Essence": "화염 정수",
    "Water Essence": "물 정수",
    "Arc Projectile": "곡사 투사체",
    "Split": "분할",
    "Bubble Shield": "거품 보호막",
    "Rainbow Prism Lens [REMOVED]": "무지개 프리즘 렌즈 [제거됨]",
    "Novice Spell Book": "초보자의 마도서",
    "Apprentice Spell Book": "마법사의 마도서",
    "Archmage Spell Book": "대마법사의 마도서",
    "Creative Spell Book": "크리에이티브 마도서",
}
KEY_OVERRIDES = {
    "ars_nouveau": {
        "ars_nouveau.page1.source": (
            "마나는 주입 챔버 가속, 장치 작동, 마법 도우미 동력 공급, 포털 생성, "
            "강력한 마법 부여 장치 조합 등에 쓰이는 마법 자원입니다.\n마나링크는 "
            "월드에서 마나를 모아 마나 단지에 집중시키는 특수 장치입니다. 마나 "
            "전달체로 단지 사이의 먼 거리에서도 마나를 옮길 수 있습니다.\n농경 "
            "마나링크와 균사 마나링크는 초반 마나 수급에 좋은 선택입니다."
        ),
        "ars_nouveau.page1.spell_casting": (
            "Ars Nouveau에서는 강력한 주문을 직접 만들 수 있습니다. 창의적인 주문 "
            "제작으로 적을 물리치고, 월드를 바꾸고, 작업을 자동화하고, 멋진 장면을 "
            "연출하는 등 다양한 일을 할 수 있습니다!\n주문 시전을 시작하려면 초보자의 "
            "주문서를 제작하세요. 마나를 사용해 주문을 만들고 저장하고 시전할 수 "
            "있습니다.\n주문서를 업그레이드하고 새 문양을 배우며 마법 장비를 만들면 "
            "더욱 새롭고 강력한 주문을 시전할 수 있습니다."
        ),
        "ars_nouveau.page1.spell_mana": (
            "주문을 시전하면 주문을 구성하는 모든 문양의 총비용만큼 마나를 "
            "소비합니다. 현재 마나 보유량은 화면 왼쪽 아래의 막대에서 볼 수 "
            "있습니다.\n\n소비한 마나는 시간이 지나면 회복됩니다. 마법 아이템이나 "
            "사역마 같은 다른 요소가 마나를 소비하거나 일정량을 점유하기도 "
            "합니다.\n새 문양을 배울 때마다 마나 재생 속도와 최대 보유량이 조금씩 "
            "영구적으로 증가합니다. 주문서 업그레이드, 일부 마법 장비 착용, 마나 "
            "물약 사용으로도 같은 보너스를 얻을 수 있습니다."
        ),
        "ars_nouveau.page.starbuncle_plush": (
            "부드럽고 푹신해요. 아마 아이템을 훔쳐 가지는 않을 거예요."
        ),
        "ars_nouveau.starby_plush_campaign": (
            "지금 Makeship에서 별다람쥐 봉제 인형을 신청하세요! 주문서 또는 낡은 "
            "고서 화면 왼쪽의 봉제 인형 버튼을 확인하세요."
        ),
        "block.ars_nouveau.starbuncle_plush": "별다람쥐 봉제 인형",
        "entity.ars_nouveau.nook": "눅",
        "jukebox_song.ars_nouveau.thistle_the_sound_of_glass": (
            "Thistle - The Sound of Glass"
        ),
    },
    "ars_additions": {
        "ars_additions.page.advanced_dominion_wand": (
            "고급 도미니언 완드는 연결 순서와 여러 블록의 동시 연결을 지원하는 "
            "도미니언 완드의 업그레이드 버전입니다. 원형 메뉴에서 첫 번째/두 번째 "
            "연결 순서와 단일/다중 연결 모드를 바꿀 수 있습니다. 다중 모드에서 "
            "블록을 Shift+우클릭하면 같은 종류로 이어진 블록을 모두 찾아 한 번에 "
            "연결합니다."
        ),
        "ars_additions.page.memory_crystal": (
            "메모리 크리스탈은 지원하는 블록과 개체의 설정을 저장하고 불러옵니다. "
            "지원하는 대상에 Shift+우클릭하면 선택한 슬롯에 설정을 저장하고, 다시 "
            "Shift+우클릭하면 저장한 설정을 불러옵니다. 원형 메뉴에서 10개 슬롯을 "
            "선택할 수 있으며, Shift 원형 메뉴에서는 슬롯을 비우거나 잠가 실수로 "
            "덮어쓰는 일을 막을 수 있습니다."
        ),
        "ars_additions.page.source_spawner": (
            "마나 생성기는 주변 몹 단지를 읽어 소환할 몹을 정합니다. 몹을 소환할 "
            "때마다 주변 마나 단지에서 몹 종류에 따른 양의 마나를 소비합니다. "
            "레드스톤 신호로 끌 수 있으며, 현재 소환 대기 시간에 비례하는 비교기 "
            "신호를 출력합니다."
        ),
        "chat.ars_additions.advanced_dominion_wand.link_success": "연결했습니다",
        "chat.ars_additions.advanced_dominion_wand.multi_link_not_wandable": (
            "%s개 블록을 찾았지만 연결할 수 있는 대상이 없습니다"
        ),
        "chat.ars_additions.advanced_dominion_wand.multi_link_success": (
            "%s/%s개 대상을 연결했습니다"
        ),
        "tooltip.ars_additions.memory_crystal.usage": (
            "Shift+우클릭하여 저장/불러오기"
        ),
    },
    "ars_controle": {
        "ars_controle.glyph.error.generic.error_at_position": (
            "%d번째 위치의 %s에서 오류가 발생했습니다."
        ),
        "ars_controle.target.get.block": "대상 블록: %s, 차원: %s.",
        "ars_controle.target.get.entity": "대상 개체: %s, 차원: %s.",
        "ars_controle.target.set.block": "%s 차원의 %s 블록을 대상으로 설정했습니다.",
        "ars_controle.target.set.none": "대상을 지웠습니다.",
        "ars_controle.target.set.self": "자신을 대상으로 설정했습니다.",
        "ars_controle.remote.error.different_dimension": (
            "다른 차원에 있는 대상은 지정할 수 없습니다."
        ),
        "ars_nouveau.page1.item.ars_controle.remote": (
            "리모컨은 도미니언 완드로 설정할 수 있는 블록과 개체를 멀리서 "
            "설정합니다.\nShift를 누르면 연결의 첫 번째 또는 두 번째 끝을 잠그는 "
            "메뉴가, 누르지 않으면 단일 또는 다중 선택 메뉴가 열립니다.\n먼저 "
            "웅크린 상태로 설정할 대상에 사용하세요."
        ),
    },
    "ars_technica": {
        "ars_technica.glyph_desc.glyph_carve": (
            "같은 아이템 개체를 잘라 계단으로 제작합니다. 돌과 나무에만 "
            "작동합니다. §a[Create 조합: 절단]"
        ),
        "ars_technica.glyph_desc.glyph_pack": (
            "같은 아이템 개체를 압축해 2x2 조합으로 제작합니다. "
            "§a[Create 조합: 포장]"
        ),
        "ars_technica.glyph_desc.glyph_polish": (
            "아이템 개체를 연마된 변형으로 가공합니다. §a[Create 조합: 연마]"
        ),
        "ars_technica.glyph_desc.glyph_obliterate": (
            "비전 망치의 순수한 힘으로 적을 분쇄합니다. 섬세함으로 보강하면 아이템 "
            "개체를 가공할 수 있습니다. §a[Create 조합: 분쇄 휠]"
        ),
        "ars_nouveau.augment_desc.glyph_press_glyph_extract": (
            "아이템으로 압축 조합을 만들 수 있으면 누르기 대신 주변 유체를 포함한 "
            "압축 조합을 사용합니다. 가열 조합에는 제련을 추가하세요."
        ),
        "ars_nouveau.augment_desc.glyph_press_glyph_sensitive": (
            "누르기나 압축 대신 같은 아이템을 2x2 또는 3x3으로 포장합니다."
        ),
        "ars_technica.entry.arcane_wrench": "비전 렌치",
        "ars_technica.page.arcane_wrench": "비전 렌치",
        "ars_technica.page.create_processing.intro": (
            "다음 문양은 Create 가공 공정을 대신할 수 있습니다:"
        ),
        "ars_technica.page.create_processing.depot": (
            "이 공정들은 월드에 놓인 아이템 개체를 처리합니다. 누르기, 연마, "
            "분쇄 및 회전은 Create 디포에서도 작동합니다."
        ),
        "ars_technica.page.armor_set.technomancer": (
            "Create 기계와 조작 학파에 조율된 방어구입니다. 각 부위는 조작 문양을 "
            "증폭하고 분쇄기나 톱 같은 Create 기계로 받는 피해를 줄입니다. 투구는 "
            "HUD에 Create 부품 정보를 표시하며, 전 부위를 장착하면 주변 스키매틱 "
            "대포가 더 빠르게 작동합니다."
        ),
        "ars_technica.page1.processing": (
            "Ars Technica는 누르기, 연마, 혼합, 분쇄 등 Create 방식의 가공을 "
            "수행하는 문양을 추가합니다. 아래 문양에 마우스를 올리면 Create 조합 "
            "정보를 볼 수 있습니다."
        ),
    },
    "not_enough_glyphs": {
        "effect.not_enough_glyphs.stuffed.desc": (
            "너무 많이 먹었습니다! 개체의 크기가 커지고 압착 피해에 더 취약해집니다. "
            "체력이 1/4 미만일 때 압착되면 폭발할 수도 있습니다."
        ),
        "not_enough_glyphs.glyph_name.glyph_feed": "먹이 주기",
        "not_enough_glyphs.glyph_name.glyph_ride": "탑승",
        "not_enough_glyphs.glyph_desc.glyph_feed": (
            "대상에게 강제로 먹이를 주며 시전자의 인벤토리에서 음식 아이템을 "
            "소비합니다. 언데드에게는 작동하지 않습니다. 이 문양은 과식 효과를 "
            "부여하여 대상을 압착 피해에 더 취약하게 만들고, 낮은 체력에서 "
            "압착되면 폭발하게 할 수 있습니다."
        ),
        "not_enough_glyphs.glyph_desc.glyph_ride": (
            "시전자가 대상 개체에 올라타지만 조종할 수는 없습니다. 대부분의 적대적 "
            "몹에게는 작동하지 않습니다."
        ),
        "not_enough_glyphs.page.focus_threads.desc": (
            "주문 결속기에 이 실타래를 장착하면 해당 포커스를 장착한 것처럼 문양 "
            "조합이 해금됩니다. 2레벨 슬롯에서는 같은 학파의 주문에 작은 피해 "
            "보너스도 부여합니다."
        ),
        "not_enough_glyphs.perk_desc.thread_earth_focus": (
            "주문 결속기의 표지 인장입니다. 대지 포커스를 장착한 것처럼 문양 "
            "조합을 활성화합니다."
        ),
    },
    "starbunclemania": {
        "block.starbunclemania.fluid_jar": "유체 격리 단지",
        "item.starbunclemania.fluid_jar": "유체 단지",
        "starbunclemania.adv.desc.fluid_jar": "유체 단지 획득",
        "starbunclemania.page.fluid_jar": (
            "캐스케이딩 아크우드 통나무로 만든 탱크로, 유체를 최대 16양동이까지 "
            "저장합니다. 물약 유체를 저장하고 위에 물약 단지를 놓으면, 플라스크나 "
            "혼합에 사용할 수 있도록 물약 단지로 옮깁니다."
        ),
        "starbunclemania.page.source_condenser": (
            "단지의 마나를 안정된 유체로 응축합니다. 가능하면 아래쪽 탱크로 자동 "
            "배출합니다. 도미니언 완드로 특정 마나 공급원을 연결할 수 있으며, 연결하지 "
            "않으면 주변의 모든 마나 단지에서 마나를 가져옵니다."
        ),
        "starbunclemania.page.robin_mask": (
            "별다람쥐가 여러 보관함에 아이템을 차례로 분배하게 합니다. 이 장신구를 "
            "착용한 별다람쥐는 바닥의 아이템만 주우며, 연결된 목적지 수에 맞춰 한 "
            "보관함에 옮길 수량을 나눈 뒤 다음 보관함으로 이동합니다."
        ),
    },
    "ars_elemancy": {
        "ars_elemancy.page.armor_set.wip": (
            "참고: 방어구 개편에는 많은 리소스 작업이 필요하므로 1.19에서는 경량과 "
            "중량 원소 방어구가 준비되지 않습니다. 현재 제작 가능한 중형 원소 "
            "방어구는 세 유형 모두로 만들 수 있습니다. 업그레이드하면 마법 부여와 "
            "실타래가 유지되지만, 기본 방어구가 3등급이어야 합니다."
        ),
    },
    "ars_elemental": {
        "ars_elemental.familiar_desc.firenando_familiar": (
            "플레어캐논 사역마는 화염 주문 피해를 2 높이고 투사체 주문의 마나 "
            "비용을 20%% 줄입니다. 마그마 크림을 먹이면 잠시 화염 저항을 얻습니다. "
            "플레어캐논 근처에서 결속 의식을 수행해 획득합니다."
        ),
        "ars_elemental.familiar_name.firenando_familiar": "플레어캐논",
        "ars_elemental.familiar_name.siren_familiar": "사이렌",
        "entity.ars_elemental.firenando_entity": "플레어캐논",
        "entity.ars_elemental.siren_entity": "사이렌",
        "ars_elemental.glyph_name.glyph_carian_phalanx": "카리아의 검진",
        "ars_elemental.glyph_name.glyph_cauterize": "소작",
        "ars_elemental.glyph_name.glyph_discharge": "방전",
        "ars_elemental.glyph_name.glyph_oxidize": "산화",
        "ars_elemental.glyph_name.glyph_phantom_grasp": "환영의 손아귀",
        "ars_elemental.glyph_name.glyph_water_jet": "물줄기",
        "ars_elemental.adv.desc.summon_strider": (
            "화염 포커스를 착용하고 군마 소환으로 스트라이더를 소환하세요."
        ),
        "ars_elemental.glyph_desc.glyph_geyser": (
            "짧은 시간 동안 개체를 적시고 위로 밀어 올리는 간헐천을 생성합니다. "
            "증폭은 높이, 광역은 크기를 조절하며, 섬세함을 더하면 수평으로도 "
            "분출할 수 있습니다. 화염 포커스와 함께 사용하면 개체에 불도 붙입니다."
        ),
        "ars_elemental.page1.earth_focus": (
            "이 주문 포커스는 대지 학파에 조율되어 있습니다. 장착하면 이 학파의 "
            "문양이 증폭되고 마나 비용이 줄어듭니다. 하급 포커스는 다른 원소 "
            "학파의 문양을 약화시키며, 상급 포커스는 착용자가 Y 0 아래에 있을 때 "
            "마나 재생 I을 부여합니다."
        ),
        "ars_elemental.page1.air_focus": (
            "이 주문 포커스는 공기 학파에 조율되어 있습니다. 장착하면 이 학파의 "
            "문양이 증폭되고 마나 비용이 줄어듭니다. 하급 포커스는 다른 원소 "
            "학파의 문양을 약화시키며, 상급 포커스는 착용자가 Y 200보다 높이 "
            "있거나 감전 상태일 때 마나 재생 I을 부여합니다."
        ),
        "ars_elemental.page1.fire_focus": (
            "이 주문 포커스는 화염 학파에 조율되어 있습니다. 장착하면 이 학파의 "
            "문양이 증폭되고 마나 비용이 줄어듭니다. 하급 포커스는 다른 원소 "
            "학파의 문양을 약화시키며, 상급 포커스는 착용자가 불타거나 용암 속에 "
            "있을 때 주문 피해 II를 부여합니다."
        ),
        "ars_elemental.page1.water_focus": (
            "이 주문 포커스는 물 학파에 조율되어 있습니다. 장착하면 이 학파의 "
            "문양이 증폭되고 마나 비용이 줄어듭니다. 하급 포커스는 다른 원소 "
            "학파의 문양을 약화시킵니다. 상급 포커스는 착용자가 젖었을 때 마나 "
            "재생 I을, 수영 중일 때 마나 재생 II와 돌고래의 은총을 부여합니다."
        ),
        "effect.ars_elemental.rust.description": (
            "개체의 방어구를 잠시 녹슬게 하여 방어력을 낮춥니다."
        ),
        "ars_elemental.page2.air_focus": (
            "이 포커스는 발사를 강화합니다. 시간 연장으로 보강하면 공중 부양을 "
            "적용합니다. 또한 절단을 강화하여, 결정타를 가할 때 머리나 해골이 "
            "떨어질 확률을 부여합니다."
        ),
        "ars_elemental.page1.elemental_turrets": (
            "마법 포탑에 원소 포커스의 힘을 주입해 일부 능력을 부여할 수 있습니다. "
            "이 포탑의 주문은 해당 포커스의 조합을 발동하며, 주문에 같은 원소 "
            "학파의 문양이 있으면 마나 비용이 65%% 감소합니다."
        ),
        "ars_elemental.page2.flashjack_charm": (
            "이 새를 조절식 또는 원소 포탑에 연결하면 포탑을 가로채 대상을 조준하고 "
            "공격합니다. 대상에 윤곽선을 표시하고 주변 윌드 워커에게 알리기도 합니다. "
            "도미니언 완드로 특정 몹 종류를 대상에서 제외할 수 있습니다."
        ),
        "block.ars_elemental.earth_relay": "심층 공급 전달체",
        "entity.ars_elemental.water_jet": "물줄기 발생점",
        "item.minecraft.potion.effect.enderference_potion": "엔더 방해의 물약",
        "item.minecraft.potion.effect.enderference_potion_long": "엔더 방해의 물약",
        "item.minecraft.potion.effect.enderference_potion_strong": "엔더 방해의 물약",
        "item.minecraft.splash_potion.effect.enderference_potion": (
            "엔더 방해의 투척용 물약"
        ),
        "item.minecraft.splash_potion.effect.enderference_potion_long": (
            "엔더 방해의 투척용 물약"
        ),
        "item.minecraft.splash_potion.effect.enderference_potion_strong": (
            "엔더 방해의 투척용 물약"
        ),
        "item.minecraft.tipped_arrow.effect.enderference_potion": "엔더 방해의 화살",
        "item.minecraft.tipped_arrow.effect.enderference_potion_long": (
            "엔더 방해의 화살"
        ),
        "item.minecraft.tipped_arrow.effect.enderference_potion_strong": (
            "엔더 방해의 화살"
        ),
    },
}

# 기존 번역과 구버전 번역에서 확인된 의미 누락·영문 잔존을 현재 원문 기준으로 고정한다.
QUALITY_OVERRIDES = {
    "ars_nouveau": {
        "ars_nouveau.global_position": "X: %1$d Y: %2$d Z: %3$d, 차원: %4$s",
        "ars_nouveau.page1.spell_casting": (
            "Ars Nouveau에서는 강력한 주문을 직접 만들 수 있습니다. 창의적인 주문 "
            "제작으로 적을 물리치고, 월드를 바꾸고, 작업을 자동화하고, 멋진 장면을 "
            "연출하는 등 다양한 일을 할 수 있습니다!\n주문 시전을 시작하려면 초보자의 "
            "마도서를 제작하세요. 마나를 사용해 주문을 만들고 저장하고 시전할 수 "
            "있습니다.\n마도서를 업그레이드하고 새 문양을 배우며 마법 장비를 만들면 "
            "더욱 새롭고 강력한 주문을 시전할 수 있습니다."
        ),
        "ars_nouveau.page1.spell_mana": (
            "주문을 시전하면 주문을 구성하는 모든 문양의 총비용만큼 마나를 "
            "소비합니다. 현재 마나는 화면 왼쪽 아래의 막대에서 볼 수 있습니다.\n\n"
            "소비한 마나는 시간이 지나면 회복됩니다. 마법 아이템이나 사역마 같은 "
            "다른 요소가 마나를 소비하거나 일정량을 점유하기도 합니다.\n새 문양을 "
            "배울 때마다 마나 재생 속도와 최대 보유량이 조금씩 영구적으로 증가합니다. "
            "마도서 업그레이드, 일부 마법 장비 착용, 마나 물약 사용으로도 같은 "
            "보너스를 얻을 수 있습니다."
        ),
        "ars_nouveau.starby_plush_campaign": (
            "지금 Makeship에서 별다람쥐 봉제 인형을 신청하세요! 마도서 또는 낡은 "
            "고서 화면 왼쪽의 봉제 인형 버튼을 확인하세요."
        ),
        "ars_nouveau.light_message": (
            "Ars Nouveau에는 동적 조명 기능이 내장되어 있습니다. `/ars-light on`으로 "
            "활성화할 수 있으며, 이 안내는 다시 표시되지 않습니다!"
        ),
        "ars_nouveau.store_text": "Redbubble 상점 보기!",
        "ars_nouveau.connection.range": "%s블록 안에서만 연결할 수 있습니다.",
        "ars_nouveau.dynamic_lights.button_on": (
            "동적 조명을 켰습니다. CPU 성능이 낮거나 할당된 RAM이 적으면 렉이 생길 수 "
            "있으며, OptiFine 같은 최적화 모드와 충돌할 수 있습니다."
        ),
        "ars_nouveau.glyph_desc.glyph_delay": (
            "오른쪽에 놓인 주문의 발동을 조금 늦춥니다. 시간 연장 또는 시간 단축으로 "
            "지연 시간을 늘리거나 줄일 수 있습니다."
        ),
        "ars_nouveau.glyph_desc.glyph_interact": (
            "플레이어가 블록이나 개체와 상호 작용하는 것처럼 작동합니다. 레버, 상자, "
            "동물처럼 직접 상호 작용해야 하는 대상에 유용합니다. 섬세함으로 보강하면 "
            "손에 든 아이템을 해당 블록이나 개체에 사용할 수 있습니다."
        ),
        "ars_nouveau.glyph_desc.glyph_name": (
            "주문 이름을 개체나 아이템에 붙입니다. 블록을 대상으로 하면 블록 위의 "
            "개체와 떨어진 아이템에 이름을 붙이고, 자신을 대상으로 하면 보조 손의 "
            "아이템에 이름을 붙입니다. 단축바에 이름표가 있으면 주문 이름 대신 "
            "이름표의 이름을 사용합니다."
        ),
        "ars_nouveau.glyph_desc.glyph_break": (
            "평균 경도의 블록을 부숩니다. 증폭으로 보강하면 채굴 등급이 높아집니다. "
            "섬세함으로 보강하면 곡괭이 대신 가위로 블록을 부순 것처럼 처리합니다."
        ),
        "ars_nouveau.glyph_desc.glyph_bubble": (
            "닿은 몹과 개체를 방울에 가두어 위로 떠오르게 합니다. 방울이 한 틱 이상 "
            "유지된 뒤 안의 개체가 피해를 받으면 방울이 터지며 추가 피해를 줍니다. "
            "시간 연장과 증폭으로 방울의 지속 시간과 피해를 늘릴 수 있습니다."
        ),
        "ars_nouveau.glyph_desc.glyph_conjure_water": (
            "대상 위치에 물을 놓거나 불이 붙은 개체의 불을 끕니다. 시간 연장으로 "
            "보강하면 개체가 젖은 상태로 더 오래 유지됩니다."
        ),
        "ars_nouveau.glyph_desc.glyph_ignite": (
            "블록과 몹에 짧은 시간 불을 붙입니다. 섬세함으로 보강하면 더 빨리 "
            "사라지고 퍼지거나 블록을 파괴하지 않는 마법 불꽃을 소환합니다."
        ),
        "ars_nouveau.glyph_desc.glyph_infuse": (
            "인벤토리의 물약이나 플라스크 효과를 대상에게 주입합니다. 광역으로 "
            "보강하면 대상 위치에 투척용 물약을, 시간 연장으로 보강하면 잔류형 물약을 "
            "생성합니다. 시전자 블록은 인접한 물약 단지에서 물약을 가져올 수 있습니다."
        ),
        "ars_nouveau.glyph_desc.glyph_light": (
            "블록에 시전하면 영구 광원을 만듭니다. 증폭으로 발광석 밝기까지 높이거나 "
            "약화로 낮출 수 있습니다. 자신에게 시전하면 야간 투시를, 다른 개체 또는 "
            "섬세함으로 보강한 대상에게는 야간 투시와 발광을 부여합니다. 섬세함을 "
            "사용하면 발광 색상이 주문 색을 따르며, 입자는 마도서의 주문 스타일 "
            "메뉴에서 설정할 수 있습니다."
        ),
        "ars_nouveau.glyph_desc.glyph_phantom_block": (
            "잠시 후 사라지는 임시 블록을 만듭니다. 증폭으로 보강하면 영구 블록이 "
            "되며, 디스펠을 시전하면 즉시 파괴됩니다. 개체에게 시전하면 개체 주변의 "
            "위쪽 방향에 블록을 만듭니다."
        ),
        "ars_nouveau.glyph_desc.glyph_place_block": (
            "시전자의 인벤토리에서 블록을 놓습니다. 플레이어가 시전하면 단축바의 "
            "블록부터 사용합니다. 개체에게 시전하면 개체 아래에서 위쪽 방향으로 "
            "블록을 놓습니다. 섬세함 1회는 시전자가 바라보는 방향에, 2회는 반대 "
            "방향에 블록을 놓습니다."
        ),
        "ars_nouveau.glyph_desc.glyph_toss": (
            "시전자의 인벤토리에서 아이템을 꺼내 대상 위치에 놓습니다. 보관함에 "
            "시전하면 아이템을 안에 넣으려 시도합니다. 기본 수량은 64개이며 약화할 "
            "때마다 절반, 증폭할 때마다 두 배가 됩니다. 무작위로 보강하면 무작위 "
            "아이템 스택을 선택합니다."
        ),
        "ars_nouveau.alakarkinos.set_home": (
            "보금자리를 설정했습니다. 수평 3블록, 수직 1블록 안에 마나와 자갈 또는 "
            "모래를 놓으세요."
        ),
        "ars_nouveau.page4.alakarkinos_charm": (
            "알라카르키노스는 결속된 보관함에서 수평 3블록, 수직 1블록 안에 놓인 "
            "자갈이나 모래를 찾습니다. 블록을 아이템으로 바꾸려면 보관함 근처에 "
            "마나를 공급해야 합니다. 잠시 뒤 알라카르키노스가 자갈이나 모래를 "
            "파괴하고 얻은 아이템을 보관함에 넣습니다."
        ),
        "tooltip.alakarkinos_shard2": "귀 뒤에 뭔가 숨기고 있나요?",
        "ars_nouveau.page.dominion_wand": (
            "마나 전달체와 자동화 개체를 설정하는 도구입니다. 전송 경로를 만들려면 "
            "먼저 마나를 가져올 대상에 완드를 사용하고, 다음으로 보낼 블록에 "
            "사용하세요. 마나 단지→마나 전달체, 전달체→전달체, 전달체→마나 단지 "
            "등을 연결할 수 있습니다. 전달체에 웅크린 채 사용하면 연결을 지웁니다. "
            "원형 메뉴의 엄격 모드에서는 사용할 블록 면도 지정할 수 있습니다."
        ),
        "ars_nouveau.page2.warp_portal": (
            "포털은 가로나 세로로 만들 수 있으며 크기는 1x1부터 21x21까지입니다. "
            "생성한 뒤 순간이동할 때는 마나를 소비하지 않습니다. 포털에 도미니언 "
            "완드를 사용하면 포털의 무늬가 바뀝니다."
        ),
        "ars_nouveau.page2.storage": (
            "열람대에 인접한 결속되지 않은 보관함에 아이템을 넣으면 열람대로 자동 "
            "반입됩니다. 레드스톤 신호를 주면 자동 반입을 끌 수 있습니다. 열람대를 "
            "'메인' 열람대에 연결하면 원래 열람대의 표시와 접근 범위가 확장되며, "
            "30블록 안에서 이 연결을 계속 이어 갈 수 있습니다. 다른 열람대에 연결된 "
            "열람대는 보관함과 연결하거나 책고룡을 받을 수 없습니다."
        ),
        "ars_nouveau.page5.wixie_charm": (
            "윅시는 주변 물약 단지와 아이템을 사용해 물약을 자동 제조합니다. 물이 "
            "필요한 물약에는 윅시가 직접 물을 공급하고, 다른 물약을 재료로 쓰는 경우 "
            "주변 물약 단지에서 가져옵니다. 제조가 끝나면 물약 3회분을 주변 물약 "
            "단지에 넣습니다. 시작하려면 빈 물약 단지를 놓고 가마솥에 어색한 물약을 "
            "우클릭한 뒤, 주변 상자에 네더 사마귀를 공급하세요."
        ),
        "ars_nouveau.page1.reactive_enchantment": (
            "반응성 마법 부여가 적용된 아이템은 휘두를 때 일정 확률로 주문을 "
            "시전합니다. 아이템에 새겨질 주문은 주문 양피지에 기록된 주문으로 "
            "결정됩니다."
        ),
        "ars_nouveau.page.runic_chalk": (
            "룬 분필로 땅에 영구 룬을 그리면 위를 지나가는 개체에게 주문을 "
            "시전합니다. 필기 작업대에서 주문 양피지에 주문을 새겨 룬에 지정하세요. "
            "주문을 시전한 룬은 충전이 사라지며 주변 마나 단지에서 스스로 다시 "
            "충전합니다. 임시 룬에 룬 분필을 사용하면 영구 룬으로 바뀌고, 룬에 "
            "정수를 사용하면 무늬가 바뀝니다."
        ),
        "ars_nouveau.page2.shapers_focus": (
            "블록을 바꾸거나 만들면 주문의 나머지가 새 블록에도 이어집니다. 예를 "
            "들어 빙결→파괴는 블록을 얼린 뒤 그 블록에 파괴를 시전합니다. 포커스가 "
            "없으면 파괴는 처음 적중한 블록에만 적용됩니다. 마법 블록 생성, 빙결, "
            "파괴, 교환, 블록 배치 등의 효과가 대상을 이어 주며, 광역을 적용하면 "
            "영향받은 모든 블록에 주문이 이어집니다."
        ),
        "ars_nouveau.page3.shapers_focus": (
            "블록을 이동시키는 효과는 이동하는 블록에 주문의 나머지를 복제합니다. "
            "마법 블록 생성→발사→지연→밀치기를 사용하면 바라보는 방향으로 날아가는 "
            "블록에서 주문이 이어지는 모습을 볼 수 있습니다. 이 대상 지정은 이동한 "
            "모든 블록에 적용되며, 블록 이동 효과에 광역을 더하면 여러 블록을 한꺼번에 "
            "조작할 수 있습니다."
        ),
        "ars_nouveau.page.dowsing_rod": (
            "수맥봉을 사용하면 잠시 싹트는 자수정 투시와 마법 탐지 효과를 얻습니다. "
            "마법 탐지는 75블록 안의 마법 생물을 빛나게 합니다. 수맥봉은 사용할 수 "
            "있는 횟수가 제한되어 있습니다."
        ),
        "ars_nouveau.page1.repository": (
            "저장고 하나에는 큰 상자 하나만큼의 아이템을 보관할 수 있습니다. 이름을 "
            "붙이면 툴팁에 표시되고 아이템으로 떨어뜨려도 유지되어, 저장소 열람대에 "
            "이름 붙은 탭을 만들 때 유용합니다. 저장고 목록은 서로 연결된 저장고 "
            "체인의 대리 블록으로 작동하며, 아이템을 넣을 때 각 저장고의 필터 "
            "두루마리를 따릅니다."
        ),
        "ars_nouveau.page.enchanters_shield": (
            "피해를 막으면 잠시 마나 재생과 주문 피해 증가 효과를 얻습니다. 또한 이 "
            "방패는 착용자의 마나를 사용해 서서히 스스로 수리됩니다."
        ),
        "ars_nouveau.page.potion_jar": (
            "물약을 최대 100회분 저장하는 단지입니다. 빈 병, 물약 플라스크 또는 "
            "화살을 사용해 물약을 꺼낼 수 있습니다. 윅시는 물약 자동 제조에 이 "
            "단지를 사용합니다. 웅크린 채 도미니언 완드를 사용하면 현재 물약으로 "
            "잠글 수 있으며, 잠긴 단지는 윅시에게서 그 물약만 받습니다. 비교기와도 "
            "함께 사용할 수 있습니다."
        ),
        "ars_nouveau.page2.armor_upgrading": (
            "방어구에도 세 티어가 있으며, 이 항목의 업그레이드 조합과 마법 부여 "
            "장치를 사용해 티어를 높일 수 있습니다. 티어가 오를 때마다 방어구가 "
            "제공하는 마나 재생량과 실타래 슬롯의 수·크기가 늘어납니다."
        ),
        "ars_nouveau.augment_desc.glyph_light_glyph_extend_time": (
            "광원이 영구적이지 않고 임시로 바뀌며 더 오래 지속됩니다. 발광과 야간 "
            "투시의 지속 시간에도 영향을 줍니다."
        ),
        "ars_nouveau.perk_desc.thread_repairing": (
            "마나를 서서히 소비해 모든 마법 방어구와 마법 부여자의 아이템을 "
            "수리합니다. 레벨이 높을수록 수리 속도가 빨라집니다. 이 효과는 실타래가 "
            "적용된 아이템뿐 아니라 모든 관련 아이템에 적용됩니다. 3레벨 이상의 "
            "슬롯에 장착하면 착용 중인 모든 마법 방어구가 파괴되지 않습니다."
        ),
        "ars_nouveau.page1.whirlisprig_charm": (
            "윌스프링은 숲이 우거진 지역에서만 발견되는 호기심 많은 자연 정령입니다. "
            "소환한 윌스프링에게 보금자리를 마련해 주면 주변에 있는 나무, 작물, 씨앗, "
            "꽃 같은 자연 재료를 생산합니다. 야생 윌스프링 근처에서 나무를 키우면 "
            "친해져 윌스프링 조각을 떨어뜨립니다."
        ),
        "ars_nouveau.page5.whirlisprig_charm": (
            "참고: 블록을 배치한 뒤 윌스프링의 기분이 갱신되기까지 몇 분이 걸릴 수 "
            "있습니다. 윌스프링은 다양성을 중요하게 여기며, 같은 블록이 너무 많으면 "
            "더 이상 행복도에 반영되지 않습니다."
        ),
    },
    "ars_additions": {
        "ars_additions.page.source_spawner": (
            "마나 스포너는 주변 격리 단지에 든 몹을 읽어 소환 대상을 정합니다. 몹을 "
            "소환할 때마다 주변 마나 단지에서 몹 종류에 따른 양의 마나를 소비합니다. "
            "레드스톤 신호로 끌 수 있으며, 현재 소환 대기 시간에 비례하는 비교기 "
            "신호를 출력합니다."
        ),
        "tooltip.ars_additions.warp_index.bound": "좌표 (%s, %s, %s), 차원 %s에 귀속됨",
        "ars_additions.page.bulk_scribing": "대량 각인",
        "ars_additions.page1.bulk_scribing": (
            "주입 챔버 옆 받침대에 마도서나 주문이 새겨진 주문 양피지를 놓고, 주입 "
            "챔버 안에는 빈 양피지 또는 주문을 새길 다른 아이템을 넣으면 여러 아이템에 "
            "한꺼번에 주문을 각인할 수 있습니다."
        ),
        "memory_handler.ars_additions.spell_sensor.on_resolve": "모드: 주문 처리 시",
        "ars_additions.page.ender_source_jar": (
            "엔더 마나 단지는 서로 연결된 공용 마나 저장 공간을 사용합니다. 어느 곳에 "
            "설치한 엔더 마나 단지든 같은 마나를 공유하므로, 어디서나 저장된 마나를 "
            "사용할 수 있습니다."
        ),
        "ars_additions.page.imbued_spell_parchment": (
            "주문 양피지에 마나를 주입하면 플레이어의 마나를 소비하지 않고 주문을 "
            "시전할 수 있습니다. 주입된 주문 양피지를 사용하려면 사용 버튼을 누르고 "
            "있어 양피지의 마나를 모은 뒤 방출해야 합니다. 마나 100만큼을 모으는 데 "
            "약 0.5초가 걸리므로 큰 주문일수록 시전 시간이 길어집니다."
        ),
        "ars_additions.page1.nexus_tower": (
            "넥서스 탑은 마나 지맥이 모이는 지점에 세워져, 월드의 자연 마나를 이용해 "
            "더 쉽게 먼 곳으로 이동할 수 있게 합니다."
        ),
        "ars_additions.page2.warp_nexus": (
            "넥서스 탑 안의 워프 넥서스는 마나 지맥 위에 있어 작동할 때 마나가 "
            "필요하지 않습니다. 다른 곳으로 옮긴 워프 넥서스는 순간이동 한 번에 마나 "
            "1,000을 소비합니다."
        ),
    },
    "ars_controle": {
        "ars_controle.glyph.error.generic.error_at_position": (
            "%s에서 오류가 발생했습니다(위치: %d)."
        ),
        "ars_controle.glyph_desc.glyph_precise_delay": (
            "시간 연장 보강 수에 따라 주문의 나머지 부분을 (2 ^ 보강 수)틱만큼 "
            "지연시킵니다."
        ),
        "ars_controle.glyph_desc.glyph_filter_above": (
            "시전자보다 위쪽에서만 주문의 나머지를 처리합니다."
        ),
        "ars_controle.glyph_desc.glyph_filter_below": (
            "시전자보다 아래쪽에서만 주문의 나머지를 처리합니다."
        ),
        "ars_controle.glyph_desc.glyph_filter_level": (
            "시전자와 같은 높이에서만 주문의 나머지를 처리합니다."
        ),
        "ars_controle.glyph_desc.glyph_filter_not": (
            "다음 필터의 결과가 거짓일 때만 주문의 나머지를 처리합니다."
        ),
        "ars_controle.glyph_desc.glyph_filter_or": (
            "다음 두 필터 중 하나라도 참일 때만 주문의 나머지를 처리합니다."
        ),
        "ars_controle.glyph_desc.glyph_filter_xnor": (
            "다음 두 필터의 결과가 같을 때만 주문의 나머지를 처리합니다."
        ),
        "ars_controle.glyph_desc.glyph_filter_xor": (
            "다음 두 필터 중 하나만 참일 때 주문의 나머지를 처리합니다."
        ),
        "ars_nouveau.augment_desc.glyph_filter_random_glyph_amplify": (
            "주문 처리 확률을 높입니다."
        ),
        "ars_nouveau.augment_desc.glyph_filter_random_glyph_dampen": (
            "주문 처리 확률을 낮춥니다."
        ),
        "ars_nouveau.spell.validation.adding.binary_filters.next_two_not_filters": (
            "%s 뒤의 문양 두 개는 필터여야 합니다."
        ),
        "ars_nouveau.spell.validation.adding.unary_filters.next_not_filter": (
            "%s 뒤의 문양은 필터여야 합니다."
        ),
        "ars_nouveau.spell.validation.exists.binary_filters.next_two_not_filters": (
            "%s 뒤의 문양 두 개는 필터여야 합니다."
        ),
        "ars_nouveau.spell.validation.exists.unary_filters.next_not_filter": (
            "%s 뒤의 문양은 필터여야 합니다."
        ),
        "ars_controle.remote.set_target": "원격 대상을 %s(으)로 설정했습니다(차원: %s).",
        "ars_controle.target.set.block": "좌표 %s(차원: %s)의 블록을 대상으로 설정했습니다.",
        "ars_controle.target.set.entity": "개체 %s(차원: %s)을(를) 대상으로 설정했습니다.",
        "ars_nouveau.page1.block.ars_controle.scryers_linkage": (
            "예지자의 연결 장치는 다른 블록과 연결되어, 멀리 떨어진 기계도 연결한 "
            "블록과 상호 작용할 수 있게 합니다. 아이템, 유체, 에너지, 레드스톤 등 "
            "여러 요소를 전달할 수 있습니다. 설정하려면 먼저 연결할 블록에 도미니언 "
            "완드를 사용한 뒤 이 연결 장치에 사용하세요."
        ),
    },
    "ars_technica": {
        "ars_technica.effect_augment_desc.glyph_whirl_glyph_conjure_water": (
            "회오리와 함께 사용: 세척(물 튀기기) 가공"
        ),
        "ars_technica.effect_augment_desc.glyph_whirl_glyph_flare": (
            "회오리와 함께 사용: 훈연 가공"
        ),
        "ars_technica.effect_augment_desc.glyph_whirl_glyph_smelt": (
            "회오리와 함께 사용: 제련 가공"
        ),
        "ars_technica.effect_augment_desc.glyph_whirl_glyph_hex": (
            "회오리와 함께 사용: 영혼 불어넣기 가공"
        ),
        "ars_technica.entry.arcane_wrench": "아케인 렌치",
        "ars_technica.page.arcane_wrench": "아케인 렌치",
        "ars_technica.page1.create_processing": (
            "다음 문양은 Create 가공 공정을 대신할 수 있습니다:\n\n"
            "이 문양들은 월드에 놓인 아이템 개체를 가공합니다. 누르기, 연마, 분쇄, "
            "회오리는 Create 디포 위에서도 작동합니다."
        ),
        "ars_technica.page2.processing": (
            "디포 지원: Create 디포에 시전할 때는 누르기, 연마, 분쇄, 회오리만 "
            "작동합니다. 디포에 시전하면 내부 아이템 가공을 자동화할 수 있습니다.\n\n"
            "깎기, 포장, 융합은 월드의 아이템 개체에만 작동하며 디포 자동화를 "
            "지원하지 않습니다."
        ),
    },
    "ars_elemancy": {
        "ars_elemental.armor_set.medium.desc": (
            "해당 원소의 피해를 흡수하면 잠시 마나 비용 감소 효과를 얻습니다. 전 "
            "부위를 착용하면 흡수한 피해 일부를 마나로 전환합니다."
        ),
        "ars_elemental.armor_set.school_set.desc": "학파 세트 보너스(같은 원소 4부위)",
        "ars_elemental.armor_set.set_bonus.desc": "방어구 세트 보너스(2부위 또는 4부위)",
        "ars_elemental.armor_set.tempest_light.desc": (
            "물과 공기 학파에 조율되어 기린과 네레이드 세트의 효과를 결합합니다."
        ),
        "ars_elemental.armor_set.tempest_heavy.desc": (
            "물과 공기 학파에 조율되어 스톰가드와 윈터가드 세트의 효과를 결합합니다."
        ),
        "ars_elemental.armor_set.mire_light.desc": (
            "물과 대지 학파에 조율되어 네레이드와 님프 세트의 효과를 결합합니다."
        ),
        "ars_elemental.armor_set.mire_heavy.desc": (
            "물과 대지 학파에 조율되어 윈터가드와 윌드가드 세트의 효과를 결합합니다."
        ),
        "ars_elemental.armor_set.cinder_light.desc": (
            "화염과 공기 학파에 조율되어 파이로매니악과 올림피안 세트의 효과를 결합합니다."
        ),
        "ars_elemental.armor_set.cinder_heavy.desc": (
            "화염과 공기 학파에 조율되어 네더가드와 썬더가드 세트의 효과를 결합합니다."
        ),
        "ars_elemental.armor_set.vapor_light.desc": (
            "화염과 물 학파에 조율되어 파이로매니악과 네레이드 세트의 효과를 결합합니다."
        ),
        "ars_elemental.armor_set.vapor_heavy.desc": (
            "화염과 물 학파에 조율되어 네더가드와 윈터가드 세트의 효과를 결합합니다."
        ),
        "ars_elemental.armor_set.silt_light.desc": (
            "대지와 공기 학파에 조율되어 님프와 올림피안 세트의 효과를 결합합니다."
        ),
        "ars_elemental.armor_set.silt_heavy.desc": (
            "대지와 공기 학파에 조율되어 윌드가드와 썬더가드 세트의 효과를 결합합니다."
        ),
        "ars_elemental.armor_set.lava_light.desc": (
            "대지와 화염 학파에 조율되어 님프와 파이로매니악 세트의 효과를 결합합니다."
        ),
        "ars_elemental.armor_set.lava_heavy.desc": (
            "대지와 화염 학파에 조율되어 네더가드와 윌드가드 세트의 효과를 결합합니다."
        ),
    },
    "ars_elemental": {
        "ars_elemental.adv.desc.air_focus": "상급 공기 포커스 획득",
        "ars_elemental.adv.desc.earth_focus": "상급 대지 포커스 획득",
        "ars_elemental.adv.desc.fire_focus": "상급 화염 포커스 획득",
        "ars_elemental.adv.desc.water_focus": "상급 물 포커스 획득",
        "ars_elemental.adv.desc.lesser_air_focus": "하급 공기 포커스 획득",
        "ars_elemental.adv.desc.lesser_earth_focus": "하급 대지 포커스 획득",
        "ars_elemental.adv.desc.lesser_fire_focus": "하급 화염 포커스 획득",
        "ars_elemental.adv.desc.lesser_water_focus": "하급 물 포커스 획득",
        "ars_elemental.adv.desc.spore_blossom": (
            "성장 또는 독 포자로 언데드를 처치해 포자 꽃을 획득하세요"
        ),
        "ars_elemental.adv.title.lesser_air_focus": "공기의 길",
        "ars_elemental.adv.title.lesser_earth_focus": "대지의 길",
        "ars_elemental.adv.title.lesser_fire_focus": "화염의 길",
        "ars_elemental.adv.title.lesser_water_focus": "물의 길",
        "ars_elemental.adv.title.levitation": "셜커예요. 셜키어가 아니라요",
        "ars_elemental.armor_set.air.desc": (
            "공기 계열 피해를 일부 흡수하고 낙하 피해를 크게 줄입니다."
        ),
        "ars_elemental.armor_set.aqua.desc": (
            "물 계열 피해를 일부 흡수하고 익사 직전에 호흡 게이지를 채웁니다."
        ),
        "ars_elemental.armor_set.earth.desc": (
            "대지 계열 피해를 일부 흡수하고, 지하 깊은 곳에서 굶기 직전이면 "
            "허기를 채웁니다."
        ),
        "ars_elemental.armor_set.fire.desc": (
            "화염 계열 피해를 일부 흡수하고 붙은 불을 즉시 끕니다."
        ),
        "ars_elemental.armor_set.earth.name": "대지의 양분",
        "ars_elemental.familiar_desc.flashjack_familiar": (
            "플래시잭 사역마는 번개 주문 피해를 2 높이고 이동 계열 주문의 마나 "
            "비용을 20% 줄입니다. 플래시파인을 먹이면 잠시 신속과 야간 투시를 "
            "얻습니다. 플래시잭 근처에서 결속 의식을 수행해 획득합니다."
        ),
        "ars_elemental.familiar_desc.siren_familiar": (
            "사이렌 사역마는 물 주문 피해를 2 높입니다. 물속에서는 소환자에게 "
            "돌고래의 우아함 II를 부여합니다. 사이렌 근처에서 결속 의식을 수행해 "
            "획득합니다."
        ),
        "ars_elemental.glyph_name.glyph_arc_projectile": "곡사 투사체",
        "ars_elemental.glyph_name.glyph_bubble_shield": "거품 보호막",
        "ars_elemental.glyph_desc.glyph_bubble_shield": (
            "피해를 받을 때 마나를 소비해 피해를 줄이는 보호막을 만듭니다. 약화 "
            "효과가 대상에게 적용되는 것을 막을 수도 있으며, 방어 중 마나가 바닥나면 "
            "사라집니다. 마법 불꽃도 막아 줍니다."
        ),
        "ars_elemental.glyph_desc.glyph_conjure_terrain": (
            "흙이나 다른 지형 블록을 놓습니다. 광역과 관통으로 더 많은 블록을 놓을 "
            "수 있습니다. 증폭 1회는 조약돌, 2회는 심층암 조약돌을 놓습니다. 물 생성 "
            "뒤에 사용하면 진흙을, 증폭과 제련을 조합하면 돌 또는 심층암을, 분쇄 뒤에 "
            "사용하면 모래를 놓으며 증폭하면 사암을 놓습니다."
        ),
        "ars_elemental.glyph_desc.glyph_homing_projectile": (
            "가장 가까운 개체를 찾아 추적하는 투사체를 발사합니다. 유효한 대상이 "
            "없으면 일반 투사체처럼 움직입니다. 섬세함으로 보강해야 플레이어도 "
            "대상으로 삼습니다."
        ),
        "ars_elemental.glyph_desc.glyph_life_link": (
            "시전자와 대상의 생명력을 연결합니다. 시전자가 받는 피해는 대상과 "
            "나누고, 대상이 받는 회복은 시전자와 똑같이 나눕니다. 섬세함은 연결 "
            "방향을 반대로 바꾸며, 절단은 양쪽의 생명 연결을 끊습니다."
        ),
        "ars_elemental.glyph_desc.glyph_propagator_homing": (
            "주문의 나머지를 유도 투사체로 바꾸어, 적중한 곳에서 시전자가 바라보는 "
            "방향으로 발사합니다."
        ),
        "ars_elemental.glyph_desc.glyph_spike": (
            "닿은 개체에게 피해를 주는 뾰족한 점적석을 만듭니다. 광역과 관통은 "
            "너비와 높이, 시간 연장은 지속 시간, 증폭은 피해를 늘립니다. 설치할 수 "
            "없으면 낙하하는 점적석을 대신 소환하며, 이때는 증폭만 적용되어 낙하 "
            "높이에 따른 피해를 늘립니다."
        ),
        "ars_elemental.glyph_desc.glyph_watery_grave": (
            "대상을 익사시킵니다. 호흡 게이지를 줄이고, 모두 소진되면 익사 피해를 "
            "줍니다. 시간 연장으로 보강하면 잠시 대상을 아래로 끌어당겨 수면으로 "
            "헤엄쳐 올라가지 못하게 합니다."
        ),
        "ars_elemental.lens.pierce": (
            "프리즘에 마나를 공급하면 방향을 바꾼 투사체가 더 많은 블록과 개체를 "
            "관통합니다."
        ),
        "ars_elemental.lens.rgb": "방향을 바꾼 투사체의 색상이 계속 순환합니다.",
        "ars_elemental.page.armor_set.air": (
            "공기 학파에 조율된 방어구입니다. 각 부위는 공기 문양을 강화하고 마나 "
            "비용을 줄이며, 낙하·비행 중 벽 충돌·번개 같은 공기 계열 피해를 "
            "줄입니다.$(br)전 부위를 착용하면 줄인 피해를 마나로 바꾸고 낙하 피해를 "
            "더욱 크게 줄입니다."
        ),
        "ars_elemental.page.armor_set.aqua": (
            "물 학파에 조율된 방어구입니다. 각 부위는 물 문양을 강화하고 마나 비용을 "
            "줄이며, 익사·동결·번개 같은 물 계열 피해를 줄입니다.$(br)전 부위를 "
            "착용하면 줄인 피해를 마나로 바꾸고 익사 직전에 호흡 게이지를 채웁니다."
        ),
        "ars_elemental.page.armor_set.earth": (
            "대지 학파에 조율된 방어구입니다. 각 부위는 대지 문양을 강화하고 마나 "
            "비용을 줄이며, 굶주림·달콤한 열매 덤불·선인장·압착 같은 대지 계열 "
            "피해를 줄입니다.$(br)전 부위를 착용하면 줄인 피해를 마나로 바꾸고, 지하 "
            "깊은 곳에서 굶기 직전이면 허기를 채웁니다."
        ),
        "ars_elemental.page.armor_set.fire": (
            "화염 학파에 조율된 방어구입니다. 각 부위는 화염 문양을 강화하고 마나 "
            "비용을 줄이며, 용암·드래곤 브레스·마그마 같은 화염 계열 피해를 "
            "줄입니다.$(br)전 부위를 착용하면 줄인 피해를 마나로 바꾸고 붙은 불을 "
            "즉시 끕니다."
        ),
        "ars_elemental.page.armor_set.wip": (
            "참고: 방어구 개편에는 많은 리소스 작업이 필요하므로 경량과 중량 원소 "
            "방어구는 아직 중형 방어구의 외형을 사용합니다. 업그레이드하면 마법 "
            "부여와 실타래가 유지되지만, 기본 방어구가 3티어여야 합니다."
        ),
        "ars_elemental.page.book_protection": (
            "이 마도서 업그레이드는 선인장이나 용암처럼 대부분의 피해로부터 마도서를 "
            "보호합니다. 다만 공허에서는 안전을 보장하지 않습니다. 금색 장식은 "
            "네더라이트처럼 검게 바뀌며, 클라이언트 설정에서 이 효과를 끌 수 있습니다."
        ),
        "ars_elemental.page.curio_bag": (
            "마법 장신구가 인벤토리를 가득 채운다면 메이지블룸 섬유로 장신구 주머니를 "
            "만들어 보세요. 단축바나 Curios 슬롯에 있을 때 "
            "$(k:ars_elemental.open_pouch) 키로 열 수 있습니다. 더 크고 염색할 수 있는 "
            "주문시전자 가방으로 업그레이드할 수도 있습니다."
        ),
        "ars_elemental.page1.curio_bag": (
            "마법 장신구가 인벤토리를 가득 채운다면 메이지블룸 섬유로 장신구 주머니를 "
            "만들어 보세요. 단축바나 Curios 슬롯에 있을 때 "
            "$(k:ars_elemental.open_pouch) 키로 열 수 있습니다. 더 크고 염색할 수 있는 "
            "주문시전자 가방으로 업그레이드할 수도 있습니다."
        ),
        "ars_elemental.page.elemental_tweaks": (
            "Ars Elemental이 설치되면 다음 변경 사항이 적용됩니다:$(br)마법 부여사의 "
            "방패로 막을 때 반응 효과가 발동할 수 있습니다.$(br)소환한 번개는 아이템을 "
            "파괴하지 않습니다.$(br)분쇄를 섬세함으로 보강하면 아이템을 가공할 수 "
            "있습니다.$(br)급속 냉각은 얼어붙는 중인 몹에게 더 큰 피해를 줍니다.$(br)"
            "점화는 얼음 블록을 물로 녹입니다."
        ),
        "ars_elemental.page.everfull_urn": (
            "이 마법 항아리는 마나를 물로 바꿉니다. 도미니언 완드로 가마솥이나 "
            "약제상을 항아리에 연결하면 적은 마나를 소비해 자동으로 물을 채웁니다."
        ),
        "ars_elemental.page.anima": (
            "아니마 학파는 삶과 죽음, 그 사이를 이해하려던 소환과 보호 학파의 "
            "마법사들에게서 갈라져 나왔습니다. 이 학파의 정수는 삶과 죽음 사이를 "
            "순환합니다. 실험에 따르면 말도 살, 스켈레톤, 좀비 형태를 차례로 "
            "오간다는데, 과연 처음과 같은 말일까요?"
        ),
        "ars_elemental.page.anima_bangle": (
            "아니마 주문의 피해를 높이는 팔찌입니다. 팔에서 삶과 죽음의 순환이 "
            "느껴지며, 적중한 적을 무작위로 회복시키거나 시들게 하고 착용자의 최대 "
            "체력도 조금 높입니다."
        ),
        "ars_elemental.page.necrotic_focus": (
            "소환 포커스에 사악한 에너지를 주입하면 강령술 포커스로 타락시킬 수 "
            "있습니다. 아니마 학파 문양에는 시간 연장 2회가 무료로 적용되고, 회복에는 "
            "증폭 2회가 적용되며, 현혹은 언데드에게 성공할 확률이 크게 높아집니다. "
            "군마 소환은 물속에서 걷고 숨 쉴 수 있는 해골 군마 소환으로 바뀝니다."
        ),
        "ars_elemental.page.schools": (
            "대부분의 문양은 특정 마법 학파에 속합니다. 원소 학파에는 화염, 물, 공기, "
            "대지가 있으며, 그 밖에 조작, 소환, 보호, 아니마 학파가 있습니다. 마법 "
            "장비는 특정 학파에 조율되어 그 학파의 문양이 든 주문을 강화하거나 마나 "
            "비용을 줄일 수 있습니다."
        ),
        "ars_elemental.page1.base_bangle": (
            "주문 피해를 일정 확률로 높이는 마법 장신구입니다. 아직 마법이 불안정하지만 "
            "특정 학파에 조율하면 능력을 안정시킬 수 있을지도 모릅니다."
        ),
        "ars_elemental.page1.mark_of_mastery": (
            "원소 방어구 세트는 네 원소 학파에 조율되어 있습니다. 각 부위는 해당 "
            "학파의 문양을 강화하고 마나 비용을 줄이며, 관련 원소 피해를 줄입니다. 전 "
            "부위를 착용하면 줄인 피해 일부를 마나로 바꾸고 특수 효과를 발동할 수 "
            "있습니다."
        ),
        "ars_elemental.page2.mermaid": (
            "사이렌 제단은 시간이 지나면 낚시 전리품을 만들며, 주기마다 마나를 "
            "소비합니다. 주변에 다양한 물 생물과 수생 식물이 많을수록 아이템 수와 "
            "보물을 얻을 확률이 높아집니다. 사이렌이 즐겁게 지낼 수 있도록 제단 주변에 "
            "수족관이나 연못을 꾸며 주세요. [참고: 점수 갱신에는 시간이 걸립니다.]"
        ),
        "ars_elemental.page2.siren_charm": (
            "사이렌 제단은 시간이 지나면 낚시 전리품을 만들며, 주기마다 마나를 "
            "소비합니다. 주변에 다양한 물 생물과 수생 식물이 많을수록 아이템 수와 "
            "보물을 얻을 확률이 높아집니다. 사이렌이 즐겁게 지낼 수 있도록 제단 주변에 "
            "수족관이나 연못을 꾸며 주세요. [참고: 점수 갱신에는 시간이 걸립니다.]"
        ),
        "ars_elemental.page.water_upstream": (
            "이 블록은 상승 수류를 만들어, 주변 물속 개체가 물 원천 블록 안에 있지 "
            "않아도 거품 기둥처럼 위로 떠오르게 합니다. 웅크리면 아래로 내려갈 수 "
            "있습니다."
        ),
        "ars_elemental.page1.advanced_prism": (
            "특정 블록을 향하도록 조절할 수 있는 주문 프리즘 업그레이드입니다. "
            "방향을 바꾼 투사체를 변형하는 렌즈를 장착할 수 있지만 피스톤으로 밀 수는 "
            "없습니다. 도미니언 완드로 목표 블록을 지정하고, Shift+우클릭으로 렌즈를 "
            "제거합니다. 일부 렌즈는 주문을 확장하기 위해 투사체의 방향을 바꿀 때마다 "
            "마나가 필요하며, 한도는 설정에서 바꿀 수 있습니다."
        ),
        "ars_elemental.page2.advanced_prism": (
            "고급 프리즘에 프리즘 렌즈를 장착하면 투사체의 방향 전환 방식을 바꿀 수 "
            "있습니다. 곡사 및 유도 렌즈는 투사체를 해당 유형으로 바꾸고, 가속 및 감속 "
            "렌즈는 속도를 조절합니다."
        ),
        "ars_elemental.page1.flashing_archwood": (
            "이 황금빛 아크우드는 하늘과 친화력이 있습니다. 다른 아크우드처럼 여러 "
            "곳과 전용 생물 군계에서 발견되며, 의식용 석판 재료나 은은한 광원으로 "
            "쓸 수 있습니다. 해당 윌드 워커는 적을 공중으로 띄우고 바람 칼날로 "
            "공격합니다."
        ),
        "ars_elemental.page1.necrotic_focus": (
            "소환한 늑대, 언데드, 벡스는 처음에는 달라 보이지 않습니다. 하지만 "
            "소환자가 이 포커스를 착용한 상태에서 죽으면 피에 굶주린 채 한 번 "
            "부활합니다. 이 언데드 소환수들은 시전자가 유도 주문을 시전할 때 함께 "
            "시전하고, 적을 처치할 때마다 시전자를 회복시킵니다."
        ),
        "ars_elemental.page2.fire_focus": (
            "이 포커스는 점화를 강화해 마법 화상을 부여합니다. 마법 화상은 화염 "
            "저항이 있는 몹에게도 섬광이 피해를 주고 번지게 하며, 마법 피해가 방어력 "
            "일부를 관통하게 하지만 대지 피해는 약해집니다. 군마 소환은 탈 수 있는 "
            "스트라이더를 소환합니다. 점화와 증발을 조합하면 얼음을 승화시킵니다."
        ),
        "ars_elemental.page2.water_focus": (
            "이 포커스는 빙결을 강화해 대상의 동결 수치를 쌓고, 끝내 잠시 얼어붙게 "
            "하여 회복을 막습니다. 물 생성 뒤에 사용하면 생성한 물이 얼음으로 "
            "바뀝니다. 군마 소환은 탈 수 있는 돌고래를 소환하며, 물 밖으로 뛰어오르는 "
            "때를 맞추면 속도가 붙습니다. 물 생물에게 주는 모든 익사 피해는 마법 "
            "피해로 바뀝니다."
        ),
        "ars_elemental.ritual_desc.ritual_attraction": (
            "화로가 반경 8블록 안의 개체를 끌어당기는 자석처럼 작동합니다. 플레이어와 "
            "보스에게는 작동하지 않습니다. 대지 정수로 강화하면 범위가 늘어납니다."
        ),
        "ars_elemental.ritual_desc.ritual_squirrels": (
            "주변 별다람쥐에게 긴 신속 효과를 부여합니다. 반경 15블록 안에서 30초마다 "
            "효과를 갱신하며, 금 블록으로 강화하면 반경이 30블록으로 늘어납니다."
        ),
        "ars_elemental.ritual_desc.ritual_tesla_coil": (
            "의식 범위에 접근한 개체에게 번개를 내리칩니다. 공기 정수로 강화하면 "
            "플레이어도 대상으로 삼습니다. [화로를 중심으로 11x7x11블록]"
        ),
        "ars_nouveau.augment_desc.glyph_mist_glyph_extend_time": (
            "안개 구름의 지속 시간을 늘립니다."
        ),
        "effect.ars_elemental.hellfire": "마법 화상",
        "effect.ars_elemental.hellfire.description": (
            "마법 불꽃은 네더 생물까지 태워 화염에 취약하게 만듭니다. 받는 대지 "
            "피해는 조금 줄지만, 마법 피해가 방어력 일부를 관통합니다."
        ),
        "entity.ars_elemental.lerp": "보간된 마나 효과",
        "item.ars_elemental.rainbow_prism_lens": "무지개 프리즘 렌즈 [제거됨]",
    },
    "not_enough_glyphs": {
        "not_enough_glyphs.perk_desc.thread_air_focus": (
            "주문 결속기의 표지 인장입니다. 공기 포커스를 장착한 것처럼 문양 조합을 "
            "활성화합니다."
        ),
        "not_enough_glyphs.perk_desc.thread_cheap_damage": (
            "주문 결속기의 표지 인장입니다. 장착한 책으로 시전하는 주문의 마나 비용을 "
            "크게 줄이지만 피해량도 크게 줄입니다."
        ),
        "not_enough_glyphs.perk_desc.thread_fire_focus": (
            "주문 결속기의 표지 인장입니다. 화염 포커스를 장착한 것처럼 문양 조합을 "
            "활성화합니다."
        ),
        "not_enough_glyphs.perk_desc.thread_knockback": (
            "주문 결속기의 표지 인장입니다. 주문 결속기를 근접 무기로 사용할 때 "
            "밀쳐내기를 늘립니다."
        ),
        "not_enough_glyphs.perk_desc.thread_scritchance": (
            "주문 결속기의 표지 인장입니다. 주문의 치명타 확률을 높입니다."
        ),
        "not_enough_glyphs.perk_desc.thread_scritdamage": (
            "주문 결속기의 표지 인장입니다. 주문의 치명타 피해를 높입니다."
        ),
        "not_enough_glyphs.perk_desc.thread_shaper_focus": (
            "주문 결속기의 표지 인장입니다. 블록 조형 포커스를 장착한 것처럼 문양 "
            "조합을 활성화합니다."
        ),
        "not_enough_glyphs.perk_desc.thread_sharp_paper": (
            "주문 결속기의 표지 인장입니다. 주문 결속기를 무기로 사용할 때 근접 "
            "피해를 높입니다."
        ),
        "not_enough_glyphs.perk_desc.thread_slow_power": (
            "주문 결속기의 표지 인장입니다. 장착한 책으로 시전하는 주문의 피해량을 "
            "높이지만 속도를 크게 줄입니다."
        ),
        "not_enough_glyphs.perk_desc.thread_summon_focus": (
            "주문 결속기의 표지 인장입니다. 소환 포커스를 장착한 것처럼 문양 조합을 "
            "활성화합니다."
        ),
        "not_enough_glyphs.perk_desc.thread_water_focus": (
            "주문 결속기의 표지 인장입니다. 물 포커스를 장착한 것처럼 문양 조합을 "
            "활성화합니다."
        ),
        "not_enough_glyphs.perk_desc.thread_wild_magic": (
            "주문 결속기의 표지 인장입니다. 장착하면 주문 효과에 이로운 보강을 "
            "무작위로 추가합니다."
        ),
    },
    "allthearcanistgear": {
        "chat.allthearcanistgear.low_tier": "이 블록을 부수려면 더 강력한 마도서가 필요합니다.",
        "item.allthearcanistgear.allthemodium_spell_book": "Allthemodium 마도서",
        "item.allthearcanistgear.creative_spell_book": "크리에이티브 마도서",
        "item.allthearcanistgear.unobtainium_spell_book": "Unobtainium 마도서",
        "item.allthearcanistgear.vibranium_spell_book": "Vibranium 마도서",
        "tab.allthearcanistgear": "All the Arcanist Gear",
    },
}

FILTER_TYPES = {
    "aerial": "공중 생물",
    "aquatic": "물 생물",
    "fiery": "화염 면역 또는 화염 생물",
    "insect": "절지동물",
    "summon": "소환된 생물",
    "undead": "언데드",
}
for filter_name, target_name in FILTER_TYPES.items():
    QUALITY_OVERRIDES["ars_elemental"].update(
        {
            f"ars_elemental.glyph_name.glyph_{filter_name}_filter": (
                f"필터: {target_name}"
            ),
            f"ars_elemental.glyph_name.glyph_not_{filter_name}_filter": (
                f"필터: {target_name} 제외"
            ),
            f"ars_elemental.glyph_desc.glyph_{filter_name}_filter": (
                f"대상이 {target_name}이면 주문의 나머지 부분을 처리하지 않습니다."
            ),
            f"ars_elemental.glyph_desc.glyph_not_{filter_name}_filter": (
                f"대상이 {target_name}이(가) 아니면 주문의 나머지 부분을 처리하지 않습니다."
            ),
        }
    )

for namespace, overrides in QUALITY_OVERRIDES.items():
    KEY_OVERRIDES.setdefault(namespace, {}).update(overrides)

QUEST_OVERRIDES = {
    "ars_nouveau": {
        "quest.17D7D34F519F7E5F.quest_desc": (
            "최종 등급 주문서를 만들려면 &6와일든 키메라&r를 처치해야 합니다. "
            "\n\n&9의식용 화로&r를 사용해 이 의식을 완료하세요."
        ),
        "quest.3D862A3D3F83CA26.quest_desc": [
            "&9마법 부여 장치&r는 모드의 여러 아이템을 제작하며 작동하려면 마나가 "
            "필요합니다.\n\n비전 받침대를 이용하는 멀티블록 구조이기도 합니다.\n\n"
            "먼저 땅에 비전 코어를 놓고 그 위에 마법 부여 장치를 설치하세요. 장치 "
            "주변에는 비전 받침대를 배치하세요.\n",
            "{image:atm:textures/questpics/ars/enchanting_app.png width:200 "
            "height:175 align:1}",
        ],
        "quest.51162B9185A45BB1.quest_desc": (
            "이 활은 필기 작업대에서 주문을 새길 수 있습니다. \n\n마나를 소비하면 "
            "화살이 주문 화살로 바뀌어 대상에게 새긴 주문을 적용합니다. \n\n화살이 "
            "없으면 피해량 0의 주문 화살을 발사하고, 마나가 부족하면 일반 화살을 "
            "발사합니다. \n\n&9마법부여사의 활&r에는 새긴 주문을 강화하는 특수 보강 "
            "화살도 사용할 수 있습니다."
        ),
        "quest.5766C8B9E850C186.quest_desc": [
            "Ars의 주요 제작 재료인 &9마나 보석&r을 만들려면 &6주입 챔버&r가 "
            "필요합니다. \n\n주입 챔버는 아이템을 주입할 때 마나를 소비합니다. 스스로 "
            "소량의 마나를 만들지만 마나 단지를 동력원으로 사용할 수도 있습니다. "
            "\n\n일부 조합은 주변에 비전 받침대도 필요합니다.\n",
            "{image:atm:textures/questpics/ars/imbuement.png width:200 height:150 "
            "align:1}",
        ],
        "quest.6F3602F5600A6221.quest_desc": (
            "3티어 문양을 만들려면 경험치 10레벨이 필요합니다. \n\n"
            "&6대마법사의 주문서&r도 필요합니다."
        ),
        "quest.0D330FAD6C993DBC.quest_desc": (
            "주문서의 다음 업그레이드입니다! \n\n전체 마나와 마나 재생량이 "
            "늘어나며 2티어 문양을 만들고 사용할 수 있습니다."
        ),
        "quest.227DBA8836021B0B.quest_desc": (
            "Ars Nouveau의 기계 동력은 &9마나&r라고 합니다. \n\n마나를 모으려면 "
            "마나 단지가 필요합니다. \n\n마나는 양동이로 옮기거나 마나 단지를 부숴 "
            "통째로 옮길 수도 있습니다."
        ),
        "quest.227DBA8836021B0B.quest_subtitle": "마나 저장",
        "quest.64D0E66CB4FBEC82.quest_desc": (
            "시작하려면 &6초보자의 주문서&r를 제작하세요! \n\n이곳에서 주문을 만들고 "
            "저장합니다. \n\n&9C&r 키를 누르면 '주문 만들기' 페이지가 열립니다. "
            "왼쪽에는 여러 탭이 있으며 주요 3개 탭은 주문 제작, 색상 선택기, "
            "사역마입니다. \n\n이 주문서는 1티어 문양만 만들고 사용할 수 있습니다. 더 "
            "강력한 주문을 만들려면 주문서를 업그레이드하세요!"
        ),
        "quest.6B511C8B572E8940.quest_subtitle": "마법사의 힘",
        "quest.6DAA82B5F94AF9F8.title": "마법 단지",
        "task.0E6876A34D1975EB.title": "AllRightsReserved",
        "task.388545A0E3B4930D.title": "AllRightsReserved",
    },
    "related": {
        "quest.3D78D9F4E8A60EDB.quest_desc": (
            "현재 조합은 비교적 간단해서 &d마나 단지&r 4개, &d마나 보석 블록&r "
            "4개와 &6&lATM의 별&r만 필요합니다. 걱정 마세요, 나중에는 더 어렵게 "
            "바뀔 거예요! \n\n이 단지는 언제나 &d마나&r로 가득 차 있으며, 마나가 "
            "&d마나&r가 필요한 모든 장치에 연결할 수 있습니다. &6&lATM의 별&r "
            "멀티블록도 "
            "포함됩니다."
        ),
        "quest.00F2C4A528873A6B.quest_desc": (
            "&l&b룬 도가니&r는 작동할 때 &d마나&r가 필요하지만, 이를 지원하는 "
            "&d마나 입력부&r는 없습니다. 대신 그 &d마나&r를 &d마나 응축기&r로 "
            "액체화할 수 있습니다. 일부 &d마나&r가 든 &d마나 단지&r를 "
            "&d마나 응축기&r 옆에 "
            "놓으면 &d액화 마나&r로 변환합니다. 이제 &9유체 입력부&r에서 다룰 수 "
            "있습니다."
        ),
        "quest.00F2C4A528873A6B.title": "&l&d마나 응축",
        "quest.06B9D8973E9C6A2C.quest_desc": (
            "Occultism 챕터에 Ars Nouveau 아이템이 있어 의아할 수 있습니다. 두 "
            "모드를 이어 주는 Ars Ocultas가 있기 때문입니다. 폴리오트 분쇄기 같은 "
            "영혼은 이 단지 안에서 작업할 수 있습니다. 영혼이 처리할 아이템을 "
            "파이프로 넣으면 인접한 보관함으로 결과를 내보냅니다. 단지 아래쪽이 "
            "가장 안정적인 출력 면이며, 보관함으로 내보낼 수 없으면 월드에 "
            "아이템을 떨어뜨립니다."
        ),
        "quest.06B9D8973E9C6A2C.quest_subtitle": ("영혼이 격리 단지 안에서 작업합니다"),
        "quest.06B9D8973E9C6A2C.title": "Ars Ocultas: 영혼 단지",
        "quest.4ABACE222E647E2C.quest_desc": (
            "희생 제단은 Ars Ocultas가 제공하는 또 다른 도구로, 희생 의식을 "
            "자동화합니다.\n\n중앙 그릇 아래에 제단을 놓으세요. 희생물이 든 격리 "
            "단지와 마나 단지가 근처에 있으면 희생물 대신 마나를 사용할 수 "
            "있습니다."
        ),
        "quest.4ABACE222E647E2C.quest_subtitle": "마나로 희생물 대체",
        "quest.6D68D9941049E806.quest_desc": (
            "이름처럼 이 생성기는 &d마나&r를 연료로 사용합니다. 소환할 몹이 든 "
            "격리 단지를 주변에 놓아 대상을 정하세요."
        ),
        "quest.29D28983E0200A3C.quest_desc": (
            "&l&dArs Nouveau&r는 주문서에 문양을 조합해 원하는 주문을 시전하는 "
            "마법 모드입니다!"
        ),
        "quest.29D28983E0200A3C.title": "&d&lArs Nouveau",
    },
}

QUEST_QUALITY_OVERRIDES = {
    "ars_nouveau": {
        "quest.04D9F6587EF8D9B7.quest_desc": [
            "&9물약 단지&r는 물약을 최대 100회분 저장합니다. 빈 병이나 물약 플라스크를 "
            "단지에 사용하면 물약을 꺼낼 수 있습니다.\n\n윅시는 물약 자동 제조에 이 "
            "단지를 사용합니다."
        ],
        "quest.0A1ABE9CF7740AAA.title": "마나 비용 감소의 반지",
        "quest.0E2AD156E5EF263A.quest_desc": [
            "필기 작업대에서 주문을 새길 때 사용합니다."
        ],
        "quest.0D330FAD6C993DBC.quest_desc": (
            "마도서의 다음 업그레이드입니다! \n\n최대 마나와 마나 재생량이 늘어나고, "
            "2티어 문양을 제작하고 사용할 수 있습니다."
        ),
        "quest.151648179684B088.quest_desc": (
            "룬 분필은 땅에 영구적인 룬을 그릴 때 사용합니다. 이 룬은 위를 지나가는 "
            "개체에게 주문을 시전합니다.\n\n룬에 주문을 연결하려면 필기 작업대에서 "
            "&e주문 양피지&r에 주문을 새기세요.\n\n참고: 룬이 작동하려면 마나가 "
            "필요합니다."
        ),
        "quest.151648179684B088.quest_subtitle": "설치 가능한 주문",
        "quest.111649D7E16D869F.quest_desc": [
            "&9시전자의 완드&r에는 주문 하나만 새길 수 있으며 필기 작업대를 "
            "사용합니다.\n\n완드의 주문은 항상 투사체 > 가속으로 시작하므로, 닿기나 "
            "자신 같은 다른 형태 문양이 없는 주문을 새겨야 합니다.\n\n이 방식으로 "
            "문양 10개 제한을 넘는 주문을 시전할 수 있습니다. 파괴를 사용하려면 "
            "완드에 파괴만 새기세요."
        ],
        "quest.14DB8A515CA50932.quest_desc": [
            "&9마법 부여자의 검&r에는 닿기 주문을 새길 수 있습니다.\n\n검에 새긴 "
            "모든 주문은 마지막 효과에 증폭 보강 1회가 추가됩니다.\n\n필기 "
            "작업대에서 검에 주문을 새기되, 형태 문양 없이 주문을 만드세요."
        ],
        "quest.17D7D34F519F7E5F.quest_desc": (
            "최종 티어 마도서를 만들려면 &6와일든 키메라&r를 처치해야 합니다. "
            "\n\n&9의식용 화로&r에서 의식을 수행하세요."
        ),
        "quest.1D86B2E553503E53.title": "소환수 다루기",
        "quest.295C77EEC89000FC.quest_subtitle": ("몹 처치와 동물 번식으로 마나 생성"),
        "quest.2D0CF18C8B2ABB7D.quest_desc": (
            "자라는 식물이나 묘목 근처에 놓으면 마나를 생성합니다. 아크우드는 더 많은 "
            "마나를 생성합니다!\n\n참고: 뼛가루로 성장시키면 마나가 생성되지 않습니다."
        ),
        "quest.2D0CF18C8B2ABB7D.quest_subtitle": "식물 성장으로 마나 생성",
        "quest.3D4D88B8BE881351.quest_desc": (
            "더 강력한 주문을 쓰려면 &6필기 작업대&r에서 마도서의 새 문양을 해금해야 "
            "합니다.\n\n문양은 3개 티어로 나뉘며, 제작할 때 경험치와 아이템이 "
            "필요합니다.\n\n필기 작업대에서는 주문 양피지에 주문도 새길 수 있습니다. "
            "양피지를 작업대에 놓고 마도서에서 주문을 선택한 뒤, 웅크린 채 작업대에 "
            "마도서를 우클릭하세요.\n\n문양을 제작하려면 마도서를 들고 작업대를 "
            "우클릭한 다음 원하는 문양을 찾아 아래의 '선택'을 누르세요. 필요한 "
            "아이템을 작업대에 넣으면 문양이 만들어지며, 완성된 문양을 사용하면 "
            "배울 수 있습니다.\n\n참고: 작업대는 주변 보관함에서 아이템을 가져올 수 "
            "있습니다."
        ),
        "quest.3D4D88B8BE881351.quest_subtitle": "주문 업그레이드",
        "quest.36CDA39C23D3AA2B.quest_desc": [
            "이 퀘스트는 &6AllTheMods Staff&r 또는 &2커뮤니티 기여자&r가 "
            "AllTheMods 모드팩용으로 작성했습니다.\n\n모든 &6AllTheMods&r 팩은 "
            "&eAll Rights Reserved&r 라이선스를 따르므로, &6AllTheMods Team&r의 "
            "명시적 허가 없이 다른 공개 모드팩에 이 퀘스트를 사용할 수 없습니다."
            "\n\n이 퀘스트는 의도적으로 숨겨져 있습니다. 이 내용이 보인다면 편집 "
            "모드입니다."
        ],
        "quest.3D862A3D3F83CA26.quest_desc": [
            "&9마법 부여 장치&r는 모드의 여러 아이템을 제작하며, 작동하려면 마나가 "
            "필요합니다.\n\n아케인 받침대를 사용하는 멀티블록 구조입니다.\n\n먼저 "
            "땅에 아케인 코어를 놓고 그 위에 마법 부여 장치를 설치하세요. 장치 "
            "주변에는 아케인 받침대를 배치하세요.\n",
            "{image:atm:textures/questpics/ars/enchanting_app.png width:200 "
            "height:175 align:1}",
        ],
        "quest.3182E8AF755104E4.quest_desc": [
            "피해를 막으면 &9마법사의 방패&r가 잠시 마나 재생과 주문 피해 증가 "
            "효과를 부여합니다.\n\n또한 방패는 착용자의 마나를 사용해 서서히 스스로 "
            "수리됩니다."
        ],
        "quest.41A0BE357C8A74E1.quest_desc": (
            "&9연금술 마나링크&r는 인접한 물약 단지의 물약을 소비해 마나를 "
            "생성합니다.\n\n생성량은 물약의 종류와 복잡도에 따라 달라집니다."
        ),
        "quest.41A0BE357C8A74E1.quest_subtitle": "물약으로 마나 생성",
        "quest.51162B9185A45BB1.quest_desc": (
            "이 활에는 필기 작업대에서 주문을 새길 수 있습니다. \n\n마나를 소비하면 "
            "화살이 주문 화살로 바뀌어 대상에게 새긴 주문을 적용합니다. \n\n화살이 "
            "없으면 피해량이 0인 주문 화살을 발사하고, 마나가 부족하면 일반 화살을 "
            "발사합니다. \n\n&9마법 부여자의 활&r에는 새긴 주문을 강화하는 특수 보강 "
            "화살도 사용할 수 있습니다."
        ),
        "quest.632BC46928CC9A8C.quest_desc": [
            "&9마법 부여자의 거울&r을 사용하면 자신에게 주문을 시전합니다.\n\n이 "
            "거울로 시전한 주문은 마나 비용이 줄고 지속 시간 보너스를 얻습니다.\n\n"
            "주문을 새기려면 필기 작업대를 사용하세요. 형태 문양 없이 주문을 "
            "만들어야 합니다."
        ],
        "quest.542C6D76B579886C.quest_desc": (
            "마법 부여 장치로 첫 번째 &5마법꽃 씨앗&r을 제작하세요. \n\n이 씨앗에서 "
            "얻은 재료로 마법 방어구를 만들 수 있습니다!"
        ),
        "quest.5766C8B9E850C186.quest_desc": [
            "Ars의 주요 제작 재료인 &9마나 보석&r을 만들려면 &6주입 챔버&r가 "
            "필요합니다. \n\n주입 챔버는 아이템을 주입할 때 마나를 소비합니다. 자체적으로 "
            "소량의 마나를 만들지만 마나 단지를 동력원으로 사용할 수도 있습니다. "
            "\n\n일부 조합에는 주변의 아케인 받침대도 필요합니다.\n",
            "{image:atm:textures/questpics/ars/imbuement.png width:200 height:150 "
            "align:1}",
        ],
        "quest.58EC47584C773B82.quest_desc": (
            "마법 부여 장치로 첫 번째 &5마법꽃 씨앗&r을 제작하세요. \n\n이 씨앗에서 "
            "얻은 재료로 마법 방어구를 만들 수 있습니다!"
        ),
        "quest.5C3FF43CF16BCF30.quest_desc": (
            "마나 보석으로 &5마나석&r을 만들면 여러 마법 장치를 제작할 수 있습니다."
        ),
        "quest.5C3FF43CF16BCF30.quest_subtitle": '이전 명칭: "아케인 스톤"',
        "quest.5C3FF43CF16BCF30.title": "마나석",
        "quest.5CFBA24B3E0CDEDD.quest_desc": [
            "마도서를 들고 C 키를 누르면 주문 제작 화면이 열립니다.\n\n모든 주문에는 "
            "형태가 하나 필요합니다. 처음에는 투사체, 자신, 닿기의 3가지 형태를 사용할 수 "
            "있습니다.\n\n효과는 주문이 실제로 무엇을 할지 결정하며, 주문 하나에 최대 "
            "9개까지 넣을 수 있습니다.\n\n처음에는 피해와 파괴를 사용할 수 있습니다."
            "\n\n형태 하나와 효과 하나를 선택하고 주문 이름을 지은 뒤 '생성'을 누르세요!",
            "",
            "{image:atm:textures/questpics/ars/spellbook.png width:200 height:150 align:1}",
        ],
        "quest.63DD7F5A4441ACE7.quest_desc": (
            "2티어 문양을 만들려면 경험치 5레벨이 필요합니다.\n\n또한 "
            "&9마법사의 마도서&r가 필요합니다."
        ),
        "quest.64D0E66CB4FBEC82.quest_desc": (
            "시작하려면 &6초보자의 마도서&r를 제작하세요! \n\n마도서에서는 주문을 "
            "만들고 저장할 수 있습니다. \n\n&9C&r 키를 누르면 '주문 만들기' 화면이 "
            "열립니다. 왼쪽의 주요 3개 탭은 주문 제작, 색상 선택기, 사역마입니다. "
            "\n\n초보자의 마도서로는 1티어 문양만 만들고 사용할 수 있습니다. 더 "
            "강력한 주문을 만들려면 마도서를 업그레이드하세요!"
        ),
        "quest.64D0E66CB4FBEC82.quest_subtitle": "첫 번째 마도서",
        "quest.64D0E66CB4FBEC82.title": "마도서",
        "quest.6E0E13806F388D7E.quest_desc": [
            "&aArs Nouveau&f에 오신 것을 환영합니다!\n\nArs Nouveau는 여러 "
            "문양을 조합해 원하는 주문을 직접 만들 수 있는 마법 모드입니다!"
        ],
        "quest.6A1C0B17B22CE50F.title": "마나 부적",
        "quest.6B511C8B572E8940.quest_desc": (
            "화면 왼쪽 아래의 막대는 현재 마나를 보여 줍니다!\n\n모드를 진행하면 최대 "
            "마나를 늘리거나 주문 효율을 높이는 여러 수단을 얻습니다. 마도서를 "
            "업그레이드해도 최대 마나가 늘어납니다!"
        ),
        "quest.6B511C8B572E8940.quest_subtitle": "마법사의 마나",
        "quest.6F3602F5600A6221.quest_desc": (
            "3티어 문양을 만들려면 경험치 10레벨이 필요합니다. \n\n"
            "&6대마법사의 마도서&r도 필요합니다."
        ),
        "quest.77145113CD5B26FB.quest_desc": (
            "마나 열매는 다른 음식보다 더 많은 마나를 생성합니다.\n\n주변 3x3 "
            "범위의 잔디나 흙을 균사체로 바꾸고, 빈 공간에는 버섯도 자라게 합니다."
        ),
        "quest.77145113CD5B26FB.quest_subtitle": "주변 음식으로 마나 생성",
        "quest.6DAA82B5F94AF9F8.quest_desc": [
            "&9빛의 단지&r는 사용자를 따라다니는 광원을 소환합니다.\n\n&6공허의 "
            "단지&r는 주운 아이템을 파괴하고 마나로 바꾸며, 파괴할 아이템을 필터로 "
            "지정할 수 있습니다.\n\n보조 손에 아이템을 들고 단지를 사용하거나, "
            "단지를 올린 필기 작업대에 아이템을 사용해 필터에 추가하거나 "
            "제거하세요.\n\n작동하려면 단지가 단축바에 있어야 합니다."
        ],
        "task.03EB390E79866058.title": "마나석",
    },
    "related": {
        "quest.3D78D9F4E8A60EDB.quest_desc": (
            "현재 조합은 비교적 간단해서 &d마나 단지&r 4개, &d마나 보석 블록&r "
            "4개와 &6&lATM의 별&r만 필요합니다. 걱정 마세요, 나중에는 더 어려워질 "
            "거예요! \n\n이 단지는 언제나 &d마나&r로 가득 차 있으며, &d마나&r가 필요한 "
            "모든 장치에 연결할 수 있습니다. &6&lATM의 별&r 멀티블록도 포함됩니다."
        ),
        "quest.66E88F916B638B3B.quest_desc": (
            "조금 헷갈릴 수 있습니다. &5크리에이티브 &e마도서&r가 여러 개 있거든요! "
            "여기서 필요한 것은 &d&lAll the Arcanist Gear&r의 마도서입니다. \n\n이 "
            "마도서를 만들려면 먼저 &l&dArs Nouveau&r의 크리에이티브 &e마도서&r를 "
            "제작해야 합니다. 그 조합에는 &e대마법사의 마도서&r, &6&lATM의 별&r, "
            "몇 가지 추가 아이템이 필요합니다. \n\n&eUnobtainium 마도서&r와 성능은 "
            "같지만 마나가 무한하고 모든 문양이 해금되어 있습니다! \n\n모든 주문 "
            "위력을 손에 넣는 겁니다. 으하하하!"
        ),
        "quest.66E88F916B638B3B.title": "&5&l크리에이티브 &e마도서",
        "quest.762581CAE5F5DDC1.quest_desc": [
            "멋진 마법 모드네요! &d&lArs Nouveau&r의 마법 부여 장치로 "
            "&5Unobtainium&r과 &6Allthemodium&r을 결합합니다! \n\n마법 부여 장치는 "
            "여러 조합에 쓰이는 멀티블록입니다. 아케인 코어 위에 마법 부여 장치를 "
            "놓고, 같은 Y 높이의 주변에 받침대를 배치하세요. \n\n받침대에 재료를 "
            "순서와 관계없이 올리고 주변에 마나를 준비한 뒤 장치에 마나 보석을 넣으면 "
            "제작이 시작됩니다. 그러면 &5Unobtainium&r-&6Allthemodium&r 합금 주괴가 "
            "완성됩니다!\n",
            '{ "text": "Ars Nouveau 퀘스트", "color": "#55FF55", '
            '"underlined": true, "clickEvent": { "action": "change_page", '
            '"value": "6AEDA2F9BEB57759" } }',
        ],
        "quest.0ABB2264CBB82470.quest_desc": "&d&lArs&r 철 등급 방어구입니다.",
        "quest.0ABB2264CBB82470.title": "&5아케니스트 복장",
        "quest.0E2515424291BB59.quest_desc": (
            "&b다이아몬드&r 등급의 &d&lArs&r 방어구입니다!"
        ),
        "quest.19F58E291A543228.quest_desc": "&e금&r 등급의 &d&lArs&r 방어구입니다!",
        "quest.2296CE4418AE62D4.title": "&6Allthemodium 아케니스트 장비",
        "quest.29D28983E0200A3C.quest_desc": (
            "&l&dArs Nouveau&r는 마도서에 문양을 조합해 원하는 주문을 시전하는 마법 "
            "모드입니다!"
        ),
        "quest.3512F47DADC07EAE.title": "&5Unobtainium 아케니스트 장비",
        "quest.52AFABA08674B6A8.title": "&3Vibranium 아케니스트 장비",
    },
}
for scope, overrides in QUEST_QUALITY_OVERRIDES.items():
    QUEST_OVERRIDES.setdefault(scope, {}).update(overrides)

GUIDE_EXTRA_ENGLISH = {
    "ars_nouveau.page.apparatus_crafting": "Apparatus Crafting",
    "ars_nouveau.page.archwood_forest": "Archwood Forest",
    "ars_nouveau.page.better_casting": "Better Casting",
    "ars_nouveau.page.new_glyphs": "New Glyphs",
    "ars_nouveau.page.starting_automation": "Starting Automation",
    "ars_nouveau.page.trinkets": "Trinkets",
    "ars_nouveau.page.upgrades": "Upgrades",
    "ars_nouveau.page.world_generation": "World Generation",
    "ars_nouveau.page1.apparatus_crafting": (
        "The Enchanting Apparatus is used for crafting special machines, curios, "
        "and equipment used to progress in Ars Nouveau. Crafting with the "
        "Enchanting Apparatus requires up to eight Arcane Pedestals, an Arcane "
        "Core, and the Enchanting Apparatus block. Once you have setup your "
        "apparatus, you should craft your first Magebloom Seed."
    ),
    "ars_nouveau.page1.archwood_forest": (
        "The Archwood Forest is a somewhat rare biome filled with magical lights "
        "and archwood trees. It contains an increased amount of gold. Additionally, "
        "magical creatures such as Starbuncles, Whirlisprigs, Archwood Treants, and "
        "Drygmys have a much higher chance of spawning. Terrablender is required to "
        "be installed to generate this biome."
    ),
    "ars_nouveau.page1.better_casting": (
        "Your mana pool may be expanded with special mage armors, enchantments, "
        "learning new glyphs, or by drinking potions. Once you have acquired a "
        "Magebloom Seed, you may craft Novice Robes which will expand your casting "
        "abilities significantly. These robes will self-repair using your mana "
        "pool, have a high enchantability, and provide decent armor."
    ),
    "ars_nouveau.page1.new_glyphs": (
        "Accessing new spells will require a small amount of setup, resources, and "
        "base building. New spells can be learned by obtaining Glyphs. Glyphs are "
        "created using the Scribe's Table with Experience and items. Once you have "
        "obtained a glyph, simply use it to memorize the glyph. See the section on "
        "the Scribes Table for more information."
    ),
    "ars_nouveau.page1.starting_automation": (
        "Spells may be used in Automation using Spell Turrets. Use these to create "
        "auto harvesters, tree farms, quarries, cake farms, glass factories, and "
        "more! For item transport, autocrafting, or resource generation, see the "
        "variety of magical entities that may be summoned using Charms."
    ),
    "ars_nouveau.page1.trinkets": (
        "Items and curios can expand your casting and can provide unique buffs. For "
        "more casting, you may want to craft a Ring of Discount or an Amulet of "
        "Mana Regen. For travel, see the Belt of Levitation, or improve your mining "
        "efficiency with the Jar of Voiding."
    ),
    "ars_nouveau.page1.upgrades": (
        "Tier 2 and 3 glyphs will require an Apprentice and Archmage spell book "
        "respectively. Higher tier books will allow you to cast higher tier spells, "
        "use them in automation, and provide additional mana and mana regeneration "
        "as a bonus. Once you are able to upgrade your book, upgrading your armor to "
        "the next tier of robes will also grant you another boost in casting."
    ),
    "ars_nouveau.page1.world_generation": (
        "Several resources can spawn in the world, each with their own magical "
        "properties. Archwood trees come in several decorative variants and may be "
        "used to craft Casting Wands. Source Berries, found in Taigas, are essential "
        "for crafting Mana Regeneration potions."
    ),
    "ars_nouveau.page2.spell_casting": (
        "Next, add any number of $(bold)Effects$() to the chain. Effects refer to "
        "$(italic)what$() the spell will do and they will resolve in the order they "
        "are placed in the book at the target or location the spell hits. An "
        "$(bold)Augment$() can be used to modify the way an Effect or Form behaves. "
        "$(bold)Augments$() may be placed after an Effect or Form. An Augment will "
        "only apply to the glyph to the $(bold)left$() of it. Multiple augments may "
        "also be applied on the same Effect or Form by chaining Augments together."
    ),
    "ars_nouveau.page2.spell_mana": (
        "Adding glyphs to your spell book will also increase your maximum amount of "
        "mana and mana regeneration. This bonus also scales with the tier of your "
        "spell book."
    ),
    "ars_nouveau.page3.spell_casting": (
        "If you would like to set a spell to a different tab, select the tab from "
        "the right side and repeat the above process. Several keybindings are "
        "provided for using the spellbook. $(br)Open Spellbook: "
        "$(k:ars_nouveau.open_book) $(br)Quick Select: "
        "$(k:ars_nouveau.selection_hud) $(br)Next Spell: "
        "$(k:ars_nouveau.next_slot) $(br)Previous Spell: "
        "$(k:ars_nouveau.previous_slot)"
    ),
    "ars_nouveau.page3.volcanic_sourcelink": (
        "The Volcanic Sourcelink will occasionally convert Stone into Magma Blocks, "
        "and Magma Blocks into Lava, given that these blocks exist beneath it in "
        "its 3x3 area. This conversion is dependent on the amount of $(item)heat$() "
        "it has produced over time. The Volcanic Sourcelink will also spawn a Lava "
        "Lily adjacent to it given that there is nothing covering the lava. Lava "
        "Lilys may be harvested and used for decoration."
    ),
    "ars_nouveau.page4.volcanic_sourcelink": (
        "The color of a Lava Lily changes if it is placed above lava, magma, or "
        "other blocks."
    ),
    "ars_elemancy.page.armor_set.elemancer": (
        "Elemancer armor is attuned to all four Elemental Schools and combines "
        "the effects of the lesser elemental armor sets."
    ),
    "ars_elemancy.page.cinder_bangle": (
        "This bangle is attuned to the Schools of Fire and Air, empowering spells "
        "from both schools and combining their bangle bonuses."
    ),
    "ars_elemancy.page.elemancer_bangle": (
        "This bangle is attuned to all four Elemental Schools, empowering their "
        "spells and combining all elemental bangle bonuses."
    ),
    "ars_elemancy.page.lava_bangle": (
        "This bangle is attuned to the Schools of Earth and Fire, empowering spells "
        "from both schools and combining their bangle bonuses."
    ),
    "ars_elemancy.page.mire_bangle": (
        "This bangle is attuned to the Schools of Water and Earth, empowering "
        "spells from both schools and combining their bangle bonuses."
    ),
    "ars_elemancy.page.silt_bangle": (
        "This bangle is attuned to the Schools of Earth and Air, empowering spells "
        "from both schools and combining their bangle bonuses."
    ),
    "ars_elemancy.page.tempest_bangle": (
        "This bangle is attuned to the Schools of Water and Air, empowering spells "
        "from both schools and combining their bangle bonuses."
    ),
    "ars_elemancy.page.vapor_bangle": (
        "This bangle is attuned to the Schools of Fire and Water, empowering spells "
        "from both schools and combining their bangle bonuses."
    ),
    "starbunclemania.wixie_jobs": "Extra Jobs for the Wixie",
}
GUIDE_EXTRA_KOREAN = {
    "ars_nouveau.page.apparatus_crafting": "마법 부여 장치 제작",
    "ars_nouveau.page.archwood_forest": "아크우드 숲",
    "ars_nouveau.page.better_casting": "더 강한 주문 시전",
    "ars_nouveau.page.new_glyphs": "새 문양",
    "ars_nouveau.page.starting_automation": "자동화 시작하기",
    "ars_nouveau.page.trinkets": "장신구",
    "ars_nouveau.page.upgrades": "업그레이드",
    "ars_nouveau.page.world_generation": "월드 생성",
    "ars_nouveau.page1.apparatus_crafting": (
        "마법 부여 장치는 Ars Nouveau 진행에 필요한 특수 기계, Curios 장신구와 "
        "장비를 제작합니다. 제작 구조에는 아케인 받침대 최대 8개, 아케인 코어와 마법 "
        "부여 장치가 필요합니다. 구조를 완성했다면 첫 마법꽃 씨앗을 제작하세요."
    ),
    "ars_nouveau.page1.archwood_forest": (
        "아크우드 숲은 마법의 빛과 아크우드 나무로 가득한 다소 희귀한 생물 "
        "군계입니다. 금이 더 많이 생성되며 별다람쥐, 윌스프링, 아크우드 트리앤트, "
        "드리그미 같은 마법 생물의 출현 확률도 훨씬 높습니다. 이 생물 군계를 "
        "생성하려면 TerraBlender가 설치되어 있어야 합니다."
    ),
    "ars_nouveau.page1.better_casting": (
        "특수 마법사 방어구와 마법 부여, 새 문양 학습, 물약 사용으로 최대 마나를 "
        "늘릴 수 있습니다. 마법꽃 씨앗을 얻으면 초보자의 로브를 제작해 주문 시전 "
        "능력을 크게 높일 수 있습니다. 이 로브는 마나로 스스로 수리되고 마법 "
        "부여 적성이 높으며 준수한 방어력을 제공합니다."
    ),
    "ars_nouveau.page1.new_glyphs": (
        "새 주문을 배우려면 약간의 준비와 자원, 거점 건설이 필요합니다. 새 주문은 "
        "문양을 얻어 배울 수 있습니다. 필기 작업대에 경험치와 아이템을 사용해 "
        "문양을 만들고, 완성된 문양을 사용하면 기억합니다. 자세한 내용은 필기 "
        "작업대 항목을 확인하세요."
    ),
    "ars_nouveau.page1.starting_automation": (
        "주문 포탑으로 주문을 자동화에 사용할 수 있습니다. 자동 수확기, 나무 "
        "농장, 채석장, 케이크 농장, 유리 공장 등을 만들어 보세요! 아이템 운송, "
        "자동 제작이나 자원 생산에는 부적으로 소환할 수 있는 여러 마법 생물을 "
        "활용하세요."
    ),
    "ars_nouveau.page1.trinkets": (
        "아이템과 Curios 장신구는 주문 능력을 넓히고 고유한 강화 효과를 줍니다. "
        "주문 능력을 높이려면 할인의 반지나 마나 재생의 부적을, 이동에는 공중 "
        "부양의 벨트를 사용하세요. 공허의 단지로 채굴 효율을 높일 수도 있습니다."
    ),
    "ars_nouveau.page1.upgrades": (
        "2티어와 3티어 문양에는 각각 마법사와 대마법사의 마도서가 필요합니다. 높은 "
        "등급의 마도서는 높은 등급 주문을 시전하고 자동화에 사용할 수 있게 하며, "
        "최대 마나와 마나 재생량도 늘립니다. 마도서를 업그레이드할 수 있게 되면 "
        "로브도 다음 등급으로 올려 주문 능력을 더 강화하세요."
    ),
    "ars_nouveau.page1.world_generation": (
        "월드에는 저마다 마법 속성을 지닌 여러 자원이 생성됩니다. 아크우드 나무는 "
        "여러 장식 변형이 있으며 시전자의 지팡이 제작에도 사용합니다. 타이가에서 "
        "발견되는 마나 열매는 마나 재생 물약의 핵심 재료입니다."
    ),
    "ars_nouveau.page2.spell_casting": (
        "다음으로 원하는 만큼 $(bold)효과$()를 연결하세요. 효과는 주문이 "
        "$(italic)무엇$()을 할지 정하며, 주문이 맞은 대상이나 위치에서 마도서에 "
        "배치한 순서대로 발동합니다. $(bold)보강$()은 효과나 형태의 작동 방식을 "
        "바꿉니다. $(bold)보강$()은 효과 또는 형태 뒤에 놓으며, 바로 "
        "$(bold)왼쪽$() 문양에만 적용됩니다. 여러 보강을 이어 같은 효과나 형태에 "
        "함께 적용할 수도 있습니다."
    ),
    "ars_nouveau.page2.spell_mana": (
        "마도서에 문양을 추가하면 최대 마나와 마나 재생량도 늘어납니다. 이 보너스는 "
        "마도서 등급에 따라 커집니다."
    ),
    "ars_nouveau.page3.spell_casting": (
        "주문을 다른 탭에 지정하려면 오른쪽에서 탭을 선택하고 위 과정을 반복하세요. "
        "마도서에는 여러 단축키가 있습니다. $(br)마도서 열기: "
        "$(k:ars_nouveau.open_book) $(br)빠른 선택: "
        "$(k:ars_nouveau.selection_hud) $(br)다음 주문: "
        "$(k:ars_nouveau.next_slot) $(br)이전 주문: "
        "$(k:ars_nouveau.previous_slot)"
    ),
    "ars_nouveau.page3.volcanic_sourcelink": (
        "화산성 마나링크 아래 3x3 범위에 돌이나 마그마 블록이 있으면 때때로 돌을 "
        "마그마 블록으로, 마그마 블록을 용암으로 바꿉니다. 변환 여부는 시간에 따라 "
        "생산한 $(item)열$()의 양에 달려 있습니다. 용암 위가 비어 있으면 옆에 용암 "
        "백합도 생성합니다. 용암 백합은 수확해 장식에 사용할 수 있습니다."
    ),
    "ars_nouveau.page4.volcanic_sourcelink": (
        "용암 백합은 용암, 마그마 또는 다른 블록 위에 놓였는지에 따라 색이 "
        "달라집니다."
    ),
    "ars_elemancy.page.armor_set.elemancer": (
        "원소술사 방어구는 네 원소 학파 모두에 조율되어 있으며 하위 원소 방어구 "
        "세트의 효과를 결합합니다."
    ),
    "ars_elemancy.page.cinder_bangle": (
        "화염과 공기 학파에 조율된 팔찌입니다. 두 학파의 주문을 강화하고 두 원소 "
        "팔찌의 보너스를 함께 제공합니다."
    ),
    "ars_elemancy.page.elemancer_bangle": (
        "네 원소 학파 모두에 조율된 팔찌입니다. 모든 원소 주문을 강화하고 원소 "
        "팔찌의 보너스를 모두 결합합니다."
    ),
    "ars_elemancy.page.lava_bangle": (
        "대지와 화염 학파에 조율된 팔찌입니다. 두 학파의 주문을 강화하고 두 원소 "
        "팔찌의 보너스를 함께 제공합니다."
    ),
    "ars_elemancy.page.mire_bangle": (
        "물과 대지 학파에 조율된 팔찌입니다. 두 학파의 주문을 강화하고 두 원소 "
        "팔찌의 보너스를 함께 제공합니다."
    ),
    "ars_elemancy.page.silt_bangle": (
        "대지와 공기 학파에 조율된 팔찌입니다. 두 학파의 주문을 강화하고 두 원소 "
        "팔찌의 보너스를 함께 제공합니다."
    ),
    "ars_elemancy.page.tempest_bangle": (
        "물과 공기 학파에 조율된 팔찌입니다. 두 학파의 주문을 강화하고 두 원소 "
        "팔찌의 보너스를 함께 제공합니다."
    ),
    "ars_elemancy.page.vapor_bangle": (
        "화염과 물 학파에 조율된 팔찌입니다. 두 학파의 주문을 강화하고 두 원소 "
        "팔찌의 보너스를 함께 제공합니다."
    ),
    "starbunclemania.wixie_jobs": "윅시의 추가 작업",
}
OCULTAS_GUIDE_TRANSLATIONS = {
    "Transmutation": "변환",
    "You can convert surplus amounts of silver into gold and vice-vera!": (
        "남는 은을 금으로, 금을 은으로 변환할 수 있습니다!"
    ),
    "Spirit Attuned Gem": "영혼 조율 보석",
    "Alternate recipe when diamonds are scarce.": (
        "다이아몬드가 부족할 때 사용할 수 있는 대체 조합입니다."
    ),
    "Spirit Jars": "영혼 단지",
    (
        "Occultism Spirits can work inside $(l:machines/mob_jar)Containment "
        "Jars$(/l). They maintain their original behaviour and $(thing)do not "
        "decay$() making them perfect from automations! $(br2)Spirit Jar will "
        "automatically pickup any item in 7x7 centered around it that matches "
        "spirit's filter (for crushing spirits, it will automatically pickup any "
        "ore that it can process)."
    ): (
        "Occultism 영혼은 $(l:machines/mob_jar)격리 단지$(/l) 안에서 일할 수 "
        "있습니다. 원래 행동을 유지하면서 $(thing)소멸하지 않기$() 때문에 자동화에 "
        "아주 알맞습니다! $(br2)영혼 단지는 중심으로부터 7x7 범위에서 영혼의 필터와 "
        "일치하는 아이템을 자동으로 줍습니다. 분쇄 영혼은 처리할 수 있는 광석을 "
        "자동으로 줍습니다."
    ),
    (
        "Items can also be pushed into the containment jar using a hopper or "
        "starbuncles (any pipe should also work!). Players can also right-click any "
        "item directly on the jar. $(br2)Spirits in Jars exhibit their default "
        "behaviour, this means that a $(thing)Crusher Spirit$() will automatically "
        "process and fling the output in one of directions"
    ): (
        "호퍼나 별다람쥐로 격리 단지에 아이템을 넣을 수 있으며 어떤 파이프든 "
        "작동합니다. 플레이어가 아이템을 들고 단지를 직접 우클릭해도 됩니다. "
        "$(br2)단지 속 영혼은 원래 행동을 하므로 $(thing)분쇄기 영혼$()은 아이템을 "
        "자동으로 처리하고 결과물을 한 방향으로 던집니다."
    ),
    "Janitor Spirits": "관리인 영혼",
    (
        "Janitor Spirits inside jars have a special property. They automatically "
        "try to pickup items nearby and push to inventory next to it. This makes "
        "automation super easy!"
    ): (
        "단지 속 관리인 영혼은 특별한 능력이 있습니다. 주변 아이템을 자동으로 주워 "
        "인접한 보관함에 넣으므로 아주 쉽게 자동화할 수 있습니다!"
    ),
    (
        "Occultism integration for Ars Nouveau. Adds compatibility and "
        "interoperability between $(thing)Occultism$() and $(thing)Ars Nouveau$() "
        "and many QoL changes."
    ): (
        "Ars Nouveau용 Occultism 연동입니다. $(thing)Occultism$()과 $(thing)Ars "
        "Nouveau$() 사이의 호환성과 상호 운용 기능, 여러 편의 기능을 추가합니다."
    ),
}
PROTECTED = re.compile(
    r"https?://\S+"
    r"|%(?:\d+\$)?[a-zA-Z%]"
    r"|\{[A-Za-z0-9_]+\}"
    r"|\$\([^)]*\)"
    r"|[&§][0-9A-FK-ORa-fk-or]"
    r"|<[^>]+>"
    r"|\\n"
    r"|\n"
    r"|\d+(?:[.,]\d+)*(?:[xX×]\d+)?"
)


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """JSON을 UTF-8 무BOM 형식으로 기록한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def target_roots() -> list[Path]:
    """준비된 Ars Nouveau 네임스페이스 작업 폴더를 반환한다."""
    return [
        WORK_ROOT / target.namespace
        for target in family_goal.targets_for("ars_nouveau")
    ]


def translation_memory() -> tuple[dict[str, str], set[str]]:
    """현재 산출물의 자기 재사용을 제외한 기존 후보 번역 기억을 만든다."""
    values: dict[str, set[str]] = defaultdict(set)
    for root in target_roots():
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        sources = load_json(root / "candidate_sources.json")
        for key, source in english.items():
            target = korean[key]
            provenance = sources[key]
            if (
                not isinstance(source, str)
                or not isinstance(target, str)
                or source == target
                or provenance == "project_output_review"
            ):
                continue
            values[source].add(target)
    conflicts = {source for source, candidates in values.items() if len(candidates) > 1}
    memory = {
        source: next(iter(candidates))
        for source, candidates in values.items()
        if len(candidates) == 1
    }
    return memory, conflicts


def mask_text(text: str) -> tuple[str, list[str]]:
    """자동 번역에서 바뀌면 안 되는 토큰을 본문과 분리한다."""
    protected: list[str] = []

    def replace(match: re.Match[str]) -> str:
        index = len(protected)
        protected.append(match.group(0))
        return f"ZXQPROTECTED{index}QXZ"

    return PROTECTED.sub(replace, text), protected


def restore_text(text: str, protected: list[str]) -> str:
    """자동 번역 후보에 보호 토큰을 원래 위치대로 복원한다."""
    for index, value in enumerate(protected):
        token = f"ZXQPROTECTED{index}QXZ"
        if text.count(token) != 1:
            raise ValueError(f"자동 번역 보호 토큰이 바뀌었습니다: {token}:{text}")
        text = text.replace(token, value)
    if re.search(r"ZXQPROTECTED\d+QXZ", text):
        raise ValueError(f"복원되지 않은 보호 토큰이 있습니다: {text}")
    return text


def request_translation(source: str) -> str:
    """보호 처리한 영어 문장을 한국어 자동 번역 후보로 요청한다."""
    masked, protected = mask_text(source)
    query = urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": "ko", "dt": "t", "q": masked}
    )
    request = urllib.request.Request(
        f"{GOOGLE_TRANSLATE}?{query}",
        headers={"User-Agent": "ATM10-Korean-translation-candidate/1.0"},
    )
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            translated = "".join(row[0] for row in payload[0] if row and row[0])
            return restore_text(translated, protected)
        except Exception as exc:  # pragma: no cover - 외부 후보 서비스 오류 보고용
            last_error = exc
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"자동 번역 후보 요청 실패: {source}") from last_error


def build_candidates() -> dict[str, object]:
    """미번역 키의 안전한 자동 번역 후보를 별도 파일로 생성한다."""
    memory, conflicts = translation_memory()
    cache = load_json(CACHE_PATH) if CACHE_PATH.is_file() else {}
    requests: set[str] = set()
    rows: dict[str, dict[str, object]] = {}
    source_rows: dict[str, dict[str, str]] = {}
    for root in target_roots():
        english = load_json(root / "en_us.json")
        sources = load_json(root / "candidate_sources.json")
        candidates: dict[str, object] = {}
        candidate_sources: dict[str, str] = {}
        for key, value in english.items():
            if sources[key] != "new_translation_required":
                continue
            if not isinstance(value, str):
                raise TypeError(f"자동 후보가 지원하지 않는 자료형: {root.name}:{key}")
            if family_goal.is_allowed_original(value):
                candidates[key] = value
                candidate_sources[key] = "reviewed_original_candidate"
            elif value in MANUAL_CANDIDATES:
                candidates[key] = MANUAL_CANDIDATES[value]
                candidate_sources[key] = "manual_candidate"
            elif value in memory and value not in conflicts:
                candidates[key] = memory[value]
                candidate_sources[key] = "family_memory_candidate"
            elif isinstance(cache.get(value), str):
                candidates[key] = cache[value]
                candidate_sources[key] = "automatic_cache_candidate"
            else:
                requests.add(value)
        rows[root.name] = candidates
        source_rows[root.name] = candidate_sources

    failures: list[str] = []
    if requests:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(request_translation, source): source
                for source in sorted(requests)
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                except Exception as exc:  # pragma: no cover - 외부 오류 목록 보존
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_PATH, cache)
    if failures:
        raise RuntimeError("자동 번역 후보 생성 실패:\n" + "\n".join(failures))

    counts: Counter[str] = Counter()
    for root in target_roots():
        english = load_json(root / "en_us.json")
        sources = load_json(root / "candidate_sources.json")
        candidates = rows[root.name]
        candidate_sources = source_rows[root.name]
        for key, value in english.items():
            if sources[key] != "new_translation_required" or key in candidates:
                continue
            translated = cache[value]
            assert isinstance(value, str) and isinstance(translated, str)
            errors = family_goal.validate_value(key, value, translated)
            if errors:
                raise ValueError("; ".join(errors))
            candidates[key] = translated
            candidate_sources[key] = "automatic_translation_candidate"
        write_json(root / "auto_candidates.json", candidates)
        write_json(root / "auto_candidate_sources.json", candidate_sources)
        counts.update(candidate_sources.values())
    report = {
        "scope": "Ars Nouveau family automatic review candidates",
        "protected_patterns": [
            "numbers",
            "placeholders",
            "URLs",
            "format codes",
            "Patchouli tags",
            "markup tags",
            "line breaks",
        ],
        "current_output_self_reuse_excluded": True,
        "translation_memory_conflicts_excluded": len(conflicts),
        "candidate_counts": dict(sorted(counts.items())),
        "review_status": "pending_manual_review",
    }
    write_json(WORK_ROOT / "auto_candidate_report.json", report)
    return report


def patterned_name(source: str) -> str | None:
    """반복되는 방어구와 원소 장비 이름을 일관된 형식으로 번역한다."""
    match = re.fullmatch(
        r"(.+)'s (Helmet|Chestplate|Leggings|Boots|Hood|Tunic|Pants|Shoes|Cap|Set)",
        source,
    )
    if match and match.group(1) in PROPER_NAMES:
        return f"{PROPER_NAMES[match.group(1)]}의 {ARMOR_PARTS[match.group(2)]}"
    match = re.fullmatch(r"(?:Lesser )?Focus of (Air|Earth|Fire|Water)", source)
    if match:
        prefix = "하급 " if source.startswith("Lesser ") else ""
        return f"{prefix}{ELEMENTS[match.group(1)]} 포커스"
    match = re.fullmatch(r"Caster Tome of (Air|Earth|Fire|Water|Anima)", source)
    if match:
        return f"{ELEMENTS[match.group(1)]} 시전자 고서"
    return None


def normalize_korean(value: str) -> str:
    """검수에서 확정한 Ars Nouveau 공통 용어와 조작 문체를 통일한다."""
    replacements = (
        ("아르누보", "Ars Nouveau"),
        ("크리에이트", "Create"),
        ("Dominion Wand", "도미니언 완드"),
        ("도미니언 지팡이", "도미니언 완드"),
        ("Source Gem", "마나 보석"),
        ("Source Jar", "마나 단지"),
        ("Source Relay", "마나 전달체"),
        ("Sourcelink", "마나링크"),
        ("Archwood", "아크우드"),
        ("Source", "마나"),
        ("소스", "마나"),
        ("근원", "마나"),
        ("아치우드", "아크우드"),
        ("아치나무", "아크우드"),
        ("글리프", "문양"),
        ("엔터티", "개체"),
        ("스타번클", "별다람쥐"),
        ("드라이그미", "드리그미"),
        ("위시", "윅시"),
        ("패밀리어", "사역마"),
        ("주문 집중기", "주문 포커스"),
        ("소환 집중기", "소환 포커스"),
        ("집중기", "포커스"),
        ("하위 포커스", "하급 포커스"),
        ("주요 포커스", "상급 포커스"),
        ("마법 학교", "마법 학파"),
        ("학교", "학파"),
        ("비전 받침대", "아케인 받침대"),
        ("비전 코어", "아케인 코어"),
        ("비전 렌치", "아케인 렌치"),
        ("비전 압축기", "아케인 압축기"),
        ("비전 포장기", "아케인 포장기"),
        ("비전 망치", "아케인 망치"),
        ("마법책", "마도서"),
        ("주문 책", "마도서"),
        ("주문책", "마도서"),
        ("마우스 오른쪽 버튼을 클릭", "우클릭"),
        ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
        ("오른쪽 클릭", "우클릭"),
        ("호기심", "Curios"),
        ("실크 터치", "섬세한 손길"),
        ("폭도를 죽일 때", "몹을 처치할 때"),
        ("마나 할인", "마나 비용 감소"),
        ("스레드", "실타래"),
        ("두번째", "두 번째"),
        ("세가지", "세 가지"),
        ("때 마다", "때마다"),
        ("할때", "할 때"),
        ("하게됩니다", "하게 됩니다"),
        ("필요로합니다", "필요로 합니다"),
        ("상태이상", "상태 이상"),
        ("마나 비용 감소을", "마나 비용 감소 효과를"),
        ("마나을", "마나를"),
        ("마나이", "마나가"),
        ("증폭되고 할인됩니다", "강화되고 마나 비용이 감소합니다"),
        ("증폭시키고 할인합니다", "강화하고 마나 비용을 줄입니다"),
        ("증폭하고 할인합니다", "강화하고 마나 비용을 줄입니다"),
        ("부여 할", "부여할"),
        ("사냥했을때", "사냥했을 때"),
        ("광역로", "광역으로"),
        ("잠깐동안", "잠깐"),
        ("잠시후", "잠시 후"),
        ("되는거 처럼", "되는 것처럼"),
        ("하는거 처럼", "하는 것처럼"),
        ("들고있는", "들고 있는"),
        ("되게할", "되게 할"),
        ("적용 시킬", "적용할"),
        ("부딫", "부딪"),
        ("좋지않은", "성능이 낮은"),
        ("cpu", "CPU"),
        ("optifine", "OptiFine"),
    )
    for before, after in replacements:
        value = value.replace(before, after)
    return value


def reviewed_value(namespace: str, key: str, source: str, candidate: str) -> str:
    """자동 후보를 원문, 키 문맥, 프로젝트 용어집에 맞춰 검수한다."""
    override = KEY_OVERRIDES.get(namespace, {}).get(key)
    if override is not None:
        return override
    override = SOURCE_OVERRIDES.get(source)
    if override is not None:
        return override
    pattern = patterned_name(source)
    if pattern is not None:
        return pattern
    return normalize_korean(candidate)


def review_candidates() -> dict[str, object]:
    """모든 신규 후보와 기존 한국어를 영어 원문에 맞춰 검수 작업본에 반영한다."""
    new_reviewed = 0
    existing_normalized = 0
    manual_overrides = 0
    for root in target_roots():
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        sources = load_json(root / "candidate_sources.json")
        candidates = load_json(root / "auto_candidates.json")
        for key, source in english.items():
            if not isinstance(source, str) or not isinstance(korean[key], str):
                continue
            before = korean[key]
            if sources[key] == "new_translation_required":
                candidate = candidates[key]
                if not isinstance(candidate, str):
                    raise TypeError(f"문자열 후보가 아닙니다: {root.name}:{key}")
                after = reviewed_value(root.name, key, source, candidate)
                new_reviewed += 1
            else:
                after = reviewed_value(root.name, key, source, before)
                if after != before:
                    existing_normalized += 1
            errors = family_goal.validate_value(key, source, after)
            if errors:
                raise ValueError("; ".join(errors))
            korean[key] = after
            if key in KEY_OVERRIDES.get(root.name, {}) or source in SOURCE_OVERRIDES:
                manual_overrides += 1
        write_json(root / "ko_kr.json", korean)
    report = {
        "new_entries_reviewed": new_reviewed,
        "existing_entries_normalized": existing_normalized,
        "manual_or_exact_overrides": manual_overrides,
        "review_status": "complete",
    }
    write_json(WORK_ROOT / "manual_review_report.json", report)
    return report


def review_quests() -> dict[str, object]:
    """Ars 관련 FTB Quests의 신규 문구와 기존 한국어 전체를 검수한다."""
    reviewed = 0
    existing_changed = 0
    remaining_new: list[str] = []
    for scope in ("ars_nouveau", "related"):
        root = WORK_ROOT / "quests" / scope
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        sources = load_json(root / "candidate_sources.json")
        for key, source in english.items():
            target = korean[key]
            if not isinstance(source, (str, list)) or not isinstance(
                target, (str, list)
            ):
                continue
            before = korean[key]
            override = QUEST_OVERRIDES.get(scope, {}).get(key)
            if override is not None:
                if isinstance(override, list):
                    reviewed_override: object = [
                        value.replace("\n", "\\n") for value in override
                    ]
                else:
                    reviewed_override = override.replace("\n", "\\n")
                if isinstance(source, list):
                    after = (
                        reviewed_override
                        if isinstance(reviewed_override, list)
                        else [reviewed_override]
                    )
                else:
                    after = reviewed_override
            elif sources[key] == "new_translation_required":
                if isinstance(source, str) and family_goal.is_allowed_original(source):
                    after = source
                else:
                    remaining_new.append(f"{scope}:{key}")
                    continue
            else:
                replacements = (
                    ("아르스 누보", "Ars Nouveau"),
                    ("아르스 엘리멘탈", "Ars Elemental"),
                    ("아르스", "Ars"),
                    ("근원", "마나"),
                    ("마법책", "주문서"),
                    ("주문 책", "주문서"),
                    ("아치나무", "아크우드"),
                    ("&2Earth 갑옷", "&2대지 갑옷"),
                    ("&cFire 갑옷", "&c화염 갑옷"),
                )

                def normalize_quest_text(value: str) -> str:
                    value = normalize_korean(value)
                    for old, new in replacements:
                        value = value.replace(old, new)
                    return value

                if isinstance(before, list):
                    after = [
                        normalize_quest_text(value) if isinstance(value, str) else value
                        for value in before
                    ]
                else:
                    after = normalize_quest_text(before)
            errors = family_goal.validate_value(key, source, after)
            if errors:
                raise ValueError("; ".join(errors))
            korean[key] = after
            reviewed += 1
            if sources[key] != "new_translation_required" and after != before:
                existing_changed += 1
        write_json(root / "ko_kr.json", korean)
    if remaining_new:
        raise ValueError("검수하지 않은 신규 퀘스트 키: " + ", ".join(remaining_new))
    report = {
        "quest_entries_reviewed": reviewed,
        "existing_quest_entries_changed": existing_changed,
        "remaining_new_translation_required": 0,
    }
    write_json(WORK_ROOT / "quest_review_report.json", report)
    return report


def replace_guide_literals(value: object, used: set[str]) -> object:
    """Ars Ocultas Patchouli JSON의 영어 literal만 확정 한국어로 바꾼다."""
    if isinstance(value, str):
        if value in OCULTAS_GUIDE_TRANSLATIONS:
            used.add(value)
        return OCULTAS_GUIDE_TRANSLATIONS.get(value, value)
    if isinstance(value, list):
        return [replace_guide_literals(child, used) for child in value]
    if isinstance(value, dict):
        return {
            key: replace_guide_literals(child, used) for key, child in value.items()
        }
    return value


def build_guides() -> dict[str, object]:
    """누락된 안내서 언어 키와 Ars Ocultas 한국어 Patchouli 페이지를 만든다."""
    if set(GUIDE_EXTRA_ENGLISH) != set(GUIDE_EXTRA_KOREAN):
        raise ValueError("안내서 추가 언어 키가 서로 다릅니다.")
    for key, source in GUIDE_EXTRA_ENGLISH.items():
        errors = family_goal.validate_value(key, source, GUIDE_EXTRA_KOREAN[key])
        if errors:
            raise ValueError("; ".join(errors))
    write_json(WORK_ROOT / "guide_extra_en_us.json", GUIDE_EXTRA_ENGLISH)
    write_json(WORK_ROOT / "guide_extra_ko_kr.json", GUIDE_EXTRA_KOREAN)
    for namespace in ("ars_nouveau", "ars_elemancy", "starbunclemania"):
        language_path = (
            PROJECT_ROOT
            / f"output/resourcepack/ATM10_Korean/assets/{namespace}/lang/ko_kr.json"
        )
        language = load_json(language_path)
        language.update(
            {
                key: value
                for key, value in GUIDE_EXTRA_KOREAN.items()
                if key.startswith(f"{namespace}.")
            }
        )
        write_json(language_path, language)

    instance = resolve_source_root()
    matches = sorted((instance / "mods").glob("ars_ocultas-*.jar"))
    if len(matches) != 1:
        raise FileNotFoundError(f"Ars Ocultas JAR 검색 실패: {matches}")
    source_root = "assets/ars_nouveau/patchouli_books/worn_notebook/en_us/"
    paths = (
        "entries/transmutation.json",
        "entries/gem.json",
        "entries/spirit_jar.json",
        "categories/ars_ocultas.json",
    )
    written: list[str] = []
    used: set[str] = set()
    with ZipFile(matches[0]) as archive:
        for relative in paths:
            data = json.loads(archive.read(source_root + relative).decode("utf-8-sig"))
            translated = replace_guide_literals(data, used)
            destination = (
                PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets/ars_nouveau/"
                "patchouli_books/worn_notebook/ko_kr" / relative
            )
            write_json(destination, translated)
            written.append(destination.relative_to(PROJECT_ROOT).as_posix())
    missing = set(OCULTAS_GUIDE_TRANSLATIONS) - used
    if missing:
        raise ValueError(
            f"Ars Ocultas 안내서 원문을 찾지 못했습니다: {sorted(missing)}"
        )
    return {
        "extra_language_keys": len(GUIDE_EXTRA_KOREAN),
        "patchouli_pages": written,
        "literal_replacements": len(used),
    }


def apply_candidates() -> dict[str, object]:
    """별도 검수한 자동 후보를 언어 작업본의 미번역 키에 반영한다."""
    changed = 0
    applied = 0
    for root in target_roots():
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        sources = load_json(root / "candidate_sources.json")
        candidates = load_json(root / "auto_candidates.json")
        expected = {
            key for key in english if sources[key] == "new_translation_required"
        }
        if set(candidates) != expected:
            raise ValueError(
                f"자동 후보 키 불일치: {root.name}:"
                f"누락={sorted(expected - set(candidates))},"
                f"초과={sorted(set(candidates) - expected)}"
            )
        for key in expected:
            translated = candidates[key]
            errors = family_goal.validate_value(key, english[key], translated)
            if errors:
                raise ValueError("; ".join(errors))
            applied += 1
            if korean[key] != translated:
                korean[key] = translated
                changed += 1
        write_json(root / "ko_kr.json", korean)
    return {"applied_review_candidates": applied, "changed": changed}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("candidates", "apply-candidates", "review", "build-guides"),
    )
    args = parser.parse_args()
    resolve_source_root()
    if args.command == "candidates":
        result = build_candidates()
    elif args.command == "apply-candidates":
        result = apply_candidates()
    elif args.command == "review":
        result = {
            "language": review_candidates(),
            "quests": review_quests(),
        }
    else:
        result = build_guides()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
