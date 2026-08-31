#!/usr/bin/env python3
"""Handcrafted와 Refurbished Furniture의 전체 표시 문자열을 번역하고 검증해요."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

FAMILY = "furniture"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
OUTPUT_ASSETS = active_output_root() / "resourcepack/ATM10_Korean/assets"
QUEST_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
MODS = {
    "handcrafted": ("handcrafted-neoforge-*.jar", 392),
    "refurbished_furniture": ("refurbished_furniture-neoforge-*.jar", 654),
}
OUTPUTS = {mod_id: OUTPUT_ASSETS / mod_id / "lang/ko_kr.json" for mod_id in MODS}
DEPLOYMENT_PATHS = {
    f"resourcepacks/ATM10_Korean/assets/{mod_id}/lang/ko_kr.json" for mod_id in MODS
} | {"config/ftbquests/quests/lang/ko_kr.snbt"}

PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[.]\d+)?")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")

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

WOODS = {
    "Acacia": "아카시아나무",
    "Bamboo": "대나무",
    "Birch": "자작나무",
    "Cherry": "벚나무",
    "Crimson": "진홍빛",
    "Dark Oak": "짙은 참나무",
    "Jungle": "정글나무",
    "Mangrove": "맹그로브나무",
    "Oak": "참나무",
    "Pale Oak": "창백한 참나무",
    "Spruce": "가문비나무",
    "Warped": "뒤틀린",
}

VARIANTS = {**COLORS, **WOODS}

HANDCRAFTED_SUFFIXES = {
    "Bench": "벤치",
    "Chair": "의자",
    "Corner Trim": "모퉁이 장식",
    "Couch": "소파",
    "Counter": "조리대",
    "Cupboard": "찬장",
    "Cushion": "쿠션",
    "Desk": "책상",
    "Dining Bench": "식탁 벤치",
    "Drawer": "서랍장",
    "Fancy Bed": "화려한 침대",
    "Nightstand": "협탁",
    "Pillar Trim": "기둥 장식",
    "Shelf": "선반",
    "Sheet": "시트",
    "Side Table": "보조 테이블",
    "Table": "테이블",
    "Bowl": "그릇",
    "Crockery Combo": "식기 세트",
    "Cup": "컵",
    "Plate": "접시",
    "Glazed Medium Pot": "유광 중형 단지",
    "Glazed Thick Pot": "유광 두꺼운 단지",
    "Glazed Thin Pot": "유광 얇은 단지",
    "Glazed Wide Pot": "유광 넓은 단지",
}

HANDCRAFTED_STATIC = {
    "Andesite Corner Trim": "안산암 모퉁이 장식",
    "Andesite Pillar Trim": "안산암 기둥 장식",
    "Bear Trophy": "곰 트로피",
    "Bench": "벤치",
    "Berry Jam Jar": "베리 잼 병",
    "Blackstone Corner Trim": "흑암 모퉁이 장식",
    "Blackstone Pillar Trim": "흑암 기둥 장식",
    "Blaze Trophy": "블레이즈 트로피",
    "Bricks Corner Trim": "벽돌 모퉁이 장식",
    "Bricks Pillar Trim": "벽돌 기둥 장식",
    "Calcite Corner Trim": "방해석 모퉁이 장식",
    "Calcite Pillar Trim": "방해석 기둥 장식",
    "Creeper Trophy": "크리퍼 트로피",
    "Deepslate Corner Trim": "심층암 모퉁이 장식",
    "Deepslate Pillar Trim": "심층암 기둥 장식",
    "Diorite Corner Trim": "섬록암 모퉁이 장식",
    "Diorite Pillar Trim": "섬록암 기둥 장식",
    "Dripstone Corner Trim": "점적석 모퉁이 장식",
    "Dripstone Pillar Trim": "점적석 기둥 장식",
    "Evoker Trophy": "소환사 트로피",
    "Fox Trophy": "여우 트로피",
    "Frozen Bench": "얼어붙은 벤치",
    "Goat Trophy": "염소 트로피",
    "Golden Medium Pot": "황금 중형 단지",
    "Golden Thick Pot": "황금 두꺼운 단지",
    "Golden Thin Pot": "황금 얇은 단지",
    "Golden Wide Pot": "황금 넓은 단지",
    "Granite Corner Trim": "화강암 모퉁이 장식",
    "Granite Pillar Trim": "화강암 기둥 장식",
    "Kitchen Hood": "주방 후드",
    "Kitchen Hood Pipe": "주방 후드 파이프",
    "Oven": "오븐",
    "Phantom Trophy": "팬텀 트로피",
    "Pillager Trophy": "약탈자 트로피",
    "Pufferfish Trophy": "복어 트로피",
    "Quartz Corner Trim": "석영 모퉁이 장식",
    "Quartz Pillar Trim": "석영 기둥 장식",
    "Red Sandstone Corner Trim": "붉은 사암 모퉁이 장식",
    "Red Sandstone Pillar Trim": "붉은 사암 기둥 장식",
    "Salmon Trophy": "연어 트로피",
    "Sandstone Corner Trim": "사암 모퉁이 장식",
    "Sandstone Pillar Trim": "사암 기둥 장식",
    "Silverfish Trophy": "좀벌레 트로피",
    "Skeleton Horse Trophy": "스켈레톤 말 트로피",
    "Skeleton Trophy": "스켈레톤 트로피",
    "Spider Trophy": "거미 트로피",
    "Stackable Book": "쌓을 수 있는 책",
    "Stone Corner Trim": "돌 모퉁이 장식",
    "Stone Pillar Trim": "돌 기둥 장식",
    "Terracotta Bowl": "테라코타 그릇",
    "Terracotta Crockery Combo": "테라코타 식기 세트",
    "Terracotta Cup": "테라코타 컵",
    "Terracotta Medium Pot": "테라코타 중형 단지",
    "Terracotta Plate": "테라코타 접시",
    "Terracotta Thick Pot": "테라코타 두꺼운 단지",
    "Terracotta Thin Pot": "테라코타 얇은 단지",
    "Terracotta Wide Pot": "테라코타 넓은 단지",
    "Tropical Fish Trophy": "열대어 트로피",
    "Vindicator Trophy": "변명자 트로피",
    "Witch Trophy": "마녀 트로피",
    "Wither Skeleton Trophy": "위더 스켈레톤 트로피",
    "Wolf Trophy": "늑대 트로피",
    "Wood Bowl": "나무 그릇",
    "Wood Crockery Combo": "나무 식기 세트",
    "Wood Cup": "나무 컵",
    "Wood Plate": "나무 접시",
    "Fancy Painting": "화려한 그림",
    "Hammer": "망치",
    "Seat": "좌석",
    "Handcrafted": "Handcrafted",
    "Kekie6": "Kekie6",
    "Ad Astra": "Ad Astra",
    "Apple": "사과",
    "Beach Sunrise Left": "해변의 일출(왼쪽)",
    "Beach Sunrise": "해변의 일출",
    "Beach Sunrise Right": "해변의 일출(오른쪽)",
    "Broken Birches": "부러진 자작나무",
    "Broken Birches Left Sidepanel": "부러진 자작나무(왼쪽 측면)",
    "Broken Birches Right Sidepanel": "부러진 자작나무(오른쪽 측면)",
    "Cookies on a Plate": "접시 위의 쿠키",
    "Coral Depths": "산호의 심해",
    "Desert Plateau": "사막 고원",
    "Green Woods": "푸른 숲",
    "Lava Puddles": "용암 웅덩이",
    "Marigold Meadows": "금잔화 들판",
    "Misty Mountain Left Sidepanel": "안개 낀 산(왼쪽 측면)",
    "Misty Mountain Right Sidepanel": "안개 낀 산(오른쪽 측면)",
    "Misty Mountains": "안개 낀 산맥",
    "My Man Diorite": "내 친구 섬록암",
    "Mysterious Mangroves": "신비로운 맹그로브",
    "Nian Cat": "니안 고양이",
    "Pride Steve": "프라이드 스티브",
    "Rocky Beach": "바위 해변",
    "Safari Sunset": "사파리의 노을",
    "Terrarium": "테라리움",
    "The Cat and the Cup": "고양이와 컵",
    "Stone is Hammered": "돌을 망치로 두드림",
    "Wood is Hammered": "나무를 망치로 두드림",
    "Bowls": "그릇",
    "Chairs": "의자",
    "Couches": "소파",
    "Counters": "조리대",
    "Crockery": "식기",
    "Crockery Combos": "식기 세트",
    "Cupboards": "찬장",
    "Cups": "컵",
    "Cushions": "쿠션",
    "Desks": "책상",
    "Dining Benches": "식탁 벤치",
    "Drawers": "서랍장",
    "Fancy Beds": "화려한 침대",
    "Nightstands": "협탁",
    "Plates": "접시",
    "Pots": "단지",
    "Sheets": "시트",
    "Shelves": "선반",
    "Side Tables": "보조 테이블",
    "Tables": "테이블",
    "Trims": "장식",
    "Trophies": "트로피",
    "Right-click with a cushion to change the bed's pillow color.": (
        "쿠션을 들고 우클릭하면 침대 베개 색상이 바뀝니다."
    ),
    "Right-click with a sheet to change the bedsheets.": (
        "시트를 들고 우클릭하면 침대 시트가 바뀝니다."
    ),
    "Right-click with wood or stone to change the counter surface.": (
        "나무나 돌을 들고 우클릭하면 조리대 상판이 바뀝니다."
    ),
    "Right-click with any item to place it on the plate.": (
        "아무 아이템이나 들고 우클릭하면 접시 위에 놓습니다."
    ),
    "Right-click with a cushion to change the block's look.": (
        "쿠션을 들고 우클릭하면 블록의 모습이 바뀝니다."
    ),
    "Changes the look of blocks.": "블록의 모습을 바꿉니다.",
    "Right-click with a hammer to change the block's look.": (
        "망치를 들고 우클릭하면 블록의 모습이 바뀝니다."
    ),
    "Shift-right-click with a hammer to change the block's look.": (
        "망치를 들고 Shift+우클릭하면 블록의 모습이 바뀝니다."
    ),
    "Right-click with a hammer to change the block's shape.": (
        "망치를 들고 우클릭하면 블록의 형태가 바뀝니다."
    ),
    "Can be placed on furniture.": "가구 위에 놓을 수 있습니다.",
    "Right-click with a sheet to change the block's look.": (
        "시트를 들고 우클릭하면 블록의 모습이 바뀝니다."
    ),
    "Hold SHIFT for more information": "자세한 정보를 보려면 Shift를 누르세요",
}

REFURBISHED_SUFFIXES = {
    "Kitchen Cabinetry": "주방 캐비닛",
    "Kitchen Drawer": "주방 서랍장",
    "Kitchen Sink": "주방 싱크대",
    "Kitchen Storage Cabinet": "주방 수납 캐비닛",
    "Toilet": "변기",
    "Basin": "세면대",
    "Bath": "욕조",
    "Grill": "그릴",
    "Cooler": "쿨러",
    "Sofa": "소파",
    "Lamp": "램프",
    "Trampoline": "트램펄린",
    "Stool": "스툴",
    "Table": "테이블",
    "Chair": "의자",
    "Desk": "책상",
    "Drawer": "서랍장",
    "Crate": "상자",
    "Cutting Board": "도마",
    "Mailbox": "우편함",
    "Storage Jar": "보관 병",
    "Light Ceiling Fan": "밝은색 천장 선풍기",
    "Dark Ceiling Fan": "어두운색 천장 선풍기",
    "Storage Cabinet": "보관 캐비닛",
    "Lattice Fence": "격자 울타리",
    "Lattice Fence Gate": "격자 울타리 문",
    "Hedge": "생울타리",
}

REFURBISHED_STATIC = {
    "Workbench": "작업대",
    "Light Toaster": "밝은색 토스터",
    "Dark Toaster": "어두운색 토스터",
    "Light Microwave": "밝은색 전자레인지",
    "Dark Microwave": "어두운색 전자레인지",
    "Light Stove": "밝은색 스토브",
    "Dark Stove": "어두운색 스토브",
    "Light Fridge": "밝은색 냉장고",
    "Dark Fridge": "어두운색 냉장고",
    "Frying Pan": "프라이팬",
    "Post Box": "우체통",
    "Doorbell": "초인종",
    "Light Lightswitch": "밝은색 조명 스위치",
    "Dark Lightswitch": "어두운색 조명 스위치",
    "Light Ceiling Light": "밝은색 천장 조명",
    "Dark Ceiling Light": "어두운색 천장 조명",
    "Light Electricity Generator": "밝은색 전기 발전기",
    "Dark Electricity Generator": "어두운색 전기 발전기",
    "Recycle Bin": "재활용통",
    "Light Range Hood": "밝은색 레인지 후드",
    "Dark Range Hood": "어두운색 레인지 후드",
    "Plate": "접시",
    "Azalea Hedge": "철쭉 생울타리",
    "Stone Stepping Stones": "돌 디딤돌",
    "Granite Stepping Stones": "화강암 디딤돌",
    "Diorite Stepping Stones": "섬록암 디딤돌",
    "Andesite Stepping Stones": "안산암 디딤돌",
    "Deepslate Stepping Stones": "심층암 디딤돌",
    "Television": "텔레비전",
    "Computer": "컴퓨터",
    "Door Mat": "현관 매트",
    "Milk": "우유",
    "Spatula": "뒤집개",
    "Knife": "칼",
    "Package": "소포",
    "Wrench": "렌치",
    "Television Remote": "텔레비전 리모컨",
    "Bread Slice": "빵 조각",
    "Toast": "토스트",
    "Sweet Berry Jam": "달콤한 열매 잼",
    "Sweet Berry Jam Toast": "달콤한 열매 잼 토스트",
    "Glow Berry Jam": "발광 열매 잼",
    "Glow Berry Jam Toast": "발광 열매 잼 토스트",
    "Sea Salt": "바다 소금",
    "Wheat Flour": "밀가루",
    "Dough": "반죽",
    "Cheese": "치즈",
    "Cheese Sandwich": "치즈 샌드위치",
    "Grilled Cheese": "구운 치즈 샌드위치",
    "Raw Vegetable Pizza": "익히지 않은 채소 피자",
    "Cooked Vegetable Pizza": "구운 채소 피자",
    "Vegetable Pizza Slice": "채소 피자 조각",
    "Raw Meat Pizza": "익히지 않은 고기 피자",
    "Cooked Meat Pizza": "구운 고기 피자",
    "Meat Pizza Slice": "고기 피자 조각",
    "MrCrayfish's Furniture Mod": "MrCrayfish's Furniture Mod",
    "General": "일반",
    "All your basics. Chairs, tables, and more": "기본 가구 모음: 의자, 테이블 등",
    "Bedroom": "침실",
    "Beds, desks, dressers, and more": "침대, 책상, 서랍장 등",
    "Kitchen": "주방",
    "Cupboards, counters, appliances, and more": "찬장, 조리대, 가전제품 등",
    "Bathroom": "욕실",
    "Toilets, basins, and more": "변기, 세면대 등",
    "Electronics": "전자 제품",
    "Lights, computers, generators and more": "조명, 컴퓨터, 발전기 등",
    "Outdoors": "야외",
    "Mailboxes, hedges, fences, and more": "우편함, 생울타리, 울타리 등",
    "Storage": "보관",
    "All furniture and decorations with storage": "수납공간이 있는 모든 가구와 장식",
    "Food": "음식",
    "Food and ingredients for cooking": "요리에 쓰는 음식과 재료",
    "Items": "아이템",
    "All items. Spatula, pans, toast, and more": "모든 아이템: 뒤집개, 팬, 토스트 등",
    "%1$s was sliced to death by a ceiling fan": (
        "%1$s이(가) 천장 선풍기에 베여 죽었습니다"
    ),
    "Drawer": "서랍장",
    "Crate": "상자",
    "Kitchen Drawer": "주방 서랍장",
    "Cooler": "쿨러",
    "Fridge": "냉장고",
    "Freezer": "냉동고",
    "Microwave": "전자레인지",
    "Stove": "스토브",
    "Mailbox": "우편함",
    "Electricity Generator": "전기 발전기",
    "Storage Cabinet": "보관 캐비닛",
    "Lightswitch": "조명 스위치",
    "Set Mailbox Name": "우편함 이름 설정",
    "Failed to update mailbox name": "우편함 이름을 바꾸지 못했습니다",
    "Mailboxes": "우편함",
    "Search...": "검색...",
    "Search mailboxes": "우편함 검색",
    "Enter message...": "메시지 입력...",
    "Package message": "소포 메시지",
    "Send": "보내기",
    "How To": "사용 방법",
    "Select a mailbox from the list. You can search for a mailbox by name, or a player by prefixing with @. Place items in package slots and optionally include a message. Click the send button to deliver the package.": (
        "목록에서 우편함을 선택하세요. 이름으로 우편함을 검색하거나, 플레이어 이름 앞에 "
        "@를 붙여 검색할 수 있습니다. 소포 칸에 아이템을 넣고 필요하면 메시지를 작성한 "
        "뒤 보내기 버튼을 누르세요."
    ),
    "Select a crafting recipe from the list and gather the required materials to craft the item. The workbench will search your inventory, its own storage, and neighboring storage blocks for materials.": (
        "목록에서 제작법을 선택하고 필요한 재료를 모으세요. 작업대는 플레이어 인벤토리, "
        "자체 보관함, 인접한 보관 블록에서 재료를 찾습니다."
    ),
    "Sent by %s": "보낸 사람: %s",
    "Right Click to Open": "우클릭하여 열기",
    "Set Doorbell Name": "초인종 이름 설정",
    "Doorbell Rang": "초인종 울림",
    "Online": "온라인",
    "Offline": "오프라인",
    "Overloaded": "과부하",
    "Fuel Empty": "연료 없음",
    "%s / %s": "%s / %s",
    "Recycle": "재활용",
    "Save": "저장",
    "Next Preset": "다음 사전 설정",
    "Previous Preset": "이전 사전 설정",
    "Missing power": "전력 없음",
    "Too far": "너무 멉니다",
    "Too many links": "연결이 너무 많습니다",
    "Already connected": "이미 연결되었습니다",
    "Invalid node": "잘못된 노드입니다",
    "Link will not be powered": "연결 대상에 전력이 공급되지 않습니다",
    "Link crosses to the outside of the powerable zone": (
        "연결선이 전력 공급 가능 구역 밖으로 나갑니다"
    ),
    "Ensure the block is receiving power from an %s. It can be connected using a %s.": (
        "블록이 %s에서 전력을 받는지 확인하세요. %s로 연결할 수 있습니다."
    ),
    "Inherited from Campfire Cooking": "모닥불 요리에서 가져옴",
    "%s %s %s": "%s %s %s",
    "Hold %s for Details": "자세히 보려면 %s 키를 누르세요",
    "SHIFT": "Shift",
    "Show All": "모두 표시",
    "You've reached your limit on Mailboxes": "설치할 수 있는 우편함 한도에 도달했습니다",
    "Mailboxes cannot be placed in this dimension": "이 차원에는 우편함을 놓을 수 없습니다",
    "Mailbox is disabled as it is not in an allowed dimension": (
        "허용되지 않은 차원에 있어 우편함을 사용할 수 없습니다"
    ),
    "Unknown Player": "알 수 없는 플레이어",
    "Unknown or invalid mailbox": "알 수 없거나 잘못된 우편함입니다",
    "The selected mailbox has reached its max mail queue": (
        "선택한 우편함의 우편 대기열이 가득 찼습니다"
    ),
    "The selected mailbox is in an undeliverable dimension": (
        "선택한 우편함이 배송할 수 없는 차원에 있습니다"
    ),
    "Package sent!": "소포를 보냈습니다!",
    "Booting...": "부팅 중...",
    "Sliceable": "자를 수 있음",
    "Placeable": "놓을 수 있음",
    "Ignore Neighbor Containers": "인접한 보관함 무시",
    "Include Neighbor Containers": "인접한 보관함 포함",
    "%s/%s Lvls": "%s/%s 레벨",
    "%s Points": "%s 포인트",
    "Withdraw Experience": "경험치 꺼내기",
    "Requires power from an %s": "%s의 전력이 필요합니다",
    "Cardboard Ripping": "종이상자 뜯김",
    "Wood Sliding": "나무 미끄러짐",
    "Doorbell Chime": "초인종 울림",
    "Generator": "발전기 작동음",
    "Item Shuffling": "아이템 뒤섞임",
    "Crushing": "분쇄",
    "Fan Spinning": "선풍기 회전",
    "Flick": "스위치 딸깍",
    "Bounce": "튀어 오름",
    "Super Bounce": "크게 튀어 오름",
    "High Pitch Tone": "고음 신호음",
    "White Noise": "백색 소음",
    "Dance Beat": "댄스 비트",
    "News Channel": "뉴스 채널",
    "Bird Chirping to Song": "새소리가 노래에 맞춰 울림",
    "LoFi Beat": "로파이 비트",
    "Piano Music": "피아노 음악",
    "Retro Arcade Song": "레트로 아케이드 음악",
    "Splat": "철퍼덕",
    "Metal Clang": "금속 쨍그랑",
    "Metal Hit": "금속 타격음",
    "Metal Place": "금속 놓임",
    "Metal Step": "금속 발걸음",
    "Sizzling": "지글거림",
    "Toaster Activated": "토스터 작동",
    "Toaster Pop": "토스트 튀어 오름",
    "Toaster Rattle": "토스터 덜컹거림",
    "Cooler Opened": "쿨러 열림",
    "Cooler Closed": "쿨러 닫힘",
    "Microwave Opened": "전자레인지 열림",
    "Microwave Closed": "전자레인지 닫힘",
    "Sliding Draw Opened": "미닫이 서랍 열림",
    "Sliding Draw Closed": "미닫이 서랍 닫힘",
    "Item Placed": "아이템 놓임",
    "Water Running": "물 흐름",
    "Fridge Open": "냉장고 열림",
    "Fridge Closed": "냉장고 닫힘",
    "Oven Open": "오븐 열림",
    "Oven Closed": "오븐 닫힘",
    "Freezer Open": "냉동고 열림",
    "Freezer Closed": "냉동고 닫힘",
    "Wooden Draw Open": "나무 서랍 열림",
    "Wooden Draw Closed": "나무 서랍 닫힘",
    "Item Constructed": "아이템 제작",
    "Node Highlighted": "노드 강조",
    "Link Removed": "연결 해제",
    "Link Connected": "연결 완료",
    "Hover Link": "연결선 가리킴",
    "Knife Chop": "칼질",
    "Spatula Scoop": "뒤집개로 퍼 올림",
    "Cabinet Door Open": "캐비닛 문 열림",
    "Cabinet Door Closed": "캐비닛 문 닫힘",
    "Microwave Hiss": "전자레인지 작동음",
    "Retro Click": "레트로 클릭음",
    "Retro Hit": "레트로 타격음",
    "Retro Success": "레트로 성공음",
    "Retro Fail": "레트로 실패음",
    "Retro Win": "레트로 승리음",
    "Retro Lose": "레트로 패배음",
    "Paddle Ball": "패들 볼",
    "Play vs AI": "AI와 대전",
    "Play vs Player": "플레이어와 대전",
    "Main Menu": "메인 메뉴",
    "You": "나",
    "You Win :)": "승리했습니다 :)",
    "You Lose :(": "패배했습니다 :(",
    "Finding an opponent...": "상대를 찾는 중...",
    "Opponent left the game": "상대가 게임을 떠났습니다",
    "Cancel": "취소",
    "Must be playing on a server": "서버에서 플레이해야 합니다",
    "Smart Home": "스마트 홈",
    "Toggle On": "모두 켜기",
    "Toggle Off": "모두 끄기",
    "HomeControl allows you to control the power of devices connected on an electricity network. The devices must be connected to the same network of the computer to be discoverable. Rename devices in an anvil before placing to make them more identifiable in the app.": (
        "HomeControl에서는 전력망에 연결된 장치의 전원을 제어할 수 있습니다. 장치를 찾으려면 "
        "컴퓨터와 같은 전력망에 연결해야 합니다. 앱에서 쉽게 구분할 수 있도록 설치하기 전에 "
        "모루에서 장치 이름을 바꾸세요."
    ),
    "Marketplace": "마켓플레이스",
    "Coin Miner": "코인 채굴기",
    "Solidifying": "응고",
    "Slicing": "썰기",
    "Frying": "프라이팬 조리",
    "Heating": "가열",
    "Recycling": "재활용",
    "Toasting": "굽기",
    "Grilling": "그릴 조리",
    "Combining": "조합",
    "Constructing": "제작",
    "Baking": "오븐 조리",
    "Fluid Transmuting": "유체 변환",
    "Open any Storage Cabinet in MrCrayfish's Furniture Mod to unlock this backpack": (
        "MrCrayfish's Furniture Mod의 아무 보관 캐비닛이나 열면 이 배낭이 잠금 해제됩니다"
    ),
}

QUEST_CORRECTIONS = {
    "quest.2B4801CD3E90BD40.quest_desc": [
        "&l&3Handcrafted&r는 실내 장식에 필요한 가구를 두루 추가합니다. "
        "\\n\\n침실에는 보기에도 편안한 침대와 협탁이 있습니다. 잠자리에 꽤 까다로운 "
        "저도 만족할 정도예요! \\n\\n거실에는 의자와 테이블이 있습니다. "
        "\\n\\n주방에는 오븐, 접시와 그릇이 있습니다. "
        "\\n\\n자랑하기 좋은 장식상까지 있습니다!"
    ],
    "quest.2B4801CD3E90BD40.title": "&l&3Handcrafted&r",
    "task.3C4997133CCECBE0.title": "Handcrafted",
    "quest.6012D6C3253895F0.quest_desc": [
        "&cMrCrayfish&r는 모드가 적용된 &2&lMinecraft&r를 대표하는 이름입니다. "
        "\\n\\n가장 많이 다운로드된 작품은 역시 Furniture Mod입니다! "
        "\\n\\n시작하려면 전력을 사용해 작동하는 작업대가 필요합니다."
    ],
    "quest.6012D6C3253895F0.title": ("&cMrCrayfish's Furniture Mod: Refurbished&c"),
    "quest.53CE66D760CEFD7E.quest_desc": [
        "싱크대, 변기와 욕조가 있습니다! \\n\\n몸을 깨끗하고 위생적으로 유지하는 데 필요한 "
        "모든 것이죠! \\n\\n모두 물을 담을 수 있으며, 변기에는 실제로 앉을 수도 있습니다."
    ],
    "quest.53CE66D760CEFD7E.title": "욕실 세트",
    "task.2828B5EAFCCB03E0.title": "욕실 세트",
    "quest.408F48C4442CE180.quest_desc": [
        "편안히 쉴 공간에 필요한 조명과 수납 가구를 넉넉히 제공합니다."
    ],
    "quest.408F48C4442CE180.title": "침실 세트",
    "task.767AF1D5EC4B4ECD.title": "침실 세트",
    "quest.1FDC8725105D822A.quest_desc": [
        "주방에는 음식을 보관하고 신선하게 유지하며 조리할 수 있는 블록이 많습니다! "
        "\\n\\n음식을 조리하거나 손질하는 블록 대부분은 전력이 필요하므로, 자세한 내용은 "
        "전력 설비를 확인하세요!"
    ],
    "quest.1FDC8725105D822A.title": "주방 세트",
    "task.02E980A373B13092.title": "주방 세트",
    "quest.655BD0A54AF1E1CA.quest_desc": [
        "실내 가구는 충분히 살펴봤으니 이제 야외는 어떨까요? 칠월 4일 바비큐를 실내에서 "
        "할 수는 없잖아요! \\n\\n야외 세트에는 그릴과 쿨러가 있으며, 손님이 도착했음을 "
        "알릴 수 있는 초인종도 있습니다!"
    ],
    "quest.655BD0A54AF1E1CA.title": "야외 세트",
    "task.293E660E52F15F10.title": "야외 세트",
    "quest.3E76BC1D0FC3E9A8.quest_desc": [
        "&cMrCrayfish's&r 모드의 많은 아이템은 전력을 사용합니다! "
        "\\n\\n전력을 공급하려면 전기 발전기가 필요합니다. 발전기는 석탄이나 다른 화로 "
        "연료를 사용합니다! \\n\\n그런 다음 렌치로 발전기와 전력이 필요한 블록을 연결하세요. "
        "\\n\\n발전기 위쪽의 스위치를 켜고 연료를 넣으면 연결된 모든 장치에 전력을 공급합니다."
    ],
    "quest.3E76BC1D0FC3E9A8.title": "전력 설비",
    "task.6A7ABDFC419B62A9.title": "전력 설비",
}

RELATED_QUEST_IDS = {
    "2B4801CD3E90BD40",
    "3C4997133CCECBE0",
    "6012D6C3253895F0",
    "53CE66D760CEFD7E",
    "2828B5EAFCCB03E0",
    "408F48C4442CE180",
    "767AF1D5EC4B4ECD",
    "1FDC8725105D822A",
    "02E980A373B13092",
    "655BD0A54AF1E1CA",
    "293E660E52F15F10",
    "3E76BC1D0FC3E9A8",
    "6A7ABDFC419B62A9",
}


def write_json(path: Path, value: object) -> None:
    """UTF-8 JSON 파일을 일정한 형식으로 써요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_json(path: Path) -> dict[str, object]:
    """JSON 객체를 읽어요."""
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 객체가 아니에요: {path}")
    return value


def sha256(path: Path) -> str:
    """파일 SHA-256 해시를 계산해요."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_jars(instance: Path) -> dict[str, Path]:
    """현재 설치본에서 정확히 한 개의 대상 JAR을 찾아요."""
    jars = {}
    for mod_id, (pattern, _count) in MODS.items():
        matches = sorted((instance / "mods").glob(pattern))
        if len(matches) != 1:
            raise FileNotFoundError(
                f"{mod_id} JAR이 정확히 한 개가 아니에요: {[p.name for p in matches]}"
            )
        jars[mod_id] = matches[0]
    return jars


def read_jar_language(jar: Path, mod_id: str, locale: str) -> dict[str, object]:
    """JAR에서 언어 파일을 읽어요. 없는 한국어 후보는 빈 객체로 처리해요."""
    name = f"assets/{mod_id}/lang/{locale}.json"
    with ZipFile(jar) as archive:
        if name not in archive.namelist():
            return {}
        value = json.loads(archive.read(name))
    if not isinstance(value, dict):
        raise TypeError(f"언어 파일이 JSON 객체가 아니에요: {jar.name}:{name}")
    return value


def translate_variant(source: str, suffixes: dict[str, str]) -> str | None:
    """목재·색상 접두사와 가구 종류를 결합해 번역해요."""
    for variant in sorted(VARIANTS, key=len, reverse=True):
        prefix = f"{variant} "
        if not source.startswith(prefix):
            continue
        suffix = source[len(prefix) :]
        if suffix in suffixes:
            return f"{VARIANTS[variant]} {suffixes[suffix]}"
    return None


def translate_handcrafted(source: str) -> str:
    """Handcrafted의 현재 영어 값을 검수된 규칙으로 번역해요."""
    translated = translate_variant(source, HANDCRAFTED_SUFFIXES)
    if translated is not None:
        return translated
    if source in HANDCRAFTED_STATIC:
        return HANDCRAFTED_STATIC[source]
    raise KeyError(f"Handcrafted 미검수 문구예요: {source!r}")


def translate_refurbished(source: str) -> str:
    """Refurbished Furniture의 현재 영어 값을 검수된 규칙으로 번역해요."""
    translated = translate_variant(source, REFURBISHED_SUFFIXES)
    if translated is not None:
        return translated
    if source in REFURBISHED_STATIC:
        return REFURBISHED_STATIC[source]
    raise KeyError(f"Refurbished Furniture 미검수 문구예요: {source!r}")


def prepare() -> dict[str, object]:
    """현재 JAR 영어 원문과 내장 한국어 후보를 작업 폴더에 기록해요."""
    instance = resolve_source_root()
    jars = find_jars(instance)
    rows = []
    candidate_sources = {}
    for mod_id, jar in jars.items():
        english = read_jar_language(jar, mod_id, "en_us")
        candidate = read_jar_language(jar, mod_id, "ko_kr")
        expected = MODS[mod_id][1]
        if len(english) != expected:
            raise ValueError(
                f"{mod_id} 영어 키 수가 달라요: 예상={expected}, 실제={len(english)}"
            )
        mod_root = WORK_ROOT / mod_id
        write_json(mod_root / "en_us.json", english)
        write_json(mod_root / "candidate_ko_kr.json", candidate)
        rows.append(
            {
                "mod_id": mod_id,
                "jar": jar.name,
                "jar_size": jar.stat().st_size,
                "jar_mtime_ns": jar.stat().st_mtime_ns,
                "english_keys": len(english),
                "bundled_korean_keys": len(candidate),
            }
        )
        candidate_sources[mod_id] = {
            "bundled_korean": f"{jar.name}:assets/{mod_id}/lang/ko_kr.json"
            if candidate
            else None,
            "policy": "현재 영어 원문과 대조해 값마다 재검수",
        }
    report = {
        "family": FAMILY,
        "mods": rows,
        "english_keys": sum(row["english_keys"] for row in rows),
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", report)
    write_json(WORK_ROOT / "candidate_sources.json", candidate_sources)
    return report


def build_quests(instance: Path) -> dict[str, object]:
    """관련 퀘스트 20키를 현재 전체 한국어 언어 파일에 병합해요."""
    candidate_path = instance / "config/ftbquests/quests/lang/ko_kr.snbt"
    candidate = quest_snbt.parse_language_snbt(candidate_path)
    merge_source = QUEST_OUTPUT if QUEST_OUTPUT.is_file() else candidate_path
    merged = quest_snbt.merge_into_full_snbt(merge_source, QUEST_CORRECTIONS)
    QUEST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    merged_values = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    for key, expected in QUEST_CORRECTIONS.items():
        if merged_values.get(key) != expected:
            raise ValueError(f"퀘스트 병합 결과가 달라요: {key}")
    reused = sum(
        candidate.get(key) == value for key, value in QUEST_CORRECTIONS.items()
    )
    existing = sum(key in candidate for key in QUEST_CORRECTIONS)
    return {
        "reviewed_keys": len(QUEST_CORRECTIONS),
        "existing_korean_reused": reused,
        "existing_korean_corrected": existing - reused,
        "new_translations": len(QUEST_CORRECTIONS) - existing,
    }


def build() -> dict[str, object]:
    """두 모드 1,046키 전체와 관련 퀘스트 산출물을 만들어요."""
    instance = resolve_source_root()
    jars = find_jars(instance)
    translators = {
        "handcrafted": translate_handcrafted,
        "refurbished_furniture": translate_refurbished,
    }
    rows = {}
    total_reused = 0
    total_new_or_corrected = 0
    for mod_id, jar in jars.items():
        english = read_jar_language(jar, mod_id, "en_us")
        candidate = read_jar_language(jar, mod_id, "ko_kr")
        korean = {}
        for key, source in english.items():
            if not isinstance(source, str):
                raise TypeError(f"{mod_id} 영어 값이 문자열이 아니에요: {key}")
            korean[key] = translators[mod_id](source)
        write_json(WORK_ROOT / mod_id / "ko_kr.json", korean)
        write_json(OUTPUTS[mod_id], korean)
        reused = sum(candidate.get(key) == value for key, value in korean.items())
        corrected = sum(
            key in candidate and candidate.get(key) != value
            for key, value in korean.items()
        )
        new = len(korean) - sum(key in candidate for key in korean)
        rows[mod_id] = {
            "reviewed_keys": len(korean),
            "existing_korean_reused": reused,
            "existing_korean_corrected": corrected,
            "new_translations": new,
        }
        total_reused += reused
        total_new_or_corrected += corrected + new
    quests = build_quests(instance)
    report = {
        "family": FAMILY,
        "mods": rows,
        "reviewed_language_keys": sum(row["reviewed_keys"] for row in rows.values()),
        "existing_korean_reused": total_reused,
        "new_or_corrected_language_keys": total_new_or_corrected,
        "quests": quests,
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def audit_jar_surfaces(jar: Path) -> tuple[dict[str, object], list[str]]:
    """발전 과제와 조합법의 사용자 표시 문구를 감사해요."""
    errors = []
    advancements = 0
    advancement_displays = []
    recipes = 0
    recipe_display_components = []

    def collect_components(value: object, path: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = f"{path}.{key}"
                if key in {
                    "custom_name",
                    "minecraft:custom_name",
                    "minecraft:item_name",
                }:
                    recipe_display_components.append(
                        {"path": child_path, "value": child}
                    )
                collect_components(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                collect_components(child, f"{path}[{index}]")

    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            if not name.endswith(".json"):
                continue
            if "/advancement" in name:
                advancements += 1
                value = json.loads(archive.read(name))
                display = value.get("display") if isinstance(value, dict) else None
                if display is not None:
                    advancement_displays.append({"path": name, "display": display})
            if "/recipe" in name:
                recipes += 1
                value = json.loads(archive.read(name))
                collect_components(value, name)
    if advancement_displays:
        errors.append(f"표시형 발전 과제가 있어요: {advancement_displays}")
    if recipe_display_components:
        errors.append(
            f"조합법에 직접 표시 구성요소가 있어요: {recipe_display_components}"
        )
    return {
        "advancement_files": advancements,
        "advancement_displays": advancement_displays,
        "recipe_files": recipes,
        "recipe_display_components": recipe_display_components,
    }, errors


def audit_references(instance: Path) -> dict[str, object]:
    """FTB Quests와 KubeJS에서 두 네임스페이스 참조를 모아요."""
    references = {"ftbquests": [], "kubejs": [], "read_errors": []}
    for label, base in (
        ("ftbquests", instance / "config/ftbquests"),
        ("kubejs", instance / "kubejs"),
    ):
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {
                ".snbt",
                ".json",
                ".js",
                ".txt",
            }:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                references["read_errors"].append(f"{path}: {exc}")
                continue
            namespaces = [mod_id for mod_id in MODS if f"{mod_id}:" in text]
            if not namespaces:
                continue
            visible_markers = sorted(
                marker
                for marker in (
                    "custom_name",
                    "displayName",
                    "customName",
                    "tooltip",
                    "lore",
                )
                if marker in text
            )
            references[label].append(
                {
                    "path": path.relative_to(instance).as_posix(),
                    "namespaces": namespaces,
                    "visible_markers_in_file": visible_markers,
                }
            )
    return references


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR·퀘스트·KubeJS의 전체 표시 표면을 감사해요."""
    instance = resolve_source_root()
    jars = find_jars(instance)
    errors = []
    jar_surfaces = {}
    for mod_id, jar in jars.items():
        report, report_errors = audit_jar_surfaces(jar)
        jar_surfaces[mod_id] = report
        errors.extend(report_errors)
    references = audit_references(instance)
    errors.extend(str(value) for value in references["read_errors"])

    english_quests = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean_quests = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    related_keys = sorted(
        key
        for key in english_quests
        if any(identifier in key for identifier in RELATED_QUEST_IDS)
    )
    if set(related_keys) != set(QUEST_CORRECTIONS):
        errors.append(
            "관련 퀘스트 키 범위가 예상과 달라요: "
            f"{sorted(set(related_keys) ^ set(QUEST_CORRECTIONS))}"
        )
    for key, expected in QUEST_CORRECTIONS.items():
        if korean_quests.get(key) != expected:
            errors.append(f"관련 퀘스트 번역값이 달라요: {key}")

    building = (
        instance / "config/ftbquests/quests/chapters/building_tips.snbt"
    ).read_text(encoding="utf-8")
    required_structure = {
        'id: "2B4801CD3E90BD40"',
        'id: "3C4997133CCECBE0"',
        'id: "6012D6C3253895F0"',
        'id: "01D63AEDEE43C288"',
        'id: "2828B5EAFCCB03E0"',
        'id: "767AF1D5EC4B4ECD"',
        'id: "02E980A373B13092"',
        'id: "293E660E52F15F10"',
        'id: "6A7ABDFC419B62A9"',
        'id: "handcrafted:yellow_crockery_combo"',
        'id: "refurbished_furniture:workbench"',
    }
    missing_structure = sorted(
        value for value in required_structure if value not in building
    )
    if missing_structure:
        errors.append(f"관련 퀘스트 구조를 찾지 못했어요: {missing_structure}")
    english_workbench_task = "task.01D63AEDEE43C288.title" in english_quests
    if english_workbench_task:
        errors.append("작업대 ItemTask에 중복 영어 task.title이 생겼어요")
    workbench_name = load_json(OUTPUTS["refurbished_furniture"]).get(
        "block.refurbished_furniture.workbench"
    )
    if workbench_name != "작업대":
        errors.append("작업대 ItemTask의 자동 아이템명이 확정 번역과 달라요")

    report = {
        "family": FAMILY,
        "jar_surfaces": jar_surfaces,
        "references": references,
        "related_quest_keys": related_keys,
        "workbench_item_task_uses_translated_item_fallback": not english_workbench_task,
        "natures_aura_refurbished_texture_reference_only": any(
            row["path"].endswith("natures_aura.snbt") for row in references["ftbquests"]
        ),
        "ftbquests_display_work": "complete",
        "kubejs_display_work": "recipe_ids_only",
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def validate_preserved(key: str, source: str, target: str) -> list[str]:
    """자리표시자·서식·숫자·줄바꿈을 원문과 비교해요."""
    errors = []
    for label, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식 코드", FORMAT_CODE),
        ("숫자", NUMBER),
    ):
        if pattern.findall(source) != pattern.findall(target):
            errors.append(
                f"{key} {label} 불일치: {pattern.findall(source)} != {pattern.findall(target)}"
            )
    for label, token in (("이스케이프 줄바꿈", "\\n"), ("실제 줄바꿈", "\n")):
        if source.count(token) != target.count(token):
            errors.append(
                f"{key} {label} 수 불일치: {source.count(token)} != {target.count(token)}"
            )
    return errors


def verify_mod(mod_id: str, jar: Path) -> tuple[dict[str, object], list[str]]:
    """한 모드의 키·값·보존 요소·영문 잔여와 이름 충돌을 검증해요."""
    errors = []
    english = read_jar_language(jar, mod_id, "en_us")
    work = load_json(WORK_ROOT / mod_id / "ko_kr.json")
    output = load_json(OUTPUTS[mod_id])
    translator = (
        translate_handcrafted if mod_id == "handcrafted" else translate_refurbished
    )
    expected = {
        key: translator(source)
        for key, source in english.items()
        if isinstance(source, str)
    }
    if list(english) != list(work) or list(english) != list(output):
        errors.append(f"{mod_id} 한국어 키 또는 순서가 영어와 달라요")
    if len(expected) != len(english):
        errors.append(f"{mod_id} 문자열이 아닌 영어 값이 있어요")
    if work != output or work != expected:
        errors.append(f"{mod_id} 작업본·산출물·확정 번역이 서로 달라요")

    untranslated = []
    latin_residue = {}
    collisions = defaultdict(list)
    allowed_latin = {
        "Ad",
        "Astra",
        "Handcrafted",
        "Kekie",
        "MrCrayfish",
        "Furniture",
        "Mod",
        "Shift",
        "AI",
        "HomeControl",
    }
    intentional_same = {
        "itemGroup.handcrafted.main",
        "painting.handcrafted.ad_astra.title",
        "itemGroup.refurbished_furniture",
        "gui.refurbished_furniture.node_count",
        "gui.refurbished_furniture.progress",
    }
    for key in english.keys() & output.keys():
        source = english[key]
        target = output[key]
        if not isinstance(source, str) or not isinstance(target, str):
            errors.append(f"{mod_id} 문자열이 아닌 값이 있어요: {key}")
            continue
        errors.extend(validate_preserved(key, source, target))
        if (
            source == target
            and key not in intentional_same
            and not key.endswith(".author")
        ):
            untranslated.append(key)
        stripped = PLACEHOLDER.sub("", FORMAT_CODE.sub("", target))
        residue = sorted(set(LATIN_WORD.findall(stripped)) - allowed_latin)
        if residue:
            latin_residue[key] = residue
        if key.startswith(("block.", "item.")) and ".info" not in key:
            collisions[target].append(key)
    unexpected_collisions = {
        target: keys
        for target, keys in collisions.items()
        if len(keys) > 1 and len({english[key] for key in keys}) > 1
    }
    if untranslated:
        errors.append(f"{mod_id} 영어 동일값이 남았어요: {untranslated}")
    if latin_residue:
        errors.append(f"{mod_id} 허용하지 않은 영문 잔여가 있어요: {latin_residue}")
    if unexpected_collisions:
        errors.append(f"{mod_id} 검색명이 충돌해요: {unexpected_collisions}")
    return {
        "keys": len(output),
        "untranslated_candidates": untranslated,
        "latin_residue": latin_residue,
        "unexpected_name_collisions": unexpected_collisions,
        "errors": errors,
    }, errors


def verify_quests(instance: Path) -> tuple[dict[str, object], list[str]]:
    """관련 퀘스트 20키의 값과 보존 요소를 확인해요."""
    errors = []
    english = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    latin_residue = {}
    allowed = {
        "Handcrafted",
        "MrCrayfish",
        "Minecraft",
        "Furniture",
        "Mod",
        "Refurbished",
    }
    for key, expected in QUEST_CORRECTIONS.items():
        if korean.get(key) != expected:
            errors.append(f"퀘스트 번역값이 달라요: {key}")
            continue
        errors.extend(quest_snbt.validate_value(key, english[key], expected))
        source_text = (
            "\n".join(english[key]) if isinstance(english[key], list) else english[key]
        )
        target_text = "\n".join(expected) if isinstance(expected, list) else expected
        errors.extend(validate_preserved(key, source_text, target_text))
        stripped = PLACEHOLDER.sub(
            "", FORMAT_CODE.sub("", target_text.replace("\\n", " "))
        )
        residue = sorted(set(LATIN_WORD.findall(stripped)) - allowed)
        if residue:
            latin_residue[key] = residue
    if latin_residue:
        errors.append(f"퀘스트에 허용하지 않은 영문 잔여가 있어요: {latin_residue}")
    return {
        "keys": len(QUEST_CORRECTIONS),
        "latin_residue": latin_residue,
        "errors": errors,
    }, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """두 모드·퀘스트·표면 감사 결과를 함께 검증해요."""
    instance = resolve_source_root()
    jars = find_jars(instance)
    mod_reports = {}
    errors = []
    for mod_id, jar in jars.items():
        report, report_errors = verify_mod(mod_id, jar)
        mod_reports[mod_id] = report
        errors.extend(report_errors)
    quests, quest_errors = verify_quests(instance)
    errors.extend(quest_errors)
    audit_report = load_json(WORK_ROOT / "surface_audit.json")
    audit_errors = audit_report.get("errors", [])
    if isinstance(audit_errors, list):
        errors.extend(str(value) for value in audit_errors)
    report = {
        "family": FAMILY,
        "mods": mod_reports,
        "language_keys": sum(row["keys"] for row in mod_reports.values()),
        "quests": quests,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "family_validation.json", report)
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = load_json(deployment_path) if deployment_path.is_file() else None
    completion = {
        "family": FAMILY,
        "language_keys": report["language_keys"],
        "quest_keys": quests["keys"],
        "surface_audit": audit_report.get("status"),
        "family_validation": report["status"],
        "deployment": deployment,
        "errors": errors,
        "status": "complete"
        if not errors
        and audit_report.get("status") == "complete"
        and (deployment is None or deployment.get("status") == "applied_and_verified")
        else "incomplete",
    }
    write_json(WORK_ROOT / "family_completion.json", completion)
    return report, errors


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 스크립트의 백업·해시 검증 결과를 작업 기록에 연결해요."""
    manifest_path = manifest_path.resolve()
    manifest = load_json(manifest_path)
    errors = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 매니페스트 상태가 완료가 아니에요")
    targets = manifest.get("targets")
    if not isinstance(targets, list) or not targets:
        errors.append("적용 대상 기록이 없어요")
        targets = []
    summarized = []
    for target in targets:
        if not isinstance(target, dict):
            errors.append("적용 대상 기록 형식이 잘못됐어요")
            continue
        records = {
            value.get("relative_path"): value
            for value in target.get("files", [])
            if isinstance(value, dict)
        }
        missing = sorted(DEPLOYMENT_PATHS - set(records))
        if missing:
            errors.append(f"적용 기록에 산출물이 없어요: {missing}")
        hash_errors = sorted(
            path
            for path in DEPLOYMENT_PATHS & set(records)
            if records[path].get("source_sha256") != records[path].get("after_sha256")
        )
        if hash_errors:
            errors.append(f"적용 후 해시가 달라요: {hash_errors}")
        if target.get("status") != "applied_and_verified":
            errors.append(
                f"적용 대상 상태가 완료가 아니에요: {target.get('target_root')}"
            )
        if target.get("unexpected_changes"):
            errors.append(
                f"예상 밖 적용 변경이 있어요: {target.get('unexpected_changes')}"
            )
        summarized.append(
            {
                "target_type": target.get("target_type"),
                "target_root": target.get("target_root"),
                "changed_paths": target.get("changed_paths", []),
                "unexpected_changes": target.get("unexpected_changes", []),
                "hash_verified_paths": sorted(
                    path
                    for path in DEPLOYMENT_PATHS & set(records)
                    if records[path].get("source_sha256")
                    == records[path].get("after_sha256")
                ),
            }
        )
    try:
        relative_manifest = manifest_path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        relative_manifest = str(manifest_path)
    report = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "backup_manifest": relative_manifest,
        "targets": summarized,
        "errors": errors,
    }
    write_json(WORK_ROOT / "deployment_report.json", report)
    verify_report, verify_errors = verify()
    return {
        "deployment": report,
        "verification": verify_report["status"],
    }, errors + verify_errors


def run_all() -> tuple[dict[str, object], list[str]]:
    """준비·생성·표면 감사·검증을 순서대로 실행해요."""
    prepared = prepare()
    built = build()
    audit_report, audit_errors = audit()
    verify_report, verify_errors = verify()
    errors = audit_errors + verify_errors
    return {
        "prepare": prepared,
        "build": built,
        "audit": audit_report,
        "verify": verify_report,
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
