#!/usr/bin/env python3
"""The Bumblezone 데이터 태그의 사용자 표시 이름을 일관되게 번역한다."""

from __future__ import annotations

import re


EXACT: dict[str, str] = {
    "Ancient Wax Full Blocks": "고대 밀랍 전체 블록",
    "Bumblezone Armors": "The Bumblezone 갑옷",
    "Bumblezone Boots": "The Bumblezone 부츠",
    "Bumblezone Chestplates": "The Bumblezone 흉갑",
    "Bumblezone Helmets": "The Bumblezone 투구",
    "Bumblezone Leggings": "The Bumblezone 레깅스",
    "Bumblezone Wrath Activating Pickup Item": "주우면 The Bumblezone의 분노를 발동하는 아이템",
    "Bumblezone Armor Ability Enhancing Wearables": "The Bumblezone 갑옷 능력을 강화하는 착용 아이템",
    "Sapling from Dead Bush Bee Queen Trades": "마른 덤불을 묘목으로 바꾸는 여왕벌 거래",
    "Bee Queen Disallowed Bonus Trade Item": "여왕벌 보너스 거래에서 제외할 아이템",
    "Bee Queen Force Allowed Bonus Trade Item": "여왕벌 보너스 거래에 강제로 허용할 아이템",
    "Honey Buckets": "꿀 양동이",
    "Royal Jelly Buckets": "로열 젤리 양동이",
    "Bumblezone Candle Consumable Lightables": "The Bumblezone 양초에 소비되는 점화 아이템",
    "Bumblezone Candle Damageable Lightables": "The Bumblezone 양초에 내구도를 소모하는 점화 아이템",
    "Bumblezone Candle Infinite Lightables": "The Bumblezone 양초에 무한히 쓰는 점화 아이템",
    "Crystalline Flower Unable To Enchant": "결정꽃으로 마법을 부여할 수 없는 아이템",
    "Crystalline Flower Cannot Consume": "결정꽃이 소비할 수 없는 아이템",
    "Crystalline Flower Max xp Items": "결정꽃 경험치를 최대로 채우는 아이템",
    "Early Right Click Bumblezone Dim Teleporting Items": "The Bumblezone 차원 순간이동을 먼저 검사할 우클릭 아이템",
    "Right Click Beehive Bumblezone Dim Teleporting Items": "벌통에 우클릭해 The Bumblezone으로 순간이동하는 아이템",
    "Crouch Right Click Beehive Bumblezone Dim Teleporting Items": "벌통에 웅크려 우클릭해 The Bumblezone으로 순간이동하는 아이템",
    "Special Bumblezone Dim Teleporting Items": "The Bumblezone 차원 순간이동 전용 호환 아이템",
    "Bumblezone Dim Teleporting Projectile Armors": "The Bumblezone 순간이동 투사체의 대상이 되는 갑옷",
    "Bumblezone Dim Teleporting Projectile Held Items": "The Bumblezone 순간이동 투사체의 대상이 되는 손에 든 아이템",
    "Calming Arena's Drowned Held Items": "평온의 경기장 드라운드가 들 아이템",
    "Cleanses Honey Bee Leggings": "꿀벌 레깅스의 꽃가루를 씻는 아이템",
    "Luminescent Wax Light Channels": "빛이 켜진 발광 밀랍 통로",
    "Luminescent Wax Light Corners": "빛이 켜진 발광 밀랍 모서리",
    "Luminescent Wax Light Nodes": "빛이 켜진 발광 밀랍 마디",
    "Luminescent Wax Channels": "발광 밀랍 통로",
    "Luminescent Wax Corners": "발광 밀랍 모서리",
    "Luminescent Wax Nodes": "발광 밀랍 마디",
    "Beehemoth Luring": "비히모스를 유인하는 아이템",
    "Beehemoth Fast Luring": "비히모스를 빠르게 유인하는 아이템",
    "Honey Slime Luring": "꿀 슬라임을 유인하는 아이템",
    "Bumblezone Music Discs": "The Bumblezone 음반",
    "Honey Drunk Advancement Trigger Items": "꿀 마시기 발전 과제를 발동하는 아이템",
    "String Curtain Extending Items": "실 커튼을 늘리는 아이템",
    "Disallowed Bumblezone Structure Flower Loots": "The Bumblezone 구조물 꽃 전리품에서 제외할 아이템",
    "Bumblezone Cannons": "The Bumblezone 대포",
    "Bumblezone Shields": "The Bumblezone 방패",
    "Bumblezone Spears": "The Bumblezone 창",
    "Washing Items": "세척용 아이템",
    "Essence Items With Abilities": "능력이 있는 정수 아이템",
    "Bee Feedable Items": "벌에게 먹일 수 있는 아이템",
    "Bumblezone Candles": "The Bumblezone 양초",
    "Stingers": "벌침",
    "Super Candles": "대형 양초",
    "Converts Slime To Honey Slime Items": "슬라임을 꿀 슬라임으로 바꾸는 아이템",
    "Calming Essence Arena Drowned Held items": "평온의 정수 경기장 드라운드가 들 아이템",
    "Radiance Essence Cannot Repair": "광휘의 정수로 수리할 수 없는 아이템",
    "Life Essence Arena Armor Cannot Be Knocked Off": "생명의 정수 경기장에서 벗겨지지 않는 갑옷",
    "Bumblezone Banner Patterns": "The Bumblezone 현수막 무늬",
    "Suspicious Pile of Pollen Additional Brushes": "수상한 꽃가루 더미에 추가로 허용할 솔",
    "Valid Potions for Potion Candle Advancement": "물약 양초 발전 과제에 유효한 물약",
    "Pollens": "꽃가루",
    "Normal Cobblestones": "일반 조약돌",
    "Dedicated Modded Bee Queen Trade Tags": "전용 모드 여왕벌 거래 태그",
    "Quartz Glasses": "석영 유리",
    "Quartz Framed Glass Panes": "석영 틀 유리판",
    "Quartz Glass Panes": "석영 유리판",
    "Quartz Framed Glasses": "석영 틀 유리",
    "Iron Bulb Lantern": "철 전구 랜턴",
    "Terminite Bulb Lantern": "터미나이트 전구 랜턴",
    "Thallasium Bulb Lantern": "탈라시움 전구 랜턴",
    "Coffins": "관",
    "Dye Blocks": "염료 블록",
    "Graveyard Urns": "Graveyard 항아리",
    "Graveyard Small Urns": "Graveyard 작은 항아리",
    "Rockwools": "암면",
    "Soliciting Carpets": "호객 카펫",
    "Trapped Soliciting Carpets": "함정 호객 카펫",
    "Small Industrial Lamps": "소형 산업용 램프",
    "Nightlights Hanging Lights": "Night Lights 매달린 조명",
    "Nightlights Fairy Lights": "Night Lights 꼬마전구",
    "Nightlights Mushroom": "Night Lights 버섯",
    "Nightlights Octopi": "Night Lights 문어",
    "Nightlights Frogs": "Night Lights 개구리",
    "Lumen Paint Balls": "루멘 페인트볼",
    "Kitchen Floors": "주방 바닥",
    "Ornament Soul Lantern Blocks": "장식 영혼 랜턴 블록",
    "Ornament Lantern Blocks": "장식 랜턴 블록",
    "Paper Soul Lantern Blocks": "종이 영혼 랜턴 블록",
    "Paper Lantern Blocks": "종이 랜턴 블록",
    "Industrial Lamps": "산업용 램프",
    "Gliders": "글라이더",
    "Module Colors": "모듈 색상",
    "Silt Pots": "실트 화분",
    "Silt Shingles": "실트 지붕널",
    "Silt Shingle Stairs": "실트 지붕널 계단",
    "Silt Shingle Walls": "실트 지붕널 벽",
    "Silt Shingle Slabs": "실트 지붕널 반 블록",
    "Lamp Candelabras": "램프 촛대",
    "Umbrellas": "우산",
    "Chairs": "의자",
    "Beach Floats": "해변 튜브",
    "Neon Lights": "네온 조명",
    "Rain Boots": "장화",
    "Plastic Shovels": "플라스틱 삽",
    "Swampier Swamps Froglights": "Swampier Swamps 개구리불",
    "Fabric Bolts": "천 두루마리",
    "Arm Chairs": "안락의자",
    "Converts To Sugar Water Fluids": "설탕물로 바뀌는 액체",
    "Removes Pollen From Honeybee Leggings": "꿀벌 레깅스의 꽃가루를 제거하는 액체",
    "Special Honey-like Fluids": "특수 꿀 종류 액체",
    "Visual Honey Fluids": "시각적으로 꿀인 액체",
    "Visual Water Fluids": "시각적으로 물인 액체",
    "Silverfishes": "좀벌레",
    "Endermites": "엔더 진드기",
    "Cave Spiders": "동굴 거미",
    "Various Non-cave Spiders": "여러 종류의 비동굴 거미",
}

BOTANY_TIERS = {
    "Ultra": "울트라",
    "Elite": "엘리트",
    "Creative": "크리에이티브",
}

BOTANY_MATERIALS = {
    "Terracotta": "테라코타",
    "Glazed Terracotta": "유광 테라코타",
    "Concrete": "콘크리트",
}


def translate(source: str) -> str | None:
    """검수된 정확 일치와 제한된 반복 패턴만 번역한다."""
    if source in EXACT:
        return EXACT[source]
    xp_match = re.fullmatch(r"Crystalline Flower (\d+)xp Items", source)
    if xp_match:
        return f"결정꽃에 {xp_match.group(1)} XP를 주는 아이템"
    botany_match = re.fullmatch(
        r"(Ultra|Elite|Creative) (Terracotta|Glazed Terracotta|Concrete) "
        r"Botany Hopper Pots",
        source,
    )
    if botany_match:
        tier, material = botany_match.groups()
        return f"{BOTANY_TIERS[tier]} {BOTANY_MATERIALS[material]} 식물 호퍼 화분"
    return None
