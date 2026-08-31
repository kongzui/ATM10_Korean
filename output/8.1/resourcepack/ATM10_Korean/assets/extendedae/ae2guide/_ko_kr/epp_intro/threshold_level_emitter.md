---
navigation:
  parent: epp_intro/epp_intro-index.md
  title: ME 임계값 레벨 방출기
  icon: extendedae:threshold_level_emitter
categories:
- extended devices
item_ids:
- extendedae:threshold_level_emitter
---

# ME 임계값 레벨 방출기

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../structure/cable_threshold_level_emitter.snbt"></ImportStructure>
</GameScene>

리셋-셋 래치처럼 작동합니다. 네트워크의 아이템 수량이 하한 임계값보다 적으면 레드스톤 신호를 끄고, 상한 임계값보다 많으면 신호를 켭니다.

예를 들어 하한 임계값은 100, 상한 임계값은 150, 이렇게 설정했다고 가정하겠습니다.

처음에는 네트워크가 비어 있으므로 방출기가 작동하지 않습니다.

아이템 수량이 늘어나 150, 즉 상한 임계값을 초과하면 방출기가 레드스톤 신호를 보냅니다.

수량이 줄어 150개보다 적어져도 방출기는 계속 신호를 보냅니다.

마지막으로 수량이 100개보다 적어지면 방출기가 꺼집니다.
