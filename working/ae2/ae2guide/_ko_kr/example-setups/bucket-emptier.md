---
navigation:
  parent: example-setups/example-setups-index.md
  title: 양동이 비우기
  icon: minecraft:bucket
---

# 양동이 비우기

[양동이 채우기](bucket-filler.md)도 참고하세요.

<ItemLink id="pattern_provider" />를 사용하므로 [자동 제작](../ae2-mechanics/autocrafting.md) 구성에 통합하기
위한 장치입니다.

때로는 유체 자체가 필요한데 양동이에 담긴 유체만 만들 수 있어 불편합니다. Thermal Expansion의 유체
전환기 같은 기계가 처리할 수도 있지만, 언제나 편리한 기계가 있는 것은 아닙니다. 다행히 기본 Minecraft의
조금 덜 편리한 <ItemLink id="minecraft:dispenser" />를 사용할 수 있습니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/bucket_emptier.snbt" />

<BoxAnnotation color="#dddddd" min="2 1 0" max="3 2 1">
        (1) 패턴 공급기: 제작 잠금을 "레드스톤 신호가 있을 때"로 설정하고 차단 모드를 켭니다.
        관련 가공 패턴을 넣습니다.

        <Row>
        ![비우기 패턴](../assets/diagrams/water_empty_pattern_small.png)
        ![비우기 패턴](../assets/diagrams/lava_empty_pattern_small.png)
        </Row>
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="2.1 2 0.1" max="2.9 2.2 0.9">
        (2) 인터페이스: 기본 설정을 사용합니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="3.1 2 1.1" max="3.9 2.2 1.9">
        (3) 저장 버스 1: 기본 설정을 사용합니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="4.05 1.05 0.8" max="4.95 1.95 1">
        (4) 소멸 평면: 설정할 GUI가 없습니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="3.2 1.2 0.8" max="3.8 1.8 1">
        (5) 반입 버스: 양동이로 필터링합니다.
        <ItemImage id="minecraft:bucket" scale="2" />
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="3 1.1 0.1" max="3.2 1.9 0.9">
        (6) 저장 버스 2: 기본 설정을 사용합니다.
  </BoxAnnotation>

<DiamondAnnotation pos="0 1.5 0.5" color="#00ff00">
        주 네트워크로 연결
    </DiamondAnnotation>

  <IsometricCamera yaw="225" pitch="45" />
</GameScene>

## 설정

* <ItemLink id="pattern_provider" /> (1)은 제작 잠금을 "레드스톤 신호가 있을 때"로 설정하고 차단 모드를
  켜며, 관련 <ItemLink id="processing_pattern" />을 넣습니다.

    ![충전기 패턴](../assets/diagrams/water_empty_pattern.png)
    ![충전기 패턴](../assets/diagrams/lava_empty_pattern.png)

* <ItemLink id="interface" /> (2)는 기본 설정을 사용합니다.
* 첫 번째 <ItemLink id="storage_bus" /> (3)은 기본 설정을 사용합니다.
* <ItemLink id="annihilation_plane" /> (4)은 설정할 GUI가 없습니다.
* <ItemLink id="import_bus" /> (5)는 양동이로 필터링합니다.
  <ItemImage id="minecraft:bucket" scale="2" />
* 두 번째 <ItemLink id="storage_bus" /> (6)은 기본 설정을 사용합니다.

## 작동 방식

1. <ItemLink id="pattern_provider" />가 재료를 <ItemLink id="interface" />로 밀어냅니다. 실제로는 최적화를
   위해 저장 버스를 공급기 면의 연장처럼 취급해 바로 통과시키므로 아이템이 인터페이스 안에 들어가지는 않습니다.
2. [파이프 서브네트워크](pipe-subnet.md#providing-to-multiple-places)의 작동 방식에 따라 양동이가
   <ItemLink id="minecraft:dispenser" /> 안으로 들어갑니다.
3. <ItemLink id="minecraft:comparator" />가 공급기의 양동이를 감지해 공급기에 전원을 공급하는 동시에
   <ItemLink id="pattern_provider" />를 잠급니다.
4. 공급기가 양동이의 유체를 쏟아내고 내부에는 빈 양동이가 남습니다.
5. <ItemLink id="import_bus" />가 빈 양동이를 공급기에서 꺼내 <ItemLink id="storage_bus" />를 통해 패턴
   공급기에 저장하여 주 네트워크로 돌려보냅니다.
6. 비교기가 공급기가 비었음을 감지해 패턴 공급기의 잠금을 풉니다.
