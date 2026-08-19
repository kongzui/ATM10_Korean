---
navigation:
  parent: example-setups/example-setups-index.md
  title: 재귀 제작
  icon: minecraft:netherite_upgrade_smithing_template
---

# 재귀 제작 구성

[자동 제작](../ae2-mechanics/autocrafting.md)에서 설명했듯이 자동 제작 계획 알고리즘은 주 출력물이 입력 중 하나인
제작법을 처리할 수 없습니다. 예를 들어 <ItemLink id="minecraft:netherite_upgrade_smithing_template" /> 복제를 처리하지 못합니다.

한 가지 해결책은 <ItemLink id="level_emitter" />가 [패턴](../items-blocks-machines/patterns.md)인 것처럼 작동하는 기능을 이용하는 것입니다.

이를 통해 제작을 계속 수행하는 작은 설비를 켤 수 있습니다. 여기서는
<ItemLink id="minecraft:netherite_upgrade_smithing_template" />을 복제하는 구성을 살펴봅니다.

<RecipeFor id="minecraft:netherite_upgrade_smithing_template" />

***

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/recursive_recipe_setup.snbt" />

  <BoxAnnotation color="#dddddd" min="1 0 0" max="2 1 1">
        (1) 인터페이스: 필요한 추가 재료인 다이아몬드와 네더랙을 비축하도록 설정했습니다.
        <Row><ItemImage id="minecraft:diamond" scale="2" /> <ItemImage id="minecraft:netherrack" scale="2" /></Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2.3 1 0.3" max="2.7 1.3 0.7">
        (2) 레벨 방출기: "네더라이트 강화 대장장이 형판"으로 설정하고 "아이템 제작을 위해 레드스톤 방출"로 지정했습니다.
        <Row><ItemImage id="minecraft:netherite_upgrade_smithing_template" scale="2" /> <ItemImage id="crafting_card" scale="2" /></Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2 0 0" max="2.3 1 1">
        (3) 반입 버스 #1: 인터페이스가 비축하는 아이템으로 필터링했습니다. 레드스톤 카드가 있으며 레드스톤 모드는
        "신호가 있을 때 활성"입니다.
        <Row>
        <ItemImage id="minecraft:diamond" scale="2" />
        <ItemImage id="minecraft:netherrack" scale="2" />
        <ItemImage id="redstone_card" scale="2" />
        </Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="3 1 1" max="4 1.3 2">
        (4) 저장 버스 #1: 다른 저장 버스보다 우선순위를 높게 설정했습니다. 매우 중요합니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="3 0 1" max="4 1 2">
        (5) 분자 조립기: 대장장이 형판 복제 패턴이 들어 있습니다.

        ![패턴](../assets/diagrams/smithing_template_pattern_small.png)

        처음 설비를 만들 때 대장장이 형판 하나를 직접 넣어 두어야 합니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2.7 0 1" max="3 1 2">
        (6) 반입 버스 #2: 기본 설정입니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="1 0 1" max="2 1 1.3">
        (7) 저장 버스 #2: "네더라이트 강화 대장장이 형판"으로 필터링했습니다. 다른 저장 버스보다 우선순위를 낮게 설정했습니다.
        <ItemImage id="minecraft:netherite_upgrade_smithing_template" scale="2" />
  </BoxAnnotation>

<DiamondAnnotation pos="0 0.5 0.5" color="#00ff00">
        주 네트워크로
    </DiamondAnnotation>

  <IsometricCamera yaw="15" pitch="30" />
</GameScene>

## 설정

* <ItemLink id="interface" /> (1)는 필요한 추가 재료인 다이아몬드와 네더랙을 비축하도록 설정했습니다.
* <ItemLink id="level_emitter" /> (2)는 "네더라이트 강화 대장장이 형판"으로 설정하고 "아이템 제작을 위해 레드스톤 방출"로 지정했습니다.
* 첫 번째 <ItemLink id="import_bus" /> (3)은 인터페이스가 비축하는 아이템으로 필터링했습니다. 레드스톤 카드가 있으며 레드스톤 모드는 "신호가 있을 때 활성"입니다.
* 첫 번째 <ItemLink id="storage_bus" /> (4)는 두 번째 저장 버스보다 [우선순위](../ae2-mechanics/import-export-storage.md#storage-priority)를 *높게* 설정했습니다.
* <ItemLink id="molecular_assembler" /> (5)에는 대장장이 형판 복제 패턴과 직접 넣어 둔 대장장이 형판 하나가 있습니다.

  ![패턴](../assets/diagrams/smithing_template_pattern.png)

* 두 번째 <ItemLink id="import_bus" /> (6)은 기본 설정입니다.
* 두 번째 <ItemLink id="storage_bus" /> (7)은 "네더라이트 강화 대장장이 형판"으로 필터링했으며 첫 번째 저장 버스보다 [우선순위](../ae2-mechanics/import-export-storage.md#storage-priority)가 *낮습니다*.

## 작동 원리

1. <ItemLink id="level_emitter" />는 <ItemLink id="crafting_card" />를 넣고 "아이템 제작을 위해 레드스톤 방출"로 설정했기 때문에
   [패턴](../items-blocks-machines/patterns.md)인 것처럼 작동합니다. 따라서 "네더라이트 강화 대장장이 형판"이
   [터미널](../items-blocks-machines/terminals.md)에 [자동 제작](../ae2-mechanics/autocrafting.md) 가능한 항목으로 표시됩니다.
2. 플레이어나 시스템 자체가 해당 아이템 제작을 요청하면 레벨 방출기가 켜집니다.
3. 첫 번째 <ItemLink id="import_bus" />가 레벨 방출기에 의해 활성화되어 <ItemLink id="interface" />에 비축된 재료를 꺼냅니다.
4. 네트워크에서 이 재료들을 저장할 수 있는 유일한 <ItemLink id="storage_bus" />는 조립기에 붙은 버스입니다.
5. <ItemLink id="molecular_assembler" />가 재료를 받아(이미 대장장이 형판 하나가 들어 있음) 제작을 수행하고 형판 두 개를 만듭니다.
6. 두 번째 <ItemLink id="import_bus" />가 대장장이 형판 하나를 꺼냅니다.
7. 첫 번째 저장 버스의 우선순위가 더 높으므로 그 대장장이 형판은 조립기로 돌아갑니다.
8. 두 번째 <ItemLink id="import_bus" />가 대장장이 형판 하나를 꺼냅니다.
9. 조립기는 형판을 하나 더 받을 수 없으므로 두 번째 형판은 우선순위가 낮은 저장 버스로 가서 인터페이스에 들어갑니다.
10. <ItemLink id="interface" />는 형판을 비축하도록 설정되지 않았으므로 이를 네트워크에 넣습니다.
