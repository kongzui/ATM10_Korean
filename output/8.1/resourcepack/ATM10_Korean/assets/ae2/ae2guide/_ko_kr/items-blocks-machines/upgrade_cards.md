---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 업그레이드 카드
  icon: speed_card
  position: 410
categories:
- tools
item_ids:
- ae2:basic_card
- ae2:advanced_card
- ae2:redstone_card
- ae2:capacity_card
- ae2:void_card
- ae2:fuzzy_card
- ae2:speed_card
- ae2:inverter_card
- ae2:crafting_card
- ae2:equal_distribution_card
- ae2:energy_card
---

# 업그레이드 카드

<Row>
  <ItemImage id="redstone_card" scale="2" />

  <ItemImage id="capacity_card" scale="2" />

  <ItemImage id="void_card" scale="2" />

  <ItemImage id="fuzzy_card" scale="2" />

  <ItemImage id="speed_card" scale="2" />

  <ItemImage id="inverter_card" scale="2" />

  <ItemImage id="crafting_card" scale="2" />

  <ItemImage id="equal_distribution_card" scale="2" />

  <ItemImage id="energy_card" scale="2" />
</Row>

업그레이드 카드는 AE2 [장치](../ae2-mechanics/devices.md)와 기계의 작동 방식을 바꿉니다. 속도를 높이고 필터 용량을 늘리며
레드스톤 제어를 활성화하는 등의 기능이 있습니다.

## 카드 부품

<Row>
  <ItemImage id="basic_card" scale="2" />

  <ItemImage id="advanced_card" scale="2" />
</Row>

카드는 기본 또는 고급 카드 기반으로 제작합니다.

<Row>
  <RecipeFor id="basic_card" />

  <RecipeFor id="advanced_card" />
</Row>

## 레드스톤 카드

<ItemImage id="redstone_card" scale="2" />

레드스톤 카드는 레드스톤 제어를 추가하며, 장치 GUI에 여러 레드스톤 조건을 전환하는 버튼을 만듭니다.

<RecipeFor id="redstone_card" />

## 용량 카드

<ItemImage id="capacity_card" scale="2" />

용량 카드는 반입·반출·저장 버스와 형성 평면의 필터 슬롯 수를 늘립니다.

<RecipeFor id="capacity_card" />

## 초과분 파괴 카드

<ItemImage id="void_card" scale="2" />

초과분 파괴 카드는 <ItemLink id="cell_workbench" />에서 [저장 셀](storage_cells.md)에 장착할 수 있으며,
셀이 가득 차면 들어오는 아이템을 삭제합니다. (반드시 셀의 [파티션](cell_workbench.md)을 설정하세요!) 균등 분배 카드와 함께 사용하면
다른 아이템의 구역이 비어 있어도 해당 아이템의 구역이 가득 찼을 때 그 아이템을 삭제합니다.

<RecipeFor id="void_card" />

## 퍼지 카드

<ItemImage id="fuzzy_card" scale="2" />

퍼지 카드는 필터가 있는 장치와 도구가 내구도 수준으로 필터링하거나 아이템 NBT를 무시하게 합니다.
내구도와 마법 부여에 상관없이 모든 철 도끼를 반출하거나, 완전히 수리된 검은 제외하고 손상된 다이아몬드 검만 반출할 수 있습니다.

아래는 퍼지 내구도 비교 모드가 작동하는 예입니다. 왼쪽은 버스 설정이고 위쪽은 비교 대상 아이템입니다.

| 25%                    | 10% 손상된 곡괭이 | 30% 손상된 곡괭이 | 80% 손상된 곡괭이 | 완전히 수리된 곡괭이 |
| ---------------------- | ------------------- | ------------------- | ------------------- | ------------------- |
| 거의 부서진 곡괭이     | ✅                   | \*\*\*\*            | \*\*\*\*            | \*\*\*\*            |
| 완전히 수리된 곡괭이   | \*\*\*\*            | ✅                   | ✅                   | ✅                   |

| 50%                    | 10% 손상된 곡괭이 | 30% 손상된 곡괭이 | 80% 손상된 곡괭이 | 완전히 수리된 곡괭이 |
| ---------------------- | ------------------- | ------------------- | ------------------- | ------------------- |
| 거의 부서진 곡괭이     | ✅                   | ✅                   | \*\*\*\*            | \*\*\*\*            |
| 완전히 수리된 곡괭이   | \*\*\*\*            | \*\*\*\*            | ✅                   | ✅                   |

| 75%                    | 10% 손상된 곡괭이 | 30% 손상된 곡괭이 | 80% 손상된 곡괭이 | 완전히 수리된 곡괭이 |
| ---------------------- | ------------------- | ------------------- | ------------------- | ------------------- |
| 거의 부서진 곡괭이     | ✅                   | ✅                   | \*\*\*\*            | \*\*\*\*            |
| 완전히 수리된 곡괭이   | \*\*\*\*            |                     | ✅                   | ✅                   |

| 99%                    | 10% 손상된 곡괭이 | 30% 손상된 곡괭이 | 80% 손상된 곡괭이 | 완전히 수리된 곡괭이 |
| ---------------------- | ------------------- | ------------------- | ------------------- | ------------------- |
| 거의 부서진 곡괭이     | ✅                   | ✅                   | ✅                   | \*\*\*\*            |
| 완전히 수리된 곡괭이   | \*\*\*\*            | \*\*\*\*            | \*\*\*\*            | ✅                   |

| 무시                   | 10% 손상된 곡괭이 | 30% 손상된 곡괭이 | 80% 손상된 곡괭이 | 완전히 수리된 곡괭이 |
| ---------------------- | ------------------- | ------------------- | ------------------- | ------------------- |
| 거의 부서진 곡괭이     | ✅                   | ✅                   | ✅                   | **✅**               |
| 완전히 수리된 곡괭이   | **✅**               | **✅**               | **✅**               | ✅                   |

<RecipeFor id="fuzzy_card" />

## 가속 카드

<ItemImage id="speed_card" scale="2" />

가속 카드는 장치를 더 빠르게 만듭니다. 반입·반출 버스가 작업당 더 많은 아이템을 옮기고,
각인기와 조립기가 더 빠르게 작동합니다.

<RecipeFor id="speed_card" />

## 반전 카드

<ItemImage id="inverter_card" scale="2" />

반전 카드는 장치와 도구의 필터를 허용 목록에서 차단 목록으로 바꿉니다.

<RecipeFor id="inverter_card" />

## 제작 카드

<ItemImage id="crafting_card" scale="2" />

제작 카드는 장치가 필요한 아이템을 얻도록 [자동 제작](../ae2-mechanics/autocrafting.md) 시스템에 제작 요청을 보내게 합니다.

<RecipeFor id="crafting_card" />

## 균등 분배 카드

<ItemImage id="equal_distribution_card" scale="2" />

균등 분배 카드는 <ItemLink id="cell_workbench" />에서 [저장 셀](storage_cells.md)에 장착할 수 있습니다.
카드의 [파티션](cell_workbench.md)에 설정된 종류에 따라 셀을 같은 크기의 구역으로 나눠 한 아이템 종류가 셀 전체를 채우지 못하게 합니다.

<RecipeFor id="equal_distribution_card" />

## 에너지 카드

<ItemImage id="energy_card" scale="2" />

에너지 카드는 휴대용 터미널 같은 일부 도구의 에너지 저장량을 늘리고 <ItemLink id="vibration_chamber" />의 효율을 높입니다.

<RecipeFor id="energy_card" />
