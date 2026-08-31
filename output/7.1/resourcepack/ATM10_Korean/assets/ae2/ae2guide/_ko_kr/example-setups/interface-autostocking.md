---
navigation:
  parent: example-setups/example-setups-index.md
  title: 인터페이스 자동 비축
  icon: interface
---

# 인터페이스 자동 비축

"여러 아이템을 일정 수량만큼 비축하고 필요할 때 더 제작하려면 어떻게 해야 할까?"라는 의문이 들 수
있습니다.

<ItemLink id="interface" />와 <ItemLink id="crafting_card" />를 사용하면 네트워크의
[자동 제작](../ae2-mechanics/autocrafting.md)에 새 아이템을 자동으로 요청할 수 있습니다. 다양한 아이템을
적은 수량씩 유지하는 데 적합한 구성입니다.

예제 장치는 너무 넓어지지 않도록 짧게 만들었습니다. [채널](../ae2-mechanics/channels.md) 8개를
일반 [케이블](../items-blocks-machines/cables.md)에서 모두 활용하려면 <ItemLink id="interface" /> 4개와
<ItemLink id="storage_bus" /> 4개를 사용하는 것이 가장 효율적입니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/interface_autostocking.snbt" />

<BoxAnnotation color="#dddddd" min="0 0 0" max="2 1 1">
        (1) 인터페이스: 원하는 아이템을 내부에 비축하도록 설정하고 제작 카드를 설치합니다.
        <ItemImage id="crafting_card" scale="2" />
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="0 1 0" max="2 1.3 1">
        (2) 저장 버스: "입출력 모드"를 "추출 전용"으로 설정합니다.
  </BoxAnnotation>

<DiamondAnnotation pos="4 0.5 0.5" color="#00ff00">
        주 네트워크로 연결
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 설정

* <ItemLink id="interface" /> (1)는 원하는 아이템을 내부에 비축하도록 설정합니다. 원하는 아이템을
  위쪽 슬롯에 클릭하거나 JEI에서 끌어 놓고, 슬롯 위의 렌치 아이콘을 눌러 수량을 설정합니다.
  <ItemLink id="crafting_card" />를 설치합니다.
* <ItemLink id="storage_bus" /> (2)는 "입출력 모드"를 "추출 전용"으로 설정합니다.

## 작동 방식

1. <ItemLink id="interface" />가 [네트워크 저장소](../ae2-mechanics/import-export-storage.md)에서 설정한
   아이템을 충분히 가져올 수 없고 <ItemLink id="crafting_card" />가 설치되어 있으면, 네트워크의
   [자동 제작](../ae2-mechanics/autocrafting.md)에 해당 아이템을 더 만들도록 요청합니다.
2. <ItemLink id="storage_bus" />는 네트워크가 인터페이스의 내용물에 접근하게 합니다.
