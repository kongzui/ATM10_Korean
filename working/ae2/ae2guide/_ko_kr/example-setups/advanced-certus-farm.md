---
navigation:
  parent: example-setups/example-setups-index.md
  title: 고급 서투스 농장
  icon: certus_quartz_crystal
  position: 120
---

# 고급 서투스 농장

기본적으로 [반자동 서투스 농장](semiauto-certus-farm.md)을 ME 시스템에 완전히 통합한 구성입니다.

싹 틔우는 블록을 대량으로 비축하고 가끔 수동으로 복구하는 대신, [충전기 자동화](charger-automation.md)와
[물에 던지기 자동화](throw-in-water-automation.md)를 이용해 자동으로 처리합니다.

예상 속도는 [서투스 성장](../ae2-mechanics/certus-growth.md)을 참고하세요.

**다른 구성 뒤에 숨은 부분이 있는 복잡한 장치입니다. 모든 각도에서 보도록 장면을 돌려 보세요.**

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/advanced_certus_farm.snbt" />

  <BoxAnnotation color="#ddaaaa" min="3.7 2 1" max="4 3 2">
        (1) 소멸 평면 1: 설정할 GUI는 없지만 행운을 부여할 수 있습니다.
  </BoxAnnotation>

  <BoxAnnotation color="#ddaaaa" min="2 2 1.7" max="3 3 2">
        (2) 저장 버스 1: 서투스 석영 수정으로 필터링합니다.
        <ItemImage id="certus_quartz_crystal" scale="2" />
  </BoxAnnotation>

  <DiamondAnnotation pos="3 2.5 1.5" color="#ff0000">
    군집 파괴 서브네트워크
  </DiamondAnnotation>

  <BoxAnnotation color="#aaddaa" min="3.7 1 1" max="4 2 2">
        (3) 소멸 평면 2: 설정할 GUI는 없으며 섬세한 손길을 부여합니다.
  </BoxAnnotation>

  <BoxAnnotation color="#aaddaa" min="2 1 1.7" max="3 2 2">
        (4) 저장 버스 2: 서투스 석영 블록으로 필터링합니다.
        <BlockImage id="quartz_block" scale="2" />
  </BoxAnnotation>

  <DiamondAnnotation pos="3 1.5 1.5" color="#00ff00">
    서투스 블록 파괴 서브네트워크
  </DiamondAnnotation>

  <BoxAnnotation color="#ffddaa" min="4 0.7 1" max="5 1 2">
        (5) 형성 평면: 기본 설정을 사용합니다.
  </BoxAnnotation>

  <BoxAnnotation color="#ffddaa" min="2 0.7 2" max="3 1 3">
        (6) 반입 버스: 흠 있는 싹 틔우는 서투스 석영으로 필터링합니다.
        <BlockImage id="flawed_budding_quartz" scale="2" />
  </BoxAnnotation>

  <DiamondAnnotation pos="3 0.5 1.5" color="#ddcc00">
    싹 틔우는 블록 배치 서브네트워크
  </DiamondAnnotation>

  <BoxAnnotation color="#aaaadd" min="1.7 2 2" max="2 3 3">
        (7) 저장 버스 3: 서투스 석영 수정으로 필터링하며 주 저장소보다 높은 우선순위를 설정합니다.
        <ItemImage id="certus_quartz_crystal" scale="2" />
  </BoxAnnotation>

  <BoxAnnotation color="#aaaadd" min="2 1 2" max="3 2 3">
        (8) 인터페이스: 흠 있는 싹 틔우는 서투스 석영 1개를 비축하며 제작 카드를 설치합니다.
        <Row><BlockImage id="flawed_budding_quartz" scale="2" /> <ItemImage id="crafting_card" scale="2" /></Row>
  </BoxAnnotation>

<DiamondAnnotation pos="1.5 0.5 0" color="#00ff00">
        주 네트워크, 충전기 자동화와 물에 던지기 자동화로 연결
        <Row>
        <GameScene zoom="3" background="transparent">
          <ImportStructure src="../assets/assemblies/charger_automation.snbt" />
          <IsometricCamera yaw="195" pitch="30" />
        </GameScene>
        <GameScene zoom="3" background="transparent">
          <ImportStructure src="../assets/assemblies/throw_in_water.snbt" />
          <IsometricCamera yaw="195" pitch="30" />
        </GameScene>
        </Row>
    </DiamondAnnotation>

  <IsometricCamera yaw="165" pitch="5" />
</GameScene>

## 설정

### 군집 파괴 장치

* 첫 번째 <ItemLink id="annihilation_plane" /> (1)은 설정할 GUI가 없지만 행운을 부여할 수 있습니다.
* 첫 번째 <ItemLink id="storage_bus" /> (2)는 <ItemLink id="certus_quartz_crystal" />로 필터링합니다.

### 서투스 블록 파괴 장치

* 두 번째 <ItemLink id="annihilation_plane" /> (3)은 설정할 GUI가 없으며 섬세한 손길을 부여해야 합니다.
* 두 번째 <ItemLink id="storage_bus" /> (4)는 <ItemLink id="quartz_block" />으로 필터링합니다.

### 싹 틔우는 블록 배치 장치

* <ItemLink id="formation_plane" /> (5)은 기본 설정을 사용합니다.
* <ItemLink id="import_bus" /> (6)는 <ItemLink id="flawed_budding_quartz" />으로 필터링합니다.

### 주 네트워크

* 세 번째 <ItemLink id="storage_bus" /> (7)은 <ItemLink id="certus_quartz_crystal" />로 필터링하며,
  [우선순위](../ae2-mechanics/import-export-storage.md#storage-priority)를 주 저장소보다 높게 설정합니다.
* <ItemLink id="interface" /> (8)는 흠 있는 싹 틔우는 서투스 석영 1개를 비축하도록 설정하며
  <ItemLink id="crafting_card" />를 설치합니다.

## 작동 방식

### 군집 파괴 장치

군집 파괴 서브네트워크는 [간단한 서투스 농장](simple-certus-farm.md)의 서브네트워크와 매우 비슷합니다.

1. <ItemLink id="annihilation_plane" />은 앞의 블록을 부수려 하지만 <ItemLink id="quartz_cluster" />만
   부술 수 있습니다. 서브네트워크의 유일한 저장소인 <ItemLink id="storage_bus" />가
   <ItemLink id="certus_quartz_crystal" />로 필터링되어 있기 때문입니다.
2. <ItemLink id="storage_bus" />는 서투스 석영 수정을 통에 저장합니다.

### 서투스 블록 파괴 장치

싹 틔우는 블록이 수명을 다해 평범한 <ItemLink id="quartz_block" />이 되면 이 서브네트워크가 블록을
부숩니다. 군집 파괴 장치와 비슷하게 작동합니다.

1. <ItemLink id="annihilation_plane" />은 앞의 블록을 부수려 하지만 <ItemLink id="quartz_block" />만
   부술 수 있습니다. 서브네트워크의 유일한 저장소인 <ItemLink id="storage_bus" />가
   <ItemLink id="quartz_block" />으로 필터링되어 있기 때문입니다. 평면에는 섬세한 손길이 필요합니다. 그래야 싹
   틔우는 블록이 부서질 때 등급이 낮아지지 않고, 평면이 너무 일찍 부수지 않습니다.
2. <ItemLink id="storage_bus" />는 서투스 석영 블록을 <ItemLink id="interface" />에 저장하여
   [물에 던지기 자동화](throw-in-water-automation.md)가 새 <ItemLink id="flawed_budding_quartz" />을
   만드는 데 사용하게 합니다.

### 싹 틔우는 블록 배치 장치

파괴 장치가 수명을 다한 블록을 부수면 이 서브네트워크가 새 <ItemLink id="flawed_budding_quartz" />을 놓습니다.

1. <ItemLink id="import_bus" />가 <ItemLink id="interface" />에서 싹 틔우는 블록을
   [네트워크 저장소](../ae2-mechanics/import-export-storage.md)로 반입합니다.
2. 서브네트워크의 유일한 저장소인 <ItemLink id="formation_plane" />이 블록을 놓습니다.

### 주 네트워크

* <ItemLink id="storage_bus" />는 주 네트워크와 [충전기 자동화](charger-automation.md)가 통의 모든
  서투스 석영 수정에 접근하게 합니다. [우선순위](../ae2-mechanics/import-export-storage.md#storage-priority)가
  높으므로 수정은 주 저장소보다 통에 우선적으로 돌아갑니다.
* <ItemLink id="interface" />는 블록 배치 서브네트워크에 <ItemLink id="flawed_budding_quartz" />을
  제공하고, 블록 파괴 서브네트워크가 수명을 다한 블록을 주 네트워크로 돌려보내게 합니다.
  <ItemLink id="crafting_card" />는 인터페이스가 주 네트워크의
  [자동 제작](../ae2-mechanics/autocrafting.md)에 새 싹 틔우는 블록을 요청하게 합니다.
