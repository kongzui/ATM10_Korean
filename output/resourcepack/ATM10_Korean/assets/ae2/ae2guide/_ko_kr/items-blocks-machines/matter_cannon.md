---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 물질 대포
  icon: matter_cannon
  position: 410
categories:
- tools
item_ids:
- ae2:matter_cannon
---

# 물질 대포

<ItemImage id="matter_cannon" scale="4" />

물질 대포는 <ItemLink id="matter_ball" />이나 금속 조각 같은 작은 아이템을 투사체로 발사하는 휴대용 레일건입니다.
피해량은 발사한 아이템에 따라 달라집니다. 금 조각처럼 "무거운" 아이템은 10의 피해를 주어 물질 공처럼 가벼운 아이템의
2 피해보다 강합니다. 한 발을 쏠 때 기본적으로 1,600 AE를 소비합니다.

설정 옵션 "matterCannonBlockDamage"가 true이면 탄약의 피해량과 블록의 경도에 따라 블록을 파괴합니다.

<ItemLink id="charger" />에서 에너지를 충전할 수 있습니다.

물질 대포는 [저장 셀](storage_cells.md)처럼 작동합니다. <ItemLink id="chest" />의 저장 셀 슬롯에 대포를 넣으면
탄창을 가장 쉽게 채울 수 있습니다.

## 업그레이드

물질 대포는 <ItemLink id="cell_workbench" />에서 다음 [업그레이드](upgrade_cards.md)를 장착할 수 있습니다.

*   <ItemLink id="fuzzy_card" />는 피해 수준으로 셀 파티션을 설정하거나 아이템 NBT를 무시하게 합니다.
*   <ItemLink id="inverter_card" />는 필터를 허용 목록에서 차단 목록으로 바꿉니다.
*   <ItemLink id="speed_card" />는 발사당 에너지 사용량을 늘려 더 강하게 발사합니다.
*   <ItemLink id="void_card" />는 셀이 가득 찼을 때 들어오는 아이템을 삭제합니다. 반드시 파티션을 주의해서 설정하세요!
*   <ItemLink id="energy_card" />는 배터리 용량을 늘립니다.

## 조합법

<RecipeFor id="matter_cannon" />
