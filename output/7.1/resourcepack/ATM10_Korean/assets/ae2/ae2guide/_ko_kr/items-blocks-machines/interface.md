---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: ME 인터페이스
  icon: interface
  position: 210
categories:
- devices
item_ids:
- ae2:interface
- ae2:cable_interface
---

# ME 인터페이스

<Row gap="20">
<BlockImage id="interface" scale="8" />
<GameScene zoom="8" background="transparent">
  <ImportStructure src="../assets/blocks/cable_interface.snbt" />
</GameScene>
</Row>

인터페이스는 작은 상자이자 유체 탱크처럼 작동합니다. 슬롯에 비축하도록 설정한 대상에 따라
[네트워크 저장소](../ae2-mechanics/import-export-storage.md)에서 스스로 채우거나 저장소로 비웁니다.
이를 게임 틱 하나에 완료하려 하므로 게임 틱당 최대 9스택을 채우거나 비울 수 있습니다. 빠른 아이템 파이프가 있다면 빠른 반입·반출 수단입니다.

대부분의 유체 탱크는 유체 한 종류만 저장하지만 인터페이스는 아이템과 함께 최대 9종의 유체를 저장할 수 있습니다.
추가 기능이 있는 상자·다중 유체 탱크인 셈이며, 어떤 네트워크에도 연결하지 않으면 추가 기능을 막을 수 있습니다.
따라서 여러 종류의 대상을 소량씩 저장하려는 특수한 상황에 유용합니다.

## 인터페이스의 내부 작동 방식

앞서 설명했듯 인터페이스는 매우 강력한 <ItemLink id="import_bus" />와 <ItemLink id="export_bus" />,
여러 <ItemLink id="level_emitter" />가 붙은 상자·탱크와 같습니다.

<GameScene zoom="3" interactive={true}>
  <ImportStructure src="../assets/assemblies/interface_internals.snbt" />

  <BoxAnnotation color="#dddddd" min="1.3 0.3 1.3" max="9.7 1 1.7">
        요청한 비축 수량을 제어하는 여러 레벨 방출기
        <GameScene zoom="4" background="transparent">
        <ImportStructure src="../assets/blocks/level_emitter.snbt" />
        </GameScene>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="1.3 4 1.3" max="9.7 4.7 1.7">
        요청한 비축 수량을 제어하는 여러 레벨 방출기
        <GameScene zoom="4" background="transparent">
        <ImportStructure src="../assets/blocks/level_emitter.snbt" />
        </GameScene>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="1.3 1.3 1.3" max="9.7 2 1.7">
        게임 틱당 1스택을 옮기는 매우 강력한 반입 버스 여러 개
        <GameScene zoom="4" background="transparent">
        <ImportStructure src="../assets/blocks/import_bus.snbt" />
        </GameScene>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="1.3 3 1.3" max="9.7 3.7 1.7">
        게임 틱당 1스택을 옮기는 매우 강력한 반출 버스 여러 개
        <GameScene zoom="4" background="transparent">
        <ImportStructure src="../assets/blocks/export_bus.snbt" />
        </GameScene>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="1 2 1" max="10 3 2">
        서로 분리된 내부 슬롯 9개
  </BoxAnnotation>

  <IsometricCamera yaw="195" pitch="15" />
</GameScene>

## 특별한 상호작용

인터페이스에는 다른 AE2 [장치](../ae2-mechanics/devices.md)와의 특별한 기능도 있습니다.

설정하지 않은 인터페이스에 <ItemLink id="storage_bus" />를 붙이면 인터페이스 쪽 네트워크가 거대한 상자이고 저장 버스가 그 위에 설치된 것처럼,
그 네트워크의 [네트워크 저장소](../ae2-mechanics/import-export-storage.md) 전체를 저장 버스 쪽 네트워크에 보여 줍니다.
인터페이스 필터 슬롯에 비축할 아이템을 설정하면 이 기능이 비활성화됩니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/interface_storage.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

[서브네트워크](../ae2-mechanics/subnetworks.md)의 인터페이스는 패턴 공급기와 특별하게 상호작용합니다. 인터페이스가 설정되지 않았다면
공급기가 인터페이스를 완전히 건너뛰고 서브네트워크의 [저장소](../ae2-mechanics/import-export-storage.md)로 직접 보냅니다.
인터페이스를 조합법 재료 묶음으로 채우지 않으며, 더 중요하게는 저장소에 공간이 생길 때까지 다음 묶음을 넣지 않습니다.

<GameScene zoom="6" background="transparent">
<ImportStructure src="../assets/assemblies/provider_interface_storage.snbt" />

<BoxAnnotation color="#dddddd" min="2.7 0 1" max="3 1 2">
        인터페이스(전체 블록이 아닌 납작한 형태여야 함)
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 0 0" max="1.3 1 4">
        저장 버스
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="0 0 0" max="1 1 4">
        패턴 재료를 공급할 위치(여러 기계 또는 기계 하나의 여러 면)
  </BoxAnnotation>

<IsometricCamera yaw="185" pitch="30" />
</GameScene>

## 변형

인터페이스에는 일반형과 납작한 [부품](../ae2-mechanics/cable-subparts.md)형의 두 가지 변형이 있습니다.
이에 따라 인벤토리에 접근할 수 있는 면과 네트워크 연결을 제공하는 면이 달라집니다.

*   일반 인터페이스는 모든 면에서 인벤토리에 넣고 꺼내며 접근할 수 있습니다. 대부분의 AE2 기계처럼 케이블 역할을 하여 모든 면에 네트워크 연결을 제공합니다.

*   납작한 인터페이스는 [케이블 부품](../ae2-mechanics/cable-subparts.md)이므로 한 케이블에 여러 개를 설치해 설비를 작게 만들 수 있습니다.
    앞면에서 인벤토리에 넣고 꺼내며 접근할 수 있지만 앞면에는 네트워크 연결을 제공하지 않습니다.

제작 격자에서 일반형과 납작한 형태를 서로 바꿀 수 있습니다.

## 설정

인터페이스의 위쪽 슬롯은 내부에 비축할 대상을 정합니다. 슬롯에 대상을 넣거나 JEI/REI에서 끌어오면
수량을 설정하는 렌치가 나타납니다.

양동이나 유체 탱크 같은 유체 용기를 들고 우클릭하면 용기 아이템 대신 그 안의 유체를 필터로 설정합니다.

슬롯을 비축 모드로 설정하면 외부 기계가 그 슬롯에 다른 대상을 넣지 못합니다.

## 업그레이드

인터페이스는 다음 [업그레이드](upgrade_cards.md)를 지원합니다.

*   <ItemLink id="fuzzy_card" />는 내구도 수준으로 필터링하거나 아이템 NBT를 무시하게 합니다.
*   <ItemLink id="crafting_card" />는 필요한 아이템을 얻도록 [자동 제작](../ae2-mechanics/autocrafting.md) 시스템에 제작 요청을 보냅니다.
    새 아이템 제작을 요청하기 전에 가능하면 저장소에서 아이템을 꺼냅니다.

## 우선순위

GUI 오른쪽 위의 렌치를 클릭해 우선순위를 설정할 수 있습니다. 우선순위가 높은 인터페이스가 낮은 인터페이스보다 먼저 아이템을 받습니다.

## 조합법

<Recipe id="network/blocks/interfaces_interface" />

<RecipeFor id="cable_interface" />
