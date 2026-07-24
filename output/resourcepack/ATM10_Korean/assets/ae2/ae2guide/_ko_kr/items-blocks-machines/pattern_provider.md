---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: ME 패턴 공급기
  icon: pattern_provider
  position: 210
categories:
- devices
item_ids:
- ae2:pattern_provider
- ae2:cable_pattern_provider
---

# ME 패턴 공급기

<Row gap="20">
<BlockImage id="pattern_provider" scale="8" />
<BlockImage id="pattern_provider" p:push_direction="up" scale="8" />
<GameScene zoom="8" background="transparent">
  <ImportStructure src="../assets/blocks/cable_pattern_provider.snbt" />
</GameScene>
</Row>

패턴 공급기는 [자동 제작](../ae2-mechanics/autocrafting.md) 시스템이 월드와 상호작용하는 주된 수단입니다.
[패턴](patterns.md)의 재료를 인접한 인벤토리로 보내며, 공급기에 아이템을 넣으면 네트워크로 들어갑니다.
<ItemLink id="import_bus" />로 기계의 출력물을 네트워크에 반입하는 대신, 가까운 패턴 공급기(보통 재료를 보낸 공급기)로
파이프를 연결해 출력물을 돌려보내면 채널을 아낄 수 있습니다.

공급기는 제작 CPU의 [제작 저장소](crafting_cpu_multiblock.md#crafting-storage)에서 재료를 직접 보내므로 인벤토리에 재료가 실제로 들어 있지 않습니다.
따라서 공급기에서 파이프로 꺼낼 수 없습니다. 공급기가 통 같은 다른 인벤토리로 보내게 한 뒤 그곳에서 파이프로 꺼내야 합니다.

또한 공급기는 모든 재료를 한꺼번에 보내야 하며 묶음의 일부만 보낼 수 없습니다. 이 특성을 유용하게 활용할 수 있습니다.

[서브네트워크](../ae2-mechanics/subnetworks.md)의 인터페이스는 패턴 공급기와 특별하게 상호작용합니다. 인터페이스가 변경되지 않아 요청 슬롯이 비었다면
공급기가 인터페이스를 완전히 건너뛰고 서브네트워크의 [저장소](../ae2-mechanics/import-export-storage.md)로 직접 보냅니다.
인터페이스를 조합법 재료 묶음으로 채우지 않으며, 더 중요하게는 기계에 공간이 생길 때까지 다음 묶음을 넣지 않습니다.
차단 모드도 올바르게 작동하며, 공급기는 인터페이스 슬롯 대신 기계 슬롯의 재료를 감시합니다.

예를 들어 이 설비는 제련할 대상과 연료를 화로의 해당 슬롯으로 직접 보냅니다.
이를 이용해 기계 하나의 여러 면이나 여러 기계에 패턴 재료를 공급할 수 있습니다.

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/furnace_automation.snbt" />

<BoxAnnotation color="#dddddd" min="1 0 0" max="2 1 1">
        (1) 패턴 공급기: 서투스 석영 렌치로 방향성 형태로 바꾸고 관련 가공 패턴을 넣었습니다.

        ![철 패턴](../assets/diagrams/furnace_pattern_small.png)
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 1 0" max="2 1.3 1">
        (2) 인터페이스: 기본 설정입니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 1 0" max="1.3 2 1">
        (3) 저장 버스 #1: 석탄으로 필터링했습니다.
        <ItemImage id="minecraft:coal" scale="2" />
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="0 2 0" max="1 2.3 1">
        (4) 저장 버스 #2: 반전 카드를 사용해 석탄을 차단 목록으로 필터링했습니다.
        <Row><ItemImage id="minecraft:coal" scale="2" /><ItemImage id="inverter_card" scale="2" /></Row>
  </BoxAnnotation>

<DiamondAnnotation pos="4 0.5 0.5" color="#00ff00">
        주 네트워크로 연결
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

다음은 여러 기계에 공급하는 일반적인 예시입니다.

<GameScene zoom="6" background="transparent">
<ImportStructure src="../assets/assemblies/provider_interface_storage.snbt" />

<BoxAnnotation color="#dddddd" min="2.7 0 1" max="3 1 2">
        인터페이스(전체 블록이 아닌 납작한 형태여야 함)
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 0 0" max="1.3 1 4">
        저장 버스
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="0 0 0" max="1 1 4">
        패턴 재료를 공급할 위치
  </BoxAnnotation>

<IsometricCamera yaw="185" pitch="30" />
</GameScene>

동일한 패턴을 가진 패턴 공급기 여러 개를 지원하며 병렬로 작동합니다.

패턴 공급기는 재료 묶음을 모든 면에 라운드 로빈 방식으로 보내 연결된 모든 기계를 병렬로 사용합니다.

## 변형

패턴 공급기에는 일반형, 방향성, 납작한 [부품](../ae2-mechanics/cable-subparts.md)형의 세 가지 변형이 있습니다.
이에 따라 재료를 보내고 아이템을 받으며 네트워크 연결을 제공하는 면이 달라집니다.

* 일반 패턴 공급기는 모든 면으로 재료를 보내고 모든 면에서 입력을 받습니다. 대부분의 AE2 기계처럼 케이블 역할을 하여
    모든 면에 [네트워크 연결](../ae2-mechanics/me-network-connections.md)을 제공합니다.

* 방향성 패턴 공급기는 일반 패턴 공급기에 <ItemLink id="certus_quartz_wrench" />를 사용해 방향을 바꾸면 됩니다.
    선택한 면으로만 재료를 보내고 모든 면에서 입력을 받으며, 선택한 면에는 특별히
  [네트워크 연결](../ae2-mechanics/me-network-connections.md)을 제공하지 않습니다. 서브네트워크를 만들 때 네트워크를 연결하지 않고 AE2 기계로 보낼 수 있습니다.

* 납작한 패턴 공급기는 [케이블 부품](../ae2-mechanics/cable-subparts.md)이므로 한 케이블에 여러 개를 설치해 설비를 작게 만들 수 있습니다.
    방향성 패턴 공급기의 선택한 면과 비슷하게 작동해 패턴을 제공하고 입력을 받지만, 앞면에는
    [네트워크 연결](../ae2-mechanics/me-network-connections.md)을 **제공하지 않습니다.**

제작 격자에서 일반형과 납작한 형태를 서로 바꿀 수 있습니다.

## 설정

패턴 공급기에는 여러 모드가 있습니다.

*   **차단 모드**는 기계에 재료가 이미 있으면 공급기가 새 재료 묶음을 보내지 않게 합니다.
*   **제작 잠금**은 여러 레드스톤 조건에서, 또는 이전 제작의 결과물이 해당 패턴 공급기에 들어올 때까지 공급기를 잠급니다.
*   <ItemLink id="pattern_access_terminal" />에 공급기를 표시하거나 숨길 수 있습니다.

## 우선순위

GUI 오른쪽 위의 렌치를 클릭해 우선순위를 설정할 수 있습니다. 같은 아이템을 만드는 [패턴](patterns.md)이 여러 개라면
우선순위가 높은 공급기의 패턴을 낮은 공급기의 패턴보다 먼저 사용합니다. 단, 네트워크에 높은 우선순위 패턴의 재료가 없다면 예외입니다.

## 흔한 오해

이유는 모르겠지만 많은 분이 계속 이렇게 구성하므로 도움이 되길 바라며 설명합니다.
(<ItemLink id="export_bus" />만 네트워크에서 대상을 내보낼 수 있다고 생각하고 패턴 공급기도 대상을 내보낸다는 점을 모르는 듯합니다.)

이 구성은 원하는 대로 작동하지 않습니다. [케이블](cables.md)에서 설명했듯 케이블은 아이템 파이프가 아니며
내부 인벤토리가 없으므로 공급기가 케이블 안으로 재료를 보내지 않습니다.

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../assets/assemblies/provider_misconception_1.snbt" />

  <BoxAnnotation color="#dddddd" min="1 0 3" max="2 1 4">
        용광로가 아님
  </BoxAnnotation>

  <IsometricCamera yaw="95" pitch="5" />
</GameScene>

공급기가 재료를 보낼 대상이 없으므로 작동할 수 없습니다. 여기서는 케이블처럼 <ItemLink id="export_bus" />를
네트워크에 연결할 뿐입니다.

공급기가 <ItemLink id="export_bus" />에 무엇을 반출할지 알려 주지도 않습니다. 반출 버스는 필터에 넣은 모든 대상을 반출할 뿐입니다.

결국 만든 구성은 다음과 같습니다.

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../assets/assemblies/provider_misconception_2.snbt" />

  <BoxAnnotation color="#dddddd" min="1 0 3" max="2 1 4">
        용광로가 아님
  </BoxAnnotation>

  <IsometricCamera yaw="95" pitch="5" />
</GameScene>

실제로 필요한 구성은 패턴 공급기가 패턴의 내용을 인접한 기계로 내보내는 다음 형태입니다.

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../assets/assemblies/provider_misconception_3.snbt" />

  <BoxAnnotation color="#dddddd" min="1 0 3" max="2 1 4">
        용광로가 아님
  </BoxAnnotation>

  <IsometricCamera yaw="95" pitch="5" />
</GameScene>

## 분자 제작기와 함께 사용하기

<ItemLink id="molecular_assembler" />는 기본적으로 다른 기계와 같습니다. 아이템을 넣을 수 있는 인벤토리가 있고,
그 안의 대상에 작업을 수행한 뒤 많은 기계처럼 결과물을 인접한 인벤토리로 보냅니다.
따라서 한 가지 추가 기능을 제외하면 다른 기계처럼 공급기와 함께 사용합니다.

제작기에 직접 넣은 <ItemLink id="crafting_pattern" />, <ItemLink id="smithing_table_pattern" />, <ItemLink id="stonecutting_pattern" />에서
원하는 패턴을 읽을 수 있습니다. 조립 라인에는 유용하지만 제작 조합법마다 전용 제작기를 두는 것은 번거롭습니다.

따라서 패턴 공급기에는 패턴 데이터를 재료와 함께 제작기로 보내는 특별한 기능이 있습니다.
패턴 공급기 옆에 제작기를 놓기만 하면 공급기가 모든 제작, 대장장이 작업대, 석재 절단 패턴에 그 제작기를 사용할 수 있습니다.

정말 간단합니다. 공급기에 패턴을 넣기만 하면 됩니다.

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/assembler_tower.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

*여기에는 공급기가 정확히 8개 있습니다. 제작기, 공급기 또는 조밀하지 않은 케이블 하나를 통해 전달할 수 있는 최대 채널 수입니다.*

## 조합법

<RecipeFor id="pattern_provider" />

<RecipeFor id="cable_pattern_provider" />
