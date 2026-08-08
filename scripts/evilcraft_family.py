#!/usr/bin/env python3
"""EvilCraft 모드군의 언어와 FTB Quests 작업본을 검수한다."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from local_paths import PROJECT_ROOT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/evilcraft"

TERM_REPLACEMENTS = (
    ("복수심에 불타는 영혼", "복수령"),
    ("복수 정령", "복수령"),
    ("어둠의 힘 보석", "다크 파워 젬"),
    ("검은 힘 보석", "다크 파워 젬"),
    ("어둠의 보석", "다크 젬"),
    ("어둠 보석", "다크 젬"),
    ("검은 보석", "다크 젬"),
    ("분쇄된 다크 젬", "분쇄된 다크 젬"),
    ("어둠 광석", "다크 광석"),
    ("검은 광석", "다크 광석"),
    ("검은 블록", "다크 블록"),
    ("검은 피의 벽돌", "다크 블러드 벽돌"),
    ("검은 피 벽돌", "다크 블러드 벽돌"),
    ("검은 벽돌", "다크 벽돌"),
    ("어둠 막대기", "다크 막대기"),
    ("검은 막대기", "다크 막대기"),
    ("이블크래프트", "EvilCraft"),
    ("garmonbozia", "가몬보지아"),
    ("Garmonbozia", "가몬보지아"),
)

LANGUAGE_OVERRIDES: dict[str, dict[str, str]] = {
    "evilcraft": {
        "block.evilcraft.blood_stain.info": "개체가 추락사할 때 생기는 피 얼룩입니다.",
        "block.evilcraft.undead_slab": "언데드 반 블록",
        "block.evilcraft.spirit_furnace.info": (
            "복수령을 태워 해당 몹의 드롭 아이템을 얻습니다."
        ),
        "block.evilcraft.dark_tank.info": (
            "다른 탱크와 제작 격자에서 조합해 용량을 늘릴 수 있습니다. "
            "Shift + 우클릭으로 자동 공급을 전환합니다."
        ),
        "block.evilcraft.sanguinary_pedestal_1": "강화 혈액 받침대",
        "block.evilcraft.blood_waxed_coal_block": "피로 왁스 처리한 석탄 블록",
        "block.evilcraft.entangled_chalice": "얽힌 성배",
        "block.evilcraft.eternal_water.auto_output.enabled": "자동 출력 활성화",
        "block.evilcraft.eternal_water.auto_output.disabled": "자동 출력 비활성화",
        "item.evilcraft.garmonbozia": "가몬보지아",
        "item.evilcraft.flesh_werewolf": "늑대인간 살점",
        "item.evilcraft.flesh_humanoid": "인간형 살점",
        "item.evilcraft.flesh_rejuvenated": "되살아난 살점",
        "item.evilcraft.weather_container": "날씨 용기",
        "item.evilcraft.blood_pearl_of_teleportation": "피 순간이동 진주",
        "item.evilcraft.blood_extractor.info": (
            "몹을 처치할 때 인벤토리에 소지하세요.\n"
            "Shift + 우클릭으로 추출 또는 자동 공급을 전환합니다."
        ),
        "item.evilcraft.burning_gem_stone.info": (
            "복수령에게 받는 피해를 허기 소모로 대신합니다."
        ),
        "item.evilcraft.creative_blood_drop.info": (
            "크리에이티브 모드 전용 아이템으로, 피를 무한히 빼내거나 채울 수 있습니다."
        ),
        "item.evilcraft.promise_tier_1.info": (
            "기계 등급 업그레이드입니다. 낮은 등급 조합법에도 사용할 수 있으며 "
            "탱크 용량이 2배가 됩니다."
        ),
        "item.evilcraft.promise_tier_2.info": (
            "기계 등급 업그레이드입니다. 낮은 등급 조합법에도 사용할 수 있으며 "
            "탱크 용량이 4배가 됩니다."
        ),
        "item.evilcraft.promise_tier_3.info": (
            "기계 등급 업그레이드입니다. 낮은 등급 조합법에도 사용할 수 있으며 "
            "탱크 용량이 8배가 됩니다."
        ),
        "item.evilcraft.bowl_of_promises_tier0": "약속의 그릇: 등급 0",
        "item.evilcraft.bowl_of_promises_tier1": "약속의 그릇: 등급 1",
        "item.evilcraft.bowl_of_promises_tier2": "약속의 그릇: 등급 2",
        "item.evilcraft.bowl_of_promises_tier3": "약속의 그릇: 등급 3",
        "item.evilcraft.sceptre_of_thunder.info": (
            "사용하면 번개를 내리치며, 한 번만 사용할 수 있습니다."
        ),
        "item.evilcraft.veined_scribing_tools": "핏줄 필기 도구",
        "item.evilcraft.blood_wand_cap": "피 지팡이 마개",
        "item.Wand.blood.cap": "피 테두리",
        "item.evilcraft.effortless_ring": "수월한 반지",
        "item.evilcraft.biome_extract.info": (
            "대상 지역을 병에 담긴 생물 군계로 바꿉니다. 원하는 생물 군계에 설치한 "
            "환경 축전기에서 제작할 수 있습니다."
        ),
        "item.evilcraft.environmental_accumulation_core": "환경 축적 코어",
        "item.evilcraft.environmental_accumulation_core.info": (
            "일반 환경 축전기를 부수면 얻을 수 있습니다."
        ),
        "item.evilcraft.primed_pendant": "충전된 펜던트",
        "item.evilcraft.spikey_claws": "뾰족한 발톱",
        "item.evilcraft.powerable.set_power": "위력을 %s로 설정",
        "item.evilcraft.powerable.info.power": "위력: %s",
        "item.evilcraft.powerable.info": "Shift + 우클릭으로 위력 단계를 변경합니다.",
        "item.evilcraft.poisonous_libelle_spawn_egg": "독성 리벨레 생성 알",
        "entity.evilcraft.poisonous_libelle": "독성 리벨레",
        "enchantment.evilcraft.unusing": "사용 방지",
        "biome.evilcraft.degraded": "황폐화됨",
        "advancement.evilcraft.evil_source.desc": (
            "동물에게 어둠에 물든 사과를 먹여 생긴 변칙점에 책을 던져 "
            "어둠의 기원 사본을 얻으세요."
        ),
        "advancement.evilcraft.first_age": "제1시대",
        "advancement.evilcraft.first_age.desc": (
            "다크 젬을 채굴하여 첫 번째 악의 시대의 기원을 발견하세요."
        ),
        "advancement.evilcraft.second_age": "제2시대",
        "advancement.evilcraft.second_age.desc": (
            "피 추출기를 제작하여 두 번째 악의 시대를 시작하세요."
        ),
        "advancement.evilcraft.power_crafting": "고급 제작",
        "advancement.evilcraft.power_crafting.desc": (
            "고급 제작기를 제작하세요. 제작기로 제작기를 만드는 셈이군요!"
        ),
        "broom.parts.evilcraft.rod_endstone": "엔드 돌 막대",
        "broom.parts.evilcraft.brush_bare": "맨 솔",
        "broom.parts.evilcraft.brush_wheat": "밀 솔",
        "broom.parts.evilcraft.brush_wool": "양털 솔",
        "broom.parts.evilcraft.brush_feather": "깃털 솔",
        "broom.parts.evilcraft.brush_twig": "잔가지 솔",
        "broom.parts.evilcraft.brush_leaves": "나뭇잎 솔",
        "broom.parts.evilcraft.brush_honey": "꿀 솔",
        "broom.parts.evilcraft.type.brush": "솔",
        "broom.modifiers.evilcraft.type.damage": "충돌 피해",
        "broom.modifiers.evilcraft.type.particles": "입자",
        "broom.modifiers.evilcraft.type.icy": "냉기",
        "broom.modifiers.evilcraft.type.sticky": "끈적임",
        "key.categories.evilcraft": "EvilCraft",
        "broom.evilcraft.shiftinfo": "<Shift로 빗자루 정보 보기>",
        "broom.parts.evilcraft.shiftinfo": "<Shift로 빗자루 부품 정보 보기>",
        "broom.modifiers.evilcraft.shiftinfo": "<Shift로 빗자루 정보 보기>",
        "block.evilcraft.entangled_chalice.info": (
            "얽힌 성배의 내용물은 어디에서나 공유됩니다.\\n"
            "Shift + 우클릭으로 전방위 공급을 전환합니다."
        ),
        "item.evilcraft.kineticator.info": (
            "Shift + 우클릭으로 끌어당기기를 전환합니다.\\n"
            "우클릭으로 범위를 변경합니다."
        ),
        "item.evilcraft.kineticator_repelling.info": (
            "Shift + 우클릭으로 밀어내기를 전환합니다.\\n"
            "우클릭으로 범위를 변경합니다."
        ),
        "item.evilcraft.vengeance_ring.info": (
            "복수령을 끌어들이거나 소환할 수 있습니다.\\n"
            "Shift + 우클릭으로 강화를 전환합니다."
        ),
        "death.attack.evilcraft.broom.player": (
            "%1$s이(가) 빗자루를 탄 %s에게 치여 죽었습니다."
        ),
        "info_book.evilcraft.structure": "&o구조&r",
        "info_book.evilcraft.preface.text1": (
            "이 세계에는 눈에 보이는 것보다 훨씬 많은 것이 숨어 있는 듯합니다. 이 책은 "
            "그 어둠 속에서 얻은 지식을 기록한 것입니다. 이 세계의 생물과 공존하는 "
            "어두운 방법을 알아냈습니다. ‘&o이것이 어떤 악을 불러올까?&r’라고 묻자, "
            "마음속 어두운 목소리는 ‘&o악은 어디에나 숨어 있다&r’고 답했습니다. "
            "어리석은 주민과 좀비는 결코 이해하지 못할 비밀을 몇 가지 발견했습니다."
        ),
        "info_book.evilcraft.preface.text2": (
            "이 세계에는 여러 마법이 있지만, &4피&0로 다루는 힘은 사뭇 다릅니다. "
            "&4피&0를 얻으려고 제 몸에 상처를 내는 사람도 보았지만, 저는 다른 일을 위해 "
            "힘을 아껴 두는 편이 낫겠습니다..."
        ),
        "info_book.evilcraft.structure.text1": (
            "이 책은 악의 역사를 두 시대로 나누어 설명합니다. 제가 이 세계에 오기 "
            "전의 모든 것을 &1제1시대&0, 제 평생의 연구를 &1제2시대&0로 분류했습니다."
        ),
        "info_book.evilcraft.structure.text2": (
            "아래쪽 화살표를 클릭해 페이지를 넘길 수 있으며, Shift를 누른 채 클릭하면 "
            "한 페이지가 아니라 섹션 전체를 넘깁니다. 큰 섹션의 첫 페이지에는 하위 "
            "항목으로 바로 이동하는 목차가 있습니다. 조합법의 아이템을 클릭하면 해당 "
            "설명으로 이동합니다. 왼쪽 위 버튼은 상위 섹션으로, 오른쪽 위 버튼은 직전에 "
            "보았던 페이지로 돌아갑니다."
        ),
        "info_book.evilcraft.first_age.new_world.introduction.text": (
            "최근 낯설고 기묘한 것들을 여럿 발견했습니다. 모두 불길한 기운을 풍기지만, "
            "곁에 오래 있을수록 점차 익숙해지는 느낌입니다... 당장은 쓸모없어 보여도 "
            "다른 곳에 활용할 방법을 찾아낼 수 있을 것입니다."
        ),
        "info_book.evilcraft.first_age.new_world.evil_dungeon.text": (
            "동굴을 탐험하다 보면 바닥 곳곳에 &4피&0가 흩어진 음침한 방을 만나곤 "
            "합니다. 이 &4피&0 흔적은 던전의 수많은 몹과 싸운 옛 탐험가들이 남긴 듯합니다."
        ),
        "info_book.evilcraft.first_age.new_world.dark_temple": "다크 신전",
        "info_book.evilcraft.first_age.new_world.dark_temple.text1": (
            "이 세계에는 환경의 힘을 아이템에 주입할 수 있었던 고대 문명이 세운 "
            "구조물이 있습니다. 이 과정을 반복할수록 자연의 균형이 무너지는 듯하며, "
            "어쩌면 그 문명이 사라진 까닭도 이것일지 모릅니다..."
        ),
        "info_book.evilcraft.first_age.new_world.dark_temple.text2": (
            "&1다크 젬&0으로 &1유리병&0을 강화해 날씨를 담는 &1날씨 용기&0를 "
            "만들었습니다. 이것을 신전 중심부에 던지면 현재 날씨가 병에 담깁니다."
        ),
        "info_book.evilcraft.first_age.new_world.weather_container_benefits": (
            "날씨 용기 활용법"
        ),
        "info_book.evilcraft.first_age.new_world.biome_extract.text2": (
            "&1환경 축전기&0에 특수한 &1생물 군계 추출 병&0을 넣으면 기계가 설치된 "
            "곳의 &1생물 군계&0를 병에 담습니다. 이 병을 땅에 던지면 주변 지역이 "
            "담긴 생물 군계로 바뀝니다."
        ),
        "info_book.evilcraft.first_age.new_world.biome_extract.text3": (
            "&1환경 축전기&0는 시간이 지나면서 주변 생물 군계를 황폐화하므로, 결국 "
            "쓸모없는 생물 군계만 병에 담게 됩니다. 나쁜 영향 없이 &1생물 군계 "
            "추출물&0을 만드는 다른 방법이 있다면 좋을 텐데요..."
        ),
        "info_book.evilcraft.first_age.new_world.libelle.text": (
            "이 세계에서 거대한 잠자리처럼 생긴 새로운 생물을 발견했습니다. 낮에는 "
            "비교적 평화롭지만 가까이 다가가면 자신을 지키려고 독을 겁니다. 밤에는 "
            "고대의 악에 지배되어 앞을 가로막는 모든 것을 공격합니다. 다행히 밤마다 "
            "저를 찾아와 독을 거는 것 말고는 특별한 무기가 없습니다. 몇 마리를 처치해 "
            "독주머니를 얻었고, 네 개를 &1물 양동이&0에 넣으면 독이 잘 우러난다는 "
            "사실을 알아냈습니다. &l독이 든 감자&r로도 같은 일을 할 수 있습니다. "
            "악의 소굴을 지킬 때 유용하겠군요... 아니, 집 말입니다. 평범한 잠자리와 "
            "구별하려고 잠자리를 뜻하는 네덜란드어에서 이름을 따 ‘리벨레’라고 불렀습니다."
        ),
        "info_book.evilcraft.first_age.new_world.werewolf.text": (
            "여행 중 머문 마을에서 다크 광석에 유난히 관심이 많은 사람을 만났습니다. "
            "우리는 몇 시간 동안 이야기를 나누고 해가 질 때까지 물건을 거래했습니다. "
            "그는 자기 집에서 자도 된다고 했지만, 저는 이미 빌린 여관방으로 돌아갔습니다. "
            "그날은 보름달이 떴고, 잠자리에 들자 비명과 늑대 같은 울음소리가 들렸습니다. "
            "창밖에는 두 발로 걷는 거대한 늑대가 서 있었습니다. 모두 겁에 질렸지만 저는 "
            "단검을 들고 맞서 싸웠습니다. 매우 강한 상대였고 그 털은 훌륭한 전리품이 "
            "되었습니다... 다음 날 거래 상대는 사라졌고, 그의 집에는 발톱 자국과 &4피&0만 "
            "남아 있었습니다. 늑대가 그를 잡아먹은 걸까요, 아니면 소문처럼 그가 바로 "
            "늑대인간이었을까요? 늑대인간의 드롭 아이템은 &1제작대&0에 넣으면 일반 "
            "아이템으로 되돌릴 수 있는 듯합니다."
        ),
        "info_book.evilcraft.first_age.new_world.nether_fish.text": (
            "네더를 탐험하던 중 평소보다 단단한 &1네더랙&0을 발견했습니다. 블록을 "
            "부수자 작은 생물이 튀어나와 저를 공격하고 불까지 붙였습니다. 약간 다쳤지만 "
            "다행히 어렵지 않게 처치했습니다."
        ),
        "info_book.evilcraft.first_age.relics.enchantments.poison_tip.text": (
            "&l&n독 묻은 촉&r&N무기에 독을 바르면 공격한 대상이 일정 확률로 중독됩니다. "
            "이 마법 부여에는 세 단계가 있습니다. 일반 책에 독성 물질을 더하면 기본 "
            "단계를 만들 수 있는 듯합니다."
        ),
        "info_book.evilcraft.first_age.items.dark_spike": "스파이크",
        "info_book.evilcraft.first_age.items.potentia_sphere": "포텐시아 구",
        "info_book.evilcraft.first_age.items.dull_dust": "흐릿한 가루",
        "info_book.evilcraft.first_age.items.dull_dust.text": (
            "&1설탕&0과 &1화약&0을 조합하면 지금은 별 쓸모가 없어 보이는 기묘한 "
            "가루가 만들어집니다. 이름이 흐릿한 까닭이죠. 언젠가는 달라질지도 모릅니다."
        ),
        "info_book.evilcraft.first_age.items.exalted_crafter": "고급 제작기",
        "info_book.evilcraft.first_age.items.exalted_crafter.text1": (
            "먼 곳에서는 제작대를 쓰기 불편할 때가 있습니다. &1분쇄된 다크 젬&0의 "
            "힘으로 인벤토리에서 바로 제작할 수 있습니다. 상자나 &1엔더 상자&0를 "
            "결합하면 내부 보관함도 생깁니다. 단축키에 지정할 수 있으며, 화면을 연 채 "
            "같은 단축키를 누르면 제작 격자를 비우고 Shift와 함께 누르면 격자 안의 "
            "아이템을 고르게 분배합니다. 토글 버튼으로 제작 격자에서 Shift를 눌러 뺀 "
            "아이템을 내부 보관함과 플레이어 인벤토리 중 어디로 돌려보낼지도 정할 수 있습니다."
        ),
        "info_book.evilcraft.first_age.items.display_stand.text2": (
            "블록의 다른 면과 상호작용하면 전시된 아이템으로 전달되므로, 그 아이템의 "
            "인벤토리나 유체, 에너지 저장소 등을 직접 사용할 수 있습니다."
        ),
        "info_book.evilcraft.first_age.vengeance_spirits": "복수령",
        "info_book.evilcraft.first_age.vengeance_spirits.catching_spirits": "복수령 포획",
        "info_book.evilcraft.first_age.vengeance_spirits.catching_spirits.text2": (
            "상자를 역설계해 직접 만들고, 복수령을 얼려 상자에 흡수시키는 방법도 "
            "알아냈습니다. &1복수 반지&0를 이 기술로 강화해 복수령을 조준하고 포획하는 "
            "&1복수 집중기&0를 만들었습니다. 가둔 복수령은 나중에 쓸모가 있을지도 모릅니다..."
        ),
        "info_book.evilcraft.second_age": "제2시대",
        "info_book.evilcraft.second_age.blood_extraction.text1": (
            "&1스파이크&0로 여러 곳에서 &4피&0를 모으는 간단한 도구를 만들었습니다. "
            "인벤토리에 넣고 특정 몹을 처치하면 &4피&0가 차오릅니다. 땅에 있는 "
            "&4피 얼룩&0에 Shift + 우클릭하면 &4피&0를 추출할 수도 있습니다. "
            "&4피 얼룩&0은 개체가 높은 곳에서 "
            "떨어져 죽을 때 생기는 듯하니 언젠가 유용하게 쓸 수 있겠습니다..."
        ),
        "info_book.evilcraft.second_age.blood_extraction.text4": (
            "기본 피 추출기의 용량은 작지만, 여러 &1피 추출기&0를 제작 격자에서 조합하면 "
            "용량을 늘릴 수 있습니다. &1다크 탱크&0와 조합하면 더 큰 용량을 얻습니다."
        ),
        "info_book.evilcraft.second_age.powers_of_blood.text2": (
            "&1다크 젬&0은 &4피&0를 잘 받아들이는 듯합니다. &4피&0 웅덩이에 던지면 "
            "&1다크 파워 젬&0이 됩니다. 월드에 &4피&0 근원 블록이 최소 다섯 개는 "
            "필요하며, 이 과정은 한 번은 거쳐야 합니다. 다음 장에서는 &1다크 파워 젬&0을 "
            "더 저렴하게 만드는 방법을 설명하겠습니다. 젬을 &4피&0 웅덩이에 던질 때는 "
            "근원 블록을 정확히 겨냥하세요."
        ),
        "info_book.evilcraft.second_age.powers_of_blood.text3": (
            "건조한 곳의 &4피&0는 시간이 지나면 &1굳은 피&0가 됩니다. &1굳은 피&0를 "
            "곡괭이나 손으로 부수면 다시 &4피&0로 돌아갑니다. &1굳은 피&0를 "
            "&1부싯돌과 부시&0로 부수면 &1굳은 피 조각&0을 얻습니다. 굳은 피 블록을 "
            "구해 구워도 조각을 얻을 수 있습니다. 부드럽게 채굴하는 방법이 도움이 될지도 "
            "모르겠군요..."
        ),
        "info_book.evilcraft.second_age.powers_of_blood.text4": (
            "희귀한 장소에서 &1응축된 피&0를 찾을 수 있습니다. &4피&0를 받는 기계에 "
            "넣으면 &4피&0 반 양동이를 추가로 공급합니다."
        ),
        "info_book.evilcraft.second_age.blood_infusion.blood_chest.text": (
            "아이템에 &4피&0를 주입하려는 첫 시도로 도구를 담가 수리하는 상자를 "
            "만들었습니다. 다만 드물게 도구에 &1파괴의 저주&0 같은 나쁜 효과가 붙습니다. "
            "이 효과를 없애도록 도구를 정화하는 방법도 찾아야겠습니다."
        ),
        "info_book.evilcraft.second_age.blood_infusion.blood_infuser.text1": (
            "아이템 수리보다 한 단계 더 나아가 보았습니다. &1다크 탱크&0처럼 &4피&0를 "
            "담는 아이템을 이 기계에 넣으면 &4피&0로 채워집니다. 일부 아이템은 "
            "&4피&0를 주입하면 "
            "특별한 형태로 변하며, 아래에는 주입 가능한 아이템 중 일부만 나열했습니다. "
            "레드스톤 신호를 주면 진행 중인 작업이 멈춥니다."
        ),
        "info_book.evilcraft.second_age.blood_infusion.undead_tree.text1": (
            "죽은 묘목을 되살렸더니 놀라운 나무가 자랐습니다. 자연적으로 키우면 피가 "
            "조금 나오지만, 떨어지는 묘목은 여전히 죽어 있는 듯합니다. 이 나무와 다크 "
            "젬을 조합하면 언젠가 쓸모가 있을 막대기를 만들 수 있습니다."
        ),
        "info_book.evilcraft.second_age.blood_infusion.undead_tree.text2": (
            "살아 있는 묘목을 제작 격자에서 가위로 자르면 간단히 죽은 묘목으로 만들 수 "
            "있습니다. &o저 나무가 사막에서 자라고 있나요?&r"
        ),
        "info_book.evilcraft.second_age.blood_infusion.advanced_blood_infusion.text1": (
            "첫 &1블러드 주입기&0를 만든 뒤 기계를 더 빠르고 효율적으로 개선할 방법을 "
            "고민했습니다. &1분쇄된 다크 젬&0으로 실체화한 &1약속&0을 만들었는데, "
            "&1블러드 주입기&0가 정말 그 약속을 따릅니다. 마치 살아 있는 것 같습니다..."
        ),
        "info_book.evilcraft.second_age.blood_infusion.advanced_blood_infusion.text2": (
            "&1빈 약속의 그릇&0에 보라색 가루를 담고 &4피&0를 주입하면 일정한 등급의 "
            "&1약속의 그릇&0이 됩니다. 이를 반응물 및 많은 &4피&0로 만든 광물 약속 "
            "수용체와 조합하면 특정 종류의 &1약속&0을 얻습니다. 유기 반응물로 만드는 "
            "&1끈기의 약속&0은 기계가 담는 &1약속&0과 &4피&0의 양을 늘리고 더 많은 "
            "주입 조합법을 엽니다. &1속도의 약속&0은 기계 속도를 높이고, &1생산성의 "
            "약속&0은 아이템 처리에 필요한 &4피&0를 줄입니다."
        ),
        "info_book.evilcraft.second_age.blood_infusion.advanced_blood_infusion_recipes": (
            "더 많은 피 주입 조합법"
        ),
        "info_book.evilcraft.second_age.evolved_blood_machinery.sanguinary_pedestal": (
            "혈액 받침대"
        ),
        "info_book.evilcraft.second_age.evolved_blood_machinery.entangled_chalice.text1": (
            "&1가스트&0의 눈물을 &4피&0로 강화하면 반으로 나누어도 성질을 공유하는 특별한 "
            "눈물이 됩니다. 이 눈물로 &l얽힌 성배&r를 만들어, 같은 눈물에서 나온 모든 "
            "성배가 유체 내용물을 공유하도록 했습니다."
        ),
        "info_book.evilcraft.second_age.evolved_blood_machinery.entangled_chalice.text2": (
            "보통 조합법으로는 내용물을 공유하는 성배 두 개가 나옵니다. 조합법 중앙의 "
            "&4금 주괴&0를 기존 성배로 바꾸면 같은 눈물 연결망에 성배를 하나 더 추가합니다."
        ),
        "info_book.evilcraft.second_age.evolved_blood_machinery.entangled_chalice.text3": (
            "성배는 월드에 놓거나 인벤토리에 보관할 수 있습니다. 손에 들고 Shift + "
            "우클릭하면 전방위 공급 모드를 켜 인벤토리의 모든 용기에 &4피&0를 계속 채웁니다."
        ),
        "info_book.second_age.evolved_blood_machinery.colossal_blood_chest.text3": (
            "그래서 &1거대한 피의 상자&0를 만들었습니다! 앞서 말한 문제를 모두 해결하지만, "
            "일반형보다 훨씬 큽니다. 이 거대한 구조를 지탱하려면 &1언데드 판자&0의 기묘한 "
            "힘이 필요했습니다."
        ),
        "info_book.second_age.evolved_blood_machinery.colossal_blood_chest.text4": (
            "&1거대한 피의 상자&0는 한꺼번에 수리할 아이템이 많을 때 쓰는 것이 좋습니다. "
            "기본 &4피&0 소모량은 &1피의 상자&0보다 많지만, 동시에 수리하는 아이템이 "
            "많을수록 &4피&0를 더 효율적으로 사용합니다."
        ),
        "info_book.second_age.evolved_blood_machinery."
        "sanguinary_environmental_accumulator.text2": (
            "연구 끝에 이 아이템으로 &4피&0를 사용하는 새로운 &1환경 축전기&0를 "
            "만들었습니다. 나쁜 영향도 완전히 막아 생물 군계가 황폐화하거나 신전 근처를 "
            "걷다가 갑자기 죽을 일도 없습니다."
        ),
        "info_book.evilcraft.second_age.tools.broom.modifiers.text.damage": (
            "&l&n피해&r&N충돌한 몹에게 주는 피해입니다. &1빗자루&0의 비행 속도가 "
            "빠를수록 피해도 커집니다."
        ),
        "info_book.evilcraft.second_age.tools.broom.modifiers.text.particles": (
            "&l&n입자&r&N비행 중 &1빗자루&0에서 방출되는 입자의 양입니다."
        ),
        "info_book.evilcraft.second_age.tools.broom.modifiers.text.kamikaze": (
            "&l&n카미카제&r&N개체와 충돌하면 &1빗자루&0가 폭발합니다. 탑승자가 "
            "살아남기는 매우 어려울 것입니다."
        ),
        "info_book.evilcraft.second_age.tools.broom.modifiers.text.withershield": (
            "&l&n위더 방패&r&N수정치가 높을수록 탑승자가 날아오는 투사체를 막을 "
            "확률이 커집니다."
        ),
        "info_book.evilcraft.second_age.tools.broom.modifiers.text.icy": (
            "&l&n냉기&r&N충돌한 개체의 이동 속도를 낮춥니다."
        ),
        "info_book.evilcraft.second_age.tools.broom.modifiers.text.sticky": (
            "&l&n끈적임&r&N다른 개체가 탑승자에게 달라붙습니다. 수정치가 높을수록 더 "
            "많은 개체가 붙습니다. 모두 태우려면 충분한 견고함 수정치가 필요합니다!"
        ),
        "info_book.evilcraft.second_age.tools.introduction.text": (
            "&4피&0를 사용하는 아이템은 대부분 내부 용기를 갖고 있습니다. "
            "&1블러드 주입기&0로 &4피&0를 채우거나, 다른 도구의 자동 공급 모드를 켠 뒤 "
            "채울 아이템을 손에 들면 됩니다. 사용할 때마다 &4피&0를 소모하며, 내부의 "
            "&4피&0가 떨어지면 인벤토리의 다른 용기에서 &4피&0를 가져옵니다. 공급할 "
            "용기가 없으면 작동을 멈춥니다."
        ),
        "info_book.evilcraft.second_age.tools.kineticator.text1": (
            "일정 범위의 아이템과 경험치 구슬을 끌어당깁니다. 우클릭으로 범위를 바꾸고 "
            "Shift + 우클릭으로 켜거나 끕니다. 가까운 아이템은 &4피&0를 거의 쓰지 않지만 "
            "멀수록 더 많은 &4피&0가 필요합니다. 웅크리면 끌어당기지 않습니다."
        ),
        "info_book.evilcraft.second_age.tools.kineticator.text2": (
            "조합법을 반대로 배치하면 아이템과 경험치 구슬을 밀어내는 반대 형태를 얻습니다."
        ),
        "info_book.evilcraft.second_age.tools.blood_pearl_of_teleportation": (
            "피 순간이동 진주"
        ),
        "info_book.evilcraft.second_age.tools.primed_pendant": "충전된 펜던트",
        "info_book.evilcraft.second_age.tools.effortless_ring": "수월한 반지",
        "info_book.evilcraft.second_age.tools.effortless_ring.text": (
            "&1생산성의 약속&0과 &1속도의 약속&0의 힘을 적용하는 반지를 만들었습니다. "
            "인벤토리에 넣어 두면&0 더 빨리 걷고, 더 높이 뛰며, 한 칸 높이의 블록을 쉽게 "
            "오릅니다. &oShift&r를 누르면 자동 오르기 효과를 잠시 막을 수 있습니다."
        ),
        "info_book.evilcraft.second_age.tools.vengeance_pickaxe": "복수 곡괭이",
        "info_book.evilcraft.second_age.tools.vengeance_pickaxe.text": (
            "&1복수 반지&0의 기술을 곡괭이에 적용했습니다. 내구도는 크게 낮아지지만, "
            "제작할 때 강력한 &1행운&0 효과가 붙는 흥미로운 특징이 있습니다."
        ),
        "info_book.evilcraft.second_age.weapons.vein_sword.text": (
            "전투를 자주 치르느라 &4피&0가 늘 부족한가요? 이 검으로 몹을 처치하면 "
            "&1피 추출기&0에 모이는 &4피&0의 양이 늘어납니다. 제작할 때 기본 &1약탈&0 "
            "효과도 붙습니다."
        ),
        "info_book.evilcraft.second_age.weapons.mace_of_distortion.text": (
            "우클릭을 누르고 있으면 철퇴 주위에 구가 커지며, 버튼을 놓으면 구 안의 개체를 "
            "밀쳐 내고 피해를 줍니다. 철퇴에 &4피&0가 충분해야 작동합니다. Shift + "
            "우클릭으로 위력 단계를 바꿀 수 있으며, 단계가 높을수록 피해와 &4피&0 소모량이 "
            "함께 늘어납니다."
        ),
        "info_book.evilcraft.second_age.weapons.mace_of_destruction.text": (
            "&1왜곡의 철퇴&0에서 파생된 무기로, 방출하는 힘이 강력한 폭발을 일으킵니다. "
            "오래 충전할수록 폭발이 커집니다. 위력 단계를 높이면 폭발의 시작 위력이 "
            "높아져 더 강하게 충전할 수 있습니다."
        ),
        "info_book.evilcraft.second_age.weapons.necromancer_staff.text": (
            "&1좀비&0는 어떤 종류든 해골을 이용하면 조종할 수 있는 듯합니다. 해골을 "
            "지팡이에 달자, 제가 지정한 개체를 일정 시간 공격하는 좀비를 소환할 수 "
            "있었습니다."
        ),
        "info_book.evilcraft.second_age.abusing_spirits.infusing_spirits.text": (
            "&1복수령&0을 상자에 가두는 것만으로는 별 쓸모가 없습니다. 약간의 "
            "&4피&0를 사용하면 복수령을 되살릴 수 있지 않을까 생각했습니다..."
        ),
        "info_book.evilcraft.second_age.abusing_spirits.spirit_furnace.text1": (
            "마침내 &1복수령&0을 되살리는 데 성공했습니다. 적어도 일부는 말입니다. "
            "되살아난 복수령은 현실 세계에서 살아가기에는 너무 약하지만, 원래 몹의 "
            "속성과 물질은 모두 지닌 듯합니다. 결과 몹을 담을 큰 기계를 만들면 많은 "
            "&4피&0를 들여 복수령을 되살린 뒤 즉시 익혀, 드롭 아이템을 기계의 "
            "인벤토리에 모을 수 있습니다. &1영원한 봉쇄 상자&0는 복수령이 빠져나오지 "
            "않아 계속 재사용할 수 있습니다."
        ),
        "info_book.evilcraft.second_age.abusing_spirits.spirit_furnace.text2": (
            "복수령이 빠져나오지 못하게 하려면 &4피&0를 주입한 &1다크 벽돌&0 같은 "
            "튼튼한 블록이 많이 필요합니다. 되살릴 몹이 들어갈 만큼 속이 빈 직육면체를 "
            "만드세요. 좀비라면 폭 1블록, 높이 2블록이므로 내부 폭 3블록, 높이 4블록이 "
            "필요합니다. 아주 큰 몹은 9x9 구조물이 필요할 수도 있습니다!"
        ),
        "info_book.evilcraft.second_age.abusing_spirits.spirit_furnace.text3": (
            "구조물 어딘가에 &1영혼 화로&0 블록 하나도 놓아야 합니다. 이 블록은 일반적인 "
            "방법으로 다른 인벤토리나 탱크에 연결할 수 있습니다. 구조물이 완성되면 선명한 "
            "붉은빛이 납니다."
        ),
        "info_book.evilcraft.second_age.abusing_spirits.spirit_reanimator.text1": (
            "&1영혼 화로&0를 알아낸 뒤에도 복수령을 되살리는 연구를 계속했습니다. "
            "불안정한 몹을 안정시키려고 &1알&0 안에 넣었습니다. 이 과정에는 여전히 많은 "
            "&4피&0와 빈 &1알&0이 필요합니다."
        ),
        "info_book.evilcraft.second_age.abusing_spirits.spirit_reanimator.text2": (
            "고급 과정에서 복수령이 완전히 소모되므로 &1복수령&0 하나당 &1알&0 하나만 "
            "만들 수 있습니다."
        ),
        "info_book.evilcraft.second_age.abusing_spirits.spirit_reanimator.text3": (
            "일부 몹은 &1알&0에 들어가기를 거부하므로, 그 복수령은 영원히 사라집니다."
        ),
        "info_book.evilcraft.second_age.after_death.spirit_killing101": "정령 처치 입문",
        "info_book.evilcraft.second_age.after_death.spirit_killing101.text2": (
            "복수령은 저를 공격하는데 맞설 방법이 없다는 사실이 늘 성가셨습니다. 조사해 "
            "보니 복수령이 두려워하는 ‘끝’, 즉 엔드와 관련된 물건이 실제로 피해를 줍니다. "
            "몇 가지 엔드 유물로 &1복수 집중기&0를 강화해 복수령을 공격할 수 있게 했습니다."
        ),
        "info_book.evilcraft.second_age.after_death.garmonbozia.text3": (
            "제 동료들은 제가 너무 멀리 갔다고 말합니다. 어리석은 자들입니다."
        ),
        "info_book.evilcraft.first_age.relics.enchantments.unusing.text": (
            "&l&n사용 방지&r&N아끼는 도구가 잠깐 한눈판 사이에 부서지는 일이 "
            "지겨워졌습니다. 그래서 내구도가 거의 다 된 도구를 사용할 수 없게 만드는 "
            "새로운 마법 부여를 고안했습니다. 덕분에 도구를 예전 모습으로 수리할 시간을 "
            "충분히 벌 수 있습니다."
        ),
        "info_book.evilcraft.second_age.evolved_blood_machinery."
        "sanguinary_pedestal.text1": (
            "몹을 절벽에서 밀어 떨어뜨리고 &4피&0를 추출하는 일이 지겨워져, 주변의 "
            "&1피 얼룩&0에서 &4피&0를 추출해 가까운 탱크에 넣는 장치를 만들었습니다. "
            "&1다크 파워 젬&0을 사용하면 이 &4피&0 추출의 &4피&0 효율을 높일 수 "
            "있습니다."
        ),
        "info_book.second_age.tools.rejuvenated_flesh.text": (
            "&1살점&0에 &1가몬보지아&0를 결합하면 무한한 식량 공급원으로 만들 수 "
            "있습니다. 다만 이것을 먹으려면 &4피&0를 공급해야 합니다."
        ),
        "info_book.evilcraft.first_age.new_world.dark_ore.text": (
            "이 세계에 온갖 자원이 있다는 사실은 오래전부터 알고 있었습니다... 하지만 "
            "오늘 새로운 광석을 발견했습니다. 어두운 빛을 띠어 귀중한 보석을 떠올리게 "
            "하지만, 그 안에서 아주 불길한 기운이 느껴집니다. 주로 &l레드스톤 광석&r과 "
            "비슷한 높이에서 발견되지만 때로는 훨씬 높은 곳에서도 나옵니다. 다크 젬을 "
            "얻으려면 최소한 철 곡괭이로 채굴해야 합니다. 행운이 부여된 도구로 채굴하면 "
            "기묘한 가루도 나오는 듯합니다. 곧 이 가루의 쓰임새를 찾을 수 있겠지요. "
            "행운 단계가 높을수록 가루를 얻을 확률도 올라갑니다."
        ),
        "info_book.evilcraft.first_age.new_world.darkened_apple.text": (
            "이 책을 읽는 동안 이미 이 아이템을 발견했을지도 모릅니다. &1사과&0와 "
            "&1다크 젬&0을 조합하면, 먹었을 때 일정 시간 큰 피해를 주는 특별한 "
            "&1사과&0가 만들어집니다. 이 효과로 대상이 죽으면 정체불명의 변칙이 "
            "남습니다. 아직 이 현상의 쓰임새는 알아내지 못했습니다..."
        ),
    },
    "evilcraftcompat": {
        "item.items.evilcraft.veined_scribing_tools": "핏줄 필기 도구",
        "info_book.evilcraftcompat.mod_integrations.enderio.text": (
            "엔더 기반 기술은 매우 흥미롭습니다. 언젠가 이를 활용해 제 기계도 개선할 수 "
            "있을 것 같습니다. 어쨌든 Ender IO의 기계로 &1다크 광석&0과 &1다크 젬&0을 "
            "처리할 수 있으니 꽤 유용합니다."
        ),
        "info_book.evilcraftcompat.mod_integrations.blood_magic.text": (
            "어느 날 &1마법사&0가 쓰던 듯한 &1피 구슬&0을 발견했습니다. 사용하자 제 "
            "&4피&0 연결망과 이어진 느낌이 들었습니다. &1블러드 주입기&0로 많은 "
            "&4피&0를 밀어 넣어, 제 &4피&0 연결망과 이어지면서 평범한 용기로도 쓸 수 "
            "있는 아이템을 만들었습니다. 이제 즐겨 쓰는 기계나 도구에 넣어 사용할 수 있습니다."
        ),
        "info_book.evilcraftcompat.mod_integrations.thaumcraft.text": (
            "신비학은 다른 마법과 사뭇 다릅니다. 신비학자들은 제 아이템과 기묘한 육각형을 "
            "유난히 좋아하는 듯합니다. 그들을 위해 잉크 대신 &4피&0로 글을 쓸 수 있는 "
            "&1핏줄 필기 도구&0를 만들었습니다."
        ),
        "info_book.evilcraftcompat.mod_integrations.tinkers_construct.text": (
            "&0도구, 도구, 또 도구!&r 이 사람들은 온통 도구 생각뿐인 듯합니다. 그렇게 "
            "많이 쓰면 심하게 손상될 텐데, 다행히 &1피의 상자&0로 수리할 수 있습니다!"
        ),
        "info_book.evilcraftcompat.mod_integrations.jei.text": (
            '어떤 사람에게는 "&oToo Many Items&r"가 있고, 다른 사람에게는 '
            '"&oNot Enough Items&r"가 있는 모양입니다. 마침내 사람들이 '
            '"&oJust Enough Items&r"를 갖춘 단계에 도달한 듯하며, 이제 그들도 '
            "이 책의 지식을 이해할 수 있습니다."
        ),
        "info_book.evilcraftcompat.mod_integrations.ic2.text": (
            "윙윙거리는 기계를 끊임없이 다루는 이상한 무리가 있습니다. 그 기계들이 "
            "무엇을 하는지는 &1분쇄기&0 말고는 잘 모르겠습니다. &1다크 광석&0을 "
            "넣으면 곧바로 &1다크 젬&0과 분쇄된 형태를 얻을 수 있습니다. 일반 "
            "&1다크 젬&0도 넣어 분쇄할 수 있습니다."
        ),
        "info_book.evilcraftcompat.mod_integrations.thermal_expansion.text": (
            "이 사람들은 꽤 기묘합니다. 늘 이상한 옷을 입고, 어째서인지 여러 종류의 "
            "렌치를 들고 다니는 듯합니다. 제가 아는 것은 하나뿐입니다. 이들에게는 "
            "액체를 옮기는 기계가 있어 아주 기본적인 피 주입을 할 수 있지만, 안타깝게도 "
            "업그레이드할 수 없습니다."
        ),
    },
}

QUEST_OVERRIDES: dict[str, object] = {
    "quest.0104C2E2E30B966B.quest_desc": [
        "&c피의 상자&r가 너무 느린가요? 수리할 아이템이 너무 많나요? "
        "&c거대한 피의 상자&r를 만들면 이 문제를 해결할 수 있습니다.\\n\\n"
        "먼저 &9강화된 언데드 판자&r 25개를 만드세요. 이 판자로 속이 빈 3x3x3 "
        "정육면체를 만든 뒤, &c거대한 피의 상자&r 블록을 놓아 멀티블록 구조를 "
        "완성하세요. 올바르게 지었다면 이제 거대한 &c피의 상자&r를 사용할 수 "
        "있습니다. 이름처럼 정말 거대하죠.\\n\\n이 상자는 &6약속&r으로 업그레이드할 "
        "수도 있습니다.\\n",
        "{image:atm:textures/questpics/evilcraft/bloodchest.png width:250 "
        "height:200 align:1}",
    ],
    "quest.0104C2E2E30B966B.quest_subtitle": "상위 피의 상자",
    "quest.026A71F98A52E3A5.quest_desc": [
        "마을에는 &o흥미로운&r 주민이 숨어 있는데, 사실 이들은 &d늑대인간&r입니다."
        "\n\n이 짐승을 처치하면 &d늑대인간 살점&r을 얻을 수 있습니다."
    ],
    "quest.066438B01655D866.quest_desc": [
        "&d복수 에센스&r도 유용하지만, 복수령을 붙잡아 나중에 쓸 수도 있습니다. "
        "악당다운 생각이죠?\n\n복수령 사냥꾼이 되려면 먼저 &d복수 집중기&r를 만드세요. "
        "집중기로 복수령을 &a얼린&r 뒤 근처에 &9영원한 봉쇄 상자&r를 놓으면, "
        "상자가 복수령을 빨아들여 보관합니다."
    ],
    "quest.066438B01655D866.title": "&d복수령 포획",
    "quest.0BB0DF36B079558F.quest_desc": [
        "&6얽힌 성배&r를 월드에 놓으면 피를 공급할 수 있습니다. 인벤토리에서 "
        "활성화하면 &c피&r를 사용하는 아이템을 채웁니다.\n\n같은 연결망을 공유하는 "
        "성배를 더 만들려면 금 주괴 대신 기존 얽힌 성배를 넣는 조합법을 사용하세요."
    ],
    "quest.10EF30B919EBA5C6.quest_desc": [
        "행운 V가 붙은 곡괭이입니다. 그게 전부예요.\n\n채굴할 때 복수령을 "
        "소환하는 일은 &o&5&l절대로 없을 겁니다&r."
    ],
    "quest.1E3471513C75CC54.quest_desc": [
        "피 양동이를 땅에 오래 두거나 건조 대야에 넣으면 &c굳은 피&r가 됩니다."
        "\n\n비위생적이지만 진행하려면 마른 피까지 온갖 형태의 피가 필요합니다."
        "\n\n굳은 피는 비를 맞거나 일반 도구로 부수면 다시 피로 돌아갑니다. "
        "&9부싯돌과 부시&r로 부수면 대신 &d굳은 피 조각&r을 얻습니다."
    ],
    "quest.1E3471513C75CC54.title": "말라붙은... &c피?",
    "quest.27E34DCC9C94F4FF.quest_desc": [
        "이 퀘스트는 &6AllTheMods 운영진&r 또는 &2커뮤니티 기여자&r가 AllTheMods "
        "모드팩용으로 작성했습니다.\n\n모든 &6AllTheMods&r 팩은 &e모든 권리 보유&r "
        "라이선스를 따릅니다. &6AllTheMods 팀&r의 명시적인 허가 없이 다른 공개 "
        "모드팩에서 이 퀘스트를 사용할 수 없습니다.\n\n이 퀘스트는 의도적으로 숨겨져 "
        "있습니다. 이 문구가 보인다면 편집 모드입니다."
    ],
    "quest.28BF66D1B8CD4D44.quest_desc": [
        "&d빗자루&r는 막대, 마개, 솔의 3가지 부품으로 만듭니다.\n\n각 기본 부품을 "
        "특정 아이템과 조합하면 고유한 수정치가 붙습니다. 종류가 많으므로 자세한 내용은 "
        "가이드북을 확인하세요!\n\n세 부품을 제작대에 함께 넣으면 빗자루가 완성됩니다. "
        "빗자루가 제대로 움직이려면 피가 필요합니다."
    ],
    "quest.290FAB3DE8FD04E7.quest_desc": [
        "우클릭을 누르고 있으면 &c피&r를 사용한 광역 공격을 충전합니다. "
        "Shift + 우클릭으로 위력 단계를 바꿀 수 있습니다.\n\n단계가 높을수록 피를 더 "
        "많이 소모하고 더 큰 피해를 줍니다.\n\n&6ATM Star&r를 제작하려면 피를 완전히 "
        "채운 철퇴가 필요합니다."
    ],
    "quest.2CB69634F6A6E53E.quest_desc": [
        "&0다크 신전&r은 중앙에서 거대한 빛기둥이 솟아 쉽게 알아볼 수 있습니다."
        "\n\n&9다크 신전&r 중앙에는 &a환경 축전기&r가 있습니다.\n\n이 장치를 사용하면 진행에 "
        "필요한 여러 아이템을 강화하거나 만들 수 있으며, &d번개 폭탄&r도 그중 하나입니다!"
    ],
    "quest.2CB69634F6A6E53E.title": "&l&0다크 신전",
    "quest.1DA0A87C471A38AC.quest_desc": [
        "&cEvilCraft&r에는 자체 몹 농장도 있습니다!\\n\\n시작하려면 "
        "&c다크 블러드 벽돌&r을 최소 33개 제작하세요. 이 벽돌로 소환된 정령을 "
        "가둘 만큼 튼튼한 구조물을 만들 수 있습니다.\\n\\n또한 &9영원한 봉쇄 "
        "상자&r에 갇힌 정령이 필요합니다. 어떤 드롭 아이템을 얻을지는 이 정령이 "
        "결정합니다.\\n\\n몹이 생성될 공간이 충분한 직육면체 구조물을 만드세요. 최소 "
        "크기는 3x4x3이며 좀비 같은 몹이 생성되기에 충분합니다. 구조물의 한 면에는 "
        "상호작용할 수 있도록 &9영혼 화로&r를 놓으세요.\\n\\n더 큰 몹을 생성하려면 "
        "더 큰 구조물이 필요합니다.\\n",
        "{image:atm:textures/questpics/evilcraft/evilcraft_spiritfurnace.png "
        "width:125 height:150 align:1}",
    ],
    "quest.35FA55BE8DF49EE8.title": "&d가몬보지아",
    "quest.35FA55BE8DF49EE8.quest_desc": [
        "처치한 &9복수령&r의 힘을 블러드 주입기로 주입하면 &d가몬보지아&r를 "
        "만들 수 있습니다.\n\n&d고통&r과 &d슬픔&r이 물질로 드러난 것으로, EvilCraft의 강력한 "
        "도구와 아이템에 쓰이는 최고급 제작 재료입니다."
    ],
    "quest.40888A2C17D8FFF6.quest_desc": [
        "블러드 주입기로 &c언데드 묘목&r을 만들면 &d언데드 나무&r가 자랍니다."
        "\n\n통나무와 판자는 EvilCraft의 여러 도구와 아이템을 만드는 데 쓰입니다."
    ],
    "quest.4978A9B616362CCE.title": "&a등급 2&r: 더 많은 &c피",
    "quest.4D7B6842B9F53459.quest_desc": [
        "수월한 반지는 이동 속도와 자동 오르기 높이를 늘려 줍니다!"
    ],
    "quest.4DF7E2149F4BD8CC.quest_desc": [
        "원하는 물약을 넣으려면 &2충전된 펜던트&r를 손에 들고 우클릭해 내부 "
        "인벤토리를 여세요."
    ],
    "quest.51B24CC5E9332C1E.quest_desc": [
        "몹을 처치하면 때때로 &d복수령&r이 나타납니다.\n\n복수령이 남기는 "
        "&d복수 에센스&r는 EvilCraft의 고급 아이템 제작에 쓰입니다.\n\n복수령이 잘 "
        "보이지 않나요? &9복수 반지&r를 만들고 켜 두면 전투 중 더 많은 복수령을 "
        "끌어들일 수 있습니다."
    ],
    "quest.51B24CC5E9332C1E.title": "&d복수령의 복수",
    "quest.525517F1625A9BCB.quest_desc": [
        "몹이 높은 곳에서 떨어져 &c피&r를 사방에 흩뿌렸나요?\n\n&c혈액 받침대&r로 "
        "귀중한 &c피&r를 흡수해 보관할 수 있습니다!\n\n자동으로 피를 모으려면 받침대 위에 "
        "&9스파이크 판&r을 놓고 몹이 그 위에 서게 하세요."
    ],
    "quest.59036A2741E7A8AA.title": "&a&9스폰 알 만들기",
    "quest.62A262A706CFCAF0.quest_desc": [
        "이제 피 웅덩이에서 다크 파워 젬을 만들 필요가 없습니다.\n\n&9블러드 "
        "주입기&r가 지저분한 작업을 대신하며, 아이템에 피를 직접 주입합니다!\n\n"
        "&6약속&r으로 업그레이드할 수도 있습니다. 진행에 꼭 필요한 핵심 기계입니다!"
    ],
    "quest.62A262A706CFCAF0.title": "&a&c블러드 주입기",
    "quest.62CE0FFAF6352287.quest_desc": [
        "EvilCraft 기계는 &6약속&r으로 업그레이드할 수 있습니다. 약속마다 효과가 "
        "다르지만, 먼저 블러드 주입기를 업그레이드해 더 많은 조합법을 열어야 합니다."
        "\n\n&6끈기의 약속: 등급 1&r을 만드세요. 보통 기계의 저장 용량을 늘리며, "
        "블러드 주입기에서는 추가 조합법도 해제합니다!"
    ],
    "quest.62CE0FFAF6352287.title": "&a기계 업그레이드",
    "quest.63AE4568375DD1BF.title": "혈액 환경 축전기",
    "quest.674E2690D66ECD6E.quest_desc": [
        "뇌우가 칠 때 &a환경 축전기&r에 &a날씨 용기&r를 던지면 폭풍의 힘을 "
        "담을 수 있습니다.\n\n이 힘으로 번개를 마음대로 다루는 아이템을 만들 수 있습니다."
        "\n\n&6ATM Star&r를 제작하려면 번개 폭탄이 필요합니다."
    ],
    "quest.68318811CCC28320.quest_desc": [
        "&c굳은 피 조각&r과 &9다크 파워 젬&r을 조합하면 피 주입 코어를 만듭니다."
        "\n\n&9피 주입 코어&r는 EvilCraft의 여러 기계에 쓰이는 핵심 제작 부품입니다."
    ],
    "quest.6B7C016407F7AE3C.quest_desc": [
        "일반 무기로는 &d복수령&r을 공격할 수 없습니다. 그러면 어떻게 처치해야 "
        "할까요?\\n\\n관통 복수 빔을 발사하면 됩니다. 관통 복수 집중기를 어느 "
        "손이든 든 채 우클릭을 누르고 있으면 빔을 발사합니다."
    ],
    "quest.6B7C016407F7AE3C.quest_subtitle": "복수령 처치하기",
    "quest.74B0308336F5E017.quest_desc": [
        "&c피의 상자&r는 &c피&r를 소모해 아이템의 내구도를 수리합니다.\n\n"
        "다만 수리한 아이템에 &d저주&r가 붙을 때도 있습니다..."
    ],
    "quest.75CF9EAB75C3907E.quest_desc": [
        "&9다크 젬&r의 힘으로 &a다크 탱크&r를 만들 수 있습니다.\n\n모든 유체를 "
        "16양동이까지 저장하며, 주로 모은 &c피&r를 담는 데 쓰게 될 것입니다.\n\n"
        "용량이 더 필요하면 제작 격자에서 다른 다크 탱크와 조합하세요."
    ],
    "quest.7B524DAD8A33BF85.quest_desc": [
        "적에게서 더 많은 피가 필요하신가요? 물론 그렇겠죠!\n\n&d광맥 검&r은 "
        "더 많은 피를 모으며, 약탈 효과 덕분에 드롭 아이템도 늘려 줍니다!"
    ],
    "quest.7E79F52147B606F9.quest_desc": [
        "피를 모으려면 먼저 &c피 추출기&r를 제작하세요.\n\n인벤토리에 넣은 채 "
        "몹을 처치하면 추출기에 피가 모입니다. &c피&r는 EvilCraft의 중요한 자원입니다."
        "\n\n용량을 늘리려면 피 추출기를 하나 더 만들어 제작 격자에서 조합하세요. "
        "다크 탱크와 조합해도 용량이 늘어납니다.\n\n땅에서 발견하거나 직접 만든 "
        "&c피 얼룩&r에 사용해 피를 추출할 수도 있습니다.\n\n피가 충분히 차면 땅을 "
        "향해 Shift + 우클릭하여 피 한 양동이를 놓을 수 있습니다."
    ],
    "task.7DE03D4A420D1028.title": "다크 신전 방문",
    "quest.745E616E97838D2E.quest_desc": [
        "&l잠깐!&r 동물을 마구 학살하지 마세요. PETA가 타협안을 제시한 모양입니다. "
        "무고한 동물을 그만 죽이면 &5크리에이티브 &4피 드롭&r을 준다고 하네요! "
        "\\n\\n이 아이템을 사용하면 &4피&r가 필요한 모든 용기를 무한히 채울 수 "
        "있습니다! \\n\\n제작하려면 &b끈기의 약속&r 4개, &6&lATM Star&r, "
        "그리고 &4피&r로 가득 찬 다른 아이템 4개가 필요합니다. "
    ],
    "quest.76A3A2A97AB66C43.quest_desc": [
        "&9영원한 봉쇄 상자&r에 가둔 복수령으로 스폰 알을 만들고 싶나요?\n\n"
        "&9영혼 소생기&r에 충분한 &c피&r와 달걀, 그리고 원하는 복수령이 든 "
        "&9영원한 봉쇄 상자&r를 넣으면 스폰 알 생성을 시도합니다!\n\n참고: 일부 "
        "몹은 스폰 알로 만들 수 없습니다."
    ],
    "quest.00AC7CC291A3E590.quest_desc": [
        "월드 곳곳에서 신호기 같은 빛기둥이 솟는 구조물을 보았을 겁니다. 조약돌로 "
        "만들었고 4개의 다리로 높이 떠 있는 구조물이죠.\n\n이곳은 &8다크 신전&r이며, "
        "우리에게 필요한 &a환경 축전기&r가 있습니다.\n\n날씨 용기를 채우려면 뇌우가 "
        "칠 때까지 기다려야 합니다. 그러고 나면 &3번개 폭탄&r을 만들 수 있습니다!"
    ],
    "quest.3F5B5D6B788E0A73.quest_desc": [
        "피, 살점, 의식까지, 사악한 것이라면 &4&lEvilCraft&r에서 나온 것일 겁니다!"
    ],
    "quest.54BAF833344F0AAE.quest_desc": [
        "이 작업은 2단계입니다! 먼저 &8다크 젬&r, 철, 유리로 간단히 만드는 "
        "&8다크 탱크&r가 필요합니다.\n\n다음은 &7이클립스 엠버 연료&r인데, "
        "이쪽은 간단하지 않습니다...\n\n&7이클립스 엠버&r를 &3액체 보이드플레임 "
        "연료&r에 떨어뜨려 &7정제되지 않은 이클립스 엠버&r를 만드세요. 그런 다음 "
        "&9섀도우펄스 구&r가 퍼지게 해 &7이클립스 엠버 연료&r로 바꿉니다.\n\n"
        "참고로 16양동이 분량이 필요합니다!"
    ],
    "quest.54BAF833344F0AAE.title": "&7이클립스 엠버 연료&r를 채운 &8다크 탱크",
    "quest.5A6831E0BD2F6AB5.title": "&4관통 복수 집중기 2개",
    "quest.73BE1EB3E69814E9.quest_desc": [
        "첫 번째이자 가장 쉬운 재료는 &5다크 막대기&r입니다. 채굴한 &8다크 젬&r과 "
        "&c언데드 나무&r에서 얻는 &c언데드 판자&r로 만듭니다.\n\n다음은 "
        "&5강화된 반전 포텐시아&r입니다. &7반전 포텐시아&r를 만든 뒤 &a환경 축전기&r에 "
        "넣고 번개를 맞히세요!\n\n마지막으로 &a빈 약속&r을 아주 많이 주입해야 합니다."
        "\n\n&4피&r를 넉넉히 준비하세요. &5철퇴&r 자체도 &4피&r로 가득 채워야 합니다."
    ],
    "quest.0447551EF7FB171B.quest_desc": [
        "더 처리할 필요는 없습니다. 이것은 &4피&r 시험이 아니라 연료입니다!\n\n"
        "&4받침대&r를 &c&l헤파이스토스 대장간&r에 파이프로 연결하고 피가 흐르는 "
        "모습을 확인하세요! &4피&r가 바로 연료입니다."
    ],
    "quest.3C5A5432E6B1EF9E.quest_desc": [
        "스포너와 몹 이동 장치는 마련했습니다. 이제 몹에게서 &4피&r를 얻을 차례입니다."
        "\n\n보통은 스파이크나 몹 매셔로 처치할 수 있지만, &4피&r를 모으려면 "
        "&4강화 혈액 받침대&r 위에 &7스파이크 판&r을 놓으세요.\n\n&4받침대&r "
        "위의 &7스파이크 판&r이 몹에게 피해를 주면서 &4피&r를 &4받침대&r로 보냅니다. "
        "몹의 &4체력&r이 많을수록 더 많은 &4피&r를 얻습니다!\n\n&4피&r는 유체 "
        "형태로 저장되며, &4받침대&r에서 &c&l헤파이스토스 대장간&r으로 파이프를 "
        "연결해 옮길 수 있습니다.",
        "{image:atm:textures/questpics/forbidden/forbidden_pedestal.png "
        "width:100 height:100 align:center}",
    ],
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def replace_terms(value: object) -> object:
    """문자열 또는 문자열 목록의 확정 용어를 통일한다."""
    if isinstance(value, str):
        for before, after in TERM_REPLACEMENTS:
            value = value.replace(before, after)
        value = value.replace("GUI", "화면").replace("Grid", "제작 격자")
        return value
    if isinstance(value, list):
        return [replace_terms(child) for child in value]
    return value


def normalize_override(value: object) -> object:
    """Python 문자열의 실제 줄바꿈을 게임 언어 파일의 이스케이프 표기로 바꾼다."""
    if isinstance(value, str):
        return value.replace("\n", "\\n")
    if isinstance(value, list):
        return [normalize_override(child) for child in value]
    return value


def review_language() -> dict[str, object]:
    """언어 작업본 전체에 용어 통일과 검수 수정을 반영한다."""
    report: dict[str, object] = {}
    for namespace in ("evilcraft", "evilcraftcompat"):
        root = WORK_ROOT / namespace
        korean_path = root / "ko_kr.json"
        source_path = root / "candidate_sources.json"
        korean = load_json(korean_path)
        sources = load_json(source_path)
        before = dict(korean)
        korean = {key: replace_terms(value) for key, value in korean.items()}
        for key, value in LANGUAGE_OVERRIDES[namespace].items():
            korean[key] = normalize_override(value)
        changed_keys = [key for key in korean if korean[key] != before[key]]
        for key in changed_keys:
            sources[key] = "manual_review"
        korean_path.write_text(
            json.dumps(korean, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        source_path.write_text(
            json.dumps(sources, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        report[namespace] = {
            "keys_reviewed": len(korean),
            "keys_changed": sum(value == "manual_review" for value in sources.values()),
            "changes_this_run": len(changed_keys),
            "source_counts": dict(sorted(Counter(sources.values()).items())),
        }
    return report


def review_quests() -> dict[str, object]:
    """전용 및 관련 퀘스트의 기존 한국어와 신규 문구를 검수한다."""
    reviewed = 0
    changed = 0
    changes_this_run = 0
    source_counts: Counter[str] = Counter()
    for root in sorted((WORK_ROOT / "quests").glob("*")):
        korean_path = root / "ko_kr.json"
        source_path = root / "candidate_sources.json"
        if not korean_path.is_file():
            continue
        korean = load_json(korean_path)
        sources = load_json(source_path)
        before = dict(korean)
        korean = {key: replace_terms(value) for key, value in korean.items()}
        for key, value in QUEST_OVERRIDES.items():
            if key in korean:
                korean[key] = normalize_override(value)
        changed_keys = [key for key in korean if korean[key] != before[key]]
        for key in changed_keys:
            sources[key] = "manual_review"
        korean_path.write_text(
            json.dumps(korean, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        source_path.write_text(
            json.dumps(sources, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        reviewed += len(korean)
        changed += sum(value == "manual_review" for value in sources.values())
        changes_this_run += len(changed_keys)
        source_counts.update(str(value) for value in sources.values())
    return {
        "keys_reviewed": reviewed,
        "keys_changed": changed,
        "changes_this_run": changes_this_run,
        "source_counts": dict(sorted(source_counts.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    report = {
        "family": "EvilCraft",
        "languages": review_language(),
        "ftbquests": review_quests(),
    }
    (WORK_ROOT / "manual_review_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
