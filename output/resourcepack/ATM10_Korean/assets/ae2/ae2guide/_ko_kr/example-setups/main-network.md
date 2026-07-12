---
navigation:
  parent: example-setups/example-setups-index.md
  title: "메인 네트워크" 예제
  icon: controller
---

# "메인 네트워크" 예제

다른 많은 구성에서 "메인 네트워크"를 언급합니다. 여러 [장치](../ae2-mechanics/devices.md)를 어떻게 모아
하나의 시스템으로 만드는지 궁금할 수도 있습니다. 다음은 그 예입니다.

<GameScene zoom="2.5" interactive={true}>
  <ImportStructure src="../assets/assemblies/small_base_network.snbt" />

    <BoxAnnotation color="#33dd33" min="5 1 10" max="9 7 14" thickness="0.05">
        패턴 공급기와 분자 제작기를 큰 무리로 배치하면 제작·석재 절단·대장장이 작업 패턴을 많이 넣을 수 있습니다.
        체스판 모양은 좁은 공간에서 공급기들이 여러 조립기를 병렬로 사용하게 해 줍니다.
        8개씩 묶으면 채널이 잘못 연결될 수 없습니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="13 10 12" max="14 11 14" thickness="0.05">
        컨트롤러를 실제로 이렇게 크게 만들 필요는 없습니다. 다른 사람의 기지에서 보이는 거대한 고리나 정육면체 설계는
        주로 멋을 내기 위한 것입니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="13 12 13" max="14 13 14" thickness="0.05">
        좋은 네트워크에는 에너지 셀이 있습니다. 게임 틱당 전력 입력 한도를 높이고
        전력 변동을 완화해 줍니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="2 1 10" max="4 4 13" thickness="0.05">
        다른 모드의 전력원, 즉 원자로·태양 전지판·발전기 등을 사용하는 편이 좋습니다.
        진동 챔버도 그럭저럭 쓸 수 있지만, AE2는 모드팩에서 기지의 주 발전기를 사용하도록 설계되었습니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="15 1 9" max="16 3 14" thickness="0.05">
        가림판으로 벽 뒤의 장치를 숨길 수 있습니다.
    </BoxAnnotation>
    <BoxAnnotation color="#33dd33" min="15 3 12" max="16 10 14" thickness="0.05">
        가림판으로 벽 뒤의 장치를 숨길 수 있습니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="13 9 7" max="14 10 9" thickness="0.05">
        일반 저장소에는 드라이브 베이와 셀이 이렇게 많이 필요하지 않습니다. 4k 또는 16k 셀을 넣은
        ME 드라이브 2~4개면 거의 언제나 충분합니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="13 9 10" max="14 11 11" thickness="0.05">
        대량 저장소에는 특정 아이템으로 필터링한 큰 셀을 사용하고, 별도의 드라이브에 넣어
        우선순위를 더 높게 설정하는 편이 좋습니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="10 9 13" max="11.7 13 14" thickness="0.05">
        인터페이스 기반 자동 비축입니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="6 10 12" max="9 12 15" thickness="0.05">
        충전기 자동화 구성을 여러 충전기로 확장한 형태입니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="2 10 12" max="5 11 15" thickness="0.05">
        1.20부터 회로 인쇄기가 결과물을 자동 배출할 수 있어 가능한 또 다른 프로세서 자동화 방법입니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="3 10 10" max="4 12 11" thickness="0.05">
        1.20부터 회로 인쇄기가 결과물을 자동 배출할 수 있어 가능한 또 다른 프로세서 자동화 방법입니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="7.2 9.2 8.2" max="7.8 10 8.8" thickness="0.05">
        무선 액세스 포인트의 범위는 구형이므로 가운데에 배치했습니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="14 1 2" max="16 5 7" thickness="0.05">
        보통 큰 작업용 대형 제작 CPU 1~2개와, 대형 CPU가 사용 중일 때 보조 작업을 처리할
        소형 CPU 몇 개를 함께 둡니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="5 3 6" max="6 4 7" thickness="0.05">
        서브넷에 장치가 8개보다 많다면(예: 8곳보다 많은 곳에 분배한다면)
        자체 컨트롤러가 필요할 수도 있습니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="7.3 1 3.3" max="9.7 4 6" thickness="0.05">
        서투스 농장입니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="10.3 1 2.3" max="12.7 3.7 5" thickness="0.05">
        물에 던지기 자동화입니다.
    </BoxAnnotation>

  <IsometricCamera yaw="135" pitch="15" />
</GameScene>
