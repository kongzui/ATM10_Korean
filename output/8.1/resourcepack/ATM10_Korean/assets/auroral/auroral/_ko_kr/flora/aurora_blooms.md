---
item_ids:
  - auroral:aurora_bloom
  - auroral:aurora_bloom_decorative
  - auroral:frozen_petals
navigation:
  title: 오로라 꽃
  icon: auroral:frozen_petals
  parent: index.md
  position: 30
---

# <Color id="gold">오로라 꽃</Color>

<Column alignItems="center" fullWidth={true}>
  <ItemImage id="aurora_bloom" scale="2" />

  오로라가 발생하는 동안 눈 위에 저절로 나타나는 마법의 꽃이에요. <ItemLink id="frozen_petals" />을 얻는 원천이며, 모드 콘텐츠 대부분의 출발점이에요.
</Column>

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">오로라 꽃 찾기</Color>
</Column>

오로라가 발생하는 동안 추운 생물 군계의 표면에 오로라 꽃이 자연적으로 생성돼요. **네 단계**를 거쳐 완전히 자라요. 오로라가 끝나고 남아 있는 꽃은 해가 뜨면 시들어 사라져요.

생성되고 살아남을 수 있는 표면:

* 눈 층 (눈이 녹았을 때 꽃이 흙이나 돌 위에 남지 않도록, 바로 아래 블록도 꽃이 살 수 있는 눈 표면이어야 해요)
* 눈 블록
* 가루눈 (아래 참고)
* 얼음, 꽁꽁 언 얼음, 푸른 얼음 (얼어붙은 바다의 표면도 가능해요)
* <ItemLink id="shimmering_ice" />

<Row>
  <ItemImage id="aurora_bloom" />
  ### <Color id="aqua">눈에 묻힌 꽃</Color>
</Row>

꽃을 **눈 층** 위에 놓거나 꽃이 **가루눈** 속에 나타나면 눈의 종류가 기억돼요. 꽃을 부수거나 꽃이 시들면 그 자리에 원래 눈이 복원돼요 — 눈 층은 눈 층으로, 가루눈은 가루눈으로 돌아와요. 묻힌 꽃은 위쪽에 눈송이 입자를 희미하게 내보내므로, 눈이 더 쌓여도 위치를 찾을 수 있어요.

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">수확하기</Color>
</Column>

다 자란(3단계) 오로라 꽃을 부수면 다음 아이템을 얻어요:

* <ItemLink id="frozen_petals" /> (행운 적용 시 1–4개)
* 다시 심을 수 있는 **살아 있는 오로라 꽃** 자체
* **15% 확률**로 살아 있는 꽃 하나 추가

덜 자란 꽃을 부수면 아무것도 나오지 않아요 — 기다린 만큼 보상받아요.

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">보존한 꽃 (섬세한 손길)</Color>
</Column>

다 자란 오로라 꽃을 **섬세한 손길** 도구로 수확하면 얼어붙은 꽃잎 대신 **장식용 오로라 꽃**을 얻어요. 장식용 꽃은:

* 해가 떠도 시들지 않고 영원히 남아요
* 항상 3단계 모습으로 보여요
* **화분**에 넣어 전시할 수 있어요
* 부수면 꽃 자체를 떨어뜨리므로 어디에든 다시 배치할 수 있어요

오로라가 발생하지 않을 때 오로라 꽃을 유지하는 유일한 방법이에요.

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">얼어붙은 꽃잎의 용도</Color>
</Column>

* **어색한 물약** — 네더 사마귀처럼 아무 양조기에서나 물병으로 양조해요
* <ItemLink id="cold_brewing_stand" /> — 시머스틸 주괴와 조합해요
* <ItemLink id="glow_leek_seeds" /> — 밀 씨앗과 조합해요
* <ItemLink id="frosted_cookies" /> — 마법의 빛이 반짝이는 달콤한 간식이에요
* <ItemLink id="aurora_shard" /> — 빙하 대야에서 오라 수위 1을 사용해 주입해요

<RecipeFor id="glow_leek_seeds" />

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">엔더 변환</Color>
</Column>

<Row>
  <ItemImage id="aurora_ender_shard" />
  ### <Color id="aqua">엔더 진주로 우클릭하기</Color>
</Row>

오로라 꽃을 **엔더 진주**로 우클릭하면 같은 성장 단계의 <ItemLink id="ender_bloom" />으로 바뀌어요. 이 과정에서 진주는 소모돼요. 전체 생장 과정은 [엔더 꽃](ender_bloom.md)을 참고하세요.
