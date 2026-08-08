#!/usr/bin/env python3
"""Silent Gear 계열 검수본에 확정 번역과 교정 사항을 반영한다."""

from __future__ import annotations

import argparse
import json

from prepare_silentgear import WORK_ROOT
from silentgear_catalog import BATCHES


COMMANDS = {
    "command.silentgear.errors.notDamageable": "%s은(는) 손상될 수 없는 아이템입니다",
    "command.silentgear.errors.notMaterial": "%s은(는) 재료가 아닙니다",
    "command.silentgear.grade.list.header": "사용 가능한 등급:",
    "command.silentgear.grade.list.total": "합계: 등급 %s개",
    "command.silentgear.grade.remove.success": "%s에서 등급을 제거했습니다",
    "command.silentgear.grade.set.success": "%2$s에 %1$s 등급을 설정했습니다",
    "command.silentgear.help.damage": "손에 든 장비의 손상도를 설정합니다",
    "command.silentgear.help.damage.amount": "손상도를 지정한 값으로 설정합니다",
    "command.silentgear.help.damage.max": "손상도를 최댓값으로 설정합니다",
    "command.silentgear.help.damage.title": "Silent Gear 손상도 명령어:",
    "command.silentgear.help.footer": "자세한 내용은 /sgear <command> help를 사용하세요",
    "command.silentgear.help.grade": "손에 든 재료의 등급을 설정합니다",
    "command.silentgear.help.grade.list": "사용 가능한 모든 등급을 표시합니다",
    "command.silentgear.help.grade.set": "손에 든 재료의 등급을 설정합니다",
    "command.silentgear.help.grade.title": "Silent Gear 등급 명령어:",
    "command.silentgear.help.mats": "재료를 표시하거나 설명하고 내보냅니다",
    "command.silentgear.help.mats.describe": "재료의 세부 정보를 표시합니다",
    "command.silentgear.help.mats.dump": "재료를 TSV 파일로 내보냅니다",
    "command.silentgear.help.mats.list": "등록된 모든 재료를 표시합니다",
    "command.silentgear.help.mats.title": "Silent Gear 재료 명령어:",
    "command.silentgear.help.operatorSection": "--- 관리자 명령어 ---",
    "command.silentgear.help.parts": "부품을 표시하거나 설명하고 내보냅니다",
    "command.silentgear.help.parts.describe": "부품의 세부 정보를 표시합니다",
    "command.silentgear.help.parts.dump": "부품을 TSV 파일로 내보냅니다",
    "command.silentgear.help.parts.list": "등록된 모든 부품을 표시합니다",
    "command.silentgear.help.parts.title": "Silent Gear 부품 명령어:",
    "command.silentgear.help.permissionLevel": "현재 권한 레벨: %s",
    "command.silentgear.help.properties": "장비 속성을 보거나 다시 계산합니다",
    "command.silentgear.help.properties.info": "손에 든 장비의 속성을 표시합니다",
    "command.silentgear.help.properties.recalculate": "플레이어 장비의 능력치를 다시 계산합니다",
    "command.silentgear.help.properties.title": "Silent Gear 속성 명령어:",
    "command.silentgear.help.publicSection": "--- 공개 명령어 ---",
    "command.silentgear.help.random": "플레이어에게 무작위 장비를 지급합니다",
    "command.silentgear.help.random.give": "플레이어에게 무작위 장비를 지급합니다",
    "command.silentgear.help.random.title": "Silent Gear 무작위 장비 명령어:",
    "command.silentgear.help.starcharged": "손에 든 재료의 별빛 충전 단계를 설정합니다",
    "command.silentgear.help.starcharged.list": "사용 가능한 모든 별빛 충전 단계를 표시합니다",
    "command.silentgear.help.starcharged.set": "손에 든 재료의 별빛 충전 단계를 설정합니다",
    "command.silentgear.help.starcharged.title": "Silent Gear 별빛 충전 명령어:",
    "command.silentgear.help.title": "Silent Gear 명령어:",
    "command.silentgear.help.traits": "특성을 표시하거나 설명하고 내보냅니다",
    "command.silentgear.help.traits.describe": "특성의 세부 정보를 표시합니다",
    "command.silentgear.help.traits.dump_md": "특성을 Markdown 파일로 내보냅니다",
    "command.silentgear.help.traits.list": "등록된 모든 특성을 표시합니다",
    "command.silentgear.help.traits.title": "Silent Gear 특성 명령어:",
    "command.silentgear.mats.describe.categories": "범주: ",
    "command.silentgear.mats.describe.id": "ID: ",
    "command.silentgear.mats.describe.parent": "상위 재료: ",
    "command.silentgear.mats.describe.partTypes": "부품 유형: ",
    "command.silentgear.mats.describe.traitsHeader": "특성",
    "command.silentgear.mats.describe.type": "유형: ",
    "command.silentgear.mats.describe.type.compound": "복합",
    "command.silentgear.mats.describe.type.simple": "단순",
    "command.silentgear.mats.list.header": "등록된 재료:",
    "command.silentgear.mats.list.total": "합계: 재료 %s개",
    "command.silentgear.mats.materialNotFound": "재료를 찾을 수 없습니다",
    "command.silentgear.parts.describe.gearType": "장비 유형: ",
    "command.silentgear.parts.describe.id": "ID: ",
    "command.silentgear.parts.describe.materials": "재료: ",
    "command.silentgear.parts.describe.traitsHeader": "특성",
    "command.silentgear.parts.describe.type": "부품 유형: ",
    "command.silentgear.parts.describe.visible": "표시 여부: ",
    "command.silentgear.parts.describe.visible.no": "아니요",
    "command.silentgear.parts.describe.visible.yes": "예",
    "command.silentgear.parts.list.header": "등록된 부품:",
    "command.silentgear.parts.list.total": "합계: 부품 %s개",
    "command.silentgear.set_damage.max.success": "%1$s의 손상도를 최대로 설정했습니다(내구도 %2$s/%3$s)",
    "command.silentgear.set_damage.success": "%2$s의 손상도를 %1$s로 설정했습니다(내구도 %3$s/%4$s)",
    "command.silentgear.starcharged.list.header": "사용 가능한 별빛 충전 단계:",
    "command.silentgear.starcharged.list.total": "합계: 단계 %s개",
    "command.silentgear.starcharged.remove.success": "%s에서 별빛 충전을 제거했습니다",
    "command.silentgear.starcharged.set.success": "%2$s의 별빛 충전 단계를 %1$s로 설정했습니다",
    "command.silentgear.traits.describe.description": "설명: ",
    "command.silentgear.traits.describe.effectsHeader": "효과",
    "command.silentgear.traits.describe.id": "ID: ",
    "command.silentgear.traits.describe.maxLevel": "최대 레벨: ",
    "command.silentgear.traits.list.header": "등록된 특성:",
    "command.silentgear.traits.list.total": "합계: 특성 %s개",
}

MATERIAL_BOOK = {
    "gui.silentgear.material_book.allMaterials": "모든 재료",
    "gui.silentgear.material_book.allMaterials.byId": "모든 재료(ID순)",
    "gui.silentgear.material_book.allMaterials.byName": "모든 재료(이름순)",
    "gui.silentgear.material_book.byId": "ID순",
    "gui.silentgear.material_book.byName": "이름순",
    "gui.silentgear.material_book.byProperty": "속성별",
    "gui.silentgear.material_book.materialsByProperty": "재료(%s순)",
    "gui.silentgear.material_book.noProperties": "이 부품 유형에는 속성이 없습니다",
    "gui.silentgear.material_book.title": "재료 도감",
    "gui.silentgear.material_book.title2": "SilentChaos512 제작",
    "item.silentgear.material_book": "재료 도감",
}

MATERIALS = {
    "material.silentgear.azure_electrum.book_desc": "하늘빛 은으로 만든 합금입니다. 내구도는 낮지만 속도가 뛰어납니다. 제작대에서도 만들 수 있지만 합금 용광로가 더 효율적입니다.",
    "material.silentgear.azure_silver.book_desc": "하늘빛 은은 엔드에서 채굴할 수 있으며 하늘빛 호박금을 만드는 데 사용합니다.",
    "material.silentgear.barrier.book_desc": "일반적으로 얻을 수 없는 장난용 재료입니다.",
    "material.silentgear.blaze_gold.book_desc": "금과 블레이즈 가루로 만듭니다. 제작대에서도 만들 수 있지만 합금 용광로가 더 효율적입니다.",
    "material.silentgear.crimson_iron.book_desc": "진홍빛 철은 네더에서 채굴할 수 있으며 진홍빛 강철을 만드는 데 사용합니다.",
    "material.silentgear.crimson_steel.book_desc": "진홍빛 철로 만든 합금입니다. 전반적으로 강하고 불에 잘 견딥니다. 제작대에서도 만들 수 있지만 합금 용광로가 더 효율적입니다.",
    "material.silentgear.crude_alloy": "조잡한 합금",
    "material.silentgear.crude_alloy.book_desc": "조잡한 혼합기에서 만드는 복합 재료입니다. 완성된 혼합 재료는 '조잡한' 보정으로 약해지지만, 조잡한 혼합기는 구하기 쉽고 범주와 관계없이 모든 재료를 혼합할 수 있습니다.",
    "material.silentgear.crushed_shulker_shell.simple": "부서진 셜커 껍데기",
    "material.silentgear.dimerald.book_desc": "다이아몬드와 에메랄드를 결합한 보석입니다. 사용자 정의 복합 재료의 예시로 사용됩니다.",
    "material.silentgear.example.book_desc": "기술적인 이유로 일부 상황에서 자리표시자로 사용하는 재료입니다. 생존 모드에서는 얻을 수 없습니다.",
    "material.silentgear.gold.simple": "금",
    "material.silentgear.high_carbon_steel.book_desc": "사용자 정의 복합 재료의 예시로 사용됩니다.",
    "material.silentgear.hybrid_gem.book_desc": "재결정기에서 보석이나 가루를 혼합해 만드는 복합 재료입니다. 완성품의 속성은 사용한 재료에 따라 달라집니다.",
    "material.silentgear.leaves": "나뭇잎",
    "material.silentgear.leaves.simple": "나뭇잎",
    "material.silentgear.metal_alloy.book_desc": "합금 용광로에서 금속이나 가루를 혼합해 만드는 복합 재료입니다. 완성품의 속성은 사용한 재료에 따라 달라집니다.",
    "material.silentgear.mixed_fabric": "혼합 직물",
    "material.silentgear.mixed_fabric.book_desc": "재직조기에서 천, 섬유 또는 슬라임을 혼합해 만드는 복합 재료입니다. 완성품의 속성은 사용한 재료에 따라 달라집니다.",
    "material.silentgear.netherite.book_desc": "네더라이트는 바닐라 방식과 최대한 비슷하게 코팅 재료로만 사용됩니다. 네더라이트로 코팅한 다이아몬드 도구는 바닐라 네더라이트 도구와 거의 같습니다.",
    "material.silentgear.sheet_metal": "판금",
    "material.silentgear.sheet_metal.book_desc": "금속 프레스에서 만드는 재료로, 겉날개 제작에 적합합니다. 방어구도 만들 수 있지만 효과는 훨씬 떨어집니다.",
    "material.silentgear.super_alloy": "슈퍼 합금",
    "material.silentgear.super_alloy.book_desc": "슈퍼 혼합기에서 만드는 복합 재료입니다. 범주와 관계없이 모든 재료를 사용할 수 있으며 조잡한 혼합기와 달리 완성품에 불이익이 없습니다.",
    "material.silentgear.tyrian_steel.book_desc": "Silent Gear가 추가하는 가장 강한 기본 재료입니다. 합금 용광로에서만 만들 수 있습니다.",
    "material.silentgear.wood.simple": "나무",
}

TRAITS = {
    "trait.condition.silentgear.gear_type": "%s에만 적용",
    "trait.condition.silentgear.material_count": "재료 %d단위",
    "trait.condition.silentgear.material_ratio": "재료의 %d%%",
    "trait.condition.silentgear.primary_material": "주재료에만 적용",
    "trait.silentgear.adamant": "강인",
    "trait.silentgear.aquatic": "수생",
    "trait.silentgear.bending": "휘어짐",
    "trait.silentgear.bending.desc": "장비가 때때로 추가로 손상됩니다",
    "trait.silentgear.bounce": "탄성",
    "trait.silentgear.brittle.desc": "장비가 때때로 추가로 손상됩니다",
    "trait.silentgear.bulky.desc": "미구현, 테스트되지 않음",
    "trait.silentgear.confetti.desc": "큰 폭발이 좋아요",
    "trait.silentgear.crude.desc": "시너지를 감소시킵니다",
    "trait.silentgear.crushing": "압쇄",
    "trait.silentgear.crushing.desc": "장비가 손상될수록 방어력이 증가하거나 공격 피해가 감소합니다",
    "trait.silentgear.cure_wither": "시듦 해제",
    "trait.silentgear.eroded": "침식된",
    "trait.silentgear.eroded.desc": "장비가 손상될수록 채굴 속도가 증가하고 공격 피해가 감소합니다",
    "trait.silentgear.fiery": "불타는",
    "trait.silentgear.flame_ward": "화염 수호",
    "trait.silentgear.flame_ward.desc": "방어구 풀세트를 착용하면 화염 저항을 부여합니다",
    "trait.silentgear.flammable.desc": "불이 붙으면 손상되며 연료로 사용할 수 있습니다",
    "trait.silentgear.flexible.desc": "장비가 가끔 덜 손상됩니다",
    "trait.silentgear.fortunate.desc": "도구에 행운을 부여합니다",
    "trait.silentgear.gold_digger": "금 채굴꾼",
    "trait.silentgear.gold_digger.desc": "채굴할 때 가끔 조각 드롭량이 증가합니다",
    "trait.silentgear.hard.desc": "아이템이 손상될수록 채굴 속도가 증가하거나 원거리 피해가 감소합니다",
    "trait.silentgear.imperial": "제왕의",
    "trait.silentgear.jabberwocky": "재버워키",
    "trait.silentgear.jabberwocky.desc": "그때는 찬란했고, 미끈한 토브들이 / 와베 속에서 빙글거리며 구멍을 뚫었네",
    "trait.silentgear.light.desc": "방어구가 이동 속도를 증가시킵니다",
    "trait.silentgear.lucky": "운",
    "trait.silentgear.lustrous": "광휘",
    "trait.silentgear.magmatic.desc": "자동 제련",
    "trait.silentgear.malleable.desc": "장비가 때때로 덜 손상됩니다",
    "trait.silentgear.moonwalker": "문워커",
    "trait.silentgear.moonwalker.desc": "난 중력을 믿지 않아!",
    "trait.silentgear.multi_break": "다중 파괴",
    "trait.silentgear.multi_break.desc": "미구현",
    "trait.silentgear.organic": "유기적",
    "trait.silentgear.reach": "도달 거리",
    "trait.silentgear.refractive.desc": "사용하면 유령 조명을 설치합니다",
    "trait.silentgear.renew": "재생",
    "trait.silentgear.renew.desc": "시간이 지나면 아이템을 천천히 수리합니다",
    "trait.silentgear.rustic": "소박한",
    "trait.silentgear.sharp.desc": "내구도가 감소할수록 채굴 속도와 공격 피해가 증가합니다",
    "trait.silentgear.snow_walker": "가루눈 보행",
    "trait.silentgear.soft.desc": "도구가 손상될수록 채굴 속도가 감소합니다",
    "trait.silentgear.synergistic": "시너지",
    "trait.silentgear.turtle": "거북이",
    "trait.silentgear.void_ward": "공허 수호",
    "trait.silentgear.wind_blast": "돌풍",
}

CORRECTIONS = {
    "advancements.silentgear.mattock.title": "괭이에 미치다",
    "advancements.silentgear.grader_catalyst_2.description": "2단계 촉매제(블레이징 가루)를 얻으세요",
    "advancements.silentgear.grader_catalyst_2.title": "2단계 촉매제",
    "advancements.silentgear.grader_catalyst_3.description": "3단계 촉매제(반짝이는 가루)를 얻으세요",
    "advancements.silentgear.grader_catalyst_3.title": "3단계 촉매제",
    "advancements.silentgear.material_grader.description": "재료를 개선할 재료 등급기와 1단계 촉매제(빛나는 가루)를 만드세요",
    "advancements.silentgear.moonwalker.description": "문워커 특성이 있는 부츠를 신고 점프하세요!",
    "advancements.silentgear.repair_kit.description": "부서진 장비를 수리할 수리 키트(종류 무관)를 만드세요",
    "advancements.silentgear.template_board.title": "당장은 이걸로 충분해",
    "advancements.silentgear.upgrade_base.title": "업그레이드 베이스",
    "block.silentgear.paint_mixer": "페인트 혼합기",
    "block.silentgear.gear_smithing_table": "장비 제작대",
    "block.silentgear.metal_press": "금속 프레스",
    "block.silentgear.phantom_light": "유령 조명",
    "block.silentgear.raw_crimson_iron_block": "진홍빛 철 원석 블록",
    "category.silentgear.material_grader": "재료 등급기",
    "container.silentgear.alloy_forge": "합금 용광로",
    "container.silentgear.metal_press": "금속 프레스",
    "container.silentgear.paint_mixer": "페인트 혼합기",
    "gui.silentgear.material_grader.catalystTier": "촉매제 단계: %s",
    "gearType.silentgear.chestplate": "흉갑",
    "gearType.silentgear.part": "부품",
    "item.silentgear.chestplate": "흉갑",
    "item.silentgear.chestplate.nameProper": "%s 흉갑",
    "item.silentgear.chestplate_plates": "흉갑 판",
    "item.silentgear.chestplate_plates.nameProper": "%s 흉갑 판",
    "item.silentgear.compound_part.part_name": "장비 부품: %s",
    "item.silentgear.crude_tool_parts": "조잡한 도구 부품",
    "item.silentgear.blueprint.necklace.desc": "나무줄기에도 맞고, 어쩌면 목에도 맞습니다",
    "item.silentgear.blueprint.pickaxe.desc": "가장 친한 친구",
    "item.silentgear.blueprint.shield.desc": "더 많이 막습니다",
    "item.silentgear.fragment.hint": "제작대에서 여덟(8)개를 합치세요",
    "item.silentgear.lining": "안감",
    "item.silentgear.lining.nameProper": "%s 안감",
    "item.silentgear.magnetic_upgrade": "자성 업그레이드",
    "item.silentgear.mod_kit.can_paint_and_remove": "이 유형의 부품을 %1$s 및 %2$s할 수 있습니다",
    "item.silentgear.mod_kit.can_paint_or_remove": "이 유형의 부품을 %s할 수 있습니다",
    "item.silentgear.mod_kit.no_actions": "이 유형의 부품은 변경할 수 없습니다",
    "item.silentgear.mod_kit.paint": "도색",
    "item.silentgear.mod_kit.remove": "제거",
    "item.silentgear.mod_kit.keyHint": "%s 와(과) %s로 부품 유형을 전환합니다",
    "item.silentgear.repair_kit.material": "- %s: %s",
    "item.silentgear.paint": "페인트",
    "item.silentgear.paint.color": "색상: %s",
    "item.silentgear.sinew.desc": "일부 동물을 처치하면 가끔 떨어집니다",
    "part.silentgear.type": "부품 유형: %s",
    "part.silentgear.type.binding": "결속재",
    "part.silentgear.type.lining": "안감",
    "part.silentgear.type.main": "주재료",
    "part.silentgear.type.rod": "도구 자루",
    "part.silentgear.type.setting": "보석 세팅",
    "property.silentgear.additive.warning": "이 재료는 첨가제이므로 이 부품 유형의 다른 재료와 함께 사용해야 합니다.",
    "property.silentgear.armor_toughness": "방어 강도",
    "property.silentgear.attack_damage": "공격 피해",
    "property.silentgear.attack_reach": "공격 도달 거리",
    "property.silentgear.block_reach": "블록 도달 거리",
    "property.silentgear.charging_value": "충전량",
    "property.silentgear.enchantment_value": "마법 부여 수치",
    "property.silentgear.harvest_speed": "채굴 속도",
    "property.silentgear.harvest_tier": "채굴 등급",
    "property.silentgear.magic_armor": "마법 방어력",
    "property.silentgear.magic_damage": "마법 피해",
    "property.silentgear.ranged_damage": "원거리 피해",
    "misc.silentgear.harvestLevel": "채굴 레벨: %s",
    "misc.silentgear.graderCatalyst": "등급기 촉매제(단계 %d)",
    "misc.silentgear.broken": "망가뜨렸습니다!",
    "misc.silentgear.notifyOnBreak": "%s이(가) 부서졌습니다. 수리해야겠네요... 수리 키트를 만들어 보세요.",
    "misc.silentgear.starlightChargerCataylst": "별빛 충전기 촉매제(단계 %d)",
    "key.silentgear.cycle.back": "이전 항목",
    "key.silentgear.cycle.next": "다음 항목",
    "key.silentgear.cycleMaterialInfo": "재료 정보 전환",
    "silentgear.configuration.allow_conversion_recipes": "변환 제작법 허용",
    "silentgear.configuration.azure": "하늘빛 재료",
    "silentgear.configuration.compounds": "복합 재료(합금)",
    "silentgear.configuration.crude_mixer": "조잡한 혼합기",
    "silentgear.configuration.material_book": "재료 도감",
    "silentgear.configuration.property_multiplier": "속성 배율",
    "silentgear.configuration.repair_kits": "수리 키트",
    "silentgear.configuration.break_down_parts_with_gear": "장비와 함께 부품 분해",
    "silentgear.configuration.can_charge_parts": "부품 충전 가능",
    "silentgear.configuration.can_grade_parts": "부품 등급 지정 가능",
    "silentgear.configuration.destroy_swapped_parts": "교체된 부품 파괴",
    "silentgear.configuration.gear": "장비",
    "silentgear.configuration.part_loss_rate": "부품 손실률",
    "silentgear.configuration.show_part_tooltips": "부품 툴팁 표시",
    "silentgear.configuration.spawn_with_material_book": "재료 도감을 가진 채 시작",
    "jei.silentgear.katana.desc": "일반 검보다 무겁고 강한 검입니다.",
    "jei.silentgear.blueprint.desc": "청사진과 템플릿은 도구 머리와 방어구를 만드는 데 사용합니다. 청사진은 무한히 재사용할 수 있지만 템플릿은 일회용입니다. 장비 제작대에서는 서로 다른 재료를 섞을 수 있으며, 그 밖의 제작 방식에서는 모든 재료가 같아야 합니다. 최종 아이템 제작 방법은 청사진이나 템플릿의 툴팁에서 확인하세요.",
    "jei.silentgear.fishing_rod.desc": "낚싯대입니다. 뭘 더 바라시나요?",
    "jei.silentgear.knife.desc": "단검과 비슷합니다. 내구도는 더 높지만 피해와 속도는 낮습니다.",
    "jei.silentgear.machete.desc": "검, 도끼, 낫의 기능을 지닌 다용도 칼날이지만 검으로 사용할 때 가장 좋습니다. 일반 검보다 약간 빠르고 약합니다. 낫처럼 식물을 넓게 제거할 수 있지만 범위는 더 작습니다.",
    "jei.silentgear.material_category.not_separator": " 제외 ",
    "jei.silentgear.mattock.desc": "경작하고 땅을 파며 나무까지 벨 수 있는 만능 농사 도구입니다. 삽이나 도끼보다 조금 느리지만 내구도는 더 높으며, 괭이가 필요한 작업에도 사용할 수 있습니다.",
    "jei.silentgear.paxel.desc": "곡괭이, 도끼, 삽의 기능을 합친 도구입니다. 내구도는 조금 높지만 채굴 속도와 마법 부여 수치가 조금 낮습니다.",
    "jei.silentgear.saw.desc": "블록 하나를 부수어 나무 전체를 벱니다. 나무로 인식되려면 원목과 나뭇잎에 올바른 태그가 있어야 합니다.",
    "jei.silentgear.sword.desc": "피해와 속도가 균형 잡힌 전형적인 검입니다. 코등이는 제작에 사용한 두 번째 재료의 모습을 따릅니다.",
    "jei.silentgear.tool_head.desc": "도구 머리, 칼날, 활대 등 다양한 부품입니다! 청사진이나 템플릿과 필요한 수의 주 도구 재료로 제작하며, 도구와 무기의 핵심이 됩니다. 자세한 내용은 청사진이나 템플릿의 툴팁에서 확인하세요.",
    "subtitles.item.silentgear.gear_damaged": "장비 손상",
    "trait.silentgear.flammable.itemDestroyed": "%s이(가) 불타 사라졌습니다",
    "trait.silentgear.fiery.desc": "무기에 발화 또는 화염을 부여합니다",
}

GEMS = {
    "gem.silentgems.black_diamond": "검은 다이아몬드",
    "gem.silentgems.carnelian": "홍옥수",
    "gem.silentgems.citrine": "황수정",
    "gem.silentgems.garnet": "석류석",
    "gem.silentgems.heliodor": "헬리오도르",
    "gem.silentgems.iolite": "아이올라이트",
    "gem.silentgems.kyanite": "남정석",
    "gem.silentgems.moldavite": "몰다바이트",
    "gem.silentgems.opal": "오팔",
    "gem.silentgems.pearl": "진주",
    "gem.silentgems.peridot": "페리도트",
    "gem.silentgems.rose_quartz": "장미 석영",
    "gem.silentgems.ruby": "루비",
    "gem.silentgems.sapphire": "사파이어",
    "gem.silentgems.tanzanite": "탄자나이트",
    "gem.silentgems.topaz": "토파즈",
    "gem.silentgems.turquoise": "터키석",
    "gem.silentgems.white_diamond": "하얀 다이아몬드",
    "item.silentgems.fishy_stew": "생선 스튜",
    "item.silentgems.fluffy_fabric": "푹신한 직물",
    "item.silentgems.fluffy_puff": "푹신한 솜뭉치",
    "item.silentgems.iron_potato": "철 감자",
    "item.silentgems.iron_potato.desc": "타협을 모르는 감자",
    "item.silentgems.meaty_stew": "고기 스튜",
    "item.silentgems.potato_on_a_stick": "막대기에 꽂은 감자",
    "item.silentgems.potato_on_a_stick.desc": "전설은 계속됩니다",
    "item.silentgems.raw_silver": "은 원석",
    "item.silentgems.soul_gem": "%s영혼 보석",
    "itemGroup.silentgems": "Silent's Gems",
    "misc.silentgems.harvestLevel.4": "하늘빛 은",
    "silentgems.configuration.features": "기능",
    "silentgems.configuration.rabbitsProduceCoffee": "토끼가 커피 생산",
    "silentgems.configuration.rabbitCoffeeDelay": "토끼 커피 생산 간격",
    "trait.silentgems.freeze_resistant.desc": "동결 피해가 감소합니다",
    "trait.silentgems.power.desc": "공격 피해를 증가시킵니다",
    "trait.silentgems.step_up": "높은 턱 넘기",
}

DATA_ONLY = {
    "silentgear": {
        "trait.silentgear.dulling": "무뎌짐",
        "trait.silentgear.dulling.desc": "손상될수록 채굴 속도와 공격 피해가 감소합니다",
        "trait.silentgear.flutter": "나풀거림",
        "trait.silentgear.flutter.desc": "안전 낙하 거리를 증가시킵니다",
        "trait.silentgear.red_card.desc": "장비가 바닐라 아이템처럼 완전히 파괴될 수 있습니다",
    },
    "silentgems": {
        "material.silentgems.reinforced_gold": "강화된 금",
        "material.silentgems.reinforced_silver": "강화된 은",
    },
}

METALWORKS = {
    "entity.productivebees.uru_metal_bee": "우루 금속 벌",
    "item.sgearmetalworks.helmet_cast": "투구 주형",
    "item.sgearmetalworks.ring_cast": "반지 주형",
    "item.sgearmetalworks.slingshot_cast": "새총 주형",
    "item.sgearmetalworks.tool_rod_cast": "도구 자루 주형",
    "tooltip.sgearmetalworks.blueprint": "모든 금속 및 보석 도구 부품은 Productive Metalworks의 주조 공장에서 주조해야 합니다.",
}


def translate(batch: str) -> dict[str, int | str]:
    """한 네임스페이스의 검수본에 확정 번역을 적용한다."""
    path = WORK_ROOT / batch / "ko_kr.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    before = dict(data)
    updates: dict[str, str] = {}
    if batch == "silentgear":
        for group in (COMMANDS, MATERIAL_BOOK, MATERIALS, TRAITS, CORRECTIONS):
            updates.update(group)
    elif batch == "silentgems":
        updates.update(GEMS)
    elif batch == "sgearmetalworks":
        updates.update(METALWORKS)
    data_only = DATA_ONLY.get(batch, {})
    unknown = sorted(set(updates) - set(data))
    if unknown:
        raise KeyError(f"존재하지 않는 번역 키: {unknown}")
    data.update(updates)
    data.update(data_only)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "namespace": batch,
        "keys": len(data),
        "changed": sum(before.get(key) != value for key, value in data.items()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", choices=BATCHES + ("all",))
    args = parser.parse_args()
    selected = BATCHES if args.batch == "all" else (args.batch,)
    print(
        json.dumps(
            [translate(batch) for batch in selected], ensure_ascii=False, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
