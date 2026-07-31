#!/usr/bin/env python3
"""Deeper and Darker 1.4.1 언어 369키의 검수 번역 규칙이다."""

from __future__ import annotations

import re

EXACT_TRANSLATIONS = {
    "Deep below the bedrock, the darkness awaits": "기반암 깊은 아래에서 어둠이 기다립니다",
    "Below the Bedrock": "기반암 아래",
    "Explore all Otherside biomes": "이면세계의 모든 생물군계를 탐험하세요",
    "Echolocation": "반향 정위",
    "Find an Ancient City": "고대 도시를 찾으세요",
    "A Metropolis of Restless Souls": "잠들지 못한 영혼의 대도시",
    "Explore the depths for a temple": "깊은 곳에서 사원을 찾으세요",
    "Abyssal Descent": "심연으로의 하강",
    "Kill one of every Sculk monster": "모든 종류의 스컬크 몬스터를 하나씩 처치하세요",
    "Sculk Slayer": "스컬크 사냥꾼",
    "Slay the Warden and take its heart": "워든을 처치하고 심장을 얻으세요",
    "Phantom Thief": "괴도",
    "Reinforce an Echo Shard": "메아리 조각을 강화하세요",
    "Sculk Engineer": "스컬크 기술자",
    "Acquire a Sculk Transmitter": "스컬크 송신기를 얻으세요",
    "Remote Storage": "원격 저장소",
    "Acquire a Sonorous Staff": "울림 지팡이를 얻으세요",
    "Noise Complaint": "소음 민원",
    "You feel something pulling you toward the source...": (
        "무언가가 근원으로 당신을 끌어당기는 느낌입니다..."
    ),
    "Sculk Story": "스컬크 이야기",
    "Protect yourself with a full set of Warden Armor": (
        "워든 갑옷 한 벌을 모두 갖춰 몸을 보호하세요"
    ),
    "Cover Me with Sculk": "스컬크로 날 감싸 줘",
    "Blooming Caverns": "개화 동굴",
    "Deeplands": "심연지대",
    "Echoing Forest": "메아리 숲",
    "Overcast Columns": "음침한 기둥",
    "Ancient Vase": "고대 항아리",
    "Blooming Moss Block": "개화 이끼 블록",
    "Blooming Sculk Stone": "개화 스컬크 돌",
    "Blooming Stem": "개화목 줄기",
    "Bordered Block of Lite": "테두른 라이트 블록",
    "Crystallized Amber": "결정화된 호박석",
    "Enriched Gloomslate Bricks": "강화된 암흑석 벽돌",
    "Flowerless Ice Lily": "꽃 없는 얼음 수련",
    "Gleam Gel Block": "광휘 젤 블록",
    "Gloomslate Light": "암흑석 조명",
    "Gloomslate Pot": "암흑석 화분",
    "Gloomy Cactus": "음울한 선인장",
    "Gloomy Geyser": "음울한 간헐천",
    "Gloomy Grass": "음울한 잔디",
    "Gloomy Sculk": "음울한 스컬크",
    "Glowing Flowers": "빛나는 꽃",
    "Glowing Grass": "빛나는 잔디",
    "Glowing Roots": "빛나는 뿌리",
    "Glowing Roots Plant": "빛나는 뿌리 식물",
    "Glowing Vines": "빛나는 덩굴",
    "Glowing Vines Plant": "빛나는 덩굴 식물",
    "Ice Lily": "얼음 수련",
    "Infested Sculk": "벌레 먹은 스컬크",
    "Lily Flower": "수련꽃",
    "Linked transmitter": "연결된 송신기",
    "Block of Lite": "라이트 블록",
    "The linked block is missing or unloaded": "연결한 블록이 없거나 불러오지 않았습니다",
    "Cannot link to block": "이 블록에는 연결할 수 없습니다",
    "Otherside Portal": "이면세계 차원문",
    "Porous Sculk Gleam": "다공성 스컬크 광휘",
    "Potted Blooming Stem": "화분에 심은 개화목 줄기",
    "Potted Echo Sapling": "화분에 심은 메아리나무 묘목",
    "Sculk Gleam": "스컬크 광휘",
    "Sculk Grime Bricks": "스컬크 진흙 벽돌 블록",
    "Sculk Jaw": "스컬크 턱",
    "Sculk Tendrils": "스컬크 촉수",
    "Sculk Tendrils Plant": "스컬크 촉수 식물",
    "Sculk Vines": "스컬크 덩굴",
    "Sculk Vines Plant": "스컬크 덩굴 식물",
    "Soundproof Glass": "방음 유리",
    "Stripped Blooming Stem": "껍질 벗긴 개화목 줄기",
    "Unlinked transmitter": "연결되지 않은 송신기",
    "%s was devoured": "%s이(가) 잡아먹혔습니다",
    "%s was given a deadly case of tinnitus by %s": (
        "%s이(가) %s 때문에 치명적인 이명을 얻었습니다"
    ),
    "Sculk Affinity": "스컬크 친화",
    "Sculk Omen": "스컬크 흉조",
    "Catalysis": "촉매 작용",
    "Spreads sculk when mobs are killed.": "몹을 처치하면 주변에 스컬크를 퍼뜨립니다.",
    "Reverberation": "잔향",
    "Increases the range of sonic blasts.": "음파 충격파의 사거리가 늘어납니다.",
    "Sculk Smite": "스컬크 강타",
    "Increases damage against sculk mobs such as Shattered and the Warden.": (
        "셰터드와 워든 같은 스컬크 몹에게 주는 피해가 늘어납니다."
    ),
    "Volume": "음량",
    "Increases damage from sonic blasts.": "음파 충격파의 피해가 늘어납니다.",
    "Anger Pot": "분노 항아리",
    "Angler Fish": "초롱아귀",
    "Fear Pot": "공포 항아리",
    "Sculk Centipede": "스컬크 지네",
    "Sculk Leech": "스컬크 거머리",
    "Sculk Snapper": "스컬크 스내퍼",
    "Shattered": "셰터드",
    "Shriek Worm": "비명 벌레",
    "Sludge": "슬러지",
    "Sorrow Pot": "슬픔 항아리",
    "Stalker": "스토커",
    "Ancient Compass": "고대 나침반",
    "Raw Angler Fish": "생 초롱아귀",
    "Cooked Angler Fish": "익힌 초롱아귀",
    "Bloom Berries": "개화 열매",
    "Dampens Vibrations": "진동 감쇠",
    "Gleam Gel": "광휘 젤",
    "Gloomsherd": "암흑 도자기 조각",
    "Grime Ball": "스컬크 진흙 덩어리",
    "Grime Brick": "스컬크 진흙 벽돌",
    "Heart of the Deep": "깊은 곳의 심장",
    "Lite": "라이트",
    "Reinforced Echo Shard": "강화된 메아리 조각",
    "Resonarium": "레조나리움",
    "Resonarium Plate": "레조나리움 판",
    "Sculk Bone": "스컬크 뼈",
    "Sculk Transmitter": "스컬크 송신기",
    "Smithing Template": "대장장이 형판",
    "Add Resonarium Plate": "레조나리움 판을 넣으세요",
    "Iron Equipment": "철 장비",
    "Add iron armor, weapon, or tool": "철 갑옷, 무기 또는 도구를 넣으세요",
    "Add Reinforced Echo Shard": "강화된 메아리 조각을 넣으세요",
    "Netherite Equipment": "네더라이트 장비",
    "Add netherite armor, weapon, or tool": "네더라이트 갑옷, 무기 또는 도구를 넣으세요",
    "Sonorous Staff": "울림 지팡이",
    "Soul Crystal": "영혼 수정",
    "Soul Dust": "영혼 가루",
    "Soul Elytra": "영혼 겉날개",
    "Boost available in %s": "%s 후 추진할 수 있습니다",
    "Press %s to boost": "%s 키를 눌러 추진하세요",
    "Boost disabled": "추진 비활성화",
    "Warden Carapace": "워든 갑각",
    "Potion of Glowing": "발광의 물약",
    "Lingering Potion of Glowing": "잔류형 발광의 물약",
    "Splash Potion of Glowing": "투척용 발광의 물약",
    "Arrow of Glowing": "발광의 화살",
    "Potion of Sculk Affinity": "스컬크 친화의 물약",
    "Lingering Potion of Sculk Affinity": "잔류형 스컬크 친화의 물약",
    "Splash Potion of Sculk Affinity": "투척용 스컬크 친화의 물약",
    "Arrow of Sculk Affinity": "스컬크 친화의 화살",
    "Boost Soul Elytra": "영혼 겉날개 추진",
    "Use Sculk Transmitter": "스컬크 송신기 사용",
    "Abstraction": "추상",
    "Adventure": "모험",
    "Back to Your Roots": "근본으로 돌아가기",
    "Clouds": "구름",
    "Echoer": "메아리꾼",
    "Millipede": "노래기",
    "Ooze": "점액",
    "Warden dreams": "워든이 꿈꿉니다",
    "The Otherside forebodes": "이면세계가 불길하게 울립니다",
    "Shears scrape": "가위가 긁힙니다",
    "Angler Fish dies": "초롱아귀가 죽습니다",
    "Angler Fish flops": "초롱아귀가 퍼덕입니다",
    "Angler Fish hurts": "초롱아귀가 다칩니다",
    "Sculk Leech hurts": "스컬크 거머리가 다칩니다",
    "Shattered growls": "셰터드가 으르렁거립니다",
    "Shattered dies": "셰터드가 죽습니다",
    "Shattered hurts": "셰터드가 다칩니다",
    "Shattered takes notice": "셰터드가 눈치챕니다",
    "Shriek Worm cries": "비명 벌레가 울부짖습니다",
    "Shriek Worm dies": "비명 벌레가 죽습니다",
    "Shriek Worm hurts": "비명 벌레가 다칩니다",
    "Sludge attacks": "슬러지가 공격합니다",
    "Sludge dies": "슬러지가 죽습니다",
    "Sludge hurts": "슬러지가 다칩니다",
    "Sludge squishes": "슬러지가 철퍽거립니다",
    "Sculk Snapper breathes": "스컬크 스내퍼가 숨 쉽니다",
    "Sculk Snapper bites": "스컬크 스내퍼가 깨뭅니다",
    "Sculk Snapper hurts": "스컬크 스내퍼가 다칩니다",
    "Sculk Snapper sniffs": "스컬크 스내퍼가 킁킁거립니다",
    "Stalker chirps": "스토커가 울음소리를 냅니다",
    "Stalker dies": "스토커가 죽습니다",
    "Stalker hurts": "스토커가 다칩니다",
    "Stalker takes notice": "스토커가 눈치챕니다",
    "Warden looms nearby": "근처에 워든의 기척이 느껴집니다",
    "Staff booms": "지팡이가 굉음을 냅니다",
    "Transmitter fails": "송신기가 작동하지 않습니다",
    "Transmitter links": "송신기가 연결됩니다",
    "Transmitter transmits": "송신기가 전송합니다",
    "Transmitter unlinks": "송신기 연결이 해제됩니다",
    "Blooming Stems": "개화목 줄기",
    "Echo Logs": "메아리나무 원목",
    "Gloomslate Sherds": "암흑 도자기 조각",
    "Resonarium Armor": "레조나리움 갑옷",
    "Scutes": "갑각판",
    "Sonic Weapons": "음파 무기",
    "Transmitter": "송신기",
    "Contains %s": "%s이(가) 들어 있습니다",
    "Contains Sculk Leech": "스컬크 거머리가 들어 있습니다",
    "Linked to %s": "%s에 연결됨",
    "Located at %s, %s, %s": "위치: %s, %s, %s",
    "Dimension: %s": "차원: %s",
    "Unlinked": "연결되지 않음",
    "Resonarium Upgrade": "레조나리움 업그레이드",
    "Warden Upgrade": "워든 업그레이드",
}

KEEP_ORIGINAL = {"Deeper and Darker", "Pedro Ricardo"}

WOOD_SUFFIXES = {
    "Boat with Chest": "상자가 실린 {wood} 보트",
    "Chest Boat": "상자가 실린 {wood} 보트",
    "Hanging Sign": "{wood} 매달린 표지판",
    "Pressure Plate": "{wood} 감압판",
    "Fence Gate": "{wood} 울타리 문",
    "Spawn Egg": "{wood} 생성 알",
    "Button": "{wood} 버튼",
    "Door": "{wood} 문",
    "Fence": "{wood} 울타리",
    "Leaves": "{wood} 나뭇잎",
    "Log": "{wood} 원목",
    "Planks": "{wood} 판자",
    "Sapling": "{wood} 묘목",
    "Sign": "{wood} 표지판",
    "Slab": "{wood} 반 블록",
    "Stairs": "{wood} 계단",
    "Trapdoor": "{wood} 다락문",
    "Wood": "{wood} 나무",
    "Boat": "{wood} 보트",
}

STONE_BASES = {
    "Gloomslate": "암흑석",
    "Sculk Stone": "스컬크 돌",
    "Sculk Grime": "스컬크 진흙",
}
STONE_PREFIXES = {
    "Chiseled": "조각된",
    "Cobbled": "조약돌",
    "Cut": "깎인",
    "Polished": "윤나는",
    "Smooth": "매끄러운",
}
STONE_SUFFIXES = {
    "Brick Fence": "벽돌 울타리",
    "Brick Slab": "벽돌 반 블록",
    "Brick Stairs": "벽돌 계단",
    "Brick Wall": "벽돌 담장",
    "Bricks": "벽돌",
    "Tile Slab": "타일 반 블록",
    "Tile Stairs": "타일 계단",
    "Tile Wall": "타일 담장",
    "Tiles": "타일",
    "Coal Ore": "석탄 광석",
    "Copper Ore": "구리 광석",
    "Diamond Ore": "다이아몬드 광석",
    "Emerald Ore": "에메랄드 광석",
    "Gold Ore": "금 광석",
    "Iron Ore": "철 광석",
    "Lapis Lazuli Ore": "청금석 광석",
    "Redstone Ore": "레드스톤 광석",
    "Slab": "반 블록",
    "Stairs": "계단",
    "Wall": "담장",
}

EQUIPMENT_SUFFIXES = {
    "Axe": "도끼",
    "Boots": "부츠",
    "Chestplate": "흉갑",
    "Helmet": "투구",
    "Hoe": "괭이",
    "Leggings": "레깅스",
    "Pickaxe": "곡괭이",
    "Plate": "판",
    "Shovel": "삽",
    "Sword": "검",
}

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

GLOOMSHERD_MOTIFS = {
    "Brittle": "깨짐",
    "Dark Heart": "어두운 심장",
    "Listener": "경청",
    "Snapper": "스내퍼",
    "Temple": "사원",
    "Transmission": "전송",
    "Ward": "수호",
    "Wayfinder": "길잡이",
}

POT_NAMES = {"Anger": "분노", "Fear": "공포", "Sorrow": "슬픔"}


def _translate_stone(source: str) -> str | None:
    """암흑석·스컬크 돌·스컬크 진흙 계열 이름을 같은 순서로 번역한다."""
    for english_base, korean_base in STONE_BASES.items():
        match = re.fullmatch(
            rf"(?:(Chiseled|Cobbled|Cut|Polished|Smooth) )?{re.escape(english_base)}"
            r"(?: (.+))?",
            source,
        )
        if not match:
            continue
        prefix, suffix = match.groups()
        if prefix == "Cobbled":
            result = (
                "스컬크 조약돌"
                if english_base == "Sculk Stone"
                else f"{korean_base} 조약돌"
            )
        elif prefix:
            result = f"{STONE_PREFIXES[prefix]} {korean_base}"
        else:
            result = korean_base
        if suffix:
            translated_suffix = STONE_SUFFIXES.get(suffix)
            if translated_suffix is None:
                return None
            if english_base == "Sculk Stone" and (
                suffix.startswith("Brick")
                or suffix.startswith("Tile")
                or suffix.endswith("Ore")
            ):
                result = "스컬크"
            result = f"{result} {translated_suffix}"
        return result
    return None


def translate_name(source: str) -> str | None:
    """아이템·블록·엔티티·UI 이름을 검수된 규칙으로 번역한다."""
    if source in EXACT_TRANSLATIONS:
        return EXACT_TRANSLATIONS[source]
    if source in KEEP_ORIGINAL:
        return source
    if source == "Echo Wood":
        return "메아리 나무"

    for english_wood, korean_wood in {"Bloom": "개화목", "Echo": "메아리나무"}.items():
        for suffix, template in WOOD_SUFFIXES.items():
            if source == f"{english_wood} {suffix}":
                return template.format(wood=korean_wood)
    if source == "Stripped Echo Log":
        return "껍질 벗긴 메아리나무 원목"
    if source == "Stripped Echo Wood":
        return "껍질 벗긴 메아리 나무"
    if source == "Echo Soil":
        return "메아리 흙"

    translated = _translate_stone(source)
    if translated is not None:
        return translated

    for color, korean_color in COLORS.items():
        if source == f"{color} Sculk Transmitter":
            return f"{korean_color} 스컬크 송신기"

    for material, korean_material in {
        "Resonarium": "레조나리움",
        "Warden": "워든",
    }.items():
        for suffix, korean_suffix in EQUIPMENT_SUFFIXES.items():
            if source == f"{material} {suffix}":
                return f"{korean_material} {korean_suffix}"

    for entity, korean_entity in {
        "Angler Fish": "초롱아귀",
        "Sculk Centipede": "스컬크 지네",
        "Sculk Leech": "스컬크 거머리",
        "Sculk Snapper": "스컬크 스내퍼",
        "Shattered": "셰터드",
        "Shriek Worm": "비명 벌레",
        "Sludge": "슬러지",
        "Stalker": "스토커",
    }.items():
        if source == f"{entity} Spawn Egg":
            return f"{korean_entity} 생성 알"

    for emotion, korean_emotion in POT_NAMES.items():
        if source == f"{emotion} Pot Spawn Egg":
            return f"{korean_emotion} 항아리 생성 알"

    for motif, korean_motif in GLOOMSHERD_MOTIFS.items():
        if source == f"{motif} Gloomsherd":
            return f"{korean_motif} 암흑 도자기 조각"

    if source == "Resonarium Upgrade":
        return "레조나리움 업그레이드"
    if source == "Warden Upgrade":
        return "워든 업그레이드"
    return None
