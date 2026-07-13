---
navigation:
  parent: appflux/appflux-index.md
  title: 플럭스 접근기
  icon: appflux:flux_accessor
categories:
- flux accessor
item_ids:
- appflux:flux_accessor
- appflux:part_flux_accessor
---

# 플럭스 접근기

<Row>
<BlockImage id="appflux:flux_accessor" scale="8"></BlockImage>
<GameScene zoom="8" background="transparent">
  <ImportStructure src="../structure/flux_accessor.snbt"></ImportStructure>
</GameScene>
</Row>

플럭스 접근기는 ME 네트워크에 저장된 에너지를 받아들이거나 내보낼 수 있습니다. 기본적으로 입출력
제한이 없지만 Applied Flux 설정에서 변경할 수 있습니다.

빠른 모드와 일반 모드가 있습니다. 빠른 모드는 매 틱마다 에너지를 내보내므로 많이 사용하면 지연을
일으킬 수 있습니다. 일반 모드는 대상에 저장된 에너지에 따라 에너지를 내보내므로 지연 문제가 없습니다.

* 주의: 여기서 말하는 "에너지"는 [FE 저장 셀](./flux_cells.md)에 저장된 FE이며,
[에너지 셀](ae2:items-blocks-machines/energy_cells.md)의 에너지가 아닙니다.
