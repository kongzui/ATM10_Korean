---
navigation:
  parent: epp_intro/epp_intro-index.md
  title: ME 임계값 반출 버스
  icon: extendedae:threshold_export_bus
categories:
- extended devices
item_ids:
- extendedae:threshold_export_bus
---

# ME 임계값 반출 버스

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../structure/cable_threshold_export_bus.snbt"></ImportStructure>
</GameScene>

ME 임계값 반출 버스는 ME 네트워크에 저장된 아이템 수량이 임계값보다 많거나 적을 때 작동합니다.

## 예시

![GUI](../pic/thr_bus_gui1.png)

구리의 임계값을 128, 모드를 초과로 설정했으므로 네트워크에 저장된 구리가 128개를 초과하면 반출합니다.

![GUI](../pic/thr_bus_gui2.png)

임계값은 위와 같지만 모드를 미만으로 설정했습니다. 저장된 구리가 128개보다 적으면 반출합니다.
