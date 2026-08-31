#!/usr/bin/env python3
"""FramedBlocks의 전체 표시 문자열과 관련 퀘스트를 번역하고 검증해요."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import build_ae2_quests as quest_snbt
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILY = "framedblocks"
NAMESPACE = "framedblocks"
JAR_PATTERN = "FramedBlocks-*.jar"
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
RESOURCE_OUTPUT = (
    active_output_root()
    / "resourcepack/ATM10_Korean/assets/framedblocks/lang/ko_kr.json"
)
QUEST_OUTPUT = (
    active_output_root() / "overrides/config/ftbquests/quests/lang/ko_kr.snbt"
)
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z%]|\{[A-Za-z0-9_]+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"\d+(?:[.]\d+)?")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")

BLOCK_PHRASES = {
    "Powered Framing Saw": "전동 프레임 절단기",
    "Framing Saw": "프레임 절단기",
    "Light Weighted Pressure Plate": "가벼운 무게 감압판",
    "Heavy Weighted Pressure Plate": "무거운 무게 감압판",
    "One-Way Window": "단방향 창문",
    "Glow Item Frame": "발광 아이템 액자",
    "Item Frame": "아이템 액자",
    "Hanging Sign": "매달린 표지판",
    "Fence Gate": "울타리 문",
    "Flower Pot": "화분",
    "Floor Board": "바닥 판",
    "Pillar Socket": "기둥 소켓",
    "Pressure Plate": "감압판",
    "Lightning Rod": "피뢰침",
    "Secret Storage": "비밀 저장소",
    "Redstone Block": "레드스톤 블록",
    "Redstone Torch": "레드스톤 횃불",
    "Stone Button": "돌 버튼",
    "Soul Lantern": "영혼 랜턴",
    "Soul Torch": "영혼 횃불",
}

BLOCK_WORDS = {
    "Framed": "프레임",
    "Activator": "작동",
    "Rail": "레일",
    "Slope": "경사",
    "Adjustable": "조절식",
    "Double": "이중",
    "Copycat": "카피캣",
    "Panel": "패널",
    "Slab": "반 블록",
    "Bars": "창살",
    "Bookshelf": "책장",
    "Bouncy": "탄성",
    "Board": "판",
    "Cube": "큐브",
    "Button": "버튼",
    "Centered": "중앙",
    "Chain": "사슬",
    "Checkered": "체크무늬",
    "Segment": "조각",
    "Chest": "상자",
    "Chiseled": "조각된",
    "Collapsible": "접이식",
    "Block": "블록",
    "Compound": "복합",
    "Corner": "모서리",
    "Pillar": "기둥",
    "Edge": "가장자리",
    "Strip": "띠",
    "Tube": "관",
    "Detector": "감지",
    "Divided": "분할",
    "Horizontal": "가로",
    "Vertical": "세로",
    "Stairs": "계단",
    "Door": "문",
    "Half": "절반",
    "Prism": "프리즘",
    "Threeway": "삼방향",
    "Elevated": "상승",
    "Inner": "안쪽",
    "Sloped": "경사진",
    "Pyramid": "피라미드",
    "Extended": "확장",
    "Fancy": "장식",
    "Powered": "전동",
    "Fence": "울타리",
    "Flat": "평면",
    "Inverse": "역방향",
    "Inverted": "역방향",
    "Stacked": "겹침",
    "Gate": "문",
    "Glowing": "빛나는",
    "Gold": "금",
    "Iron": "철",
    "Hopper": "호퍼",
    "Pane": "판유리",
    "Trapdoor": "다락문",
    "Ladder": "사다리",
    "Lantern": "랜턴",
    "Large": "대형",
    "Lattice": "격자",
    "Layered": "다층",
    "Lever": "레버",
    "Masonry": "석조",
    "Mini": "소형",
    "Obsidian": "흑요석",
    "Path": "길",
    "Post": "말뚝",
    "Sign": "표지판",
    "Sliced": "절단",
    "Small": "소형",
    "Stone": "돌",
    "Split": "분할",
    "Target": "과녁",
    "Tank": "탱크",
    "Thick": "두꺼운",
    "Torch": "횃불",
    "Upper": "상부",
    "Wall": "담장",
}

STATIC_TRANSLATIONS = {
    "config.framedblocks.client.altGhostRenderer": "대체 설치 미리보기 렌더러 사용",
    "config.framedblocks.client.camoMessageVerbosity": "허용되지 않는 위장 안내 수준",
    "config.framedblocks.client.camoRotationMode": "위장 회전 오버레이 표시 방식",
    "config.framedblocks.client.conTexDisabled": "연결 텍스처 지원 비활성화",
    "config.framedblocks.client.conTexMode": "연결 텍스처 방식",
    "config.framedblocks.client.copycatStyleMode": "카피캣 형식 오버레이 표시 방식",
    "config.framedblocks.client.detailedCulling": "정밀 컬링",
    "config.framedblocks.client.discreteUVSteps": "불연속 UV 단계 사용",
    "config.framedblocks.client.fancyHitboxes": "정교한 충돌 상자",
    "config.framedblocks.client.forceAoOnGlowingBlocks": (
        "빛나는 프레임 블록에 주변광 차폐 강제 적용"
    ),
    "config.framedblocks.client.ghostRenderOpacity": "설치 미리보기 불투명도",
    "config.framedblocks.client.itemFrameBackgroundMode": (
        "아이템 액자 배경 오버레이 표시 방식"
    ),
    "config.framedblocks.client.maxOverlayMode": "최대 오버레이 표시 방식",
    "config.framedblocks.client.oneWayWindowMode": "단방향 창문 오버레이 표시 방식",
    "config.framedblocks.client.prismOffsetMode": "프리즘 오프셋 오버레이 표시 방식",
    "config.framedblocks.client.reinforcedMode": "보강 오버레이 표시 방식",
    "config.framedblocks.client.renderCamoInJade": "Jade 오버레이에 위장 표시",
    "config.framedblocks.client.renderItemModelsWithCamo": ("아이템 모델에 위장 표시"),
    "config.framedblocks.client.showAllRecipePermutationsInEmi": (
        "EMI에 프레임 절단기 제작법 조합 모두 표시"
    ),
    "config.framedblocks.client.showButtonPlateTypeOverlay": (
        "버튼·감압판 종류 오버레이 표시"
    ),
    "config.framedblocks.client.showCamoCraftingInJei": ("JEI에 위장 적용 제작법 표시"),
    "config.framedblocks.client.showGhostBlocks": "설치 미리보기 블록 표시",
    "config.framedblocks.client.showSpecialCubeTypeOverlay": (
        "특수 큐브 종류 오버레이 표시"
    ),
    "config.framedblocks.client.solidFrameMode": "단색 프레임 방식",
    "config.framedblocks.client.splitLineMode": (
        "접이식 블록 분할선 오버레이 표시 방식"
    ),
    "config.framedblocks.client.stateLockMode": "상태 잠금 오버레이 표시 방식",
    "config.framedblocks.client.toggleWaterlogMode": (
        "수중 설치 가능 여부 오버레이 표시 방식"
    ),
    "config.framedblocks.client.toggleYSlopeMode": "Y축 경사 오버레이 표시 방식",
    "config.framedblocks.client.trapdoorTextureRotationMode": (
        "다락문 텍스처 회전 오버레이 표시 방식"
    ),
    "config.framedblocks.devtools.connectionDebug": "연결 조건 디버그",
    "config.framedblocks.devtools.doubleBlockPartDebug": "이중 블록 부분 디버그",
    "config.framedblocks.devtools.occlusionShapeDebug": "가림 형태 디버그",
    "config.framedblocks.devtools.quadWindingDebug": "사각형 정점 순서 디버그",
    "config.framedblocks.devtools.stateMergerDebug": "상태 병합기 디버그",
    "config.framedblocks.devtools.stateMergerDebugFilter": "상태 병합기 디버그 필터",
    "config.framedblocks.server.allowBlockEntities": "블록 엔티티 허용",
    "config.framedblocks.server.consumeCamoItem": "위장 재료 소비",
    "config.framedblocks.server.consumption": "소비량",
    "config.framedblocks.server.craftingDuration": "제작 시간",
    "config.framedblocks.server.enableIntangibleFeature": "비실체 기능 활성화",
    "config.framedblocks.server.energyCapacity": "에너지 용량",
    "config.framedblocks.server.fireproofBlocks": "내화 블록",
    "config.framedblocks.server.glowstoneLightLevel": "발광석 밝기",
    "config.framedblocks.server.maxReceive": "최대 입력",
    "config.framedblocks.server.oneWayWindowOwnable": "단방향 창문 소유권 설정 허용",
    "config.jade.plugin_framedblocks.framed_block_generic": "FramedBlocks 위장",
    "config.jade.plugin_framedblocks.framed_item_frame": "프레임 아이템 액자",
    "desc.framedblocks.block.fluid_tank.contents": "저장된 유체: %s",
    "desc.framedblocks.block.fluid_tank.contents.empty": "비어 있음",
    "desc.framedblocks.block.stored_camo": "위장: %s",
    "desc.framedblocks.blueprint_block": "포함된 블록: %s",
    "desc.framedblocks.blueprint_camo": "위장 블록: %s",
    "desc.framedblocks.blueprint_cant_copy": (
        "[프레임 설계도] 현재 이 블록은 복사할 수 없습니다!"
    ),
    "desc.framedblocks.blueprint_cant_place_fluid_camo": (
        "[프레임 설계도] 유체 위장이 적용된 블록은 현재 복사할 수 없습니다!"
    ),
    "desc.framedblocks.blueprint_false": "거짓",
    "desc.framedblocks.blueprint_illuminated": "발광: %s",
    "desc.framedblocks.blueprint_intangible": "비실체: %s",
    "desc.framedblocks.blueprint_invalid": "유효하지 않음",
    "desc.framedblocks.blueprint_missing_materials": (
        "[프레임 설계도] 필요한 재료가 부족합니다:"
    ),
    "desc.framedblocks.blueprint_none": "없음",
    "desc.framedblocks.blueprint_reinforced": "보강됨: %s",
    "desc.framedblocks.blueprint_true": "참",
    "desc.framedblocks.camo.empty": "비어 있음",
    "desc.framedblocks.framed_axe.retain_camo": (
        "이 도끼로 부순 프레임 블록은 위장 재료를 따로 떨어뜨리지 않고 유지합니다"
    ),
    "desc.framedblocks.slope_slab.place_upside_down": (
        "거꾸로 설치하려면 웅크리기 키를 누르세요"
    ),
    "framedblocks.configuration.general": "일반",
    "framedblocks.configuration.overlay": "오버레이",
    "framedblocks.configuration.powered_framing_saw": "전동 프레임 절단기",
    "framedblocks.configuration.section.framedblocks.devtools.toml": ("개발 도구 설정"),
    "framedblocks.configuration.section.framedblocks.devtools.toml.title": (
        "FramedBlocks 개발 도구 설정"
    ),
    "framedblocks.key.categories.framedblocks": "FramedBlocks",
    "framedblocks.key.update_cull": "컬링 캐시 갱신",
    "framedblocks.key.wipe_cache": "모델 캐시 비우기",
    "item.framedblocks.framed_axe": "프레임 도끼",
    "item.framedblocks.framed_blueprint": "프레임 설계도",
    "item.framedblocks.framed_hammer": "프레임 망치",
    "item.framedblocks.framed_key": "프레임 열쇠",
    "item.framedblocks.framed_reinforcement": "프레임 보강재",
    "item.framedblocks.framed_screwdriver": "프레임 드라이버",
    "item.framedblocks.framed_wrench": "프레임 렌치",
    "item.framedblocks.framing_saw_pattern": "프레임 절단기 형판",
    "item.framedblocks.phantom_paste": "유령 페이스트",
    "itemGroup.framed_blocks": "FramedBlocks",
    "label.framedblocks.jade.camo.details_prefix": "    %s",
    "label.framedblocks.jade.camo.double.one": "첫 번째 위장: %s",
    "label.framedblocks.jade.camo.double.two": "두 번째 위장: %s",
    "label.framedblocks.jade.camo.single": "위장: %s",
    "label.framedblocks.source_tooltip.anim_splitter.frames": "프레임",
    "label.framedblocks.source_tooltip.anim_splitter.texture": "텍스처",
    "msg.framedblocks.camo.blacklisted": "이 블록은 위장 재료로 사용할 수 없습니다!",
    "msg.framedblocks.camo.block_entity": (
        "블록 엔티티가 있는 블록은 프레임 블록에 넣을 수 없습니다!"
    ),
    "msg.framedblocks.camo.non_solid": (
        "태그가 없는 비고체 블록은 프레임 블록에 넣을 수 없습니다!"
    ),
    "msg.framedblocks.camo_application.camo.most_supported": (
        "블록 상호작용으로 위장을 적용할 수 있는 아이템 대부분을 지원합니다"
    ),
    "msg.framedblocks.feature.intangibility.disabled": (
        "비실체 기능이 비활성화되어 이 아이템은 아무 기능도 하지 않습니다!"
    ),
    "msg.framedblocks.frame_crafter.fail.camo_present": (
        "입력 아이템에 위장이 적용되어 있으면 안 됩니다"
    ),
    "msg.framedblocks.frame_crafter.fail.incorrect_additive_0": (
        "첫 번째 칸에 잘못된 첨가 재료가 있습니다"
    ),
    "msg.framedblocks.frame_crafter.fail.incorrect_additive_1": (
        "두 번째 칸에 잘못된 첨가 재료가 있습니다"
    ),
    "msg.framedblocks.frame_crafter.fail.incorrect_additive_2": (
        "세 번째 칸에 잘못된 첨가 재료가 있습니다"
    ),
    "msg.framedblocks.frame_crafter.fail.insufficient_additive_0": (
        "첫 번째 칸의 첨가 재료 수량이 부족합니다"
    ),
    "msg.framedblocks.frame_crafter.fail.insufficient_additive_1": (
        "두 번째 칸의 첨가 재료 수량이 부족합니다"
    ),
    "msg.framedblocks.frame_crafter.fail.insufficient_additive_2": (
        "세 번째 칸의 첨가 재료 수량이 부족합니다"
    ),
    "msg.framedblocks.frame_crafter.fail.material_lcm": (
        "이 결과물로 고르게 변환하기에는 입력 아이템이 너무 적습니다"
    ),
    "msg.framedblocks.frame_crafter.fail.material_value": "입력 재료가 부족합니다",
    "msg.framedblocks.frame_crafter.fail.missing_additive_0": (
        "첫 번째 칸에 첨가 재료가 없습니다"
    ),
    "msg.framedblocks.frame_crafter.fail.missing_additive_1": (
        "두 번째 칸에 첨가 재료가 없습니다"
    ),
    "msg.framedblocks.frame_crafter.fail.missing_additive_2": (
        "세 번째 칸에 첨가 재료가 없습니다"
    ),
    "msg.framedblocks.frame_crafter.fail.output_size": (
        "결과 수량이 최대 묶음 크기를 초과합니다"
    ),
    "msg.framedblocks.frame_crafter.fail.success": "제작 가능",
    "msg.framedblocks.frame_crafter.fail.unexpected_additive_0": (
        "첫 번째 칸에 예상하지 않은 첨가 재료가 있습니다"
    ),
    "msg.framedblocks.frame_crafter.fail.unexpected_additive_1": (
        "두 번째 칸에 예상하지 않은 첨가 재료가 있습니다"
    ),
    "msg.framedblocks.frame_crafter.fail.unexpected_additive_2": (
        "세 번째 칸에 예상하지 않은 첨가 재료가 있습니다"
    ),
    "msg.framedblocks.framing_saw.search": "검색...",
    "msg.framedblocks.framing_saw.transfer.invalid_recipe": "유효하지 않은 제작법",
    "msg.framedblocks.framing_saw.transfer.not_implemented": (
        "전송 기능이 구현되지 않아 아이템을 옮기지 않습니다"
    ),
    "msg.framedblocks.lock_state": "이 블록의 상태가 이제 %s 상태입니다",
    "msg.framedblocks.lock_state.locked": "잠김",
    "msg.framedblocks.lock_state.unlocked": "잠금 해제",
    "msg.framedblocks.powered_saw.status": "상태: ",
    "msg.framedblocks.powered_saw.status.no_match": "제작법이 일치하지 않음",
    "msg.framedblocks.powered_saw.status.no_recipe": "제작법 없음",
    "msg.framedblocks.powered_saw.status.ready": "준비됨",
    "msg.framedblocks.prism_offset.switch": ("프레임 망치로 때려 오프셋을 전환하세요"),
    "msg.framedblocks.split_line.switch": ("프레임 렌치로 때려 분할선 방향을 바꾸세요"),
    "tag.block.framedblocks.group.full": "전체 프레임 블록",
    "tag.item.c.tools.wrench": "렌치",
    "tag.item.framedblocks.disable_intangible": "비실체 비활성화",
    "title.framedblocks.framed_chest": "프레임 상자",
    "title.framedblocks.framed_hopper": "프레임 아이템 호퍼",
    "title.framedblocks.framed_secret_storage": "프레임 비밀 저장소",
    "title.framedblocks.framing_saw": "프레임 절단기",
    "title.framedblocks.powered_framing_saw": "전동 프레임 절단기",
    "title.framedblocks.powered_saw.target_block": "대상:",
}

STATIC_TRANSLATIONS.update(
    {
        "tooltip.framedblocks.camo_rotation.false": "대상 위장은 회전할 수 없습니다",
        "tooltip.framedblocks.camo_rotation.true": "대상 위장을 회전할 수 있습니다",
        "tooltip.framedblocks.copycat_style.set_copycat": (
            "프레임 망치로 때려 카피캣 형식 외형을 사용하세요"
        ),
        "tooltip.framedblocks.copycat_style.set_standard": (
            "프레임 망치로 때려 표준 외형을 사용하세요"
        ),
        "tooltip.framedblocks.copycat_style.use_copycat": (
            "대상 블록이 카피캣 형식 외형을 사용합니다"
        ),
        "tooltip.framedblocks.copycat_style.use_standard": (
            "대상 블록이 표준 외형을 사용합니다"
        ),
        "tooltip.framedblocks.frame_bg.set_camo": (
            "프레임 망치로 때려 위장을 배경으로 사용하세요"
        ),
        "tooltip.framedblocks.frame_bg.set_leather": (
            "프레임 망치로 때려 가죽을 배경으로 사용하세요"
        ),
        "tooltip.framedblocks.frame_bg.use_camo": (
            "프레임 아이템 액자가 위장을 배경으로 사용합니다"
        ),
        "tooltip.framedblocks.frame_bg.use_leather": (
            "프레임 아이템 액자가 가죽을 배경으로 사용합니다"
        ),
        "tooltip.framedblocks.framing_saw.have_item_none": "없음",
        "tooltip.framedblocks.framing_saw.have_x_but_need_y_item": ("%s 보유, %s 필요"),
        "tooltip.framedblocks.framing_saw.have_x_but_need_y_item_count": (
            "아이템 %s개 보유, 최소 %s개 필요"
        ),
        "tooltip.framedblocks.framing_saw.have_x_but_need_y_item_multi": (
            "%s 보유, %s 또는 표시된 대체 재료 필요"
        ),
        "tooltip.framedblocks.framing_saw.have_x_but_need_y_material_count": (
            "재료 %s 보유, 최소 %s 필요"
        ),
        "tooltip.framedblocks.framing_saw.have_x_but_need_y_tag": (
            "%s 보유, %s 중 하나 필요"
        ),
        "tooltip.framedblocks.framing_saw.loose_additive": (
            "첨가 재료로 제작한 아이템이며, 이 재료는 사라집니다"
        ),
        "tooltip.framedblocks.framing_saw.material": "재료 가치: %s",
        "tooltip.framedblocks.framing_saw.mode.crafting": "제작",
        "tooltip.framedblocks.framing_saw.mode.pattern_encode": "AE2 패턴 인코딩",
        "tooltip.framedblocks.framing_saw.output_count": (
            "결과 수량: %s, 최대 수량: %s"
        ),
        "tooltip.framedblocks.framing_saw.press_to_show": (
            "가능한 아이템을 모두 보려면 [%s] 키를 누르세요"
        ),
        "tooltip.framedblocks.framing_saw.use_intermediate": (
            "더 작은 블록을 중간 단계로 사용"
        ),
        "tooltip.framedblocks.is_waterloggable.false": (
            "블록 안에 물을 채울 수 없습니다."
        ),
        "tooltip.framedblocks.is_waterloggable.true": (
            "블록 안에 물을 채울 수 있습니다."
        ),
        "tooltip.framedblocks.lock_state": "상태: %s",
        "tooltip.framedblocks.make_waterloggable.false": (
            "프레임 망치로 때려 블록 안에 물을 채울 수 없게 하세요"
        ),
        "tooltip.framedblocks.make_waterloggable.true": (
            "프레임 망치로 때려 블록 안에 물을 채울 수 있게 하세요"
        ),
        "tooltip.framedblocks.one_way_window.clear_face": (
            "웅크린 채 프레임 렌치로 때려 투시 면을 지우세요"
        ),
        "tooltip.framedblocks.one_way_window.curr_face": "현재 투시 면: %s",
        "tooltip.framedblocks.one_way_window.dir.down": "아래쪽",
        "tooltip.framedblocks.one_way_window.dir.east": "동쪽",
        "tooltip.framedblocks.one_way_window.dir.north": "북쪽",
        "tooltip.framedblocks.one_way_window.dir.south": "남쪽",
        "tooltip.framedblocks.one_way_window.dir.up": "위쪽",
        "tooltip.framedblocks.one_way_window.dir.west": "서쪽",
        "tooltip.framedblocks.one_way_window.face.down": "아래쪽",
        "tooltip.framedblocks.one_way_window.face.east": "동쪽",
        "tooltip.framedblocks.one_way_window.face.none": "없음",
        "tooltip.framedblocks.one_way_window.face.north": "북쪽",
        "tooltip.framedblocks.one_way_window.face.south": "남쪽",
        "tooltip.framedblocks.one_way_window.face.up": "위쪽",
        "tooltip.framedblocks.one_way_window.face.west": "서쪽",
        "tooltip.framedblocks.one_way_window.face_abbr.down": "하",
        "tooltip.framedblocks.one_way_window.face_abbr.east": "동",
        "tooltip.framedblocks.one_way_window.face_abbr.none": "-",
        "tooltip.framedblocks.one_way_window.face_abbr.north": "북",
        "tooltip.framedblocks.one_way_window.face_abbr.south": "남",
        "tooltip.framedblocks.one_way_window.face_abbr.up": "상",
        "tooltip.framedblocks.one_way_window.face_abbr.west": "서",
        "tooltip.framedblocks.one_way_window.set_face": (
            "프레임 렌치로 때려 투시 면을 %s 방향으로 설정하세요"
        ),
        "tooltip.framedblocks.powered_saw.energy": "%s / %s FE",
        "tooltip.framedblocks.powered_saw.status.no_recipe": (
            "선택한 제작법이 없습니다. 대상 칸을 아무 프레임 블록으로 클릭하여 "
            "제작법을 선택하세요"
        ),
        "tooltip.framedblocks.prism_offset.false": (
            "삼각형 텍스처에 오프셋이 없습니다."
        ),
        "tooltip.framedblocks.prism_offset.true": (
            "삼각형 텍스처가 블록 절반만큼 어긋나 있습니다."
        ),
        "tooltip.framedblocks.reinforce_state": "블록이 %s 상태입니다.",
        "tooltip.framedblocks.reinforce_state.false": "보강되지 않음",
        "tooltip.framedblocks.reinforce_state.true": "보강됨",
        "tooltip.framedblocks.split_line.false": (
            "변형된 면의 분할선이 가파른 대각선을 따릅니다."
        ),
        "tooltip.framedblocks.split_line.true": (
            "변형된 면의 분할선이 완만한 대각선을 따릅니다."
        ),
        "tooltip.framedblocks.trapdoor_texture_rotation.false": (
            "다락문을 열 때 위장 텍스처가 회전하지 않습니다"
        ),
        "tooltip.framedblocks.trapdoor_texture_rotation.toggle": (
            "프레임 망치로 때려 텍스처 회전을 전환하세요"
        ),
        "tooltip.framedblocks.trapdoor_texture_rotation.true": (
            "다락문을 열 때 위장 텍스처가 회전합니다"
        ),
        "tooltip.framedblocks.y_slope": ("블록의 세로 경사면이 %s 면을 사용합니다."),
        "tooltip.framedblocks.y_slope.alt": (
            "블록의 가로 경사면이 %s 면을 사용합니다."
        ),
        "tooltip.framedblocks.y_slope.alt.toggle": (
            "프레임 렌치로 때려 %s 면으로 전환하세요"
        ),
        "tooltip.framedblocks.y_slope.front": "앞쪽",
        "tooltip.framedblocks.y_slope.horizontal": "가로",
        "tooltip.framedblocks.y_slope.side": "오른쪽",
        "tooltip.framedblocks.y_slope.toggle": (
            "프레임 렌치로 때려 %s 면으로 전환하세요"
        ),
        "tooltip.framedblocks.y_slope.vertical": "세로",
    }
)

QUEST_CORRECTIONS = {
    "quest.09E25B1CD6CABD5A.quest_desc": [
        "이 업그레이드는 라우터를 프레임 블록처럼 위장하게 합니다."
        "\\n\\n블록을 웅크린 채 우클릭하면 라우터의 외형을 그 블록으로 바꿉니다."
        "\\n\\n잃어버리지 않도록 조심하세요!"
    ],
    "quest.3E4B27759C973006.quest_desc": [
        "&l&6FramedBlocks&r는 가장 중요한 건축 모드라고 해도 과언이 아닙니다. "
        "&l&6FramedBlocks&r가 없는 모드팩이라면 저는 플레이하지 않을 정도예요! "
        "\\n\\n&l&6FramedBlocks&r는 블록 엔티티가 아닌 거의 모든 블록의 외형을 "
        "입힐 수 있는 프레임 블록을 제공합니다. 블록 엔티티란 제작대, 화로, "
        "농축기처럼 별도의 데이터를 가진 블록입니다. "
        "\\n\\n프레임은 세로 반 블록, 경사, 사분 블록 등 거의 모든 모양으로 "
        "만들 수 있습니다! "
        "\\n\\n&5네더라이트&r 계단이나 건초 더미 제작대, 정확한 각도의 건축물이 "
        "필요하다면 &l&6FramedBlocks&r를 사용해 보세요!"
    ],
    "quest.3E4B27759C973006.title": "&l&6FramedBlocks&r",
    "quest.4AE8D8826F894EC7.quest_desc": [
        "&l&5Domum Ornamentum&r은 &l&6FramedBlocks&r와 &l&bChipped&r를 합친 "
        "것과 비슷한 모드입니다! \\n\\n건축가의 절단기로 다양한 모양과 변형 블록을 "
        "만들 수 있습니다. \\n\\n먼저 문, 조명 같은 블록 그룹을 고르세요. "
        "\\n그다음 변형을 선택하세요. \\n마지막으로 완성품에 사용할 재료 블록을 "
        "넣으세요. 어떤 블록은 서로 다른 재료 두 개가 필요하고, 어떤 블록은 한 개만 "
        "필요합니다."
    ],
    "quest.4AE8D8826F894EC7.title": "&l&5Domum Ornamentum&r",
    "task.16EF7FF802D5A2BB.title": "FramedBlocks",
}

RELATED_QUEST_IDS = {
    "09E25B1CD6CABD5A",
    "3E4B27759C973006",
    "4AE8D8826F894EC7",
    "16EF7FF802D5A2BB",
}

ALLOWED_LATIN = {
    "AE",
    "Chipped",
    "Domum",
    "EMI",
    "FE",
    "FramedBlocks",
    "Jade",
    "JEI",
    "Ornamentum",
    "UV",
}

INTENTIONAL_SAME = {
    "framedblocks.key.categories.framedblocks",
    "itemGroup.framed_blocks",
    "label.framedblocks.jade.camo.details_prefix",
    "tooltip.framedblocks.one_way_window.face_abbr.none",
    "tooltip.framedblocks.powered_saw.energy",
}

BLOCK_OVERRIDES = {
    "block.framedblocks.framed_gate": "프레임 게이트",
    "block.framedblocks.framed_iron_gate": "프레임 철 게이트",
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽어요."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 객체가 아니에요: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 JSON을 안정된 형식으로 써요."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    """파일 SHA-256을 계산해요."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_jar(instance: Path) -> Path:
    """현재 인스턴스의 유일한 FramedBlocks JAR을 찾아요."""
    matches = sorted((instance / "mods").glob(JAR_PATTERN))
    if len(matches) != 1:
        raise FileNotFoundError(f"JAR 수가 1개가 아니에요: {matches}")
    return matches[0]


def read_jar_language(jar: Path) -> dict[str, object]:
    """JAR의 영어 언어 파일을 읽어요."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read("assets/framedblocks/lang/en_us.json"))
    if not isinstance(value, dict):
        raise TypeError(f"JAR 언어 파일이 객체가 아니에요: {jar.name}")
    return value


def translate_block_name(source: str) -> str:
    """복합 프레임 블록 이름을 일관된 모양 용어로 번역해요."""
    target = source
    for phrase, translated in sorted(
        BLOCK_PHRASES.items(), key=lambda row: len(row[0]), reverse=True
    ):
        target = target.replace(phrase, translated)
    for word, translated in sorted(
        BLOCK_WORDS.items(), key=lambda row: len(row[0]), reverse=True
    ):
        target = re.sub(rf"\b{re.escape(word)}\b", translated, target)
    residue = LATIN_WORD.findall(target)
    if residue:
        raise ValueError(
            f"블록 이름에 처리하지 않은 영어가 있어요: {source} -> {residue}"
        )
    return target


def translations(english: dict[str, object]) -> dict[str, object]:
    """436개 영어 키 전체를 원문 순서로 번역해요."""
    translated = dict(STATIC_TRANSLATIONS)
    for key, value in english.items():
        if key.startswith("block.") and isinstance(value, str):
            translated[key] = BLOCK_OVERRIDES.get(key, translate_block_name(value))
    missing = sorted(set(english) - set(translated))
    extra = sorted(set(translated) - set(english))
    if missing or extra:
        raise ValueError(f"번역 키 불일치: 누락={missing}, 초과={extra}")
    return {key: translated[key] for key in english}


def prepare() -> dict[str, object]:
    """현재 JAR 영어 원문과 표면 목록을 작업 폴더에 기록해요."""
    instance = resolve_source_root()
    jar = source_jar(instance)
    english = read_jar_language(jar)
    write_json(WORK_ROOT / "en_us.json", english)
    report = {
        "family": FAMILY,
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_mtime_ns": jar.stat().st_mtime_ns,
        "english_keys": len(english),
        "bundled_korean_keys": 0,
        "block_name_keys": sum(key.startswith("block.") for key in english),
        "other_display_keys": sum(not key.startswith("block.") for key in english),
        "status": "prepared",
    }
    write_json(WORK_ROOT / "inventory.json", report)
    return report


def build() -> dict[str, object]:
    """언어와 관련 FTB Quests 산출물을 만들어요."""
    english = load_json(WORK_ROOT / "en_us.json")
    korean = translations(english)
    write_json(WORK_ROOT / "ko_kr.json", korean)
    write_json(RESOURCE_OUTPUT, korean)
    write_json(
        WORK_ROOT / "candidate_sources.json",
        {key: "new_translation_required" for key in korean},
    )

    instance = resolve_source_root()
    quest_candidate = instance / "config/ftbquests/quests/lang/ko_kr.snbt"
    candidate_values = quest_snbt.parse_language_snbt(quest_candidate)
    merge_source = QUEST_OUTPUT if QUEST_OUTPUT.is_file() else quest_candidate
    merged = quest_snbt.merge_into_full_snbt(merge_source, QUEST_CORRECTIONS)
    QUEST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QUEST_OUTPUT.write_text(merged, encoding="utf-8")
    merged_values = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    for key, expected in QUEST_CORRECTIONS.items():
        if merged_values.get(key) != expected:
            raise ValueError(f"퀘스트 병합 결과가 달라요: {key}")
    quest_reused = sum(
        candidate_values.get(key) == value for key, value in QUEST_CORRECTIONS.items()
    )
    report = {
        "reviewed_language_keys": len(english),
        "existing_korean_reused": 0,
        "new_language_translations": len(english),
        "quest_reviewed_keys": len(QUEST_CORRECTIONS),
        "quest_existing_korean_reused": quest_reused,
        "quest_existing_korean_corrected": len(QUEST_CORRECTIONS) - quest_reused,
        "status": "complete",
    }
    write_json(WORK_ROOT / "translation_report.json", report)
    return report


def collect_references(instance: Path) -> dict[str, object]:
    """FTB Quests와 KubeJS에서 FramedBlocks 참조를 모아요."""
    suffixes = {
        ".cfg",
        ".js",
        ".json",
        ".kjs",
        ".properties",
        ".snbt",
        ".toml",
        ".txt",
        ".zs",
    }
    results: dict[str, object] = {
        "quest_references": [],
        "kubejs_references": [],
        "custom_name_candidates": [],
        "read_errors": [],
    }
    for label, root in (
        ("quest_references", instance / "config/ftbquests/quests/chapters"),
        ("kubejs_references", instance / "kubejs"),
    ):
        rows = results[label]
        custom_names = results["custom_name_candidates"]
        read_errors = results["read_errors"]
        if not all(
            isinstance(value, list) for value in (rows, custom_names, read_errors)
        ):
            raise TypeError("참조 보고서 목록 초기화에 실패했어요")
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                read_errors.append(f"{path}: {exc}")
                continue
            lines = text.splitlines()
            relative = path.relative_to(instance).as_posix()
            for index, line in enumerate(lines):
                if "framedblocks:" not in line.lower():
                    continue
                rows.append(f"{relative}:{index + 1}:{line.strip()}")
                window = "\n".join(lines[max(0, index - 8) : index + 9]).lower()
                if "custom_name" in window:
                    custom_names.append(f"{relative}:{index + 1}:{line.strip()}")
    return results


def audit_jar_surfaces(jar: Path) -> tuple[dict[str, object], list[str]]:
    """발전 과제, 별도 안내서와 호환 코드의 표시 경로를 확인해요."""
    errors = []
    advancement_files = []
    translated_keys = []
    direct_literals = []
    guide_json = []
    compat_counts: Counter[str] = Counter()
    compat_terms = {
        "ae2": ("ae2", "appliedenergistics"),
        "create": ("compat/create",),
        "jade": ("compat/jade",),
        "mekanism": ("mekanism",),
    }
    with ZipFile(jar) as archive:
        for internal in sorted(archive.namelist()):
            lower = internal.lower()
            if internal.endswith(".json") and (
                "guidebook" in lower or "/guide/" in lower or "patchouli" in lower
            ):
                guide_json.append(internal)
            for label, needles in compat_terms.items():
                if any(needle in lower for needle in needles):
                    compat_counts[label] += 1
            if "/advancement/" not in internal or not internal.endswith(".json"):
                continue
            advancement_files.append(internal)
            value = json.loads(archive.read(internal))
            display = value.get("display", {})
            if not isinstance(display, dict):
                continue
            for field in ("title", "description"):
                shown = display.get(field)
                if isinstance(shown, dict) and isinstance(shown.get("translate"), str):
                    translated_keys.append(shown["translate"])
                elif isinstance(shown, str):
                    direct_literals.append(
                        {"file": internal, "field": field, "value": shown}
                    )
    language = load_json(WORK_ROOT / "ko_kr.json")
    missing = sorted(set(translated_keys) - set(language))
    if missing:
        errors.append(f"발전 과제 번역 키가 누락됐어요: {missing}")
    if direct_literals:
        errors.append("발전 과제에 직접 영어 문구가 있어요")
    return {
        "advancement_files": advancement_files,
        "advancement_translation_keys": sorted(set(translated_keys)),
        "missing_advancement_keys": missing,
        "direct_advancement_text": direct_literals,
        "standalone_guide_json": guide_json,
        "compatibility_entry_counts": dict(compat_counts),
    }, errors


def audit() -> tuple[dict[str, object], list[str]]:
    """발전 과제, FTB Quests, KubeJS와 호환 표면을 감사해요."""
    instance = resolve_source_root()
    jar = source_jar(instance)
    errors = []
    jar_surfaces, jar_errors = audit_jar_surfaces(jar)
    errors.extend(jar_errors)
    references = collect_references(instance)
    read_errors = references.get("read_errors", [])
    if isinstance(read_errors, list):
        errors.extend(str(value) for value in read_errors)
    if references.get("custom_name_candidates"):
        errors.append("관련 참조 주변에 custom_name 후보가 있어요")

    english_quests = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean_quests = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    related_quest_keys = sorted(
        key
        for key in english_quests
        if any(identifier in key for identifier in RELATED_QUEST_IDS)
    )
    if set(related_quest_keys) != set(QUEST_CORRECTIONS):
        errors.append(
            "관련 FTB Quests 키 범위가 예상과 달라요: "
            f"{sorted(set(related_quest_keys) ^ set(QUEST_CORRECTIONS))}"
        )
    for key, expected in QUEST_CORRECTIONS.items():
        if korean_quests.get(key) != expected:
            errors.append(f"관련 퀘스트 교정값이 달라요: {key}")

    chapter = (
        instance / "config/ftbquests/quests/chapters/building_tips.snbt"
    ).read_text(encoding="utf-8")
    task_verified = (
        'id: "16EF7FF802D5A2BB"' in chapter
        and '"ftbfiltersystem:filter": "or(mod(framedblocks))"' in chapter
    )
    if not task_verified:
        errors.append("FramedBlocks 스마트 필터 Task 구조를 확인하지 못했어요")
    if korean_quests.get("task.16EF7FF802D5A2BB.title") != "FramedBlocks":
        errors.append("FramedBlocks 범주형 Task 제목이 확정값과 달라요")
    report = {
        "family": FAMILY,
        "jar": jar.name,
        "jar_surfaces": jar_surfaces,
        "references": references,
        "related_quest_keys": related_quest_keys,
        "related_quest_keys_corrected": len(QUEST_CORRECTIONS),
        "smart_filter_task_verified": task_verified,
        "ftbquests_display_work": "complete",
        "kubejs_display_work": "no_related_display_text",
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "surface_audit.json", report)
    return report, errors


def validate_preserved(key: str, source: str, target: str) -> list[str]:
    """자리표시자·서식·숫자·줄바꿈 보존을 확인해요."""
    errors = []
    for label, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식 코드", FORMAT_CODE),
    ):
        if Counter(pattern.findall(source)) != Counter(pattern.findall(target)):
            errors.append(f"{label} 불일치: {key}")
    if Counter(NUMBER.findall(source)) != Counter(NUMBER.findall(target)):
        errors.append(f"숫자 불일치: {key}")
    if source.count("\n") != target.count("\n"):
        errors.append(f"줄바꿈 불일치: {key}")
    return errors


def verify_quests(instance: Path) -> tuple[dict[str, object], list[str]]:
    """관련 FTB Quests 번역과 보존 요소를 확인해요."""
    errors = []
    english = quest_snbt.parse_language_snbt(
        instance / "config/ftbquests/quests/lang/en_us.snbt"
    )
    korean = quest_snbt.parse_language_snbt(QUEST_OUTPUT)
    latin_residue = {}
    for key, expected in QUEST_CORRECTIONS.items():
        if korean.get(key) != expected:
            errors.append(f"퀘스트 번역값이 달라요: {key}")
            continue
        errors.extend(quest_snbt.validate_value(key, english[key], expected))
        text = "\n".join(expected) if isinstance(expected, list) else expected
        residue = sorted(
            set(LATIN_WORD.findall(FORMAT_CODE.sub("", text.replace("\\n", " "))))
            - ALLOWED_LATIN
        )
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
    """현재 JAR과 언어·퀘스트 산출물의 완결성을 검증해요."""
    instance = resolve_source_root()
    jar = source_jar(instance)
    jar_english = read_jar_language(jar)
    english = load_json(WORK_ROOT / "en_us.json")
    korean = load_json(WORK_ROOT / "ko_kr.json")
    output = load_json(RESOURCE_OUTPUT)
    audit_report = load_json(WORK_ROOT / "surface_audit.json")
    translation_report = load_json(WORK_ROOT / "translation_report.json")
    errors = []
    untranslated = []
    latin_residue = {}
    if jar_english != english:
        errors.append("작업 영어가 현재 설치 JAR 영어와 달라요")
    if list(english) != list(korean):
        errors.append("한국어 키 또는 순서가 영어 원문과 달라요")
    if korean != output:
        errors.append("작업 한국어와 산출물이 달라요")
    for key in english.keys() & korean.keys():
        source = english[key]
        target = korean[key]
        if type(source) is not type(target):
            errors.append(f"자료형 불일치: {key}")
            continue
        if not isinstance(source, str) or not isinstance(target, str):
            continue
        errors.extend(validate_preserved(key, source, target))
        if source == target and key not in INTENTIONAL_SAME:
            untranslated.append(key)
        residue = sorted(set(LATIN_WORD.findall(target)) - ALLOWED_LATIN)
        if residue:
            latin_residue[key] = residue
    collisions = defaultdict(list)
    for key, target in korean.items():
        if isinstance(target, str) and key.startswith(("item.", "block.")):
            collisions[target].append(key)
    unexpected_collisions = {
        target: keys
        for target, keys in collisions.items()
        if len(keys) > 1 and len({english[key] for key in keys}) > 1
    }
    if untranslated:
        errors.append(f"영어와 같은 미번역 후보: {untranslated}")
    if latin_residue:
        errors.append(f"허용하지 않은 영문 잔여: {latin_residue}")
    if unexpected_collisions:
        errors.append(f"서로 다른 이름의 한국어 충돌: {unexpected_collisions}")
    if audit_report.get("status") != "complete":
        errors.append("표시 표면 감사가 완료되지 않았어요")
    quests, quest_errors = verify_quests(instance)
    errors.extend(quest_errors)
    report = {
        "family": FAMILY,
        "keys": len(english),
        "untranslated_candidates": untranslated,
        "latin_residue": latin_residue,
        "unexpected_name_collisions": unexpected_collisions,
        "quests": quests,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "language_validation.json", report)
    completion = {
        "family": FAMILY,
        "language_keys": len(english),
        "existing_korean_reused": 0,
        "new_or_corrected_language_translations": len(english),
        "ftbquests": {
            "reviewed_keys": quests["keys"],
            "existing_korean_reused": translation_report[
                "quest_existing_korean_reused"
            ],
            "corrected_keys": translation_report["quest_existing_korean_corrected"],
            "display_work": audit_report["ftbquests_display_work"],
        },
        "kubejs_references": len(
            audit_report.get("references", {}).get("kubejs_references", [])
        ),
        "output_files": [
            "resourcepacks/ATM10_Korean/assets/framedblocks/lang/ko_kr.json",
            "config/ftbquests/quests/lang/ko_kr.snbt",
        ],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    completion_path = WORK_ROOT / "family_completion.json"
    if completion_path.is_file():
        previous = load_json(completion_path)
        if "deployment" in previous:
            completion["deployment"] = previous["deployment"]
    write_json(completion_path, completion)
    return report, errors


def output_source(relative: str) -> Path:
    """적용 상대 경로를 저장소 산출물 경로로 바꿔요."""
    if relative.startswith("resourcepacks/"):
        return (
            active_output_root()
            / "resourcepack"
            / relative.removeprefix("resourcepacks/")
        )
    return active_output_root() / "overrides" / relative


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 스크립트의 백업·해시 결과를 완료 기록에 반영해요."""
    resolved = manifest_path.resolve()
    try:
        relative_manifest = resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError as exc:
        raise ValueError(f"프로젝트 밖의 적용 기록이에요: {resolved}") from exc
    manifest = load_json(resolved)
    completion_path = WORK_ROOT / "family_completion.json"
    completion = load_json(completion_path)
    expected = set(completion["output_files"])
    errors = []
    matched = []
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 기록 상태가 applied_and_verified가 아니에요")
    targets = manifest.get("targets")
    if not isinstance(targets, list):
        targets = []
        errors.append("적용 기록의 targets가 목록이 아니에요")
    for target in targets:
        if not isinstance(target, dict) or not isinstance(target.get("files"), list):
            continue
        files = {
            str(row.get("relative_path")): row
            for row in target["files"]
            if isinstance(row, dict) and row.get("relative_path") in expected
        }
        if set(files) != expected:
            continue
        for relative, row in files.items():
            source = output_source(relative)
            target_file = Path(str(row.get("target")))
            if not target_file.is_file() or sha256(target_file) != sha256(source):
                errors.append(f"적용 대상과 산출물 해시가 달라요: {relative}")
            if row.get("source_sha256") != row.get("after_sha256"):
                errors.append(f"적용 기록의 전후 해시가 달라요: {relative}")
        matched.append(target)
    if len(matched) != 1:
        errors.append(f"일치하는 적용 대상 기록 수가 1개가 아니에요: {len(matched)}")
    target = matched[0] if matched else {}
    deployment = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "target": target.get("target_root"),
        "changed_paths": target.get("changed_paths", []),
        "backup_manifest": relative_manifest,
        "errors": errors,
    }
    completion["deployment"] = deployment
    if errors:
        completion["status"] = "incomplete"
    write_json(completion_path, completion)
    return deployment, errors


def run_all() -> tuple[dict[str, object], list[str]]:
    """준비, 생성, 감사와 검증을 차례로 실행해요."""
    prepare_report = prepare()
    build_report = build()
    audit_report, audit_errors = audit()
    verify_report, verify_errors = verify()
    report = {
        "prepare": prepare_report,
        "build": build_report,
        "audit": audit_report,
        "verify": verify_report,
        "status": "complete"
        if not audit_errors and not verify_errors
        else "incomplete",
    }
    return report, audit_errors + verify_errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("prepare", "build", "audit", "verify", "record-deployment", "all"),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    errors = []
    if args.command == "prepare":
        report = prepare()
    elif args.command == "build":
        report = build()
    elif args.command == "audit":
        report, errors = audit()
    elif args.command == "verify":
        report, errors = verify()
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        report, errors = record_deployment(args.manifest)
    else:
        report, errors = run_all()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
