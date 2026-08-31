---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 충전기
  icon: charger
  position: 310
categories:
- machines
item_ids:
- ae2:charger
---

# 충전기

<BlockImage id="charger" scale="8" />

충전기는 지원되는 도구와 <ItemLink id="certus_quartz_crystal" />을 충전합니다.

위나 아래에서 AE2 [케이블](cables.md) 또는 다른 모드의 전력 케이블로 전력을 공급할 수 있습니다.
AE2 전력(AE)과 Forge Energy(FE)를 모두 받습니다. 어느 면에서든 아이템을 넣고 꺼낼 수 있지만 결과물만 꺼내지므로,
충전된 서투스 석영 대신 일반 서투스 석영을 꺼내지 않도록 필터를 설정할 필요가 없습니다.
자동화하기 쉽도록 <ItemLink id="certus_quartz_wrench" />로 회전할 수 있습니다.

<ItemLink id="charged_certus_quartz_crystal" />은 <ItemLink id="certus_quartz_crystal" />로 만들고,
<ItemLink id="meteorite_compass" />는 <ItemLink id="minecraft:compass" />로 만들 수 있습니다.

수동으로 동력을 공급하려면 위나 아래에 <ItemLink id="crank" />를 설치하고 아이템이 충전될 때까지 우클릭하세요.

[플루익스 연구원](fluix_researcher.md)의 작업소 블록이기도 합니다.

## 간단한 자동화

회전할 수 있다는 점을 활용하면 다음과 같이 충전기를 반자동화할 수 있습니다.

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/charger_hopper.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 조합법

<RecipeFor id="charger" />
