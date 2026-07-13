---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: ME 레벨 방출기
  icon: level_emitter
  position: 220
categories:
- devices
item_ids:
- ae2:level_emitter
- ae2:energy_level_emitter
---

# ME 레벨 방출기

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../assets/blocks/level_emitter.snbt" />
</GameScene>

ME 레벨 방출기는 [네트워크 저장소](../ae2-mechanics/import-export-storage.md)에 있는 아이템 수량에 따라 레드스톤 신호를 출력합니다.

네트워크에 저장된 [에너지](../ae2-mechanics/energy.md) 양에 따라 레드스톤 신호를 출력하는 변형도 있습니다.

실제로 가지고 있지 않은 아이템이나 유체도 JEI/REI에서 슬롯으로 끌어올 수 있습니다.

양동이나 유체 탱크 같은 유체 용기를 들고 우클릭하면 용기 아이템 대신 그 안의 유체를 필터로 설정합니다.

[케이블 부품](../ae2-mechanics/cable-subparts.md)으로 설치됩니다.

다른 [장치](../ae2-mechanics/devices.md)와 달리 레벨 방출기에는 [채널](../ae2-mechanics/channels.md)이 *필요하지 않습니다.*

## 설정

*   "크거나 같음" 또는 "미만" 모드로 설정할 수 있습니다.
*   <ItemLink id="crafting_card" />를 장착하면 "아이템 제작 중 레드스톤 출력" 또는
    "아이템 제작을 위해 레드스톤 출력"으로 설정할 수 있습니다.

## 업그레이드

레벨 방출기는 다음 [업그레이드](upgrade_cards.md)를 지원합니다.

*   <ItemLink id="fuzzy_card" />는 내구도 수준으로 필터링하거나 아이템 NBT를 무시하게 합니다.
*   <ItemLink id="crafting_card" />는 제작 기능을 활성화합니다.

## 제작 기능

<ItemLink id="crafting_card" />를 장착하면 방출기가 제작 모드로 전환됩니다.

두 가지 옵션이 활성화됩니다.

첫 번째 옵션인 "아이템 제작 중 레드스톤 출력"은 [자동 제작](../ae2-mechanics/autocrafting.md)이 <ItemLink id="pattern_provider" />를 통해
특정 아이템을 제작하는 동안 방출기가 레드스톤 신호를 출력하게 합니다. 전력을 많이 쓰는 특정 자동화 설비를
실제로 사용할 때만 켜는 데 유용합니다.

두 번째 옵션인 "아이템 제작을 위해 레드스톤 출력"은 무한 농장이나 결과물이 확정되지 않고 확률적으로 생성되는 자동화 설비에 매우 유용합니다.
이 설정은 방출기의 필터 슬롯에 있는 아이템에 대해 가상 [패턴](patterns.md)을 만들어 [자동 제작](../ae2-mechanics/autocrafting.md)이 사용하게 합니다.
(올바르게 작동하려면 <ItemLink id="pattern_provider" />에 같은 아이템의 실제 패턴이 **없어야 합니다.**)

이 "패턴"은 재료를 정의하지도, 신경 쓰지도 않습니다. 단지 "이 레벨 방출기가 레드스톤을 출력하면 가까운 미래든 먼 미래든
ME 시스템이 이 아이템을 받는다"고 지정합니다. 보통 입력 재료가 필요 없는 무한 농장을 켜고 끄거나,
조약돌을 복제하는 기계의 "조약돌 1개 = 조약돌 2개"처럼 표준 자동 제작이 이해하지 못하는
[재귀 조합법 처리 시스템](../example-setups/recursive-crafting-setup.md)을 활성화할 때 사용합니다.

## 조합법

<RecipeFor id="level_emitter" />

<RecipeFor id="energy_level_emitter" />
