---
navigation:
  parent: example-setups/example-setups-index.md
  title: 프로세서 자동화
  icon: logic_processor
---

# 프로세서 생산 자동화

[프로세서](../items-blocks-machines/processors.md)를 자동화하는 방법은 많으며, 이것은 그중 하나입니다.

필터링할 수만 있다면 다른 모드에서 무엇이라 부르든 아이템 물류 파이프·도관·덕트로도 이 일반적인 배치를 만들 수 있습니다.

![공정 흐름도](../assets/diagrams/processor_flow_diagram.png)

여기서는 ["파이프" 서브넷](pipe-subnet.md)을 사용해 AE2만으로 만드는 자세한 방법을 설명합니다.

이 구성은 <ItemLink id="pattern_provider" />를 사용하므로 [자동 제작](../ae2-mechanics/autocrafting.md)
설비에 통합하기 위한 것입니다. 프로세서만 따로 자동화하려면 패턴 공급기를 다른 통으로 바꾸고 위쪽 통에 재료를 직접 넣으세요.

이 구성은 이전 AE2 버전과도 호환됩니다. <ItemLink id="inscriber" />에 면별 입출력 제한이 있더라도
파이프 서브넷이 올바른 면으로 넣고 꺼내기 때문입니다.

## 패턴 인코딩에서 배울 점

필요한 [패턴](../items-blocks-machines/patterns.md)은 종종 **JEI에 보이는 것 또는 + 버튼을 눌렀을 때 JEI가 만드는 것과 다릅니다**.
이 경우 JEI는 인쇄된 부품용과 최종 조립용 패턴을 따로 만들며, 인쇄된 부품 패턴에는
[압형](../items-blocks-machines/presses.md)도 포함합니다. 하지만 설비가 그렇게 작동하지 않으므로 원하는 패턴이 아닙니다.
원재료를 입력해 완성된 프로세서를 출력하는 패턴 하나가 필요하며, 압형은 이미 회로 인쇄기 안에 있으므로 패턴에 넣지 않아야 합니다.

---

<GameScene zoom="4" interactive={true}>
  <ImportStructure src="../assets/assemblies/processor_automation.snbt" />

  <BoxAnnotation color="#dddddd" min="5 1 0" max="6 2 1" thickness=".05">
        (1) 패턴 공급기: 관련 가공 패턴을 넣은 기본 설정입니다.

        <Row>
            ![논리 패턴](../assets/diagrams/logic_pattern_small.png)
            ![연산 패턴](../assets/diagrams/calculation_pattern_small.png)
            ![엔지니어링 패턴](../assets/diagrams/engineering_pattern_small.png)
        </Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="4.7 2 0" max="5 3 1" thickness=".05">
        (2) 저장 버스 #1: 기본 설정입니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="4 1 0" max="4.3 2 1" thickness=".05">
        (3) 반출 버스 #1: 실리콘으로 필터링했으며 가속 카드가 2장 있습니다.
        <Row><ItemImage id="silicon" scale="2" /> <ItemImage id="speed_card" scale="2" /></Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="4 4 0" max="4.3 3 1" thickness=".05">
        (4) 반출 버스 #2: 금괴로 필터링했으며 가속 카드가 2장 있습니다.
        <Row><ItemImage id="minecraft:gold_ingot" scale="2" /> <ItemImage id="speed_card" scale="2" /></Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="4 5 0" max="4.3 4 1" thickness=".05">
        (5) 반출 버스 #3: 서투스 석영 수정으로 필터링했으며 가속 카드가 2장 있습니다.
        <Row><ItemImage id="certus_quartz_crystal" scale="2" /> <ItemImage id="speed_card" scale="2" /></Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="4 6 0" max="4.3 5 1" thickness=".05">
        (6) 반출 버스 #4: 다이아몬드로 필터링했으며 가속 카드가 2장 있습니다.
        <Row><ItemImage id="minecraft:diamond" scale="2" /> <ItemImage id="speed_card" scale="2" /></Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2.3 3 0" max="2 2 1" thickness=".05">
        (7) 반출 버스 #5: 레드스톤 가루로 필터링했으며 가속 카드가 2장 있습니다.
        <Row><ItemImage id="minecraft:redstone" scale="2" /> <ItemImage id="speed_card" scale="2" /></Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="4 1 0" max="3 2 1" thickness=".05">
        (8) 회로 인쇄기 #1: 기본 설정입니다. 실리콘 압형과 가속 카드 4장이 있습니다.
        <Row><ItemImage id="silicon_press" scale="2" /> <ItemImage id="speed_card" scale="2" /></Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="4 3 0" max="3 4 1" thickness=".05">
        (9) 회로 인쇄기 #2: 기본 설정입니다. 논리 회로 압형과 가속 카드 4장이 있습니다.
        <Row><ItemImage id="logic_processor_press" scale="2" /> <ItemImage id="speed_card" scale="2" /></Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="4 4 0" max="3 5 1" thickness=".05">
        (10) 회로 인쇄기 #3: 기본 설정입니다. 연산 회로 압형과 가속 카드 4장이 있습니다.
        <Row><ItemImage id="calculation_processor_press" scale="2" /> <ItemImage id="speed_card" scale="2" /></Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="4 5 0" max="3 6 1" thickness=".05">
        (11) 회로 인쇄기 #4: 기본 설정입니다. 엔지니어링 회로 압형과 가속 카드 4장이 있습니다.
        <Row><ItemImage id="engineering_processor_press" scale="2" /> <ItemImage id="speed_card" scale="2" /></Row>
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2 2 0" max="1 3 1" thickness=".05">
        (12) 회로 인쇄기 #5: 기본 설정입니다. 가속 카드 4장이 있습니다.
        <ItemImage id="speed_card" scale="2" />
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2.7 2 0" max="3 1 1" thickness=".05">
        (13) 반입 버스 #1: 기본 설정이며 가속 카드가 2장 있습니다.
        <ItemImage id="speed_card" scale="2" />
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2.7 4 0" max="3 3 1" thickness=".05">
        (14) 반입 버스 #2: 기본 설정이며 가속 카드가 2장 있습니다.
        <ItemImage id="speed_card" scale="2" />
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2.7 5 0" max="3 4 1" thickness=".05">
        (15) 반입 버스 #3: 기본 설정이며 가속 카드가 2장 있습니다.
        <ItemImage id="speed_card" scale="2" />
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2.7 6 0" max="3 5 1" thickness=".05">
        (16) 반입 버스 #4: 기본 설정이며 가속 카드가 2장 있습니다.
        <ItemImage id="speed_card" scale="2" />
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2 3 0" max="1 3.3 1" thickness=".05">
        (17) 저장 버스 #2: 기본 설정입니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2 1.7 0" max="1 2 1" thickness=".05">
        (18) 저장 버스 #3: 기본 설정입니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="1 2 0" max="0.7 3 1" thickness=".05">
        (19) 반입 버스 #5: 기본 설정이며 가속 카드가 2장 있습니다.
        <ItemImage id="speed_card" scale="2" />
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="5 0.7 0" max="6 1 1" thickness=".05">
        (20) 저장 버스 #4: 기본 설정입니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="3.3 2.7 0.3" max="3.7 3 0.7" thickness=".05">
        회로 인쇄기는 케이블처럼 작동해 에너지를 전달하므로 석영 섬유 하나가 회로 인쇄기 3대 모두에 전력을 공급합니다.
  </BoxAnnotation>

<DiamondAnnotation pos="7 1.5 0.5" color="#00ff00">
        메인 네트워크로
    </DiamondAnnotation>

  <IsometricCamera yaw="185" pitch="5" />
</GameScene>

## 설정

* <ItemLink id="pattern_provider" /> (1)는 관련 <ItemLink id="processing_pattern" />을 넣은 기본 설정입니다.
  패턴은 원재료에서 완성된 프로세서로 바로 이어지며 [압형](../items-blocks-machines/presses.md)을 포함하지 **않습니다**.

  ![논리 패턴](../assets/diagrams/logic_pattern.png)
  ![연산 패턴](../assets/diagrams/calculation_pattern.png)
  ![엔지니어링 패턴](../assets/diagrams/engineering_pattern.png)

* <ItemLink id="storage_bus" /> (2, 17, 18, 20)는 기본 설정입니다.
* <ItemLink id="export_bus" /> (3~7)는 해당 재료로 필터링했으며 <ItemLink id="speed_card" />가 2장씩 있습니다.
    <Row>
      <ItemImage id="silicon" scale="2" />
      <ItemImage id="minecraft:gold_ingot" scale="2" />
      <ItemImage id="certus_quartz_crystal" scale="2" />
      <ItemImage id="minecraft:diamond" scale="2" />
      <ItemImage id="minecraft:redstone" scale="2" />
    </Row>
* <ItemLink id="import_bus" /> (13~16, 19)는 기본 설정이며 <ItemLink id="speed_card" />가 2장씩 있습니다.
* <ItemLink id="inscriber" />는 기본 설정이며 해당 [압형](../items-blocks-machines/presses.md)과
  <ItemLink id="speed_card" /> 4장이 들어 있습니다.
   <Row>
     <ItemImage id="silicon_press" scale="2" />
     <ItemImage id="logic_processor_press" scale="2" />
     <ItemImage id="calculation_processor_press" scale="2" />
     <ItemImage id="engineering_processor_press" scale="2" />
   </Row>

## 작동 원리

1. <ItemLink id="pattern_provider" />가 재료를 통에 넣습니다.
2. 첫 번째 [파이프 서브넷](pipe-subnet.md)(주황색)이 통에서 실리콘, 레드스톤 가루, 해당 프로세서 재료
   (금괴, 서투스 석영 수정 또는 다이아몬드)를 꺼내 적절한 <ItemLink id="inscriber" />에 넣습니다.
3. 앞의 <ItemLink id="inscriber" /> 4대가 <ItemLink id="printed_silicon" />과 <ItemLink id="printed_logic_processor" />,
   <ItemLink id="printed_calculation_processor" /> 또는 <ItemLink id="printed_engineering_processor" />를 만듭니다.
4. 두 번째와 세 번째 [파이프 서브넷](pipe-subnet.md)(초록색)이 앞의 <ItemLink id="inscriber" /> 4대에서 인쇄된 회로를 꺼내
   최종 조립용 다섯 번째 <ItemLink id="inscriber" />에 넣습니다.
5. 다섯 번째 <ItemLink id="inscriber" />가 [프로세서](../items-blocks-machines/processors.md)를 조립합니다.
6. 네 번째 [파이프 서브넷](pipe-subnet.md)(보라색)이 프로세서를 패턴 공급기에 넣어 메인 네트워크로 되돌립니다.
