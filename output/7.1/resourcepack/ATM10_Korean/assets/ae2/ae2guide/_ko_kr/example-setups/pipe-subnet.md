---
navigation:
  parent: example-setups/example-setups-index.md
  title: 아이템/유체 "파이프" 서브네트워크
  icon: storage_bus
---

# 아이템/유체 "파이프" 서브네트워크

AE2 [장치](../ae2-mechanics/devices.md)로 아이템·유체 파이프를 흉내 내는 간단한 방법입니다. 일반적인
파이프 용도와 제작 결과를 <ItemLink id="pattern_provider" />로 돌려보낼 때 유용합니다.

일반적으로 두 가지 방법이 있습니다.

## 반입 버스 → 저장 버스

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/import_storage_pipe.snbt" />

<BoxAnnotation color="#dddddd" min="3.7 0 0" max="4 1 1">
        (1) 반입 버스: 필터를 설정할 수 있습니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 0 0" max="1.3 1 1">
        (2) 저장 버스: 필터를 설정할 수 있습니다. 목적지로 사용할 다른 저장 버스와 함께 네트워크의
        유일한 저장소여야 합니다.
  </BoxAnnotation>

<DiamondAnnotation pos="4.5 0.5 0.5" color="#00ff00">
        출발지
    </DiamondAnnotation>

<DiamondAnnotation pos="0.5 0.5 0.5" color="#00ff00">
        목적지
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

출발지 인벤토리의 <ItemLink id="import_bus" /> (1)가 아이템이나 유체를 반입하여
[네트워크 저장소](../ae2-mechanics/import-export-storage.md)에 저장하려 합니다. 네트워크의 유일한 저장소가
<ItemLink id="storage_bus" /> (2)이므로 아이템이나 유체가 목적지 인벤토리에 들어가 전송됩니다. 이 때문에
주 네트워크가 아닌 서브네트워크로 구성합니다. <ItemLink id="quartz_fiber" />를 통해 전력을 공급합니다.
두 버스 모두 필터를 설정할 수 있으며, 필터가 없으면 접근 가능한 모든 것을 전송합니다. 반입·저장 버스를
여러 개씩 사용해도 작동합니다.

## 저장 버스 → 반출 버스

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/storage_export_pipe.snbt" />

<BoxAnnotation color="#dddddd" min="3.7 0 0" max="4 1 1">
        (1) 저장 버스: 필터를 설정할 수 있습니다. 출발지로 사용할 다른 저장 버스와 함께 네트워크의
        유일한 저장소여야 합니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 0 0" max="1.3 1 1">
        (2) 반출 버스: 반드시 필터를 설정해야 합니다.
  </BoxAnnotation>

<DiamondAnnotation pos="4.5 0.5 0.5" color="#00ff00">
        출발지
    </DiamondAnnotation>

<DiamondAnnotation pos="0.5 0.5 0.5" color="#00ff00">
        목적지
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

목적지 인벤토리의 <ItemLink id="export_bus" />가 필터의 아이템을
[네트워크 저장소](../ae2-mechanics/import-export-storage.md)에서 가져오려 합니다. 네트워크의 유일한 저장소가
<ItemLink id="storage_bus" />이므로 출발지 인벤토리에서 아이템이나 유체를 가져와 전송합니다.
<ItemLink id="quartz_fiber" />로 전력을 공급합니다. 반출 버스는 필터가 있어야 작동하므로 반드시 설정해야
합니다. 저장·반출 버스를 여러 개씩 사용해도 작동합니다.

## 작동하지 않는 구성: 반입 버스 → 반출 버스

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/import_export_pipe.snbt" />

<BoxAnnotation color="#dd3333" min="3.7 0 0" max="4 1 1">
        반입 버스: 네트워크에 저장소가 없어 반입할 곳이 없습니다.
  </BoxAnnotation>

<BoxAnnotation color="#dd3333" min="1 0 0" max="1.3 1 1">
        (2) 반출 버스: 네트워크에 저장소가 없어 반출할 것이 없습니다.
  </BoxAnnotation>

<DiamondAnnotation pos="4.5 0.5 0.5" color="#ff0000">
        출발지
    </DiamondAnnotation>

<DiamondAnnotation pos="0.5 0.5 0.5" color="#ff0000">
        목적지
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

반입 버스와 반출 버스만 연결하면 작동하지 않습니다. 반입 버스는 출발지에서 가져와 네트워크 저장소에
저장하려 하고, 반출 버스는 네트워크 저장소에서 가져와 목적지에 넣으려 합니다. 하지만 이 네트워크에는
**저장소가 없으므로** 반입도 반출도 할 수 없어 아무 일도 일어나지 않습니다.

## 한 면으로 입력하고 출력하기

<ItemLink id="charger" />처럼 한 면으로 입력을 받고 같은 면에서 출력을 꺼낼 수 있는 기계가 있다고
가정해 봅시다. 두 파이프 서브네트워크 방식을 결합하면 재료를 넣고 결과물을 꺼낼 수 있습니다.

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../assets/assemblies/import_storage_export_pipe.snbt" />

<BoxAnnotation color="#dddddd" min="4 1 1" max="5 1.3 2">
        (1) 반입 버스: 필터를 설정할 수 있습니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="2 1 1" max="3 1.3 2">
        (2) 저장 버스: 필터를 설정할 수 있습니다. 아이템을 넣고 꺼낼 다른 저장 버스와 함께 네트워크의
        유일한 저장소여야 합니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="2 0 1" max="3 1 2">
        (3) 입력하고 출력할 대상: 이 예에서는 충전기입니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="0 1 1" max="1 1.3 2">
        (4) 반출 버스: 반드시 필터를 설정해야 합니다.
  </BoxAnnotation>

<DiamondAnnotation pos="4.5 0.5 1.5" color="#00ff00">
        출발지
    </DiamondAnnotation>

<DiamondAnnotation pos="0.5 0.5 1.5" color="#00ff00">
        목적지
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 인터페이스

반입·반출 버스 외에도 [장치](../ae2-mechanics/devices.md) 중에는 아이템을
[네트워크 저장소](../ae2-mechanics/import-export-storage.md)로 넣고 가져오는 것이 있습니다. 여기서는
<ItemLink id="interface" />가 중요합니다. 비축하도록
설정되지 않은 아이템이 들어오면 인터페이스가 네트워크 저장소로 밀어내므로 반입 버스 → 저장 버스 파이프와
비슷하게 활용할 수 있습니다. 아이템 비축을 설정하면 네트워크 저장소에서 가져오므로 저장 버스 → 반출 버스와
비슷합니다. 일부는 비축하고 일부는 비축하지 않도록 설정해 저장 버스를 통해 원격으로 넣고 꺼낼 수 있습니다.

<GameScene zoom="6" background="transparent">
<ImportStructure src="../assets/assemblies/interface_pipes.snbt" />

<BoxAnnotation color="#dddddd" min="3.7 0 0" max="4 1 1">
        인터페이스
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 0 0" max="1.3 1 1">
        저장 버스
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="3.7 0 2" max="4 1 3">
        저장 버스
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="0 1 2" max="1 1.3 3">
        인터페이스
  </BoxAnnotation>

<IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 일대다, 다대일과 다대다

<ItemLink id="import_bus" />, <ItemLink id="export_bus" /> 또는 <ItemLink id="storage_bus" />를 하나씩만
사용할 필요는 없습니다.

<GameScene zoom="3" background="transparent">
<ImportStructure src="../assets/assemblies/many_to_many_pipe.snbt" />

<IsometricCamera yaw="185" pitch="30" />
</GameScene>

## 여러 장소로 공급하기

지금까지의 내용을 이용하면 <ItemLink id="pattern_provider" />의 한 면에서 기계 배열이나 한 기계의 여러
면처럼 서로 다른 여러 장소로 재료를 보낼 수 있습니다.

<ItemLink id="pattern_provider" />는 재료를 실제로 보관하지 않으므로 반입 → 저장 파이프나 저장 → 반출
파이프는 적합하지 않습니다. 공급기는 인접 인벤토리로 재료를 *밀어내므로* 아이템을 반입할 수 있는 인접
인벤토리가 필요합니다.

바로 <ItemLink id="interface" />가 그 역할을 합니다! 공급기를 방향성 또는 평면 부품 형태로 만들거나
인터페이스를 평면 부품 형태로 만들어 둘이 네트워크 연결을 형성하지 않게 하세요.

<GameScene zoom="6" background="transparent">
<ImportStructure src="../assets/assemblies/provider_interface_storage.snbt" />

<BoxAnnotation color="#dddddd" min="2.7 0 1" max="3 1 2">
        인터페이스: 완전한 블록이 아니라 평면형이어야 합니다.
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="1 0 0" max="1.3 1 4">
        저장 버스
  </BoxAnnotation>

<BoxAnnotation color="#dddddd" min="0 0 0" max="1 1 4">
        패턴 재료를 공급할 장소: 여러 기계 또는 한 기계의 여러 면
  </BoxAnnotation>

<IsometricCamera yaw="185" pitch="30" />
</GameScene>
