---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: P2P 터널
  icon: me_p2p_tunnel
  position: 210
categories:
- devices
item_ids:
- ae2:me_p2p_tunnel
- ae2:redstone_p2p_tunnel
- ae2:item_p2p_tunnel
- ae2:fluid_p2p_tunnel
- ae2:fe_p2p_tunnel
- ae2:light_p2p_tunnel
---

# P2P 터널

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/p2p_tunnels.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

P2P 터널은 아이템, 유체, 레드스톤 신호, 전력, 빛, [채널](../ae2-mechanics/channels.md) 등을 네트워크와 직접 상호작용시키지 않고
네트워크 주변으로 옮기는 방법입니다. 여러 변형이 있지만 각 터널은 지정된 한 종류만 운반합니다.
멀리 떨어진 두 블록 면을 직접 잇는 포털처럼 작동합니다. 양방향이 아니며 입력과 출력이 정해져 있습니다.

![포털](../assets/assemblies/p2p_portal.png)

예를 들어 아이템 P2P를 향한 호퍼는 통에 직접 연결된 것처럼 작동하여 아이템이 흐릅니다.

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/p2p_hopper_barrel.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

하지만 서로 붙어 있는 통 두 개 사이에서는 아이템이 이동하지 않습니다.

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/p2p_barrel_barrel.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

레드스톤 P2P 같은 다른 변형도 있습니다.

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/p2p_redstone.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

ME P2P는 채널을 옮깁니다.

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/p2p_channels.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## P2P 터널 종류와 조율

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/p2p_tunnels.snbt" />
  <IsometricCamera yaw="180" pitch="90" />
</GameScene>

P2P 터널에는 여러 종류가 있습니다. ME P2P 터널만 직접 제작할 수 있으며, 나머지는 P2P 터널을 특정 아이템으로 우클릭해 만듭니다.
- ME P2P 터널은 아무 [케이블](../items-blocks-machines/cables.md)로 우클릭해 조율합니다.
- 레드스톤 P2P 터널은 여러 레드스톤 부품으로 우클릭해 조율합니다.
- 아이템 P2P 터널은 상자나 호퍼로 우클릭해 조율합니다.
- 유체 P2P 터널은 양동이나 병으로 우클릭해 조율합니다.
- 에너지 P2P 터널은 에너지가 든 거의 모든 아이템으로 우클릭해 조율합니다.
- 빛 P2P 터널은 횃불이나 발광석으로 우클릭해 조율합니다.

일부 터널 종류에는 특이점이 있습니다. ME P2P 터널의 채널은 다른 ME P2P 터널을 통과할 수 없습니다.
에너지 P2P 터널은 자체 [에너지](../ae2-mechanics/energy.md) 소비량을 늘리는 방식으로 통과하는 FE의 2.5%를 간접적으로 소모합니다.

## 가장 흔한 P2P 사용법

P2P 터널의 가장 흔한 용도는 ME P2P 터널로 [채널](../ae2-mechanics/channels.md) 전송 밀도를 압축하는 것입니다.
조밀한 케이블을 여러 줄 묶는 대신 한 줄로 많은 채널을 운반할 수 있습니다.

이 예에서는 ME P2P 입력 8개가 주 네트워크의 <ItemLink id="controller" />에서 채널 256개(8*32)를 받아,
ME P2P 출력 8개가 다른 곳으로 내보냅니다. 각 P2P 터널 입력 또는 출력이 채널 1개를 사용한다는 점에 주목하세요.
따라서 가는 케이블로 많은 채널을 보낼 수 있습니다. P2P 터널이 전용 [서브네트워크](../ae2-mechanics/subnetworks.md)에 있으므로
이 작업에 주 네트워크의 채널은 전혀 사용하지 않습니다! P2P 터널을 제어기에 직접 붙일 수도 있지만,
사이에 [조밀한 스마트 케이블](../items-blocks-machines/cables.md#smart-cable)을 놓으면 채널을 더 쉽게 시각화할 수 있습니다.

<GameScene zoom="4" interactive={true}>
  <ImportStructure src="../assets/assemblies/p2p_compact_channels.snbt" />

  <BoxAnnotation color="#dddddd" min="1.3 1.3 6.3" max="2 2.7 6.7">
        석영 섬유가 주 네트워크와 P2P 서브네트워크 사이에 에너지를 공유합니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="4.1 0 5.7" max="5 2.3 6.4">
        터널 입력을 제어기에 직접 붙이거나 케이블로 연결할 수 있습니다.
  </BoxAnnotation>

  <IsometricCamera yaw="225" pitch="30" />
</GameScene>

다른 예시([양자 브리지](quantum_bridge.md)와 함께 사용하는 경우 포함)는 미처 다듬지 못한 이 그림판 도식을 참고하세요.

![P2P와 양자 브리지](../assets/diagrams/p2p_quantum_network.png)

## 중첩

하지만 이 방식으로 케이블 하나에 무한한 채널을 보낼 수는 없습니다. ME P2P 터널의 채널은 다른 ME P2P 터널을 통과하지 않으므로
재귀적으로 중첩할 수 없습니다. 빨간 케이블 바깥쪽의 ME P2P 터널이 오프라인인 것을 확인하세요.
이는 ME P2P 터널에만 적용됩니다. 레드스톤 P2P 터널이 정상 작동하는 것처럼 다른 종류의 P2P 터널은 ME P2P 터널을 통과할 수 있습니다.

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/p2p_nesting.snbt" />
  <IsometricCamera yaw="225" pitch="30" />
</GameScene>

## 연결

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/p2p_linking_frequency.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

P2P 터널 연결의 양 끝은 <ItemLink id="memory_card" />로 연결할 수 있습니다. 주파수는 터널 뒷면에 2x2 색상 배열로 표시됩니다.
- Shift+우클릭하면 새 P2P 연결 주파수를 생성합니다.
- 우클릭하면 설정, 업그레이드 카드 또는 연결 주파수를 붙여 넣습니다.

Shift+우클릭한 터널이 입력이 되고 우클릭한 터널이 출력이 됩니다. 출력은 여러 개 둘 수 있지만,
ME P2P 터널에서는 입력으로 들어온 채널이 출력 사이에 나뉘므로 채널을 복제할 수 없습니다.

## 조합법

<RecipeFor id="me_p2p_tunnel" />
