---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 토글 버스
  icon: toggle_bus
  position: 110
categories:
- network infrastructure
item_ids:
- ae2:toggle_bus
- ae2:inverted_toggle_bus
---

# 토글 버스

<GameScene zoom="8" background="transparent">
<ImportStructure src="../assets/assemblies/toggle_bus.snbt" />
<IsometricCamera yaw="195" pitch="30" />
</GameScene>

<ItemLink id="fluix_glass_cable" />이나 다른 케이블과 비슷하게 작동하지만 레드스톤으로 연결 상태를 전환할 수 있는 버스입니다.
[ME 네트워크](../ae2-mechanics/me-network-connections.md)의 일부 구역을 분리할 수 있습니다.

레드스톤 신호가 공급되면 연결을 활성화합니다. <ItemLink id="inverted_toggle_bus" />는 반대로 연결을 비활성화합니다.

상태를 전환하면 네트워크가 재시작되어 연결된 장치를 다시 계산할 수 있습니다.

[케이블 부품](../ae2-mechanics/cable-subparts.md)으로 설치됩니다.

## 조합법

<RecipeFor id="toggle_bus" />

<RecipeFor id="inverted_toggle_bus" />
