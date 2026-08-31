---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 모니터
  icon: storage_monitor
  position: 210
categories:
- devices
item_ids:
- ae2:storage_monitor
- ae2:conversion_monitor
---

# 모니터

<GameScene zoom="8" background="transparent">
<ImportStructure src="../assets/assemblies/monitors.snbt" />
<IsometricCamera yaw="195" pitch="30" />
</GameScene>

모니터는 GUI를 열지 않고도 한 종류의 아이템 또는 유체를 표시하고 상호작용하게 합니다.

모니터는 장착된 [케이블](cables.md)의 색을 따릅니다.

모니터가 바닥이나 천장에 있으면 <ItemLink id="certus_quartz_wrench" />로 회전할 수 있습니다.

[케이블 부품](../ae2-mechanics/cable-subparts.md)으로 설치됩니다.

# 저장 모니터

아이템 또는 유체와 그 수량을 표시합니다. 농장 옆 같은 곳에 놓아 보세요...

[채널](../ae2-mechanics/channels.md)이 *필요하지 않습니다.*

조작법:

*   아이템을 들고 우클릭하거나 유체 용기를 들고 빠르게 두 번 우클릭하면 해당 아이템/유체로 설정합니다.
*   빈손으로 우클릭하면 모니터 설정을 지웁니다.
*   빈손으로 Shift+우클릭하면 모니터를 잠급니다.

## 조합법

<RecipeFor id="storage_monitor" />

# 변환 모니터

변환 모니터는 저장 모니터와 비슷하지만 설정한 아이템을 넣거나 꺼낼 수 있습니다.

설정한 아이템을 [자동 제작](../ae2-mechanics/autocrafting.md)할 수 있지만 저장소에 없다면,
아이템을 꺼내려 할 때 제작할 수량을 지정하는 UI가 대신 열립니다.

[채널](../ae2-mechanics/channels.md)이 *필요합니다.*

추가 조작법:

*   좌클릭하면 설정한 아이템 한 스택을 꺼냅니다. 저장소에 없다면 해당 아이템의 제작을 요청합니다.
*   아이템을 들고 우클릭하면 그 아이템을 넣습니다.
*   빈손으로 우클릭하면 인벤토리에서 설정한 아이템을 모두 넣습니다.

## 조합법

<RecipeFor id="conversion_monitor" />
