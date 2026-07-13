---
navigation:
  title: ME Requester
  icon: requester
  position: 100
item_ids:
  - merequester:requester
  - merequester:requester_terminal
---

# ME Requester

<Row>
  <ItemImage id="requester" scale="3"/>
  <ItemImage id="requester_terminal" scale="3"/>
</Row>

[ME 시스템](ae2:getting-started.md#your-very-first-me-system)의 아이템과 유체 재고를 유지할 수 있게 해주는 애드온 모드입니다.
<br/>

## 시작하기

먼저 <ItemLink id="requester"/>를 놓고 네트워크에 연결하세요. [자동 제작](ae2:ae2-mechanics/autocrafting.md) 기능이
있는 네트워크와 같아야 합니다. 이 네트워크에는 [제작 CPU](ae2:ae2-mechanics/autocrafting.md#the-crafting-cpu)와
<ItemLink id="ae2:pattern_provider"/>가 있어야 합니다.

<RecipeFor id="requester"/>

<ItemLink id="requester"/>가 작동하려면 재고로 유지할 아이템이나 유체의 패턴이 있어야 하며, 플레이어가 직접
요청했을 때도 제작할 수 있어야 합니다. 이 블록은 요청 과정만 자동화하며, 제작은
[ME 시스템](ae2:getting-started.md#your-very-first-me-system)이 처리합니다.
<br/>

<FloatingImage src="assets/gui.png" align="right"/>

## 설정

<ItemLink id="requester"/>를 처음 열면 요청 설정 목록이 표시됩니다. 블록 하나에 넣을 수 있는 슬롯 수는 설정에서
조절할 수 있습니다. 화면의 각 행은 하나의 개별 요청을 나타냅니다.
<br/>

### 켜기/끄기

왼쪽의 확인란으로 해당 행에 설정된 요청을 켜거나 끌 수 있습니다. 요청을 끄면 재고를 확인하지 않으며 목표
재고도 유지하지 않습니다.<br/>
특정 요청을 잠시 끄거나, 행을 수정하는 동안 <ItemLink id="requester"/>가 제작 작업을 내보내지 않게 할 때
사용할 수 있습니다.
<br/>

### 재고로 유지할 대상

두 번째 열에서 재고로 유지할 대상을 지정할 수 있습니다. 이 슬롯은 고스트 슬롯이므로 실제 아이템을 보관하지
않습니다. 아이템을 슬롯으로 끌 때 오른쪽 클릭하면 수량을 1로 설정하고, 왼쪽 클릭하면 끌고 있는 아이템 묶음의
수량을 사용합니다. 유체가 든 양동이를 슬롯으로 끌 때 오른쪽 클릭하면 담긴 유체를, 왼쪽 클릭하면 양동이 자체를
설정합니다. 아이템을 Shift+클릭하여 종류를 빠르게 설정할 수도 있습니다. 원하는 아이템이 인벤토리에 없다면
Applied Energistics가 지원하는 조합법 뷰어에서 끌어다 놓을 수도 있습니다.
<br/>

### 목표 재고량

목표 재고량 입력란은 유지할 수량을 나타냅니다. 먼저 재고로 유지할 대상을 지정한 다음 원하는 값을 입력하세요.
아이템이 아닌 요청에는 대상 종류에 맞는 단위가 표시됩니다. 예를 들어 유체에는 양동이 단위를 나타내는 `B`가
표시됩니다.<br/>
현재 재고가 지정한 수량보다 적어지면 <ItemLink id="requester"/>가 추가 제작을 요청합니다.
<br/>

### 일괄 요청량

다음 입력란에서는 현재 재고가 목표 재고량보다 적어졌을 때 한 번에 요청할 수량을 지정합니다.<br/>
여러 개별 작업 대신 전체 수량을 한 번에 요청하므로 [제작 CPU](ae2:ae2-mechanics/autocrafting.md#the-crafting-cpu)와
제작에 사용하는 기계의 부담을 줄일 수 있습니다.
<br/>

### 적용 버튼

요청 변경 사항을 적용하려면 목표 재고량과 일괄 요청량 입력란에 원하는 값을 입력한 다음 Enter를 누르거나 현재
행의 오른쪽에 있는 적용 버튼을 클릭하세요. 다른 행을 클릭하면 입력한 값이 이전 상태로 초기화됩니다.
<br/>

### 상태 표시줄

입력란과 적용 버튼 아래의 표시줄은 현재 요청 상태를 보여줍니다.
<br clear="all" />
<br/>

## 상태

각 요청의 상태 표시줄에는 다음 상태가 표시됩니다.
<br/>

### 회색 - 비어 있음

현재 행을 껐거나 재고로 유지할 대상을 지정하지 않았습니다.
<br/>

### 초록색 - 대기

목표 재고량에 이미 도달했거나 설정된 요청의 패턴이 없습니다.
<br/>

### 빨간색 - 재료 부족

현재 작업을 내보내는 데 필요한 재료가 시스템에 부족합니다. 시스템에 재료가 충분해지면 바로 계속합니다.
<br/>

### 노란색 - 제작 중

요청한 대상을 현재 제작하고 있으며, 요청기는 작업이 끝나기를 기다립니다.<br/>
이 상태에서는 해당 <ItemLink id="requester"/> 요청의 설정이 잠겨 변경할 수 없습니다.
<br/>

### 보라색 - 내보내는 중

<ItemLink id="requester"/>가 현재 작업의 결과를 모두 받아 저장 시스템으로 내보내고 있습니다.<br/>
보통은 이 상태가 보이지 않습니다. 너무 오래 지속된다면 저장 시스템에 공간이 부족하다는 뜻입니다.
<br/>

### 블록 모습

<ItemLink id="requester"/>의 요청 중 하나라도 대기 또는 비어 있음 이외의 상태라면 블록 모습이 바뀝니다.

<Row>
  <Column>
    비활성
    <BlockImage id="requester" scale="3" p:active="false"/>
  </Column>
  <Column>
    활성
    <BlockImage id="requester" scale="3" p:active="true"/>
  </Column>
</Row>
<br/>

## 터미널

이 모드는 <ItemLink id="requester_terminal"/>이라는 새 터미널도 제공합니다. 중앙 지점에서 같은 네트워크의 모든
<ItemLink id="requester"/>에 접근할 수 있습니다.

이 터미널은 <ItemLink id="ae2:pattern_access_terminal"/>과 같은 기능을 갖추고 있어 특정 요청을 검색할 수 있습니다.
모든 <ItemLink id="requester"/>는 기본 이름이 같으므로 모든 요청이 같은 제목 아래에 묶입니다. 여러
<ItemLink id="requester"/>를 <ItemLink id="requester_terminal"/>에서 별도 그룹으로 나누려면 모루 또는
<ItemLink id="ae2:name_press"/>로 이름을 바꾸세요.
