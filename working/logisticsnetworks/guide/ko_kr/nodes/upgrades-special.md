---
item_ids: [logisticsnetworks:dimensional_upgrade, logisticsnetworks:mekanism_chemical_upgrade, logisticsnetworks:ars_source_upgrade]
navigation:
  title: 특수 업그레이드
  parent: nodes/index.md
  icon: logisticsnetworks:dimensional_upgrade
  position: 5
---

# 특수 업그레이드

특수 업그레이드는 노드의 전송량 한도를 바꾸지 않아요. 차원 간 전송, Mekanism 화학 물질, Ars Nouveau 마나 같은 **새 기능**을 열어요. 각각 업그레이드 슬롯을 하나 차지하며, 같은 노드의 [성능 업그레이드](upgrades-performance.md)와 함께 사용할 수 있어요.

업그레이드 슬롯은 [필터 및 업그레이드](filters-upgrades.md) 패널에 있어요. 같은 업그레이드는 중복할 수 없지만 서로 다른 종류의 효과는 함께 적용돼요. 고성능 노드에는 네더라이트, 차원, Mekanism 화학 물질, Ars 마나 업그레이드를 하나씩 넣을 수 있어요.

## 차원 업그레이드

**차원 간 전송을 활성화해요.** 없으면 같은 차원의 노드끼리만 전송할 수 있어요. 설치하면 오버월드와 네더, 엔드와 오버월드 또는 모드 차원처럼 서로 다른 차원의 노드 사이에서도 자원을 주고받을 수 있어요.

**양쪽 모두 필요해요.** 송신 노드와 수신 노드에 모두 차원 업그레이드를 설치해야 해요. 한쪽에만 설치하면 안 돼요. 전송 시스템이 양쪽 노드를 확인한 뒤 차원 간 전송을 허용하기 때문이에요.

같은 차원에서는 추가 효과가 없어요. 일반 전송은 이 업그레이드 없이도 작동해요.

<RecipeFor id="logisticsnetworks:dimensional_upgrade" />

## Mekanism 화학 물질 업그레이드

**화학 물질 채널 유형을 활성화해요.** 없으면 해당 노드의 [채널 설정](channel-settings.md)에서 유형을 화학 물질로 고를 수 없어요. 설치하면 화학 물질 유형으로 설정한 채널에서 Mekanism의 기체, 주입 물질, 안료, 슬러리를 감지하고 전송할 수 있어요.

업그레이드는 채널을 설정한 노드에만 적용돼요. 화학 물질 송신 노드와 수신 노드는 각각 업그레이드가 필요해요. 화학 물질을 옮기지 않는 노드에는 필요하지 않아요.

제작과 사용 모두 **Mekanism** 모드가 설치되어 있어야 해요. 아래 제작법은 Mekanism이 불러와졌을 때만 표시돼요.

<RecipeFor id="logisticsnetworks:mekanism_chemical_upgrade" fallbackText="이 제작법을 사용하려면 Mekanism을 설치하세요." />

## Ars 마나 업그레이드

**마나 채널 유형을 활성화해요.** Mekanism 화학 물질 업그레이드와 같은 방식으로 Ars Nouveau 마나를 다뤄요. 설치하면 채널 유형을 마나로 설정하여 Ars Nouveau 마나 단지와 마나를 지원하는 다른 블록 사이에서 마나를 옮길 수 있어요.

마나를 옮기는 송신·수신 노드는 각각 Ars 마나 업그레이드가 필요해요.

제작과 사용 모두 **Ars Nouveau** 모드가 설치되어 있어야 해요. 아래 제작법은 Ars Nouveau가 불러와졌을 때만 표시돼요.

<RecipeFor id="logisticsnetworks:ars_source_upgrade" fallbackText="이 제작법을 사용하려면 Ars Nouveau를 설치하세요." />
