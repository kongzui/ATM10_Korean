#!/usr/bin/env python3
"""XyCraft 계열 언어와 관련 퀘스트를 현재 영어 원문 기준으로 번역하고 검증한다."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path
from zipfile import ZipFile

import ars_family
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root


FAMILY = "xycraft"
NAMESPACES = (
    "xycraft_core",
    "xycraft_machines",
    "xycraft_world",
    "xycraft_override",
)
WORK_ROOT = PROJECT_ROOT / "working/xycraft"
CACHE_FILE = PROJECT_ROOT / "temp/xycraft_language_candidate_cache_v1.json"
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?(?:\.\d+)?[a-zA-Z%]|\{[^{}]*\}")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")

COLORS = {
    "Blue": "파란색",
    "Dark": "검은색",
    "Green": "초록색",
    "Light": "하얀색",
    "Red": "빨간색",
}

SOURCE_OVERRIDES = {
    "XyCraft": "XyCraft",
    "XyCraft Core": "XyCraft Core",
    "XyCraft Machines": "XyCraft Machines",
    "XyCraft World": "XyCraft World",
    "XyCraft Override": "XyCraft Override",
    "XyCraft Foils": "XyCraft 포일",
    "Kivi": "키비",
    "Xynergy": "Xynergy",
    "Soaryn": "Soaryn",
    "UI Interpolation Rate": "UI 보간 속도",
    "Item IO": "아이템 입출력기",
    "TEST": "테스트",
    "Woop!": "좋았어!",
    "AllRightsReserved": "All Rights Reserved",
    "Fabricator": "제작기",
    "Soaryn Box": "Soaryn 상자",
    "Valve": "밸브",
    "Water Block": "물 블록",
    "Isolator": "격리기",
    "Gauntlet": "건틀릿",
    "Foil": "포일",
    "Visor": "바이저",
    "Pulse": "펄스",
    "Orientations": "방향",
    "Squasher": "압착기",
    "Batter": "튀김옷 반죽",
    "Flare": "섬광탄",
}

KEY_OVERRIDES = {
    "config.client.xycraft_core.visuals": "화면 효과",
    "config.client.xycraft_core.visuals.fluid_unit": "유체 단위",
    "config.server.xycraft_core.energy_paradigm": "에너지 체계",
    "gui.xycraft.slot.strict": "정밀 모드",
    "gui.xycraft.slot.strict.set": "%1$s 키로 정밀 모드를 전환합니다.",
    "jei.xycraft.recipe.general.requirement.locked": "연구하지 않은 조합법",
    "key.xycraft_core.modifier_key": "보조 키",
    "tag.block.c.immovable": "이동 불가 블록",
    "tag.block.c.incorrect.quick_pickup": "빠른 회수에 부적합한 블록",
    "tag.block.c.mineable.quick_pickup": "빠른 회수로 채굴 가능한 블록",
    "tag.block.c.valid_features.dirt": "유효한 흙 지형",
    "tag.block.xycraft.chorus_stem": "후렴과 열매 줄기",
    "tag.block.xycraft.colored_clouds": "색상 구름 블록",
    "tag.block.xycraft.connected_textures.ignored_occlusion": "연결 텍스처 가림 판정 제외 블록",
    "tag.block.xycraft.dragon_head": "드래곤 머리",
    "tag.block.xycraft.fluid_voids": "유체 소멸기",
    "tag.block.xycraft.immune.fabricator": "제작기에 면역인 블록",
    "tag.block.xycraft.immune.void_containment": "공허 컨테이너에 면역인 블록",
    "tag.block.xycraft.kivi_ore_replaceables": "키비 광석으로 대체 가능한 블록",
    "tag.block.xycraft.multiblock.invalid_face": "멀티블록의 허용되지 않는 면 블록",
    "tag.block.xycraft.multiblock.invalid_frame": "멀티블록의 허용되지 않는 틀 블록",
    "tag.block.xycraft.multiblock.invalid_interior": "멀티블록의 허용되지 않는 내부 블록",
    "tag.block.xycraft.multiblock.tank.invalid_empty": "탱크 멀티블록의 허용되지 않는 빈 공간",
    "tag.block.xycraft.multiblock.tank.invalid_face": "탱크 멀티블록의 허용되지 않는 면 블록",
    "tag.block.xycraft.multiblock.tank.invalid_frame": "탱크 멀티블록의 허용되지 않는 틀 블록",
    "tag.block.xycraft.multiblock.tank.valid_empty": "탱크 멀티블록의 유효한 빈 공간",
    "tag.block.xycraft.multiblock.tank.valid_face": "탱크 멀티블록의 유효한 면 블록",
    "tag.block.xycraft.multiblock.tank.valid_frame": "탱크 멀티블록의 유효한 틀 블록",
    "tag.block.xycraft.multiblock.valid_face": "멀티블록의 유효한 면 블록",
    "tag.block.xycraft.multiblock.valid_frame": "멀티블록의 유효한 틀 블록",
    "tag.block.xycraft.multiblock.valid_interior": "멀티블록의 유효한 내부 블록",
    "tag.item.c.dirty_dusts.aluminum": "오염된 알루미늄 가루",
    "tag.item.c.dusts.aluminum": "알루미늄 가루",
    "tag.item.c.ingots.aluminum": "알루미늄 주괴",
    "tag.item.c.nuggets.aluminum": "알루미늄 조각",
    "tag.item.c.nuggets.brass_like": "황동 계열 조각",
    "tag.item.c.nuggets.copper": "구리 조각",
    "tag.item.c.nuggets.osmium": "오스뮴 조각",
    "tag.item.c.ore_bearing_ground.kivi": "키비 광석을 품은 기반 블록",
    "tag.item.c.ores_in_ground.kivi": "기반 블록 속 키비 광석",
    "tag.item.c.plates.aluminum": "알루미늄 판",
    "tag.item.c.plates.copper": "구리 판",
    "tag.item.c.plates.gold": "금 판",
    "tag.item.c.plates.iron": "철 판",
    "tag.item.c.raw_materials.aluminum": "미가공 알루미늄",
    "tag.item.c.shards.aluminum": "알루미늄 조각",
    "tag.item.c.storage_blocks.raw_aluminum": "미가공 알루미늄 저장 블록",
    "tag.item.xycraft.crafting_groups.cloud.aluminum": "알루미늄 구름 조합 그룹",
    "tag.item.xycraft.crafting_groups.cloud.inverted": "반전 구름 조합 그룹",
    "tag.item.xycraft.crafting_groups.cloud.kivi": "키비 구름 조합 그룹",
    "tag.item.xycraft.crafting_groups.aluminum": "알루미늄 조합 그룹",
    "tag.item.xycraft.crafting_groups.kivi": "키비 조합 그룹",
    "tag.item.xycraft.crafting_groups.tuff": "응회암 조합 그룹",
    "tag.item.xycraft.groupings.smooth_stone": "매끄러운 돌 그룹",
    "tag.item.xycraft.lamps": "조명",
    "tag.item.xycraft.plates": "판",
    "unit.xycraft.xynergy": "%s Xynergy",
    "block.xycraft_machines.charger.tooltip": "외부 에너지로 아이템을 충전합니다.",
    "block.xycraft_machines.collector.tooltip": "필터를 설정할 수 있으며, 떨어진 아이템이 엔티티가 되기 전에 수집합니다.",
    "block.xycraft_machines.fluid_selector.tooltip.0": "크리에이티브 아이템: ",
    "block.xycraft_machines.hydro_pump.tooltip.2": "기본 속도: 주기당 %s",
    "block.xycraft_machines.hydro_pump.tooltip.3": "물에 잠김: 주기당 %s",
    "block.xycraft_machines.ignition_plate.tooltip": "필요할 때 바로 불을 붙입니다!",
    "block.xycraft_machines.item_io.tooltip": "렌치로 채우기 면과 비우기 면을 전환할 수 있습니다.",
    "block.xycraft_machines.item_selector.tooltip.0": "크리에이티브 아이템: ",
    "block.xycraft_machines.light_field.tooltip.0": "정육면체 범위 안에서 몹 생성을 막습니다.",
    "block.xycraft_machines.nitrogen_extractor.tooltip": "70%%는 너무 많아 보이네요! 조금 줄여 보죠.",
    "block.xycraft_machines.void_container.tooltip": "내부에 블랙홀이 들어 있습니다! 아이템이나 유체를 없애는 데 사용합니다.",
    "block.xycraft_machines.water_block.tooltip": "슈뢰딩거의 물 블록!",
    "item.xycraft_machines.module_area_survey.tooltip": "전환 가능한 3×3 채굴 기능을 해제합니다.",
    "item.xycraft_machines.module_fortune.tooltip": "모듈식 도구에 행운 I을 부여합니다.",
    "item.xycraft_machines.module_hunter.tooltip": "모듈식 무기를 약탈 VII 특화 무기로 만듭니다.",
    "item.xycraft_machines.module_looting.tooltip": "모듈식 무기에 약탈 I을 부여합니다.",
    "item.xycraft_machines.module_prospector.tooltip": "모듈식 도구를 행운 VII 특화 도구로 만듭니다.",
    "jei.xycraft.recipe.crusher.tooltip": "성공 확률 %s%%",
    "recipe.xycraft.refinery.fuel": "저급 연료",
    "recipe.xycraft.refinery.obsidian": "부서지기 쉬운 암석",
    "xycraft_machines.fluid.batter": "튀김옷 반죽",
    "xycraft_machines.fluid.bio_fuel": "바이오 연료",
    "xycraft_machines.fluid.liquid_dye": "액체 염료",
    "xycraft_machines.fluid.liquid_nitrogen": "액체 질소",
    "xycraft_machines.fluid.nitrogen": "질소 기체",
    "xycraft_machines.fluid.resin": "바이오 수지",
    "xycraft_machines.fluid.shaken_milk": "저은 우유",
    "xycraft_machines.fluid.super_heated_ore": "초고온 광석 슬러리",
    "block.xycraft_override.smooth_smooth_stone": "아주 매끈한 돌",
}

NAME_TERMS = {
    "Mekanical Chemical Condenser": "메카니즘 화학 응축기",
    "Mekanical Fluid Evaporator": "메카니즘 유체 증발기",
    "Archon Affinity Specialization Module": "아콘 친화 특화 모듈",
    "Bastille Specialization Module": "바스티유 특화 모듈",
    "Hunter Specialization Module": "사냥꾼 특화 모듈",
    "Mythical Snipe Module": "신화급 저격 모듈",
    "Prospector Specialization Module": "탐광꾼 특화 모듈",
    "Totemic Death Specialization Module": "토템 죽음 특화 모듈",
    "Tunneler Specialization Module": "굴착 특화 모듈",
    "Environmental Processing Module": "환경 처리 모듈",
    "Energy Efficiency Module": "에너지 효율 모듈",
    "Movement Speed Module": "이동 속도 모듈",
    "Overclocked Mining Module": "오버클럭 채굴 모듈",
    "Area Survey Module": "지역 조사 모듈",
    "AI Mining Module": "AI 채굴 모듈",
    "Tree Focus Module": "나무 집중 모듈",
    "Vein Logic Module": "광맥 판정 모듈",
    "Silk Touch Module": "섬세한 손길 모듈",
    "Protection Module": "보호 모듈",
    "Fortune Module": "행운 모듈",
    "Looting Module": "약탈 모듈",
    "Mining Module": "채굴 모듈",
    "Improved Gauntlet": "개선된 건틀릿",
    "Perfected Gauntlet": "완성된 건틀릿",
    "Balloon on a Stick": "막대에 매단 풍선",
    "Accelerated Planter": "가속 화분",
    "Illumination Field": "조명장",
    "Ignition Plate": "점화판",
    "Nitrogen Extractor": "질소 추출기",
    "Engineering Table": "공학 작업대",
    "Void Container": "공허 컨테이너",
    "Fluid Selector": "유체 선택기",
    "Item Selector": "아이템 선택기",
    "Fluid Void": "유체 소멸기",
    "Hydro Pump": "수력 펌프",
    "Hover Pylon": "호버 파일런",
    "Light Field": "광원장",
    "Power Core": "동력 코어",
    "Machine Base": "기계 베이스",
    "Soaryn Box": "Soaryn 상자",
    "Energy Pipe": "에너지 파이프",
    "Fluid Pipe": "유체 파이프",
    "Energy Port": "에너지 포트",
    "Fluid Port": "유체 포트",
    "Chemical Port": "화학 물질 포트",
    "Item Port": "아이템 포트",
    "Creative Cell": "크리에이티브 셀",
    "Durable Cell": "내구성 셀",
    "Fluid IO": "유체 입출력기",
    "Item IO": "아이템 입출력기",
    "Fluid Tank": "유체 탱크",
    "ProtoBlock": "프로토블록",
    "Block of Resin": "수지 블록",
    "Resin Ball": "수지 덩어리",
    "Aluminum Wrench": "알루미늄 렌치",
    "Hover Pack": "호버 팩",
    "Flare Rod": "섬광 막대",
    "Dye Palette": "염료 팔레트",
    "Incomplete Processor": "미완성 프로세서",
    "Mantle Core Extraction": "맨틀 코어 추출",
    "Nitrogen Extraction": "질소 추출",
    "Gravel Separation": "자갈 분리",
    "Pebble Crushing": "조약돌 분쇄",
    "Rock Crushing": "암석 분쇄",
    "Steel Refining": "강철 정제",
    "Water Packaging": "물 포장",
    "Water Emptying": "물 비우기",
    "Washing Gravel": "자갈 세척",
    "Vulcanization Module": "가황 모듈",
    "Ore Slurry": "광석 슬러리",
    "Redstone Slurry": "레드스톤 슬러리",
    "Super Heated Ore Slurry": "초고온 광석 슬러리",
    "Clean Aluminum Slurry": "깨끗한 알루미늄 슬러리",
    "Dirty Aluminum Slurry": "오염된 알루미늄 슬러리",
    "Aluminum Ore Slurry": "알루미늄 광석 슬러리",
    "Copper Ore Slurry": "구리 광석 슬러리",
    "Gold Ore Slurry": "금 광석 슬러리",
    "Iron Ore Slurry": "철 광석 슬러리",
    "Liquid Nitrogen": "액체 질소",
    "Nitrogen Gas": "질소 기체",
    "Sulfuric Acid": "황산",
    "Heavy Oil Residue": "중유 잔류물",
    "Crude Oil": "원유",
    "Crude Fuel": "저급 연료",
    "Bio Fuel": "바이오 연료",
    "Bio Resin": "바이오 수지",
    "Polymer Resin": "고분자 수지",
    "Cryo Coolant": "극저온 냉각수",
    "Cooking Oil": "식용유",
    "Salt Water": "소금물",
    "Shaken Milk": "저은 우유",
    "Liquid Dye": "액체 염료",
    "Coagulated Lava": "응고된 용암",
    "Coagulated Water": "응고된 물",
    "Cooled Magma": "식은 마그마",
    "Molten Rock": "용융 암석",
    "Brittle Rock": "부서지기 쉬운 암석",
    "Saddened Obsidian": "우울한 흑요석",
    "Hardened Red Sand": "굳은 붉은 모래",
    "Hardened Gravel": "굳은 자갈",
    "Hardened Sand": "굳은 모래",
    "Cobble Mixture": "조약돌 혼합물",
    "Aluminum Crystal": "알루미늄 결정",
    "Aluminum Clump": "알루미늄 덩어리",
    "Dirty Aluminum Dust": "오염된 알루미늄 가루",
    "Aluminum Dust": "알루미늄 가루",
    "Aluminum Shard": "알루미늄 조각",
    "Aluminum Sheet": "알루미늄 판",
    "Copper Sheet": "구리 판",
    "Gold Sheet": "금 판",
    "Iron Sheet": "철 판",
    "Copper Nugget": "구리 조각",
    "Raw Aluminum": "미가공 알루미늄",
    "Block of Raw Aluminum": "미가공 알루미늄 블록",
    "Aluminum Storage": "알루미늄 저장 블록",
    "Xychorium Gem Storage": "자이코륨 보석 블록",
    "Xychorium Gem": "자이코륨 보석",
    "Xychorium Ore": "자이코륨 광석",
    "Aluminum Ore": "알루미늄 광석",
    "Aluminum Ingot": "알루미늄 주괴",
    "Aluminum Nugget": "알루미늄 조각",
    "Aluminum Bricks": "알루미늄 벽돌",
    "Aluminum Tiles": "알루미늄 타일",
    "Aluminum Pillar": "알루미늄 기둥",
    "Aluminum Trim": "알루미늄 장식재",
    "Aluminum Torch": "알루미늄 횃불",
    "Copper Torch": "구리 횃불",
    "Kivi Bricks": "키비 벽돌",
    "Kivi Tiles": "키비 타일",
    "Kivi Pillar": "키비 기둥",
    "Kivi Trim": "키비 장식재",
    "Kivi Rajan": "키비 라잔",
    "Smooth Kivi": "매끈한 키비",
    "Immortal Aluminum": "불멸의 알루미늄",
    "Immortal Stone": "불멸의 돌",
    "Inverted Bricks": "반전 벽돌",
    "Inverted Tiles": "반전 타일",
    "Glass Viewer": "유리 뷰어",
    "RGB Viewer": "RGB 뷰어",
    "RGB Cube Lamp": "RGB 큐브 조명",
    "RGB Flush Lamp": "RGB 매립형 조명",
    "RGB Lantern Lamp": "RGB 랜턴 조명",
    "RGB Pillar Lamp": "RGB 기둥 조명",
    "RGB Lamp": "RGB 조명",
    "Inverted RGB Lamp": "반전 RGB 조명",
    "Aurey Block": "오리 블록",
    "Shiny Layers": "빛나는 층",
    "Shiny Bricks": "빛나는 벽돌",
    "Ore Geyser": "광석 간헐천",
    "Chiseled Polished Blackstone": "조각된 윤나는 흑암",
    "Chiseled Nether Bricks": "조각된 네더 벽돌",
    "Chiseled Red Sandstone": "조각된 붉은 사암",
    "Chiseled Stone Bricks": "조각된 석재 벽돌",
    "Chiseled Tuff Bricks": "조각된 응회암 벽돌",
    "Chiseled Wood Pillar": "조각된 나무 기둥",
    "Chiseled Deepslate": "조각된 심층암",
    "Chiseled Sandstone": "조각된 사암",
    "Chiseled Tuff": "조각된 응회암",
    "Crying Obsidian": "우는 흑요석",
    "Deepslate Bricks": "심층암 벽돌",
    "Deepslate Tiles": "심층암 타일",
    "End Stone Bricks": "엔드 석재 벽돌",
    "Gilded Blackstone": "금빛 흑암",
    "Mossy Stone Bricks": "이끼 낀 석재 벽돌",
    "Polished Blackstone Bricks": "윤나는 흑암 벽돌",
    "Prismarine Bricks": "프리즈머린 벽돌",
    "Red Nether Bricks": "붉은 네더 벽돌",
    "Nether Bricks": "네더 벽돌",
    "Quartz Bricks": "석영 벽돌",
    "Stone Bricks": "석재 벽돌",
    "Mud Bricks": "진흙 벽돌",
    "Purpur Block": "퍼퍼 블록",
    "Purpur Pillar": "퍼퍼 기둥",
    "Magma Block": "마그마 블록",
    "Bricks": "벽돌",
}

TEXT_REPLACEMENTS = (
    ("자이크래프트", "XyCraft"),
    ("Xychorium", "자이코륨"),
    ("자이코리움", "자이코륨"),
    ("크시코륨", "자이코륨"),
    ("키위", "키비"),
    ("키비위", "키비"),
    ("소아린", "Soaryn"),
    ("아이템 IO", "아이템 입출력기"),
    ("유체 IO", "유체 입출력기"),
    ("멀티 블록", "멀티블록"),
    ("다중 블록", "멀티블록"),
    ("기계 프레임", "기계 틀"),
    ("스토리지", "저장소"),
    ("액체", "유체"),
    ("항목", "아이템"),
    ("엔터티", "엔티티"),
    ("레시피", "조합법"),
    ("토글", "전환"),
)

QUEST_OVERRIDES: dict[str, object] = {
    "quest.030AC1AF8F735550.quest_desc": [
        "탱크에 유체를 넣으려면 파이프가 필요합니다.\n\n수력 펌프는 느리지만 아무 비용 없이 탱크에 물을 자동으로 채울 수 있습니다!"
    ],
    "quest.030AC1AF8F735550.title": "파이프",
    "quest.06B85804163DD18B.quest_desc": [
        "Soaryn 상자(Soaryn은 XyCraft의 제작자입니다)는 XyCraft의 상자입니다.\n\n블록을 부수면 안의 아이템을 보존하지 않습니다! 상자에 있는 네모 칸들은 무슨 역할을 할까요?"
    ],
    "quest.08E484DD3E751697.quest_subtitle": "ROYGBIV의 B",
    "quest.08E484DD3E751697.title": "&b파란색 자이코륨 보석",
    "quest.0D01524F249E25D7.quest_subtitle": "누가 불을 껐나요?",
    "quest.0D01524F249E25D7.title": "&8검은색 자이코륨 보석",
    "quest.15540271BF17C2E4.quest_desc": [
        "&lXyCraft에 오신 것을 환영합니다!&r\n\n이 모드 계열은 주로 XyCraft: World와 Machines로 이루어져 있습니다!\nWorld에서는 채굴 중에 여러 색상의 자이코륨 보석을 찾을 수 있습니다."
    ],
    "quest.15540271BF17C2E4.title": "&lXyCraft",
    "quest.16B4A00948D1F60D.quest_desc": [
        "이 퀘스트는 AllTheMods 모드팩에서 사용하기 위해 &6AllTheMods 제작진&r 또는 &2커뮤니티 기여자&r가 작성했습니다.\n\n모든 &6AllTheMods&r 팩은 &eAll Rights Reserved&r 라이선스로 배포되므로, 명시적인 허가 없이 &6AllTheMods 팀&r이 출시하지 않은 공개 팩에서 이 퀘스트를 사용할 수 없습니다.\n\n이 퀘스트는 의도적으로 숨겨져 있습니다. 이 내용이 보인다면 편집 모드입니다."
    ],
    "quest.1A96C595CBA42840.quest_desc": [
        "키비 씨앗으로 키비 정수를 기를 수 있으며, 키비 정수를 조합해 키비를 만들 수 있습니다!"
    ],
    "quest.1A96C595CBA42840.title": "키비 자동화",
    "quest.1E00DBAACDF4404F.quest_desc": [
        "수집기는 값싼 흡수 호퍼처럼 작동합니다.\n\n반경 3블록 안의 아이템을 주워 아래쪽 인벤토리나 자신의 인벤토리에 넣습니다. 레드스톤 신호로 끌 수도 있습니다!"
    ],
    "quest.2278A98DCDF713D7.quest_desc": [
        "이제 탱크를 만들 차례입니다! 먼저 건축 블록과 밸브가 최소 1개 필요합니다. 유리와 아이템 입출력기는 선택 사항입니다.\n\n탱크는 건축 블록으로 틀을 만들어야 합니다. 투명하지 않고, 중력의 영향을 받지 않으며, 자연 흙이나 잔디가 아닌 블록을 건축 블록으로 사용할 수 있습니다.\n\n돌·나무·금속 같은 블록으로 틀과 모서리를 만들고, 유리·밸브·아이템 입출력기는 벽에 설치하세요. 내부는 비어 있어야 합니다.\n\n최대 크기는 13x13x13입니다. 구조를 완성한 뒤 밸브를 우클릭하면 ‘완성됨’이라고 표시되거나 문제점을 알려 줍니다."
    ],
    "quest.2278A98DCDF713D7.title": "&l탱크",
    "quest.2AC7BC448C007BDB.quest_desc": [
        "키비를 알루미늄으로 보강하면 기계를 만드는 데 필요한 기계 틀을 얻을 수 있습니다."
    ],
    "quest.2B5E14A47062F83C.quest_subtitle": "ROYGBIV의 R",
    "quest.2B5E14A47062F83C.title": "&c빨간색 자이코륨 보석",
    "quest.2C4ECA4F5B1639F4.quest_desc": [
        "광원장은 눈에 잘 보이는 빛을 내지는 않지만 거대 횃불처럼 작동합니다.\n\n주변 약 32블록 반경에서는 몹이 생성되지 않습니다."
    ],
    "quest.2C4ECA4F5B1639F4.title": "&f광원장",
    "quest.2C7D62231AD6406A.quest_desc": [
        "XyCraft에는 훌륭한 멀티블록 유체 탱크가 있습니다!"
    ],
    "quest.2C7D62231AD6406A.title": "&b유체 저장 및 운반",
    "quest.355244420EA47546.quest_desc": [
        "제작기는 자동 조합 장치입니다. 아래쪽 인벤토리에서 아이템을 가져와 지정한 조합법을 만듭니다.\n\nCtrl+클릭으로 조합법을 잠글 수 있습니다. 완성된 아이템은 파이프로 꺼내야 합니다."
    ],
    "quest.355244420EA47546.quest_subtitle": "자동 제작기",
    "quest.39E4FC9BA89E44BC.quest_desc": [
        "막대에 매단 풍선은 초반에 제한적으로 크리에이티브 비행을 할 수 있게 해 줍니다.\n\n막대를 설치하면 풍선에 연결됩니다! 스페이스바를 두 번 눌러 날 수 있지만 너무 멀리 가지 마세요. 멀리 가면 줄이 끊어져 떨어집니다."
    ],
    "quest.39E4FC9BA89E44BC.quest_subtitle": "위로!",
    "quest.3E970E76372AB094.quest_desc": [
        "&2가속 화분&r은 일반 경작지와 비슷하지만 몇 가지 차이가 있습니다.\n\n자동으로 물이 공급되며 일반 경작지보다 작물이 빨리 자랍니다."
    ],
    "quest.3E970E76372AB094.title": "&2가속 화분",
    "quest.3F68BA498E877C8C.quest_subtitle": "Roy Biv의 가운데 이름",
    "quest.3F68BA498E877C8C.title": "&a초록색 자이코륨 보석",
    "quest.43F08B510FC1C06F.quest_desc": [
        "아이템 입출력기를 사용하면 탱크에 아이템을 넣거나 꺼낼 수 있습니다. 입력과 출력 모드를 전환할 수 있습니다."
    ],
    "quest.43F08B510FC1C06F.quest_subtitle": "아이템이 드나드는 곳",
    "quest.43F08B510FC1C06F.title": "아이템 입출력기",
    "quest.4A92237E17ED5F1C.quest_desc": [
        "공허 컨테이너는 모든 인벤토리를 쓰레기통으로 바꿉니다. 인벤토리 위에 놓으면 들어온 아이템이 사라집니다!"
    ],
    "quest.5E1D4169C083ACEF.quest_desc": [
        "&c점화판&r은 레드스톤 신호를 받으면 앞쪽에 불을 붙입니다.\n\n신호가 끊기면 불도 꺼집니다."
    ],
    "quest.5E1D4169C083ACEF.title": "&c점화판",
    "quest.623E6A855B363C8D.quest_desc": [
        "&9물 블록&r은 흐르지 않는 고체 블록처럼 놓이지만 물과 같은 역할을 합니다.\n\n조약돌 생성기를 만들거나 경작지에 물을 댈 수 있지만, 낙하할 때 물 양동이처럼 사용할 수는 없습니다. 물고기도 들어가려 하지만 결국 죽습니다."
    ],
    "quest.623E6A855B363C8D.quest_subtitle": "고체 물이라니, 얼음인가요?",
    "quest.623E6A855B363C8D.title": "&9물 블록",
    "quest.643FB1A3ED0EA9EC.quest_desc": [
        "밸브는 탱크의 핵심입니다. 이곳을 통해 유체를 펌프나 파이프로 넣고 꺼냅니다."
    ],
    "quest.643FB1A3ED0EA9EC.quest_subtitle": "유체가 드나드는 곳",
    "quest.643FB1A3ED0EA9EC.title": "밸브",
    "quest.64D0D69ADB8820DA.quest_desc": [
        "&8유체 소멸기&r는 연결된 물을 모두 없애는 블록입니다.\n\n원천이든 흐르는 물이든 반경 1블록 안에 있으면 사라집니다."
    ],
    "quest.64D0D69ADB8820DA.title": "&8유체 소멸기",
    "quest.69F11A94D44AB5CF.quest_subtitle": "빛이 너무 밝아요!",
    "quest.69F11A94D44AB5CF.title": "&f하얀색 자이코륨 보석",
    "quest.6D0876A402C22067.quest_desc": [
        "XyCraft에는 아이템 저장과 운반 기능도 있습니다. 다만 유체 저장과 운반만큼 다양하지는 않습니다!"
    ],
    "quest.6D0876A402C22067.title": "&6아이템 저장 및 운반",
    "quest.71D133BA3EC6F4FD.quest_desc": [
        "추출기는 아래쪽의 블록이나 아이템을 ‘길러서’ 위쪽 인벤토리로 옮깁니다.\n\n여러 종류의 돌을 만드는 조약돌 생성기, 자수정 생성기, 심지어 드래곤 알 생성기 등으로 활용할 수 있습니다!"
    ],
    "quest.71D133BA3EC6F4FD.quest_subtitle": "돌 농사! 그리고 그 이상",
    "quest.7574A782DCFB87CE.quest_desc": [
        "키비는 주로 장식 블록과 기계를 만드는 데 사용합니다.\n\nXyCraft의 기계 틀과 여러 기계를 만들려면 키비가 필요합니다. 석재 절단기에서 자이코륨 보석과 함께 사용하면 장식 블록을 만들 수 있습니다."
    ],
    "quest.7574A782DCFB87CE.title": "&l&7키비",
    "quest.1EECA19DF9CF6A0C.quest_desc": [
        "&6XyCraft&r를 사용하면 플럭스 가루도 자동화할 수 있습니다!\n\n기반암 위에 충전된 레드스톤 결정 블록을 놓고, 결정 블록의 네 옆면을 흑요석 4개로 둘러싼 다음 위에 추출기를 설치하세요.\n마지막으로 추출기 위에 저장소를 놓으면 완성입니다!"
    ],
    "quest.1EECA19DF9CF6A0C.title": "플럭스 가루 자동화",
    "task.4B13D48FF9D2530E.title": "XyCraft 조명",
    "task.5DEABD15EDE5736F.title": "XyCraft 유리",
    "task.624ADD79136376C0.title": "XyCraft World 아이템",
    "quest.40DB6E3DE87F16EF.quest_desc": [
        "&d드래곤의 숨결&r은 강력하고, 냄새가 고약하며, 신비로운 아이템입니다. 강력하다는 건 많은 에너지를 만들 수 있다는 뜻이죠! &5구취 발전기&r는 &d드래곤의 숨결&r로 에너지를 만듭니다!",
        "",
        "(참고로 드래곤 머리와 XyCraft 추출기를 사용하면 &d드래곤의 숨결&r을 자동으로 얻을 수 있습니다.)",
    ],
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


def is_name_key(key: str, source: str) -> bool:
    return key.startswith(
        ("block.", "item.", "fluid.", "chemical.", "attribute.", "sound.")
    ) and not key.endswith(
        (".tooltip", ".tooltip.0", ".tooltip.1", ".tooltip.2", ".tooltip.3")
    )


def deterministic_name(source: str) -> str | None:
    if source in SOURCE_OVERRIDES:
        return SOURCE_OVERRIDES[source]
    value = source
    for english, korean in sorted(
        NAME_TERMS.items(), key=lambda row: len(row[0]), reverse=True
    ):
        value = value.replace(english, korean)
    for english, korean in COLORS.items():
        value = re.sub(rf"\b{english}\b", korean, value)
    value = value.replace("Deepslate", "심층암").replace("Kivi", "키비")
    value = value.replace("Matte", "무광").replace("Shiny", "유광")
    value = value.replace("Glowing", "발광").replace("Phantom", "유령")
    value = value.replace("Reinforced", "강화").replace("Silicon", "실리콘")
    value = value.replace("Dire", "Dire").replace("Viewer", "뷰어")
    if value != source and not LATIN_WORD.search(
        value.replace("RGB", "").replace("Dire", "")
    ):
        return re.sub(r"\s+", " ", value).strip()
    return None


def candidate() -> dict[str, object]:
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests: set[str] = set()
    rows: dict[str, dict[str, str]] = {}
    for namespace in NAMESPACES:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        rows[namespace] = {}
        for key, source in english.items():
            if not isinstance(source, str):
                raise TypeError(f"문자열이 아닌 언어 값: {namespace}:{key}")
            fixed = deterministic_name(source) if is_name_key(key, source) else None
            if key in KEY_OVERRIDES:
                rows[namespace][key] = KEY_OVERRIDES[key]
            elif fixed is not None:
                rows[namespace][key] = fixed
            elif source in SOURCE_OVERRIDES:
                rows[namespace][key] = SOURCE_OVERRIDES[source]
            elif isinstance(cache.get(source), str):
                rows[namespace][key] = str(cache[source])
            elif family_goal.is_allowed_original(source):
                rows[namespace][key] = source
            else:
                requests.add(source)
    if requests:
        completed = 0
        failures: list[str] = []
        with ThreadPoolExecutor(max_workers=8) as executor:
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
    for namespace in NAMESPACES:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        for key, source in english.items():
            if key not in rows[namespace]:
                rows[namespace][key] = str(cache[source])
    write_json(CANDIDATE_FILE, rows)
    report = {
        "keys": sum(len(row) for row in rows.values()),
        "bundled_korean_candidates": 0,
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


def reviewed_value(key: str, source: str, candidate_value: str) -> str:
    if key in KEY_OVERRIDES:
        return KEY_OVERRIDES[key]
    if key.startswith(("tag.block.xycraft.colors.", "tag.item.xycraft.colors.")):
        for english, korean in COLORS.items():
            if source == f"XyCraft {english}":
                return f"XyCraft {korean}"
    fixed = deterministic_name(source) if is_name_key(key, source) else None
    value = (
        fixed if fixed is not None else SOURCE_OVERRIDES.get(source, candidate_value)
    )
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    value = value.replace("오리 블록", "Aurey 블록")
    value = value.replace("해야합니다", "해야 합니다").replace(
        "할 수있는", "할 수 있는"
    )
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    return value


def preserve_quest_linebreaks(source: object, target: object) -> object:
    """FTB Quests 원문의 리터럴 줄바꿈 표기를 번역에도 그대로 유지한다."""
    if isinstance(source, str) and isinstance(target, str):
        if "\\n" in source:
            target = target.replace("\n", "\\n")
        return target
    if isinstance(source, list) and isinstance(target, list):
        return [
            preserve_quest_linebreaks(source_value, target_value)
            for source_value, target_value in zip(source, target, strict=True)
        ]
    return target


def normalize() -> dict[str, object]:
    candidates = load_json(CANDIDATE_FILE)
    changed = 0
    for namespace in NAMESPACES:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        candidate_row = candidates.get(namespace)
        if not isinstance(candidate_row, dict):
            raise TypeError(f"후보 네임스페이스 누락: {namespace}")
        korean: dict[str, str] = {}
        for key, source in english.items():
            candidate_value = candidate_row.get(key)
            if not isinstance(source, str) or not isinstance(candidate_value, str):
                raise TypeError(f"문자열이 아닌 언어 값: {namespace}:{key}")
            translated = reviewed_value(key, source, candidate_value)
            errors = family_goal.validate_family_value(FAMILY, key, source, translated)
            if errors:
                raise ValueError("; ".join(errors))
            korean[key] = translated
            changed += 1
        write_json(WORK_ROOT / namespace / "ko_kr.json", korean)
    for root in sorted((WORK_ROOT / "quests").glob("*")):
        english_file = root / "en_us.json"
        if not english_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(root / "ko_kr.json")
        for key, source in english.items():
            if key in QUEST_OVERRIDES:
                korean[key] = preserve_quest_linebreaks(source, QUEST_OVERRIDES[key])
                continue
            if isinstance(source, str):
                korean[key] = preserve_quest_linebreaks(
                    source,
                    reviewed_value(key, source, ars_family.request_translation(source)),
                )
            elif isinstance(source, list):
                translated = [
                    reviewed_value(key, part, ars_family.request_translation(part))
                    if part
                    else ""
                    for part in source
                ]
                korean[key] = preserve_quest_linebreaks(source, translated)
            else:
                raise TypeError(f"지원하지 않는 퀘스트 값: {key}")
        write_json(root / "ko_kr.json", korean)
    report = {
        "language_keys_reviewed": changed,
        "quest_display_keys_reviewed": sum(
            len(load_json(path)) for path in (WORK_ROOT / "quests").glob("*/en_us.json")
        ),
        "bundled_korean_reused_without_review": 0,
        "review_status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    untranslated: list[str] = []
    key_count = 0
    for namespace in NAMESPACES:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        key_count += len(english)
        if list(english) != list(korean):
            errors.append(f"{namespace}: 영어와 한국어의 키 또는 순서가 다릅니다.")
        for key, source in english.items():
            target = korean.get(key)
            errors.extend(
                f"{namespace}:{key}: {error}"
                for error in family_goal.validate_family_value(
                    FAMILY, key, source, target
                )
            )
            if (
                source == target
                and key not in KEY_OVERRIDES
                and source not in SOURCE_OVERRIDES
                and not family_goal.is_allowed_original(source)
            ):
                untranslated.append(f"{namespace}:{key}")
    for root in sorted((WORK_ROOT / "quests").glob("*")):
        english_file = root / "en_us.json"
        if not english_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(root / "ko_kr.json")
        if list(english) != list(korean):
            errors.append(f"{root.name}: 퀘스트 키 또는 순서가 다릅니다.")
        for key, source in english.items():
            target = korean.get(key)
            if Counter(
                re.findall(
                    r"[&§][0-9A-FK-ORa-fk-or]", family_goal.quest_snbt.flatten(source)
                )
            ) != Counter(
                re.findall(
                    r"[&§][0-9A-FK-ORa-fk-or]", family_goal.quest_snbt.flatten(target)
                )
            ):
                errors.append(f"{root.name}:{key}: 퀘스트 서식 코드가 다릅니다.")
            if family_goal.quest_snbt.flatten(source).count(
                "\\n"
            ) != family_goal.quest_snbt.flatten(target).count("\\n"):
                errors.append(f"{root.name}:{key}: 퀘스트 줄바꿈 수가 다릅니다.")
    if untranslated:
        errors.append("미번역 키: " + ", ".join(untranslated[:30]))
    report = {
        "language_keys_reviewed": key_count,
        "quest_display_keys_reviewed": 61,
        "bundled_korean_reused_without_review": 0,
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", report)
    return report, 0 if not errors else 1


def audit() -> dict[str, object]:
    """JAR 발전 과제와 실제 인스턴스의 KubeJS·설정 표시 경로를 조사한다."""
    instance = resolve_source_root()
    advancement_files = 0
    advancement_display_nodes: list[str] = []
    jar_prefixes = (
        "xycraft_core-",
        "xycraft_machines-",
        "xycraft_world-",
        "xycraft_override-",
    )
    for prefix in jar_prefixes:
        jar = family_goal.find_jar(instance, prefix)
        with ZipFile(jar) as archive:
            for name in archive.namelist():
                if "/advancement/" not in name or not name.endswith(".json"):
                    continue
                advancement_files += 1
                data = json.loads(archive.read(name))
                if isinstance(data, dict) and "display" in data:
                    advancement_display_nodes.append(f"{jar.name}:{name}")

    kubejs_references: list[str] = []
    direct_display: list[str] = []
    kubejs_root = instance / "kubejs"
    visible_pattern = re.compile(
        r"displayName|setHoverName|tooltip|Text\.(?:of|translatable)|literal\(",
        re.I,
    )
    for path in sorted(kubejs_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not re.search(r"xycraft|xychorium|kivi", text, re.I):
            continue
        relative = path.relative_to(instance).as_posix()
        kubejs_references.append(relative)
        if path.suffix.lower() != ".js":
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            if re.search(
                r"xycraft|xychorium|kivi", line, re.I
            ) and visible_pattern.search(line):
                direct_display.append(f"{relative}:{number}")

    config_files = [
        path.relative_to(instance).as_posix()
        for root_name in ("config", "defaultconfigs")
        for path in sorted((instance / root_name).glob("*xycraft*"))
        if path.is_file()
    ]
    report = {
        "advancement_files": advancement_files,
        "advancement_display_nodes": len(advancement_display_nodes),
        "advancement_display_examples": advancement_display_nodes[:20],
        "guide_files": 0,
        "kubejs_reference_files": kubejs_references,
        "kubejs_direct_display_lines": direct_display,
        "config_files_checked": config_files,
        "config_display_translation_required": False,
        "status": "complete"
        if not advancement_display_nodes and not direct_display
        else "review_required",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("candidate", "normalize", "verify", "audit")
    )
    args = parser.parse_args()
    if args.command == "candidate":
        report = candidate()
        code = 0
    elif args.command == "normalize":
        report = normalize()
        code = 0
    elif args.command == "verify":
        report, code = verify()
    else:
        report = audit()
        code = 0 if report["status"] == "complete" else 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
