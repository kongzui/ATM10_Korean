---
navigation:
  parent: ae2-mechanics/ae2-mechanics-index.md
  title: 공간 I/O
  icon: spatial_storage_cell_2
---

# 공간 I/O

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/spatial_storage_1x1x1.snbt" />

  <BoxAnnotation color="#33dd33" min="1 1 1" max="2 2 2">
        이동할 공간
  </BoxAnnotation>

  <IsometricCamera yaw="195" pitch="30" />

</GameScene>

공간 I/O는 월드의 물리적인 공간을 잘라내어 붙이는 기능입니다. <ItemLink id="flawless_budding_quartz" />을
옮기거나, 기지의 방 내부를 여러 형태로 바꿔 끼워 다른 용도로 사용하거나, 엔드 차원문까지 옮길 수 있습니다.

지정한 공간과 공간 저장소 차원의 같은 크기 공간을 서로 *교환*하는 방식으로 작동합니다. 공간 지시탑 배열
안에 있던 것은 공간 저장소 차원으로 보내고, 해당 차원에 있던 것은 공간 지시탑 배열 안으로 가져옵니다.

차원 사이를 이동할 방법이 있다면 사용자 지정 크기의 소형 기계나 포켓 차원처럼 사용할 수도 있습니다.
공간 I/O 자체로 순간 이동 장치를 만들 수는 있지만, 매우 복잡하고 다소 불안정해 이 가이드에서는 다루지
않습니다.

# 다중 블록 구성

공간 I/O가 작동하고 잘라 붙일 공간을 정의하려면 구성 요소를 정해진 방식으로 배치해야 합니다.

모든 구성 요소가 같은 [네트워크](me-network-connections.md)에 있어야 하며, 한 네트워크에는 공간 I/O
구성을 하나만 둘 수 있습니다. 따라서 [서브네트워크](subnetworks.md)를 사용하는 것이 좋습니다.

## 공간 I/O 포트

<BlockImage id="spatial_io_port" p:powered="true" scale="4" />

<ItemLink id="spatial_io_port" />는 공간 I/O 작업을 제어합니다. 다중 블록 구성의 통계를 보여 주며
[공간 셀](../items-blocks-machines/spatial_cells.md)을 보관합니다.

표시되는 정보는 다음과 같습니다.
- 네트워크에 저장된 [에너지](energy.md)와 최대 에너지
- 작업에 필요한 에너지. 매우 클 수 있고 한순간에 사용되므로 전부 저장할 만큼 충분한
  [에너지 셀](../items-blocks-machines/energy_cells.md)을 준비해야 합니다.
- 공간 지시탑 배열의 효율
- 지정된 공간의 크기

공간 I/O 작업을 수행하려면 입력 슬롯에 공간 저장 셀을 넣고 공간 I/O 포트에 레드스톤 펄스를 주세요.
공간 지시탑 안의 공간과 공간 저장소 차원의 공간이 서로 *교환*됩니다. 블록 묶음 하나를 공간 저장소 차원으로
보낸 다음 공간 지시탑 안에 다른 블록 묶음을 놓고 셀을 입력 슬롯에 다시 넣어 I/O 포트를 작동시키면, 두 번째
블록 묶음은 사라지고 첫 번째 블록 묶음이 다시 나타납니다.

**주의하세요. 지정한 공간 안에 있는 모든 개체는 플레이어를 포함해 함께 이동합니다. 빠져나올 방법이
없다면 어둡고 아무것도 없는 상자 같은 공간 저장소 차원에 갇힙니다.** 친구를 놀리는 데 활용해 보세요!

## 공간 지시탑

<BlockImage id="spatial_pylon" p:powered_on="true" scale="4" />

<ItemLink id="spatial_pylon" />은 공간 I/O 구성의 주요 부품으로, 영향을 받을 공간을 정의합니다.

공간 지시탑 바깥쪽을 둘러싼 경계 상자에서 모든 방향으로 한 블록씩 안쪽으로 줄인 범위가 실제 공간입니다.

규칙은 다음과 같습니다.
- 최소 크기는 3x3x3이며, 이때 1x1x1 공간을 정의합니다.
- 모든 공간 지시탑은 바깥쪽 경계 상자 위에 있어야 합니다.
- 모든 공간 지시탑은 같은 네트워크에 있어야 합니다.
- 모든 공간 지시탑은 최소 두 블록 길이여야 합니다.

예를 들어 3x3x3 공간을 정의하려면 두 번째 규칙에 따라 모든 공간 지시탑이 지정할 공간 주변의 5x5x5 껍질
안에 있어야 합니다. 한 블록 두께의 5x5x5 껍질 안에 포함되기만 하면 거의 어떤 형태로든 배치할 수 있습니다.

<GameScene zoom="4" interactive={true}>
<ImportStructure src="../assets/assemblies/spatial_storage_3x3x3_pylon_demonstration.snbt" />

<BoxAnnotation color="#33dd33" min="1 1 1" max="4 4 4">
        이동할 공간
  </BoxAnnotation>

<BoxAnnotation color="#3333ff" min="5 5 0" max="0 0 5">
  </BoxAnnotation>

<IsometricCamera yaw="195" pitch="30" />
</GameScene>

다음은 더 합리적인 구성입니다.

<GameScene zoom="4" interactive={true}>
<ImportStructure src="../assets/assemblies/better_spatial_storage_3x3x3.snbt" />

<BoxAnnotation color="#33dd33" min="1 1 1" max="4 4 4">
        이동할 공간
  </BoxAnnotation>

<BoxAnnotation color="#3333ff" min="5 5 0" max="0 0 5">
  </BoxAnnotation>

<IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 효율

공간 지시탑 배열의 효율은 껍질을 얼마나 많이 채웠는지에 따라 달라집니다. 큰 공간 주변에 최소한의 공간 지시탑만
놓으면 효율이 매우 낮아져 수십억 AE가 필요할 수도 있습니다.

## 셀 크기

[공간 셀](../items-blocks-machines/spatial_cells.md)은 한 번 사용하면 XYZ 크기, 예를 들어 3x4x2가 영구히
정해지고 공간 저장소 차원의 공간 하나와 연결됩니다. **한 번 사용한 공간 셀은 초기화, 재포맷 또는 크기
변경을 할 수 없습니다.** 다른 크기가 필요하면 새 셀을 만드세요.

이 크기는 셀 이름의 크기와 같다는 뜻이 아닙니다. 16^3 셀은 최대 16x16x16 이내에서 어떤 크기든
사용할 수 있습니다.

공간에는 방향이 있어 회전할 수 없습니다. 2x2x3과 3x2x2는 전체 크기가 같아도 서로 다른 공간입니다.

셀의 XYZ 크기가 I/O 포트에 표시되는 지정 공간과 일치하지 않으면 I/O 포트가 작동하지 않습니다.
