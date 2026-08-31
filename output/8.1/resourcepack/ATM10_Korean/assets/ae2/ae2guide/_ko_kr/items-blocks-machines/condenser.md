---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 물질 응축기
  icon: condenser
  position: 310
categories:
- machines
item_ids:
- ae2:condenser
---

# 물질 응축기

<BlockImage id="condenser" scale="8" />

물질 응축기는 쓰레기통으로 사용하거나 <ItemLink id="matter_ball" />과 [특이점](singularities.md)을 만드는 데 사용할 수 있습니다.
저장 셀이 저장할 수 있는 모든 아이템과 유체 등을 받아들입니다.

## 설정 및 조합법

*   쓰레기통 모드에서는 들어오는 모든 것을 삭제합니다.
*   물질 덩어리 모드에서는 넣은 재료로 <ItemLink id="matter_ball" />을 만듭니다.
    이 모드에서는 응축기의 위쪽 슬롯에 저장 부품을 넣어야 합니다. 물질 덩어리 하나에는 아이템 또는 양동이 256개가 필요하므로
    8,192비트 용량을 제공하는 <ItemLink id="cell_component_1k" />면 충분하고도 남습니다.
*   물질 특이점 모드에서는 넣은 재료로 [특이점](singularities.md)을 만듭니다.
    이 모드에서도 응축기의 위쪽 슬롯에 저장 부품을 넣어야 합니다. 특이점 하나에는 아이템 또는 양동이 256,000개가 필요하므로
    524,288비트 용량을 제공하는 <ItemLink id="cell_component_64k" />면 충분하고도 남습니다.

자원을 생산하는 뒤의 두 모드에서는 물질 응축기가 *막힐 수 있습니다.* 에너지 버퍼와 출력 아이템 버퍼가 모두 완전히 차면
더 이상 입력을 받지 않습니다.

## 조합법

<RecipeFor id="condenser" />
