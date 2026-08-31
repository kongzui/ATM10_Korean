---
navigation:
  parent: example-setups/example-setups-index.md
  title: 간단한 서투스 농장
  icon: certus_quartz_crystal
  position: 110
---

# 간단한 서투스 농장

[서투스 성장](../ae2-mechanics/certus-growth.md)에서 설명했듯 <ItemLink id="certus_quartz_crystal" /> 자동
수확에는 <ItemLink id="annihilation_plane" />과 <ItemLink id="storage_bus" />를 사용합니다.
<ItemLink id="growth_accelerator" />로 서투스 석영 봉오리의 성장 속도를 크게 높인 다음 완전히 자란
<ItemLink id="quartz_cluster" />을 평면으로 부숩니다. 다 자라지 않은 서투스 봉오리는 아무것도 나오지
않는 대신 <ItemLink id="certus_quartz_dust" />를 떨어뜨린다는 절묘한 특성을 이용해 필터링합니다.

<ItemLink id="flawless_budding_quartz" />을 사용하면 완전히 자동으로 작동합니다. 흠 있는, 깎인, 손상된
싹 틔우는 서투스 석영을 사용하면 블록을 수동으로 교체해야 합니다. 또는
[반자동 서투스 농장](semiauto-certus-farm.md)과 [고급 서투스 농장](advanced-certus-farm.md)에서 설명하는
방식으로 자동화할 수 있습니다.

예상 속도는 [서투스 성장](../ae2-mechanics/certus-growth.md)을 참고하세요.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/simple_certus_farm.snbt" />

  <BoxAnnotation color="#dddddd" min="3.7 1 1" max="4 2 2">
        (1) 소멸 평면: 설정할 GUI는 없지만 행운을 부여할 수 있습니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="3 1 1" max="3.3 2 2">
        (2) 저장 버스 1: 서투스 석영 수정으로 필터링합니다.
        <ItemImage id="certus_quartz_crystal" scale="2" />
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="3 1 .7" max="2 2 1">
        (3) 저장 버스 2: 서투스 석영 수정으로 필터링하며 주 저장소보다 높은 우선순위를 설정합니다.
        <ItemImage id="certus_quartz_crystal" scale="2" />
  </BoxAnnotation>

<DiamondAnnotation pos="1 0.5 0.5" color="#00ff00">
        주 네트워크로 연결
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 설정

* 첫 번째 <ItemLink id="annihilation_plane" /> (1)은 설정할 GUI가 없지만 행운을 부여할 수 있습니다.
* 첫 번째 <ItemLink id="storage_bus" /> (2)는 <ItemLink id="certus_quartz_crystal" />로 필터링합니다.
* 두 번째 <ItemLink id="storage_bus" /> (3)도 <ItemLink id="certus_quartz_crystal" />로 필터링하며,
  [우선순위](../ae2-mechanics/import-export-storage.md#storage-priority)를 주 저장소보다 높게 설정합니다.

## 작동 방식

1. <ItemLink id="annihilation_plane" />은 앞의 블록을 부수려 하지만 <ItemLink id="quartz_cluster" />만
   부술 수 있습니다. 서브네트워크의 유일한 저장소인 <ItemLink id="storage_bus" />가
   <ItemLink id="certus_quartz_crystal" />로 필터링되어 있기 때문입니다.
4. 첫 번째 <ItemLink id="storage_bus" />는 서투스 석영 수정을 통에 저장합니다.
5. 두 번째 <ItemLink id="storage_bus" />는 주 네트워크가 통의 모든 서투스 석영 수정에 접근하게 합니다.
   [우선순위](../ae2-mechanics/import-export-storage.md#storage-priority)가 높으므로 수정은 주 저장소보다 통에
   우선적으로 돌아갑니다.
