---
item_ids:
  - auroral:ender_bloom
  - auroral:aurora_ender_shard
navigation:
  title: 엔더 꽃
  icon: auroral:aurora_ender_shard
  parent: index.md
  position: 33
---

# <Color id="gold">엔더 꽃</Color>

<Column alignItems="center" fullWidth={true}>
  <ItemImage id="ender_bloom" scale="2" />

  엔더의 기운이 깃든 오로라 꽃의 친척이에요 — 보라색을 띠고 가만히 있지 못하며, 엔더 진주를 계속 얻을 수 있게 해 줘요.
</Column>

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">만들기</Color>
</Column>

엔더 꽃은 자연적으로 생성되지 않아요. 만드는 방법은 다음과 같아요:

1. 오로라 현상이 일어나는 동안 <ItemLink id="aurora_bloom" />을 찾거나 기르세요.
2. **엔더 진주**를 든 채 꽃을 우클릭하세요.
3. 같은 성장 단계의 엔더 꽃으로 바뀌어요. 진주는 소모돼요.

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">유지</Color>
</Column>

오로라 꽃과 달리 엔더 꽃은 **영원히 남아요**. 해가 떠도 시들지 않고 오로라가 끝나도 유지돼요.

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">성장 조건</Color>
</Column>

엔더 꽃은 다음 블록 위에 심었을 때만 다음 성장 단계로 자라요:

* <ItemLink id="shimmer_soil" />
* **엔드 돌**

다른 받침 블록 위에서도 계속 살아남지만, 심었을 때의 성장 단계에 머물러요. 위에 나열한 블록 위에 심지 않으면 뼛가루도 효과가 없어요.

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">수확하기</Color>
</Column>

엔더 꽃은 **어느** 단계에서 부수든 엔더 꽃 아이템 하나를 떨어뜨려요 (다시 심으면 항상 0단계부터 시작해요).

3단계에서 부수면 다음 아이템도 **추가로** 떨어뜨려요:

* <ItemLink id="aurora_ender_shard" /> 하나
* **5% 확률**로 엔더 꽃 하나 추가

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">오로라 엔더 조각</Color>
</Column>

<Row>
  <ItemImage id="aurora_ender_shard" />
  ### <Color id="aqua">재생 가능한 엔더 진주</Color>
</Row>

오로라 엔더 조각 두 개를 조합하면 엔더 진주로 되돌릴 수 있어요. 다 자란 엔더 꽃을 수확하는 농장은 엔더 진주를 계속 얻을 수 있는 공급원이 돼요.

<Recipe id="auroral:ender_pearl_from_shards" />
