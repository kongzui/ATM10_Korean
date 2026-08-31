---
navigation:
  parent: epp_intro/epp_intro-index.md
  title: ME 정밀 반출 버스
  icon: extendedae:precise_export_bus
categories:
- extended devices
item_ids:
- extendedae:precise_export_bus
---

# ME 정밀 반출 버스

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../structure/cable_precise_export_bus.snbt"></ImportStructure>
</GameScene>

ME 정밀 반출 버스는 아이템이나 유체를 지정한 수량만큼 반출합니다. 대상 보관함이 반출량 전부를 받을 수 있을 때만 작동합니다.

## 예시

![GUI](../pic/pre_bus_gui1.png)

이 설정은 작업 한 번에 조약돌 3개를 반출한다는 뜻입니다. 네트워크의 조약돌이 3개보다 적으면 반출을 멈춥니다.

![GUI](../pic/pre_bus_gui2.png)

대상 보관함이 반출량을 전부 담을 수 없을 때도 멈춥니다. 현재 상자에는 조약돌이 2개만 더 들어갈 수 있으므로 반출 버스가 작동하지 않습니다.
