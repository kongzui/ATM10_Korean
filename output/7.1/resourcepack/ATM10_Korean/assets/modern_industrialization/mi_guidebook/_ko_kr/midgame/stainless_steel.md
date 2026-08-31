---
navigation:
  title: "스테인리스강"
  icon: "modern_industrialization:stainless_steel_dust"
  position: 201
  parent: modern_industrialization:midgame.md
item_ids:
  - modern_industrialization:vacuum_freezer
  - modern_industrialization:distillation_tower
---

# 스테인리스강

## 스테인리스강

<ItemImage id="modern_industrialization:stainless_steel_ingot" />

다음 대량 생산의 목표는 바로 스테인리스강입니다. 왜 그런지 계속 읽어보세요!

스테인리스강 가루를 전기 용광로에서 구우면 뜨거운 주괴를 얻을 수 있습니다. 뜨거운 주괴는 진공 냉각기에서 식힐 수 있습니다.

## 진공 냉각기

<GameScene zoom="2" interactive={true} fullWidth={true}>
    <MultiblockShape controller="vacuum_freezer" />
</GameScene>

REI를 사용해 필요한 재료를, 렌치를 사용해 멀티블록 구조를 확인하세요!

<Recipe id="modern_industrialization:electric_age/machine/vacuum_freezer_asbl" />

## 증류탑

디지털 회로를 만들었다면, 증류탑을 꼭 건설하세요. 증류소는 원유 처리 부산물을 하나밖에 얻을 수 없었지만, 증류탑은 층 하나당 부산물을 하나씩 얻을 수 있습니다!

<Recipe id="modern_industrialization:electric_age/machine/distillation_tower_asbl" />

다음은 가장 작은 증류탑과 가장 큰 증류탑을 나란히 놓은 예시입니다.
크기가 2인 증류탑은 제작법의 첫 번째 산출물만 내고, 크기가 3이면 첫 두 산출물을 내는 식으로 늘어납니다...


<GameScene zoom="1" interactive={true} fullWidth={true}>
    <MultiblockShape controller="distillation_tower" />
    <MultiblockShape controller="distillation_tower" x="-6" useBigShape={true} />
</GameScene>
