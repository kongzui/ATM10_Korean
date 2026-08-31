---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: ME 제어기
  icon: controller
  position: 110
categories:
- network infrastructure
item_ids:
- ae2:controller
---

# ME 제어기

<BlockImage id="controller" p:state="online" scale="8" />

ME 제어기는 [ME 네트워크](../ae2-mechanics/me-network-connections.md)의 경로 지정 중심입니다.
제어기가 없는 네트워크는 "임시 네트워크"가 되어 채널을 사용하는 [장치](../ae2-mechanics/devices.md)를 총 8개까지만 둘 수 있습니다.

하나의 [ME 네트워크](../ae2-mechanics/me-network-connections.md)에 제어기 2개를 둘 수 없습니다.

제어기는 각 면마다 32개의 [채널](../ae2-mechanics/channels.md)을 제공합니다.

제어기 블록 하나가 작동하려면 6 AE/t가 필요합니다. 각 제어기 블록은 8,000 AE를 저장하므로
대규모 네트워크에는 추가 에너지 저장소가 필요할 수 있습니다. 자세한 내용은 [에너지](../ae2-mechanics/energy.md)를 참고하세요.

다중 블록 제어기는 상당히 자유로운 형태로 만들 수 있습니다.

<GameScene zoom="2" background="transparent">
  <ImportStructure src="../assets/assemblies/controllers.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

다만 다음 규칙을 따라야 합니다.

1.  [ME 네트워크](../ae2-mechanics/me-network-connections.md)의 모든 제어기 블록은 서로 연결되어야 합니다. 그렇지 않으면 빨간색으로 변합니다.
2.  제어기의 크기는 7x7x7 이하여야 합니다. 그보다 크면 빨간색으로 변합니다.
3.  제어기 블록은 최대 한 축에서만 양쪽에 블록이 인접할 수 있습니다. 이 규칙을 어기면 비활성화되어 빨간색으로 변합니다.

<GameScene zoom="2" background="transparent">
  <ImportStructure src="../assets/assemblies/controller_rules.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

모든 규칙을 지키고 전력을 공급하면 제어기가 빛나며 색상이 순환합니다.

제어기를 우클릭하면 <ItemLink id="network_tool" />와 같은 GUI가 열립니다.

## 조합법

<RecipeFor id="controller" />
