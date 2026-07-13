---
navigation:
  title: 방사성 화학 물질 셀(Applied Mekanistics 전용)
  icon: radioactive_chemical_cell
  parent: index.md
  position: 050
categories:
  - megacells
item_ids:
  - radioactive_cell_component
  - radioactive_chemical_cell
---

# MEGA Cells: 방사성 화학 물질 셀

MEGA는 여러 애드온을 폭넓게 연동하며, *Mekanism*과 ***Applied Mekanistics*** 애드온을 함께 사용하는
플레이어를 위한 두 번째 전문 셀도 제공합니다. 두 모드를 사용하지 않아 아래 조합법에 오류가 표시된다면,
이 페이지와 셀은 안전하게 무시해도 됩니다.

## 방사성 화학 물질 셀

<Row>
  <ItemImage id="radioactive_cell_component" scale="3" />
  <ItemImage id="radioactive_chemical_cell" scale="3" />
</Row>

이름에서 알 수 있듯이 **MEGA 방사성 화학 물질 저장 셀**은 *Applied Mekanistics*가 제공하는 일반 저장
셀과 MEGA의 연동 셀을 보완하여 *Mekanism*의 "화학 물질"을 저장합니다. 일반 화학 물질 셀에는 한 가지
제약이 있습니다. *방사성* 화학 물질을 저장하지 못하며, Mekanism에서는 주로 *핵폐기물*, *폴로늄*,
*플루토늄*이 이에 해당합니다. 반대로 방사성 셀은 앞서 언급한 화학 물질*만* 저장합니다.

<Row>
  <RecipeFor id="radioactive_cell_component" />
  <RecipeFor id="radioactive_chemical_cell" />
</Row>

방사성 셀은 방사성 화학 물질 한 종류만 저장할 수 있고 사용 전에 분할해야 한다는 점에서
<ItemLink id="megacells:bulk_item_cell" />과 비슷합니다. 하지만 공통점은 여기까지입니다. 방사성 셀의
저장량은 유한하며, 최대 *256[바이트](ae2:ae2-mechanics/bytes-and-types.md)*입니다. 그래도 이는 화학 물질
*2048양동이*, 즉 핵폐기물 통 *4개* 분량을 셀 하나에 담는 것과 같습니다.

![폴로늄을 담은 방사성 셀](assets/diagrams/radioactive_cell.png)

이처럼 불안정한 물질을 비교적 안정된 상태로 유지하려면 셀에 훨씬 많은 전력이 필요합니다. 일반적인
<ItemLink id="ae2:item_storage_cell_1k" />은 0.5 AE/틱, <ItemLink id="ae2:item_storage_cell_256k" />은
2.5 AE/t, <ItemLink id="megacells:item_storage_cell_256m" />은 5 AE/t를 소모하지만, 방사성 셀 하나는
연결된 ME 상자나 드라이브 안에서 무려 **250 AE/틱**을 소모합니다.

마지막으로 Mekanism 플레이어가 의도대로 핵폐기물을 관리하도록, 방사성 셀은 ***사용후** 핵폐기물*을
명시적으로 저장하지 않습니다. *기본 설정에서는* 원자로 시설 관리를 그렇게 쉽게 피할 수 없습니다.
그래도 쉬운 길을 택하고 싶은 플레이어를 위해 이 동작은 설정할 수 있습니다. *어떻게* 설정하는지는
독자에게 연습 문제로 남겨 두겠습니다.
