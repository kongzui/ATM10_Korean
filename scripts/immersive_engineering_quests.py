"""Immersive Engineering FTB Quests 번역을 정규화하고 검증한다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import build_ae2_quests as quest_snbt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUEST_ROOT = PROJECT_ROOT / "working/immersive_engineering/quests"

TEXT_REPLACEMENTS = (
    ("이머시브 엔지니어링", "Immersive Engineering"),
    ("엔지니어의", "공학자의"),
    ("엔지니어 작업대", "공학자의 작업대"),
    ("기술자 작업대", "공학자의 작업대"),
    ("엔지니어링 블록", "공학 블록"),
    ("경형 공학 블록", "경공학 블록"),
    ("중형 공학 블록", "중공학 블록"),
    ("중형 방패", "중장갑 방패"),
    ("상위 버전으로 변환", "업그레이드"),
    ("액체", "유체"),
    ("원형 톱", "원형톱"),
    ("스크루드라이버", "드라이버"),
    ("축전기 백팩", "축전기 배낭"),
    ("청사진", "설계도"),
    ("코크 오븐", "코크스로"),
    ("투박한 용광로", "조잡한 용광로"),
    ("개선된 용광로", "개량 용광로"),
    ("강화된 용광로", "개량 용광로"),
    ("정제기", "정유기"),
    ("금속 압축기", "금속 프레스"),
    ("금속 압착기", "금속 프레스"),
    ("중간 전압", "중전압"),
    ("저압", "저전압"),
    ("고압", "고전압"),
    ("HOP 흑연괴", "HOP 흑연 주괴"),
    ("화학 투척기", "화학 분사기"),
    ("기술자의 드라이버", "공학자의 드라이버"),
    ("기술자의 망치", "공학자의 망치"),
    ("상위 버전", "업그레이드"),
    ("조명 공학 블록", "경공학 블록"),
    ("크레오소트 오일", "크레오소트유"),
    ("왼손 슬롯", "왼쪽 슬롯"),
    ("오른손 슬롯", "오른쪽 슬롯"),
    ("물론 엔지니어링에 관한", "물론 공학을 다루는"),
    ("업그레이드은", "업그레이드는"),
    ("업그레이드을", "업그레이드를"),
    ("업그레이드이", "업그레이드가"),
    ("축전지 가방", "축전기 배낭"),
    ("중공업 블록", "중공학 블록"),
    ("경공업 블록", "경공학 블록"),
    ("경량 공학 블록", "경공학 블록"),
    ("라이트 공학 블록", "경공학 블록"),
    ("빛 공학 블록", "경공학 블록"),
    ("경형 블록", "경공학 블록"),
    ("코크스 오븐", "코크스로"),
    ("병조림기", "병입기"),
    ("바이오 디젤", "바이오디젤"),
    ("켐스로어", "화학 분사기"),
    ("쉐이더", "셰이더"),
    ("방열기 블록", "방열 블록"),
    ("톱날 통", "톱날통"),
    ("오른손 클릭", "우클릭"),
    ("오른손으로 클릭", "우클릭"),
    ("보조 장비 슬롯에 홀드하는", "보조 장비 슬롯에 든"),
)

KEY_TEXT_REPLACEMENTS = {
    "quest.360B150190A5C894.quest_desc": (("룬 인챈터", "룬 마법부여기"),),
    "quest.063241B72BB3403E.quest_desc": (
        ("이러한 업그레이드는", "이 업그레이드는"),
        (
            "2개의 업그레이드를 홀드할 수 있습니다",
            "업그레이드를 2개 장착할 수 있습니다",
        ),
    ),
    "quest.0AE6AD813928DE4F.quest_desc": (
        ("열은 다른 양쪽 면에서", "열은 아래쪽을 제외한 면에서"),
        ("프리히터", "예열기"),
        ("사용되지만", "사용하지만"),
    ),
    "quest.1BF02D43986ABB03.quest_desc": (
        (
            "1개는 왼손, 1개는 오른손, 1개는 왼손, 1개는 오른손으로 갑니다",
            "1개는 왼쪽, 다음 1개는 오른쪽, 그다음 1개는 왼쪽, 마지막 1개는 "
            "오른쪽으로 번갈아 갑니다",
        ),
    ),
    "quest.2224AA108FC006F3.quest_desc": (
        ("탄약통으로 채우세요", "탄약통을 채우세요"),
        ("우클릭으로 즉시 재장전", "우클릭하면 즉시 재장전"),
    ),
    "quest.231E0C0A9B0C0509.quest_desc": (
        ("이것은 당신의", "이 업그레이드는"),
        ("&c&l가방&r", "&c&l배낭&r"),
        ("당신의 인벤토리", "인벤토리"),
    ),
    "quest.23FDFA44A162023A.quest_desc": (
        ("업그레이드를 추가하기 위해", "업그레이드를 장착하려면"),
        ("또한 &e아이템&r과", "&e아이템&r과"),
    ),
    "quest.257C80468B080B3C.quest_desc": (
        ("&8&lIE의&r", "&8&lIE&r의"),
        ("&e아이템&r을 홀드하지 않고", "&e아이템&r을 보관하지 않고"),
        (
            "전자석의 윗면과 가장 가깝게 이동합니다",
            "전자석의 윗면 가까이로 이동시킵니다",
        ),
    ),
    "quest.27FA2DB7839172BB.quest_desc": (
        ("&c&l가방&r", "&c&l배낭&r"),
        ("보관함에서 충전됩니다", "인벤토리 안에서 충전됩니다"),
    ),
    "quest.28847A536C38EEA0.quest_desc": (
        ("&c저전압 변압기&r", "&c변압기&r"),
        ("&5HV 저전압 변압기&r", "&5HV 변압기&r"),
        (
            "&6MV&r 없이 &5LV&r에서 &eHV&r로",
            "&eMV&r를 거치지 않고 &6LV&r에서 &5HV&r로",
        ),
    ),
    "quest.28E99A6E17E86709.quest_desc": (
        ("크레오소트유과", "크레오소트유와"),
        ("식물성 오일", "식물성 기름"),
    ),
    "quest.29C9F8719DA63D8D.quest_desc": (
        ("&2바이오 디젤&r", "&2바이오디젤&r"),
        ("통나무, 잎, 새 둥지가", "통나무, 나뭇잎, 새 둥지가"),
        ("&8톱&r은", "&8톱날&r은"),
        (
            "1개의 &8날&r 또는 &8디스크&r",
            "&8톱날&r 또는 &8디스크&r 1개",
        ),
    ),
    "quest.2E9D1131DC21CC5B.quest_desc": (
        ("&l인더스트리얼 포어고잉&r", "&lIndustrial Foregoing&r"),
        (
            "이것들은 판, 가루를 만들거나",
            "공학자의 망치는 판과 가루를 만들거나",
        ),
    ),
    "quest.2F8D117F802FEAF0.quest_desc": (
        (
            "그들은 12개의 하트와 갑옷이 없습니다",
            "체력은 하트 12개이며 방어구는 없습니다",
        ),
    ),
    "quest.35E399D88D2EDCB6.quest_desc": (
        (
            "이 업그레이드를 사용하면 당신을 공격하는 모든 대상은 1.",
            "이 업그레이드를 장착하면 공격자가 1.",
        ),
        ("2. 피해를 입으며", "2. 피해를 입고"),
        ("3. 모든 투사체가 파괴됩니다", "3. 발사한 투사체까지 파괴됩니다"),
    ),
    "quest.38C98FCB6A2D4226.quest_desc": (
        ("&c &l 백팩&r", "&c&l배낭&r"),
        ("당신을 때리는 사람은", "사용자를 공격한 대상은"),
        ("피해를 주고 효과를 줍니다", "피해와 상태 효과를 받습니다"),
    ),
    "quest.3ED40CC40458087E.quest_desc": (
        (
            "&c&l축전기 배낭&r 자체로는 많은 기능을 하지 않습니다",
            "&c&l축전기 배낭&r은 자체로는 작동하지 않습니다",
        ),
        (
            "&c축전기&r를 &6공학자의 작업대&r에 장착하면",
            "&6공학자의 작업대&r에서 &c축전기&r를 배낭에 장착하면",
        ),
        ("이 가방은", "이 배낭은"),
    ),
    "quest.407C2D00F22BD89D.quest_desc": (
        ("총 14개까지 만들 수 있습니다", "총 14발을 넣을 수 있습니다"),
    ),
    "quest.56E30438AE512475.quest_desc": (
        ("매우 단순한 구성원입니다", "간단한 추가 장치입니다"),
        ("왼손과 오른손에 간단히 배치하세요", "왼쪽과 오른쪽에 하나씩 설치하세요"),
        ("상단에 힘을 연결하면", "위쪽에 전력을 공급하면"),
        ("속도를 높이기 시작합니다", "작동 속도가 빨라집니다"),
        ("&l&4강화 용광로&r", "&l&4개량 용광로&r"),
    ),
    "quest.5EE1DF1C8F0C1FF9.quest_desc": (
        (
            "자체 &c에너지&r 저장소에 &c에너지&r가 되도록 할 수 있습니다",
            "자체 &c에너지&r 저장소에 &c에너지&r를 충전할 수 있습니다",
        ),
        ("어머니 자연의 가장 파괴적인 힘을", "대자연의 파괴적인 힘을"),
        ("단순한 가공된 울타리", "방부목 울타리"),
    ),
    "quest.6140EAA6E042EF7C.quest_desc": (
        ("기지 주변을 이동하는 데", "기지 주변을 돌아다니는 데"),
        ("우클릭을 홀드하여", "우클릭을 길게 눌러"),
        ("헴프", "대마"),
        ("업그레이드를 홀드할 수 있습니다", "업그레이드를 장착할 수 있습니다"),
        ("높은 회전력 모터", "고토크 모터"),
        ("절연 처리된 혼합된 손잡이", "절연 손잡이"),
        ("헤비 임팩트 훅", "고충격 갈고리"),
    ),
    "quest.63F5314A1072FA05.quest_desc": (
        (
            "뒤쪽 윗면으로 &c에너지&r를 공급하고 &e컨베이어 벨트&r로 "
            "&e아이템&r을 &9입력&r하세요. 가공된 &e아이템은 같은 &e벨트&r로 "
            "&6출력&r되고, 톱밥은 &e&l기계&r 앞쪽 포트로 나옵니다.",
            "뒤쪽 윗면으로 &c에너지&r를 공급하세요. &9입력할 &e아이템&r은 "
            "&e컨베이어 벨트&r에 올립니다. 가공된 &e아이템&r은 같은 &e벨트&r로 "
            "&6출력&r되고, 톱밥은 &e&l기계&r 앞쪽 포트로 나옵니다.",
        ),
    ),
    "quest.662DD269B027B6C8.quest_desc": (
        ("당신의", ""),
        ("&c유선&r으로", "&c유선&r으로는"),
        (
            "&c에너지&r를 전송하는 &c전선&r으로 걸어가면 가방으로 에너지가 일부 "
            "들어올 것입니다&c&l배낭&r",
            "&c에너지&r를 전송하는 &c전선&r 가까이 가면 에너지 일부가 "
            "&c&l배낭&r으로 들어옵니다",
        ),
    ),
    "quest.67940C0774E73217.quest_desc": (
        (
            "&9아이템&e을 &r입력&6하고 특정 위치로 &r출력합니다",
            "&9입력된 &e아이템&r을 특정 위치로 &6출력&r합니다",
        ),
        ("이것들은", "출력 대상은"),
    ),
    "quest.6BD348735C27BB44.quest_desc": (
        (
            "&e아이템&r이 &e벨트&r를 타고 지나갈 때마다 채워줍니다",
            "&e벨트&r를 타고 지나가는 &e아이템&r을 채웁니다",
        ),
    ),
    "quest.72CE46D28C9E7452.quest_desc": (
        ("가운데 클릭을 눌러", "마우스 가운데 버튼을 눌러"),
        ("정밀 스코프", "정밀 조준경"),
    ),
    "quest.7A1E3E7E2DF17AD2.quest_desc": (
        ("&2트리&r", "&2나무&r"),
        ("석재절단 톱날", "암석 절단 톱날"),
        ("섬세한 손길이 있는 곡괭이", "섬세한 손길 곡괭이"),
        ("산화물을 긁어내는 데", "산화를 벗겨 내는 데"),
    ),
    "quest.04DD3F761C210822.quest_desc": (
        ("Slag...", "슬래그..."),
        ("또 다른 3x3x3이며", "이번에도 3x3x3 구조이며"),
        ("우클릭하는 또 다른 시간", "우클릭하세요"),
    ),
    "quest.066B8A75B299AED8.quest_desc": (
        ("&9아이템&e을 &r입력", "&9입력 &e아이템&r"),
        ("&6유체&b를 &r출력", "&6출력 &b유체&r"),
        ("&9입력 &e아이템&r하기 위해", "&e아이템&r을 &9입력하기 위해"),
        ("&6출력 &b유체&r합니다", "&b유체&r를 &6출력합니다"),
        ("매우 쉬움 &6망치&r 피스톤 아래의 통을", "피스톤 아래 통을 &6망치&r로"),
    ),
    "quest.0A7B0D0B81E138DE.quest_desc": (
        ("&c전선&r, &c전선&r,", "&c배선&r 섹션에는 &c전선&r,"),
        ("분리된 셜커", "구역이 나뉜 셜커 상자"),
        (
            "&c배선&r 섹션에는 &c전선&r, &c연결기&r 또는 &c릴레이&r를 넣을 수 있는 전선 섹션",
            "&c배선&r 섹션에는 &c전선&r, &c연결기&r 또는 &c릴레이&r를 넣을 수 있습니다",
        ),
        ("넣을 수 있습니다, 그리고", "넣을 수 있습니다. 또한"),
        ("기타 섹션처럼 더 다양하게 사용해 보세요", "기타 섹션처럼 차별하지 마세요"),
    ),
    "quest.1A6A383B4EF26B20.quest_desc": (
        ("the...보다 내구도가 낮습니다", "강철 드릴 헤드보다 내구도가 낮습니다"),
        ("이것들은 7의 피해", "7의 피해"),
    ),
    "quest.251464B43353D4C6.quest_desc": (
        ("우리가 사랑하는 원예기", "우리가 사랑하는 원예용 온실"),
        ("왼손, 오른손 또는 위쪽", "왼쪽, 오른쪽 또는 위쪽"),
        ("클로슈", "원예용 온실"),
        ("&c에너지&6 입력&r", "&c에너지 &6입력&r"),
        ("&e아이템&6 입력&r", "&e아이템 &6입력&r"),
        ("원예용 온실를", "원예용 온실을"),
        ("( &9싱크대", "(&9싱크대"),
    ),
    "quest.252A24CED69C1882.quest_desc": (
        ("열전기 발전기(Thermo라고 부르겠습니다)", "열전 발전기"),
        ("Thermo의 양쪽", "열전 발전기의 양쪽"),
    ),
    "quest.33732EE8110A0911.quest_desc": (
        ("행운 III을 넣었습니다", "행운 III 효과를 추가했습니다"),
        ("그것은 암석 연화 산입니다", "그 역할을 하는 것이 암석 연화 산입니다"),
    ),
    "quest.341BB1353A1E45EA.quest_desc": (
        (
            "플레이어나 몹의 [Type]을 추가할 수 있는 [Type] 막대가 있습니다",
            "입력란에 플레이어나 몹의 이름을 입력해 추가할 수 있습니다",
        ),
        ("과녁을 설정", "공격 대상을 설정"),
        ("총 포탑은 설치한 사람은", "총 포탑은 설치한 사람을"),
        (
            "블랙리스트에 등록된 대상만 사격합니다",
            "블랙리스트에 등록된 대상을 사격합니다",
        ),
    ),
    "quest.373668AE257A7A94.quest_desc": (
        ("you...에 가장 가까운", "플레이어에게 가장 가까운"),
        ("늑대 무리 셸", "울프팩 포탄"),
    ),
    "quest.3E32450DBB7529AA.quest_desc": (
        ("롤러코스터의 라인", "롤러코스터의 대기열"),
        (
            "&6출력&r &e아이템&r을 수행하지 않습니다",
            "&e아이템&r을 &6출력&r하지 않습니다",
        ),
        ("&e아이템&r &9입력&r이 필요한", "&e아이템&r을 일정 수량 &9입력&r해야 하는"),
        ("일정량의 &e아이템&r을 일정 수량", "정해진 수량의 &e아이템&r을"),
    ),
    "quest.3E89034E0CB8D687.quest_desc": (
        (
            "나무 상자는 arrels...B처럼 작동하지만 &2&lMinecraft&r 상자와 달리 어느 쪽에서든 열 수 있습니다",
            "나무 저장 상자는 통처럼 작동하지만, &2&lMinecraft&r의 상자처럼 어느 쪽에서든 열 수 있습니다",
        ),
        ("강화된 상자", "강화 저장 상자"),
    ),
    "quest.458265FCD6B3068E.quest_desc": (
        ("&6엔지니어 제작대&r", "&6공학자의 제작대&r"),
        ("보관함을 닫아도", "화면을 닫아도"),
    ),
    "quest.4BBF987FEF639801.quest_desc": (
        ("Wait...", "잠깐..."),
        ("고마워, 수은!", "수은은 예외지만요!"),
    ),
    "quest.4D193D60A3CAF435.quest_desc": (
        ("최악에서 best", "효율이 낮은 순서부터 높은 순서"),
        ("크레오소트 오일", "크레오소트유"),
        ("방열기 블록", "라디에이터 블록"),
        ("방열 블록", "라디에이터 블록"),
    ),
    "quest.5218DAE147AC9F44.quest_desc": (
        ("&8칼날", "&8톱날"),
        ("홀드할 수 있습니다", "보관할 수 있습니다"),
        ("&8갈고리 디스크&r", "&8연마 디스크&r"),
        ("&8톱날과 같은 아이템&r", "&8톱날 계열 아이템&r"),
    ),
    "quest.586F6FD38CF85DCA.quest_desc": (
        (
            "make... 매우 어려운 제작법을 가지고 있습니다. 연료를 공급하는 방법을 찾는 퀘스트는 별도로 진행됩니다!",
            "제작법이 매우 어렵지만, 이 퀘스트에서는 연료를 넣는 방법만 알아봅니다!",
        ),
        ("상위 버전", "업그레이드"),
        ("홀드할 수 있습니다", "장착할 수 있습니다"),
    ),
    "quest.598DE7CEDA864B50.quest_desc": (
        ("함께 사용할 수 없습니다 though...", "함께 사용할 수는 없습니다..."),
    ),
    "quest.5C5546A5103BCF55.quest_desc": (
        ("Gases...와 같은", "기체 같은"),
        (
            "최소 2개의 업그레이드이 가능합니다",
            "그래도 업그레이드는 2개까지 장착할 수 있습니다",
        ),
        ("그것들은 작동합니다", "업그레이드는 제대로 작동합니다"),
    ),
    "quest.5F4F7637044BD4F1.quest_desc": (
        ("에탄올[Ethanol] 형태로", "에탄올로"),
        ("[왼쪽] 측면의 [포트]", "왼쪽 포트"),
        ("[오른쪽] 측면의 [포트]", "오른쪽 포트"),
        ("상단의 [포트]", "상단 포트"),
        ("&e조명 공학 블록&r", "&e경공학 블록&r"),
    ),
    "quest.6D42D0102D1CBC19.quest_desc": (
        (
            "추가 앵커는 오직 &4&l드릴&r에만 Sharpness... 있습니다",
            "추가 오거는 &4&l드릴&r에만 적용되는 날카로움 업그레이드입니다",
        ),
        ("쌓인 힘을 위해", "효과를 중첩하려면"),
    ),
    "quest.79BEECD4E545793F.quest_desc": (("Cobwebs...처럼", "거미줄처럼"),),
}

KEY_OVERRIDES: dict[str, object] = {
    "quest.063241B72BB3403E.title": "&8&l중장갑 방패",
    "quest.13471E64CDE49D27.title": "&l&a정유기",
    "quest.1759A4E2AF0D2C88.title": "&7중공학 블록",
    "quest.18A9392BBCF5A871.title": "&8&lImmersive Engineering&r 물류",
    "quest.2A1BFB2E0F1F3312.title": "&5&l레일건&r 탄약: &2&lMinecraft에서 획득",
    "quest.23FDFA44A162023A.title": "&6공학자의 작업대",
    "quest.3E89034E0CB8D687.title": "&e아이템 저장",
    "quest.3ED40CC40458087E.title": "&c&l축전기 배낭",
    "quest.4104C5D003D4705A.title": "&l&6자동 공학자의 작업대",
    "quest.431C62A6F8ECB4EC.title": "&5&l레일건&r 탄약: &8&lIE&r",
    "quest.5EC1B868720BF521.title": "&8&lImmersive Engineering",
    "quest.573C2242EAB85B49.title": "&l&8코크스로",
    "quest.63F5314A1072FA05.title": "&e&l제재기",
    "quest.6BD348735C27BB44.title": "&b&l병입기",
    "quest.78DA970F97002975.title": "&b유체 저장",
    "quest.7A1E3E7E2DF17AD2.title": "&2&l원형톱&r용 톱날",
    "task.0837FA64B9C50048.title": "원형톱용 톱날",
    "quest.7B9672C4FCFFB887.title": "&9경고 표지 설계도",
}

ALLOWED_EXACT_KEYS = {
    "quest.2E9D1131DC21CC5B.title",
    "quest.5EC1B868720BF521.title",
    "task.0D7C60D7BFBD8CF0.title",
    "task.603A16080675C348.title",
}

NEW_TRANSLATIONS: dict[str, object] = {
    "quest.0ACC0092A8F722C6.quest_desc": [
        "&8&lIE&r의 대부분 기계는 작동하려면 &c에너지&r가 필요하며, "
        "&c전선&r은 그 에너지를 옮기는 수단입니다! \n\n&c전선 코일&r을 든 채 "
        "한쪽 부품을 우클릭한 다음, 같은 &c코일&r로 두 번째 부품을 우클릭하면 "
        "&c전선&r이 연결됩니다. 두 지점 사이가 막혀 있으면 연결할 수 없습니다. "
        "\n\n&c전선&r을 회수하려면 연결된 부품을 부수거나 믿음직한 "
        "&6전선 절단기&r를 사용하세요! \n\n&c전선&r의 등급에 따라 전송량이 "
        "달라지며, &5HV&r 전선이 가장 많이 전송합니다."
    ],
    "quest.13471E64CDE49D27.quest_desc": [
        "&a&l정유기&r는 2개의 &b유체&r를 받아 혼합하고 정제하여 더 나은 1개의 "
        "&b유체&r로 만듭니다! \n\n2개의 &b유체&r는 왼쪽과 오른쪽 포트로 "
        "&9입력&r할 수 있고, 완성된 유체는 앞쪽 포트로 나옵니다. \n\n"
        "&b양동이&r를 사용해 탱크에 &b유체&r를 직접 넣을 수도 있습니다! "
        "&a&l정유기&r를 우클릭해 GUI를 열고 촉매를 넣어야 기계가 작동합니다. \n"
        "뒤쪽 포트로 &c에너지&r도 공급해야 합니다!",
        "{@pagebreak}",
        "먼저 &b유체 파이프&r 5개를 한 줄로 놓으세요. 가운데 파이프 한쪽에는 "
        "&e경공학 블록&r을, 반대쪽에는 &7중공학 블록&r을 놓습니다. 나머지 "
        "&b유체 파이프&r 옆에는 &8강철 비계&r를 놓으세요.",
        "{image:atm:textures/questpics/immersive/immersive_refinery1.png width:150 height:100 align:center}",
        "앞서 놓은 공학 블록 위에 같은 블록을 더 놓으세요. &7중공학 블록&r "
        "오른쪽에서 1칸 띄운 곳에 &4레드스톤 공학 블록&r을 놓습니다. "
        "&e경공학 블록&r 옆에는 &7철 판금&r으로 된 2개의 2x2 벽을 만드세요.",
        "{image:atm:textures/questpics/immersive/immersive_refinery2.png width:150 height:100 align:center}",
        "이제 &7철 판금&r을 몇 개만 더 놓으면 됩니다!",
        "{image:atm:textures/questpics/immersive/immersive_refinery3.png width:150 height:100 align:center}",
        "맨 위의 &7중공학 블록&r을 &6망치&r로 우클릭하세요.",
        "{image:atm:textures/questpics/immersive/immersive_refinery.png width:100 height:100 align:center}",
    ],
    "quest.1759A4E2AF0D2C88.quest_desc": [
        "&e경공학 블록&r의 모든 재료를 훨씬 만들기 어렵게 바꾼다고 생각하면 "
        "됩니다! \n\n1번째로 &6&l합금 가마&r에서 &e금&r과 &7은&r을 합금해 "
        "만드는 &e일렉트럼&r이 필요합니다. \n\n2번째로 &8강철 판금&r 4개가 "
        "필요합니다. &7철 판금&r처럼 &8판&r 4개를 조합해 만듭니다. \n\n"
        "3번째로 &8강철 기계 부품&r이 필요합니다. 제작대에서 &6구리 주괴&r 하나와 "
        "&8강철 판&r 4개로 만들거나, &6공학자의 작업대&r에서 더 적은 재료로 "
        "만들 수 있습니다."
    ],
    "quest.1A13039D6302ADA5.quest_desc": [
        "앞선 퀘스트에서 일부 재료의 제작법을 확인할 수 있습니다. &e경공학 "
        "블록&r에는 &7철 기계 부품&r이, &7중공학 블록&r에는 &8강철 판금&r이 "
        "들어갑니다. \n하지만 &e일렉트럼 코일&r은 조금 다릅니다... \n\n"
        "&e일렉트럼 코일&r에는 철 주괴와 MV 전선 코일 8개가 필요합니다. "
        "MV 전선 코일을 만들려면 공학자의 전선 절단기로 &e일렉트럼&r을 "
        "잘라야 합니다."
    ],
    "quest.1C76E244AE3582E6.quest_desc": [
        "&5&l조립기&r는 다른 기계와 달리 대부분의 작업을 GUI에서 설정합니다. "
        "\n\n기계를 우클릭하고 화면 위쪽 격자에 제작법을 넣어 최대 3개까지 "
        "설정하세요. 왼쪽에 있는 제작법부터 우선 처리합니다. \n\n&e컨베이어 "
        "벨트&r로 &e아이템&r을 &9입력하면 뒤쪽 &a벨트&r로 &6출력&r됩니다. "
        "제작에 쓰이는 &b양동이&r나 &b탱크&r를 채우도록 &b유체&r를 &6입력할 "
        "수도 있습니다! \n\n위쪽에서 &c에너지&r도 공급해야 합니다.",
        "{@pagebreak}",
        "&8강철 비계&r 3개짜리 줄 2개를 한 칸 간격으로 평행하게 놓으세요. "
        "그 사이 중앙에는 &e경공학 블록&r을, 주변에는 &4레드스톤 공학 "
        "블록&r을 놓습니다.",
        "{image:atm:textures/questpics/immersive/immersive_assembler1.png width:100 height:100 align:center}",
        "&4레드스톤 공학 블록&r이 있는 양옆에 &7철 판금&r을 놓으세요. "
        "&e경공학 블록&r 위에도 같은 블록을 하나 더 놓습니다. 그런 다음 "
        "&e컨베이어 벨트&r가 &e경공학 블록&r을 지나가도록 배치하세요!",
        "{image:atm:textures/questpics/immersive/immersive_assemble2.png width:100 height:100 align:center}",
        "그림만 보면 헷갈릴 수 있습니다. 앞서 놓은 &7철 판금&r 위에 "
        "&7철 판금 반 블록&r을 놓고, 그 사이에는 온전한 &7철 판금&r을 놓으세요.",
        "{image:atm:textures/questpics/immersive/immersive_assembler3.png width:100 height:100 align:center}",
        "첫 번째 &e컨베이어 벨트&r를 &6망치&r로 우클릭하면 &5&l조립기&r가 완성됩니다!",
        "{image:atm:textures/questpics/immersive/immersive_assembler.png width:100 height:100 align:center}",
    ],
    "quest.2A1BFB2E0F1F3312.quest_desc": [
        "&d엔드 막대&r는 10의 피해를 주며 엔더맨도 공격할 수 있습니다. "
        "\n&5엔더 진주&r는 몹에게 피해를 주지 않고, 발사하면 플레이어를 훨씬 "
        "멀리 순간이동시킵니다. \n&3삼지창&r은 일반 &3삼지창&r을 던진 것처럼 "
        "작동하며 8의 피해를 줍니다. \n&c블레이즈 막대&r는 10의 피해를 주고 "
        "몹에게 불을 붙입니다!"
    ],
    "quest.36EB83BB41A9E621.quest_desc": [
        "&b&l탱크&r는 &l&e사일로&r의 &b유체용 버전입니다! \n\n1종류의 "
        "&b유체&r만 담을 수 있지만, 그 &b유체&r를 512양동이까지 저장합니다. "
        "\n\n위쪽이나 아래쪽에서 &b유체&r를 &9입력&r할 수 있지만, &6출력&r은 "
        "아래쪽에서만 가능합니다.",
        "{@pagebreak}",
        "&b&l탱크&r는 &e&l사일로&r와 비슷하게 만듭니다. 방부목 울타리와 "
        "&7철 판금&r 하나로 시작하세요.",
        "{image:atm:textures/questpics/immersive/immersive_tank1.png width:125 height:100 align:center}",
        "울타리 위에 &7철 판금&r으로 속이 빈 사각형을 쌓으세요. 이번에는 "
        "3블록 높이로 만듭니다.",
        "{image:atm:textures/questpics/immersive/immersive_tank2.png width:100 height:100 align:center}",
        "{image:atm:textures/questpics/immersive/immersive_tank3.png width:100 height:100 align:center}",
        "{image:atm:textures/questpics/immersive/immersive_tank4.png width:100 height:100 align:center}",
        "맨 위를 &7철 판금&r으로 가득 채운 사각형으로 막으세요!",
        "{image:atm:textures/questpics/immersive/immersive_tank5.png width:100 height:100 align:center}",
        "&e&l사일로&r를 만들 때와 같은 블록을 우클릭하면 &b&l탱크&r가 완성됩니다.",
        "{image:atm:textures/questpics/immersive/immersive_tank.png width:100 height:120 align:center}",
    ],
    "quest.3A4A8EAA3022C7BA.quest_desc": [
        "물레방아는 운동 에너지 발전기에 연결할 수 있는 기계 중 하나입니다. "
        "\n\n풍차보다 훨씬 작지만 더 비쌉니다. \n\n사용하려면 물레방아 "
        "위로 &9물&r이 흐르게 해야 합니다. 주변에 흐르는 &9물&r이 많을수록 "
        "더 빨리 회전하지만, &9물&r이 2개의 서로 다른 방향으로 흐르지 않게 주의하세요! "
        "\n\n크기가 작으므로 운동 에너지 발전기 1개에 물레방아를 3개까지 "
        "연결해 더 많은 에너지를 얻을 수 있습니다."
    ],
    "quest.3EE95747CA6DFB1A.quest_desc": [
        "&7&l금속 프레스&r는 &7금속&r 제작법을 처리할 때 가장 든든한 "
        "기계입니다! \n\n프레스에 주형을 장착하고 위쪽으로 &c에너지&r를 "
        "공급한 다음, &e컨베이어 벨트&r에 &e아이템&r을 올리면 됩니다. "
        "\n\n&e아이템&r은 기계를 통과하며 &7&l압착&r되어 새 &e아이템&r으로 바뀐 뒤 "
        "&e벨트&r를 따라 계속 이동합니다! \n\n&c전선&r, &7판&r, &8막대&r, "
        "그리고... &2수박 조각&r도 만들 수 있나요?",
        "{@pagebreak}",
        "첫 층은 간단합니다. &8강철 비계&r와 &4레드스톤 공학 블록&r을 "
        "그림처럼 놓으세요.",
        "{image:atm:textures/questpics/immersive/immersive_press1.png width:150 height:75 align:center}",
        "&4레드스톤 공학 블록&r 위에 아래를 향한 피스톤을 놓고, 양옆에 "
        "컨베이어 벨트 두 개를 추가하세요.",
        "{image:atm:textures/questpics/immersive/immersive_press2.png width:125 height:100 align:center}",
        "피스톤 위에 &7중공학 블록&r 하나를 놓으세요!",
        "{image:atm:textures/questpics/immersive/immersive_press3.png width:100 height:100 align:center}",
        "마지막으로 피스톤을 공학자의 망치로 우클릭하세요!",
    ],
    "quest.4104C5D003D4705A.quest_desc": [
        "&e벨트&r를 사용하는 멀티블록이 또 나왔네요. 먼저 &9설계도&r를 "
        "설정해야 합니다. &6&l자동 공학자의 작업대&r를 우클릭해 GUI를 열고 "
        "가장 오른쪽 슬롯에 &9설계도&r를 넣으세요. \n\n그런 다음 "
        "&e벨트&r로 들어온 &e아이템&r을 가능한 제작법에 사용합니다. \n\n"
        "완성된 &e아이템&r과 실수로 &e벨트&r에 넣은 &e아이템&r은 출구 &e벨트&r로 "
        "나옵니다. \n\n탄약, &0HOP 흑연&r과 &7기계 부품&r을 자동으로 "
        "제작할 때 유용합니다.",
        "{@pagebreak}",
        "이번에도 &8강철 비계&r로 시작하지만 대각선으로 놓습니다. 작은 "
        "모서리에는 &7중공학 블록&r을, 큰 모서리에는 &e경공학 블록&r 2개와 "
        "&4레드스톤 공학 블록&r을 놓으세요.",
        "{image:atm:textures/questpics/immersive/immersive_automated1.png width:100 height:100 align:center}",
        "앞서 놓은 &e경공학 블록&r과 &7중공학 블록&r 위에 같은 블록을 더 "
        "쌓으세요. &4레드스톤 공학 블록&r과 그 왼쪽 &8강철 비계&r 위에는 "
        "방부목 반 블록을 놓습니다. 나머지 공간에는 그림처럼 &e컨베이어 "
        "벨트&r를 배치하세요.",
        "{image:atm:textures/questpics/immersive/immersive_automated2.png width:100 height:100 align:center}",
        "왼쪽 방부목 반 블록을 &6공학자의 망치&r로 치면 &6&l자동 공학자의 "
        "작업대&r가 완성됩니다!",
        "{image:atm:textures/questpics/immersive/immersive_automated.png width:100 height:100 align:center}",
    ],
    "quest.41B99DBD03EB74FF.quest_desc": [
        "이 멀티블록이 '개량'되었다는 말은 과장이 아닙니다! \n\n위쪽에서 "
        "&9입력&r을 받고 앞뒤 슬롯으로 &6출력&r하도록 자동화할 수 있습니다. "
        "\n\n왼쪽과 오른쪽에는 예열기도 장착할 수 있습니다! \n\n덕분에 "
        "훨씬 빠르고 효율적으로 작동합니다!",
        "{@pagebreak}",
        "드디어 다른 모양이네요! &4강화 용광로 벽돌&r로 3x3x3 바닥과 벽을 " "만드세요.",
        "{image:atm:textures/questpics/immersive/immersive_blast1.png width:100 height:100 align:center}",
        "{image:atm:textures/questpics/immersive/immersive_blast2.png width:100 height:100 align:center}",
        "{image:atm:textures/questpics/immersive/immersive_blast3.png width:100 height:100 align:center}",
        "가운데 블록 위에 호퍼를 놓으세요.",
        "{image:atm:textures/questpics/immersive/immersive_blast4.png width:100 height:125 align:center}",
        "이제 2번째 층의 가운데 블록을 &6공학자의 망치&r로 우클릭하세요.",
        "{image:atm:textures/questpics/immersive/immersive_blast.png width:100 height:150 align:center}",
    ],
    "quest.47656073894224AF.quest_desc": [
        "네, 거대한 전함에 달린 그것과 비슷합니다! \n\n&5&l레일건&r은 특별한 "
        "총입니다. 1. 리볼버용 탄약통이 아닌 전용 탄약을 사용합니다. 2. "
        "&c에너지&r를 사용하며 발사 전에 충전해야 합니다. \n\n탄약은 "
        "인벤토리에 있는 &e아이템&r입니다. &7알루미늄&r·&7철&r·&8강철 "
        "막대&r, &0흑연 전극&r, 톱날, 엔더 진주, 삼지창, 블레이즈 막대와 "
        "엔드 막대를 발사할 수 있습니다. \n\n인벤토리에 있는 탄약을 자동으로 "
        "사용하며, Shift를 누른 채 스크롤하면 발사할 탄약을 바꿀 수 있습니다. "
        "\n\n발사하려면 내부에 &c에너지&r가 있어야 합니다. &8&lImmersive "
        "Engineering&r의 충전소를 비롯한 &c아이템 충전기&r로 충전하세요! "
        "\n\n준비가 끝나면 충전 단계가 99가 될 때까지 우클릭을 누른 뒤 놓으세요! "
        "\n\n&5&l레일건&r에는 정밀 조준경과 방열판 업그레이드를 장착할 수 "
        "있습니다. \n\n업그레이드 슬롯은 2개입니다. 그보다 많이 달 곳도 없어 보이네요!"
    ],
    "quest.4C4C9ADAC6107F89.quest_desc": [
        "&e경공학 블록&r의 제작법은 꽤 간단합니다. \n\n먼저 &6구리 "
        "주괴&r 1개가 필요합니다. &2&l바닐라&r 재료이니 설명이 필요 없겠죠. "
        "\n\n&7철 판금&r 4개도 필요합니다. &7철 판&r 4개를 조합하면 "
        "됩니다! \n\n마지막으로 &7철 기계 부품&r 4개가 필요합니다. 제작대에서는 "
        "&7철 판&r 4개와 &6구리 주괴&r로, &6공학자의 작업대&r에서는 "
        "&7철 판&r 2개와 &6구리 주괴&r로 만들 수 있습니다."
    ],
    "quest.50326B1D6EE8FA0B.quest_desc": [
        "&c축전기&r는 &8&lIE&r의 배터리입니다. \n\n&6LV&r는 100k FE, "
        "&eMV&r는 1M FE, &5HV&r는 4M FE의 &c에너지&r를 저장합니다! "
        "\n\n기본적으로 위쪽 면은 &9입력&r만 받지만, &6공학자의 망치&r를 "
        "사용하면 어느 면이든 &9입력&r, &6출력&r 또는 연결 안 함으로 바꿀 수 "
        "있습니다."
    ],
    "quest.5A2A718C569F3C19.quest_desc": [
        "&l코크스로&r에서 &0석탄&r을 구우면 &0석탄 코크스&r를 얻습니다! "
        "여기서는 간단히 &0코크스&r라고 부르겠습니다. \n\n기본적으로는 "
        "&0석탄&r과 비슷하지만 &8&lIE&r에서 더 다양한 용도로 쓰입니다. "
        "\n\n철과 결합해 &7강철&r을 만들거나, 분쇄해 &0코크스 가루&r로 "
        "만들어 &0흑연&r 제작에 쓰거나, 용광로 연료로 사용할 수 있습니다."
    ],
    "quest.63F5314A1072FA05.quest_desc": [
        "&e&l제재기&r는 &e컨베이어 벨트&r와 추가 부품을 사용한다는 점에서 "
        "&7&l금속 프레스&r와 비슷합니다. \n\n2단계로 작동합니다. 먼저 "
        "통나무의 껍질을 벗기며, 톱날이 없으면 이 단계만 수행합니다. 두 번째로 "
        "톱날을 사용해 통나무를 판자로 자릅니다. \n\n톱날은 많은 &8강철&r로 "
        "제작하며 내구도가 있습니다. 제재기 뒤쪽 슬롯을 우클릭해 장착하세요. "
        "꺼내려면 &4레드스톤&r 신호로 제재기를 끈 뒤 장착한 곳을 Shift+우클릭합니다. "
        "\n\n뒤쪽 윗면으로 &c에너지&r를 공급하고 &e컨베이어 벨트&r로 "
        "&e아이템&r을 &9입력&r하세요. 가공된 &e아이템은 같은 &e벨트&r로 &6출력&r되고, "
        "톱밥은 &e&l기계&r 앞쪽 포트로 나옵니다.",
        "{@pagebreak}",
        "&8강철 비계&r를 I자 모양으로 놓고 &7중공학 블록&r도 잊지 마세요. "
        "한쪽은 &e경공학 블록&r으로, 다른 쪽은 &7철 판금&r으로 채우세요.",
        "{image:atm:textures/questpics/immersive/immersive_saw1.png width:150 height:100 align:center}",
        "아래쪽 &e경공학 블록&r 위에 같은 블록 3개를 더 놓으세요. 앞서 놓은 "
        "&7철 판금&r 중 가장 왼쪽 &7철 판금&r 위에 판금 1개를, 그 옆에 "
        "&4레드스톤 공학 블록&r을 "
        "놓습니다. 위쪽 &7철 판금&r 옆에는 &7중공학 블록&r을 하나 더 "
        "놓으세요. 완성에 필요한 컨베이어 벨트도 잊지 마세요!",
        "{image:atm:textures/questpics/immersive/immersive_saw2.png width:100 height:100 align:center}",
        "가운데 &7철 판금&r을 공학자의 망치로 우클릭하세요!",
        "{image:atm:textures/questpics/immersive/immersive_saw.png width:100 height:100 align:center}",
    ],
    "quest.7060290E107D92AB.quest_desc": [
        "&5&l레일건&r처럼 설치할 수 없는 &e아이템&r도 &c에너지&r가 필요한 "
        "경우가 많습니다. 이런 아이템은 어떻게 충전할까요? \n\n충전소가 그 "
        "역할을 맡습니다! \n\n뒤쪽이나 아래쪽에서 &6입력 &c에너지&r를 공급하면 "
        "안에 넣은 &e아이템&r을 충전할 준비가 끝납니다! \n\n&5&l레일건&r, "
        "&c축전기&r와 다른 모드의 아이템도 충전할 수 있습니다. 다만 주변에 "
        "놓인 블록은 충전하지 못합니다..."
    ],
    "quest.7A41038180C06B00.quest_desc": [
        "&c연결기&r는 이름 그대로 무언가를 연결합니다! 기계와 &c축전기&r, "
        "발전기를 비롯한 거의 모든 장치에 &c전선&r을 연결합니다. \n\n"
        "&c연결기의 &9입력 &f또는 &6출력&r 여부는 연결된 장치의 면 설정에 따라 "
        "결정됩니다! \n\n연결기 자체에도 &c에너지&r 저장 공간이 있으며, 전압 "
        "등급에 따라 저장량이 달라집니다."
    ],
}


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def replace_text(value: object) -> object:
    if isinstance(value, list):
        return [replace_text(child) for child in value]
    if not isinstance(value, str):
        return value
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    return value


def replace_key_text(
    value: object, replacements: tuple[tuple[str, str], ...]
) -> object:
    if isinstance(value, list):
        return [replace_key_text(child, replacements) for child in value]
    if not isinstance(value, str):
        return value
    for old, new in replacements:
        value = value.replace(old, new)
    return value


def encode_literal_linebreaks(value: object) -> object:
    if isinstance(value, list):
        return [encode_literal_linebreaks(child) for child in value]
    if isinstance(value, str):
        return value.replace("\n", "\\n")
    return value


def normalize() -> dict[str, object]:
    changed = 0
    unresolved = []
    reviewed = 0
    for root in sorted(QUEST_ROOT.glob("*")):
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        source_file = root / "candidate_sources.json"
        if not english_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        sources = load_json(source_file)
        for key, source in english.items():
            target = korean[key]
            if key in NEW_TRANSLATIONS:
                target = encode_literal_linebreaks(NEW_TRANSLATIONS[key])
            elif sources[key] == "new_translation_required":
                unresolved.append(key)
                continue
            if key in KEY_OVERRIDES:
                target = KEY_OVERRIDES[key]
            target = replace_text(target)
            if key in KEY_TEXT_REPLACEMENTS:
                target = replace_key_text(target, KEY_TEXT_REPLACEMENTS[key])
            errors = quest_snbt.validate_value(key, source, target)
            if errors:
                raise ValueError("; ".join(errors))
            reviewed += 1
            if korean[key] != target:
                korean[key] = target
                changed += 1
        write_json(korean_file, korean)
    report = {
        "display_keys_reviewed": reviewed,
        "changed": changed,
        "new_translations": len(NEW_TRANSLATIONS),
        "unresolved": len(unresolved),
        "unresolved_examples": unresolved,
    }
    write_json(QUEST_ROOT.parent / "quest_normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], list[str]]:
    errors = []
    untranslated = []
    checked = 0
    for root in sorted(QUEST_ROOT.glob("*")):
        english_file = root / "en_us.json"
        korean_file = root / "ko_kr.json"
        if not english_file.is_file():
            continue
        english = load_json(english_file)
        korean = load_json(korean_file)
        if list(english) != list(korean):
            errors.append(f"{root.name}: 키 또는 순서가 영어 원문과 다릅니다.")
        for key, source in english.items():
            target = korean.get(key)
            errors.extend(quest_snbt.validate_value(key, source, target))
            if key not in ALLOWED_EXACT_KEYS and quest_snbt.flatten(
                source
            ) == quest_snbt.flatten(target):
                untranslated.append(key)
            checked += 1
    report = {
        "display_keys": checked,
        "untranslated": len(untranslated),
        "untranslated_examples": untranslated,
        "errors": errors,
        "status": "complete" if not errors and not untranslated else "incomplete",
    }
    write_json(QUEST_ROOT.parent / "specialized_quest_validation.json", report)
    if untranslated:
        errors.append(f"미번역 {len(untranslated)}개")
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("normalize", "verify"))
    args = parser.parse_args()
    if args.command == "normalize":
        report = normalize()
        errors = []
    else:
        report, errors = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
