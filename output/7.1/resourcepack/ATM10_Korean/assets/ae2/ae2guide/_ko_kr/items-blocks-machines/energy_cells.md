---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 에너지 셀
  icon: energy_cell
  position: 110
categories:
- network infrastructure
item_ids:
- ae2:energy_cell
- ae2:dense_energy_cell
- ae2:creative_energy_cell
---

# 에너지 셀

<Row gap="20">
  <BlockImage id="energy_cell" scale="8" p:fullness="4" />

  <BlockImage id="dense_energy_cell" scale="8" p:fullness="4" />

  <BlockImage id="creative_energy_cell" scale="8" />
</Row>

에너지 셀은 네트워크의 [에너지](../ae2-mechanics/energy.md) 저장량을 늘립니다. 에너지 완충 공간이 있으면 많은 아이템을
한꺼번에 넣거나 꺼낼 때 생기는 소비량 급증을 완화합니다. 저장량이 크면 태양 전지판을 쓰는 밤처럼 에너지가 생성되지 않을 때도
네트워크를 가동하거나 [공간 저장소](../ae2-mechanics/spatial-io.md)의 막대한 순간 에너지 소비를 감당할 수 있습니다.

## 충전 표시 막대

<Row>
<BlockImage id="energy_cell" scale="4" p:fullness="0" />
<BlockImage id="energy_cell" scale="4" p:fullness="1" />
<BlockImage id="energy_cell" scale="4" p:fullness="2" />
<BlockImage id="energy_cell" scale="4" p:fullness="3" />
<BlockImage id="energy_cell" scale="4" p:fullness="4" />
</Row>

셀 측면의 막대는 저장된 에너지 양을 나타냅니다.

*   충전량이 25% 미만이면 0개
*   충전량이 25% 이상 50% 미만이면 1개
*   충전량이 50% 이상 75% 미만이면 2개
*   충전량이 75% 이상 99% 미만이면 3개
*   충전량이 99% 이상이면 4개

## 셀 종류

*   <ItemLink id="energy_cell" />은 200k AE를 저장합니다. 일반적인 네트워크 사용 중 발생하는 전력 급증을 쉽게 감당하므로
    대부분의 용도에는 하나면 충분합니다.
*   <ItemLink id="dense_energy_cell" />은 1.6M AE를 저장합니다. 저장된 전력만으로 네트워크를 가동하거나
    대규모 [공간 저장소](../ae2-mechanics/spatial-io.md) 설비의 막대한 순간 에너지 소비를 감당할 때 사용합니다.
*   <ItemLink id="creative_energy_cell" />은 시험용 크리에이티브 아이템으로, 무제한 전력을 제공합니다.

## 조합법

<Row>
  <RecipeFor id="energy_cell" />

  <RecipeFor id="dense_energy_cell" />
</Row>
