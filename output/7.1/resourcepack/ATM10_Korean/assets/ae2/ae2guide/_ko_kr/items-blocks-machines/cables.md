---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 케이블
  icon: fluix_glass_cable
  position: 110
categories:
- network infrastructure
item_ids:
- ae2:white_glass_cable
- ae2:orange_glass_cable
- ae2:magenta_glass_cable
- ae2:light_blue_glass_cable
- ae2:yellow_glass_cable
- ae2:lime_glass_cable
- ae2:pink_glass_cable
- ae2:gray_glass_cable
- ae2:light_gray_glass_cable
- ae2:cyan_glass_cable
- ae2:purple_glass_cable
- ae2:blue_glass_cable
- ae2:brown_glass_cable
- ae2:green_glass_cable
- ae2:red_glass_cable
- ae2:black_glass_cable
- ae2:fluix_glass_cable
- ae2:white_covered_cable
- ae2:orange_covered_cable
- ae2:magenta_covered_cable
- ae2:light_blue_covered_cable
- ae2:yellow_covered_cable
- ae2:lime_covered_cable
- ae2:pink_covered_cable
- ae2:gray_covered_cable
- ae2:light_gray_covered_cable
- ae2:cyan_covered_cable
- ae2:purple_covered_cable
- ae2:blue_covered_cable
- ae2:brown_covered_cable
- ae2:green_covered_cable
- ae2:red_covered_cable
- ae2:black_covered_cable
- ae2:fluix_covered_cable
- ae2:white_covered_dense_cable
- ae2:orange_covered_dense_cable
- ae2:magenta_covered_dense_cable
- ae2:light_blue_covered_dense_cable
- ae2:yellow_covered_dense_cable
- ae2:lime_covered_dense_cable
- ae2:pink_covered_dense_cable
- ae2:gray_covered_dense_cable
- ae2:light_gray_covered_dense_cable
- ae2:cyan_covered_dense_cable
- ae2:purple_covered_dense_cable
- ae2:blue_covered_dense_cable
- ae2:brown_covered_dense_cable
- ae2:green_covered_dense_cable
- ae2:red_covered_dense_cable
- ae2:black_covered_dense_cable
- ae2:fluix_covered_dense_cable
- ae2:white_smart_cable
- ae2:orange_smart_cable
- ae2:magenta_smart_cable
- ae2:light_blue_smart_cable
- ae2:yellow_smart_cable
- ae2:lime_smart_cable
- ae2:pink_smart_cable
- ae2:gray_smart_cable
- ae2:light_gray_smart_cable
- ae2:cyan_smart_cable
- ae2:purple_smart_cable
- ae2:blue_smart_cable
- ae2:brown_smart_cable
- ae2:green_smart_cable
- ae2:red_smart_cable
- ae2:black_smart_cable
- ae2:fluix_smart_cable
- ae2:white_smart_dense_cable
- ae2:orange_smart_dense_cable
- ae2:magenta_smart_dense_cable
- ae2:light_blue_smart_dense_cable
- ae2:yellow_smart_dense_cable
- ae2:lime_smart_dense_cable
- ae2:pink_smart_dense_cable
- ae2:gray_smart_dense_cable
- ae2:light_gray_smart_dense_cable
- ae2:cyan_smart_dense_cable
- ae2:purple_smart_dense_cable
- ae2:blue_smart_dense_cable
- ae2:brown_smart_dense_cable
- ae2:green_smart_dense_cable
- ae2:red_smart_dense_cable
- ae2:black_smart_dense_cable
- ae2:fluix_smart_dense_cable
---

# 케이블

<GameScene zoom="3" background="transparent">
  <ImportStructure src="../assets/assemblies/cables.snbt" />
  <IsometricCamera yaw="180" pitch="30" />
</GameScene>

ME 기능이 있는 기계를 서로 맞대어도 ME 네트워크가 형성되지만, 넓은 지역으로 ME 네트워크를 확장하는 주된 방법은 케이블입니다.

서로 다른 색의 케이블은 맞닿아도 연결되지 않으므로 [채널](../ae2-mechanics/channels.md)을 더 효율적으로 분배할 수 있습니다.
연결된 터미널의 색에도 영향을 주므로 모든 터미널을 보라색으로 둘 필요가 없습니다. 플루익스 케이블은 모든 색과 연결됩니다.

중요하게도 **채널은 케이블 색상과 아무 관계가 없습니다.**

## 중요한 참고 사항

**AE2가 처음이고 채널에 익숙하지 않다면 가능한 모든 곳에 스마트 케이블과 조밀한 스마트 케이블을 사용하세요.
네트워크에서 채널이 지나가는 경로를 보여 주어 작동 방식을 이해하기 쉬워집니다.**

## 또 다른 참고 사항

**이 케이블은 아이템, 유체, 에너지 등을 운반하는 파이프가 아닙니다.** 내부 인벤토리가 없고 패턴 공급기와 기계가
내용물을 케이블 안으로 "밀어 넣지" 않습니다. AE2 [장치](../ae2-mechanics/devices.md)를 네트워크로 연결할 뿐입니다.

## 유리 케이블

<GameScene zoom="6" background="transparent">
<ImportStructure src="../assets/assemblies/fluix_glass_cable.snbt" />
<IsometricCamera yaw="195" pitch="30" />
</GameScene>

<ItemLink id="fluix_glass_cable" />은 가장 만들기 쉬운 케이블로 전력과 최대 8개의 [채널](../ae2-mechanics/channels.md)을 전달합니다.
기본 플루익스 색을 포함해 17가지 색상이 있으며 16종의 염료로 원하는 색을 입힐 수 있습니다.

색 케이블을 제작하려면 같은 종류의 케이블 8개로 염료를 둘러싸세요. 케이블의 색은 상관없지만
유리, 스마트 등 종류는 같아야 합니다. 월드에서 Forge 호환 페인트 붓으로 케이블을 칠할 수도 있습니다.

색 케이블을 물 양동이와 함께 제작하면 염료를 제거할 수 있습니다.

케이블을 양털로 덮어 <ItemLink id="fluix_covered_cable" />을 만들 수 있고, <ItemLink id="fluix_smart_cable" />을 제작하면
[채널](../ae2-mechanics/channels.md)의 상태를 더 쉽게 파악할 수 있습니다.

<RecipeFor id="fluix_glass_cable" />

<RecipeFor id="blue_glass_cable" />

## 피복 케이블

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/fluix_covered_cable.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

피복 케이블은 <ItemLink id="fluix_glass_cable" />보다 기능적으로 나은 점은 없지만, 피복된 외형을 선호할 때 장식용으로 선택할 수 있습니다.

<ItemLink id="fluix_glass_cable" />과 같은 방식으로 색을 입힐 수 있습니다. <ItemLink id="fluix_covered_cable" /> 4개를
레드스톤 및 발광석과 조합하면 <ItemLink id="fluix_covered_dense_cable" />을 만들 수 있습니다.

<Recipe id="network/cables/covered_fluix" />

<RecipeFor id="blue_covered_cable" />

## 조밀한 케이블

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/fluix_covered_dense_cable.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

표준 케이블은 채널을 8개만 전달하지만 조밀한 케이블은 32개를 전달합니다. 다만 버스를 지원하지 않으므로
버스나 패널을 사용하기 전에 <ItemLink id="fluix_glass_cable" /> 또는 <ItemLink id="fluix_smart_cable" /> 같은
작은 케이블로 바꿔 연결해야 합니다.

조밀한 케이블은 채널의 "최단 경로" 동작을 일부 덮어씁니다. 채널은 조밀한 케이블까지 최단 경로를 택한 뒤,
그 조밀한 케이블을 통해 제어기까지 가는 최단 경로를 택합니다.

<Recipe id="network/cables/dense_covered_fluix" />

<RecipeFor id="blue_covered_dense_cable" />

## 스마트 케이블

<Row>
<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/fluix_smart_cable.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>
<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/fluix_smart_dense_cable.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>
</Row>

외형은 <ItemLink id="fluix_covered_cable" />과 비슷하지만 케이블의 채널 사용량을 시각화하는 진단 기능이 있습니다.
채널은 케이블의 검은 띠를 따라 빛나는 색 선으로 표시되어 네트워크에서 채널이 어떻게 사용되는지 보여 줍니다.
일반 스마트 케이블은 처음 네 채널을 케이블 색과 같은 선으로, 다음 네 채널을 흰 선으로 표시합니다.
조밀한 스마트 케이블에서는 선 하나가 채널 4개를 나타냅니다.

<ItemLink id="controller" />가 있는 네트워크에서는 케이블의 선이 채널의 정확한 경로를 보여 줍니다.

임시 네트워크의 스마트 케이블은 해당 케이블을 흐르는 채널 수 대신 네트워크 전체에서 사용 중인 채널 수를 표시합니다.

<ItemLink id="fluix_glass_cable" />과 같은 방식으로 색을 입힐 수도 있습니다.

<Recipe id="network/cables/smart_fluix" />

<Recipe id="network/cables/dense_smart_fluix" />

<RecipeFor id="blue_smart_cable" />
