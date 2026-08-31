---
navigation:
  parent: example-setups/example-setups-index.md
  title: 화로 자동화
  icon: minecraft:furnace
---

# 화로 자동화

이 구성은 <ItemLink id="pattern_provider" />를 사용하므로 [자동 제작](../ae2-mechanics/autocrafting.md)
설비에 통합하기 위한 것입니다. 화로 하나만 자동화하려면 호퍼와 상자 등을 사용하세요.

<ItemLink id="minecraft:furnace" /> 자동화는 [충전기](../example-setups/charger-automation.md)처럼 단순한 기계의
자동화보다 조금 복잡합니다. 화로는 서로 다른 두 면으로 재료를 넣고, 세 번째 면으로 결과물을 꺼내야 합니다.
제련할 아이템은 윗면, 연료는 옆면으로 넣고 결과물은 밑면으로 꺼내야 합니다.

윗면에 <ItemLink id="pattern_provider" />, 옆면에 연료를 계속 넣는 <ItemLink id="export_bus" />,
밑면에 결과물을 네트워크로 가져오는 <ItemLink id="import_bus" />를 붙일 수도 있습니다.
하지만 이 방법은 [채널](../ae2-mechanics/channels.md) 3개를 사용합니다.

채널 하나만 사용하는 방법은 다음과 같습니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/furnace_automation.snbt" />

<BoxAnnotation color="#dddddd" min="1 0 0" max="2 1 1">
        (1) 패턴 공급기: 서투스 석영 렌치를 사용해 방향을 지정했으며, 관련 가공 패턴이 들어 있습니다.

        ![철 패턴](../assets/diagrams/furnace_pattern_small.png)
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 1 0" max="2 1.3 1">
        (2) 인터페이스: 기본 설정입니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 1 0" max="1.3 2 1">
        (3) 저장 버스 #1: 석탄으로 필터링했습니다.
        <ItemImage id="minecraft:coal" scale="2" />
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="0 2 0" max="1 2.3 1">
        (4) 저장 버스 #2: 반전 카드를 사용해 석탄을 블랙리스트로 지정했습니다.
        <Row><ItemImage id="minecraft:coal" scale="2" /><ItemImage id="inverter_card" scale="2" /></Row>
  </BoxAnnotation>

<DiamondAnnotation pos="4 0.5 0.5" color="#00ff00">
        주 네트워크로
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 설정

* <ItemLink id="pattern_provider" /> (1)는 관련 <ItemLink id="processing_pattern" />을 넣은 기본 설정입니다.
  <ItemLink id="certus_quartz_wrench" />를 사용해 방향을 지정했습니다.

  ![철 패턴](../assets/diagrams/furnace_pattern.png)

* <ItemLink id="interface" /> (2)는 기본 설정입니다.
* 첫 번째 <ItemLink id="storage_bus" /> (3)은 석탄 또는 사용할 연료로 필터링했습니다.
* 두 번째 <ItemLink id="storage_bus" /> (4)는 <ItemLink id="inverter_card" />를 사용해 사용할 연료를 블랙리스트로 지정했습니다.

## 작동 원리

1. <ItemLink id="pattern_provider" />가 재료를 <ItemLink id="interface" />에 넣습니다.
   (실제로는 최적화를 위해 저장 버스를 공급기 면의 연장처럼 취급하여 곧바로 통과시킵니다. 아이템은 인터페이스 안에 들어가지 않습니다.)
2. 인터페이스는 아무것도 비축하지 않도록 설정되어 있으므로 재료를 [네트워크 저장소](../ae2-mechanics/import-export-storage.md)에 넣으려 합니다.
3. 초록색 서브네트워크의 유일한 저장소는 <ItemLink id="storage_bus" />들입니다. 석탄으로 필터링한 버스는 옆면을 통해 화로의 연료 칸에 석탄을 넣습니다.
   석탄이 아닌 것으로 필터링한 버스는 윗면을 통해 제련할 아이템을 위쪽 칸에 넣습니다.
4. 화로가 아이템을 제련합니다.
5. 호퍼가 화로 밑면에서 결과물을 꺼내 공급기의 반환 칸에 넣어 주 네트워크로 되돌립니다.
