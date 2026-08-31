---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 진동실
  icon: vibration_chamber
  position: 110
categories:
- network infrastructure
item_ids:
- ae2:vibration_chamber
---

# 진동실

<BlockImage id="vibration_chamber" p:active="true" scale="8" />

네트워크에 [에너지](../ae2-mechanics/energy.md)를 공급하는 주된 방법은 <ItemLink id="energy_acceptor" />이지만,
진동실은 적은 양에서 중간 정도의 AE를 직접 생성할 수 있습니다.

기본 상태([업그레이드](upgrade_cards.md) 없음, 기본 설정)에서는 40 AE/t를 생성합니다.

네트워크의 [에너지](../ae2-mechanics/energy.md) 저장소가 가득 차면 연료를 아끼도록 진동실의 속도가 낮아지지만 완전히 꺼지지는 않습니다.

## 설정

*   진동실에서 에너지를 AE 또는 E/FE로 표시하는 전역 설정을 바꿀 수 있습니다.

## 업그레이드

진동실은 다음 [업그레이드](upgrade_cards.md)를 지원합니다.

*   <ItemLink id="energy_card" />는 진동실의 효율을 장당 +50%, 최대 +150%까지 높여 기본 효율의 250%로 만듭니다.
*   <ItemLink id="speed_card" />는 진동실의 연소 속도를 장당 +50%, 최대 +150%까지 높여 기본 출력의 250%로 만듭니다.

## 설정 파일

진동실의 속성은 .minecraft\
디렉터리의 config 폴더 아래 ae2 폴더에 있는 common.json에서 수정할 수 있습니다.

*   baseEnergyPerFuelTick은 업그레이드하지 않은 진동실의 기본 효율을 설정합니다.
*   minEnergyPerGameTick은 가능한 최저 에너지 생성량을 설정합니다(네트워크에 에너지가 필요하지 않아도 진동실은 항상 연료를 조금씩 사용합니다).
*   maxEnergyPerGameTick은 업그레이드하지 않은 진동실의 최대 출력과 속도를 설정합니다.

## 조합법

<RecipeFor id="vibration_chamber" />
