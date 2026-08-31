---
navigation:
  title: "고압!"
  icon: "modern_industrialization:pressurizer"
  position: 202
  parent: modern_industrialization:midgame.md
item_ids:
  - modern_industrialization:pressurizer
  - modern_industrialization:high_pressure_large_steam_boiler
  - modern_industrialization:high_pressure_advanced_large_steam_boiler
  - modern_industrialization:large_steam_turbine
  - modern_industrialization:heat_exchanger
  - modern_industrialization:hv_steam_turbine
---

# 고압!

## 가압기

<GameScene zoom="2" interactive={true} fullWidth={true}>
    <MultiblockShape controller="pressurizer" />
</GameScene>

가압기는 물을 고압수로, 혹은 증기를 고압 증기로 바꿀 수 있습니다. 물론 다른 것도 가능합니다.

<Recipe id="modern_industrialization:electric_age/machine/pressurizer_asbl" />

## 고압 대형 증기 보일러

<GameScene zoom="2" interactive={true} fullWidth={true}>
    <MultiblockShape controller="high_pressure_large_steam_boiler" />
</GameScene>

고압 물을 만들었다면, 고압 대형 증기 보일러를 활용해 고압 증기를 만들 수 있습니다.

고압 증기 1밀리버킷은 일반 증기 8 mb, 즉 8 EU에 해당합니다.

<Recipe id="modern_industrialization:electric_age/machine/high_pressure_large_steam_boiler_asbl" />

## 고압 고급 대형 증기 보일러

<GameScene zoom="2" interactive={true} fullWidth={true}>
    <MultiblockShape controller="high_pressure_advanced_large_steam_boiler" />
</GameScene>

나중에는 고압 대형 증기 보일러의 고급 버전도 만들 수 있습니다.

## 대형 증기 터빈

<GameScene zoom="2" interactive={true} fullWidth={true}>
    <MultiblockShape controller="large_steam_turbine" />
</GameScene>

대형 증기 터빈은 증기나 고압 증기 둘 다 전력으로 변환할 수 있습니다. 최대 발전량은 16384 EU/t 입니다.**하지만, 고압 증기를 넣는다고 해서 고압 물을 다시 되돌려받지는 못합니다.**

<Recipe id="modern_industrialization:electric_age/machine/large_steam_turbine_asbl" />

## 열교환기

<GameScene zoom="2" interactive={true} fullWidth={true}>
    <MultiblockShape controller="heat_exchanger" />
</GameScene>

물을 압축하는건 엄청난 에너지가 소모되지만, 터빈에서 고압 물을 회수할 수는 없습니다. 열 교환기를 사용해 고압 물을 순환시킬 수 있습니다.

<Recipe id="modern_industrialization:electric_age/machine/heat_exchanger_asbl" />

## HV 증기 터빈

좀 작은 규모의 발전을 원하신다면, HV 증기 터빈을 사용해보세요. 512 EU/t 만큼의 발전이 가능하지만, 일반적인 증기만을 받아들입니다.

<Recipe id="modern_industrialization:electric_age/machine/hv_steam_turbine_asbl" />
