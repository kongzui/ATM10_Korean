---
navigation:
  parent: example-setups/example-setups-index.md
  title: 자수정 농장
  icon: minecraft:amethyst_shard
---

# 자수정 농사

<ItemLink id="growth_accelerator" />는 자수정에도 작동하지만 <ItemLink id="annihilation_plane" />을 이용해
[서투스 봉오리](../items-blocks-machines/budding_certus.md)를 필터링하는 일반적인 방법은 자수정 봉오리에
통하지 않습니다. 다 자라지 않은 서투스 봉오리는 <ItemLink id="certus_quartz_dust" />를 떨어뜨리지만,
다 자라지 않은 자수정 봉오리는 아무것도 떨어뜨리지 않습니다. 네트워크는 언제나 "아무것도 없음"을
저장할 수 있으므로 소멸 평면이 자수정 봉오리를 항상 부수게 됩니다.

이를 피하려면 소멸 평면에 섬세한 손길을 부여하세요. 그러면 다 자라지 않은 자수정 봉오리도 여러 성장
단계의 실제 봉오리 블록을 떨어뜨리므로 필터링할 수 있습니다.

그런 다음 <ItemLink id="minecraft:amethyst_cluster" />을 <ItemLink id="formation_plane" />으로 다시
놓고, 섬세한 손길이 없는 <ItemLink id="annihilation_plane" />으로 다시 부숴
<ItemLink id="minecraft:amethyst_shard" />을 얻어야 합니다.

군집에는 방향이 있으므로 형성 평면의 정반대쪽에 단단한 블록 면이 있어야 합니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/amethyst_farm.snbt" />

  <BoxAnnotation color="#dddddd" min="2.7 1 1" max="3 2 2">
        (1) 소멸 평면 1: 설정할 GUI는 없으며 섬세한 손길을 부여합니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2 1 1" max="2.3 2 2">
        (2) 형성 평면: 자수정 군집으로 필터링합니다.
        <ItemImage id="minecraft:amethyst_cluster" scale="2" />
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="1.3 0.7 1" max="2 1 2">
        (3) 소멸 평면 2: 설정할 GUI는 없지만 행운을 부여할 수 있습니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="1 0 1" max="1.3 1 2">
        (4) 저장 버스 1: 자수정 조각으로 필터링합니다.
        <ItemImage id="minecraft:amethyst_shard" scale="2" />
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="0 0 .7" max="1 1 1">
        (5) 저장 버스 2: 자수정 조각으로 필터링하며 주 저장소보다 높은 우선순위를 설정합니다.
        <ItemImage id="minecraft:amethyst_shard" scale="2" />
  </BoxAnnotation>

<DiamondAnnotation pos="0 0.5 0.5" color="#00ff00">
        주 네트워크로 연결
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 설정

* 첫 번째 <ItemLink id="annihilation_plane" /> (1)은 설정할 GUI가 없으며 섬세한 손길을 부여해야 합니다.
* <ItemLink id="formation_plane" /> (2)는 <ItemLink id="minecraft:amethyst_cluster" />으로 필터링합니다.
* 두 번째 <ItemLink id="annihilation_plane" /> (3)은 설정할 GUI가 없지만 행운을 부여할 수 있습니다.
* 첫 번째 <ItemLink id="storage_bus" /> (4)는 <ItemLink id="minecraft:amethyst_shard" />으로 필터링합니다.
* 두 번째 <ItemLink id="storage_bus" /> (5)도 <ItemLink id="minecraft:amethyst_shard" />으로 필터링하며,
  [우선순위](../ae2-mechanics/import-export-storage.md#storage-priority)를 주 저장소보다 높게 설정합니다.

## 작동 방식

1. 첫 번째 <ItemLink id="annihilation_plane" />은 앞의 블록을 부수려 하지만
   <ItemLink id="minecraft:amethyst_cluster" />만 부술 수 있습니다. 서브네트워크의 유일한 저장소인
   <ItemLink id="formation_plane" />이 자수정 군집으로 필터링되어 있기 때문입니다. 평면에 섬세한 손길이 있어야만
   작동합니다. 그렇지 않으면 다 자라지 않은 봉오리가 아무것도 떨어뜨리지 않아 평면이 부술 수 있습니다.
2. <ItemLink id="formation_plane" />은 반대편 블록 면에 군집을 놓습니다.
3. 두 번째 <ItemLink id="annihilation_plane" />이 군집을 부숴
   <ItemLink id="minecraft:amethyst_shard" />을 만듭니다.
4. 첫 번째 <ItemLink id="storage_bus" />는 조각을 통에 저장합니다. 두 번째 소멸 평면이 완전히 자란
   군집만 만나야 하므로 엄밀히는 필터가 없어도 됩니다.
5. 두 번째 <ItemLink id="storage_bus" />는 주 네트워크가 통의 모든 자수정 조각에 접근하게 합니다.
   [우선순위](../ae2-mechanics/import-export-storage.md#storage-priority)가 높으므로 조각은 주 저장소보다 통에
   우선적으로 돌아갑니다.
