---
navigation:
  parent: ae2-mechanics/ae2-mechanics-index.md
  title: 네트워크 연결
  icon: fluix_glass_cable
---

# 네트워크 연결

## "네트워크"란 무엇인가요?

"네트워크"는 [장치](../ae2-mechanics/devices.md) 묶음입니다. 이들은
[채널](../ae2-mechanics/channels.md)을 전달할 수 있는 [케이블](../items-blocks-machines/cables.md), 완전한
블록 형태의 기계나 [장치](../ae2-mechanics/devices.md)로 연결됩니다. 예를 들면 <ItemLink id="charger" />,
<ItemLink id="interface" />, <ItemLink id="drive" /> 등이 있습니다. 엄밀히 말하면 케이블 하나만
있어도 네트워크입니다.

## 장치 위치에 관한 참고 사항

[장치](../ae2-mechanics/devices.md) 중에는 특정 네트워크 기능을 수행하는 것들이 있습니다. 예를 들어
<ItemLink id="interface" />는 [네트워크 저장소](../ae2-mechanics/import-export-storage.md)에 넣고 가져오며,
<ItemLink id="level_emitter" />는 네트워크 저장소의 내용물을 읽고, <ItemLink id="drive" />는 네트워크
저장소 역할을 합니다. 이런 장치는 물리적인 위치가 중요하지 않습니다.

다시 강조하지만 **장치의 물리적인 위치는 중요하지 않습니다**. 중요한 것은 장치가 네트워크에 연결되어
있는지, 그리고 어느 네트워크에 연결되어 있는지뿐입니다.

## 네트워크 연결

네트워크에서 무엇이 연결되어 있는지 쉽게 확인하려면 <ItemLink id="network_tool" />를 사용하세요.
네트워크의 모든 구성 요소가 표시됩니다. 있어서는 안 될 것이 보이거나 있어야 할 것이 보이지 않는다면
연결에 문제가 있는 것입니다.

예를 들어 다음은 서로 분리된 네트워크 2개입니다.

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/2_networks_1.snbt" />

  <BoxAnnotation color="#915dcd" min="0 0 0" max="1 2 2">
        네트워크 1
  </BoxAnnotation>

<BoxAnnotation color="#5CA7CD" min="2 0 0" max="3 2 2">
        네트워크 2
  </BoxAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

다음도 서로 분리된 네트워크 2개입니다. <ItemLink id="quartz_fiber" />는 [에너지](../ae2-mechanics/energy.md)를
공유하지만 네트워크 연결은 제공하지 않기 때문입니다.

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/2_networks_2.snbt" />

  <BoxAnnotation color="#915dcd" min="0 0 0" max="1 2 2">
        네트워크 1
  </BoxAnnotation>

  <BoxAnnotation color="#5CA7CD" min="1.3 0 0" max="3 2 2">
        네트워크 2
  </BoxAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

하지만 다음은 두 개가 아니라 하나의 네트워크입니다. [양자 연결기](../items-blocks-machines/quantum_bridge.md)는
무선 [조밀 케이블](../items-blocks-machines/cables.md#dense-cable)처럼 작동하므로 양쪽 끝이 같은 네트워크에
속합니다.

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/actually_1_network.snbt" />

  <BoxAnnotation color="#915dcd" min="0 0 0" max="7 3 3">
        모두 하나의 네트워크
  </BoxAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

다음 역시 하나의 네트워크입니다. 서로 다른 색의 케이블끼리 연결되지 않는다는 점을 제외하면
[케이블](../items-blocks-machines/cables.md) 색상은 네트워크 연결에 영향을 주지 않습니다. 모든 색상은
플루익스 케이블, 즉 "무색" 케이블과 연결됩니다.

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/actually_1_network_2.snbt" />

  <BoxAnnotation color="#915dcd" min="0 0 0" max="4 2 2">
        모두 하나의 네트워크
  </BoxAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 서브네트워크에서의 연결

[서브네트워크](../ae2-mechanics/subnetworks.md)는 네트워크 연결, 특히 서로 **연결되지 않은 상태**를
활용하여 [장치](../ae2-mechanics/devices.md)가 접근할 수 있는 다른 장치를 제한합니다.

사실 서브네트워크란 그저 분리된 네트워크입니다.

[자동 행운 광석 처리기](../example-setups/ore-fortuner.md)를 예로 들어 보겠습니다. 이 구성에는 서로
분리된 네트워크 3개가 있으며 각각 특정한 역할을 맡습니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/ore_fortuner.snbt" />

  <BoxAnnotation color="#915dcd" min="0 0 2" max="3 1 3">
        네트워크 1은 파이프 서브네트워크처럼 작동합니다. 반입 버스가 접근할 수 있는 대상을 제한하여
        형성 평면을 통해 광석 블록을 "저장"하게 합니다.
  </BoxAnnotation>

  <BoxAnnotation color="#5CA7CD" min="0 0 0" max="3 1 1">
        네트워크 2는 또 다른 파이프 서브네트워크처럼 작동합니다. 소멸 평면이 접근할 수 있는 대상을
        제한하여 행운으로 늘어난 광석 조각을 주 네트워크가 아닌 통에 저장합니다. 주 네트워크의 채널도
        사용하지 않습니다.
  </BoxAnnotation>

  <BoxAnnotation color="#82CD5C" min="2 0 1" max="4 1 2">
        네트워크 3은 모든 저장소와 제작 기능이 있는 주 네트워크입니다. 실제로는 전력을 공급하기 위해
        있을 뿐이며, 두 서브네트워크와는 의도적으로 연결되지 않았습니다.
  </BoxAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## P2P에서의 연결

[P2P 터널](../items-blocks-machines/p2p_tunnels.md) 중 한 종류는 아이템, 유체 또는 레드스톤 신호 대신
[채널](channels.md)을 운반하는데, 이 때문에 혼동하기 쉽습니다. 터널이 설치된 네트워크와 터널이 운반하는
네트워크는 서로 관계가 없습니다. 같은 네트워크일 수도 있지만 그럴 필요는 없으며, 보통은 서로 다릅니다.

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/p2p_channels_network_connection.snbt" />

  <BoxAnnotation color="#915dcd" min="0 0 0" max="1.98 2 1">
        네트워크 1, 운반되는 네트워크이며 보통 주 네트워크입니다.
  </BoxAnnotation>

  <BoxAnnotation color="#5CA7CD" min="2.02 0 0" max="3.98 1 1">
        네트워크 2, ME P2P 터널을 작동시키는 네트워크이며 보통 주 네트워크가 아닙니다.
  </BoxAnnotation>

  <BoxAnnotation color="#915dcd" min="4.02 0 0" max="6 1 1">
        네트워크 1, 운반되는 네트워크이며 보통 주 네트워크입니다.
  </BoxAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 직관적이지 않은 연결

다음 구성은 하나의 네트워크입니다. 완전한 블록 형태의 장치인 <ItemLink id="pattern_provider" />가
케이블처럼 작동하고 <ItemLink id="inscriber" />도 비슷하게 작동하기 때문입니다. 네트워크 연결이 패턴
공급기와 각인기를 통과합니다.

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/pattern_provider_network_connection_1.snbt" />

  <BoxAnnotation color="#915dcd" min="0 0 0" max="4 2 2">
        모두 하나의 네트워크
  </BoxAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

[서브네트워크](../ae2-mechanics/subnetworks.md)를 사용하는 자동 제작 구성 등에서 이 연결을 막으려면
<ItemLink id="certus_quartz_wrench" />로 패턴 공급기를 우클릭해 방향성을 부여하세요. 그러면 한쪽
면으로 채널을 전달하지 않습니다.

<Row gap="40">
<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/pattern_provider_network_connection_2.snbt" />

  <BoxAnnotation color="#915dcd" min="0 0 0" max="1.98 2 2">
        네트워크 1
  </BoxAnnotation>

  <BoxAnnotation color="#5CA7CD" min="2.02 0 0" max="4 2 2">
        네트워크 2
  </BoxAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/pattern_provider_directional_connection.snbt" />

  <BoxAnnotation color="#ee3333" min="1 .3 .3" max="1.3 .7 .7">
        케이블이 연결되지 않는 모습에 주목하세요.
  </BoxAnnotation>

  <IsometricCamera yaw="255" pitch="30" />
</GameScene>
</Row>

방향성 네트워크 연결을 제공하지 않는 다른 부품으로는 <ItemLink id="import_bus" />,
<ItemLink id="storage_bus" />, <ItemLink id="cable_interface" />처럼 대부분의
[케이블 부품](../ae2-mechanics/cable-subparts.md) [장치](../ae2-mechanics/devices.md)가 있습니다.

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/subpart_no_connection.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>
