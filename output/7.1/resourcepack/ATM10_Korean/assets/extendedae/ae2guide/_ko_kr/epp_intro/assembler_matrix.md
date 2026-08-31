---
navigation:
  parent: epp_intro/epp_intro-index.md
  title: 조립기 매트릭스
  icon: extendedae:assembler_matrix_frame
categories:
- extended devices
item_ids:
- extendedae:assembler_matrix_frame
- extendedae:assembler_matrix_wall
- extendedae:assembler_matrix_glass
- extendedae:assembler_matrix_pattern
- extendedae:assembler_matrix_crafter
- extendedae:assembler_matrix_speed
---

# 조립기 매트릭스

<Row>
<BlockImage id="extendedae:assembler_matrix_frame" p:formed="true" p:powered="true" scale="5"></BlockImage>
<BlockImage id="extendedae:assembler_matrix_wall" scale="5"></BlockImage>
<BlockImage id="extendedae:assembler_matrix_glass" scale="5"></BlockImage>
</Row>
<Row>
<BlockImage id="extendedae:assembler_matrix_pattern" scale="5"></BlockImage>
<BlockImage id="extendedae:assembler_matrix_crafter" scale="5"></BlockImage>
<BlockImage id="extendedae:assembler_matrix_speed" scale="5"></BlockImage>
</Row>

조립기 매트릭스는 <ItemLink id="ae2:molecular_assembler" />와 <ItemLink id="ae2:pattern_provider" />를 합친 멀티블록 구조물입니다.
ME 네트워크에 <ItemLink id="ae2:crafting_accelerator" />가 충분하다면 많은 제작 작업을 동시에 실행하면서 채널도 절약할 수 있습니다.

## 구조

<GameScene zoom="3" background="transparent" interactive={true}>
  <ImportStructure src="../structure/assembler_matrix.snbt"></ImportStructure>
</GameScene>

각 모서리 길이가 3에서 7 사이인 직육면체입니다.
- 모서리는 조립기 매트릭스 프레임으로 구성합니다.
- 면은 조립기 매트릭스 벽 또는 유리로 구성합니다.
- 내부는 조립기 매트릭스 패턴/제작/가속 코어로 구성합니다.

올바른 조립기 매트릭스에는 패턴 코어와 제작 코어가 각각 하나 이상 있어야 합니다.
내부를 빈틈없이 채워야 하며, 속이 비어 있으면 안 됩니다.
조립기 매트릭스가 올바르게 형성되고 전력을 공급받으면 조립기 매트릭스 프레임의 선이 파란색으로 바뀝니다.

## 조립기 매트릭스 코어

조립기 매트릭스 코어는 3종류입니다.

- 조립기 매트릭스 패턴 코어

조립기 매트릭스는 패턴 코어에서만 패턴을 가져옵니다. 패턴 코어 하나마다 조립기 매트릭스에 패턴 슬롯 36개가 추가됩니다.

- 조립기 매트릭스 제작 코어

조립기 매트릭스는 받은 제작 작업을 제작 코어에 할당합니다. 제작 코어 하나마다 제작 작업을 8개까지 동시에 실행할 수 있습니다.

- 조립기 매트릭스 가속 코어

조립기 매트릭스에서 <ItemLink id="ae2:speed_card" /> 역할을 합니다. 가속 코어 5개를 설치하면 조립기 매트릭스가 최고 속도로 작동합니다.
가속 코어를 5개보다 많이 설치해도 속도는 더 빨라지지 않습니다.

## GUI

형성되어 온라인 상태인 조립기 매트릭스를 오른쪽 클릭하면 GUI가 열립니다.

![GUI](../pic/assembler_matrix.png)

패턴을 넣거나 검색하고, 현재 실행 중인 제작 작업 수를 확인할 수 있습니다.
