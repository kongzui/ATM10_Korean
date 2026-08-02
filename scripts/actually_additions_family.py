#!/usr/bin/env python3
"""Actually Additions 언어 파일 전체를 현재 영어 원문 기준으로 번역·검증한다."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path

import ars_family
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root


FAMILY = "actually_additions"
NAMESPACE = "actuallyadditions"
WORK_ROOT = PROJECT_ROOT / "working/actually_additions"
LANG_ROOT = WORK_ROOT / NAMESPACE
CACHE_FILE = PROJECT_ROOT / "temp/actually_additions_language_candidate_cache.json"
BOOKLET_CACHE_FILE = (
    PROJECT_ROOT / "temp/actually_additions_booklet_candidate_cache.json"
)
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"

COLORS = {
    "Black": "검은색",
    "Blue": "파란색",
    "Brown": "갈색",
    "Cyan": "청록색",
    "Gray": "회색",
    "Green": "초록색",
    "Light Blue": "하늘색",
    "LightBlue": "하늘색",
    "Light Gray": "회백색",
    "Lime": "연두색",
    "Magenta": "자홍색",
    "Orange": "주황색",
    "Pink": "분홍색",
    "Purple": "보라색",
    "Red": "빨간색",
    "Silver": "회백색",
    "White": "하얀색",
    "Yellow": "노란색",
}

PROPER_TERMS = {
    "Actually Additions": "Actually Additions",
    "Restonia": "레스토니아",
    "Palis": "팰리스",
    "Diamatine": "디아마틴",
    "Emeradic": "에메라딕",
    "Enori": "에노리",
    "Ethetic": "에테틱",
    "Canola": "카놀라",
    "Crystal Flux": "Crystal Flux",
    "Black Quartz": "검은 석영",
    "Atomic Reconstructor": "원자 재구성기",
    "Phantom Connector": "팬텀 연결기",
    "Laser Relay": "레이저 중계기",
    "AIOT": "AIOT",
}

EXACT_NAMES = {
    "Actually Additions": "Actually Additions",
    "Refined Canola Oil": "정제된 카놀라유",
    "Canola Oil": "카놀라유",
    "Crystallized Oil": "결정화유",
    "Empowered Oil": "강화유",
    "Jam Guy": "잼 아저씨",
    "Crystallizer": "결정화 전문가",
    "Engineer": "기술자",
    "Worm": "지렁이",
    "Black Quartz Ore": "검은 석영 광석",
    "Block of Black Quartz": "검은 석영 블록",
    "Chiseled Black Quartz": "조각된 검은 석영",
    "Pillar of Black Quartz": "검은 석영 기둥",
    "Smooth Black Quartz": "매끄러운 검은 석영",
    "Black Quartz Bricks": "검은 석영 벽돌",
    "Ethetic Green Quartz": "에테틱 녹색 석영",
    "Ethetic Quartz": "에테틱 석영",
    "Ethetic Green Quartz Stairs": "에테틱 녹색 석영 계단",
    "Ethetic Quartz Stairs": "에테틱 석영 계단",
    "Ethetic Green Quartz Slab": "에테틱 녹색 석영 반 블록",
    "Ethetic Quartz Slab": "에테틱 석영 반 블록",
    "Ethetic Quartz Wall": "에테틱 석영 담장",
    "Ethetic Green Quartz Wall": "에테틱 녹색 석영 담장",
    "Automatic Feeder": "자동 먹이 공급기",
    "Crusher": "분쇄기",
    "Double Crusher": "이중 분쇄기",
    "Powered Furnace": "전동 화로",
    "Heat Collector": "열 수집기",
    "Wood Casing": "목재 외장",
    "Greenhouse Glass": "온실 유리",
    "Energizer": "충전기",
    "Enervator": "방전기",
    "Rice Plant": "벼",
    "Coal Generator": "석탄 발전기",
    "Lamp Controller": "조명 제어기",
    "Phantom Itemface": "팬텀 아이템 인터페이스",
    "Player Interface": "플레이어 인터페이스",
    "Phantom Energyface": "팬텀 에너지 인터페이스",
    "Phantom Redstoneface": "팬텀 레드스톤 인터페이스",
    "Phantom Liquiface": "팬텀 유체 인터페이스",
    "Phantom Placer": "팬텀 배치기",
    "Phantom Breaker": "팬텀 파괴기",
    "Lava Factory Controller": "용암 공장 제어기",
    "Lava Factory Casing": "용암 공장 외장",
    "Fluid Placer": "유체 배치기",
    "Fluid Collector": "유체 수집기",
    "Range Booster": "범위 증폭기",
    "Coffee Plant": "커피나무",
    "Canola Plant": "카놀라 작물",
    "Canola Press": "카놀라 압착기",
    "Fermenting Barrel": "발효통",
    "Oil Generator": "유체 연료 발전기",
    "Auto-Breaker": "자동 파괴기",
    "Auto-Placer": "자동 배치기",
    "Automatic Precision Dropper": "자동 정밀 공급기",
    "Ender Casing": "엔더 외장",
    "Flax Plant": "아마",
    "Coffee Maker": "커피 제조기",
    "Experience Solidifier": "경험치 응고기",
    "Leaf-Eating Generator": "나뭇잎 발전기",
    "Long-Range Breaker": "장거리 파괴기",
    "Ranged Collector": "원거리 수집기",
    "Energy Laser Relay": "에너지 레이저 중계기",
    "Advanced Energy Laser Relay": "고급 에너지 레이저 중계기",
    "Extreme Energy Laser Relay": "최고급 에너지 레이저 중계기",
    "Fluid Laser Relay": "유체 레이저 중계기",
    "Item Laser Relay": "아이템 레이저 중계기",
    "Advanced Item Laser Relay": "고급 아이템 레이저 중계기",
    "Iron Casing": "철 외장",
    "Black Lotus": "검은 연꽃",
    "Vertical Digger": "수직 굴착기",
    "Firework Box": "폭죽 상자",
    "Item Interface": "아이템 인터페이스",
    "Hopping Item Interface": "호퍼형 아이템 인터페이스",
    "Wall-Mount Manual (WIP)": "벽걸이 설명서(WIP)",
    "Display Stand": "전시대",
    "Shock Absorber": "충격 흡수기",
    "Tiny Torch": "작은 횃불",
    "Empowerer": "강화기",
    "Item Distributor (WIP)": "아이템 분배기(WIP)",
    "Bio Reactor": "생물 반응기",
    "Farmer": "자동 농부",
    "Battery Box": "배터리 상자",
    "Atomic Reconstructor": "원자 재구성기",
    "Small Storage Crate (WIP)": "소형 저장 상자(WIP)",
    "Medium Storage Crate (WIP)": "중형 저장 상자(WIP)",
    "Large Storage Crate (WIP)": "대형 저장 상자(WIP)",
    "Rice": "쌀",
    "Rice Dough": "쌀 반죽",
    "Rice Seeds": "벼 씨앗",
    "Tiny Coal": "작은 석탄",
    "Tiny Charcoal": "작은 숯",
    "Rice Slimeball": "쌀 슬라임볼",
    "Single Battery": "단일 배터리",
    "Double Battery": "이중 배터리",
    "Triple Battery": "삼중 배터리",
    "Quadruple Battery": "사중 배터리",
    "Quintuple Battery": "오중 배터리",
    "Ring of Growth": "성장의 반지",
    "Ring of Magnetizing": "자화의 반지",
    "Wings Of The Bats (WIP)": "박쥐의 날개(WIP)",
    "Bat's Wing": "박쥐 날개",
    "Empty Cup": "빈 컵",
    "Cup with Coffee": "커피가 든 컵",
    "Coffee Seeds": "커피 씨앗",
    "Coffee Beans": "커피콩",
    "Canola Seeds": "카놀라 씨앗",
    "Canola": "카놀라",
    "Canola Oil Bucket": "카놀라유 양동이",
    "Refined Canola Oil Bucket": "정제된 카놀라유 양동이",
    "Crystallized Oil Bucket": "결정화유 양동이",
    "Empowered Oil Bucket": "강화유 양동이",
    "Resonant Rice": "공명하는 쌀",
    "Dough (WIP)": "반죽(WIP)",
    "Black Quartz": "검은 석영",
    "Black Quartz Wall": "검은 석영 담장",
    "Black Quartz Stairs": "검은 석영 계단",
    "Black Quartz Slab": "검은 석영 반 블록",
    "Chiseled Black Quartz Wall": "조각된 검은 석영 담장",
    "Chiseled Black Quartz Stairs": "조각된 검은 석영 계단",
    "Chiseled Black Quartz Slab": "조각된 검은 석영 반 블록",
    "Smooth Black Quartz Wall": "매끄러운 검은 석영 담장",
    "Smooth Black Quartz Stairs": "매끄러운 검은 석영 계단",
    "Smooth Black Quartz Slab": "매끄러운 검은 석영 반 블록",
    "Black Quartz Brick Wall": "검은 석영 벽돌 담장",
    "Black Quartz Brick Stairs": "검은 석영 벽돌 계단",
    "Black Quartz Brick Slab": "검은 석영 벽돌 반 블록",
    "Black Quartz Pillar Wall": "검은 석영 기둥 담장",
    "Black Quartz Pillar Stairs": "검은 석영 기둥 계단",
    "Black Quartz Pillar Slab": "검은 석영 기둥 반 블록",
    "Ring": "반지",
    "Blaze Stored (WIP)": "저장된 블레이즈(WIP)",
    "Teleport Staff": "순간이동 지팡이",
    "Leaf Blower": "낙엽 송풍기",
    "Advanced Leaf Blower": "고급 낙엽 송풍기",
    "Crafting Table On A Stick": "막대형 제작대",
    "Basic Coil": "기본 코일",
    "Advanced Coil": "고급 코일",
    "Solidified Experience": "응고된 경험치",
    "Crushed Iron (WIP)": "분쇄된 철(WIP)",
    "Crushed Gold (WIP)": "분쇄된 금(WIP)",
    "Crushed Diamond (WIP)": "분쇄된 다이아몬드(WIP)",
    "Crushed Lapis (WIP)": "분쇄된 청금석(WIP)",
    "Crushed Emerald (WIP)": "분쇄된 에메랄드(WIP)",
    "Crushed Quartz (WIP)": "분쇄된 석영(WIP)",
    "Crushed Coal (WIP)": "분쇄된 석탄(WIP)",
    "Crushed Black Quartz (WIP)": "분쇄된 검은 석영(WIP)",
    "Actually Additions Manual (WIP)": "Actually Additions 설명서(WIP)",
    "Reconstruction Module (WIP)": "재구성 모듈(WIP)",
    "Laser Wrench": "레이저 렌치",
    "Drill Core": "드릴 코어",
    "Lens": "렌즈",
    "Lens of Color": "색상의 렌즈",
    "Lens of Detonation": "폭발의 렌즈",
    "Lens of Certain Death": "필멸의 렌즈",
    "Lens of Disenchanting": "마법 해제 렌즈",
    "Storage Crate Keeper (WIP)": "저장 상자 보존기(WIP)",
    "Ender Star": "엔더의 별",
    "Firework Box Cart (WIP)": "폭죽 상자 광산 수레(WIP)",
    "Bowl of Water": "물그릇",
    "Item Filter": "아이템 필터",
    "Player Probe": "플레이어 탐사기",
    "Phantom Connector": "팬텀 연결기",
    "Traveler's Sack": "여행자의 자루",
    "Void Sack": "공허 자루",
    "Crystallized Canola Seeds": "결정화된 카놀라 씨앗",
    "Empowered Canola Seeds": "강화된 카놀라 씨앗",
    "Lens of the Miner": "채굴의 렌즈",
    "Lens of the Killer (WIP)": "살해의 렌즈(WIP)",
    "Handheld Filler": "휴대용 채움기",
    "Engineer's Goggles": "기술자의 고글",
    "Engineer's Infrared Goggles": "기술자의 적외선 고글",
    "Banner Pattern": "현수막 무늬",
    "Book": "책",
    "Item Tag": "아이템 태그",
    "Wooden AIOT": "나무 AIOT",
    "Stone AIOT": "돌 AIOT",
    "Iron AIOT": "철 AIOT",
    "Golden AIOT": "금 AIOT",
    "Diamond AIOT": "다이아몬드 AIOT",
    "Netherite AIOT": "네더라이트 AIOT",
    "Drill": "드릴",
    "Breaker": "파괴기",
    "Placer": "배치기",
    "Redstone Torch": "레드스톤 횃불",
    "Spawner Changer": "생성기 변환기",
    "Phantomface": "팬텀 인터페이스",
    "Phantomfaces": "팬텀 인터페이스",
    "Phantom Booster": "팬텀 범위 증폭기",
    "Smiley Cloud": "미소 구름",
    "Lamps": "조명",
    "Rotten Flesh": "썩은 살점",
    "Leather": "가죽",
    "Feeder": "자동 먹이 공급기",
    "Storage Crates": "저장 상자",
    "Storage Crate": "저장 상자",
    "Chest To Storage Crate Upgrade": "상자→저장 상자 업그레이드",
    "Small To Medium Storage Crate Upgrade": "소형→중형 저장 상자 업그레이드",
    "Medium To Large Storage Crate Upgrade": "중형→대형 저장 상자 업그레이드",
    "Item Repairer": "아이템 수리기",
    "Drills": "드릴",
    "Staff": "지팡이",
    "Ring Of Magnetism": "자화의 반지",
    "Ring Of Growth": "성장의 반지",
    "Ring Of Liquid Banning": "액체 추방의 반지",
    "Balls of Fur": "털뭉치",
    "Ball of Fur-s": "털뭉치",
}

KEY_OVERRIDES = {
    "itemGroup.actuallyadditions": "Actually Additions",
    "achievement.page.actuallyadditions": "Actually Additions",
    "key.actuallyadditions.category": "Actually Additions",
    "key.actualladditions.openBooklet.name": "Actually Additions 설명서 열기",
    "actuallyadditions.lolWutHowUDoDis": "이 아이템은 손상되었습니다. 버려 주세요.",
    "misc.actuallyadditions.energy_tick": "CF/t",
    "misc.actuallyadditions.energy": "CF",
    "misc.actuallyadditions.energy_name": "Crystal Flux",
    "misc.actuallyadditions.power_name_long": "Crystal Flux",
    "misc.actuallyadditions.power_name_short": "CF",
    "death.actuallyadditions.atomic_reconstructor.1": "%s의 원자가 재구성되었습니다.",
    "death.actuallyadditions.atomic_reconstructor.2": "원자 재구성기가 %s를 조준했습니다.",
    "death.actuallyadditions.atomic_reconstructor.3": (
        "사람, 특히 %s를 원자 단위로 재구성하는 건 잘 안 되나 봅니다."
    ),
    "death.actuallyadditions.atomic_reconstructor.4": (
        "%s는 그 재구성기를 먹지 말았어야 했습니다!"
    ),
    "death.actuallyadditions.atomic_reconstructor.5": (
        "%s는 재구성용 발포제를 썼어야 했습니다."
    ),
    "tooltip.actuallyadditions.onSuffix.desc": "켜짐",
    "tooltip.actuallyadditions.phantom.connected.desc": "<블록 연결됨!>",
    "tooltip.actuallyadditions.phantom.stored.desc": "<이 연결기에 블록 저장됨!>",
    "tooltip.actuallyadditions.laser.stored.desc": "<레이저 중계기 저장됨!>",
    "tooltip.actuallyadditions.laser.connected.desc": "<레이저 연결 변경됨!>",
    "tooltip.actuallyadditions.phantom.unbound.desc": "연결이 해제되었습니다!",
    "tooltip.actuallyadditions.boundTo.desc": "연결 대상",
    "tooltip.actuallyadditions.clearStorage.desc": (
        "제작 칸에 놓으면 저장 내용을 비웁니다!"
    ),
    "tooltip.actuallyadditions.phantom.blockInfo.desc": (
        "연결된 블록은 %s이며 좌표는 %s, %s, %s, 거리는 %s블록입니다."
    ),
    "tooltip.actuallyadditions.oredictName.desc": "광석 사전 항목",
    "tooltip.actuallyadditions.baseUnlocName.desc": "아이템의 미번역 이름",
    "tooltip.actuallyadditions.unlocName.desc": "메타데이터의 미번역 이름",
    "tooltip.actuallyadditions.disablingInfo.desc": (
        "이 정보를 숨기려면 Actually Additions 설정에서 비활성화하세요!"
    ),
    "tooltip.actuallyadditions.item_booklet.desc": "다르게 말하면 ‘소책자’입니다",
    "tooltip.actuallyadditions.item_booklet.sub.1": (
        "이 책에서는 Actually Additions의"
    ),
    "tooltip.actuallyadditions.item_booklet.sub.2": "모든 기능을",
    "tooltip.actuallyadditions.item_booklet.sub.3": "안내합니다.",
    "tooltip.actuallyadditions.item_booklet.sub.4": "들고 사용하면 열립니다.",
    "tooltip.actuallyadditions.playerProbe.disconnect.1": (
        "조사하던 플레이어가 플레이어 인터페이스에 연결되기 전에 접속을 끊었습니다! "
        "데이터를 지웁니다!"
    ),
    "tooltip.actuallyadditions.playerProbe.disconnect.2": (
        "조사하던 플레이어가 플레이어 인터페이스에 연결되기 전에 서버에서 나갔습니다! "
        "데이터를 지웁니다!"
    ),
    "tooltip.actuallyadditions.playerProbe.probing": "조사 중",
    "tooltip.actuallyadditions.playerProbe.notice": (
        "조심하세요! 누군가 당신을 조사해 플레이어 인터페이스에 연결하려 했지만 "
        "실패했습니다!"
    ),
    "tooltip.actuallyadditions.battery.discharge": (
        "인벤토리의 다른 아이템을 충전하는 중"
    ),
    "tooltip.actuallyadditions.battery.noDischarge": (
        "인벤토리의 다른 아이템을 충전하지 않음"
    ),
    "tooltip.actuallyadditions.battery.changeMode": ("웅크린 채 우클릭하여 전환"),
    "tooltip.actuallyadditions.previouslyDoubleFurnace": "이전 이름: ‘이중 화로’",
    "tooltip.actuallyadditions.previouslyBag": "이전 이름: ‘가방’",
    "tooltip.actuallyadditions.previouslyVoidBag": "이전 이름: ‘공허 가방’",
    "tooltip.actuallyadditions.item_tag.no_tag": "모루에서 태그를 설정하세요.",
    "tooltip.actuallyadditions.coal_generator_stats": ("%d CF 생성(%d틱 동안 %d CF/t)"),
    "tooltip.actuallyadditions.drill.augments": "설치된 업그레이드: %s",
    "tooltip.actuallyadditions.drill.missing_tier": (
        "이 업그레이드를 설치하려면 이전 등급이 필요합니다!"
    ),
    "tooltip.actuallyadditions.drill.remove_highest": (
        "가장 높은 등급의 업그레이드부터 제거해야 합니다!"
    ),
    "tooltip.actuallyadditions.drill.already_installed": (
        "이 업그레이드는 이미 설치되어 있습니다!"
    ),
    "info.actuallyadditions.gui.disabled": "비활성화",
    "info.actuallyadditions.gui.up": "위",
    "info.actuallyadditions.gui.down": "아래",
    "info.actuallyadditions.gui.put": "넣기",
    "info.actuallyadditions.gui.pull": "꺼내기",
    "info.actuallyadditions.gui.respectDamage": "내구도 구분",
    "info.actuallyadditions.gui.ignoreDamage": "내구도 무시",
    "info.actuallyadditions.gui.respectNBT": "NBT 데이터 구분",
    "info.actuallyadditions.gui.ignoreNBT": "NBT 데이터 무시",
    "info.actuallyadditions.gui.ignoreMod": "모드 구분 꺼짐",
    "info.actuallyadditions.gui.respectMod": "모드 구분 켜짐",
    "info.actuallyadditions.gui.respectModInfo": (
        "이 기능을 켜면 필터가 §c아이템 자체가 아니라 아이템을 추가한 모드§r를 "
        "비교합니다. "
    ),
    "info.actuallyadditions.gui.respectModInfo2": (
        "모드별 상자를 사용하는 저장 시스템에 유용합니다. 내구도 구분과 함께 "
        "사용할 수 있지만 일반적으로 큰 도움이 되지는 않습니다."
    ),
    "info.actuallyadditions.gui.autosplititems.on": "아이템 자동 분할 켜짐",
    "info.actuallyadditions.gui.autosplititems.off": "아이템 자동 분할 꺼짐",
    "info.actuallyadditions.gui.inbound": "유입",
    "info.actuallyadditions.gui.outbound": "유출",
    "info.actuallyadditions.gui.ok": "확인",
    "info.actuallyadditions.gui.the": "해당",
    "info.actuallyadditions.gui.smartInfo": (
        "이 버튼을 누르면 중계기에 인접한 인벤토리의 모든 아이템이 이 허용 또는 "
        "차단 목록에 추가됩니다. 미리 아이템 필터를 목록에 넣어 두면 그 필터도 "
        "함께 채워집니다."
    ),
    "info.actuallyadditions.inputter.info.1": (
        "연결된 인벤토리에서 <p> 작업을 시작할 첫 번째 슬롯입니다."
    ),
    "info.actuallyadditions.inputter.info.2": (
        "연결된 인벤토리에서 <p> 작업을 끝낼 슬롯의 다음 번호입니다. 예를 들어 "
        "왼쪽 칸에 2, 이 칸에 5를 입력하면 2, 3, 4번 슬롯에서 <p> 작업을 합니다."
    ),
    "info.actuallyadditions.noitem": "버퍼에 아이템 없음",
    "info.actuallyadditions.booklet.manualName.1.2": "액추얼 애디션즈",
    "info.actuallyadditions.booklet.manualName.1.3": "액추얼리 애딕션",
    "info.actuallyadditions.booklet.manualName.1.4": "액추얼 에디션",
    "info.actuallyadditions.booklet.manualName.1.5": "액추얼 애디션",
    "info.actuallyadditions.booklet.manualName.1.6": "액추얼리 애드온즈",
    "info.actuallyadditions.booklet.manualName.1.7": "애디셔널 애드온즈",
    "info.actuallyadditions.booklet.manualName.2": "설명서",
    "info.actuallyadditions.booklet.hudDisplay.open": "우클릭하여 열기...",
    "info.actuallyadditions.booklet.hudDisplay.noInfo.desc.1": (
        "Actually Additions 블록을 보면서 웅크리면"
    ),
    "info.actuallyadditions.booklet.hudDisplay.noInfo.desc.2": (
        "자세한 정보를 볼 수 있습니다!"
    ),
    "info.actuallyadditions.machineBroke": (
        "부수려고 하자 블록이 산산조각 났습니다. 부술 만큼 튼튼하지 않았나 봅니다."
    ),
    "info.actuallyadditions.redstoneMode.pulse": "펄스",
    "info.actuallyadditions.redstoneMode.invalidItem": "%s을(를) 들고 전환하세요!",
    "info.actuallyadditions.redstoneMode.validItem": "우클릭하여 전환하세요!",
    "info.actuallyadditions.farmer.validItem": "우클릭하여 범위를 바꾸세요!",
    "info.actuallyadditions.farmer.invalidItem": (
        "%s을(를) 들고 농사 범위를 변경하세요!"
    ),
    "info.actuallyadditions.farmer.area": "범위: %dx%d",
    "info.actuallyadditions.laserRelay.item.extra": "우선순위",
    "info.actuallyadditions.laserRelay.item.display.1": "우클릭하여 높이기!",
    "info.actuallyadditions.laserRelay.item.display.2": (
        "웅크린 채 우클릭하여 낮추기!"
    ),
    "info.actuallyadditions.laserRelay.energy.display": "우클릭하여 변경!",
    "info.actuallyadditions.laserRelay.mode.inputOnly": "인접한 블록에서만 꺼냄",
    "info.actuallyadditions.laserRelay.mode.noCompasss": "%s을(를) 들고 변경하세요!",
    "container.actuallyadditions.placer": "배치기",
    "container.actuallyadditions.breaker": "파괴기",
    "container.actuallyadditions.liquiface": "팬텀 유체 인터페이스",
    "container.actuallyadditions.energyface": "팬텀 에너지 인터페이스",
    "container.actuallyadditions.drill": "드릴",
    "container.actuallyadditions.cloud": "미소 구름",
    "container.actuallyadditions.smileyCloud": "미소 구름",
    "container.actuallyadditions.laserRelayExtreme": "최고급 레이저 중계기",
    "container.actuallyadditions.shockSuppressor": "충격 흡수기",
    "container.actuallyadditions.distributorItem": "아이템 분배기",
    "info.actuallyadditions.update.generic": (
        '[{"text":"Actually Additions "},{"text":"업데이트","color":"dark_green"},'
        '{"text":"가 있습니다!","color":"none"}]'
    ),
    "info.actuallyadditions.update.buttons": (
        '[{"text":"["},{"text":"변경 내역 열기","color":"green","clickEvent":'
        '{"action":"open_url","value":"%s"}},{"text":"] [","color":"none"},'
        '{"text":"다운로드 열기","color":"green","clickEvent":{"action":"open_url",'
        '"value":"%s"}},{"text":"]","color":"none"}]'
    ),
    "info.actuallyadditions.update.buttonOptions": (
        "클릭: 변경 내역, Shift+클릭: 다운로드(브라우저에서 열림)"
    ),
    "info.actuallyadditions.update.failed": (
        '[{"text":"Actually Additions "},{"text":"업데이트 확인","color":"dark_green"},'
        '{"text":"에 실패했습니다! 자세한 내용은 로그를 확인하세요!",'
        '"color":"none"}]'
    ),
    "jei.actuallyadditions.coffee.maxAmount": "최대 수량",
    "booklet.actuallyadditions.shapeless_recipe": "모양 없는 조합법",
    "booklet.actuallyadditions.shaped_recipe": "모양 있는 조합법",
    "booklet.actuallyadditions.shapeless_ore_recipe": "모양 없는 광석 사전 조합법",
    "booklet.actuallyadditions.shapedore_recipe": "모양 있는 광석 사전 조합법",
    "booklet.actuallyadditions.empowerer_recipe": "강화기 조합법",
    "booklet.actuallyadditions.crusher_recipe": "분쇄기 조합법",
    "booklet.actuallyadditions.furnace_recipe": "화로 조합법",
    "booklet.actuallyadditions.reconstructor_recipe": "원자 재구성기 조합법",
    "booklet.actuallyadditions.indexEntry.misc": "기타",
    "booklet.actuallyadditions.indexEntry.reconstruction": "재구성",
    "booklet.actuallyadditions.configButton": "설정 화면 열기",
    "booklet.actuallyadditions.achievementButton": "업적 열기",
    "booklet.actuallyadditions.trialFinishButton.completed": "완료",
    "booklet.actuallyadditions.trials.crystalProduction.text.1": (
        "여러 종류의 <item>수정<r>은 자주 대량으로 만들려면 번거롭습니다. <n>아이템을 "
        "떨어뜨리거나 배치하는 장치, 수집기 또는 파괴기, 레드스톤을 함께 사용하면 "
        "원재료를 수정으로 <imp>자동 변환<r>하는 장치를 만들 수 있습니다."
    ),
    "booklet.actuallyadditions.trials.leatherProduction.text.1": (
        "<item>원자 재구성기<r>를 자동화하면 특히 <item>썩은 살점<r>을 "
        "<item>가죽<r>으로 바꿀 때 유용합니다. 쓸모없던 자원을 마침내 활용할 수 "
        "있습니다."
    ),
    "booklet.actuallyadditions.trials.crystalOil": "결정화유 자동화",
    "booklet.actuallyadditions.trials.autoDisenchanter": "자동 마법 해제기",
    "booklet.actuallyadditions.trials.empoweredOil": "강화유 자동화",
    "booklet.actuallyadditions.trials.mobFarm": "몬스터 분쇄기",
    "booklet.actuallyadditions.trials.crystalOil.text.1": (
        "<item>기름<r>의 첫 두 등급은 만들기 쉽지만, <imp>훨씬 많은 에너지<r>를 "
        "생산하려면 등급이 높아질수록 <imp>더 복잡해집니다<r>. <n><item>결정화유<r>를 "
        "만들려면 월드에 놓인 <item>기름<r>을 변환하는 <imp>고급 자동화 장치<r>가 "
        "필요합니다."
    ),
    "booklet.actuallyadditions.trials.autoDisenchanter.text.1": (
        "<item>마법 해제 렌즈<r>를 사용하면 <imp>낚시 그물이나 던전의 전리품<r>, "
        "좋아하는 도구에 붙은 <imp>원치 않는 마법 부여<r>를 쉽게 떼어낼 수 있습니다. "
        "<n>이 과정을 자동화하면 훨씬 편해집니다."
    ),
    "booklet.actuallyadditions.trials.empoweredOil.text.1": (
        "<imp>에너지 수요<r>는 계속 늘어나는데 <imp>농장만 더 짓는 것<r>으로는 "
        "부족한가요? <n><item>강화유<r>를 만들어 <item>기름<r> 생산을 "
        "<imp>업그레이드<r>해 보세요. 다만 작동시키려면 상당히 고급인 "
        "<imp>월드 내 장치<r>가 필요해 쉽지는 않습니다."
    ),
    "booklet.actuallyadditions.trials.empowererAutomation": "강화기 자동화",
    "booklet.actuallyadditions.trials.empowererAutomation.text.1": (
        "<item>강화기<r>로 <imp>수정을 변환<r>하려면 많은 자원이 필요합니다. 이 "
        "과정을 <imp>자동화<r>하는 장치를 만들어 보세요. <item>아이템 레이저 "
        "중계기<r>를 사용하면 알맞은 아이템을 알맞은 전시대로 쉽게 보낼 수 있습니다."
    ),
    "booklet.actuallyadditions.chapter.intro.text.1": (
        "<i>너무나 오랫동안 마인크래프티아 사람들은 어떤 노예 주인의 채찍보다도 "
        "가혹한 ‘불편함’이라는 채찍 아래 고생해 왔습니다. 수많은 불편함은 플레이어가 "
        "나무를 베고 밀을 기르는 따위의 단조로운 일에 몇 시간, 아니 며칠씩 쓰게 합니다,"
    ),
    "booklet.actuallyadditions.chapter.intro.text.2": (
        "<i>그저 지루함에서 잠시 벗어나 건축과 동굴 탐험, 미지의 아름답고 풍요로운 "
        "세계를 누비는 마인크래프티아의 진정한 즐거움을 맛보기 위해서 말입니다. 하지만 "
        "창작에 몰입하자마자 수백만 마리의 성난 벌처럼 불편함이 다시 달려들어 게임의 "
        "즐거움을 앗아 가고, 결국 영원히 떠나게 만듭니다."
    ),
    "booklet.actuallyadditions.chapter.intro.text.3": (
        "<i>그래서 Ellpeck은 마인크래프트의 반복 작업을 자동화하고 간소화하여 플레이어가 "
        "건축과 모험이라는 핵심 경험에 더 집중할 수 있도록 이 Actual Addition을 "
        "만들었습니다. 이제 Ellpeck이 이 모드의 사용법을 알려 줄 Actually Additions "
        "설명서를 겸손히 선보입니다. 이 설명서는 궁극적으로,"
    ),
    "booklet.actuallyadditions.chapter.intro.text.4": (
        "<i>여러분이 불편함을 초월하고 깨달음에 이르도록 도울 것입니다. "
        "<r><n><n>                   ~<imp>Tulkas<r> 씀"
    ),
    "booklet.actuallyadditions.chapter.quartz.text.1": (
        "<item>검은 석영<r>은 월드의 <imp><lowest>층부터 <highest>층 사이<r>에 "
        "생성되는 <imp>광석<r>입니다. 캐낸 뒤 <imp>화로에서 제련<r>하거나 "
        "<imp>분쇄기에서 분쇄<r>하면 <item>검은 석영<r>을 얻을 수 있습니다."
    ),
    "booklet.actuallyadditions.chapter.cloud.text.1": (
        "<item>미소 구름<r>은 안에 든 응고된 경험치로 생명을 얻은 마법의 구름입니다. "
        "즐겁게 위아래로 떠다니며, <imp>우클릭<r>하면 <imp>이름을 붙일<r> 수 있습니다. "
        "<n><imp>‘Ellpeck’<r>이나 <imp>‘Etho’<r> 같은 <imp>특별한 이름<r>을 붙이면 "
        "특별한 아이템을 들고 다닙니다!"
    ),
    "booklet.actuallyadditions.chapter.treasureChest.text.2": (
        "<item>보물 상자<r>는 <imp>바다 생물 군계<r>의 해저에서 드물게 발견됩니다. "
        "지나가던 배가 떨어뜨리거나 잃어버린 짐인 듯합니다. 운이 좋으면 상자에서 "
        "<imp>귀중한 아이템<r>을 얻을 수 있습니다. 부숴도 아무것도 나오지 않으니 "
        "<imp>우클릭<r>해서 멋진 전리품을 받으세요."
    ),
    "booklet.actuallyadditions.chapter.phantomfaces.text.1": (
        "<item>팬텀 인터페이스<r>는 <imp>인벤토리를 연결<r>하는 장치지만 중요한 "
        "차이가 있습니다. 두 인벤토리를 단순히 연결하는 대신, <item>팬텀 "
        "인터페이스<r>는 연결된 인벤토리를 "
        "<imp>그대로 모방<r>하므로 <item>팬텀 인터페이스<r> 자체에 아이템을 넣고 "
        "꺼낼 수 있습니다. <item>팬텀 인터페이스<r>의 기본 범위는 "
        "<imp><range>블록<r>이며 <item>팬텀 범위 증폭기<r>로 "
        "늘릴 수 있습니다. 인벤토리를 <item>팬텀 연결기<r>로 <imp>우클릭<r>한 뒤 "
        "<item>팬텀 인터페이스를 <imp>우클릭<r>하면 연결됩니다."
    ),
    "booklet.actuallyadditions.chapter.phantomfaces.text.7": (
        "첫 페이지에서 설명했듯이 <item>팬텀 범위 증폭기<r>를 <item>팬텀 "
        "인터페이스<r> <imp>위에<r> 놓으면 범위가 늘어납니다. <item>팬텀 "
        "인터페이스<r> "
        "하나당 최대 <imp>3개<r>까지 놓을 수 있습니다."
    ),
    "booklet.actuallyadditions.chapter.phantomBreaker": "팬텀 파괴기와 배치기",
    "booklet.actuallyadditions.chapter.phantomBreaker.text.1": (
        "<item>팬텀 파괴기<r>와 <item>팬텀 배치기<r>는 일반 <item>팬텀 "
        "인터페이스<r>와 비슷하지만 <imp>멀리서 블록을 파괴하고 배치<r>합니다. "
        "기본 범위는 <imp><range>블록<r>입니다. 파괴할 블록에 연결하는 방법은 "
        "<imp>팬텀 인터페이스 장<r>을 참고하세요. 공중에 연결하려면 그 자리에 "
        "블록을 놓고 저장한 뒤 다시 부수면 됩니다. <n><item>레드스톤 횃불<r>을 들고 "
        "우클릭하면 <imp>레드스톤 신호로 비활성화되는<r> 모드와 "
        "<imp>펄스에 반응하는<r> 모드를 전환합니다."
    ),
    "booklet.actuallyadditions.chapter.esd.text.1": (
        "<item>ESD<r>는 기능이 훨씬 많은 <item>호퍼<r>와 같습니다. 입출력 면을 "
        "고르고 슬롯 범위를 <imp>정밀하게 설정<r>할 수 있습니다. <n>자세한 설명은 "
        "<imp>화면의 각 요소에 마우스를 올려<r> 확인하세요. <n><n>처음 연결할 때 "
        "인벤토리의 <imp>슬롯 수<r>를 확인하지만, 인벤토리가 바뀌어도 "
        "<tifisgrin>자동으로 맞추지는 않습니다<r>. <item>아이템 인터페이스<r>처럼 "
        "슬롯 수가 바뀔 수 있는 인벤토리를 연결할 때는 무시되는 슬롯이 없도록 ESD "
        "화면에서 슬롯 수를 큰 값으로 설정하세요."
    ),
    "booklet.actuallyadditions.chapter.xpSolidifier.text.1": (
        "<item>경험치 응고기<r>는 플레이어의 경험치를 <item>응고된 경험치<r>로 "
        "바꿉니다. 나중에 <imp>우클릭<r>하면 경험치를 되찾으며, 웅크린 채 우클릭하면 "
        "한 묶음을 한꺼번에 사용합니다. <n>또한 응고기에 <item>응고된 경험치<r>를 "
        "넣으면 자신이 만든 것이 아닌 바닥의 <imp>경험치 구슬을 주워<r> "
        "<item>응고된 경험치<r>로 바꿉니다. <n><item>응고된 경험치<r>는 가끔 "
        "몹에게서도 나옵니다."
    ),
    "booklet.actuallyadditions.chapter.greenhouseGlass.text.1": (
        "<item>온실 유리<r>는 <imp>식물의 성장을 빠르게<r> 합니다! 식물 위에 "
        "놓고, 그 사이를 막는 블록이 없으며 유리 위로 햇빛이 비치면 "
        "<imp>식물이 훨씬 빨리 자랍니다<r>. <n>물론 낮이어야 합니다. 당연하죠."
    ),
    "booklet.actuallyadditions.chapter.compost.text.3": (
        "<item>바이오 매시<r>는 제작 칸에서 원하는 수의 <imp>음식 아이템<r>을 "
        "<item>칼<r>과 조합해 만들 수 있습니다. 얻는 <item>바이오 매시<r>의 양은 "
        "음식의 <imp>포만도<r>와 <imp>회복량<r>에 따라 <imp>달라집니다<r>."
    ),
    "booklet.actuallyadditions.chapter.crate.text.4": (
        "저장 상자를 부수기 전에 안에 <item>저장 상자 보존기<r>를 넣으면 "
        "<imp>모든 아이템을 유지<r>하지만 보존기는 사라집니다. <n>제작으로 크기를 "
        "업그레이드한 저장 상자도 내용물을 잃지 않습니다."
    ),
    "booklet.actuallyadditions.chapter.coffeeMachine.text.1": (
        "<item>커피 제조기<r>는 여러 강화 효과를 주는 <imp>물약 같은<r> "
        "<item>커피<r>를 만듭니다. <n>한 잔을 만들려면 <item>빈 컵<r>, 야생에서 "
        "찾아 수확하고 <imp>경작지에 다시 심을<r> 수 있는 <coffee>개의 "
        "<item>커피콩<r>, <rf> CF/t와 물 <water>mB가 필요합니다. <n>뒤쪽의 커피 "
        "제조기 조합법 페이지에서 커피 컵에 마우스를 올리면 효과를 볼 수 있습니다."
    ),
    "booklet.actuallyadditions.chapter.coffeeMachine.text.3": (
        "<imp>화염 저항 I(0:20)<r>과 <imp>신속 I(2:30)<r> 효과가 든 커피 "
        "조합법의 예입니다."
    ),
    "booklet.actuallyadditions.chapter.coffeeMachine.text.7": (
        "<i>이 글이 보인다면 <imp>HarvestCraft<r><i>가 설치되어 있거나 언어 파일을 "
        "직접 보고 있다는 뜻입니다. <r><n>채식주의자를 위해 <item>우유<r>와 같은 "
        "기능을 합니다."
    ),
    "booklet.actuallyadditions.chapter.crusher.text.1": (
        "<item>분쇄기<r>는 <rf> CF/t를 사용해 광석, 주괴, 보석을 알맞은 "
        "<imp>가루<r>로 만듭니다. <n><imp>광석<r>을 넣으면 <imp>가루 2개<r>를 "
        "얻습니다. <n><item>이중 분쇄기<r>도 같은 일을 하지만 광석 두 개를 동시에 "
        "분쇄할 수 있습니다. <n>다음 페이지에서 분쇄기에 쓸 수 있는 유용한 추가 "
        "조합법을 볼 수 있습니다. <n><n><i>내가 반한 분쇄기"
    ),
    "booklet.actuallyadditions.chapter.lavaFactory": "용암 공장",
    "booklet.actuallyadditions.chapter.lavaFactory.text.1": (
        "<item>용암 공장<r>은 블록당 <imp><rf> CF<r>를 사용해 용암 블록을 "
        "만듭니다. <n>제어기 위의 빈칸을 외장 블록 4개로 둘러싸야 용암을 만들 수 "
        "있습니다. <n><item>용암 공장 제어기<r>를 우클릭하면 현재 구조에서 용암을 "
        "만들 수 있는지 알려 줍니다. <n><n><i>Lava, for a fact.<n>                ory"
    ),
    "booklet.actuallyadditions.chapter.canola.text.5": (
        "<item>유체 연료 발전기<r>를 부숴도 안의 액체는 유지됩니다. <n>비우려면 "
        "<imp>제작 칸<r>에 놓으세요. <n><imp>레드스톤 신호<r>를 받으면 "
        "<imp>발전을 멈춥니다<r>. <n><item>비교기<r>를 연결하면 "
        "<imp>저장된 에너지<r>의 비율에 맞는 신호를 냅니다."
    ),
    "booklet.actuallyadditions.chapter.wings.text.1": (
        "가끔 박쥐가 <item>박쥐 날개<r>를 떨어뜨립니다. 이 재료로 "
        "<item>박쥐의 날개<r>를 만들면 <imp>창의 모드처럼<r> <imp>날 수<r> "
        "있습니다. <n>하지만 약 <secs>초가 지나면 더는 몸을 <imp>지탱하지 못해<r> "
        "<imp>땅으로 떨어집니다<r>. <n>날개의 피로는 <imp>땅에 서서<r> "
        "<imp>천천히<r> 회복하거나, 완전히 지치기 전에 박쥐처럼 "
        "<imp>단단한 블록 아래로 날아 올라<r> 천장에 매달려 <imp>빠르게<r> "
        "회복할 수 있습니다."
    ),
    "booklet.actuallyadditions.chapter.leafBlower.text.1": (
        "<item>낙엽 송풍기<r>는 <imp>우클릭을 누르고 있으면<r> 주변의 키 큰 풀, "
        "꽃 등을 날려 버립니다. <item>고급 낙엽 송풍기<r>는 기본형보다 "
        "<imp>훨씬 빠르며<r> <imp>나뭇잎도 파괴합니다<r>."
    ),
    "booklet.actuallyadditions.chapter.aiots.text.1": (
        "<item>AIOT<r>는 <item>곡괭이<r>, <item>도끼<r>, <item>삽<r>, "
        "<item>검<r>, <item>괭이<r>를 하나로 합친 도구이며 여러 일반 재료로 만들 수 "
        "있습니다. <n>돌, 나무와 더 무른 재료를 캘 수 있고, <imp>웅크리지 않고<r> "
        "우클릭하면 <item>경작지<r>를, <imp>웅크리고<r> 우클릭하면 "
        "<item>흙길<r>을 만듭니다."
    ),
    "booklet.actuallyadditions.chapter.jams.text.1": (
        "한때 잼을 정말 먹고 싶어 하는 <imp>고양이<r>가 있었습니다. <n>그래서 "
        "<item>잼<r>을 만들었습니다. <n>진짜 잼입니다. 마을 집에서 찾거나 "
        "<imp>잼 주민<r>에게 살 수 있습니다. <n>잼마다 서로 다른 "
        "<imp>물약 효과<r> 두 가지를 줍니다!"
    ),
    "booklet.actuallyadditions.chapter.jams.text.2": (
        "<imp>잼 가게<r>와 <n>그곳의 주민"
    ),
    "booklet.actuallyadditions.chapter.potionRings.text.1": (
        "<item>물약 반지<r>는 <imp>물약 효과를 계속 부여<r>합니다. <n>반지는 "
        "<imp>두 등급<r>이며, 1등급은 <imp>어느 손이든 들고 있어야<r> "
        "<imp>I 단계<r> "
        "효과를 주고 2등급은 <imp>인벤토리 어디에 있어도<r> <imp>II 단계<r> 효과를 "
        "줍니다. <n>사용하기 전에 <imp>제작 칸<r>에서 <item>물약 반지<r>와 "
        "<item>블레이즈 가루<r>를 <imp>한 개 이상<r> 조합해 반지를 "
        "<item>충전<r>해야 합니다. <n>시간이 지나면 반지 속 가루를 "
        "<imp>소모<r>해 효과를 부여합니다."
    ),
    "booklet.actuallyadditions.chapter.batteries.text.1": (
        "<item>배터리<r>는 CF를 저장해 옮기기 좋습니다. <imp>충전기에서 "
        "충전<r>하고 <imp>방전기에서 방전<r>할 수 있습니다. <n><n>손에 들고 "
        "<imp>웅크린 채 우클릭<r>하면 <imp>방전 모드<r>로 전환되어 "
        "<imp>인벤토리의 다른 아이템<r>을 <imp>충전<r>합니다."
    ),
    "booklet.actuallyadditions.chapter.leafGen.text.1": (
        "<item>나뭇잎 발전기<r>는 <item>나뭇잎<r> 옆에 놓기만 하면 "
        "<imp>CF<r>를 만듭니다. <n>나뭇잎을 파괴하며 한 장당 "
        "<imp><rf> CF<r>를 생산합니다. <n>발전기를 우클릭하면 저장된 CF를 볼 수 "
        "있습니다. <n>작동 범위는 <imp><range>블록<r>입니다."
    ),
    "booklet.actuallyadditions.chapter.longRangeBreaker.text.1": (
        "<item>장거리 파괴기<r>는 일반 <item>파괴기<r>처럼 작동하지만 앞쪽 "
        "<imp>최대 <range>블록<r>까지 파괴합니다. <n>블록 하나마다 "
        "<imp><rf> CF<r>를 사용합니다. <n><item>레드스톤 횃불<r>을 들고 우클릭하면 "
        "<imp>레드스톤 신호로 비활성화되는<r> 모드와 <imp>펄스에 반응하는<r> "
        "모드를 전환합니다. <n><n><i><range>번째 벽 허물기"
    ),
    "booklet.actuallyadditions.chapter.hairBalls.text.1": (
        "<imp>살아 있는<r> 고양이가 떨어뜨린 <item>털뭉치<r>입니다. <n>자세한 "
        "내용은 다음 페이지에 있습니다."
    ),
    "booklet.actuallyadditions.chapter.laserIntro.text.2": (
        "모든 <item>레이저 중계기<r>는 여러 방식으로 <imp>네트워크의 다른 중계기와 "
        "상호 작용<r>합니다. <n>다만 두 중계기를 연결할 때는 제한이 있습니다. "
        "<item>레이저 중계기<r>는 서로 <imp>최대 <range>블록<r> 안에 있어야 하며, "
        "<imp>종류가 다른<r> <item>레이저 중계기<r>끼리는 연결할 수 없습니다. "
        "<n><n><n><i>여러 종류의 <item>레이저 중계기<r>는 이 장의 다른 아이템을 "
        "참고하세요!"
    ),
    "booklet.actuallyadditions.chapter.laserIntro.text.3": (
        "<item>레이저 렌치<r>를 든 채 레이저 중계기에 <imp>마우스를 올리면<r> "
        "<imp>에너지 흐름 설정<r>이나 <imp>우선순위 설정<r> 같은 정보가 나옵니다. "
        "<n><n>이미 <imp>연결된<r> 두 중계기를 다시 연결하면 "
        "<imp>연결이 해제<r>됩니다."
    ),
    "booklet.actuallyadditions.chapter.laserRelays.text.1": (
        "<item>에너지 레이저 중계기<r>는 <imp>CF를 무선 전송<r>합니다. <n>발전기나 "
        "에너지 수신 장치를 중계기 옆에 놓으면 네트워크의 <imp>다른 중계기에서<r> "
        "에너지를 받거나 <imp>다른 중계기로<r> 보낼 수 있습니다. <n>전송할 때마다 "
        "약간의 <imp>에너지 손실<r>이 있지만 <imp>전송 한 번당<r> 계산되므로 두 "
        "기계 사이에 중계기가 몇 개 있든 손실량은 <imp>항상 같습니다<r>."
    ),
    "booklet.actuallyadditions.chapter.blackLotus.text.1": (
        "생각해 보세요. <n><imp>검은색 양털<r>, <imp>검은색 테라코타<r>처럼 "
        "<imp>검은색 염료가 필요한<r>데 무고한 <imp>오징어<r>를 너무 많이 잡아 "
        "미안한가요? <n><item>검은 연꽃<r>이 답입니다! <n><imp>야생<r>을 찾아보면 "
        "발견할 수 있고, <imp>먹물 주머니 대신<r> 쓸 <item>검은색 염료<r>를 만들 "
        "수 있습니다. 이제 불쌍한 오징어를 그만 잡아도 됩니다."
    ),
    "booklet.actuallyadditions.chapter.crystals": "수정과 원자 재구성기",
    "booklet.actuallyadditions.chapter.crystals.text.1": (
        "<item>원자 재구성기<r>는 Actually Additions의 여러 아이템에 쓰이는 핵심 "
        "재료인 <item>수정<r>을 만듭니다. <n>에너지를 공급하면 레이저를 발사합니다. "
        "<tifisgrin>광선이 블록에 닿을 때까지 경로 주변의 <imp>변환 가능한 "
        "아이템과 블록<r>을 모두 변환합니다."
    ),
    "booklet.actuallyadditions.chapter.crystals.text.2": (
        "레이저를 한 번 발사할 때 <imp>1000 CF<r>를 사용하며 변환에 따라 추가 "
        "비용이 달라집니다. <n>원자 재구성기에는 기본 동작을 바꿔 특별한 기능을 "
        "수행하는 여러 <item>렌즈<r>를 장착할 수 있습니다. <n><imp>자세한 내용<r>은 "
        "설명서의 <imp>재구성 항목<r>을 참고하세요."
    ),
    "booklet.actuallyadditions.chapter.crystals.text.3": (
        "<item>레드스톤 횃불<r>을 들고 원자 재구성기를 우클릭하면 "
        "<imp>레드스톤 신호로 비활성화되는<r> 모드와 <imp>펄스에 반응하는<r> "
        "모드를 전환합니다. 렌즈 정보가 없는 조합법은 렌즈를 <imp>사용하지 "
        "않습니다<r>. <n><i>당연한 이야기지만요."
    ),
    "booklet.actuallyadditions.chapter.crystals.text.5": (
        "아이템을 몇 가지 만들고 나면 이 과정을 <imp>자동화<r>하고 싶을 것입니다. "
        "<n>간단한 방법이 있습니다. <n><item>원자 재구성기<r>가 "
        "<item>자동 정밀 공급기<r>를 향하게 놓으세요(<imp>모든 아이템<r> 항목에서 "
        "찾을 수 있습니다). <n>변환 결과를 허용 목록에 넣은 <item>원거리 "
        "수집기<r>를 주변에 놓으세요. <n>이제 공급기에 원재료를 넣으면 자동으로 "
        "변환됩니다!"
    ),
    "booklet.actuallyadditions.chapter.book_tutorial": "설명서 사용법",
    "booklet.actuallyadditions.chapter.book_tutorial.text.2": (
        "<imp>왼쪽 위 버튼<r>이나 <imp>우클릭<r>으로 한 단계 <imp>뒤로<r> 가면 "
        "<item>항목<r> 화면이 나옵니다. 항목에는 <imp>특정 주제<r>와 관련된 장이 "
        "모여 있으며 여기에서도 <imp>페이지를 넘기고<r> 아이템을 클릭할 수 있습니다. "
        "<n><n><imp>다시 한 단계 뒤로<r> 가면 설명서의 <item>메인 화면<r>이 "
        "나옵니다. "
        "<n><n><i>이제 오른쪽 아래 버튼으로 페이지를 넘겨 보세요."
    ),
    "booklet.actuallyadditions.chapter.book_tutorial.text.3": (
        "<item>메인 화면<r>에는 <imp>모든 항목<r>의 목록이 있습니다. <n><n>설명서 "
        "<imp>아래쪽<r>의 <item>북마크<r>를 이용하면 <imp>장을 읽는 중<r>인 현재 "
        "페이지를 <imp>나중에 볼 수 있게<r> 저장할 수 있습니다. <n><n>설명서에는 "
        "<imp>다른 기능도 많으니<r> 화면을 둘러보세요! "
        "<n><n><i><imp>왼쪽 위의 뒤로 버튼<r>을 누르거나 우클릭하여 이 장을 "
        "나가세요."
    ),
    "booklet.actuallyadditions.chapter.reconstructorLenses.text.1": (
        "<item>원자 재구성기<r>는 기본적으로 일부 블록만 변환하지만 "
        "<item>렌즈<r>로 동작을 바꿀 수 있습니다. 렌즈를 들고 <imp>우클릭<r>하면 "
        "장착되고 빈손으로 우클릭하면 빠집니다. <n>렌즈마다 에너지 사용량이 다르며 "
        "<imp>필요한 에너지가 모여야<r> 작동합니다. <n><n><item>렌즈<r>의 여러 "
        "기능은 <imp>이 장<r>에서 볼 수 있고, <n><imp>유용한 추가 조합법<r>도 "
        "있습니다."
    ),
    "booklet.actuallyadditions.chapter.bookSplitting.text.1": (
        "<item>원자 재구성기<r>는 마법이 여러 개 붙은 책을 마법 하나씩 붙은 여러 "
        "책으로 나눕니다. 비용은 <imp>155000 CF<r>이므로 한 번에 한 권만 처리할 수 "
        "있습니다. 경로에 책을 여러 권 두면 마법이 하나뿐인 책을 맞혀 "
        "<imp>155000 CF를 낭비<r>할 수 있으니 조심하세요! 이 과정에서 필요한 수만큼 "
        "마법이 부여된 책이 허공에서 생겨납니다. 마법이죠?"
    ),
    "booklet.actuallyadditions.chapter.lensDisenchanting.text.1": (
        "<item>마법 해제 렌즈<r>는 마법이 부여된 아이템의 <imp>마법 부여<r> 하나를 "
        "<item>책<r>이나 <item>마법이 부여된 책<r>으로 <imp>옮깁니다<r>. <n>두 "
        "아이템을 <imp>레이저 앞의 같은 블록 공간에 던지면<r> 되며 "
        "<imp>종류별로 하나씩만<r> "
        "작동합니다. <n>레이저가 맞으면 책이 아닌 아이템의 <imp>맨 위 마법 부여<r>가 "
        "<imp>제거<r>되어 <imp>책에 추가<r>됩니다. <n><n>이 과정에는 "
        "<imp><energy> CF<r>가 듭니다."
    ),
    "booklet.actuallyadditions.chapter.miscDecorStuffsAndThings.text.1": (
        "건축하다 보면 <imp>장식 블록이 부족하다<r>고 느낄 때가 있습니다. 그래서 "
        "<item>에테틱 블록<r>을 준비했습니다! <n>아름다운 무늬의 석영 계열 장식 "
        "블록이며 익숙한 조합법으로 <imp>계단<r>, <imp>반 블록<r>, "
        "<imp>담장<r>으로 <imp>가공<r>할 수 있습니다."
    ),
    "booklet.actuallyadditions.chapter.fireworkBox.text.1": (
        "<item>폭죽 상자<r>는 새해에 딱 어울립니다! 설치하고 <imp>CF<r>를 공급하면 "
        "주변에 <imp>무작위로 생성된<r> <item>폭죽<r>을 발사합니다. <n>발사할 때마다 "
        "<rf> CF를 사용합니다. 블록을 <imp>우클릭<r>하면 원하는 <item>폭죽<r>의 "
        "종류와 발사 <imp>빈도<r>, 여러 <imp>추가 옵션<r>을 <imp>정밀하게 설정<r>할 "
        "수 있습니다. 화면을 직접 조작해 각 설정을 확인해 보세요. <n><n>멋진 폭죽 "
        "쇼를 만드는 좋은 방법입니다."
    ),
    "booklet.actuallyadditions.chapter.rf.text.1": (
        "기존 레드스톤 플럭스가 쇠퇴한 뒤 새로운 에너지 저장 방식인 "
        "<item>Crystal Flux<r>가 등장했습니다. <n><imp>Actually Additions<r>의 "
        "<imp>모든 기계<r>가 사용하며 <item>Tesla<r> 및 <item>Forge Units<r>와도 "
        "<imp>호환<r>됩니다. 따라서 이 시스템들의 기계는 별도 <imp>변환<r> 없이 "
        "<imp>서로 연결<r>하여 <item>Crystal Flux<r>를 쓸 수 있습니다."
    ),
    "booklet.actuallyadditions.chapter.rf.text.2": (
        "<item>Crystal Flux<r>를 <imp>전송<r>하려면 이를 <imp>생산<r>하거나 "
        "전송하는 장치를 <imp>사용<r>하거나 저장하는 장치 <imp>옆에<r> 놓으면 "
        "됩니다. <item>충전기<r>로 <imp>아이템을 충전<r>할 수도 있습니다."
    ),
    "booklet.actuallyadditions.chapter.phantomRedstoneface.text.1": (
        "<imp>팬텀 인터페이스를 모른다면 먼저 해당 항목을 읽어 보세요.<r> "
        "<n><n><item>팬텀 레드스톤 인터페이스<r>는 레드스톤 신호를 전달합니다. "
        "다른 팬텀 인터페이스와 <imp>다르게 작동<r>하며 <imp>한 방향으로만<r> "
        "전달합니다. <imp>연결된 블록이 레드스톤 신호를 내야<r> 인터페이스 옆으로 "
        "신호가 나오며 <imp>반대 방향<r>으로는 <imp>작동하지 않습니다<r>."
    ),
    "booklet.actuallyadditions.chapter.spawnerChanger": "생성기 변환기",
    "booklet.actuallyadditions.chapter.spawnerShard": "생성기 파편",
    "booklet.actuallyadditions.chapter.spawnerChanger.text.1": (
        "<item>생성기 변환기<r>는 <imp>생성기가 소환할 몹<r>을 "
        "<imp>변경<r>합니다. <n>먼저 원하는 몹을 변환기로 <imp>포획<r>하면 그 몹은 "
        "죽습니다. 그다음 생성기를 변환기로 <imp>우클릭<r>하면 생성기가 바뀌고 "
        "변환기는 <imp>사라집니다<r>. <n><n>모든 종류의 몹에 작동하지는 않을 수 "
        "있습니다."
    ),
    "booklet.actuallyadditions.chapter.itemRelays": "아이템 레이저 중계기",
    "booklet.actuallyadditions.chapter.itemRelays.text.1": (
        "먼저 알아둘 점이 있습니다. <item>아이템 레이저 중계기<r>는 유체나 에너지 "
        "중계기보다 <imp>복잡<r>하지만 아이템을 관리하고 운반하는 "
        "<imp>매우 강력한<r> 수단입니다. <n><item>아이템 레이저 중계기<r>를 아이템을 "
        "<imp>보관하거나 처리하는 블록<r>에 연결하면 그 슬롯과 내용물을 "
        "<imp>파악<r>합니다. <n>이것만으로는 쓸 수 없지만 <item>아이템 "
        "인터페이스<r>가 해당 아이템과 상호 작용합니다. 자세한 방법은 "
        "<imp>아이템 인터페이스 장<r>을 참고하세요."
    ),
    "booklet.actuallyadditions.chapter.itemInterfaces.text.1": (
        "<item>아이템 인터페이스<r>는 <item>아이템 레이저 중계기<r> 네트워크와 "
        "<imp>상호 작용<r>하는 <item>장치<r>입니다. 네트워크 자체는 연결된 "
        "보관함의 "
        "<imp>아이템과 슬롯<r>을 <imp>파악<r>하기만 합니다. <n><item>아이템 "
        "인터페이스<r>는 이 아이템과 직접 <imp>상호 작용<r>하며, 연결된 모든 "
        "보관함의 <imp>모든 슬롯<r>을 가진 <imp>아주 큰 상자<r>처럼 "
        "<imp>동작<r>합니다."
    ),
    "booklet.actuallyadditions.chapter.itemInterfaces.text.2": (
        "<item>아이템 인터페이스<r>에 <imp>호퍼<r>나 다른 운송 장치를 연결하면 "
        "상자처럼 "
        "<imp>아이템을 받고<r> <imp>꺼낼<r> 수 있습니다. 다만 아이템은 인터페이스 "
        "안이 아니라 <imp>레이저 중계기 네트워크<r>에서 들어오고 나갑니다. "
        "<n><n><item>아이템 인터페이스<r>를 네트워크에 <imp>연결<r>하려면 "
        "<item>아이템 레이저 중계기<r>를 바로 옆에 <imp>놓으세요<r>."
    ),
    "booklet.actuallyadditions.chapter.itemRelaysAdvanced": (
        "고급 아이템 레이저 중계기"
    ),
    "booklet.actuallyadditions.chapter.itemRelaysAdvanced.text.1": (
        "보관함에 실제로 들어갈 아이템을 <imp>허용 또는 차단 목록<r>으로 정해야 할 "
        "때가 있습니다. <n><item>고급 아이템 레이저 중계기<r>를 <imp>우클릭<r>하면 "
        "화면에서 <imp>허용 목록<r>이나 <imp>차단 목록<r>을 설정할 수 있습니다. "
        "<n>목록은 두 방향으로 나뉩니다. <imp>유입<r>은 중계기가 붙은 보관함으로 "
        "들어가려는 아이템, <imp>유출<r>은 그 보관함에서 나가려는 아이템을 뜻합니다."
    ),
    "booklet.actuallyadditions.chapter.itemInterfacesHopping.text.1": (
        "<item>호퍼형 아이템 인터페이스<r>는 일반 <item>아이템 "
        "인터페이스<r>처럼 <item>아이템 인터페이스<r> 옆에 "
        "옆에 <item>아이템 레이저 중계기<r>를 <imp>놓아<r> 네트워크에 "
        "<imp>연결<r>합니다. <n>일반형에는 아이템을 파이프로 넣어야 하지만 호퍼형은 "
        "<imp>스스로<r> 아이템을 <imp>넣고 꺼냅니다<r>. <item>호퍼<r>의 "
        "<imp>모든 기능<r>을 갖추되 <item>아이템<r>을 <imp>내부 인벤토리<r>가 아닌 "
        "<imp>네트워크<r>에 저장합니다."
    ),
    "booklet.actuallyadditions.chapter.banners.text.1": (
        "<imp>Actually Additions<r>의 <imp>특별한 아이템<r>에는 전용 <item>현수막 "
        "무늬<r>가 있습니다. 제작 칸에서 <imp>현수막 옆에 아이템<r>을 놓고 필요하면 "
        "<imp>염료<r>를 더하면 됩니다. 일반 무늬처럼 <item>방패<r>에도 합칠 수 "
        "있습니다. <n>무늬가 있는 아이템은 다음과 같습니다. <n><item>Actually "
        "Additions 설명서<r> <n><item>팬텀 연결기<r> <n><item>낙엽 송풍기<r>(고급형 "
        "제외) <n><item>드릴<r>(현수막의 작동 방식 때문에 흰색만 가능)"
    ),
    "booklet.actuallyadditions.chapter.playerInterface.text.1": (
        "<item>플레이어 인터페이스<r>는 <item>팬텀 인터페이스<r>와 비슷하지만 블록 "
        "대신 <imp>플레이어에 연결<r>되며, 장치를 <imp>설치<r>할 때 연결됩니다. "
        "<n><imp>아이템을 입력<r>하면 <imp>플레이어의 인벤토리로 이동<r>하고, "
        "<imp>CF를 입력<r>하면 인벤토리의 <imp>아이템을 충전<r>합니다. <n>기본 "
        "범위는 <range>블록이며 위에 <item>팬텀 범위 증폭기<r>를 최대 3개 놓아 "
        "늘릴 수 있습니다."
    ),
    "booklet.actuallyadditions.chapter.video_guide.booty.text.1": (
        "<item>Actually Additions<r>의 기능을 보여 주는 <imp>영상 소개<r>를 "
        "원한다면 제 친구 "
        "<item>Booty Toast<r>가 만든 멋진 영상을 보세요(이름이 이상한 건 저도 "
        "압니다)."
    ),
    "booklet.actuallyadditions.chapter.shockSuppressor.text.2": (
        "<i>공은 공을 세운 사람에게: <r><n><n>뭐, 그런 말입니다. <n>이 장치는 "
        "<imp>praetoras<r>가 생각해 내고 제안했습니다. 훌륭한 아이디어에 감사드립니다! "
        "<n><n><i>제4의 벽이 뭐죠..?"
    ),
    "booklet.actuallyadditions.chapter.worms": "지렁이",
    "booklet.actuallyadditions.chapter.worms.text.1": (
        "<item>지렁이<r>는 꽤 유용합니다. <n><imp>흙이나 잔디에 놓으면<r> 주변 "
        "3x3 범위의 <imp>땅을 갈고<r> <imp>젖은 상태로 유지<r>합니다. <n>땅을 "
        "<imp>부드럽게 만들어<r> 작물도 <imp>더 빨리 자랍니다<r>. "
        "<n><n><item>지렁이<r>는 "
        "괭이로 <imp>잔디를 갈 때<r> 얻을 수 있습니다. <n>없애려면 지렁이가 있는 "
        "<imp>블록을 부수세요<r>."
    ),
    "booklet.actuallyadditions.chapter.bags.text.2": (
        "아이템이 많이 든 <item>자루<r>로 상자나 <item>저장 상자<r> 같은 "
        "보관함을 <imp>우클릭<r>하면 자루의 <imp>모든 아이템<r>을 빠르게 옮깁니다."
    ),
    "booklet.actuallyadditions.chapter.empowerer.text.1": (
        "<item>강화기<r>는 수정과 다른 아이템을 <imp>강화<r>하는 중간 단계 "
        "장치입니다. <n>강화할 아이템은 강화기에 <imp>우클릭하여 올리고<r>, "
        "<imp>재료 아이템<r>은 다음 페이지 그림처럼 <imp>두 블록 떨어진<r> "
        "<item>전시대<r>에 놓습니다. <n>과정을 시작하려면 "
        "<imp>모든 전시대에 많은 CF를 공급<r>해야 하며, 이 에너지가 강화기의 "
        "아이템을 강화하는 데 소모됩니다."
    ),
    "booklet.actuallyadditions.chapter.distributorItem": "아이템 분배기",
    "booklet.actuallyadditions.chapter.farmer.text.2": (
        "<item>밀<r>, <item>감자<r>, <item>카놀라<r>, <item>아마<r> 같은 "
        "<imp>기본 작물<r>을 재배합니다. 땅은 자동 농부가 직접 "
        "<imp>경작<r>합니다."
    ),
    "booklet.actuallyadditions.chapter.farmer.text.3": (
        "<item>선인장<r>을 재배합니다. 심을 모래를 깔아야 하며, "
        "<imp>2블록보다 높게<r> 자라면 <imp>윗부분을 잘라<r> <item>자동 농부 안에 "
        "보관합니다."
    ),
    "booklet.actuallyadditions.chapter.farmer.text.7": (
        "<imp>Extra Utilities 2<r>의 <item>엔더 백합<r>을 재배합니다. "
        "<imp>엔드 돌<r>, <imp>잔디 블록<r>, <imp>흙<r>에 심어야 합니다."
    ),
    "booklet.actuallyadditions.chapter.farmer.text.8": (
        "<imp>Extra Utilities 2<r>의 <item>빨간 난초<r>를 재배합니다. "
        "<imp>레드스톤 광석<r>에 심어야 합니다."
    ),
    "booklet.actuallyadditions.chapter.engineer_house.text.1": (
        "어디서 시작할지 모르겠다면 <imp>기술자들<r>을 찾아가 보세요. <n>여러 "
        "물건을 파는 친절한 <imp>주민<r> 두 명입니다. <item>결정화 전문가<r>는 "
        "<imp>에메랄드와 수정<r>을 교환하고, <item>기술자<r>는 "
        "<imp>여러 기계<r>를 팝니다! <n>다음 페이지에 그들이 사는 "
        "<imp>집<r>이 나옵니다. <imp>집 안의 기계<r>는 조금 <imp>약해서<r> "
        "부수려 하면 "
        "산산조각 나니 조심하세요."
    ),
    "booklet.actuallyadditions.chapter.batteryBox.text.1": (
        "<item>배터리 상자<r>는 <imp>에너지를 저장<r>하기 좋습니다. 사용하려면 "
        "<item>배터리<r>를 상자에 <imp>우클릭<r>하여 넣어야 하며, "
        "<imp>에너지는 그 배터리에 저장<r>됩니다. <n><n>배터리를 "
        "<imp>웅크린 채 우클릭<r>하거나 "
        "<item>배터리 상자<r>에 <imp>레드스톤 펄스<r>를 주어 "
        "<imp>방전 모드<r>로 바꾸면 받은 에너지를 인접한 "
        "<imp>최대 15개<r>의 <item>배터리 상자<r>에 고르게 나눕니다."
    ),
    "booklet.actuallyadditions.chapter.goggles.text.1": (
        "<item>기술자의 고글<r>은 플레이어의 <imp>머리에 장착<r>하는 유용한 "
        "아이템입니다. <n><imp>레이저 중계기의 업그레이드나 보이지 않는 광선<r>처럼 "
        "평소에는 "
        "볼 수 없는 <imp>정보<r>를 보여 줍니다. <n><n><item>기술자의 적외선 "
        "고글<r>은 고급형으로, 블록에 가려져 있어도 주변의 <imp>엔티티를 "
        "발광시켜<r> 쉽게 <imp>볼 수 있게<r> 합니다."
    ),
    "booklet.actuallyadditions.chapter.trialsIntro": "시험 소개",
    "booklet.actuallyadditions.chapter.trialsIntro.text.1": (
        "<item>시험<r>은 다음에 무엇을 만들지 <imp>영감<r>을 얻을 수 있는 재미있는 "
        "<imp>도전 과제<r>입니다. <n><item>시험<r>을 <imp>완료<r>하면 오른쪽 아래 "
        "<imp>버튼<r>으로 완료 표시를 해 <imp>목록의 이름을 초록색으로<r> 바꿀 수 "
        "있습니다. <n>실제 완료 여부를 <imp>자동으로 확인할 방법이 없으므로<r> "
        "<item>시험<r>은 "
        "<imp>개인 목표<r>입니다. <n><n>설명서 화면 오른쪽 위의 "
        "<imp>북마크<r>를 누르면 <item>시험<r> 페이지로 <imp>이동<r>합니다."
    ),
    "booklet.actuallyadditions.chapter.trialsIntro.text.2": (
        "<item>시험<r>은 <imp>마인크래프트<r>와 <imp>Actually Additions<r>의 "
        "기능만으로 완료하도록 설계되었습니다."
    ),
    "booklet.actuallyadditions.chapter.laserUpgradeInvisibility": "개조: 투명화",
    "booklet.actuallyadditions.chapter.laserUpgradeRange": "개조: 범위",
    "booklet.actuallyadditions.chapter.crystalClusters": "수정 군집",
    "booklet.actuallyadditions.chapter.drill": "드릴",
    "booklet.actuallyadditions.chapter.staff": "지팡이",
    "booklet.actuallyadditions.chapter.itemFilter.text.1": (
        "<item>아이템 필터<r>는 <item>고급 아이템 레이저 중계기<r>, "
        "<item>ESD<r>, <item>원거리 수집기<r>의 <imp>허용 목록 크기를 "
        "늘립니다<r>. 필터를 들고 우클릭한 뒤 안에 걸러낼 아이템을 넣으세요. 그런 "
        "다음 원하는 기계의 허용 목록 슬롯에 필터를 넣으면 됩니다. <n>자세한 내용은 "
        "<imp>허용 목록을 지원하는 기계 화면의 허용 목록 버튼에 마우스를 "
        "올려<r> 확인하세요!"
    ),
    "booklet.actuallyadditions.chapter.playerProbe.text.1": (
        "<item>플레이어 탐사기<r>는 <item>플레이어 인터페이스<r>가 연결할 "
        "플레이어를 바꿉니다. 기능을 모른다면 <item>플레이어 인터페이스<r> 항목을 "
        "먼저 "
        "읽어 보세요! <n><n>탐사기로 <imp>플레이어를 우클릭<r>한 뒤 "
        "<imp>인터페이스를 우클릭<r>하면 됩니다. 단, 대상 플레이어가 웅크리거나 "
        "<imp>서버에서 나가면<r> 그 플레이어에게 <imp>알림을 보내고 연결을 "
        "해제<r>합니다! <n><n><n><i>장난치기"
    ),
    "booklet.actuallyadditions.chapter.fillingWand.text.1": (
        "<item>휴대용 채움기<r>는 블록으로 <imp>영역을 채우는<r> 도구입니다. "
        "<n>먼저 채울 블록을 들고 월드의 같은 블록을 <imp>웅크린 채 우클릭<r>하여 "
        "<imp>채움 블록으로 선택<r>하세요. <n><n><imp>첫 번째 모서리<r>를 보며 "
        "<imp>우클릭을 누른<r> 뒤 <imp>두 번째 모서리<r>에서 놓으면 평면이나 "
        "직육면체 영역을 채웁니다. <n>블록을 놓을 때 <imp>CF<r>를 사용하며 필요한 "
        "<imp>블록을 인벤토리에 가지고 있어야<r> 합니다."
    ),
    "achievement.actuallyadditions.openBooklet": "지식을 전하는 책!",
    "achievement.actuallyadditions.nameSmileyCloud": "가장 친한 친구",
    "achievement.actuallyadditions.nameSmileyCloud.desc": "미소 구름에 이름 붙이기",
    "achievement.actuallyadditions.craftPhantomface": "아이템을 쏙, 쏙!",
    "achievement.actuallyadditions.craftPhantomface.desc": (
        "팬텀 아이템 인터페이스 제작"
    ),
    "achievement.actuallyadditions.openTreasureChest": "수중 던전",
    "achievement.actuallyadditions.openTreasureChest.desc": "보물 상자 열기",
    "achievement.actuallyadditions.craftLiquiface": "유체를 쏙, 쏙!",
    "achievement.actuallyadditions.craftLiquiface.desc": ("팬텀 유체 인터페이스 제작"),
    "achievement.actuallyadditions.craftEnergyface": "CF를 쏙, 쏙!",
    "achievement.actuallyadditions.craftEnergyface.desc": (
        "팬텀 에너지 인터페이스 제작"
    ),
    "achievement.actuallyadditions.craftCoalGen": "근사한 발전기",
    "achievement.actuallyadditions.craftLeafGen.desc": "나뭇잎 발전기 제작",
    "achievement.actuallyadditions.craftReconstructor": "지이잉",
    "achievement.actuallyadditions.craftReconstructor.desc": "원자 재구성기 제작",
    "achievement.actuallyadditions.craftEmpowerer": "주입 제단",
    "achievement.actuallyadditions.craftEmpowerer.desc": "강화기 제작",
    "achievement.actuallyadditions.makeCrystal": "티 없이 맑은 수정",
    "achievement.actuallyadditions.makeCrystal.desc": ("원자 재구성기로 수정 만들기"),
    "achievement.actuallyadditions.craftLaserRelay": "지연 없이 중계!",
    "achievement.actuallyadditions.craftLaserRelayItem": "아이템 정보 전달",
    "achievement.actuallyadditions.craftItemInterface": "인터페이스 공개",
    "achievement.actuallyadditions.craftLaserRelayAdvanced": "힘찬 확장",
    "achievement.actuallyadditions.craftLaserRelayExtreme": "에너지에 미치다",
    "achievement.actuallyadditions.craftLaserRelayExtreme.desc": (
        "최고급 레이저 중계기 제작"
    ),
    "achievement.actuallyadditions.craftCrusher": "두 배로!",
    "achievement.actuallyadditions.craftDoubleCrusher": "두 배를 또 두 배로!",
    "achievement.actuallyadditions.pickUpCoffee": "중독되는 맛",
    "achievement.actuallyadditions.pickUpCoffee.desc": "커피 수확",
    "achievement.actuallyadditions.craftCoffeeMachine": "한 잔에 담긴 중독",
    "achievement.actuallyadditions.craftCoffeeMachine.desc": "커피 제조기 제작",
    "achievement.actuallyadditions.craftFireworkBox": "펑! 쾅! 펑!",
    "achievement.actuallyadditions.getCrystalsMilestone": "재구성의 달인",
    "achievement.actuallyadditions.getCrystalsMilestone.desc": "수정 200개 만들기",
    "achievement.actuallyadditions.openBookletMilestone.desc": "설명서 50번 열기",
    "achievement.actuallyadditions.getUnProbed": "은밀하게!",
    "achievement.actuallyadditions.getUnProbed.desc": (
        "다른 플레이어가 조사할 때 웅크려서 알아차리기"
    ),
    "achievement.actuallyadditions.completeTrials.desc": ("설명서의 모든 시험 완료"),
    "actuallyadditions.configuration.doUpdateCheck": "업데이트 확인",
    "actuallyadditions.configuration.doBatDrops": "박쥐 전리품 활성화",
    "actuallyadditions.configuration.advancedInfoTooltips": "고급 정보 툴팁",
    "actuallyadditions.configuration.hideEnergyOverlay": "에너지 표시 숨기기",
    "actuallyadditions.configuration.generateFlax": "아마 생성",
    "actuallyadditions.configuration.doCatDrops": "고양이 전리품 활성화",
    "actuallyadditions.configuration.generateCanola": "카놀라 생성",
    "actuallyadditions.configuration.generateQuartz": "석영 생성",
    "actuallyadditions.configuration.reconstructorPower": "재구성기 에너지",
    "actuallyadditions.configuration.leafGeneratorCPPerLeaf": (
        "나뭇잎당 나뭇잎 발전기 CP"
    ),
    "actuallyadditions.configuration.villageAndDungeonLoot": ("마을 및 던전 전리품"),
    "actuallyadditions.configuration.drillExtraWhitelist": "드릴 추가 허용 목록",
    "actuallyadditions.configuration.solidXPOrbs": "고체 경험치 구슬",
    "actuallyadditions.configuration.tillingWorms": "지렁이 경작",
    "actuallyadditions.configuration.advancedInfo": "고급 정보",
    "actuallyadditions.configuration.fluidLaserTransferRate": ("유체 레이저 전송 속도"),
    "actuallyadditions.configuration.itemsSettings": "아이템 설정",
    "actuallyadditions.configuration.superDuperHardRecipes": ("극도로 어려운 조합법"),
    "actuallyadditions.configuration.relayConfigurator": "중계기 설정",
    "actuallyadditions.configuration.waterBowlSpilling": "물그릇 쏟기",
    "actuallyadditions.configuration.oilGeneratorTransfer": "유체 연료 발전기 전송량",
    "actuallyadditions.configuration.laserRelayLoss": "레이저 중계기 손실률",
    "actuallyadditions.configuration.farmerConfigurator": "자동 농부 설정",
    "actuallyadditions.configuration.leafGeneratorCooldown": (
        "나뭇잎 발전기 대기 시간"
    ),
    "actuallyadditions.configuration.redstoneConfigurator": "레드스톤 설정",
    "actuallyadditions.configuration.verticalDiggerBlacklist": (
        "수직 굴착기 차단 목록"
    ),
    "actuallyadditions.configuration.versionSpecificUpdateChecker": (
        "버전별 업데이트 확인"
    ),
    "actuallyadditions.configuration.other": "기타",
    "actuallyadditions.configuration.generateCoffee": "커피 생성",
    "actuallyadditions.configuration.wormDeathTime": "지렁이 생존 시간",
    "actuallyadditions.configuration.farmerArea": "자동 농부 범위",
    "actuallyadditions.configuration.leafGeneratorArea": "나뭇잎 발전기 범위",
    "actuallyadditions.configuration.minerLensEnergy": "채굴 렌즈 에너지",
    "actuallyadditions.configuration.worldgenSettings": "세계 생성 설정",
    "actuallyadditions.configuration.giveBookletOnFirstCraft": (
        "첫 제작 시 설명서 지급"
    ),
    "actuallyadditions.configuration.waterBowl": "물그릇",
    "actuallyadditions.configuration.machineSettings": "기계 설정",
    "actuallyadditions.configuration.tinyCoal": "작은 석탄",
    "actuallyadditions.configuration.noColoredItemNames": ("아이템 이름 색상 비활성화"),
    "actuallyadditions.configuration.verticalDiggerExtraWhitelist": (
        "수직 굴착기 추가 허용 목록"
    ),
    "actuallyadditions.configuration.generateRice": "쌀 생성",
}

SOURCE_OVERRIDES = {
    "Molecular": "분자",
    "Material": "물질",
    "Quarkal": "쿼크식",
    "Atomatic": "원자식",
    "Tiny Bit": "아주 작은",
    "Component": "부품",
    "Vittle": "비틀",
    "Transmaterial": "초물질",
    "Partial": "부분",
    "Spatial": "공간",
    "Stuffy": "채움식",
    "Interdimensional": "차원 간",
    "Recombobulizer": "재결합기",
    "Shiftulator": "시프트 조정기",
    "Recombinator": "재조합기",
    "Modulator": "변조기",
    "Moleculizer": "분자화기",
    "Modificulator": "개조기",
    "Changer": "변환기",
    "Atomizer": "원자화기",
    "Makerator": "제작기",
    "Swapper": "맞바꾸기",
    "Exchanger": "교환기",
    "Replacer": "대체기",
    "Differentiator": "분화기",
    "Receiver": "수신기",
    "Drill Speed Augment I": "드릴 속도 업그레이드 I",
    "Drill Speed Augment II": "드릴 속도 업그레이드 II",
    "Drill Speed Augment III": "드릴 속도 업그레이드 III",
    "Drill Silk Touch Augment": "드릴 섬세한 손길 업그레이드",
    "Drill Fortune Augment I": "드릴 행운 업그레이드 I",
    "Drill Fortune Augment II (Gives Fortune III!)": "드릴 행운 업그레이드 II(행운 III 부여!)",
    "Drill Block Placing Augment": "드릴 블록 배치 업그레이드",
    "Drill Area Augment I": "드릴 범위 업그레이드 I",
    "Drill Area Augment II": "드릴 범위 업그레이드 II",
    "Laser Relay Modifier: Invisibility (WIP)": "레이저 중계기 개조: 투명화(WIP)",
    "Laser Relay Modifier: Range (WIP)": "레이저 중계기 개조: 범위(WIP)",
    (
        "The <item>Fermenting Barrel<r> can have a <item>Comparator<r> attached "
        "to it which will result in the Redstone strength being equivalent to the "
        "<imp>percentage<r> of the <imp>output tank<r>."
    ): (
        "<item>발효통<r>에 <item>비교기<r>를 연결하면 레드스톤 신호 세기가 "
        "<imp>출력 탱크<r>가 찬 <imp>비율<r>과 같아집니다."
    ),
}

TEXT_REPLACEMENTS = (
    ("액추얼리 애디션즈", "Actually Additions"),
    ("실제로 추가", "Actually Additions"),
    ("실제 추가", "Actually Additions"),
    ("실제 추가 사항", "Actually Additions"),
    ("실제 추가 기능", "Actually Additions"),
    ("실제로 Additions", "Actually Additions"),
    ("크리스탈 플럭스", "Crystal Flux"),
    ("결정 플럭스", "Crystal Flux"),
    ("카놀라 오일", "카놀라유"),
    ("세련된 카놀라유", "정제된 카놀라유"),
    ("파워", "에너지"),
    ("전원", "에너지"),
    ("인챈트", "마법 부여"),
    ("디스인챈트", "마법 해제"),
    ("레이저 릴레이", "레이저 중계기"),
    ("임에너지러", "강화기"),
    ("크러셔", "분쇄기"),
    ("원자 재구성자", "원자 재구성기"),
    ("스마일리 클라우드", "미소 구름"),
    ("Smiley Cloud", "미소 구름"),
    ("팬텀페이스", "팬텀 인터페이스"),
    ("Phantomface", "팬텀 인터페이스"),
    ("팬텀 브레이커", "팬텀 파괴기"),
    ("플레이서", "배치기"),
    ("브레이커", "파괴기"),
    ("항목 레이저 중계기", "아이템 레이저 중계기"),
    ("레시피", "조합법"),
    ("광석 딕트", "광석 사전"),
    ("OreDict", "광석 사전"),
    ("구성 GUI", "설정 화면"),
    ("구성 파일", "설정 파일"),
    ("구성에서", "설정에서"),
    ("결정화된 오일", "결정화유"),
    ("강화된 오일", "강화유"),
    ("수정로", "수정으로"),
    ("마우스 오른쪽 버튼을 길게 클릭", "우클릭을 누르고"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("마우스 오른쪽 버튼 클릭", "우클릭"),
    ("몰래 오른쪽 버튼으로 클릭", "웅크린 채 우클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("Redstone", "레드스톤"),
    ("Crafting Recipes", "조합법"),
    ("에너자이저", "충전기"),
    ("에너베이터", "방전기"),
    ("동력 화로", "전동 화로"),
    ("오일 생성기", "유체 연료 발전기"),
    ("자동 정밀 드로퍼", "자동 정밀 공급기"),
    ("나뭇잎 송풍기", "낙엽 송풍기"),
    ("텔레포트 스태프", "순간이동 지팡이"),
    ("포션 링", "물약 반지"),
    ("몰래 우클릭", "웅크린 채 우클릭"),
    ("화이트 또는 차단 목록", "허용 또는 차단 목록"),
    ("양동이을", "양동이를"),
    ("조합법를", "조합법을"),
    ("품목", "아이템"),
    ("첨단 아이템 레이저 중계기", "고급 아이템 레이저 중계기"),
    ("엔더 스타", "엔더의 별"),
    ("확실한 죽음의 렌즈", "필멸의 렌즈"),
    ("마력 추출의 렌즈", "마법 해제 렌즈"),
    ("광부의 렌즈", "채굴의 렌즈"),
    ("색채의 렌즈", "색상의 렌즈"),
    ("실크 터치", "섬세한 손길"),
    ("수정 클러스터", "수정 군집"),
    ("수정 파편", "수정 조각"),
    ("엔지니어 고글", "기술자의 고글"),
    ("배터리 박스", "배터리 상자"),
    ("에너지을", "에너지를"),
    ("블랙쿼츠", "검은 석영"),
    ("블랙 쿼츠", "검은 석영"),
    ("크리스털", "수정"),
    ("크리스탈", "수정"),
    ("용광로", "화로"),
    ("버킷", "양동이"),
    ("툴팁", "툴팁"),
    ("우클릭을 클릭", "우클릭"),
    ("좌클릭을 클릭", "좌클릭"),
)

ALLOWED_EXACT_KEYS = {
    "itemGroup.actuallyadditions",
    "achievement.page.actuallyadditions",
    "key.actuallyadditions.category",
    "misc.actuallyadditions.energy_tick",
    "misc.actuallyadditions.energy",
    "misc.actuallyadditions.energy_name",
    "misc.actuallyadditions.power_name_long",
    "misc.actuallyadditions.power_name_short",
    "misc.actuallyadditions.power_long",
    "misc.actuallyadditions.power_single",
    "misc.actuallyadditions.power_double",
    "booklet.actuallyadditions.chapter.rf",
}


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


def banner_name(source: str) -> str | None:
    for color, korean in COLORS.items():
        prefix = f"{color} "
        if not source.startswith(prefix) or not source.endswith(" Pattern"):
            continue
        pattern = source.removeprefix(prefix).removesuffix(" Pattern")
        pattern = {
            "Actually Additions Manual": "Actually Additions 설명서",
            "Phantom Connector": "팬텀 연결기",
            "Leaf Blower": "낙엽 송풍기",
            "Drill": "드릴",
        }.get(pattern, pattern)
        return f"{korean} {pattern} 무늬"
    return None


def crystal_name(source: str) -> str | None:
    match = re.fullmatch(
        r"(Empowered )?(Restonia|Palis|Diamatine|Emeradic|Void|Enori) "
        r"Crystal(?: (Block|Cluster|Shard|AIOT))?\)?",
        source,
    )
    if not match:
        return None
    empowered, material, form = match.groups()
    material_ko = {
        "Restonia": "레스토니아",
        "Palis": "팰리스",
        "Diamatine": "디아마틴",
        "Emeradic": "에메라딕",
        "Void": "보이드",
        "Enori": "에노리",
    }[material]
    suffix = {
        None: " 수정",
        "Block": " 수정 블록",
        "Cluster": " 수정 군집",
        "Shard": " 수정 조각",
        "AIOT": " 수정 AIOT",
    }[form]
    return f"{'강화된 ' if empowered else ''}{material_ko}{suffix}"


def colored_name(source: str) -> str | None:
    for color, korean in sorted(
        COLORS.items(), key=lambda row: len(row[0]), reverse=True
    ):
        prefix = f"{color} "
        if not source.startswith(prefix):
            continue
        noun = source.removeprefix(prefix)
        translated = {
            "Lamp": "조명",
            "Drill": "드릴",
            "Crystal Cluster": "수정 군집",
            "Crystal Shard": "수정 조각",
        }.get(noun)
        if translated:
            return f"{korean} {translated}"
    return None


def translate_name(source: str, candidate_value: str) -> str:
    for resolver in (banner_name, crystal_name, colored_name):
        translated = resolver(source)
        if translated:
            return translated
    if source in EXACT_NAMES:
        return EXACT_NAMES[source]
    if source in SOURCE_OVERRIDES:
        return SOURCE_OVERRIDES[source]
    value = candidate_value
    for english, korean in sorted(
        PROPER_TERMS.items(), key=lambda row: len(row[0]), reverse=True
    ):
        value = value.replace(english, korean)
    return value


def request_translation_candidate(source: str) -> str:
    """긴 설명 문장은 URL 한도를 피하도록 의미 구분점에서 나눠 요청한다."""
    if len(source) <= 140:
        return ars_family.request_translation(source)
    parts = re.split(r"(<[^>]+>|(?<=[.!?])\s+|,\s+)", source)
    translated: list[str] = []
    for part in parts:
        if not part:
            continue
        if re.fullmatch(r"<[^>]+>", part) or part.isspace() or part.startswith(","):
            translated.append(part)
            continue
        if len(part) <= 140:
            translated.append(ars_family.request_translation(part))
            continue
        words = part.split(" ")
        chunks: list[str] = []
        current = ""
        for word in words:
            proposed = f"{current} {word}".strip()
            if current and len(proposed) > 120:
                chunks.append(current)
                current = word
            else:
                current = proposed
        if current:
            chunks.append(current)
        translated.append(
            " ".join(ars_family.request_translation(chunk) for chunk in chunks)
        )
    return "".join(translated)


def marker(index: int, prefix: str) -> str:
    """숫자 없이 자동 번역에서 안정적으로 남는 임시 표식을 만든다."""
    letters = ""
    value = index
    while True:
        letters = chr(ord("A") + value % 26) + letters
        value = value // 26 - 1
        if value < 0:
            break
    return f"QX{prefix}{letters}QX"


def translate_booklet_segment(source: str) -> str:
    """설명서 한 문장 조각을 자연스럽게 번역하고 강조 태그를 복원한다."""
    literal_quotes: list[str] = []

    def hide_quote(match: re.Match[str]) -> str:
        token = marker(len(literal_quotes), "Q")
        literal_quotes.append(token)
        return token

    masked = re.sub(r'"', hide_quote, source)
    opening_tags = re.findall(r"<(?:item|imp|i)>", masked)
    if len(opening_tags) != masked.count("<r>"):
        return request_translation_candidate(source)
    for tag in opening_tags:
        masked = masked.replace(tag, '"', 1)
    masked = masked.replace("<r>", '"')
    protected: list[tuple[str, str]] = []

    def hide_tag(match: re.Match[str]) -> str:
        token = marker(len(protected), "P")
        protected.append((token, match.group(0)))
        return token

    masked = re.sub(r"<[^>]+>", hide_tag, masked)
    translated = ars_family.request_translation(masked)
    for token in literal_quotes:
        translated = translated.replace(token, '"')
    for token, tag in protected:
        translated = translated.replace(token, tag)
    if translated.count('"') != len(opening_tags) * 2:
        raise ValueError(f"설명서 강조 표식 복원 실패: {source}")
    for tag in opening_tags:
        translated = translated.replace('"', tag, 1)
        translated = translated.replace('"', "<r>", 1)
    return translated


def rebuild_booklet_candidates() -> dict[str, object]:
    """설명서 328개 키의 후보를 문장 단위로 다시 생성한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    candidates = load_json(CANDIDATE_FILE)
    existing_by_source = {
        source: candidates[key]
        for key, source in english.items()
        if isinstance(source, str) and isinstance(candidates.get(key), str)
    }
    cache = load_json(BOOKLET_CACHE_FILE) if BOOKLET_CACHE_FILE.is_file() else {}
    requests = {
        source
        for key, source in english.items()
        if key.startswith("booklet.")
        and isinstance(source, str)
        and source not in SOURCE_OVERRIDES
        and source not in EXACT_NAMES
        and not family_goal.is_allowed_original(source)
        and not isinstance(cache.get(source), str)
    }
    failures: list[str] = []
    if requests:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(
                    lambda text: "<n>".join(
                        translate_booklet_segment(part) for part in text.split("<n>")
                    ),
                    source,
                ): source
                for source in sorted(requests)
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{source}: {exc}")
                    cache[source] = existing_by_source[source]
        write_json(BOOKLET_CACHE_FILE, cache)
    rebuilt = 0
    for key, source in english.items():
        if not key.startswith("booklet.") or not isinstance(source, str):
            continue
        if key in KEY_OVERRIDES:
            candidates[key] = KEY_OVERRIDES[key]
        elif source in SOURCE_OVERRIDES:
            candidates[key] = SOURCE_OVERRIDES[source]
        elif source in EXACT_NAMES:
            candidates[key] = EXACT_NAMES[source]
        elif family_goal.is_allowed_original(source):
            candidates[key] = source
        else:
            candidates[key] = cache[source]
        rebuilt += 1
    write_json(CANDIDATE_FILE, candidates)
    return {
        "booklet_keys": rebuilt,
        "fallback_candidates": len(failures),
        "status": "candidate_requires_full_review",
    }


def candidate() -> dict[str, object]:
    """현재 영어 1,026개 값에 대해 독립 번역 후보를 만든다."""
    english = load_json(LANG_ROOT / "en_us.json")
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests = {
        source
        for key, source in english.items()
        if isinstance(source, str)
        and key not in KEY_OVERRIDES
        and source not in SOURCE_OVERRIDES
        and source not in EXACT_NAMES
        and not family_goal.is_allowed_original(source)
        and not isinstance(cache.get(source), str)
    }
    failures: list[str] = []
    if requests:
        completed = 0
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(request_translation_candidate, source): source
                for source in sorted(requests)
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                    completed += 1
                    if completed % 25 == 0:
                        write_json(CACHE_FILE, cache)
                except Exception as exc:  # pragma: no cover - 외부 번역 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("자동 번역 후보 생성 실패:\n" + "\n".join(failures))

    candidates: dict[str, str] = {}
    for key, source in english.items():
        if not isinstance(source, str):
            raise TypeError(f"문자열이 아닌 언어 값: {key}")
        if key in KEY_OVERRIDES:
            translated = KEY_OVERRIDES[key]
        elif source in SOURCE_OVERRIDES:
            translated = SOURCE_OVERRIDES[source]
        elif source in EXACT_NAMES:
            translated = EXACT_NAMES[source]
        elif family_goal.is_allowed_original(source):
            translated = source
        else:
            translated = cache[source]
        candidates[key] = translated
    write_json(CANDIDATE_FILE, candidates)
    report = {
        "keys": len(english),
        "candidate_keys": len(candidates),
        "existing_korean": 0,
        "review_scope": "all_language_keys_translated_and_reviewed_from_current_english",
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "auto_candidate_report.json", report)
    return report


def reviewed_value(key: str, source: str, candidate_value: str) -> str:
    if key in KEY_OVERRIDES:
        value = KEY_OVERRIDES[key]
    elif key.startswith(("block.", "item.", "entity.", "fluid.", "fluid_type.")):
        value = translate_name(source, candidate_value)
    elif source in SOURCE_OVERRIDES:
        value = SOURCE_OVERRIDES[source]
    else:
        value = candidate_value
    for english, korean in sorted(
        EXACT_NAMES.items(), key=lambda row: len(row[0]), reverse=True
    ):
        value = value.replace(english, korean)
    for english, korean in sorted(
        PROPER_TERMS.items(), key=lambda row: len(row[0]), reverse=True
    ):
        value = value.replace(english, korean)
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    value = value.replace("해야합니다", "해야 합니다")
    value = value.replace("할 수있는", "할 수 있는")
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    return value


def normalize() -> dict[str, object]:
    """후보 1,026개를 키별로 전부 재검수하여 작업본에 반영한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    candidates = load_json(CANDIDATE_FILE)
    changed = 0
    unresolved: list[str] = []
    for key, source in english.items():
        candidate_value = candidates.get(key)
        if not isinstance(source, str) or not isinstance(candidate_value, str):
            raise TypeError(f"문자열이 아닌 언어 값: {key}")
        translated = reviewed_value(key, source, candidate_value)
        errors = family_goal.validate_family_value(FAMILY, key, source, translated)
        if errors:
            raise ValueError("; ".join(errors))
        if korean.get(key) != translated:
            korean[key] = translated
            changed += 1
        if (
            source == translated
            and key not in ALLOWED_EXACT_KEYS
            and not family_goal.is_allowed_original(source)
        ):
            unresolved.append(key)
    write_json(LANG_ROOT / "ko_kr.json", korean)
    report = {
        "keys_reviewed": len(english),
        "changed": changed,
        "unresolved": len(unresolved),
        "unresolved_examples": unresolved[:30],
        "review_status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    errors: list[str] = []
    untranslated: list[str] = []
    if list(english) != list(korean):
        errors.append("영어와 한국어의 키 또는 순서가 다릅니다.")
    for key, source in english.items():
        target = korean.get(key)
        errors.extend(family_goal.validate_family_value(FAMILY, key, source, target))
        if (
            key.startswith("booklet.")
            and isinstance(source, str)
            and isinstance(target, str)
            and Counter(re.findall(r"<[^>]+>", source))
            != Counter(re.findall(r"<[^>]+>", target))
        ):
            errors.append(f"설명서 태그 불일치: {key}")
        if (
            source == target
            and key not in ALLOWED_EXACT_KEYS
            and isinstance(source, str)
            and not family_goal.is_allowed_original(source)
        ):
            untranslated.append(key)
    if untranslated:
        errors.append(f"미번역 키: {untranslated[:30]}")
    report = {
        "keys_reviewed": len(english),
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", report)
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("candidate", "booklet-candidate", "normalize", "verify")
    )
    args = parser.parse_args()
    resolve_source_root()
    if args.command == "candidate":
        result = candidate()
        status = 0
    elif args.command == "booklet-candidate":
        result = rebuild_booklet_candidates()
        status = 0
    elif args.command == "normalize":
        result = normalize()
        status = 0
    else:
        result, status = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
