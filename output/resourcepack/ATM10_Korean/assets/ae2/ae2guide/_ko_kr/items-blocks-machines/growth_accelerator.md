---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 수정 성장 가속기
  icon: growth_accelerator
  position: 310
categories:
- machines
item_ids:
- ae2:growth_accelerator
---

# 수정 성장 가속기

<BlockImage id="growth_accelerator" p:powered="true" scale="8"/>

수정 성장 가속기를 싹 틔우는 블록 옆에 설치하면 서투스 또는 자수정의 [성장](../ae2-mechanics/certus-growth.md)을 크게 가속합니다.

흥미롭게도 여러 식물의 성장도 *가속할 수 있습니다.*

자연적으로 발생하는 무작위 틱에 더해 인접한 블록에 "무작위 틱"을 적용합니다.
이론상 가속기 하나는 대상을 평소보다 약 90배 빠르게 성장시키며, 효과는 가산 방식으로 중첩됩니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/growth_accelerator.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

위나 아래에서 AE2 [케이블](cables.md) 또는 다른 모드의 전력 케이블로 전력을 공급할 수 있습니다.
AE2 전력(AE)과 Forge Energy(FE)를 모두 받습니다.

수동으로 동력을 공급하려면 위나 아래에 <ItemLink id="crank" />를 설치하고 우클릭하세요.

분홍색 플럭스 장식 부품이 있는 면이 위와 아래입니다.

<GameScene zoom="6" background="transparent">
<ImportStructure src="../assets/assemblies/accelerator_connections.snbt" />
<IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 조합법

<RecipeFor id="growth_accelerator" />
