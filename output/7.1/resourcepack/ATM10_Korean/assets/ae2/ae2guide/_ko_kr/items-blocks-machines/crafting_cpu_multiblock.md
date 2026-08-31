---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 제작 CPU 다중 블록(저장소, 보조 처리 장치, 모니터, 유닛)
  icon: 1k_crafting_storage
  position: 210
categories:
- devices
item_ids:
- ae2:1k_crafting_storage
- ae2:4k_crafting_storage
- ae2:16k_crafting_storage
- ae2:64k_crafting_storage
- ae2:256k_crafting_storage
- ae2:crafting_accelerator
- ae2:crafting_monitor
- ae2:crafting_unit
---

# 제작 CPU

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/crafting_cpus.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

<Row>
  <BlockImage id="1k_crafting_storage" scale="4" />

  <BlockImage id="crafting_accelerator" scale="4" />

  <BlockImage id="crafting_monitor" scale="4" />

  <BlockImage id="crafting_unit" scale="4" />
</Row>

제작 CPU는 제작 요청과 작업을 관리합니다. 여러 단계의 제작 작업이 진행되는 동안 중간 재료를 저장하며,
처리할 수 있는 작업의 크기와 어느 정도는 완료 속도에도 영향을 줍니다. 자세한 내용은
[자동 제작](../ae2-mechanics/autocrafting.md)을 참고하세요.

제작 CPU 하나는 요청 또는 작업 하나를 처리합니다. 계산 프로세서와 매끄러운 돌 256개를 동시에 요청하려면 CPU 다중 블록 2개가 필요합니다.

플레이어의 요청, 자동화 장치(반출 버스와 인터페이스)의 요청 또는 둘 다 처리하도록 설정할 수 있습니다.

우클릭하면 제작 상태 UI가 열려 CPU가 처리 중인 제작 작업의 진행 상황을 확인할 수 있습니다.

## 설정

*   CPU가 플레이어의 요청만, <ItemLink id="export_bus" />와 <ItemLink id="crafting_card" /> 같은 자동화의 요청만,
    또는 둘 다 받도록 설정할 수 있습니다.

## 구성

제작 CPU는 다중 블록이며 빈틈없는 직육면체여야 합니다. 여러 부품으로 구성됩니다.

각 CPU에는 제작 저장소 블록이 하나 이상 있어야 합니다. 실제로 작동하는 최소 CPU는 1k 제작 저장소 하나뿐인 구조입니다.

# 제작 유닛

<BlockImage id="crafting_unit" scale="4" />

(선택 사항) 다른 부품이 부족할 때 제작 유닛은 CPU의 빈 공간을 채워 직육면체로 만듭니다.
다른 부품의 기본 제작 재료이기도 합니다.

<RecipeFor id="crafting_unit" />

# 제작 저장소

<Row>
  <BlockImage id="1k_crafting_storage" scale="4" />

  <BlockImage id="4k_crafting_storage" scale="4" />

  <BlockImage id="16k_crafting_storage" scale="4" />

  <BlockImage id="64k_crafting_storage" scale="4" />

  <BlockImage id="256k_crafting_storage" scale="4" />
</Row>

(필수) 제작 저장소는 모든 표준 셀 크기(1k, 4k, 16k, 64k, 256k)로 제공됩니다. 제작에 쓰이는 재료와 중간 재료를 저장하므로,
재료가 많은 제작 작업을 CPU가 처리하려면 더 크거나 더 많은 저장소가 필요합니다.

<Column>
  <Row>
    <RecipeFor id="1k_crafting_storage" />

    <RecipeFor id="4k_crafting_storage" />

    <RecipeFor id="16k_crafting_storage" />
  </Row>

  <Row>
    <RecipeFor id="64k_crafting_storage" />

    <RecipeFor id="256k_crafting_storage" />
  </Row>
</Column>

# 제작 보조 처리 장치

<BlockImage id="crafting_accelerator" scale="4" />

(선택 사항) 제작 보조 처리 장치는 CPU의 틱을 빠르게 하여 <ItemLink id="pattern_provider" />가 재료 묶음을 더 자주 보내게 합니다.
따라서 처리 속도가 빠른 기계를 따라갈 수 있습니다. 예를 들어 <ItemLink id="molecular_assembler" />로 둘러싼 패턴 공급기는
제작기 하나가 처리하는 것보다 빠르게 재료를 보낼 수 있으므로 재료 묶음을 주변 제작기 사이에 분배합니다.

책장을 만들기 위해 판자와 책을 동시에 만드는 것처럼, 복잡한 조합법에는 병렬로 수행할 수 있는 단계가 여러 개 있습니다.
CPU를 우클릭하거나 [터미널](terminals.md)의 망치 아이콘으로 여는 제작 상태 화면에서 이러한 단계는 모두 "예약됨"으로 표시됩니다.
보조 처리 장치가 하나 늘어날 때마다 이러한 단계를 하나 더 병렬로 수행해 "제작 중"으로 만들 수 있습니다.
다만 보통 병렬 가능한 단계 수보다 삽입 속도를 위해 설치한 보조 처리 장치 수가 더 많으므로 이 효과의 중요성은 크지 않습니다.

<RecipeFor id="crafting_accelerator" />

# 제작 모니터

<BlockImage id="crafting_monitor" scale="4" />

(선택 사항) 제작 모니터는 현재 CPU가 처리 중인 작업을 표시합니다.
화면은 <ItemLink id="color_applicator" />로 색을 입힐 수 있습니다.

<RecipeFor id="crafting_monitor" />
