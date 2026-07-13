---
navigation:
    parent: ae2:items-blocks-machines/items-blocks-machines-index.md
    icon: ae2netanalyser:tick_analyser
    title: ME 틱 프로파일러
categories:
- tools
item_ids:
- ae2netanalyser:tick_analyser
---

# ME 틱 속도 프로파일링

<ItemImage id="ae2netanalyser:tick_analyser" scale="4"></ItemImage>

ME 네트워크가 매우 커지면 게임이 느려질 수 있지만, 네트워크에서 렉의 원인을 찾기는 쉽지 않습니다.
ME 틱 프로파일러를 사용하면 어떤 장치가 느린지 쉽게 찾을 수 있습니다.

## 무엇이 게임을 느리게 하나요?

일부 AE 장치는 게임 틱마다 작업을 수행합니다. ME 틱 프로파일러는 작업을 마치는 데 걸리는 시간(μs/틱)을
측정하여 월드에 표시하므로, 가장 오래 걸리는 장치를 찾는 데 도움이 됩니다.

**악용을 막기 위해 멀티플레이 서버에서는 OP 권한이 있어야 사용할 수 있습니다.**

![개요](./pic/tick_rate.png)

블록의 색상은 렉이 얼마나 심한지를 나타냅니다. 붉을수록 더 느린 블록입니다.

숫자는 이 블록의 틱 처리 시간을 나타냅니다. TPS(초당 틱)가 20보다 낮으면 게임이 느려집니다.
즉, 게임 전체의 틱 처리 시간은 항상 50000μs/틱보다 낮아야 합니다.

일반적으로 대부분의 블록은 틱 처리 시간이 100μs/틱보다 낮아야 하며, 그렇지 않으면 렉을 일으킬 수 있습니다.

## 표시 설정

설정 화면에서 틱 처리 시간 구간별 월드 표시 여부를 조절할 수 있습니다.

![설정 화면](./pic/gui2.png)

초록색 점은 해당 틱 처리 시간 구간의 블록을 표시한다는 뜻입니다. 점을 클릭하면 표시 여부를 켜거나 끌 수
있습니다.
