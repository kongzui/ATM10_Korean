---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 공간 정박기
  icon: spatial_anchor
  position: 110
categories:
- network infrastructure
item_ids:
- ae2:spatial_anchor
---

# 공간 정박기

<BlockImage id="spatial_anchor" p:powered="true" scale="8"/>

AE2 네트워크의 [장치](../ae2-mechanics/devices.md)가 작동하려면 네트워크가 청크 로딩되어야 하며, 일부만 로딩되면 제대로 작동하지 않을 수 있습니다.
공간 정박기는 네트워크가 차지한 청크를 강제로 로딩해 이 문제를 해결합니다. 케이블 하나가 청크 경계를 넘어가기만 해도 새 청크를 로딩합니다.

"로딩"은 [양자 브리지](quantum_bridge.md)를 통해 전달되지만 차원 사이에는 전달되지 않습니다. 따라서 네더로 이어지는 양자 브리지가 있다면
기지의 네트워크와 네더의 네트워크에 공간 정박기를 각각 설치해야 합니다.

기본적으로 로딩한 청크의 무작위 틱도 활성화하며, AE2 설정에서 끌 수 있습니다.

필요하다면 <ItemLink id="certus_quartz_wrench" />로 회전할 수 있습니다.

## 설정

*   공간 정박기에서 에너지를 AE 또는 E/FE로 표시하는 전역 설정을 바꿀 수 있습니다.
*   로딩 중인 청크를 보여 주는 홀로그램을 월드에 표시할 수 있습니다.

## 에너지

공간 정박기는 다음 식에 따라 [에너지](../ae2-mechanics/energy.md)를 사용합니다.

e = 80 + (x\*(x+1))/2

여기서 x는 로딩 중인 청크 수입니다.

## 조합법

<RecipeFor id="spatial_anchor" />
