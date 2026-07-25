---
navigation:
  title: 기타 기능
  icon: mega_interface
  parent: index.md
  position: 060
categories:
  - megacells
item_ids:
  - mega_interface
  - cell_dock
  - portable_cell_workbench
---

# MEGA Cells: 기타 기능

애드온의 핵심 기능을 모두 살펴봤으니, 이제 완성도를 높이고 조금 더 실험할 수 있도록 MEGA가 제공하는
작은 추가 기능으로 마무리하겠습니다.

## MEGA 인터페이스

<Row>
  <BlockImage id="mega_interface" scale="4" />
  <GameScene zoom="4" background="transparent">
    <ImportStructure src="assets/assemblies/cable_mega_interface.snbt" />
  </GameScene>
</Row>

<ItemLink id="megacells:mega_pattern_provider" />를 보완하는 **MEGA 인터페이스**는
<ItemLink id="ae2:interface" />의 용량을 두 배로 늘린 버전입니다. 슬롯, 입출력과 처리량, 재고 유지
기능이 모두 두 배입니다.

<RecipeFor id="mega_interface" />
<RecipeFor id="cable_mega_interface" />

## 휴대용 셀 작업대

<ItemImage id="portable_cell_workbench" scale="4" />

애드온의 다른 장치와 조금 다르게, **휴대용 셀 작업대**는 <ItemLink id="ae2:cell_workbench" />의...
*더 작은* 버전입니다. 손바닥에 들어갈 만큼 작지만, 일반 작업대처럼 모든 저장 셀을 설정할 수 있습니다.

작업대 하나가 어떻게 이 작은 물건에 들어갔는지는 상상에 맡기겠습니다.

<RecipeFor id="portable_cell_workbench" />

## 셀 도크

<GameScene zoom="8" background="transparent">
  <ImportStructure src="assets/assemblies/cell_dock.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

마지막 장치도 큰 것이 아니라 다시 더 작은 물건입니다. 그래서 "MEGA" 아이템이라고 부르기에는 가장
어색했을 것 같네요.

**ME 셀 도크**는 <ItemLink id="ae2:chest" />를 더 작게 만든 것과 비슷하며, 저장 셀을 한 번에 하나씩
넣을 수 있습니다. 내장 터미널 같은 ME 상자의 일부 추가 기능은 없지만, 소형 저장 장치로 충분히
쓸 만합니다. 특히 "평평한" [케이블 부품](ae2:ae2-mechanics/cable-subparts.md)이므로 케이블 하나가 같은
한 블록 공간에 여러 셀 도크를 담을 수 있습니다. 임시 버퍼 저장소가 필요한 소형 서브네트워크에 유용할
수 있습니다.

<RecipeFor id="cell_dock" />

## "클래식 셀 색상"

과거의 시각적 스타일을 선택 사항으로 되살릴 수 있도록, MEGA에는 사용자가 활성화할 수 있는 다음
리소스팩이 포함되어 있습니다.

![클래식 셀 색상 리소스팩](assets/diagrams/cell_colours_pack.png)

Minecraft 1.21 이전의 AE2와 애드온 버전에서 저장 셀 세트의 옛 텍스처는 5단계 색상 체계를
사용했습니다. 1k 셀의 적갈색에서 시작해 노랑, 초록, 파랑을 거쳐 256k의 밝은 보라색 또는 라벤더색으로
바뀌었습니다. MEGA도 이 흐름을 따라 1M의 진한 빨강에서 시작해 256M의 더 진한 보라색으로 끝났습니다.

![옛 셀 텍스처](assets/diagrams/cell_colours_old.png)

AE2의 1.20.x 이후 버전에 도입된 전반적인 텍스처 개편으로 저장 셀도 더 넓은 색상 범위를 사용하게
됐습니다. AE2 기본 저장 셀은 등급이 올라가며 파랑에서 초록으로 바뀌고, MEGA는 노랑에서 빨강을 거쳐
분홍으로 이어집니다. 이 방식도 멋지지만, 현재 방식보다 예전 색상 체계를 좋아하는 사용자를 위해 선택지를
제공하는 것도 나쁘지 않겠죠.

![AE2 셀 색상](assets/diagrams/cell_colours_ae2.png)
![MEGA 셀 색상](assets/diagrams/cell_colours_mega.png)
