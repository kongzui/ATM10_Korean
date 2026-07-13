---
navigation:
  title: MEGA 저장소
  icon: item_storage_cell_256m
  parent: index.md
  position: 010
categories:
  - megacells
item_ids:
  - cell_component_1m
  - cell_component_4m
  - cell_component_16m
  - cell_component_64m
  - cell_component_256m
  - mega_item_cell_housing
  - mega_fluid_cell_housing
  - mega_chemical_cell_housing
  - mega_source_cell_housing
  - mega_mana_cell_housing
  - mega_experience_cell_housing
  - item_storage_cell_1m
  - item_storage_cell_4m
  - item_storage_cell_16m
  - item_storage_cell_64m
  - item_storage_cell_256m
  - fluid_storage_cell_1m
  - fluid_storage_cell_4m
  - fluid_storage_cell_16m
  - fluid_storage_cell_64m
  - fluid_storage_cell_256m
  - chemical_storage_cell_1m
  - chemical_storage_cell_4m
  - chemical_storage_cell_16m
  - chemical_storage_cell_64m
  - chemical_storage_cell_256m
  - source_storage_cell_1m
  - source_storage_cell_4m
  - source_storage_cell_16m
  - source_storage_cell_64m
  - source_storage_cell_256m
  - mana_storage_cell_1m
  - mana_storage_cell_4m
  - mana_storage_cell_16m
  - mana_storage_cell_64m
  - mana_storage_cell_256m
  - experience_storage_cell_1m
  - experience_storage_cell_4m
  - experience_storage_cell_16m
  - experience_storage_cell_64m
  - experience_storage_cell_256m
  - portable_item_cell_1m
  - portable_item_cell_4m
  - portable_item_cell_16m
  - portable_item_cell_64m
  - portable_item_cell_256m
  - portable_fluid_cell_1m
  - portable_fluid_cell_4m
  - portable_fluid_cell_16m
  - portable_fluid_cell_64m
  - portable_fluid_cell_256m
  - portable_chemical_cell_1m
  - portable_chemical_cell_4m
  - portable_chemical_cell_16m
  - portable_chemical_cell_64m
  - portable_chemical_cell_256m
  - portable_source_cell_1m
  - portable_source_cell_4m
  - portable_source_cell_16m
  - portable_source_cell_64m
  - portable_source_cell_256m
  - portable_mana_cell_1m
  - portable_mana_cell_4m
  - portable_mana_cell_16m
  - portable_mana_cell_64m
  - portable_mana_cell_256m
  - portable_experience_cell_1m
  - portable_experience_cell_4m
  - portable_experience_cell_16m
  - portable_experience_cell_64m
  - portable_experience_cell_256m
  - sky_bronze_ingot
  - sky_bronze_block
  - sky_osmium_ingot
  - sky_osmium_block
---

# MEGA Cells: 저장소

<GameScene zoom="8" background="transparent">
  <ImportStructure src="assets/assemblies/drive_cells.snbt" />
  <IsometricCamera yaw="195" pitch="10" />
</GameScene>

## MEGA [저장 셀](ae2:items-blocks-machines/storage_cells.md)

<Row>
  <ItemImage id="mega_item_cell_housing" scale="4" />
  <ItemImage id="item_storage_cell_1m" scale="4" />
  <ItemImage id="item_storage_cell_4m" scale="4" />
  <ItemImage id="item_storage_cell_16m" scale="4" />
  <ItemImage id="item_storage_cell_64m" scale="4" />
  <ItemImage id="item_storage_cell_256m" scale="4" />
</Row>

앞서 설명했듯이 <ItemLink id="megacells:accumulation_processor" />는 모든 MEGA 기반 시설을 만드는
첫 단계이며, 여기에는 더 높은 등급의 저장 셀도 포함됩니다. 이 프로세서를 사용하면
<ItemLink id="ae2:cell_component_256k" />를 **1M MEGA 저장 부품**("1024k"와 같음)부터 M 등급의 최고 단계인
**256M**까지 *훨씬 더* 확장할 수 있습니다. 이는 256k보다 용량이 *천 배 이상* 큽니다.

<RecipeFor id="cell_component_1m" />
<RecipeFor id="cell_component_4m" />
<RecipeFor id="cell_component_16m" />
<RecipeFor id="cell_component_64m" />
<RecipeFor id="cell_component_256m" />

더 뛰어난 저장소에는 당연히 더 뛰어난 하우징도 필요합니다. 하늘 강철을 더 사용하여 새로운 M 등급
부품을 담을 아이템 셀 하우징을 만들 수 있습니다.

<Row>
  <RecipeFor id="mega_item_cell_housing" />
  <Recipe id="cells/standard/item_storage_cell_1m" />
  <Recipe id="cells/standard/item_storage_cell_1m_with_housing" />
</Row>

유체와 그 밖의 대상을 위한 전용 하우징도 있습니다. 하늘석은 다른 금속과 합금을 만들 만큼 강력합니다.
예를 들어 구리와 합쳐 **하늘 청동**을 만들면 유체 셀 하우징을 제작할 수 있습니다. 이 가이드에 나오지
않더라도, 생각할 수 있는 여러 저장 대상은 MEGA의 전용 셀과 하우징으로 지원될 수 있습니다.

<Row>
  <ItemImage id="sky_bronze_ingot" scale="4" />
  <ItemImage id="mega_fluid_cell_housing" scale="4" />
  <ItemImage id="fluid_storage_cell_1m" scale="4" />
  <ItemImage id="fluid_storage_cell_4m" scale="4" />
  <ItemImage id="fluid_storage_cell_16m" scale="4" />
  <ItemImage id="fluid_storage_cell_64m" scale="4" />
  <ItemImage id="fluid_storage_cell_256m" scale="4" />
</Row>

<Row>
  <Recipe id="transform/sky_bronze_ingot" />
  <RecipeFor id="mega_fluid_cell_housing" />
</Row>

## MEGA [휴대용 셀](ae2:items-blocks-machines/storage_cells.md#portable-item-storage)

MEGA도 AE2처럼 모든 셀의 휴대용 버전을 제공하지만, 늘어난 용량만큼 훨씬 많은 전력이 필요합니다.
따라서 <ItemLink id="ae2:dense_energy_cell" />을 사용하여 제작하며, 일반
<ItemLink id="ae2:energy_cell" />을 사용하지 않는다는 점에 주의하세요.

이 휴대용 셀은 일반 ME 휴대용 셀처럼 모든 [업그레이드](ae2:items-blocks-machines/upgrade_cards.md)를
지원합니다. 하지만 더 큰 배터리와 높은 전력 소모량 때문에 일반 <ItemLink id="ae2:energy_card" />만으로는
충분하지 않습니다. 이때는 <ItemLink id="megacells:greater_energy_card" />만 사용할 수 있습니다.

<Row>
  <RecipeFor id="portable_item_cell_1m" />
</Row>
