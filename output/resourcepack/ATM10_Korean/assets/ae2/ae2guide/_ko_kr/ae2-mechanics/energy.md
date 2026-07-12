---
navigation:
  parent: ae2-mechanics/ae2-mechanics-index.md
  title: 에너지
  icon: energy_cell
---

# 에너지

네트워크가 작동하려면 에너지가 필요합니다. 네트워크에는 [장치](../ae2-mechanics/devices.md)가 직접
사용하는 공동 에너지 저장고가 있으며, <ItemLink id="vibration_chamber" />와
<ItemLink id="energy_acceptor" />, 그리고 <ItemLink id="controller" />가 에너지를 공급합니다.
<ItemLink id="network_tool" />로 네트워크의 아무 곳이나 우클릭하거나, 제어기가 있다면 제어기를
우클릭하여 네트워크 에너지 통계를 볼 수 있습니다. 네트워크 전체가 에너지를 함께 저장하고 분배하므로
전송 속도 제한이 없습니다. 장치는 필요한 만큼 높은 속도로 에너지를 가져갈 수 있고, 에너지 수용기도
에너지 저장 용량만 허용한다면 사실상 제한 없는 속도로 에너지를 받을 수 있습니다.

## 에너지 받기

<Row>
  <BlockImage id="energy_acceptor" scale="4" />

  <GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/blocks/cable_energy_acceptor.snbt" />
  </GameScene>

  <BlockImage id="controller" p:state="online" scale="4" />

  <BlockImage id="vibration_chamber" p:active="true" scale="4" />
  
  <BlockImage id="crystal_resonance_generator" scale="4" />
</Row>

AE2는 내부적으로 Forge의 Forge Energy나 Fabric의 TechReborn Energy를 사용하지 않습니다. 대신 이들을
자체 단위인 AE로 변환합니다. 변환은 한 방향으로만 가능합니다. <ItemLink id="energy_acceptor" />와
<ItemLink id="controller" />가 에너지를 변환할 수 있지만, 제어기의 면은 더 많은
[채널](../ae2-mechanics/channels.md)을 연결하는 데 쓰는 편이 좋습니다. <ItemLink id="vibration_chamber" />로
직접 생산하거나 <ItemLink id="crystal_resonance_generator" />로 수동 공급 없이 생산할 수도 있습니다.
다만 AE2는 더 좋은 발전 기능을 가진 다른 기술 모드와 함께 사용하도록 설계되었습니다.

따라서 기지의 에너지 분배 구조를 설계할 때는 AE2 네트워크 전체를 하나의 거대한 다중 블록 기계로
생각하는 것이 좋습니다.

Forge Energy와 TechReborn Energy의 변환 비율은 다음과 같습니다.

*   2 FE = 1 AE (Forge 환경)
*   1 E  = 2 AE (Fabric 환경)

## 에너지 저장

<Row>
  <BlockImage id="energy_cell" scale="4" p:fullness="4" />

  <BlockImage id="dense_energy_cell" scale="4" p:fullness="4" />

  <BlockImage id="creative_energy_cell" scale="4" />
</Row>

당연한 이유로, 네트워크는 한 게임 틱에 저장할 수 있는 양보다 많은 에너지를 받거나 소비할 수 없습니다.
네트워크가 800 AE만 저장할 수 있다면 [장치](../ae2-mechanics/devices.md)가 에너지를 요청해도 저장고가
가득 찬 상태에서 최대 800 AE까지만 사용할 수 있습니다. 저장고가 비어 있어도 에너지 수용기가 한 번에
네트워크로 넣을 수 있는 양 역시 최대 800 AE입니다.

이 때문에 이상하게 보이는 동작이 자주 발생합니다. 에너지 수용기, ME 드라이브, 터미널과 몇몇 장치만
있는 작은 네트워크에 인벤토리를 가득 채운 조약돌을 한꺼번에 넣는 경우가 그 예입니다. 조약돌을 한 게임
틱에 모두 넣으려면 네트워크 저장량보다 많은 에너지가 필요합니다. 결국 일부 조약돌만 들어가고 네트워크의
에너지가 바닥나 재부팅됩니다.

**에너지 셀을 추가하면 이 문제를 해결할 수 있습니다.**

네트워크는 케이블, 기계 또는 부품 하나당 25 AE의 기본 에너지 버퍼를 가집니다.

<ItemLink id="controller" />에는 8,000 AE의 작은 내부 에너지 저장소가 있습니다.

<ItemLink id="energy_cell" />은 200k AE를 저장합니다. 일반적인 네트워크 사용 중 발생하는 순간적인
전력 증가를 충분히 감당하므로 대부분은 하나만 있어도 됩니다.

<ItemLink id="dense_energy_cell" />은 1.6M AE를 저장합니다. 저장된 전력만으로 네트워크를 가동하거나
대규모 [공간 저장소](spatial-io.md)가 순간적으로 소비하는 막대한 에너지를 감당할 때 사용합니다.

<ItemLink id="creative_energy_cell" />은 시험용 크리에이티브 아이템으로, 무한한 전력을 제공합니다.
