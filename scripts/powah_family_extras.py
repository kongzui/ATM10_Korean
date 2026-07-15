#!/usr/bin/env python3
"""Powah!·Flux Networks의 퀘스트, GuideME, 발전 과제와 KubeJS를 처리한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/powah_flux"
OUTPUT_ASSETS = PROJECT_ROOT / "output/resourcepack/ATM10_Korean/assets"
QUEST_OUTPUT = PROJECT_ROOT / "output/overrides/config/ftbquests/quests/lang/ko_kr.snbt"
POWAH_GUIDE_ROOT = "assets/powah/guides/powah/book"
GUIDE_OUTPUT = OUTPUT_ASSETS / "powah/guides/powah/book/_ko_kr"
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
TAG = re.compile(r"<[^>]+>")
LINK_TARGET = re.compile(r"\]\([^)]*\)")

QUEST_OVERRIDES: dict[str, object] = {
    "quest.05B0A7D0B991050F.title": "원자로 (강화)",
    "quest.08245411AFDB63DB.quest_desc": [
        "이 퀘스트는 &6AllTheMods 운영진&r 또는 &2커뮤니티 기여자&r가 AllTheMods "
        "모드팩에서 사용할 수 있도록 작성했습니다.\\n\\n모든 &6AllTheMods&r 팩은 "
        "&e모든 권리 보유&r로 배포되므로, &6AllTheMods 팀&r의 명시적인 허가 없이 "
        "다른 공개 모드팩에 이 퀘스트를 사용할 수 없습니다.\\n\\n이 퀘스트는 의도적으로 "
        "숨겨져 있습니다. 이 문구가 보인다면 편집 모드입니다."
    ],
    "quest.0FD62827710F0AC6.quest_desc": [
        "&c마그마토르&r에 용암을 공급하면 FE를 생산합니다."
    ],
    "quest.0FFF2BEE5D8EBE12.title": "원자로 (나이오틱)",
    "quest.1B0087400B0B8B49.quest_desc": [
        "&9원자로&r는 &a우라니나이트&r를 연료로 태워 FE를 생산하는 3x4x3 멀티블록 "
        "발전기입니다.\\n\\n원자로를 만들려면 원자로 블록 36개가 필요합니다. 블록 36개를 "
        "손에 든 상태에서 하나를 놓으면 원자로가 자동으로 완성됩니다. 먼저 충분한 공간을 "
        "비워 두세요!\\n\\n원자로를 냉각하면 더 많은 FE를 생산합니다. 고체 또는 액체 "
        "&b냉각재&r를 사용할 수 있지만, 고체 냉각재를 쓸 때도 액체 냉각재가 함께 "
        "필요합니다. &b드라이 아이스&r는 훌륭한 고체 냉각재입니다! (참고: 물 양동이 "
        "1개면 됩니다.)\\n\\n연료 버퍼를 가득 채우고 석탄과 레드스톤을 추가해 발전량을 "
        "더 높일 수도 있습니다. 석탄 블록과 레드스톤 블록도 사용할 수 있습니다!"
    ],
    "quest.1B0087400B0B8B49.title": "원자로 (초급)",
    "quest.1C273D9E046FD18A.quest_desc": [
        "에너지 주입 오브에서 아이템에 에너지를 주입할 때 사용합니다."
    ],
    "quest.25EFC21A3C48E0B6.title": "등급: &2활기찬",
    "quest.33816AF0E699F19F.quest_desc": ["이 블록은 충전된 아이템의 FE를 방전합니다."],
    "quest.341486C9F277FEB7.title": "원자로 (활기찬)",
    "quest.3CB6DC5B09C62CFE.quest_desc": [
        "&5엔더 게이트&r는 인접한 블록과 &7엔더 네트워크&r 사이에서 전력을 무선으로 "
        "전송합니다.\\n\\n무선 전력망에 접속하는 액세스 포인트라고 생각하면 됩니다."
        "\\n\\n참고: 네트워크의 &a전력 저장 용량&r은 엔더 셀로만 늘릴 수 있습니다."
    ],
    "quest.3DDF87A1E5F5D009.quest_desc": [
        "처음에는 철로 &7초급&r 및 &b기본&r 등급 기계를 만들 수 있지만, 곧 "
        "&9에너지 주입 오브&r에서 더 높은 등급의 재료를 만들어야 합니다.\\n\\n"
        "&9에너지 주입 오브&r는 주변 9x9 범위에 있는 &a에너지 주입 막대&r를 통해 "
        "아이템에 에너지를 주입합니다. 이렇게 만든 재료로 Powah!의 다음 &e등급&r을 "
        "해금할 수 있습니다.\\n\\n오브에 전력을 공급하려면 전력이 흐르는 에너지 케이블에 "
        "에너지 주입 막대를 설치하세요. 더 빨리 처리하려면 막대를 늘리거나 더 높은 등급의 "
        "막대로 업그레이드하면 됩니다. 막대의 연결 상태는 &a렌치&r를 연결 모드로 바꾼 뒤 "
        "막대와 오브를 연결해 확인할 수 있습니다.",
        "",
        "{image:atm:textures/questpics/powah/powah_energizing.png width:200 height:200 align:1}",
    ],
    "quest.3DDF87A1E5F5D009.title": "&9에너지 주입 오브",
    "quest.4F1FFC02F4EAA2E6.title": "등급: &4니트로",
    "quest.52E59FCB39D66BCF.quest_desc": [
        "수동 발전에 매우 유용한 &9열 발전기&r는 &c열원&r 위에 설치하고 물을 계속 "
        "공급하면 FE를 생산합니다.\\n\\n현재 사용할 수 있는 열원은 3가지입니다. 발전량이 "
        "가장 낮은 마그마 블록, 그보다 나은 용암 근원 블록, 가장 많은 열을 제공하는 "
        "&c타오르는 수정 블록&r이 있습니다."
    ],
    "quest.562BD37539EE318E.title": "등급: &c타오르는",
    "quest.5E090C9BB4DAA5D4.title": "등급: &a에너지화",
    "quest.61A8FAEC4FF18449.quest_desc": [
        "배터리는 인벤토리의 아이템을 충전하거나 &7엔더 네트워크&r 채널의 전체 전력 "
        "저장 용량을 늘리는 데 사용할 수 있습니다."
    ],
    "quest.66ECC26BC81D0093.title": "등급: &b기본",
    "quest.6754612E9AD4B9C0.title": "원자로 (타오르는)",
    "quest.677365A816994C8B.quest_desc": [
        "&9플레이어 송신기&r는 플레이어의 아이템을 무선으로 충전합니다. 먼저 &9결속 "
        "카드&r로 플레이어를 연결해야 합니다. 일반 결속 카드는 같은 차원에서만 작동하며, "
        "&d결속 카드 (차원)&r을 사용하면 차원을 넘어 충전할 수 있습니다.",
        "",
        "참고: 플레이어 공중 진주는 좀비나 허스크에게 공중 진주를 사용해 얻습니다.",
    ],
    "quest.6B2027DA7AA6FF34.quest_desc": [
        "&9Powah!&r는 &d전력&r의 생산, 저장, 전송을 다루는 기술 모드입니다. 기본 FE "
        "발전기부터 &b250k FE/t&r를 생산하는 &a원자로&r까지 다양한 장치를 제공합니다!"
        "\\n\\n먼저 밖으로 나가 &a우라니나이트&r를 채굴하세요!"
    ],
    "quest.6B2027DA7AA6FF34.title": "&a&9Powah!&r에 오신 것을 환영합니다!!!",
    "quest.6D88C19F47D0D469.title": "등급: &7초소형",
    "quest.700F3FF7C23D0C0F.quest_desc": [
        "&5엔더 셀&r은 &7엔더 네트워크&r의 특정 채널에 전력을 저장합니다. 네트워크 "
        "용량을 늘리려면 엔더 셀을 우클릭해 화면을 연 뒤 &a배터리&r 또는 &9에너지 셀&r을 "
        "추가하세요."
    ],
    "quest.7678B5DD1339833E.quest_desc": [
        "태양광 패널은 햇빛을 직접 받으면 FE를 생산합니다. &7엔더 렌즈&r를 장착하면 "
        "위쪽을 가로막는 블록을 무시할 수 있습니다."
    ],
    "quest.78202A1CF5D86B94.quest_desc": [
        "Powah!의 &9전력 저장고&r입니다.\\n\\n무선 &7엔더 네트워크&r의 전체 전력 "
        "저장 용량을 늘리는 데에도 사용할 수 있습니다."
    ],
    "quest.7D7983F39E6E818D.title": "등급: &9나이오틱",
    "quest.7E92ED270C67FDE5.title": "유전체 재료부터 시작하기",
    "task.09C7E50E7E13C53C.title": "모든 권리 보유",
    "task.3282910297C28795.title": "모든 권리 보유",
    "quest.3FF61A4D7A250AE1.quest_desc": [
        "다른 &5크리에이티브 &d에너지 셀&r과 혼동하기 쉬운 이 &5크리에이티브 "
        "&c에너지 셀&r을 만들려면 &c니트로 셀&r 4개가 필요합니다.\\n\\n각 &c니트로 "
        "셀&r에는 &a활기찬 셀&r 2개가, 각 &a활기찬 셀&r에는 &b나이오틱 셀&r 2개가 "
        "필요합니다. 이런 과정이 한동안 계속됩니다...\\n\\n계산은 제작법 트리에 맡기세요. "
        "저는 더 중요한 일이 있거든요!"
    ],
    "quest.7B3613C01F0B1373.quest_desc": [
        "&3비브라늄&r과 &6올더모디움&r을 결합하려면 &l&cPowah!&r의 힘이 필요합니다! "
        "\\n\\n에너지 주입 오브를 놓고 에너지 주입 막대가 오브를 향하게 배치하세요. 막대는 "
        "전력원 위에 놓아야 하며, 등급에 따라 저장량과 전송량이 달라집니다. "
        "\\n\\n주괴, 피글리치 심장 2개, 1배 압축 니트로 수정 블록을 오브에 넣으세요. "
        "순서는 상관없습니다. 막대를 통해 1 Billion FE를 공급하면 완성됩니다!\\n",
        '{ "text": "Powah! 퀘스트", "color": "#55FF55", "underlined": true, '
        '"clickEvent": { "action": "change_page", "value": "2A6EBEEBAB882679" } }',
    ],
    "quest.27A4FA38992448A0.quest_desc": [
        "Flux Networks에서는 차원을 넘어 인벤토리의 아이템을 무선으로 충전할 수 "
        "있습니다!\\n\\n먼저 전력 시스템에 플럭스 플러그를 연결한 뒤 &9플럭스 컨트롤러&r를 "
        '만들어 설치하세요.\\n\\n우클릭해 화면을 열고 "무선 충전" 탭으로 이동하세요. '
        "계속 충전할 인벤토리 영역을 각각 선택할 수 있습니다. 아래쪽 전환 버튼으로 무선 "
        "충전을 켠 뒤 적용 버튼을 누르면 활성화됩니다!\\n",
        "{image:atm:textures/questpics/basic_power/wireless_ui.png width:125 height:150 align:center}",
    ],
    "quest.35ABB0DEE70DF7FD.quest_desc": [
        "믿기 어렵겠지만 &aPowah!&r에는 전력을 생산하는 훌륭한 장치가 아주 많습니다."
        "\\n\\n자세한 사용법은 &cPowah!&r 퀘스트 챕터에서 확인하세요!"
    ],
    "quest.35ABB0DEE70DF7FD.title": "더 많은 &aPowah!&r!",
    "quest.35CC898E0E49FE58.quest_desc": [
        "&9Flux Networks&r는 무선 전력 문제를 해결하는 모드입니다.\\n\\n직접 전력을 "
        "생산하지는 않지만 전력을 저장하고 차원을 넘어 무선으로 전송할 수 있으며, 인벤토리의 "
        "아이템도 충전할 수 있습니다.\\n\\n비행 중인 제트팩도 충전할 수 있습니다."
        "\\n\\n시작하려면 플럭스 가루가 필요합니다. 기반암 위에 레드스톤 가루를 던지고, "
        "떠 있는 레드스톤 바로 위에 흑요석을 놓은 다음 흑요석을 좌클릭하세요."
    ],
    "quest.35CC898E0E49FE58.quest_subtitle": "궁극의 무선 전력 솔루션",
    "quest.35CC898E0E49FE58.title": "&8Flux Networks",
    "quest.56B6ABF3D6EA0D84.quest_desc": [
        "플러그를 설치했으니 이제 네트워크의 전력을 꺼내 쓸 수 있습니다. &9플럭스 "
        "포인트&r는 연결된 기계, 파이프 또는 케이블에 네트워크 전력을 공급합니다."
        '\\n\\n전력을 공급할 블록에 포인트를 설치하고 우클릭한 뒤 "네트워크 선택" 탭에서 '
        "네트워크를 고르세요. 플러그와 마찬가지로 전송 제한과 우선순위 등을 조절할 수 "
        "있습니다."
    ],
    "quest.56B6ABF3D6EA0D84.title": "네트워크 전력 사용하기",
    "quest.79AD74A863EA43CB.quest_desc": [
        "Flux Networks에는 네트워크에서 사용할 전력을 저장하는 장치도 있습니다!"
        "\\n\\n플럭스 저장소는 매우 많은 전력을 저장하며 더 높은 등급으로 업그레이드할 수 "
        "있습니다."
    ],
    "quest.79AD74A863EA43CB.quest_subtitle": "전력 저장",
    "quest.535525EA4DF4AB59.quest_desc": [
        "&c플레이어 송신기&r는 결속 카드를 연결한 플레이어의 방어구, 도구와 인벤토리 "
        "아이템에 에너지를 공급합니다.\\n\\n가장 마지막이자 제작하기 어려운 &c니트로 등급&r "
        "송신기는 &6&lATM Star&r 제작에 필요합니다."
    ],
    "quest.535525EA4DF4AB59.title": "&c니트로 플레이어 송신기",
    "quest.7E4367252A39BE6C.quest_desc": [
        "&c&lPowah!&r는 전력을 생산하는 모드입니다! 생산한 FE로 &5&lMekanism&r이나 "
        "&lIndustrial Foregoing&r 같은 다른 모드의 기계를 작동할 수 있습니다. "
        "\\n\\n여러 등급을 차례로 제작해야 하며, 마지막 등급은 물론 &6&lATM Star&r에 "
        "필요합니다!"
    ],
    "quest.7E4367252A39BE6C.title": "&c&lPowah!",
}

GUIDE_TITLES = {
    "Thermo Generator": "열 발전기",
    "Magmator": "마그마토르",
    "Generators": "발전기",
    "Solar Panel": "태양광 패널",
    "Reactor": "원자로",
    "Furnator": "퍼네이터",
    "Materials": "재료",
    "Uraninite Ore": "우라니나이트 광석",
    "Dry Ice": "드라이 아이스",
    "Ender Gates": "엔더 게이트",
    "Storage / Transfer": "저장 및 전송",
    "Ender Cells": "엔더 셀",
    "Energy Cables": "에너지 케이블",
    "Energy Cells": "에너지 셀",
    "Energizing": "에너지 주입",
    "Energy Discharger": "에너지 방전기",
    "Functional Blocks": "기능 블록",
    "Player Transmitter": "플레이어 송신기",
    "Energy Hopper": "에너지 호퍼",
    "Binding Card (Dimensional)": "결속 카드 (차원)",
    "Binding Card": "결속 카드",
    "Charged Snowball": "충전된 눈덩이",
    "Items": "아이템",
    "Wrench": "렌치",
    "Player Aerial Pearl": "플레이어 공중 진주",
    "Batteries": "배터리",
    "Lens Of Ender": "엔더 렌즈",
}

GUIDE_PARAGRAPHS = {
    (
        "The Thermo Generator is an FE generator that generates energy when "
        "placed on top of a high temp block/fluid like lava, require a coolant "
        "fluid like water to run. "
    ): "열 발전기는 용암처럼 뜨거운 블록이나 유체 위에 설치하면 FE를 생산하며, 작동하려면 물 같은 냉각 유체가 필요합니다. ",
    (
        "The Magmator is an FE generator that generates energy from high temp "
        "fluids like Lava. "
    ): "마그마토르는 용암처럼 뜨거운 유체를 연료로 사용해 FE를 생산합니다. ",
    (
        "High tiers generate more FE/t and it has higher energy output, also "
        "they burn the fuel faster with the same energy gained per fuel tick. "
    ): "높은 등급일수록 FE/t와 최대 출력이 커지며, 연료 단위당 총 발전량은 같지만 더 빠르게 소모합니다. ",
    (
        "The Solar Panel is an FE generator that generates energy when exposed "
        "to sunlight, high tiers generates more FE/t, any block that stop light "
        "above the Solar panel will stop its production. "
    ): "태양광 패널은 햇빛을 받으면 FE를 생산합니다. 높은 등급일수록 FE/t가 늘어나며, 위쪽에서 빛을 가리는 블록이 있으면 발전을 멈춥니다. ",
    "The Reactor is a multi-block (FE) generator that use Uraninite as main fuel. ": "원자로는 우라니나이트를 주 연료로 사용하는 멀티블록 FE 발전기입니다. ",
    (
        "To build it you will need 36 Reactor block in your hand and placing them "
        "in a 3X4 replaceable area, then the reactor will complete building itself "
        "automatically. "
    ): "원자로 블록 36개를 손에 들고 3x4 크기의 빈 공간에 하나를 놓으면 나머지 구조가 자동으로 완성됩니다. ",
    (
        "The Furnator is an FE generator that generates energy from solid Furnace "
        "fuel like coal, wood ... "
    ): "퍼네이터는 석탄이나 나무처럼 화로에서 태울 수 있는 고체 연료로 FE를 생산합니다. ",
    (
        "Uraninite Ore is an ore rarely found underground at levels below 64 for "
        "poor, below 20 for the normal, and below 0 for dense, and is found in "
        "1 - 5 block deposits. "
    ): "우라니나이트 광석은 지하에서 드물게 생성됩니다. 하급 광석은 Y 64 아래, 일반 광석은 Y 20 아래, 고밀도 광석은 Y 0 아래에서 1~5개가 한 광맥으로 발견됩니다. ",
    (
        "An iron or better pickaxe is needed to mine it, and when mined it will "
        "drop 1 piece of Raw Uraninite based on the ore type (the amount dropped "
        "are effected by fortune). "
    ): "채굴하려면 철 곡괭이 이상이 필요합니다. 광석 종류에 따라 우라니나이트 원석 1개가 나오며 행운 마법부여의 영향을 받습니다. ",
    (
        "Dry Ice used mainly to cool down reactors, it can be found underground "
        "at levels below 64, you can also obtain it by energizing two pieces of "
        "blue ice. "
    ): "드라이 아이스는 주로 원자로를 냉각하는 데 사용합니다. Y 64 아래 지하에서 발견하거나, 푸른 얼음 2개에 에너지를 주입해 만들 수 있습니다. ",
    "Transfer energy between the adjacent block and the ender network. ": "인접한 블록과 엔더 네트워크 사이에서 전력을 전송합니다. ",
    "Unlike the Ender cell you can not Upgrade the network from it. ": "엔더 셀과 달리 이 블록에서는 네트워크 용량을 업그레이드할 수 없습니다. ",
    (
        "The Ender Cell its a block used to store energy (FE) to a specific "
        "channel of the ender network of the owner. "
    ): "엔더 셀은 소유자의 엔더 네트워크에서 특정 채널의 FE를 저장하는 블록입니다. ",
    (
        "You can access the energy stored of a selected channel from anywhere in "
        "the world if the Ender Cell that you want to transfer power from/to have "
        "an active channel with a valid capacity. "
    ): "유효한 저장 용량이 있는 활성 채널에 엔더 셀이 연결되어 있으면, 월드 어디서든 선택한 채널의 전력을 주고받을 수 있습니다. ",
    "Cables are used to transfer power between machines. ": "케이블은 기계 사이에서 전력을 전송합니다. ",
    (
        "You can change transfer mode of by right-clicking a cable using "
        '<ItemLink id="powah:wrench" /> with Config mode selected. '
    ): '설정 모드로 바꾼 <ItemLink id="powah:wrench" />를 들고 케이블을 우클릭하면 전송 모드를 바꿀 수 있습니다. ',
    "The Energy Cell its a block used to store energy (FE). ": "에너지 셀은 FE를 저장하는 블록입니다. ",
    (
        "Can Also be used to add capacity to an Ender Network channel by "
        "Shift-clicking it to an Ender Cell GUI, if the Energy Cell contains "
        "energy then will also be applied to the ender network channel. "
    ): "엔더 셀 화면에서 에너지 셀을 Shift+클릭하면 엔더 네트워크 채널의 용량을 늘릴 수 있습니다. 에너지 셀에 저장된 전력도 채널로 함께 옮겨집니다. ",
    (
        "The Energizing Orb its a block used to energize items, require at least "
        "one Energizing Rod in range of 9X9 to work, the energizing speed depends "
        "on amount of rods and the rod tier (I/O rate). "
    ): "에너지 주입 오브는 아이템에 에너지를 주입하는 블록입니다. 작동하려면 9x9 범위 안에 에너지 주입 막대가 하나 이상 있어야 하며, 처리 속도는 막대의 수와 등급(입출력 속도)에 따라 달라집니다. ",
    (
        "The orb does not require energy but the rods must be placed on cables or "
        "any Forge Energy (FE) block to work. "
    ): "오브 자체에는 전력이 필요하지 않지만, 막대는 케이블이나 Forge Energy(FE)를 사용하는 블록 위에 설치해야 합니다. ",
    (
        "The Energy Discharger its a block used to drain energy (FE) out of "
        "charged items and then store it to an internal buffer if then connected "
        "via cables to extract that stored power and re-using it again. "
    ): "에너지 방전기는 충전된 아이템에서 FE를 빼내 내부 버퍼에 저장합니다. 케이블을 연결하면 저장된 전력을 꺼내 다시 사용할 수 있습니다. ",
    (
        "The Player Transmitter its a block used to charge items wirelessly in "
        "linked player inventory including armor slots and off-hand anywhere in "
        "the same dimension when has a normal binding card and across dimensions "
        "when has a dimensional binding card. "
    ): "플레이어 송신기는 연결된 플레이어의 인벤토리, 방어구 슬롯과 보조 손 아이템을 무선으로 충전합니다. 일반 결속 카드는 같은 차원에서, 차원 결속 카드는 차원을 넘어 작동합니다. ",
    (
        "The Energy Hopper its a block used to charge chargeable items inside an "
        "adjacent inventory like a chest or any block with an accessible inventory "
        "and not a not has forge energy. "
    ): "에너지 호퍼는 상자처럼 인벤토리를 열 수 있는 인접한 블록 안의 충전 가능한 아이템에 전력을 공급합니다. ",
    "Dimensional Binding Card used to link a player with a Player Transmitter across dimensions. ": "차원 결속 카드는 플레이어와 플레이어 송신기를 차원을 넘어 연결합니다. ",
    "Binding Card used to link a player with a Player Transmitter in the same dimension. ": "결속 카드는 같은 차원에 있는 플레이어와 플레이어 송신기를 연결합니다. ",
    "You need to link it with you before adding it to the player transmitter, Right-click it to bind. ": "플레이어 송신기에 넣기 전에 카드를 우클릭해 자신에게 결속해야 합니다. ",
    (
        "Throwing a Charged Snowball will cause a bolt of lightning to spawn when "
        "hitting the ground or when it hits the mob, obtained by energizing a "
        "snowball. "
    ): "충전된 눈덩이는 땅이나 몹에 맞으면 번개를 떨어뜨립니다. 일반 눈덩이에 에너지를 주입해 만들 수 있습니다. ",
    "The Wrench has 3 modes: ": "렌치에는 3가지 모드가 있습니다. ",
    "Config Mode: used to change cables I/O configuration. ": "설정 모드: 케이블의 입출력 설정을 바꿉니다. ",
    "Link Mode: used to link linkable blocks like energizing orb and rods. ": "연결 모드: 에너지 주입 오브와 막대처럼 서로 연결할 수 있는 블록을 연결합니다. ",
    "Rotate Mode: used to rotate blocks horizontally. ": "회전 모드: 블록을 수평으로 회전합니다. ",
    "Player Aerial Pearl used to craft the player transmitter. ": "플레이어 공중 진주는 플레이어 송신기 제작에 사용합니다. ",
    "You can get it by using an Aerial Pearl on a Zombie or Husk. ": "좀비나 허스크에게 공중 진주를 사용하면 얻을 수 있습니다. ",
    (
        "Charge items when is in player inventory, can Also be used to upgrade "
        "the capacity of a Ender Network channel by Shift clicking a Battery to "
        "an Ender Cell GUI, if the Battery contain energy then will also be "
        "applied to the ender network channel. "
    ): "배터리는 플레이어 인벤토리의 아이템을 충전합니다. 엔더 셀 화면에서 배터리를 Shift+클릭하면 엔더 네트워크 채널의 용량을 늘릴 수 있으며, 배터리에 저장된 전력도 채널로 함께 옮겨집니다. ",
    "When Applying a Lens Of Ender to a Solar Panel will make it see through blocks. ": "태양광 패널에 엔더 렌즈를 장착하면 위쪽의 블록을 투과해 햇빛을 받을 수 있습니다. ",
}

INDEX_LINKS = {
    "Generators": "발전기",
    "Storage / Transfer": "저장 및 전송",
    "Functional Blocks": "기능 블록",
    "Items": "아이템",
    "Materials": "재료",
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def find_jar(instance: Path, prefix: str) -> Path:
    """설치된 JAR 하나를 접두사로 확정한다."""
    matches = sorted(
        path
        for path in (instance / "mods").glob("*.jar")
        if path.name.lower().startswith(prefix.lower())
    )
    if len(matches) != 1:
        raise RuntimeError(f"JAR을 하나로 확정하지 못했습니다: {prefix}:{matches}")
    return matches[0]


def apply_quest_overrides() -> dict[str, object]:
    """검수에서 확정한 퀘스트 번역을 작업본에 반영한다."""
    found: set[str] = set()
    changed = 0
    for root in sorted((WORK_ROOT / "quests").glob("*")):
        english_path = root / "en_us.json"
        korean_path = root / "ko_kr.json"
        if not english_path.is_file() or not korean_path.is_file():
            continue
        english = load_json(english_path)
        korean = load_json(korean_path)
        for key in english:
            if key not in QUEST_OVERRIDES:
                continue
            translated = QUEST_OVERRIDES[key]
            errors = quest_snbt.validate_value(key, english[key], translated)
            if errors:
                raise ValueError("; ".join(errors))
            found.add(key)
            if korean[key] != translated:
                korean[key] = translated
                changed += 1
        korean_path.write_text(
            json.dumps(korean, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    missing = sorted(set(QUEST_OVERRIDES) - found)
    if missing:
        raise KeyError(
            f"퀘스트 영어 원문에서 확정 번역 키를 찾지 못했습니다: {missing}"
        )
    return {"overrides": len(found), "changed": changed}


def guide_source_names(archive: ZipFile) -> list[str]:
    """Powah! 영어 GuideME Markdown 경로를 반환한다."""
    prefix = f"{POWAH_GUIDE_ROOT}/"
    return sorted(
        name
        for name in archive.namelist()
        if name.startswith(prefix)
        and name.endswith(".md")
        and not name[len(prefix) :].startswith("_")
    )


def translate_guide(text: str, replacements: Counter[str]) -> str:
    """GuideME 원문의 표시 문구만 확정 번역으로 교체한다."""
    for english, korean in GUIDE_TITLES.items():
        for source, target in (
            (f"  title: {english}", f"  title: {korean}"),
            (f"# {english}", f"# {korean}"),
        ):
            count = text.count(source)
            if count:
                text = text.replace(source, target)
                replacements[source] += count
    for english, korean in GUIDE_PARAGRAPHS.items():
        count = text.count(english)
        if count:
            text = text.replace(english, korean)
            replacements[english] += count
    for english, korean in INDEX_LINKS.items():
        source = f"[{english}]"
        count = text.count(source)
        if count:
            text = text.replace(source, f"[{korean}]")
            replacements[source] += count
    lines = []
    for line in text.splitlines(keepends=True):
        ending = "\n" if line.endswith("\n") else ""
        line = line.rstrip("\r\n")
        if line.lstrip().startswith("|") and "<" not in line:
            for english, korean in (
                ("Capacity", "용량"),
                ("Generates", "발전량"),
                ("Generation Factor", "발전 계수"),
                ("Max Extract", "최대 출력"),
                ("Max I/O", "최대 입출력"),
            ):
                line = re.sub(
                    rf"(?<=\| ){re.escape(english)}(?= +\|)",
                    korean,
                    line,
                )
        lines.append(line.rstrip() + ending)
    return "".join(lines)


def build_guides(instance: Path) -> dict[str, object]:
    """설치 JAR의 영어 GuideME 페이지에서 한국어 페이지를 생성한다."""
    jar = find_jar(instance, "Powah-")
    replacements: Counter[str] = Counter()
    outputs: list[str] = []
    with ZipFile(jar) as archive:
        names = guide_source_names(archive)
        for name in names:
            relative = Path(name).relative_to(POWAH_GUIDE_ROOT)
            source = archive.read(name).decode("utf-8-sig")
            translated = translate_guide(source, replacements)
            destination = GUIDE_OUTPUT / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(translated, encoding="utf-8")
            outputs.append(destination.relative_to(PROJECT_ROOT).as_posix())
    missing_paragraphs = sorted(
        source for source in GUIDE_PARAGRAPHS if replacements[source] == 0
    )
    if missing_paragraphs:
        raise ValueError(f"GuideME 원문 문단을 찾지 못했습니다: {missing_paragraphs}")
    return {
        "jar": jar.name,
        "pages": len(outputs),
        "translated_paragraph_occurrences": sum(
            replacements[source] for source in GUIDE_PARAGRAPHS
        ),
        "outputs": outputs,
    }


def verify_guides(instance: Path) -> tuple[dict[str, object], list[str]]:
    """GuideME 페이지의 경로, 태그, 링크와 미번역 원문을 검증한다."""
    jar = find_jar(instance, "Powah-")
    errors: list[str] = []
    checked = 0
    with ZipFile(jar) as archive:
        names = guide_source_names(archive)
        expected = {
            Path(name).relative_to(POWAH_GUIDE_ROOT).as_posix() for name in names
        }
        actual = {
            path.relative_to(GUIDE_OUTPUT).as_posix()
            for path in GUIDE_OUTPUT.rglob("*.md")
        }
        if actual != expected:
            errors.append(
                f"GuideME 페이지 경로 불일치: 누락={sorted(expected - actual)}, "
                f"초과={sorted(actual - expected)}"
            )
        for name in names:
            relative = Path(name).relative_to(POWAH_GUIDE_ROOT)
            output = GUIDE_OUTPUT / relative
            if not output.is_file():
                continue
            source = archive.read(name).decode("utf-8-sig")
            target = output.read_text(encoding="utf-8")
            checked += 1
            if TAG.findall(source) != TAG.findall(target):
                errors.append(f"GuideME 태그 순서 불일치: {relative.as_posix()}")
            source_links = re.findall(r"\]\(([^)]*)\)", source)
            target_links = re.findall(r"\]\(([^)]*)\)", target)
            if source_links != target_links:
                errors.append(f"GuideME 링크 순서 불일치: {relative.as_posix()}")
            remaining = [
                paragraph
                for paragraph in GUIDE_PARAGRAPHS
                if paragraph in source and paragraph in target
            ]
            if remaining:
                errors.append(
                    f"GuideME 영어 문단 유지: {relative.as_posix()}:{remaining}"
                )
            for english in GUIDE_TITLES:
                if english != "Powah" and (
                    f"  title: {english}" in target or f"# {english}" in target
                ):
                    errors.append(
                        f"GuideME 영어 제목 유지: {relative.as_posix()}:{english}"
                    )
    return {
        "jar": jar.name,
        "pages_checked": checked,
        "path_parity": not any("페이지 경로" in error for error in errors),
        "tag_and_link_order_checked": True,
    }, errors


def nested_display_fields(value: object) -> list[object]:
    """발전 과제 JSON의 title·description 표시 값을 모은다."""
    found: list[object] = []
    if isinstance(value, dict):
        display = value.get("display")
        if isinstance(display, dict):
            found.extend(
                display[key] for key in ("title", "description") if key in display
            )
        for child in value.values():
            found.extend(nested_display_fields(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(nested_display_fields(child))
    return found


def verify_advancements(instance: Path) -> tuple[dict[str, object], list[str]]:
    """Powah! 발전 과제의 사용자 표시 문자열 경로를 전수 검사한다."""
    jar = find_jar(instance, "Powah-")
    errors: list[str] = []
    files = 0
    fields = 0
    literals: list[str] = []
    translate_keys: list[str] = []
    translations = load_json(OUTPUT_ASSETS / "powah/lang/ko_kr.json")
    with ZipFile(jar) as archive:
        names = [
            name
            for name in archive.namelist()
            if name.startswith("data/powah/advancement/") and name.endswith(".json")
        ]
        files = len(names)
        for name in names:
            data = json.loads(archive.read(name).decode("utf-8-sig"))
            for value in nested_display_fields(data):
                fields += 1
                if isinstance(value, str):
                    literals.append(f"{name}:{value}")
                elif isinstance(value, dict) and isinstance(
                    value.get("translate"), str
                ):
                    key = value["translate"]
                    translate_keys.append(key)
                    if key.startswith(
                        ("item.powah.", "block.powah.", "advancement.powah.")
                    ):
                        if key not in translations:
                            errors.append(f"발전 과제 번역 키 누락: {name}:{key}")
    if literals:
        errors.append(f"발전 과제 literal 표시 문구가 있습니다: {literals}")
    return {
        "jar": jar.name,
        "files_checked": files,
        "display_fields": fields,
        "translate_keys": len(translate_keys),
        "literal_display_fields": len(literals),
    }, errors


def verify_kubejs(instance: Path) -> tuple[dict[str, object], list[str]]:
    """KubeJS의 모드군 참조와 직접 표시 문자열 후보를 검사한다."""
    root = instance / "kubejs"
    references: list[str] = []
    display_candidates: list[str] = []
    family = re.compile(r"powah|fluxnetworks|flux networks", re.IGNORECASE)
    display = re.compile(
        r"displayName|tooltip|Text\.(?:of|literal)|custom_name|\bname\s*:",
        re.IGNORECASE,
    )
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".js",
            ".json",
            ".snbt",
            ".md",
            ".txt",
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        if not family.search(text):
            continue
        relative = path.relative_to(instance).as_posix()
        references.append(relative)
        for number, line in enumerate(text.splitlines(), 1):
            if family.search(line) and display.search(line):
                display_candidates.append(f"{relative}:{number}:{line.strip()}")
    errors = []
    if display_candidates:
        errors.append(
            "KubeJS 직접 표시 문자열 후보를 수동 분류해야 합니다: "
            + " | ".join(display_candidates[:30])
        )
    return {
        "files_referencing_family": len(references),
        "referenced_paths": references,
        "direct_display_candidates": len(display_candidates),
    }, errors


def verify_quest_overrides() -> tuple[dict[str, object], list[str]]:
    """확정 퀘스트 번역이 누적 SNBT에 반영되었는지 확인한다."""
    output = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    errors = [
        f"퀘스트 확정 번역 불일치: {key}"
        for key, value in QUEST_OVERRIDES.items()
        if output.get(key) != value
    ]
    return {
        "reviewed_overrides": len(QUEST_OVERRIDES),
        "matching_output": len(QUEST_OVERRIDES) - len(errors),
    }, errors


def deployment_report() -> dict[str, object]:
    """가장 최근 적용 기록에서 이 모드군의 해시 일치 결과를 모은다."""
    manifests = sorted(
        (PROJECT_ROOT / "temp/backups").glob("*/backup_manifest.json"),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )
    if not manifests:
        return {"status": "not_applied", "hash_matches": 0, "changed_paths": []}
    path = manifests[0]
    manifest = load_json(path)
    targets = manifest.get("targets", [])
    if not isinstance(targets, list) or not targets:
        return {"status": "not_applied", "hash_matches": 0, "changed_paths": []}
    target = targets[0]
    assert isinstance(target, dict)
    files = target.get("files", [])
    relevant = []
    for row in files if isinstance(files, list) else []:
        if not isinstance(row, dict):
            continue
        relative = str(row.get("relative_path", ""))
        if relative == "config/ftbquests/quests/lang/ko_kr.snbt" or relative.startswith(
            (
                "resourcepacks/ATM10_Korean/assets/powah/",
                "resourcepacks/ATM10_Korean/assets/lollipop/",
                "resourcepacks/ATM10_Korean/assets/fluxnetworks/",
            )
        ):
            relevant.append(row)
    matches = sum(
        row.get("source_sha256") == row.get("after_sha256") for row in relevant
    )
    changed = sorted(
        str(row["relative_path"]) for row in relevant if row.get("changed")
    )
    return {
        "status": (
            "applied_and_verified"
            if relevant and matches == len(relevant)
            else "incomplete"
        ),
        "target": target.get("target_root"),
        "backup_manifest": path.relative_to(PROJECT_ROOT).as_posix(),
        "files_checked": len(relevant),
        "hash_matches": matches,
        "changed_paths": changed,
        "unexpected_changes": target.get("unexpected_changes", []),
    }


def verify(instance: Path) -> tuple[dict[str, object], int]:
    """Powah!·Flux Networks 전체 표시 경로 완료 보고서를 만든다."""
    errors: list[str] = []
    core_path = WORK_ROOT / "language_validation.json"
    core = load_json(core_path) if core_path.is_file() else {}
    if core.get("status") != "complete":
        errors.append("언어·FTB Quests 핵심 검증이 완료되지 않았습니다.")
    quests, quest_errors = verify_quest_overrides()
    guides, guide_errors = verify_guides(instance)
    advancements, advancement_errors = verify_advancements(instance)
    kubejs, kubejs_errors = verify_kubejs(instance)
    errors.extend(quest_errors)
    errors.extend(guide_errors)
    errors.extend(advancement_errors)
    errors.extend(kubejs_errors)
    provenance = core.get("language_provenance", {})
    report = {
        "family": "Powah!·Flux Networks",
        "installed_versions": ["Powah-6.2.10.jar", "FluxNetworks-1.21.1-8.0.0.jar"],
        "language_provenance": provenance,
        "ftbquests": {**core.get("ftbquests", {}), **quests},
        "guides": guides,
        "advancements": advancements,
        "kubejs": kubejs,
        "deployment": deployment_report(),
        "validation_errors": len(errors),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    path = WORK_ROOT / "family_completion.json"
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    args = parser.parse_args()
    instance = resolve_source_root()
    if args.command == "build":
        result = {
            "quests": apply_quest_overrides(),
            "guides": build_guides(instance),
        }
        status = 0
    else:
        result, status = verify(instance)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
