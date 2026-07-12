---
navigation:
  parent: example-setups/example-setups-index.md
  title: 물에 던지기 자동화
  icon: fluix_crystal
---

# 물에 던지는 제작법 자동화

이 구성은 <ItemLink id="pattern_provider" />를 사용하므로 [자동 제작](../ae2-mechanics/autocrafting.md)
설비에 통합하기 위한 것입니다.

일부 제작법은 아이템을 물에 던져야 합니다(비슷한 구성으로 다른 곳에 아이템을 던질 수도 있습니다).
<ItemLink id="formation_plane" />, <ItemLink id="annihilation_plane" />과 보조 설비로 자동화할 수 있으며,
본질적으로 변형된 [파이프 서브넷](pipe-subnet.md) 두 개를 사용합니다.

이 구성은 [충전기 자동화](charger-automation.md)와 함께 사용하여 <ItemLink id="charged_certus_quartz_crystal" />을 공급하도록 설계했습니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/throw_in_water.snbt" />

<BoxAnnotation color="#dddddd" min="2 0 1" max="3 1 2">
        (1) 패턴 공급기: 관련 가공 패턴을 넣은 기본 설정입니다.

        ![플루익스 패턴](../assets/diagrams/fluix_pattern_small.png) ![흠 있는 싹 틔우는 서투스 석영 패턴](../assets/diagrams/flawed_budding_pattern_small.png)
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1.7 0 1" max="2 1 2">
        (2) 인터페이스: 기본 설정입니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 .7 1" max="2 1 2">
        (3) 형성 평면: 입력물을 아이템으로 떨어뜨리도록 설정했습니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 2 1" max="2 2.3 2">
        (4) 소멸 평면: 설정 GUI가 없습니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="2 1 1" max="3 1.3 2">
        (5) 저장 버스: 패턴의 출력물로 필터링했습니다.
        <Row><ItemImage id="fluix_crystal" scale="2" /><BlockImage id="flawless_budding_quartz" scale="2" /></Row>
  </BoxAnnotation>

<DiamondAnnotation pos="3.9 0.5 1.5" color="#00ff00">
        메인 네트워크 및 충전기 자동화로
        <GameScene zoom="3" background="transparent">
          <ImportStructure src="../assets/assemblies/charger_automation.snbt" />
          <IsometricCamera yaw="195" pitch="30" />
        </GameScene>
    </DiamondAnnotation>

  <IsometricCamera yaw="180" pitch="0" />
</GameScene>

## 설정과 패턴

* <ItemLink id="pattern_provider" /> (1)는 관련 <ItemLink id="processing_pattern" />을 넣은 기본 설정입니다.
  * <ItemLink id="fluix_crystal" />에는 JEI/REI의 기본 제작법을 그대로 사용해도 됩니다.

    ![플루익스 패턴](../assets/diagrams/fluix_pattern.png)

  * <ItemLink id="flawed_budding_quartz" />은 <ItemLink id="quartz_block" />에서 바로 만드는 편이 좋습니다.
    한 제작법의 입력물이 다른 제작법의 출력물이 되어 저장 버스가 필터링하지 못하는 문제를 피할 수 있습니다.

    ![흠 있는 싹 틔우는 서투스 석영 패턴](../assets/diagrams/flawed_budding_pattern.png)

* <ItemLink id="interface" /> (2)는 기본 설정입니다.
* <ItemLink id="formation_plane" /> (3)은 입력물을 아이템으로 떨어뜨리도록 설정했습니다.
* <ItemLink id="annihilation_plane" /> (4)은 GUI가 없어 설정할 수 없습니다.
* <ItemLink id="storage_bus" /> (5)는 패턴의 출력물로 필터링했습니다.

## 작동 원리

1. <ItemLink id="pattern_provider" />가 재료를 옆면에 붙은 초록색 서브넷의 <ItemLink id="interface" />에 넣습니다.
2. 인터페이스는 기본적으로 아무것도 비축하지 않도록 설정되어 있으므로 내용물을 [네트워크 저장소](../ae2-mechanics/import-export-storage.md)에 넣으려 합니다.
3. 초록색 서브넷의 유일한 저장소인 <ItemLink id="formation_plane" />이 받은 아이템을 물에 떨어뜨립니다.
4. 주황색 서브넷의 <ItemLink id="annihilation_plane" />이 방금 떨어진 아이템을 주우려 하지만 그러지 못합니다.
   패턴 공급기 위의 <ItemLink id="storage_bus" />(주황색 서브넷의 유일한 저장소)가 제작 결과물만 받도록 필터링되어 있기 때문입니다.
5. 아이템이 월드 내 변환을 수행합니다.
6. 이제 저장 버스가 해당 아이템을 저장할 수 있으므로 소멸 평면이 앞에 있는 아이템을 주울 수 있습니다.
7. 저장 버스가 결과물을 패턴 공급기에 저장하여 네트워크로 되돌립니다.
