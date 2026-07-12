---
navigation:
  parent: ae2-mechanics/ae2-mechanics-index.md
  title: 채널
  icon: controller
---

# 채널

Applied Energistics 2의 [ME 네트워크](me-network-connections.md)는 네트워크 저장소나 다른 네트워크
서비스를 사용하는 [장치](../ae2-mechanics/devices.md)를 지원하기 위해 채널이 필요합니다. 채널을 모든
장치로 이어지는 USB 케이블처럼 생각하면 됩니다. 컴퓨터의 USB 포트 수가 한정되어 연결할 수 있는 장치
수도 제한되는 것과 같습니다. 대부분의 기계, 완전한 블록 형태의 장치와 일반 케이블은 최대 8채널만
전달할 수 있습니다. 완전한 블록 장치와 일반 케이블을 8개의 "채널 선" 묶음으로 생각할 수 있습니다.
하지만 [조밀 케이블](../items-blocks-machines/cables.md#dense-cable)은 최대 32채널을 지원합니다. 이외에
32채널을 전달할 수 있는 장치는 <ItemLink id="me_p2p_tunnel" />과
[양자 네트워크 연결기](../items-blocks-machines/quantum_bridge.md)뿐입니다. 장치 하나가 채널을 사용할
때마다 묶음에서 USB "선" 하나를 떼어낸다고 생각하세요. 그러면 당연히 그 뒤쪽에서는 해당 선을 사용할
수 없습니다.

<GameScene zoom="7" interactive={true}>
  <ImportStructure src="../assets/assemblies/channel_demonstration_1.snbt" />

  <LineAnnotation color="#33ff33" from="1 .4 .7" to="2.4 .4 .7" alwaysOnTop={true}/>
  <LineAnnotation color="#33ff33" from="1 .6 .7" to="2.4 .6 .7" alwaysOnTop={true}/>
  <LineAnnotation color="#33ff33" from="1 .4 .6" to="2.6 .4 .6" alwaysOnTop={true}/>
  <LineAnnotation color="#33ff33" from="1 .6 .6" to="2.6 .6 .6" alwaysOnTop={true}/>
  <LineAnnotation color="#33ff33" from="1 .6 .6" to="2.6 .6 .6" alwaysOnTop={true}/>

  <LineAnnotation color="#33ff33" from="2.4 .6 .7" to="2.4 .6 1.5" alwaysOnTop={true}/>
  <LineAnnotation color="#33ff33" from="2.4 .4 .7" to="2.4 .4 1.5" alwaysOnTop={true}/>
  <LineAnnotation color="#33ff33" from="2.6 .6 .6" to="2.6 .6 1.5" alwaysOnTop={true}/>
  <LineAnnotation color="#33ff33" from="2.6 .4 .6" to="2.6 .4 1.5" alwaysOnTop={true}/>

  <LineAnnotation color="#33ff33" from="2.1 .6 1.5" to="2.4 .6 1.5" alwaysOnTop={true}/>
  <LineAnnotation color="#33ff33" from="2.6 .4 1.5" to="2.9 .4 1.5" alwaysOnTop={true}/>

  <LineAnnotation color="#33ff33" from="2.6 .6 1.5" to="2.6 .9 1.5" alwaysOnTop={true}/>
  <LineAnnotation color="#33ff33" from="2.4 .1 1.5" to="2.4 .4 1.5" alwaysOnTop={true}/>

  <LineAnnotation color="#33ff33" from="1 .6 .4" to="3.5 .6 .4" alwaysOnTop={true}/>
  <LineAnnotation color="#33ff33" from="1 .4 .4" to="3.5 .4 .4" alwaysOnTop={true}/>

  <LineAnnotation color="#33ff33" from="3.5 .6 .4" to="3.5 .9 .4" alwaysOnTop={true}/>
  <LineAnnotation color="#33ff33" from="3.5 .1 .4" to="3.5 .4 .4" alwaysOnTop={true}/>

  <LineAnnotation color="#33ff33" from="1 .6 .3" to="1.5 .6 .3" alwaysOnTop={true}/>
  <LineAnnotation color="#33ff33" from="1 .4 .3" to="1.5 .4 .3" alwaysOnTop={true}/>

  <LineAnnotation color="#33ff33" from="1.5 .6 .3" to="1.5 .9 .3" alwaysOnTop={true}/>
  <LineAnnotation color="#33ff33" from="1.5 .1 .3" to="1.5 .4 .3" alwaysOnTop={true}/>

  <LineAnnotation color="#ff3333" from="3.5 .5 .5" to="5.5 .5 .5" alwaysOnTop={true}>
  케이블의 8채널을 모두 사용해 ME 드라이브에 할당할 채널이 없습니다.
  </LineAnnotation>

  <LineAnnotation color="#993333" from="1 .5 .5" to="1.25 .5 .5" alwaysOnTop={true}/>
  <LineAnnotation color="#993333" from="1.5 .5 .5" to="1.75 .5 .5" alwaysOnTop={true}/>
  <LineAnnotation color="#993333" from="2 .5 .5" to="2.25 .5 .5" alwaysOnTop={true}/>
  <LineAnnotation color="#993333" from="2.5 .5 .5" to="2.75 .5 .5" alwaysOnTop={true}/>
  <LineAnnotation color="#993333" from="3 .5 .5" to="3.25 .5 .5" alwaysOnTop={true}/>

  <DiamondAnnotation pos="3.6 0.5 0.5" color="#ff0000">
        케이블의 8채널을 모두 사용해 ME 드라이브에 할당할 채널이 없습니다.
    </DiamondAnnotation>

  <IsometricCamera yaw="15" pitch="30" />
</GameScene>

[스마트 케이블](../items-blocks-machines/cables.md)을 사용하면 네트워크에서 채널이 사용되고 전달되는
경로를 쉽게 볼 수 있습니다. 케이블 표면에 채널 경로와 사용량이 표시됩니다.

채널은 통과하는 노드마다 1⁄128 AE/t를 소비합니다. 장치 8개와 노드 96개가 넘는 네트워크에
<ItemLink id="controller" />를 추가하면 채널 할당 방식이 바뀌어 오히려 전력 소비량이 줄어들 수도
있습니다.

중요한 점으로, **채널은 케이블 색상과 아무 관계가 없습니다**. 케이블 색상은 서로 연결되지 않게 할
뿐입니다.

## 채널 경로

<ItemLink id="controller" />를 사용하면 채널은 3단계로 경로를 찾습니다. 먼저 인접한 기계를 통과하는
가장 짧은 경로로 가까운 [일반 케이블](../items-blocks-machines/cables.md), 즉 유리·차폐·스마트 케이블에
도달합니다. 그다음 일반 케이블에서 가장 가까운 [조밀 케이블](../items-blocks-machines/cables.md), 즉
조밀·조밀 스마트 케이블까지 가장 짧은 경로를 택합니다. 마지막으로 조밀 케이블을 따라
<ItemLink id="controller" />까지 가장 짧은 경로로 이동합니다. 최단 경로의 용량이 이미 가득 차면 일부
[장치](devices.md)가 필요한 채널을 받지 못할 수 있습니다. 색상 케이블, 케이블 고정대와 터널을 활용해
채널이 원하는 경로로 흐르도록 만드세요.

다음 예에서는 케이블 전체 용량은 충분하지만 채널이 최단 경로를 선택하면서 일부 케이블만 과부하되고
다른 케이블은 비어 있어 몇몇 ME 드라이브가 채널을 받지 못합니다.

<GameScene zoom="4" interactive={true}>
  <ImportStructure src="../assets/assemblies/channel_path_length_issue.snbt" />

  <LineAnnotation color="#33ff33" from="3 .5 1.4" to="0.4 0.5 1.4" alwaysOnTop={true} thickness="0.05"/>
  <LineAnnotation color="#33ff33" from="0.4 .5 1.4" to="0.4 0.5 3.6" alwaysOnTop={true} thickness="0.05"/>
  <LineAnnotation color="#33ff33" from="0.4 0.5 3.6" to="1.4 0.5 3.6" alwaysOnTop={true} thickness="0.05"/>
  <LineAnnotation color="#33ff33" from="1.4 0.5 3.6" to="1.4 0.5 5" alwaysOnTop={true} thickness="0.05"/>

  <LineAnnotation color="#33ff33" from="3 0.5 3.6" to="1.6 0.5 3.6" alwaysOnTop={true} thickness="0.05"/>
  <LineAnnotation color="#33ff33" from="1.6 0.5 3.6" to="1.6 0.5 5" alwaysOnTop={true} thickness="0.05"/>

  <LineAnnotation color="#ff3333" from="3 .5 1.6" to="0.6 .5 1.6" alwaysOnTop={true} thickness="0.05"/>
  <LineAnnotation color="#ff3333" from="0.6 .5 1.6" to="0.6 .5 3.4" alwaysOnTop={true} thickness="0.05"/>
  <LineAnnotation color="#ff3333" from="0.6 .5 3.4" to="1.4 .5 3.4" alwaysOnTop={true} thickness="0.05"/>

  <LineAnnotation color="#ff3333" from="3 .5 3.4" to="1.6 .5 3.4" alwaysOnTop={true} thickness="0.05"/>

  <BoxAnnotation color="#dddddd" min="1.2 0.2 3.2" max="1.8 0.8 3.8" alwaysOnTop={true} thickness="0.05">
        8개가 넘는 채널이 이곳을 통과하려 하므로 일부 채널이 끊깁니다.
  </BoxAnnotation>

  <IsometricCamera yaw="90" pitch="90" />

</GameScene>

채널이 갈 수 있는 경로를 더 꼼꼼하게 제한하면 해결할 수 있습니다. 네트워크는 나무나 덤불처럼 뻗는
구조가 좋습니다. 순환 경로와 여러 방향으로 해석될 수 있는 채널 경로를 최소화하세요.

<GameScene zoom="4" interactive={true}>
  <ImportStructure src="../assets/assemblies/channel_path_length_issue_fix.snbt" />

  <LineAnnotation color="#33ff33" from="3 .5 1.4" to="0.4 0.5 1.4" alwaysOnTop={true} thickness="0.05"/>
  <LineAnnotation color="#33ff33" from="0.4 .5 1.4" to="0.4 0.5 5.6" alwaysOnTop={true} thickness="0.05"/>
  <LineAnnotation color="#33ff33" from="0.4 0.5 5.6" to="1 0.5 5.6" alwaysOnTop={true} thickness="0.05"/>

  <LineAnnotation color="#33ff33" from="3 0.5 3.6" to="1.6 0.5 3.6" alwaysOnTop={true} thickness="0.05"/>
  <LineAnnotation color="#33ff33" from="1.6 0.5 3.6" to="1.6 0.5 5" alwaysOnTop={true} thickness="0.05"/>

  <IsometricCamera yaw="90" pitch="90" />

</GameScene>

## 임시 네트워크

<ItemLink id="controller" />가 없는 네트워크는 임시 네트워크로 간주되며 채널을 사용하는 장치를 최대
8개까지 지원합니다. 장치가 8개를 넘으면 채널을 사용하는 장치가 종료됩니다. 장치를 제거하거나
<ItemLink id="controller" />를 추가하세요.

제어기가 있는 네트워크와 달리, 임시 네트워크의 [스마트 케이블](../items-blocks-machines/cables.md)은 해당
케이블을 통과하는 채널 수가 아니라 네트워크 전체에서 사용 중인 채널 수를 표시합니다.

임시 네트워크에서는 각 장치가 네트워크 전체에서 채널 하나씩을 사용합니다. 이는
<ItemLink id="controller" />가 최단 경로에 따라 채널을 할당하는 방식과 매우 다릅니다.

## 설계

앞서 [채널 경로](channels.md#channel-routing)에서 설명했듯 네트워크는 나무처럼 설계하는 것이 좋습니다.
제어기에서 조밀 케이블이 뻗고, 조밀 케이블에서 일반 케이블이 갈라지며, 일반 케이블에는
[장치](../ae2-mechanics/devices.md)를 8개 이하의 묶음으로 연결하세요.

다음은 피해야 할 구성입니다.

채널 경로를 따라가 보겠습니다.

1. 제어기에서 오른쪽으로 나오자마자 ME 드라이브가 일반 케이블처럼 작동해 8채널로 병목이 생깁니다.
스마트 케이블을 사용하지 않아 사용 중인 채널 수는 보이지 않습니다. 8채널이 남습니다.
2. ME 드라이브가 채널 하나를 사용합니다. 7채널이 남습니다.
3. 터미널로 채널 2개가 올라갑니다. 5채널이 남습니다.
4. 오른쪽으로 계속 가면 인터페이스가 채널 하나를 더 사용합니다. 4채널이 남습니다.
5. 패턴 공급기로 채널 하나가 올라갑니다. 3채널이 남습니다.
6. 오른쪽의 반입 버스로 채널 하나가 올라갑니다. 2채널이 남습니다.
7. 분자 조립기에 재료를 공급하는 패턴 공급기 묶음은 채널 2개만 받아 공급기 2개에는 채널이 없습니다.

결국 문제는 채널에 병목을 만들고 채널이 어떻게 분배될지 충분히 고려하지 않은 것입니다.

<GameScene zoom="4" interactive={true}>
  <ImportStructure src="../assets/assemblies/bad_network_structure.snbt" />

<LineAnnotation color="#33ff33" from="6.5 .5 1.5" to="6 .5 1.5" alwaysOnTop={true} thickness="0.4">
  32채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="6 .5 1.5" to="5.5 .5 1.5" alwaysOnTop={true} thickness="0.2">
  8채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="5.5 .5 1.5" to="5.5 1.5 1.5" alwaysOnTop={true} thickness="0.1">
  2채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="5.5 .5 1.5" to="5.5 .3 1.5" alwaysOnTop={true} thickness="0.071">
  1채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="5.5 1.5 1.5" to="5.5 2.5 1.5" alwaysOnTop={true} thickness="0.071">
  1채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="5.5 2.5 1.5" to="5.5 2.5 1.1" alwaysOnTop={true} thickness="0.071">
  1채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="5.5 .5 1.5" to="4.5 .5 1.5" alwaysOnTop={true} thickness="0.158">
  5채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="4.5 .5 1.5" to="4.5 .3 1.5" alwaysOnTop={true} thickness="0.071">
  1채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="4.5 .5 1.5" to="4.5 1.5 1.5" alwaysOnTop={true} thickness="0.071">
  1채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="4.5 .5 1.5" to="3.5 .5 1.5" alwaysOnTop={true} thickness="0.122">
  3채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="3.5 .5 1.5" to="3.5 2.5 1.5" alwaysOnTop={true} thickness="0.071">
  1채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="3.5 2.5 1.5" to="3.7 2.5 1.5" alwaysOnTop={true} thickness="0.071">
  1채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="3.5 .5 1.5" to="1.5 .5 1.5" alwaysOnTop={true} thickness="0.1">
  2채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="1.5 0.5 1.5" to="1.5 0.3 1.5" alwaysOnTop={true} thickness="0.071">
  1채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="1.5 0.5 1.5" to="0.5 0.5 1.5" alwaysOnTop={true} thickness="0.071">
  1채널
</LineAnnotation>

<LineAnnotation color="#33ff33" from="0.5 0.5 1.5" to="0.5 0.5 0.5" alwaysOnTop={true} thickness="0.071">
  1채널
</LineAnnotation>

<LineAnnotation color="#ff3333" from="0.5 1.5 1.5" to="0.5 1.3 1.5" alwaysOnTop={true} thickness="0.071">
  채널 없음
</LineAnnotation>

<LineAnnotation color="#ff3333" from="1.5 1.5 0.5" to="1.5 1.3 0.5" alwaysOnTop={true} thickness="0.071">
  채널 없음
</LineAnnotation>

  <IsometricCamera yaw="195" pitch="30" />
</GameScene>

---

다음은 좋은 구조의 예입니다.

<GameScene zoom="2.5" interactive={true}>
  <ImportStructure src="../assets/assemblies/treelike_network_structure.snbt" />

    <BoxAnnotation color="#dddddd" min="6.9 0 4.9" max="9.1 4 7.1" thickness="0.05">
        패턴 공급기가 8개씩 별도 묶음으로 나뉜 점에 주목하세요.
    </BoxAnnotation>

    <BoxAnnotation color="#dddddd" min="5 4 4" max="8 5 5" thickness="0.05">
        채널이 가득 찬 일반 케이블 두 개가 합쳐지므로 조밀 케이블이 필요합니다.
    </BoxAnnotation>

    <BoxAnnotation color="#dddddd" min="5 0 13" max="8 1 14" thickness="0.05">
        인접한 케이블이 연결되지 않도록 서로 다른 케이블 색상을 사용했습니다.
    </BoxAnnotation>


  <IsometricCamera yaw="315" pitch="30" />
</GameScene>

## 채널 모드

Minecraft 1.18용 AE2 10.0.0부터 월드에서 AE2 채널이 작동하는 방식을 바꾸는 선택지가 추가되었습니다.
일반 설정의 `channels` 항목으로 제어할 수 있으며, 운영자는 게임 안에서 명령어로 모드와 설정을 바꿀
수 있습니다. `/ae2 channelmode <mode>`로 모드를 변경하고 `/ae2 channelmode`로 현재 모드를 확인합니다.
게임 안에서 모드를 바꾸면 기존의 모든 그리드가 재부팅되어 즉시 새 모드를 사용합니다.

이는 Minecraft 1.12에 있던 선택지를 되살려 개선한 기능입니다. 채널 시스템을 완전히 제거하고 싶지는
않지만 조금 더 편안하게 플레이하려는 사용자에게 더 나은 선택지를 제공합니다.

다음 표는 설정 파일과 명령어에서 사용할 수 있는 모드를 보여 줍니다.

| 설정       | 설명 |
| ---------- | ---- |
| `default`  | 이 가이드에서 설명하는 일반 케이블과 임시 네트워크의 표준 채널 용량을 사용합니다. |
| `x2`       | 모든 채널 용량이 두 배가 됩니다. 일반 케이블 16, 조밀 케이블 64, 임시 네트워크 16채널입니다. |
| `x3`       | 모든 채널 용량이 세 배가 됩니다. 일반 케이블 24, 조밀 케이블 92, 임시 네트워크 24채널입니다. |
| `x4`       | 모든 채널 용량이 네 배가 됩니다. 일반 케이블 32, 조밀 케이블 128, 임시 네트워크 32채널입니다. |
| `infinite` | 모든 채널 제한을 제거합니다. 제어기는 여전히 그리드의 전력 소비를 *크게* 줄입니다. 스마트 케이블은 채널을 전혀 운반하지 않는 꺼짐 상태와 하나 이상 운반하는 켜짐 상태만 표시합니다. |
