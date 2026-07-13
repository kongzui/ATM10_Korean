---
navigation:
  parent: epp_intro/epp_intro-index.md
  title: ME 태그 저장 버스
  icon: extendedae:tag_storage_bus
categories:
- extended devices
item_ids:
- extendedae:tag_storage_bus
---

# ME 태그 저장 버스

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../structure/cable_tag_storage_bus.snbt"></ImportStructure>
</GameScene>

ME 태그 저장 버스는 아이템 또는 유체 태그로 필터링할 수 있고 몇 가지 기본 논리 연산자를 지원하는 <ItemLink id="ae2:storage_bus" />입니다.

다음은 몇 가지 예시입니다.

- 원석만 허용

c:raw_materials/*

- 모든 주괴와 보석 허용

태그 식: c:ingots/* | c:gems/*
