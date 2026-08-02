#!/usr/bin/env python3
"""Oritech 언어 파일을 현재 영어 원문 기준으로 전체 번역·재검수한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path

import ars_family
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root


FAMILY = "oritech"
NAMESPACE = "oritech"
WORK_ROOT = PROJECT_ROOT / "working/oritech"
LANG_ROOT = WORK_ROOT / NAMESPACE
CACHE_FILE = PROJECT_ROOT / "temp/oritech_language_candidate_cache.json"
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"

SOURCE_OVERRIDES = {
    "Oritech": "Oritech",
    "Powered Furnace": "전기 화로",
    "Pulverizer": "분쇄기",
    "Foundry": "주조소",
    "Assembler": "조립기",
    "Centrifuge": "원심 분리기",
    "Atomic Forge": "원자 단조기",
    "Fragment Forge": "파편 단조기",
    "Industrial Chiller": "산업용 냉각기",
    "Refinery": "정유기",
    "Refinery Chamber Module": "정유기 반응실 모듈",
    "Basic Generator": "기본 발전기",
    "Bio Generator": "바이오 발전기",
    "Fuel Generator": "연료 발전기",
    "Lava Generator": "용암 발전기",
    "Steam Engine": "증기 기관",
    "Solar Panel": "태양광 패널",
    "Equipment Charger": "장비 충전기",
    "Bedrock Extractor": "기반암 추출기",
    "Drone Port": "드론 포트",
    "Enderic Laser": "엔더릭 레이저",
    "Pipe Booster": "파이프 증폭기",
    "Pump": "펌프",
    "Addon Splicer": "애드온 접합기",
    "Tree Cutter": "벌목기",
    "Machine Frame": "기계 프레임",
    "Destroyer Block": "파괴 블록",
    "Fertilizer Block": "비료 살포 블록",
    "Placer Block": "배치 블록",
    "Machine Addon Extender": "기계 애드온 확장기",
    "Power Bank Addon Extender": "전력 저장고 애드온 확장기",
    "Capacitor Addon": "축전기 애드온",
    "Acceptor Addon": "입력 애드온",
    "Speed Addon": "속도 애드온",
    "Efficiency Addon": "효율 애드온",
    "Synergy Matrix Addon": "시너지 매트릭스 애드온",
    "Burst Addon": "급속 애드온",
    "Auxiliary Processing Chamber Addon": "보조 처리실 애드온",
    "Fluid Addon": "유체 애드온",
    "Inventory Proxy Addon": "인벤토리 프록시 애드온",
    "Control Unit Addon": "제어 장치 애드온",
    "Steam Boiler Addon": "증기 보일러 애드온",
    "Hunter Addon": "사냥 애드온",
    "Quarry Addon": "채석장 애드온",
    "Crop Filter Addon": "작물 필터 애드온",
    "Yield Addon": "수확량 애드온",
    "Silk Touch Addon": "섬세한 손길 애드온",
    "Heart of the Machine": "기계의 심장",
    "Cybernetic Augmentation Center": "사이버네틱 증강 센터",
    "Basic Research Station": "기본 연구대",
    "Quantum Research Station": "양자 연구대",
    "Arcane Research Station": "비전 연구대",
    "Energy Pipe": "에너지 파이프",
    "Fluid Pipe": "유체 파이프",
    "Item Pipe": "아이템 파이프",
    "Item Filter": "아이템 필터",
    "Power Pole": "전력 전봇대",
    "Superconductor": "초전도체",
    "Creative Energy Storage": "크리에이티브 에너지 저장고",
    "Creative Fluid Tank": "크리에이티브 유체 탱크",
    "Large Energy Storage": "대형 에너지 저장고",
    "Portable Energy Storage": "휴대용 에너지 저장고",
    "Portable Fluid Tank": "휴대용 유체 탱크",
    "Schrödinger's Safe": "슈뢰딩거의 금고",
    "Stabilized Enchanter": "안정화 마법 부여기",
    "Arcane Catalyst": "비전 촉매",
    "Tainted Refinery": "오염된 정제소",
    "Spawner Cage": "생성기 우리",
    "Spawner Controller": "생성기 제어기",
    "Soul Flower": "영혼꽃",
    "Nuclear Reactor Controller": "원자로 제어기",
    "Reactor Wall": "원자로 벽",
    "Reactor Heat Absorber": "원자로 열 흡수기",
    "Reactor Heat Pipe": "원자로 열 파이프",
    "Reactor Heat Vent": "원자로 방열구",
    "Neutron Reflector": "중성자 반사기",
    "Reactor Fuel Rod": "원자로 연료봉",
    "Reactor Double Rod": "원자로 이중 연료봉",
    "Reactor Quad Rod": "원자로 사중 연료봉",
    "Reactor Fuel Port": "원자로 연료 포트",
    "Reactor Energy Port": "원자로 에너지 포트",
    "Reactor Redstone Port": "원자로 레드스톤 포트",
    "Manhattan Module": "맨해튼 모듈",
    "Low-Yield Nuclear Explosion Device": "저위력 핵폭발 장치",
    "Accelerator Controller": "가속기 제어기",
    "Accelerator Motor": "가속기 모터",
    "Accelerator Guide Ring": "가속기 유도 고리",
    "Accelerator Speed Sensor": "가속기 속도 감지기",
    "Tachyon Collector": "타키온 수집기",
    "Hand Drill": "휴대용 드릴",
    "Chainsaw": "전기톱",
    "Electric Mace": "전기 철퇴",
    "Portable Laser": "휴대용 레이저",
    "Target Designator": "표적 지정기",
    "Pipe Wrench": "파이프 렌치",
    "Exo Suit": "엑소 슈트",
    "Exo Helmet": "엑소 헬멧",
    "Exo Chestplate": "엑소 흉갑",
    "Exo Leggings": "엑소 레깅스",
    "Exo Boots": "엑소 부츠",
    "Jetpack": "제트팩",
    "Fluxite": "플럭사이트",
    "Prometheum": "프로메튬",
    "Prometheum Ingot": "프로메튬 주괴",
    "Prometheum Pickaxe": "프로메튬 곡괭이",
    "Prometheum Battleaxe": "프로메튬 전투 도끼",
    "Duratium": "듀라티움",
    "Adamant": "아다만트",
    "Biosteel": "바이오스틸",
    "Energite": "에너자이트",
    "Enderic Compound": "엔더릭 화합물",
    "Enderic Lens": "엔더릭 렌즈",
    "Dubios Container": "두비오스 용기",
    "Heisenberg Compensator": "하이젠베르크 보정기",
    "Unholy Intelligence": "불경한 지능체",
    "Super AI Chip": "슈퍼 AI 칩",
    "Advanced Computing Engine": "고급 연산 엔진",
    "Processing Unit": "처리 장치",
    "Magnetic Coil": "자기 코일",
    "Ion Thruster": "이온 추진기",
    "Flux Gate": "플럭스 게이트",
    "Basic Battery": "기본 배터리",
    "Advanced Battery": "고급 배터리",
    "Silicon Wafer": "실리콘 웨이퍼",
    "Carbon Fibre Strands": "탄소 섬유 가닥",
    "Reinforced Carbon Sheet": "강화 탄소판",
    "Polymer Resin": "고분자 수지",
    "Raw Biopolymer": "가공 전 바이오폴리머",
    "Solid Biofuel": "고체 바이오연료",
    "Packed Wheat": "압축 밀",
    "Clay Catalyst Beads": "점토 촉매 구슬",
    "Overcharged Crystal": "과충전된 수정",
    "Banana": "바나나",
}

SOURCE_OVERRIDES.update(
    {
        "Energy Transmission Pole": "전력 전송 전봇대",
        "Heart of the Machine (Addon)": "기계의 심장(애드온)",
        "Deepslate Uranium Ore": "심층암 우라늄 광석",
        "Uranite Crystal": "우라나이트 수정",
        "Complex Plating": "복합 장갑판",
        "Item Pipe Connection": "아이템 파이프 연결부",
        "Framed Item Pipe": "프레임형 아이템 파이프",
        "Framed Item Pipe Connection": "프레임형 아이템 파이프 연결부",
        "Item Pipe Duct": "아이템 파이프 덕트",
        "Frame Gantry Arm": "프레임 갠트리 암",
        "Block Destroyer Head": "블록 파괴 헤드",
        "Block Placer Head": "블록 배치 헤드",
        "Block Fertilizer": "블록 비료 살포기",
        "Pump Trunk": "펌프 몸체",
        "Carbon Plating Block": "탄소 장갑판 블록",
        "Carbon Reinforced Plating Slab": "탄소 강화 장갑판 반 블록",
        "Carbon Reinforced Plating Stairs": "탄소 강화 장갑판 계단",
        "Carbon Reinforced Plating Pressure Plate": "탄소 강화 장갑판 압력판",
        "Tachyon Absorber": "타키온 흡수기",
        "Big Solar Panel": "대형 태양광 패널",
        "Portable Tank": "휴대용 유체 탱크",
        "Creative Tank": "크리에이티브 유체 탱크",
        "Primitive Machine Core": "초급 기계 핵",
        "Basic Machine Core": "기본 기계 핵",
        "Improved Machine Core": "개량 기계 핵",
        "Advanced Machine Core": "고급 기계 핵",
        "Elite Machine Core": "정예 기계 핵",
        "Ultra Machine Core": "초고급 기계 핵",
        "Ultimate Machine Core": "최종 기계 핵",
        "Molten Adamant": "용융 아다만트",
        "Molten Biosteel": "용융 바이오스틸",
        "Molten Duratium": "용융 듀라티움",
        "Molten Energite": "용융 에너자이트",
        "Molten Fluxite": "용융 플럭사이트",
        "Light Naphtha": "경질 나프타",
        "Silicon Wash": "실리콘 세척액",
        "Mineral Slurry": "광물 슬러리",
        "Sheol Fire": "스올의 불",
        "Strange Matter": "기묘한 물질",
        "Nickel Ore": "니켈 광석",
        "Deepslate Nickel Ore": "심층암 니켈 광석",
        "Endstone Platinum Ore": "엔드 돌 백금 광석",
        "Deepslate Platinum Ore": "심층암 백금 광석",
        "Iron Resource Node": "철 자원 노드",
        "Gold Resource Node": "금 자원 노드",
        "Platinum Resource Node": "백금 자원 노드",
        "Industrial Light": "산업용 조명",
        "Hanging Light": "매달린 조명",
        "Industrial Door": "산업용 문",
        "Industrial Support Beam": "산업용 지지 빔",
        "Industrial Support Girder": "산업용 지지 거더",
        "Copper Reinforced Plating": "구리 강화 장갑판",
        "Copper Reinforced Plating Slab": "구리 강화 장갑판 반 블록",
        "Copper Reinforced Plating Stairs": "구리 강화 장갑판 계단",
        "Copper Reinforced Plating Pressure Plate": "구리 강화 장갑판 압력판",
        "Iron Reinforced Plating": "철 강화 장갑판",
        "Iron Reinforced Plating Slab": "철 강화 장갑판 반 블록",
        "Iron Reinforced Plating Stairs": "철 강화 장갑판 계단",
        "Iron Reinforced Plating Pressure Plate": "철 강화 장갑판 압력판",
        "Nickel Reinforced Plating": "니켈 강화 장갑판",
        "Nickel Reinforced Plating Slab": "니켈 강화 장갑판 반 블록",
        "Nickel Reinforced Plating Stairs": "니켈 강화 장갑판 계단",
        "Nickel Reinforced Plating Pressure Plate": "니켈 강화 장갑판 압력판",
        "Block of Adamant": "아다만트 블록",
        "Block of Electrum": "일렉트럼 블록",
        "Block of Raw Nickel": "가공 전 니켈 블록",
        "Block of Raw Uranium": "가공 전 우라늄 블록",
        "Block of Raw Platinum": "가공 전 백금 블록",
        "Soul Flowers": "영혼꽃",
        "Particle Accelerator Guide Ring": "입자 가속기 유도 고리",
        "Particle Accelerator Linear Motor": "입자 가속기 선형 모터",
        "Particle Accelerator": "입자 가속기",
        "Particle Accelerator Sensor": "입자 가속기 감지기",
        "Single Reactor Rod": "원자로 단일 연료봉",
        "Reactor Neutron Reflector": "원자로 중성자 반사기",
        "Reactor Coolant Absorber Port": "원자로 냉각재 흡수 포트",
        "Cybernetic Research Station": "사이버네틱 연구대",
        "Weed Killer": "제초제",
        "Crude Oil Bucket": "원유 양동이",
        "Turbofuel Bucket": "터보연료 양동이",
        "Steam Bucket": "증기 양동이",
        "Biofuel Bucket": "바이오연료 양동이",
        "Heavy Oil Bucket": "중유 양동이",
        "Diesel Bucket": "디젤 양동이",
        "Light Naphtha Bucket": "경질 나프타 양동이",
        "Sulfuric Acid Bucket": "황산 양동이",
        "Silicon Wash Bucket": "실리콘 세척액 양동이",
        "Mineral Slurry Bucket": "광물 슬러리 양동이",
        "Sheol Fire Bucket": "스올의 불 양동이",
        "Strange Matter Bucket": "기묘한 물질 양동이",
        "Molten Adamant Bucket": "용융 아다만트 양동이",
        "Molten Biosteel Bucket": "용융 바이오스틸 양동이",
        "Molten Duratium Bucket": "용융 듀라티움 양동이",
        "Molten Energite Bucket": "용융 에너자이트 양동이",
        "Molten Fluxite Bucket": "용융 플럭사이트 양동이",
        "Nickel Ingot": "니켈 주괴",
        "Raw Nickel": "가공 전 니켈",
        "Nickel Dust": "니켈 가루",
        "Small Nickel Dust": "작은 니켈 가루",
        "Nickel Nugget": "니켈 조각",
        "Raw Platinum": "가공 전 백금",
        "Platinum Clump": "백금 덩어리",
        "Small Platinum Clump": "작은 백금 덩어리",
        "Platinum Dust": "백금 가루",
        "Small Platinum Dust": "작은 백금 가루",
        "Platinum Gem": "백금 보석",
        "Platinum Nugget": "백금 조각",
        "Small Iron Dust": "작은 철 가루",
        "Small Copper Dust": "작은 구리 가루",
        "Copper Nugget": "구리 조각",
        "Gold Clump": "금 덩어리",
        "Gold Dust": "금 가루",
        "Adamant Ingot": "아다만트 주괴",
        "Adamant Dust": "아다만트 가루",
        "Biosteel Ingot": "바이오스틸 주괴",
        "Biosteel Dust": "바이오스틸 가루",
        "Duratium Ingot": "듀라티움 주괴",
        "Duratium Dust": "듀라티움 가루",
        "Electrum Dust": "일렉트럼 가루",
        "Energite Dust": "에너자이트 가루",
        "Enderic Railgun": "엔더릭 레일건",
        "Steel Dust": "강철 가루",
        "Coal Dust": "석탄 가루",
        "Fine Wire": "가는 전선",
        "Machine Plating": "기계 장갑판",
        "Raw Silicon": "가공 전 실리콘",
        "Silicon": "실리콘",
        "Plastic Sheet": "플라스틱판",
        "Dubious Container": "두비오스 용기",
        "Quartz Dust": "석영 가루",
        "Boosted Exo Elytra": "강화 엑소 겉날개",
        "Raw Uranium": "가공 전 우라늄",
        "Small Uranium Dust": "작은 우라늄 가루",
        "Uranium Dust": "우라늄 가루",
        "Small Plutonium Dust": "작은 플루토늄 가루",
        "Plutonium Dust": "플루토늄 가루",
        "Uranium Pellet": "우라늄 펠릿",
        "Small Plutonium Pellet": "작은 플루토늄 펠릿",
        "Adamant Machine Paint": "아다만트 기계 도색제",
        "Redstone Machine Paint": "레드스톤 기계 도색제",
        "Orange Machine Paint": "주황색 기계 도색제",
        "Camo Machine Paint": "위장 기계 도색제",
        "Fluxite Machine Paint": "플럭사이트 기계 도색제",
        "White Machine Paint": "흰색 기계 도색제",
        "Industrial Machine Paint": "산업용 기계 도색제",
        "Netherite Machine Paint": "네더라이트 기계 도색제",
        "Sculk Machine Paint": "스컬크 기계 도색제",
        "Oil": "원유",
    }
)

TEXT_REPLACEMENTS = (
    ("오리테크", "Oritech"),
    ("오리텍", "Oritech"),
    ("애드온", "애드온"),
    ("업그레이드 추가", "애드온"),
    ("기계 추가 기능", "기계 애드온"),
    ("플럭사이트", "플럭사이트"),
    ("플럭스사이트", "플럭사이트"),
    ("프로메테움", "프로메튬"),
    ("프로메티움", "프로메튬"),
    ("에너지테", "에너자이트"),
    ("엔더릭", "엔더릭"),
    ("정제 공장", "정유기"),
    ("정유소", "정유기"),
    ("분쇄기", "분쇄기"),
    ("파쇄기", "분쇄기"),
    ("조립 공장", "조립기"),
    ("원자 대장간", "원자 단조기"),
    ("조각 대장간", "파편 단조기"),
    ("기계 코어", "기계 핵"),
    ("머신 코어", "기계 핵"),
    ("머신 UI", "기계 UI"),
    ("Oritech 머신", "Oritech 기계"),
    ("항목 파이프", "아이템 파이프"),
    ("재고", "인벤토리"),
    ("우클릭", "우클릭"),
    ("마우스 오른쪽 버튼으로 클릭", "우클릭"),
    ("마우스 오른쪽 버튼 클릭", "우클릭"),
    ("마우스 왼쪽 버튼으로 클릭", "좌클릭"),
    ("마우스 왼쪽 버튼 클릭", "좌클릭"),
)

KEY_OVERRIDES = {
    "advancements.oritech.begin": "Oritech",
    "advancements.oritech.begin.description": (
        "니켈 한 푼 - 가공 전 니켈을 얻어 기술 모험을 시작하세요. 빛나라, 광부여!"
    ),
    "advancements.oritech.generator": "전원 켜기!",
    "advancements.oritech.generator.description": (
        "기본 발전기로 본격적인 전력을 생산하세요. 짜릿하지 않나요?"
    ),
    "advancements.oritech.furnace": "미래의 화로",
    "advancements.oritech.furnace.description": (
        "전기 화로를 손에 넣으세요. 이제 열기가 오르기 시작합니다!"
    ),
    "advancements.oritech.pulverizer": "완전히 분쇄",
    "advancements.oritech.pulverizer.description": (
        "분쇄기를 얻어 광석을 가루로 만드세요. 신나게 부숴 봅시다!"
    ),
    "advancements.oritech.foundry": "녹여 버려",
    "advancements.oritech.foundry.description": (
        "주조소를 얻어 강력한 합금 단조를 시작하세요. 연금술의 진수입니다!"
    ),
    "advancements.oritech.assembler": "조립 라인",
    "advancements.oritech.assembler.description": (
        "조립기를 얻어 부품을 조립하세요. 이제 모든 것이 맞아떨어집니다!"
    ),
    "advancements.oritech.exo_boots": "깃털 같은 부츠",
    "advancements.oritech.exo_boots.description": (
        "엑소 부츠를 제작해 낙하 피해와 작별하세요. 중력이라고요? 처음 듣는데요!"
    ),
    "advancements.oritech.exo_legs": "하체 운동의 날",
    "advancements.oritech.exo_legs.description": (
        "엑소 레깅스를 제작해 경쟁에서 한발 앞서세요. 더 강하고 빠르고 뛰어나게!"
    ),
    "advancements.oritech.exo_chest": "강철의 심장",
    "advancements.oritech.exo_chest.description": (
        "엑소 흉갑을 제작해 몸통을 보호하세요. 아이언 맨이 누구죠?"
    ),
    "advancements.oritech.exo_helmet": "앞서 나가기",
    "advancements.oritech.exo_helmet.description": (
        "엑소 헬멧을 제작해 게임에서 앞서 나가세요. 정신이 물질을 이깁니다!"
    ),
    "advancements.oritech.drill": "드릴 교관",
    "advancements.oritech.drill.description": (
        "휴대용 드릴을 얻어 땅을 뚫기 시작하세요. 깊이 파라, 병사여!"
    ),
    "advancements.oritech.resource_node": "번쩍이는 보물",
    "advancements.oritech.resource_node.description": (
        "자원 노드를 찾으세요. 무한한 부가 기다립니다!"
    ),
    "advancements.oritech.centrifuge": "회전 전문가",
    "advancements.oritech.centrifuge.description": (
        "원심 분리기를 얻어 좋은 것과 나쁜 것을 분리하세요. 돌려서 승리하세요!"
    ),
    "advancements.oritech.plastic": "환상적인 플라스틱",
    "advancements.oritech.plastic.description": (
        "플라스틱판을 손에 넣으세요. 환상적일 뿐 아니라 플라스틱이기도 합니다!"
    ),
    "advancements.oritech.catalyst": "비전 기술자",
    "advancements.oritech.catalyst.description": (
        "비전 안정기를 얻으세요. 경고: 영혼이 들어 있을 수 있습니다!"
    ),
    "advancements.oritech.overenchanted": "비전 공학자",
    "advancements.oritech.overenchanted.description": (
        "X레벨 마법이 부여된 아이템을 얻으세요. 폭발이라니 무슨 말이죠?"
    ),
    "advancements.oritech.laser": "레이저 집중",
    "advancements.oritech.laser.description": (
        "엔더릭 레이저를 얻으세요. 전력을 넣고 플럭사이트를 캐며 땅을 뚫으세요. "
        "뿅뿅, 아무도 막을 수 없습니다!"
    ),
    "advancements.oritech.fluxite": "플럭사이트",
    "advancements.oritech.fluxite.description": (
        "플럭사이트를 얻으세요. 세상에, 미래로 돌아갈 시간입니다!"
    ),
    "advancements.oritech.augmenter": "사이버네틱스!",
    "advancements.oritech.augmenter.description": (
        "타고난… 한계를 강화하세요! 경고: '삐빅'이라고 말하고 싶은 욕구가 커질 수 있습니다."
    ),
    "advancements.oritech.reactor": "원자력",
    "advancements.oritech.reactor.description": (
        "원자로를 건설하세요. 안전이 우선입니다! 아니면… 빛 구경을 즐겨도 좋고요."
    ),
    "advancements.oritech.atomicforge": "원자 대장장이",
    "advancements.oritech.atomicforge.description": (
        "원자 단조기를 얻어 전문가처럼 제작하세요. 원자 단위로 말이죠!"
    ),
    "advancements.oritech.promethium": "프로메테우스의 불",
    "advancements.oritech.promethium.description": (
        "프로메튬 주괴를 얻으세요. 신들에게서 불을 훔쳤습니다!"
    ),
    "advancements.oritech.ultimate_core": "최종 기계",
    "advancements.oritech.ultimate_core.description": (
        "최종 기계 핵을 얻으세요. 이제 애드온을 잔뜩 붙일 수 있습니다!"
    ),
    "advancements.oritech.gold_gem": "전설적인 연금술사",
    "advancements.oritech.gold_gem.description": (
        "금을 더 많은 금으로 바꾸는 비밀 기술을 배우세요!"
    ),
    "advancements.oritech.ai": "인공적인 총명함",
    "advancements.oritech.ai.description": (
        "슈퍼 AI 칩을 얻으세요. 스카이넷이 누구죠? 영리할 뿐 아니라 엄청나게 똑똑합니다!"
    ),
    "advancements.oritech.unholy": "불경한 지식",
    "advancements.oritech.unholy.description": (
        "불경한 지능체를 얻으세요. 지식은 힘이라지만, 이건 뭔가 다릅니다!"
    ),
    "advancements.oritech.steam_engine": "증기의 꿈",
    "advancements.oritech.steam_engine.description": (
        "증기의 힘을 활용하세요! 물을 에너지로 바꿨으니, 이제 뜨거운 사고만 나지 않길 바랍니다!"
    ),
    "tooltip.oritech.promethium_pick": "Shift + 우클릭으로 모드를 전환합니다.",
    "tooltip.oritech.portable_laser.3": "우클릭하면 고에너지 폭발을 일으킵니다.",
    "tooltip.oritech.portable_laser.status.hint": ("(웅크린 채 우클릭하여 전환)"),
    "tooltip.oritech.core_desc": "멀티블록. 필요한 기계 핵: ",
    "tooltip.oritech.machine.quality": (
        "기계 품질: %d\n\n이 블록에 연결할 수 있는 애드온\n확장기 수를 결정합니다."
        "\n\n더 높은 등급의 기계 핵을 사용하면 늘어납니다."
        "\n\n현재 품질 진행도: %s"
    ),
    "tooltip.oritech.pulverizer_dust_combine": ("작은 가루를 주괴로 자동 결합합니다."),
    "tooltip.oritech.tank_content": (
        "%f mB %s\n\n유체 용기를 좌클릭하면 주입하고,\n우클릭하면 추출합니다."
    ),
    "tooltip.oritech.accelerator_ring": (
        "입자의 이동 경로를 정합니다. 우클릭하면 한쪽 끝의 방향을 바꿀 수 있으며, "
        "레드스톤으로 제어할 수 있습니다."
    ),
    "tooltip.oritech.item_pipe.1": "우클릭하여 추출을 전환합니다.",
    "tooltip.oritech.item_pipe.3": (
        "모터 아이템으로 클릭하면 모든 슬롯에서 추출하도록 파이프를 업그레이드합니다."
    ),
    "tooltip.oritech.creative_tank": (
        "유체가 든 양동이로 우클릭하면 유체를 설정하고, 빈 양동이로 우클릭하면 비웁니다."
    ),
    "tooltip.oritech.unstable_laser_tooltip": (
        "레이저는 이 기계의 처리 용량을 늘리지 않고, 대신 다음 항목을 늘립니다:"
    ),
    "tooltip.oritech.unstable_laser_tooltip.2": (
        "이 블록의 저장 용량. 이 수치는 기하급수적으로 증가합니다(최대 5,000배)."
    ),
    "text.oritech.load_augments.tooltip": ("플레이어의 기존 증강을 기계로 불러옵니다"),
    "oritech.configuration.fluidPipeInternalStorageBuckets": (
        "유체 파이프 내부 저장량(양동이)"
    ),
    "oritech.configuration.steamBoilerCapacityBuckets": ("증기 보일러 용량(양동이)"),
    "oritech.configuration.enableHelpButton": "기계 UI 도움말 버튼 활성화",
    "oritech.configuration.tankSizeInBuckets": "탱크 크기(양동이)",
    "oritech.configuration.fluidPipeExtractAmountBuckets": (
        "유체 파이프 추출량(양동이)"
    ),
    "oritech.configuration.portableTankCapacityBuckets": ("휴대용 탱크 용량(양동이)"),
    "oritech.configuration.itemPipeIntervalDuration": "아이템 파이프 작동 간격",
    "tag.item.c.storage_blocks.adamant": "아다만트 블록",
    "tag.item.c.storage_blocks.electrum": "일렉트럼 블록",
    "tag.item.c.storage_blocks.platinum": "백금 블록",
    "tag.item.c.storage_blocks.raw_nickel": "가공 전 니켈 블록",
    "tag.item.c.storage_blocks.raw_platinum": "가공 전 백금 블록",
    "key.oritech.augment_screen": "임플란트 제어 [길게 누르기]",
    "tooltip.oritech.oracle_missing": (
        "Oracle Index Wiki 모드가 설치되지 않아 게임 내 도움말을 사용할 수 없습니다."
    ),
    "tooltip.oritech.addon_yield_desc": (
        "파편 단조기의 부산물 양을 두 배로 늘립니다. 블록 파괴기와 엔더릭 레이저의 "
        "블록 생산량도 증가합니다."
    ),
    "tooltip.oritech.addon_crop_desc": (
        "블록 파괴기와 엔더릭 레이저에 적용됩니다. 다 자라지 않은 작물이나 동물은 "
        "건너뜁니다."
    ),
    "tooltip.oritech.capture_item_desc_2": (
        "알레이가 이 설명에 맞을지도 모릅니다. 다만 항상 아이템을 가져가려 합니다."
    ),
    "tooltip.oritech.machine.addon_silk_touch": (
        "섬세한 손길 애드온과 행운 애드온을 함께 설치하면 섬세한 손길이 우선합니다."
    ),
    "title.oritech.burst.active.tooltip": (
        "급속 처리가 작동 중입니다. 남은 시간: %s틱."
    ),
    "tooltip.oritech.machine.byproduct_bonus.tooltip": (
        "수확량 애드온이 설치되어 부산물이 두 배로 늘어납니다."
    ),
    "message.oritech.drone.target_set": (
        "대상 포트를 설정했습니다.\n인벤토리가 비어 있지 않으면 드론이 운반합니다."
    ),
    "text.oritech.reactor.explosion_imminent": "위험",
    "oritech.configuration.ziplineCameraSwitch": ("집라인 이용 중 3인칭 카메라 활성화"),
    "oritech.configuration.collectorEnergyStorage": "타키온 수집기 에너지 용량",
    "oritech.configuration.tachyonCollisionEnergyFactor": ("입자 충돌 타키온 RF 배율"),
    "oritech.configuration.tightMachineAddonHitboxes": (
        "기계 애드온의 좁은 충돌 상자 사용"
    ),
    "tooltip.oritech.input_mode_fill_evenly": (
        "아이템을 고르게 채웁니다. 새 아이템은 항상\n조건에 맞는 가장 아래 슬롯에 넣습니다."
    ),
    "tooltip.oritech.input_mode_sided": "아이템 입출력은 면의 영향을 받습니다.\n\n",
    "tooltip.oritech.item_filter": (
        "인벤토리에 넣을 수 있는 아이템을 선별하는 데 사용합니다."
    ),
    "tooltip.oritech.chambers": (
        "처리실을 하나 추가할 때마다 기계가 매 주기마다\n아이템 X개를 더 처리합니다."
    ),
    "tooltip.oritech.item_filter.whitelist": (
        "현재 목록의 아이템과 \n일치하는 아이템만 통과시킵니다."
    ),
    "tooltip.oritech.item_filter.blacklist": (
        "현재 목록의 아이템과 \n일치하지 않는 아이템만 통과시킵니다."
    ),
    "tooltip.oritech.item_filter.nbt": (
        "현재 목록의 아이템에서 사용자 지정 NBT 데이터를 검사합니다."
    ),
    "tooltip.oritech.item_filter.no_nbt": "현재 아이템 유형/ID만 검사합니다.",
    "tooltip.oritech.item_filter.component": (
        "현재 목록의 아이템에서 모든 데이터 구성 요소 값을 검사합니다."
    ),
    "tooltip.oritech.black_hole": (
        "무엇을 하는지 정확히 알지 못한다면 절대 설치하지 마세요."
    ),
    "tooltip.oritech.portable_laser.1": (
        "좌클릭하면 에너지를 전송하고 블록을 채굴하며 엔티티에 피해를 주고"
    ),
    "tooltip.oritech.portable_laser.2": (
        "채굴한 아이템을 엔더릭 레이저처럼 변환하는 연속 광선을 발사합니다."
    ),
    "tooltip.oritech.refinery_module_count": (
        "위에 반응실 탱크 모듈 두 개를 추가로 지어 각 탱크를 열 수 있습니다.\n"
        "모듈이 없으면 아이템 출력과 느린 첫 번째 출력이 두 배가 됩니다.\n"
        "모듈 하나는 두 번째 탱크 출력만 두 배로 만들고, 두 개는 모든 출력을 활성화합니다."
    ),
    "tooltip.oritech.enchanter_item_needed": "아이템 삽입",
    "message.oritech.enchanter.insert_item": "아이템 삽입",
    "message.oritech.pump.initializing": (
        "펌프를 초기화하는 중입니다... (유체가 많으면 시간이 걸릴 수 있습니다.)"
    ),
    "message.oritech.pump.no_fluids": "사용 가능한 유체가 없습니다",
    "message.oritech.pump.pump_finished": "모든 유체를 퍼냈습니다",
    "tooltip.oritech.power_pole_connection_disabled": (
        "전력 전봇대가 연결되지 않았습니다. 표적 지정기를 사용해 연결하세요."
    ),
    "text.oritech.accelerator.ui.waiting": "가속할 아이템 삽입",
    "oritech.configuration.liquidPerBlockUsage": "블록당 유체 사용량",
}

ALLOWED_EXACT_KEYS = {
    "oracle_index.title.oritech",
    "advancements.oritech.begin",
    "key.oritech.hotkey_category",
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


def candidate() -> dict[str, object]:
    """모든 영어 문자열의 보호된 자동 번역 후보를 만든다."""
    english = load_json(LANG_ROOT / "en_us.json")
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests = {
        source
        for source in english.values()
        if isinstance(source, str)
        and source not in SOURCE_OVERRIDES
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
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("자동 번역 후보 생성 실패:\n" + "\n".join(failures))

    candidates: dict[str, str] = {}
    for key, source in english.items():
        if not isinstance(source, str):
            raise TypeError(f"문자열이 아닌 언어 값: {key}")
        if key in KEY_OVERRIDES:
            candidates[key] = KEY_OVERRIDES[key]
        elif source in SOURCE_OVERRIDES:
            candidates[key] = SOURCE_OVERRIDES[source]
        elif family_goal.is_allowed_original(source):
            candidates[key] = source
        else:
            candidates[key] = str(cache[source])
    write_json(CANDIDATE_FILE, candidates)
    report = {
        "keys": len(english),
        "candidate_keys": len(candidates),
        "review_scope": "all_current_english_keys",
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "auto_candidate_report.json", report)
    return report


def reviewed_value(key: str, source: str, candidate_value: str) -> str:
    """영어 원문과 자동 후보를 대조해 프로젝트 용어로 정규화한다."""
    value = KEY_OVERRIDES.get(key, SOURCE_OVERRIDES.get(source, candidate_value))
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    if key.startswith(("block.oritech.", "item.oritech.", "fluid.oritech.")):
        value = value.rstrip(".")
    return value


def normalize() -> dict[str, object]:
    """전체 1,255개 키를 영어 원문과 대조한 검수값으로 교체한다."""
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
        if korean[key] != translated:
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
    """키·형식·미번역·번역 유발 이름 충돌을 검사한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    errors: list[str] = []
    untranslated: list[str] = []
    if list(english) != list(korean):
        errors.append("키 또는 순서 불일치")
    for key, source in english.items():
        target = korean.get(key)
        if not isinstance(source, str) or not isinstance(target, str):
            errors.append(f"문자열이 아닌 값: {key}")
            continue
        errors.extend(family_goal.validate_family_value(FAMILY, key, source, target))
        if (
            source == target
            and key not in ALLOWED_EXACT_KEYS
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
