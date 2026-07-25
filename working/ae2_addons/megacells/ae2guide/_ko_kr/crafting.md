---
navigation:
  title: MEGA 자동 제작
  icon: 256m_crafting_storage
  parent: index.md
  position: 020
categories:
  - megacells
item_ids:
  - mega_crafting_unit
  - 1m_crafting_storage
  - 4m_crafting_storage
  - 16m_crafting_storage
  - 64m_crafting_storage
  - 256m_crafting_storage
  - mega_crafting_accelerator
  - mega_crafting_monitor
  - mega_pattern_provider
  - cable_mega_pattern_provider
---

# MEGA Cells: 자동 제작

<GameScene zoom="6" background="transparent">
  <ImportStructure src="assets/assemblies/crafting_cpu.snbt" />
  <IsometricCamera yaw="195" pitch="10" />
</GameScene>

## MEGA [제작 CPU](ae2:items-blocks-machines/crafting_cpu_multiblock.md)

<Row>
  <BlockImage id="mega_crafting_unit" scale="4" />
  <BlockImage id="1m_crafting_storage" scale="4" />
  <BlockImage id="4m_crafting_storage" scale="4" />
  <BlockImage id="16m_crafting_storage" scale="4" />
  <BlockImage id="64m_crafting_storage" scale="4" />
  <BlockImage id="256m_crafting_storage" scale="4" />
</Row>

저장 셀과 마찬가지로 MEGA는 제작 CPU에도 더 큰 저장 등급을 제공합니다. 늘어난 성능을 감당하려면 전용
<ItemLink id="ae2:crafting_unit" />인 **MEGA 제작 유닛**이 필요하지만, 더 많은 메모리로 가장 큰 제작
작업도 쉽게 처리합니다. 검은색 외형도 *아주 멋집니다*.

<RecipeFor id="mega_crafting_unit" />
<RecipeFor id="1m_crafting_storage" />
<RecipeFor id="4m_crafting_storage" />
<RecipeFor id="16m_crafting_storage" />
<RecipeFor id="64m_crafting_storage" />
<RecipeFor id="256m_crafting_storage" />

보너스로 MEGA는 <ItemLink id="ae2:crafting_accelerator" />에 해당하는 장치도 제공합니다. 보조 처리
블록 하나마다 스레드가 하나가 아니라 무려 *네 개* 추가된다는 장점이 있습니다.

<BlockImage id="mega_crafting_accelerator" scale="4" />
<RecipeFor id="mega_crafting_accelerator" />

완전한 구성을 갖추도록 <ItemLink id="ae2:crafting_monitor" />에 해당하는 MEGA 장치도 있습니다. 일반
모니터와 기능상 차이는 없지만, CPU 멀티블록 전체에 매끈하고 어두운 외형을 유지하여 앞서 설명한 장치와
시각적으로 통일할 수 있습니다.

<BlockImage id="mega_crafting_monitor" scale="4" />
<RecipeFor id="mega_crafting_monitor" />

## MEGA 패턴 공급기

<Row>
  <BlockImage id="mega_pattern_provider" scale="4" />
  <GameScene zoom="4" background="transparent">
    <ImportStructure src="assets/assemblies/cable_mega_pattern_provider.snbt" />
  </GameScene>
</Row>

<ItemLink id="ae2:pattern_provider" />를 보완하는 **MEGA 패턴 공급기**는 적합한 AE2 장치의 더 큰
버전을 제공한다는 흐름을 이어갑니다. 패턴 용량이 두 배여서 총 18개 패턴을 보관하고 처리할 수 있습니다.
대신 [**처리 패턴**](ae2:items-blocks-machines/patterns.md)만 담을 수 있으므로
<ItemLink id="ae2:molecular_assembler" />와는 제대로 작동하지 않습니다.

<Row>
  <RecipeFor id="mega_pattern_provider" />
  <RecipeFor id="cable_mega_pattern_provider" />
</Row>
