---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 에너지 수용기
  icon: energy_acceptor
  position: 110
categories:
- network infrastructure
item_ids:
- ae2:energy_acceptor
---

# 에너지 수용기

<Row gap="20">
<BlockImage id="energy_acceptor" scale="8" /> 

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../assets/blocks/cable_energy_acceptor.snbt" />
</GameScene>
</Row>

에너지 수용기는 다른 기술 모드의 일반적인 에너지 형식을 AE2 내부 [에너지](../ae2-mechanics/energy.md)인 AE로 변환합니다.
<ItemLink id="controller" />도 변환할 수 있지만 제어기 면은 귀중하므로 에너지 수용기를 따로 사용하는 편이 나을 때가 많습니다.

Forge Energy와 Tech Reborn Energy의 변환 비율은 다음과 같습니다.

*   Forge 기준: 2 FE = 1 AE
*   Fabric 기준: 1 E = 2 AE

변환 속도는 네트워크가 저장할 수 있는 AE 양에 전적으로 좌우됩니다. 이유는 [이 페이지](../ae2-mechanics/energy.md)에 설명되어 있습니다.

## 변형

에너지 수용기는 일반형과 납작한 [부품](../ae2-mechanics/cable-subparts.md)형의 두 가지 변형이 있어 설비를 더 작게 구성할 수 있습니다.

제작 격자에서 일반형과 납작한 형태를 서로 바꿀 수 있습니다.

## 조합법

<RecipeFor id="energy_acceptor" />

<RecipeFor id="cable_energy_acceptor" />
