#!/usr/bin/env python3
"""Railcraft Reborn 언어 파일을 현재 영어 원문 기준으로 번역하고 전수 검증한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path

import actually_additions_family as candidate_helper
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root


FAMILY = "railcraft_reborn"
NAMESPACE = "railcraft"
WORK_ROOT = PROJECT_ROOT / "working/railcraft_reborn"
LANG_ROOT = WORK_ROOT / NAMESPACE
CACHE_FILE = PROJECT_ROOT / "temp/railcraft_reborn_language_candidate_cache.json"
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"

# UI와 아이템 검색에서 동일한 개념이 흔들리지 않도록 Railcraft 용어를 고정한다.
TERM_REPLACEMENTS = (
    ("RailCraft", "Railcraft"),
    ("레일크래프트", "Railcraft"),
    ("Railcraft Inc.의", "Railcraft의"),
    ("광산 수레", "광산 수레"),
    ("마인카트", "광산 수레"),
    ("카트", "광산 수레"),
    ("기관차", "기관차"),
    ("트랙 키트", "선로 키트"),
    ("궤도 키트", "선로 키트"),
    ("트랙", "선로"),
    ("레일", "선로"),
    ("롤링 머신", "압연기"),
    ("롤링 기계", "압연기"),
    ("코크스 오븐", "코크스로"),
    ("코크 오븐", "코크스로"),
    ("블라스트 퍼니스", "용광로"),
    ("크레오소트", "크레오소트유"),
    ("크로우바", "쇠지렛대"),
    ("터널 보어", "터널 굴착기"),
    ("보어 헤드", "굴착기 헤드"),
    ("아이템 로더", "아이템 적재기"),
    ("아이템 언로더", "아이템 하역기"),
    ("액체 로더", "유체 적재기"),
    ("액체 언로더", "유체 하역기"),
    ("유체 로더", "유체 적재기"),
    ("유체 언로더", "유체 하역기"),
    ("액체", "유체"),
    ("파이어박스", "화실"),
    ("스팀", "증기"),
    ("Steam", "증기"),
    ("Firebox", "화실"),
    ("Token Signal", "토큰 신호기"),
    ("Distant Signal", "원거리 신호기"),
    ("Block Signal", "구간 신호기"),
    ("부스터", "가속"),
    ("디텍터", "감지"),
    ("커플링", "연결"),
    ("디커플링", "연결 해제"),
    ("수신기", "수신기"),
    ("컨트롤러", "제어기"),
    ("레시피", "조합법"),
    ("엔터티", "엔티티"),
    ("품목", "아이템"),
    ("디스펜서", "발사기"),
    ("피드 스테이션", "사료 공급기"),
    ("휘슬", "기적"),
    ("멀티 블록", "멀티블록"),
    ("선로을", "선로를"),
    ("선로으로", "선로로"),
    ("원색", "주 색상"),
    ("현재 시즌", "현재 계절"),
    ("복장을 갖춘 선로", "장착형 선로"),
    ("골든티켓", "황금 승차권"),
    ("골든 티켓", "황금 승차권"),
    ("티켓", "승차권"),
    ("월드스파이크", "월드 스파이크"),
)

SOURCE_OVERRIDES = {
    "Railcraft": "Railcraft",
    "Railcraft Reborn": "Railcraft Reborn",
    "Steam": "증기",
    "Charge": "전하",
    "None": "없음",
    "Unknown": "알 수 없음",
    "Default": "기본값",
    "Disabled": "비활성화",
    "Enabled": "활성화",
    "Yes": "예",
    "No": "아니요",
    "True": "참",
    "False": "거짓",
    "Any": "모두",
    "Empty": "비어 있음",
    "Owner": "소유자",
    "Destination": "목적지",
    "Current": "현재",
    "Next": "다음",
    "Previous": "이전",
    "Save": "저장",
    "Reset": "초기화",
    "Delete": "삭제",
    "Edit": "편집",
    "Done": "완료",
    "Cancel": "취소",
    "Open": "열기",
    "Close": "닫기",
    "Start": "시작",
    "Stop": "정지",
    "Pause": "일시 정지",
    "Continue": "계속",
    "Mode": "모드",
    "Status": "상태",
    "Color": "색상",
    "Name": "이름",
    "Type": "유형",
    "Signal": "신호",
    "Redstone": "레드스톤",
    "Minecraft": "Minecraft",
    "JEI": "JEI",
    "EMI": "EMI",
    "FE": "FE",
    "EU": "EU",
}

KEY_OVERRIDES: dict[str, str] = {
    "itemGroup.railcraft_decorative_blocks": "Railcraft Reborn 장식 블록",
    "itemGroup.railcraft_outfitted_tracks": "Railcraft Reborn 장착형 선로",
    "jei.railcraft.desc.dual_token_signal": (
        "위쪽 램프에는 토큰 신호기, 아래쪽 램프에는 원거리 신호기가 결합된 신호기입니다. "
        "제어기와 수신기 역할을 모두 합니다."
    ),
    "screen.railcraft.golden_ticket.help": (
        "황금 승차권은 공용 열차나 발행자가 소유한 열차에 횟수 제한 없이 탈 수 있는 "
        "승차권입니다. 종이와 조합하면 일회용 승차권을 만들 수도 있습니다."
    ),
    "block.railcraft.feed_station": "사료 공급기",
    "block.railcraft.coal_coke_block": "석탄 코크스 블록",
    "block.railcraft.dual_block_signal": "이중 구간 신호기",
    "block.railcraft.dual_distant_signal": "이중 원거리 신호기",
    "block.railcraft.dual_token_signal": "이중 토큰 신호기",
    "block.railcraft.player_detector": "플레이어 감지기",
    "block.railcraft.steam_turbine": "증기 터빈 외장",
    "block.railcraft.switch_track_motor": "분기 선로 모터",
    "block.railcraft.switch_track_router": "분기 선로 라우터",
    "block.railcraft.token_signal": "토큰 신호기",
    "block.railcraft.token_signal_box": "토큰 신호기 상자",
    "block.railcraft.water_tank_siding": "물탱크 외벽",
    "container.railcraft.blast_furnace": "용광로",
    "container.railcraft.crusher": "분쇄기",
    "container.railcraft.coke_oven": "코크스로",
    "container.railcraft.water_tank_siding": "물탱크",
    "death.railcraft.bore.1": "%s이(가) 발전을 가로막았습니다.",
    "death.railcraft.bore.2": "%s이(가) 터널 굴착기를 막으려 했습니다.",
    "death.railcraft.bore.3": "%s이(가) 터널 굴착기에 짓눌렸습니다.",
    "death.railcraft.bore.4": "%s이(가) 존 헨리보다 잘할 수 있다고 생각했습니다.",
    "death.railcraft.bore.5": "%s이(가) 진퇴양난에 빠졌습니다.",
    "death.railcraft.bore.6": "%s이(가) 발전의 반대편에 서 있었습니다.",
    "death.railcraft.crusher.1": "%s이(가) 중장비 근처에서 발을 헛디뎠습니다.",
    "death.railcraft.crusher.2": "%s은(는) 강철의 사나이가 아니어서 다른 이들처럼 짓눌렸습니다.",
    "death.railcraft.crusher.3": "%s이(가) 심연을 들여다보다 미끄러졌습니다.",
    "death.railcraft.crusher.4": "%s은(는) 장비를 새로 마련해야겠습니다.",
    "death.railcraft.crusher.5": "%s이(가) '발밑 조심!' 표지판을 무시했습니다.",
    "death.railcraft.crusher.6": "지금 판매 중! %s 피 젤리",
    "death.railcraft.crusher.7": "%s이(가) 곤죽이 되었습니다.",
    "death.railcraft.crusher.8": "%s은(는) 설명서를 읽었어야 했습니다.",
    "death.railcraft.electric.1": "%s이(가) 니콜라 테슬라에게 인사하러 갑니다.",
    "death.railcraft.electric.2": "%s이(가) '고전압'의 뜻을 깨달았습니다.",
    "death.railcraft.electric.3": "%s이(가) 전기화의 경이로움을 온몸으로 깨달았습니다.",
    "death.railcraft.electric.4": "%s은(는) 경고 문구를 읽었어야 했습니다.",
    "death.railcraft.electric.5": "%s이(가) 충격적인 사실을 깨달았습니다.",
    "death.railcraft.electric.6": "%s이(가) 전기에 관해 하나 배웠습니다. 아픕니다!",
    "death.railcraft.steam.1": "%s이(가) 육즙이 흐르도록 푹 익었습니다.",
    "death.railcraft.steam.2": "%s은(는) 주장과 달리 고온에 면역이 아니었습니다.",
    "death.railcraft.steam.3": "%s이(가) 증기가 얼마나 뜨거운지 깨달았습니다.",
    "death.railcraft.steam.4": "%s이(가) 산업 재해를 당했습니다.",
    "death.railcraft.steam.5": "%s은(는) 그곳을 밟지 말았어야 했습니다.",
    "death.railcraft.steam.6": "%s이(가) 증기욕은 사우나에서만 해야 한다는 걸 깨달았습니다.",
    "death.railcraft.track_electric.1": "%s이(가) 전기 선로에 소변을 봤습니다.",
    "death.railcraft.track_electric.2": "%s이(가) '고전압'의 뜻을 깨달았습니다.",
    "death.railcraft.track_electric.3": "%s이(가) 전기화의 경이로움을 온몸으로 깨달았습니다.",
    "death.railcraft.track_electric.4": "%s이(가) 제3궤조에 발이 걸렸습니다.",
    "death.railcraft.track_electric.5": "%s이(가) 충격적인 사실을 깨달았습니다.",
    "death.railcraft.track_electric.6": "%s이(가) 전기에 관해 하나 배웠습니다. 아픕니다!",
    "death.railcraft.train.1": "%s이(가) 열차에 치였습니다.",
    "death.railcraft.train.2": "%s이(가) 선로에서 놀고 있었습니다.",
    "death.railcraft.train.3": "%s이(가) 열차와 담력 대결을 벌였지만 열차가 이겼습니다.",
    "death.railcraft.train.4": "%s이(가) 잘못된 열차를 탔습니다.",
    "death.railcraft.train.5": "%s이(가) 저승행 편도 승차권을 샀습니다.",
    "death.railcraft.train.6": "%s은(는) 작업복을 입었어야 했습니다.",
    "entity.railcraft.track_layer": "선로 설치 광산 수레",
    "entity.railcraft.track_relayer": "선로 교체 광산 수레",
    "entity.railcraft.track_remover": "선로 제거 광산 수레",
    "entity.railcraft.track_undercutter": "노반 교체 광산 수레",
    "item.railcraft.track_layer": "선로 설치 광산 수레",
    "item.railcraft.track_relayer": "선로 교체 광산 수레",
    "item.railcraft.track_remover": "선로 제거 광산 수레",
    "item.railcraft.track_undercutter": "노반 교체 광산 수레",
    "item.railcraft.advanced_rail": "고급 레일",
    "item.railcraft.electric_rail": "전기 레일",
    "item.railcraft.high_speed_rail": "고속 레일",
    "item.railcraft.golden_ticket": "황금 승차권",
    "item.railcraft.reinforced_rail": "강화 레일",
    "item.railcraft.routing_table_book": "라우팅 테이블 책",
    "item.railcraft.signal_block_surveyor": "신호 구간 측량기",
    "item.railcraft.signal_tuner": "신호 조율기",
    "item.railcraft.whistle_tuner": "기적 조율기",
    "entity.railcraft.world_spike_minecart": "월드 스파이크 광산 수레",
    "advancements.railcraft.tracks.regular_track.desc": "일반 레일로 선로 제작하기",
    "jei.railcraft.category.fluid_boiler": "유체 연료 보일러",
    "jei.railcraft.category.solid_boiler": "고체 연료 보일러",
    "key.railcraft.loco.whistle": "기관차 기적 울리기",
    "looking_at.railcraft.aspect_received": "수신한 신호 표시: ",
    "looking_at.railcraft.aspect_relayed": "중계한 신호 표시: ",
    "looking_at.railcraft.aspect_sent": "보낸 신호 표시: ",
    "looking_at.railcraft.mode": "모드: ",
    "looking_at.railcraft.reverse": "반전: ",
    "jei.railcraft.desc.block_signal": (
        "광산 수레를 감지하는 기본 신호기입니다. 인접한 구간 신호기와 일대일로 연결해 "
        "둘 사이의 광산 수레를 감지하고, 그 결과에 맞는 신호 표시를 연결된 수신기로 보냅니다."
    ),
    "jei.railcraft.desc.disposable_battery": (
        "전하 네트워크용 배터리입니다. 값싼 일회용 저장 장치로 쓰기 좋으며 완전히 충전된 "
        "상태로 제공됩니다."
    ),
    "jei.railcraft.desc.disposable_battery_empty": (
        "전하 네트워크용 일회용 배터리의 빈 형태입니다. 분쇄기에서 재활용할 수 있습니다."
    ),
    "jei.railcraft.desc.distant_signal": (
        "주로 장식용으로 쓰는 신호기입니다. 광산 수레를 직접 감지하지 않고 연결된 제어기에서 "
        "받은 신호 표시만 보여 줍니다."
    ),
    "jei.railcraft.desc.dual_block_signal": (
        "위쪽 램프에는 구간 신호기, 아래쪽 램프에는 원거리 신호기가 결합된 신호기입니다. "
        "제어기와 수신기 역할을 모두 합니다."
    ),
    "jei.railcraft.desc.dual_distant_signal": (
        "원거리 신호기 두 개가 결합되어 있으며 각각 다른 제어기에 연결할 수 있습니다."
    ),
    "jei.railcraft.desc.manual_rolling_machine": (
        "여러 형태의 금속을 압연하는 기계입니다. 제작 칸에 한 번 작업할 재료만 남았을 때는 "
        "출력 표시를 클릭해 강제로 제작할 수 있습니다."
    ),
    "jei.railcraft.desc.feed_station": (
        "주변 동물에게 자동으로 먹이를 줍니다. 레드스톤으로 끌 수 있으며, 개체 수가 너무 "
        "많아지면 과도한 번식을 막기 위해 먹이 공급을 멈춥니다."
    ),
    "jei.railcraft.desc.logbook": (
        "반경 16블록 안을 지나간 플레이어와 방문한 날짜를 기록합니다. 소유자만 부술 수 있습니다."
    ),
    "jei.railcraft.desc.nickel_iron_battery": (
        "전하 네트워크에서 범용으로 사용하기 좋은 충전식 배터리입니다."
    ),
    "jei.railcraft.desc.nickel_zinc_battery": (
        "전하 네트워크에서 소비 전력이 낮은 장기 저장 용도로 쓰기 좋은 충전식 배터리입니다."
    ),
    "jei.railcraft.desc.personal_world_spike": (
        "월드를 불러올 때 주변 3x3 청크를 불러온 상태로 유지합니다. 소유자만 부술 수 있습니다."
    ),
    "jei.railcraft.desc.powered_rolling_machine": (
        "여러 형태의 금속을 압연하는 기계입니다. 아이템을 파이프로 넣고 빼 자동화할 수 있습니다. "
        "제작 칸에 한 번 작업할 재료만 남았을 때는 출력 표시를 클릭해 강제로 제작할 수 있습니다."
    ),
    "jei.railcraft.desc.token_signal": (
        "광산 수레가 드나드는 구역을 감시하도록 정의하는 신호기입니다. 여러 신호기를 그물처럼 "
        "연결할 수 있고 구역을 이루는 신호기 수에는 제한이 없습니다. 교차로나 대각선 구간에 "
        "사용하는 것이 좋으며, 감지 결과에 맞는 신호 표시를 연결된 수신기로 보냅니다."
    ),
    "jei.railcraft.desc.world_spike": "월드를 불러올 때 주변 3x3 청크를 불러온 상태로 유지합니다.",
    "jei.railcraft.desc.world_spike_minecart": (
        "현재 청크와 동서남북으로 인접한 청크를 불러온 상태로 유지합니다."
    ),
    "railcraft.configuration.boreDestroysBlocks": "터널 굴착기가 블록 파괴",
    "railcraft.configuration.boreMinesAllBlocks": "터널 굴착기가 모든 블록 채굴",
    "railcraft.configuration.boreMiningSpeedMultiplier": "터널 굴착기 채굴 속도 배율",
    "railcraft.configuration.cargoBlacklist": "화물 제외 목록",
    "railcraft.configuration.cartDispenserDelay": "광산 수레 발사기 지연 시간",
    "railcraft.configuration.cartsBreakOnDrop": "낙하 시 광산 수레 파손",
    "railcraft.configuration.cartsCollideWithItems": "광산 수레와 아이템 충돌",
    "railcraft.configuration.changeDungeonLoot": "던전 전리품 변경",
    "railcraft.configuration.chestAllowFluids": "상자 광산 수레에 유체 허용",
    "railcraft.configuration.damageMobs": "기관차가 몹에게 피해 줌",
    "railcraft.configuration.fuelMultiplier": "연료 소비 배율",
    "railcraft.configuration.fuelPerSteamMultiplier": "증기당 연료 소비 배율",
    "railcraft.configuration.ghostTrainEnabled": "유령 열차 활성화",
    "railcraft.configuration.highSpeedTrackIgnoredEntities": "고속 선로가 무시할 엔티티",
    "railcraft.configuration.highSpeedTrackMaxSpeed": "고속 선로 최대 속도",
    "railcraft.configuration.locomotiveLightLevel": "기관차 조명 밝기",
    "railcraft.configuration.lossMultiplier": "손실 배율",
    "railcraft.configuration.maxLauncherTrackForce": "발사 선로 최대 발사력",
    "railcraft.configuration.polarExpressEnabled": "Polar Express 활성화",
    "railcraft.configuration.seasonsEnabled": "계절 장식 활성화",
    "railcraft.configuration.solidCarts": "광산 수레 충돌 판정 활성화",
    "railcraft.configuration.steamLocomotiveEfficiency": "증기 기관차 효율",
    "railcraft.configuration.strapIronTrackMaxSpeed": "띠철 선로 최대 속도",
    "railcraft.configuration.tankStackingEnabled": "탱크 쌓기 활성화",
    "screen.railcraft.action_signal_box.lock.locked": (
        "이 신호기 상자는 %s의 소유로 잠겨 있습니다. 소유자나 관리자만 수정할 수 있습니다."
    ),
    "screen.railcraft.action_signal_box.lock.unlocked": (
        "클릭해 신호기 상자를 잠급니다. 잠그면 본인이나 관리자만 수정할 수 있습니다."
    ),
    "screen.railcraft.cart.maintenance.mode.off": "끔",
    "screen.railcraft.cart.maintenance.mode.on": "켬",
    "screen.railcraft.golden_ticket.desc1": "이 승차권은 다음 목적지에",
    "screen.railcraft.golden_ticket.desc2": "사용할 수 있습니다:",
    "screen.railcraft.golden_ticket.title": "황금 승차권",
    "screen.railcraft.help": "도움말",
    "screen.railcraft.item_detector.filter_mode.at_least": "최소",
    "screen.railcraft.item_detector.filter_mode.at_most": "최대",
    "screen.railcraft.item_detector.filter_mode.exactly": "정확히",
    "screen.railcraft.item_detector.filter_mode.greater_than": "초과",
    "screen.railcraft.item_detector.filter_mode.less_than": "미만",
    "screen.railcraft.item_detector.primary_mode.analog": "아날로그",
    "screen.railcraft.item_detector.primary_mode.anything": "모든 내용물",
    "screen.railcraft.item_detector.primary_mode.empty": "비어 있음",
    "screen.railcraft.item_detector.primary_mode.filtered": "필터 일치",
    "screen.railcraft.item_detector.primary_mode.full": "가득 참",
    "screen.railcraft.item_detector.primary_mode.not_empty": "비어 있지 않음",
    "screen.railcraft.item_manipulator.buffer": "버퍼",
    "screen.railcraft.launcher_track.launch_force": "발사력: %s",
    "screen.railcraft.locomotive.lock.locked": (
        "이 광산 수레는 %s의 소유로 잠겨 있습니다. 소유자나 관리자가 발행한 승차권만 받습니다."
    ),
    "screen.railcraft.locomotive.lock.private": (
        "이 광산 수레는 %s 전용입니다. 소유자나 관리자만 제어할 수 있습니다."
    ),
    "screen.railcraft.locomotive.lock.unlocked": (
        "클릭해 기관차를 잠급니다. 잠그면 본인이나 관리자가 발행한 승차권만 받습니다."
    ),
    "screen.railcraft.locomotive.mode.idle": "대기",
    "screen.railcraft.locomotive.mode.running": "운행",
    "screen.railcraft.locomotive.mode.shutdown": "정지",
    "screen.railcraft.locomotive.steam.mode.description.idle": (
        "열을 유지하면서 연료 소비를 줄입니다. 선로에 붙잡힌 열차도 대기 모드처럼 작동합니다."
    ),
    "screen.railcraft.router_block_entity.private_railway": "사설 철도",
    "screen.railcraft.router_block_entity.public_railway": "공공 철도",
    "screen.railcraft.routing_table_book": "라우팅 테이블 책",
    "screen.railcraft.signal_controller_box.default_aspect": "기본 신호 표시:",
    "screen.railcraft.signal_controller_box.powered_aspect": "전력 공급 시 신호 표시:",
    "screen.railcraft.steam_turbine.output": "출력:",
    "screen.railcraft.steam_turbine.rotor": "회전자:",
    "screen.railcraft.steam_turbine.usage": "소비량:",
    "screen.railcraft.switch_track_motor.redstone_triggered": "레드스톤 작동",
    "screen.railcraft.tank_detector.analog": "탱크 내용물에 비례해 아날로그 레드스톤 신호 출력",
    "screen.railcraft.tank_detector.empty": "빈 탱크",
    "screen.railcraft.tank_detector.full": "가득 찬 탱크",
    "screen.railcraft.tank_detector.half": "절반 이상",
    "screen.railcraft.tank_detector.less_than_full": "가득 차지 않음",
    "screen.railcraft.tank_detector.less_than_half": "절반 미만",
    "screen.railcraft.tank_detector.less_than_most": "3/4 미만",
    "screen.railcraft.tank_detector.less_than_quarter": "1/4 미만",
    "screen.railcraft.tank_detector.most": "3/4 이상",
    "screen.railcraft.tank_detector.not_empty": "비어 있지 않음",
    "screen.railcraft.tank_detector.quarter": "1/4 이상",
    "screen.railcraft.tank_detector.void": "모든 양",
    "screen.railcraft.track_layer.patter": "패턴",
    "screen.railcraft.track_undercutter.sides": "양옆",
    "screen.railcraft.track_undercutter.under": "아래",
    "screen.railcraft.tunnel_bore.ballast": "노반",
    "screen.railcraft.tunnel_bore.head": "굴착기 헤드",
    "screen.railcraft.tunnel_bore.track": "선로",
    "screen.railcraft.water_tank.base_rate": "기본 수집량: %s mB/초",
    "screen.railcraft.water_tank.final_rate": "최종 수집량: %s mB/초",
    "screen.railcraft.water_tank.humidity": "습도 배율: %s",
    "screen.railcraft.water_tank.precipitation": "강수 배율: %s",
    "screen.railcraft.water_tank.sky": "하늘 노출: %s",
    "screen.railcraft.water_tank.temperature": "온도 보정량: %s mB",
    "signal.railcraft.aspect.off": "꺼짐",
    "signal.railcraft.capacitor.falling_edge": "하강 에지",
    "signal.railcraft.capacitor.falling_edge.desc": "마지막 입력 신호가 꺼질 때 타이머를 시작합니다.",
    "signal.railcraft.capacitor.rising_edge": "상승 에지",
    "signal.railcraft.capacitor.rising_edge.desc": "입력 신호를 받는 즉시 타이머를 시작합니다.",
    "signal.railcraft.surveyor.abandoned": "신호 구간 측정을 중단했습니다.",
    "signal.railcraft.surveyor.begin": "신호 구간 측정을 시작합니다.",
    "signal.railcraft.surveyor.invalid_block": "올바른 신호기가 아닙니다.",
    "signal.railcraft.surveyor.invalid_pair": "연결할 수 없는 신호기 조합입니다.",
    "signal.railcraft.surveyor.invalid_track": "선로를 찾을 수 없습니다.",
    "signal.railcraft.surveyor.lost": "첫 번째 신호기가 파괴되었습니다.",
    "signal.railcraft.surveyor.success": "%s을(를) %s에 연결했습니다.",
    "signal.railcraft.tuner.abandoned": "신호기 연결을 중단했습니다.",
    "signal.railcraft.tuner.already_paired": "%s은(는) 이미 %s에 연결되어 있습니다.",
    "signal.railcraft.tuner.begin": "%s을(를) 수신기에 연결하기 시작했습니다.",
    "signal.railcraft.tuner.invalid_controller": "올바른 신호 제어기가 아닙니다.",
    "signal.railcraft.tuner.invalid_receiver": "올바른 신호 수신기가 아닙니다.",
    "signal.railcraft.tuner.lost": "신호 제어기가 파괴되었습니다.",
    "signal.railcraft.tuner.success": "%s을(를) %s에 연결했습니다.",
    "subtitle.railcraft.locomotive.electric.whistle": "전기 기관차가 기적을 울림",
    "subtitle.railcraft.locomotive.steam.whistle": "증기 기관차가 기적을 울림",
    "subtitle.railcraft.machine.steam.burst": "기계에서 증기가 분출됨",
    "subtitle.railcraft.machine.steam.hiss": "기계에서 증기가 샘",
    "subtitle.railcraft.machine.zap": "기계에서 전기가 튐",
    "tips.railcraft.apply_redstone_to_dispense_carts": "- 레드스톤 신호로 광산 수레 배치 -",
    "tips.railcraft.apply_redstone_to_change_direction": "- 레드스톤 신호로 방향 변경 -",
    "tips.railcraft.apply_redstone_to_disable": "- 레드스톤 신호로 비활성화 -",
    "tips.railcraft.apply_redstone_to_enable": "- 레드스톤 신호로 활성화 -",
    "tips.railcraft.apply_redstone_to_open": "- 레드스톤 신호로 열기 -",
    "tips.railcraft.apply_redstone_to_release_carts": "- 레드스톤 신호로 광산 수레 출발 -",
    "tips.railcraft.apply_redstone_to_release_trains": "- 레드스톤 신호로 열차 출발 -",
    "tips.railcraft.blast_furnace": "멀티블록: 3x4x3(속이 빈 구조)",
    "tips.railcraft.block_signal": "신호 구간 안의 광산 수레 감지",
    "tips.railcraft.booster_track": "광산 수레에 가속력을 가합니다.",
    "tips.railcraft.buffer_stop_track": "선로의 끝을 막습니다.",
    "tips.railcraft.cart_dispenser": "광산 수레를 선로 위에 배치합니다.",
    "tips.railcraft.charge_network_battery": "전하 네트워크용 배터리",
    "tips.railcraft.charge_network_empty_battery": "전하 네트워크용 빈 배터리",
    "tips.railcraft.coal_coke_block": "연료 효율: %s개",
    "tips.railcraft.coke_oven": "멀티블록: 3x3x3(속이 빈 구조)",
    "tips.railcraft.comparator_output_from_carts": "- 광산 수레 내용물을 비교기로 측정할 수 있습니다 -",
    "tips.railcraft.control_track": "광산 수레에 약한 추진력을 가합니다.",
    "tips.railcraft.coupler_track": "지나가는 광산 수레를 연결하거나 연결 해제합니다.",
    "tips.railcraft.coupler_track.auto_coupler": "자동 연결",
    "tips.railcraft.coupler_track.decoupler": "연결 해제",
    "tips.railcraft.crowbar.desc": "웅크린 상태로 우클릭해 광산 수레를 연결합니다.",
    "tips.railcraft.crowbar.link.created": "광산 수레 연결 완료",
    "tips.railcraft.crowbar.link.broken": "광산 수레 연결이 끊어졌습니다.",
    "tips.railcraft.crowbar.link.failed": "광산 수레 연결 실패",
    "tips.railcraft.crowbar.link.started": "광산 수레 연결 시작",
    "tips.railcraft.detector_track": "광산 수레가 표시 방향으로 지나가면 레드스톤 신호를 냅니다.",
    "tips.railcraft.disembarking_track": "화살표 방향으로 탑승한 엔티티를 내립니다.",
    "tips.railcraft.distant_signal": "연결된 제어기가 보낸 신호 표시를 보여 줍니다.",
    "tips.railcraft.dumping_track": "지나가는 광산 수레의 엔티티나 아이템을 선로 아래로 내립니다.",
    "tips.railcraft.embarking_track": "엔티티를 광산 수레에 태웁니다.",
    "tips.railcraft.feed_station": "주변 동물에게 자동으로 먹이를 줍니다.",
    "tips.railcraft.firestone.charged": "에너지로 가득 차 있습니다. 의지를 집중하면 작열하는 열기를 방출합니다...",
    "tips.railcraft.firestone.cut": "아직도 에너지가 걷잡을 수 없이 날뜁니다...",
    "tips.railcraft.firestone.empty": "에너지가 안정되었습니다. 다시 충전할 수 있다면 쓸모가 있을 것입니다...",
    "tips.railcraft.firestone.ore": "네더의 용암 지대에서 발견됩니다.",
    "tips.railcraft.firestone.raw": "손안에서 고동치며 주변 공기에서도 그 힘이 느껴집니다...",
    "tips.railcraft.fluid_loader": "광산 수레에 유체를 채웁니다.",
    "tips.railcraft.fluid_unloader": "광산 수레에서 유체를 꺼냅니다.",
    "tips.railcraft.force_track_emitter": "에너지로 선로를 투사합니다.",
    "tips.railcraft.frame": "전기 선로에 전력을 공급합니다.",
    "tips.railcraft.fueled_boiler_firebox": "멀티블록: 가변 크기, 맨 아래층",
    "tips.railcraft.gated_track": "선로에 차단문이 내장되어 있습니다.",
    "tips.railcraft.goggles.aura.shunting": "입환",
    "tips.railcraft.goggles.aura.signalling": "신호",
    "tips.railcraft.goggles.aura.surveying": "신호 구간 측정",
    "tips.railcraft.goggles.aura.tracking": "추적",
    "tips.railcraft.goggles.aura.tuning": "신호 조율",
    "tips.railcraft.goggles.aura.worldspike": "월드 스파이크",
    "tips.railcraft.goggles.desc": "우클릭해 오라를 변경합니다.",
    "tips.railcraft.hit_crowbar_to_change_detection_direction": "- 쇠지렛대로 때려 감지 방향 변경 -",
    "tips.railcraft.hit_crowbar_to_change_direction": "- 쇠지렛대로 때려 방향 변경 -",
    "tips.railcraft.hit_crowbar_to_change_force": "- 쇠지렛대로 때려 추진력 변경 -",
    "tips.railcraft.hit_crowbar_to_change_mode": "- 쇠지렛대로 때려 모드 변경 -",
    "tips.railcraft.hit_crowbar_to_change_range": "- 쇠지렛대로 때려 범위 변경 -",
    "tips.railcraft.hit_crowbar_to_change_ticket": "- 쇠지렛대로 때려 승차권 변경 -",
    "tips.railcraft.hit_crowbar_to_rotate": "- 쇠지렛대로 때려 회전 -",
    "tips.railcraft.item_loader": "광산 수레에 아이템을 싣습니다.",
    "tips.railcraft.item_unloader": "광산 수레에서 아이템을 내립니다.",
    "tips.railcraft.launcher_track": "광산 수레를 공중으로 발사합니다!",
    "tips.railcraft.listen": "수신",
    "tips.railcraft.locking_track": "광산 수레를 멈춰 대기시킵니다.",
    "tips.railcraft.locking_track.holding": "대기",
    "tips.railcraft.locking_track.lockdown": "잠금",
    "tips.railcraft.locking_track.train_holding": "열차 대기",
    "tips.railcraft.locking_track.train_lockdown": "열차 잠금",
    "tips.railcraft.locking_track.train_boarding_reversed": "역방향 열차 탑승",
    "tips.railcraft.locomotive_track": "기관차 출발/정지",
    "tips.railcraft.locomotive.item.whistle": "기적 음높이:",
    "tips.railcraft.manipulator.redstone_mode.complete": "완료 시",
    "tips.railcraft.manipulator.redstone_mode.immediate": "즉시",
    "tips.railcraft.manipulator.redstone_mode.manual.desc": "레드스톤 신호를 출력하지 않습니다.",
    "tips.railcraft.manipulator.redstone_mode.partial.desc": (
        "공간이나 공급품이 부족할 때까지 처리하되 광산 수레의 기존 내용물은 남깁니다."
    ),
    "tips.railcraft.manipulator.transfer_mode.all.desc": "일치하는 아이템을 모두 옮깁니다.",
    "tips.railcraft.manipulator.transfer_mode.excess.desc": "출발지 내용물이 필터 수량과 같아질 때까지 옮깁니다.",
    "tips.railcraft.manipulator.transfer_mode.stock.desc": "목적지 내용물이 필터 수량과 같아질 때까지 옮깁니다.",
    "tips.railcraft.manipulator.transfer_mode.transfer": "지정량",
    "tips.railcraft.manipulator.transfer_mode.transfer.desc": "필터에 지정한 수량만큼 정확히 옮깁니다.",
    "tips.railcraft.max_draw": "최대 소비량: %s FE/t",
    "tips.railcraft.one_way_track": "광산 수레는 화살표 방향으로만 지나갈 수 있습니다.",
    "tips.railcraft.pair_with_control_track": "- 제어 선로와 연결 -",
    "tips.railcraft.require_boosters_transition": "고속에 도달하려면 가속·전환 선로가 필요합니다.",
    "tips.railcraft.signal_interlock_box": "한 번에 한 신호 표시만 통과시킵니다.",
    "tips.railcraft.signal_label.desc2": "웅크린 상태로 우클릭해 신호기나 신호기 상자의 이름을 지정합니다.",
    "tips.railcraft.signal_receiver_box": "제어기의 신호를 받습니다.",
    "tips.railcraft.signal_sequencer_box": "인접한 블록을 차례로 반복 작동합니다.",
    "tips.railcraft.signal_surveyor": "신호 구간 측량기",
    "tips.railcraft.signal_tuner": "신호 조율기",
    "tips.railcraft.spike_maul": "선로를 분기·Y자·교차 선로로 바꿉니다.",
    "tips.railcraft.steam_turbine_desc2": "아래쪽으로 물을 내보냅니다.",
    "tips.railcraft.steam_turbine_desc3": "터빈 회전자가 필요합니다.",
    "tips.railcraft.strap_iron_track": "철 선로 속도의 30%",
    "tips.railcraft.switch_track_lever": "인접한 분기 선로를 제어합니다.",
    "tips.railcraft.track_layer": "이동하면서 선로를 설치합니다.",
    "tips.railcraft.track_relayer": "기존 선로를 다른 선로로 교체합니다.",
    "tips.railcraft.track_remover": "지나간 선로를 제거합니다.",
    "tips.railcraft.track_kit.slopes_unsupported": "경사로는 지원되지 않습니다.",
    "tips.railcraft.train_dispenser": "연결된 열차를 선로 위에 배치합니다.",
    "tips.railcraft.transition_track": "일반 속도와 고속 사이를 전환합니다.",
    "tips.railcraft.very_fast": "매우 빠름",
    "tips.railcraft.water_tank_siding": "멀티블록: 3x3x3(속이 빈 구조)",
    "tips.railcraft.whistle_track": "지나가는 기관차가 기적을 울립니다.",
    "manual.railcraft.routing_table.page.1": (
        "라우팅 테이블을 라우팅 감지기나 스위치에 놓으면 지나가는 기관차와 대조할 규칙을 "
        "정의합니다. 규칙은 단순한 논리 문법을 사용하므로 간단한 규칙부터 복잡한 규칙까지 "
        "만들 수 있습니다. 연산자 뒤에 피연산자가 오는 전위 표기법을 사용하며, 한 줄에는 "
        "키워드 하나만 쓸 수 있습니다. 연산자를 생략하면 OR로 처리합니다. 제작 칸에 라우팅 "
        "테이블을 두 개 이상 함께 놓으면 내용을 복사할 수 있습니다."
    ),
    "manual.railcraft.routing_table.page.2": (
        "연산자 키워드:\n"
        "  AND - 피연산자 2개가 모두 참이어야 합니다.\n"
        "  OR - 피연산자 2개 중 하나가 참이어야 합니다.\n"
        "  NOT - 다음 피연산자의 결과를 뒤집습니다.\n"
        "  IF - 피연산자 3개: 조건, 참일 때, 거짓일 때.\n"
        "       조건이 참이면 두 번째 값을,\n"
        "       거짓이면 세 번째 값을 사용합니다.\n"
    ),
    "manual.railcraft.routing_table.page.3": (
        "조건 키워드:\n"
        "  Dest=<문자열>\n"
        "    기관차의 목적지가 이 문자열로\n"
        "    시작하면 참입니다.\n"
        "    Dest=null은 목적지가 없는\n"
        "    광산 수레와\n"
        "    일치합니다.\n"
        "  Owner=<사용자 이름>\n"
        "    기관차의 소유자가 이 사용자이면\n"
        "    참입니다.\n"
    ),
    "manual.railcraft.routing_table.page.4": (
        "조건 키워드:\n"
        "  Name=<엔티티 이름>\n"
        "    광산 수레의 이름과 일치하면 참입니다.\n"
        "    Name=null은 사용자 지정 이름이 없는\n"
        "    광산 수레와 일치합니다.\n"
        "  Type=<모드 ID:\n"
        "        아이템 이름>\n"
        "    광산 수레 아이템의 ID와 일치하면\n"
        "    참입니다.\n"
    ),
    "manual.railcraft.routing_table.page.5": (
        "조건 키워드:\n"
        "  Rider=<유형>[:<한정자>]\n"
        "    열차에 일치하는 승객이 있으면 참입니다.\n"
        "    단순 유형:\n"
        "      any, none, mob, animal, unnamed\n"
        "    한정자를 쓸 수 있는 유형:\n"
        "      player, named, entity\n"
        "    정규식을 쓸 수 있는 유형:\n"
        "      player, named\n"
        "  예시는 GitHub 이슈\n"
        "  #844를 참고하세요.\n"
    ),
    "manual.railcraft.routing_table.page.6": (
        "조건 키워드:\n"
        "  Color=<주 색상>,<보조 색상>\n"
        "    기관차의 주 색상과 보조 색상이\n"
        "    일치하면 참입니다.\n"
        "    Any를 와일드카드로\n"
        "    쓸 수 있습니다.\n"
        "    색상: Black, Red, Green, Brown, Blue,\n"
        "    Purple, Cyan, LightGray, Gray, Pink, Lime,\n"
        "    Yellow, LightBlue, Magenta, Orange, White\n"
        "  NeedsRefuel=<true/false>\n"
        "    기관차에 연료나 물이 부족하면 참입니다.\n"
    ),
    "manual.railcraft.routing_table.page.7": (
        "조건 키워드:\n"
        "  Redstone=<true/false>\n"
        "    라우팅 블록에 레드스톤 신호가\n"
        "    공급되면 참입니다.\n"
    ),
    "manual.railcraft.routing_table.page.8": (
        "조건 키워드:\n"
        "  Loco=<문자열>\n"
        "    기관차가 지정한 문자열과 일치하면\n"
        "    참입니다.\n"
        "    허용값: electric, steam,\n"
        "    creative, none.\n"
        "    none은 기관차가 없을 때만\n"
        "    참을 반환합니다.\n"
    ),
    "manual.railcraft.routing_table.page.9": (
        "예제 스크립트:\n"
        "  Dest=TheFarLands\n"
        "  Color=Black,Red\n"
        "  AND\n"
        "  NOT\n"
        "  Owner=Steve\n"
        "  Dest=SecretHideout/OceanEntrance\n"
    ),
    "manual.railcraft.routing_table.page.10": (
        "결과:\n"
        "  이전 페이지의 스크립트는 목적지가\n"
        "  TheFarLands/Milliways인 기관차,\n"
        "  검은색과 빨간색으로 칠한 기관차,\n"
        "  또는 목적지가\n"
        "  SecretHideout/OceanEntrance이면서\n"
        "  Steve의 소유가 아닌 기관차와\n"
        "  일치합니다.\n"
    ),
    "manual.railcraft.routing_table.page.11": (
        "정규식:\n"
        "  일부 조건은 정규식을 지원합니다.\n"
        "  정규식을 쓰려면 = 앞에 ?를 붙입니다.\n"
        "  표준 Java Pattern\n"
        "  문법을 사용합니다.\n"
        "지원 조건:\n"
        "  Dest, Name\n"
        "예시:\n"
        "  Dest?=.*Hill\n"
    ),
    "manual.railcraft.routing_table.page.12": (
        "아날로그 출력:\n"
        "  IF에 정수 상수를 사용해\n"
        "  아날로그 신호를\n"
        "  출력할 수 있습니다. 정수와 IF는 최상위나\n"
        "  IF의 참·거짓 결과에만 쓸 수 있습니다.\n"
        "  TRUE와 FALSE는 어디에서나 쓸 수 있습니다.\n"
        "예시:\n"
        "  IF\n"
        "  Dest=Town\n"
        "  8\n"
        "  IF\n"
        "  Dest=City\n"
        "  4\n"
        "  FALSE\n"
    ),
    "advancements.railcraft.carts.bed_cart.desc": "침대 광산 수레를 타고 잠자기",
    "advancements.railcraft.carts.bed_cart.name": "바퀴 위의 꿈",
    "advancements.railcraft.carts.jukebox_cart.desc": "주크박스 광산 수레에서 음반 재생하기",
    "advancements.railcraft.carts.jukebox_cart.name": "움직이는 음악",
    "advancements.railcraft.carts.link_carts.desc": "웅크리기를 잊지 마세요!",
    "advancements.railcraft.carts.link_carts.name": "광산 수레 연결하기",
    "advancements.railcraft.carts.locomotive.desc": "기관차로 열차에 동력 공급하기",
    "advancements.railcraft.carts.locomotive.name": "힘차게 달리기",
    "advancements.railcraft.carts.root.desc": "Railcraft의 차량과 기술",
    "advancements.railcraft.carts.root.name": "Railcraft 광산 수레",
    "advancements.railcraft.carts.seasons.desc": "계절 쇠지렛대로 광산 수레의 계절 장식 바꾸기",
    "advancements.railcraft.carts.seasons.name": "시대착오",
    "advancements.railcraft.carts.surprise.desc": "계절 광산 수레를 폭발시키고 선물(정말로?) 모으기",
    "advancements.railcraft.carts.surprise.name": "절묘한 폭발",
    "advancements.railcraft.tracks.blast_furnace.desc": "용광로 건설하기",
    "advancements.railcraft.tracks.blast_furnace.name": "제철소",
    "advancements.railcraft.tracks.coke_oven.desc": "코크스로 벽돌의 툴팁을 읽고 완전한 코크스로 건설하기",
    "advancements.railcraft.tracks.coke_oven.name": "코크스 전문가",
    "advancements.railcraft.tracks.crusher.desc": "분쇄기 건설하기",
    "advancements.railcraft.tracks.crusher.name": "중장비",
    "advancements.railcraft.tracks.firestone.desc": "네더 용암 바다 바닥에서 화염석 광석을 찾아 암석 분쇄기로 분쇄하기",
    "advancements.railcraft.tracks.firestone.name": "다루기 힘든 에너지",
    "advancements.railcraft.tracks.high_speed_track.desc": "고속 선로를 얻고 그 위에서 광산 수레 타기",
    "advancements.railcraft.tracks.high_speed_track.name": "불붙은 광산 수레",
    "advancements.railcraft.tracks.junctions.desc": "스파이크 망치로 일반 선로를 분기·Y자·교차 선로로 바꾸기",
    "advancements.railcraft.tracks.junctions.name": "더 나은 분기",
    "advancements.railcraft.tracks.manual_rolling_machine.desc": "합금으로 수동 압연기 만들기",
    "advancements.railcraft.tracks.manual_rolling_machine.name": "쉬지 않는 압연",
    "advancements.railcraft.tracks.regular_track.name": "합리적인 가격",
    "advancements.railcraft.tracks.root.desc": "Railcraft의 철도 기술",
    "advancements.railcraft.tracks.root.name": "선로",
    "advancements.railcraft.tracks.track_kit.desc": "유연 선로에 선로 키트를 설치해 완충 정지 선로처럼 기능 추가하기",
    "advancements.railcraft.tracks.track_kit.name": "다기능 선로",
    "advancements.railcraft.tracks.wooden_track.desc": "철이 거의 들지 않는 띠철 선로 얻기",
    "advancements.railcraft.tracks.wooden_track.name": "나무 시대",
}

ALLOWED_EXACT_VALUES = {
    "Railcraft",
    "Railcraft Reborn",
    "Minecraft",
    "JEI",
    "EMI",
    "FE",
    "EU",
    "AND",
    "OR",
    "NOT",
    "IF",
    "TRUE",
    "FALSE",
}

FORBIDDEN_ARTIFACTS = (
    "레시피",
    "컨트롤러",
    "파이어박스",
    "터널 보어",
    "보어 헤드",
    "트랙 키트",
    "궤도 키트",
    "아이템 로더",
    "아이템 언로더",
    "액체 로더",
    "액체 언로더",
    "코크스 오븐",
    "롤링 머신",
    "롤링 기계",
    "엔터티",
)

COLORS = {
    "black": "검은색",
    "blue": "파란색",
    "brown": "갈색",
    "cyan": "청록색",
    "gray": "회색",
    "green": "초록색",
    "light_blue": "하늘색",
    "light_gray": "밝은 회색",
    "lime": "라임색",
    "magenta": "자홍색",
    "orange": "주황색",
    "pink": "분홍색",
    "purple": "보라색",
    "red": "빨간색",
    "white": "흰색",
    "yellow": "노란색",
}

TRACK_TYPES = {
    "abandoned": "버려진",
    "electric": "전기",
    "high_speed": "고속",
    "high_speed_electric": "고속 전기",
    "iron": "철",
    "reinforced": "강화",
    "strap_iron": "띠철",
}

TRACK_FEATURES = {
    "activator": "작동",
    "booster": "가속",
    "buffer_stop": "완충 정지",
    "control": "제어",
    "coupler": "연결",
    "detector": "감지",
    "disembarking": "하차",
    "dumping": "투하",
    "embarking": "승차",
    "gated": "차단문",
    "junction": "교차",
    "launcher": "발사",
    "locking": "잠금",
    "locomotive": "기관차",
    "one_way": "단방향",
    "routing": "라우팅",
    "throttle": "속도 조절",
    "transition": "전환",
    "turnout": "분기",
    "whistle": "기적",
    "wye": "Y자",
}


def structured_name(key: str, value: str) -> str:
    """반복 이름은 키 구조에서 등급·색상·기능을 복원해 충돌 없이 통일한다."""
    path = key.removeprefix("block.railcraft.").removeprefix("item.railcraft.")
    for color, color_name in COLORS.items():
        if path == f"{color}_post":
            return f"{color_name} 기둥"
        if path == f"{color}_strengthened_glass":
            return f"{color_name} 강화 유리"
        for material, material_name in (("iron", "철제"), ("steel", "강철")):
            for part, part_name in (
                ("gauge", "게이지"),
                ("valve", "밸브"),
                ("wall", "벽"),
            ):
                if path == f"{color}_{material}_tank_{part}":
                    return f"{color_name} {material_name} 탱크 {part_name}"

    if key.startswith("block.railcraft.") and path.endswith("_track"):
        stem = path[: -len("_track")]
        track_type = ""
        for prefix in sorted(TRACK_TYPES, key=len, reverse=True):
            if stem == prefix:
                return f"{TRACK_TYPES[prefix]} 선로"
            if stem.startswith(prefix + "_"):
                track_type = TRACK_TYPES[prefix]
                stem = stem[len(prefix) + 1 :]
                break
        feature = TRACK_FEATURES.get(stem)
        if feature:
            return " ".join(part for part in (track_type, feature, "선로") if part)

    if key.startswith("item.railcraft.") and path.endswith("_track_kit"):
        feature = TRACK_FEATURES.get(path[: -len("_track_kit")])
        if feature:
            return f"{feature} 선로 키트"

    fixed_items = {
        "coal_coke": "석탄 코크스",
        "coal_coke_block": "석탄 코크스 블록",
        "coke_oven_bricks": "코크스로 벽돌",
        "cracked_firestone": "금이 간 화염석",
        "cut_firestone": "가공된 화염석",
        "raw_firestone": "가공 전 화염석",
        "firestone_ore": "화염석 광석",
        "diamond_spike_maul": "다이아몬드 스파이크 망치",
        "iron_spike_maul": "철 스파이크 망치",
        "steel_spike_maul": "강철 스파이크 망치",
        "world_spike": "월드 스파이크",
        "personal_world_spike": "개인용 월드 스파이크",
        "world_spike_minecart": "월드 스파이크 광산 수레",
    }
    return fixed_items.get(path, value)


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


def request_candidate(source: str) -> str:
    return candidate_helper.request_translation_candidate(source)


def candidate() -> dict[str, object]:
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
                executor.submit(request_candidate, source): source
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

    translated: dict[str, str] = {}
    for key, source in english.items():
        if not isinstance(source, str):
            raise TypeError(f"문자열이 아닌 언어 값: {key}")
        if source in SOURCE_OVERRIDES:
            translated[key] = SOURCE_OVERRIDES[source]
        elif family_goal.is_allowed_original(source):
            translated[key] = source
        else:
            translated[key] = str(cache[source])
    write_json(CANDIDATE_FILE, {NAMESPACE: translated})
    report = {
        "keys": len(english),
        "candidate_keys": len(translated),
        "review_scope": "all_current_english_keys_including_bundled_korean",
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "auto_candidate_report.json", report)
    return report


def reviewed_value(key: str, source: str, candidate_value: str) -> str:
    value = SOURCE_OVERRIDES.get(source, candidate_value)
    for old, new in TERM_REPLACEMENTS:
        value = value.replace(old, new)
    value = KEY_OVERRIDES.get(key, value)
    value = structured_name(key, value)
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    value = re.sub(r" {2,}", " ", value)
    if key.startswith(("item.", "block.", "entity.", "effect.")):
        value = value.rstrip(".")
    return value


def normalize() -> dict[str, object]:
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    candidates = load_json(CANDIDATE_FILE).get(NAMESPACE)
    if not isinstance(candidates, dict):
        raise TypeError("Railcraft 후보 네임스페이스가 없습니다.")
    changed = 0
    unresolved: list[str] = []
    for key, source in english.items():
        candidate_value = candidates.get(key)
        if not isinstance(source, str) or not isinstance(candidate_value, str):
            raise TypeError(f"문자열이 아닌 언어 값: {key}")
        translated = reviewed_value(key, source, candidate_value)
        errors = family_goal.validate_family_value(FAMILY, key, source, translated)
        if errors:
            raise ValueError("; ".join(errors))
        if korean.get(key) != translated:
            korean[key] = translated
            changed += 1
        if (
            source == translated
            and source not in ALLOWED_EXACT_VALUES
            and not family_goal.is_allowed_original(source)
        ):
            unresolved.append(key)
    write_json(LANG_ROOT / "ko_kr.json", korean)
    report = {
        "keys_reviewed": len(english),
        "bundled_korean_reused_without_review": 0,
        "changed": changed,
        "unresolved": len(unresolved),
        "unresolved_examples": unresolved[:30],
        "review_status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    errors: list[str] = []
    untranslated: list[str] = []
    if list(english) != list(korean):
        errors.append("영어와 한국어의 키 또는 순서가 다릅니다.")
    for key, source in english.items():
        target = korean.get(key)
        if not isinstance(source, str) or not isinstance(target, str):
            errors.append(f"문자열이 아닌 값: {key}")
            continue
        errors.extend(family_goal.validate_family_value(FAMILY, key, source, target))
        artifacts = [word for word in FORBIDDEN_ARTIFACTS if word in target]
        if artifacts:
            errors.append(f"용어 미정리: {key}: {', '.join(artifacts)}")
        if (
            source == target
            and source not in ALLOWED_EXACT_VALUES
            and not family_goal.is_allowed_original(source)
        ):
            untranslated.append(key)
    if untranslated:
        errors.append(f"미번역 키: {untranslated[:30]}")
    report = {
        "keys_reviewed": len(english),
        "bundled_korean_reused_without_review": 0,
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
