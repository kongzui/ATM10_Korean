---
navigation:
  parent: example-setups/example-setups-index.md
  title: 전용 지역 저장소
  icon: drive
---

# 전용 지역 저장소

[인터페이스의 특별한 동작](../items-blocks-machines/interface.md#special-interactions)을 이용하면
[서브네트워크](../ae2-mechanics/subnetworks.md)가 주 네트워크의 저장소를 볼 수 없는 상태로 자신의 저장소
내용을 주 네트워크에 제공할 수 있습니다. 주 네트워크에서는 [채널](../ae2-mechanics/channels.md) 하나만
사용합니다.

농장 생산물이 주 저장소로 넘치지 않도록 지역 저장소를 만들 때 유용합니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/local_storage.snbt" />

<BoxAnnotation color="#dddddd" min="4 0 0" max="5 2 1">
        (1) 아이템을 반입하는 방법: 이 예에서는 인터페이스입니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="3 0 0" max="4 1 1">
        (2) ME 드라이브: 셀을 장착합니다. 셀은 농장 생산물로 필터링해야 합니다. 균등 분배 카드와
        초과분 파괴 카드를 설치할 수 있습니다.
        <Row><ItemImage id="item_storage_cell_4k" scale="2" /> <ItemImage id="equal_distribution_card" scale="2" /> <ItemImage id="void_card" scale="2" /></Row>
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="3 1 0" max="4 2 0.3">
        (3) 제작 터미널: 서브네트워크의 ME 드라이브 내용은 보이지만 주 네트워크 저장소 내용은 보이지 않습니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="2 0 0" max="2.3 1 1">
        (4) 인터페이스 2: 기본 설정을 사용합니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1.7 0 0" max="2 1 1">
        (5) 저장 버스: 주 저장소보다 높은 우선순위를 설정하며 농장 생산물로 필터링할 수 있습니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 1 0" max="2 2 0.3">
        제작 터미널: 주 네트워크 저장소와 서브네트워크의 내용을 모두 볼 수 있습니다.
  </BoxAnnotation>

<DiamondAnnotation pos="0 0.5 0.5" color="#00ff00">
        주 네트워크로 연결
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 설정

* 첫 번째 <ItemLink id="interface" /> (1)는 농장의 아이템을 받아 서브네트워크로 밀어냅니다.
* <ItemLink id="drive" /> (2)에 [셀](../items-blocks-machines/storage_cells.md)을 장착합니다. 셀은 농장
  생산물에 맞게 [파티션](../items-blocks-machines/cell_workbench.md)을 설정해야 합니다. 셀에
  <ItemLink id="equal_distribution_card" />와 <ItemLink id="void_card" />를 설치할 수 있습니다.
* 두 번째 <ItemLink id="interface" /> (4)는 기본 설정을 사용합니다.
* <ItemLink id="storage_bus" />는 [우선순위](../ae2-mechanics/import-export-storage.md#storage-priority)를 주
  저장소보다 높게 설정하며 농장 생산물로 필터링할 수 있습니다.

## 작동 방식

* 서브네트워크의 <ItemLink id="interface" />는 주 네트워크의 <ItemLink id="storage_bus" />에
  <ItemLink id="drive" />의 내용을 보여 줍니다. 저장 버스는 ME 드라이브의 셀에 아이템을 직접 넣고
  꺼낼 수 있습니다.
* 저장 버스는 높은 [우선순위](../ae2-mechanics/import-export-storage.md#storage-priority)를 사용하므로 아이템이
  주 저장소보다 서브네트워크로 우선적으로 돌아갑니다.
* 중요한 점으로, 서브네트워크의 셀이 가득 차도 아이템이 주 네트워크로 넘치지 않습니다. 밀려서 멈추면
  문제가 생기는 농장이라면 <ItemLink id="void_card" />로 초과 아이템을 삭제할 수 있습니다.
* 농장이 여러 아이템을 생산한다면 <ItemLink id="equal_distribution_card" />로 한 아이템이 모든 셀을
  채워 다른 아이템을 저장하지 못하는 일을 막을 수 있습니다.
