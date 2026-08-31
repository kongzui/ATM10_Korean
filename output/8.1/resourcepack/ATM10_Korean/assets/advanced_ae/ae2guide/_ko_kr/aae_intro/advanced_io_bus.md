---
navigation:
  parent: aae_intro/aae_intro-index.md
  title: ME 고급 입출력 버스
  icon: advanced_ae:advanced_io_bus_part
categories:
  - advanced items
item_ids:
  - advanced_ae:advanced_io_bus_part
---

# ME 고급 입출력 버스

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../structure/cable_advanced_io_bus.snbt"></ImportStructure>
</GameScene>

ME 고급 입출력 버스는 외부 인벤토리와 상호 작용하는 매우 강력한 도구입니다.
<ItemLink id="advanced_ae:import_export_bus_part"/>와 <ItemLink id="advanced_ae:stock_export_bus_part"/>를
결합하여 만들며, 두 상위 장치의 기능을 모두 물려받습니다. 또한 ME 고급 입출력 버스의 기본 속도는
<ItemLink id="ae2:export_bus"/>의 기본 속도보다 8배 빠릅니다. 최고 속도에 도달하기까지 시간이 조금
걸리지만, 완전히 업그레이드하면 엄청나게 빨라집니다.

## 반출

ME 고급 입출력 버스는 필터에 따라 정해진 수량까지 반출한 뒤 멈춥니다. UI 왼쪽에는 아이템 재고 수량을
조절할지 선택하는 설정도 있습니다.

## 반입

ME 고급 입출력 버스는 반출 필터에 없는 모든 아이템도 반입합니다. 반입과 반출 작업은 별도로 계산되므로
한쪽 작업만 하느라 버스가 멈추지 않습니다. 수량 조절을 사용하도록 설정하면 지정 수량을 초과한
아이템을 우선 반입합니다. 작업 횟수가 남으면 필터에 없는 아이템도 반입합니다.

<RecipeFor id="advanced_ae:advanced_io_bus_part"/>
