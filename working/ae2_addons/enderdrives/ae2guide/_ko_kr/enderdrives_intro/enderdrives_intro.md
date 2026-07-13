---
navigation:
  parent: enderdrives_intro/enderdrives_intro-index.md
  title: 엔더 아이템 저장 셀
  icon: enderdrives:ender_disk_1k
categories:
  - enderdrives
item_ids:
  - enderdrives:ender_disk_1k
  - enderdrives:ender_disk_4k
  - enderdrives:ender_disk_16k
  - enderdrives:ender_disk_64k
  - enderdrives:ender_disk_256k
  - enderdrives:ender_disk_creative
---

# 엔더 드라이브

엔더 드라이브는 주파수를 통해 여러 ME 시스템과 차원, 심지어 서로 다른 플레이어 사이에서도 전역 동기화 저장소를 제공하는 강력한 드라이브입니다.

<Row gap="10">
  <Column>
    <ItemImage id="enderdrives:ender_disk_1k" />
  </Column>
  <Column>
    <ItemLink id="enderdrives:ender_disk_1k" />
  </Column>
</Row>

<Row gap="10">
  <Column>
    <ItemImage id="enderdrives:ender_disk_4k" />
  </Column>
  <Column>
    <ItemLink id="enderdrives:ender_disk_4k" />
  </Column>
</Row>

<Row gap="10">
  <Column>
    <ItemImage id="enderdrives:ender_disk_16k" />
  </Column>
  <Column>
    <ItemLink id="enderdrives:ender_disk_16k" />
  </Column>
</Row>

<Row gap="10">
  <Column>
    <ItemImage id="enderdrives:ender_disk_64k" />
  </Column>
  <Column>
    <ItemLink id="enderdrives:ender_disk_64k" />
  </Column>
</Row>

<Row gap="10">
  <Column>
    <ItemImage id="enderdrives:ender_disk_256k" />
  </Column>
  <Column>
    <ItemLink id="enderdrives:ender_disk_256k" />
  </Column>
</Row>

---

## 작동 방식
각 엔더 드라이브에는 주파수, 공유 범위와 모드를 설정합니다.
- **주파수**: 같은 주파수의 드라이브는 같은 인벤토리를 공유합니다.
- **공유 범위**: 드라이브에 접근할 수 있는 대상을 결정합니다(전체 공개, 비공개 또는 팀).
- **모드**: 아이템의 이동 방향을 제어합니다(양방향, 입력, 출력).

주파수와 공유 범위가 같은 모든 드라이브는 어디에 있든 **동일한 가상 인벤토리**에 접근합니다.

---

## 종류 한도
기존 AE2 드라이브와 달리 엔더 드라이브의 한도는 종류 수만으로 결정됩니다. 내부적으로 아이템을 저장하는 방식 때문에 유일한 절대 한도는 종류 수입니다. 종류마다 최대 2^63 - 1개, 즉 9,223,372,036,854,775,807개의 아이템을 저장할 수 있습니다. 단, 해당 주파수의 드라이브에 저장된 아이템이 많을수록 전력 소모량이 증가하니 주의하세요!

서버마다 부하가 발생하기 시작하는 종류 수가 다릅니다. 자동 벤치마크 명령어로 서버를 시험할 수 있습니다. 정확한 결과를 얻으려면 선택한 주파수의 드라이브를 비공개로 설정하고 터미널을 열어 두어야 합니다. 벤치마크는 TPS가 18 아래로 떨어질 때까지 계속되며 몇 분이 걸릴 수 있습니다.

제 환경의 평균은 약 275,000종입니다. 275,000/255 ≈ 1078입니다. 즉 성능 문제가 나타나기 전에 256k 엔더 드라이브와 서로 다른 종류의 아이템으로 ME 드라이브 107.8개를 채워야 합니다. 권장 최대 종류 수는 이보다 높거나 낮을 수 있습니다. 이 한도는 같은 월드에서 드라이브를 이용하는 모든 사용자가 공유합니다.

---

## 드라이브 모드
각 드라이브는 다음 세 가지 **전송 모드** 중 하나로 설정할 수 있습니다.

- ![양방향](../pic/transport_bidirectional_alt.png) **양방향** _(기본값)_
  일반적인 ME 드라이브처럼 작동합니다. 아이템을 자유롭게 넣고 꺼낼 수 있습니다.


- ![입력 전용](../pic/transport_input_alt.png) **입력 전용**
  아이템을 넣을 수 있지만 꺼낼 수는 없습니다. 입력 동기화나 버퍼에 유용합니다.


- ![출력 전용](../pic/transport_output_alt.png) **출력 전용**
  아이템을 꺼낼 수 있지만 넣을 수는 없습니다. 출력 버퍼나 읽기 전용 저장소에 적합합니다.

---

## 공유 범위 및 공개 설정

각 드라이브에는 인벤토리에 접근할 수 있는 대상을 제어하는 **공유 범위**도 있습니다.
-  **전체 공개** _(기본값)_
   공개 저장소입니다! 같은 주파수를 사용하는 모든 플레이어가 공유 인벤토리에 접근할 수 있습니다.


-  **비공개**
  UUID에 연결됩니다. 해당 주파수에 접근하는 드라이브는 본인만 만들 수 있습니다. 단, ME 시스템의 다른 사용자는 여전히 이 저장소에 접근할 수 있습니다.


-  **팀**
  FTB 팀과 공유합니다. 모든 팀원이 같은 주파수에 접근하는 드라이브를 만들 수 있습니다.
