---
navigation:
  parent: aae_intro/aae_intro-index.md
  title: ME 처리량 모니터
  icon: advanced_ae:throughput_monitor
categories:
  - advanced items
item_ids:
  - advanced_ae:throughput_monitor
  - advanced_ae:throughput_monitor_configurator
---

# ME 처리량 모니터

<GameScene zoom="8" background="transparent">
<ImportStructure src="../structure/throughput_monitors.snbt"></ImportStructure>
<IsometricCamera yaw="195" pitch="30" />
</GameScene>

처리량 모니터는 모니터의 한 종류입니다. <ItemLink id="ae2:storage_monitor" />와 같은 기능에 처리량
측정 기능을 더했습니다. 아이템 또는 유체 한 종류의 수량 변화를 추적하여 사용자에게 초당 변화량을
표시합니다.

채널이 *필요하지 않습니다*.

## 키 조작

*   아이템을 들고 우클릭하거나 유체 용기를 들고 빠르게 두 번 우클릭하면 해당 아이템 또는 유체로 모니터를 설정합니다.
*   빈손으로 우클릭하면 모니터의 설정을 지웁니다.
*   빈손으로 Shift+우클릭하면 모니터를 잠급니다.

## 처리량 모니터 설정기

<ItemImage id="advanced_ae:throughput_monitor_configurator" scale="4"></ItemImage>

처리량 모니터 설정기는 표시할 데이터를 바꾸는 도구입니다. 손에 들고 모니터를 우클릭하면 다음 세
옵션을 차례로 전환합니다:

* 틱당 아이템 수
* 초당 아이템 수
* 분당 아이템 수

참고: 모드를 바꾸면 측정값이 안정될 때까지 시간이 조금 걸릴 수 있으니 처음 표시되는 값은 믿지 마세요!
