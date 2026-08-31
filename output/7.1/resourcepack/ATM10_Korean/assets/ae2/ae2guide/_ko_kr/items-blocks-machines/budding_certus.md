---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 싹 틔우는 서투스 석영
  icon: flawless_budding_quartz
  position: 010
categories:
- misc ingredients blocks
item_ids:
- ae2:flawless_budding_quartz
- ae2:flawed_budding_quartz
- ae2:chipped_budding_quartz
- ae2:damaged_budding_quartz
- ae2:small_quartz_bud
- ae2:medium_quartz_bud
- ae2:large_quartz_bud
- ae2:quartz_cluster
---

# 싹 틔우는 서투스 석영

([서투스 성장](../ae2-mechanics/certus-growth.md)도 참고하세요.)

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/budding_blocks.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

자수정처럼 싹 틔우는 서투스 블록에서 서투스 석영 싹이 자랍니다. 이 블록은 [운석](../ae2-mechanics/meteorites.md)에서 발견됩니다.
싹 틔우는 서투스 블록에는 흠잡을 데 없는, 흠 있는, 깎인, 손상된 블록의 4등급이 있습니다.
HWYLA, Jade, The One Probe 같은 모드나 F3 화면으로 가장 쉽게 구분할 수 있습니다.

흠 있는, 깎인, 손상된 싹 틔우는 서투스 블록에서는 싹이 한 단계 자랄 때마다 블록이 일정 확률로 한 등급 열화하며,
결국 일반 <ItemLink id="quartz_block" />이 됩니다.

흠잡을 데 없는 싹 틔우는 서투스 석영은 싹이 자라도 열화하지 않으므로 무한한 공급원으로 쓸 수 있습니다.

싹 틔우는 서투스 블록을 일반 곡괭이로 부수면 한 등급 열화합니다. 섬세한 손길 마법이 부여된 곡괭이로 부수면
열화하지 않지만, 흠잡을 데 없는 블록은 예외입니다. **즉, 흠잡을 데 없는 싹 틔우는 서투스 블록은 곡괭이로
회수해 옮길 수 없습니다.** 대신 [공간 저장소](../ae2-mechanics/spatial-io.md)를 사용하면 흠잡을 데 없는 싹 틔우는 블록을
잘라내 붙이듯 옮길 수 있습니다.

## 조합법

흠 있는, 깎인, 손상된 싹 틔우는 서투스 블록은 이전 등급 블록(또는 <ItemLink id="quartz_block" />)과
하나 이상의 <ItemLink id="charged_certus_quartz_crystal" />을 물에 던져 제작할 수 있습니다.

흠잡을 데 없는 싹 틔우는 서투스 석영은 제작할 수 없으며 월드에서만 발견됩니다.

<Row>
  <RecipeFor id="damaged_budding_quartz" />

  <RecipeFor id="chipped_budding_quartz" />

  <RecipeFor id="flawed_budding_quartz" />
</Row>
