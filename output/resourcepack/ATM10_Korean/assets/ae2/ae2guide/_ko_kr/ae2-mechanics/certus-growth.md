---
navigation:
  parent: ae2-mechanics/ae2-mechanics-index.md
  title: 서투스 성장
  icon: quartz_cluster
---

# 서투스 성장

## 시작하기 페이지에서 가져온 기본 내용

<GameScene zoom="6" background="transparent">
<ImportStructure src="../assets/assemblies/budding_certus_1.snbt" />
</GameScene>

자수정과 비슷하게, 서투스 석영 봉오리는
[싹 틔우는 서투스 석영 블록](../items-blocks-machines/budding_certus.md)에서 자라납니다. 다 자라지 않은
봉오리를 부수면 행운의 영향을 받지 않고 <ItemLink id="certus_quartz_dust" /> 1개가 나옵니다. 완전히
자란 군집을 부수면 <ItemLink id="certus_quartz_crystal" /> 4개가 나오며, 행운을 사용하면 수량이 늘어납니다.

싹 틔우는 서투스 석영 블록에는 흠잡을 데 없는, 흠 있는, 깎인, 손상된 총 4개 등급이 있으며, 처음에는
[운석](../ae2-mechanics/meteorites.md)에서 찾을 수 있습니다.

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/budding_blocks.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

봉오리가 다음 성장 단계로 넘어갈 때마다 싹 틔우는 블록은 한 등급 낮아질 수 있으며, 결국 평범한
서투스 석영 블록이 됩니다. 싹 틔우는 블록 또는 서투스 석영 블록을 하나 이상의
<ItemLink id="charged_certus_quartz_crystal" />과 함께 물에 던지면 복구할 수 있고, 새로운 싹 틔우는
블록도 만들 수 있습니다.

<RecipeFor id="damaged_budding_quartz" />

흠잡을 데 없는 싹 틔우는 서투스 석영 블록은 등급이 낮아지지 않아 서투스를 무한히 생산합니다.
하지만 제작할 수 없으며, 섬세한 손길이 붙은 곡괭이로도 옮길 수 없습니다. 단,
[공간 저장소](../ae2-mechanics/spatial-io.md)를 사용하면 옮길 수 있습니다.

서투스 석영 봉오리는 그대로 두면 매우 느리게 자랍니다. 다행히 <ItemLink id="growth_accelerator" />를
싹 틔우는 블록 옆에 놓으면 성장 속도가 크게 빨라집니다. 가장 먼저 몇 개 만들어 두는 것이 좋습니다.

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/budding_certus_2.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

싹 틔우는 블록은 각 면이 가려질 때마다 전체 성장 속도가 느려지는 복잡한 상호작용이 있습니다. 이 효과는
가속기를 더 설치해서 얻는 이점보다 결국 더 커집니다. 실제 실험에서 확인한 결과는 다음과 같습니다.

![비율별 분당 아이템 수](../assets/diagrams/certus_farm_speed_chart_1.png)

![일반적인 구성](../assets/diagrams/certus_farm_speed_chart_2.png)

<ItemLink id="energy_acceptor" />나 <ItemLink id="vibration_chamber" />까지 만들 석영이 부족하다면,
<ItemLink id="crank" />을 만들어 수정 성장 가속기 끝에 붙일 수 있습니다.

서투스 석영을 자동으로 수확하는 방법은 [여기](../example-setups/simple-certus-farm.md)에 설명되어 있습니다.
