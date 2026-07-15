---
navigation:
  title: 시작하기 (1.20+)
  position: 10
---

<div class="notification is-info">
  다음 내용은 Minecraft 1.20 이상 버전의 Applied Energistics 2에만 적용됩니다.
</div>

# 시작하기

## 첫 재료 구하기

<GameScene zoom="4" background="transparent">
  <ImportStructure src="assets/assemblies/meteor_interior.snbt" />
</GameScene>

Applied Energistics 2를 시작하려면 먼저 [운석](ae2-mechanics/meteorites.md)을 찾아야 합니다. 운석은
제법 흔하고 지형에 커다란 구덩이를 남기므로, 여행 중에 이미 본 적이 있을지도 모릅니다.
아직 찾지 못했다면 <ItemLink id="meteorite_compass" />를 제작하세요. 이 탐지기는 가장 가까운
<ItemLink id="mysterious_cube" />를 가리킵니다.

운석을 찾았다면 중심부까지 파고 들어가세요. 그곳에서 서투스 석영 군집과 서투스 석영 봉오리,
여러 등급의 [싹 틔우는 서투스 석영 블록](items-blocks-machines/budding_certus.md), 그리고 중심에
놓인 신비한 큐브를 찾을 수 있습니다.

서투스 석영 군집과 발견한 서투스 석영 블록을 채굴하세요. 싹 틔우는 서투스 석영 블록도 가져갈 수
있지만, 섬세한 손길 없이 캐면 한 등급 낮아집니다.

흠잡을 데 없는 싹 틔우는 서투스 석영은 부수지 마세요. 섬세한 손길을 사용해도 흠 있는 싹 틔우는
서투스 석영으로 낮아지며, 다시 흠잡을 데 없는 등급으로 복구할 수 없습니다.

운석 중심의 신비한 큐브도 채굴하여 각인기 프레스 4종을 모두 얻으세요.

## 서투스 석영 성장시키기

<GameScene zoom="4" background="transparent">
<ImportStructure src="assets/assemblies/budding_certus_1.snbt" />
</GameScene>

자수정과 비슷하게, 서투스 석영 봉오리는 [싹 틔우는 서투스 석영 블록](items-blocks-machines/budding_certus.md)에서
자라납니다. 다 자라지 않은 봉오리를 부수면 행운의 영향을 받지 않고
<ItemLink id="certus_quartz_dust" /> 1개가 나옵니다. 완전히 자란 군집을 부수면
<ItemLink id="certus_quartz_crystal" /> 4개가 나오며, 행운을 사용하면 수량이 늘어납니다.

싹 틔우는 서투스 석영 블록에는 흠잡을 데 없는, 흠 있는, 깎인, 손상된 총 4개 등급이 있습니다.

<GameScene zoom="4" background="transparent">
<ImportStructure src="assets/assemblies/budding_blocks.snbt" />
<IsometricCamera yaw="195" pitch="30" />
</GameScene>

봉오리가 다음 성장 단계로 넘어갈 때마다 싹 틔우는 블록은 한 등급 낮아질 수 있으며, 결국 평범한
서투스 석영 블록이 됩니다. 싹 틔우는 블록 또는 서투스 석영 블록을 하나 이상의
<ItemLink id="charged_certus_quartz_crystal" />과 함께 물에 던지면 복구할 수 있고, 새로운 싹 틔우는
블록도 만들 수 있습니다.

<RecipeFor id="damaged_budding_quartz" />

흠잡을 데 없는 싹 틔우는 서투스 석영 블록은 등급이 낮아지지 않아 서투스를 무한히 생산합니다.
하지만 제작할 수 없으며, 섬세한 손길이 붙은 곡괭이로도 옮길 수 없습니다. 단,
[공간 저장소](ae2-mechanics/spatial-io.md)를 사용하면 옮길 수 있습니다.

서투스 석영 봉오리는 그대로 두면 매우 느리게 자랍니다. 다행히 <ItemLink id="growth_accelerator" />를
싹 틔우는 블록 옆에 놓으면 성장 속도가 크게 빨라집니다. 가장 먼저 몇 개 만들어 두는 것이 좋습니다.

<GameScene zoom="4" background="transparent">
<ImportStructure src="assets/assemblies/budding_certus_2.snbt" />
<IsometricCamera yaw="195" pitch="30" />
</GameScene>

<ItemLink id="energy_acceptor" />나 <ItemLink id="vibration_chamber" />까지 만들 석영이 부족하다면,
<ItemLink id="crank" />을 만들어 수정 성장 가속기 끝에 붙일 수 있습니다.

서투스 석영을 자동으로 수확하는 방법은 [여기](example-setups/simple-certus-farm.md)에 설명되어 있습니다.

## 플루익스 간단히 알아보기

수정 성장 가속기를 만들면서 이미 접했겠지만, 플루익스도 필요한 재료입니다. 충전된 서투스 석영,
레드스톤, 네더 석영을 물에 던지면 만들 수 있습니다. 이 과정을 자동화하는 방법은 "독자 여러분의
연습 문제로 남겨 둡니다."

아직 만들지 않았다면 <ItemLink id="charger" />가 필요합니다. 충전기는
<ItemLink id="charged_certus_quartz_crystal" />을 생산하는 데 사용합니다.

## 프로세서 회로 인쇄하기

운석의 신비한 큐브를 부쉈다면 네 종류의 "프레스"를 얻었을 것입니다. 이 프레스는
<ItemLink id="inscriber" />에서 세 종류의 프로세서를 만드는 데 사용합니다.

<ItemGrid>
  <ItemIcon id="silicon_press" />

  <ItemIcon id="logic_processor_press" />

  <ItemIcon id="calculation_processor_press" />

  <ItemIcon id="engineering_processor_press" />
</ItemGrid>

각인기는 일반 화로처럼 면에 따라 입출력 위치가 달라지는 기계입니다. 위나 아래에서 넣으면 각각
위쪽 또는 아래쪽 슬롯으로 들어가고, 옆이나 뒤에서 넣으면 가운데 슬롯으로 들어갑니다. 결과물은 옆이나
뒤에서 꺼낼 수 있습니다.

깔때기를 이용한 자동화를 편하게 하고 복잡하게 얽힌 파이프를 줄이기 위해, 각인기는
<ItemLink id="certus_quartz_wrench" />로 방향을 돌릴 수 있습니다.

다음 단계인 아주 기초적인 ME 시스템을 준비하도록 각 프로세서를 몇 개씩 만드세요. 프로세서 생산
자동화는 "[독자 여러분의 연습 문제로 남겨 둡니다](example-setups/processor-automation.md)".

## 물질 에너지 기술: ME 네트워크와 저장소

### ME 저장소란?

ME는 물질 에너지(Matter Energy)의 약자이며, 영어로는 각 글자를 따로 읽습니다.

물질 에너지는 Applied Energistics 2의 핵심 요소입니다. 괴짜 과학자가 만든 다중 블록 상자와 비슷하며,
기존의 저장 환경을 완전히 바꿀 수 있습니다. ME는 Minecraft의 다른 저장 시스템과 매우 달라 익숙해지려면
조금 색다른 사고가 필요할 수 있습니다. 하지만 일단 시작하고 나면 좁은 공간에 엄청난 양을 저장하고 여러
터미널에서 접근하는 것은 수많은 가능성의 시작에 불과합니다.

### 시작하려면 무엇을 알아야 하나요?

먼저 ME는 아이템을 [저장 셀](items-blocks-machines/storage_cells.md)이라는 다른 아이템 안에 저장합니다.
저장 공간이 점점 커지는 5개 등급이 있습니다. 저장 셀을 사용하려면 <ItemLink id="chest" /> 또는
<ItemLink id="drive" /> 안에 넣어야 합니다.

<ItemLink id="chest" />에 셀을 넣으면 곧바로 내용물이 표시되며, <ItemLink id="minecraft:chest" />처럼
아이템을 넣고 꺼낼 수 있습니다. 단, 아이템은 <ItemLink id="chest" /> 자체가 아니라 저장 셀 안에
실제로 보관됩니다.

<ItemLink id="chest" />는 쓰임새가 제한적이고 특정 상황에만 유용합니다. AE2의 장점을 제대로
활용하려면 [ME 네트워크](ae2-mechanics/me-network-connections.md)를 구성해야 합니다.

## 첫 ME 시스템 만들기

이제 Applied Energistics 2의 기본 재료와 기계를 모두 갖췄으므로 첫 ME(물질 에너지) 시스템을 만들 수
있습니다. 자동 제작이나 물류 기능 없이, 단순하고 검색하기 편한 저장소만 갖춘 매우 기초적인 시스템입니다.

<GameScene zoom="6" interactive={true}>
<ImportStructure src="assets/assemblies/tiny_me_system.snbt" />

</GameScene>

*   필요한 재료:
    * <ItemLink id="drive" /> 1개
    * <ItemLink id="terminal" /> 또는 <ItemLink id="crafting_terminal" /> 1개
    * <ItemLink id="energy_acceptor" /> 1개
    * [케이블](items-blocks-machines/cables.md) 몇 개. 유리, 차폐, 스마트 케이블은 가능하지만 조밀 케이블은 제외
    * [저장 셀](items-blocks-machines/storage_cells.md) 몇 개. 용량과 종류 수의 균형이 좋은 4k 등급을 권장합니다.
    4k와 1k 셀을 섞어 [파티션](items-blocks-machines/cell_workbench.md)을 설정하면 더 효율적이지만,
    여기서는 그 복잡한 내용까지 다루지 않습니다.
---
1.  ME 드라이브를 놓습니다.
2.  에너지 수용기와 일부 AE2 [장치](ae2-mechanics/devices.md)는 정육면체와 평면 형태를 지원합니다.
    제작 격자에서 두 형태를 서로 바꿀 수 있습니다. 에너지 수용기가 정육면체라면 ME 드라이브 옆에
    놓으세요. 평평한 형태라면 ME 드라이브에 케이블을 놓고 그 케이블에 수용기를 설치하세요.
3.  원하는 발전 모드의 케이블, 파이프 또는 도관으로 에너지 수용기에 에너지를 공급합니다.
4.  ME 드라이브 위쪽이나 눈높이에 케이블을 놓고 ME 터미널 또는 ME 제작 터미널을 설치합니다.
5.  저장 셀을 ME 드라이브에 넣습니다.
6.  이익을 누립니다.
7.  터미널 설정을 이것저것 조정합니다.
8.  궁극의 힘과 능력을 만끽합니다.
9.  전체 규모로 보면 이 네트워크가 아직 꽤 작다는 사실을 깨닫습니다.

### 네트워크 확장하기

기초적인 저장소와 접근 수단을 갖췄으니 좋은 출발입니다. 이제 가공 자동화를 시도하고 싶을 것입니다.

좋은 예로, 화로 위쪽에 <ItemLink id="export_bus" />를 설치해 광석을 넣고 화로 아래쪽에
<ItemLink id="import_bus" />를 설치해 제련된 광물을 꺼낼 수 있습니다.

<ItemLink id="export_bus" />는 네트워크의 아이템을 연결된 인벤토리로 내보내며,
<ItemLink id="import_bus" />는 연결된 인벤토리의 아이템을 네트워크로 가져옵니다.

### 한계 극복하기

이쯤이면 [장치](ae2-mechanics/devices.md)가 8개 정도에 가까워졌을 것입니다. 장치가 9개가 되면
[채널](ae2-mechanics/channels.md)을 관리해야 합니다. 모든 장치가 그런 것은 아니지만, 많은 장치가
작동하려면 채널을 사용합니다.

기본적으로 네트워크 하나는 채널 8개를 지원합니다. 이 한계를 넘으려면 네트워크에
<ItemLink id="controller" />를 추가해야 합니다. 그러면 네트워크를 크게 확장할 수 있습니다.
[스마트 케이블](items-blocks-machines/cables.md)을 사용하면 채널이 네트워크를 따라 전달되는 모습을
볼 수 있습니다. 처음 채널의 작동 방식을 배울 때나 레드스톤과 발광석이 충분할 때 적극 활용하세요.
