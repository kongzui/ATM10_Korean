#!/usr/bin/env python3
"""LaserIO·MFFS 언어, 퀘스트와 Patchouli 안내서를 번역하고 검증한다."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import shutil
from pathlib import Path
from zipfile import ZipFile

import actually_additions_family as candidate_helper
import ars_family
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root


FAMILY = "laser_io_mffs"
WORK_ROOT = PROJECT_ROOT / "working/laser_io_mffs"
LANG_CACHE = PROJECT_ROOT / "temp/laser_io_mffs_language_candidate_cache_v1.json"
GUIDE_CACHE = PROJECT_ROOT / "temp/laser_io_mffs_guide_candidate_cache_v1.json"
LANG_CANDIDATES = WORK_ROOT / "auto_candidates.json"
GUIDE_ROOT = WORK_ROOT / "guides"
GUIDE_CANDIDATES = GUIDE_ROOT / "auto_candidates.json"
VISIBLE_FIELDS = {"name", "description", "text", "landing_text", "title", "heading"}
PROTECTED = re.compile(
    r"\$\([^)]*\)|%(?:\d+\$)?(?:\.\d+)?[A-Za-z%]|\{[^{}]*\}|"
    r"#[0-9A-Fa-f]{6}|\b(?:laserio|mffs|minecraft|mekanism):[a-z0-9_./-]+\b"
)
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")

TARGETS = {
    "laserio": {
        "jar_prefix": "laserio-",
        "book": "laseriobook",
        "source_prefix": "assets/laserio/patchouli_books/laseriobook/en_us/",
        "output": PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/laserio/patchouli_books/laseriobook/ko_kr",
    },
    "mffs": {
        "jar_prefix": "mffs-",
        "book": "handbook",
        "source_prefix": "assets/mffs/patchouli_books/handbook/en_us/",
        "output": PROJECT_ROOT
        / "output/resourcepack/ATM10_Korean/assets/mffs/patchouli_books/handbook/ko_kr",
    },
}

SOURCE_OVERRIDES = {
    "LaserIO": "LaserIO",
    "MFFS": "MFFS",
    "Modular Force Field Systems": "Modular Force Field Systems",
    "Laser Connector": "레이저 커넥터",
    "Advanced Laser Connector": "고급 레이저 커넥터",
    "Laser Node": "레이저 노드",
    "Laser Wrench": "레이저 렌치",
    "Logic Chip": "논리 칩",
    "Raw Logic Chip": "미가공 논리 칩",
    "Chemical Card": "화학 물질 카드",
    "Card Cloner": "카드 복제기",
    "Energy Card": "에너지 카드",
    "Fluid Card": "유체 카드",
    "Card Holder": "카드 보관함",
    "Item Card": "아이템 카드",
    "Redstone Card": "레드스톤 카드",
    "Basic Filter": "기본 필터",
    "Counting Filter": "수량 필터",
    "Mod Filter": "모드 필터",
    "Data Filter": "데이터 필터",
    "Tag Filter": "태그 필터",
    "Card Overclocker": "카드 오버클러커",
    "Node Overclocker": "노드 오버클러커",
    "Extract": "추출",
    "Insert": "삽입",
    "Sensor": "센서",
    "Stock": "재고 유지",
    "Sneaky": "접근 면",
    "Allow": "허용",
    "Deny": "차단",
    "Apply": "적용",
    "Alpha": "투명도",
    "Default": "기본값",
    "Enforced": "강제 적용",
    "Exact": "정확히",
    "Ignored": "무시",
    "Regulate": "수량 조절",
    "Round Robin: ": "순환 분배: ",
    "Strong": "강함",
    "Weak": "약함",
    "High": "높음",
    "Low": "낮음",
    "Settings": "설정",
    "NBT UI": "NBT 화면",
    "Wrench Alpha": "렌치 투명도",
    "Force Field": "역장",
    "Force Field Projector": "역장 프로젝터",
    "Force Field Handbook": "역장 안내서",
    "Base Machine Block": "기본 기계 블록",
    "Coercion Deriver": "강제 유도기",
    "Fortron Capacitor": "포트론 축전기",
    "Biometric Identifier": "생체 인식 식별기",
    "Interdiction Matrix": "차단 매트릭스",
    "Remote Controller": "원격 제어기",
    "Cube Mode": "정육면체 모드",
    "Sphere Mode": "구체 모드",
    "Tube Mode": "관 모드",
    "Pyramid Mode": "피라미드 모드",
    "Cylinder Mode": "원기둥 모드",
    "Custom Mode": "사용자 지정 모드",
    "Camouflage Module": "위장 모듈",
    "Capacity Module": "용량 모듈",
    "Disintegration Module": "분해 모듈",
    "Rotation Module": "회전 모듈",
    "Scale Module": "크기 모듈",
    "Speed Module": "속도 모듈",
    "Translation Module": "이동 모듈",
    "Glow Module": "발광 모듈",
    "Silence Module": "소음 제거 모듈",
    "Shock Module": "충격 모듈",
    "Sponge Module": "스펀지 모듈",
    "Field Fusion Module": "역장 융합 모듈",
    "Dome Module": "돔 모듈",
    "Collection Module": "수집 모듈",
    "Stabilization Module": "안정화 모듈",
    "Inverter Module": "반전 모듈",
    "Warn Module": "경고 모듈",
    "Block Alter Module": "블록 변경 차단 모듈",
    "Block Access Module": "블록 사용 차단 모듈",
    "Anti-Friendly Module": "우호적 몹 차단 모듈",
    "Anti-Hostile Module": "적대적 몹 차단 모듈",
    "Anti-Personnel Module": "플레이어 차단 모듈",
    "Anti-Spawn Module": "생성 차단 모듈",
    "Confiscation Module": "압수 모듈",
    "Focus Matrix": "초점 매트릭스",
    "Battery": "배터리",
    "Steel Compound": "강철 혼합물",
    "Steel Ingot": "강철 주괴",
    "Blank Card": "빈 카드",
    "Identification Card": "신원 카드",
    "Infinite Power Card": "무한 동력 카드",
    "Frequency Card": "주파수 카드",
    "Fortron": "포트론",
    "Upgrade": "업그레이드",
    "Operation": "사용법",
    "Usage": "사용법",
    "Crafting": "제작",
    "Getting Started": "시작하기",
    "Machines": "기계",
    "Tools": "도구",
    "Upgrade Modules": "업그레이드 모듈",
    "Projector Modes": "프로젝터 모드",
    "Projector Modules": "프로젝터 모듈",
    "Interdiction Modules": "차단 모듈",
    "Blocks": "블록",
    "Cards": "카드",
    "Filters": "필터",
    "Items": "아이템",
    "Card Mechanics": "카드 작동 방식",
    "Basics": "기초",
}

GUIDE_LOCATION_OVERRIDES = {
    "laserio/entries/basics.json.pages[0].text": (
        "손에 든 카드를 우클릭하면 설정 화면이 열립니다. "
        "$(l:laserio:laser_node)노드$(/l) 화면 안의 카드도 우클릭할 수 있습니다."
        "$(br2)삽입 모드:$(br)1. $(l:laserio:modes)모드$(/l)$(br)2. "
        "$(l:laserio:sneaky)접근 면$(/l)$(br)3. 필터$(br)4. "
        "$(l:laserio:overclocker_card)카드 오버클러커$(/l)$(br)5. "
        "$(l:laserio:priority)우선순위$(/l)$(br)6. $(l:laserio:channel)채널$(/l)"
        "$(br)7. $(l:laserio:redstonemode)레드스톤 모드$(/l)$(br)8. "
        "$(l:laserio:redstonechannel)레드스톤 채널$(/l)"
    ),
    "laserio/entries/basics.json.pages[2].text": (
        "추출 모드:$(br2)1. $(l:laserio:modes)모드$(/l)$(br)2. "
        "$(l:laserio:sneaky)접근 면$(/l)$(br)3. $(l:laserio:roundrobin)순환 분배$(/l)"
        "$(br)4. $(l:laserio:exact)정확히$(/l)$(br)5. 필터$(br)6. "
        "$(l:laserio:overclocker_card)카드 오버클러커$(/l)$(br)7. "
        "$(l:laserio:extractamount)추출량$(/l)$(br)8. "
        "$(l:laserio:tickspeed)틱 속도$(/l)$(br)9. $(l:laserio:channel)채널$(/l)"
    ),
    "laserio/entries/basics.json.pages[4].text": (
        "재고 유지 모드:$(br2)1. $(l:laserio:modes)모드$(/l)$(br)2. "
        "$(l:laserio:sneaky)접근 면$(/l)$(br)3. $(l:laserio:regulate)수량 조절$(/l)"
        "$(br)4. $(l:laserio:exact)정확히$(/l)$(br)5. 필터$(br)6. "
        "$(l:laserio:overclocker_card)카드 오버클러커$(/l)$(br)7. "
        "$(l:laserio:extractamount)추출량$(/l)$(br)8. "
        "$(l:laserio:tickspeed)틱 속도$(/l)$(br)9. $(l:laserio:channel)채널$(/l)"
    ),
    "laserio/entries/card_chemical.json.pages[0].text": (
        "화학 물질 카드는 Mekanism 탱크 같은 인벤토리 사이에서 화학 물질을 전송합니다.  "
        "Mekanism이 설치되어 있을 때만 사용할 수 있습니다."
        "$(br2)오버클러커별 수치는 다음 페이지에서 설명합니다."
    ),
    "laserio/entries/card_chemical.json.pages[1].text": (
        "오버클러커별 최대 mB/틱:$(br2)$(li)0개: 15,000mb/20t$(li)1개:  "
        "60,000mb/15t$(li)2개: 120,000mb/10t$(li)3개: 180,000mb/5t$(li)4개: "
        "240,000mb/1t"
    ),
    "laserio/entries/card_cloner.json.pages[0].text": (
        "카드 복제기로 한 카드의 설정을 다른 카드에 복사해 붙여넣을 수 있습니다! "
        "$(l:laserio:laser_node)레이저 노드$(/l) 화면에서 카드 복제기를 커서로 집은 뒤 "
        "카드를 좌클릭하면 설정을 복사합니다. $(br2)다른 카드를 우클릭하면 저장한 설정을 "
        "붙여넣습니다."
    ),
    "laserio/entries/card_cloner.json.pages[1].text": (
        "붙여넣을 때 필요한 $(l:laserio:overclocker_card)오버클러커$(/l)와 "
        "$(l:laserio:filters)필터$(/l)는 현재 사용 중인 "
        "$(l:laserio:card_holder)카드 보관함$(/l)에서 자동으로 꺼내거나 되돌려 놓습니다. "
        "플레이어 인벤토리에서는 꺼내지 않습니다.$(br2)필요한 아이템이 하나라도 없으면 "
        "붙여넣기 전체가 실패하며, 일부 설정만 붙여넣지는 않습니다."
    ),
    "laserio/entries/card_energy.json.pages[0].text": (
        "에너지 카드는 기계와 배터리 같은 인벤토리 사이에서 에너지를 전송합니다."
        "$(br2)에너지 카드는 다른 카드와 작동 방식이 조금 다르며 다음 페이지에서 설명합니다."
    ),
    "laserio/entries/card_energy.json.pages[1].text": (
        "아이템·유체 카드는 20틱보다 빠르게 작동하려면 오버클러커가 필요하지만, 에너지 "
        "카드는 기본적으로 매 틱 작동할 수 있습니다.$(br2)에너지 카드에는 오버클러커를 넣을 "
        "수 없습니다. 항상 최대 1,000,000 FE/tick으로 작동하며, 원한다면 이 한도를 낮출 수 "
        "있습니다."
    ),
    "laserio/entries/card_energy.json.pages[2].text": (
        "에너지 카드에는 '에너지 제한 %' 설정도 있습니다. 삽입·재고 유지 모드의 기본값은 "
        "100%이고 추출 모드는 0%입니다. 삽입·재고 유지 모드에서는 대상 에너지 저장소를 "
        "얼마나 채울지 정합니다. $(br2)예를 들어 용량이 1,000,000 FE일 때 50%로 설정하면 "
        "500,000FE까지만 채웁니다."
    ),
    "laserio/entries/card_energy.json.pages[3].text": (
        "추출 모드에서는 저장소에 남겨 둘 비율을 정합니다.$(br2)예를 들어 용량이 "
        "1,000,000FE인 에너지 셀에서 추출하면서 제한을 25%로 설정하면 250,000 FE 아래로는 "
        "추출하지 않습니다."
    ),
    "laserio/entries/card_energy.json.pages[4].text": (
        "기술 참고: Forge Energy 시스템은 약 21억 4천만 FE인 MAX_INT까지만 에너지 저장을 "
        "지원합니다. Draconic Evolution이나 Mekanism의 저장 장치는 Forge Energy의 작동 "
        "방식을 우회해 이보다 많은 에너지를 저장할 수 있습니다. 따라서 이 비율 표시는 "
        "21억 4천만 FE를 넘는 저장 장치에서는 작동하지 않습니다. 죄송합니다! :)"
    ),
    "laserio/entries/card_fluid.json.pages[0].text": (
        "유체 카드는 탱크 같은 인벤토리 사이에서 유체를 전송합니다."
        "$(br2)오버클러커별 수치는 다음 페이지에서 설명합니다."
    ),
    "laserio/entries/card_fluid.json.pages[1].text": (
        "오버클러커별 최대 mB/틱:$(br2)$(li)0개: 5,000mb/20t$(li)1개:  "
        "10,000mb/15t$(li)2개: 20,000mb/10t$(li)3개: 30,000mb/5t$(li)4개: "
        "40,000mb/1t"
    ),
    "laserio/entries/card_holder.json.pages[0].text": (
        "카드 때문에 생긴 인벤토리 문제는 카드 보관함으로 해결할 수 있습니다! 카드 보관함을 "
        "제작해 우클릭하면 화면이 열립니다. NBT 데이터가 같은 카드는 이 화면에서 64개까지 "
        "겹칠 수 있습니다. (참고: 카드를 단독으로 조합하면 NBT를 초기화할 수 있습니다.)"
    ),
    "laserio/entries/card_holder.json.pages[1].text": (
        "보관함 안의 카드 묶음을 우클릭하면 레이저 노드에서처럼 설정을 바꿀 수 있습니다."
        "$(br2)참고: 카드가 2개 이상 겹쳐 있으면 아이템 복제를 막기 위해 필터와 오버클러커 "
        "슬롯이 비활성화됩니다. #BlameSoaryn"
    ),
    "laserio/entries/card_holder.json.pages[2].text": (
        "카드 보관함을 Shift+우클릭하면 인벤토리의 카드를 자동으로 가져오기 시작합니다! "
        "활성화되면 카드 보관함이 마법 부여된 아이템처럼 빛납니다. 다시 Shift+우클릭하면 "
        "꺼집니다. 카드 보관함을 인벤토리에 둔 채 노드를 열면 보관함의 카드도 표시됩니다."
    ),
    "laserio/entries/card_holder.json.pages[3].text": (
        "참고: 필터와 오버클러커도 카드 보관함에 넣을 수 있습니다! 저장된 데이터가 없는 "
        "필터만 자동으로 들어갑니다. 필터를 단독으로 조합하면 저장된 데이터를 지울 수 "
        "있습니다.$(br2)데이터가 저장된 필터도 직접 넣을 수 있습니다."
    ),
    "laserio/entries/card_item.json.pages[0].text": (
        "아이템 카드는 상자와 화로 같은 인벤토리 사이에서 아이템을 전송합니다."
        "$(br2)오버클러커별 수치는 다음 페이지에서 설명합니다."
    ),
    "laserio/entries/card_item.json.pages[1].text": (
        "오버클러커별 최대 아이템/틱:$(br2)$(li)0개: 8 Items/20t$(li)1개:  "
        "16 Items/15t$(li)2개: 32 Items/10t$(li)3개: 48 Items/5t$(li)4개: "
        "64 Items/1t"
    ),
    "laserio/entries/card_redstone.json.pages[0].text": (
        "레드스톤 카드는 LaserIO 네트워크 전체에 레드스톤 신호를 전송합니다. "
        "$(br2)다른 카드가 쓰는 채널과 별개인 전용 '레드스톤 채널'을 사용합니다. "
    ),
    "laserio/entries/card_redstone.json.pages[1].text": (
        "레드스톤 카드에는 두 가지 모드가 있습니다:$(br2)$(bold)입력$()$(br)레드스톤 가루, "
        "레버, 버튼 등에서 레드스톤 신호를 받아 카드에 설정된 레드스톤 채널로 네트워크에 "
        "전송합니다.$(br2)$(bold)출력$()$(br)레드스톤 가루, 램프, 중계기 같은 블록에 "
        "레드스톤 신호를 보냅니다."
    ),
    "laserio/entries/card_redstone.json.pages[2].text": (
        "출력 모드에서는 약함과 강함을 선택할 수 있습니다. 약함은 레드스톤 가루처럼 바로 "
        "인접한 블록에만 신호를 보냅니다.$(br2)강함은 레버처럼 인접한 블록을 통과해 그 "
        "반대편 블록에도 신호를 전달합니다."
    ),
    "laserio/entries/card_redstone.json.pages[3].text": (
        "모든 카드에는 레드스톤 모드가 있으며, 기본값은 '무시'라서 항상 작동합니다."
        "$(br2)'낮음'에서는 레드스톤 채널에 신호가 없을 때만 작동합니다. 채널 버튼은 "
        "레드스톤 모드 버튼 오른쪽에 있습니다.$(br2)'높음'에서는 레드스톤 채널에 신호가 "
        "있을 때만 작동합니다."
    ),
    "laserio/entries/channel.json.pages[0].text": (
        "카드는 같은 채널의 카드하고만 상호 작용합니다. 따라서 하나의 네트워크에서 여러 "
        "물류 규칙을 함께 사용할 수 있습니다.$(br2)예를 들어 '주황색' 채널의 추출 카드는 "
        "주황색 채널의 삽입 카드로만 보내고 다른 카드는 무시합니다."
    ),
    "laserio/entries/channel.json.pages[1].text": (
        "예를 들어 조약돌 필터를 넣은 추출 카드를 '주황색 채널'로, 석탄 필터를 넣은 다른 "
        "추출 카드를 '검은색 채널'로 설정해 같은 노드에 넣습니다. $(br2)주황색 채널의 삽입 "
        "카드는 화로 위에, 검은색 채널의 삽입 카드는 아래에 놓을 수 있습니다. 그러면 "
        "조약돌은 화로 위쪽으로, 석탄은 아래쪽으로만 들어갑니다."
    ),
    "laserio/entries/exact.json.pages[0].text": (
        "'정확히'는 추출 및 재고 유지 모드에서만 사용할 수 있습니다.$(br2)이 모드를 켜면 "
        "'추출량'에 설정한 수량을 정확히 한 번에 추출합니다. 예를 들어 추출량이 8이고 "
        "인접한 상자에 아이템이 5개뿐이라면 8개가 모일 때까지 추출하지 않습니다."
    ),
    "laserio/entries/exact.json.pages[1].text": (
        "재고 유지 카드에서는 조금 다르게 작동합니다. 목표 재고까지 필요한 수량과 추출량 "
        "가운데 더 작은 수량이 네트워크에 있어야 옮깁니다.$(br2)예를 들어 재고 유지 카드에 "
        "13개가 더 필요하고 한 번에 32개를 추출할 수 있다면, 네트워크 어딘가에 13개가 "
        "있을 때만 추출합니다."
    ),
    "laserio/entries/extractamount.json.pages[0].text": (
        "추출량은 추출 및 재고 유지 모드에서만 사용할 수 있습니다.$(br2)작업 한 번에 추출할 "
        "아이템 수 또는 유체·FE 양을 정합니다.$(br2)예를 들어 20틱당 아이템 8개로 "
        "설정하면 추출 카드는 20틱마다 8개씩 추출합니다."
    ),
    "laserio/entries/extractamount.json.pages[1].text": (
        "추출 및 재고 유지 카드의 기본 추출량은 1, 최대는 8입니다. "
        "$(l:laserio:overclocker_card)카드 오버클러커$(/l)를 넣으면 다음 추출량을 사용할 수 "
        "있습니다:$(br)1. 16$(br)2. 32$(br)3. 48$(br)4. 64$(br2)한 번에 64개를 "
        "추출하려면 오버클러커 4개가 필요합니다."
    ),
    "laserio/entries/extractamount.json.pages[2].text": (
        "좌클릭하면 1 증가하고 우클릭하면 1 감소합니다. Shift를 누르면 변화량이 10배, "
        "Ctrl을 누르면 64배가 됩니다.$(br2)두 키를 함께 누르면 640배가 됩니다."
        "$(br2)예를 들어 Shift+우클릭하면 10 감소합니다."
    ),
    "laserio/entries/priority.json.pages[2].text": (
        "좌클릭하면 1 증가하고 우클릭하면 1 감소합니다. Shift를 누르면 변화량이 10배, "
        "Ctrl을 누르면 64배가 됩니다.$(br2)두 키를 함께 누르면 640배가 됩니다."
        "$(br2)예를 들어 Shift+우클릭하면 10 감소합니다."
    ),
    "laserio/entries/tickspeed.json.pages[2].text": (
        "좌클릭하면 1 증가하고 우클릭하면 1 감소합니다. Shift를 누르면 변화량이 10배, "
        "Ctrl을 누르면 64배가 됩니다.$(br2)두 키를 함께 누르면 640배가 됩니다."
        "$(br2)예를 들어 Shift+우클릭하면 10 감소합니다."
    ),
    "laserio/entries/filter_basic.json.pages[0].text": (
        "기본 필터는 인벤토리에 들어갈 수 있는 아이템을 제한합니다.$(br2)필터 슬롯은 실제 "
        "아이템을 보관하지 않고 아이템 모양만 기록하는 '고스트 슬롯'입니다."
    ),
    "laserio/entries/filter_basics.json.pages[0].text": (
        "필터를 우클릭하면 설정 화면이 열립니다. 카드 안에 넣은 필터도 카드 화면에서 설정할 "
        "수 있습니다.$(br2)필터는 삽입·추출·재고 유지할 아이템을 제한합니다."
        "$(br2)1. 허용 또는 차단$(br)2. NBT 비교$(br)3. 필터 슬롯"
    ),
    "laserio/entries/filter_basics.json.pages[2].text": (
        "허용 또는 차단$(br2)허용 모드에서는 필터에 등록한 아이템을 허용합니다. 예를 들어 "
        "삽입 카드는 조약돌을 받고, 추출 카드는 조약돌을 꺼낼 수 있습니다."
        "$(br2)차단 모드에서는 반대로 작동합니다."
    ),
    "laserio/entries/filter_basics.json.pages[3].text": (
        "NBT 비교$(br2)NBT 비교를 켜면 필터가 아이템의 NBT 태그도 확인합니다. 예를 들어 "
        "검의 손상도는 NBT에 저장되므로, 손상되지 않은 다이아몬드 검과 손상되거나 마법 "
        "부여된 검을 서로 다르게 취급합니다.$(br2)NBT 비교를 끄면 상태와 관계없이 모든 "
        "다이아몬드 검이 일치합니다. "
    ),
    "laserio/entries/filter_count.json.pages[0].text": (
        "수량 필터는 아이템 수를 지정하며 카드 모드에 따라 다르게 작동합니다.$(br2)수량은 "
        "1부터 4096까지 설정할 수 있습니다. 좌클릭하면 증가하고 우클릭하면 감소합니다. "
        "Shift나 Ctrl을 누르면 변화량이 각각 10 또는 64가 됩니다."
    ),
    "laserio/entries/filter_count.json.pages[1].text": (
        "재고 유지 카드에 넣으면 지정한 수량을 유지합니다. 예를 들어 조약돌 64개를 설정한 "
        "수량 필터를 쓰면 상자에 조약돌 64개를 유지합니다.$(br2)삽입 카드에 넣으면 추출 "
        "카드가 그 인벤토리로 보낼 수 있는 아이템 수를 제한합니다."
    ),
    "laserio/entries/filter_count.json.pages[2].text": (
        "추출 카드에 넣으면 지정한 수량을 남겨 둡니다. 예를 들어 조약돌 8개를 설정하면 "
        "상자에 마지막 8개를 남기고 나머지를 모두 꺼냅니다.$(br2)수량 필터에는 의미가 없는 "
        "차단 모드가 없으며 항상 허용 모드로 작동합니다. JEI 조작은 "
        "$(l:laserio:filter_basic)기본 필터$(/l)와 같습니다."
    ),
    "laserio/entries/filter_nbt.json.pages[0].text": (
        "NBT 필터의 화면과 기능은 $(l:laserio:filter_tag)태그 필터$(/l)와 비슷합니다."
        "$(br2)오른쪽 위 슬롯에 아이템을 넣으면 그 아이템의 NBT 태그 이름이 모두 표시됩니다. "
        "태그 필터와 같은 방법으로 목록에 추가하면 값과 관계없이 해당 태그를 가진 아이템을 "
        "필터링합니다."
    ),
    "laserio/entries/filter_nbt.json.pages[2].text": (
        "예를 들어 마법 부여된 아이템에는 약탈, 날카로움 등을 지정하는 'Enchantments' "
        "태그가 있습니다. 이 태그를 목록에 추가하면 모든 마법 부여 아이템을 걸러낼 수 "
        "있습니다.$(br2)적용된 마법의 종류와 관계없이 마법 부여된 검과 그렇지 않은 검을 "
        "서로 다른 인벤토리로 보낼 수 있습니다."
    ),
    "laserio/entries/filter_tag.json.pages[0].text": (
        "태그 필터는 자원의 태그를 기준으로 필터링합니다.$(br2)Minecraft는 태그로 비슷한 "
        "자원을 묶습니다. 예를 들어 철 주괴에는 금·구리·주석 주괴 등에도 붙는 "
        "'forge:ingots' 태그가 있습니다.$(br2)따라서 항목 하나만 등록해 모든 주괴를 "
        "분류할 수 있습니다!"
    ),
    "laserio/entries/filter_tag.json.pages[2].text": (
        "먼저 오른쪽 위 슬롯에 아이템을 넣습니다. 그 아이템의 태그 목록이 "
        "$(#0000ff)파란색$()으로 나타납니다. 원하는 태그를 선택하고 + 버튼을 누르세요. "
        "Shift를 누른 채 + 버튼을 누르면 모든 태그가 추가됩니다.$(br2)목록에서 태그를 "
        "제거하려면 선택한 뒤 - 버튼을 누르세요. $(br2)Shift+클릭으로 태그를 바로 추가하거나 "
        "제거할 수도 있습니다."
    ),
    "laserio/entries/filter_tag.json.pages[3].text": (
        "X 버튼은 목록 전체를 지웁니다.$(br2)목록은 '또는' 조건으로 작동하므로 목록의 태그 "
        "중 하나라도 일치하는 아이템이 필터링됩니다.$(br2)태그 필터는 NBT 비교를 지원하지 "
        "않습니다."
    ),
    "laserio/entries/filter_basic.json.pages[1].text": (
        "JEI가 설치되어 있다면 JEI의 아이템을 필터의 '고스트 슬롯'으로 드래그할 수 "
        "있습니다. JEI에서 아이템을 좌클릭한 채 필터 화면으로 끌어오세요."
    ),
    "laserio/entries/laser_node.json.pages[1].text": "상자와 상호 작용하는 노드",
    "laserio/entries/limit.json.pages[0].text": (
        "제한 %는 에너지 카드에서만 사용할 수 있습니다. 인접한 에너지 저장 블록을 기준으로 "
        "처리할 FE 비율을 정합니다.$(br2)재고 유지·삽입 모드의 삽입 제한과 추출 모드의 "
        "추출 제한 두 가지가 있습니다."
    ),
    "laserio/entries/limit.json.pages[2].text": (
        "$(l)추출 제한$()$(br2)기본값은 0%이며, 지정한 에너지 블록에 남겨 둘 양을 "
        "정합니다.$(br2)예를 들어 용량이 1,000,000 FE인 블록에서 50%로 설정하면 "
        "500,000fe가 남을 때까지 추출한 뒤 멈춥니다.$(br2)기본값 0%에서는 에너지를 모두 "
        "추출합니다."
    ),
    "laserio/entries/laser_connector.json.pages[0].text": (
        "$(l:laserio:laser_node)레이저 노드$(/l)는 "
        "$(l:laserio:laser_wrench)레이저 렌치$(/l)로 서로 직접 연결할 수 있지만 최대 거리는 "
        "8블록입니다. $(br2)레이저 커넥터를 값싼 중간 연결 지점으로 사용하면 여러 인벤토리를 "
        "잇는 네트워크를 만들 수 있습니다."
    ),
    "laserio/entries/laser_connector_advanced.json.pages[0].text": (
        "고급 레이저 커넥터는 $(l:laserio:laser_connector)레이저 커넥터$(/l)처럼 8블록 "
        "이내의 기본 커넥터와 노드에 연결됩니다. $(br2)고급 커넥터끼리는 하나의 상대와만 "
        "짝을 이룹니다. 두 고급 커넥터 사이의 연결 거리는 차원이 달라도 무제한입니다!"
    ),
    "laserio/entries/laser_connector_advanced.json.pages[2].text": (
        "이미 짝이 있는 고급 커넥터를 새 커넥터와 연결하면 기존 연결이 끊어지고 새 연결이 "
        "생깁니다. $(br2)$(l:laserio:laser_wrench)레이저 렌치$(/l)를 들고 커넥터를 바라보면 "
        "짝이 된 커넥터의 좌표가 표시됩니다."
    ),
    "laserio/entries/laser_connector_advanced.json.pages[4].text": (
        "고급 레이저 커넥터는 청크를 강제로 불러오지 않습니다. 청크 로딩은 직접 관리해야 "
        "하며, 불러오지 않은 청크의 노드는 작동하지 않습니다."
    ),
    "laserio/entries/laser_node.json.pages[0].text": (
        "레이저 노드는 인접한 블록과 상호 작용하는 LaserIO의 핵심 블록입니다. "
        "$(br2)$(l:laserio:card_item)아이템 카드$(/l) 같은 카드를 사용하면 인접한 블록과 "
        "아이템, 유체, 에너지 또는 레드스톤을 주고받을 수 있습니다."
    ),
    "laserio/entries/laser_node.json.pages[2].text": (
        "노드의 각 면에는 카드를 넣는 3x3 슬롯이 있습니다. 노드의 해당 면을 우클릭하면 "
        "화면이 열립니다. $(br2)원하는 면에 접근하기 어렵다면 위쪽 버튼으로 작업할 면을 "
        "바꿀 수 있습니다.$(br2)옆 그림에서는 노드가 서쪽 인벤토리와 상호 작용합니다. "
    ),
    "laserio/entries/laser_node.json.pages[6].text": (
        "$(l:laserio:laser_wrench)레이저 렌치$(/l)로 노드를 연결하면 멀리 떨어진 인벤토리도 "
        "연결할 수 있습니다. 연결 하나의 최대 거리는 8블록입니다.$(br2)노드가 더 멀리 "
        "떨어져 있다면 $(l:laserio:laser_connector)레이저 커넥터$()를 사용하세요."
    ),
    "laserio/entries/laser_wrench.json.pages[0].text": (
        "레이저 렌치는 여러 블록을 연결하는 데 주로 사용합니다.$(br2)"
        "$(l:laserio:laser_node)노드$(/l)나 $(l:laserio:laser_connector)커넥터$(/l)를 "
        "Shift+우클릭해 선택한 뒤 다른 블록을 우클릭하면 연결됩니다.$(br2)최대 연결 거리는 "
        "8블록입니다."
    ),
    "laserio/entries/modes.json.pages[0].text": (
        "모드는 카드의 기본 동작을 정합니다. 다음 페이지에서 각 모드를 설명합니다."
        "$(br2)아이템·유체·에너지 카드는 다음 세 가지 모드를 지원하며 아이템 카드를 예로 "
        "듭니다.$(br2)레드스톤 카드는 별도의 모드를 사용합니다."
    ),
    "laserio/entries/modes.json.pages[1].text": (
        "삽입 모드 카드는 추출 모드 카드가 꺼낸 대상이 들어갈 곳입니다."
        "$(br2)재고 유지 모드 카드는 삽입 모드 카드에서 대상을 가져옵니다."
    ),
    "laserio/entries/modes.json.pages[2].text": (
        "추출 모드 카드는 인접한 블록에서 대상을 꺼냅니다. 예를 들어 인접한 상자에서 "
        "아이템을 꺼내 삽입 카드로 보냅니다."
    ),
    "laserio/entries/modes.json.pages[3].text": (
        "재고 유지 모드 카드는 필터에 지정된 아이템을 찾아 같은 네트워크의 다른 삽입 "
        "노드에서 가져옵니다.$(br2)필터를 허용 모드로 설정해야 합니다."
    ),
    "laserio/entries/modes.json.pages[4].text": (
        "센서 카드는 대상을 옮기지 않습니다. 인접한 인벤토리를 검사해 내용이 필터와 "
        "일치하면 레드스톤 채널로 신호를 보냅니다.$(br2)센서 모드에는 필터가 필요합니다."
    ),
    "laserio/entries/oveclocker_node.json.pages[0].text": (
        "노드 오버클러커는 작동 방식이 조금 복잡합니다.$(br2)각 "
        "$(l:laserio:laser_node)노드$(/l)는 한 면에서 틱당 카드 하나만 처리합니다. "
        "$(br2)한 면에 추출 카드가 3개라면 첫 카드만 해당 틱에 작동하고, 첫 카드가 아무 "
        "작업도 하지 못했을 때만 두 번째 카드가 작동합니다."
    ),
    "laserio/entries/oveclocker_node.json.pages[2].text": (
        "노드 한 면에 설치한 노드 오버클러커 하나마다 틱당 처리할 카드가 하나씩 늘어납니다. "
        "최대 8개를 설치하면 슬롯 9개의 카드를 모두 처리할 수 있습니다. $(br2)삽입 카드는 "
        "$(l)$(#ff0000)오버클러커가 필요하지 않으며$(), $(l)추출 및 재고 유지 카드에만$() "
        "필요합니다."
    ),
    "laserio/entries/priority.json.pages[0].text": (
        "우선순위는 삽입 모드에서만 사용할 수 있습니다.$(br2)삽입 카드의 처리 순서를 "
        "정합니다. 기본값은 '가까운 곳부터'이며, 추출 카드는 가장 가까운 인벤토리부터 "
        "삽입을 시도합니다."
    ),
    "laserio/entries/priority.json.pages[1].text": (
        "삽입 카드의 우선순위를 바꾸면 먼저 들어갈 인벤토리를 정할 수 있습니다. 높은 값이 "
        "먼저이므로 10, 0, -10 순서입니다. $(br2)우선순위가 같으면 가까운 곳부터 처리합니다."
    ),
    "laserio/entries/redstonechannel.json.pages[0].text": (
        "카드에는 기본 채널과 별개인 '레드스톤 채널'이 있습니다.$(br2)이 채널의 레드스톤 "
        "신호가 카드에 영향을 줍니다. $(l:laserio:redstonemode)레드스톤 모드$(/l)와 "
        "$(l:laserio:card_redstone)레드스톤 카드$(/l) 항목을 참고하세요."
    ),
    "laserio/entries/redstonemode.json.pages[0].text": (
        "레드스톤 모드는 $(l:laserio:redstonechannel)레드스톤 채널$(/l)의 신호가 카드에 "
        "미치는 영향을 정합니다.$(br2)기본값은 $(bold)무시$()이며, 이때 카드는 레드스톤 "
        "신호와 관계없이 항상 작동합니다."
    ),
    "laserio/entries/redstonemode.json.pages[1].text": (
        "$(br2)'낮음'에서는 레드스톤 채널에 신호가 없을 때만 작동합니다. 채널 버튼은 "
        "레드스톤 모드 버튼 오른쪽에 있습니다.$(br2)'높음'에서는 레드스톤 채널에 신호가 "
        "있을 때만 작동합니다."
    ),
    "laserio/entries/roundrobin.json.pages[0].text": (
        "순환 분배는 추출 모드에서만 사용할 수 있습니다.$(br2)여러 삽입 카드에 아이템을 "
        "고르게 나눕니다.$(br2)세 가지 설정이 있습니다:$(br)1. 끄기$(br)2. 켜기$(br)3. "
        "강제 적용"
    ),
    "laserio/entries/roundrobin.json.pages[1].text": (
        "$(l)끄기$()에서는 순환 분배를 사용하지 않고 $(l:laserio:priority)우선순위$(/l)를 "
        "따릅니다. 첫 인벤토리가 가득 찬 뒤 두 번째 인벤토리로 보냅니다.$(br2)$(l)켜기$()"
        "에서는 우선순위 순서대로 보내면서 고르게 분배합니다.$(br2)상자가 3개라면 첫 묶음은 "
        "첫 상자, 두 번째 묶음은 두 번째 상자에 들어가는 식입니다."
    ),
    "laserio/entries/roundrobin.json.pages[2].text": (
        "$(l)강제 적용$()은 '켜기'와 같은 규칙을 따르지만, 목적지 하나가 가득 차면 다시 "
        "공간이 생길 때까지 추출 카드 전체가 멈춥니다.$(br2)참고: 일부 노드만 불러온 "
        "상태라면 청크 언로드 때문에 순환 분배 동작이 달라질 수 있습니다."
    ),
    "laserio/entries/sensormode.json.pages[0].text": (
        "센서 모드는 다른 모드와 달리 대상을 옮기지 않습니다. 인접한 인벤토리·탱크·셀의 "
        "내용이 필터와 일치하는지 확인하고, 일치하면 지정한 레드스톤 채널로 세기 15의 "
        "신호를 보냅니다.$(br2)필터가 없으면 아무 작업도 하지 않습니다."
    ),
    "laserio/entries/sensormode.json.pages[1].text": (
        "기본 필터는 수량과 관계없이 대상을 찾습니다. 예를 들어 조약돌을 등록하면 인접한 "
        "상자에 조약돌이 하나라도 있을 때 레드스톤 신호를 보냅니다.$(br2)조약돌이 1개든 "
        "1000개든 같습니다."
    ),
    "laserio/entries/sensormode.json.pages[2].text": (
        "수량 필터는 지정한 수량 이상인지 확인합니다. 예를 들어 조약돌 32개로 설정하면 "
        "32개, 33개, 34개 이상일 때 신호를 보냅니다.$(br2)'정확히'를 켜면 더 많거나 적은 "
        "경우에는 보내지 않고 정확히 32개일 때만 신호를 보냅니다."
    ),
    "laserio/entries/sensormode.json.pages[3].text": (
        "센서 모드에는 '그리고/또는' 버튼이 있습니다. '또는'에서는 앞의 규칙에 따라 필터 "
        "하나만 일치해도 됩니다.$(br2)예를 들어 조약돌 32개와 유리 16개를 등록했다면 둘 "
        "중 하나 또는 둘 다 만족할 때 신호를 보냅니다.$(br2)'그리고'에서는 모든 필터를 "
        "만족해야 하므로 조약돌 32개와 유리 16개가 모두 필요합니다."
    ),
    "laserio/entries/sensormode.json.pages[4].text": (
        "태그·모드 필터도 같은 원리로 작동합니다. 태그 필터를 '그리고'로 설정하면 한 "
        "아이템이 모든 태그와 일치하든 여러 아이템이 나눠서 일치하든, 내용물이 모든 태그를 "
        "만족해야 합니다.$(br2)여러 센서가 경쟁해 예기치 않은 결과가 나올 수 있으므로 한 "
        "면의 레드스톤 채널마다 센서 카드 하나만 사용하는 것이 좋습니다."
    ),
    "laserio/entries/settings_screen.json.pages[3].text": (
        "노드나 네트워크를 다른 네트워크에 연결할 때는 다음 규칙을 따릅니다.$(br2)한쪽만 "
        "색을 설정했고 다른 쪽은 기본값이면 설정한 색이 적용됩니다.$(br2)둘 다 색이 있다면 "
        "먼저 선택한 블록의 설정이 나중에 클릭한 블록으로 전달됩니다. 예를 들어 녹색 노드를 "
        "Shift+클릭한 뒤 파란색 노드를 클릭하면 파란색 노드가 녹색으로 바뀝니다. "
    ),
    "laserio/entries/settings_screen.json.pages[4].text": (
        "투명도 설정은 '투명도'와 '렌치 투명도' 두 가지입니다.$(br2)'투명도'는 블록 사이의 "
        "레이저에만 적용됩니다. 0이면 노드와 커넥터 사이의 레이저가 보이지 않습니다."
        "$(br2)플레이어가 렌치를 들면 '렌치 투명도' 값이 기본 투명도에 더해집니다."
    ),
    "laserio/entries/settings_screen.json.pages[5].text": (
        "예를 들어 투명도를 0, 렌치 투명도를 80으로 설정하면 렌치를 들었을 때만 레이저가 "
        "보입니다!$(br2)투명도를 80, 렌치 투명도를 200으로 설정하면 렌치를 들었을 때 더 "
        "밝게 보입니다. 합계가 255를 넘어도 자동으로 255로 제한됩니다."
    ),
    "laserio/entries/sneaky.json.pages[1].text": (
        "이 카드는 이제 화로의 '위쪽' 면으로 아이템을 넣습니다.$(br2)다른 카드를 '아래쪽 "
        "접근 면'으로 설정하면 화로 아래쪽에 연료를 넣을 수 있습니다."
    ),
    "laserio/entries/tickspeed.json.pages[0].text": (
        "틱 속도는 추출 및 재고 유지 모드에서만 사용할 수 있습니다.$(br2)카드가 얼마나 "
        "자주 작동할지 정합니다. 기본값 20틱이면 추출 카드는 20틱, 즉 1초마다 작동합니다."
    ),
    "laserio/entries/tickspeed.json.pages[1].text": (
        "추출 및 재고 유지 카드의 기본값과 최소값은 20, 최대값은 1200입니다. "
        "$(l:laserio:overclocker_card)카드 오버클러커$(/l)를 넣으면 다음 최소 틱 간격을 "
        "사용할 수 있습니다:$(br)1. 15$(br)2. 10$(br)3. 5$(br)4. 1$(br2)매 틱마다 "
        "아이템을 추출하려면 오버클러커 4개가 필요합니다."
    ),
    "mffs/entries/getting_started/gathering_resources.json.pages[0].text": (
        "역장을 만들려면 먼저 기본 자원을 구해야 합니다.$(br)MFFS 부품은 주로 "
        "$(5)강철 주괴$()로 만들며, 두 단계로 제작할 수 있습니다. 먼저 조합대에서 "
        "$(5)강철 혼합물$()을 만든 뒤 제련해 주괴로 만드세요."
    ),
    "mffs/entries/getting_started/introduction.json.pages[0].text": (
        "$(l)Modular Force Field Systems$()(MFFS)는 Minecraft에 $(3)역장$(), "
        "$(5)첨단 기계$(), $(6)방어 수단$()을 추가하는 모드입니다. 핵폭발이 집을 날려 "
        "버리거나 다른 사람이 비밀 기지에 들어오는 일에 지치셨나요? "
        "$(l)MFFS가 해결해 드립니다!$()"
    ),
    "mffs/entries/interdiction_modules/anti_friendly_module.json.pages[0].text": (
        "$(5)우호적 몹 차단 모듈$()은 $(l:mffs:machines/interdiction_matrix)차단 "
        "매트릭스$()에 넣는 선택 모듈입니다. 설치하면 스캔 범위에 들어온 양, 소, 주민 같은 "
        "우호적 엔티티를 감지해 거의 즉시 처치합니다. 플레이어와 적대적 몹은 피해를 입지 "
        "않습니다."
    ),
    "mffs/entries/interdiction_modules/anti_spawn_module.json.pages[0].text": (
        "$(5)생성 차단 모듈$()은 $(l:mffs:machines/interdiction_matrix)차단 매트릭스$()에 "
        "넣는 선택 모듈입니다. 설치하면 작동 범위 안에서 우호적·적대적 엔티티가 생성되지 "
        "않습니다. 다만 플레이어가 작동 범위 바로 밖에서 생성 알을 사용하면 보호 영역 "
        "안에도 엔티티를 생성할 수 있습니다."
    ),
    "mffs/entries/interdiction_modules/confiscation_module.json.pages[0].text": (
        "$(5)압수 모듈$()은 $(l:mffs:machines/interdiction_matrix)차단 매트릭스$()가 "
        "플레이어의 아이템을 자동으로 빼앗게 하는 선택 모듈입니다. 작동 범위 안의 플레이어 "
        "인벤토리를 검사해 금지된 아이템을 압수합니다. 손에 들었거나 장착했거나 인벤토리에 "
        "보관한 아이템 모두에 적용됩니다."
    ),
    "mffs/entries/interdiction_modules/warn_module.json.pages[0].text": (
        "$(5)경고 모듈$()을 $(l:mffs:machines/interdiction_matrix)차단 매트릭스$()의 "
        "매트릭스 슬롯에 넣으면 작동 범위 안의 권한 없는 모든 플레이어에게 주기적으로 "
        "경고를 보냅니다."
    ),
    "mffs/entries/machines/biometric_identifier.json.pages[2].text": (
        "$(9)생체 인식 식별기$()에 플레이어를 등록하려면 화면을 열고 $(2)권한$()이라고 "
        "표시된 왼쪽 위 슬롯에 $(l:mffs:tools/id_card)신원 카드$()를 넣습니다. 비어 있는 "
        "카드는 손에 들고 자신을 Shift+우클릭해 자신에게 할당하거나 다른 플레이어를 "
        "Shift+우클릭해 그 플레이어에게 할당할 수 있습니다."
    ),
    "mffs/entries/machines/biometric_identifier.json.pages[3].text": (
        "이제 화면 오른쪽 버튼으로 플레이어에게 줄 권한을 정합니다:$(li)$(bold)통과$(): "
        "웅크린 채 역장을 통과할 수 있습니다.$(li)$(bold)블록 설치·파괴$(): "
        "$(l:mffs:machines/interdiction_matrix)차단 매트릭스$()의 보호 영역 안에서 블록을 "
        "놓거나 부술 수 있습니다.$()"
    ),
    "mffs/entries/machines/biometric_identifier.json.pages[4].text": (
        "$(li)$(bold)블록 사용$(): 매트릭스 작동 범위 안의 블록 화면을 열 수 있습니다."
        "$(li)$(bold)보안 설정$(): 생체 인식 식별기와 사용자 권한을 설정할 수 있습니다."
        "$(li)$(bold)방어 우회$(): $(l:mffs:machines/interdiction_matrix)차단 매트릭스$()의 "
        "방어 제한을 무시합니다.$(li)$(bold)압수 우회$(): 차단 매트릭스가 아이템을 압수하지 "
        "않습니다.$()"
    ),
    "mffs/entries/machines/biometric_identifier.json.pages[5].text": (
        "$(li)$(bold)원격 제어$(): 식별기에 연결된 기계에 원격 제어기를 사용할 수 있습니다."
        "$(p)권한을 지정한 카드를 화면 아래쪽의 9개 슬롯 가운데 하나로 옮기면 설정이 "
        "끝납니다. 자신을 $(9)생체 인식 식별기$()의 소유자로 지정하려면 자신에게 할당한 "
        "$(l:mffs:tools/id_card)신원 카드$()를 $(2)소유자$() 슬롯에 넣으세요."
    ),
    "mffs/entries/machines/biometric_identifier.json.pages[6].text": (
        "$(9)생체 인식 식별기$()의 소유자는 $(4)모든 권한을 자동으로 받습니다.$() "
        "레드스톤 신호를 보내거나 화면 왼쪽 위의 레드스톤 횃불 버튼을 눌러 "
        "$(9)생체 인식 식별기$()를 활성화하세요. 활성화되면 "
        "$(9)생체 인식 식별기$()에 불이 켜지고 설정한 권한이 적용됩니다."
    ),
    "mffs/entries/machines/biometric_identifier.json.pages[8].text": (
        "$(li)역장을 통과할 때는 완전히 빠져나올 때까지 계속 웅크려야 합니다. 중간에 멈추면 "
        "사망합니다.$(li)활성화된 식별기에서는 $(l:mffs:tools/id_card)신원 카드$()를 꺼낼 수 "
        "없습니다.$(li)역장을 통과하면 일시적으로 멀미 IV 효과를 받을 수 있습니다."
        "$(li)크리에이티브 모드 플레이어는 언제나 역장을 통과할 수 있습니다.$()"
    ),
    "mffs/entries/machines/coercion_deriver.json.pages[0].text": (
        "$(9)강제 유도기$()는 다른 MFFS 기계에 필요한 FE 에너지를 "
        "$(l:mffs:getting_started/fortron)포트론$()으로 바꾸는 기계입니다. "
        "$(9)강제 유도기$()를 $(l:mffs:machines/fortron_capacitor)포트론 축전기$()와 함께 "
        "사용해 축전기를 $(l:mffs:getting_started/fortron)포트론$()으로 채우면, 축전기가 "
        "$(l:mffs:getting_started/fortron)포트론$()을 다른 기계에 분배합니다."
    ),
    "mffs/entries/machines/coercion_deriver.json.pages[2].text": (
        "$(l:mffs:getting_started/fortron)포트론$()을 만들려면 $(9)강제 유도기$()를 FE "
        "전원에 연결하고 레드스톤 신호로 활성화하세요. 전원과 신호가 공급되면 "
        "$(9)강제 유도기$()가 빨간색에서 파란색으로 바뀌며 "
        "$(l:mffs:getting_started/fortron)포트론$()을 생성합니다. $(9)강제 유도기$()의 "
        "주파수 번호를 맞추면 "
        "$(l:mffs:machines/fortron_capacitor)포트론 축전기$() 같은 다른 MFFS 기계와 "
        "연결할 수 있습니다."
    ),
    "mffs/entries/machines/coercion_deriver.json.pages[3].text": (
        "주파수는 다음 방법으로 설정합니다:$(li)강제 유도기를 우클릭하고 화면에 원하는 "
        "주파수 번호 입력$(li)주파수 카드를 들고 강제 유도기를 Shift+우클릭$(p)"
        "$(9)강제 유도기$()의 $(l:mffs:getting_started/fortron)포트론$() 생성량은 화살표 옆 "
        "슬롯에 $(2)청금석$()이나 $(2)네더 석영$()을 넣어 높일 수 있습니다. 그러면 "
        "$(l:mffs:getting_started/fortron)포트론$() 출력이 약 20배로 늘어납니다."
    ),
    "mffs/entries/machines/coercion_deriver.json.pages[4].text": (
        "$(9)강제 유도기$()에는 유도와 통합 두 가지 모드가 있습니다. 기본 '유도' 모드는 "
        "FE를 $(l:mffs:getting_started/fortron)포트론$()으로 계속 변환합니다. 화면 중앙의 "
        "$(2)유도$() 버튼을 누르면 $(2)통합$() 모드로 전환되며, 다시 누르면 돌아옵니다. "
        "통합 모드에서는 반대로 $(l:mffs:getting_started/fortron)포트론$()을 FE로 변환합니다."
    ),
    "mffs/entries/machines/coercion_deriver.json.pages[5].text": (
        "강제 유도기는 모듈로 성능을 높일 수 있습니다.$(li)"
        "$(l:mffs:upgrade_modules/speed_module)$(5)속도 모듈$(): $(2)청금석$()이나 "
        "$(2)네더 석영$()의 "
        "증폭 효과를 높입니다.$(li)$(l:mffs:upgrade_modules/capacity_module)"
        "$(5)용량 모듈$(): 저장할 수 있는 $(l:mffs:getting_started/fortron)포트론$()의 양을 "
        "늘립니다.$()"
    ),
    "mffs/entries/machines/fortron_capacitor.json.pages[2].text": (
        "축전기를 놓고 사용할 주파수를 정하세요. 기본 주파수는 0이며 다음 방법으로 바꿀 수 "
        "있습니다:$(li)축전기를 우클릭하고 화면에 원하는 주파수 번호 입력$(li)"
        "$(l:mffs:tools/frequency_card)주파수 카드$()를 들고 축전기를 Shift+우클릭"
    ),
    "mffs/entries/machines/fortron_capacitor.json.pages[3].text": (
        "레드스톤 신호로 포트론 축전기를 활성화하세요. 활성화되면 빨간색에서 파란색으로 "
        "바뀌며, 같은 주파수를 사용하고 범위 안에 있는 다른 MFFS 장치와 "
        "$(l:mffs:getting_started/fortron)포트론$()을 주고받습니다. 기본 범위는 15블록입니다."
    ),
    "mffs/entries/machines/fortron_capacitor.json.pages[4].text": (
        "포트론 축전기는 모듈로 성능을 높일 수 있습니다:$(li)"
        "$(l:mffs:upgrade_modules/scale_module)$(5)크기 모듈$(): 다른 MFFS 기계와 연결되는 "
        "거리를 늘립니다. 기본 15블록에서 모듈마다 1블록씩 늘어납니다.$(li)"
        "$(l:mffs:upgrade_modules/speed_module)$(5)속도 모듈$(): 기계와 "
        "$(l:mffs:getting_started/fortron)포트론$()을 더 빠르게 주고받습니다. 모듈마다 "
        "전송량이 50 FE 증가합니다."
    ),
    "mffs/entries/machines/interdiction_matrix.json.pages[2].text": (
        "$(9)차단 매트릭스$() 주변은 $(bold)작동$() 영역과 $(bold)경고$() 영역으로 "
        "나뉩니다. 작동 영역은 설치한 $(l:mffs:upgrade_modules/scale_module)"
        "$(5)크기 모듈$() 수만큼 매트릭스에서 바깥으로 넓어집니다. 기본 경고 영역은 작동 "
        "영역 가장자리에서 다시 3블록만큼 이어지는 동심 구입니다."
    ),
    "mffs/entries/machines/projector.json.pages[4].text": (
        "화면 아래 숫자는 설정한 크기와 모양의 역장을 유지하는 데 필요한 포트론 양입니다. "
        "레드스톤 신호로 프로젝터를 활성화하세요. 충분한 "
        "$(l:mffs:getting_started/fortron)포트론$()이 있다면 프로젝터가 빨간색에서 파란색으로 "
        "바뀌고 $(9)역장 프로젝터$()가 역장을 투사합니다.$(p)역장을 통과하려면 "
        "$(l:mffs:machines/biometric_identifier)생체 인식 식별기$()가 필요합니다."
    ),
    "mffs/entries/machines/projector.json.pages[5].text": (
        "$(9)역장 프로젝터$()는 여러 모듈로 강화할 수 있습니다.$(li)"
        "$(l:mffs:upgrade_modules/scale_module)$(5)크기 모듈$(): 투사할 역장의 모양을 "
        "조절합니다.$(li)$(l:mffs:upgrade_modules/speed_module)$(5)속도 모듈$(): 역장을 더 "
        "빠르게 생성합니다.$(li)$(l:mffs:upgrade_modules/capacity_module)$(5)용량 모듈$(): "
        "프로젝터가 저장할 수 있는 $(l:mffs:getting_started/fortron)포트론$() 양을 늘립니다.$()"
    ),
    "mffs/entries/projector_modes/custom_mode.json.pages[0].text": (
        "$(2)사용자 지정 모드$()는 원하는 모양이나 구조의 역장을 만들 수 있는 가장 유연한 "
        "모드입니다. 사용자가 만든 블록 모양을 $(2)사용자 지정 모드$() 아이템이 분석해 "
        "저장하면 프로젝터가 "
        "원본의 $(9)정확한 복제본$()을 역장으로 만듭니다. 다리, 집, 거대한 요새처럼 "
        "$(9)만들 수 있는 모든 구조$()를 역장으로 구현할 수 있습니다!"
    ),
    "mffs/entries/projector_modes/custom_mode.json.pages[3].text": (
        "프로젝터에 $(2)사용자 지정 모드$()를 넣으면 알려진 모드 모양과 다르다는 표시로 "
        "무작위 홀로그램이 계속 나타납니다. 이는 정상 동작입니다. 원한다면 방향 화살표가 "
        "있는 슬롯에 $(l:mffs:projector_modules/translation_module)$(5)이동 모듈$()을 넣어 "
        "프로젝터를 기준으로 역장이 나타날 위치를 정할 수 있습니다."
    ),
    "mffs/entries/projector_modes/custom_mode.json.pages[4].text": (
        "다른 프로젝터 모드처럼 $(2)사용자 지정 모드$() 역장도 "
        "$(l:mffs:projector_modules/rotation_module)$(5)회전 모듈$()과 "
        "$(l:mffs:upgrade_modules/scale_module)$(5)크기 모듈$()로 각각 회전하거나 크기를 "
        "바꿀 수 있습니다."
    ),
    "mffs/entries/projector_modules/collection_module.json.pages[0].text": (
        "$(l:mffs:machines/projector)역장 프로젝터$()의 매트릭스 슬롯에 "
        "$(l:mffs:projector_modules/disintegration_module)$(5)분해 모듈$()과 "
        "$(5)수집 모듈$()을 함께 넣으면 파괴된 블록의 아이템을 프로젝터 주변 인벤토리로 "
        "모읍니다."
    ),
    "mffs/entries/projector_modules/disintegration_module.json.pages[2].text": (
        "$(5)분해 모듈$()은 모든 프로젝터 모드와 호환되며 "
        "$(l:mffs:projector_modules/stabilization_module)$(5)안정화 모듈$()의 효과를 되돌릴 "
        "때도 사용할 수 있습니다. $(l:mffs:upgrade_modules/speed_module)$(5)속도 모듈$()을 "
        "넣으면 여러 블록을 동시에 분해합니다. "
        "$(l:mffs:projector_modules/collection_module)$(5)수집 모듈$()과 함께 쓰면 파괴한 "
        "블록을 자동으로 수집합니다."
    ),
    "mffs/entries/projector_modules/dome_module.json.pages[0].text": (
        "$(5)돔 모듈$()을 $(l:mffs:machines/projector)역장 프로젝터$()의 매트릭스 슬롯에 "
        "넣으면 프로젝터의 Y 높이보다 아래에 투사되는 블록을 모두 잘라 내 돔 모양을 만듭니다."
    ),
    "mffs/entries/projector_modules/fusion_module.json.pages[0].text": (
        "$(5)역장 융합 모듈$()을 여러 $(l:mffs:machines/projector)역장 프로젝터$()의 "
        "매트릭스 슬롯에 넣으면 둘 이상의 역장을 합칠 수 있습니다. 다른 역장과 겹치는 "
        "블록을 잘라 내 여러 역장을 하나로 자연스럽게 이어 줍니다."
    ),
    "mffs/entries/projector_modules/glow_module.json.pages[0].text": (
        "$(5)발광 모듈$()을 $(l:mffs:machines/projector)역장 프로젝터$()에 넣으면 역장 "
        "주변을 밝힙니다. $(5)발광 모듈$()을 설치하면 역장이 빛을 내며 "
        "$(5)발광 모듈$()은 최대 64개까지 넣을 수 있습니다. 모듈을 더 넣을수록 밝아져 "
        "최대 발광석 밝기에 도달합니다."
    ),
    "mffs/entries/projector_modules/rotation_module.json.pages[0].text": (
        "$(5)회전 모듈$()을 $(l:mffs:machines/projector)역장 프로젝터$()의 해당 방향 "
        "슬롯에 넣으면 x, y, z축을 기준으로 역장을 회전합니다. "
        "$(5)회전 모듈$()을 각 축의 슬롯에 넣으세요. $(li)동쪽·서쪽: 좌우 회전"
        "$(li)위·아래: 상하 회전$(li)남쪽·북쪽: 기울기 회전$()"
    ),
    "mffs/entries/projector_modules/sponge_module.json.pages[0].text": (
        "$(5)스펀지 모듈$()을 $(l:mffs:machines/projector)역장 프로젝터$()에 넣으면 역장 "
        "안의 유체를 계속 감지해 제거합니다. "
        "$(l:mffs:upgrade_modules/speed_module)$(5)속도 모듈$()을 넣으면 제거 속도가 "
        "빨라집니다. 물처럼 무한히 생성되는 유체를 제거할 때는 속도를 높여야 할 수 있습니다."
    ),
    "mffs/entries/projector_modules/stabilization_module.json.pages[2].text": (
        "안정화 작업은 일반 역장 투사보다 많은 $(l:mffs:getting_started/fortron)포트론$()이 "
        "필요하고 느리지만, 프로젝터의 "
        "$(l:mffs:projector_modes/custom_mode)$(2)사용자 지정 모드$()와 함께 쓰면 활용법이 "
        "거의 무한합니다. 예를 들어 $(2)크리퍼$()가 폭발시킬 때마다 자동으로 복구되는 구조물을 만들 "
        "수 있습니다. $(l:mffs:upgrade_modules/speed_module)$(5)속도 모듈$()을 넣으면 여러 "
        "블록을 동시에 안정화합니다."
    ),
    "mffs/entries/projector_modules/translation_module.json.pages[0].text": (
        "$(5)이동 모듈$()을 $(l:mffs:machines/projector)역장 프로젝터$()의 방향별 슬롯에 "
        "넣으면 투사되는 역장의 위치를 옮깁니다. $(5)이동 모듈$() 하나마다 해당 방향으로 1블록씩 "
        "이동합니다."
    ),
    "mffs/entries/upgrade_modules/scale_module.json.pages[0].text": (
        "$(5)크기 모듈$()은 여러 MFFS 기계의 거리 관련 성능을 높입니다. 기계에 따라 "
        "효과가 다르며 주로 다음 기능을 제공합니다: $(li)역장 크기 증가$(li)차단 영역 증가"
        "$(li)$(l:mffs:machines/coercion_deriver)강제 유도기$()의 연료 증폭 효과 증가"
    ),
    "mffs/entries/upgrade_modules/speed_module.json.pages[0].text": (
        "$(5)속도 모듈$()은 여러 MFFS 기계의 성능을 높입니다. 기계에 따라 효과가 다르며 "
        "주로 다음 기능을 제공합니다: $(li)역장 투사 속도 증가$(li)"
        "$(l:mffs:machines/fortron_capacitor)포트론 축전기$()의 "
        "$(l:mffs:getting_started/fortron)포트론$() 전송 한도 증가$(li)"
        "$(l:mffs:machines/coercion_deriver)강제 유도기$() 효율 증가"
    ),
    "mffs/entries/interdiction_modules/block_access_module.json.pages[0].text": (
        "$(5)블록 사용 차단 모듈$()은 $(l:mffs:machines/interdiction_matrix)차단 "
        "매트릭스$()에 넣는 선택 모듈입니다. 설치하면 작동 범위 안의 플레이어가 블록을 "
        "우클릭해 화면을 열지 못하게 합니다."
    ),
    "mffs/entries/interdiction_modules/block_access_module.json.pages[1].text": (
        "$(5)블록 사용 차단 모듈() 제작법입니다."
    ),
    "mffs/entries/interdiction_modules/warn_module.json.pages[1].text": (
        "$(5)경고 모듈$() 제작법입니다."
    ),
    "mffs/entries/machines/projector.json.pages[2].text": (
        "역장을 만들려면 $(9)역장 프로젝터$()와 가까운 "
        "$(l:mffs:machines/fortron_capacitor)포트론 축전기$()를 연결해 "
        "$(l:mffs:getting_started/fortron)포트론$()을 공급하세요. 다음 방법 가운데 하나를 "
        "사용합니다:$(li)$(9)역장 프로젝터$()를 우클릭하고 화면에 축전기와 같은 주파수 "
        "번호 입력$(li)$(l:mffs:tools/frequency_card)주파수 카드$()를 들고 프로젝터를 "
        "Shift+우클릭"
    ),
    "mffs/entries/projector_modes/cube_mode.json.pages[2].text": (
        "$(2)정육면체 모드$()로 직육면체 모양의 역장도 만들 수 있습니다. 방향 화살표가 "
        "있는 슬롯에 $(l:mffs:upgrade_modules/scale_module)$(5)크기 모듈$()을 넣으면 해당 "
        "방향으로만 역장이 1블록 늘어납니다. 예를 들어 역장 높이를 1블록 늘리려면 화면 "
        "왼쪽 위나 오른쪽 위를 가리키는 슬롯에 "
        "$(l:mffs:upgrade_modules/scale_module)$(5)크기 모듈$()을 넣으세요."
    ),
    "mffs/entries/projector_modes/cyllinder_mode.json.pages[2].text": (
        "방향 화살표가 있는 슬롯에 $(l:mffs:upgrade_modules/scale_module)$(5)크기 모듈$()을 "
        "넣으면 해당 방향으로만 역장이 1블록 늘어납니다. 예를 들어 역장 높이를 1블록 "
        "늘리려면 화면 왼쪽 위나 오른쪽 위를 가리키는 슬롯에 "
        "$(l:mffs:upgrade_modules/scale_module)$(5)크기 모듈$()을 넣으세요."
    ),
    "mffs/entries/projector_modes/pyramid_mode.json.pages[3].text": (
        "예를 들어 역장 높이를 1블록 늘리려면 화면 왼쪽 위나 오른쪽 위를 가리키는 슬롯에 "
        "$(l:mffs:upgrade_modules/scale_module)$(5)크기 모듈$()을 넣으세요."
    ),
    "mffs/entries/projector_modes/tube_mode.json.pages[2].text": (
        "방향 화살표가 있는 슬롯에 $(l:mffs:upgrade_modules/scale_module)$(5)크기 모듈$()을 "
        "넣으면 해당 방향으로만 역장이 1블록 늘어납니다. 예를 들어 역장 높이를 1블록 "
        "늘리려면 화면 왼쪽 위나 오른쪽 위를 가리키는 슬롯에 "
        "$(l:mffs:upgrade_modules/scale_module)$(5)크기 모듈$()을 넣으세요."
    ),
    "mffs/entries/projector_modes/sphere_mode.json.pages[0].text": (
        "기본적으로 $(2)구체 모드$()는 두께가 정확히 1블록인 구 모양 역장을 만듭니다. "
        "$(l:mffs:upgrade_modules/scale_module)$(5)크기 모듈$()마다 역장 크기가 1블록 "
        "늘어납니다."
    ),
    "mffs/entries/projector_modes/sphere_mode.json.pages[1].text": (
        "$(2)구체 모드$() 제작법입니다."
    ),
    "mffs/entries/projector_modes/tube_mode.json.pages[0].text": (
        "기본적으로 $(2)관 모드$()는 두께가 정확히 1블록인 네모난 관 모양의 역장을 "
        "만듭니다. 관 모양 역장은 수평으로 이어지는 네 개의 막힌 면으로 이루어지며, "
        "프로젝터의 앞뒤 방향이 관의 열린 면이 됩니다."
    ),
    "mffs/entries/projector_modules/dome_module.json.pages[1].text": (
        "$(5)돔 모듈$() 제작법입니다."
    ),
    "mffs/entries/projector_modules/fusion_module.json.pages[1].text": (
        "$(5)역장 융합 모듈$() 제작법입니다."
    ),
    "mffs/entries/projector_modules/glow_module.json.pages[2].text": (
        "$(5)발광 모듈$()을 설치한 역장을 투사하는 역장 프로젝터입니다."
    ),
    "mffs/entries/upgrade_modules/scale_module.json.pages[1].text": (
        "$(5)크기 모듈$() 제작법입니다."
    ),
    "mffs/entries/upgrade_modules/speed_module.json.pages[1].text": "$(5)속도 모듈$() 제작법입니다.",
}

TEXT_REPLACEMENTS = (
    ("레이저 I/O", "LaserIO"),
    ("레이저IO", "LaserIO"),
    ("Laser IO", "LaserIO"),
    ("포트론", "포트론"),
    ("Fortron", "포트론"),
    ("강압 유도체", "강제 유도기"),
    ("강제력 유도체", "강제 유도기"),
    ("생체 인식 식별자", "생체 인식 식별기"),
    ("금지 매트릭스", "차단 매트릭스"),
    ("인터딕션 매트릭스", "차단 매트릭스"),
    ("포스 필드", "역장"),
    ("힘의 장", "역장"),
    ("강제장", "역장"),
    ("프로젝터", "프로젝터"),
    ("항목", "아이템"),
    ("액체", "유체"),
    ("엔터티", "엔티티"),
    ("레시피", "조합법"),
    ("화이트리스트", "허용 목록"),
    ("블랙리스트", "차단 목록"),
    ("오버클러커", "오버클러커"),
    ("GUI", "화면"),
    ("오른쪽 클릭", "우클릭"),
    ("마우스 오른쪽 버튼 클릭", "우클릭"),
    ("Shift-우클릭", "Shift+우클릭"),
    ("시프트 우클릭", "Shift+우클릭"),
)

KEY_OVERRIDES = {
    "laserio.tooltip.item.card.sneaky": "접근 면: ",
    "laserio.tooltip.item.show_settings": "Shift 키를 누르면 설정을 표시합니다",
    "screen.laserio.comparenbt": "데이터 비교",
    "screen.laserio.energylimit": "에너지 제한 (%)",
    "screen.laserio.extractamt": "전송량",
    "screen.laserio.hideparticles": "입자 숨기기",
    "screen.laserio.nbtfalse": "데이터 무시",
    "screen.laserio.nbttrue": "데이터 일치",
    "screen.laserio.redstoneMode": "레드스톤 모드: ",
    "screen.laserio.redstonechannel": "레드스톤 채널: ",
    "screen.laserio.showparticles": "입자 표시",
    "screen.laserio.tickSpeed": "속도(틱)",
    "info.mffs.coercion_deriver.mode.integrate": "통합",
    "info.mffs.coercion_deriver.mode.derive": "유도",
    "info.mffs.field_permission.warp": "통과",
    "info.mffs.field_permission.use_blocks": "블록 사용",
    "info.mffs.field_permission.place_blocks": "블록 설치·파괴",
    "info.mffs.field_permission.configure_security_center": "보안 설정",
    "info.mffs.field_permission.bypass_defense": "방어 우회",
    "info.mffs.field_permission.bypass_confiscation": "압수 우회",
    "info.mffs.field_permission.remote_control": "원격 제어",
    "info.mffs.handbook.title": "역장 안내서",
    "item.mffs.custom_mode.mode.additive": "더하기",
    "item.mffs.custom_mode.mode.subtractive": "빼기",
    "mffs.confiscation_mode.blacklist": "차단",
    "mffs.confiscation_mode.whitelist": "허용",
    "screen.mffs.master": "소유자",
    "advancements.mffs.root.title": "Modular Force Field Systems",
    "advancements.mffs.root.description": "역장의 세계로 들어가세요!",
    "advancements.mffs.steel_compound.title": "튼튼한 혼합물",
    "advancements.mffs.steel_compound.description": "강철 혼합물을 제작하세요",
    "advancements.mffs.smelt_steel.title": "철보다 단단하게",
    "advancements.mffs.smelt_steel.description": "강철 주괴를 제련하세요",
    "advancements.mffs.field_shock.title": "짜릿한 경험",
    "advancements.mffs.field_shock.description": "역장에 의해 분해되세요",
    "advancements.mffs.projector.title": "포스가 함께하기를!",
    "advancements.mffs.projector.description": "역장 프로젝터를 제작하세요",
    "advancements.mffs.sponge_module.title": "내 물은 어디로 갔지?",
    "advancements.mffs.sponge_module.description": "스펀지 모듈을 제작하세요",
    "advancements.mffs.field_shape.title": "역장 설계자",
    "advancements.mffs.field_shape.description": "자신만의 역장 모양을 만드세요",
    "advancements.mffs.camouflage.title": "눈앞에 숨기",
    "advancements.mffs.camouflage.description": "위장 모듈을 제작하세요",
    "advancements.mffs.custom_camouflage.title": "매트릭스 속으로",
    "advancements.mffs.custom_camouflage.description": "사용자 지정 모드와 위장을 함께 사용하세요",
}

QUEST_OVERRIDES: dict[str, object] = {
    "quest.046C417B2ADF3AA7.quest_desc": [
        "카드에도 한계가 있습니다. 아이템 추출은 한 번에 8개, 유체 추출은 5양동이까지만 옮길 수 있습니다. 화학 물질과 에너지는 얼마나 될까요? \n\n하지만 여기는 모드가 적용된 &2&lMinecraft&r입니다. 이 정도로는 부족하니 오버클럭해야 합니다. \n\n카드 오른쪽 위 칸에 카드 오버클러커를 넣으면 한 번에 옮길 수 있는 최대량이 늘어납니다!"
    ],
    "quest.046C417B2ADF3AA7.quest_subtitle": "최대: 4",
    "quest.06767BA0AFE8C1EE.quest_desc": [
        "1... 2... 어딘가에 4도 있겠죠. \n\n수량을 설정하려면 필터에 아이템을 넣고 좌클릭이나 우클릭으로 수량을 바꾸세요. Shift를 누른 채 같은 조작을 하면 10씩 바뀝니다. 설정한 뒤 필터를 카드에 넣으세요! \n\n이제 설정한 수량 이상의 아이템이 있을 때만 추출하며, 첫 번째 인벤토리에는 그 수량만큼 남겨 둡니다."
    ],
    "quest.0BB562FB44B0AAA7.quest_desc": [
        "카드만 속도 제한이 있는 것은 아니므로 오버클러커도 카드에만 쓰는 것이 아닙니다! \n\n노드 오버클러커를 &c노드&r 오른쪽 아래 칸에 넣으면 노드의 작업 속도가 빨라집니다."
    ],
    "quest.0BB562FB44B0AAA7.quest_subtitle": "최대: 8",
    "quest.1C70D739CE464E25.quest_desc": [
        "&2아이템 카드&r와 똑같이 추출 카드와 삽입 카드가 필요합니다. 이번에는 &9유체&r가 든 탱크에서 다른 탱크로 옮깁니다. 월드의 &9유체&r 원천을 직접 퍼 올리거나 놓는 기능은 아닙니다."
    ],
    "quest.1C70D739CE464E25.title": "&9유체 카드",
    "quest.2A6900E87DE8BAE0.quest_desc": [
        "모드 필터도 사용법이 간단합니다. 아이템을 넣고 허용 목록이나 차단 목록으로 설정하세요. 단, 그 아이템 하나가 아니라 같은 모드의 모든 아이템을 대상으로 합니다. \n\n예를 들어 Apotheosis 보석은 Apotheosis 아이템만, Mekanism 합금은 Mekanism 아이템만 통과시킵니다."
    ],
    "quest.3065EA195D0A36BA.quest_desc": [
        "태그는 Minecraft에서 아이템을 묶는 중요한 방법이므로 필터에도 활용할 수 있습니다! \n\n아이템을 넣고 태그를 선택하거나, 태그를 알고 있다면 직접 입력하세요. \n\n도구 태그를 사용해 시스템에서 장비만 꺼내는 작업 등에 유용합니다. \n\n(손에 든 아이템의 태그는 /kubejs hand 명령으로 확인할 수 있습니다.)"
    ],
    "quest.308935C85364B04D.quest_desc": [
        "카드마다 설정을 따로 저장하므로 여러 카드를 계속 설정하기는 번거롭습니다. 이럴 때는 설정을 복제하세요! \n\n카드 복제기로 카드를 좌클릭하면 데이터를 복사하고, 다른 카드를 우클릭하면 그 데이터를 붙여넣습니다!"
    ],
    "quest.47768B1FFD57D56E.quest_desc": [
        "&4레드스톤&r 배선을 사방에 깔아야 해서 불편하지 않았나요? FE를 무선으로 보낼 수 있다면 &4레드스톤&r도 무선으로 보낼 수 있어야겠죠. &c&lLaserIO&r라면 가능합니다. &4입력 카드&r로 &4레드스톤 신호&r를 받은 뒤 &4출력 카드&r로 다른 곳에 &4신호&r를 출력하세요!"
    ],
    "quest.47768B1FFD57D56E.title": "&4레드스톤 카드",
    "quest.47A2BEFB11F4D581.quest_desc": [
        "기본 필터는 이름 그대로 사용하기 쉽습니다. 아이템을 넣으면 해당 아이템이 필터 대상이 됩니다. \n\n허용 목록으로 설정하면 등록한 아이템만 통과하고, 차단 목록으로 설정하면 등록한 아이템만 막습니다. \n\n데이터 일치를 켜면 마법 부여, 내구도, 아이템 안의 몹 같은 구성 요소까지 같아야 합니다. 끄면 데이터와 관계없이 같은 종류의 아이템을 처리합니다."
    ],
    "quest.4C41FD926F31180B.quest_desc": [
        "&c&lLaserIO&r로 &2아이템&r을 옮기려면 &2아이템 카드&r가 필요합니다. \n\n한 카드를 추출로 설정해 아이템을 가져올 &c레이저 노드&r의 면에 넣고, 다른 카드는 삽입으로 설정해 아이템을 보낼 면에 넣으세요. \n\n추출 대상이 여러 곳이라면 우선순위와 순환 분배 같은 설정을 사용할 수 있습니다. 순환 분배는 가장 가까운 인벤토리만 먼저 처리하지 않고 대상들을 차례로 처리합니다."
    ],
    "quest.4C41FD926F31180B.title": "&2아이템 카드",
    "quest.52F85CED20C8B1E9.quest_desc": [
        "&e에너지&r도 원하는 곳으로 옮겨야 합니다. &2아이템&r, &9유체&r, &5화학 물질&r과 같은 방식으로 전송하세요!"
    ],
    "quest.52F85CED20C8B1E9.title": "&e에너지 카드",
    "quest.5C0F6B1C93A52113.quest_desc": [
        "이것이 &c&lLaserIO&r의 진짜 핵심입니다! 실제로 작동할 카드는 &c레이저 노드&r에 넣습니다. \n\n노드는 동서남북 4개 기본 방향과 위아래에 인접한 인벤토리 사이에서 아이템을 옮깁니다. 더 먼 인벤토리로 보내려면 두 번째 &c노드&r를 놓고, 렌치로 1번 노드를 Shift+우클릭한 뒤 2번 노드를 우클릭해 연결하세요. \n\n카드는 알맞은 방향의 슬롯에 넣습니다. 노드 오버클러커도 넣어 작업 속도를 높일 수 있습니다. "
    ],
    "quest.5F1218CF8EFC607B.quest_desc": [
        "&c&lLaserIO&r는 DireWolf가 &a&lEnderIO&r의 &l물류&r 기능을 이어 만든 모드입니다.",
        "",
        "&c레이저&r로 아이템을 옮기는 모드예요! &c레이저&r를 싫어할 사람이 있나요?!",
        "",
        "모든 것은 논리 칩에서 시작합니다.",
    ],
    "quest.5F1218CF8EFC607B.title": "&c&lLaserIO",
    "quest.617695A9CA45D88F.quest_desc": [
        "&c&lLaserIO&r로 &l물류&r를 구성하다 보면 카드가 아주 많아집니다. 카드마다 인벤토리 한 칸을 차지하니 금세 꽉 차겠죠. 다행히 카드 보관함이 있습니다! \n\n여러 카드를 보관할 수 있고, 레이저 노드를 열면 카드 보관함도 두 번째 인벤토리처럼 함께 열립니다. 아주 유용합니다!"
    ],
    "quest.6718043D0F2D1830.quest_desc": [
        "DireWolf는 카드가 &5&lMekanism&r의 여러 물질 상태도 처리할 수 있게 해 달라는 요청을 받았습니다. 가압 튜브로 옮길 수 있는 기체, 주입 물질과 안료를 이 카드로 전송할 수 있습니다."
    ],
    "quest.6718043D0F2D1830.title": "&5화학 물질 카드",
    "quest.7BC8F50A89A3BE1A.quest_desc": [
        "레이저 렌치는 &c레이저 노드&r끼리 연결하거나 노드를 커넥터에 연결할 때 사용합니다. 렌치라는 주제에 맞추기 위한 도구이기도 하죠. \n\n다른 모드의 블록 설정을 바꾸는 일반 렌치로도 사용할 수 있습니다!"
    ],
    "quest.7EE27C3908008E20.quest_desc": [
        "&c레이저 노드&r를 먼 거리까지 연결해야 한다면 커넥터를 사용하세요! 연결 방법은 렌치를 평소처럼 사용하면 됩니다."
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


def translate_fixed(source: str) -> str | None:
    return SOURCE_OVERRIDES.get(source)


def normalize_text(value: str) -> str:
    value = value.replace("Modular Force Field Systems", "__MFFS_OFFICIAL_NAME__")
    for english, korean in sorted(
        SOURCE_OVERRIDES.items(), key=lambda row: len(row[0]), reverse=True
    ):
        value = value.replace(english, korean)
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    value = value.replace("해야합니다", "해야 합니다").replace(
        "할 수있는", "할 수 있는"
    )
    value = value.replace(".,", ".").replace(". ,", ".")
    value = value.replace("__MFFS_OFFICIAL_NAME__", "Modular Force Field Systems")
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    return value


def candidate_language() -> dict[str, object]:
    cache = load_json(LANG_CACHE) if LANG_CACHE.is_file() else {}
    rows: dict[str, dict[str, str]] = {}
    requests: set[str] = set()
    for namespace in TARGETS:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        rows[namespace] = {}
        for key, source in english.items():
            if not isinstance(source, str):
                raise TypeError(f"문자열이 아닌 언어 값: {namespace}:{key}")
            if key in KEY_OVERRIDES:
                rows[namespace][key] = KEY_OVERRIDES[key]
            elif translate_fixed(source) is not None:
                rows[namespace][key] = str(translate_fixed(source))
            elif isinstance(cache.get(source), str):
                rows[namespace][key] = str(cache[source])
            elif family_goal.is_allowed_original(source):
                rows[namespace][key] = source
            else:
                requests.add(source)
    if requests:
        failures: list[str] = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(ars_family.request_translation, source): source
                for source in sorted(requests)
            }
            for number, future in enumerate(as_completed(futures), start=1):
                source = futures[future]
                try:
                    cache[source] = future.result()
                    if number % 25 == 0:
                        write_json(LANG_CACHE, cache)
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(LANG_CACHE, cache)
        if failures:
            raise RuntimeError("자동 번역 후보 생성 실패:\n" + "\n".join(failures))
    for namespace in TARGETS:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        for key, source in english.items():
            if key not in rows[namespace]:
                rows[namespace][key] = str(cache[source])
    write_json(LANG_CANDIDATES, rows)
    report = {
        "keys": sum(len(row) for row in rows.values()),
        "bundled_korean_candidates": 0,
        "status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


def normalize_language() -> dict[str, object]:
    candidates = load_json(LANG_CANDIDATES)
    count = 0
    for namespace in TARGETS:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        row = candidates.get(namespace)
        if not isinstance(row, dict):
            raise TypeError(f"후보 네임스페이스 누락: {namespace}")
        korean: dict[str, str] = {}
        for key, source in english.items():
            candidate = row.get(key)
            if not isinstance(source, str) or not isinstance(candidate, str):
                raise TypeError(f"문자열이 아닌 언어 값: {namespace}:{key}")
            translated = KEY_OVERRIDES.get(key, translate_fixed(source) or candidate)
            translated = normalize_text(translated)
            errors = family_goal.validate_family_value(FAMILY, key, source, translated)
            if errors:
                raise ValueError("; ".join(errors))
            korean[key] = translated
            count += 1
        write_json(WORK_ROOT / namespace / "ko_kr.json", korean)
    for root in sorted((WORK_ROOT / "quests").glob("*")):
        english_file = root / "en_us.json"
        if not english_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(root / "ko_kr.json")
        for key, source in english.items():
            if key not in QUEST_OVERRIDES:
                raise KeyError(f"검수한 퀘스트 번역 누락: {key}")
            target = QUEST_OVERRIDES[key]
            if isinstance(source, str) and isinstance(target, str) and "\\n" in source:
                target = target.replace("\n", "\\n")
            elif isinstance(source, list) and isinstance(target, list):
                target = [
                    target_value.replace("\n", "\\n")
                    if "\\n" in source_value
                    else target_value
                    for source_value, target_value in zip(source, target, strict=True)
                ]
            korean[key] = target
        write_json(root / "ko_kr.json", korean)
    report = {
        "language_keys_reviewed": count,
        "quest_display_keys_reviewed": len(QUEST_OVERRIDES),
        "bundled_korean_reused_without_review": 0,
        "status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def find_jar(prefix: str) -> Path:
    return family_goal.find_jar(resolve_source_root(), prefix)


def prepare_guides(force: bool) -> dict[str, object]:
    inventory: dict[str, object] = {}
    for namespace, config in TARGETS.items():
        en_root = GUIDE_ROOT / namespace / "en_us"
        if force and en_root.exists():
            shutil.rmtree(en_root)
        jar = find_jar(str(config["jar_prefix"]))
        source_prefix = str(config["source_prefix"])
        files = 0
        with ZipFile(jar) as archive:
            for name in sorted(archive.namelist()):
                if not name.startswith(source_prefix) or not name.endswith(".json"):
                    continue
                relative = name.removeprefix(source_prefix)
                destination = en_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(name))
                files += 1
        inventory[namespace] = {"jar": jar.name, "files": files}
    write_json(GUIDE_ROOT / "inventory.json", inventory)
    return inventory


def walk_visible(value: object, location: str = "") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}" if location else key
            if key in VISIBLE_FIELDS and isinstance(child, str):
                rows.append((child_location, child))
            rows.extend(walk_visible(child, child_location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(walk_visible(child, f"{location}[{index}]"))
    return rows


def guide_sources() -> dict[str, str]:
    rows: dict[str, str] = {}
    for namespace in TARGETS:
        root = GUIDE_ROOT / namespace / "en_us"
        for path in sorted(root.rglob("*.json")):
            relative = path.relative_to(root).as_posix()
            for field, source in walk_visible(load_json(path)):
                rows[f"{namespace}/{relative}.{field}"] = source
    return rows


def candidate_guides() -> dict[str, object]:
    sources = guide_sources()
    cache = load_json(GUIDE_CACHE) if GUIDE_CACHE.is_file() else {}
    requests = {
        source
        for source in sources.values()
        if source not in SOURCE_OVERRIDES and not isinstance(cache.get(source), str)
    }
    if requests:
        failures: list[str] = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(
                    candidate_helper.request_translation_candidate, source
                ): source
                for source in sorted(requests)
            }
            for number, future in enumerate(as_completed(futures), start=1):
                source = futures[future]
                try:
                    cache[source] = future.result()
                    if number % 20 == 0:
                        write_json(GUIDE_CACHE, cache)
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(GUIDE_CACHE, cache)
        if failures:
            raise RuntimeError("안내서 후보 생성 실패:\n" + "\n".join(failures))
    candidates = {
        location: SOURCE_OVERRIDES[source]
        if source in SOURCE_OVERRIDES
        else str(cache[source])
        for location, source in sources.items()
    }
    write_json(GUIDE_CANDIDATES, candidates)
    report = {
        "visible_fields": len(sources),
        "unique_sources": len(set(sources.values())),
        "status": "candidate_requires_full_review",
    }
    write_json(GUIDE_ROOT / "candidate_report.json", report)
    return report


def replace_visible(
    value: object, prefix: str, candidates: dict[str, object]
) -> object:
    if isinstance(value, dict):
        result: dict[str, object] = {}
        for key, child in value.items():
            location = f"{prefix}.{key}" if prefix else key
            if key in VISIBLE_FIELDS and isinstance(child, str):
                candidate = GUIDE_LOCATION_OVERRIDES.get(
                    location, candidates.get(location)
                )
                if not isinstance(candidate, str):
                    raise KeyError(f"안내서 후보 누락: {location}")
                result[key] = normalize_text(candidate)
            else:
                result[key] = replace_visible(child, location, candidates)
        return result
    if isinstance(value, list):
        return [
            replace_visible(child, f"{prefix}[{index}]", candidates)
            for index, child in enumerate(value)
        ]
    return value


def normalize_guides() -> dict[str, object]:
    candidates = load_json(GUIDE_CANDIDATES)
    files = fields = 0
    for namespace in TARGETS:
        en_root = GUIDE_ROOT / namespace / "en_us"
        ko_root = GUIDE_ROOT / namespace / "ko_kr"
        for path in sorted(en_root.rglob("*.json")):
            relative = path.relative_to(en_root).as_posix()
            prefix = f"{namespace}/{relative}"
            localized = replace_visible(load_json(path), prefix, candidates)
            write_json(ko_root / relative, localized)
            files += 1
            fields += len(walk_visible(localized))
    report = {
        "files_reviewed": files,
        "visible_fields_reviewed": fields,
        "status": "all_visible_fields_reviewed",
    }
    write_json(GUIDE_ROOT / "normalization.json", report)
    return report


def strip_protected(value: str) -> str:
    return PROTECTED.sub("", value)


def verify_guides() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    files = fields = 0
    for namespace in TARGETS:
        en_root = GUIDE_ROOT / namespace / "en_us"
        ko_root = GUIDE_ROOT / namespace / "ko_kr"
        en_files = [
            path.relative_to(en_root) for path in sorted(en_root.rglob("*.json"))
        ]
        ko_files = [
            path.relative_to(ko_root) for path in sorted(ko_root.rglob("*.json"))
        ]
        if en_files != ko_files:
            errors.append(f"{namespace}: 안내서 파일 목록이 다릅니다.")
            continue
        for relative in en_files:
            english = load_json(en_root / relative)
            korean = load_json(ko_root / relative)
            en_rows = dict(walk_visible(english))
            ko_rows = dict(walk_visible(korean))
            if list(en_rows) != list(ko_rows):
                errors.append(
                    f"{namespace}/{relative.as_posix()}: 표시 필드가 다릅니다."
                )
                continue
            for location, source in en_rows.items():
                target = ko_rows[location]
                fields += 1
                if Counter(PROTECTED.findall(source)) != Counter(
                    PROTECTED.findall(target)
                ):
                    errors.append(
                        f"{namespace}/{relative}:{location}: 보호 토큰 불일치"
                    )
                if (
                    source == target
                    and source not in SOURCE_OVERRIDES
                    and LATIN_WORD.search(strip_protected(source))
                ):
                    errors.append(f"{namespace}/{relative}:{location}: 미번역")
                forbidden = (
                    ".,",
                    "화면 화면",
                    "역장를",
                    "오버클러커s",
                    "교대 근무",
                    "아버지 떨어져",
                    "E에너지",
                    "다른 사람에게는",
                    "Modular 역장",
                    "force fields",
                    "Speed ​​모듈",
                )
                if any(fragment in target for fragment in forbidden):
                    errors.append(f"{namespace}/{relative}:{location}: 기계번역 흔적")
            files += 1
    report = {
        "files": files,
        "visible_fields_reviewed": fields,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(GUIDE_ROOT / "validation.json", report)
    return report, errors


def verify_language() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    untranslated: list[str] = []
    count = 0
    for namespace in TARGETS:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        count += len(english)
        if list(english) != list(korean):
            errors.append(f"{namespace}: 키 또는 순서 불일치")
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
                and source not in SOURCE_OVERRIDES
                and not family_goal.is_allowed_original(source)
            ):
                untranslated.append(f"{namespace}:{key}")
    for root in sorted((WORK_ROOT / "quests").glob("*")):
        english = load_json(root / "en_us.json")
        korean = load_json(root / "ko_kr.json")
        if list(english) != list(korean):
            errors.append(f"{root.name}: 퀘스트 키 또는 순서 불일치")
        for key, source in english.items():
            target = korean.get(key)
            source_text = family_goal.quest_snbt.flatten(source)
            target_text = family_goal.quest_snbt.flatten(target)
            if Counter(re.findall(r"[&§][0-9A-FK-ORa-fk-or]", source_text)) != Counter(
                re.findall(r"[&§][0-9A-FK-ORa-fk-or]", target_text)
            ):
                errors.append(f"{root.name}:{key}: 서식 코드 불일치")
            if source_text.count("\\n") != target_text.count("\\n"):
                errors.append(f"{root.name}:{key}: 줄바꿈 불일치")
    if untranslated:
        errors.append("미번역 키: " + ", ".join(untranslated[:30]))
    report = {
        "language_keys_reviewed": count,
        "quest_display_keys_reviewed": len(QUEST_OVERRIDES),
        "bundled_korean_reused_without_review": 0,
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", report)
    return report, errors


def build_guides() -> dict[str, object]:
    copied = 0
    for namespace, config in TARGETS.items():
        source_root = GUIDE_ROOT / namespace / "ko_kr"
        output_root = Path(config["output"])
        for source in sorted(source_root.rglob("*.json")):
            destination = output_root / source.relative_to(source_root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            copied += 1
    return {"copied": copied}


def audit() -> dict[str, object]:
    instance = resolve_source_root()
    advancements = display_nodes = direct_literals = 0
    for config in TARGETS.values():
        jar = find_jar(str(config["jar_prefix"]))
        with ZipFile(jar) as archive:
            for name in archive.namelist():
                if "/advancement/" not in name or not name.endswith(".json"):
                    continue
                advancements += 1
                data = json.loads(archive.read(name))
                display = data.get("display") if isinstance(data, dict) else None
                if not isinstance(display, dict):
                    continue
                display_nodes += 1
                for key in ("title", "description"):
                    value = display.get(key)
                    if isinstance(value, str) and not value.startswith(
                        ("advancements.", "item.")
                    ):
                        direct_literals += 1
    references: list[str] = []
    direct_display: list[str] = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not re.search(r"laserio|mffs|modular force field", text, re.I):
            continue
        relative = path.relative_to(instance).as_posix()
        references.append(relative)
        if path.suffix.lower() == ".js":
            for number, line in enumerate(text.splitlines(), start=1):
                if re.search(
                    r"displayName|setHoverName|tooltip|Text\.(?:of|literal)", line, re.I
                ):
                    direct_display.append(f"{relative}:{number}")
    report = {
        "advancement_files": advancements,
        "advancement_display_nodes": display_nodes,
        "advancement_direct_literals": direct_literals,
        "kubejs_reference_files": references,
        "kubejs_direct_display_lines": direct_display,
        "status": "complete"
        if not direct_literals and not direct_display
        else "review_required",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "candidate-language",
            "normalize-language",
            "prepare-guides",
            "candidate-guides",
            "normalize-guides",
            "verify",
            "build-guides",
            "audit",
        ),
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    code = 0
    if args.command == "candidate-language":
        report = candidate_language()
    elif args.command == "normalize-language":
        report = normalize_language()
    elif args.command == "prepare-guides":
        report = prepare_guides(args.force)
    elif args.command == "candidate-guides":
        report = candidate_guides()
    elif args.command == "normalize-guides":
        report = normalize_guides()
    elif args.command == "verify":
        language_report, language_errors = verify_language()
        guide_report, guide_errors = verify_guides()
        report = {"language": language_report, "guides": guide_report}
        code = 1 if language_errors or guide_errors else 0
    elif args.command == "build-guides":
        report = build_guides()
    else:
        report = audit()
        code = 0 if report["status"] == "complete" else 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
