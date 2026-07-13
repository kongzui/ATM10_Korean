---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 저장 셀
  icon: item_storage_cell_1k
  position: 410
categories:
- tools
item_ids:
- ae2:item_cell_housing
- ae2:fluid_cell_housing
- ae2:cell_component_1k
- ae2:cell_component_4k
- ae2:cell_component_16k
- ae2:cell_component_64k
- ae2:cell_component_256k
- ae2:item_storage_cell_1k
- ae2:item_storage_cell_4k
- ae2:item_storage_cell_16k
- ae2:item_storage_cell_64k
- ae2:item_storage_cell_256k
- ae2:fluid_storage_cell_1k
- ae2:fluid_storage_cell_4k
- ae2:fluid_storage_cell_16k
- ae2:fluid_storage_cell_64k
- ae2:fluid_storage_cell_256k
---

# 저장 셀

<Column>
  <Row>
    <ItemImage id="item_storage_cell_1k" scale="4" />

    <ItemImage id="item_storage_cell_4k" scale="4" />

    <ItemImage id="item_storage_cell_16k" scale="4" />

    <ItemImage id="item_storage_cell_64k" scale="4" />

    <ItemImage id="item_storage_cell_256k" scale="4" />
  </Row>

  <Row>
    <ItemImage id="fluid_storage_cell_1k" scale="4" />

    <ItemImage id="fluid_storage_cell_4k" scale="4" />

    <ItemImage id="fluid_storage_cell_16k" scale="4" />

    <ItemImage id="fluid_storage_cell_64k" scale="4" />

    <ItemImage id="fluid_storage_cell_256k" scale="4" />
  </Row>
</Column>

저장 셀은 Applied Energistics의 주요 저장 방식 중 하나입니다. <ItemLink id="drive" />나
<ItemLink id="chest" />에 넣어 사용합니다.

바이트와 유형에 따른 용량 설명은 [바이트와 유형](../ae2-mechanics/bytes-and-types.md)을 참고하세요.

셀이 비어 있을 때 손에 들고 Shift+우클릭하면 하우징에서 저장 부품을 분리할 수 있습니다.

<Row>
    <Recipe id="upgrade/item_storage_cell_1k_to_4k" />

    제작 격자에서 저장 셀과 상위 등급 저장 부품을 조합하면 셀을 상위 등급으로 업그레이드할 수 있습니다. 내용물은 유지되고 하위 등급 부품은 반환됩니다.
</Row>

## 유형 수에 따른 저장 용량

[유형의 선불 비용](../ae2-mechanics/bytes-and-types.md) 때문에 한 유형만 저장하는 셀은 63개 유형을 모두 사용하는 셀보다 2배 많이 저장할 수 있습니다.

| 셀                                       | 1개 유형 사용 시 셀의 총용량 | 63개 유형 사용 시 셀의 총용량 |
| ---------------------------------------- | ----------------------------------------: | ------------------------------------------: |
| <ItemLink id="item_storage_cell_1k" />   |                                     8,128 |                                       4,160 |
| <ItemLink id="item_storage_cell_4k" />   |                                    32,512 |                                      16,640 |
| <ItemLink id="item_storage_cell_16k" />  |                                   130,048 |                                      66,560 |
| <ItemLink id="item_storage_cell_64k" />  |                                   520,192 |                                     266,240 |
| <ItemLink id="item_storage_cell_256k" /> |                                 2,080,768 |                                   1,064,960 |


## 파티션 설정

<ItemLink id="storage_bus" />의 필터와 비슷하게 셀이 특정 아이템만 받도록 설정할 수 있습니다.
<ItemLink id="cell_workbench" />에서 설정합니다.

실제로 가지고 있지 않은 아이템도 JEI/REI에서 슬롯으로 끌어올 수 있습니다.

## 업그레이드

저장 셀은 <ItemLink id="cell_workbench" />에서 다음 [업그레이드](upgrade_cards.md)를 장착할 수 있습니다.

*   <ItemLink id="fuzzy_card" />는 피해 수준으로 셀 파티션을 설정하거나 아이템 NBT를 무시하게 합니다(유체 셀에는 사용할 수 없음).
*   <ItemLink id="inverter_card" />는 필터를 허용 목록에서 차단 목록으로 바꿉니다.
*   <ItemLink id="equal_distribution_card" />는 각 유형에 같은 양의 셀 바이트 공간을 할당해 한 유형이 셀 전체를 채우지 못하게 합니다.
*   <ItemLink id="void_card" />는 셀이 가득 찼을 때 들어오는 아이템을 삭제합니다. 균등 분배 카드가 있으면 해당 유형에
    할당된 공간이 가득 찼을 때 삭제하므로 농장이 막히는 일을 방지하는 데 유용합니다. 반드시 파티션을 주의해서 설정하세요!
*   휴대용 셀에는 <ItemLink id="energy_card" />를 장착해 배터리 용량을 늘릴 수 있습니다.

## 색상 입히기

휴대용 아이템 및 유체 셀은 가죽 갑옷처럼 염료와 함께 제작해 색을 입힐 수 있습니다.

# 하우징

셀은 저장 부품과 하우징을 조합하거나, 저장 부품 주위에 하우징 조합법의 재료를 배치해 만들 수 있습니다.

<Row>
  <Recipe id="network/cells/item_storage_cell_1k" />

  <Recipe id="network/cells/item_storage_cell_1k_storage" />
</Row>

하우징 자체는 다음과 같이 제작합니다.

<Row>
  <RecipeFor id="item_cell_housing" />

  <RecipeFor id="fluid_cell_housing" />
</Row>

# 저장 부품

저장 부품은 모든 AE2 셀의 핵심이며 셀의 용량을 결정합니다. 등급이 오를 때마다 용량이 4배가 되고
이전 등급 부품 3개가 필요합니다.

<Column>
  <Row>
    <RecipeFor id="cell_component_1k" />

    <RecipeFor id="cell_component_4k" />

    <RecipeFor id="cell_component_16k" />
  </Row>

  <Row>
    <RecipeFor id="cell_component_64k" />

    <RecipeFor id="cell_component_256k" />
  </Row>
</Column>

# 아이템 저장 셀

아이템 저장 셀은 서로 다른 아이템 유형을 최대 63개까지 저장하며, 모든 표준 용량으로 제공됩니다.

<Column>
  <Row>
    <Recipe id="network/cells/item_storage_cell_1k_storage" />

    <Recipe id="network/cells/item_storage_cell_4k_storage" />

    <Recipe id="network/cells/item_storage_cell_16k_storage" />
  </Row>

  <Row>
    <Recipe id="network/cells/item_storage_cell_64k_storage" />

    <Recipe id="network/cells/item_storage_cell_256k_storage" />
  </Row>
</Column>

## 휴대용 아이템 저장소

주머니 속의 작은 <ItemLink id="chest" /> 또는 배낭처럼 작동합니다. <ItemLink id="charger" />에서 충전할 수 있습니다.

표준 저장 셀과 달리 바이트 용량이 늘어날수록 유형 용량이 *줄어들며*, 총 바이트 용량은 절반입니다.

모든 셀이 장착할 수 있는 업그레이드 카드 외에 <ItemLink id="energy_card" />도 장착해 내부 배터리를 늘릴 수 있습니다.

<Column>
  <Row>
    <RecipeFor id="portable_item_cell_1k" />

    <RecipeFor id="portable_item_cell_4k" />

    <RecipeFor id="portable_item_cell_16k" />
  </Row>

  <Row>
    <RecipeFor id="portable_item_cell_64k" />

    <RecipeFor id="portable_item_cell_256k" />
  </Row>
</Column>

# 유체 저장 셀

유체 저장 셀은 서로 다른 유체 유형을 최대 5개까지 저장하며, 모든 표준 용량으로 제공됩니다.

<Column>
  <Row>
    <Recipe id="network/cells/fluid_storage_cell_1k_storage" />

    <Recipe id="network/cells/fluid_storage_cell_4k_storage" />

    <Recipe id="network/cells/fluid_storage_cell_16k_storage" />
  </Row>

  <Row>
    <Recipe id="network/cells/fluid_storage_cell_64k_storage" />

    <Recipe id="network/cells/fluid_storage_cell_256k_storage" />
  </Row>
</Column>

## 휴대용 유체 저장소

주머니 속의 작은 <ItemLink id="chest" /> 또는 배낭처럼 작동합니다. <ItemLink id="charger" />에서 충전할 수 있습니다.

표준 저장 셀과 달리 바이트 용량이 늘어날수록 유형 용량이 *줄어들며*, 총 바이트 용량은 절반입니다.

모든 셀이 장착할 수 있는 업그레이드 카드 외에 <ItemLink id="energy_card" />도 장착해 내부 배터리를 늘릴 수 있습니다.

<Column>
  <Row>
    <RecipeFor id="portable_fluid_cell_1k" />

    <RecipeFor id="portable_fluid_cell_4k" />

    <RecipeFor id="portable_fluid_cell_16k" />
  </Row>

  <Row>
    <RecipeFor id="portable_fluid_cell_64k" />

    <RecipeFor id="portable_fluid_cell_256k" />
  </Row>
</Column>

# 크리에이티브 저장 셀

<Row>
  <ItemImage id="creative_storage_cell" scale="2" />
</Row>

크리에이티브 셀은 **무한한 저장 공간을 제공하지 않습니다.** 대신 [파티션](cell_workbench.md)에 설정한
아이템이나 유체의 무한한 공급원이자 소멸 지점으로 작동합니다.
