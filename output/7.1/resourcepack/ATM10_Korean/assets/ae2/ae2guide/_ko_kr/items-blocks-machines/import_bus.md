---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: ME 반입 버스
  icon: import_bus
  position: 220
categories:
- devices
item_ids:
- ae2:import_bus
---

# ME 반입 버스

<GameScene zoom="8" background="transparent">
<ImportStructure src="../assets/blocks/import_bus.snbt" />
</GameScene>

반입 버스는 맞닿은 인벤토리에서 아이템과 유체(애드온이 있다면 그 밖의 대상도)를 꺼내
[네트워크 저장소](../ae2-mechanics/import-export-storage.md)로 보냅니다.

렉을 줄이기 위해 최근에 반입한 대상이 없으면 느리게 작동하는 "절전 모드"로 들어갑니다.
무언가를 성공적으로 반입하면 깨어나 최대 속도인 초당 4회 작업으로 가속합니다.

[케이블 부품](../ae2-mechanics/cable-subparts.md)으로 설치됩니다.

## 필터링

기본적으로 접근할 수 있는 모든 대상을 반입합니다. 필터 슬롯에 넣은 아이템은 허용 목록으로 작동해 지정한 아이템만 반입합니다.

현재 인벤토리에 없는 아이템이나 유체도 JEI/REI에서 슬롯으로 끌어올 수 있습니다.

양동이나 유체 탱크 같은 유체 용기를 들고 우클릭하면 용기 아이템 대신 그 안의 유체를 필터로 설정합니다.

## 업그레이드

반입 버스는 다음 [업그레이드](upgrade_cards.md)를 지원합니다.

*   <ItemLink id="capacity_card" />는 필터 슬롯 수를 늘립니다.
*   <ItemLink id="speed_card" />는 작업당 이동량을 늘립니다.
*   <ItemLink id="fuzzy_card" />는 내구도 수준으로 필터링하거나 아이템 NBT를 무시하게 합니다.
*   <ItemLink id="inverter_card" />는 필터를 허용 목록에서 차단 목록으로 바꿉니다.
*   <ItemLink id="redstone_card" />는 강한 신호, 약한 신호 또는 펄스당 한 번 작동하는 레드스톤 제어를 추가합니다.

## 속도

| 가속 카드 | 작업당 이동 아이템 수 |
|:-------------------|:--------------------------|
| 0                  | 1                         |
| 1                  | 8                         |
| 2                  | 32                        |
| 3                  | 64                        |
| 4                  | 96                        |

## 조합법

<RecipeFor id="import_bus" />
