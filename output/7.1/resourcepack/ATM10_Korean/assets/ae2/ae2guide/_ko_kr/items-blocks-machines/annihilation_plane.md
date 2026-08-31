---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 소멸 평면
  icon: annihilation_plane
  position: 210
categories:
- devices
item_ids:
- ae2:annihilation_plane
---

# 소멸 평면

<GameScene zoom="8" background="transparent">
<ImportStructure src="../assets/blocks/annihilation_plane.snbt" />
</GameScene>

소멸 평면은 블록을 부수고 아이템을 줍습니다. <ItemLink id="import_bus" />와 비슷하게 대상을
[네트워크 저장소](../ae2-mechanics/import-export-storage.md)로 보냅니다. 아이템을 주우려면 평면의 면에 닿아야 하며 범위 내 아이템을 줍지는 않습니다.

소멸 평면에는 모든 곡괭이 마법을 부여할 수 있습니다. 모드팩에서 허용한다면 몇 개에 높은 수준의 행운을 부여해
[광물 처리를 자동화](../example-setups/ore-fortuner.md)할 수 있습니다. 섬세한 손길은 예상대로 작동하고,
효율은 블록 파괴의 에너지 비용을 줄이며, 내구성은 일정 확률로 에너지를 소비하지 않게 합니다.

[케이블 부품](../ae2-mechanics/cable-subparts.md)으로 설치됩니다.

**청크 보호에서 가짜 플레이어를 반드시 허용하세요.**

## 필터링

소멸 평면은 결과 드롭이나 아이템을 네트워크에 저장할 수 있을 때만 블록을 부수거나 아이템을 줍습니다.
따라서 필터링하려면 *그 네트워크가 저장할 수 있는 대상을 제한해야 합니다.* 보통 [서브네트워크](../ae2-mechanics/subnetworks.md)에 연결합니다.
<ItemLink id="storage_bus" /> 또는 [셀](../items-blocks-machines/storage_cells.md)의 [파티션](cell_workbench.md)을 설정해 제한할 수 있습니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/annihilation_filtering.snbt" />

  <DiamondAnnotation pos="1 0.5 0.5" color="#00ff00">
        부수려는 대상의 드롭으로 필터링합니다.
  </DiamondAnnotation>

  <DiamondAnnotation pos=".5 0.5 2.5" color="#00ff00">
        부수려는 대상의 드롭으로 파티션을 설정합니다.
  </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

다시 말해 *드롭 아이템을 기준으로* 필터링합니다. 예를 들어 <ItemLink id="minecraft:amethyst_cluster" />만 부수도록 필터링하려면
섬세한 손길이 부여된 평면이 필요합니다. 그렇지 않으면 이전 성장 단계는 아무것도 떨어뜨리지 않으므로,
네트워크가 "아무것도 없음"은 항상 저장할 수 있다고 판단해 평면이 모든 단계를 부숩니다.

## 조합법

<RecipeFor id="annihilation_plane" />
