---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: ME 드라이브
  icon: drive
  position: 210
categories:
- devices
item_ids:
- ae2:drive
---

# ME 드라이브

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../assets/blocks/drive.snbt" />
</GameScene>

ME 드라이브는 [장치](../ae2-mechanics/devices.md)로, [저장 셀](storage_cells.md)을 넣어
[네트워크 저장소](../ae2-mechanics/import-export-storage.md)로 사용합니다. 셀을 하나씩 넣을 수 있는 슬롯이 10개 있습니다.

필요하다면 호퍼나 AE2 버스 같은 모든 아이템 물류 장치로 인벤토리의 셀을 넣고 꺼낼 수 있습니다.

<ItemLink id="certus_quartz_wrench" />로 회전할 수 있습니다.

## 셀 상태 LED

드라이브 안의 셀에는 상태를 보여 주는 LED가 있습니다.

| 색상   | 상태                                                                             |
| :----- | :------------------------------------------------------------------------------- |
| 초록색 | 비어 있음                                                                        |
| 파란색 | 내용물이 일부 있음                                                               |
| 주황색 | [유형](../ae2-mechanics/bytes-and-types.md)이 가득 차 새 유형을 추가할 수 없음   |
| 빨간색 | [바이트](../ae2-mechanics/bytes-and-types.md)가 가득 차 더 넣을 수 없음          |
| 검은색 | 전력이 없거나 드라이브에 [채널](../ae2-mechanics/channels.md)이 없음             |

## 우선순위

GUI 오른쪽 위의 렌치를 클릭해 우선순위를 설정할 수 있습니다.
네트워크에 들어오는 아이템은 우선순위가 가장 높은 저장소부터 향합니다. 저장소나 셀 둘의 우선순위가 같고
한쪽에 해당 아이템이 이미 있다면 다른 저장소보다 그곳을 우선합니다. [파티션](cell_workbench.md)이 설정된 셀은
같은 우선순위 그룹의 다른 저장소와 비교할 때 해당 아이템이 이미 있는 것으로 취급됩니다.
아이템을 꺼낼 때는 우선순위가 가장 낮은 저장소부터 꺼냅니다. 따라서 네트워크 저장소에 아이템을 넣고 꺼내면
우선순위가 높은 저장소는 채워지고 낮은 저장소는 비워집니다.

## 조합법

<RecipeFor id="drive" />
