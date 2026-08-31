---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 케이블 덮개
  icon: facade
  icon_components:
    "ae2:facade_item": "minecraft:stone"
  position: 110
categories:
- network infrastructure
item_ids:
- ae2:facade
---

# 케이블 덮개

케이블 덮개를 사용하면 기지를 더 깔끔하게 보이게 할 수 있습니다. 두 굵기의 케이블을 모두 가릴 수 있으며,
여러 종류의 블록으로 만들 수 있습니다.

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/facades_1.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

케이블의 모든 면을 가릴 수 있지만 [부품](../ae2-mechanics/cable-subparts.md)과 케이블 연결부는 밖으로 돌출됩니다.

<GameScene zoom="6"  interactive={true}>
  <ImportStructure src="../assets/assemblies/facades_2.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

재치 있게 활용해 기지를 꾸미거나 면마다 질감이 다른 블록을 만들어 보세요.

<GameScene zoom="4" interactive={true}>
  <ImportStructure src="../assets/assemblies/facades_3.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 케이블 덮개 숨기기

어느 손이든 <a href="network_tool.md">네트워크 도구</a>를 들고 있으면 케이블 덮개가 숨겨집니다.

덮개를 먼저 제거하지 않고도 숨겨진 덮개 뒤의 블록과 상호작용할 수 있습니다.

## 조합법

원하는 질감의 블록을 <ItemLink id="cable_anchor" /> 4개 가운데에 놓으세요.

![케이블 덮개 조합법](../assets/diagrams/facade_recipe.png)
