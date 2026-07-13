---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 양자 네트워크 브리지
  icon: quantum_ring
  position: 110
categories:
- network infrastructure
item_ids:
- ae2:quantum_link
- ae2:quantum_ring
---

# 양자 네트워크 브리지

![완성된 양자 네트워크 브리지](../assets/diagrams/quantum_bridge_demonstration.png)

양자 네트워크 브리지는 [네트워크](../ae2-mechanics/me-network-connections.md)를 무한한 거리, 심지어 차원 사이로 확장할 수 있습니다.
케이블이 각 면에 어떻게 연결되었는지와 관계없이 총 32개 채널을 전달하므로, 사실상 무선 [조밀한 케이블](cables.md#dense-cable)처럼 작동합니다.

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/quantum_bridge_internal_structure_1.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/quantum_bridge_internal_structure_2.snbt" />

  <BoxAnnotation color="#33dd33" min="1 1 1" max="6 2 3">
        두 끝점을 잇는 가상의 케이블
  </BoxAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

중요하게도 **양쪽 모두 청크 로딩되어야 합니다.** 두 지점이 멀리 떨어져 있다면 <ItemLink id="spatial_anchor" />나
다른 청크 로더를 사용해야 합니다.

# ME 양자 고리

<BlockImage id="quantum_ring" scale="8" />

이 블록 8개를 <ItemLink id="quantum_link" /> 주위에 놓으면 양자 네트워크 브리지가 만들어집니다.
<ItemLink id="quantum_ring" /> 4개 중 <ItemLink id="quantum_link" />에 인접한 블록만 네트워크 연결을 받으며,
모서리의 4개 블록에는 케이블을 연결할 수 없습니다.

## 조합법

<RecipeFor id="quantum_ring" />

# ME 양자 연결기

<BlockImage id="quantum_link" scale="8" />

이 블록 하나를 <ItemLink id="quantum_ring" />으로 둘러싸면 양자 네트워크 브리지가 만들어집니다.
이 블록에는 케이블을 연결할 수 없으며 완전한 브리지가 만들어져야 네트워크의 일부로 등록됩니다.

이 블록의 인벤토리에는 <ItemLink id="quantum_entangled_singularity" /> 하나만 들어가며 자동화 장치로 접근할 수 있습니다.

## 조합법

<RecipeFor id="quantum_link" />
