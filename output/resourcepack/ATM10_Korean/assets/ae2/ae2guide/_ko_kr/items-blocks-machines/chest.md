---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: ME 상자
  icon: chest
  position: 210
categories:
- devices
item_ids:
- ae2:chest
---

# ME 상자

<GameScene zoom="8" background="transparent">
<ImportStructure src="../assets/blocks/chest.snbt" />
</GameScene>

ME 상자는 <ItemLink id="terminal" />, <ItemLink id="drive" />, <ItemLink id="energy_acceptor" />를 갖춘 소형 네트워크처럼 작동합니다.
작은 저장 네트워크로 쓸 수 있지만 [저장 셀](../items-blocks-machines/storage_cells.md)을 하나만 넣을 수 있어 활용도는 제한적입니다.

대신 내부에 장착한 특정 저장 셀과 상호작용할 때 유용합니다. 내장 터미널에서는 장착된 셀의 아이템만 보고 이용할 수 있습니다.
일반 네트워크의 [장치](../ae2-mechanics/devices.md)는 ME 상자를 포함한 모든 [네트워크 저장소](../ae2-mechanics/import-export-storage.md)의 아이템에 접근할 수 있습니다.

서로 다른 GUI 두 개가 있으며 아이템 운반에는 면별 규칙이 적용됩니다. 위쪽 터미널과 상호작용하면 내장 터미널이 열립니다.
이 면에서는 장착된 저장 셀에 아이템을 넣을 수 있지만 꺼낼 수 없습니다. 다른 면과 상호작용하면 저장 셀 슬롯과 우선순위 설정 GUI가 열립니다.
아이템 물류 장치는 셀 슬롯이 있는 면을 통해서만 셀을 넣고 꺼낼 수 있습니다.

<ItemLink id="certus_quartz_wrench" />로 회전할 수 있습니다.

작은 AE 에너지 저장 버퍼가 있습니다. [에너지 셀](../items-blocks-machines/energy_cells.md)이 있는 네트워크에 연결하지 않았다면
아이템을 한꺼번에 너무 많이 넣거나 꺼낼 때 전력이 부족해질 수 있습니다.

터미널은 <ItemLink id="color_applicator" />로 색을 입힐 수 있습니다.

<GameScene zoom="6" background="transparent">
<ImportStructure src="../assets/assemblies/chest_color.snbt" />
<IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 설정

ME 상자에는 <ItemLink id="terminal" /> 또는 <ItemLink id="crafting_terminal" />과 같은 설정이 모두 있습니다.
다만 <ItemLink id="view_cell" />은 지원하지 않습니다.

## 셀 상태 LED

상자 안의 셀에는 상태를 보여 주는 LED가 있습니다.

| 색상   | 상태                                                                             |
| :----- | :------------------------------------------------------------------------------- |
| 초록색 | 비어 있음                                                                        |
| 파란색 | 내용물이 일부 있음                                                               |
| 주황색 | [유형](../ae2-mechanics/bytes-and-types.md)이 가득 차 새 유형을 추가할 수 없음   |
| 빨간색 | [바이트](../ae2-mechanics/bytes-and-types.md)가 가득 차 더 넣을 수 없음          |
| 검은색 | 전력이 없거나 드라이브에 [채널](../ae2-mechanics/channels.md)이 없음             |

## 우선순위

셀 슬롯 GUI 오른쪽 위의 렌치를 클릭해 우선순위를 설정할 수 있습니다.
네트워크에 들어오는 아이템은 우선순위가 가장 높은 저장소부터 향합니다. 저장소나 셀 둘의 우선순위가 같고
한쪽에 해당 아이템이 이미 있다면 다른 저장소보다 그곳을 우선합니다. [파티션](cell_workbench.md)이 설정된 셀은
같은 우선순위 그룹의 다른 저장소와 비교할 때 해당 아이템이 이미 있는 것으로 취급됩니다.
아이템을 꺼낼 때는 우선순위가 가장 낮은 저장소부터 꺼냅니다. 따라서 네트워크 저장소에 아이템을 넣고 꺼내면
우선순위가 높은 저장소는 채워지고 낮은 저장소는 비워집니다.

## 조합법

<RecipeFor id="chest" />
