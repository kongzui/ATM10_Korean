---
navigation:
  parent: example-setups/example-setups-index.md
  title: 충전기 자동화
  icon: charger
---

# 충전기 자동화

이 구성은 <ItemLink id="pattern_provider" />를 사용하므로 [자동 제작](../ae2-mechanics/autocrafting.md)
설비에 통합하기 위한 것입니다. <ItemLink id="charger" /> 하나만 자동화하려면 호퍼와 상자 등을 사용하세요.

<ItemLink id="charger" /> 자동화는 상당히 간단합니다. <ItemLink id="pattern_provider" />가 재료를 충전기에 넣으면
[파이프 서브넷](pipe-subnet.md)이나 다른 아이템 파이프가 결과물을 공급기로 되돌립니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/charger_automation.snbt" />

<BoxAnnotation color="#dddddd" min="1 0 0" max="2 1 1">
        (1) 패턴 공급기: 관련 가공 패턴을 넣은 기본 설정입니다. 충전기에 전력도 공급합니다.

        ![충전기 패턴](../assets/diagrams/charger_pattern_small.png)
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="0 1 0" max="1 1.3 1">
        (2) 반입 버스: 기본 설정입니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 1 0" max="2 1.3 1">
        (3) 저장 버스: 기본 설정입니다.
  </BoxAnnotation>

<DiamondAnnotation pos="4 0.5 0.5" color="#00ff00">
        메인 네트워크로
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 설정

* <ItemLink id="pattern_provider" /> (1)는 관련 <ItemLink id="processing_pattern" />을 넣은 기본 설정입니다.
  또한 <ItemLink id="charger" />에 [에너지](../ae2-mechanics/energy.md)를 공급합니다.
  [케이블](../items-blocks-machines/cables.md)처럼 작동하기 때문입니다.

    ![충전기 패턴](../assets/diagrams/charger_pattern.png)

* <ItemLink id="import_bus" /> (2)는 기본 설정입니다.
* <ItemLink id="storage_bus" /> (3)은 기본 설정입니다.

## 작동 원리

1. <ItemLink id="pattern_provider" />가 재료를 <ItemLink id="charger" />에 넣습니다.
2. 충전기가 재료를 충전합니다.
3. 초록색 서브넷의 <ItemLink id="import_bus" />가 충전기에서 결과물을 꺼내
   [네트워크 저장소](../ae2-mechanics/import-export-storage.md)에 저장하려 합니다.
4. 초록색 서브넷의 유일한 저장소인 <ItemLink id="storage_bus" />가 결과물을 패턴 공급기에 저장하여 메인 네트워크로 되돌립니다.
