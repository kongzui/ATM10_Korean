---
navigation:
  parent: aae_intro/aae_intro-index.md
  title: 고급 패턴 인코더
  icon: advanced_ae:adv_pattern_encoder
categories:
  - advanced items
item_ids:
  - advanced_ae:adv_pattern_encoder
  - advanced_ae:adv_processing_pattern
---

# 고급 패턴 인코더

ME 고급 패턴 공급기에 아이템을 보낼 위치를 알려 주려면 해당 정보를 인코딩하는 특별한 장치가
필요합니다. 손에 든 채 우클릭하면 GUI를 열 수 있습니다.

<ItemImage id="advanced_ae:adv_pattern_encoder" scale="4"></ItemImage>

인코딩된 처리 패턴을 왼쪽 슬롯에 넣으면 패턴을 디코딩하고 모든 원재료를 목록으로 표시합니다.

![고급 패턴 인코더 GUI](../pic/ape_pattern.png)

각 행에는 재료를 보낼 수 있는 모든 블록 면을 나타내는 버튼이 있습니다. "A" 버튼을 선택한 상태로
두면 패턴 공급기에 직접 연결된 면으로 재료를 보내며, 특정 면을 선택하면 반드시 그 면으로 아이템을
삽입합니다. 고급 패턴은 <ItemLink id="advanced_ae:adv_pattern_provider" />에서만 제대로 디코딩되며,
다른 종류의 패턴 공급기에 사용하면 일반 패턴처럼 작동한다는 점에 주의하세요.
또한 아이템 하나라도 지정한 면에 삽입할 수 없으면 어떤 아이템도 방향을 지정해 삽입하지 않고 일반
패턴 공급기의 동작을 적용합니다.
