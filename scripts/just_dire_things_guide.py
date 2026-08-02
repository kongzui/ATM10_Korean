#!/usr/bin/env python3
"""Just Dire Things Patchouli 가이드와 관련 표시 경로를 번역·검증한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path
from zipfile import ZipFile

import ars_family
import just_dire_things_family as language
from local_paths import PROJECT_ROOT, resolve_source_root


WORK_ROOT = PROJECT_ROOT / "working/just_dire_things/guide"
ENGLISH_ROOT = WORK_ROOT / "en_us"
KOREAN_ROOT = WORK_ROOT / "ko_kr"
OUTPUT_ROOT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/justdirethings/patchouli_books/justdirethingsbook/ko_kr"
)
BOOK_OUTPUT = (
    PROJECT_ROOT
    / "output/overrides/kubejs/data/justdirethings/patchouli_books/justdirethingsbook/book.json"
)
CACHE_FILE = PROJECT_ROOT / "temp/just_dire_things_guide_candidate_cache.json"
BOOK_PREFIX = "assets/justdirethings/patchouli_books/justdirethingsbook/en_us/"
BOOK_SOURCE = "data/justdirethings/patchouli_books/justdirethingsbook/book.json"
VISIBLE_FIELDS = {"name", "description", "title", "text"}
PATCHOULI_TAG = re.compile(r"\$\([^)]+\)")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")

CATEGORY_OVERRIDES = {
    "Machines": "기계",
    "Armor": "방어구",
    "Upgrades": "업그레이드",
    "Goo": "구",
    "Items": "아이템",
    "Tools": "도구",
    "Resources": "자원",
    "Fluids": "유체",
    "Lots of machines - focused mainly around automation!": "자동화에 초점을 맞춘 다양한 기계입니다!",
    "Each of the armor pieces has a bunch of cool abilities - some assembly required!": (
        "각 방어구 부위에는 멋진 능력이 여럿 있으며, 일부는 조립이 필요합니다!"
    ),
    "Armor and Tools can both accept upgrades, which are detailed here.": (
        "방어구와 도구에 적용할 수 있는 업그레이드를 설명합니다."
    ),
    "The goo! No ones quite sure how it works, but it seems to be alive....somehow?$(br2)It appears to consume certain items, leaving behind small bits of leftovers that appear pretty useful!": (
        "구입니다! 작동 원리는 아무도 확실히 모르지만, 어쩐지 살아 있는 것 같습니다..."
        "$(br2)특정 아이템을 먹어 치우고 꽤 쓸모 있어 보이는 작은 부산물을 남깁니다!"
    ),
    "Theres a bunch of other fun items to try!": "사용해 볼 만한 재미있는 아이템이 더 있습니다!",
    "Each of the tools has a bunch of cool abilities - some assembly required!": (
        "각 도구에는 멋진 능력이 여럿 있으며, 일부는 조립이 필요합니다!"
    ),
}

SOURCE_OVERRIDES = {
    "The simple block breaker uses a tool (such as a pickaxe or shovel) to break the block it is facing. It cannot operate without a tool, and will damage the tool (or consume power) whenever a block is broken, just like what would happen if a player was using it.": (
        "간단한 블록 파괴기는 곡괭이나 삽 같은 도구로 앞의 블록을 파괴합니다. 도구 없이는 "
        "작동하지 않으며, 플레이어가 직접 사용할 때처럼 블록을 부술 때마다 도구의 내구도나 "
        "에너지를 소비합니다."
    ),
    "The Inventory Holder is essential a super advanced Armor Stand!$(br2)When placed in the world, it acts sort of like a chest, simply right click to access the inventory.  You'll notice it has a UI matching your player's inventory - with slots for the Hotbar, items, Armor, and even your offhand!": (
        "인벤토리 저장기는 매우 발전된 방어구 거치대와 같습니다!$(br2)월드에 놓으면 상자처럼 "
        "작동하며 우클릭해 인벤토리를 엽니다. 화면에는 플레이어 인벤토리와 같은 단축바, 일반 "
        "아이템, 방어구, 보조 손 슬롯이 있습니다."
    ),
    "Initially you can insert whatever you like into the inventory. Once an item is placed into the inventory, you can control-click on it to 'save' that item, including its stack size.$(br2)By doing this, you've now applied a filter to that slot, ensuring that only items of that type can fit there. If you want this filter to apply NBT filtering, toggle Compare NBT with the button on the top right.": (
        "처음에는 아무 아이템이나 넣을 수 있습니다. 넣은 아이템을 Ctrl + 클릭하면 아이템 "
        "종류와 묶음 수량을 해당 슬롯에 저장합니다.$(br2)이후 그 슬롯에는 필터와 일치하는 "
        "아이템만 들어갑니다. NBT까지 비교하려면 오른쪽 위의 'NBT 비교'를 켜세요."
    ),
    "When you shift click into the inventory, the following logic will apply in this order:$(br2)$(li)Attempt to find a matching filter, and insert there.$(li)Attempt to insert into the same slot in the inventory as it was in the players (For example, top right corner to top right corner).$(li)Finally, insert as normal (starting with top left corner).": (
        "Shift + 클릭으로 아이템을 넣으면 다음 순서로 처리합니다:$(br2)$(li)일치하는 필터 슬롯을 "
        "찾아 넣습니다.$(li)플레이어 인벤토리와 같은 위치의 슬롯에 넣습니다. 예를 들어 오른쪽 "
        "위 아이템은 오른쪽 위 슬롯으로 갑니다.$(li)마지막으로 왼쪽 위부터 일반 방식으로 넣습니다."
    ),
    "If you toggle on 'Filtered Items Only' via the button on the top right, items will not be allowed to be inserted into 'unfiltered' slots.  This means that if you attempt to put an item into a slot without a filter, it won't be allowed.$(br2)If you toggle on 'Compare Stack Sizes', the filtered slots will only accept up to their saved stack size.": (
        "오른쪽 위의 '필터에 맞는 아이템만'을 켜면 필터가 없는 슬롯에는 아이템을 넣을 수 "
        "없습니다.$(br2)'묶음 수량 비교'를 켜면 필터 슬롯은 저장된 수량까지만 받습니다."
    ),
    "On the top left, there are buttons to control how pipes, hoppers, etc can interact with this machine.$(br2)When Filtered Items Only is enabled, it will only allow you to pipe into slots with a matching filter, and 'Compare Stack sizes' works as above for insert.$(br2)When extracting, slots with a filter applied will be ignored, and Compare Stack Sizes determines if extracting will try to match the filter's stack size.": (
        "왼쪽 위 버튼은 파이프와 호퍼가 이 기계와 상호 작용하는 방식을 제어합니다.$(br2)"
        "'필터에 맞는 아이템만'을 켜면 일치하는 필터 슬롯으로만 아이템을 넣을 수 있고, "
        "'묶음 수량 비교'도 위와 같이 적용됩니다.$(br2)아이템을 꺼낼 때는 필터가 적용된 "
        "슬롯을 건너뛰며, '묶음 수량 비교'에 따라 저장된 수량을 남길지 결정합니다."
    ),
    "The 'Show Fake Player' button on the top left will toggle the rendered player above the block.$(br2)Ctrl+Shift Clicking one of the hotbar slots in the UI will place a red border around that slot. This determines which inventory slot is rendered in the fake player's 'main hand'.  This is purely cosmetic.": (
        "왼쪽 위의 '가짜 플레이어 표시' 버튼으로 블록 위의 가짜 플레이어를 보이거나 숨깁니다."
        "$(br2)단축바 슬롯을 Ctrl + Shift + 클릭하면 빨간 테두리가 생깁니다. 해당 슬롯의 "
        "아이템이 가짜 플레이어의 주 손에 표시되며 외형만 바뀝니다."
    ),
    "Towards the bottom of the UI is a Pull Items and Push Items button.  Push Items will attempt to insert all the items in your inventory into the block, and match the filter slots you've defined.$(br2)Note: The 'filtered items only' and 'compare stack sizes' buttons on the top right of the UI are respected when you push.$(br2)Pull Inventory will pull items out of the block, and place them in your inventory.": (
        "화면 아래쪽에는 '아이템 가져오기'와 '아이템 내보내기' 버튼이 있습니다. '아이템 "
        "내보내기'는 플레이어 인벤토리의 아이템을 필터에 맞춰 블록으로 옮깁니다.$(br2)"
        "이때 오른쪽 위의 '필터에 맞는 아이템만'과 '묶음 수량 비교' 설정도 적용됩니다."
        "$(br2)'아이템 가져오기'는 블록의 아이템을 플레이어 인벤토리로 옮깁니다."
    ),
    "The swap inventory button attempts to swap each inventory slot in your player's inventory with the matching inventory slots in the block's inventory.$(br2)It is recommended to do this with minimal filtering, otherwise items won't be able to switch over, however you are welcome to configure this in any way you like, feel free to experiment with the different options!": (
        "'인벤토리 교환' 버튼은 플레이어 인벤토리의 각 슬롯을 블록 인벤토리의 같은 위치와 "
        "맞바꿉니다.$(br2)필터가 많으면 아이템을 바꾸지 못할 수 있으므로 최소한의 필터만 "
        "사용하는 것이 좋습니다. 필요에 맞게 여러 설정을 시험해 보세요!"
    ),
    "Time Fluid is a multi-purpose fluid powering all time altering Items and Blocks. It doesn't seem to be entirely part of this timesteam, as it is nearly transparent.$(br2)It is created by dropping a $(l:justdirethings:res_time_crystal)Time Crystal$(/l) into a pool of $(l:justdirethings:res_polymorphic_fluid)Polymorphic Fluid.$(/l)": (
        "시간 유체는 시간을 조작하는 모든 아이템과 블록에 에너지를 공급하는 다목적 유체입니다. "
        "거의 투명한 것을 보면 이 시간 흐름에 완전히 속하지 않는 듯합니다.$(br2)"
        "$(l:justdirethings:res_time_crystal)시간 수정$(/l)을 "
        "$(l:justdirethings:res_polymorphic_fluid)다형성 유체$(/l)에 떨어뜨리면 만들어집니다."
    ),
    "The Celestigem Bow surpasses $(l:justdirethings:tool_blazegold_bow)Blazegold Bow$(/l), utilizing Forge Energy instead of durability. It can hold up to 10,000 FE, ideal for long use without wear.$(br2)This bow features 3 'Potion Canister slots', allowing for customized effects. Load it with a $(l:justdirethings:item_potion_canister)Potion Canisters$(/l) for enhanced arrows.": (
        "셀레스티젬 활은 $(l:justdirethings:tool_blazegold_bow)블레이즈골드 활$(/l)의 상위 "
        "티어로, 내구도 대신 최대 10,000 FE의 Forge Energy를 사용합니다.$(br2)물약 캔 슬롯 "
        "세 개가 있어 효과를 조합할 수 있습니다. "
        "$(l:justdirethings:item_potion_canister)물약 캔$(/l)을 넣어 화살에 효과를 부여하세요."
    ),
    "Upgraded from $(l:justdirethings:tool_blazegold_hoe)Blazegold Hoe$(/l), Celestigem tools have Forge Energy instead of durability. This hoe creates Voidshimmer soil.$(br2)If the hoe has 'teleport drops' ability, and is bound to an inventory, the soil will teleport the autoharvested blocks to that inventory.": (
        "$(l:justdirethings:tool_blazegold_hoe)블레이즈골드 괭이$(/l)의 상위 티어이며 내구도 "
        "대신 Forge Energy를 사용합니다. 이 괭이로 경작하면 보이드시머 토양이 됩니다."
        "$(br2)괭이에 전리품 순간이동 능력이 있고 인벤토리에 연결되어 있으면 자동 수확한 "
        "아이템이 해당 인벤토리로 이동합니다."
    ),
    "The Eclipse Alloy Pickaxe combines immense durability with powerful energy storage, making it perfect for harvesting even the toughest materials. $(br2)It is capable of supporting high-level mining enhancements.": (
        "이클립스 합금 곡괭이는 뛰어난 내구도와 큰 에너지 저장량을 갖춰 매우 단단한 재료도 "
        "효율적으로 채굴합니다.$(br2)높은 티어의 채굴 업그레이드를 지원합니다."
    ),
    "The Eclipse Alloy Sword is the pinnacle of combat technology in Just Dire Things, featuring a large energy capacity capable of supporting the most advanced upgrades. $(br2)Forged from Eclipse Alloy, this end-tier tool offers exceptional damage and durability, and is ideal for the most lethal offensive abilities.": (
        "이클립스 합금 검은 Just Dire Things 전투 도구의 최종 티어이며, 가장 강력한 "
        "업그레이드를 지원할 만큼 에너지 용량이 큽니다.$(br2)이클립스 합금으로 만든 이 도구는 "
        "공격력과 내구도가 뛰어나 강력한 공격 능력에 적합합니다."
    ),
    "The Ferricore Bow, crafted from robust Ferricore, enhances standard bow functionalities with increased durability and the ability to be upgraded with various abilities.$(br2)This bow includes a special Potion Canister slot in the tool settings UI, allowing you to enhance arrows with various potion effects. Insert a $(l:justdirethings:item_potion_canister)Potion Canister$(/l) to apply effects.": (
        "페리코어 활은 일반 활보다 내구도가 높고 여러 능력을 업그레이드할 수 있습니다."
        "$(br2)도구 설정 화면에 물약 캔 슬롯이 있어 화살에 다양한 물약 효과를 부여합니다. "
        "$(l:justdirethings:item_potion_canister)물약 캔$(/l)을 넣어 효과를 적용하세요."
    ),
    "Boost your survival chances with the Cauterize Wounds upgrade. This upgrade gives you the ability to heal rapidly after taking damage, using the heat of battle to seal wounds.$(br2)Activate this ability by right clicking - it will instantly heal you, and use some durability. Note there is a cooldown period before you can use it again.": (
        "상처 지혈 업그레이드는 피해를 입은 뒤 전투의 열기로 상처를 막아 빠르게 회복합니다."
        "$(br2)우클릭으로 발동하면 즉시 회복하고 내구도를 조금 소비합니다. 다시 사용하려면 "
        "재사용 대기 시간이 필요합니다."
    ),
    "Instantly smelt items with the Smelter upgrade. Applied to tools, this upgrade allows you to directly obtain smelted products from mined ores.$(br2)Uses some durability.": (
        "제련 업그레이드를 도구에 적용하면 채굴한 광석에서 제련된 결과물을 바로 얻습니다."
        "$(br2)사용할 때 내구도를 조금 소비합니다."
    ),
    "The Blazejet Wand is a great way to get around! It comes with the air burst ability built in.$(br2)Activate this ability using right click (or customize it in the tool settings screen) to blast you in the direction you're facing.": (
        "블레이즈젯 지팡이는 이동에 유용하며 공기 폭발 능력이 내장되어 있습니다.$(br2)"
        "우클릭으로 능력을 발동하면 바라보는 방향으로 날아갑니다. 발동 방식은 도구 설정 "
        "화면에서 바꿀 수 있습니다."
    ),
    "Higher tiers of this wand allow you to go even further, which you can configure with a slider in the tool settings screen.$(br2)While holding this in your hand, you won't take any fall damage. But ensure its in your hand!$(br2)This tool comes with the lava repair ability, so drop it in a lava source block to repair it.": (
        "지팡이 티어가 높을수록 더 멀리 날아가며 도구 설정 화면의 슬라이더로 거리를 조정할 "
        "수 있습니다.$(br2)이 지팡이를 손에 들고 있는 동안에는 낙하 피해를 받지 않습니다. "
        "반드시 손에 들고 있어야 합니다!$(br2)용암 수리 능력이 있으므로 용암 원천 블록에 "
        "떨어뜨리면 수리됩니다."
    ),
    "The Creature Catcher is an innovative tool for capturing and releasing entities. Simply throw it at an entity to capture it, and toss it again to release the captured entity.$(br2)You can also use it in some filters to filter very specific types of entities, such as only filtering blue sheep.": (
        "생물 포획기는 엔티티를 붙잡아 운반하는 도구입니다. 엔티티에게 던지면 포획되고 다시 "
        "던지면 풀어줍니다.$(br2)일부 필터에서는 파란색 양처럼 특정 조건의 엔티티를 정확히 "
        "지정하는 데도 사용할 수 있습니다."
    ),
    "The Eclipsegate Wand represents the pinnacle of magical tool development, featuring unparalleled powers.$(br2)In addition to the $(l:justdirethings:item_voidshift_wand)Voidshift Wand$(/l) abilities, you can activate the Eclipse Gate ability. Simply right click on a block, and all blocks around and behind it disappear temporarily!": (
        "이클립스 게이트 지팡이는 마법 도구의 최종 티어입니다.$(br2)"
        "$(l:justdirethings:item_voidshift_wand)보이드 시프트 지팡이$(/l)의 능력에 이클립스 "
        "게이트가 추가됩니다. 블록을 우클릭하면 그 주변과 뒤쪽 블록이 잠시 사라집니다!"
    ),
    "After a few moments the original blocks will return as they were. Block Entities like chests are not affected.$(br2)The setting screen lets you adjust the range of this ability. ": (
        "잠시 뒤 블록은 원래 상태로 돌아옵니다. 상자 같은 블록 엔티티에는 영향을 주지 "
        "않습니다.$(br2)설정 화면에서 능력의 범위를 조정할 수 있습니다."
    ),
    "The Fluid Canister can hold up to 8 buckets of liquid. Right-click to place or pick up liquids, similar to a bucket.$(br2)Shift right-click to enable auto-filling of other fluid containers in your inventory. There are three settings: 'None', Just Dire Things items only, and 'ALL' (fills all fluid holders, including from other mods).": (
        "유체 캔에는 최대 8양동이 분량의 유체를 담을 수 있습니다. 양동이처럼 우클릭해 유체를 "
        "놓거나 담습니다.$(br2)Shift + 우클릭하면 인벤토리의 다른 유체 용기를 자동으로 "
        "채웁니다. 채움 모드는 '없음', 'Just Dire Things만', 다른 모드까지 포함하는 '모두'의 "
        "세 가지입니다."
    ),
    "The Fuel Canister is essential for storing and transporting large quantities of fuel.$(br2)Right click the item to open the UI. Insert fuel by shift clicking (or picking up the fuel and clicking it into the UI). Any fuel will work, such as coal, wood, etc, but not lava buckets.": (
        "연료 캔은 많은 연료를 저장하고 운반합니다.$(br2)아이템을 우클릭해 화면을 연 뒤 "
        "Shift + 클릭하거나 연료를 집어 슬롯에 놓으세요. 석탄과 목재 같은 연료는 사용할 수 "
        "있지만 용암 양동이는 사용할 수 없습니다."
    ),
    "The tooltip will tell you how much fuel you've stored. The fuel canister can then be placed into machines such as furnaces and generators, and it will consume fuel from the canister. This is a good way to ensure you don't waste a full piece of coal to smelt 1 ore!$(br2)Note: theres no way to get the items back out!": (
        "저장된 연료량은 툴팁에 표시됩니다. 연료 캔을 화로와 발전기 같은 기계에 넣으면 "
        "캔에 저장된 연료를 사용합니다. 광석 한 개를 제련하면서 석탄 한 개를 통째로 낭비하지 "
        "않아도 됩니다!$(br2)참고: 넣은 연료 아이템은 다시 꺼낼 수 없습니다!"
    ),
    "Inserting the fuel from this mod will also transfer its fuel multipler attribute, and will average it with the existing fuel in the canister. The tooltip on the canister will tell you the multiplier you'll get, if you use the canister in a $(l:justdirethings:item_pocket_generator)Pocket Generator$(/l) or $(l:justdirethings:mach_generatort1)Generator$(/l).": (
        "이 모드의 연료를 넣으면 연료 배수 속성도 전달되며 캔 안의 기존 연료와 평균을 냅니다. "
        "$(l:justdirethings:item_pocket_generator)휴대용 발전기$(/l)나 "
        "$(l:justdirethings:mach_generatort1)석탄 발전기$(/l)에서 사용할 때 적용되는 배수는 "
        "연료 캔의 툴팁에서 확인할 수 있습니다."
    ),
    "This tool allows for the copying of machine settings. Shift-right click on a $(l:justdirethings:machines)Machine$(/l) to copy its settings, then right click on another machine to paste them. Click in the air to open a menu and select specific settings to copy.": (
        "기계 설정 복사기는 기계 사이에서 설정을 복사합니다. "
        "$(l:justdirethings:machines)기계$(/l)를 Shift + 우클릭해 설정을 복사한 뒤 다른 기계를 "
        "우클릭해 붙여넣으세요. 공중을 클릭하면 복사할 설정을 고르는 화면이 열립니다."
    ),
    "The Pocket Generator is a portable energy source, perfect for keeping energy-dependent tools and armor charged while on the go. Essential for adventurers relying on Forge Energy.$(br2)Open the UI by clicking it, and insert fuel in the form of coal or upgraded coals from this mod!": (
        "휴대용 발전기는 이동 중에 도구와 방어구의 Forge Energy를 충전하는 휴대용 전원입니다."
        "$(br2)아이템을 클릭해 화면을 열고 석탄이나 이 모드의 특수 석탄을 연료로 넣으세요!"
    ),
    "Higher tier fuels burn hotter and longer, so you'll get more forge energy / tick if you use higher tier fuels.  You can also use the $(l:justdirethings:item_fuel_canister)Fuel Canister$(/l).": (
        "높은 티어의 연료는 더 뜨겁고 오래 타므로 틱당 더 많은 Forge Energy를 생산합니다. "
        "$(l:justdirethings:item_fuel_canister)연료 캔$(/l)도 사용할 수 있습니다."
    ),
    "The polymorphic wand uses the latent energy available in Blazegold to activate the Polymorphic Fluid, randomly changing mobs from one form to another!$(br2)Simply activate the wand on a hostile entity, and it'll convert randomly into another hostile entity. The same can happen with peaceful entities.": (
        "다형성 지팡이는 블레이즈골드의 잠재 에너지로 다형성 유체를 활성화해 몹을 무작위로 "
        "다른 종류로 바꿉니다!$(br2)적대적 몹에게 사용하면 다른 적대적 몹으로, 비적대적 "
        "몹에게 사용하면 다른 비적대적 몹으로 바뀝니다."
    ),
    "With this simple form of the wand, it is not possible to guarantee which mob you will get, nor is is possible to swap hostile and friendly mobs with each other. You suspect the wand can be upgraded to allow for these features, however!": (
        "이 기본 지팡이로는 결과로 나올 몹을 지정할 수 없고 적대적 몹과 비적대적 몹을 서로 "
        "바꿀 수도 없습니다. 하지만 지팡이를 업그레이드하면 가능할지도 모릅니다!"
    ),
    "The advanced polymorphic wand is an upgrade to the Polymorphic Wand. The existing 'random polymorph' ability still exists, but a new ability, 'targetted polymorph' is now available!": (
        "고급 다형성 지팡이는 다형성 지팡이의 상위 버전입니다. 기존 '무작위 변이' 능력과 "
        "새로운 '대상 지정 변이' 능력을 모두 사용할 수 있습니다!"
    ),
    "Simply shift-right click on any mob to save that type of mob to the wand, then activate the targeted polymorph ability to convert any mob to that type automatically!$(br2)Some mobs cannot be saved to the wand (You can edit these with Tags).$(br2)It is recommended to set the two abilities to different clicks or hotkeys.": (
        "몹을 Shift + 우클릭해 그 종류를 지팡이에 저장한 뒤 대상 지정 변이를 발동하면 다른 "
        "몹을 저장한 종류로 바꿉니다!$(br2)일부 몹은 저장할 수 없으며 태그에서 이 목록을 "
        "수정할 수 있습니다.$(br2)두 변이 능력은 서로 다른 마우스 버튼이나 단축키에 지정하는 "
        "것이 좋습니다."
    ),
    "The Portal Gun is a revolutionary device that enables the creation of portals. Left click to fire a projectile creating a blue portal, and right click for an orange portal. Step through one to emerge from the other, applicable to both players and items.": (
        "포털 건은 포털 두 개를 만드는 장치입니다. 좌클릭하면 파란색 포털, 우클릭하면 주황색 "
        "포털을 만드는 투사체를 발사합니다. 플레이어와 아이템 모두 한쪽 포털로 들어가 다른 "
        "포털로 나올 수 있습니다."
    ),
    "The Advanced Portal Gun enhances the functionality of the standard portal gun by adding a favorites menu. Activate the menu with the default hotkey 'v'.$(br2)In the menu, you can add locations, allowing you to save the position where your player is standing. Fire a projectile that opens a portal to the saved location from anywhere.": (
        "고급 포털 건에는 일반 포털 건의 기능에 즐겨찾기 화면이 추가됩니다. 기본 단축키 'V'로 "
        "화면을 여세요.$(br2)현재 위치를 즐겨찾기에 저장하면 어디서든 그 위치로 연결되는 "
        "포털 투사체를 발사할 수 있습니다."
    ),
    "The Totem of Death Recall provides a second chance after a fatal mistake. Keep it in your inventory, and it will automatically activate on death, binding itself to the position you died at.$(br2)Hold Right-click the activated totem to teleport back to your death point. The totem is consumed upon use.": (
        "죽음 귀환의 토템을 인벤토리에 넣어 두면 사망할 때 자동으로 활성화되어 사망 위치를 "
        "저장합니다.$(br2)활성화된 토템을 들고 우클릭하면 사망 지점으로 순간이동하며 토템은 "
        "소모됩니다."
    ),
    "Advancing from the $(l:justdirethings:item_blazejet_wand)Blazejet Wand$(/l), the Voidshift Wand utilizes dimensional energies for more complex operations.$(br2)The new void shift ability lets you teleport wherever you're looking - up to a certain distance": (
        "$(l:justdirethings:item_blazejet_wand)블레이즈젯 지팡이$(/l)의 다음 티어인 보이드 "
        "시프트 지팡이는 차원 에너지로 더 복잡한 능력을 사용합니다.$(br2)새로운 보이드 "
        "시프트 능력으로 바라보는 방향의 일정 거리까지 순간이동할 수 있습니다."
    ),
    "Access the tool settings screen to customize the hotkey or mouse button needed to activate it. I personally like air burst on right click, and void shift on left click.$(br2)You can also shorten the max distance traveled, and toggle on or off the player rendering.": (
        "도구 설정 화면에서 발동 단축키나 마우스 버튼을 지정하세요. 개인적으로 공기 폭발은 "
        "우클릭, 보이드 시프트는 좌클릭을 추천합니다.$(br2)최대 이동 거리를 줄이거나 플레이어 "
        "표시를 켜고 끌 수도 있습니다."
    ),
    "Each of the tiers of resources have an equivalent set of Armor. These armors each have a set of $(l:justdirethings:upgrades)Upgrades$(/l) available to them.$(br2)Check which upgrades are available for the tools by looking at their tooltip while holding 'shift'.": (
        "각 자원 티어에는 대응하는 방어구 세트가 있으며, 방어구마다 사용할 수 있는 "
        "$(l:justdirethings:upgrades)업그레이드$(/l)가 다릅니다.$(br2)Shift를 누른 채 "
        "툴팁을 보면 적용 가능한 업그레이드를 확인할 수 있습니다."
    ),
    "To install upgrades, craft the appropriate upgrade item, and then place your armor and the upgrade item in a smithing table.$(br2)Use the upgrade templates to upgrade from one tier to the next, and maintain your installed upgrades.": (
        "알맞은 업그레이드 아이템을 제작한 뒤 방어구와 함께 대장장이 작업대에 넣어 설치합니다."
        "$(br2)티어 형판으로 다음 티어로 올리면 기존에 설치한 업그레이드가 유지됩니다."
    ),
    "Shift-Click any tool when it's in your hand to configure it. You can then click on your armor in this screen to access it's upgrades. From here, you can toggle on or off specific upgrades by clicking on them.$(br2)Right click the upgrade to change some settings (if they have any) or assign a hotkey. If the ability is passive, the hotkey will toggle its activation. If the ability is active, the hotkey will trigger it.": (
        "도구를 손에 든 채 Shift + 클릭하면 설정 화면이 열립니다. 이 화면에서 방어구를 "
        "클릭해 업그레이드를 확인하고 각 능력을 켜거나 끌 수 있습니다.$(br2)업그레이드를 "
        "우클릭하면 세부 설정을 바꾸거나 단축키를 지정할 수 있습니다. 패시브 능력은 단축키로 "
        "켜고 끄며, 액티브 능력은 단축키를 누를 때 발동합니다."
    ),
    "Active abilities, such as invulnerability, must be assigned to a hotkey. See the $(l:justdirethings:upgrade_basics)Upgrade Basics$(/l) entry for more details on this system.$(br2)Armor can be upgraded in the smithing table (check JEI for the recipe) and will maintain installed upgrades when crafted in this way.": (
        "무적 같은 액티브 능력은 단축키를 지정해야 합니다. 자세한 사용법은 "
        "$(l:justdirethings:upgrade_basics)업그레이드 기본$(/l) 항목을 확인하세요.$(br2)"
        "방어구는 대장장이 작업대에서 다음 티어로 올릴 수 있으며, 제작법은 JEI에서 확인할 수 "
        "있습니다. 이 방식으로 올리면 설치한 업그레이드가 유지됩니다."
    ),
    "Each of the tiers of resources have an equivalent set of tools. These tools each have a set of $(l:justdirethings:upgrades)Upgrades$(/l) available to them.$(br2)Check which upgrades are available for the tools by looking at their tooltip while holding 'shift'.": (
        "각 자원 티어에는 대응하는 도구 세트가 있으며, 도구마다 사용할 수 있는 "
        "$(l:justdirethings:upgrades)업그레이드$(/l)가 다릅니다.$(br2)Shift를 누른 채 "
        "툴팁을 보면 적용 가능한 업그레이드를 확인할 수 있습니다."
    ),
    "To install upgrades, craft the appropriate upgrade item, and then place your tool and the upgrade item in a smithing table.$(br2)Use the upgrade templates to upgrade from one tier to the next, and maintain your installed upgrades.$(br2)Activate or Deactivate the tool with the assigned hotkey ('v' by default). When the tool is deactivated, ALL abilities are turned off.": (
        "알맞은 업그레이드 아이템을 제작한 뒤 도구와 함께 대장장이 작업대에 넣어 설치합니다."
        "$(br2)티어 형판으로 다음 티어로 올리면 기존에 설치한 업그레이드가 유지됩니다."
        "$(br2)지정된 단축키(기본값 'V')로 도구를 활성화하거나 비활성화합니다. 도구가 "
        "비활성화되면 모든 능력이 꺼집니다."
    ),
    "Shift-Click the tool when it's in your hand to configure it (there is also a hotkey for this screen). From here, you can toggle on or off specific upgrades by clicking on them.$(br2)Right click the upgrade to change some settings (if they have any) or assign a hotkey. If the ability is passive, the hotkey will toggle its activation. If the ability is active, the hotkey will trigger it.": (
        "도구를 손에 든 채 Shift + 클릭하면 설정 화면이 열립니다. 이 화면에는 별도 단축키도 "
        "있습니다. 업그레이드를 클릭해 각 능력을 켜거나 끌 수 있습니다.$(br2)업그레이드를 "
        "우클릭하면 세부 설정을 바꾸거나 단축키를 지정할 수 있습니다. 패시브 능력은 단축키로 "
        "켜고 끄며, 액티브 능력은 단축키를 누를 때 발동합니다."
    ),
    "Active abilities, such as the mob scanner, can be configured to happen either on right click, left click, or with a designated hotkey. See the $(l:justdirethings:upgrade_basics)Upgrade Basics$(/l) entry for more details on this system.$(br2)Tools can be upgraded in the smithing table (check JEI for the recipe) and will maintain installed upgrades when crafted in this way.": (
        "몹 스캐너 같은 액티브 능력은 우클릭, 좌클릭 또는 지정한 단축키로 발동하게 설정할 수 "
        "있습니다. 자세한 사용법은 $(l:justdirethings:upgrade_basics)업그레이드 기본$(/l) "
        "항목을 확인하세요.$(br2)도구는 대장장이 작업대에서 다음 티어로 올릴 수 있으며, "
        "제작법은 JEI에서 확인할 수 있습니다. 이 방식으로 올리면 설치한 업그레이드가 유지됩니다."
    ),
    "Upgrades are installed in $(l:justdirethings:tools)Tools$(/l) or $(l:justdirethings:armor)Armor$(/l) to grant them certain abilities. They can be installed using the Smithing Table, you should be able to look the recipe up with JEI.$(br2)There are several kinds of abilities.": (
        "업그레이드는 $(l:justdirethings:tools)도구$(/l)나 $(l:justdirethings:armor)방어구$(/l)에 "
        "특정 능력을 부여합니다. 대장장이 작업대에서 설치하며 제작법은 JEI에서 확인할 수 "
        "있습니다.$(br2)능력에는 여러 종류가 있습니다."
    ),
    "$(l)Use Abilities$() are used to activate. For example, Mob Scanner is a use ability that when activated will show the position of all nearby mobs.$(br2)$(l)Passive Abilities$() affect how your tool operates. For example, the hammer ability allows your tool to break in a 3x3, 5x5, or 7x7 area whenever you mine a block.": (
        "$(l)액티브 능력$()은 플레이어가 직접 발동합니다. 예를 들어 몹 스캐너를 발동하면 "
        "주변 몹의 위치가 표시됩니다.$(br2)$(l)패시브 능력$()은 도구의 작동 방식을 바꿉니다. "
        "예를 들어 망치 능력은 블록을 채굴할 때 3x3, 5x5 또는 7x7 영역을 함께 파괴합니다."
    ),
    "Some abilities have $(l)cooldowns$(), like the invulnerability ability will make you invulnerable for a few seconds, but can't be used again for a few minutes. Both $(l)passive$() and $(l)active$() abilities can have cooldowns, but not all of them do. See the individual upgrade sections for more details.": (
        "일부 능력에는 $(l)재사용 대기 시간$()이 있습니다. 무적 능력은 몇 초 동안 피해를 "
        "막아 주지만 다시 사용하려면 몇 분 기다려야 합니다. $(l)패시브$()와 $(l)액티브$() "
        "능력 모두 재사용 대기 시간이 생길 수 있지만 모든 능력에 있는 것은 아닙니다. 자세한 "
        "내용은 각 업그레이드 항목을 확인하세요."
    ),
    "Abilities can be controlled using the $(l)Tool Settings Screen$() which can be activated by shift-right clicking any tool.$(br2)Once in this screen, you can access the settings for other tools by clicking on them from the UI.  For example, shift-right click a Ferricore Sword to open the UI, and then click on your Ferricore Helmet to access it's settings.": (
        "능력은 $(l)도구 설정 화면$()에서 관리합니다. 도구를 Shift + 우클릭해 화면을 "
        "여세요.$(br2)화면이 열린 뒤 다른 도구나 방어구를 클릭하면 그 아이템의 설정으로 "
        "이동합니다. 예를 들어 페리코어 검으로 화면을 연 뒤 페리코어 투구를 클릭해 해당 "
        "투구의 설정을 확인할 수 있습니다."
    ),
    "When looking at an item, you'll see an icon representing each of its abilities. You can left click this icon to toggle the ability on or off.$(br2)When off, the abilities won't activate by their hotkey if they are active, and won't cause their effects if passive.$(br2)For example, if you toggle off the hammer ability, your pickaxe will only mine 1 block.": (
        "아이템 화면에는 각 능력을 나타내는 아이콘이 표시됩니다. 아이콘을 좌클릭하면 능력을 "
        "켜거나 끌 수 있습니다.$(br2)꺼진 액티브 능력은 단축키를 눌러도 발동하지 않으며, "
        "꺼진 패시브 능력은 효과가 적용되지 않습니다.$(br2)예를 들어 망치 능력을 끄면 "
        "곡괭이는 블록 한 개만 채굴합니다."
    ),
    "Right click the ability to access it's options screen. For $(l)active$() abilities, you can specify which hotkey (or mouse click) activates them.$(br2)For passive abilities, the hotkey assignment will toggle it on or off when that hotkey is pressed.$(br2)Abilities can be activated or toggled even if the item isn't equipped! But first, toggle the 'activate if equipped' button to 'activate from inventory'": (
        "능력을 우클릭하면 옵션 화면이 열립니다. $(l)액티브$() 능력에는 발동할 단축키나 "
        "마우스 버튼을 지정할 수 있습니다.$(br2)패시브 능력에 단축키를 지정하면 그 키로 "
        "능력을 켜거나 끕니다.$(br2)아이템을 장착하지 않아도 능력을 사용할 수 있습니다! "
        "먼저 '장착 중일 때 활성화'를 '인벤토리에서 활성화'로 바꾸세요."
    ),
    "This means that you can activate the 'air burst' ability, or 'ore scanner' ability, even if the wand or pickaxe isn't in your hand.  As long as its *somewhere* in your inventory, you can use these abilities.$(br2)Curios support is planned for some items.": (
        "지팡이나 곡괭이를 손에 들지 않아도 '공기 폭발'이나 '광석 스캐너' 능력을 사용할 수 "
        "있다는 뜻입니다. 아이템이 인벤토리 *어딘가*에 있기만 하면 됩니다.$(br2)일부 "
        "아이템에는 추후 Curios 지원이 추가될 예정입니다."
    ),
    "Some abilities have custom settings as well. For example, the run speed or jump height abilities have sliders (available after Tier 2 armor), that control how much faster you run, or how much higher you jump.$(br2)Some abilities improve based on the tier of tool they are installed in. For example, the Hammer ability is 3x3 in a $(l:justdirethings:tool_blazegold_pickaxe)Blazegold Pickaxe$(/l), and 7x7 in $(l:justdirethings:tool_eclipse_alloy_pickaxe)Eclipse Alloy Pickaxe$(/l).": (
        "일부 능력에는 별도 설정이 있습니다. 달리기 속도와 점프 강화 능력은 2티어 이상의 "
        "방어구에서 슬라이더로 강도를 조정할 수 있습니다.$(br2)설치한 도구의 티어에 따라 "
        "강해지는 능력도 있습니다. 망치 능력은 "
        "$(l:justdirethings:tool_blazegold_pickaxe)블레이즈골드 곡괭이$(/l)에서 3x3, "
        "$(l:justdirethings:tool_eclipse_alloy_pickaxe)이클립스 합금 곡괭이$(/l)에서 7x7 "
        "영역을 채굴합니다."
    ),
    "Time Crystals are no trivial task to create, but they are very worth while as they have the power to affect time itself!  Creating them is a multi step process that will be outlined in the following pages.$(br2)First, use $(l:justdirethings:goo_tier4)Shadowpulse Goo$(/l) to convert a budding Amethyst block into a Budding Time Crystal block.": (
        "시간 수정은 만들기 어렵지만 시간 자체에 영향을 주므로 충분한 가치가 있습니다. 제작에는 "
        "여러 단계가 필요하며 다음 페이지에서 차례로 설명합니다.$(br2)먼저 "
        "$(l:justdirethings:goo_tier4)섀도우펄스 구$(/l)로 싹트는 자수정 블록을 싹트는 "
        "시간 수정 블록으로 바꾸세요."
    ),
    "The Budding Time Crystal block must absorb time energy from each of Minecraft's 3 dimensions: The Overworld, The Nether, and The End.$(br2)Place the Budding Time Crystal block in The Overworld for some time. It will begin absorbing Overworld Time Energy, which you'll be able to see as blue particle effects. Once the block changes color, its ready for the next step.": (
        "싹트는 시간 수정 블록은 Minecraft의 세 차원인 오버월드, 네더, 엔드에서 시간 에너지를 "
        "차례로 흡수해야 합니다.$(br2)먼저 오버월드에 한동안 놓아두세요. 오버월드 시간 "
        "에너지를 흡수하면 파란색 입자가 나타나며, 블록의 색이 바뀌면 다음 단계로 넘어갈 "
        "준비가 된 것입니다."
    ),
    "You'll need to move the block into The Nether at this point, however you cannot break the block without shattering it - Even with Silk touch! You'll need to find $(l:justdirethings:mach_blockswappert1)Some Other Way$(/l) to move it across dimensions.  Once in the nether, it will absorb Nether Time Energy, which will appear as orange particle effects. Once the block changes color, its ready to move again.": (
        "이제 블록을 네더로 옮겨야 하지만 섬세한 손길을 사용해도 채굴하면 산산이 부서집니다! "
        "차원을 건너 옮길 $(l:justdirethings:mach_blockswappert1)다른 방법$(/l)을 찾아야 합니다. "
        "네더에서는 네더 시간 에너지를 흡수하며 주황색 입자가 나타납니다. 블록의 색이 "
        "바뀌면 다시 옮길 준비가 된 것입니다."
    ),
    "Finally, move the block into The End. Here, it will absord End Time Energy, visualized as Green particle effects. Once complete, the block will turn green, and Time Crystal Buds will begin to appear.$(br2)Each time a time crystal bud sprouts, it consumes some of the time energy. Ensure you don't break the time crystal buds until they've fully grown, or you will destroy them, receiving nothing in return!": (
        "마지막으로 블록을 엔드로 옮기세요. 엔드 시간 에너지를 흡수하면 초록색 입자가 나타납니다. "
        "흡수가 끝나 블록이 초록색으로 변하면 시간 수정 새싹이 생기기 시작합니다.$(br2)새싹이 "
        "날 때마다 시간 에너지를 조금씩 소비합니다. 완전히 자라기 전에 부수면 아무것도 얻지 "
        "못하므로 기다리세요!"
    ),
    "Eventually, all of the time energy in the budding time crystal will be consumed.  At this point, you'll need to move it back to the Overworld and begin the charging process from the start.$(br)Note: While out of charge, the buds will not grow any longer. In addition, if you move JUST the Budding Time Crystal, the buds themselves will shatter. Its recommended to move the Crystal and its buds $(l:justdirethings:mach_blockswappert2)All Together$(/l).": (
        "결국 싹트는 시간 수정의 시간 에너지가 모두 소모됩니다. 이때 오버월드로 다시 옮겨 "
        "처음부터 충전해야 합니다.$(br)참고: 충전되지 않은 동안에는 새싹이 자라지 않습니다. "
        "싹트는 시간 수정 블록만 옮기면 새싹이 부서지므로 블록과 새싹을 "
        "$(l:justdirethings:mach_blockswappert2)모두 함께$(/l) 옮기는 것이 좋습니다."
    ),
    "Some people have reported unusual time distortions while carrying these around.  You should be cautious.": (
        "이것을 들고 다닐 때 이상한 시간 왜곡을 겪었다는 보고가 있습니다. 조심하세요."
    ),
    "Simply right click on any block that ticks - this includes machines like Furnaces, and crops like Wheat. At first, it will cause the block to run twice as fast. Click again to double it to 4x, then 8x, all the way up to #time_wand.time_wand_max_multiplier#x speed!$(br2)Each acceleration will consume both Forge Energy and Time Fluid based on how fast the speed increase is.$(br2)This speed increase will last for 30 seconds.": (
        "용광로 같은 기계나 밀 같은 작물처럼 틱마다 작동하는 블록을 우클릭하세요. 처음에는 "
        "두 배, 다시 클릭하면 4x와 8x처럼 배수가 두 배씩 올라가 최대 "
        "#time_wand.time_wand_max_multiplier#x가 됩니다!$(br2)가속 배수가 높을수록 더 많은 "
        "Forge Energy와 시간 유체를 소비합니다.$(br2)가속 효과는 30초 동안 지속됩니다."
    ),
    "Goo is a transformative substance that can alter certain blocks placed adjacent to it. Each tier of goo has the capacity to consume and convert stronger blocks into new, advanced resources.$(br2)This system allows for the progressive unlocking of materials and crafting capabilities.": (
        "구는 옆에 놓인 특정 블록을 다른 물질로 바꾸는 변환 물질입니다. 티어가 높을수록 더 "
        "단단한 블록을 소비해 새로운 고급 자원으로 바꿀 수 있습니다.$(br2)이 과정을 따라 "
        "새로운 재료와 제작법을 차례로 해금합니다."
    ),
    "To utilize goo:$(br2)1. Craft a goo block and position it in your world.$(br2)2. Activate the goo by feeding it a specific resource it can consume (indicated by the goo block).$(br2)3. Place an eligible block next to the activated goo to start the transformation process.": (
        "구 사용법:$(br2)1. 구 블록을 만들어 월드에 놓습니다.$(br2)2. 구 블록에 표시된 "
        "소모 자원을 먹여 구를 활성화합니다.$(br2)3. 활성화된 구 옆에 변환 가능한 블록을 "
        "놓아 변환을 시작합니다."
    ),
    "Note: After transforming a block, there's a 10% chance the goo will need reactivation by feeding it another item. While inactive, the goo cannot initiate new transformations, but any ongoing processes will continue to completion.$(br2)Higher tier goo can always craft everything a lower tier can, and are much faster.": (
        "참고: 블록을 변환한 뒤 10% 확률로 구가 비활성화되며, 다시 아이템을 먹여 활성화해야 "
        "합니다. 비활성 상태에서는 새 변환을 시작할 수 없지만 이미 진행 중인 변환은 끝까지 "
        "완료됩니다.$(br2)높은 티어의 구는 낮은 티어의 모든 변환을 수행할 수 있고 속도도 훨씬 "
        "빠릅니다."
    ),
    "Primogel Goo, the foundational tier of goo, can transform basic resources like Iron into Ferricore. It is perfect for initial experiments in material transformation and enhancing common materials into something more useful and efficient.$(br2)Crafted from simple Overworld materials, Primogel Goo is the first step in exploring the alchemical potential of goo.": (
        "첫 번째 티어인 프라이모젤 구는 철 같은 기본 자원을 페리코어로 바꿉니다. 흔한 재료를 "
        "더 유용하고 효율적인 물질로 바꾸는 첫 변환 단계입니다.$(br2)간단한 오버월드 재료로 "
        "제작하며, 구의 연금술적 가능성을 탐구하는 출발점입니다."
    ),
    "Blazebloom Goo captures the fiery essence of the Nether. It can transform Gold into Blazegold, a material infused with solar energies that enhances both crafting and magical applications.$(br2)Ideal for intermediate alchemists, Blazebloom Goo represents a step up in the ability to manipulate and refine resources.": (
        "블레이즈블룸 구에는 네더의 불타는 기운이 담겨 있습니다. 금을 태양 에너지가 깃든 "
        "블레이즈골드로 바꾸며, 제작과 마법 양쪽에서 더 좋은 재료를 제공합니다.$(br2)자원을 "
        "조작하고 정제하는 능력이 한 단계 높아진 중간 티어의 구입니다."
    ),
    "VoidShimmer Goo, imbued with the mysterious energies of the End, allows for the transformation of Diamonds into Celestigem. This goo tier enables the creation of materials with extraordinary properties, such as enhanced energy storage, and teleportation.": (
        "보이드시머 구에는 엔드의 신비한 에너지가 깃들어 있으며 다이아몬드를 셀레스티젬으로 "
        "바꿉니다. 향상된 에너지 저장과 순간이동처럼 특별한 성질을 지닌 재료를 만들 수 있습니다."
    ),
    "At the pinnacle of goo research lies Shadowpulse Goo, capable of transforming Netherite into Eclipse Alloy. This top-tier goo enables the creation of supremely powerful items.$(br2)Shadowpulse Goo is crafted from the rarest and most powerful of materials, offering unmatched capabilities in material transformation.": (
        "구 연구의 정점인 섀도우펄스 구는 네더라이트를 이클립스 합금으로 바꿉니다. 이 최상위 "
        "구를 이용하면 매우 강력한 아이템을 만들 수 있습니다.$(br2)가장 희귀하고 강력한 "
        "재료로 제작하며 다른 구와 비교할 수 없는 변환 능력을 제공합니다."
    ),
    "Blazegold Ingots are derived from smelting Raw Blazegold, harvested from $(l:justdirethings:res_blazegold_raw)Raw Blazegold Blocks$(/l). These ingots are essential for crafting items imbued with magical properties.": (
        "블레이즈골드 주괴는 $(l:justdirethings:res_blazegold_raw)미가공 블레이즈골드 광석$(/l)에서 "
        "얻은 블레이즈골드 원석을 제련해 만듭니다. 마법적 성질을 지닌 아이템의 핵심 재료입니다."
    ),
    "A Gold Block transformed by Blazebloom Goo becomes a Raw Blazegold Block. Mining this block yields Raw Blazegold items, which are smelted into $(l:justdirethings:res_blazegold)Blazegold Ingots$(/l).": (
        "금 블록을 블레이즈블룸 구로 변환하면 미가공 블레이즈골드 광석이 됩니다. 이를 채굴해 "
        "얻은 블레이즈골드 원석을 제련하면 $(l:justdirethings:res_blazegold)블레이즈골드 주괴$(/l)가 "
        "됩니다."
    ),
    "Raw Blazegold drops when you break the Raw Blazegold Block": (
        "미가공 블레이즈골드 광석을 부수면 블레이즈골드 원석이 나옵니다"
    ),
    "Celestigems are obtained by mining $(l:justdirethings:res_celestigem_raw)Raw Celestigem Blocks$(/l). These gems possess unique properties ideal for high-tier mystical applications, including storing energy and facilitating teleportation abilities.": (
        "$(l:justdirethings:res_celestigem_raw)미가공 셀레스티젬 광석$(/l)을 채굴하면 "
        "셀레스티젬을 얻습니다. 에너지를 저장하고 순간이동 능력을 지원하는 등 높은 티어의 "
        "마법적 용도에 적합한 보석입니다."
    ),
    "Eclipse Alloy Ingots, obtained by smelting Raw Eclipse Alloy, offer unmatched durability and strength. They are derived from mining $(l:justdirethings:res_eclipsealloy_raw)Raw Eclipse Alloy Blocks$(/l), providing the ultimate material for crafting the most powerful and durable items.": (
        "이클립스 합금 원석을 제련하면 뛰어난 내구도와 강도를 지닌 이클립스 합금 주괴가 "
        "됩니다. 원석은 $(l:justdirethings:res_eclipsealloy_raw)미가공 이클립스 합금 광석$(/l)을 "
        "채굴해 얻으며, 강력하고 튼튼한 아이템을 만드는 최상위 재료입니다."
    ),
    "When a Netherite Block is transformed by Shadowpulse Goo, it becomes a Raw Eclipse Alloy Block. Mine this block to obtain Raw Eclipse Alloy items, which can be smelted into $(l:justdirethings:res_eclipsealloy)Eclipse Alloy Ingots$(/l).": (
        "네더라이트 블록을 섀도우펄스 구로 변환하면 미가공 이클립스 합금 광석이 됩니다. 이를 "
        "채굴해 얻은 이클립스 합금 원석을 제련하면 "
        "$(l:justdirethings:res_eclipsealloy)이클립스 합금 주괴$(/l)가 됩니다."
    ),
    "Raw Eclipse Alloy drops when you break the Raw Eclipse Alloy Block": (
        "미가공 이클립스 합금 광석을 부수면 이클립스 합금 원석이 나옵니다"
    ),
    "Ferricore Ingots are obtained by smelting Raw Ferricore, which is mined from $(l:justdirethings:res_ferricore_raw)Raw Ferricore Blocks$(/l). These ingots are enhanced for durability and strength, serving as a superior alternative to ordinary iron.": (
        "페리코어 주괴는 $(l:justdirethings:res_ferricore_raw)미가공 페리코어 광석$(/l)에서 얻은 "
        "페리코어 원석을 제련해 만듭니다. 일반 철보다 내구도와 강도가 뛰어납니다."
    ),
    "When an Iron Block is consumed by Primogel Goo, it transforms into a Raw Ferricore Block. Mine this block to obtain Raw Ferricore items, which can be smelted into $(l:justdirethings:res_ferricore)Ferricore Ingots$(/l).": (
        "철 블록을 프라이모젤 구로 변환하면 미가공 페리코어 광석이 됩니다. 이를 채굴해 얻은 "
        "페리코어 원석을 제련하면 $(l:justdirethings:res_ferricore)페리코어 주괴$(/l)가 됩니다."
    ),
    "Raw Ferricore drops when you break the Raw Ferricore Block": (
        "미가공 페리코어 광석을 부수면 페리코어 원석이 나옵니다"
    ),
    "Blaze Ember is crafted by placing a block of $(l:justdirethings:res_coal_t1)Primal Coal$(/l) next to a $(l:justdirethings:gooblock_tier2)Blazebloom Goo$(/l). It burns hotter and more efficiently than its predecessor, generating even more RF/T.": (
        "블레이즈 엠버는 $(l:justdirethings:res_coal_t1)프라이멀 석탄$(/l) 블록을 "
        "$(l:justdirethings:gooblock_tier2)블레이즈블룸 구$(/l) 옆에 놓으면 만들어집니다. "
        "이전 단계보다 더 뜨겁고 효율적으로 타서 더 많은 RF/t를 생산합니다."
    ),
    "Voidflame Coal is obtained by placing a block of $(l:justdirethings:res_coal_t2)Blaze Ember$(/l) next to a $(l:justdirethings:gooblock_tier3)VoidShimmer Goo$(/l). This coal variant has mystical properties, enhancing its energy output.": (
        "보이드플레임 석탄은 $(l:justdirethings:res_coal_t2)블레이즈 엠버$(/l) 블록을 "
        "$(l:justdirethings:gooblock_tier3)보이드시머 구$(/l) 옆에 놓으면 얻을 수 있습니다. "
        "신비한 성질을 지녀 더 많은 에너지를 생산합니다."
    ),
    "Eclipse Ember is the final evolution of specialized coal, crafted by placing a block of $(l:justdirethings:res_coal_t3)Voidflame Coal$(/l) next to a $(l:justdirethings:gooblock_tier4)Shadowpulse Goo$(/l). It offers the highest energy density among coal types.": (
        "이클립스 엠버는 특수 석탄의 마지막 단계입니다. "
        "$(l:justdirethings:res_coal_t3)보이드플레임 석탄$(/l) 블록을 "
        "$(l:justdirethings:gooblock_tier4)섀도우펄스 구$(/l) 옆에 놓으면 만들어지며, "
        "석탄 계열 중 에너지 밀도가 가장 높습니다."
    ),
    "$(bold)Warning!!$()$(br2)The paradox is an unstable spacetime event brought on by overuse of the $(l:justdirethings:mach_paradox)Paradox Machine$(/l).$(br2)The paradox starts out small, but over time will grow larger. The larger it grows, the more it will be able to consume.": (
        "$(bold)경고!!$()$(br2)패러독스는 $(l:justdirethings:mach_paradox)패러독스 기계$(/l)를 "
        "과도하게 사용하면 생기는 불안정한 시공간 현상입니다.$(br2)처음에는 작지만 시간이 "
        "지날수록 커지며, 크기가 커질수록 더 많은 것을 집어삼킬 수 있습니다."
    ),
    "The Time Wand is a portable way to take advantage of the time altering abilities of $(l:justdirethings:res_time_crystal)Time Crystals$(/l)$(br2)Do note, to use this wand you'll need to charge it with both Forge Energy and $(l:justdirethings:res_time_fluid)Time Fluid$(/l)": (
        "시간 지팡이는 $(l:justdirethings:res_time_crystal)시간 수정$(/l)의 시간 조작 능력을 "
        "휴대용으로 이용하는 도구입니다.$(br2)이 지팡이를 사용하려면 Forge Energy와 "
        "$(l:justdirethings:res_time_fluid)시간 유체$(/l)를 모두 충전해야 합니다."
    ),
    "You can hold multiple favorites, edit their names, and remove them as needed. Additionally, you can toggle the 'Stay Open' option to control whether the menu stays open or requires you to hold the hotkey.$(br2)You must fill the gun with $(l:justdirethings:res_portal_fluid)Portal Fluid$(/l), by right clicking on a source block, or using a $(l:justdirethings:item_fluid_canister)Fluid Canister$(/l).": (
        "즐겨찾기를 여러 개 저장하고 이름을 편집하거나 필요 없는 항목을 삭제할 수 있습니다. "
        "'화면 유지' 옵션을 전환하면 메뉴를 계속 열어 둘지, 단축키를 누르는 동안만 열지 "
        "정할 수 있습니다.$(br2)포털 건에 $(l:justdirethings:res_portal_fluid)포털 유체$(/l)를 "
        "채워야 합니다. 유체 원천 블록을 우클릭하거나 "
        "$(l:justdirethings:item_fluid_canister)유체 캔$(/l)을 사용하세요."
    ),
}

SOURCE_OVERRIDES.update(
    {
        "The Blazegold Helmet offers superior protection compared to its Ferricore predecessor, enhanced with the unique Lava Repair ability. Drop this item into a lava source block to fully repair it.": (
            "블레이즈골드 투구는 이전 티어인 페리코어 투구보다 방어력이 높고 용암 수리 능력이 "
            "있습니다. 용암 원천 블록에 떨어뜨리면 완전히 수리됩니다."
        ),
        "The Potion Canister can be right-clicked to open a UI where you can insert potion bottles. These will fill the canister's internal fluid holder. $(br2) This canister can be slotted into bows, and the potion effects will apply to the arrows you shoot.": (
            "물약 캔을 우클릭하면 물약 병을 넣는 화면이 열립니다. 넣은 물약은 캔 내부에 "
            "저장됩니다.$(br2)물약 캔을 활의 전용 슬롯에 장착하면 발사한 화살에 물약 효과가 "
            "적용됩니다."
        ),
        "Ensure that the bow has the appropriate upgrade(s) installed to take advantage of this canister.$(br2) Ensure that the canister is slotted into the appropriate slot within the bow's tool settings.": (
            "물약 캔을 사용하려면 활에 필요한 업그레이드를 설치해야 합니다.$(br2)활의 도구 "
            "설정 화면에서 물약 캔을 알맞은 슬롯에 넣었는지도 확인하세요."
        ),
        "Stronger than the $(l:justdirethings:tool_ferricore_bow)Ferricore Bow$(/l). Features 'Lava Repair'.$(br2)In addition, it has 2 slots for $(l:justdirethings:item_potion_canister)Potion Canister$(/l)": (
            "$(l:justdirethings:tool_ferricore_bow)페리코어 활$(/l)보다 강하며 용암 수리 능력이 "
            "있습니다.$(br2)$(l:justdirethings:item_potion_canister)물약 캔$(/l) 슬롯도 두 개 "
            "제공합니다."
        ),
        "Enhanced damage over the $(l:justdirethings:tool_ferricore_sword)Ferricore Sword$(/l). Features 'Lava Repair' for full repair when dropped into lava.": (
            "$(l:justdirethings:tool_ferricore_sword)페리코어 검$(/l)보다 공격력이 높습니다. 용암 "
            "수리 능력이 있어 용암에 떨어뜨리면 완전히 수리됩니다."
        ),
        "Advancing from $(l:justdirethings:tool_blazegold_axe)Blazegold Axe$(/l), this axe harnesses Forge Energy, featuring a 10,000 FE storage. Maintain power levels with a $(l:justdirethings:item_pocket_generator)Pocket Generator$(/l).": (
            "$(l:justdirethings:tool_blazegold_axe)블레이즈골드 도끼$(/l)의 상위 티어로, 내구도 "
            "대신 최대 10,000 FE의 Forge Energy를 사용합니다. "
            "$(l:justdirethings:item_pocket_generator)휴대용 발전기$(/l)로 충전하세요."
        ),
        "Building upon $(l:justdirethings:tool_blazegold_shovel)Blazegold Shovel$(/l), this shovel operates on Forge Energy. Equipped with a 10,000 FE capacity, keep it powered using a $(l:justdirethings:item_pocket_generator)Pocket Generator$(/l).": (
            "$(l:justdirethings:tool_blazegold_shovel)블레이즈골드 삽$(/l)의 상위 티어로, 내구도 "
            "대신 최대 10,000 FE의 Forge Energy를 사용합니다. "
            "$(l:justdirethings:item_pocket_generator)휴대용 발전기$(/l)로 충전하세요."
        ),
        "An upgrade to $(l:justdirethings:tool_blazegold_sword)Blazegold Sword$(/l), this sword uses Forge Energy instead of durability. It holds 10,000 FE, best kept charged with a $(l:justdirethings:item_pocket_generator)Pocket Generator$(/l).": (
            "$(l:justdirethings:tool_blazegold_sword)블레이즈골드 검$(/l)의 상위 티어로, 내구도 "
            "대신 최대 10,000 FE의 Forge Energy를 사용합니다. "
            "$(l:justdirethings:item_pocket_generator)휴대용 발전기$(/l)로 충전하세요."
        ),
        "The Eclipse Alloy Bow embodies the ultimate in ranged weaponry, providing vast energy reserves for prolonged use. $(br2)It features 4 slots for Potion Canisters, enhancing arrows with various effects. $(l:justdirethings:item_potion_canister)Potion Canister$(/l)": (
            "이클립스 합금 활은 큰 에너지 용량을 지닌 최종 티어 원거리 무기입니다.$(br2)"
            "$(l:justdirethings:item_potion_canister)물약 캔$(/l) 슬롯 네 개로 화살에 다양한 효과를 "
            "부여할 수 있습니다."
        ),
        "The Eclipse Alloy Paxel represents the pinnacle of tool integration, combining the functionality of a pickaxe, axe, and shovel into a single formidable tool. $(br2)Craft it either by combining an Eclipse Alloy Pickaxe, Axe, and Shovel in a smithing table, or upgrade a $(l:justdirethings:tool_celestigem_paxel)Celestigem Paxel$(/l) using the smithing table. Both methods preserve any installed upgrades.": (
            "이클립스 합금 팍셀은 곡괭이, 도끼, 삽의 기능을 하나로 합친 최종 티어 도구입니다."
            "$(br2)대장장이 작업대에서 이클립스 합금 곡괭이·도끼·삽을 합치거나 "
            "$(l:justdirethings:tool_celestigem_paxel)셀레스티젬 팍셀$(/l)을 업그레이드해 "
            "제작합니다. 두 방법 모두 설치된 업그레이드를 유지합니다."
        ),
        "Eclipse Alloy Shovel is unmatched in moving large amounts of material efficiently with its enhanced energy capacity. $(br2)Ideal for handling the toughest digging challenges.": (
            "이클립스 합금 삽은 큰 에너지 용량으로 많은 블록을 효율적으로 파낼 수 있습니다."
            "$(br2)매우 까다로운 굴착 작업에 적합합니다."
        ),
        "This Ferricore Hoe provides an excellent tool for preparing and maintaining farmland. It is eligible for various upgrades.$(br2)When used to till dirt, the Ferricore Hoe converts it into Primogel Soil. Primogel Soil offers the benefit of being trample-proof, ensuring that your crops remain undisturbed. Crops also grow just a little bit faster": (
            "페리코어 괭이는 농지를 만들고 관리하는 도구이며 여러 업그레이드를 적용할 수 "
            "있습니다.$(br2)흙을 경작하면 프라이모젤 토양이 됩니다. 이 토양은 밟아도 농지로 "
            "유지되며 작물도 조금 더 빨리 자랍니다."
        ),
        "The Ferricore Sword is a robust melee weapon slightly superior to traditional iron swords. Crafted from Ferricore, it not only provides enhanced damage but also offers the potential for further upgrades with special abilities, enhancing its utility in combat scenarios.": (
            "페리코어 검은 철 검보다 공격력과 내구도가 조금 높은 근접 무기입니다. 여러 특수 "
            "능력을 업그레이드해 전투 성능을 더 높일 수 있습니다."
        ),
        "Gain the power of unrestricted flight with the Flight upgrade. This upgrade allows you to fly freely in survival mode, much like in creative mode.$(br2)It does use forge energy to keep you aloft, so don't run out!": (
            "비행 업그레이드는 크리에이티브 모드처럼 생존 모드에서도 자유롭게 날 수 있게 "
            "합니다.$(br2)비행 중에는 Forge Energy를 계속 소비하므로 에너지가 떨어지지 않게 "
            "주의하세요!"
        ),
        "Protect yourself from the scorching heat of lava with the Lava Immunity upgrade. This upgrade grants complete immunity to lava damage.$(br2)It does use forge energy to keep you aloft, so don't run out!": (
            "용암 면역 업그레이드는 용암 피해를 완전히 막아 줍니다.$(br2)작동 중에는 Forge "
            "Energy를 소비하므로 에너지가 떨어지지 않게 주의하세요!"
        ),
        "This passive ability will make you harder to detect. Mobs won't be able to detect you as easily, and you can get closer to them before they start to agro on you.$(br2)Higher tiers of armor will make this ability even more effective.": (
            "이 패시브 능력은 몹이 플레이어를 감지하는 거리를 줄입니다. 몹이 공격을 시작하기 "
            "전에 더 가까이 접근할 수 있습니다.$(br2)방어구 티어가 높을수록 효과가 강해집니다."
        ),
        "The Mental Obliteration upgrade disables the artificial intelligence of the targeted mob. The mob will forever be completely brainless, taking no further action, due to a complete time lock on it's brain.$(br2)This is an activated ability, and must be bound to a hotkey in the tool settings menu.": (
            "정신 말살 업그레이드는 대상 몹의 AI를 시간 속에 완전히 고정해 영구적으로 행동하지 "
            "못하게 합니다.$(br2)액티브 능력이므로 도구 설정 화면에서 단축키를 지정해야 합니다."
        ),
        "The Ore Miner upgrade is a passive ability which can go onto pickaxes starting at Ferricore. It automatically mines ore blocks connected to the one you mine, sort of like a 'vein miner' but only for ores, and automatic.": (
            "광석 채굴 업그레이드는 페리코어 이상의 곡괭이에 설치하는 패시브 능력입니다. 직접 "
            "캔 광석과 이어진 같은 광석 블록을 자동으로 함께 채굴합니다. 광석에만 적용되는 자동 "
            "광맥 채굴과 비슷합니다."
        ),
        "The Phase upgrade allows you to pass through walls and obstacles. Activate it to become ethereal, ignoring all physical barriers except the floor.$(br2)This allows you to walk through walls while active. Some blocks may still be solid, such as bedrock and any blocks mod pack makers specify.": (
            "위상 이동 업그레이드를 발동하면 바닥을 제외한 벽과 장애물을 통과할 수 있습니다."
            "$(br2)기반암이나 모드팩에서 따로 지정한 블록은 여전히 통과하지 못할 수 있습니다."
        ),
        "Enhance your culinary capabilities with the Smoker upgrade. Any drops from mobs will be smoked automatically! Beef will be turned into Steak.$(br2)Uses some durability.": (
            "훈연 업그레이드는 몹이 떨어뜨리는 음식 전리품을 자동으로 훈연합니다. 예를 들어 "
            "익히지 않은 소고기가 스테이크로 바뀝니다.$(br2)사용할 때 내구도를 조금 소비합니다."
        ),
        "Confuse your foes with the Stupefy upgrade. When looking at an enemy and activating this ability with a hotkey, they will immediately forget about you!.$(br2)Furthermore, they won't be able to target you again for a few moments. This ability has a cooldown!": (
            "망각 업그레이드는 바라보는 적이 즉시 플레이어를 잊게 합니다. 단축키로 발동하면 "
            "적이 잠시 동안 플레이어를 다시 대상으로 삼지 못합니다.$(br2)이 능력에는 재사용 "
            "대기 시간이 있습니다."
        ),
        "$(l:justdirethings:res_time_crystal)Time Crystals$(/l) are amazing! However, they can sometimes have unintended side effects from carrying them around. Furthermore, they may lead to time altering fields and abilities after further research.$(br2)Equipping this upgrade will protection you from any strange effects from playing around with time!": (
            "$(l:justdirethings:res_time_crystal)시간 수정$(/l)은 강력하지만 들고 다니면 의도하지 "
            "않은 시간 왜곡이 생길 수 있습니다. 더 연구하면 시간을 바꾸는 장치와 능력에도 쓰일 "
            "수 있습니다.$(br2)이 업그레이드를 장착하면 시간 조작으로 생기는 이상 현상에서 "
            "보호받습니다."
        ),
        "Treefeller is a passive ability that goes on Ferricore Axes and above. When you break a piece of wood, it will break any adjacent matching wood blocks at the same time.$(br2)Chop down those trees in a single swing!$(br2)Note: Chopping down an entire tree at once takes a bit longer than a single block!": (
            "나무 벌목은 페리코어 이상의 도끼에 설치하는 패시브 능력입니다. 원목 하나를 부수면 "
            "이어진 같은 원목 블록을 함께 부숩니다.$(br2)도끼질 한 번으로 나무 전체를 벨 수 "
            "있습니다!$(br2)나무 전체를 베는 데는 블록 하나를 부술 때보다 조금 더 오래 걸립니다."
        ),
        "Speed through your mining tasks with the Insta-Break upgrade. Equipped tools can instantly break blocks, thanks to the addition of $(l:justdirethings:res_time_crystal)Time Crystals$(/l), drastically reducing the time it takes to gather materials.$(br2)Note: Energy use significantly increases based on the hardness of the block. Obsidian costs far more energy to instantly break than stone does.": (
            "즉시 파괴 업그레이드는 $(l:justdirethings:res_time_crystal)시간 수정$(/l)의 힘으로 "
            "블록을 즉시 부숩니다.$(br2)블록이 단단할수록 에너지 소비량이 크게 늘어납니다. "
            "흑요석은 돌보다 훨씬 많은 에너지가 필요합니다."
        ),
        "The Lawn Mower upgrade is an activated ability which can be installed on shovels starting at ferricore. When you activate it, all nearby grass and flowers will be cut down, and their items will be dropped on the ground.": (
            "잔디깎이 업그레이드는 페리코어 이상의 삽에 설치하는 액티브 능력입니다. 발동하면 "
            "주변의 풀과 꽃을 모두 베고 해당 아이템을 땅에 떨어뜨립니다."
        ),
        "The leaf breaker upgrade is an activated ability. Simply right click on a leaves block to activate it, and all adjacent leaf blocks will also be broken. ": (
            "나뭇잎 파괴 업그레이드는 액티브 능력입니다. 나뭇잎 블록을 우클릭하면 이어진 "
            "나뭇잎 블록을 함께 부숩니다."
        ),
        "Gain temporary invincibility with the Invulnerability upgrade. You'll need to assign a hotkey to this ability, and activate it with the hotkey.  Once done, you'll be completely immune from all damage for a short time.$(br2)Note: There is a long cooldown before you can use it again, and it uses some durability to activate.": (
            "무적 업그레이드는 지정한 단축키로 발동하며 잠시 동안 모든 피해를 막습니다."
            "$(br2)발동할 때 내구도를 조금 소비하고, 다시 사용하기까지 긴 재사용 대기 시간이 "
            "필요합니다."
        ),
        "Advanced machines typically have the same controls as their simple counterparts and several more.$(br2)$(l)Area Affect$()$(br2)Advanced machines can affect a large area, which can be visualized by clicking the 'Render area' button, to see in-world what area the block will affect.": (
            "고급 기계에는 간단한 기계의 제어 기능과 몇 가지 추가 기능이 있습니다."
            "$(br2)$(l)작동 영역$()$(br2)고급 기계는 넓은 영역에서 작동합니다. '영역 표시' "
            "버튼을 누르면 실제 월드에서 작동 범위를 확인할 수 있습니다."
        ),
        "Using the RAD and OFF buttons will adjust where this area affect applies.$(br2)RAD will affect the radius, increase the area being affected.$(br2)OFF will affect the block offset, moving the center of the area to a different position.$(br2)Test using these button with 'render area' active.": (
            "RAD와 OFF 버튼으로 작동 영역을 조정합니다.$(br2)RAD는 반경을 바꿔 영역의 크기를 "
            "늘리거나 줄입니다.$(br2)OFF는 오프셋을 바꿔 영역의 중심을 이동합니다.$(br2)'영역 "
            "표시'를 켠 상태에서 버튼을 조정하면 결과를 쉽게 확인할 수 있습니다."
        ),
        "$(l)Filters$()$(br2)Most advanced machines have a row of filter slots, that allow you to filter what the machine affects. This might be items, blocks or entities!$(br2)You can drag from JEI to populate these, or click on them with an itemstack in your hand while in the GUI.$(br2)To filter entities, use either a spawn egg or creature catcher.": (
            "$(l)필터$()$(br2)대부분의 고급 기계에는 작동 대상을 제한하는 필터 슬롯이 "
            "있습니다. 아이템, 블록, 엔티티를 필터링할 수 있습니다.$(br2)JEI에서 항목을 "
            "끌어오거나 화면에서 아이템을 든 채 슬롯을 클릭해 등록하세요.$(br2)엔티티를 "
            "필터링하려면 생성 알이나 생물 포획기를 사용합니다."
        ),
        "You can also toggle the 'allow vs deny' list button. In allow mode, only items listed will be affected, while in deny mode,anything BUT the items listed will be affected.$(br2)Compare NBT can be used to be more specific in your filters, such as having to match enchantments or damage on a tool, or filtering a specific color of sheep if using a creature catcher.": (
            "'허용/거부 목록' 버튼도 전환할 수 있습니다. 허용 모드에서는 목록에 있는 대상만, "
            "거부 모드에서는 목록에 없는 대상만 영향을 받습니다.$(br2)'NBT 비교'를 켜면 도구의 "
            "마법 부여와 내구도, 생물 포획기에 담긴 양의 색상처럼 세부 정보까지 비교합니다."
        ),
        "The Advanced Block Placer is an upgraded version of the $(l:justdirethings:mach_blockplacert1)Simple Block Placer$(/l).$(br2)Use the filters to specify which blocks can be placed on. For example, filtering stone will only allow the placer to place on stone blocks. This filter also respects the direction setting, if set to 'down' it will only place on TOP of stone blocks.": (
            "고급 블록 배치기는 $(l:justdirethings:mach_blockplacert1)간단한 블록 배치기$(/l)의 "
            "상위 버전입니다.$(br2)필터로 아이템을 놓을 바탕 블록을 지정합니다. 돌을 필터에 "
            "넣으면 돌 블록에만 배치합니다. 방향을 '아래'로 설정했다면 돌 블록의 윗면에만 "
            "배치합니다."
        ),
        "The Simple Swapper is designed to swap blocks and/or entities in the world between it and a paired partner.$(br2)Start by placing two swappers in the world. Then use a Ferricore Wrench, right click the first swapper, then the 2nd. A message will tell you that they are bound.$(br2)The UI will also have a green button showing where its bound to.": (
            "간단한 교환기는 서로 연결된 두 위치의 블록이나 엔티티를 맞바꿉니다.$(br2)교환기 "
            "두 개를 놓은 뒤 페리코어 렌치로 첫 번째와 두 번째 교환기를 차례로 우클릭하세요. "
            "연결되었다는 메시지가 표시됩니다.$(br2)화면의 초록색 버튼에서도 연결 위치를 확인할 "
            "수 있습니다."
        ),
        "The slot in the UI is what item should be used to click with.  This could be sheers for sheering sheep, or a sword for attacking mobs. It can also be left empty, if you want to click a button.$(br2)The $(l)show fake player$() button will show (using particles in world) the direction the click will occur, based on the $(l)direction$() button.": (
            "화면의 슬롯에는 클릭 동작에 사용할 아이템을 넣습니다. 양털을 깎으려면 가위를, "
            "몹을 공격하려면 검을 넣고, 버튼만 누를 때는 비워 두어도 됩니다.$(br2)$(l)가짜 "
            "플레이어 표시$() 버튼은 $(l)방향$() 설정에 따라 클릭할 방향을 월드의 입자로 "
            "보여 줍니다."
        ),
        "The $(l)sneak$() button will toggle 'sneak' clicking, which will simulate what happens if you sneak-click an item.$(br2)The $(l)click button$() will toggle between right click, left click, and hold click, which indicates which kind of click to use. Left click for attacking, for example, and hold click for a trident. The number under hold click is how long to hold it for before releasing.": (
            "$(l)웅크리기$() 버튼은 Shift를 누른 상태의 클릭을 재현합니다.$(br2)$(l)클릭 "
            "버튼$()은 우클릭, 좌클릭, 클릭 유지 중 사용할 동작을 고릅니다. 공격에는 좌클릭, "
            "삼지창에는 클릭 유지를 사용할 수 있습니다. 클릭 유지 아래의 숫자는 버튼을 놓기 "
            "전까지 누르고 있을 시간입니다."
        ),
        "The $(l)target$() button which specify which type of thing to click on. Target $(l)blocks$() will only click on a block in that space, while target $(l)air$() will only click if there is NOT a block in that space.$(br2)Target $(l)Hostile$() will only click on hostile mobs, like zombies, while target $(l)passive$() only hits non-hostiles, like sheep or pigs.": (
            "$(l)대상$() 버튼은 클릭할 대상의 종류를 정합니다. $(l)블록$()은 해당 공간에 "
            "블록이 있을 때만, $(l)공기$()는 블록이 없을 때만 클릭합니다.$(br2)$(l)적대적 "
            "몹$()은 좀비 같은 적대적 몹만, $(l)비적대적 몹$()은 양이나 돼지 같은 비적대적 "
            "몹만 대상으로 삼습니다."
        ),
        "Target $(l)Adult$() will only hit adult mobs, like fully grown zombies or sheep, while target $(l)child$() will only target babies, like baby cows or baby zombies.$(br2)Target $(l)Player$() will only affect players.$(br2)Finally, target $(l)all living$() affects any living creature, be it a player, zombie, or baby sheep.": (
            "$(l)성체$()는 다 자란 좀비나 양만, $(l)새끼$()는 아기 소나 아기 좀비만 "
            "대상으로 삼습니다.$(br2)$(l)플레이어$()는 플레이어에게만 작동합니다.$(br2)"
            "$(l)모든 생명체$()는 플레이어, 좀비, 아기 양을 포함한 모든 생명체에 작동합니다."
        ),
        "The Advanced Clicker is an upgraded version of the $(l:justdirethings:mach_clickert1)Simple Clicker$(/l).It can affect a larger area, and will also support filtering blocks or entities.$(br2)Use a spawn egg or creature catcher to filter entities.$(br2)This can be used for a mob farm, if set to left click hostiles, or an animal breeder if set to right click adults!": (
            "고급 클릭기는 $(l:justdirethings:mach_clickert1)간단한 클릭기$(/l)의 상위 "
            "버전으로, 더 넓은 영역에서 작동하고 블록과 엔티티 필터를 지원합니다.$(br2)엔티티 "
            "필터에는 생성 알이나 생물 포획기를 사용하세요.$(br2)적대적 몹을 좌클릭하도록 설정하면 "
            "몹 농장에, 성체를 우클릭하도록 설정하면 동물 번식기에 활용할 수 있습니다."
        ),
        "The number button on this screen controls the stack size thats dropped.$(br2)By default this is 1, meaning 1 item at a time will be dropped, but increasing it will mean more items will be dropped at a time.$(br2)When set to 64, it'll drop an entire stack at once.$(br2)Note: When set to 64, it doesn't NEED to have 64 items to drop, it'll just drop as many as it has.": (
            "화면의 숫자 버튼은 한 번에 떨어뜨릴 아이템 수를 정합니다.$(br2)기본값은 1이며 "
            "숫자를 늘리면 한 번에 더 많이 떨어뜨립니다.$(br2)64로 설정하면 최대 한 묶음을 "
            "한꺼번에 떨어뜨립니다.$(br2)아이템이 64개보다 적어도 현재 들어 있는 수량만큼 "
            "정상적으로 떨어뜨립니다."
        ),
        "The 'pickup delay' button on this screen controls the pickup delay applied to the items dropped.$(br2)By default in minecraft, when you drop an item on the ground, theres a short period of time before you can pick it up again. This button controls that delay for items dropped by the dropper.$(br2)The default is 0, meaning items can be picked up immediately.": (
            "'줍기 지연' 버튼은 떨어뜨린 아이템을 다시 주울 수 있기까지의 시간을 정합니다."
            "$(br2)Minecraft에서는 보통 땅에 떨어뜨린 아이템을 바로 줍지 못하는 짧은 지연이 "
            "있습니다. 이 버튼은 공급기가 떨어뜨린 아이템의 지연을 조정합니다.$(br2)기본값은 "
            "0이므로 즉시 주울 수 있습니다."
        ),
        "The item collector works like an $(l:justdirethings:mach_advanced_controls)Advanced Machine$(/l), despite being made with Tier 1 resources.  It will vacuum up any item entites in it's area of effect, and deposit them in the inventory it's attached to.$(br2)You can filter which items are picked up in the GUI, and increase the pickup speed if desired.": (
            "아이템 수집기는 티어 1 자원으로 만들지만 "
            "$(l:justdirethings:mach_advanced_controls)고급 기계$(/l)처럼 작동합니다. 작동 영역의 "
            "아이템 엔티티를 빨아들여 연결된 인벤토리에 넣습니다.$(br2)화면에서 수집할 아이템을 "
            "필터링하고 수집 속도를 높일 수 있습니다."
        ),
        "The Player Accessor is a unique utility block that facilitates direct interaction with a player's inventory. It allows external systems like hoppers or pipes to insert or extract items directly from a player's inventory, effectively bridging the gap between player and automated storage solutions.": (
            "플레이어 접근기는 호퍼나 파이프 같은 외부 장치가 플레이어 인벤토리에 아이템을 "
            "직접 넣거나 꺼내게 하는 보조 블록입니다. 플레이어 인벤토리를 자동화 시스템에 "
            "연결할 때 사용합니다."
        ),
        "The UI buttons let you toggle which side accesses which inventory slots.$(br2)For example, you can set it so that insert into the 'top' face equips or removes armor, and the bottom face interacts with your offhand slot.": (
            "화면의 버튼으로 각 면이 접근할 인벤토리 슬롯을 정합니다.$(br2)예를 들어 윗면은 "
            "방어구 슬롯에 장착하거나 꺼내고, 아랫면은 보조 손 슬롯과 상호 작용하도록 설정할 수 "
            "있습니다."
        ),
        "The Advanced Sensor is an upgraded version of the $(l:justdirethings:mach_sensort1)Simple Sensor$(/l).$(br2)It can detect how MANY matches exist in its target area. By default, this is set to > 0, meaning if there is 1 or more matches in an area, it emits a redstone signal.": (
            "고급 센서는 $(l:justdirethings:mach_sensort1)간단한 센서$(/l)의 상위 버전입니다."
            "$(br2)대상 영역에서 조건과 일치하는 개수까지 감지합니다. 기본 조건은 > 0이므로 "
            "일치하는 대상이 하나 이상이면 레드스톤 신호를 출력합니다."
        ),
        "You can toggle the greater-than button to less-than or equals to, and then use the number button to the right to increase this.$(br2)Example use cases include, sensing if there are less than 10 adult cows, and then emitting a signal to enable a clicker to feed them.": (
            "비교 버튼을 초과, 미만, 같음으로 전환하고 오른쪽 숫자 버튼으로 기준값을 정합니다."
            "$(br2)예를 들어 성체 소가 10마리보다 적을 때 신호를 보내 클릭기가 먹이를 주게 할 "
            "수 있습니다."
        ),
        "At this time very little is known about The Paradox. The only thing scientists have been able to determine so far, is that it can be sealed shut by feeding it a $(l:justdirethings:res_time_crystal)Time Crystal$(/l).$(br2)Tossing one in should do the trick.$(br2)There will likely be more to come as studies advance.": (
            "현재 패러독스에 관해 알려진 사실은 거의 없습니다. 지금까지 확인된 것은 "
            "$(l:justdirethings:res_time_crystal)시간 수정$(/l)을 먹이면 봉인할 수 있다는 것뿐입니다."
            "$(br2)시간 수정 하나를 던져 넣으면 됩니다.$(br2)연구가 진행되면 더 많은 사실이 "
            "밝혀질 것입니다."
        ),
        "Raw Blazegold Block": "미가공 블레이즈골드 광석",
        "Raw Celestigem Block": "미가공 셀레스티젬 광석",
        "Raw Eclipse Alloy Block": "미가공 이클립스 합금 광석",
        "Raw Ferricore Block": "미가공 페리코어 광석",
        "Smelting Raw Blazegold": "블레이즈골드 원석 제련",
        "Smelting Raw Eclipse Alloy": "이클립스 합금 원석 제련",
        "Smelting Raw Ferricore": "페리코어 원석 제련",
        "Portal fluid is required to fuel the advanced portal gun.  Start by dropping a Portal Fluid Catalyst into a block of Polymorphic Fluid.$(br2)Note that the unstable version will immediately break down anywhere outside of the end!": (
            "고급 포털 건에는 포털 유체가 필요합니다. 포털 유체 촉매를 다형성 유체 원천에 "
            "떨어뜨려 불안정한 포털 유체를 만드세요.$(br2)불안정한 포털 유체는 엔드 밖에서 "
            "즉시 분해됩니다!"
        ),
        "The catalyst needed to create the unstable fluid.$(br2)Void Shimmer goo (or higher) can then be used to stabilize the fluid. Stabilized fluid can exist outside of the end.": (
            "포털 유체 촉매는 불안정한 포털 유체를 만드는 데 사용합니다.$(br2)보이드시머 구 "
            "이상으로 유체를 안정화하면 엔드 밖에서도 유지할 수 있습니다."
        ),
        "Refined Blaze Ember Fuel": "블레이즈 엠버 연료",
        "Refined Voidflame Fuel": "보이드플레임 연료",
        "Refined Eclipse Ember Fuel": "이클립스 엠버 연료",
        "Homing Crafting": "유도 업그레이드 제작",
        "Insta-Break Crafting": "즉시 파괴 업그레이드 제작",
        "No AI Crafting": "정신 말살 업그레이드 제작",
        "The advanced block breaker is an upgraded version of the $(l:justdirethings:mach_blockbreakert1)Simple Block Breaker$(/l). It can break blocks in a much larger area. Details of each feature of the UI follow.$(br2)$(l)Filter Block vs Filter Item.$()$(br2)The filter section allows you to specify what blocks to break. ": (
            "고급 블록 파괴기는 $(l:justdirethings:mach_blockbreakert1)간단한 블록 "
            "파괴기$(/l)의 상위 버전으로, 훨씬 넓은 영역의 블록을 부술 수 있습니다."
            "$(br2)$(l)블록 필터/아이템 필터$()$(br2)필터에서 파괴할 대상을 지정합니다."
        ),
        "In 'filter block' mode, this will let you specify which BLOCKS to break. For example, if you place cobblestone in there, it will only break cobblestone blocks.$(br2)In filter ITEMS mode, it specifies which item drops to allow. For example, if you place cobblestone in there, it can break either stone or cobblestone, since breaking stone will drop cobblestone (unless the pick has silk touch).": (
            "'블록 필터' 모드는 파괴할 블록 자체를 지정합니다. 조약돌을 넣으면 조약돌 블록만 "
            "부숩니다.$(br2)'아이템 필터' 모드는 파괴 후 나오는 아이템을 기준으로 합니다. "
            "조약돌을 넣으면 조약돌 블록뿐 아니라 조약돌을 떨어뜨리는 돌도 부술 수 있습니다. "
            "단, 곡괭이에 섬세한 손길이 있으면 결과가 달라집니다."
        ),
        "$(l)Direction Button.$()$(br2)The direction button lets you specify which block face to break from. Normally this doesn't matter, but if your tool has a 'hammer' like ability, it lets you specify which 'side' of the block you're hitting when you break it, so you can control the hammers direction.": (
            "$(l)방향 버튼$()$(br2)블록을 어느 면에서 때리는 것으로 처리할지 정합니다. 보통은 "
            "차이가 없지만 도구에 망치 같은 범위 능력이 있으면 파괴 영역이 펼쳐질 방향을 "
            "제어할 수 있습니다."
        ),
        "The Simple Dropper is designed to drop items into the world.$(br2)The direction button changes the direction in which items are dropped - by default this is 'downwards' like a normal dropper. Keep in mind that it'll drop in the block space that the dropper is facing.": (
            "간단한 공급기는 아이템을 월드에 떨어뜨립니다.$(br2)방향 버튼으로 아이템을 "
            "떨어뜨릴 방향을 바꿉니다. 기본값은 일반 공급기처럼 아래쪽이며, 공급기가 바라보는 "
            "블록 공간에 아이템이 생성됩니다."
        ),
        "The energy transmitter is a revolutionary way to transmit energy from your generators to machines!$(br2)First, connect this machine to a power source, like the $(l:justdirethings:mach_generatort1)Coal$(/l) or $(l:justdirethings:mach_generatorfluidt1)Fuel$(/l) generators. This will cause the internal buffer to fill with Forge Energy.": (
            "에너지 송신기는 발전기의 에너지를 기계에 무선으로 전달합니다.$(br2)먼저 "
            "$(l:justdirethings:mach_generatort1)석탄 발전기$(/l)나 "
            "$(l:justdirethings:mach_generatorfluidt1)유체 연료 발전기$(/l) 같은 전원에 "
            "연결해 내부 버퍼를 Forge Energy로 채우세요."
        ),
        "Second, define the Area of Effect, like you can with most $(l:justdirethings:mach_advanced_controls)Advanced Machines$(/l).$(br2)Any blocks inside the area of effect that can receive Forge Energy will start getting filled up by the internal buffer.$(br2)NOTE: There is a small amount of energy loss as a result of this wireless energy transfer. This is intended, and is meant as a balance for 'wireless energy' transfer. This loss is configurable.": (
            "다른 $(l:justdirethings:mach_advanced_controls)고급 기계$(/l)처럼 작동 영역을 "
            "설정하세요.$(br2)영역 안에서 Forge Energy를 받을 수 있는 블록은 송신기의 내부 "
            "버퍼에서 에너지를 공급받습니다.$(br2)무선 전송에는 설정 가능한 소량의 에너지 "
            "손실이 있습니다."
        ),
        "If you wish, you may filter the machines that receive power using the filter slots in the UI, same with most other $(l:justdirethings:mach_advanced_controls)Advanced Machines$(/l).$(br2)If another energy transmitter is inside the area of effect, they will keep each other balanced automatically. Energy balancing does not incur any energy loss. You can disable particle rendering with a button in the UI.": (
            "다른 $(l:justdirethings:mach_advanced_controls)고급 기계$(/l)처럼 필터 슬롯으로 "
            "에너지를 받을 기계를 제한할 수 있습니다.$(br2)작동 영역 안에 다른 에너지 송신기가 "
            "있으면 서로의 에너지량을 손실 없이 자동으로 맞춥니다. 화면의 버튼으로 입자 표시도 "
            "끌 수 있습니다."
        ),
        "The Simple Fluid Collector automates the collection of fluids from the world. It will try to collect any fluid in front of it, and fill it's internal buffer with that fluid. Note that it can only hold 1 fluid at a time.$(br2)The item slot can be used to fill an empty bucket, or other fluid containing item like the fluid canister.": (
            "간단한 유체 수집기는 앞에 있는 유체를 자동으로 회수해 내부 탱크에 저장합니다. 한 "
            "번에 한 종류의 유체만 담을 수 있습니다.$(br2)아이템 슬롯에서는 빈 양동이나 유체 "
            "캔 같은 용기에 저장된 유체를 채울 수 있습니다."
        ),
        "Building on the $(l:justdirethings:mach_fluidcollectort1)Simple Fluid Collector$(/l), the Advanced Fluid Collector can collect fluids from a larger area, and offers the ability to filter upon which fluids are collected.$(br2)Simply place a bucket of the appropriate fluid in the filter slots to filter which fluids can be picked up.": (
            "고급 유체 수집기는 $(l:justdirethings:mach_fluidcollectort1)간단한 유체 "
            "수집기$(/l)보다 넓은 영역의 유체를 회수하고 필터도 지원합니다.$(br2)필터 슬롯에 "
            "원하는 유체 양동이를 넣어 회수할 유체를 지정하세요."
        ),
        "Transformed by VoidShimmer Goo, a Diamond Block becomes a Raw Celestigem Block. Mine this block to get $(l:justdirethings:res_celestigem)Celestigem$(/l).": (
            "다이아몬드 블록을 보이드시머 구로 변환하면 미가공 셀레스티젬 광석이 됩니다. 이 "
            "블록을 채굴하면 $(l:justdirethings:res_celestigem)셀레스티젬$(/l)을 얻습니다."
        ),
        "The Celestigem Paxel combines the capabilities of a pickaxe, axe, and shovel. Crafted with the respective tools, it inherits their upgrades, offering versatility and extended utility.$(br2)Craft it by combining a Celestigem Pickaxe, Axe, and Shovel in a smithing table. Any installed upgrades on the tools will carry over to the paxel.": (
            "셀레스티젬 팍셀은 곡괭이, 도끼, 삽의 기능을 하나로 합친 도구입니다.$(br2)"
            "대장장이 작업대에서 셀레스티젬 곡괭이·도끼·삽을 합쳐 제작하며, 세 도구에 설치된 "
            "업그레이드는 팍셀에 그대로 이어집니다."
        ),
        "The experience holder does what it says on the tin. It holds experience!$(br2)In the UI, you'll see the current levels stored (represented by the green number), and the partial levels stored (represented by the green exp bar). Clicking the + or - buttons will transfer 1 level from you (the player) to the block.": (
            "경험치 저장기는 플레이어의 경험치를 보관합니다.$(br2)화면의 초록색 숫자는 저장된 "
            "레벨을, 초록색 경험치 막대는 한 레벨보다 적은 경험치를 나타냅니다. +와 - 버튼으로 "
            "플레이어와 블록 사이에 한 레벨씩 옮깁니다."
        ),
        "Hold Shift while clicking these buttons to transfer 10 levels at a time, and hold Ctrl while clicking to transfer ALL your levels at once!$(br2)You'll notice this has an Area of Effect on it, which serves two purposes. First of which is automating nearby player's experience levels.": (
            "Shift를 누른 채 버튼을 클릭하면 10레벨씩, Ctrl을 누른 채 클릭하면 모든 레벨을 "
            "한꺼번에 옮깁니다.$(br2)이 블록의 작동 영역에는 두 가지 용도가 있으며, 첫 번째는 "
            "주변 플레이어의 경험치 레벨을 자동으로 조정하는 것입니다."
        ),
        "Using the Number Button to the left of the - button, set the desired amount of experience a player inside the area of affect should have. Then, use the redstone control button to determine when this occurs, either on pulse (by default) or always. The machine will use the Speed (ticks) to attempt to modify nearby player(s) levels every so often.": (
            "- 버튼 왼쪽의 숫자 버튼으로 작동 영역 안의 플레이어가 유지할 목표 레벨을 "
            "정하세요. 레드스톤 제어 버튼으로 기본값인 펄스 작동이나 상시 작동을 고르고, "
            "속도(틱)에서 주변 플레이어의 레벨을 확인할 간격을 설정합니다."
        ),
        "The machine will add or remove levels to the player as needed to get that player's level at the target -- assuming of course theres enough exp stored in the machine to raise them that high!$(br2)Toggle the 'owner only' button to ensure this only gives experience to the player who originally placed the block.": (
            "기계는 플레이어가 목표 레벨에 도달하도록 경험치를 넣거나 회수합니다. 레벨을 "
            "올리려면 기계에 충분한 경험치가 저장되어 있어야 합니다.$(br2)'소유자 전용'을 켜면 "
            "처음 블록을 설치한 플레이어에게만 경험치를 줍니다."
        ),
        "Use this to automatically store your experience when you return to your base by setting it to 0, or keep your experience always at level 30 while enchanting at an enchanting table! Every time you enchant something, this machine can automatically top you off back to exactly level 30!": (
            "목표를 0으로 설정하면 기지에 돌아왔을 때 경험치를 자동으로 보관할 수 있습니다. "
            "마법 부여대 옆에서 목표를 30으로 설정하면 마법을 부여할 때마다 레벨을 다시 정확히 "
            "30으로 채울 수도 있습니다."
        ),
        "In addition, there is a 'Collect Experience' button, which will attempt to find experience orbs inside the area of effect.  When this is enabled, it will absorb any exp orbs nearby, and store them.  This feature ignores the redstone state of the block, and either runs or not based on this buttons setting.": (
            "'경험치 수집'을 켜면 작동 영역 안의 경험치 구슬을 흡수해 저장합니다. 이 기능은 "
            "블록의 레드스톤 설정과 관계없이 버튼의 켜짐/꺼짐 상태만 따릅니다."
        ),
        "The block is a fluid tank as well, and can transfer exp points into XP Fluid at a rate of 20mb per 1 experience point.  You can interact with this block using either a bucket or the $(l:justdirethings:item_fluid_canister)Fluid Canister$(/l).$(br2)Its also possible to extract or insert the fluid using pipes or Laserio, etc.$(br2)The block will retain its experience when broken, so no worries if you need to relocate it!": (
            "이 블록은 유체 탱크이기도 하며 경험치 1포인트를 경험치 유체 20 mB로 바꿉니다. "
            "양동이나 $(l:justdirethings:item_fluid_canister)유체 캔$(/l)으로 상호 작용할 수 "
            "있습니다.$(br2)파이프나 LaserIO로 유체를 넣고 뺄 수도 있습니다.$(br2)블록을 "
            "부숴 옮겨도 저장된 경험치는 유지됩니다."
        ),
        "The paradox machine is the next evolution in Time Manipulation Technology!$(br2)It allows you to take a 'snapshot' of an area of the world, recording the entities and blocks that exist at the moment you click the button.$(br2)This machine can rewind time to the point where those things existed.": (
            "패러독스 기계는 시간 조작 기술의 다음 단계입니다!$(br2)버튼을 누른 순간 작동 영역에 "
            "있는 블록과 엔티티를 '스냅샷'으로 기록합니다.$(br2)이후 그 상태로 시간을 되돌릴 수 "
            "있습니다."
        ),
        "First, place the machine in the world, and designate an area of effect like with most advanced machines.$(br2)Second, place any Blocks (Raw Ores only!) or Entities (Zombies, cows, etc) into the area of effect that you'd like to save.$(br2)Finally, click the 'snapshot' button in the machine's UI.": (
            "먼저 기계를 놓고 다른 고급 기계처럼 작동 영역을 지정합니다.$(br2)저장할 블록은 "
            "원광석만 가능하며, 좀비나 소 같은 엔티티도 영역 안에 놓을 수 있습니다.$(br2)마지막으로 "
            "기계 화면의 '스냅샷' 버튼을 누르세요."
        ),
        "Now, the machine will need a significant amount of both Power and Time Fluid.  After clearing the area of blocks or entities, activate the machine. The blocks and entities you've cleared will be restored!$(br2)Note: A button on the UI allows you to toggle between Entities Only, Blocks Only, or both.": (
            "복원에는 많은 에너지와 시간 유체가 필요합니다. 영역에서 기록한 블록이나 엔티티를 "
            "치운 뒤 기계를 작동하면 원래 상태로 복원됩니다!$(br2)화면의 버튼으로 엔티티만, "
            "블록만, 또는 둘 다 복원하도록 선택할 수 있습니다."
        ),
        "Now, technically speaking, the Paradox Machine doesn't exactly revert to entities and blocks from a previous point in time.$(br2)Its more like it is grabbing that entity from a parallel universe at a prior point in its own time stream. Its all very technical!$(br2)What this means is the entities may not be EXACTLY identical to the one you snapshot.": (
            "엄밀히 말하면 패러독스 기계는 과거의 블록과 엔티티를 그대로 되돌리는 것이 아닙니다."
            "$(br2)평행 우주의 이전 시간대에서 대상을 가져오는 것에 가깝습니다.$(br2)따라서 "
            "복원된 엔티티가 스냅샷의 대상과 완전히 같지 않을 수 있습니다."
        ),
        "$(bold)WARNING!!!$()$(br2)Overuse of this machine can lead to some corruption of the space time continuum.  A dangerous side effect known as the $(l:justdirethings:misc_paradox)Paradox$(/l) can appear after extended use! The machine will track the buildup of paradox energy, and represent it on the UI.$(br2)User Discretion is Advised.$(br2)They should really print the warning before the spell.": (
            "$(bold)경고!!!$()$(br2)이 기계를 지나치게 사용하면 시공간 연속체가 손상되고 "
            "$(l:justdirethings:misc_paradox)패러독스$(/l)라는 위험한 부작용이 나타날 수 "
            "있습니다. 기계 화면에서 패러독스 에너지의 축적량을 확인할 수 있습니다.$(br2)"
            "신중하게 사용하세요.$(br2)정말 주문보다 경고문을 먼저 보여 줘야겠군요."
        ),
        "The $(l)target$() button lets you cycle between targeting Blocks, Air, Hostile, Passive, Adult, Child, Player, All Living, and Item entities. See the $(l:justdirethings:mach_clickert1)Simple Clicker$(/l) book entry for details on what each of these do.$(br2)Items mode will detect items sitting in the world in front of the block.": (
            "$(l)대상$() 버튼으로 블록, 공기, 적대적 몹, 비적대적 몹, 성체, 새끼, 플레이어, "
            "모든 생명체, 아이템 엔티티를 차례로 선택합니다. 자세한 설명은 "
            "$(l:justdirethings:mach_clickert1)간단한 클릭기$(/l) 항목을 확인하세요.$(br2)아이템 "
            "모드는 블록 앞의 월드에 놓인 아이템을 감지합니다."
        ),
        "When targeting blocks, you can right click the filter slot to designate a specific block STATE to filter on!$(br)For example, you can detect whether a door is opened or closed, or a level is on or off.$(br2)Simply right click on the filter slot when a block is in it, and you'll see a list of all blockstates on the left. Click on each one to cycle through the options.": (
            "블록을 대상으로 할 때 필터 슬롯을 우클릭하면 특정 블록 상태까지 지정할 수 "
            "있습니다!$(br)예를 들어 문이 열렸는지 닫혔는지, 레버가 켜졌는지 꺼졌는지를 "
            "감지할 수 있습니다.$(br2)필터에 블록을 넣고 슬롯을 우클릭하면 왼쪽에 모든 블록 "
            "상태가 나타납니다. 각 항목을 클릭해 조건을 바꾸세요."
        ),
        "Simple machines typically have the following controls.$(br2)$(l)Redstone Button$()$(br2)The redstone button controls when the machine runs. By default redstone is ignored, meaning the machine always runs.$(br2)Low means the machine will only run when NOT receiving a redstone signal.": (
            "간단한 기계에는 보통 다음 제어 기능이 있습니다.$(br2)$(l)레드스톤 버튼$()"
            "$(br2)기본값은 레드스톤 신호를 무시해 항상 작동합니다.$(br2)'낮음'은 레드스톤 "
            "신호를 받지 않을 때만 작동합니다."
        ),
        "High means the machine will only run when it is receiving a redstone signal$(br2)Finally, pulse will make the machine do a single operation per redstone pulse. For simple machines, this usually means doing 1 thing, like breaking 1 block. For advanced machines, it may mean breaking all the blocks in its area.": (
            "'높음'은 레드스톤 신호를 받을 때만 작동합니다.$(br2)'펄스'는 레드스톤 펄스마다 "
            "작업을 한 번 수행합니다. 간단한 기계라면 블록 한 개를 부수는 식이고, 고급 기계라면 "
            "작동 영역의 모든 블록을 한 번에 처리할 수 있습니다."
        ),
        "$(l)Speed(ticks) Button$()$(br2)This is how often the machine runs while active. When set to the default (20) it will operate once every second (or 20 ticks).$(br2)It can be reduced as far as 1, meaning it will operate every tick (or 20 times per second), but avoid doing this unless absolutely necessary, as this could contribute to lag.": (
            "$(l)속도(틱) 버튼$()$(br2)기계가 작동 중일 때 작업할 간격을 정합니다. 기본값 "
            "20은 20틱, 즉 1초마다 한 번 작동합니다.$(br2)최솟값 1은 매 틱, 즉 초당 20회 "
            "작동합니다. 지연을 일으킬 수 있으므로 꼭 필요할 때만 사용하세요."
        ),
        "The Simple Coal Generator is a basic machine for generating energy. While you can use simple fuels, like any furnace burnable fuel, it can also use various tiers of specialized coal to generate Forge Energy (FE). Higher tiers of coal, such as $(l:justdirethings:res_coal_t1)Primal Coal$(/l), $(l:justdirethings:res_coal_t2)Blaze Ember$(/l), $(l:justdirethings:res_coal_t3)Voidflame Coal$(/l), and $(l:justdirethings:res_coal_t4)Eclipse Ember$(/l), increase both the FE per tick (FE/T) and total FE generated.": (
            "간단한 석탄 발전기는 화로에서 태울 수 있는 일반 연료나 이 모드의 특수 석탄으로 "
            "Forge Energy(FE)를 만듭니다. $(l:justdirethings:res_coal_t1)프라이멀 석탄$(/l), "
            "$(l:justdirethings:res_coal_t2)블레이즈 엠버$(/l), "
            "$(l:justdirethings:res_coal_t3)보이드플레임 석탄$(/l), "
            "$(l:justdirethings:res_coal_t4)이클립스 엠버$(/l) 순으로 티어가 높아지며 틱당 "
            "FE와 총 생성량이 모두 늘어납니다."
        ),
        "The Simple Block Placer automates the placement of blocks. When powered, it places the block held within its inventory into the space in front of it.$(br2)Use the direction button to indicate which 'direction' to place your items in. Useful for things like torches..": (
            "간단한 블록 배치기는 인벤토리의 블록을 앞쪽 공간에 자동으로 놓습니다.$(br2)방향 "
            "버튼으로 어느 면을 향해 배치할지 정할 수 있어 횃불처럼 방향이 있는 블록에 "
            "유용합니다."
        ),
        "The $(l)blocks$() button lets you toggle between swapping blocks or not. When enabled, it'll swap blocks in front of the swappers with each other. When disabled, it'll ignore them.$(br2)The $(l)entities$() button matches the functionality of the  $(l:justdirethings:mach_clickert1)Simple Clicker$(/l) filters for entities.": (
            "$(l)블록$() 버튼을 켜면 두 교환기 앞의 블록을 서로 바꾸고, 끄면 블록을 무시합니다."
            "$(br2)$(l)엔티티$() 버튼의 대상 설정은 "
            "$(l:justdirethings:mach_clickert1)간단한 클릭기$(/l)의 엔티티 필터와 같습니다."
        ),
        "When swapping blocks, block entities like chests will swap just fine.$(br2)You can use this to switch out different chests or machines, or swap two types of blocks in the world.": (
            "상자 같은 블록 엔티티도 내용물과 함께 정상적으로 교환됩니다.$(br2)서로 다른 상자나 "
            "기계를 맞바꾸거나 월드의 두 블록 종류를 한꺼번에 교체할 수 있습니다."
        ),
        "The Advanced Swapper is an upgraded version of the $(l:justdirethings:mach_blockswappert1)Simple Swapper$(/l).$(br2)Its main feature upgrades include area of effect and filtering entities/blocks.$(br2)When bound to another swapper, the 'Radius' settings will replicate to each other, meaning if you change the radius on one block, it'll copy to its partner.": (
            "고급 교환기는 $(l:justdirethings:mach_blockswappert1)간단한 교환기$(/l)에 작동 "
            "영역과 블록·엔티티 필터를 추가한 상위 버전입니다.$(br2)블록과 엔티티를 넓은 "
            "영역에서 필터링할 수 있습니다.$(br2)연결된 교환기 두 개는 반경 설정을 공유하므로 "
            "한쪽에서 바꾸면 다른 쪽에도 복사됩니다."
        ),
        "The Advanced Dropper is an upgraded version of the $(l:justdirethings:mach_droppert1)Simple Dropper$(/l).$(br2)Unlike most Advanced machines, you can't change the radius, but can you change the offset, meaning you can drop items further away from the dropper itself.": (
            "고급 공급기는 $(l:justdirethings:mach_droppert1)간단한 공급기$(/l)의 상위 "
            "버전입니다.$(br2)다른 고급 기계와 달리 반경은 바꿀 수 없지만 오프셋을 조정해 "
            "공급기에서 더 먼 위치에 아이템을 떨어뜨릴 수 있습니다."
        ),
        "There is a 3x3 grid to fill with droppable items.$(br2)The filter slots at the bottom can be used to specify which items are allowed to be dropped, and more importantly, which ORDER they drop in! For example, if you put cobblestone, followed by redstone, it will drop cobblestone first, then redstone next.$(br2)If you run out of redstone, it'll stop dropping until it gets more.": (
            "3x3 인벤토리에 떨어뜨릴 아이템을 넣습니다.$(br2)아래쪽 필터 슬롯은 허용할 "
            "아이템과 배출 순서를 정합니다. 조약돌 다음에 레드스톤을 등록하면 조약돌을 먼저, "
            "레드스톤을 다음에 떨어뜨립니다.$(br2)차례가 된 레드스톤이 없으면 보충될 때까지 "
            "배출을 멈춥니다."
        ),
        "The Advanced Fluid Placer builds upon the $(l:justdirethings:mach_fluidplacert1)Simple Fluid Placer$(/l)$(br2)It can place fluids in a larger area, and much like its partner, the $(l:justdirethings:mach_blockplacert2)Advanced Placer$(/l), the filter slots allow you to specify which blocks to place fluids on.": (
            "고급 유체 배치기는 $(l:justdirethings:mach_fluidplacert1)간단한 유체 배치기$(/l)의 "
            "상위 버전으로, 더 넓은 영역에 유체를 놓습니다.$(br2)"
            "$(l:justdirethings:mach_blockplacert2)고급 블록 배치기$(/l)처럼 필터 슬롯에서 "
            "유체를 놓을 바탕 블록을 지정할 수 있습니다."
        ),
        "The paradox will absorb any blocks, items, or entities in its area of effect. Once they've been consumed, theres no getting them back! Where did they go? No one really knows.$(br2)The only thing we do know, is that the more it consumes, the faster it grows!$(br2)Luckily there seems to be a limit to its size.": (
            "패러독스는 작동 영역의 블록, 아이템, 엔티티를 흡수하며 한번 삼킨 것은 되찾을 수 "
            "없습니다! 어디로 갔는지는 아무도 모릅니다.$(br2)확실한 것은 많이 삼킬수록 더 빨리 "
            "커진다는 점입니다.$(br2)다행히 크기에는 한계가 있는 듯합니다."
        ),
        "Refined Blaze Ember Fuel is a potent source of energy. It is produced by processing Unrefined Blaze Ember Fuel, which is obtained by dropping $(l:justdirethings:res_coal_t2)Blaze Ember$(/l) into $(l:justdirethings:res_polymorphic_fluid)Polymorphic Fluid$(/l). Place this mixture beside a Blazebloom Goo block to refine it.": (
            "블레이즈 엠버 연료는 강력한 에너지원입니다. "
            "$(l:justdirethings:res_coal_t2)블레이즈 엠버$(/l)를 "
            "$(l:justdirethings:res_polymorphic_fluid)다형성 유체$(/l)에 떨어뜨려 정제되지 않은 "
            "블레이즈 엠버 연료를 만든 뒤, 블레이즈블룸 구 옆에 놓아 정제하세요."
        ),
        "Refined Voidflame Fuel is crafted by enhancing Unrefined Voidflame Fuel. Start by dropping $(l:justdirethings:res_coal_t3)Voidflame Coal$(/l) into $(l:justdirethings:res_refined_fuel_t2)Refined Blaze Ember Fuel$(/l). Then, expose this fluid to a VoidShimmer Goo block for refinement. This fuel variant is noted for its superior energy output compared to previous tier fuels, significantly boosting FE/T and total FE generation.": (
            "$(l:justdirethings:res_coal_t3)보이드플레임 석탄$(/l)을 "
            "$(l:justdirethings:res_refined_fuel_t2)블레이즈 엠버 연료$(/l)에 떨어뜨려 정제되지 "
            "않은 보이드플레임 연료를 만드세요. 이 유체를 보이드시머 구 옆에 놓으면 정제됩니다. "
            "이전 티어보다 틱당 FE와 총 FE 생성량이 큽니다."
        ),
        "To produce Refined Eclipse Ember Fuel, begin with Unrefined Eclipse Ember Fuel. This initial stage is made by dropping $(l:justdirethings:res_coal_t4)Eclipse Ember$(/l) into $(l:justdirethings:res_refined_fuel_t3)Refined Voidflame Fuel$(/l). Place the resulting fluid next to a Shadowpulse Goo block for the final refinement. This top-tier fuel offers the highest FE/T and total FE output, ideal for powering advanced machinery and systems.": (
            "$(l:justdirethings:res_coal_t4)이클립스 엠버$(/l)를 "
            "$(l:justdirethings:res_refined_fuel_t3)보이드플레임 연료$(/l)에 떨어뜨려 정제되지 "
            "않은 이클립스 엠버 연료를 만드세요. 이 유체를 섀도우펄스 구 옆에 놓으면 최종 "
            "티어 연료로 정제됩니다. 틱당 FE와 총 FE 생성량이 가장 큽니다."
        ),
    }
)

# 같은 영어 문구가 다른 파일에서 다른 의미로 쓰이거나, 원문 자체의 제목이 잘못된 경우에는
# 파일 단위로 교정한다. 기존 한국어 후보는 사용하지 않고 현재 JAR의 영어 문구와 직접 대조한 값이다.
FILE_SOURCE_OVERRIDES = {
    (
        "entries/upgrade_timeprotection.json",
        "Walk Speed Upgrade Crafting",
    ): "시간 조작 방지 업그레이드 제작",
    (
        "entries/mach_itemcollector.json",
        "Simple Block Breaker",
    ): "아이템 수집기",
}

TERM_OVERRIDES = {
    "Just Dire Things": "Just Dire Things",
    "Goo Spreading": "구 확산",
    "Goo Spread": "구 확산",
    "Goo": "구",
    "Upgrade": "업그레이드",
    "Upgrades": "업그레이드",
    "Ability": "능력",
    "Abilities": "능력",
    "Redstone": "레드스톤",
    "Forge Energy": "Forge Energy",
    "FE": "FE",
    "RF": "RF",
    "JEI": "JEI",
}

TEXT_REPLACEMENTS = (
    ("저스트 다이어 띵스", "Just Dire Things"),
    ("오직 끔찍한 것들", "Just Dire Things"),
    ("끈적이 퍼뜨리기", "구 확산"),
    ("끈적임 확산", "구 확산"),
    ("끈적끈적한", "구"),
    ("끈적이", "구"),
    ("다형성 액체", "다형성 유체"),
    ("차원문 액체", "포털 유체"),
    ("차원문 총", "포털 건"),
    ("포탈", "포털"),
    ("블레이즈 불씨", "블레이즈 엠버"),
    ("공허 화염", "보이드플레임"),
    ("공허불꽃", "보이드플레임"),
    ("원시 석탄", "프라이멀 석탄"),
    ("프라이모겔", "프라이모젤"),
    ("공허 쉬머", "보이드시머"),
    ("그림자 펄스", "섀도우펄스"),
    ("상위 버전", "업그레이드"),
    ("광물 스캐너", "광석 스캐너"),
    ("하늘 청소부", "낙하물 제거"),
    ("잎 파괴기", "나뭇잎 파괴"),
    ("자동 제련기", "자동 제련"),
    ("자동 훈연기", "자동 훈연"),
    ("전원", "에너지"),
    ("마우스 오른쪽 버튼", "우클릭"),
    ("마우스 왼쪽 버튼", "좌클릭"),
    ("오른쪽 클릭", "우클릭"),
    ("왼쪽 클릭", "좌클릭"),
    ("Eclipse Alloy", "이클립스 합금"),
    ("Blazegold", "블레이즈골드"),
    ("Ferricore", "페리코어"),
    ("Netherite", "네더라이트"),
    ("Blazebloom", "블레이즈블룸"),
    ("Void Shimmer goo", "보이드시머 구"),
    ("Goo", "구"),
    ("goo", "구"),
    ("Iron", "철"),
    ("Swapper", "교환기"),
    ("Generator", "발전기"),
    ("Advanced Machines", "고급 기계"),
    ("Advanced Machine", "고급 기계"),
    ("Machine", "기계"),
    ("Simple Placer", "간단한 배치기"),
    ("Advanced Placer", "고급 배치기"),
    ("Area Affect", "작동 영역"),
    ("Filter", "필터"),
    ("ITEMS", "아이템"),
    ("blocks", "블록"),
    ("entities", "엔티티"),
    ("sneak", "웅크리기"),
    ("target blocks", "블록 대상"),
    ("target air", "공기 대상"),
    ("Target Hostile", "적대적 몹 대상"),
    ("Target passive", "비적대적 몹 대상"),
    ("Adult/child", "성체/새끼"),
    ("Target Player", "플레이어 대상"),
    ("Coal Fuel", "석탄 연료"),
    ("Control", "제어"),
    ("Tier", "티어"),
    ("redstone", "레드스톤"),
    ("target Items", "아이템 대상"),
    ("Low", "낮음"),
    ("Speed (ticks)", "속도(틱)"),
    ("Refined", "정제된"),
    ("The Overworld", "오버월드"),
    ("The Nether", "네더"),
    ("The End", "엔드"),
    ("Overworld", "오버월드"),
    ("Budding", "싹트는"),
    ("Time Energy", "시간 에너지"),
    ("paxel", "팍셀"),
    ("Tools", "도구"),
    ("Armor", "방어구"),
    ("Smithing Table", "대장장이 작업대"),
    ("passive", "패시브"),
    ("active", "액티브"),
    ("Drop Teleport", "전리품 순간이동"),
    ("Homing", "유도"),
    ("Insta-Break", "즉시 파괴"),
    ("Step Height", "자동 오르기"),
    ("shift", "Shift"),
    ("Axolotl", "아홀로틀"),
    ("Hold 활성화된", "활성화된"),
    ("E각", "각"),
    ("Laserio", "LaserIO"),
    ("RAD", "RAD"),
    ("OFF", "OFF"),
    ("target", "대상"),
    ("Target", "대상"),
    ("air", "공기"),
    ("Hostile", "적대적 몹"),
    ("Adult", "성체"),
    ("child", "새끼"),
    ("Player", "플레이어"),
    ("Items", "아이템"),
    ("Coal", "석탄"),
    ("Fuel", "유체 연료"),
    ("Speed", "속도"),
    ("ticks", "틱"),
    ("End", "엔드"),
    ("Eclipse", "이클립스"),
    ("흉갑는", "흉갑은"),
    ("검는", "검은"),
    ("활는", "활은"),
    ("팍셀는", "팍셀은"),
    ("캔는", "캔은"),
    ("건는", "건은"),
    ("석탄는", "석탄은"),
    ("수정는", "수정은"),
    ("셀레스티젬는", "셀레스티젬은"),
    ("셀레스티젬를", "셀레스티젬을"),
    ("원석가", "원석이"),
    ("원석를", "원석을"),
    ("검를", "검을"),
    ("캔s", "캔"),
    ("수정s", "수정"),
    ("에너지을", "에너지를"),
    ("에너지이", "에너지가"),
    ("능력는", "능력은"),
    ("대장장이 작업대을", "대장장이 작업대를"),
    ("우클릭으로 클릭", "우클릭"),
    ("좌클릭으로 클릭", "좌클릭"),
    ("Shift를 우클릭", "Shift + 우클릭"),
    ("Shift 클릭", "Shift + 클릭"),
    ("레시피", "제작법"),
    ("구성 메뉴", "설정 화면"),
    ("구성 화면", "설정 화면"),
    ("구성할", "설정할"),
    ("구성하고", "설정하고"),
    ("구성된", "설정된"),
    ("구성 가능", "설정 가능"),
    ("구성됩니다", "설정됩니다"),
    ("구성하세요", "설정하세요"),
    ("렌더링", "표시"),
    ("단조 에너지", "Forge Energy"),
    ("대장간 에너지", "Forge Energy"),
    ("전력", "에너지"),
    ("개체", "엔티티"),
    ("단체", "엔티티"),
    ("폭도", "몹"),
    ("바인딩", "연결"),
    ("쿨다운", "재사용 대기 시간"),
    ("공급원 블록", "원천 블록"),
    ("소스 블록", "원천 블록"),
    ("항목", "아이템"),
    ("도구 설명", "툴팁"),
    ("제작 템플릿", "형판"),
    ("템플릿", "형판"),
    ("대장간 테이블", "대장장이 작업대"),
    ("페리코어 레벨", "페리코어 티어"),
    ("크리쳐", "몹"),
    ("스왑퍼", "교환기"),
    ("단순한", "간단한"),
    ("홀드 클릭", "클릭 유지"),
    ("사용 능력", "액티브 능력"),
    ("수동 능력", "패시브 능력"),
    ("활성화 능력", "액티브 능력"),
    ("단축키에 연결", "단축키에 지정"),
    ("당신", "플레이어"),
    ("이 제품", "이 아이템"),
    ("머신", "기계"),
    ("액세스할 수 있습니다", "열 수 있습니다"),
    ("액세스합니다", "엽니다"),
    ("내구력", "내구도"),
    ("방울", "전리품"),
    ("등급", "티어"),
    ("계층", "티어"),
    ("재사용 대기시간", "재사용 대기 시간"),
    ("재사용 대기 시간 기간", "재사용 대기 시간"),
    ("우클릭을 클릭", "우클릭"),
    ("좌클릭을 클릭", "좌클릭"),
    ("전력을", "에너지를"),
    ("전력이", "에너지가"),
    ("단순 블록", "간단한 블록"),
    ("파괴자", "파괴기"),
    ("공허쉬머", "보이드시머"),
    ("업그레이드d,", "상위 버전으로,"),
    ("이클립스 합금로", "이클립스 합금으로"),
    ("페리코어 이전 제품", "이전 티어인 페리코어"),
    ("용암 근원 블록", "용암 원천 블록"),
    ("플레이어을", "플레이어를"),
    ("플레이어이", "플레이어가"),
    ("티어은", "티어는"),
    ("티어이", "티어가"),
    ("기계은", "기계는"),
    ("기계이", "기계가"),
    ("삽는", "삽은"),
    ("캔를", "캔을"),
    ("캔와", "캔과"),
    ("팍셀를", "팍셀을"),
    ("토양로", "토양으로"),
    ("토양는", "토양은"),
    ("내구도을", "내구도를"),
    ("낮음는", "낮음은"),
    ("표시을", "표시를"),
    ("에너지과", "에너지와"),
    ("0로", "0으로"),
    ("20 횟수", "20회"),
    ("스토리지", "저장 공간"),
    ("데미지", "피해"),
    ("철제 헬멧", "철 투구"),
    ("철 갑옷", "철 방어구"),
    ("마법 테이블", "마법 부여대"),
    ("버킷", "양동이"),
    ("엔터티", "엔티티"),
    ("세련된 ", "정제된 "),
    ("스포이드", "공급기"),
    ("끝 외부", "엔드 밖"),
    ("끝이 아닌 곳", "엔드가 아닌 곳"),
    ("양동이을", "양동이를"),
    ("양동이이나", "양동이나"),
    ("쿨타임", "재사용 대기 시간"),
    ("수동적 동물", "비적대적 동물"),
    ("역설은", "패러독스는"),
)

ALLOWED_LATIN = {
    "Just Dire Things",
    "JDT",
    "FE",
    "RF",
    "JEI",
    "NBT",
    "GUI",
    "Shift",
    "Ctrl",
    "Alt",
    "Minecraft",
    "NeoForge",
    "Direwolf20",
    "Forge Energy",
    "LaserIO",
    "Curios",
    "RAD",
    "OFF",
    "Enderman",
    "Endermen",
    "Elytra",
    "Redstone",
    "Cardboard Box",
    "Cut Paste Gadget",
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


def find_jar(instance: Path) -> Path:
    matches = sorted((instance / "mods").glob("justdirethings-*.jar"))
    if len(matches) != 1:
        raise RuntimeError(
            f"Just Dire Things JAR을 하나로 확정하지 못했습니다: {matches}"
        )
    return matches[0]


def visible_locations(
    value: object, path: tuple[object, ...] = ()
) -> list[tuple[tuple[object, ...], str]]:
    rows: list[tuple[tuple[object, ...], str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (*path, key)
            if key in VISIBLE_FIELDS and isinstance(child, str):
                rows.append((child_path, child))
            rows.extend(visible_locations(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(visible_locations(child, (*path, index)))
    return rows


def set_path(value: object, path: tuple[object, ...], translated: str) -> None:
    current = value
    for part in path[:-1]:
        current = current[part]  # type: ignore[index]
    current[path[-1]] = translated  # type: ignore[index]


def item_name_map() -> dict[str, str]:
    english = language.load_json(
        PROJECT_ROOT / "working/just_dire_things/justdirethings/en_us.json"
    )
    korean = language.load_json(
        PROJECT_ROOT / "working/just_dire_things/justdirethings/ko_kr.json"
    )
    return {
        source: korean[key]
        for key, source in english.items()
        if key.startswith(("block.", "item.", "fluid_type.", "entity."))
        and isinstance(source, str)
        and isinstance(korean[key], str)
    }


def prepare() -> dict[str, object]:
    """현재 JAR 가이드, 발전 과제, KubeJS 관련 표시 경로를 조사한다."""
    instance = resolve_source_root()
    jar = find_jar(instance)
    files = 0
    advancement_rows: list[dict[str, object]] = []
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            if name.startswith(BOOK_PREFIX) and name.endswith(".json"):
                relative = name.removeprefix(BOOK_PREFIX)
                write_json(ENGLISH_ROOT / relative, json.loads(archive.read(name)))
                files += 1
            elif "/advancement/" in name and name.endswith(".json"):
                data = json.loads(archive.read(name))
                display = data.get("display") if isinstance(data, dict) else None
                advancement_rows.append(
                    {
                        "path": name,
                        "has_display": isinstance(display, dict),
                        "display": display if isinstance(display, dict) else None,
                    }
                )
        write_json(WORK_ROOT / "book_en_us.json", json.loads(archive.read(BOOK_SOURCE)))
    write_json(WORK_ROOT / "advancements.json", advancement_rows)

    reference = re.compile(r"justdirethings|just_dire_things|just dire things", re.I)
    visible_api = re.compile(
        r"displayName|tooltip|custom_name|Text\.(?:of|translatable)|"
        r'["\'](?:text|title|description|name)["\']\s*:',
        re.I,
    )
    kubejs_files: list[str] = []
    visible_literals: list[str] = []
    for path in sorted((instance / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".json", ".snbt"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if not reference.search(text):
            continue
        relative = path.relative_to(instance).as_posix()
        kubejs_files.append(relative)
        for number, line in enumerate(text.splitlines(), 1):
            if reference.search(line) and visible_api.search(line):
                visible_literals.append(f"{relative}:{number}:{line.strip()}")
    report = {
        "jar": jar.name,
        "english_files": files,
        "advancements": len(advancement_rows),
        "advancements_with_display": sum(
            row["has_display"] for row in advancement_rows
        ),
        "kubejs_reference_files": kubejs_files,
        "kubejs_visible_literals": visible_literals,
    }
    write_json(WORK_ROOT / "scope.json", report)
    return report


def protect_terms(source: str, names: dict[str, str]) -> tuple[str, list[str]]:
    """고유명사를 자동 번역에서 보호하고 복원할 한국어 목록을 반환한다."""
    terms = {**TERM_OVERRIDES, **names, **language.ABILITY_NAMES}
    replacements: list[str] = []
    value = source
    for english, korean in sorted(
        terms.items(), key=lambda row: len(row[0]), reverse=True
    ):
        if english not in value:
            continue
        token = f"<JDTTERM{len(replacements)}>"
        value = value.replace(english, token)
        replacements.append(korean)
    return value, replacements


def restore_terms(value: str, replacements: list[str]) -> str:
    for index, korean in enumerate(replacements):
        token = f"<JDTTERM{index}>"
        if token not in value:
            raise ValueError(f"가이드 용어 보호 토큰이 사라졌습니다: {token}:{value}")
        value = value.replace(token, korean)
    return value


def candidate() -> dict[str, object]:
    """가이드의 모든 표시 문자열에 보호 처리한 번역 후보를 만든다."""
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    names = item_name_map()
    requests: dict[str, tuple[str, list[str]]] = {}
    locations = 0
    for path in sorted(ENGLISH_ROOT.rglob("*.json")):
        for _, source in visible_locations(load_json(path)):
            locations += 1
            if (
                source in CATEGORY_OVERRIDES
                or source in SOURCE_OVERRIDES
                or source in names
                or isinstance(cache.get(source), str)
            ):
                continue
            requests[source] = protect_terms(source, names)
    failures: list[str] = []
    if requests:
        completed = 0
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(ars_family.request_translation, masked): (source, terms)
                for source, (masked, terms) in sorted(requests.items())
            }
            for future in as_completed(futures):
                source, terms = futures[future]
                try:
                    cache[source] = restore_terms(future.result(), terms)
                    completed += 1
                    if completed % 20 == 0:
                        write_json(CACHE_FILE, cache)
                except Exception as exc:  # pragma: no cover - 외부 번역 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("가이드 후보 생성 실패:\n" + "\n".join(failures))
    report = {
        "visible_locations": locations,
        "unique_requests": len(requests),
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


def review_text(source: str, candidate_value: str, names: dict[str, str]) -> str:
    if source in CATEGORY_OVERRIDES:
        return CATEGORY_OVERRIDES[source]
    if source in SOURCE_OVERRIDES:
        return SOURCE_OVERRIDES[source]
    if source in names:
        return names[source]
    tags: list[str] = []

    def mask_tag(match: re.Match[str]) -> str:
        tags.append(match.group(0))
        return f"ZXQGUIDETAG{len(tags) - 1}QXZ"

    value = PATCHOULI_TAG.sub(mask_tag, candidate_value)
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    for old, new in sorted(names.items(), key=lambda row: len(row[0]), reverse=True):
        value = value.replace(old, new)
    value = value.replace("해야합니다", "해야 합니다")
    value = value.replace("할 수있는", "할 수 있는")
    value = value.replace("티어 업", "티어 상승")
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    for index, tag in enumerate(tags):
        value = value.replace(f"ZXQGUIDETAG{index}QXZ", tag)
    return value


def build() -> dict[str, object]:
    """검수 규칙을 적용해 한국어 가이드 165파일과 책 표지를 만든다."""
    cache = load_json(CACHE_FILE)
    names = item_name_map()
    files = 0
    locations = 0
    changed = 0
    for source_path in sorted(ENGLISH_ROOT.rglob("*.json")):
        relative = source_path.relative_to(ENGLISH_ROOT)
        data = load_json(source_path)
        for field_path, source in visible_locations(data):
            file_override = FILE_SOURCE_OVERRIDES.get((relative.as_posix(), source))
            candidate_value = file_override or CATEGORY_OVERRIDES.get(
                source,
                SOURCE_OVERRIDES.get(source, names.get(source, cache.get(source))),
            )
            if not isinstance(candidate_value, str):
                raise KeyError(f"가이드 후보 누락: {relative}:{field_path}:{source}")
            translated = (
                file_override
                if file_override is not None
                else review_text(source, candidate_value, names)
            )
            set_path(data, field_path, translated)
            locations += 1
            changed += int(source != translated)
        write_json(KOREAN_ROOT / relative, data)
        write_json(OUTPUT_ROOT / relative, data)
        files += 1

    book = load_json(WORK_ROOT / "book_en_us.json")
    book["name"] = "Just Dire Things 가이드"
    book["landing_text"] = (
        "Just Dire Things의 기계, 도구, 방어구, 구 확산을 설명합니다!"
    )
    write_json(BOOK_OUTPUT, book)
    report = {
        "files": files,
        "visible_locations": locations,
        "changed": changed,
        "book_override": BOOK_OUTPUT.relative_to(PROJECT_ROOT).as_posix(),
        "review_status": "all_guide_strings_reviewed_from_current_english",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    untranslated: list[str] = []
    latin_residuals: list[str] = []
    files = 0
    locations = 0
    for source_path in sorted(ENGLISH_ROOT.rglob("*.json")):
        relative = source_path.relative_to(ENGLISH_ROOT)
        target_path = KOREAN_ROOT / relative
        output_path = OUTPUT_ROOT / relative
        if not target_path.is_file() or not output_path.is_file():
            errors.append(f"가이드 출력 누락: {relative.as_posix()}")
            continue
        source = load_json(source_path)
        target = load_json(target_path)
        if source.keys() != target.keys():
            errors.append(f"가이드 최상위 구조 불일치: {relative.as_posix()}")
        if target != load_json(output_path):
            errors.append(f"가이드 누적 출력 불일치: {relative.as_posix()}")
        target_locations = dict(visible_locations(target))
        for field_path, source_value in visible_locations(source):
            locations += 1
            target_value = target_locations.get(field_path)
            label = f"{relative.as_posix()}:{'.'.join(map(str, field_path))}"
            if not isinstance(target_value, str):
                errors.append(f"가이드 표시 값 누락: {label}")
                continue
            if PATCHOULI_TAG.findall(source_value) != PATCHOULI_TAG.findall(
                target_value
            ):
                errors.append(f"Patchouli 태그 불일치: {label}")
            if source_value == target_value and LATIN_WORD.search(source_value):
                untranslated.append(label)
            residue = target_value
            for allowed in ALLOWED_LATIN:
                residue = residue.replace(allowed, "")
            residue = PATCHOULI_TAG.sub("", residue)
            residue = re.sub(r"#[A-Za-z0-9_.-]+#", "", residue)
            residue = re.sub(r"https?://\S+", "", residue)
            if LATIN_WORD.search(residue):
                latin_residuals.append(f"{label}:{target_value}")
        files += 1

    advancements = json.loads(
        (WORK_ROOT / "advancements.json").read_text(encoding="utf-8")
    )
    displayed = [row for row in advancements if row.get("has_display")]
    if displayed:
        errors.append(f"literal 발전 과제 표시 발견: {len(displayed)}")
    scope = load_json(WORK_ROOT / "scope.json")
    visible_literals = scope.get("kubejs_visible_literals", [])
    if visible_literals:
        errors.append(f"KubeJS literal 표시 문구 발견: {len(visible_literals)}")
    if untranslated:
        errors.append(f"미번역 가이드 문구: {untranslated[:20]}")
    if latin_residuals:
        errors.append(f"가이드 영문 잔존: {latin_residuals[:30]}")
    if not BOOK_OUTPUT.is_file():
        errors.append("책 표지 덮어쓰기 누락")
    report = {
        "files": files,
        "visible_locations": locations,
        "untranslated": len(untranslated),
        "latin_residuals": len(latin_residuals),
        "advancements": len(advancements),
        "advancements_with_display": len(displayed),
        "kubejs_reference_files": len(scope.get("kubejs_reference_files", [])),
        "kubejs_visible_literals": len(visible_literals),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "validation.json", report)
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "candidate", "build", "verify"))
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare()
        status = 0
    elif args.command == "candidate":
        result = candidate()
        status = 0
    elif args.command == "build":
        result = build()
        status = 0
    else:
        result, status = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
