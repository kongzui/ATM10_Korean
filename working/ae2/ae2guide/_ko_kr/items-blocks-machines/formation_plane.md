---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 형성 평면
  icon: formation_plane
  position: 210
categories:
- devices
item_ids:
- ae2:formation_plane
---

# 형성 평면

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../assets/blocks/formation_plane.snbt" />
</GameScene>

형성 평면은 블록을 설치하고 아이템을 떨어뜨립니다. 삽입 전용 <ItemLink id="storage_bus" />와 비슷하게 작동합니다.
<ItemLink id="import_bus" />나 <ItemLink id="interface" /> 같은 [장치](../ae2-mechanics/devices.md)가
[네트워크 저장소](../ae2-mechanics/import-export-storage.md)에 대상을 "저장"하면 블록을 설치하거나 아이템을 떨어뜨립니다.

<GameScene zoom="8" interactive={true}>
  <ImportStructure src="../assets/assemblies/formation_plane_demonstration.snbt" />
  <IsometricCamera yaw="255" pitch="30" />
</GameScene>

[파이프 서브네트워크](../example-setups/pipe-subnet.md)의 반입 버스 -> 저장 버스 및 인터페이스 -> 저장 버스 파이프와 비슷하다는 점에 주목하세요.

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/import_storage_pipe.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

<GameScene zoom="6" interactive={true}>
  <ImportStructure src="../assets/assemblies/interface_storage_pipe.snbt" />
  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

이 [장치](../ae2-mechanics/devices.md)는 [파이프 서브네트워크](../example-setups/pipe-subnet.md) 등에서 저장 버스가 사용하는 원리를 활용합니다.
아이템을 운반하는 대신 떨어뜨리거나 블록을 설치하려면 그러한 설비의 저장 버스를 대신할 수 있습니다.

[케이블 부품](../ae2-mechanics/cable-subparts.md)으로 설치됩니다.

**청크 보호에서 가짜 플레이어를 반드시 허용하세요.**

## 필터링

기본적으로 모든 대상을 설치하거나 떨어뜨립니다. 필터 슬롯에 넣은 아이템은 허용 목록으로 작동해 지정한 아이템만 배치합니다.

실제로 가지고 있지 않은 아이템이나 유체도 JEI/REI에서 슬롯으로 끌어올 수 있습니다.

양동이나 유체 탱크 같은 유체 용기를 들고 우클릭하면 용기 아이템 대신 그 안의 유체를 필터로 설정합니다.

## 우선순위

GUI 오른쪽 위의 렌치를 클릭해 우선순위를 설정할 수 있습니다.
네트워크에 들어오는 아이템은 우선순위가 가장 높은 저장소부터 향합니다.

## 설정

*   월드에 블록을 설치하거나 아이템을 떨어뜨리도록 설정할 수 있습니다.

## 업그레이드

형성 평면은 다음 [업그레이드](upgrade_cards.md)를 지원합니다.

*   <ItemLink id="capacity_card" />는 필터 슬롯 수를 늘립니다.
*   <ItemLink id="fuzzy_card" />는 내구도 수준으로 필터링하거나 아이템 NBT를 무시하게 합니다.
*   <ItemLink id="inverter_card" />는 필터를 허용 목록에서 차단 목록으로 바꿉니다.

## 조합법

<RecipeFor id="formation_plane" />
