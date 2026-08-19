---
navigation:
  parent: example-setups/example-setups-index.md
  title: 자동 조절 조약돌 생성기
  icon: minecraft:cobblestone
---

# 자동 조절 조약돌 생성기

조약돌 생성기 자동화는 간단합니다. 표준 바닐라 수동 조약돌 생성기를 향해 <ItemLink id="annihilation_plane" />을
설치하면 됩니다. 하지만 그대로 두면 결국 네트워크가 조약돌로 가득 차 막히므로 조절 장치가 필요합니다.

소멸 평면은 <ItemLink id="import_bus" />처럼 작동하므로 <ItemLink id="level_emitter" />를
<ItemLink id="export_bus" /> 쪽에 설치하고 <ItemLink id="redstone_card" />를 넣는 단순한 방법은 쓸 수 없습니다.
(중간에 저장소 없이 반입에서 반출로 바로 보낼 수 없기 때문입니다.) 조금 우회해야 합니다.

<ItemLink id="toggle_bus" />를 사용하면 레드스톤 신호로 네트워크 일부를 연결하거나 끊을 수 있지만,
그때마다 네트워크가 재부팅됩니다. 토글 버스를 [서브네트워크](../ae2-mechanics/subnetworks.md)에 두어
해당 서브네트워크만 재부팅되게 하면 간단히 해결할 수 있습니다.

<ItemLink id="annihilation_plane" />과 <ItemLink id="storage_bus" />로 독립된 [서브네트워크](../ae2-mechanics/subnetworks.md)를
구성하여 주 네트워크의 <ItemLink id="interface" />로 밀어 넣을 수 있습니다. 토글 버스는 서브네트워크와
<ItemLink id="quartz_fiber" />의 연결을 제어하여 평면의 전력을 끊습니다.

<GameScene zoom="4" interactive={true}>
  <ImportStructure src="../assets/assemblies/regulated_cobble_gen.snbt" />

<BoxAnnotation color="#dddddd" min="3 2 2" max="7 2.3 3">
        (1) 소멸 평면: 설정 GUI는 없지만 효율과 내구성 마법을 부여하여 전력 소모를 줄일 수 있습니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2 2 2" max="2.3 3 3">
        (2) 저장 버스: 기본 설정입니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2.3 2.3 2" max="2.7 2.7 2.3">
        (3) 토글 버스: 반드시 주 네트워크가 아니라
        서브네트워크에 두어야 합니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="2.3 3 2.3" max="2.7 3.3 2.7">
        (4) 레벨 방출기: 조약돌과 원하는 수량으로 설정하고 "수량이 한도 미만일 때 방출"로 지정했습니다.
  </BoxAnnotation>

  <BoxAnnotation color="#dddddd" min="1 2 3" max="2 3 2">
        (5) 인터페이스: 기본 설정입니다.
  </BoxAnnotation>

<DiamondAnnotation pos="0 2.5 1.5" color="#00ff00">
        주 네트워크로
    </DiamondAnnotation>

<DiamondAnnotation pos="5 1.5 3.5" color="#00ff00">
        물이 든 계단은 물의 흐름을 막아 용암이 흑요석으로 변하지 않게 합니다.
    </DiamondAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

## 설정

* <ItemLink id="annihilation_plane" /> (1)은 설정 GUI가 없지만 효율과 내구성 마법을 부여하여 전력 소모를 줄일 수 있습니다.
* <ItemLink id="storage_bus" /> (2)는 기본 설정입니다.
* <ItemLink id="toggle_bus" /> (3)은 반드시 주 네트워크가 아니라 석영 섬유의 서브네트워크 쪽에 있어야 합니다. 그렇지 않으면 토글할 때마다 주 네트워크가 재부팅됩니다.
* <ItemLink id="level_emitter" /> (4)는 원하는 아이템과 수량으로 설정하고 "수량이 한도 미만일 때 방출"로 지정했습니다.
* <ItemLink id="interface" /> (5)는 기본 설정입니다.

## 작동 원리

1. 조약돌 생성기가 조약돌을 만듭니다.
2. <ItemLink id="annihilation_plane" />이 조약돌을 캡니다.
3. <ItemLink id="storage_bus" />가 조약돌을 <ItemLink id="interface" />에 저장하여 주 네트워크로 보냅니다.
4. 주 네트워크의 조약돌 수량이 설정값을 넘으면 <ItemLink id="level_emitter" />가 신호 방출을 멈추어
   <ItemLink id="toggle_bus" />를 끕니다.
5. 서브네트워크의 전력이 끊기면서 소멸 평면이 작동을 멈춥니다.
