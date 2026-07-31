#!/usr/bin/env python3
"""The Bumblezone 장문 아이템·블록 설명의 원문 대조 번역."""

from __future__ import annotations

import re


TRANSLATIONS: dict[str, str] = {
    "the_bumblezone.recipe_viewers.bee_queen_trades": "여왕벌 거래",
    "the_bumblezone.recipe_viewers.queen_trade_chance_tooltip": "확률: %s%%",
    "the_bumblezone.recipe_viewers.queen_trade_chance_text": "%s%%",
    "the_bumblezone.recipe_viewers.queen_trade_xp": "%s XP",
    "the_bumblezone.recipe_viewers.bee_queen_color_randomizing_trades": "여왕벌 색상 거래",
    "the_bumblezone.recipe_viewers.queen_trade_colors": "%s가지 색상",
    "the_bumblezone.honey_slime_spawn_egg.description": " 수동적인 꿀 슬라임을 생성하는 알입니다. 성체 꿀 슬라임에 유리병을 사용하면 꿀이 든 병을 얻을 수 있습니다. \n\n 설탕으로 유인하고 번식시킬 수 있으며, 새끼는 시간이 지나면 성체가 됩니다. 성체를 죽이면 새끼 꿀 슬라임으로 나뉘며, 이미 꿀을 채취한 성체라면 작은 일반 슬라임으로 나뉩니다. 한 마리를 죽이면 근처 꿀 슬라임이 복수하러 달려듭니다! \n\n 작은 또는 중간 크기의 일반 슬라임에게 꿀 양동이를 사용해도 꿀 슬라임을 만들 수 있습니다! \n\n Buzzier Bees 제작자 Bagel이 The Bumblezone에 기증한 몹입니다. 특별히 감사드립니다!",
    "the_bumblezone.variant_bee_spawn_egg.description": " 다른 외형의 벌을 생성하는 알입니다! 이 벌들은 생김새만 다를 뿐 바닐라 벌과 완전히 똑같이 행동합니다.",
    "the_bumblezone.beehemoth_spawn_egg.description": " 거대한 벌 비히모스를 생성하는 알입니다! 꿀 양동이, 꿀이 든 병 같은 벌 먹이와 여러 꿀 아이템을 먹여 길들일 수 있지만, 꿀 양동이를 들고 있을 때만 따라옵니다. 계속 먹이면 길들여 안장을 얹고 탈 수 있습니다! 먹이를 주고 타고 다닐수록 친밀도가 올라 이동 속도와 최대 체력이 증가합니다. 친밀도가 최대가 되면 여왕 비히모스로 성장해 최고 속도로 날 수 있습니다! 피해를 받으면 친밀도가 감소하며, 모두 잃으면 다시 야생 상태가 되어 불행해집니다. :( Carrier Bees 모드의 Aranaira, Alexthe666, Nooby가 The Bumblezone에 기증한 몹입니다. 특별히 감사드립니다!",
    "the_bumblezone.bee_queen_spawn_egg.description": " 거래를 원하는 거대하고 수동적인 여왕벌을 생성하는 알입니다! 아이템을 든 채 우클릭하거나 여왕벌 앞에 아이템을 떨어뜨리면 거래합니다. 여러 아이템을 건네 무엇을 받을 수 있는지 확인해 보세요! 여왕벌은 제한 시간 동안 특정 아이템을 요구하고 추가 보상을 주는 보너스 거래를 제안할 수도 있습니다. 이때도 다른 아이템으로 일반 거래를 할 수 있습니다.\n\n 첫 거래에 성공하면 발전 과제를 하나 완료할 때마다 로열 젤리 병을 주는 여왕의 소망 발전 과제 계열이 열립니다. \n\n 전체 발전 과제 계열을 완료한 뒤 여왕벌을 찾아 빈손으로 우클릭하면 보상을 다시 받을 수 있도록 계열을 초기화합니다!",
    "the_bumblezone.rootmin_spawn_egg.description": " 루트민을 생성하는 알입니다! 잔디 블록으로 위장하며 벌 장비를 착용하지 않은 대상을 공격하는 반적대적 몹입니다. 우클릭하면 머리에 든 꽃을 다른 작은 꽃이나 키 큰 꽃으로 바꿀 수 있습니다! 이름표를 사용하면 주인에게 발사하지 않고 근처 몬스터를 노리게 되어 어느 정도 길들일 수 있습니다.",
    "the_bumblezone.sentry_watcher_spawn_egg.description": " 센트리 감시자를 생성하는 제작 가능한 알입니다. 앞에 있는 벌 이외의 생명체를 향해 돌진하는 거대한 무생물 벌 석상입니다! 생성 알로 자신을 만든 플레이어에게는 돌진하지 않습니다. 속도가 빠를수록 큰 피해를 주며, 몹을 벽에 짓누르면 추가 피해를 줍니다. 자신이 생성 알로 배치한 감시자를 빠르게 두 번 우클릭하면 다시 생성 알로 바꿀 수 있습니다. 영원 성소에서 생성된 센트리 감시자는 구조물 밖으로 옮기거나 구조물 안에서 죽이면 폭발합니다. 구조물 안에서는 총 폭발 저항이 높은 블록을 제외하고 앞을 막는 블록도 부숩니다.",
    "the_bumblezone.porous_honeycomb_block.description": " 구멍이 가득한 벌집 조각 블록입니다! 꿀이 든 병이나 꿀 양동이로 꿀을 저장할 수 있습니다. 꽃가루가 묻은 벌이 닿으면 자동으로 꿀이 찹니다!",
    "the_bumblezone.filled_porous_honeycomb_block.description": " 꿀이 가득 찬 벌집 조각 블록입니다! 유리병으로 꿀을 꺼낼 수 있지만, 벌집의 보호 효과가 없고 벌의 정수도 섭취하지 않았다면 근처 벌이 화낼 수 있습니다. 다친 벌은 이 블록의 꿀을 먹고 회복하기도 합니다.  \n\n 캐면 다공성 벌집 조각 블록과 벌집 조각 몇 개를 떨어뜨립니다. 행운은 드롭량에 영향을 주며, 섬세한 손길을 사용하면 블록을 그대로 얻습니다. \n\n 비교기가 이 블록을 향하면 레드스톤 신호 1을 출력합니다.",
    "the_bumblezone.empty_honeycomb_brood_block.description": " 내부가 비어 있는 커다란 구멍이 난 벌집 조각 블록입니다. 꽃가루가 묻은 벌이 닿으면 블록을 되살려 안에 유충을 넣습니다! Buzzier Bees의 병에 든 벌이나 Potion of Bees의 벌 물약으로도 되살릴 수 있습니다.",
    "the_bumblezone.honeycomb_brood_block.description": " 벌집 조각 블록의 커다란 구멍 안에 유충이 삽니다! 유충은 4단계에 걸쳐 천천히 자라며 The Bumblezone 차원에서는 더 빨리 자랍니다. 마지막 단계가 되면 블록 앞에 벌이나 꿀 슬라임을 생성할 수 있습니다! 설탕물 병, 꿀이 든 병, 꿀 양동이 또는 일부 모드의 꿀 아이템을 손이나 발사기로 먹이면 성장을 재촉할 수 있습니다. \n\n 유리병으로 꿀을 꺼내면 빈 벌집 유충 블록으로 바뀌고, 유충을 죽인 일 때문에 근처 벌이 화냅니다! 섬세한 손길 없이 이 블록을 캐도 같은 일이 일어납니다. \n\n 비교기가 이 블록을 향하면 내부 유충의 성장 단계에 따라 1~4의 레드스톤 신호를 출력합니다. \n\n 이 블록의 모드 호환성에 관한 자세한 내용은 The Bumblezone 모드 페이지를 확인하세요.",
    "the_bumblezone.sugar_infused_cobblestone.description": " 설탕물이 용암 태그가 붙은 액체와 만나면 생기는 장식 블록입니다. 화로에서 설탕을 태워 경험치를 얻거나 일부 조합법에 사용할 수 있습니다! 닿는 물을 설탕물로 바꾸기도 합니다.",
    "the_bumblezone.sugar_infused_stone.description": " 용암 태그가 붙은 액체가 정지된 설탕물과 만나면 생기는 장식 블록입니다. 화로에서 설탕을 태워 경험치를 얻거나 일부 조합법에 사용할 수 있습니다! 닿는 물을 설탕물로 바꾸기도 합니다.",
    "the_bumblezone.sticky_honey_residue.description": " 꿀 수정, 꿀 수정 조각 또는 꿀 블록을 화로에서 녹여 만드는 매우 끈적이는 찌꺼기입니다. \n\n이 블록에 닿은 몹은 느려지며 벽을 오르는 데도 사용할 수 있습니다. \n 캐는 속도가 느리고 아무것도 떨어뜨리지 않습니다. 빠르게 없애려면 젖은 스펀지, 물병, 물 양동이, 설탕물 병 또는 설탕물 양동이를 들고 표면을 씻듯 우클릭하세요. 흐르는 액체가 통과하거나 피스톤이 밀어도 즉시 파괴됩니다.",
    "the_bumblezone.sticky_honey_redstone.description": " 끈적이는 꿀 찌꺼기와 레드스톤 가루를 합쳐 만드는 유용한 레드스톤 장치 블록입니다. 끈적이는 꿀 찌꺼기의 모든 특성을 가지며 몹이 갇히면 레드스톤 신호 1을 출력합니다. \n\n붙어 있는 블록과 그 너머로 전력을 전달합니다. 바닥에 붙어 있으면 옆면에 붙은 대상에도 전력을 공급합니다.",
    "the_bumblezone.beehive_beeswax.description": " The Bumblezone 차원의 천장과 바닥 경계를 이루는 장식 블록이며 벌집 블록 제작에도 사용됩니다. 도끼로 쉽게 캘 수 있습니다.",
    "the_bumblezone.honey_crystal.description": " The Bumblezone 차원의 동굴과 물속 곳곳에서 발견되는 재생 불가능한 장식 블록입니다. 옆면이나 아래쪽을 포함해 단단한 모든 표면에 설치할 수 있습니다. 물 태그가 붙은 액체로 물에 잠기게 만들 수 있으며, 이때 블록 안의 액체는 설탕물로 바뀝니다. \n\n섬세한 손길 없이 부수면 꿀 수정 조각을 떨어뜨리며 행운이 드롭량에 영향을 줍니다.",
    "the_bumblezone.honey_crystal_shards.description": " 꿀 수정 조각입니다. 먹어 허기를 조금 회복하거나, 화로에서 녹여 끈적이는 꿀 찌꺼기를 만들거나, 꿀 수정 방패를 제작하고 수리하는 데 사용할 수 있습니다.",
    "the_bumblezone.sugar_water_bucket.description": " 설탕물이 든 양동이입니다. 물 양동이와 설탕을 조합하거나 빈 양동이로 설탕물을 담아 얻습니다. 발사기에서도 사용할 수 있습니다!",
    "the_bumblezone.sugar_water_bottle.description": " 설탕물이 든 병입니다. 병으로 설탕물을 담아 얻습니다. \n\n마시면 허기를 아주 조금 회복하고 잠시 성급함 효과를 얻습니다. \n\n벌집 유충 블록에 먹이면 일정 확률로 유충이 한 단계 자랍니다. 벌에게 먹이면 회복시키며 일정 확률로 플레이어의 벌집의 분노 효과를 제거합니다.",
    "the_bumblezone.sugar_water_still.description": " 설탕이 녹아든 물입니다. The Bumblezone 차원에서 찾거나, 물 양동이와 설탕을 조합하거나, 꿀 수정 블록을 물에 잠기게 해 얻을 수 있습니다.\n 설탕물에는 물 태그가 있어 일반 물과 거의 똑같이 행동합니다. 농지를 적시고 산호를 살아 있게 유지할 수 있습니다. \n\n\n 식물 옆에 두면 사탕수수가 훨씬 빨리 자라며 이 효과는 최대 4번 중첩됩니다. \n\n 용암 태그가 붙은 다른 액체와 만나면 설탕이 스며든 조약돌 또는 설탕이 스며든 돌로 바뀝니다.",
    "the_bumblezone.honey_fluid_still.description": " 맛있는 액체 꿀입니다! 매우 천천히 흐르며 안에 있는 몹을 크게 느려지게 합니다. \n\n 양동이나 유리병으로 담을 수 있고, 다친 벌이 들어오면 회복시킵니다. \n\n 꿀도 용암도 아닌 다른 액체와 만나면 반짝이는 꿀 수정 블록으로 바뀝니다. 용암에 닿으면 설탕이 스며든 돌 또는 설탕이 스며든 조약돌로 바뀝니다.",
    "the_bumblezone.royal_jelly_bucket.description": " 여왕벌이 만든 극히 희귀하고 귀중한 꿀을 서툴게 담은 양동이입니다! \n\n 벌에게 먹이면 단계가 매우 높고 지속 시간이 엄청나게 긴 벌에너지 효과를 줍니다. 비히모스는 무한 지속되는 벌에너지 V를 얻고, 여왕이 아닌 비히모스는 즉시 여왕 비히모스가 됩니다. 여왕벌에게 다시 거래하면 매우 귀중한 보상을 얻을 수도 있습니다! \n\n 빈 양동이로 로열 젤리 액체를 담거나 로열 젤리 병 4개와 양동이를 조합해 얻습니다. 발사기에서도 사용할 수 있습니다! \n\n 따뜻한 생물군계에서는 더 빨리, 추운 생물군계에서는 더 느리게 흐릅니다. 네더처럼 매우 뜨거운 차원에서는 반짝이는 꿀 수정 블록으로 바뀝니다. \n\n 병 형태는 여왕의 소망 발전 과제를 완료하면 얻습니다. 전체 발전 과제 계열을 완료하면 여왕벌에게 초기화해 병 보상을 다시 받을 수 있습니다.",
    "the_bumblezone.royal_jelly_bottle.description": " 대대로 전해진 왕실 조리법으로 여왕벌이 만든 놀라운 꿀입니다! 여왕의 소망 발전 과제를 완료하면 얻습니다. 전체 발전 과제 계열을 완료하면 여왕벌에게 초기화해 병 보상을 다시 받을 수 있습니다. \n\n마시면 허기를 많이 회복하고 속도 증가 II, 점프 강화 IV, 느린 낙하 I, 벌에너지 II를 얻습니다! 독, 나약함, 구속 효과도 제거합니다. \n\n 여왕벌에게 다시 거래하면 귀중한 보상을 얻을 수도 있습니다! \n\n 벌에게 먹이면 단계가 매우 높고 오래 지속되는 벌에너지 효과를 줍니다. 비히모스에게는 친밀도를 크게 올리고 무한 지속되는 벌에너지 IV를 부여합니다.",
    "the_bumblezone.royal_jelly_fluid_still.description": " 벌 왕실이 특별히 빚은 꿀입니다! 매우 천천히 흐르며 안에 있는 몹을 크게 느려지게 합니다. \n\n 양동이나 유리병으로 담을 수 있고, 다친 벌이 들어오면 회복시키며 벌에너지와 재생 효과를 줍니다. \n\n 꿀도 용암도 아닌 다른 액체와 만나면 반짝이는 꿀 수정 블록으로 바뀝니다. 용암에 닿으면 설탕이 스며든 돌 또는 설탕이 스며든 조약돌로 바뀝니다. \n\n 병 형태는 여왕의 소망 발전 과제를 완료하면 얻습니다. 전체 발전 과제 계열을 완료하면 여왕벌에게 초기화해 병 보상을 다시 받을 수 있습니다.",
    "the_bumblezone.royal_jelly_block.description": " 로열 젤리를 굳혀 보관하는 블록입니다! 바닐라 꿀 블록과 비슷하지만 피스톤으로 밀 수 없고 당길 수만 있습니다! 이 특성을 활용해 멋진 움직이는 레드스톤 장치를 만들어 보세요. \n\n 병 형태는 여왕의 소망 발전 과제를 완료하면 얻습니다. 전체 발전 과제 계열을 완료하면 여왕벌에게 초기화해 병 보상을 다시 받을 수 있습니다.",
    "the_bumblezone.honey_crystal_shield.description": " 꿀 수정 조각으로 만드는 방패입니다. 처음에는 매우 약하지만 모루에서 꿀 수정 조각으로 수리할수록 강해집니다. 최고 단계에서는 바닐라 방패의 약 두 배에 달하는 내구도를 가집니다. \n\n단, 폭발이나 화염 피해를 막으면 항상 막대한 내구도를 잃습니다. \n\n 방패에 물리 피해를 준 몹을 잠시 느려지게 합니다. 내구성, 귀속 저주, 소실 저주 마법을 부여할 수 있지만 균형을 위해 수선은 부여할 수 없습니다.",
    "the_bumblezone.pile_of_pollen.description": " 커다란 꽃가루 더미입니다! 꽃가루 뭉치가 블록에 부딪히면 만들어집니다. 캘 때 행운은 꽃가루 뭉치 드롭량을 늘리고, 완전히 쌓인 꽃가루 더미에 섬세한 손길을 사용하면 더미 자체를 아이템으로 얻습니다. \n\n 안에 있는 몹을 느려지게 하고 많은 꽃가루 입자를 내뿜습니다. 꽃가루가 묻지 않은 벌이 들어오면 꽃가루를 묻히며 판다는 재채기합니다.\n\n 충분히 두껍게 쌓여 완전히 몸을 가리면 화난 벌에게서 숨을 수 있습니다! 레드스톤 비교기로 높이도 측정할 수 있습니다. \n\n 마지막으로 진동을 막아 스컬크 감지기의 탐지를 차단합니다.",
    "the_bumblezone.pile_of_pollen_suspicious.description": " 어딘가 수상한 커다란 꽃가루 더미입니다... 일반 꽃가루 더미와 거의 똑같이 행동하지만 무언가 더 숨겨져 있습니다. 솔로 털어 무엇이 나오는지 확인해 보세요!",
    "the_bumblezone.pollen_puff.description": " 뭉친 꽃가루로 만든 부드러운 공입니다! 꽃가루 더미를 캐거나, 젖은 스펀지·물병·물 양동이·설탕물 병·설탕물 양동이로 벌을 우클릭해 꽃가루를 씻어 내면 얻습니다. \n\n 던지면 부딪힌 곳에 꽃가루 더미를 만듭니다. 꽃가루가 묻지 않은 벌을 맞히면 꽃가루가 묻고, 판다를 맞히면 재채기하며, 허용된 꽃을 맞히면 번식할 수 있습니다! \n\n 꽃가루 더미는 안에 있는 몹을 느려지게 하고 많은 꽃가루 입자를 내뿜습니다. 꽃가루가 묻지 않은 벌이 들어오면 꽃가루를 묻히며 판다는 재채기합니다.\n\n 충분히 두껍게 쌓여 완전히 몸을 가리면 화난 벌에게서 숨을 수 있습니다! 레드스톤 비교기로 높이도 측정할 수 있습니다.",
    "the_bumblezone.dirt_pellet.description": " 거친 흙과 뿌리내린 흙을 단단히 뭉친 것으로 맞으면 아픕니다! 여러 비행 몹에게 추가 피해를 줍니다. 루트민이 적에게 즐겨 쏘는 강한 밀치기 투사체입니다.",
    "the_bumblezone.bee_bread.description": " 꽃가루와 꿀을 발효해 만든 보기 흉한 알갱이입니다. 벌은 벌빵을 좋아하며 먹이면 순간적으로 기운을 얻어 빨라집니다. 플레이어가 먹어도 영양은 좋지만 1~2초 동안 어지러울 수 있습니다...",
    "the_bumblezone.bee_soup.description": " 발가락이 오그라들 만큼 묘한 맛의 수프입니다. \n\n마시면 오래 지속되는 벌에너지 II를 얻고, 공중 부양·느린 낙하·독·마비·행운 중 하나에 걸릴 수 있습니다.",
    "the_bumblezone.honey_bucket.description": " 액체 꿀이 든 양동이입니다. 꿀이 든 병으로 양동이를 제작해 얻고 다시 꿀이 든 병으로 되돌릴 수 있습니다. 꿀 블록과 양동이로도 제작하고 되돌릴 수 있습니다! \n\n 벌에게 사용하면 완전히 회복시킵니다. 성체 벌에게 사용하면 그 벌과 근처 벌이 번식 상태가 되며, 새끼 벌에게 사용하면 일정 확률로 성체가 됩니다. 발사기에서도 사용할 수 있습니다! \n\n 따뜻한 생물군계에서는 더 빨리, 추운 생물군계에서는 더 느리게 흐릅니다. 네더처럼 매우 뜨거운 차원에서는 반짝이는 꿀 수정 블록으로 바뀝니다.",
    "the_bumblezone.honey_web.description": " 매우 끈적이는 꿀 그물입니다! 갇힌 몹을 크게 느려지게 하지만 젖은 스펀지, 물병, 물 양동이, 설탕물 병 또는 설탕물 양동이로 쉽게 씻어 낼 수 있습니다. 블록에 붙어 있을 필요가 없다는 점을 제외하면 끈적이는 꿀 찌꺼기와 비슷합니다. 검으로 가장 빠르게 캘 수 있습니다.",
    "the_bumblezone.redstone_honey_web.description": " 몹이 갇히면 레드스톤 신호를 출력하는 꿀 그물의 레드스톤 변형입니다. 레드스톤 꿀 그물이 아닌 꿀 그물 블록에서는 레드스톤 신호를 받을 수 없습니다. 나머지 행동은 꿀 그물과 같으며 검으로 가장 빠르게 캘 수 있습니다.",
    "the_bumblezone.honey_cocoon.description": " 꿀로 만든 기묘한 고치입니다! 안에 아이템을 보관할 수 있습니다. 고치 안의 빈 벌집 유충 블록은 벌 먹이를 소비해 유충이 든 블록으로 바뀝니다! 고치가 물에 잠기면 시간이 지날수록 아이템을 잃기도 합니다...",
    "the_bumblezone.music_disc_flight_of_the_bumblebee_rimsky_korsakov.description": " 귀 기울이면 여전히 성난 벌 떼가 윙윙거리는 소리가 들립니다... 이 희귀 음반은 떠돌이 상인이나 The Bumblezone의 일부 구조물에서 얻습니다! 곡은 Rimsky Korsakov의 Flight of the Bumblebee를 MIDI로 연주한 버전입니다.",
    "the_bumblezone.music_disc_honey_bee_rat_faced_boy.description": " 벌과 함께 신나는 명곡을 즐기세요! 이 희귀 음반은 떠돌이 상인이나 The Bumblezone의 일부 구조물에서 얻습니다! 곡은 Rat Faced Boy의 Honey Bee이며 https://acidburp.bandcamp.com/track/honey-bee 에서 구매할 수 있습니다. 좋아하는 곡의 음악가를 언제나 응원해 주세요!",
    "the_bumblezone.music_disc_rivers_of_honey_moserao.description": ' 느긋한 노래와 함께 차원의 흐름에 몸을 맡겨 보세요! 이 희귀 음반은 떠돌이 상인이나 The Bumblezone의 일부 구조물에서 얻습니다! 곡은 Moserao의 Rivers of Honey이며 https://moserao.bandcamp.com/track/rivers-of-honey-2 에서 구매할 수 있습니다. 좋아하는 곡의 음악가를 언제나 응원해 주세요!"',
    "the_bumblezone.music_disc_la_bee_da_loca.description": " 놀라운 The Bumblezone을 탐험하며 부드러운 선율을 즐기세요! 이 희귀 음반은 떠돌이 상인이나 The Bumblezone의 일부 구조물에서 얻습니다! 곡은 LudoCrypt의 La Bee-da Loca이며 https://ludocrypt.bandcamp.com/track/la-bee-da-loca 에서 구매할 수 있습니다. 좋아하는 곡의 음악가를 언제나 응원해 주세요!",
    "the_bumblezone.music_disc_bee_laxing_with_the_hom_bees.description": " 모든 벌이 좋아하는 차분한 노래를 들으며 쉬어 가세요! 이 희귀 음반은 떠돌이 상인이나 The Bumblezone의 일부 구조물에서 얻습니다! 곡은 LudoCrypt의 Bee-laxing with the Hom-bees이며 https://ludocrypt.bandcamp.com/track/bee-laxing-with-the-hom-bees 에서 구매할 수 있습니다. 좋아하는 곡의 음악가를 언제나 응원해 주세요!",
    "the_bumblezone.music_disc_bee_ware_of_the_temple.description": " 불길한 구조물에 어울리는 불길한 노래입니다... 이 희귀 음반은 떠돌이 상인이나 The Bumblezone의 일부 구조물에서 얻습니다! 곡은 LudoCrypt의 Bee-ware of the Temple이며 https://ludocrypt.bandcamp.com/track/bee-ware-of-the-temple 에서 구매할 수 있습니다. 좋아하는 곡의 음악가를 언제나 응원해 주세요!",
    "the_bumblezone.music_disc_knowing_renren.description": " 이 노래와 함께 파티를 즐기세요! 이 희귀 음반은 떠돌이 상인이나 The Bumblezone의 일부 구조물에서 얻습니다! 곡은 RenRen의 Knowing입니다.",
    "the_bumblezone.music_disc_radiance_renren.description": " 함께 들으며 넘치는 활력을 느껴 보세요! 이 희귀 음반은 떠돌이 상인이나 The Bumblezone의 일부 구조물에서 얻습니다! 곡은 RenRen의 Radiance입니다.",
    "the_bumblezone.music_disc_life_renren.description": " 루트민 사이에서 고전으로 통하는 노래입니다! 이 희귀 음반은 떠돌이 상인이나 The Bumblezone의 일부 구조물에서 얻습니다! 곡은 RenRen의 Life입니다.",
    "the_bumblezone.music_disc_drowning_in_despair.description": " 갇힌 듯한 느낌을 불러일으키는 노래입니다! 이 희귀 음반은 떠돌이 상인이나 The Bumblezone의 일부 구조물에서 얻습니다! 곡은 Punpudle의 Drowning in Despair이며 https://punpudle.bandcamp.com/track/drowning-in-despair-blue-sempiternal-sanctum 에서 구매할 수 있습니다. 좋아하는 곡의 음악가를 언제나 응원해 주세요!",
    "the_bumblezone.music_disc_a_last_first_last.description": " 마지막 결전에 어울리는 노래입니다! 이 희귀 음반은 떠돌이 상인이나 The Bumblezone의 일부 구조물에서 얻습니다! 곡은 Punpudle의 A Last First Last이며 https://punpudle.bandcamp.com/track/a-last-first-last-white-sempiternal-sanctum 에서 구매할 수 있습니다. 좋아하는 곡의 음악가를 언제나 응원해 주세요!",
    "the_bumblezone.music_disc_beenna_box.description": " 몬스터를 때려눕히기 좋은 곡입니다! 이 희귀 음반은 떠돌이 상인이나 The Bumblezone의 일부 구조물에서 얻습니다! 곡은 Punpudle의 Beenna Box이며 https://punpudle.bandcamp.com/track/beenna-box-red-sempiternal-sanctum 에서 구매할 수 있습니다. 좋아하는 곡의 음악가를 언제나 응원해 주세요!",
    "the_bumblezone.bee_stinger.description": " 여왕벌이 흔히 주는 선물입니다! 활과 쇠뇌에 낮은 피해의 탄약으로 사용하면 언데드가 아닌 몹에게 일정 확률로 독, 나약함, 구속 또는 마비를 부여합니다. \n\n 양조기에서 어색한 물약과 함께 사용하면 지속 시간이 긴 독 물약을 만들 수 있습니다! \n\n 벌침을 잃은 벌에게 우클릭하면 벌침을 다시 붙여 줄 수 있습니다.",
    "the_bumblezone.stinger_spear.description": " 벌침을 이용해 만든 약하지만 치명적인 투척 창입니다! 부싯돌이나 벌침으로 수리하고 마법을 부여할 수 있습니다. 언데드가 아닌 몹을 맞히면 항상 약한 독을 부여합니다.",
    "the_bumblezone.honey_compass.description": " 꿀이 스며든 나침반입니다. 벌통이나 벌집을 우클릭하면 그 블록의 위치를 계속 가리킵니다! The Bumblezone 차원에서 허공을 우클릭하면 어떤 구조물을 가리키는 듯합니다...",
    "the_bumblezone.buzzing_briefcase.description": " 벌을 최대 14마리까지 잡을 수 있는 희귀 도구입니다! 벌을 우클릭해 잡습니다. \n\nShift+우클릭으로 UI를 열어 벌을 회복시키고, 벌침을 되돌려 주고, 꽃가루를 묻히거나 새끼 벌을 성장시킬 수 있습니다! \n\n블록을 좌클릭하면 벌 한 마리를 풀어 주고, Shift+좌클릭하면 모든 벌을 풀어 줍니다. 엔티티를 좌클릭하면 풀려난 벌이 그 엔티티에게 화를 냅니다!",
    "the_bumblezone.bee_cannon.description": " 벌을 발사하는 내구성이 의심스러운 대포입니다! 벌을 최대 3마리까지 저장합니다. 사용 버튼을 누르고 있다가 놓으면 벌을 발사합니다! 발사할 때 바라보던 벌 이외의 엔티티를 잠시 공격합니다. \n\n 설탕이 스며든 돌이나 설탕이 스며든 조약돌로 수리할 수 있습니다.",
    "the_bumblezone.crystal_cannon.description": " 꿀 수정 조각을 발사하는 강력하고 치명적이지만 내구성이 의심스러운 대포입니다! 조각을 최대 3개까지 저장합니다. 사용 버튼을 누르고 있다가 놓으면 높은 피해와 밀치기를 지닌 조각을 발사합니다! \n\n 꿀 수정 조각, 설탕이 스며든 돌 또는 설탕이 스며든 조약돌로 수리할 수 있습니다.",
    "the_bumblezone.flower_headwear.description": " 가죽 모자와 꽃으로 제작하는 크고 염색 가능한 특별한 꽃잎 장식입니다. 착용하면 벌이 플레이어를 거대한 꽃으로 착각해 다가옵니다! 벌집의 분노 지속 시간이 두 배 빠르게 줄고, 일부 구조물에 들어갈 때 벌집의 분노를 얻지 않습니다. 가죽 갑옷처럼 염색할 수 있습니다! 이 아이템을 포함해 벌 테마 착용 아이템을 4개 이상 장착하면 벌집의 분노 지속 시간이 더 빨리 줄어듭니다.",
    "the_bumblezone.glistering_honey_crystal.description": " 결정화된 꿀로 이루어진 빛나는 광원입니다. The Bumblezone의 수정 협곡 생물군계에서만 발견됩니다.\n\n 부수면 많은 꿀 수정 조각을 주며, 제련하면 많은 끈적이는 꿀 찌꺼기가 됩니다. 장식이나 조명으로도 좋습니다!\n\n 양조기에서 어색한 물약과 조합하면 행운의 물약을 만듭니다! 행운 효과는 주로 일부 데이터팩이나 모드 전리품 표의 드롭을 개선할 수 있습니다.\n 이웃한 물 원천 블록도 설탕물로 바꿉니다.",
    "the_bumblezone.super_candle.description": " 많은 빛을 내는 거대한 장식용 양초입니다!\n\n 일반 마인크래프트 양초처럼 불을 붙이고 물에 잠기게 할 수 있습니다. 불붙은 투사체가 맞아도 점화되며, 불꽃 안의 몹은 약한 피해를 받으면서 불이 붙습니다.\n\n 대형 양초는 쌓을 수 있습니다. 영혼 모래, 영혼 흙 또는 영혼이 가득한 다른 블록을 아래에 두면 피글린을 쫓아내는 영혼 불꽃이 됩니다!\n\n 비교기가 대형 양초 받침을 향하면 불이 켜졌을 때 신호 5를 냅니다. 대형 양초 심지를 향하면 영혼 불꽃일 때 3, 일반 불꽃일 때 5를 냅니다. 발사기로도 양초에 불을 붙일 수 있습니다.",
    "the_bumblezone.potion_candle.description": " 근처 엔티티에 효과를 퍼뜨리는 강력한 마법 양초입니다!\n\n 기본적으로 일반 대형 양초와 똑같이 행동하지만, 물약 양초 제작에 사용한 물약에 따라 여러 상태 효과를 담아 근처 엔티티에게 부여할 수 있습니다.\n\n 물약 양초의 힘이 떨어지면 불이 꺼집니다. 다시 불을 붙이면 상태 효과 부여가 재개됩니다. 여러 물약 조합으로 어떤 물약 양초를 만들 수 있는지 확인해 보세요!",
    "the_bumblezone.crystalline_flower.description": " 마법의 꿀 수정으로 이루어진 희귀한 꽃으로, 아이템이나 경험치를 소비해 성장합니다! 반짝이는 꿀 수정, 자수정 또는 자수정과 비슷한 수정 느낌을 지닌 일부 모드 블록 위에서만 살 수 있습니다. 지나가는 몹은 가시에 피해를 받습니다. \n\n 우클릭하면 꽃에게 먹이를 주거나 책과 마법이 부여된 책에 마법을 추가하는 화면이 열립니다! 꽃의 티어가 높을수록 적용 가능한 마법이 늘고 마법 단계도 높아집니다.\n\n 최고 티어에서는 '보물'로 표시된 마법도 사용할 수 있습니다! 참고로 마법이 부여된 책은 UI에서 직접 먹여야 일부 경험치를 되찾거나 마법을 더 추가할 수 있습니다. \n\n캘 때 섬세한 손길이 필요하지 않으며, 현재 티어가 아이템에 저장된 채로 꽃 자체를 떨어뜨립니다.",
    "the_bumblezone.windy_air.description": " 엔티티를 일정한 방향으로 밀어내는 바람 부는 블록입니다. \n\n이 아이템을 들면 근처의 모든 바람 부는 공기 블록이 보입니다. 여왕벌에게 The Bumblezone 갑옷이나 도구를 거래하면 이 아이템을 받을 수 있습니다. \n\n다른 블록이나 액체로 대체할 수 있습니다. 바람 부는 공기를 들면 블록을 더 쉽게 보고 캘 수 있습니다.",
    "the_bumblezone.heavy_air.description": " 무거운 기운으로 엔티티를 아래로 끌어당기고 여러 비행 능력을 비활성화하는 블록입니다. \n\n아이템 형태는 명령어나 크리에이티브 메뉴에서만 얻습니다. 이 아이템을 들면 근처의 모든 무거운 공기 블록이 보입니다.",
    "the_bumblezone.essence_of_the_bees.description": " 여왕벌의 여왕의 소망 발전 과제 계열에서 얻는 게임 후반부의 소모성 보물입니다! 정수 자체에서 강력하면서도 따뜻한 기운이 퍼지는 듯합니다... 섭취하면 다음 보너스를 영구히 얻습니다.\n\n벌집 미로에 들어가도 벌집의 분노 효과를 얻지 않습니다.\n\n왕좌 기둥에서 여왕벌 근처에 가도 채굴 피로를 얻지 않습니다.\n\n액체 꿀에 들어가면 재생 효과를 얻습니다.\n\n로열 젤리 액체에 들어가면 짧은 벌에너지 효과와 더 강한 재생 효과를 얻습니다.\n\n벌통과 벌집을 캐거나, 병으로 꿀을 담거나, 가위로 벌집 조각을 채취해도 벌이 화내지 않습니다. 모닥불도 필요 없습니다!\n\n꿀이 찬 다공성 벌집 조각 블록에서 안전하게 꿀을 채취하며 벌집의 분노를 얻지 않습니다.\n\n꿀 슬라임에게서 꿀을 채취해도 꿀 슬라임이 화내지 않습니다.\n\n참고: 설정 파일에서 바꾸지 않는 한 죽어도 이 효과는 유지됩니다.",
    "the_bumblezone.essence_raging.description": " 붉은 영원 성소 구조물에서 얻는 게임 후반 아이템입니다! 분노와 파괴의 충동을 내뿜습니다. \n\n보조 손에 들면 근처 몬스터를 강조 표시합니다. 표시된 몬스터를 죽이면 힘 효과를 얻고, 연속으로 처치할수록 효과가 강해집니다. 연속 처치 7회에서 최대가 된 뒤 초기화되며, 처치 사이에 너무 오래 걸려도 초기화됩니다. \n\n힘을 모두 소모하면 재사용 대기시간에 들어갑니다. 벌의 정수를 섭취한 플레이어의 인벤토리에서 30분이 지나면 충전됩니다.",
    "the_bumblezone.essence_knowing.description": " 보라색 영원 성소 구조물에서 얻는 게임 후반 아이템입니다! 필멸자의 정신으로는 감당하기 힘든 지식을 전합니다. \n\n보조 손에 들면 아주 먼 거리까지 근처의 모든 몬스터와 생명체를 강조 표시합니다. 상자, 생성기, 수상한 블록 같은 일부 블록 엔티티도 시야 안에서 강조 표시하며, 현재 들어와 있는 구조물의 이름도 알려 줍니다! \n\n힘을 모두 소모하면 재사용 대기시간에 들어갑니다. 벌의 정수를 섭취한 플레이어의 인벤토리에서 15분이 지나면 충전됩니다.",
    "the_bumblezone.essence_calming.description": " 푸른 영원 성소 구조물에서 얻는 게임 후반 아이템입니다! 주변 모두에게 한 번도 느껴 본 적 없는 평온을 가져옵니다. \n\n보조 손에 들면 많은 몹이 소지자에게 더는 화내지 않습니다. 몹이 소지자를 해치거나 소지자가 플레이어나 몹을 공격하면 효과를 잃습니다. 달릴 때는 아이템의 힘도 빠르게 소모됩니다. \n힘을 모두 소모하면 재사용 대기시간에 들어갑니다. 벌의 정수를 섭취한 플레이어의 인벤토리에서 10분이 지나면 충전됩니다.",
    "the_bumblezone.essence_life.description": " 초록색 영원 성소 구조물에서 얻는 게임 후반 아이템입니다! 믿기 어려울 만큼 빠르게 생명을 번성시킵니다. \n\n보조 손에 들면 근처 작물과 식물이 빠르게 자랍니다. 소지자의 근처 아군과 길들인 동물도 회복시키며, 회복된 대상의 시듦과 독 효과를 제거합니다. \n\n힘을 모두 소모하면 재사용 대기시간에 들어갑니다. 벌의 정수를 섭취한 플레이어의 인벤토리에서 10분이 지나면 충전됩니다.",
    "the_bumblezone.essence_radiance.description": " 노란색 영원 성소 구조물에서 얻는 게임 후반 아이템입니다! 태양의 축복과 압도적인 힘을 품고 있습니다. \n\n보조 손에 들고 낮의 하늘을 바로 볼 수 있으면 재생 I, 속도 증가 I, 포화 I, 저항 II, 성급함 II를 얻습니다. 햇빛을 받는 동안 갑옷도 천천히 수리됩니다. \n\n힘을 모두 소모하면 재사용 대기시간에 들어갑니다. 벌의 정수를 섭취한 플레이어의 인벤토리에서 10분이 지나면 충전됩니다.",
    "the_bumblezone.essence_continuity.description": " 하얀 영원 성소 구조물에서 얻는 게임 후반 아이템입니다! 논리와 존재를 거스르며 이 세상에 있으면서도 그 너머에 존재합니다. \n\n보조 손에 들면 죽음도 소지자를 죽일 수 없습니다. 대신 마지막으로 저장한 재생성 지점으로 순간이동하며 체력과 허기가 모두 회복되고, 중립 및 해로운 상태 효과가 제거되며, 낙하 거리와 몸에 붙은 불이 초기화됩니다. 경험치와 아이템도 그대로 유지됩니다. \n\n\n 죽을 뻔한 위치와 상황을 자세히 적은 쓰인 책도 받습니다.\n\n힘을 모두 소모하면 재사용 대기시간에 들어갑니다. 벌의 정수를 섭취한 플레이어의 인벤토리에서 40분이 지나면 충전됩니다.",
    "the_bumblezone.hanging_gardens_flowers.description": " The Bumblezone 차원의 매달린 정원 구조물에서 발견되는 꽃입니다! 참고로 블록과 아이템의 연결이 명확하지 않은 꽃은 가능한 종류가 모두 이 페이지에 표시되지 않을 수 있습니다.",
    "the_bumblezone.crystalline_flower_can_be_placed_on.description": " 결정꽃을 위에 심을 수 있는 수정처럼 생긴 블록입니다!",
}

BANNER_MOTIFS = {
    "bee": "벌",
    "honeycombs": "벌집 조각",
    "swords": "검",
    "sun": "태양",
    "pluses": "십자",
    "eyes": "눈",
    "peace": "평화",
    "arrows": "화살",
}

ARMOR_DESCRIPTIONS = {
    "carpenter_bee_boots": " 최고의 벌 직조공이 만든 놀라운 옷입니다! 나무, 판자, 나뭇잎, 벌집 조각 블록의 벽을 달리고 벽에서 뛰어오를 수 있습니다! 해당 블록 중앙에서 아래를 보며 웅크리면 자동으로 블록을 캡니다. 벌집 조각, 가죽, 양털 또는 토끼 가죽으로 수리할 수 있습니다. 벌 갑옷이나 벌 장신구를 더 많이 착용할수록 벽에 더 오래 매달리고 블록을 더 빨리 자동 채굴합니다.",
    "honey_bee_leggings": " 최고의 벌 직조공이 만든 놀라운 옷입니다! 구속을 일으키는 여러 The Bumblezone 블록의 감속을 견디고, 꽃이나 꽃가루 더미에서 꽃가루를 모읍니다! 꽃가루가 가득 찼을 때 웅크리면 꽃가루 뭉치를 생성합니다. 벌집 조각, 가죽, 양털 또는 토끼 가죽으로 수리할 수 있습니다. 벌 갑옷이나 벌 장신구를 더 많이 착용할수록 꽃에서 꽃가루를 모을 확률이 높아지고 구속 효과가 더 빨리 사라집니다!",
    "bumble_bee_chestplate": " 최고의 벌 직조공이 만든 놀라운 옷입니다! 점프한 뒤 언제든 점프 버튼을 누르고 있으면 잠시 날 수 있습니다. 벌에너지 효과를 얻으면 비행 성능이 좋아집니다! 벌집 조각, 가죽, 양털 또는 토끼 가죽으로 수리할 수 있습니다. 착용한 벌 갑옷이나 벌 장신구 하나마다 비행 시간이 더 늘어납니다!",
    "stingless_bee_helmet": " 최고의 벌 직조공이 만든 놀라운 옷입니다! 웅크리면 모든 벌과 비히모스가 발광해 보입니다. 착용 중에는 멀미 효과의 지속 시간이 두 배 빠르게 줄어듭니다. 벌집 조각, 가죽, 양털 또는 토끼 가죽으로 수리할 수 있습니다.\n\n 벌 갑옷이나 벌 장신구를 더 많이 착용할수록 멀미와 독 효과가 더 빨리 사라집니다. 벌 윤곽선 표시 범위도 늘어나며, 추가 장비를 착용했다면 일어난 뒤에도 잠시 발광이 유지됩니다.",
}

SUPER_CANDLE_COLORED = " 색이 있는 거대한 장식용 양초로 많은 빛을 냅니다!\n\n 일반 마인크래프트 양초처럼 불을 붙이고 물에 잠기게 할 수 있습니다. 불붙은 투사체가 맞아도 점화되며, 불꽃 안의 몹은 약한 피해를 받으면서 불이 붙습니다.\n\n 대형 양초는 쌓을 수 있습니다. 영혼 모래, 영혼 흙 또는 영혼이 가득한 다른 블록을 아래에 두면 피글린을 쫓아내는 영혼 불꽃이 됩니다!\n\n 비교기가 대형 양초 받침을 향하면 불이 켜졌을 때 신호 5를 냅니다. 대형 양초 심지를 향하면 영혼 불꽃일 때 3, 일반 불꽃일 때 5를 냅니다. 발사기로도 양초에 불을 붙일 수 있습니다."

STRING_CURTAIN = " 구슬과 실로 만든 아름다운 커튼으로 블록의 옆면이나 아랫면에 붙일 수 있습니다!\n\n 실을 들고 우클릭하면 커튼이 아래로 늘어납니다. 여러 비행 곤충 몹은 이 블록을 통과하기 매우 어려워 일정 구역에 벌이 드나들지 못하게 막기 좋습니다!\n\n 발사기에 실을 넣어 늘릴 수도 있습니다. 비교기는 커튼이 비교기보다 얼마나 아래까지 늘어났는지 측정합니다. \n\n 마지막으로 진동을 막아 스컬크 감지기의 탐지를 차단합니다."

CARVABLE_WAX = " 가위나 검을 들고 우클릭해 조각할 수 있는 단단한 밀랍 블록입니다! 새긴 무늬에 따라 비교기에 서로 다른 신호를 출력합니다."

ANCIENT_WAX = " 오래전 조각된 뒤 수백 년에 걸쳐 크게 굳은 밀랍입니다. 알 수 없는 기묘한 힘이 깃들어 폭발에 매우 강합니다. \n\n검이나 가위로 우클릭해 블록의 무늬를 바꿀 수 있습니다. \n\n벌의 정수를 섭취한 적이 없는 플레이어가 위에 서면 구속, 채굴 피로, 나약함을 얻습니다..."

ANCIENT_WAX_SINGLE_BREAK = " 오래전 조각된 뒤 수백 년에 걸쳐 크게 굳은 밀랍입니다. 알 수 없는 기묘한 힘이 깃들어 폭발에 매우 강합니다. 검이나 가위로 우클릭해 블록의 무늬를 바꿀 수 있습니다. \n\n벌의 정수를 섭취한 적이 없는 플레이어가 위에 서면 구속, 채굴 피로, 나약함을 얻습니다..."

LUMINOUS_COLORS = {
    "red": "붉은",
    "purple": "보라색",
    "blue": "푸른",
    "green": "초록색",
    "yellow": "노란색",
    "white": "하얀",
}


def luminescent_wax_description(kind: str, color: str | None) -> str:
    """발광 밀랍 변형의 공통 동작과 색상별 첫 문장을 조합한다."""
    korean_kind = {"channel": "통로", "corner": "모서리 통로", "node": "마디"}[kind]
    if color is None:
        if kind == "channel":
            first = " 덧없이 사라지는 기묘한 힘이 조금 남은 빈 통로로, 폭발에 매우 강합니다. "
        elif kind == "corner":
            first = " 기묘한 힘의 잔재가 남은 빈 모서리 통로로, 폭발에 매우 강합니다. "
        else:
            first = " 기묘한 힘의 잔재가 남은 빈 마디로, 폭발에 매우 강합니다. "
    elif kind == "channel":
        first = f" {LUMINOUS_COLORS[color]} 이계의 힘을 경로를 따라 전달하는 통로로, 폭발에 매우 강합니다. "
    else:
        first = f" {LUMINOUS_COLORS[color]} 이계의 힘이 넘쳐흐르는 {korean_kind}로, 폭발에 매우 강합니다. "
    return (
        first
        + "\n\n검이나 가위로 우클릭해 블록의 방향을 바꿀 수 있습니다. 벌의 정수를 섭취한 플레이어가 위에 서면 속도 증가, 저항, 벌에너지 효과를 얻습니다. "
        + "\n\n벌의 정수를 섭취한 적이 없는 플레이어가 위에 서면 구속, 채굴 피로, 나약함을 얻습니다..."
    )


def translate(key: str, source: str) -> str | None:
    """키별 원문 대조 번역 또는 검수된 반복 설명을 반환한다."""
    if key in TRANSLATIONS:
        return TRANSLATIONS[key]
    banner_match = re.fullmatch(
        r"the_bumblezone\.banner_pattern_(\w+)\.description", key
    )
    if banner_match and banner_match.group(1) in BANNER_MOTIFS:
        motif = BANNER_MOTIFS[banner_match.group(1)]
        return (
            f" The Bumblezone 차원의 일부 구조물과 수상한 꽃가루 더미에서 "
            f"발견되는 희귀한 {motif} 현수막 무늬입니다."
        )
    for armor, translated in ARMOR_DESCRIPTIONS.items():
        if key.startswith(f"the_bumblezone.{armor}_"):
            return translated
    if key.startswith("the_bumblezone.bumble_bee_chestplate_trans_"):
        return ARMOR_DESCRIPTIONS["bumble_bee_chestplate"]
    if re.fullmatch(r"the_bumblezone\.super_candle_(?!wick|base)\w+\.description", key):
        return SUPER_CANDLE_COLORED
    if re.fullmatch(r"the_bumblezone\.string_curtain_\w+\.description", key):
        return STRING_CURTAIN
    if re.fullmatch(r"the_bumblezone\.carvable_wax(?:_\w+)?\.description", key):
        return CARVABLE_WAX
    if key.startswith("the_bumblezone.ancient_wax_") and key.endswith(".description"):
        if key == "the_bumblezone.ancient_wax_compound_eyes_slab.description":
            return ANCIENT_WAX_SINGLE_BREAK
        return ANCIENT_WAX
    luminous_match = re.fullmatch(
        r"the_bumblezone\.luminescent_wax_(channel|corner|node)(?:_(red|purple|blue|green|yellow|white))?\.description",
        key,
    )
    if luminous_match:
        return luminescent_wax_description(*luminous_match.groups())
    del source
    return None
