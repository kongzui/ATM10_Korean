---
navigation:
  parent: example-setups/example-setups-index.md
  title: 광물 행운 자동화
  icon: minecraft:raw_iron
---

# 광물 행운 자동화

<ItemLink id="annihilation_plane" />에는 행운을 비롯한 곡괭이 마법 부여를 적용할 수 있습니다. 따라서
<ItemLink id="formation_plane" />과 <ItemLink id="annihilation_plane" /> 여러 개로 광물을 빠르게 설치하고
캐는 것이 대표적인 활용법입니다.

<ItemLink id="import_bus" />는 "속도가 붙는" 방식이므로 이 구성은 처음에는 느리다가 몇 초 뒤 최고 속도에 도달합니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/ore_fortuner.snbt" />

  <BoxAnnotation color="#dddddd" min="2.7 0 2" max="3 1 3">
        (1) 반입 버스: 가속 카드가 몇 장 들어 있습니다.
        <ItemImage id="speed_card" scale="2" />
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="0 0 2" max="2 1 2.3">
        (2) 형성 평면: 기본 설정입니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="0 0 0.7" max="2 1 1">
        (3) 소멸 평면: 설정 GUI는 없지만 행운 마법을 부여했습니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2.7 0 0" max="3 1 1">
        (4) 저장 버스: 기본 설정입니다.
  </BoxAnnotation>

<DiamondAnnotation pos="3.5 0.5 2.5" color="#00ff00">
        입력
    </DiamondAnnotation>

<DiamondAnnotation pos="3.5 0.5 0.5" color="#00ff00">
        출력
    </DiamondAnnotation>

<DiamondAnnotation pos="4 0.5 1.5" color="#00ff00">
        메인 네트워크로
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 설정

* <ItemLink id="import_bus" /> (1)에는 <ItemLink id="speed_card" />가 몇 장 들어 있습니다. 형성 평면 배열이
  클수록 한 번에 더 많은 아이템을 가져와야 하므로 더 많은 카드가 필요합니다.
* <ItemLink id="formation_plane" /> (2)은 기본 설정입니다.
* <ItemLink id="annihilation_plane" /> (3)은 GUI가 없어 설정할 수 없지만 행운 마법을 부여했습니다.
* <ItemLink id="storage_bus" /> (4)는 기본 설정입니다.

## 작동 원리

1. 초록색 서브넷의 <ItemLink id="import_bus" />가 첫 번째 통에서 블록을 가져와 [네트워크 저장소](../ae2-mechanics/import-export-storage.md)에 저장합니다.
2. 초록색 서브넷의 유일한 저장소인 <ItemLink id="formation_plane" />이 블록을 설치합니다.
3. 주황색 서브넷의 <ItemLink id="annihilation_plane" />이 행운을 적용해 블록을 캡니다.
4. 주황색 서브넷의 <ItemLink id="storage_bus" />가 채굴 결과물을 두 번째 통에 저장합니다.
