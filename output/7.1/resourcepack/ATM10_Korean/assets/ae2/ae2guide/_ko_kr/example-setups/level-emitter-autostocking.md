---
navigation:
  parent: example-setups/example-setups-index.md
  title: 레벨 방출기 자동 비축
  icon: level_emitter
---

# 레벨 방출기 자동 비축

"아이템 하나를 일정 수량만큼 비축하고 필요할 때 더 제작하려면 어떻게 해야 할까?"라는 의문이 들 수
있습니다.

<ItemLink id="export_bus" />, <ItemLink id="level_emitter" />와 <ItemLink id="crafting_card" />를 사용하면
네트워크의 [자동 제작](../ae2-mechanics/autocrafting.md)에 새 아이템을 자동으로 요청할 수 있습니다. 한
아이템을 대량으로 유지하는 데 적합한 구성입니다.

레벨 방출기와 레드스톤 카드를 생략하면 네트워크가 계속 제작하도록 만들 수도 있습니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/level_emitter_autostocking.snbt" />

  <BoxAnnotation color="#dddddd" min="1 1 0" max="2 1.3 1">
        (1) 반출 버스: 원하는 아이템으로 필터링하고 레드스톤 카드와 제작 카드를 설치합니다. 레드스톤
        모드는 "신호가 있으면 활성화", 제작 동작은 "비축된 아이템 사용 안 함"으로 설정합니다.
        <Row><ItemImage id="redstone_card" scale="2" /> <ItemImage id="crafting_card" scale="2" /></Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="0.7 1 0" max="1 2 1">
        (2) 레벨 방출기: 원하는 아이템과 수량을 지정하고 "수량이 한도 미만이면 방출"로 설정합니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="1 0 0" max="2 1 1">
        (3) 인터페이스: 기본 설정을 사용합니다.
  </BoxAnnotation>

<DiamondAnnotation pos="4 0.5 0.5" color="#00ff00">
        주 네트워크로 연결
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 설정

* <ItemLink id="export_bus" /> (1)는 원하는 아이템으로 필터링하고 <ItemLink id="redstone_card" />와
  <ItemLink id="crafting_card" />를 설치합니다. "레드스톤 모드"는 "신호가 있으면 활성화", "제작 동작"은
  "비축된 아이템 사용 안 함"으로 설정합니다.
* <ItemLink id="level_emitter" /> (2)는 원하는 아이템과 수량을 지정하고 "수량이 한도 미만이면 방출"로
  설정합니다.
* <ItemLink id="interface" /> (3)은 기본 설정을 사용합니다.

## 작동 방식

1. [네트워크 저장소](../ae2-mechanics/import-export-storage.md)의 원하는 아이템 수량이
   <ItemLink id="level_emitter" />에 지정한 수량보다 적으면 레드스톤 신호를 내보냅니다.
2. 레드스톤 신호를 받고 <ItemLink id="crafting_card" />가 설치되어 있으며 비축된 아이템을 사용하지
   않도록 설정된 <ItemLink id="export_bus" />는 네트워크의 [자동 제작](../ae2-mechanics/autocrafting.md)에
   해당 아이템을 더 만들도록 요청한 다음 반출합니다.
3. 내부 인벤토리에 비축 항목이 설정되지 않은 <ItemLink id="interface" />는 들어온 아이템을 네트워크
   저장소로 밀어냅니다.
