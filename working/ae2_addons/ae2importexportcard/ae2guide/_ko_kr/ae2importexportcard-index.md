---
navigation:
  title: "애드온: AE2 Import Export Card"
  icon: ae2importexportcard:export_card
  position: 150
categories:
  - tools
item_ids:
- ae2importexportcard:export_card
- ae2importexportcard:import_card
---

# AE2 Import Export Card

<Row>
  <ItemImage id="ae2importexportcard:export_card" scale="2" />

  <ItemImage id="ae2importexportcard:import_card" scale="2" />
</Row>

반입 카드와 반출 카드를 사용하면 인벤토리에서 아이템을 반입하거나 반출할 수 있습니다.

## 반입 카드

<ItemImage id="ae2importexportcard:import_card" scale="2" />

반입 카드는 인벤토리의 특정 슬롯에 있는 아이템을 ME 시스템으로 옮깁니다.

![반입 카드](diagrams/import_card.png)

슬롯을 클릭하면 확인 표시가 생깁니다. 확인 표시가 있는 슬롯의 모든 아이템은 ME 시스템으로 반입됩니다.
필터를 바꾸려면 인벤토리의 아이템을 위쪽으로 끌어다 놓으세요.

### 업그레이드

반입 카드는 다음 [업그레이드](items-blocks-machines/upgrade_cards.md)를 지원합니다.

*   <ItemLink id="fuzzy_card" />: 내구도로 필터링하거나 아이템 NBT를 무시합니다
*   <ItemLink id="inverter_card" />: 필터를 허용 목록에서 차단 목록으로 전환합니다

### 제작법

<RecipeFor id="ae2importexportcard:import_card" />

## 반출 카드

<ItemImage id="ae2importexportcard:export_card" scale="2" />

반출 카드는 같은 방식으로 작동하지만, ME 시스템의 아이템을 인벤토리로 가져옵니다.

![반출 카드](diagrams/export_card.png)

반출할 아이템을 지정하려면 인벤토리의 아이템을 위쪽 슬롯 중 하나로 끌어다 놓고, 인벤토리 슬롯을
클릭하여 원하는 수량으로 바꾸세요. 오른쪽 클릭하면 X로 초기화됩니다.

### 업그레이드

반출 카드는 다음 [업그레이드](items-blocks-machines/upgrade_cards.md)를 지원합니다.

*   <ItemLink id="fuzzy_card" />: 내구도로 필터링하거나 아이템 NBT를 무시합니다
*   <ItemLink id="speed_card" />: 전송 속도를 1개에서 아이템 한 묶음까지 높입니다
*   <ItemLink id="crafting_card" />: 현재 없는 아이템을 자동으로 요청하고 제작합니다

### 제작법

<RecipeFor id="ae2importexportcard:export_card" />
