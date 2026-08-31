---
navigation:
  parent: enderdrives_intro/enderdrives_intro-index.md
  title: 테이프 디스크 아이템 저장 셀
  icon: enderdrives:tape_disk
categories:
  - tapedrives
item_ids:
  - enderdrives:tape_disk
---

# 테이프 드라이브

테이프 드라이브는 도구, 방어구, 마법이 부여된 장비처럼 **NBT 데이터가 많은 아이템**이나, 같은 종류로 묶이지 않아 기존 ME 드라이브의 종류 한도를 빠르게 소모하는 아이템을 보관하도록 설계된 AE2 호환 저장 셀입니다.

일반적인 AE2 드라이브와 달리 테이프 디스크의 바이트 사용량은 저장된 아이템의 실제 **NBT 크기**에 따라 동적으로 변하므로 시스템을 세밀하게 관리할 수 있습니다. 테이프 드라이브는 필터에 맞는 아이템을 우선 저장해야 한다고 AE2에 알리지 **않습니다**. ME 드라이브의 우선순위 설정을 사용하세요.

<Row gap="10">
  <Column>
    <ItemImage id="enderdrives:tape_disk" />
  </Column>
  <Column>
    <ItemLink id="enderdrives:tape_disk" />
  </Column>
</Row>

---

## 작동 방식

각 테이프 디스크에는 비표준 NBT가 있는 아이템, 방어구나 도구, 중첩할 수 없는 아이템만 저장할 수 있습니다.

---

## 바이트 및 종류 한도

테이프 디스크에는 **종류 한도**와 **바이트 사용량 한도**가 모두 적용됩니다.

- **종류 한도** – 저장할 수 있는 고유 아이템 종류의 최대 수입니다(예: 마법이 부여된 책, 맞춤형 방어구).
- **바이트 한도** – 각 아이템의 **NBT 데이터 크기**에 따라 결정됩니다. Apotheosis 장비처럼 태그가 많은 아이템은 NBT의 양 때문에 더 많은 공간을 사용합니다.

테이프 디스크는 **NBT 데이터가 많은 아이템**을 보관하도록 설계되어, 서로 다른 장비나 개별 아이템이 기존 드라이브의 종류 공간을 차지하지 않게 분리하기에 적합합니다.

---


## 테이프 디스크를 사용할 때

다음과 같은 경우 기존 드라이브 대신 테이프 디스크를 사용하세요.

- 방어구, 도구나 장비처럼 **중첩할 수 없는 아이템**을 저장할 때
- **NBT 데이터가 많은 모드 아이템**을 저장할 공간이 필요할 때
- 특수 아이템을 일반 ME 드라이브와 분리하고 싶을 때

테이프 드라이브는 일반 드라이브의 종류 한도를 빠르게 소모하는 아이템을 처리하는 데 뛰어납니다.

---

## ME 입출력 포트 전송

테이프 디스크는 ME 입출력 포트를 통해 아이템을 주고받을 때 전송 속도를 자동으로 제한합니다. NBT 데이터가 많은 아이템을 한꺼번에 쏟아 내어 게임이 멈추는 것을 방지하기 위해서입니다.

---

## 저장할 수 있는 아이템

테이프 디스크는 **NBT 데이터가 많거나**, **중첩할 수 없거나**, **고유 데이터가 있는** 아이템을 위한 특수 저장소이며 일반 대량 저장소가 아닙니다.

---

### 저장 가능

| 아이템                                | 예시                                  |
|-------------------------------------|------------------------------------------|
| <ItemImage id="minecraft:diamond_chestplate" /> | 마법이 부여된 **다이아몬드 흉갑** |
| <ItemImage id="minecraft:enchanted_book" />     | 마법이 부여된 **책**                 |
| <ItemImage id="minecraft:splash_potion" />      | 효과가 있는 **투척용 물약**           |
| <ItemImage id="minecraft:netherite_pickaxe" />  | 내구도가 있는 **도구**                  |

---

### 저장 불가

| 아이템                              | 이유                         |
|-----------------------------------|--------------------------------|
| <ItemImage id="minecraft:cobblestone" /> | NBT 없음, 중첩 가능              |
| <ItemImage id="minecraft:wheat" />       | NBT 없음, 중첩 가능  |
| <ItemImage id="minecraft:oak_log" />     | NBT 없음, 중첩 가능             |
| <ItemImage id="minecraft:apple" />       | NBT 없음, 중첩 가능    |
| <ItemImage id="minecraft:iron_ingot" />  | NBT 없음, 중첩 가능    |

---
