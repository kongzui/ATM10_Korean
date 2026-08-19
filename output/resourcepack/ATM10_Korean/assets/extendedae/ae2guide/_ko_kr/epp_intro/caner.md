---
navigation:
  parent: epp_intro/epp_intro-index.md
  title: ME 주입기
  icon: extendedae:caner
categories:
- extended devices
item_ids:
- extendedae:caner
---

# ME 주입기

<BlockImage id="extendedae:caner" scale="8"></BlockImage>

ME 주입기는 유체, Mekanism 기체, Botania 마나, 심지어 에너지까지 각종 자원을 용기에 채우는 기계입니다!

첫 번째 슬롯에는 채울 자원을, 두 번째 슬롯에는 자원을 담을 용기를 넣습니다.

작동하려면 에너지가 필요하며, 작업 한 번에 80 AE를 소모합니다.

![GUI](../pic/caner_gui.png)

기본적으로 유체만 채울 수 있습니다. 다른 자원을 채우려면 해당 애드온을 설치해야 합니다.

### 지원 애드온:
- Applied Flux
- Applied Mekanistics
- Applied Botanics Addon

## ME 주입기로 자동 제작하기

위쪽과 아래쪽 면만 에너지를 받거나 네트워크에 연결할 수 있습니다.

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../structure/caner_example.snbt"></ImportStructure>
</GameScene>

간단한 ME 주입기 구성입니다. ME 주입기가 <ItemLink id="ae2:pattern_provider" />에서 재료를 받으면 내용물을 채운 아이템을 자동으로 내보냅니다.

<GameScene zoom="6" background="transparent">
  <ImportStructure src="../structure/caner_auto.snbt"></ImportStructure>
</GameScene>

패턴에는 채울 자원과 자원을 담을 용기만 들어가야 합니다. 다음은 몇 가지 예시입니다.

물 양동이 채우기:

![물 양동이](../pic/fill_water.png)

에너지 태블릿 충전하기(Applied Flux 설치 필요):

![에너지 태블릿](../pic/fill_energy.png)


## 내용물 비우기

ME 주입기는 비우기 모드에서 용기의 내용물을 빼낼 수도 있습니다. 이때는 패턴의 입력과 출력을 서로 바꿔야 합니다.
