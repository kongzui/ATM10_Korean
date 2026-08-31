---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 각인기
  icon: inscriber
  position: 310
categories:
- machines
item_ids:
- ae2:inscriber
---

# 각인기

<BlockImage id="inscriber" scale="8" />

각인기는 회로와 [프로세서](processors.md)를 [프레스](presses.md)로 인쇄하고 여러 아이템을 가루로 분쇄합니다.
AE2 전력(AE)과 Fabric/Forge Energy(E/FE)를 모두 받습니다. 면별 입출력을 활성화하면 아이템을 넣는 면에 따라
서로 다른 인벤토리 슬롯으로 들어갑니다. 이를 쉽게 구성하도록 <ItemLink id="certus_quartz_wrench" />로 회전할 수 있습니다.
제작 결과물을 인접한 인벤토리로 밀어내도록 설정할 수도 있습니다.

입력 버퍼 크기를 조절할 수 있습니다. 예를 들어 인벤토리 하나에서 많은 각인기로 재료를 공급한다면 작은 버퍼를 사용하세요.
첫 번째 각인기만 64개로 가득 차고 나머지는 비는 대신 재료가 여러 각인기에 더 알맞게 분배됩니다.

회로 프레스 4종은 [프로세서](processors.md)를 제작하는 데 사용됩니다.

<Row>
  <ItemImage id="silicon_press" scale="4" />

  <ItemImage id="logic_processor_press" scale="4" />

  <ItemImage id="calculation_processor_press" scale="4" />

  <ItemImage id="engineering_processor_press" scale="4" />
</Row>

이름 프레스는 모루처럼 블록에 이름을 붙일 수 있어 <ItemLink id="pattern_access_terminal" />에서 대상을 구분할 때 유용합니다.

<ItemImage id="name_press" scale="4" />

## 설정

* 각인기는 아래 설명처럼 면별 입출력을 사용하거나, 어느 면에서든 모든 슬롯에 입력을 허용하고 내부 필터가 목적지를 정하게 할 수 있습니다.
    면별 입출력을 사용하지 않을 때는 위·아래 슬롯에서 아이템을 추출할 수 없습니다.
* 아이템을 인접한 인벤토리로 밀어내도록 설정할 수 있습니다.
* 입력 버퍼 크기를 조절할 수 있습니다. 큰 버퍼는 수동으로 재료를 넣는 독립형 각인기에 적합하고,
작은 버퍼는 대규모 병렬 설비에 적합합니다.

## GUI와 면별 입출력

면별 입출력 모드에서는 어느 면에서 넣거나 꺼내는지에 따라 아이템의 목적지가 정해집니다.

![각인기 GUI](../assets/diagrams/inscriber_gui.png) ![각인기 면](../assets/diagrams/inscriber_sides.png)

A. **위쪽 입력**: 각인기의 위쪽 면으로 접근합니다(이 슬롯에는 아이템을 넣고 꺼낼 수 있음).

B. **가운데 입력**: 왼쪽, 오른쪽, 앞쪽, 뒤쪽 면으로 넣습니다(이 슬롯에는 아이템을 넣을 수만 있고 꺼낼 수 없음).

C. **아래쪽 입력**: 각인기의 아래쪽 면으로 접근합니다(이 슬롯에는 아이템을 넣고 꺼낼 수 있음).

D. **출력**: 왼쪽, 오른쪽, 앞쪽, 뒤쪽 면으로 꺼냅니다(이 슬롯에서는 아이템을 꺼낼 수만 있고 넣을 수 없음).

## 간단한 자동화

면별 입출력과 회전 기능을 활용하면 다음과 같이 각인기를 반자동화할 수 있습니다.

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/inscriber_hopper_automation.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

면별 입출력을 사용하지 않을 때는 파이프로 각인기에 바로 넣고 꺼내도 됩니다.

## 업그레이드

각인기는 다음 [업그레이드](upgrade_cards.md)를 지원합니다.

*   <ItemLink id="speed_card" />

## 조합법

<RecipeFor id="inscriber" />
