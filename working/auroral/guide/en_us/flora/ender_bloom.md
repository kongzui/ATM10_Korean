---
item_ids:
  - auroral:ender_bloom
  - auroral:aurora_ender_shard
navigation:
  title: Ender Blooms
  icon: auroral:aurora_ender_shard
  parent: index.md
  position: 33
---

# <Color id="gold">Ender Blooms</Color>

<Column alignItems="center" fullWidth={true}>
  <ItemImage id="ender_bloom" scale="2" />

  The ender-touched cousins of Aurora Blooms — purple, restless, and a renewable source of Ender Pearls.
</Column>

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">Creation</Color>
</Column>

Ender Blooms never spawn on their own. To make one:

1. Find or grow an <ItemLink id="aurora_bloom" /> during an aurora event.
2. Right-click the bloom while holding an **Ender Pearl**.
3. The bloom transforms into an Ender Bloom at the same growth stage. The pearl is consumed.

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">Persistence</Color>
</Column>

Unlike Aurora Blooms, Ender Blooms **persist forever**. They do not wilt at sunrise and remain when the aurora ends.

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">Growth Requirements</Color>
</Column>

An Ender Bloom will only progress through its growth stages when planted on:

* <ItemLink id="shimmer_soil" />
* **End Stone**

On any other supporting block it survives indefinitely but stays at whatever stage it was placed. Bonemeal is also ineffective unless planted on one of the blocks above.

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">Harvesting</Color>
</Column>

Breaking an Ender Bloom at **any** stage drops a single Ender Bloom item (which always replants at stage 0).

When broken at stage 3, it **also** drops:

* One <ItemLink id="aurora_ender_shard" />
* A **5% chance** for an additional Ender Bloom

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">Aurora Ender Shards</Color>
</Column>

<Row>
  <ItemImage id="aurora_ender_shard" />
  ### <Color id="aqua">Renewable Ender Pearls</Color>
</Row>

Two Aurora Ender Shards craft back into an Ender Pearl. A mature Ender Bloom farm becomes a renewable Ender Pearl source.

<Recipe id="auroral:ender_pearl_from_shards" />
