#!/usr/bin/env python3
"""Just Dire Things 언어 파일 전체를 영어 원문 기준으로 번역하고 검증한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path

import ars_family
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root


FAMILY = "just_dire_things"
NAMESPACE = "justdirethings"
WORK_ROOT = PROJECT_ROOT / "working/just_dire_things"
LANG_ROOT = WORK_ROOT / NAMESPACE
CACHE_FILE = PROJECT_ROOT / "temp/just_dire_things_language_candidate_cache.json"
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"

PROPER_TERMS = {
    "Just Dire Things": "Just Dire Things",
    "Eclipse Alloy": "이클립스 합금",
    "Primal Coal": "프라이멀 석탄",
    "Blaze Ember": "블레이즈 엠버",
    "Voidflame Coal": "보이드플레임 석탄",
    "Eclipse Ember": "이클립스 엠버",
    "Primogel": "프라이모젤",
    "Blazebloom": "블레이즈블룸",
    "VoidShimmer": "보이드시머",
    "Shadowpulse": "섀도우펄스",
    "Ferricore": "페리코어",
    "Blazegold": "블레이즈골드",
    "Celestigem": "셀레스티젬",
}

ABILITY_NAMES = {
    "Air Burst": "공기 폭발",
    "Cauterize Wounds": "상처 지혈",
    "Death Protection": "죽음 방지",
    "Debuff Remover": "해로운 효과 제거",
    "Decoy": "미끼",
    "Drops Teleport": "전리품 순간이동",
    "Drops Teleporter": "전리품 순간이동",
    "Earthquake": "지진",
    "Eclipse Gate": "이클립스 게이트",
    "Elytra": "겉날개",
    "Yondu Arrow": "욘두 화살",
    "Extinguish": "소화",
    "Flight": "비행",
    "Mob X-Ray": "몹 엑스레이",
    "Ground Stomp": "지면 강타",
    "Hammer": "망치",
    "Homing Arrow": "유도 화살",
    "Instant Break": "즉시 파괴",
    "Invulnerability": "무적",
    "Jump Boost": "점프 강화",
    "Lava Immunity": "용암 면역",
    "Lava Repair": "용암 수리",
    "Lawnmower": "잔디깎기",
    "Leafbreaker": "나뭇잎 파괴",
    "Leaf Breaker": "나뭇잎 파괴",
    "Lingering": "잔류형",
    "Mind Fog": "정신 안개",
    "Mob Scanner": "몹 스캐너",
    "Negate Fall Damage": "낙하 피해 무효화",
    "Night Vision": "야간 투시",
    "Mental Obliteration": "정신 말살",
    "Ore Miner": "광석 채굴",
    "Ore Scanner": "광석 스캐너",
    "Ore X-Ray": "광석 엑스레이",
    "X-Ray": "엑스레이",
    "Phase": "위상 이동",
    "Random Polymorph": "무작위 변이",
    "Targeted Polymorph": "대상 지정 변이",
    "Potion Arrow": "물약 화살",
    "Run Speed": "달리기 속도",
    "Skysweeper": "낙하물 제거",
    "Sky Sweeper": "낙하물 제거",
    "Smelter": "제련",
    "Auto Smelter": "자동 제련",
    "Smoker": "훈연",
    "Auto Smoker": "자동 훈연",
    "Splash": "투척형",
    "Step Assist": "자동 오르기",
    "Stupefy": "망각",
    "Swim Speed": "수영 속도",
    "Time Protection": "시간 조작 방지",
    "Treefeller": "나무 벌목",
    "Tree Feller": "나무 벌목",
    "Void Shift": "보이드 시프트",
    "Walk Speed": "걷기 속도",
    "Water Breathing": "수중 호흡",
    "Blank": "빈",
}

EXACT_NAMES = {
    "Simple Block Breaker": "간단한 블록 파괴기",
    "Advanced Block Breaker": "고급 블록 파괴기",
    "Simple Block Placer": "간단한 블록 배치기",
    "Advanced Block Placer": "고급 블록 배치기",
    "Simple Swapper": "간단한 교환기",
    "Advanced Swapper": "고급 교환기",
    "Simple Clicker": "간단한 클릭기",
    "Advanced Clicker": "고급 클릭기",
    "Simple Dropper": "간단한 공급기",
    "Advanced Dropper": "고급 공급기",
    "Simple Fluid Collector": "간단한 유체 수집기",
    "Advanced Fluid Collector": "고급 유체 수집기",
    "Simple Fluid Placer": "간단한 유체 배치기",
    "Advanced Fluid Placer": "고급 유체 배치기",
    "Simple Fuel Generator": "간단한 유체 연료 발전기",
    "Simple Coal Generator": "간단한 석탄 발전기",
    "Simple Sensor": "간단한 센서",
    "Advanced Sensor": "고급 센서",
    "Eclipse Gate": "이클립스 게이트",
    "Energy Transmitter": "에너지 송신기",
    "Experience Holder": "경험치 저장기",
    "Inventory Holder": "인벤토리 저장기",
    "Item Collector": "아이템 수집기",
    "Paradox Machine": "패러독스 기계",
    "Player Accessor": "플레이어 접근기",
    "Creature Catcher": "생물 포획기",
    "Area Effect Cloud": "범위 효과 구름",
    "Dire Arrow": "다이어 화살",
    "Paradox": "패러독스",
    "DirePortal": "다이어 포털",
    "Portal Projectile": "포털 투사체",
    "Time Wand Entity": "시간 지팡이 엔티티",
    "Fluid Canister": "유체 캔",
    "Fuel Canister": "연료 캔",
    "Machine Settings Copier": "기계 설정 복사기",
    "Pocket Generator": "휴대용 발전기",
    "Polymorphic Catalyst": "다형성 촉매",
    "Polymorphic Wand": "다형성 지팡이",
    "Advanced Polymorphic Wand": "고급 다형성 지팡이",
    "Portal Fluid Catalyst": "포털 유체 촉매",
    "Portal Gun": "포털 건",
    "Advanced Portal Gun": "고급 포털 건",
    "Potion Canister": "물약 캔",
    "Time Crystal": "시간 수정",
    "Time Wand": "시간 지팡이",
    "Totem of Death Recall": "죽음 귀환의 토템",
    "Blazejet Wand": "블레이즈젯 지팡이",
    "Eclipsegate Wand": "이클립스 게이트 지팡이",
    "Voidshift Wand": "보이드 시프트 지팡이",
    "Ferricore Wrench": "페리코어 렌치",
}

NAME_PARTS = (
    ("Unstable Portal Fluid", "불안정한 포털 유체"),
    ("Polymorphic Fluid", "다형성 유체"),
    ("Unrefined ", "정제되지 않은 "),
    ("Blaze Ember Fuel", "블레이즈 엠버 연료"),
    ("Voidflame Fuel", "보이드플레임 연료"),
    ("Eclipse Ember Fuel", "이클립스 엠버 연료"),
    ("Portal Fluid", "포털 유체"),
    ("Time Fluid", "시간 유체"),
    ("XP Fluid", "경험치 유체"),
    ("Budding Time Crystal Block", "싹트는 시간 수정 블록"),
    ("Large Time Crystal Cluster", "대형 시간 수정 군집"),
    ("Medium Time Crystal Cluster", "중형 시간 수정 군집"),
    ("Small Time Crystal Cluster", "소형 시간 수정 군집"),
    ("Time Crystal Cluster", "시간 수정 군집"),
    ("Time Crystal Block", "시간 수정 블록"),
    ("Charcoal Block", "숯 블록"),
    ("Exhausted ", "고갈된 "),
    ("Raw ", "미가공 "),
    (" Block", " 블록"),
    (" Soil", " 토양"),
    (" Goo", " 구"),
    (" Fuel", " 연료"),
    (" Ore", " 광석"),
    (" Bucket", " 양동이"),
    (" Ingot", " 주괴"),
    (" Chestplate", " 흉갑"),
    (" Leggings", " 레깅스"),
    (" Helmet", " 투구"),
    (" Boots", " 부츠"),
    (" Pickaxe", " 곡괭이"),
    (" Shovel", " 삽"),
    (" Sword", " 검"),
    (" Axe", " 도끼"),
    (" Hoe", " 괭이"),
    (" Bow", " 활"),
    (" Paxel", " 팍셀"),
)

KEY_OVERRIDES = {
    "itemGroup.DeferredHolder{ResourceKey[minecraft:creative_mode_tab / justdirethings:justdirethings]}": (
        "Just Dire Things"
    ),
    "justdirethings.key.category": "Just Dire Things",
    "justdirethings.ability": "능력: %s - %s",
    "justdirethings.bound-key": "지정 키: %s",
    "justdirethings.bound-mouse": "마우스 버튼: %s",
    "justdirethings.boundside": " -연결된 면: ",
    "justdirethings.boundto": "연결 대상: %s:%s",
    "justdirethings.boundto-missing": "연결 대상(블록 없음): %s:%s",
    "justdirethings.festored": "에너지: %s / %s",
    "justdirethings.fillmode.jdtonly": "Just Dire Things만",
    "justdirethings.presshotkey": "<%s 누르기>",
    "justdirethings.screen.energy": "에너지: %s/%s FE",
    "justdirethings.screen.fepertick": "FE/t: %s",
    "justdirethings.screen.fluid": "%s: %s/%s mB",
    "justdirethings.screen.paradoxenergycost": "에너지 비용: %s FE",
    "justdirethings.screen.paradoxfluidcost": "유체 비용: %s mB",
    "justdirethings.timecrystaltooltip": "흐물흐물 흔들흔들",
    "justdirethings.timecrystaltooltiptwo": "시간이 꼬이고 또 꼬이고",
    "sound.justdirethings.beep": "삐",
    "sound.justdirethings.paradox_ambient": "패러독스 기계 작동음",
    "sound.justdirethings.portal_gun_close": "포털 건 닫힘",
    "sound.justdirethings.portal_gun_open": "포털 건 열림",
    "Block{justdirethings:gooblock_tier1}_dead": "고갈된 프라이모젤 구",
    "Block{justdirethings:gooblock_tier2}_dead": "고갈된 블레이즈블룸 구",
    "Block{justdirethings:gooblock_tier3}_dead": "고갈된 보이드시머 구",
    "Block{justdirethings:gooblock_tier4}_dead": "고갈된 섀도우펄스 구",
    "entity.justdirethings.decoy_entity": "미끼 엔티티",
    "justdirethings.ability.hammer_off": "망치: 비활성화",
    "item.justdirethings.raw_blazegold": "블레이즈골드 원석",
    "item.justdirethings.raw_eclipsealloy": "이클립스 합금 원석",
    "item.justdirethings.raw_ferricore": "페리코어 원석",
}

SOURCE_OVERRIDES = {
    "Launch yourself in the direction you're looking": "바라보는 방향으로 자신을 발사합니다",
    "Safer than Fireworks": "폭죽보다 안전합니다",
    "Binding Failed": "연결에 실패했습니다",
    "Binding Removed": "연결을 해제했습니다",
    "Activate to heal yourself": "활성화하면 자신을 회복합니다",
    "Feel the Burn!": "뜨거운 맛을 느껴 보세요!",
    "Creature: ": "생물: ",
    "Prevents death once every 5 minutes": "5분마다 한 번 죽음을 방지합니다",
    "Activate to Remove negative effects": "활성화하면 해로운 효과를 제거합니다",
    "Milk not included": "우유는 따로 준비하세요",
    "Decoy": "미끼",
    "Activate to summon a decoy that mobs will attack": "활성화하면 몹이 공격할 미끼를 소환합니다",
    "Disabled": "비활성화",
    "Bind tool to chest, and drops will teleport there": (
        "도구를 상자에 연결하면 전리품이 그곳으로 순간이동합니다"
    ),
    "My inventory is a mess -Dire Probably": "내 인벤토리는 엉망이야 -아마 Dire",
    "Slow all nearby mobs": "주변의 모든 몹을 느리게 합니다",
    "Temporarily remove blocks you click on": "클릭한 블록을 일시적으로 제거합니다",
    "I just missed the portable hole, ok?": "휴대용 구멍이 아쉬웠을 뿐이에요, 알겠죠?",
    "Built In Elytra": "겉날개가 내장됩니다",
    "Enabled": "활성화",
    "Arrows can hit multiple targets": "화살이 여러 대상을 공격할 수 있습니다",
    "I'm Mary Poppins Ya'll": "난 메리 포핀스라고!",
    "Removes Burning Effect": "불타는 효과를 제거합니다",
    "Fill Mode: ": "채움 모드: ",
    "All": "모두",
    "Fill Mode Set to: %s": "채움 모드 설정: %s",
    "None": "없음",
    "Creative mode style flight": "크리에이티브 모드 방식으로 비행합니다",
    "Amount: ": "양: ",
    "Fluid Drop Recipes": "유체 투입 제작법",
    "Fluid: ": "유체: ",
    "Cook time (ticks): %d": "조리 시간(틱): %d",
    "Stack Cook time (ticks): %d": "묶음 조리 시간(틱): %d",
    "Fuel Amount: %f": "연료량: %f",
    "Stack Fuel Amount: %f": "묶음 연료량: %f",
    "See all nearby mobs": "주변의 모든 몹을 표시합니다",
    "Goo Spreading Recipes": "구 확산 제작법",
    "Tagged Goo Spreading Recipes": "태그 기반 구 확산 제작법",
    "Activate to push mobs away": "활성화하면 몹을 밀어냅니다",
    "3x3, 5x5, or 7x7 depending on tool tier": (
        "도구 티어에 따라 3x3, 5x5 또는 7x7 영역을 채굴합니다"
    ),
    "Drop in Water": "물에 떨어뜨리세요",
    "Arrows seek their targets": "화살이 대상을 추적합니다",
    "Instantly break all blocks": "모든 블록을 즉시 파괴합니다",
    "Invalid Entity for Polymorphing": "변이시킬 수 없는 엔티티입니다",
    "Activate for a few seconds of invulnerability": "활성화하면 몇 초 동안 무적이 됩니다",
    "Bring it!!": "덤벼!!",
    "Jump Higher": "더 높이 점프합니다",
    "Toggle Tool Abilities": "도구 능력 전환",
    "Open Tool Settings UI": "도구 설정 화면 열기",
    "No Damage from Lava or Fire": "용암과 불로 피해를 받지 않습니다",
    "Fancy a swim?": "한번 헤엄쳐 볼까요?",
    "Drop item in Lava to repair it": "아이템을 용암에 떨어뜨려 수리합니다",
    "Harvest all nearby grass": "주변의 풀을 모두 수확합니다",
    "Clear nearby leaves": "주변의 나뭇잎을 제거합니다",
    "Seriously, who doesn't have fast leaf decay": "요즘 빠른 나뭇잎 소멸이 없는 사람이 있나요?",
    "Lingering effect on potions": "물약에 잔류형 효과를 부여합니다",
    "Insufficient Energy": "에너지가 부족합니다",
    "Insufficient Portal Fluid": "포털 유체가 부족합니다",
    "Insufficient Time Fluid": "시간 유체가 부족합니다",
    "Mobs are less likely to notice you": "몹이 플레이어를 감지하기 어려워집니다",
    " (Missing Upgrade)": " (업그레이드 없음)",
    "Show the location of nearby mobs": "주변 몹의 위치를 표시합니다",
    "Whats making THAT noise?!": "대체 무슨 소리가 나는 거죠?!",
    "No fall damage": "낙하 피해를 받지 않습니다",
    "Automatic Night Vision": "야간 투시가 자동으로 적용됩니다",
    "Nearby mobs completely stop. Forever.": "주변의 몹을 완전히, 영원히 멈춥니다.",
    "Auto Harvest connected ores": "연결된 광석을 자동으로 모두 채굴합니다",
    "Show the location of nearby ores": "주변 광석의 위치를 표시합니다",
    "Ores to Resources": "광석에서 자원으로",
    "See all nearby ores": "주변의 모든 광석을 표시합니다",
    "Thats Overpowered!!": "이건 너무 강력하잖아!!",
    "Paradox Energy: %s / %s": "패러독스 에너지: %s / %s",
    "Walk through walls": "벽을 통과해 이동합니다",
    "Burn Time: %f / %f": "연소 시간: %f / %f",
    "Fuel: %f %s": "연료: %f %s",
    "Fuel Empty": "연료 없음",
    "Polymorphic Fluid: %s / %s": "다형성 유체: %s / %s",
    "Polymorph Target: %s": "변이 대상: %s",
    "Portal Fluid: %s / %s": "포털 유체: %s / %s",
    "Insert a Potion Canister to apply effects to enemies": (
        "물약 캔을 넣으면 적에게 물약 효과를 적용합니다"
    ),
    "Like Vanilla, without inventory issues...": "바닐라 방식이지만 인벤토리 걱정은 없습니다...",
    "Click on the block with its food to activate it": (
        "해당 생물의 먹이를 든 채 블록을 클릭하면 활성화됩니다"
    ),
    "Run Faster": "더 빠르게 달립니다",
    "Hold Shift for details": "자세히 보려면 Shift를 누르세요",
    "Clear falling blocks above the one you break": "파괴한 블록 위의 낙하 블록을 제거합니다",
    "Oww my head!": "아야, 내 머리!",
    "Auto Smelt Block Drops": "블록 전리품을 자동으로 제련합니다",
    "Auto Smelt Mob Drops": "몹 전리품을 자동으로 훈연합니다",
    "Add splash effect to your potions": "물약에 투척형 효과를 추가합니다",
    "Automatically step up 1 block": "1블록 높이를 자동으로 올라갑니다",
    "Activate to make the targeted mob forget you": "활성화하면 대상 몹이 플레이어를 잊습니다",
    "Professor Lockhart would be proud": "록하트 교수님도 자랑스러워할 겁니다",
    "Swim Faster": "더 빠르게 헤엄칩니다",
    "Time Fluid: %s / %s": "시간 유체: %s / %s",
    "Protection from Time Altering Effects": "시간 조작 효과를 방지합니다",
    "Tool: %s - %s": "도구: %s - %s",
    "Chop down trees in 1 fell swoop": "나무 전체를 한 번에 벌목합니다",
    " -Not Bound": " -연결 안 됨",
    "Not Bound": "연결 안 됨",
    "Teleport to where you're looking": "바라보는 곳으로 순간이동합니다",
    "Walk Faster": "더 빠르게 걷습니다",
    "Allows player to breath under water": "물속에서 숨을 쉴 수 있습니다",
    "Just keep swimming, just keep swimming!": "계속 헤엄쳐요, 계속 헤엄쳐요!",
}

SCREEN_OVERRIDES = {
    "add_favorite": "즐겨찾기 추가",
    "allowlist": "허용 목록",
    "burn_time": "남은 연소 시간: %ss",
    "burnspeedmultiplier": "연소 속도 배수: %s",
    "cancel": "취소",
    "click-custom": "사용자 지정 입력",
    "click-hold": "클릭 유지",
    "click-hold-for": "클릭 유지 시간(틱)",
    "click-left": "좌클릭",
    "click-right": "우클릭",
    "collectexp": "경험치 수집",
    "comparecounts": "묶음 수량 비교",
    "comparenbt": "NBT 비교",
    "copy_area": "작동 영역 복사",
    "copy_filter": "필터 복사",
    "copy_offset": "위치 차이 복사",
    "copy_redstone": "레드스톤 설정 복사",
    "denylist": "차단 목록",
    "direction-down": "아래쪽",
    "direction-east": "동쪽",
    "direction-none": "없음",
    "direction-north": "북쪽",
    "direction-south": "남쪽",
    "direction-up": "위쪽",
    "direction-west": "서쪽",
    "dropcount": "배출 수량",
    "edit_favorite": "즐겨찾기 편집",
    "energy": "에너지: %s/%s FE",
    "energycost": "에너지 비용: %s",
    "entity-all": "모든 엔티티",
    "entity-none": "엔티티 없음",
    "equals": "같음",
    "fepertick": "FE/t: %s",
    "filter-block": "필터: 블록",
    "filter-item": "필터: 아이템",
    "filteronlytrue": "필터에 맞는 아이템만",
    "fluid": "%s: %s/%s mB",
    "greaterthan": "초과",
    "hiderender": "표시 숨기기",
    "high": "높음",
    "ignored": "무시",
    "inv-armor": "방어구 슬롯",
    "inv-normal": "인벤토리 슬롯",
    "inv-offhand": "보조 손 슬롯",
    "lessthan": "미만",
    "low": "낮음",
    "no_fuel": "연료 없음",
    "notrequireequipped": "인벤토리에서 활성화",
    "owneronly": "소유자만",
    "paradoxall": "블록과 엔티티 되돌리기",
    "paradoxblock": "블록 되돌리기",
    "paradoxenergycost": "에너지 비용: %s FE",
    "paradoxentity": "엔티티 되돌리기",
    "paradoxfluidcost": "유체 비용: %s mB",
    "pickupdelay": "줍기 지연 시간(틱)",
    "pullfluids": "유체 가져오기",
    "pullitems": "아이템 가져오기",
    "pulse": "펄스",
    "pushfluids": "유체 내보내기",
    "redstone-strong": "강한 신호",
    "redstone-weak": "약한 신호",
    "remove_favorite": "즐겨찾기 제거",
    "renderarea": "작동 영역 표시",
    "renderparadox": "패러독스 영역 표시",
    "requireequipped": "장착 중일 때 활성화",
    "respectpickupdelay": "아이템 줍기 지연 적용",
    "retrieveexp": "레벨 회수",
    "rightclicksettings": "우클릭하여 설정",
    "save_close": "저장 후 닫기",
    "senditems": "아이템 내보내기",
    "senseamount": "수량 감지",
    "setbinding": "연결 설정",
    "showfakeplayer": "가짜 플레이어 표시",
    "showparticles": "입자 표시",
    "showrender": "표시 보이기",
    "snapshotarea": "영역 스냅샷",
    "sneak-click": "웅크리고 클릭",
    "stay_open": "화면 유지",
    "storeexp": "레벨 저장",
    "swapitems": "아이템 교환",
    "target-adult": "성체 대상",
    "target-air": "공기 대상",
    "target-block": "블록 대상",
    "target-child": "새끼 대상",
    "targetexp": "목표 레벨",
    "target-hostile": "적대적 몹 대상",
    "target-item": "아이템 대상",
    "target-living": "모든 생명체 대상",
    "target-noblock": "블록 무시",
    "target-passive": "비적대적 몹 대상",
    "target-player": "플레이어 대상",
    "tickspeed": "속도(틱)",
}

ALLOWED_EXACT_KEYS = {
    "itemGroup.DeferredHolder{ResourceKey[minecraft:creative_mode_tab / justdirethings:justdirethings]}",
    "justdirethings.key.category",
}

TEXT_REPLACEMENTS = (
    ("저스트 다이어 띵스", "Just Dire Things"),
    ("오직 끔찍한 것들", "Just Dire Things"),
    ("다형성 액체", "다형성 유체"),
    ("차원문 액체", "포털 유체"),
    ("차원문 총", "포털 건"),
    ("경험 액체", "경험치 유체"),
    ("경험치 액체", "경험치 유체"),
    ("엑스피 유체", "경험치 유체"),
    ("전원", "에너지"),
    ("힘 비용", "에너지 비용"),
    ("상위 버전으로 변환", "업그레이드"),
    ("상위 버전 변환", "업그레이드"),
    ("업그레이드로 변환", "업그레이드"),
    ("사용 가능한 업그레이드", "적용 가능한 업그레이드"),
    ("유효한 업그레이드", "적용 가능한 업그레이드"),
    ("텔레포터 떨굼", "전리품 순간이동"),
    ("드롭 텔레포트", "전리품 순간이동"),
    ("광물 스캐너", "광석 스캐너"),
    ("하늘 청소부", "낙하물 제거"),
    ("잎 파괴기", "나뭇잎 파괴"),
    ("허수아비", "미끼"),
    ("진화", "소화"),
    ("용암 능력", "용암 수리"),
    ("포탈", "포털"),
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


def translate_name(source: str) -> str:
    if source in EXACT_NAMES:
        return EXACT_NAMES[source]
    if source.startswith("Template: "):
        return f"{translate_name(source.removeprefix('Template: '))} 형판"
    if source.startswith("Upgrade: "):
        ability = source.removeprefix("Upgrade: ")
        return f"{ABILITY_NAMES.get(ability, translate_name(ability))} 업그레이드"
    if source in ABILITY_NAMES:
        return ABILITY_NAMES[source]
    value = source
    for old, new in sorted(
        PROPER_TERMS.items(), key=lambda row: len(row[0]), reverse=True
    ):
        value = value.replace(old, new)
    for old, new in NAME_PARTS:
        value = value.replace(old, new)
    return value


def candidate() -> dict[str, object]:
    """모든 영어 값에 대해 독립 번역 후보를 만든다."""
    english = load_json(LANG_ROOT / "en_us.json")
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests = {
        source
        for key, source in english.items()
        if isinstance(source, str)
        and key not in KEY_OVERRIDES
        and not key.startswith(("block.", "item.", "entity.", "fluid_type."))
        and ".ability." not in key
        and not family_goal.is_allowed_original(source)
        and not isinstance(cache.get(source), str)
    }
    failures: list[str] = []
    if requests:
        completed = 0
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(ars_family.request_translation, source): source
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
        elif key.startswith("justdirethings.screen."):
            translated = SCREEN_OVERRIDES[key.removeprefix("justdirethings.screen.")]
        elif source in SOURCE_OVERRIDES:
            translated = SOURCE_OVERRIDES[source]
        elif key.startswith(("block.", "item.", "entity.", "fluid_type.")):
            translated = translate_name(source)
        elif ".ability." in key:
            translated = translate_name(source)
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
    elif key.startswith("justdirethings.screen."):
        value = SCREEN_OVERRIDES[key.removeprefix("justdirethings.screen.")]
    elif source in SOURCE_OVERRIDES:
        value = SOURCE_OVERRIDES[source]
    elif key.startswith(("block.", "item.", "entity.", "fluid_type.")):
        value = translate_name(source)
    elif ".ability." in key and not key.endswith((".detailtext", ".flavortext")):
        value = translate_name(source)
    else:
        value = candidate_value
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    for old, new in sorted(
        PROPER_TERMS.items(), key=lambda row: len(row[0]), reverse=True
    ):
        value = value.replace(old, new)
    for old, new in sorted(
        ABILITY_NAMES.items(), key=lambda row: len(row[0]), reverse=True
    ):
        value = value.replace(old, new)
    value = value.replace("간단한 교환자", "간단한 교환기")
    value = value.replace("고급 교환자", "고급 교환기")
    value = value.replace("채우기 모드", "채움 모드")
    value = value.replace("허용 목록", "허용 목록")
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    return value


def normalize() -> dict[str, object]:
    """후보 488개를 키별 규칙과 용어표로 전부 재검수하여 작업본에 반영한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    candidates = load_json(CANDIDATE_FILE)
    changed = 0
    unresolved: list[str] = []
    for key, source in english.items():
        if not isinstance(source, str) or not isinstance(candidates[key], str):
            raise TypeError(f"문자열이 아닌 언어 값: {key}")
        translated = reviewed_value(key, source, candidates[key])
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
        "review_status": "full_existing_korean_reviewed",
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
    parser.add_argument("command", choices=("candidate", "normalize", "verify"))
    args = parser.parse_args()
    resolve_source_root()
    if args.command == "candidate":
        result = candidate()
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
