---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 프로세서
  icon: logic_processor
  position: 010
categories:
- misc ingredients blocks
item_ids:
- ae2:logic_processor
- ae2:calculation_processor
- ae2:engineering_processor
- ae2:printed_silicon
- ae2:printed_logic_processor
- ae2:printed_calculation_processor
- ae2:printed_engineering_processor
- ae2:silicon
---

# 프로세서

<Row>
  <ItemImage id="logic_processor" scale="4" />

  <ItemImage id="calculation_processor" scale="4" />

  <ItemImage id="engineering_processor" scale="4" />
</Row>

프로세서는 AE2 [장치](../ae2-mechanics/devices.md)와 기계의 주요 재료 중 하나이며, 처음 마주하는 큰 자동화 과제이기도 합니다.
프로세서는 세 종류로, 각각 금, <ItemLink id="certus_quartz_crystal" />, 다이아몬드로 만듭니다.
<ItemLink id="inscriber" />에서 [프레스](presses.md)를 사용하는 여러 단계의 공정으로 제작합니다
(보통 여러 회로 인쇄기와 필터가 설정된 파이프를 이용합니다).

## 제작 단계

<Column gap="5">
  1.  필요한 재료를 모으거나 만듭니다: 실리콘, 레드스톤, 금, <ItemLink id="certus_quartz_crystal" />, 다이아몬드.

  <RecipeFor id="silicon" />

  <br />

  2.  필요한 인쇄 회로 부품을 찍어 냅니다.

  <Row>
    <RecipeFor id="printed_silicon" />

    <RecipeFor id="printed_logic_processor" />
  </Row>

  <Row>
    <RecipeFor id="printed_calculation_processor" />

    <RecipeFor id="printed_engineering_processor" />
  </Row>

  <br />

  3.  최종 조립

  <Row>
    <RecipeFor id="logic_processor" />

    <RecipeFor id="calculation_processor" />
  </Row>

  <RecipeFor id="engineering_processor" />
</Column>
