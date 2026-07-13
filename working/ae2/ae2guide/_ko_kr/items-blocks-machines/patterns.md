---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 패턴
  icon: crafting_pattern
  position: 410
categories:
- tools
item_ids:
- ae2:blank_pattern
- ae2:crafting_pattern
- ae2:processing_pattern
- ae2:smithing_table_pattern
- ae2:stonecutting_pattern
---

# 패턴

<ItemImage id="crafting_pattern" scale="4" />

패턴은 <ItemLink id="pattern_encoding_terminal" />에서 빈 패턴으로 만들며, <ItemLink id="pattern_provider" />나
<ItemLink id="molecular_assembler" />에 넣어 사용합니다.

용도에 따라 여러 종류의 패턴이 있습니다.

*   <ItemLink id="crafting_pattern" />은 제작대 조합법을 인코딩합니다. <ItemLink id="molecular_assembler" />에 직접 넣으면 재료를
    받았을 때 결과물을 제작하지만, 주로 분자 조립기 옆의 <ItemLink id="pattern_provider" />에서 사용합니다.
    이때 패턴 공급기는 특별하게 작동해 관련 패턴과 재료를 인접한 조립기로 보냅니다.
    조립기는 제작 결과물을 인접한 인벤토리로 자동 배출하므로, 패턴 공급기에 조립기를 붙이는 것만으로 제작 패턴을 자동화할 수 있습니다.

***

*   <ItemLink id="smithing_table_pattern" />은 제작 패턴과 매우 비슷하지만 대장장이 작업대 조합법을 인코딩합니다.
    패턴 공급기와 분자 조립기로 똑같이 자동화하며, 제작·대장장이 작업대·석재 절단 패턴을 같은 설비에서 사용할 수 있습니다.

***

*   <ItemLink id="stonecutting_pattern" />은 제작 패턴과 매우 비슷하지만 석재 절단기 조합법을 인코딩합니다.
    패턴 공급기와 분자 조립기로 똑같이 자동화하며, 제작·대장장이 작업대·석재 절단 패턴을 같은 설비에서 사용할 수 있습니다.

***

*   <ItemLink id="processing_pattern" />은 자동 제작에 큰 유연성을 줍니다. 가장 일반화된 유형으로, 단순히
    "패턴 공급기가 이 재료를 인접한 인벤토리로 보내면 가까운 미래든 먼 미래든 ME 시스템이 이 결과물을 받는다"고 지정합니다.
    거의 모든 모드 기계와 화로 등을 자동 제작에 연결할 때 사용합니다. 재료를 보낸 뒤 결과물을 받기까지 무슨 일이 일어나는지
    신경 쓰지 않으므로 아주 독특한 구성도 가능합니다. 재료를 복잡한 공장 생산 사슬에 넣어 분류하고, 무한 생산 농장에서 다른
    재료를 받아들이고, 꿀벌 대소동 대본 전체를 인쇄하더라도 패턴이 지정한 결과물만 받으면 ME 시스템은 개의치 않습니다.
    재료와 결과물이 서로 관련 있는지도 신경 쓰지 않습니다. "벚나무 판자 1개 = 네더의 별 1개"라고 지정하고,
    벚나무 판자를 받은 위더 농장이 위더를 처치하게 해도 작동합니다.

동일한 패턴을 가진 여러 <ItemLink id="pattern_provider" />를 지원하며 병렬로 작동합니다. 또한 패턴을 조약돌 1개 = 돌 1개 대신
조약돌 8개 = 돌 8개로 지정할 수 있습니다. 그러면 패턴 공급기가 매 작업마다 조약돌을 하나씩이 아니라 8개씩 제련 설비에 넣습니다.

## 조합법

<RecipeFor id="blank_pattern" />
