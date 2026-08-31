---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 공간 저장 셀
  icon: spatial_storage_cell_128
  position: 410
categories:
- tools
item_ids:
- ae2:spatial_storage_cell_2
- ae2:spatial_storage_cell_16
- ae2:spatial_storage_cell_128
- ae2:spatial_cell_component_2
- ae2:spatial_cell_component_16
- ae2:spatial_cell_component_128
---

# 공간 저장 셀

  <Row>
    <ItemImage id="spatial_storage_cell_2" scale="4" />

    <ItemImage id="spatial_storage_cell_16" scale="4" />

    <ItemImage id="spatial_storage_cell_128" scale="4" />
  </Row>

공간 저장 셀은 [물리적인 공간을 저장](../ae2-mechanics/spatial-io.md)하는 데 사용됩니다.
<ItemLink id="spatial_io_port" />에서 사용합니다.

[저장 셀](../items-blocks-machines/storage_cells.md)과 달리 공간 셀은 다시 포맷할 수 없습니다.

다시 강조하지만 **한 번 사용한 공간 셀은 초기화하거나 다시 포맷하거나 크기를 바꿀 수 없습니다.** 다른 크기가 필요하면 새 셀을 만드세요.


## 조합법

  <Row>
    <Recipe id="network/cells/spatial_storage_cell_2_cubed_storage" />

    <Recipe id="network/cells/spatial_storage_cell_16_cubed_storage" />

    <Recipe id="network/cells/spatial_storage_cell_128_cubed_storage" />
  </Row>

# 하우징

셀은 공간 부품과 하우징을 조합하거나, 공간 부품 주위에 하우징 조합법의 재료를 배치해 만들 수 있습니다.

<Row>
  <Recipe id="network/cells/spatial_storage_cell_2_cubed" />

  <Recipe id="network/cells/spatial_storage_cell_2_cubed_storage" />
</Row>

하우징 자체는 다음과 같이 제작합니다.

  <RecipeFor id="item_cell_housing" />

# 공간 부품

공간 부품은 공간 저장 셀의 핵심입니다. 등급이 오를 때마다 저장할 수 있는 공간의 각 변 길이가 8배로 늘어납니다.

  <Row>
    <RecipeFor id="spatial_cell_component_2" />

    <RecipeFor id="spatial_cell_component_16" />

    <RecipeFor id="spatial_cell_component_128" />
  </Row>
