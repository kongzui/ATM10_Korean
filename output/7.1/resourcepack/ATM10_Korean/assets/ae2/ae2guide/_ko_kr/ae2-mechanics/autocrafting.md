---
navigation:
  parent: ae2-mechanics/ae2-mechanics-index.md
  title: 자동 제작
  icon: pattern_provider
---

# 자동 제작

### 가장 중요한 기능

<GameScene zoom="4" interactive={true}>
  <ImportStructure src="../assets/assemblies/autocraft_setup_greebles.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

자동 제작은 AE2의 핵심 기능 중 하나입니다. 하위 재료를 정확한 수량만큼 일일이 만들며 *고생하는* 대신
ME 시스템에 요청할 수 있습니다. 아이템을 자동으로 제작해 원하는 곳으로 반출하거나, 여러 기능을
영리하게 조합해 특정 수량을 항상 비축할 수도 있습니다. 유체도 지원하며, Mekanism 기체처럼 다른
모드의 추가 재료 종류를 지원하는 애드온이 있다면 그런 재료도 사용할 수 있습니다. 정말 유용합니다.

상당히 복잡한 주제이므로 차근차근 살펴보겠습니다.

자동 제작 구성은 세 요소로 이루어집니다.
- 제작 요청을 보내는 요소
- 제작 CPU
- <ItemLink id="pattern_provider" />

작동 순서는 다음과 같습니다.

1.  무언가가 제작 요청을 만듭니다. 터미널에서 자동 제작 가능한 항목을 플레이어가 클릭할 수도 있고,
    제작 카드가 설치된 반출 버스나 인터페이스가 반출·비축하도록 설정된 아이템을 요청할 수도 있습니다.

*   (**중요:** 이미 비축 중인 아이템의 제작을 요청하려면 "블록 선택"에 지정된 키, 보통 마우스 가운데
    버튼을 사용하세요. 인벤토리 정렬 모드와 충돌할 수 있습니다.)

2.  ME 시스템이 요청을 완료하는 데 필요한 재료와 선행 제작 단계를 계산하여 선택된 제작 CPU에 저장합니다.

3.  관련 [패턴](../items-blocks-machines/patterns.md)이 들어 있는 <ItemLink id="pattern_provider" />가
    패턴에 지정된 재료를 인접한 인벤토리로 밀어냅니다. 제작대 조합법인 "제작 패턴"은
    <ItemLink id="molecular_assembler" />로 보냅니다. 일반 제작이 아닌 "가공 패턴"은 다른 블록이나
    기계, 또는 정교한 레드스톤 제어 장치로 보냅니다.

4.  제작 결과는 반입 버스, 인터페이스 또는 패턴 공급기로 다시 밀어 넣는 등의 방법으로 시스템에
    반환됩니다. **반드시 "아이템이 시스템에 들어오는" 사건이 발생해야 합니다. <ItemLink id="storage_bus" />가
    붙은 상자로 결과물을 보내기만 해서는 안 됩니다.**

5.  해당 제작이 요청 안의 다른 제작에 필요한 선행 단계라면, 결과물을 제작 CPU에 저장했다가 다음
    제작에 사용합니다.

## 재귀 조합법

<ItemImage id="minecraft:netherite_upgrade_smithing_template" scale="4" />

자동 제작 알고리즘이 처리하지 *못하는* 것 중 하나가 재귀 조합법입니다. Botania 마나 웅덩이에 레드스톤을
던져 "레드스톤 가루 1개 = 레드스톤 가루 2개"로 복제하는 조합법이나 기본 Minecraft의 대장장이 형판이
그 예입니다. 하지만 [이런 조합법을 처리하는 방법](../example-setups/recursive-crafting-setup.md)이 있습니다.

# 패턴

<ItemImage id="crafting_pattern" scale="4" />

패턴 인코딩 터미널인 <ItemLink id="pattern_encoding_terminal" />에서 빈 패턴으로 패턴을 만듭니다.

용도에 따라 여러 종류의 패턴이 있습니다.

*   <ItemLink id="crafting_pattern" />은 제작대 조합법을 기록합니다. <ItemLink id="molecular_assembler" />에
    직접 넣어 재료가 공급될 때마다 결과물을 만들 수도 있지만, 주된 용도는 분자 조립기 옆의
    <ItemLink id="pattern_provider" />에 넣는 것입니다. 이 구성에서 패턴 공급기는 특별하게 작동하여
    관련 패턴 정보와 재료를 인접한 조립기로 함께 보냅니다. 조립기는 제작 결과를 인접 인벤토리로 자동
    배출하므로 패턴 공급기에 붙은 조립기만으로 제작 패턴을 자동화할 수 있습니다.

***

*   <ItemLink id="smithing_table_pattern" />은 제작 패턴과 매우 비슷하지만 대장장이 작업대 조합법을
    기록합니다. 패턴 공급기와 분자 조립기로 같은 방식으로 자동화합니다. 제작, 대장장이 작업대와
    석재 절단 패턴은 실제로 같은 구성에서 사용할 수 있습니다.

***

*   <ItemLink id="stonecutting_pattern" />은 제작 패턴과 매우 비슷하지만 석재 절단기 조합법을 기록합니다.
    패턴 공급기와 분자 조립기로 같은 방식으로 자동화합니다. 제작, 대장장이 작업대와 석재 절단 패턴은
    실제로 같은 구성에서 사용할 수 있습니다.

***

*   <ItemLink id="processing_pattern" />은 자동 제작에 매우 큰 유연성을 제공합니다. 가장 범용적인
    패턴으로, "패턴 공급기가 이 재료들을 인접 인벤토리로 밀어내면 가까운 미래나 먼 미래의 어느 시점에
    ME 시스템이 이 결과물을 받는다"라고 정의할 뿐입니다. 거의 모든 모드 기계와 화로 등을 자동 제작에
    사용할 때 쓰입니다. 재료를 보낸 뒤 결과를 받기까지 무슨 일이 일어나는지 신경 쓰지 않으므로, 재료를
    복잡한 공장 생산 라인에 넣어 분류하고 무한 생산 농장의 다른 재료와 합치는 등 독특한 구성을 만들 수
    있습니다. 패턴이 지정한 결과물만 돌아오면 ME 시스템은 중간 과정을 신경 쓰지 않습니다. 재료와
    결과물이 실제로 관련되어 있는지도 확인하지 않습니다. "벚나무 판자 1개 = 네더의 별 1개"라고
    설정하고, 판자를 받으면 위더 농장이 위더를 처치하도록 만들어도 작동합니다.

같은 패턴이 들어 있는 여러 <ItemLink id="pattern_provider" />를 지원하며 병렬로 작동합니다. 또한 패턴을
조약돌 1개 = 돌 1개가 아니라 조약돌 8개 = 돌 8개로 설정할 수 있습니다. 그러면 패턴 공급기는 작업마다
조약돌을 하나씩이 아니라 8개씩 제련 구성에 넣습니다.

## 가장 범용적인 형태의 "패턴"

가공 패턴보다 더 범용적인 형태도 있습니다. 제작 카드가 설치된 <ItemLink id="level_emitter" />가 어떤
항목을 제작하도록 레드스톤 신호를 내보내게 할 수 있습니다. 이 "패턴"은 재료를 정의하지도, 신경 쓰지도
않습니다. "이 레벨 방출기가 레드스톤을 내보내면 가까운 미래나 먼 미래의 어느 시점에 ME 시스템이 이
아이템을 받는다"라고 정의할 뿐입니다. 보통 입력 재료가 필요 없는 무한 농장을 켜고 끄거나, 표준 자동
제작이 이해하지 못하는 "조약돌 1개 = 조약돌 2개" 같은 재귀 조합법 처리 장치를 작동시킬 때 사용합니다.

# 제작 CPU

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/assemblies/crafting_cpus.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

제작 CPU는 제작 요청과 작업을 관리합니다. 여러 단계의 제작 작업을 수행하는 동안 중간 재료를 저장하며,
처리할 수 있는 작업 크기와 어느 정도는 완료 속도에도 영향을 줍니다. 다중 블록 구조이며, 제작 저장소를
하나 이상 포함한 직육면체여야 합니다.

제작 CPU는 다음 블록으로 구성합니다.

*   (필수) [제작 저장소](../items-blocks-machines/crafting_cpu_multiblock.md)는 일반 저장 셀과 같은
    1k, 4k, 16k, 64k, 256k 크기가 있습니다. 제작에 사용되는 재료와 중간 재료를 저장하므로, 재료가
    많은 제작 작업을 처리하려면 더 크거나 더 많은 제작 저장소가 필요합니다.
*   (선택) <ItemLink id="crafting_accelerator" />는 패턴 공급기가 재료 묶음을 더 자주 내보내게 합니다.
    예를 들어 분자 조립기 6개로 둘러싸인 패턴 공급기가 한 번에 하나가 아니라 6개 모두로 재료를 보내
    동시에 사용하게 합니다.
*   (선택) <ItemLink id="crafting_monitor" />는 CPU가 현재 처리 중인 작업을 표시합니다.
    <ItemLink id="color_applicator" />로 색상을 바꿀 수 있습니다.
*   (선택) <ItemLink id="crafting_unit" />은 CPU를 직육면체로 만들기 위해 공간만 채웁니다.

제작 CPU 하나는 요청이나 작업 하나를 처리합니다. 계산 프로세서와 매끄러운 돌 256개를 동시에
요청하려면 제작 CPU 다중 블록이 2개 필요합니다.

플레이어의 요청, 반출 버스·인터페이스의 자동화 요청 또는 양쪽 모두를 처리하도록 설정할 수 있습니다.

# 패턴 공급기

<Row>
<BlockImage id="pattern_provider" scale="4" />

<BlockImage id="pattern_provider" p:push_direction="up" scale="4" />

<GameScene zoom="4" background="transparent">
  <ImportStructure src="../assets/blocks/cable_pattern_provider.snbt" />
</GameScene>
</Row>

<ItemLink id="pattern_provider" />는 자동 제작 시스템이 외부와 상호작용하는 주된 수단입니다. 내부의
[패턴](../items-blocks-machines/patterns.md)에 지정된 재료를 인접 인벤토리로 밀어내고, 아이템을 공급기에
넣어 네트워크로 보낼 수도 있습니다. 기계의 출력물을 <ItemLink id="import_bus" />로 가져오는 대신
가까운 패턴 공급기, 흔히 재료를 보낸 공급기로 다시 보내면 채널을 절약할 수 있습니다.

패턴 공급기는 제작 CPU의 [제작 저장소](../items-blocks-machines/crafting_cpu_multiblock.md#crafting-storage)에서
재료를 직접 밀어내므로 실제 인벤토리에 재료를 보관하지 않습니다. 따라서 공급기에서 파이프로 재료를
뽑아낼 수 없습니다. 공급기가 통 같은 다른 인벤토리로 밀어낸 다음 그곳에서 파이프로 꺼내야 합니다.

또한 공급기는 모든 재료를 한꺼번에 밀어내야 하며 절반짜리 묶음을 보낼 수 없습니다. 이 특성을 유용하게
활용할 수 있습니다.

패턴 공급기는 [서브네트워크](../ae2-mechanics/subnetworks.md)의 인터페이스와 특별하게 상호작용합니다.
인터페이스를 변경하지 않아 요청 슬롯이 비어 있으면 공급기는 인터페이스를 건너뛰고 서브네트워크의
[저장소](../ae2-mechanics/import-export-storage.md)로 바로 밀어냅니다. 인터페이스를 조합법 묶음으로 채우지
않으며, 더 중요한 점으로 저장소에 공간이 생길 때까지 다음 묶음을 넣지 않습니다.

같은 패턴이 들어 있는 여러 패턴 공급기를 지원하며 병렬로 작동합니다.

패턴 공급기는 모든 면에 재료 묶음을 돌아가며 보내 연결된 기계를 병렬로 사용하려 합니다.

## 변형

패턴 공급기에는 일반, 방향성, 평면형 세 가지 변형이 있습니다. 재료를 내보내는 면, 아이템을 받는 면과
네트워크 연결을 제공하는 면이 달라집니다.

*   일반 패턴 공급기는 모든 면으로 재료를 내보내고 모든 면에서 입력을 받습니다. 대부분의 AE2 기계처럼
    케이블 역할을 하여 모든 면에 네트워크 연결을 제공합니다.

*   방향성 패턴 공급기는 일반 패턴 공급기에 <ItemLink id="certus_quartz_wrench" />를 사용해 방향을
    바꾸면 만들 수 있습니다. 선택한 면으로만 재료를 내보내고 모든 면에서 입력을 받지만, 선택한 면에는
    네트워크 연결을 제공하지 않습니다. 서브네트워크를 만들 때 네트워크를 연결하지 않고 AE2 기계로
    재료를 보낼 수 있습니다.

*   평면형 패턴 공급기는 [케이블 부품](../ae2-mechanics/cable-subparts.md)이므로 같은 케이블에 여러 개를
    설치해 좁은 공간에 구성할 수 있습니다. 방향성 패턴 공급기의 선택된 면과 비슷하게 작동하여 패턴을
    제공하고 입력을 받지만, 설치된 면에는 네트워크 연결을 제공하지 않습니다.

일반형과 평면형 패턴 공급기는 제작 격자에서 서로 바꿀 수 있습니다.

## 설정

패턴 공급기에는 여러 모드가 있습니다.

*   **차단 모드**는 기계 안에 재료가 이미 있으면 새 재료 묶음을 내보내지 않습니다.
*   **제작 잠금**은 여러 레드스톤 조건에서, 또는 이전 제작 결과가 해당 패턴 공급기로 들어올 때까지
    공급기를 잠글 수 있습니다.
*   <ItemLink id="pattern_access_terminal" />에 공급기를 표시하거나 숨길 수 있습니다.

## 우선순위

GUI 오른쪽 위의 렌치를 클릭해 우선순위를 설정할 수 있습니다. 같은 아이템을 만드는
[패턴](../items-blocks-machines/patterns.md)이 여러 개라면, 네트워크에 높은 우선순위 패턴의 재료가 없는
경우를 제외하고 높은 우선순위 공급기의 패턴을 낮은 우선순위보다 먼저 사용합니다.

# 분자 조립기

<BlockImage id="molecular_assembler" scale="4" />

<ItemLink id="molecular_assembler" />는 들어온 아이템으로 인접한 <ItemLink id="pattern_provider" />가
지정한 작업이나 장착된 <ItemLink id="crafting_pattern" />, <ItemLink id="smithing_table_pattern" /> 또는
<ItemLink id="stonecutting_pattern" />의 작업을 수행한 뒤 결과물을 인접한 인벤토리로 밀어냅니다.

주로 <ItemLink id="pattern_provider" /> 옆에서 사용합니다. 이 구성에서 패턴 공급기는 특별하게 작동하여
관련 패턴 정보와 재료를 인접한 조립기로 함께 보냅니다. 조립기는 제작 결과를 인접 인벤토리, 즉 패턴
공급기의 반환 슬롯으로 자동 배출하므로 패턴 공급기에 붙은 조립기만으로 제작 패턴을 자동화할 수 있습니다.

<GameScene zoom="4" background="transparent">
<ImportStructure src="../assets/assemblies/assembler_tower.snbt" />
<IsometricCamera yaw="195" pitch="30" />
</GameScene>
