---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 터미널
  icon: crafting_terminal
  position: 210
categories:
- devices
item_ids:
- ae2:terminal
- ae2:crafting_terminal
- ae2:pattern_encoding_terminal
- ae2:pattern_access_terminal
---

# 터미널

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/terminals.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

<ItemLink id="pattern_provider" />, <ItemLink id="import_bus" />, <ItemLink id="storage_bus" /> 등이 AE2 네트워크가 월드와 상호작용하는
주된 수단이라면, 터미널은 AE2 네트워크가 *플레이어와* 상호작용하는 주된 수단입니다. 기능이 서로 다른 여러 변형이 있습니다.

터미널은 장착된 [케이블](cables.md)의 색을 따릅니다.

[케이블 부품](../ae2-mechanics/cable-subparts.md)으로 설치됩니다.

## 터미널 설치

터미널은 처음 설치하는 [부품](../ae2-mechanics/cable-subparts.md)인 경우가 많아 거꾸로 놓기 쉽습니다.
다음은 올바른 설치와 잘못된 설치의 예입니다.

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/terminal_placement.snbt" />
  <IsometricCamera yaw="195" pitch="30" />

  <LineAnnotation color="#ff3333" from="2.5 .5 .5" to="4.5 2.5 .5" alwaysOnTop={true} thickness="0.05"/>
  <LineAnnotation color="#ff3333" from="2.5 2.5 .5" to="4.5 .5 .5" alwaysOnTop={true} thickness="0.05"/>

  <LineAnnotation color="#33ff33" from="-.5 2.5 .5" to="1 .5 .5" alwaysOnTop={true} thickness="0.05"/>
  <LineAnnotation color="#33ff33" from="1 .5 .5" to="1.5 1 .5" alwaysOnTop={true} thickness="0.05"/>
</GameScene>

여전히 터미널과 에너지 수용기가 있지만, 이제 터미널의 방향이 올바르고 실제로 네트워크에 연결되며 공간도 더 적게 차지합니다.

<a name="terminal-ui"></a>

# 터미널 검색

검색창은 정규 표현식을 지원합니다. 예를 들어 "gtceu:.*ore"를 입력하면 GregTech의 모든 광물을 찾을 수 있습니다.
정규 표현식을 배우는 일은 독자 여러분께 맡깁니다.

# ME 터미널

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/blocks/terminal.snbt" />
  <IsometricCamera yaw="180" />
</GameScene>

기본 터미널입니다. [네트워크 저장소](../ae2-mechanics/import-export-storage.md)의 내용물을 보고 이용하며,
[자동 제작](../ae2-mechanics/autocrafting.md) 설비에 아이템을 요청할 수 있습니다.

## UI

기본 터미널 UI는 여러 구역으로 나뉩니다.

가운데 구역에서는 네트워크 저장소에 접근해 대상을 넣고 꺼낼 수 있습니다. 다음 마우스·키보드 단축 조작을 지원합니다.

*   좌클릭하면 한 스택을 집고 우클릭하면 반 스택을 집습니다.
*   아이템이나 유체 등을 [자동 제작](../ae2-mechanics/autocrafting.md)할 수 있다면 "블록 선택"에 지정한 키(보통 가운데 클릭)를 눌러
    제작 수량 지정 UI를 엽니다. `3*64/2` 같은 수식을 입력하거나 `=32`를 입력해 저장소의 수량이 32개가 되는 데 필요한 만큼만 제작할 수도 있습니다.
*   Shift를 누르면 표시된 항목의 위치가 고정되어 수량이 바뀌거나 새 항목이 들어와도 재정렬되지 않습니다.
*   양동이나 다른 유체 용기를 들고 우클릭하면 유체를 넣고, 빈 유체 용기를 든 채 터미널의 유체를 좌클릭하면 유체를 꺼냅니다.

왼쪽 구역에는 다음 설정 버튼이 있습니다.

*   이름, 모드, 수량 같은 속성으로 정렬
*   저장된 항목, 제작 가능한 항목 또는 둘 다 표시
*   아이템, 유체 또는 둘 다 표시
*   정렬 순서 변경
*   상세 터미널 설정 창 열기
*   터미널 UI 높이 변경

오른쪽에는 <ItemLink id="view_cell" /> 슬롯이 있습니다.

가운데 구역 오른쪽 위의 망치 버튼은 [자동 제작](../ae2-mechanics/autocrafting.md) 상태 UI를 엽니다.
자동 제작 진행 상황과 각 [제작 CPU](crafting_cpu_multiblock.md)의 작업을 확인할 수 있습니다.

## 조합법

<RecipeFor id="terminal" />

<a name="crafting-terminal-ui"></a>

# ME 제작 터미널

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/blocks/crafting_terminal.snbt" />
  <IsometricCamera yaw="180" />
</GameScene>

ME 제작 터미널은 일반 터미널과 설정 및 구성이 같지만 제작 격자가 추가되어 있습니다.
제작 격자는 [네트워크 저장소](../ae2-mechanics/import-export-storage.md)에서 자동으로 다시 채워집니다. 결과물을 Shift+클릭할 때 주의하세요!

가능한 한 빨리 터미널을 제작 터미널로 업그레이드하세요.

## UI

제작 터미널은 일반 터미널과 같은 UI를 사용하지만 가운데에 제작 격자가 추가됩니다.

제작 격자의 내용물을 네트워크 저장소 또는 플레이어 인벤토리로 비우는 버튼 두 개가 추가됩니다.

## 조합법

<RecipeFor id="crafting_terminal" />

<a name="pattern-encoding-terminal-ui"></a>

# ME 패턴 인코딩 터미널

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/blocks/pattern_encoding_terminal.snbt" />
  <IsometricCamera yaw="180" />
</GameScene>

ME 패턴 인코딩 터미널은 일반 터미널과 설정 및 구성이 같지만 [패턴](patterns.md) 인코딩 인터페이스가 추가되어 있습니다.
제작 터미널 UI와 비슷해 보이지만 이 제작 격자는 실제로 제작하지 않습니다.

제작 터미널과 별도로 하나 마련하는 것이 좋습니다.

## UI

일반 터미널과 같은 UI에 [패턴](patterns.md) 인코딩 인터페이스가 추가됩니다.

패턴 인코딩 인터페이스는 여러 구역으로 나뉩니다.

<ItemLink id="blank_pattern" />을 넣는 슬롯입니다.

패턴을 인코딩하는 큰 화살표입니다.

인코딩된 패턴 슬롯입니다. 이미 인코딩된 패턴을 편집하려면 이 슬롯에 넣고 "인코딩" 화살표를 클릭하세요.

오른쪽의 탭 4개로 인코딩할 패턴 유형을 전환합니다.

*   제작
*   가공
*   대장장이 작업대
*   석재 절단

가운데 UI는 인코딩할 패턴 유형에 따라 달라집니다.

*   제작 모드:
    *   좌클릭하거나 JEI/REI에서 재료를 끌어와 조합법을 구성합니다. 우클릭하면 재료를 제거합니다.
    *   대체 재료를 활성화하면 모든 종류의 판자로 막대기를 만드는 식으로 작동합니다. 꼭 필요할 때만 사용하세요.
    *   유체 대체를 활성화하면 유체 양동이 대신 저장된 유체를 사용할 수 있습니다.
    *   JEI/REI 조합법 화면에서 패턴을 직접 인코딩할 수도 있습니다.

*   가공 모드:
    * 좌클릭·우클릭하거나 JEI/REI에서 재료를 끌어와 조합법의 입력과 출력을 지정합니다.
    * 양동이나 유체 탱크 같은 유체 용기를 들고 우클릭하면 용기 아이템 대신 그 안의 유체를 재료로 설정합니다.
    * 스택을 들고 좌클릭하면 스택 전체를, 우클릭하면 아이템 하나를 놓습니다. 기존 재료 스택을 좌클릭하면 전체를 제거하고
        우클릭하면 수량을 1 줄입니다. "블록 선택"에 지정한 키(보통 가운데 클릭)로 아이템이나 유체의 정확한 양을 지정할 수 있습니다.
    * 출력 슬롯에는 주 출력과 자동 제작 알고리즘에 알려 줄 보조 출력을 넣는 공간이 있습니다.
    * 입력과 출력 슬롯을 모두 스크롤할 수 있어 서로 다른 재료 81개와 보조 출력 26개를 지정할 수 있습니다.
    * JEI/REI 조합법 화면에서 패턴을 직접 인코딩할 수도 있습니다.

*   대장장이 작업대와 석재 절단 모드 UI는 각각 대장장이 작업대 및 석재 절단기와 비슷하게 작동합니다.

## 조합법

<RecipeFor id="pattern_encoding_terminal" />

<a name="pattern-access-terminal-ui"></a>

# ME 패턴 접근 터미널

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/blocks/pattern_access_terminal.snbt" />
  <IsometricCamera yaw="180" />
</GameScene>

ME 패턴 접근 터미널은 특정 문제를 해결합니다. <ItemLink id="pattern_provider" />와 <ItemLink id="molecular_assembler" />가 빽빽한 탑에서는
새 패턴을 넣으려고 공급기에 직접 접근할 수 없습니다. 또는 [패턴](patterns.md)을 넣으러 기지 반대편까지 걷기 귀찮을 수도 있습니다.
패턴 접근 터미널에서는 네트워크의 모든 패턴 공급기에 접근할 수 있습니다.

## UI

이 터미널은 다른 모든 터미널과 UI가 다릅니다.

터미널 높이와 표시할 패턴 공급기를 설정할 수 있습니다.

터미널의 각 행은 특정 패턴 공급기에 대응합니다.

터미널의 패턴 공급기는 연결된 블록 또는 모루나 <ItemLink id="name_press" />로 붙인 이름에 따라 정렬됩니다.

## 조합법

<RecipeFor id="pattern_access_terminal" />
