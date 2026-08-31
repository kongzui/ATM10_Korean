---
navigation:
  parent: example-setups/example-setups-index.md
  title: 셀 비우기 또는 채우기
  icon: io_port
---

# 셀 비우기 또는 채우기

"셀을 상자, 서랍 배열이나 배낭으로 빠르게 비우거나 반대로 그곳의 내용물로 셀을 채우려면 어떻게
해야 할까?"라는 의문이 들 수 있습니다.

<ItemLink id="io_port" />와 서브네트워크를 사용해 아이템을 넣거나 가져올 위치를 제한하면 됩니다.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/cell_dumper_filler.snbt" />

<BoxAnnotation color="#dddddd" min="1 1 0" max="2 2 1">
        (1) I/O 포트: GUI 중앙의 화살표 버튼으로 "네트워크로 데이터 전송" 또는 "저장 셀로 데이터
        전송"을 선택합니다. 가속 카드를 3개 설치합니다.
        <ItemImage id="speed_card" scale="2" />
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="0 0.7 0" max="1 1 1">
        (2) 저장 버스: 기본 설정을 사용합니다.
  </BoxAnnotation>

<BoxAnnotation color="#33dd33" min="0 1 0" max="1 2 1">
        채우거나 비울 대상을 이곳에 놓으세요.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="2 0.35 0.35" max="2.3 0.65 0.65">
        석영 섬유: 다른 네트워크에서 전력을 받을 때만 필요합니다.
  </BoxAnnotation>

<DiamondAnnotation pos="3 0.5 0.5" color="#00ff00">
        다른 네트워크나 에너지 수용기 같은 에너지원으로 연결
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 설정

* <ItemLink id="io_port" /> (1)은 GUI 중앙의 화살표 버튼으로 "네트워크로 데이터 전송" 또는 "저장 셀로
  데이터 전송"을 선택합니다. 최대 속도를 위해 가속 카드 3개를 설치합니다.
* <ItemLink id="storage_bus" /> (2)는 기본 설정을 사용합니다.

## 작동 방식

### "네트워크로 전송" 모드

1. <ItemLink id="io_port" />가 장착된 [저장 셀](../items-blocks-machines/storage_cells.md)의 내용물을
   [네트워크 저장소](../ae2-mechanics/import-export-storage.md)로 비우려 합니다.
2. 서브네트워크의 유일한 저장소인 <ItemLink id="storage_bus" />는 앞에 놓인 대상에 아이템, 유체 등을
   저장합니다.
* <ItemLink id="energy_cell" />은 게임 틱마다 많은 아이템을 전송할 때 네트워크 에너지가 바닥나지
  않도록 충분한 [에너지](../ae2-mechanics/energy.md) 버퍼를 제공합니다.

### "저장 셀로 전송" 모드

1. <ItemLink id="io_port" />가 [네트워크 저장소](../ae2-mechanics/import-export-storage.md)의 내용물을
   장착된 [저장 셀](../items-blocks-machines/storage_cells.md)로 비우려 합니다.
2. 서브네트워크의 유일한 저장소인 <ItemLink id="storage_bus" />는 앞에 놓인 대상에서 아이템, 유체 등을
   꺼냅니다.
* <ItemLink id="energy_cell" />은 게임 틱마다 많은 아이템을 전송할 때 네트워크 에너지가 바닥나지
  않도록 충분한 [에너지](../ae2-mechanics/energy.md) 버퍼를 제공합니다.
