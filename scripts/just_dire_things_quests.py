#!/usr/bin/env python3
"""Just Dire Things 관련 FTB Quests 한국어 190키를 전부 재검수한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path

import ars_family
import build_ae2_quests as quest_snbt
import just_dire_things_family as language
from local_paths import PROJECT_ROOT


QUEST_ROOT = PROJECT_ROOT / "working/just_dire_things/quests"
CACHE_FILE = PROJECT_ROOT / "temp/just_dire_things_quest_candidate_cache.json"
CANDIDATE_FILE = PROJECT_ROOT / "working/just_dire_things/quest_auto_candidates.json"

KEY_OVERRIDES: dict[str, object] = {
    "quest.0C25F73C0E0FB22A.quest_desc": [
        (
            "&c&l자동 단조&r에 필요한 또 다른 정수는 &a경험치&r입니다! 정확히는 "
            "&3&lJust Dire Things&r의 &a경험치 유체&r예요. \\n\\n&a경험치 유체&r를 얻으려면 "
            "&a경험치 저장기&r가 필요합니다. 경험치 수집 옵션을 사용하면 설정한 영역의 "
            "&a경험치&r를 모을 수 있어요. \\n\\n걱정하지 마세요. &7가시판&r으로 처치한 몹도 "
            "&a경험치&r를 떨어뜨리니 몹 농장 옆에 설치하면 됩니다! \\n\\n다른 형태의 "
            "&a경험치 유체&r나 플레이어 자신의 &a경험치&r 레벨도 넣을 수 있습니다!"
        )
    ],
    "quest.0C25F73C0E0FB22A.title": "자동 &a경험치",
    "quest.10AA2B20D86747F7.quest_desc": [
        "&b페리코어&r는 철과 능력치가 같지만 철에는 없는 특별한 능력이 있습니다! "
        "\\n\\n각 아이템의 설명에서 자세한 기능을 확인해 보세요."
    ],
    "quest.10AA2B20D86747F7.title": "&b페리코어 방어구",
    "quest.1A8440C0048EEB02.quest_desc": [
        "&c블레이즈골드&r는 철과 능력치가 같지만 철에는 없는 특별한 능력이 있습니다! "
        "\\n\\n각 아이템의 설명에서 자세한 기능을 확인해 보세요."
    ],
    "quest.1A8440C0048EEB02.title": "&c블레이즈골드 방어구",
    "quest.3DF1435A15515DA9.quest_desc": [
        "영혼을 자동으로 얻으려면 &3&lJust Dire Things&r의 기계 몇 대가 필요합니다. "
        "\\n먼저 영혼 모래를 놓도록 설정한 블록 배치기를 준비하세요. \\n\\n그다음 영혼 "
        "모래가 놓일 자리에 영혼 추출기를 든 고급 클릭기를 설치합니다. 클릭 유지로 설정하고 "
        "충분한 틱 동안 누르게 해야 합니다. \\n\\n마지막으로 영혼 모래가 놓이는 자리를 부술 "
        "고급 블록 파괴기를 설치하세요. 영혼 없는 모래만 부수도록 필터를 설정하고 도구를 "
        "넣는 것도 잊지 마세요! \\n\\n일반 블록 배치기를 제외한 기계에는 에너지가 필요하며, "
        "고급 블록 파괴기와 고급 클릭기에는 내구도가 있는 도구가 필요합니다.",
        "{@pagebreak}",
        "{image:atm:textures/questpics/forbidden/forbidden_autosoul.png width:150 height:100 align:center}",
        "이미지에서는 왼쪽이 파괴기, 아래쪽이 배치기, 오른쪽이 클릭기입니다. 기계의 상대적인 "
        "배치만 맞으면 방향은 중요하지 않습니다!",
    ],
    "quest.3DF1435A15515DA9.title": "영혼 자동화",
    "quest.40C068B2B8AC0F33.quest_desc": [
        "지형 다듬기는 간단한 건축에서도 중요하지만, 우리 &2&lMinecraft&r 플레이어에게는 "
        "그럴 시간과 노력이 부족합니다. \\n\\n그렇다면 기계에 맡겨 보는 건 어떨까요? "
        "\\n\\n채석장은 손쉬운 방법이며 모두 블록 파괴기에서 시작합니다. 간단한 블록 파괴기는 "
        "바로 앞의 블록만 부숩니다. 그다지 편리하지 않죠... \\n\\n하지만 고급 블록 파괴기는 "
        "설정한 영역 전체를 채굴하므로 지형을 다듬기에 훨씬 좋습니다!"
    ],
    "quest.4E014B495668A601.quest_desc": [
        "이제 &a경험치 저장기&r가 &a경험치&r를 모으고 있으니 &a경험치 유체&r를 "
        "&c&l자동 단조&r로 보내면 됩니다!"
    ],
    "quest.4E014B495668A601.title": "&a경험치 유체&r",
    "quest.5660E81BBEED6DC3.quest_desc": [
        "&d영혼 결속 수정&r은 가장 제작하기 어려운 수정입니다. \\n&3엔더 진주 조각&r은 "
        "&3엔더 진주&r로 만들 수 있고, 엔더 진주는 &5엔더맨&r에게서 얻을 수 있습니다. "
        "추출기로 &5자수정&r을 무한히 만들 수 있으며 석영은 &2&lMA&r로 재배할 수 있습니다. "
        "\\n\\n이제 영혼을 준비해야 합니다. 먼저 일반 영혼이 필요합니다! 보통 영혼 모래에 영혼 "
        "추출기를 사용해 영혼을 꺼냅니다. \\n\\n하지만 아이템을 직접 사용해야 하고 영혼 모래도 "
        "변합니다. 먼저 &3&lJust Dire Things&r의 클릭기로 플레이어의 사용 동작을 대신할 수 "
        "있습니다! \\n\\n이후 영혼 없는 모래를 영혼 모래로 바꿔 놓으면 됩니다. 이 과정에는 역시 "
        "&3&lJust Dire Things&r의 블록 파괴기와 배치기를 사용할 수 있습니다. \\n\\n영혼을 "
        "&5Corrupti Dust&r 및 갇힌 영혼(&5Lunar Guardian&r에게서 얻음)과 결합하면 타락한 "
        "영혼을 만들 수 있습니다. \\n\\n마지막으로 영혼을 Liquid Aureal 및 성스러운 수류탄과 "
        "결합해 마법 부여된 영혼을 만드세요. 성스러운 수류탄은 &c&lReliquary&r 제작법 계열에 "
        "있습니다."
    ],
    "quest.6A46A9F04D2A0748.quest_desc": [
        "Direwolf는 모드가 적용된 Minecraft를 대표하는 이름이며, &3&lJust Dire Things&r는 "
        "그가 만든 모드 중 하나입니다. \\n\\n이 모드는 구를 중심으로 진행됩니다. 네, 정말 매력적으로 "
        "들리죠!"
    ],
    "quest.6A46A9F04D2A0748.title": "&3&lJust Dire Things",
    "quest.6D1E8399AD39FFC8.quest_desc": [
        "&7패러독스 기계&r는 많은 에너지와 &a시간 유체&r를 소비해 지정한 영역의 블록과 "
        "엔티티를 스냅샷으로 저장한 뒤 복제할 수 있습니다. \\n\\n설정에서 많은 블록과 "
        "엔티티를 차단하므로 벌을 복제할 수는 없습니다!"
    ],
    "quest.6D1E8399AD39FFC8.title": "&7패러독스 기계",
    "task.68667F586AF5D058.title": "Just Dire Things 다이아몬드 곡괭이",
    "quest.0FAF274ADA65B26A.quest_desc": [
        (
            "포털 유체는 고급 포털 건 작동에 꼭 필요한 신비한 초록색 유체입니다.\\n\\n"
            "포털 유체 촉매를 다형성 유체에 떨어뜨리면 불안정한 포털 유체가 만들어집니다. "
            "단, 불안정한 포털 유체는 엔드에서만 존재할 수 있습니다. 세 번째 티어 이상의 구를 "
            "확산시키면 불안정한 포털 유체가 포털 유체로 변환됩니다."
        )
    ],
    "quest.079A415488A32076.quest_desc": [
        "블레이즈 엠버는 JDT가 추가하는 새로운 재료입니다. 두 번째 티어 이상의 구를 "
        "프라이멀 석탄 블록에 확산시키면 얻을 수 있으며, 블레이즈 엠버 광석에는 "
        "행운 마법 부여가 적용됩니다."
    ],
    "quest.09D2137B4F42006E.quest_desc": [
        "이클립스 엠버는 JDT가 추가하는 새로운 재료입니다. 네 번째 티어의 구를 "
        "보이드플레임 석탄 블록에 확산시키면 얻을 수 있으며, 이클립스 엠버 광석에는 "
        "행운 마법 부여가 적용됩니다."
    ],
    "quest.1705175C20CE91DD.quest_desc": [
        "이클립스 합금은 JDT가 추가하는 새로운 재료입니다. 네 번째 티어의 구를 "
        "네더라이트 블록에 확산시키면 얻을 수 있으며, 이클립스 합금 광석에는 "
        "행운 마법 부여가 적용됩니다."
    ],
    "quest.16E02F671FBE9148.quest_desc": [
        "포털 건은 에너지를 사용해 두 지점 사이를 오가는 포털 두 개를 만듭니다. 좌클릭하면 "
        "파란색 포털, 우클릭하면 주황색 포털을 발사하며 Shift + 우클릭하면 두 포털을 모두 "
        "제거합니다."
    ],
    "quest.200ECDC70E97D254.quest_desc": [
        "연료 캔은 내부 유체로 다른 용기를 채울 수 있는 탱크입니다.\\n\\n연료 캔에는 세 가지 "
        "채움 모드가 있습니다.\\n\\n - 없음\\n - 모두\\n - Just Dire Things"
    ],
    "quest.2D86D4403E0F4EB9.quest_desc": [
        "블레이즈골드는 JDT가 추가하는 새로운 재료입니다. 두 번째 티어 이상의 구를 "
        "금 블록에 확산시키면 얻을 수 있으며, 블레이즈골드 광석에는 행운 마법 부여가 "
        "적용됩니다.",
        "",
        "블레이즈골드 도구와 방어구에는 용암 수리 고유 능력이 있습니다. 도구나 방어구를 "
        "용암 원천 블록에 떨어뜨리면 해당 블록을 흑요석으로 바꾸는 대신 내구도를 수리합니다.",
    ],
    "quest.3D9964CB0440DD5A.quest_desc": [
        "블레이즈 엠버를 다형성 유체에 떨어뜨리면 정제되지 않은 블레이즈 엠버 연료가 "
        "생성됩니다. 두 번째 티어 이상의 구를 확산시키면 블레이즈 엠버 연료로 변환됩니다."
    ],
    "quest.3971FF7D044D1FE5.quest_desc": [
        "방어구 능력은 설정 화면에서 구성하고 켜거나 끌 수 있습니다. JDT 도구나 지팡이로 "
        "화면을 연 뒤 방어구를 클릭하면 각 부위의 능력을 설정할 수 있습니다."
    ],
    "quest.446A37C7FCDACF84.quest_desc": [
        "보이드플레임 석탄은 JDT가 추가하는 새로운 재료입니다. 세 번째 티어 이상의 구를 "
        "블레이즈 엠버 블록에 확산시키면 얻을 수 있으며, 보이드플레임 석탄 광석에는 "
        "행운 마법 부여가 적용됩니다."
    ],
    "quest.49EF8A4346AEF582.quest_desc": [
        "이클립스 엠버를 보이드플레임 연료에 떨어뜨리면 정제되지 않은 이클립스 엠버 연료가 "
        "생성됩니다. 네 번째 티어의 구를 확산시키면 이클립스 엠버 연료로 변환됩니다."
    ],
    "quest.4B3F20E5C7E3BCFB.quest_desc": [
        "프라이멀 석탄은 JDT가 추가하는 새로운 재료입니다. 첫 번째 티어 이상의 구를 "
        "석탄 블록에 확산시키면 얻을 수 있으며, 프라이멀 석탄 광석에는 행운 마법 부여가 "
        "적용됩니다."
    ],
    "quest.5BD5737703F3F077.quest_desc": [
        "페리코어는 JDT가 추가하는 새로운 재료입니다. 첫 번째 티어 이상의 구를 철 블록에 "
        "확산시키면 얻을 수 있으며, 페리코어 광석에는 행운 마법 부여가 적용됩니다."
    ],
    "quest.60A4994078500F63.quest_desc": [
        "셀레스티젬은 JDT가 추가하는 새로운 재료입니다. 세 번째 티어 이상의 구를 다이아몬드 "
        "블록에 확산시키면 얻을 수 있으며, 셀레스티젬 광석에는 행운 마법 부여가 적용됩니다."
    ],
    "quest.70BF85E2D235BAD5.quest_desc": [
        "보이드플레임 석탄을 블레이즈 엠버 연료에 떨어뜨리면 정제되지 않은 보이드플레임 "
        "연료가 생성됩니다. 세 번째 티어 이상의 구를 확산시키면 보이드플레임 연료로 변환됩니다."
    ],
    "quest.7B9486981786AC47.quest_desc": [
        "&l능력 유형:&r 액티브",
        "",
        "&l능력 기능:&r",
        "",
        "주변 몹의 AI를 영구적으로 제거합니다. 에너지 비용이 커서 한 번에 최대 다섯 마리에게만 "
        "적용되며, 재사용 대기 시간이 매우 깁니다.",
    ],
    "quest.05D8C6EF8FCD6250.quest_desc": [
        "프라이모젤 구는 JDT가 추가하는 첫 번째 티어의 구이며, 오버월드의 기본 재료로 제작합니다.",
        "",
        "해금되는 제작법:",
        "- 페리코어",
        "- 프라이멀 석탄",
        "",
        "구 확산 예시:",
        "",
        "{image:atm:textures/questpics/justdirethings/goo_spread_ferricore.png width:200 height:200 align:center}",
    ],
    "quest.4C54BD57CAB8A54B.quest_desc": [
        "블레이즈블룸 구는 JDT가 추가하는 두 번째 티어의 구이며, 네더 재료로 제작합니다.",
        "",
        "해금되는 제작법:",
        "- 블레이즈골드",
        "- 블레이즈 엠버",
    ],
    "quest.5C6709350BEF4050.quest_desc": [
        "보이드시머 구는 JDT가 추가하는 세 번째 티어의 구이며, 엔드 재료로 제작합니다.",
        "",
        "해금되는 제작법:",
        "- 셀레스티젬",
        "- 보이드플레임 석탄",
    ],
    "quest.25213DBA6E6CEDD2.quest_desc": [
        "섀도우펄스 구는 JDT가 추가하는 네 번째이자 마지막 티어의 구이며, 고대 도시와 "
        "워든의 재료로 제작합니다.",
        "",
        "해금되는 제작법:",
        "- 이클립스 합금",
        "- 이클립스 엠버",
        "- 시간 수정",
    ],
    "quest.1EA02BA24AF02256.quest_desc": [
        "이클립스 합금 형판은 마법 부여와 설치된 업그레이드를 유지하면서 셀레스티젬 "
        "방어구와 도구를 이클립스 합금으로 업그레이드할 때 사용합니다."
    ],
    "quest.2409EAD96CE3BDF7.quest_desc": [
        "블레이즈골드 형판은 마법 부여와 설치된 업그레이드를 유지하면서 페리코어 "
        "방어구와 도구를 블레이즈골드로 업그레이드할 때 사용합니다."
    ],
    "quest.25E915AE1FC53254.quest_desc": [
        "셀레스티젬 형판은 마법 부여와 설치된 업그레이드를 유지하면서 블레이즈골드 "
        "방어구와 도구를 셀레스티젬으로 업그레이드할 때 사용합니다."
    ],
    "quest.27FD46A8C958D259.quest_desc": [
        "죽음 귀환의 토템은 플레이어가 사망한 위치로 돌아갈 수 있게 해 주는 일회용 아이템입니다."
    ],
    "quest.41E8C93A44559E48.quest_desc": [
        "&7패러독스 기계&r는 많은 에너지와 &a시간 유체&r를 소비해 지정한 영역의 블록과 "
        "엔티티를 스냅샷으로 저장한 뒤 복제할 수 있습니다. \\n\\n설정에서 많은 블록과 "
        "엔티티를 차단하므로 벌을 복제할 수는 없습니다!"
    ],
    "quest.441F37A95AB66E6B.quest_desc": [
        "이 퀘스트는 AllTheMods 모드팩에서 사용하도록 &6AllTheMods Staff&r 또는 "
        "&2커뮤니티 기여자&r가 작성했습니다. \\n\\n모든 &6AllTheMods&r 팩은 "
        "&eAll Rights Reserved&r로 배포되므로, &6AllTheMods Team&r의 명시적 허가 없이 "
        "다른 공개 모드팩에서 이 퀘스트를 사용할 수 없습니다. \\n\\n이 퀘스트는 의도적으로 "
        "숨겨져 있습니다. 이 문구가 보인다면 편집 모드에 있는 것입니다."
    ],
    "quest.4458F8829800A950.quest_desc": [
        "다형성 유체는 JDT의 모든 유체와 연료의 기반입니다. 다형성 촉매를 물에 떨어뜨리면 "
        "다형성 유체가 만들어집니다."
    ],
    "quest.48E4D75FD3145AD6.quest_desc": [
        "시간 유체는 패러독스 기계와 시간 지팡이에 사용합니다. 시간 수정을 다형성 유체에 "
        "떨어뜨리면 얻을 수 있습니다.\\n\\n얻기 힘든 수정에 비해 유체를 만드는 방법은 "
        "간단해서 다행이네요."
    ],
    "quest.4F9932477EDDCB8E.quest_desc": [
        "고급 포털 건은 에너지와 포털 유체로 작동하는 포털 건의 상위 버전입니다. 일반 "
        '포털 건과 달리 저장한 위치 사이를 순간이동할 수 있습니다. 기본 단축키인 "V"를 '
        "누르면 목적지를 저장하고 선택하는 메뉴가 열립니다."
    ],
    "quest.53F9E5CE7EE6F852.quest_desc": [
        "생물 포획기는 몹을 붙잡아 운반할 수 있게 해 줍니다. 엔티티 태그로 포획할 수 없는 "
        "몹을 지정할 수 있습니다."
    ],
    "quest.5B02719C13B1FFE2.quest_desc": [
        "능력:",
        "- 공기 폭발: 발사 거리가 더 늘어납니다.",
        "- 보이드 시프트: 순간이동 거리가 늘어납니다.",
        "- 이클립스 게이트: 대상 블록의 면을 기준으로 3x3 영역에 휴대용 구멍을 만듭니다. "
        "구멍의 거리를 설정할 수 있으며 블록 엔티티에는 사용할 수 없습니다.",
    ],
    "quest.5EE7D5DE07A83C7D.quest_desc": [
        "&l능력 유형:&r 액티브\\n\\n&l능력 기능:&r\\n\\n활성화하면 주변 광석을 초록색 "
        "입자로 표시합니다.\\n\\n&4&l참고: 이 능력은 비활성화되어 있습니다.&r&f"
    ],
    "quest.636854555AD75DC3.quest_desc": [
        "&l능력 유형:&r 패시브",
        "",
        "&l능력 기능:&r",
        "",
        "아이템 전리품을 도구에 연결한 인벤토리로 자동 순간이동시킵니다. 인벤토리에 대고 "
        "도구를 Shift + 우클릭하면 연결됩니다. JDT 괭이의 자동 수확으로 보이드시머 또는 "
        "섀도우펄스 경작지에서 나온 아이템도 연결된 인벤토리로 이동합니다. 도구의 연결 "
        "대상이 바뀌었다면 해당 경작지를 우클릭하여 다시 연결하세요.",
    ],
    "quest.6ADE6F9E004055F7.quest_desc": [
        "시간 수정은 JDT가 추가하는 새로운 재료입니다. 싹트는 자수정이나 시간 수정 블록에 "
        "구를 확산시키면 싹트는 시간 수정 블록이 만들어지고, 그 위에서 시간 수정 군집이 "
        "자랍니다.\\n\\n하지만 싹트는 시간 수정 블록은 군집을 키우기 전에 &9오버월드&r, "
        "&6네더&r, &a엔드&r의 시간을 모두 모아야 합니다. 이 블록은 파괴하거나 섬세한 손길로 "
        "채굴할 수 없습니다. 교환기, Cardboard Box 또는 Cut Paste Gadget으로 옮기세요."
        "\\n\\n시간이 지나면 싹트는 시간 수정 블록의 &2에너지가 바닥나며&r, 다시 &9오버월드&r, "
        "&6네더&r, &a엔드&r를 차례로 거쳐야 합니다.",
        "{@pagebreak}",
        "이 과정을 자동화하려면 퀘스트 위 이미지에 연결된 영상을 참고하세요.\\n\\n이전 페이지의 "
        "&2색&9상 &6표&a현&r만으로 구분하기 어렵다면 아래 이미지에서 싹트는 시간 수정 블록의 "
        "각 단계를 확인할 수 있습니다.",
        "",
        "{image:atm:textures/questpics/justdirethings/budding_time_crystal_reference.png width:250 height:125 align:center}",
    ],
    "quest.7305EE0F7D73C231.quest_desc": [
        "빈 업그레이드는 모든 능력의 기반입니다. 능력은 패시브와 액티브, 두 종류로 나뉩니다."
        "\\n\\n패시브 능력은 별도 조작 없이 작동하지만 액티브 능력은 설정 화면에서 지정한 키를 "
        "눌러야 작동하며, 사용할 때 내구도나 에너지를 소비합니다. 높은 티어의 방어구에 "
        "설치하면 액티브 능력의 재사용 대기 시간이 줄고 패시브 능력의 효과가 커집니다."
        "\\n\\n대장장이 작업대에서 JDT 도구와 방어구에 업그레이드를 적용할 수 있습니다. "
        "JDT 도구나 방어구에 마우스를 올리고 Shift를 누르면 적용 가능한 업그레이드가 표시됩니다."
    ],
    "quest.76B1C5AFC5D6B7CF.quest_desc": [
        "시간 지팡이는 시간이 담긴 병처럼 블록의 작동 속도를 최대 x128까지 높입니다. 저장된 "
        "시간 대신 FE와 시간 유체를 연료로 사용하므로 훨씬 쉽게 다시 채울 수 있습니다."
        "\\n\\n단, 가짜 플레이어는 사용할 수 없습니다. 이것만큼은 자동화하지 마세요."
    ],
    "quest.7F0B2D58361FB00E.quest_desc": [
        "Just Dire Things는 여러 분야를 두루 다루는 모드입니다. 구 확산이라는 새로운 제작 "
        "방식과 이를 자동화하는 기계, 그 밖의 다양한 유틸리티를 추가합니다."
    ],
    "quest.7AEFF81E7C8CF300.quest_desc": [
        "JDT 도구나 지팡이를 든 채 Shift + 우클릭하면 능력을 설정하고 켜거나 끌 수 있는 "
        "화면이 열립니다."
    ],
    "quest.1705175C20CE91DD.title": "이클립스 합금",
    "quest.2D86D4403E0F4EB9.title": "블레이즈골드",
    "quest.4E9B35DCA018FD42.title": "도구 업그레이드",
    "quest.5BD5737703F3F077.title": "페리코어",
    "quest.67B87570C340C243.title": "방어구 업그레이드",
    "quest.6ADE6F9E004055F7.quest_subtitle": "시간이 꼬이고 또 꼬이고",
    "quest.6ADE6F9E004055F7.title": "시간 수정",
    "quest.76B1C5AFC5D6B7CF.quest_subtitle": "시간이 담긴 병의 사촌",
    "quest.7F0B2D58361FB00E.title": "Just Dire Things",
    "task.00B0A3B14DEB34B9.title": "혼합 업그레이드",
    "task.03982D782B426ABB.title": "모든 권리 보유",
    "task.0FB06A55F5FE6F26.title": "",
    "task.19931057AAC1A03A.title": "모든 권리 보유",
    "task.32309011F80C0A9E.title": "참고",
    "task.366CA7D53571A552.title": "유틸리티",
    "task.3AC95E8DC4229D17.title": "Just Dire Things",
    "task.3CAD6AD06BE4C3D3.title": "도구",
    "task.40B39896B6CD41C6.title": "방어구",
    "task.5AB4103FF540ABB4.title": "유체",
    "task.5DD919AF75C92C8A.title": "도구",
    "task.665A5DFA6270ADA6.title": "간단한 기계",
    "task.67B21CF59C3D02E5.title": "고급 기계",
    "task.7197FBBA21C0F94A.title": "방어구",
}

ALLOWED_EXACT_KEYS = {
    "quest.6A46A9F04D2A0748.title",
    "quest.7F0B2D58361FB00E.title",
    "task.0FB06A55F5FE6F26.title",
    "task.3AC95E8DC4229D17.title",
}

PRETRANSLATIONS = {
    "Just Dire Things": "Just Dire Things",
    "JustDireThings": "Just Dire Things",
    "Eclipse Alloy": "이클립스 합금",
    "Primal Coal": "프라이멀 석탄",
    "Blaze Ember": "블레이즈 엠버",
    "Voidflame Coal": "보이드플레임 석탄",
    "Voidflame": "보이드플레임",
    "Eclipse Ember": "이클립스 엠버",
    "Primogel Goo": "프라이모젤 구",
    "Blazebloom Goo": "블레이즈블룸 구",
    "VoidShimmer Goo": "보이드시머 구",
    "Shadowpulse Goo": "섀도우펄스 구",
    "Ferricore": "페리코어",
    "Blazegold": "블레이즈골드",
    "Celestigem": "셀레스티젬",
    "Polymorphic Fluid": "다형성 유체",
    "Portal Fluid": "포털 유체",
    "Time Fluid": "시간 유체",
    "Time Crystal": "시간 수정",
    "Paradox Machine": "패러독스 기계",
    "Time Wand": "시간 지팡이",
    "Portal Gun": "포털 건",
    "Potion Canister": "물약 캔",
    "Player Accessor": "플레이어 접근기",
    "Machine Settings Copier": "기계 설정 복사기",
    "Creature Catcher": "생물 포획기",
    "Energy Transmitter": "에너지 송신기",
    "Goo Spreading": "구 확산",
    "Goo Spread": "구 확산",
    "Valid Upgrades": "적용 가능한 업그레이드",
    "Intrinsic Ability": "고유 능력",
    "Ability Type": "능력 유형",
    "Ability Function": "능력 기능",
    "Passive": "패시브",
    "Active": "액티브",
}

TEXT_REPLACEMENTS = (
    ("저스트 다이어 띵스", "Just Dire Things"),
    ("오직 다이어 무언가", "Just Dire Things"),
    ("JustDireThings", "Just Dire Things"),
    ("다형성 액체", "다형성 유체"),
    ("차원문 액체", "포털 유체"),
    ("차원문 총", "포털 건"),
    ("포탈", "포털"),
    ("원시 석탄", "프라이멀 석탄"),
    ("블레이즈 불씨", "블레이즈 엠버"),
    ("공허 화염 석탄", "보이드플레임 석탄"),
    ("공허 불꽃 석탄", "보이드플레임 석탄"),
    ("공허불꽃", "보이드플레임"),
    ("공허빛 구", "보이드시머 구"),
    ("그림자 펄스 구", "섀도우펄스 구"),
    ("프라이모겔", "프라이모젤"),
    ("끈적이 퍼뜨리기", "구 확산"),
    ("끈적이를 퍼뜨려", "구를 확산시켜"),
    ("끈적이을", "구를"),
    ("끈적이를", "구를"),
    ("끈적이", "구"),
    ("상위 버전으로 변환", "업그레이드"),
    ("상위 버전 변환", "업그레이드"),
    ("유효한 업그레이드", "적용 가능한 업그레이드"),
    ("사용 가능한 업그레이드", "적용 가능한 업그레이드"),
    ("텔레포터 떨굼", "전리품 순간이동"),
    ("광물 스캐너", "광석 스캐너"),
    ("하늘 청소부", "낙하물 제거"),
    ("스카이 스위퍼", "낙하물 제거"),
    ("잎 파괴기", "나뭇잎 파괴"),
    ("허수아비", "미끼"),
    ("진화", "소화"),
    ("지혈", "상처 지혈"),
    ("자동 제련기", "자동 제련"),
    ("자동 훈연기", "자동 훈연"),
    ("용암 능력", "용암 수리"),
    ("에어 폭발형", "공기 폭발"),
    ("공허 Shift", "보이드 시프트"),
    ("무효화 Shift", "보이드 시프트"),
    ("타일 엔티티", "블록 엔티티"),
    ("모드 팩", "모드팩"),
    ("업데이트 적용", "적용 가능한 업그레이드"),
    ("고유능력", "고유 능력"),
    ("용암수리", "용암 수리"),
    ("자동제련", "자동 제련"),
    ("나무벌목", "나무 벌목"),
    ("야간투시", "야간 투시"),
    ("플레이어 접속자", "플레이어 접근기"),
    ("단순 교환기", "간단한 교환기"),
    ("스왑퍼", "교환기"),
    ("블록 차단기", "블록 파괴기"),
    ("단순한 블록 배치기", "간단한 블록 배치기"),
    ("단순한 유체 수집기", "간단한 유체 수집기"),
    ("단순한 유체 배치기", "간단한 유체 배치기"),
    ("단순한 석탄 발전기", "간단한 석탄 발전기"),
    ("액체 연료 생성기", "유체 연료 발전기"),
    ("왼쪽 클릭", "좌클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("Shift 오른쪽 클릭", "Shift + 우클릭"),
    ("Shift Right", "Shift + 우클릭"),
    ("창의적인 비행", "크리에이티브 비행"),
    ("전력", "에너지"),
)

LIST_LABELS = {
    "Valid Upgrades:": "적용 가능한 업그레이드:",
    "Valid Upgrade:": "적용 가능한 업그레이드:",
    "Intrinsic Ability:": "고유 능력:",
    "Intrisic Ability:": "고유 능력:",
    "Abilities:": "능력:",
    "Abilites:": "능력:",
    "Crafts Unlocked:": "해금되는 제작법:",
    "Goo Spread Example:": "구 확산 예시:",
    "&lAbility Type:&r Active": "&l능력 유형:&r 액티브",
    "&lAbility Type:&r Passive": "&l능력 유형:&r 패시브",
    "&lAbility Function:&r": "&l능력 기능:&r",
    "&lAbility Function:": "&l능력 기능:",
    "&lAbility Function:&r ": "&l능력 기능:&r ",
}

LIST_ITEMS = {
    "No Trampling": "밭 짓밟기 방지",
    "Auto Havesting": "자동 수확",
    "Auto Harvesting": "자동 수확",
    "Accelerated Crop Growth I": "작물 성장 가속 I",
    "Accelerated Crop Growth II": "작물 성장 가속 II",
    "Accelerated Crop Growth III": "작물 성장 가속 III",
    "Accelerated Crop Growth IV": "작물 성장 가속 IV",
    "Lava Ability": "용암 수리",
    "Void Flame": "보이드플레임 석탄",
}

DESCRIPTION_OVERRIDES = {
    "Removes all negative debuffs from the player when activated, has a cooldown.": (
        "활성화하면 플레이어의 모든 해로운 효과를 제거하며, 재사용 대기 시간이 있습니다."
    ),
    "Breaks nearby grass and flowers when activated.": "활성화하면 주변의 풀과 꽃을 파괴합니다.",
    "Temporarily makes nearby hostile mobs loose aggro to the player, has a cooldown.": (
        "활성화하면 주변의 적대적 몹이 잠시 플레이어를 인식하지 못하며, 재사용 대기 시간이 있습니다."
    ),
    "Temporarily makes the player immune to damage when activated, has a cooldown.": (
        "활성화하면 잠시 피해를 받지 않으며, 재사용 대기 시간이 있습니다."
    ),
    "Increases the jump height of the player.": "플레이어의 점프 높이를 높입니다.",
    "Breaks nearby leaves when activated.": "활성화하면 주변의 나뭇잎을 파괴합니다.",
    "Grants the player Night Vision.": "플레이어에게 야간 투시를 부여합니다.",
    "Makes Arrows chain to nearby enemies.": "화살이 주변의 적에게 연쇄적으로 적중합니다.",
    "Increases walking speed.": "걷기 속도를 높입니다.",
    "Automatically smelts items dropped from mined blocks.": "채굴한 블록의 전리품을 자동으로 제련합니다.",
    "Provides step assist to the player.": "플레이어가 한 블록 높이를 자동으로 오를 수 있게 합니다.",
    "Highlights nearby mobs with particles when activated.": "활성화하면 주변 몹을 입자로 표시합니다.",
    "An upgraded version of Ore Scanner that renders nearby ores when activated.": (
        "활성화하면 주변 광석을 표시하는 광석 스캐너의 상위 능력입니다."
    ),
    "An upgraded version of Ground Stomp that repels and slows nearby mobs, has a cooldown.": (
        "주변 몹을 밀쳐 내고 느리게 만드는 지면 강타의 상위 능력이며, 재사용 대기 시간이 있습니다."
    ),
    "An upgraded version of Mob Scanner that applies Glowing to nearby mobs when activated.": (
        "활성화하면 주변 몹에 발광 효과를 부여하는 몹 스캐너의 상위 능력입니다."
    ),
    "Provides minor healing when activated, but can only be actived if the player has recently taken damage or is taking damage.": (
        "활성화하면 조금 회복합니다. 최근에 피해를 받았거나 현재 피해를 받는 중일 때만 사용할 수 있습니다."
    ),
    "Mines adjacent ore blocks all at once, but takes slightly longer to mine.": (
        "서로 붙은 광석 블록을 한꺼번에 채굴하지만 채굴 시간이 조금 늘어납니다."
    ),
    "Provides the player with an Elytra, note the Elytra provided by this upgrade is affected by the Walk and Run Speed upgrades.": (
        "플레이어에게 겉날개 기능을 부여합니다. 이 겉날개는 걷기 속도와 달리기 속도 "
        "업그레이드의 영향을 받습니다."
    ),
    "Extinguishes the player if they are on fire, has a cooldown.": (
        "플레이어에게 붙은 불을 끄며, 재사용 대기 시간이 있습니다."
    ),
    "Increases running speed.": "달리기 속도를 높입니다.",
    "Reduces the detection range of hostile mobs.": "적대적 몹이 플레이어를 감지하는 범위를 줄입니다.",
    "Makes Potion Arrows fired by the Bow have a Splash effect, hitting multiple targets in an area.": (
        "활에서 발사한 물약 화살에 투척형 효과를 부여해 범위 안의 여러 대상에게 적중시킵니다."
    ),
    "Makes Arrows actively seek their targets.": "화살이 대상을 추적합니다.",
    "Allows the player to walk though blocks when applied to leggings. There is a block tag to blacklist blocks from being able to be phased through.": (
        "레깅스에 적용하면 블록을 통과해 이동할 수 있습니다. 통과할 수 없는 블록은 블록 "
        "태그로 지정할 수 있습니다."
    ),
    "When applied to a bow, allows arrows to phase through walls.": "활에 적용하면 화살이 벽을 통과합니다.",
    "Allows the tool to instantly mine blocks.": "도구로 블록을 즉시 채굴할 수 있게 합니다.",
    "Automatically clears any blocks affected by gravity directly above the block mined.": (
        "채굴한 블록 바로 위에서 중력의 영향을 받는 블록을 자동으로 제거합니다."
    ),
    "Grants the player creative flight.": "플레이어에게 크리에이티브 비행을 부여합니다.",
    "Spawns a decoy of the player that pulls aggro away from the player, has a cooldown.": (
        "몹의 공격을 대신 끌어당기는 미끼를 소환하며, 재사용 대기 시간이 있습니다."
    ),
    "Automatically smokes items dropped by kills.": "처치한 몹의 전리품을 자동으로 훈연합니다.",
    "Increases area mined at once. When installed on higher tier tools the maximum area mined is increased. Mined area can be configured in the menu.": (
        "한 번에 채굴하는 영역을 넓힙니다. 높은 티어의 도구에 설치할수록 최대 영역이 "
        "커지며, 설정 화면에서 채굴 영역을 조정할 수 있습니다."
    ),
    "Makes Potion Arrows fired by the bow have a Lingering effect, applying effects to an area over time.": (
        "활에서 발사한 물약 화살에 잔류형 효과를 부여해 일정 시간 범위 효과를 남깁니다."
    ),
    "Repels nearby mobs when activated, has a cooldown.": (
        "활성화하면 주변 몹을 밀쳐 내며, 재사용 대기 시간이 있습니다."
    ),
    "Makes the player immune to lava.": "플레이어가 용암 피해를 받지 않게 합니다.",
    "Allows the player to cheat death, has a very long cooldown. So otherwise a Totem of Undying with a cooldown that isn't consumed.": (
        "죽음을 한 번 피할 수 있지만 재사용 대기 시간이 매우 깁니다. 소모되지 않는 대신 "
        "재사용 대기 시간이 있는 불사의 토템과 같습니다."
    ),
    "The player accessor acts as a chest that interfaces with the player's inventory. Using the GUI the player accessor can have its sides configured to interface with the player's inventory, off-hand or armor slots.": (
        "플레이어 접근기는 플레이어의 인벤토리와 연결되는 상자처럼 작동합니다. 설정 화면에서 "
        "각 면을 일반 인벤토리, 보조 손 또는 방어구 슬롯에 연결할 수 있습니다."
    ),
    "The simple swapper can teleport items, blocks, mobs or players above it to another simple swapper it is linked to. To link swappers use the Ferricore wrench.": (
        "간단한 교환기는 위에 있는 아이템, 블록, 몹 또는 플레이어를 연결된 다른 간단한 "
        "교환기로 순간이동시킵니다. 페리코어 렌치로 두 교환기를 연결하세요."
    ),
    "A simple dropper and you can configure the amount dropped at once.": (
        "한 번에 배출할 수량을 설정할 수 있는 간단한 공급기입니다."
    ),
    "The item collecter collects items and deposits them into the inventory below it.": (
        "아이템 수집기는 아이템을 모아 아래쪽 인벤토리에 넣습니다."
    ),
    "The Pocket Generator is a handheld generator that uses burnable items to charge items and tools in the player's inventory, the Pocket Generator is compatible with the Fuel Canister.": (
        "휴대용 발전기는 연소 가능한 아이템으로 플레이어 인벤토리의 아이템과 도구를 "
        "충전합니다. 연료 캔과 함께 사용할 수 있습니다."
    ),
    "The Ferricore Wrench allows the player to rotate machines, but it is also used to link swappers together.": (
        "페리코어 렌치는 기계를 회전하거나 교환기끼리 연결할 때 사용합니다."
    ),
    "All simple machines come with redstone control, and some come with filtering.": (
        "모든 간단한 기계는 레드스톤 제어를 지원하며, 일부는 필터도 제공합니다."
    ),
    "Advanced machines have the same capabilities as their simple variants with the addition of configurable working area, more filter slots and requiring power.": (
        "고급 기계는 간단한 기계와 같은 기능에 설정 가능한 작동 영역과 더 많은 필터 슬롯이 "
        "추가되며, 작동할 때 에너지가 필요합니다."
    ),
    "The energy transmitter provides power to blocks within its working range, it can only accept power from the bottom.": (
        "에너지 송신기는 작동 범위 안의 블록에 에너지를 공급하며 아래쪽 면으로만 에너지를 받습니다."
    ),
    "A simple block breaker that requires a tool to break blocks.": (
        "도구를 넣어 블록을 파괴하는 간단한 블록 파괴기입니다."
    ),
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


def iter_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for child in value for text in iter_strings(child)]
    return []


def map_strings(value: object, translations: dict[str, str]) -> object:
    if isinstance(value, str):
        return translations[value]
    if isinstance(value, list):
        return [map_strings(child, translations) for child in value]
    return value


def item_name_pairs() -> tuple[tuple[str, str], ...]:
    english = language.load_json(
        PROJECT_ROOT / "working/just_dire_things/justdirethings/en_us.json"
    )
    korean = language.load_json(
        PROJECT_ROOT / "working/just_dire_things/justdirethings/ko_kr.json"
    )
    pairs = [
        (source, korean[key])
        for key, source in english.items()
        if key.startswith(("block.", "item.", "fluid_type.", "entity."))
        and isinstance(source, str)
        and isinstance(korean[key], str)
    ]
    return tuple(sorted(pairs, key=lambda row: len(row[0]), reverse=True))


def prepare_source(source: str, pairs: tuple[tuple[str, str], ...]) -> str:
    value = source
    for old, new in pairs:
        value = value.replace(old, new)
    for old, new in sorted(
        PRETRANSLATIONS.items(), key=lambda row: len(row[0]), reverse=True
    ):
        value = value.replace(old, new)
    for old, new in sorted(
        language.ABILITY_NAMES.items(), key=lambda row: len(row[0]), reverse=True
    ):
        value = value.replace(old, new)
    return value


def candidate() -> dict[str, object]:
    """기존 한국어를 사용하지 않고 영어 190키 전체의 독립 후보를 만든다."""
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    pairs = item_name_pairs()
    requests: dict[str, str] = {}
    english_by_scope: dict[str, dict[str, object]] = {}
    for root in sorted(QUEST_ROOT.glob("*")):
        if not (root / "en_us.json").is_file():
            continue
        english = load_json(root / "en_us.json")
        english_by_scope[root.name] = english
        for key, value in english.items():
            if key in KEY_OVERRIDES:
                continue
            for source in iter_strings(value):
                if not source or re.fullmatch(r"\{image:[^}]+\}", source):
                    continue
                if not isinstance(cache.get(source), str):
                    requests[source] = prepare_source(source, pairs)
    failures: list[str] = []
    if requests:
        completed = 0
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(ars_family.request_translation, prepared): source
                for source, prepared in sorted(requests.items())
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                    completed += 1
                    if completed % 20 == 0:
                        write_json(CACHE_FILE, cache)
                except Exception as exc:  # pragma: no cover - 외부 번역 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("퀘스트 후보 생성 실패:\n" + "\n".join(failures))

    candidates: dict[str, dict[str, object]] = {}
    for scope, english in english_by_scope.items():
        rows: dict[str, object] = {}
        for key, value in english.items():
            if key in KEY_OVERRIDES:
                rows[key] = KEY_OVERRIDES[key]
                continue
            translations = {
                source: (
                    source
                    if not source or re.fullmatch(r"\{image:[^}]+\}", source)
                    else cache[source]
                )
                for source in iter_strings(value)
            }
            rows[key] = map_strings(value, translations)
        candidates[scope] = rows
    write_json(CANDIDATE_FILE, candidates)
    report = {
        "candidate_keys": sum(len(rows) for rows in candidates.values()),
        "unique_requests": len(requests),
        "review_scope": "all_existing_and_missing_korean_independently_retranslated",
        "review_status": "candidate_requires_full_review",
    }
    write_json(QUEST_ROOT.parent / "quest_auto_candidate_report.json", report)
    return report


def review_text(value: object, pairs: tuple[tuple[str, str], ...]) -> object:
    if isinstance(value, list):
        return [review_text(child, pairs) for child in value]
    if not isinstance(value, str) or re.fullmatch(r"\{image:[^}]+\}", value):
        return value
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    for old, new in pairs:
        value = value.replace(old, new)
    for old, new in sorted(
        language.ABILITY_NAMES.items(), key=lambda row: len(row[0]), reverse=True
    ):
        value = value.replace(old, new)
    value = value.replace("해야합니다", "해야 합니다")
    value = value.replace("할 수있는", "할 수 있는")
    value = value.replace("플레이어에게서 모든", "플레이어의 모든")
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    return value


def translate_list_item(source: str, pairs: tuple[tuple[str, str], ...]) -> str:
    """업그레이드·재료 목록의 짧은 이름을 원문에서 직접 확정한다."""
    disabled = " &4&l비활성화&r&f" if "&4&lDISABLED&r&f" in source else ""
    name = source.replace(" &4&lDISABLED&r&f", "")
    translated = LIST_ITEMS.get(name)
    if translated is None:
        translated = language.ABILITY_NAMES.get(name)
    if translated is None:
        translated = language.translate_name(name)
    if translated == name:
        for old, new in pairs:
            if name == old:
                translated = new
                break
    return translated + disabled


def review_value(
    source: object,
    candidate_value: object,
    pairs: tuple[tuple[str, str], ...],
) -> object:
    """목록 구조는 영어 원문에서 다시 만들고 설명문만 독립 후보를 검수한다."""
    if not isinstance(source, list) or not isinstance(candidate_value, list):
        return review_text(candidate_value, pairs)
    if len(source) != len(candidate_value):
        return review_text(candidate_value, pairs)
    result: list[object] = []
    for source_line, candidate_line in zip(source, candidate_value, strict=True):
        if not isinstance(source_line, str) or not isinstance(candidate_line, str):
            result.append(review_text(candidate_line, pairs))
            continue
        if source_line in LIST_LABELS:
            result.append(LIST_LABELS[source_line])
            continue
        if source_line in DESCRIPTION_OVERRIDES:
            result.append(DESCRIPTION_OVERRIDES[source_line])
            continue
        if source_line.startswith("- "):
            item = source_line.removeprefix("- ")
            if ":" not in item:
                result.append("- " + translate_list_item(item, pairs))
                continue
        result.append(review_text(candidate_line, pairs))
    return result


def normalize() -> dict[str, object]:
    """독립 후보를 원문·용어·아이템 이름과 대조한 검수값으로 교체한다."""
    candidates = load_json(CANDIDATE_FILE)
    pairs = item_name_pairs()
    reviewed = 0
    changed = 0
    unresolved: list[str] = []
    for root in sorted(QUEST_ROOT.glob("*")):
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        if not english_file.is_file() or not korean_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        scope_candidates = candidates[root.name]
        for key, source in english.items():
            translated = KEY_OVERRIDES.get(
                key, review_value(source, scope_candidates[key], pairs)
            )
            errors = quest_snbt.validate_value(key, source, translated)
            if errors:
                raise ValueError("; ".join(errors))
            reviewed += 1
            if korean[key] != translated:
                korean[key] = translated
                changed += 1
            if source == translated and key not in ALLOWED_EXACT_KEYS:
                if any(
                    re.search(r"[A-Za-z]{3,}", text) for text in iter_strings(source)
                ):
                    unresolved.append(key)
        write_json(korean_file, korean)
    report = {
        "keys_reviewed": reviewed,
        "changed": changed,
        "unresolved": len(unresolved),
        "unresolved_examples": unresolved[:30],
        "review_status": "full_existing_korean_reviewed",
    }
    write_json(QUEST_ROOT.parent / "quest_normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    untranslated: list[str] = []
    reviewed = 0
    for root in sorted(QUEST_ROOT.glob("*")):
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        if not english_file.is_file() or not korean_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        if list(english) != list(korean):
            errors.append(f"키 또는 순서 불일치: {root.name}")
            continue
        for key, source in english.items():
            target = korean[key]
            errors.extend(quest_snbt.validate_value(key, source, target))
            reviewed += 1
            if source == target and key not in ALLOWED_EXACT_KEYS:
                if any(
                    re.search(r"[A-Za-z]{3,}", text) for text in iter_strings(source)
                ):
                    untranslated.append(key)
    if untranslated:
        errors.append(f"미번역 퀘스트 키: {untranslated[:30]}")
    report = {
        "keys_reviewed": reviewed,
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(QUEST_ROOT.parent / "specialized_quest_validation.json", report)
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("candidate", "normalize", "verify"))
    args = parser.parse_args()
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
