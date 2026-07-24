---
navigation:
  parent: aae_intro/aae_intro-index.md
  title: 퀀텀 컴퓨터
  icon: advanced_ae:quantum_core
categories:
  - advanced devices
item_ids:
  - advanced_ae:quantum_unit
  - advanced_ae:quantum_core
  - advanced_ae:quantum_structure
  - advanced_ae:quantum_accelerator
  - advanced_ae:quantum_multi_threader
  - advanced_ae:quantum_storage_128
  - advanced_ae:quantum_storage_256
  - advanced_ae:data_entangler
---

# 퀀텀 컴퓨터

퀀텀 컴퓨터는 특별한 종류의 제작 컴퓨터입니다. 제작 저장소가 충분한 한 제한 없이 제작 요청을 실행할
수 있습니다.

<GameScene zoom="2" background="transparent">
  <ImportStructure src="../structure/quantum_computer_multiblock.snbt"></ImportStructure>
</GameScene>

## 퀀텀 컴퓨터 코어

<BlockImage id="advanced_ae:quantum_core" p:powered="true" p:formed="true" scale="4"></BlockImage>

퀀텀 코어는 퀀텀 컴퓨터의 심장입니다. 자체적으로 256M 제작 저장소와 보조 처리 스레드 8개를
제공합니다. 단독으로 완성된 퀀텀 컴퓨터를 구성하고 모든 혜택을 제공할 수 있는 유일한 블록입니다.
하지만 멀티블록을 구성하는 데 사용하면 훨씬 강력한 컴퓨터를 만들 수 있습니다. 단독 컴퓨터로 사용할
때는 연결부가 있는 위쪽 또는 아래쪽 면으로 전력을 공급해야 합니다.

## 퀀텀 컴퓨터 저장소

<Row gap="20">
<BlockImage id="advanced_ae:quantum_storage_128" scale="4"></BlockImage>
<BlockImage id="advanced_ae:quantum_storage_256" scale="4"></BlockImage>
</Row>

이 블록은 퀀텀 코어의 제작 저장소를 확장합니다. 퀀텀 컴퓨터가 동시에 실행할 수 있는 작업 수를
실질적으로 늘립니다. 용량이 128M과 256M인 두 종류가 있습니다.

## 퀀텀 데이터 얽힘기

<BlockImage id="advanced_ae:data_entangler" scale="4"></BlockImage>

데이터 얽힘기는 멀티블록에 있는 모든 저장소 블록에 영향을 주는 특별한 블록입니다. 저장소 블록이 여러
차원에 데이터를 저장하게 하여 용량을 실질적으로 4배로 늘립니다. 퀀텀 컴퓨터 멀티블록마다 하나만 놓을
수 있습니다.

## 퀀텀 컴퓨터 가속기

<BlockImage id="advanced_ae:quantum_accelerator" scale="4"></BlockImage>

퀀텀 가속기는 퀀텀 컴퓨터 멀티블록에 보조 처리 스레드 8개를 추가합니다. 퀀텀 컴퓨터가 실행하는 모든
제작 패턴은 모든 보조 처리 스레드를 공유할 수 있으므로, 이 블록을 많이 마련하는 것이 좋습니다.

## 퀀텀 컴퓨터 멀티 스레더

<BlockImage id="advanced_ae:quantum_multi_threader" scale="4"></BlockImage>

데이터 얽힘기와 마찬가지로 멀티 스레더는 가속기가 별도의 차원에서 추가 스레드를 실행하게 하여 보조
처리 능력을 4배로 늘립니다. 퀀텀 컴퓨터 멀티블록마다 하나만 놓을 수 있습니다.

## 퀀텀 컴퓨터 구조 유리

<Row gap="20">
<BlockImage id="advanced_ae:quantum_structure" scale="4"></BlockImage>
<BlockImage id="advanced_ae:quantum_structure" p:formed="true" p:powered="true" scale="4"></BlockImage>
</Row>

이 블록은 퀀텀 컴퓨터의 골격을 구성합니다. 퀀텀 컴퓨터를 만드는 기본 블록으로 사용하며 모든 부분을
서로 연결합니다.

## 멀티블록

멀티블록 퀀텀 컴퓨터를 만들려면 다음 규칙을 지켜야 합니다:
- 최대 크기는 7x7x7입니다(외부 치수).
- 멀티블록 내부에 빈 공간이 없어야 합니다. 추가 효과가 없는 <ItemLink id="advanced_ae:quantum_unit" />로
채울 수 있습니다.
- <ItemLink id="advanced_ae:quantum_core" /> 정확히 하나
- <ItemLink id="advanced_ae:data_entangler" /> 최대 하나
- <ItemLink id="advanced_ae:quantum_multi_threader" /> 최대 하나
- 외부 층의 모든 블록은 <ItemLink id="advanced_ae:quantum_structure" />여야 합니다.
- 내부에는 <ItemLink id="advanced_ae:quantum_structure" />를 놓을 수 없습니다.

## 서버 설정

서버 설정에서 다음과 같은 여러 값을 조절할 수 있습니다:
- 최대 멀티블록 크기
- 각 퀀텀 가속기의 보조 처리 스레드 수
- 최대 퀀텀 멀티 스레더 수
- 멀티 스레더의 스레드 배율
- 최대 데이터 얽힘기 수
- 데이터 얽힘기의 저장소 배율

현재 인스턴스의 제한은 아이템 툴팁에서 확인할 수 있습니다.
