---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 분자 제작기
  icon: molecular_assembler
  position: 310
categories:
- machines
item_ids:
- ae2:molecular_assembler
---

# 분자 제작기

<BlockImage id="molecular_assembler" scale="8" />

분자 제작기는 입력된 아이템으로 인접한 <ItemLink id="pattern_provider" />가 지정한 작업이나,
내부에 넣은 <ItemLink id="crafting_pattern" />, <ItemLink id="smithing_table_pattern" />, <ItemLink id="stonecutting_pattern" />의 작업을 수행한 뒤
결과물을 인접한 인벤토리로 밀어냅니다.

이 제작기에는 참나무 원목 1개 = 참나무 판자 4개 조합법을 지정한 제작 패턴이 들어 있습니다.
위쪽 호퍼로 참나무 원목을 공급하면 제작기가 판자를 만들어 아래쪽 호퍼로 내보냅니다.

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/standalone_assembler.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 분자 제작기의 주요 용도

하지만 주된 용도는 <ItemLink id="pattern_provider" /> 옆에 설치하는 것입니다. 이때 패턴 공급기는 특별하게 작동하여
관련 패턴 정보와 재료를 인접한 제작기로 보냅니다. 제작기는 결과물을 인접한 인벤토리, 즉 패턴 공급기의 반환 슬롯으로
자동 배출하므로 패턴 공급기에 제작기를 붙이는 것만으로 제작 패턴을 자동화할 수 있습니다.

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/assembler_tower.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 업그레이드

분자 제작기는 다음 [업그레이드](upgrade_cards.md)를 지원합니다.

*   <ItemLink id="speed_card" />

## 조합법

<RecipeFor id="molecular_assembler" />

## 참고

OptiFine은 "인접한 인벤토리로 밀어내기" 기능을 망가뜨리므로 제작기를 사용하는 대부분의 제작 설비가 작동하지 않습니다.
