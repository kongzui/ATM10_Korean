---
navigation:
  parent: ae2-mechanics/ae2-mechanics-index.md
  title: 반입, 반출 및 저장
---

# 반입, 반출 및 저장

**ME 시스템과 외부 세계의 관계**

AE2에서 중요한 개념 중 하나는 네트워크 저장소입니다. 네트워크의 내용물이 저장되는 곳으로, 일반적으로
[저장 셀](../items-blocks-machines/storage_cells.md)이나 <ItemLink id="storage_bus" />가 연결된
인벤토리를 뜻합니다. 대부분의 AE2 [장치](../ae2-mechanics/devices.md)는 어떤 방식으로든 네트워크
저장소와 상호작용합니다.

예를 들면 다음과 같습니다.

*   <ItemLink id="import_bus" />는 내용물을 네트워크 저장소로 밀어 넣습니다.
*   <ItemLink id="export_bus" />는 내용물을 네트워크 저장소에서 가져옵니다.
*   <ItemLink id="interface" />는 네트워크 저장소로 넣기도 하고 가져오기도 합니다.
*   [터미널](../items-blocks-machines/terminals.md)은 아이템을 넣거나 꺼낼 때, 또는 제작 슬롯을 다시
    채울 때 네트워크 저장소로 넣고 가져옵니다.
*   <ItemLink id="storage_bus" /> 자체는 저장소로 넣거나 가져오는 장치라기보다, 연결된 인벤토리를
    네트워크 저장소로 사용하도록 그 인벤토리에 넣고 가져옵니다. 실제로는 다른 장치가 저장 버스를
    대상으로 내용물을 넣거나 가져오는 셈입니다.

<GameScene zoom="4" interactive={true}>
  <ImportStructure src="../assets/assemblies/import_export_storage.snbt" />

  <BoxAnnotation color="#dddddd" min="8 1 1" max="9 1.3 2">
        반입 버스는 향하고 있는 인벤토리의 내용물을 네트워크 저장소로 반입합니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="8 2 1" max="9 3 1.3">
        플레이어 인벤토리에서 터미널로 무언가를 넣는 것도 네트워크가 반입한 것으로 간주됩니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="7 0 1" max="8 1 2">
        인터페이스의 슬롯에 비축 항목이 설정되지 않았거나 설정된 수량보다 많은 아이템이 있으면 내부
        인벤토리에서 반입합니다. 따라서 인터페이스에 내용물을 밀어 넣어 네트워크에 넣을 수 있습니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="6 0 1" max="7 1 2">
        패턴 공급기는 내부 반환 슬롯에서 반입하므로, 내용물을 밀어 넣어 네트워크에 넣을 수 있습니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="4 1 1" max="5 2 2">
        ME 드라이브는 장착된 셀을 네트워크 저장소로 제공합니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="3 1 1" max="4 1.3 2">
        ME 저장 버스는 향하고 있는 인벤토리를 네트워크 저장소로 사용합니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="1 1 1" max="2 1.3 2">
        반출 버스는 네트워크 저장소의 내용물을 향하고 있는 인벤토리로 반출합니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="1 2 1" max="2 3 1.3">
        터미널에서 무언가를 꺼내는 것도 네트워크가 반출한 것으로 간주됩니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="0 1 1" max="1 2 2">
        인터페이스의 슬롯에 비축 항목이 설정되어 있으면 내부 인벤토리로 반출합니다. 따라서 인터페이스에서
        내용물을 꺼내 네트워크에서 가져올 수 있습니다.
  </BoxAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

자동화와 물류 구성을 설계할 때는 네트워크 저장소로 밀어 넣고 가져오는 동작과 사건을 염두에 두어야
합니다.

## 저장소 우선순위

일부 GUI의 오른쪽 위에 있는 렌치를 클릭해 우선순위를 설정할 수 있습니다. 네트워크에 들어오는 아이템은
가장 높은 우선순위의 저장소를 첫 목적지로 선택합니다. 두 저장소의 우선순위가 같다면 해당 아이템을 이미
보관 중인 저장소를 다른 곳보다 우선합니다. 허용 목록이 설정된 셀은 같은 우선순위 그룹의 다른 저장소와
비교할 때 해당 아이템을 이미 보관 중인 것으로 취급됩니다. 아이템을 꺼낼 때는 가장 낮은 우선순위의
저장소부터 꺼냅니다. 따라서 네트워크 저장소에 아이템을 넣고 꺼내는 과정에서 높은 우선순위 저장소는
채워지고 낮은 우선순위 저장소는 비워집니다.
