---
navigation:
  parent: epp_intro/epp_intro-index.md
  title: ME 무선 연결기
  icon: extendedae:wireless_connect
categories:
- extended devices
item_ids:
- extendedae:wireless_connect
- extendedae:wireless_tool
---

# ME 무선 연결기

<Row gap="20">
<BlockImage id="extendedae:wireless_connect" scale="6"></BlockImage>
<ItemImage id="extendedae:wireless_tool" scale="6"></ItemImage>
</Row>

ME 무선 연결기는 <ItemLink id="ae2:quantum_link" />처럼 두 네트워크를 연결할 수 있지만 거리에 제한이 있고 차원을 넘을 수 없습니다. ME 무선 연결기는 일대일 연결만 지원하므로 다대다 연결이 필요하다면 <ItemLink id="extendedae:wireless_hub" />를 사용해야 합니다.

## 무선 연결기 연결하기

ME 무선 설정 키트로 연결할 무선 연결기 두 개를 차례로 클릭하면 서로 연결됩니다.

웅크린 채 클릭하면 ME 무선 설정 키트의 현재 설정을 지웁니다.

연결이 성공하면 ME 무선 연결기의 모습이 바뀝니다.

연결되지 않은 ME 무선 연결기

<GameScene zoom="5" background="transparent">
  <ImportStructure src="../structure/wireless_connector_off.snbt"></ImportStructure>
</GameScene>

연결된 ME 무선 연결기

<GameScene zoom="5" background="transparent">
  <ImportStructure src="../structure/wireless_connector_on.snbt"></ImportStructure>
</GameScene>

## 색상

무선 연결기는 케이블처럼 색칠할 수 있으며 같은 색상의 케이블 및 연결기에만 연결됩니다.

연결기를 색칠하려면 <ItemLink id="ae2:color_applicator" />가 필요합니다.

따라서 다음과 같이 무선 연결기를 구성할 수 있습니다.

<GameScene zoom="3" background="transparent" interactive={true}>
  <ImportStructure src="../structure/wireless_connector_setup.snbt"></ImportStructure>
</GameScene>

## 전력 사용량

ME 무선 연결기는 거리가 멀수록 더 많은 에너지를 소모합니다. 거리와 소모 전력의 관계는 선형이 아니므로 너무 멀리 떨어뜨리면 전력 소모가 매우 커질 수 있습니다.

<ItemLink id="ae2:energy_card" />로 전력을 절약할 수 있으며, 카드 하나마다 에너지 소모가 10% 감소합니다.
