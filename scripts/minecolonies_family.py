#!/usr/bin/env python3
"""MineColonies 계열 언어와 관련 FTB Quests를 현재 영어 원문으로 전면 재검수해요."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import actually_additions_family as candidate_helper
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "minecolonies"
ROOT = PROJECT_ROOT / "working" / FAMILY
CACHE = PROJECT_ROOT / "temp/minecolonies_candidate_cache_v1.json"
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
LATIN = re.compile(r"[A-Za-z]{3,}")
LANGUAGES = {
    "minecolonies": "MineColonies",
    "structurize": "Structurize",
    "domum_ornamentum": "Domum Ornamentum",
    "blockui": "BlockUI",
}

KEY_EXACT = {
    "itemGroup.minecolonies": "MineColonies",
    "key.minecolonies.categories.general": "MineColonies",
    "com.minecolonies.configgui.title": "MineColonies 설정",
    "minecolonies.config.showdyetooltips": "가죽 아이템의 염색 색상 툴팁 표시",
    "minecolonies.config.showdyetooltips.comment": (
        "활성화하면 염색한 가죽 아이템에 필요한 색상을 알려 주는 툴팁이 표시됩니다."
    ),
    "minecolonies.config.diseasemodifier": "질병 발생 빈도",
    "minecolonies.config.research.comment": "연구 시스템과 관련된 모든 설정",
    "block.structurize.blockbarreldeco_onside": "가로형 나무통",
    "block.structurize.blockbarreldeco_standing": "세로형 나무통",
    "block.structurize.blockfluidsubstitution": "유체 자리표시자",
    "block.structurize.blocksolidsubstitution": "고체 자리표시자",
    "block.structurize.blocksubstitution": "자리표시자 블록",
    "block.structurize.blocktagsubstitution": "태그 기준점 블록",
    "block.domum_ornamentum.architectscutter": "건축가의 절단기",
    "domum_ornamentum.architectscutter": "건축가의 절단기",
    "blockui.container_gui.client_side_only": (
        "통합 서버에서 플레이할 때만 컨테이너 내용을 볼 수 있습니다"
        "(싱글플레이, LAN 비공개)."
    ),
    "blockui.container_gui.empty": "이 컨테이너는 비어 있습니다.",
    "blockui.tooltip.item_additional_info": "%s 키를 누르면 추가 정보를 표시합니다",
    "blockui.tooltip.properties": "블록 상태 속성:",
    "blockui.config.default.boolean": "[기본값: %s]",
    "blockui.config.default.string": "[기본값: %s]",
    "blockui.config.default.enum": "[기본값: %s, 값: %s]",
    "blockui.config.default.number": "[기본값: %s, 최솟값: %s, 최댓값: %s]",
    "key.structurize.categories.general": "Structurize",
    "item.sceptersteel.scanformat": "스캔_%s",
    "itemGroup.structurize": "Structurize",
}

KEY_EXACT.update(
    {
        "com.minecolonies.coremod.workorderadded": (
            "%s 건설 요청이 콜로니 %s에 생성되었습니다! 건물 블록의 위치는 %s, %s, %s입니다."
        ),
        "com.minecolonies.core.gui.colony.delete.warning": (
            "⚠ 경고 ⚠ \n\n 이미 관리 중인 정착지가 있습니다. \n [%d %d %d]의 %s "
            "정착지입니다. "
            "\n\n 이곳에 다른 정착지를 세우려면 기존 정착지를 완전히 철거하여 유령 도시로 "
            "남겨야 합니다."
        ),
        "com.minecolonies.core.gui.colony.abandon.warning": (
            "⚠ 경고 ⚠ \n\n 이미 관리 중인 정착지가 있습니다. \n [%d %d %d]의 %s "
            "정착지입니다. "
            "\n\n 이곳에 다른 정착지를 세우려면 두 가지 방법이 있습니다. \n\n "
            "- 기존 정착지를 완전히 철거하여 유령 도시로 남깁니다. \n\n "
            "- 시장 자리에서 물러나 기존 콜로니의 장교로 남습니다."
        ),
        "com.minecolonies.coremod.workorder.outofcolony": (
            "%s 건설 명령(x: %d, z: %d)은 콜로니 밖에 있어 건설할 수 없습니다!"
        ),
        "com.minecolonies.coremod.request.crafting.display": "%d * 제작법: %s",
        "com.minecolonies.coremod.gui.workerhuts.assignedbed": (
            "%s이(가) %s 직업을 맡았습니다. %s(%s)에 새 주민을 위한 빈 침대가 생겼습니다."
        ),
        "com.minecolonies.coremod.gui.workerhuts.knighttraineeassignbed": (
            "%s이(가) 기사 훈련병이 되었습니다. %s(%s)에 새 주민을 위한 빈 침대가 생겼습니다."
        ),
        "com.minecolonies.coremod.gui.workerhuts.archertraineeassignbed": (
            "%s이(가) 궁수 훈련병이 되었습니다. %s(%s)에 새 주민을 위한 빈 침대가 생겼습니다."
        ),
        "com.minecolonies.coremod.gui.workerhuts.guardassignbed": (
            "%s이(가) 경비원이 되었습니다. %s(%s)에 새 주민을 위한 빈 침대가 생겼습니다."
        ),
        "com.minecolonies.coremod.gui.tavern.visitordeath": (
            "방문객 %s이(가) %s 때문에 %s에서 사망했습니다. 여관이 위험하다는 소문이 "
            "퍼져 앞으로 방문객이 줄어들 수 있습니다!"
        ),
        "com.minecolonies.coremod.gui.townhall.stats.pickups_made": "%d번 이동(출발지: %s)",
        "com.minecolonies.coremod.invalidbuilding": (
            "%s 건물(%d %d %d)에 %s 양식의 원래 설계도가 없습니다. 건물이 작동하지 않을 수 "
            "있으니 설계도를 복구하거나 건물을 회수한 뒤 다시 배치하세요."
        ),
        "com.minecolonies.coremod.pvp.townhall.broke": (
            "경고!!! %s이(가) 마을회관을 %d%% 넘게 파괴했습니다! 100%%가 되면 잃게 됩니다!!!"
        ),
        "com.minecolonies.coremod.colonysizechange": "%d청크 안의 %s 영토를 모두 확보했습니다.",
        "com.minecolonies.coremod.pvp.attack.guardgroupsize": (
            "§e주의하세요. %s§e에는 현재 경비가 %d명§e 있습니다!"
        ),
        "com.minecolonies.coremod.pvp.defended.success": (
            "§a%s§a의 공격으로부터 콜로니를 성공적으로 방어했습니다."
        ),
        "com.minecolonies.coremod.crafters.recipeimproved.0": (
            "%s이(가) %s 제작법에서 필요한 %s의 양을 줄이는 데 성공했습니다."
        ),
        "com.minecolonies.coremod.item.scroll.wrong_building": (
            "%s(%s)에 자원 스크롤을 연결할 수 없습니다."
        ),
        "com.minecolonies.coremod.request.toolow": (
            "%s 블록(%d %d %d)을 캘 수 없어요. 더 높은 채굴 단계의 도구를 쓸 수 있도록 "
            "건물을 업그레이드하거나 직접 캐 주세요."
        ),
        "com.minecolonies.coremod.item.buildlevel.gui": "%s의 단계가 %s 이상일 때 제작됨",
        "com.minecolonies.coremod.questobjectives.buildbuilding.progress.cumulative": (
            "%d/%d: 건설한 %s 건물의 누적 단계"
        ),
        "com.minecolonies.coremod.questobjectives.buildbuilding.cumulative.existing": (
            "%s 건물의 누적 단계가 %d에 도달하기를 기다리고 있어요!"
        ),
        "com.minecolonies.coremod.research.limit.requirement": "요구 조건: %s %s",
        "com.minecolonies.coremod.gui.colony.here": "%s 안에 있습니다(소유자: %s)",
        "com.minecolonies.coremod.item.scroll.no_builder": "§o건축가 없음",
        "advancements.minecolonies.army_8.title": "§o분대장",
        "item.minecolonies.pirate_cap": "해적 캡",
        "advancements.minecolonies.build.mysticalsite_5.description": (
            "신비한 제단을 5단계로 업그레이드하여 온 세상의 부러움을 사세요!"
        ),
        "com.minecolonies.coremod.info.citizen.0": (
            "주택은 주민이 사는 곳입니다. 주택 단계마다 주민 한 명을 수용하므로 모두에게 "
            "거처를 마련하려면 주택이 여러 채 필요합니다. 경비원만 주택에서 살지 않습니다."
        ),
        "com.minecolonies.coremod.info.lumberjack.0": (
            "산림 관리인은 콜로니의 생산 일꾼입니다. 도끼를 주면 주변 나무를 베고 묘목이 "
            "있을 때 그 자리에 다시 심습니다.\n 벨 수 있는 나무를 제한하려면 두 번째 "
            "페이지를 확인하세요.\n 세 번째 페이지에서는 묘목을 다시 심지 않도록 설정하고, "
            "세 번째 버튼으로 받는 도구를 사용해 작업 구역을 특정 3D 상자로 제한할 수 있습니다."
        ),
        "com.minecolonies.coremod.info.fisherman.1": (
            "제한 사항:\n\n 1. 낚시꾼에게는 가로 일곱 블록, 세로 일곱 블록 이상이고 "
            "깊이가 한 블록 이상인 물이 필요합니다. 건물 블록은 물과 같은 높이에 있어야 하며 "
            "물에서 열 블록 이내여야 합니다."
        ),
        "advancements.minecolonies.colony_population_50.description": (
            "주민 50명이면 직업마다 일꾼을 한 명씩 두고도 남습니다!"
        ),
        "com.minecolonies.coremod.info.barracks.0": (
            "병영은 군사 방어의 중심입니다. 병영이 없으면 병영 탑을 지을 수 없습니다!\n "
            "병영 하나에는 단계마다 하나씩, 네 단계까지 병영 탑을 네 개 둘 수 있습니다."
        ),
        "minecolonies.quests.general.alchemy.obj0.answer0.reply.answer2": "음, 세 개만요?",
        "com.minecolonies.coremod.info.barrackstower.0": (
            "병영 탑은 군사 방어의 중심입니다. 병영 탑은 단계마다 경비원 1명을 고용하여 총 "
            "5명까지 둘 수 있습니다. 경비원은 탑에서 생활하므로 다른 주민이 쓸 침대도 "
            "확보됩니다.\n경비원은 검을 쓰는 기사와 활을 쓰는 궁수로 나뉩니다."
        ),
        "com.minecolonies.coremod.info.barrackstower.1": (
            "제한 사항:\n\n 1. 건물 단계에 따라 경비원이 사용할 수 있는 도구가 "
            "늘어납니다:\n   0단계. 나무/금 도구\n   1단계. 돌 도구\n   2단계. 철 도구\n   "
            "3단계. 다이아몬드 도구\n   4-5단계. 마법 부여된 도구\n\n "
        ),
        "minecolonies.config.loadtime.comment": (
            "플레이어가 떠난 뒤 청크가 로드된 상태로 유지되는 시간입니다. 재시작 후에는 "
            "유지되지 않습니다. 기본값: 10분"
        ),
        "minecolonies.config.builderbuildblockdelay.comment": (
            "블록을 하나 설치한 뒤의 지연 시간입니다. 값을 높이면 지연 시간도 늘어납니다."
        ),
        "tile.blockhut.noworkerassigned": (
            "일꾼이 없는 작업소에는 작업 지시를 배정할 수 없습니다."
        ),
        "tile.blockhut.cannotbuild": (
            "건설할 수 없는 건축가에게 작업 지시를 배정할 수 없습니다."
        ),
        "entity.deliveryman.forcepickupfailed": (
            "처리할 수 없습니다. 이미 회수 작업이 진행 중입니다!"
        ),
        "death.attack.entity.minecolonies.chiefbarbarian": (
            "%s이(가) 바바리안 대족장에게 으깨졌습니다"
        ),
        "death.attack.entity.minecolonies.campchiefbarbarian": (
            "%s이(가) 바바리안 대족장에게 으깨졌습니다"
        ),
        "death.attack.entity.minecolonies.chiefpirate": (
            "%s이(가) 해적 선장에게 으깨졌습니다"
        ),
        "death.attack.entity.minecolonies.campchiefpirate": (
            "%s이(가) 해적 선장에게 으깨졌습니다"
        ),
        "com.minecolonies.command.whereami.closecolony": (
            "어떤 콜로니 안에도 없습니다. 가장 가까운 콜로니는 %s(ID: %s)이며 약 "
            "%s블록 떨어져 있습니다."
        ),
        "com.minecolonies.command.whereami.incolony": (
            "%s 콜로니(ID: %s) 안에 있습니다. 콜로니 중심은 약 %s블록 떨어져 있습니다."
        ),
        "com.minecolonies.command.whoami.hascolony": (
            "플레이어: %s. 소유 콜로니는 %s(ID: %s, 위치: %s)입니다."
        ),
        "com.minecolonies.coremod.buildtool.indestructible": (
            "건물 블록을 설치하지 못했습니다! 설치할 위치의 블록은 파괴할 수 없습니다!"
        ),
        "com.minecolonies.coremod.raid.end.barbarian_raid1": (
            "%s에서 온 바바리안들은 방어선을 뚫지 못하고 최후를 맞았습니다."
        ),
        "com.minecolonies.coremod.pvp.attack.start": (
            "§c조심하세요. %s§c이(가) 경비원들을 이끌고 공격하고 있습니다!"
        ),
        "com.minecolonies.coremod.progress.newchild": (
            "새 아이 %s이(가) 이제 %s에서 행복하게 살고 있습니다!"
        ),
        "advancements.minecolonies.build.lumberjack.description": (
            "건축 도구로 나무꾼 작업소를 배치하고 완공하여 더 많은 건물에 쓸 목재를 "
            "모으세요."
        ),
        "advancements.minecolonies.build.smeltery_5.description": (
            "5단계 제련소는 광석 블록을 처리할 때 행운 4를 적용합니다. 이보다 더 좋을 "
            "수는 없겠죠!"
        ),
        "com.minecolonies.coremod.jei.baker": (
            "빵을 굽고, 단계가 오르면 다른 음식도 만듭니다. 3단계부터 추가 제작법을 "
            "가르칠 수 있습니다."
        ),
        "com.minecolonies.coremod.jei.sifter": (
            "흔한 자원에서 드물게 귀중한 자원을 걸러냅니다. 거름망은 오래가지만 결국 "
            "부서질 수 있습니다."
        ),
        "com.minecolonies.core.settlementcovenant3.hasclose": (
            "또한, 이웃 정착지 %s(이곳에서 %s블록 이내)와 건설적인 관계를 맺을 것을 "
            "엄숙히 약속합니다."
        ),
        "com.minecolonies.research.civilian.gorger.subtitle": "더!???",
        "com.minecolonies.research.effects.sleeplessmultiplier.description": (
            "경비원에게 필요한 수면 시간 감소"
        ),
        "minecolonies.quests.tutorial.restaurant.obj0.answer0.reply": (
            "식당의 웨이터는 화로에서 음식을 자동으로 요리할 뿐 아니라 배고픈 주민에게 "
            "음식도 나눠 줍니다. 이제 방법은 아시죠? 제작대에서 식당 블록을 만드세요. "
            "이번에는 사과를 판자로 둘러싸고 맨 위에 건축 도구를 놓으면 됩니다.'"
        ),
        "com.minecolonies.research.civilian.scholarly.subtitle": "향후 십 년간 할 숙제... 확인!",
        "minecolonies.config.averageemptycolonydistance.comment": (
            "비어 있는 콜로니 2곳 사이의 평균 거리(청크)"
        ),
        "com.minecolonies.coremod.info.barracks.2": (
            "자주 묻는 질문:\n\n Q 1. 병영을 1개보다 많이 지을 수 있나요?\n   A 1. "
            "네. 다만 병영 탑의 단계는 연결된 병영을 따릅니다. 한 병영이 5단계여도 두 번째 "
            "병영이 1단계라면 그 병영에는 1단계 탑 하나만 둘 수 있습니다."
        ),
        "com.minecolonies.coremod.entity.citizen.demands.unemployment": (
            "두 주 넘게 일자리를 기다리고 있어요! 정말 화가 납니다!"
        ),
        "com.minecolonies.coremod.citizen.rename.same": (
            "주민 두 명에게 같은 이름을 붙일 수 없어 이름 변경에 실패했습니다!"
        ),
        "minecolonies.quests.tutorial.university.obj0.answer0.reply.answer0.reply": (
            "좋아요. 제작 격자의 가운데와 아래 칸에 책을 놓고 판자로 둘러싼 다음 위쪽에 "
            "건설 도구를 놓아 대학 건물 블록을 만드세요. 콜로니 안의 적당한 장소에 배치한 "
            "뒤 건축가에게 1단계까지 건설하게 하세요."
        ),
        "minecolonies.quests.general.alchemy.obj0.answer0.reply": (
            "훌륭해요! 좀비 세 마리의 살점이 필요합니다!"
        ),
        "com.minecolonies.coremod.gui.tooldesc.scepterlumberjack": (
            "도구로 한쪽 모서리를 우클릭하고 반대쪽 모서리를 좌클릭하여 산림 관리인의 3D "
            "작업 구역을 지정하세요. 높이도 포함됩니다."
        ),
        "com.minecolonies.coremod.research.research.maxunlocked": (
            "분기마다 6단계 연구는 최대 1개"
        ),
        "com.minecolonies.coremod.entity.citizen.no.slepttonight": (
            "지난 사흘 동안 잠자리에 들 시간이 부족했어요!"
        ),
        "com.minecolonies.coremod.gui.chat.recruitstory12": "*중얼거림* 포스가 함께하길.",
        "com.minecolonies.coremod.gui.interval.yesterday": "어제부터",
        "advancements.minecolonies.build.smeltery_3.title": "두 배로 곤란해!",
        "com.minecolonies.coremod.info.barracks.1": (
            "제한 사항:\n\n 1. 병영에는 단계마다 병영 탑을 1개만 둘 수 있고, 탑의 "
            "단계는 병영보다 높을 수 없습니다. 1단계 병영에는 최대 1단계인 병영 탑을 "
            "1개만 둘 수 있습니다. 3단계 병영에는 최대 3단계인 병영 탑을 3개 둘 수 있습니다."
        ),
        "com.minecolonies.coremod.entity.citizen.demands.idleatjob": (
            "두 주 넘게 일을 못 하고 있어요! 뭐라도 해 주세요!"
        ),
        "minecolonies.quests.tutorial.housing2.obj0": (
            "이제 2단계 건축가가 생겼으니 주거지를 업그레이드할 차례입니다. 주거지는 단계마다 "
            "주민 1명을 수용하며, 다섯 단계에서 최대 다섯 명까지 수용합니다."
        ),
        "com.minecolonies.core.gui.modules.stats.hidezerolabel": "값이 없는 항목 숨기기",
        "minecolonies.quests.tutorial.tavern.obj3": (
            "훌륭해요. 이제 모든 주민에게 거처를 제공하고 있습니다. 여관은 거주 공간 네 칸을 "
            "제공하지만 콜로니마다 한 채만 지을 수 있습니다. 잠시 뒤 다시 오면 다음 단계를 "
            "알려 드릴게요! 주민의 식량에 보태도록 보상으로 구운 감자를 받으세요!"
        ),
        "minecolonies.quests.general.cookies.obj0.answer0.reply": (
            "밀 두 개와 코코아콩 한 개가 필요해요!"
        ),
        "com.minecolonies.research.effects.plantationlarge.description": (
            "플랜테이션에 밭 1개 추가"
        ),
        "minecolonies.quests.guides.rallybanner.obj0": (
            "요즘 밤마다 스켈레톤이 많이 돌아다닙니다. 열 마리를 처치해 주시면 정말 "
            "고맙겠습니다!"
        ),
        "com.minecolonies.coremod.gui.interval.lastweek": "지난주",
        "minecolonies.quests.general.alchemy.obj2": (
            "가져온 살점이 조금 차갑네요. 따뜻한 좀비 살점이 필요합니다. 다시 세 개 부탁해요."
        ),
        "com.minecolonies.coremod.info.builder.0": (
            "건축가는 콜로니의 중심입니다. 건축가 없이는 아무 일도 진행할 수 없습니다!\n "
            "건축가를 제외한 모든 일꾼은 일을 시작하기 전에 건물이 최소 1단계여야 합니다. "
            "건축가의 건물이 0단계(건물 없음)라면 자기 건물 한 채만 지을 수 있습니다.\n\n "
            "건축가가 자기 건물이 아닌 건물을 건설, 업그레이드, 이동 또는 수리하려면 "
            "건축가의 건물이 대상 건물과 같은 단계 이상이어야 합니다. 예를 들어 3단계 건물을 "
            "지으려면 건축가의 건물도 3단계 이상이어야 합니다."
        ),
        "item.sceptersteel.point2": "두 번째 지점 저장: %d %d %d.",
        "domum_ornamentum.light.frame.type.four_light": "네 개",
        "minecolonies.config.turnoffexplosionsincolonies.comment": (
            "콜로니 보호 설정과 별개로 콜로니 안의 폭발을 끌지 설정합니다. DAMAGE_NOTHING은 "
            "폭발 피해를 완전히 막습니다. DAMAGE_PLAYERS는 플레이어와 적대적 몹에게만 피해를 "
            "줍니다. DAMAGE_ENTITIES는 모든 엔티티에게 피해를 줍니다. DAMAGE_EVERYTHING은 "
            "엔티티와 블록 모두에 피해를 줍니다."
        ),
        "com.minecolonies.building.stable.desc": "기병의 탈것을 마구간에서 돌봅니다.",
        "com.minecolonies.core.configsetting": "설정값 기준",
        "com.minecolonies.core.item.colonysign.tip": (
            "시작하려면 관문을 Shift+우클릭하세요.\n다른 콜로니로 이어지는 길에 50블록마다 "
            "표지판을 설치하세요.\n대상 관문이나 콜로니 표지판을 Shift+우클릭하면 연결이 "
            "완료됩니다."
        ),
        "com.minecolonies.core.item.sign.needcolony": (
            "연결된 콜로니 없음(웅크린 채 관문이나 앞서 설치한 표지판에 사용하세요)"
        ),
        "com.minecolonies.core.item.sign.nullcolony": (
            "콜로니를 찾을 수 없습니다. 이 표지판에 연결된 콜로니가 삭제되었을 수 있습니다."
        ),
        "com.minecolonies.core.gui.connectioneventlist.howto": (
            "동맹 연결 방법: \n\n - 자신의 콜로니에 관문을 건설하세요.\n\n- 대상 콜로니에도 "
            "관문이 있는지 확인하세요.\n\n- 두 관문 사이에 콜로니 표지판을 설치하여 연결하세요."
        ),
        "com.minecolonies.core.gui.residence.warning.3": (
            "경고: 높은 단계의 주민은 규칙적인 식사를 기대합니다. 업그레이드하기 전에 식당을 "
            "짓고 메뉴에 MineColonies 음식을 등록하세요."
        ),
        "minecolonies.quests.tutorial.mine.obj0": (
            "안녕하세요! 지금은 식량을 충분히 생산하고 있을 거예요. 주민의 보관함에 식량을 "
            "넣어 굶지 않게 해 주세요. 다음 단계는 광산을 가동하는 것입니다!"
        ),
        "minecolonies.quests.tutorial.restaurant.obj0.answer0.reply.answer1.reply": (
            "좋아요! 이제 건축 도구로 식당을 배치하고 건설을 누르세요. 지난번처럼 건축가에게 "
            "필요한 재료를 제공한 뒤 완공되면 돌아오세요!"
        ),
        "minecolonies.quests.tutorial.restaurant.obj1.answer1.reply": (
            "좋아요! 이제 건축 도구로 식당을 배치하고 건설을 누르세요. 지난번처럼 건축가에게 "
            "필요한 재료를 제공한 뒤 완공되면 돌아오세요!"
        ),
        "minecolonies.quests.tutorial.tieredfood.obj2": (
            "좋아요. 요리사의 주방이 완성됐으니 농부가 제작법에 필요한 작물을 기르는지 "
            "확인하세요. 괭이로 잔디, 양치식물, 덤불 같은 블록을 부수면 씨앗을 얻을 수 "
            "있습니다. 시작할 수 있도록 양파와 마늘을 드릴게요!"
        ),
        "com.minecolonies.core.gui.supplies.guide": (
            "이 보급품으로 %s을(를) 조립하여 새 콜로니의 기반을 마련하세요. 안에는 "
            "§2풍부한 자원§r과 함께\n회수한 §2마을회관 블록§r 및 새 콜로니의 터를 잡는 데 "
            "쓸 §2건축 도구§r가 들어 있습니다. 콜로니를 세우려면 끈기가 필요합니다. 거처, "
            "식량, 치료 같은 기본 생활뿐 아니라 해적과 야만인의 위협에 맞설 방어 시설도 "
            "갖춰야 합니다. 이 시련을 견디면 성장 가능성은 끝이 없습니다. 장인과 학자, 광부와 "
            "연금술사가 어우러진 정착지는 §2번영과 지식을 스스로 일구는 보루§r로 발전할 수 "
            "있습니다."
        ),
        "com.minecolonies.research.technology.woodwork.subtitle": (
            "나무를 다루는 목공은 어디에서 나무를 다룰까요?"
        ),
        "com.minecolonies.coremod.structures.nocustomhuts": (
            "건축가가 이 건물의 설계도를 알지 못합니다. 올바르게 처리했는지 확인하세요."
        ),
        "com.minecolonies.core.item.food.tooltip.tier.1": (
            "주민이 그럭저럭 받아들일 만한 음식입니다."
        ),
        "com.minecolonies.core.gui.restaurant.foodquality": (
            "%d단계 거주지의 주민까지 먹음"
        ),
        "tag.item.minecolonies.dyer_ingredient_excluded": "염색공 제작 제외 재료",
        "tag.item.minecolonies.farmer_product_excluded": "농부 제작 제외 생산물",
        "tag.item.minecolonies.fletcher_product_excluded": "화살 제작자 제작 제외 생산물",
        "key.structurize.categories.general": "Structurize",
        "itemGroup.structurize": "Structurize",
        "structurize.config.ignoreSchematicsFromJar": "JAR의 설계도 무시",
        "structurize.config.ignoreSchematicsFromJar.comment": (
            "JAR에 포함된 기본 설계도를 무시할지 설정합니다."
        ),
        "structurize.config.maxCachedSchematics": "최대 설계도 캐시 수",
        "structurize.config.maxCachedSchematics.comment": (
            "서버에 캐시할 수 있는 최대 설계도 수입니다."
        ),
        "structurize.gui.buildtool.creative_only": (
            "Structurize는 생존 모드에서 건축 도구 사용을 지원하지 않습니다. 크리에이티브 "
            "모드로 전환하거나 MineColonies를 설치하여 MineColonies 건축가를 이용하세요."
        ),
        "structurize.gui.manipulation.info": (
            "오른쪽 화살표 버튼이나 설정된 키로 미리보기를 이동하세요. Esc 키로 화면을 "
            "닫고 위치를 바꾼 뒤 다시 우클릭하면 돌아올 수 있습니다."
        ),
        "structurize.preview_renderer.exception": (
            "설계도 미리보기를 렌더링하는 중 오류가 발생했습니다. 가능하다면 latest.log를 "
            "이슈 추적기에 제출해 주세요."
        ),
        "structurize.preview_renderer.cannot_render": (
            "설계도 %s을(를) 렌더링하는 중 복구할 수 없는 오류가 발생했습니다. 가능하다면 "
            "latest.log를 이슈 추적기에 제출해 주세요."
        ),
        "com.ldtteam.tag.tooltip.groundlevel": (
            "건축 도구로 설계도를 지면에 맞춰 배치할 때 사용합니다."
        ),
        "com.ldtteam.tag.tooltip.invisible": (
            "통합 건물이나 폐광 같은 설계도를 건축 도구 미리보기에서 숨깁니다."
        ),
        "com.ldtteam.tag.tooltip.leisure": ("장식 컨트롤러를 여가 시설로 지정합니다."),
        "structurize.config.render_placeholders_nice.comment": (
            "비활성화하면 자리표시자를 일반 블록으로 렌더링합니다. 활성화하면 공기 "
            "자리표시자(밝음)는 없음으로, 유체(파랑)는 차원의 기본 유체로, 고체(갈색)는 "
            "월드 생성 블록으로, 태그(투명)는 내용 블록으로 표시합니다. 유체 및 고체 "
            "자리표시자는 싱글플레이어나 LAN 호스트에서만 정확히 작동하며, 그 외에는 최선의 "
            "추정값을 사용합니다. 현재 자동으로 갱신되지 않습니다."
        ),
        "minecolonies.scroll.noguardbuilding": (
            "먼저 경비탑이나 군사 기지 탑의 건물 블록에 웅크린 채 우클릭하여 이 스크롤을 "
            "등록하세요."
        ),
        "minecolonies.config.blueprintbuildmode": "설계도 제작 모드",
        "minecolonies.config.blueprintbuildmode.comment": (
            "현재 세계를 설계도 제작과 스캔에 사용하려면 활성화하세요."
        ),
        "com.minecolonies.coremod.gui.deco.level.none": (
            "이 설계도는 이미 최고 단계이거나 업그레이드할 수 없습니다!"
        ),
        "advancements.minecolonies.build.barracks_tower.description": (
            "새 군사 기지 안에 군사 기지 탑을 건설하세요. 탑은 군사 기지와 같은 단계까지만 "
            "올릴 수 있으며, 단계가 오를 때마다 배치할 수 있는 경비원 수가 늘어납니다!"
        ),
        "com.structurize.command.paste.no.blueprint": "지정한 설계도가 없습니다.",
        "structurize.pack.missing.blueprint": (
            "요청한 설계도가 같은 팩의 서버에 없습니다. 클라이언트 팩이 변경되었거나 서버 "
            "팩이 오래되었을 수 있습니다."
        ),
        "minecolonies.quests.tutorial.tieredfood.obj0": (
            "안녕하세요. 최근에 완공된 멋진 새 거주지를 봤어요. 그곳에 사는 주민들의 입맛이 "
            "조금 더 까다로워지기 시작한 것 같습니다."
        ),
        "minecolonies.config.pathNodeLimitMultiplier.comment": (
            "길 찾기 노드 제한을 지정한 배수만큼 늘립니다. 더 정확한 길 찾기를 위해 주민이 "
            "더 넓은 범위를 탐색하지만 오프스레드 성능 비용이 증가합니다."
        ),
        "com.minecolonies.coremod.info.cook.0": (
            "웨이터는 콜로니의 식량 생산을 담당합니다. 모든 주민에게 음식을 나눠 주고, 고기와 "
            "감자처럼 화로에서 굽기만 하면 되는 음식도 조리합니다.\n 주민이 배고프면 요리사에게 "
            "가서 먹을 것을 받습니다."
        ),
        "com.minecolonies.coremod.info.cook.1": (
            "자주 묻는 질문:\n\n Q 1. 웨이터가 이미 조리된 음식을 요청하는 것이 정상인가요?\n   "
            "A 1. 미리 조리한 음식을 주면 웨이터가 주민에게 나눠 줄 수 있습니다."
        ),
        "com.minecolonies.core.gui.residence.warning.4": (
            "경고: 높은 단계의 주민은 다양한 조리 음식을 요구합니다. 업그레이드하기 전에 "
            "식당에 요리사를 배치하고 메뉴를 충분히 채우세요."
        ),
        "minecolonies.quests.tutorial.builder.obj0.answer0.reply": (
            "좋아요. 이제 건축사무소를 지어 봅시다. 건축사무소 블록을 우클릭하고 '건축 설정'에 "
            "들어가 '건물 건설'을 누르세요."
        ),
        "structurize.config.transparency.warning": (
            "투명 렌더링은 대부분 올바르게 보이지만, 투명한 미리보기를 통해 볼 때 결과가 "
            "이상하거나 잘못 보이고 다른 물체 너머까지 보이는 경우가 있습니다. 투명도 설정을 "
            "변경하시겠습니까?"
        ),
        "structurize.pack.equaluser.error": (
            "서버에 플레이어 이름과 같은 팩이 있어 개인 스캔 배치를 방해할 수 있습니다. 이를 "
            "막으려면 서버에서 해당 팩을 삭제하세요."
        ),
    }
)

KEY_EXACT.update(
    {
        "com.minecolonies.command.resetstats.success": (
            "%s 콜로니(%s)의 모든 통계와 건물 %s개의 통계를 초기화했습니다."
        ),
        "com.minecolonies.coremod.tooltype.crossbow": "쇠뇌",
        "death.attack.entity.minecolonies.pierce": "%s의 방어구가 관통당했습니다!",
        "com.minecolonies.job.huscarl": "허스칼",
        "com.minecolonies.job.marksman": "명사수",
        "com.minecolonies.coremod.gui.workerhuts.huscarl": "허스칼",
        "com.minecolonies.coremod.gui.workerhuts.marksman": "명사수",
        "minecolonies:huscarl.job.desc": (
            "공격할 때마다 방어구를 가릅니다. 근접전에 취약합니다. 공격력은 강하지만 "
            "방패를 장비할 수 없습니다."
        ),
        "minecolonies:marksman.job.desc": (
            "먼 거리에서 방어구를 관통합니다. 탁 트인 곳에서 치명적이지만 궁수보다 "
            "공격 속도가 느립니다."
        ),
        "com.minecolonies.research.combat.slicedanddecided.name": "썰고 또 썰고!",
        "com.minecolonies.research.combat.thathitthemark.name": "정확히 명중!",
        "com.minecolonies.research.effects.huscarl.description": (
            "새 경비병 유형인 허스칼(도끼)을 잠금 해제합니다."
        ),
        "com.minecolonies.research.effects.marksman.description": (
            "새 경비병 유형인 명사수(쇠뇌)를 잠금 해제합니다."
        ),
        "minecolonies.quests.general.adayinthefield": "들판에서의 하루",
        "minecolonies.quests.general.adayinthefield.obj0": (
            "아, 마침 잘 오셨어요! 대학 학자들과 희귀한 약초를 모으러 현장 탐사를 "
            "계획하고 있었어요. 여기서 멀지 않은 곳에 제가 아는 멋진 장소가 있거든요. "
            "갈 때는 어렵지 않지만, 해가 지기 전에 모두를 무사히 데려올 수 있을지가 "
            "걱정이에요. 어두워지면 숲길이 위험해질 수 있잖아요! 모두를 한꺼번에 데려올 "
            "단체 순간이동 스크롤을 만들고 싶은데, 다른 일에 순간이동 스크롤을 모두 써 "
            "버렸어요. 세 장만 가져다주시겠어요?"
        ),
        "minecolonies.quests.general.adayinthefield.obj0.answer0": (
            "스크롤 세 장이요? 그 정도는 구할 수 있어요!"
        ),
        "minecolonies.quests.general.adayinthefield.obj0.answer1": (
            "스크롤이 꽤 많이 필요하네요. 그만큼은 내드리기 어려워요."
        ),
        "minecolonies.quests.general.adayinthefield.obj2": (
            "훌륭해요! 필요한 게 모두 모였어요. 단체 스크롤을 만들고 바로 떠날게요! "
            "학자들은 벌써 신이 나서 어쩔 줄 모르고 일주일 내내 탐사 이야기만 했답니다. "
            "내일 저를 찾아오시면 무엇을 모았는지 보여 드릴게요. 먼 길을 다녀올 만한 "
            "성과가 있으면 좋겠네요!"
        ),
        "minecolonies.quests.general.adayinthefield.obj2.answer0": (
            "찾으시는 걸 꼭 발견하길 바라요! 내일 다시 들를게요."
        ),
        "minecolonies.quests.general.adayinthefield.obj3": (
            "돌아오셨군요! 정말 굉장한 하루였어요! 학자들이 제가 기대한 것보다 두 배나 "
            "많이 찾았답니다. 횃불꽃과 난초를 비롯해 놀라운 표본이 한가득이에요! "
            "스크롤도 완벽하게 작동해서 모두가 저녁 식사 전에 무사히 돌아왔어요. 여기, "
            "탐사에서 남은 스크롤 한 장과 빌려주신 스크롤을 돌려드릴게요. 전부 당신 "
            "덕분이에요. 고마워요!"
        ),
        "minecolonies.quests.general.adayinthefield.obj3.answer0": (
            "아주 성공적인 탐사였군요! 도울 수 있어서 기뻐요."
        ),
        "minecolonies.quests.general.adayinthefield.obj3.answer1": (
            "무엇을 찾았는지 더 들려주세요!"
        ),
        "minecolonies.quests.general.adayinthefield.obj3.answer1.reply": (
            "어디서부터 이야기해야 할까요! 난초밭 바로 옆에 횃불꽃이 무리 지어 "
            "자라고 있었는데, 그런 모습은 처음 봤어요. 학자들도 몹시 들떠 있었답니다. "
            "하루 종일 이야기할 수도 있지만, 우선 보상부터 받으세요! 언젠가 꼭 다시 "
            "가야겠어요."
        ),
        "minecolonies.quests.general.adayinthefield.obj3.answer1.reply.answer0": (
            "정말 놀랍네요. 고마워요!"
        ),
        "minecolonies.quests.general.ancientmagic": "고대의 마법",
        "minecolonies.quests.general.ancientmagic.obj0": (
            "오! 아주 특별한 일이 벌어지고 있어요. 당신이 들어온 뒤로 제 수정들이 "
            "노래하듯 울리고 있거든요. 근처에 제가 실제로는 한 번도 접해 보지 못한, "
            "아주 오래되고 강력한 마법이 있어요... 혹시 여행 중에 신성한 재생 스크롤을 "
            "발견하셨나요? 낡은 양피지에 손을 대면 따뜻하고 은은한 라벤더 향이 나는 "
            "물건이에요. 오래전에 사라진 마법이라서 어떻게 다시 만들 수 있을지는 저도 "
            "도무지 모르겠어요. 최근 콜로니에 지독한 독감이 퍼져 의사 선생님이 감당하기 "
            "힘들 정도예요. 그런 스크롤이 있다면 부탁이에요. 당장 $1에게 가져다주세요. "
            "모든 상황을 바꿀 수도 있어요."
        ),
        "minecolonies.quests.general.ancientmagic.obj0.answer0": (
            "그런 물건을 가지고 있는 것 같아요..."
        ),
        "minecolonies.quests.general.ancientmagic.obj0.answer1": (
            "아직 그런 물건은 보지 못했어요."
        ),
        "minecolonies.quests.general.ancientmagic.obj0.answer2": (
            "이번에는 도와드리기 어려울 것 같아요."
        ),
        "minecolonies.quests.general.ancientmagic.obj2": (
            "오... 세상에. 이게 정말...? 글로만 읽어 봤지 실제로 본 적은 없어요... "
            "눈물이 날 것 같네요. 이게 어떤 의미인지 아시나요? 이번 주 내내 돌보느라 "
            "애썼던 모든 환자의 상황이 달라질 거예요. 바로 사용하겠습니다. 이렇게 "
            "귀한 물건은 대신할 것도 없고, 이런 고대 마법을 되돌려드릴 수도 없다는 걸 "
            "알아요. 그래도 이것들을 받아 주세요. 오늘 콜로니에 주신 것과 비교하면 "
            "보잘것없지만 진심을 담았어요."
        ),
        "minecolonies.quests.general.ancientmagic.obj2.answer0": (
            "모두 빨리 낫기를 바라요. 정말 훌륭한 일을 하고 계세요."
        ),
        "minecolonies.quests.general.ancientmagic.obj2.answer1": (
            "제가 더 도울 일이 있을까요?"
        ),
        "minecolonies.quests.general.ancientmagic.obj2.answer1.reply": (
            "당신처럼 우리를 돌봐 주는 사람이 있다는 사실만으로도 충분해요. 이제 "
            "가보세요. 오늘은 이미 넘칠 만큼 도와주셨어요. 진심으로, 마음 깊이 "
            "감사드려요."
        ),
        "minecolonies.quests.general.ancientmagic.obj2.answer1.reply.answer0": (
            "환자들을 잘 돌봐 주세요. 고마워요!"
        ),
        "minecolonies.quests.general.apromisetokeep": "지켜야 할 약속",
        "minecolonies.quests.general.apromisetokeep.obj0": (
            "들러 주셔서 잘됐어요! 경비원 한 분이 곤란한 일을 상담하러 왔어요. 가족을 "
            "보러 근처 마을에 다녀와야 하는데 오늘 밤 순찰 근무가 있어서 콜로니를 "
            "비워 두고 싶지 않대요. 순간이동 스크롤을 만들어 주면 제시간에 돌아올 수 "
            "있을 거라고 했어요. 재료가 조금 필요한데 도와주시겠어요?"
        ),
        "minecolonies.quests.general.apromisetokeep.obj0.answer0": (
            "물론이죠! 무엇이 필요한가요?"
        ),
        "minecolonies.quests.general.apromisetokeep.obj0.answer0.reply": (
            "좋아요! 종이 세 장과 나침반 하나면 돼요. 건축 도구는 이미 준비해 뒀어요. "
            "간단하죠! 재료만 있으면 스크롤을 금방 완성할 수 있어요."
        ),
        "minecolonies.quests.general.apromisetokeep.obj0.answer0.reply.answer0": (
            "바로 구해 올게요!"
        ),
        "minecolonies.quests.general.apromisetokeep.obj0.answer1": (
            "미안하지만 지금은 조금 바빠요."
        ),
        "minecolonies.quests.general.apromisetokeep.obj3": (
            "완벽해요! 스크롤은 벌써 완성했어요. 조금 전에 경비원이 들렀길래 곧바로 "
            "전해 줬답니다. 지금 어디선가 길을 걷고 있을 거예요. 가서 인사해 보시는 게 "
            "어때요? 당신의 도움으로 가능했다는 걸 알면 분명 고마워할 거예요!"
        ),
        "minecolonies.quests.general.apromisetokeep.obj3.answer0": (
            "좋아요! 찾아가 볼게요."
        ),
        "minecolonies.quests.general.apromisetokeep.obj4": (
            "오! 마법부여사가 재료를 모으도록 도와주신 분이군요! 이야기는 다 들었어요. "
            "사실 좋은 소식이 있어요. 다른 경비원이 제 근무를 대신해 주겠다고 해서 "
            "오늘 밤 가족과 함께 지낼 수 있게 됐어요! 혹시 모르니 스크롤도 가져가려고요. "
            "어머니가 도움을 주신 분께 꼭 이것을 전하라고 하셨어요. 오늘 아침에 갓 "
            "구우셨답니다!"
        ),
        "minecolonies.quests.general.apromisetokeep.obj4.answer0": (
            "가족분들께 안부 전해 주세요! 조심히 다녀오세요!"
        ),
        "minecolonies.quests.general.apromisetokeep.obj4.answer1": (
            "정말 친절하시네요! 냄새가 아주 좋다고 전해 주세요."
        ),
        "minecolonies.quests.general.apromisetokeep.obj4.answer1.reply": (
            "하하! 꼭 전할게요. 아주 기뻐하실 거예요. 그럼 가보세요. 그리고 다시 한번 "
            "진심으로 고마워요. 이곳 사람들이 서로를 보살핀다는 건 정말 뜻깊은 "
            "일이에요."
        ),
        "minecolonies.quests.general.apromisetokeep.obj4.answer1.reply.answer0": (
            "좋은 콜로니라면 그래야죠!"
        ),
        "minecolonies.quests.general.bumpinthenight": "한밤중의 수상한 소리",
        "minecolonies.quests.general.bumpinthenight.obj0": (
            "오! 들러 주셔서 정말 다행이에요. 밤마다 탑 근처에서 바스락거리고 쿵쿵대는 "
            "등 아주 불안한 소리가 들려요. 동물일 수도 있지만 더 나쁜 무언가일지도 "
            "모르죠. 만일에 대비해 아공간 경비원 강화 스크롤이 있으면 훨씬 안심될 것 "
            "같아요. 재료를 모으는 걸 도와주시겠어요?"
        ),
        "minecolonies.quests.general.bumpinthenight.obj0.answer0": (
            "물론이죠! 무엇이 필요한가요?"
        ),
        "minecolonies.quests.general.bumpinthenight.obj0.answer0.reply": (
            "좋아요, 고마워요! 순간이동 스크롤 한 장, 청금석 다섯 개, 엔더 진주 한 "
            "개와 종이 한 장이 필요해요. 마법부여 설비는 준비돼 있으니 원재료만 있으면 "
            "돼요. 가져다주시면 오늘 밤 바로 작업할게요."
        ),
        "minecolonies.quests.general.bumpinthenight.obj0.answer0.reply.answer0": (
            "맡겨 주세요. 바로 모아 올게요!"
        ),
        "minecolonies.quests.general.bumpinthenight.obj0.answer1": (
            "미안하지만 지금은 조금 바빠요."
        ),
        "minecolonies.quests.general.bumpinthenight.obj5": (
            "완벽해요! 필요한 게 모두 모였어요. 오늘 밤 스크롤을 만들면서 탑 주변의 "
            "소리도 제대로 들어볼게요. 내일 다시 들러 주세요. 무엇을 찾았는지 알려 "
            "드릴게요!"
        ),
        "minecolonies.quests.general.bumpinthenight.obj5.answer0": (
            "물론이죠! 내일 다시 올게요."
        ),
        "minecolonies.quests.general.bumpinthenight.obj6": (
            "오! 돌아오셨군요! 하하, 이 이야기를 들으면 믿지 못하실 거예요. 밤을 꼬박 "
            "새우며 창문마다 내다봤는데, 그 소리의 정체가 뭔지 아세요? 다람쥐였어요! "
            "다람쥐 가족이 밖의 장작더미에 둥지를 틀었더라고요. 전혀 위험하지 않았어요. "
            "솔직히 조금 바보가 된 기분이네요. 그래도 그 시간을 알차게 써서 스크롤을 "
            "한 장도 아니고 세 장이나 만들었어요! 여기, 남은 재료와 함께 가져가세요. "
            "겁먹은 마법부여사의 부탁을 들어주셔서 고마워요."
        ),
        "minecolonies.quests.general.bumpinthenight.obj6.answer0": (
            "하하! 더 위험한 것이 아니라 다행이네요. 조심하세요!"
        ),
        "minecolonies.quests.general.bumpinthenight.obj6.answer1": (
            "스크롤을 세 장이나요? 정말 대단하네요!"
        ),
        "minecolonies.quests.general.bumpinthenight.obj6.answer1.reply": (
            "그 불안한 기운으로 뭐라도 해야 했거든요! 게다가 언제 경비원이 필요해질지 "
            "모르잖아요. 이제 가보세요. 마법부여 작업이 더 필요하면 언제든 찾아오시고요."
        ),
        "minecolonies.quests.general.bumpinthenight.obj6.answer1.reply.answer0": (
            "그럴게요. 고마워요!"
        ),
        "minecolonies.quests.general.wheresthebuilder": "건축가는 어디에?",
        "minecolonies.quests.general.wheresthebuilder.obj0": (
            "어서 들어오세요! 여관 주인이 또 푸념하는 걸 우연히 들었어요. 건축가가 일을 "
            "하다가 사라졌고 여관 차양은 아직도 수리해야 한다는군요. 솔직히 두 분 다 "
            "안됐어요. 일꾼아 어디있니 스크롤을 만들면 건축가가 빛나게 해서 금방 찾을 수 "
            "있을 테니 도와볼까 해요! 재료를 모아 주실 수 있나요?"
        ),
        "minecolonies.quests.general.wheresthebuilder.obj0.answer0": (
            "기꺼이 도울게요! 무엇이 필요한가요?"
        ),
        "minecolonies.quests.general.wheresthebuilder.obj0.answer0.reply": (
            "좋아요! 순간이동 스크롤 세 장, 발광석 가루 여섯 개와 종이 두 장이 "
            "필요해요. 조금 번거롭지만 이 일을 완전히 해결할 수 있다면 그만한 가치가 "
            "있겠죠!"
        ),
        "minecolonies.quests.general.wheresthebuilder.obj0.answer0.reply.answer0": (
            "재료를 모아 올게요!"
        ),
        "minecolonies.quests.general.wheresthebuilder.obj0.answer1": (
            "두 분이 해결할 문제인 것 같으니 저는 빠질게요."
        ),
        "minecolonies.quests.general.wheresthebuilder.obj4": (
            "훌륭해요! 지금 스크롤을 만들고 있어요. 제대로 완성하려면 시간이 조금 "
            "걸리거든요. 준비되면 다시 들러 주세요. 그때는 완성해 둘게요!"
        ),
        "minecolonies.quests.general.wheresthebuilder.obj4.answer0": (
            "천천히 하세요. 곧 다시 들를게요!"
        ),
        "minecolonies.quests.general.wheresthebuilder.obj4.answer1": (
            "다시 왔어요. 스크롤은 완성됐나요?"
        ),
        "minecolonies.quests.general.wheresthebuilder.obj5": (
            "아, 마침 잘 오셨어요! 스크롤이 완성됐어요. 잠시만요... [스크롤을 들어 "
            "올리고 눈을 감는다] ...됐어요! 이제 건축가가 은은하게 빛날 텐데, 본인은 "
            "눈치채지 못할 거예요. 찾아가서 무엇을 하는지 확인해 보세요. 돌아올 때까지 "
            "여기서 기다릴게요!"
        ),
        "minecolonies.quests.general.wheresthebuilder.obj5.answer0": (
            "알겠어요! 찾아보고 돌아올게요."
        ),
        "minecolonies.quests.general.wheresthebuilder.obj6": (
            "오! 이런, 들켰네요. 제발, 제발 비밀로 해 주세요! 일하는 틈틈이 창고 "
            "지하실로 몰래 내려오고 있었어요. 콜로니 전체에서 누군가 잔소리하지 않는 "
            "곳에서 단 오 분이라도 쉴 수 있는 유일한 장소거든요. 여관 주인의 차양은 "
            "저도 알고 있어요. 잊지 않았다고 약속할게요. 잠시 숨을 돌릴 시간이 "
            "필요했을 뿐이에요. 이해하시죠? 마법부여사에게도 고맙다고 전해 주세요. "
            "정말 친절한 분이에요. 하지만 이건 우리끼리만 아는 걸로 해 주시겠어요?"
        ),
        "minecolonies.quests.general.wheresthebuilder.obj6.answer0": (
            "비밀은 지켜 드릴게요. 푹 쉬세요!"
        ),
        "minecolonies.quests.general.wheresthebuilder.obj6.answer1": (
            "충분히 이해해요. 아무 말도 하지 않을게요."
        ),
        "minecolonies.quests.general.wheresthebuilder.obj6.answer1.reply": (
            "정말 고마워요! 내일 아침 가장 먼저 차양을 고치겠다고 맹세할게요. 괜찮다면 "
            "낮잠 시간이 십 분 정도 남았으니 조금만 더 쉴게요. 진심으로 고마워요."
        ),
        "minecolonies.quests.general.wheresthebuilder.obj6.answer1.reply.answer0": (
            "좋은 꿈 꾸세요. 그럴 자격이 있어요!"
        ),
        "minecolonies.quests.general.wheresthebuilder.obj7": (
            "하하! 창고 지하실에 숨어 있었다고요! 그건... 솔직히 건축가를 탓할 수도 "
            "없겠네요. 이번 주에는 여관 주인이 정말 끈질겼거든요. 어쨌든 건축가를 "
            "찾았으니 차양도 언젠가는 고쳐지겠죠. 여기, 스크롤과 재료를 돌려드릴게요. "
            "오늘 모두의 마음의 평화를 지킨 셈이니 좋은 일을 하셨어요!"
        ),
        "minecolonies.quests.general.wheresthebuilder.obj7.answer0": (
            "누구나 한 번쯤 조용한 구석이 필요하죠."
        ),
        "minecolonies.quests.general.wheresthebuilder.obj7.answer1": (
            "여관 주인이 지하실을 찾지 못하길 바라죠."
        ),
        "minecolonies.quests.general.wheresthebuilder.obj7.answer1.reply": (
            "하하! 언젠가는 찾아내겠죠. 하지만 그건 나중에 걱정할 일이에요. 보상을 "
            "받으세요. 충분히 받을 만한 일을 하셨어요. 그리고 비밀을 지켜 주셔서 "
            "고마워요!"
        ),
        "minecolonies.quests.general.wheresthebuilder.obj7.answer1.reply.answer0": (
            "언제든지요. 고마워요!"
        ),
    }
)

WORKER_LEVEL_ROLES = {
    "com.minecolonies.coremod.info.builder.3": "건축가",
    "com.minecolonies.coremod.info.miner.4": "광부",
    "com.minecolonies.coremod.info.lumberjack.3": "나무꾼",
    "com.minecolonies.coremod.info.deliveryman.3": "배달부",
    "com.minecolonies.coremod.info.cook.2": "웨이터",
    "com.minecolonies.coremod.info.baker.3": "제빵사",
    "com.minecolonies.coremod.info.farmer.3": "농부",
    "com.minecolonies.coremod.info.fisherman.3": "낚시꾼",
    "com.minecolonies.coremod.info.chickenherder.3": "양계업자",
    "com.minecolonies.coremod.info.swineherder.3": "돼지치기",
    "com.minecolonies.coremod.info.shepherd.3": "양치기",
    "com.minecolonies.coremod.info.cowboy.3": "소몰이",
    "com.minecolonies.coremod.info.composter.3": "퇴비 작업자",
    "com.minecolonies.coremod.info.guardtower.3": "경비원",
    "com.minecolonies.coremod.info.barrackstower.3": "경비원",
}
KEY_EXACT.update(
    {
        key: (
            f"{role}도 일하면서 단계가 오릅니다.\n 단계가 높을수록 {role}의 작업 속도가 "
            "빨라집니다. 건물 단계와 지능 능력치가 높을수록 더 빨리 성장합니다. \n 하지만 "
            "일꾼의 단계는 거주지 단계로 제한됩니다. 생활 환경에 만족하지 못하면 더 나은 "
            "거주지를 제공할 때까지 성장이 멈춥니다."
        )
        for key, role in WORKER_LEVEL_ROLES.items()
    }
)

DOMUM_COLORS = {
    "black": "검은색",
    "blue": "파란색",
    "brown": "갈색",
    "cyan": "청록색",
    "gray": "회색",
    "green": "초록색",
    "light_blue": "하늘색",
    "light_gray": "밝은 회색",
    "lime": "연두색",
    "magenta": "자홍색",
    "orange": "주황색",
    "pink": "분홍색",
    "purple": "보라색",
    "red": "빨간색",
    "white": "흰색",
    "yellow": "노란색",
}
KEY_EXACT.update(
    {
        f"block.domum_ornamentum.{color}_floating_carpet": (
            f"떠다니는 {translated_color} 카펫"
        )
        for color, translated_color in DOMUM_COLORS.items()
    }
)
KEY_EXACT.update(
    {
        f"domum_ornamentum.extra.name.format.{color}": f"{translated_color} %s 장식"
        for color, translated_color in DOMUM_COLORS.items()
    }
)
KEY_EXACT.update(
    {
        "block.domum_ornamentum.blockbarreldeco_onside": "가로형 나무통",
        "block.domum_ornamentum.blockbarreldeco_standing": "세로형 나무통",
        "block.domum_ornamentum.beige_bricks": "베이지색 벽돌",
        "block.domum_ornamentum.beige_stone_bricks": "베이지색 석재 벽돌",
        "block.domum_ornamentum.brown_bricks": "갈색 벽돌",
        "block.domum_ornamentum.brown_stone_bricks": "갈색 석재 벽돌",
        "block.domum_ornamentum.cream_bricks": "크림색 벽돌",
        "block.domum_ornamentum.cream_stone_bricks": "크림색 석재 벽돌",
        "block.domum_ornamentum.roan_bricks": "적갈색 벽돌",
        "block.domum_ornamentum.roan_stone_bricks": "적갈색 석재 벽돌",
        "block.domum_ornamentum.sand_bricks": "모래색 벽돌",
        "block.domum_ornamentum.sand_stone_bricks": "모래색 석재 벽돌",
        "cuttergroup.domum_ornamentum.avanilla": "바닐라 블록",
        "cuttergroup.domum_ornamentum.btimberframe": "목재 틀",
        "cuttergroup.domum_ornamentum.cshingle": "지붕널",
        "cuttergroup.domum_ornamentum.ddoor": "문",
        "cuttergroup.domum_ornamentum.etrapdoor": "다락문",
        "cuttergroup.domum_ornamentum.fpanel": "패널",
        "cuttergroup.domum_ornamentum.gpillar": "기둥",
        "cuttergroup.domum_ornamentum.hpaperwall": "종이벽",
        "cuttergroup.domum_ornamentum.ilight": "조명",
        "cuttergroup.domum_ornamentum.jbrick": "벽돌",
        "cuttergroup.domum_ornamentum.kpost": "지주",
        "domum_ornamentum.allbrick.column.format": "주 재료: %s",
        "domum_ornamentum.blockpaperwall.center.format": "- 중심: %s",
        "domum_ornamentum.blockpaperwall.frame.format": "- 틀: %s",
        "domum_ornamentum.blockpaperwall.header": "재료:",
        "domum_ornamentum.blockpaperwall.name.format": "%s 틀 종이벽",
        "domum_ornamentum.blockpillar.name.format": "원형 %s 기둥",
        "domum_ornamentum.blocktiledpaperwall.center.format": "- 중심: %s",
        "domum_ornamentum.blocktiledpaperwall.frame.format": "- 틀: %s",
        "domum_ornamentum.blocktiledpaperwall.header": "재료:",
        "domum_ornamentum.blocktiledpaperwall.name.format": "%s 타일 종이벽",
        "domum_ornamentum.blockypillar.name.format": "각진 %s 기둥",
        "domum_ornamentum.dark_brick.name.format": "어두운 %s 벽돌",
        "domum_ornamentum.dark_brick_stair.name.format": "어두운 %s 벽돌 계단",
        "domum_ornamentum.desc.center": "중심: %s",
        "domum_ornamentum.desc.frame": "틀: %s",
        "domum_ornamentum.desc.main": "주 재료: %s",
        "domum_ornamentum.desc.material": "재료: %s",
        "domum_ornamentum.desc.shingle": "지붕널: %s",
        "domum_ornamentum.desc.support": "지지대: %s",
        "domum_ornamentum.door.block.format": "재료: %s",
        "domum_ornamentum.door.name.format": "%s 문",
        "domum_ornamentum.door.type.format": "변형: %s",
        "domum_ornamentum.door.type.name.full": "통짜형",
        "domum_ornamentum.door.type.name.port.manteau": "포트맨토형",
        "domum_ornamentum.door.type.name.vertically.striped": "세로 줄무늬형",
        "domum_ornamentum.door.type.name.waffle": "격자형",
        "domum_ornamentum.dynamic.frame.name.format": "가변형 %s 틀",
        "domum_ornamentum.extra.name.format": "%s 장식",
        "domum_ornamentum.fancydoor.center.block.format": "- 재료: %s",
        "domum_ornamentum.fancydoor.center.header": "중심:",
        "domum_ornamentum.fancydoor.frame.block.format": "- 재료: %s",
        "domum_ornamentum.fancydoor.frame.header": "틀:",
        "domum_ornamentum.fancydoor.name.format": "화려한 %s 문",
        "domum_ornamentum.fancydoor.type.format": "변형: %s",
        "domum_ornamentum.fancydoor.type.name.creeper": "크리퍼형",
        "domum_ornamentum.fancydoor.type.name.full": "통짜형",
        "domum_ornamentum.fancytrapdoor.center.block.format": "- 재료: %s",
        "domum_ornamentum.fancytrapdoor.center.header": "중심:",
        "domum_ornamentum.fancytrapdoor.frame.block.format": "- 재료: %s",
        "domum_ornamentum.fancytrapdoor.frame.header": "틀:",
        "domum_ornamentum.fancytrapdoor.name.format": "화려한 %s 다락문",
        "domum_ornamentum.fancytrapdoor.type.format": "변형: %s",
        "domum_ornamentum.fancytrapdoor.type.name.creeper": "크리퍼형",
        "domum_ornamentum.fancytrapdoor.type.name.full": "통짜형",
        "domum_ornamentum.fence-gate.name.format": "%s 울타리 문",
        "domum_ornamentum.fence.name.format": "%s 울타리",
        "domum_ornamentum.group": "그룹:",
        "domum_ornamentum.light.center.block.format": "- 재료: %s",
        "domum_ornamentum.light.center.header": "중심:",
        "domum_ornamentum.light.frame.block.format": "- 재료: %s",
        "domum_ornamentum.light.frame.header": "틀:",
        "domum_ornamentum.light.frame.name.format": "%s 조명",
        "domum_ornamentum.light.frame.type.center_light": "중심형",
        "domum_ornamentum.light.frame.type.crossed_light": "교차형",
        "domum_ornamentum.light.frame.type.fancy_light": "화려한 형식",
        "domum_ornamentum.light.frame.type.format": "- 유형: %s",
        "domum_ornamentum.light.frame.type.four_light": "네 갈래형",
        "domum_ornamentum.light.frame.type.framed_light": "틀형",
        "domum_ornamentum.light.frame.type.horizontal_light": "가로형",
        "domum_ornamentum.light.frame.type.vertical_light": "세로형",
        "domum_ornamentum.light_brick.name.format": "밝은 %s 벽돌",
        "domum_ornamentum.light_brick_stair.name.format": "밝은 %s 벽돌 계단",
        "domum_ornamentum.panel.block.format": "재료: %s",
        "domum_ornamentum.panel.name.format": "%s 패널",
        "domum_ornamentum.panel.type.format": "변형: %s",
        "domum_ornamentum.pillar.column.format": "주 재료: %s",
        "domum_ornamentum.pillar.header": "유형:",
        "domum_ornamentum.post.block.format": "재료: %s",
        "domum_ornamentum.post.name.format": "%s 지주",
        "domum_ornamentum.post.type.format": "변형: %s",
        "domum_ornamentum.post.type.name.double": "이중형",
        "domum_ornamentum.post.type.name.heavy": "중량형",
        "domum_ornamentum.post.type.name.pinched": "오목형",
        "domum_ornamentum.post.type.name.plain": "기본형",
        "domum_ornamentum.post.type.name.quad": "사중형",
        "domum_ornamentum.post.type.name.turned": "선반 가공형",
        "domum_ornamentum.shingle.main.format": "주 재료: %s",
        "domum_ornamentum.shingle.name.format.block.domum_ornamentum.shingle": (
            "%s 지붕널"
        ),
        "domum_ornamentum.shingle.name.format.block.domum_ornamentum.shingle_flat": (
            "%s 완만한 지붕널"
        ),
        "domum_ornamentum.shingle.name.format.block.domum_ornamentum.shingle_flat_lower": (
            "%s 완만한 하부 지붕널"
        ),
        "domum_ornamentum.shingle.name.format.block.domum_ornamentum.shingle_steep": (
            "%s 가파른 지붕널"
        ),
        "domum_ornamentum.shingle.name.format.block.domum_ornamentum.shingle_steep_lower": (
            "%s 가파른 하부 지붕널"
        ),
        "domum_ornamentum.shingle.support.format": "지지대: %s",
        "domum_ornamentum.shingle_slab.cover.format": "덮개: %s",
        "domum_ornamentum.shingle_slab.main.format": "주 재료: %s",
        "domum_ornamentum.shingle_slab.name.format": "%s 지붕널 반 블록",
        "domum_ornamentum.shingle_slab.support.format": "지지대: %s",
        "domum_ornamentum.slab.name.format": "%s 반 블록",
        "domum_ornamentum.squarepillar.name.format": "사각 %s 기둥",
        "domum_ornamentum.stair.name.format": "%s 계단",
        "domum_ornamentum.timber.center.block.format": "- 재료: %s",
        "domum_ornamentum.timber.center.header": "중심:",
        "domum_ornamentum.timber.frame.block.format": "- 재료: %s",
        "domum_ornamentum.timber.frame.header": "틀:",
        "domum_ornamentum.timber.frame.name.format": "%s 목재 틀",
        "domum_ornamentum.timber.frame.type.double_crossed": "이중 교차형",
        "domum_ornamentum.timber.frame.type.down_gated": "하부 문양형",
        "domum_ornamentum.timber.frame.type.format": "- 유형: %s",
        "domum_ornamentum.timber.frame.type.framed": "틀형",
        "domum_ornamentum.timber.frame.type.horizontal_plain": "가로 기본형",
        "domum_ornamentum.timber.frame.type.one_crossed_lr": "좌우 교차형",
        "domum_ornamentum.timber.frame.type.one_crossed_rl": "우좌 교차형",
        "domum_ornamentum.timber.frame.type.plain": "기본형",
        "domum_ornamentum.timber.frame.type.side_framed": "측면 틀형",
        "domum_ornamentum.timber.frame.type.side_framed_horizontal": "가로 측면 틀형",
        "domum_ornamentum.timber.frame.type.up_gated": "상부 문양형",
        "domum_ornamentum.trapdoor.block.format": "재료: %s",
        "domum_ornamentum.trapdoor.name.format": "%s 다락문",
        "domum_ornamentum.trapdoor.type.format": "변형: %s",
        "domum_ornamentum.variant": "변형:",
        "domum_ornamentum.wall.name.format": "%s 담장",
        "itemGroup.domum_ornamentum.doors": "DO - 문",
        "itemGroup.domum_ornamentum.extra-blocks": "DO - 장식 블록",
        "itemGroup.domum_ornamentum.fences": "DO - 울타리",
        "itemGroup.domum_ornamentum.floating-carpets": "DO - 떠다니는 카펫",
        "itemGroup.domum_ornamentum.general": "Domum Ornamentum",
        "itemGroup.domum_ornamentum.paperwalls": "DO - 종이벽",
        "itemGroup.domum_ornamentum.posts": "DO - 지주",
        "itemGroup.domum_ornamentum.shingle_slabs": "DO - 지붕널 반 블록",
        "itemGroup.domum_ornamentum.shingles": "DO - 지붕널",
        "itemGroup.domum_ornamentum.slabs": "DO - 반 블록",
        "itemGroup.domum_ornamentum.stairs": "DO - 계단",
        "itemGroup.domum_ornamentum.timber_frames": "DO - 목재 틀",
        "itemGroup.domum_ornamentum.walls": "DO - 담장",
    }
)

DOMUM_PANEL_VARIANTS = {
    "boss": "돌출형",
    "coffer": "격자형",
    "full": "통짜형",
    "horizontal.bars": "가로 막대형",
    "horizontally.squiggly.striped": "가로 물결무늬형",
    "horizontally.striped": "가로 줄무늬형",
    "moulding": "몰딩형",
    "port.manteau": "포트맨토형",
    "porthole": "현창형",
    "roundel": "원형 장식형",
    "slot": "슬롯형",
    "vertical.bars": "세로 막대형",
    "vertically.squiggly.striped": "세로 물결무늬형",
    "vertically.striped": "세로 줄무늬형",
    "waffle": "격자무늬형",
}
for prefix in ("panel", "trapdoor"):
    KEY_EXACT.update(
        {
            f"domum_ornamentum.{prefix}.type.name.{variant}": translated_variant
            for variant, translated_variant in DOMUM_PANEL_VARIANTS.items()
        }
    )

KEY_EXACT.update(
    {
        "com.ldtteam.structurize.gui.scantool.from": "시작",
        "com.ldtteam.structurize.gui.scantool.remove": "제거",
        "com.ldtteam.structurize.gui.scantool.replace": "교체",
        "com.ldtteam.structurize.gui.scantool.select": "선택",
        "com.ldtteam.structurize.gui.scantool.to": "끝",
        "com.ldtteam.structurize.gui.scantool.copy.notscan": (
            "스캔 명령만 복사할 수 있습니다. 활성 스캔을 붙여넣으려면 웅크린 채 클릭하세요."
        ),
        "com.ldtteam.structurize.gui.scantool.paste.badcommand": (
            "명령 블록에 스캔 명령이 아닌 내용이 있습니다. 붙여넣기 전에 먼저 지우세요."
        ),
        "com.ldtteam.structurize.gui.scantool.teleport.dimension": (
            "건축물과 같은 차원에 있어야 합니다."
        ),
        "com.ldtteam.structurize.gui.scantool.fillplacerholder.ystretch": (
            "Y축 늘이기"
        ),
        "com.ldtteam.structurize.gui.scantool.fillplacerholder.blockdist": (
            "블록 거리"
        ),
        "com.ldtteam.structurize.gui.scantool.fillplacerholder.apply": "적용",
        "com.ldtteam.structurize.gui.shapetool.hollow": "속이 빈",
        "com.ldtteam.structurize.gui.shapetool.solid": "속이 찬",
        "com.ldtteam.structurize.gui.selectres.count": "수량",
        "com.ldtteam.structurize.network.messages.schematicsavemassage.toobig": (
            "설계도 크기가 너무 큽니다. %s바이트를 넘을 수 없습니다!"
        ),
        "com.structurize.command.paste.no.perm": (
            "명령어로 붙여넣을 권한이 없습니다. 대신 건축 도구를 사용하세요!"
        ),
        "com.structurize.gui.buildtool.leave.tip": (
            "건축 도구로 단단한 블록을 우클릭하여 건축 위치를 조정하세요."
        ),
        "key.structurize.move_forward": "앞으로 이동",
        "key.structurize.mirror": "대칭 이동",
        "key.structurize.place": "구조물 배치",
        "item.caliper.message.1d": "%s블록 길이입니다.",
        "item.caliper.message.2d": "%s×%s블록 크기입니다.",
        "item.caliper.message.3d": "%s×%s×%s블록 크기입니다.",
        "item.sceptersteel.badanchorpos": (
            "스캔 도구의 앵커 위치가 스캔 영역 밖에 있습니다! Shift+우클릭하여 옮기세요!"
        ),
        "item.sceptersteel.point": "첫 번째 지점 저장: %d %d %d",
        "structurize.config.renderer": "설계도 미리보기 렌더러",
        "structurize.config.maxBlocksChecked": "최대 확인 블록 수",
        "structurize.config.maxBlocksChecked.comment": (
            "일꾼이 확인할 수 있는 최대 블록 수입니다."
        ),
        "structurize.config.maxCachedChanges": "최대 변경 기록 수",
        "structurize.config.maxCachedChanges.comment": (
            "저장할 최대 실행 취소 기록 수입니다. 값이 높을수록 메모리를 더 사용합니다."
        ),
        "structurize.config.schematicBlockLimit": "설계도 블록 제한",
        "structurize.config.schematicBlockLimit.comment": (
            "스캔 설계도 하나에 포함할 수 있는 최대 블록 수입니다."
        ),
        "structurize.config.scan_tool_scrolling": "스캔 도구 스크롤 전환",
        "structurize.config.teleportAllowed": "순간이동 허용",
        "structurize.config.teleportAllowed.comment": (
            "크리에이티브 모드 플레이어가 스캔 도구로 건축물 사이를 순간이동할 수 있는지 "
            "설정합니다."
        ),
        "structurize.config.teleportBuildDirection": "건축물 방향",
        "structurize.config.teleportBuildDirection.comment": (
            "건축물로 순간이동할 때 도착할 방향입니다."
        ),
        "structurize.config.teleportBuildDistance": "건축물 거리",
        "structurize.config.teleportBuildDistance.comment": (
            "건축물로 순간이동할 때 떨어져 도착할 거리입니다."
        ),
        "structurize.config.light_level.comment": (
            "-1은 바닐라 세계의 현재 밝기를 사용하며, 고정 밝기는 0~15(최소~최대)입니다."
        ),
        "structurize.config.transparency": "미리보기 투명도",
        "structurize.config.transparency.comment": (
            "0(투명)부터 1(불투명)까지 설정합니다. 알파 기능의 알려진 문제는 수정되지 않을 "
            "수 있으며, 음수는 기능을 끕니다."
        ),
        "structurize.gui.undoredo": "실행 취소/다시 실행 창 열기",
        "structurize.gui.undoredo.undo.add": "%s을(를) 실행 취소 대기열에 추가",
        "structurize.gui.undoredo.redo.add": "%s을(를) 다시 실행 대기열에 추가",
        "structurize.gui.undoredo.redoop": "다시 실행",
        "structurize.gui.undoredo.undoop": "실행 취소",
        "structurize.gui.buildtool.switchpack": "팩 전환",
        "structurize.gui.switchpack.select": "선택",
        "structurize.gui.missing.pos": (
            "먼저 도구로 단단한 블록을 클릭하여 시작 위치를 선택하세요."
        ),
        "com.ldtteam.structurize.remove_block": "%s 블록 제거",
        "com.ldtteam.structurize.remove_blocks": "필터링한 블록 제거",
        "com.ldtteam.structurize.place_structure": "%s 구조물 배치",
        "com.ldtteam.structurize.iterators.random": "무작위",
        "com.ldtteam.structurize.gui.switchpack.list.empty": (
            "구조물 팩을 찾을 수 없습니다. 팩을 설치하세요."
        ),
        "com.ldtteam.structurize.gui.switchpack.pack_disabled.hover_text": (
            "이 팩은 클라이언트에만 있어 비활성화되었습니다. 사용하려면 서버에서 설정 옵션 "
            "'%s'을(를) 활성화해야 합니다."
        ),
        "structurize.gui.replaceblock.badpct": (
            "잘못된 비율이 선택되어 100으로 간주합니다."
        ),
        "com.ldtteam.structurize.gui.scantool.teleport.nocmd": (
            "순간이동 위치를 설정하려면 명령 블록을 한 번 이상 복사하거나 붙여넣어야 합니다."
        ),
        "com.ldtteam.structurize.gui.scantool.teleport.noscan": (
            "순간이동 위치를 설정하려면 현재 슬롯에 스캔 영역을 지정해야 합니다."
        ),
        "key.structurize.teleport": "스캔 도구 순간이동",
        "item.sceptersteel.toobig": "설계도가 너무 큽니다. 최대 부피는 %d블록입니다.",
        "item.structurize.sceptergold": "건축 도구",
        "structurize.config.teleport.comment": "스캔 도구 순간이동 관련 설정",
        "structurize.config.gameplay.comment": "핵심 게임플레이 관련 설정",
        "structurize.config.scan_tool_scrolling.comment": (
            "웅크린 채 마우스 휠을 돌려 스캔 도구 슬롯을 전환합니다."
        ),
        "structurize.config.render_placeholders_nice": (
            "자리표시자를 대응 블록처럼 렌더링"
        ),
        "structurize.gui.buildtool.complete": "즉시 붙여넣기",
        "structurize.gui.buildtool.pretty": "자연스럽게 배치",
        "structurize.gui.buildtool.specialized": "특수 배치",
        "com.ldtteam.structurize.gui.structure.edit.title": "구조물 경로:",
        "com.ldtteam.structurize.gui.tagtool.notag": (
            "블록에 적용할 유효한 태그를 먼저 입력하세요!"
        ),
        "com.ldtteam.structurize.gui.tagtool.discard.success": (
            "태그를 저장된 상태로 되돌렸습니다."
        ),
    }
)

REPLACEMENTS = (
    ("%s (이) 가", "%s이(가)"),
    ("%s (이)가", "%s이(가)"),
    ("Minecolonies", "MineColonies"),
    ("Structurize하다", "Structurize"),
    ("Struturize", "Structurize"),
    ("Architects Cutter", "건축가의 절단기"),
    ("Build Tool", "건축 도구"),
    ("Buildtool", "건축 도구"),
    ("Gatehouse", "관문"),
    ("Colony Sign", "콜로니 표지판"),
    ("최신.log", "latest.log"),
    ("회로도", "설계도"),
    ("청사진", "설계도"),
    ("식민지", "콜로니"),
    ("건축업자", "건축가"),
    ("경비병", "경비원"),
    ("병영 탑", "군사 기지 탑"),
    ("병영", "군사 기지"),
    ("산림 관리인", "나무꾼"),
    ("신비한 제단", "신비로운 제단"),
    ("보관함를", "보관함을"),
    ("눈치 채 셨", "눈치채셨"),
    ("자급 자족", "자급자족"),
    ("가동해보져", "가동해 보죠"),
    ("될겁니다", "될 것입니다"),
    ("할거에요", "할 거예요"),
    ("좋을거같아요", "좋을 것 같아요"),
    ("매번하던대로", "매번 하던 대로"),
    ("하시면됩니다", "하시면 됩니다"),
    ("건설 할", "건설할"),
    ("요청 하기도", "요청하기도"),
    ("마인콜로니즈", "MineColonies"),
    ("마인콜로니", "MineColonies"),
    ("마인 콜로니", "MineColonies"),
    ("도뭄 오르나멘툼", "Domum Ornamentum"),
    ("도문 오르나멘툼", "Domum Ornamentum"),
    ("구조화", "Structurize"),
    ("오른쪽 클릭", "우클릭"),
    ("왼쪽 클릭", "좌클릭"),
    ("마우스 오른쪽 버튼을 클릭", "우클릭"),
    ("마우스 왼쪽 버튼을 클릭", "좌클릭"),
    ("툴팁", "도움말"),
    ("플레이스홀더", "자리표시자"),
    ("자리 표시자", "자리표시자"),
    ("타운 홀", "마을회관"),
    ("타운홀", "마을회관"),
    ("빌더", "건축가"),
    ("포레스터", "나무꾼"),
    ("크래프터", "제작자"),
    ("워커", "일꾼"),
    ("시티즌", "주민"),
    ("시민", "주민"),
    ("콜로니스트", "주민"),
    ("인벤토리", "보관함"),
    ("쿨다운", "재사용 대기시간"),
    ("레벨", "단계"),
    ("갯수", "개수"),
    ("해야합니다", "해야 합니다"),
    ("할수", "할 수"),
    ("되지않", "되지 않"),
    ("설계도을", "설계도를"),
    ("보관함가", "보관함이"),
    ("보관함를", "보관함을"),
    ("군사기지", "군사 기지"),
    ("레시피", "제작법"),
    ("블럭", "블록"),
    ("lvl ", "단계 "),
    ("단계 당", "단계당"),
    ("할려면", "하려면"),
    ("할 수록", "할수록"),
    ("할때", "할 때"),
    ("우클릭 하", "우클릭하"),
    ("해주시고", "해 주시고"),
    ("해주면", "해 주면"),
    ("안될거같아요", "안 될 것 같아요"),
    ("될거야", "될 거야"),
    ("될거에요", "될 거예요"),
    ("shift+", "Shift+"),
    ("설계도이", "설계도가"),
    ("설계도은", "설계도는"),
    ("군사 기지은", "군사 기지는"),
    ("군사 기지이", "군사 기지가"),
    ("군사 기지을", "군사 기지를"),
    ("단계은", "단계는"),
    ("단계을", "단계를"),
    ("단계이나", "단계나"),
    ("단계과", "단계와"),
    ("거주지을", "거주지를"),
    ("경비탑를", "경비탑을"),
    ("경비 탑", "경비탑"),
    ("스폰와", "스폰과"),
    ("물품를", "물품을"),
    ("나갈때", "나갈 때"),
    ("들어갈때", "들어갈 때"),
    ("업그레이드해주세요", "업그레이드해 주세요"),
    ("단계이 오릅니다", "단계가 오릅니다"),
    ("단계이 높을수록", "단계가 높을수록"),
    ("단계이 없습니다", "단계가 없습니다"),
    ("단계이 너무", "단계가 너무"),
    ("단계이 최소", "단계가 최소"),
    ("단계이 올라", "단계가 올라"),
    ("단계이 더", "단계가 더"),
    ("단계이 오르", "단계가 오르"),
    ("단계이어야", "단계여야"),
    ("단계이여야", "단계여야"),
    ("안될 거", "안 될 것"),
    ("업그레이드 할", "업그레이드할"),
    ("수 있게돼", "수 있게 돼"),
    ("이였", "이었"),
    ("찾고있", "찾고 있"),
    ("있을거", "있을 거"),
    ("먹을거", "먹을 거"),
    ("쉬울거", "쉬울 거"),
    ("않을거", "않을 거"),
    ("해볼거", "해 볼 거"),
    ("거에요", "거예요"),
    ("친구에요", "친구예요"),
    ("내어주세요", "내어 주세요"),
    ("전달해줘서", "전달해 줘서"),
    (") 이", ")이"),
    (".,", ","),
    ("해보", "해 보"),
)

QUEST_EXACT = {
    "quest.3CD307DDD6A5F5A3.quest_subtitle": "&f4 &c공격력",
    "quest.44BD0B40EB5451AF.quest_desc": [
        (
            "보급 캠프와 보급선은 &lMineColonies&r에서 추가하는 아이템입니다. "
            "거주할 기지와 콜로니를 즉시 시작할 수 있게 해 줍니다! "
            "\\n\\n우클릭해 메뉴를 열고 원하는 캠프나 선박 유형을 선택하세요. "
            "\\n\\n그다음 설치할 장소를 찾으세요. 땅은 평평해야 하며, 빨간 "
            "윤곽선으로 표시된 블록은 치워야 합니다. \\n\\n배치를 확정하면 새 캠프나 "
            "선박이 자원 소모 없이 완성됩니다! \\n\\n마을회관, 침대, 보급품 등 "
            "정착에 필요한 여러 물품이 들어 있습니다."
        )
    ],
    "quest.4AE8D8826F894EC7.quest_desc": [
        (
            "&l&5Domum Ornamentum&r은 &l&6Framed Blocks&r와 &l&bChipped&r를 "
            "합친 것과 비슷한 모드입니다! \\n\\n건축가의 절단기로 다양한 모양과 "
            "변형 블록을 만들 수 있습니다. \\n\\n먼저 문, 조명 같은 블록 그룹을 "
            "고른 뒤 변형을 선택하세요. \\n그다음 완성품에 사용할 재료 블록을 "
            "넣으세요. 어떤 블록은 서로 다른 재료 2개가 필요하고, 어떤 블록은 "
            "1개만 필요합니다."
        )
    ],
    "quest.4AE8D8826F894EC7.title": "&l&5Domum Ornamentum&r",
}

QUEST_EXACT.update(
    {
        "quest.4AE8D8826F894EC7.quest_desc": [
            (
                "&l&5Domum Ornamentum&r은 &l&6Framed Blocks&r와 &l&bChipped&r를 "
                "합친 것과 비슷한 모드입니다! \\n\\n건축가의 절단기로 다양한 모양과 변형 "
                "블록을 만들 수 있습니다. \\n\\n먼저 문, 조명 같은 블록 그룹을 고르세요. "
                "\\n그다음 변형을 선택하세요. \\n마지막으로 완성품에 사용할 재료 블록을 "
                "넣으세요. 어떤 블록은 서로 다른 재료 두 개가 필요하고, 어떤 블록은 한 개만 "
                "필요합니다."
            )
        ]
    }
)


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value for text in strings(item)]
    if isinstance(value, dict):
        return [text for item in value.values() for text in strings(item)]
    return []


def translated(value: object, cache: dict[str, str]) -> object:
    if isinstance(value, str):
        return cache.get(value, value)
    if isinstance(value, list):
        return [translated(item, cache) for item in value]
    if isinstance(value, dict):
        return {key: translated(item, cache) for key, item in value.items()}
    return value


def candidates() -> dict[str, object]:
    cache_value = load(CACHE) if CACHE.is_file() else {}
    cache = {str(key): str(value) for key, value in cache_value.items()}
    roots = [ROOT / namespace for namespace in LANGUAGES] + [ROOT / "quests/related"]
    requests = set()
    for root in roots:
        english = load(root / "en_us.json")
        sources = load(root / "candidate_sources.json")
        for key, value in english.items():
            if sources.get(key) in {"bundled_ko_kr", "project_output_review"}:
                continue
            requests.update(text for text in strings(value) if LATIN.search(text))
    pending = sorted(source for source in requests if source not in cache)
    failures = []
    if pending:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(
                    candidate_helper.request_translation_candidate, source
                ): source
                for source in pending
            }
            for number, future in enumerate(as_completed(futures), 1):
                source = futures[future]
                try:
                    cache[source] = future.result()
                except (
                    Exception
                ) as exc:  # pragma: no cover - 외부 후보 서비스 오류 보고용
                    failures.append(f"{source}: {exc}")
                    cache[source] = source
                if number % 25 == 0:
                    write(CACHE, cache)
        write(CACHE, cache)
    outputs = []
    for root in roots:
        english = load(root / "en_us.json")
        existing = load(root / "ko_kr.json")
        sources = load(root / "candidate_sources.json")
        output = {}
        for key, value in english.items():
            if sources.get(key) in {"bundled_ko_kr", "project_output_review"}:
                output[key] = existing[key]
            else:
                output[key] = translated(value, cache)
        write(root / "auto_candidates.json", output)
        outputs.append({"scope": root.name, "keys": len(output)})
    result = {
        "unique_requests": len(requests),
        "new_requests": len(pending),
        "failures": failures,
        "outputs": outputs,
        "status": "candidate_requires_full_review",
    }
    write(ROOT / "auto_candidate_report.json", result)
    return result


def bundled_minecolonies() -> dict[str, object]:
    instance = resolve_source_root()
    jar = family_goal.find_jar(instance, "minecolonies-")
    with ZipFile(jar) as archive:
        value = json.loads(
            archive.read("assets/minecolonies/lang/ko_kr.json").decode("utf-8")
        )
    if not isinstance(value, dict):
        raise TypeError(jar)
    write(ROOT / "minecolonies/bundled_candidates.json", value)
    return value


def review(key: str, source: object, candidate: object) -> object:
    if not isinstance(source, str) or not isinstance(candidate, str):
        return candidate
    value = KEY_EXACT.get(key, candidate)
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    return value


def normalize() -> dict[str, object]:
    bundled = bundled_minecolonies()
    rows = []
    for namespace in LANGUAGES:
        root = ROOT / namespace
        english = load(root / "en_us.json")
        auto = load(root / "auto_candidates.json")
        korean = {}
        for key, source in english.items():
            candidate = bundled.get(key) if namespace == "minecolonies" else None
            if (
                candidate is None
                or candidate == source
                or family_goal.validate_value(key, source, candidate)
            ):
                candidate = auto.get(key, source)
            korean[key] = review(key, source, candidate)
        write(root / "ko_kr.json", korean)
        rows.append({"namespace": namespace, "keys": len(korean)})
    related = ROOT / "quests/related"
    english = load(related / "en_us.json")
    auto = load(related / "auto_candidates.json")
    korean = {
        key: QUEST_EXACT.get(key, review(key, source, auto[key]))
        for key, source in english.items()
    }
    write(related / "ko_kr.json", korean)
    result = {
        "languages": rows,
        "bundled_candidates_reviewed": len(bundled),
        "related_quest_keys": len(korean),
        "status": "complete",
    }
    write(ROOT / "normalization.json", result)
    return result


def verify_scope(root: Path) -> tuple[dict[str, object], list[str]]:
    english, korean = load(root / "en_us.json"), load(root / "ko_kr.json")
    errors = []
    if list(english) != list(korean):
        errors.append(f"키 또는 순서 불일치: {root.name}")
    for key in english.keys() & korean.keys():
        source, target = english[key], korean[key]
        errors.extend(family_goal.validate_value(key, source, target))
        for left, right in zip(strings(source), strings(target), strict=True):
            if Counter(NUMBER.findall(left)) != Counter(NUMBER.findall(right)):
                errors.append(f"숫자 불일치: {root.name}:{key}")
    return {"scope": root.name, "keys": len(english)}, errors


def verify() -> tuple[dict[str, object], list[str]]:
    rows, errors = [], []
    for root in [ROOT / namespace for namespace in LANGUAGES] + [
        ROOT / "quests/related"
    ]:
        row, current = verify_scope(root)
        rows.append(row)
        errors.extend(current)
    result = {
        "scopes": rows,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write(ROOT / "specialized_validation.json", result)
    return result, errors


def audit() -> tuple[dict[str, object], list[str]]:
    instance = resolve_source_root()
    rows = []
    guide_surfaces = []
    style_packs = []
    towntalk_surface = {}
    for target in family_goal.targets_for(FAMILY):
        jar = family_goal.find_jar(instance, target.jar_prefix)
        with ZipFile(jar) as archive:
            names = archive.namelist()
            rows.append(
                {
                    "jar": jar.name,
                    "language_target": target.language_target,
                    "advancements": sum(
                        name.endswith(".json") and "/advancement" in name
                        for name in names
                    ),
                    "recipes": sum(
                        name.endswith(".json") and "/recipe" in name for name in names
                    ),
                }
            )
            if target.namespace == "minecolonies":
                for name in names:
                    if not (
                        name.startswith("data/minecolonies/colony/quests/guides/")
                        and name.endswith(".json")
                    ):
                        continue
                    payload = json.loads(archive.read(name).decode("utf-8"))
                    references = []
                    literals = []

                    def inspect_display_fields(value: object) -> None:
                        if isinstance(value, dict):
                            for key, item in value.items():
                                if key in {"name", "text", "answer"} and isinstance(
                                    item, str
                                ):
                                    if family_goal.TRANSLATION_KEY.fullmatch(item):
                                        references.append(item)
                                    else:
                                        literals.append(item)
                                inspect_display_fields(item)
                        elif isinstance(value, list):
                            for item in value:
                                inspect_display_fields(item)

                    inspect_display_fields(payload)
                    guide_surfaces.append(
                        {
                            "file": name,
                            "language_key_references": len(set(references)),
                            "literal_display_text": sorted(set(literals)),
                        }
                    )
            elif target.namespace == "stylecolonies":
                for name in names:
                    if not name.endswith("/pack.json"):
                        continue
                    payload = json.loads(archive.read(name).decode("utf-8-sig"))
                    style_packs.append(
                        {
                            "file": name,
                            "name": payload.get("name"),
                            "description": payload.get("desc"),
                            "classification": "공식 구조물 팩 메타데이터",
                        }
                    )
            elif target.namespace == "towntalk":
                pack_meta = json.loads(
                    archive.read("respack/pack.mcmeta").decode("utf-8")
                )
                towntalk_surface = {
                    "language_files": [
                        name
                        for name in names
                        if "/lang/" in name and name.endswith(".json")
                    ],
                    "embedded_pack_description": pack_meta.get("pack", {}).get(
                        "description"
                    ),
                    "sound_registry_only": "respack/assets/minecolonies/sounds.json"
                    in names,
                }
    visible_lines = []
    markers = tuple(f"{namespace}:" for namespace in LANGUAGES)
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json", ".snbt"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            lowered = line.lower()
            if any(marker in lowered for marker in markers) and any(
                token in lowered
                for token in ("display", "tooltip", "lore", "text", ".name(")
            ):
                visible_lines.append(
                    f"{path.relative_to(instance).as_posix()}:{number}:{line.strip()}"
                )
    result = {
        "jars": rows,
        "minecolonies_guide_surfaces": guide_surfaces,
        "stylecolonies_audit_only_packs": style_packs,
        "towntalk_audit_only_surface": towntalk_surface,
        "kubejs_direct_display_lines": visible_lines,
        "status": "complete",
    }
    write(ROOT / "surface_audit.json", result)
    return result, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("candidates", "normalize", "verify", "audit")
    )
    args = parser.parse_args()
    if args.command == "candidates":
        report, errors = candidates(), []
    elif args.command == "normalize":
        report, errors = normalize(), []
    elif args.command == "verify":
        report, errors = verify()
    else:
        report, errors = audit()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
